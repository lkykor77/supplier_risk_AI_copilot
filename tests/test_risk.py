import unittest
from risk_scoring import summarize_risk

class RiskTests(unittest.TestCase):
    def setUp(self):
        self.rows = [{"requirement_id": key, "review": {"status": status}}
                     for key, status in [("a", "met"), ("b", "partly_met"), ("c", "missing"), ("d", "unknown")]]

    def test_score_separates_unknown_from_confirmed_gap(self):
        result = summarize_risk(self.rows)
        self.assertEqual(result["score"], 62.5)
        self.assertEqual(result["confirmed_gap_points"], 37.5)
        self.assertEqual(result["unresolved_evidence_points"], 25)
        self.assertEqual(result["unknown_count"], 1)

    def test_no_score_until_every_human_review(self):
        self.rows[0]["review"] = None
        result = summarize_risk(self.rows)
        self.assertFalse(result["ready"])
        self.assertNotIn("score", result)

    def test_all_met_zero_and_unknown_full_penalty(self):
        for row in self.rows: row["review"]["status"] = "met"
        self.assertEqual(summarize_risk(self.rows)["score"], 0)
        for row in self.rows: row["review"]["status"] = "unknown"
        result = summarize_risk(self.rows)
        self.assertEqual(result["score"], 100)
        self.assertEqual(result["confirmed_gap_points"], 0)
        self.assertEqual(result["unresolved_evidence_points"], 100)

    def test_criticality_changes_triage_not_arbitrary_numeric_score(self):
        normal, critical = summarize_risk(self.rows), summarize_risk(self.rows, "critical")
        self.assertEqual(normal["score"], critical["score"])
        self.assertFalse(normal["enhanced_review"])
        self.assertTrue(critical["enhanced_review"])
        self.assertEqual(len(critical["findings"]), 3)
        for row in self.rows: row["review"]["status"] = "met"
        self.assertFalse(summarize_risk(self.rows, "critical")["enhanced_review"])

    def test_invalid_classification_and_status_rejected(self):
        with self.assertRaises(ValueError): summarize_risk(self.rows, 'low')
        self.rows[0]["review"]["status"] = "approved"
        with self.assertRaises(ValueError): summarize_risk(self.rows)
