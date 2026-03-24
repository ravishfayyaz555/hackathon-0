import time
import logging
from pathlib import Path
import os
import json

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    logging.warning("Playwright not installed! Run: pip install playwright && playwright install")

from base_watcher import BaseWatcher

class WhatsAppWatcher(BaseWatcher):
    def __init__(self, vault_path: str, session_path: str):
        super().__init__(vault_path, check_interval=30)
        self.session_path = Path(session_path)
        self.keywords = ['urgent', 'asap', 'invoice', 'payment', 'help']
        
    def check_for_updates(self) -> list:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path), headless=True
                )
                page = browser.pages[0]
                page.goto('https://web.whatsapp.com')
                # Wait for the chat list to appear (means login was successful)
                page.wait_for_selector('[data-testid="chat-list"]', timeout=15000)
                
                # Find unread messages
                unread = page.query_selector_all('[aria-label*="unread"]')
                messages = []
                for chat in unread:
                    text = chat.inner_text().lower()
                    # Filter only the messages that contain our keywords
                    if any(kw in text for kw in self.keywords):
                        messages.append({'text': text, 'chat_id': str(hash(text))})
                browser.close()
                return messages
        except Exception as e:
            self.logger.error(f"WhatsApp Web monitoring error (Usually requires manual login first time): {e}")
            return []

    def create_action_file(self, message) -> Path:
        content = f'''---
type: whatsapp
received: {time.strftime('%Y-%m-%dT%H:%M:%S')}
status: pending_review
---

## WhatsApp Message Content
{message['text']}

## Suggested Actions
- [ ] Read message
- [ ] Prepare reply and put in /Pending_Approval
- [ ] Reply directly if authorized
'''
        filepath = self.needs_action / f"WHATSAPP_{message['chat_id']}.md"
        filepath.write_text(content, encoding='utf-8')
        self.logger.info("Created action item for WhatsApp message")
        return filepath

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    VAULT_DIR = r"c:\Users\Rawish\Desktop\Hackathon_0"
    SESSION_PATH = r"c:\Users\Rawish\Desktop\Hackathon_0\whatsapp_session"
    
    watcher = WhatsAppWatcher(VAULT_DIR, SESSION_PATH)
    logging.info("Starting WhatsApp Watcher (Playwright). First run requires headless=False to scan QR.")
    # In production, run watcher.run()
