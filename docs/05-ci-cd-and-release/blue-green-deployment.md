# Blue-green deployment

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

## 1. Definícia

Blue-green deployment udržiava dva oddelené produkčne relevantné deployment targets. Jeden je aktívny a obsluhuje používateľský traffic; druhý obsahuje kandidátsku verziu a pripravuje sa na prevzatie trafficu. Po overení sa routing presunie z aktívneho targetu na kandidátsky.

```text
blue  = active
 green = candidate

prepare green
→ verify green
→ cut over traffic
→ observe
→ keep blue as recovery candidate
→ retire or rotate
```

Farby sú iba labels. Podstatné sú dve oddelené application generations, jednoznačný routing state a explicitná shared-state stratégia.

## 2. Mental model: dvojica targetov a jeden aktívny routing pointer

```text
routing pointer
→ blue alebo green
```

Každý target má vlastnú:

- application capacity,
- artifact a config identity,
- network a service registration,
- telemetry dimensions,
- readiness stav.

Shared dependencies, databáza, queues, caches alebo externé služby môžu zostať spoločné. Preto blue-green oddeľuje application runtime, nie automaticky celý systémový state.

## 3. Hlavný trade-off

Výhody:

- novú verziu možno pripraviť mimo hlavného trafficu,
- cutover môže byť rýchly,
- routing rollback môže byť rýchly,
- application mixed-version okno môže byť krátke.

Cena:

- dočasne takmer dvojnásobná capacity,
- komplikovaná data a worker koordinácia,
- ostrý cutover môže zasiahnuť veľkú časť používateľov,
- starý target sa môže počas rollback window driftovať alebo degradovať.

## 4. Deployment subject a color record

Pre oba targety uchovaj:

```text
color
artifact digest
config revision
infrastructure revision
capacity
readiness
traffic weight
worker/scheduler state
database compatibility phase
```

Deployment record musí obsahovať aj routing revision, cutover timestamp a rollback relation. Mutable tag nestačí na určenie, čo v každej farbe beží.

## 5. Blue-green state machine

```text
active blue / green absent
→ green provisioning
→ green ready, no production traffic
→ pre-cutover verification
→ cutover armed
→ traffic switching
→ green active / blue draining
→ observation
→ release accepted
→ blue retired or retained
```

Alternatívne výsledky:

- cutover aborted,
- routing rollback,
- roll-forward,
- inconclusive validation,
- dual-active degraded state,
- cleanup failure.

## 6. Preconditions

Pred vytvorením kandidáta over:

- immutable release candidate,
- kapacitu a quotas pre druhý target,
- config a secret-reference compatibility,
- databázový expand-contract stav,
- worker a scheduler activation policy,
- routing a rollback control path,
- telemetry podľa farby a digestu,
- previous target health,
- žiadny konfliktujúci deployment.

## 7. Behaviorálna ekvivalencia

Green nemusí byť fyzicky identický s blue, ale musí byť ekvivalentný v oblastiach relevantných pre release:

- rovnaká architecture a runtime class,
- rovnaký network a auth path,
- porovnateľné resource limits,
- rovnaké deployment templates a policies,
- production-relevantné dependencies,
- kompatibilná data schema,
- rovnaké observability contracts.

Testovanie green cez internú skratku, ktorá obchádza DNS, ingress, TLS alebo auth, poskytuje slabší dôkaz než skutočný produkčný path.

## 8. Configuration a secret identity

Green musí byť validovaný s konfiguráciou, ktorú bude používať po cutover-e. Ak sa pri switchi zároveň mení config, pre-cutover test neoveril finálny stav.

Zachovaj:

- rendered config digest,
- secret reference versions,
- feature-flag snapshot alebo policy,
- routing configuration,
- environment-specific identity.

Secret values nekopíruj medzi targetmi ručne; používaj scoped references a short-lived workload identity.

## 9. Capacity model

Typicky:

```text
peak application capacity
≈ blue + green
```

Treba však rátať aj shared limits:

- database connection pools,
- message broker consumers,
- external API quotas,
- licenses,
- load-balancer targets,
- IP addresses,
- storage throughput,
- monitoring cardinality.

Green môže začať menší, ale pred cutoverom musí preukázať schopnosť niesť plánovaný traffic.

## 10. Pre-cutover verification

Pred routing switchom over:

- artifact/config identity,
- startup a functional readiness,
- dependency a identity access,
- critical synthetic journeys,
- authorization a negative paths,
- database migration status,
- capacity a warm-up,
- logs/metrics/traces,
- workers a schedulers,
- data integrity,
- rollback target health.

Výsledok musí byť `ready`, `not ready` alebo `inconclusive`. Chýbajúca telemetry nie je pass.

## 11. Synthetic, replay a shadow traffic

Green možno overiť cez:

- synthetics s dedikovanými identitami,
- interný cohort,
- read-only produkčné requests,
- anonymizovaný replay,
- shadow traffic bez účinku na používateľa.

Pri shadow trafficu:

- zakáž alebo izoluj writes,
- zabráň duplicitným external side effects,
- kontroluj downstream load,
- rediguj citlivé dáta,
- normalizuj nondeterministické response polia.

## 12. Traffic cutover mechanizmy

Možnosti:

- load-balancer target group,
- reverse proxy alebo service mesh route,
- service selector,
- virtual IP,
- platform deployment slot,
- region traffic manager,
- DNS.

L4/L7 routing zvyčajne poskytuje presnejší a rýchlejší cutover než DNS. DNS TTL, resolver cache a persistent connections bránia okamžitému globálnemu switchu.

## 13. Cutover ako transakcia

Cutover má mať explicitný intended state a compare-and-swap ochranu:

```text
expected active = blue
new active = green
routing revision = R42
```

Tým sa zabráni, aby súbežný deployment alebo manuálna zmena prepísala routing nečakane.

Zachovaj pre/post routing snapshot a možnosť idempotentného zopakovania.

## 14. Instant verzus weighted cutover

### Instant

```text
100 % blue → 100 % green
```

Rýchly a jednoduchý, ale prvý produkčný load zasiahne kandidáta naraz.

### Weighted

```text
99/1 → 90/10 → 50/50 → 0/100
```

Znižuje blast radius a približuje stratégiu canary modelu. Potrebuje cohort, metrics a promotion policy.

### Segmentový

Traffic sa presúva podľa regionu, tenanta, ring-u alebo identity. Musí byť reprezentatívny a auditovateľný.

## 15. Connection draining

Po odobratí nového trafficu môže blue stále obsluhovať:

- keep-alive requests,
- WebSockets,
- streams,
- uploads,
- dlhé transactions,
- async work.

Flow:

```text
stop new routing
→ wait propagation
→ drain
→ confirm no critical active work
→ mark standby
```

Cutover completion musí odlišovať new-request switch od úplného ukončenia old connections.

## 16. Database ako shared mutable state

Najčastejší model používa jednu spoločnú databázu. Potom musí platiť:

```text
expand schema
→ green kompatibilný s old aj new state
→ cutover
→ observation
→ blue drain
→ backfill/migrate
→ contract až po skončení rollback window
```

Ak green vykoná nekompatibilné writes, routing rollback na blue nemusí byť bezpečný.

## 17. Oddelené databázy

Separate blue/green databázy vyžadujú riešiť:

- synchronizáciu writes,
- replication lag,
- cutover consistency point,
- identity sequences,
- external consumers,
- rollback nových writes,
- failback.

Je to data migration stratégia, nie iba jednoduché rozšírenie application blue-green.

## 18. Workers, consumers a schedulers

Obe farby nemajú automaticky bezpečne vykonávať mutácie.

Použi podľa systému:

- single active consumer group,
- leader election,
- active-color flag mimo application artifactu,
- oddelené queues,
- idempotency a deduplication,
- samostatný worker rollout,
- external scheduler.

Pred cutoverom presne definuj, kedy green preberá producers, consumers a cron jobs.

## 19. Cache a sessions

Shared cache/session store musí podporovať obe verzie počas prechodu a rollback window.

Riziká:

- serialization incompatibility,
- cache key semantic change,
- session schema drift,
- invalidation storm,
- green warm-up znečistí blue cache.

Použi versioned keys, backward-compatible readers, stateless tokens alebo kontrolované namespace prepnutie.

## 20. Warm-up

Green môže potrebovať:

- JIT alebo model loading,
- cache prewarming,
- connection pools,
- discovery propagation,
- lazy initialization,
- autoscaler stabilization.

Warm-up requesty označ a chráň pred side effects. Readiness bez realistického warm-up loadu môže byť false positive.

## 21. Post-cutover validation

Po switchi vyhodnoť:

- version/color-specific error rate a latency,
- saturation a capacity,
- business success,
- authorization anomalies,
- queue lag a workers,
- cache/session behavior,
- data invariants,
- support/user signal.

Definuj observation window aj delayed signals. Cutover nemusí byť accepted okamžite.

## 22. Routing rollback eligibility

Rýchly routing rollback je bezpečný iba ak:

- blue zostal healthy a warm,
- schema a data sú backward compatible,
- config a flags sú pre blue platné,
- workers/schedulers možno vrátiť,
- connections a routing sa dajú prepnúť,
- green nevytvoril nekompatibilné side effects.

Routing rollback nie je data rollback.

## 23. Standby retention

Po cutover-e možno old target:

- ponechať warm počas rollback window,
- scale-downovať s rýchlou reaktiváciou,
- zachovať iba immutable deklaráciu a artifact,
- odstrániť po prijatí release.

Rollback candidate musí byť počas retention health-checkovaný. Neaktívny target môže stratiť credentials, dependencies alebo capacity.

## 24. Environment drift

Dlhodobo existujúce farby môžu driftovať cez:

- manuálne config zmeny,
- rozdielne patches,
- tajomstvá alebo certifikáty,
- odlišné network rules,
- neaktívne monitoring targets.

Ochrany:

- IaC a immutable infrastructure,
- rovnaký template,
- drift detection,
- pravidelná rotácia farieb,
- zákaz neauditovaných mutations.

## 25. Concurrency a routing lock

Jeden environment môže mať iba jednu autoritatívnu cutover operáciu. Použi routing lock/lease a generation check.

Superseded deployment musí:

- zrušiť pending cutover,
- odstrániť candidate bezpečne,
- zachovať current active state,
- auditovať dôvod.

## 26. Failure taxonomy

- provisioning failure,
- pre-cutover verification failure,
- capacity/warm-up failure,
- routing switch failure,
- partial propagation,
- runtime regression po trafficu,
- shared-state compatibility failure,
- worker/scheduler duplication,
- rollback-ineligible state,
- old-target degradation.

## 27. Observability a evidence

Uchovaj:

- blue/green artifact a config identities,
- readiness a capacity evidence,
- routing revision a weights,
- cutover timeline,
- connection-drain stav,
- version/color SLIs,
- worker/scheduler ownership,
- data migration phase,
- rollback alebo retirement verdict.

## 28. Metriky stratégie

- candidate provisioning time,
- pre-cutover failure rate,
- cutover propagation time,
- old connection drain time,
- routing rollback time a success,
- standby drift rate,
- duplicate-worker incidents,
- capacity overprovisioning cost,
- post-cutover change fail rate,
- rollback-ineligible releases.

## 29. Typické anti-patterny

### Oba targety používajú mutable tag

Color label neidentifikuje konkrétne bytes.

### Green sa overí s inou config než po cutover-e

Evidence sa nevzťahuje na finálny runtime state.

### Routing switch bez concurrency ochrany

Súbežný deployment môže prepísať aktívnu farbu.

### Oba schedulery sú aktívne

Vznikajú duplicate mutations.

### Routing rollback sa zamieňa s data rollbackom

Green writes môžu byť pre blue nečitateľné.

### Old target sa okamžite odstráni

Hlavná recovery výhoda zmizne.

### Farby sa manuálne udržiavajú mesiace

Drift a náklady rastú.

## 30. Diagnostický postup

1. Urči aktívny routing revision a skutočné weights.
2. Over digest/config oboch farieb.
3. Skontroluj propagation, persistent connections a DNS, ak sa používa.
4. Porovnaj color-specific telemetry a requests per target.
5. Over shared database/cache/session compatibility.
6. Skontroluj worker a scheduler ownership.
7. Pri green failure posúď rollback eligibility.
8. Pri blue rollback failure over jeho aktuálnu readiness a dependencies.
9. Po recovery over data/business invariants.
10. Zachovaj cutover timeline a final state.

## 31. Rozhodovací rámec

1. Máme capacity pre dva produkčne relevantné targety?
2. Ktoré dependencies a state zostávajú shared?
3. Ako sa green testuje cez reálny path?
4. Je finálna config známa pred cutoverom?
5. Aký routing mechanizmus a propagation používame?
6. Ako sa koordinujú connections, workers a schedulers?
7. Aké data writes môžu zneplatniť rollback?
8. Ako dlho zostáva old target recovery candidate?
9. Ako sa chráni routing pred súbežnými zmenami?
10. Aké metrics a verdicty rozhodnú acceptance?

## 32. Kontrolný checklist

- oba targety majú immutable identities,
- config a secret references sú známe,
- green je behaviorálne ekvivalentný,
- capacity a shared quotas sú pripravené,
- pre-cutover smoke používa relevantný path,
- routing switch je idempotentný a locked,
- drain a long-lived connections sú riešené,
- DB/cache/session/events sú compatible,
- workers a schedulers majú single ownership,
- telemetry obsahuje color a version,
- rollback eligibility je potvrdená,
- old target sa health-checkuje počas retention,
- teardown je bezpečný a auditovateľný.

## 33. Kontrolné otázky

1. Čo je skutočným predmetom blue-green stratégie?
2. Prečo dve application fleets neznamenajú dva úplne oddelené systémy?
3. Prečo DNS neposkytuje presný okamžitý cutover?
4. Čo musí obsahovať pre-cutover verification?
5. Ako sa chráni routing transition pred race condition?
6. Prečo connection draining pokračuje po switchi nových requests?
7. Ako databáza obmedzuje routing rollback?
8. Ako koordinovať schedulers a workers?
9. Prečo old target potrebuje kontinuálny health check?
10. Ako environment drift znižuje recovery hodnotu?

## Summary

Blue-green deployment pripravuje novú application generation v oddelenom targete a následne mení autoritatívny routing pointer. Poskytuje silnú pre-cutover verification a potenciálne rýchly routing rollback, ale potrebuje takmer dvojnásobnú capacity, presnú configuration identity, riadený cutover, connection drain a koordináciu shared databázy, cache, sessions, workers a schedulers. Najdôležitejšie obmedzenie je, že routing rollback nevracia mutable data state; recovery candidate musí zostať kompatibilný, healthy a auditovateľný.

## Glossary impact

Relevantné pojmy: blue-green deployment, deployment target, active color, candidate color, routing pointer, traffic cutover, routing revision, behavioral equivalence, warm standby, color-specific telemetry, routing rollback a standby retention.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Rolling update](rolling-update.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Canary deployment →](canary-deployment.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
