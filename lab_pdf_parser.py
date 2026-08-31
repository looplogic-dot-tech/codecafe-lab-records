from __future__ import annotations

import io
import os
import re
import sys
import unicodedata
from pathlib import Path
from dataclasses import dataclass
from typing import Any

from pypdf import PdfReader

try:
    import pymupdf
except Exception:  # optional at import time; setup installs it for OCR support
    pymupdf = None


UNIT_PATTERNS = (
    r"miles/µL", r"millones/µL", r"µg/dL", r"mg/dL", r"g/dL(?: \(%\))?",
    r"ng/mL", r"U/L", r"meq/L", r"mEq/L", r"mmol/L", r"µU/mL",
    r"mL/min/1\.73m2", r"fL", r"fl", r"pg", r"%", r"eri/uL", r"leu/uL",
    r"/campo", r"UFC/mL", r"CFU/mL", r"K/?[uµp]L", r"M/?[uµp]L", r"10\*?3/?[uµp]L", r"10\*?6/?[uµp]L",
)
UNIT_RE = re.compile(r"(?:" + "|".join(UNIT_PATTERNS) + r")$", re.I)
UNIT_ONLY_RE = re.compile(r"^(?:" + "|".join(UNIT_PATTERNS) + r")$", re.I)

FOOTER_PREFIXES = (
    "www.chopo.com.mx", "Gracias por su preferencia", "GRUPO DIAGNÓSTICO MÉDICO PROA",
    "SUCURSAL ", "AV CONSTITUYENTES", "MUNICIPIO ", "Descarga nuestra App",
)

BOILERPLATE_PREFIXES = (
    "Fuente:", "Límites de referencia", "Límites de Referencia", "De acuerdo con",
    "Evaluation and Management", "valores menores", "lo que para", "pruebas más específicas",
    "para apoyar al diagnóstico", "esta guía se sugieren", "Categorías de Tasa", "Estadio G",
    "Instituciones CDC/AHA", "Proteína C reactiva ultrasensible (mg/dL) Riesgo relativo",
    "AHA:", "CDC:", "Nota:", "La relación AST/ALT", "Favor de considerar",
    "Resultado verificado", "Para un mejor seguimiento", "fuera de valores normales",
    "monitoreo continuo", "para detectar", "hiperglicemias postprandiales", "llamado glucomap",
    "Observaciones", "Una prueba de hemoglobina positiva", "lisis celular",
)

NON_STUDY_HEADINGS = {
    "FUNCIÓN RENAL", "RIESGO CARDIOVASCULAR", "FUNCIONAMIENTO HEPÁTICO",
    "METABOLISMO DE HIERRO", "RESPUESTA INMUNOLÓGICA", "EXAMEN FÍSICO",
    "EXAMEN QUÍMICO", "EXAMEN MICROSCÓPICO", "EXAMEN FISICO", "EXAMEN FISICO-QUIMICO", "UREA",
}

OCR_STOP_MARKERS = (
    "recuerde un diagnostico", "todos los resultados fuera del rango", "atentamente",
    "responsable sanitario", "jefe de laboratorio", "nota estudio fuera del rango",
)
OCR_SKIP_MARKERS = (
    "liberacion", "libero", "estudio validado", "tecnica citometria", "ced prof",
    "domicilio", "horario de toma", "horario de entrega", "medico solicitante",
)

MONTHS_ES = {
    "ene": 1, "enero": 1, "feb": 2, "febrero": 2, "mar": 3, "marzo": 3,
    "abr": 4, "abril": 4, "may": 5, "mayo": 5, "jun": 6, "junio": 6,
    "jul": 7, "julio": 7, "ago": 8, "agosto": 8, "sep": 9, "sept": 9,
    "septiembre": 9, "oct": 10, "octubre": 10, "nov": 11, "noviembre": 11,
    "dic": 12, "diciembre": 12,
}


@dataclass
class ParsedValue:
    numeric: float | None
    text: str


@dataclass
class ExtractionBundle:
    layout_pages: list[str]
    plain_pages: list[str]
    ocr_pages: list[dict[str, Any]]
    engine: str
    warnings: list[str]


def clean_text(value: str) -> str:
    value = (value or "").replace("\u00a0", " ").replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", value).strip()


def key_text(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.casefold().replace("µ", "u").replace("μ", "u")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9#%]+", " ", value)).strip()


def normalize_heading(value: str) -> str:
    return clean_text(value).strip("_ ").strip()


def _useful_char_count(pages: list[str]) -> int:
    return sum(len(re.sub(r"\s+", "", p or "")) for p in pages)


def _pypdf_text_pages(pdf_bytes: bytes) -> tuple[list[str], list[str]]:
    reader = PdfReader(io.BytesIO(pdf_bytes), strict=False)
    layout_pages: list[str] = []
    plain_pages: list[str] = []
    for page in reader.pages:
        try:
            layout = page.extract_text(extraction_mode="layout") or ""
        except Exception:
            try:
                layout = page.extract_text() or ""
            except Exception:
                layout = ""
        try:
            plain = page.extract_text() or layout
        except Exception:
            plain = layout
        layout_pages.append(layout)
        plain_pages.append(plain)
    return layout_pages, plain_pages


def _reconstruct_layout_from_words(words: list[tuple[Any, ...]], page_width: float) -> str:
    """Build a deterministic, column-preserving text layout from positioned PDF words.

    pypdf's layout extraction can differ inside frozen macOS apps because font/layout
    resources are resolved differently. PyMuPDF gives us word coordinates, so we rebuild
    monospaced lines ourselves. This makes table parsing independent of the host OS.
    """
    if not words:
        return ""
    # Around 120-135 characters across a typical Letter/A4 clinical report is a good
    # compromise: enough horizontal resolution to preserve table columns without
    # creating huge gaps. Clamp to avoid pathological page sizes.
    target_columns = 128.0
    char_width = max(3.4, min(6.5, float(page_width or 612.0) / target_columns))

    ordered = sorted(words, key=lambda w: (((float(w[1]) + float(w[3])) / 2.0), float(w[0])))
    rows: list[list[Any]] = []
    y_tolerance = 3.8
    for word in ordered:
        cy = (float(word[1]) + float(word[3])) / 2.0
        if rows and abs(cy - float(rows[-1][0])) <= y_tolerance:
            rows[-1][1].append(word)
            rows[-1][0] = sum((float(x[1]) + float(x[3])) / 2.0 for x in rows[-1][1]) / len(rows[-1][1])
        else:
            rows.append([cy, [word]])

    lines: list[str] = []
    for _cy, row_words in rows:
        row_words = sorted(row_words, key=lambda w: float(w[0]))
        chunks: list[str] = []
        cursor = 0
        for word in row_words:
            text = clean_text(str(word[4]))
            if not text:
                continue
            col = max(0, int(round(float(word[0]) / char_width)))
            # Preserve at least one blank between ordinary words and at least two when
            # the PDF geometry shows a real table-column gap.
            spaces = max(1, col - cursor)
            chunks.append(" " * spaces + text)
            cursor = max(col + len(text), cursor + spaces + len(text))
        lines.append("".join(chunks).rstrip())
    return "\n".join(lines)


def _pymupdf_text_pages(pdf_bytes: bytes) -> tuple[list[str], list[str]]:
    if pymupdf is None:
        return [], []
    layout_pages: list[str] = []
    plain_pages: list[str] = []
    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page in doc:
            plain = page.get_text("text", sort=True) or ""
            words = page.get_text("words", sort=True) or []
            layout = _reconstruct_layout_from_words(words, float(page.rect.width)) or plain
            layout_pages.append(layout)
            plain_pages.append(plain or layout)
    return layout_pages, plain_pages


def embedded_text_pages(pdf_bytes: bytes) -> tuple[list[str], list[str], str, list[str]]:
    warnings: list[str] = []
    pypdf_layout: list[str] = []
    pypdf_plain: list[str] = []
    try:
        pypdf_layout, pypdf_plain = _pypdf_text_pages(pdf_bytes)
    except Exception as exc:
        warnings.append(f"pypdf embedded-text extraction failed; PyMuPDF fallback was used: {exc}")

    pymu_layout: list[str] = []
    pymu_plain: list[str] = []
    try:
        pymu_layout, pymu_plain = _pymupdf_text_pages(pdf_bytes)
    except Exception as exc:
        warnings.append(f"PyMuPDF native-text fallback failed: {exc}")

    pypdf_score = _useful_char_count(pypdf_plain)
    pymu_score = _useful_char_count(pymu_plain)

    # Preserve pypdf's layout-oriented output when it is usable because the Chopo
    # parser was validated against that spacing. If it is empty / badly degraded in
    # a frozen macOS build, PyMuPDF native extraction becomes a second independent
    # text engine instead of incorrectly falling through to OCR.
    if pypdf_score >= 60 or pypdf_score >= pymu_score * 0.65:
        return pypdf_layout, pypdf_plain, "pypdf-layout", warnings
    if pymu_score > pypdf_score:
        warnings.append("Embedded text was recovered with the PyMuPDF fallback engine.")
        return pymu_layout, pymu_plain, "pymupdf-native", warnings
    return pypdf_layout, pypdf_plain, "pypdf-layout", warnings


def _bundled_tessdata_dir() -> str | None:
    # PyInstaller exposes bundled data through sys._MEIPASS.  v0.6.5 ships
    # Spanish + English traineddata with the project and always bundles them into
    # the desktop application, so Finder-launched macOS apps do not depend on
    # Homebrew, PATH, or the original source folder.
    root = getattr(sys, "_MEIPASS", None)
    if root:
        for rel in (("tessdata",), ("ocr", "tessdata")):
            candidate = Path(root).joinpath(*rel)
            if (candidate / "eng.traineddata").exists():
                return str(candidate)
    return None


def _source_tessdata_dir() -> str | None:
    # Source/development runs use the same language data that will be bundled.
    candidate = Path(__file__).resolve().parent / "ocr" / "tessdata"
    if (candidate / "eng.traineddata").exists():
        return str(candidate)
    return None


def _find_tessdata_dir() -> str | None:
    bundled = _bundled_tessdata_dir()
    if bundled:
        return bundled
    env = os.environ.get("TESSDATA_PREFIX", "").strip()
    if env:
        candidate = Path(env).expanduser()
        if (candidate / "eng.traineddata").exists():
            return str(candidate)

    source = _source_tessdata_dir()
    if source:
        return source

    candidates = [
        Path("/opt/homebrew/share/tessdata"),
        Path("/usr/local/share/tessdata"),
        Path("/opt/homebrew/opt/tesseract/share/tessdata"),
        Path("/usr/local/opt/tesseract/share/tessdata"),
        Path("/usr/share/tesseract-ocr/5/tessdata"),
        Path("/usr/share/tesseract-ocr/4.00/tessdata"),
        Path("/usr/share/tessdata"),
    ]
    for candidate in candidates:
        if (candidate / "eng.traineddata").exists():
            return str(candidate)

    if pymupdf is not None:
        try:
            candidate = Path(pymupdf.get_tessdata())
            if (candidate / "eng.traineddata").exists():
                return str(candidate)
        except Exception:
            pass
    return None


def _ocr_language(tessdata: str | None = None) -> str:
    # Prefer Spanish + English when both traineddata files are present.
    if tessdata and not (Path(tessdata) / "spa.traineddata").exists():
        return "eng"
    return "spa+eng"


def ocr_status() -> dict[str, Any]:
    path = _find_tessdata_dir()
    base = Path(path) if path else None
    return {
        "available": bool(base and (base / "eng.traineddata").exists()),
        "tessdata": str(base) if base else "",
        "eng": bool(base and (base / "eng.traineddata").exists()),
        "spa": bool(base and (base / "spa.traineddata").exists()),
        "frozen": bool(getattr(sys, "frozen", False)),
    }


def ocr_document(pdf_bytes: bytes) -> tuple[list[dict[str, Any]], list[str]]:
    warnings: list[str] = []
    if pymupdf is None:
        return [], ["OCR is unavailable because PyMuPDF is not installed."]
    tessdata = _find_tessdata_dir()
    if not tessdata:
        return [], ["OCR is required for this scanned PDF, but Tesseract language data (tessdata) was not found. Run the platform OCR installer or rebuild the app with bundled OCR data."]
    pages: list[dict[str, Any]] = []
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    for page_no, page in enumerate(doc, start=1):
        textpage = None
        language_used = _ocr_language(tessdata)
        try:
            textpage = page.get_textpage_ocr(language=language_used, dpi=300, full=True, tessdata=tessdata)
        except Exception:
            language_used = "eng"
            try:
                textpage = page.get_textpage_ocr(language=language_used, dpi=300, full=True, tessdata=tessdata)
                warnings.append(f"Page {page_no}: Spanish OCR data was unavailable; English OCR fallback was used.")
            except Exception as exc:
                warnings.append(f"Page {page_no}: OCR failed: {exc}")
                continue
        text = page.get_text("text", textpage=textpage) or ""
        words = page.get_text("words", textpage=textpage) or []
        pages.append({
            "page": page_no,
            "text": text,
            "words": words,
            "width": float(page.rect.width),
            "height": float(page.rect.height),
            "language": language_used,
        })
    return pages, warnings


def extract_document(pdf_bytes: bytes) -> ExtractionBundle:
    layout_pages, plain_pages, native_engine, warnings = embedded_text_pages(pdf_bytes)
    useful_chars = _useful_char_count(plain_pages)
    page_count = max(1, len(plain_pages))
    # A page-sized clinical report with less than ~60 characters per page is effectively image-only.
    if useful_chars >= 60 * page_count:
        return ExtractionBundle(layout_pages, plain_pages, [], native_engine, warnings)
    warnings.append("No usable embedded text was found. Local OCR was used for this scanned PDF.")
    ocr_pages, ocr_warnings = ocr_document(pdf_bytes)
    warnings.extend(ocr_warnings)
    if ocr_pages:
        return ExtractionBundle(layout_pages, [p["text"] for p in ocr_pages], ocr_pages, "pymupdf-tesseract-ocr", warnings)
    return ExtractionBundle(layout_pages, plain_pages, [], native_engine, warnings)


def is_heading(line: str) -> bool:
    value = normalize_heading(line)
    if not value or len(value) > 100:
        return False
    if ":" in value and not value.upper().startswith("HOMA-IR"):
        return False
    if re.search(r"\s{2,}", line.strip()):
        return False
    letters = [c for c in value if c.isalpha()]
    if len(letters) < 5:
        return False
    uppercase_ratio = sum(c.isupper() for c in letters) / len(letters)
    return uppercase_ratio >= 0.72


def parse_number(value: str) -> float | None:
    value = clean_text(value).replace(",", ".")
    value = re.sub(r"(?<=\d)[Oo](?=\d|$)", "0", value)
    if value in {"o", "O"}:
        value = "0"
    value = value.rstrip(".")
    if not re.fullmatch(r"-?\d+(?:\.\d+)?", value):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def parse_reference(reference: str) -> tuple[float | None, float | None]:
    ref = clean_text(reference).replace(",", ".")
    ref = re.sub(r"(?<=\d)\s*[=E]\s*(?=\d)", " - ", ref, flags=re.I)
    m = re.search(r"(-?\d+(?:\.\d+)?)\s*-\s*(-?\d+(?:\.\d+)?)", ref)
    if m:
        return float(m.group(1)), float(m.group(2))
    m = re.search(r"([<>]=?)\s*=?\s*(-?\d+(?:\.\d+)?)", ref)
    if m:
        value = float(m.group(2))
        if m.group(1).startswith("<"):
            return None, value
        return value, None
    return None, None


def split_reference_and_unit(reference: str) -> tuple[str, str]:
    ref = clean_text(reference)
    m = UNIT_RE.search(ref)
    if not m:
        return ref, ""
    unit = m.group(0)
    return ref[: m.start()].strip(), unit


def parsed_value(raw: str) -> ParsedValue:
    raw = clean_text(raw)
    return ParsedValue(parse_number(raw), raw)


def _lines(text: str) -> list[str]:
    return [clean_text(x) for x in (text or "").splitlines() if clean_text(x)]


def _label_value(lines: list[str], labels: tuple[str, ...]) -> str:
    normalized_labels = tuple(key_text(x) for x in labels)
    for i, line in enumerate(lines):
        k = key_text(line)
        for label in normalized_labels:
            if k == label or k.startswith(label + " "):
                if ":" in line:
                    tail = clean_text(line.split(":", 1)[1])
                    if tail:
                        return tail
                # OCR frequently puts the value on the following line.
                if i + 1 < len(lines):
                    candidate = clean_text(lines[i + 1])
                    ck = key_text(candidate)
                    if candidate and not any(ck.startswith(x) for x in normalized_labels):
                        return candidate
    return ""


def _date_iso(raw: str) -> str:
    raw = clean_text(raw).replace(".", "").replace(" ", "")
    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", raw)
    if m:
        return f"{int(m.group(3)):04d}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
    m = re.search(r"(\d{1,2})/([A-Za-zÁÉÍÓÚáéíóú]{3,12})/(\d{4})", raw)
    if m:
        month_key = key_text(m.group(2))
        month = MONTHS_ES.get(month_key) or MONTHS_ES.get(month_key[:3])
        if month:
            return f"{int(m.group(3)):04d}-{month:02d}-{int(m.group(1)):02d}"
    return ""


def detect_lab(text: str) -> str:
    k = key_text(text)
    if "chopo com mx" in k or "grupo diagnostico medico proa" in k:
        return "Chopo"
    if "dna diagnostica" in k or "centro integral de diagnostico" in k:
        return "DNA Diagnóstica"
    if "similab" in k or "simi lab" in k or ("estimado medico" in k and "examen general de orina" in k and "unidad" in k):
        return "SimiLab"
    if ("imss" in k and "laboratorio clinico" in k) or ("hospital general de zona" in k and "laboratorio clinico" in k and "nss" in k):
        return "IMSS"
    return ""


def match_metadata(all_text: str) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "lab": detect_lab(all_text), "provider_legal": "", "branch": "", "address": "",
        "location": "", "registration_datetime": "", "report_date": "", "patient_name": "",
        "sex": "", "dob": "", "patient_external_id": "", "order_number": "", "directed_to": "",
    }
    lines = _lines(all_text)
    lab = metadata["lab"]

    # Chopo has a reliable embedded-text layout. Preserve the exact tested extraction
    # before running the looser cross-laboratory label heuristics.
    if lab == "Chopo":
        patterns = {
            "patient_external_id": r"ID Paciente:\s*(\d+)",
            "order_number": r"Orden:\s*(RH\d+)",
            "dob": r"Fecha de nacimiento:\s*(\d{2}/\d{2}/\d{4})",
            "directed_to": r"Dirigido a:\s*([^\n]+?)(?:\s{2,}|\n)",
        }
        for key, pattern in patterns.items():
            m = re.search(pattern, all_text, re.I)
            if m:
                metadata[key] = clean_text(m.group(1))
        m = re.search(r"Fecha de Registro:\s*(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2})", all_text, re.I)
        if m:
            metadata["registration_datetime"] = f"{m.group(1)} {m.group(2)}"
            metadata["report_date"] = _date_iso(m.group(1))
        m = re.search(r"Paciente:\s*([^\n]+?)\s{2,}Sexo:\s*(Masculino|Femenino|Male|Female)", all_text, re.I)
        if m:
            metadata["patient_name"] = clean_text(m.group(1))
            metadata["sex"] = clean_text(m.group(2))

    # Shared labels across laboratories.
    patient = _label_value(lines, ("Paciente", "Nombre"))
    if patient and not metadata["patient_name"]:
        metadata["patient_name"] = re.sub(r"\s+(Masculino|Femenino|Male|Female)$", "", patient, flags=re.I).strip()
    sex = _label_value(lines, ("Sexo",))
    if sex and not metadata["sex"]:
        metadata["sex"] = clean_text(sex.split()[0])
    directed = _label_value(lines, ("Dirigido a", "Doctor", "Médico", "Medico"))
    if directed and not metadata["directed_to"]:
        metadata["directed_to"] = directed

    date_raw = _label_value(lines, ("Fecha de Registro", "Fecha Registro", "Fecha de ingreso", "Fecha"))
    if date_raw and not metadata["report_date"]:
        metadata["report_date"] = _date_iso(date_raw)
        metadata["registration_datetime"] = date_raw

    order = _label_value(lines, ("Orden", "Solicitud", "Folio", "Código", "Codigo", "Cédigo", "Cedigo"))
    if order and not metadata["order_number"]:
        metadata["order_number"] = clean_text(order.split()[0])
    external = _label_value(lines, ("ID Paciente", "NSS", "Expediente"))
    if external and not metadata["patient_external_id"]:
        metadata["patient_external_id"] = clean_text(external.split()[0])

    if lab == "Chopo":
        metadata["provider_legal"] = "GRUPO DIAGNÓSTICO MÉDICO PROA S.A. DE C.V."
        m = re.search(r"SUCURSAL\s+([^\n]+)", all_text, re.I)
        metadata["branch"] = clean_text(m.group(1)) if m else ""
        m = re.search(r"\n\s*(AV [^\n]+)\n\s*MUNICIPIO", all_text, re.I)
        if m:
            metadata["address"] = clean_text(m.group(1))
        m = re.search(r"\n\s*(MUNICIPIO [^\n]+)", all_text, re.I)
        if m:
            metadata["location"] = clean_text(m.group(1))
        # DOB already captured by the strict Chopo regex above.
    elif lab == "DNA Diagnóstica":
        metadata["provider_legal"] = "DNA Diagnóstica - Centro Integral de Diagnóstico"
        metadata["branch"] = "Matriz" if "matriz" in key_text(all_text) else ""
        metadata["location"] = "Torreón / Gómez Palacio" if "torreon" in key_text(all_text) else ""
    elif lab == "SimiLab":
        metadata["provider_legal"] = "SimiLab"
        metadata["branch"] = _label_value(lines, ("Unidad",))
        if "quintana roo" in key_text(all_text):
            metadata["location"] = "Solidaridad, Quintana Roo"
    elif lab == "IMSS":
        metadata["provider_legal"] = "IMSS"
        hospital = next((x for x in lines if "HOSPITAL GENERAL" in x.upper()), "")
        metadata["branch"] = hospital
        if "torreon" in key_text(all_text):
            metadata["location"] = "Torreón, Coahuila"

    # Chopo embedded-text layout has patient and sex on the same extracted line.
    if not metadata["patient_name"]:
        m = re.search(r"Paciente:\s*([^\n]+?)\s{2,}Sexo:\s*(Masculino|Femenino|Male|Female)", all_text, re.I)
        if m:
            metadata["patient_name"] = clean_text(m.group(1))
            metadata["sex"] = clean_text(m.group(2))
    return metadata


def parse_result_row(line: str, next_line: str = "") -> tuple[dict[str, Any] | None, bool]:
    columns = [clean_text(part) for part in re.split(r"\s{2,}", line.strip()) if clean_text(part)]
    if len(columns) < 2:
        return None, False
    name, value_raw = columns[0], columns[1]
    # Microbiology/culture reports often have no numeric reference column.  A valid
    # result may therefore be only two columns, for example:
    #     CULTIVO    Sin desarrollo microbiano
    # Do not generalize this to every two-column line: require a microbiology label
    # and a plausible culture result so headings/narrative text are not imported.
    if len(columns) == 2:
        if not (_looks_microbiology_label(name) and _looks_microbiology_result(value_raw)):
            return None, False
        value = parsed_value(value_raw)
        return ({
            "test_name": _canonical_microbiology_label(name),
            "raw_test_name": name,
            "value_numeric": value.numeric,
            "value_text": value.text,
            "unit": "",
            "reference_low": None,
            "reference_high": None,
            "reference_text": "",
        }, False)
    if not name or any(name.startswith(prefix) for prefix in BOILERPLATE_PREFIXES):
        return None, False
    # A table row must contain either a numeric laboratory value or a known
    # qualitative result. This prevents section headings / reference narratives from
    # becoming false observations when a positional PDF engine creates extra columns.
    if UNIT_ONLY_RE.fullmatch(value_raw):
        return None, False
    value = parsed_value(value_raw)
    if value.numeric is None:
        if len(value.text) > 40 or not _looks_qualitative_result(value.text):
            return None, False

    tail = columns[2:]
    unit = ""
    reference_text = ""
    # Laboratories / extraction engines may emit either:
    #   test | value | reference | unit
    # or
    #   test | value | unit | reference
    # Handle both deterministically.
    if tail and UNIT_ONLY_RE.fullmatch(tail[0]):
        unit = tail[0]
        reference_text = " ".join(tail[1:]).strip()
    elif tail and UNIT_ONLY_RE.fullmatch(tail[-1]):
        unit = tail[-1]
        reference_text = " ".join(tail[:-1]).strip()
    else:
        reference_text, unit = split_reference_and_unit(" ".join(tail))

    consumed_next = False
    if not unit and next_line and UNIT_ONLY_RE.fullmatch(clean_text(next_line)):
        unit = clean_text(next_line)
        consumed_next = True
    low, high = parse_reference(reference_text)
    return ({
        "test_name": name, "raw_test_name": name, "value_numeric": value.numeric,
        "value_text": value.text, "unit": unit, "reference_low": low,
        "reference_high": high, "reference_text": reference_text,
    }, consumed_next)


def infer_specimens(headings: list[str], explicit_samples: list[str]) -> str:
    specimens: list[str] = []
    def add(value: str) -> None:
        value = clean_text(value)
        if value and value.casefold() not in {x.casefold() for x in specimens}:
            specimens.append(value)
    for sample in explicit_samples:
        add(sample.title())
    for heading in headings:
        upper = heading.upper()
        if "ORINA" in upper or "UROCULTIVO" in upper or "URINE CULTURE" in upper:
            add("Orina")
        if "SUERO" in upper:
            add("Suero")
        if any(token in upper for token in ("BIOMETRÍA HEMÁTICA", "BIOMETRIA HEMATICA", "HEMATOLOGÍA", "HEMATOLOGIA")):
            add("Sangre")
        if "QUÍMICA CLÍNICA" in upper or "QUIMICA CLINICA" in upper:
            add("Sangre")
    return " / ".join(specimens)


def summarize_study(headings: list[str]) -> str:
    candidates = [h for h in headings if h.upper() not in NON_STUDY_HEADINGS]
    if not candidates:
        return ""
    if len(candidates) <= 3:
        return " + ".join(candidates)
    return " + ".join(candidates[:3]) + f" + {len(candidates) - 3} más"


def parse_layout_rows(layout_pages: list[str]) -> tuple[list[str], list[dict[str, Any]], list[str]]:
    headings: list[str] = []
    observations: list[dict[str, Any]] = []
    explicit_samples: list[str] = []
    current_panel = ""
    in_results = False
    current_panel_start = 0
    for page_number, page_text in enumerate(layout_pages, start=1):
        raw_lines = page_text.splitlines()
        index = 0
        while index < len(raw_lines):
            raw_line = raw_lines[index]
            line = clean_text(raw_line)
            if not line:
                index += 1; continue
            header_window = clean_text(" ".join(raw_lines[index:index + 3]))
            header_key = key_text(header_window)
            # Do not require the PDF engine to keep the complete column header on one
            # physical line. Frozen macOS builds may split it across adjacent lines.
            if (
                key_text(line).startswith("prueba")
                and (
                    "limites de referencia" in header_key
                    or all(token in header_key for token in ("bajo", "dentro", "sobre"))
                    or ("resultado" in header_key and "referencia" in header_key)
                )
            ):
                in_results = True; index += 1; continue
            if any(line.startswith(prefix) for prefix in FOOTER_PREFIXES):
                in_results = False; index += 1; continue
            if not in_results:
                index += 1; continue
            if line.startswith("Método:"):
                method = clean_text(line.split(":", 1)[1])
                for obs in observations[current_panel_start:]:
                    if not obs.get("method"):
                        obs["method"] = method
                index += 1; continue
            columns = [clean_text(part) for part in re.split(r"\s{2,}", raw_line.strip()) if clean_text(part)]
            if len(columns) == 2 and columns[0].casefold() == "muestra":
                explicit_samples.append(columns[1]); index += 1; continue
            heading_candidate = ""
            if len(columns) == 2 and normalize_heading(columns[1]) == "" and is_heading(columns[0]):
                heading_candidate = normalize_heading(columns[0])
            elif is_heading(raw_line):
                heading_candidate = normalize_heading(line)
            if heading_candidate:
                if heading_candidate not in headings:
                    headings.append(heading_candidate)
                current_panel = heading_candidate
                current_panel_start = len(observations)
                index += 1; continue
            line_key = key_text(line)
            # Skip continuation fragments of the result-table header. Some PDF engines
            # split "Prueba / Bajo / Dentro / Sobre / Límites de referencia" across
            # multiple physical lines. These are column labels, never observations.
            if (
                ("limites de referencia" in line_key and any(x in line_key for x in ("bajo", "dentro", "sobre")))
                or all(x in line_key for x in ("bajo", "dentro", "sobre"))
            ):
                index += 1; continue
            if any(line.startswith(prefix) for prefix in BOILERPLATE_PREFIXES) or set(line) == {"="}:
                index += 1; continue
            next_line = clean_text(raw_lines[index + 1]) if index + 1 < len(raw_lines) else ""
            result, consumed_next = parse_result_row(raw_line, next_line)
            if result:
                result.update({"panel": current_panel, "method": "", "source_page": page_number,
                               "extraction_confidence": 0.97, "auto_extracted": 1, "notes": ""})
                observations.append(result)
                if consumed_next:
                    index += 1
            index += 1
    return headings, observations, explicit_samples


def _group_words(words: list[tuple[Any, ...]], y_tolerance: float = 3.6) -> list[tuple[float, list[tuple[Any, ...]]]]:
    ordered = sorted(words, key=lambda w: (((float(w[1]) + float(w[3])) / 2), float(w[0])))
    rows: list[list[Any]] = []
    for word in ordered:
        cy = (float(word[1]) + float(word[3])) / 2
        if rows and abs(cy - float(rows[-1][0])) <= y_tolerance:
            rows[-1][1].append(word)
            rows[-1][0] = sum((float(w[1]) + float(w[3])) / 2 for w in rows[-1][1]) / len(rows[-1][1])
        else:
            rows.append([cy, [word]])
    return [(float(cy), sorted(ws, key=lambda w: float(w[0]))) for cy, ws in rows]


def _find_ocr_header(rows: list[tuple[float, list[tuple[Any, ...]]]]) -> tuple[int | None, dict[str, float] | None]:
    for index, (_y, words) in enumerate(rows):
        joined = " ".join(key_text(str(w[4])) for w in words)
        if not (("resultado" in joined or "resultados" in joined) and "referencia" in joined):
            continue
        cols: dict[str, float] = {}
        for word in words:
            token = key_text(str(word[4]))
            x = float(word[0])
            if token in {"prueba", "estudios", "estudio"} and "name" not in cols:
                cols["name"] = x
            if token.startswith("resultado") and "result" not in cols:
                cols["result"] = x
            if token.startswith("unidad") and "unit" not in cols:
                cols["unit"] = x
        if "result" not in cols:
            continue
        ref_words = [w for w in words if key_text(str(w[4])) in {"val", "valores", "referencia"} and float(w[0]) > cols["result"] + 35]
        if ref_words:
            cols["ref"] = min(float(w[0]) for w in ref_words)
        if "ref" in cols:
            return index, cols
    return None, None


def _ocr_cells(words: list[tuple[Any, ...]], cols: dict[str, float]) -> tuple[str, str, str, str]:
    result_x, ref_x = cols["result"], cols["ref"]
    unit_x = cols.get("unit")
    name_words: list[str] = []
    result_words: list[str] = []
    unit_words: list[str] = []
    ref_words: list[str] = []
    if unit_x is not None:
        result_unit_boundary = (result_x + unit_x) / 2
        unit_ref_boundary = (unit_x + ref_x) / 2
    else:
        result_ref_boundary = (result_x + ref_x) / 2
    for word in words:
        cx = (float(word[0]) + float(word[2])) / 2
        token = str(word[4])
        if cx < result_x - 12:
            name_words.append(token)
        elif unit_x is not None and cx < result_unit_boundary:
            result_words.append(token)
        elif unit_x is not None and cx < unit_ref_boundary:
            unit_words.append(token)
        elif unit_x is None and cx < result_ref_boundary:
            result_words.append(token)
        else:
            ref_words.append(token)
    return tuple(clean_text(" ".join(x)) for x in (name_words, result_words, unit_words, ref_words))


def _strip_ocr_flags(value: str) -> str:
    value = re.sub(r"(^|\s)[*xX](?=\s|$)", " ", value or "")
    return clean_text(value).strip("* ")


def _extract_value_and_unit(value_cell: str, unit_cell: str) -> tuple[str, str]:
    value_cell = _strip_ocr_flags(value_cell)
    unit_cell = _strip_ocr_flags(unit_cell)
    if re.fullmatch(r"-?\d+(?:[.,]\d+)?\s*\+", value_cell):
        value_cell = clean_text(value_cell[:-1])
    if unit_cell:
        return value_cell, unit_cell
    # Some layouts (SimiLab) place a unit in the same visual column as the value.
    m = re.search(r"\s+(mg/dL|g/dL|ng/mL|mmol/L|U/L|fL|fl|pg|%|K/?[uµp]L|M/?[uµp]L|10\*?3/?[uµp]L|10\*?6/?[uµp]L)\s*$", value_cell, re.I)
    if m:
        return clean_text(value_cell[:m.start()]), clean_text(m.group(1))
    return value_cell, ""


def _ocr_heading(full_line: str) -> str:
    line = clean_text(full_line).strip("_ ")
    if re.search(r"\d", line):
        return ""
    k = key_text(line)
    known = (
        "hematologia", "biometria hematica", "quimica clinica", "examen general de orina",
        "examen fisico", "examen fisico quimico", "examen microscopico", "urea",
    )
    if any(k == x or k.startswith(x + " ") for x in known):
        return line
    return ""


def _looks_qualitative_result(value: str) -> bool:
    k = key_text(value)
    if not k:
        return False
    common = (
        "negativo", "positivo", "ausente", "ausentes", "presente", "presentes",
        "no se observa", "no se observan", "no observado", "no observados",
        "escaso", "escasa", "escasos", "escasas", "claro", "transparente", "turbio",
        "lig turbio", "amarillo", "amarilla", "reactivo", "no reactivo", "trazas",
        "normal", "anormal", "detectado", "no detectado",
    )
    return any(k == item or k.startswith(item + " ") for item in common)




MICROBIOLOGY_PANEL_TOKENS = (
    "urocultivo", "cultivo de orina", "urine culture", "hemocultivo", "coprocultivo",
    "cultivo bacteriologico", "cultivo bacteriológico", "microbiologia", "microbiología",
)

MICROBIOLOGY_LABEL_MAP = {
    "cultivo": "Cultivo",
    "resultado": "Resultado del cultivo",
    "resultado del cultivo": "Resultado del cultivo",
    "desarrollo": "Desarrollo microbiológico",
    "desarrollo microbiologico": "Desarrollo microbiológico",
    "aislamiento": "Microorganismo",
    "microorganismo": "Microorganismo",
    "germen": "Microorganismo",
    "germen aislado": "Microorganismo",
    "recuento": "Recuento microbiológico",
    "recuento bacteriano": "Recuento microbiológico",
    "cuenta de colonias": "Recuento microbiológico",
}


def _looks_microbiology_panel(value: str) -> bool:
    k = key_text(value)
    if not k or k.startswith(("metodo ", "tecnica ", "responsable ", "observacion ", "nota ")):
        return False
    return any(token in k for token in (key_text(x) for x in MICROBIOLOGY_PANEL_TOKENS))


def _looks_microbiology_label(value: str) -> bool:
    k = key_text(value)
    return k in MICROBIOLOGY_LABEL_MAP or k in {"urocultivo", "cultivo bacteriologico", "cultivo bacteriológico"}


def _canonical_microbiology_label(value: str) -> str:
    k = key_text(value)
    if k in {"urocultivo", "cultivo bacteriologico", "cultivo bacteriológico"}:
        return "Cultivo"
    return MICROBIOLOGY_LABEL_MAP.get(k, clean_text(value))


def _looks_microbiology_result(value: str) -> bool:
    text = clean_text(value)
    k = key_text(text)
    if not k or len(text) > 120:
        return False
    exact_or_prefix = (
        "sin desarrollo microbiano", "sin desarrollo bacteriano", "sin desarrollo",
        "sin crecimiento", "no hubo crecimiento", "no hubo desarrollo",
        "no se observa crecimiento", "no se observa desarrollo",
        "no se observo crecimiento", "no se observo desarrollo",
        "no se aislo", "no se aislaron", "no se identifica", "no se identifican",
        "desarrollo de", "crecimiento de", "se aislo", "se aislaron", "aislamiento de",
        "negativo", "positivo", "flora habitual", "flora mixta",
    )
    if any(k == item or k.startswith(item + " ") for item in exact_or_prefix):
        return True
    # Colony counts are often the only value in culture reports and may include
    # UFC/mL / CFU/mL without a reference range.
    if re.search(r"\d", text) and re.search(r"\b(?:UFC|CFU)\s*/?\s*mL\b", text, re.I):
        return True
    return False


def _microbiology_value_for_label(label: str, candidate: str) -> bool:
    label_key = key_text(label)
    candidate = clean_text(candidate)
    if not candidate or len(candidate) > 120:
        return False
    if _looks_microbiology_result(candidate):
        return True
    # Organism / isolate fields may legitimately contain a species name rather than
    # one of the standard positive/negative phrases.  Accept a short non-narrative
    # value only when the PDF explicitly labels the field as organism/isolate.
    if label_key in {"microorganismo", "germen", "germen aislado", "aislamiento"}:
        k = key_text(candidate)
        if 2 <= len(candidate) <= 80 and not any(x in k for x in (
            "metodo", "responsable", "fecha", "paciente", "dirigido", "pagina", "limites de referencia"
        )):
            return True
    if label_key in {"recuento", "recuento bacteriano", "cuenta de colonias"} and re.search(r"\d", candidate):
        return True
    return False


def _split_microbiology_value_unit(value: str) -> tuple[str, str]:
    text = clean_text(value)
    m = re.search(r"\s*((?:UFC|CFU)\s*/?\s*mL)\s*$", text, re.I)
    if not m:
        return text, ""
    unit = clean_text(m.group(1)).replace(" ", "")
    return clean_text(text[:m.start()]), unit


def _is_microbiology_layout_noise(value: str) -> bool:
    """Return True for table-layout fragments that may sit between a culture label and value.

    Positional PDF extraction can serialize one visual row vertically, e.g.::

        CULTIVO
        ---
        Sin
        desarrollo
        microbiano

    Column labels and placeholder dashes are layout noise, not clinical data.
    """
    text = clean_text(value)
    k = key_text(text)
    if not text:
        return True
    if re.fullmatch(r"[-_=–—.·•*]+", text):
        return True
    noise = {
        "prueba", "resultado", "resultados", "unidad", "unidades", "referencia",
        "val referencia", "valor de referencia", "valores de referencia",
        "bajo lr", "dentro lr", "sobre lr", "limites de referencia",
    }
    return k in noise


def _is_microbiology_boundary(value: str) -> bool:
    """Stop multiline-value recovery before metadata, methods, or a new field."""
    text = clean_text(value)
    if not text:
        return False
    k = key_text(text)
    if _looks_microbiology_label(text) or _looks_microbiology_panel(text):
        return True
    prefixes = (
        "metodo", "tecnica", "nota", "observacion", "responsable", "validado",
        "fecha", "paciente", "dirigido", "orden", "folio", "pagina", "hoja",
        "aislamiento", "microorganismo", "germen", "recuento", "cuenta de colonias",
    )
    return any(k == x or k.startswith(x + " ") for x in prefixes)


def _microbiology_lookahead_value(
    raw_lines: list[str], start_index: int, label: str, *, max_physical_lines: int = 7
) -> tuple[str, int]:
    """Recover a culture value that the PDF engine split over several physical lines.

    Returns ``(value, last_consumed_index)``. The longest plausible value is preferred,
    while harmless table placeholders are skipped. Missing/ambiguous content is never
    invented.
    """
    fragments: list[str] = []
    best = ""
    best_end = start_index - 1
    limit = min(len(raw_lines), start_index + max_physical_lines)
    for j in range(start_index, limit):
        piece = clean_text(raw_lines[j])
        if not piece:
            continue
        if _is_microbiology_layout_noise(piece):
            continue
        if _is_microbiology_boundary(piece):
            # In phrases such as "Sin / desarrollo / microbiano", the word
            # "desarrollo" is simultaneously a possible field label and part of the
            # actual value. Allow it only when a value phrase is already being built.
            if not (fragments and key_text(piece) in {"desarrollo", "crecimiento"}):
                break
        # Avoid swallowing long narrative paragraphs as a result.
        if len(piece) > 100:
            break
        fragments.append(piece)
        candidate = clean_text(" ".join(fragments))
        if len(candidate) > 120:
            break
        if _microbiology_value_for_label(label, candidate):
            best, best_end = candidate, j
    return best, best_end


def _microbiology_unlabelled_lookahead(
    raw_lines: list[str], start_index: int, *, max_physical_lines: int = 5
) -> tuple[str, int]:
    """Recover an unlabelled qualitative culture phrase under a known culture panel."""
    fragments: list[str] = []
    best = ""
    best_end = start_index - 1
    limit = min(len(raw_lines), start_index + max_physical_lines)
    for j in range(start_index, limit):
        piece = clean_text(raw_lines[j])
        if not piece:
            continue
        if _is_microbiology_layout_noise(piece):
            continue
        if j > start_index and _is_microbiology_boundary(piece):
            if not (fragments and key_text(piece) in {"desarrollo", "crecimiento"}):
                break
        if len(piece) > 100:
            break
        fragments.append(piece)
        candidate = clean_text(" ".join(fragments))
        if len(candidate) > 120:
            break
        if _looks_microbiology_result(candidate):
            best, best_end = candidate, j
    return best, best_end


def parse_microbiology_qualitative_rows(
    pages: list[str], *, ocr: bool = False
) -> tuple[list[str], list[dict[str, Any]]]:
    """Recover culture/microbiology observations that do not have reference columns.

    Culture reports vary widely and may serialize one visual result across several text
    lines.  This parser is intentionally context driven: it requires a microbiology panel
    or explicit microbiology field label and never invents missing organisms/results.
    """
    headings: list[str] = []
    observations: list[dict[str, Any]] = []
    current_panel = ""
    confidence = 0.82 if ocr else 0.96

    for page_number, page_text in enumerate(pages, start=1):
        raw_lines = (page_text or "").splitlines()
        i = 0
        while i < len(raw_lines):
            raw = raw_lines[i]
            line = clean_text(raw)
            if not line:
                i += 1
                continue

            # Remember a microbiology study/panel heading. Do not turn the heading
            # itself into a result unless it is explicitly paired with a value.
            if _looks_microbiology_panel(line) and len(line) <= 120:
                current_panel = normalize_heading(line)
                if current_panel and current_panel not in headings:
                    headings.append(current_panel)

            columns = [clean_text(part) for part in re.split(r"\s{2,}", raw.strip()) if clean_text(part)]
            label = ""
            candidate = ""
            consumed_until = i

            if len(columns) >= 2 and _looks_microbiology_label(columns[0]):
                label, candidate = columns[0], columns[1]
                # A positional engine may create more than two value fragments in the
                # same row. Preserve them when they form a plausible microbiology value.
                if len(columns) > 2:
                    joined = clean_text(" ".join(columns[1:]))
                    if _microbiology_value_for_label(label, joined):
                        candidate = joined
            else:
                # Single-space / OCR form: ``CULTIVO Sin desarrollo microbiano``.
                m = re.match(
                    r"^(CULTIVO|RESULTADO(?:\s+DEL\s+CULTIVO)?|DESARROLLO|AISLAMIENTO|MICROORGANISMO|GERMEN(?:\s+AISLADO)?|RECUENTO(?:\s+BACTERIANO)?|CUENTA\s+DE\s+COLONIAS)\s*[:\-]?\s+(.+)$",
                    line, re.I,
                )
                if m:
                    label, candidate = clean_text(m.group(1)), clean_text(m.group(2))

            # Vertically split form. Search several lines because macOS/PDF layout
            # extraction may emit "Sin / desarrollo / microbiano" on separate lines,
            # with a placeholder dash between the label and the value.
            if not candidate and _looks_microbiology_label(line):
                looked, end_index = _microbiology_lookahead_value(raw_lines, i + 1, line)
                if looked:
                    label, candidate = line, looked
                    consumed_until = max(consumed_until, end_index)

            # Some reports print only the qualitative phrase below a culture panel and
            # no explicit result label. Recover split phrases in that case as well.
            if not candidate and current_panel:
                looked, end_index = _microbiology_unlabelled_lookahead(raw_lines, i)
                if looked:
                    label, candidate = "Cultivo", looked
                    consumed_until = max(consumed_until, end_index)

            if label and candidate and _microbiology_value_for_label(label, candidate):
                value_text, unit = _split_microbiology_value_unit(candidate)
                numeric = parse_number(value_text)
                obs = {
                    "test_name": _canonical_microbiology_label(label),
                    "raw_test_name": clean_text(label),
                    "value_numeric": numeric,
                    "value_text": value_text,
                    "unit": unit,
                    "reference_low": None,
                    "reference_high": None,
                    "reference_text": "",
                    "panel": current_panel or "Microbiología / Cultivo",
                    "method": "",
                    "source_page": page_number,
                    "extraction_confidence": confidence,
                    "auto_extracted": 1,
                    "notes": (
                        "OCR microbiology import: verify the qualitative result against the source PDF before confirming."
                        if ocr else
                        "Qualitative microbiology result extracted from the source report."
                    ),
                }
                # Local de-duplication without relying on dictionary normalization.
                if not any(
                    x["source_page"] == obs["source_page"]
                    and key_text(x["test_name"]) == key_text(obs["test_name"])
                    and key_text(x["value_text"]) == key_text(obs["value_text"])
                    and clean_text(x.get("unit", "")) == unit
                    for x in observations
                ):
                    observations.append(obs)
            i = max(i + 1, consumed_until + 1)
    return headings, observations

def _clean_ocr_test_name(name: str, unit: str) -> str:
    """Remove small OCR artifacts from common differential names without guessing values."""
    cleaned = clean_text(name)
    k = key_text(cleaned)
    cells = (
        ("neutrofil", "Neutrófilos"),
        ("linfocit", "Linfocitos"),
        ("monocit", "Monocitos"),
        ("eosinofil", "Eosinófilos"),
        ("basofil", "Basófilos"),
    )
    unit_key = key_text(unit)
    for stem, label in cells:
        if k.startswith(stem):
            if "absolut" in k:
                return f"{label} absolutos"
            if unit_key == "" or unit_key == "%" or "%" in unit:
                # Percentage rows are frequently OCR'd with a stray trailing letter/symbol.
                return f"{label} %"
    return cleaned


def parse_ocr_rows(ocr_pages: list[dict[str, Any]]) -> tuple[list[str], list[dict[str, Any]], list[str], list[str]]:
    headings: list[str] = []
    observations: list[dict[str, Any]] = []
    explicit_samples: list[str] = []
    warnings: list[str] = []
    last_cols: dict[str, float] | None = None
    current_panel = ""

    for page in ocr_pages:
        rows = _group_words(page.get("words", []))
        header_index, cols = _find_ocr_header(rows)
        if cols is not None:
            last_cols = cols
        elif last_cols is not None:
            cols = last_cols
            header_index = -1
        else:
            warnings.append(f"Page {page['page']}: OCR found text but could not identify result/reference columns.")
            continue

        page_text_lines = _lines(page.get("text", ""))
        for line in page_text_lines:
            heading = _ocr_heading(line)
            if heading and heading not in headings:
                headings.append(heading)
        start = (header_index or 0) + 1 if header_index is not None else 0
        for _y, words in rows[start:]:
            full_line = clean_text(" ".join(str(w[4]) for w in words))
            fk = key_text(full_line)
            if any(marker in fk for marker in OCR_STOP_MARKERS):
                break
            if any(marker in fk for marker in OCR_SKIP_MARKERS):
                continue

            heading = _ocr_heading(full_line)
            if heading:
                current_panel = heading
                if heading not in headings:
                    headings.append(heading)
                continue

            name, result_cell, unit_cell, reference_cell = _ocr_cells(words, cols)
            raw_name = _strip_ocr_flags(name)
            had_absolute_marker = clean_text(raw_name).endswith(("#", "+"))
            name = clean_text(raw_name.rstrip("#+ ")) + (" #" if had_absolute_marker else "")
            result_cell, unit_cell = _extract_value_and_unit(result_cell, unit_cell)
            # OCR often reads the laboratory's abnormal-result asterisk as + or - next to the unit.
            unit_cell = clean_text(re.sub(r"(^|\s)[+*-](?=\s|$)", " ", unit_cell))
            name = _clean_ocr_test_name(name, unit_cell)
            reference_cell = clean_text(reference_cell)

            # Lines fully left of the result column are usually section headings.
            if name and not result_cell and not unit_cell and not reference_cell:
                heading = _ocr_heading(name)
                if heading:
                    current_panel = heading
                    if heading not in headings:
                        headings.append(heading)
                continue
            if not name or not result_cell or not reference_cell:
                continue
            if len(name) > 85 or len(result_cell) > 45 or len(reference_cell) > 80:
                continue
            # Narrative interpretation lines can align under the same visual columns. Only keep
            # non-numeric rows when they resemble legitimate qualitative laboratory values.
            preliminary_numeric = parse_number(result_cell)
            if preliminary_numeric is None and not _looks_qualitative_result(result_cell):
                if not re.search(r"\d", result_cell):
                    continue

            value = parsed_value(result_cell)
            ref_text = reference_cell.strip(" ,")
            low, high = parse_reference(ref_text)
            confidence = 0.86
            notes = "OCR import: verify against the source PDF before confirming the report."
            reported_abnormal = "*" in full_line
            # A printed abnormal marker is useful as an OCR consistency check. If OCR turns an
            # abnormal value into a plausible in-range number (e.g. 15 -> 45), do not silently trust it.
            if reported_abnormal and value.numeric is not None and (low is not None or high is not None):
                appears_inside = (low is None or value.numeric >= low) and (high is None or value.numeric <= high)
                if appears_inside:
                    confidence = min(confidence, 0.60)
                    notes += " Laboratory marked this row abnormal, but the OCR value appears inside the parsed reference range; verify this value carefully."
                else:
                    notes += " Laboratory marked this row abnormal."
            # OCR-like symbols in numeric fields indicate uncertainty; preserve the text instead of guessing.
            if value.numeric is None and re.search(r"[£{}]|[A-Za-z]{1,3}:$", result_cell):
                confidence = 0.68
            if re.search(r"\d", ref_text) and low is None and high is None:
                confidence = min(confidence, 0.72)
            observations.append({
                "test_name": name, "raw_test_name": name, "value_numeric": value.numeric,
                "value_text": value.text, "unit": unit_cell, "reference_low": low,
                "reference_high": high, "reference_text": ref_text, "panel": current_panel,
                "method": "", "source_page": page["page"], "extraction_confidence": confidence,
                "auto_extracted": 1, "notes": notes,
            })
    return headings, observations, explicit_samples, warnings


def parse_lab_pdf(pdf_bytes: bytes) -> dict[str, Any]:
    warnings: list[str] = []
    try:
        bundle = extract_document(pdf_bytes)
    except Exception as exc:
        return {"ok": False, "engine": "pdf-extraction", "warnings": [f"PDF extraction failed: {exc}"],
                "metadata": {}, "headings": [], "observations": [], "page_count": 0, "confidence": 0.0}

    warnings.extend(bundle.warnings)
    all_text_sources: list[str] = list(bundle.layout_pages) + list(bundle.plain_pages)
    page_count = max(len(bundle.layout_pages), len(bundle.plain_pages), 1)
    used_ocr = bool(bundle.ocr_pages)
    selected_engine = bundle.engine
    selected_text_pages = list(bundle.plain_pages or bundle.layout_pages)
    # Keep every text representation for qualitative microbiology recovery. A visual
    # culture row may serialize very differently between pypdf, PyMuPDF, OCR, Linux
    # and macOS even when the chemistry-table parser has already chosen one engine.
    micro_source_variants: list[tuple[list[str], bool]] = []
    for initial_pages in (bundle.layout_pages, bundle.plain_pages):
        if initial_pages:
            micro_source_variants.append((list(initial_pages), False))

    if bundle.ocr_pages:
        headings, observations, explicit_samples, row_warnings = parse_ocr_rows(bundle.ocr_pages)
        selected_text_pages = [p.get("text", "") for p in bundle.ocr_pages]
        micro_source_variants.append((list(selected_text_pages), True))
        warnings.extend(row_warnings)
        warnings.append("OCR values can be misread in low-quality scans. Review detected values and reference ranges before confirming the report.")
    else:
        # Parse the primary embedded-text extraction, then independently parse both
        # native engines. Choose the candidate that actually yields the most structured
        # observations instead of assuming that the engine with the most characters has
        # the best table layout. This is the key cross-platform parity rule.
        candidates: list[tuple[str, list[str], list[str], list[str], list[dict[str, Any]], list[str]]] = []

        primary_headings, primary_obs, primary_samples = parse_layout_rows(bundle.layout_pages)
        candidates.append((bundle.engine, bundle.layout_pages, bundle.plain_pages, primary_headings, primary_obs, primary_samples))

        extraction_attempts = (
            ("pypdf-layout", _pypdf_text_pages),
            ("pymupdf-positional", _pymupdf_text_pages),
        )
        seen_layouts = {"\n".join(bundle.layout_pages)}
        for engine_name, extractor in extraction_attempts:
            try:
                layout_pages, plain_pages = extractor(pdf_bytes)
            except Exception as exc:
                warnings.append(f"{engine_name} structured-text retry failed: {exc}")
                continue
            if not layout_pages:
                continue
            fingerprint = "\n".join(layout_pages)
            if fingerprint in seen_layouts:
                continue
            seen_layouts.add(fingerprint)
            all_text_sources.extend(layout_pages)
            all_text_sources.extend(plain_pages)
            page_count = max(page_count, len(layout_pages), len(plain_pages))
            h, o, samples = parse_layout_rows(layout_pages)
            candidates.append((engine_name, layout_pages, plain_pages, h, o, samples))
            if layout_pages:
                micro_source_variants.append((list(layout_pages), False))
            if plain_pages:
                micro_source_variants.append((list(plain_pages), False))

        # Prefer more structured rows. In a tie, keep the primary engine to avoid
        # unnecessary behavioral changes on documents already validated in Linux.
        best_index = max(range(len(candidates)), key=lambda i: (len(candidates[i][4]), -i))
        best_engine, _best_layout, _best_plain, headings, observations, explicit_samples = candidates[best_index]
        selected_text_pages = list(_best_layout or _best_plain)
        if best_engine != bundle.engine and len(observations) > len(primary_obs):
            warnings.append(
                f"Structured rows were recovered with {best_engine} after {bundle.engine} produced fewer usable rows."
            )
            selected_engine = best_engine

        # Last-resort structural fallback: a PDF may have embedded text that is useful
        # for metadata but whose table coordinates are unusable in a frozen app. OCR the
        # page image only when both native text engines fail to produce any rows.
        if not observations:
            ocr_pages, ocr_warnings = ocr_document(pdf_bytes)
            warnings.extend(ocr_warnings)
            if ocr_pages:
                oh, oo, osamples, row_warnings = parse_ocr_rows(ocr_pages)
                warnings.extend(row_warnings)
                if oo:
                    headings, observations, explicit_samples = oh, oo, osamples
                    all_text_sources.extend(p.get("text", "") for p in ocr_pages)
                    page_count = max(page_count, len(ocr_pages))
                    selected_engine = "pymupdf-tesseract-ocr-fallback"
                    used_ocr = True
                    selected_text_pages = [p.get("text", "") for p in ocr_pages]
                    micro_source_variants.append((list(selected_text_pages), True))
                    warnings.append(
                        "Embedded text was readable but did not preserve the result-table structure; local OCR recovered structured rows."
                    )
                    warnings.append(
                        "OCR values can be misread in low-quality scans. Review detected values and reference ranges before confirming the report."
                    )

    # Culture/microbiology reports often have qualitative results but no reference
    # column.  Parse *all* available text representations, not only the engine chosen
    # for numeric tables. This is critical for urocultures whose visual row can become
    # horizontal in one engine and vertically fragmented in another.
    if selected_text_pages:
        micro_source_variants.append((list(selected_text_pages), used_ocr))
    existing_signatures = {
        (
            int(obs.get("source_page") or 0),
            key_text(obs.get("test_name", "")),
            key_text(obs.get("value_text", "")),
            clean_text(obs.get("unit", "")),
        )
        for obs in observations
    }
    seen_micro_sources: set[tuple[bool, str]] = set()
    recovered_micro = 0
    for micro_pages, micro_is_ocr in micro_source_variants:
        fingerprint = (micro_is_ocr, "\n\f\n".join(micro_pages))
        if not any(micro_pages) or fingerprint in seen_micro_sources:
            continue
        seen_micro_sources.add(fingerprint)
        micro_headings, micro_observations = parse_microbiology_qualitative_rows(
            micro_pages, ocr=micro_is_ocr
        )
        for heading in micro_headings:
            if heading not in headings:
                headings.append(heading)
        for obs in micro_observations:
            page_no = int(obs.get("source_page") or 0)
            test_key = key_text(obs.get("test_name", ""))
            value_key = key_text(obs.get("value_text", ""))
            unit_text = clean_text(obs.get("unit", ""))
            sig = (page_no, test_key, value_key, unit_text)
            if sig in existing_signatures:
                continue

            # Different PDF engines can expose a multiline culture value at different
            # granularity (e.g. "Sin desarrollo" vs "Sin desarrollo microbiano").
            # For the same field/page/unit keep the more specific prefix-extension,
            # rather than importing both as separate clinical results.
            dominated_index = None
            dominated_sig = None
            skip_new = False
            for idx, existing in enumerate(observations):
                if int(existing.get("source_page") or 0) != page_no:
                    continue
                if key_text(existing.get("test_name", "")) != test_key:
                    continue
                if clean_text(existing.get("unit", "")) != unit_text:
                    continue
                old_key = key_text(existing.get("value_text", ""))
                if not old_key or not value_key or old_key == value_key:
                    continue
                if value_key.startswith(old_key + " "):
                    dominated_index = idx
                    dominated_sig = (page_no, test_key, old_key, unit_text)
                    break
                if old_key.startswith(value_key + " "):
                    skip_new = True
                    break
            if skip_new:
                continue
            if dominated_index is not None:
                observations[dominated_index] = obs
                if dominated_sig is not None:
                    existing_signatures.discard(dominated_sig)
                existing_signatures.add(sig)
                continue

            observations.append(obs)
            existing_signatures.add(sig)
            recovered_micro += 1
    if recovered_micro:
        warnings.append(
            f"Recovered {recovered_micro} qualitative microbiology/culture result(s) across available PDF text layouts."
        )

    combined = "\n".join(all_text_sources)
    metadata = match_metadata(combined)

    if not metadata.get("lab"):
        warnings.append("Laboratory name was not identified automatically; review it before saving.")
    if not metadata.get("report_date"):
        warnings.append("Report/registration date was not identified automatically.")
    if not observations:
        warnings.append("No structured result rows were detected; manual review is required.")

    metadata["study_type"] = summarize_study(headings)
    metadata["specimen"] = infer_specimens(headings, explicit_samples)

    essential_hits = sum(bool(metadata.get(k)) for k in ("lab", "report_date", "patient_name", "order_number"))
    confidence = (0.50 if used_ocr else 0.55) + 0.07 * essential_hits
    if observations:
        confidence += 0.10
    if used_ocr and observations:
        row_average = sum(float(x.get("extraction_confidence") or 0.0) for x in observations) / len(observations)
        confidence = min(confidence, row_average)
    confidence = min(confidence, 0.97 if not used_ocr else 0.88)

    return {"ok": True, "engine": selected_engine, "warnings": list(dict.fromkeys(warnings)),
            "metadata": metadata, "headings": headings, "observations": observations,
            "page_count": page_count, "confidence": round(confidence, 2)}
