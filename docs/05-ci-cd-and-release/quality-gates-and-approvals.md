# Quality gates a approvals

Quality gate je rozhodovací bod, ktorý na základe explicitnej policy a dôkazov určí, či môže zmena pokračovať do ďalšej fázy delivery. Approval je ľudské alebo organizačné rozhodnutie. Obe vrstvy majú riadiť konkrétne riziko; nemajú byť dekoráciou ani administratívnym checkboxom.

## 1. Quality gate

Gate vyhodnocuje:

```text
artifact alebo change
+ evidence
+ policy
→ allow | deny | warn | require review
```

Príklady evidence:

- test results,
- static-analysis findings,
- code coverage delta,
- vulnerability findings,
- artifact signature a provenance,
- IaC policy result,
- deployment smoke,
- canary metrics,
- change-risk classification.

## 2. Gate vs. check

Check iba vytvorí signál. Gate tento signál použije na rozhodnutie o pokračovaní.

```text
SAST scan
→ check result

policy: critical reachable finding = block
→ quality gate
```

Nie každý check má byť blocking. Blocking policy musí zohľadniť kvalitu signálu, false-positive rate, závažnosť a dostupnú nápravu.

## 3. Blocking a advisory gate

### Blocking

Pipeline alebo promotion sa zastaví.

Vhodné pre:

- compilation failure,
- required tests,
- invalid artifact signature,
- porušenie kritickej security policy,
- nekompatibilnú databázovú migráciu,
- chýbajúcu povinnú evidence.

### Advisory

Pipeline pokračuje, ale finding zostáva viditeľný.

Vhodné pre:

- nový nástroj počas kalibrácie,
- nízku závažnosť,
- neistý heuristický signál,
- trendové metriky,
- postupné sprísňovanie policy.

Advisory result potrebuje ownera a lifecycle; inak sa stane ignorovaným šumom.

## 4. Deterministická policy

Gate má mať versionovanú a vysvetliteľnú policy:

```text
block when:
- unit tests fail
- new critical vulnerability is reachable
- artifact signature is missing
- diff coverage < 80 % on changed production code
```

Nejasné pravidlo typu „quality musí byť dostatočná“ nie je automatizovateľné ani auditovateľné.

## 5. Baseline a new-code policy

Legacy systém môže mať veľký existujúci dlh. Okamžitý absolútny threshold by zablokoval všetky zmeny.

Ratcheting model:

- nezhoršovať existujúci stav,
- blokovať nové kritické findings,
- vyžadovať coverage pre changed code,
- postupne znižovať baseline debt.

Baseline musí byť versionovaná a jej zmena reviewovaná.

## 6. Quality gate poradie

Lacné a rýchle gates majú bežať skôr:

```text
syntax/format
→ lint/type checks
→ unit tests
→ build
→ integration/contract
→ security/artifact checks
→ environment validation
→ production rollout gates
```

Cieľom je fast failure bez straty potrebnej fidelity.

## 7. Gate scope

Gate môže byť viazaný na:

- commit alebo merge request,
- branch,
- artifact digest,
- environment promotion,
- deployment,
- release cohort.

Release gate viazaný iba na branch status môže omylom schváliť iný artifact. Evidence sa má viazať na immutable identity.

## 8. Freshness evidence

Výsledok môže zastarať, keď sa zmení:

- commit,
- artifact,
- dependency lockfile,
- pipeline definition,
- environment config,
- policy version,
- target branch.

Approval a gate result musia mať freshness pravidlá. Nový commit typicky invaliduje predchádzajúce code review a test evidence.

## 9. Approval

Approval je explicitné rozhodnutie oprávnenej osoby alebo skupiny.

Legitímne účely:

- business timing,
- compliance alebo separation of duties,
- potvrdenie risk acceptance,
- koordinácia s externým partnerom,
- kontrola neautomatizovateľnej evidence,
- production change počas citlivého okna.

Approval nemá nahrádzať test, ktorý sa dá spoľahlivo automatizovať.

## 10. Evidence-based approval

Approver má dostať stručný decision packet:

- čo sa mení,
- artifact digest/version,
- risk classification,
- test/security results,
- deployment plan,
- rollback/roll-forward plan,
- known exceptions,
- target environment,
- čas a blast radius.

Approval bez relevantnej evidence je iba ceremónia.

## 11. Separation of duties

Pri citlivých zmenách môže policy vyžadovať, aby autor nebol jediným approverom.

Možnosti:

- code owner review,
- security approval,
- operations approval,
- business approval,
- two-person rule.

Separation of duties má znižovať riziko, nie vytvárať univerzálne fronty pre každú nízkorizikovú zmenu.

## 12. Risk-based approvals

Príklad policy:

```text
low risk + all automated gates pass
→ automatic promotion

medium risk
→ one environment owner approval

high risk / destructive migration
→ two approvals + change window
```

Risk classification môže zohľadniť:

- blast radius,
- customer impact,
- data mutation,
- privileged access,
- reversibility,
- novelty,
- incident history.

## 13. Protected branches a environments

Approval môže byť enforcement mechanizmom pre:

- merge do protected branch,
- použitie production secretu,
- deployment do protected environmentu,
- release tag/signing.

Policy sa má vynucovať platformou, nie iba textovým procesom.

## 14. Approval expiry

Approval má expirovať pri:

- novom commite,
- zmene artifact digestu,
- zmene deployment planu,
- významnej zmene environmentu,
- prekročení časového okna,
- novej kritickej security informácii.

Staré approval na nový obsah je neplatné.

## 15. Delegation a ownership

Approver group má mať:

- jasné členstvo,
- backup/on-call model,
- least privilege,
- audit zmien členstva,
- definovaný SLA pre rozhodnutie.

Osobný účet jedného človeka ako jediný production approver je availability risk.

## 16. Bypass a break-glass

Emergency bypass môže byť potrebný, ale musí byť:

- explicitný,
- silne autorizovaný,
- časovo obmedzený,
- auditovaný,
- sprevádzaný dôvodom,
- následne reviewovaný,
- doplnený chýbajúcimi kontrolami po stabilizácii.

Trvalý admin override používaný rutinne znamená, že gate design nefunguje.

## 17. Exceptions

Finding môže mať schválenú výnimku s:

- presným scope-om,
- ownerom,
- odôvodnením,
- compensating control,
- expiry,
- ticketom,
- policy version.

Výnimka bez expiry je permanentné oslabenie policy.

## 18. Multi-dimensional gates

Jeden threshold nemusí stačiť. Canary gate môže vyhodnotiť:

- error rate,
- latency,
- saturation,
- business conversion,
- support signals,
- log anomaly.

Decision logic musí definovať:

- baseline/control group,
- observation window,
- sample size,
- abort threshold,
- missing-data behavior.

## 19. Missing evidence

Chýbajúci report nie je automaticky success.

Fail-open model povoľuje pokračovanie pri nedostupnom gate systéme. Fail-closed blokuje.

Rozhodnutie závisí od risku:

- production signature verification: typicky fail closed,
- advisory trend dashboard: môže fail open s alertom.

## 20. Gate availability

Gate service môže byť dependency delivery systému. Potrebuje:

- timeout,
- retry pre transient failure,
- degraded mode policy,
- observability,
- ownera,
- audit log.

Nedefinovaný timeout môže zastaviť všetky releases.

## 21. Manual job vs. approval

Manual job znamená, že človek spustí krok. Approval znamená, že človek autorizuje rozhodnutie. Nie sú totožné.

Manuálny deployment button bez identity, evidence a policy nie je kvalitný approval control.

## 22. Gate output

Dobrý failure output odpovie:

- ktorý gate zlyhal,
- ktorá policy rule,
- na akej evidence,
- aký artifact/change bol hodnotený,
- kto je owner,
- ako reprodukovať alebo opraviť problém,
- či existuje exception process.

Neužitočný result `quality gate failed` predlžuje lead time.

## 23. Audit trail

Uchovaj:

- policy version,
- evidence IDs,
- result,
- approver identity,
- timestamp,
- comments,
- exception/bypass,
- artifact digest,
- target environment.

Audit trail musí byť chránený pred dodatočnou manipuláciou.

## 24. Metrics

Sleduj:

- gate failure rate podľa pravidla,
- false-positive/waiver rate,
- approval wait time,
- bypass frequency,
- expired exceptions,
- stale evidence incidents,
- lead time contribution,
- defects uniknuté cez zelený gate.

Cieľom nie je 100 % pass rate. Gate má zachytávať relevantný risk bez neprimeraného šumu.

## 25. Troubleshooting

### Gate blokuje všetky zmeny

Over:

- calibration a threshold,
- baseline,
- tool version,
- missing report behavior,
- scope changed-code vs. entire repository,
- false-positive trend.

### Approval sa po novom commite zachovalo

Skontroluj stale-approval dismissal policy a väzbu approvalu na commit/artifact identity.

### Deployment čaká, hoci approval existuje

Over required group, environment, approval count, expiry, branch protection a whether approver is eligible.

### Gate report patrí inému artifactu

Porovnaj digest, pipeline run a evidence metadata. Branch name alebo release label nestačí.

## 26. Časté omyly

### „Viac approvals znamená vyššiu bezpečnosť“

Bez kvalitnej evidence a jasného risku iba rastie queue time.

### „Manuálny gate je bezpečnejší než automatický“

Opakované deterministické kontroly sú typicky spoľahlivejšie automatizované.

### „Coverage threshold dokazuje kvalitu“

Coverage je iba jeden signal a neoveruje assertions ani business správanie.

### „Emergency bypass netreba spätne riešiť“

Bez review sa bypass stane skrytou normou.

## 27. Kontrolné otázky

1. Aký je rozdiel medzi checkom a quality gateom?
2. Kedy má byť gate blocking a kedy advisory?
3. Ako funguje ratcheting nad legacy baseline?
4. Prečo musí byť evidence naviazaná na artifact digest?
5. Aké udalosti invalidujú approval?
6. Kedy je ľudský approval legitímny?
7. Ako navrhneš risk-based approval policy?
8. Čo musí obsahovať break-glass proces?
9. Ako rozhodneš medzi fail-open a fail-closed?
10. Aké metriky odhalia, že gate vytvára viac šumu než hodnoty?

## Glossary impact

Relevantné pojmy: quality gate, blocking gate, advisory gate, ratcheting, baseline debt, evidence freshness, approval, separation of duties, risk-based approval, protected environment, break-glass, exception, fail open a fail closed.
