import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import { parseEnv } from "node:util";
import type { MailboxConfig } from "../../../packages/integrations/src/mail.ts";

/** .env keys whose file value loses to a different value already set in the environment. */
export function shadowedEnvKeys(
  file: Record<string, string | undefined>,
  env: Record<string, string | undefined> = process.env,
): string[] {
  return Object.keys(file).filter((key) => env[key] !== undefined && env[key] !== file[key]);
}

if (existsSync(".env")) {
  // loadEnvFile never overrides existing variables. A stale shell or system-wide value
  // (for example OPENAI_API_KEY) would otherwise silently replace the .env setting.
  const shadowed = shadowedEnvKeys(parseEnv(readFileSync(".env", "utf8")));
  process.loadEnvFile(".env");
  if (shadowed.length)
    console.warn(
      `[OpenMuse] Using ${shadowed.join(", ")} from the environment instead of .env. ` +
        (shadowed.length === 1
          ? "Unset it to use the .env value."
          : "Unset them to use the .env values."),
    );
}
// Capture the full setup/activation funnel while preserving explicit SDK opt-outs
// and any deployment-specific sampling rate. Config loads before runtime imports.
process.env.COPILOTKIT_TELEMETRY_SAMPLE_RATE ??= "1";

export interface Config {
  mode: "sample" | "live";
  port: number;
  host: string;
  publicUrl: string;
  dataDir: string;
  databaseUrl?: string;
  accessKey?: string;
  encryptionKey?: string;
  model?: string;
  jevMode?: "off" | "sample" | "live";
  typesafeApiKey?: string;
  jevModel?: string;
  agentBackend: "sample" | "model" | "agui";
  /** Runs open-ended delegated tasks. Conversation keeps using agentBackend. */
  taskBackend?: "model" | "qwen";
  qwenCommand?: string;
  qwenTimeoutMs?: number;
  /** The Obsidian vault. Without it the app runs with no vault integration. */
  vaultPath?: string;
  agentUrl?: string;
  agentToken?: string;
  intelligenceApiKey?: string;
  googleClientId?: string;
  googleClientSecret?: string;
  googleRedirectUri: string;
  workerUrl?: string;
  workerToken?: string;
  taskWorkerEnabled?: boolean;
  webSearchEnabled?: boolean;
  computerEnabled?: boolean;
  computerImage?: string;
  computerDeploymentId?: string;
  computerProvider?: ComputerProvider;
  computerE2bTemplate?: string;
  e2bApiKey?: string;
  allowedOrigins: string[];
  trustProxy?: boolean;
  /** The owner's own mailbox over SMTP and IMAP. When set, it replaces Gmail for mail. */
  mailbox?: MailboxConfig;
  /** How often the monitor checks IMAP for new mail. */
  mailPollSeconds?: number;
  /** Which new emails become vault tasks: every message, personal mail only, or none. */
  mailAutoTasks?: "all" | "personal" | "off";
}

export type ComputerProvider = "docker" | "e2b-desktop";

/** Pinned so live rankings do not shift when TypeSafe moves the `jev-latest` alias. */
export const defaultJevModel = "jev-1.13.0";

export const intelligenceKeyRequiredMessage =
  "OpenMuse requires CPK_INTELLIGENCE_API_KEY. " +
  "Run `npx copilotkit@latest login` and `npx copilotkit@latest project select`, " +
  "then set the generated server-only key. " +
  "See https://docs.copilotkit.ai/intelligence/connect-your-runtime";

export function required(name: string, message: string, value = process.env[name]): string {
  if (!value?.trim()) throw new Error(message);
  return value.trim();
}

export function assertApiDeploymentConfig(
  config: Config,
): asserts config is Config & { intelligenceApiKey: string } {
  required(
    "CPK_INTELLIGENCE_API_KEY",
    intelligenceKeyRequiredMessage,
    config.intelligenceApiKey ?? "",
  );
}

/** Accept a full worker URL, or host:port from a platform that omits the scheme. */
export function browserWorkerUrl(value?: string): string | undefined {
  const trimmed = value?.trim();
  if (!trimmed) return undefined;
  return trimmed.includes("://") ? trimmed : `http://${trimmed}`;
}

// Provider SDKs retry transient failures before the response starts, with
// exponential backoff: OpenAI and Anthropic retry HTTP 408, 409, 429, 5xx and
// connection errors and honor retry-after; Gemini retries 408, 429, 500, 502,
// 503 and 504. Other 4xx responses such as 400, 401 and 403 fail on the first
// attempt, and a stream that fails after it starts is not retried. External
// writes never re-fire here: they are dispatched outside the model loop through
// reviewed, idempotency-keyed actions.
export const MODEL_MAX_RETRIES = 2;

const flag = (value: string | undefined, fallback: boolean) =>
  value?.trim() ? /^(1|true|yes)$/i.test(value.trim()) : fallback;

/** SMTP_HOST turns the mailbox on; IMAP settings default to the SMTP account. */
export function readMailbox(env: Record<string, string | undefined> = process.env) {
  const host = env.SMTP_HOST?.trim();
  if (!host) return undefined;
  const user = env.SMTP_USER?.trim() ?? "";
  const pass = env.SMTP_PASS ?? "";
  if (!user || !pass) throw new Error("SMTP_HOST requires SMTP_USER and SMTP_PASS");
  const port = Number(env.SMTP_PORT?.trim() || 587);
  const imapPort = Number(env.IMAP_PORT?.trim() || 993);
  if (!Number.isInteger(port) || !Number.isInteger(imapPort))
    throw new Error("SMTP_PORT and IMAP_PORT must be port numbers");
  const from = env.MAIL_FROM?.trim() || user;
  if (!/^[^\s@]+@[^\s@]+$/.test(from))
    throw new Error("MAIL_FROM (or SMTP_USER) must be an email address");
  const config: MailboxConfig = {
    from,
    fromName: env.MAIL_FROM_NAME?.trim() || undefined,
    smtp: { host, port, secure: flag(env.SMTP_SECURE, port === 465), user, pass },
    imap: {
      host: env.IMAP_HOST?.trim() || host.replace(/^smtp\./i, "imap."),
      port: imapPort,
      secure: flag(env.IMAP_SECURE, imapPort === 993),
      user: env.IMAP_USER?.trim() || user,
      pass: env.IMAP_PASS || pass,
    },
    saveSent: flag(env.MAIL_SAVE_SENT, false),
  };
  return config;
}
function mailAutoTasks(value?: string): "all" | "personal" | "off" {
  const mode = value?.trim() || "personal";
  if (mode !== "all" && mode !== "personal" && mode !== "off")
    throw new Error("MAIL_AUTO_TASKS must be all, personal or off");
  return mode;
}
export function readConfig(): Config {
  const mode = process.env.WORKSPACE_MODE ?? "sample";
  if (mode !== "sample" && mode !== "live")
    throw new Error("WORKSPACE_MODE must be sample or live");
  const backend = process.env.AGENT_BACKEND ?? (mode === "sample" ? "sample" : "model");
  if (backend !== "sample" && backend !== "model" && backend !== "agui")
    throw new Error("AGENT_BACKEND must be sample, model or agui");
  if (mode === "live" && backend === "sample")
    throw new Error("Live workspaces cannot use the sample agent");
  const taskBackend = process.env.TASK_BACKEND?.trim() || "model";
  if (taskBackend !== "model" && taskBackend !== "qwen")
    throw new Error("TASK_BACKEND must be model or qwen");
  const jevMode = process.env.JEV_MODE ?? "off";
  if (jevMode !== "off" && jevMode !== "sample" && jevMode !== "live")
    throw new Error("JEV_MODE must be off, sample or live");
  const typesafeApiKey = process.env.TYPESAFE_API_KEY?.trim();
  if (jevMode === "live" && !typesafeApiKey)
    throw new Error("JEV_MODE=live requires a nonblank TYPESAFE_API_KEY");
  const computerProvider = process.env.COMPUTER_PROVIDER?.trim() || "docker";
  if (computerProvider !== "docker" && computerProvider !== "e2b-desktop")
    throw new Error("COMPUTER_PROVIDER must be docker or e2b-desktop");
  const e2bApiKey = process.env.E2B_API_KEY?.trim();
  if (process.env.COMPUTER_ENABLED === "true" && computerProvider === "e2b-desktop") {
    if (!e2bApiKey)
      throw new Error("COMPUTER_PROVIDER=e2b-desktop requires a nonblank E2B_API_KEY");
    // Sandboxes are matched by metadata across the whole E2B team, and every default
    // install would otherwise derive the same deployment label from localhost:8787.
    if (!process.env.COMPUTER_DEPLOYMENT_ID?.trim())
      throw new Error(
        "COMPUTER_PROVIDER=e2b-desktop requires a unique COMPUTER_DEPLOYMENT_ID, e.g. from `openssl rand -hex 12`",
      );
  }
  const port = Number(process.env.PORT ?? 8787);
  const publicUrl = process.env.PUBLIC_API_URL ?? `http://localhost:${port}`;
  const config: Config = {
    mode,
    port,
    host: process.env.HOST ?? "127.0.0.1",
    publicUrl,
    dataDir: resolve(process.env.DATA_DIR ?? ".openmuse"),
    databaseUrl: process.env.DATABASE_URL,
    accessKey: process.env.OPENMUSE_ACCESS_KEY,
    encryptionKey: process.env.TOKEN_ENCRYPTION_KEY,
    model: process.env.MODEL,
    jevMode,
    typesafeApiKey,
    jevModel: process.env.JEV_MODEL?.trim() || defaultJevModel,
    agentBackend: backend,
    taskBackend,
    qwenCommand: process.env.QWEN_COMMAND?.trim() || "qwen",
    vaultPath: process.env.VAULT_PATH?.trim() ? resolve(process.env.VAULT_PATH.trim()) : undefined,
    agentUrl: process.env.AGENT_URL,
    agentToken: process.env.AGENT_TOKEN,
    intelligenceApiKey: required("CPK_INTELLIGENCE_API_KEY", intelligenceKeyRequiredMessage),
    googleClientId: process.env.GOOGLE_CLIENT_ID,
    googleClientSecret: process.env.GOOGLE_CLIENT_SECRET,
    googleRedirectUri: `${publicUrl}/api/google/callback`,
    workerUrl: browserWorkerUrl(process.env.BROWSER_WORKER_URL),
    workerToken: process.env.WORKER_TOKEN,
    taskWorkerEnabled: process.env.TASK_WORKER_ENABLED !== "false",
    webSearchEnabled: process.env.WEB_SEARCH_ENABLED !== "false",
    computerEnabled: process.env.COMPUTER_ENABLED === "true",
    computerImage: process.env.COMPUTER_IMAGE ?? "openmuse-computer:local",
    // A blank line from .env is unset; otherwise every such install would share one name.
    computerDeploymentId: process.env.COMPUTER_DEPLOYMENT_ID?.trim() || undefined,
    computerProvider,
    computerE2bTemplate: process.env.COMPUTER_E2B_TEMPLATE?.trim() || "desktop",
    e2bApiKey,
    allowedOrigins: (
      process.env.ALLOWED_ORIGINS ?? "http://localhost:8081,http://127.0.0.1:8081"
    ).split(","),
    // Only trust X-Forwarded-For/X-Real-IP when the deployment is known to sit
    // behind a proxy that sets them; otherwise a direct caller can spoof them.
    trustProxy: process.env.TRUST_PROXY === "true",
    mailbox: readMailbox(),
    mailPollSeconds: Math.max(15, Number(process.env.MAIL_POLL_SECONDS?.trim() || 60) || 60),
    mailAutoTasks: mailAutoTasks(process.env.MAIL_AUTO_TASKS),
  };
  if (
    mode === "live" &&
    (!config.accessKey || config.accessKey.length < 24 || !config.encryptionKey)
  )
    throw new Error(
      "Live mode requires OPENMUSE_ACCESS_KEY (24+ characters) and TOKEN_ENCRYPTION_KEY (32-byte base64)",
    );
  if (mode === "sample" && !["127.0.0.1", "localhost", "::1"].includes(config.host))
    throw new Error("Sample workspace is local-only. HOST must be a loopback address.");
  return config;
}
