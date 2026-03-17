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
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'
        self.dashboard = self.vault_path / 'Dashboard.md'
        
        # Ensure directories exist
        for folder in [self.needs_action, self.pending_approval, self.approved, self.done, self.logs]:
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
    
    def process_with_qwen(self, item_path: Path) -> bool:
        """
        Process an item using Qwen Code.

        Args:
            item_path: Path to the item to process

        Returns:
            True if processing succeeded, False otherwise
        """
        self.logger.info(f'Processing item: {item_path.name}')

        # Create prompt for Qwen Code
        prompt = f'''You are processing an item from the AI Employee Needs_Action folder.

1. Read the file: {item_path}
2. Read the Company Handbook: {self.vault_path / 'Company_Handbook.md'}
3. Determine what action needs to be taken based on the content
4. Create a plan in the Plans folder if multiple steps are required
5. Execute simple actions directly or create an approval request for sensitive actions
6. Move this file to the Done folder when complete
7. Update the Dashboard.md with the activity

Follow the rules in the Company Handbook. When in doubt, create an approval request.'''

        try:
            # Run Qwen Code with the prompt
            # Using -p flag for prompt (Qwen Code CLI syntax)
            # On Windows, use shell=True to properly resolve qwen.cmd
            import platform
            use_shell = platform.system() == 'Windows'
            
            result = subprocess.run(
                f'qwen -p "{prompt}"' if use_shell else ['qwen', '-p', prompt],
                cwd=str(self.vault_path),
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                encoding='utf-8',
                errors='replace',
                shell=use_shell
            )

            if result.returncode == 0:
                self.logger.info(f'Qwen Code completed processing: {item_path.name}')
                self.items_processed += 1
                
                # For Bronze tier: Move file to Done after successful processing
                # Qwen Code output is logged but file movement is handled by orchestrator
                dest = self.done / item_path.name
                try:
                    item_path.rename(dest)
                    self.logger.info(f'Moved to Done: {dest.name}')
                    
                    # Log the processing result
                    log_entry = f'''---
timestamp: {datetime.now().isoformat()}
action: file_processed
file: {item_path.name}
result: success
---

# Processing Log Entry

- **File**: {item_path.name}
- **Processed at**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Result**: Successfully processed by Qwen Code
- **Output**: Moved to Done folder

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
