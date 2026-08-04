#!/usr/bin/env python3
"""Temporary closeout helper for Section 21 chapters 21-24."""

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
active_anchor = "20. [Agent tracing, replay a debugging](agent-tracing-replay-debugging.md)\n"
active_addition = active_anchor + (
    "21. [Cost, latency a token budgets](cost-latency-token-budgets.md)\n"
    "22. [Agent reliability, fallback a kill switch](agent-reliability-fallback-kill-switch.md)\n"
    "23. [Multi-tenant isolation](multi-tenant-isolation.md)\n"
    "24. [Agent governance a audit](agent-governance-audit.md)\n"
)
if active_anchor not in text:
    raise SystemExit("Section 21 active-list anchor not found")
text = text.replace(active_anchor, active_addition, 1)

for planned in (
    "21. Cost, latency a token budgets\n",
    "22. Agent reliability, fallback a kill switch\n",
    "23. Multi-tenant isolation\n",
    "24. Agent governance a audit\n",
):
    if planned not in text:
        raise SystemExit(f"Planned README entry not found: {planned.strip()}")
    text = text.replace(planned, "", 1)

status_marker = "## Stav\n\n"
if status_marker not in text:
    raise SystemExit("Section 21 status marker not found")
status = (
    "Aktuálny authoritative stav sekcie je **24/62 · In progress**. Šiesty authoritative blok aktivuje kapitoly 21–24 a incident `AGENT-GOV-06`. "
    "Cost/latency kapitola zavádza exact budget subject, price-catalog generation, organization/tenant/workflow/operation/turn/tool hierarchy, hard/soft/forecast hranice, input/output/cached/reasoning token accounting, context amplification, deadlines, critical path, queue/rate-limit pressure, reservations, in-flight reconciliation, graceful degradation a cost-per-accepted-outcome acceptance. "
    "Reliability kapitola oddeľuje retry od semantického fallbacku, používa failure taxonomy, retry budgets, circuit breakers, bulkheads, model/provider/tool/retrieval compatibility manifests, state a approval revalidation, single-writer side effects, out-of-band scoped kill switch, loaded-generation proof, in-flight cancellation, re-enable canary a pravidelné drilly. "
    "Multi-tenant isolation kapitola viaže verified tenant identity na data, memory, vector retrieval, caches, context, tool catalogs, credentials, sandboxes, network, queues, provider usage, tracing, audit, evals, backup/restore a noisy-neighbor fairness; pool/silo/bridge modely sú hodnotené ako end-to-end controls a nie ako samotný dôkaz isolation. "
    "Governance kapitola definuje accountable owners, system inventory, intended use, internal risk classification, samostatnú legal applicability analýzu, NIST Govern/Map/Measure/Manage mapping, composed-release change control, segregation of duties, expiring exceptions, supplier/data governance, human oversight, audit-event schema/integrity/retention/access, incident/corrective action a retirement. "
    "Kapitoly 21–24 sú pripravené na repository closeout; reálne provider usage, budgets, fallbacky, kill-switch propagation, tenant isolation, governance decisions, audit storage, incident drilly ani business outcomes neboli vykonané. "
    "Sekcia zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. Ďalší blok sú kapitoly 25–28: n8n architecture/execution model, triggers/nodes/expressions/data mapping, webhooks/API integrations a credentials/secrets/access control.\n"
)
text = text.split(status_marker, 1)[0] + status_marker + status
readme.write_text(text, encoding="utf-8")

roadmap = ROOT / "ROADMAP.md"
for title, target in (
    ("Cost, latency a token budgets", "cost-latency-token-budgets.md"),
    ("Agent reliability, fallback a kill switch", "agent-reliability-fallback-kill-switch.md"),
    ("Multi-tenant isolation", "multi-tenant-isolation.md"),
    ("Agent governance a audit", "agent-governance-audit.md"),
):
    replace_exact(
        roadmap,
        f"- [ ] {title}",
        f"- [x] [{title}](docs/21-ai-agents-and-intelligent-automation/{target})",
    )

ledger = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
lines = ledger.read_text(encoding="utf-8").splitlines()
replacement = (
    "| `21-ai-agents-and-intelligent-automation` — AI Agents and Intelligent Automation | 24/62 authoritative drafting | In progress | 2026-08-04 | "
    "Šiesty authoritative blok aktivuje kapitoly 21–24 a incident `AGENT-GOV-06`. Cost/latency kapitola pokrýva hierarchical budgets, price a release generations, provider usage, context amplification, deadline/timeout/queue/rate-limit paths, reservations, in-flight accounting, degradation a billing reconciliation. Reliability kapitola oddeľuje retry, compatibility-gated fallback, deterministic/human degraded modes a out-of-band scoped kill switch s loaded-state, single-writer, unknown-outcome a re-enable evidence. Multi-tenant isolation viaže verified tenant context na data, memory, retrieval, caches, tools, sandboxes, queues, network, provider quotas, traces, audit a capacity fairness a používa cross-tenant negative/residue tests. Governance kapitola zavádza inventory, intended use, owners, internal risk a samostatnú legal applicability analýzu, composed-release approvals, segregation of duties, expiring exceptions, supplier/data/human-oversight controls a append-only audit lifecycle. Reálne provider usage, budgets, fallbacky, kill-switch drilly, tenant isolation, governance approvals, audit storage, incident recovery a business outcomes neboli vykonané; stav zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. |"
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

print("Synchronized Section 21 chapters 21-24 README, ROADMAP and review ledger.")
