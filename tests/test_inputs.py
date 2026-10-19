import unittest
from unittest.mock import patch
from assessment_inputs import build_request, load_inputs, combined_development_inputs

class InputTests(unittest.TestCase):
    def test_schema_and_model_input_exclude_answer_key(self):
        requirements, suppliers = load_inputs("evaluation")
        for supplier in suppliers:
            request = build_request(requirements, supplier)
            self.assertEqual(set(request), {"task", "schema"})
            self.assertEqual(set(request["task"]), {"supplier_id", "requirements"})
            for item in request["task"]["requirements"]:
                self.assertEqual(set(item), {"id", "description", "answer"})
            self.assertEqual(request["schema"]["type"], "object")

    def test_frozen_prompt_change_is_rejected(self):
        with patch("assessment_inputs.PROMPT", "Changed"):
            with self.assertRaisesRegex(ValueError, "Frozen evaluation inputs changed"):
                load_inputs("evaluation")

    def test_combined_development_has_six_suppliers(self):
        questions, suppliers = combined_development_inputs()
        self.assertEqual(len(questions) * len(suppliers), 30)
        self.assertEqual(len({s["id"] for s in suppliers}), 6)
