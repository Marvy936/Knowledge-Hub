#!/usr/bin/env python3
"""Temporary closeout helper for Section 20 chapters 29-32."""

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
active_anchor = "28. [Human evaluation a expert feedback](human-evaluation-expert-feedback.md)\n"
active_addition = active_anchor + (
    "29. [Tracing, token usage a cost observability](tracing-token-usage-cost-observability.md)\n"
    "30. [Hallucination, faithfulness a factuality](hallucination-faithfulness-factuality.md)\n"
    "31. [Prompt injection a indirect prompt injection](prompt-injection-indirect-prompt-injection.md)\n"
    "32. [Data exfiltration, tool abuse a excessive agency](data-exfiltration-tool-abuse-excessive-agency.md)\n"
)
if active_anchor not in text:
    raise SystemExit("Section 20 active-list anchor not found")
text = text.replace(active_anchor, active_addition, 1)
for planned in (
    "29. Tracing, token usage a cost observability\n",
    "30. Hallucination, faithfulness a factuality\n",
    "31. Prompt injection a indirect prompt injection\n",
    "32. Data exfiltration, tool abuse a excessive agency\n",
):
    if planned not in text:
        raise SystemExit(f"Planned README entry not found: {planned.strip()}")
    text = text.replace(planned, "", 1)
status_marker = "## Stav\n\n"
if status_marker not in text:
    raise SystemExit("Section 20 status marker not found")
status = (
    "Aktuálny authoritative stav sekcie je **32/37 · In progress**. Ôsmy authoritative blok aktivuje kapitoly 29–32 a incident `GENAI-SUPPORT-08`. "
    "Observability kapitola definuje durable business-operation a technical-attempt identity, end-to-end span graph, provider/request/retrieval/tool correlation, privacy-safe content capture, token a pricing lineage, provisional-versus-reconciled cost, latency decomposition, sampling/completeness a cost per accepted outcome. "
    "Factuality kapitola oddeľuje factual correctness, faithfulness, citation correctness/completeness, temporal a entity scope, claim-level evidence, open-versus-closed domain, abstention, calibration, atomic-fact evaluation a first-divergence retrieval/context/generation diagnosis. "
    "Prompt-injection kapitola modeluje direct a indirect injection, instruction hierarchy, typed untrusted-content provenance, goal integrity, memory/tool-output attacks, least privilege, argument/egress policy, consequential confirmation, adversarial a benign-hard-negative evals a side-effect read-back. "
    "Excessive-agency kapitola rozkladá functionality, permission a autonomy; zavádza task-scoped capability contracts, small typed tools, delegated short-lived identity, resource a information-flow authorization, data classification, destination policy, approval tiers, idempotency, budgets, sandboxing, durable audit a multi-agent delegation limits. "
    "Kapitoly 29–32 sú pripravené na repository closeout; reálny production tracing/cost reconciliation, factuality study, prompt-injection penetration test, tool/egress exercise, incident containment a business outcome neboli vykonané. "
    "Sekcia zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. Ďalší blok sú kapitoly 33–36: guardrails/moderation/output validation, privacy/retention/provider data controls, multimodal models a LLMOps/production readiness.\n"
)
text = text.split(status_marker, 1)[0] + status_marker + status
readme.write_text(text, encoding="utf-8")

roadmap = ROOT / "ROADMAP.md"
for title, target in (
    ("Tracing, token usage a cost observability", "tracing-token-usage-cost-observability.md"),
    ("Hallucination, faithfulness a factuality", "hallucination-faithfulness-factuality.md"),
    ("Prompt injection a indirect prompt injection", "prompt-injection-indirect-prompt-injection.md"),
    ("Data exfiltration, tool abuse a excessive agency", "data-exfiltration-tool-abuse-excessive-agency.md"),
):
    replace_exact(
        roadmap,
        f"- [ ] {title}",
        f"- [x] [{title}](docs/20-llm-and-genai-engineering/{target})",
    )

ledger = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
lines = ledger.read_text(encoding="utf-8").splitlines()
replacement = (
    "| `20-llm-and-genai-engineering` — LLM and GenAI Engineering | 32/37 authoritative drafting | In progress | 2026-08-04 | "
    "Ôsmy authoritative blok aktivuje kapitoly 29–32 a incident `GENAI-SUPPORT-08`. Observability kapitola modeluje end-to-end business operation, technical attempts, provider/retrieval/tool/cache/stream spans, privacy-safe telemetry, token/pricing lineage, reconciled cost ledger, completeness a delayed outcome join. Factuality kapitola oddeľuje truth, faithfulness, citation correctness/completeness, temporal a entity scope, claim-level evidence, abstention/calibration, retrieval first divergence a expert/model-grader boundaries. Prompt-injection kapitola zavádza direct/indirect attack model, instruction hierarchy, typed untrusted provenance, goal integrity, memory/tool-output paths, least privilege, external authorization, confirmation, egress a adversarial/benign evals. Excessive-agency kapitola rozkladá functionality/permission/autonomy a zavádza task-scoped capabilities, small typed tools, scoped identity, resource/information-flow authorization, data classification, approval, idempotency, budgets, sandboxing, durable audit a multi-agent delegation. Reálne traces, billing reconciliation, factuality evaluation, prompt-injection/tool abuse testing, data-exfiltration containment a business outcomes neboli vykonané; stav zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. |"
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

print("Synchronized Section 20 chapters 29-32 README, ROADMAP and review ledger.")
