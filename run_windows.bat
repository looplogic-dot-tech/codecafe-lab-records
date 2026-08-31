@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe call setup_windows.bat
.venv\Scripts\python.exe -c "import flask,pypdf,fitz,webview" >nul 2>nul
if errorlevel 1 call setup_windows.bat
.venv\Scripts\python.exe desktop_window.py %*
