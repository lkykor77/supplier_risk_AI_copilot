import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from rag import EvidenceStore, chunk_document, digest, ranked, vector, embed
from review_store import ReviewStore


def document(text, name="supplier-policy.pdf", page=1):
    return {
        "id": hashlib.sha256((name + text).encode()).hexdigest(),
        "filename": name,
        "pages": [
            {"page": page, "mode": "native", "native_text": text, "ocr_text": ""}
        ],
    }


class RAGTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.config = {
            "base_url": "http://127.0.0.1:1234/v1",
            "model": "test-local",
            "timeout_seconds": 10,
            "max_tokens": 4096,
            "temperature": 0,
            "top_p": 1,
            "top_k": 20,
            "presence_penalty": 0,
            "reasoning_effort": "none",
        }
        self.calls = []
        self.store = EvidenceStore(
            self.root, requester=self.request, config_reader=lambda: self.config
        )
        self.case = self.store.create("Fictional supplier")

    def tearDown(self):
        self.temp.cleanup()

    def request(self, base, endpoint, payload, timeout):
        self.calls.append((endpoint, payload))
        if endpoint == "/embeddings":
            return {
                "data": [
                    {"index": i, "embedding": [1, 0]}
                    for i, _ in enumerate(payload["input"])
                ]
            }
        task = json.loads(payload["messages"][1]["content"])
        p = task["retrieved_passages"][0]
        row = {
            "requirement_id": task["requirements"][0]["id"],
            "status": "unknown",
            "evidence_quote": p["text"][:80],
            "reason": "This fixture does not establish the full practice.",
            "citations": [{"passage_id": p["id"], "quote": p["text"][:80]}],
        }
        return {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"content": json.dumps({"assessments": [row]})},
                }
            ]
        }

    def test_passages_preserve_page_text_and_version(self):
        doc = document("access reviews " * 200)
        chunks = chunk_document(doc)
        self.assertGreater(len(chunks), 1)
        self.assertTrue(
            all(
                c["text"] in doc["pages"][0]["native_text"] and c["page"] == 1
                for c in chunks
            )
        )
        self.assertNotEqual(
            chunks[0]["id"], chunk_document(document("changed"))[0]["id"]
        )

    def test_layout_whitespace_is_normalized_without_rewriting_words(self):
        chunks = chunk_document(
            document("Annual access\nreviews include\ncontractors.")
        )
        self.assertEqual(
            chunks[0]["text"], "Annual access reviews include contractors."
        )
        self.assertEqual(len(chunk_document(document("x " * 480))), 1)

    def test_other_supplier_text_never_enters_search_or_ranking_statistics(self):
        self.store.add(
            self.case["id"], document("The supplier reviews user access annually.")
        )
        first = self.store.search(self.case["id"], "BUYER-03")
        other = self.store.create("Other supplier")
        self.store.add(
            other["id"],
            document("user access annually OTHER_SUPPLIER_ONLY " * 100, "other.pdf"),
        )
        later = self.store.search(self.case["id"], "BUYER-03")
        self.assertEqual(first, later)
        self.assertNotIn("OTHER_SUPPLIER_ONLY", json.dumps(later))

    def test_no_match_is_empty_and_generation_unknown(self):
        self.store.add(self.case["id"], document("zebras planets galaxies"))
        self.assertEqual(self.store.search(self.case["id"], "BUYER-03")["passages"], [])
        result = self.store.assess(self.case["id"])
        run = (
            ReviewStore(self.root).read(result["report_sha256"])
            if ReviewStore(self.root).catalog()
            else None
        )
        self.assertIsNotNone(run)
        self.assertEqual(len(run["suppliers"][0]["assessments"]), 20)
        self.assertTrue(
            all(
                r["ai"]["status"] == "unknown" and not r["ai"]["evidence_quote"]
                for r in run["suppliers"][0]["assessments"]
            )
        )
        self.assertFalse(run["suppliers"][0]["risk"]["ready"])
        self.assertEqual(self.calls, [])

    def test_dense_retrieval_can_recover_a_no_keyword_passage(self):
        chunks = chunk_document(document("Permissions are checked each January."))
        chunks[0]["vector"] = [1, 0]
        self.assertEqual(ranked(chunks, "annual access review"), [])
        self.assertEqual(
            ranked(chunks, "annual access review", [1, 0])[0]["id"], chunks[0]["id"]
        )

    def test_embeddings_are_local_explicit_and_nomic_prefixes_are_distinct(self):
        case = self.store.create("Hybrid", "nomic-embed-text-v1.5")
        self.store.add(case["id"], document("Annual access reviews."))
        result = self.store.search(case["id"], "BUYER-03")
        self.assertEqual(result["retrieval_mode"], "hybrid")
        self.assertTrue(self.calls[0][1]["input"][0].startswith("search_document: "))
        self.assertTrue(self.calls[1][1]["input"][0].startswith("search_query: "))

    def test_invalid_vectors_and_incomplete_embeddings_fail_closed(self):
        for v in [[float("nan")], [float("inf")], [0, 0], [True, 1], [1e308], []]:
            with self.assertRaises(ValueError):
                vector(v)
        with self.assertRaises(ValueError):
            embed(["a"], "local", self.config, lambda *a: {"data": []})
        case = self.store.create("Failing hybrid", "local-embedding")
        self.store.requester = lambda *a: (_ for _ in ()).throw(
            ValueError("Local server unavailable")
        )
        with self.assertRaises(ValueError):
            self.store.add(case["id"], document("annual access"))
        self.assertEqual(self.store.case(case["id"])["documents"], [])

    def test_validated_citations_survive_review_and_snapshot_does_not_change(self):
        self.store.add(
            self.case["id"], document("The supplier reviews user access annually.")
        )
        result = self.store.assess(self.case["id"])
        reviews = ReviewStore(self.root)
        reviews.catalog()
        before = reviews.read(result["report_sha256"])
        row = before["suppliers"][0]["assessments"][2]
        self.assertTrue(row["rag_sources"])
        self.assertIn(row["ai"]["evidence_quote"], row["rag_sources"][0]["text"])
        self.store.add(
            self.case["id"],
            document("We no longer perform access reviews.", "new-policy.pdf"),
        )
        self.assertEqual(before, reviews.read(result["report_sha256"]))
        saved = reviews.save(
            result["report_sha256"],
            {
                "revision": 0,
                "supplier_id": before["suppliers"][0]["id"],
                "requirement_id": row["requirement_id"],
                "reviewer": "TEST FIXTURE",
                "comment": "",
                **row["ai"],
            },
        )
        self.assertEqual(saved["reviewed_count"], 1)
        self.assertFalse(saved["suppliers"][0]["risk"]["ready"])

    def test_forged_citations_reject_entire_run(self):
        self.store.add(
            self.case["id"], document("The supplier reviews access annually.")
        )
        valid = self.request

        def forged(*args):
            r = valid(*args)
            if args[1] == "/chat/completions":
                content = json.loads(r["choices"][0]["message"]["content"])
                content["assessments"][0]["citations"][0][
                    "passage_id"
                ] = "other-supplier-id"
                r["choices"][0]["message"]["content"] = json.dumps(content)
            return r

        self.store.requester = forged
        with self.assertRaisesRegex(ValueError, "verbatim retrieved source"):
            self.store.assess(self.case["id"])
        self.assertEqual(ReviewStore(self.root).catalog(), [])

    def test_contradictions_are_both_in_prompt_and_other_suppliers_are_excluded(self):
        self.store.add(
            self.case["id"],
            document("All user access is reviewed annually.", "policy.pdf"),
        )
        self.store.add(
            self.case["id"],
            document(
                "Contractor user access is reviewed every two years.", "answers.pdf"
            ),
        )
        other = self.store.create("Other")
        self.store.add(
            other["id"], document("OTHER_ONLY annual user access review", "other.pdf")
        )
        self.store.assess(self.case["id"])
        payload = next(
            p
            for e, p in self.calls
            if e == "/chat/completions"
            and json.loads(p["messages"][1]["content"])["requirements"][0]["id"]
            == "BUYER-03"
        )
        text = payload["messages"][1]["content"]
        self.assertIn("annually", text)
        self.assertIn("two years", text)
        self.assertNotIn("OTHER_ONLY", text)

    def test_obsidian_guidance_is_not_indexed_or_treated_as_supplier_evidence(self):
        self.store.add(
            self.case["id"], document("The supplier reviews user access annually.")
        )
        context = {
            "rules": [{"text": "PRIVATE_GUIDANCE_MARKER"}],
            "knowledge": [],
            "memory": [],
        }
        with patch("rag.load_context", return_value=context):
            result = self.store.assess(self.case["id"], with_vault=True)
        payload = next(p for e, p in self.calls if e == "/chat/completions")
        self.assertIn("PRIVATE_GUIDANCE_MARKER", payload["messages"][0]["content"])
        self.assertNotIn(
            "PRIVATE_GUIDANCE_MARKER",
            json.dumps(self.store.search(self.case["id"], "BUYER-03")),
        )
        self.assertNotIn(
            "PRIVATE_GUIDANCE_MARKER",
            next(
                (self.root / "rag" / self.case["id"]).glob("assessment-run-*.json")
            ).read_text(),
        )

    def test_case_path_and_unknown_questions_are_rejected(self):
        for ident in ["../.env", "x", "", None]:
            with self.assertRaises(ValueError):
                self.store.case(ident)
        with self.assertRaises(ValueError):
            self.store.search(self.case["id"], "not-a-question")
