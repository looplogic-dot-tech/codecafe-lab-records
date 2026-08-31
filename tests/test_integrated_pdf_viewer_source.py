from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class IntegratedPdfViewerSourceTests(unittest.TestCase):
    def test_backend_has_internal_page_renderer(self):
        text = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn('@app.get("/pdf-page/<int:document_id>/<int:page_number>")', text)
        self.assertIn('page.get_pixmap', text)

    def test_frontend_uses_internal_page_images_not_pdf_iframe(self):
        text = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
        self.assertIn('/pdf-page/${d.id}/${i+1}', text)
        self.assertNotIn('<iframe title="PDF" src="/pdf/', text)

if __name__ == "__main__":
    unittest.main()
