# CodeCafe Lab Records v0.6.8

## RPM / Linux ABI packaging fix

- Removes the optional Qt TIFF image-format plugin (`libqtiff.so`) from the frozen Linux payload.
- Prevents an obsolete `libtiff.so.5` requirement from leaking into CentOS Stream 10 RPM packages.
- Adds RPM dependency validation before a package is considered distributable.
- No clinical parser, database, OCR, PDF-library, Bulk, or UI behavior is intentionally changed from v0.6.7.
