"""Build a clean public sample, with a strict allowlist for sample-vault context."""

import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
allowed = {
    p.name: hashlib.sha256(p.read_bytes()).hexdigest()
    for p in (ROOT / "examples/rag").glob("*.pdf")
}
notes = [
    {
        "group": group,
        "filename": name,
        "sha256": hashlib.sha256(
            (ROOT / "examples/obsidian-vault" / name).read_bytes()
        ).hexdigest(),
    }
    for group, name in [
        ("rules", "assessment-rules.md"),
        ("memory", "project-memory.md"),
    ]
]
ids = ["BUYER-03", "BUYER-08", "BUYER-17"]
questions = {
    "BUYER-03": (
        "Access reviews",
        "Is access reviewed at least annually for all users?",
    ),
    "BUYER-08": ("Evidence gap", "Are remote employee workstations protected?"),
    "BUYER-17": ("Encryption", "Is sensitive data encrypted in transit?"),
}
excerpts = {
    "BUYER-03": {
        "supplier-l-security-policy.pdf": "Our access policy requires all user access, including contractors, to be reviewed annually.",
        "supplier-l-questionnaire.pdf": "Our operational access review covers employees annually. Contractor access is reviewed once every two years, despite the annual policy for all users.",
    },
    "BUYER-08": {
        "supplier-l-questionnaire.pdf": "Remote employee workstation safeguards: no response supplied."
    },
    "BUYER-17": {
        "supplier-l-security-policy.pdf": "Sensitive data uses TLS 1.2 or later in transit and encryption at rest."
    },
}
runs = []
for name, has_context in [
    ("rag-showcase-context-run.json", True),
    ("rag-fictional-development-run.json", False),
]:
    r = json.loads((ROOT / "reports" / name).read_text())
    assert r["provider"] == "local" and r["dataset"] == "rag" and r["complete"] is True
    assert r.get("source_review") is None and r["rag"]["retrieval_mode"] == "hybrid"
    assert (
        r["rag"]["supplier_name"] == "Fictional Supplier L · RAG development · hybrid"
    )
    if has_context:
        assert r["context_mode"] == "selected-vault-notes"
        assert r["showcase_context"] == {
            "kind": "public-sample-obsidian-vault",
            "notes": notes,
        }
        assert r["context_counts"] == {"rules": 1, "knowledge": 0, "memory": 1}
    else:
        assert r["context_mode"] == "local-retrieved-evidence"
    rows = {row["requirement_id"]: row for row in r["suppliers"][0]["assessments"]}
    output = []
    for rid in ids:
        retrieval = r["rag"]["retrievals"][rid]
        passages = retrieval["passages"]
        citations = r["rag"]["citations"][rid]
        for p in passages:
            assert allowed.get(p["filename"]) == p["document_id"]
        for c in citations:
            assert any(c["id"] == p["id"] and c["quote"] in p["text"] for p in passages)
        shown = []
        for filename, text in excerpts[rid].items():
            p = next(
                p for p in passages if p["filename"] == filename and text in p["text"]
            )
            shown.append(
                {
                    **p,
                    "excerpt": text,
                    "cited": any(c["id"] == p["id"] for c in citations),
                }
            )
        cue = ""
        if rid == "BUYER-03":
            cue = "A policy target does not prove implementation. The two-year contractor cycle is an explicit frequency gap; inspect both sources before deciding."
        if rid == "BUYER-08":
            cue = "An unanswered question means insufficient evidence, not an absent practice. Under the project rubric, Unknown is the appropriate draft label."
        output.append(
            {
                "id": rid,
                "short_label": questions[rid][0],
                "question": questions[rid][1],
                "assessment": rows[rid],
                "display_sources": shown,
                "passages": passages,
                "citations": citations,
                "review_note": cue,
            }
        )
    runs.append(
        {
            "id": "with-context" if has_context else "rag-only",
            "label": (
                "RAG + Obsidian rules & memory"
                if has_context
                else "RAG only · comparison example"
            ),
            "has_context": has_context,
            "context_counts": r.get(
                "context_counts", {"rules": 0, "knowledge": 0, "memory": 0}
            ),
            "question_count": len(rows),
            "questions": output,
        }
    )
result = {
    "runs": runs,
    "notes": [
        {
            "label": "Assessment rules" if n["group"] == "rules" else "Project memory",
            "text": (ROOT / "examples/obsidian-vault" / n["filename"]).read_text(),
        }
        for n in notes
    ],
}
(ROOT / "showcase/showcase-data.json").write_text(json.dumps(result, indent=2) + "\n")
for name in ["showcase_view.js", "showcase_view.css"]:
    shutil.copyfile(ROOT / name, ROOT / "showcase" / name)
print(
    "Built combined and RAG-only showcase from approved fictional sources and public sample notes."
)
