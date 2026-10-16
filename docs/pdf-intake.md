# Local questionnaire PDF intake

Upload a selectable-text, scanned, or mixed PDF in the local analyst screen. A local table parser matches known HECVAT question IDs to complete rows. For other questions, the local Open Weight AI model scans extracted text in bounded chunks and proposes answers and page references for 20 security questions. Review and approve these proposals, then assess them locally. This is an analyst upload workflow; there is no supplier portal.

## Start on this Mac

The PDF helper, English/Korean OCR language files and Node OCR runtime are configured on the development Mac. Keep LM Studio's local server running with the configured Open Weight AI model loaded. If the review screen is already running, stop it with Control-C and restart from the project folder:

```sh
python3 review_app.py
```

Open http://127.0.0.1:8501 and choose **Upload questionnaire PDF**.

1. Upload the PDF. Local text extraction and OCR run first, followed by automatic evidence selection in LM Studio. Large documents can take several minutes.
2. Review the prefilled excerpts and source pages against the original. The model selects immutable excerpts; it cannot invent or silently rewrite supplier answers.
3. Questions with no located answer have blank answers and no page requirement. **Mark as not found** clears both fields. Absence of evidence is assessed as **unknown**, not a confirmed missing control.
4. OCR notes identify uncorrected OCR evidence automatically. No correction is claimed unless you edit the OCR wording and explain the correction after checking the page. Optional editing controls remain available.
5. Enter your initials and approve the mapping. Optional Obsidian context is applied to assessment, not evidence selection.
6. Choose **Confirm answers & assess locally**. Each requirement is assessed separately to bound context and output size. Review all 20 decisions before a risk score appears.

The 20-question catalog is in `data/pdf_requirements.json`. It retains the original five requirements and adds 15 security topics inspired by [this public completed HECVAT Lite questionnaire](https://cursivetechnology.com/wp-content/uploads/2024/04/Cursive-hecvatlite304-2024.pdf). These are security assessment questions, not a complete HECVAT, ISO 27001 or NIST compliance assessment. The frozen synthetic benchmark retains its original five-question dataset; the public demo offers both those saved runs and a hand-authored 20-question example; benchmark results do not validate this expanded workflow.

Uploaded questionnaires have no answer key or accuracy score. A matching quote proves that the text occurs in the confirmed answer; it does not prove that OCR was accurate or that the quote supports the model's conclusion.

## Reproduce the PDF setup on another Mac

Requirements: Python 3.10+, macOS with `swiftc` (Apple command-line developer tools), and Node.js 16+ with npm. The assessors and saved-report review use Python's standard library. PDF OCR adds the pinned Node dependency:

```sh
npm install
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-pdf.txt
python3 setup_pdf.py
```

The setup command downloads English and Korean language files once. Extraction then uses local PDFKit, Apple Vision when available, and local Tesseract.js as a fallback. Tesseract receives rendered page images because it does not directly read PDF files; see the [official Tesseract.js documentation](https://github.com/naptha/tesseract.js). No document content is sent to an OCR service. Configure LM Studio using the [local setup guide](local-setup.md); no Google API key is needed for PDF assessments.

## Limits and storage

- Up to 10 MB and 25 pages per PDF; password-protected files must be exported unlocked.
- Confirmed answers are limited to 60,000 characters overall; assessment requests run separately per requirement. Extremely long individual answers or large optional vault context can still exceed the loaded model context.
- Automatic mapping can select irrelevant passages or miss evidence. Analysts must check page references, reading order, negations, and frequency statements. A source match proves provenance, not relevance.
- Poor scans, handwriting, complex tables, and Korean layouts need further evaluation. English and Korean OCR languages are configured, but only English fixtures have been verified so far.
- Originals, extracted text, confirmed mappings and immutable assessment runs live in ignored `intake/`. Human decisions and audit events live in ignored `reviews/`. Rendered pages and OCR assets live in ignored `.cache/`. Private config and Obsidian notes stay out of GitHub.
- The server binds to loopback and has no authentication. This is a local portfolio prototype, not a shared production supplier service.

## Verification fixtures

Use `examples/fictional-questionnaire-text.pdf` or `examples/fictional-questionnaire-scan.pdf`. Both contain the same five fictional answers. The image-only version has no selectable text. The rubric statuses are `met`, `partly_met`, `met`, `met`, `unknown`.

Automated checks cover native extraction, scanned extraction, required confirmation, page validation, verbatim mapping checks, explained OCR corrections, malformed input, and integration with the separate reviewer record. A two-page mixed fixture selected native text on page 1 and OCR on page 2. An encrypted fixture was rejected. The browser flow uses an isolated QA data directory and the reviewer name `Automated UI test`; these are test records, not user approvals.

The live scanned-PDF browser test returned the five expected fixture statuses (`met`, `partly_met`, `met`, `met`, `unknown`) and valid quotes. This verifies one synthetic end-to-end example, not general supplier assessment accuracy. The current suite passes 54 tests on the development Mac. The public eight-page Cursive HECVAT PDF was also tested for table-row extraction, automatic proposals and acceptance of an unanswered question without a page. One expanded question was assessed live through LM Studio; all 20 assessment calls have not been independently evaluated for accuracy.

![Scanned PDF assessed with local Open Weight AI model — isolated automated QA](screenshots/pdf-intake.jpg)
