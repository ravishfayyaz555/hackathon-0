import time
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Orchestrator:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.approved = self.vault_path / 'Approved'
        
    def check_folders(self) -> bool:
        """Check if there are any '.md' files in Needs_Action or Approved folders."""
        needs_action_files = list(self.needs_action.glob('*.md'))
        approved_files = list(self.approved.glob('*.md'))
        
        if needs_action_files:
            logging.info(f"Found {len(needs_action_files)} items needing action.")
        if approved_files:
            logging.info(f"Found {len(approved_files)} approved items to execute.")
            
        return len(needs_action_files) > 0 or len(approved_files) > 0

    def wake_up_ai(self):
        logging.info("Waking up AI Engine (Simulation Mode) to process items...")
        
        # Mock AI logic for testing Silver Tier without external LLM CLI
        needs_action_files = list(self.needs_action.glob('*.md'))
        
        for file in needs_action_files:
            logging.info(f"[AI SIMULATION] Thinking about: {file.name}")
            time.sleep(2) # Simulating thinking time
            
            # Create a mock plan
            plan_file = self.vault_path / 'Plans' / f"PLAN_{file.name}"
            plan_content = f"---\nstatus: pending_approval\ntarget_file: {file.name}\n---\n\n## Objective\nProcess the file '{file.name}' via AI Simulation.\n\n## Action Plan\n- [x] Read file contents\n- [x] Analyze intention\n- [ ] Awaiting Human Approval in Pending_Approval folder\n"
            plan_file.write_text(plan_content, encoding='utf-8')
            
            # Create an approval request
            approval_file = self.vault_path / 'Pending_Approval' / f"APPROVAL_{file.name}"
            approval_content = f"The AI has decided this file ({file.name}) requires your permission to proceed. Move this to /Approved to execute."
            approval_file.write_text(approval_content, encoding='utf-8')
            
            # Move the original to Done
            done_file = self.vault_path / 'Done' / file.name
            file.rename(done_file)
            
            logging.info(f"[AI SIMULATION] Finished reasoning. Created Plan and requested Approval for {file.name}.")
            
        # Process Approved Files
        approved_files = list(self.approved.glob('*.md'))
        for file in approved_files:
            logging.info(f"[AI SIMULATION] Executing approved action for: {file.name}")
            time.sleep(1)
            
            with open(self.vault_path / "Dashboard.md", "a", encoding='utf-8') as db:
                db.write(f"\n- [x] AI Simulation executed action for {file.name} successfully.")
                
            done_file = self.vault_path / 'Done' / file.name
            file.rename(done_file)
            logging.info(f"[AI SIMULATION] Action executed and logged to Dashboard.")
            
    def run(self, check_interval=10):
        logging.info("Orchestrator started. Acting as the 'Dimagh' of the AI Employee.")
        logging.info(f"Watching Obsidian Vault at: {self.vault_path}")
        
        while True:
            if self.check_folders():
                self.wake_up_ai()
            time.sleep(check_interval)

if __name__ == "__main__":
    # Point this to your actual vault directory
    VAULT_DIR = r"c:\Users\Rawish\Desktop\Hackathon_0"
    
    orchestrator = Orchestrator(VAULT_DIR)
    orchestrator.run()
