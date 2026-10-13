# Local Qwen and Obsidian integration

## Architecture

The Python CLI calls a native LM Studio server through its OpenAI-compatible local API. Gemini remains a separate comparison provider. All local inference is sequential, with no automatic cloud fallback or retries. No Python dependencies are required.

Docker is not necessary for this workflow. oMLX is an optional alternative local server; it is not started alongside LM Studio. Its OpenAI-compatible endpoint can be configured later, but model format, schema support and settings must be tested for that runtime. The current integration is verified against LM Studio first.

## Start LM Studio

Load Qwen in LM Studio and start the Developer server on localhost, usually port 1234. Use the model ID returned by:

```sh
python3 local_assessor.py --check-server
```

The project's default is `qwen/qwen3.8-27b`. Save private configuration in `.local-config.json`, based on `local-config.example.json`. The actual config is Git-ignored. If server authentication is enabled, set `LOCAL_MODEL_API_KEY` locally; do not place secrets in the example config.

The assessor sends `reasoning_effort: none`, verified on this Qwen MLX model. In the initial live test, schema-constrained JSON appeared in `reasoning_content` while the final answer was empty. Explicit non-thinking mode returned valid JSON in the final answer. The app never uses hidden reasoning as an assessment. A new model or runtime may support different reasoning controls; verify the setting before switching.

## First comparison: unchanged prompt

```sh
python3 local_assessor.py
python3 local_assessor.py --dataset evaluation --all
```

The first command assesses `fictional-d`. The second uses all five frozen evaluation suppliers with the same assessment instructions used for Gemini. Provider-specific request formatting and sampling settings differ and are recorded in the local report. Record LM Studio runtime version, model quantization, thinking mode, and context length separately before interpreting results. Local model loading and thinking may require a longer timeout than Gemini.

Report names are separate from the existing Gemini reports:

- `results/latest-local-development-baseline-prompt.json`
- `results/latest-local-evaluation-baseline-prompt.json`

## Obsidian rules, knowledge, and memory

Configure an absolute `vault_path` and three allowlists:

- `rule_notes`: approved guidance relevant to the current assessment. The initial selection is the user's constitution, core rules and output rules. This is an analysis workflow, so coding/tool modules are not loaded.
- `knowledge_notes`: selected reference notes. They are context, not instructions or evidence of supplier practices.
- `memory_notes`: this application's dedicated project-memory note.

The app reads the selected Markdown files again for each CLI run. Notes are not permanently learned by the model. Files are limited to the vault, including symlink resolution, and context is capped at 12,000 characters. No recursive vault scan or automatic model-generated edits to rules occur.

Personal Hermes notes may mention different servers or models. Those descriptions do not configure this application. The app's structured response contract and supplier evidence rubric remain mandatory. Approved vault rules are supplemental guidance for assessment explanations.

```sh
python3 local_assessor.py --with-vault --dry-run
python3 local_assessor.py --with-vault --save-memory
```

The dry run prints only note names and hashes, not note contents. The live run sends selected notes only to the loopback server. It records note hashes and effective prompt/context hashes in a private local report.

Adding vault rules changes the assessment context, so vault-enhanced runs are separate experiments. `--with-vault --dataset evaluation` is rejected to protect the original frozen comparison. A future evaluation with vault context needs its own frozen notes and fresh cases.

## Saving persistent project memory

`--save-memory` writes a concise completed-run summary to `Supplier Risk Copilot/project-memory.md` and a separate run-history note in that folder. Only the app-owned note, marked with its ownership comment, may be updated. Existing personal notes are preserved. The initial project note is created during setup.

No keys, raw supplier answers, full private rules, or expected labels are written into these memory summaries. Current project memory is loaded on a subsequent `--with-vault` run. Keep knowledge notes factual; do not turn previous model decisions into unquestioned assessment rules.

Vault paths, personal notes, raw local reports and debug responses are excluded from the public repository. Publish only explicitly reviewed synthetic reports later.

## Troubleshooting

- Unavailable server: start LM Studio's Developer server and confirm the port.
- Unknown model: use `--check-server` and configure the exact ID.
- Timeout or incomplete output: check thinking mode, context, memory pressure and output budget. The app rejects incomplete responses.
- Invalid JSON: check runtime version and JSON-schema support. The app does not accept a malformed assessment as a successful result.
- Missing note: correct the allowlist or create the dedicated project-memory note. The app does not silently skip requested rules.
- HTTP 401/403: configure a local server token through `LOCAL_MODEL_API_KEY`.

For an oMLX experiment, set `base_url` to its loopback `/v1` URL and `model` to a model served by that runtime. This does not convert or download model weights. Start only the server you intend to use.

Official references: [LM Studio local chat API](https://lmstudio.ai/docs/developer/openai-compat/chat-completions), [structured outputs](https://lmstudio.ai/docs/developer/openai-compat/structured-output).
