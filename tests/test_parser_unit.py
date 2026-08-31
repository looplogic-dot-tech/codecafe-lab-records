import unittest

from lab_pdf_parser import match_metadata, parse_ocr_rows, parse_reference, parse_result_row, embedded_text_pages


def word(x, y, text, width=35):
    return (float(x), float(y), float(x + width), float(y + 10), text, 0, 0, 0)


class ParserUnitTest(unittest.TestCase):
    def test_numeric_range_row(self):
        row, consumed = parse_result_row("Glucosa                    111                    55 - 99 mg/dL")
        self.assertFalse(consumed)
        self.assertEqual(row["test_name"], "Glucosa")
        self.assertEqual(row["value_numeric"], 111.0)
        self.assertEqual(row["unit"], "mg/dL")
        self.assertEqual(row["reference_low"], 55.0)
        self.assertEqual(row["reference_high"], 99.0)

    def test_strict_comparator_is_preserved(self):
        row, _ = parse_result_row("Colesterol LDL directo     128                    < 100 mg/dL")
        self.assertEqual(row["reference_text"], "< 100")
        self.assertEqual(row["reference_high"], 100.0)

    def test_qualitative_urine_row(self):
        row, _ = parse_result_row("Nitritos                    Negativo               Negativo")
        self.assertIsNone(row["value_numeric"])
        self.assertEqual(row["value_text"], "Negativo")
        self.assertEqual(row["reference_text"], "Negativo")

    def test_comparators_and_ocr_range_separator(self):
        self.assertEqual(parse_reference("< 4.0"), (None, 4.0))
        self.assertEqual(parse_reference(">60"), (60.0, None))
        self.assertEqual(parse_reference("4.06 = 4.69"), (4.06, 4.69))
        self.assertEqual(parse_reference("7,00 - 25,00"), (7.0, 25.0))

    def test_adaptive_ocr_column_parser(self):
        words = [
            word(42, 100, "PRUEBA"), word(277, 100, "RESULTADO", 55),
            word(377, 100, "UNIDAD"), word(490, 100, "REFERENCIA", 65),
            word(42, 125, "Glucosa"), word(283, 125, "133.00"),
            word(382, 125, "mg/dL"), word(478, 125, "69.00"),
            word(513, 125, "-", 8), word(530, 125, "105.00"),
        ]
        pages = [{"page": 1, "text": "PRUEBA RESULTADO UNIDAD REFERENCIA\nGlucosa 133.00 mg/dL 69.00 - 105.00", "words": words, "width": 612, "height": 842}]
        headings, rows, _samples, warnings = parse_ocr_rows(pages)
        self.assertEqual(warnings, [])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["test_name"], "Glucosa")
        self.assertEqual(rows[0]["value_numeric"], 133.0)
        self.assertEqual(rows[0]["unit"], "mg/dL")
        self.assertEqual(rows[0]["reference_low"], 69.0)
        self.assertEqual(rows[0]["reference_high"], 105.0)

    def test_scanned_lab_metadata_heuristics(self):
        simi = match_metadata("""Unidad:\nF999-CENTRO 1\nCódigo:\n987654\nPaciente:\nPACIENTE PRUEBA UNO\nFecha:\n20 /nov./2024\nSexo:\nMASCULINO\nMédico:\nESTIMADO MÉDICO\nEXAMEN GENERAL DE ORINA""")
        self.assertEqual(simi["lab"], "SimiLab")
        self.assertEqual(simi["report_date"], "2024-11-20")
        self.assertEqual(simi["order_number"], "987654")

        imss = match_metadata("""HOSPITAL GENERAL DE ZONA/MEDICINA FAMILIAR No. 16\nLABORATORIO CLINICO\nPACIENTE:\nPACIENTE PRUEBA DOS\nNSS:\n0000000000\nFOLIO:\n9900112233\nFECHA DE INGRESO:\n21/07/2023 07:17:46 p. m.""")
        self.assertEqual(imss["lab"], "IMSS")
        self.assertEqual(imss["report_date"], "2023-07-21")
        self.assertEqual(imss["order_number"], "9900112233")

    def test_pymupdf_embedded_text_fallback_when_pypdf_is_unavailable(self):
        import io
        import unittest.mock as mock
        import pymupdf
        import lab_pdf_parser as parser

        doc = pymupdf.open()
        page = doc.new_page()
        page.insert_text((72, 72), "Glucosa 85 55 - 99 mg/dL")
        pdf_bytes = doc.tobytes()
        doc.close()

        with mock.patch.object(parser, "_pypdf_text_pages", side_effect=RuntimeError("simulated frozen-build failure")):
            layout, plain, engine, warnings = embedded_text_pages(pdf_bytes)
        self.assertEqual(engine, "pymupdf-native")
        self.assertIn("Glucosa", "\n".join(plain))
        self.assertTrue(any("PyMuPDF fallback" in w for w in warnings))

    def test_tessdata_discovery_finds_language_files(self):
        import tempfile
        import os
        import unittest.mock as mock
        import lab_pdf_parser as parser
        from pathlib import Path

        with tempfile.TemporaryDirectory() as td:
            Path(td, "eng.traineddata").write_bytes(b"x")
            with mock.patch.dict(os.environ, {"TESSDATA_PREFIX": td}, clear=False):
                self.assertEqual(parser._find_tessdata_dir(), td)

    def test_project_ships_self_contained_english_and_spanish_ocr_data(self):
        import lab_pdf_parser as parser
        status = parser.ocr_status()
        self.assertTrue(status["available"])
        self.assertTrue(status["eng"])
        self.assertTrue(status["spa"])

    def test_unit_before_reference_layout_is_supported(self):
        row, consumed = parse_result_row("Glucosa        85        mg/dL        55 - 99")
        self.assertFalse(consumed)
        self.assertEqual(row["test_name"], "Glucosa")
        self.assertEqual(row["value_numeric"], 85.0)
        self.assertEqual(row["unit"], "mg/dL")
        self.assertEqual(row["reference_low"], 55.0)
        self.assertEqual(row["reference_high"], 99.0)

    def test_split_result_header_still_opens_table(self):
        import lab_pdf_parser as parser
        page = "\n".join([
            "Prueba",
            "Bajo (LR)   Dentro (LR)   Sobre (LR)   Límites de referencia",
            "Glucosa        85        55 - 99 mg/dL",
        ])
        headings, rows, samples = parser.parse_layout_rows([page])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["test_name"], "Glucosa")

    def test_cross_platform_retry_chooses_engine_with_structured_rows(self):
        import unittest.mock as mock
        import lab_pdf_parser as parser

        bad_layout = ["Paciente: PRUEBA\nPrueba"]
        good_layout = ["\n".join([
            "Prueba",
            "Bajo (LR)   Dentro (LR)   Sobre (LR)   Límites de referencia",
            "Glucosa        85        mg/dL        55 - 99",
        ])]
        bundle = parser.ExtractionBundle(bad_layout, bad_layout, [], "pypdf-layout", [])
        with mock.patch.object(parser, "extract_document", return_value=bundle), \
             mock.patch.object(parser, "_pypdf_text_pages", return_value=(bad_layout, bad_layout)), \
             mock.patch.object(parser, "_pymupdf_text_pages", return_value=(good_layout, good_layout)), \
             mock.patch.object(parser, "ocr_document", return_value=([], [])):
            result = parser.parse_lab_pdf(b"synthetic")
        self.assertEqual(result["engine"], "pymupdf-positional")
        self.assertEqual(len(result["observations"]), 1)
        self.assertEqual(result["observations"][0]["test_name"], "Glucosa")

    def test_two_column_culture_result_without_reference_range(self):
        import lab_pdf_parser as parser
        row, consumed = parser.parse_result_row("CULTIVO                    Sin desarrollo microbiano")
        self.assertFalse(consumed)
        self.assertIsNotNone(row)
        self.assertEqual(row["test_name"], "Cultivo")
        self.assertEqual(row["value_text"], "Sin desarrollo microbiano")
        self.assertEqual(row["reference_text"], "")

    def test_uroculture_layout_recovers_qualitative_result(self):
        import lab_pdf_parser as parser
        page = "\n".join([
            "Prueba",
            "Bajo (LR)   Dentro (LR)   Sobre (LR)   Límites de referencia",
            "UROCULTIVO + CULTIVO",
            "CULTIVO                    Sin desarrollo microbiano",
            "Método:Cultivo bacteriológico en medios específicos",
        ])
        headings, rows, samples = parser.parse_layout_rows([page])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["panel"], "UROCULTIVO + CULTIVO")
        self.assertEqual(rows[0]["test_name"], "Cultivo")
        self.assertEqual(rows[0]["value_text"], "Sin desarrollo microbiano")

    def test_split_uroculture_result_is_recovered(self):
        import lab_pdf_parser as parser
        headings, rows = parser.parse_microbiology_qualitative_rows([
            "UROCULTIVO + CULTIVO\nCULTIVO\nSin desarrollo microbiano\nMétodo: Cultivo bacteriológico"
        ])
        self.assertIn("UROCULTIVO + CULTIVO", headings)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["test_name"], "Cultivo")
        self.assertEqual(rows[0]["value_text"], "Sin desarrollo microbiano")

    def test_microbiology_organism_and_colony_count_are_supported(self):
        import lab_pdf_parser as parser
        _headings, rows = parser.parse_microbiology_qualitative_rows([
            "UROCULTIVO\nMicroorganismo: Escherichia coli\nRecuento: 100000 UFC/mL"
        ])
        self.assertEqual(len(rows), 2)
        organism = next(x for x in rows if x["test_name"] == "Microorganismo")
        count = next(x for x in rows if x["test_name"] == "Recuento microbiológico")
        self.assertEqual(organism["value_text"], "Escherichia coli")
        self.assertEqual(count["value_text"], "100000")
        self.assertEqual(count["unit"], "UFC/mL")

    def test_uroculture_multiline_value_with_layout_noise_is_recovered(self):
        import lab_pdf_parser as parser
        headings, rows = parser.parse_microbiology_qualitative_rows([
            "UROCULTIVO + CULTIVO\nCULTIVO\n---\nSin\ndesarrollo\nmicrobiano\nMétodo: Cultivo bacteriológico"
        ])
        self.assertIn("UROCULTIVO + CULTIVO", headings)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["test_name"], "Cultivo")
        self.assertEqual(rows[0]["value_text"], "Sin desarrollo microbiano")

    def test_uroculture_qualitative_parser_tries_multiple_text_layouts(self):
        import unittest.mock as mock
        import lab_pdf_parser as parser
        bad = ["UROCULTIVO + CULTIVO\nCULTIVO\n---"]
        good = ["UROCULTIVO + CULTIVO\nCULTIVO\n---\nSin\ndesarrollo\nmicrobiano"]
        bundle = parser.ExtractionBundle(bad, bad, [], "pypdf-layout", [])
        with mock.patch.object(parser, "extract_document", return_value=bundle), \
             mock.patch.object(parser, "_pypdf_text_pages", return_value=(bad, bad)), \
             mock.patch.object(parser, "_pymupdf_text_pages", return_value=(good, good)), \
             mock.patch.object(parser, "ocr_document", return_value=([], [])):
            result = parser.parse_lab_pdf(b"synthetic")
        cultures = [x for x in result["observations"] if x["test_name"] == "Cultivo"]
        self.assertEqual(len(cultures), 1)
        self.assertEqual(cultures[0]["value_text"], "Sin desarrollo microbiano")


if __name__ == "__main__":
    unittest.main()
