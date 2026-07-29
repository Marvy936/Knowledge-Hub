# SRE and Operations

Táto sekcia vysvetľuje, ako prevádzkovať služby podľa explicitných user a business reliability objectives namiesto nejasného cieľa `udržať systém hore`. Vedie od definície spoľahlivého outcome-u cez measurement, risk a operational demand až po incident response, causal learning, recovery, controlled experiments a production readiness.

SRE tu nie je názov produktu ani synonymum pre tradičné operations. Je to engineering prístup, ktorý spája software design, production evidence, bounded risk, incident learning, automatizáciu a vlastníctvo služby.

## Predpoklady

Odporúča sa najprv dokončiť:

- [DevOps Foundations](../00-foundations/README.md),
- [Testing and Software Quality](../04-testing-and-quality/README.md),
- [CI/CD and Release Engineering](../05-ci-cd-and-release/README.md),
- [Kubernetes](../09-kubernetes/README.md),
- [Cloud and AWS](../11-cloud-and-aws/README.md),
- [Observability](../12-observability/README.md),
- [Security and Identity](../13-security-and-identity/README.md).

## Authoritative poradie

1. [Reliability, availability a durability](reliability-availability-durability.md)
2. [SLI, SLO a SLA](sli-slo-sla.md)
3. [Error budgets](error-budgets.md)
4. [Toil](toil.md)
5. [Capacity planning](capacity-planning.md)
6. [Incident management](incident-management.md)
7. [On-call a escalation](on-call-and-escalation.md)
8. [Runbooks a playbooks](runbooks-and-playbooks.md)
9. [Root cause analysis](root-cause-analysis.md)
10. [Blameless postmortems](blameless-postmortems.md)
11. [Backup a restore](backup-and-restore.md)
12. [RPO a RTO](rpo-and-rto.md)
13. [Disaster recovery](disaster-recovery.md)
14. [Chaos engineering](chaos-engineering.md)
15. [Operational readiness](operational-readiness.md)

Aktuálny authoritative stav sekcie je **15/15 · In progress**. Všetky kapitoly existujú; stav **Ready for user review** možno nastaviť až po finálnom section-level consistency passe.

## Connected learning scenarios

### `SRE-PAY-52` — reliability, SLO, error budget a toil

```text
merchant settlement request
→ atlas-settlement-api
→ atomic payment + outbox commit
→ HTTP 202
→ publisher a broker
→ settlement worker
→ provider acknowledgement
→ final customer-visible state
```

Broker partition vytvorila backlog. Opakovaný privileged cleanup odstránil `4 182` ešte nepublikovaných outbox commands. Front-door availability zostala zelená, no end-to-end completion a durability acknowledged intentu zlyhali.

```text
business reliability subject
→ user-centered SLI a SLO
→ completion error-budget consumption
→ policy consequence
→ operational demand a toil classification
→ redesign a safe recovery
```

### `SRE-PAY-53` — capacity, incident command, on-call a runbook safety

End-of-month campaign vytvorila `2 800` unique settlements/s pri provider slowdown-e. API prijímala `3 600` HTTP attempts/s, ale safe completion capacity bola `1 850/s` a one-AZ-safe capacity `1 420/s`.

```text
forecast a SLO
→ chybný front-door CPU capacity model
→ retry amplification a rast queue age
→ critical burn-rate page
→ acknowledgement bez qualified escalation
→ oneskorené incident declaration
→ nekorelované parallel mitigations
→ stale lease-reset runbook
→ redelivery amplification
→ bounded admission, incident command a reconciliation
```

Capacity root cause bol model viazaný na priemerný request rate a API CPU namiesto logical demandu, constrained completion pathu, retries a failure headroomu. Stale runbook resetoval `62 418` in-flight lease-ov a vytvoril `143` sent-unknown operations.

### `SRE-PAY-54` — causal learning, logical-corruption recovery a objectives

Release `payments-api 7.25.0` pridal compactor, ktorého missing `tenant_scope` sa interpretoval ako wildcard.

```text
release 7.25.0
→ missing tenant_scope
→ wildcard destructive query
→ 186 420 rows archived
→ 7 842 active rows poškodených
→ correlation metadata odstránené
→ 613 callbacks vyžadovalo secondary correlation
→ 91 merchant-visible stale/unknown outcomes
→ corruption replikovaná do replicas a snapshots
```

Technical root cause bol fail-open wildcard contract. Systemic cause bol chýbajúci destructive-operation safety model; escape a recovery-delay causes zahŕňali zero-row canary, exit-code oracle, stale decrypt grants, unrehearsed restore a neúplný consistency group.

```text
RCA a causal graph
→ blameless postmortem
→ clean-point selection
→ isolated PITR
→ affected manifest
→ provider-ledger reconciliation
→ bounded merge/replay
→ business recovery
→ objective-versus-actual verdict
```

Deklarované objectives `RPO 5 min`, `RTO 45 min` a maximum tolerable disruption `2 h` neprešli. Database clean point bol 9 sekúnd pred corruption, business-consistent point bol starý `11 min 7 s` a recovery trvala `3 h 48 min 53 s`.

### `SRE-PAY-55` — DR, chaos evidence a operational readiness

Primary Region stratil network/control-plane connectivity. Warm standby mala database lag iba 32 sekúnd, ale complete business recovery graph nebol current.

```text
regional disruption
→ DR activation
→ database promotion
→ /healthz green a DNS cutover
→ runtime KMS grant missing
→ provider egress/callback path nepripravený
→ broker checkpoint a fencing stale
→ HTTP 202 bez final completion
→ bounded degraded mode
→ provider/broker/data reconciliation
→ safe recovery za 2 h 19 min
```

Primary DR root cause bol warm-standby plan bez versionovaného end-to-end business recovery graphu a current rehearsal-u.

Pred incidentom bol narrow experiment `CH-PAY-41`, ktorý zabil iba worker Pody a sledoval HTTP `202`, nesprávne interpretovaný ako regional DR evidence. Review `ORR-PAY-55-v2` súčasne prijala open tickets, configured placeholders a stale runbook ako `conditional green` bez blocking semantics, expiry alebo effective-state evidence.

```text
DR failure graph
→ exact chaos hypothesis a bounded business cohort
→ provider/KMS/broker/DNS/fencing experiment
→ falsified keep-alive routing assumption
→ remediation a repeat experiment
→ business recovery 31 min 42 s
→ operational-readiness gates a day-2 acceptance
```

## Cieľ zvládnutia prvého bloku

### Reliability, availability a durability

- definovať exact reliability subject a success boundary;
- odlíšiť availability, correctness, latency, durability a reconstructability;
- navrhnúť acknowledgement boundary;
- vysvetliť partial availability a logical corruption;
- validovať user/business outcome namiesto process healthu.

### SLI, SLO a SLA

- definovať eligible population, good/bad event a observation point;
- rozlišovať request attempts a unique business operations;
- používať rolling/calendar windows a missing-data semantics;
- odlíšiť interný SLO od external SLA;
- vytvoriť reprodukovateľný service-level verdict.

### Error budgets

- odvodiť budget z SLO a population;
- používať consumption, forecast a multi-window burn rate;
- premeniť budget state na bounded release/incident decision;
- odlíšiť discretionary risk od remediation/security changes;
- validovať recurrence a second-window behavior.

### Toil

- klasifikovať manual, repetitive, automatable, tactical, non-enduring a scale-linked work;
- merať frequency, touch time, interruption, risk a growth;
- nájsť root operational demand;
- vybrať elimination, redesign, automation, self-service alebo acceptance;
- overiť trvalé zníženie demandu bez reliability regresie.

## Cieľ zvládnutia druhého bloku

### Capacity planning

- modelovať logical demand a amplification;
- mapovať end-to-end constrained resources;
- rozlíšiť configured a effective capacity;
- odvodiť burst, failover, rollout a recovery headroom;
- započítať acquisition/provisioning lead time;
- preukázať load, soak, failover, backlog a second-peak acceptance.

### Incident management

- definovať declaration, severity a incident subject;
- oddeliť IC, Operations, Communications a Planning;
- používať evidence-preserving stabilization;
- viazať actions na hypotheses, owners a abort criteria;
- definovať business recovery, handoff a closure.

### On-call a escalation

- definovať support contract a page eligibility;
- odlíšiť delivery, acknowledgement a qualified response;
- navrhnúť primary/secondary coverage a tested escalation;
- overiť access, contacts a schedule;
- merať page quality a sustainable load.

### Runbooks a playbooks

- rozlíšiť repeatable procedure a decision framework;
- definovať document subject, generation a eligibility;
- zapisovať preconditions, safety, branches a bounded actions;
- riešiť partial/unknown outcome cez rollback, compensation alebo reconciliation;
- rehearse, withdrawnúť a nahradiť stale dokumenty.

## Cieľ zvládnutia tretieho bloku

### Root cause analysis

- odlíšiť trigger, proximate mechanismus a business impact;
- analyzovať technical, systemic, escape, detection, amplification a recovery causes;
- používať evidence timeline, causal graph a counterfactual tests;
- navrhnúť mechanism-level corrective actions a recurrence closure.

### Blameless postmortems

- vytvoriť factual impact a timeline;
- zachovať accountability bez osobného blame;
- vyhodnotiť response, luck a organizational context;
- sledovať action portfolio až po effective-state verification;
- vykonávať independent review a cross-incident learning.

### Backup a restore

- definovať protected subject a consistency group;
- odlíšiť backup, replication, snapshot, archive, restore a recovery;
- vybrať clean point namiesto automatického latest pointu;
- testovať isolation, keys, restore, fencing a reconciliation;
- validovať infrastructure, data, application a business outcome.

### RPO a RTO

- odvodiť objectives z BIA a exact scenario;
- odlíšiť RPO, RTO, maximum tolerable disruption a work recovery;
- používať time aj event/data boundaries;
- merať actual recovered point a actual recovery time;
- overiť objectives current-generation timed exercise-om.

## Cieľ zvládnutia záverečného bloku

### Disaster recovery

- odlíšiť HA, incident response a DR;
- definovať recovery subject, consistency group a strategy tier;
- modelovať complete recovery graph vrátane control plane-u, identities, providers a routing;
- navrhnúť writer fencing, degraded mode, cutover a failback;
- merať RPO/RTO a work recovery počas full exercise-u.

### Chaos engineering

- definovať exact experiment subject, cohorts a falsifikovateľnú steady-state hypotézu;
- vybrať realistic event a reprezentatívny bounded blast radius;
- používať safety state machine, abort a injection identity;
- odlíšiť supported, falsified, inconclusive a incident verdict;
- uzatvoriť finding remediation repeat experimentom.

### Operational readiness

- odlíšiť release, launch a operational readiness;
- vytvoriť service-specific PRR s current evidence inventory;
- rozlišovať designed, configured, loaded, effective a rehearsed controls;
- používať blocker taxonomy a expiring exact exceptions;
- riadiť staged launch, handover, day-2 ownership a re-readiness triggers.

## Dominantný model sekcie

```text
user a business capability
→ exact reliability/recovery/operating subject
→ objective a tolerance failure-u
→ production evidence a current generation
→ risk alebo operational demand
→ bounded decision, action alebo experiment
→ effective-state a business verification
→ recovery alebo learning
→ recurrence, second-operation a lifecycle closure
```

Každá komplexná kapitola rozlišuje:

- configured, observed, loaded a effective state;
- technical success a user/business outcome;
- trigger, root cause a causal amplifier;
- containment, remediation, recovery a work recovery;
- activity metric a reliability evidence;
- prvý úspech a second-operation/reconciliation closure;
- exact evidence scope a širší nepreukázaný claim.

## Stav

| Téma | Status | Úroveň |
|---|---|---|
| Reliability, availability a durability | Learning | L2 |
| SLI, SLO a SLA | Learning | L2 |
| Error budgets | Learning | L2 |
| Toil | Learning | L2 |
| Capacity planning | Learning | L2 |
| Incident management | Learning | L2 |
| On-call a escalation | Learning | L2 |
| Runbooks a playbooks | Learning | L2 |
| Root cause analysis | Learning | L2 |
| Blameless postmortems | Learning | L2 |
| Backup a restore | Learning | L2 |
| RPO a RTO | Learning | L2 |
| Disaster recovery | Learning | L2 |
| Chaos engineering | Learning | L2 |
| Operational readiness | Learning | L2 |

Sekcia zostáva **In progress** až do úspešného finálneho section-level consistency passu. Gate musí overiť authoritative ordering všetkých 15 kapitol, connected incident chain, obojsmernú navigation, prechod zo Security and Identity, výstup na roadmapu alebo nasledujúcu authoritative sekciu, glossary merge, prázdne audit-failure artifacts, terminology a current primary-source facts.