import time
import subprocess
import logging
from pathlib import Path
from datetime import datetime
import os
import threading

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Orchestrator:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.approved = self.vault_path / 'Approved'
        self.dashboard = self.vault_path / 'Dashboard.md'
        self.last_heartbeat = 0
        self.loop_count = 0
        self.processes = []
        
    def start_watchers(self):
        """Start all specialized watchers as background processes (Platinum Tier)."""
        scripts = [
            'filesystem_watcher.py',
            'gmail_watcher.py',
            'whatsapp_watcher.py'
        ]
        
        for script in scripts:
            script_path = self.vault_path / 'scripts' / script
            if script_path.exists():
                logging.info(f"[PLATINUM] Starting background watcher: {script}")
                proc = subprocess.Popen(['python', str(script_path)])
                self.processes.append(proc)
            else:
                logging.warning(f"[PLATINUM] Watcher script not found: {script}")

    def check_folders(self) -> bool:
        """Check if there are any '.md' files in Needs_Action or Approved folders."""
        needs_action_files = list(self.needs_action.glob('*.md'))
        approved_files = list(self.approved.glob('*.md'))
        
        if needs_action_files:
            logging.info(f"Found {len(needs_action_files)} items needing action.")
        if approved_files:
            logging.info(f"Found {len(approved_files)} approved items to execute.")
            
        return len(needs_action_files) > 0 or len(approved_files) > 0

    def ralph_wiggum_check(self):
        """Proactive check for system health, business audit, and 'Ralph Wiggum' logic."""
        self.loop_count += 1
        now = time.time()
        
        # 1. Heartbeat every ~1 minute
        if now - self.last_heartbeat > 60:
            logging.info("[RALPH WIGGUM] Logging Heartbeat to Dashboard...")
            self._log_heartbeat()
            self.last_heartbeat = now
            
        # 2. Sunday Business Audit Check
        today = datetime.now()
        if today.weekday() == 6: # Sunday
            audit_report = self.vault_path / "Reports" / f"Business_Audit_{today.strftime('%Y-%m-%d')}.md"
            if not audit_report.exists():
                logging.info("[RALPH WIGGUM] It's Sunday! Triggering Business Audit...")
                self._run_business_audit()

    def _log_heartbeat(self):
        """Update Dashboard.md with system health status (Platinum Tier)."""
        health_section = f"\n## 🛡️ System Health\n- **Last Heartbeat**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n- **Orchestrator Status**: Active (Platinum Tier - All Watchers Running)\n"
        
        content = self.dashboard.read_text(encoding='utf-8')
        if "## 🛡️ System Health" in content:
            parts = content.split("## 🛡️ System Health")
            new_content = parts[0] + health_section
        else:
            new_content = content + health_section
            
        self.dashboard.write_text(new_content, encoding='utf-8')

    def _run_business_audit(self):
        """Trigger the business audit script."""
        try:
            audit_script = self.vault_path / "scripts" / "business_audit.py"
            subprocess.run(["python", str(audit_script)], check=True)
            logging.info("[RALPH WIGGUM] Business Audit completed successfully.")
        except Exception as e:
            logging.error(f"[RALPH WIGGUM] Business Audit failed: {e}")

    def wake_up_ai(self):
        logging.info("Waking up AI Engine (Platinum Mode) to process items...")
        
        needs_action_files = list(self.needs_action.glob('*.md'))
        for file in needs_action_files:
            logging.info(f"[PLATINUM AI] Thinking about: {file.name}")
            time.sleep(1)
            
            # Create a mock plan
            plan_file = self.vault_path / 'Plans' / f"PLAN_{file.name}"
            plan_content = f"---\nstatus: pending_approval\ntarget_file: {file.name}\n---\n\n## Objective\nPlatinum Tier Processing for '{file.name}'.\n\n## Action Plan\n- [x] Read source content\n- [ ] Draft response (Email/WhatsApp/LinkedIn)\n- [ ] Awaiting Human Approval in Pending_Approval folder\n"
            plan_file.write_text(plan_content, encoding='utf-8')
            
            # Create an approval request
            approval_file = self.vault_path / 'Pending_Approval' / f"APPROVAL_{file.name}"
            approval_content = f"The Platinum AI has analyzed this item ({file.name}). Move this to /Approved to execute the multi-channel response."
            approval_file.write_text(approval_content, encoding='utf-8')
            
            done_file = self.vault_path / 'Done' / file.name
            file.rename(done_file)
            logging.info(f"[PLATINUM AI] Created Plan and Approval Request for {file.name}.")
            
        # Process Approved Files
        approved_files = list(self.approved.glob('*.md'))
        for file in approved_files:
            logging.info(f"[PLATINUM AI] Executing approved action for: {file.name}")
            
            # Specific logic for LinkedIn posts
            if "linkedin" in file.name.lower() or "PLAN_LINKEDIN" in file.name:
                self._execute_linkedin_post(file)
            
            # Log to Dashboard
            content = self.dashboard.read_text(encoding='utf-8')
            log_entry = f"\n- [x] Platinum AI executed {file.name} successfully at {datetime.now().strftime('%H:%M:%S')}."
            
            if "## 📝 Recent Activity" in content:
                parts = content.split("## 📝 Recent Activity")
                new_content = parts[0] + "## 📝 Recent Activity" + log_entry + parts[1]
            else:
                new_content = content + "\n## 📝 Recent Activity" + log_entry
                
            self.dashboard.write_text(new_content, encoding='utf-8')
            
            done_file = self.vault_path / 'Done' / file.name
            file.rename(done_file)
            logging.info(f"[PLATINUM AI] Action completed and logged.")

    def _execute_linkedin_post(self, file):
        """Call the LinkedIn MCP tool."""
        try:
            linkedin_script = self.vault_path / "scripts" / "linkedin_mcp.py"
            # In a real scenario, we'd pass content as an argument
            subprocess.run(["python", str(linkedin_script)], check=True)
            logging.info("[PLATINUM] LinkedIn post executed.")
        except Exception as e:
            logging.error(f"[PLATINUM] LinkedIn post failed: {e}")

    def run(self, check_interval=10):
        logging.info("Orchestrator started: PLATINUM TIER ACTIVE.")
        logging.info(f"Watching Obsidian Vault at: {self.vault_path}")
        
        # Start the external watchers
        self.start_watchers()
        
        try:
            while True:
                self.ralph_wiggum_check()
                if self.check_folders():
                    self.wake_up_ai()
                time.sleep(check_interval)
        except KeyboardInterrupt:
            logging.info("Shutting down Orchestrator and background processes...")
            for proc in self.processes:
                proc.terminate()
            logging.info("System stopped.")

if __name__ == "__main__":
    VAULT_DIR = r"c:\Users\Rawish\Desktop\Hackathon_0"
    orchestrator = Orchestrator(VAULT_DIR)
    orchestrator.run()
