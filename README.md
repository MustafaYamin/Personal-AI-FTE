# Personal AI Employee (Digital FTE)

> **Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.**

A comprehensive blueprint and implementation framework for building a **Personal AI Employee** (Digital Full-Time Equivalent) powered by **Qwen Code** and **Obsidian**. This AI agent proactively manages personal and business affairs 24/7 using a local-first, privacy-focused architecture.

[![Status](https://img.shields.io/badge/status-bronze--complete-brightgreen)](https://github.com/MustafaYamin/Personal-AI-FTE.git)
[![Tier](https://img.shields.io/badge/tier-Bronze-orange)](https://github.com/MUSTAFA/Personal-AI-FTE)
[![Qwen Code](https://img.shields.io/badge/AI-Qwen%20Code-blue)](https://qwen.ai)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Achievement Tiers](#achievement-tiers)
- [✅ Bronze Tier - COMPLETE](#-bronze-tier---complete)
- [📋 Silver Tier - TODO](#-silver-tier---todo)
- [📋 Gold Tier - TODO](#-gold-tier---todo)
- [📋 Platinum Tier - TODO](#-platinum-tier---todo)
- [Quick Start](#quick-start)
- [Detailed Setup Guide](#detailed-setup-guide)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

This project implements a **Digital FTE (Full-Time Equivalent)** - an AI agent that works like a human employee but with superhuman capabilities:

| Feature | Human FTE | Digital FTE |
|---------|-----------|-------------|
| Availability | 40 hours/week | **168 hours/week (24/7)** |
| Monthly Cost | $4,000 - $8,000+ | **$50 - $200** (API costs) |
| Ramp-up Time | 3-6 months | **Instant** |
| Consistency | 85-95% accuracy | **99%+ consistency** |
| Scaling | Linear (hire more) | **Exponential (duplicate instantly)** |
| Cost per Task | ~$5.00 | **~$0.50** |

**The 'Aha!' Moment:** A Digital FTE works 8,760 hours/year vs a human's 2,000 hours. That's **85-90% cost savings**—the threshold where CEOs approve projects without debate.

---

## Architecture

### Core Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    PERSONAL AI EMPLOYEE                     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL SOURCES                         │
│    Gmail  │  WhatsApp  │  Bank APIs  │  Files  │  Social   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  PERCEPTION LAYER (Watchers)                │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐              │
│  │Gmail Watcher│ │WhatsApp Watcher│ │File Watcher│         │
│  │  (Python)  │ │ (Playwright)│ │  (Python)  │            │
│  └─────┬──────┘ └─────┬──────┘ └─────┬──────┘             │
└────────┼──────────────┼──────────────┼─────────────────────┘
         │              │              │
         ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│                  OBSIDIAN VAULT (Memory)                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Dashboard.md │ Company_Handbook.md │ Business_Goals  │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │ /Inbox │ /Needs_Action │ /Done │ /Plans │ /Approved  │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                 REASONING LAYER (Qwen Code)                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Read → Think → Plan → Execute → Request Approval    │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    ACTION LAYER (MCP)                       │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐              │
│  │ Email MCP  │ │Browser MCP │ │Payment MCP │              │
│  └────────────┘ └────────────┘ └────────────┘              │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

| Layer | Component | Technology | Purpose |
|-------|-----------|------------|---------|
| **Brain** | Qwen Code | LLM | Reasoning engine |
| **Memory** | Obsidian | Markdown | Dashboard + long-term memory |
| **Senses** | Watcher Scripts | Python | Monitor Gmail, WhatsApp, files |
| **Hands** | MCP Servers | Node.js/Python | External actions |

---

## Achievement Tiers

This project follows a tiered development approach. Each tier builds on the previous one.

| Tier | Time | Status | Deliverables |
|------|------|--------|--------------|
| **Bronze** | 8-12h | ✅ **COMPLETE** | Vault, 1 Watcher, Qwen Code integration |
| **Silver** | 20-30h | 📋 TODO | Multiple Watchers, MCP server, HITL workflow |
| **Gold** | 40+h | 📋 TODO | Full integration, Odoo, social media, Ralph Wiggum loop |
| **Platinum** | 60+h | 📋 TODO | Cloud deployment, work-zone specialization |

---

## ✅ Bronze Tier - COMPLETE

### Achievements

- ✅ **Obsidian Vault Structure**
  - `Dashboard.md` - Real-time status dashboard
  - `Company_Handbook.md` - Rules of engagement
  - All required folders created and functional

- ✅ **Filesystem Watcher**
  - Real-time monitoring of `Inbox/` folder
  - Automatic action file creation in `Needs_Action/`
  - Uses Watchdog library for efficient file monitoring

- ✅ **Qwen Code Integration**
  - Orchestrator triggers Qwen Code for task processing
  - Output displayed in terminal
  - Automatic file movement to `Done/` after processing

- ✅ **Plan.md Generation**
  - Automatic complexity analysis of tasks
  - Plan files created for complex tasks (3+ steps)
  - Plan status updated on completion

- ✅ **Qwen Code Skill**
  - Documented skill in `.qwen/skills/ai-employee-bronze/`
  - Templates for plans, approvals, and logs
  - Registered in `skills-lock.json`

- ✅ **Logging System**
  - Daily log files in `/Logs/`
  - Processing entries with timestamps
  - Error tracking and debugging support

### Test Results

```
✅ Filesystem Watcher: Detects files in Inbox/
✅ Orchestrator: Triggers Qwen Code every 30s
✅ Qwen Code: Processes tasks and outputs to terminal
✅ File Movement: Tasks move to Done/ after processing
✅ Plan Generation: Complex tasks get Plan.md files
✅ Logging: All actions logged to /Logs/YYYY-MM-DD.log
```

---

## 📋 Silver Tier - TODO

### Planned Features

- [ ] **Second Watcher Script**
  - [ ] Gmail Watcher (monitor important emails)
  - [ ] OR WhatsApp Watcher (keyword-based message detection)

- [ ] **HITL Approval Workflow**
  - [ ] Process files in `/Pending_Approval/` folder
  - [ ] Execute actions when moved to `/Approved/`
  - [ ] Move rejected files to `/Rejected/`

- [ ] **MCP Server Integration**
  - [ ] Email MCP server (send responses)
  - [ ] OR Browser MCP (Playwright for web automation)

- [ ] **Task Scheduler**
  - [ ] Windows Task Scheduler setup script
  - [ ] Auto-start on system boot
  - [ ] Scheduled daily briefings

- [ ] **Enhanced Qwen Code Skill**
  - [ ] Multi-step task coordination
  - [ ] Better error handling
  - [ ] Context preservation across sessions

### Estimated Time: 20-30 hours

---

## 📋 Gold Tier - TODO

### Planned Features

- [ ] **Full Cross-Domain Integration**
  - [ ] Personal affairs (Gmail, WhatsApp, Bank)
  - [ ] Business operations (Social Media, Payments, Tasks)

- [ ] **Odoo Accounting Integration**
  - [ ] Local Odoo Community setup
  - [ ] MCP server for Odoo JSON-RPC APIs
  - [ ] Transaction logging and categorization

- [ ] **Social Media Integration**
  - [ ] Facebook/Instagram posting
  - [ ] Twitter (X) integration
  - [ ] LinkedIn auto-posting

- [ ] **Multiple MCP Servers**
  - [ ] Email MCP
  - [ ] Browser MCP
  - [ ] Calendar MCP
  - [ ] Payment MCP

- [ ] **Weekly CEO Briefing**
  - [ ] Autonomous business audit
  - [ ] Revenue tracking
  - [ ] Bottleneck identification
  - [ ] Proactive suggestions

- [ ] **Ralph Wiggum Loop**
  - [ ] Persistent task completion
  - [ ] Multi-step autonomous workflows
  - [ ] Error recovery and retry logic

- [ ] **Comprehensive Audit Logging**
  - [ ] All actions logged with metadata
  - [ ] Searchable log database
  - [ ] Weekly log summaries

### Estimated Time: 40+ hours

---

## 📋 Platinum Tier - TODO

### Planned Features

- [ ] **Cloud Deployment (24/7)**
  - [ ] Oracle Cloud Free VM setup
  - [ ] Always-on watchers and orchestrator
  - [ ] Health monitoring and auto-recovery

- [ ] **Work-Zone Specialization**
  - [ ] Cloud agent: Email triage + draft replies
  - [ ] Local agent: Approvals + WhatsApp + payments
  - [ ] Clear separation of responsibilities

- [ ] **Vault Sync (Phase 1)**
  - [ ] Git-based synchronization
  - [ ] Claim-by-move rule implementation
  - [ ] Single-writer rule for Dashboard.md

- [ ] **Security Hardening**
  - [ ] Secrets never sync (.env, tokens, sessions)
  - [ ] Encrypted vault storage
  - [ ] Access control lists

- [ ] **Odoo Cloud Deployment**
  - [ ] HTTPS configuration
  - [ ] Automated backups
  - [ ] Health monitoring

- [ ] **A2A Upgrade (Phase 2)**
  - [ ] Direct agent-to-agent messaging
  - [ ] Vault as audit record
  - [ ] Reduced file handoffs

### Estimated Time: 60+ hours

---

## Quick Start

### Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| [Qwen Code](https://qwen.ai) | Latest | Primary reasoning engine |
| [Python](https://python.org) | 3.13+ | Watcher scripts |
| [Obsidian](https://obsidian.md) | v1.10.6+ | Knowledge base |
| [Node.js](https://nodejs.org) | v24+ LTS | MCP servers (Silver+) |
| [Git](https://git-scm.com) | Latest | Version control |

### 5-Minute Setup

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/Personal-AI-FTE.git
cd Personal-AI-FTE

# 2. Install Python dependencies
cd AI_Employee_Vault/src
pip install -r requirements.txt

# 3. Verify Qwen Code
qwen --version

# 4. Open vault in Obsidian
# Launch Obsidian → Open folder as vault → Select AI_Employee_Vault
```

### Run the System

**Terminal 1 - Watcher:**
```bash
cd AI_Employee_Vault/src
python filesystem_watcher.py ..
```

**Terminal 2 - Orchestrator:**
```bash
cd AI_Employee_Vault/src
python orchestrator.py ..
```

**Test it:**
```bash
echo "What is 2+2? Answer briefly." > AI_Employee_Vault/Inbox/test.txt
```

**Watch Terminal 2 for Qwen Code's output!**

---

## Detailed Setup Guide

### Step 1: Install Prerequisites

#### Qwen Code
```bash
# Install via npm
npm install -g @qwen-code/qwen-code

# Verify installation
qwen --version
```

#### Python 3.13+
```bash
# Windows: Download from python.org
# macOS: brew install python@3.13
# Linux: sudo apt install python3.13 python3.13-venv

# Verify
python --version  # Should be 3.13 or higher
```

#### Obsidian
1. Download from [obsidian.md/download](https://obsidian.md/download)
2. Install and launch
3. Click "Open folder as vault"
4. Select `AI_Employee_Vault` folder

### Step 2: Clone and Setup

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/Personal-AI-FTE.git
cd Personal-AI-FTE

# Create Python virtual environment (recommended)
cd AI_Employee_Vault/src
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Company Handbook

Edit `AI_Employee_Vault/Company_Handbook.md` to set your rules:

```markdown
## Financial Actions
| Action Type | Auto-Approve | Requires Approval |
|-------------|-------------|-------------------|
| Payments | Never | All payments |
| Invoices | <$100 | >$100 or new clients |

## Communication Rules
- Always be polite and professional
- Response time target: <24 hours
- Include "Sent with AI assistance" signature
```

### Step 4: Customize Dashboard

Edit `AI_Employee_Vault/Dashboard.md` to track your metrics:

```markdown
## Quick Status
| Metric | Your Value |
|--------|------------|
| Revenue MTD | $X,XXX |
| Active Projects | X |
```

### Step 5: Test the System

```bash
# Terminal 1 - Start Watcher
cd AI_Employee_Vault/src
python filesystem_watcher.py ..

# Terminal 2 - Start Orchestrator
cd AI_Employee_Vault/src
python orchestrator.py ..

# Terminal 3 - Create test task
echo "Summarize: The quick brown fox jumps over the lazy dog." > AI_Employee_Vault/Inbox/test_summary.txt
```

**Expected Output in Terminal 2:**
```
============================================================
[AI] QWEN CODE PROCESSING: FILE_20260318_xxx.md
============================================================

The quick brown fox jumps over the lazy dog is a famous
pangram that contains every letter of the alphabet...

============================================================
[OK] QWEN CODE COMPLETED: FILE_20260318_xxx.md
============================================================

[DONE] File moved to: Done/FILE_20260318_xxx.md
```

---

## Usage

### Daily Workflow

1. **Morning**: Check `Dashboard.md` in Obsidian for status
2. **Throughout Day**: Drop tasks in `Inbox/` folder
3. **Watch Terminal 2**: See Qwen Code's responses in real-time
4. **Evening**: Review `/Logs/` for activity summary

### Task Types

#### Simple Tasks (Direct Execution)
```bash
echo "What is the weather today?" > Inbox/question.txt
```

#### Complex Tasks (Auto Plan Generation)
```bash
echo "Research AI trends and create a summary report with recommendations." > Inbox/research.txt
```

#### Sensitive Actions (Require Approval)
Files requiring approval are moved to `/Pending_Approval/`. Review and move to:
- `/Approved/` - Execute the action
- `/Rejected/` - Decline the action

### File Movement Rules

| From | To | When |
|------|-----|------|
| `Inbox/` | `Needs_Action/` | Watcher detects new file |
| `Needs_Action/` | `Plans/` | Complex task detected |
| `Needs_Action/` | `Pending_Approval/` | Sensitive action needed |
| `Pending_Approval/` | `Approved/` | Human approves |
| `Pending_Approval/` | `Rejected/` | Human rejects |
| `Needs_Action/` or `Approved/` | `Done/` | Task completed |

---

## Project Structure

```
Personal-AI-FTE/
├── README.md                          # This file
├── QWEN.md                            # Qwen Code context
├── skills-lock.json                   # Skill version tracking
├── .qwen/
│   └── skills/
│       ├── ai-employee-bronze/        # ✅ Bronze Tier Skill
│       │   ├── SKILL.md               # Skill documentation
│       │   └── references/
│       │       └── templates.md       # Plan/approval templates
│       └── browsing-with-playwright/  # (Silver+ Tier)
├── AI_Employee_Vault/                 # ✅ Bronze Tier Vault
│   ├── README.md                      # Vault-specific README
│   ├── Dashboard.md                   # Real-time status
│   ├── Company_Handbook.md            # Rules of engagement
│   ├── Inbox/                         # Drop folder for tasks
│   ├── Needs_Action/                  # Tasks awaiting processing
│   ├── Plans/                         # Generated action plans
│   ├── Pending_Approval/              # Awaiting human approval
│   ├── Approved/                      # Approved for execution
│   ├── Rejected/                      # Declined actions
│   ├── Done/                          # Completed tasks
│   ├── Logs/                          # Activity logs
│   ├── Briefings/                     # CEO briefings (Gold+)
│   ├── Accounting/                    # Financial records (Gold+)
│   └── src/
│       ├── base_watcher.py            # Abstract base class
│       ├── filesystem_watcher.py      # File monitoring
│       ├── orchestrator.py            # Main orchestrator
│       └── requirements.txt           # Python dependencies
└── Personal AI Employee Hackathon 0_...md  # Full blueprint
```

---

## Configuration

### Orchestrator Settings

Edit `AI_Employee_Vault/src/orchestrator.py`:

```python
# Check interval (seconds)
orchestrator = Orchestrator(vault_path, check_interval=30)

# Timeout for Qwen Code (seconds)
timeout=300  # 5 minutes
```

### Watcher Settings

Edit `AI_Employee_Vault/src/filesystem_watcher.py`:

```python
# Check interval (seconds)
watcher = FilesystemWatcher(vault_path, check_interval=5)
```

### Company Handbook Rules

Edit `AI_Employee_Vault/Company_Handbook.md`:

```markdown
## Escalation Rules
- Flag transactions over $500
- Unknown contacts require approval
- Keywords: "urgent", "asap", "emergency" → immediate attention
```

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| `qwen: command not found` | Run `npm install -g @qwen-code/qwen-code` |
| `ModuleNotFoundError: watchdog` | Run `pip install -r requirements.txt` |
| Watcher not detecting files | Check file permissions, verify process is running |
| Orchestrator not processing | Check logs in `Logs/` folder |
| Qwen Code timeout | Increase timeout in `orchestrator.py` (default: 300s) |
| File stuck in `Needs_Action/` | Check Qwen Code output in Terminal 2 |
| Plan.md not created | Task needs 2+ complexity factors (questions, checkboxes, keywords) |

### Check Logs

```bash
# View today's log
type AI_Employee_Vault\Logs\2026-03-18.log
# macOS/Linux:
cat AI_Employee_Vault/Logs/2026-03-18.log
```

### Verify Processes

```bash
# Windows
tasklist | findstr python

# macOS/Linux
ps aux | grep python
```

### Restart System

```bash
# Kill all Python processes
taskkill /F /IM python.exe  # Windows
killall python3             # macOS/Linux

# Clear cache
del /Q AI_Employee_Vault\src\__pycache__\*

# Restart
cd AI_Employee_Vault/src
python filesystem_watcher.py .. &
python orchestrator.py ..
```

---

## Contributing

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Python: PEP 8 compliant
- Markdown: GitHub-flavored
- Comments: Minimal, focus on "why" not "what"

### Adding a New Watcher

1. Inherit from `base_watcher.BaseWatcher`
2. Implement `check_for_updates()` and `create_action_file()`
3. Add to `requirements.txt` if new dependencies needed
4. Test with sample data

Example:
```python
from base_watcher import BaseWatcher

class GmailWatcher(BaseWatcher):
    def check_for_updates(self) -> list:
        # Return list of new emails
        pass

    def create_action_file(self, email) -> Path:
        # Create .md file in Needs_Action/
        pass
```

---

## License

MIT License - Build your own AI Employee!

```
Copyright (c) 2026 Personal AI FTE Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Resources

### Documentation

- [Qwen Code Documentation](https://qwen.ai/docs)
- [Obsidian Help](https://help.obsidian.md)
- [Python Watchdog](https://pypi.org/project/watchdog/)

### Community

- [Wednesday Research Meetings](https://us06web.zoom.us/j/87188707642) - Wednesdays 10:00 PM
- [YouTube Channel](https://www.youtube.com/@panaversity) - Tutorials and recordings

### Related Projects

- [Agent Skills Overview](https://platform.qwen.ai/docs/agents/agent-skills)
- [MCP Server Documentation](https://github.com/modelcontextprotocol/servers)
- [Oracle Cloud Free VMs](https://www.oracle.com/cloud/free/) (for Platinum tier)

---

## Acknowledgments

Built with inspiration from the Personal AI Employee Hackathon 0 blueprint. Special thanks to the Qwen Code community and all contributors making autonomous AI agents accessible to everyone.

---

**Ready to build your Digital FTE?** Start with Bronze Tier and work your way up! 🚀

For questions or support, open an issue or join our Wednesday Research Meetings.
