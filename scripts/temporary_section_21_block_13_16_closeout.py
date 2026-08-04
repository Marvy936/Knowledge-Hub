#!/usr/bin/env python3
"""Temporary closeout helper for Section 21 chapters 13-16."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs/21-ai-agents-and-intelligent-automation"


def replace_exact(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"Expected text not found in {path}: {old[:180]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


readme = SECTION / "README.md"
text = readme.read_text(encoding="utf-8")
active_anchor = "12. [Agent interoperability a protocol evolution](agent-interoperability-protocol-evolution.md)\n"
active_addition = active_anchor + (
    "13. [Agent identity, authentication a authorization](agent-identity-authentication-authorization.md)\n"
    "14. [Least privilege pre tools a credentials](least-privilege-tools-credentials.md)\n"
    "15. [Sandboxing a code execution](sandboxing-code-execution.md)\n"
    "16. [Prompt injection cez tools a retrieved content](prompt-injection-tools-retrieved-content.md)\n"
)
if active_anchor not in text:
    raise SystemExit("Section 21 active-list anchor not found")
text = text.replace(active_anchor, active_addition, 1)

for planned in (
    "13. Agent identity, authentication a authorization\n",
    "14. Least privilege pre tools a credentials\n",
    "15. Sandboxing a code execution\n",
    "16. Prompt injection cez tools a retrieved content\n",
):
    if planned not in text:
        raise SystemExit(f"Planned README entry not found: {planned.strip()}")
    text = text.replace(planned, "", 1)

status_marker = "## Stav\n\n"
if status_marker not in text:
    raise SystemExit("Section 21 status marker not found")
status = (
    "Aktuálny authoritative stav sekcie je **16/62 · In progress**. Štvrtý authoritative blok aktivuje kapitoly 13–16 a incident `AGENT-SEC-04`. "
    "Identity kapitola oddeľuje human alebo business subject, agent definition, attested workload, runtime instance, run/task/tool-call identity a downstream actor chain; pokrýva SPIFFE/SVID, authentication verzus authorization, delegation verzus impersonation, OAuth token exchange, audience/resource/scope reduction, sender-constrained credentials, step-up, revocation a multi-tenant audit. "
    "Least-privilege kapitola rozdeľuje read/propose/execute capabilities, používa reviewed capability manifest, dynamic tool exposure, exact resource a argument bounds, environment isolation, credential broker, dynamic/JIT secrets, short TTL a one-shot handles, sender constraint, no-inheritance, egress/filesystem/data privilege a descendant cleanup. "
    "Sandboxing kapitola definuje threat-driven isolation tiers od hardened procesu a containera cez gVisor po microVM/dedicated host; zavádza immutable execution manifest, loaded runtime evidence, user namespaces, seccomp/MAC/capabilities, mount/device/network default deny, secret separation, resource quotas, output contracts, teardown a residual-state acceptance. "
    "Prompt-injection kapitola modeluje indirect injection ako information-integrity a flow-control problém cez content envelopes, provenance a transformation lineage, integrity/confidentiality labels, tool/MCP/agent outputs, RAG a memory poisoning, context separation, probabilistic detection, deterministic taint/endorsement, plan drift, tool-chain policy, least privilege, approval a adversarial evals. "
    "Kapitoly 13–16 sú pripravené na repository closeout; reálne identity providers, credential brokers, sandboxes, injected attacks, side effects, data exposure, recovery drilly ani business outcomes neboli vykonané. "
    "Sekcia zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. Ďalší blok sú kapitoly 17–20: tool poisoning/confused deputy/data exfiltration, agent evaluation, trajectory/tool-selection/outcome evaluation a agent tracing/replay/debugging.\n"
)
text = text.split(status_marker, 1)[0] + status_marker + status
readme.write_text(text, encoding="utf-8")

roadmap = ROOT / "ROADMAP.md"
for title, target in (
    ("Agent identity, authentication a authorization", "agent-identity-authentication-authorization.md"),
    ("Least privilege pre tools a credentials", "least-privilege-tools-credentials.md"),
    ("Sandboxing a code execution", "sandboxing-code-execution.md"),
    ("Prompt injection cez tools a retrieved content", "prompt-injection-tools-retrieved-content.md"),
):
    replace_exact(
        roadmap,
        f"- [ ] {title}",
        f"- [x] [{title}](docs/21-ai-agents-and-intelligent-automation/{target})",
    )

ledger = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
lines = ledger.read_text(encoding="utf-8").splitlines()
replacement = (
    "| `21-ai-agents-and-intelligent-automation` — AI Agents and Intelligent Automation | 16/62 authoritative drafting | In progress | 2026-08-04 | "
    "Štvrtý authoritative blok aktivuje kapitoly 13–16 a incident `AGENT-SEC-04`. Identity kapitola oddeľuje human/business subject, agent definition, attested workload, runtime/run/tool identity a downstream actor chain; pokrýva SPIFFE/SVID, authentication/authorization, delegation/impersonation, OAuth token exchange, audience/resource/scope, sender constraint, step-up, revocation a tenant audit. Least privilege rozdeľuje read/propose/execute, definuje capability manifest, dynamic catalog, exact resource/argument bounds, JIT brokered credentials, one-shot handles, no inheritance, egress/filesystem/data privilege a descendant cleanup. Sandboxing kapitola zavádza threat-driven isolation tiers, immutable execution manifest, loaded runtime evidence, namespaces/seccomp/MAC/capabilities, mount/device/network default deny, secret separation, quotas, output validation, teardown a residual-state proof. Prompt injection kapitola používa content envelopes, provenance/lineage, integrity/confidentiality labels, RAG/tool/MCP/agent output boundaries, memory poisoning, context separation, probabilistic detection, deterministic information-flow policy, taint/endorsement, plan drift, tool-chain analysis, least privilege, approval a adversarial evals. Reálne identity providers, brokers, sandboxes, attacks, side effects, data exposure, recovery drilly a business outcomes neboli vykonané; stav zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. |"
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

print("Synchronized Section 21 chapters 13-16 README, ROADMAP and review ledger.")
