# Recreate deployment

Recreate deployment nahradí všetky instances starej verzie novou verziou tak, že medzi ukončením starej a pripravenosťou novej verzie môže vzniknúť obdobie bez dostupnej application capacity.

Je to jednoduchá deployment stratégia s nízkou súbežnou resource spotrebou, ale typicky s downtime alebo výrazným capacity dipom.

## 1. Základný mechanizmus

```text
old version running
→ stop old version
→ deploy/start new version
→ readiness verification
→ serve traffic
```

Počas prechodu môže byť služba nedostupná:

```text
capacity
100 % ──────┐
             └──── 0 % ────┐
                           └──── 100 %
```

## 2. Kedy je recreate vhodný

Recreate môže byť racionálna voľba, ak:

- downtime je akceptovateľný,
- aplikácia je interná alebo má maintenance window,
- nie je možné súčasne spustiť dve verzie,
- resource capacity je obmedzená,
- workload je single-instance alebo stateful,
- stará a nová verzia nemôžu bezpečne koexistovať,
- deployment je jednoduchší než orchestration rolling alebo blue-green modelu.

Jednoduchšia stratégia môže byť bezpečnejšia, ak sú jej obmedzenia explicitné a business ich akceptuje.

## 3. Downtime budget

Pred použitím recreate definuj:

- maximálny akceptovaný downtime,
- očakávaný startup time,
- migration duration,
- readiness verification time,
- rollback time,
- používateľskú komunikáciu,
- maintenance window.

Celkový outage nie je iba čas kopírovania artifactu:

```text
total downtime = shutdown + deployment + startup + migration + readiness + routing propagation
```

## 4. Graceful shutdown

Stará verzia nemá byť okamžite zabitá bez ukončenia práce.

Bezpečný shutdown:

```text
stop accepting new traffic
→ drain active requests/connections
→ finish or checkpoint work
→ release locks
→ flush telemetry
→ terminate process
```

Dôležité sú:

- termination grace period,
- connection draining,
- message-consumer shutdown,
- job checkpointing,
- idempotent retry,
- session persistence.

## 5. Readiness novej verzie

Process start nie je readiness.

Nová verzia môže potrebovať:

- načítať configuration,
- pripojiť dependencies,
- warmnúť cache,
- aplikovať migrations,
- zostaviť runtime indexes,
- zaregistrovať sa v service discovery,
- dokončiť startup probes.

Traffic sa má obnoviť až po overení kritickej request path, nie iba PID existencie.

## 6. Maintenance mode

Maintenance mode môže počas recreate:

- vracať kontrolovanú response,
- zablokovať write operácie,
- povoliť read-only režim,
- komunikovať expected duration,
- odkloniť traffic na statickú stránku.

Maintenance stránka má byť prevádzkovo nezávislá od aplikácie, ktorá sa práve nasadzuje.

## 7. Load balancer a routing

Možné flow:

```text
remove backend from load balancer
→ wait for drain
→ stop old version
→ deploy new version
→ readiness test
→ add backend to load balancer
```

Pri jedinom backende removal znamená nulovú application capacity. Load balancer však môže poskytovať kontrolovanú maintenance response.

## 8. Databázové migrácie

Recreate neodstraňuje potrebu bezpečných migrácií.

Ak je aplikácia úplne zastavená, možno vykonať nekompatibilnú migration bez mixed-version obdobia. Riziká však zostávajú:

- dlhý migration time,
- locky,
- failure uprostred migrácie,
- nedostatok disk capacity,
- nemožný rollback dát,
- neoverený restore.

Pre veľké dáta je online expand-contract často bezpečnejší aj pri recreate deployment-e.

## 9. Stateful applications

Pri stateful workload-e over:

- persistent storage attachment,
- exclusive locks,
- leader election,
- unclean shutdown recovery,
- write-ahead log replay,
- backup/restore,
- identity a hostname assumptions.

Recreate môže znížiť riziko split-brain, pretože stará a nová verzia nie sú súčasne aktívne.

## 10. Background jobs a consumers

Pred ukončením starej verzie:

- zastav scheduling novej práce,
- drainuj queue alebo bezpečne vráť messages,
- zachovaj checkpoint,
- uvoľni distributed locks,
- over idempotency po re-delivery.

Nečisté ukončenie consumerov môže vytvoriť duplicates alebo stratené side effects.

## 11. Sessions

In-memory sessions sa pri recreate stratia.

Možnosti:

- external session store,
- stateless tokens,
- kontrolované session invalidation,
- maintenance komunikácia,
- client retry a re-authentication.

## 12. Deployment workflow

Príklad:

```text
1. validate release identity
2. verify backup a recovery prerequisites
3. announce maintenance
4. enable maintenance/read-only mode
5. stop new background work
6. drain requests a consumers
7. stop old version
8. apply required migrations
9. deploy immutable new artifact
10. start new version
11. readiness a smoke tests
12. restore routing/write traffic
13. observe technical a business signals
14. close maintenance window
```

## 13. Rollback

Rollback flow:

```text
stop failed new version
→ restore compatible schema/config if required
→ deploy previous immutable artifact
→ readiness test
→ restore traffic
```

Rollback môže predĺžiť downtime. Preto definuj maximum decision time a abort criteria ešte pred začiatkom deploymentu.

## 14. Roll-forward

Ak migration nie je reversible alebo nová verzia už vykonala external side effects, roll-forward môže byť bezpečnejší:

```text
fix forward artifact
→ deploy opravu
→ verify state
```

Emergency fix musí stále zachovať artifact identity a audit trail.

## 15. Capacity a resource model

Výhoda recreate:

```text
peak capacity ≈ max(old capacity, new capacity)
```

Nie je potrebné držať starú a novú fleet súčasne.

Nevýhoda:

- nulová alebo znížená dostupnosť počas replacementu,
- startup spike,
- cold caches,
- connection storm po obnovení trafficu.

## 16. Cold start a thundering herd

Po obnovení môže všetok traffic zasiahnuť cold application.

Ochrany:

- warm-up pred routingom,
- gradual traffic restoration,
- connection limits,
- cache prewarming,
- client retry s jitterom,
- queue rate control.

## 17. Monitoring

Sleduj počas a po deployment-e:

- downtime duration,
- shutdown/drain duration,
- startup time,
- readiness latency,
- migration duration,
- request success rate,
- tail latency,
- queue backlog,
- session/auth failures,
- dependency connection count,
- business transaction recovery.

## 18. Recreate v orchestrátoroch

Niektoré orchestrátory podporujú explicitnú recreate strategy. Aj vtedy treba rozumieť:

- poradiu termination/start,
- scheduler timing,
- storage reattachment,
- readiness gates,
- rollout timeoutom,
- starým resources čakajúcim na termination.

Deklarovaný strategy name nie je dôkaz nulového overlapu vo všetkých external dependencies.

## 19. Výhody

- jednoduchý mental model,
- nízka peak resource spotreba,
- žiadne mixed-version traffic obdobie,
- jednoduchšia compatibility matica,
- vhodné pre exclusive stateful workloady,
- ľahšie reprodukovateľná sekvencia.

## 20. Nevýhody

- downtime,
- tvrdý capacity cutover,
- cold-start riziko,
- pomalší rollback,
- veľký blast radius,
- release pre všetkých používateľov naraz,
- potreba maintenance komunikácie.

## 21. Anti-patterny

### Recreate prezentovaný ako zero-downtime

Ak je jediná aktívna capacity odstránená pred novou readiness, downtime existuje.

### Stop process bez drainu

Requests a messages sa prerušia uprostred práce.

### Migration bez odhadu času

Maintenance window sa nepredvídateľne predĺži.

### Traffic obnovený pri process start

Aplikácia nemusí byť pripravená.

### Rollback artifact už nie je dostupný

Retention policy zrušila recovery možnosť.

### Maintenance page beží v rovnakej aplikácii

Zmizne spolu s nasadzovanou službou.

## 22. Troubleshooting

### Downtime je výrazne dlhší než plán

Rozlož čas na shutdown, migrations, image pull, startup, readiness a routing. Meraj každý krok oddelene.

### Stará verzia sa nevie ukončiť

Skontroluj active connections, stuck jobs, termination handler, locky a grace timeout.

### Nová verzia je ready, ale traffic zlyháva

Over routing, DNS/service discovery, TLS, dependency credentials a reálny smoke request.

### Po obnovení rastie latency

Hľadaj cold cache, connection storm, JIT warm-up, autoscaling delay a retry amplification.

### Rollback nevie čítať dáta

Nová verzia vykonala nekompatibilnú schema alebo data zmenu. Použi restore alebo roll-forward podľa pripraveného recovery plánu.

## 23. Kontrolné otázky

1. Ako funguje recreate deployment?
2. Kedy je downtime prijateľný trade-off?
3. Čo všetko tvorí celkový downtime?
4. Prečo je graceful shutdown kritický?
5. Ako maintenance mode znižuje používateľský dopad?
6. Aké riziká majú databázové migrácie počas recreate?
7. Prečo môže recreate pomôcť pri exclusive stateful workload-e?
8. Ako zabrániť thundering-herd efektu po štarte?
9. Kedy rollback nemusí byť bezpečný?
10. Aké metriky treba zachovať pre analýzu deploymentu?

## Glossary impact

Relevantné pojmy: recreate deployment, maintenance window, maintenance mode, graceful shutdown, connection draining, startup readiness, cold start, thundering herd, exclusive stateful workload a deployment downtime.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Release management](release-management.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Rolling update →](rolling-update.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
