# Quality gates a approvals

Quality gate je automatizovaný alebo policy-driven rozhodovací bod, ktorý na základe konkrétneho subjectu, evidence a versionovanej policy určí, či môže zmena pokračovať. Approval je explicitné rozhodnutie oprávneného človeka alebo skupiny nad rizikom, ktoré nemožno alebo nemá zmysel plne automatizovať.

Obe vrstvy majú chrániť konkrétny failure mode. Gate bez presnej policy je iba dashboard. Approval bez kontextu je iba administratívny klik.

## 1. Mental model

Dôveryhodné rozhodnutie má štyri vstupy:

```text
subject
+ evidence manifest
+ policy version
+ decision authority
→ verdict
```

- **Subject —** commit, merge-result SHA, artifact digest, deployment plan, environment alebo release cohort.
- **Evidence manifest —** presný zoznam testov, scanov, attestations, reports a runtime signálov.
- **Policy —** pravidlá, thresholds, scope, freshness a missing-data semantics.
- **Authority —** automatický policy engine alebo oprávnený approver.

Verdict musí byť auditovateľný a viazaný na immutable identity subjectu.

## 2. Check verzus gate

Check vytvorí signál. Gate použije jeden alebo viac signálov na rozhodnutie.

```text
SAST scanner
→ findings report

policy:
reachable critical finding bez platnej výnimky = deny
→ security gate
```

Jeden check môže vstupovať do viacerých gates. Napríklad SBOM môže byť použitý pri build promotion, production deployment aj compliance audite.

## 3. Subject gate-u

Gate musí presne pomenovať, čo hodnotí:

- source commit,
- synthetic merge-result SHA,
- artifact digest,
- release manifest digest,
- infrastructure plan digest,
- rendered configuration digest,
- environment deployment revision,
- canary cohort,
- database migration plan.

Branch name alebo pipeline label je slabá identity. Môže sa zmeniť alebo ukazovať na iný obsah.

## 4. Evidence manifest

Evidence manifest je zoznam požadovaných dôkazov pre jeden subject.

Príklad:

```text
subject: image digest A
required evidence:
- build provenance P1
- unit report U1
- contract report C1
- SCA report S1
- image signature G1
- staging smoke D1
```

Manifest má zachovať:

- evidence ID a typ,
- subject digest/SHA,
- producer tool a version,
- workflow/run identity,
- completion status,
- timestamp a expiry,
- result summary,
- integrity/signature,
- exception reference.

Bez manifestu môže fan-in gate omylom skombinovať reporty z rôznych artifacts alebo prehliadnuť chýbajúci shard.

## 5. Verdict taxonomy

Binárny `pass/fail` model je často nedostatočný. Gate má podľa potreby rozlišovať:

- **Allow —** všetky povinné podmienky sú splnené.
- **Deny —** platná policy je porušená.
- **Warn/advisory —** finding je viditeľný, ale neblokuje.
- **Require review —** automatika nemá dostatočný kontext.
- **Incomplete —** chýba povinná evidence alebo shard.
- **Invalid evidence —** report nepatrí subjectu, je poškodený alebo neoveriteľný.
- **Expired —** evidence alebo approval prekročili freshness window.
- **Tool/infrastructure error —** kontrola sa nevykonala spoľahlivo.
- **Inconclusive —** signál nestačí na bezpečné rozhodnutie.
- **Waived —** porušenie bolo dočasne prijaté platnou výnimkou.

`Tool error`, `incomplete` a `inconclusive` nesmú byť ticho mapované na pass.

## 6. Blocking gate

Blocking gate zastaví merge, promotion, deployment alebo release.

Je vhodný, keď:

- chráni významné a explicitné riziko,
- signál má vysokú presnosť,
- výsledok je reprodukovateľný,
- remediation je jasná,
- tool a evidence pipeline sú stabilné,
- runtime je primeraný rozhodovaciemu bodu,
- exception proces je definovaný.

Príklady:

- compilation failure,
- required test failure,
- neplatná artifact signature,
- chýbajúca provenance,
- kritická nekompatibilná migration,
- high-confidence secret exposure,
- zakázaný production network exposure,
- chýbajúci povinný report.

## 7. Advisory gate

Advisory gate reportuje riziko bez blokovania.

Vhodné použitie:

- nový nástroj počas kalibrácie,
- trendová metrika,
- heuristický signál s vyšším false-positive rate,
- legacy baseline rollout,
- odporúčanie s ľudským posúdením,
- nízka závažnosť.

Advisory gate potrebuje:

- ownera,
- definovaný scope,
- dashboard alebo issue lifecycle,
- cieľový stav,
- rozhodnutie, či sa stane blocking, ostane advisory alebo sa odstráni.

Inak sa zmení na trvalý šum.

## 8. Policy ako versionovaný kontrakt

Policy musí byť explicitná, versionovaná a vysvetliteľná.

Príklad:

```text
block production promotion when:
- artifact signature missing or invalid
- required test evidence incomplete
- new reachable critical vulnerability exists
- migration compatibility result = deny
- approval expired
```

Policy version je súčasť verdictu. Pri zmene pravidla musí byť možné vysvetliť, prečo ten istý artifact prešiel včera a dnes nie.

## 9. Policy composition

Komplexný gate môže skladať viac sub-policies:

```text
build eligibility
AND security eligibility
AND compliance eligibility
AND environment readiness
AND release approval
```

Pri composition definuj:

- AND/OR semantics,
- required a optional evidence,
- precedence pravidiel,
- conflict resolution,
- fail-open/fail-closed behavior,
- override scope,
- aggregation report.

Nejasná OR policy môže povoliť release iba preto, že jeden z viacerých scannerov bol zelený.

## 10. Scope a applicability

Nie každé pravidlo platí pre každý subject.

Príklady:

- mobile signing gate sa nevzťahuje na backend image,
- database compatibility gate sa spustí iba pri schema/migration zmene,
- production IAM approval sa nevzťahuje na dokumentáciu,
- performance gate môže byť povinný pre critical path alebo runtime zmenu.

Applicability musí byť explicitná a auditovateľná. `Skipped` má obsahovať dôvod a policy rule, nie prázdny stav.

## 11. Baseline a ratcheting

Legacy systém môže mať existujúci dlh. Bezpečný adoption model:

```text
existujúci baseline
+ blokovanie nových kritických porušení
+ zákaz zhoršenia
+ postupné znižovanie debt
```

Baseline musí byť:

- versionovaná,
- viazaná na scope,
- reviewovaná,
- merateľne znižovaná,
- chránená pred automatickým prepisom,
- odlíšená od jednotlivých waivers.

Ratcheting nie je povolenie debt navždy. Je to riadený prechod na prísnejšiu policy.

## 12. Evidence completeness

Gate musí vedieť, ktoré dôkazy očakáva.

Príklady neúplnosti:

- jeden test shard chýba,
- report upload zlyhal,
- scan preskočil časť image layers,
- coverage report obsahuje iba unit tests namiesto aggregate scope,
- policy engine nedostal rendered plan,
- canary nemá dostatok samples.

„Nenašli sme finding“ nie je rovnaké ako „kontrola kompletne prebehla“.

## 13. Evidence freshness graph

Freshness sa neviaže iba na čas. Evidence invalidujú zmeny vstupov.

Príklady dependencies:

```text
source commit change
→ invaliduje build/test/code-review evidence

artifact digest change
→ invaliduje scan/signature/deployment evidence

config revision change
→ invaliduje environment verification a approval

policy version change
→ môže vyžadovať nové vyhodnotenie

target branch change
→ invaliduje merge-result checks
```

Gate má poznať dependency graph a odmietnuť stale result.

## 14. Časová freshness

Niektoré evidence expirujú aj bez zmeny subjectu:

- vulnerability scan po aktualizácii threat database,
- environment health,
- canary metrics,
- business/calendar approval,
- temporary exception,
- certificate validity check,
- change window.

Freshness window má byť policy parameter podľa rizika.

## 15. Missing evidence a fail-open/fail-closed

Pri chýbajúcej evidence alebo gate outage musí policy rozhodnúť:

- **Fail closed —** pokračovanie sa blokuje.
- **Fail open —** pokračovanie je povolené s viditeľným degraded stavom.
- **Require review —** človek posúdi kontext.
- **Use last known evidence —** iba ak je to explicitne povolené a stále čerstvé.

Príklady:

- artifact signature verification pre production: typicky fail closed;
- advisory trend dashboard: môže fail open;
- critical incident hotfix: require review alebo break-glass s následnou kontrolou.

## 16. Tool a infrastructure failure

Scanner, runner, registry alebo policy service sú dependencies delivery systému.

Gate musí rozlíšiť:

- finding,
- deterministic test failure,
- timeout,
- rate limit,
- unavailable backend,
- parser/report error,
- authentication failure,
- corrupt evidence.

Automatický retry je vhodný iba pre identifikované transient failures. Opakovať deterministic finding alebo flaky test dovtedy, kým prejde, ničí dôveryhodnosť gate-u.

## 17. Gate placement

Kontrola má byť umiestnená do najskoršieho bodu s dostatočnou fidelity.

```text
editor/local
→ syntax, format, targeted lint

pull request
→ build, tests, static, contracts, diff policy

merge queue
→ integration candidate proti aktuálnemu main

artifact promotion
→ signature, provenance, scans, compatibility

environment deployment
→ plan, config, protected policy

progressive rollout
→ runtime SLI, canary a business guardrails
```

Rovnaký risk sa nemá zbytočne kontrolovať päťkrát rovnakým spôsobom. Neskorší gate má pridať fidelity alebo nový kontext.

## 18. Approval

Approval je explicitné rozhodnutie oprávnenej osoby alebo skupiny. Je legitímny, keď treba posúdiť:

- business timing,
- neautomatizovateľný kontext,
- risk acceptance,
- compliance/separation of duties,
- externú koordináciu,
- destructive alebo nevratnú zmenu,
- nejednoznačný runtime signal,
- emergency trade-off.

Approval nemá nahrádzať compile, unit tests alebo deterministickú policy.

## 19. Decision packet

Approver má dostať kompaktný, ale úplný decision packet:

- subject identity a digest,
- source/change summary,
- target environment a release cohort,
- risk classification,
- povinné evidence a ich freshness,
- findings a platné waivers,
- deployment strategy,
- blast radius,
- rollback/roll-forward plan,
- data/schema impact,
- observation a abort criteria,
- change window,
- requested decision a expiry.

Approver nemá ručne hľadať základné informácie v desiatkach pipeline logov.

## 20. Approval verdict

Approval nemusí byť iba `approve/reject`.

Možnosti:

- approve,
- reject,
- request changes,
- approve with conditions,
- defer/pause,
- escalate to required specialist,
- accept risk via scoped waiver.

Podmienené approval musí mať strojovo alebo procesne overiteľné conditions. Voľný komentár „OK, ak sa nič nezmení“ nestačí.

## 21. Separation of duties

Pri citlivých zmenách môže policy vyžadovať nezávislosť rolí:

- autor zmeny,
- code owner,
- security owner,
- database/platform owner,
- environment owner,
- business/risk owner.

Kontroluj conflict-of-interest pravidlá:

- autor nemôže byť jediný approver,
- service account nesmie nahradiť ľudskú risk authority,
- skupinové členstvo je auditované,
- dočasná delegácia má expiráciu.

Separation of duties má byť risk-based. Univerzálne dve approvals pre dokumentačnú zmenu iba zvyšujú queue time.

## 22. Quorum a approval groups

Policy môže vyžadovať:

- jeden approval z konkrétnej skupiny,
- dva nezávislé approvals,
- kombináciu security + environment owner,
- approval majority/quorum,
- explicitný approver pre destructive action.

Definuj:

- eligible members,
- conflict rules,
- backup/on-call coverage,
- SLA,
- membership audit,
- behavior pri nedostupnosti skupiny.

## 23. Risk-based approvals

Príklad:

```text
low risk + complete automated evidence
→ automatic promotion

medium risk alebo širší blast radius
→ environment owner approval

high risk / irreversible data change
→ specialist + risk owner + controlled window
```

Risk classification môže zohľadniť:

- customer impact,
- data mutation,
- privileged access,
- reversibility,
- novelty,
- incident history,
- dependency criticality,
- test/evidence strength,
- release exposure.

Classification musí byť transparentná a chránená pred jednoduchým self-declaration gamingom.

## 24. Approval freshness a revocation

Approval je viazaný na decision packet. Invalidujú ho napríklad:

- nový commit alebo merge result,
- zmena artifact digestu,
- zmena config/infrastructure planu,
- nový critical finding,
- expirovaná evidence,
- zmena target environmentu,
- zmena rollout strategy alebo blast radiusu,
- incident alebo freeze,
- prekročenie časového okna.

Approver alebo policy authority musí vedieť approval aj explicitne revoke-nuť.

## 25. Manual job verzus approval

- **Manual job —** človek technicky spustí krok.
- **Approval —** človek autorizuje rozhodnutie.

Manuálne tlačidlo bez evidence, identity, expiry a policy nie je kvalitný approval. Ide iba o odložený trigger.

Ideálny model:

```text
approval rozhodne
→ automation vykoná deterministický deployment
```

Nie:

```text
approval rozhodne
→ človek ručne kopíruje príkazy z runbooku
```

## 26. Exceptions a waivers

Výnimka povoľuje konkrétne porušenie policy v presnom scope.

Musí obsahovať:

- rule/policy ID,
- subject a environment scope,
- finding identity,
- dôvod,
- risk ownera,
- compensating control,
- expiry,
- remediation issue,
- review/approval identity,
- creation a revocation timestamp.

Výnimka sa nesmie automaticky preniesť na nový artifact alebo širší environment, ak to policy výslovne nepovoľuje.

## 27. Break-glass a emergency override

Emergency override môže byť potrebný pri incidente, ale musí byť samostatný kontrolovaný lifecycle:

```text
emergency declared
→ silná autentizácia
→ scoped temporary privilege
→ reason + incident ID
→ minimal action
→ full audit
→ privilege revocation
→ retrospective review
→ doplnenie preskočenej evidence
```

Ochrany:

- two-person alebo incident-commander authorization podľa rizika,
- short-lived token,
- explicitný target/environment,
- zákaz univerzálneho admin bypassu,
- real-time alerting,
- povinné post-event review,
- automatická expirácia.

Rutinné používanie break-glass znamená, že normálny gate alebo delivery path je nefunkčný.

## 28. Multi-dimensional runtime gates

Canary alebo progressive gate môže kombinovať:

- error rate delta,
- p95/p99 latency,
- saturation,
- restart rate,
- dependency errors,
- business completion,
- support signal,
- data integrity.

Decision contract potrebuje:

- control group alebo baseline,
- sample-size minimum,
- observation window,
- signal latency,
- promotion threshold,
- abort threshold,
- missing-data behavior,
- inconclusive state,
- rollback/roll-forward akciu.

## 29. Human judgement boundary

Ľudský approval je vhodný pre kontext, hodnoty a trade-offy. Nie je vhodný pre opakovanú mechanickú kontrolu.

Automatizuj:

- podpis verification,
- policy thresholds,
- test result completeness,
- environment lock,
- identity a authorization,
- artifact/config matching.

Človek posudzuje:

- business timing,
- risk acceptance,
- nevratnosť,
- nejasné alebo protichodné signály,
- externú koordináciu,
- incident trade-off.

## 30. Gate output a diagnosability

Dobrý verdict odpovie:

- ktorý gate a policy version rozhodovali,
- aký subject bol hodnotený,
- ktoré evidence vstúpili,
- ktoré pravidlo zlyhalo,
- či ide o finding, missing evidence alebo tool error,
- aký je severity/risk,
- kto je owner,
- ako reprodukovať alebo opraviť problém,
- či existuje waiver alebo escalation proces.

Text `quality gate failed` je nedostatočný.

## 31. Audit trail

Uchovaj:

- subject identity,
- evidence manifest,
- policy version,
- verdict a rule details,
- automated decision identity,
- approver identity a eligibility,
- timestamps,
- comments a conditions,
- waiver/bypass references,
- revocation,
- target environment,
- deployment/release relation.

Audit trail musí byť chránený pred dodatočnou manipuláciou a dostupný počas požadovanej retention doby.

## 32. Gate service availability

Gate engine je kritická delivery dependency. Potrebuje:

- health a SLO,
- timeouty,
- retry pre transient failures,
- capacity a queue monitoring,
- degraded-mode policy,
- versioned rollout,
- audit log,
- disaster recovery,
- ownera a runbook.

Nedefinovaný gate outage môže zastaviť všetky releases alebo nebezpečne otvoriť fail-open cestu.

## 33. Metriky gate programu

Sleduj:

- gate failure rate podľa rule a failure class,
- finding verzus tool-error pomer,
- false-positive a waiver rate,
- time to remediation,
- approval wait time,
- stale/expired approval incidents,
- bypass a break-glass frequency,
- expired exception backlog,
- lead-time contribution,
- evidence incomplete rate,
- escaped defects cez zelený gate,
- percent automated low-risk promotions,
- approver load a availability.

Cieľ nie je 100 % pass rate. Cieľ je relevantný risk detection s prijateľným noise a lead time.

## 34. Diagnostický postup

### Gate blokuje takmer všetko

Over policy scope, baseline, threshold, analyzer version, changed-code mapping, false-positive trend, missing-data behavior a tool health.

### Gate je zelený, ale evidence chýba

Skontroluj manifest completeness, shard aggregation, optional/required classification a fail-open policy.

### Approval ostalo po novom commite

Skontroluj väzbu approvalu na SHA/digest, stale-dismissal event a dependency graph freshness.

### Deployment čaká napriek approvalu

Over eligible group, quorum, approval expiry, environment, target digest, change window, lock a protected policy.

### Report patrí inému artifactu

Porovnaj subject digest, evidence metadata, pipeline run a provenance. Branch label nestačí.

### Break-glass sa používa často

Analyzuj normálny lead time, false-positive gates, unavailable approvers a incident classification. Oprav štandardný path.

## 35. Typické anti-patterny

### Viac approvals automaticky znamená vyššiu bezpečnosť

Bez kvalitného decision packetu iba rastie queue time a diffusion of responsibility.

### Manuálny gate je automaticky bezpečnejší

Deterministické opakované kontroly bývajú spoľahlivejšie automatizované.

### Chýbajúci report znamená žiadny finding

Kontrola sa možno vôbec nevykonala.

### Approval platí pre branch navždy

Nové bytes, config alebo environment state potrebujú nové rozhodnutie.

### Výnimka bez expiry

Dočasné oslabenie sa stane trvalou policy.

### Break-glass bez retrospective

Emergency bypass sa mení na skrytý normálny proces.

### Coverage threshold ako jediný quality gate

Coverage neoveruje assertions, requirements ani runtime behavior.

### Jeden globálny approver

Vytvára availability risk a slabú separation of duties.

### Tool failure mapovaný na success

Delivery pokračuje bez dôkazu, ktorý policy považuje za povinný.

## 36. Praktický checklist

Pred zavedením gate-u alebo approvalu over:

- subject má immutable identity,
- required evidence je v manifeste,
- evidence patrí subjectu a je kompletná,
- policy je versionovaná a vysvetliteľná,
- applicability a skip semantics sú explicitné,
- verdict taxonomy rozlišuje incomplete/tool error/inconclusive,
- blocking režim má primeranú presnosť,
- baseline a ratcheting majú ownera,
- freshness graph invaliduje stale výsledky,
- fail-open/fail-closed policy je vedomá,
- decision packet obsahuje risk a recovery kontext,
- approver eligibility a conflict rules sú vynútené,
- approval má expiry a revocation,
- waivery sú scoped a expirovateľné,
- break-glass je krátkodobý a auditovaný,
- gate output je akčný,
- audit trail je immutable,
- escaped defects a false decisions sa merajú.

## 37. Kontrolné otázky

1. Aký je rozdiel medzi checkom a gate-om?
2. Čo je subject gate-u a prečo branch name nestačí?
3. Načo slúži evidence manifest?
4. Ktoré verdicty treba rozlišovať okrem allow/deny?
5. Kedy je gate vhodný ako blocking?
6. Ako sa advisory gate zabráni stať ignorovaným šumom?
7. Ako sa skladajú viaceré policies?
8. Prečo `skipped` potrebuje explicitný dôvod?
9. Ako baseline a ratcheting zavádzajú gate do legacy systému?
10. Čo znamená evidence completeness?
11. Ako freshness graph invaliduje výsledky?
12. Kedy sa používa fail-open a kedy fail-closed?
13. Aký je rozdiel medzi tool errorom a findingom?
14. Kedy je ľudský approval legitímny?
15. Čo musí obsahovať decision packet?
16. Ako separation of duties rieši conflict of interest?
17. Kedy approval expiroval alebo bol revoked?
18. Ako sa waiver líši od break-glass override-u?
19. Čo musí obsahovať canary runtime gate?
20. Ktoré metriky odhalia, že gate vytvára viac šumu než hodnoty?

## Summary

Quality gate premieňa konkrétny subject, úplný evidence manifest a versionovanú policy na auditovateľný verdict. Dôveryhodný model rozlišuje finding, incomplete evidence, tool failure, expired a inconclusive stav, vynucuje freshness a nevydáva stale alebo nesúvisiaci dôkaz za pass. Approval dopĺňa automatizáciu tam, kde treba business, risk alebo nevratný kontext. Musí mať decision packet, oprávneného approvera, conflict rules, expiry, revocation a audit trail. Waivery a break-glass sú dočasné, scoped a musia skončiť remediation closure.

## Glossary impact

Relevantné pojmy: quality gate, check, gate subject, evidence manifest, blocking gate, advisory gate, verdict taxonomy, baseline, ratcheting, evidence completeness, evidence freshness graph, fail open, fail closed, approval, decision packet, separation of duties, quorum, stale approval, revocation, waiver, break-glass a emergency override.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Environment a promotion](environment-and-promotion.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Pipeline as Code →](pipeline-as-code.md)
<!-- KNOWLEDGE-NAVIGATION:END -->