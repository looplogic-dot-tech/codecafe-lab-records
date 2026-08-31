import unittest

from clinical_dictionary import choose_seed, convert_numeric, normalize_unit, specimen_from_context


class ClinicalDictionaryUnitTest(unittest.TestCase):
    def test_blood_and_urine_glucose_are_distinct(self):
        blood = choose_seed("Glucosa", "QUÍMICA INTEGRAL", "mg/dL")
        urine = choose_seed("Glucosa", "EXAMEN GENERAL DE ORINA / EXAMEN QUÍMICO", "mg/dL")
        self.assertEqual(blood["key"], "glucose_blood")
        self.assertEqual(urine["key"], "glucose_urine")

    def test_hemoglobin_context_is_distinct(self):
        blood = choose_seed("Hemoglobina", "BIOMETRÍA HEMÁTICA", "g/dL")
        urine = choose_seed("Hemoglobina", "EXAMEN GENERAL DE ORINA / EXAMEN QUÍMICO", "eri/uL")
        self.assertEqual(blood["key"], "hemoglobin")
        self.assertEqual(urine["key"], "urine_blood")

    def test_differential_percent_and_absolute_are_distinct(self):
        percent = choose_seed("Neutrófilos", "BIOMETRÍA HEMÁTICA", "%")
        absolute = choose_seed("Neutrófilos", "BIOMETRÍA HEMÁTICA", "miles/µL")
        self.assertEqual(percent["key"], "neutrophil_percent")
        self.assertEqual(absolute["key"], "neutrophil_absolute")

    def test_safe_glucose_conversion(self):
        value, unit, ucum, status = convert_numeric("glucose_blood", 5.55, "mmol/L")
        self.assertAlmostEqual(value, 99.999, places=2)
        self.assertEqual(unit, "mg/dL")
        self.assertEqual(ucum, "mg/dL")
        self.assertEqual(status, "converted")

    def test_unit_aliases_are_homologated(self):
        self.assertEqual(normalize_unit("meq/L").display, "mEq/L")
        self.assertEqual(normalize_unit("g/dL (%)").display, "g/dL")
        self.assertEqual(normalize_unit("miles/µL").display, "10³/µL")
        self.assertEqual(normalize_unit("millones/µL").display, "10⁶/µL")

    def test_unknown_unit_is_preserved_not_guessed(self):
        rule = normalize_unit("custom-units")
        self.assertEqual(rule.display, "custom-units")
        self.assertEqual(rule.ucum, "")

    def test_specimen_context(self):
        self.assertEqual(specimen_from_context("EXAMEN GENERAL DE ORINA", "pH"), "Urine")
        self.assertEqual(specimen_from_context("BIOMETRÍA HEMÁTICA", "Hemoglobina"), "Blood")
        self.assertEqual(specimen_from_context("FUNCIÓN RENAL", "Creatinina"), "Serum")

    def test_uroculture_canonical_mapping_uses_urine_context(self):
        from clinical_dictionary import choose_seed
        seed = choose_seed("Cultivo", "UROCULTIVO + CULTIVO", "")
        self.assertIsNotNone(seed)
        self.assertEqual(seed["key"], "urine_culture")
        self.assertIn("bacteria-culture-test", seed["url"])


if __name__ == "__main__":
    unittest.main()
