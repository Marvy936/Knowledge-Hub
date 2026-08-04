#!/usr/bin/env python3
"""Temporary closeout helper for Section 20 chapters 33-36."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs/20-llm-and-genai-engineering"


def replace_exact(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"Expected text not found in {path}: {old[:120]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


readme = SECTION / "README.md"
text = readme.read_text(encoding="utf-8")
active_anchor = "32. [Data exfiltration, tool abuse a excessive agency](data-exfiltration-tool-abuse-excessive-agency.md)\n"
active_addition = active_anchor + (
    "33. [Guardrails, moderation a output validation](guardrails-moderation-output-validation.md)\n"
    "34. [Privacy, retention a provider data controls](privacy-retention-provider-data-controls.md)\n"
    "35. [Multimodal models](multimodal-models.md)\n"
    "36. [LLMOps a production readiness](llmops-production-readiness.md)\n"
)
if active_anchor not in text:
    raise SystemExit("Section 20 active-list anchor not found")
text = text.replace(active_anchor, active_addition, 1)
for planned in (
    "33. Guardrails, moderation a output validation\n",
    "34. Privacy, retention a provider data controls\n",
    "35. Multimodal models\n",
    "36. LLMOps a production readiness\n",
):
    if planned not in text:
        raise SystemExit(f"Planned README entry not found: {planned.strip()}")
    text = text.replace(planned, "", 1)
status_marker = "## Stav\n\n"
if status_marker not in text:
    raise SystemExit("Section 20 status marker not found")
status = (
    "Aktuálny authoritative stav sekcie je **36/37 · In progress**. Deviaty authoritative blok aktivuje kapitoly 33–36 a incident `GENAI-SUPPORT-09`. "
    "Guardrails kapitola oddeľuje detector signal, policy decision a enforcement cez input, context, model output, tool call/response a egress; zavádza schema a business validation, calibration, fail modes, streaming, multimodálne controls, human review, adversarial evals a complete rollback. "
    "Privacy kapitola modeluje exact provider/product/endpoint/region/feature subject, training usage versus abuse logs versus application state, files/caches/memory/tools/telemetry/evals/customization, data residency, minimization, encryption, deletion graph, backups, policy as code a runtime read-back. "
    "Multimodálna kapitola viaže raw media digest na image/audio/video/document preprocessing, OCR/STT, spatial/temporal/speaker evidence, context budget, cost, safety/privacy, task-specific metrics, cross-modal consistency a recovery. "
    "LLMOps kapitola definuje immutable composed release cez model, prompt, corpus/index, tools/schemas, guardrails, privacy, preprocessing, caches, evals, infra a code; pokrýva lifecycle, registries, CI/eval gates, shadow/canary, SLOs, drift, incident containment, rollback, fallback, continuous improvement a decommissioning. "
    "Kapitoly 33–36 sú pripravené na repository closeout; reálna moderation/guardrail calibration, provider retention/deletion verification, multimodálne evals, load/canary, rollback drill a business outcome neboli vykonané. "
    "Sekcia zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. Posledná kapitola sekcie je 37: LLM application troubleshooting.\n"
)
text = text.split(status_marker, 1)[0] + status_marker + status
readme.write_text(text, encoding="utf-8")

roadmap = ROOT / "ROADMAP.md"
for title, target in (
    ("Guardrails, moderation a output validation", "guardrails-moderation-output-validation.md"),
    ("Privacy, retention a provider data controls", "privacy-retention-provider-data-controls.md"),
    ("Multimodal models", "multimodal-models.md"),
    ("LLMOps a production readiness", "llmops-production-readiness.md"),
):
    replace_exact(
        roadmap,
        f"- [ ] {title}",
        f"- [x] [{title}](docs/20-llm-and-genai-engineering/{target})",
    )

ledger = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
lines = ledger.read_text(encoding="utf-8").splitlines()
replacement = (
    "| `20-llm-and-genai-engineering` — LLM and GenAI Engineering | 36/37 authoritative drafting | In progress | 2026-08-04 | "
    "Deviaty authoritative blok aktivuje kapitoly 33–36 a incident `GENAI-SUPPORT-09`. Guardrails kapitola modeluje intervention points, detector/policy/enforcement chain, schema a business invariants, calibration, fail behavior, streaming, multimodálne controls, human review, adversarial evals a rollback. Privacy kapitola oddeľuje training usage, abuse logs a application state a pokrýva provider/product/endpoint/region/feature matrix, files, caches, memory, tools, telemetry, evals, customization, residency, minimization, encryption, deletion/backups, policy as code a read-back. Multimodálna kapitola modeluje immutable media artifacts, preprocessing, OCR/STT, image/audio/video/document grounding, token/cost/latency, injection, safety/privacy a task-specific evaluation. LLMOps kapitola skladá model, prompt, corpus/index, tools, guardrails, privacy, preprocessing, caches, eval suite, infra a code do immutable release manifestu s lifecycle, gates, canary, drift detection, SLOs, incident response, rollback, fallback a decommissioning. Reálna calibration, provider retention/deletion verification, multimodálne evals, production load/canary, rollback drill a business outcomes neboli vykonané; stav zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. |"
)
found = False
for index, line in enumerate(lines):
    if line.startswith("| `20-llm-and-genai-engineering`"):
        lines[index] = replacement
        found = True
        break
if not found:
    raise SystemExit("Section 20 ledger row not found")
ledger.write_text("\n".join(lines) + "\n", encoding="utf-8")

print("Synchronized Section 20 chapters 33-36 README, ROADMAP and review ledger.")
