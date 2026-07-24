# Release management

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

## 1. Definícia

Release management riadi cestu od overeného immutable candidate-u k používateľsky dostupnej a následne podporovanej zmene. Prepája scope, versioning, artifact identity, compatibility, approvals, deployment, exposure, komunikáciu, observability, recovery a support lifecycle.

Release nie je build ani deployment:

```text
build
→ vytvorenie immutable artifactu

deployment
→ umiestnenie artifactu do runtime environmentu

release
→ sprístupnenie capability používateľovi alebo business procesu
```

Tieto udalosti môžu nastať v rozdielnom čase. Kód môže byť nasadený za vypnutým feature flagom. Mobilný client môže byť publikovaný do store pred aktiváciou backend capability. Databázový expand krok môže prebehnúť mnoho deploymentov pred contract krokom.

## 2. Mental model: release ako stavový automat

Release nie je jednorazové kliknutie. Je to state machine nad explicitnou release unit:

```text
draft
→ candidate assembled
→ evidence collecting
→ ready
→ approved/policy-eligible
→ deploying
→ deployed
→ progressively released
→ validated
→ supported
→ deprecated
→ end of life
```

Vedľajšie stavy:

```text
blocked
superseded
aborted
rolled back
rolled forward
revoked
partially released
```

Každý prechod má subject identity, preconditions, ownera, evidence a audit record.

## 3. Release unit

Release unit je presne definovaný súbor artifacts, konfigurácií a zmien, ktoré sa schvaľujú a riadia ako jeden release.

Môže obsahovať:

- jeden application artifact,
- viac koordinovaných services,
- frontend, backend a mobile compatibility set,
- application artifacts a migrations,
- infrastructure/config bundle,
- model alebo data package,
- release manifest s viacerými component digestmi,
- feature-flag alebo traffic-policy transition.

Bez explicitnej release unit nie je jasné:

- čo je v scope,
- čo prešlo testami spolu,
- čo approval schvaľuje,
- čo sa má rollbacknúť,
- čo komunikovať používateľom,
- ktoré components tvoria podporovanú kombináciu.

## 4. Release identity

Release má mať immutable alebo content-addressed identity. Typicky obsahuje:

- release ID alebo logical version,
- release-manifest digest,
- component artifact digests,
- source commits,
- config a infrastructure revisions,
- migration bundle/state,
- pipeline definition a run identity.

Ľudsky čitateľné meno ako `2026.07.24.1` je užitočné, ale runtime a evidence sa majú viazať na immutable digests.

## 5. Release manifest

Pri multi-component release je release manifest zdroj pravdy pre presnú kombináciu:

```yaml
release: 2026.07.24.1
components:
  api: sha256:aaa...
  worker: sha256:bbb...
  frontend: sha256:ccc...
  migrations: sha256:ddd...
config_revision: 8d2a11f
infrastructure_revision: 719ab3c
contract_set: 12
```

Manifest musí byť:

- immutable alebo content-addressed,
- podpísaný podľa policy,
- prepojený na provenance componentov,
- validovaný proti compatibility pravidlám,
- použitý deploymentom aj rollbackom,
- zachovaný podľa support a audit lifecycle.

## 6. Release record

Release record je auditný a prevádzkový záznam celej state machine.

Obsahuje:

- release identity a current state,
- candidate a final manifest digest,
- component/source identities,
- zmenu od predchádzajúceho podporovaného release,
- evidence manifest,
- risk classification,
- approvals/policy decisions,
- waivery a known risks,
- rollout a exposure plan,
- target environments,
- deployment records,
- feature-flag transitions,
- validation výsledky,
- abort/rollback/roll-forward udalosti,
- ownerov a on-call kontakty,
- support/EOL stav,
- komunikáciu a incident links.

Release record má byť strojovo generovaný tam, kde dáta už existujú. Ručné prepisovanie digestov a výsledkov do ticketu vytvára drift.

## 7. Change inventory

Pred zostavením candidate-u vytvor inventory zmien:

- features a user-visible behavior,
- fixes,
- security changes,
- dependency a base-image updates,
- config/default changes,
- API/event/schema changes,
- database migrations,
- infrastructure/IAM/network changes,
- deprecations a removals,
- operational/runbook changes,
- known issues.

Inventory musí byť naviazané na konkrétny release scope. Git log je technický vstup, nie hotová kurátorská komunikácia.

## 8. Scope admission

Zmena vstúpi do release scope iba vtedy, keď spĺňa admission policy:

- je integrovaná do správnej mainline/release line,
- artifact alebo component candidate existuje,
- ownership a risk classification sú známe,
- required tests a reviews sú dostupné,
- compatibility a migration impact sú popísané,
- release notes fragment existuje,
- dependencies a blockers sú vyriešené.

Release train alebo cutoff má používať objektívny admission stav, nie neformálne „takmer hotové“ zmeny.

## 9. Release candidate

Release candidate je immutable release unit považovaná za možný final release.

```text
assemble manifest M
→ verify M
→ deploy/test M
→ approve M
→ final release alias na M
```

Candidate nesmie byť po testovaní rebuildnutý pod rovnakou identity. Ak sa zmení component, config alebo migration, vzniká nový candidate manifest a staré evidence sa musia znovu vyhodnotiť podľa freshness policy.

## 10. Candidate supersession

Nový candidate môže nahradiť starší:

```text
RC1 → finding
RC2 → supersedes RC1
```

Supersession record má uviesť:

- starý a nový manifest digest,
- presný delta scope,
- dôvod,
- ktoré evidence sa dá znovu použiť,
- ktoré checks sa invalidujú,
- či RC1 ostáva diagnosticky dostupný,
- kto prechod autorizoval.

„Opravili sme iba jeden súbor“ nie je dôvod na automatické zachovanie všetkých výsledkov. Freshness závisí od dependency a risk graphu.

## 11. Release readiness packet

Readiness je risk-based evidence packet nad konkrétnym candidate-om.

Typicky obsahuje:

- artifact/manifest identity a provenance,
- change inventory a risk classification,
- functional, contract a regression evidence,
- performance/capacity evidence podľa rizika,
- security, license a policy findings,
- compatibility matrix,
- database/event migration plan,
- rollout a abort criteria,
- rollback/roll-forward eligibility,
- observability a support readiness,
- known risks a waivery,
- communication plan.

Checklist bez immutable subjectu a evidence references nie je dôveryhodný readiness model.

## 12. Readiness verdicts

Readiness nemá byť iba `ready/not ready`. Užitočná taxonomy:

- **Ready —** complete a fresh evidence spĺňa policy.
- **Ready with accepted risk —** existuje explicitná, expirovateľná waiver a compensating control.
- **Blocked —** konkrétny finding alebo chýbajúca precondition.
- **Incomplete —** required evidence sa nevytvorila alebo chýba.
- **Inconclusive —** evidence existuje, ale nestačí na rozhodnutie.
- **Expired —** candidate alebo evidence prekročila freshness window.
- **Superseded —** novší candidate nahradil subject.

## 13. Release cadence

Cadence určuje, kedy sa ready changes môžu dostať k používateľom.

### On-demand

Release sa spustí po splnení conditions. Podporuje malé batches a krátky feedback.

### Fixed cadence

Denné, týždenné alebo mesačné windows. Uľahčujú koordináciu, ale môžu vytvárať batchovanie a čakací čas po readiness.

### Release train

Zmeny, ktoré sú ready pred cutoffom, nastúpia na train. Ostatné automaticky prejdú na ďalší train bez tlaku na zníženie quality bar-u.

### Continuous release

Malé zmeny sa priebežne uvoľňujú cez automatizovaný progressive flow.

Cadence má zodpovedať recovery capability, customer expectations, regulácii a dependency coordination.

## 14. Release train admission

Train potrebuje stabilné pravidlá:

- immutable candidate identity do cutoffu,
- complete readiness packet,
- žiadne unresolved required blockers,
- known dependency ordering,
- environment a support capacity,
- rollback/roll-forward readiness,
- communication scope.

Cutoff nemá meniť quality policy. Zmena, ktorá nestihla readiness, čaká na ďalší train.

## 15. Scope freeze verzus code freeze

Scope freeze znamená, že konkrétny release candidate už neprijíma nové features; iba explicitne schválené fixes vytvoria nový candidate.

Code freeze blokuje širší development alebo integráciu. Často zvyšuje divergence a batch size.

Preferovaný model:

- mainline pokračuje,
- release scope je immutable cez manifest,
- fixes sa aplikujú cielene,
- každá zmena vytvorí nový candidate,
- feature flags alebo branch by abstraction oddelia nehotovú capability.

Code freeze môže byť legitímny pri kritickej udalosti alebo regulačnom okne, ale nemá nahrádzať deployability a recovery.

## 16. Release branch

Release branch môže spravovať konkrétnu podporovanú line:

```text
release/2.8
```

Použitie:

- stabilizácia candidate-u,
- backport fixes,
- LTS/security support,
- oddelený cadence pre distribučný produkt.

Riziká:

- divergence od mainline,
- fix iba v jednej line,
- cherry-pick conflicts,
- duplicitná validácia,
- nejasný source of truth,
- dlhodobý freeze.

Release branch potrebuje ownera, support/EOL termín, forward-propagation policy a automatizované comparison checks.

## 17. Multi-component consistency

Coordinated release musí overiť, že kombinácia componentov je podporovaná.

Príklady rizík:

- nový API producer s nepodporovaným starým consumerom,
- frontend očakáva capability, ktorú backend flag ešte neposkytuje,
- worker spracúva event schema, ktorú API ešte nepublikuje,
- migration contract prebehne pred odstránením starých pods,
- config revision patrí inému artifact setu.

Release manifest a compatibility tests majú overovať set, nie iba jednotlivé artifacts izolovane.

## 18. Producer/consumer coordination

Bezpečný release preferuje backward-compatible transitions:

```text
producer rozšíri contract
→ starí aj noví consumers fungujú
→ consumers sa migrujú
→ telemetry potvrdí adopciu
→ starý contract sa odstráni neskôr
```

Big-bang release všetkých participantov naraz je často signálom, že compatibility window alebo version negotiation chýba.

## 19. Databázový release lifecycle

Databáza je shared mutable state. Release ju nemôže spravovať ako immutable binary.

```text
expand schema
→ deploy compatible code
→ backfill/migrate data
→ over reads/writes
→ prepnúť behavior
→ odstrániť starých consumers
→ contract schema
```

Release record má zachytiť:

- migration IDs a status,
- lock/runtime expectations,
- backfill checkpoint,
- old/new application compatibility,
- rollback limitations,
- reconciliation a integrity evidence,
- moment, keď je contract krok eligible.

## 20. Event-driven release lifecycle

Pri queues a events zohľadni:

- uložené staré messages,
- parallel producer/consumer versions,
- backward/forward schema compatibility,
- replay a poison messages,
- idempotency,
- backlog počas rollout-u,
- rollback consumera,
- deprecation window podľa retention.

Release finalizácia nemá znamenať, že starý event contract možno okamžite odstrániť.

## 21. Deployment verzus release exposure

Deployment odpovedá „kde artifact beží“. Release exposure odpovedá „kto dostáva nový behavior“.

Exposure môže byť riadená cez:

- feature flags,
- rings,
- tenant allowlist,
- canary traffic,
- region rollout,
- store/phased distribution,
- configuration alebo entitlement.

Release record musí rozlišovať:

```text
artifact deployed: 100 % instances
feature exposed: 10 % users
```

Inak je nejasné, kedy používateľský release skutočne nastal.

## 22. Rollout plan

Rollout plan definuje state transitions:

- initial target cohort,
- rollout kroky alebo rings,
- minimálne observation windows,
- promotion metrics,
- abort criteria,
- maximálny blast radius,
- feature-flag transitions,
- dependency ordering,
- rollback, roll-forward alebo disable action,
- ownera pre každé rozhodnutie.

Percentá bez criteria nie sú progressive delivery.

## 23. Release approval

Approval je risk decision nad immutable candidate-om a readiness packetom.

Approver má vidieť:

- čo je v scope,
- presný manifest digest,
- delta od posledného release,
- risk a reversibility,
- blockers, waivery a known issues,
- rollout/abort plan,
- recovery eligibility,
- communication a support readiness.

Approval musí expirovať pri zmene manifestu, relevantnej config, policy, environment preconditions alebo významnej security informácii.

## 24. Separation of duties

Pri citlivých releases môže byť potrebné oddeliť:

- autora zmeny,
- code reviewerov,
- build identity,
- evidence producerov,
- release approvera,
- deployment identity,
- auditora.

Separation of duties sa má vynucovať platformou a identity policy. Nemá znamenať manuálne kopírovanie artifacts alebo údajov medzi systémami.

## 25. Release window

Window môže zohľadňovať:

- support a on-call coverage,
- traffic a business criticality,
- external dependency support,
- regulated change periods,
- customer maintenance expectations,
- error-budget stav,
- prebiehajúce incidenty,
- recovery time.

„Nenasadzovať v piatok“ nie je univerzálne pravidlo. Dôležité je, či organizácia dokáže zmenu pozorovať a bezpečne obnoviť.

## 26. Communication plan

Komunikácia má byť viazaná na release ID a používateľský dopad.

Publiká:

- end users,
- administrators,
- API integrators,
- support a operations,
- security/compliance,
- internal stakeholders,
- external partners.

Plán definuje:

- predbežné oznámenie,
- maintenance/degradation expectation,
- breaking/deprecated behavior,
- live release status,
- incident/rollback update,
- final validation a known issues.

## 27. Release notes

Release notes sú kurátorská komunikácia konkrétneho release.

Obsah podľa publika:

- nové capabilities,
- opravy a security zmeny,
- breaking changes,
- deprecations a removals,
- migration kroky,
- config/default zmeny,
- compatibility requirements,
- known issues,
- recovery alebo rollback limitations,
- support/EOL informácie.

Commit log nevyjadruje vždy user impact a nemá byť publikovaný bez kurácie.

## 28. Changelog

Changelog je dlhodobý chronologický záznam významných zmien. Release notes sú komunikácia konkrétnej release unit.

Changelog fragments umožňujú, aby informácia vznikla spolu so zmenou:

```text
changes/1842.feature.md
changes/1847.fix.md
changes/1851.breaking.md
```

Release automation ich agreguje, validuje kategóriu a priradí immutable release identity.

## 29. Post-deploy verification

Po deployment-e over:

- správny artifact/manifest digest,
- config a schema revision,
- desired počet healthy instances,
- routing a feature-flag stav,
- migrations a background jobs,
- synthetics a critical smoke,
- technical errors, latency a saturation.

Deployment controller success nie je dôkaz správneho runtime state.

## 30. Post-release validation

Po exposure sleduj:

- functional journey completion,
- business KPIs,
- user/support signals,
- authorization a data correctness,
- async side effects a settlements,
- long-running memory/backlog behavior,
- cohort a region differences,
- SLO/error-budget dopad.

Niektoré signals majú delay. Release nemá byť formálne uzavretý skôr, než prejde relevantná observation window alebo je delayed validation explicitne odovzdaná do ongoing monitoring ownershipu.

## 31. Hypercare

Hypercare je dočasne zvýšená pripravenosť po významnom release.

Môže zahŕňať:

- dostupného release ownera,
- zvýšenú dashboard/alert pozornosť,
- support triage channel,
- business KPI review,
- rýchly decision path,
- častejšie status updates.

Hypercare má mať začiatok, koniec a exit criteria. Nenahrádza permanentnú observability ani on-call model.

## 32. Abort, rollback, roll-forward a disable

Recovery action závisí od failure a state compatibility.

- **Abort —** zastaví ďalšie rollout kroky.
- **Feature disable —** odstráni exposure pri zachovanom deployment-e.
- **Rollback —** obnoví staršiu application/release unit.
- **Roll-forward —** nasadí opravu alebo dokončí migráciu.
- **Traffic shift —** presmeruje na zdravý region/ring.
- **Write freeze —** chráni dáta pri corruption riziku.

Rozhodnutie zohľadňuje:

- database/event compatibility,
- external side effects,
- client versions,
- queue/backlog state,
- cache/serialized formats,
- čas na opravu,
- user impact a exposure.

## 33. Rollback eligibility

Pred releaseom over:

- starý artifact/release manifest je dostupný,
- provenance a trust policy ho povoľujú,
- config a secrets references existujú,
- databáza a events sú backward-compatible,
- starý client/server contract stále funguje,
- deployment workflow podporuje návrat,
- post-rollback validation je pripravená.

„Vrátime predchádzajúcu version“ nie je plán bez týchto preconditions.

## 34. Emergency release a hotfix

Emergency flow má byť rýchlejší, nie neauditovaný.

Minimálne zachovaj:

- explicitný incident/risk dôvod,
- source review primeraný situácii,
- immutable artifact a provenance,
- kritické targeted tests,
- security a policy minimum,
- ownera a on-call readiness,
- deployment/release record,
- recovery plan,
- post-release validation,
- následné doplnenie obídených evidence.

Break-glass musí byť časovo obmedzený, auditovaný a následne reviewovaný.

## 35. Hotfix source of truth

Hotfix môže vzniknúť na podporovanej release branch alebo z current mainline podľa incident contextu.

Musí sa zabezpečiť:

- oprava v affected release line,
- forward propagation do mainline a novších lines,
- samostatná version a artifact digest,
- testy pre každú podporovanú line,
- aktualizované release notes,
- odstránenie dočasného workaroundu.

Fix iba v production branch vytvára budúcu regresiu pri ďalšom release.

## 36. Supported version policy

Definuj, ktoré versions sú podporované:

- latest only,
- current a previous major/minor,
- LTS lines,
- security-only support,
- extended paid/regulatory support,
- end-of-life date.

Policy ovplyvňuje:

- backports,
- test matrix,
- artifact retention,
- dependency updates,
- documentation,
- incident response,
- vulnerability SLAs,
- client compatibility.

## 37. Deprecation a end of life

Release lifecycle nekončí vydaním.

EOL proces:

```text
announce deprecation
→ publish replacement/migration
→ measure active usage
→ warning period
→ restrict new adoption
→ end support
→ remove artifacts/endpoints podľa policy
```

EOL musí uviesť:

- poslednú podporovanú version,
- dátum ukončenia,
- typ supportu do termínu,
- migration path,
- data/export obligations,
- security implications,
- ownera a communication channels.

## 38. Release revocation

Release môže byť revokovaný pri kompromitácii, corruption alebo kritickom defekte.

Revocation môže:

- zablokovať nové deployments,
- zastaviť rollout/exposure,
- označiť artifacts ako nepovolené,
- upozorniť active environments,
- spustiť incident, rollback alebo hotfix,
- zachovať artifacts pre forenznú analýzu.

Revocation nie je automaticky fyzické zmazanie evidence.

## 39. Uzatvorenie release recordu

Release sa formálne uzavrie, keď:

- deployment a exposure dosiahli plánovaný stav,
- required validation windows prešli,
- abort/rollback stav je vyriešený,
- known issues a support ownership sú zaznamenané,
- communication bola dokončená,
- evidence a deployment records sú kompletné,
- waivery a follow-up actions majú ownerov a termíny,
- release support/EOL class je priradená.

Closed neznamená, že monitoring končí. Znamená, že release event bol odovzdaný do normálneho prevádzkového a support lifecycle.

## 40. Release retrospective

Pri významnom, neúspešnom alebo emergency release vyhodnoť:

- čo spôsobilo delay alebo incident,
- kvalitu readiness evidence,
- správnosť risk classification,
- approval a waiting time,
- rollout signal quality,
- recovery effectiveness,
- komunikáciu,
- manual steps,
- defect escape a chýbajúce guardrails.

Výstup musí viesť k testu, policy, automation, platform defaultu alebo procesnej zmene.

## 41. Metriky

Sleduj spoločne flow, quality a recovery:

- release frequency,
- lead time od change po release,
- čas ready-to-release waiting,
- candidate count a supersession rate,
- release-train miss rate,
- approval wait time,
- rollout duration,
- abort/rollback/roll-forward rate,
- change fail rate,
- mean exposure before detection,
- failed release recovery time,
- defect escape rate,
- stale candidates,
- emergency release rate,
- unsupported version population,
- release-note alebo communication defects,
- otvorené follow-up actions podľa veku.

Vyšší počet releaseov nie je úspech, ak rastie user impact alebo support debt.

## 42. Diagnostický postup

Keď release zlyhá alebo je nejasný:

1. identifikuj release/manifest digest a current state;
2. zisti presný deployment a exposure scope;
3. porovnaj candidate, approved a deployed identities;
4. over config, infrastructure a schema revisions;
5. skontroluj readiness evidence a freshness;
6. rozlíš deployment, functional, business, compatibility alebo telemetry failure;
7. zastav ďalšiu expozíciu podľa abort policy;
8. zhodnoť rollback/roll-forward/disable eligibility;
9. over data a event integrity;
10. komunikuj release ID a user impact;
11. uchovaj timeline a decision records;
12. po recovery uzavri hotfix forward propagation a preventívnu kontrolu.

## 43. Typické anti-patterny

### Release je manuálny checklist v tickete

Evidence je ručne kopírovaná, zastaraná a neviazaná na immutable candidate.

### Final artifact sa po schválení rebuildne

Approval a tests patria iným bytes.

### Scope sa mení počas rollout-u

Nie je možné určiť, čo evidence a communication pokrývali.

### Veľký mesačný release bundle

Zvyšuje blast radius, compatibility matrix a root-cause ambiguity.

### Approval bez risk packetu

Je ceremoniálny a predlžuje queue bez kvalitnejšieho rozhodnutia.

### Deployment = release = validation

Orchestrátor success sa zamieňa za používateľský outcome.

### Rollback plán ignoruje mutable state

Starý artifact nemusí rozumieť novej databáze, events alebo cache.

### Hotfix iba v release branch

Nasledujúci release z mainline problém znovu zavedie.

### Release branch bez EOL

Vzniká neurčitý support záväzok a divergence.

### Hypercare bez exit criteria

Dočasný režim sa stane trvalým manuálnym dohľadom.

### Release record sa nikdy neuzavrie

Nie je jasný support owner, final state ani follow-up debt.

## 44. Praktický rozhodovací rámec

1. Čo presne tvorí release unit?
2. Aká immutable identity a manifest ju reprezentujú?
3. Aké changes sú v scope a ktoré nie?
4. Aká admission/readiness policy platí?
5. Ktoré evidence sú complete a fresh?
6. Je candidate superseded alebo stále aktuálny?
7. Aké component/API/event/database compatibility existujú?
8. Aký cadence alebo train release používa?
9. Ktorý deployment stav a ktorý exposure stav sa menia?
10. Aké promotion a abort criteria platia?
11. Aký je maximálny blast radius a observation window?
12. Je rollback kompatibilný so shared state?
13. Aký roll-forward alebo disable mechanizmus existuje?
14. Kto schvaľuje a kto reaguje?
15. Aké publikum potrebuje komunikáciu?
16. Kedy je release validated a kedy formálne closed?
17. Aký support/EOL lifecycle dostane?
18. Ako sa hotfix forward-propaguje?

## 45. Kontrolný checklist

Pred release over:

- release unit a manifest sú immutable,
- change inventory je úplné,
- candidate nebol po evidence rebuildnutý,
- readiness packet patrí správnemu manifestu,
- evidence je complete, fresh a policy-eligible,
- waivery majú ownera, compensating control a expiry,
- compatibility matrix pokrýva old/new participants,
- migrations a backfills majú explicitné fázy,
- deployment a exposure sú oddelené,
- rollout, observation a abort criteria sú definované,
- rollback/roll-forward/disable sú reálne eligible,
- on-call, support a communication sú pripravené,
- release notes uvádzajú breaking/deprecation/known issues,
- post-deploy aj post-release validation sú definované,
- support/EOL class je určená,
- hotfix a branch lifecycle majú forward-propagation pravidlá,
- release record bude po validation formálne uzavretý.

## 46. Kontrolné otázky

1. Aký je rozdiel medzi buildom, deploymentom a releaseom?
2. Čo tvorí release unit?
3. Načo slúži release manifest?
4. Aké stavy má release lifecycle?
5. Prečo zmena candidate-u invaliduje časť evidence?
6. Čo obsahuje readiness packet?
7. Aký je rozdiel medzi blocked, incomplete a inconclusive readiness?
8. Ako funguje release train admission?
9. Aký je rozdiel medzi scope freeze a code freeze?
10. Aké riziká má release branch?
11. Prečo multi-component release potrebuje set-level compatibility?
12. Ako sa deployment odlišuje od release exposure?
13. Kedy má approval reálnu rozhodovaciu hodnotu?
14. Ako database a events komplikujú release?
15. Prečo rollback nemusí byť bezpečný?
16. Čo musí zachovať emergency release?
17. Ako sa hotfix propaguje do mainline?
18. Čo má obsahovať supported-version a EOL policy?
19. Kedy je release record možné uzavrieť?
20. Ktoré metriky odhalia release process debt?

## Summary

Release management je riadený lifecycle immutable release unit od candidate assembly cez readiness, approval, deployment, progressive exposure a validation až po support a end of life. Dôveryhodný proces používa release manifest, complete a fresh evidence, explicitný scope, compatibility windows, oddelenie deploymentu od releaseu, merateľné rollout/abort criteria a overenú recovery. Hotfix, revocation, support, EOL a formálne uzatvorenie release recordu sú súčasťou rovnakého systému; release nekončí vytvorením artifactu ani zeleným deployment jobom.

## Glossary impact

Relevantné pojmy: release management, release unit, release identity, release manifest, release record, release state machine, change inventory, scope admission, release candidate, candidate supersession, readiness packet, release cadence, release train, scope freeze, release branch, deployment exposure, hypercare, emergency release, hotfix, release revocation, supported version policy, end of life a release closure.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Semantic Versioning](semantic-versioning.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Recreate deployment →](recreate-deployment.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
