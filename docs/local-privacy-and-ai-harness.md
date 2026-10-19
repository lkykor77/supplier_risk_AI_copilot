# Confidential supplier evidence and the custom AI harness

## Customer constraint and deployment decision

Supplier security submissions can contain confidential policies, infrastructure descriptions and incident procedures. The project chooses local processing so the reviewer can assess those documents without sending their contents to a cloud AI provider. Privacy is a reason for this deployment choice, not a claim that local models are inherently more accurate.

**Within the implemented local workflow, supplier documents, extracted answers, prompts, selected Obsidian context, model results and review records remain on the user’s computer. The application does not upload that content to cloud AI.**

## Benefits and practical limits

| Benefit | What the project provides | Practical limit |
| --- | --- | --- |
| Confidential evidence processing | On-device PDF/OCR, loopback LM Studio inference and local persistence | The app does not control OS, vault sync, backups, remote access or exports |
| Inference control | Supported model choice, settings, prompts, context selection and traceable outputs | Each model/runtime change requires validation; Open Weight does not mean every license permits every use |
| Independence from cloud inference | No provider inference account/quota or cloud fallback needed for the local path | Model/runtime/packages and OCR language files must be obtained first |
| Local operating option | LM Studio supports offline operation after setup | This project has not independently tested a fully disconnected end-to-end run; downloads and update checks are separate network operations |
| No per-request cloud inference bill | Local assessment uses the user’s hardware | Hardware, memory, electricity and setup have costs; the measured local run was slower than the saved cloud run |

[LM Studio’s offline-operation documentation](https://lmstudio.ai/docs/app/offline) describes downloaded-model inference and local-server use without internet access. [Structured-output documentation](https://lmstudio.ai/docs/developer/openai-compat/structured-output) describes JSON-schema response constraints. The application also validates received results rather than trusting model output alone.

## What the custom Python AI harness means here

The harness is the code that prepares, executes and checks model use. It is a bounded assessment workflow rather than an autonomous agent or a separately installed agent framework.

1. Prepare the buyer rubric and supplier answers without the answer key.
2. Load only explicitly selected Obsidian rules, knowledge and project memory, with path containment and context limits.
3. Call the locally hosted Open Weight AI model through LM Studio with a structured response schema.
4. Reject non-local URLs, redirects, incomplete final output, malformed coverage and non-verbatim evidence quotes.
5. Preserve validated model suggestions; the review application stores human decisions separately and gates risk scoring until review is complete.

LM Studio serves the model. The custom Python harness manages the application’s use of it. Obsidian supplies selected context, not supplier evidence; no recursive personal-vault import is performed.

## Implementation evidence

| Boundary or responsibility | Code evidence |
| --- | --- |
| Analyst UI on loopback | `review_app.py` binds to `127.0.0.1` and serves specific application routes |
| Local document extraction | `pdf_intake.py`, `helpers/pdf_extract.swift`, `helpers/ocr_pages.cjs` use on-device extraction/OCR and locally installed language assets |
| Request preparation and output parsing | `local_assessor.py`: `local_payload`, `parse_local` |
| Local inference routing | `local_assessor.py`: `checked_url` accepts loopback hostnames only; `request_json` disables HTTP proxies; `NoRedirect` refuses redirects |
| Evidence and coverage checks | `assessment.py`: `validate_assessment` |
| Selected Obsidian context | `vault_context.py`: `note_path`, `load_context`, `save_memory` |
| Human accountability | `review_store.py` preserves model snapshots, separate reviewer records and revision history |
| Public/private separation | `.gitignore` excludes private runtime files; `.github/workflows/pages.yml` publishes only `showcase/` |

Existing tests in `tests/test_local.py` and `tests/test_pdf_intake.py` cover endpoint restrictions, redirects, context containment, private answer-key separation, memory boundaries, PDF mapping and review integration. These checks do not establish the security of every application on the computer.

## Privacy boundary and operating conditions

Use the local PDF workflow or `local_assessor.py` for confidential material. Keep LM Studio serving on loopback and avoid adding network serving, remote inference or external tools to this workflow. Store confidential evidence and sensitive selected vault context in approved local locations, and review independent sync/backup settings.

The repository supports local model inference only. Installing models, runtimes, packages and OCR assets, checking updates, accessing GitHub Pages, or deliberately exporting records may involve network access. Independently configured Obsidian/iCloud sync, backups, extensions, malware or remote-access software can transmit information outside the app.

Consequently, “this local workflow does not upload supplier content to cloud AI” is supported by the application design. “Nothing can ever leave the computer” would overstate what the application controls. Local storage is not a substitute for endpoint security, access control, retention policy or an approved supplier-risk process. The public demo contains fictional saved results and accepts no document uploads.
