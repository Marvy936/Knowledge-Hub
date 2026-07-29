# CAP theorem

CAP theorem nie je pravidlo „vyber si dve vlastnosti“ pre celý systém za každých okolností. Je to scoped impossibility result o správaní replikovanej služby počas network partition-u pri konkrétnych definíciách consistency a availability.

Praktická otázka preto nie je:

> Je systém CP alebo AP?

Presnejšia otázka je:

> Čo urobí konkrétna read alebo write operation, keď required replicas nemôžu navzájom komunikovať, a aký business outcome tým systém dovolí alebo odmietne?

## 1. Dominantný model

```text
business operation a invariant
→ exact replicated subject a client cohort
→ normal topology a authority
→ partition/failure scenario
→ dostupné observations a quorum
→ per-operation consistency/availability decision
→ acknowledgement alebo explicit refusal
→ stale/divergent/unknown outcome
→ reconciliation a partition-heal behavior
→ second-partition validation
```

CAP je užitočný iba vtedy, keď sa mapuje na exact operation, exact failure a exact response semantics.

## 2. Formálna intuition

Gilbert–Lynch formalizácia pracuje v asynchronous network model-e, kde správy môžu byť arbitrárne oneskorené alebo stratené. Pri partition-e nemôže replikovaná služba súčasne garantovať:

- **atomic consistency** — operation sa správa ako jediná aktuálna kópia;
- **availability** — každý request prijatý non-failed node-om nakoniec dostane response;
- **partition tolerance** — systém musí fungovať napriek strate komunikácie medzi časťami siete.

V modernej terminológii sa CAP „C“ typicky interpretuje ako linearizability alebo veľmi podobná single-copy consistency vlastnosť, nie ako ľubovoľná databázová consistency alebo ACID `C`.

## 3. Čo znamená consistency v CAP

CAP consistency znamená, že reads a writes možno usporiadať tak, akoby existovala jedna aktuálna kópia a operations nastali atomicky medzi invocation a response.

Príklad:

```text
write route_generation = 912 dokončený
→ neskorší linearizable read
→ nesmie vrátiť 911
```

Neznamená to automaticky:

- schema constraints;
- referential integrity;
- serializable multi-row transaction;
- causal consistency;
- eventual convergence;
- application business correctness.

Tieto properties musia byť definované samostatne.

## 4. Čo znamená availability v CAP

Availability v proof modeli nie je percentuálne SLO ani „väčšina requestov funguje“.

Je to silný liveness contract:

```text
request na non-failed node
→ finite processing
→ response
```

Response môže byť stale alebo conflict-producing, ak sa systém rozhodol zachovať availability namiesto single-copy consistency.

Systém, ktorý počas partition-u odmietne write alebo čaká na quorum bez garantovaného response, zachováva consistency za cenu CAP availability pre danú operation.

## 5. Partition tolerance nie je voliteľný checkbox

V distributed systéme môže dôjsť k:

- packet loss;
- asymmetric reachability;
- routing blackhole;
- overloaded linku;
- DNS alebo load-balancer divergence;
- firewall/policy skew;
- process pause;
- disk stall vyzerajúcemu ako network failure;
- arbitrárne dlhému message delay-u.

Aplikácia nevie spoľahlivo odlíšiť vzdialený crash od partition-u alebo extrémne pomalého peer-u. Timeout je observation, nie proof konkrétnej príčiny.

## 6. CAP decision vzniká počas partition-u

Mimo partition-u systém môže poskytovať silnú consistency aj availability v bežnom zmysle. Konflikt sa aktivuje, keď required participants nemôžu koordinovať.

```text
normal operation
→ quorum reachable
→ linearizable write/read

partition
→ quorum side môže pokračovať konzistentne
→ minority side musí odmietnuť, čakať alebo obslúžiť slabší contract
```

Preto „CA databáza“ v reálnej sieti často znamená iba to, že partition behavior nie je explicitne navrhnutý.

## 7. Decision je per operation, nie iba per product

Jeden systém môže počas rovnakého partition-u používať rôzne policies:

| Operation | Požadovaný outcome počas partition-u |
|---|---|
| Create settlement intent | odmietnuť bez authoritative quorum |
| Read immutable product catalog | dovoliť bounded stale read |
| Read current provider route | vyžadovať minimum generation alebo linearizable read |
| Append telemetry | lokálne bufferovať a neskôr merge-núť |
| Merchant dashboard projection | zobraziť stale marker a known revision |
| Provider side effect | nevykonať bez stable idempotency a current authority |

Nálepka `CP` alebo `AP` bez operation matrixu je príliš hrubá.

## 8. Quorum a majority side

Pri päťčlennom consensus clusteri je quorum `3`.

Partition `3 + 2` vytvára:

```text
majority side 3
→ môže zvoliť alebo zachovať leadera
→ môže commitovať nové decisions

minority side 2
→ nemôže bezpečne commitovať nový log entry
→ môže odmietnuť alebo poskytovať explicitne stale/local reads
```

Quorum neznamená, že každý client automaticky dostane current result. Client môže stále:

- čítať z local cache;
- použiť serializable/member-local read;
- držať staré connection;
- ignorovať revision;
- pokračovať s previously loaded generation.

## 9. Consistency-preserving partition behavior

Pre critical authoritative write môže byť správny outcome:

```text
quorum unavailable
→ write rejected alebo deadline exceeded
→ no success acknowledgement
→ stable operation identity retained
→ client neskôr queryuje authoritative state
```

Výhoda:

- žiadne divergentné committed histories pre daný invariant.

Cena:

- operation nie je CAP-available na minority alebo quorum-less side;
- caller potrebuje truthful degraded behavior;
- timeout môže stále vytvoriť unknown outcome, ak request dosiahol quorum tesne pred stratou response.

## 10. Availability-preserving partition behavior

Pre mergeable alebo derived data môže systém akceptovať local progress:

```text
partitioned replica
→ local write/read accepted
→ operation označená origin/causal/version identity
→ po heal-e merge alebo conflict resolution
```

To je bezpečné iba ak domain podporuje:

- commutative operations;
- last-writer policy s akceptovanou stratou;
- CRDT alebo explicitný merge;
- append-only local log;
- bounded stale semantics;
- post-heal reconciliation.

Availability bez conflict modelu je iba deferred corruption.

## 11. Stale reads sú contract, nie náhoda

Slabší read musí deklarovať:

- maximálnu age alebo revision gap;
- source replica/generation;
- session guarantees;
- whether read môže autorizovať write alebo external effect;
- fallback pri prekročení freshness boundu;
- UI/API stale marker;
- recovery po heal-e.

```text
read route generation 911
current required generation 912
→ stale read možno použiť na dashboard
→ nesmie autorizovať nový provider side effect
```

## 12. Partition-heal nie je automatická correctness

Po obnovení connectivity treba rozlíšiť:

- committed majority history;
- uncommitted minority attempts;
- local accepted writes;
- external effects vykonané mimo consensus;
- cache/session-loaded generations;
- client retries a duplicate attempts;
- stale decisions, ktoré už ovplyvnili business.

```text
network healed
→ replicas converge na committed log
→ application side effects sa nemusia samy vrátiť
→ potrebná je business reconciliation
```

## 13. PACELC ako doplnková otázka

CAP sa sústreďuje na partition. V normálnom stave stále existuje trade-off medzi latency a consistency.

Praktický návrh preto hodnotí:

```text
if partition:
  consistency vs availability
else:
  latency vs consistency
```

Nie je to náhrada CAP theorem-u, ale pripomienka, že quorum/read semantics majú cenu aj bez incidentu.

## 14. Connected incident `DB-PAY-59`

Atlas Payments release `payments 8.3` presunul provider-route control do päťčlenného consensus clusteru:

```text
Region A: 3 voting members
Region B: 2 voting members
quorum:   3
```

Provider `P1` začal vracať vysoký timeout rate. Control plane v Region A úspešne commitol:

```text
provider_route_generation: 911 → 912
route: P1 → P2
```

Následne deväťminútový network partition oddelil Region B.

Majority Region A:

- zachoval quorum;
- commitol generation `912`;
- linearizable reads vracali current route `P2`.

Minority Region B:

- nemohla commitovať nový route state;
- control client používal member-local serializable read;
- application cache držala generation `911` s desaťminútovým TTL;
- request path nerozlišoval stale route od current authority.

Počas partition-u Region B naďalej posielal časť settlements na `P1`.

## 15. CAP boundary incidentu

CAP theorem nevysvetľuje celý incident jedinou vetou. Exact decision bol:

```text
partitioned Region B
→ current linearizable route unavailable bez quorum
→ application zvolila local stale availability
→ stale route bola dovolená pre side-effecting operation
→ business correctness sa porušila
```

Primary CAP/design root cause bol:

> Provider-route read nemal per-operation partition contract; member-local availability bola implicitne použitá tam, kde side-effecting settlement vyžadoval current authority alebo explicitné refusal.

Consensus cluster sa nesprával split-brain. Majority history bola správna. Application nad minority readom vytvorila nesprávny business decision.

## 16. Dôsledky `DB-PAY-59`

Počas 9 minút:

- `24 600` logical settlement operations vstúpilo do affected flowu;
- `3 842` operations v Region B načítalo stale route generation `911`;
- `1 126` provider attempts smerovalo na degraded `P1` po commitnutí generation `912`;
- `1 384` operations skončilo ako `sent-unknown` pre timeout;
- `27` duplicate physical provider attempts vyžadovalo reconciliation;
- provider idempotency zabránila duplicate financial settlement effectom.

Nulové duplicate financial effects neznamenajú, že CAP/read contract prešiel. Systém porušil required current-route decision a vytvoril vysoký unknown-outcome load.

## 17. Evidence-preserving containment

```text
freeze route/config changes
→ preserve cluster term, revision a member topology
→ map partitioned client cohorts a loaded generations
→ stop stale-route side effects v Region B
→ require quorum/current-generation read pre new settlement
→ preserve provider attempts, idempotency a timeout evidence
→ classify committed, never-sent, sent-unknown a completed operations
→ reconcile provider ledger
```

Unsafe response by bol globálny cache flush bez zachovania loaded-generation a request evidence.

## 18. Authoritative redesign

Per-operation matrix:

```text
create settlement / choose provider route
→ linearizable current-generation read
→ fail closed pri quorum/current-generation uncertainty

merchant dashboard
→ bounded stale read allowed
→ response includes observed_generation a stale=true

telemetry append
→ local durable buffer allowed
→ later merge
```

Application contract:

- route decision obsahuje exact generation;
- settlement row persistuje used route generation;
- minimum acceptable generation sa prenáša requestom;
- local cache key je versionovaný;
- stale read nemôže autorizovať external effect;
- degraded mode je explicitný, observable a rate-limited;
- partition-heal spúšťa cohort reconciliation.

## 19. CAP acceptance verdict

CAP design je prijatý, keď:

- exact replicated subject a invariant sú explicitné;
- partition scenarios a observation limits sú pomenované;
- consistency znamená konkrétny model, nie všeobecnú „správnosť“;
- availability znamená konkrétny response/liveness contract;
- decision je definovaný per operation a cohort;
- quorum/minority behavior je explicitné;
- stale/local reads majú freshness, generation a allowed-use contract;
- writes počas partition-u majú conflict/merge alebo refusal model;
- acknowledgement neklame o current authority;
- timeout/unknown outcomes majú stable identity a reconciliation;
- partition heal rieši external effects a loaded/cached state;
- second partition, asymmetric partition a delayed-message tests prejdú;
- forbidden stale-authority a divergent-unmergeable outcomes sú odmietnuté.

## 20. Troubleshooting flow

```text
stale/divergent/unavailable distributed outcome
→ exact operation a replicated subject
→ normal authority/topology
→ partition a reachable-set evidence
→ quorum, term, revision a leader state
→ client read/write consistency mode
→ cache/session-loaded generation
→ acknowledgement a timeout evidence
→ local/external side effects
→ heal/convergence behavior
→ reconciliation a second-partition validation
```

## 21. Anti-patterny

### CAP znamená vyber si dve

Trade-off je scoped na partition a konkrétne definície properties.

### Partition tolerance vypneme

V sieti neviete garantovať, že komunikácia nikdy nezlyhá alebo sa arbitrárne neoneskorí.

### CP systém je vždy unavailable

Môže byť dostupný mimo partition-u a na quorum side; konkrétne minority operations môžu byť odmietnuté.

### AP systém je nekonzistentný navždy

Môže konvergovať alebo poskytovať domain-specific merge semantics. Musí to však dokazovať.

### Quorum vyriešilo application correctness

Client môže použiť stale cache, weak read alebo external side effect mimo consensus.

### Stale read je bezpečný, lebo ide iba o read

Read môže autorizovať write, route, access alebo external effect.

### Po heal-e je incident ukončený

Replicas môžu konvergovať, ale external effects a client retries zostanú.

## 22. Kontrolné otázky

1. Aké presné definície C, A a P používa CAP theorem?
2. Prečo „pick two“ skresľuje partition decision?
3. Ako sa CAP consistency líši od ACID consistency?
4. Čo znamená availability vo formálnom modeli?
5. Prečo je timeout iba observation?
6. Prečo treba rozhodovať per operation?
7. Kedy je stale read bezpečný?
8. Čo musí obsahovať availability-preserving conflict model?
9. Prečo quorum cluster nezabránil `DB-PAY-59`?
10. Ktorá operation mala failnúť closed počas partition-u?
11. Čo treba reconciliovať po heal-e?
12. Čo overuje CAP acceptance verdict?

## Glossary impact

Relevantné pojmy: CAP subject, atomic consistency — CAP, CAP availability, network partition, per-operation partition contract, quorum side, minority side, partition refusal, partition-local progress, partition-heal reconciliation, stale-authority read, minimum acceptable generation, PACELC question a CAP acceptance verdict.

## Primárne zdroje

- [Gilbert a Lynch — Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services](https://groups.csail.mit.edu/tds/reflist.html)
- [etcd API guarantees](https://etcd.io/docs/v3.7/learning/api_guarantees/)
- [etcd Failure modes](https://etcd.io/docs/v3.8/op-guide/failures/)
