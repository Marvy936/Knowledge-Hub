# Model version pinning a compatibility

Model identifier v produkčnej LLM aplikácii nie je iba názov modelu. Je súčasťou runtime kontraktu, ktorý určuje behavior, podporované API features, tokenizer a context semantics, tool a schema capabilities, latency profile, safety behavior, region availability a lifecycle. Mutable alias zjednodušuje adopciu noviniek, ale oslabuje reprodukovateľnosť. Pinned snapshot zvyšuje kontrolu, no sám osebe negarantuje rovnaký outcome, pretože výsledok závisí aj od promptu, decoding configuration, retrievalu, tool catalogu a provider runtime.

V incidente `GENAI-SUPPORT-04` používala aplikácia alias `support-pro-latest`. Provider alias presmeroval na nový snapshot. Súčasne ingestion pipeline prebudovala časť knowledge indexu novým embedding modelom, ale zachovala rovnaký index alias. Support odpovede začali citovať nesprávne policy verzie. Tím najprv obvinil nový model, ale nemal uložený resolved model snapshot, embedding generation ani corpus manifest. Root cause nebolo možné určiť jedným rollbackom, pretože „predchádzajúci stav“ nebol jednoznačne identifikovaný.

## 1. Exact runtime subject

Exact model subject musí obsahovať viac než marketingový family name:

```yaml
model_runtime:
  provider: example-ai
  endpoint_family: responses-v2
  requested_model: support-pro-latest
  resolved_model: support-pro-2026-07-28
  provider_api_version: "2026-06-01"
  region: eu-central
  service_tier: standard
  reasoning_profile: medium
  tokenizer_profile: provider-managed-2026-07
  context_profile: 128k-advertised-96k-application
  structured_output_profile: json-schema-subset-v5
  tool_call_profile: strict-functions-v3
```

`requested_model` zachytáva to, čo aplikácia poslala. `resolved_model` zachytáva to, čo provider skutočne obslúžil, ak je táto informácia dostupná. Ak provider resolved snapshot nevracia, platforma musí explicitne evidovať, že request použil mutable alias a reprodukovateľnosť je obmedzená.

## 2. Alias, family, snapshot a deployment

Tieto identity nie sú zameniteľné:

```text
model family
≠ mutable alias
≠ dated snapshot
≠ fine-tuned model
≠ regional deployment
≠ provider endpoint
```

Family vyjadruje produktovú líniu. Alias môže smerovať na meniaci sa snapshot. Snapshot označuje konkrétnu vydanú generáciu. Fine-tuned model pridáva vlastný artifact a training lineage. Cloud deployment môže mať vlastný názov, kapacitu a regionálnu konfiguráciu. Rovnaký snapshot cez dve endpoint families nemusí podporovať rovnaký tool alebo structured-output contract.

## 3. Čo pinning rieši a čo nerieši

Pinned snapshot obmedzuje jednu významnú os variability: zmenu modelovej generácie. Uľahčuje reprodukciu evalov, rollback a compatibility testing. Nerobí však inference absolútne deterministickou a nezamŕza celý systém.

Aj pri rovnakom snapshot-e môže provider meniť runtime scheduling, batching alebo numerical execution. Tieto zmeny môžu ovplyvniť latency a pri stochastickom decodingu aj konkrétny output, hoci modelová identity zostáva rovnaká. Safety a abuse filters môžu navyše rozhodnúť, či request prejde, bude odmietnutý alebo dostane odlišný response envelope.

Application vrstva má vlastné nezávislé generácie. SDK alebo API serialization môžu zmeniť request shape; prompt, examples a decoding parameters menia behavior; retrieval corpus, chunking a index menia dostupné evidence; tool implementation a authoritative data menia side effect; postprocessing môže zmeniť alebo zahodiť správny model output. Rovnaký pinned model preto neznamená rovnaký end-to-end request subject.

Pinning sa používa ako jedna položka release manifestu, nie ako samostatný acceptance dôkaz. Jeho úlohou je zmenšiť search space pri reprodukcii a migrácii, zatiaľ čo zvyšné závislosti musia mať vlastnú identity, compatibility a read-back.

## 4. Application compatibility contract

Kompatibilita má najmenej štyri vrstvy:

| Vrstva | Príklady |
|---|---|
| Transport | endpoint, API version, SDK, streaming events |
| Interface | context limit, modalities, JSON Schema subset, tool syntax |
| Behavior | instruction following, refusal, extraction, reasoning, multilingual quality |
| Operations | latency, rate limits, region, capacity, retention a cost |

Transport compatibility neznamená behavior compatibility. Request môže dostať HTTP 200 a validný JSON, ale nový snapshot môže inak interpretovať examples alebo častejšie vyberať write tool. Naopak, behavior môže zostať prijateľný, ale zmena event streamu môže rozbiť parser.

## 5. Versioned release manifest

Model sa propaguje spolu so závislosťami, pretože production behavior vzniká až z ich resolved kombinácie. Manifest vytvára immutable alebo časovo presnú boundary, ktorú možno použiť pri evale, canary, incidente aj rollbacku. Bez nej sa zmena modelu mieša so zmenou promptu, retrievalu alebo tool contractu a výsledok sa nedá korektne priradiť jednej príčine.

Manifest zároveň definuje promotion unit. Release sa nepovažuje za nasadený iba preto, že provider prijal model string; platforma musí vedieť prečítať späť, ktoré components boli pre request skutočne resolved.

Príklad manifestu:

```yaml
llm_release: support-answer-v27
model:
  requested: support-pro-2026-07-28
  resolved_policy: exact-snapshot-required
api:
  endpoint: responses-v2
  provider_version: "2026-06-01"
prompt:
  release: support-grounded-v18
  digest: sha256:8b7d...
retrieval:
  corpus_generation: policy-corpus-2026-08-03.2
  index_generation: policy-index-emb3-2026-08-03.2
  embedding_model: embed-multilingual-3-2026-06-10
contracts:
  output_schema: support-answer-v7
  tools: support-tools-v14
evaluation:
  suite: support-prod-gate-2026-08-03
```

Release alias môže existovať, ale musí sa dať rozbaliť na immutable alebo časovo presne identifikovateľné components.

## 6. Model a tokenizer compatibility

Pri self-hosted modeloch sa tokenizer, chat template, special tokens, quantization a generation runtime pinujú samostatne. Pri hosted API je časť tejto vrstvy provider-managed, ale application stále sleduje token usage, truncation behavior a context serialization.

Chybná kombinácia model weights a tokenizeru môže meniť token IDs, special-token boundaries alebo context budget. Chybná chat template môže zmeniť role hierarchy. Preto lokálny manifest obsahuje model artifact digest, tokenizer digest, chat-template digest a inference-engine version.

```yaml
local_model:
  weights: sha256:aa91...
  tokenizer: sha256:12fe...
  chat_template: sha256:64c2...
  runtime: vllm-0.12.1
  quantization: awq-int4-v2
```

## 7. Feature compatibility matrix

Pred migráciou sa porovnávajú konkrétne features, nie iba model names:

```yaml
compatibility_checks:
  - context_serialization
  - max_effective_input
  - strict_schema_subset
  - refusal_representation
  - tool_choice_modes
  - parallel_tool_calls
  - streaming_event_types
  - usage_fields
  - logprobs_or_confidence_surface
  - image_and_file_inputs
  - regional_availability
```

Unsupported keyword v JSON Schema môže viesť k request erroru alebo k silently relaxed contractu podľa providera. Rozdielny refusal object môže rozbiť consumer. Nový snapshot môže generovať viac parallel tool calls, hoci starý typicky používal jeden.

## 8. Behavioral compatibility a evals

Behavioral compatibility sa meria na reprezentatívnych datasetoch. Nepredpokladá sa z benchmark leaderboardu ani z provider release note.

```text
pinned baseline release
→ replay dataset
→ candidate snapshot
→ segmented quality/safety/tool/schema metrics
→ paired difference analysis
→ compatibility verdict
```

Paired eval porovnáva rovnaké cases. Segmenty zahŕňajú policy exceptions, multilingual input, ambiguous requests, prompt-injection cases, long-context placement, refusal a tool-use scenarios. Aggregate average nesmie zakryť regresiu kritického segmentu.

## 9. Migration lifecycle

Bezpečná migrácia používa explicitný lifecycle:

```text
inventory a deadline
→ compatibility matrix
→ offline replay
→ contract tests
→ shadow traffic
→ bounded canary
→ outcome observation
→ promotion alebo rollback
```

Provider deprecation deadline je trigger pre plánovanie, nie dôvod preskočiť eval. Shadow traffic nesmie vykonávať write tools. Canary assignment musí byť stabilný podľa user, tenant alebo case, aby jeden business flow nepreskakoval medzi snapshotmi.

## 10. Rollback semantics

Rollback musí pomenovať celý release, nie iba starý model string. Ak sa počas migrácie zmenil prompt, schema alebo index generation, návrat iba na model snapshot nevytvorí predchádzajúci stav.

```text
rollback target =
model + API profile + prompt + retrieval generation + tools + schema + route policy
```

Rollback acceptance zahŕňa read-back resolved release, replay kritických cases a druhú operáciu po návrate. „Alias sme prepli späť“ bez read-back a outcome telemetry nie je dôkaz.

## 11. Deprecation a end-of-life

Každý pinned snapshot má lifecycle. Registry sleduje release date, deprecation announcement, migration target, shutdown date, owner a readiness status.

```yaml
lifecycle:
  model: support-pro-2026-07-28
  state: active
  deprecation_announced: null
  retirement_deadline: null
  replacement: null
  owner: genai-platform
  last_revalidated: 2026-08-04
```

Alert sa viaže na zostávajúci čas a migration lead time. Produkčná závislosť nesmie prvýkrát zistiť retirement pri runtime chybe.

## 12. Provider API versioning

Model version a API version sú samostatné. Provider môže používať stabilnú API major verziu, dátumový header alebo regionálny deployment contract. SDK môže zároveň meniť typy a defaulty.

Platforma preto pinne alebo kontrolovane aktualizuje:

```text
provider API version
+ SDK package version
+ request/response schema
+ model snapshot
```

SDK upgrade bez model change môže zmeniť serialization, retry policy alebo streaming parser. Model migration bez SDK change môže zaviesť nové event types. Obe osi sa testujú.

## 13. Mutable alias policy

Mutable alias nie je vždy zakázaný. Môže byť vhodný pre experimentálne interné workloady alebo tam, kde provider-managed latest behavior je zámer. Musí však byť explicitne označený:

```yaml
alias_policy:
  mode: mutable
  allowed_workloads:
    - low-risk-drafting
  forbidden_workloads:
    - financial-decision
    - write-tool-execution
  required_controls:
    - resolved-model-telemetry
    - daily-sentinel-eval
    - immediate-disable-switch
```

Pre high-risk alebo strict-contract workloads je exact snapshot alebo controlled deployment typicky vhodnejší.

## 14. Observability

Request trace loguje requested model, resolved model alebo unknown-resolution flag, provider API version, release manifest, fallback route, response identifiers, usage, latency, refusal/finish reason, schema validation a outcome link.

Metrics sa segmentujú podľa snapshotu a route. Ak sa alias presunie, dashboard musí ukázať transition boundary. Bez tejto hranice sa behavior change mieša s bežnou variabilitou.

## 15. Failure hypotheses a troubleshooting

Pri regresii sa oddelene skúma:

```text
model snapshot drift
API/SDK compatibility drift
prompt release drift
retrieval/index drift
tool/schema drift
traffic-segment drift
provider runtime incident
```

Najprv sa rekonštruuje exact request subject. Potom sa rovnaký eval case prehrá na baseline a candidate release. Ak nie je možné určiť resolved model alebo corpus generation, incident sa označí ako observability gap; nevytvára sa falošne presný root cause.

## 16. Acceptance

Pozitívna acceptance vyžaduje explicitnú model identity policy, versioned release manifest, interface a behavioral compatibility tests, lifecycle monitoring, controlled rollout, resolved runtime telemetry a outcome metrics.

Recovery acceptance vyžaduje reprodukovateľný baseline, rollback celého dependent release graphu, replay kritických segmentov a potvrdenie druhej operácie po návrate.

Forbidden acceptance je tvrdenie, že rovnaký family name znamená rovnaké správanie, že pinned snapshot garantuje deterministický outcome, že HTTP compatibility znamená application compatibility alebo že model alias možno meniť bez evalov a trace boundary.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Model selection a capability/cost trade-offs](model-selection-capability-cost-tradeoffs.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Retrieval-Augmented Generation architecture →](retrieval-augmented-generation-architecture.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
