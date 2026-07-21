# Blue-green deployment

Blue-green deployment udržiava dve oddelené, produkčne relevantné prostredia alebo fleet-y: aktuálne aktívne prostredie a kandidátske prostredie s novou verziou. Traffic sa po overení presmeruje zo starej farby na novú.

Názvy `blue` a `green` sú iba labels. Dôležitý je model dvoch oddelených deployment targets a riadeného traffic cutoveru.

## 1. Základný mechanizmus

```text
blue  = current production
 green = new candidate
```

Flow:

```text
deploy green
→ verify green bez production trafficu alebo s test trafficom
→ switch routing blue → green
→ observe
→ ponechaj blue ako recovery candidate
→ neskôr retire blue
```

Pri ďalšom release sa roly môžu otočiť.

## 2. Traffic switch

Cutover môže byť realizovaný cez:

- load balancer target groups,
- reverse proxy configuration,
- service selector,
- DNS,
- routing table,
- virtual IP,
- platform deployment slot,
- service mesh route.

Najrýchlejší a najdeterministickejší je typicky L4/L7 routing switch. DNS má cache a TTL propagation, preto nie je okamžitý globálny prepínač.

## 3. Hlavné vlastnosti

Blue-green poskytuje:

- oddelenú prípravu novej verzie,
- rýchly traffic cutover,
- jednoduché vrátenie routingu,
- možnosť smoke a acceptance testov pred release,
- minimálne mixed-version obdobie pri ostrých requestoch,
- jasnú environment-level identity.

Cena je vysoká dočasná resource spotreba a potreba koordinovať shared state.

## 4. Environment parity

Green má byť behaviorálne ekvivalentný blue v relevantných oblastiach:

- compute a architecture,
- network topology,
- identity a permissions,
- configuration,
- dependencies,
- TLS a routing,
- resource limits,
- observability,
- data schema.

Úplná fyzická identita nie je vždy potrebná, ale rozdiely musia byť známe a kontrolované.

## 5. Immutable artifact

Green musí dostať presne identifikovaný artifact digest, ktorý prešiel predchádzajúcimi gates.

Nie:

```text
blue: image:stable
green: image:stable
```

ak `stable` môže ukazovať na rozdielne bytes v čase.

Deployment record má zachytiť:

```text
blue_digest
green_digest
config revisions
routing state
cutover time
```

## 6. Pre-cutover verification

Pred switchom over:

- startup a readiness,
- critical request paths,
- dependency connectivity,
- authorization,
- migrations a schema compatibility,
- logs/metrics/traces,
- background jobs,
- capacity,
- security policy,
- configuration a secrets references.

Test traffic nemá poškodiť production data alebo externé systémy.

## 7. Shadow a synthetic traffic

Green možno overiť pomocou:

- synthetic requests,
- replay anonymizovaného trafficu,
- shadow trafficu bez side effects,
- interných test users,
- read-only production queries.

Shadow response sa typicky nevracia používateľovi. Write operácie musia byť blokované alebo idempotentne izolované.

## 8. Cutover modely

### Instant cutover

```text
100 % blue → 100 % green
```

Jednoduché, ale prvý production traffic zasiahne green naraz.

### Weighted transition

```text
99/1 → 90/10 → 50/50 → 0/100
```

Technicky sa približuje canary deploymentu, ale stále využíva dve celé environment-y.

### Tenant alebo region cutover

Vybrané tenants, regions alebo rings sa presmerujú postupne.

## 9. Connection draining

Pri cutover-e môže blue stále obsluhovať existujúce connections.

Flow:

```text
stop new traffic to blue
→ drain active requests/connections
→ terminate alebo ponechaj warm
```

Osobitne rieš:

- WebSockets,
- streaming,
- long polling,
- large uploads,
- database transactions,
- background workers.

## 10. DNS cutover

DNS-based switch má obmedzenia:

- resolver a client caching,
- TTL,
- stale records,
- connection reuse,
- negatívnu cache,
- rozdielne propagation časy.

DNS môže byť súčasťou regionálneho traffic managementu, ale nie je vhodný na presný sekundový rollback bez ďalšej routing vrstvy.

## 11. Database ako shared state

Najväčší problém blue-green je databáza.

Obe verzie často používajú rovnaký database cluster. Potom musia byť schema a data behavior kompatibilné.

Bezpečný flow:

```text
expand schema
→ deploy green kompatibilne s old/new schema
→ cutover traffic
→ observe
→ drain blue
→ migrate/backfill
→ contract schema neskôr
```

Ak green vykoná nevratné data changes, routing rollback na blue nemusí byť bezpečný.

## 12. Separate databases

Samostatná blue a green databáza komplikuje:

- synchronizáciu writes,
- cutover consistency,
- replication lag,
- identity sequences,
- rollback po nových writes,
- external integrations.

Je vhodná iba s jasnou data migration a ownership stratégiou.

## 13. Background workers

Ak sú blue aj green workers aktívne, môžu:

- spracovať message dvakrát,
- súťažiť o partitions,
- spustiť scheduled job dvakrát,
- používať rozdielnu event semantics.

Možnosti:

- workers aktivovať až pri cutover-e,
- používať leader election,
- oddeliť queue/consumer group,
- zabezpečiť idempotency,
- rolloutovať workers samostatnou stratégiou.

## 14. Cron a scheduled jobs

Pred cutoverom definuj, ktorá farba smie vykonávať scheduled mutations.

Environment label sám nezabráni dvojitému spusteniu.

Použi:

- distributed lock,
- active-color configuration,
- single scheduler,
- external orchestration,
- idempotent job semantics.

## 15. Cache a session state

Shared cache musí byť compatible s oboma verziami.

Riziká:

- serialization changes,
- cache poisoning medzi verziami,
- session schema drift,
- stale data,
- invalidation storm.

Možnosti:

- versioned cache namespace,
- backward-compatible serialization,
- stateless sessions,
- external session store,
- controlled invalidation.

## 16. Capacity

Blue-green typicky potrebuje približne dvojnásobnú application capacity počas prípravy:

```text
peak ≈ blue fleet + green fleet
```

Treba zohľadniť:

- compute,
- memory,
- load-balancer targets,
- IP addresses,
- quotas,
- database connections,
- external API limits,
- licenses.

Green nemusí byť od začiatku na 100 % veľkosti, ale pred cutoverom musí zvládnuť očakávaný traffic.

## 17. Warm-up

Pred trafficom môže green potrebovať:

- cache prewarming,
- JIT compilation,
- connection pool initialization,
- model/data loading,
- service discovery propagation,
- lazy dependency setup.

Warm-up requests musia byť odlíšené od reálneho business trafficu a nesmú vytvárať neželané side effects.

## 18. Rollback routingom

Najväčšia výhoda:

```text
green failure
→ route traffic back to blue
```

Rýchlosť rollbacku však závisí od:

- routing propagation,
- blue readiness,
- connection draining,
- state compatibility,
- data mutations vykonaných green,
- feature flags a configuration.

Blue musí zostať warm a overiteľný dostatočne dlho.

## 19. Retention starej farby

Po úspešnom cutover-e blue možno:

- ponechať warm na krátke rollback window,
- scale-downovať, ale zachovať deklaráciu,
- úplne odstrániť po observation window.

Dlhodobé držanie dvoch plných prostredí zvyšuje náklady a drift.

## 20. Environment drift

Ak blue a green existujú dlhodobo, môžu sa odlišovať manuálnymi zmenami.

Ochrany:

- Infrastructure as Code,
- immutable infrastructure,
- rovnaké deployment templates,
- drift detection,
- pravidelná rotácia farieb,
- zákaz manuálnych mutations.

## 21. Secrets a identity

Green potrebuje production-relevantné permissions, čo rozširuje citlivý footprint.

Použi:

- environment-scoped identity,
- short-lived credentials,
- least privilege,
- oddelené write permissions pred cutoverom,
- audit accessu,
- bezpečnú secret rotation.

## 22. Observability

Metriky musia byť rozlíšiteľné podľa farby a version digestu:

- request rate,
- error rate,
- latency,
- saturation,
- dependency errors,
- business KPIs,
- restarts,
- queue lag,
- cache behavior.

Bez labelov `environment_color` a `version` je cutover diagnostika slabá.

## 23. Cutover checklist

Pred switchom:

1. green artifact digest potvrdený,
2. configuration a migrations overené,
3. capacity pripravená,
4. synthetic/smoke tests úspešné,
5. background jobs koordinované,
6. routing change pripravený,
7. promotion a abort criteria definované,
8. blue dostupný pre rollback,
9. on-call a communication pripravené,
10. dashboards rozlišujú blue/green.

## 24. Výhody

- rýchly traffic cutover,
- rýchly routing rollback,
- testovanie novej verzie v oddelenom targete,
- minimálne application mixed-version obdobie,
- jednoduché porovnanie environmentov,
- nižšie riziko in-place mutation.

## 25. Nevýhody

- približne dvojnásobná capacity,
- shared-state compatibility zostáva,
- zložitá koordinácia workers a scheduled jobs,
- environment drift,
- DNS a connection propagation,
- rollback nemusí vrátiť data state,
- cutover môže zasiahnuť všetkých používateľov naraz.

## 26. Anti-patterny

### Blue a green používajú mutable tag

Nie je isté, ktoré bytes sú v jednotlivých farbách.

### Green sa testuje s inou konfiguráciou než po cutover-e

Pre-release evidence nie je relevantná.

### Oba schedulery vykonávajú mutations

Vznikajú duplicate side effects.

### Routing rollback sa považuje za data rollback

Green writes môžu byť pre blue nekompatibilné.

### Stará farba sa okamžite odstráni

Recovery výhoda zmizne.

### Dve environment-y sa manuálne udržiavajú mesiace

Drift a náklady rastú.

## 27. Troubleshooting

### Green je healthy bez trafficu, po cutover-e zlyháva

Over capacity, cold caches, production-only dependencies, permissions, rate limits a reálny workload mix.

### Časť klientov stále používa blue

Skontroluj DNS cache, persistent connections, service discovery propagation a sticky routing.

### Rollback na blue spôsobuje chyby dát

Green vykonal incompatible writes alebo migration. Použi roll-forward/restore podľa recovery plánu.

### Scheduled job sa spustil dvakrát

Obe farby mali active scheduler. Zaveď leader/lock alebo explicitnú active-color policy.

### Green nemá dostatok capacity

Over quotas, autoscaling warm-up, DB connection limit, IPs, licenses a external dependencies.

### Blue po observation window už nie je ready

Ponechaná farba degradovala alebo stratila dependencies. Rollback candidate musí byť kontinuálne health-checkovaný.

## 28. Kontrolné otázky

1. Ako funguje blue-green deployment?
2. Aký je rozdiel medzi deployment targetom a environment labelom?
3. Prečo DNS nie je okamžitý cutover mechanizmus?
4. Ako sa overuje green pred produkčným trafficom?
5. Prečo shared databáza vyžaduje compatibility?
6. Ako koordinovať background workers a schedulery?
7. Čo musí zostať zachované pre rýchly rollback?
8. Prečo routing rollback nie je data rollback?
9. Ako environment drift oslabuje stratégiu?
10. Ktoré metriky musia byť rozlíšené podľa farby a verzie?

## Glossary impact

Relevantné pojmy: blue-green deployment, blue environment, green environment, traffic cutover, deployment slot, active color, warm standby, routing rollback, environment parity, color-specific telemetry a cutover window.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Rolling update](rolling-update.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Canary deployment →](canary-deployment.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
