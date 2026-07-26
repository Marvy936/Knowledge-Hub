# Quality gates a approvals

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

Quality gate je rozhodovací mechanizmus, ktorý vyhodnotí konkrétny subject proti úplnému evidence manifestu a versionovanej policy. Approval je explicitné rozhodnutie oprávnenej authority nad rizikom alebo kontextom, ktorý nemožno spoľahlivo zredukovať na deterministické pravidlo.

```text
immutable subject
+ expected evidence manifest
+ applicability a freshness graph
+ versioned policy
+ automatic alebo human authority
→ allow / deny / review / incomplete / expired / inconclusive / waived
→ audit, remediation alebo ďalší delivery transition
```

## 1. Cieľ kapitoly

Nosný model kapitoly je gate-decision lifecycle:

```text
rozhodovací subject
→ expected evidence a completion contract
→ subject/evidence identity verification
→ policy applicability a freshness
→ automated evaluation
→ human decision packet podľa potreby
→ explicitný verdict
→ exception, expiry a revocation lifecycle
→ audit a defect-escape learning
```

Cieľom nie je pridať čo najviac červených a zelených kontrol. Cieľom je vytvoriť dôveryhodné rozhodnutie, ktoré vie odlíšiť reálne porušenie od chýbajúceho dôkazu, nástrojového zlyhania, expirovaného kontextu alebo legitímne prijatého rizika.

## 2. Nosný scenár: Atlas Orders 3.10.1

Atlas chce promovať release tuple:

```text
subject Q = {
  release manifest R,
  rendered config K,
  target environment E3,
  infrastructure revision I,
  rollout strategy canary,
  migration state snapshot D
}
```

Expected evidence:

```text
build provenance P
unit/component/contract reports T
SCA/image/security reports S
migration compatibility M
staging deployment/smoke O
production precheck H
rollback/roll-forward plan C
```

Policy musí rozhodnúť, či Q môže vstúpiť do production canary. Nestačí vedieť, že pipeline je zelená; treba vedieť, či všetky požadované dôkazy existujú, patria Q, sú čerstvé a spĺňajú príslušné pravidlá.

## 3. Check verzus gate

Check vytvára signál. Gate z neho robí rozhodnutie.

```text
scanner
→ signed report S pre digest R

policy
→ reachable critical finding bez platnej výnimky = deny
→ missing alebo invalid S = incomplete, nie allow
```

Jeden report môže vstupovať do viacerých rozhodnutí: artifact eligibility, environment promotion aj compliance audit. Jeho význam sa mení podľa subjectu, scope-u a policy.

## 4. Subject identity

Gate subject musí byť immutable alebo jednoznačne versionovaný:

- synthetic merge candidate SHA;
- artifact alebo release manifest digest;
- rendered configuration digest;
- infrastructure/plan digest;
- environment revision;
- migration plan/state snapshot;
- rollout cohort a strategy revision.

Branch, tag alias alebo pipeline name nie sú dostatočná identity. Atlas gate viaže verdict na tuple Q, nie na názov `release-3.10.1`.

## 5. Evidence manifest a completeness

Evidence manifest deklaruje, čo musí existovať pred rozhodnutím:

```text
subject Q
required:
- P: build provenance, complete
- T1..T4: test reports, complete
- S1: image scan, complete
- S2: signature verification, complete
- M1: migration compatibility, complete
- O1: staging smoke, complete
optional/advisory:
- performance trend A1
```

Každá evidence položka obsahuje subject identity, producer/tool version, workflow/run, timestamps, completion state, result, integrity a exception reference.

Fan-in najprv dokazuje úplnosť a až potom interpretuje findings. Chýbajúci shard alebo report nie je nulový finding.

## 6. Policy applicability

Nie každé pravidlo platí pre každú zmenu. Atlas policy odvodí applicability z manifestu, diff classification a targetu:

```text
migration bundle prítomný
→ migration compatibility gate required

production IAM alebo network change
→ environment/security owner review required

dokumentačná zmena bez artifactu
→ production deployment rules not applicable
```

`Skipped` je explicitný policy verdict s pravidlom a dôvodom. Tichá absencia jobu nevytvára dôkaz, že kontrola nebola potrebná.

## 7. Freshness graph

Evidence platnosť invalidujú dependency zmeny:

```text
candidate SHA change
→ build/test/review stale

release manifest digest change
→ scan/signature/deployment evidence stale

rendered config alebo infrastructure revision change
→ environment verification a approval stale

policy version change
→ verdict musí byť reevaluated

target environment drift alebo incident
→ health/approval snapshot stale
```

Niektoré výsledky expirujú aj časom: vulnerability scan, environment health, canary signal, deployment window a temporary exception.

## 8. Verdict taxonomy

Atlas gate vracia:

- **allow** — complete, valid a fresh evidence spĺňa policy;
- **deny** — platná policy je porušená;
- **warn/advisory** — signal je viditeľný, ale neblokuje;
- **require review** — treba ľudský risk/context judgement;
- **incomplete** — povinná evidence nevznikla;
- **invalid evidence** — report nepatrí subjectu alebo nie je overiteľný;
- **expired** — evidence alebo approval už nie je platný;
- **tool/infrastructure error** — kontrola sa spoľahlivo nevykonala;
- **inconclusive** — vzorka alebo signál nestačí;
- **waived** — konkrétne porušenie má platnú scoped výnimku.

Mapovanie všetkého na pass/fail ničí diagnostiku a môže vytvoriť fail-open bez vedomého risk rozhodnutia.

## 9. Blocking a advisory controls

Blocking je vhodný, keď signal chráni významný risk, je presný, reprodukovateľný, akčný a stabilný. Advisory control má maturity lifecycle:

```text
pilot/baseline
→ merať precision a noise
→ tuning a ownership
→ blocking pre nový alebo critical scope
→ rozšírenie, ponechanie advisory alebo odstránenie
```

Permanentný advisory finding bez ownera a remediation je dekorácia.

## 10. Missing-data policy

Pri chýbajúcej evidence Atlas explicitne volí:

- **fail closed** pre signature, provenance, required tests a migration compatibility;
- **require review** pri emergency hotfixe alebo dočasne nedostupnom contextual signal-e;
- **fail open with degraded state** iba pri nepovinnom trendovom reporte, kde dostupnosť delivery prevyšuje riziko chýbajúceho signálu;
- **last known evidence** iba pri explicitnom scope-e, subject matchi a platnej freshness.

Tool outage nie je automaticky absence findings.

## 11. Policy composition

Production decision môže skladať:

```text
artifact eligibility
AND evidence completeness
AND security/compliance eligibility
AND environment readiness
AND shared-state compatibility
AND approval alebo automated risk authorization
```

Policy definuje precedence, required/optional inputs, conflict resolution a missing-data semantics. Nejasná `OR` kompozícia môže povoliť release preto, že jeden z dvoch rozdielnych scannerov bol zelený.

## 12. Baseline, ratcheting a legacy debt

Atlas legacy image má známe medium findings. Adoption policy:

```text
versioned baseline
+ block new critical findings
+ deny net worsening podľa scope-u
+ expiring remediation targets
+ pravidelné znižovanie baseline
```

Baseline nie je globálna waiver. Je versionovaná, reviewovaná, scoped a chránená pred automatickým prepisom aktuálnymi findings.

## 13. Approval je risk decision

Approval je legitímny pri:

- nevratnej alebo destructive data zmene;
- business timingu a externých koordináciách;
- risk acceptance;
- compliance/separation-of-duties požiadavke;
- protichodných alebo inconclusive signáloch;
- emergency trade-offe.

Človek nemá ručne overovať compile result, podpis alebo report completeness. Deterministický control patrí automation.

## 14. Decision packet

Atlas approver dostane:

```text
subject Q a diff summary
risk classification a blast radius
evidence manifest s freshness a verdictmi
findings, baseline a waivers
target environment/effective state
migration a data impact
rollout strategy a cohort
promote/abort criteria
rollback eligibility a roll-forward plan
requested decision a expiry
```

Approval bez packetu presúva hľadanie základných faktov na človeka a zvyšuje variability rozhodnutia.

## 15. Authority, separation of duties a quorum

Policy rozlišuje:

- autora zmeny;
- code ownera;
- security/database/platform ownera;
- environment ownera;
- business/risk ownera.

Conflict rules bránia autorovi byť jediným approverom pri high-risk zmene. Low-risk zmena s complete automated evidence môže byť automaticky povolená. Univerzálne dve approvals pre každý commit iba zväčšujú queue a diffusion of responsibility.

## 16. Approval freshness a revocation

Approval patrí presnému decision packetu. Invaliduje ho:

- nový candidate alebo artifact digest;
- zmena config/infra/migration planu;
- nový critical finding;
- environment drift alebo incident;
- zmena rollout strategy či blast radiusu;
- expiry change windowu.

Authority môže approval explicitne revoke-nuť. Manual job spustený po stale approval-e nesmie pokračovať.

## 17. Waiver a break-glass

Waiver povoľuje konkrétne porušenie konkrétnej rule:

```text
policy/rule ID
+ subject/environment scope
+ finding identity
+ risk owner
+ compensating control
+ remediation issue
+ expiry a revocation
```

Break-glass je incidentný privilege lifecycle:

```text
incident declared
→ strong authentication
→ scoped short-lived privilege
→ minimal action
→ real-time audit/alert
→ automatic revocation
→ retrospective a doplnenie preskočenej evidence
```

Ani jeden mechanizmus nemení failure na bežný pass.

## 18. Worked failure: missing security report bol interpretovaný ako green

Image scan job skončil timeoutom pred uploadom reportu. Aggregator spočítal findings z existujúcich JSON súborov:

```text
expected S1 report nevznikol
→ glob match našiel nula reportov
→ suma critical findings = 0
→ production gate allow
```

### Root cause

Gate nepoznal expected evidence manifest a zamieňal prázdny input za úspešne vykonanú kontrolu.

### Náprava

- manifest deklaruje required S1;
- fan-in overuje completion a subject digest pred findings;
- tool timeout je `tool_error`/`incomplete`;
- signature/security controls fail closed pre production;
- report uploader beží `always` a zachová execution metadata;
- gate metriky sledujú incomplete evidence rate.

## 19. Worked failure: approval zostal platný po zmene configu

Database owner schválil canary pre manifest R a config K1 s concurrency 20. Neskôr platform owner zmenil config na K2 s concurrency 120, ale manual production job stále zobrazoval starý approval:

```text
approval pre R + K1
→ config revision zmenená na K2
→ approval UI ostalo green
→ deployment R + K2 pokračoval
→ DB saturation
```

### Root cause

Approval bolo viazané na release label a environment alias, nie na celý subject tuple a freshness graph.

### Náprava

- decision packet identity je R + K + I + E + strategy;
- každá dependency zmena invaliduje approval;
- protected environment reevaluuje policy tesne pred mutation;
- manual trigger nemôže obísť stale-dismissal;
- approval audit zaznamenáva packet digest a expiry.

## 20. Runtime gates

Canary gate používa:

```text
release/cohort identity
+ control alebo baseline
+ minimum sample a observation window
+ technical/functional/business metrics
+ promote a abort thresholds
+ missing-data/inconclusive semantics
+ recovery action
```

Nulový traffic alebo chýbajúca telemetry nie sú úspešný canary. Runtime gate je ďalšia aplikácia rovnakého decision contractu.

## 21. Diagnostický postup

1. Identifikuj gate subject a policy version.
2. Načítaj expected evidence manifest.
3. Over subject identity, completion, integrity a tool status každého reportu.
4. Vyhodnoť applicability a explicitné skip reasons.
5. Skontroluj freshness dependency graph a expiry.
6. Rozlíš finding, incomplete, invalid, tool error a inconclusive.
7. Over fail-open/fail-closed a policy composition semantics.
8. Pri approval-e porovnaj decision packet digest, approver eligibility a conflict rules.
9. Skontroluj waiver/break-glass scope, expiry a remediation.
10. Zachovaj audit trail a oprav policy/control model pri escaped defecte.

## 22. Referenčné pravidlá

- Gate rozhoduje nad immutable subjectom, nie branch labelom.
- Check produkuje signal; gate aplikuje policy.
- Expected evidence manifest predchádza findings aggregation.
- Completeness a subject match sa overujú pred interpretáciou výsledku.
- Skipped, incomplete, tool error a inconclusive sú odlišné stavy.
- Freshness je dependency graph aj časové okno.
- Blocking control potrebuje presnosť, ownera a remediation.
- Fail-open je explicitné risk rozhodnutie.
- Approval dopĺňa, nie nahrádza deterministickú automation.
- Decision packet viaže risk, evidence, target a recovery.
- Approval má expiry, invalidation a revocation.
- Waiver a break-glass sú scoped a dočasné.
- Escaped defect mení policy, evidence manifest alebo control.

## 23. Časté omyly

### „Check prešiel, gate má prejsť“

Gate môže vyžadovať viac signálov, inú freshness alebo iný subject.

### „Nenašli sa findings“

Najprv treba dokázať, že kontrola kompletne prebehla.

### „Viac approvals znamená vyššiu bezpečnosť“

Bez kvalitného packetu a role clarity rastie iba queue time.

### „Manual job je approval“

Tlačidlo je trigger. Approval je autorizované risk rozhodnutie nad konkrétnym subjectom.

### „Waiver znamená pass“

Verdict zostáva waived risk s expiry a remediation.

### „Approval platí pre release name“

Platí iba pre nezmenený decision packet a target state.

## 24. Zhrnutie

Dôveryhodný Atlas gate je:

```text
immutable subject tuple
→ expected evidence manifest
→ completion, identity a freshness verification
→ versioned applicability/policy evaluation
→ automated alebo human authority
→ explicitný viacstavový verdict
→ scoped exception/revocation/remediation
→ audit a defect-escape learning
```

Quality gate nie je dashboard a approval nie je administratívny klik. Obe sú súčasťou jedného decision contractu, ktorý musí vedieť vysvetliť, čo hodnotil, z akých dôkazov a prečo povolil alebo zastavil ďalší transition.

## 25. Kontrolné otázky

1. Aký je rozdiel medzi checkom a gate-om?
2. Čo tvorí Atlas gate subject?
3. Prečo evidence manifest musí existovať pred agregáciou findings?
4. Ako sa líši incomplete, invalid a tool-error verdict?
5. Čo určuje applicability a skip semantics?
6. Ako freshness graph invaliduje evidence?
7. Kedy je blocking control primeraný?
8. Ako baseline a ratcheting riešia legacy debt?
9. Kedy má rozhodovať človek namiesto policy engine-u?
10. Čo musí obsahovať decision packet?
11. Ako separation of duties závisí od risku?
12. Prečo approval po config zmene expiroval?
13. Ako sa waiver líši od break-glass?
14. Prečo missing scan report vytvoril false green?

## Glossary impact

Relevantné pojmy: gate decision contract, gate subject, evidence manifest, evidence completeness, applicability, freshness graph, blocking gate, advisory gate, fail open, fail closed, verdict taxonomy, decision packet, approval authority, approval freshness, approval revocation, waiver, break-glass a runtime gate.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Environment a promotion](environment-and-promotion.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Pipeline as Code →](pipeline-as-code.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
