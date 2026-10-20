"""Evaluate local retrieval on fictional source pages; optionally generate a review run.

python3 rag_eval.py --hybrid --generate
Only the included fictional PDF pack is used. No vault context is loaded.
"""

import argparse
import base64
from datetime import datetime, timezone
import json
from pathlib import Path
from pdf_intake import PDFIntake
from rag import EvidenceStore, digest

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hybrid", action="store_true")
    parser.add_argument(
        "--embedding-model", default="text-embedding-nomic-embed-text-v1.5"
    )
    parser.add_argument("--generate", action="store_true")
    args = parser.parse_args()
    fixture = json.loads((ROOT / "examples/rag/fixture.json").read_text())
    store = EvidenceStore(ROOT)
    intake = PDFIntake(ROOT)
    docs = []
    for source in fixture["documents"]:
        path = ROOT / "examples/rag" / source["filename"]
        docs.append(
            intake.upload(path.name, base64.b64encode(path.read_bytes()).decode())
        )
    results = []
    cases = []
    for model in ["", args.embedding_model] if args.hybrid else [""]:
        name = (
            fixture["supplier"]
            + " · RAG development · "
            + ("hybrid" if model else "keyword-only")
        )
        case = next(
            (
                c
                for c in store.catalog()
                if c["name"] == name and c["embedding_model"] == model
            ),
            None,
        ) or store.create(name, model)
        for doc in docs:
            store.add(case["id"], doc)
        cases.append(case["id"])
        queries = []
        for query in fixture["queries"]:
            result = store.search(case["id"], query["question_id"])
            found = {(p["filename"], p["page"]) for p in result["passages"]}
            gold = {tuple(x) for x in query["gold"]}
            queries.append(
                {
                    "question_id": query["question_id"],
                    "gold_pages": query["gold"],
                    "retrieved_pages": [list(x) for x in sorted(found)],
                    "gold_pages_retrieved": len(gold & found),
                    "gold_page_count": len(gold),
                    "retrieval": result,
                }
            )
        results.append(
            {
                "mode": "hybrid" if model else "keyword-only",
                "embedding_model": model,
                "gold_pages_retrieved": sum(q["gold_pages_retrieved"] for q in queries),
                "gold_page_count": sum(q["gold_page_count"] for q in queries),
                "query_count": len(queries),
                "queries": queries,
            }
        )
        print(
            results[-1]["mode"],
            results[-1]["gold_pages_retrieved"],
            "/",
            results[-1]["gold_page_count"],
            "gold pages found in top six passages",
            flush=True,
        )
    report = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "fixture_sha256": digest(fixture),
        "results": results,
        "limits": "Six synthetic development queries over three source pages; relevance labels were not independently validated. This measures retrieval coverage, not assessment accuracy or a representative benchmark.",
    }
    (ROOT / "reports/rag-retrieval-evaluation.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    if args.generate:
        print(
            "Generating 20 suggestions with local model; no vault context.", flush=True
        )
        result = store.assess(cases[-1])
        print(json.dumps(result), flush=True)
        path = next(
            p
            for p in (ROOT / "rag" / cases[-1]).glob("assessment-run-*.json")
            if __import__("hashlib").sha256(p.read_bytes()).hexdigest()
            == result["report_sha256"]
        )
        saved = json.loads(path.read_text())
        # This public fixture run contains only the included fictional sources and no personal notes/config.
        (ROOT / "reports/rag-fictional-development-run.json").write_text(
            json.dumps(saved, indent=2) + "\n"
        )
        print("Saved fictional run and retrieval evaluation.", flush=True)


if __name__ == "__main__":
    main()
