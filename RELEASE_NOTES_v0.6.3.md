# CodeCafe Lab Records v0.6.3 — Cross-platform parser parity fix

## Fixed
- macOS compiled builds no longer stop at metadata when `pypdf` exposes text but loses the result-table layout.
- The parser now retries PyMuPDF positional extraction when the primary embedded-text engine yields no / fewer usable structured rows.
- If both embedded-text layouts fail to recover rows, local OCR is attempted as a final structural fallback.
- Result-table headers may be split across adjacent PDF text lines.
- Both `value → reference → unit` and `value → unit → reference` table orders are supported.
- Non-result headings and reference narratives are rejected more aggressively to avoid false observations.

## Cross-platform consistency
`requirements.txt` pins the same pypdf, PyMuPDF, Flask, and pywebview versions across supported platforms.

## Regression validation
The seven retained parser test documents produced the same validated counts as the previous Linux baseline: 1, 90, 89, 95, 20, 19, and 24 structured observations. No medical test documents are included in the source distribution.
