from __future__ import annotations

"""v0.6.12 application bridge.

This module layers adaptive multi-record OCR and glucose alias normalization over the
validated v0.6.11 Flask application. The stable application/database code remains in
app.py; v0.6.12 patches parser/version behavior at runtime.
"""

import app as core
from glucose_filter import format_glucose_specimen_detail, glucose_lookup_name, is_glucose_name
from lab_pdf_parser_v612 import parse_lab_pdf

APP_VERSION = "0.6.12-multi-record-adaptive-ocr"

core.APP_VERSION = APP_VERSION
core.parse_lab_pdf = parse_lab_pdf

_original_normalize_observation_payload = core.normalize_observation_payload
_original_init_db = core.init_db


def normalize_observation_payload(*args, **kwargs):
    """Map glucose wording variants to one analyte and retain source context.

    ``raw_test_name`` in observations is still written by app.py from the untouched
    laboratory label. Only the dictionary lookup receives the generic Glucosa label.
    Existing urine/specimen context continues to disambiguate glucose in urine.
    """
    raw_name = str(kwargs.get("raw_name", ""))
    panel = str(kwargs.get("panel", ""))
    specimen_hint = core.specimen_from_context(panel, raw_name)

    lookup_kwargs = dict(kwargs)
    lookup_kwargs["raw_name"] = glucose_lookup_name(raw_name, panel, specimen_hint)
    result = _original_normalize_observation_payload(*args, **lookup_kwargs)

    if result.get("canonical_key") == "glucose_blood" and is_glucose_name(raw_name):
        result["specimen_detail"] = format_glucose_specimen_detail(
            raw_name, panel, str(result.get("specimen_detail", specimen_hint))
        )
    return result


# app.py route functions resolve this global dynamically at request time.
core.normalize_observation_payload = normalize_observation_payload


def _remap_existing_glucose_rows() -> None:
    """Converge older glucose aliases without deleting original laboratory wording."""
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
            raw_name = row["raw_test_name"] or row["test_name"]
            if not is_glucose_name(raw_name):
                continue
            normalized = normalize_observation_payload(
                conn,
                raw_name=raw_name,
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
