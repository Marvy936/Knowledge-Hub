# SRE capacity, incident, on-call and runbook lifecycle glossary entries

## Capacity-planning subject

Exact business operation, valid demand population, tenant/Region/cohort, release/configuration/topology generation, SLO, dependency/quota state, failure assumptions, planning window a provisioning lead time analyzovaného capacity modelu. Pozri [Capacity planning](docs/14-sre-and-operations/capacity-planning.md).

## Logical demand unit — capacity

Jedna unique business operation, napríklad settlement intent, oddelená od HTTP retries, broker redeliveries, provider attempts a internal fan-out calls. Pozri [Capacity planning](docs/14-sre-and-operations/capacity-planning.md).

## Demand amplification — capacity

Pomer technických attempts, retries, redeliveries alebo fan-out operácií voči unique business demandu, ktorý určuje skutočný pressure na required service boundaries. Pozri [Capacity planning](docs/14-sre-and-operations/capacity-planning.md).

## Service capacity model

End-to-end model required processing boundaries, ich sustainable throughputu, concurrency, queueing, dependency limits a failure behavioru pre konkrétny business operation subject. Pozri [Capacity planning](docs/14-sre-and-operations/capacity-planning.md).

## Constrained resource — capacity

Required resource alebo dependency boundary, ktorého sustainable capacity aktuálne limituje end-to-end business throughput alebo SLO. Pozri [Capacity planning](docs/14-sre-and-operations/capacity-planning.md).

## Effective service capacity

Kapacita skutočne dostupná analyzovanému business subjectu po odpočítaní unhealthy members, reservations, topology constraints, safe utilization margin, rollout/failover reserve a external quotas. Pozri [Capacity planning](docs/14-sre-and-operations/capacity-planning.md).

## Steady-state headroom

Rezerva effective capacity nad očakávaným normal demandom určená na forecast uncertainty, krátke bursty a control latency. Pozri [Capacity planning](docs/14-sre-and-operations/capacity-planning.md).

## Failover headroom

Remaining effective capacity po strate definovaného failure domainu, ktorá musí udržať critical workload v požadovanom degraded alebo full SLO contracte. Pozri [Capacity planning](docs/14-sre-and-operations/capacity-planning.md).

## Recovery headroom

Kapacita umožňujúca súčasne obsluhovať live demand a bezpečne drainovať backlog alebo rekonštruovať state po incidente. Pozri [Capacity planning](docs/14-sre-and-operations/capacity-planning.md).

## Acquisition lead time — capacity

Čas od identifikácie capacity potreby cez approval, quota/hardware získanie, provisioning, warmup a validation po production availability. Pozri [Capacity planning](docs/14-sre-and-operations/capacity-planning.md).

## Queue drain rate

Rozdiel medzi completed service rate a new arrival rate pre konkrétnu queue population; kladná hodnota znamená, že backlog sa zmenšuje. Pozri [Capacity planning](docs/14-sre-and-operations/capacity-planning.md).

## Overload contract

Explicitné pravidlá admission controlu, prioritization, load sheddingu, backpressure, degraded mode-u a caller-visible failure semantics pri prekročení safe completion capacity. Pozri [Capacity planning](docs/14-sre-and-operations/capacity-planning.md).

## Capacity acceptance verdict

Dôkaz, že demand, amplification, constrained resources, headroom, provisioning lead time a overload behavior sú správne modelované a load/failover/backlog-recovery experiment potvrdil original aj degraded business outcome. Pozri [Capacity planning](docs/14-sre-and-operations/capacity-planning.md).

## Second-peak validation

Opakovaný production-like alebo controlled peak test po capacity zmene, ktorý preukazuje, že first successful recovery nebol jednorazový alebo závislý od hidden manuálneho override-u. Pozri [Capacity planning](docs/14-sre-and-operations/capacity-planning.md).

## Incident subject

Exact business capability, affected outcome, start/detection/declaration timeline, tenant/Region/cohort, release/configuration/topology generations, SLO impact, active mitigations a command ownership jedného incidentu. Pozri [Incident management](docs/14-sre-and-operations/incident-management.md).

## Incident declaration

Explicitný transition z normal troubleshootingu do coordinated incident režimu s pridelenou severity, authority, roles, communication a recovery contractom. Pozri [Incident management](docs/14-sre-and-operations/incident-management.md).

## Severity contract — incident

Organizačný model mapujúci user/business/data/security impact a growth uncertainty na response urgency, roles, communication a escalation požiadavky. Pozri [Incident management](docs/14-sre-and-operations/incident-management.md).

## Incident Commander — IC

Rola vlastniaca incident objective, priority, command structure, decision cadence, escalation, handoff a closure; nemusí byť najhlbším technical expertom. Pozri [Incident management](docs/14-sre-and-operations/incident-management.md).

## Incident Operations lead

Rola koordinujúca technical hypotheses, observations, bounded changes a effective outcomes počas incidentu. Pozri [Incident management](docs/14-sre-and-operations/incident-management.md).

## Incident Communications lead

Rola publikujúca potvrdený impact, current action a update cadence pre interných alebo externých stakeholders bez zamieňania hypothesis za fact. Pozri [Incident management](docs/14-sre-and-operations/incident-management.md).

## Incident Planning lead

Rola sledujúca staffing, handoffs, logistics, temporary divergence, follow-up work a dlhší recovery horizon. Pozri [Incident management](docs/14-sre-and-operations/incident-management.md).

## Incident state document

Authoritative priebežný záznam incident subjectu, impactu, timeline-u, hypotheses, evidence, actions, owners, risks, communication a recovery criteria. Pozri [Incident management](docs/14-sre-and-operations/incident-management.md).

## Incident stabilization

Evidence-preserving bounded actions určené na zastavenie rastu blast radiusu a obnovenie bezpečného service outcome-u pred úplným root-cause vysvetlením. Pozri [Incident management](docs/14-sre-and-operations/incident-management.md).

## Bounded incident change

Incident action s exact subjectom, ownerom, hypothesis, scope-om, expected observation, abort criterion, rollback alebo compensation a recorded resultom. Pozri [Incident management](docs/14-sre-and-operations/incident-management.md).

## Incident recovery criteria

Explicitný súbor technical, user, business, data a forbidden-outcome podmienok, ktoré musia prejsť pred označením incidentu ako recovered. Pozri [Incident management](docs/14-sre-and-operations/incident-management.md).

## Command continuity

Zachovanie incident objective, roles, state, decisions, risks a authority počas shift, geography alebo personnel handoffu. Pozri [Incident management](docs/14-sre-and-operations/incident-management.md).

## Incident-management acceptance verdict

Dôkaz, že incident bol včas deklarovaný, koordinovaný explicitnými roles, stabilizovaný bounded actions a uzavretý až po business recovery, forbidden tests, handoffe a follow-up ownership. Pozri [Incident management](docs/14-sre-and-operations/incident-management.md).

## On-call support contract

Versionovaný contract podporovanej služby určujúci coverage hours, page eligibility, primary/secondary roles, response a escalation targets, required skills/access, dependencies, handoff a sustainability limits. Pozri [On-call a escalation](docs/14-sre-and-operations/on-call-and-escalation.md).

## Page eligibility

Verdikt, že signal je urgentný, relevantný, dostatočne spoľahlivý, actionable pre receiving role a časovo citlivý vzhľadom na user/business impact. Pozri [On-call a escalation](docs/14-sre-and-operations/on-call-and-escalation.md).

## Notification-delivery chain

Lifecycle od alert firingu cez routing, provider/device delivery a acknowledgement po qualified human ownership, action alebo escalation. Pozri [On-call a escalation](docs/14-sre-and-operations/on-call-and-escalation.md).

## Qualified response — on-call

Stav, keď pripravený responder potvrdil exact subject a impact a začal bezpečnú diagnosis, mitigation, incident declaration alebo escalation; je silnejší než samotné acknowledgement. Pozri [On-call a escalation](docs/14-sre-and-operations/on-call-and-escalation.md).

## Primary on-call

Prvá zodpovedná rotačná rola pre triage, safe first response, incident declaration a ownership do explicitného handoffu. Pozri [On-call a escalation](docs/14-sre-and-operations/on-call-and-escalation.md).

## Secondary on-call

Backup alebo parallel-response rola pre ďalšie alerts, deep diagnosis, primary replacement, IC/Ops podporu a ochranu primary pred overloadom. Pozri [On-call a escalation](docs/14-sre-and-operations/on-call-and-escalation.md).

## Shift handoff — on-call

Explicitný transfer active incidents, pages, risks, temporary overrides, recent changes, constraints, commitments a follow-up owners medzi on-call generations. Pozri [On-call a escalation](docs/14-sre-and-operations/on-call-and-escalation.md).

## Progress-based escalation

Escalation spustená absenciou qualified response alebo effective mitigation progressu, aj keď pôvodný page bol acknowledged. Pozri [On-call a escalation](docs/14-sre-and-operations/on-call-and-escalation.md).

## Schedule canary — on-call

Kontrolovaná notification overujúca current schedule, timezone, overrides, routing, primary/secondary delivery a acknowledgement/escalation behavior. Pozri [On-call a escalation](docs/14-sre-and-operations/on-call-and-escalation.md).

## Page quality

Hodnotenie pages podľa actionability, false positives, duplicates, urgency, contextu, runbook coverage, response time a contribution k user/business recovery. Pozri [On-call a escalation](docs/14-sre-and-operations/on-call-and-escalation.md).

## On-call sustainability

Dlhodobý stav, v ktorom rotation poskytuje požadované coverage bez chronickej únavy, key-person dependency, nadmerného interruption loadu alebo vytlačenia reliability engineering práce. Pozri [On-call a escalation](docs/14-sre-and-operations/on-call-and-escalation.md).

## On-call acceptance verdict

Dôkaz, že správny urgentný page dosiahne pripraveného respondera, escalation reaguje na time/skill/authority/capacity/severity a dlhodobý page load zostáva udržateľný. Pozri [On-call a escalation](docs/14-sre-and-operations/on-call-and-escalation.md).

## Runbook

Versionovaný repeatable operational postup pre rozpoznateľný exact state, explicitné preconditions, bounded actions, verification a rollback/escalation. Pozri [Runbooks a playbooks](docs/14-sre-and-operations/runbooks-and-playbooks.md).

## Playbook — operations

Širší decision framework pre triedu incidents alebo operational scenárov, ktorý podľa evidence a risku vyberá konkrétne branches, controls a runbooks. Pozri [Runbooks a playbooks](docs/14-sre-and-operations/runbooks-and-playbooks.md).

## Runbook subject

Exact service, environment, architecture generation, resource/data identity, trigger, actor, allowed scope, expected/forbidden outcomes a recovery boundary analyzovaného operational postupu. Pozri [Runbooks a playbooks](docs/14-sre-and-operations/runbooks-and-playbooks.md).

## Trigger eligibility — runbook

Testovateľné conditions určujúce, že current state patrí do supported runbook branchu a postup možno bezpečne začať. Pozri [Runbooks a playbooks](docs/14-sre-and-operations/runbooks-and-playbooks.md).

## Safety boundary — runbook

Maximálny scope, rate, concurrency, dry-run, approvals, abort criteria, evidence preservation, forbidden cohorts a recovery pravidlá konkrétneho runbooku. Pozri [Runbooks a playbooks](docs/14-sre-and-operations/runbooks-and-playbooks.md).

## Operational decision point

Explicitné mapovanie observation a state classification na allowed runbook branch, approval, action a next expected evidence. Pozri [Runbooks a playbooks](docs/14-sre-and-operations/runbooks-and-playbooks.md).

## Bounded command

Operational command viazaný na exact target manifest, maximálny scope/rate, timeout, audit, expected output a partial/unknown-outcome handling. Pozri [Runbooks a playbooks](docs/14-sre-and-operations/runbooks-and-playbooks.md).

## Affected manifest — operations

Immutable zoznam exact resource, record alebo message identities, nad ktorými sa má vykonať bounded remediation, replay, restore alebo compensation. Pozri [Runbooks a playbooks](docs/14-sre-and-operations/runbooks-and-playbooks.md).

## Unknown operational outcome

Stav, keď responder nevie, či operational side effect nastal alebo v akom scope-e, a preto musí vykonať authoritative read-back/reconciliation namiesto blind retry-u. Pozri [Runbooks a playbooks](docs/14-sre-and-operations/runbooks-and-playbooks.md).

## Runbook generation

Exact version dokumentu spolu s compatible architecture, tool, API, schema a permission assumptions. Pozri [Runbooks a playbooks](docs/14-sre-and-operations/runbooks-and-playbooks.md).

## Last-tested generation — runbook

Najnovšia environment, architecture a tool generation, proti ktorej bol runbook úspešne rehearsed vrátane wrong-subject a failure branchov. Pozri [Runbooks a playbooks](docs/14-sre-and-operations/runbooks-and-playbooks.md).

## Runbook withdrawal

Riadené vyradenie nebezpečnej alebo stale document generation pri zachovaní historical evidence, komunikácii affected responders a publikovaní replacement pathu. Pozri [Runbooks a playbooks](docs/14-sre-and-operations/runbooks-and-playbooks.md).

## Runbook acceptance verdict

Dôkaz, že current runbook správne klasifikuje subject, presadzuje safety boundary, dosahuje technical/business outcome, odmieta forbidden branches a prejde new-responder rehearsal-om. Pozri [Runbooks a playbooks](docs/14-sre-and-operations/runbooks-and-playbooks.md).
