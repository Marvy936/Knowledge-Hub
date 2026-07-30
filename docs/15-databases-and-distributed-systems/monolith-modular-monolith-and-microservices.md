# Monolith, modular monolith a microservices

Monolith, modular monolith a microservices nie sú maturity levels, cez ktoré musí každá aplikácia povinne prejsť. Sú to rozdielne boundaries pre build, deployment, process failure, data authority, transactions, communication, scaling, ownership a recovery. Správna architecture minimalizuje coordination cost a distributed failure surface bez toho, aby rozdelila business invariant na viac nezávislých writers.

```text
business capability a invariant
→ exact architecture subject
→ module/service a data authority boundaries
→ local alebo cross-boundary transaction model
→ communication a compatibility protocol
→ deployment, scale a failure isolation
→ ownership, SLO, on-call a recovery
→ migration s single authority
→ intended benefit vs effective cost
→ second-change, dependency-failure a restore validation
```

Počet repositories, Kubernetes Deployments alebo databases sám neurčuje architecture. Desať independently deployed services nad jednou shared database a synchronized release-om môže byť distributed monolith. Jeden artifact môže byť dobre modularizovaný, horizontally scaled a spoľahlivo prevádzkovaný.

## 1. Architecture subject a rozhodovacie hranice

Exact architecture subject musí pomenovať business capabilities a critical journeys, domain a invariant boundaries, team ownership a change coupling, source/build/deploy/process boundaries, authoritative data ownership, transaction a consistency model, synchronous a asynchronous paths, scale a failure profiles, release compatibility, observability, security, on-call, recovery a očakávaný merateľný benefit.

Pre settlement capability je rozhodujúci invariant:

```text
one merchant operation
→ at most one authoritative settlement intent
→ exactly one durable outbox command for accepted transition
→ provider outcome reconciled to that same identity
```

Tento invariant prirodzene patrí do jednej local transaction a ownership boundary. Merchant policy, provider execution a reporting môžu mať odlišné scale alebo freshness profily, ale ich oddelenie je bezpečné iba vtedy, keď command core uchová exact policy generation, durable event identity a unknown-outcome state.

Architecture style je teda outcome konkrétnych boundaries. Source repository, build artifact, deployment, process, database a team boundary sa môžu prekrývať, ale nemusia byť totožné.

## 2. Monolith a jeho skutočný contract

Monolith buildí a deployuje významnú časť systému ako jeden artifact alebo runtime unit:

```text
source change
→ one build/artifact
→ one deployment generation
→ in-process calls
→ shared process/resources
→ local data transaction
→ coordinated rollback/recovery
```

Jeho výhodou je jednoduchší local development, debugging a deployment; in-process calls nemajú network timeout a partial-failure semantics; invariant-heavy operations môžu používať jednu database transaction; platforma spravuje menej identities, certificates, routes, dashboards, pools a runbooks. Je vhodný pre menší tím, meniace sa domain boundaries a podobný scale/failure profil.

Cena je coordinated release, shared process failure a resource contention, hrubšie scaling, rastúci build/test cycle, slabé ownership a jednoduché obchádzanie internal boundaries. Monolith nie je synonymum single instance ani legacy code. Jeden artifact môže mať veľa replicas, HA, queues a caches. Problémom nie je deployment unit, ale coupling, ktorý organizácia nevie kontrolovať.

## 3. Modular monolith ako enforce-nutá boundary

Modular monolith zachováva jeden deployment/process, ale capability boundaries vynucuje v source a data access modeli:

```text
business capability
→ module public contract
→ private implementation a tables
→ explicit dependency direction
→ in-process command/event
→ one deployment generation
```

Module potrebuje jasný purpose, public API, private model, controlled dependencies, owned schema alebo role-based access boundary, architecture tests a explicitné transaction assumptions. Priame SQL alebo shared ORM entity naprieč modulmi boundary ruší, aj keď diagram tvrdí opak.

Modular monolith zachováva local transactions tam, kde majú vysokú hodnotu, a zároveň umožňuje team ownership a budúcu extraction. Je lacnejšie presúvať hranice v jednom codebase než meniť remote API, multiple data histories a fleet operations. Zostáva však shared failure a deployment boundary; nejde o predstieranú microservice autonomy.

Dlhodobý modular monolith môže byť optimálny výsledok. Extraction má prísť až vtedy, keď independent deployment, scale, compliance alebo failure isolation prináša merateľnú hodnotu vyššiu než distributed overhead.

## 4. Microservices a povinný distributed contract

Microservice vlastní coherent business capability, deployuje sa independentne a má explicitnú runtime, data a operational boundary:

```text
service-owned capability
→ versioned API/event contract
→ network alebo broker transport
→ service-owned authoritative state
→ local transaction
→ durable cross-service workflow
→ independent failure/recovery
```

Potenciálny benefit je independent release cadence, scale, failure isolation, technology fit a end-to-end team ownership. Tieto benefity nie sú zadarmo. Service pridáva latency, timeout, retry a unknown outcomes; identity, TLS a authorization; discovery a routing; API/event compatibility; tracing a log correlation; per-service capacity, SLO, on-call, backup a runbooks; data projections, backlog, replay a reconciliation.

Microservice nie je malá trieda vystavená cez HTTP. Boundary má byť stabilná capability s vlastnou authority a operational ownerom. Ak dve services vždy musia commitovať, deployovať a obnovovať spolu, decomposition pravdepodobne neoddelila reálnu capability.

## 5. Data authority a transaction model

Shared database môže zjednodušiť joins a transactions, ale direct table access vytvára hidden coupling. `Database per service` neznamená server per service. Znamená, že authoritative state sa mení iba cez service contract. Physical realization môže byť separate cluster, database alebo schema s enforced roles podľa isolation risku.

Derived projection má samostatnú semantics:

```text
source service authoritative event
→ durable delivery
→ consumer local transaction
→ projection generation
→ freshness a completeness evidence
→ rebuild/reconciliation path
```

Projection absence alebo staleness nesmie meniť source write outcome bez explicitného degraded contractu.

Monolith alebo modular monolith môže chrániť invariant local transaction. Cross-service workflow potrebuje local commit per service, outbox/inbox, stable identity, idempotency, durable delivery, saga alebo process manager, compensation a reconciliation.

```text
local authority commit
→ durable outbox event
→ delivery attempt
→ consumer local commit
→ acknowledgement
→ workflow state
→ timeout, retry, compensation alebo reconciliation
```

Tento mechanismus nie je automaticky horší, ale je drahší a musí priniesť reálny boundary benefit. Rozdeliť settlement a outbox do dvoch services len preto, že `eventing má byť samostatná služba`, vytvorí distributed invariant bez užitočnej isolation.

## 6. Communication, deployment a scale coupling

Synchronous call poskytuje immediate response, ale vytvára runtime availability a latency coupling. Caller potrebuje deadline, bounded retry a unknown-outcome semantics. Chain piatich synchronous services môže byť tesnejší runtime monolith než in-process modular application.

Asynchronous communication poskytuje temporal decoupling, buffering a durable workflow evidence. Cena sú duplicates, ordering, backlog, schema evolution, delayed failure visibility a reconciliation. `Všetko cez events` je rovnaký anti-pattern ako `všetko cez HTTP`; transport sa vyberá podľa operation contractu.

Independent deployment existuje iba vtedy, keď old/new provider a consumer generations zostanú compatible počas staged rollout-u a rollbacku. Shared DTO package, synchronized migrations alebo direct database reads môžu vytvoriť distributed deployment monolith.

Microservices tiež násobia resources:

```text
services × replicas × per-replica pools/retries/buffers
→ database, broker, cache a provider demand
```

Každý service môže byť lokálne „správne“ nastavený a fleet napriek tomu prekročí shared dependency envelope. Capacity a retry budget preto musia byť capability-wide.

## 7. Failure isolation a organizational capability

Service boundary izoluje iba failures, ktoré neprechádzajú cez shared dependencies a retry paths. Spoločná overloaded database, central Redis authority, synchronous call chain, shared identity/control plane alebo common library rollout môžu zlyhanie rozšíriť cez celý fleet.

Failure isolation sa dokazuje controlled dependency-failure a partial-rollout testom. `Beží v inom Pode` nie je evidence.

Každý independently operated service potrebuje ownera, SLI/SLO, capacity, dashboards, alerts, traces, on-call, runbooks, backup/recovery, security lifecycle a compatibility inventory. Capability zároveň potrebuje jedného end-to-end ownera pre incident command a reconciliation. Model `dev owns code, DBA database, platform deploy a ops incident` bez spoločnej authority vytvára queues a ownership gaps.

Organizácia, ktorá nevie bezpečne prevádzkovať desať services, nezíska autonomy len tým, že monolith rozdelí. Platform maturity, cognitive load a support capacity sú architecture constraints rovnako ako latency a transaction semantics.

## 8. Connected incident `DB-PAY-57`

Pred release `payments 8.1` bol settlement command súčasťou modular monolithu:

```text
merchant-policy module
→ settlement + idempotency + outbox transaction
→ provider worker
→ projection module
```

Extraction vytvorila synchronous chain cez merchant-policy-service/MySQL, idempotency-service/Redis, ledger-service/PostgreSQL a provider-execution-service. Deklarovaným cieľom bolo independent scaling a ownership. Effective state však používal shared on-call tím, synchronized release cez shared DTO package, jeden invariant rozdelený medzi tri services, Redis cache miss ako authority decision, 96 independently tuned connection pools a recovery runbook iba pre PostgreSQL.

Network flap a pool exhaustion spustili:

```text
fleet connection multiplication
→ emergency transaction pooling
→ session tenant-state failure
→ stale/missing policy context
→ Redis dedupe ambiguity
→ cross-service retries
→ provider unknown outcomes
→ no common recovery point
```

Primary architecture root cause bola premature service extraction bez zachovania authoritative settlement invariant-u, versionovaných contracts a operational/recovery ownershipu. Monolith nebol automaticky správny a microservices neboli automaticky chybné; runtime boundaries vznikli skôr než domain authority, workflow, capacity a recovery contract.

## 9. Redesign, migration a acceptance paths

Tím zvolil hybrid target. Settlement command, idempotency operation a outbox zostali v modular command core s jednou PostgreSQL transaction, ownerom a recovery boundary. Merchant policy zostal samostatný versioned service; každý accepted command ukladá exact policy generation. Provider execution konzumuje durable outbox event asynchronous spôsobom. Projection/reporting zostáva rebuildable service. Redis je cache a admission accelerator, nie final authority.

Migration používa `modularize first`: enforce code/data boundary, odstrániť direct internal access, zaviesť explicitný contract a až potom extrahovať bounded cohort. Strangler alebo branch-by-abstraction postup drží jedného authoritative writera; old path sa po convergence musí retire-nuť.

**Positive path** preukáže independent change v policy alebo projection service bez synchronized release a bez zmeny settlement invariant-u.

**Recovery path** znefunkční policy, provider alebo projection dependency. Command core buď používa current bounded policy evidence, alebo vstúpi do explicitného pending/degraded state-u; acknowledged intent zostane durable a workflow sa po recovery reconciliuje.

**Failure path** pri incompatible contracte, unavailable authority alebo exhausted shared dependency zastaví affected cohort a zachová exact operation state namiesto cascading retries.

**Forbidden path** odmietne direct cross-service table writes, dual authority počas extraction, synchronized deployment vydávaný za independence, cache miss ako business decision a service bez ownera/SLO/recovery pathu.

Acceptance vyžaduje second change, partial rollout, dependency failure, fleet-scale test a restore. Intended benefit — napríklad faster independent releases alebo isolated provider scaling — sa porovnáva s reálnou latency, incident a operational cost.

## 10. Troubleshooting a anti-patterny

Pri delivery alebo runtime probléme sa mapuje exact capability, source/build/deploy/process boundaries, data authority, synchronous a asynchronous graph, local a cross-service transactions, shared dependency multiplication, contract coupling, ownership a recovery. Až potom sa rozhoduje, či boundary modularizovať, zlúčiť, extrahovať alebo redesignovať.

Najčastejšie anti-patterny sú microservices ako symbol modernosti, service per entity, database per service interpretovaná ako server per service, shared database s direct accessom, všetko cez HTTP, všetko cez events, modular monolith ako dočasný neúspech, technology autonomy bez platform capacity a extraction bez retirementu old pathu.

## 11. Kontrolné otázky

1. Ktoré boundaries tvoria exact architecture subject?
2. Ako sa monolith líši od modular monolithu?
3. Čo musí microservice vlastniť okrem code a deploymentu?
4. Prečo repository alebo Pod count neurčuje architecture style?
5. Ako business invariant ovplyvňuje service boundary?
6. Čo znamená database per service a čo neznamená?
7. Ako local transaction prechádza na durable cross-service workflow?
8. Čo je distributed monolith?
9. Ako services násobia pools, retries a shared dependency demand?
10. Ktoré positive, recovery, failure a forbidden paths musia prejsť?

## Glossary impact

Relevantné pojmy: architecture subject, monolith, modular monolith, microservice, module boundary, service boundary, deployment boundary, failure boundary, database per service, distributed monolith, local transaction boundary, cross-service workflow, saga/process manager, service extraction, strangler pattern, branch by abstraction, architecture benefit verdict a architecture acceptance verdict.

## Primárne zdroje

- [Martin Fowler — Microservices](https://martinfowler.com/articles/microservices.html)
- [Martin Fowler — Monolith First](https://martinfowler.com/bliki/MonolithFirst.html)
- [AWS Prescriptive Guidance — Decomposing monoliths into microservices](https://docs.aws.amazon.com/prescriptive-guidance/latest/modernization-decomposing-monoliths/welcome.html)
- [Microsoft Azure Architecture Center — Microservices architecture style](https://learn.microsoft.com/azure/architecture/guide/architecture-styles/microservices)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: PostgreSQL, MySQL a Redis](postgresql-mysql-and-redis.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Synchronous vs. asynchronous communication →](synchronous-vs-asynchronous-communication.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
