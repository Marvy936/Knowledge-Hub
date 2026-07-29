# Chaos engineering

Chaos engineering je disciplinované experimentovanie na systéme s cieľom získať evidence-backed dôveru, že kritická business capability odolá realistickým turbulentným podmienkam. Nie je to náhodné vypínanie resources ani dramatický game day bez hypotézy a closure.

```text
reliability risk alebo unknown
→ exact experiment subject a current generation
→ steady-state a business hypothesis
→ realistic fault alebo condition
→ control a experimental cohort
→ safety boundary a abort criteria
→ authorized injection
→ observation počas faultu a recovery
→ hypothesis verdict
→ weakness/remediation
→ effective-state a recurrence validation
→ second experiment a confidence update
```

## 1. Experiment, test a incident

### Test

Overuje explicitný contract s definovaným oracle-om. Môže byť deterministic a prebiehať mimo production.

### Chaos experiment

Skúša falsifikovať hypotézu o správaní komplexného systemu pod realistickou turbulentnou podmienkou. Outcome môže odhaliť unknown interaction.

### Game day

Koordinované cvičenie ľudí, systems a procedures. Môže obsahovať chaos experiments, ale môže byť aj tabletop alebo disaster-recovery rehearsal.

### Incident

Neplánovaný alebo nekontrolovaný user/business impact. Experiment, ktorý prekročí safety boundary a už nie je riadený, sa musí preklasifikovať na incident.

```text
fault injection bez hypotézy
→ experiment nie je definovaný

hypotéza bez user/business steady state-u
→ technický drill, nie reliability evidence

impact mimo abort/containment contractu
→ incident response
```

## 2. Exact chaos subject

Experiment subject má uviesť:

- business capability a user journey;
- service, environment a Region;
- architecture/release/config generation;
- control a experimental cohorts;
- exact fault target;
- dependency a failure boundary;
- steady-state metrics a populations;
- SLO/error-budget context;
- experiment window;
- owner, approver a responders;
- blast radius;
- abort a recovery mechanisms;
- expected evidence;
- forbidden outcomes.

Príklad:

```text
experiment: CH-PAY-55-2
capability: provider-confirmed settlement completion
release: 7.26.1
control: prod-eu1 tenant cohort A
experimental: prod-euw1 synthetic + 1 % internal cohort
event: provider egress unavailable 8 min
hypothesis: accepted durable intents remain reconstructable;
            completion recovers within 12 min after egress restoration
steady state:
  completion good ratio >= 99.9 %
  no duplicate provider settlement
  queue age <= 10 min
  sent-unknown cohort = 0 after reconciliation
blast radius: max 1 % internal merchants, max 2 000 operations
```

## 3. Reliability question a hypothesis

Silná chaos hypotéza je falsifikovateľná a viazaná na outcome.

```text
za podmienok X
pre subject/cohort Y
keď nastane event Z
systém zachová invariant A
alebo sa obnoví do boundary B
bez forbidden outcome-u C
```

Slabé hypotézy:

- `systém by mal prežiť`;
- `Kubernetes prescheduluje Pody`;
- `DR funguje`;
- `retry policy je správna`.

Silná hypotéza:

```text
ak provider vracia timeouty 8 minút,
unique accepted settlement intents zostanú durable,
provider attempts neprekročia shared retry budget 1.4×,
DB acquire p99 zostane pod 250 ms,
a po obnove provider pathu sa 99 % affected operations
uzavrie do 12 minút bez duplicate settlementu.
```

## 4. Steady state

Steady state opisuje measurable system behavior, nie iba interný component health.

Vhodné steady-state dimensions:

- successful business completion ratio;
- correctness a duplicate/loss rate;
- latency distribution;
- queue age a drain behavior;
- durability/reconstructability;
- user-visible degraded outcome;
- security invariant;
- resource saturation guardrails;
- recovery time;
- reconciliation closure.

Nevhodný jediný oracle:

- Pod count;
- CPU;
- HTTP `/healthz`;
- database process running;
- experiment tool exit code.

Steady state má mať control aj experimental cohort, aby zmena počas experimentu nebola zamieňaná za bežný traffic alebo dependency drift.

## 5. Realistické events

Chaos variables majú reprezentovať relevantné real-world conditions.

### Compute a process

- process crash;
- node loss;
- CPU throttling;
- memory pressure alebo OOM;
- slow startup;
- partial fleet generation loss.

### Network

- latency, packet loss a reordering;
- DNS failure alebo stale cache;
- asymmetric routing;
- dependency connection refusal;
- Region alebo AZ partition;
- MTU alebo TLS handshake failure.

### Data a state

- replica lag;
- unavailable leader;
- disk/full I/O latency;
- stale cache;
- corrupted record alebo schema incompatibility;
- lost acknowledgement/unknown outcome.

### Dependencies a control planes

- provider timeout/429;
- identity issuer unavailable;
- KMS/secret access denied;
- registry/artifact unavailable;
- admission/control plane failure;
- quota exhaustion;
- telemetry pipeline loss.

### Non-failure turbulence

- traffic spike;
- autoscaling event;
- deployment alebo config rollout;
- certificate/key rotation;
- tenant hotspot;
- backlog replay.

Fault frequency nie je jediný prioritization signal. Rare event s catastrophic impact a slabou recovery evidence môže mať vyššiu prioritu než častý bounded failure.

## 6. Preconditions

Pred experimentom over:

- current service owner a on-call coverage;
- no active relevant incident;
- experiment environment a release generation;
- steady-state baseline;
- reliable observability;
- injection tool identity a permissions;
- affected manifest;
- blast-radius controls;
- abort automation;
- recovery mechanism;
- communication channel;
- error-budget/policy eligibility;
- downstream/provider approval, ak je potrebný;
- data-integrity a regulatory constraints.

Experiment nesmie prvýkrát objaviť, že team nemá access, telemetry alebo recovery command.

## 7. Blast radius

Blast radius má dimensions:

- users/tenants;
- operations/events;
- Region/AZ/node/pod count;
- dependency scope;
- data set;
- time;
- traffic percentage;
- financial alebo legal exposure;
- recovery complexity.

Minimize blast radius neznamená urobiť experiment nereprezentatívny. Znamená nájsť najmenší scope, ktorý stále testuje daný failure mechanismus.

```text
jeden Pod kill
→ vhodný pre local replica behavior
→ nevhodný dôkaz regional DR

synthetic request bez provider side effectu
→ vhodný pre edge path
→ nevhodný dôkaz settlement correctness
```

## 8. Safety state machine

Chaos tooling má používať explicitnú state machine.

```text
Draft
→ Reviewed
→ Armed
→ BaselineVerified
→ Injecting
→ Observing
→ Recovering
→ Reconciling
→ Accepted alebo Failed
→ Closed
```

Každý transition potrebuje:

- ownera;
- timestamp;
- preconditions;
- expected state;
- abort path;
- audit evidence.

Forbidden transitions:

- injectovať bez baseline;
- rozšíriť scope bez nového approval;
- označiť experiment `passed`, kým recovery/reconciliation nie sú complete;
- spustiť ďalší fault pri unknown current state-e.

## 9. Abort criteria

Abort criterion musí byť measurable a automaticky alebo rýchlo vyhodnotiteľný.

Príklady:

- completion fast-burn prekročí 14× počas 5 minút;
- affected population presiahne 2 000 operations;
- duplicate provider settlement > 0;
- sent-unknown cohort > 20;
- queue age > 12 minút;
- DB acquire p99 > 500 ms počas 3 minút;
- observability coverage klesne pod required threshold;
- recovery command zlyhá;
- adjacent tenant cohort vykazuje impact.

Abort neznamená iba zastaviť injection. Musí aktivovať recovery a incident declaration, ak impact pretrváva.

## 10. Injection identity a control

Fault injection je privileged operation. Potrebuje:

- exact target manifest;
- least-privilege identity;
- short-lived authorization;
- environment/Region restrictions;
- max scope a duration;
- dry-run/read-back;
- immutable experiment definition;
- dual control pre high-risk faults;
- audit trail;
- kill switch;
- automatic expiry a cleanup.

Broad credential, ktoré dokáže meniť ľubovoľnú production network policy, je independent security risk.

## 11. Observation počas experimentu

Sleduj tri vrstvy:

### Injection evidence

- fault bol applied na intended target;
- effective duration a intensity;
- partial failures injection toolu;
- cleanup state.

### System behavior

- control vs experimental cohort;
- business SLI;
- component path;
- retries, queues a saturation;
- failover/reconciliation state;
- telemetry coverage.

### Human/operational behavior

- page delivery a qualified response;
- runbook eligibility;
- declaration a escalation;
- communication;
- decision latency;
- manual touch points;
- recovery authority.

Chaos môže testovať technický mechanizmus aj organizational response, ale tieto outcomes majú byť hodnotené oddelene.

## 12. Recovery je súčasť experimentu

Experiment nekončí odstránením faultu.

```text
fault removed
→ dependency/service reconnection
→ backlog a retries stabilize
→ data/state convergence
→ business outcomes close
→ temporary overrides removed
→ adjacent cohort valid
→ second operation succeeds
```

Sleduj:

- recovery latency;
- overshoot/oscillation;
- retry storm po obnove;
- stale connections/caches;
- backlog drain;
- duplicate/unknown outcomes;
- operator cleanup;
- recurrence po druhom fault cycle.

## 13. Experiment verdict

Možné verdicts:

### Hypothesis supported

Steady state a recovery boundaries prešli, evidence je complete a forbidden outcomes nenastali.

### Hypothesis falsified

System behavior alebo recovery porušili hypotézu. Experiment je úspešný ako learning, ale reliability claim neprešiel.

### Inconclusive

Fault nebol effective, telemetry bola neúplná, cohort nereprezentatívny alebo concurrent event znemožnil attribution.

### Aborted safely

Safety threshold sa aktivoval a recovery prešla. Reliability claim môže zostať unresolved alebo failed podľa evidence.

### Experiment-induced incident

Impact prekročil controlled boundary alebo recovery nebola bounded. Incident management preberá authority.

`Tool exit code 0` nie je chaos acceptance verdict.

## 14. Remediation closure

Weakness má pokračovať lifecycle-om:

```text
experiment finding
→ exact failure mechanism
→ severity a owner
→ containment alebo risk acceptance
→ engineering control
→ test a rollout
→ production effective-state evidence
→ repeat experiment
→ hypothesis verdict
→ residual risk
```

Action `upraviť runbook` nestačí, ak executable system path zostáva rovnaký. Repeat experiment má použiť rovnaký mechanismus aj alternate cohort alebo second cycle.

## 15. Worked false-confidence experiment pred `SRE-PAY-55`

Pred regional incidentom Atlas evidoval experiment `CH-PAY-41 — Region resilience`, označený ako passed.

Experiment vykonal:

```text
kill 50 % settlement worker Pods v prod-eu1
→ overiť, že Kubernetes vytvorí replacement Pody
→ sledovať HTTP 202 error rate
→ ukončiť po návrate replica countu
```

Chýbalo:

- strata Region/control plane-u;
- standby identity a KMS path;
- provider egress allowlist a callback routing;
- broker checkpoint/fencing;
- DNS cutover;
- standby capacity;
- final settlement completion SLI;
- reconciliation a actual RTO;
- current DR plan generation.

Experiment korektne dokázal iba local worker replacement. Organizational reporting ho však interpretoval ako regional DR evidence.

Primary chaos-engineering failure bol **experiment-subject mismatch: narrow Pod-failure drill bol bez validného causal contractu použitý ako dôkaz end-to-end regional business recovery**.

## 16. Post-remediation experiment `CH-PAY-55-2`

Po incidente tím vytvoril bounded regional recovery experiment.

```text
control: prod-eu1 synthetic merchant cohort
experimental: prod-euw1 internal merchant cohort
faults:
  deny primary provider egress
  freeze primary writer epoch
  activate recovery provider/DNS path
steady state:
  durable acceptance
  provider-confirmed completion
  no duplicate/lost operation
  queue age <= 10 min
  actual recovery <= 45 min
scope:
  max 2 000 operations
  max 1 % internal cohort
```

Preconditions:

- `DR-PAY-55-v4` current;
- KMS decrypt canary prešiel;
- provider recovery allowlist a callbacks verified;
- broker checkpoint generation current;
- on-call, IC a provider contacts active;
- rollback a fencing read-back available.

Experiment odhalil prvú slabinu: DNS cutover bol effective za 94 sekúnd, ale existing client keep-alive sessions držali primary route dlhšie než modelovaných 30 sekúnd. Hypotéza bola falsified bez customer impactu, pretože cohort bol bounded a abort criterion zastavil ramp.

Remediation:

- connection-drain a TTL/keep-alive contract;
- active-path header/read-back;
- client reconnect guardrail;
- updated traffic ramp.

Repeat experiment prešiel:

```text
business recovery: 31 min 42 s
business-consistent recovered point gap: 48 s
confirmed duplicates: 0
confirmed lost intents: 0
sent-unknown after reconciliation: 0
second cycle: passed
```

## 17. Chaos acceptance verdict

Experiment je prijatý, keď:

- exact business/reliability question je definovaná;
- subject, generations, cohorts a fault target sú immutable;
- steady state používa user/business outcome a guardrails;
- hypothesis je falsifikovateľná;
- event je realistický pre modeled risk;
- blast radius je minimálny, ale reprezentatívny;
- current baseline a telemetry coverage sú overené;
- privileged injection má bounded identity, scope a duration;
- abort a recovery state machine sú testované;
- control a experimental observations sú attributable;
- recovery, backlog, reconciliation a second operation sú complete;
- verdict rozlišuje supported, falsified, inconclusive a incident;
- weakness má ownera a mechanism-level remediation;
- repeat experiment overí production-effective control;
- experiment evidence sa nepoužíva na širší claim než testovaný subject.

## 18. Troubleshooting experimentu

```text
experiment nevytvoril dôveru alebo spôsobil incident
→ exact experiment definition/generation
→ question a hypothesis
→ control/experimental cohorts
→ baseline a telemetry coverage
→ injection target/effective fault
→ blast radius/abort behavior
→ concurrent changes/events
→ business steady state
→ recovery a reconciliation
→ verdict scope
→ remediation/effective-state
→ repeat experiment
```

## 19. Earlier controls

- reliability risk register;
- experiment templates a review;
- steady-state business SLI;
- bounded fault catalog;
- injection identity policy;
- scope/duration enforcement;
- automated abort a cleanup;
- incident-command integration;
- experiment calendar/change coordination;
- data/security/legal guardrails;
- finding/action ownership;
- repeat-experiment requirement;
- confidence claim via exact experiment subject.

## 20. Anti-patterny

### Chaos monkey ako stratégia

Random fault bez hypothesis a ownera nevytvára actionable evidence.

### Experiment prešiel, lebo app nepadla

User outcome, correctness, backlog alebo recovery mohli zlyhať.

### Pod kill dokazuje regional DR

Claim je širší než experiment subject.

### Production za každú cenu

Authenticity je dôležitá, ale blast radius, maturity a regulatory boundary majú prednosť.

### Abort = stop injection

Recovery a incident response môžu byť stále potrebné.

### Experiment skončil po obnovení metric

Backlog, retries a unknown outcomes nemusia byť uzavreté.

### Finding bez repeat experimentu

Implementovaná zmena nemusí byť effective alebo môže presunúť failure.

### Tool output je verdict

Orchestration success nie je reliability evidence.

## 21. Kontrolné otázky

1. Ako sa chaos experiment líši od testu, game day a incidentu?
2. Čo tvorí exact chaos subject?
3. Ako sa píše falsifikovateľná steady-state hypotéza?
4. Prečo internal health nestačí ako steady state?
5. Ako vybrať realistic event?
6. Ktoré dimensions má blast radius?
7. Čo má obsahovať safety state machine?
8. Ako abort criterion súvisí s incident declaration?
9. Prečo recovery patrí do experimentu?
10. Prečo `CH-PAY-41` nedokazoval regional DR?
11. Čo znamená inconclusive experiment?
12. Čo musí overiť chaos acceptance verdict?

## Glossary impact

Relevantné pojmy: chaos experiment subject, steady-state hypothesis, chaos variable, control cohort, experimental cohort, blast-radius contract, experiment safety state machine, injection identity, effective fault, chaos abort criterion, experiment-induced incident, chaos evidence scope, hypothesis verdict, remediation repeat experiment a chaos acceptance verdict.

## Primárne zdroje

- [Principles of Chaos Engineering](https://principlesofchaos.org/)
- [Google SRE — Testing for Reliability](https://sre.google/sre-book/testing-reliability/)
- [Google SRE — Emergency Response](https://sre.google/sre-book/emergency-response/)
- [Google SRE — Data Integrity](https://sre.google/sre-book/data-integrity/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Disaster recovery](disaster-recovery.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->