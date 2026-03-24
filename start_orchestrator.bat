@echo off
REM Silver Tier Requirement: Basic scheduling via Task Scheduler
REM You can point Windows Task Scheduler to this .bat file to start the Orchestrator automatically

echo Starting AI Employee Orchestrator...
cd /d "%~dp0"
call venv\Scripts\activate.bat
python scripts\orchestrator.py
pause
