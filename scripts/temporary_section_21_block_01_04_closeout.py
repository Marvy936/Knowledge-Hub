#!/usr/bin/env python3
"""Temporary closeout helper for Section 21 chapters 1-4."""

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
planned_heading = "## Plánované authoritative poradie\n"
if planned_heading not in text:
    raise SystemExit("Section 21 planned heading not found")
active_block = (
    "## Authoritative poradie — aktívne kapitoly\n\n"
    "1. [Deterministic workflow, probabilistic component a autonomous agent](deterministic-workflow-probabilistic-component-autonomous-agent.md)\n"
    "2. [Agent loop, state, observation, action a termination](agent-loop-state-observation-action-termination.md)\n"
    "3. [Tool calling a tool contracts](tool-calling-tool-contracts.md)\n"
    "4. [Planning, decomposition a replanning](planning-decomposition-replanning.md)\n\n"
)
text = text.replace(planned_heading, active_block + planned_heading, 1)
for planned in (
    "1. Deterministic workflow, probabilistic component a autonomous agent\n",
    "2. Agent loop, state, observation, action a termination\n",
    "3. Tool calling a tool contracts\n",
    "4. Planning, decomposition a replanning\n",
):
    if planned not in text:
        raise SystemExit(f"Planned README entry not found: {planned.strip()}")
    text = text.replace(planned, "", 1)

status_marker = "## Stav\n\n"
if status_marker not in text:
    raise SystemExit("Section 21 status marker not found")
status = (
    "Aktuálny authoritative stav sekcie je **4/62 · In progress**. Prvý authoritative blok aktivuje kapitoly 1–4 a incident `AGENT-OPS-01`. "
    "Architecture kapitola oddeľuje deterministic workflow, bounded probabilistic component a autonomous agent cez control-flow authority, autonomy dimensions, business invariants, complexity budget a architecture ladder. "
    "Agent-loop kapitola definuje exact run a operation identity, typed state, observation provenance a freshness, action outcomes, interruptions, budgets, cycle detection a deterministic termination. "
    "Tool-contract kapitola oddeľuje model proposal od schema a semantic validation, canonical resource resolution, authorization, approval, idempotency, timeout a retry semantics, postconditions, trust a versioned catalog. "
    "Planning kapitola zavádza explicitný versioned operational plan bez private chain-of-thought, evidence-first decomposition, dependencies, feasibility, risk ordering, observation-driven replanning, unknown-outcome reconciliation a trajectory acceptance. "
    "Kapitoly 1–4 sú pripravené na repository closeout; reálne agent runs, production tools, approvals, side effects, failure injection, recovery drills ani business outcomes neboli vykonané. "
    "Sekcia zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. Ďalší blok sú kapitoly 5–8: memory, single/multi-agent architecture, supervisor/router/specialist patterns a human approval gates.\n"
)
text = text.split(status_marker, 1)[0] + status_marker + status
readme.write_text(text, encoding="utf-8")

roadmap = ROOT / "ROADMAP.md"
for title, target in (
    ("Deterministic workflow, probabilistic component a autonomous agent", "deterministic-workflow-probabilistic-component-autonomous-agent.md"),
    ("Agent loop, state, observation, action a termination", "agent-loop-state-observation-action-termination.md"),
    ("Tool calling a tool contracts", "tool-calling-tool-contracts.md"),
    ("Planning, decomposition a replanning", "planning-decomposition-replanning.md"),
):
    replace_exact(
        roadmap,
        f"- [ ] {title}",
        f"- [x] [{title}](docs/21-ai-agents-and-intelligent-automation/{target})",
    )

ledger = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
lines = ledger.read_text(encoding="utf-8").splitlines()
replacement = (
    "| `21-ai-agents-and-intelligent-automation` — AI Agents and Intelligent Automation | 4/62 authoritative drafting | In progress | 2026-08-04 | "
    "Prvý authoritative blok aktivuje kapitoly 1–4 a incident `AGENT-OPS-01`. Architecture kapitola oddeľuje deterministic workflows, bounded probabilistic components a autonomous agents cez control-flow authority, autonomy dimensions, invariants, complexity budget a architecture ladder. Agent-loop kapitola modeluje exact run identity, typed state, trusted observations, action outcomes, interruptions, budgets, cycles a deterministic termination. Tool-contract kapitola pokrýva proposal/execution boundary, schema a semantic validation, canonicalization, authorization, approval, idempotency, timeout/retry semantics, postconditions, trust, versioning a observability. Planning kapitola definuje explicitné operational plans bez private chain-of-thought, evidence-first decomposition, dependencies, feasibility, risk, replanning triggers, unknown-outcome reconciliation a trajectory acceptance. Reálne runs, tools, approvals, side effects, recovery drills a business outcomes neboli vykonané; stav zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. |"
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

print("Synchronized Section 21 chapters 1-4 README, ROADMAP and review ledger.")
