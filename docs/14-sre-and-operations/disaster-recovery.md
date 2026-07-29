# Disaster recovery

Disaster recovery je riadená obnova kritickej business capability po disruption, ktorá presiahne bežný high-availability, retry alebo lokálny incident-response mechanizmus. Neznamená iba spustiť infraštruktúru v inom Regione. Recovery je hotová až vtedy, keď je obnovený správny, bezpečný a reconciled business outcome.

```text
business capability a disruption scenario
→ exact recovery subject a consistency group
→ recovery strategy a authority
→ standby generation, dependencies a capacity
→ activation trigger a declaration
→ fencing a evidence preservation
→ data/control/dependency recovery
→ traffic a writer cutover
→ technical, security a business validation
→ reconciliation a work recovery
→ failback alebo steady-state adoption
→ second-disruption acceptance
```

## 1. Disaster, incident a high availability

Nie každý incident je disaster. Praktické rozlíšenie používa rozsah a recovery mechanismus.

### High availability

Systém absorbuje bežný component alebo failure-domain výpadok bez manuálneho obnovenia celej capability. Príklady:

- Pod alebo VM replacement;
- database failover v jednej Region;
- strata jednej Availability Zone;
- traffic redistribution medzi zdravé replicas.

### Incident response

Tím koordinuje containment a recovery pri degradácii alebo outage. Služba môže zostať v pôvodnom failure domain-e.

### Disaster recovery

Obnova potrebuje alternate environment, clean restore, regional cutover, rekonštrukciu významnej časti service graphu alebo dlhšie business continuity opatrenie.

```text
component failure zvládnutý local redundancy
→ HA

impact vyžadujúci coordinated mitigation
→ incident response

primary environment alebo business state nie je bezpečne použiteľný
→ disaster recovery
```

Label `disaster` nemá byť emocionálny. Je to activation class s explicitným planom, authority a recovery objective-mi.

## 2. Exact DR subject

Tvrdenie `máme DR v druhom Regione` nie je overiteľné. DR subject má uviesť:

- business capability a critical journeys;
- disruption scenario;
- primary a recovery locations;
- application, data a dependency consistency group;
- recovery tier a strategy;
- RPO, RTO a degraded-mode objective;
- architecture a release generation;
- data replication alebo backup generation;
- identity, key, network a DNS generations;
- external-provider contracts;
- traffic a writer ownership;
- activation authority;
- plan/runbook generation;
- validation a failback contract.

Príklad:

```text
capability: merchant settlement completion
scenario: primary Region unavailable > 10 min
primary: eu-central-1 / prod-eu1
recovery: eu-west-1 / prod-euw1
strategy: warm standby
RPO: 5 min business-consistent
RTO: 45 min merchant-facing safe recovery
release: payments 7.26.0
plan: DR-PAY-55-v4
consistency group:
  PostgreSQL + outbox + broker position + provider correlation
traffic authority: Route 53 generation DNS-PAY-18
writer authority: FENCE-PAY-7
```

## 3. Business impact analysis a recovery tier

Recovery strategy musí vychádzať z business impact analysis, nie z preferencie konkrétnej cloud služby.

Vyhodnoť:

- financial a contractual impact;
- data integrity a legal risk;
- customer tolerance;
- maximum tolerable disruption;
- maximum tolerable data divergence;
- degraded operations;
- dependency criticality;
- staffing a vendor availability;
- recovery cost a complexity.

Praktické strategy tiers:

### Backup a restore

Najnižšie steady-state náklady, najdlhší recovery čas. Vyžaduje pripravenú infrastructure generation, clean recovery points a rekonštrukciu dependencies.

### Pilot light

Critical data a minimálne control components existujú v recovery environment-e. Compute a traffic path sa aktivujú počas recovery.

### Warm standby

Zmenšená, priebežne aktualizovaná service generation je spustiteľná, ale potrebuje scale-up, dependency activation a traffic cutover.

### Active-passive

Standby je pripravený prevziať traffic, no writer authority je typicky iba na jednej strane.

### Active-active

Viac lokalít spracúva production traffic. Znižuje activation time, ale zvyšuje consistency, conflict, routing a split-brain complexity.

Strategy label nie je acceptance evidence. Warm standby bez current secrets, provider allowlistu a recovery capacity je iba čiastočne provisioned environment.

## 4. Recovery graph

DR sa má modelovať ako dependency graph, nie zoznam resources.

```text
customer DNS a routing
→ edge/TLS/WAF
→ workload runtime a service discovery
→ identity, secrets a KMS
→ database a durable log
→ broker/queue a consumer position
→ external provider network/credentials/callbacks
→ observability, paging a audit
→ support, reconciliation a business operations
```

Pre každý node a edge urč:

- source of truth;
- recovery mechanismus;
- current generation;
- dependency order;
- recovery ownera;
- capacity a quota;
- validation oracle;
- forbidden outcome;
- fallback alebo manual continuity path.

Database replica bez functional provider pathu neobnoví settlement capability.

## 5. Control plane a data plane

Recovery environment potrebuje viac než application data.

### Data plane

- user a business records;
- message a event state;
- object/block/file data;
- consumer offsets;
- idempotency a correlation records;
- configuration potrebná pre business processing.

### Control plane

- infrastructure definitions;
- cluster a deployment controllers;
- DNS a certificates;
- identity, policies, secrets a keys;
- release artifacts a registries;
- feature flags a routing policy;
- observability a incident tooling;
- recovery automation a approvals.

Control plane môže byť unavailable alebo compromised súčasne s data plane-om. DR plan uložený iba v primary account-e nie je recovery plan.

## 6. Replication, clean point a corruption

Replication znižuje lag, ale kopíruje aj:

- logical corruption;
- malicious writes;
- mistaken deletes;
- incompatible schema state;
- invalid configuration;
- compromised credentials alebo policy effects.

DR potrebuje scenario-specific recovery choice:

```text
physical/regional failure
→ current replicated state môže byť správny

logical corruption alebo compromise
→ current replica môže byť unsafe
→ vyber clean point a side-by-side recovery
```

Recovery plan má podporovať:

- current replicated failover;
- point-in-time clean restore;
- partial object/table recovery;
- external-ledger reconciliation;
- event replay alebo compensation;
- immutable recovery artifacts.

## 7. Writer fencing a split brain

Pred aktiváciou alternate writera treba preukázať, že old writer už nemôže pokračovať alebo byť neskôr neúmyselne obnovený.

Mechanizmy:

- database promotion generation;
- lease alebo epoch token;
- consensus/leader election;
- network isolation;
- credential revocation;
- write endpoint rotation;
- queue ownership generation;
- explicit traffic and writer fence.

```text
primary unknown alebo partially reachable
+ standby promoted bez fencing
→ divergent writes
→ ambiguous reconciliation
```

Fencing verdict musí byť založený na effective state-e, nie na vydanom command-e.

## 8. Activation trigger a authority

DR activation má definovať:

- objective trigger;
- decision authority;
- required consultation;
- maximum waiting time;
- conditions pre degraded mode;
- evidence cutoff;
- communication cadence;
- cost a regulatory consequences;
- abort alebo alternate strategy.

Príklady triggerov:

- primary Region unavailable dlhšie než 10 minút;
- projected RTO breach bez regional recovery;
- confirmed integrity compromise;
- primary recovery path unsafe;
- facility alebo account control plane unavailable;
- provider declares extended regional impact.

Čakanie na absolútnu istotu môže spotrebovať RTO. Predčasný failover bez fencing a consistency verdictu môže vytvoriť horší incident. Plan preto potrebuje explicitný decision contract.

## 9. Recovery phases

Praktický DR lifecycle môže používať tieto fázy.

### Declaration a stabilization

- declare disaster subject a authority;
- preserve volatile evidence;
- freeze unrelated changes;
- classify physical vs logical vs malicious failure;
- fence writers a destructive automation;
- activate communication a vendor paths.

### Environment activation

- verify recovery account/Region access;
- activate network, compute a service control plane;
- load approved release/config generation;
- verify key, secret a certificate paths;
- confirm quotas a capacity.

### Data a dependency recovery

- select replicated alebo clean recovery state;
- restore/promote database a broker state;
- recover external correlations;
- validate schema a invariants;
- activate provider egress, credentials a callbacks.

### Traffic cutover

- prove health at business boundary;
- update routing generation;
- observe resolver/cache behavior;
- ramp traffic podľa guardrailov;
- preserve rollback/failback options.

### Work recovery

- drain backlog;
- reconcile post-point operations;
- resume scheduled/batch work;
- remove temporary overrides;
- close support a customer commitments.

## 10. Degraded mode

DR nemusí okamžite obnoviť všetky capabilities. Degraded mode môže zachovať critical invariant pri nižšej funkcionalite.

Príklady:

- prijímať settlement intents, ale odložiť provider submission;
- povoliť read-only history;
- prioritizovať regulated alebo high-value cohorts;
- pozastaviť reporting a recomputation;
- obmedziť tenant traffic;
- používať explicitné `Retry-After` namiesto silent acceptance.

Degraded mode musí mať:

- user-visible semantics;
- durability a queue limits;
- maximum duration;
- reconciliation path;
- ownera a exit criteria;
- testovaný capacity model.

## 11. DR testing a exercise classes

Plan bez current-generation exercise-u je hypothesis.

### Tabletop

Overuje decisions, roles, communications a assumptions bez technickej aktivácie.

### Component recovery test

Overuje konkrétny restore, DNS, key alebo dependency path.

### Parallel recovery

Aktivuje alternate environment bez production trafficu a porovnáva behavior.

### Partial traffic exercise

Presunie bounded cohort alebo synthetic business operations.

### Full regional exercise

Testuje complete service graph, traffic, data, provider path a work recovery.

### Surprise alebo limited-notice exercise

Testuje real readiness a discovery friction, ale musí zachovať safety a organizational authorization.

Exercise musí merať:

- declaration time;
- access a environment activation;
- data recovered point;
- technical service recovery;
- business validation;
- reconciliation/work recovery;
- actual RPO/RTO;
- unresolved manual steps;
- second-responder reproducibility.

## 12. Worked incident `SRE-PAY-55`

Atlas Payments používal warm standby `prod-euw1` pre primary `prod-eu1`. Service catalog deklaroval:

```text
RPO: 5 min
RTO: 45 min
strategy: warm standby
last DR test: 2026-03-18
plan: DR-PAY-55-v3
```

Dňa 29. júla o `07:12 UTC` primary Region stratil podstatnú časť network/control-plane connectivity. Existing workloads nedokázali spoľahlivo komunikovať s database, brokerom ani providerom. Incident command aktivoval regional DR.

Počiatočný recovery inventory:

```text
standby database lag:          32 s
standby application release:   7.26.0
standby configured capacity:   70 % primary
KMS restore/decrypt grant:     missing pre runtime role
provider egress allowlist:     iba eu-central-1 NAT IPs
broker consumer checkpoint:    posledná verified sync pred 27 min
DNS health endpoint:           /healthz bez provider completion
runbook generation:            DR-PAY-55-v3, architecture pred broker v4
```

O `07:41 UTC` bola standby database promoted. O `07:53 UTC` prešiel `/healthz` a DNS weight sa presunul do `eu-west-1`. API začala vracať HTTP `202`, ale final settlement completion zostala zablokovaná:

- runtime nevedel decryptnúť provider credential;
- po manuálnom grant-e provider odmietal egress z nových IP;
- broker recovery použil stale checkpoint a vytvoril mixed `never-sent`/`sent-unknown` cohort;
- callbacks smerovali na primary Region;
- standby worker scale prekročil DB pool guardrail;
- monitoring ukazoval front-door availability, nie provider-confirmed completion.

Trigger bol regional connectivity/control-plane failure.

Primary DR root cause bol **warm-standby design a plan, ktoré nepredstavovali versionovaný end-to-end business recovery graph a neboli rehearsed na current identity, provider, broker a routing generation**.

Causal amplifiers:

- component-level readiness namiesto consistency-group readiness;
- `/healthz` bez final business oracle;
- missing tested KMS grant;
- external provider allowlist a callback routing mimo DR manifestu;
- stale broker checkpoint/runbook generation;
- configured capacity bez failure-mode load testu;
- nejasný writer/consumer fencing contract.

## 13. Evidence-preserving containment

IC zastavil ďalší unbounded cutover:

```text
freeze non-DR changes
→ preserve DNS, KMS, broker, provider a deployment evidence
→ stop new provider submissions
→ keep durable intent acceptance bounded
→ fence primary a standby consumer ownership
→ classify broker/provider cohorts
→ activate provider emergency contact
→ replace green /healthz verdict business completion oracle-om
```

Traffic sa dočasne obmedzil na `900 unique intents/s` s explicitným degraded-mode contractom.

## 14. Authoritative recovery

1. vytvoriť exact recovery manifest `REC-PAY-55-1`;
2. opraviť runtime KMS grant a overiť decrypt canary;
3. pridať recovery egress IPs do provider allowlistu;
4. presunúť callback routing na recovery Region;
5. obnoviť broker checkpoint z authoritative event/provider evidence;
6. rozdeliť `never-sent`, `sent-unknown` a `completed` cohorts;
7. aktivovať consumers s epoch fencing a bounded concurrency;
8. validovať provider-confirmed synthetic settlement;
9. rampovať tenant traffic podľa completion SLI a DB/provider saturation;
10. reconciliovať affected operations;
11. odstrániť temporary grants a overrides;
12. prijať `prod-euw1` ako current active generation do controlled failbacku.

Safe merchant-facing recovery nastala o `09:31 UTC`, teda `2 h 19 min` po disruption start-e. Deklarovaný 45-minútový RTO neprešiel. Potvrdená permanentná strata acknowledged intents bola nula, ale `318` operations vyžadovalo provider-ledger reconciliation.

## 15. Failback

Failback je samostatná risky transition, nie automatický návrat po skončení provider incidentu.

Vyžaduje:

- current authoritative writer identity;
- reverse replication alebo merge plan;
- conflict a post-point manifest;
- restored primary capacity a dependencies;
- traffic ramp a abort criteria;
- old active environment retirement;
- updated RPO/RTO measurement;
- customer/business closure.

Častý správny outcome je ponechať recovery Region ako dočasný primary a naplánovať controlled rebalancing.

## 16. DR acceptance verdict

Disaster recovery je prijatá, keď:

- business capability, disruption scenarios a consistency groups sú explicitné;
- strategy zodpovedá BIA, RPO, RTO a maximum tolerable disruption;
- complete recovery graph má owners a recovery mechanisms;
- control plane, data plane, identity, keys, network, DNS a external dependencies sú zahrnuté;
- standby release/config/data generations sú current alebo majú bounded convergence path;
- writer/consumer fencing zabraňuje split brain;
- recovery identity a access sú testované;
- capacity a quotas prežijú failure-mode load;
- technical, security, user a business validation prejdú;
- post-point work má replay/merge/compensation/reconciliation contract;
- degraded mode je explicitný a bounded;
- actual RPO/RTO sú zmerané od business boundaries;
- failback alebo adopted-steady-state plan je overený;
- alternate responder vykoná second exercise;
- forbidden scenario, napríklad wrong Region alebo stale key, je odmietnutý.

## 17. Troubleshooting flow

```text
DR activation alebo exercise zlyháva
→ exact capability/scenario/plan generation
→ declaration a authority
→ primary fencing/writer ownership
→ recovery account/Region access
→ control-plane a release generation
→ identity/key/secret/certificate path
→ network/DNS/provider connectivity
→ data clean point/replication/checkpoint
→ capacity/quotas/dependency readiness
→ technical a business oracle
→ traffic ramp/reconciliation
→ actual RPO/RTO a failback closure
```

## 18. Earlier controls

- BIA a scenario-specific objectives;
- versionovaný recovery graph;
- recovery account/Region independence;
- immutable infrastructure a artifact availability;
- tested recovery identities a keys;
- provider DR contract a contacts;
- DNS/certificate/egress/callback manifest;
- broker/queue checkpoint a fencing semantics;
- clean recovery points a catalog;
- failure-mode capacity test;
- business-outcome health canary;
- scheduled tabletop, partial a full exercises;
- action closure a second-responder test.

## 19. Anti-patterny

### Druhý Region existuje

Neznamená, že obsahuje current, accessible a business-complete recovery generation.

### Database replica je DR

Ignoruje application, identity, broker, network, provider a reconciliation graph.

### Healthcheck je green

Môže overovať process alebo front door, nie final business outcome.

### Failover bez fencing

Vytvára split brain a divergentné writes.

### DR test bez trafficu alebo provider pathu

Neoveruje skutočnú business capability.

### Runbook bol testovaný minulý rok

Architecture, credentials, contacts, quotas a dependencies sa mohli zmeniť.

### RTO končí pri DNS cutover-e

Ignoruje cache propagation, business validation, backlog a work recovery.

### Failback hneď po obnove primary Regionu

Pridáva ďalšiu risky transition počas stále neuzavretého incidentu.

## 20. Kontrolné otázky

1. Ako sa HA, incident response a disaster recovery líšia?
2. Čo tvorí exact DR subject a consistency group?
3. Ako sa backup/restore, pilot light, warm standby a active-active líšia?
4. Prečo database replica nie je complete DR plan?
5. Ako control plane ovplyvňuje recovery?
6. Kedy treba current replica a kedy clean point?
7. Prečo je writer fencing povinný?
8. Čo má obsahovať activation decision contract?
9. Ako sa degraded mode bezpečne navrhuje?
10. Prečo `SRE-PAY-55` vrátilo HTTP `202`, ale nie settlement capability?
11. Ktoré hranice má merať full DR exercise?
12. Čo musí overiť DR acceptance verdict?

## Glossary impact

Relevantné pojmy: disaster-recovery subject, recovery graph, recovery strategy tier, pilot light, warm standby, business continuity mode, disaster declaration, recovery authority, recovery environment generation, provider DR contract, regional writer fencing, recovery traffic cutover, failback generation, DR exercise, work recovery a DR acceptance verdict.

## Primárne zdroje

- [NIST SP 800-34 Rev. 1 — Contingency Planning Guide for Federal Information Systems](https://csrc.nist.gov/pubs/sp/800/34/r1/upd1/final)
- [NIST CSRC Glossary — Contingency plan a disaster recovery plan](https://csrc.nist.gov/glossary/term/contingency_plan)
- [Google SRE — Emergency Response](https://sre.google/sre-book/emergency-response/)
- [Google SRE — Data Integrity](https://sre.google/sre-book/data-integrity/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: RPO a RTO](rpo-and-rto.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Chaos engineering →](chaos-engineering.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
