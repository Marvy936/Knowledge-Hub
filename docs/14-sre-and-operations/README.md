# SRE and Operations

Táto sekcia vysvetľuje, ako prevádzkovať služby podľa explicitných user a business reliability objectives namiesto nejasného cieľa `udržať systém hore`. Začína rozlíšením reliability, availability a durability, pokračuje merateľnými SLI/SLO a error-budget control loopom a následne prechádza cez toil, capacity, incident response, on-call, recovery a operational readiness.

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

## Authoritative poradie — aktívne kapitoly

1. [Reliability, availability a durability](reliability-availability-durability.md)
2. [SLI, SLO a SLA](sli-slo-sla.md)
3. [Error budgets](error-budgets.md)
4. [Toil](toil.md)
5. [Capacity planning](capacity-planning.md)
6. [Incident management](incident-management.md)
7. [On-call a escalation](on-call-and-escalation.md)
8. [Runbooks a playbooks](runbooks-and-playbooks.md)

Aktuálny authoritative stav sekcie je **8/15 · In progress**.

## Plánované pokračovanie

Authoritative poradie bude pokračovať bez zmeny roadmapy:

9. Root cause analysis
10. Blameless postmortems
11. Backup a restore
12. RPO a RTO
13. Disaster recovery
14. Chaos engineering
15. Operational readiness

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

Broker partition spustila backlog. Opakovaný manuálny cleanup odstránil `4 182` ešte nepublikovaných outbox commands. Front-door HTTP availability zostala zelená, no end-to-end settlement reliability a durability acknowledged intentu zlyhali.

Incident vytvára chain:

```text
business reliability subject
→ user-centered SLI a SLO
→ completion error-budget consumption
→ policy consequence
→ operational demand a toil classification
→ redesign a safe recovery
```

### `SRE-PAY-53` — capacity, incident command, on-call a runbook safety

End-of-month campaign vytvorila `2 800` unique settlements/s pri provider slowdown-e. API prijímala `3 600` HTTP attempts/s, ale safe end-to-end completion capacity bola iba `1 850` settlements/s a one-AZ-safe capacity `1 420/s`.

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

Trigger bol traffic spike a provider slowdown. Primary capacity root cause bol model viazaný na priemerný HTTP request rate a API CPU namiesto logical demandu, constrained completion pathu, retry amplificationu a failure headroomu.

Causal amplifiers:

- admission nebola naviazaná na downstream completion capacity;
- 24-minútové oneskorenie incident declaration;
- on-call escalation sledovala iba acknowledgement, nie mitigation progress alebo severity;
- stale runbook `RB-PAY-17` resetoval `62 418` lease-ov bez state classification;
- `143` operations prešlo do `sent-unknown` cohortu a vyžadovalo provider-ledger reconciliation.

Recovery použila explicitný IC/Ops/Comms/Planning model, admission `1 700 unique intents/s`, shared retry budget, bounded worker concurrency, provider escalation, queue cohort inventory, controlled drain a business reconciliation.

## Cieľ zvládnutia prvého bloku

Po prvých štyroch kapitolách má byť možné:

### Reliability, availability a durability

- definovať exact reliability subject cez required function, stated conditions a period;
- rozlíšiť reliability, availability, correctness, latency a durability;
- vybrať time-based alebo event-based availability model;
- identifikovať partial availability podľa cohortu, Region, operation alebo release generation;
- navrhnúť acknowledgement a durable-state boundary;
- vysvetliť, prečo replication nechráni pred logical corruption;
- overiť reconstructability cez restore a business reconciliation;
- diagnostikovať front-door success pri zlyhanom downstream outcome-e.

### SLI, SLO a SLA

- definovať valid-event population, good event, observation point a measurement generation;
- navrhnúť user-centered availability, latency, correctness, completion a durability indicators;
- rozlíšiť request attempts od unique business operations;
- používať rolling a calendar compliance windows;
- odlíšiť interný SLO od contractual SLA;
- navrhnúť exclusions a missing-data semantics;
- pracovať s provisional, late a corrected outcomes;
- preukázať, že SLO verdict je reprodukovateľný.

### Error budgets

- odvodiť allowed bad events zo SLO a eligible population;
- vysvetliť remaining, consumed a forecast budget;
- používať burn rate a multi-window alerting;
- navrhnúť error-budget policy s release a incident consequences;
- odlíšiť discretionary risk od remediation a security changes;
- riadiť viac critical SLOs bez neplatného priemerovania;
- zachovať user impact pri shared-dependency attribution;
- overiť reset, recurrence a second-window behavior.

### Toil

- odlíšiť toil od engineering worku, overheadu a grungy worku;
- identifikovať manual, repetitive, automatable, tactical, non-enduring a scale-linked vlastnosti;
- merať frequency, touch time, interruption cost, risk a growth;
- nájsť root operational demand;
- vybrať elimination, redesign, automation, self-service alebo explicit acceptance;
- navrhnúť bezpečnú automation s idempotency, bounded scope a auditom;
- odhaliť toil presunutý na iný tím alebo používateľa;
- preukázať trvalé zníženie demandu bez reliability regresie.

## Cieľ zvládnutia druhého bloku

### Capacity planning

- definovať capacity subject cez business operation, SLO, topology a failure assumptions;
- modelovať unique demand a retry/fan-out amplification;
- mapovať end-to-end constrained resources;
- rozlíšiť configured, installed a effective capacity;
- odvodiť steady-state, burst, failover, rollout a recovery headroom;
- započítať provisioning a provider-quota lead time;
- navrhnúť load, stress, soak, failover a backlog-recovery experiments;
- preukázať second-peak a one-failure-domain acceptance.

### Incident management

- definovať incident subject, declaration criteria a severity;
- oddeliť IC, Operations, Communications a Planning responsibilities;
- udržiavať authoritative incident state;
- používať evidence-preserving stabilization;
- viazať mitigations na hypotheses, owners a abort criteria;
- koordinovať accelerated, ale auditovateľný change control;
- definovať business recovery, handoff a closure criteria;
- overiť adjacent cohort a recurrence watch.

### On-call a escalation

- definovať service support contract a page eligibility;
- odlíšiť delivery, acknowledgement a qualified response;
- navrhnúť primary/secondary coverage a shift handoff;
- používať time, skill, authority, capacity, severity a dependency escalation;
- overiť schedule, timezone, access a vendor contacts;
- merať page quality a sustainable load;
- odstrániť duplicate/nonurgent pages;
- preukázať second-shift a schedule-failure response.

### Runbooks a playbooks

- rozlíšiť repeatable runbook od širšieho playbooku;
- definovať exact document subject, generation a eligibility;
- zapisovať preconditions, safety boundary a decision branches;
- používať read-before-write, dry-run, bounded manifests a idempotency;
- riešiť partial a unknown outcomes cez rollback, compensation alebo reconciliation;
- overiť technical, business, forbidden a second-operation outcomes;
- testovať wrong-subject a stale-generation rejection;
- withdrawnúť a nahradiť nebezpečný dokument bez straty incident evidence.

## Dominantný model sekcie

```text
user a business capability
→ exact reliability/recovery subject
→ objective a tolerance failure-u
→ production evidence
→ risk alebo operational demand
→ bounded decision a action
→ effective-state a business verification
→ recovery alebo learning
→ recurrence a second-operation closure
```

Každá komplexná kapitola musí rozlišovať:

- configured, observed a effective state;
- technical success a user/business outcome;
- trigger, root cause a causal amplifier;
- containment, remediation a recovery;
- activity metric a reliability evidence;
- prvý úspech a second-operation/reconciliation closure.

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
| Root cause analysis | Not Started | L0 |
| Blameless postmortems | Not Started | L0 |
| Backup a restore | Not Started | L0 |
| RPO a RTO | Not Started | L0 |
| Disaster recovery | Not Started | L0 |
| Chaos engineering | Not Started | L0 |
| Operational readiness | Not Started | L0 |

Sekcia zostáva **In progress**. Stav **Ready for user review** možno použiť až po vytvorení všetkých 15 authoritative kapitol, overení ich navigation chainu, glossary, audit artifacts a finálnom section-level consistency passe.
