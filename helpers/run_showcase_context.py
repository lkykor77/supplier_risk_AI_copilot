"""Run a curated fictional RAG sample with public Obsidian rules and memory.

Reads only the included sample notes, never the user's configured private vault.
"""

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from local_assessor import read_config
from rag import EvidenceStore

config = {
    **read_config(),
    "vault_path": str(ROOT / "examples/obsidian-vault"),
    "rule_notes": ["assessment-rules.md"],
    "knowledge_notes": [],
    "memory_notes": ["project-memory.md"],
}
store = EvidenceStore(ROOT, config_reader=lambda: config)
case = next(
    (
        c
        for c in store.catalog()
        if c["name"] == "Fictional Supplier L · RAG development · hybrid"
    ),
    None,
)
if case is None:
    raise SystemExit(
        "Run python3 rag_eval.py --hybrid first to index the fictional sample PDFs."
    )
print(
    "Generating three showcase questions with local RAG + public sample rules and memory.",
    flush=True,
)
result = store.assess(
    case["id"], with_vault=True, question_ids=["BUYER-03", "BUYER-08", "BUYER-17"]
)
path = next(
    p
    for p in (ROOT / "rag" / case["id"]).glob("assessment-run-*.json")
    if hashlib.sha256(p.read_bytes()).hexdigest() == result["report_sha256"]
)
report = json.loads(path.read_text())
report["replaces_runs"] = [result["report_sha256"]]
report["showcase_context"] = {
    "kind": "public-sample-obsidian-vault",
    "notes": [
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
    ],
}
(ROOT / "reports/rag-showcase-context-run.json").write_text(
    json.dumps(report, indent=2) + "\n"
)
print("Saved three-question context run; no personal vault notes used.", flush=True)
