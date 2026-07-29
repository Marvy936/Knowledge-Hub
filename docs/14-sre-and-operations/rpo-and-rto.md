# RPO a RTO

Recovery Point Objective (RPO) vyjadruje **bod v čase, ku ktorému musia byť dáta po disruption obnovené**, teda tolerovanú stratu alebo potrebu rekonštrukcie dát. Recovery Time Objective (RTO) vyjadruje **čas, počas ktorého môže recovery trvať, kým disruption negatívne prekročí prijateľný business alebo mission impact**.

RPO a RTO nie sú hodnoty backup produktu. Sú to business recovery objectives pre presne definovanú capability, data state, scope a failure scenario. Musia byť odvodené z business impact analysis, premietnuté do architecture a následne overené reálnym recovery testom.

```text
business capability a impact tolerance
→ exact recovery-objective subject
→ dependency a data-consistency inventory
→ disruption/corruption scenarios
→ RPO, RTO a maximum-tolerance boundaries
→ recovery strategy a per-boundary budgets
→ backup/failover/restore/reconciliation design
→ timed exercise a measured actuals
→ objective gap a corrective action
→ second-scenario acceptance
```

## 1. Exact recovery-objective subject

Tvrdenie `RPO je päť minút` je neúplné. Subject musí uviesť:

- business capability a operation;
- customer alebo internal cohort;
- data stores a consistency group;
- failure scenario;
- start/end measurement boundaries;
- timezone a clock authority;
- recovery mode;
- degraded-mode assumptions;
- dependency objectives;
- ownera;
- review generation.

Príklad:

```text
capability: merchant settlement reconciliation
scope: production EU merchant settlements
consistency group: CG-PAY-04
scenario: logical corruption of primary settlement ledger
RPO: 5 min business-consistent point
RTO: 45 min to safe merchant-facing processing
maximum tolerable disruption: 2 h
measurement start: first invalid committed mutation
measurement end: new + historical affected operations safely processable
owner: Payments Resilience
```

RPO/RTO pre read-only reporting môžu byť výrazne voľnejšie než pre financial settlement.

## 2. Recovery Point Objective

NIST definuje RPO ako bod v čase, ku ktorému musia byť dáta po outage obnovené.

Prakticky:

```text
incident/corruption boundary
- oldest acceptable recovery point
= tolerované data-change exposure window
```

Ak corruption nastala o `02:14` a RPO je `5 min`, recovery design musí umožniť návrat aspoň k business-valid state-u okolo `02:09` alebo novšiemu, prípadne preukázať ekvivalentnú rekonštrukciu všetkých neskorších operations.

RPO nehovorí, ako dlho restore potrvá. To rieši RTO.

## 3. Recovery Time Objective

RTO je celkový prijateľný recovery interval pred neprijateľným business impactom.

```text
business disruption start
→ detection/declaration
→ containment
→ environment provisioning
→ data restore
→ dependency recovery
→ application startup
→ validation
→ reconciliation/work recovery
→ safe business service
```

Ak tím meria RTO iba od kliknutia `Start restore` po stav `database available`, skracuje denominator a vynecháva významnú časť user impactu.

## 4. RPO a RTO riešia iné osi

| Objective | Hlavná otázka | Typický trade-off |
|---|---|---|
| RPO | Koľko data change-u alebo ktorú časovú históriu smieme stratiť/rekonštruovať? | capture frequency, logging, consistency, cost |
| RTO | Ako rýchlo musí byť capability bezpečne obnovená? | warm capacity, automation, staffing, complexity, cost |

Príklady:

```text
RPO 24 h, RTO 15 min
→ rýchlo obnovíme staršie dáta

RPO 0, RTO 8 h
→ nestratíme acknowledged data, ale obnova môže trvať dlho

RPO 5 min, RTO 45 min
→ potrebujeme jemný recovery point aj rýchly end-to-end restore
```

Nízke RPO automaticky neznamená nízke RTO.

## 5. Business impact analysis

Business impact analysis (BIA) identifikuje:

- critical capabilities;
- dependency chain;
- impact rastúci s časom;
- data-loss tolerance;
- legal/regulatory commitments;
- financial a customer impact;
- manual/degraded alternatives;
- restoration priority;
- maximum tolerable disruption;
- seasonal alebo event-specific constraints.

Príklad impact curve:

| Disruption | Settlement impact |
|---|---|
| 0–15 min | queueing, bez customer breach |
| 15–45 min | merchant delay, error-budget burn |
| 45–120 min | contractual/support escalation, liquidity risk |
| >120 min | unacceptable business disruption |

RTO `45 min` má potom konkrétny business dôvod. Nie je to okrúhle číslo vybrané infra tímom.

## 6. Maximum tolerable disruption

Organizácie používajú termíny ako Maximum Tolerable Downtime (MTD), Maximum Tolerable Period of Disruption (MTPD) alebo Maximum Acceptable Outage podľa vlastného frameworku.

Spoločný význam:

```text
hranica, za ktorou disruption vytvára neprijateľný business/mission impact
```

RTO má byť kratší než táto hranica a ponechať priestor na uncertainty, work recovery a escalation.

```text
RTO < maximum tolerable disruption
```

Ak sa obe hodnoty rovnajú, recovery plán nemá rezervu na validation alebo komplikácie.

## 7. Work Recovery Time

Po technickom restore môže nasledovať Work Recovery Time (WRT):

- backlog drain;
- data reconciliation;
- manual case processing;
- customer communication;
- index/cache rebuild;
- temporary override removal;
- audit closure.

Približný model:

```text
technical recovery time
+ work recovery time
≤ maximum tolerable disruption
```

Definície a názvoslovie sa medzi organizáciami líšia, preto musia byť measurement boundaries explicitné.

## 8. Actual recovery metrics

Objective oddeľ od nameraného výsledku:

- **RPO** — požadovaný recovery point;
- **actual recovered point** — zvolený a obnovený point;
- **data-loss/reconstruction result** — čo zostalo nenávratne stratené alebo muselo byť replaynuté;
- **RTO** — požadovaný recovery čas;
- **actual recovery time** — nameraný čas do safe business service-u.

Nepoužívaj rovnaké pole `RTO` pre target aj výsledok.

## 9. Measurement boundaries

### RPO boundary

Definuj:

- incident alebo corruption reference time;
- recovery point timestamp/sequence;
- clock authority;
- included consistency-group members;
- acknowledgement semantics;
- reconstructable vs permanently lost operations.

### RTO boundary

Definuj:

- start: first business disruption, detection alebo formal declaration?
- end: infra ready, app ready, new operations safe alebo full historical reconciliation?

Pre SRE learning používaj user/business boundary. Môžeš zároveň publikovať sub-metrics pre detection, restore a work recovery.

## 10. Time-based a event-based RPO

Time-based RPO:

```text
maximálne 5 minút acknowledged changes
```

Event-based RPO:

```text
maximálne 1 000 reconstructable settlement intents
alebo 0 permanently lost acknowledged settlements
```

Pri bursty trafficu môže päť minút znamenať výrazne rozdielny počet operations. Critical financial capability preto často potrebuje time aj event/data invariant.

## 11. Zero RPO

`RPO = 0` znamená, že žiadny acknowledged required state nesmie byť nenávratne stratený v definovanom scenári.

Nevyplýva z toho automaticky synchronous replication. Potrebný je end-to-end acknowledgement contract:

```text
user acknowledgement
→ durable authority
→ replicated/logged state
→ external side-effect identity
→ reconstructability
```

V distributed workflowe s external providerom môže byť stav `sent-unknown`. Zero permanent data loss vyžaduje idempotency, evidence a reconciliation, nie iba lokálnu database repliku.

Zero RPO má vysoké latency, availability, complexity a cost trade-offy. Nemá sa deklarovať bez testu.

## 12. Zero RTO

Skutočné `RTO = 0` by znamenalo žiadny disruption na definovanej business boundary. To je skôr continuous-availability objective než klasický restore objective.

HA/failover môže znížiť disruption, ale stále existujú:

- detection a routing convergence;
- in-flight operations;
- stale sessions/caches;
- data consistency;
- dependency failure;
- validation;
- partial cohort impact.

Marketingové `zero downtime` tvrdenie musí mať exact measurement a failure model.

## 13. Objectives podľa capability a cohortu

Jedna aplikácia môže mať viac objectives:

| Capability | RPO | RTO |
|---|---:|---:|
| accept settlement intent | 0 acknowledged intents | 15 min |
| complete settlement | 5 min reconstructable state | 45 min |
| merchant reporting | 4 h | 8 h |
| audit archive | 24 h capture, no deletion | 24 h retrieval |

Globálny priemer môže skryť critical tenant alebo Region.

## 14. Dependency budgeting

End-to-end RTO potrebuje per-boundary budgets:

```text
RTO 45 min
├── detection/declaration: 5 min
├── containment/fencing: 5 min
├── target provisioning/access: 8 min
├── data restore: 12 min
├── application/dependency startup: 5 min
├── validation: 5 min
└── initial reconciliation/cutover: 5 min
```

Súčet bez parallelism a uncertainty nie je guarantee. Budget pomáha odhaliť, že jedna dependency má provisioning lead time dlhší než celý objective.

Dependency musí mať objective kompatibilný s parent capability. Service s RTO `15 min` nemôže reálne závisieť od identity alebo key restore trvajúceho štyri hodiny.

## 15. Recovery strategy mapping

| Objective need | Candidate mechanism |
|---|---|
| very low RPO | synchronous/continuous logging, durable event log, reconciliation |
| low RTO | warm standby, preprovisioned recovery environment, automated restore |
| logical corruption | retained PITR, immutable history, clean-point analysis |
| Region/account loss | isolated cross-domain copy, alternate identity/network |
| external side effects | idempotency ledger, provider reconciliation |
| long discovery window | dlhšia retention, historical validation |

Mechanizmus musí riešiť konkrétny scenario. Multi-AZ failover nepomôže pri broad logical corruption.

## 16. RPO nie je backup interval

Backup každých päť minút nemusí dať RPO päť minút:

- job môže meškať;
- capture môže trvať;
- latest backup môže byť corrupted;
- log chain môže mať gap;
- copy nemusí dokončiť;
- consistency group môže byť rozídený;
- restore point nemusí byť readable;
- external state nemusí byť reconstructable.

RPO preukáže až selected valid recovery point a business reconciliation.

## 17. RTO nie je restore duration z konzoly

Control-plane restore môže skončiť, ale:

- storage je cold;
- schema migration chýba;
- application nevie načítať dáta;
- identities/secrets nie sú dostupné;
- DNS/traffic nie je prepnutý;
- backlog rastie;
- post-point operations nie sú reconciled;
- forbidden duplicate outcome nie je vylúčený.

RTO končí na dohodnutej business boundary.

## 18. Scenario-specific objectives

RPO/RTO sa môžu líšiť podľa failure-u:

- instance loss;
- zonal failure;
- regional failure;
- logical corruption;
- ransomware/account compromise;
- provider outage;
- operator deletion;
- schema incompatibility;
- widespread identity outage.

`RTO 45 min` bez scenario inventory môže byť splniteľný pre failover, ale nemožný pre clean-room ransomware recovery.

## 19. Degraded mode

RTO môže povoľovať bounded degraded capability:

```text
15 min: prijímať durable settlement intents
45 min: obnoviť automatic completion
2 h: dokončiť historical reconciliation a reporting
```

Degraded mode musí definovať:

- allowed operations;
- denied operations;
- data guarantees;
- capacity;
- duration;
- communication;
- exit criteria;
- forbidden side effects.

Manual spreadsheet bez audit/idempotency nemusí byť prijateľný degraded mode.

## 20. Test design

Recovery objective sa testuje cez timed scenario:

```text
known baseline
→ fault/corruption injection
→ detection a declaration
→ candidate selection
→ access/provisioning
→ restore/failover
→ validation
→ reconciliation/cutover
→ business canary
→ measured point/time
→ cleanup a second run
```

Test report musí uviesť:

- exact generation;
- scenario;
- start/end timestamps;
- recovered point;
- permanently lost a reconstructed data;
- objective vs actual;
- manual steps;
- blockers;
- temporary assumptions;
- residual risk.

## 21. Worked incident `SRE-PAY-54`

### Deklarované objectives

```text
business capability: settlement reconciliation
RPO: 5 min business-consistent recovery point
RTO: 45 min safe merchant-facing recovery
maximum tolerable disruption: 2 h
```

Tieto hodnoty boli zapísané v service catalogu, ale posledný full drill prebehol pred 14 mesiacmi na schema v15 a pred account/key migration.

### Namerané recovery points

Corruption boundary:

```text
02:14:07 UTC
```

Database-only clean point:

```text
02:13:58 UTC
→ 9 sekúnd pred corruption
→ DB-level RPO by vyzeralo splnené
```

Posledný pre-built coordinated DB/provider checkpoint:

```text
02:03:00 UTC
→ 11 min 7 s pred corruption
→ business consistency RPO 5 min nebolo splnené
```

Tím použil DB restore `02:13:58` a provider idempotency ledger na neskoršiu reconciliation. Potvrdená permanentná strata acknowledged settlements bola nakoniec `0`, ale okamžite dostupný business-consistent recovery point prekročil objective a vyžadoval dodatočný reconstruction workflow.

To ukazuje rozdiel:

```text
final permanent data loss = 0
≠ RPO bol počas initial recovery splnený
```

### Nameraný recovery čas

```text
first bad mutation:       02:14:07
incident declaration:     02:41:00
isolated DB queryable:     04:31:00
business recovery:         06:03:00
```

Výsledky:

```text
detection/declaration delay: 26 min 53 s
technical restore boundary:  2 h 16 min 53 s
work recovery/reconciliation: 1 h 32 min
actual business recovery:    3 h 48 min 53 s
RTO objective:               45 min
maximum tolerable disruption: 2 h
```

RTO aj maximum tolerable disruption boli prekročené.

### Prečo objective zlyhal

- objective nemal versionovaný scenario/consistency-group subject;
- RTO začínal v dashboarde až restore jobom, nie first business impactom;
- restore key/access path nebol current;
- recovery environment nebola preprovisioned;
- provider reconciliation nebola zahrnutá do timing modelu;
- drill nepokrýval schema v17 ani logical corruption;
- action owners po account migration neaktualizovali recovery plan;
- service catalog zobrazoval target, nie posledný measured actual.

## 22. Corrective objective generation `REC-PAY-55`

Nový contract:

```text
RPO-1: 0 permanently lost acknowledged settlement intents
RPO-2: ≤ 5 min initial business-consistent replay/reconciliation window
RTO-1: ≤ 15 min durable-intent degraded admission
RTO-2: ≤ 45 min safe new settlement completion
RTO-3: ≤ 120 min historical affected-cohort reconciliation
```

Supporting changes:

- 5-min provider consistency checkpoints;
- continuous idempotency-ledger query path;
- preprovisioned isolated recovery control plane;
- restore key/access canary;
- schema/application compatibility automation;
- bounded affected-manifest extraction;
- quarterly logical-corruption drill;
- objective dashboard s target aj last measured actual;
- dependency budgets a escalation pri miss-e.

## 23. RPO/RTO acceptance verdict

Objectives sú prijaté, keď:

- exact business capability, scope a owner sú definované;
- BIA a impact curve podporujú hodnoty;
- failure scenarios a consistency groups sú explicitné;
- acknowledgement a data authority sú známe;
- RPO má time aj critical event/data semantics;
- RTO start/end boundaries sú user/business-centered;
- maximum tolerable disruption a degraded modes sú definované;
- dependency objectives a lead times sú kompatibilné;
- architecture a recovery strategy mapujú na objectives;
- full timed exercise používa current generations;
- actual recovery point, permanent loss/reconstruction a actual time sú zmerané;
- technical restore aj work recovery sú zahrnuté;
- wrong/corrupted candidate a alternate failure scenario sú testované;
- gaps majú corrective actions a residual-risk ownera;
- second exercise vykoná iný responder alebo target;
- service catalog ukazuje target aj posledný measured result.

## 24. Troubleshooting objective miss-u

```text
missed RPO alebo RTO
→ exact objective generation a scenario
→ measurement start/end a clock authority
→ protected subject/consistency group
→ selected recovery point a clean verdict
→ capture/log chain a reconstructability
→ detection/declaration delay
→ access/key/provisioning lead time
→ restore throughput a capacity
→ dependency/application startup
→ validation/reconciliation/work recovery
→ objective-vs-actual gap
→ redesign, priority alebo explicit risk acceptance
```

Neznižuj objective iba preto, aby dashboard zozelenel. Zmena objective potrebuje nový BIA/risk decision.

## 25. Earlier controls

- business impact analysis;
- capability/dependency inventory;
- consistency-group definitions;
- acknowledgement a data-authority contract;
- scenario-specific objectives;
- RTO dependency budgets;
- preprovisioned recovery path;
- continuous logs/checkpoints podľa RPO;
- tested key/access recovery;
- timed full-stack drills;
- target-versus-actual dashboard;
- degraded-mode contract;
- post-point reconciliation tooling;
- second-responder a alternate-scenario exercise;
- objective review pri architecture/change incidentoch.

## 26. Anti-patterny

### RPO = backup schedule

Ignoruje job delay, clean point, consistency group a restore validity.

### RTO = database available

Ignoruje application, dependencies, validation, reconciliation a user outcome.

### Jedno číslo pre celú firmu

Criticality a data semantics sa medzi capabilities líšia.

### RPO/RTO bez scenára

Failover objective sa nesprávne použije na ransomware alebo logical corruption.

### Zero RPO/RTO ako marketing

Chýba acknowledgement, measurement a failure-model dôkaz.

### Objective bez actual metric

Service catalog ukazuje želanie, nie recoverability.

### Stopky sa spustia pri declaration

Vynechá detection delay a časť user impactu.

### Permanent loss nula, teda RPO splnené

Late reconstruction môže zachrániť dáta, hoci initial recovery point prekročil tolerované window.

### Znížime target po incidente

Bez BIA je to metric gaming, nie risk management.

## 27. Kontrolné otázky

1. Ako sa RPO a RTO líšia?
2. Čo tvorí exact recovery-objective subject?
3. Prečo musia byť objectives odvodené z BIA?
4. Ako maximum tolerable disruption a WRT súvisia s RTO?
5. Prečo RPO nie je backup interval?
6. Prečo RTO nekončí stavom `database available`?
7. Ako time-based a event-based RPO dopĺňajú jeden druhý?
8. Čo znamená zero RPO pre acknowledged external operation?
9. Ako dependency budgets odhalia nesplniteľný RTO?
10. Prečo `SRE-PAY-54` splnilo DB-level point, ale nie business-consistent RPO?
11. Ako sa actual recovery time správne meria?
12. Čo musí overiť RPO/RTO acceptance verdict?

## Glossary impact

Relevantné pojmy: recovery-objective subject, Recovery Point Objective, Recovery Time Objective, business-consistent RPO, actual recovered point, actual recovery time, maximum tolerable disruption, Work Recovery Time, event-based RPO, dependency recovery budget, degraded recovery objective, objective measurement boundary, target-versus-actual recovery a RPO/RTO acceptance verdict.

## Primárne zdroje

- [NIST CSRC Glossary — Recovery Point Objective](https://csrc.nist.gov/glossary/term/recovery_point_objective)
- [NIST CSRC Glossary — Recovery Time Objective](https://csrc.nist.gov/glossary/term/Recovery_Time_Objective)
- [NIST SP 800-34 Rev. 1 — Contingency Planning Guide for Federal Information Systems](https://csrc.nist.gov/pubs/sp/800/34/r1/upd1/final)
- [Google SRE — Emergency Response](https://sre.google/sre-book/emergency-response/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Backup a restore](backup-and-restore.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Disaster recovery →](disaster-recovery.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
