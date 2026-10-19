"""Provider-independent request data and validation for AI assessments."""

STATUSES = {"met", "partly_met", "missing", "unknown"}


def assessment_input(requirements, supplier):
    """Keep expected labels and keyword rules out of the model's input."""
    return {
        "supplier_id": supplier["id"],
        "requirements": [
            {"id": r["id"], "description": r["description"],
             "answer": supplier["answers"].get(r["question_id"], "")}
            for r in requirements
        ],
    }


def validate_assessment(result, requirements, supplier):
    """Reject incomplete results and fabricated quotes; do not certify meaning."""
    if not isinstance(result, dict) or set(result) != {"assessments"}:
        raise ValueError("Result must contain only an assessments list.")
    rows = result["assessments"]
    if not isinstance(rows, list) or len(rows) != len(requirements):
        raise ValueError("Expected exactly one assessment per requirement.")
    by_id = {r["id"]: r for r in requirements}
    seen = set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != {
            "requirement_id", "status", "evidence_quote", "reason"
        }:
            raise ValueError("Each assessment needs an ID, status, quote, and reason.")
        if not all(isinstance(v, str) for v in row.values()):
            raise ValueError("Assessment fields must be strings.")
        rid = row["requirement_id"]
        if rid not in by_id or rid in seen:
            raise ValueError("Unknown or duplicate requirement ID.")
        seen.add(rid)
        if row["status"] not in STATUSES or not row["reason"].strip():
            raise ValueError("Invalid status or empty reason.")
        answer = supplier["answers"].get(by_id[rid]["question_id"], "")
        quote = row["evidence_quote"]
        if quote and (not quote.strip() or quote not in answer):
            raise ValueError(f"{rid}: evidence quote is not verbatim in the answer.")
        if not answer.strip():
            if row["status"] != "unknown" or quote:
                raise ValueError(f"{rid}: a blank answer must be unknown with no quote.")
        elif not quote.strip():
            raise ValueError(f"{rid}: a nonblank answer needs an exact evidence quote.")
    return rows
