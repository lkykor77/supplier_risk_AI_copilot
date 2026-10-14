# Deployment Strategist portfolio narrative

## From business ambiguity to an inspectable application

Supplier Risk AI Copilot is an independent portfolio prototype for a supplier-onboarding problem. It combines operational problem framing, a document-to-decision data pipeline, hands-on coding, and a review workflow that keeps a person accountable for the decision.

The product question is: **how can a security analyst turn inconsistent supplier evidence into a traceable assessment and identify the next due-diligence action?** The response is a bounded working application, evaluated with fictional data, and a proposed customer pilot for validating its value.

## Capabilities demonstrated by the artifact

| Capability | Evidence in this project |
| --- | --- |
| Operational problem framing | Problem statement, analyst/procurement/risk-owner perspectives, explicit decision boundaries and a proposed pilot |
| Data preparation and pipelining | JSON/PDF intake, local OCR, checked answer mapping, source-page references, stable IDs and immutable source snapshots |
| Application building | Python HTTP API and JavaScript review interface; structured suggestions, corrections, revision checks and deterministic scoring |
| Code analysis and debugging | Evidence validation, frozen comparisons, diagnosis of empty final model output, failure examples and 47 automated tests |
| Open Weight AI model integration | Local LM Studio inference with schema-constrained output and no cloud fallback on the local path |
| Rules and persistent memory | Explicitly selected Obsidian notes, provenance hashes, bounded context and app-owned project memory |
| Product judgment | Human confirmation for ambiguous PDF extraction; separate unknown evidence; critical-supplier follow-up; simpler scoring after feedback |
| Communication and adoption | Public interactive demo, captioned walkthrough, English/Korean overview, diagrams and a proposed reviewer-training sequence |
| Impact measurement | Defined manual/assisted timing and error measures; synthetic technical evidence reported separately from unmeasured customer outcomes |

## Suggested interview walkthrough

1. Explain the supplier-onboarding decision and whose workflow the app supports.
2. Show how raw documents become linked evidence, answers, requirements, suggestions and human decisions.
3. Correct the saved model error and explain why quote matching alone is insufficient.
4. Show the final risk indicator and critical-supplier follow-up boundary.
5. Inspect the Python/JavaScript implementation and a meaningful test or failure.
6. Explain what to validate with users before expanding the deployment.

## Role research informing the presentation

The supplied [London](https://jobs.lever.co/palantir/79c3f906-622b-4261-8fc6-8af0028caa27), [New York](https://jobs.lever.co/palantir/e0ab8226-b928-4e3a-bf87-08fe7b1ea595) and [Seoul](https://jobs.lever.co/palantir/2e193bdf-e668-49c1-ba32-66cc1aa131a4) postings emphasize customer workflows, relevant data, applications, collaboration with engineers, training, demos and communication. Palantir's [day-in-the-life article](https://blog.palantir.com/a-day-in-the-life-of-a-palantir-deployment-strategist-951cb59a5a96) describes a mix of product, technical implementation and customer iteration. Sources reviewed October 14, 2026.

The narrative is tailored to those capabilities. This independent project uses Python, JavaScript, Swift/Node PDF helpers, LM Studio and Obsidian. It does not use Palantir Foundry or AIP and does not imply Palantir affiliation, a completed customer deployment, or measured business impact. Raw evaluation reports and runtime configuration retain exact model identifiers for reproducibility; portfolio copy uses the term **Open Weight AI model**.

## Two-sentence CV description

Built a Python/JavaScript supplier-review application and document-processing pipeline with PDF/OCR extraction, local Open Weight AI model inference through LM Studio, selected Obsidian rules/memory, and traceable human decisions. Defined the stakeholder workflow and a proposed customer pilot with discovery, reviewer training and outcome measures; published an interactive demo with architecture diagrams, code investigation, failure analysis and synthetic evaluation evidence.
