@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

echo [1/6] Checking Windows environment
where py >nul 2>nul || (echo Python 3 is required. & exit /b 69)

echo [2/6] Preparing Python environment
call setup_windows.bat || exit /b %errorlevel%
call validate_source_windows.bat || exit /b %errorlevel%

echo [3/6] Installing build dependencies
set "PY=.venv\Scripts\python.exe"
set "HAS_CACHE=0"
for %%F in (packages\windows\*.whl packages\windows\*.tar.gz packages\windows\*.zip) do if exist "%%F" set "HAS_CACHE=1"
if "%HAS_CACHE%"=="1" (
  "%PY%" -m pip install --disable-pip-version-check --no-index --find-links packages\windows -r requirements-build.txt
) else (
  "%PY%" -m pip install --disable-pip-version-check -r requirements-build.txt
)
if errorlevel 1 exit /b %errorlevel%

echo [4/6] Building standalone desktop application
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist codecafe-lab-records.spec del /q codecafe-lab-records.spec
"%PY%" -m PyInstaller --noconfirm --clean --windowed --onedir --name codecafe-lab-records --collect-all webview --collect-all pypdf --collect-all pymupdf --add-data "templates;templates" --add-data "static;static" --add-data "ocr\tessdata\eng.traineddata;tessdata" --add-data "ocr\tessdata\spa.traineddata;tessdata" desktop_window.py
if errorlevel 1 exit /b %errorlevel%
if not exist "dist\codecafe-lab-records\codecafe-lab-records.exe" (echo Expected executable was not created. & exit /b 70)

echo [5/6] Creating end-user installer folder
set "PKG=dist\CodeCafe_Lab_Records_Windows_Installer"
if exist "%PKG%" rmdir /s /q "%PKG%"
mkdir "%PKG%\payload"
xcopy /E /I /Y "dist\codecafe-lab-records\*" "%PKG%\payload\" >nul
copy /Y AUTHORSHIP.md "%PKG%\AUTHORSHIP.txt" >nul

> "%PKG%\Install Registros Clinicos.cmd" echo @echo off
>>"%PKG%\Install Registros Clinicos.cmd" echo setlocal
>>"%PKG%\Install Registros Clinicos.cmd" echo net session ^>nul 2^>nul ^|^| ^(powershell -NoProfile -Command "Start-Process -Verb RunAs -FilePath '%%~f0'" ^& exit /b^)
>>"%PKG%\Install Registros Clinicos.cmd" echo set "DEST=%%ProgramFiles%%\Registros Clinicos"
>>"%PKG%\Install Registros Clinicos.cmd" echo if exist "%%DEST%%" rmdir /s /q "%%DEST%%"
>>"%PKG%\Install Registros Clinicos.cmd" echo mkdir "%%DEST%%"
>>"%PKG%\Install Registros Clinicos.cmd" echo xcopy /E /I /Y "%%~dp0payload\*" "%%DEST%%\" ^>nul
>>"%PKG%\Install Registros Clinicos.cmd" echo powershell -NoProfile -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut($env:ProgramData+'\\Microsoft\\Windows\\Start Menu\\Programs\\Registros Clinicos.lnk');$s.TargetPath=$env:ProgramFiles+'\\Registros Clinicos\\codecafe-lab-records.exe';$s.Save()"
>>"%PKG%\Install Registros Clinicos.cmd" echo echo.
>>"%PKG%\Install Registros Clinicos.cmd" echo echo Registros Clinicos by CodeCafe is installed. The installer folder may now be deleted.
>>"%PKG%\Install Registros Clinicos.cmd" echo start "" "%%DEST%%\codecafe-lab-records.exe"

> "%PKG%\Uninstall Registros Clinicos.cmd" echo @echo off
>>"%PKG%\Uninstall Registros Clinicos.cmd" echo net session ^>nul 2^>nul ^|^| ^(powershell -NoProfile -Command "Start-Process -Verb RunAs -FilePath '%%~f0'" ^& exit /b^)
>>"%PKG%\Uninstall Registros Clinicos.cmd" echo rmdir /s /q "%%ProgramFiles%%\Registros Clinicos"
>>"%PKG%\Uninstall Registros Clinicos.cmd" echo del /q "%%ProgramData%%\Microsoft\Windows\Start Menu\Programs\Registros Clinicos.lnk" 2^>nul
>>"%PKG%\Uninstall Registros Clinicos.cmd" echo echo Application removed. Personal medical data was left untouched.

echo [6/6] Done
powershell -NoProfile -Command "Compress-Archive -Force -Path 'dist\CodeCafe_Lab_Records_Windows_Installer' -DestinationPath 'dist\CodeCafe_Lab_Records_Windows_Installer.zip'"
echo Installer: %CD%\dist\CodeCafe_Lab_Records_Windows_Installer.zip
