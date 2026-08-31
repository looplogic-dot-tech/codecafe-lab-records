@echo off
where tesseract >nul 2>nul
if errorlevel 1 (
  echo Tesseract OCR was not found in PATH.
  echo Text-based PDFs will still work. Scanned PDFs require a local Tesseract installation.
  exit /b 1
)
tesseract --version
tesseract --list-langs
