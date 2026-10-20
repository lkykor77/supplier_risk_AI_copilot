"""Publish only the explicitly fictional, no-vault RAG fixture into static assets."""

import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
report = json.loads((ROOT / "reports/rag-fictional-development-run.json").read_text())
assert report["provider"] == "local" and report["dataset"] == "rag"
assert (
    report["context_mode"] == "local-retrieved-evidence"
    and report.get("source_review") is None
)
assert report["rag"]["supplier_name"].startswith(
    "Fictional Supplier L · RAG development · "
)
allowed = {
    p.name: hashlib.sha256(p.read_bytes()).hexdigest()
    for p in (ROOT / "examples/rag").glob("*.pdf")
}
assert set(allowed) == {
    "supplier-l-security-policy.pdf",
    "supplier-l-questionnaire.pdf",
}
notes = {
    "BUYER-03": "Review cue: the policy requires annual reviews; it does not prove that they happen. The operational response states a two-year contractor cycle. Consider whether Partly met better describes that explicit frequency gap. The saved suggestion remains unchanged.",
    "BUYER-08": "Review cue: no response is an evidence gap, not an explicit absence of workstation safeguards. Under this project rubric the analyst should correct Missing to Unknown. This annotation is a draft rubric review, not independent analyst validation.",
}
questions = []
for row in report["suppliers"][0]["assessments"]:
    rid = row["requirement_id"]
    retrieval = report["rag"]["retrievals"][rid]
    sources = report["rag"]["citations"][rid]
    for p in retrieval["passages"]:
        assert (
            allowed.get(p["filename"]) == p["document_id"]
        ), "Only included fictional source PDFs may be published."
    for c in sources:
        assert any(
            c["id"] == p["id"] and c["quote"] in p["text"]
            for p in retrieval["passages"]
        )
    questions.append(
        {
            "id": rid,
            "label": "Question-" + rid.split("-")[1] + " · " + retrieval["question"],
            "assessment": row,
            "passages": retrieval["passages"],
            "citations": sources,
            "review_note": notes.get(rid, ""),
        }
    )
order = ["BUYER-03", "BUYER-08", "BUYER-05", "BUYER-17"]
questions.sort(
    key=lambda q: (
        order.index(q["id"]) if q["id"] in order else 100 + int(q["id"].split("-")[1])
    )
)
(ROOT / "showcase/rag-demo.json").write_text(
    json.dumps(
        {"kind": "actual-saved-local-development-run", "questions": questions}, indent=2
    )
    + "\n"
)
target = ROOT / "showcase/assets/rag"
target.mkdir(exist_ok=True)
for name in allowed:
    shutil.copyfile(ROOT / "examples/rag" / name, target / name)
print(
    "Built fictional RAG demo with",
    len(questions),
    "saved questions and",
    len(allowed),
    "source PDFs.",
)
