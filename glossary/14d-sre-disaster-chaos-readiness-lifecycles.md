# SRE disaster, chaos a operational-readiness lifecycles

## Business continuity mode

Explicitný dočasný operating contract, ktorý počas disruption zachová iba prioritné capabilities alebo bounded degraded outcomes a určuje user semantics, capacity, maximum duration, reconciliation a exit criteria. Pozri [Disaster recovery](../docs/14-sre-and-operations/disaster-recovery.md).

## Chaos abort criterion

Merateľná podmienka, ktorá zastaví ďalšie fault injection alebo traffic expansion a aktivuje recovery či incident declaration, keď experiment prekračuje approved reliability, data, security alebo blast-radius boundary. Pozri [Chaos engineering](../docs/14-sre-and-operations/chaos-engineering.md).

## Chaos acceptance verdict

Dôkaz, že exact experiment subject, hypothesis, cohorts, effective fault, safety boundary, business steady state, recovery, reconciliation a repeat experiment tvoria scoped reliability claim bez prekročenia forbidden outcomes. Pozri [Chaos engineering](../docs/14-sre-and-operations/chaos-engineering.md).

## Chaos evidence scope

Najširší reliability claim, ktorý môže experiment podporiť podľa skutočne testovaného business subjectu, faultu, cohortu, environmentu, generation, observation a recovery boundary. Pozri [Chaos engineering](../docs/14-sre-and-operations/chaos-engineering.md).

## Chaos experiment subject

Exact business capability, service/environment/release generation, control a experimental cohorts, fault target, steady-state hypothesis, blast radius, safety state machine a evidence window analyzovaného experimentu. Pozri [Chaos engineering](../docs/14-sre-and-operations/chaos-engineering.md).

## Chaos variable

Realistická turbulentná podmienka alebo event zavedený do experimentu, napríklad process loss, network latency, replica lag, dependency timeout, quota exhaustion, traffic spike alebo control-plane failure. Pozri [Chaos engineering](../docs/14-sre-and-operations/chaos-engineering.md).

## Conditional blocker

Readiness finding, ktorý možno pred launchom uzavrieť iba technicky vynútenou podmienkou odstraňujúcou exposure, napríklad disabled feature alebo nulový production traffic do nepripraveného Regionu; všeobecné risk acknowledgement nestačí. Pozri [Operational readiness](../docs/14-sre-and-operations/operational-readiness.md).

## Control cohort — chaos

Porovnávacia population, ktorá počas experimentu nepodlieha intended faultu a pomáha odlíšiť experiment effect od bežného trafficu, deploymentu alebo dependency driftu. Pozri [Chaos engineering](../docs/14-sre-and-operations/chaos-engineering.md).

## Disaster declaration

Explicitný state transition, ktorým authorized owner klasifikuje disruption ako disaster-recovery scenario a aktivuje recovery authority, plan, communication, fencing, alternate environment a objective measurement. Pozri [Disaster recovery](../docs/14-sre-and-operations/disaster-recovery.md).

## Disaster-recovery subject

Exact business capability, disruption scenario, primary/recovery locations, consistency group, strategy, RPO/RTO, release/data/identity/network generations, external dependencies, authority a validation scope analyzovanej recovery. Pozri [Disaster recovery](../docs/14-sre-and-operations/disaster-recovery.md).

## DR acceptance verdict

Dôkaz, že scenario-specific recovery graph, standby generations, identities, keys, network, external dependencies, fencing, capacity, data recovery, business validation, reconciliation, RPO/RTO a failback prešli current-generation exercise-om. Pozri [Disaster recovery](../docs/14-sre-and-operations/disaster-recovery.md).

## DR exercise

Controlled tabletop, component, parallel, partial-traffic alebo full-disruption rehearsal, ktoré meria declaration, activation, recovered point, business recovery, reconciliation a second-responder reproducibility. Pozri [Disaster recovery](../docs/14-sre-and-operations/disaster-recovery.md).

## Effective fault

Overený runtime stav, že intended chaos variable bola aplikovaná na exact target, v schválenej intensity a duration, bez neznámeho partial injection outcome-u. Pozri [Chaos engineering](../docs/14-sre-and-operations/chaos-engineering.md).

## Evidence cutoff — readiness

Timestamp a generation boundary určujúca, ktoré architecture, policy, runtime, exercise a ownership dôkazy boli zahrnuté do readiness verdictu. Pozri [Operational readiness](../docs/14-sre-and-operations/operational-readiness.md).

## Experimental cohort — chaos

Bounded population, environment alebo resource scope, na ktorý sa aplikuje experiment fault a ktorého user/business behavior sa porovnáva s control cohortom. Pozri [Chaos engineering](../docs/14-sre-and-operations/chaos-engineering.md).

## Experiment-induced incident

Stav, keď chaos experiment prekročí controlled safety boundary, vytvorí nebounded user/business impact alebo nemá bounded recovery a authority sa prepne na incident management. Pozri [Chaos engineering](../docs/14-sre-and-operations/chaos-engineering.md).

## Experiment safety state machine

Versionovaný lifecycle `Draft → Reviewed → Armed → BaselineVerified → Injecting → Observing → Recovering → Reconciling → verdict → Closed`, ktorého transitions majú preconditions, owners, abort path a audit evidence. Pozri [Chaos engineering](../docs/14-sre-and-operations/chaos-engineering.md).

## Failback generation

Exact data, writer, routing, identity, application a dependency state použitý na controlled návrat alebo rebalancing z recovery environmentu späť do obnoveného primary environmentu. Pozri [Disaster recovery](../docs/14-sre-and-operations/disaster-recovery.md).

## Handover capability

Preukázaná schopnosť receiving tímu prevádzkovať, meniť, diagnostikovať a obnovovať service s potrebnými objectives, accessom, telemetry, runbooks, contacts a decision authority; nie iba prijatie dokumentácie. Pozri [Operational readiness](../docs/14-sre-and-operations/operational-readiness.md).

## Hypothesis verdict — chaos

Rozhodnutie `supported`, `falsified`, `inconclusive`, `aborted safely` alebo `experiment-induced incident` odvodené z effective faultu, steady state-u, recovery a evidence quality. Pozri [Chaos engineering](../docs/14-sre-and-operations/chaos-engineering.md).

## Injection identity

Short-lived least-privilege principal oprávnený aplikovať iba schválený chaos fault na exact target, environment, scope a duration s auditom, kill switchom a automatic expiry. Pozri [Chaos engineering](../docs/14-sre-and-operations/chaos-engineering.md).

## Launch readiness

Evidence-backed stav, že konkrétny business rollout má pripravené cohorty, capacity, telemetry, support, stakeholder communication, entry/abort criteria a recovery pre plánovaný launch. Pozri [Operational readiness](../docs/14-sre-and-operations/operational-readiness.md).

## Operational acceptance

State transition po bounded launchi a day-2 observation, pri ktorom current service generation spĺňa production objectives, ownership, support, telemetry, recovery a residual-risk contract. Pozri [Operational readiness](../docs/14-sre-and-operations/operational-readiness.md).

## Operational-readiness acceptance verdict

Dôkaz, že exact service/change generation má current architecture, effective reliability/security/capacity/recovery controls, tested ownership a day-2 paths, uzavreté blockers, bounded exceptions a staged production acceptance. Pozri [Operational readiness](../docs/14-sre-and-operations/operational-readiness.md).

## Operational-readiness subject

Exact service alebo capability, change type, release/config/infrastructure generation, environment/Region/cohort, operating model, objectives, evidence cutoff, launch window a decision authority analyzovanej readiness review. Pozri [Operational readiness](../docs/14-sre-and-operations/operational-readiness.md).

## Operating model — readiness

Explicitné rozdelenie service ownershipu, support hours, on-call/escalation, change authority, dependency contracts, objectives, recovery responsibilities, lifecycle a retirement obligations. Pozri [Operational readiness](../docs/14-sre-and-operations/operational-readiness.md).

## Pilot light

DR strategy, pri ktorej critical data a minimálne control components existujú v recovery environment-e, zatiaľ čo väčšina compute, capacity a traffic paths sa aktivuje až počas disaster recovery. Pozri [Disaster recovery](../docs/14-sre-and-operations/disaster-recovery.md).

## Production Readiness Review — PRR

Structured analysis a improvement process, ktorý pred launchom alebo ownership transition overuje production design, objectives, capacity, observability, incident response, security, recovery, support a day-2 operability konkrétneho service subjectu. Pozri [Operational readiness](../docs/14-sre-and-operations/operational-readiness.md).

## Provider DR contract

Versionovaný recovery dependency contract pre external providera vrátane alternate Region endpoints, credentials, egress allowlists, callbacks, quotas, support contacts, consistency semantics a validation canary. Pozri [Disaster recovery](../docs/14-sre-and-operations/disaster-recovery.md).

## Readiness blocker

Finding, bez ktorého closure nie je možné bezpečne prejsť do intended production scope-u, pretože chýba required business invariant, security/data control, operational ownership alebo recovery capability. Pozri [Operational readiness](../docs/14-sre-and-operations/operational-readiness.md).

## Readiness dimension

Jedna analyzovaná oblasť production operability, napríklad architecture/dependencies, service levels, capacity, observability, incident/on-call, data/recovery, security, release alebo lifecycle operations. Pozri [Operational readiness](../docs/14-sre-and-operations/operational-readiness.md).

## Readiness evidence inventory

Versionovaný zoznam dôkazov viazaných na readiness requirements, subjects, authorities, generations, timestamps, expirations, limitations a reviewer verdicts. Pozri [Operational readiness](../docs/14-sre-and-operations/operational-readiness.md).

## Readiness exception

Exact, approved, monitored a expiring residual-risk contract pre konkrétny readiness gap, ktorý uvádza scope, justification, compensating controls, ownera, launch limitation, exit criteria a revocation trigger. Pozri [Operational readiness](../docs/14-sre-and-operations/operational-readiness.md).

## Readiness state machine

Lifecycle `Proposed → Scoping → EvidenceCollection → Review → Blocked/Conditional → ReadyForBoundedLaunch → Launching → OperatingUnderObservation → OperationallyAccepted → ReReviewRequired/Retired`. Pozri [Operational readiness](../docs/14-sre-and-operations/operational-readiness.md).

## Recovery authority

Principal alebo role oprávnená deklarovať disaster, aktivovať alternate environment, fence-núť writers, meniť recovery routing a prijať recovery/failback verdict podľa explicitného decision contractu. Pozri [Disaster recovery](../docs/14-sre-and-operations/disaster-recovery.md).

## Recovery environment generation

Exact infrastructure, application, configuration, identity, key, data, network, DNS, provider a observability state pripravený alebo aktivovaný pre disaster recovery. Pozri [Disaster recovery](../docs/14-sre-and-operations/disaster-recovery.md).

## Recovery graph

Directed dependency model celej business recovery capability od routing, identity a runtime cez data/broker/provider paths po telemetry, support a reconciliation, pričom každý node/edge má ownera, mechanismus a validation oracle. Pozri [Disaster recovery](../docs/14-sre-and-operations/disaster-recovery.md).

## Recovery strategy tier

Zvolený contingency model, napríklad backup/restore, pilot light, warm standby, active-passive alebo active-active, odvodený z BIA, failure scenarios, RPO/RTO, complexity a costu. Pozri [Disaster recovery](../docs/14-sre-and-operations/disaster-recovery.md).

## Recovery traffic cutover

Versionovaný transition klientského alebo internal trafficu na validated recovery generation s routing identity, cache/connection behaviorom, ramp stages, guardrails, abortom a read-backom. Pozri [Disaster recovery](../docs/14-sre-and-operations/disaster-recovery.md).

## Regional writer fencing

Mechanizmus, ktorý pred promotion alternate Regionu odníme alebo epoch-bound obmedzí write authority old primary systému a zabráni split brainu a divergentným writes. Pozri [Disaster recovery](../docs/14-sre-and-operations/disaster-recovery.md).

## Re-readiness trigger

Architecture, dependency, Region, traffic, security, recovery, ownership, incident alebo lifecycle change, ktorý zneplatňuje časť existujúceho readiness evidence a vyžaduje proportional review novej generation. Pozri [Operational readiness](../docs/14-sre-and-operations/operational-readiness.md).

## Release readiness

Evidence-backed stav, že exact software/configuration artifact má complete build, test, policy, compatibility, deployment a recovery evidence pre zamýšľanú release transition. Pozri [Operational readiness](../docs/14-sre-and-operations/operational-readiness.md).

## Remediation repeat experiment

Opakovaný chaos experiment po production-effective change, ktorý skúša pôvodný failure mechanismus a často alternate cohort alebo second cycle, aby preukázal recurrence closure. Pozri [Chaos engineering](../docs/14-sre-and-operations/chaos-engineering.md).

## Steady-state hypothesis

Falsifikovateľné tvrdenie, že definovaný user/business outcome, invariant alebo recovery boundary zostane zachovaný pre exact cohort počas a po realistickom turbulentnom evente. Pozri [Chaos engineering](../docs/14-sre-and-operations/chaos-engineering.md).

## Warm standby

DR strategy, pri ktorej zmenšená priebežne aktualizovaná service generation existuje v recovery environment-e, ale pred plným použitím potrebuje scale-up, dependency activation, validation a traffic cutover. Pozri [Disaster recovery](../docs/14-sre-and-operations/disaster-recovery.md).

## Work recovery

Fáza po technickom obnovení service, v ktorej sa drainuje backlog, reconciliujú post-point alebo unknown operations, obnovuje batch/support práca, odstraňujú temporary overrides a uzatvára customer/business impact. Pozri [Disaster recovery](../docs/14-sre-and-operations/disaster-recovery.md).