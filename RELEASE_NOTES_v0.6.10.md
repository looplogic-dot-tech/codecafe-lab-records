# CodeCafe Lab Records v0.6.10 — Native Print Fix

- Fixes the Doctor View **Print / Imprimir** button in Linux Desktop Window mode.
- Qt WebEngine's `printRequested` signal is now connected to a native `QPrintDialog` / CUPS workflow.
- Keeps `window.print()` and the existing print CSS, so browser mode remains unchanged.
- Printing failures are isolated from the clinical-record application and show an error instead of crashing the app.
- RPM packaging keeps the safe staging strategy, removes the optional incompatible Qt TIFF plugin only from the RPM copy, and disables global `/usr/lib/.build-id` links for the private PyInstaller payload.
- Clinical parser, OCR, Bulk import, PDF viewer, database model, and patient records are intentionally unchanged.
