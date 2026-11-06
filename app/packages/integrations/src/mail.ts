import { createHash } from "node:crypto";
import { ImapFlow, type SearchObject } from "imapflow";
import { type ParsedMail, simpleParser } from "mailparser";
import nodemailer from "nodemailer";
import type { EmailDraft, Mail } from "../../domain/src/index.ts";

/** A mailbox reached with the owner's own SMTP (send) and IMAP (read) credentials. */
export interface MailboxConfig {
  from: string;
  fromName?: string;
  smtp: { host: string; port: number; secure: boolean; user: string; pass: string };
  imap: { host: string; port: number; secure: boolean; user: string; pass: string };
  /** Append sent messages to the IMAP Sent folder. Gmail and Outlook already do this. */
  saveSent: boolean;
}

/** IMAP mail plus the RFC 5322 headers a reply needs. */
export interface MailboxMessage extends Mail {
  messageId?: string;
  references: string[];
  uid: number;
  /** Mailing-list, auto-reply or bulk mail, which should not become work by default. */
  bulk: boolean;
}

export class MailboxError extends Error {
  override name = "MailboxError";
  outcomeUnknown?: boolean;
}

const MAX_BODY = 100000;
const box = { inbox: "INBOX" } as const;
type Folder = "inbox" | "sent";

const b64 = (text: string) => Buffer.from(text, "utf8").toString("base64url");
const unb64 = (text: string) => Buffer.from(text, "base64url").toString("utf8");

/** Thread IDs travel in URL paths, so the root Message-ID is encoded. */
export const mailThreadId = (rootMessageId: string) => `t${b64(rootMessageId)}`;
export function threadRoot(threadId: string): string | null {
  if (!threadId.startsWith("t")) return null;
  const root = unb64(threadId.slice(1));
  return /^<[^<>\s]+>$/.test(root) ? root : null;
}

/** A stable account identity: changing host or user invalidates prepared sends. */
export function mailboxConnectionId(config: MailboxConfig) {
  return `smtp-${createHash("sha256")
    .update(`${config.smtp.host}|${config.smtp.user}|${config.imap.host}|${config.imap.user}`)
    .digest("hex")
    .slice(0, 24)}`;
}

const address = (value: ParsedMail["from"] | ParsedMail["to"]) => {
  const list = Array.isArray(value) ? value : value ? [value] : [];
  return list.flatMap((group) => group.value);
};

function toMail(
  parsed: ParsedMail,
  folder: Folder,
  uidValidity: string,
  uid: number,
  flags: Set<string> | undefined,
): MailboxMessage {
  const id = `${folder}~${uidValidity}~${uid}`;
  const from = address(parsed.from)[0];
  const references = (
    Array.isArray(parsed.references)
      ? parsed.references
      : parsed.references
        ? [parsed.references]
        : []
  ).filter(Boolean);
  const messageId = parsed.messageId;
  const root = references[0] ?? parsed.inReplyTo ?? messageId ?? `<${id}@local>`;
  const header = (name: string) => String(parsed.headers.get(name) ?? "").toLowerCase();
  const bulk =
    parsed.headers.has("list-unsubscribe") ||
    parsed.headers.has("list-id") ||
    ["bulk", "list", "junk"].includes(header("precedence")) ||
    (header("auto-submitted") !== "" && header("auto-submitted") !== "no");
  const text =
    (parsed.text ?? "").trim() || htmlText(typeof parsed.html === "string" ? parsed.html : "");
  return {
    id,
    uid,
    threadId: mailThreadId(root),
    messageId,
    references: [...references, ...(messageId ? [messageId] : [])],
    sender: from?.name || from?.address || "Unknown sender",
    from: from?.address ?? "",
    to: [...address(parsed.to), ...address(parsed.cc)].map((a) => a.address ?? "").filter(Boolean),
    subject: parsed.subject?.trim() || "(no subject)",
    body: text.slice(0, MAX_BODY),
    date: (parsed.date ?? new Date()).toISOString(),
    unread: folder === "inbox" && !flags?.has("\\Seen"),
    label: folder === "sent" ? "Sent" : "Inbox",
    attachments: parsed.attachments
      .map((attachment, index) => ({ attachment, index }))
      .filter(({ attachment }) => attachment.contentType === "application/pdf")
      .map(
        ({ attachment, index }) =>
          `${id}:${index}:${encodeURIComponent(attachment.filename ?? `attachment-${index + 1}.pdf`)}`,
      ),
    bulk,
  };
}

function htmlText(html: string) {
  return html
    .replace(/<(script|style)[\s\S]*?<\/\1>/gi, "")
    .replace(/<br\s*\/?>|<\/p>|<\/div>/gi, "\n")
    .replace(/<[^>]+>/g, "")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

export class MailboxClient {
  constructor(private readonly config: MailboxConfig) {}

  get account() {
    return this.config.from;
  }

  /** One short-lived IMAP session per operation keeps polling and requests independent. */
  private async session<T>(work: (client: ImapFlow) => Promise<T>): Promise<T> {
    const client = new ImapFlow({
      host: this.config.imap.host,
      port: this.config.imap.port,
      secure: this.config.imap.secure,
      auth: { user: this.config.imap.user, pass: this.config.imap.pass },
      logger: false,
      socketTimeout: 60000,
    });
    client.on("error", () => {});
    try {
      await client.connect();
    } catch (error) {
      throw new MailboxError(
        `Could not sign in to IMAP ${this.config.imap.host}: ${error instanceof Error ? error.message : String(error)}`,
      );
    }
    try {
      return await work(client);
    } finally {
      await client.logout().catch(() => client.close());
    }
  }

  private async sentPath(client: ImapFlow) {
    const boxes = await client.list();
    return (
      boxes.find((b) => b.specialUse === "\\Sent")?.path ??
      boxes.find((b) => /^(sent|sent items|sent mail|\[gmail\]\/sent mail)$/i.test(b.path))?.path
    );
  }

  private async read(
    client: ImapFlow,
    folder: Folder,
    path: string,
    query: SearchObject | null,
    limit: number,
    afterUid = 0,
  ): Promise<{ mail: MailboxMessage[]; uidValidity: string; uidNext: number }> {
    const lock = await client.getMailboxLock(path, { readOnly: true });
    try {
      const mailbox = client.mailbox;
      if (!mailbox) throw new MailboxError(`Mailbox ${path} could not be opened`);
      const uidValidity = String(mailbox.uidValidity);
      const uidNext = Number(mailbox.uidNext ?? 0);
      const mail: MailboxMessage[] = [];
      if (!mailbox.exists) return { mail, uidValidity, uidNext };
      // `N:*` always matches the last message, so UIDs at or below the cursor are dropped.
      const found = (
        (await client.search(query ?? (afterUid ? { uid: `${afterUid + 1}:*` } : { all: true }), {
          uid: true,
        })) || []
      )
        .filter((uid) => uid > afterUid)
        .sort((a, b) => a - b);
      // Monitoring advances oldest first so a burst is never skipped; reading shows the newest.
      const uids = afterUid && !query ? found.slice(0, limit) : found.slice(-limit);
      if (!uids.length) return { mail, uidValidity, uidNext };
      for await (const message of client.fetch(
        uids.join(","),
        { uid: true, flags: true, source: true },
        { uid: true },
      )) {
        if (!message.source) continue;
        mail.push(
          toMail(
            await simpleParser(message.source),
            folder,
            uidValidity,
            message.uid,
            message.flags,
          ),
        );
      }
      mail.sort((a, b) => a.uid - b.uid);
      return { mail, uidValidity, uidNext };
    } finally {
      lock.release();
    }
  }

  /** Newest inbox messages, or those matching every word of `query`. */
  async list(query = "", limit = 25): Promise<MailboxMessage[]> {
    const words = query
      .replace(/\bin:inbox\b/gi, "")
      .trim()
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 6);
    // The server narrows by the first word; every word is then matched locally.
    const search: SearchObject | null = words.length ? { text: words[0] } : null;
    const { mail } = await this.session((client) =>
      this.read(client, "inbox", box.inbox, search, words.length ? 200 : limit),
    );
    const matches = mail.filter((m) =>
      words.every((word) =>
        `${m.sender} ${m.from} ${m.subject} ${m.body}`.toLowerCase().includes(word.toLowerCase()),
      ),
    );
    return matches.sort((a, b) => b.date.localeCompare(a.date)).slice(0, limit);
  }

  /** Inbox and Sent messages that share the thread's root Message-ID. */
  async thread(threadId: string): Promise<MailboxMessage[]> {
    const root = threadRoot(threadId);
    if (!root) return [];
    const query: SearchObject = {
      or: [{ header: { "message-id": root } }, { header: { references: root } }],
    };
    return this.session(async (client) => {
      const sent = await this.sentPath(client);
      const results = [await this.read(client, "inbox", box.inbox, query, 50)];
      if (sent) results.push(await this.read(client, "sent", sent, query, 50));
      return results
        .flatMap((r) => r.mail)
        .filter((m) => m.threadId === threadId || m.references.includes(root))
        .sort((a, b) => a.date.localeCompare(b.date));
    });
  }

  /** Inbox messages newer than `afterUid` within one UIDVALIDITY epoch. */
  async since(afterUid: number, limit = 20) {
    return this.session((client) =>
      this.read(client, "inbox", box.inbox, null, limit, Math.max(afterUid, 0)),
    );
  }

  /** The current UIDVALIDITY and next UID, used as a monitoring baseline. */
  async status() {
    return this.session(async (client) => {
      const status = await client.status(box.inbox, { uidNext: true, uidValidity: true });
      if (!status) throw new MailboxError("The IMAP inbox status could not be read");
      return { uidValidity: String(status.uidValidity), uidNext: Number(status.uidNext ?? 1) };
    });
  }

  async attachment(messageId: string, index: number): Promise<Uint8Array> {
    const [folder, uidValidity, uidText] = messageId.split("~");
    const uid = Number(uidText);
    if ((folder !== "inbox" && folder !== "sent") || !Number.isInteger(uid))
      throw new MailboxError("Attachment reference is invalid");
    return this.session(async (client) => {
      const path = folder === "inbox" ? box.inbox : await this.sentPath(client);
      if (!path) throw new MailboxError("Sent folder not found");
      const lock = await client.getMailboxLock(path, { readOnly: true });
      try {
        if (client.mailbox ? String(client.mailbox.uidValidity) !== uidValidity : true)
          throw new MailboxError("The mailbox changed. Refresh the inbox and try again.");
        const message = await client.fetchOne(String(uid), { source: true }, { uid: true });
        const source = message ? message.source : undefined;
        if (!source) throw new MailboxError("Message not found");
        const attachment = (await simpleParser(source)).attachments[index];
        if (!attachment) throw new MailboxError("Attachment not found");
        return new Uint8Array(attachment.content);
      } finally {
        lock.release();
      }
    });
  }

  /** Verifies both logins without reading or sending mail. */
  async verify() {
    await this.transport().verify();
    await this.status();
  }

  private transport() {
    return nodemailer.createTransport({
      host: this.config.smtp.host,
      port: this.config.smtp.port,
      secure: this.config.smtp.secure,
      auth: { user: this.config.smtp.user, pass: this.config.smtp.pass },
    });
  }

  async send(
    draft: EmailDraft,
    attachments: { name: string; mimeType: string; bytes: Uint8Array }[],
    reply?: { messageId?: string; references: string[] },
  ): Promise<{ id: string }> {
    const message = {
      from: this.config.fromName
        ? { name: this.config.fromName, address: this.config.from }
        : this.config.from,
      to: draft.to,
      cc: draft.cc,
      bcc: draft.bcc,
      subject: draft.subject,
      text: draft.body,
      inReplyTo: reply?.messageId,
      references: reply?.references.length ? reply.references.join(" ") : undefined,
      attachments: attachments.map((a) => ({
        filename: a.name,
        contentType: a.mimeType,
        content: Buffer.from(a.bytes),
      })),
    };
    let info: { messageId: string; accepted: unknown[]; rejected: unknown[] };
    try {
      info = await this.transport().sendMail(message);
    } catch (error) {
      const failure = new MailboxError(
        `SMTP send failed: ${error instanceof Error ? error.message : String(error)}`,
      );
      // A dropped connection after DATA may still have delivered the message.
      const code = (error as { code?: string }).code;
      failure.outcomeUnknown = code === "ETIMEDOUT" || code === "ECONNRESET" || code === "ESOCKET";
      throw failure;
    }
    if (!info.accepted.length) throw new MailboxError("SMTP server rejected every recipient");
    if (this.config.saveSent) {
      const raw = await new Promise<Buffer>((resolve, reject) =>
        nodemailer
          .createTransport({ streamTransport: true, buffer: true })
          .sendMail({ ...message, messageId: info.messageId }, (error, result) =>
            error ? reject(error) : resolve(result.message as Buffer),
          ),
      );
      // The message is already delivered; failing to file a copy is not a send failure.
      await this.session(async (client) => {
        const sent = await this.sentPath(client);
        if (sent) await client.append(sent, raw, ["\\Seen"]);
      }).catch(() => {});
    }
    return { id: info.messageId };
  }
}
