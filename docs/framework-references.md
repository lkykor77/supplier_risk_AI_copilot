# Supplier questionnaires and framework topic references

Each selected supplier has one questionnaire containing five answers. `Question-01` through `Question-05` are internal security requirement IDs. The interface now presents **Fictional Supplier F · Question 1 of 5**, a natural-language question, that supplier's answer, a security-requirement result, and related framework references.

## Interpretation

The model and human decisions still evaluate the original fictional buyer rubric. Adding a reference does not turn a met buyer requirement into verified ISO or NIST conformity. These are narrow, illustrative topic alignments that require analyst validation; the source datasets, original prompt and stored assessment IDs are unchanged.

| Question | Security requirement | Related ISO/IEC 27001:2022 Annex A topic | Related NIST CSF 2.0 outcome | Boundary |
| --- | --- | --- | --- | --- |
| 1 | Identify a security contact | A.5.2 — security role assignment | GV.RR-02 — cybersecurity responsibilities | A named contact alone does not establish the broader roles, authority and enforcement outcome. |
| 2 | Have a documented incident response plan | A.5.24 — incident preparedness | ID.IM-04 — response planning | Documentation alone does not prove communication, maintenance, improvement or operational readiness. |
| 3 | Review all user access at least annually | A.5.18 — access-rights management | PR.AA-05 — authorization and review | The annual interval is buyer-defined; these references address broader access management. |
| 4 | Require MFA for all administrators | A.8.5 — authentication safeguards | PR.AA-03 — authentication | The all-administrator MFA condition is buyer-defined, not a universal requirement inferred from either reference. |
| 5 | Test backup restoration at least annually | A.8.13 — backup maintenance/testing | PR.DS-11 — backup protection/testing | The annual interval is buyer-defined; broader backup and recovery evidence remains necessary. |

An answer marked met means the answer supports this security requirement criterion. Whether the supplier implements the practice, fulfills a full framework outcome, or has an effective ISMS needs additional evidence and scope-specific assessment. No standard text, certification or complete crosswalk is reproduced here.

## Sources and mapping provenance

- [NIST CSF 2.0 Core, CSWP 29](https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf), Appendix A: outcome identifiers and scope; the descriptions above are paraphrases.
- [ISO/IEC 27001:2022 overview](https://www.iso.org/standard/27001): ISMS context.
- [Published ISO/IEC 27002:2022 sample](https://cdn.standards.iteh.ai/samples/sist/sist-en-iso-iec-27002-2022/2780c93ddd364bd0adfeb4bf5120b169/sist-en-iso-iec-27002-2022.pdf): control identifiers in the table of contents. This is the underlying published standard sample, hosted by its distributor; the full standard is not copied into the project.
- [ISO/IEC JTC 1/SC 27 Journal 2025, pages 18–19](https://committee.iso.org/files/live/sites/jtc1sc27/files/resources/Journal%202025.pdf): the relationship of 27002 reference controls to 27001 Annex A and the importance of context-specific applicability.
