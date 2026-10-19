import copy
import unittest

from assessment import assessment_input, validate_assessment


class EvidenceValidationTests(unittest.TestCase):
    def setUp(self):
        self.requirements = [{"id": "BUYER-01", "description": "Annual reviews.",
                              "question_id": "review", "keyword": "annual"}]
        self.supplier = {"id": "fictional", "answers": {"review": "We review annually."},
                         "expected": {"BUYER-01": "met"}}
        self.result = {"assessments": [{"requirement_id": "BUYER-01", "status": "met",
                                       "evidence_quote": "We review annually.",
                                       "reason": "The frequency is annual."}]}

    def validate(self, result):
        return validate_assessment(result, self.requirements, self.supplier)

    def test_model_input_excludes_expected_labels_and_keyword_rules(self):
        payload = assessment_input(self.requirements, self.supplier)
        self.assertEqual(set(payload["requirements"][0]), {"id", "description", "answer"})
        self.assertNotIn("expected", payload)
        self.assertNotIn("expected", payload["requirements"][0])

    def test_accepts_verbatim_quote(self):
        self.assertEqual(self.validate(self.result), self.result["assessments"])

    def test_rejects_invented_quote(self):
        result = copy.deepcopy(self.result)
        result["assessments"][0]["evidence_quote"] = "We review monthly."
        with self.assertRaises(ValueError):
            self.validate(result)

    def test_rejects_quote_copied_from_another_answer(self):
        self.supplier["answers"]["unrelated"] = "We review monthly."
        self.result["assessments"][0]["evidence_quote"] = "We review monthly."
        with self.assertRaises(ValueError):
            self.validate(self.result)

    def test_rejects_duplicate_or_omitted_requirements(self):
        with self.assertRaises(ValueError):
            self.validate({"assessments": []})
        self.requirements.append({"id": "BUYER-02", "description": "Other practice.",
                                  "question_id": "other", "keyword": "other"})
        self.result["assessments"].append(copy.deepcopy(self.result["assessments"][0]))
        with self.assertRaises(ValueError):
            self.validate(self.result)

    def test_blank_answer_cannot_be_met(self):
        self.supplier["answers"]["review"] = ""
        self.result["assessments"][0]["evidence_quote"] = ""
        with self.assertRaises(ValueError):
            self.validate(self.result)
        self.result["assessments"][0]["status"] = "unknown"
        self.assertEqual(len(self.validate(self.result)), 1)


if __name__ == "__main__":
    unittest.main()
