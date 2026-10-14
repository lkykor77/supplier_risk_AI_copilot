# Analyst review screen

Start the local app from the project folder:

```sh
python3 review_app.py
```

Open **http://127.0.0.1:8501** in your browser. Press Control-C in Terminal to stop the server. No packages, model server, Obsidian connection, or API key are needed for reviewing previously saved results.

## Your first review

1. Choose the local Qwen evaluation run with 25 assessments.
2. Enter your name or initials. No assessment is automatically approved.
3. Choose `evaluation-h` and inspect `BUYER-01`.
4. Compare the complete supplier answer with the AI quote and explanation.
5. Click **Correct assessment**, choose `unknown`, and explain why unspecified contact details do not prove the practice is absent.
6. Add a review note explaining the correction and save.
7. Refresh the page to confirm your decision persists. The original AI label still appears beside your saved decision.

For an assessment you agree with, use **Accept AI suggestion**. You can edit status, evidence quote, and explanation. A correction requires a review note. Quotes must occur verbatim in the relevant supplier answer; blank answers must remain `unknown` with no quote.

The synthetic answer key is hidden by default. Reveal it as a learning reference after making your own assessment; its labels have not been independently validated by an analyst.

## What gets saved

- Completed reports are discovered in `results/` and the checked-in synthetic `reports/` folder. Failed or malformed reports are excluded.
- Each available run is snapshotted, together with its source questionnaire and requirements, under `reviews/<source-sha256>/source.json`.
- Analyst decisions are stored separately in `review.json`, with reviewer, time, status, quote, explanation, and review note.
- An event history retains earlier saved decisions when a reviewer changes their mind.
- Each save checks the review revision. A stale browser tab must refresh before overwriting a newer review.
- Snapshots remain available when an assessor overwrites a `latest` report. A changed report becomes a different review run.
- The `reviews/` folder is Git-ignored. Source report files and evaluation answer keys are not changed by the screen.

The server listens only on loopback. It serves explicit app routes rather than the project directory. Saving requires a same-origin request; private configuration, keys and Obsidian notes are not served. Supplier text is displayed as text, not executable HTML. This is a local, single-user workflow, not a multi-user production deployment.

## Verified workflow

Automated tests cover persistence, unchanged model outputs, fabricated quotes, reviewer identification, correction notes, audit history, stale saves, snapshots, and HTTP boundaries. A browser test corrected `evaluation-h/BUYER-01` in an isolated QA copy and verified it after reload. The test used the reviewer name **Automated UI test**; it is not a real analyst review or evidence of user adoption. Desktop and narrow layouts were inspected.

![Isolated QA test showing the preserved AI label and a separate corrected decision](screenshots/analyst-review.jpg)

## Next validation

Time a manual review and an assisted review, including corrections. Ask a potential user to try the screen and record what they find useful or confusing. Keep measured feedback separate from simulated or automated tests.

Saved-report review uses Python's standard library with a small HTML/CSS/JavaScript interface. The optional [PDF intake workflow](pdf-intake.md) adds local extraction and OCR dependencies and calls LM Studio only after answer confirmation. Streamlit, Docker and hosted deployment are optional future choices.

## Weighted questionnaire risk indicator

Choose **Normal supplier** or **Critical supplier** for the selected relationship. The score appears once all its requirements have human decisions. Fixed factors are met 0, partly met 0.5, missing 1 and unknown 1, with equal control weights. The result separates confirmed gaps from unresolved evidence. Critical suppliers receive enhanced-review flags for non-met answers. It recalculates after corrections; classification changes retain revision history. See [the methodology](risk-scoring.md).
