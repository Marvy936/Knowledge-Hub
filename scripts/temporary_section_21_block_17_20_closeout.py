#!/usr/bin/env python3
"""Temporary closeout helper for Section 21 chapters 17-20."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs/21-ai-agents-and-intelligent-automation"


def replace_exact(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"Expected text not found in {path}: {old[:160]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


readme = SECTION / "README.md"
text = readme.read_text(encoding="utf-8")
active_anchor = "16. [Prompt injection cez tools a retrieved content](prompt-injection-tools-retrieved-content.md)\n"
active_addition = active_anchor + (
    "17. [Tool poisoning, confused deputy a data exfiltration](tool-poisoning-confused-deputy-data-exfiltration.md)\n"
    "18. [Agent evaluation](agent-evaluation.md)\n"
    "19. [Trajectory, tool-selection a outcome evaluation](trajectory-tool-selection-outcome-evaluation.md)\n"
    "20. [Agent tracing, replay a debugging](agent-tracing-replay-debugging.md)\n"
)
if active_anchor not in text:
    raise SystemExit("Section 21 active-list anchor not found")
text = text.replace(active_anchor, active_addition, 1)

for planned in (
    "17. Tool poisoning, confused deputy a data exfiltration\n",
    "18. Agent evaluation\n",
    "19. Trajectory, tool-selection a outcome evaluation\n",
    "20. Agent tracing, replay a debugging\n",
):
    if planned not in text:
        raise SystemExit(f"Planned README entry not found: {planned.strip()}")
    text = text.replace(planned, "", 1)

status_marker = "## Stav\n\n"
if status_marker not in text:
    raise SystemExit("Section 21 status marker not found")
status = (
    "Aktuálny authoritative stav sekcie je **20/62 · In progress**. Piaty authoritative blok aktivuje kapitoly 17–20 a incident `AGENT-EVAL-05`. "
    "Tool-security kapitola spája exact host/server/tool/catalog/schema a implementation generation, publisher provenance, untrusted metadata a outputs, schema/description/error poisoning, OAuth audience a resource separation, delegation verzus impersonation, per-client consent, tenant binding, source/sink inventory, data minimization, opaque handles, egress/SSRF, tool chaining, remote deputies, telemetry leaks a descendant-effect reconciliation. "
    "Agent-evaluation kapitola definuje composed-release subject, capability a forbidden invariants, component/integration/end-to-end vrstvy, offline/simulation/shadow/canary proof boundaries, representative a risk-weighted datasets, slices, adversarial/synthetic/production cases, deterministic/model/human graders, calibration, repeated runs, uncertainty, environment fidelity, fault injection, cost/latency/security/business outcomes, release gates a continuous production-gap monitoring. "
    "Trajectory kapitola hodnotí observable events bez požiadavky na private chain-of-thought: exact identities a generations, event taxonomy, partial-order graph, step/transition/tool/argument/handoff/planning/retry/recovery/termination quality, memory a approval side effects, authoritative technical/business/security/privacy outcomes, efficiency, loops, alternative valid paths, counterfactuals, trace compression a deterministic/model graders. "
    "Tracing kapitola oddeľuje logs, metrics, traces a authoritative audit, zavádza root/span/link/context identity, sensitive-data a secure-reference policy, sampling/export-loss/completeness boundaries, schema versioning, deterministic workflow, recorded-response, simulator a model/tool re-execution replay, historical dependency pinning, side-effect isolation, debugging ladder, evidence freeze, causal timeline, first divergence a trace diff. "
    "Kapitoly 17–20 sú pripravené na repository closeout; reálne poisoned tools, credentials, data exfiltration, eval runs, traces, replays, incident recovery ani business outcomes neboli vykonané. "
    "Sekcia zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. Ďalší blok sú kapitoly 21–24: cost/latency/token budgets, reliability/fallback/kill switch, multi-tenant isolation a agent governance/audit.\n"
)
text = text.split(status_marker, 1)[0] + status_marker + status
readme.write_text(text, encoding="utf-8")

roadmap = ROOT / "ROADMAP.md"
for title, target in (
    ("Tool poisoning, confused deputy a data exfiltration", "tool-poisoning-confused-deputy-data-exfiltration.md"),
    ("Agent evaluation", "agent-evaluation.md"),
    ("Trajectory, tool-selection a outcome evaluation", "trajectory-tool-selection-outcome-evaluation.md"),
    ("Agent tracing, replay a debugging", "agent-tracing-replay-debugging.md"),
):
    replace_exact(
        roadmap,
        f"- [ ] {title}",
        f"- [x] [{title}](docs/21-ai-agents-and-intelligent-automation/{target})",
    )

ledger = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
lines = ledger.read_text(encoding="utf-8").splitlines()
replacement = (
    "| `21-ai-agents-and-intelligent-automation` — AI Agents and Intelligent Automation | 20/62 authoritative drafting | In progress | 2026-08-04 | "
    "Piaty authoritative blok aktivuje kapitoly 17–20 a incident `AGENT-EVAL-05`. Tool-security kapitola viaže exact tool/catalog/schema/implementation generation, publisher provenance, untrusted metadata/outputs, OAuth audience a delegated authority na source/sink data-flow, egress, SSRF, tool-chain a descendant-effect controls. Agent evaluation definuje composed-release subject, capability a forbidden invariants, representative/risk slices, controlled environment, deterministic/model/human graders, calibration, repeated runs, uncertainty, hard release gates a production-gap monitoring. Trajectory evaluation hodnotí observable events, partial-order constraints, tools/arguments/handoffs/planning/retries/approvals/data flows/termination a authoritative technical/business/security outcome bez vyžadovania private chain-of-thought. Tracing kapitola oddeľuje traces od audit ledgeru, pokrýva context propagation, secure evidence references, sampling/export loss, completeness, schema evolution, štyri replay režimy, historical dependency pinning, side-effect isolation, first divergence a trace diff. Reálne poisoned tools, credential misuse, data exposure, eval runs, traces, replays, incident recovery a business outcomes neboli vykonané; stav zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. |"
)
found = False
for index, line in enumerate(lines):
    if line.startswith("| `21-ai-agents-and-intelligent-automation`"):
        lines[index] = replacement
        found = True
        break
if not found:
    raise SystemExit("Section 21 ledger row not found")
ledger.write_text("\n".join(lines) + "\n", encoding="utf-8")

print("Synchronized Section 21 chapters 17-20 README, ROADMAP and review ledger.")
