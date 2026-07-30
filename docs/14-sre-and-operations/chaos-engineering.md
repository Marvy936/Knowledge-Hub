# Chaos engineering

Chaos engineering je disciplinované experimentovanie, ktorým sa organizácia pokúša falsifikovať konkrétnu hypotézu o spoľahlivosti business capability pod realistickou turbulentnou podmienkou. Nie je to náhodné vypínanie resources, všeobecný game day ani dôkaz odvahy spúšťať faults v production. Hodnota vzniká až z presného experiment subjectu, user-centered steady state-u, controlled faultu, safety state machine, úplnej recovery observation a mechanism-level remediation.

Experiment môže úspešne odhaliť, že hypotéza bola nepravdivá. To je valuable learning, ale reliability claim neprešiel. Naopak tool exit code `0`, obnovený Pod count alebo krátky pokles error rate-u neznamenajú, že business outcome, backlog a unknown external effects zostali v povolených hraniciach.

## 1. Dominantný risk-to-confidence lifecycle

Chaos program začína známym riskom alebo neovereným assumptionom. Z neho sa vytvorí falsifikovateľná hypothesis, current baseline a najmenší reprezentatívny experiment. Fault injection je iba stred lifecycle-u; verdict vzniká až po recovery, reconciliation a repeat experiment-e.

```text
reliability risk alebo unknown assumption
→ exact experiment subject a evidence claim
→ measurable steady state a falsifikovateľná hypothesis
→ realistic variable, control a experimental cohort
→ preconditions, blast radius a safety state machine
→ authorized effective injection
→ business, technical a human observations
→ abort alebo controlled recovery
→ backlog/state/external-effect reconciliation
→ supported, falsified, inconclusive alebo incident verdict
→ mechanism-bound remediation
→ repeat experiment a bounded confidence update
```

Evidence scope je súčasťou claimu. Experiment nad local Pod failure-om môže potvrdiť replica replacement, ale nesmie byť prezentovaný ako dôkaz regional DR, provider continuity alebo business-consistent recovery.

## 2. Test, chaos experiment, game day a incident

Test overuje explicitný contract s definovaným oracle-om a môže byť deterministic mimo production. Chaos experiment skúša falsifikovať hypothesis o komplexnom system behavior-e pod turbulentnou condition. Game day je širšie coordinated exercise ľudí, systems a procedures; môže obsahovať chaos experiment, DR rehearsal alebo tabletop. Incident je neplánovaný alebo nekontrolovaný impact.

Rozlíšenie mení authority a safety behavior. Experiment bez hypothesis je fault injection bez learning contractu. Experiment bez business steady state-u môže byť component drill, nie service reliability evidence. Keď impact prekročí approved boundary alebo recovery nie je controlled, chaos authority končí a incident command preberá vedenie.

## 3. Exact experiment subject a immutable claim

Subject zachováva capability a journey, environment/Region, architecture/release/config generations, control a experimental cohorts, exact fault target a dependency boundary, steady-state population, SLO/error-budget context, window, owner/approver/responders, maximum blast radius, abort/recovery mechanisms, expected evidence a forbidden outcomes.

```text
experiment: CH-PAY-55-2
capability: provider-confirmed settlement completion
release: payments 7.26.1
control: prod-eu1 synthetic cohort
experimental: prod-euw1 internal merchants, max 1 %
variable: provider egress unavailable 8 min
hypothesis: durable intents remain reconstructable;
            completion recovers within 12 min;
            no duplicate or lost settlement
steady state:
  completion good ratio >= 99.9 %
  queue age <= 10 min
  retry amplification <= 1.4x
blast radius: max 2 000 operations
```

Experiment definition má byť immutable alebo reprodukovateľná. Zmena cohortu, release-u, intensity, duration, oracle-u alebo abort threshold-u vytvára novú generation. Inak môže report tvrdiť, že prešiel experiment, ktorý sa počas executionu zmenil na ľahší.

## 4. Reliability question, hypothesis a steady state

Silná hypothesis má tvar: za podmienok X, pre subject Y, keď nastane variable Z, systém zachová invariant A alebo sa obnoví do boundary B bez forbidden outcome-u C. `Systém by mal prežiť` alebo `Kubernetes prescheduluje Pody` neposkytuje business claim ani recovery bound.

Pre provider timeout experiment je silná hypothesis:

```text
ak provider timeoutuje 8 minút,
unique acknowledged settlement intents zostanú durable,
provider attempts neprekročia shared retry budget 1.4x,
DB acquire p99 zostane pod 250 ms,
a 99 % affected operations sa po obnove uzavrie do 12 minút
bez duplicate settlementu.
```

Steady state opisuje measurable behavior pred, počas a po fault-e. Zahŕňa completion/correctness, latency, queue age/drain, durability/reconstructability, degraded user outcome, security invariant, saturation, recovery time a reconciliation. Component metrics vysvetľujú mechanismus, ale Pod count, CPU alebo `/healthz` samostatne nevytvárajú service oracle. Control cohort pomáha odlíšiť fault effect od bežného trafficu, release driftu alebo provider variability.

## 5. Realistická variable a experiment fidelity

Variable má reprezentovať modeled real-world condition: process/node loss, CPU alebo memory pressure, latency/packet loss/DNS failure, replica lag alebo leader loss, provider timeout/429, KMS denial, quota exhaustion, telemetry loss, traffic spike, certificate rotation, deployment alebo backlog replay.

Priorita nevychádza iba z frequency. Rare event s catastrophic impactom a slabou recovery evidence môže byť dôležitejší než častý bounded failure. Experiment musí zasiahnuť správnu boundary. Jeden Pod kill je vhodný pre local scheduling hypothesis, ale nie pre regional control-plane loss. Synthetic request bez external side effectu môže overiť edge path, ale nie exactly-once provider operation.

Fidelity rastie postupne: model/simulation, nonproduction experiment, shadow alebo synthetic production cohort, bounded internal cohort a širší production scope. Nižšia fidelity je užitočná na bezpečné odhalenie základných defects; vyššia sa používa až vtedy, keď otázku nemožno spoľahlivo zodpovedať inde.

## 6. Preconditions a experiment eligibility

Pred executionom sa overí current owner a on-call coverage, neprítomnosť relevantného incidentu, exact release/environment, stable baseline, telemetry coverage, injection identity a permissions, affected manifest, blast-radius enforcement, abort automation, recovery path, communication channel, error-budget eligibility a data/security/regulatory constraints.

Precondition nie je formalita. Experiment nesmie prvýkrát zistiť, že team nemá decrypt access, recovery command, provider contact alebo business oracle. Ak monitoring nevie rozlíšiť control a experimental cohort alebo recovery path nebol rehearse-nutý, experiment sa zastaví pred injection.

Eligibility môže byť denied aj pri zdravom service state-e, ak error budget je at risk, prebieha critical launch alebo dependency owner nedal potrebný súhlas. Chaos program nemá prednosť pred customer a safety commitments.

## 7. Blast radius a privileged injection

Blast radius má user/tenant, operation, Region/AZ/resource, dependency, data, duration, traffic, financial/legal a recovery-complexity dimensions. Minimal blast radius znamená najmenší scope, ktorý stále testuje daný mechanismus; nereprezentatívny fault vytvára false confidence.

Injection je privileged change. Potrebuje exact target manifest, least-privilege short-lived identity, environment restrictions, max scope/duration, dry-run/read-back, immutable definition, dual control pre high-risk faults, audit, automatic expiry, cleanup a kill switch. Credential schopné meniť ľubovoľnú production network policy je samostatný security defect, aj keby samotný experiment bol dobre navrhnutý.

Scope expansion počas experimentu vyžaduje novú approval a generation. Operator nesmie neformálne zvýšiť percento trafficu, pretože „zatiaľ je všetko zelené“.

## 8. Safety state machine a abort semantics

Experiment používa explicitné states:

```text
Draft → Reviewed → Armed → BaselineVerified
→ Injecting → Observing → Recovering → Reconciling
→ Accepted | Falsified | Inconclusive | Aborted | Incident
→ Closed
```

Každý transition má ownera, preconditions, expected evidence, timestamp a abort path. Injection bez baseline, širší scope bez approval, druhý fault pri unknown state-e alebo `Passed` pred reconciliation sú forbidden transitions.

Abort criteria sú measurable: completion fast burn, population nad 2 000 operations, duplicate settlement nad nulu, sent-unknown cohort nad 20, queue age nad 12 minút, DB acquire p99 nad 500 ms, telemetry coverage pod threshold alebo adjacent cohort impact. Abort neznamená iba stopnúť injector. Aktivuje cleanup/recovery a pri pretrvávajúcom impacte incident declaration. Kill switch bez overenej recovery path je neúplný safety control.

## 9. Observation a attribution

Počas experimentu sa sledujú tri vrstvy. Injection evidence potvrdzuje intended target, effective intensity/duration, partial injector failures a cleanup. System behavior porovnáva control/experimental cohorts, business SLI, retries, queues, saturation, failover a telemetry coverage. Human behavior sleduje page delivery, qualified response, runbook eligibility, declaration/escalation, decision latency a manual touch points.

Tieto outcomes sa hodnotia oddelene. Technický mechanismus môže prejsť, ale on-call escalation zlyhať. Alebo injection tool môže skončiť successom, no fault sa na intended network path nikdy neprejavil; výsledok je inconclusive, nie supported.

Concurrent deployment, traffic spike alebo provider event môže attribution narušiť. Experiment state preto zachováva change calendar a independent observations. Keď causal attribution nemožno urobiť, report nesmie vybrať želaný verdict.

## 10. Recovery a reconciliation ako súčasť experimentu

Experiment nekončí odstránením faultu. Sleduje reconnection, backlog a retry stabilization, state convergence, business outcome closure, removal temporary overrides, adjacent cohort a second operation. Dôležité sú recovery latency, overshoot/oscillation, retry storm, stale connections/cache, drain rate a unknown/duplicate outcomes.

```text
fault removed
→ dependency reconnect
→ retries/concurrency stabilize
→ backlog drains
→ data a external effects converge
→ affected operations close
→ temporary controls retire
→ adjacent a second operation succeed
```

Ak metric krátko dosiahne baseline, ale queue rastie alebo sent-unknown cohort nie je reconciled, experiment zostáva v `Recovering` alebo `Reconciling`. Predčasný closure by zamenil symptom recovery za business recovery.

## 11. Verdict a evidence scope

`Hypothesis supported` vyžaduje complete evidence, steady state a recovery within boundaries a neprítomnosť forbidden outcomes. `Falsified` znamená, že behavior alebo recovery porušili hypothesis; experiment priniesol learning, ale reliability claim zlyhal. `Inconclusive` znamená neúčinný fault, nedostatočnú telemetry, nereprezentatívny cohort alebo confounding event. `Aborted safely` potvrdzuje safety response, nie automaticky pôvodnú hypothesis. Pri prekročení controlled boundary vzniká experiment-induced incident.

Verdict musí uviesť presný scope. `Local worker replacement supported` sa nesmie publikovať ako `regional resilience proven`. Confidence je bounded claim viazaný na current generation, variable, cohort a observation window.

## 12. False confidence pred `SRE-PAY-55`

Experiment `CH-PAY-41 — Region resilience` zabil 50 % settlement worker Pods v `prod-eu1`, čakal na replacement replicas, sledoval HTTP `202` error rate a skončil pri obnovenom Pod count-e. Korektne dokázal local worker replacement.

Neobsahoval Region/control-plane loss, standby KMS identity, provider egress/callback, broker checkpoint/fencing, DNS cutover, standby capacity, final completion SLI, reconciliation ani actual RTO. Organizational report napriek tomu použil `Passed` ako regional DR evidence.

Root cause chaos failure-u bol experiment-subject mismatch: narrow Pod drill bol bez causal contractu použitý na širší business-recovery claim. Readiness review následne prijala nesúvisiace evidence ako dôkaz current DR capability.

## 13. Post-remediation experiment `CH-PAY-55-2`

Nový bounded experiment použil control cohort v `prod-eu1`, internal experimental cohort v `prod-euw1`, deny primary provider egress, primary writer epoch freeze a recovery provider/DNS path. Scope bol max 2 000 operations a jedno percento internal merchants. Steady state vyžadoval durable acceptance, provider-confirmed completion, nulové duplicate/lost outcomes, queue age do desať minút a recovery do 45 minút.

Preconditions zahŕňali current `DR-PAY-55-v4`, decrypt canary, provider allowlist/callback, broker checkpoint, active on-call/IC/provider contacts a fencing read-back. Prvý run falsifikoval hypothesis: DNS cutover bol effective za 94 sekúnd, no existing keep-alive sessions držali primary route dlhšie než modelovaných 30 sekúnd. Bounded abort zabránil customer impactu.

Po connection-drain, TTL/keep-alive contracte, active-path read-backu a reconnect guardraile repeat prešiel: business recovery `31 min 42 s`, recovered-point gap 48 sekúnd, nula duplicate/lost intents, nula sent-unknown po reconciliation a druhý cycle successful.

## 14. Remediation a chaos acceptance contract

Finding pokračuje od exact mechanismu cez severity/owner, containment, engineering control, deployment/effective read-back a repeat experiment. `Upraviť runbook` nestačí, ak executable path zostáva rovnaký. Repeat má použiť rovnaký mechanismus a adjacent cohort alebo second cycle, aby odhalil presun failure-u.

Positive path preukáže effective fault, stable business steady state a complete recovery. Falsification path musí bezpečne zastaviť ramp, zachovať evidence a vytvoriť owned remediation. Abort path musí prejsť do recovery/incident authority. Forbidden paths zahŕňajú injection bez baseline, broad identity, scope expansion, incomplete telemetry, claim širší než subject a closure pred reconciliation.

```text
positive:
current baseline → effective fault → bounded behavior → full recovery

falsified:
assumption broken → safe abort → mechanism action → repeat

forbidden:
random fault bez hypothesis
Pod health ako business oracle
stop injection bez recovery
inconclusive označené passed
old experiment evidence pre new generation
```

## 15. Troubleshooting chaos experimentu

Pri slabom alebo nebezpečnom výsledku sleduj experiment generation, question/hypothesis, cohorts, baseline/coverage, target a effective fault, blast radius, abort behavior, concurrent events, business steady state, recovery/reconciliation, verdict scope a remediation repeat.

```text
experiment nevytvoril dôveru
→ subject a evidence claim
→ hypothesis/oracle
→ cohort a baseline
→ injection effectiveness
→ safety/abort
→ business a technical behavior
→ recovery/reconciliation
→ verdict scope
→ action a repeat
```

Tool output je iba injection evidence. Reliability conclusion vzniká až integráciou všetkých boundaries.

## 16. Anti-patterny

Chaos anti-patterny maximalizujú spectacle alebo activity namiesto falsifikovateľného learningu.

- **Chaos monkey ako stratégia —** random fault bez hypothesis, ownera a recovery contractu nevytvára actionable evidence.
- **App nepadla, experiment prešiel —** correctness, backlog, user outcome alebo recovery mohli zlyhať.
- **Pod kill dokazuje regional DR —** evidence claim je širší než experiment subject.
- **Production za každú cenu —** fidelity nesmie prekročiť maturity, blast-radius a regulatory boundaries.
- **Abort znamená stop injection —** recovery a incident response môžu stále pokračovať.
- **Experiment končí pri obnovenej metric —** retries, queue a unknown outcomes nemusia byť uzavreté.
- **Finding bez repeat experimentu —** implementovaný control nemusí byť effective alebo môže presunúť failure.
- **Tool exit code je verdict —** orchestration success nie je business reliability evidence.

## 17. Kontrolné otázky

1. Ako sa chaos experiment líši od testu, game day a incidentu?
2. Čo tvorí exact experiment subject a claim?
3. Ako sa píše falsifikovateľná hypothesis?
4. Prečo steady state potrebuje business outcome a control cohort?
5. Ako sa vyberá realistická variable a fidelity?
6. Čo musí prejsť pred experiment eligibility?
7. Ako blast radius a injection identity obmedzujú risk?
8. Čo riadi safety state machine a abort?
9. Prečo recovery a reconciliation patria do experimentu?
10. Prečo `CH-PAY-41` nevytvoril regional DR evidence?
11. Ako supported, falsified, inconclusive a incident verdicts odlíšiš?
12. Ktoré positive, falsified a forbidden paths patria do acceptance?

## Glossary impact

Relevantné pojmy: chaos experiment subject, evidence claim, steady-state hypothesis, realistic variable, control/experimental cohort, experiment fidelity, blast-radius contract, injection identity, safety state machine, chaos abort, effective fault, hypothesis verdict, experiment-induced incident, repeat experiment a chaos acceptance contract.

## Primárne zdroje

- [Principles of Chaos Engineering](https://principlesofchaos.org/)
- [Google SRE — Testing for Reliability](https://sre.google/sre-book/testing-reliability/)
- [Google SRE — Emergency Response](https://sre.google/sre-book/emergency-response/)
- [Google SRE — Data Integrity](https://sre.google/sre-book/data-integrity/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Disaster recovery](disaster-recovery.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Operational readiness →](operational-readiness.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
