# Branching strategies

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Git and Automation Basics
- Predpoklady: [Merge a rebase](merge-and-rebase.md), [Konflikty](merge-conflicts.md)
- Súvisiace témy: trunk-based development, Git Flow, release branches, feature flags, CI/CD

## 1. Definícia

Branching strategy je explicitná delivery policy, ktorá určuje, kde vznikajú zmeny, ako dlho sú izolované, kedy sa integrujú, ktorý commit je releasable a ako sa opravy propagujú medzi podporovanými verziami.

Nie je to iba naming convention. Branch topology ovplyvňuje:

- feedback latency — ako rýchlo tím zistí, že dve zmeny spolu nefungujú,
- batch size — koľko práce sa integruje naraz,
- release confidence — či bol nasadzovaný presne testovaný commit a artifact,
- auditability — ako sa dá dohľadať review, approval a pôvod release,
- recovery — ako sa vykoná revert alebo hotfix,
- parallel-version cost — koľko odlišných kódových línií treba udržiavať.

Stratégia je vhodná iba vtedy, keď podporuje reálny release model, CI kapacitu, architektúru systému a organizačné obmedzenia.

## 2. Mentálny model: izolácia verzus integrácia

Každá branch dočasne izoluje zmenu od iných zmien. Izolácia znižuje okamžitý zásah do hlavnej línie, ale vytvára divergence debt.

```text
čas od oddelenia branch
        +
počet paralelných zmien
        +
change coupling
        ↓
riziko neskorého integračného problému
```

Dlhšia branch nie je automaticky zlá. Je však drahšia, pretože:

- merge base sa vzďaľuje od aktuálneho trunku,
- konflikty obsahujú viac nezávislých rozhodnutí,
- testy na branchi nemusia reprezentovať kombináciu s ostatnými zmenami,
- produktové a databázové kontrakty môžu diverzifikovať,
- review narastie do veľkého batchu.

Dobrá stratégia preto minimalizuje čas medzi vytvorením zmeny a jej integráciou do spoločného testovateľného stavu.

## 3. Ciele funkčnej stratégie

Branching strategy má vytvoriť odpoveď na tieto otázky:

1. Ktorá branch alebo commit je source of truth pre ďalší vývoj?
2. Čo znamená „releasable“ a ktoré gates to dokazujú?
3. Ako sa zmena dostane do produkcie bez rekompilovania iného obsahu?
4. Ako sa podporujú staršie verzie?
5. Ako sa produkčný hotfix vráti do všetkých relevantných línií?
6. Kto a čo môže meniť chránené refs?
7. Ktorá merge metóda je povolená a aký auditný význam má výsledný graph?
8. Ako sa stratégia meria a kedy sa má zmeniť?

Stratégia bez týchto odpovedí je iba zvyk, nie kontrolovaný proces.

## 4. Trunk-based development

Trunk-based development používa jednu hlavnú integračnú líniu, typicky `main` alebo `trunk`. Vývojári integrujú malé zmeny veľmi často. Short-lived branches môžu existovať, ale ich účelom je review a krátkodobá izolácia, nie dlhodobý paralelný vývoj.

Typický tok:

```text
malá zmena
→ short-lived branch alebo priamy gated commit
→ automatické checks
→ integrácia do trunku
→ build immutable artifactu
→ promotion artifactu
```

Kľúčové podmienky:

- branch lifetime sa meria skôr v hodinách alebo malom počte dní,
- CI poskytuje rýchly a spoľahlivý feedback,
- neúplné správanie sa izoluje feature flagom alebo kompatibilným interným kontraktom,
- databázové a API zmeny podporujú prechodné obdobie,
- trunk sa opravuje prioritne, ak sa stane červeným,
- release sa oddeľuje od integrácie.

Výhoda nie je „lineárny Git log“. Hlavná výhoda je skoré zistenie integračných problémov a nízka divergence.

Riziká vznikajú, keď tím deklaruje trunk-based development, ale používa:

- pomalé alebo flaky CI,
- veľké pull requests,
- nekompatibilné schema zmeny,
- neudržiavané feature flags,
- manuálne deploymenty bez reprodukovateľného artifactu.

## 5. Short-lived feature branch workflow

Feature branch vytvorí samostatný ref pre jednu logickú zmenu.

```text
main:    A---B---------M
              \       /
feature:       C---D--/
```

Je vhodná na:

- izolované review,
- required approvals,
- branch-specific CI,
- experimentálne zmeny bez priameho zápisu do main,
- automatizované security a quality gates.

Feature branch workflow je kompatibilný s trunk-based development iba vtedy, keď integrácia zostáva častá. Dlhodobo žijúca feature branch sa už správa ako samostatná vývojová línia.

Praktické kontroly:

- maximálny alebo sledovaný branch age,
- limity veľkosti pull requestu,
- pravidelná synchronizácia s trunkom,
- required current-base alebo merge-queue checks,
- automatické mazanie zintegrovaných branches,
- viditeľný owner a dôvod blokovania.

## 6. Dlhodobé feature branches

Dlhodobá branch typicky vzniká, keď feature nemožno bezpečne integrovať po menších častiach. Problém však často nie je Git, ale architecture a delivery design.

Dlhá branch môže signalizovať:

- silne previazaný monolit bez modularity,
- chýbajúce feature flags,
- nemožnosť robiť expand-and-contract migrations,
- nejasné rozdelenie veľkej iniciatívy,
- chýbajúci testovací environment pre priebežný stav,
- kultúru review až na konci práce.

Náprava nie je iba „častejšie rebasovať“. Rebase znižuje textovú divergenciu, ale nevyrieši neskorú behaviorálnu integráciu.

## 7. GitHub Flow a GitLab Flow

Zjednodušený platformový model často vyzerá:

```text
short-lived branch
→ pull/merge request
→ review + CI
→ merge do main
→ build/deploy
```

GitLab Flow môže doplniť release alebo environment-oriented refs podľa konkrétneho delivery modelu, ale samotný názov nezaručuje správny proces.

Dôležité je rozlíšiť:

- source integration — zlučovanie kódu,
- artifact creation — vytvorenie nemenného release kandidáta,
- environment promotion — nasadenie toho istého artifactu,
- release exposure — sprístupnenie používateľom.

Tieto štyri udalosti nemajú byť automaticky reprezentované štyrmi source-code branches.

## 8. Git Flow

Klasický Git Flow používa viac dlhodobých línií:

```text
main/master   produkčné release body
develop       integračná línia budúceho release
release/*     stabilizácia pripravovanej verzie
hotfix/*      urgentná oprava produkčnej verzie
feature/*     vývoj jednotlivých zmien
```

Tento model môže byť opodstatnený, keď:

- produkt sa vydáva v diskrétnych balíkoch,
- existuje dlhá stabilizačná fáza,
- podporuje sa viac inštalovaných verzií,
- release candidate potrebuje samostatnú hardening líniu,
- deployment nie je continuous delivery.

Cena modelu:

- viac merge smerov,
- patch drift medzi `develop`, `main` a release branches,
- vyššie riziko, že oprava chýba v jednej línii,
- neskoršia integračná spätná väzba,
- komplikovanejší automation a release provenance.

Git Flow nie je univerzálny „profesionálnejší Git“. Je to trade-off pre konkrétny release model.

## 9. Release branches

Release branch reprezentuje podporovanú alebo stabilizovanú produktovú líniu, napríklad:

```text
release/2.4
release/3.1-lts
```

Má zmysel, keď treba:

- opravovať produkčnú verziu bez prijatia všetkých nových zmien z main,
- podporovať LTS alebo enterprise edície,
- udržiavať viac aktívnych major/minor verzií,
- vykonávať formálnu release stabilizáciu.

Musí mať definované:

- okamih vytvorenia a source commit,
- povolené typy zmien,
- ownership a approval pravidlá,
- test matrix,
- versioning a tagging,
- dobu podpory a end-of-life,
- smer propagácie opráv.

Príklad pravidla propagácie:

```text
fix vznikne v najstaršej postihnutej podporovanej línii
→ otestuje sa
→ cherry-pick alebo samostatná ekvivalentná zmena do novších línií
→ main
```

Iný tím môže opravovať najprv main a následne backportovať. Dôležitá je konzistentná a auditovateľná policy.

## 10. Hotfix lifecycle

Hotfix nie je iba branch name. Je to riadený incident change flow.

```text
identifikovaný produkčný commit/tag
→ hotfix branch z presného produkčného stavu
→ minimálna oprava + relevantné tests
→ review a emergency approvals
→ nový artifact
→ kontrolovaný rollout
→ spätná integrácia do main a podporovaných release branches
→ odstránenie dočasných bypassov
```

Časté zlyhanie:

```text
hotfix nasadený do produkcie
ale nie je v main
→ nasledujúci release chybu znovu zavedie
```

Hotfix workflow musí tiež evidovať, ktoré bežné gates boli skrátené a ako sa doplnia po stabilizácii incidentu.

## 11. Environment branches

Branches ako `dev`, `test`, `stage` a `prod` sa niekedy používajú na source-code promotion.

```text
main → merge do dev → merge do stage → merge do prod
```

Tento model vytvára riziko, že:

- každé prostredie obsahuje iný commit graph,
- promotion môže vytvoriť nový merge commit,
- testovaný obsah nie je identický s produkčným artifactom,
- environment-specific changes sa miešajú so source code,
- rollback znamená ďalšiu Git integráciu namiesto deployment rozhodnutia.

Preferovaný aplikačný model:

```text
commit
→ build raz
→ immutable artifact s digestom
→ deploy do test
→ ten istý digest do stage
→ ten istý digest do prod
```

Environment branch môže byť legitímna v GitOps repository, kde branch alebo adresár reprezentuje desired deployment configuration. Aj vtedy treba jasne oddeliť application source, artifact identity a environment configuration.

## 12. Feature flags

Feature flag oddeľuje tri udalosti:

```text
integrácia kódu
≠ deployment
≠ release používateľovi
```

Flag môže podporovať:

- skrytie neúplného behavioru,
- canary rollout,
- tenant alebo cohort exposure,
- experiment,
- rýchle operačné vypnutie.

Flag však pridáva runtime state a nové kombinácie systému.

Každý flag potrebuje:

- jednoznačného ownera,
- typ flagu: release, experiment, permission alebo operational,
- bezpečný default,
- expiry alebo removal kritérium,
- observability podľa variantu,
- test coverage relevantných kombinácií,
- ochranu pred client-side manipuláciou pri security rozhodnutiach.

Feature flag nie je authorization mechanizmus, pokiaľ jeho hodnotu nekontroluje dôveryhodná serverová policy.

## 13. Backward-compatible integration

Častá integrácia vyžaduje, aby prechodné commits zostali deployable.

Príklad databázovej expand-and-contract zmeny:

```text
1. pridať nový nullable column alebo nový endpoint
2. nasadiť code, ktorý podporuje starý aj nový model
3. migrovať dáta/consumers
4. prepnúť čítanie a zápis
5. odstrániť starý kontrakt až po potvrdení nepoužívania
```

Podobne pri API:

- najprv rozšíriť provider,
- potom aktualizovať consumers,
- až nakoniec odstrániť starú verziu.

Branching strategy nedokáže kompenzovať breaking changes, ktoré nemožno integrovať po bezpečných krokoch.

## 14. Branch protection

Branch protection je server-side enforcement nad refs. Typické pravidlá:

- zákaz direct push,
- required reviews,
- CODEOWNERS approvals,
- required status checks,
- requirement aktuálnej base alebo merge queue,
- signed commits/tags alebo verified identity,
- zákaz branch deletion,
- zákaz force push alebo jeho silné obmedzenie,
- environment approval pre deployment,
- secret scanning a policy hooks.

Protection má vynucovať skutočné rizikové hranice. Veľké množstvo formálnych checks bez jasného ownershipu môže iba predĺžiť lead time bez zvýšenia kvality.

## 15. Merge metódy a ich kontrakt

### Merge commit

```text
A---B-------M
     \     /
      C---D
```

Zachová parent relationship a branch topology. Uľahčuje revert celej integrácie cez merge commit, ale môže vytvárať hlučný graph pri malých zmenách.

### Squash merge

```text
A---B---S
```

Obsah celej pull request branch sa uloží ako jeden commit. Zjednodušuje main históriu a revert, ale pôvodné commits nie sú ancestors main a ich podpisy sa neprenesú na squash commit.

### Rebase merge

Commity sa replayujú lineárne na nový base. Zachová granularitu, ale vytvorí nové IDs a vyžaduje, aby séria commitov bola sama o sebe zmysluplná.

Tím má zvoliť metódu podľa:

- auditných požiadaviek,
- spôsobu revertovania,
- kvality branch commitov,
- potreby bisectu,
- release-note generation,
- podpisovej a provenance policy.

## 16. Merge queue

Pre-merge CI na jednotlivých branches nemusí otestovať ich výslednú kombináciu.

```text
main = M0
PR A testovaná na M0 → green
PR B testovaná na M0 → green
A sa merge-ne → main = M1
B na M1 môže byť broken
```

Merge queue vytvára dočasného kandidáta z plánovaného poradia integrácie a spustí required checks nad budúcim výsledným stavom.

Queue potrebuje:

- dostatočne rýchle CI,
- kontrolu flaky tests,
- cancellation zastaraných behov,
- prioritizáciu urgentných zmien,
- jasný model batchovania,
- observability queue wait time a failure reason.

Merge queue nerieši neúplné tests; iba testuje presnejší integračný kandidát.

## 17. Release provenance a immutable artifacts

Silná delivery policy prepája:

```text
Git commit/tag
→ CI run
→ build inputs
→ artifact digest
→ deployment record
→ environment
```

Produkčný release má byť spätne dohľadateľný na presný commit a build. Rebuild rovnakého tagu nemusí vytvoriť rovnaký artifact, ak build nie je reprodukovateľný alebo dependencies nie sú pinované.

Preto stratégia nemá hovoriť iba „nasadzujeme z main“. Má definovať:

- ktorý commit bol vybraný,
- ktorý CI run artifact vytvoril,
- ktorý digest bol promovovaný,
- kto deployment schválil,
- ako sa vykoná rollback na predchádzajúci digest.

## 18. Compliance a segregácia povinností

Regulované prostredie môže vyžadovať:

- oddelenie autora, reviewera a deployera,
- povinné approvals,
- nemennú audit trail,
- podpísané release tags,
- kontrolované emergency bypassy,
- retention build a deployment evidence.

To neznamená automaticky potrebu mnohých dlhodobých branches. Segregácia sa môže implementovať serverovou policy, CI identities a environment approvals nad jednou integračnou líniou.

## 19. Branching strategy pre monorepo

V monorepe jedna branch často obsahuje zmeny viacerých komponentov. Stratégia musí doplniť:

- path-based ownership,
- affected-change detection,
- dependency-aware CI,
- atomic cross-component changes,
- koordinované versioning/release pravidlá.

Dlhodobá branch v monorepe zvyšuje divergence pre veľkú časť systému. Preto je mimoriadne dôležitý rýchly selective CI a malé changesets.

## 20. Branching strategy pre viac podporovaných verzií

Ak systém podporuje napríklad verzie `2.x` a `3.x`, treba evidovať patch matrix:

| Oprava | main/4.x | release/3.x | release/2.x |
|---|---|---|---|
| CVE fix | required | required | required do EOL |
| nová feature | áno | nie | nie |
| dependency update | podľa kompatibility | podľa policy | iba security |

Každý backport má byť samostatne buildnutý a testovaný. Rovnaký patch text nemusí mať rovnaké runtime dôsledky v odlišnej verzii.

## 21. Výber stratégie podľa kontextu

Rozhodovacie faktory:

- release cadence — viackrát denne verzus štvrťročné balíky,
- počet podporovaných verzií — jedna produkčná línia verzus LTS matrix,
- deployment model — SaaS, mobile, embedded, on-premise,
- CI duration a spoľahlivosť,
- veľkosť a coupling zmien,
- databázové a API compatibility schopnosti,
- regulačné approvals,
- tímová topológia a ownership,
- schopnosť používať feature flags,
- incident a hotfix požiadavky.

Príklady:

- SaaS služba s automatizovaným CI/CD — trunk-based, short-lived branches, merge queue, immutable artifact promotion.
- Desktop produkt s kvartálnymi releases a dlhšou podporou — main plus kontrolované release branches.
- Embedded produkt s certifikovanými verziami — dlhodobé maintenance lines, prísne backport a evidence rules.

## 22. Baseline pre modernú službu

Rozumný východiskový model:

```text
main je integračný source of truth
short-lived feature branches
required review a automatické checks
merge queue pri paralelnej integrácii
jedna konzistentná merge metóda
build immutable artifactu z chráneného commitu
promotion toho istého digestu
feature flags pre oddelenie deploymentu a release
release branches iba pre reálne podporované verzie
explicitný hotfix propagation workflow
```

Baseline sa má upraviť podľa meraných problémov, nie podľa popularity konkrétneho workflow názvu.

## 23. Metriky stratégie

Sleduj najmenej:

- branch age — čas od vytvorenia po integráciu,
- pull request cycle time,
- veľkosť zmien,
- čas čakania na review a CI,
- merge queue wait time,
- conflict a rework rate,
- percento failed integrations,
- change failure rate,
- revert/hotfix rate,
- počet a vek aktívnych release branches,
- backport lead time,
- čas, počas ktorého je trunk broken.

Metrika má viesť k systémovej otázke. Napríklad vysoký branch age môže byť spôsobený pomalým review, flaky CI, príliš veľkou zmenou alebo chýbajúcou kompatibilnou migráciou.

## 24. Anti-patterny

### Branch per environment pre application source

Mieša integráciu kódu s promotion a oslabuje artifact identity.

### Dlhodobá integračná branch bez jasného dôvodu

Vytvára druhý trunk a odkladá spätnú väzbu.

### Permanentný emergency bypass

Dočasné vypnutie protections sa stane neauditovanou normou.

### Hotfix iba v produkčnej branchi

Oprava sa stratí pri ďalšom release.

### Feature flag bez removal lifecycle

Runtime komplexita a neotestované kombinácie rastú bez limitu.

### Required checks, ktoré netestujú výsledný merge candidate

Green PR môže po integrácii rozbiť main.

### Stratégia kopírovaná bez kontextu

Git Flow, trunk-based ani squash merge nie sú správne samy osebe. Správnosť závisí od delivery systému.

## 25. Diagnostika nefunkčnej stratégie

Symptóm: merge conflicts a release chyby rastú.

1. Zmeraj branch age a veľkosť changesets.
2. Zisti, kedy bola zmena naposledy testovaná s aktuálnym trunkom.
3. Porovnaj PR CI commit s reálne merge-nutým commitom.
4. Over flaky tests a priemerný CI čas.
5. Zmapuj počet aktívnych release línií a backport smerov.
6. Skontroluj, či environment promotion používa rovnaký artifact digest.
7. Zisti, koľko hotfixov chýbalo v main alebo inej podporovanej branchi.
8. Identifikuj feature flags bez ownera a expiry.
9. Preskúmaj, ktoré protections sa pravidelne obchádzajú a prečo.
10. Zmeň jednu policy, meraj dopad a až potom pokračuj.

## 26. Časté omyly

### „Trunk-based znamená, že všetci pushujú priamo do main“

Nie. Môže používať short-lived branches, pull requests aj merge queue. Rozhodujúca je častá integrácia do jednej hlavnej línie.

### „Git Flow je bezpečnejší, lebo má viac branches“

Viac branches pridáva explicitné línie, ale aj merge, drift a backport riziko.

### „Branch protection nahrádza CI/CD design“

Nie. Chráni ref updates, ale sama nevytvára kvalitné tests, artifact provenance ani bezpečný deployment.

### „Environment branch dokazuje, čo je nasadené“

Iba ak deployment systém striktne používa a eviduje konkrétny commit. Artifact digest a deployment record sú presnejšie dôkazy.

### „Feature flag umožňuje commitnúť ľubovoľne rozbitý kód“

Disabled path nesmie poškodiť build, migrations, security ani spoločné runtime komponenty.

### „Release branch potrebuje každý projekt“

Nie. Jej cena má zmysel iba pri skutočnej paralelnej podpore alebo stabilizačnej potrebe.

## 27. Kontrolné otázky

1. Prečo je branching strategy súčasť delivery architecture?
2. Aký je rozdiel medzi krátkou izoláciou a dlhodobou divergenciou?
3. Čo musí platiť, aby short-lived feature branches zostali trunk-based?
4. Kedy má Git Flow alebo release branch reálne opodstatnenie?
5. Prečo source-code environment branches oslabujú immutable promotion?
6. Ako feature flag oddeľuje integráciu, deployment a release?
7. Čo presne rieši merge queue?
8. Ako sa hotfix propaguje späť do všetkých relevantných línií?
9. Aký je rozdiel medzi branch protection a release provenance?
10. Ktoré metriky ukazujú, že stratégia odkladá integráciu?

## Glossary impact

Relevantné pojmy: branching strategy, trunk-based development, feature branch, Git Flow, release branch, hotfix branch, feature flag, branch protection, merge queue, squash merge, artifact promotion, release provenance.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Konflikty](merge-conflicts.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Monorepo vs. multirepo →](monorepo-vs-multirepo.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
