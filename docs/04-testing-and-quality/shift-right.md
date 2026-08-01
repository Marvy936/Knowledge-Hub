# Shift-right

<!-- CONCEPT-FIRST:START -->
## Čo znamená shift-right

Shift-right znamená získavať quality a behavior evidence v neskorších fázach delivery a v produkčnom alebo production-like prostredí. Nejde o testovanie namiesto pre-release kontrol, ale o overenie assumptions, ktoré sa naplno prejavia až pri reálnom trafficu, dátach, topológii a používateľoch.

Bežné mechanizmy:

```text
post-deploy smoke
synthetic transactions
real-user monitoring
canary alebo ring exposure
feature flags
shadow traffic
runtime assertions
business metrics
```

Technická validácia sleduje readiness, errors, latency a resource state. Funkčná validácia overuje user journey. Business validácia sleduje výsledok ako dokončená objednávka, successful payment alebo správny export. Zelená infraštruktúra nemusí znamenať zelený business outcome.

Synthetic test je umelý kontrolovaný actor. RUM pozoruje skutočných users a cohorts. Synthetic poskytuje deterministický probe, RUM reprezentatívnosť reálneho sveta; každý má odlišné bias a privacy hranice.

Canary znižuje exposure tým, že nový artifact dostane časť trafficu. Verdict musí porovnávať relevantné cohorts a metriky. Ak canary dostáva iba interných users alebo ľahšie requests, môže byť nereprezentatívna.

Neutrálny príklad: release je technicky zdravý a server vracia `200`, ale nový frontend skrýva tlačidlo pre mobile viewport. Backend metrics sú zelené; synthetic mobile journey alebo RUM conversion odhalí functional/business regresiu.

Shift-right potrebuje safety controls: bounded blast radius, abort criteria, immutable artifact identity, traffic/feature/data state inventory a recovery plan. Experimentovanie priamo v produkcii bez týchto hraníc nie je quality strategy.

Observability nie je automaticky test. Metrika sa stane oracle-om až po definovaní expected behavior, threshold, cohortu a rozhodnutia. Produkčný signal treba korelovať s exact release a exposure state-om.
<!-- CONCEPT-FIRST:END -->

## Detailný výklad a Atlas aplikácia

## Metadata

- Status: Learning
- Level: L2
- Domain: Testing and Software Quality

Shift-right rozširuje verification, validation a experimentovanie do deploymentu a produkčnej prevádzky. Jeho cieľom nie je „testovať až na používateľoch“, ale bezpečne získať dôkaz o vlastnostiach, ktoré predprodukčné prostredie nevie úplne reprodukovať: reálny traffic mix, identity, tenant skew, objem dát, regionálnu sieť, quotas, dlhodobý state a emergentné distribuované správanie.

```text
release hypotéza a riziko
→ immutable artifact a configuration identity
→ obmedzená cohort/exposure
→ technical + functional + business oracle
→ porovnateľný baseline alebo control
→ promote, pause, rollback alebo roll-forward
→ dlhšie recovery a delayed-effect pozorovanie
→ poznatok prevedený na skorší control
```

Shift-right nadväzuje na shift-left. Skoré kontroly znižujú počet predvídateľných chýb; produkčný feedback odhaľuje zostávajúce blind spots a spätne zlepšuje requirements, testy, policies a platform defaults.

## 1. Cieľ kapitoly

Nosný model kapitoly je controlled-production-evidence lifecycle:

```text
čo ešte nevieme pred produkciou
→ hypotéza a acceptance/guardrail criteria
→ artifact, config a cohort provenance
→ najmenší užitočný blast radius
→ exposure state machine
→ kompozitný oracle a signal latency
→ kauzálne porovnanie s control/baseline
→ rozhodnutie a bezpečná transition
→ post-promotion observation
→ defect escape premenený na trvalú kontrolu
```

Produkčný dashboard bez vopred definovaného rozhodnutia nie je shift-right experiment. Rovnako release bez cohort identity a observation window nevytvára dôveryhodný dôkaz o novej verzii.

## 2. Nosný scenár: Atlas Orders 3.9.2

Atlas releasuje export objednávok pre veľkých tenantov. Predprodukčné testy už potvrdili:

- tenant authorization a event contract;
- compatibility starého a nového workeru;
- PostgreSQL migration a restartovateľný backfill;
- component load pri syntetickom datasete;
- telemetry schema a deployment smoke.

Stále zostávajú neistoty:

```text
reálny tenant-size skew
→ veľké exporty môžu držať DB connections dlhšie

regionálna latency
→ download link môže expirovať skôr, než ho používateľ otvorí

production identity a object-storage policy
→ signed URL môže mať iné effective permissions

skutočný retry behavior klientov
→ timeout môže zvýšiť duplicate attempts

business workflow
→ technicky dokončený export nemusí byť používateľsky použiteľný
```

Shift-right z týchto neistôt vytvorí explicitný rollout experiment, nie neštruktúrované „sledovanie po deploymente“.

## 3. Predpoklady bezpečnej produkčnej validácie

Atlas nezačne expozíciu bez týchto controls:

- immutable image digest a source provenance;
- deployment a configuration revision;
- feature-flag snapshot a routing policy;
- cohort identity a stabilné assignment semantics;
- technical, functional a business metrics s release labels;
- rollback alebo roll-forward path;
- abort criteria a owner;
- synthetic identity a bezpečné test data;
- data/privacy review pre RUM a business events;
- komunikačný a incidentný postup.

Bez týchto predpokladov sa pozorovaný outcome nedá pripísať release-u a blast radius nemožno riadiť.

## 4. Exposure state machine

Atlas rollout používa explicitné stavy:

```text
deployed, 0 % user traffic
→ synthetics a config verification
→ internal tenant
→ 1 % eligible production cohort
→ 5 % matched cohort
→ 25 % vrátane large-tenant segmentu
→ 50 % capacity observation
→ 100 % promotion
→ post-promotion watch
```

Každý stav definuje:

- minimálnu duration a sample count;
- cohort composition;
- success metrics a guardrails;
- maximálnu signal latency;
- abort threshold;
- povolenú next transition;
- rollback alebo roll-forward action;
- decision ownera.

Percentá nie sú univerzálny recept. Pri malej populácii môže byť dôležitejší počet kritických journeys než percento trafficu.

## 5. Kompozitný produkčný oracle

Produkčný oracle má tri vrstvy:

### Technický výsledok

Atlas sleduje:

- request a job error rate;
- p95/p99 API a export completion latency;
- DB connection wait, lock waits a query duration;
- queue depth, oldest-message age a retry amplification;
- worker restarts, memory a CPU saturation;
- object-storage a identity-provider failures;
- telemetry completeness.

### Funkčný výsledok

Overuje:

- export obsahuje iba správny tenant;
- vznikne presne jeden export object pre idempotency key;
- signed URL funguje a neprekročí permission scope;
- event, worker a download path zachovajú correlation ID;
- timeout/retry nevytvorí duplicate side effect;
- starý aj nový worker spracujú povolenú schema kombináciu.

### Business a používateľský výsledok

Sleduje:

- export completion a download success rate;
- čas od requestu po reálne použitie súboru;
- abandonment a repeat-request rate;
- support contacts alebo manual retries;
- segmenty podľa tenant size, regiónu a klienta;
- poškodenie iných kritických journeys.

HTTP 200 a zelené pods nemusia znamenať, že release je prijateľný.

## 6. Release a signal provenance

Každý signal musí byť prepojiteľný s:

```text
artifact digest
+ deployment revision
+ config/flag version
+ cohort a assignment rule
+ region/zone
+ tenant segment
+ request/job/trace identity
+ rollout stage a čas
```

Ak dashboard agreguje starú a novú verziu bez release dimension, nemožno určiť, ktorá verzia spôsobila regresiu. Rovnako feature flag bez audit trailu môže zmeniť behavior počas observation window a znehodnotiť experiment.

## 7. Baseline a control group

Produkčná metrika potrebuje porovnanie. Atlas môže použiť:

- súbežnú control group na starej verzii;
- matched cohort podľa tenant size, regiónu a operation mixu;
- stabilný synthetic journey proti starej aj novej verzii;
- historický baseline iba pri porovnateľnej sezónnosti;
- pre/post okno ako slabší pomocný signál.

Control musí byť vystavený podobnému workloadu. Canary z malých tenantov nie je validný control pre full rollout, ktorý obsahuje veľkých tenantov s inou distribúciou dát.

## 8. Synthetic monitoring

Synthetic probe poskytuje kontrolovaný opakovateľný journey:

```text
external DNS a TLS
→ login test identity
→ request exportu v test tenantovi
→ wait na terminal state
→ overenie signed URL a redigovaného obsahu
→ cleanup/TTL
```

Synthetic test potrebuje least-privilege identity, označené dáta, rate limit, idempotency, cleanup a jasný observation point. Interný probe nepreukazuje public DNS, CDN alebo client-visible TLS path.

Synthetics odhaľujú availability a contract failures aj pri nízkom reálnom trafficu. Nemodelujú však distribúciu reálnych zariadení, dát a používateľského správania.

## 9. Real User Monitoring a business events

RUM a client/business telemetry ukazujú skutočné experience boundaries:

- client-perceived latency;
- frontend alebo SDK errors;
- device, browser a region segment;
- journey completion a abandonment;
- retry behavior;
- feature cohort;
- download completion a použitie výsledku.

Instrumentation musí používať data minimization, sampling, redaction, retention a access controls. Session replay alebo raw URLs môžu obsahovať osobné alebo citlivé údaje a nie sú automaticky legitímne iba preto, že slúžia testovaniu.

## 10. Canary ako safety mechanizmus

Canary znižuje blast radius a vytvára porovnateľný produkčný dôkaz. Nie je to automaticky A/B experiment.

```text
canary otázka
→ je nový artifact dostatočne bezpečný na širšiu expozíciu?

A/B otázka
→ ktorý variant lepšie spĺňa business hypotézu?
```

Canary potrebuje stabilné assignment, guardrails a technické abort criteria. A/B test navyše potrebuje experiment unit, randomizáciu, sample-size/statistical model a ochranu pred interference.

## 11. Feature flags a oddelenie deploymentu od exposure

Feature flag umožní nasadiť kód bez okamžitého sprístupnenia behavioru:

```text
artifact deployed
→ flag off
→ synthetics/internal validation
→ cohort enablement
→ observation
→ širšia expozícia alebo disable
```

Flag contract obsahuje default pri nedostupnom evaluatorovi, targeting rules, audit, ownera, expiry a cleanup. Dlhodobo zabudnutý flag zväčšuje state space a môže vytvoriť kombináciu, ktorú testy ani rollout nepoznajú.

## 12. Shadow traffic

Shadowing kopíruje request alebo event do novej implementácie bez použitia jej response pre používateľa. Je vhodné na porovnanie parsera, query behavioru alebo model outputu pri reálnom input mixe.

Shadow musí zabrániť reálnym side effects:

- payment, email a notification sú zakázané alebo presmerované;
- writes idú do izolovaného storage alebo dry-run boundary;
- credentials majú minimálne permissions;
- shadow load má capacity budget;
- citlivé dáta a retention majú explicitný contract.

Shadow pass nepreukazuje client-visible latency, routing, authorization response ani write consistency, pokiaľ tieto boundaries nie sú reálne vykonané.

## 13. Decision contract

Rollout decision rozlišuje:

```text
PROMOTE
→ evidence je complete a criteria splnené

PAUSE
→ signal potrebuje dlhšiu observation alebo triage

ROLLBACK
→ predchádzajúci artifact/config je bezpečne obnoviteľný

ROLL_FORWARD
→ rýchla kompatibilná oprava je bezpečnejšia než návrat

ABORT/CONTAIN
→ blast radius sa okamžite znižuje a incident sa eskaluje

INCONCLUSIVE
→ evidence alebo sample nestačí; nie je to pass
```

Rollback nie je vždy možný. Database mutation, event emission alebo external side effect môžu vyžadovať roll-forward, reconciliation alebo compensating action.

## 14. Signal latency a observation window

Rôzne failures majú odlišnú dobu prejavu:

```text
route alebo startup failure
→ sekundy

retry amplification a queue growth
→ minúty

large-tenant completion regression
→ desiatky minút až hodiny

memory leak, retention alebo billing side effect
→ dlhšie okno
```

Automatická promotion po krátkom technickom okne môže prehliadnuť business alebo delayed-state failure. Observation window sa odvodzuje z mechanizmu, nie z univerzálneho časovača.

## 15. Worked failure: technický canary bol zelený, journey zlyhal

Atlas canary mal normálnu API latency, error rate aj worker health. Veľká časť používateľov v pomalšom regióne však export nestiahla:

```text
export job sa dokončil
→ signed URL mala 60-sekundovú expiráciu od vytvorenia
→ notification a regionálna latency spotrebovali väčšinu okna
→ používateľ otvoril link po expirácii
→ API a worker metrics zostali zelené
→ download completion rate klesla
```

### Root cause

Oracle obsahoval iba server-side technické signály. Chýbal business/client observation point medzi notification delivery a úspešným downloadom.

### Náprava

- signed URL expiry sa viaže na reálny access contract;
- RUM/business event meria `export_ready → download_success`;
- synthetic probe beží z relevantných regiónov;
- canary guardrail zahŕňa download completion podľa region segmentu;
- regression test používa fake clock a delayed-open scenár;
- product requirement explicitne definuje použiteľné download window.

Produkčný finding sa tým vrátil do požiadavky, unit/component testu aj shift-right guardrailu.

## 16. Worked failure: canary cohort nebola reprezentatívna

Prvých 10 % trafficu bolo routovaných podľa tenant ID hash. Náhodou obsahovalo prevažne malých tenantov:

```text
canary DB wait normal
→ export completion normal
→ rollout 100 %
→ veľkí tenants spustili paralelné exporty
→ DB pool a object-storage quota sa saturovali
→ queue backlog a abandonment prudko vzrástli
```

### Root cause

Assignment bolo stabilné, ale control a canary neboli matched podľa tenant-size a workload distribution. Percento trafficu sa nesprávne považovalo za reprezentatívnu vzorku.

### Náprava

- cohort design explicitne stratifikoval tenant-size tiers;
- rollout mal samostatnú large-tenant fázu;
- guardrails sledovali DB wait, queue age a completion per segment;
- capacity model používal produkčnú distribúciu;
- post-promotion watch zostal aktívny po 100 % trafficu.

## 17. Rollback, roll-forward a data compatibility

Pred expozíciou Atlas overí recovery package:

- last-known-good artifact a config identity;
- compatibility starej aplikácie s aktuálnou schema;
- feature-flag disable path;
- event a queue behavior pri mixed versions;
- compensating actions pre external side effects;
- reconciliation pre partial exports;
- ownera a runbook.

Rollback, ktorý obnoví starý image nad nekompatibilnou databázou, môže incident zhoršiť. Recovery decision musí zahŕňať application, config, data a external-state compatibility.

## 18. Produkčné experimenty a etika

Produkčná validácia nesmie prenášať neprimerané riziko na používateľov. Potrebuje:

- najmenší užitočný blast radius;
- explicitné excluded populations pri citlivom workflowe;
- privacy a consent semantics;
- zákaz neplánovaných finančných alebo právnych side effects;
- audit experimentu a rozhodnutí;
- rýchle containment controls;
- transparentný ownership.

„Potrebujeme reálne dáta“ nie je dostatočný dôvod na nekontrolovaný experiment.

## 19. Feedback do skorších vrstiev

Každý shift-right finding sa klasifikuje:

```text
predvídateľný a reprodukovateľný failure
→ nový requirement, test, policy alebo secure default vľavo

prostredie-špecifický failure
→ production guardrail, synthetic alebo canary control

emergentný failure
→ model, observability a chaos experiment

business mismatch
→ upravený acceptance criterion a product metric
```

Cieľom nie je odstrániť produkčné učenie, ale zabezpečiť, aby sa rovnaká trieda chyby neopakovala bez skoršej ochrany.

## 20. Diagnostický postup

Pri podozrení na rollout regression:

1. Potvrď artifact digest, deployment/config revision a rollout stage.
2. Over cohort assignment a porovnateľnosť control group.
3. Rozdeľ technical, functional a business signals.
4. Nájdite prvý observation point, kde sa canary od controlu odlíšil.
5. Skontroluj sample size, signal latency, missing telemetry a dashboard aggregation.
6. Rozlíš release effect od regionálneho incidentu, dependency outage alebo traffic zmeny.
7. Zastav promotion alebo zníž exposure podľa abort contractu.
8. Vyhodnoť rollback/roll-forward/data compatibility.
9. Zachovaj timeline, release dimensions, traces a cohort evidence.
10. Preveď root cause na skorší regression control alebo trvalý production guardrail.

## 21. Referenčné pravidlá

- Shift-right nie je náhrada predprodukčných testov.
- Produkčný experiment začína hypotézou a rozhodnutím.
- Artifact, config, flag a cohort identity patria do evidence provenance.
- Exposure rastie po explicitnej state machine, nie po pocite.
- Oracle kombinuje technical, functional aj business outcomes.
- Control group musí byť porovnateľná s canary workloadom.
- Synthetics a RUM poskytujú rozdielne observation points.
- Percento trafficu nie je automaticky reprezentatívna cohorta.
- Inconclusive alebo missing evidence nie je pass.
- Observation window sa odvodzuje z failure latency.
- Rollback potrebuje application, data a side-effect kompatibilitu.
- Produkčný finding sa má podľa možnosti zmeniť na skorší control.

## 22. Časté omyly

### „Deployment bol úspešný, release je zdravý“

Orchestrátor potvrdil mutation, nie používateľský ani business outcome.

### „Canary je iba 5 % trafficu“

Dôležitá je cohort composition, assignment, sample a guardrails, nie samotné percento.

### „Server metrics sú zelené“

Client journey, tenant correctness alebo business completion môžu byť červené.

### „RUM nahrádza synthetics“

RUM potrebuje reálny traffic; synthetics poskytujú kontrolovaný journey a known observation point.

### „Flag off znamená nulové riziko“

Kód, migrácia, startup behavior alebo shared resources môžu ovplyvniť systém aj pri vypnutom feature path-e.

### „Rollback je vždy najbezpečnejší“

Data a external side effects môžu spraviť návrat nekompatibilným.

## 23. Zhrnutie

Dôveryhodný shift-right model pre Atlas je:

```text
reziduálne produkčné riziko
→ hypotéza a guardrails
→ immutable artifact/config/flag identity
→ matched cohort a bounded exposure
→ technical + functional + business oracle
→ kauzálne porovnanie
→ promote/pause/rollback/roll-forward
→ delayed-effect a recovery observation
→ skorší regression control alebo production guardrail
```

Shift-right premieňa produkciu na riadený zdroj dôkazov. Nerobí z používateľov nekontrolovaných testerov; používa blast-radius controls, observability a explicitné rozhodnutia na bezpečné učenie.

## 24. Kontrolné otázky

1. Ktoré neistoty zostávajú po predprodukčných Atlas testoch?
2. Čo musí obsahovať exposure state machine?
3. Prečo produkčný oracle potrebuje technical, functional aj business vrstvu?
4. Aké dimensions patria do release provenance?
5. Ako sa líši synthetic monitoring od RUM?
6. Prečo canary percento nemusí byť reprezentatívne?
7. Aký je rozdiel medzi canary safety rolloutom a A/B experimentom?
8. Aké blind spots má shadow traffic?
9. Ako signal latency určuje observation window?
10. Prečo bol Atlas technický canary zelený pri business failure?
11. Kedy je roll-forward bezpečnejší než rollback?
12. Ako sa shift-right finding vracia do shift-left systému?

## Glossary impact

Relevantné pojmy: shift-right, controlled exposure, rollout state machine, production validation, synthetic monitoring, Real User Monitoring, release cohort, matched cohort, control group, canary analysis, feature exposure, shadow traffic, signal latency, technical validation, functional validation, business validation a post-promotion watch.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Shift-left](shift-left.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Chaos testing →](chaos-testing.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
