# Root cause analysis

Root cause analysis — RCA — je systematické vysvetlenie, prečo konkrétny nežiaduci outcome vznikol, prečo ho existujúce kontroly nezastavili, prečo dosiahol daný impact a ktoré mechanizmy treba zmeniť, aby sa rovnaký failure path neopakoval. Nie je to hľadanie jednej osoby, posledného commitu ani prvého chybového logu. V komplexnom systéme incident typicky vzniká kombináciou triggera, technického mechanismu, latentných podmienok, escape a detection gaps, amplification controls a recovery constraints.

RCA musí zostať viazaná na evidence a presný incident subject. Presvedčivý príbeh bez reprodukovateľnej timeline, competing hypotheses a counterfactual reasoning môže byť rovnako nebezpečný ako žiadna analýza, pretože vedie k actions, ktoré zatvoria ticket, ale nie failure mechanismus.

## 1. Dominantný outcome-to-mechanism lifecycle

Analýza začína nežiaducim business outcome-om a postupne rekonštruuje state transitions, causal paths a zlyhané barriers. Action portfolio sa odvodzuje až z overeného mechanismu a uzatvára sa production evidence, nie statusom `Done`.

```text
incident a exact nežiaduci outcome
→ RCA subject, evidence cutoff a known-good/bad boundaries
→ overená timeline state transitions
→ trigger, proximate a impact mechanismus
→ technical/systemic/escape/detection/amplification/recovery causes
→ competing hypotheses a causal graph
→ counterfactual a barrier tests
→ corrective-action portfolio
→ deployed/effective control verification
→ recurrence a second-operation validation
```

Trigger vysvetľuje, čo failure path aktivovalo. Root cause vysvetľuje, ktorý controllable mechanismus umožnil nežiaduci outcome. Escape cause vysvetľuje, prečo ho delivery controls pustili; amplification cause, prečo bol impact taký veľký; recovery cause, prečo obnova trvala tak dlho.

## 2. Exact RCA subject a outcome

Tvrdenie `analyzujeme payments incident` je príliš široké. Exact subject obsahuje incident ID, affected capability, service/data/operation scope, release a policy generations, tenant/Region/cohort, impact interval, evidence cutoff, known-good a first-known-bad state, ownera a explicitne vylúčený scope.

```text
incident: SRE-PAY-54
capability: merchant settlement reconciliation
release: payments-api 7.25.0
job: settlement-ledger-compactor generation 54
scope: production EU, all merchant tenants
first bad mutation: 2026-07-29 02:14:07 UTC
impact: active settlements označené ako archived
analysis cutoff: 2026-07-29 12:00 UTC
excluded: provider-side settlement calculation
```

Outcome sa zapisuje cez intended a observed transition. V tomto incidente nemala „database problém“. Aktívne settlement rows mali zostať queryable a correlatable, no compactor ich označil ako archived, odstránil provider/outbox correlation metadata, callbacks sa nedali bezpečne priradiť a merchant-visible state zostal stale alebo unknown.

## 3. Timeline ako state-transition evidence

Timeline nie je dump incident chatu. Zachytáva iba kauzálne významné transitions s exact subjectom, timestampom, clock authority a dôkazom.

| Čas UTC | Subject | Transition | Dôkaz |
|---|---|---|---|
| 02:02 | release 7.25.0 | deployed → ready | deployment/readiness evidence |
| 02:10 | compactor config 54 | loaded bez `tenant_scope` | config read-back |
| 02:14:07 | batch 54-1 | eligible query → wildcard scope | query plan a job log |
| 02:14:12 | settlement ledger | 186 420 rows → archived | WAL a audit |
| 02:15–02:31 | replicas/backups | current corruption → replicated/captured | replication/snapshot evidence |
| 02:33 | provider callbacks | normal → correlation failures | callback logs |
| 02:37 | business SLI | correctness fast burn | SLI evaluation |
| 02:41 | incident | detected → declared | incident log |
| 02:48 | compactor | active → disabled | controller audit |

Application, DB commit, provider a incident-chat clocks nemusia byť identické. Timeline preto uvádza time authority a uncertainty; inak sa môže recovery action omylom zaradiť pred causal mutation.

## 4. Trigger, mechanisms a causal taxonomy

Prvý production run compactoru generation 54 bol trigger. Proximate technical mechanismus bol:

```text
missing tenant_scope
→ query generator použil wildcard semantics
→ destructive batch zahrnul všetkých tenantov
→ active rows prešli do archived state-u
```

Impact mechanismus pokračoval odstránením correlation metadata, nemožnosťou priradiť provider callback a stale/unknown merchant outcome-om. Trigger však nebol root cause; rovnaký run by incident nevytvoril, keby destructive operation chýbajúci scope fail-closed odmietla.

Užitočná RCA rozlišuje viac príčinných vrstiev:

- **technical root cause —** missing scope sa pri destructive query interpretoval ako wildcard;
- **systemic root cause —** destructive-operation contract nemal mandatory scope, affected manifest, max rows/rate ani invariant gate;
- **escape cause —** zero-row canary a exit-code oracle neobsahovali positive eligible population ani forbidden-state assertion;
- **detection cause —** monitoring sledoval job errors, nie active-to-archived transitions a callback correctness;
- **amplification cause —** broad DB role a unbounded multi-tenant batch umožnili 186 420 mutations;
- **recovery-delay cause —** restore identity nemala current decrypt grant a consistency-group/post-point manifest nebol pripravený.

Jedna veta `root cause bol bug` tieto rozhodovacie boundaries odstráni.

## 5. Causal graph, hypotheses a counterfactuals

Causal graph ukazuje paralelné podmienky a ich úlohu:

```text
release 7.25.0
       |
       v
missing tenant_scope ----> wildcard default
       |                         |
missing fail-closed schema -----+
                                 v
                        broad destructive query
                       /        |         \
                  no max rows  broad role  zero-row canary
                       \        |         /
                                 v
                       186 420 rows archived
                                 |
                    correlation metadata removed
                                 |
                       callback mapping failure
                                 |
                    stale/unknown merchant state
```

Competing hypotheses sa zapisujú spolu s očakávaným a observed evidence. Provider poškodené callbacks, replica lag alebo manual query boli relevantné možnosti, ale provider payloady boli validné, failures nastali aj na primary a audit actor bol workload identity. WAL, query plan a batch IDs potvrdili compactor hypothesis.

Counterfactual otázky disciplinujú causal tvrdenia. Keby `tenant_scope` bol mandatory a fail-closed, broad batch by nevznikol. Keby canary obsahovala eligible rows a invariant check, release gate by zlyhal. Keby existoval `max_rows=500`, impact by mal menší blast radius. Counterfactual nie je úplný matematický dôkaz, ale oddeľuje causal control od korelácie.

## 6. Hranice Five Whys a actionable depth

Five Whys môže pomôcť rozvinúť jednoduchý lineárny chain, no distributed incident má paralelné branches a počet päť nie je zákon. Metóda ľahko skončí pri `human error`, ignoruje escape/detection/recovery causes alebo je vedená k preferovanému záveru.

Analýza má ísť do controllable a testovateľnej hĺbky. `Engineer zabudol parameter` je plytké; `komplexné systémy zlyhávajú` je príliš abstraktné. Actionable verdict znie: destructive production API akceptovala optional scope, runtime použil wildcard default, policy nekontrolovala affected manifest a canary neobsahovala positive mutation population.

Human action sa zapisuje fakticky a v context-e. Responder spustil current označený runbook, pretože alert naň odkazoval a queue panel krátko ukazoval zlepšenie. To je presnejšie než hodnotenie `bezhlavo spustil zlý príkaz`. Úmyselné policy violation sa môže riešiť separátnym people/compliance procesom; technická RCA stále analyzuje detekciu a obmedzenie.

## 7. Evidence quality a confidence

Každé významné tvrdenie potrebuje source, subject, timestamp, generation, completeness, retention status, confidence a limitation. DB WAL môže autoritatívne potvrdiť mutation, ale nie user-visible semantics; provider ledger a merchant projection sú potrebné pre business outcome.

```text
WAL/transaction audit
→ mutation truth

config/query plan
→ execution intent a generation

provider ledger
→ external side-effect truth

application projection/support evidence
→ user-visible interpretation
```

Dashboard aggregation a recollection sú useful leads, nie automatická causal authority. Evidence cutoff tiež zabraňuje tomu, aby sa neskoršia informácia retrospektívne tvárila ako dostupná responderom počas incidentu.

## 8. Connected incident `SRE-PAY-54`

Release `payments-api 7.25.0` pridal `settlement-ledger-compactor`. Intended eligibility bola exact tenant, terminal settlement, finalized provider a age nad 90 dní. Production config vynechala `tenant_scope`; schema to dovolila a query generator interpretoval missing scope ako all tenants.

Canary dataset nemal žiadne eligible rows, preto test dostal `0 rows affected`, job skončil exit code `0` a rollout gate ho označil successful. Prvý production batch vybral `186 420` rows, z toho `7 842` neterminálnych, odstránil correlation metadata, `613` callbacks potrebovalo secondary evidence a `91` merchant-visible settlements zostalo stale alebo unknown. Replication a snapshots faithfully zachytili poškodenú business semantics.

Causal verdict bol:

```text
trigger:
first production run compactor generation 54

technical root:
missing scope → wildcard destructive query

systemic root:
no fail-closed destructive-operation contract

escape:
zero-row canary + exit-code oracle

amplification:
broad role + unbounded multi-tenant batch

recovery delay:
stale decrypt/access path + missing consistency-group manifest
```

## 9. Containment a corrective-action portfolio

RCA nesmie spomaľovať urgentné containment. Compactor generation 54 bol disabled, jeho write capability revoked, config/query/plan/actor/WAL/affected IDs preserved, ďalšie destructive jobs blocked a current corrupted state snapshotnutý na forensic comparison. Broad production rewind sa nezačal bez clean-point a divergence analýzy.

Action portfolio pokrýva viac control layers. Mechanismus odstráni mandatory `tenant_scope`, fail-closed runtime a typed destructive API bez wildcard defaultu. Blast radius obmedzí immutable affected manifest, per-tenant max rows/rate a invariant abort. Detection zlepší transition/correlation SLI a positive business canary. Recovery zlepší consistency-group inventory, isolated PITR, decrypt/access canary a provider reconciliation tooling. Organizácia pridelí destructive-change ownera a similar-system audit.

Action item mapuje mechanismus na control, ownera, priority, due date, dependency a verification evidence:

```text
ARCH-219
mechanism: missing scope → wildcard destructive query
control: required tenant_scope + runtime fail-closed
owner: Settlement Platform
due: 2026-08-05
verification: missing, empty a wrong tenant rejected
```

`Buďte opatrnejší` ani `napísať dokumentáciu` samostatne executable failure path neodstraňujú.

## 10. RCA acceptance a mechanism closure

Positive acceptance musí preukázať exact subject, evidence-backed timeline, oddelený trigger/proximate/business mechanismus, causal taxonomy, competing-hypothesis verdicts a counterfactuals. Actions musia mapovať na mechanisms a mať production verification.

Forbidden paths zahŕňajú `human error` ako koncový verdict, jedinú root cause za každú cenu, causal claim bez source, action closed po merge-i, recurrence test iba na pôvodnom fixture a residual risk bez ownera.

```text
analysis:
outcome → evidence → causal graph → control portfolio

closure:
implemented → deployed → effective → recurrence test

forbidden:
trigger označený za root cause
blame namiesto mechanismu
ticket closure bez effective state
similar-system path ignorovaný
```

Mechanism closure nastane až keď negative a second-operation tests preukážu, že missing/empty/wrong scope je odmietnutý aj na podobných destructive workflows. Closed ticket nie je closed failure mechanismus.

## 11. Troubleshooting slabej RCA

Ak incident recurs alebo actions nefungujú, porovnaj exact prior RCA generation, pôvodný causal graph, action closure evidence a effective scope. Urči, či recurrence použila rovnaký mechanismus, alternate path alebo podobný symptom.

```text
recurrence
→ prior subject a causal graph
→ actions a verification evidence
→ configured vs effective control
→ same vs alternate mechanism
→ missing escape/detection/recovery branch
→ organizational ownership/incentive gap
→ re-open analysis a portfolio
```

RCA sa nemá „obhájiť“ tým, že bola už publikovaná. Nová evidence môže vytvoriť revision s auditovaným correction recordom.

## 12. Anti-patterny

RCA anti-patterny vytvárajú jednoduchý príbeh na úkor causal completeness a testovateľnej nápravy.

- **Posledná zmena je root cause —** change môže byť trigger; barriers mali zamedziť unsafe outcome alebo blast radiusu.
- **Human error —** opisuje action bez vysvetlenia, prečo bola možná, rozumná alebo neobmedzená.
- **Jedna root cause za každú cenu —** skryje escape, detection, amplification a recovery paths.
- **Five Whys ako rituál —** lineárny chain nahradí distributed causal graph a môže skončiť pri abstraktnej osobe.
- **Timeline iba z chatu —** chat je neúplný a časovo skreslený; potrebuje system evidence a clock authority.
- **Action item je training —** training môže pomôcť, ale bez executable guardrailu sa mechanismus vráti.
- **RCA bez follow-up verification —** dokument vysvetlí minulosť, no production behavior zostane rovnaký.

## 13. Kontrolné otázky

1. Čo tvorí exact RCA subject a outcome?
2. Ako sa trigger, proximate mechanismus a root cause líšia?
3. Prečo treba rozlišovať technical, systemic, escape a amplification causes?
4. Ako causal graph zlepšuje lineárny príbeh?
5. Čo testuje counterfactual reasoning?
6. Aké sú limity Five Whys?
7. Kedy je causal depth príliš plytká alebo abstraktná?
8. Ako zapísať human action blameless, ale presne?
9. Prečo replication a backup incident nezastavili?
10. Čo robí corrective action overiteľnou?
11. Ako sa mechanism closure líši od ticket closure?
12. Ktoré analysis, closure a forbidden paths patria do acceptance?

## Glossary impact

Relevantné pojmy: RCA subject, proximate mechanismus, technical/systemic root cause, escape/detection/amplification/recovery cause, causal graph, counterfactual test, actionable root-cause depth, corrective-action portfolio, mechanism closure a RCA acceptance contract.

## Primárne zdroje

- [Google SRE — Postmortem Culture: Learning from Failure](https://sre.google/sre-book/postmortem-culture/)
- [Google SRE Workbook — Postmortem Culture](https://sre.google/workbook/postmortem-culture/)
- [Google SRE — Effective Troubleshooting](https://sre.google/sre-book/effective-troubleshooting/)
- [NIST SP 800-61 Rev. 3](https://csrc.nist.gov/pubs/sp/800/61/r3/final)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Runbooks a playbooks](runbooks-and-playbooks.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Blameless postmortems →](blameless-postmortems.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
