# Rolling update

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

## 1. Definícia

Rolling update postupne nahrádza instances starej verzie novou bez vypnutia celej fleet naraz. Počas rollout-u preto existuje mixed-version obdobie, v ktorom staré aj nové instances obsluhujú traffic alebo pracujú nad rovnakým runtime stavom.

```text
O O O O
→ N O O O
→ N N O O
→ N N N O
→ N N N N
```

`O` je old generation a `N` new generation. Stratégia znižuje okamžitý blast radius a môže zachovať dostupnosť, ale jej bezpečnosť závisí od compatibility, capacity, readiness, termination a rollout-control mechanizmov.

## 2. Mental model: kontrolovaná výmena capacity

Rolling update je state machine nad dvoma generáciami a jednou spoločnou službou:

```text
desired fleet
= old available
+ new available
+ temporarily unavailable/pending
```

Controller opakovane:

1. vytvorí alebo aktivuje časť novej capacity,
2. overí readiness,
3. presunie traffic,
4. drainuje a odstráni starú capacity,
5. vyhodnotí, či môže pokračovať.

Názov stratégie v orchestrátore nezaručuje zero downtime. Ak je readiness slabá, surge nemožný alebo fleet príliš malá, rolling update môže spôsobiť výrazný capacity dip.

## 3. Základný predpoklad: mixed-version compatibility

Počas overlapu musia bezpečne koexistovať:

- staré a nové API behavior,
- staré a nové databázové očakávania,
- producers a consumers udalostí,
- cache a session formáty,
- background workers,
- config a feature flags,
- starí a noví clients.

Compatibility nie je iba syntaktická. Nová verzia môže používať rovnakú schema, ale zmeniť význam hodnoty, retry semantics alebo ordering.

Ak sa nedá vytvoriť bezpečné mixed-version okno, použi inú stratégiu alebo viacfázovú migráciu.

## 4. Deployment subject a rollout generation

Každý rollout musí byť viazaný na:

- new artifact digest,
- previous artifact digest,
- config a secret-reference revision,
- deployment generation/revision,
- database a migration state,
- rollout policy version,
- target environment a topology,
- ownera a pipeline run.

Mutable image tag alebo implicitná config zmena môže spôsobiť, že instances jednej „verzie“ nemajú rovnaký obsah.

## 5. Rolling state machine

```text
planned
→ prechecks
→ new batch scheduling
→ new batch starting
→ new batch ready
→ traffic observing
→ old batch draining
→ old batch removed
→ next batch
→ full new generation
→ post-rollout observing
→ completed
```

Alternatívne stavy:

- paused,
- inconclusive,
- progressing too slowly,
- aborting,
- rolling back,
- rolling forward,
- degraded mixed state.

Controller musí vedieť presne oznámiť, koľko old/new/pending/unavailable capacity existuje.

## 6. Batch size

Batch môže byť vyjadrený absolútnym počtom, percentom, zónou alebo ringom.

Menší batch:

- znižuje blast radius,
- zvyšuje počet observation bodov,
- predlžuje rollout,
- udržiava mixed-version stav dlhšie.

Väčší batch:

- skracuje rollout,
- zvyšuje capacity shock,
- znižuje čas na detekciu pred širším dopadom.

Percentá vždy prepočítaj na absolútne čísla. Pri dvoch replikách znamená jedna nedostupná 50 % capacity.

## 7. Maximum unavailable

`max unavailable` určuje, aká časť desired fleet môže byť počas rollout-u nedostupná.

```text
replicas = 10
max unavailable = 2
→ cieľ je zachovať približne aspoň 8 available
```

Skontroluj rounding pravidlá konkrétnej platformy. Pri malej fleet môže percento zaokrúhlené nahor vytvoriť nečakane veľký outage.

Hodnota musí rešpektovať:

- aktuálny utilization headroom,
- failure jednej ďalšej instance,
- disruption budget,
- dependency limits,
- požadované SLO.

## 8. Maximum surge

`max surge` povoľuje dočasnú capacity nad desired count.

```text
replicas = 10
max surge = 2
→ počas rollout-u môže existovať 12 instances
```

Surge potrebuje rezervu v:

- CPU a memory,
- IP addresses a load-balancer targets,
- database connections,
- message partitions alebo licenses,
- external API quotas,
- storage attachments,
- zone capacity.

Surge bez reálnej rezervy vedie k pending instances a stuck rollout-u.

## 9. Capacity model

Bez surge:

```text
stop old
→ capacity klesne
→ start new
```

So surge:

```text
start new
→ wait ready
→ route
→ drain old
→ remove old
```

Zachovanie počtu instances neznamená zachovanie throughputu. Nová verzia môže mať inú resource efficiency, cold cache alebo pomalší startup.

## 10. Prechecks

Pred prvým batchom over:

- artifact a config identity,
- cluster/host capacity pre surge,
- database a event compatibility,
- healthy baseline,
- version-level telemetry,
- rollout a abort policy,
- rollback eligibility,
- autoscaler a disruption-controller interakcie,
- žiadny prebiehajúci incident alebo konfliktujúci deployment.

## 11. Startup, readiness a liveness

Rozlišuj:

- **Startup probe —** aplikácia ešte inicializuje a nemá byť restartovaná pre pomalý štart.
- **Readiness probe —** instance smie prijímať traffic.
- **Liveness probe —** proces je unrecoverably stuck a má byť reštartovaný.

Readiness má overovať relevantný request path, nie iba otvorený TCP port. Príliš slabá readiness rozšíri chybu; príliš prísna readiness môže pri dependency degradácii vyradiť celú fleet.

## 12. Readiness stability

Jednorazový pass nemusí stačiť. Nová instance môže byť krátko ready a následne zlyhať pri warm-up alebo load-e.

Použi podľa rizika:

- minimum ready duration,
- startup smoke,
- initial traffic cap,
- stabilization window,
- consecutive-success requirement,
- dependency a pool health.

## 13. Traffic a load-balancing semantics

Počas rollout-u traffic smeruje na obe generácie. Skontroluj:

- load-balancer health-check lag,
- sticky sessions,
- connection reuse,
- zone-aware routing,
- long-lived connections,
- request hashing,
- per-instance load,
- routing propagation.

Weight podľa počtu instances nemusí znamenať rovnaký podiel requests, najmä pri persistent connections.

## 14. Graceful termination

Bezpečný removal old instance:

```text
mark not ready
→ wait routing propagation
→ stop new work intake
→ drain active work
→ checkpoint/requeue
→ release locks
→ terminate
```

Over WebSockets, streaming, queue acknowledgements, scheduled work, pre-stop hook a termination grace period. Instance ukončená pred routing propagation môže stále dostávať requests.

## 15. Database compatibility

Preferovaný expand-contract flow:

```text
expand schema
→ deploy code kompatibilný so starou aj novou cestou
→ backfill/migrate
→ prepnúť reads/writes
→ odstrániť old generation
→ contract schema neskôr
```

Nedovoľ `DROP`, rename alebo semantic change, ktorú old instances nevedia tolerovať. Migration status musí byť súčasťou rollout evidence.

## 16. Events a queues

Počas overlapu môžu old a new producers/consumers používať rovnaký stream.

Kontroluj:

- backward a forward schema compatibility,
- unknown fields a enum values,
- event ordering,
- duplicate delivery,
- poison-message behavior,
- partition rebalancing,
- idempotency,
- retry/dead-letter semantics.

Nový producer nesmie emitovať contract, ktorý stále aktívny old consumer odmietne alebo zle interpretuje.

## 17. Cache a session compatibility

Riziká:

- nový serialization format,
- rovnaký key s novým významom,
- old version číta new entry,
- session schema drift,
- global invalidation a stampede.

Možnosti:

- versioned namespaces,
- backward-compatible readers,
- dual-read/write,
- stateless tokens,
- krátkodobá affinity iba ako transition pomoc.

Affinity nesmie skrývať nekompatibilitu, ktorú neskôr odhalí reconnect alebo scale event.

## 18. Background jobs a schedulers

Rolling web fleet neznamená bezpečný rolling worker fleet. Rieš:

- single-active schedulers,
- leader election,
- partition ownership,
- job format compatibility,
- in-flight checkpoint,
- old/new worker concurrency,
- idempotency side effects.

Worker rollout môže potrebovať samostatné poradie voči API producerom.

## 19. Topology-aware ordering

Nevymieňaj naraz celú failure domain. Rollout môže postupovať:

- po nodes,
- po availability zones,
- po regions,
- po rings,
- po tenant segments.

Controller musí rešpektovať anti-affinity a disruption budgets. Inak môže plánovaný rollout skombinovaný s náhodným failure odstrániť celú zónovú capacity.

## 20. Observation gate medzi batchmi

Po každom batchi vyhodnoť:

- error-rate delta old verzus new,
- p95/p99 latency,
- saturation a requests per instance,
- restart/probe failures,
- dependency errors,
- queue lag,
- business success,
- security a authorization anomalies.

Výsledky:

- continue,
- pause,
- abort,
- rollback,
- inconclusive pre chýbajúce alebo nedostatočné dáta.

Rolling update bez observation gate iba pomalšie šíri chybu.

## 21. Evidence freshness a comparability

Canary-like porovnanie batchu je platné iba ak:

- old a new traffic sú porovnateľné,
- config a dependencies sú známe,
- metrics obsahujú version digest,
- observation window má dostatok vzoriek,
- autoscaling alebo region incident neskresľuje porovnanie.

## 22. Pause a resume

Pause musí zachovať stabilný mixed state:

- current old/new counts,
- active artifact digests,
- routing a traffic distribution,
- database migration phase,
- pending cleanup,
- reason a owner.

Resume musí znovu overiť freshness preconditions. Po hodinách môže environment alebo policy vyzerať inak než pri pause.

## 23. Autoscaling interaction

Autoscaler môže:

- meniť desired replica count počas rollout-u,
- reagovať na cold-start latency,
- spotrebovať surge rezervu,
- scale-downovať nesprávnu generáciu,
- skresliť per-version metrics.

Definuj ownership desired countu a otestuj rollout pri scale-up aj scale-down udalosti.

## 24. Concurrency a deployment locks

Dva súbežné rollouty do jednej fleet vytvárajú nejasnú generáciu a recovery path. Použi environment lock, generation compare-and-swap alebo deployment queue.

Novší rollout môže starší supersedovať iba po bezpečnom cancel/cleanup a explicitnom state transition.

## 25. Rollback eligibility

Rolling rollback je bezpečný len ak:

- previous artifact je dostupný,
- database/cache/session/events zostali kompatibilné,
- new writes sú čitateľné starou verziou,
- rollout neaktivoval nevratné external side effects,
- traffic a background work možno znovu presunúť.

Orchestrátorová funkcia `undo` neoveruje tieto podmienky.

## 26. Rolling rollback

Rollback sám trvá ďalší rollout:

```text
mixed old/new bad state
→ pause forward rollout
→ introduce previous generation
→ verify
→ replace failed generation batch by batch
```

Počas rollbacku môže existovať až trojica relevantných stavov: pôvodná verzia, chybná nová verzia a opravená/rollback generation. Udržiavaj presnú identity.

## 27. Roll-forward

Roll-forward je vhodný pri nevratných state changes. Najprv rozhodni, či:

- pause-ni chybnú expozíciu,
- scale-down-ni new generation,
- vypni feature flag,
- zastav producers/consumers,
- nasadíš fix ako novú immutable generation.

## 28. Progress deadline a timeouts

Namiesto jedného veľkého timeoutu meraj:

- scheduling,
- image/artifact pull,
- startup,
- readiness,
- minimum-ready duration,
- traffic observation,
- drain,
- batch progress.

Progress deadline má viesť k pause/abort rozhodnutiu a diagnostickým artifacts, nie iba k označeniu `failed`.

## 29. Failure taxonomy

- scheduling/capacity failure,
- startup failure,
- readiness instability,
- traffic/runtime regression,
- drain/termination failure,
- compatibility failure,
- observation-system failure,
- rollout-controller failure,
- rollback-ineligible state.

Každá trieda potrebuje iný recovery postup.

## 30. Observability a deployment record

Zachovaj:

- deployment generation a policy,
- old/new digests a counts v čase,
- max unavailable/surge,
- batch transitions,
- scheduling/probe events,
- traffic distribution,
- version-level SLIs,
- pause/abort/rollback decisions,
- migration a config state.

## 31. Metriky stratégie

Sleduj:

- rollout duration a p95,
- batch observation time,
- stuck rollout rate,
- capacity dip,
- pending/scheduling failures,
- readiness false-positive incidents,
- drain timeout rate,
- rollback duration a success,
- mixed-version compatibility incidents,
- change exposure before detection.

## 32. Typické anti-patterny

### Readiness je iba otvorený port

Instance sa zaradí do trafficu pred funkčnou pripravenosťou.

### `maxUnavailable` hodnotený iba percentom

Pri malej fleet vznikne nečakaný absolútny outage.

### Surge bez rezervy

Nové instances zostanú pending a rollout sa nepohne.

### Nekompatibilná migration na začiatku

Old generation okamžite zlyhá.

### Žiadna version-level telemetry

Nie je možné odlíšiť regresiu od globálneho incidentu.

### Automatické pokračovanie pri missing metrics

Absencia dôkazu sa zmení na false promotion.

### Súbežné rollouty

Generácie, cleanup a rollback relation sú nejednoznačné.

## 33. Diagnostický postup

1. Urči rollout generation a aktuálne old/new/pending counts.
2. Over artifact/config identity každej generácie.
3. Skontroluj scheduling, quotas a surge rezervu.
4. Rozlíš startup, readiness a liveness failures.
5. Over skutočný traffic a requests per version.
6. Skontroluj database/event/cache compatibility.
7. Pri old termination probléme analyzuj routing propagation a active work.
8. Pri pause over evidence freshness pred resume.
9. Posúď rollback eligibility podľa mutable state.
10. Po recovery over business a data invariants.

## 34. Rozhodovací rámec

1. Môžu old a new verzie bezpečne koexistovať?
2. Aká absolútna capacity strata je prijateľná?
3. Aký surge je reálne schedulovateľný?
4. Čo presne znamená readiness?
5. Ako sa drainujú requests, connections a consumers?
6. Aké compatibility windows potrebujú DB, events, cache a sessions?
7. Aké topology ordering znižuje failure-domain risk?
8. Ktoré metrics rozhodujú medzi continue/pause/abort?
9. Čo sa stane pri missing telemetry?
10. Ako autoscaler interaguje s rolloutom?
11. Je rollback kompatibilný s aktuálnym stavom?
12. Aký record umožní reprodukciu rollout-u?

## 35. Kontrolný checklist

- artifact a config identities sú immutable,
- mixed-version compatibility je otestovaná,
- max unavailable/surge sú posúdené absolútne,
- surge capacity a quotas existujú,
- startup/readiness/liveness sú oddelené,
- graceful drain je overený,
- DB/event/cache/session migration je viacfázová,
- telemetry obsahuje version labels,
- batch observation a inconclusive stav sú definované,
- deployment lock zabraňuje súbehu,
- autoscaler interakcia je známa,
- rollback eligibility je vyhodnotená,
- progress timeouty publikujú evidence.

## 36. Kontrolné otázky

1. Prečo rolling update vytvára mixed-version obdobie?
2. Aký je rozdiel medzi `max unavailable` a `max surge`?
3. Prečo počet ready instances nemusí znamenať zachovaný throughput?
4. Ako sa odlišujú startup, readiness a liveness probes?
5. Prečo je minimum-ready duration užitočná?
6. Ako expand-contract chráni old generation?
7. Aké problémy vznikajú pri eventoch, cache a sessions?
8. Ako topology-aware rollout znižuje riziko?
9. Prečo pause potrebuje freshness recheck?
10. Prečo orchestrátorové undo nedokazuje bezpečný rollback?

## Summary

Rolling update je kontrolovaná výmena capacity, počas ktorej stará a nová generácia zdieľajú traffic a mutable state. Zachovanie dostupnosti závisí od reálnej surge capacity, absolútne posúdeného `max unavailable`, funkčnej readiness, graceful termination a mixed-version compatibility databázy, eventov, cache a sessions. Bez version-level telemetry a observation gate stratégia iba spomaľuje úplné rozšírenie chyby. Rollback je ďalší rollout a je možný len vtedy, keď ho dovoľuje aktuálny stav systému.

## Glossary impact

Relevantné pojmy: rolling update, rollout generation, mixed-version compatibility, maximum unavailable, maximum surge, minimum ready duration, topology-aware rollout, progress deadline, version-level telemetry, rolling rollback a capacity dip.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Recreate deployment](recreate-deployment.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Blue-green deployment →](blue-green-deployment.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
