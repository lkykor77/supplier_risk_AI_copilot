# Frozen synthetic evaluation — local model results

The local Open Weight AI model matched **24/25** draft labels; the keyword baseline matched **8/25**. Median local request latency was **26.086 seconds**. All 25 quotes passed verbatim checks, which do not establish that the quote supports the label.

The unspecified security contact in Supplier H, Question-01 was classified `missing` rather than the expected `unknown`: missing information does not establish an absent practice. A human reviewer must resolve that interpretation.

See [local integration results and limits](local-integration-results.md), the [saved local report](../reports/local-evaluation-run-2026-10-13.json), and the [evaluation plan](evaluation-plan.md). This small synthetic dataset and its draft labels have not been independently validated; these results are not real-world accuracy or verified supplier compliance.
