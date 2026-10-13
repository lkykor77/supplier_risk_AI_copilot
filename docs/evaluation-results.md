# Frozen synthetic evaluation v1 — results

Date: October 13, 2026. Model: `gemini-3.5-flash-lite`. Dataset and unchanged prompt were committed in `6a66159` before any requests for these cases. See the [evaluation plan](evaluation-plan.md), [manifest](../data/evaluation_manifest.json), and [saved live report](../reports/evaluation-run-2026-10-13.json).

## Results

| Expected status | Examples | AI matches | Keyword baseline matches |
| --- | --- | --- | --- |
| `met` | 7 | 7/7 | 1/7 |
| `partly_met` | 4 | 3/4 | 0/4 |
| `missing` | 7 | 7/7 | 0/7 |
| `unknown` | 7 | 6/7 | 7/7 |
| **Total** | **25** | **23/25 (92%)** | **8/25 (32%)** |

The same model previously matched 25/25 development labels against 18/25 for the baseline. Both sets contain five suppliers and five requirements, but they are distinct datasets. Scores should not be pooled to conceal the two new errors.

All 25 quotes occur verbatim in the corresponding supplier answers. There are no blank answers in this evaluation. Unlike the development dataset, unknown cases involve missing detail or contradictions rather than empty responses.

The API reported 4,372 total tokens. Median request latency was 1.439 seconds, excluding request spacing. Dollar cost and billing tier were not verified.

## Two mistakes

### Eighteen-month restoration tests: partial practice classified as absent

`evaluation-g`, `BUYER-05`: "We restore a backup as a test once every eighteen months."

Expected: `partly_met`. AI: `missing`. The reason says this fails the annual requirement. That identifies the frequency gap correctly, but under our rubric an existing practice with insufficient frequency is partial, not absent. The original prompt explicitly mentioned two-year tests; the eighteen-month example exposes incomplete generalization to a different interval.

### Unspecified security contact: missing information classified as absent practice

`evaluation-h`, `BUYER-01`: "Our help desk receives messages. We have not specified who handles security questions."

Expected: `unknown`. AI: `missing`. The answer does not identify a security contact, but it does not explicitly establish that none exists. The model conflates missing information with an absent practice. An analyst should review this label because the distinction is a rubric decision.

## Other observations

An AI assistant reviewed the quotes and reasons against the current rubric; this is not independent analyst validation.

- Equivalent wording was recognized in all five positive paraphrase cases.
- Both unresolved contradictory answers were classified `unknown`, with quotes including both sides of the contradiction.
- Every explicit absence example was correctly classified `missing`.
- The embedded instructions in `evaluation-j` did not cause the model to mark the other requirements `met`; all five labels for that supplier matched the expected labels. This demonstrates one limited test, not general prompt-injection resistance.
- No AI false `met` labels occurred in this run. That observation is limited to these 25 cases.

## Interpretation and limits

The prompt, expected labels and dataset were frozen before the first run. Neither the prompt nor answer key was changed in response to the two mistakes. Hashes in the saved report match the manifest.

The examples and expected labels were drafted by the same AI assistant helping build the project, using the existing rubric. They were not independently annotated or validated by an analyst. The dataset is small and synthetic, several patterns resemble development cases, and the keyword baseline is deliberately weak. Describe the result as "23/25 matches on a frozen synthetic evaluation," not "92% real-world accuracy."

## Next engineering step

Build the analyst review screen so a person can inspect quotes, accept or correct labels, and save a review record. Use these two errors as concrete review demonstrations. Keep initial model results separate from reviewer decisions.

Before claiming useful workflow impact, have a potential user review the rubric and try the screen. Any prompt tuning based on these failures converts these cases into development data; evaluate a revised prompt on fresh frozen cases.
