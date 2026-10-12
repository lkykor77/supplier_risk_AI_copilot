"""Run a deliberately naive keyword baseline on fictional questionnaire data."""

import json
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"


def assess(answer, keyword):
    if not answer.strip():
        return "unknown"
    if keyword.casefold() in answer.casefold():
        return "met"
    return "unknown"


def main():
    requirements = json.loads((DATA / "requirements.json").read_text())
    suppliers = json.loads((DATA / "suppliers.json").read_text())
    correct = 0
    total = 0
    for supplier in suppliers:
        print(f"\nSupplier: {supplier['id']}")
        for requirement in requirements:
            answer = supplier["answers"].get(requirement["question_id"], "")
            predicted = assess(answer, requirement["keyword"])
            expected = supplier["expected"][requirement["id"]]
            matches = predicted == expected
            correct += int(matches)
            total += 1
            print(f"  {requirement['id']}: {predicted} | expected: {expected} | {'MATCH' if matches else 'MISMATCH'}")
            print(f"    Evidence: {answer if answer.strip() else '(no answer provided)'}")
    print(f"\nToy exercise: {correct}/{total} labels match the answer key.")
    print("Inspect the mismatches: keyword presence does not establish that a practice exists.")


if __name__ == "__main__":
    main()
