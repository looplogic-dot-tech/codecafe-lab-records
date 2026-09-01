from __future__ import annotations

"""v0.6.12 application bridge.

This module layers adaptive multi-record OCR and canonical glucose filtering over the
validated v0.6.11 Flask application. The stable application/database code stays in
app.py; v0.6.12 patches parser/version behavior and safely enriches glucose metadata.
"""

import app as core
from clinical_dictionary import glucose_context, key_text
from lab_pdf_parser_v612 import parse_lab_pdf

APP_VERSION = "0.6.12-multi-record-adaptive-ocr"

# Route functions in app.py resolve these globals at request time, so replacing them
# here upgrades analysis/import flows without forking the stable application module.
core.APP_VERSION = APP_VERSION
core.parse_lab_pdf = parse_lab_pdf

_original_normalize_observation_payload = core.normalize_observation_payload
_original_init_db = core.init_db


def _glucose_specimen_detail(raw_name: str, panel: str, default: str) -> str:
    meta = glucose_context(raw_name, panel)
    parts: list[str] = []
    specimen = str(meta.get("specimen_detail") or default or "").strip()
    context = str(meta.get("collection_context") or "").strip()
    timepoint = meta.get("timepoint_minutes")
    if specimen:
        parts.append(specimen)
    if context:
        parts.append(context)
    if timepoint is not None and not context.startswith(f"{timepoint} min"):
        parts.append(f"t={int(timepoint)} min")
    return " · ".join(parts) or default


def normalize_observation_payload(*args, **kwargs):
    """Normalize glucose aliases while preserving matrix/collection context.

    The canonical test remains a single glucose analyte for longitudinal charts.
    The laboratory's original label remains untouched in raw_test_name, and explicit
    serum/plasma/blood/capillary + basal/fasting/timepoint information is retained in
    specimen_detail so no clinically useful context is discarded.
    """
    result = _original_normalize_observation_payload(*args, **kwargs)
    raw_name = str(kwargs.get("raw_name", ""))
    panel = str(kwargs.get("panel", ""))
    if result.get("canonical_key") == "glucose_blood":
        result["specimen_detail"] = _glucose_specimen_detail(
            raw_name, panel, str(result.get("specimen_detail", ""))
        )
    return result


# All core routes resolve this function name from app.py globals at request time.
core.normalize_observation_payload = normalize_observation_payload


def _remap_existing_glucose_rows() -> None:
    """Converge glucose aliases imported by older builds onto glucose_blood/urine."""
    with core.db() as conn:
        rows = conn.execute(
            """
            SELECT * FROM observations
            WHERE lower(raw_test_name) LIKE '%gluc%'
               OR lower(raw_test_name) LIKE '%glyc%'
               OR lower(test_name) LIKE '%gluc%'
            """
        ).fetchall()
        for row in rows:
            normalized = normalize_observation_payload(
                conn,
                raw_name=row["raw_test_name"] or row["test_name"],
                panel=row["panel"],
                lab=row["lab"],
                raw_unit=row["unit"],
                value_numeric=row["value_numeric"],
                reference_low=row["reference_low"],
                reference_high=row["reference_high"],
            )
            if normalized.get("canonical_key") not in {"glucose_blood", "glucose_urine"}:
                continue
            assignments = ",".join(f"{name}=?" for name in normalized)
            conn.execute(
                f"UPDATE observations SET {assignments}, test_name=? WHERE id=?",
                (*normalized.values(), normalized["canonical_name_es"], row["id"]),
            )


def init_db() -> None:
    _original_init_db()
    _remap_existing_glucose_rows()


# Browser/developer execution through app.main() also uses the patched init function.
core.init_db = init_db

app = core.app
main_with_args = core.main_with_args
current_state = core.current_state


def main() -> None:
    core.main()


def __getattr__(name: str):
    return getattr(core, name)


if __name__ == "__main__":
    main()
