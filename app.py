from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import sqlite3
import zipfile
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from flask import Flask, abort, jsonify, render_template, request, send_file
import fitz
from werkzeug.utils import secure_filename
from werkzeug.serving import make_server

from lab_pdf_parser import parse_lab_pdf
from clinical_dictionary import (
    MEDLINEPLUS_DIR, SEEDS, choose_seed, convert_bound, convert_numeric, fallback_reference,
    key_text, normalize_unit, slug, specimen_from_context,
)

APP_VERSION = "0.6.11-registros-clinicos-weight"
ABOUT = {
    "product": "Registros Clínicos",
    "product_en": "Clinical Records",
    "legacy_product": "CodeCafe Lab Records",
    "author": "Jaime Sánchez Sáenz",
    "brand": "CodeCafe.io",
    "contact": "contacto@codecafe.io",
    "copyright": "© 2026 Jaime Sánchez Sáenz",
}

ROOT = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("CODECAFE_LAB_DATA", ROOT / "data")).resolve()
PDF_DIR = DATA_DIR / "pdfs"
DB_PATH = DATA_DIR / "lab_records.db"

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024
_SERVER = None


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def db() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}


def ensure_column(conn: sqlite3.Connection, table: str, name: str, ddl: str) -> None:
    if name not in table_columns(conn, table):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}")


def create_daily_measurements_table(conn: sqlite3.Connection, table: str = "daily_measurements") -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {table} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL REFERENCES patients(id),
            kind TEXT NOT NULL CHECK(kind IN ('blood_pressure','glucose','weight')),
            measured_at TEXT NOT NULL,
            systolic REAL,
            diastolic REAL,
            pulse REAL,
            glucose_value REAL,
            glucose_unit TEXT NOT NULL DEFAULT '',
            glucose_mg_dl REAL,
            weight_value REAL,
            weight_unit TEXT NOT NULL DEFAULT '',
            weight_kg REAL,
            context TEXT NOT NULL DEFAULT '',
            source_type TEXT NOT NULL DEFAULT 'manual',
            device_label TEXT NOT NULL DEFAULT '',
            notes TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        )
        """
    )


def migrate_daily_measurements_if_needed(conn: sqlite3.Connection) -> None:
    row = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='daily_measurements'"
    ).fetchone()
    if not row:
        create_daily_measurements_table(conn)
        return

    sql = (row["sql"] or "").lower()
    columns = table_columns(conn, "daily_measurements")
    if {"weight_value", "weight_unit", "weight_kg"}.issubset(columns) and "'weight'" in sql:
        return

    conn.execute("DROP INDEX IF EXISTS idx_daily_measurements_patient_time")
    conn.execute("ALTER TABLE daily_measurements RENAME TO daily_measurements_pre_weight")
    create_daily_measurements_table(conn)
    old_columns = table_columns(conn, "daily_measurements_pre_weight")

    def source(name: str, fallback: str = "NULL") -> str:
        return name if name in old_columns else fallback

    conn.execute(
        f"""
        INSERT INTO daily_measurements(
            id,patient_id,kind,measured_at,systolic,diastolic,pulse,
            glucose_value,glucose_unit,glucose_mg_dl,weight_value,weight_unit,weight_kg,
            context,source_type,device_label,notes,created_at
        )
        SELECT
            {source('id')},{source('patient_id')},{source('kind')},{source('measured_at')},
            {source('systolic')},{source('diastolic')},{source('pulse')},
            {source('glucose_value')},{source('glucose_unit', "''")},{source('glucose_mg_dl')},
            {source('weight_value')},{source('weight_unit', "''")},{source('weight_kg')},
            {source('context', "''")},{source('source_type', "'manual'")},
            {source('device_label', "''")},{source('notes', "''")},{source('created_at', "''")}
        FROM daily_measurements_pre_weight
        """
    )
    conn.execute("DROP TABLE daily_measurements_pre_weight")


def create_observations_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS observations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL REFERENCES patients(id),
            document_id INTEGER REFERENCES documents(id),
            test_name TEXT NOT NULL,
            raw_test_name TEXT NOT NULL DEFAULT '',
            value_numeric REAL,
            value_text TEXT NOT NULL DEFAULT '',
            unit TEXT NOT NULL DEFAULT '',
            reference_low REAL,
            reference_high REAL,
            reference_text TEXT NOT NULL DEFAULT '',
            date TEXT NOT NULL,
            lab TEXT NOT NULL DEFAULT '',
            panel TEXT NOT NULL DEFAULT '',
            method TEXT NOT NULL DEFAULT '',
            source_page INTEGER,
            extraction_confidence REAL,
            auto_extracted INTEGER NOT NULL DEFAULT 0,
            notes TEXT NOT NULL DEFAULT '',
            clinical_test_id INTEGER REFERENCES clinical_tests(id),
            canonical_key TEXT NOT NULL DEFAULT '',
            canonical_name_es TEXT NOT NULL DEFAULT '',
            canonical_name_en TEXT NOT NULL DEFAULT '',
            specimen_detail TEXT NOT NULL DEFAULT '',
            canonical_unit TEXT NOT NULL DEFAULT '',
            unit_ucum TEXT NOT NULL DEFAULT '',
            normalized_value_numeric REAL,
            normalized_reference_low REAL,
            normalized_reference_high REAL,
            normalization_status TEXT NOT NULL DEFAULT '',
            reference_url TEXT NOT NULL DEFAULT '',
            reference_label TEXT NOT NULL DEFAULT '',
            mapping_status TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        )
        """
    )


def migrate_observations_if_needed(conn: sqlite3.Connection) -> None:
    tables = {row["name"] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if "observations" not in tables:
        create_observations_table(conn)
        return
    columns = table_columns(conn, "observations")
    if "value_numeric" in columns:
        return
    if "value" not in columns:
        return

    conn.execute("DROP INDEX IF EXISTS idx_observations_patient_test_date")
    conn.execute("ALTER TABLE observations RENAME TO observations_v1")
    create_observations_table(conn)
    conn.execute(
        """
        INSERT INTO observations(
            id, patient_id, document_id, test_name, raw_test_name,
            value_numeric, value_text, unit, reference_low, reference_high,
            reference_text, date, lab, panel, method, source_page,
            extraction_confidence, auto_extracted, notes, created_at
        )
        SELECT
            id, patient_id, document_id, test_name, test_name,
            value, CAST(value AS TEXT), unit, reference_low, reference_high,
            '', date, lab, '', '', NULL, NULL, 0, notes, created_at
        FROM observations_v1
        """
    )
    conn.execute("DROP TABLE observations_v1")


def init_db() -> None:
    with db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS clinical_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                canonical_key TEXT NOT NULL UNIQUE,
                name_es TEXT NOT NULL,
                name_en TEXT NOT NULL,
                specimen TEXT NOT NULL DEFAULT '',
                canonical_unit TEXT NOT NULL DEFAULT '',
                ucum_code TEXT NOT NULL DEFAULT '',
                loinc_code TEXT NOT NULL DEFAULT '',
                reference_url TEXT NOT NULL DEFAULT '',
                reference_label TEXT NOT NULL DEFAULT 'MedlinePlus / NLM',
                status TEXT NOT NULL DEFAULT 'seed',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS test_aliases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                clinical_test_id INTEGER NOT NULL REFERENCES clinical_tests(id),
                alias_raw TEXT NOT NULL,
                alias_key TEXT NOT NULL,
                lab_scope TEXT NOT NULL DEFAULT '',
                specimen_scope TEXT NOT NULL DEFAULT '',
                unit_scope TEXT NOT NULL DEFAULT '',
                confirmed INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                UNIQUE(alias_key, lab_scope, specimen_scope, unit_scope)
            );

            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                initials TEXT NOT NULL DEFAULT '',
                dob TEXT NOT NULL DEFAULT '',
                notes TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL REFERENCES patients(id),
                file_name TEXT NOT NULL,
                stored_name TEXT NOT NULL,
                sha256 TEXT NOT NULL UNIQUE,
                lab TEXT NOT NULL DEFAULT '',
                report_date TEXT NOT NULL DEFAULT '',
                study_type TEXT NOT NULL DEFAULT '',
                specimen TEXT NOT NULL DEFAULT '',
                notes TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'review' CHECK(status IN ('review','confirmed')),
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS daily_measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL REFERENCES patients(id),
                kind TEXT NOT NULL CHECK(kind IN ('blood_pressure','glucose','weight')),
                measured_at TEXT NOT NULL,
                systolic REAL,
                diastolic REAL,
                pulse REAL,
                glucose_value REAL,
                glucose_unit TEXT NOT NULL DEFAULT '',
                glucose_mg_dl REAL,
                weight_value REAL,
                weight_unit TEXT NOT NULL DEFAULT '',
                weight_kg REAL,
                context TEXT NOT NULL DEFAULT '',
                source_type TEXT NOT NULL DEFAULT 'manual',
                device_label TEXT NOT NULL DEFAULT '',
                notes TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            );
            """
        )

        ensure_column(conn, "clinical_tests", "loinc_code", "TEXT NOT NULL DEFAULT ''")
        migrate_daily_measurements_if_needed(conn)

        document_columns = {
            "provider_legal": "TEXT NOT NULL DEFAULT ''",
            "branch": "TEXT NOT NULL DEFAULT ''",
            "address": "TEXT NOT NULL DEFAULT ''",
            "location": "TEXT NOT NULL DEFAULT ''",
            "registration_datetime": "TEXT NOT NULL DEFAULT ''",
            "patient_name_detected": "TEXT NOT NULL DEFAULT ''",
            "patient_dob_detected": "TEXT NOT NULL DEFAULT ''",
            "patient_sex_detected": "TEXT NOT NULL DEFAULT ''",
            "patient_external_id": "TEXT NOT NULL DEFAULT ''",
            "order_number": "TEXT NOT NULL DEFAULT ''",
            "directed_to": "TEXT NOT NULL DEFAULT ''",
            "page_count": "INTEGER",
            "extraction_engine": "TEXT NOT NULL DEFAULT ''",
            "extraction_confidence": "REAL",
            "extraction_warnings": "TEXT NOT NULL DEFAULT '[]'",
        }
        for name, ddl in document_columns.items():
            ensure_column(conn, "documents", name, ddl)

        migrate_observations_if_needed(conn)
        create_observations_table(conn)
        observation_columns = {
            "clinical_test_id": "INTEGER REFERENCES clinical_tests(id)",
            "canonical_key": "TEXT NOT NULL DEFAULT ''",
            "canonical_name_es": "TEXT NOT NULL DEFAULT ''",
            "canonical_name_en": "TEXT NOT NULL DEFAULT ''",
            "specimen_detail": "TEXT NOT NULL DEFAULT ''",
            "canonical_unit": "TEXT NOT NULL DEFAULT ''",
            "unit_ucum": "TEXT NOT NULL DEFAULT ''",
            "normalized_value_numeric": "REAL",
            "normalized_reference_low": "REAL",
            "normalized_reference_high": "REAL",
            "normalization_status": "TEXT NOT NULL DEFAULT ''",
            "reference_url": "TEXT NOT NULL DEFAULT ''",
            "reference_label": "TEXT NOT NULL DEFAULT ''",
            "mapping_status": "TEXT NOT NULL DEFAULT ''",
        }
        for name, ddl in observation_columns.items():
            ensure_column(conn, "observations", name, ddl)
        seed_clinical_dictionary(conn)
        normalize_existing_observations(conn)

        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_documents_patient_date ON documents(patient_id, report_date DESC)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_observations_patient_test_date ON observations(patient_id, test_name, date)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_daily_measurements_patient_time ON daily_measurements(patient_id, measured_at DESC)"
        )

        defaults = {
            "language": "es",
            "advanced_mode": "0",
            "active_patient_id": "",
            "text_size": "large",
        }
        for key, value in defaults.items():
            conn.execute("INSERT OR IGNORE INTO settings(key,value) VALUES(?,?)", (key, value))


def get_setting(conn: sqlite3.Connection, key: str, default: str = "") -> str:
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return row["value"] if row else default


def set_setting(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        "INSERT INTO settings(key,value) VALUES(?,?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, value),
    )


def row_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {key: row[key] for key in row.keys()}


def observation_dict(row: sqlite3.Row) -> dict[str, Any]:
    result = row_dict(row)
    result["value"] = result["value_numeric"] if result["value_numeric"] is not None else result["value_text"]
    return result


def seed_clinical_dictionary(conn: sqlite3.Connection) -> None:
    for item in SEEDS:
        unit_rule = normalize_unit(str(item.get("unit", "")))
        conn.execute(
            """
            INSERT INTO clinical_tests(
                canonical_key,name_es,name_en,specimen,canonical_unit,ucum_code,
                reference_url,reference_label,status,created_at
            ) VALUES(?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(canonical_key) DO UPDATE SET
                name_es=excluded.name_es,name_en=excluded.name_en,specimen=excluded.specimen,
                canonical_unit=excluded.canonical_unit,ucum_code=excluded.ucum_code,
                reference_url=excluded.reference_url,reference_label=excluded.reference_label
            """,
            (
                item["key"], item["es"], item["en"], item.get("specimen", ""),
                item.get("unit", ""), unit_rule.ucum, item.get("url", MEDLINEPLUS_DIR),
                "MedlinePlus / NLM" if "medlineplus.gov" in item.get("url", "") else "Autoridad médica",
                "seed", utc_now(),
            ),
        )
        test_id = conn.execute("SELECT id FROM clinical_tests WHERE canonical_key=?", (item["key"],)).fetchone()["id"]
        for alias in list(dict.fromkeys(item.get("aliases", []) + [item["es"], item["en"]])):
            conn.execute(
                """
                INSERT OR IGNORE INTO test_aliases(
                    clinical_test_id,alias_raw,alias_key,lab_scope,specimen_scope,unit_scope,confirmed,created_at
                ) VALUES(?,?,?,?,?,?,1,?)
                """,
                (test_id, alias, key_text(alias), "", item.get("specimen", ""), item.get("unit", ""), utc_now()),
            )


def clinical_test_dict(row: sqlite3.Row) -> dict[str, Any]:
    item = row_dict(row)
    item["aliases"] = []
    return item


def find_alias_match(
    conn: sqlite3.Connection, raw_name: str, lab: str, panel: str, raw_unit: str
) -> sqlite3.Row | None:
    alias_key = key_text(raw_name)
    specimen = specimen_from_context(panel, raw_name)
    unit_display = normalize_unit(raw_unit).display
    # IMPORTANT: select the canonical test columns first.  v0.3 selected
    # ``a.*, t.*`` which produced two columns named ``id``. sqlite3.Row returns
    # the *first* duplicate name, so observation inserts could accidentally use
    # the alias id as clinical_test_id and fail with a foreign-key HTTP 500.
    rows = conn.execute(
        """
        SELECT
            t.*,
            a.id AS alias_id,
            a.unit_scope AS alias_unit_scope,
            a.lab_scope AS alias_lab_scope,
            a.specimen_scope AS alias_specimen_scope,
            a.confirmed AS alias_confirmed
        FROM test_aliases a
        JOIN clinical_tests t ON t.id=a.clinical_test_id
        WHERE a.alias_key=? AND (a.lab_scope='' OR lower(a.lab_scope)=lower(?))
          AND (a.specimen_scope='' OR a.specimen_scope=?)
        ORDER BY (a.lab_scope<>'') DESC, (a.specimen_scope<>'') DESC, a.confirmed DESC
        """,
        (alias_key, lab, specimen),
    ).fetchall()
    if not rows:
        return None
    if len(rows) == 1:
        return rows[0]
    exact = [r for r in rows if not r["alias_unit_scope"] or r["alias_unit_scope"] == unit_display]
    return exact[0] if len(exact) == 1 else None


def create_provisional_test(
    conn: sqlite3.Connection, raw_name: str, lab: str, panel: str, raw_unit: str
) -> sqlite3.Row:
    specimen = specimen_from_context(panel, raw_name)
    unit = normalize_unit(raw_unit)
    canonical_key = f"provisional_{slug(raw_name)}_{slug(specimen)}_{slug(unit.display)}"
    reference_url = fallback_reference(panel, specimen)
    conn.execute(
        """
        INSERT OR IGNORE INTO clinical_tests(
            canonical_key,name_es,name_en,specimen,canonical_unit,ucum_code,
            reference_url,reference_label,status,created_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?)
        """,
        (
            canonical_key, raw_name, raw_name, specimen, unit.display, unit.ucum, reference_url,
            "MedlinePlus / NLM", "provisional", utc_now(),
        ),
    )
    test = conn.execute("SELECT * FROM clinical_tests WHERE canonical_key=?", (canonical_key,)).fetchone()
    conn.execute(
        """
        INSERT OR IGNORE INTO test_aliases(
            clinical_test_id,alias_raw,alias_key,lab_scope,specimen_scope,unit_scope,confirmed,created_at
        ) VALUES(?,?,?,?,?,?,0,?)
        """,
        (test["id"], raw_name, key_text(raw_name), lab, specimen, unit.display, utc_now()),
    )
    return test


def normalize_observation_payload(
    conn: sqlite3.Connection, *, raw_name: str, panel: str, lab: str, raw_unit: str,
    value_numeric: float | None, reference_low: float | None, reference_high: float | None
) -> dict[str, Any]:
    test = find_alias_match(conn, raw_name, lab, panel, raw_unit)
    if test is None:
        seed = choose_seed(raw_name, panel, raw_unit)
        if seed is not None:
            test = conn.execute("SELECT * FROM clinical_tests WHERE canonical_key=?", (seed["key"],)).fetchone()
            if test is not None:
                specimen = specimen_from_context(panel, raw_name)
                conn.execute(
                    """
                    INSERT OR IGNORE INTO test_aliases(
                        clinical_test_id,alias_raw,alias_key,lab_scope,specimen_scope,unit_scope,confirmed,created_at
                    ) VALUES(?,?,?,?,?,?,1,?)
                    """,
                    (test["id"], raw_name, key_text(raw_name), lab, specimen, normalize_unit(raw_unit).display, utc_now()),
                )
        if test is None:
            test = create_provisional_test(conn, raw_name, lab, panel, raw_unit)
    canonical_key = test["canonical_key"]
    normalized_value, display_unit, ucum, norm_status = convert_numeric(canonical_key, value_numeric, raw_unit)
    canonical_unit = test["canonical_unit"] or display_unit
    if norm_status == "original-only" and canonical_unit and display_unit and canonical_unit != display_unit:
        normalized_value = None
    return {
        "clinical_test_id": test["id"],
        "canonical_key": canonical_key,
        "canonical_name_es": test["name_es"],
        "canonical_name_en": test["name_en"],
        "specimen_detail": specimen_from_context(panel, raw_name),
        "canonical_unit": canonical_unit or display_unit,
        "unit_ucum": test["ucum_code"] or ucum,
        "normalized_value_numeric": normalized_value,
        "normalized_reference_low": convert_bound(canonical_key, reference_low, raw_unit),
        "normalized_reference_high": convert_bound(canonical_key, reference_high, raw_unit),
        "normalization_status": norm_status,
        "reference_url": test["reference_url"] or MEDLINEPLUS_DIR,
        "reference_label": test["reference_label"] or "MedlinePlus / NLM",
        "mapping_status": "confirmed" if test["status"] == "seed" else "review",
    }


def normalize_existing_observations(conn: sqlite3.Connection) -> None:
    rows = conn.execute(
        "SELECT * FROM observations WHERE canonical_key='' OR reference_url='' OR normalization_status=''"
    ).fetchall()
    for row in rows:
        normalized = normalize_observation_payload(
            conn, raw_name=row["raw_test_name"] or row["test_name"], panel=row["panel"], lab=row["lab"],
            raw_unit=row["unit"], value_numeric=row["value_numeric"],
            reference_low=row["reference_low"], reference_high=row["reference_high"],
        )
        assignments = ",".join(f"{key}=?" for key in normalized)
        conn.execute(
            f"UPDATE observations SET {assignments}, test_name=? WHERE id=?",
            (*normalized.values(), normalized["canonical_name_es"], row["id"]),
        )


def current_state() -> dict[str, Any]:
    with db() as conn:
        patients = [row_dict(r) for r in conn.execute("SELECT * FROM patients ORDER BY name COLLATE NOCASE")]
        documents = [row_dict(r) for r in conn.execute("SELECT * FROM documents ORDER BY report_date DESC, id DESC")]
        observations = [observation_dict(r) for r in conn.execute("SELECT * FROM observations ORDER BY date DESC, id DESC")]
        daily_measurements = [row_dict(r) for r in conn.execute(
            "SELECT * FROM daily_measurements ORDER BY measured_at DESC, id DESC"
        )]
        clinical_tests = [row_dict(r) for r in conn.execute(
            """SELECT t.*, COUNT(a.id) AS alias_count, SUM(CASE WHEN a.confirmed=0 THEN 1 ELSE 0 END) AS unresolved_aliases
               FROM clinical_tests t LEFT JOIN test_aliases a ON a.clinical_test_id=t.id
               GROUP BY t.id ORDER BY t.name_es COLLATE NOCASE"""
        )]
        unresolved_aliases = [row_dict(r) for r in conn.execute(
            """SELECT a.*, t.canonical_key, t.name_es AS current_name_es, t.name_en AS current_name_en
               FROM test_aliases a JOIN clinical_tests t ON t.id=a.clinical_test_id
               WHERE a.confirmed=0 ORDER BY a.alias_raw COLLATE NOCASE"""
        )]
        active_raw = get_setting(conn, "active_patient_id")
        active_id = int(active_raw) if active_raw.isdigit() else None
        valid_ids = {p["id"] for p in patients}
        if active_id not in valid_ids:
            active_id = patients[0]["id"] if patients else None
            set_setting(conn, "active_patient_id", str(active_id or ""))
        return {
            "language": get_setting(conn, "language", "es"),
            "advancedMode": get_setting(conn, "advanced_mode", "0") == "1",
            "textSize": get_setting(conn, "text_size", "large"),
            "activePatientId": active_id,
            "patients": patients,
            "documents": documents,
            "observations": observations,
            "dailyMeasurements": daily_measurements,
            "clinicalTests": clinical_tests,
            "unresolvedAliases": unresolved_aliases,
            "version": APP_VERSION,
            "desktopMode": os.environ.get("CODECAFE_DESKTOP_MODE") == "1",
            "about": ABOUT,
        }


def read_pdf_upload(file) -> tuple[bytes | None, tuple[Any, int] | None]:
    if not file or not file.filename:
        return None, (jsonify({"error": "pdf_required"}), 400)
    if not file.filename.lower().endswith(".pdf"):
        return None, (jsonify({"error": "pdf_only"}), 400)
    data = file.read()
    if not data.startswith(b"%PDF"):
        return None, (jsonify({"error": "invalid_pdf"}), 400)
    return data, None


def optional_float(raw: Any) -> float | None:
    if raw in (None, ""):
        return None
    return float(raw)


@app.errorhandler(500)
def api_internal_error(error):
    if request.path.startswith("/api/"):
        original = getattr(error, "original_exception", None)
        if original is not None:
            app.logger.error("API error on %s: %s", request.path, original)
        payload = {"error": "server_error"}
        if app.debug and original is not None:
            payload["detail"] = str(original)
        return jsonify(payload), 500
    return "Internal Server Error", 500


@app.after_request
def privacy_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    if request.path.startswith("/api/") or request.path.startswith("/pdf/") or request.path.startswith("/pdf-page/"):
        response.headers["Cache-Control"] = "private, no-store"
    return response


@app.get("/")
def index():
    return render_template("index.html", initial_state=current_state())


@app.get("/api/state")
def api_state():
    return jsonify(current_state())


@app.get("/api/health")
def health():
    return jsonify({"ok": True, "database": str(DB_PATH), "version": APP_VERSION})


@app.post("/api/settings")
def update_settings():
    payload = request.get_json(silent=True) or {}
    with db() as conn:
        if payload.get("language") in {"es", "en"}:
            set_setting(conn, "language", payload["language"])
        if "advancedMode" in payload:
            set_setting(conn, "advanced_mode", "1" if bool(payload["advancedMode"]) else "0")
        if payload.get("textSize") in {"normal", "large", "xlarge"}:
            set_setting(conn, "text_size", payload["textSize"])
    return jsonify(current_state())


@app.post("/api/profiles")
def create_profile():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    if not name:
        return jsonify({"error": "name_required"}), 400
    initials = str(payload.get("initials", "")).strip()[:8]
    dob = str(payload.get("dob", "")).strip()
    notes = str(payload.get("notes", "")).strip()
    with db() as conn:
        cur = conn.execute(
            "INSERT INTO patients(name,initials,dob,notes,created_at) VALUES(?,?,?,?,?)",
            (name, initials, dob, notes, utc_now()),
        )
        patient_id = int(cur.lastrowid)
        if not get_setting(conn, "active_patient_id"):
            set_setting(conn, "active_patient_id", str(patient_id))
    return jsonify(current_state()), 201


@app.post("/api/profiles/<int:patient_id>")
def update_profile(patient_id: int):
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    if not name:
        return jsonify({"error": "name_required"}), 400
    with db() as conn:
        exists = conn.execute("SELECT 1 FROM patients WHERE id=?", (patient_id,)).fetchone()
        if not exists:
            abort(404)
        conn.execute(
            "UPDATE patients SET name=?, initials=?, dob=?, notes=? WHERE id=?",
            (
                name,
                str(payload.get("initials", "")).strip()[:8],
                str(payload.get("dob", "")).strip(),
                str(payload.get("notes", "")).strip(),
                patient_id,
            ),
        )
    return jsonify(current_state())


@app.post("/api/profiles/<int:patient_id>/select")
def select_profile(patient_id: int):
    with db() as conn:
        exists = conn.execute("SELECT 1 FROM patients WHERE id=?", (patient_id,)).fetchone()
        if not exists:
            abort(404)
        set_setting(conn, "active_patient_id", str(patient_id))
    return jsonify(current_state())


@app.delete("/api/profiles/<int:patient_id>")
def delete_profile(patient_id: int):
    with db() as conn:
        linked = conn.execute(
            "SELECT (SELECT COUNT(*) FROM documents WHERE patient_id=?) + "
            "(SELECT COUNT(*) FROM observations WHERE patient_id=?) + "
            "(SELECT COUNT(*) FROM daily_measurements WHERE patient_id=?) AS total",
            (patient_id, patient_id, patient_id),
        ).fetchone()["total"]
        if linked:
            return jsonify({"error": "profile_has_records"}), 409
        cur = conn.execute("DELETE FROM patients WHERE id=?", (patient_id,))
        if cur.rowcount == 0:
            abort(404)
        if get_setting(conn, "active_patient_id") == str(patient_id):
            next_row = conn.execute("SELECT id FROM patients ORDER BY name COLLATE NOCASE LIMIT 1").fetchone()
            set_setting(conn, "active_patient_id", str(next_row["id"] if next_row else ""))
    return jsonify(current_state())


@app.post("/api/documents/analyze")
def analyze_document():
    file = request.files.get("file")
    data, error = read_pdf_upload(file)
    if error:
        return error
    assert data is not None
    parsed = parse_lab_pdf(data)
    parsed["sha256"] = hashlib.sha256(data).hexdigest()
    parsed["file_name"] = file.filename
    return jsonify(parsed)


def store_document_bytes(
    *,
    patient_id: int,
    file_name: str,
    data: bytes,
    import_results: bool = True,
    report_date: str = "",
    lab: str = "",
    study_type: str = "",
    specimen: str = "",
    notes: str = "",
    parsed: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Persist one PDF and its extracted observations.

    This shared helper is used by both the ordinary upload flow and the desktop bulk
    importer, so single-file and folder imports follow exactly the same validation,
    duplicate detection, normalization and source-preservation rules.
    """
    if not file_name.lower().endswith(".pdf") or not data.startswith(b"%PDF"):
        return {"error": "invalid_pdf"}
    digest = hashlib.sha256(data).hexdigest()
    parsed = parsed or parse_lab_pdf(data)
    metadata = parsed.get("metadata", {}) if parsed.get("ok") else {}

    with db() as conn:
        if not conn.execute("SELECT 1 FROM patients WHERE id=?", (patient_id,)).fetchone():
            return {"error": "patient_required"}
        duplicate = conn.execute("SELECT id FROM documents WHERE sha256=?", (digest,)).fetchone()
        if duplicate:
            return {"error": "duplicate", "documentId": int(duplicate["id"]), "sha256": digest}

        safe = secure_filename(file_name) or f"report-{digest[:12]}.pdf"
        patient_dir = PDF_DIR / str(patient_id)
        patient_dir.mkdir(parents=True, exist_ok=True)
        stored_name = f"{digest}_{safe}"
        final_path = patient_dir / stored_name
        final_path.write_bytes(data)

        final_report_date = report_date.strip() or str(metadata.get("report_date", "")).strip()
        final_lab = lab.strip() or str(metadata.get("lab", "")).strip()
        final_study_type = study_type.strip() or str(metadata.get("study_type", "")).strip()
        final_specimen = specimen.strip() or str(metadata.get("specimen", "")).strip()

        try:
            cur = conn.execute(
                """
                INSERT INTO documents(
                    patient_id,file_name,stored_name,sha256,lab,report_date,study_type,specimen,
                    notes,status,created_at,provider_legal,branch,address,location,
                    registration_datetime,patient_name_detected,patient_dob_detected,
                    patient_sex_detected,patient_external_id,order_number,directed_to,page_count,
                    extraction_engine,extraction_confidence,extraction_warnings
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    patient_id,
                    file_name,
                    stored_name,
                    digest,
                    final_lab,
                    final_report_date,
                    final_study_type,
                    final_specimen,
                    notes.strip(),
                    "review",
                    utc_now(),
                    str(metadata.get("provider_legal", "")),
                    str(metadata.get("branch", "")),
                    str(metadata.get("address", "")),
                    str(metadata.get("location", "")),
                    str(metadata.get("registration_datetime", "")),
                    str(metadata.get("patient_name", "")),
                    str(metadata.get("dob", "")),
                    str(metadata.get("sex", "")),
                    str(metadata.get("patient_external_id", "")),
                    str(metadata.get("order_number", "")),
                    str(metadata.get("directed_to", "")),
                    parsed.get("page_count"),
                    str(parsed.get("engine", "")),
                    parsed.get("confidence"),
                    json.dumps(parsed.get("warnings", []), ensure_ascii=False),
                ),
            )
            document_id = int(cur.lastrowid)

            imported_count = 0
            if import_results:
                for item in parsed.get("observations", []):
                    value_text = str(item.get("value_text", "")).strip()
                    value_numeric = item.get("value_numeric")
                    if not str(item.get("test_name", "")).strip() or (value_numeric is None and not value_text):
                        continue
                    raw_name = str(item.get("raw_test_name", item.get("test_name", ""))).strip()
                    raw_unit = str(item.get("unit", "")).strip()
                    panel = str(item.get("panel", "")).strip()
                    normalized = normalize_observation_payload(
                        conn, raw_name=raw_name, panel=panel, lab=final_lab, raw_unit=raw_unit,
                        value_numeric=value_numeric, reference_low=item.get("reference_low"),
                        reference_high=item.get("reference_high"),
                    )
                    conn.execute(
                        """
                        INSERT INTO observations(
                            patient_id,document_id,test_name,raw_test_name,value_numeric,value_text,
                            unit,reference_low,reference_high,reference_text,date,lab,panel,method,
                            source_page,extraction_confidence,auto_extracted,notes,
                            clinical_test_id,canonical_key,canonical_name_es,canonical_name_en,specimen_detail,
                            canonical_unit,unit_ucum,normalized_value_numeric,normalized_reference_low,
                            normalized_reference_high,normalization_status,reference_url,reference_label,mapping_status,
                            created_at
                        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                        """,
                        (
                            patient_id, document_id, normalized["canonical_name_es"], raw_name,
                            value_numeric, value_text, raw_unit, item.get("reference_low"), item.get("reference_high"),
                            str(item.get("reference_text", "")).strip(), final_report_date, final_lab, panel,
                            str(item.get("method", "")).strip(), item.get("source_page"),
                            item.get("extraction_confidence"), 1, str(item.get("notes", "")).strip(),
                            normalized["clinical_test_id"], normalized["canonical_key"],
                            normalized["canonical_name_es"], normalized["canonical_name_en"],
                            normalized["specimen_detail"], normalized["canonical_unit"], normalized["unit_ucum"],
                            normalized["normalized_value_numeric"], normalized["normalized_reference_low"],
                            normalized["normalized_reference_high"], normalized["normalization_status"],
                            normalized["reference_url"], normalized["reference_label"], normalized["mapping_status"],
                            utc_now(),
                        ),
                    )
                    imported_count += 1
        except Exception:
            final_path.unlink(missing_ok=True)
            raise

    return {
        "ok": True,
        "documentId": document_id,
        "importedResults": imported_count,
        "sha256": digest,
        "parsed": parsed,
    }


@app.post("/api/documents")
def create_document():
    patient_raw = request.form.get("patient_id", "")
    if not patient_raw.isdigit():
        return jsonify({"error": "patient_required"}), 400
    patient_id = int(patient_raw)

    file = request.files.get("file")
    data, error = read_pdf_upload(file)
    if error:
        return error
    assert data is not None and file is not None

    result = store_document_bytes(
        patient_id=patient_id,
        file_name=file.filename,
        data=data,
        import_results=request.form.get("import_results", "1") not in {"0", "false", "False"},
        report_date=request.form.get("report_date", ""),
        lab=request.form.get("lab", ""),
        study_type=request.form.get("study_type", ""),
        specimen=request.form.get("specimen", ""),
        notes=request.form.get("notes", ""),
    )
    if result.get("error") == "patient_required":
        return jsonify({"error": "patient_required"}), 400
    if result.get("error") == "duplicate":
        return jsonify({"error": "duplicate", "documentId": result.get("documentId")}), 409
    if result.get("error"):
        return jsonify({"error": result["error"]}), 400
    return jsonify({
        "state": current_state(),
        "documentId": result["documentId"],
        "importedResults": result["importedResults"],
    }), 201


def _desktop_local_path_allowed() -> bool:
    return os.environ.get("CODECAFE_DESKTOP_MODE") == "1"


def _pdf_paths_in_folder(folder: Path, recursive: bool) -> list[Path]:
    iterator = folder.rglob("*") if recursive else folder.iterdir()
    paths = [p for p in iterator if p.is_file() and p.suffix.casefold() == ".pdf"]
    return sorted(paths, key=lambda x: str(x).casefold())[:250]


@app.post("/api/documents/bulk/analyze-local")
def bulk_analyze_local_documents():
    if not _desktop_local_path_allowed():
        return jsonify({"error": "desktop_only"}), 403
    payload = request.get_json(silent=True) or {}
    folder_raw = str(payload.get("folder", "")).strip()
    if not folder_raw:
        return jsonify({"error": "folder_required"}), 400
    folder = Path(folder_raw).expanduser().resolve()
    if not folder.is_dir():
        return jsonify({"error": "folder_not_found"}), 404
    recursive = bool(payload.get("recursive", False))
    paths = _pdf_paths_in_folder(folder, recursive)
    items: list[dict[str, Any]] = []
    with db() as conn:
        for path in paths:
            try:
                data = path.read_bytes()
                if not data.startswith(b"%PDF"):
                    items.append({"path": str(path), "fileName": path.name, "error": "invalid_pdf"})
                    continue
                digest = hashlib.sha256(data).hexdigest()
                duplicate = conn.execute("SELECT id FROM documents WHERE sha256=?", (digest,)).fetchone()
                if duplicate:
                    items.append({
                        "path": str(path), "fileName": path.name, "sha256": digest,
                        "duplicate": True, "documentId": int(duplicate["id"]),
                    })
                    continue
                parsed = parse_lab_pdf(data)
                items.append({
                    "path": str(path), "fileName": path.name, "sha256": digest,
                    "duplicate": False, "parsed": parsed,
                })
            except Exception as exc:
                app.logger.error("Bulk analysis failed for %s: %s", path, exc)
                items.append({"path": str(path), "fileName": path.name, "error": "analysis_failed"})
    return jsonify({"folder": str(folder), "recursive": recursive, "count": len(paths), "items": items})


@app.post("/api/documents/bulk/import-local")
def bulk_import_local_documents():
    if not _desktop_local_path_allowed():
        return jsonify({"error": "desktop_only"}), 403
    payload = request.get_json(silent=True) or {}
    try:
        patient_id = int(payload.get("patientId"))
    except (TypeError, ValueError):
        return jsonify({"error": "patient_required"}), 400
    paths_raw = payload.get("paths") or []
    if not isinstance(paths_raw, list) or not paths_raw:
        return jsonify({"error": "files_required"}), 400
    import_results = bool(payload.get("importResults", True))
    results: list[dict[str, Any]] = []
    imported_documents = 0
    imported_results = 0
    for raw in paths_raw[:250]:
        path = Path(str(raw)).expanduser().resolve()
        if not path.is_file() or path.suffix.casefold() != ".pdf":
            results.append({"path": str(path), "fileName": path.name, "error": "file_not_found"})
            continue
        try:
            data = path.read_bytes()
            result = store_document_bytes(
                patient_id=patient_id, file_name=path.name, data=data,
                import_results=import_results,
            )
            if result.get("error"):
                results.append({"path": str(path), "fileName": path.name, **result})
                continue
            imported_documents += 1
            imported_results += int(result.get("importedResults") or 0)
            results.append({
                "path": str(path), "fileName": path.name, "ok": True,
                "documentId": result["documentId"], "importedResults": result["importedResults"],
            })
        except Exception as exc:
            app.logger.error("Bulk import failed for %s: %s", path, exc)
            results.append({"path": str(path), "fileName": path.name, "error": "server_error"})
    return jsonify({
        "state": current_state(),
        "importedDocuments": imported_documents,
        "importedResults": imported_results,
        "items": results,
    })


@app.post("/api/documents/<int:document_id>/confirm")
def confirm_document(document_id: int):
    with db() as conn:
        cur = conn.execute("UPDATE documents SET status='confirmed' WHERE id=?", (document_id,))
        if cur.rowcount == 0:
            abort(404)
    return jsonify(current_state())


@app.delete("/api/documents/<int:document_id>")
def delete_document(document_id: int):
    with db() as conn:
        row = conn.execute("SELECT patient_id, stored_name FROM documents WHERE id=?", (document_id,)).fetchone()
        if not row:
            abort(404)
        # Results imported from a report belong to that source document. Deleting the
        # PDF from Advanced mode therefore removes its linked structured results too,
        # after the UI confirmation, so a mistaken import can be cleanly undone.
        conn.execute("DELETE FROM observations WHERE document_id=?", (document_id,))
        conn.execute("DELETE FROM documents WHERE id=?", (document_id,))
        (PDF_DIR / str(row["patient_id"]) / row["stored_name"]).unlink(missing_ok=True)
    return jsonify(current_state())


def document_pdf_path(document_id: int):
    with db() as conn:
        row = conn.execute(
            "SELECT patient_id, stored_name, file_name, page_count FROM documents WHERE id=?",
            (document_id,),
        ).fetchone()
        if not row:
            abort(404)
    path = PDF_DIR / str(row["patient_id"]) / row["stored_name"]
    if not path.is_file():
        abort(404)
    return row, path


@app.get("/pdf/<int:document_id>")
def pdf_file(document_id: int):
    # Preserve access to the exact original PDF. The normal desktop UI does not
    # navigate here directly; it renders pages through /pdf-page so that the
    # document stays inside the pywebview application even on systems whose web
    # engine delegates application/pdf to an external browser.
    row, path = document_pdf_path(document_id)
    return send_file(path, mimetype="application/pdf", download_name=row["file_name"], conditional=True)


@app.get("/api/documents/<int:document_id>/pdf-info")
def pdf_info(document_id: int):
    row, path = document_pdf_path(document_id)
    page_count = int(row["page_count"] or 0)
    if page_count <= 0:
        try:
            with fitz.open(path) as pdf:
                page_count = pdf.page_count
        except Exception:
            abort(500)
    return jsonify({"documentId": document_id, "pageCount": page_count, "fileName": row["file_name"]})


@app.get("/pdf-page/<int:document_id>/<int:page_number>")
def pdf_page_image(document_id: int, page_number: int):
    # Page numbers are 1-based for the UI. Rendering with PyMuPDF avoids relying
    # on a browser PDF plug-in and therefore works consistently inside pywebview.
    _, path = document_pdf_path(document_id)
    if page_number < 1:
        abort(404)
    try:
        zoom_raw = request.args.get("zoom", "1.65")
        zoom = max(0.8, min(float(zoom_raw), 2.5))
    except (TypeError, ValueError):
        zoom = 1.65
    try:
        pdf = fitz.open(path)
    except Exception as exc:
        app.logger.error("Could not open PDF %s for rendering: %s", document_id, exc)
        abort(500)
    with pdf:
        if page_number > pdf.page_count:
            abort(404)
        try:
            page = pdf.load_page(page_number - 1)
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
            payload = io.BytesIO(pix.tobytes("png"))
        except Exception as exc:
            app.logger.error("Could not render PDF page %s/%s: %s", document_id, page_number, exc)
            abort(500)
    return send_file(payload, mimetype="image/png", download_name=f"page-{page_number}.png")


@app.post("/api/observations")
def create_observation():
    payload = request.get_json(silent=True) or {}
    try:
        patient_id = int(payload.get("patientId"))
    except (TypeError, ValueError):
        return jsonify({"error": "patient_required"}), 400

    test_name = str(payload.get("testName", "")).strip()
    date = str(payload.get("date", "")).strip()
    raw_value = payload.get("value")
    value_text = str(raw_value if raw_value is not None else "").strip()
    if not test_name or not date or not value_text:
        return jsonify({"error": "required_fields"}), 400
    try:
        value_numeric = float(raw_value)
    except (TypeError, ValueError):
        value_numeric = None

    document_id = payload.get("documentId")
    if document_id in (None, "", 0, "0"):
        document_id = None
    else:
        try:
            document_id = int(document_id)
        except (TypeError, ValueError):
            return jsonify({"error": "invalid_document"}), 400

    try:
        low = optional_float(payload.get("referenceLow"))
        high = optional_float(payload.get("referenceHigh"))
    except (TypeError, ValueError):
        return jsonify({"error": "invalid_range"}), 400

    with db() as conn:
        if not conn.execute("SELECT 1 FROM patients WHERE id=?", (patient_id,)).fetchone():
            return jsonify({"error": "patient_required"}), 400
        if document_id is not None:
            doc = conn.execute("SELECT patient_id FROM documents WHERE id=?", (document_id,)).fetchone()
            if not doc or doc["patient_id"] != patient_id:
                return jsonify({"error": "invalid_document"}), 400
        lab = str(payload.get("lab", "")).strip()
        panel = str(payload.get("panel", "")).strip()
        raw_unit = str(payload.get("unit", "")).strip()
        normalized = normalize_observation_payload(
            conn, raw_name=test_name, panel=panel, lab=lab, raw_unit=raw_unit,
            value_numeric=value_numeric, reference_low=low, reference_high=high,
        )
        conn.execute(
            """
            INSERT INTO observations(
                patient_id,document_id,test_name,raw_test_name,value_numeric,value_text,
                unit,reference_low,reference_high,reference_text,date,lab,panel,method,
                source_page,extraction_confidence,auto_extracted,notes,
                clinical_test_id,canonical_key,canonical_name_es,canonical_name_en,specimen_detail,
                canonical_unit,unit_ucum,normalized_value_numeric,normalized_reference_low,
                normalized_reference_high,normalization_status,reference_url,reference_label,mapping_status,created_at
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                patient_id, document_id, normalized["canonical_name_es"], test_name, value_numeric, value_text,
                raw_unit, low, high, str(payload.get("referenceText", "")).strip(), date, lab, panel,
                str(payload.get("method", "")).strip(), None, None, 0, str(payload.get("notes", "")).strip(),
                normalized["clinical_test_id"], normalized["canonical_key"], normalized["canonical_name_es"],
                normalized["canonical_name_en"], normalized["specimen_detail"], normalized["canonical_unit"],
                normalized["unit_ucum"], normalized["normalized_value_numeric"], normalized["normalized_reference_low"],
                normalized["normalized_reference_high"], normalized["normalization_status"], normalized["reference_url"],
                normalized["reference_label"], normalized["mapping_status"], utc_now(),
            ),
        )
    return jsonify(current_state()), 201


@app.delete("/api/observations/<int:observation_id>")
def delete_observation(observation_id: int):
    with db() as conn:
        cur = conn.execute("DELETE FROM observations WHERE id=?", (observation_id,))
        if cur.rowcount == 0:
            abort(404)
    return jsonify(current_state())


@app.post("/api/measurements")
def create_daily_measurement():
    payload = request.get_json(silent=True) or {}
    try:
        patient_id = int(payload.get("patientId"))
    except (TypeError, ValueError):
        return jsonify({"error": "patient_required"}), 400

    kind = str(payload.get("kind", "")).strip()
    measured_at = str(payload.get("measuredAt", "")).strip()
    if kind not in {"blood_pressure", "glucose", "weight"} or not measured_at:
        return jsonify({"error": "required_fields"}), 400

    def positive_float(value: Any, *, required: bool = False) -> float | None:
        if value in (None, ""):
            if required:
                raise ValueError
            return None
        number = float(value)
        if number <= 0:
            raise ValueError
        return number

    try:
        systolic = diastolic = pulse = None
        glucose_value = None
        glucose_unit = ""
        glucose_mg_dl = None
        weight_value = None
        weight_unit = ""
        weight_kg = None

        if kind == "blood_pressure":
            systolic = positive_float(payload.get("systolic"), required=True)
            diastolic = positive_float(payload.get("diastolic"), required=True)
            pulse = positive_float(payload.get("pulse"))
        elif kind == "glucose":
            glucose_value = positive_float(payload.get("glucoseValue"), required=True)
            glucose_unit = str(payload.get("glucoseUnit", "mg/dL")).strip() or "mg/dL"
            if glucose_unit not in {"mg/dL", "mmol/L"}:
                return jsonify({"error": "invalid_glucose_unit"}), 400
            glucose_mg_dl = glucose_value if glucose_unit == "mg/dL" else glucose_value * 18.0182
        else:
            weight_value = positive_float(payload.get("weightValue"), required=True)
            weight_unit = str(payload.get("weightUnit", "kg")).strip().lower() or "kg"
            if weight_unit not in {"kg", "lb"}:
                return jsonify({"error": "invalid_weight_unit"}), 400
            weight_kg = weight_value if weight_unit == "kg" else weight_value * 0.45359237
    except (TypeError, ValueError):
        return jsonify({"error": "invalid_measurement"}), 400

    with db() as conn:
        if not conn.execute("SELECT 1 FROM patients WHERE id=?", (patient_id,)).fetchone():
            return jsonify({"error": "patient_required"}), 400
        conn.execute(
            """
            INSERT INTO daily_measurements(
                patient_id,kind,measured_at,systolic,diastolic,pulse,glucose_value,
                glucose_unit,glucose_mg_dl,weight_value,weight_unit,weight_kg,context,
                source_type,device_label,notes,created_at
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                patient_id, kind, measured_at, systolic, diastolic, pulse, glucose_value,
                glucose_unit, glucose_mg_dl, weight_value, weight_unit, weight_kg,
                str(payload.get("context", "")).strip(),
                str(payload.get("sourceType", "manual")).strip() or "manual",
                str(payload.get("deviceLabel", "")).strip(),
                str(payload.get("notes", "")).strip(), utc_now(),
            ),
        )
    return jsonify(current_state()), 201


@app.delete("/api/measurements/<int:measurement_id>")
def delete_daily_measurement(measurement_id: int):
    with db() as conn:
        cur = conn.execute("DELETE FROM daily_measurements WHERE id=?", (measurement_id,))
        if cur.rowcount == 0:
            abort(404)
    return jsonify(current_state())


@app.post("/api/dictionary/aliases/<int:alias_id>/map")
def map_dictionary_alias(alias_id: int):
    payload = request.get_json(silent=True) or {}
    try:
        target_id = int(payload.get("clinicalTestId"))
    except (TypeError, ValueError):
        return jsonify({"error": "clinical_test_required"}), 400
    with db() as conn:
        alias = conn.execute("SELECT * FROM test_aliases WHERE id=?", (alias_id,)).fetchone()
        target = conn.execute("SELECT * FROM clinical_tests WHERE id=?", (target_id,)).fetchone()
        if not alias or not target:
            abort(404)
        conn.execute(
            "UPDATE test_aliases SET clinical_test_id=?, confirmed=1 WHERE id=?",
            (target_id, alias_id),
        )
        rows = conn.execute("SELECT * FROM observations").fetchall()
        for row in rows:
            if key_text(row["raw_test_name"] or row["test_name"]) != alias["alias_key"]:
                continue
            if alias["lab_scope"] and row["lab"].casefold() != alias["lab_scope"].casefold():
                continue
            specimen = specimen_from_context(row["panel"], row["raw_test_name"] or row["test_name"])
            if alias["specimen_scope"] and specimen != alias["specimen_scope"]:
                continue
            if alias["unit_scope"] and normalize_unit(row["unit"]).display != alias["unit_scope"]:
                continue
            normalized = normalize_observation_payload(
                conn, raw_name=row["raw_test_name"] or row["test_name"], panel=row["panel"], lab=row["lab"],
                raw_unit=row["unit"], value_numeric=row["value_numeric"],
                reference_low=row["reference_low"], reference_high=row["reference_high"],
            )
            assignments = ",".join(f"{key}=?" for key in normalized)
            conn.execute(
                f"UPDATE observations SET {assignments}, test_name=? WHERE id=?",
                (*normalized.values(), normalized["canonical_name_es"], row["id"]),
            )
    return jsonify(current_state())


@app.get("/api/backup/metadata")
def metadata_backup():
    payload = current_state()
    payload["format"] = "codecafe-lab-records-metadata-v0.6"
    payload["exportedAt"] = utc_now()
    raw = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    return send_file(
        io.BytesIO(raw),
        mimetype="application/json",
        as_attachment=True,
        download_name=f"codecafe-lab-records-metadata-{datetime.now().date().isoformat()}.json",
    )


@app.get("/api/backup/full")
def full_backup():
    memory = io.BytesIO()
    with zipfile.ZipFile(memory, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        if DB_PATH.exists():
            zf.write(DB_PATH, "data/lab_records.db")
        if PDF_DIR.exists():
            for path in PDF_DIR.rglob("*.pdf"):
                zf.write(path, f"data/pdfs/{path.relative_to(PDF_DIR)}")
        manifest = {
            "format": "codecafe-lab-records-full-backup-v0.6",
            "exportedAt": utc_now(),
            "warning": "Contains private medical information. Store securely.",
        }
        zf.writestr("backup-manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    memory.seek(0)
    return send_file(
        memory,
        mimetype="application/zip",
        as_attachment=True,
        download_name=f"codecafe-lab-records-full-backup-{datetime.now().date().isoformat()}.zip",
    )


@app.post("/api/shutdown")
def shutdown_app():
    # This control is intentionally local-only. A future phone client must never be able
    # to turn off the host application's server over the network.
    if request.remote_addr not in {"127.0.0.1", "::1"}:
        return jsonify({"error": "local_only"}), 403
    server = globals().get("_SERVER")
    if server is None:
        return jsonify({"error": "shutdown_unavailable"}), 409

    def stop_server() -> None:
        time.sleep(0.15)  # allow the HTTP response to reach the browser first
        server.shutdown()

    threading.Thread(target=stop_server, daemon=True).start()
    return jsonify({"ok": True})



def main_with_args(*, host: str = "127.0.0.1", port: int = 5000, debug: bool = False, open_browser: bool = False) -> None:
    global _SERVER
    init_db()
    app.debug = bool(debug)
    _SERVER = make_server(host, port, app, threaded=True)
    url = f"http://{host}:{port}"
    print(f"Registros Clínicos by CodeCafe {APP_VERSION} running at {url}")
    if open_browser:
        import webbrowser
        threading.Timer(0.35, lambda: webbrowser.open(url, new=1)).start()
    try:
        _SERVER.serve_forever()
    finally:
        _SERVER.server_close()
        _SERVER = None


def main() -> None:
    parser = argparse.ArgumentParser(description=f"Registros Clínicos by CodeCafe {APP_VERSION} browser/developer server")
    parser.add_argument("--host", default="127.0.0.1", help="Bind address; default keeps the app local-only")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--open-browser", action="store_true")
    args = parser.parse_args()
    main_with_args(host=args.host, port=args.port, debug=args.debug, open_browser=args.open_browser)


if __name__ == "__main__":
    main()
