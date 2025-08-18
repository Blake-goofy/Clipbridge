@echo off
REM Clipbridge Service Startup Script
cd /d "C:\Users\blake\source\repos\Clipbridge"
call "venv\Scripts\activate.bat"
python clipbridge.py --service
