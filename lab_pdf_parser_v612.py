from __future__ import annotations

from typing import Any

import lab_pdf_parser as legacy
from multi_record_ocr import parse_multi_record_pdf, should_use_multi_record


def parse_lab_pdf(pdf_bytes: bytes) -> dict[str, Any]:
    """v0.6.12 parser entrypoint.

    The validated v0.6.11 parser remains authoritative for ordinary single-report
    PDFs. Only PDFs that are clearly large/multi-period are routed through the
    adaptive multi-record layer, which then reuses the legacy parser for each
    logical laboratory record.
    """
    if not should_use_multi_record(pdf_bytes):
        return legacy.parse_lab_pdf(pdf_bytes)
    try:
        return parse_multi_record_pdf(pdf_bytes, legacy.parse_lab_pdf)
    except Exception as exc:
        result = legacy.parse_lab_pdf(pdf_bytes)
        result.setdefault("warnings", []).append(
            f"Adaptive multi-record OCR failed; stable parser fallback was used: {type(exc).__name__}: {exc}"
        )
        return result


ocr_status = legacy.ocr_status
