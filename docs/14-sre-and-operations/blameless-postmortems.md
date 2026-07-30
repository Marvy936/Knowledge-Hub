# Blameless postmortems

Blameless postmortem je reviewovaný a zdieľaný záznam incidentu, ktorý zachytáva user a business impact, timeline, response, príčinné mechanizmy, úspešné aj zlyhané controls a overiteľné follow-up actions bez osobného obviňovania ľudí, ktorí konali s informáciami, incentives a nástrojmi dostupnými v danom čase. Jeho účelom nie je vytvoriť pekný dokument, ale premeniť incident na organizačný learning a production change.

Blameless neznamená anonymný, nepresný ani bez accountability. Human actions sa zapisujú fakticky; action owners majú termíny a verification; leadership poskytuje priority a accepted residual risk má ownera. Osobný blame je zlý analytický model, pretože nevysvetľuje, prečo systém považoval danú action za možnú, bezpečnú alebo normálnu.

## 1. Dominantný incident-to-learning lifecycle

Postmortem nadväzuje na incident a RCA, ale pridáva review, publication, action governance a cross-incident learning. Dokument je iba intermediate artifact; konečný outcome je effective control a znížený recurrence alebo impact risk.

```text
postmortem trigger a exact incident subject
→ evidence-preserving draft
→ factual impact, timeline a response
→ causal analysis a control evaluation
→ what went well / poorly / where we got lucky
→ mechanism-bound action portfolio
→ independent review a safe publication
→ implemented, deployed a effective verification
→ similar-system a recurrence review
→ organizational learning closure
```

Incident response obnovuje službu. RCA vysvetľuje causes. Postmortem uchováva tento knowledge, hodnotí response a zabezpečuje, aby actions nezostali iba v dokumente.

## 2. Exact postmortem subject a trigger

Postmortem patrí immutable incident a document generation. Zachováva incident ID, capability, affected cohorts, impact start/end, severity, release/config generations, response roles, evidence cutoff, document ownera, reviewers, revision a publication state.

```text
postmortem: PM-SRE-PAY-54-v1
incident: SRE-PAY-54
capability: settlement reconciliation
impact: 91 stale alebo unknown merchant settlements
technical cohort: 7 842 active rows incorrectly archived
window: 02:14–06:03 UTC
status: draft → reviewed → published
```

Published document sa neopravuje silent editom; nová evidence vytvára auditovanú revision alebo correction note. Trigger criteria sa definujú pred incidentom: významný user impact, data corruption/loss, SEV-1/2, veľký error-budget burn, destructive intervention, missed recovery objective, monitoring/escalation failure, high-potential near miss alebo recurrence. Minor events môžu mať lightweight review, no criteria nesmú závisieť od reputačného nepohodlia tímu.

## 3. Blameless analysis a accountability

Blameless contract predpokladá, že ľudia mali pracovný cieľ a konali podľa vtedy dostupného local contextu. Analýza sa pýta, aké signals, defaults, permissions, incentives, workload a process urobili dané rozhodnutie pravdepodobným.

Namiesto `operator neopatrne spustil compactor` je presnejšie:

```text
release workflow povolil production activation,
pretože config schema prijala missing scope,
canary mala zero eligible rows
a gate hodnotil exit code namiesto business invariantu.
```

Role alebo identity možno uviesť pre timeline, audit, handoff, action ownership a recognition dobrej response práce. Zakázané je hodnotiace označenie bez causal významu. Úmyselné podvody alebo závažné policy violations patria do príslušného procesu; technická analýza stále skúma prevention, detection a blast-radius limits.

Accountability znamená, že postmortem owner dokončí review, action owners dodajú alebo eskalujú blockers, reviewers odmietnu plytké causes a leadership poskytne capacity. Blamelessness nie je dôvod tolerovať neuzavreté actions.

## 4. Impact, detection a factual timeline

Executive summary v niekoľkých vetách vysvetlí, čo sa stalo, komu, ako dlho, cez aký failure mechanismus, ako prebehla recovery a ktoré actions sú najdôležitejšie. Nesmie deklarovať definitívnu root cause pred dokončením analýzy.

Impact je user-centered a numerický: affected users/operations, duration, failed/delayed/unknown outcomes, financial/legal/security/support impact, data-integrity class, SLO/error-budget consumption, cohorts, confidence a limitations. `Database bola corrupted` je technical state, nie impact statement.

Response timings sa oddeľujú:

```text
time to detect
→ acknowledge
→ declare
→ contain
→ technical recovery
→ business reconciliation
→ full closure
```

Timeline používa exact state transitions, source a confidence, nie retrospektívne hodnotenia. `02:10 — workload načítal config 54 bez tenant_scope; config read-back potvrdzuje absent field` je analyticky hodnotnejšie než `team urobil zlú konfiguráciu`.

## 5. Controls: went well, poorly a luck

`What went well` identifikuje controls a behavior, ktoré treba zachovať. Pri `SRE-PAY-54` business correctness SLI odhalila silent failure, IC zastavil destructive jobs, WAL/audit zachovali IDs, provider podporoval idempotency lookup, isolated restore zabránil broad rewind a responders odmietli unsafe replay.

`What went poorly` pomenúva system gaps: missing scope bol fail-open, canary nemala positive eligible population, job oracle bol exit code, broad role a unbounded batch zvýšili impact, restore decrypt grant bol stale a consistency-group manifest chýbal. Formulácia `team nevedel` sa nahrádza konkrétnym missing signalom alebo contractom.

`Where we got lucky` odhaľuje latentný risk. WAL clean point bol ešte retained, provider ledger dostupný, immutable reference zostala pri väčšine rows, incident nastal mimo najvyššieho peaku a corruption nezasiahla credentials/audit. Luck nie je control; kritické lucky condition potrebuje action alebo explicitné risk acceptance.

## 6. Causal section a response evaluation

Postmortem preberá RCA verdict bez jeho zjednodušenia na dramatický lineárny príbeh. Rozlišuje trigger, technical/systemic roots, escape/detection causes, amplification, recovery delay a residual unknowns. Causal tvrdenia majú evidence a counterfactual podporu.

Zároveň hodnotí incident response: či declaration prišla včas, command roles boli jasné, actions boli bounded, evidence sa zachovalo, communication bola pravdivá, mitigation znížila impact a recovery zahŕňala business reconciliation. Dobrá root cause analýza nekompenzuje zlý response process a naopak.

## 7. Action portfolio a prioritization

Actions musia mapovať na failure mechanisms a kombinovať prevent, detect, contain, recover a learn controls. Iba detection necháva incident opakovať; iba prevention môže byť neúmerne drahá a stále nezlepší recovery.

| ID | Mechanismus | Action | Owner | Priority | Due | Verification |
|---|---|---|---|---|---|---|
| ARCH-219 | missing scope → wildcard | required scope + fail-closed runtime | Settlement Platform | P0 | 2026-08-05 | missing/empty/wrong scope rejected |
| SAFE-87 | unbounded batch | manifest + max 500 rows | Data Platform | P0 | 2026-08-07 | broad batch abort test |
| OBS-311 | silent corruption | transition/correlation SLI | Observability | P1 | 2026-08-12 | controlled failure pages |
| REC-144 | stale decrypt access | restore access canary | Resilience | P1 | 2026-08-10 | isolated drill |
| REC-145 | incomplete consistency group | DB/outbox/broker/provider manifest | Payments SRE | P0 | 2026-08-14 | reconciliation drill |

Priority vychádza z impactu, recurrence, current exposure, lead time, dependency, error-budget a compliance/security urgency. Organizácia môže mať action-item SLO, ale hodnoty sú local policy. `Všetko P0` odstráni schopnosť rozhodovať.

## 8. Review, publication a knowledge distribution

Independent review overuje impact completeness, evidence timeline, causal depth, factual language, control analysis, action mapping, owners/terms, privacy redaction, similar-system scope a publication audience. Unreviewed draft nie je organizational knowledge.

Postmortem sa zdieľa owning a dependent teams, platform/security/data owners, leadership podľa impactu a searchable incident repository. Secrets, PII, exploit details alebo sensitive vendor data patria do redacted alebo restricted annexu. Cieľom je čo najširšie useful learning bez rozšírenia security/privacy risku.

Structured metadata podporuje trend analysis: common triggers, escape causes, detection gaps, dependencies, recovery delays, stale runbooks, overdue actions, toil a repeated technology/control failures. Desať lokálnych incidents môže odhaliť jednu platform root cause.

## 9. Connected postmortem `PM-SRE-PAY-54-v1`

Impact zahŕňal `186 420` broad-archived rows, `7 842` neterminálnych, `613` callbacks so secondary correlation, `91` stale/unknown merchant settlements, nula potvrdených duplicates a business recovery `3 h 49 min`, čím sa prekročil RTO `45 min`.

Learning verdict nebol „jedna osoba zle nastavila parameter“. Destructive workflow považoval missing scope za validný broad intent a delivery/recovery systém túto interpretáciu neodmietol. Replication a backup zachovali validné bytes poškodeného state-u; decrypt/access a consistency-group gaps predĺžili recovery.

Actions preto nesmerovali iba na compactor code, ale aj schema contract, blast-radius guardrail, business canary, detection, restore access, reconciliation a similar-system wildcard audit.

## 10. Action lifecycle a mechanism closure

Action zostáva otvorená cez celý lifecycle:

```text
accepted
→ planned
→ implemented
→ deployed
→ effective read-back
→ verified against original mechanism
→ mechanism closed alebo residual risk accepted
```

Merge alebo ticket status nie je production effectiveness. Verification môže vyžadovať negative test, canary, restore drill, wrong-subject rejection, recurrence-free observation window alebo second scenario. Similar-system search musí skontrolovať, či rovnaký wildcard/default/destructive pattern neexistuje inde.

Pri recurrence sa analyzuje, či ide o rovnaký mechanismus alebo podobný symptom, či previous controls boli effective v správnom scope-e a či vznikol alternate path. Recurrence nie je dôvod na blame; je dôkaz nedokončeného learning/control loopu.

## 11. Postmortem acceptance contract

Positive acceptance preukazuje objective trigger, exact generation, kvantifikovaný impact, evidence timeline, blameless causal depth, response evaluation, controls/luck analysis a mechanism-bound actions. Review a publication musia prejsť pre intended audience.

Closure path vyžaduje deployed/effective verification, similar-system review a recurrence test. Forbidden paths zahŕňajú postmortem ako trest, anonymnú neurčitosť, memory-only timeline, `human error` root, `buďte opatrnejší` action, priority inflation a publikovaný dokument bez action governance.

```text
learning:
incident evidence → causal/control review → actions

closure:
action deployed → effective → mechanism test → trend learning

forbidden:
blame language
impact bez user semantics
luck ignorovaná
closed ticket bez verification
silent revision historical recordu
```

## 12. Troubleshooting postmortem programu

Ak sa documents publikujú, ale reliability sa nemení, sleduj postmortem trigger coverage, time-to-draft/review, action ownership, overdue rate, effective verification, repeated mechanism classes a leadership capacity decisions.

```text
repeated incident
→ prior postmortem generation
→ causal/action mapping
→ deployed scope a effectiveness
→ similar-system review
→ recurrence watch
→ ownership/priority/blocker gap
→ re-open action alebo program design
```

Počet postmortemov nie je success metric. Dôležitá je kvalita learningu a uzavretie high-risk mechanisms.

## 13. Anti-patterny

Postmortem anti-patterny buď poškodzujú psychological safety, alebo vytvárajú dokument bez účinnej zmeny.

- **Postmortem ako trest —** ľudia skrývajú uncertainty a incidenty, čím rastie systemic risk.
- **Blameless znamená nekonkrétny —** vynechanie actions a failures znemožní causal learning a accountability.
- **Šablóna vyplnená po pamäti —** bez preserved evidence vznikne presvedčivý, no nepresný príbeh.
- **Root cause je human error —** organizácia nevie, ktorý executable control zmeniť.
- **Action je buďte opatrnejší —** nie je scoped, owned ani verifiable.
- **Všetko P0 —** priority stratia význam a kritické controls sa utopia.
- **Dokument published, actions zabudnuté —** pre usera je to nerozoznateľné od žiadneho postmortemu.
- **Luck ignorovaná —** latentný high-impact path zostane otvorený.

## 14. Kontrolné otázky

1. Čo robí postmortem blameless, ale accountable?
2. Ktoré objective triggers vyžadujú postmortem?
3. Čo tvorí exact postmortem generation?
4. Ako summary, timeline a causal section plnia odlišné úlohy?
5. Prečo impact musí byť user-centered?
6. Ako sa human action zapíše fakticky?
7. Prečo analyzovať went well, poorly a luck?
8. Ako action portfolio mapuje na mechanisms?
9. Prečo merge nie je mechanism closure?
10. Ako independent review a publication zvyšujú learning?
11. Ako recurrence review odlíši same mechanism od similar symptom?
12. Ktoré learning, closure a forbidden paths patria do acceptance?

## Glossary impact

Relevantné pojmy: postmortem subject, blameless analysis contract, system accountability, factual timeline, what went well/poorly/lucky, action portfolio, action-item SLO, mechanism closure, recurrence review, cross-incident trend analysis a postmortem acceptance contract.

## Primárne zdroje

- [Google SRE — Postmortem Culture](https://sre.google/sre-book/postmortem-culture/)
- [Google SRE Workbook — Postmortem Culture](https://sre.google/workbook/postmortem-culture/)
- [Google SRE — Incident Management Guide](https://sre.google/resources/practices-and-processes/incident-management-guide/)
- [NIST SP 800-61 Rev. 3](https://csrc.nist.gov/pubs/sp/800/61/r3/final)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Root cause analysis](root-cause-analysis.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Backup a restore →](backup-and-restore.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
