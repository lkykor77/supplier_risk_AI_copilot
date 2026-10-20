"""Serve the local analyst review screen: python3 review_app.py."""

import argparse
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import sqlite3
from pathlib import Path
import urllib.parse

from review_store import ReviewConflict, ReviewStore
from pdf_intake import PDFIntake
from rag import EvidenceStore
from local_assessor import read_config

ROOT = Path(__file__).resolve().parent


def make_handler(store: ReviewStore):
    """Serve only explicit app routes; never expose the project directory."""
    intake = PDFIntake(store.root)
    evidence = EvidenceStore(store.root)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            return  # No questionnaire or review content in access logs.

        def send(self, body: bytes, status: int = 200, mime: str = "application/json"):
            self.send_response(status)
            self.send_header("Content-Type", mime + "; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'")
            self.end_headers()
            self.wfile.write(body)

        def reply(self, data: dict | list, status: int = 200):
            self.send(json.dumps(data).encode(), status)

        def valid_host(self):
            host = self.headers.get("Host", "")
            return host in {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}

        def do_GET(self):
            if not self.valid_host():
                self.reply({"error": "Local host required."}, 403)
                return
            route = urllib.parse.urlsplit(self.path)
            try:
                assets = {"/": ("index.html", "text/html"), "/app.js": ("app.js", "text/javascript"),
                          "/styles.css": ("styles.css", "text/css"), "/rag.js": ("rag.js", "text/javascript")}
                if route.path in {"/risk_ui.js", "/framework_view.js"}:
                    self.send((ROOT / route.path.lstrip("/")).read_bytes(), mime="text/javascript")
                elif route.path in assets:
                    filename, mime = assets[route.path]
                    self.send((ROOT / "review_ui" / filename).read_bytes(), mime=mime)
                elif route.path == "/api/rag/settings":
                    self.reply({"embedding_model": read_config().get("embedding_model", "")})
                elif route.path == "/api/rag/cases":
                    self.reply(evidence.catalog())
                elif route.path == "/api/runs":
                    self.reply(store.catalog())
                elif route.path == "/api/run":
                    run_id = urllib.parse.parse_qs(route.query).get("id", [""])[0]
                    self.reply(store.read(run_id))
                elif route.path == "/api/pdf":
                    document_id = urllib.parse.parse_qs(route.query).get("id", [""])[0]
                    original = intake.folder(document_id) / "original.pdf"
                    if not original.exists():
                        # Saved public fixture runs work before a user indexes their first pack.
                        fixtures = [ROOT / "examples/rag" / name for name in
                                    ["supplier-l-security-policy.pdf", "supplier-l-questionnaire.pdf"]]
                        original = next((p for p in fixtures if p.exists() and
                                         hashlib.sha256(p.read_bytes()).hexdigest() == document_id), None)
                        if original is None:
                            self.reply({"error": "Source PDF not found locally."}, 404)
                            return
                    self.send(original.read_bytes(), mime="application/pdf")
                else:
                    self.reply({"error": "Not found."}, 404)
            except (ValueError, OSError, KeyError, TypeError):
                self.reply({"error": "Unable to load this run. Refresh or regenerate the assessment report."}, 400)

        def do_POST(self):
            origin = self.headers.get("Origin")
            expected = f"http://{self.headers.get('Host', '')}"
            if not self.valid_host() or origin != expected or self.headers.get("X-Review-App") != "1":
                self.reply({"error": "Same-origin review request required."}, 403)
                return
            if self.path not in {"/api/review", "/api/supplier-class", "/api/pdf/upload", "/api/pdf/suggest", "/api/pdf/confirm", "/api/pdf/assess", "/api/rag/create", "/api/rag/add", "/api/rag/search", "/api/rag/assess"} or self.headers.get("Content-Type") != "application/json":
                self.reply({"error": "Invalid review request."}, 400)
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                maximum = 15000000 if self.path == "/api/pdf/upload" else 500000 if self.path == "/api/pdf/confirm" else 65536
                if not 0 < length <= maximum:
                    raise ValueError("Invalid review size.")
                payload = json.loads(self.rfile.read(length))
                if not isinstance(payload, dict):
                    raise ValueError("Invalid review object.")
                if self.path == "/api/rag/create":
                    self.reply(evidence.create(payload.get("name"), payload.get("embedding_model", "")))
                elif self.path == "/api/rag/add":
                    self.reply(evidence.add(payload.get("case_id"), intake.read(payload.get("document_id", ""))))
                elif self.path == "/api/rag/search":
                    self.reply(evidence.search(payload.get("case_id"), payload.get("requirement_id")))
                elif self.path == "/api/rag/assess":
                    reviewer = payload.get("reviewer")
                    if payload.get("confirmed") is not True or not isinstance(reviewer, str) or not 1 <= len(reviewer.strip()) <= 100:
                        raise ValueError("Confirm source ownership/extraction review and enter your name or initials first.")
                    self.reply(evidence.assess(payload.get("case_id"), payload.get("with_vault") is True, reviewer=reviewer.strip()))
                elif self.path == "/api/review":
                    self.reply(store.save(payload.get("run_id", ""), payload))
                elif self.path == "/api/supplier-class":
                    self.reply(store.save_supplier_class(payload.get("run_id", ""), payload))
                elif self.path == "/api/pdf/upload":
                    self.reply(intake.upload(payload.get("filename"), payload.get("base64")))
                elif self.path == "/api/pdf/suggest":
                    self.reply(intake.suggest(payload.get("document_id", "")))
                elif self.path == "/api/pdf/confirm":
                    self.reply(intake.confirm(payload.get("document_id", ""), payload))
                else:
                    self.reply(intake.assess(payload.get("document_id", ""), payload.get("mapping_id", ""), payload.get("with_vault") is True))
            except ReviewConflict as error:
                self.reply({"error": str(error)}, 409)
            except (ValueError, KeyError, TypeError) as error:
                self.reply({"error": str(error)}, 400)
            except (OSError, sqlite3.Error):
                self.reply({"error": "Could not complete the local operation. Check the saved files and local model server."}, 500)

    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8501)
    parser.add_argument("--data-root", type=Path, default=ROOT, help="Optional isolated report/review directory for QA")
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(ReviewStore(args.data_root.resolve())))
    print(f"Review screen: http://127.0.0.1:{server.server_port}", flush=True)
    print("Press Control-C to stop. Reviews stay on this computer.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
