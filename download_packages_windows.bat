@echo off
setlocal
cd /d "%~dp0"
if not exist packages\windows mkdir packages\windows
py -3 -m pip download --disable-pip-version-check --dest packages\windows -r requirements.txt
if errorlevel 1 exit /b %errorlevel%
py -3 -m pip download --disable-pip-version-check --dest packages\windows -r requirements-build.txt
if errorlevel 1 exit /b %errorlevel%
echo.
echo Windows dependency cache updated: %CD%\packages\windows
