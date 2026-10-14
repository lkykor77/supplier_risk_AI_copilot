# Deployment Strategist portfolio narrative

## From business ambiguity to an inspectable application

Supplier Risk AI Copilot is an independent portfolio prototype for a pre-engagement supplier information security risk assessment problem. It combines operational problem framing, a document-to-decision data pipeline, hands-on coding, and a review workflow that keeps a person accountable for the decision.

The product question is: **how can a security analyst turn inconsistent supplier evidence into a traceable assessment and identify the next due-diligence action?** The response is a bounded working application, evaluated with fictional data, and a proposed customer pilot for validating its value.

## Capabilities demonstrated by the artifact

| Capability | Evidence in this project |
| --- | --- |
| Operational problem framing | Problem statement, analyst/procurement/risk-owner perspectives, explicit decision boundaries and a proposed pilot |
| Data preparation and pipelining | JSON/PDF intake, local OCR, checked answer mapping, source-page references, stable IDs and immutable source snapshots |
| Application building | Python HTTP API and JavaScript review interface; structured suggestions, corrections, revision checks and deterministic scoring |
| Code analysis and debugging | Evidence validation, frozen comparisons, diagnosis of empty final model output, failure examples and 47 automated tests |
| Privacy-driven AI deployment | Confidential supplier evidence processed locally; Open Weight AI model through LM Studio; no cloud upload or fallback in the local workflow |
| Custom AI harness engineering | Python prompt/context orchestration, constrained loopback execution, structured-output and evidence validation, with separate human review |
| Rules and persistent memory | Explicitly selected Obsidian notes, provenance hashes, bounded context and app-owned project memory |
| Product judgment | Human confirmation for ambiguous PDF extraction; separate unknown evidence; critical-supplier follow-up; simpler scoring after feedback |
| Communication and adoption | Public interactive demo, captioned walkthrough, English/Korean overview, diagrams and a proposed reviewer-training sequence |
| Impact measurement | Defined manual/assisted timing and error measures; synthetic technical evidence reported separately from unmeasured customer outcomes |

## Suggested interview walkthrough

1. Explain the pre-engagement supplier information security decision and whose workflow the app supports.
2. Show how raw documents become linked evidence, answers, requirements, suggestions and human decisions.
3. Correct the saved model error and explain why quote matching alone is insufficient.
4. Show the final risk indicator and critical-supplier follow-up boundary.
5. Inspect the Python/JavaScript implementation and a meaningful test or failure.
6. Explain what to validate with users before expanding the deployment.

