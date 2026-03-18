#!/usr/bin/env python3
"""
Orchestrator - Master process for the AI Employee.

The orchestrator:
1. Monitors the Needs_Action folder for new items
2. Triggers Qwen Code to process pending items
3. Updates the Dashboard.md with current status
4. Manages the overall workflow

For Bronze Tier: Basic polling and Qwen Code triggering.
"""

import subprocess
import sys
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional


class Orchestrator:
    """
    Main orchestrator for the AI Employee system.

    Coordinates between watchers, Qwen Code, and the vault.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 30):
        """
        Initialize the orchestrator.
        
        Args:
            vault_path: Path to the Obsidian vault
            check_interval: How often to check for work (in seconds)
        """
        self.vault_path = Path(vault_path)
        self.check_interval = check_interval

        # Vault folders
        self.needs_action = self.vault_path / 'Needs_Action'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.done = self.vault_path / 'Done'
        self.plans = self.vault_path / 'Plans'
        self.logs = self.vault_path / 'Logs'
        self.dashboard = self.vault_path / 'Dashboard.md'

        # Ensure directories exist
        for folder in [self.needs_action, self.pending_approval, self.approved, self.rejected, self.done, self.plans, self.logs]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Track processing state
        self.last_process_time: Optional[datetime] = None
        self.items_processed = 0
        
    def _setup_logging(self):
        """Configure logging."""
        log_file = self.logs / f'{datetime.now().strftime("%Y-%m-%d")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('Orchestrator')
        
    def count_pending_items(self) -> dict:
        """
        Count items in each folder.
        
        Returns:
            Dictionary with counts for each folder
        """
        return {
            'needs_action': len(list(self.needs_action.glob('*.md'))),
            'pending_approval': len(list(self.pending_approval.glob('*.md'))),
            'approved': len(list(self.approved.glob('*.md'))),
            'done_today': len([
                f for f in self.done.glob('*.md')
                if f.stat().st_mtime > (datetime.now().timestamp() - 86400)
            ])
        }
    
    def update_dashboard(self):
        """Update the Dashboard.md with current status."""
        counts = self.count_pending_items()
        
        if self.dashboard.exists():
            content = self.dashboard.read_text()
            
            # Update pending tasks count
            content = content.replace(
                '| Pending Tasks | 0 |',
                f'| Pending Tasks | {counts["needs_action"]} |'
            )
            
            # Update awaiting approval count
            content = content.replace(
                '| Awaiting Approval | 0 |',
                f'| Awaiting Approval | {counts["pending_approval"]} |'
            )
            
            # Update completed today count
            content = content.replace(
                '| Completed Today | 0 |',
                f'| Completed Today | {counts["done_today"]} |'
            )
            
            # Update last check time
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            content = content.replace(
                '- **Last Check**: -',
                f'- **Last Check**: {now}'
            )
            
            # Update watcher status
            content = content.replace(
                '- **Watcher Status**: ⚪ Not running',
                '- **Watcher Status**: 🟢 Running'
            )
            
            # Update orchestrator status
            content = content.replace(
                '- **Orchestrator**: ⚪ Not running',
                '- **Orchestrator**: 🟢 Running'
            )
            
            self.dashboard.write_text(content)
            self.logger.debug('Dashboard updated')
    
    def get_next_item(self) -> Optional[Path]:
        """
        Get the next item to process from Needs_Action folder.
        
        Returns:
            Path to the next item, or None if no items
        """
        items = sorted(self.needs_action.glob('*.md'), key=lambda f: f.stat().st_mtime)
        return items[0] if items else None
    
    def analyze_task_complexity(self, item_path: Path) -> dict:
        """
        Analyze a task to determine its complexity.

        Args:
            item_path: Path to the task file

        Returns:
            Dictionary with complexity analysis
        """
        content = item_path.read_text(encoding='utf-8')
        
        # Count potential steps based on content
        steps_detected = []
        
        # Check for multiple action items
        if '[ ]' in content or '- [ ]' in content:
            steps_detected.extend(['checkbox_items'])
        
        # Check for multiple questions or requests
        question_count = content.count('?')
        if question_count > 1:
            steps_detected.append('multiple_questions')
        
        # Check for file attachments or references
        if 'attachment' in content.lower() or 'file:' in content.lower():
            steps_detected.append('has_attachments')
        
        # Check for complex keywords
        complex_keywords = ['research', 'analyze', 'compare', 'summarize multiple', 
                          'create plan', 'investigate', 'review all']
        for keyword in complex_keywords:
            if keyword in content.lower():
                steps_detected.append(f'keyword:{keyword}')
        
        # Determine complexity
        is_complex = len(steps_detected) >= 2 or question_count >= 2
        
        return {
            'is_complex': is_complex,
            'steps_detected': steps_detected,
            'question_count': question_count,
            'estimated_steps': max(1, len(steps_detected))
        }

    def create_plan_file(self, item_path: Path, complexity: dict) -> Path:
        """
        Create a Plan.md file for complex tasks.

        Args:
            item_path: Path to the original task file
            complexity: Complexity analysis dictionary

        Returns:
            Path to the created plan file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        plan_filename = f'PLAN_{timestamp}_{item_path.stem}.md'
        plan_path = self.plans / plan_filename
        
        # Read task content for context
        task_content = item_path.read_text(encoding='utf-8')
        
        plan_content = f'''---
created: {datetime.now().isoformat()}
status: in_progress
task_file: Needs_Action/{item_path.name}
priority: normal
complexity: {"complex" if complexity['is_complex'] else "simple"}
---

# Plan: {item_path.stem.replace('_', ' ').title()}

## Objective
Process the task from Needs_Action folder following Company Handbook rules.

## Task Analysis
- **Complexity**: {"Complex" if complexity['is_complex'] else "Simple"}
- **Steps Detected**: {len(complexity['steps_detected'])}
- **Factors**: {', '.join(complexity['steps_detected']) if complexity['steps_detected'] else 'Standard processing'}

## Steps
- [ ] Read task file: Needs_Action/{item_path.name}
- [ ] Read Company Handbook for rules
- [ ] Determine required action(s)
- [ ] Execute action or create approval request
- [ ] Update Dashboard.md
- [ ] Move task to Done folder

## Resources Needed
- Company_Handbook.md
- Dashboard.md (for updates)

## Approval Required
To be determined based on Company Handbook rules.

## Notes
<!-- Add any additional notes during processing -->

---
*Generated by AI Employee Bronze Tier Orchestrator*
'''
        
        plan_path.write_text(plan_content, encoding='utf-8')
        self.logger.info(f'Created plan file: {plan_path.name}')
        
        return plan_path

    def process_with_qwen(self, item_path: Path) -> bool:
        """
        Process an item using Qwen Code.

        Args:
            item_path: Path to the item to process

        Returns:
            True if processing succeeded, False otherwise
        """
        self.logger.info(f'Processing item: {item_path.name}')
        
        # Analyze task complexity
        complexity = self.analyze_task_complexity(item_path)
        self.logger.info(f'Task complexity: {complexity}')
        
        # Create Plan.md for complex tasks
        plan_path = None
        if complexity['is_complex']:
            self.logger.info(f'Task is complex, creating Plan.md')
            plan_path = self.create_plan_file(item_path, complexity)

        # Create prompt for Qwen Code - reference the AI Employee Bronze Skill
        prompt = f'''You are using the AI Employee Bronze Tier Skill to process a task.

TASK FILE: {item_path}
COMPANY HANDBOOK: {self.vault_path / 'Company_Handbook.md'}
DASHBOARD: {self.vault_path / 'Dashboard.md'}
'''
        
        if plan_path:
            prompt += f'PLAN FILE: {plan_path}\n\n'
            prompt += '''A Plan.md has been created for this complex task.

Your responsibilities:
1. Read the task file and understand the requirements
2. Read the Company Handbook for rules and guidelines
3. Follow the steps in the Plan.md
4. Update the Plan.md checkboxes as you complete each step
5. Execute actions or create approval requests as needed
6. When complete, update Dashboard.md with the activity

WRITE YOUR RESPONSE:
Create a file called 'RESPONSE_[task_filename].md' in the same folder as the task file with your detailed response/answer/output.
'''
        else:
            prompt += '''
Your responsibilities:
1. Read the task file and understand what needs to be done
2. Read the Company Handbook for rules and guidelines
3. Execute the task directly (it's a simple task)
4. If you discover the task is more complex than expected, create a Plan.md
5. For sensitive actions, create an approval request in Pending_Approval/
6. When complete, update Dashboard.md with the activity

WRITE YOUR RESPONSE:
Create a file called 'RESPONSE_[task_filename].md' in the same folder as the task file with your detailed response/answer/output.
For example, if the task file is 'Needs_Action/FILE_123.md', create 'Needs_Action/RESPONSE_FILE_123.md'
'''

        prompt += '''
IMPORTANT: 
1. Write your response/answer to a file BEFORE completing the task
2. After completing all work, output exactly: <TASK_COMPLETE/>
This signals the orchestrator to move the file to Done.
'''

        try:
            # Run Qwen Code with the prompt using -p flag
            # On Windows, use shell=True to properly resolve qwen.cmd
            # Output goes directly to terminal (not captured)
            import platform
            use_shell = platform.system() == 'Windows'
            
            print(f"\n{'='*60}")
            print(f"[AI] QWEN CODE PROCESSING: {item_path.name}")
            print(f"{'='*60}\n")
            
            result = subprocess.run(
                f'qwen -p "{prompt}"' if use_shell else ['qwen', '-p', prompt],
                cwd=str(self.vault_path),
                # NO capture - output goes to terminal
                timeout=300,
                encoding='utf-8',
                errors='replace',
                shell=use_shell
            )

            # Check if Qwen completed the task (returncode 0 means success)
            task_completed = result.returncode == 0

            print(f"\n{'='*60}")
            if task_completed:
                print(f"[OK] QWEN CODE COMPLETED: {item_path.name}")
            else:
                print(f"[ERROR] QWEN CODE ERROR: {item_path.name}")
            print(f"{'='*60}\n")

            if task_completed:
                self.logger.info(f'Qwen Code completed processing: {item_path.name}')
                self.items_processed += 1

                # Update plan status if one was created
                if plan_path and plan_path.exists():
                    try:
                        plan_content = plan_path.read_text(encoding='utf-8')
                        plan_content = plan_content.replace('status: in_progress', 'status: completed')
                        plan_content = plan_content.replace('To be determined', 'Completed - see Done folder')
                        plan_path.write_text(plan_content, encoding='utf-8')
                        self.logger.info(f'Updated plan status: {plan_path.name}')
                    except Exception as e:
                        self.logger.error(f'Error updating plan: {e}')

                # Move file to Done
                dest = self.done / item_path.name
                try:
                    # Check if file still exists (Qwen Code may have already moved it)
                    if item_path.exists():
                        item_path.rename(dest)
                        self.logger.info(f'Moved to Done: {dest.name}')
                        print(f"[DONE] File moved to: Done/{dest.name}\n")
                    else:
                        # File was already moved (possibly by Qwen Code's file tools)
                        # Check if it's already in Done
                        if dest.exists():
                            self.logger.info(f'File already in Done: {dest.name}')
                            print(f"[DONE] File already in: Done/{dest.name}\n")
                        else:
                            self.logger.warning(f'File disappeared: {item_path.name}')
                            print(f"[WARN] File not found: {item_path.name}\n")

                    # Log the processing result
                    log_entry = f'''---
timestamp: {datetime.now().isoformat()}
action: file_processed
file: {item_path.name}
result: success
plan_created: {"yes" if plan_path else "no"}
---

# Processing Log Entry

- **File**: {item_path.name}
- **Processed at**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Result**: Successfully processed by Qwen Code
- **Plan Created**: {"Yes - " + plan_path.name if plan_path else "No - simple task"}
- **Output**: Was displayed in terminal above

'''
                    log_file = self.logs / f'{datetime.now().strftime("%Y-%m-%d")}.md'
                    with open(log_file, 'a', encoding='utf-8') as f:
                        f.write(log_entry)

                except Exception as e:
                    self.logger.error(f'Error moving file to Done: {e}')

                return True
            else:
                self.logger.error(f'Qwen Code error: {result.stderr}')
                self.logger.error(f'Qwen Code stdout: {result.stdout}')
                return False

        except subprocess.TimeoutExpired:
            self.logger.error(f'Timeout processing: {item_path.name}')
            return False
        except FileNotFoundError as e:
            self.logger.error(f'Qwen Code not found: {e}')
            self.logger.error('Please ensure Qwen Code CLI is installed. Run: npm install -g @qwen-code/qwen-code')
            return False
        except Exception as e:
            self.logger.error(f'Error processing with Qwen: {e}')
            return False
    
    def process_approved_items(self):
        """
        Process items in the Approved folder.
        
        These items have human approval and can be executed directly.
        """
        approved_items = list(self.approved.glob('*.md'))
        
        for item in approved_items:
            self.logger.info(f'Processing approved item: {item.name}')
            # For Bronze tier, we just log and move to Done
            # Higher tiers would execute actual actions here
            
            # Move to Done
            dest = self.done / item.name
            item.rename(dest)
            self.logger.info(f'Moved to Done: {dest.name}')
    
    def run(self):
        """
        Main run loop.
        
        Continuously monitors folders and processes items.
        """
        self.logger.info('=' * 50)
        self.logger.info('AI Employee Orchestrator Starting')
        self.logger.info(f'Vault: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        self.logger.info('=' * 50)
        
        try:
            while True:
                # Update dashboard
                self.update_dashboard()
                
                # Check for approved items first
                self.process_approved_items()
                
                # Process needs_action items
                item = self.get_next_item()
                if item:
                    self.process_with_qwen(item)
                else:
                    self.logger.debug('No items to process')
                
                # Sleep until next check
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info('Orchestrator stopped by user')
        except Exception as e:
            self.logger.error(f'Fatal error: {e}')
            raise
        finally:
            # Update dashboard to show stopped status
            self.update_dashboard()
            self.logger.info('Orchestrator shutdown complete')


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print('Usage: python orchestrator.py <vault_path> [check_interval]')
        print('  vault_path: Path to the Obsidian vault')
        print('  check_interval: Check interval in seconds (optional, default: 30)')
        sys.exit(1)
    
    vault_path = sys.argv[1]
    check_interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    
    # Validate vault path
    if not Path(vault_path).exists():
        print(f'Error: Vault path does not exist: {vault_path}')
        sys.exit(1)
    
    orchestrator = Orchestrator(vault_path, check_interval)
    orchestrator.run()


if __name__ == '__main__':
    main()
