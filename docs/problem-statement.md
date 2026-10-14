# Problem statement — draft to validate

A supplier-security analyst needs to evaluate prospective suppliers against the buyer's security requirements, which may draw on ISO/IEC 27001, NIST CSF, contractual terms, and applicable regulations. Supplier evidence arrives as standard questionnaires, spreadsheets, selectable-text PDFs, scans, and documents with inconsistent formats.

Finding relevant answers, interpreting vague or contradictory claims, tracking source references, and documenting decisions involves repetitive manual work. Baseline review time and assisted-review savings have not been measured. No universal “average hours” figure is claimed.

The proposed tool extracts supported PDF evidence locally, requires analyst confirmation, suggests structured statuses with evidence quotes, and retains human decisions separately. After complete human review, a deterministic weighted control-gap indicator supports follow-up prioritization. Unknown evidence remains visible; critical suppliers receive enhanced-review flags for non-met answers.

Current scope is five fictional buyer requirements, JSON/PDF input, local AI and optional Obsidian context, human review and questionnaire-gap scoring. Full framework mappings, Excel import, regulatory checks and real-supplier validation remain future work. The tool supports the assessment process; it does not certify compliance, verify supplier practices or make acceptance decisions.

## Validation measures

- Manual and assisted review time per questionnaire, including mapping and correction effort.
- Corrections to labels and explanations; unsupported positive assessments.
- Evidence retrieval errors, OCR corrections and source-reference accuracy.
- Follow-up requests and analyst confidence in the review record.
- Independent rubric validation and weighting-policy review.

## Discovery questions

1. Which formats and layouts arrive most often, and what takes the most time?
2. Which buyer requirements are mandatory for each supplier/service context?
3. How are access, data sensitivity, criticality, impact and risk acceptance assessed today?
4. What evidence is needed to distinguish missing from unknown?
5. Who approves the rubric, risk criteria and supplier decision?

Use fictional examples in initial interviews. Record actual findings; do not invent user feedback.
