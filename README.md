# Supplier Risk AI Copilot

An FDE portfolio project in progress: help a supplier-security analyst review questionnaire answers, see the evidence, and approve or correct each suggested assessment.

## First exercise

This project uses Python's standard library only. It includes a keyword baseline and a Gemini AI assessor. All suppliers and answers are fictional.

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
- Input: structured questionnaire answers in JSON.
- Output: a proposed status, an exact supporting quote when available, and a reason.
- Statuses: met, partly_met, missing, unknown.
- `missing` means explicit evidence that a required practice is absent; an unanswered question means `unknown`.
- Suggested statuses describe the supplied answers; they do not verify actual supplier practices or certify compliance.
- Human review will be added before the app is considered complete.

The five requirements are fictional buyer requirements, not official NIST or ISO controls. Next, document how these buyer requirements relate to NIST CSF 2.0 guidance, including the limits of each mapping. Some framework outcomes concern the buyer's own processes and cannot be assessed from supplier answers alone.

## Build milestones

1. Run this exercise and explain the two false-positive results.
2. Write a one-page problem statement and clarify the assessment rubric with a potential user.
3. Initial dataset complete: five buyer requirements and five fictional suppliers with rubric-based expected labels. Review these labels with a potential user before treating them as ground truth.
4. Add an AI assessor with structured results and validated evidence quotes.
5. Compare AI and keyword results on additional suppliers held out from prompt development. Track per-status errors, unsupported positive assessments, unknown handling, latency, and cost.
6. Add a Streamlit review screen and persist reviewer corrections.
7. Add reproducible setup, essential tests, GitHub CI, screenshots, user feedback, and a deployment guide.

Keep ISO mappings, MCP, website checks, NIS2 and CRA reporting for later.

The [frozen evaluation plan](docs/evaluation-plan.md) adds 25 new synthetic assessments using the unchanged prompt. The first run matched **23/25 AI labels versus 8/25 baseline labels**; see the [two errors and evaluation limits](docs/evaluation-results.md). Run it separately from the development examples:

```sh
python3 ai_assessor.py --dataset evaluation --all
```

## AI assessment preparation

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

This repository contains a keyword baseline, a Gemini assessor, and fictional data. ISO 27001 / NIST CSF mappings are planned; they are not implemented yet. Only running the AI assessor without `--dry-run` makes model API calls. Never commit credentials or confidential supplier data.

Reference: https://csrc.nist.gov/pubs/sp/1305/final
