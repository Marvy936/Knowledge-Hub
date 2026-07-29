# Caching

Cache je odvodená kópia alebo vypočítaný výsledok uložený bližšie k consumerovi, aby znížil latency, load alebo cost. Cache nie je automaticky source of truth. Jej správnosť závisí od **cache key identity, freshness, invalidation, authority fallbacku, failure semantics a toho, či stale alebo absent value môže zmeniť business decision**.

```text
business read alebo computed result
→ exact cache subject a authority
→ cache key/variant identity
→ lookup a hit/miss classification
→ freshness a validation
→ fill/update/invalidation
→ eviction/expiry/failure
→ authoritative fallback alebo bounded stale use
→ business outcome
→ mutation/failover/second-read validation
```

## 1. Exact cache subject

Tvrdenie `Redis cache má TTL 15 minút` je neúplné. Subject musí uvádzať:

- business value alebo representation;
- authoritative owner a version/generation;
- cache layer a topology;
- cache key a všetky variant dimensions;
- serialization/schema generation;
- fill pattern;
- freshness a staleness tolerance;
- invalidation/update mechanism;
- eviction a capacity policy;
- hit/miss/error semantics;
- consistency requirement;
- fallback behavior;
- observability a recovery.

Príklad:

```text
value: merchant settlement policy
owner: MySQL merchant-policy generation 1842
cache: Redis policy-cache-v3
key: merchant_id + policy_generation
freshness: immutable generation key, pointer max age 30 s
miss: authoritative MySQL lookup
error: bounded fallback, never infer default allow
```

## 2. Cache authority boundary

Cache môže obsahovať:

- derived projection;
- immutable artifact;
- computed query result;
- session/token metadata;
- rate-limit counter;
- negative lookup;
- materialized policy decision;
- HTTP representation.

Každá kategória má iné correctness requirements. `Cache miss` môže znamenať:

- value nikdy nebola načítaná;
- expirovala;
- bola evicted;
- cache restartla;
- invalidation ju odstránila;
- key/schema generation sa zmenila;
- request používa nesprávny variant key;
- authoritative fact neexistuje.

Iba posledný bod je business absence. Cache miss sa preto nesmie automaticky interpretovať ako `operation neexistuje`, `policy nepovoľuje` alebo `user nemá entitlement` bez explicitného fail-safe contractu.

## 3. Cache key

Cache key je identity cached representation-u. Musí zahŕňať všetky dimensions, ktoré menia výsledok:

- resource/business ID;
- tenant/merchant/account;
- authorization scope;
- locale/currency;
- API/schema version;
- policy/config generation;
- query parameters;
- representation format;
- feature/ring cohort;
- dependency version.

Missing dimension môže spôsobiť stale result alebo cross-tenant leak. Príliš veľa unbounded dimensions vytvorí cardinality a low hit ratio.

Key design musí rozlišovať stable identity od mutable state. Vhodný model pre versioned policy:

```text
pointer key: policy-current:{merchant_id} → generation 1842
immutable value key: policy:{merchant_id}:1842 → policy body
```

Update zmení immutable generation a potom pointer. Old readers môžu bounded používať starú generation, no nemajú dostať nový pointer s old body.

## 4. Freshness, expiry a validation

### Time-to-live

TTL určuje, ako dlho entry zostane eligible bez explicitnej obnovy. Nie je to garancia, že entry bude existovať celý čas; eviction alebo failure ju môže odstrániť skôr.

### Freshness

Freshness je business verdict, či cached value možno použiť pre konkrétnu operation v konkrétnom čase.

### Validation

Consumer overí cache version/validator voči authority alebo metadata.

HTTP caching podľa RFC 9111 rozlišuje fresh response, stale response a validation pomocou validators, napríklad ETag. Rovnaký princíp sa používa aj mimo HTTP: version alebo generation umožní zistiť, či cached value zodpovedá current authority.

## 5. Cache patterns

### Cache-aside

```text
read cache
→ hit: return
→ miss: read authority
→ fill cache
→ return
```

Application vlastní fill a fallback. Riziká sú stampede, stale fills a race s mutation.

### Read-through

Cache layer sama načíta authority. Zjednoduší clients, ale presúva schema, auth a failure semantics do cache providera.

### Write-through

Write prejde cez cache do authority. Acknowledgement musí pomenovať, či authority už commitla.

### Write-behind/write-back

Cache ackne pred durable authority write-om. Znižuje latency, ale cache sa stáva durability/ordering/recovery boundary.

### Refresh-ahead

Entry sa obnoví pred expiry. Potrebuje demand prediction, concurrency control a stale-fill ochranu.

## 6. Invalidation

Invalidation je distribuovaný consistency protocol.

Možnosti:

- delete exact key po commit-e;
- update exact generation;
- publish invalidation event;
- short TTL;
- versioned key/pointer;
- CDC-driven invalidation;
- namespace/generation bump.

Nesprávne poradie:

```text
delete cache
→ database update fails
→ old value sa znovu načíta alebo cache ostane empty
```

Iný race:

```text
reader načíta old DB value
→ writer commitne new value a invaliduje cache
→ reader neskôr zapíše old value do cache
```

Ochrany:

- version/generation compare-and-set;
- write cache only if authority version still matches;
- immutable generation keys;
- delayed second invalidation;
- CDC/outbox event after commit;
- bounded TTL;
- read-your-write path pre mutation ownera.

## 7. Cache consistency models

Cache môže poskytovať:

- best-effort eventual freshness;
- bounded staleness;
- read-your-write pre session/user;
- monotonic reads;
- version-pinned reads;
- invalidation-before-next-decision;
- no stale authorization/policy decision.

Nie každá hodnota potrebuje rovnaký model. Product catalog môže tolerovať minúty stale state-u. Settlement authorization, idempotency alebo revocation môžu vyžadovať current generation alebo authoritative lookup.

## 8. Stampede, herd a hot keys

Pri expiry populárneho keyu môže veľa requests naraz načítať authority.

Ochrany:

- single-flight/request coalescing;
- distributed lock s fencing/timeout semantics;
- probabilistic early refresh;
- jittered TTL;
- stale-while-revalidate;
- per-key admission;
- prewarming podľa bounded inventory.

Hot key môže vyčerpať jeden shard/thread/network path, aj keď celková cache utilization je nízka. Key distribution a request skew musia byť observable.

## 9. Negative caching

Negative cache ukladá `not found`, `rejected` alebo temporary failure result.

Riziká:

- novo vytvorený resource ostane neviditeľný;
- transient authorization failure sa zmení na dlhé deny;
- missing cache key sa zamieňa s authoritative absence;
- broad key neobsahuje tenant alebo generation;
- error response sa cacheuje ako validný business result.

Negative TTL má byť kratší a viazaný na exact error class. `Dependency unavailable` sa nemá cacheovať ako `policy does not exist`.

## 10. Eviction a capacity

Eviction policy rozhoduje, ktoré entries sa odstránia pri memory pressure. Môže používať LRU/LFU approximations, TTL alebo random selection.

Treba sledovať:

- memory used a fragmentation;
- hit/miss ratio po workload cohortoch;
- eviction rate;
- expired versus evicted keys;
- hot-key load;
- fill latency;
- authority fallback load;
- key cardinality a payload size;
- replication/persistence lag.

High hit ratio nie je correctness verdict. Cache môže konzistentne vracať nesprávnu stale value.

## 11. Multi-level caching

Request môže prejsť cez:

```text
browser/private HTTP cache
→ CDN/shared cache
→ API gateway cache
→ service local memory
→ distributed Redis
→ database buffer/query cache/materialized projection
→ authoritative store
```

Každá vrstva má vlastný key, TTL, validator a invalidation. Oprava Redis entry nemusí opraviť CDN alebo process-local cache. Troubleshooting musí inventarizovať všetky cache layers.

## 12. HTTP caching

HTTP cache key typicky vychádza z method a target URI plus request headers uvedených vo `Vary`. Response directives riadia storage a reuse:

- `max-age` a `s-maxage`;
- `no-cache` — uloženie môže byť povolené, ale pred reuse sa vyžaduje validation;
- `no-store` — response sa nemá uložiť;
- `private` — shared cache ju nemá použiť pre iných users;
- `must-revalidate`;
- validators `ETag` a `Last-Modified`.

`Authorization` alebo tenant context mimo cache key môže vytvoriť data leak. Query string, content negotiation a API version musia byť súčasťou identity podľa contractu.

## 13. Cache a transactions

Cache update nie je súčasť database transaction iba preto, že application ho vykoná v rovnakej method.

```text
database commit
→ process crash before cache invalidation
→ stale cache
```

Alebo:

```text
cache update succeeds
→ database rollback
→ cache obsahuje non-authoritative future state
```

Správny model často používa:

- database commit;
- outbox/CDC change event;
- idempotent version-aware cache update/invalidation;
- read fallback na authority;
- lag/freshness monitoring.

## 14. Cache fail-open a fail-closed

Pri cache failure treba definovať business semantics.

### Fail-open

Pokračovať bez cache alebo s bounded stale value. Vhodné pre performance optimization, ak authority zvládne load a stale state je bezpečný.

### Fail-closed

Operation odmietnuť, keď cache nesie security/safety data a authoritative fallback nie je dostupný.

Nesprávne je implicitne zvoliť `default allow`, `operation absent` alebo unlimited traffic len preto, že cache neodpovedá.

## 15. Worked incident `DB-PAY-58`

Settlement v8.2 používal MySQL ako authority pre merchant policy generations a Redis ako cache.

Pôvodný key:

```text
policy:{merchant_id}
```

Cached payload obsahoval:

```text
provider_route
risk_mode
maximum_amount
updated_at
```

Neobsahoval explicitnú `policy_generation`. Update flow:

```text
MySQL transaction commits policy generation 1842
→ outbox publishes MerchantPolicyChanged
→ cache invalidation consumer deletes policy:{merchant_id}
```

Invalidation consumer používal rovnaký unsafe auto-commit pattern ako provider workers. Po OOM/rebalance sa offset pre `MerchantPolicyChanged` commitol pred delete operation.

Dôsledky:

- `1 206` settlements použilo stale policy počas 17 minút;
- `74` operations smerovalo na starý provider route;
- `16` operations prekročilo nový merchant risk limit, ale provider ich pred final effectom odmietol;
- cache hit ratio ostal `97.8 %` a dashboard bol zelený;
- MySQL obsahovala correct policy generation;
- event existoval v brokeri, ale consumer offset bol už za ním;
- Redis entry nemala generation, takže mismatch nebolo možné zistiť lokálne.

Súčasne Redis failover odstránil recent dedupe accelerator keys. Gateway interpretovala cache miss ako `operation absent` a vytvorila redundantné retries, kým PostgreSQL a provider ledger už operation poznali.

### Cache root cause

Primary cache root cause bol **unversioned mutable cache entry, ktorej invalidation bola jediným coherence mechanizmom, pričom invalidation acknowledgement nastalo pred effective delete-om**.

Dedupe root cause bol cache authority inversion: absence evictable Redis keyu bola použitá ako authoritative evidence o neexistujúcej operation.

## 16. Evidence-preserving containment

```text
freeze policy mutations a cache schema changes
→ preserve MySQL generations/binlog positions
→ preserve invalidation events/consumer offsets
→ snapshot Redis keys, TTLs a replication state
→ disable cache-only policy/idempotency decisions
→ route reads to MySQL/PostgreSQL authority
→ identify stale generation cohort
→ reconcile provider attempts a policy used
```

Broad `FLUSHALL` nebol použitý, pretože by vytvoril stampede, odstránil unrelated keys a zničil forensic evidence.

## 17. Authoritative redesign

Versioned policy cache:

```text
policy-current:{merchant_id} → generation 1842
policy:{merchant_id}:1842 → immutable policy body
```

Settlement command persistuje `policy_generation=1842` spolu s operation. Cache fill overuje MySQL generation a používa compare-and-set pointer. Invalidation event je idempotentný a consumer ackne až po effective update/delete.

Read flow:

```text
read current pointer
→ read immutable generation
→ validate payload generation
→ on miss/mismatch read MySQL authority
→ fill only if generation is still current
```

Dedupe flow:

```text
Redis hit
→ fast suppression

Redis miss/error
→ PostgreSQL operation lookup
→ provider idempotency lookup on unknown outcome
→ never infer absence from cache alone
```

Operational controls:

- jittered TTL a single-flight fill;
- per-key hotness metrics;
- invalidation lag a generation mismatch metrics;
- bounded authority fallback load;
- cache schema/version rollout;
- multi-layer cache inventory;
- fail-open/fail-closed decision per data class.

## 18. Cache acceptance verdict

Cache design je prijatý, keď:

- exact cached value, authority a business tolerance sú explicitné;
- cache key obsahuje všetky result-changing dimensions;
- schema a authority generation sú verifiable;
- hit, miss, stale, error a evicted semantics sú odlíšené;
- TTL/freshness/validation zodpovedajú use case-u;
- fill a invalidation races sú version-aware;
- invalidation acknowledgement nastáva po effective mutation;
- cache failure má explicitný safe fallback;
- negative caching neprepisuje transient failure na business absence;
- stampede/hot-key/eviction behavior je bounded;
- multi-level caches majú inventory a coordinated validators;
- cache absence sa nepoužíva ako authority bez contractu;
- mutation, delayed invalidation, failover, eviction a second-read tests prejdú;
- forbidden cross-tenant, stale-policy, duplicate-effect a false-absence outcomes zlyhajú.

## 19. Troubleshooting flow

```text
stale, missing, leaked alebo overload cache outcome
→ exact business value a authority generation
→ cache layer inventory
→ key/variant/schema identity
→ hit/miss/stale/error classification
→ TTL/age/validator
→ fill/invalidation event and acknowledgement
→ eviction/failover/replication state
→ authority fallback and load
→ affected business cohort
→ repair, refill a second-read validation
```

## 20. Anti-patterny

### Cache je source of truth, lebo je rýchla

Authority sa odvodzuje z invariantov a recovery contractu, nie latency.

### TTL vyrieši invalidation

Iba ohraničuje niektoré stale windows a vytvára expiry load.

### Cache miss = neexistuje

Miss môže byť eviction, failure alebo key mismatch.

### Hit ratio je health metric

Môže byť vysoký pri nesprávnych stale values.

### Delete po update je atomic

Database commit a cache delete sú samostatné transitions.

### FLUSHALL opraví cache

Môže zničiť evidence a vytvoriť authority stampede.

### Redis failover nemení correctness

Ak cache získala authority role, jej loss/replication semantics menia business outcome.

### `no-cache` znamená neukladať

V HTTP znamená povinnú validation pred reuse; `no-store` zakazuje storage.

## 21. Kontrolné otázky

1. Čo tvorí exact cache subject?
2. Ako sa cache absence líši od business absence?
3. Ktoré dimensions musia byť v cache key?
4. Ako TTL, freshness a validation súvisia?
5. Ako cache-aside a write-behind menia acknowledgement?
6. Aké races vznikajú pri fill a invalidation?
7. Čo je bounded staleness a read-your-write?
8. Ako sa stampede a hot key diagnostikujú?
9. Aké riziká má negative caching?
10. Prečo unversioned policy cache zlyhala v `DB-PAY-58`?
11. Ako versioned immutable keys zlepšujú coherence?
12. Čo musí overiť cache acceptance verdict?

## Glossary impact

Relevantné pojmy: cache subject, cache authority boundary, cache key, variant dimension, freshness, staleness, validator, cache-aside, read-through, write-through, write-behind, refresh-ahead, invalidation race, versioned cache key, cache stampede, single-flight, hot key, negative caching, cache authority inversion, multi-level cache, bounded stale use a cache acceptance verdict.

## Primárne zdroje

- [RFC 9111 — HTTP Caching](https://www.rfc-editor.org/rfc/rfc9111.html)
- [Redis — Client-side caching](https://redis.io/docs/latest/develop/clients/client-side-caching/)
- [Redis — Key eviction](https://redis.io/docs/latest/develop/reference/eviction/)
- [Redis — Cache](https://redis.io/solutions/caching/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Service discovery a API gateway](service-discovery-and-api-gateway.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
