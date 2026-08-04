# Tracing, token usage a cost observability

GenAI observability musí vysvetliť celý application journey, nie iba posledný model call. LLM odpoveď môže vzniknúť cez gateway routing, retrieval, reranking, prompt render, viac provider attempts, streaming, tool calls, retries, cache hits a postprocessing. Ak trace zachytí iba finálny úspešný request, tím môže vidieť nízku latency a správny output, hoci predchádzajúci attempt už vykonal side effect, retrieval použil nesprávnu corpus generation alebo fallback minul trojnásobok plánovaného budgetu.

V incidente `GENAI-SUPPORT-08` support agent pri timeout-e zopakoval model request. Prvý attempt navrhol a vykonal write tool, ale jeho span sa stratil pri sampling drop-e. Druhý attempt skončil úspešne a trace obsahoval iba tento výsledok. Cost dashboard priradil requestu jednu model invocation, hoci provider vyúčtoval tri attempts a tool backend evidoval duplicitnú operáciu. Root cause nebola „nepresná cena“, ale neúplný operation graph a chýbajúce spojenie medzi technical attempts, durable business operation a billing ledger.

## 1. Exact observability subject

Observability subject je jedna business operation a všetky jej execution attempts. Request ID, trace ID, conversation ID a provider request ID nie sú zameniteľné.

```yaml
operation_subject:
  business_operation_id: refund-case-82413
  journey_id: support-session-4801
  trace_id: 4f8c...
  request_attempt: 3
  tenant: sk-retail
  release_manifest: support-release-2026-08-04.8
  model_route: support-policy-v14
  prompt_version: support-answer-v22
  corpus_generation: refund-policy-2026-08-01
  tool_catalog: support-tools-v16
  authorization_snapshot: authz-71c2
```

`business_operation_id` ostáva stabilné cez retry, fallback a reconnect. `request_attempt` sa mení pri každom technickom vykonaní. Trace bez tejto dvojice nevie rozlíšiť jednu pomalú operáciu od viacerých duplicitných attempts.

## 2. Operation graph

Jedna GenAI journey sa modeluje ako parent operation s explicitnými child operations:

```text
incoming request
→ policy a route resolution
→ retrieval query
→ candidate retrieval a reranking
→ context assembly
→ prompt render
→ model invocation attempt 1
→ tool proposal
→ authorization a approval
→ tool execution
→ model invocation attempt 2
→ output validation
→ response commit
→ business outcome
```

Span reprezentuje operáciu s trvaním. Point-in-time udalosti, napríklad cache decision, approval verdict alebo token-budget rejection, môžu byť events. Metrics agregujú správanie cez mnoho operations. Log bez trace correlation je diagnostický text, nie reconstructable journey.

## 3. Trace boundaries

Parent span začína pri prijatí application requestu, nie až pri provider API call-e. Končí sa po committed response alebo durable business outcome, podľa contractu. Streaming response môže byť používateľovi viditeľná pred tým, než je output validation alebo tool workflow úplne uzavretý; trace preto rozlišuje first byte, first token, stream completion a response commit.

Asynchrónne tool jobs alebo delayed business outcomes pokračujú cez propagated correlation. Umelé ukončenie trace pri HTTP 202 zakryje neskorší failure.

## 4. Stable semantic model

Telemetry používa stabilné nízkokardinalitné názvy operations a osobitné attributes pre dynamické identities. Span name nesmie obsahovať user prompt, document ID alebo model-generated tool arguments.

```python
with tracer.start_as_current_span("gen_ai.chat") as span:
    span.set_attribute("gen_ai.operation.name", "chat")
    span.set_attribute("gen_ai.provider.name", provider)
    span.set_attribute("gen_ai.request.model", requested_model)
    span.set_attribute("app.model.resolved", resolved_model)
    span.set_attribute("app.prompt.version", prompt_version)
    span.set_attribute("app.corpus.generation", corpus_generation)
    span.set_attribute("app.request.attempt", attempt)
```

OpenTelemetry GenAI conventions poskytujú spoločný vocabulary pre operation, provider, requested model, token usage, messages a retrieval documents. Ich stability level a verzia sa pinujú; experimentálne attribute names sa nesmú potichu zameniť za stabilný interný contract.

## 5. Content telemetry a privacy

Prompt, system instructions, retrieved documents, model output a tool arguments môžu obsahovať PII, secrets alebo obchodné dáta. Full-content tracing preto nie je default.

```yaml
content_capture:
  default: metadata-only
  allowed_environments: [isolated-eval]
  redaction_policy: pii-secrets-v8
  maximum_bytes: 8192
  retention_days: 7
  access_role: genai-forensics
```

Produkčný trace typicky ukladá digests, length, token counts, classification, source IDs a validation verdict. Raw content sa zachytáva iba v explicitne povolenom režime s redaction, encryption, access control, retention a auditom. Hash nie je anonymizácia, ak sa vstup dá uhádnuť z malého priestoru.

## 6. Model invocation attempts

Každý provider attempt má vlastný span a identity:

```yaml
model_attempt:
  attempt: 2
  provider_request_id: req_91b...
  requested_model: provider/model-pro
  resolved_model: provider/model-pro-2026-07-28
  region: eu
  status: timeout-after-headers
  output_commit_state: unknown
  input_tokens: 5820
  cached_input_tokens: 4100
  output_tokens_observed: 214
```

Timeout neznamená, že provider nič nespracoval. Pri streaming disconnecte môže byť časť outputu alebo tool proposal už vytvorená. Retry policy loguje failure class, retry eligibility, delay, route mutation a unknown-outcome read-back.

## 7. Retrieval a context telemetry

Retrieval trace potrebuje query generation, collection/index generation, filters, top-k, reranker, candidate IDs, scores a selected evidence IDs. Samotné `search=200` nepreukazuje správny evidence set.

```yaml
retrieval_span:
  corpus_generation: refund-policy-2026-08-01
  embedding_generation: embed-v9
  index_generation: refunds-hnsw-44
  query_rewrite: support-query-v7
  mandatory_filters:
    tenant: sk-retail
    effective_at: 2026-08-04T09:00:00Z
  retrieved: 20
  reranked: 8
  packed: 5
```

Context assembly zaznamená token budget, truncation, deduplication, conflicts a citation-label mapping. Bez toho sa factuality regression nesprávne pripíše modelu.

## 8. Tool a side-effect telemetry

Tool proposal a tool execution sú dve operácie. Trace zaznamená proposed tool, validated schema, authorization decision, approval, idempotency key, downstream request ID a durable outcome.

```yaml
tool_execution:
  tool: create_refund
  proposal_id: toolcall_3f1
  authorization: allowed
  approval: required-and-confirmed
  idempotency_key: refund-case-82413
  downstream_operation_id: refunds-77102
  outcome: committed
```

Sensitive arguments sa nahradia typed summary alebo digestom. Tool success znamená transport alebo API success iba vtedy, ak backend contract takto definuje outcome. Business read-back je samostatná evidence.

## 9. Token accounting

Token telemetry rozlišuje input, cached input, output, reasoning alebo equivalent provider-specific usage, tool payload a embedding tokens. Provider usage je authoritative pre billing konkrétneho requestu, ale application tokenizer estimate je potrebný pre admission a predikciu.

```text
estimated tokens before request
≠ provider-reported billable usage
≠ application-visible output tokens
≠ useful accepted output tokens
```

Pri streaming failure môže application pozorovať menej textu, než provider vyúčtuje. Pri cache hit-e sa input token count môže zachovať, ale billable rate je odlišná. Cost model musí používať provider pricing generation platnú v čase execution.

## 10. Cost ledger

Cost sa nepočíta iba z model tokens. Ledger zahŕňa retrieval, reranking, embedding, built-in tools, external APIs, GPU serving, cache infrastructure, retries, human review a durable side effects.

```yaml
cost_entry:
  operation_id: refund-case-82413
  component: model-inference
  provider_request_id: req_91b
  pricing_version: provider-eu-2026-08-01
  quantity:
    input_tokens: 5820
    cached_input_tokens: 4100
    output_tokens: 214
  calculated_cost_eur: 0.0318
  source: provider-usage
  reconciliation_state: provisional
```

Online estimate je provisional. Neskoršia invoice alebo provider usage export môže viesť k reconciliation adjustment. Cost dashboard bez pricing version a billing source nevie reprodukovať historickú sumu.

## 11. Unit economics

Najdôležitejšia metrika nie je cena jedného call-u, ale cena accepted outcome-u.

```text
cost per accepted case =
(model + retrieval + tools + platform + review + retry cost)
/
accepted business outcomes
```

Lacnejší model môže zvýšiť retries a escalation. Prompt cache môže znížiť billable input, ale zhoršiť latency pri miss storme. Unit economics sa segmentuje podľa route, tenant, language, risk class a outcome.

## 12. Latency decomposition

End-to-end latency sa rozkladá na queue, gateway policy, retrieval, context assembly, provider queue, time to first token, decode, tools, validation a response commit.

```yaml
latency_ms:
  queue: 48
  route_resolution: 3
  retrieval: 91
  prompt_render: 7
  provider_ttft: 420
  generation: 880
  tool_wait: 1400
  validation: 18
  total: 2867
```

Aggregate average zakrýva p95/p99 a multimodálnu distribúciu. Tool workflow a no-tool workflow sa neporovnávajú bez segmentácie.

## 13. Streaming observability

Streaming potrebuje checkpoints: request accepted, first byte, first token, first validated chunk, stream end, output validation a committed response. Token count počas streamu je priebežný a nemusí sa rovnať provider final usage.

Cancellation sa klasifikuje podľa pôvodu: user cancel, client disconnect, gateway timeout, provider error alebo application abort. Bez tohto rozlíšenia sa vysoká cancellation rate môže zameniť za model latency problém.

## 14. Cache telemetry

Prompt/prefix, semantic a response cache majú odlišné events. Zaznamenáva sa cache type, key generation, hit/miss/bypass, security scope, dependency generations, age, validation a false-hit verdict.

Hit rate bez accepted-output rate je nebezpečná. Semantic cache môže zlepšiť latency a súčasne zvýšiť wrong-answer rate. Prefix cache hit znižuje compute, ale odpoveď sa stále generuje nanovo.

## 15. Sampling

Head sampling rozhoduje pred známym outcome-om, preto môže zahodiť zriedkavé failures. Tail sampling môže ponechať traces podľa error, latency, security eventu, fallbacku alebo high cost.

```yaml
sampling:
  baseline: 2_percent
  keep_if:
    - error
    - fallback_used
    - tool_write
    - cost_eur_above_0.20
    - prompt_injection_signal
    - latency_p99_candidate
```

Sampling decision sa nesmie aplikovať nezávisle na child spans tak, že zostane orphan model call bez parent journey. Security a billing evidence môže vyžadovať samostatný unsampled ledger s minimal metadata.

## 16. Cardinality

Tenant, user ID, prompt digest, document ID a request ID sú vysokokardinalitné. Nie všetko patrí do metric labels. Metrics používajú bounded dimensions; exact identities zostávajú v traces alebo logs.

Unbounded label môže zničiť telemetry backend alebo dramaticky zvýšiť cost. Redaction a cardinality policy sa testujú pred rolloutom instrumentácie.

## 17. Metrics

Core metrics zahŕňajú request rate, success/error, latency, TTFT, output token rate, input/output/cached tokens, provider attempts, fallback rate, tool execution rate, validation failures, retrieval no-evidence, cost a accepted outcome.

```text
technical success
→ model response returned

contract success
→ schema, policy a tool constraints passed

journey success
→ user task completed

business success
→ durable intended outcome confirmed
```

Tieto vrstvy sa nesmú zlúčiť do jedného `success=true`.

## 18. SLO a budget

SLO sa definuje pre konkrétny user journey a segment. Latency SLO môže používať TTFT aj total completion; reliability SLO musí určiť, či no-answer je úspech pri nedostatku evidence.

Cost budget môže byť per request, per tenant, per feature alebo per accepted case. Hard budget gate pred execution používa estimate; post-execution ledger používa actual usage. Budget overrun je operation outcome, nie iba finančný report.

## 19. Release comparison

Telemetry musí umožniť porovnať candidate a baseline podľa full release manifestu. Model-only dimension nestačí, ak sa súčasne zmenil prompt, retriever alebo gateway policy.

```yaml
release_dimensions:
  model: provider/model-pro-2026-07-28
  prompt: support-answer-v22
  corpus: refund-policy-2026-08-01
  retriever: hybrid-v10
  tools: support-tools-v16
  gateway_policy: gateway-v13
  guardrails: guardrails-v8
```

Canary assignment sa loguje spolu s exposure unit. Inak sa users preskakujúci medzi variants javia ako stochastic model variance.

## 20. Outcome join

Technical trace sa spája s delayed outcome cez durable operation ID. Ticket resolution, refund reversal alebo complaint môže prísť o hodiny neskôr.

Join musí rešpektovať late arrivals, corrections a multiple outcomes. Bez mature label window sa čerstvý candidate môže javiť lepší iba preto, že jeho negatívne outcomes ešte nedorazili.

## 21. Security events

Prompt injection signal, policy override attempt, forbidden tool proposal, cross-tenant cache key, secret pattern a unusual egress destination sa zapisujú ako structured security events. Samotný model refusal nie je dôkaz, že útok nemal side effect v skoršom tool kroku.

Security telemetry minimalizuje raw malicious content a zachová attack class, source trust, affected capability, verdict a evidence references.

## 22. Cost anomaly diagnosis

Pri cost spike sa najprv rozdelí volume, tokens per request, retries, route mix, cache hit, output length, tool usage a pricing changes. Aggregate suma nevysvetlí príčinu.

```text
cost increase =
traffic volume effect
+ mix effect
+ unit price effect
+ retry effect
+ token length effect
+ tool/platform effect
```

Každá hypotéza má predikovaný trace alebo ledger evidence. „Model zdražel“ bez pricing-version porovnania je neoverená domnienka.

## 23. Missing telemetry ako state

Chýbajúci span alebo usage nie je nula. Telemetry pipeline zaznamenáva dropped spans, exporter failures, queue pressure, schema rejection a sampling rate. Dashboard s neúplnými dátami musí niesť completeness verdict.

```yaml
telemetry_completeness:
  traces_received_ratio: 0.973
  usage_join_ratio: 0.991
  outcome_join_ratio_mature: 0.884
  verdict: incomplete-for-promotion
```

Promotion založená na neúplnom candidate telemetry je forbidden.

## 24. Forensic replay

Incident package obsahuje release manifest, trace graph, provider request IDs, retrieval evidence IDs, tool ledger, usage/cost entries, security events a outcome. Raw content sa pripojí iba podľa privacy policy.

Replay používa izolované prostredie a write tools sú stubované alebo idempotentné. Reprodukcia model textu nemusí byť bit-identical; cieľom je overiť first divergence a contract behavior.

## 25. Failure hypotheses

Ak dashboard ukazuje nízku cenu, ale invoice rastie, preverí sa dropped attempts, cached-token pricing, unjoined providers, tool fees, regional price a pricing-version drift. Ak trace ukazuje success, ale user journey zlyhal, preverí sa response commit, tool durable outcome, delayed label a fallback route. Ak chýba iba security incident, preverí sa sampling, redaction pipeline, event schema a tenant-specific instrumentation.

Diagnostika začína completeness a identity kontrolou. Analýza perfektného grafu nad nesprávnym release alebo neúplnými attempts iba vytvorí presný, ale chybný záver.

## 26. Containment a recovery

Containment môže vypnúť fallback, write tools alebo high-cost route; zvýšiť tail sampling; zapnúť metadata-only forensic capture; a zastaviť promotion. Existujúce durable operations sa read-backnú pred retry.

Recovery opraví instrumentation alebo correlation, backfillne usage a outcomes, zreconciliuje cost ledger a zopakuje bounded canary. Druhá operácia musí overiť odlišnú route, tool alebo failure class a potvrdiť, že telemetry zostane complete aj pri retry a cancellation.

## 27. Acceptance

Pozitívna acceptance vyžaduje end-to-end operation graph, stable business/attempt identity, exact release dimensions, provider usage a pricing lineage, retrieval/tool/outcome correlation, privacy-safe content policy, completeness telemetry, segment metrics a cost per accepted outcome.

Recovery acceptance vyžaduje identifikovaný first missing alebo wrong span, opravenú correlation, reconciled ledger, replay alebo canary a second-operation test vrátane retry, fallback alebo tool side effectu.

Forbidden acceptance je provider dashboard ako úplný application trace, missing usage ako zero, request average ako SLO, token price ako total cost, sampled success trace ako dôkaz bez duplicated attempts alebo observability workflow ako runtime `Verified` business outcome.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Human evaluation a expert feedback](human-evaluation-expert-feedback.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Hallucination, faithfulness a factuality →](hallucination-faithfulness-factuality.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
