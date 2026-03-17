#!/usr/bin/env python3
"""
Base Watcher - Abstract base class for all watcher scripts.

Watchers are lightweight Python scripts that run continuously in the background,
monitoring various inputs (Gmail, WhatsApp, filesystems) and creating actionable
files for Claude Code to process.
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime


class BaseWatcher(ABC):
    """
    Abstract base class for all watcher implementations.
    
    All watchers follow the same pattern:
    1. Continuously monitor a data source
    2. Detect new/updated items
    3. Create .md action files in the Needs_Action folder
    """
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root directory
            check_interval: How often to check for updates (in seconds)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.inbox = self.vault_path / 'Inbox'
        self.logs = self.vault_path / 'Logs'
        self.check_interval = check_interval
        
        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.inbox.mkdir(parents=True, exist_ok=True)
        self.logs.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Track processed items to avoid duplicates
        self.processed_ids: set = set()
        
    def _setup_logging(self):
        """Configure logging to file and console."""
        log_file = self.logs / f'{datetime.now().strftime("%Y-%m-%d")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(self.__class__.__name__)
        
    @abstractmethod
    def check_for_updates(self) -> list:
        """
        Check the data source for new or updated items.
        
        Returns:
            List of items that need processing
        """
        pass
    
    @abstractmethod
    def create_action_file(self, item) -> Path:
        """
        Create a markdown action file in the Needs_Action folder.
        
        Args:
            item: The item to create an action file for
            
        Returns:
            Path to the created action file
        """
        pass
    
    def run(self):
        """
        Main run loop. Continuously checks for updates and creates action files.
        
        This method runs indefinitely until interrupted (Ctrl+C).
        """
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        
        try:
            while True:
                try:
                    items = self.check_for_updates()
                    for item in items:
                        try:
                            action_file = self.create_action_file(item)
                            self.logger.info(f'Created action file: {action_file.name}')
                        except Exception as e:
                            self.logger.error(f'Error creating action file: {e}')
                except Exception as e:
                    self.logger.error(f'Error in check loop: {e}')
                
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            self.logger.info(f'{self.__class__.__name__} stopped by user')
        except Exception as e:
            self.logger.error(f'Fatal error: {e}')
            raise
        finally:
            self.logger.info(f'{self.__class__.__name__} shutting down')


def load_processed_ids(vault_path: str, watcher_name: str) -> set:
    """
    Load previously processed IDs from a cache file.
    
    Args:
        vault_path: Path to the vault
        watcher_name: Name of the watcher (for cache file naming)
        
    Returns:
        Set of processed IDs
    """
    cache_file = Path(vault_path) / '.cache' / f'{watcher_name}_processed.txt'
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    
    if cache_file.exists():
        with open(cache_file, 'r') as f:
            return set(line.strip() for line in f if line.strip())
    return set()


def save_processed_ids(vault_path: str, watcher_name: str, processed_ids: set, max_ids: int = 1000):
    """
    Save processed IDs to a cache file.
    
    Args:
        vault_path: Path to the vault
        watcher_name: Name of the watcher
        processed_ids: Set of processed IDs to save
        max_ids: Maximum number of IDs to keep (for memory management)
    """
    cache_file = Path(vault_path) / '.cache' / f'{watcher_name}_processed.txt'
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Keep only the most recent IDs to prevent unbounded growth
    ids_to_save = list(processed_ids)[-max_ids:]
    
    with open(cache_file, 'w') as f:
        f.write('\n'.join(ids_to_save))
