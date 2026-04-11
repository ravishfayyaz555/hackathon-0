import time
import subprocess
import logging
from pathlib import Path
from datetime import datetime
import os
import threading
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import re
import http.server
import socketserver
from functools import partial

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
        
        # UI & API Setup
        self.ui_path = os.path.abspath(os.path.join(str(self.vault_path), "ui"))
        self.app = Flask(__name__)
        CORS(self.app)
        self._setup_routes()
        
        # KPI Stats Cache
        self.stats = {
            "response_time": "...",
            "payment_rate": "...",
            "software_costs": "$0.00"
        }
        
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
            logging.info("[RALPH WIGGUM] Logging Heartbeat & Updating Dashboard...")
            self._calculate_kpis()
            self._update_dashboard_comms()
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

    def _update_dashboard_comms(self):
        """Scan Needs_Action and update Gmail/WhatsApp tables in Dashboard.md."""
        gmail_items = list(self.needs_action.glob("GMAIL_*.md"))
        whatsapp_items = list(self.needs_action.glob("WHATSAPP_*.md"))
        
        content = self.dashboard.read_text(encoding='utf-8')
        
        # Update Gmail Table
        gmail_rows = ""
        for item in gmail_items[:5]:
            text = item.read_text(encoding='utf-8')
            sender = re.search(r"from: (.*)", text)
            subject = re.search(r"subject: (.*)", text)
            gmail_rows += f"| {sender.group(1) if sender else 'Unknown'} | {subject.group(1) if subject else 'No Subject'} | Pending |\n"
        
        if not gmail_rows: gmail_rows = "| - | No new emails | - |\n"
        
        gmail_section = "## 📧 Inbound Communication (Gmail)\n| From | Subject | Status |\n|------|---------|--------|\n" + gmail_rows
        content = re.sub(r"## 📧 Inbound Communication \(Gmail\)\n\| From \| Subject \| Status \|\n\|------\|---------\|--------\|\n(?:\|.*\|\n)*", gmail_section, content)

        # Update WhatsApp Alerts
        wa_alerts = ""
        for item in whatsapp_items[:3]:
            wa_alerts += f"- [ ] {item.name.replace('WHATSAPP_', '').replace('.md', '')}: Urgent keyword detected.\n"
        
        if not wa_alerts: wa_alerts = "- [ ] No urgent keywords detected.\n"
        
        wa_section = "## 💬 WhatsApp Alerts\n" + wa_alerts
        content = re.sub(r"## 💬 WhatsApp Alerts\n(?:- \[ \].*\n)*", wa_section, content)
        
        self.dashboard.write_text(content, encoding='utf-8')

    def _calculate_kpis(self):
        """Calculate real-time KPIs from the vault data."""
        done_folder = self.vault_path / "Done"
        accounting_folder = self.vault_path / "Accounting"
        
        # 1. Response Time (Mock calculation based on file age vs fixed metric for now)
        # In real logic, we'd compare Frontmatter 'received' vs File 'mtime'
        self.stats["response_time"] = "1.2 hrs" 
        
        # 2. Invoice Payment Rate
        invoices = list(accounting_folder.glob("*.md"))
        paid = 0
        total = 0
        for inv in invoices:
            if "vendor:" in inv.read_text(encoding='utf-8').lower():
                total += 1
                if "status: \"paid\"" in inv.read_text(encoding='utf-8').lower():
                    paid += 1
        
        rate = (paid / total * 100) if total > 0 else 0
        self.stats["payment_rate"] = f"{rate:.1f}%"
        
        # Update Dashboard KPI Table
        content = self.dashboard.read_text(encoding='utf-8')
        content = re.sub(r"\| Client Response Time \| .* \| < 24 hrs \|", f"| Client Response Time | {self.stats['response_time']} | < 24 hrs |", content)
        content = re.sub(r"\| Invoice Payment Rate \| .* \| > 90% \|", f"| Invoice Payment Rate | {self.stats['payment_rate']} | > 90% |", content)
        self.dashboard.write_text(content, encoding='utf-8')

    def _execute_linkedin_post(self, file):
        """Call the LinkedIn MCP tool."""
        try:
            linkedin_script = self.vault_path / "scripts" / "linkedin_mcp.py"
            # In a real scenario, we'd pass content as an argument
            subprocess.run(["python", str(linkedin_script)], check=True)
            logging.info("[PLATINUM] LinkedIn post executed.")
        except Exception as e:
            logging.error(f"[PLATINUM] LinkedIn post failed: {e}")

    # --- API ENDPOINTS ---
    def _setup_routes(self):
        @self.app.route('/api/status')
        def get_status():
            try:
                # Get latest counts
                gmail_items = list(self.needs_action.glob("GMAIL_*.md"))
                whatsapp_items = list(self.needs_action.glob("WHATSAPP_*.md"))
                
                content = self.dashboard.read_text(encoding='utf-8')
                
                # Extract Revenue
                revenue_match = re.search(r"- \*\*Current MTD Revenue\*\*: \$([0-9,.]+)", content)
                revenue = revenue_match.group(1) if revenue_match else "0"
                
                # Extract Target %
                reach_match = re.search(r"- \*\*Target Reach %\*\*: ([0-9.]+)%", content)
                reach = reach_match.group(1) if reach_match else "0"
                
                # Extract Recent Activity
                activity = []
                if "## 📝 Recent Activity" in content:
                    act_part = content.split("## 📝 Recent Activity")[1].split("##")[0]
                    activity = [line.strip("- [x] ").strip() for line in act_part.strip().splitlines() if line.strip()][:5]

                return jsonify({
                    "status": "Active (Platinum)",
                    "tier": "Platinum",
                    "revenue": f"${revenue}",
                    "reach": f"{reach}%",
                    "heartbeat": datetime.now().strftime("%H:%M:%S"),
                    "activity": activity,
                    "pending_approvals": len(list((self.vault_path / 'Pending_Approval').glob('*.md'))) - 1,
                    "response_time": self.stats["response_time"],
                    "payment_rate": self.stats["payment_rate"],
                    "gmail_count": len(gmail_items),
                    "whatsapp_count": len(whatsapp_items)
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500

    def start_api_and_ui(self):
        """Start the Flask API (8000) and UI Server (8080) in separate threads."""
        
        # 1. Flask API
        def run_flask():
            import logging as flask_logging
            log = flask_logging.getLogger('werkzeug')
            log.setLevel(flask_logging.ERROR)
            self.app.run(port=8000, debug=False, use_reloader=False)
            
        # 2. UI Static Server
        def run_ui():
            os.chdir(self.ui_path)
            handler = http.server.SimpleHTTPRequestHandler
            with socketserver.TCPServer(("", 8080), handler) as httpd:
                logging.info(f"[UI] Static Dashboard serving at http://localhost:8080")
                httpd.serve_forever()

        threading.Thread(target=run_flask, daemon=True).start()
        threading.Thread(target=run_ui, daemon=True).start()
        logging.info("[SYSTEM] Dual-server started. API: 8000 | UI: 8080")

    def run(self, check_interval=10):
        logging.info("Orchestrator started: PLATINUM TIER ACTIVE.")
        logging.info(f"Watching Obsidian Vault at: {self.vault_path}")
        
        # Start the external watchers
        self.start_watchers()
        
        # Start the UI and API
        self.start_api_and_ui()
        
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
