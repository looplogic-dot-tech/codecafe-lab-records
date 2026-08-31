# v0.6.12 — Multi-Record Adaptive OCR

Development branch: `develop-v0.6.12-multi-record-ocr`

`main` remains the stable v0.6.11 baseline until v0.6.12 passes regression testing.

## Goals

- Detect and segment multiple clinical episodes/dates contained in one source PDF.
- Preserve the original PDF as a single Library document while linking logical records to page ranges.
- Keep the existing multi-laboratory parser behavior intact.
- Add configurable OCR profiles through `ocr_profiles.json` for future laboratory/layout tuning.
- Use a fast classification pass followed by selective higher-resolution OCR only where needed.
- Add conservative date inheritance/correction for continuation pages.
- Recognize diagnostic pages such as ECG and ultrasound without treating them as laboratory-result tables.
- Deduplicate repeated pages/results without collapsing legitimate repeated analytes from different panels or dates.
- Preserve per-observation source page, record date, laboratory, study, units, and reference range.
- Support scanned PDFs and PDFs containing embedded text.

## Validation before merge to main

- Regression tests against previously supported SimiLab, Chopo, IMSS and DNA Diagnóstica layouts.
- Multi-date PDF regression using anonymized or synthetic fixtures only.
- Linux desktop validation.
- macOS desktop/OCR validation.
- Packaging validation for DEB and RPM, including prevention of packaged `/usr/lib/.build-id` conflicts.
- Confirm that no real clinical PDFs, SQLite databases, patient exports, local backups, credentials, or build artifacts are committed.

## Repository data-safety rule

Real clinical records are test inputs only and must never be committed. Tests added to the repository must use synthetic or fully anonymized fixtures.
