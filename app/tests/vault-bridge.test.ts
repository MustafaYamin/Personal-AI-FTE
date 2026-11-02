import assert from "node:assert/strict";
import { mkdir, mkdtemp, readdir, readFile, rename, rm, utimes, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { after, before, beforeEach, test } from "node:test";
import { createApp } from "../apps/server/src/app.ts";
import type { Config } from "../apps/server/src/config.ts";
import { createStore, type Store } from "../apps/server/src/db.ts";
import { parseQwenOutput } from "../apps/server/src/engine/qwen.ts";
import type { AgentService } from "../apps/server/src/engine/service.ts";
import { parseFrontmatter, VaultBridge } from "../apps/server/src/vault.ts";
import type { AgentTask } from "../packages/domain/src/agent.ts";
import type { ActionProposal } from "../packages/domain/src/index.ts";

const owner = "local-user";
const email = (subject: string) => ({
  kind: "email.send" as const,
  data: { to: ["sam@example.com"], subject, body: "Hello", cc: [], bcc: [], attachmentIds: [] },
});
// Stands in for the qwen CLI. It records its stdin and answers according to the task text.
const fakeQwen = `
const fs = require("node:fs");
let input = "";
process.stdin.on("data", (d) => (input += d));
process.stdin.on("end", () => {
  fs.writeFileSync(process.env.QWEN_CAPTURE, JSON.stringify({ input, argv: process.argv.slice(2) }));
  const task = input.slice(input.lastIndexOf("Task:"));
  if (task.includes("QWEN_FAIL")) { console.error("quota exceeded"); process.exit(3); }
  if (task.includes("QWEN_ASK")) return console.log("<FTE_QUESTION>Which account?</FTE_QUESTION>");
  if (task.includes("QWEN_BADJSON")) return console.log("<FTE_ACTION>{nope</FTE_ACTION>");
  if (task.includes("QWEN_EMAIL"))
    return console.log('<FTE_ACTION>{"kind":"email.send","data":{"to":["sam@example.com"],"subject":"From Qwen","body":"Hi"}}</FTE_ACTION>');
  if (task.includes("QWEN_HANG")) return setTimeout(() => {}, 60000);
  console.log("thinking\\n<FTE_RESULT>The answer is 4</FTE_RESULT>");
});`;

let directory: string, vault: string, capture: string, script: string;
let db: Store | undefined, agent: AgentService, bridge: VaultBridge;
const store = () => {
  assert.ok(db);
  return db;
};
const path = (...parts: string[]) => join(vault, ...parts);
const list = (folder: string) => readdir(path(folder));
const put = async (folder: string, name: string, text: string) => {
  await mkdir(path(folder), { recursive: true });
  await writeFile(path(folder, name), text);
};
const tasks = () => store().list<AgentTask>(owner, "tasks");
const actionsList = () => store().list<ActionProposal>(owner, "actions");
const actionStatus = async (id: string) =>
  (await store().get<ActionProposal>(owner, "actions", id))?.status;
const vaultTask = async (name: string) => {
  const task = (await tasks()).find((t) => t.input.vaultFile === name);
  assert.ok(task, `task for ${name}`);
  return task;
};
const run = async () => {
  await bridge.sync();
  await agent.worker.tick();
  await bridge.sync();
};

before(async () => {
  directory = await mkdtemp(join(tmpdir(), "fte-vault-"));
  capture = join(directory, "capture.json");
  script = join(directory, "fake-qwen.cjs");
  await writeFile(script, fakeQwen);
  process.env.QWEN_CAPTURE = capture;
});
after(async () => {
  await db?.close();
  delete process.env.QWEN_CAPTURE;
  await rm(directory, { recursive: true, force: true });
});
beforeEach(async () => {
  await db?.close();
  vault = await mkdtemp(join(directory, "vault-"));
  await writeFile(
    path("Company_Handbook.md"),
    "---\nversion: 1\n---\n\nAlways sign as Dev Team.\n",
  );
  await writeFile(path("Dashboard.md"), "# Dashboard\n\nMy own notes.\n");
  db = await createStore();
  const config: Config = {
    mode: "sample",
    port: 8787,
    host: "127.0.0.1",
    publicUrl: "http://localhost:8787",
    dataDir: directory,
    agentBackend: "sample",
    taskBackend: "qwen",
    qwenCommand: `node "${script}"`,
    qwenTimeoutMs: 20000,
    vaultPath: vault,
    intelligenceApiKey: "test-project-key-never-sent",
    googleRedirectUri: "http://localhost:8787/api/google/callback",
    allowedOrigins: ["http://localhost:8081"],
  };
  ({ agent } = await createApp(db, config));
  bridge = new VaultBridge(agent, vault, { settleMs: 0 });
  // Prompts read the service's own bridge, so that is the one that must load the handbook.
  await agent.vault?.sync();
  await agent.ensure(owner);
});

test("frontmatter parsing handles CRLF and files without it", () => {
  assert.equal(parseFrontmatter("---\r\ntype: email\r\n---\r\nBody").meta.type, "email");
  assert.deepEqual(parseFrontmatter("plain").meta, {});
});

test("intake queues oldest first, once, and leaves responses alone", async () => {
  await put("Needs_Action", "B_new.md", "---\nsubject: Older by mtime\n---\nolder");
  await put("Needs_Action", "A_old.md", "---\nsubject: Newer by mtime\n---\nnewer");
  await put("Needs_Action", "RESPONSE_x.md", "old response");
  const past = new Date(Date.now() - 60000);
  await utimes(path("Needs_Action", "B_new.md"), past, past);
  await bridge.sync();
  await bridge.sync();
  assert.deepEqual((await list("In_Progress")).sort(), ["A_old.md", "B_new.md"]);
  assert.deepEqual(await list("Needs_Action"), ["RESPONSE_x.md"]);
  const scanned = (await store().scan<AgentTask>("tasks")).map((r) => r.value.title);
  assert.deepEqual(scanned, ["Older by mtime", "Newer by mtime"]);
});

test("a crash between task creation and the move does not duplicate work", async () => {
  await put("Needs_Action", "A.md", "same content");
  await bridge.sync();
  await rename(path("In_Progress", "A.md"), path("Needs_Action", "A.md"));
  await bridge.sync();
  assert.equal((await tasks()).length, 1);
});

test("source text is marked untrusted and dropped files are read only from Inbox", async () => {
  await put("Inbox", "note.txt", "INBOX CONTENT");
  await writeFile(join(directory, "outside.txt"), "OUTSIDE CONTENT");
  await put("Needs_Action", "in.md", `---\noriginal_path: ${path("Inbox", "note.txt")}\n---\nA`);
  await put(
    "Needs_Action",
    "out.md",
    `---\noriginal_path: ${join(directory, "outside.txt")}\n---\nB`,
  );
  await bridge.sync();
  const inside = await vaultTask("in.md");
  const outside = await vaultTask("out.md");
  assert.match(inside.prompt, /untrusted source data/);
  assert.match(inside.prompt, /INBOX CONTENT/);
  assert.doesNotMatch(outside.prompt, /OUTSIDE CONTENT/);
});

test("oversized items still fit the task limit", async () => {
  await put("Needs_Action", "big.md", "x".repeat(50000));
  await bridge.sync();
  assert.ok((await vaultTask("big.md")).prompt.length <= 12000);
});

test("a finished task reaches Done with its response, plan and log", async () => {
  await put("Needs_Action", "T.md", "What is 2+2?");
  await run();
  assert.deepEqual((await list("Done")).sort(), ["RESPONSE_T.md", "T.md"]);
  assert.match(await readFile(path("Done", "RESPONSE_T.md"), "utf8"), /The answer is 4/);
  assert.match(await readFile(path("Plans", "PLAN_T.md"), "utf8"), /status: succeeded/);
  const daily = (await list("Logs")).find((name) => /^\d{4}-\d{2}-\d{2}\.md$/.test(name));
  assert.ok(daily);
  assert.match(await readFile(path("Logs", daily), "utf8"), /Completed T\.md/);
});

test("the prompt reaches qwen intact over stdin, without -y", async () => {
  await put("Needs_Action", "T.md", "first line\nsecond line\nthird line");
  await run();
  const { input, argv } = JSON.parse(await readFile(capture, "utf8"));
  assert.match(input, /first line\nsecond line\nthird line/);
  assert.match(input, /Always sign as Dev Team/);
  assert.ok(!argv.includes("-y") && !argv.includes("--yolo"));
});

test("a qwen failure is reported, not hidden", async () => {
  await put("Needs_Action", "T.md", "QWEN_FAIL");
  await run();
  assert.match((await vaultTask("T.md")).error ?? "", /code 3: quota exceeded/);
  assert.deepEqual(await list(join("Logs", "Failed_Executions")), ["T.md"]);
  assert.ok((await list("Logs")).some((name) => name.startsWith("ERROR_T_")));
});

test("an invalid qwen action fails without proposing anything", async () => {
  await put("Needs_Action", "T.md", "QWEN_BADJSON");
  await run();
  assert.equal((await vaultTask("T.md")).status, "failed");
  assert.equal((await actionsList()).length, 0);
});

test("qwen can ask a question", async () => {
  await put("Needs_Action", "T.md", "QWEN_ASK");
  await run();
  const task = await vaultTask("T.md");
  assert.equal(task.status, "waiting_input");
  assert.equal(task.question, "Which account?");
});

test("pausing a task stops a running qwen process", async () => {
  await put("Needs_Action", "T.md", "QWEN_HANG");
  await bridge.sync();
  const started = Date.now();
  const running = agent.worker.tick();
  const task = await vaultTask("T.md");
  while ((await store().get<AgentTask>(owner, "tasks", task.id))?.status !== "running")
    await new Promise((resolve) => setTimeout(resolve, 20));
  await new Promise((resolve) => setTimeout(resolve, 300));
  await agent.control(owner, task.id, "pause");
  await running;
  assert.ok(Date.now() - started < 15000);
  assert.equal((await store().get<AgentTask>(owner, "tasks", task.id))?.status, "paused");
});

test("nothing sends until a human moves the review to Approved", async () => {
  await put("Needs_Action", "T.md", "QWEN_EMAIL");
  await run();
  const [name] = await list("Pending_Approval");
  assert.match(name, /^REVIEW_/);
  const [action] = await actionsList();
  assert.equal(action.status, "awaiting_review");
  assert.equal((await vaultTask("T.md")).status, "waiting_approval");
  await bridge.sync();
  assert.equal(await actionStatus(action.id), "awaiting_review");
  await rename(path("Pending_Approval", name), path("Approved", name));
  await bridge.sync();
  assert.equal(await actionStatus(action.id), "succeeded");
  assert.ok((await list("Done")).includes(name));
  assert.ok((await list("Logs")).some((file) => file.startsWith("EXEC_REVIEW_")));
  // The repeated request after approval resolves to the finished action, never a second send.
  await run();
  assert.equal((await actionsList()).length, 1);
  assert.equal((await vaultTask("T.md")).status, "succeeded");
});

test("rejecting a review declines it and never executes", async () => {
  const action = await agent.actions.propose(owner, email("Decline me"));
  await bridge.sync();
  const [name] = await list("Pending_Approval");
  await rename(path("Pending_Approval", name), path("Rejected", name));
  await bridge.sync();
  await bridge.sync();
  assert.equal(await actionStatus(action.id), "denied");
  assert.deepEqual(await list("Rejected"), [name]);
});

test("editing a review file cannot change what is sent", async () => {
  const action = await agent.actions.propose(owner, email("Original"));
  await bridge.sync();
  const [name] = await list("Pending_Approval");
  const text = await readFile(path("Pending_Approval", name), "utf8");
  await writeFile(path("Approved", name), text.replace(/sam@example\.com/g, "evil@example.com"));
  await rm(path("Pending_Approval", name));
  await bridge.sync();
  const saved = await store().get<ActionProposal>(owner, "actions", action.id);
  assert.ok(saved);
  assert.equal(saved.status, "succeeded");
  assert.deepEqual((saved.data as { to: string[] }).to, ["sam@example.com"]);
});

test("a stale or forged review file is refused", async () => {
  const action = await agent.actions.propose(owner, email("Guarded"));
  await put("Approved", "REVIEW_forged.md", `---\naction_id: ${action.id}\nhash: wrong\n---\n`);
  await put("Approved", "REVIEW_unknown.md", "---\naction_id: nope\nhash: x\n---\n");
  await bridge.sync();
  assert.equal(await actionStatus(action.id), "awaiting_review");
  assert.deepEqual((await list(join("Logs", "Failed_Executions"))).sort(), [
    "REVIEW_forged.md",
    "REVIEW_unknown.md",
  ]);
});

test("a review decided in the app leaves Pending_Approval", async () => {
  const action = await agent.actions.propose(owner, email("In app"));
  await bridge.sync();
  await agent.actions.decide(owner, action.id, action.hash, "approve");
  await bridge.sync();
  assert.deepEqual(await list("Pending_Approval"), []);
  assert.equal((await list("Done")).filter((name) => name.startsWith("REVIEW_")).length, 1);
});

test("a hand-written approved email becomes a review instead of sending", async () => {
  await put(
    "Approved",
    "old.md",
    "---\ntype: email\nto: sam@example.com\nsubject: Old style\n---\n\n## Draft Content\nHi Sam\n---\nfooter",
  );
  await bridge.sync();
  const [action] = await actionsList();
  assert.equal(action.status, "awaiting_review");
  assert.equal((action.data as { body: string }).body, "Hi Sam");
  assert.equal((await list("Pending_Approval")).length, 1);
});

test("a hand-written draft is saved without any send", async () => {
  await put(
    "Approved",
    "d.md",
    "---\ntype: email\naction: draft\nto: sam@example.com\nsubject: Later\n---\n\n## Draft Content\nBody",
  );
  await bridge.sync();
  assert.equal((await store().list(owner, "drafts")).length, 1);
  assert.equal((await actionsList()).length, 0);
  assert.ok((await list("Logs")).some((name) => name.startsWith("EXEC_d_")));
});

test("whatsapp is logged only, and unknown types claim no effect", async () => {
  await put("Approved", "w.md", "---\ntype: whatsapp\nto: Sam\n---\n\n## Draft Content\nHello");
  await put("Approved", "g.md", "---\ntype: payment\nreason: pay\n---\n");
  await bridge.sync();
  const logs = await list("Logs");
  const whatsapp = logs.find((name) => name.startsWith("EXEC_w_"));
  const generic = logs.find((name) => name.startsWith("EXEC_g_"));
  assert.ok(whatsapp && generic);
  assert.match(await readFile(path("Logs", whatsapp), "utf8"), /whatsapp_logged[\s\S]*manual/i);
  assert.match(await readFile(path("Logs", generic), "utf8"), /Nothing was done/);
  assert.equal((await actionsList()).length, 0);
});

test("an invalid hand-written email is quarantined", async () => {
  await put("Approved", "bad.md", "---\ntype: email\nto: not-an-address\nsubject: X\n---\n");
  await bridge.sync();
  assert.deepEqual(await list(join("Logs", "Failed_Executions")), ["bad.md"]);
});

test("the dashboard block updates repeatedly and keeps the owner's notes", async () => {
  await put("Needs_Action", "T.md", "hello | world");
  await bridge.sync();
  const first = await readFile(path("Dashboard.md"), "utf8");
  assert.match(first, /My own notes\./);
  assert.match(first, /\| Pending Tasks \| 1 \|/);
  await agent.worker.tick();
  await bridge.sync();
  await bridge.sync();
  const second = await readFile(path("Dashboard.md"), "utf8");
  assert.match(second, /\| Pending Tasks \| 0 \|/);
  assert.match(second, /\| Completed Today \| 1 \|/);
  assert.equal(second.match(/fte:status:start/g)?.length, 1);
});

test("parsing qwen output prefers tags and falls back to plain text", () => {
  assert.deepEqual(parseQwenOutput("plain answer"), { kind: "result", text: "plain answer" });
  assert.equal(parseQwenOutput("x<FTE_QUESTION>Why?</FTE_QUESTION>").kind, "question");
  assert.throws(() => parseQwenOutput("  \n"), /without producing/);
});
