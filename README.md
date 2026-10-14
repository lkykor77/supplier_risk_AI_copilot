# Supplier Risk AI Copilot

An FDE portfolio project in progress: help a supplier-security analyst review questionnaire answers, see the evidence, and approve or correct each suggested assessment.


**[Try the public interactive demo](https://lkykor77.github.io/supplier_risk_AI_copilot/)** · [Engineering case study](docs/portfolio-case-study.md) · [한국어 개요](docs/overview-ko.md)

The public demo uses saved AI results and fictional data. Try correcting the real saved model error, watch the captioned local-app walkthrough, and inspect the evaluation limits. The full application runs locally with LM Studio.

## Review assessments in your browser

```sh
python3 review_app.py
```

Open **http://127.0.0.1:8501**. The [analyst review guide](docs/analyst-review.md) explains how to accept or correct assessments, validate quotes, and save decisions separately from the AI output. It works from saved reports without running a model. Your review history stays local.

![Analyst workspace — isolated automated QA example](docs/screenshots/analyst-review.jpg)

## Upload supplier questionnaires as PDF

The [PDF intake guide](docs/pdf-intake.md) covers local uploads of text, scanned, and mixed PDFs. Check the extracted text, map answers to the five requirements with page references, then assess with LM Studio and review the proposed decisions. Originals and intake records stay local. No Google API call is used for this flow.

## Run the keyword exercise

The assessors and saved-report review use Python's standard library. PDF intake adds a macOS helper and a Node OCR dependency. It includes a keyword baseline, a Gemini assessor, and a local model assessor with optional Obsidian context. All suppliers and answers are fictional.

After cloning this repository, open a terminal in the project folder and run:

```sh
python3 baseline.py
```

You should see twenty-five assessments and a count of matches against the hand-written answer key. This is a toy exercise, not a meaningful performance benchmark.

Open `data/suppliers.json` in an editor. Notice how the third supplier explicitly denies having some practices. The deliberately naive keyword baseline still marks two denied practices as met. This gives the future AI version a concrete problem to improve on.

Two additional suppliers test frequency: `fictional-d` reviews access every two years (`partly_met`), while `fictional-e` reviews it "regularly" (`unknown`). They also include partial or vague answers about administrator authentication and backup restore testing. Their security contact and incident response answers are intentionally blank. The baseline currently matches 18 of 25 labels; this small development dataset is not a held-out evaluation.

## Initial scope

Next, read the [draft problem statement](docs/problem-statement.md) and [assessment guide](docs/assessment-guide.md). The guide explains the four statuses and includes your next exercise.

- One user: a supplier-security analyst.
- Input: structured answers in JSON, or locally uploaded PDFs with analyst-confirmed answer mapping.
- Output: a proposed status, an exact supporting quote when available, and a reason.
- Statuses: met, partly_met, missing, unknown.
- `missing` means explicit evidence that a required practice is absent; an unanswered question means `unknown`.
- Suggested statuses describe the supplied answers; they do not verify actual supplier practices or certify compliance.
- Human decisions are saved separately from immutable model output, with an audit history.

The five requirements are fictional buyer requirements, not official NIST or ISO controls. Next, document how these buyer requirements relate to NIST CSF 2.0 guidance, including the limits of each mapping. Some framework outcomes concern the buyer's own processes and cannot be assessed from supplier answers alone.

## Build milestones

1. Run this exercise and explain the two false-positive results.
2. Write a one-page problem statement and clarify the assessment rubric with a potential user.
3. Initial dataset complete: five buyer requirements and five fictional suppliers with rubric-based expected labels. Review these labels with a potential user before treating them as ground truth.
4. Add an AI assessor with structured results and validated evidence quotes.
5. Compare AI and keyword results on additional suppliers held out from prompt development. Track per-status errors, unsupported positive assessments, unknown handling, latency, and cost.
6. Local analyst review and PDF intake implemented; persist reviewer corrections separately.
7. Add reproducible setup, essential tests, GitHub CI, screenshots, user feedback, and a deployment guide.

Keep ISO mappings, MCP, website checks, NIS2 and CRA reporting for later.

The [frozen evaluation plan](docs/evaluation-plan.md) adds 25 new synthetic assessments using the unchanged prompt. The first run matched **23/25 AI labels versus 8/25 baseline labels**; see the [two errors and evaluation limits](docs/evaluation-results.md). Run it separately from the development examples:

```sh
python3 ai_assessor.py --dataset evaluation --all
```

## AI assessment preparation

### Local Qwen and Obsidian

The [local setup guide](docs/local-setup.md) connects LM Studio with an optional allowlist of Obsidian rules, knowledge and project memory:

```sh
python3 local_assessor.py --check-server
python3 local_assessor.py
python3 local_assessor.py --with-vault --save-memory
```

The [verified local integration results](docs/local-integration-results.md) record a 5/5 vault-enhanced smoke test and a separate 24/25 frozen evaluation result (Gemini: 23/25; keyword baseline: 8/25). These small synthetic runs do not establish general accuracy.

Use `python3 local_assessor.py --dataset evaluation --all` for the unchanged-prompt comparison. Vault-enhanced runs are separate experiments. Local inference has no cloud fallback. Personal notes and machine-specific config stay out of GitHub. Docker and oMLX are optional later choices, not required services.

`assessment.py` prepares model input without expected labels or keyword rules. It validates that results cover each requirement exactly once and quote only the corresponding supplier answer. Blank answers must be `unknown`. Quote matching checks that evidence exists; a person must still check that it supports the conclusion.

The Gemini connection is implemented in `ai_assessor.py`. Follow the [local Gemini setup guide](docs/gemini-setup.md):

```sh
python3 setup_key.py
python3 ai_assessor.py
```

The first run assesses one supplier; `python3 ai_assessor.py --all` compares all five. On October 13, 2026, a complete live run with `gemini-3.5-flash-lite` matched 25/25 development labels, versus 18/25 for the keyword baseline. All 16 nonempty quotes passed verbatim checks. These examples informed the prompt; this is not a held-out accuracy estimate. See the [evaluation results and limitations](docs/development-evaluation.md) and [saved run](reports/development-run-2026-10-13.json). Run the evidence-validation and mocked integration tests without an API account or network access:

```sh
python3 -m unittest discover -s tests -v
```

## Portfolio evidence to collect

- Discovery notes without confidential information.
- Manual review time versus assisted review time, including corrections.
- Evaluation method, results, limitations, and failure examples.
- Architecture, engineering tradeoffs, and what changed after user feedback.
- English README and demo; optionally a short Korean overview.

This repository contains a keyword baseline, Gemini and local assessors, and fictional data. ISO 27001 / NIST CSF mappings are planned; they are not implemented yet. The Gemini assessor makes cloud API calls; the local assessor calls only a loopback model server. Dry runs make no inference requests. Never commit credentials or confidential supplier data.

Reference: https://csrc.nist.gov/pubs/sp/1305/final
