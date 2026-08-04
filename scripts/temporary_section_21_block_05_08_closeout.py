#!/usr/bin/env python3
"""Temporary closeout helper for Section 21 chapters 5-8."""

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
active_anchor = "4. [Planning, decomposition a replanning](planning-decomposition-replanning.md)\n"
active_addition = active_anchor + (
    "5. [Short-term state, long-term memory a external memory](short-term-state-long-term-external-memory.md)\n"
    "6. [Single-agent a multi-agent architecture](single-agent-multi-agent-architecture.md)\n"
    "7. [Supervisor, router a specialist patterns](supervisor-router-specialist-patterns.md)\n"
    "8. [Human-in-the-loop a approval gates](human-in-the-loop-approval-gates.md)\n"
)
if active_anchor not in text:
    raise SystemExit("Section 21 active-list anchor not found")
text = text.replace(active_anchor, active_addition, 1)

for planned in (
    "5. Short-term state, long-term memory a external memory\n",
    "6. Single-agent a multi-agent architecture\n",
    "7. Supervisor, router a specialist patterns\n",
    "8. Human-in-the-loop a approval gates\n",
):
    if planned not in text:
        raise SystemExit(f"Planned README entry not found: {planned.strip()}")
    text = text.replace(planned, "", 1)

status_marker = "## Stav\n\n"
if status_marker not in text:
    raise SystemExit("Section 21 status marker not found")
status = (
    "Aktuálny authoritative stav sekcie je **8/62 · In progress**. Druhý authoritative blok aktivuje kapitoly 5–8 a incident `AGENT-OPS-02`. "
    "Memory kapitola oddeľuje thread-scoped typed state, reviewed cross-session semantic/episodic/procedural memory a external authoritative systems; zavádza exact namespace a identity, provenance, authority hierarchy, freshness, TTL a event-driven invalidation, compaction lineage, conflict resolution, poisoning controls, privacy/deletion graph a tenant-isolated second-operation acceptance. "
    "Architecture kapitola používa single-agent návrh ako default baseline a povoľuje multi-agent topológiu iba pri preukázanej potrebe context isolation, paralelizácie alebo privilege separation; definuje versioned topology manifest, state a memory ownership, delegation/output contracts, join/cancellation policy, single-writer side-effect ownera a topology-wide cost/latency budget. "
    "Pattern kapitola oddeľuje bounded router decision, stateful supervisor orchestration a specialist contract cez route taxonomy, abstain, single/multi-route fan-out, capability registry, context packaging, independent evidence, authority-aware synthesis, false-consensus detection, recursion a nested-approval propagation. "
    "Approval kapitola modeluje immutable action envelope s canonical subjectom, proposal/tool/policy generations, argument digestom, preview a evidence, reviewer identity a current authorization, separation of duties, TTL, edit/reject/escalate semantics, durable interruption, resume revalidation, duplicate-proposal control, idempotency, unknown-outcome reconciliation a business read-back. "
    "Kapitoly 5–8 sú pripravené na repository closeout; reálne memory stores, multi-agent runs, routing, approvals, identity systems, side effects, recovery drills ani business outcomes neboli vykonané. "
    "Sekcia zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. Ďalší blok sú kapitoly 9–12: durable execution, idempotency, Model Context Protocol a agent interoperability.\n"
)
text = text.split(status_marker, 1)[0] + status_marker + status
readme.write_text(text, encoding="utf-8")

roadmap = ROOT / "ROADMAP.md"
for title, target in (
    ("Short-term state, long-term memory a external memory", "short-term-state-long-term-external-memory.md"),
    ("Single-agent a multi-agent architecture", "single-agent-multi-agent-architecture.md"),
    ("Supervisor, router a specialist patterns", "supervisor-router-specialist-patterns.md"),
    ("Human-in-the-loop a approval gates", "human-in-the-loop-approval-gates.md"),
):
    replace_exact(
        roadmap,
        f"- [ ] {title}",
        f"- [x] [{title}](docs/21-ai-agents-and-intelligent-automation/{target})",
    )

ledger = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
lines = ledger.read_text(encoding="utf-8").splitlines()
replacement = (
    "| `21-ai-agents-and-intelligent-automation` — AI Agents and Intelligent Automation | 8/62 authoritative drafting | In progress | 2026-08-04 | "
    "Druhý authoritative blok aktivuje kapitoly 5–8 a incident `AGENT-OPS-02`. Memory kapitola oddeľuje thread-scoped typed state, reviewed cross-session semantic/episodic/procedural memory a external authoritative systems s exact namespace a identity, provenance, authority hierarchy, freshness, invalidation, compaction lineage, poisoning, privacy/deletion a tenant-isolation boundaries. Architecture kapitola používa single-agent ako default baseline a multi-agent povoľuje iba pri merateľnej potrebe context isolation, parallelism alebo privilege separation; definuje topology manifest, state/memory ownership, delegation/output contracts, join/cancellation policy, single-writer side-effect ownera a global cost/latency budget. Pattern kapitola oddeľuje bounded router, stateful supervisor a bounded specialist cez taxonomy, abstain, capability registry, context packaging, independent evidence, authority-aware synthesis, false-consensus detection, recursion a nested approvals. Approval kapitola zavádza immutable action envelope, canonical subject a digest, preview/evidence, current reviewer identity/authorization, separation of duties, TTL, durable pause/resume, drift revalidation, duplicate-proposal control, idempotency, unknown-outcome reconciliation a business read-back. Reálne memory stores, multi-agent runs, routing, approvals, identity systems, side effects, recovery drills a business outcomes neboli vykonané; stav zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. |"
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

print("Synchronized Section 21 chapters 5-8 README, ROADMAP and review ledger.")
