# Release management

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

Release management riadi immutable release unit od zostavenia candidate-u po používateľskú expozíciu, validation, support a ukončenie životného cyklu. Build vytvorí artifact. Deployment ho umiestni do runtime. Release sprístupní zmenu konkrétnym používateľom alebo business procesom.

```text
release scope
→ immutable candidate
→ complete a fresh evidence
→ eligibility decision
→ deployment
→ riadená exposure
→ technical, functional a business validation
→ recovery alebo promotion
→ support a lifecycle closure
```

## 1. Cieľ kapitoly

Nosný model kapitoly je release state machine:

```text
draft
→ candidate assembled
→ evidence collecting
→ ready alebo blocked
→ approved/policy-eligible
→ deploying
→ deployed
→ progressively exposed
→ validated
→ supported
→ closed, deprecated alebo end of life
```

Vedľajšie prechody zahŕňajú:

```text
superseded
aborted
rolled back
rolled forward
partially released
revoked
```

Každý prechod má subject identity, preconditions, evidence, ownera a audit record. Release nie je manuálny checklist nad pohyblivým targetom.

## 2. Nosný scenár: Atlas Orders 3.11.0

SemVer review z predchádzajúcej kapitoly schválil optional `riskDecision` capability ako Orders 3.11.0. Release unit obsahuje:

```text
orders-api digest D_api
orders-worker digest D_worker
expand migration bundle D_migration
release config revision C17
feature flag risk-decision = off
compatibility evidence E
```

Content-addressed manifest M2:

```yaml
release: 3.11.0-rc.2
components:
  orders-api: sha256:D_api
  orders-worker: sha256:D_worker
  migrations: sha256:D_migration
config_revision: C17
feature_flags:
  risk-decision: off
evidence: sha256:E
```

Release plan:

```text
1. nasadiť M2 na 100 % Orders instances s flagom off
2. overiť artifact, config, migration a old behavior
3. exponovať riskDecision internému ring-u 5 %
4. pozorovať minimálne 30 minút
5. rozšíriť na 25 % eligible users
6. overiť delayed async a business outcomes
7. rozšíriť na 100 %
8. uzavrieť release a odovzdať ho do support lifecycle
```

Deployment a exposure sú zámerne oddelené. Binary môže bežať všade, zatiaľ čo novú capability dostáva iba malá cohorta.

## 3. Build, deployment a release sú tri odlišné udalosti

```text
build
→ vytvorí immutable component artifacts a manifest

deployment
→ zmení runtime assignment artifactu a konfigurácie

release
→ zmení používateľskú alebo business expozíciu capability
```

Pri Atlas 3.11.0:

```text
M2 deployed: 100 % instances
riskDecision exposed: 5 % users
```

Deployment controller môže byť zelený, hoci feature flag zostáva vypnutý. Naopak config alebo flag môže exponovať behavior bez nového deploymentu. Release record musí zaznamenať obidve osi.

## 4. Release unit určuje subject rozhodnutia

Release unit je presný set, ktorý sa testuje, schvaľuje, nasadzuje a podporuje spolu.

Pre Orders 3.11.0 ju tvorí M2, nie iba `orders-api:3.11.0`.

Bez explicitnej release unit nie je možné určiť:

- ktoré component digests boli testované spolu;
- ktorá config revision patrí candidate-u;
- ktorú migration approval pokrýva;
- čo sa má nasadiť alebo vrátiť;
- čo je v release notes;
- ktoré kombinácie sú podporované.

Ak sa zmení API image, worker, migration alebo relevantná config, vzniká nový manifest a nový candidate subject.

## 5. Release record je autoritatívna história state machine

Atlas release record zachová:

```text
release ID a current state
manifest digest a component identities
source a pipeline provenance
change inventory a risk classification
evidence manifest a freshness
approvals, waivery a policy verdicts
deployment a exposure records
migration a backfill state
validation windows a outcomes
abort, rollback alebo roll-forward decisions
communication, support a EOL class
```

Dáta sa majú generovať z build, policy, deployment a observability systémov. Ručné kopírovanie digestov do ticketu vytvára drift medzi skutočným runtime state a deklarovaným release stavom.

## 6. Scope admission predchádza candidate assembly

Do 3.11.0 scope vstúpia iba zmeny, ktoré majú:

- integrovaný source candidate;
- immutable component artifact;
- ownera a risk classification;
- changelog alebo release-note fragment;
- contract a migration impact;
- required test evidence;
- vyriešené dependencies a blockers;
- rollout a recovery ownera.

„Takmer hotová“ zmena sa nepridá tesne pred cutoffom. Buď spĺňa admission contract, alebo prejde do ďalšieho release candidate-u.

Scope freeze znamená, že M2 už neprijíma ďalšie features. Mainline development môže pokračovať. Ak sa musí opraviť candidate, vznikne M3 a jeho delta invaliduje relevantnú evidence.

## 7. Candidate je immutable možný final release

Candidate lifecycle:

```text
assemble manifest M
→ over component a config compatibility
→ zbieraj evidence pre M
→ rozhodni eligibility M
→ final release alias smeruje na schválený M
```

Finalizácia 3.11.0 nerebuildne source. Mení release status alebo alias, nie bytes.

Candidate identity musí zostať stabilná počas testovania, approvalu aj rollout-u. Inak každý krok hodnotí iný subject.

## 8. Supersession je explicitná zmena subjectu

RC1 používal config C16. Component test odhalil, že default `risk_timeout_ms=0` vypína downstream call namiesto použitia safe defaultu. Tím vytvoril C17 a M2.

```text
M1 = D_api + D_worker + D_migration + C16
M2 = D_api + D_worker + D_migration + C17
M2 supersedes M1
```

Supersession record obsahuje:

- old a new manifest digest;
- presný delta scope;
- dôvod;
- ktoré evidence zostávajú použiteľné;
- ktoré evidence sa invalidujú;
- ownera decisionu.

Source-only SAST nad rovnakým commitom môže zostať fresh. Config precedence test, component test, rollout plan a approval nad M1 sa musia prepočítať pre M2.

## 9. Readiness je evidence packet nad konkrétnym manifestom

Readiness packet pre M2 obsahuje:

```text
artifact a manifest provenance
change inventory a compatibility decision
unit, component, contract a regression evidence
migration expand a old/new compatibility evidence
security a policy verdicts
capacity evidence pre risk dependency
rollout cohorts, windows a guardrails
rollback, roll-forward a flag-disable eligibility
observability, on-call a communication readiness
known risks a waivery
```

Checklist bez subject identity a report references nie je dôveryhodný. „Testy prešli“ musí znamenať konkrétne checks nad M2 alebo nad explicitne uvedenými component subjects.

## 10. Readiness má viac než dva stavy

Atlas rozlišuje:

- **Ready —** required evidence je complete, fresh a policy-eligible.
- **Ready with accepted risk —** explicitná waiver má ownera, compensating control a expiry.
- **Blocked —** známy finding alebo nesplnená precondition.
- **Incomplete —** required evidence chýba alebo sa job nevytvoril.
- **Inconclusive —** evidence existuje, ale nerozhoduje hypotézu.
- **Expired —** candidate alebo evidence prekročila freshness window.
- **Superseded —** subject nahradil nový manifest.

Missing report nie je pass. Incomplete sa nesmie mapovať na green iba preto, že neexistuje červený result.

## 11. Risk classification určuje požadovanú evidence a rollout

Orders 3.11.0 mení:

- response contract additive spôsobom;
- nový downstream risk call;
- config a timeout behavior;
- expand database migration;
- async worker enrichment;
- feature exposure.

Riziko preto vyžaduje viac než basic smoke. Atlas pridá:

- old-client/new-server contract fixture;
- downstream timeout a circuit behavior test;
- duplicate-order invariant;
- migration compatibility;
- async backlog a reconciliation metric;
- cohort-level user journey a business guardrails.

Risk classification nemá slúžiť na pridanie approverov bez lepšej evidence. Má meniť test scope, rollout blast radius, observation window a recovery pripravenosť.

## 12. Approval je decision nad immutable subjectom

Approver vidí:

```text
manifest M2 a delta od current production
risk a reversibility
complete/fresh evidence
known findings a waivery
rollout a abort criteria
recovery eligibility
support a communication plan
```

Approval patrí M2. Exspiruje pri zmene:

- manifestu alebo component digestu;
- relevantnej config;
- migration state;
- policy alebo environment precondition;
- závažnej novej vulnerability;
- rollout subjectu alebo scope-u.

Approval bez immutable subjectu je ceremoniálny súhlas s nejasnou zmenou.

## 13. Cadence riadi vstup ready candidates, nie quality bar

Atlas môže používať daily release train:

```text
candidate ready pred 14:00
→ vstúpi do dnešného trainu
candidate incomplete o 14:00
→ automaticky čaká na ďalší train
```

Cutoff nemení required evidence. Zmena sa nestane menej rizikovou iba preto, že by inak zmeškala window.

On-demand, fixed cadence aj continuous release sú legitímne. Voľba závisí od recovery capability, customer expectations, regulácie a dependency coordination. Veľké batchovanie zvyšuje blast radius a root-cause ambiguity.

## 14. Multi-component compatibility sa overuje na úrovni setu

Jednotlivé componenty môžu byť samostatne validné a spolu nekompatibilné:

```text
new API + old worker
→ worker nerozumie enrichment eventu

new config + old API
→ old process odmietne neznámy required field

contract migration + old pods
→ staré writes používajú odstránený column
```

M2 compatibility matrix určuje podporované kombinácie počas rollout-u:

```text
old API / old worker / expanded schema
new API / old worker / expanded schema
new API / new worker / expanded schema
```

Contract schema removal nie je eligible, kým telemetry nepotvrdí, že old writers a readers zmizli.

## 15. Databázová zmena je release lifecycle shared state-u

Orders používa expand-first migration:

```text
expand schema
→ nasadiť old/new compatible API a worker
→ zapnúť dual-compatible writes
→ backfill enrichment state
→ reconcile counts a invariants
→ exponovať nový behavior
→ odstrániť old consumers
→ contract schema v neskoršom release
```

Release record zachová:

- migration IDs a applied stav;
- lock a runtime assumptions;
- backfill checkpoint;
- old/new reader-writer compatibility;
- integrity a reconciliation evidence;
- rollback limitations;
- podmienku pre budúci contract krok.

Application rollback nemusí vrátiť databázu. Recovery decision sa preto robí nad combined application a shared-state stavom.

## 16. Event a async state prežívajú deployment

Orders worker spracúva enrichment events. Počas rollout-u existujú:

- events vytvorené old API;
- events vytvorené new API;
- old a new workers;
- backlog z observation window;
- retry a dead-letter state.

Release validation kontroluje:

```text
schema compatibility
idempotency
backlog growth a drain
poison-message rate
replay behavior
reconciliation medzi orders a enrichment records
```

Ukončenie deploymentu neznamená, že všetky async side effects candidate-u sú dokončené.

## 17. Deployment najprv vytvorí nový runtime state

Pred exposure Atlas overí:

- manifest digest bežiacich instances;
- rendered config C17;
- migration applied state;
- desired a healthy replica count;
- routing a readiness;
- downstream connectivity;
- synthetics pre existujúci order journey;
- error, latency a saturation baseline.

Controller success dokazuje iba dokončenie svojho reconciliation contractu. User-level smoke a effective-state checks dokazujú, že deployment vytvoril použiteľný runtime.

## 18. Exposure je samostatný riadený prechod

Feature flag assignment je stabilný podľa user alebo tenant identity:

```text
internal ring 5 %
→ customer cohort 25 %
→ 100 % eligible population
```

Každý krok má:

- presný cohort a assignment rule;
- minimálnu observation window;
- technical, functional a business metrics;
- promotion a abort thresholds;
- maximálny blast radius;
- ownera decisionu.

Náhodné prehadzovanie používateľa medzi old a new behaviorom komplikuje diagnózu a môže porušiť workflow consistency.

## 19. Technical, functional a business oracles sa nesmú zamieňať

Atlas pri každom kroku sleduje:

### Technical oracle

```text
5xx, latency, saturation, downstream timeout, worker backlog
```

### Functional oracle

```text
CreateOrder journey completion
idempotency invariant
správne riskDecision pole
order detail čitateľný starými aj novými clients
```

### Business oracle

```text
order completion rate
rejection distribution
manual-review volume
support contact rate
```

Zelené CPU a 5xx metriky nepreukazujú, že `riskDecision` je správne priradené alebo že zákazníci dokončia objednávku.

## 20. Observation window vychádza z failure latency

Časové okno musí pokryť mechanizmus chyby:

- synchronous HTTP failure sa prejaví rýchlo;
- memory leak potrebuje dlhšie zaťaženie;
- async backlog sa môže prejaviť po desiatkach minút;
- settlement alebo reconciliation môže mať hodinové oneskorenie;
- support a business signal môže prísť neskôr.

Atlas nepromotuje z 25 na 100 % po piatich zelených requestoch, ak critical risk zahŕňa 30-minútový retry/backlog cyklus.

## 21. Abort zastaví rast blast radiusu

Abort znamená:

```text
nepokračovať do ďalšieho exposure kroku
```

Nemusí automaticky odstrániť deployment. Pri feature-gated release môže Atlas:

- vrátiť flag exposure na 0 %;
- ponechať M2 nasadený;
- zachovať evidence a cohort data;
- opraviť config alebo pripraviť M3;
- reconcile už vykonané side effects.

Abort action musí byť rýchlejšia než plný rollback, ak failure pochádza iba z novej capability.

## 22. Rollback, roll-forward a disable riešia iné stavy

Recovery decision pre Orders zohľadňuje:

```text
artifact a config compatibility
database expand/backfill stav
event backlog a side effects
client contract
čas na opravu
aktuálnu exposure
```

- **Disable** — vypne `risk-decision`, ak old behavior zostáva bezpečný.
- **Rollback** — vráti previous manifest, ak shared state a config sú kompatibilné.
- **Roll-forward** — nasadí M3 alebo opraví config, ak návrat by poškodil nové dáta.
- **Traffic shift** — presmeruje na healthy region alebo ring.
- **Write freeze** — chráni integritu pri corruption riziku.

„Vrátime starú verziu“ nie je recovery plan bez overených preconditions.

## 23. Recovery eligibility sa overuje pred releaseom

Previous release M_prev je rollback-eligible iba ak:

- component artifacts a manifest sú dostupné;
- trust policy ich povoľuje;
- old config a secret references existujú;
- expanded schema zostáva old-reader/writer compatible;
- old worker spracuje aktuálne events;
- deployment workflow pozná návrat;
- post-rollback synthetics a reconciliation sú pripravené.

Ak tieto podmienky neplatia, release plan musí preferovať roll-forward alebo feature disable.

## 24. Worked failure: RC1 evidence bola použitá pre RC2

M1 s config C16 prešiel component a load tests. Po oprave timeoutu vznikol M2 s C17, ale release ticket ponechal pôvodné approval a performance reporty:

```text
M1 tests → C16 nepoužíval downstream risk call
M2 runtime → C17 call aktivoval
→ production dostala nový latency a capacity path
→ evidence packet tvrdil, že load test prešiel
→ v skutočnosti testoval iný effective config subject
```

Pri 25 % exposure sa risk dependency saturovala a Orders latency prekročila SLO.

### Root cause

Release identity nezahŕňala config revision a supersession nemala dependency-aware evidence invalidation.

### Náprava

- manifest obsahuje rendered-config revision;
- evidence deklaruje subject vrstvy, ktoré pokrýva;
- config delta invaliduje component, capacity a rollout evidence;
- approval sa automaticky zruší pri zmene manifestu;
- candidate comparison ukazuje presný runtime delta set.

## 25. Worked failure: deployment bol zelený, ale 25 % cohorta vytvárala duplicate orders

M2 sa úspešne nasadil na všetky instances. Pri 5 % internom ring-u boli technické metriky zelené. Pri 25 % customer exposure však nový risk timeout spustil client retries:

```text
server dokončil prvý request po client timeout-e
→ client retry použil chybný idempotency header mapping
→ druhý logical order vznikol
→ 5xx ostali nízke
→ order count a support signal začali rásť
```

### Detection

Functional invariant `jeden logical order na idempotency key` a business metric duplicate-order reconciliation prekročili abort threshold. Infrastructure dashboard samotný incident neukázal.

### Recovery

```text
abort ďalšej promotion
→ risk-decision flag na 0 %
→ zachovať M2 deployment
→ zastaviť affected retry path
→ reconcile duplicate orders a side effects
→ pripraviť M3 s opravou header mappingu
→ zopakovať old/new client contract a cohort validation
```

### Learning

Release oracle sa rozšíril o idempotency invariant, delayed reconciliation a client-version cohort. Promotion criteria sa neobmedzujú na server health.

## 26. Communication je súčasť release contractu

Release ID `3.11.0` spája komunikáciu s konkrétnym manifestom a exposure stavom.

Podľa publika Atlas pripraví:

- user-visible capability a known limitations;
- API additive field a compatibility guidance;
- operator config a observability zmeny;
- support diagnostické signály;
- maintenance alebo degradation expectation;
- incident, abort alebo recovery updates.

Commit log nie je release note. Release notes kurátorsky vysvetľujú user a integration impact.

## 27. Emergency release je zrýchlený, nie neauditovaný flow

Ak sa duplicate-order chyba musí opraviť urgentne, Atlas stále zachová:

- incident a risk dôvod;
- review primeraný zmene;
- immutable artifact a provenance;
- targeted invariant a regression tests;
- minimálne policy/security gates;
- deployment a release record;
- recovery a on-call ownera;
- post-release validation;
- následné doplnenie obídenej evidence.

Break-glass má scope, expiry a post-incident review. Generický bypass všetkých controls nie je emergency process.

## 28. Hotfix sa musí forward-propagovať

Ak hotfix vznikne v podporovanej `release/3.11` line:

```text
fix v 3.11.1
→ samostatný artifact a manifest
→ targeted tests v support matrix
→ cherry-pick alebo ekvivalentná oprava v mainline
→ comparison check potvrdí forward propagation
```

Fix iba v production branch vytvorí regresiu pri ďalšom release z mainline.

## 29. Release nekončí po promotion na 100 %

Po full exposure Atlas čaká na relevantné delayed signals a potom release uzavrie:

- target deployment a exposure sú potvrdené;
- required validation windows prešli;
- async backlog a reconciliation sú stabilné;
- known issues majú ownerov;
- communication je dokončená;
- support class a EOL policy sú priradené;
- waivery a follow-up tasks majú termíny.

Closed znamená odovzdanie do normálnej prevádzky, nie koniec monitoringu.

## 30. Support, deprecation a end of life sú pokračovaním state machine

Atlas policy môže podporovať current a previous minor line:

```text
3.11.x → active support
3.10.x → security a critical fixes do dátumu X
3.9.x → end of life
```

Policy určuje:

- backport scope;
- vulnerability response;
- test matrix;
- artifact retention;
- documentation;
- client compatibility;
- migration a EOL komunikáciu.

EOL transition:

```text
announce
→ publish replacement a migration
→ measure usage
→ warning period
→ restrict new adoption
→ end support
→ remove endpoints/artifacts podľa retention a legal policy
```

## 31. Release revocation zachováva forenznú stopu

Pri kompromitovanom alebo kriticky chybnom M2 môže revocation:

- zastaviť exposure;
- zablokovať nové deployments;
- označiť component artifacts ako nepovolené;
- upozorniť aktívne environments;
- spustiť incident a recovery;
- zachovať bytes, evidence a timeline pre analýzu.

Revocation nie je automatická deletion.

## 32. Diagnostický postup

Keď release zlyhá alebo jeho stav nie je jasný:

1. identifikuj release ID, manifest digest a current state;
2. porovnaj candidate, approved, deployed a exposed identities;
3. potvrď component, config, infrastructure, migration a flag revisions;
4. urč presný affected cohort, region, client a časové okno;
5. over completeness a freshness evidence po poslednom supersession;
6. rozlíš deployment, exposure, compatibility, data, functional alebo telemetry failure;
7. zastav rast blast radiusu podľa abort policy;
8. zhodnoť disable, rollback, roll-forward, traffic shift a write-freeze eligibility;
9. over async backlog, database/event integrity a external side effects;
10. komunikuj release ID, impact a recovery state;
11. zachovaj timeline a decision records;
12. po recovery pridaj regression evidence a forward-propaguj fix.

## 33. Referenčné pravidlá

- Release unit je immutable set artifacts, config, migrations a contractov.
- Candidate change vytvára nový manifest a môže invalidovať evidence.
- Readiness patrí konkrétnemu manifestu a rozlišuje blocked, incomplete a inconclusive.
- Approval je risk decision, nie náhrada evidence.
- Cadence nemení quality bar.
- Deployment a user exposure sú samostatné osi.
- Promotion používa technical, functional aj business oracles.
- Observation window vychádza z failure latency.
- Abort zastavuje ďalší blast radius; nemusí znamenať rollback.
- Recovery rozhodnutie zahŕňa application, config, data, events a side effects.
- Hotfix má vlastnú immutable identity a forward-propagation.
- Release pokračuje support, deprecation, revocation a EOL lifecycle-om.

## 34. Časté omyly

### „Zelený deployment znamená úspešný release“

Deployment controller nepreukazuje user exposure ani functional a business outcome.

### „Approval platí, kým sa nezmení source commit“

Config, migration, policy alebo environment precondition môže zmeniť release subject bez source diffu.

### „Release train cutoff ospravedlňuje chýbajúci test“

Cutoff riadi cadence. Nesmie znižovať readiness policy.

### „100 % instances znamená 100 % používateľov“

Feature flags, routing a entitlement môžu držať inú exposure.

### „Rollback je vždy najrýchlejšia recovery“

Shared-state alebo event compatibility môže robiť rollback nebezpečnejším než disable alebo roll-forward.

### „Hotfix v release branch stačí“

Bez forward propagation sa chyba vráti z mainline.

## 35. Zhrnutie

Atlas release management lifecycle je:

```text
explicitný scope
→ immutable manifest M2
→ evidence a readiness nad M2
→ approval a policy eligibility
→ deployment s flagom off
→ stabilné cohort exposure 5 % → 25 % → 100 %
→ technical + functional + business validation
→ abort, disable, rollback alebo roll-forward podľa state-u
→ support, closure, deprecation a EOL
```

Release management spája identity, compatibility, evidence, rollout a recovery do jedného auditovateľného state machine. Až keď je release unit ready, treba zvoliť konkrétnu deployment stratégiu. Nasledujúca kapitola začína najjednoduchším modelom: recreate deploymentom s jedným exkluzívnym runtime slotom a explicitným downtime contractom.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Semantic Versioning](semantic-versioning.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Recreate deployment →](recreate-deployment.md)
<!-- KNOWLEDGE-NAVIGATION:END -->