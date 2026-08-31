# CodeCafe Registros Clínicos v0.6.12

## Multi-Record Adaptive OCR

v0.6.12 extends the stable v0.6.11 application so that one physical PDF may contain many logical clinical records from different dates and study types.

### Added in this development snapshot

- Low-cost first-pass classification by page.
- Recognition of multiple dates within one source PDF.
- Conservative date inheritance for continuation pages.
- Logical record segmentation while preserving original source-page provenance.
- Explicit diagnostic-page classification, including ECG and abdominal ultrasound.
- Selective high-resolution OCR only for laboratory pages that need structured extraction.
- Disposable OCR helper processes with per-batch timeout to recycle Tesseract/Leptonica state on large scans.
- `ocr_profiles.json` for future laboratory/layout-specific OCR tuning.
- Exact duplicate-page marking scoped by date, laboratory and study.
- Existing multi-laboratory parsing remains authoritative for SimiLab, Chopo, IMSS, DNA Diagnóstica and future profiles.

### Data-safety rule

Real clinical PDFs, patient databases, exports and backups are not repository fixtures and must not be committed. Automated tests use synthetic text only.

### Status

This commit is the v0.6.12 development snapshot. It is not a claim that all platform/package regression testing is complete. The last stable baseline is preserved in the `stable-v0.6.11` branch.
