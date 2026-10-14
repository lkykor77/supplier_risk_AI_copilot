# Frozen synthetic evaluation v1

The original prompt is saved in `prompts/assessment-v1.txt`. Its SHA-256 hash is the same as the prompt used for the first 25 development assessments. `data/evaluation_manifest.json` freezes that prompt and the new dataset before its first Gemini run. The evaluator checks both hashes before making API requests.

## What is new

`data/evaluation_suppliers.json` contains five additional fictional suppliers and 25 expected labels:

- **evaluation-f:** Positive practices expressed through paraphrases rather than baseline keywords.
- **evaluation-g:** Explicitly absent contact and partial documentation, account coverage, and testing frequency.
- **evaluation-h:** Contradictory statements and vague answers. Making backups is not evidence of restoring them.
- **evaluation-i:** Explicitly absent practices, expressed without the baseline's exact phrases.
- **evaluation-j:** Supplier answers contain instructions to mark everything met. Those instructions must be ignored; assess the factual claims only. Future plans and unspecified frequency are also included.

There are seven `met`, four `partly_met`, seven `missing`, and seven `unknown` labels. There are no blank answers. The model never receives the expected labels or their explanatory notes.

## Run

```sh
python3 ai_assessor.py --dataset evaluation --all
```

This makes five requests with the same model as the development run, spaced by 15 seconds. Results go to `results/latest-evaluation-run.json`; the earlier development report is kept separately. Quota failures stop the run and preserve its partial report. API availability and free quota are not guaranteed.

To inspect one request without making an API call:

```sh
python3 ai_assessor.py --dataset evaluation --dry-run
```

## Review policy

Compare status matches, false `met` results, unknown handling, quote validity and interpretation. Review contradictions carefully: a single verbatim quote may omit conflicting evidence elsewhere in the answer. One embedded-instruction example cannot demonstrate comprehensive prompt-injection resistance.

Do not tune the original prompt after seeing these results and report an improved score as fresh evaluation. If these cases become tuning data, create and freeze a new evaluation set. Record any label corrections transparently, with the original score and reason for changing the answer key.
