# Reliability, availability a durability

Reliability nie je synonymum pre `server beží`. Je to schopnosť systému plniť požadovanú funkciu za definovaných podmienok a počas definovaného obdobia. Availability opisuje, či možno službu alebo operáciu použiť vtedy, keď ju používateľ potrebuje. Durability opisuje, či už prijatý a potvrdený stav zostane zachovaný a obnoviteľný napriek zlyhaniam.

Tieto vlastnosti sa prekrývajú, ale nie sú zameniteľné. API môže byť dostupné a pritom vracať nesprávny výsledok. Databáza môže byť dočasne nedostupná, ale všetky potvrdené dáta zostanú durable. Systém môže mať zdravé procesy a infraštruktúru, no zlyhať v end-to-end business journey.

```text
business capability a user expectation
→ exact reliability subject a conditions
→ required function a success boundary
→ availability, correctness, latency a durability properties
→ failure opportunities a measurement population
→ observed effective behavior
→ impact a recovery
→ allowed, forbidden a residual-risk validation
```

## 1. Exact reliability subject

Tvrdenie `payments sú reliable` je príliš neurčité. Reliability subject musí uvádzať najmenej:

- konkrétnu business operation alebo journey;
- actor alebo traffic cohort;
- vstupné a výstupné conditions;
- environment, Region a release generation;
- časový interval alebo počet opportunities;
- požadovaný outcome;
- dependencies zahrnuté v end-to-end boundary;
- acknowledgement boundary;
- data a recovery subject;
- spôsob merania a evidence authority.

Príklad subjectu:

```text
operation: submit settlement
cohort: valid production merchant requests
service: atlas-settlement-api
release: 7.25.0
region: eu-central-1
period: rolling 28 days
success: accepted settlement completes exactly once within 10 minutes
ack boundary: HTTP 202 after PostgreSQL payment + outbox commit
recovery requirement: every acknowledged intent remains reconstructable for 90 days
```

Ak sa zmení operation, cohort, release, Region, časové okno alebo acknowledgement semantics, mení sa analyzovaný subject. Priemerná hodnota cez nezlučiteľné subjects môže skryť závažné zlyhanie.

## 2. Reliability

Reliability možno chápať ako pravdepodobnosť, že systém vykoná požadovanú funkciu bez failure-u za stated conditions a počas stated period. Prakticky to znamená, že treba pomenovať:

1. **Required function** — čo má systém reálne dokončiť.
2. **Stated conditions** — traffic, dependency state, data shape, failure assumptions a environment.
3. **Period alebo opportunities** — počas akého času alebo koľkých operácií sa vlastnosť hodnotí.
4. **Failure definition** — ktoré outcomes sú nesprávne, oneskorené, duplicitné alebo stratené.

Reliability je širšia než availability. Môže zahŕňať:

- dostupnosť operácie;
- správnosť výsledku;
- bounded latency;
- data integrity a durability;
- exactly-once alebo at-least-once business semantics;
- recovery behavior;
- bezpečné degraded modes.

Reliability nie je automaticky súčinom niekoľkých percent. Dependencies a failure modes bývajú korelované. Jedna chybná release generation môže súčasne narušiť availability, correctness aj durability.

## 3. Availability

Availability odpovedá na otázku, či je požadovaná service capability použiteľná v potrebnom čase. Dva bežné modely sú:

### Time-based availability

```text
availability = usable time / total eligible time
```

Je vhodná pre capability, ktorá má byť kontinuálne dostupná, napríklad administratívny portal alebo database endpoint. Musí však definovať:

- observation point;
- eligible service window;
- planned-maintenance semantics;
- partial degradation;
- regional alebo tenant scope;
- čo znamená `usable`.

### Event-based alebo request-based availability

```text
availability = good eligible events / total eligible events
```

Je vhodná pre request-driven služby. Lepšie zachytáva partial failures a rozdielny traffic v čase. Potrebuje presnú klasifikáciu:

- validných a invalidných requests;
- success a failure outcomes;
- retries;
- duplicate attempts;
- client-aborted requests;
- load-shed a rate-limited operations;
- requests, ktoré sa k measurement pointu vôbec nedostali.

HTTP `2xx` nie je automaticky good event. `202 Accepted` môže byť správny iba vtedy, ak downstream contract garantuje durable prijatie, sledovateľný stav a dokončenie alebo explicitný final failure.

## 4. Partial availability a user cohorts

Služba nemusí byť iba `up` alebo `down`. Môže zlyhávať:

- iba pre jednu Region alebo Availability Zone;
- iba pre nový release cohort;
- iba pre určitý tenant;
- iba pre write operations;
- iba pri konkrétnom payload type;
- iba v jednom downstream path-e;
- iba nad určitou latency hranicou.

Aggregate availability cez celý systém môže zostať zelená, hoci kritický cohort je úplne nefunkčný. Preto availability subject často potrebuje segmentáciu podľa user journey, operation, tenant, Region, platform alebo release generation.

## 5. Durability

Durability je pravdepodobnosť, že potvrdený data alebo state subject zostane zachovaný počas definovaného intervalu. Neznamená iba, že existuje viac storage copies.

Durability contract musí uviesť:

- ktoré bytes alebo business facts sú chránené;
- kedy systém tvrdí, že write je committed alebo acknowledged;
- ktoré copies a logs vstupujú do durability modelu;
- consistency medzi súvisiacimi records;
- retention a deletion semantics;
- ochranu pred logical corruption a malicious mutation;
- backup a restore coverage;
- encryption-key dependency;
- spôsob preukázania reconstructability.

```text
business intent
→ write set a transaction boundary
→ commit/acknowledgement
→ replicated alebo journaled state
→ retention a mutation lifecycle
→ backup/restore lineage
→ reconstructed business fact
→ application a business validation
```

Storage replication chráni najmä pred physical failure-om. Nechráni automaticky pred:

- chybným `DELETE` alebo retention jobom;
- application corruption;
- kompromitovaným privileged principalom;
- replikovanou nesprávnou zmenou;
- chýbajúcou dependent record;
- neplatným encryption keyom;
- backupom, ktorý nemožno obnoviť;
- obnovou technických bytes bez business consistency.

## 6. Acknowledgement boundary

Najdôležitejšia durability otázka je: **čo presne systém sľúbil v okamihu acknowledgementu?**

Príklad:

```text
HTTP 202
→ payment row aj outbox command sú committed v jednej PostgreSQL transaction
→ command môže byť neskôr publishnutý
→ caller môže bezpečne opakovať request s rovnakým idempotency keyom
```

Ak API vráti `202` pred durable commitom, môže po process failure stratiť prijatý intent. Ak commit prebehne, ale response sa stratí, vzniká unknown outcome a retry musí byť idempotentný. Ak payment row prežije, ale outbox command sa stratí, business intent nie je complete, hoci časť dát zostala durable.

## 7. Availability nie je durability

Tieto scenáre sú odlišné:

| Stav | Availability | Durability |
|---|---|---|
| API je nedostupné, no potvrdené dáta zostali zachované | zlá | dobrá |
| API odpovedá, ale potvrdené writes sa po crashi stratia | zdanlivo dobrá | zlá |
| Read-only degraded mode sprístupní existujúce dáta | čiastočná | môže byť dobrá |
| Backup existuje, ale restore nevie obnoviť konzistentný system | runtime môže byť dobrý | nepreukázaná |
| Všetky replicas okamžite replikujú chybný delete | krátkodobo dobrá | business durability zlá |

Reliability design preto potrebuje oddelené indicators a recovery tests. Jedna `uptime` metric nemôže reprezentovať všetky tri vlastnosti.

## 8. Connected failure `SRE-PAY-52`

Atlas Payments používa transactional outbox:

```text
merchant request
→ atlas-settlement-api
→ PostgreSQL transaction:
   payments row + outbox row
→ HTTP 202
→ outbox publisher
→ broker
→ settlement worker
→ provider acknowledgement
→ final settlement state
```

Dňa 29. júla 2026 o `08:15 UTC` začala broker partition zvyšovať publish latency. API naďalej zapisovalo payment a outbox rows a vracalo `202`. Edge dashboard ukazoval request availability `99.99 %`, pretože front door a PostgreSQL commits fungovali.

Prevádzkový tím mal opakovaný runbook:

```text
nájsť outbox rows staršie než 30 minút
→ manuálne zvýšiť počet workers
→ pri pretrvávajúcom backloge spustiť cleanup SQL
→ znovu spustiť publisher
```

Cleanup query používala `created_at < now() - interval '30 minutes'` bez podmienky `published_at IS NOT NULL`. O `09:02 UTC` odstránila `4 182` stále nepublikovaných commands. Payment rows zostali v databáze a API bolo dostupné, ale accepted settlements sa nikdy nedostali k providerovi.

### Vlastnosti incidentu

- **Availability:** HTTP acceptance path zostal dostupný.
- **Reliability:** required function `complete exactly once within 10 minutes` zlyhala.
- **Durability:** acknowledged settlement intent neprežil celý required lifecycle; payment fact zostal, execution command sa stratil.
- **Correctness:** status `accepted` už nereprezentoval skutočne vykonateľný intent.
- **Recoverability:** production databáza sama neobsahovala complete current outbox set.

Root cause nebola samotná broker partition. Partition bola trigger. Root cause bol nebezpečný retention/cleanup contract nad nepublikovanými commands. Causal amplifiers boli green front-door SLI, manuálny runbook, chýbajúca backlog age boundary a neprítomná end-to-end reconciliation.

## 9. Competing hypotheses a discriminating evidence

Pri symptóme `accepted settlement sa nedokončil` treba odlíšiť:

1. request sa nikdy nedostal k API;
2. API necommitlo payment row;
3. payment commitol, ale response sa stratila;
4. outbox row existuje a publisher stojí;
5. broker message existuje, worker ju nespracoval;
6. provider prijal operation, ale acknowledgement sa stratilo;
7. outbox row bola po acknowledgement-e odstránená;
8. UI číta stale projection.

Discriminating evidence:

```text
idempotency key a request ID
→ API access/application log
→ PostgreSQL transaction/payment/outbox records
→ WAL alebo CDC archive
→ publisher attempt a cursor
→ broker offset/message identity
→ worker execution log
→ provider idempotency ledger
→ projection generation
```

Prítomná payment row bez outbox row a bez broker/provider evidence, pričom isolated PITR obsahuje outbox row pred cleanupom, dokazuje post-commit logical deletion.

## 10. Evidence-preserving containment

Bezpečné prvé kroky:

1. zastaviť cleanup job a odobrať jeho write capability;
2. pozastaviť nové `202` acknowledgements alebo prejsť na bounded backpressure;
3. zachovať cleanup SQL, actor, transaction ID, audit a WAL/CDC evidence;
4. snapshotnúť current payment, outbox, broker a provider state;
5. oddeliť known completed, pending, unknown a lost-intent cohorts;
6. zabrániť blind replayu bez idempotency a provider reconciliation.

Scale-up publishera bez zastavenia cleanupu by iba zrýchlil race. Obnovenie všetkých rows bez provider comparison by mohlo vytvoriť duplicate settlements.

## 11. Authoritative recovery

Recovery používa isolated point-in-time restore do času pred cleanupom:

```text
isolated PITR candidate
→ extract deleted outbox commands
→ join s production payment state
→ compare broker a provider idempotency ledgers
→ classify never-sent, sent-unknown a completed
→ reinsert iba safe commands s pôvodným idempotency keyom
→ publish cez bounded cohort
→ verify provider a customer outcome
→ retire temporary recovery path
```

Recovery je complete až keď:

- všetkých `4 182` intents má authoritative final classification;
- never-sent commands boli bezpečne vykonané;
- sent-unknown commands boli reconciled bez duplicate side effectu;
- completed operations neboli replaynuté;
- customer-visible status zodpovedá provider ledgeru;
- unsafe cleanup path už neexistuje;
- druhá broker partition nespôsobí stratu acknowledged intentu.

## 12. Reliability acceptance verdict

Business capability je prijatá, keď:

- required function, conditions, period a population sú explicitné;
- availability, correctness, latency a durability majú oddelené evidence;
- acknowledgement boundary zodpovedá durable state transitionu;
- partial cohorts a downstream completion sú merané;
- dependency failure vedie k bounded backpressure alebo bezpečnému degraded mode-u;
- logical deletion a corruption majú recovery path;
- restore preukáže reconstructability, nie iba existenciu backupu;
- original business operation funguje;
- duplicate, lost-intent, stale-status a silent-success paths zlyhajú;
- second-failure a second-recovery test prejdú.

## 13. Troubleshooting flow

```text
user-visible failed capability
→ exact operation, cohort, release a time window
→ acknowledgement a required final outcome
→ availability observation point
→ transaction a durable-state identity
→ async delivery a dependency chain
→ correctness a latency verdict
→ backup/recovery lineage
→ competing hypotheses
→ evidence-preserving containment
→ business reconciliation
→ original a forbidden outcome validation
```

## 14. Earlier controls

- user-journey reliability contract;
- event-based availability namiesto process-up metric;
- atomic payment + outbox commit;
- idempotency key od edge po provider;
- unpublished-row deletion invariant;
- backlog age a completion-latency indicators;
- automatic backpressure pri broker outage;
- immutable, reviewed retention policy;
- least-privilege cleanup identity;
- isolated restore rehearsal;
- periodic payment/outbox/broker/provider reconciliation;
- silent-success a logical-delete chaos test.

## 15. Anti-patterny

### Uptime equals reliability

Healthy process alebo `200/202` nepreukazuje final business outcome.

### Viac replicas equals durability

Replication môže okamžite rozmnožiť logical corruption alebo chybný delete.

### Backup exists

Bez restore, dependency a business validation nie je durability preukázaná.

### Planned downtime sa vždy odpočíta

Používateľský impact nezmizne preto, že maintenance bola naplánovaná. Exclusion musí byť explicitná a zmysluplná pre daný contract.

### Priemer cez všetkých používateľov

Critical tenant alebo Region môže byť úplne nedostupný pri zelenom globálnom priemere.

### Acknowledged means queued somewhere

Acknowledgement musí patriť presnej durable state transition, nie nádeji, že downstream proces neskôr uspeje.

## 16. Kontrolné otázky

1. Čo tvorí exact reliability subject?
2. Ako sa reliability, availability a durability líšia?
3. Kedy je vhodnejšia time-based a kedy event-based availability?
4. Prečo `202 Accepted` nemusí byť good event?
5. Ako partial availability skryje aggregate metric?
6. Čo musí obsahovať durability contract?
7. Prečo storage replication nechráni pred logical corruption?
8. Kde je acknowledgement boundary transactional outboxu?
9. Ako odlíšiť lost response od lost committed intentu?
10. Prečo restore bytes nie je automaticky business recovery?
11. Ktorý dôkaz potvrdí post-commit deletion?
12. Čo musí overiť reliability acceptance verdict?

## Glossary impact

Relevantné pojmy: reliability subject, required function, stated conditions, event-based availability, time-based availability, partial availability, durability subject, acknowledgement boundary, durable intent, logical durability failure, reconstructability, reliability acceptance verdict a second-failure validation.

## Primárne zdroje

- [Google SRE — Service Level Objectives](https://sre.google/sre-book/service-level-objectives/)
- [Google SRE — Embracing Risk](https://sre.google/sre-book/embracing-risk/)
- [Google SRE — Availability Table](https://sre.google/sre-book/availability-table/)
- [Google SRE — Introduction](https://sre.google/sre-book/introduction/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Zero Trust](../13-security-and-identity/zero-trust.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: SLI, SLO a SLA →](sli-slo-sla.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
