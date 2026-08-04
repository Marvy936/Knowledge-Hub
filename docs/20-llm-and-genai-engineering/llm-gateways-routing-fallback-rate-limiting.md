# LLM gateways, routing, fallback a rate limiting

LLM gateway je runtime boundary medzi aplikáciou a jedným alebo viacerými modelovými backendmi. Nejde iba o reverse proxy s premenovaným endpointom. Produkčný gateway musí zachovať identitu volajúceho, resolved model route, prompt a tool contract, tokenový rozpočet, retry semantics, security policy, telemetry a business-operation identity tak, aby routing alebo fallback nezmenili význam requestu bez dôkazu a kontroly.

V incidente `GENAI-SUPPORT-07` support aplikácia volala gateway alias `support-default`. Primárny backend vrátil `429`, gateway automaticky prepol request na lacnejší model a zopakoval celý request. Fallback model nepodporoval rovnaký strict schema subset ani rovnakú tool-call behavior, takže namiesto `propose_refund` vrátil free-text odporúčanie. Aplikačná vrstva ho nesprávne interpretovala ako schválenú operáciu a po druhom retry vytvorila duplicitný refund. Dashboard pritom ukazoval úspešný HTTP status a zníženú priemernú latency. Root cause bol gateway contract, ktorý zamieňal dostupnosť backendu za behaviorálnu kompatibilitu a retryable transport failure za bezpečne opakovateľnú business operáciu.

## 1. Exact gateway subject

Gateway request sa identifikuje ako zložený runtime subject, nie iba URL a model string. Potrebná je identita klienta, policy generation, route generation, requested a resolved backend, prompt/model/tool/schema release a durable operation key.

```yaml
gateway_request:
  request_id: gwreq-01J8Z7KQ
  trace_id: 4c2d6f8a...
  caller:
    workload_identity: support-api-prod
    tenant_id: tenant-481
    user_id: user-772
  operation:
    type: refund-proposal
    idempotency_key: refund:case-9481:v1
    side_effect_class: reversible-write
  requested_route: support-default
  routing_policy: support-route-v18
  resolved_backend:
    provider: provider-a
    deployment: eu-support-pro
    model_snapshot: support-pro-2026-07-28
  prompt_release: support-refund-v14
  schema_release: refund-decision-v5
  tool_catalog: support-tools-v15
  budget:
    input_tokens: 12000
    output_tokens: 900
    deadline_ms: 8500
```

Bez tejto identity sa nedá odlíšiť, či regresiu spôsobil model, prompt, gateway policy, fallback, region, provider endpoint alebo downstream tool. Gateway log, ktorý uchová iba `model=default` a `status=200`, je prevádzkový údaj, nie reprodukovateľný execution record.

## 2. Control plane a data plane

Gateway control plane spravuje model catalog, backend credentials, routing policies, quotas, aliases, health rules a deployment konfiguráciu. Data plane prijíma runtime requesty, autentifikuje klienta, aplikuje policy, vyberá backend, transformuje request/response a emituje telemetry.

Tieto dva planes majú oddelené generácie. Uložená policy v control plane nepreukazuje, že konkrétny gateway pod načítal rovnakú verziu. Runtime trace preto zaznamenáva loaded policy digest alebo generation, nie iba názov konfigurácie.

```text
policy source
→ validated policy artifact
→ gateway deployment
→ loaded route generation
→ exercised request
→ resolved backend
→ validated response
→ business outcome
```

## 3. Gateway responsibilities

Gateway typicky centralizuje authentication, credential isolation, routing, quotas, token limits, request normalization, observability a provider abstraction. Každá z týchto funkcií však musí mať jasnú authority boundary. Gateway môže rozhodnúť, ktorý schválený backend obslúži request, ale nemá automaticky právo meniť business operation, znižovať security scope alebo obísť application validation.

Provider abstraction nesmie predstierať úplnú zameniteľnosť. Rozdiely v role hierarchy, streaming events, structured outputs, tool calls, refusals, usage accounting, tokenization a error codes sa explicitne mapujú do interného contractu. Neznámy alebo nepodporovaný provider field sa nesmie ticho zahodiť, ak mení semantics.

## 4. Internal request contract

Aplikácia by mala komunikovať s gateway cez stabilný interný contract, ktorý je bohatší než najmenší spoločný menovateľ providerov. Contract zachytáva požadované capabilities a zakazuje route, ktorá ich nespĺňa.

```json
{
  "route": "support-refund",
  "requirements": {
    "strict_json_schema": "refund-decision-v5",
    "required_tools": ["propose_refund"],
    "parallel_tools": false,
    "region": "eu",
    "data_class": "customer-confidential",
    "max_p95_ms": 8000
  },
  "operation": {
    "idempotency_key": "refund:case-9481:v1",
    "allow_write_tools": false
  }
}
```

Gateway najprv filtruje kandidátov podľa hard requirements a až potom optimalizuje cenu, latency alebo load. Backend, ktorý nepodporuje schema alebo region requirement, nie je fallback candidate bez ohľadu na jeho dostupnosť.

## 5. Static routing

Static routing mapuje workload segment na presný backend alebo deployment. Je jednoduchšie auditovateľný a vhodný pre regulované alebo úzko definované workloads, kde je dôležitejšia predvídateľnosť než dynamická optimalizácia.

```yaml
routes:
  support-status:
    backend: provider-a/eu-mini-2026-07-20
  support-refund:
    backend: provider-a/eu-pro-2026-07-28
  support-legal-escalation:
    backend: provider-b/eu-legal-2026-07-15
```

Static routing stále potrebuje lifecycle. Backend môže byť deprecated, rate-limited alebo behaviorálne nekompatibilný s novým prompt release. Route manifest sa preto versionuje a testuje spolu s model/prompt/schema/tool generation.

## 6. Dynamic routing

Dynamic routing vyberá backend podľa complexity, risk, modality, language, context length, budget alebo observed health. Router môže byť rules engine, classifier alebo samostatný model, ale jeho decision je súčasťou production release a musí byť reprodukovateľný.

Router output nie je iba model name. Mal by obsahovať reason code, candidate set, hard-filter results, selected route a policy version.

```json
{
  "routing_policy": "support-route-v18",
  "segment": "policy-exception",
  "risk": "medium",
  "candidates": [
    {"backend": "eu-pro-a", "eligible": true},
    {"backend": "eu-mini-a", "eligible": false, "reason": "schema-v5-unsupported"},
    {"backend": "us-pro-b", "eligible": false, "reason": "region-policy"}
  ],
  "selected": "eu-pro-a"
}
```

Model-based router sa hodnotí ako classifier: potrebuje labels, confusion matrix, calibrated escalation a negative tests. Jeho vlastná neistota nesmie byť jediným dôvodom na výber lacnejšieho alebo menej bezpečného backendu.

## 7. Capability-aware routing

Capability matrix je authority pre to, ktoré backendy môžu obslúžiť konkrétny contract. Eviduje schema subset, tool semantics, context/output limits, modalities, streaming, reasoning controls, data controls, region a lifecycle stav.

```yaml
backend_capability:
  id: eu-pro-a-2026-07-28
  structured_output:
    strict: true
    schema_profile: json-schema-subset-v5
  tools:
    strict_arguments: true
    parallel_calls: true
  data:
    region: eu
    retention_profile: zero-retention-eligible
  lifecycle:
    state: approved
    retirement_after: 2027-01-31
```

Capability claim sa overuje provider documentation a contract tests. Úspešný jednoduchý request nepreukazuje, že backend správne zvláda refusal, incomplete output, tool choice alebo max-context edge cases.

## 8. Load balancing

Load balancing rozdeľuje requesty medzi behaviorálne kompatibilné deployments. Algoritmus môže používať round-robin, weighted routing, least-connections, latency-aware alebo capacity-aware selection. Predpokladom je, že members jednej pool generácie spĺňajú rovnaký application contract.

Health check nesmie byť iba TCP alebo model-list endpoint. Potrebný je lightweight capability probe, ktorý overí authentication, minimal inference, schema/tool behavior a expected region/deployment identity bez vykonania business side effectu.

```text
network health
≠ API authentication health
≠ inference health
≠ schema/tool compatibility
≠ business correctness
```

## 9. Fallback contract

Fallback je explicitná policy pre degradovaný stav. Každá fallback route má definované triggers, minimum capabilities, allowed workloads, changed guarantees, user-visible behavior a rollback condition.

```yaml
fallback_policy:
  primary: eu-pro-a
  alternatives:
    - backend: eu-pro-b
      allowed_for: [read-only, draft-generation]
      required_capabilities: [schema-v5, strict-tools]
    - backend: eu-mini-a
      allowed_for: [status-summary]
      forbidden_for: [refund, legal, write-tool]
  on_no_compatible_backend:
    action: fail_closed
    response: temporary_unavailable
```

Fallback, ktorý vypne citations, structured output alebo safety policy bez explicitného product decisionu, je contract downgrade. Pri high-risk workflow je správnym fallbackom často kontrolované odmietnutie alebo human escalation, nie ľubovoľný dostupný model.

## 10. Failure classification

Gateway rozlišuje transport failure, provider rejection, rate limit, timeout, invalid response, safety refusal, application validation failure a unknown business outcome. Tieto stavy nemajú rovnaké retry semantics.

Provider `429` môže znamenať per-key limit, token quota, concurrency saturation alebo region capacity. `500` môže vzniknúť pred prijatím requestu alebo po začatí inference. Timeout po tool dispatch môže mať unknown side effect. Bez classification sa retry mení na hazard.

```python
from enum import Enum

class FailureClass(str, Enum):
    CONNECT = "connect"
    RATE_LIMIT = "rate_limit"
    PROVIDER_5XX = "provider_5xx"
    INVALID_OUTPUT = "invalid_output"
    REFUSAL = "refusal"
    UNKNOWN_OUTCOME = "unknown_outcome"

RETRYABLE = {FailureClass.CONNECT, FailureClass.RATE_LIMIT, FailureClass.PROVIDER_5XX}
```

Aj pri technicky retryable class musí application overiť idempotency a remaining deadline. Retry permission je prienik transport classification, business operation contractu a time budgetu.

## 11. Retry semantics

Read-only inference bez external side effectu sa dá často bezpečne zopakovať, ak request používa pinned dependencies a retry neprekročí deadline. Request, ktorý môže viesť k tool write, potrebuje durable operation identity a read-before-retry.

```text
failure observed
→ classify stage
→ determine whether side effect could have occurred
→ authoritative read-back by operation key
→ retry only missing work
```

Gateway nemá slepo replayovať celý agent loop. Ak model už navrhol tool call a executor ho vykonal, nový model response môže navrhnúť druhú operáciu. Tool execution ledger musí byť mimo ephemeral gateway requestu.

## 12. Idempotency a deduplication

Idempotency key reprezentuje business operation, nie HTTP attempt. Rovnaký operation key môže prežiť provider retry, gateway failover aj application restart, zatiaľ čo každý attempt má vlastný request ID.

```sql
INSERT INTO llm_operations(operation_key, state, request_digest)
VALUES (:key, 'started', :digest)
ON CONFLICT (operation_key) DO NOTHING;
```

Gateway môže deduplikovať concurrent identical attempts, ale authoritative outcome patrí application operation ledgeru. Cache hit alebo provider response ID nie sú náhradou durable business read-backu.

## 13. Time budgets a hedging

End-to-end deadline sa rozdelí medzi queue, gateway policy, provider connect, inference, validation a tool execution. Každý retry spotrebúva remaining budget; gateway nesmie začať fallback, ktorý už nemá čas dokončiť validation a bezpečný response commit.

Hedged requests posielajú druhý request po oneskorení, aby znížili tail latency. Pri LLM workload zvyšujú cost a môžu duplikovať tool proposals, preto sa používajú iba pre read-only alebo striktne izolované inference. Víťazný response sa validuje a ostatné attempts sa zrušia, pričom billing a late arrivals ostávajú observované.

## 14. Rate limits a quotas

Gateway môže limitovať requests, input tokens, output tokens, total tokens, concurrent streams alebo cost budget. Request-per-minute limit sám osebe nechráni backend pred niekoľkými extrémne dlhými promptami.

Rate counter sa viaže na správnu identity dimension: tenant, application, user, route alebo cost center. IP adresa je slabý business key pri NAT, shared proxies a mobile clients.

```yaml
limits:
  key: tenant_id
  requests_per_minute: 120
  input_tokens_per_minute: 240000
  output_tokens_per_minute: 40000
  concurrent_requests: 12
  daily_cost_eur: 180
```

## 15. Token preflight

Gateway môže pred requestom odhadnúť token count a odmietnuť prompt, ktorý prekračuje context alebo tenant quota. Odhad musí používať tokenizer/profile kompatibilný s resolved backendom a zahŕňať system instructions, tools, schema a reserved output budget.

Preflight estimate nie je vždy exact provider accounting. Gateway loguje estimated aj provider-reported usage a sleduje rozdiel. Veľká odchýlka môže signalizovať zmenu tokenizeru, hidden provider instructions alebo nesprávnu serialization.

## 16. Backpressure

Pri overload stave gateway obmedzuje admission skôr, než queue rastie bez hranice. Môže vrátiť `429`, prioritizovať high-value traffic, znížiť per-tenant concurrency alebo dočasne vypnúť optional workloads.

Backpressure musí byť explicitná product policy. Nekontrolované queueing zvyšuje latency, drží connection resources a spôsobuje retry storm. Fail-fast response s `Retry-After` môže byť spoľahlivejší než request, ktorý po minúte timeoutne po spotrebovaní provider tokens.

## 17. Fairness a priority

Global quota môže dovoliť jednému tenantovi spotrebovať celú capacity. Fair scheduler používa per-tenant alebo per-workload queues, weighted fairness a hard ceilings. Priority traffic nesmie permanentne vyhladovať bežných používateľov.

Priority je súčasť contractu a auditu. Emergency alebo regulated journey môže dostať vyššiu váhu, ale rozhodnutie musí byť transparentné a merateľné; nesmie byť skryté v ad-hoc headeri klienta.

## 18. Circuit breaker

Circuit breaker zastaví posielanie requestov na backend s vysokou failure alebo latency rate. Stav `open` chráni backend a znižuje cascaded retries, ale jeho threshold a recovery probe musia byť workload-aware.

Invalid-output rate je rovnako dôležitá ako HTTP failure rate. Backend, ktorý vracia `200` s nekompatibilným JSON, je pre daný route unhealthy. Half-open probe overí presný capability contract pred návratom do poolu.

## 19. Request a response transformation

Gateway môže normalizovať provider-specific requesty a response events. Každá transformácia je verzovaný parser/serializer s contract tests. Tiché odstránenie unknown fields alebo zmena role/tool semantics je forbidden.

Streaming transformácia potrebuje commit boundary. Partial provider output sa nesmie prezentovať downstreamu ako complete validated JSON. Pri structured output môže gateway bufferovať, validovať a až potom publikovať, alebo používať provisional event contract, ktorý consumer nesmie commitnúť.

## 20. Authentication a credentials

Aplikácia sa autentifikuje voči gateway vlastnou workload identity. Gateway používa oddelené provider credentials alebo managed identity. Provider keys sa neposielajú klientom a neukladajú do request logs.

Authentication nie je authorization. Gateway policy rozhoduje, ktoré route, modely a tools môže workload použiť, v akom tenant scope a s akým budgetom. Jeden globálny runtime key pre všetky aplikácie znemožňuje attribution a least privilege.

## 21. Data classification a region routing

Route selection filtruje backends podľa data class, residency, retention a subprocessors. Fallback do iného regiónu je data-boundary change, nie iba availability optimization.

```yaml
data_policy:
  customer-confidential:
    allowed_regions: [eu]
    retention_profile: zero-retention-eligible
    external_tools: denied
  public-content:
    allowed_regions: [eu, us]
```

Request trace zaznamenáva applied data policy a resolved region. Provider endpoint hostname bez authoritative deployment metadata nemusí spoľahlivo dokazovať processing location.

## 22. Cost controls

Gateway môže presadzovať budget per tenant, route alebo application a používať price metadata pri routing decision. Cena sa však hodnotí spolu s retries, invalid outputs, human escalations a accepted outcomes.

Hard budget exhaustion má definovaný behavior: fail, defer do batch queue alebo route na kompatibilný lacnejší model. Tiché skrátenie output budgetu alebo vypnutie reasoning/tool capabilities môže meniť correctness a musí byť samostatne evaluované.

## 23. Observability

Gateway telemetry spája attempt-level a operation-level identity. Loguje policy generation, route decision, requested/resolved backend, provider request ID, retries, fallback reason, usage, queue time, TTFT, total latency, validation verdict a business outcome link.

```json
{
  "operation_key": "refund:case-9481:v1",
  "attempt": 2,
  "route_policy": "support-route-v18",
  "backend": "eu-pro-b",
  "fallback_reason": "primary_token_rate_limit",
  "provider_request_id": "req_92...",
  "input_tokens": 4180,
  "output_tokens": 312,
  "schema_valid": true,
  "business_state": "proposal-only"
}
```

Metrics sa segmentujú podľa route, backend, tenant, failure class a fallback. Aggregate success rate môže skryť, že jeden fallback má vysokú invalid-output rate iba pre multilingual alebo long-context segment.

## 24. Deployment a rollout

Gateway policy sa publikuje ako immutable artifact s digestom. Rollout používa canary gateway cohort alebo stable request assignment, aby ten istý tenant či case nepreskakoval medzi policy generations.

Pred promotion sa vykonajú route-table tests, capability probes, negative authorization tests, rate-limit tests, provider outage simulation a fallback contract replay. Control-plane apply success nepreukazuje, že všetky data-plane instances načítali novú generáciu.

## 25. Failure hypotheses

Pri náhlom náraste chýb sa najprv rozdelí problém podľa stage: authentication, policy load, route eligibility, provider connect, rate limit, inference, transformácia, validation alebo downstream business commit. Každá hypotéza predikuje odlišný evidence pattern a má falsifikačný test.

Ak iba jeden tenant dostáva `429`, pravdepodobná je per-key quota alebo nesprávny counter key; global provider saturation by mala zasiahnuť viac tenants. Ak HTTP success ostáva vysoký, ale schema validity klesne iba po fallbacku, príčina je behavior compatibility alebo transformácia, nie sieť. Ak duplicate operations korelujú s timeouts, treba skúmať unknown-outcome retry a operation ledger, nie iba model sampling.

## 26. Containment

Containment vypne nekompatibilný fallback, zastaví write-enabled retries, zníži admission alebo route vráti do fail-closed režimu. Zachová route policy, loaded generation, provider request IDs, attempt timeline a affected operation keys.

Pri cross-region alebo cross-tenant incidente sa okamžite zastaví problematická route a spustí data-incident postup. Reštart gateway bez evidence freeze môže odstrániť loaded-state a queue telemetry a sťažiť RCA.

## 27. Recovery

Recovery obnoví known-good route manifest, overí loaded policy na každom gateway cohort, vykoná capability probes a replay incident cases bez write tools. Následne bounded canary overí schema, tool, latency, rate-limit a business read-back.

Druhá operácia testuje iný tenant, iný failure trigger a fallback recovery. Úspešné zopakovanie jediného pôvodného requestu nepreukazuje fairness, quota isolation ani half-open circuit behavior.

## 28. Acceptance

Pozitívna acceptance vyžaduje exact gateway subject, immutable route generation, capability-aware candidate filtering, explicit fallback contract, identity-scoped quotas, safe retry/idempotency model, data-region policy, layered telemetry a business outcome correlation.

Recovery acceptance vyžaduje known-good route restore, loaded-generation read-back, incident replay, provider/fallback capability validation, unknown-outcome reconciliation a druhú odlišnú operation journey.

Forbidden acceptance je HTTP `200` ako dôkaz kompatibility, fallback na ľubovoľný model, retry write-intentu bez operation ledgeru, IP-only multi-tenant quota, control-plane status ako loaded runtime evidence alebo nižšia token price ako jediný routing verdict.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Prompt caching, semantic caching a response caching](prompt-semantic-response-caching.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Prompt Registry a lifecycle →](prompt-registry-lifecycle.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
