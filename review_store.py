"""Preserve model outputs and record separate, validated analyst decisions."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import threading

from ai_assessor import load_inputs
from assessment import validate_assessment
from risk_scoring import summarize_risk


class ReviewConflict(ValueError):
    """A review was updated by another browser since it was read."""


class ReviewStore:
    """Local immutable run snapshots with append-only review events."""

    def __init__(self, root: Path):
        self.root = root
        self.directory = root / "reviews"
        self.lock = threading.RLock()

    def _folder(self, run_id: str) -> Path:
        if not re.fullmatch(r"[a-f0-9]{64}", run_id):
            raise ValueError("Invalid run ID.")
        return self.directory / run_id

    def _snapshot(self, path: Path) -> tuple[str, dict]:
        raw = path.read_bytes()
        report = json.loads(raw)
        if report.get("complete") is not True or report.get("dataset") not in {"development", "evaluation", "pdf"}:
            raise ValueError("Only completed development, evaluation or PDF reports can be reviewed.")
        if report["dataset"] == "pdf":
            requirements = report["source_data"]["requirements"]
            suppliers = report["source_data"]["suppliers"]
        else:
            requirements, suppliers = load_inputs(report["dataset"])
        digest = hashlib.sha256(json.dumps([requirements, suppliers], sort_keys=True).encode()).hexdigest()
        if report.get("dataset_sha256") != digest:
            raise ValueError("Report does not match the current source dataset.")
        by_id = {s["id"]: s for s in suppliers}
        selected = []
        seen = set()
        for entry in report["suppliers"]:
            supplier = by_id[entry["supplier_id"]]
            if supplier["id"] in seen:
                raise ValueError("Duplicate supplier in report.")
            seen.add(supplier["id"])
            rows = [{k: row[k] for k in ["requirement_id", "status", "evidence_quote", "reason"]}
                    for row in entry["assessments"]]
            validate_assessment({"assessments": rows}, requirements, supplier)
            selected.append(supplier)
        if not selected:
            raise ValueError("Report has no suppliers.")
        run_id = hashlib.sha256(raw).hexdigest()
        return run_id, {"source_sha256": run_id, "report": report,
                        "requirements": requirements, "suppliers": selected}

    def catalog(self) -> list:
        """Discover completed saved runs; malformed and failed runs are excluded."""
        with self.lock:
            runs = {}
            for pattern in ["results/latest*.json", "reports/*run*.json", "intake/*/assessment-run-*.json"]:
                for path in sorted(self.root.glob(pattern)):
                    try:
                        run_id, snapshot = self._snapshot(path)
                    except (ValueError, KeyError, TypeError, OSError):
                        continue
                    folder = self._folder(run_id)
                    folder.mkdir(parents=True, exist_ok=True)
                    target = folder / "source.json"
                    if not target.exists():
                        with target.open("x", encoding="utf-8") as handle:
                            json.dump(snapshot, handle, indent=2)
                    runs[run_id] = self._metadata(run_id, snapshot)
            # Reviewed snapshots remain accessible after latest reports are overwritten.
            if self.directory.exists():
                for path in self.directory.glob("*/source.json"):
                    if path.parent.name not in runs:
                        snapshot = json.loads(path.read_text())
                        runs[path.parent.name] = self._metadata(path.parent.name, snapshot)
            return sorted(runs.values(), key=lambda item: item["created_at"], reverse=True)

    def _metadata(self, run_id: str, snapshot: dict) -> dict:
        report = snapshot["report"]
        return {"id": run_id, "model": report["model"], "dataset": report["dataset"],
                "context_mode": report.get("context_mode", "original-frozen-prompt"),
                "created_at": report["created_at"], "count": sum(len(s["assessments"]) for s in report["suppliers"])}

    def read(self, run_id: str) -> dict:
        """Return questionnaire evidence, original AI decisions and saved reviews."""
        with self.lock:
            folder = self._folder(run_id)
            source = folder / "source.json"
            if not source.exists():
                raise ValueError("Run not found. Refresh the run list.")
            snapshot = json.loads(source.read_text())
            state = self._state(folder)
            requirements = {r["id"]: r for r in snapshot["requirements"]}
            answers = {s["id"]: s for s in snapshot["suppliers"]}
            suppliers = []
            for entry in snapshot["report"]["suppliers"]:
                rows = []
                supplier = answers[entry["supplier_id"]]
                for original in entry["assessments"]:
                    requirement = requirements[original["requirement_id"]]
                    key = supplier["id"] + ":" + requirement["id"]
                    rows.append({"requirement_id": requirement["id"], "description": requirement["description"],
                                 "answer": supplier["answers"].get(requirement["question_id"], ""),
                                 "ai": {k: original[k] for k in ["status", "evidence_quote", "reason"]},
                                 "expected": supplier.get("expected", {}).get(requirement["id"]),
                                 "pdf_source": {"document_id": snapshot["report"]["source_document_id"],
                                                **snapshot["report"]["source_mapping"]["provenance"][requirement["id"]]}
                                                if snapshot["report"]["dataset"] == "pdf" else None,
                                 "review": state["decisions"].get(key)})
                supplier_class = state.get("supplier_classes", {}).get(supplier["id"], "normal")
                suppliers.append({"id": supplier["id"], "assessments": rows,
                                  "risk": summarize_risk(rows, supplier_class)})
            return {"meta": self._metadata(run_id, snapshot), "revision": state["revision"],
                    "suppliers": suppliers, "reviewed_count": len(state["decisions"]),
                    "events": state["events"], "classification_events": state.get("classification_events", [])}

    def _state(self, folder: Path) -> dict:
        path = folder / "review.json"
        return json.loads(path.read_text()) if path.exists() else {"revision": 0, "decisions": {}, "events": []}

    def save(self, run_id: str, payload: dict) -> dict:
        """Record one explicit analyst decision after quote and revision validation."""
        with self.lock:
            folder = self._folder(run_id)
            current = self.read(run_id)
            if type(payload.get("revision")) is not int or payload["revision"] != current["revision"]:
                raise ReviewConflict("This run changed in another tab. Refresh before saving.")
            supplier_id = payload.get("supplier_id")
            requirement_id = payload.get("requirement_id")
            row = next((row for supplier in current["suppliers"] if supplier["id"] == supplier_id
                        for row in supplier["assessments"] if row["requirement_id"] == requirement_id), None)
            if row is None:
                raise ValueError("Unknown supplier or requirement.")
            for field, maximum in [("reviewer", 100), ("comment", 4000), ("reason", 4000), ("evidence_quote", 12000), ("status", 30)]:
                value = payload.get(field)
                if not isinstance(value, str) or len(value) > maximum:
                    raise ValueError(f"Invalid {field}.")
            if not payload["reviewer"].strip():
                raise ValueError("Enter your name or initials before saving a review.")
            validate_assessment({"assessments": [{k: payload[k] for k in ["requirement_id", "status", "evidence_quote", "reason"]}]},
                                [{"id": requirement_id, "question_id": "answer"}],
                                {"answers": {"answer": row["answer"]}})
            corrected = any(payload[k] != row["ai"][k] for k in ["status", "evidence_quote", "reason"])
            if corrected and not payload["comment"].strip():
                raise ValueError("Add a review note explaining your correction.")
            decision = {k: payload[k] for k in ["status", "evidence_quote", "reason", "comment"]}
            decision.update(reviewer=payload["reviewer"].strip(), updated_at=datetime.now(timezone.utc).isoformat(),
                            action="corrected" if corrected else "accepted")
            state = self._state(folder)
            key = supplier_id + ":" + requirement_id
            state["events"].append({"supplier_id": supplier_id, "requirement_id": requirement_id,
                                    "before": state["decisions"].get(key), "after": decision})
            state["decisions"][key] = decision
            state["revision"] += 1
            temp = folder / "review.json.tmp"
            temp.write_text(json.dumps(state, indent=2) + "\n")
            temp.replace(folder / "review.json")
            return self.read(run_id)

    def save_supplier_class(self, run_id: str, payload: dict) -> dict:
        """Record supplier classification with identity and revision history."""
        with self.lock:
            current = self.read(run_id)
            if type(payload.get("revision")) is not int or payload["revision"] != current["revision"]:
                raise ReviewConflict("This run changed in another tab. Refresh before changing supplier class.")
            supplier_id = payload.get("supplier_id")
            if not any(s["id"] == supplier_id for s in current["suppliers"]):
                raise ValueError("Unknown supplier.")
            reviewer, classification = payload.get("reviewer"), payload.get("supplier_class")
            if not isinstance(reviewer, str) or not reviewer.strip() or len(reviewer) > 100:
                raise ValueError("Enter your name or initials before changing supplier class.")
            if classification not in {"normal", "critical"}:
                raise ValueError("Choose normal or critical supplier.")
            folder = self._folder(run_id)
            state = self._state(folder)
            classes = state.setdefault("supplier_classes", {})
            state.setdefault("classification_events", []).append({"supplier_id": supplier_id,
                "before": classes.get(supplier_id, "normal"), "after": classification,
                "reviewer": reviewer.strip(), "updated_at": datetime.now(timezone.utc).isoformat()})
            classes[supplier_id] = classification
            state["revision"] += 1
            temp = folder / "review.json.tmp"
            temp.write_text(json.dumps(state, indent=2) + "\n")
            temp.replace(folder / "review.json")
            return self.read(run_id)
