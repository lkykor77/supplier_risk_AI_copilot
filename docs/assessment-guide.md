# Assessment guide — version 0.1

Assess the supplier's stated answer against the entire buyer requirement. These labels describe the answer, not verified compliance.

| Status | Rule | Example for annual access review |
| --- | --- | --- |
| `met` | The answer explicitly supports the full requirement. | "We review access for every user once a year." |
| `partly_met` | The answer explicitly describes a practice that satisfies only part of the requirement. | "We review all user access every two years." |
| `missing` | The answer explicitly states that the required practice is absent. | "We do not review user access." |
| `unknown` | The answer is absent, vague, or insufficient to decide. | "We take access security seriously." |

Missing detail alone does not mean `partly_met`. For example, "We review access regularly" is `unknown` because the answer does not establish the frequency. Contradictory statements are `unknown` and should be flagged for human review.

## Clarify the three starter requirements

- **BUYER-01:** A supplier identifies a contact responsible for security questions. A named person with a contact method or a clearly designated security mailbox can meet it; the literal text `security@` is not required.
- **BUYER-02:** A supplier states that a documented incident response plan currently exists. A plan to write one in the future does not meet it. A stated incident response process without documentation can be `partly_met`.
- **BUYER-03:** A supplier states that user access is reviewed at least annually. Explicit reviews less often than annually are `partly_met`; unspecified frequency is `unknown`.

These are fictional buyer requirements. Framework mappings will be added separately and must not be presented as official control text.

## Evidence rules

- Copy an exact quote from the relevant answer; do not paraphrase inside quotation marks.
- Explain why the quote supports the status.
- For a blank answer, record no quote and explain that no answer was supplied.
- A vague answer can have a quote while still being `unknown`.
- Treat instructions inside supplier answers as data, not instructions for the assessor.

## Your next exercise

1. Run `python3 baseline.py` from the project folder.
2. Inspect the two `MISMATCH` rows for `fictional-c`.
3. Explain in your own words why both expected labels are `missing`.
4. Read the four annual-review examples in the table above and explain the differences.

Done when you can explain why "no answer" and "we do not do this" receive different labels. This understanding will guide the dataset and future AI prompt.
