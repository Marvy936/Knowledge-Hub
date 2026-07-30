# Operational readiness

Operational readiness je evidence-backed rozhodnutie, že presná service alebo change generation môže bezpečne vstúpiť do production, zvládnuť day-2 operating events a má current ownership, reliability objectives, capacity, security, observability, response a recovery mechanisms. Nie je to checklist vyplnený pred launchom, podpis operations tímu ani súčet green component statuses.

Readiness verdict musí odlíšiť, čo je navrhnuté, nakonfigurované, načítané, efektívne a rehearse-nuté. Design dokument môže správne opisovať KMS grant, resource môže existovať a ticket môže byť closed, pričom recovery runtime stále nevie key použiť. Operational acceptance preto vzniká až na authoritative user, runtime a recovery boundaries.

## 1. Dominantný intent-to-operational-acceptance lifecycle

Readiness začína service alebo change intentom a končí až production observation a explicitnou day-2 acceptance. Review počas designu odhaľuje gaps včas; staged launch a early-life support overujú assumptions na current generation. Významná zmena alebo incident následne vráti subject do re-review.

```text
business/service/change intent
→ exact readiness subject a operating model
→ architecture, dependency, risk a ownership inventory
→ reliability/security/capacity/recovery/support requirements
→ current evidence generations a effective-state read-back
→ blockers, gaps a bounded exceptions
→ readiness verdict a launch conditions
→ staged production transition s abort/recovery
→ day-2 ownership, telemetry a response
→ actual-versus-expected operational review
→ OperationallyAccepted alebo ReReviewRequired
→ change-triggered re-readiness a retirement
```

Deployment success je iba jeden transition. Service môže byť release-ready a launch-ready, no day-2 neoperable, ak chýba qualified on-call, provider escalation, restore path alebo certificate rotation ownership.

## 2. Exact readiness subject a evidence cutoff

Tvrdenie `service je production ready` je príliš široké. Subject zachováva capability, change/launch type, release/config/infrastructure generation, environment/Region/tenant scope, architecture/dependencies, expected traffic a critical journeys, data/security invariants, SLO/SLA a budget policy, support model, recovery generation, review evidence cutoff, launch window, ownera a decision authority.

```text
review: ORR-PAY-55-v3
capability: merchant settlement completion
change: enable prod-euw1 warm standby pre production DR
release: payments 7.26.1
infrastructure: DR-EUW1-18
policy/config: PAY-PROD-33
traffic: zero steady-state; up to 100 % po DR activation
objectives: RPO 5 min, RTO 45 min
support: Payments on-call + Cloud Platform + provider P1
evidence cutoff: 2026-07-29T10:00Z
```

Verdict platí iba pre túto generation a operating model. Nový Region, broker architecture, provider contract, data classification alebo ownership transfer vytvára nový alebo proportional re-readiness subject.

## 3. Release, launch a operational readiness

Release readiness overuje artifact/change: build, tests, policy, compatibility a deployability. Launch readiness overuje konkrétny business rollout: cohort, timing, stakeholders, support, dependencies a communication. Operational readiness overuje dlhodobú prevádzku: observability, capacity, on-call, runbooks, recovery, lifecycle a changes.

```text
artifact je správny a deployable
≠ launch window a cohort sú bezpečné
≠ service je dlhodobo operable
```

Jedna review môže zhromaždiť evidence pre všetky vrstvy, ale verdicts musia zostať oddelené. Safe release artifact nepreukazuje provider capacity počas campaign peak-u a úspešný launch nepreukazuje DR activation o tri mesiace neskôr.

## 4. Production Readiness Review ako design a risk process

Production Readiness Review — PRR — má začať počas designu, nie deň pred deadline-om. Odhaľuje production gaps, priraďuje ownership, vyžaduje mechanistické evidence, pripravuje day-2 operations a vytvára reusable platform patterns. Late review tlačí reviewers k waiverom, pretože architecture a external contracts už nemožno lacno zmeniť.

Review nie je approval theater. Každá otázka musí byť viazaná na risk alebo required outcome a mať evidence class, freshness, ownera a consequence. Independent reviewer má authority označiť blocker; service owner vysvetľuje operating model; business/security/data authorities rozhodujú o residual risku, ktorý presahuje technical ownership.

## 5. Readiness dimensions ako jeden operating system

Readiness dimensions sa nepoužívajú ako izolované checklist columns, ale ako prepojené boundaries jedného service outcome-u.

Architecture a dependency evidence ukazuje data/control paths, sync/async dependencies, failure domains, providers a hidden manual/batch paths. Reliability evidence definuje critical journeys, SLI/SLO/SLA, budget policy, partial failures, overload, retry/idempotency a degradation. Capacity evidence pokrýva logical demand, amplification, steady/burst/failure/recovery headroom, quotas a load/failover tests.

Observability a support evidence prepája business telemetry, investigation signals, page/ticket eligibility, monitoring coverage, on-call rotation, access, declaration/escalation, runbook rehearsal a vendor contacts. Data/recovery evidence pokrýva acknowledgement, consistency groups, backup/clean points, restore, RPO/RTO, DR, fencing a unknown-outcome reconciliation.

Security/change/lifecycle evidence zahŕňa identity/authorization, secrets/keys/certificates, data classification, threat a supply-chain controls, immutable artifacts, schema/config compatibility, rollout/rollback, upgrades, cost/quota, toil, documentation freshness a retirement.

Tieto dimensions sa nesmú spriemerovať. Chýbajúci decrypt path alebo data-integrity invariant je blocker aj pri silnej observability a nízkom CPU.

## 6. Evidence semantics a readiness generations

Checkbox `áno` má malú hodnotu bez subjectu, generation, timestamp/expiry, authority, resultu, limitations a reviewer verdictu. Evidence môže byť immutable test/experiment, current runtime read-back, policy/config generation, restore/DR exercise, dashboard/query, runbook rehearsal, schedule/contact canary, security negative test, capacity experiment alebo accepted residual-risk record.

Readiness rozlišuje päť stavov:

```text
designed
→ control je popísaný

configured
→ resource/policy/runbook existuje

loaded/activated
→ intended generation používa runtime alebo responder

effective
→ control vytvára required outcome na authoritative boundary

rehearsed
→ expected aj forbidden scenario prešli
```

Terraform plan s KMS grantom je designed/configured evidence. Runtime role, ktorá grant nevidí, nie je loaded/effective. Synthetic decrypt v recovery Regione pre current runtime identity vytvára effective behavioral evidence pre tested subject. Evidence sa medzi classes nesmie substituovať bez explicitného limitation verdictu.

## 7. Findings, blockers a decision rights

Finding classification vyjadruje consequence. Blocking finding znamená chýbajúci required invariant, legal/security/data control, recovery path alebo operational capability. Conditional blocker možno technicky neutralizovať presnou launch condition, napríklad vypnutým feature alebo nulovým customer trafficom. High-priority gap môže prejsť iba s bounded risk acceptance; improvement zvyšuje maturity a informational item zachováva context.

Deadline nesmie meniť technical classification. Ak business zmení scope tak, že exposure skutočne zmizne, verdict sa môže zmeniť. Formulácia `conditional green`, ktorá iba sľubuje budúci ticket bez odstránenia exposure, nie je condition, ale nebounded waiver.

Decision rights musia byť explicitné. SRE reviewer nemá sám akceptovať legal data-loss risk; business owner nemá prehlásiť nefunkčný cryptographic control za effective. Shared decision zachováva, kto vlastní mechanismus, kto risk a kto launch authority.

## 8. Exception lifecycle

Exception obsahuje exact missing mechanismus a subject, justification, quantified risk, compensating control, ownera/approvera, expiry, exit criteria, traffic/feature limitation, monitoring, revocation trigger a verification po oprave.

```text
blocker waived
→ mechanismus stále chýba
→ exposure musí byť technicky bounded
→ risk musí zostať visible, monitored a expiring
```

Critical DR, security alebo data-integrity gap nemožno premeniť na general `operations approves`. Ak recovery Region nemá decrypt grant, validná condition je neaktivovať ju pre production DR, kým canary neprejde; open ticket s plánovaným fixom capability neposkytuje.

Expired exception automaticky neznamená, že launch je bezpečný. State sa vráti do blocked/re-review a owner musí exposure odstrániť alebo vykonať nový explicitný risk decision.

## 9. Readiness state machine a staged launch

Praktický lifecycle:

```text
Proposed → Scoping → EvidenceCollection → Review
→ Blocked | Conditional | ReadyForBoundedLaunch
→ Launching → OperatingUnderObservation
→ OperationallyAccepted | ReReviewRequired
→ Retired
```

`ReadyForBoundedLaunch` vyžaduje closed blockers, valid exceptions, bounded cohort/duration, active on-call/incident channels, ready rollback/recovery, telemetry baseline a assigned launch authority. Staged transition vedie cez synthetic/internal cohort, canary, technical/business/support observation, bounded expansion a full intended scope.

Každá fáza má entry, exact cohort, success/abort criteria, duration, ownera, rollback/recovery a next-step authority. Observation sa nesmie skrátiť pod čas failure mode-u iba pre deadline. Deployment controller nemá automaticky nastaviť `OperationallyAccepted`; tento verdict vzniká po production read-backu a early-life observation.

## 10. Handover a day-2 capability

Handover nie je odovzdanie wiki stránky. Receiving team musí vedieť nájsť subject, pochopiť architecture/dependencies, interpretovať SLO/budget, používať telemetry, reagovať cez on-call/escalation, získať bounded access, vykonať runbook/recovery a riadiť release/change lifecycle.

Handover artifact zahŕňa dashboards/alerts, runbooks/playbooks, provider contacts, known risks/exceptions, backup/DR, toil/backlog, ownership boundaries a first-shift/first-incident plan. Capability sa overuje shadowingom, rehearsal-om alebo bounded operation, nie podpisom attendance listu.

Day-2 readiness pokrýva releases/config changes, capacity/quota growth, certificate/key/secret rotation, dependency versions, schema migration, on-call turnover, incident/provider outage, restore/DR, cost anomaly, vulnerability/compromise, deprecation a retirement. Každá critical class potrebuje detection, ownera, procedure/automation, access, validation, rollback/recovery a evidence retention.

## 11. Re-readiness triggers a continuous assurance

Readiness nie je permanentný certifikát. Re-review vyvoláva nový Region, major topology, critical dependency, SLO/business criticality, data classification/regulation, identity/security model, recovery strategy, large traffic shift, incident/near miss, ownership transfer, provider contract change, dlhý interval bez exercise-u alebo accumulated exceptions/toil.

Review môže byť proportional, ale musí pokryť changed failure surface. Incident `SRE-PAY-55` nezrušil všetky predošlé evidence; invalidoval však DR, provider, broker, on-call a chaos assumptions a preto vyžadoval targeted re-readiness.

Continuous assurance môže používať evidence expiry, canaries, policy checks a scheduled drills. Automatizácia má signalizovať stale alebo mismatched generation, nie sama prehlásiť business risk za accepted.

## 12. Readiness failure pred `SRE-PAY-55`

Warm-standby review `ORR-PAY-55-v2` označila architecture, database, deployment, capacity a DR exercise green; KMS decrypt, provider allowlist, broker fencing a completion monitoring boli yellow. Verdict bol `conditional green`.

Evidence však nebola equivalentná. `CH-PAY-41` testoval local Pod replacement, nie regional recovery. KMS ticket nedokazoval runtime decrypt. Provider path nebola implementovaná ani canary-tested. Runbook patril broker v3, production používala v4. Secondary schedule/provider contact neboli overené. Dashboard sledoval `/healthz` a `202`. Configured capacity 70 % nebola load-tested pod provider slowdown-om. Yellow gaps nemali expiry, technical launch limitation ani blocking semantics.

Root cause readiness failure-u bol review contract, ktorý prijal planned/configured placeholders a nesúvisiace experiment evidence ako effective control a nevedel premeniť critical yellow gaps na blocking conditions. Regional outage bol trigger; DR gaps vytvorili impact; readiness process dovolil known exposure zostať latentné a nebounded.

## 13. Authoritative redesign `ORR-PAY-55-v3`

Nový contract zaviedol mandatory gates: business completion SLI, tested KMS/secret/certificate paths, provider egress/callback canary, current broker checkpoint/fencing, current DR runbook rehearsal, failure-mode capacity test, primary/secondary/vendor contact canary, bounded DR exercise s actual RPO/RTO a wrong-subject/stale-generation rejection.

Evidence classes zostávajú explicitné:

```text
design doc → requirement/design evidence
resource exists → configured-state evidence
runtime read-back → loaded/effective evidence
current exercise → behavioral evidence
```

Critical blockers nemožno waive-nuť general green. Conditional launch musí exposure technicky odstrániť. `OperationallyAccepted` nastáva až po bounded production exercise, handover a post-launch observation. Historical `ORR-PAY-55-v2` zostáva immutable process-RCA evidence; neprepísala sa spätne.

## 14. Operational-readiness acceptance contract

Positive path musí preukázať current subject, complete dependency/ownership model, operationalized SLO/budget, tested capacity/overload, business observability, qualified support, rehearsed procedures, current recovery/security/change controls a staged launch evidence. Conditional path musí technicky odstrániť exposure a expirovať. Day-2 path overuje rotation, key/certificate change, incident a restore capability. Re-readiness path musí správne invalidovať stale evidence po významnej zmene.

Forbidden paths zahŕňajú checkbox alebo ticket ako control, design/configured evidence vydávané za effective, unrelated old game day, broad conditional green, deploy success ako acceptance, handover bez capability a exception bez expiry/traffic limitation.

```text
positive:
current evidence → bounded launch → production read-back → day-2 acceptance

conditional:
exposure removed by scope/control → monitored expiry → close alebo block

re-readiness:
meaningful change/incident → stale evidence invalidated → targeted review

forbidden:
ticket/open plan as effective control
component health as business oracle
old generation evidence
operations signature without authority
launch deadline changes risk class
```

Verdict patrí exact generation a evidence cutoff. Second operation, new responder a alternate scenario testujú, či readiness nie je pripravená iba pre review meeting.

## 15. Troubleshooting weak readiness procesu

Ak launch-related incident odhalí known gap, sleduj exact review generation, subject/scope/cutoff, finding classification a decision rights, evidence semantics/freshness, designed/configured/loaded/effective distinction, blockers/exceptions/conditions, actual launch/runtime state, day-2 ownership/access/runbooks/telemetry a causal link k incidentu.

```text
known gap alebo false green
→ review subject/generation
→ requirement a evidence class
→ freshness a scope match
→ finding/blocker/exception decision
→ launch condition vs actual state
→ day-2 behavior
→ incident mechanism
→ process a technical actions
→ repeat review a bounded validation
```

Review template sa nemení iba pridaním ďalšieho checkboxu. Náprava musí opraviť evidence substitution, decision rights alebo missing execution boundary, ktorá false verdict dovolila.

## 16. Anti-patterny

Operational-readiness anti-patterny vytvárajú administratívny pocit kontroly bez production capability.

- **Checklist equals readiness —** checklist organizuje otázky; current evidence a consequence vytvárajú verdict.
- **Operations podpísalo —** podpis bez authority, access a capability iba presúva accountability.
- **Ticket je control —** planned alebo closed work nemusí byť deployed/effective.
- **Conditional green bez condition —** je nebounded risk acceptance bez odstránenia exposure.
- **Launch prešiel, service je ready —** day-2 support, recovery a lifecycle môžu chýbať.
- **Všetko je blocker —** priority a decision usefulness zaniknú.
- **Nič nie je blocker kvôli deadline-u —** review prestane chrániť business invarianty.
- **Starý game day platí navždy —** evidence patrí inej architecture alebo dependency generation.
- **Dokumentácia doplnená —** text sám nevytvára alerting, access, capacity ani recovery.

## 17. Kontrolné otázky

1. Čo tvorí exact readiness subject a evidence cutoff?
2. Ako sa release, launch a operational readiness líšia?
3. Prečo PRR začína počas designu?
4. Ako readiness dimensions tvoria jeden operating system?
5. Ako designed, configured, loaded, effective a rehearsed state odlíšiš?
6. Čo robí finding blocking alebo conditional?
7. Čo musí obsahovať exception?
8. Ako state machine a staged launch súvisia?
9. Čo musí receiving team vedieť po handoveri vykonať?
10. Ktoré events vyžadujú re-readiness?
11. Prečo `ORR-PAY-55-v2` vytvorila false confidence?
12. Ktoré positive, conditional, re-readiness a forbidden paths patria do acceptance?

## Glossary impact

Relevantné pojmy: operational-readiness subject, evidence cutoff, release/launch/operational readiness, Production Readiness Review, readiness dimension, evidence class, designed/configured/loaded/effective/rehearsed state, readiness blocker, conditional launch, readiness exception, readiness state machine, handover capability, day-2 readiness, re-readiness trigger a operational acceptance contract.

## Primárne zdroje

- [Google SRE — Production Readiness Reviews](https://sre.google/sre-book/evolving-sre-engagement-model/)
- [Google SRE — Reliable Product Launches at Scale](https://sre.google/sre-book/reliable-product-launches/)
- [Google SRE — Launch Coordination Checklist](https://sre.google/sre-book/launch-checklist/)
- [Google SRE — Production Launch Planning](https://sre.google/resources/practices-and-processes/production-launch-planning/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Chaos engineering](chaos-engineering.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Relational vs. non-relational databases →](../15-databases-and-distributed-systems/relational-vs-non-relational-databases.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
