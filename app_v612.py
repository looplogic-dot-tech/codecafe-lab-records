from __future__ import annotations

"""v0.6.12 application bridge.

This module layers adaptive multi-record OCR, glucose alias normalization and
review-time OCR correction over the validated v0.6.11 Flask application.
The stable application/database code remains in app.py; v0.6.12 patches
parser/version/review behavior at runtime.
"""

import json
from typing import Any

from flask import abort, jsonify, request

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


def _ensure_review_schema() -> None:
    """Add correction/audit metadata without replacing the stable observations table."""
    with core.db() as conn:
        core.ensure_column(conn, "observations", "manual_corrected", "INTEGER NOT NULL DEFAULT 0")
        core.ensure_column(conn, "observations", "corrected_at", "TEXT NOT NULL DEFAULT ''")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS observation_corrections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                observation_id INTEGER NOT NULL REFERENCES observations(id) ON DELETE CASCADE,
                document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
                patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
                before_json TEXT NOT NULL,
                after_json TEXT NOT NULL,
                edited_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_observation_corrections_observation "
            "ON observation_corrections(observation_id, id)"
        )


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
    _ensure_review_schema()
    _remap_existing_glucose_rows()


core.init_db = init_db


def _optional_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


def _editable_snapshot(row) -> dict[str, Any]:
    return {
        "testName": row["test_name"],
        "value": row["value_numeric"] if row["value_numeric"] is not None else row["value_text"],
        "valueText": row["value_text"],
        "unit": row["unit"],
        "referenceLow": row["reference_low"],
        "referenceHigh": row["reference_high"],
        "referenceText": row["reference_text"],
        "date": row["date"],
        "lab": row["lab"],
        "panel": row["panel"],
        "method": row["method"],
        "notes": row["notes"],
    }


def _apply_observation_edit(conn, row, payload: dict[str, Any]) -> bool:
    """Apply one manual correction and preserve the pre-edit values in an audit table."""
    corrected_name = str(payload.get("testName", row["test_name"] or row["raw_test_name"])).strip()
    if not corrected_name:
        raise ValueError("test_required")

    raw_value = payload.get("value", row["value_numeric"] if row["value_numeric"] is not None else row["value_text"])
    value_text = str(raw_value if raw_value is not None else "").strip()
    if not value_text:
        raise ValueError("value_required")
    try:
        value_numeric = float(raw_value)
    except (TypeError, ValueError):
        value_numeric = None

    raw_unit = str(payload.get("unit", row["unit"] or "")).strip()
    reference_low = _optional_float(payload.get("referenceLow", row["reference_low"]))
    reference_high = _optional_float(payload.get("referenceHigh", row["reference_high"]))
    reference_text = str(payload.get("referenceText", row["reference_text"] or "")).strip()
    date = str(payload.get("date", row["date"] or "")).strip()
    lab = str(payload.get("lab", row["lab"] or "")).strip()
    panel = str(payload.get("panel", row["panel"] or "")).strip()
    method = str(payload.get("method", row["method"] or "")).strip()
    notes = str(payload.get("notes", row["notes"] or "")).strip()

    before = _editable_snapshot(row)
    proposed = {
        "testName": corrected_name,
        "value": value_numeric if value_numeric is not None else value_text,
        "valueText": value_text,
        "unit": raw_unit,
        "referenceLow": reference_low,
        "referenceHigh": reference_high,
        "referenceText": reference_text,
        "date": date,
        "lab": lab,
        "panel": panel,
        "method": method,
        "notes": notes,
    }
    if before == proposed:
        return False

    normalized = normalize_observation_payload(
        conn,
        raw_name=corrected_name,
        panel=panel,
        lab=lab,
        raw_unit=raw_unit,
        value_numeric=value_numeric,
        reference_low=reference_low,
        reference_high=reference_high,
    )
    now = core.utc_now()
    conn.execute(
        """
        UPDATE observations SET
            test_name=?, value_numeric=?, value_text=?, unit=?, reference_low=?, reference_high=?,
            reference_text=?, date=?, lab=?, panel=?, method=?, notes=?,
            clinical_test_id=?, canonical_key=?, canonical_name_es=?, canonical_name_en=?, specimen_detail=?,
            canonical_unit=?, unit_ucum=?, normalized_value_numeric=?, normalized_reference_low=?,
            normalized_reference_high=?, normalization_status=?, reference_url=?, reference_label=?, mapping_status=?,
            manual_corrected=1, corrected_at=?
        WHERE id=?
        """,
        (
            normalized["canonical_name_es"], value_numeric, value_text, raw_unit,
            reference_low, reference_high, reference_text, date, lab, panel, method, notes,
            normalized["clinical_test_id"], normalized["canonical_key"],
            normalized["canonical_name_es"], normalized["canonical_name_en"],
            normalized["specimen_detail"], normalized["canonical_unit"], normalized["unit_ucum"],
            normalized["normalized_value_numeric"], normalized["normalized_reference_low"],
            normalized["normalized_reference_high"], normalized["normalization_status"],
            normalized["reference_url"], normalized["reference_label"], normalized["mapping_status"],
            now, row["id"],
        ),
    )
    after_row = conn.execute("SELECT * FROM observations WHERE id=?", (row["id"],)).fetchone()
    after = _editable_snapshot(after_row)
    conn.execute(
        """
        INSERT INTO observation_corrections(
            observation_id, document_id, patient_id, before_json, after_json, edited_at
        ) VALUES(?,?,?,?,?,?)
        """,
        (
            row["id"], row["document_id"], row["patient_id"],
            json.dumps(before, ensure_ascii=False), json.dumps(after, ensure_ascii=False), now,
        ),
    )
    return True


@core.app.get("/api/documents/<int:document_id>/review-results")
def review_document_results(document_id: int):
    with core.db() as conn:
        document = conn.execute("SELECT * FROM documents WHERE id=?", (document_id,)).fetchone()
        if not document:
            abort(404)
        rows = conn.execute(
            "SELECT * FROM observations WHERE document_id=? ORDER BY source_page, id", (document_id,)
        ).fetchall()
        items = []
        for row in rows:
            item = core.observation_dict(row)
            first = conn.execute(
                "SELECT before_json FROM observation_corrections WHERE observation_id=? ORDER BY id LIMIT 1",
                (row["id"],),
            ).fetchone()
            item["ocr_original"] = json.loads(first["before_json"]) if first else None
            items.append(item)
    return jsonify({"document": core.row_dict(document), "observations": items})


@core.app.post("/api/documents/<int:document_id>/review-results")
def update_document_review_results(document_id: int):
    payload = request.get_json(silent=True) or {}
    edits = payload.get("observations") or []
    if not isinstance(edits, list):
        return jsonify({"error": "invalid_observations"}), 400
    changed = 0
    try:
        with core.db() as conn:
            document = conn.execute("SELECT id FROM documents WHERE id=?", (document_id,)).fetchone()
            if not document:
                abort(404)
            for edit in edits:
                try:
                    observation_id = int(edit.get("id"))
                except (TypeError, ValueError):
                    return jsonify({"error": "invalid_observation"}), 400
                row = conn.execute(
                    "SELECT * FROM observations WHERE id=? AND document_id=?",
                    (observation_id, document_id),
                ).fetchone()
                if not row:
                    return jsonify({"error": "invalid_observation"}), 400
                changed += 1 if _apply_observation_edit(conn, row, edit) else 0
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"state": core.current_state(), "changed": changed})


@core.app.post("/api/observations/<int:observation_id>/edit")
def edit_observation(observation_id: int):
    """Advanced-mode edit endpoint. UI gates it; API validates the record itself."""
    payload = request.get_json(silent=True) or {}
    try:
        with core.db() as conn:
            row = conn.execute("SELECT * FROM observations WHERE id=?", (observation_id,)).fetchone()
            if not row:
                abort(404)
            changed = _apply_observation_edit(conn, row, payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"state": core.current_state(), "changed": bool(changed)})


app = core.app
main_with_args = core.main_with_args
current_state = core.current_state


def main() -> None:
    core.main()


def __getattr__(name: str):
    return getattr(core, name)


if __name__ == "__main__":
    main()
