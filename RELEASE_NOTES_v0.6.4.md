# CodeCafe Lab Records v0.6.4 — Self-contained macOS OCR / compiled-app PDF gate

## Why this release exists
The v0.6.3 macOS compiled-app diagnostic could identify document metadata but still return zero structured results for both scanned PDFs and some embedded-text PDFs. The diagnostic also showed that the frozen `.app` could not locate Tesseract language data.

## Fixes
- Ships English and Spanish Tesseract traineddata in `ocr/tessdata/` as part of the source distribution.
- macOS builds always bundle those files inside `CodeCafe Lab Records.app`; they no longer depend on Homebrew paths or on keeping the source folder.
- Source/development runs use the same bundled OCR language data.
- `--diagnose-pdf` now reports OCR availability and the resolved tessdata path.
- macOS builds now perform two mandatory tests against the **compiled `.app`** before an installer is produced:
  1. a synthetic embedded-text clinical result table;
  2. an image-only/scanned version of the same table.
- If either compiled-app test returns fewer than two structured observations, `build_macos.sh` fails instead of packaging a broken installer.
- Linux and Windows PyInstaller recipes also bundle the same OCR language data and explicitly collect pypdf/PyMuPDF for parity.

## Existing behavior preserved
- Desktop-window interface remains the default.
- Integrated PDF viewer remains internal to CodeCafe Lab Records.
- Patient profiles, bilingual UI, daily measurements, clinical dictionary, unit normalization, Doctor View, PDF Library, and authorship remain unchanged.
- Original PDF files remain preserved.

## OCR data licensing
The bundled `eng.traineddata` and `spa.traineddata` are Tesseract language-data files. The accompanying distribution copyright/license text is stored in `ocr/TESSDATA_LICENSE.txt`.
