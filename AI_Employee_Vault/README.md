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

## Bronze Tier Deliverables

✅ Obsidian vault with Dashboard.md and Company_Handbook.md
✅ One working Watcher script (Filesystem Watcher)
✅ Claude Code integration for processing
✅ Basic folder structure: /Inbox, /Needs_Action, /Done

## Troubleshooting

### Qwen Code not found
Ensure Qwen Code CLI is installed and in your PATH.

### Python module not found
```bash
pip install watchdog
```

### Watcher not detecting files
- Ensure the Inbox folder path is correct
- Check file permissions
- Verify the watcher process is running

### Orchestrator not processing
- Check logs in `Logs/` folder
- Verify Claude Code is configured
- Ensure items are in `Needs_Action/` folder

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
