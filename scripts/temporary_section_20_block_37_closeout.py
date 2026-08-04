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


chapter = SECTION / "llm-application-troubleshooting.md"
old_playbook = """## 46. Troubleshooting playbook

Praktický playbook drží vyšetrovanie v konzistentnom poradí. Každý krok vytvára artifact alebo rozhodnutie, ktoré možno review-nuť a zopakovať.

1. Zapíš exact symptom, business impact a porušený invariant.
2. Identifikuj business operation, technical attempts, tenant, time window a release manifest.
3. Zastav ďalší high-impact harm a zachovaj evidence.
4. Zostav timeline a operation graph vrátane retries, fallbacks, tools a durable outcomes.
5. Porovnaj desired, resolved, loaded a effective state.
6. Vytvor competing hypotheses s potvrdzujúcim a vyraďujúcim dôkazom.
7. Nájdi first divergence pre každý material outcome.
8. Reprodukuj bezpečne s immutable fixture a dry-run tools.
9. Aplikuj complete rollback alebo reviewed forward fix.
10. Over loaded state, positive, forbidden, recovery a second-operation acceptance.
11. Reconcile-ni business, security, privacy a cost následky.
12. Zaznamenaj verdict, detection gaps, owners a follow-up controls.

Playbook nie je mechanický checklist, ktorý nahrádza expert judgment. Udržiava však evidence discipline a zabraňuje preskakovaniu business recovery alebo acceptance krokov.
"""
new_playbook = """## 46. Troubleshooting playbook

Praktický playbook drží vyšetrovanie v konzistentnom poradí, pretože neskorší krok závisí od artifacts vytvorených skôr. Bez exact subjectu sa timeline skladá z cudzích attempts; bez zachovanej evidence môže containment zničiť root-cause proof; bez first divergence sa recovery mení na náhodné editovanie promptu alebo retry policy. Každý krok preto vytvára reviewable výstup, určuje authoritative evidence a explicitne rozhoduje, či možno pokračovať do ďalšej fázy.

Poradie zároveň oddeľuje investigation od remediation. Tím môže kvôli impactu vykonať skorý containment, ale nesmie ho spätne prezentovať ako root-cause dôkaz. Rollback alebo forward fix sa považuje za technickú hypotézu, kým loaded-state read-back, incident replay a durable business outcome nepotvrdia recovery. Nasledujúce kroky sú operation-level workflow, nie iba názvy aktivít:

1. **Zarámuj symptom a invariant** — zapíš exact observed-versus-expected rozdiel, business impact, affected segment a pravidlo, ktoré malo nežiaducemu outcome-u zabrániť.
2. **Uzamkni troubleshooting subject** — identifikuj business operation, všetky technical attempts, tenant, časové okno a immutable release manifest, aby každý ďalší dôkaz patril rovnakému incidentu.
3. **Contain-ni ďalší harm a zachovaj evidence** — vypni alebo izoluj high-impact path, no pred cache flushom či redeployom ulož loaded generations, request IDs, operation IDs a authoritative state.
4. **Zostav causal timeline a operation graph** — spoj retries, fallbacks, retrieval, streaming, guardrails, tools a durable outcomes tak, aby sa nestratil attempt pred posledným úspešným requestom.
5. **Porovnaj desired, resolved, loaded a effective state** — preukáž, čo malo byť nasadené, čo sa resolve-lo, čo instances skutočne načítali a aký behavior vytvorili provider controls, caches a overrides.
6. **Formuluj falzifikovateľné competing hypotheses** — ku každej možnej príčine priraď potvrdzujúci aj vyraďujúci dôkaz a ponechaj ju otvorenú, kým authoritative evidence nerozhodne.
7. **Urči first divergence pre každý material outcome** — oddeľ prvú odchýlku answer pathu, side-effect pathu, privacy pathu alebo cost pathu namiesto hľadania jednej univerzálnej príčiny.
8. **Reprodukuj v bezpečnom a vernom prostredí** — použi immutable incident fixture, synthetic alebo controlled data a dry-run tools; zároveň dokumentuj, ktoré produkčné conditions replay nedokázal zachovať.
9. **Vyber complete rollback alebo reviewed forward fix** — zmeň compatible composed release, nie iba model alias, a uveď prečo zvolená recovery cesta znižuje riziko oproti ostatným možnostiam.
10. **Over runtime aj acceptance vrstvy** — potvrď loaded state a vykonaj positive, forbidden, recovery a second-operation tests nad exact recovered manifestom a dotknutými segmentmi.
11. **Reconcile-ni durable následky** — skontroluj a naprav business transakcie, security permissions, privacy copies, invoices a customer impact, ktoré technický rollback sám nevráti.
12. **Uzavri evidence-based verdict a prevention** — zaznamenaj symptom, first divergence, root causes, contributing factors, detection gaps, owners a follow-up controls s vlastnou acceptance a deadline-om.

Playbook nie je mechanický checklist, ktorý nahrádza expert judgment. Udržiava však evidence discipline, chráni causal chain pred predčasnou mutáciou a zabraňuje tomu, aby sa incident uzavrel po jednom úspešnom replayi bez business recovery a second-operation dôkazu.
"""
replace_exact(chapter, old_playbook, new_playbook)

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
