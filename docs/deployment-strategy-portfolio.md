# Deployment Strategist portfolio narrative

## From business ambiguity to an inspectable application

Supplier Risk AI Copilot is an independent portfolio prototype for a pre-engagement supplier information security risk assessment problem. It combines operational problem framing, a document-to-decision data pipeline, hands-on coding, and a review workflow that keeps a person accountable for the decision.

The product question is: **how can a security analyst turn inconsistent supplier evidence into a traceable assessment and identify the next due-diligence action?** The response is a bounded working application, evaluated with fictional data, and a proposed customer pilot for validating its value.

## Capabilities demonstrated by the artifact

| Capability | Evidence in this project |
| --- | --- |
| Operational problem framing | Problem statement, analyst/procurement/risk-owner perspectives, explicit decision boundaries and a proposed pilot |
| Data preparation and pipelining | JSON/PDF intake, local OCR, checked answer mapping, source-page references, stable IDs and immutable source snapshots |
| Retrieval engineering | Supplier-scoped SQLite passages, BM25/local embedding search, rank fusion, source-page citations and explicit retrieval limits |
| Application building | Python HTTP API and JavaScript review interface; structured suggestions, corrections, revision checks and deterministic scoring |
| Code analysis and debugging | Evidence validation, frozen comparisons, diagnosis of empty final model output, failure examples and 64 automated tests |
| Privacy-driven AI deployment | Confidential supplier evidence processed locally; Open Weight AI model through LM Studio; no cloud upload or fallback in the local workflow |
| Custom AI harness engineering | Python prompt/context orchestration, constrained loopback execution, structured-output and evidence validation, with separate human review |
| Rules and persistent memory | Explicitly selected Obsidian notes, provenance hashes, bounded context and app-owned project memory |
| Product judgment | Human confirmation for ambiguous PDF extraction; separate unknown evidence; critical-supplier follow-up; simpler scoring after feedback |
| Communication and adoption | Clean interactive showcase, verified screenshots, English/Korean overview, diagrams and a proposed reviewer-training sequence |
| Impact measurement | Defined manual/assisted timing and error measures; synthetic technical evidence reported separately from unmeasured customer outcomes |


## Local RAG engineering extension

Supplier Evidence Search turns a multi-document security-review problem into a bounded retrieval and decision workflow. The implementation connects PDF/OCR extraction, supplier-scoped SQLite indexing, BM25/local embedding retrieval, citation-checked Open Weight LLM generation and existing human review. The first small retrieval fixture supports reproducibility rather than a claim of customer impact; independent evidence labeling and analyst-effort measurement remain the next validation steps. See [the RAG design and limitations](local-rag.md).
