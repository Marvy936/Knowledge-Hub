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

## Authoritative poradie — aktívny blok

1. [Reliability, availability a durability](reliability-availability-durability.md)
2. [SLI, SLO a SLA](sli-slo-sla.md)
3. [Error budgets](error-budgets.md)
4. [Toil](toil.md)

Aktuálny authoritative stav sekcie je **4/15 · In progress**.

## Plánované pokračovanie

Po prvom bloku bude authoritative poradie pokračovať bez zmeny roadmapy:

- Capacity planning
- Incident management
- On-call a escalation
- Runbooks a playbooks
- Root cause analysis
- Blameless postmortems
- Backup a restore
- RPO a RTO
- Disaster recovery
- Chaos engineering
- Operational readiness

## Connected learning scenario

Prvý blok používa incident `SRE-PAY-52` v Atlas Payments:

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

Incident vytvára jeden kauzálny learning chain:

```text
business reliability subject
→ user-centered SLI a SLO
→ completion error-budget consumption
→ policy consequence
→ operational demand a toil classification
→ redesign a safe recovery
```

## Cieľ zvládnutia aktívneho bloku

Po dokončení prvých štyroch kapitol má byť možné:

### Reliability, availability a durability

- definovať exact reliability subject cez required function, stated conditions a period,
- rozlíšiť reliability, availability, correctness, latency a durability,
- vybrať time-based alebo event-based availability model,
- identifikovať partial availability podľa cohortu, Region, operation alebo release generation,
- navrhnúť acknowledgement a durable-state boundary,
- vysvetliť, prečo replication nechráni pred logical corruption,
- overiť reconstructability cez restore a business reconciliation,
- diagnostikovať front-door success pri zlyhanom downstream outcome-e.

### SLI, SLO a SLA

- definovať valid-event population, good event, observation point a measurement generation,
- navrhnúť user-centered availability, latency, correctness, completion a durability indicators,
- rozlíšiť request attempts od unique business operations,
- používať rolling a calendar compliance windows,
- odlíšiť interný SLO od contractual SLA,
- navrhnúť exclusions a missing-data semantics,
- pracovať s provisional, late a corrected outcomes,
- preukázať, že SLO verdict je reprodukovateľný.

### Error budgets

- odvodiť allowed bad events zo SLO a eligible population,
- vysvetliť remaining, consumed a forecast budget,
- používať burn rate a multi-window alerting,
- navrhnúť error-budget policy s release a incident consequences,
- odlíšiť discretionary risk od remediation a security changes,
- riadiť viac critical SLOs bez neplatného priemerovania,
- zachovať user impact pri shared-dependency attribution,
- overiť reset, recurrence a second-window behavior.

### Toil

- odlíšiť toil od engineering worku, overheadu a grungy worku,
- identifikovať manual, repetitive, automatable, tactical, non-enduring a scale-linked vlastnosti,
- merať frequency, touch time, interruption cost, risk a growth,
- nájsť root operational demand,
- vybrať elimination, redesign, automation, self-service alebo explicit acceptance,
- navrhnúť bezpečnú automation s idempotency, bounded scope a auditom,
- odhaliť toil presunutý na iný tím alebo používateľa,
- preukázať trvalé zníženie demandu bez reliability regresie.

## Dominantný model sekcie

SRE and Operations bude používať spoločný model:

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
| Capacity planning | Not Started | L0 |
| Incident management | Not Started | L0 |
| On-call a escalation | Not Started | L0 |
| Runbooks a playbooks | Not Started | L0 |
| Root cause analysis | Not Started | L0 |
| Blameless postmortems | Not Started | L0 |
| Backup a restore | Not Started | L0 |
| RPO a RTO | Not Started | L0 |
| Disaster recovery | Not Started | L0 |
| Chaos engineering | Not Started | L0 |
| Operational readiness | Not Started | L0 |

Sekcia zostáva **In progress**. Stav **Ready for user review** možno použiť až po vytvorení všetkých 15 authoritative kapitol, overení ich navigation chainu, glossary, audit artifacts a finálnom section-level consistency passe.
