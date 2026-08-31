from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any

MEDLINEPLUS_BASE = "https://medlineplus.gov/lab-tests/"
MEDLINEPLUS_DIR = MEDLINEPLUS_BASE


def key_text(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.casefold().replace("µ", "u")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def slug(value: str) -> str:
    return key_text(value).replace(" ", "_") or "unknown"


def specimen_from_context(panel: str, test_name: str = "") -> str:
    text = key_text(f"{panel} {test_name}")
    if any(token in text for token in ("orina", "urine", "urocultivo", "urine culture", "microscopico", "quimico", "fisico")):
        return "Urine"
    if any(token in text for token in ("biometria hematica", "hemograma", "complete blood", "cbc")):
        return "Blood"
    return "Serum"


@dataclass(frozen=True)
class UnitRule:
    display: str
    ucum: str


UNIT_RULES: dict[str, UnitRule] = {
    "mg/dl": UnitRule("mg/dL", "mg/dL"),
    "g/dl": UnitRule("g/dL", "g/dL"),
    "g/dl(%)": UnitRule("g/dL", "g/dL"),
    "ng/ml": UnitRule("ng/mL", "ng/mL"),
    "ug/dl": UnitRule("µg/dL", "ug/dL"),
    "mcg/dl": UnitRule("µg/dL", "ug/dL"),
    "u/l": UnitRule("U/L", "U/L"),
    "meq/l": UnitRule("mEq/L", "meq/L"),
    "mmol/l": UnitRule("mmol/L", "mmol/L"),
    "uu/ml": UnitRule("µU/mL", "uU/mL"),
    "uiu/ml": UnitRule("µIU/mL", "u[IU]/mL"),
    "ml/min/1.73m2": UnitRule("mL/min/1.73 m²", ""),
    "fl": UnitRule("fL", "fL"),
    "pg": UnitRule("pg", "pg"),
    "%": UnitRule("%", "%"),
    "miles/ul": UnitRule("10³/µL", "10*3/uL"),
    "millones/ul": UnitRule("10⁶/µL", "10*6/uL"),
    "eri/ul": UnitRule("eritrocitos/µL", "/uL"),
    "leu/ul": UnitRule("leucocitos/µL", "/uL"),
    "/campo": UnitRule("/campo", ""),
    "ufc/ml": UnitRule("UFC/mL", ""),
    "cfu/ml": UnitRule("CFU/mL", ""),
    "k/ul": UnitRule("10³/µL", "10*3/uL"),
    "kiul": UnitRule("10³/µL", "10*3/uL"),
    "klul": UnitRule("10³/µL", "10*3/uL"),
    "klub": UnitRule("10³/µL", "10*3/uL"),
    "kul": UnitRule("10³/µL", "10*3/uL"),
    "10*3/ul": UnitRule("10³/µL", "10*3/uL"),
    "10*3/pl": UnitRule("10³/µL", "10*3/uL"),
    "10*3/pul": UnitRule("10³/µL", "10*3/uL"),
    "10%3/pl>": UnitRule("10³/µL", "10*3/uL"),
    "10%3/pl": UnitRule("10³/µL", "10*3/uL"),
    "m/ul": UnitRule("10⁶/µL", "10*6/uL"),
    "10*6/ul": UnitRule("10⁶/µL", "10*6/uL"),
    "10*6/pl": UnitRule("10⁶/µL", "10*6/uL"),
    "": UnitRule("", ""),
}


def normalize_unit(raw_unit: str) -> UnitRule:
    raw = (raw_unit or "").strip().replace("μ", "µ")
    k = key_text(raw).replace(" ", "")
    # key_text strips punctuation such as '/', so direct aliases are checked first.
    direct = raw.casefold().replace("µ", "u").replace("μ", "u").replace(" ", "")
    return UNIT_RULES.get(direct) or UNIT_RULES.get(k) or UnitRule(raw, "")


# Conversion factors convert the source value to the canonical display unit.
# They are intentionally analyte-specific. Unknown conversions are never guessed.
CONVERSIONS: dict[str, dict[str, tuple[str, str, float]]] = {
    "glucose_blood": {
        "mmol/l": ("mg/dL", "mg/dL", 18.0182),
        "mg/dl": ("mg/dL", "mg/dL", 1.0),
    },
    "cholesterol_total": {
        "mmol/l": ("mg/dL", "mg/dL", 38.67),
        "mg/dl": ("mg/dL", "mg/dL", 1.0),
    },
    "cholesterol_hdl": {
        "mmol/l": ("mg/dL", "mg/dL", 38.67),
        "mg/dl": ("mg/dL", "mg/dL", 1.0),
    },
    "cholesterol_ldl": {
        "mmol/l": ("mg/dL", "mg/dL", 38.67),
        "mg/dl": ("mg/dL", "mg/dL", 1.0),
    },
    "cholesterol_non_hdl": {
        "mmol/l": ("mg/dL", "mg/dL", 38.67),
        "mg/dl": ("mg/dL", "mg/dL", 1.0),
    },
    "triglycerides": {
        "mmol/l": ("mg/dL", "mg/dL", 88.57),
        "mg/dl": ("mg/dL", "mg/dL", 1.0),
    },
    "creatinine": {
        "umol/l": ("mg/dL", "mg/dL", 1 / 88.4),
        "mg/dl": ("mg/dL", "mg/dL", 1.0),
    },
    "uric_acid": {
        "umol/l": ("mg/dL", "mg/dL", 1 / 59.48),
        "mg/dl": ("mg/dL", "mg/dL", 1.0),
    },
}


def unit_token(raw: str) -> str:
    return (raw or "").strip().casefold().replace("µ", "u").replace("μ", "u").replace(" ", "")


def convert_numeric(canonical_key: str, value: float | None, raw_unit: str) -> tuple[float | None, str, str, str]:
    rule = normalize_unit(raw_unit)
    if value is None:
        return None, rule.display, rule.ucum, "text"
    conversions = CONVERSIONS.get(canonical_key, {})
    conversion = conversions.get(unit_token(raw_unit))
    if conversion:
        display, ucum, factor = conversion
        return value * factor, display, ucum, "converted" if factor != 1.0 else "normalized"
    return value, rule.display, rule.ucum, "normalized" if rule.display or not raw_unit else "original-only"


def convert_bound(canonical_key: str, value: float | None, raw_unit: str) -> float | None:
    if value is None:
        return None
    conversion = CONVERSIONS.get(canonical_key, {}).get(unit_token(raw_unit))
    return value * conversion[2] if conversion else value


# Canonical dictionary seed. Aliases are exact semantic synonyms; fuzzy matches are never auto-merged.
# Context (specimen/unit) disambiguates repeated names such as glucose or hemoglobin.
SEEDS: list[dict[str, Any]] = [
    {"key":"glucose_blood","es":"Glucosa en sangre","en":"Blood glucose","aliases":["glucosa","glucose","glucosa serica","glucosa sérica","serum glucose","blood glucose"],"specimen":"Serum","unit":"mg/dL","url":MEDLINEPLUS_BASE+"blood-glucose-test/"},
    {"key":"glucose_urine","es":"Glucosa en orina","en":"Urine glucose","aliases":["glucosa","glucose","glucosa en orina","urine glucose"],"specimen":"Urine","unit":"mg/dL","url":MEDLINEPLUS_BASE+"glucose-in-urine-test/"},
    {"key":"bun","es":"Nitrógeno ureico en sangre (BUN)","en":"Blood urea nitrogen (BUN)","aliases":["nitrógeno de urea en sangre (bun)","nitrogeno de urea en sangre bun","nitrógeno ureico (bun)","nitrogeno ureico (bun)","nitrogeno ureico bun","bun","blood urea nitrogen","urea nitrogen"],"specimen":"Serum","unit":"mg/dL","url":MEDLINEPLUS_BASE+"bun-blood-urea-nitrogen/"},
    {"key":"creatinine","es":"Creatinina","en":"Creatinine","aliases":["creatinina","creatinine","serum creatinine"],"specimen":"Serum","unit":"mg/dL","url":MEDLINEPLUS_BASE+"creatinine-test/"},
    {"key":"bun_creatinine_ratio","es":"Relación BUN/creatinina","en":"BUN/creatinine ratio","aliases":["relación bun/creat","relacion bun creat","bun/creatinine ratio","bun creatinine ratio"],"specimen":"Serum","unit":"","url":MEDLINEPLUS_BASE+"bun-blood-urea-nitrogen/"},
    {"key":"uric_acid","es":"Ácido úrico","en":"Uric acid","aliases":["ácido úrico","acido urico","uric acid"],"specimen":"Serum","unit":"mg/dL","url":MEDLINEPLUS_BASE+"uric-acid-test/"},
    {"key":"phosphorus","es":"Fósforo / fosfato","en":"Phosphorus / phosphate","aliases":["fósforo","fosforo","phosphorus","phosphate"],"specimen":"Serum","unit":"mg/dL","url":MEDLINEPLUS_BASE+"phosphate-in-blood/"},
    {"key":"calcium","es":"Calcio","en":"Calcium","aliases":["calcio","calcium"],"specimen":"Serum","unit":"mg/dL","url":MEDLINEPLUS_BASE+"calcium-blood-test/"},
    {"key":"magnesium","es":"Magnesio","en":"Magnesium","aliases":["magnesio","magnesium","mg"],"specimen":"Serum","unit":"mg/dL","url":MEDLINEPLUS_BASE+"magnesium-blood-test/"},
    {"key":"sodium","es":"Sodio","en":"Sodium","aliases":["sodio","sodium","na"],"specimen":"Serum","unit":"mEq/L","url":MEDLINEPLUS_BASE+"sodium-blood-test/"},
    {"key":"potassium","es":"Potasio","en":"Potassium","aliases":["potasio","potassium","k"],"specimen":"Serum","unit":"mEq/L","url":MEDLINEPLUS_BASE+"potassium-blood-test/"},
    {"key":"chloride","es":"Cloro / cloruro","en":"Chloride","aliases":["cloro","cloruro","chloride","cl"],"specimen":"Serum","unit":"mEq/L","url":MEDLINEPLUS_BASE+"chloride-blood-test/"},
    {"key":"egfr","es":"Filtración glomerular estimada (eGFR/TFGe)","en":"Estimated glomerular filtration rate (eGFR)","aliases":["tasa de filtración glomerular estima","tasa de filtracion glomerular estimada","tfge","egfr","estimated glomerular filtration rate"],"specimen":"Serum","unit":"mL/min/1.73 m²","url":MEDLINEPLUS_BASE+"glomerular-filtration-rate-gfr-test/"},
    {"key":"cholesterol_total","es":"Colesterol total","en":"Total cholesterol","aliases":["colesterol","colesterol total","total cholesterol"],"specimen":"Serum","unit":"mg/dL","url":MEDLINEPLUS_BASE+"cholesterol-levels/"},
    {"key":"cholesterol_hdl","es":"Colesterol HDL","en":"HDL cholesterol","aliases":["colesterol hdl","hdl","hdl cholesterol"],"specimen":"Serum","unit":"mg/dL","url":MEDLINEPLUS_BASE+"cholesterol-levels/"},
    {"key":"cholesterol_ldl","es":"Colesterol LDL","en":"LDL cholesterol","aliases":["colesterol ldl directo","colesterol ldl","ldl directo","ldl cholesterol","direct ldl"],"specimen":"Serum","unit":"mg/dL","url":MEDLINEPLUS_BASE+"cholesterol-levels/"},
    {"key":"cholesterol_non_hdl","es":"Colesterol no-HDL","en":"Non-HDL cholesterol","aliases":["colesterol no-hdl","colesterol no hdl","non-hdl cholesterol","non hdl cholesterol"],"specimen":"Serum","unit":"mg/dL","url":MEDLINEPLUS_BASE+"cholesterol-levels/"},
    {"key":"triglycerides","es":"Triglicéridos","en":"Triglycerides","aliases":["triglicéridos","trigliceridos","triglycerides"],"specimen":"Serum","unit":"mg/dL","url":MEDLINEPLUS_BASE+"triglycerides-test/"},
    {"key":"crp_hs","es":"Proteína C reactiva ultrasensible","en":"High-sensitivity C-reactive protein","aliases":["proteína c reactiva ultrasensible","proteina c reactiva ultrasensible","hs-crp","hs crp","high sensitivity c reactive protein"],"specimen":"Serum","unit":"mg/dL","url":MEDLINEPLUS_BASE+"c-reactive-protein-crp-test/"},
    {"key":"bilirubin_total","es":"Bilirrubina total","en":"Total bilirubin","aliases":["bilirrubina total","total bilirubin"],"specimen":"Serum","unit":"mg/dL","url":MEDLINEPLUS_BASE+"bilirubin-blood-test/"},
    {"key":"bilirubin_direct","es":"Bilirrubina directa","en":"Direct bilirubin","aliases":["bilirrubina directa","direct bilirubin"],"specimen":"Serum","unit":"mg/dL","url":MEDLINEPLUS_BASE+"bilirubin-blood-test/"},
    {"key":"bilirubin_indirect","es":"Bilirrubina indirecta","en":"Indirect bilirubin","aliases":["bilirrubina indirecta","indirect bilirubin"],"specimen":"Serum","unit":"mg/dL","url":MEDLINEPLUS_BASE+"bilirubin-blood-test/"},
    {"key":"ast","es":"AST (TGO)","en":"AST","aliases":["ast (tgo)","ast","tgo","aspartate aminotransferase"],"specimen":"Serum","unit":"U/L","url":MEDLINEPLUS_BASE+"ast-test/"},
    {"key":"alt","es":"ALT (TGP)","en":"ALT","aliases":["alt (tgp)","alt","tgp","alanine aminotransferase"],"specimen":"Serum","unit":"U/L","url":MEDLINEPLUS_BASE+"alt-blood-test/"},
    {"key":"ast_alt_ratio","es":"Relación AST/ALT","en":"AST/ALT ratio","aliases":["relación: ast/alt","relacion ast alt","ast/alt ratio"],"specimen":"Serum","unit":"","url":MEDLINEPLUS_BASE+"liver-function-tests/"},
    {"key":"ggt","es":"Gamma-glutamil transferasa (GGT)","en":"Gamma-glutamyl transferase (GGT)","aliases":["gama glutamil transpeptidasa","gamma glutamil transpeptidasa","ggt","gamma glutamyl transferase"],"specimen":"Serum","unit":"U/L","url":MEDLINEPLUS_BASE+"gamma-glutamyl-transferase-ggt-test/"},
    {"key":"alkaline_phosphatase","es":"Fosfatasa alcalina","en":"Alkaline phosphatase","aliases":["f. alcalina total","fosfatasa alcalina","alkaline phosphatase","alp"],"specimen":"Serum","unit":"U/L","url":MEDLINEPLUS_BASE+"alkaline-phosphatase/"},
    {"key":"ldh","es":"Lactato deshidrogenasa (LDH)","en":"Lactate dehydrogenase (LDH)","aliases":["ldh","lactato deshidrogenasa","lactate dehydrogenase"],"specimen":"Serum","unit":"U/L","url":MEDLINEPLUS_BASE+"lactate-dehydrogenase-ldh-test/"},
    {"key":"total_protein","es":"Proteínas totales","en":"Total protein","aliases":["proteínas totales","proteinas totales","total protein"],"specimen":"Serum","unit":"g/dL","url":MEDLINEPLUS_BASE+"comprehensive-metabolic-panel-cmp/"},
    {"key":"albumin","es":"Albúmina","en":"Albumin","aliases":["albúmina","albumina","albumin"],"specimen":"Serum","unit":"g/dL","url":MEDLINEPLUS_BASE+"albumin-blood-test/"},
    {"key":"globulin","es":"Globulinas","en":"Globulins","aliases":["globulinas","globulin","globulins"],"specimen":"Serum","unit":"g/dL","url":MEDLINEPLUS_BASE+"globulin-test/"},
    {"key":"ag_ratio","es":"Relación albúmina/globulina (A/G)","en":"Albumin/globulin ratio (A/G)","aliases":["relación a/g","relacion a g","a/g ratio","albumin globulin ratio"],"specimen":"Serum","unit":"","url":MEDLINEPLUS_BASE+"comprehensive-metabolic-panel-cmp/"},
    {"key":"iron","es":"Hierro sérico","en":"Serum iron","aliases":["hierro","serum iron","iron"],"specimen":"Serum","unit":"µg/dL","url":MEDLINEPLUS_BASE+"iron-tests/"},
    {"key":"uibc","es":"UIBC","en":"Unsaturated iron-binding capacity (UIBC)","aliases":["uibc","unsaturated iron binding capacity"],"specimen":"Serum","unit":"µg/dL","url":MEDLINEPLUS_BASE+"iron-tests/"},
    {"key":"tibc","es":"Capacidad total de fijación de hierro","en":"Total iron-binding capacity (TIBC)","aliases":["captación de hierro","captacion de hierro","tibc","total iron binding capacity"],"specimen":"Serum","unit":"µg/dL","url":MEDLINEPLUS_BASE+"iron-tests/"},
    {"key":"iron_saturation","es":"Saturación de hierro","en":"Iron saturation","aliases":["porcentaje de saturación de hierro","porcentaje de saturacion de hierro","iron saturation","transferrin saturation"],"specimen":"Serum","unit":"%","url":MEDLINEPLUS_BASE+"iron-tests/"},
    {"key":"immunoglobulin_g","es":"Inmunoglobulina G (IgG)","en":"Immunoglobulin G (IgG)","aliases":["inmunoglobulina g","igg","immunoglobulin g"],"specimen":"Serum","unit":"mg/dL","url":MEDLINEPLUS_BASE+"immunoglobulins-blood-test/"},
    {"key":"immunoglobulin_a","es":"Inmunoglobulina A (IgA)","en":"Immunoglobulin A (IgA)","aliases":["inmunoglobulina a","iga","immunoglobulin a"],"specimen":"Serum","unit":"mg/dL","url":MEDLINEPLUS_BASE+"immunoglobulins-blood-test/"},
    {"key":"immunoglobulin_m","es":"Inmunoglobulina M (IgM)","en":"Immunoglobulin M (IgM)","aliases":["inmunoglobulina m","igm","immunoglobulin m"],"specimen":"Serum","unit":"mg/dL","url":MEDLINEPLUS_BASE+"immunoglobulins-blood-test/"},
    {"key":"psa_total","es":"Antígeno prostático específico total (PSA)","en":"Total prostate-specific antigen (PSA)","aliases":["antígeno prostático específico total","antigeno prostatico especifico total","psa total","total psa","prostate specific antigen total"],"specimen":"Serum","unit":"ng/mL","url":MEDLINEPLUS_BASE+"prostate-specific-antigen-psa-test/"},
    {"key":"testosterone_total","es":"Testosterona total","en":"Total testosterone","aliases":["testosterona total","total testosterone","testosterone total"],"specimen":"Serum","unit":"ng/mL","url":MEDLINEPLUS_BASE+"testosterone-levels-test/"},
    {"key":"hba1c","es":"Hemoglobina glicosilada A1c","en":"Hemoglobin A1c","aliases":["hemoglobina glicosilada a1c","hemoglobina glucosilada a1c","hba1c","a1c","hemoglobin a1c"],"specimen":"Blood","unit":"%","url":MEDLINEPLUS_BASE+"hemoglobin-a1c-hba1c-test/"},
    {"key":"insulin_fasting","es":"Insulina basal","en":"Fasting insulin","aliases":["insulina basal","insulina en ayuno","fasting insulin","insulin fasting"],"specimen":"Serum","unit":"µU/mL","url":MEDLINEPLUS_BASE+"insulin-in-blood/"},
    {"key":"homa_ir","es":"HOMA-IR","en":"HOMA-IR","aliases":["homa-ir","homa ir"],"specimen":"Serum","unit":"","url":"https://www.niddk.nih.gov/health-information/diabetes/overview/what-is-diabetes/prediabetes-insulin-resistance"},
    {"key":"microalbumin_urine","es":"Microalbuminuria / albúmina en orina","en":"Urine microalbumin / albumin","aliases":["microalbuminuria","microalbumin","urine albumin","albúmina en orina","albumina en orina"],"specimen":"Urine","unit":"mg/dL","url":MEDLINEPLUS_BASE+"microalbumin-creatinine-ratio/"},
    {"key":"urine_specific_gravity","es":"Densidad urinaria","en":"Urine specific gravity","aliases":["densidad","densidad urinaria","specific gravity","urine specific gravity"],"specimen":"Urine","unit":"","url":"https://medlineplus.gov/ency/article/003587.htm"},
    {"key":"urine_ph","es":"pH urinario","en":"Urine pH","aliases":["ph","pH","ph urinario","urine ph"],"specimen":"Urine","unit":"","url":"https://medlineplus.gov/urinalysis.html"},
    {"key":"urine_leukocyte_esterase","es":"Esterasa leucocitaria en orina","en":"Urine leukocyte esterase","aliases":["esterasa leucocitaria","leukocyte esterase"],"specimen":"Urine","unit":"","url":"https://medlineplus.gov/ency/article/003584.htm"},
    {"key":"urine_nitrite","es":"Nitritos en orina","en":"Nitrites in urine","aliases":["nitritos","nitrite","nitrites"],"specimen":"Urine","unit":"","url":MEDLINEPLUS_BASE+"nitrites-in-urine/"},
    {"key":"urine_protein","es":"Proteína en orina","en":"Protein in urine","aliases":["proteínas","proteinas","protein","proteína en orina","protein in urine"],"specimen":"Urine","unit":"mg/dL","url":MEDLINEPLUS_BASE+"protein-in-urine/"},
    {"key":"urine_ketones","es":"Cetonas en orina","en":"Ketones in urine","aliases":["cetonas","ketones","ketone"],"specimen":"Urine","unit":"mg/dL","url":MEDLINEPLUS_BASE+"ketones-in-urine/"},
    {"key":"urine_bilirubin","es":"Bilirrubina en orina","en":"Bilirubin in urine","aliases":["bilirrubina","bilirubin"],"specimen":"Urine","unit":"mg/dL","url":MEDLINEPLUS_BASE+"bilirubin-in-urine/"},
    {"key":"urine_urobilinogen","es":"Urobilinógeno en orina","en":"Urobilinogen in urine","aliases":["urobilinógeno","urobilinogeno","urobilinogen"],"specimen":"Urine","unit":"mg/dL","url":MEDLINEPLUS_BASE+"urobilinogen-in-urine/"},
    {"key":"urine_blood","es":"Sangre/hemoglobina en orina","en":"Blood/hemoglobin in urine","aliases":["hemoglobina","blood","blood in urine"],"specimen":"Urine","unit":"","url":MEDLINEPLUS_BASE+"blood-in-urine/"},
    {"key":"urine_rbc","es":"Eritrocitos en orina","en":"Red blood cells in urine","aliases":["eritrocitos","red blood cells","rbc"],"specimen":"Urine","unit":"/campo","url":MEDLINEPLUS_BASE+"blood-in-urine/"},
    {"key":"urine_wbc","es":"Leucocitos en orina","en":"White blood cells in urine","aliases":["leucocitos","white blood cells","wbc"],"specimen":"Urine","unit":"/campo","url":"https://medlineplus.gov/urinalysis.html"},
    {"key":"urine_crystals","es":"Cristales en orina","en":"Crystals in urine","aliases":["cristales","crystals"],"specimen":"Urine","unit":"","url":MEDLINEPLUS_BASE+"crystals-in-urine/"},
    {"key":"urine_epithelial_cells","es":"Células epiteliales en orina","en":"Epithelial cells in urine","aliases":["células pavimentosas","celulas pavimentosas","células de transición","celulas de transicion","células tubulares renales","celulas tubulares renales","epithelial cells"],"specimen":"Urine","unit":"","url":MEDLINEPLUS_BASE+"epithelial-cells-in-urine/"},
    {"key":"urine_mucus","es":"Moco en orina","en":"Mucus in urine","aliases":["redes mucoides","moco","mucus"],"specimen":"Urine","unit":"","url":MEDLINEPLUS_BASE+"mucus-in-urine/"},
    {"key":"urine_culture","es":"Urocultivo / cultivo de orina","en":"Urine culture","aliases":["cultivo","urocultivo","cultivo de orina","urine culture","cultivo bacteriológico en orina","cultivo bacteriologico en orina"],"specimen":"Urine","unit":"","url":MEDLINEPLUS_BASE+"bacteria-culture-test/"},
    {"key":"urinalysis_general","es":"Examen general de orina","en":"Urinalysis","aliases":["color","aspecto","bacterias","levaduras","cilindros","eritrocitos dismórficos"],"specimen":"Urine","unit":"","url":"https://medlineplus.gov/urinalysis.html"},
]

SEEDS.extend([
    {"key":"urea","es":"Urea","en":"Urea","aliases":["urea","serum urea"],"specimen":"Serum","unit":"mg/dL","url":MEDLINEPLUS_BASE+"bun-blood-urea-nitrogen/"},
    {"key":"atherogenic_index","es":"Índice aterogénico","en":"Atherogenic index","aliases":["índice aterogénico","indice aterogenico","atherogenic index"],"specimen":"Serum","unit":"","url":MEDLINEPLUS_BASE+"cholesterol-levels/"},
    {"key":"ldl_hdl_ratio","es":"Relación LDL/HDL","en":"LDL/HDL ratio","aliases":["relación ldl/hdl","relacion ldl hdl","ldl/hdl ratio"],"specimen":"Serum","unit":"","url":MEDLINEPLUS_BASE+"cholesterol-levels/"},
    {"key":"small_dense_ldl","es":"LDL pequeña y densa","en":"Small dense LDL","aliases":["sd ldl","small dense ldl","small dense LDL"],"specimen":"Serum","unit":"","url":MEDLINEPLUS_BASE+"cholesterol-levels/"},
    {"key":"vldl_cholesterol","es":"Colesterol VLDL","en":"VLDL cholesterol","aliases":["vldl colesterol","colesterol vldl","vldl cholesterol"],"specimen":"Serum","unit":"mg/dL","url":MEDLINEPLUS_BASE+"cholesterol-levels/"},
    {"key":"total_lipids","es":"Lípidos totales","en":"Total lipids","aliases":["lípidos totales","lipidos totales","total lipids"],"specimen":"Serum","unit":"mg/dL","url":MEDLINEPLUS_BASE+"cholesterol-levels/"},
    {"key":"serum_phospholipids","es":"Fosfolípidos en suero","en":"Serum phospholipids","aliases":["fosfolípidos en suero","fosfolipidos en suero","serum phospholipids"],"specimen":"Serum","unit":"mg/dL","url":MEDLINEPLUS_BASE+"cholesterol-levels/"},
])

# CBC cells and indices use context + unit to distinguish percentages from absolute counts.
CBC_REFERENCE = MEDLINEPLUS_BASE + "complete-blood-count-cbc/"
DIFF_REFERENCE = MEDLINEPLUS_BASE + "blood-differential/"
for _key, _es, _en, _aliases, _unit, _url in [
    ("wbc_count","Leucocitos","White blood cell count",["leucocitos","white blood count","wbc"],"10³/µL",CBC_REFERENCE),
    ("rbc_count","Eritrocitos","Red blood cell count",["eritrocitos","red blood cell count","rbc"],"10⁶/µL",CBC_REFERENCE),
    ("hemoglobin","Hemoglobina","Hemoglobin",["hemoglobina","hemoglobin","hgb"],"g/dL",MEDLINEPLUS_BASE+"hemoglobin-test/"),
    ("hematocrit","Hematócrito","Hematocrit",["hematócrito","hematocrito","hematocrit","hct"],"%",MEDLINEPLUS_BASE+"hematocrit-test/"),
    ("mcv","Volumen corpuscular medio (VCM)","Mean corpuscular volume (MCV)",["volumen corp. medio","volumen corpuscular medio","mcv"],"fL",MEDLINEPLUS_BASE+"mcv-mean-corpuscular-volume/"),
    ("mch","Hemoglobina corpuscular media (HCM)","Mean corpuscular hemoglobin (MCH)",["hemoglobina corp. media","hemoglobina corpuscular media","mch"],"pg",CBC_REFERENCE),
    ("mchc","Concentración media de hemoglobina corpuscular (CHCM)","Mean corpuscular hemoglobin concentration (MCHC)",["conc. media de hemoglobina corp.","concentracion media de hemoglobina corpuscular","mchc"],"g/dL",CBC_REFERENCE),
    ("rdw_cv","RDW-CV","RDW-CV",["ancho de distrib. de eritrocitos (cv","rdw cv","rdw-cv"],"%",MEDLINEPLUS_BASE+"rdw-red-cell-distribution-width/"),
    ("rdw_sd","RDW-SD","RDW-SD",["ancho de distrib. de eritrocitos (sd","rdw sd","rdw-sd"],"fL",MEDLINEPLUS_BASE+"rdw-red-cell-distribution-width/"),
    ("platelet_count","Plaquetas","Platelet count",["plaquetas","platelets","platelet count"],"10³/µL",MEDLINEPLUS_BASE+"platelet-tests/"),
    ("mpv","Volumen plaquetario medio","Mean platelet volume (MPV)",["volumen plaquetario medio","mpv","mean platelet volume"],"fL",MEDLINEPLUS_BASE+"mpv-blood-test/"),
]:
    SEEDS.append({"key":_key,"es":_es,"en":_en,"aliases":_aliases,"specimen":"Blood","unit":_unit,"url":_url})

SEEDS.append({"key":"band_neutrophil_percent","es":"Neutrófilos en banda (%)","en":"Band neutrophils (%)","aliases":["en banda","neutrofilos en banda","neutrófilos en banda","band neutrophils","bands"],"specimen":"Blood","unit":"%","url":DIFF_REFERENCE})

for _cell_es, _cell_en, _base in [
    ("Neutrófilos","Neutrophils","neutrophil"),
    ("Linfocitos","Lymphocytes","lymphocyte"),
    ("Monocitos","Monocytes","monocyte"),
    ("Eosinófilos","Eosinophils","eosinophil"),
    ("Basófilos","Basophils","basophil"),
]:
    SEEDS.append({"key":f"{_base}_percent","es":f"{_cell_es} (%)","en":f"{_cell_en} (%)","aliases":[_cell_es,_cell_en],"specimen":"Blood","unit":"%","url":DIFF_REFERENCE})
    SEEDS.append({"key":f"{_base}_absolute","es":f"{_cell_es} absolutos","en":f"Absolute {_cell_en.lower()}","aliases":[_cell_es,_cell_en],"specimen":"Blood","unit":"10³/µL","url":DIFF_REFERENCE})


# Additional cross-laboratory aliases observed in scanned reports. These are only exact
# semantic synonyms; OCR noise or ambiguous terms still remain provisional for review.
_EXTRA_ALIASES = {
    "wbc_count": ["globulos blancos", "glóbulos blancos"],
    "rbc_count": ["globulos rojos", "glóbulos rojos"],
    "mch": ["hb corpuscular media"],
    "mchc": ["concentracion media de hb", "concentración media de hb"],
    "rdw_cv": ["rdw", "ancho dist. eritrocitos"],
    "neutrophil_percent": ["segmentados", "neutrofilos %", "neutrófilos %"],
    "neutrophil_absolute": ["segmentados #", "segmentados +", "neutrofilos absolutos", "neutrófilos absolutos"],
    "lymphocyte_absolute": ["linfocitos #", "linfocitos +", "linfocitos absolutos"],
    "monocyte_absolute": ["monocitos #", "monocitos +", "monocitos absolutos"],
    "eosinophil_absolute": ["eosinofilos #", "eosinófilos #", "eosinofilos +", "eosinofilos absolutos", "eosinófilos absolutos"],
    "basophil_absolute": ["basofilos #", "basófilos #", "basofilos +", "basofilos absolutos", "basófilos absolutos"],
    "urine_ketones": ["cuerpos cetonicos", "cuerpos cetónicos"],
    "urine_blood": ["sangre"],
    "urine_epithelial_cells": ["epitelio plano uretra", "epitelio plano (uretra)", "celulas epiteliales", "células epiteliales", "celulas renales", "células renales"],
    "urine_mucus": ["filamentos de mucina"],
    "urinalysis_general": ["piocitos"],
}
for _item in SEEDS:
    _item["aliases"] = list(dict.fromkeys(_item.get("aliases", []) + _EXTRA_ALIASES.get(_item["key"], [])))

def seed_index() -> dict[str, list[dict[str, Any]]]:
    index: dict[str, list[dict[str, Any]]] = {}
    for item in SEEDS:
        for alias in dict.fromkeys(item["aliases"] + [item["es"], item["en"]]):
            bucket = index.setdefault(key_text(alias), [])
            if not any(existing["key"] == item["key"] for existing in bucket):
                bucket.append(item)
    return index


SEED_INDEX = seed_index()


def choose_seed(raw_name: str, panel: str, raw_unit: str) -> dict[str, Any] | None:
    candidates = SEED_INDEX.get(key_text(raw_name), [])
    if not candidates:
        return None
    specimen = specimen_from_context(panel, raw_name)
    normalized = normalize_unit(raw_unit).display
    filtered = [c for c in candidates if c.get("specimen") in ("", specimen)]
    if filtered:
        candidates = filtered
    # If an alias has percentage/absolute variants, unit must agree.
    if len(candidates) > 1 and normalized:
        exact_unit = [c for c in candidates if c.get("unit") == normalized]
        if exact_unit:
            candidates = exact_unit
    return candidates[0] if len(candidates) == 1 else None


def fallback_reference(panel: str, specimen: str) -> str:
    p = key_text(panel)
    if specimen == "Urine":
        return "https://medlineplus.gov/urinalysis.html"
    if any(x in p for x in ("biometria", "hemograma", "cbc")):
        return MEDLINEPLUS_BASE + "complete-blood-count-cbc/"
    if any(x in p for x in ("hepatico", "liver")):
        return MEDLINEPLUS_BASE + "liver-function-tests/"
    if any(x in p for x in ("hierro", "iron")):
        return MEDLINEPLUS_BASE + "iron-tests/"
    if any(x in p for x in ("cardiovascular", "lipid")):
        return MEDLINEPLUS_BASE + "cholesterol-levels/"
    if any(x in p for x in ("renal", "quimica", "chemistry")):
        return MEDLINEPLUS_BASE + "comprehensive-metabolic-panel-cmp/"
    return MEDLINEPLUS_DIR
