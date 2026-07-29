# Operational readiness

Operational readiness je evidence-backed rozhodnutie, že konkrétna service alebo change generation môže bezpečne vstúpiť do production, byť prevádzkovaná počas day-2 situácií a má jasných ownerov, objectives, controls, recovery paths a residual risks. Nie je to checklist vyplnený tesne pred launchom ani formálny podpis operations tímu.

```text
business/service/change intent
→ exact readiness subject a operating model
→ architecture/dependency/risk inventory
→ reliability/security/capacity/recovery/support requirements
→ current evidence a effective-state verification
→ gaps, blockers a expiring exceptions
→ readiness verdict a launch conditions
→ staged production transition
→ day-2 ownership, telemetry a response
→ actual-vs-expected review
→ change-triggered re-readiness
```

## 1. Readiness subject

Tvrdenie `service je production ready` je príliš široké. Readiness subject má uviesť:

- service alebo capability;
- change/launch type;
- release, configuration a infrastructure generation;
- environment, Region a tenant scope;
- architecture a dependencies;
- expected traffic a critical journeys;
- data classification a business invariants;
- SLO/SLA a error-budget policy;
- support a ownership model;
- recovery/DR generation;
- security a compliance context;
- review evidence cutoff;
- intended launch window;
- readiness owner a decision authority.

Príklad:

```text
review: ORR-PAY-55-v3
capability: merchant settlement completion
change: enable eu-west-1 warm standby for production DR
release: payments 7.26.1
infrastructure: DR-EUW1-18
policy/config: PAY-PROD-33
traffic: zero steady-state customer traffic; up to 100 % after DR activation
objectives: RPO 5 min, RTO 45 min
support: Payments on-call + Cloud Platform + provider P1
review evidence cutoff: 2026-07-29T10:00Z
```

Readiness verdict platí iba pre tento subject a generation. Neprenáša sa automaticky na ďalší Region, release alebo operating model.

## 2. Launch readiness, release readiness a operational readiness

### Release readiness

Overuje, že konkrétny artifact/change je buildnutý, testovaný, policy-compliant a deployable.

### Launch readiness

Overuje business rollout, traffic, stakeholder, support a external-event podmienky konkrétneho launchu.

### Operational readiness

Overuje, že service možno dlhodobo prevádzkovať, pozorovať, obnovovať, škálovať, podporovať a meniť.

```text
artifact je správny
≠ launch je bezpečný
≠ service je day-2 operable
```

Jedna review môže pokrývať všetky tri vrstvy, ale verdicts a evidence majú zostať rozlíšené.

## 3. Production Readiness Review

Production Readiness Review je structured analysis a improvement process, nie jednorazový approval meeting.

Ciele:

- odhaliť production gaps pred customer impactom;
- priradiť ownership a dependencies;
- vyžadovať mechanistické evidence;
- rozlíšiť blocking a nonblocking risk;
- pripraviť day-2 operations;
- znížiť incident severity a recovery time;
- vytvoriť reusable production patterns.

Review má začať počas designu a opakovať sa pri významných zmenách. Late review často objaví blockers v čase, keď business deadline vytvára pressure ich waive-nuť.

## 4. Readiness dimensions

Kompletná readiness review typicky pokrýva tieto dimensions.

### Architecture a dependencies

- current diagram a data/control paths;
- synchronous/asynchronous dependencies;
- failure domains a shared dependencies;
- external providers;
- ownership a support contracts;
- hidden manual alebo batch paths.

### Reliability a service levels

- critical journeys;
- SLI/SLO/SLA;
- error-budget policy;
- partial/cohort failure semantics;
- degradation a overload behavior;
- retry, timeout, idempotency a backpressure.

### Capacity a performance

- logical demand a amplification;
- steady, burst, rollout, failure a recovery capacity;
- quotas a acquisition lead time;
- load/soak/failover evidence;
- dependency capacity a noisy-neighbor risks.

### Observability a alerting

- business-outcome telemetry;
- component/resource signals;
- dashboards a investigation paths;
- page vs ticket eligibility;
- telemetry coverage/retention;
- monitoring of monitoring.

### Incident, on-call a runbooks

- service ownership;
- primary/secondary rotation;
- access a escalation;
- declaration criteria;
- current runbooks/playbooks;
- communication a vendor paths;
- rehearsal a handoff.

### Data, backup a recovery

- acknowledgement/durability contract;
- consistency groups;
- backup coverage a clean points;
- tested restore;
- RPO/RTO;
- DR/fencing/failback;
- reconciliation a unknown-outcome handling.

### Security a compliance

- identity/authorization;
- secrets, keys a certificates;
- data classification;
- threat model;
- vulnerability/supply-chain evidence;
- audit a incident obligations;
- forbidden access paths.

### Change a release management

- immutable artifact a provenance;
- staged rollout/canary;
- schema/config compatibility;
- rollback/roll-forward;
- feature flags;
- old-generation retirement.

### Operations a lifecycle

- provisioning/decommissioning;
- patch/upgrade ownership;
- cost a quota monitoring;
- dependency/version lifecycle;
- toil inventory;
- documentation freshness;
- service retirement plan.

## 5. Evidence, not answers

Checklist answer `áno` má malú hodnotu bez evidence.

Evidence classes:

- immutable test/run/experiment result;
- current production read-back;
- configuration/policy generation;
- restore/failover exercise;
- dashboard/query s defined subjectom;
- runbook rehearsal;
- owner/on-call schedule canary;
- provider contract alebo ticket closed with validation;
- security review a negative test;
- capacity model plus actual load evidence;
- accepted residual-risk record.

Každé evidence má mať:

- subject a scope;
- generation;
- timestamp a expiry;
- producer/authority;
- result a limitations;
- link alebo retrievable artifact;
- reviewer verdict.

```text
checkbox completed
≠ control implemented
≠ control effective
≠ current generation covered
```

## 6. Configured, loaded a effective readiness

Readiness musí rozlišovať:

### Designed

Control je popísaný v architecture alebo plan-e.

### Configured

Resource/policy/runbook existuje.

### Loaded alebo activated

Runtime alebo responder používa intended generation.

### Effective

Control vytvára required outcome na authoritative boundary.

### Rehearsed

Expected aj forbidden scenarios boli overené.

Príklad:

```text
KMS grant v Terraform pláne
→ designed/configured

runtime role grant nevidí
→ nie loaded/effective

synthetic decrypt v recovery Regione prejde
→ effective pre tested subject
```

## 7. Blockers, gaps a recommendations

Review findings musia byť classified.

### Blocking

Bez odstránenia je launch/change neprijateľný, pretože required invariant, legal/security control, recovery path alebo operational capability chýba.

### Conditional blocker

Môže byť riešený explicitnou launch condition, napríklad obmedzeným traffic scope-om alebo disabled feature, ktorý skutočne odstráni exposure.

### High-priority gap

Launch môže prejsť s ownerom, termínom a residual-risk acceptance, ale gap významne zvyšuje incident alebo toil risk.

### Improvement

Zvyšuje efficiency alebo maturity bez bezprostredného ohrozenia readiness.

### Informational

Context alebo future recommendation.

Priority sa nemá meniť iba preto, že launch deadline je blízko.

## 8. Exception lifecycle

Readiness exception potrebuje:

- exact finding a missing mechanismus;
- affected subject/scope;
- business justification;
- quantified risk;
- compensating control;
- ownera a approvera;
- expiry;
- exit criteria;
- launch/traffic limitation;
- monitoring;
- revocation trigger;
- verification po oprave.

Broad exception `operations approves risk` je neplatná. Exception nesmie predstierať, že missing control existuje.

```text
blocker waived
→ risk nezmizol
→ musí byť bounded, visible a expiring
```

## 9. Readiness state machine

```text
Proposed
→ Scoping
→ EvidenceCollection
→ Review
→ Blocked alebo Conditional
→ ReadyForBoundedLaunch
→ Launching
→ OperatingUnderObservation
→ OperationallyAccepted
→ ReReviewRequired
→ Retired
```

Transition má byť viazaný na explicitné gates.

Príklad `ReadyForBoundedLaunch`:

- blocking findings closed;
- exceptions valid;
- launch cohort a duration bounded;
- on-call a incident channels active;
- rollback/recovery paths ready;
- telemetry baseline verified;
- launch authority assigned.

`Deployment succeeded` nemá automaticky prepnúť state na `OperationallyAccepted`.

## 10. Handover a ownership

Service handover nie je odovzdanie dokumentu. Vyžaduje transfer capability a authority.

Handover artifact má obsahovať:

- service/capability scope;
- architecture/dependencies;
- SLO a error budget;
- dashboards/alerts;
- runbooks/playbooks;
- on-call/escalation;
- access a break-glass;
- provider/support contacts;
- known risks a exceptions;
- release/change process;
- backup/restore/DR;
- toil a operational backlog;
- ownership boundaries;
- first-shift a first-incident support plan.

Receiving team musí vedieť vykonať bounded operation, nie iba nájsť wiki stránku.

## 11. Launch gate a staged transition

Readiness verdict má riadiť staged launch:

```text
prelaunch baseline
→ synthetic/internal cohort
→ canary traffic
→ technical + business + support observation
→ bounded expansion
→ full intended scope
→ post-launch observation
→ operational acceptance
```

Každá fáza potrebuje:

- entry criteria;
- exact cohort;
- success a abort criteria;
- observation duration;
- ownera;
- rollback/recovery;
- next-step authority.

Launch pressure nesmie skrátiť observation pod čas potrebný na relevantný failure mode.

## 12. Day-2 readiness

Operational readiness musí pokrývať viac než launch day.

Day-2 events:

- normal releases a configuration changes;
- capacity growth a quota limits;
- certificate/key/secret rotation;
- dependency version changes;
- schema migration;
- on-call turnover;
- incident a provider outage;
- restore a DR activation;
- cost anomaly;
- security vulnerability/compromise;
- deprecation a service retirement.

Pre každú critical class urč:

- detection;
- ownera;
- procedure alebo automation;
- required access;
- validation;
- rollback/recovery;
- evidence retention.

## 13. Re-readiness triggers

Readiness nie je permanentný certifikát. Re-review vyžadujú napríklad:

- nová Region alebo environment;
- major architecture/topology change;
- nový critical dependency;
- SLO/SLA alebo business criticality change;
- data classification alebo regulatory change;
- identity/security model change;
- recovery strategy change;
- major capacity/traffic shift;
- incident alebo near miss odhaľujúci false assumption;
- ownership/on-call transfer;
- provider contract change;
- long interval bez exercise-u;
- accumulated exceptions alebo toil.

Review môže byť proportional, ale musí pokryť zmenený failure surface.

## 14. Worked readiness failure pred `SRE-PAY-55`

Warm-standby launch prešiel review `ORR-PAY-55-v2` dva týždne pred regional incidentom.

Review status obsahoval:

```text
architecture: green
standby database: green
application deployment: green
KMS/runtime decrypt: yellow — ticket open
provider recovery allowlist: yellow — planned before first use
broker checkpoint/fencing: yellow — runbook exists
DR exercise: green — CH-PAY-41 passed
on-call: green — primary rotation exists
business completion monitoring in standby: yellow — dashboard pending
capacity: green — 70 % configured
verdict: conditional green
```

Skutočné evidence limitations:

- `CH-PAY-41` testoval local Pod replacement, nie regional recovery;
- KMS ticket nepotvrdzoval effective decrypt grant;
- provider allowlist nebola implementovaná ani canary-tested;
- runbook bol pre broker v3, production používala v4;
- on-call secondary schedule a provider P1 contact neboli overené;
- standby dashboard sledoval `/healthz` a HTTP `202`, nie completion;
- 70 % configured capacity nebola load-tested s provider slowdown-om;
- yellow findings nemali expiry, launch limitation ani blocking semantics.

Primary operational-readiness root cause bol **review contract, ktorý prijal planned/configured placeholders a nesúvisiace experiment evidence ako effective control a nevedel premeniť kritické yellow gaps na blocking launch conditions**.

Regional outage bol trigger. DR design gaps spôsobili dlhý recovery. Readiness process umožnil, aby známe gaps zostali latentné a nebounded.

## 15. Evidence-preserving response

Po incidente tím zachoval:

- `ORR-PAY-55-v2` snapshot a reviewer comments;
- evidence links a ich pôvodné generations;
- open tickets a due dates;
- launch decision a exceptions;
- actual runtime/readiness state;
- `CH-PAY-41` experiment subject;
- on-call schedule a runbook versions;
- DR timeline a failed assumptions.

Review nebol potichu prepísaný. Historical generation zostala evidence pre process RCA.

## 16. Authoritative readiness redesign

Nový contract `ORR-PAY-55-v3` zaviedol:

### Mandatory blocking gates

- business SLI/SLO a standby completion oracle;
- tested KMS/secret/certificate paths;
- provider egress/callback canary;
- current broker checkpoint a fencing generation;
- current DR runbook rehearsal;
- failure-mode capacity test;
- primary/secondary/vendor contact canary;
- bounded DR exercise s actual RPO/RTO;
- wrong-subject a stale-generation rejection.

### Evidence semantics

```text
design doc
→ requirement evidence

resource exists
→ configured-state evidence

runtime read-back
→ loaded/effective evidence

current exercise
→ behavioral evidence
```

Evidence sa už nesmie substituovať medzi týmito classes bez explicitného limitation verdictu.

### Exception policy

Critical DR/security/data-integrity blockers nemožno waive-nuť všeobecným `conditional green`. Conditional launch musí technicky odstrániť exposure, napríklad neaktivovať Region pre production DR, kým gates neprejdú.

### Acceptance

`OperationallyAccepted` nastáva až po bounded production exercise, on-call handover a post-launch observation, nie po deploymente standby resources.

## 17. Operational-readiness acceptance verdict

Service/change je operationally ready, keď:

- exact readiness subject, operating model a evidence cutoff sú definované;
- architecture a complete dependency graph sú current;
- user journeys, SLO/SLA a error-budget policy sú operationalized;
- capacity, quotas, overload a recovery headroom sú testované;
- observability používa business outcomes a má coverage verdict;
- pages sú actionable a on-call/escalation sú canary-tested;
- runbooks/playbooks sú generation-compatible a rehearsed;
- backup/restore, RPO/RTO a DR prešli current scenario exercise-om;
- security, identity, key, secret a data controls sú effective;
- release, schema/config a rollback/roll-forward paths sú overené;
- blocking findings sú closed mechanistickým evidence;
- exceptions sú exact, bounded, monitored a expiring;
- staged launch má entry/exit/abort criteria;
- ownership a handover capability sú explicitné;
- day-2 events majú detection, procedure a recovery;
- post-launch actual state zodpovedá assumptions;
- forbidden a second-operation scenarios prejdú;
- re-readiness triggers sú versionované.

## 18. Troubleshooting weak readiness procesu

```text
service mala known gap alebo launch-related incident
→ exact readiness review generation
→ subject/scope/evidence cutoff
→ finding classification a decision rights
→ evidence semantics a freshness
→ planned/configured/loaded/effective distinction
→ blockers/exceptions/launch conditions
→ actual launch/runtime state
→ day-2 owner/access/runbook/telemetry
→ incident causal link
→ process + mechanism actions
→ repeat review a bounded launch validation
```

## 19. Earlier controls

- early SRE/operations engagement;
- service-specific PRR template;
- immutable evidence inventory;
- mandatory blocker taxonomy;
- evidence expiry a generation matching;
- independent reviewers;
- exception policy a technical launch limits;
- staged launch state machine;
- current on-call/access/contact canaries;
- recovery/DR exercises;
- handover capability test;
- post-launch review;
- re-readiness triggers a service lifecycle ownership.

## 20. Anti-patterny

### Checklist = readiness

Checklist organizuje otázky; evidence a verdict vytvárajú readiness.

### Operations podpísalo

Podpis bez capability, authority a evidence iba presúva accountability.

### Ticket je control

Open alebo closed ticket nemusí znamenať production-effective mechanismus.

### Conditional green bez podmienky

Je to nebounded risk acceptance.

### Launch prešiel, service je ready

Day-2 operations, recovery a ownership môžu stále chýbať.

### Všetko je blocker

Review sa stane nepoužiteľná a priority stratia význam.

### Nič nie je blocker kvôli deadline-u

Process prestáva chrániť business invarianty.

### Starý game day platí navždy

Evidence môže patriť inej architecture, dependency alebo operating generation.

### Dokumentácia doplnená

Text sám nevytvára alerting, access, capacity ani recovery capability.

## 21. Kontrolné otázky

1. Čo tvorí exact operational-readiness subject?
2. Ako sa release, launch a operational readiness líšia?
3. Aký je cieľ Production Readiness Review?
4. Ktoré readiness dimensions treba typicky pokryť?
5. Prečo checkbox `áno` nestačí?
6. Ako sa designed, configured, loaded, effective a rehearsed state líšia?
7. Ako blocking finding, gap a improvement odlíšiš?
8. Čo musí obsahovať readiness exception?
9. Ako staged launch súvisí s readiness state machine?
10. Prečo `ORR-PAY-55-v2` vytvorila false confidence?
11. Ktoré events vyžadujú re-readiness?
12. Čo musí overiť operational-readiness acceptance verdict?

## Glossary impact

Relevantné pojmy: operational-readiness subject, Production Readiness Review, release readiness, launch readiness, operating model, readiness dimension, readiness evidence inventory, evidence cutoff, readiness blocker, conditional blocker, readiness exception, readiness state machine, handover capability, day-2 readiness, operational acceptance, re-readiness trigger a operational-readiness acceptance verdict.

## Primárne zdroje

- [Google SRE — Production Readiness Reviews](https://sre.google/sre-book/evolving-sre-engagement-model/)
- [Google SRE — Reliable Product Launches at Scale](https://sre.google/sre-book/reliable-product-launches/)
- [Google SRE — Launch Coordination Checklist](https://sre.google/sre-book/launch-checklist/)
- [Google SRE — Creating a Production Launch Plan](https://sre.google/resources/practices-and-processes/production-launch-planning/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Chaos engineering](chaos-engineering.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
