# Replication a high availability

Replikácia vytvára ďalšie copies alebo odvodené logické state-y. High availability používa tieto copies, failure detection, promotion, routing a fencing na obnovenie služby. Samotná existencia replica preto nie je HA verdict a počet copies nie je durability guarantee.

```text
business availability a durability objective
→ exact replicated-data subject
→ replication topology a log/change stream
→ commit acknowledgement policy
→ transfer, flush, apply a visibility
→ lag a read-routing semantics
→ failure detection a promotion authority
→ writer fencing a client convergence
→ data/business reconciliation
→ failback a second-failure validation
```

## 1. Exact replication/HA subject

Subject má uvádzať:

- business capability a write/read operation;
- authoritative database, cluster a timeline generation;
- replicated tables/databases/partitions;
- physical alebo logical replication mechanismus;
- primary/leader a replica/follower identities;
- synchronous alebo asynchronous acknowledgement policy;
- transfer, durable-flush, apply a visibility positions;
- read routing a staleness tolerance;
- failure detector a promotion authority;
- fencing a split-brain prevention;
- client DNS/proxy/pool convergence;
- RPO, RTO a degraded-mode contract;
- backup/PITR a corruption-recovery path;
- failback a reconciliation plan.

Príklad:

```text
capability: create settlement intent
primary: postgres-prod-euc1 generation 56
standby: postgres-prod-euw1 generation 56
commit policy: local durable commit, asynchronous standby
acknowledged subject: settlement + outbox transaction
read routing: authoritative writes and read-after-write from primary
RPO target for regional failure: 0 acknowledged intents
RTO target: 45 min
fencing: one writer epoch managed by failover controller
```

Tento príklad obsahuje konflikt: local-only asynchronous acknowledgement nemusí vedieť garantovať zero-loss RPO pri permanentnej strate primary. Design musí objective alebo commit policy zmeniť.

## 2. Prečo replikovať

Replikácia môže slúžiť na:

- fast failover;
- read scaling;
- locality a lower read latency;
- rolling maintenance;
- migration alebo upgrade;
- analytical/change-data pipeline;
- disaster-recovery copy;
- backup/PITR input.

Jedna topology nemusí spĺňať všetky ciele. Read replica optimalizovaná na analytical queries môže mať veľký apply lag a nie je automaticky failover candidate. Synchronous local standby môže chrániť zonal failure, ale nemusí chrániť regional alebo account compromise.

## 3. Physical a logical replication

### Physical replication

Prenáša storage alebo write-ahead log changes na block/engine úrovni. Typicky zachováva celý cluster alebo database state a podporuje high-fidelity standby.

Výhody:

- rýchla a kompletná engine-level replica;
- vhodná pre failover;
- constraints, indexes a physical changes sa reprodukujú podľa engine mechanizmu.

Limity:

- často tesnejšia version/engine compatibility;
- menšia selektivita;
- logical corruption sa replikuje;
- target nie je nezávislý data model.

### Logical replication

Prenáša logické row/change operations alebo events.

Výhody:

- selective tables alebo schemas;
- migration medzi generations;
- odvodené consumers;
- transformations podľa product contractu.

Limity:

- nemusí prenášať všetky DDL, sequences alebo side state automaticky;
- ordering a transaction boundaries treba overiť;
- conflicts a unsupported changes môžu zastaviť apply;
- subscriber môže diverge-nuť.

Physical a logical replication nie sú vyššia a nižšia kvalita. Riešia odlišné subjects.

## 4. Replication positions

Replication treba pozorovať cez explicitné positions, nie iba status `healthy`.

```text
primary generates log position P
→ replica receives P
→ replica durably flushes P
→ replica applies P
→ replica exposes state from P
```

Dôležité rozdiely:

- **sent position** — primary odoslal log;
- **received/write position** — replica prijala bytes;
- **flush position** — replica ich durably uložila;
- **replay/apply position** — zmena bola aplikovaná;
- **query-visible position** — reader ju môže vidieť podľa snapshot/routing semantics.

Replica môže byť network-connected a stále výrazne zaostávať v apply. Byte lag, time lag a business-operation lag môžu ukazovať odlišný obraz.

## 5. Synchronous a asynchronous replication

### Asynchronous

Primary môže potvrdiť commit bez čakania na replica acknowledgement.

```text
local commit/flush
→ client acknowledgement
→ replica transfer neskôr
```

Výhody sú nižšia write latency a menšia dependency na standby. Rizikom je strata acknowledged writes pri permanentnej strate primary pred replikáciou.

### Synchronous

Commit čaká na definovaný standby/quorum stage, napríklad receive, durable flush alebo apply.

```text
local commit intent
→ replica acknowledgement podľa policy
→ commit success
→ client acknowledgement
```

Výhoda je silnejší acknowledged-write durability contract. Nevýhody sú vyššia latency a availability coupling. Ak required synchronous standby nie je dostupná, writes môžu čakať alebo zlyhať podľa policy.

`Synchronous` bez uvedenia počtu replicas a acknowledgement stage je neúplné tvrdenie.

## 6. Commit policy a business RPO

Business RPO sa musí mapovať na commit policy.

```text
RPO: zero lost acknowledged settlement intents
→ settlement + outbox atomic commit
→ acknowledgement waits for required durable failure-domain copies
→ failover selects replica containing acknowledged position
→ provider/reconciliation validates unknown edge cases
```

Ak primary potvrdzuje lokálne a standby je async, truthful contract môže byť:

- non-zero RPO pre catastrophic primary loss;
- durable admission iba po synchronous boundary;
- degraded write pause pri unavailable required replica;
- external reconstructability cez idempotency/provider ledger.

Marketingové `Multi-AZ` alebo `replicated` nenahrádza meraný acknowledgement contract.

## 7. Replication lag

Lag vzniká, keď generation rate prevyšuje transfer/apply capacity alebo replica nemôže aplikovať changes.

Príčiny:

- write spike alebo migration/backfill;
- slow network;
- replica CPU/storage saturation;
- long-running read conflicts;
- missing indexes na logical subscriber-i;
- large transactions;
- DDL alebo apply error;
- retention/slot pressure;
- paused replication;
- version/config mismatch.

Sleduj:

```text
primary generation rate
vs.
network receive rate
vs.
replica flush rate
vs.
replica apply rate
```

Jedna `replica lag seconds` metric môže používať heartbeat a nezachytiť absent traffic alebo stalled business cohort.

## 8. Read replicas a stale reads

Read replica môže znížiť primary load, ale mení read semantics.

Riziká:

- read-after-write vráti starý state;
- session preskočí medzi replicas s odlišným position;
- projection alebo UI ukáže predchádzajúci status;
- lag nie je rovnaký pre všetky tables/partitions;
- failover mení writer aj freshness boundary.

Patterns:

- authoritative reads z primary;
- session stickiness;
- minimum required LSN/position;
- bounded-staleness contract;
- monotonic-read token;
- explicit `pending replication` user state;
- route podľa operation, nie global read/write split.

`SELECT` nie je automaticky safe na stale replica. Authorization, inventory decrement alebo operation-status rozhodnutie môže vyžadovať current authority.

## 9. Failure detection

Failover začína detection verdictom:

```text
missing heartbeat alebo failed health
→ distinguish process/network/zone/control-plane failure
→ quorum/witness evidence
→ declare primary ineligible
→ acquire recovery authority
→ fence old writer
→ promote eligible replica
```

Príliš citlivý detector vytvára false failovers. Príliš pomalý predlžuje outage. Network partition je najťažší scenár, pretože old primary môže byť stále alive, ale unreachable pre časť systému.

## 10. Promotion eligibility

Nie každá replica je bezpečný promotion candidate. Eligibility potrebuje:

- compatible engine/schema/config generation;
- complete required data subject;
- known flush/apply position;
- acceptable RPO gap;
- healthy storage a recovery state;
- current credentials/keys/network;
- sufficient capacity;
- no unresolved apply error;
- ability stať sa authoritative writer;
- reconciliation plan pre missing/unknown writes.

Automatická voľba najbližšej alebo najrýchlejšej replica bez data-position verdictu môže zhoršiť incident.

## 11. Fencing a split brain

Promotion bez fencing môže vytvoriť viac writers.

```text
network partition
→ controller promotes standby
→ old primary stále prijíma writes
→ two divergent histories
```

Fencing mechanisms môžu zahŕňať:

- lease/epoch term;
- quorum/consensus leadership;
- storage-level exclusive attachment;
- network isolation;
- cloud instance stop/fence;
- credential/token generation;
- proxy routing with writer generation;
- application-level write epoch.

Fencing musí byť effective, nie iba request na vypnutie old primary. Reader a downstream consumers tiež musia vedieť, ktorá history je authoritative.

## 12. Client convergence

Po promotion sa musia clients pripojiť k novému writerovi.

Hranice:

- DNS TTL a resolver cache;
- connection-pool lifetime;
- proxy/load-balancer health;
- stale service discovery;
- TLS certificate/hostname;
- credentials a role grants;
- read-only session state;
- prepared statements a transaction retries.

Databáza môže byť promoted za sekundy, no application RTO môže byť minúty až hodiny, ak pools držia dead connections alebo clients stále smerujú na old endpoint.

## 13. Failover transaction outcomes

Transactions počas failover-u môžu byť:

- definitely aborted;
- definitely committed and present on promoted replica;
- committed on old primary but missing on new primary;
- unknown pre clienta;
- retried a duplicate;
- partially realized v external systems.

Každá business operation potrebuje stable identity a reconciliation. `Connection reset` nie je dostatočný outcome.

## 14. Replication nie je backup

Replica faithfully kopíruje:

- správne writes;
- accidental deletes;
- application corruption;
- compromised admin changes;
- destructive migrations.

Backup/PITR poskytuje historical recovery points a oddelenú retention/immutability boundary. Replikácia poskytuje current alebo near-current availability copy. Obe treba testovať.

## 15. Rolling maintenance a mixed generations

HA topology často umožňuje maintenance:

```text
upgrade replica
→ catch up
→ validate
→ switchover
→ upgrade old primary
→ restore redundancy
```

Treba overiť:

- version compatibility;
- replication protocol;
- schema/app compatibility;
- rollback eligibility;
- mixed-version duration;
- failover počas maintenance;
- replica identity a monitoring;
- old-generation retirement.

Switchover je planned role change. Failover je response na failure alebo ineligibility. Oba potrebujú fencing a client convergence.

## 16. Worked incident `DB-PAY-56`

Atlas PostgreSQL topology používala primary v `eu-central-1` a asynchronous standby v `eu-west-1`. Commit acknowledgement čakal iba na local WAL flush.

Počas unindexed migration backfill-u:

```text
WAL generation: 6.4× baseline
standby receive lag: 18 s
standby replay lag: 94 s
application timeout retries: 3.1×
```

O `10:14 UTC` AZ network failure oddelila primary od application a failover controllera. Primary databáza však zostala alive a časť batch workerov v rovnakom network segmente ju stále dosiahla.

Failover controller o `10:19 UTC` promoted standby na základe process health a receive connection, bez exact flush/replay position porovnania s poslednými acknowledged business operations.

Dôsledky:

- promoted standby chýbala časť acknowledged settlement/outbox transactions;
- old primary prijímala writes ďalších 93 sekúnd;
- application pools konvergovali na nový endpoint nerovnomerne;
- vznikli dve divergentné write histories;
- document projection skryla časť missing relational state-u;
- `286` merchant operations potrebovalo reconciliation;
- `37` intents bolo potvrdených clientovi, ale nebolo na promoted history;
- provider ledger zabránil niektorým duplicates, no `sent-unknown` cohort zostal.

### Trigger, root cause a amplifiers

- **Trigger:** AZ network failure.
- **Primary HA root cause:** promotion contract neviazal eligibility na acknowledged business position a nevyžadoval effective fencing old writer-a.
- **Durability mismatch:** local asynchronous commit policy nezodpovedala deklarovanému zero-loss RPO.
- **Capacity amplifier:** migration WAL spôsobila large apply lag.
- **Client amplifier:** connection pools a DNS nemali generation-aware convergence.
- **Data-model amplifier:** read projection ukazovala accepted state bez authoritative outbox evidence.

## 17. Competing hypotheses a discriminating evidence

Pri missing writes po failover-e treba odlíšiť:

1. transaction nikdy necommitla;
2. commitla a je na promoted replica, reader je stale;
3. commitla na old primary, nebola replikovaná;
4. replica received, ale neflushla/aplikovala;
5. application retry vytvoril duplicate identity;
6. old primary pokračovala vo writes;
7. document/cache skryli authoritative gap;
8. external provider má side effect bez local final state-u.

Evidence:

```text
business operation/idempotency key
→ client attempt a response
→ primary transaction/WAL commit LSN
→ standby receive/flush/replay LSN
→ promotion timeline/term
→ fencing evidence
→ old/new primary rows and timelines
→ DNS/proxy/pool routing
→ outbox/broker/provider ledger
→ reconciliation verdict
```

## 18. Evidence-preserving containment

```text
zastaviť automatic failback a blind retries
→ fence oba possible writers podľa explicitnej authority
→ preserve WAL/timelines/promotion/routing evidence
→ pause destructive migration
→ restrict new writes alebo enter durable degraded mode
→ inventory acknowledged operations around failover window
→ classify histories and external effects
→ establish one authoritative writer generation
```

Nesnaž sa okamžite merge-nuť divergentné histories bez business manifestu.

## 19. Authoritative recovery

1. vybrať authoritative timeline podľa declared recovery authority a complete evidence;
2. fence old primary a revoke old writer credentials;
3. porovnať acknowledged operations s promoted database, old primary, outbox a provider ledgerom;
4. klasifikovať `missing`, `never-sent`, `sent-unknown`, `completed` a `duplicate-attempt` cohorts;
5. replayovať iba exact safe manifest;
6. rebuildnúť projections z authoritative streamu;
7. zaviesť writer epoch do application writes a events;
8. zmeniť commit/replication policy alebo truthful RPO;
9. pridať lag/position-aware promotion gate;
10. testovať client convergence, failover pod migration loadom a second failover.

## 20. Replication/HA acceptance verdict

Topology je prijatá, keď:

- exact replicated subject a failure scenarios sú explicitné;
- physical/logical mechanismus zodpovedá use case-u;
- transfer/flush/apply/visibility positions sú observable;
- commit acknowledgement zodpovedá business RPO;
- lag má capacity, alert a abort contract;
- read routing má explicitnú staleness semantics;
- promotion eligibility kontroluje generation, position a capacity;
- old writer je effective fence-nutý pred new writes;
- clients konvergujú v RTO vrátane pools/DNS/proxy;
- unknown failover outcomes majú idempotency a reconciliation;
- backup/PITR rieši logical corruption;
- failback je samostatne rehearsed;
- zonal, regional, network-partition a second-failure tests prejdú;
- forbidden stale-read, lost-acknowledged-write a split-brain outcomes zlyhajú.

## 21. Troubleshooting flow

```text
replica lag, stale read alebo failover inconsistency
→ exact cluster/timeline/operation subject
→ primary and replica roles/generations
→ sent/receive/flush/replay/visible positions
→ generation vs apply capacity
→ commit acknowledgement policy
→ read/client routing
→ failure detector/promotion authority
→ fencing and divergent histories
→ business/external reconciliation
→ second failover and failback validation
```

## 22. Anti-patterny

### Replica je healthy

Bez position, lag a data-subject evidence to nič nehovorí o promotion eligibility.

### Asynchronous je vždy rýchlejšie a dosť dobré

Môže byť správne, ale business musí akceptovať RPO alebo mať reconstructability.

### Synchronous znamená zero loss

Záleží na počte replicas, failure domains a receive/flush/apply stage-i.

### Read-only query môže ísť na ľubovoľnú replica

Read môže rozhodovať o authoritative state alebo vyžadovať read-after-write.

### Promotion vyriešila HA

Bez fencing a client convergence môže vzniknúť split brain alebo pokračujúci outage.

### Replikácia je backup

Logical corruption sa replikuje.

### Failback je reverse failover

Divergence, capacity a current authority z neho robia samostatnú risky transition.

## 23. Kontrolné otázky

1. Čo tvorí exact replication/HA subject?
2. Ako sa physical a logical replication líšia?
3. Aký je rozdiel medzi receive, flush, replay a visibility position?
4. Ako synchronous a asynchronous commit menia RPO a latency?
5. Čo spôsobuje replication lag?
6. Kedy je stale read neprijateľný?
7. Čo tvorí promotion eligibility?
8. Prečo je fencing povinný?
9. Ako client convergence ovplyvňuje RTO?
10. Prečo `DB-PAY-56` stratilo acknowledged writes?
11. Prečo replica nenahrádza backup?
12. Čo overuje replication/HA acceptance verdict?

## Glossary impact

Relevantné pojmy: replication subject, physical replication, logical replication, replication position, receive/flush/replay lag, synchronous replication, asynchronous replication, acknowledged-write RPO, read-replica staleness, promotion eligibility, recovery authority, writer fencing, split brain, writer epoch, client convergence, failback generation a replication/HA acceptance verdict.

## Primárne zdroje

- [PostgreSQL Documentation — High Availability, Load Balancing, and Replication](https://www.postgresql.org/docs/current/high-availability.html)
- [PostgreSQL Documentation — Log-Shipping Standby Servers](https://www.postgresql.org/docs/current/warm-standby.html)
- [PostgreSQL Documentation — Replication Configuration](https://www.postgresql.org/docs/current/runtime-config-replication.html)
- [MongoDB Manual — Replication](https://www.mongodb.com/docs/manual/replication/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Indexy, locks a migrations](indexes-locks-and-migrations.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Backups a point-in-time recovery →](backups-and-point-in-time-recovery.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
