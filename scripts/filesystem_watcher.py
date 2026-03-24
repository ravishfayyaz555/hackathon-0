import time
import shutil
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DropFolderHandler(FileSystemEventHandler):
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.needs_action.mkdir(exist_ok=True)
        
    def on_created(self, event):
        if event.is_directory:
            return
        source = Path(event.src_path)
        
        # Ignore our own markdown files to avoid loops, and temp/hidden files
        if source.suffix == '.md' or source.name.startswith('.'):
            return
            
        logging.info(f"New file dropped in Inbox: {source.name}")
        
        # Wait a tiny bit to make sure file is fully written before copying
        time.sleep(1)
        
        dest = self.needs_action / f'FILE_{source.name}'
        try:
            shutil.copy2(source, dest)
            self.create_metadata(source, dest)
            logging.info(f"Successfully moved {source.name} to Needs_Action for AI to process.")
            
            # Delete the original file from Inbox after moving
            source.unlink()
        except Exception as e:
            logging.error(f"Error processing {source.name}: {e}")
        
    def create_metadata(self, source: Path, dest: Path):
        meta_path = dest.with_suffix('.md')
        meta_content = f"""---
type: file_drop
original_name: {source.name}
size: {source.stat().st_size} bytes
status: pending_review
---

# New File Received
**Filename:** {source.name}

This file was detected in the Inbox. AI Employee, please review this file and decide the next steps.

## Claude Next Actions
1. If the file is a document/receipt, read it and create a summary in `/Accounting` or `/Done`.
2. Move this markdown file to `/Done` when you have processed it.
"""
        meta_path.write_text(meta_content, encoding='utf-8')

def start_watcher(vault_path: str, drop_path: str):
    observer = Observer()
    handler = DropFolderHandler(vault_path)
    observer.schedule(handler, path=drop_path, recursive=False)
    observer.start()
    logging.info(f"FileSystem Watcher is running. Monitoring: {drop_path}")
    logging.info("Waiting for files to be dropped into the Inbox folder...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logging.info("Watcher stopped.")
    observer.join()

if __name__ == "__main__":
    # Point these paths to the absolute paths of the vault and inbox
    VAULT_DIR = r"c:\Users\Rawish\Desktop\Hackathon_0"
    INBOX_DIR = r"c:\Users\Rawish\Desktop\Hackathon_0\Inbox"
    
    start_watcher(VAULT_DIR, INBOX_DIR)
