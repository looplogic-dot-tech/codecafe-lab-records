# CodeCafe Lab Records v0.6.1 — Integrated PDF Viewer

## Main fix

- Original PDFs now open inside the CodeCafe desktop window instead of being delegated to the system browser.
- Pages are rendered on demand by PyMuPDF and displayed in a scrollable in-app viewer.
- The exact original PDF remains preserved unchanged.
- `Open PDF externally` is available only in Advanced Mode.
- The viewer remains linked to document metadata, confirmation, deletion controls, and Doctor View.

## Architecture

The browser PDF plug-in is no longer required for the normal desktop workflow. The backend exposes an internal page-render endpoint (`/pdf-page/<document>/<page>`) while `/pdf/<document>` continues to serve the original source document.
