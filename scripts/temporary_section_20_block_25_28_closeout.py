#!/usr/bin/env python3
"""Temporary closeout helper for Section 20 chapters 25-28."""

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
active_anchor = "24. [Prompt caching, semantic caching a response caching](prompt-semantic-response-caching.md)\n"
active_addition = active_anchor + (
    "25. [LLM gateways, routing, fallback a rate limiting](llm-gateways-routing-fallback-rate-limiting.md)\n"
    "26. [Prompt Registry a lifecycle](prompt-registry-lifecycle.md)\n"
    "27. [LLM evaluation datasets a graders](llm-evaluation-datasets-graders.md)\n"
    "28. [Human evaluation a expert feedback](human-evaluation-expert-feedback.md)\n"
)
if active_anchor not in text:
    raise SystemExit("Section 20 active-list anchor not found")
text = text.replace(active_anchor, active_addition, 1)
for planned in (
    "25. LLM gateways, routing, fallback a rate limiting\n",
    "26. Prompt Registry a lifecycle\n",
    "27. LLM evaluation datasets a graders\n",
    "28. Human evaluation a expert feedback\n",
):
    if planned not in text:
        raise SystemExit(f"Planned README entry not found: {planned.strip()}")
    text = text.replace(planned, "", 1)
status_marker = "## Stav\n\n"
if status_marker not in text:
    raise SystemExit("Section 20 status marker not found")
status = (
    "Aktuálny authoritative stav sekcie je **28/37 · In progress**. Siedmy authoritative blok aktivuje kapitoly 25–28 a incident `GENAI-SUPPORT-07`. "
    "Gateway kapitola modeluje caller a operation identity, control/data plane generations, capability-aware routing, behavior-compatible load balancing a fallback, failure classification, read-before-retry, quotas, backpressure, fairness, circuit breakers, region/data policy a attempt-versus-business telemetry. "
    "Prompt Registry kapitola oddeľuje immutable prompt version, mutable alias, rendered instance a composed application release; zavádza typed variables, role/examples/schema/tool dependencies, semantic diff, eval/approval gates, compare-and-swap promotion, runtime loaded-generation read-back, rollback, lineage a access control. "
    "LLM-evaluation kapitola definuje estimand, immutable dataset/case manifests, temporal validity, leakage-safe splits, deterministic a model graders, calibration, position/self-preference bias, multi-grader hard gates, repetitions, segment uncertainty, online correlation a grader-gaming recovery. "
    "Human-evaluation kapitola zavádza authority matrix, reprezentatívne a kvalifikované cohorts, versioned rubric/UI, blindness/randomization/overlap, inter-annotator agreement, disagreement analysis, expert adjudication, model-assisted review boundaries, ethics/privacy a authority-specific promotion evidence. "
    "Kapitoly 25–28 sú pripravené na repository closeout; reálny gateway traffic/failover/rate-limit exercise, prompt-registry promotion, provider eval execution, human annotation study, expert adjudication a business outcome neboli vykonané. "
    "Sekcia zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. Ďalší blok sú kapitoly 29–32: tracing/token usage/cost observability, hallucination/faithfulness/factuality, prompt injection a indirect prompt injection a data exfiltration/tool abuse/excessive agency.\n"
)
text = text.split(status_marker, 1)[0] + status_marker + status
readme.write_text(text, encoding="utf-8")

roadmap = ROOT / "ROADMAP.md"
for title, target in (
    ("LLM gateways, routing, fallback a rate limiting", "llm-gateways-routing-fallback-rate-limiting.md"),
    ("Prompt Registry a lifecycle", "prompt-registry-lifecycle.md"),
    ("LLM evaluation datasets a graders", "llm-evaluation-datasets-graders.md"),
    ("Human evaluation a expert feedback", "human-evaluation-expert-feedback.md"),
):
    replace_exact(
        roadmap,
        f"- [ ] {title}",
        f"- [x] [{title}](docs/20-llm-and-genai-engineering/{target})",
    )

ledger = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
lines = ledger.read_text(encoding="utf-8").splitlines()
replacement = (
    "| `20-llm-and-genai-engineering` — LLM and GenAI Engineering | 28/37 authoritative drafting | In progress | 2026-08-04 | "
    "Siedmy authoritative blok aktivuje kapitoly 25–28 a incident `GENAI-SUPPORT-07`. Gateway kapitola pinne caller/tenant/business-operation, route policy a resolved backend; vysvetľuje capability-aware routing, compatible fallback, retry/idempotency, token/request/concurrency/cost limits, admission/backpressure/fairness, circuit-breaker a cross-region governance. Prompt Registry kapitola definuje immutable version/digest, mutable alias, rendered instance, dependencies, promotion state machine, eval/approval evidence, full release manifest, runtime cache a loaded-generation proof, rollback, deprecation, access control a lineage. Eval kapitola zavádza workload estimand, versioned datasets/cases, sampling, temporal validity, leakage-safe splits, deterministic/text/model/human graders, calibration, bias tests, hard gates, repetitions, segment confidence, baseline a online correlation. Human-evaluation kapitola oddeľuje annotator preference a domain authority cez authority matrix, qualification, rubric/UI versions, blindness/randomization/overlap, agreement/disagreement, adjudication, worker ethics/privacy, expert feedback lineage a authority-specific promotion verdict. Reálny gateway/provider failover, prompt promotion, eval API execution, annotation study, adjudication a business outcomes neboli vykonané; stav zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. |"
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

print("Synchronized Section 20 chapters 25-28 README, ROADMAP and review ledger.")
