import assert from "node:assert/strict";
import test from "node:test";
import { readMailbox } from "../apps/server/src/config.ts";
import {
  mailboxConnectionId,
  mailThreadId,
  threadRoot,
} from "../packages/integrations/src/mail.ts";

test("SMTP settings turn on the mailbox and IMAP defaults to the same account", () => {
  assert.equal(readMailbox({}), undefined);
  const config = readMailbox({
    SMTP_HOST: "smtp.example.com",
    SMTP_PORT: "465",
    SMTP_USER: "me@example.com",
    SMTP_PASS: "secret",
  });
  assert.ok(config);
  assert.equal(config.from, "me@example.com");
  assert.equal(config.smtp.secure, true);
  assert.deepEqual(config.imap, {
    host: "imap.example.com",
    port: 993,
    secure: true,
    user: "me@example.com",
    pass: "secret",
  });
  assert.equal(
    readMailbox({
      SMTP_HOST: "smtp.example.com",
      SMTP_PORT: "587",
      SMTP_USER: "me@example.com",
      SMTP_PASS: "x",
    })?.smtp.secure,
    false,
  );
});

test("an incomplete SMTP login fails at startup instead of at the first send", () => {
  assert.throws(() => readMailbox({ SMTP_HOST: "smtp.example.com" }), /SMTP_USER and SMTP_PASS/);
  assert.throws(
    () =>
      readMailbox({
        SMTP_HOST: "smtp.example.com",
        SMTP_USER: "not-an-address",
        SMTP_PASS: "x",
      }),
    /MAIL_FROM/,
  );
});

test("thread IDs carry the root Message-ID safely and reject anything else", () => {
  const id = mailThreadId("<abc.123@mail.example>");
  assert.match(id, /^t[A-Za-z0-9_-]+$/);
  assert.equal(threadRoot(id), "<abc.123@mail.example>");
  assert.equal(threadRoot("trip-thread"), null);
  assert.equal(threadRoot(mailThreadId("no brackets")), null);
});

test("changing the mailbox account changes the connection that prepared sends are bound to", () => {
  const base = readMailbox({
    SMTP_HOST: "smtp.example.com",
    SMTP_USER: "me@example.com",
    SMTP_PASS: "x",
  });
  const other = readMailbox({
    SMTP_HOST: "smtp.example.com",
    SMTP_USER: "you@example.com",
    SMTP_PASS: "x",
  });
  assert.ok(base && other);
  assert.notEqual(mailboxConnectionId(base), mailboxConnectionId(other));
  assert.equal(
    mailboxConnectionId(base),
    mailboxConnectionId({ ...base, imap: { ...base.imap, pass: "rotated" } }),
  );
});
