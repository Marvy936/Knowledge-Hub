# RPO a RTO

Recovery Point Objective — RPO — vyjadruje, ku ktorému business-valid pointu musí byť state po disruption obnovený, teda koľko acknowledged change-u možno stratiť alebo musí byť rekonštruované. Recovery Time Objective — RTO — vyjadruje, dokedy musí byť capability bezpečne obnovená, kým disruption prekročí prijateľný business alebo mission impact. Nie sú to vlastnosti backup produktu ani čísla, ktoré si infra tím vyberie podľa aktuálnej technológie.

RPO a RTO patria presnej capability, cohortu, consistency groupu a failure scenáru. Musia vychádzať z business impact analysis, premietnuť sa do architecture, staffing, dependencies a degraded mode-u a následne byť overené timed exercise-om na current generation.

## 1. Dominantný impact-to-measured-recovery lifecycle

Recovery objectives prekladajú business toleranciu na technický a operational contract. Target zostáva iba želaním, kým full recovery test nezmeria actual point, actual time, reconstructed/lost state a forbidden outcomes.

```text
business capability a impact tolerance
→ exact recovery-objective subject
→ data/dependency/acknowledgement inventory
→ failure a corruption scenarios
→ RPO, RTO a maximum-tolerance boundaries
→ recovery strategy a dependency budgets
→ backup/failover/restore/reconciliation design
→ timed exercise na current generation
→ actual recovered point a actual recovery time
→ objective gap a corrective action
→ alternate-scenario a second-responder validation
```

RPO rieši data-history os; RTO time-to-capability os. Nízke RPO neznamená automaticky nízke RTO a rýchly failover nemusí zachovať business-consistent state.

## 2. Exact recovery-objective subject

`RPO päť minút, RTO 45 minút` je bez scope-u neauditovateľné. Exact subject obsahuje capability a operation, cohort, data stores a consistency group, failure scenario, measurement start/end, clock authority, recovery/degraded mode, dependency objectives, ownera a review generation.

```text
capability: merchant settlement reconciliation
scope: production EU merchant settlements
consistency group: CG-PAY-04
scenario: logical corruption primary settlement ledgeru
RPO: ≤ 5 min business-consistent replay/reconciliation window
RTO: ≤ 45 min safe merchant-facing completion
maximum tolerable disruption: 2 h
start: first invalid committed mutation
end: new + affected historical operations safely processable
owner: Payments Resilience
```

Reporting, audit retrieval a settlement completion môžu mať odlišné objectives. Rovnaké číslo pre celú aplikáciu skryje rozdielnu criticality a data semantics.

## 3. RPO: time, events a acknowledgement semantics

RPO sa meria medzi disruption/corruption boundary a selected valid recovery pointom. Pri corruption o `02:14:07` a RPO päť minút musí byť dostupný business-valid point `02:09:07` alebo novší, prípadne musí existovať reprodukovateľná reconstruction všetkých acknowledged changes po staršom point-e.

Time-based objective treba doplniť event alebo invariant semantics. Päť minút počas low trafficu a campaign peaku predstavuje iný počet operations. Financial capability môže vyžadovať:

```text
RPO-time: ≤ 5 min initial business-consistent window
RPO-event: 0 permanently lost acknowledged settlements
```

`RPO=0` znamená, že žiadny acknowledged required state nesmie byť nenávratne stratený v definovanom scenári. Nevyplýva iba zo synchronous replication. Potrebuje end-to-end acknowledgement, durable authority, external side-effect identity, idempotency a reconstructability. Sent-unknown provider outcome sa rieši ledger reconciliation, nie tvrdením, že local DB replica všetko obsahuje.

Backup interval nie je RPO. Job môže meškať, capture trvať, log chain mať gap, latest point byť corrupted, consistency group rozídený alebo artifact unreadable. RPO dokazuje až selected clean point a business reconciliation.

## 4. RTO: business boundary a work recovery

RTO zahŕňa celý interval od dohodnutého business disruption startu po safe capability:

```text
first business disruption
→ detection a declaration
→ containment/fencing
→ target provisioning a access
→ data restore alebo failover
→ dependency/application startup
→ validation
→ reconciliation a work recovery
→ safe business service
```

Ak sa stopky spustia až kliknutím `Start restore`, organizácia vynechá detection a decision delay. Ak sa zastavia pri `database available`, vynechá application, dependencies, validation, backlog a user outcome.

Po technical restore môže nasledovať Work Recovery Time: backlog drain, reconciliation, manual cases, communication, cache/index rebuild, override removal a audit closure. Názvoslovie sa líši, preto objective musí explicitne definovať, či RTO končí safe new operations alebo až historical reconciliation. Maximum tolerable disruption je hranica neprijateľného impactu; RTO musí byť kratší a ponechať rezervu na uncertainty a work recovery.

## 5. Business impact, scenarios a degraded modes

Business impact analysis určuje critical capabilities, dependency chain, impact curve, data-loss tolerance, legal/financial/customer commitments, manual alternatives, restoration priority a seasonal constraints.

| Disruption | Settlement impact |
|---|---|
| 0–15 min | queueing bez customer breachu |
| 15–45 min | merchant delay a error-budget burn |
| 45–120 min | contractual/support escalation a liquidity risk |
| >120 min | neprijateľný business disruption |

Objectives sú scenario-specific. Instance alebo AZ loss, Region loss, logical corruption, ransomware/account compromise, provider outage, operator deletion, schema incompatibility a identity outage majú iné clean-point, isolation a lead-time constraints. Multi-AZ failover contract nemožno použiť ako ransomware recovery dôkaz.

RTO môže obsahovať staged degraded modes:

```text
≤ 15 min: durable settlement admission
≤ 45 min: safe automatic completion
≤ 120 min: historical reconciliation a reporting
```

Každý mode definuje allowed/denied operations, data guarantees, capacity, duration, communication, exit criteria a forbidden side effects. Manual spreadsheet bez identity, audit a idempotency nie je automaticky bezpečný degraded mode.

## 6. Architecture a dependency budgets

End-to-end objective sa rozkladá na boundaries, aby bolo viditeľné, kde je technický alebo organizačný lead time dlhší než celý target.

```text
RTO 45 min
├── detect/declare: 5 min
├── contain/fence: 5 min
├── target/access: 8 min
├── data restore: 12 min
├── app/dependencies: 5 min
├── validation: 5 min
└── initial reconcile/cutover: 5 min
```

Súčet nie je garancia; niektoré kroky bežia paralelne a uncertainty potrebuje rezervu. Parent capability s RTO 15 min nemôže závisieť od key alebo identity recovery trvajúcej štyri hodiny.

Strategy sa mapuje podľa scenario: continuous logs a durable events pre nízke RPO, warm/preprovisioned target pre nízke RTO, retained PITR a clean-point analysis pre logical corruption, isolated cross-domain copy pre account loss a provider idempotency ledger pre external effects.

## 7. Target verzus actual measurement

Objective a nameraný výsledok majú samostatné fields:

- **RPO target —** požadovaný recovery point;
- **actual recovered point —** point skutočne zvolený a obnovený;
- **loss/reconstruction result —** permanently lost alebo dodatočne reconstructed state;
- **RTO target —** požadovaný business recovery interval;
- **actual recovery time —** čas od start boundary po end boundary;
- **technical a work-recovery submetrics —** vysvetľujú gap bez skracovania end-to-end measure.

Service catalog má ukazovať target aj posledný measured actual, scenario a test generation. Target bez actual exercise je plán, nie recoverability evidence.

## 8. Connected incident `SRE-PAY-54`

Catalog uvádzal RPO `5 min`, RTO `45 min` a maximum disruption `2 h`, no posledný full drill bol 14 mesiacov starý, na schema v15 a pred account/key migration.

Corruption vznikla `02:14:07`. DB-only clean point `02:13:58` bol iba deväť sekúnd starý, takže datastore-level RPO vyzeralo splnené. Posledný pre-built coordinated DB/provider checkpoint však bol `02:03:00`, teda `11 min 7 s` pred mutation. Business-consistent RPO päť minút preto nebolo okamžite splnené.

Tím obnovil DB point `02:13:58` a neskôr použil provider idempotency ledger na reconciliation. Final permanent loss acknowledged settlements bol nula, ale to neznamená, že initial RPO bolo splnené; dodatočná reconstruction zachránila data po prekročení intended recovery window.

Namerané časy boli:

```text
first bad mutation:        02:14:07
incident declaration:      02:41:00
isolated DB queryable:      04:31:00
business recovery:          06:03:00

actual business recovery:  3 h 48 min 53 s
RTO target:                 45 min
maximum disruption:         2 h
```

RTO aj maximum tolerable disruption boli prekročené. Dashboard pritom začínal timer až restore jobom, restore access/key path bol stale, target nebol preprovisioned, provider reconciliation nebola v model-e a drill nepokrýval schema v17 ani logical corruption.

## 9. Corrective objective generation `REC-PAY-55`

Nový contract oddelil permanent loss, initial reconstructability a staged service recovery:

```text
RPO-1: 0 permanently lost acknowledged settlement intents
RPO-2: ≤ 5 min initial business-consistent replay/reconciliation window
RTO-1: ≤ 15 min durable-intent degraded admission
RTO-2: ≤ 45 min safe new settlement completion
RTO-3: ≤ 120 min historical affected-cohort reconciliation
```

Podporuje ho päťminútový provider checkpoint, continuous idempotency-ledger query, preprovisioned isolated control plane, key/access canary, schema compatibility automation, bounded affected-manifest extraction, quarterly logical-corruption drill a dashboard target-versus-actual.

## 10. Timed exercise a acceptance contract

Exercise začína known baseline-om, injectuje fault/corruption a meria detection, declaration, candidate selection, access/provisioning, restore/failover, validation, reconciliation/cutover, business canary a cleanup. Report zachová generation, scenario, timestamps, recovered point, permanent loss/reconstruction, actual time, manual steps, blockers, assumptions a residual risk.

Positive path preukáže target point/time. Logical-corruption path odmietne latest bad point. Alternate account/Region path overí key, network a identity. Degraded path overí allowed a forbidden operations. Second-responder test preukáže, že objective nezávisí od jedného človeka.

```text
positive:
current scenario → point/time within targets

corruption:
latest bad point denied → clean candidate + reconstruction

degraded:
bounded capability → explicit guarantees → exit criteria

forbidden:
stop timer at DB ready
backup interval reported as RPO
permanent loss zero used to hide late reconstruction
objective changed without BIA
```

## 11. Troubleshooting objective miss-u

Pri miss-e najprv zachovaj exact objective generation, scenario a measurement boundaries. Potom sleduj protected subject, selected point, log/capture chain, reconstructability, detection delay, access/key/provisioning lead time, restore throughput, dependency startup, validation a work recovery.

```text
objective miss
→ target/scenario/start/end
→ consistency group a authority
→ selected clean point
→ capture/log/reconstructability
→ detection/decision delay
→ access/target/restore capacity
→ application/dependencies
→ validation/reconciliation
→ objective-vs-actual gap
→ redesign alebo explicit risk decision
```

Objective sa nesmie znížiť iba kvôli zelenému dashboardu. Zmena potrebuje novú BIA, business ownera a residual-risk decision.

## 12. Anti-patterny

Recovery-objective anti-patterny zamieňajú technical submetric alebo desired target za business recovery proof.

- **RPO je backup schedule —** ignoruje delay, clean point, consistency group, readability a external state.
- **RTO je database available —** ignoruje application, dependencies, validation, reconciliation a user outcome.
- **Jedno číslo pre celú firmu —** criticality, cohorts a data semantics sa líšia.
- **RPO/RTO bez scenario —** failover target sa nesprávne použije na corruption alebo ransomware.
- **Zero RPO/RTO ako marketing —** chýba acknowledgement, measurement a failure-model evidence.
- **Objective bez actual metric —** catalog ukazuje želanie, nie recoverability.
- **Timer od declaration alebo restore jobu —** vynechá detection a user impact.
- **Permanent loss nula znamená RPO splnené —** late reconstruction môže zachrániť data po prekročení window-u.
- **Po incidente znížime target —** bez BIA ide o metric gaming.

## 13. Kontrolné otázky

1. Ako sa RPO a RTO líšia?
2. Čo tvorí exact recovery-objective subject?
3. Prečo objectives vychádzajú z BIA?
4. Ako maximum tolerable disruption a work recovery súvisia s RTO?
5. Prečo RPO nie je backup interval?
6. Prečo RTO nekončí pri `database available`?
7. Ako time a event RPO dopĺňajú jeden druhý?
8. Čo znamená zero RPO pri external operation?
9. Ako dependency budgets odhalia nesplniteľný target?
10. Prečo `SRE-PAY-54` splnilo DB point, ale nie business-consistent RPO?
11. Ako sa objective a actual result oddeľujú?
12. Ktoré positive, corruption, degraded a forbidden paths patria do acceptance?

## Glossary impact

Relevantné pojmy: recovery-objective subject, RPO, RTO, business-consistent RPO, actual recovered point, actual recovery time, maximum tolerable disruption, work recovery, event-based RPO, dependency budget, degraded recovery objective a RPO/RTO acceptance contract.

## Primárne zdroje

- [NIST CSRC — Recovery Point Objective](https://csrc.nist.gov/glossary/term/recovery_point_objective)
- [NIST CSRC — Recovery Time Objective](https://csrc.nist.gov/glossary/term/Recovery_Time_Objective)
- [NIST SP 800-34 Rev. 1](https://csrc.nist.gov/pubs/sp/800/34/r1/upd1/final)
- [Google SRE — Emergency Response](https://sre.google/sre-book/emergency-response/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Backup a restore](backup-and-restore.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Disaster recovery →](disaster-recovery.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
