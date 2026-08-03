# Model selection a capability/cost trade-offs

Model selection je rozhodnutie, ktorý model a execution profile najlepšie spĺňajú konkrétny workload contract. Najnižšia cena za token ani najvyššie benchmark score samy osebe neurčujú najlepší model. Produkčný výber musí zohľadniť task quality, tool a schema support, latency, throughput, context behavior, modality, safety, data controls, region availability, rate limits a celkový cost na accepted outcome.

V incidente `GENAI-SUPPORT-03` tím nahradil hlavný support model lacnejším variantom, pretože jeho input/output token price bola nižšia. Nový model mal vyššiu invalid-tool-call rate, častejšie potreboval retry, horšie rozlišoval refund exceptions a nepodporoval rovnaký strict schema subset. Priemerná cena jedného requestu klesla, ale cena jedného správne vyriešeného prípadu stúpla a human escalation backlog sa zdvojnásobil. Root cause bolo optimalizovanie unit price namiesto end-to-end accepted outcome.

## 1. Selection subject

Model selection subject zahŕňa workload segment, model snapshot, API mode, reasoning effort, context profile, tool/schema features, deployment region, provider tier a evaluation generation.

```yaml
selection_candidate:
  workload: support-refund-resolution
  segment: low-risk-known-policy
  model_snapshot: provider/model-mini-2026-07-20
  api: responses-v2
  reasoning_effort: low
  context_profile: support-8k-effective
  structured_output: refund-decision-v4
  tool_catalog: support-tools-v13
  region: eu
  service_tier: standard
  eval_suite: support-selection-2026-08-03
```

Mutable alias bez snapshotu alebo observed model ID oslabuje reprodukovateľnosť. Availability endpoint s model name nepreukazuje feature parity ani behavior stability.

## 2. Workload decomposition

Jeden produkt môže potrebovať viac model classes. Intent routing, extraction, long-context analysis, code generation, multimodal understanding a high-risk decision support majú rozdielne requirements.

```text
request segment
→ capability requirements
→ candidate models
→ task-specific eval
→ operational and compliance filters
→ cost/latency frontier
→ controlled routing policy
```

„Používame model X“ je príliš hrubý architecture statement. Selection policy môže používať menší model pre bounded extraction a výkonnejší model pre ambiguous multi-document reasoning.

## 3. Capability matrix

Capability matrix zachytáva features potrebné pre workload:

| Oblasť | Otázka |
|---|---|
| Input | text, image, audio, files, context size a effective long-context quality |
| Output | free text, strict schema, tool calls, citations, modality |
| Reasoning | task accuracy, configurable effort, planning a multi-step reliability |
| Tools | function calling, parallel calls, built-in tools, MCP alebo ekvivalent |
| Operations | latency, throughput, rate limits, batch, streaming, availability |
| Governance | data retention, residency, zero-retention eligibility, audit |
| Lifecycle | pinned snapshots, deprecation policy, migration path |

Marketingový capability claim sa potvrdzuje concrete API/model combination a evalom. Feature dostupná v jednej endpoint family nemusí byť dostupná v realtime, batch alebo regional deployment variante.

## 4. Quality evaluation

Selection eval používa reprezentatívny dataset, jasné success criteria a segment results. Aggregate score môže zakryť kritické zlyhanie high-risk segmentu.

```yaml
metrics:
  - answer_correctness
  - evidence_faithfulness
  - schema_adherence
  - tool_selection_accuracy
  - unauthorized_action_rate
  - human_escalation_rate
  - p95_latency
  - cost_per_accepted_case
segments:
  - simple_status
  - policy_exception
  - multilingual
  - adversarial_instruction
  - long_context
```

Model judge môže byť súčasť eval, ale kalibruje sa proti expert labels. Rovnaký model family ako candidate a judge môže mať correlated bias.

## 5. Cost model

Total cost zahŕňa input/output tokens, reasoning tokens, cached versus uncached input, tool fees, retrieval, retries, failed requests, human review a infrastructure overhead.

```text
cost per accepted outcome =
(total model + tool + platform + review cost)
/
number of accepted outcomes
```

Lacnejší request môže byť drahší workflow, ak zvyšuje retries alebo escalations. Drahší model môže znížiť total cost, ak spoľahlivo vyrieši high-value cases na prvý attempt.

Cost telemetry sa viaže na exact model, prompt, route a outcome. Bez outcome joinu sa optimalizuje iba spotreba, nie hodnota.

## 6. Latency a throughput

Latency sa rozkladá na queue time, time to first token, generation time, tool latency a postprocessing. Model s nižším token throughputom môže byť prijateľný pri krátkom structured outpute, ale nevhodný pri streaming UX.

Reasoning effort, output length, context size a tool loops menia latency. Benchmark bez rovnakého request profile nie je porovnateľný.

Capacity zahŕňa rate limits a burst behavior. Routing všetkého na najlepší model môže vytvoriť throttling a zhoršiť tail latency.

## 7. Context window a effective context

Maximum context length je hard limit, nie dôkaz, že model rovnako spoľahlivo využije informácie na každej pozícii. Selection eval musí testovať reálnu serialization, retrieval density, ordering a truncation policy.

Dlhší context môže zvýšiť cost a latency a znížiť signal-to-noise. Model s kratším contextom a kvalitnejším retrievalom môže dosiahnuť lepší accepted outcome.

## 8. Structured output a tool compatibility

Model selection musí overiť podporovaný schema subset, refusal/incomplete behavior, function-call strictness, parallel tool semantics a tool choice modes. „Podporuje JSON“ nie je ekvivalent strict structured output.

Migration na model bez rovnakej tool/schema compatibility je interface change. Consumer contract, prompt a eval sa musia znovu validovať.

## 9. Data governance a region

Provider/model combination sa filtruje podľa data classification, retention, training usage, residency, encryption, subprocessors a regional processing. Remote tools alebo MCP servers môžu prenášať data mimo provider boundary.

Model, ktorý vyhrá quality eval, môže byť nepoužiteľný pre konkrétny tenant alebo jurisdiction. Governance filter sa aplikuje pred production routingom, nie ako neskorší disclaimer.

## 10. Routing a cascades

Static routing mapuje workload segment na model. Dynamic routing používa classifier alebo policy na výber podľa complexity, risk a budget. Cascade môže začať lacnejším modelom a eskalovať pri low confidence alebo validation failure.

Cascade potrebuje presné escalation criteria. Modelom generovaný confidence bez kalibrácie nestačí. Validátory, ambiguity signals, missing evidence a risk class sú silnejšie routing inputs.

Fallback pri outage mení model generation a často behavior. Fallback model musí mať preukázanú minimum capability a compatible schemas/tools. „Ak primary zlyhá, použi čokoľvek dostupné“ je forbidden.

## 11. Model registry a compatibility record

Application registry zachytáva:

```yaml
model_release: support-model-route-v12
routes:
  simple_status:
    model: provider/model-mini-2026-07-20
    prompt: support-simple-v8
    schema: status-answer-v3
  policy_exception:
    model: provider/model-pro-2026-07-15
    prompt: support-exception-v11
    schema: refund-decision-v4
compatibility:
  tool_catalog: support-tools-v13
  tokenizer_profile: provider-managed-2026-07
  eval_suite: support-selection-2026-08-03
```

Registry alias sa používa ako operational pointer, nie ako jediná identity. Request trace loguje resolved snapshot a route decision.

## 12. Controlled experiment

Candidate selection postup:

```text
offline replay
→ contract and safety gates
→ shadow traffic
→ bounded canary
→ segment outcome comparison
→ promotion or rollback
```

Shadow traffic nesmie vykonať write tools. Canary má stabilnú assignment jednotku, aby jeden user alebo case nepreskakoval medzi modelmi. Outcome delay sa zohľadní pred promotion.

## 13. Migration a deprecation

Provider môže meniť aliases, dostupnosť a model families. Pinned snapshot zvyšuje reproducibility, ale má lifecycle a deprecation deadline. Platforma sleduje announcements, compatibility a migration readiness.

Migration nie je iba zmena stringu `model`. Revaliduje tokenizer/context behavior, prompts, schemas, tools, safety, latency, cost a outcome metrics.

## 14. Observability

Každý request loguje selection policy version, candidate set, chosen route, resolved model snapshot, fallback reason, reasoning effort, usage, latency, validation result a business outcome link.

Metrics sa segmentujú podľa model a route. Aggregate product metric môže zakryť, že fallback model zlyháva iba v jednej language alebo policy exception class.

## 15. Failure hypotheses a troubleshooting

Pri quality regressione sa skúma route mix, model snapshot, prompt compatibility, context/truncation, schema/tool support a data drift. Pri cost spike retries, output length, reasoning effort, cache hit rate, tool loops a escalation rate. Pri latency spike queue, region, service tier, context size a tool dependency.

Pred rollbackom sa zachová exact selection event. Návrat na mutable alias bez resolved snapshotu nie je reprodukovateľný rollback.

## 16. Acceptance

Pozitívna acceptance vyžaduje workload-specific capability matrix, representative segmented eval, operational/governance filters, total cost per accepted outcome, pinned compatible model releases, controlled rollout a outcome observability.

Recovery acceptance vyžaduje identifikáciu regression segmentu, návrat na známu compatible route, replay a canary validation a second-operation test vrátane fallbacku.

Forbidden acceptance je výber iba podľa token price, leaderboard score bez workload eval, maximum context ako dôkaz long-context reliability alebo fallback model bez schema/tool a governance parity.
