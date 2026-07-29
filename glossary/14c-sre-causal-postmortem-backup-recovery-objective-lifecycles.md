# SRE causal learning, postmortem, backup and recovery-objective glossary entries

## RCA subject

Versionovaný analysis subject spájajúci incident, affected business capability, exact service/data/operation scope, release/configuration generations, impact interval, evidence cutoff a ownera. Pozri [Root cause analysis](docs/14-sre-and-operations/root-cause-analysis.md).

## Proximate mechanism

Bezprostredný technický state transition, ktorým trigger vytvoril nežiaduci outcome; nie je automaticky dostatočným vysvetlením systémovej root cause. Pozri [Root cause analysis](docs/14-sre-and-operations/root-cause-analysis.md).

## Technical root cause

Technický mechanismus, bez ktorého by konkrétny incidentný outcome nevznikol v analyzovanom scope-e. Pozri [Root cause analysis](docs/14-sre-and-operations/root-cause-analysis.md).

## Systemic root cause

Design, control, governance alebo organizačná podmienka, ktorá umožnila technical mechanismu existovať, prejsť kontrolami alebo dosiahnuť impact. Pozri [Root cause analysis](docs/14-sre-and-operations/root-cause-analysis.md).

## Escape cause

Dôvod, prečo defect alebo unsafe condition neodhalili testy, review, policy gate, canary alebo rollout controls pred production impactom. Pozri [Root cause analysis](docs/14-sre-and-operations/root-cause-analysis.md).

## Detection cause

Dôvod, prečo production evidence alebo monitoring neodhalili failure mechanismus skôr alebo na správnej user/business boundary. Pozri [Root cause analysis](docs/14-sre-and-operations/root-cause-analysis.md).

## Amplification cause

Podmienka zväčšujúca blast radius, duration, attempt count, data scope alebo downstream impact pôvodného failure mechanismu. Pozri [Root cause analysis](docs/14-sre-and-operations/root-cause-analysis.md).

## Recovery-delay cause

Access, dependency, documentation, capacity, compatibility alebo decision gap, ktorý predĺžil containment, restore, reconciliation alebo business recovery. Pozri [Root cause analysis](docs/14-sre-and-operations/root-cause-analysis.md).

## Causal graph — RCA

Evidence-backed graf spájajúci trigger, state transitions, latent conditions, controls a business impact tak, aby bolo možné rozlíšiť necessary, sufficient a amplifying branches. Pozri [Root cause analysis](docs/14-sre-and-operations/root-cause-analysis.md).

## Counterfactual test — RCA

Otázka, či by odstránenie alebo zmena konkrétnej podmienky zabránila incidentu alebo obmedzila jeho impact; používa sa na disciplinovanie causal claims. Pozri [Root cause analysis](docs/14-sre-and-operations/root-cause-analysis.md).

## Root-cause depth

Úroveň causal explanation dostatočne konkrétna na actionable a controllable mechanismus, ale nie redukovaná iba na osobu, trigger alebo príliš abstraktné tvrdenie. Pozri [Root cause analysis](docs/14-sre-and-operations/root-cause-analysis.md).

## Corrective-action portfolio

Koordinovaná množina prevent, detect, contain, recover a learning controls mapovaných na konkrétne failure mechanisms. Pozri [Root cause analysis](docs/14-sre-and-operations/root-cause-analysis.md) a [Blameless postmortems](docs/14-sre-and-operations/blameless-postmortems.md).

## Mechanism closure

Dôkaz, že corrective control je nielen implementovaný, ale effective v production-relevant scope-e a pôvodný failure path neprejde recurrence alebo second-operation testom. Pozri [Root cause analysis](docs/14-sre-and-operations/root-cause-analysis.md).

## Similar-system search

Review príbuzných services, workflows alebo control implementations s cieľom nájsť rovnaký failure mechanismus mimo pôvodného incident scope-u. Pozri [Root cause analysis](docs/14-sre-and-operations/root-cause-analysis.md).

## RCA acceptance verdict

Rozhodnutie, že incident má evidence-backed timeline, dostatočný causal model, odlíšené root/escape/amplification/recovery causes a overiteľné corrective actions vedúce k recurrence closure. Pozri [Root cause analysis](docs/14-sre-and-operations/root-cause-analysis.md).

## Postmortem subject

Immutable alebo auditovane versionovaný document subject spájajúci incident generation, impact interval, affected capability, evidence cutoff, ownera, reviewers a publication state. Pozri [Blameless postmortems](docs/14-sre-and-operations/blameless-postmortems.md).

## Blameless analysis contract

Princíp, že human actions sa opisujú fakticky v kontexte dostupných informácií, tools a incentives a analysis hľadá opraviteľné system/process conditions namiesto osobného obviňovania. Pozri [Blameless postmortems](docs/14-sre-and-operations/blameless-postmortems.md).

## System accountability

Zodpovednosť za ownerstvo dokumentu, corrective actions, priorities, verification a residual-risk decisions bez redukovania incidentu na osobnú vinu. Pozri [Blameless postmortems](docs/14-sre-and-operations/blameless-postmortems.md).

## Postmortem trigger

Vopred definovaná condition, napríklad data loss, user-visible impact, severity, recovery-objective miss alebo monitoring failure, ktorá vyžaduje post-incident review. Pozri [Blameless postmortems](docs/14-sre-and-operations/blameless-postmortems.md).

## Factual timeline — postmortem

Chronológia overených incident state transitions s timestampom, subjectom, evidence source-om a outcome-om bez retrospectívneho osobného hodnotenia. Pozri [Blameless postmortems](docs/14-sre-and-operations/blameless-postmortems.md).

## Where we got lucky

Postmortem sekcia identifikujúca podmienky, ktoré náhodne obmedzili impact, ale nepredstavovali spoľahlivý control a preto vyžadujú risk decision alebo action. Pozri [Blameless postmortems](docs/14-sre-and-operations/blameless-postmortems.md).

## Action-item SLO

Lokálny časový a quality contract pre prioritizáciu, implementáciu a verification postmortem actions; nie je univerzálnou hodnotou bez organizačného contextu. Pozri [Blameless postmortems](docs/14-sre-and-operations/blameless-postmortems.md).

## Recurrence review

Analýza opakovaného incidentu, ktorá overuje, či ide o rovnaký failure mechanismus, alternate path, neúčinný control alebo príliš lokálne previous actions. Pozri [Blameless postmortems](docs/14-sre-and-operations/blameless-postmortems.md).

## Cross-incident trend analysis

Agregácia structured postmortem metadata s cieľom nájsť opakované causal classes, detection gaps, recovery delays, stale controls alebo platform-wide investment needs. Pozri [Blameless postmortems](docs/14-sre-and-operations/blameless-postmortems.md).

## Postmortem acceptance verdict

Dôkaz, že incident impact, timeline, response, causal model, luck, corrective actions, review, publication a effective-state action tracking tvoria complete organizational learning artifact. Pozri [Blameless postmortems](docs/14-sre-and-operations/blameless-postmortems.md).

## Protected backup subject

Versionovaný recovery subject spájajúci business capability, exact data stores, schema/application generations, scope, consistency group, acknowledgement boundary, key dependencies, retention, RPO/RTO a ownera. Pozri [Backup a restore](docs/14-sre-and-operations/backup-and-restore.md).

## Consistency group — backup

Versionovaný zoznam datastore, event, evidence, configuration, identity a external-ledger subjects, ktoré musia byť obnovené alebo reconciliované ako jeden business-valid state. Pozri [Backup a restore](docs/14-sre-and-operations/backup-and-restore.md).

## Crash-consistent backup

Recovery representation zodpovedajúca náhlemu zastaveniu systému; engine recovery môže byť možná, ale application alebo cross-system business invariants nemusia byť potvrdené. Pozri [Backup a restore](docs/14-sre-and-operations/backup-and-restore.md).

## Application-consistent backup

Recovery representation vytvorená s application/datastore koordináciou tak, aby internal application invariants boli obnoviteľné. Pozri [Backup a restore](docs/14-sre-and-operations/backup-and-restore.md).

## Business-consistent recovery

Obnovený a reconciliovaný state všetkých relevantných stores a external effects, ktorý spĺňa critical business invariants a customer outcome. Pozri [Backup a restore](docs/14-sre-and-operations/backup-and-restore.md).

## Clean point

Recovery point klasifikovaný ako nezasiahnutý analyzovanou corruption, compromise alebo invalid state transition a vhodný pre plánovaný recovery flow. Pozri [Backup a restore](docs/14-sre-and-operations/backup-and-restore.md).

## Recovery candidate

Konkrétna backup/snapshot/log generation vybraná na restore po vyhodnotení clean pointu, completeness, key/access eligibility, compatibility a business consistency. Pozri [Backup a restore](docs/14-sre-and-operations/backup-and-restore.md).

## Effective backup assignment

Dôkaz, že deklarovaná backup policy skutočne zahrnula exact resource, vytvorila expected generation, dokončila required copy, uplatnila retention/immutability a je obnoviteľná. Pozri [Backup a restore](docs/14-sre-and-operations/backup-and-restore.md).

## Recovery catalog

Dostupný inventory recovery generations, timestamps, classifications, locations, retention, key dependencies, restore tooling a posledného tested statusu. Pozri [Backup a restore](docs/14-sre-and-operations/backup-and-restore.md).

## Key recoverability

Schopnosť authorized recovery identity nájsť a použiť správny cryptographic key v affected account/Regione a restore generation bez oslabenia separation-of-duties. Pozri [Backup a restore](docs/14-sre-and-operations/backup-and-restore.md).

## Isolated restore

Materializácia recovery candidate-u v oddelenom validation alebo recovery environmentu pred production merge/cutoverom, aby sa zachovalo evidence a obmedzil blast radius. Pozri [Backup a restore](docs/14-sre-and-operations/backup-and-restore.md).

## Recovery fencing

Mechanismus zabraňujúci starému a novému writerovi nekontrolovane mutovať rovnaký business subject počas restore, replay, merge alebo cutoveru. Pozri [Backup a restore](docs/14-sre-and-operations/backup-and-restore.md).

## Post-point divergence

Množina validných, unknown alebo external operations vzniknutých po zvolenom recovery pointe, ktoré treba replaynúť, merge-núť, kompenzovať alebo reconciliovať. Pozri [Backup a restore](docs/14-sre-and-operations/backup-and-restore.md).

## Side-by-side restore

Restore historického subjectu do paralelného environmentu s následnou extrakciou a bounded merge/reconciliation namiesto broad rewind-u current production state-u. Pozri [Backup a restore](docs/14-sre-and-operations/backup-and-restore.md).

## Restore validation stack

Postupná validation od infrastructure a engine cez data/application až po business a forbidden outcomes. Pozri [Backup a restore](docs/14-sre-and-operations/backup-and-restore.md).

## Backup/restore acceptance verdict

Dôkaz, že exact protected subject má effective, isolated a readable recovery generations a current responder dokáže vybrať clean point, obnoviť, reconciliovať, fence-núť a validovať business service v objectives. Pozri [Backup a restore](docs/14-sre-and-operations/backup-and-restore.md).

## Recovery-objective subject

Versionovaný subject spájajúci business capability, cohort, consistency group, failure scenario, measurement boundaries, degraded-mode assumptions, dependency objectives a ownera. Pozri [RPO a RTO](docs/14-sre-and-operations/rpo-and-rto.md).

## Recovery Point Objective

Bod v čase, ku ktorému musia byť dáta po disruption obnovené; reprezentuje tolerovanú data-change exposure alebo reconstruction window pre exact recovery subject. Pozri [RPO a RTO](docs/14-sre-and-operations/rpo-and-rto.md).

## Recovery Time Objective

Celkový prijateľný recovery interval pre exact capability pred prekročením business alebo mission impact tolerance, meraný na explicitnej start/end boundary. Pozri [RPO a RTO](docs/14-sre-and-operations/rpo-and-rto.md).

## Business-consistent RPO

Recovery-point objective vyhodnotený nad celým consistency groupom a business invariants, nie iba timestampom jedného datastore-u. Pozri [RPO a RTO](docs/14-sre-and-operations/rpo-and-rto.md).

## Actual recovered point

Skutočný timestamp alebo sequence boundary obnoveného validného state-u, ktorý sa porovnáva s RPO targetom. Pozri [RPO a RTO](docs/14-sre-and-operations/rpo-and-rto.md).

## Actual recovery time

Nameraný interval od definovaného business disruption startu po safe recovery end boundary vrátane restore, validation, reconciliation a work recovery podľa contractu. Pozri [RPO a RTO](docs/14-sre-and-operations/rpo-and-rto.md).

## Maximum tolerable disruption

Hranica, za ktorou outage alebo degradation vytvára neprijateľný business/mission impact; lokálny framework ju môže označovať MTD, MTPD alebo podobným termínom. Pozri [RPO a RTO](docs/14-sre-and-operations/rpo-and-rto.md).

## Work Recovery Time

Čas po technickom restore potrebný na backlog drain, reconciliation, manual case completion, customer communication a návrat capability do normálneho business state-u. Pozri [RPO a RTO](docs/14-sre-and-operations/rpo-and-rto.md).

## Event-based RPO

Data-loss alebo reconstruction objective vyjadrený počtom či invariantom business events, napríklad nulou permanently lost acknowledged intents, namiesto samotného času. Pozri [RPO a RTO](docs/14-sre-and-operations/rpo-and-rto.md).

## Dependency recovery budget

Časová časť end-to-end RTO pridelená konkrétnej detection, access, restore, dependency, validation alebo reconciliation boundary. Pozri [RPO a RTO](docs/14-sre-and-operations/rpo-and-rto.md).

## Degraded recovery objective

Časovo a funkčne bounded objective pre bezpečné obnovenie subsetu critical capability pred úplnou recovery, s explicitnými allowed a forbidden operations. Pozri [RPO a RTO](docs/14-sre-and-operations/rpo-and-rto.md).

## Target-versus-actual recovery

Explicitné porovnanie deklarovaných RPO/RTO targets s posledným nameraným recovery pointom, data-loss/reconstruction výsledkom a actual business recovery časom. Pozri [RPO a RTO](docs/14-sre-and-operations/rpo-and-rto.md).

## RPO/RTO acceptance verdict

Dôkaz, že objectives sú odvodené z BIA, viazané na exact scenarios a consistency groups, implementované v recovery design-e a splnené current-generation timed exercise-om. Pozri [RPO a RTO](docs/14-sre-and-operations/rpo-and-rto.md).
