import base64
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from pdf_mapping import pdf_requirements
from pdf_intake import PDFIntake, ROOT, extract_pdf
from review_store import ReviewStore


class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.text = "The supplier reviews all user access annually."
        self.extraction = {"pages": [{"page": 1, "native_text": self.text, "ocr_text": self.text,
                                      "text": self.text, "mode": "native", "warning": ""}],
                           "native_engine": "test", "ocr_engine": "test"}
        self.intake = PDFIntake(self.root, extractor=lambda path: self.extraction.copy())
        encoded = base64.b64encode(b"%PDF-1.4\nfictional test fixture").decode()
        self.document = self.intake.upload("fictional.pdf", encoded)
        requirements = pdf_requirements()
        self.payload = {"confirmed": True, "reviewer": "TEST FIXTURE",
                        "mappings": [{"requirement_id": r["id"], "answer": "", "pages": [],
                                      "modes": {}, "correction_note": ""} for r in requirements]}
        self.payload["mappings"][2].update(answer=self.text, pages=[1])

    def tearDown(self):
        self.temp.cleanup()

    def test_confirmation_required_and_mapping_has_no_expected_labels(self):
        self.payload["confirmed"] = False
        with self.assertRaises(ValueError):
            self.intake.confirm(self.document["id"], self.payload)
        self.payload["confirmed"] = True
        result = self.intake.confirm(self.document["id"], self.payload)
        mapping = json.loads((self.intake.folder(self.document["id"]) / ("mapping-" + result["mapping_id"] + ".json")).read_text())
        self.assertNotIn("expected", mapping["supplier"])
        self.assertEqual(mapping["provenance"]["BUYER-03"]["pages"], [1])

    def test_rejects_wrong_pages_and_invented_native_answer(self):
        self.payload["mappings"][2]["pages"] = [99]
        with self.assertRaises(ValueError):
            self.intake.confirm(self.document["id"], self.payload)
        self.payload["mappings"][2].update(pages=[1], answer="We test restores daily.")
        with self.assertRaises(ValueError):
            self.intake.confirm(self.document["id"], self.payload)

    def test_ocr_correction_requires_explanation_and_is_marked(self):
        self.payload["mappings"][2].update(answer="We review all user access each year.", modes={"1": "ocr"})
        with self.assertRaises(ValueError):
            self.intake.confirm(self.document["id"], self.payload)
        self.payload["mappings"][2]["correction_note"] = "Test fixture: corrected OCR after visual inspection."
        result = self.intake.confirm(self.document["id"], self.payload)
        mapping = json.loads((self.intake.folder(self.document["id"]) / ("mapping-" + result["mapping_id"] + ".json")).read_text())
        self.assertTrue(mapping["provenance"]["BUYER-03"]["ocr_corrected"])

    def test_no_evidence_needs_no_page_and_twenty_decisions(self):
        for row in self.payload['mappings']:
            row.update(answer='',pages=[])
        result = self.intake.confirm(self.document['id'], self.payload)
        saved = json.loads((self.intake.folder(self.document['id']) / ('mapping-' + result['mapping_id'] + '.json')).read_text())
        self.assertEqual(len(saved['requirements']), 20)
        self.assertTrue(all(not p['pages'] for p in saved['provenance'].values()))

    def test_multiple_verbatim_excerpts_are_accepted(self):
        self.payload['mappings'][2]['answer'] = 'The supplier reviews\n\nall user access annually.'
        self.intake.confirm(self.document['id'], self.payload)

    def test_no_path_traversal_or_non_pdf(self):
        with self.assertRaises(ValueError):
            self.intake.folder("../.gemini-key")
        with self.assertRaises(ValueError):
            self.intake.upload("file.pdf", base64.b64encode(b"not PDF").decode())

    def test_malformed_mappings_are_rejected(self):
        self.payload["mappings"][0] = None
        with self.assertRaises(ValueError):
            self.intake.confirm(self.document["id"], self.payload)
        self.payload["mappings"][0] = {"requirement_id": "BUYER-01", "answer": "", "pages": [], "modes": []}
        with self.assertRaises(ValueError):
            self.intake.confirm(self.document["id"], self.payload)

    def test_pdf_assessment_integrates_with_review_without_accuracy_key(self):
        confirmed = self.intake.confirm(self.document["id"], self.payload)
        requirements = pdf_requirements()
        rows = [{"requirement_id": r["id"], "status": "met" if r["id"] == "BUYER-03" else "unknown",
                 "evidence_quote": self.text if r["id"] == "BUYER-03" else "", "reason": "Test fixture explanation."}
                for r in requirements]
        response = {"choices": [{"finish_reason": "stop", "message": {"content": json.dumps({"assessments": rows})}}]}
        def respond(base, endpoint, payload, timeout):
            ids = {r["id"] for r in json.loads(payload["messages"][1]["content"])["requirements"]}
            return {"choices": [{"finish_reason": "stop", "message": {"content": json.dumps({"assessments": [r for r in rows if r["requirement_id"] in ids]})}}]}
        with patch("pdf_intake.request_json", side_effect=respond):
            result = self.intake.assess(self.document["id"], confirmed["mapping_id"])
        store = ReviewStore(self.root)
        self.assertEqual(store.catalog()[0]["id"], result["report_sha256"])
        run = store.read(result["report_sha256"])
        self.assertTrue(all(row["expected"] is None for row in run["suppliers"][0]["assessments"]))
        self.assertEqual(run["suppliers"][0]["assessments"][2]["pdf_source"]["pages"], [1])


class NativePDFTests(unittest.TestCase):
    @unittest.skipUnless(sys.platform == "darwin" and (ROOT / ".cache/ocr-languages/eng.traineddata.gz").exists(),
                         "macOS PDF/OCR setup is required for this integration test")
    def test_digital_and_image_only_pdf_text(self):
        text = extract_pdf(ROOT / "examples/fictional-questionnaire-text.pdf")["pages"][0]
        scan = extract_pdf(ROOT / "examples/fictional-questionnaire-scan.pdf")["pages"][0]
        self.assertGreater(len(text["native_text"]), 100)
        self.assertEqual(scan["native_text"], "")
        for page in [text, scan]:
            self.assertIn("BUYER-05", page["text"])
            self.assertIn("not documented", page["text"])
        self.assertEqual(scan["mode"], "ocr")


if __name__ == "__main__":
    unittest.main()
