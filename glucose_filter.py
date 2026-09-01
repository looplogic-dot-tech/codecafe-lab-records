from __future__ import annotations

import re
import unicodedata
from typing import Any


def key_text(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.casefold().replace("µ", "u").replace("μ", "u")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def is_glucose_name(raw_name: str) -> bool:
    name = key_text(raw_name)
    return any(token in name for token in ("glucosa", "glucose", "glucemia", "glycemia"))


def glucose_lookup_name(raw_name: str, panel: str, specimen: str) -> str:
    """Return the safe canonical lookup label while preserving urine separation.

    Matrix/collection words in labels such as ``Glucosa sérica basal`` are context,
    not a different analyte. The app therefore resolves them through its existing
    generic ``Glucosa`` seed. Urine is still disambiguated by the existing specimen
    context in clinical_dictionary.py.
    """
    if is_glucose_name(raw_name):
        return "Glucosa"
    return raw_name


def glucose_context(raw_name: str, panel: str = "", specimen_hint: str = "") -> dict[str, Any]:
    """Extract glucose matrix and collection/timepoint metadata without altering values."""
    combined = key_text(f"{raw_name} {panel}")
    if not is_glucose_name(raw_name):
        return {
            "specimen_detail": specimen_hint,
            "collection_context": "",
            "timepoint_minutes": None,
        }

    if specimen_hint == "Urine" or any(token in combined for token in ("orina", "urine", "urocultivo")):
        return {
            "specimen_detail": "Urine",
            "collection_context": "",
            "timepoint_minutes": None,
        }

    if any(token in combined for token in ("capilar", "capillary")):
        matrix = "Capillary blood"
    elif any(token in combined for token in ("sangre total", "whole blood")):
        matrix = "Whole blood"
    elif any(token in combined for token in ("plasma", "plasmatica", "plasmatic")):
        matrix = "Plasma"
    elif any(token in combined for token in ("serica", "serico", "serum")):
        matrix = "Serum"
    elif any(token in combined for token in ("en sangre", "sanguinea", "sanguineo", "blood glucose")):
        matrix = "Blood"
    else:
        matrix = specimen_hint or "Serum"

    collection_context = ""
    timepoint: int | None = None

    if any(token in combined for token in ("en ayunas", "ayuno", "fasting", "basal")):
        collection_context = "Basal/Ayuno"
        timepoint = 0
    elif any(token in combined for token in ("postprandial", "post prandial", "despues de comer", "after meal")):
        collection_context = "Postprandial"
    elif any(token in combined for token in ("aleatoria", "al azar", "random glucose")):
        collection_context = "Aleatoria"

    minute_match = re.search(r"(?:^|\s)(\d{1,3})\s*(?:min|minuto|minutos)(?:\s|$)", combined)
    hour_match = re.search(r"(?:^|\s)(\d{1,2})\s*(?:h|hr|hrs|hora|horas)(?:\s|$)", combined)
    if minute_match:
        timepoint = int(minute_match.group(1))
        collection_context = f"{timepoint} min post carga" if timepoint else (collection_context or "Basal")
    elif hour_match:
        timepoint = int(hour_match.group(1)) * 60
        collection_context = f"{timepoint} min post carga" if timepoint else (collection_context or "Basal")

    return {
        "specimen_detail": matrix,
        "collection_context": collection_context,
        "timepoint_minutes": timepoint,
    }


def format_glucose_specimen_detail(raw_name: str, panel: str, specimen_hint: str) -> str:
    meta = glucose_context(raw_name, panel, specimen_hint)
    parts: list[str] = []
    matrix = str(meta.get("specimen_detail") or specimen_hint or "").strip()
    context = str(meta.get("collection_context") or "").strip()
    timepoint = meta.get("timepoint_minutes")
    if matrix:
        parts.append(matrix)
    if context:
        parts.append(context)
    if timepoint is not None and not context.startswith(f"{timepoint} min"):
        parts.append(f"t={int(timepoint)} min")
    return " · ".join(parts) or specimen_hint
