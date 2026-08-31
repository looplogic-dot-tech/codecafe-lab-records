@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe call setup_windows.bat
.venv\Scripts\python.exe desktop_window.py --browser --port 5000 %*
