"""Load explicitly selected Obsidian notes and save app-owned project memory."""

import hashlib
import json
from pathlib import Path


def note_path(vault: Path, relative: str) -> Path:
    """Require Markdown paths contained inside the configured vault."""
    path = (vault / relative).resolve()
    if not path.is_relative_to(vault.resolve()) or path.suffix != ".md":
        raise ValueError("Vault note must be a Markdown file inside the vault.")
    return path


def load_context(config: dict) -> tuple[dict, list]:
    """Read allowlisted notes, never scan a vault or route from model output."""
    if not config.get("vault_path"):
        raise ValueError("Configure vault_path in .local-config.json first.")
    vault = Path(config["vault_path"]).expanduser().resolve()
    context = {"rules": [], "knowledge": [], "memory": []}
    sources = []
    total = 0
    for group, field in [("rules", "rule_notes"), ("knowledge", "knowledge_notes"), ("memory", "memory_notes")]:
        for relative in config.get(field, []):
            path = note_path(vault, relative)
            text = path.read_text(encoding="utf-8")
            total += len(text)
            if total > 12000:
                raise ValueError("Selected vault context exceeds 12,000 characters. Select fewer notes.")
            context[group].append({"note": relative, "text": text})
            sources.append({"group": group, "note": relative,
                            "sha256": hashlib.sha256(text.encode()).hexdigest()})
    return context, sources


def save_memory(config: dict, report: dict) -> Path:
    """Update only a dedicated app-owned memory file; never edit personal rules."""
    vault = Path(config["vault_path"]).expanduser().resolve()
    path = note_path(vault, config.get("project_memory_note", "Supplier Risk Copilot/project-memory.md"))
    marker = "<!-- supplier-risk-copilot-owned-memory -->"
    previous = path.read_text(encoding="utf-8") if path.exists() else ""
    if previous and not previous.startswith(marker):
        raise ValueError("Memory note already contains user content; choose a separate app-owned note.")
    if not report.get("complete"):
        raise ValueError("Only completed assessments can be saved as project memory.")
    summary = report["summary"]
    text = f"""{marker}
# Supplier Risk Copilot — project memory

- Last run: {report['created_at']}
- Provider: local; model: {report['model']}
- Dataset: {report['dataset']}; context: {report['context_mode']}
- AI labels matched: {summary['ai_correct']}/{summary['total']}
- Keyword labels matched: {summary['baseline_correct']}/{summary['total']}
- Effective prompt hash: {report['prompt_sha256']}
- This is synthetic, AI-assisted evaluation; labels need analyst review.
- Next: inspect mistakes and build a human review screen.

This file is maintained by the project CLI only when --save-memory is selected.
Assessment rules remain in the user's approved rule notes. No raw answers, keys,
private rule text or expected labels are copied here.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    # Keep a separate immutable summary for each completed run.
    history = note_path(vault, "Supplier Risk Copilot/Run history/" + report["run_id"] + ".md")
    history.parent.mkdir(parents=True, exist_ok=True)
    with history.open("x", encoding="utf-8") as handle:
        handle.write(text)
    return path
