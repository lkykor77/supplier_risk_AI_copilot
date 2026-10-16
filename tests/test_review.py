import hashlib
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
import urllib.error
import urllib.request

from review_app import make_handler
from review_store import ReviewConflict, ReviewStore


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.requirements = [{"id": "BUYER-01", "description": "Annual reviews.", "question_id": "review"}]
        self.suppliers = [{"id": "fictional", "answers": {"review": "We review access regularly."},
                           "expected": {"BUYER-01": "unknown"}}]
        self.loader = patch("review_store.load_inputs", return_value=(self.requirements, self.suppliers))
        self.loader.start()
        self.report = {"complete": True, "dataset": "development", "model": "test-model",
                       "created_at": "2026-10-14T00:00:00+00:00",
                       "dataset_sha256": hashlib.sha256(json.dumps([self.requirements, self.suppliers], sort_keys=True).encode()).hexdigest(),
                       "suppliers": [{"supplier_id": "fictional", "assessments": [{"requirement_id": "BUYER-01",
                        "status": "met", "evidence_quote": "We review access regularly.", "reason": "An intentionally incorrect fixture."}]}]}
        (self.root / "results").mkdir()
        self.source = self.root / "results/latest-ai-run.json"
        self.source.write_text(json.dumps(self.report))
        self.original = self.source.read_bytes()
        self.store = ReviewStore(self.root)
        self.run_id = self.store.catalog()[0]["id"]
        self.payload = {"revision": 0, "supplier_id": "fictional", "requirement_id": "BUYER-01",
                        "status": "unknown", "evidence_quote": "We review access regularly.",
                        "reason": "The frequency is unspecified.", "comment": "Missing frequency is insufficient evidence.",
                        "reviewer": "TEST FIXTURE"}

    def tearDown(self):
        self.loader.stop()
        self.temp.cleanup()

    def test_correction_preserves_original_and_persists_after_reload(self):
        result = self.store.save(self.run_id, self.payload)
        self.assertEqual(result["reviewed_count"], 1)
        self.assertEqual(self.source.read_bytes(), self.original)
        loaded = ReviewStore(self.root).read(self.run_id)
        row = loaded["suppliers"][0]["assessments"][0]
        self.assertEqual(row["ai"]["status"], "met")
        self.assertEqual(row["review"]["status"], "unknown")
        self.assertEqual(row["review"]["action"], "corrected")

    def test_supplier_class_persists_and_is_revision_audited(self):
        criteria = {"revision": 0, "supplier_id": "fictional", "reviewer": "TEST FIXTURE", "supplier_class": "critical"}
        self.store.save_supplier_class(self.run_id, criteria)
        with self.assertRaises(ReviewConflict):
            self.store.save(self.run_id, self.payload)
        self.payload["revision"] = 1
        self.store.save(self.run_id, self.payload)
        loaded = ReviewStore(self.root).read(self.run_id)
        risk = loaded["suppliers"][0]["risk"]
        self.assertTrue(risk["ready"])
        self.assertEqual(risk["score"], 100)
        self.assertTrue(risk["enhanced_review"])
        self.assertEqual(self.source.read_bytes(), self.original)
        criteria.update(revision=2, supplier_class="normal")
        result = self.store.save_supplier_class(self.run_id, criteria)
        self.assertEqual(len(result["classification_events"]), 2)
        self.assertEqual(result["classification_events"][1]["before"], "critical")
        self.assertFalse(result["suppliers"][0]["risk"]["enhanced_review"])

    def test_rejects_fabricated_quote_without_saving(self):
        self.payload["evidence_quote"] = "We review monthly."
        with self.assertRaises(ValueError):
            self.store.save(self.run_id, self.payload)
        self.assertEqual(self.store.read(self.run_id)["reviewed_count"], 0)

    def test_requires_reviewer_and_correction_note(self):
        for field in ["reviewer", "comment"]:
            payload = {**self.payload, field: ""}
            with self.assertRaises(ValueError):
                self.store.save(self.run_id, payload)

    def test_stale_tab_cannot_overwrite_newer_review(self):
        self.store.save(self.run_id, self.payload)
        with self.assertRaises(ReviewConflict):
            self.store.save(self.run_id, self.payload)
        self.assertEqual(len(self.store.read(self.run_id)["events"]), 1)

    def test_audit_history_keeps_previous_decision(self):
        self.store.save(self.run_id, self.payload)
        self.payload.update(revision=1, reason="The annual frequency cannot be established.")
        result = self.store.save(self.run_id, self.payload)
        self.assertEqual(len(result["events"]), 2)
        self.assertEqual(result["events"][1]["before"]["reason"], "The frequency is unspecified.")

    def test_snapshots_survive_latest_report_overwrite(self):
        self.source.unlink()
        self.assertEqual(self.store.catalog()[0]["id"], self.run_id)
        self.assertEqual(self.store.read(self.run_id)["suppliers"][0]["assessments"][0]["answer"], "We review access regularly.")

    def test_combined_run_replaces_choices_but_preserves_old_history(self):
        suppliers = self.suppliers + [{**self.suppliers[0], 'id':'fictional-2'}]
        combined = {**self.report, 'run_scope':'combined-fictional-development',
                    'context_mode':'selected-vault-notes', 'replaces_runs':[self.run_id],
                    'created_at':'2026-10-16T00:00:00+00:00',
                    'dataset_sha256':hashlib.sha256(json.dumps([self.requirements,suppliers],sort_keys=True).encode()).hexdigest(),
                    'suppliers':self.report['suppliers'] + [{**self.report['suppliers'][0],'supplier_id':'fictional-2'}]}
        path = self.root / 'results/latest-combined.json'
        path.write_text(json.dumps(combined))
        with patch('review_store.combined_development_inputs',return_value=(self.requirements,suppliers)):
            catalog = self.store.catalog()
            self.assertEqual(len(catalog),1)
            self.assertEqual(catalog[0]['count'],2)
            self.assertNotEqual(catalog[0]['id'],self.run_id)
            self.assertEqual(self.store.read(self.run_id)['meta']['id'],self.run_id)
            combined['complete']=False
            path.write_text(json.dumps(combined))
            # The immutable completed combined snapshot remains available.
            self.assertEqual(self.store.catalog()[0]['id'],catalog[0]['id'])

    def test_partial_combined_run_does_not_hide_previous_run(self):
        combined = {**self.report, 'run_scope':'combined-fictional-development',
                    'replaces_runs':[self.run_id]}
        (self.root / 'results/latest-combined.json').write_text(json.dumps(combined))
        suppliers = self.suppliers + [{**self.suppliers[0],'id':'fictional-2'}]
        with patch('review_store.combined_development_inputs',return_value=(self.requirements,suppliers)):
            self.assertEqual([r['id'] for r in self.store.catalog()],[self.run_id])

    def test_invalid_run_path_rejected(self):
        with self.assertRaises(ValueError):
            self.store.read("../.gemini-key")

    def test_failed_reports_not_offered_for_review(self):
        self.source.write_text(json.dumps({**self.report, "complete": False}))
        # Existing archived completed snapshot still appears; the failed file adds no run.
        self.assertEqual(len(self.store.catalog()), 1)

    def test_http_requires_same_origin_and_exposes_only_app_routes(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(self.store))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f"http://127.0.0.1:{server.server_port}"
        try:
            with urllib.request.urlopen(base + "/api/runs") as response:
                self.assertIn("frame-ancestors 'none'", response.headers["Content-Security-Policy"])
                self.assertEqual(len(json.load(response)), 1)
            with self.assertRaises(urllib.error.HTTPError) as caught:
                urllib.request.urlopen(base + "/.gemini-key")
            self.assertEqual(caught.exception.code, 404)
            body = json.dumps({**self.payload, "run_id": self.run_id}).encode()
            request = urllib.request.Request(base + "/api/review", data=body,
                                             headers={"Content-Type": "application/json", "X-Review-App": "1", "Origin": "https://example.com"})
            with self.assertRaises(urllib.error.HTTPError) as caught:
                urllib.request.urlopen(request)
            self.assertEqual(caught.exception.code, 403)
            request = urllib.request.Request(base + "/api/review", data=body,
                                             headers={"Content-Type": "application/json", "X-Review-App": "1", "Origin": base})
            with urllib.request.urlopen(request) as response:
                self.assertEqual(json.load(response)["reviewed_count"], 1)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == "__main__":
    unittest.main()
