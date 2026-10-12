# Supplier Risk AI Copilot

An FDE portfolio project in progress: help a supplier-security analyst review questionnaire answers, see the evidence, and approve or correct each suggested assessment.

## First exercise

This starter uses Python's standard library only. It has no AI integration yet. All suppliers and answers are fictional.

After cloning this repository, open a terminal in the project folder and run:

```sh
python3 baseline.py
```

You should see fifteen assessments and a count of matches against the hand-written answer key. This is a toy exercise, not a meaningful performance benchmark.

Open `data/suppliers.json` in an editor. Notice how the third supplier explicitly denies having some practices. The deliberately naive keyword baseline still marks two denied practices as met. This gives the future AI version a concrete problem to improve on.

Two additional suppliers test frequency: `fictional-d` reviews access every two years (`partly_met`), while `fictional-e` reviews it "regularly" (`unknown`). Their other answers are intentionally blank. The baseline currently matches 12 of 15 labels; this small development dataset is not a held-out evaluation.

## Initial scope

Next, read the [draft problem statement](docs/problem-statement.md) and [assessment guide](docs/assessment-guide.md). The guide explains the four statuses and includes your next exercise.

- One user: a supplier-security analyst.
- Input: structured questionnaire answers in JSON.
- Output: a proposed status, an exact supporting quote when available, and a reason.
- Statuses: met, partly_met, missing, unknown.
- `missing` means explicit evidence that a required practice is absent; an unanswered question means `unknown`.
- Suggested statuses describe the supplied answers; they do not verify actual supplier practices or certify compliance.
- Human review will be added before the app is considered complete.

The three requirements are fictional buyer requirements, not official NIST or ISO controls. Next, use NIST CSF 2.0 supply-chain guidance to design 5–8 buyer requirements with documented reference mappings. Some framework outcomes concern the buyer's own processes and cannot be assessed from supplier answers alone.

## Build milestones

1. Run this exercise and explain the two false-positive results.
2. Write a one-page problem statement and clarify the assessment rubric with a potential user.
3. Expand to 5–8 requirements and 5 fictional suppliers, with human-written expected labels.
4. Add an AI assessor with structured results and validated evidence quotes.
5. Compare AI and keyword results on additional suppliers held out from prompt development. Track per-status errors, unsupported positive assessments, unknown handling, latency, and cost.
6. Add a Streamlit review screen and persist reviewer corrections.
7. Add reproducible setup, essential tests, GitHub CI, screenshots, user feedback, and a deployment guide.

Keep ISO mappings, MCP, website checks, NIS2 and CRA reporting for later.

## Portfolio evidence to collect

- Discovery notes without confidential information.
- Manual review time versus assisted review time, including corrections.
- Evaluation method, results, limitations, and failure examples.
- Architecture, engineering tradeoffs, and what changed after user feedback.
- English README and demo; optionally a short Korean overview.

This repository currently contains the local keyword baseline and fictional data. AI assessment and ISO 27001 / NIST CSF mappings are planned; they are not implemented yet. No model API calls are made. Never commit credentials or confidential supplier data.

Reference: https://csrc.nist.gov/pubs/sp/1305/final
