# Personal AI FTE - Project Context

## Project Overview

This repository contains a blueprint and implementation framework for building a **Personal AI Employee** (Digital FTE - Full-Time Equivalent). It's a local-first, agent-driven automation system where an AI agent powered by **Qwen Code** and **Obsidian** proactively manages personal and business affairs 24/7.

### Core Architecture

| Layer | Component | Purpose |
|-------|-----------|---------|
| **Brain** | Qwen Code | Reasoning engine for decision-making |
| **Memory/GUI** | Obsidian (Markdown) | Dashboard and long-term memory |
| **Senses** | Python Watcher Scripts | Monitor Gmail, WhatsApp, filesystems |
| **Hands** | MCP Servers | External actions (email, browser, payments) |

### Key Concepts

- **Watcher Pattern**: Lightweight Python scripts run continuously, monitoring inputs and creating actionable `.md` files in `/Needs_Action` folder
- **Ralph Wiggum Loop**: A Stop hook pattern that keeps Claude iterating until multi-step tasks are complete
- **Human-in-the-Loop**: Sensitive actions require approval via file movement (`/Pending_Approval` → `/Approved`)
- **Monday Morning CEO Briefing**: Autonomous weekly audit generating business insights

## Repository Structure

```
Personal-AI-FTE/
├── .qwen/skills/               # Qwen Code skills for AI assistance
│   └── browsing-with-playwright/
│       ├── SKILL.md            # Skill documentation
│       ├── references/
│       │   └── playwright-tools.md  # MCP tool reference
│       └── scripts/
│           ├── mcp-client.py   # Universal MCP client (HTTP + stdio)
│           ├── start-server.sh # Start Playwright MCP server
│           ├── stop-server.sh  # Stop Playwright MCP server
│           └── verify.py       # Server health check
├── Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md  # Main blueprint
├── skills-lock.json            # Skill version tracking
└── .gitattributes              # Git line ending configuration
```

## Building and Running

### Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| Claude Code | Active subscription | Primary reasoning engine |
| Obsidian | v1.10.6+ | Knowledge base & dashboard |
| Python | 3.13+ | Watcher scripts & orchestration |
| Node.js | v24+ LTS | MCP servers |
| GitHub Desktop | Latest | Version control |

### Playwright MCP Server

The repository includes a ready-to-use Playwright MCP skill for browser automation.

```bash
# Start the server (keeps browser context alive)
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh

# Verify server is running
python .qwen/skills/browsing-with-playwright/scripts/verify.py

# Stop the server (closes browser first)
bash .qwen/skills/browsing-with-playwright/scripts/stop-server.sh
```

### MCP Client Usage

```bash
# List available tools
python .qwen/skills/browsing-with-playwright/scripts/mcp-client.py list -u http://localhost:8808

# Call a tool (navigate)
python .qwen/skills/browsing-with-playwright/scripts/mcp-client.py call \
  -u http://localhost:8808 \
  -t browser_navigate \
  -p '{"url": "https://example.com"}'

# Take a snapshot (get page state)
python .qwen/skills/browsing-with-playwright/scripts/mcp-client.py call \
  -u http://localhost:8808 \
  -t browser_snapshot \
  -p '{}'
```

## Development Conventions

### File Organization

- **Obsidian Vault Structure** (to be created by user):
  ```
  AI_Employee_Vault/
  ├── Dashboard.md           # Real-time summary
  ├── Company_Handbook.md    # Rules of engagement
  ├── Inbox/                 # Raw incoming items
  ├── Needs_Action/          # Items requiring processing
  ├── In_Progress/<agent>/   # Claimed by specific agent
  ├── Pending_Approval/      # Awaiting human approval
  ├── Approved/              # Approved actions (triggers execution)
  ├── Rejected/              # Declined actions
  ├── Done/                  # Completed tasks
  ├── Plans/                 # Generated plans (Plan.md)
  ├── Briefings/             # CEO briefings
  └── Accounting/            # Financial records
  ```

### Agent Skills Pattern

All AI functionality should be implemented as Agent Skills:
- Skills are discoverable by Qwen Code
- Skills encapsulate specific domain functionality
- Skills can be shared and versioned (see `skills-lock.json`)

### Watcher Script Pattern

All Watcher scripts follow a common base class:

```python
from base_watcher import BaseWatcher

class MyWatcher(BaseWatcher):
    def check_for_updates(self) -> list:
        '''Return list of new items to process'''
        pass

    def create_action_file(self, item) -> Path:
        '''Create .md file in Needs_Action folder'''
        pass
```

## Key Files Reference

| File | Description |
|------|-------------|
| `Personal AI Employee Hackathon 0_...md` | Complete architectural blueprint with tiered deliverables (Bronze/Silver/Gold/Platinum) |
| `AI_Employee_Vault/README.md` | **Bronze Tier Complete** - Setup and usage guide |
| `AI_Employee_Vault/src/orchestrator.py` | Main orchestrator with Plan.md generation |
| `AI_Employee_Vault/src/filesystem_watcher.py` | File drop watcher (real-time monitoring) |
| `.qwen/skills/ai-employee-bronze/SKILL.md` | AI Employee Bronze Skill documentation |
| `.qwen/skills/browsing-with-playwright/SKILL.md` | Playwright MCP usage guide |
| `.qwen/skills/browsing-with-playwright/scripts/mcp-client.py` | Universal MCP client supporting HTTP and stdio transports |
| `.qwen/skills/browsing-with-playwright/references/playwright-tools.md` | Complete tool reference (22 tools available) |

## Achievement Tiers

| Tier | Time | Deliverables | Status |
|------|------|--------------|--------|
| **Bronze** | 8-12h | Obsidian vault, one Watcher, basic folder structure, Qwen Code Skill, Plan.md generation | ✅ COMPLETE |
| **Silver** | 20-30h | Multiple Watchers, one MCP server, HITL workflow, Task Scheduler | 📋 Ready to start |
| **Gold** | 40+h | Full integration, Odoo accounting, social media, Ralph Wiggum loop | ⏳ Pending |
| **Platinum** | 60+h | Cloud deployment, work-zone specialization, A2A upgrade | ⏳ Pending |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Playwright server not responding | Run `bash scripts/stop-server.sh && bash scripts/start-server.sh` |
| Element not found in browser | Run `browser_snapshot` first to get current element refs |
| Qwen Code exits prematurely | Implement Ralph Wiggum Stop hook pattern |
| Watcher not triggering | Check file system permissions and Python dependencies |

## External Resources

- Qwen Code Documentation
- Agent Skills Overview
- MCP Server Documentation
- Ralph Wiggum Pattern (for persistent task completion)
- Oracle Cloud Free VMs (for Platinum tier deployment)
