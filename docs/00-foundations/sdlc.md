# Software Development Life Cycle

Software Development Life Cycle nie je iba zoznam fáz medzi požiadavkou a nasadením. Je to riadený chain rozhodnutí a stavov, v ktorom sa musí dať preukázať, prečo zmena vznikla, ktorá verzia požiadavky a návrhu bola implementovaná, aký artifact z nej vznikol, kde bol nasadený a či priniesol zamýšľaný používateľský alebo prevádzkový výsledok.

Užitočný mentálny model preto nezačína slovami `plan → code → deploy`, ale exact change subjectom a evidence chainom:

```text
potreba a očakávaný outcome
→ versionovaná požiadavka a acceptance contract
→ návrh a risk boundaries
→ source change a review
→ build artifact a verification evidence
→ release a deployment generation
→ runtime exposure
→ user/business observation
→ maintenance, recovery alebo retirement
```

Každá šípka predstavuje state transition, ktorá môže uspieť, zlyhať či skončiť s neznámym výsledkom. Zelený build napríklad preukazuje iba vlastnosti konkrétneho build subjectu; nepreukazuje, že produkcia načítala rovnaký artifact ani že používateľ dokončil svoj workflow. SDLC je preto uzavretý feedback system, nie jednosmerná výrobná linka.

## 1. Definícia

Software Development Life Cycle (SDLC) je riadený životný cyklus softvéru od vzniku potreby cez návrh, implementáciu, overenie, nasadenie a prevádzku až po kontrolované vyradenie systému. Model spája technickú prácu s business hodnotou, vlastníctvom, rizikom a dôkazmi o tom, že zmena funguje.

SDLC nie je konkrétny nástroj ani jediná metodika. Waterfall, Agile, Lean alebo DevOps-oriented delivery sú rôzne spôsoby, ako organizovať rovnaký základný lifecycle a jeho feedback loops.

## 2. Problém, ktorý SDLC rieši

Bez riadeného životného cyklu sa vývoj redukuje na písanie kódu a odovzdanie výsledku ďalšiemu tímu. Produkčný systém však musí riešiť správnosť požiadavky, bezpečnosť, testovateľnosť, deployment, pozorovateľnosť, podporu, zmeny závislostí, obnovu a nakoniec bezpečné odstránenie.

SDLC vytvára spoločný rámec, v ktorom má každá zmena definovaný dôvod, ownera, acceptance criteria a spôsob overenia. Tým znižuje riziko, že technicky správne riešenie vyrieši nesprávny problém alebo sa dostane do produkcie bez možnosti zistiť jeho reálny dopad.

Kľúčové otázky nie sú iba procesný checklist; určujú, či má zmena zmysluplný end-to-end contract:

- **Prečo zmenu robíme?** — otázka spája implementáciu s používateľským alebo prevádzkovým outcome-om a zabraňuje práci bez preukázanej hodnoty.
- **Kto za zmenu zodpovedá?** — ownership určuje, kto rozhoduje o scope-e, risku, nasadení, rollbacku a následnej prevádzke.
- **Ako dokážeme, že funguje?** — acceptance criteria, testy a produkčné signály premieňajú neurčitú požiadavku na overiteľný contract.
- **Ako sa bezpečne dostane do produkcie?** — build, release, deployment a rollout model musia kontrolovať identitu artifactu, kompatibilitu a blast radius.
- **Ako zistíme správne správanie v produkcii?** — observability a user feedback musia merať skutočný outcome, nie iba stav procesu alebo servera.
- **Ako zmenu opravíme alebo odstránime?** — rollback, migration, maintenance a retirement musia byť súčasťou návrhu skôr, než vznikne incident.

## 3. Mentálny model

SDLC je uzavretý tok hodnoty a spätnej väzby. Zmena začína hypotézou o probléme, prechádza technickým spracovaním a končí meraním výsledku, ktoré môže potvrdiť pôvodný predpoklad alebo vytvoriť ďalšiu potrebu.

```text
Potreba alebo problém
  ↓
Discovery a požiadavky
  ↓
Planning a analýza
  ↓
Návrh
  ↓
Implementácia
  ↓
Verification a testing
  ↓
Build, release a deployment
  ↓
Prevádzka a pozorovanie
  ↓
Spätná väzba, maintenance alebo retirement
  └───────────────────────────────↺
```

Nejde o jednosmernú výrobnú linku. Informácie z testov a prevádzky sa vracajú do požiadaviek, návrhu aj priorít a často odhalia, že pôvodná predstava o používateľovi alebo systéme bola neúplná.

## 4. Aktéri, stav a zodpovednosť

SDLC prepája product, engineering, security, platform, operations a business vlastníkov. Každý aktér vidí inú časť rizika, preto izolované handoffy vedú k lokálnej optimalizácii a strate kontextu.

Authoritative state lifecycle-u vzniká v rôznych systémoch: požiadavky v product backlogu, kód v source control, artifact v registry, deployment configuration v deklaratívnom source of truth a prevádzkové evidence v telemetry a incident systémoch. Dôležité je vedieť, ktorý systém je autoritatívny pre konkrétne rozhodnutie a ako sa zmena medzi týmito stavmi trasuje.

## 5. Discovery a requirements

Discovery identifikuje používateľský, business alebo technický problém, ktorý sa má riešiť. Výstupom nemá byť iba zoznam funkcií, ale opis očakávanej hodnoty, používateľov, obmedzení, rizík a spôsobu merania úspechu.

Požiadavka potrebuje acceptance criteria a explicitné non-functional requirements, napríklad dostupnosť, latency, bezpečnosť, data retention alebo recovery. Zlá požiadavka implementovaná bezchybne je stále zlyhanie, pretože systém optimalizuje nesprávny outcome.

## 6. Planning a analýza

Planning určuje scope, poradie práce, dependencies, kapacitné potreby a spôsob dodania. Analýza preveruje, či je problém vhodné riešiť softvérom, aké systémy zmena ovplyvní a ktoré predpoklady treba overiť skôr než vznikne drahá implementácia.

Táto fáza nemá vytvoriť falošnú presnosť dlhodobého plánu. Má znížiť najväčšie neznáme, rozdeliť prácu na overiteľné kroky a pomenovať riziká, ktoré môžu zmeniť návrh alebo business rozhodnutie.

## 7. Design

Design opisuje application boundaries, interfaces, data model, identity, security controls, infrastructure, deployment a prevádzkový model. Dobrý návrh ukazuje, ako bude systém fungovať v normálnom stave aj pri neplatnom vstupe, preťažení, strate dependency alebo neúspešnom rollout-e.

Návrh nie je iba diagram komponentov. Musí vysvetliť state ownership, consistency, trust boundaries, failure domains, observability a migration path, pretože práve tieto vlastnosti určujú správanie v produkcii.

## 8. Implementation

Implementation premieňa návrh na verzovaný kód, konfiguráciu, databázové migrácie, infrastructure definitions a automatizáciu. Zmena má byť reprodukovateľná a reviewovateľná, aby bolo možné zistiť, čo presne sa zmenilo, kto to schválil a aký artifact z toho vznikol.

Kvalitná implementácia zahŕňa aj test hooks, telemetry, feature-control mechanizmy a bezpečné defaults. Ak sa operability dopĺňa až po incidente, systém môže byť funkčný v deme, ale neprevádzkovateľný v produkcii.

## 9. Verification a testing

Verification overuje, či implementácia spĺňa definovaný contract a či nevytvára neprijateľné regresie. Rôzne testy poskytujú odlišné dôkazy: unit test izoluje malú logiku, integration test overuje spoluprácu komponentov a end-to-end test skúma používateľský tok v realistickejšom prostredí.

Testing nemôže dokázať absenciu všetkých chýb. Jeho cieľom je znížiť neistotu primerane riziku a doplniť testy o statickú analýzu, security scanning, performance evidence a neskoršie produkčné pozorovanie.

## 10. Build

Build transformuje source inputs na spustiteľný alebo distribuovateľný výstup. Proces môže kompilovať kód, riešiť dependencies, spúšťať generovanie, vytvárať balík alebo container image a pridávať metadata potrebné na identifikáciu pôvodu.

Reprodukovateľný build používa verzované vstupy, pinned dependencies a kontrolované prostredie. Ak rovnaký source revision vytvára nepredvídateľne odlišný artifact, nemožno spoľahlivo auditovať ani obnoviť konkrétnu produkčnú verziu.

## 11. Artifact

Artifact je nemenný výstup buildu, napríklad binary, package, archive alebo container image. Musí mať jednoznačnú identitu, ideálne digest alebo iný content-derived identifier, aby deployment presne vedel, ktoré bytes nasadzuje.

Artifact nemá byť znovu buildovaný pre každé prostredie. Rovnaký overený artifact sa má promovať medzi prostrediami a environment-specific správanie sa pridáva cez kontrolovanú konfiguráciu, inak staging a production nepoužívajú totožný testovaný výstup.

## 12. Release

Release je rozhodnutie, že konkrétna verzia je pripravená na určený spôsob použitia. Zahŕňa schválenie evidence, risku, compatibility, dokumentácie a prípadného rollout plánu; nemusí ešte znamenať, že verzia obsluhuje production traffic.

Release identity má odkazovať na konkrétny artifact a source revision. Nejasný label typu `latest` s meniacim sa obsahom znemožňuje určiť, čo bolo schválené a čo sa má pri incidente rollbacknúť.

## 13. Deployment

Deployment je technická operácia, ktorá umiestni artifact a configuration do cieľového prostredia. Mení runtime state systému, preto musí riešiť ordering, permissions, migrations, health verification a failure behavior jednotlivých krokov.

Úspešný deployment job nepreukazuje úspešný user outcome. Pipeline môže vytvoriť resources a napriek tomu nasadiť chybnú konfiguráciu alebo verziu, ktorá zlyháva až pri reálnom trafficu.

## 14. Rollout

Rollout určuje, ako sa nasadená verzia sprístupňuje instances, tenants alebo používateľom. Môže byť okamžitý, rolling, canary, blue-green alebo riadený feature flagom podľa rizika a architecture constraints.

Cieľom rollout-u je obmedziť blast radius a vytvoriť čas na vyhodnotenie signálov. Ak systém nevie rozlíšiť starú a novú verziu v telemetry alebo nemá abort condition, postupné nasadenie neposkytuje reálnu kontrolu rizika.

## 15. Operations

Operations udržiava službu dostupnú, bezpečnú a obnoviteľnú počas reálneho používania. Zahŕňa monitoring, incident response, capacity, backup, patching, dependency lifecycle, cost a podporu používateľov.

Prevádzka nie je koniec SDLC, ale zdroj najpresnejšej spätnej väzby. Produkčný traffic, zlyhania a používateľské správanie odhaľujú vlastnosti, ktoré staging ani test data nedokážu úplne reprodukovať.

## 16. Maintenance a evolution

Väčšina životnosti softvéru prebieha po prvom release. Systém dostáva opravy, security updates, dependency upgrades, performance zmeny, nové capabilities a úpravy podľa zmeneného business prostredia.

Maintenance potrebuje rovnakú disciplínu ako nový vývoj. „Malá oprava“ môže meniť data schema, compatibility alebo deployment risk a musí prejsť primeraným lifecycle-om namiesto priamej ručnej zmeny v produkcii.

## 17. Retirement

Retirement kontrolovane ukončuje službu, component alebo verziu. Musí riešiť migráciu používateľov a dát, retention, legal hold, zrušenie credentials, DNS, integrations, monitoring, backupov a cloud resources.

Nedokončený retirement ponecháva attack surface, náklady a nejasný data ownership. Systém sa nepovažuje za vyradený iba preto, že už neprijíma nový traffic; jeho dáta, identities a dependencies môžu zostať aktívne.

## 18. Modely organizácie SDLC

### Waterfall

Waterfall organizuje fázy prevažne sekvenčne a každá fáza má formálne výstupy. Poskytuje predvídateľný governance model, ale feedback o chybných požiadavkách alebo integrácii prichádza neskoro a zmena je drahšia.

Je vhodnejší tam, kde sú požiadavky stabilné, proces regulovaný a zmeny potrebujú formálne schválenie. Ani v takom prostredí však nemusí znamenať nulovú iteráciu alebo odklad testovania až na koniec.

### Iterative a incremental development

Iterative model opakovane spresňuje riešenie na základe feedbacku. Incremental model dodáva použiteľné časti systému po menších prírastkoch namiesto jedného veľkého release-u.

Kombinácia znižuje risk tým, že technické aj produktové predpoklady sa overujú skôr. Nevýhodou môže byť fragmentovaný design, ak iterácie nemajú spoločný architecture a product direction.

### Agile

Agile uprednostňuje spoluprácu, krátke feedback loops, priebežné dodávanie hodnoty a schopnosť reagovať na zmenu. Nie je synonymom Scrumu, absencie dokumentácie ani neplánovanej práce.

Agile funguje iba vtedy, keď tím dokáže získať reálny feedback a upraviť smer. Ak sa práca rozdelí na krátke sprinty, ale release nastane raz za pol roka, hlavný feedback loop zostáva dlhý.

### Lean

Lean skúma celý value stream a odstraňuje čakanie, handoffy, nadprodukciu a rozpracovanú prácu, ktorá neprináša hodnotu. Optimalizuje flow celého systému, nie iba utilization jednotlivého tímu.

Maximálne vyťaženie každého človeka môže flow zhoršiť, pretože nevzniká rezerva na review, incidenty alebo neplánované závislosti. Lean preto pracuje s WIP limits, malými batchmi a meraním end-to-end lead time-u.

### DevOps-oriented SDLC

DevOps-oriented lifecycle spája development, delivery a operations cez zdieľaný ownership, automation a produkčný feedback. Nástroje ako CI/CD, infrastructure as code a observability podporujú model, ale samy nevytvoria spoluprácu ani zodpovednosť.

Cieľom je zmenšiť batch size, skrátiť feedback a odstrániť handoff, pri ktorom jeden tím optimalizuje release speed a druhý nesie všetok production risk. Bez spoločných cieľov môže automatizácia iba zrýchliť chybný proces.

## 19. Delivery a continuous delivery

Delivery je schopnosť dostať overenú zmenu do stavu pripraveného na bezpečné production nasadenie. Continuous delivery znamená, že tento stav vzniká opakovateľne a často, pričom production release môže zostať business rozhodnutím.

Continuous deployment ide ďalej a úspešné zmeny automaticky nasadzuje do produkcie. Obe praktiky vyžadujú vysokú dôveru v tests, artifact identity, deployment safety a production feedback; rozdiel je v poslednom decision gate-e.

## 20. End-to-end príklad zmeny

Požiadavka hovorí, že používateľ má dostať upozornenie pri neúspešnej platbe. Lifecycle musí najprv definovať, čo je neúspešná platba, aký kanál sa použije, aké sú privacy požiadavky a čo sa stane pri zlyhaní notification providera.

```text
Product requirement a success metric
  ↓
Acceptance criteria, privacy a reliability requirements
  ↓
Návrh payment eventu, notification workflowu a retry contractu
  ↓
Implementácia application kódu, queue a infrastructure
  ↓
Unit, integration, contract a failure tests
  ↓
Build immutable container image a provenance metadata
  ↓
Release approval podľa testov a risku
  ↓
Deployment do stagingu a end-to-end verification
  ↓
Canary rollout do produkcie
  ↓
Sledovanie payment failures, delivery success, latency a duplicate notifications
  ↓
Plný rollout, rollback alebo úprava požiadavky
```

DevOps engineer sa v toku nepodieľa iba na deployment kroku. Ovplyvňuje reprodukovateľnosť buildu, test environments, artifact storage, deployment safety, telemetry, scaling, secret delivery a recovery workflow.

## 21. Feedback loops

Feedback loop je cesta od vykonanej akcie k informácii o jej výsledku. Hodnota feedbacku závisí od rýchlosti, presnosti a od toho, či sa informácia dostane k človeku alebo automation schopnej zmeniť ďalšie rozhodnutie.

Jednotlivé loops odhaľujú odlišné typy problémov:

- **IDE alebo linter — sekundy**: odhaľuje syntax, style a časť statických chýb ešte pred commitom, ale nepozná správanie integrovaného systému.
- **Unit testy — sekundy až minúty**: overujú izolovanú logiku s rýchlym feedbackom, no môžu používať mocks, ktoré nezodpovedajú skutočnej dependency.
- **CI pipeline — minúty**: kombinuje build, tests a policy checks nad konkrétnym revision, pričom dlhá alebo flaky pipeline znižuje frekvenciu používania feedbacku.
- **Integračné prostredie — minúty až hodiny**: overuje interakciu komponentov a configuration, ale môže sa líšiť od produkčnej scale, data a network conditions.
- **Produkčná telemetry — sekundy až dni**: ukazuje reálny traffic, latency, errors a resource behavior, no potrebuje koreláciu s konkrétnou zmenou a správne signal semantics.
- **Používateľská spätná väzba — dni až mesiace**: overuje, či zmena priniesla hodnotu alebo vytvorila nový problém, ale býva oneskorená a ovplyvnená ďalšími faktormi.

Čím neskôr sa chyba objaví, tým viac ďalšej práce už môže stáť na nesprávnom predpoklade. Cieľom však nie je presunúť všetko doľava; performance pod reálnym trafficom alebo skutočný user behavior sa dôveryhodne overujú až v neskorších loops.

## 22. Evidence a quality gates

Quality gate je decision point založený na evidence, nie univerzálna požiadavka na konkrétny nástroj. Gate môže overovať tests, vulnerabilities, artifact signatures, migration compatibility, change approval alebo production health podľa risku zmeny.

Príliš slabý gate prepustí neoverenú zmenu, zatiaľ čo príliš pomalý alebo nerelevantný gate vytvára obchádzanie procesu. Každý gate musí mať ownera, failure semantics, exception lifecycle a pravidelné vyhodnotenie, či skutočne znižuje incident risk.

## 23. Security a compliance v SDLC

Security sa nemá pridávať ako finálny scan pred release-om. Threat modeling, identity, data classification, dependency governance a recovery requirements ovplyvňujú požiadavky a design ešte pred implementáciou.

Compliance potrebuje traceability medzi požiadavkou, zmenou, approvalom, artifactom, deploymentom a prevádzkovým evidence. Samotné splnenie checklistu nepreukazuje bezpečnosť; control musí byť správne implementovaný, monitorovaný a pravidelne overovaný.

## 24. Riziká nesprávneho SDLC

Nesprávny lifecycle často optimalizuje jednotlivú fázu a poškodí celý value stream:

- **Nejasné požiadavky** — tím môže bezchybne vytvoriť funkciu, ktorá nerieši skutočný problém alebo nemá definovaný úspech.
- **Manuálne buildy a deploymenty** — výsledok závisí od lokálneho prostredia a nezdokumentovaných krokov, takže rollback ani audit nemajú spoľahlivý artifact.
- **Dlhé integračné vetvy** — konflikty a nekompatibilné zmeny sa odhalia až po veľkom množstve práce a oprava zasiahne viac tímov naraz.
- **Oddelenie vývoja a prevádzky** — development optimalizuje feature throughput, operations stabilitu a medzi tímami vzniká handoff namiesto spoločného reliability rozhodnutia.
- **Chýbajúca observability** — deployment môže byť technicky úspešný, ale tím nevie zistiť user impact, regresiu alebo postupné zhoršovanie.
- **Chýbajúci retirement proces** — nepoužívaný systém naďalej spotrebúva peniaze, uchováva citlivé dáta a zväčšuje attack surface.

## 25. Troubleshooting delivery lifecycle-u

Pri pomalom alebo nespoľahlivom delivery neoptimalizuj automaticky najviditeľnejší job. Najprv zmeraj celý tok od požiadavky po produkčný feedback a rozdeľ waiting time, active work, rework a failure rate podľa jednotlivých krokov.

```text
požiadavka
→ waiting na rozhodnutie
→ implementation
→ review a test
→ waiting na environment alebo approval
→ deployment
→ production validation
```

Typické symptómy majú odlišné príčiny:

- **Lead time je dlhý, hoci build je rýchly** — hľadaj waiting na review, environment, security approval alebo coordinated release window namiesto ďalšej optimalizácie kompilácie.
- **Pipeline je zelená, production incidenty rastú** — over reprezentatívnosť testov, deployment verification a production signal coverage, pretože gate pravdepodobne nemeria hlavný risk.
- **Rollbacks sú časté a pomalé** — skontroluj artifact identity, data migration compatibility a schopnosť obnoviť predchádzajúcu configuration, nie iba deployment tool.
- **Zmeny sa hromadia do veľkých release-ov** — hľadaj dlhé branches, manuálne gates, nekompatibilné dependencies alebo strach z deploymentu spôsobený slabou observability.

## 26. Časté omyly

### SDLC je iba Waterfall

Waterfall je jeden spôsob organizácie fáz, nie definícia lifecycle-u. Každý software má požiadavky, implementáciu, prevádzku a retirement bez ohľadu na to, či organizácia používa Scrum, Kanban alebo formálny stage-gate proces.

### Deploymentom je práca hotová

Deployment iba mení runtime state. Až production validation a používateľský outcome ukážu, či zmena poskytuje očakávanú hodnotu a či nevytvorila reliability alebo security regresiu.

### Agile znamená bez dokumentácie a plánovania

Agile obmedzuje dokumentáciu a plánovanie, ktoré nevytvárajú hodnotu, ale neodstraňuje potrebu spoločného modelu, acceptance criteria a risk decisions. Bez nich sa tím iba rýchlejšie pohybuje bez overiteľného smeru.

### DevOps začína až pri CI/CD

DevOps ovplyvňuje requirements, architecture, testability, ownership aj production feedback. CI/CD je implementačná capability, ktorá môže podporiť flow, ale nevyrieši nejasnú zodpovednosť alebo konfliktné ciele tímov.

## 27. Kontrolné otázky

1. Prečo SDLC nie je iba proces písania a nasadenia kódu?
2. Ako sa odlišujú build, artifact, release, deployment a rollout?
3. Prečo má artifact zostať rovnaký medzi stagingom a produkciou?
4. Ako production operations vracia informácie do discovery a designu?
5. Aký rozdiel je medzi iterative a incremental developmentom?
6. Prečo krátky sprint automaticky nevytvára krátky feedback loop?
7. Ako quality gate znižuje risk a kedy sa stáva iba bottleneckom?
8. Prečo môže zelená pipeline sprevádzať rast production incidentov?
9. Aké evidence dokazujú, že retirement systému je dokončený?
10. Ktoré časti SDLC ovplyvňuje DevOps engineer a akým mechanizmom?

## 28. Zhrnutie

SDLC pokrýva celý život softvéru od problému po retirement a prepája business outcome s technickým evidence. Jednotlivé fázy nie sú izolované oddelenia; tvoria spätnoväzbový systém, v ktorom každá zmena môže upraviť predchádzajúci predpoklad.

Build, artifact, release, deployment a rollout sú odlišné koncepty s odlišným ownershipom a failure modes. DevOps zlepšuje lifecycle zmenšením batchov, automatizáciou opakovateľnej práce, skrátením feedback loops a zdieľanou zodpovednosťou za produkčný výsledok.

## Glossary impact

Relevantné pojmy: Software Development Life Cycle, discovery, acceptance criteria, build, artifact, release, deployment, rollout, delivery, continuous delivery, continuous deployment, feedback loop, quality gate, maintenance a retirement.

## Primárne zdroje

- [Manifesto for Agile Software Development](https://agilemanifesto.org/)
- [NIST Secure Software Development Framework](https://csrc.nist.gov/pubs/sp/800/218/final)
- [Google Cloud — DevOps capabilities](https://cloud.google.com/architecture/devops)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[↑ Obsah sekcie](README.md) · [Nasledujúca: DevOps →](devops.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
