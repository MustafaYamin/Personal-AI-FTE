# AI Employee Vault - Silver Tier

A local-first, agent-driven personal automation system powered by Qwen Code and Obsidian.

**Status: Silver Tier Complete ✅**

## Quick Start

### Prerequisites

1. **Qwen Code** - Ensure Qwen Code CLI is installed and configured
2. **Python 3.13+** - Download from python.org
3. **Obsidian** - Download from obsidian.md
4. **Node.js** - Download from nodejs.org (for MCP servers)

### Installation

1. **Install Python dependencies:**

```bash
cd AI_Employee_Vault\src
pip install -r requirements.txt
playwright install chromium
```

2. **Verify Qwen Code:**

```bash
qwen --version
```

3. **Open the vault in Obsidian:**
   - Launch Obsidian
   - Click "Open folder as vault"
   - Select the `AI_Employee_Vault` folder

### Running the System

#### Option 1: Start All Watchers (Recommended)

```batch
cd AI_Employee_Vault\src\scheduler
start_all_watchers.bat ..
```

This starts all watchers and the orchestrator in separate windows.

#### Option 2: Individual Components

**Terminal 1 - Filesystem Watcher:**

```bash
cd AI_Employee_Vault\src
python filesystem_watcher.py ..
```

**Terminal 2 - Gmail Watcher (requires credentials):**

```bash
cd AI_Employee_Vault\src
python gmail_watcher.py .. ..\.cache\gmail_credentials.json
```

**Terminal 3 - WhatsApp Watcher:**

```bash
cd AI_Employee_Vault\src
python whatsapp_watcher.py ..
```

**Terminal 4 - Orchestrator:**

```bash
cd AI_Employee_Vault\src
python orchestrator.py ..
```

### Automatic Startup (Windows Task Scheduler)

```powershell
# Run as Administrator
cd AI_Employee_Vault\src\scheduler
.\register_task_scheduler.ps1
```

## Where to See Qwen Code's Output

**Qwen Code's response appears in the Orchestrator terminal.**

When a task is processed, you'll see:

```
============================================================
[AI] QWEN CODE PROCESSING: FILE_20260318_xxx.md
============================================================

[Qwen Code's response/answer appears here]

============================================================
[OK] QWEN CODE COMPLETED: FILE_20260318_xxx.md
============================================================

[DONE] File moved to: Done/FILE_20260318_xxx.md
```

## Watchers

### Filesystem Watcher

Monitors `Inbox/` folder for new files.

```bash
python filesystem_watcher.py /path/to/vault
```

### Gmail Watcher

Monitors Gmail for unread messages.

```bash
python gmail_watcher.py /path/to/vault /path/to/credentials.json
```

**Setup:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project → Enable Gmail API
3. Create OAuth2 credentials (Desktop app)
4. Download `credentials.json`
5. Place in `AI_Employee_Vault\.cache\gmail_credentials.json`

### WhatsApp Watcher

Monitors WhatsApp Web for priority messages.

```bash
python whatsapp_watcher.py /path/to/vault [session_path]
```

**Setup:**
1. First run requires QR code scan with WhatsApp mobile app
2. Session saved for future runs
3. Keywords: urgent, asap, invoice, payment, help, emergency, etc.

## Folder Structure

```
AI_Employee_Vault/
├── Dashboard.md          # Real-time status dashboard
├── Company_Handbook.md   # Rules and guidelines
├── Inbox/                # Drop folder for new items
├── Needs_Action/         # Items awaiting processing
├── Plans/                # Generated action plans
├── Pending_Approval/     # Awaiting human approval
├── Approved/             # Approved for execution
├── Rejected/             # Declined items
├── Done/                 # Completed tasks
├── Logs/                 # Activity logs
├── Briefings/            # CEO briefings
├── Accounting/           # Financial records
└── src/                  # Python source code
    ├── base_watcher.py
    ├── filesystem_watcher.py
    ├── gmail_watcher.py
    ├── whatsapp_watcher.py
    ├── orchestrator.py
    ├── requirements.txt
    ├── mcp_servers/
    │   ├── __init__.py
    │   └── email_mcp_server.py
    └── scheduler/
        ├── start_all_watchers.bat
        ├── stop_all_watchers.bat
        ├── register_task_scheduler.ps1
        └── unregister_task_scheduler.ps1
```

## Silver Tier Features

### Multiple Watchers

| Watcher | Purpose | Check Interval |
|---------|---------|----------------|
| Filesystem | Inbox folder monitoring | 5 seconds |
| Gmail | New email detection | 2 minutes |
| WhatsApp | Priority message detection | 30 seconds |

### Human-in-the-Loop (HITL) Workflow

```
1. Qwen detects sensitive action needed
2. Creates approval request in Pending_Approval/
3. Human reviews and moves to Approved/
4. Orchestrator executes the action
5. File moved to Done/ with execution log
```

### MCP Servers

| Server | Capabilities | Transport |
|--------|--------------|-----------|
| Email MCP | Send, draft, search emails | stdio |
| Playwright MCP | Browser automation | HTTP |

### Task Scheduler Integration

- Automatic startup at logon
- Automatic startup at system boot
- Manual start/stop scripts

## Testing the Workflow

### Test 1: File Drop

1. **Drop a test file** in the `Inbox` folder:
   ```
   AI_Employee_Vault\Inbox\test_task.txt
   ```

2. **Watch the magic happen:**
   - Filesystem Watcher detects the file
   - Creates an action file in `Needs_Action/`
   - Orchestrator triggers Qwen Code
   - Qwen processes the task
   - File moves to `Done/` when complete

3. **Check the Dashboard.md** in Obsidian for status updates

### Test 2: Email Approval Workflow

1. **Create a test email task:**
   ```markdown
   ---
   type: email
   from: test@example.com
   subject: Test Email
   received: 2026-03-23T10:00:00Z
   status: pending
   ---

   # Test Email

   Please reply to this email with a test message.

   ## Suggested Actions
   - [ ] Draft reply
   - [ ] Create approval request
   - [ ] Move to Done when complete
   ```

2. **Place in `Needs_Action/` folder**

3. **Orchestrator will:**
   - Trigger Qwen Code
   - Qwen creates approval request in `Pending_Approval/`
   - Human moves file to `Approved/`
   - Orchestrator executes and logs action
   - File moves to `Done/`

## Configuration

### Customize Company Handbook

Edit `Company_Handbook.md` to set your rules:
- Financial thresholds
- Communication guidelines
- Working hours
- Escalation rules
- Email tone and style

### Adjust Check Intervals

```bash
# Filesystem watcher (default: 5 seconds)
python filesystem_watcher.py .. --interval 10

# Gmail watcher (default: 120 seconds)
python gmail_watcher.py .. credentials.json --interval 300

# WhatsApp watcher (default: 30 seconds)
python whatsapp_watcher.py .. --interval 60

# Orchestrator (default: 30 seconds)
python orchestrator.py .. --interval 60
```

## Silver Tier Deliverables (COMPLETE ✅)

### Core Requirements
- ✅ All Bronze requirements
- ✅ Two or more Watcher scripts (Filesystem + Gmail + WhatsApp)
- ✅ Plan.md generation with Qwen reasoning
- ✅ One working MCP server (Email MCP)
- ✅ Human-in-the-Loop approval workflow
- ✅ Basic scheduling via Windows Task Scheduler

### Additional Features Implemented
- ✅ **Email MCP Server** - Send, draft, search emails via Gmail API
- ✅ **Gmail Watcher** - OAuth2 authenticated email monitoring
- ✅ **WhatsApp Watcher** - Playwright-based message monitoring
- ✅ **HITL Execution Logic** - Orchestrator executes approved actions
- ✅ **Task Scheduler Scripts** - Windows automation
- ✅ **Qwen Code Skill** (`.qwen/skills/ai-employee-silver/`) - Documented skill
- ✅ **Execution Logging** - All actions logged with details

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                      WATCHERS LAYER                         │
├─────────────────┬─────────────────┬─────────────────────────┤
│   Filesystem    │      Gmail      │       WhatsApp          │
│   (Inbox/)      │   (Gmail API)   │   (Playwright + Web)    │
└────────┬────────┴────────┬────────┴──────────┬──────────────┘
         │                 │                   │
         └─────────────────┼───────────────────┘
                           │
                           ↓
              ┌────────────────────────┐
              │   Needs_Action/ Folder │
              └───────────┬────────────┘
                          │
                          ↓
              ┌────────────────────────┐
              │     Orchestrator       │
              │  (Analyzes Complexity) │
              └───────────┬────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ↓               ↓               ↓
   ┌──────────┐   ┌──────────┐   ┌──────────────┐
   │ Simple   │   │ Complex  │   │  Sensitive   │
   │(1-2 steps)│   │(3+ steps)│   │  (Approval)  │
   └────┬─────┘   └────┬─────┘   └──────┬───────┘
        │              │                │
        ↓              ↓                ↓
   Direct Qwen   Create Plan.md   Pending_Approval/
   Processing    in Plans/              │
        │              │                │
        │              │                ↓
        │              │         Human Review
        │              │                │
        │              │         ┌──────┴──────┐
        │              │         │  Approved/  │
        │              │         └──────┬──────┘
        │              │                │
        └──────────────┴────────────────┘
                       │
                       ↓
              ┌────────────────┐
              │  Execute Action │
              │  (MCP Server)   │
              └────────┬────────┘
                       │
                       ↓
              ┌────────────────┐
              │  Move to Done/ │
              │  Update Logs   │
              └────────────────┘
```

## Troubleshooting

### Qwen Code not found
Ensure Qwen Code CLI is installed and in your PATH:
```bash
qwen --version
```

### Python dependencies not found
```bash
cd AI_Employee_Vault\src
pip install -r requirements.txt
playwright install chromium
```

### Gmail Watcher authentication fails
1. Delete existing token: `.cache\gmail_token.pickle`
2. Re-run Gmail Watcher manually
3. Check credentials.json is valid

### WhatsApp Watcher shows QR code
1. First run requires QR code scan
2. Run manually: `python whatsapp_watcher.py ..`
3. Scan QR with WhatsApp mobile app
4. Session saved for future runs

### Orchestrator not processing
- Check logs in `Logs/` folder
- Verify Qwen Code is configured
- Ensure items are in `Needs_Action/` folder
- Check if Qwen Code process timed out (default: 300 seconds)

### Task Scheduler not starting
1. Open Task Scheduler (taskschd.msc)
2. Navigate to: Task Scheduler Library → AI-Employee
3. Check task history for errors
4. Verify Python is in PATH

## Security Notes

- Never commit `.cache` folder with credentials
- Keep your vault private (use .gitignore)
- Review all actions in Logs regularly
- Start with DRY_RUN mode for testing
- Never share `credentials.json` or token files

## Next Steps (Gold Tier)

- Odoo accounting integration
- Social media posting (LinkedIn, Twitter, Facebook)
- Ralph Wiggum loop for autonomous multi-step completion
- Weekly CEO Briefing generation
- Comprehensive audit logging

## License

MIT License - Build your own AI Employee!
