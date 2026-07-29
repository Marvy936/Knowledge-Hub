# Monolith, modular monolith a microservices

Monolith, modular monolith a microservices nie sú maturity levels, cez ktoré musí každá aplikácia postupne prejsť. Sú to rozdielne boundaries pre deployment, runtime failure, data ownership, transactions, communication, scaling, operations a team autonomy. Správny návrh minimalizuje nezvládnutú koordináciu pri zachovaní business invariantov a požadovanej rýchlosti zmeny.

```text
business capabilities a change topology
→ exact architecture subject
→ domain/invariant/ownership boundaries
→ module/service a data boundaries
→ communication a transaction model
→ deployment, scale a failure isolation
→ observability, security a operations
→ migration/compatibility strategy
→ effective organizational a runtime behavior
→ business outcome a second-change/failure validation
```

## 1. Exact architecture subject

Tvrdenie `máme microservices` podľa počtu repozitárov alebo Kubernetes Deploymentov je slabé. Subject musí obsahovať:

- business capabilities a user journeys;
- domain/subdomain a invariant boundaries;
- team ownership a change coupling;
- source/module/build/deployment boundaries;
- process a failure boundaries;
- authoritative data ownership;
- transaction a consistency model;
- synchronous/asynchronous communication paths;
- independent scaling requirements;
- release a compatibility protocol;
- observability, security, on-call a recovery ownership;
- platform/organizational capability;
- migration generation a exit/rollback strategy;
- expected benefits a measurable costs.

Príklad:

```text
capability: merchant settlement
invariant: one merchant operation creates one executable settlement intent
modules/services:
  settlement command
  merchant policy
  provider execution
  projection/reporting
authority:
  PostgreSQL settlement/outbox
  versioned merchant policy
communication:
  synchronous decision path + durable asynchronous completion
failure objective:
  policy/reporting failure nesmie stratiť acknowledged settlement intent
ownership:
  one team owns end-to-end SLO and reconciliation
```

## 2. Monolith

Monolith je application, ktorej významná časť sa buildí a deployuje ako jeden artifact alebo runtime unit. Môže byť dobre modularizovaný alebo úplne previazaný.

Typický lifecycle:

```text
source change
→ one build/artifact
→ one deployment generation
→ in-process calls
→ shared transaction/data access
→ process-level scaling/failure
→ coordinated rollback/recovery
```

### Výhody

- jednoduché local development a end-to-end debugging;
- in-process calls bez network failure semantics;
- jednoduchšie atomic transactions cez jeden database boundary;
- menej deployment, identity, certificate, discovery a observability objects;
- nižší platform/on-call overhead;
- jednoduchšia consistency a refactoring naprieč codebase-om;
- dobrá voľba pre malý tím alebo neustálené domain boundaries.

### Náklady

- whole-artifact release coupling;
- shared process failure a resource contention;
- coarse independent scaling;
- slow build/test/deploy pri nekontrolovanom raste;
- nejasné ownership pri veľkom tíme;
- jednoduché obchádzanie module boundaries;
- shared database môže vytvoriť schema coupling;
- jedna change môže vyžadovať koordináciu veľkej časti systému.

Monolith nie je synonymum pre single instance. Jeden monolithic artifact môže mať mnoho replicas, HA, queues, cache a external dependencies.

## 3. Modular monolith

Modular monolith používa jeden deployment/process boundary, ale zavádza explicitné internal module boundaries:

```text
business capability
→ module API
→ hidden internal model/data access
→ explicit dependency direction
→ in-process call/event
→ one deployment generation
```

Module má typicky:

- jasný business purpose;
- public contract;
- private implementation;
- controlled dependencies;
- owned schema/tables alebo aspoň enforced data-access boundary;
- tests na architecture/dependency rules;
- explicit event/command model;
- failure a transaction assumptions.

### Výhody

- zachováva jednoduché deployment a operations;
- umožňuje atomic transactions medzi modulmi, keď je to skutočne potrebné;
- znižuje network/distributed-system overhead;
- vytvára boundaries použiteľné pre budúcu extraction;
- podporuje team ownership bez okamžitého distributed runtime-u;
- refactoring boundaries je lacnejší než pri remote contracts a independent data histories.

### Riziká

- boundaries môžu existovať iba v diagramoch;
- priame SQL/shared ORM entities ich obídu;
- internal events môžu byť iba skryté function calls bez durable semantics;
- jeden deploy stále koordinuje release;
- resource/failure isolation zostáva process-level;
- team môže predčasne predstierať service autonomy.

Modular monolith je často najnižší spoľahlivý architecture scope pre rastúci domain, kým independent deployment, scaling alebo failure isolation neprinesú preukázanú hodnotu.

## 4. Microservices

Microservice architecture rozdeľuje systém na independently deployable services s explicitnými runtime a ownership boundaries.

```text
service-owned capability
→ service API/event contract
→ network/broker transport
→ independent process/deployment
→ service-owned state
→ local transaction
→ cross-service workflow/consistency
→ independent failure/recovery
```

### Potenciálne výhody

- independent deployment a release cadence;
- failure a resource isolation;
- independent scaling;
- jasnejšie team/service ownership;
- technology/data model fit per bounded capability;
- menší deployable unit;
- možnosť oddeleného compliance/security boundary.

### Povinné náklady

- network latency, timeout a partial failure;
- service discovery, identity, TLS a authorization;
- API/event versioning a compatibility;
- distributed tracing/log correlation;
- cross-service consistency a workflow recovery;
- per-service deployment, capacity, SLO, on-call a runbooks;
- data duplication/projections;
- integration test a environment complexity;
- fleet-wide connection, retry a resource multiplication;
- incident coordination a ownership gaps.

Microservice nie je `malá trieda cez HTTP`. Service boundary má zodpovedať coherent business capability, ownership a data authority.

## 5. Boundary dimensions

Architecture sa nesmie klasifikovať iba jednou osou.

| Boundary | Monolith | Modular monolith | Microservices |
|---|---|---|---|
| source | môže byť jeden repo | často jeden repo s modules | jeden alebo viac repos |
| build | jeden build graph/artifact | jeden artifact, module checks | independent artifacts |
| deployment | coordinated | coordinated | independent |
| process/failure | shared | shared | per service |
| communication | in-process | controlled in-process | network/event |
| data | často shared | ownership môže byť enforced logicky | service-owned authority |
| transaction | local/shared DB | local/shared DB podľa invariantov | local per service; workflow naprieč services |
| scaling | whole application | whole application/module-specific iba interne | per service |
| operations | one service surface | one service surface + modules | fleet of service surfaces |

Jeden repository s desiatimi independently deployed services je microservice runtime. Desať repositories buildovaných a deployovaných naraz nad jednou shared database môže byť distributed monolith.

## 6. Domain a invariant boundaries

Boundary má vychádzať z:

- business capability;
- ubiquitous language;
- invariantov, ktoré musia byť atomic alebo strongly coordinated;
- data ownership;
- change cadence;
- team cognitive load;
- failure isolation;
- scale profile;
- security/compliance needs.

Silný invariant:

```text
settlement row + executable outbox intent vzniknú spolu alebo vôbec
```

naznačuje spoločnú local transaction boundary. Rozdelenie len preto, že `outbox je eventing service`, vytvorí distributed invariant bez benefitu.

Naopak reporting projection môže mať:

- iný freshness objective;
- independent scale;
- rebuildable derived state;
- eventual consistency;
- separate deployment.

Je prirodzenejší extraction candidate.

## 7. Data ownership

### Shared database

Shared database zjednodušuje joins a transactions, ale umožňuje hidden coupling:

- service A číta private tables service B;
- schema change obchádza contract;
- ownership incidentu je nejasné;
- independent deployment je iba zdanlivý.

### Database per service

`Database per service` znamená exclusive authority cez service contract, nie povinne samostatný database server. Môže byť:

- separate database;
- separate schema s enforced role ownership;
- separate cluster pri isolation potrebe.

Nesmie znamenať, že jeden business fact má viac authoritative writers.

### Derived data

Service môže mať local projection:

```text
source service authoritative event
→ durable delivery
→ local projection
→ freshness/lag evidence
→ rebuild path
```

Projection absence alebo staleness nesmie meniť authoritative write outcome bez explicitného contractu.

## 8. Transactions naprieč boundaries

Monolith/modular monolith môže používať jednu local database transaction. Microservices typicky potrebujú:

- local transaction per service;
- transactional outbox/inbox;
- durable message delivery;
- idempotency;
- saga/process manager;
- compensation;
- reconciliation;
- unknown-outcome handling.

```text
local commit
→ durable event
→ delivery attempt
→ consumer local commit
→ acknowledgement
→ workflow state
→ timeout/compensation/reconciliation
```

Distributed transaction protocol môže byť vhodný v niektorých controlled environments, ale nie je automatic replacement za dobrú boundary. Ak dva services vždy musia commitovať spolu a zlyhávať spolu, decomposition môže byť nesprávne.

## 9. Communication coupling

### Synchronous

Výhody:

- immediate response;
- jednoduchší caller mental model;
- prirodzené request/response validation.

Náklady:

- runtime availability coupling;
- latency multiplication;
- timeout/retry/unknown outcome;
- cascading failure;
- version/contract coupling.

### Asynchronous

Výhody:

- temporal decoupling;
- buffering a independent consumption;
- fan-out;
- durable workflow evidence.

Náklady:

- eventual consistency;
- duplicates a ordering;
- backlog/replay;
- schema evolution;
- delayed failure visibility;
- reconciliation.

Microservices s chainom piatich synchronous calls môžu mať silnejší runtime coupling než modular monolith.

## 10. Deployment a compatibility

Independent deployment potrebuje independent compatibility:

```text
provider contract generation
→ old/new consumer inventory
→ backward/forward-compatible change
→ staged provider rollout
→ consumer convergence
→ contract retirement
```

Ak každý service deployment vyžaduje synchronized release všetkých consumers, systém je distributed deployment monolith.

Data migrations musia zohľadniť:

- old/new service versions;
- event backlog;
- rollback artifacts;
- projections;
- shared libraries;
- cross-service invariants;
- recovery po partial rollout-e.

## 11. Scaling a resource multiplication

Microservice extraction môže oddeliť scale profile, ale zároveň násobí:

- application instances;
- connection pools;
- caches;
- telemetry agents;
- healthchecks;
- queues;
- TLS connections;
- control-plane objects.

Fleet-wide resource model:

```text
services × replicas × per-replica pools/retries/buffers
→ database/broker/provider demand
```

Každý service optimalizovaný lokálne môže globálne preťažiť shared dependency.

## 12. Failure isolation

Service boundary izoluje iba failures, ktoré neprechádzajú cez shared dependencies a retry paths.

Príklady slabého isolation:

- všetky services používajú jednu overloaded database;
- shared Redis cluster zlyhá ako central authority;
- synchronous call chain prenesie latency;
- common library defect sa rolloutne všade;
- retry storm zasiahne provider;
- shared identity/DNS/control plane zastaví všetky services.

Failure isolation sa preukazuje experimentom a incident evidence, nie počtom Pods.

## 13. Observability a operations

Každý independently operated service potrebuje:

- ownera;
- SLI/SLO a error budget;
- dashboards a actionable alerts;
- logs/traces/events s stable identity;
- capacity model;
- on-call/escalation;
- runbooks a incident roles;
- backup/recovery;
- security/identity lifecycle;
- dependency a contract inventory;
- deployment/recovery evidence.

Ak organizácia nevie bezpečne prevádzkovať desať services, decomposition môže znížiť delivery aj reliability.

## 14. Organizational boundaries

Architecture a organization sa vzájomne ovplyvňujú. Service ownership má byť end-to-end:

```text
source
→ build/release
→ runtime/data
→ SLO/on-call
→ incident/recovery
→ lifecycle/retirement
```

`Dev team owns code, DBA owns database, platform owns deploy, ops owns incidents` bez spoločného capability ownera vytvára queue a gaps bez ohľadu na architecture style.

Team size nie je jediný faktor. Dôležité sú:

- domain expertise;
- cognitive load;
- communication paths;
- release autonomy;
- compliance separation;
- support model;
- platform maturity.

## 15. Migration patterns

### Modularize first

```text
identify capability
→ enforce code/data boundary
→ remove direct internal access
→ introduce explicit contract
→ measure change/failure/scale need
→ extract iba ak benefit pretrváva
```

### Strangler extraction

```text
route bounded operation/cohort
→ new service local authority
→ compatibility adapter/event sync
→ compare outcomes
→ increase exposure
→ retire old path
```

### Branch by abstraction

Callers prepnú na abstraction, za ktorou sa implementation postupne nahrádza. Umožňuje incremental migration a rollback bez permanentného dual write-u.

### Event-carried projection

Najprv sa extrahuje rebuildable read model, nie critical write invariant. Je to nižšie risk extraction.

Migration musí mať:

- exact generation;
- single authority;
- dual-write avoidance alebo reconciliation;
- cohort boundaries;
- rollback/roll-forward;
- data verification;
- old-path retirement.

## 16. Kedy zvoliť ktorý model

### Monolith je rozumný, keď

- tím je malý;
- domain boundaries sa menia;
- local transaction prináša veľkú hodnotu;
- scale/failure profile je podobný;
- platform/on-call capacity je obmedzená;
- independent deployment benefit nie je preukázaný.

### Modular monolith je rozumný, keď

- treba jasné domain/ownership boundaries;
- jeden deployment je stále efektívny;
- transactions naprieč niektorými modulmi sú legitímne;
- budúca extraction je možná, ale nie nutná;
- chcete testovať architecture boundaries bez distributed overheadu.

### Microservices sú rozumné, keď

- bounded capabilities sú stabilné;
- independent deployment/scale/failure isolation prináša merateľnú hodnotu;
- data ownership a cross-service workflow sú explicitné;
- team/platform vie prevádzkovať fleet;
- compatibility, observability a recovery mechanisms sú pripravené.

## 17. Connected incident `DB-PAY-57`

Pred release `payments 8.1` bol settlement modul súčasťou modular monolithu:

```text
merchant policy module
→ settlement module
→ atomic PostgreSQL settlement + outbox
→ provider worker
→ projection module
```

Extraction vytvorila:

```text
settlement-api
→ merchant-policy-service / MySQL
→ idempotency-service / Redis
→ ledger-service / PostgreSQL
→ provider-execution-service
→ projection-service
```

Deklarovaný cieľ bol independent scaling a ownership. Effective stav však mal:

- shared end-to-end on-call tím bez service-specific ownership;
- synchronous policy + idempotency + ledger chain;
- jeden business invariant rozdelený medzi tri services;
- Redis cache miss použitý ako authority decision;
- policy generation neprenesenú do settlement recordu;
- 96 Podov s independently configured pools;
- synchronized deployment kvôli shared DTO package-u;
- recovery runbook iba pre PostgreSQL, nie cross-service workflow.

Network flap a pool exhaustion boli trigger. Architecture amplifikovala incident:

```text
local scale decisions
→ fleet connection multiplication
→ emergency transaction pooling
→ session-state failure
→ stale/missing policy context
→ Redis dedupe ambiguity
→ cross-service retry
→ provider unknown outcomes
→ no common recovery point
```

### Architecture root cause

Primary architecture root cause bol **premature service extraction bez zachovania jedného authoritative settlement invariant-u, versionovaných contracts a operational/recovery ownershipu**.

Monolith nebol automaticky správny a microservices neboli automaticky chybné. Chyba bola, že runtime boundaries boli zavedené skôr než:

- domain/invariant boundaries;
- data authority;
- transaction/outbox workflow;
- product roles;
- independent compatibility;
- capacity budgets;
- on-call/recovery contracts.

## 18. Evidence-preserving containment

```text
freeze service/pool/retry changes
→ map exact call/data/ownership graph
→ identify one authority per business fact
→ preserve per-service logs, DB positions a message/provider evidence
→ stop duplicate retries
→ fence affected tenant cohort
→ route correctness decisions na PostgreSQL/provider authority
→ retain service generations for RCA
```

## 19. Authoritative redesign

Tím zvolil hybrid target:

### Modular command core

```text
settlement command + idempotency + outbox
→ one PostgreSQL local transaction
→ one owner/SLO/recovery boundary
```

### Separate services

- merchant policy zostáva versionovaný service; command request uloží exact policy generation;
- provider execution je asynchronous service consuming durable outbox/event;
- projection/reporting je independent rebuildable service;
- Redis je cache/admission accelerator, nie business authority.

### Compatibility a ownership

- contracts sú independently versionované;
- shared DTO package nie je synchronized-release gate;
- every service má explicitný owner, SLO, pool/capacity budget a runbook;
- end-to-end settlement capability má jedného incident/reconciliation ownera;
- recovery manifest mapuje PostgreSQL, MySQL, Redis a provider evidence.

Tento návrh nie je návrat k `jednému veľkému monolitu`. Zachováva local invariant tam, kde je atomicita najcennejšia, a oddeľuje capabilities, ktorých scale/failure/freshness model je skutočne iný.

## 20. Architecture acceptance verdict

Architecture je prijatá, keď:

- exact business capabilities a invarianty sú explicitné;
- module/service boundaries zodpovedajú coherent ownership;
- každý authoritative fact má jedného writera/ownera;
- local vs cross-boundary transaction model je mechanistický;
- sync/async communication má timeout, retry, delivery a recovery contract;
- deployment independence je preukázaná compatibility testom;
- scale model zahŕňa fleet-wide pools/retries/shared dependencies;
- failure isolation je testovaná, nie iba deklarovaná;
- observability, security, on-call, backup a recovery existujú per boundary;
- organizational capability unesie operational surface;
- migration drží single authority a bounded cohorts;
- expected architecture benefit je meraný proti reálnym costom;
- second change, partial rollout, dependency failure a restore prejdú;
- distributed-monolith a dual-authority forbidden outcomes sú odmietnuté.

## 21. Troubleshooting architecture failure-u

```text
slow delivery alebo runtime incident
→ exact capability/journey
→ source/build/deploy/process boundaries
→ data authority a invariant map
→ sync/async call graph
→ transaction a unknown-outcome path
→ shared dependency/resource multiplication
→ contract/release coupling
→ failure/ownership/recovery graph
→ intended benefit vs effective cost
→ modularize, merge, extract alebo redesign boundary
→ second-change/failure validation
```

## 22. Anti-patterny

### Microservices sú modernejšie

Modernosť nie je business alebo reliability requirement.

### Jeden service na entity

Entity boundary nemusí byť coherent capability alebo invariant boundary.

### Database per service = server per service

Authority boundary možno vynútiť aj logical database/schema/roles; physical isolation sa odvodzuje z risku.

### Shared database, ale services sú independent

Direct table access vytvára hidden deployment a ownership coupling.

### Všetko cez synchronous HTTP

Vytvára runtime monolith s network failure semantics.

### Všetko cez events

Command/query a immediate validation use cases môžu byť zbytočne komplikované; delivery a consistency costs nezmiznú.

### Modular monolith je dočasný neúspech

Môže byť dlhodobý optimal architecture outcome.

### Každý tím vlastný stack

Technology autonomy bez platform/operations capability násobí risk.

### Extraction bez retirementu

Old a new path vytvoria permanent dual authority.

## 23. Kontrolné otázky

1. Čo tvorí exact architecture subject?
2. Ako sa monolith líši od modular monolithu?
3. Ktoré boundaries microservice pridáva?
4. Prečo repository count neurčuje architecture?
5. Ako invariant boundary ovplyvňuje service boundary?
6. Čo znamená database per service?
7. Ako sa local transaction nahrádza cross-service workflowom?
8. Čo je distributed monolith?
9. Ako microservices násobia connection a retry demand?
10. Prečo `DB-PAY-57` nebol dôkazom, že microservices vždy zlyhajú?
11. Ktoré časti settlement flowu zostali alebo boli oddelené po redesign-e?
12. Čo musí overiť architecture acceptance verdict?

## Glossary impact

Relevantné pojmy: architecture subject, monolith, modular monolith, microservice, module boundary, service boundary, deployment boundary, failure boundary, database per service, distributed monolith, local transaction boundary, cross-service workflow, saga/process manager, service extraction, strangler pattern, branch by abstraction, architecture benefit verdict a architecture acceptance verdict.

## Primárne zdroje

- [Martin Fowler — Microservices](https://martinfowler.com/articles/microservices.html)
- [Martin Fowler — Monolith First](https://martinfowler.com/bliki/MonolithFirst.html)
- [AWS Prescriptive Guidance — Decomposing monoliths into microservices](https://docs.aws.amazon.com/prescriptive-guidance/latest/modernization-decomposing-monoliths/welcome.html)
- [Microsoft Azure Architecture Center — Microservices architecture style](https://learn.microsoft.com/azure/architecture/guide/architecture-styles/microservices)
