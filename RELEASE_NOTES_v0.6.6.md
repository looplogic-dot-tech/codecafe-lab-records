# CodeCafe Lab Records v0.6.6 — Uroculture + Bulk Import

## Fixed
- Uroculture qualitative results that were visually present but serialized as multiple PDF text lines are now reconstructed.
- Microbiology recovery runs across pypdf layout, plain text, PyMuPDF positional/plain text, and OCR representations and merges only source-supported observations.
- Partial prefix duplicates from different engines are replaced by the more specific value.

## Added
- Native desktop folder chooser for Bulk PDF import.
- Optional subfolder scan.
- Pre-import review table with date, laboratory, study, extracted-result count, warnings, duplicate status, and patient compatibility.
- Multi-PDF selection fallback for browser/developer mode.
- Shared persistence helper so single and bulk imports use the same duplicate detection, normalization, PDF preservation, and SQLite writes.
- macOS compiled-app self-test for an uroculture PDF.

## Safety behavior
- Nothing from a selected folder is saved until the user reviews the list and chooses documents.
- Known duplicate PDFs are disabled by default.
- PDFs whose detected patient does not match the active profile are not preselected.
- Original PDFs remain preserved and linked to structured results.
