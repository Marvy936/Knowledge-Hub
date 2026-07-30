# Caching

Cache je odvodená kópia alebo computed representation uložená bližšie k consumerovi, aby znížila latency, load alebo cost. Nie je automaticky source of truth. Correctness závisí od identity cache keyu, authority generation, freshness, invalidation, failover a od toho, či miss alebo stale value smie ovplyvniť business decision.

```text
business read alebo decision input
→ exact cached value a authoritative owner
→ key, variant a schema generation
→ lookup: hit / miss / stale / error
→ freshness validation
→ version-aware fill alebo invalidation
→ eviction, expiry a failover
→ authoritative fallback alebo bounded stale use
→ business outcome a affected cohort
→ mutation, delayed-event, cache-loss a second-read validation
```

High hit ratio môže znamenať, že cache veľmi efektívne vracia nesprávnu value. Latency a correctness preto potrebujú oddelené verdicts.

## 1. Cache subject, authority a miss semantics

Exact cache subject musí pomenovať cached business value, authoritative owner a generation, cache layer/topology, key a variant dimensions, serialization schema, fill pattern, freshness tolerance, invalidation/update mechanism, eviction/capacity, hit/miss/error semantics a fallback.

Atlas policy cache:

```text
value: merchant settlement policy
owner: MySQL immutable policy generation
cache: Redis policy-cache-v3
pointer: policy-current:{merchant_id}
value key: policy:{merchant_id}:{generation}
miss/mismatch: authoritative MySQL lookup
error: never infer default allow
```

Cache miss môže znamenať, že entry nikdy nebola načítaná, expirovala, bola evicted, cache restartla, invalidation ju odstránila, request používa iný key/schema alebo authoritative fact neexistuje. Iba posledná možnosť je business absence. Miss sa nesmie interpretovať ako `operation neexistuje`, `user nemá entitlement` alebo `provider call je safe zopakovať` bez authority read-backu.

Cache môže niesť derived projection, immutable artifact, query result, authorization metadata, rate counter, negative lookup alebo HTTP representation. Každá class potrebuje vlastný stale a failure contract.

## 2. Key, variant a generation identity

Cache key musí obsahovať všetky dimensions, ktoré menia result: resource a tenant, authorization scope, locale/currency, API/schema version, policy/config generation, query parameters, representation format a rollout cohort. Chýbajúca dimension spôsobí stale value alebo cross-tenant leak; unbounded dimensions znižujú hit ratio a zvyšujú cardinality.

Stable identity a mutable state je vhodné oddeliť:

```text
policy-current:merchant-42 → generation 1842
policy:merchant-42:1842 → immutable policy body
```

Writer vytvorí immutable generation a compare-and-setom zmení pointer. Reader validuje, že body nesie rovnakú generation. Old value môže zostať pre bounded historical use; current pointer sa však nesmie spárovať s old body.

Serialization/schema generation patrí do identity rovnako ako business generation. Nový code nesmie interpretovať old bytes podľa nového významu iba preto, že key zostal rovnaký.

HTTP shared cache key typicky zahŕňa method a target URI plus headers určené cez `Vary`. Tenant, authorization alebo content negotiation mimo identity môžu sprístupniť representation nesprávnemu userovi. `private`, `no-store`, validators a freshness directives sú security a correctness controls, nie iba performance hints.

## 3. Freshness, TTL a validation

TTL určuje, dokedy entry zostáva eligible bez explicitného refreshu. Nezaručuje, že entry bude existovať celý interval; eviction alebo restart ju môžu odstrániť skôr. Freshness je business verdict, či value možno použiť pre konkrétnu operation teraz. Validation porovnáva version, ETag alebo generation s authority.

Staleness model môže byť best-effort eventual, bounded, read-your-write, monotonic, version-pinned alebo `no stale policy/authorization decision`. Product catalog môže tolerovať minúty; settlement risk policy môže vyžadovať current generation alebo explicitne persisted generation použitú pri decision-e.

HTTP caching podľa RFC 9111 rozlišuje fresh a stale response a conditional validation. `no-cache` neznamená zákaz storage; vyžaduje validation pred reuse. `no-store` zakazuje uloženie podľa directive semantics. Rovnaký mechanizmus version/validator je užitočný aj v service cache.

Bounded stale use musí mať maximum age, operation classes, fallback a audit evidence. `Serve stale on error` je bezpečné pre niektoré read representations, nie automaticky pre revocation, risk limit alebo idempotency authority.

## 4. Fill, write a invalidation protocol

Cache-aside číta cache, pri miss-e authority a potom fillne value. Read-through presúva fill do cache layeru. Write-through ackne až podľa toho, či authority commitla. Write-behind ackne pred durable authority write-om a tým robí cache súčasťou durability a recovery boundary.

Database commit a cache mutation nie sú jedna transaction:

```text
database commit
→ crash pred invalidation
→ stale cache
```

Opačné poradie môže cacheovať future state, ktorý database rollbackla. Invalidation je preto distributed consistency protocol, nie `DEL` statement.

Typický safe flow:

```text
authority transaction commit
→ outbox/CDC change event
→ idempotent version-aware consumer
→ effective update/delete
→ až potom acknowledgement
→ generation-mismatch monitoring
```

Stale-fill race vznikne, keď reader načíta old DB value, writer commitne new generation a invaliduje cache, no reader následne old value znovu zapíše. Ochrany sú immutable generation keys, compare-and-set pointer, fill iba pri stále current version, second invalidation a bounded TTL.

Acknowledgement invalidation consumeru musí nasledovať po effective cache mutation. Offset posunutý pred `DEL` alebo pointer update vytvára accepted-but-not-applied coherence gap.

## 5. Capacity, stampede a multi-level caches

Expiry populárneho keyu môže spustiť stovky authority reads. Single-flight/coalescing, jittered TTL, probabilistic refresh, bounded stale-while-revalidate a per-key admission chránia origin. Distributed lock potrebuje timeout a fencing; bez nich môže stale refresher prepísať novšiu value.

Hot key môže vyčerpať jeden Redis shard alebo network path pri nízkej total utilization. Sleduje sa key-level request skew, fill latency, eviction/expiry rate, payload size, fallback load a replication/persistence state.

Request môže prejsť browser cache, CDN, gateway cache, local memory, Redis a materialized projection. Každá vrstva má vlastný key, validator a invalidation generation. Oprava Redis entry neopraví automaticky process-local ani CDN cache. Troubleshooting preto začína inventory vrstiev a per-layer age/version evidence.

Negative cache ukladá `not found`, rejection alebo error. Transient dependency failure sa nesmie cacheovať ako permanentná business absence. Negative TTL má byť kratší a key musí obsahovať tenant, authorization a generation. Error class je súčasť value semantics.

## 6. Cache failure a authority fallback

Cache failure môže byť fail-open, fail-closed alebo degraded podľa data classu. Performance cache môže fail-open na authority, ak origin má bounded capacity. Security/safety value môže fail-closed, keď current authority nie je dostupná. Žiadny model nesmie implicitne zvoliť default allow, unlimited traffic alebo operation absence.

Authority fallback potrebuje admission control. Cache outage môže presunúť celý read load do database a vytvoriť stampede. Controlled fallback limituje concurrency, prioritizuje critical operations a prípadne používa bounded stale values pre safe cohorts.

Redis cache failover môže stratiť recent keys podľa replication a persistence semantics. Correct design zmení latency a load, nie business truth. Ak loss keyu zmení payment retry decision, cache získala nebezpečnú authority role.

## 7. Connected incident `DB-PAY-58`

Settlement v8.2 používal MySQL ako authority pre policy generations a Redis key `policy:{merchant_id}` bez explicitnej `policy_generation`. MySQL commitla generation `1842`, outbox publikoval `MerchantPolicyChanged` a invalidation consumer mal key odstrániť.

Consumer však používal rovnaký unsafe auto-commit model ako provider workers. Po OOM/rebalance sa offset posunul pred effective delete. Počas 17 minút `1 206` settlements použilo stale policy, `74` smerovalo na old provider route a `16` prekročilo nový risk limit; provider ich pred final effectom odmietol. Cache hit ratio zostal `97.8 %`, MySQL mala correct generation a broker obsahoval event, ale consumer position už bola za ním.

Redis failover súčasne odstránil recent dedupe accelerator keys. Gateway interpretovala miss ako operation absence a vytvorila redundantné retries, hoci PostgreSQL a provider ledger operation poznali.

Policy root cause bola unversioned mutable entry s invalidation ako jediným coherence mechanizmom a acknowledgement pred effective mutation. Dedupe root cause bola authority inversion: evictable key absence bola použitá ako proof neexistujúcej operation.

## 8. Redesign a acceptance paths

Versioned cache používa immutable body a current pointer. Settlement record persistuje exact policy generation použitú pri decision-e. Fill porovná MySQL generation a pointer mení compare-and-setom. Invalidation consumer ackne až po effective update/delete a mismatch je observable.

```text
read current pointer
→ read immutable generation body
→ validate embedded generation
→ miss/mismatch: read MySQL authority
→ fill iba ak generation stále current
```

Dedupe miss alebo error vždy pokračuje PostgreSQL operation lookupom a pri unknown outcome-e provider lookupom. Redis hit poskytuje fast suppression, no Redis absence nikdy nevytvára nový provider attempt sama.

**Positive path** po policy commite načíta alebo validuje exact new generation a settlement uloží generation used.

**Recovery path** oneskorí invalidation alebo stratí Redis. Reader zistí mismatch/miss, použije bounded authority fallback a nevytvorí stale decision ani duplicate effect.

**Failure path** pri unavailable authority odmietne risk-sensitive operation alebo použije explicitný safe degraded contract; nevráti default allow.

**Forbidden path** odmietne key bez tenant/authorization/generation dimension, hit ratio ako correctness proof, cache miss ako business absence, ack pred mutation, broad `FLUSHALL` a stale fill prepísaný po novšom commite.

Acceptance zahŕňa mutation race, delayed invalidation, eviction, Redis failover, multi-layer stale value, second read a cross-tenant negative test.

## 9. Troubleshooting a anti-patterny

Diagnostika ide od exact value a authority generation cez cache-layer inventory, key/variant/schema, hit/miss/stale/error classification, TTL/validator, fill/invalidation event a acknowledgement, eviction/failover state, authority fallback load a affected business cohort. Repair sa uzatvára second-read a second-mutation testom.

Najčastejšie anti-patterny sú cache označená za authority pre svoju rýchlosť, TTL považované za invalidation, miss považovaný za absence, hit ratio za health verdict, delete po DB update vydávaný za atomic transition, `FLUSHALL` ako repair a `no-cache` zamieňané s `no-store`.

## 10. Kontrolné otázky

1. Čo tvorí exact cache subject?
2. Ako sa cache miss líši od business absence?
3. Ktoré dimensions patria do keyu a variant identity?
4. Ako TTL, freshness a validation súvisia?
5. Prečo database commit a cache invalidation nie sú atomic?
6. Ako versioned immutable keys bránia stale fill race-u?
7. Ako stampede a hot key ovplyvňujú authority?
8. Kedy cache fail-open a kedy fail-closed?
9. Prečo `97.8 %` hit ratio nezabránilo `DB-PAY-58`?
10. Ktoré positive, recovery, failure a forbidden paths musia prejsť?

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

[← Predchádzajúca: Service discovery a API gateway](service-discovery-and-api-gateway.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: CAP theorem →](cap-theorem.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
