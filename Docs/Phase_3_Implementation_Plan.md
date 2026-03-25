# Phase 3: Gold Tier Implementation Plan

Implementing the "Ralph Wiggum" proactive loop and the specialized "Sunday Business Audit" to complete the Digital FTE foundation.

## Proposed Changes

### [Component] Orchestrator (The Brain)
Enhancing the `orchestrator.py` to be proactive rather than strictly reactive.

#### [MODIFY] [orchestrator.py](file:///c:/Users/Rawish/Desktop/Hackathon_0/scripts/orchestrator.py)
- Rename `wake_up_ai` to `process_tasks`.
- Add `ralph_wiggum_loop()` which periodically:
    - Checks for "Urgent" items.
    - Triggers the `Business Audit` if it is Sunday.
    - Logs a "System Heartbeat" to `Dashboard.md`.

### [Component] Business Intelligence (The Audit)
Creating a dedicated script for financial and goal auditing.

#### [NEW] [business_audit.py](file:///c:/Users/Rawish/Desktop/Hackathon_0/scripts/business_audit.py)
- Logic to read `Business_Goals.md` and `Dashboard.md`.
- Generate a markdown report in a new `/Reports` folder.
- Compare current MTD (Month to Date) revenue against targets.

### [Component] Storage & Reporting
Updating the Obsidian vault structure for Phase 3 documentation.

#### [NEW] [Reports/](file:///c:/Users/Rawish/Desktop/Hackathon_0/Reports/) [DIRECTORY]
- A folder to store all generated Business Audits.

#### [MODIFY] [Dashboard.md](file:///c:/Users/Rawish/Desktop/Hackathon_0/Dashboard.md)
- Add a "System Health" section for the Heartbeat logs.

## Verification Plan

### Automated Tests
1. **Orchestrator Simulation**: Run `python scripts/orchestrator.py` and verify it detects files and triggers the "Ralph Wiggum" logic.
2. **Audit Generation**: Run `python scripts/business_audit.py` manually and verify a report is created in `Reports/`.

### Manual Verification
1. **Sunday Trigger**: Change the system time (or mock the date) to verify the audit triggers automatically on Sundays.
2. **Dashboard Update**: Verify `Dashboard.md` shows the latest "Heartbeat" after the loop runs.
