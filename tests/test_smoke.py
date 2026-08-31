import io
import os
import tempfile
import unittest
from unittest import mock

TMP = tempfile.TemporaryDirectory()
os.environ["CODECAFE_LAB_DATA"] = TMP.name

import app as labapp  # noqa: E402


class LabRecordsSmokeTest(unittest.TestCase):
    def setUp(self):
        self.client = labapp.app.test_client()

    def test_first_use_flow(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Registros Clínicos".encode("utf-8"), response.data)

        response = self.client.post(
            "/api/profiles",
            json={"name": "Synthetic Patient", "initials": "SP", "dob": "1970-01-01"},
        )
        self.assertEqual(response.status_code, 201)
        state = response.get_json()
        patient_id = state["activePatientId"]
        self.assertIsNotNone(patient_id)

        pdf = b"%PDF-1.4\n% synthetic test fixture\n%%EOF\n"
        response = self.client.post(
            "/api/documents",
            data={
                "patient_id": str(patient_id),
                "lab": "Synthetic Lab",
                "report_date": "2026-08-15",
                "study_type": "Synthetic panel",
                "specimen": "Serum",
                "file": (io.BytesIO(pdf), "synthetic.pdf"),
            },
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 201)
        document_id = response.get_json()["documentId"]

        response = self.client.post(
            "/api/observations",
            json={
                "patientId": patient_id,
                "documentId": document_id,
                "testName": "Synthetic analyte",
                "value": 11.2,
                "unit": "mg/dL",
                "referenceLow": 5,
                "referenceHigh": 10,
                "date": "2026-08-15",
                "lab": "Synthetic Lab",
            },
        )
        self.assertEqual(response.status_code, 201)
        state = response.get_json()
        self.assertEqual(len(state["documents"]), 1)
        self.assertEqual(len(state["observations"]), 1)

        response = self.client.get(f"/pdf/{document_id}")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data.startswith(b"%PDF"))

    def test_imported_results_use_canonical_test_id_not_alias_id(self):
        response = self.client.post(
            "/api/profiles",
            json={"name": "Import Regression Patient", "initials": "IR"},
        )
        patient_id = response.get_json()["activePatientId"]
        parsed = {
            "ok": True,
            "engine": "synthetic",
            "confidence": 0.99,
            "page_count": 1,
            "warnings": [],
            "metadata": {
                "lab": "Synthetic Lab",
                "report_date": "2026-08-15",
                "study_type": "Chemistry",
                "specimen": "Serum",
            },
            "observations": [
                {
                    "test_name": "Urea",
                    "raw_test_name": "Urea",
                    "value_numeric": 35.0,
                    "value_text": "35",
                    "unit": "mg/dL",
                    "reference_low": 16.6,
                    "reference_high": 48.5,
                    "reference_text": "16.6 - 48.5",
                    "panel": "FUNCIÓN RENAL",
                    "method": "",
                    "source_page": 1,
                    "extraction_confidence": 0.99,
                }
            ],
        }
        pdf = b"%PDF-1.4\n% synthetic import regression\n%%EOF\n"
        with mock.patch.object(labapp, "parse_lab_pdf", return_value=parsed):
            response = self.client.post(
                "/api/documents",
                data={
                    "patient_id": str(patient_id),
                    "file": (io.BytesIO(pdf), "import-regression.pdf"),
                    "import_results": "1",
                },
                content_type="multipart/form-data",
            )
        self.assertEqual(response.status_code, 201, response.get_data(as_text=True))
        self.assertEqual(response.get_json()["importedResults"], 1)
        state = response.get_json()["state"]
        imported = [o for o in state["observations"] if o["raw_test_name"] == "Urea"]
        self.assertEqual(len(imported), 1)
        self.assertEqual(imported[0]["canonical_key"], "urea")


    def test_text_size_setting(self):
        response = self.client.post("/api/settings", json={"textSize": "xlarge"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["textSize"], "xlarge")

    def test_daily_measurements_flow(self):
        response = self.client.post(
            "/api/profiles",
            json={"name": "Readings Patient", "initials": "RP"},
        )
        patient_id = response.get_json()["activePatientId"]

        response = self.client.post(
            "/api/measurements",
            json={
                "patientId": patient_id,
                "kind": "blood_pressure",
                "measuredAt": "2026-08-15T08:15",
                "systolic": 122,
                "diastolic": 78,
                "pulse": 67,
                "sourceType": "manual",
            },
        )
        self.assertEqual(response.status_code, 201)

        response = self.client.post(
            "/api/measurements",
            json={
                "patientId": patient_id,
                "kind": "glucose",
                "measuredAt": "2026-08-15T08:20",
                "glucoseValue": 5.5,
                "glucoseUnit": "mmol/L",
                "context": "fasting",
                "sourceType": "manual",
            },
        )
        self.assertEqual(response.status_code, 201)
        response = self.client.post(
            "/api/measurements",
            json={
                "patientId": patient_id,
                "kind": "weight",
                "measuredAt": "2026-08-15T08:25",
                "weightValue": 176.4,
                "weightUnit": "lb",
                "sourceType": "manual",
            },
        )
        self.assertEqual(response.status_code, 201)
        readings = [m for m in response.get_json()["dailyMeasurements"] if m["patient_id"] == patient_id]
        self.assertEqual(len(readings), 3)
        glucose = next(m for m in readings if m["kind"] == "glucose")
        self.assertAlmostEqual(glucose["glucose_mg_dl"], 99.1001, places=3)
        weight = next(m for m in readings if m["kind"] == "weight")
        self.assertAlmostEqual(weight["weight_kg"], 80.0137, places=3)


    def test_desktop_bulk_folder_analysis_and_import(self):
        response = self.client.post(
            "/api/profiles",
            json={"name": "Bulk Synthetic Patient", "initials": "BP"},
        )
        patient_id = response.get_json()["activePatientId"]
        parsed = {
            "ok": True,
            "engine": "synthetic-bulk",
            "confidence": 0.98,
            "page_count": 1,
            "warnings": [],
            "metadata": {
                "lab": "Synthetic Lab",
                "report_date": "2026-08-16",
                "study_type": "UROCULTIVO + CULTIVO",
                "specimen": "Orina",
                "patient_name": "Bulk Synthetic Patient",
            },
            "observations": [
                {
                    "test_name": "Cultivo",
                    "raw_test_name": "CULTIVO",
                    "value_numeric": None,
                    "value_text": "Sin desarrollo microbiano",
                    "unit": "",
                    "reference_low": None,
                    "reference_high": None,
                    "reference_text": "",
                    "panel": "UROCULTIVO + CULTIVO",
                    "method": "Cultivo bacteriológico",
                    "source_page": 1,
                    "extraction_confidence": 0.98,
                }
            ],
        }
        with tempfile.TemporaryDirectory() as folder:
            pdf_path = os.path.join(folder, "urocultivo-synthetic.pdf")
            with open(pdf_path, "wb") as fh:
                fh.write(b"%PDF-1.4\n% bulk synthetic\n%%EOF\n")
            with mock.patch.dict(os.environ, {"CODECAFE_DESKTOP_MODE": "1"}, clear=False), \
                 mock.patch.object(labapp, "parse_lab_pdf", return_value=parsed):
                analyzed = self.client.post(
                    "/api/documents/bulk/analyze-local",
                    json={"folder": folder, "recursive": False},
                )
                self.assertEqual(analyzed.status_code, 200, analyzed.get_data(as_text=True))
                body = analyzed.get_json()
                self.assertEqual(body["count"], 1)
                self.assertEqual(len(body["items"][0]["parsed"]["observations"]), 1)

                imported = self.client.post(
                    "/api/documents/bulk/import-local",
                    json={"patientId": patient_id, "paths": [pdf_path], "importResults": True},
                )
                self.assertEqual(imported.status_code, 200, imported.get_data(as_text=True))
                body = imported.get_json()
                self.assertEqual(body["importedDocuments"], 1)
                self.assertEqual(body["importedResults"], 1)
                cultures = [o for o in body["state"]["observations"] if o["raw_test_name"] == "CULTIVO"]
                self.assertEqual(len(cultures), 1)
                self.assertEqual(cultures[0]["value_text"], "Sin desarrollo microbiano")


if __name__ == "__main__":
    unittest.main()
