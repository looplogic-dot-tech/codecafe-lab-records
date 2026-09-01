import unittest

from glucose_filter import format_glucose_specimen_detail, glucose_context, glucose_lookup_name, is_glucose_name


class GlucoseFilterTest(unittest.TestCase):
    def test_common_lab_variants_use_generic_glucose_lookup(self):
        labels = [
            "Glucosa sérica basal",
            "Glucosa basal",
            "Glucosa en sangre",
            "Glucosa sanguínea",
            "Glucemia en ayunas",
            "Fasting glucose",
        ]
        for label in labels:
            with self.subTest(label=label):
                self.assertTrue(is_glucose_name(label))
                self.assertEqual(glucose_lookup_name(label, "QUÍMICA SANGUÍNEA", "Serum"), "Glucosa")

    def test_matrix_is_retained(self):
        self.assertEqual(glucose_context("Glucosa sérica basal", "", "Serum")["specimen_detail"], "Serum")
        self.assertEqual(glucose_context("Glucosa plasmática", "", "Serum")["specimen_detail"], "Plasma")
        self.assertEqual(glucose_context("Glucosa capilar", "", "Serum")["specimen_detail"], "Capillary blood")
        self.assertEqual(glucose_context("Glucosa en sangre", "", "Serum")["specimen_detail"], "Blood")

    def test_basal_and_curve_timepoint_are_retained(self):
        basal = glucose_context("Glucosa sérica basal", "", "Serum")
        self.assertEqual(basal["collection_context"], "Basal/Ayuno")
        self.assertEqual(basal["timepoint_minutes"], 0)

        curve = glucose_context("Glucosa plasmática 2 h", "Curva de tolerancia", "Serum")
        self.assertEqual(curve["collection_context"], "120 min post carga")
        self.assertEqual(curve["timepoint_minutes"], 120)

    def test_urine_context_stays_explicit(self):
        urine = glucose_context("Glucosa", "EXAMEN GENERAL DE ORINA", "Urine")
        self.assertEqual(urine["specimen_detail"], "Urine")
        self.assertEqual(urine["collection_context"], "")
        self.assertIsNone(urine["timepoint_minutes"])

    def test_display_detail_contains_matrix_and_condition(self):
        detail = format_glucose_specimen_detail("Glucosa sérica basal", "", "Serum")
        self.assertIn("Serum", detail)
        self.assertIn("Basal/Ayuno", detail)
        self.assertIn("t=0 min", detail)


if __name__ == "__main__":
    unittest.main()
