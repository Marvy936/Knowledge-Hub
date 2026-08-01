# Monorepo vs. multirepo

Repository topology určuje, ktoré source subjects, ownership boundaries a changes sa verzujú spolu. **Monorepo** ukladá viac komponentov alebo služieb v jednom repository a commit graph-e. **Multirepo** ich rozdeľuje do viacerých repositories. Hybrid kombinuje obe podľa change a governance boundaries.

Monorepo neznamená automaticky jeden build alebo jeden deploy. Multirepo neznamená automaticky nezávislé služby. Skutočná nezávislosť závisí od contracts, build graphu, release procesu a runtime coupling.

Pri monorepe môže jeden atomic commit zmeniť library, consumer a tests naraz. Ref transition poskytne spoločný source snapshot. Cena je väčší repository scale, zložitejšie ownership rules, selective build a potreba presného dependency graphu.

Pri multirepe má každý komponent vlastný ref lifecycle, permissions a release cadence. Cross-repository change však nie je atomic. Potrebuje kompatibilné poradie, dočasné expand/contract obdobie, versioned contracts alebo koordinovaný rollout.

Neutrálny príklad zmeny API:

```text
producer pridá nový optional field
→ publikuje kompatibilný contract
→ consumers sa postupne aktualizujú
→ producer začne field vyžadovať až po migrácii
```

V monorepe možno source changes commitnúť spolu, ale production deployments stále nemusia byť simultánne. V multirepe sa source changes prirodzene delia, preto je compatibility contract ešte viditeľnejší.

Rozhodovanie má vychádzať z **change coupling**: ktoré súbory, komponenty a tímy sa často menia ako jedna business zmena. Ďalšie faktory sú ownership, security boundaries, build scale, tooling, artifact promotion, dependency update automation a compliance.

Repository boundary nie je service boundary ani team boundary. Jedno repository môže obsahovať mnoho tímov a jedna služba môže závisieť od viacerých repositories. Topology je optimalizácia toku zmien a governance, nie architektonická pravda sama o sebe.

Atlas change `ORD-8421` upravuje API schema, service config, shared client library a deployment policy. Otázka repository modelu nie je ideologická. Ide o to, ktoré zmeny musia byť atomické, kto vlastní hranice, ako sa počíta affected graph a ako sa verzujú a publikujú outputs.

## Change coupling ako hlavný vstup

Ak producer a consumer musia byť zmenené spolu, monorepo môže umožniť jeden commit a jednu integration decision. Ak majú nezávislý release lifecycle, ownership a compliance boundary, multirepo môže byť vhodnejšie.

Treba rozlíšiť:

```text
source coupling
build coupling
release coupling
runtime coupling
data-contract coupling
organizational ownership
```

Dve služby môžu byť runtime coupled, ale nemusia byť v jednom repository. Naopak shared schema a generated clients môžu mať silný source coupling aj pri oddelenom deploymente.

## Monorepo

Monorepo ukladá viac komponentov do jedného repository. Výhody vznikajú iba so správnym toolingom: affected builds, ownership paths, cache, sparse checkout a hermetic dependencies.

Atomický commit môže zmeniť schema, server aj consumer tests. To znižuje transition gap, ale jeden commit stále nevytvára atomický production deployment. Runtime compatibility musí byť navrhnutá pre postupné rollouty.

Veľký repository bez build graphu môže spúšťať všetko pri každej zmene a vytvoriť pomalý feedback. Monorepo nie je automaticky jednoduchšie; presúva zložitosť do repository tooling a governance.

## Multirepo

Multirepo dáva komponentom oddelené histories, permissions a release cadence. Contract change sa koordinuje cez versionované artifacts a compatibility matrix:

```text
schema package 2.3.0
→ producer supports 2.2 a 2.3
→ consumers adopt 2.3 postupne
→ telemetry potvrdí retirement 2.2
```

Cross-repo change nemá jeden atomic commit. Potrebuje orchestrated sequence, dependency bot, integration environment alebo contract tests. Výhodou je jasnejší blast radius a ownership; nevýhodou vyššia coordination latency.

## Hybrid

Organizácia môže používať doménové monorepos a samostatné platform repositories. Dôležité je, aby hranice sledovali change coupling, nie historické org chart boxes.

Generated clients sa nemajú kopírovať ručne medzi repositories. Publikujú sa ako immutable artifacts s provenance a version contractom. Git submodules alebo subtree môžu riešiť source composition, ale prinášajú vlastný ref a update lifecycle.

## Permissions a secrets

Monorepo s citlivým pathom môže vyžadovať path-based ownership, no Git clone typicky poskytne read access k celej histórii. Ak komponent obsahuje právne alebo bezpečnostne oddelené source data, samostatné repository môže byť potrebné.

Secrets nepatria ani do jedného modelu. Repository boundary nie je secret vault.

## CI graph

Monorepo pipeline musí určiť affected targets podľa dependency graphu, nie iba podľa changed paths. Zmena shared library môže ovplyvniť desiatky consumers. Cache key musí zahŕňať všetky relevantné inputs.

Multirepo pipeline musí vedieť, s ktorými versions dependencies testuje. „Latest“ je mutable a nereprodukovateľné. Integration evidence má explicitný matrix subject.

## History a scale

Veľkosť `.git` závisí od histórie veľkých blobs a počtu objektov, nie iba aktuálneho working tree. Partial clone, sparse checkout a LFS môžu znížiť client cost, ale komplikujú tooling a offline behavior.

Rozdelenie monorepa neskôr mení commit IDs a history mapping. Zlúčenie repositories potrebuje collision a provenance plan. Repository topology je dlhodobý architectural decision, hoci nie nezvratný.

## Praktický rozbor affected graphu a cross-repository transitionu

Changed paths nie sú dependency graph. V monorepe môže zmena v `libs/contracts` ovplyvniť služby, ktoré sa samy v diff-e nenachádzajú. Minimálny observation je:

```bash
base=$(git merge-base origin/main HEAD)
git diff --name-status "$base" HEAD
git diff --name-only "$base" HEAD > /tmp/changed-paths.txt
```

Tento zoznam je input pre build-graph tool, nie konečný affected set. Tool musí poznať edges, napríklad:

```text
libs/contracts
├── services/orders
├── services/payments
└── clients/web
```

Ak cache key používa iba hash vlastného directory, consumer môže reuse-nuť output vytvorený so starou shared library. Správny key zahŕňa transitive source/dependency/toolchain inputs alebo používa hermetic action graph.

Atomic source commit v monorepe stále neznamená atomic runtime. Predstav si commit, ktorý pridá optional response field a aktualizuje web client. Ak server deployne prvý, starý client musí field ignorovať. Ak client deployne prvý, starý server nesmie spôsobiť failure. Compatibility matrix je potrebný aj pri spoločnom commit-e.

Multirepo transition zapisuje versions explicitne:

```text
contract artifact: orders-schema 2.3.0 @ digest D23
producer tested with: 2.2.0, 2.3.0
consumer-web tested with: 2.2.0, 2.3.0
consumer-batch tested with: 2.2.0 only
retirement gate: no 2.2.0 traffic for 14 days
```

Pipeline jednotlivého repository má uložiť dependency lock/digest. Testovanie proti `latest` nevie spätne určiť, ktorý contract bol použitý. Cross-repo coordinator alebo release manifest potom skladá immutable versions do jedného integration subjectu.

Pri rozhodovaní o rozdelení zmeraj reálne change coupling:

```text
koľko PRs pravidelne mení oba komponenty
koľko incidentov vzniká z compatibility gapu
koľko CI času spotrebuje nepresný affected graph
kto potrebuje read/write access k celej histórii
či release a compliance lifecycle sú naozaj oddelené
```

Repo split nie je iba presun directories. Mení commit IDs, CODEOWNERS, secrets/tokens, CI provenance, package coordinates, issue links a release automation. Migračný plan potrebuje source-history mapping a obdobie, v ktorom staré repository už nie je writer.

Generated code sa publikuje ako artifact s source schema digestom a generator version. Ručné kopírovanie medzi repositories vytvára hidden source a znemožňuje zistiť, či consumer používa správnu generation.

## Incident: samostatné repositories vytvoria nekompatibilný rollout

Schema repo publikuje breaking change ako minor version. Service repo ju adoptuje, client repo nie. Každá pipeline je zelená proti vlastným fixtures, ale production client zlyhá.

Root cause nie je multirepo samo. Chýba versioned contract, consumer compatibility test a rollout sequence. Oprava pridá provider/consumer matrix a additive migration. Rovnaký problém by mohol vzniknúť aj v monorepe, ak atomický source commit vedie k neatomickému runtime rollout-u.

## Zhrnutie

Monorepo optimalizuje atomické source changes a spoločné tooling; multirepo optimalizuje nezávislé ownership a release boundaries. Rozhodnutie sa opiera o change coupling, permissions, CI graph, artifact versioning a runtime transition model. Repository boundary nikdy nenahrádza compatibility design.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Branching strategies](branching-strategies.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Bash automation →](bash-automation.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
