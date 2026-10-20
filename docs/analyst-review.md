# Analyst review screen

Start the local app from the project folder:

```sh
python3 review_app.py
```

Open **http://127.0.0.1:8501** in your browser. Press Control-C in Terminal to stop the server. No packages, model server, Obsidian connection, or API key are needed for reviewing previously saved results.

## Your first review

1. Choose the local Open Weight AI model evaluation run with 25 assessments.
2. Enter your name or initials. No assessment is automatically approved.
3. Choose **Fictional Supplier H** and inspect **Question 1**.
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

![Isolated QA test showing the preserved AI label and a separate corrected decision](screenshots/analyst-review-questions.png)

## Next validation

Time a manual review and an assisted review, including corrections. Ask a potential user to try the screen and record what they find useful or confusing. Keep measured feedback separate from simulated or automated tests.

Saved-report review uses Python's standard library with a small HTML/CSS/JavaScript interface. The optional [PDF intake workflow](pdf-intake.md) adds local extraction and OCR dependencies and uses LM Studio to propose answer mappings after upload, then assesses only after answer confirmation. Local PDF intake covers 20 questions. Approve the prefilled excerpts and page references; unanswered questions can remain blank with no source page. OCR correction notes are optional unless you change OCR wording. Streamlit, Docker and hosted deployment are optional future choices.

## Weighted questionnaire risk indicator

Choose **Normal supplier** or **Critical supplier** for the selected relationship. The score appears once all its requirements have human decisions. Fixed factors are met 0, partly met 0.5, missing 1 and unknown 1, with equal control weights. The result separates confirmed gaps from unresolved evidence. Critical suppliers receive enhanced-review flags for non-met answers. It recalculates after corrections; classification changes retain revision history. See [the methodology](risk-scoring.md).

## Combined Obsidian development run

To generate the default local development run for fictional suppliers D, F, G, H, I and J, use:

```sh
python3 local_assessor.py --combined-development --with-vault
```

This makes six fresh local model requests using the same selected Obsidian rules and memory, producing 30 assessments across five questions per supplier. It is a development experiment using existing fictional answers, not a new held-out benchmark. Raw note contents and local results remain ignored by Git. A complete combined run replaces the previous local development/evaluation choices in the selector; immutable source snapshots and earlier human review records are preserved. New suggestions require fresh human decisions. The selector prioritizes runs generated with Obsidian context.

## Provisional scores

The local app shows a provisional score for every supplier using only its saved AI suggestions, including separate suggested control-gap points and unresolved-evidence points. These draft indicators do not create or modify human decisions. The final indicator remains gated until every question for the selected supplier has a human decision. Correcting an assessment changes the final indicator; the provisional score continues to represent the original saved AI suggestions.

## Workspace views

The root URL opens on **Showcase**, a public fictional sample with a genuine local RAG + sample Obsidian rules/memory run. Use **Assess a supplier** for the existing review controls, uploads, evidence search and human risk decisions. The original 30-assessment vault-enabled development run remains the initial analyst selection. **Engineering details** keeps pipeline, context notes and limits out of the default sample. Demo decisions never modify real review records.
