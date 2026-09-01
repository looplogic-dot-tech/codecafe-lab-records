import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ReviewCorrectionSourceTest(unittest.TestCase):
    def test_v612_backend_has_review_and_advanced_edit_routes(self):
        source = (ROOT / "app_v612.py").read_text(encoding="utf-8")
        ast.parse(source)
        self.assertIn('/api/documents/<int:document_id>/review-results', source)
        self.assertIn('/api/observations/<int:observation_id>/edit', source)
        self.assertIn('observation_corrections', source)
        self.assertIn('manual_corrected', source)

    def test_review_layer_is_loaded_after_stable_app(self):
        html = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
        self.assertLess(html.index("app.js"), html.index("v612_review.js"))
        self.assertIn("v612_review.css", html)

    def test_review_ui_supports_edit_before_confirm_and_later_advanced_edit(self):
        js = (ROOT / "static" / "v612_review.js").read_text(encoding="utf-8")
        self.assertIn("v612SaveReviewCorrections", js)
        self.assertIn("confirmAndSave", js)
        self.assertIn("data-edit-result", js)
        self.assertIn("ocrCorrectionNotice", js)


if __name__ == "__main__":
    unittest.main()
