@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (echo Run setup_windows.bat first. & exit /b 69)
.venv\Scripts\python.exe -m unittest discover -s tests -v
