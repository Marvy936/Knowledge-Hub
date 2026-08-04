# Prompt caching, semantic caching a response caching

LLM application môže používať viac cache vrstiev, ktoré majú rozdielne semantics. Prompt alebo prefix caching znovu používa vypočítané model states pre identický token prefix, ale model stále generuje nový output. Semantic caching približne porovná nový request s predchádzajúcimi významovo podobnými requests a môže znovu použiť uložený result. Response caching vracia predchádzajúcu response pre exact application key. Zamieňanie týchto vrstiev vytvára security, freshness a correctness chyby.

V incidente `GENAI-SUPPORT-06` tím zaviedol semantic cache podľa embedding similarity user otázky. Cache key neobsahoval tenant, authenticated entitlements, model/prompt release ani RAG corpus generation. Otázka jedného zákazníka „Mám nárok na refundáciu?“ bola vyhodnotená ako podobná staršej otázke iného tenant contextu a systém vrátil cached answer s neplatnou policy verziou. Trace obsahoval iba `cache_hit=true`, takže nebolo zrejmé, či sa reuse-nul provider prefix, application response alebo semantic neighbor. Root cause bolo neexplicitné cache contract, nedostatočné namespacing/invalidation a zamieňanie latency gainu za business correctness.

## 1. Business outcome a cache boundary

Cache znižuje compute, latency alebo external calls iba vtedy, keď reuse zachováva required semantics a authority boundary.

```text
request subject
→ cache eligibility
→ exact alebo approximate lookup
→ reuse validation
→ result alebo normal execution
→ authoritative outcome
```

Cache hit je optimization event, nie acceptance verdict. Correctness sa hodnotí podľa výsledku pre aktuálneho principal, model release, policy/corpus generation a business state.

## 2. Tri odlišné cache contracts

Cache vrstvy sa rozlišujú podľa toho, čo presne sa reuse-uje a ktorý computation alebo business contract sa tým preskakuje. Prefix cache zachováva iba modelový medzivýpočet, semantic cache robí approximate rozhodnutie o ekvivalencii requestov a response cache vracia už vytvorený application result. Čím viac vrstiev sa preskočí, tým silnejší musí byť key, authorization, freshness a validation gate.

```text
prompt/prefix cache
→ reuse model prefill computation pre identický prefix
→ nový decode/output

semantic cache
→ approximate query match
→ reuse predchádzajúceho application resultu alebo intermediate artifactu

response cache
→ exact application key
→ reuse predchádzajúcej response
```

Názov „LLM cache“ bez typu je diagnosticky nepoužiteľný. Každá vrstva má vlastný key, scope, TTL, invalidation, privacy a observability.

## 3. Exact cache subject

Cache entry manifest identifikuje nielen uložené bytes, ale aj podmienky, za ktorých je ich reuse semanticky a bezpečnostne platný. Model, adapter, prompt, tools, corpus, locale a authorization scope patria do subjectu, pretože zmena ktorejkoľvek z týchto vrstiev môže pri rovnakom user texte vytvoriť iný správny výsledok. Entry age a TTL dopĺňajú generation identity, ale nenahrádzajú ju.

Cache entry manifest obsahuje:

```yaml
cache_entry:
  cache_type: semantic_response
  namespace: support-eu-tenant-817
  key_version: support-semantic-key-v6
  model_release: support-llm-route-v24
  adapter_release: refund-lora-v7
  prompt_release: support-refund-v18
  tool_catalog: support-tools-v13
  corpus_generation: support-policy-42
  authorization_scope_digest: sha256:c129...
  locale: sk-SK
  created_at: 2026-08-04T08:10:00Z
  expires_at: 2026-08-04T08:20:00Z
  source_request_digest: sha256:19aa...
  response_digest: sha256:8b4f...
```

Nie všetky fields musia byť uložené ako raw content; digest a metadata však musia umožniť bezpečný scope a reprodukciu.

## 4. Prompt alebo prefix caching

Transformer prefill vypočíta KV states pre input tokens. Ak ďalší request zdieľa identický prefix pod compatible model state, runtime alebo provider môže tieto states reuse-nuť.

```text
identické prefix tokens
+ rovnaký effective model/adapter
+ compatible runtime cache scope
→ reuse prefill states
→ generuj nový suffix
```

Prompt caching nevracia starú odpoveď. Neodstraňuje sampling variability, tool execution ani potrebu output validation.

## 5. Prefix identity

Prefix identity je token-level, nie iba text-level. Rozdiel v template, whitespace, JSON property order, tool schema, image bytes alebo special tokens môže zrušiť hit.

```text
system instructions
→ tool definitions
→ static examples/context
→ variable user/request data
```

Stabilný content patrí na začiatok a variable content neskôr, ak to neporuší instruction hierarchy alebo security. Optimalizácia prompt order nesmie oslabiť trust boundaries.

## 6. Prompt cache key scope

Safe prefix key zahŕňa alebo implicitne dedí:

```text
provider/runtime
model snapshot alebo effective weights
adapter identity
serialized token prefix
attention/position relevant config
security namespace alebo cache salt
```

KV states z iného modelu alebo adaptera nie sú compatible. Multi-tenant runtime používa tenant/security salt alebo izolovaný pool, ak prefix obsahuje sensitive content.

## 7. Provider prompt cache verzus self-hosted prefix cache

Managed provider môže automaticky cacheovať common prefixes a reportovať `cached_tokens` alebo podobnú usage field. Self-hosted runtime môže ukladať KV blocks vo vlastnom memory manageri.

Tieto systems majú rozdielne retention, isolation a eviction guarantees. Application musí čítať aktuálnu provider/runtime dokumentáciu a nesmie predpokladať, že cache je persistentná, dostupná v každom region/modeli alebo compatible so zero-retention policy.

## 8. Prompt cache economics

Prompt cache benefit závisí od reusable prefix length, hit rate, retention, request locality a provider pricing.

```text
saved prefill work ≈ cached input tokens × hits
```

Skutočný cost model zahŕňa cache-write cost, cached-input price, misses, serialization changes a latency. Veľký static prefix môže byť lacnejší pri hit rate, ale stále zvyšuje context occupancy a môže znížiť effective signal-to-noise.

## 9. Prefix invalidation

Prompt cache sa prirodzene invaliduje pri zmene prefix tokens alebo scoped model state. Application release však musí vedieť, ktoré zmeny bustnú cache:

```text
prompt/template update
tool schema/order update
RAG static context update
model alebo adapter update
security salt rotation
```

Cache miss po release nie je incident, ak je očakávaný. Capacity plan počíta s cold-cache obdobím a rolloutom.

## 10. Semantic caching

Semantic cache vytvorí representation requestu a hľadá podobný existujúci key. Potom môže reuse-nuť response alebo intermediate result.

```text
current request
→ normalized semantic subject
→ embedding
→ nearest cached entries
→ eligibility/threshold/authority checks
→ reuse alebo miss
```

Approximate similarity znamená, že dva requests nie sú identické. Preto semantic hit potrebuje silnejšie validation než exact cache.

## 11. Čo je semantic subject

User text sám osebe často nestačí. Význam requestu závisí od conversation state, locale, authenticated principal, product state, policy version, tools a requested output contract.

```json
{
  "intent": "refund_eligibility",
  "question": "Mám nárok na refundáciu?",
  "locale": "sk-SK",
  "product": "flight",
  "case_state": "delayed_over_3h",
  "policy_generation": "eu261-2026-07",
  "authorization_scope": "customer:self"
}
```

Semantic key sa buduje zo serverom odvodeného structured subjectu. Model-generated normalization sa validuje a nesmie meniť identity alebo entitlement.

## 12. Similarity threshold

Threshold je workload-specific trade-off medzi hit rate a false reuse. Vysoká cosine similarity nepreukazuje rovnaký business answer.

Príklady podobných, ale neekvivalentných questions:

```text
„Môžem dostať refundáciu?“
„Môžem dostať refundáciu za nevratný firemný tarif?“
„Môžem dostať refundáciu po čiastočnom použití?“
```

Critical qualifiers môžu tvoriť malú časť embeddingu. Eligibility filter preto porovnáva structured facets a semantic similarity používa iba vnútri rovnakého contract scope.

## 13. Semantic cache safety gate

Safe reuse path:

```text
same tenant/security namespace
same model/prompt/corpus/tool contract
non-expired entry
same structured facets
similarity above calibrated threshold
response class cacheable
optional verifier
→ reuse
```

Ak jedna podmienka chýba, ide o miss. Fail-open pri cache backend error je acceptable iba tak, že sa vykoná normal model path, nie že sa vráti nearest stale entry.

## 14. Cacheable a non-cacheable classes

Semantic response reuse je vhodnejšie pre stable public FAQ, canonical definitions alebo read-only informational results. Je rizikové pre personalized, transactional, authorization-sensitive, temporal alebo high-stakes answers.

```yaml
cache_policy:
  public_product_definition: semantic_allowed
  current_price: exact_short_ttl_only
  account_balance: no_shared_cache
  refund_decision: no_semantic_response_cache
  generated_tool_plan: no_cache
```

Niektoré workloads môžu semantic-cacheovať retrieval candidates alebo query embeddings, ale stále vykonať fresh authorization, context assembly a generation.

## 15. Response caching

Response cache používa exact application key a vracia stored response. Je vhodný, keď rovnaký request subject má počas TTL rovnaký answer contract.

```text
canonical exact key
→ lookup
→ freshness/authorization check
→ stored response
```

Exact text request nie je vždy exact business subject. Current inventory alebo user state musí byť súčasť key alebo response nesmie byť cacheovaná.

## 16. Determinism a response cache

Response caching mení behavior sampled modelu: opakovaný request dostane starý output namiesto novej sample. To môže byť zámerné, ale musí byť súčasť product contractu.

Pri creative generation je cache často nevhodná alebo explicitne opt-in. Pri deterministic extraction môže byť vhodná, ak key zahŕňa input bytes, model/prompt/schema release a decoding configuration.

## 17. Canonical cache key

Key sa serializuje deterministicky:

```python
import hashlib
import json

subject = {
    "tenant": tenant_id,
    "principal_scope": sorted(entitlements),
    "model_release": model_release,
    "prompt_release": prompt_release,
    "schema": schema_release,
    "corpus_generation": corpus_generation,
    "request": validated_request,
}

payload = json.dumps(subject, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
cache_key = "support:v6:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()
```

Raw secrets sa nevkladajú do key names. HMAC alebo namespace isolation môže byť vhodnejšia pri citlivých identifiers.

## 18. Authorization pred cache lookupom

Cache nesmie obísť authorization. Principal a entitlements sa overia pred použitím entry a authorization-relevant scope je súčasťou key alebo metadata filteru.

```text
authenticate
→ authorize requested resource
→ derive cache namespace/key
→ lookup
```

Pattern `lookup by document_id → potom skontroluj access` môže leaknúť timing, existence alebo content. Pre RAG sa ACL filter aplikuje pred retrieval aj pred reuse stored evidence.

## 19. Tenant isolation

Shared cache môže byť efektívna iba pre skutočne public, non-personal content. Tenant-specific prompts, adapters, corpora a responses používajú oddelený namespace/salt.

```text
public immutable knowledge
→ public cache

tenant corpus alebo user context
→ tenant/principal-scoped cache
```

Tenant name z user inputu nie je trusted namespace. Scope pochádza z authenticated server contextu.

## 20. Freshness, TTL a version invalidation

TTL je časový bound, nie dôkaz, že data ostali správne počas celého intervalu. Versioned dependencies sú silnejšie:

```text
model release
prompt release
corpus/index generation
tool/business API version
policy effective period
```

Ak sa dependency zmení, nový key prirodzene missne. Explicit invalidation sa používa pri revocation, incidentoch alebo unversioned upstream state.

## 21. Event-driven invalidation

Pri mutable business entities môže source system publikovať version/event:

```text
policy updated
→ create new policy generation
→ switch authoritative pointer
→ expire related response/semantic entries
```

Invalidation event potrebuje idempotency a audit. Ak sa cache delete nepodarí, versioned key stále zabráni reuse starej generation. Preto sa preferuje immutable generation plus pointer switch pred masovým best-effort delete.

## 22. Negative caching

Caching `not found`, refusal alebo upstream error môže znížiť load, ale potrebuje krátky TTL a presný error class.

```text
404 immutable object
→ môže byť cacheable

503 dependency outage
→ nemá byť dlhodobo cacheované ako business absence
```

Model refusal môže závisieť od current safety policy a request context. Negative entry nesmie zamraziť transient failure.

## 23. Cache stampede

Po expiracii populárneho key môžu stovky requests naraz spustiť rovnaký expensive model call. Ochrany zahŕňajú single-flight, request coalescing, jittered TTL a stale-while-revalidate pre bezpečné read-only classes.

```text
first miss
→ acquire per-key lease
→ execute
→ publish entry

followers
→ bounded wait alebo independent fallback podľa SLO
```

Lease timeout nesmie uviaznuť po crashed producerovi. High-risk responses sa nevracajú stale iba kvôli latency.

## 24. Streaming a partial responses

Partial streamed output nie je complete cache entry. Entry sa publikuje až po finish reason, schema/content validation a prípadnom authoritative read-back.

```text
stream chunks
→ temporary buffer
→ completion status
→ validation
→ atomic cache publish
```

Client disconnect môže zrušiť generation alebo server pokračovať; cache policy musí byť explicitná. Incomplete output sa nesmie označiť ako hit-ready.

## 25. Tool calls a side effects

Tool proposal ani result s write side effectom sa bežne nereuse-uje ako response cache. Cached tool call ID alebo arguments môžu zopakovať stale alebo unauthorized action.

Read-only tool data môže mať vlastný cache contract na data-access vrstve. Model stále dostane fresh authorization-scoped evidence. Idempotency key rieši duplicate execution, nie response caching.

## 26. RAG caching layers

RAG môže cacheovať viac stages:

```text
parsed document/chunks
embeddings
query embedding
retrieval result
reranker result
assembled context
final answer
```

Každá stage má iné invalidation dependencies. Query embedding závisí od embedding model, retrieval result od index generation a filters, context od assembly policy a final answer od model/prompt/schema.

Cacheovať final answer s dlhým TTL, keď corpus je mutable, je najrizikovejšie. Intermediate exact caches často prinášajú benefit s menšou correctness stratou.

## 27. Cache hierarchy

Application môže používať:

```text
L1 worker memory
→ nízka latency, replica-local

L2 distributed cache
→ shared hit rate, network a tenant isolation

provider/runtime prompt cache
→ prefill reuse mimo application response store
```

L1 a L2 version/key contract musí byť konzistentný. Local stale entry nesmie prežiť invalidation iba preto, že distributed cache bola opravená.

## 28. Eviction

Eviction policy môže byť LRU, LFU, size-aware, cost-aware alebo semantic-aware. Najčastejšie entry nemusí mať najväčšiu compute hodnotu a veľký entry môže vytlačiť tisíce malých.

Eviction je performance decision; correctness nesmie závisieť od entry prítomnosti. Miss vždy spustí validný normal path.

## 29. Privacy a retention

Prompt, embeddings, KV states a responses môžu obsahovať personal alebo confidential data. Cache potrebuje data classification, encryption, access control, retention a deletion semantics.

Prompt cache providera môže mať odlišnú eligibility pri zero-retention alebo regional processing. Self-hosted KV blocks sú stále application state v GPU memory a môžu byť zdieľané iba podľa explicitných isolation guarantees.

Semantic embeddings nie sú automaticky anonymné. Môžu niesť information o inpute a patria do rovnakého governance scope ako odvodené data.

## 30. Poisoning a untrusted content

Attacker môže skúsiť vložiť response do cache cez crafted prompt alebo kontaminovaný RAG context a potom vyvolať semantic hits pre iných users.

Mitigácie zahŕňajú trusted write path, validation pred publish, tenant scope, minimum support/citation evidence, abuse limits a no-cache policy pre adversarial alebo low-confidence cases.

Cache entry sa nikdy nevytvára z nevalidovaného partial outputu alebo tool outputu považovaného za trusted instruction.

## 31. Observability

Každý request zaznamenáva:

```json
{
  "cache_layer": "semantic_response",
  "lookup_result": "hit",
  "key_version": "support-semantic-key-v6",
  "namespace": "tenant-817",
  "entry_generation": "support-policy-42",
  "age_ms": 18420,
  "similarity": 0.94,
  "threshold": 0.97,
  "eligibility_verdict": "rejected-below-threshold",
  "fallback": "normal-inference"
}
```

Pri prompt cache sa logujú input tokens, cached tokens, hit/miss a retention mode. Pri response cache sa loguje age, TTL, invalidation generation a served digest. Sensitive raw content sa nemusí logovať.

## 32. Cache metrics

Hit rate bez quality je nebezpečná optimization. Metrics zahŕňajú:

```text
lookup hit rate
eligible hit rate
reused tokens alebo saved compute
latency/cost savings
false semantic hit rate
stale response rate
cross-scope violation rate
cache-induced retry/escalation
business outcome per hit/miss
```

Semantic threshold sa kalibruje na labeled pairs a monitoruje sa drift. Vyšší hit rate nie je cieľ, ak zvyšuje false reuse.

## 33. Testing

Test matrix zahŕňa:

```text
exact repeat
same intent s kritickým qualifierom
same text v inom tenant scope
model/prompt/corpus release change
entry expiration
revocation/invalidation
cache backend outage
concurrent stampede
partial stream a tool path
```

Forbidden-hit tests sú rovnako dôležité ako positive hit. Second-operation test overí, že po invalidácii vznikne fresh result pre odlišný request.

## 34. Failure hypotheses

Pri nesprávnom cached result sa skúma cache type, key version, namespace, dependency generations, TTL, semantic threshold/facets, authorization order, publish validation a invalidation delivery.

Pri nízkom prompt hit rate sa kontroluje token prefix stability, model/adapter scope, prompt/tool ordering, retention a rollout cold start. Pri cost spike sa oddelí cache-write cost, misses, output generation, tool/retrieval a stampede.

## 35. Containment

Containment vypne problematickú cache layer alebo konkrétnu key version, nie nevyhnutne všetky caches. Semantic response cache sa môže fail-closed na miss, zatiaľ čo safe prompt prefix caching ostane aktívny.

Pri cross-tenant incidente sa izoluje namespace, zneplatnia entries, rotuje salt/key version a spustí privacy/security incident proces. Zachovajú sa entry metadata a request traces podľa retention policy.

## 36. Recovery

Recovery opraví key composition, authorization ordering, threshold/facets, TTL alebo invalidation generation a nasadí novú cache key version. Staré entries sa nereinterpretujú pod novým contractom.

```text
known-bad key v5
→ disable
→ key v6 build
→ replay positive a forbidden cases
→ bounded canary
→ monitor false-hit/outcome
```

Second-operation test zahŕňa iného tenant scope alebo critical qualifier a overí normal miss aj následný bezpečný hit.

## 37. Acceptance

Pozitívna acceptance vyžaduje explicitne oddelené prefix, semantic a response cache contracts; exact model/adapter/prompt/corpus/security subject; deterministic keys; authorization pred lookupom; calibrated semantic eligibility; versioned freshness/invalidation; atomic publish; privacy/isolation; hit aj false-hit telemetry; load/stampede test a accepted-outcome measurement.

Recovery acceptance vyžaduje identifikovanú cache layer a bad key generation, bezpečný disable/rollback, novú version, positive aj forbidden replay, canary a druhú odlišnú operation po obnovení.

Forbidden acceptance je `cache_hit=true` bez typu a subjectu, semantic similarity ako business equivalence, shared cache bez tenant/authorization scope, TTL ako jediná freshness guarantee, partial stream uložený ako complete answer, cached tool side effect alebo hit-rate zvýšenie prezentované ako quality improvement.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: GPU memory, batching a serving performance](gpu-memory-batching-serving-performance.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
