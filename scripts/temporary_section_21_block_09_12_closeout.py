#!/usr/bin/env python3
"""Temporary closeout helper for Section 21 chapters 9-12."""

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
active_anchor = "8. [Human-in-the-loop a approval gates](human-in-the-loop-approval-gates.md)\n"
active_addition = active_anchor + (
    "9. [Durable execution, retries a resumability](durable-execution-retries-resumability.md)\n"
    "10. [Idempotency a side-effect control](idempotency-side-effect-control.md)\n"
    "11. [Model Context Protocol](model-context-protocol.md)\n"
    "12. [Agent interoperability a protocol evolution](agent-interoperability-protocol-evolution.md)\n"
)
if active_anchor not in text:
    raise SystemExit("Section 21 active-list anchor not found")
text = text.replace(active_anchor, active_addition, 1)

for planned in (
    "9. Durable execution, retries a resumability\n",
    "10. Idempotency a side-effect control\n",
    "11. Model Context Protocol\n",
    "12. Agent interoperability a protocol evolution\n",
):
    if planned not in text:
        raise SystemExit(f"Planned README entry not found: {planned.strip()}")
    text = text.replace(planned, "", 1)

status_marker = "## Stav\n\n"
if status_marker not in text:
    raise SystemExit("Section 21 status marker not found")
status = (
    "Aktuálny authoritative stav sekcie je **12/62 · In progress**. Tretí authoritative blok aktivuje kapitoly 9–12 a incident `AGENT-OPS-03`. "
    "Durable-execution kapitola oddeľuje business operation lifetime od process/workflow attemptu, authoritative event history alebo checkpoint, deterministic replay, activities, commit boundaries, retries, timeouts, heartbeats, durable timers, signals, pause/resume, state a code versioning, cancellation, compensation, remote tasks a unknown-outcome reconciliation. "
    "Idempotency kapitola definuje stable operation-scoped key, canonical argument digest, atomic claim, leases a fencing, effectively-once invariant, side-effect inventory a single writera, outbox/inbox, retry ownership, conditional writes, compensation identity, retention, multi-region a tenant-isolated deduplication. "
    "MCP kapitola oddeľuje host/client/server, exact server identity a protocol revision, JSON-RPC correlation od business idempotency, capability a catalog generations, tools/resources/prompts, stdio a HTTP trust boundaries, OAuth-based authorization, consent, structured results, Tasks/extensions, caching a independent business read-back. "
    "Interoperability kapitola používa A2A 1.0 model Agent Card, interfaces, skills, security requirements, message/context/task IDs, submitted/working/interrupted/terminal states, artifacts, streaming, push notifications, semantic contracts, extensions, compatibility matrix, conformance, deprecation, rolling upgrade a rollback. "
    "Kapitoly 9–12 sú pripravené na repository closeout; reálne workflow engines, durable stores, MCP/A2A servers, remote tasks, retries, side effects, protocol upgrades, recovery drills ani business outcomes neboli vykonané. "
    "Sekcia zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. Ďalší blok sú kapitoly 13–16: agent identity, least privilege, sandboxing a prompt injection cez tools alebo retrieved content.\n"
)
text = text.split(status_marker, 1)[0] + status_marker + status
readme.write_text(text, encoding="utf-8")

roadmap = ROOT / "ROADMAP.md"
for title, target in (
    ("Durable execution, retries a resumability", "durable-execution-retries-resumability.md"),
    ("Idempotency a side-effect control", "idempotency-side-effect-control.md"),
    ("Model Context Protocol", "model-context-protocol.md"),
    ("Agent interoperability a protocol evolution", "agent-interoperability-protocol-evolution.md"),
):
    replace_exact(
        roadmap,
        f"- [ ] {title}",
        f"- [x] [{title}](docs/21-ai-agents-and-intelligent-automation/{target})",
    )

ledger = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
lines = ledger.read_text(encoding="utf-8").splitlines()
replacement = (
    "| `21-ai-agents-and-intelligent-automation` — AI Agents and Intelligent Automation | 12/62 authoritative drafting | In progress | 2026-08-04 | "
    "Tretí authoritative blok aktivuje kapitoly 9–12 a incident `AGENT-OPS-03`. Durable execution oddeľuje operation lifetime od process/run attemptu, persisted history/checkpoint, deterministic replay, activities, commit boundaries, retry/timeout/heartbeat/timer policy, pause/resume, state a code versioning, cancellation, compensation, remote tasks a unknown-outcome reconciliation. Idempotency kapitola zavádza operation-scoped key, canonical digest, atomic claim, leases/fencing, side-effect graph a single writera, outbox/inbox, retry ownership, conditional writes, compensation identity, retention a multi-region/tenant boundaries. MCP kapitola pokrýva exact server/protocol/catalog identity, JSON-RPC, capabilities, tools/resources/prompts, transports, OAuth authorization, consent, structured results, Tasks/extensions, caching a business proof boundary. Interoperability kapitola používa A2A 1.0 Agent Cards, interfaces, skills, security requirements, message/context/task IDs, task states, artifacts, streaming/push, semantic contracts, extensions, compatibility, conformance, deprecation a upgrade/rollback. Reálne workflow engines, durable stores, MCP/A2A servers, remote tasks, retries, side effects, protocol upgrades, recovery drills a business outcomes neboli vykonané; stav zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. |"
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

print("Synchronized Section 21 chapters 9-12 README, ROADMAP and review ledger.")
