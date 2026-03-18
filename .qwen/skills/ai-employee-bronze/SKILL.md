---
name: ai-employee-bronze
description: |
  AI Employee Bronze Tier skill for processing tasks from the Obsidian vault.
  Handles file drops, creates action plans, processes tasks, and manages
  the Human-in-the-Loop approval workflow.
  Use when processing items from Needs_Action folder or managing vault workflow.
---

# AI Employee Bronze Tier Skill

Process tasks from the AI Employee Obsidian vault workflow.

## Quick Start

### Process a Task from Needs_Action

```bash
qwen -p "Process the task in AI_Employee_Vault/Needs_Action/ using the AI Employee Bronze skill"
```

### Process All Pending Tasks

```bash
qwen -p "Process all files in AI_Employee_Vault/Needs_Action/ folder using AI Employee Bronze skill"
```

## Workflow Overview

```
1. Read task from /Needs_Action/
2. Read Company_Handbook.md for rules
3. Determine action complexity:
   - Simple (1-2 steps): Execute directly
   - Complex (3+ steps): Create Plan.md
4. Execute or request approval
5. Move to /Done/ when complete
6. Update Dashboard.md
```

## Task Processing Rules

### Simple Tasks (Execute Directly)
- File operations within vault
- Reading and summarizing documents
- Creating new markdown files
- Moving files between folders

### Complex Tasks (Create Plan.md)
- Multi-step workflows (3+ steps)
- Tasks requiring research
- Tasks with dependencies

### Sensitive Actions (Require Approval)
- Moving files outside vault
- Deleting files
- Financial decisions
- External communications

## Creating a Plan.md

For complex tasks, create a plan file:

```markdown
---
created: 2026-03-17T12:00:00Z
status: in_progress
task_file: Needs_Action/FILE_xxx.md
---

# Plan: [Task Name]

## Objective
[Clear statement of what needs to be accomplished]

## Steps
- [ ] Step 1: Description
- [ ] Step 2: Description
- [ ] Step 3: Description

## Resources Needed
- [List any files or information needed]

## Approval Required
[Yes/No - specify if human approval is needed]
```

## Human-in-the-Loop Pattern

For sensitive actions, create an approval request:

```markdown
---
type: approval_request
action: [action_type]
created: 2026-03-17T12:00:00Z
status: pending
---

# Approval Required

## Action Details
- **Action**: [Description]
- **Reason**: [Why this is needed]

## To Approve
Move this file to `/Approved/` folder.

## To Reject
Move this file to `/Rejected/` folder.
```

## File Movement Rules

| From | To | When |
|------|-----|------|
| `/Needs_Action/` | `/Done/` | Task completed successfully |
| `/Needs_Action/` | `/Plans/` | Complex task requiring plan |
| `/Needs_Action/` | `/Pending_Approval/` | Sensitive action needed |
| `/Pending_Approval/` | `/Approved/` | Human approved action |
| `/Pending_Approval/` | `/Rejected/` | Human rejected action |
| `/Approved/` | `/Done/` | Action executed |

## Dashboard Update Pattern

After completing a task, update `Dashboard.md`:

1. Read current dashboard
2. Update "Recent Activity" table
3. Update "Pending Tasks" count
4. Update "Completed Today" count
5. Write updated dashboard

## Example: Process a File Drop

```bash
qwen -p "
Using AI Employee Bronze skill:
1. Read AI_Employee_Vault/Needs_Action/FILE_xxx.md
2. Read Company_Handbook.md for rules
3. Determine required action
4. Execute or create plan
5. Move to Done when complete
6. Update Dashboard.md
"
```

## Example: Create a Plan for Complex Task

```bash
qwen -p "
Using AI Employee Bronze skill:
This task requires multiple steps:
1. Research the topic
2. Create summary document
3. Get approval
4. Send notification

Create a Plan.md in /Plans/ folder with checkboxes.
"
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Task not moving to Done | Ensure file permissions allow rename |
| Plan.md not created | Check if task has 3+ distinct steps |
| Approval not requested | Review Company_Handbook.md rules |
| Dashboard not updating | Verify Dashboard.md is not locked |

## Logging

All actions should be logged to `/Logs/YYYY-MM-DD.md`:

```markdown
---
timestamp: 2026-03-17T12:00:00Z
action: [action_type]
file: [filename]
result: [success/failure]
---

# Processing Log Entry

- **File**: [filename]
- **Processed at**: [timestamp]
- **Result**: [outcome]
```
