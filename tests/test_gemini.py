import copy
import io
import json
import unittest
from unittest.mock import patch
import urllib.error

from ai_assessor import build_request, call_gemini, comparison, main, parse_response


class GeminiIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.requirements = [{"id": "BUYER-01", "description": "Annual reviews.",
                              "question_id": "review", "keyword": "annual"}]
        self.supplier = {"id": "fictional", "answers": {"review": "We review every two years."},
                         "expected": {"BUYER-01": "partly_met"}}
        self.assessment = {"assessments": [{"requirement_id": "BUYER-01", "status": "partly_met",
                                           "evidence_quote": "We review every two years.",
                                           "reason": "The frequency is insufficient."}]}
        self.response = {"candidates": [{"finishReason": "STOP", "content": {"parts": [
            {"text": json.dumps(self.assessment)}]}}], "usageMetadata": {"totalTokenCount": 100}}

    def test_request_excludes_answer_key_and_uses_schema(self):
        payload = build_request(self.requirements, self.supplier)
        supplied = json.loads(payload["contents"][0]["parts"][0]["text"])
        self.assertNotIn("expected", supplied)
        self.assertNotIn("keyword", supplied["requirements"][0])
        self.assertEqual(payload["generationConfig"]["responseMimeType"], "application/json")

    def test_rejects_truncated_and_blocked_outputs(self):
        for reason in ["MAX_TOKENS", "SAFETY"]:
            response = copy.deepcopy(self.response)
            response["candidates"][0]["finishReason"] = reason
            with self.assertRaises(ValueError):
                parse_response(response)
        with self.assertRaises(ValueError):
            parse_response({"candidates": []})

    def test_rejects_malformed_json(self):
        self.response["candidates"][0]["content"]["parts"][0]["text"] = "not JSON"
        with self.assertRaises(ValueError):
            parse_response(self.response)

    @patch("ai_assessor.urllib.request.urlopen")
    def test_transport_uses_header_for_key_and_parses_response(self, mock_open):
        mock_open.return_value.__enter__.return_value = io.BytesIO(json.dumps(self.response).encode())
        result, usage, latency = call_gemini(build_request(self.requirements, self.supplier),
                                           "dummy-test-key", "gemini-2.5-flash-lite")
        request = mock_open.call_args.args[0]
        self.assertNotIn("dummy-test-key", request.full_url)
        self.assertNotIn("dummy-test-key", request.data.decode())
        self.assertEqual(request.get_header("X-goog-api-key"), "dummy-test-key")
        self.assertEqual(result, self.assessment)
        self.assertEqual(usage["totalTokenCount"], 100)
        self.assertGreaterEqual(latency, 0)

    @patch("ai_assessor.urllib.request.urlopen")
    def test_rate_limit_has_safe_message_and_no_retry(self, mock_open):
        mock_open.side_effect = urllib.error.HTTPError(
            "https://example.invalid", 429, "dummy-test-secret", {}, io.BytesIO(b"dummy-test-secret"))
        with self.assertRaises(ValueError) as caught:
            call_gemini({}, "dummy-test-secret", "gemini-2.5-flash-lite")
        self.assertIn("Quota", str(caught.exception))
        self.assertNotIn("dummy-test-secret", str(caught.exception))
        self.assertEqual(mock_open.call_count, 1)

    def test_comparison_keeps_ai_and_baseline_separate(self):
        row = comparison(self.assessment["assessments"], self.requirements, self.supplier)[0]
        self.assertEqual(row["status"], "partly_met")
        self.assertEqual(row["baseline_status"], "unknown")
        self.assertEqual(row["expected"], "partly_met")

    @patch("ai_assessor.load_key", side_effect=AssertionError("Must not read key"))
    @patch("ai_assessor.urllib.request.urlopen", side_effect=AssertionError("Must not call API"))
    def test_dry_run_does_not_read_key_or_call_api(self, mock_open, mock_key):
        with patch("sys.stdout", new_callable=io.StringIO) as stdout:
            self.assertEqual(main(["--dry-run"]), 0)
        self.assertIn("no network requests", stdout.getvalue())
        mock_key.assert_not_called()
        mock_open.assert_not_called()


if __name__ == "__main__":
    unittest.main()
