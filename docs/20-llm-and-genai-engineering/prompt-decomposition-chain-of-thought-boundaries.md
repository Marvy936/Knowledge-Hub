# Prompt decomposition a chain-of-thought boundaries

Prompt decomposition rozdeľuje zložitú úlohu na menšie, overiteľné operácie. Chain of thought označuje textové alebo interné medzi-kroky, ktoré model používa alebo generuje pri riešení. Tieto pojmy sa prekrývajú iba čiastočne. Produkčná aplikácia potrebuje explicitný workflow, typed intermediate artifacts a validačné body; nepotrebuje automaticky ukladať alebo používateľovi zobrazovať voľný vnútorný monológ modelu.

V incidente `GENAI-SUPPORT-03` tím požiadal model, aby pred každou odpoveďou vypísal celý „reasoning“. Tento text sa ukladal do audit logu a operátori ho začali považovať za vysvetlenie rozhodnutia. Model však v jednej požiadavke uviedol presvedčivý, ale nepravdivý medzi-krok, v ďalšej zreprodukoval citlivú časť retrieved kontextu a pri tool flow opisoval akciu, ktorú systém nakoniec vôbec nevykonal. Audit tak obsahoval fluent narrative, nie authoritative evidence. Root cause bola zámena decomposition contractu, interného reasoning procesu a overiteľného decision recordu.

## 1. Decomposition subject

Decomposition subject nie je iba pôvodný user prompt. Tvoria ho business goal, input generation, decomposition policy, model snapshot, prompt release, dostupné tools, retrieval generation, time budget a acceptance criteria. Rovnaká otázka spracovaná inou decomposition policy je iný execution subject, aj keď finálna odpoveď vyzerá podobne.

```yaml
decomposition_run_id: support-2026-08-03-1842
goal: classify-and-resolve-billing-case
model_snapshot: provider/model-2026-07-15
prompt_release: support-decompose-v8
decomposition_policy: support-workflow-v5
retrieval_index_generation: billing-kb-2026-08-02
tool_catalog_generation: support-tools-v12
deadline_ms: 6000
acceptance_policy: billing-answer-v7
```

Execution record musí odlíšiť pôvodný request, plánované kroky, skutočne vykonané kroky, artifacts, tool calls, validations a finálny verdict. Voľný text „premýšľal som takto“ tieto väzby nenahrádza.

## 2. Task graph namiesto neurčitého „mysli krok za krokom“

Produkčný decomposition modeluje úlohu ako task graph. Každý uzol má definovaný input, output, authority, timeout, retry policy a acceptance. Uzly môžu byť sekvenčné, paralelné alebo podmienené.

```text
normalize request
→ classify intent
→ retrieve eligible evidence
→ extract claims
→ validate entitlement
→ compose answer
→ schema and policy validation
→ release response
```

Krok `retrieve eligible evidence` môže bežať paralelne pre knowledge base a account state, ak sú nezávislé. Krok `validate entitlement` však nesmie začať iba z textového summary predchádzajúceho kroku; potrebuje typed evidence s identitou zdroja, timestampom a access decision.

Decomposition znižuje cognitive load jedného promptu, ale pridáva orchestration failure modes. Viac krokov znamená viac latency, cost, partial failures, mutable intermediate state a možností, že skorá chyba kontaminuje ďalšie kroky.

## 3. Observable intermediate artifacts

Medzi-krok má byť observable vtedy, keď je potrebný pre kontrolu, recovery alebo audit. Observable artifact má úzky contract, nie voľný esejistický reasoning.

```json
{
  "intent": "refund_status",
  "confidence": 0.91,
  "required_evidence": [
    "order_record",
    "refund_event"
  ],
  "needs_human_review": false
}
```

Tento artifact sa dá validovať, porovnať s ground truthom a opätovne použiť. Neobsahuje predstieraný psychologický opis toho, „čo si model myslel“. Pre rozhodnutie sa loguje použitý evidence set, pravidlo, verdict a concise rationale viazané na konkrétne facts.

```json
{
  "decision": "refund_pending",
  "evidence_ids": ["order:9138", "refund:rf_771"],
  "policy_version": "refund-policy-v9",
  "reason_code": "PROCESSOR_PENDING",
  "explanation": "Refund event exists and processor settlement is not final."
}
```

`reason_code` a evidence IDs sú auditne silnejšie než dlhý generovaný chain of thought, pretože sa dajú read-backnúť z authoritative systems.

## 4. Chain of thought nie je authority

Textový chain of thought môže zlepšiť výkon pri niektorých tasks, no nie je automaticky faithful trace interného výpočtu ani dôkaz správnosti. Model môže dodatočne vytvoriť presvedčivé vysvetlenie nesprávneho answeru, vynechať rozhodujúci faktor alebo uviesť medzi-krok, ktorý nezodpovedá skutočnému execution path.

Z toho vyplývajú tri hranice. Po prvé, správnosť sa overuje výsledkom a evidence, nie štýlom reasoning textu. Po druhé, raw reasoning sa neukladá bez explicitnej privacy, security a retention analýzy. Po tretie, používateľská požiadavka „ukáž celý chain of thought“ sa nesmie zameniť za povinnosť odhaliť interný reasoning. Systém môže poskytnúť stručné vysvetlenie, zdroje, výpočty alebo decision factors bez publikovania súkromného scratchpadu.

## 5. Reasoning effort a model-specific behavior

Niektoré modely majú explicitný reasoning mode alebo parameter typu reasoning effort. Tento parameter mení compute budget, latency, token accounting a často aj tool behavior. Nie je univerzálny naprieč providers ani model families.

Reasoning effort je súčasť request generation:

```yaml
reasoning:
  mode: provider-managed
  effort: medium
  expose_raw_reasoning: false
  require_summary: true
```

Zníženie effort môže zrýchliť odpoveď a znížiť cost, ale môže meniť accuracy. Zvýšenie effort nie je záruka correctness. Selection sa overuje na task-specific evaloch a production telemetry. Ak provider vracia reasoning summary, loguje sa oddelene od authoritative decision evidence.

## 6. Decomposition patterns

**Plan then execute** vytvorí explicitný plán a až potom vykonáva kroky. Je vhodný, keď sa plán dá validovať pred side effects. Plán však môže zastarať po nových tool results, preto musí byť revidovateľný.

**Route then specialize** najprv klasifikuje task a vyberie špecializovaný prompt/model/tool set. Routing error je samostatný failure class a potrebuje confusion matrix.

**Map-reduce** spracuje časti inputu paralelne a následne ich agreguje. Reduce krok musí vedieť pracovať s missing alebo conflicting partial results.

**Generate then verify** vytvorí candidate a samostatne ho kontroluje validatorom, rule engineom alebo druhým modelom. Validator nesmie byť iba rovnaký prompt s formuláciou „si si istý?“.

**Retrieve then answer** oddeľuje retrieval od generation. Retrieved passages sú data, nie instructions, a finálny answer sa viaže na source IDs.

Pattern sa vyberá podľa task graphu, nie podľa trendu. Zbytočné rozdelenie jednoduchej úlohy zvyšuje cost a failure surface bez merateľného zisku.

## 7. Typed orchestration example

Nasledujúci príklad ukazuje orchestration boundary. Model functions vracajú typed outputs; side effects nie sú súčasťou decomposition bez explicitného dispatcheru.

```python
from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class Intent:
    name: Literal["refund_status", "invoice_copy", "unknown"]
    confidence: float

@dataclass(frozen=True)
class Evidence:
    source_id: str
    generation: str
    facts: dict[str, object]

@dataclass(frozen=True)
class Decision:
    code: str
    evidence_ids: tuple[str, ...]
    needs_human_review: bool

def resolve_support_case(request: str) -> Decision:
    intent = classify_intent(request)
    if intent.confidence < 0.75 or intent.name == "unknown":
        return Decision("HUMAN_REVIEW", (), True)

    evidence = retrieve_authorized_evidence(intent, request)
    validate_evidence_freshness(evidence)

    decision = apply_domain_policy(intent, evidence)
    validate_decision(decision, evidence)
    return decision
```

V produkcii sa logujú component versions, input/output digests, timings, retries a validation verdicts. Funkcia `apply_domain_policy` môže používať LLM, rules alebo kombináciu, ale final write alebo external action zostáva za authorization boundary.

## 8. Error propagation a confidence

Confidence jedného model step-u nie je calibrated probability, pokiaľ to nebolo osobitne preukázané. Násobenie alebo priemerovanie modelom generovaných confidence scores nevytvára spoľahlivý workflow confidence.

Pipeline musí zachytiť failure class každého kroku: invalid output, missing evidence, timeout, policy conflict, low coverage alebo tool failure. Downstream krok nesmie ticho interpretovať missing artifact ako prázdny úspešný výsledok.

```text
step failed
→ classify failure
→ preserve inputs and generation
→ retry same subject alebo escalate
→ never fabricate placeholder evidence
```

Ak retry mení model, prompt, data alebo decomposition policy, ide o nový attempt generation, nie o identické opakovanie.

## 9. Checkpointing, idempotency a recovery

Dlhý decomposition workflow ukladá immutable checkpoints po významných krokoch. Checkpoint obsahuje artifacts a state transition, nie iba poslednú textovú odpoveď. Recovery pokračuje z posledného validného checkpointu iba vtedy, keď sú dependencies stále kompatibilné.

External mutation sa chráni idempotency key a read-before-retry. Ak model navrhol tool call a orchestrator stratil response po odoslaní, nesmie jednoducho zopakovať celý reasoning flow a vytvoriť druhý side effect.

## 10. Evaluation

Decomposition sa hodnotí na viacerých úrovniach. Step-level eval meria routing, extraction a validation. Journey eval meria, či task graph vytvoril správny response alebo action. Efficiency eval sleduje latency, token usage, tool calls a redundant steps. Safety eval skúša injection, sensitive data propagation a unauthorized side effects.

Ablation test porovnáva decomposition proti jednoduchšiemu baseline. Ak zložitejší workflow neprináša merateľné zlepšenie accepted outcomes, nie je odôvodnený.

## 11. Failure hypotheses a troubleshooting

Ak finálny answer zlyhá, najprv sa určí prvá divergence: nesprávny route, chýbajúci evidence, chybný intermediate schema, validator gap, stale checkpoint alebo output composition. Dlhý reasoning transcript sa nepoužíva ako jediný diagnostický zdroj.

Ak sa objaví citlivý text v explanation, skúma sa context assembly, retrieved data classification, logging policy a renderer. Ak workflow opakuje side effects, skúma sa call identity, idempotency a unknown-outcome recovery. Ak decomposition zvyšuje latency bez quality gain, skúma sa počet model calls, serial dependencies a redundant verifier steps.

## 12. Acceptance

Pozitívna acceptance vyžaduje explicitný task graph, exact generations, typed intermediate artifacts, evidence-linked decision records, bounded reasoning exposure, step a journey evals a recovery z validného checkpointu.

Recovery acceptance vyžaduje zachovanie pôvodného failed subjectu, identifikáciu prvej divergence, opravenie konkrétneho kroku a second-operation test bez duplicate side effectu.

Forbidden acceptance je fluent chain of thought ako dôkaz correctness, raw reasoning uložený bez privacy boundary, „mysli krok za krokom“ ako náhrada orchestration designu alebo finálny answer bez väzby na evidence a vykonané kroky.
