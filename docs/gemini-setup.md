# Connect Gemini locally

This implementation uses Python's standard library and the Gemini REST API. No package installation is required. The default model is `gemini-3.5-flash-lite`; check its current availability and your project's quota in Google AI Studio. Google's pricing page currently lists free input/output tokens for this model on the Free Tier. A paid project may incur charges for the same request. The script cannot detect billing tier and does not change billing settings.

## 1. Save your API key

Open Terminal in this project folder and run:

```sh
python3 setup_key.py
```

Paste your key at the hidden prompt and press Enter. Seeing no characters while pasting is normal. The key is saved to `.gemini-key` with owner-only file permissions. Git ignores this file. Do not paste the key in chat or commit it to GitHub. Alternatively, advanced users can supply `GEMINI_API_KEY` through their environment; it takes precedence over the file.

## 2. Assess one supplier

```sh
python3 ai_assessor.py
```

This makes one API request for `fictional-d`, whose answers include partial practices. The model receives the requirements and answers, but not the expected labels or keyword rules. The script then validates the quotes and prints AI, expected, and baseline statuses side by side. It saves a local report in `results/latest-ai-run.json`.

Check each reason yourself. An exact quote can still be misinterpreted by a model. A successful run is not a compliance verdict or proof of real-world accuracy.

## 3. Compare all five suppliers

After the first request works:

```sh
python3 ai_assessor.py --all
```

This makes five requests, spaced by 15 seconds. It does not retry automatically. Free-tier limits vary by account and model; five requests are not guaranteed to fit your current quota. On failure the script stops and keeps a report marked `complete: false` with any already-completed suppliers. A new run replaces the previous report, so copy a report elsewhere under `results/` if you want to keep it.

These suppliers were used to develop the prompt. Results on them are development measurements, not a held-out benchmark. The expected labels have not been independently reviewed by an analyst.

## Useful commands

To assess new examples with the unchanged prompt, see the [frozen evaluation plan](evaluation-plan.md):

```sh
python3 ai_assessor.py --dataset evaluation --all
```

This uses a separate dataset and saves `results/latest-evaluation-run.json`.

```sh
python3 ai_assessor.py --supplier fictional-c
python3 ai_assessor.py --dry-run
python3 -m unittest discover -s tests -v
```

`--dry-run` prints the request payload without loading a key or calling Gemini. Tests use mocked responses and do not need a key.

## Troubleshooting

The earlier default, `gemini-2.5-flash-lite`, returned HTTP 404 during initial setup. The default is now `gemini-3.5-flash-lite`, verified with one live supplier assessment. Google's [model guide](https://ai.google.dev/gemini-api/docs/models) says access to 2.5 models is restricted to users who previously used them and recommends newer models for new projects. A model appearing in the list does not guarantee that every request will succeed.

- **No key found:** Run `python3 setup_key.py` in the project folder.
- **HTTP 400 / 401 / 403:** Check the key, model, API access and project permissions. Error messages deliberately exclude the provider's response body.
- **HTTP 404:** Check the current model list. Use `--model MODEL_ID` to select a compatible Gemini model with JSON-schema support and available free quota.
- **HTTP 429:** Check quota in AI Studio and wait for the indicated reset. Do not enable paid billing to solve this if your goal is to stay free.
- **Network error:** Check your internet connection. Requests time out after 45 seconds and are not automatically retried.
- **Invalid quote / truncated JSON:** No assessment from that supplier is accepted. Inspect the rubric and request, then retry only after understanding the failure.

The report includes model ID, prompt/dataset hashes, token usage reported by Gemini, latency, quotes, reasons and comparison labels. It does not calculate dollar cost because pricing and billing tier are external configuration.

## Official references

- [API keys](https://ai.google.dev/gemini-api/docs/api-key)
- [Generate content API](https://ai.google.dev/api/generate-content)
- [Structured outputs](https://ai.google.dev/gemini-api/docs/structured-output)
- [Pricing](https://ai.google.dev/gemini-api/docs/pricing)

Continue using fictional data: free-tier data use is governed by Google's terms.
