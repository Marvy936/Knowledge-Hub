# Recreate deployment

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

## 1. Definícia

Recreate deployment nahradí starú runtime verziu novou tak, že stará application capacity sa odstráni pred tým, než je nová verzia pripravená prijímať produkčný traffic. Stratégia preto vytvára plánovaný capacity gap a zvyčajne aj downtime.

```text
old active
→ traffic stop alebo maintenance mode
→ drain a shutdown old
→ migration/deployment
→ start a verify new
→ traffic restore
```

Je to jednoduchá a často úplne legitímna stratégia. Bezpečná je však iba vtedy, keď organizácia vedome akceptuje outage, pozná jeho hornú hranicu a má overený recovery postup.

## 2. Mental model: exkluzívny runtime slot

Recreate používa jeden logický runtime slot:

```text
slot = old
→ empty/maintenance
→ new
```

V jednom okamihu má byť aktívny iba jeden application generation. Tým sa odstraňuje mixed-version problém, ale zároveň mizne produkčná fallback capacity.

Hlavný trade-off:

```text
nižšia orchestration a compatibility zložitosť
za cenu downtime, cutover blast radiusu a pomalšieho rollbacku
```

## 3. Kedy je stratégia vhodná

Recreate je racionálna, keď:

- **Downtime je explicitne prijateľný —** interný systém, maintenance window alebo služba s dohodnutým outage budgetom.
- **Workload je single-instance alebo exkluzívne stateful —** dve súbežné generácie by vytvorili split-brain, lock alebo licensing problém.
- **Verzie nemôžu bezpečne koexistovať —** protocol, local state alebo schema vyžaduje ostrý cutover.
- **Peak capacity je obmedzená —** organizácia nemôže držať surge alebo druhé prostredie.
- **Jednoduchší recovery model je hodnotnejší —** sekvencia je ľahšie auditovateľná a testovateľná než komplexný partial rollout.

Nie je vhodná tam, kde business požaduje kontinuálnu dostupnosť, startup je nepredvídateľný alebo neexistuje bezpečný maintenance režim.

## 4. Deployment subject a preconditions

Pred zásahom musí byť jednoznačné:

- artifact digest a release ID,
- config revision a secret references,
- infrastructure a database state,
- previous rollback candidate,
- deployment owner a target environment,
- maintenance a communication plan,
- maximálny downtime,
- abort decision deadline.

Preconditions:

- starý artifact a config sú stále dostupné,
- backup alebo recovery mechanizmus je použiteľný,
- migration plan bol testovaný na reprezentatívnom stave,
- maintenance response je dostupná mimo nasadzovanej aplikácie,
- observability a synthetics fungujú,
- dependencies a quotas sú zdravé,
- neprebieha konfliktujúca mutácia environmentu.

## 5. Downtime contract

Downtime nie je iba čas štartu procesu:

```text
total outage
= traffic withdrawal propagation
+ drain
+ shutdown
+ migration
+ artifact transfer
+ startup
+ readiness
+ smoke validation
+ routing restoration
```

Definuj pre každú fázu:

- očakávaný čas,
- hard timeout,
- ownera,
- failure action,
- dôkaz začiatku a konca.

Bez rozkladu nemožno zistiť, prečo maintenance window prekročilo plán.

## 6. Recreate state machine

Odporúčaný lifecycle:

```text
planned
→ prechecks passed
→ maintenance enabled
→ writes/work intake stopped
→ old draining
→ old stopped
→ migration/deploying
→ new starting
→ new verifying
→ traffic restoring
→ observing
→ completed
```

Alternatívne konce:

```text
aborted before shutdown
rollback in progress
roll-forward in progress
recovery failed
```

Každý transition musí byť idempotentný alebo musí rozpoznať už vykonaný stav.

## 7. Maintenance mode

Maintenance mode má znížiť používateľský dopad a chrániť konzistenciu:

- vracia kontrolovaný status a retry guidance,
- môže povoliť read-only operácie,
- blokuje nové writes a background work,
- poskytuje status page alebo maintenance page,
- chráni systém pred connection stormom počas štartu.

Musí byť nezávislý od služby, ktorú vypínaš. Maintenance stránka hostovaná tou istou aplikáciou zmizne spolu s ňou.

## 8. Traffic withdrawal a graceful drain

Bezpečný shutdown:

```text
mark unavailable for new traffic
→ wait for routing propagation
→ drain requests/connections
→ stop consumers a schedulers
→ checkpoint work
→ release locks
→ flush telemetry
→ terminate
```

Osobitne rieš:

- keep-alive a HTTP/2 connections,
- WebSockets a streaming,
- dlhé requests a uploads,
- queue acknowledgements,
- distributed locks,
- leader leases,
- cron alebo schedulers,
- in-memory sessions.

Hard kill po grace timeout-e musí zanechať dôkaz o nedokončenej práci.

## 9. Write freeze a background work

Application traffic nemusí byť jediný zdroj writes. Pred migration alebo shutdownom zastav:

- scheduled jobs,
- queue consumers,
- webhook workers,
- batch a reconciliation jobs,
- externé producers, ak to kontrakt vyžaduje,
- administratívne mutácie.

Potvrď, že work intake je skutočne nulový alebo bounded. Inak môže migration prebiehať proti meniacej sa databáze.

## 10. Databázové migrácie

Recreate odstraňuje mixed-version application window, ale nie riziko dátovej zmeny.

Kontroluj:

- lock duration a blocking,
- migration runtime pri reálnom objeme,
- disk a log growth,
- partial execution,
- retry/idempotency,
- checksum alebo post-migration invariants,
- rollback alebo roll-forward semantiku,
- backup restore čas.

Nekompatibilná offline migration môže byť prijateľná, ale iba s explicitným outage a recovery kontraktom. Pri veľkých dátach môže byť expand-contract stále bezpečnejší.

## 11. Stateful workloads

Pri stateful službe over:

- persistent volume attachment a ownership,
- fencing pred novým leaderom,
- WAL alebo journal recovery,
- unclean shutdown behavior,
- hostname/identity assumptions,
- lock a lease expiráciu,
- data integrity po reštarte,
- backup a restore.

Recreate môže znižovať split-brain riziko, ale iba ak je potvrdené, že stará generácia už nemôže zapisovať.

## 12. Artifact a configuration deployment

Nasadzuj immutable artifact identifikovaný digestom. Config musí byť validovaná proti novej verzii pred odstránením starej capacity, ak je to možné.

Zachovaj:

- artifact digest,
- config revision,
- migration bundle version,
- deployment tool revision,
- runtime image a platform identity,
- effective rendered configuration bez secret values.

Mutable tag alebo runtime download nepinovaných dependencies predlžuje outage a ničí reprodukovateľnosť.

## 13. Startup a readiness

Process start nie je readiness. Nová verzia môže potrebovať:

- načítať config a secrets,
- overiť schema compatibility,
- pripojiť dependencies,
- obnoviť local state,
- zahriať JIT, cache alebo model,
- zaregistrovať sa v discovery,
- dokončiť startup probes.

Readiness má overiť schopnosť vykonať kritickú operáciu. Pri read/write službe nestačí iba read-only health endpoint.

## 14. Pre-traffic validation

Pred obnovením trafficu vykonaj:

- artifact a version verification,
- startup/readiness checks,
- dependency connectivity,
- authorization a secret access,
- migration status,
- kritický synthetic smoke,
- queue a scheduler ownership,
- telemetry a alert readiness,
- data invariants.

Failure v tejto fáze má viesť k explicitnému rozhodnutiu rollback verzus roll-forward, nie k nekonečnému čakaniu.

## 15. Traffic restoration

Traffic neobnovuj nutne naraz. Aj recreate môže použiť riadené otvorenie:

```text
maintenance
→ interné synthetics
→ obmedzený request rate
→ 25 % ingress capacity
→ 100 %
```

Ochrany:

- rate limiting,
- connection admission,
- retry jitter,
- cache prewarming,
- dependency pool limity,
- queue rate control.

Tým sa znižuje thundering herd po outage.

## 16. Post-deploy validation

Po obnovení sleduj:

- request success a tail latency,
- business completion,
- authentication/session errors,
- dependency connections,
- queue backlog a drain,
- resource saturation,
- data integrity,
- new-version logs a traces,
- support alebo user signal.

Deployment nie je completed pri prvom zelenom health checku. Potrebuje definovanú observation window.

## 17. Rollback eligibility

Rollback je možný iba ak:

- previous artifact a config existujú,
- stará verzia rozumie aktuálnej schema a dátam,
- nové writes neporušili staré invariants,
- external contracts zostali kompatibilné,
- queue/events možno bezpečne spracovať,
- storage a session format sú kompatibilné.

Routing ani binary rollback nevracia automaticky data state.

## 18. Rollback workflow

```text
re-enable maintenance
→ stop new writes/work
→ drain a stop failed new version
→ restore/adjust compatible state
→ deploy previous immutable artifact
→ verify readiness a data invariants
→ restore traffic
→ observe
```

Stanov decision deadline. Príliš dlhé hľadanie chyby počas nulovej capacity môže byť horšie než skorý rollback.

## 19. Roll-forward

Roll-forward je vhodnejší, keď:

- migration je nevratná,
- nová verzia už vytvorila external side effects,
- starý artifact nevie čítať nový state,
- oprava je malá a rýchlo overiteľná,
- restore by prekročil RTO.

Hotfix musí stále prejsť immutable buildom, minimálnymi gates a audit trailom.

## 20. Failure taxonomy

Rozlišuj:

- **Precheck failure —** deployment sa ešte nemá začať.
- **Drain failure —** stará práca sa nevie bezpečne ukončiť.
- **Migration failure —** data state môže byť partial.
- **Artifact/startup failure —** nová verzia sa nespustí.
- **Readiness failure —** proces beží, ale služba nie je použiteľná.
- **Traffic restoration failure —** routing, TLS alebo discovery nefunguje.
- **Post-release regression —** problém sa prejaví až pri reálnom workloade.
- **Recovery failure —** rollback alebo roll-forward neobnoví službu.

Každá trieda potrebuje inú reakciu a artifacts.

## 21. Capacity a dependency shock

Peak application capacity môže byť nízka, ale po štarte vzniká náraz na shared dependencies:

- všetky connection pools sa otvoria naraz,
- cache je cold,
- clients retryujú,
- queues začnú rýchlo drainovať,
- autoscaler reaguje oneskorene,
- externé API dostane burst.

Recreate capacity model preto zahŕňa aj downstream limits, nie iba počet instances.

## 22. Observability a evidence

Zachovaj timeline:

- maintenance enabled,
- traffic withdrawn,
- last old request/work item,
- old termination,
- migration start/end,
- artifact pull/start,
- readiness pass,
- traffic restoration,
- business recovery,
- final verdict.

Evidence musí byť viazaná na release ID, artifact digest a environment.

## 23. Metriky stratégie

Sleduj:

- planned verzus actual downtime,
- čas každej state-machine fázy,
- drain timeout rate,
- migration failure rate,
- startup/readiness p95,
- rollback decision time,
- rollback/roll-forward success,
- post-restore thundering-herd incidenty,
- maintenance-window overrun,
- user-visible error a lost-work count.

## 24. Typické anti-patterny

### Recreate prezentovaný ako zero downtime

Ak stará capacity zmizne pred novou readiness, outage existuje.

### Maintenance mode bez write freeze

Používateľské requests sú blokované, ale consumers alebo cron stále menia dáta.

### Process kill bez drainu

Prerušia sa requests, transactions a queue work.

### Migration bez partial-failure plánu

Po chybe nie je jasné, či opakovať, obnoviť alebo pokračovať.

### Traffic pri process start

Aplikácia ešte nemusí byť pripravená ani zahrievaná.

### Rollback podľa verzie, nie podľa eligibility

Starý artifact môže byť dostupný, ale nekompatibilný s novými dátami.

### Maintenance komponent v rovnakom failure domaine

Status stránka alebo control endpoint zmizne spolu s aplikáciou.

## 25. Diagnostický postup

1. Urči aktuálny state machine stav.
2. Over artifact, config, migration a environment identity.
3. Rozlož elapsed time podľa fáz.
4. Skontroluj routing a skutočný traffic withdrawal.
5. Over aktívne requests, consumers, locks a sessions.
6. Pri migration failure urč partial state a posledný úspešný krok.
7. Pri readiness failure porovnaj process health s critical-path smoke.
8. Pri post-start regresii skontroluj cold state, dependency burst a retry amplification.
9. Posúď rollback eligibility, nie iba technickú dostupnosť starej verzie.
10. Po recovery over business a data invariants.

## 26. Rozhodovací rámec

1. Aký downtime je businessovo prijateľný?
2. Aká je horná hranica každej fázy?
3. Prečo verzie nemôžu alebo nemusia koexistovať?
4. Ktoré writes a background work treba zastaviť?
5. Aký je migration a data-recovery kontrakt?
6. Ako sa preukáže úplné vypnutie starej generácie?
7. Čo tvorí funkčnú readiness?
8. Ako sa traffic obnoví bez thundering herd?
9. Kedy je rollback kompatibilný?
10. Aký je roll-forward path?
11. Ktorý nezávislý control path zapne maintenance alebo recovery?
12. Aké evidence zostane po deploymente?

## 27. Kontrolný checklist

- release identity je immutable,
- downtime budget je schválený,
- maintenance komponent je nezávislý,
- traffic a work intake možno zastaviť,
- graceful drain je otestovaný,
- backup/restore a migration boli overené,
- previous artifact a config sú dostupné,
- startup/readiness majú samostatné timeouty,
- smoke overuje kritický outcome,
- traffic restoration je rate-controlled,
- rollback eligibility je vyhodnotená,
- data invariants sa overia po recovery,
- timeline a artifacts sa uchovajú.

## 28. Kontrolné otázky

1. Aký je základný trade-off recreate deploymentu?
2. Čo tvorí celkový downtime?
3. Prečo maintenance mode nestačí bez zastavenia background writes?
4. Ako sa líši shutdown, drain a fencing?
5. Prečo offline migration stále potrebuje recovery plán?
6. Čo musí overiť funkčná readiness?
7. Ako sa dá znížiť thundering herd po obnovení?
8. Kedy je rollback nekompatibilný s dátami?
9. Prečo je roll-forward niekedy bezpečnejší?
10. Aké state-machine a business evidence treba uchovať?

## Summary

Recreate deployment používa jeden exkluzívny runtime slot a vedome vytvára obdobie bez application capacity. Jeho výhodou je jednoduchší orchestration a nulové mixed-version obdobie; nevýhodou downtime, ostrý blast radius a slabšia okamžitá fallback kapacita. Bezpečný recreate potrebuje downtime contract, nezávislý maintenance mode, graceful drain, write freeze, overenú migration a recovery cestu, funkčnú readiness, riadené obnovenie trafficu a rollback eligibility založenú na stave dát, nie iba na dostupnosti starého artifactu.

## Glossary impact

Relevantné pojmy: recreate deployment, exclusive runtime slot, maintenance mode, downtime budget, write freeze, graceful drain, fencing, functional readiness, traffic restoration, thundering herd, rollback eligibility a offline migration.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Release management](release-management.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Rolling update →](rolling-update.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
