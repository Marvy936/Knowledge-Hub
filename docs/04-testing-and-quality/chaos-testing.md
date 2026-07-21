# Chaos testing

## Metadata

- Status: Learning
- Level: L2
- Domain: Testing and Software Quality

## 1. Definícia

Chaos testing je riadené experimentovanie so zlyhaniami s cieľom overiť, či systém zachová definovaný steady state aj pri poruche komponentu, dependency, siete, kapacity alebo prevádzkového procesu.

Nejde o náhodné rozbíjanie produkcie.

```text
hypotéza
→ definovaný steady state
→ kontrolované narušenie
→ pozorovanie
→ rozhodnutie
→ zlepšenie
```

Chaos testing patrí do širšieho chaos engineeringu a resilience engineeringu.

## 2. Čo testuje

Bežný test overuje:

```text
pri správnych podmienkach vznikne očakávaný výsledok
```

Chaos experiment overuje:

```text
pri konkrétnom narušení systém zostane v prijateľných hraniciach
```

Príklady narušení:

- ukončenie instance alebo procesu,
- network latency, packet loss alebo partition,
- nedostupná dependency,
- DNS failure,
- disk full alebo read-only filesystem,
- CPU alebo memory pressure,
- queue backlog,
- expired certificate,
- clock skew,
- zone outage,
- poškodený alebo oneskorený event,
- zlyhanie operátorského postupu.

## 3. Steady state

Steady state je merateľné správanie, ktoré má systém zachovať.

Nemá byť definovaný iba ako „proces beží“.

Príklady:

- checkout success rate nad 99,5 %,
- p95 latency pod 500 ms,
- žiadna duplicitná platba,
- backlog sa po obnove vyprázdni do 15 minút,
- failover dokončený do 60 sekúnd,
- error budget burn neprekročí limit,
- používateľ dostane graceful degradation namiesto úplného failure.

Bez steady-state hypotézy nemožno rozhodnúť, či experiment uspel.

## 4. Hypotéza

Dobrá hypotéza má formu:

```text
Ak nastane X,
systém zachová Y
v limite Z,
pretože funguje mechanizmus M.
```

Príklad:

```text
Ak jedna application instance prestane odpovedať,
load balancer ju odstráni do 20 sekúnd,
error rate zostane pod 1 %
a nová kapacita sa doplní do 2 minút.
```

Hypotéza testuje konkrétny resilience mechanizmus, nie všeobecnú vieru v systém.

## 5. Experiment contract

Pred spustením definuj:

- cieľ a hypotézu,
- steady-state metrics,
- presný fault,
- scope a target,
- environment,
- čas trvania,
- blast radius,
- preconditions,
- abort criteria,
- rollback/recovery,
- ownera,
- observerov,
- evidence,
- communication plan.

Experiment bez kontraktu je neauditovateľný zásah.

## 6. Blast radius

Blast radius určuje maximálny rozsah dopadu.

Možné obmedzenia:

- jedna test instance,
- jeden pod,
- jedna availability zone,
- interní používatelia,
- malé percento trafficu,
- jeden tenant,
- read-only workflow,
- časovo obmedzené fault injection.

Začni najmenším rozsahom, ktorý ešte poskytne relevantný dôkaz.

## 7. Safety controls

Chaos experiment potrebuje technické aj procesné poistky:

- kill switch,
- automatický timeout,
- health prechecks,
- scope allowlist,
- approval podľa rizika,
- monitoring experimentu,
- rate limits,
- zákaz kritických targets,
- automatické rollback/cleanup,
- maintenance alebo low-risk window podľa potreby.

Bezpečný experiment sa musí dať zastaviť rýchlejšie, než sa škoda nekontrolovane šíri.

## 8. Abort criteria

Abort criteria musia byť konkrétne.

Príklady:

- error rate nad 2 % počas 60 sekúnd,
- p99 latency nad 2 sekundy,
- prvá duplicita finančnej transakcie,
- backlog nad 100 000 messages,
- SLO burn rate nad stanovený limit,
- strata observability,
- neočakávaný dopad mimo target scope.

„Zastavíme, keď to bude vyzerať zle“ nie je operovateľné pravidlo.

## 9. Experiment ladder

Bezpečný progres:

```text
model/tabletop
→ local/test environment
→ integration/staging
→ production shadow alebo internal cohort
→ small production scope
→ širší scope
```

Každý krok má zvýšiť fidelity, nie slepo zopakovať rovnaký fault.

Niektoré failure modes sa dajú dôveryhodne overiť iba v produkcii, ale predchádzajúce kroky majú odstrániť základné chyby.

## 10. Tabletop exercise

Tabletop je simulované prevádzkové cvičenie bez technického fault injection.

Scenár:

- región je nedostupný,
- on-call dostane alert,
- tím používa runbook,
- rozhoduje o failoveri,
- komunikuje incident,
- overuje recovery.

Odhaľuje:

- nejasné ownership,
- neaktuálne kontakty,
- chýbajúce prístupy,
- nefunkčné runbooky,
- nejasné rozhodovacie právomoci,
- chýbajúce business priority.

Resilience nie je iba technická vlastnosť.

## 11. Process a instance failure

Experiment môže ukončiť process alebo instance.

Overuj:

- health detection,
- traffic removal,
- restart policy,
- rescheduling,
- capacity replacement,
- connection draining,
- state recovery,
- request retry behavior,
- alerting.

Riziko:

Ak klienti agresívne retryujú, malý failure môže vytvoriť retry storm.

## 12. Network fault

Možné faults:

- latency,
- jitter,
- packet loss,
- bandwidth limit,
- DNS failure,
- asymmetric reachability,
- complete partition.

Overuj:

- timeouts,
- retries,
- circuit breakers,
- queueing,
- fallback,
- idempotency,
- telemetry.

Fault musí byť aplikovaný na správnom observation point-e. Namespace, service mesh alebo cloud network layer môžu meniť výsledok.

## 13. Dependency failure

Dependency nemusí byť úplne down.

Realistickejšie scenáre:

- pomalé responses,
- partial errors,
- malformed payload,
- rate limiting,
- stale data,
- intermittent timeout,
- connection resets,
- auth failure.

Systém má rozlíšiť retryable a non-retryable failure a nesmie nekontrolovane násobiť load.

## 14. Resource pressure

Experimenty:

- CPU saturation,
- memory pressure,
- disk exhaustion,
- inode exhaustion,
- file descriptor exhaustion,
- thread pool exhaustion,
- connection pool saturation.

Overuj:

- backpressure,
- admission control,
- load shedding,
- graceful degradation,
- autoscaling,
- alerting,
- recovery po odstránení pressure.

Resource exhaustion môže poškodiť observability ako prvú, preto treba externý observation point.

## 15. Data a messaging faults

Možné scenáre:

- duplicitný event,
- out-of-order delivery,
- oneskorenie,
- poison message,
- consumer restart po side effecte,
- partial transaction,
- schema mismatch.

Overuj:

- idempotency,
- deduplication,
- ordering assumptions,
- dead-letter handling,
- replay,
- checkpointing,
- reconciliation.

Experiment nesmie nevratne poškodiť produkčné dáta.

## 16. State a recovery

Dôležitá otázka nie je iba „prežije systém fault?“, ale aj:

```text
vráti sa po fault-e do zdravého stavu?
```

Overuj:

- backlog drain,
- cache warming,
- replica synchronization,
- leader election,
- stuck locks,
- orphaned resources,
- data reconciliation,
- capacity normalization.

Systém môže počas faultu fungovať prijateľne, ale po jeho odstránení zostať degradovaný.

## 17. Disaster recovery experiments

DR experimenty overujú:

- backup restore,
- RPO,
- RTO,
- region failover,
- DNS/routing cutover,
- secrets a certificates,
- dependencies,
- integrity dát,
- návrat do primary režimu.

„Backup job bol úspešný“ nie je dôkaz obnoviteľnosti.

DR test musí overiť používateľský alebo business výsledok po obnove.

## 18. Game day

Game day je plánované tímové cvičenie kombinujúce faults, observability, incident response a learning.

Dobrý game day:

- má jasný scope,
- nie je skúškou jednotlivca,
- používa realistický scenár,
- zachytáva timeline,
- testuje techniku aj koordináciu,
- končí konkrétnymi actions.

Cieľom nie je „nachytať“ on-call tím.

## 19. Automatisované chaos experimenty

Opakované experimenty možno automatizovať v CI/CD alebo scheduled production workflow.

Podmienky:

- stabilný experiment contract,
- nízky blast radius,
- kvalitné abort controls,
- deterministic cleanup,
- dôveryhodné metrics,
- jasný ownership.

Automatizácia neznižuje zodpovednosť. Zvyšuje potrebu bezpečných guardrails.

## 20. Chaos testing a SLO

SLO poskytuje steady-state hranicu.

Experiment môže overiť:

- či failure neprekročí SLO,
- ako rýchlo sa míňa error budget,
- či alert reaguje pred vážnym dopadom,
- či recovery obnoví SLI.

Bez používateľsky orientovaného SLI môže experiment optimalizovať internú metriku bez reálneho významu.

## 21. Observability requirements

Pred experimentom musí byť možné sledovať:

- experiment start/stop,
- target identity,
- fault state,
- user-facing SLIs,
- infrastructure metrics,
- logs a traces,
- dependency behavior,
- recovery progress.

Experiment label alebo correlation ID musí umožniť oddeliť jeho efekt od bežného trafficu.

## 22. Learning a remediation

Výsledok experimentu:

- hypotéza potvrdená,
- hypotéza vyvrátená,
- experiment nejednoznačný,
- experiment neplatný pre chybný setup.

Výstup nemá byť iba report.

Má viesť k:

- oprave resilience mechanizmu,
- novému alertu,
- zmene timeout/retry policy,
- aktualizácii runbooku,
- novému regression testu,
- platformovému guardrailu,
- opakovaniu experimentu po oprave.

## 23. Anti-patterny

### Chaos bez hypotézy

Vznikne incident alebo šum bez jasného poznatku.

### Náhodné vypínanie produkcie

Nie je to experiment, ale neplánovaný risk.

### Test iba v stagingu

Môže byť užitočný, ale nemusí overiť produkčné topology a traffic behavior.

### Experiment bez abort criteria

Tím nevie, kedy zásah zastaviť.

### Game day ako hodnotenie ľudí

Vedie k skrývaniu problémov a psychologicky nebezpečnému prostrediu.

### Chaos tool ako cieľ

Nainštalovaný framework nie je dôkaz resilience.

### Potvrdená hypotéza bez ďalšej práce

Systém sa mení; experiment potrebuje opakovanie alebo automatizáciu.

## 24. Metriky

Sleduj napríklad:

- počet experimentov podľa failure domain,
- podiel potvrdených/vyvrátených/neplatných hypotéz,
- čas detection a recovery,
- SLI dopad,
- počet a vek remediation actions,
- repeat experiment success,
- experiment abort rate,
- neplánovaný blast-radius expansion,
- coverage kritických dependencies a recovery paths.

Počet spôsobených failures nie je cieľová metrika.

## 25. Rozhodovací rámec

1. Akú konkrétnu vlastnosť resilience overujeme?
2. Aký je steady state?
3. Aký fault najlepšie testuje hypotézu?
4. Aký je najmenší relevantný blast radius?
5. Aké sú abort criteria?
6. Máme externý observation point?
7. Ako sa experiment zastaví a cleanupne?
8. Aký je data-integrity risk?
9. Kto experiment vlastní a sleduje?
10. Aká zmena alebo opakovanie nasleduje po výsledku?

## 26. Kontrolné otázky

1. Aký je rozdiel medzi chaos testingom a náhodným rozbíjaním?
2. Čo je steady-state hypothesis?
3. Čo musí obsahovať experiment contract?
4. Ako sa riadi blast radius?
5. Načo slúžia abort criteria a kill switch?
6. Aký je význam experiment ladderu?
7. Čo testuje tabletop exercise?
8. Prečo treba sledovať recovery aj po skončení faultu?
9. Ako chaos testing súvisí so SLO a error budgetom?
10. Ako sa výsledok experimentu mení na trvalé zlepšenie?

## Glossary impact

Relevantné pojmy: chaos testing, chaos engineering, resilience engineering, steady state, experiment hypothesis, experiment contract, blast radius, abort criterion, kill switch, fault injection, game day, tabletop exercise, graceful degradation, load shedding, RPO a RTO.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Shift-right](shift-right.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Continuous Integration →](../05-ci-cd-and-release/continuous-integration.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
