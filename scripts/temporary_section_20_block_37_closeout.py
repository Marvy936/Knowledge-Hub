#!/usr/bin/env python3
"""Temporary closeout helper for Section 20 chapter 37."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs/20-llm-and-genai-engineering"


def replace_exact(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"Expected text not found in {path}: {old[:160]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


readme = SECTION / "README.md"
text = readme.read_text(encoding="utf-8")
active_anchor = "36. [LLMOps a production readiness](llmops-production-readiness.md)\n"
active_addition = active_anchor + "37. [LLM application troubleshooting](llm-application-troubleshooting.md)\n"
if active_anchor not in text:
    raise SystemExit("Section 20 active-list anchor not found")
text = text.replace(active_anchor, active_addition, 1)

planned_block = (
    "\n## Plánované authoritative poradie\n\n"
    "Nasledujúci inventory je schválený plán sekcie. Položka sa zmení na aktívny Markdown link až v pracovnom bloku, ktorý vytvorí a validuje príslušnú kapitolu. Tým sa plánovaný obsah nezamieňa za hotovú dokumentáciu.\n\n"
    "37. LLM application troubleshooting\n"
)
if planned_block not in text:
    raise SystemExit("Section 20 planned chapter 37 block not found")
text = text.replace(planned_block, "", 1)

status_marker = "## Stav\n\n"
if status_marker not in text:
    raise SystemExit("Section 20 status marker not found")
status = (
    "Aktuálny authoritative stav sekcie je **37/37 · Ready for user review**. Desiaty a záverečný authoritative blok uzatvára sekciu kapitolou 37 a incidentom `GENAI-SUPPORT-10`. "
    "Troubleshooting kapitola používa exact business-operation a technical-attempt identity, symptom a invariant framing, privacy-safe evidence preservation, jednotný evidence envelope, desired/resolved/loaded/effective-state comparison, causal operation graph, competing hypotheses a first-divergence analysis. "
    "Diagnostika pokrýva provider/API errors, request IDs, retryability a unknown outcomes, quotas a overload, latency a streaming, model/route/prompt/context resolution, RAG a citations, factuality, structured outputs, tools a durable side effects, guardrails, prompt injection, privacy, multimodal preprocessing, caches, cost a segment regressions aj measurement defects. "
    "Recovery model zahŕňa safe replay, counterfactual tests, composed-release bisect, change correlation, impact-driven containment, complete rollback, business/security/privacy reconciliation a positive, forbidden, recovery, second-operation a alternate-scenario acceptance. "
    "Všetkých 37 kapitol sekcie má authoritative prose-first obsah a synchronizovaný repository evidence model. Dokumentačné kontroly nepreukazujú complete production traces, provider behavior, reálne tool side effects, incident response, rollback drills ani business outcomes; sekcia je preto `Ready for user review`, nie runtime `Verified`, production `Stable` ani user `Accepted`.\n"
)
text = text.split(status_marker, 1)[0] + status_marker + status
readme.write_text(text, encoding="utf-8")

roadmap = ROOT / "ROADMAP.md"
replace_exact(
    roadmap,
    "- [ ] LLM application troubleshooting",
    "- [x] [LLM application troubleshooting](docs/20-llm-and-genai-engineering/llm-application-troubleshooting.md)",
)

ledger = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
lines = ledger.read_text(encoding="utf-8").splitlines()
replacement = (
    "| `20-llm-and-genai-engineering` — LLM and GenAI Engineering | 37/37 authoritative drafting | Ready for user review | 2026-08-04 | "
    "Desiaty a záverečný authoritative blok uzatvára sekciu kapitolou 37 a incidentom `GENAI-SUPPORT-10`. Troubleshooting kapitola spája exact operation/release identity, evidence preservation, desired/resolved/loaded/effective state, causal timeline, competing hypotheses a first divergence s provider/API a streaming failures, retries a unknown outcomes, model/prompt/route/context resolution, RAG/factuality/citations, structured outputs, tool authorization a durable side effects, guardrails, prompt injection, privacy, multimodal preprocessing, caches, cost, segmenty a observability defects. Recovery používa safe replay, counterfactual tests, composed-release bisect, impact-driven containment, complete rollback, business/security/privacy reconciliation a positive/forbidden/recovery/second-operation acceptance. Všetkých 37 kapitol má authoritative prose-first obsah a synchronizovaný repository evidence model. Reálne traces, provider behavior, side effects, incident drills, rollback a business outcomes neboli vykonané; sekcia je `Ready for user review`, nie runtime `Verified`, production `Stable` ani user `Accepted`. |"
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

print("Synchronized final Section 20 chapter 37 README, ROADMAP and review ledger.")
