@echo off
setlocal
cd /d "%~dp0"
set "PY=python"
if exist .venv\Scripts\python.exe set "PY=.venv\Scripts\python.exe"
"%PY%" -m py_compile app.py desktop_window.py lab_pdf_parser.py clinical_dictionary.py tests\test_smoke.py tests\test_parser_unit.py tests\test_dictionary_unit.py tests\test_desktop_window.py
if errorlevel 1 exit /b %errorlevel%
where node >nul 2>nul
if not errorlevel 1 node --check static\app.js
if errorlevel 1 exit /b %errorlevel%
findstr /C:"Jaime Sánchez Sáenz" app.py >nul || (echo Permanent authorship attribution missing. & exit /b 65)
findstr /C:"contacto@codecafe.io" app.py >nul || (echo Project contact attribution missing. & exit /b 65)
if exist data\lab_records.db (echo Database file must not be distributed in source. & exit /b 65)
echo Source validation: OK
