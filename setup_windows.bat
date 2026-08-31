@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul || (echo Python 3 is required. & exit /b 69)
if exist .venv\Scripts\python.exe goto :venvcheck
if exist .venv rmdir /s /q .venv
py -3 -m venv .venv
goto :venvready
:venvcheck
.venv\Scripts\python.exe -c "import sys; raise SystemExit(0 if sys.platform=='win32' else 1)" >nul 2>nul
if errorlevel 1 (rmdir /s /q .venv & py -3 -m venv .venv)
:venvready
set "PY=.venv\Scripts\python.exe"
for %%F in (packages\windows\*.whl packages\windows\*.tar.gz packages\windows\*.zip) do (
  if exist "%%F" goto :offline
)
goto :online
:offline
"%PY%" -m pip install --disable-pip-version-check --no-index --find-links packages\windows -r requirements.txt
if errorlevel 1 exit /b %errorlevel%
goto :done
:online
"%PY%" -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 exit /b %errorlevel%
:done
echo.
where tesseract >nul 2>nul
if errorlevel 1 echo WARNING: Tesseract OCR was not found. Text PDFs work; scanned PDFs require Tesseract.
"%PY%" -c "import flask,pypdf,fitz,webview; print('Desktop dependencies: OK')"
echo Setup complete. Start with run_windows.bat
