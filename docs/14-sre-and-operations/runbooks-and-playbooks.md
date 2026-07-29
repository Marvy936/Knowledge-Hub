# Runbooks a playbooks

Runbook je versionovaný operatívny postup pre rozpoznateľný stav a bounded action. Playbook je širší decision framework pre triedu incidentov alebo operational scenárov, v ktorých sa konkrétna cesta vyberá podľa evidence, risku a scope-u.

Ani jeden dokument nie je zoznam príkazov bez kontextu. Musí prenášať safety, identity, decision a verification contract medzi authorom a responderom.

## 1. Runbook a playbook

### Runbook

Vhodný pre repeatable a dobre ohraničený workflow:

```text
konkrétny trigger
→ presná klasifikácia
→ preconditions
→ bounded kroky
→ očakávaný outcome
→ verify/rollback/escalate
```

Príklady:

- reštart jednej unhealthy replica po overení, že controller ju bezpečne nahradí;
- bounded replay exact message IDs;
- failover na pretested standby generation;
- rotácia credentialu cez coordinated lifecycle;
- odobratie node-u z trafficu.

### Playbook

Vhodný pre širší scenario space:

```text
incident alebo risk class
→ scope a severity
→ competing branches
→ rozhodovacie kritériá
→ zvolené runbooks/controls
→ communication a recovery strategy
```

Príklady:

- database saturation;
- provider outage;
- regional degradation;
- credential compromise;
- suspected data loss;
- traffic overload.

Playbook môže odkazovať na viac runbooks. Runbook nesmie predstierať, že každá situácia má identický mechanický krok.

## 2. Dominantný lifecycle

```text
operational intent a exact subject
→ trigger a eligibility
→ document/version/tool generation
→ prerequisites, access a safety boundary
→ observation a state classification
→ decision gate
→ bounded action
→ expected a forbidden outcomes
→ technical a business verification
→ rollback, compensation alebo escalation
→ evidence a follow-up ownership
→ rehearsal, freshness review a retirement
```

Runbook je prijatý až keď správny responder dokáže na current architecture bezpečne dosiahnuť intended outcome a odmietnuť nesprávny subject, stale generation alebo unsafe precondition.

## 3. Exact runbook subject

Runbook subject musí obsahovať:

```text
service a business capability
+ operation/failure state
+ environment/Region/cohort
+ architecture/release/config generation
+ resource alebo data identity
+ permissions a actor
+ trigger/observation window
+ allowed action scope
+ expected a forbidden outcomes
+ rollback/escalation boundary
```

Názov `Fix stuck settlements` je nepresný. Lepšie:

```text
runbook: RB-PAY-24
subject: unpublished settlement outbox commands
Region: prod-eu1
architecture: lease generation v3
eligibility: publisher healthy, command never sent, age > 10 min
allowed action: dry-run classification a bounded replay max 500 IDs
forbidden: delete, broad lease reset, replay sent-unknown cohort
```

## 4. Povinná štruktúra runbooku

### Purpose

Aký user/business outcome obnovuje a čo zámerne nerieši.

### Trigger a eligibility

Ktorý page, symptom alebo operator request ho aktivuje a ktoré observations musia byť pravdivé.

### Preconditions

- current environment a resource identity;
- required access;
- maintenance alebo incident state;
- backup/recovery availability;
- dependency health;
- peer/IC approval pre riskantné kroky;
- known incompatible generations.

### Safety boundary

- maximálny scope;
- rate/concurrency limit;
- dry-run;
- idempotency;
- abort criteria;
- forbidden commands alebo cohorts;
- evidence preservation;
- rollback/compensation.

### Diagnostic observations

Príkazy a queries s vysvetlením:

```text
čo pozorujú
→ na ktorom boundary
→ aký expected result
→ ako zmeniť decision podľa výsledku
```

### Actions

Každý krok potrebuje exact target, expected effect a validation.

### Verification

Technický aj business outcome vrátane forbidden a second-operation testu.

### Escalation

Kedy postup zastaviť, komu a s akým evidence bundle-om eskalovať.

### Metadata

Owner, reviewers, last tested date, compatible versions, dependencies a retirement trigger.

## 5. Decision points

Runbook nemá zakrývať nebezpečné judgment calls vetou „podľa potreby“.

Decision point:

```text
observation
→ classification
→ allowed branch
→ risk/approval
→ next expected evidence
```

Príklad:

```text
command provider_attempt_id is null
AND broker publish audit absent
→ never-sent
→ bounded replay allowed

provider_attempt_id exists
OR acknowledgement outcome unknown
→ sent-unknown
→ automatic replay forbidden
→ provider-ledger reconciliation a human approval
```

Ak branch nemožno bezpečne automatizovať, runbook musí explicitne eskalovať.

## 6. Commands ako controlled operations

Príkaz musí byť:

- copy-safe, nie iba syntakticky validný;
- parameterizovaný exact identity;
- read-before-write;
- scoped a bounded;
- auditovateľný;
- idempotentný alebo chránený idempotency keyom;
- vybavený timeoutom;
- sprevádzaný expected outputom;
- s explicitnou reakciou na partial alebo unknown outcome.

Nebezpečný príklad:

```sql
DELETE FROM settlement_outbox
WHERE created_at < now() - interval '15 minutes';
```

Chýba state, publish evidence, terminal status, tenant, count limit, dry-run, transaction plan, backup a recovery contract.

Bezpečnejší pattern:

```text
select exact candidate IDs
→ classify by authoritative state/evidence
→ produce immutable manifest
→ review count a risk
→ execute bounded idempotent operation
→ read back per-ID outcome
→ reconcile downstream state
```

## 7. Verification

Každý runbook musí overiť viac než exit code `0`.

### Source/config verification

Správna version a parameters boli použité.

### Effective-state verification

Runtime alebo authoritative system skutočne prijal zmenu.

### Service verification

Latency, errors, queue a dependencies sa správajú podľa hypothesis.

### Business verification

Pôvodný user outcome funguje.

### Forbidden-outcome verification

Nevznikli duplicate effects, data loss, cross-tenant impact alebo broader access.

### Second-operation verification

Ďalšia nezávislá operation prejde bez manual correction.

## 8. Rollback, compensation a unknown outcome

Nie každá operácia sa dá rollbacknúť.

- reversible config change môže mať rollback;
- external provider call môže vyžadovať reconciliation a compensation;
- delete môže vyžadovať restore;
- failover môže vyžadovať fencing, nie jednoduchý failback;
- partial replay môže vyžadovať per-ID outcome classification.

Runbook musí odlišovať:

```text
operation failed before side effect
operation succeeded
operation partially succeeded
operation outcome unknown
```

Retry po unknown outcome bez idempotency môže vytvoriť duplicate business effect.

## 9. Automation boundary

Dobrý runbook je kandidát na automation, ale automatizuje sa decision contract, nie iba shell commands.

Automation potrebuje:

- typed inputs a schema;
- subject identity validation;
- current-state read;
- plan/dry-run;
- policy/approval;
- bounded apply;
- idempotency;
- per-step evidence;
- compensation;
- final business validation;
- emergency stop;
- owner a lifecycle.

Automatizovaný broad cleanup je nebezpečnejší než manuálny broad cleanup, pretože zväčšuje speed a scope failure-u.

## 10. Freshness a compatibility

Runbook driftuje spolu so systémom.

Review triggers:

- architecture alebo topology change;
- schema/state-machine change;
- nový release alebo API;
- identity/permission model change;
- incident alebo near miss;
- tool deprecation;
- owner/team change;
- runbook nepoužitý alebo netestovaný definovaný interval;
- zmena provider contractu;
- zmena recovery mechanismu.

Metadata `last updated` nestačí. Potrebný je `last tested against generation`.

## 11. Rehearsal

Runbook testuj cez:

- sandbox/lab;
- read-only production validation;
- game day;
- shadow execution;
- fault injection;
- table-top walkthrough;
- new-responder exercise;
- scheduled canary.

Test musí obsahovať aj nesprávny subject alebo nesplnenú precondition a potvrdiť, že postup odmietne unsafe branch.

## 12. Worked incident `SRE-PAY-53`

Primary responder otvoril runbook `RB-PAY-17 — Clear stuck settlement leases`. Dokument vznikol pre starú architecture generation, v ktorej lease nemal heartbeat extension a jeden command spracúval iba jeden consumer.

Runbook obsahoval:

```text
1. scale workers to 240
2. reset leases older than 15 min
3. restart publisher
4. monitor queue length
```

Chýbalo:

- compatible architecture generation;
- distinction `never-sent`, `in-flight`, `sent-unknown` a `completed`;
- dry-run candidate count;
- max scope a rate;
- DB/provider saturation guardrail;
- incident declaration trigger;
- expected queue drain rate;
- duplicate/unknown-outcome verification;
- rollback alebo reconciliation path.

V current lease v3 architecture heartbeat timestamp mohol byť starší než 15 minút počas provider slowdown-u, hoci command bol stále in-flight. Reset preto sprístupnil `62 418` commands druhému consumer cohortu.

Dôsledky:

- broker redeliveries prudko vzrástli;
- provider attempts a DB writes sa ďalej zosilnili;
- `143` operations prešli do `sent-unknown` classification;
- idempotency keys zabránili potvrdenému duplicate settlementu, ale cohort vyžadoval provider-ledger reconciliation;
- queue length krátko klesla, čo vytvorilo false-green dojem, kým completion latency ďalej rástla.

Runbook failure bol **stale procedural document bez generation, state-classification a safety contractu, ktorý aplikoval broad lease reset na semanticky odlišnú current architecture**.

## 13. Evidence-preserving containment

IC zastavil ďalšie použitie `RB-PAY-17` a vykonal:

1. preservation executed SQL, actor, timestamp a affected IDs;
2. označenie runbooku ako withdrawn;
3. zastavenie new lease resets a unbounded replays;
4. classification affected IDs podľa broker/provider evidence;
5. bounded concurrency a admission reduction;
6. provider-ledger reconciliation pre `sent-unknown` cohort;
7. temporary playbook s explicitnými decision branches;
8. communication všetkým rotations a support teams.

Runbook bol stiahnutý, nie potichu editovaný, aby historical incident evidence zostala reprodukovateľná.

## 14. Replacement playbook a runbook

### Playbook `PB-PAY-24 — Settlement backlog`

```text
confirm impact a declare incident podľa SLO burn
→ classify capacity, broker, DB, provider alebo consumer fault
→ protect admission a durable state
→ choose drain, failover, provider escalation alebo degraded mode
→ verify completion a data integrity
```

### Runbook `RB-PAY-24 — Bounded never-sent replay`

```text
exact incident a command manifest
→ current lease/state-machine generation
→ dry-run classify max 500 IDs
→ require provider_attempt_id absent
→ require broker publish evidence absent
→ policy/IC approval
→ idempotent replay max 50/s
→ per-ID read-back
→ completion/provider reconciliation
→ second batch only after guardrails
```

Runbook explicitne odmieta `sent-unknown` a `completed` cohorts.

## 15. Runbook acceptance verdict

Dokument je prijatý, keď:

- purpose a exact subject sú explicitné;
- trigger a eligibility sú testovateľné;
- compatible architecture/tool generations sú uvedené;
- prerequisites, access a safety boundaries sú overené;
- observations vedú k explicitným decision branches;
- commands sú scoped, bounded a auditovateľné;
- partial a unknown outcomes majú recovery;
- technical aj business verification sú definované;
- forbidden a second-operation tests prejdú;
- stale alebo wrong subject je odmietnutý;
- owner, reviewers a last-tested generation existujú;
- new responder ho úspešne vykoná v rehearsal-e;
- retirement alebo replacement trigger je definovaný.

## 16. Troubleshooting runbook failure

```text
runbook bol vykonaný, outcome je zlý
→ exact document version a actor
→ intended vs actual subject/generation
→ trigger a preconditions
→ observations a classification
→ commands/parameters a affected manifest
→ partial/unknown outcomes
→ effective-state read-back
→ business a forbidden outcomes
→ rollback/compensation availability
→ stale assumption alebo missing decision branch
→ withdraw, repair a rehearse
```

Najprv zachovaj použitú document generation. Editovanie in-place môže zničiť dôkaz, čo responder skutočne čítal.

## 17. Earlier controls

- standard runbook template;
- owner a reviewer;
- architecture/version compatibility;
- exact subject a manifest;
- read-before-write a dry-run;
- bounded scope/rate;
- approval a policy gates;
- abort criteria;
- business/forbidden verification;
- last-tested generation;
- new-responder rehearsal;
- automatic stale-doc reminders;
- withdrawal a replacement workflow.

## 18. Anti-patterny

### Zoznam príkazov

Neobsahuje trigger, state classification, risk ani outcome.

### Copy-paste ako usability

Rýchlo spustiteľný destructive command iba zrýchli failure.

### Queue klesla, problém je vyriešený

Work mohol byť zahodený, duplikovaný alebo presunutý do downstream bottlenecku.

### Runbook nemá verziu

Nie je možné určiť, ktoré assumptions responder použil.

### Automatizuj všetko

Nejasný decision point sa zmení na rýchly broad side effect.

### Last updated = current

Dokument mohol byť editovaný bez rehearsal-u na current architecture.

## 19. Kontrolné otázky

1. Ako sa runbook a playbook líšia?
2. Čo tvorí exact runbook subject?
3. Aké sekcie musí mať bezpečný runbook?
4. Ako sa observation mení na decision branch?
5. Prečo command potrebuje expected output?
6. Ako sa rollback, compensation a unknown outcome líšia?
7. Čo znamená generation compatibility?
8. Ktoré verification vrstvy má runbook pokryť?
9. Kedy je runbook vhodný na automation?
10. Prečo `RB-PAY-17` vytvoril redelivery amplification?
11. Ako sa dokument bezpečne withdraw-ne?
12. Čo musí overiť runbook acceptance verdict?

## Glossary impact

Relevantné pojmy: runbook, playbook, runbook subject, trigger eligibility, safety boundary, operational decision point, bounded command, affected manifest, unknown operational outcome, runbook generation, last-tested generation, runbook withdrawal, runbook acceptance verdict a new-responder rehearsal.

## Primárne zdroje

- [Google SRE — Managing Incidents](https://sre.google/sre-book/managing-incidents/)
- [Google SRE — Being On-Call](https://sre.google/sre-book/being-on-call/)
- [Google SRE Workbook — Incident Response](https://sre.google/workbook/incident-response/)
- [Google SRE — Emergency Response](https://sre.google/sre-book/emergency-response/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: On-call a escalation](on-call-and-escalation.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
