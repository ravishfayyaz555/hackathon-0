import time
import logging
from pathlib import Path
from datetime import datetime
import os

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
except ImportError:
    logging.error("Google API libraries not found. Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")

from base_watcher import BaseWatcher

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailWatcher(BaseWatcher):
    def __init__(self, vault_path: str, credentials_path: str):
        super().__init__(vault_path, check_interval=60)
        self.credentials_path = credentials_path
        self.token_path = Path(vault_path) / 'token.json'
        
        self.service = None
        try:
            self.service = self._authenticate()
        except Exception as e:
            self.logger.error(f"Could not authenticate with Google API: {e}")
            
        self.processed_ids = set()
        
    def _authenticate(self):
        creds = None
        
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)
            
        if not creds or not creds.valid:
            if not os.path.exists(self.credentials_path):
                self.logger.error(f"Oauth Credentials not found at {self.credentials_path}. Please download from Google Cloud Console.")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
            # This requires opening a browser windows for login
            creds = flow.run_local_server(port=0)
            
            with open(str(self.token_path), 'w') as token:
                token.write(creds.to_json())
                
        return build('gmail', 'v1', credentials=creds)

    def check_for_updates(self) -> list:
        if not self.service:
            # Service not authenticated, return empty list
            return []
            
        try:
            # Search for unread emails 
            results = self.service.users().messages().list(
                userId='me', q='is:unread'
            ).execute()
            messages = results.get('messages', [])
            return [m for m in messages if m['id'] not in self.processed_ids]
        except Exception as e:
            self.logger.error(f"Error fetching emails: {e}")
            return []
    
    def create_action_file(self, message) -> Path:
        msg = self.service.users().messages().get(
            userId='me', id=message['id']
        ).execute()
        
        headers = {h['name']: h['value'] for h in msg['payload']['headers']}
        
        content = f'''---
type: email
from: {headers.get('From', 'Unknown')}
subject: {headers.get('Subject', 'No Subject')}
received: {datetime.now().isoformat()}
priority: normal
status: pending_review
---

## Email Content Overview
{msg.get('snippet', '')}

## Suggested Actions
- [ ] Read email
- [ ] Determine if reply is needed
- [ ] Wait for Human Approval (move to /Pending_Approval) if writing a reply
'''
        filepath = self.needs_action / f'GMAIL_{message["id"]}.md'
        filepath.write_text(content, encoding='utf-8')
        self.processed_ids.add(message['id'])
        self.logger.info(f"Created action item for email from: {headers.get('From', 'Unknown')}")
        return filepath

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    VAULT_DIR = r"c:\Users\Rawish\Desktop\Hackathon_0"
    CREDS_PATH = r"c:\Users\Rawish\Desktop\Hackathon_0\credentials.json"
    
    watcher = GmailWatcher(VAULT_DIR, CREDS_PATH)
    if watcher.service:
        logging.info("Gmail Watcher started. Listening for unread emails...")
        watcher.run()
    else:
        logging.info("Please set up Google Cloud OAuth credentials and save to 'credentials.json' to start Gmail monitoring.")
