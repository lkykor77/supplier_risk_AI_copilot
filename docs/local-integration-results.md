# Local integration — verified results

Date: October 13, 2026.

## Working configuration

- Native LM Studio loopback server on port 1234.
- Model: Open Weight AI model (27B), MLX 4-bit; loaded context: 8,192 tokens.
- Explicit `reasoning_effort: none`, temperature 0.7, top-p 0.8, top-k 20, presence penalty 1.5. Settings are stored in the report. Loaded server supported four parallel predictions, but this client made only one request at a time.
- Python standard-library client, JSON schema, and exact quote validation.
- Selected Obsidian rule notes and a dedicated project-memory note are read at run time. Personal rule files are not copied into GitHub or changed by the app.
- Completed summaries persist in the app-owned Obsidian project folder. A subsequent context load successfully read the updated memory.
- Docker and oMLX were not required or started. oMLX endpoint compatibility remains an optional, untested future configuration.

## Live checks

A vault-enhanced run on `fictional-d` matched 5/5 expected labels versus 2/5 for the keyword baseline. It saved a concise Obsidian memory summary and history note. This smoke test verifies the integration; it does not establish general model accuracy. Its private report and note metadata remain local.

A separate run on all five frozen evaluation suppliers used the original assessment prompt and no vault context:

| Provider | Labels matched | Median request latency |
| --- | --- | --- |
| Local Open Weight AI model (27B) MLX 4-bit | **24/25 (96%)** | **26.086 s** |
| Gemini 3.5 Flash-Lite, earlier run | 23/25 (92%) | 1.439 s |
| Keyword baseline | 8/25 (32%) | Not measured |

Source: [local synthetic report](../reports/local-evaluation-run-2026-10-13.json), [earlier Gemini report](../reports/evaluation-run-2026-10-13.json).

The local model handled the eighteen-month restoration test correctly as `partly_met`. Both models misclassified an unspecified security contact as `missing` instead of the expected `unknown`. All 25 local quotes occur verbatim in their respective answers. The contradiction and embedded-instruction cases matched their expected labels; these few examples do not establish comprehensive robustness.

One local explanation used the word "compliance" when describing conflicting incident-plan statements. That is too broad for this app: it evaluates questionnaire claims, not verified compliance. A review screen should let analysts correct explanations as well as labels.

## Output-channel issue found and fixed

The initial local request produced schema-shaped JSON in `reasoning_content` and an empty final `content`. The parser rejected it. A targeted local test verified that `reasoning_effort: none` produces JSON in final content; that setting is now explicit and recorded. The app never treats reasoning text as the final assessment.

## Interpretation

The local result is one additional matching label on 25 synthetic cases. It is not sufficient evidence that this Open Weight AI model is generally superior to Gemini. Expected labels were drafted with AI assistance and have not been independently validated by an analyst. Generation settings and provider runtimes differ; latency reflects these specific runs, not a controlled hardware benchmark. Prompt and dataset hashes match the original frozen evaluation inputs.

The analyst review screen now keeps raw model decisions separate from reviewer corrections. Measuring total reviewer effort with an independent analyst remains a customer-validation milestone.
