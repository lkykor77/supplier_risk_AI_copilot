"""Local PDF extraction, confirmed answer mapping, and local-only assessment."""

import base64
import os
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import threading
import time
import uuid

from ai_assessor import load_inputs
from assessment import validate_assessment
from baseline import assess
from local_assessor import local_payload, parse_local, read_config, request_json

ROOT = Path(__file__).resolve().parent


def extract_pdf(path: Path) -> dict:
    """Use PDFKit and Vision in a bounded child process; no cloud OCR."""
    cache = ROOT / ".cache"
    cache.mkdir(exist_ok=True)
    binary = cache / "pdf-extract"
    source = ROOT / "helpers/pdf_extract.swift"
    if not binary.exists() or binary.stat().st_mtime < source.stat().st_mtime:
        swift = shutil.which("swiftc")
        if not swift:
            raise ValueError("PDF intake requires macOS and Apple's command-line developer tools (swiftc).")
        try:
            result = subprocess.run([swift, str(source), "-o", str(binary), "-module-cache-path", str(cache / "swift-modules")],
                                    capture_output=True, timeout=180)
        except subprocess.TimeoutExpired:
            raise ValueError("Building the PDF helper timed out. Check Apple command-line tools.") from None
        if result.returncode:
            raise ValueError("Could not build the local PDF helper. Check Apple command-line tools.")
    try:
        rendered = cache / ("pdf-pages-" + hashlib.sha256(path.read_bytes()).hexdigest())
        result = subprocess.run([str(binary), str(path), str(rendered)], capture_output=True, timeout=180)
    except subprocess.TimeoutExpired:
        raise ValueError("PDF extraction timed out. Try a smaller PDF.") from None
    if result.returncode:
        # Helper errors are fixed strings, not PDF content.
        raise ValueError(result.stderr.decode(errors="replace")[:300] or "PDF extraction failed.")
    extracted = json.loads(result.stdout)
    if any(not p["ocr_text"] for p in extracted["pages"]):
        config = read_config()
        node = config.get("ocr_node_binary") or shutil.which("node")
        languages = cache / "ocr-languages"
        if not node or not all((languages / (lang + ".traineddata.gz")).exists() for lang in ["eng", "kor"]):
            raise ValueError("OCR fallback is not configured. Follow docs/pdf-intake.md and run setup_pdf.py.")
        env = dict(os.environ)
        if config.get("ocr_node_modules"):
            env["NODE_PATH"] = config["ocr_node_modules"]
        (cache / "ocr-worker").mkdir(exist_ok=True)
        try:
            fallback = subprocess.run([node, str(ROOT / "helpers/ocr_pages.cjs"), str(rendered),
                                       str(languages), str(cache / "ocr-worker")], env=env, capture_output=True, timeout=180)
        except subprocess.TimeoutExpired:
            raise ValueError("Local OCR timed out. Try a smaller PDF.") from None
        if fallback.returncode:
            raise ValueError("Local OCR fallback failed. Check Node, tesseract.js and language setup.")
        by_page = {p["page"]: p for p in json.loads(fallback.stdout)["pages"]}
        for page in extracted["pages"]:
            if not page["ocr_text"]:
                ocr = by_page[page["page"]]
                page["ocr_text"] = ocr["text"]
                page["minimum_ocr_confidence"] = ocr["confidence"]
                page["warning"] = "OCR text must be checked against the original page."
                native = page["native_text"]
                page["mode"] = "native" if len(native) >= 80 and len(ocr["text"]) <= len(native) * 1.25 else "ocr"
                page["text"] = page[page["mode"] + "_text"]
        extracted["ocr_engine"] = "Tesseract.js fallback (on-device)"
    if sum(len(p["native_text"]) + len(p["ocr_text"]) for p in extracted["pages"]) > 300000:
        raise ValueError("Extracted PDF text exceeds this prototype's size limit.")
    return extracted


def normalized(text: str) -> str:
    """Treat PDF line wrapping as whitespace, without altering words."""
    return " ".join(text.split())


class PDFIntake:
    """Persist intake privately and require explicit mapping confirmation."""

    def __init__(self, root: Path, extractor=extract_pdf):
        self.root = root
        self.extractor = extractor
        self.lock = threading.RLock()

    def folder(self, document_id: str) -> Path:
        if not isinstance(document_id, str) or not re.fullmatch(r"[a-f0-9]{64}", document_id):
            raise ValueError("Invalid document ID.")
        return self.root / "intake" / document_id

    def upload(self, filename: str, encoded: str) -> dict:
        if not isinstance(filename, str) or not filename.lower().endswith(".pdf") or not isinstance(encoded, str):
            raise ValueError("Choose a PDF file.")
        if len(encoded) > 14000000:
            raise ValueError("PDF is too large; maximum upload size is 10 MB.")
        data = base64.b64decode(encoded, validate=True)
        if not 0 < len(data) <= 10 * 1024 * 1024 or b"%PDF-" not in data[:1024]:
            raise ValueError("Invalid PDF or file larger than 10 MB.")
        document_id = hashlib.sha256(data).hexdigest()
        with self.lock:
            folder = self.folder(document_id)
            folder.mkdir(parents=True, exist_ok=True)
            original = folder / "original.pdf"
            if not original.exists():
                original.write_bytes(data)
            metadata = folder / "extraction.json"
            if not metadata.exists():
                extracted = self.extractor(original)
                extracted.update(id=document_id, filename=Path(filename).name[:120],
                                 uploaded_at=datetime.now(timezone.utc).isoformat())
                metadata.write_text(json.dumps(extracted, indent=2) + "\n")
            return self.read(document_id)

    def read(self, document_id: str) -> dict:
        folder = self.folder(document_id)
        extraction = json.loads((folder / "extraction.json").read_text())
        requirements, _ = load_inputs("development")
        return {**extraction, "requirements": [{k: r[k] for k in ["id", "description", "question_id"]}
                                               for r in requirements]}

    def confirm(self, document_id: str, payload: dict) -> dict:
        with self.lock:
            document = self.read(document_id)
            if payload.get("confirmed") is not True or not isinstance(payload.get("reviewer"), str) or not payload["reviewer"].strip():
                raise ValueError("Confirm the mapped answers against the PDF and enter your name or initials.")
            requirements, _ = load_inputs("development")
            mappings = payload.get("mappings")
            if (not isinstance(mappings, list) or not all(isinstance(m, dict) for m in mappings)
                    or len(mappings) != len(requirements)
                    or any(not isinstance(m.get("requirement_id"), str) for m in mappings)
                    or {m["requirement_id"] for m in mappings} != {r["id"] for r in requirements}):
                raise ValueError("Map every requirement exactly once. Use a blank answer when not found.")
            pages = {p["page"]: p for p in document["pages"]}
            answers = {}
            provenance = {}
            total = 0
            for mapping in mappings:
                answer = mapping.get("answer")
                source_pages = mapping.get("pages")
                modes = mapping.get("modes", {})
                if not isinstance(modes, dict):
                    raise ValueError("Invalid extraction modes.")
                correction = mapping.get("correction_note", "")
                if not isinstance(answer, str) or not isinstance(correction, str) or len(correction) > 2000:
                    raise ValueError("Invalid mapped text or correction note.")
                total += len(answer)
                if total > 16000:
                    raise ValueError("Mapped answers exceed this prototype's 16,000-character limit.")
                if not isinstance(source_pages, list) or any(type(p) is not int or p not in pages for p in source_pages):
                    raise ValueError("Use valid source page numbers.")
                if answer.strip() and not source_pages:
                    raise ValueError("Every nonblank answer needs a source page.")
                selected = []
                ocr_selected = False
                for number in source_pages:
                    mode = modes.get(str(number), pages[number]["mode"])
                    if mode not in {"native", "ocr"}:
                        raise ValueError("Invalid extraction mode.")
                    selected.append(pages[number][mode + "_text"])
                    ocr_selected |= mode == "ocr"
                copied = not answer.strip() or normalized(answer) in normalized("\n".join(selected))
                if not copied and not (ocr_selected and correction.strip()):
                    raise ValueError("Copy the answer from its selected source pages. OCR corrections require an explanation.")
                requirement = next(r for r in requirements if r["id"] == mapping["requirement_id"])
                answers[requirement["question_id"]] = answer.strip()
                provenance[requirement["id"]] = {"pages": source_pages, "modes": modes,
                                                 "ocr_corrected": not copied, "correction_note": correction.strip()}
            mapping_id = str(uuid.uuid4())
            confirmed = {"id": mapping_id, "document_id": document_id, "confirmed_by": payload["reviewer"].strip()[:100],
                         "confirmed_at": datetime.now(timezone.utc).isoformat(),
                         "supplier": {"id": "pdf-" + document_id[:12], "answers": answers}, "provenance": provenance}
            (self.folder(document_id) / ("mapping-" + mapping_id + ".json")).write_text(json.dumps(confirmed, indent=2) + "\n")
            return {"mapping_id": mapping_id, "document_id": document_id}

    def assess(self, document_id: str, mapping_id: str, with_vault: bool = False) -> dict:
        if not isinstance(mapping_id, str) or not re.fullmatch(r"[a-f0-9-]{36}", mapping_id):
            raise ValueError("Invalid confirmed mapping ID.")
        confirmed = json.loads((self.folder(document_id) / ("mapping-" + mapping_id + ".json")).read_text())
        requirements, _ = load_inputs("development")
        supplier = confirmed["supplier"]
        config = read_config()
        context, sources = None, []
        if with_vault:
            from vault_context import load_context
            context, sources = load_context(config)
        payload, prompt = local_payload(requirements, supplier, config, context)
        started = time.monotonic()
        response = request_json(config["base_url"], "/chat/completions", payload, config["timeout_seconds"])
        rows = validate_assessment(parse_local(response), requirements, supplier)
        by_id = {r["id"]: r for r in requirements}
        for row in rows:
            requirement = by_id[row["requirement_id"]]
            row["baseline_status"] = assess(supplier["answers"][requirement["question_id"]], requirement["keyword"])
        run_id = str(uuid.uuid4())
        report = {"run_id": run_id, "created_at": datetime.now(timezone.utc).isoformat(), "provider": "local", "model": config["model"],
                  "dataset": "pdf", "context_mode": "selected-vault-notes" if context else "original-frozen-prompt",
                  "complete": True, "source_document_id": document_id, "source_mapping": confirmed,
                  "source_data": {"requirements": requirements, "suppliers": [supplier]},
                  "dataset_sha256": hashlib.sha256(json.dumps([requirements, [supplier]], sort_keys=True).encode()).hexdigest(),
                  "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(), "note_sources": sources,
                  "suppliers": [{"supplier_id": supplier["id"], "assessments": rows,
                                 "latency_seconds": round(time.monotonic() - started, 3), "usage": response.get("usage", {})}]}
        target = self.folder(document_id) / ("assessment-run-" + run_id + ".json")
        target.write_text(json.dumps(report, indent=2) + "\n")
        return {"report_sha256": hashlib.sha256(target.read_bytes()).hexdigest()}
