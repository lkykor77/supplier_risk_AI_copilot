import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from ai_assessor import PROMPT
from local_assessor import DEFAULTS, NoRedirect, checked_url, local_payload, main, parse_local
from vault_context import load_context, note_path, save_memory


class LocalTests(unittest.TestCase):
    def setUp(self):
        self.requirements = [{"id": "BUYER-01", "description": "Security contact.",
                              "question_id": "contact", "keyword": "security@"}]
        self.supplier = {"id": "example", "answers": {"contact": "No contact exists."},
                         "expected": {"BUYER-01": "missing"}, "expected_reasons": {"BUYER-01": "Absent"}}

    def test_original_prompt_and_private_answer_key_separation(self):
        payload, prompt = local_payload(self.requirements, self.supplier, DEFAULTS)
        self.assertEqual(prompt, PROMPT)
        data = json.loads(payload["messages"][1]["content"])
        self.assertEqual(set(data), {"supplier_id", "requirements"})
        self.assertEqual(set(data["requirements"][0]), {"id", "description", "answer"})
        self.assertTrue(payload["response_format"]["json_schema"]["strict"])
        self.assertEqual(payload["reasoning_effort"], "none")

    def test_vault_context_changes_prompt_and_remains_separate_from_supplier_evidence(self):
        context = {"rules": [{"note": "rules.md", "text": "Be precise."}],
                   "knowledge": [{"note": "facts.md", "text": "Context"}], "memory": []}
        payload, prompt = local_payload(self.requirements, self.supplier, DEFAULTS, context)
        self.assertNotEqual(prompt, PROMPT)
        self.assertIn("take precedence", prompt)
        self.assertIn("reference_notes", json.loads(payload["messages"][1]["content"]))

    def test_loopback_only(self):
        self.assertEqual(checked_url("http://127.0.0.1:1234/v1"), "http://127.0.0.1:1234/v1")
        for url in ["https://example.com/v1", "http://localhost.evil/v1", "http://user:secret@localhost/v1",
                    "http://localhost/v1?key=secret", "http://localhost/other"]:
            with self.assertRaises(ValueError):
                checked_url(url)

    def test_redirects_refused(self):
        with self.assertRaises(ValueError):
            NoRedirect().redirect_request(None, None, 302, "", {}, "https://example.com")

    def test_parser_ignores_reasoning_and_rejects_truncation(self):
        result = {"assessments": []}
        response = {"choices": [{"finish_reason": "stop", "message": {
            "content": json.dumps(result), "reasoning_content": "Not JSON"}}]}
        self.assertEqual(parse_local(response), result)
        response["choices"][0]["finish_reason"] = "length"
        with self.assertRaises(ValueError):
            parse_local(response)
        response["choices"][0]["finish_reason"] = "stop"
        response["choices"][0]["message"]["content"] = ""
        response["choices"][0]["message"]["reasoning_content"] = json.dumps(result)
        with self.assertRaisesRegex(ValueError, "no final assessment"):
            parse_local(response)

    @patch("local_assessor.read_config", return_value=DEFAULTS)
    @patch("local_assessor.request_json", side_effect=AssertionError("Must not call server"))
    def test_vault_cannot_contaminate_frozen_evaluation(self, mock_request, mock_config):
        with self.assertRaises(SystemExit):
            main(["--dataset", "evaluation", "--with-vault"])
        mock_request.assert_not_called()


class VaultTests(unittest.TestCase):
    def test_allowlist_hashes_and_path_containment(self):
        with tempfile.TemporaryDirectory() as folder:
            vault = Path(folder)
            (vault / "rules.md").write_text("Be precise.")
            (vault / "unselected.md").write_text("Do not load this.")
            context, sources = load_context({"vault_path": folder, "rule_notes": ["rules.md"]})
            self.assertEqual(len(context["rules"]), 1)
            self.assertEqual(len(sources), 1)
            self.assertEqual(len(sources[0]["sha256"]), 64)
            with self.assertRaises(ValueError):
                note_path(vault, "../outside.md")
            (vault / "escape.md").symlink_to(vault.parent / "outside.md")
            with self.assertRaises(ValueError):
                note_path(vault, "escape.md")

    def test_memory_preserves_existing_user_note(self):
        with tempfile.TemporaryDirectory() as folder:
            vault = Path(folder)
            (vault / "user.md").write_text("My own note")
            config = {"vault_path": folder, "project_memory_note": "user.md"}
            with self.assertRaises(ValueError):
                save_memory(config, {})
            self.assertEqual((vault / "user.md").read_text(), "My own note")

    def test_completed_run_saves_only_concise_memory_and_history(self):
        with tempfile.TemporaryDirectory() as folder:
            config = {"vault_path": folder}
            report = {"complete": True, "created_at": "2026-10-13", "model": "qwen",
                      "dataset": "development", "context_mode": "original-frozen-prompt",
                      "prompt_sha256": "abc", "run_id": "test-run",
                      "summary": {"total": 5, "ai_correct": 4, "baseline_correct": 2},
                      "private_text": "PRIVATE-NOTE-CONTENT"}
            path = save_memory(config, report)
            self.assertIn("4/5", path.read_text())
            self.assertNotIn("PRIVATE-NOTE-CONTENT", path.read_text())
            self.assertTrue((Path(folder) / "Supplier Risk Copilot/Run history/test-run.md").exists())


if __name__ == "__main__":
    unittest.main()
