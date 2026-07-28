# Well-Architected Framework

AWS Well-Architected Framework je opakovateľný architecture-risk review model. Nie je to certifikát, automatic scanner ani checklist, ktorý zmení configured AWS services na preukázane bezpečný a spoľahlivý workload.

Review vytvára hodnotu iba vtedy, keď prepojí business outcome, exact workload generation, aktuálne evidence, konkrétny failure scenario, risk decision, vykonateľnú improvement zmenu a následné overenie.

Dominantný lifecycle:

```text
business outcome a constraints
→ exact workload a review subject
→ current evidence inventory a cut-off
→ question a best-practice applicability
→ evidence-backed answer
→ failure scenario, likelihood a impact
→ risk/trade-off decision
→ owned improvement item alebo expiring acceptance
→ bounded implementation
→ technical a business validation
→ residual-risk verdict a milestone
→ continuous re-review pri zmene
```

Zaškrtnutá odpoveď bez evidence nie je control. Implementovaná zmena bez validation nie je closed risk. Milestone je historický snapshot, nie dôkaz dnešného production state-u.

## 1. Exact workload-review subject

Atlas Payments používa subject `WA-PAY-42`:

```text
workload = CAP-PAY-42
business outcome = authorize, settle and ledger payments exactly once
business owner = Payments Product
technical owner = Atlas Payments Team
criticality = tier 1
users = EU payment clients and internal reconciliation operators

review generation = WA-PAY-2026-07-R3
review date = 2026-07-28
evidence cut-off = 2026-07-28T12:00:00Z
framework/lens generation = AWS Framework Lens + PAYMENTS-CUSTOM-4
previous milestone = WA-PAY-2026-06-M2

production accounts = 100000000042 and shared security/logging accounts
primary Region = eu-central-1
recovery Region = eu-west-1
application release = payments-api 7.18.0
Lambda settlement release = 5.4.0
database subject = DB-PAY-42 / schema SCHEMA-215
recovery subject = REC-PAY-42
security subject = SEC-PAY-42

SLO = 99.95% successful payment API
p99 latency objective = 750 ms
RTO = 2 hours
ledger RPO = 15 minutes

review evidence inventory =
  architecture and data-flow diagrams generation ARCH-31
  IaC commit and deployed-state evidence INFRA-64
  CloudWatch SLI dashboard generation OBS-19
  CloudTrail and security evidence window EVID-42
  failover drill FD-12
  restore test RT-PAY-6
  load test PERF-18
  cost/unit-economics report FIN-PAY-42
  incident and postmortem inventory INC-2026-Q3

forbidden outcomes =
  configured service is accepted as effective control without test evidence
  stale diagram or previous milestone is treated as current production truth
  review excludes external payment provider, CI/CD, people or recovery process
  risk is marked closed when only a ticket or resource exists
  cost optimization removes reliability/security control without explicit decision
  accepted risk has no owner, expiry or re-review trigger
```

Každý finding musí viazať exact question a best practice na workload generation, evidence timestamp, affected component, failure scenario, existing controls, owner, decision, validation a residual risk.

## 2. Workload boundary je business capability, nie AWS diagram

Workload boundary obsahuje všetko, čo musí spolu fungovať, aby business outcome vznikol:

```text
users a channels
→ DNS/edge/API
→ application and event processing
→ databases, objects and queues
→ external payment provider
→ identity, keys and secrets
→ deployment and artifact supply chain
→ observability and incident response
→ backup, reconciliation and recovery
→ teams, on-call, finance and compliance
```

Ak review obsahuje iba production VPC a RDS diagram, ignoruje:

- retry behavior po unknown transaction outcome;
- CI/CD permissions a rollback eligibility;
- external provider idempotency;
- secret rotation consumer refresh;
- restore approval a reconciliation;
- support hours, escalation a decision authority;
- shared observability alebo egress blast radius;
- unit economics a commitment constraints.

Boundary sa zapisuje explicitne. „Managed by another team“ znamená dependency s contractom a ownerom, nie automatické `not applicable`.

## 3. Review subject musí byť versionovaný

Architektúra sa mení. Review answer bez generation identity môže opisovať iný workload než ten, ktorý beží.

Review subject zahŕňa:

- application a schema release;
- accounts, Regions a topology;
- IaC/deployment generation;
- security a recovery policy generations;
- current traffic/capacity profile;
- evidence window;
- open incidents a accepted risks;
- applied lens versions.

Keď sa po review zmení retry policy, target-group routing, KMS key, RTO alebo account boundary, affected answers sú stale aj keď milestone stále existuje.

## 4. Evidence inventory predchádza odpovediam

Pred question walkthroughom tím zhromaždí expected evidence inventory:

```text
question/best practice
→ required observation point
→ authoritative source
→ owner
→ freshness limit
→ expected allowed and forbidden result
```

Príklady:

| Review claim | Slabý dôkaz | Silnejší dôkaz |
|---|---|---|
| Failover funguje | Multi-AZ enabled screenshot | timed failover drill s production client/retry behavior a business reconciliation |
| Backups sú pripravené | backup jobs completed | clean restore generation + application invariants + measured RTO |
| Least privilege je zavedené | policy JSON | effective caller tests, denied forbidden actions, CloudTrail a access review |
| Autoscaling chráni service | scaling policy exists | load/failure test, downstream saturation a recovery evidence |
| Cost je optimalizovaný | recommendation accepted | bounded change, SLO guardrails a realized unit-cost result |

Evidence má timestamp, scope a subject. Live console screenshot bez resource ARN, Region, policy generation a test outcome je slabý audit artifact.

## 5. Question applicability je explicitný verdict

Well-Architected question alebo best practice môže byť:

- applicable a implemented;
- applicable a partially implemented;
- applicable a not implemented;
- not applicable s rationale a evidence;
- unknown, pretože evidence chýba.

`Not applicable` nesmie znamenať „nevieme“ alebo „vlastní to vendor“. External dependency môže zmeniť implementation, ale failure impact zostáva súčasťou workloadu.

Unknown answer je často bezpečnejší než optimistic yes. Vytvára evidence-gathering action namiesto falošne closed risku.

## 6. Šesť pilierov sú pohľady na ten istý outcome

Framework používa šesť pilierov. Nemajú sa riešiť ako šesť nezávislých checklistov. Každý skúma inú časť rovnakého workload lifecycle-u.

### Operational Excellence: vieme systém bezpečne meniť a prevádzkovať?

Atlas overuje:

```text
owner a operating model
→ change/release mechanism
→ observability a decision signals
→ runbook/playbook
→ incident learning
→ improvement closure
```

Evidence zahŕňa deployment/rollback históriu, on-call, runbook executions, alarm tests, postmortems, toil a change-failure metrics.

Configured alarm bez ownera a tested action pathu nie je operational control. Runbook, ktorý sa pri poslednom incidente nepoužil alebo odkazuje na retired topology, je stale evidence.

### Security: kto môže čo vykonať a ako odhalíme zneužitie?

Security pohľad sleduje identity foundation, traceability, infrastructure/data protection, vulnerability management, detection a response.

End-to-end otázka:

```text
human/workload identity
→ effective authorization
→ protected resource/data action
→ telemetry and detection
→ containment
→ credential/key/data recovery
```

Evidence musí obsahovať allowed aj forbidden tests. Encryption enabled bez key-policy, deletion, rotation a recovery modelu je incomplete answer.

### Reliability: čo sa stane pri failure a ako obnovíme business outcome?

Reliability spája quotas, capacity, dependencies, change, failure management, backup a recovery.

```text
failure assumption
→ detection
→ containment/isolation
→ failover/retry/recovery behavior
→ data and external-side-effect reconciliation
→ SLO/RTO/RPO outcome
```

Multi-AZ, queue alebo backup existence sú mechanisms. Reliability answer potrebuje test konkrétneho failure scenario vrátane client, transaction a business semantics.

### Performance Efficiency: spĺňa resource model požiadavky pri reálnom demand-e?

Review skúma resource/service selection, load profile, scaling, saturation, latency distribution a technology evolution.

Average CPU nie je performance model. Atlas používa p50/p95/p99, queue age, database connections/locks, downstream latency, scaling delay a failure headroom.

Performance test musí používať representative request mix, data size, cache state a failure cohort. Benchmark jedného isolated componentu nepreukazuje end-to-end payment latency.

### Cost Optimization: poskytuje workload value pri rozumnom total cost?

Cost pillar spája attribution, unit economics, demand/capacity, commitments, waste a optimization cadence.

```text
business volume and outcome
→ allocated cost
→ unit cost and cost drivers
→ optimization hypothesis
→ reliability/security/performance trade-off
→ realized savings
```

Najnižší účet nie je success, ak znižuje payment success rate, predlžuje recovery alebo zvyšuje toil a incident loss.

### Sustainability: koľko resources spotrebujeme na užitočný outcome?

Sustainability hodnotí demand matching, utilization, software/data efficiency, Region/service/hardware voľbu a lifecycle.

Odstránenie idle capacity môže zlepšiť cost aj sustainability, ale nesmie odstrániť required failover headroom. Environmental a financial outcomes sa prekrývajú, nie sú totožné.

## 7. Cross-pillar trade-off je versionované rozhodnutie

Architecture change sa hodnotí proti všetkým relevantným outcomes.

Príklad: zníženie RDS a application standby capacity:

```text
nižší monthly spend
+ vyššia utilization
- menšia failover headroom
- vyššie recovery saturation risk
- možno dlhší RTO
```

Decision record obsahuje:

- context a exact subject;
- alternatives;
- expected benefit;
- affected pillars;
- failure scenario;
- guardrails a abort criteria;
- owner a approver;
- validation;
- residual risk a review date.

Trade-off nemusí mať „dokonalé“ riešenie. Musí byť vedomý, overiteľný a vlastnený.

## 8. Risk statement musí byť kauzálny

Vágne findingy ako „zlepšiť monitoring“ alebo „nemáme DR“ sa ťažko prioritizujú.

Lepší risk statement:

```text
Pretože payments-api po database connection loss retryuje provider authorization
bez reconciliation podľa business idempotency key,
môže RDS failover po durable commit a stratenom acknowledgement-e
vytvoriť duplicate settlement s finančným a compliance dopadom.
```

Risk record obsahuje:

- trigger/cause;
- mechanizmus;
- affected outcome;
- likelihood evidence;
- impact a blast radius;
- current preventive/detective/recovery controls;
- evidence gaps;
- decision a owner.

Počet HRI/MRI nie je quality metric. Jeden otvorený duplicate-payment risk môže byť dôležitejší než desiatky low-impact findings.

## 9. Configured, effective a accepted control

### Configured

Resource, policy, alarm alebo runbook existuje.

### Effective

Control bol pozorovaný alebo otestovaný proti intended failure/threat a vytvoril required outcome.

### Accepted

Business/technical authority explicitne prijala residual risk po pochopení failure scenario, duration a alternatives.

```text
configured backup plan
≠ effective recovery
≠ accepted residual data-loss risk
```

Review answer má označiť, ktorú úroveň evidence preukazuje.

## 10. Improvement item je bounded change contract

Každá remediation položka potrebuje:

```text
problem/risk
→ exact target state
→ owner a dependency
→ implementation plan
→ safety/rollback model
→ acceptance oracle
→ forbidden outcomes
→ evidence location
→ target date
```

Príklad:

> Zaviesť provider idempotency key viazaný na payment ID, transactional outbox a reconciliation pred retryom; vykonať RDS failover test medzi durable commitom a acknowledgementom; preukázať jeden ledger/provider outcome a nulový duplicate settlement.

„Implementovať idempotenciu“ bez exact boundary a testu nie je closeable item.

## 11. Risk acceptance má expiry a triggers

Accepted risk obsahuje:

- accountable approvera;
- rationale a business context;
- exact residual scenario;
- temporary compensating controls;
- expiry date;
- re-review triggers;
- budget alebo dependency potrebnú na remediation.

Trigger môže byť traffic growth, nový Region, incident, provider contract change, compliance deadline alebo removal compensating control.

Acceptance bez expiry sa stáva neviditeľným permanentným designom.

## 12. Milestone je immutable comparison point

Milestone zachytáva review state v určitom čase. Používa sa na porovnanie:

```text
previous risk/evidence generation
→ implemented changes
→ current validated outcomes
→ new/stale risks
```

Milestone sa vytvára po baseline review, pred launchom, po významnej architecture change, DR/failure drill, major incidente alebo uzavretí dôležitého improvement bloku.

Milestone sám neaktualizuje evidence. Report z júna nemôže preukazovať júlový release bez explicitnej revalidation.

## 13. Lenses a custom controls

Lens je sada questions, best practices a improvement guidance pre domain alebo technology scope. AWS Framework Lens sa môže kombinovať s AWS-provided a organization custom lenses.

Atlas custom lens pridáva otázky pre:

- payment exactly-once boundary;
- provider idempotency/reconciliation;
- PCI/data handling;
- secret rotation loaded-state;
- restore business invariants;
- unit cost per successful payment.

Custom lens nemá kopírovať každú internú policy. Každá otázka musí viesť k failure scenario, evidence a decision.

## 14. Well-Architected Tool je review system of record, nie scanner

AWS Well-Architected Tool podporuje workload definitions, lenses, answers, risk issues, improvement plans, milestones, reports a sharing.

Tool nevie automaticky rozhodnúť:

- či screenshot je aktuálny;
- či failover vytvorí duplicate payment;
- či accepted risk má správneho ownera;
- či restore spĺňa business invariant;
- či optimization trade-off je prijateľný.

Odpoveď je taká kvalitná, ako evidence a reasoning, ktoré tím vložil.

## 15. Worked failure: Multi-AZ screenshot falošne uzavrel reliability risk

### Review answer

Review `WA-PAY-2026-06-R2` odpovedal pozitívne na failure-management a recovery practices, pretože:

- RDS bol Multi-AZ;
- application používala retry library;
- AWS Backup jobs boli green;
- runbook obsahoval „retry request after reconnect“.

Finding bol označený closed. Evidence tvorili console screenshots a architecture diagram. Neexistoval failover test v transaction commit boundary ani provider reconciliation test.

### Production incident

Po RDS failover-e payment `P-884` prešiel týmto lifecycle-om:

```text
provider authorization succeeded
→ database transaction and outbox committed
→ connection dropped before application acknowledgement
→ client/runtime classified result as failure
→ whole operation retried
→ provider received second authorization
```

RDS endpoint sa správne presmeroval a database bola available. Infrastructure control fungoval, ale business reliability zlyhala.

### Competing hypotheses o review failure

1. production drift odstránil pôvodne funkčný control;
2. evidence bola stale;
3. workload boundary nezahŕňala payment provider;
4. question bola interpretovaná ako „máme Multi-AZ“;
5. retry control nebol otestovaný pri unknown commit outcome;
6. risk bol vedome accepted, ale acceptance sa stratila.

### Discriminating evidence

- review evidence neobsahuje provider transaction alebo idempotency boundary;
- architecture diagram končí pri RDS commit-e;
- failover drill inventory neexistuje;
- retry configuration bola rovnaká už počas review, takže nejde o neskorší drift;
- ticket „add idempotency“ bol open bez ownera a nebol linked k risku;
- žiadny risk acceptance record neexistuje.

Root cause je evidence-free control inference. Tím zamenil infrastructure redundancy za end-to-end reliability a existence retry library za bezpečný retry contract.

### Incident containment a recovery

- zastav blind retries a obmedz settlement consumers;
- reconcile provider a ledger podľa payment/idempotency identity;
- refund/void duplicate authorization podľa business runbooku;
- zachovaj failover, database, provider a application evidence;
- implementuj provider idempotency key a transactional reconciliation;
- otestuj failure medzi durable commitom a acknowledgementom.

### Review-system recovery

1. reopen reliability HRI;
2. oprav workload boundary o provider a client retry;
3. nahradiť screenshot evidence failover experimentom;
4. vytvoriť owned improvement item a exact acceptance oracle;
5. rozšíriť custom lens o unknown-outcome scenario;
6. vytvoriť nový milestone až po validated fix-e;
7. skontrolovať podobné optimistic answers v backup, secret rotation a alarms.

### Acceptance verdict

Risk možno uzavrieť až keď:

- failover experiment prejde s production-equivalent clientom;
- provider a ledger obsahujú exactly one business outcome;
- retry po unknown outcome najprv vykoná reconciliation;
- forbidden duplicate authorization nevznikne;
- alarm/runbook vedú k správnej action;
- evidence je linked k exact release/review generation;
- residual provider failure risk má ownera a recovery procedure.

## 16. Continuous Well-Architected

Review sa integruje do delivery a operations:

```text
architecture decision
→ review-impact declaration
→ IaC/policy/static controls
→ deployment evidence
→ SLO/security/cost signals
→ failure and recovery drills
→ findings and improvement backlog
→ validated closure
→ milestone/re-review
```

Automatizovať možno evidence collection pre encryption, public exposure, backup coverage, policy drift, cost anomalies, SLO alebo stale resources. Human review zostáva potrebný pre business boundaries, trade-offs, risk acceptance a outcome validation.

Re-review triggers:

- new Region/account/provider;
- major release alebo data migration;
- changed SLO/RTO/RPO;
- security incident;
- failover/restore test failure;
- material cost or demand change;
- expired accepted risk;
- significant AWS capability or support change.

## 17. Operational readiness a review

Pred launchom alebo major cutoverom review overuje:

- owner, support model a escalation;
- SLO/SLI a alarm action paths;
- capacity, quota a downstream protection;
- deployment, rollback/roll-forward a schema compatibility;
- identity, secrets, encryption and audit;
- backup, failover, restore and reconciliation;
- dependencies and failure contracts;
- cost/unit-economic guardrails;
- runbooks a completed drills.

Operational readiness je decision gate pre konkrétnu release generation. Well-Architected je širší a priebežný risk-improvement system.

## 18. Troubleshooting review procesu

### Odpoveď nemá evidence

Zmeň verdict na unknown/partial a vytvor evidence action. Neakceptuj verbal assurance.

### Stále sa vracajú rovnaké findings

Over root dependency, owner authority, funding, backlog priority, acceptance a či validation skutočne testuje failure mechanism.

### Tool ukazuje low risk, incidenty pokračujú

Over workload boundary, stale milestone, optimistic answers, missing custom scenarios a whether configured controls were mistaken for effective controls.

### Review nevytvoril engineering change

Over ownerov, target dates, dependency order, integration do delivery backlogu a leadership risk decision.

### Pillar teams si odporujú

Vytvor cross-pillar decision record s shared business outcome a measurable guardrails; neoptimalizuj metrics každého tímu izolovane.

## 19. SOA-C03 mapovanie

- **Domain 1** — operational evidence, observability, performance a remediation.
- **Domain 2** — reliability, failure management, backup a business continuity.
- **Domain 3** — operations as code, safe change, automation a improvement execution.
- **Domain 4** — security controls, audit, compliance a incident readiness.
- **Domain 5** — network, DNS, edge, dependency a failure-isolation trade-offs.

## 20. Anti-patterny

### Checklist compliance

Zaškrtne mechanismus bez failure scenario a outcome evidence.

### Review iba nad AWS diagramom

Vynechá users, providers, delivery, people, data a recovery process.

### Configured control ako effective control

Resource existence nenahrádza test.

### HRI closed vytvorením ticketu

Risk zostáva otvorený, kým change neprejde validation.

### Milestone ako current truth

Historical snapshot môže byť stale po ďalšom release.

### `Not applicable` namiesto dependency analýzy

External alebo shared ownership neodstraňuje workload impact.

### Accepted risk bez expiry

Dočasná výnimka sa zmení na permanentný neviditeľný state.

### Izolovaná optimalizácia jedného piliera

Local metric improvement môže poškodiť business outcome alebo iný pillar.

## 21. Praktický risk record

```text
Workload/review generation:
Business outcome:
Question/best practice:
Applicability verdict:
Evidence and timestamp:
Failure scenario:
Cause/mechanism:
Likelihood evidence:
Business/technical impact:
Existing controls and effectiveness:
Decision:
Improvement item:
Owner/approver:
Target date:
Validation and forbidden outcomes:
Residual risk:
Acceptance expiry/re-review trigger:
Milestone:
```

## 22. Kontrolné otázky

1. Prečo workload boundary nie je iba AWS resource diagram?
2. Čo musí obsahovať exact review subject?
3. Ako sa líši configured a effective control?
4. Kedy je answer `unknown` správnejší než `yes`?
5. Ako vytvoríš kauzálny risk statement?
6. Čo potrebuje closeable improvement item?
7. Prečo milestone nie je current-state evidence?
8. Ako sa zaznamenáva cross-pillar trade-off?
9. Prečo Well-Architected Tool nie je scanner?
10. Aký acceptance verdict uzavrie reliability risk?

## Glossary impact

Relevantné pojmy: workload-review subject, evidence cut-off, expected evidence inventory, applicability verdict, configured control, effective control, risk-closure lifecycle, causal risk statement, cross-pillar decision, expiring risk acceptance, improvement validation, milestone generation, review-staleness trigger, business-outcome lens, risk closure verdict a continuous Well-Architected loop.

## Oficiálna dokumentácia

- [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html)
- [The pillars of the framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/the-pillars-of-the-framework.html)
- [AWS Well-Architected Tool](https://docs.aws.amazon.com/wellarchitected/latest/userguide/intro.html)
- [Using lenses](https://docs.aws.amazon.com/wellarchitected/latest/userguide/lenses.html)
- [Milestones](https://docs.aws.amazon.com/wellarchitected/latest/userguide/milestones.html)
- [Implement and track improvements](https://docs.aws.amazon.com/wellarchitected/latest/userguide/implement-and-track-improvements.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: AWS Backup](aws-backup.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Cost management a FinOps →](cost-management-finops.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
