# Customer deployment plan — supplier review pilot

This is a proposed pilot plan for a hypothetical customer. It demonstrates how the working prototype could be evaluated with security and procurement users.

## Start with an operational decision

**Decision to support:** which supplier answers justify moving to the next due-diligence stage, which gaps need follow-up, and which critical relationships require closer review?

**Initial workflow hypothesis:** security analysts spend effort locating evidence, interpreting inconsistent answers, and preserving their reasoning. Procurement needs a timely, explainable review record; the risk owner needs to see unresolved issues before accepting a relationship. The application supports the evidence review and gap summary. Final onboarding, risk acceptance and follow-up assignment remain outside the prototype.

The pilot should test whether assisted review reduces total reviewer effort without increasing unsupported positive assessments. Time savings and adoption are not measured yet.

## Stakeholders and discovery

| Stakeholder | Question to resolve | Deliverable |
| --- | --- | --- |
| Security analyst | Which answers are hardest to interpret? Which evidence is necessary before marking a requirement met? | Validated rubric and examples of ambiguous evidence |
| Procurement/process owner | Where does the review sit in onboarding? What delays the next decision? | Workflow map, handoffs and baseline timing |
| Risk owner | What makes a supplier critical? Which findings need escalation, and who accepts risk? | Agreed classification and decision boundaries |
| Engineering/data owner | Which formats arrive, who owns them, and what privacy/setup constraints apply? | Data inventory, permissions and deployment requirements |


## Proposed delivery sequence

| Stage | Work | Evidence required to advance |
| --- | --- | --- |
| Discover | Walk through a real process with analysts; identify the decision, pain points, inputs and owners | Stakeholder-approved problem statement and baseline measures |
| Prepare data | Inventory formats; test PDF reading order and OCR; agree answer mappings and the buyer rubric | Analysts confirm source text, coverage and reference limits |
| Configure workflow | Choose local processing constraints, criticality rules and review responsibilities | Documented criteria and a reproducible local setup |
| Pilot with users | Demonstrate upload → checked mapping → suggestion → correction → risk summary; train reviewers on unknown evidence | Completed guided sessions and observed feedback, not invented testimonials |
| Evaluate | Compare manual and assisted reviews on comparable cases, including mapping, correction and follow-up effort | Results reported with sample size, errors and unresolved evidence |
| Decide next scope | Fix the largest observed friction; prioritize broader formats, access control or integration based on need | Named owner, accepted next milestone and risk/benefit rationale |

These stages are a plan rather than a promised schedule. Timing and acceptance thresholds should be agreed with the customer after discovery.

## Measures that connect the software to value

- Total analyst time per questionnaire, including OCR checks, mapping, inference and corrections.
- Unsupported `met` decisions and corrections to labels or explanations.
- Evidence/source-reference errors and unresolved follow-up requests.
- Review completion and ability to explain the next due-diligence action.
- Setup/training friction and whether reviewers can use the workflow independently.

Do not treat lower latency or a high synthetic label score as proof of customer value. Set pilot thresholds after observing the baseline, and report both improvements and regressions.

## Training and adoption walkthrough

1. Start with the clean showcase: one fictional supplier, one question, cited passages and separate Obsidian guidance. Then open the full review demo or local analyst workspace for a complete questionnaire.
2. Inspect the answer, security requirement and related ISO/NIST topic; distinguish evidence from verified practice.
3. Correct the saved unknown-versus-missing error and explain the change.
4. Complete all human decisions; inspect confirmed gaps versus unresolved-evidence points.
5. Classify the relationship as normal or critical, and discuss proportionate follow-up.
6. Run the full local PDF workflow with a fictional scan, checking page references before inference.

The clean showcase replays a three-question local RAG run using only included public sample rules/memory, with a RAG-only comparison. The full review demo also offers saved five-question runs and an authored 20-question example. These are practice decisions, separate from real review records. The public demo replays saved results; the actual application runs the Open Weight AI model through LM Studio. Obsidian supplies only selected local rules, knowledge and project memory. Reviewers should understand these boundaries before interpreting results.

## Scope decisions

The proposed first pilot focuses on one local analyst, supported JSON/PDF input, supplier-document retrieval and a transparent review record. Select an agreed subset of the 20-question catalog with the customer; the original five-question benchmark does not validate the expanded scope. Excel import, multi-user access, complete validated framework mappings, richer threat/impact assessment and enterprise integration need further implementation. Prioritize them from observed workflow needs rather than expanding the stack prematurely.

## Project iteration already demonstrated

These changes followed feedback during portfolio development, not security-customer research:

- Added local text/scanned-PDF intake with explicit answer mapping.
- Simplified scoring from custom analyst weights to fixed factors and normal/critical supplier classification.
- Replaced internal BUYER labels with supplier-level questionnaires and natural-language questions.
- Added related framework topics with explicit limits, preserving frozen evaluation inputs.

An independent analyst interview and real-world pilot remain next steps.

## Scenario-based next session

Use the [fictional SaaS, managed IT and logistics scenarios](supplier-assessment-scenarios.md) to validate pre-engagement supplier information security decisions with an independent analyst. Identify exposure, required supporting records, remediation owners and who can accept unresolved risk before access or data sharing. Keep regional obligations as discovery questions, not assumptions encoded into the questionnaire score.
