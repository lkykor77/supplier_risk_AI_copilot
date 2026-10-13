# First development evaluation

Date: October 13, 2026. Model: `gemini-3.5-flash-lite`. Five fictional suppliers, five buyer requirements each. Source code at run time: `ecf8ecb`. The [saved report](../reports/development-run-2026-10-13.json) contains the exact model outputs, token counts, latency, and prompt/dataset hashes.

## Results

| Expected status | Examples | AI matches | Keyword baseline matches |
| --- | --- | --- | --- |
| `met` | 6 | 6/6 | 6/6 |
| `partly_met` | 3 | 3/3 | 0/3 |
| `missing` | 4 | 4/4 | 0/4 |
| `unknown` | 12 | 12/12 | 12/12 |
| **Total** | **25** | **25/25 (100%)** | **18/25 (72%)** |

The AI corrected seven baseline errors: four explicit denials that the keyword checker marked `met`, and three partial practices it marked `unknown`. Both methods matched all twelve `unknown` examples. Nine of those examples were blank answers; only three contained vague text, so the unknown score is mostly an easy blank-answer check.

All 16 nonempty quotes occur verbatim in the corresponding answers. The other nine assessments have blank answers, empty quotes, and `unknown` statuses. These checks were re-run against the source data before saving this report.

The API reported 3,749 total tokens across five requests. Median request latency was 1.482 seconds, excluding the deliberate 15-second spacing. These are measurements from one run, not performance guarantees. Billing tier and actual charged cost were not verified.

## Review of the explanations

An AI assistant reviewed all 25 outputs against the documented rubric. This is not an independent analyst review.

- Positive answers explicitly support the requested practice.
- Explicit denials correctly produce `missing`.
- Two-year review/testing cycles and MFA covering only cloud administrators correctly produce `partly_met`.
- Vague frequency, generic security language, and backup creation without restoration evidence correctly produce `unknown`.
- The security-contact explanations use the word "named" even though the evidence provides a designated mailbox, not a person's name. The `met` label is supported by our rubric, which accepts a security mailbox, but the wording should be more precise.

No label correction was identified under the current rubric. Exact quote matching alone cannot validate an explanation's interpretation.

## What this result establishes

The live Gemini connection works, structured responses pass validation, and the model handles these development cases better than the deliberately simple keyword baseline.

## Limits and next experiment

These examples were used to design the prompt, which explicitly describes several of their patterns. The dataset and answer key were drafted with AI assistance and have not been independently validated by an analyst. The keyword baseline is intentionally naive. Do not describe this result as "100% accurate supplier-risk assessment."

Next, freeze this prompt and create a separate evaluation dataset with new fictional suppliers and independently reviewed expected labels. Include paraphrases, mixed positive/negative statements, contradictions, incomplete coverage, and instructions embedded in answers. Run both assessors before making any prompt changes. If we tune on those examples, they become development data and we need a fresh test set.

The current score says nothing about real supplier practices, regulatory compliance, adoption, or time saved in an analyst's workflow.
