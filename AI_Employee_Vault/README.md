# AI Employee Vault - Bronze Tier

A local-first, agent-driven personal automation system powered by Qwen Code and Obsidian.

## Quick Start

### Prerequisites

1. **Qwen Code** - Ensure Qwen Code CLI is installed and configured
2. **Python 3.13+** - Download from python.org
3. **Obsidian** - Download from obsidian.md

### Installation

1. **Install Python dependencies:**

```bash
cd AI_Employee_Vault/src
pip install -r requirements.txt
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

**Terminal 1 - Start the File Watcher:**

```bash
cd AI_Employee_Vault/src
python filesystem_watcher.py ..
```

This watches the `Inbox` folder for new files.

**Terminal 2 - Start the Orchestrator:**

```bash
cd AI_Employee_Vault/src
python orchestrator.py ..
```

This processes items and triggers Qwen Code.

## Where to See Qwen Code's Output

**Qwen Code's response appears in Terminal 2 (the orchestrator terminal).**

When a task is processed, you'll see the output directly in the terminal:

```
============================================================
[AI] QWEN CODE PROCESSING: FILE_20260318_xxx.md
============================================================

[Qwen Code's response/answer appears here - this is where
 you'll see the AI's answer to your question/task]

============================================================
[OK] QWEN CODE COMPLETED: FILE_20260318_xxx.md
============================================================

[DONE] File moved to: Done/FILE_20260318_xxx.md
```

**Tip:** Keep Terminal 2 visible to watch the AI's responses in real-time!

### Testing the Workflow

1. **Drop a test file** in the `Inbox` folder:
   ```
   AI_Employee_Vault/Inbox/test_task.txt
   ```

2. **Watch the magic happen:**
   - Filesystem Watcher detects the file
   - Creates an action file in `Needs_Action/`
   - Orchestrator triggers Qwen Code
   - Qwen processes the task and creates a plan
   - File moves to `Done/` when complete

3. **Check the Dashboard.md** in Obsidian for status updates

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
├── Briefings/            # CEO briefings (future)
├── Accounting/           # Financial records (future)
└── src/                  # Python source code
    ├── base_watcher.py
    ├── filesystem_watcher.py
    ├── orchestrator.py
    └── requirements.txt
```

## Configuration

### Customize Company Handbook

Edit `Company_Handbook.md` to set your rules:
- Financial thresholds
- Communication guidelines
- Working hours
- Escalation rules

### Adjust Check Intervals

```bash
# Filesystem watcher (default: 5 seconds)
python filesystem_watcher.py .. --interval 10

# Orchestrator (default: 30 seconds)
python orchestrator.py .. --interval 60
```

## Bronze Tier Deliverables (COMPLETE ✅)

### Core Requirements
- ✅ Obsidian vault with Dashboard.md and Company_Handbook.md
- ✅ One working Watcher script (Filesystem Watcher)
- ✅ Qwen Code integration for processing
- ✅ Basic folder structure: /Inbox, /Needs_Action, /Done, /Plans, /Pending_Approval, /Approved, /Rejected, /Logs

### Additional Features Implemented
- ✅ **Qwen Code Skill** (`.qwen/skills/ai-employee-bronze/`) - Documented skill for AI Employee processing
- ✅ **Plan.md Generation** - Automatic plan creation for complex tasks (3+ steps)
- ✅ **Task Complexity Analysis** - Orchestrator analyzes tasks and creates plans when needed
- ✅ **Processing Logs** - All actions logged to `/Logs/YYYY-MM-DD.md`
- ✅ **Human-in-the-Loop Structure** - Approval workflow folders ready for Silver tier

## How It Works

```
1. Drop file in Inbox/
       ↓
2. Filesystem Watcher detects → Creates action file in Needs_Action/
       ↓
3. Orchestrator analyzes complexity
       ↓
   ┌─────────────┬─────────────┐
   │  Simple     │   Complex   │
   │  (1-2 steps)│  (3+ steps) │
   └──────┬──────┴──────┬──────┘
          │             │
          ↓             ↓
   Direct processing  Create Plan.md
          │             │
          └──────┬──────┘
                 ↓
   4. Qwen Code processes task
                 ↓
   5. File moved to Done/
   6. Plan status updated (if created)
   7. Log entry created
```

## Example Log Output

```
2026-03-18 11:30:50 - Created action file: FILE_20260318_113050_test_live.md
2026-03-18 11:31:06 - Task complexity: {'is_complex': True, ...}
2026-03-18 11:31:06 - Task is complex, creating Plan.md
2026-03-18 11:31:06 - Created plan file: PLAN_...md
2026-03-18 11:31:31 - Qwen Code completed processing
2026-03-18 11:31:31 - Updated plan status: completed
2026-03-18 11:31:31 - Moved to Done: FILE_...md
```

## Troubleshooting

### Qwen Code not found
Ensure Qwen Code CLI is installed and in your PATH. Run:
```bash
qwen --version
```

### Python module not found
```bash
pip install watchdog
```

### Watcher not detecting files
- Ensure the Inbox folder path is correct
- Check file permissions
- Verify the watcher process is running
- Check logs in `Logs/YYYY-MM-DD.log`

### Orchestrator not processing
- Check logs in `Logs/` folder
- Verify Qwen Code is configured: `qwen --version`
- Ensure items are in `Needs_Action/` folder
- Check if Qwen Code process timed out (default: 300 seconds)

### Plan.md not created for complex task
- Task complexity is determined by:
  - Multiple checkbox items (`[ ]`)
  - Multiple questions (`?`)
  - Complex keywords (research, analyze, compare, etc.)
- Check orchestrator logs for complexity analysis

### File stuck in Needs_Action/
- Check Qwen Code output in logs
- Task may require approval (check `Pending_Approval/`)
- Qwen Code may have encountered an error

## Next Steps (Silver Tier)

- Add Gmail Watcher
- Add WhatsApp Watcher
- Implement MCP servers for external actions
- Create human-in-the-loop approval workflow
- Add scheduling via cron/Task Scheduler

## Security Notes

- Never commit `.env` files with credentials
- Keep your vault private (use .gitignore)
- Review all actions in Logs regularly
- Start with DRY_RUN mode for testing

## License

MIT License - Build your own AI Employee!
