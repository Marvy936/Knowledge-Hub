# Runbooks a playbooks

Runbook je versionovaný operational procedure pre rozpoznateľný stav a bounded action. Playbook je širší decision framework pre triedu incidentov alebo operational scenárov, v ktorých sa konkrétna cesta volí podľa evidence, risku a scope-u. Ani jeden nie je iba zoznam príkazov. Dokument prenáša medzi authorom a responderom exact subject, state classification, authority, safety, expected outcome, recovery a verification contract.

Runbook je vhodný tam, kde trigger, preconditions a decision branches možno opakovane reprodukovať. Playbook je vhodný tam, kde najprv treba rozlíšiť viac hypotheses alebo zvoliť medzi viacerými recovery stratégiami. Dobrý playbook môže odkázať na viac runbooks; runbook nesmie predstierať, že každý podobne vyzerajúci symptom má rovnaký state a bezpečnú action.

## 1. Dominantný observation-to-safe-action lifecycle

Operational dokument musí viesť respondera od presnej identity problému k overenému outcome-u. Commands sú iba jedna časť. Najprv sa overí generation a eligibility, potom sa state klasifikuje, vyberie bounded branch a po apply sa číta effective aj business state.

```text
operational intent a exact subject
→ trigger, document a architecture generation
→ prerequisites, access a safety boundary
→ authoritative observation
→ state classification a decision branch
→ bounded action alebo explicitná escalation
→ technical, business a forbidden verification
→ rollback, compensation alebo unknown-outcome handling
→ evidence a follow-up ownership
→ rehearsal, freshness review a withdrawal
```

Runbook je prijateľný iba vtedy, keď správny responder dosiahne intended outcome na current architecture a dokument bezpečne odmietne wrong subject, stale generation alebo nesplnenú precondition.

## 2. Exact runbook subject a generation

Názov `Fix stuck settlements` neposkytuje bezpečný scope. Exact subject obsahuje service a capability, operation alebo failure state, environment/Region/cohort, architecture a release generation, resource/data identity, actor permissions, observation window, allowed maximum action, expected a forbidden outcomes a rollback/escalation boundary.

```text
runbook: RB-PAY-24
subject: unpublished settlement outbox commands
Region: prod-eu1
architecture: lease/state generation v3
eligibility: publisher healthy, command never sent, age > 10 min
actor: incident responder via JIT role
allowed: classify max 500 IDs, replay max 50/s
forbidden: delete, broad lease reset, sent-unknown replay
last tested: release 8.1.0 / 2026-07-29
```

Document version a compatible system generation sú dve odlišné identities. Editovať Markdown dnes nepreukazuje, že procedure bola rehearse-nutá proti current DB schema, state machine, CLI alebo permission modelu. Historical incident musí vedieť reprodukovať presnú document generation, ktorú responder čítal.

## 3. Trigger, eligibility a preconditions

Trigger opisuje signal alebo operator request, ktorý procedure otvára. Eligibility opisuje observations, pri ktorých sa smie použiť. Preconditions chránia execution boundary: správny environment a subject, required access, dependency health, incident alebo maintenance state, backup/recovery availability, compatible generations a approval pri high-risk action.

```text
page: unpublished queue age > 10 min
AND publisher health = ready
AND provider_attempt_id absent
AND broker publish audit absent
AND lease generation = v3
→ never-sent cohort eligible na bounded replay
```

Samotný vek row nie je state classification. Ak chýba provider alebo broker evidence, outcome môže byť unknown. Runbook musí radšej zastaviť a eskalovať než vybrať najslabšiu interpretáciu iba preto, aby pokračoval.

## 4. Observation a state classification

Každý diagnostic command musí vysvetliť, čo pozoruje, na ktorej boundary, aký result sa očakáva a ako výsledok mení decision. Raw query bez semantics prenáša syntax, nie knowledge.

Pre settlement backlog je potrebné odlíšiť aspoň:

```text
never-sent
→ durable outbox existuje
→ broker publish evidence absent
→ provider attempt absent
→ bounded replay môže byť povolený

in-flight
→ active lease/heartbeat alebo broker delivery
→ ďalší consumer forbidden

sent-unknown
→ publish/provider attempt možný
→ final acknowledgement chýba
→ automatic replay forbidden
→ ledger reconciliation

completed
→ authoritative provider outcome existuje
→ replay forbidden
```

Classification má byť reprodukovateľná nad exact manifestom IDs. Ak procedure používa neurčité „staré rows“ alebo „stuck messages“, skrýva rozdiel medzi stavmi s úplne iným duplicate a data-loss riskom.

## 5. Playbook ako decision framework

Playbook rieši scenario space širší než jeden bounded procedure. Pri settlement backloge najprv rozlišuje capacity saturation, broker failure, DB contention, provider slowdown, consumer defect alebo data-integrity risk. Každá branch má vlastný containment a môže aktivovať iný runbook.

```text
impact a SLO burn
→ exact incident subject
→ preserve durable state a evidence
→ capacity/broker/DB/provider/consumer classification
→ admission, failover, drain, vendor alebo degraded branch
→ selected runbook s own eligibility
→ business completion a integrity verification
```

Playbook neobsahuje neurčité „skús všetky možnosti“. Určuje observations, decision authority, incompatible simultaneous actions a moment, keď treba incident deklarovať alebo privolať specialistu.

## 6. Bounded commands a execution contract

Command musí byť parameterizovaný exact identity, read-before-write, scoped, count/rate bounded, auditovateľný, idempotentný alebo chránený idempotency keyom, vybavený timeoutom a expected outputom. Potrebuje aj behavior pri partial alebo unknown outcome-u.

Nebezpečný command:

```sql
DELETE FROM settlement_outbox
WHERE created_at < now() - interval '15 minutes';
```

Nevie rozlíšiť never-sent, in-flight a sent-unknown state. Nemá tenant, manifest, count limit, dry-run, transaction plan, backup ani business recovery contract.

Bezpečnejší execution pattern:

```text
select exact candidate IDs
→ classify authoritative state per ID
→ produce immutable manifest
→ review count, tenant a risk
→ acquire approval/fence
→ execute bounded idempotent action
→ read back per-ID result
→ reconcile broker/provider/business state
```

Copy-paste usability nesmie znamenať copy-paste blast radius. Ak action nie je bezpečná pre unreviewed input, interface má vyžadovať typed manifest alebo generated plan.

## 7. Verification a acceptance boundaries

Exit code `0` dokazuje iba, že tool neoznámil failure podľa vlastnej semantics. Runbook musí overiť source/config generation, effective runtime state, service behavior, pôvodný business outcome, forbidden side effects a ďalšiu nezávislú operation.

```text
source/config
→ správna version a parameters

effective state
→ authoritative runtime prijal zmenu

service
→ queue/latency/errors/dependencies sa správajú podľa hypothesis

business
→ pôvodná user operation sa dokončila správne

forbidden
→ žiadny duplicate, data loss, cross-tenant alebo broader scope

second operation
→ nový nezávislý subject prejde bez manual correction
```

Verification musí uviesť observation window. Krátky pokles queue length môže znamenať delete alebo presun bottlenecku, nie recovery.

## 8. Rollback, compensation a unknown outcome

Nie každá operation je reverzibilná. Config change môže mať rollback, external provider effect potrebuje reconciliation alebo compensation, delete môže vyžadovať restore a failover fencing pred failbackom. Procedure musí odlíšiť failure pred side effectom, confirmed success, partial success a unknown outcome.

Retry po unknown outcome bez idempotency môže vytvoriť duplicate business effect. Runbook preto nesmie všeobecne hovoriť „zopakuj krok“. Musí určiť evidence, podľa ktorej sa retry povolí, alebo explicitne odovzdať cohort na ledger reconciliation a human authority.

## 9. Automation boundary

Dobrý runbook je kandidát na automation, ale automatizuje sa decision contract, nie iba shell text. Automation potrebuje typed inputs, subject/generation validation, current-state read, plan, policy/approval, bounded apply, idempotency, per-step evidence, compensation, business validation a emergency stop.

```text
runbook observation/decision contract
→ executable typed workflow
→ policy-bound subject
→ dry-run plan
→ bounded mutation
→ effective/business read-back
→ stop, compensate alebo escalate
```

Nejasný judgment point sa nesmie skryť default branchom. Ak `sent-unknown` cohort potrebuje business decision, automation ho má fenced odložiť a pripraviť evidence, nie automaticky replayovať.

## 10. Freshness, rehearsal a withdrawal

Runbook driftuje spolu so schema, state machine, topology, identity modelom, CLI, provider contractom a recovery mechanismom. Metadata preto obsahuje ownera, reviewers, compatible versions, dependencies, last tested generation a retirement trigger.

Rehearsal môže byť sandbox, read-only production validation, game day, shadow execution, fault injection, tabletop, new-responder exercise alebo scheduled canary. Musí obsahovať aj wrong subject alebo nesplnenú precondition a preukázať, že procedure unsafe branch odmietne.

Stale alebo nebezpečný runbook sa withdraw-ne ako immutable historical generation a nahradí novým dokumentom. Tiché editovanie po incidente môže zničiť evidence o tom, čo responder skutočne vykonal a prečo.

## 11. Connected incident `SRE-PAY-53`

Primary responder otvoril `RB-PAY-17 — Clear stuck settlement leases`, vytvorený pre starú architecture, kde lease nemal heartbeat extension a command spracúval jediný consumer. Runbook prikazoval scale workers na 240, reset leases staršie než 15 minút, restart publisher a sledovanie queue length.

Chýbala compatible generation, state classification, dry-run count, maximum scope/rate, DB/provider guardrail, incident trigger, expected drain rate, duplicate/unknown verification a reconciliation path. V lease v3 mohol byť heartbeat timestamp starší než 15 minút počas provider slowdown-u, hoci command zostával in-flight.

Broad reset sprístupnil `62 418` commands druhému consumer cohortu. Broker redeliveries a DB/provider writes vzrástli; `143` operations prešlo do `sent-unknown`. Idempotency keys zabránili potvrdenému duplicate settlementu, ale vyžadovala sa provider-ledger reconciliation. Queue krátko klesla, hoci completion latency rástla.

Root failure bol stale procedural document bez generation, state classification a safety contractu, ktorý aplikoval broad lease reset na semanticky odlišnú architecture.

## 12. Containment a replacement contract

IC zachoval executed SQL, actor, timestamp a affected IDs, označil `RB-PAY-17` ako withdrawn, zastavil ďalšie resets a unbounded replays, klasifikoval affected IDs, znížil admission/concurrency a reconcilioval `sent-unknown` cohort. Všetky rotations dostali explicitný notice; dokument nebol potichu prepísaný.

Replacement playbook `PB-PAY-24 — Settlement backlog` najprv deklaruje impact, chráni durable state a rozlišuje capacity, broker, DB, provider a consumer branch. Runbook `RB-PAY-24 — Bounded never-sent replay` vyžaduje current lease generation, dry-run max 500 IDs, absent provider attempt aj broker evidence, IC/policy approval, replay max 50/s, per-ID read-back a completion reconciliation. `sent-unknown` a `completed` cohorts explicitne odmieta.

## 13. Runbook acceptance contract

Positive path musí preukázať, že eligible exact subject prejde observation, classification, bounded action a business verification. Wrong-subject path musí odmietnuť iný tenant, Region alebo state. Stale-generation path musí zastaviť procedure pred mutation. Unknown-outcome path musí fenced odovzdať cohort na reconciliation.

```text
positive:
never-sent manifest → bounded replay → provider completion

wrong subject:
foreign tenant alebo in-flight state → deny

stale generation:
incompatible lease/schema/tool → stop + replacement

unknown:
possible external effect → no retry + reconcile

continuity:
new responder → rehearsal → rovnaký safe verdict
```

Acceptance zahŕňa ownera, reviewers, current last-tested generation, withdrawal trigger a new-responder rehearsal. Druhý batch sa spúšťa až po guardrailoch a prvom business read-backu.

## 14. Troubleshooting runbook failure-u

Ak procedure bola vykonaná, ale outcome je zlý, najprv zachovaj presnú document version a affected manifest. Potom porovnaj intended a actual subject/generation, preconditions, observations, classification, commands, partial/unknown outcomes, effective state a business side effects.

```text
bad outcome po runbooku
→ document generation a actor
→ actual subject/system generation
→ trigger a eligibility
→ observation/classification branch
→ manifest/parameters/action log
→ partial alebo unknown effects
→ business/forbidden read-back
→ withdraw, recover, repair a rehearse
```

Editovanie dokumentu pred preservation môže zničiť causal evidence.

## 15. Anti-patterny

Tieto anti-patterny prenášajú responderovi syntax alebo optimistic assumption namiesto decision a safety contractu.

- **Zoznam príkazov —** neobsahuje trigger, state classification, authority, risk ani business outcome.
- **Copy-paste ako usability —** rýchlo spustiteľný destructive command iba zrýchli a rozšíri failure.
- **Queue klesla, problém je vyriešený —** work mohol byť zahodený, duplikovaný alebo presunutý do downstream bottlenecku.
- **Runbook nemá generation —** nemožno určiť, ktoré architecture assumptions a tools responder použil.
- **Automatizuj všetko —** nejasný decision point sa zmení na rýchly broad side effect; uncertainty potrebuje fenced escalation.
- **Last updated znamená current —** text mohol byť editovaný bez rehearsal-u na current release a permissions.

## 16. Kontrolné otázky

1. Ako sa runbook a playbook líšia?
2. Čo tvorí exact runbook subject a generation?
3. Ako trigger, eligibility a preconditions chránia execution?
4. Prečo vek row nie je state classification?
5. Ako observation vedie k decision branchu?
6. Čo robí command bounded a copy-safe?
7. Aké verification boundaries má procedure pokryť?
8. Ako sa rollback, compensation a unknown outcome líšia?
9. Kedy je runbook vhodný na automation?
10. Prečo `RB-PAY-17` vytvoril redelivery amplification?
11. Ako sa dokument bezpečne withdraw-ne?
12. Ktoré positive, wrong-subject, stale, unknown a continuity paths patria do acceptance?

## Glossary impact

Relevantné pojmy: runbook, playbook, runbook subject, document/system generation, trigger eligibility, operational state classification, bounded command, affected manifest, unknown operational outcome, last-tested generation, withdrawal a runbook acceptance contract.

## Primárne zdroje

- [Google SRE — Managing Incidents](https://sre.google/sre-book/managing-incidents/)
- [Google SRE — Being On-Call](https://sre.google/sre-book/being-on-call/)
- [Google SRE Workbook — Incident Response](https://sre.google/workbook/incident-response/)
- [Google SRE — Emergency Response](https://sre.google/sre-book/emergency-response/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: On-call a escalation](on-call-and-escalation.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Root cause analysis →](root-cause-analysis.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
