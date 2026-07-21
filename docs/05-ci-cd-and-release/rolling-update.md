# Rolling update

Rolling update postupne nahrádza instances starej verzie novou verziou bez vypnutia celej fleet naraz. Cieľom je zachovať dostupnosť a obmedziť blast radius, pričom počas rollout-u typicky koexistujú stará a nová verzia.

Je to bežná deployment stratégia pre stateless alebo horizontálne škálované služby, ale vyžaduje mixed-version compatibility, správne readiness a termination správanie a kontrolu rollout tempa.

## 1. Základný mechanizmus

Príklad fleet so štyrmi instances:

```text
krok 0: O O O O
krok 1: N O O O
krok 2: N N O O
krok 3: N N N O
krok 4: N N N N
```

`O` je old version, `N` je new version.

Traffic sa počas rollout-u rozdeľuje medzi obe verzie.

## 2. Hlavný predpoklad: kompatibilita

Počas rolling update musia bezpečne koexistovať:

- old a new application instances,
- old a new API behavior,
- old a new event consumers,
- old a new cache formats,
- old a new database expectations,
- old a new clients.

Ak verzie nemôžu súčasne pracovať nad rovnakým runtime stavom, rolling update nie je bezpečný bez dodatočnej migration stratégie.

## 3. Batch size

Rollout môže nahrádzať:

- jednu instance naraz,
- fixný počet,
- percento fleet,
- jednu availability zone alebo ring naraz.

Menší batch:

- znižuje blast radius,
- zvyšuje čas rollout-u,
- poskytuje viac observation bodov.

Väčší batch:

- zrýchľuje rollout,
- zvyšuje capacity fluctuation a blast radius.

## 4. Maximum unavailable

`max unavailable` určuje, koľko požadovanej capacity môže byť počas rollout-u nedostupnej.

Príklad:

```text
replicas = 10
max unavailable = 2
```

Orchestrátor má zachovať aspoň približne osem dostupných instances, podľa konkrétnej implementácie a rounding pravidiel.

Nesprávne nastavenie môže pri malej fleet vytvoriť väčší výpadok, než sa očakávalo.

## 5. Maximum surge

`max surge` určuje, koľko dočasnej capacity nad desired count možno vytvoriť.

Príklad:

```text
replicas = 10
max surge = 2
```

Počas rollout-u môže existovať až 12 instances.

Surge zrýchľuje rollout a zachováva capacity, ale potrebuje:

- compute resources,
- IP addresses,
- load-balancer targets,
- database connections,
- quota,
- license capacity.

## 6. Capacity model

Bez surge:

```text
stop old
→ start new
```

môže dočasne znížiť capacity.

So surge:

```text
start new
→ wait ready
→ route traffic
→ drain old
→ stop old
```

zachováva dostupnosť lepšie, ale zvyšuje peak resource usage.

## 7. Readiness gate

Nová instance sa nesmie považovať za dostupnú len preto, že proces beží.

Readiness má overiť:

- configuration načítanie,
- dependency connectivity,
- required migrations alebo schema compatibility,
- schopnosť obslúžiť kritický request,
- cache/index initialization,
- service discovery registration.

Príliš slabá readiness zrýchli šírenie chybnej verzie.

## 8. Startup a liveness probes

Rozlišuj:

- startup probe — aplikácia ešte inicializuje,
- readiness probe — môže prijímať traffic,
- liveness probe — proces je v recoverable stave.

Liveness nesmie zabíjať pomaly štartujúcu aplikáciu skôr, než dokončí startup.

## 9. Graceful termination

Pri odstraňovaní old instance:

```text
mark not ready
→ remove from routing
→ wait for propagation
→ drain active work
→ terminate
```

Over:

- keep-alive connections,
- WebSockets,
- long requests,
- streaming,
- queue consumers,
- background jobs,
- shutdown hooks,
- termination grace period.

## 10. Load balancing

Load balancer môže počas rollout-u posielať traffic starej aj novej verzii.

Riziká:

- sticky sessions,
- nerovnomerné connection distribution,
- long-lived connections ostávajúce na old version,
- health-check lag,
- topology imbalance,
- version-dependent cache.

Version-level telemetry je potrebná na porovnanie správania.

## 11. Database compatibility

Bezpečný model:

```text
1. expand schema kompatibilne
2. deploy new application, ktorá podporuje old aj new schema
3. migrate/backfill data
4. over usage novej cesty
5. odstráň old instances
6. contract schema neskôr
```

Nekompatibilné `DROP COLUMN` pred dokončením rollout-u môže okamžite zlomiť old version.

## 12. Event a queue compatibility

Počas rollout-u môžu old a new consumers spracúvať rovnakú queue.

Over:

- backward/forward schema compatibility,
- unknown fields,
- event versioning,
- idempotency,
- ordering,
- poison-message handling,
- re-delivery,
- partition ownership.

Nový producer nesmie publikovať event, ktorý old consumers nevedia bezpečne spracovať, kým ešte existujú.

## 13. Cache compatibility

Riziká:

- zmena serialization formátu,
- zmena key namespace,
- nový meaning existujúcej hodnoty,
- old version číta new cache entry,
- cache stampede po invalidation.

Použi versioned keys alebo dual-read/write podľa potreby.

## 14. Session compatibility

Ak session obsahuje version-specific state, request prechádzajúci medzi old/new instances môže zlyhať.

Preferuj:

- backward-compatible session schema,
- stateless tokens,
- external versioned session store,
- krátkodobú affinity iba ako transition mechanizmus.

## 15. Rollout ordering

Deployment môže postupovať:

- náhodne,
- po nodes,
- po zones,
- po regions,
- podľa rings,
- podľa tenantov.

Topology-aware rollout zabraňuje, aby bola naraz zasiahnutá celá failure domain.

## 16. Observation window

Po každom batchi môže pipeline čakať a vyhodnotiť:

- error rate,
- latency,
- saturation,
- restart rate,
- business KPIs,
- logs/traces,
- version-specific failures.

Rolling update bez observation gates iba spomaľuje úplné rozšírenie chyby; nemusí ju zastaviť.

## 17. Pause a resume

Orchestrátor alebo deployment controller má podporovať:

- pause,
- resume,
- abort,
- rollback,
- scale adjustment,
- manual investigation.

Pause musí zachovať jasný stav, koľko old/new capacity je aktívnej.

## 18. Rollback

Rolling rollback postupne vracia previous artifact.

Riziká:

- databázová nekompatibilita,
- new-version side effects,
- zmenený event stream,
- cache/session schema,
- rollout už dosiahol všetkých používateľov.

Rollback nie je automaticky bezpečný len preto, že orchestrátor ho podporuje.

## 19. Roll-forward

Pri state changes je často bezpečnejšie vytvoriť opravený artifact a pokračovať rolling update.

Potrebné je:

- rýchly build/test path,
- explicitná version identity,
- zachovanie mixed-version compatibility,
- rozhodnutie, či najprv zastaviť chybný rollout.

## 20. Autoscaling interaction

Autoscaler môže rollout skomplikovať:

- meniť desired replica count,
- reagovať na cold-start latency,
- scale-downovať old/new instances nerovnomerne,
- spotrebovať surge capacity.

Deployment controller a autoscaler musia mať kompatibilné pravidlá.

## 21. Resource constraints

Rollout môže uviaznuť, ak new instances nemožno naplánovať pre:

- CPU/memory shortage,
- anti-affinity,
- quota,
- unavailable storage,
- port conflicts,
- IP exhaustion,
- zone constraints.

Surge strategy musí byť testovaná proti reálnej cluster capacity.

## 22. Minimum fleet size

Rolling update nad jednou instance bez surge typicky spôsobí downtime.

Aj pri dvoch instances môže jedna nedostupná znamenať 50 % capacity loss.

Strategy parametre treba posudzovať v absolútnych počtoch, nie iba percentách.

## 23. Deployment timeout

Timeout má rozlíšiť:

- image pull,
- scheduling,
- startup,
- readiness,
- drain,
- rollout progress.

Jedno veľké timeout číslo komplikuje diagnostiku.

## 24. Monitoring rollout-u

Sleduj:

- old/new replica count,
- available/unavailable replicas,
- rollout progress time,
- scheduling failures,
- probe failures,
- version-level error rate a latency,
- restarts,
- drain duration,
- active long-lived connections,
- capacity a saturation.

## 25. Výhody

- typicky bez úplného downtime,
- postupný replacement,
- nižšia peak capacity než blue-green,
- obmedziteľný batch blast radius,
- prirodzený model pre veľké stateless fleets,
- možnosť pause a rollback.

## 26. Nevýhody

- mixed-version complexity,
- pomalší rollout,
- zložitejšia diagnostika,
- potreba compatibility disciplíny,
- stará a nová verzia zdieľajú runtime state,
- rollback môže trvať ďalší celý rollout.

## 27. Anti-patterny

### Readiness = TCP port open

Aplikácia nemusí byť funkčne pripravená.

### `maxUnavailable: 100%`

Rolling update sa prakticky mení na recreate.

### Nekompatibilná migration v prvom kroku

Old instances okamžite zlyhajú.

### Žiadna version-level telemetry

Nie je možné porovnať old a new behavior.

### Automatický pokračujúci rollout po alertoch

Chyba sa postupne rozšíri na celú fleet.

### Surge bez resource rezervy

New instances zostanú pending a rollout uviazne.

## 28. Troubleshooting

### Rollout je stuck

Over scheduling events, resource quota, readiness failures, deployment timeout a old instances čakajúce na drain.

### New instances sú ready, ale error rate rastie

Readiness je príliš slabá alebo problém vzniká iba pri reálnom trafficu. Použi version labels a traces.

### Old instances sa neukončujú

Skontroluj long-lived connections, shutdown hook, grace period, pre-stop delay a routing propagation.

### Capacity počas rollout-u klesá

Over max unavailable, max surge, startup duration, autoscaling a load-balancer health-check lag.

### Rollback zlyháva na databáze

New rollout vykonal nekompatibilnú schema/data zmenu. Zastav automatický rollback a použi pripravený roll-forward alebo restore plan.

## 29. Kontrolné otázky

1. Ako funguje rolling update?
2. Prečo vzniká mixed-version obdobie?
3. Aký je rozdiel medzi max unavailable a max surge?
4. Čo musí overovať readiness?
5. Ako graceful termination chráni active requests?
6. Prečo je expand-contract kritický?
7. Aké event a cache compatibility problémy môžu vzniknúť?
8. Ako topology-aware rollout obmedzuje failure domain?
9. Prečo rolling rollback nemusí byť bezpečný?
10. Ktoré signály určujú pause alebo abort?

## Glossary impact

Relevantné pojmy: rolling update, mixed-version deployment, maximum unavailable, maximum surge, rollout batch, rollout pause, topology-aware rollout, startup probe, readiness probe, liveness probe, version-level telemetry a rolling rollback.
