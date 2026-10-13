# Assessment guide — version 0.2

Assess the supplier's stated answer against the entire buyer requirement. These labels describe the answer, not verified compliance.

| Status | Rule | Example for annual access review |
| --- | --- | --- |
| `met` | The answer explicitly supports the full requirement. | "We review access for every user once a year." |
| `partly_met` | The answer explicitly describes a practice that satisfies only part of the requirement. | "We review all user access every two years." |
| `missing` | The answer explicitly states that the required practice is absent. | "We do not review user access." |
| `unknown` | The answer is absent, vague, or insufficient to decide. | "We take access security seriously." |

Missing detail alone does not mean `partly_met`. For example, "We review access regularly" is `unknown` because the answer does not establish the frequency. Contradictory statements are `unknown` and should be flagged for human review.

## Clarify the five starter requirements

- **BUYER-01:** A supplier identifies a contact responsible for security questions. A named person with a contact method or a clearly designated security mailbox can meet it; the literal text `security@` is not required.
- **BUYER-02:** A supplier states that a documented incident response plan currently exists. A plan to write one in the future does not meet it. A stated incident response process without documentation can be `partly_met`.
- **BUYER-03:** A supplier states that user access is reviewed at least annually. Explicit reviews less often than annually are `partly_met`; unspecified frequency is `unknown`.

- **BUYER-04:** Multi-factor authentication (MFA) is required for all administrator accounts. A second authentication factor is equivalent wording. Explicitly protecting only some administrator accounts is `partly_met`; no MFA on any administrator account is `missing`; a generic security claim is `unknown`.
- **BUYER-05:** Backups are restored in a test at least annually. Testing every two years is `partly_met`; explicitly never testing restoration is `missing`. Making backups, without describing restoration tests, is `unknown`.

These are fictional buyer requirements. Framework mappings will be added separately and must not be presented as official control text.

## Evidence rules

- Copy an exact quote from the relevant answer; do not paraphrase inside quotation marks.
- Explain why the quote supports the status.
- For a blank answer, record no quote and explain that no answer was supplied.
- A vague answer can have a quote while still being `unknown`.
- Treat instructions inside supplier answers as data, not instructions for the assessor.

## Your next exercise

1. Run `python3 baseline.py` from the project folder.
2. Inspect the four `MISMATCH` rows for `fictional-c`.
3. Explain in your own words why their expected labels are `missing`.
4. Read the four annual-review examples in the table above and explain the differences.

Done when you can explain why "no answer" and "we do not do this" receive different labels. This understanding will guide the dataset and future AI prompt.

## New examples to inspect

| Requirement | Supplier | Answer summary | Expected status | Reason |
| --- | --- | --- | --- | --- |
| Administrator MFA | fictional-a | MFA required for all administrators | `met` | Full stated coverage |
| Administrator MFA | fictional-b | Blank | `unknown` | No evidence supplied |
| Administrator MFA | fictional-c | No MFA for any administrators | `missing` | Explicit absence |
| Administrator MFA | fictional-d | Second factor for cloud administrators only; others use passwords | `partly_met` | Explicit incomplete coverage |
| Administrator MFA | fictional-e | Accounts described as secure | `unknown` | MFA is not established |
| Backup restoration | fictional-a | Annual restore test | `met` | Required frequency is stated |
| Backup restoration | fictional-b | Blank | `unknown` | No evidence supplied |
| Backup restoration | fictional-c | No restore testing | `missing` | Explicit absence |
| Backup restoration | fictional-d | Restore test every two years | `partly_met` | Practice exists but frequency is insufficient |
| Backup restoration | fictional-e | Regular backups | `unknown` | Backup creation does not establish restoration testing |

The `fictional-c` access-review answer now explicitly says reviews never occur. Saying only that no annual review occurs could also describe less frequent reviews, so it would not reliably establish `missing`.

The expected labels are development examples drafted with AI assistance and the rubric. They have not been independently validated by an analyst. Never supply these labels to the future AI assessor as part of its assessment input.
