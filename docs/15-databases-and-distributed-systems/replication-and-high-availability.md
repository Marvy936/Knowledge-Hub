# Replication a high availability

Replikácia vytvára ďalšie copies alebo odvodené state-y. High availability používa tieto copies spolu s failure detection, promotion authority, writer fencing, routing a client convergence na obnovenie jednej authoritative služby. Samotná existencia replica preto nie je HA verdict a počet copies nie je automaticky durability guarantee.

```text
business availability a durability objective
→ exact replicated-data subject
→ replication topology a position semantics
→ commit acknowledgement policy
→ receive, flush, apply a visibility
→ read-routing a staleness contract
→ failure detection a promotion eligibility
→ old-writer fencing a new-writer authority
→ client convergence
→ business reconciliation a failback
→ second-failure validation
```

Kapitola sleduje jednu business operation od commit boundary cez replica positions až po failover a reconciliation. Tým oddeľuje process health od promotion eligibility, network connectivity od applied state-u a `COMMIT succeeded` od toho, čo môže prežiť stratu konkrétneho failure domain-u.

## 1. Exact replication a HA subject

Tvrdenie `máme primary a standby` je príliš slabé. Exact subject musí pomenovať business operation a acknowledged write set, cluster a timeline generation, primary a replica identities, physical alebo logical mechanismus, commit acknowledgement stage, receive/flush/apply positions, read-routing semantics, RPO/RTO, promotion authority, fencing, client convergence a corruption-recovery path.

Príklad pre `DB-PAY-56`:

```text
capability: create settlement intent
acknowledged write set: settlement + outbox transaction
primary: postgres-prod-euc1 generation 56
standby: postgres-prod-euw1 generation 56
replication: physical streaming, asynchronous
commit: local durable WAL flush
read-after-write: primary
regional RPO claim: zero acknowledged intents lost
promotion: failover controller
fencing: writer epoch + credential revocation + network isolation
```

Tento subject odhaľuje rozpor. Local-only asynchronous acknowledgement nemôže samo garantovať zero-loss regional RPO pri permanentnej strate primary pred prenosom WAL. Design musí zmeniť commit policy, failure-domain topology, reconstructability contract alebo samotný RPO claim.

## 2. Replica positions a visibility

Replication health sa má pozorovať cez explicitné positions, nie cez jedno zelené `connected` alebo `streaming`.

```text
primary vytvorí log position P
→ odošle P
→ replica prijme P
→ replica P durably flushne
→ replica P aplikuje
→ reader môže state z P vidieť
```

Receive, flush, replay a query visibility nie sú synonymá. Replica môže bytes prijať, ale nemať ich durable. Môže ich flushnúť, ale ešte neaplikovať. Môže ich aplikovať, ale konkrétny long-running snapshot ich ešte nevidí. Pri logical replication môže byť navyše jedna table alebo subscription zablokovaná, zatiaľ čo iné pokračujú.

Byte lag, time lag a business-operation lag tiež merajú odlišné veci. Malý byte gap môže obsahovať kritický acknowledged settlement. Veľký byte gap môže byť prevažne rebuildable index alebo batch data. Promotion gate preto potrebuje business-position mapping, nie iba počet megabajtov.

## 3. Commit acknowledgement a business RPO

Asynchronous replication umožní primary potvrdiť commit bez čakania na standby. Znižuje write latency a coupling, ale acknowledged writes môžu chýbať na promoted history. Synchronous replication čaká na definovaný počet replicas a stage, napríklad receive alebo durable flush. Zvyšuje acknowledged-write durability, no môže znížiť write availability a zvýšiť latency.

```text
business RPO
→ acknowledged business write set
→ required failure domains
→ required replica count
→ required acknowledgement stage
→ commit success
→ client acknowledgement
```

Slovo `synchronous` nestačí bez počtu replicas, failure domains a stage-u. Receive acknowledgement nie je to isté ako durable flush. Flush nie je to isté ako apply. Apply nie je automaticky business completion, ak operation pokračuje cez outbox, broker alebo providera.

Unknown commit outcome zostáva možný aj pri silnej replication policy. Databáza môže transaction commitnúť a response sa stratí. Application potrebuje stable operation identity, unique constraint, queryable outcome a safe retry/reconciliation. HA nerieši idempotency za klienta.

## 4. Read replicas a staleness contract

Read replica môže znížiť primary load alebo zlepšiť locality, ale mení semantics čítania. `SELECT` nie je automaticky bezpečný na ľubovoľnej replica. Authorization rozhodnutie, inventory decrement, workflow transition alebo status po práve potvrdenom write môže vyžadovať current authority.

Bezpečný read-routing contract určuje, ktoré operations tolerujú staleness, aký je maximum age alebo position gap a čo sa stane po write. Mechanizmy môžu používať primary reads pre authoritative decisions, session stickiness, minimum required LSN, monotonic-read token alebo explicitný `pending replication` user state.

```text
client write acknowledged at position P
→ následný read nesmie ísť na replica pod P
→ router/pool overí minimum position
→ current alebo explicitne stale outcome
```

Global `writes to primary, reads to replicas` je príliš hrubé pravidlo. Routing sa má viazať na operation class a consistency need.

## 5. Failure detection, promotion a fencing

Failover začína uncertainty, nie automaticky istotou, že primary je mŕtva. Missing heartbeat môže znamenať process failure, network partition, AZ isolation, control-plane outage alebo iba zlyhaný monitoring path. Network partition je nebezpečný, pretože old primary môže zostať alive a dostupná pre časť writers.

Promotion eligibility preto potrebuje compatible engine/schema/config generation, known data position, acceptable RPO gap, zdravé storage, current keys a network, dostatočnú capacity a schopnosť prevziať authoritative writer role. Najbližšia alebo najrýchlejšia replica nemusí byť najbezpečnejšia.

Pred prvým new write musí byť old writer effective fence-nutý. Request na stop instance nie je fencing verdict. Mechanizmus môže používať consensus term, lease alebo writer epoch, storage attachment authority, credential generation, proxy routing alebo network isolation. Dôležité je, aby old writer po promotion nemohol úspešne commitnúť ďalší authoritative write.

```text
failure suspicion
→ acquire recovery authority
→ prove candidate eligibility
→ increment writer term/epoch
→ revoke alebo isolate old writer
→ read back effective fence
→ promote candidate
→ admit new writes
```

Ak new writer prijíma writes pred effective fence, vzniká split brain a divergentné histories. Neskorší merge nie je bežný replication repair; je to business reconciliation medzi konkurenčnými authorities.

## 6. Client convergence a application RTO

Databáza môže byť promoted za sekundy, ale service môže zostať nedostupná, ak clients držia staré DNS records, dead pooled connections, stale service-discovery endpoints, incompatible prepared statements alebo credentials viazané na old role.

Client convergence contract zahŕňa DNS TTL a resolver behavior, proxy/LB update, pool lifetime a validation, transaction retry, TLS hostname, credentials a read-only session reset. RTO sa meria po obnovenie business operation, nie po log message `promotion complete`.

Po failover-e treba klasifikovať in-flight operations ako definitely aborted, committed and present, committed only on old history, unknown, retried alebo externally realized. Connection reset nie je business verdict. Stable idempotency key a provider/outbox evidence umožnia odlíšiť safe replay od duplicate side effectu.

## 7. Replikácia nie je backup ani corruption recovery

Replica verne kopíruje správne writes aj accidental deletes, malicious changes, schema mistakes a logical corruption. Replikácia poskytuje current alebo near-current availability copy. Backup a PITR poskytujú historical recovery points, retention a často oddelenú immutability boundary.

Pri physical failure môže byť current replica správny recovery candidate. Pri logical corruption môže byť rovnaká replica rovnako poškodená ako primary. HA plan preto musí odkazovať na samostatný clean-point a reconciliation contract, nie predpokladať, že ďalšia copy je vždy bezpečná.

## 8. Worked incident `DB-PAY-56`

Atlas používal PostgreSQL primary v `eu-central-1` a asynchronous standby v `eu-west-1`. Commit acknowledgement čakal iba na local WAL flush. Počas unindexed migration backfill-u vzniklo:

```text
WAL generation: 6.4× baseline
standby receive lag: 18 s
standby replay lag: 94 s
application timeout retries: 3.1×
```

O `10:14 UTC` AZ network failure oddelila primary od časti application a failover controllera. Primary však zostala alive a niektoré batch workers ju stále dosiahli. Controller o `10:19 UTC` promoted standby podľa process health a connection state-u, bez porovnania replay position s poslednými acknowledged business operations.

Old primary nebola effective fence-nutá a prijímala writes ďalších `93 sekúnd`. Connection pools konvergovali nerovnomerne. Výsledkom boli dve write histories, `286` operations vyžadujúcich reconciliation a `37` client-acknowledged intents chýbajúcich na promoted history. Document projection časť gapu skryla tým, že zobrazovala `accepted` bez authoritative outbox evidence.

Triggerom bola AZ network failure. Primary HA root cause bol promotion contract bez acknowledged-position gate-u a effective fencing. Durability mismatch vznikol tým, že local asynchronous commit policy nezodpovedala zero-loss RPO claimu. Migration WAL, retry load, stale projection a pomalá client convergence boli amplifiers.

## 9. Evidence, containment a recovery

Pri missing write po failover-e treba odlíšiť necommitnutú transaction, commitnutú a prítomnú transaction, commitnutú iba na old primary, received-but-not-applied log, stale reader, duplicate retry a external side effect bez local final state-u.

```text
business operation key
→ client attempt a acknowledgement
→ old-primary transaction a WAL position
→ standby receive/flush/replay position
→ promotion term a writer epoch
→ fencing read-back
→ DNS/proxy/pool route
→ outbox, broker a provider evidence
→ cohort reconciliation
```

Containment zastaví automatic failback a blind retries, fence-ne všetkých možných writers, zachová timelines, WAL a routing evidence a obmedzí nové writes na durable degraded mode. Divergentné histories sa nesmú zlievať podľa timestampu bez business manifestu.

Authoritative recovery vyberie jednu timeline podľa declared recovery authority a complete evidence. Potom klasifikuje `missing`, `never-sent`, `sent-unknown`, `completed` a duplicate-attempt cohorts, replayuje iba exact safe manifest, rebuildne projections a zmení commit policy alebo truthful RPO. Lag/position-aware promotion gate, writer epoch a client-convergence test musia prejsť pred ďalším automatic failoverom.

## 10. Acceptance paths

**Positive path** potvrdí business transaction, overí required replica flush stage a následne vykoná controlled switchover. New writer obsahuje acknowledged position, old writer je fence-nutý a clients konvergujú bez duplicate operation.

**Lag path** vytvorí WAL alebo apply pressure. Replica zostane connected, ale promotion gate ju správne označí za ineligible podľa business-position gapu. System buď počká, zvolí inú candidate alebo explicitne prijme degraded RPO.

**Partition path** izoluje control plane od primary, zatiaľ čo časť writers ju stále dosiahne. Recovery authority musí old writer effective fence-nuť pred new writes; inak test zlyhá ako split brain.

**Unknown-outcome path** stratí commit response počas role transition. Stable operation identity a reconciliation nájdu committed outcome alebo bezpečne vytvoria jediný intended result.

**Corruption path** replikuje logical error na standby. HA failover nesmie byť označený za recovery; plan vyberie clean historical point a vykoná business reconciliation.

**Second-failure path** testuje failover počas migration loadu a následnú stratu novej replica alebo controlled failback. Tým sa overí, že topology po prvom failover-e stále spĺňa redundancy a recovery contract.

## 11. Troubleshooting a anti-patterny

Diagnostika ide od exact cluster/timeline/operation subjectu cez roles, positions, commit policy, routing, promotion authority a fencing až po business reconciliation. Green process health bez position evidence nepodporuje promotion decision.

Typické anti-patterny sú `replica je healthy`, `synchronous znamená zero loss`, `read-only query môže ísť kamkoľvek`, promotion bez fencing-u, RTO merané pri database role change-i, replica používaná ako backup a automatic failback bez divergence analýzy. Každý z nich zamieňa jednu technickú vrstvu za complete business availability contract.

## 12. Kontrolné otázky

1. Aký je rozdiel medzi receive, flush, replay a query-visible position?
2. Ako sa commit acknowledgement mapuje na business RPO?
3. Prečo asynchronous standby nemôže automaticky garantovať zero-loss RPO?
4. Kedy read replica porušuje read-after-write alebo authorization semantics?
5. Čo tvorí promotion eligibility?
6. Prečo musí fencing prebehnúť pred new writes?
7. Ako DNS a connection pools ovplyvňujú application RTO?
8. Ako sa klasifikuje unknown transaction počas failover-u?
9. Prečo replikácia nenahrádza backup/PITR?
10. Ktoré causal boundaries vysvetľujú `DB-PAY-56`?
11. Čo musí odmietnuť partition path?
12. Prečo treba testovať second failure a failback?

## Glossary impact

Relevantné pojmy: replication subject, timeline generation, physical replication, logical replication, receive/flush/replay/visibility position, acknowledged-write RPO, synchronous acknowledgement stage, read-replica staleness contract, promotion eligibility, recovery authority, writer fencing, writer epoch, split brain, client convergence, divergent history, failback generation a second-failure validation.

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