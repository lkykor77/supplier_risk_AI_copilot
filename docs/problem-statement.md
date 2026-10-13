# Problem statement — draft to validate

## User and problem

A supplier-security analyst reviews questionnaire answers against a buyer's security requirements. Our hypothesis is that manually finding relevant evidence and recording consistent assessments takes time, especially when answers are incomplete or ambiguous. We have not validated this hypothesis with users yet.

## Proposed workflow

Load fictional questionnaire answers → propose one assessment per requirement → show the exact supporting quote and a short reason → let the analyst accept or correct the result → save the reviewed assessment.

The tool evaluates what the answer states. It does not verify the supplier's actual practices.

## First working version

- Structured JSON input, using the five fictional buyer requirements in `data/requirements.json`.
- Four possible statuses: `met`, `partly_met`, `missing`, `unknown`.
- A keyword baseline and, later, an AI assessor using the same input and output structure.
- Exact quotes for supported assessments; no invented evidence.
- A simple review screen that stores analyst decisions.
- The initial dataset now contains five requirements and five fictional suppliers; validate the rubric and expected labels with a potential user.

## How we will measure usefulness

- Compare predictions with rubric-based expected labels reviewed by a person on held-out fictional suppliers.
- Report mistakes for each status, particularly unsupported `met` results.
- Check that each quote exists verbatim in the supplied answer and supports the result.
- Compare manual review time with assisted review time, including time spent correcting mistakes.
- Record AI latency and cost per supplier.

The current twenty-five-assessment keyword exercise is a learning example, not evidence of real-world performance. Performance targets will be set after the dataset and baseline are established.

## Deferred work

Multiple framework mappings, a supplier-facing upload portal, website checks, MCP, real supplier evaluation, and regulatory reporting. Local PDF intake is now implemented with analyst-confirmed answer mapping; see [PDF intake](pdf-intake.md).

## Discovery questions

Ask a potential user these questions using fictional examples only. Record their answers; do not invent interview findings.

1. Which part of questionnaire review takes the most time?
2. What evidence would you need before accepting a suggested assessment?
3. How would you distinguish an absent practice from an unclear answer?
4. Would this workflow fit your process? What would you change first?

If no analyst is available yet, conduct a timed self-review and label it as a simulation rather than user research.
