# CodeCafe Lab Records v0.6.2 — macOS PDF extraction fix

- Fixes PDF extraction in frozen macOS `.app` builds.
- Embedded-text PDFs now have two independent extraction engines: pypdf first, PyMuPDF native fallback.
- OCR no longer depends on Finder inheriting Homebrew's executable PATH.
- PyMuPDF receives an explicit tessdata directory.
- macOS builds bundle `eng.traineddata` and `spa.traineddata` when available at build time, allowing OCR after installation even if the source/build folder is deleted.
- macOS PyInstaller build explicitly collects pypdf and PyMuPDF resources.
- Linux behavior and existing parser rules remain unchanged when pypdf extraction is healthy.
