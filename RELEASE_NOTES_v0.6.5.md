# CodeCafe Lab Records v0.6.5 — Structured microbiology / culture results

- Adds structured extraction for qualitative microbiology and culture reports that do not use numeric reference ranges.
- Supports two-column and vertically split forms such as `CULTIVO — Sin desarrollo microbiano`.
- Supports common qualitative culture phrases without inventing data.
- Adds labeled microorganism/isolate and colony-count extraction (UFC/mL / CFU/mL) when explicitly present in the source report.
- Adds canonical urine-culture dictionary mapping when the panel/specimen context indicates urine.
- Adds MedlinePlus Bacteria Culture Test as the authoritative reference for canonical urine-culture results.
- Preserves the original PDF and original text/value exactly as extracted.
- Keeps v0.6.4 self-contained macOS OCR and cross-platform fallbacks.
- Regression baseline remains 1 / 90 / 89 / 95 / 20 / 19 / 24 observations on the seven existing validation reports.
