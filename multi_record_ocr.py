from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import time
import unicodedata
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

try:
    import pymupdf
except Exception:  # pragma: no cover - optional until runtime setup is complete
    pymupdf = None


DEFAULT_PROFILE: dict[str, Any] = {
    "enabled": True,
    "multi_record_min_pages": 8,
    "first_pass_dpi": 90,
    "workers": 1,
    "batch_size": 4,
    "page_timeout_seconds": 30,
    "language": "spa+eng",
}

MONTHS = {
    "ene": 1, "enero": 1, "feb": 2, "febrero": 2, "mar": 3, "marzo": 3,
    "abr": 4, "abril": 4, "may": 5, "mayo": 5, "jun": 6, "junio": 6,
    "jul": 7, "julio": 7, "ago": 8, "agosto": 8, "sep": 9, "sept": 9,
    "septiembre": 9, "set": 9, "setiembre": 9, "oct": 10, "octubre": 10,
    "nov": 11, "noviembre": 11, "dic": 12, "diciembre": 12,
}

LAB_STUDIES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Examen general de orina", ("examen general de orina", "uroanalisis", "urianalisis")),
    ("Química sanguínea", ("quimica sanguinea",)),
    ("Biometría hemática", ("biometria hematica",)),
    ("Perfil hepático", ("perfil hepatico",)),
    ("Antígeno prostático específico (PSA)", ("antigeno prostatico especifico", " psa ")),
    ("Antígeno carcinoembrionario (CEA)", ("antigeno carcinoembrionario", " cea ")),
    ("Testosterona libre", ("testosterona libre",)),
    ("Anticuerpos anti-HIV", ("anticuerpos anti hiv", "anti hiv", "antihiv")),
    ("Curva de tolerancia a la insulina", ("curva de tolerancia a la insulina",)),
    ("Curva de tolerancia a la glucosa", ("curva de tolerancia a la glucosa",)),
    ("Urocultivo / cultivo", ("urocultivo", "cultivo bacteriologico")),
)


@dataclass
class PageDescriptor:
    page: int
    date: str = ""
    kind: str = "unknown"
    study_type: str = ""
    lab: str = ""
    text: str = ""
    needs_detail: bool = False
    confidence: float = 0.0
    inherited_date: bool = False
    ocr_dpi: int = 0


def key_text(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.casefold().replace("µ", "u").replace("μ", "u")
    value = re.sub(r"[^a-z0-9%/.-]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _iso_date(day: int, month: int, year: int) -> str:
    try:
        return datetime(year, month, day).date().isoformat()
    except ValueError:
        return ""


def detect_dates(text: str) -> list[str]:
    raw = text or ""
    found: list[str] = []
    for match in re.finditer(r"(?<!\d)(\d{1,2})\s*[/.-]\s*(\d{1,2})\s*[/.-]\s*(20\d{2})(?!\d)", raw):
        iso = _iso_date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        if iso and iso not in found:
            found.append(iso)

    normalized = key_text(raw)
    month_pattern = "|".join(sorted(MONTHS, key=len, reverse=True))
    pattern = rf"(?<!\d)(\d{{1,2}})\s*(?:/|de\s+)?\s*({month_pattern})\.?\s*(?:/|de\s+)?\s*(20\d{{2}})(?!\d)"
    for match in re.finditer(pattern, normalized, re.I):
        month_key = key_text(match.group(2))
        month = MONTHS.get(month_key) or MONTHS.get(month_key[:3])
        if month:
            iso = _iso_date(int(match.group(1)), int(month), int(match.group(3)))
            if iso and iso not in found:
                found.append(iso)
    return found


def detect_date(text: str) -> str:
    dates = detect_dates(text)
    if not dates:
        return ""
    # Report dates in these records are modern; a much older date is usually DOB.
    modern = [value for value in dates if int(value[:4]) >= 2000]
    return modern[0] if modern else dates[0]


def detect_lab(text: str) -> str:
    value = key_text(text)
    if "similab" in value or "analisis clinicos del dr simi" in value or "analisis clinicos dr simi" in value:
        return "SimiLab"
    if "chopo" in value or "grupo diagnostico medico proa" in value:
        return "Chopo"
    if "dna diagnostica" in value or "centro integral de diagnostico" in value:
        return "DNA Diagnóstica"
    if "imss" in value and ("laboratorio" in value or "hospital" in value):
        return "IMSS"
    return ""


def detect_study(text: str) -> tuple[str, str]:
    value = f" {key_text(text)} "
    if "electrocardiograma" in value or "electrocardiografia" in value or re.search(r"\becg\b", value):
        return "Electrocardiograma", "diagnostic"
    if "ultrasonido" in value or "ecografia" in value or "sonografia" in value:
        if "abdomen" in value or "abdominal" in value:
            return "Ultrasonido abdominal", "diagnostic"
        return "Ultrasonido", "diagnostic"
    for title, tokens in LAB_STUDIES:
        if any(token in value for token in tokens):
            return title, "laboratory"
    if (" resultado " in value or " resultados " in value) and (" referencia " in value or " val referencia " in value):
        return "Resultados de laboratorio", "laboratory"
    return "", "unknown"


def classify_page(page: int, text: str, *, dpi: int = 0) -> PageDescriptor:
    text = text or ""
    date = detect_date(text)
    lab = detect_lab(text)
    study, kind = detect_study(text)
    compact = len(re.sub(r"\s+", "", text))
    value = f" {key_text(text)} "
    lab_markers = sum(marker in value for marker in (
        " resultado ", " resultados ", " referencia ", " mg/dl ", " g/dl ", " mmol/l ",
        " biometria hematica ", " quimica sanguinea ", " examen general de orina ",
    ))
    if kind == "unknown" and lab_markers >= 2:
        kind = "laboratory"
        study = "Resultados de laboratorio"
    if kind == "unknown" and compact < 45:
        kind = "image"

    needs_detail = kind == "laboratory" or (
        kind == "unknown" and bool(lab) and bool(date) and compact >= 45
    )
    confidence = 0.25
    confidence += 0.25 if date else 0.0
    confidence += 0.15 if lab else 0.0
    confidence += 0.25 if study else 0.0
    confidence += 0.10 if compact >= 80 else 0.0
    return PageDescriptor(
        page=int(page), date=date, kind=kind, study_type=study, lab=lab,
        text=text, needs_detail=needs_detail, confidence=min(confidence, 0.95),
        ocr_dpi=int(dpi or 0),
    )


def repair_page_dates(pages: list[PageDescriptor]) -> list[dict[str, Any]]:
    repairs: list[dict[str, Any]] = []
    for index in range(1, len(pages) - 1):
        previous, current, following = pages[index - 1], pages[index], pages[index + 1]
        if not previous.date or previous.date != following.date or current.date == previous.date:
            continue
        compatible = (
            current.kind == previous.kind == following.kind
            or (current.study_type and current.study_type in {previous.study_type, following.study_type})
            or (current.lab and current.lab in {previous.lab, following.lab})
        )
        if compatible:
            old = current.date
            current.date = previous.date
            current.inherited_date = not bool(old)
            repairs.append({
                "page": current.page,
                "from": old,
                "to": current.date,
                "reason": "matching-neighbours",
            })
    return repairs


def segment_descriptors(pages: list[PageDescriptor]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for desc in pages:
        # Sparse image pages immediately after a diagnostic report belong to that
        # diagnostic episode unless the page exposes a new date/study of its own.
        if current and desc.kind == "image" and not desc.date and not desc.study_type and current["kind"] == "diagnostic":
            current["pages"].append(desc.page)
            current["page_end"] = desc.page
            continue

        date = desc.date
        if not date and current and desc.kind == current["kind"]:
            date = current.get("date", "")
        study = desc.study_type
        kind = desc.kind
        can_join = False
        if current:
            same_date = bool(date and current.get("date") and date == current["date"])
            same_study = bool(study and current.get("study_type") and study == current["study_type"])
            if same_date and same_study:
                can_join = True
            elif same_date and kind == current["kind"] == "laboratory" and not study:
                can_join = True
            elif same_date and kind == current["kind"] == "diagnostic" and same_study:
                can_join = True

        if can_join:
            current["pages"].append(desc.page)
            current["page_end"] = desc.page
            current["confidence"] = min(float(current["confidence"]), float(desc.confidence or current["confidence"]))
            if not current.get("lab") and desc.lab:
                current["lab"] = desc.lab
            continue

        if current:
            records.append(current)
        current = {
            "record_key": f"r{len(records) + 1:03d}",
            "date": date,
            "kind": kind,
            "study_type": study or ("Documento diagnóstico" if kind == "diagnostic" else "Resultados de laboratorio" if kind == "laboratory" else "Documento clínico"),
            "lab": desc.lab,
            "pages": [desc.page],
            "page_start": desc.page,
            "page_end": desc.page,
            "confidence": float(desc.confidence),
            "observations": [],
            "warnings": [],
        }
    if current:
        records.append(current)
    return records


def load_profile(base_dir: Path | None = None) -> dict[str, Any]:
    profile = dict(DEFAULT_PROFILE)
    path = (base_dir or Path(__file__).resolve().parent) / "ocr_profiles.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        profile.update(data.get("default") or {})
    except Exception:
        pass
    return profile


def should_use_multi_record(pdf_bytes: bytes) -> bool:
    if pymupdf is None:
        return False
    profile = load_profile()
    if not profile.get("enabled", True):
        return False
    try:
        with pymupdf.open(stream=pdf_bytes, filetype="pdf") as doc:
            if doc.page_count >= int(profile.get("multi_record_min_pages") or 8):
                return True
            dates: set[str] = set()
            for page in doc:
                dates.update(detect_dates(page.get_text("text", sort=True) or ""))
            return len(dates) >= 2
    except Exception:
        return False


def _find_tessdata() -> str | None:
    base = Path(__file__).resolve().parent
    candidates = [
        base / "ocr" / "tessdata",
        base / "tessdata",
        Path(os.environ.get("TESSDATA_PREFIX", "")),
        Path("/usr/share/tesseract-ocr/5/tessdata"),
        Path("/usr/share/tessdata"),
    ]
    for path in candidates:
        if str(path) and path.is_dir() and (path / "eng.traineddata").exists():
            return str(path)
    return None


def worker_task_main(task_file: str | Path, output_file: str | Path) -> int:
    if pymupdf is None:
        return 2
    task = json.loads(Path(task_file).read_text(encoding="utf-8"))
    out = Path(output_file)
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        with pymupdf.open(task["pdf_path"]) as doc, out.open("a", encoding="utf-8", buffering=1) as handle:
            for page_no in task["pages"]:
                try:
                    page = doc[int(page_no) - 1]
                    language = str(task.get("language") or "spa+eng")
                    try:
                        textpage = page.get_textpage_ocr(
                            language=language,
                            dpi=int(task.get("dpi") or 90),
                            full=True,
                            tessdata=task.get("tessdata") or None,
                        )
                    except Exception:
                        language = "eng"
                        textpage = page.get_textpage_ocr(
                            language=language,
                            dpi=int(task.get("dpi") or 90),
                            full=True,
                            tessdata=task.get("tessdata") or None,
                        )
                    payload = {
                        "ok": True,
                        "page": int(page_no),
                        "text": page.get_text("text", textpage=textpage, sort=True) or "",
                        "dpi": int(task.get("dpi") or 90),
                        "language": language,
                    }
                except Exception as exc:
                    payload = {"ok": False, "page": int(page_no), "error": f"{type(exc).__name__}: {exc}"}
                handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
                handle.flush()
        return 0
    except Exception as exc:
        out.write_text(json.dumps({"ok": False, "page": 0, "error": f"{type(exc).__name__}: {exc}"}) + "\n", encoding="utf-8")
        return 2


def _worker_command(task_file: Path, output_file: Path) -> list[str]:
    if getattr(sys, "frozen", False):
        return [sys.executable, "--ocr-worker", str(task_file), str(output_file)]
    helper = Path(__file__).resolve().with_name("multi_record_worker_cli.py")
    return [sys.executable, str(helper), str(task_file), str(output_file)]


def run_first_pass(pdf_path: Path, page_count: int) -> tuple[dict[int, str], list[str]]:
    profile = load_profile()
    tessdata = _find_tessdata()
    if not tessdata:
        return {}, ["Adaptive OCR first pass is unavailable because tessdata was not found."]
    pages = list(range(1, page_count + 1))
    batch_size = max(1, min(int(profile.get("batch_size") or 4), 4))
    batches = [pages[i:i + batch_size] for i in range(0, len(pages), batch_size)]
    results: dict[int, str] = {}
    warnings: list[str] = []
    timeout = float(profile.get("page_timeout_seconds") or 30)
    with tempfile.TemporaryDirectory(prefix="codecafe-ocr-") as temp_dir:
        root = Path(temp_dir)
        for index, batch in enumerate(batches, start=1):
            task_file = root / f"task-{index}.json"
            output_file = root / f"result-{index}.jsonl"
            task_file.write_text(json.dumps({
                "pdf_path": str(pdf_path),
                "pages": batch,
                "dpi": int(profile.get("first_pass_dpi") or 90),
                "language": str(profile.get("language") or "spa+eng"),
                "tessdata": tessdata,
            }, ensure_ascii=False), encoding="utf-8")
            process = subprocess.Popen(_worker_command(task_file, output_file), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            last_progress = time.monotonic()
            seen = 0
            done: set[int] = set()
            while process.poll() is None:
                if output_file.exists():
                    lines = output_file.read_text(encoding="utf-8", errors="replace").splitlines()
                    for line in lines[seen:]:
                        try:
                            item = json.loads(line)
                        except Exception:
                            continue
                        page_no = int(item.get("page") or 0)
                        if item.get("ok") and page_no:
                            results[page_no] = str(item.get("text") or "")
                            done.add(page_no)
                        elif page_no:
                            warnings.append(f"Page {page_no}: {item.get('error','OCR failed')}")
                    if len(lines) > seen:
                        last_progress = time.monotonic()
                        seen = len(lines)
                if time.monotonic() - last_progress > timeout:
                    process.kill()
                    warnings.extend(f"Page {page}: first-pass OCR timed out." for page in batch if page not in done)
                    break
                time.sleep(0.05)
            try:
                process.wait(timeout=2)
            except Exception:
                pass
            if output_file.exists():
                lines = output_file.read_text(encoding="utf-8", errors="replace").splitlines()
                for line in lines[seen:]:
                    try:
                        item = json.loads(line)
                    except Exception:
                        continue
                    page_no = int(item.get("page") or 0)
                    if item.get("ok") and page_no:
                        results[page_no] = str(item.get("text") or "")
    return results, list(dict.fromkeys(warnings))


def _subset_pdf(pdf_bytes: bytes, pages: list[int]) -> bytes:
    assert pymupdf is not None
    source = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    target = pymupdf.open()
    try:
        for page_no in pages:
            target.insert_pdf(source, from_page=int(page_no) - 1, to_page=int(page_no) - 1)
        return target.tobytes(garbage=4, deflate=True)
    finally:
        target.close()
        source.close()


def parse_multi_record_pdf(pdf_bytes: bytes, base_parser: Callable[[bytes], dict[str, Any]]) -> dict[str, Any]:
    if pymupdf is None:
        return base_parser(pdf_bytes)
    warnings: list[str] = []
    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as document:
        page_count = document.page_count
        native_text = {index + 1: (page.get_text("text", sort=True) or "") for index, page in enumerate(document)}

    with tempfile.TemporaryDirectory(prefix="codecafe-multirecord-") as temp_dir:
        pdf_path = Path(temp_dir) / "source.pdf"
        pdf_path.write_bytes(pdf_bytes)
        first_pass, first_warnings = run_first_pass(pdf_path, page_count)
        warnings.extend(first_warnings)

    descriptors: list[PageDescriptor] = []
    for page_no in range(1, page_count + 1):
        native = native_text.get(page_no, "")
        text = native if len(re.sub(r"\s+", "", native)) >= 80 else first_pass.get(page_no, native)
        descriptors.append(classify_page(page_no, text, dpi=90 if page_no in first_pass else 0))
    repairs = repair_page_dates(descriptors)
    for repair in repairs:
        warnings.append(
            f"Page {repair['page']}: date {repair.get('from') or 'missing'} was repaired to {repair['to']} from matching neighboring pages."
        )
    records = segment_descriptors(descriptors)

    observations: list[dict[str, Any]] = []
    for record in records:
        if record["kind"] != "laboratory":
            record["observation_count"] = 0
            continue
        try:
            parsed = base_parser(_subset_pdf(pdf_bytes, record["pages"]))
        except Exception as exc:
            record["warnings"].append(f"Detailed record parsing failed: {type(exc).__name__}: {exc}")
            record["observation_count"] = 0
            continue
        metadata = parsed.get("metadata") or {}
        if metadata.get("lab"):
            record["lab"] = metadata["lab"]
        if metadata.get("report_date") and not record.get("date"):
            record["date"] = metadata["report_date"]
        if metadata.get("study_type") and record.get("study_type") == "Resultados de laboratorio":
            record["study_type"] = metadata["study_type"]
        record_items: list[dict[str, Any]] = []
        for item in parsed.get("observations") or []:
            value = dict(item)
            local_page = int(value.get("source_page") or 1)
            if 1 <= local_page <= len(record["pages"]):
                value["source_page"] = record["pages"][local_page - 1]
            value["record_key"] = record["record_key"]
            value["record_date"] = record.get("date", "")
            value["record_page_start"] = record["page_start"]
            value["record_page_end"] = record["page_end"]
            value["lab"] = record.get("lab", "")
            value["study_type"] = record.get("study_type", "")
            record_items.append(value)
            observations.append(value)
        record["observations"] = record_items
        record["observation_count"] = len(record_items)
        record["warnings"].extend(parsed.get("warnings") or [])

    deduped: list[dict[str, Any]] = []
    seen: set[tuple[Any, ...]] = set()
    for item in observations:
        signature = (
            item.get("record_date"), key_text(str(item.get("study_type", ""))),
            key_text(str(item.get("test_name", ""))), key_text(str(item.get("value_text", ""))),
            str(item.get("value_numeric")), key_text(str(item.get("unit", ""))),
            key_text(str(item.get("reference_text", ""))),
        )
        if signature in seen:
            continue
        seen.add(signature)
        deduped.append(item)
    observations = deduped
    by_record: dict[str, list[dict[str, Any]]] = {}
    for item in observations:
        by_record.setdefault(str(item.get("record_key", "")), []).append(item)
    for record in records:
        record["observations"] = by_record.get(record["record_key"], [])
        record["observation_count"] = len(record["observations"])

    dates = sorted({record["date"] for record in records if record.get("date")}, reverse=True)
    labs = sorted({record["lab"] for record in records if record.get("lab")})
    patient_name = ""
    for record in records:
        for item in record.get("observations") or []:
            if item.get("patient_name"):
                patient_name = item["patient_name"]
                break
        if patient_name:
            break
    warnings.insert(0, f"Multi-record PDF: {len(records)} logical clinical record(s) detected across {page_count} pages.")
    metadata = {
        "lab": " / ".join(labs),
        "provider_legal": "",
        "branch": "",
        "address": "",
        "location": "",
        "registration_datetime": "",
        "report_date": dates[0] if dates else "",
        "patient_name": patient_name,
        "sex": "",
        "dob": "",
        "patient_external_id": "",
        "order_number": "",
        "directed_to": "",
        "study_type": f"Múltiples registros ({len(records)})",
        "specimen": "",
    }
    return {
        "ok": True,
        "engine": "adaptive-multi-record-ocr",
        "warnings": list(dict.fromkeys(warnings)),
        "metadata": metadata,
        "headings": [],
        "observations": observations,
        "records": records,
        "multi_record": True,
        "record_summary": {"record_count": len(records), "dates": dates, "labs": labs},
        "page_count": page_count,
        "confidence": round(min(0.90, 0.58 + (0.12 if dates else 0.0) + (0.12 if observations else 0.0)), 2),
        "page_descriptors": [asdict(page) for page in descriptors],
    }
