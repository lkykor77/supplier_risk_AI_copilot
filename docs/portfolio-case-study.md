# Supplier Risk AI Copilot — deployment strategy and engineering case study

A working prototype that connects an operational pre-engagement supplier information security risk assessment problem to a document-processing pipeline, an analyst application, and a proposed customer pilot. Python/JavaScript implementation, local Open Weight AI model inference in LM Studio, and selected Obsidian rules/memory support an evidence-led review workflow.

## Problem and scope

An analyst needs to distinguish a claimed security practice from an explicit gap or insufficient evidence. A deliberately naive keyword baseline accepts phrases even when a supplier denies the practice, while missing equivalent wording. The project implements five fictional buyer requirements and four statuses: met, partly met, missing, unknown.

The initial questionnaire exercise developed into JSON assessment, frozen evaluation, local inference, selected Obsidian context, a review interface, and PDF intake. It is a portfolio prototype, not a compliance certification service. No customer discovery interviews, production deployments, or real-supplier accuracy measurements are claimed.

## Customer decision and delivery strategy

The initial decision is whether supplier evidence is sufficient to proceed to the next due-diligence stage and what needs follow-up. Security analysts interpret the evidence; procurement manages onboarding; a risk owner determines criticality and acceptance; engineering owns data access and runtime constraints. These stakeholder roles are a discovery hypothesis to validate, not completed customer research.

The [pilot plan](customer-deployment-plan.md) sequences discovery, data preparation, workflow configuration, guided use, outcome measurement and the next scope decision. It measures total reviewer effort and unsupported positive assessments rather than using model accuracy as a substitute for operational impact.

## Data model and pipeline

The pipeline links **Supplier → Questionnaire/source document → Answer → Buyer requirement → AI assessment → Human decision**. Source-page references and stable IDs preserve provenance; model suggestions and corrections remain separate; scoring derives from completed human decisions. The structured records provide a basis for later customer-specific integration without changing the frozen evaluation inputs.

## Implementation

- **Input:** fictional JSON answers or local analyst-uploaded PDFs. PDFKit extracts text and renders pages; Apple Vision attempts OCR, with local Tesseract.js fallback configured for English and Korean.
- **Confirmation:** the analyst maps answers to requirements and page numbers. Nonblank mappings must occur in their selected extracted text after whitespace normalization; explained OCR corrections are marked. Blank answers remain unknown.
- **Assessment:** the Python client calls an explicitly configured loopback LM Studio endpoint, requests structured JSON, rejects truncated or missing final output, and validates requirement coverage and exact evidence quotes. Expected labels are excluded from model input.
- **Context:** optional allowlisted Obsidian notes are read with path checks and provenance hashes. App-owned project memory stays separate from personal rule notes. Vault context is prohibited for the frozen evaluation.
- **Review:** immutable source/model snapshots, separate reviewer decisions, required correction notes, revision checks, and append-only decision events. Evidence can be traced back to the original PDF page.
- **Public presentation:** a static GitHub Pages demo serves only explicitly copied fictional data and assets. Demo corrections stay in browser session storage; no local model, private vault, or uploaded PDF is exposed.

## Decisions and tradeoffs

**Open Weight AI model versus cloud.** Local inference avoids transmitting supplier answers to a model provider. On the small saved comparison it was substantially slower than the earlier Gemini run. This reflects the actual runtimes and settings, not a controlled model-speed experiment. The local path has no cloud fallback.

**Manual PDF mapping versus guessed extraction.** Tables, reading order, mixed text/images, and OCR errors can break question-answer alignment. Explicit confirmation adds analyst effort but keeps the meaning and page references inspectable. Arbitrary supplier formats and handwriting are not guaranteed.

**Small native stack versus more infrastructure.** Python's standard library and a buildless review interface keep setup understandable. Swift and Node are added only for local PDF extraction/OCR. Docker and oMLX were not required. This choice suits a single local analyst; authentication, multi-user access, and hosted inference would need additional work.

**Quotes versus conclusions.** A valid quote only proves the words occur in the answer. It does not prove the claim is true, that OCR matches the page, or that the quote supports the label. Human review is essential to this workflow.

## Evaluation and failures

The frozen synthetic evaluation contains five suppliers × five requirements. Original prompt and dataset hashes were checked; Obsidian context was excluded. On October 13, 2026:

| Assessor | Labels matched | Median request latency |
| --- | --- | --- |
| Open Weight AI model, local MLX 4-bit | 24/25 | 26.086 seconds |
| Earlier Gemini 3.5 Flash-Lite | 23/25 | 1.439 seconds |
| Keyword baseline | 8/25 | Not measured |

All 25 local quotes passed verbatim checks. Expected labels were drafted with AI assistance and have not been independently validated. Different generation settings and runtimes limit comparison; 25 cases cannot establish general model superiority.

The local model labeled an unspecified security contact as **missing** instead of **unknown**. The public demo makes this error visible and lets visitors correct it. One explanation used “compliance” too broadly; the actual tool assesses questionnaire claims.

An earlier local request returned schema-shaped JSON in `reasoning_content` with empty final `content`. The parser rejected it. A targeted check showed that explicit `reasoning_effort: none` produced a final JSON answer. Reasoning text is never used as the final assessment.

## Verified checks

- 47 automated app tests passed on the development Mac, covering evidence validation, provider behavior, vault boundaries, intake mapping, review persistence, audit history, and concurrency conflicts.
- A one-page selectable-text PDF and its image-only equivalent extracted successfully. A two-page mixed fixture selected native text and OCR per page; an encrypted fixture was rejected.
- A live browser flow uploaded the fictional scan, confirmed the five mapped answers, and called the Open Weight AI model through LM Studio. It returned the expected fixture statuses in 27.276 seconds. That is one end-to-end example, not an accuracy benchmark.
- The public demo is tested separately for corrections, fabricated-quote rejection, session persistence, reset, and responsive layout.

See [local evaluation details](local-integration-results.md), [saved local report](../reports/local-evaluation-run-2026-10-13.json), [review workflow](analyst-review.md), and [PDF intake](pdf-intake.md).

## Next validation

Interview a security analyst using fictional examples; validate labels and the unknown/missing boundary; measure manual versus assisted review time and correction rates. Expand PDF fixtures to realistic tables, poor scans, and Korean questionnaires. Run a larger held-out evaluation before making real-world performance claims.

## Code investigation and product iteration

The local output-channel failure was investigated by inspecting request settings and returned fields, reproducing the behavior, and testing an explicit configuration. The parser rejected empty final output instead of treating reasoning as the assessment. Evidence-validation tests reject invented quotes and preserve the distinction between model output and reviewer decisions.

Portfolio feedback led to concrete changes: local PDF intake with checked mapping; simpler fixed scoring with supplier criticality; and supplier-level questionnaire labels with framework topic references. These changes demonstrate iteration on the product. Independent customer feedback and measured adoption remain future validation.

## Reproduce and present

Follow the [README](../README.md) and local setup guides. The public `showcase/` folder is a self-contained static demo published by `.github/workflows/pages.yml`. It includes a captioned walkthrough assembled from actual local app captures, not a continuous screen recording. Captures use fictional data in an isolated QA folder, with reviewer actions clearly marked as tests.

Assisted development used Codex for implementation and verification. The repository exposes the code, tests, decisions and limitations so the work can be inspected and reproduced.

## Human-reviewed risk summary

The app calculates a fixed questionnaire-gap indicator only after all human decisions. Status factors are met 0, partly met 0.5, missing 1 and unknown 1, with equal requirement weights. Unknown penalties are shown separately from confirmed missing-control gaps. A normal/critical supplier selection changes the follow-up flag, preserving classification changes with reviewer identity and revision history. Critical suppliers receive enhanced-review flags for every non-met answer. The formula is a prototype design choice, not an ISO/NIST-prescribed score. See [methodology and limits](risk-scoring.md), [data flow](diagrams/data-flow.png), and [system design](diagrams/system-design.png).

## Portfolio positioning

See the [Deployment Strategist narrative](deployment-strategy-portfolio.md) for the capability-to-evidence map and role research. Runtime configuration and raw reports preserve model identifiers; the public narrative focuses on the Open Weight AI model integration and the operational decision it supports.
