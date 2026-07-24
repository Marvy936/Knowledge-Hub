# Monorepo vs. multirepo

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Git and Automation Basics
- Predpoklady: [Branching strategies](branching-strategies.md), [Value Stream Mapping](../00-foundations/value-stream-mapping.md)
- Súvisiace témy: repository boundaries, ownership, CI graph, dependency management, platform engineering

## 1. Definícia

Monorepo ukladá viac projektov, služieb, knižníc alebo nástrojov do jedného Git repository. Multirepo ich rozdeľuje medzi viac samostatných repositories.

Repository topology určuje fyzickú hranicu verziovania a zmeny. Neurčuje automaticky:

- počet deployable services,
- runtime architektúru,
- počet tímov,
- počet release trains,
- jeden alebo viac programovacích jazykov,
- monolit verzus microservices.

Monorepo môže obsahovať stovky nezávisle deployovaných služieb. Multirepo môže obsahovať jeden silne previazaný produkt rozdelený do desiatok repositories.

Rozhodnutie preto musí vychádzať z change coupling, ownershipu, security boundaries, dependency modelu a delivery topology, nie zo sloganu „jeden repo je jednoduchší“ alebo „jedna služba = jedno repo“.

## 2. Mentálny model: repository ako hranica zmeny

Repository definuje spoločný priestor pre:

```text
commit graph
refs a branching policy
review a approvals
CI entry point
permissions
hooks a server-side policy
history retention
```

Otázka nie je iba „koľko súborov je spolu“. Dôležitejšie je:

```text
ktoré zmeny musia byť koordinované
ktoré zmeny majú byť atomické
ktoré dependencies majú byť viditeľné
ktoré hranice musia byť bezpečnostne oddelené
```

Dobrá repository boundary znižuje celkový coordination cost. Nevhodná boundary iba presunie komplexitu:

- z Git merge do package versioningu,
- z jednej CI pipeline do cross-repo orchestration,
- z path ownershipu do repository permissions,
- z atomic commitu do backward-compatible rolloutov.

## 3. Štyri hranice, ktoré sa nesmú zamieňať

### Repository boundary

Určuje, čo môže byť súčasťou jedného Git commitu a jednej ref policy.

### Build boundary

Určuje, čo sa kompiluje, testuje alebo balí ako jeden target. Jedno repo môže mať tisíce build targets.

### Deployment boundary

Určuje, čo možno nasadiť nezávisle. Monorepo nemusí znamenať jeden deployment.

### Ownership a security boundary

Určuje, kto môže čítať, meniť, schvaľovať alebo prevádzkovať konkrétnu oblasť. Path-based review nie je to isté ako repository-level confidentiality.

Architektúra má tieto hranice navrhovať vedome. Ich automatické zrovnanie môže byť jednoduché pre malý projekt, ale vo väčšom systéme často vytvára zbytočné coupling.

## 4. Monorepo model

Príklad:

```text
repo/
├── services/
│   ├── api/
│   ├── worker/
│   └── billing/
├── libraries/
│   ├── auth/
│   └── observability/
├── infrastructure/
├── tools/
└── docs/
```

Jeden commit môže meniť viac častí systému:

```text
API contract
+ producer implementation
+ consumer implementation
+ tests
+ deployment config
```

To umožňuje atomickú source zmenu. Neznamená to však, že všetky komponenty budú naraz buildnuté, versionované alebo nasadené.

## 5. Multirepo model

Príklad:

```text
api-repo
worker-repo
billing-repo
auth-library-repo
infrastructure-repo
platform-tools-repo
```

Každé repo má vlastný:

- commit graph,
- branch policy,
- permissions,
- CI/CD lifecycle,
- version a release history,
- issue a review context.

Cross-repo zmena nemôže byť jeden Git commit. Musí byť rozdelená na kompatibilnú sekvenciu alebo koordinovanú release transakciu.

## 6. Atomická zmena

Atomická repository zmena znamená, že jeden commit reprezentuje konzistentný source snapshot viacerých komponentov.

Monorepo:

```text
commit X:
- provider pridá nový field
- consumer začne field používať
- tests pokrývajú obidve strany
```

Výhoda:

- review vidí celý intent,
- bisect nájde jeden prechodový bod,
- CI môže testovať presnú kombináciu,
- refactoring nemusí dočasne publikovať intermediary package.

Riziko:

- ak komponenty deployujeme nezávisle, source atomicity nezaručuje deployment atomicity,
- provider a consumer sa môžu v produkcii aktualizovať v opačnom poradí,
- jeden commit môže obsahovať príliš široký blast radius.

Preto aj monorepo potrebuje backward-compatible deployment design.

## 7. Kompatibilná cross-repo zmena

Multirepo typicky používa expand-and-contract postup:

```text
1. provider pridá backward-compatible contract
2. provider publikuje nový immutable artifact
3. consumers adoptujú novú version
4. telemetry potvrdí nepoužívanie starého contractu
5. provider odstráni starý contract
```

Tento proces má vyšší coordination overhead, ale podporuje nezávislé release lifecycles a núti explicitné rozhrania.

Cross-repo zmenu možno koordinovať cez:

- issue alebo change plan s dependency graphom,
- release manifest,
- package registry,
- contract tests,
- automated dependency update pull requests,
- environment integration tests,
- orchestration pipeline.

„Nie je atomická“ neznamená „nedá sa spraviť bezpečne“. Znamená to, že atomicitu musí nahradiť compatibility a orchestration model.

## 8. Change coupling ako hlavný signál

Change coupling meria, ako často sa komponenty menia spolu pre jeden business intent.

Silné signály pre spoločnú repository boundary:

- rovnaké pull requests často menia oba komponenty,
- interfaces sa vyvíjajú koordinovane,
- refactoring pravidelne prekračuje hranice,
- komponenty používajú spoločné tooling a test fixtures,
- oddelené releases neprinášajú hodnotu.

Silné signály pre oddelenie:

- komponenty majú stabilný versioned contract,
- releases sú nezávislé,
- read access musí byť oddelený,
- zmeny sa koordinujú zriedka,
- lifecycle alebo compliance je zásadne odlišný.

Organizačný diagram je slabší signál než dlhodobý change coupling. Tímy sa reorganizujú; dependency a domain boundaries bývajú stabilnejšie.

## 9. Dependency model v monorepe

Monorepo môže používať source-level dependencies:

```text
service A target
→ library B target
→ generated schema C
```

Potrebný je autoritatívny dependency graph, ktorý odpovedá:

- ktorý target závisí od ktorých vstupov,
- ktoré tests validujú daný target,
- ktoré runtime artifacts vznikajú,
- ktoré environment/config dependencies existujú,
- čo ovplyvní zmena spoločného tooling.

Graph môže byť deklarovaný build systémom alebo odvodený, ale musí byť overiteľný. Chybný graph vytvorí false green pipeline, pretože affected-change detection vynechá potrebný build alebo test.

## 10. Dependency model v multirepe

Multirepo potrebuje explicitný artifact contract:

```text
source repo
→ build
→ immutable package/image/schema
→ registry
→ consumer dependency declaration
```

Dôležité mechanizmy:

- immutable versions alebo digests,
- semantic versioning iba tam, kde contract semantics skutočne zodpovedajú SemVer,
- lockfiles a dependency pinning,
- deprecation windows,
- compatibility matrix,
- provenance a signature verification,
- update automation.

Anti-pattern:

```text
consumer build vždy stiahne latest z main iného repo
```

Taký build nie je reprodukovateľný a jeho výsledok závisí od času.

## 11. CI topology v monorepe

Naivný model:

```text
každý commit → build a test všetkého
```

je jednoduchý, ale pri raste vedie k dlhému feedbacku a vysokej spotrebe compute.

Škálovateľný model:

```text
changed paths
→ dependency graph
→ affected targets
→ cache lookup
→ parallel build/test
→ required global checks
```

Potrebné vlastnosti:

- hermetic alebo dostatočne deterministické targets,
- presné cache keys,
- remote cache a execution podľa potreby,
- test sharding,
- cancellation zastaraných behov,
- merge queue,
- pravidelné širšie validation runs.

Selective CI je optimalizácia correctness systému, nie iba výkonová funkcia. Musí sa testovať, že pri zmene dependency sa spustia všetci consumers.

## 12. False green riziko v affected detection

Príklad:

```text
shared config generator sa zmení
ale dependency graph ho neeviduje ako input služby A
→ služba A sa netestuje
→ pipeline green
→ produkčný artifact je chybný
```

Ochrany:

- graph conformance tests,
- periodic full builds,
- shadow comparison selective verzus full run,
- explicitné owners spoločných rules,
- conservative fallback pri neznámej zmene,
- telemetry cache hitov a skipped targets.

Optimalizácia nesmie potichu meniť required validation contract.

## 13. CI topology v multirepe

Každé repo má lokálnu pipeline, ale systémová kompatibilita vzniká až medzi artifacts.

Potrebné vrstvy:

- unit a component tests v source repo,
- contract tests producer/consumer,
- package publishing pipeline,
- dependency update automation,
- integration environment alebo ephemeral test environment,
- cross-repo release manifest,
- end-to-end validation kritických flows.

Cross-repo trigger bez jasného artifactu môže vytvoriť retry loops a nejasný provenance chain. Lepší trigger nesie konkrétnu version alebo digest.

## 14. Ownership

Monorepo používa path-based ownership:

```text
/services/api/       @api-team
/libraries/auth/      @identity-team
/infrastructure/      @platform-team
/build-rules/         @developer-platform
```

Ownership môže riadiť:

- required reviews,
- triage,
- documentation responsibility,
- on-call mapping,
- deprecation approvals.

CODEOWNERS však typicky nie je read-access boundary. Používateľ s prístupom do private monorepa môže vidieť všetky paths.

Multirepo prirodzene poskytuje repository-level permissions, ale cross-repo maintainers a shared tooling môžu vyžadovať široký access.

## 15. Security a confidentiality boundary

Silný dôvod na oddelené repo:

- rozdielne právne entity alebo externí partneri,
- export-control alebo customer-specific source,
- vysoko citlivé security components,
- need-to-know read access,
- odlišná retention alebo compliance policy.

Path review rules nie sú náhradou za repository-level confidentiality, pokiaľ platforma neposkytuje skutočné path-level read isolation.

Naopak, nadmerné rozdelenie pre domnelú bezpečnosť môže vytvoriť token sprawl, duplicate pipelines a neprehľadné dependencies. Boundary má zodpovedať konkrétnemu threat modelu.

## 16. Branching a merge queue v monorepe

Monorepo typicky používa jednu hlavnú integračnú branch, ale zmeny môžu ovplyvňovať rôzne subsets systému.

Potrebné sú:

- short-lived branches,
- path-aware required reviews,
- affected checks,
- merge queue testujúca kombináciu paralelných changes,
- kontrola spoločných root files,
- limit veľkých mechanických refactorov.

Zmena centrálneho build rule môže mať väčší blast radius než zmena jednej služby, aj keď diff obsahuje menej riadkov. Risk-based CI nemá hodnotiť iba počet zmenených files.

## 17. Versioning v monorepe

Monorepo nemusí používať jednu version pre všetko.

### Unified versioning

Všetky komponenty zdieľajú release version.

Vhodné pre jeden produkt alebo SDK balík, ktorý sa vydáva spolu.

### Independent versioning

Každý package alebo service má vlastnú version a release lifecycle.

Vyžaduje:

- affected package detection,
- changelog/version metadata,
- dependency version updates,
- release automation.

### Commit-based identity

Internal artifacts môžu používať commit SHA plus build metadata alebo immutable digest.

### Release manifest

```yaml
source_commit: abc123
artifacts:
  api: sha256:...
  worker: sha256:...
  web: sha256:...
```

Manifest oddeľuje spoločný source snapshot od nezávislých runtime artifacts.

## 18. Versioning v multirepe

Každé repo má vlastnú history a versions. Systémový release preto potrebuje bill of materials:

```yaml
release: 2026.07.24
components:
  api: 3.8.1
  worker: 2.4.0
  web: 5.12.3
```

Bez manifestu je ťažké presne reprodukovať environment alebo incident state.

Version string sama nestačí. Potrebné sú:

- artifact digest,
- source commit,
- build provenance,
- dependency lock state,
- deployment record.

## 19. Release coupling

Dva komponenty môžu byť v rovnakom repo, ale release-núť sa nezávisle. Dva komponenty v rôznych repos môžu byť prakticky viazané na jeden release train.

Sleduj:

- ako často musia byť nasadené spolu,
- či majú backward-compatible contract,
- či rollback jedného vyžaduje rollback druhého,
- či jeden deployment blokuje druhý,
- či environment manifest povoľuje ľubovoľné kombinácie.

Repository topology nemá zakrývať skutočný release coupling.

## 20. Developer experience v monorepe

Výhody:

- jeden clone a search scope,
- jednotný onboarding,
- lokálne cross-component refactoringy,
- spoločné tooling,
- jednoduchšia navigácia medzi producerom a consumerom.

Náklady:

- veľký checkout,
- pomalý `status` alebo IDE indexing,
- zložitý local environment,
- preťaženie informáciami,
- central tooling ako kritická dependency.

Riešenia:

- sparse checkout,
- partial clone,
- workspace/project views,
- target-oriented commands,
- local/remote cache,
- developer portal a ownership metadata.

## 21. Developer experience v multirepe

Výhody:

- menší checkout a jasný scope,
- jednoduchší lokálny build jedného componentu,
- prirodzený repository ownership.

Náklady:

- viac clones a credential contexts,
- zložitejšie code search,
- rozdielne commands a conventions,
- dependency updates cez viac pull requests,
- ťažší cross-repo refactoring.

Platform engineering môže znížiť drift cez:

- reusable CI workflows,
- repository templates,
- centralized policy,
- dependency bots,
- organization-wide code search,
- bootstrap CLI.

## 22. Shared tooling

Monorepo podporuje centralizované:

- linting a formatting rules,
- build macros,
- test harnesses,
- code generation,
- dependency policy,
- security scanning.

Riziko:

```text
jedna zmena root toolchainu
→ ovplyvní celý repository
```

Potrebné sú staged migrations, compatibility obdobie, owner a rollback.

Multirepo môže používať:

- versioned reusable workflows,
- shared packages,
- central runner images,
- policy-as-code service.

Ak sa shared config kopíruje, vzniká verzionovaný drift bez viditeľnej dependency.

## 23. Git performance

Veľký repository môže mať problém s:

- počtom objects,
- veľkosťou packfiles,
- počtom paths v indexe,
- checkout a status časom,
- history traversal,
- veľkými binaries,
- server-side fetch negotiation.

Mechanizmy:

```bash
git clone --filter=blob:none <url>
git sparse-checkout init --cone
git sparse-checkout set services/api libraries/auth
```

Ďalšie optimalizácie:

- commit-graph,
- multi-pack-index,
- filesystem monitor,
- scalar alebo platform-specific large-repo tooling,
- Git LFS pre vhodné binaries.

Technická optimalizácia však nemá ospravedlniť bezhraničné ukladanie generated artifacts a build outputs do Git history.

## 24. Binaries a generated artifacts

Repository nie je všeobecný package registry.

Preferuj:

- reprodukovateľný build zo source,
- artifact registry,
- object storage,
- package registry,
- Git LFS iba pri jasnom ownership a lifecycle.

Riziká veľkých binaries v Git:

- history rastie aj po zmazaní súčasnej verzie,
- clone a backup sa predražujú,
- diff/review má malú hodnotu,
- cleanup vyžaduje history rewrite.

Generated file môže byť commitovaný, ak je potrebný pre consumers alebo bootstrap, ale musí mať deterministický generator a validation, že je synchronizovaný so source.

## 25. Submodules, subtrees a vendoring

Tieto mechanizmy nerobia z viacerých repositories monorepo.

### Submodule

Superproject uchováva gitlink na konkrétny commit iného repo. Poskytuje explicitné pinning, ale samostatný lifecycle, permissions a clone/update workflow zostáva.

### Subtree

Kopíruje history alebo obsah iného projektu do podadresára a synchronizuje ho explicitnými operáciami.

### Vendoring

Uloží dependency source alebo artifact do repository podľa vlastného update procesu.

Každý model má trade-off medzi reprodukovateľnosťou, update friction a ownershipom.

## 26. Hybridný model

Veľká organizácia často používa viac domain monorepos:

```text
commerce-platform-monorepo
identity-platform-monorepo
mobile-monorepo
infrastructure-config-repo
public-sdk-repos
```

Hybridný model môže:

- zoskupiť silne coupled komponenty,
- zachovať security boundaries,
- oddeliť open-source a interný kód,
- obmedziť blast radius tooling,
- znížiť počet cross-repo transakcií v rámci domény.

Cieľom nie je minimalizovať počet repositories. Cieľom je minimalizovať náklady hraníc bez straty potrebnej izolácie.

## 27. Kedy preferovať monorepo

Silné signály:

- časté cross-component changes,
- veľké interné refactoringy,
- spoločné language/toolchain ekosystémy,
- potreba jedného review contextu,
- prijateľný spoločný read access,
- ochota investovať do build graphu, cache a platform tooling,
- produkt sa vyvíja ako koordinovaný celok.

Monorepo nie je vhodné iba preto, že „všetko je jednoduchšie nájsť“. Bez tooling investície sa jednoduchosť rýchlo stratí.

## 28. Kedy preferovať multirepo

Silné signály:

- stabilné versioned contracts,
- nezávislé product a release lifecycles,
- rozdielne confidentiality alebo compliance boundaries,
- externí contributors alebo partneri,
- výrazne odlišné technologické stacky a tooling,
- veľmi nízky change coupling,
- samostatné open-source projekty.

Multirepo nie je vhodné iba preto, že systémy sú microservices. Silne coupled microservices v oddelených repos môžu vytvoriť distribuovaný monolit s vysokým coordination cost.

## 29. Rozhodovací rámec

Pre každý kandidátny boundary zodpovedz:

1. Ako často sa komponenty menia v jednom business change?
2. Potrebujú source-atomickú zmenu?
3. Môžu sa nasadzovať v ľubovoľnom poradí?
4. Majú stabilný backward-compatible contract?
5. Kto potrebuje read a write access?
6. Aké approvals alebo retention policy sa líšia?
7. Ako vznikajú a publikujú artifacts?
8. Ako sa vypočíta affected test/build set?
9. Ako sa vykoná cross-boundary refactoring?
10. Aký je incident a rollback model?
11. Kto vlastní shared tooling?
12. Aký je očakávaný rast source, history a tímov?

Rozhodnutie zdokumentuj ako architecture decision so signálmi, trade-offmi a podmienkami pre budúce prehodnotenie.

## 30. Metriky po rozhodnutí

Sleduj:

- cross-repo pull requests na jednu business zmenu,
- čas od producer change po adoption consumers,
- dependency version drift,
- CI feedback time,
- cache hit rate,
- percento full verzus selective builds,
- false-green incidents spôsobené dependency graphom,
- branch a pull-request cycle time,
- počet duplicate CI/tooling configs,
- čas cross-component refactoringu,
- počet emergency coordination releases,
- clone/status/build performance,
- ownership a approval wait time.

Metrika nehovorí automaticky, že treba migrovať. Ukazuje, kde repository boundary vytvára náklady.

## 31. Migrácia multirepo → monorepo

Potrebný plán:

1. Definovať scope a canonical histories.
2. Rozhodnúť, či zachovať úplnú history alebo importovaný snapshot.
3. Vytvoriť directory a ownership taxonomy.
4. Zjednotiť build a dependency graph.
5. Zachovať attribution, tags a release provenance.
6. Migrovať CI po komponentoch.
7. Zaviesť affected detection a full-validation fallback.
8. Presmerovať issues, docs a automation.
9. Archivovať staré repos ako read-only.
10. Monitorovať performance a developer flow.

Riziká:

- history collisions,
- nejasné tags,
- broken tooling assumptions,
- masívny first clone,
- neúplné permissions mapping.

## 32. Migrácia monorepo → multirepo

Potrebný plán:

1. Určiť stabilné domain a contract boundaries.
2. Extrahovať history relevantných paths.
3. Vytvoriť package/artifact publishing.
4. Nahradiť source dependencies immutable versions.
5. Zaviesť compatibility a contract tests.
6. Definovať cross-repo release manifest.
7. Migrovať permissions a ownership.
8. Nahradiť atomic changes expand-and-contract workflowom.
9. Aktualizovať developer tooling a code search.
10. Overiť hotfix, rollback a incident workflow.

Rozdelenie bez dependency discipline iba presunie implicitný coupling do neviditeľných runtime kombinácií.

## 33. Anti-patterny

### Monorepo bez build-system investície

Každá zmena spúšťa všetko, feedback rastie a tím začne CI obchádzať.

### Multirepo bez artifact contractu

Consumers používajú mutable `latest`, branch snapshots alebo ručné kopírovanie.

### Repo per microservice ako dogma

Ignoruje change coupling a vytvára veľa koordinovaných releases.

### Monorepo ako náhrada architektúry

Spoločný Git repository nevyrieši nejasné module boundaries alebo runtime coupling.

### CODEOWNERS ako security boundary

Review routing neobmedzuje automaticky čítanie source.

### Central tooling bez ownershipu

Jedna root zmena má organization-wide blast radius bez rollout a rollback plánu.

### Shared config copy-paste

Vytvára skrytú dependency a drift.

### Generated artifacts bez reprodukovateľného source

Repository sa stane manuálne udržiavaným binary store.

## 34. Diagnostický scenár: monorepo CI je príliš pomalé

1. Zmeraj queue, setup, build, test a upload fázy oddelene.
2. Over, či affected graph zodpovedá skutočným dependencies.
3. Zisti cache hit/miss dôvody.
4. Skontroluj nestabilné cache keys a environment inputs.
5. Rozlíš CPU-bound, I/O-bound a runner-capacity problém.
6. Zaveď sharding alebo parallel targets podľa graphu.
7. Použi conservative selective CI a periodic full runs.
8. Odstráň generated/binary inputs, ktoré invalidujú veľkú časť graphu.
9. Meraj feedback po zmene.
10. Nerozdeľuj repo automaticky, kým nie je potvrdené, že problém je boundary a nie build design.

## 35. Diagnostický scenár: multirepo release drift

1. Vytvor manifest reálne nasadených component versions.
2. Porovnaj deklarované a runtime dependencies.
3. Identifikuj consumers na zastaraných alebo nepodporovaných versions.
4. Over deprecation a compatibility policy.
5. Zaveď automated dependency updates.
6. Pridaj contract tests a integration matrix.
7. Zakáž mutable `latest` v release pipeline.
8. Eviduj source commit a artifact digest.
9. Definuj ownership cross-repo upgradeov.
10. Sleduj adoption lead time a failure rate.

## 36. Časté omyly

### „Monorepo znamená jeden release“

Nie. Komponenty môžu mať nezávislé artifacts, versions a deployments.

### „Multirepo znamená loose coupling“

Nie. Coupling môže zostať, iba sa presunie do package, API a deployment koordinácie.

### „Jedna služba má mať jedno repo“

Je to možná konvencia, nie architektonický zákon.

### „Atomický commit znamená atomický deployment“

Nie. Nezávislé runtime komponenty stále potrebujú kompatibilný rollout.

### „Monorepo je lacnejšie, lebo netreba versionovať interné dependencies“

Aj source dependency potrebuje stabilný contract, ownership a build graph.

### „Rozdelením veľkého repo sa automaticky zrýchli CI“

Lokálne pipelines môžu byť menšie, ale cross-repo integration a duplicate setup môžu celkový feedback zhoršiť.

## 37. Kontrolné otázky

1. Aký je rozdiel medzi repository, build, deployment a security boundary?
2. Čo poskytuje atomická source zmena a čo neposkytuje?
3. Ako multirepo nahrádza atomický commit kompatibilným rolloutom?
4. Prečo je change coupling dôležitejší než organizačný diagram?
5. Ako vzniká false green pri chybnom dependency graphe?
6. Prečo CODEOWNERS nie je plná confidentiality boundary?
7. Ako môže monorepo podporovať independent versioning a releases?
8. Načo slúži release manifest v monorepe aj multirepe?
9. Kedy je hybridný domain-monorepo model vhodný?
10. Aké signály odôvodňujú migráciu repository topology?

## Glossary impact

Relevantné pojmy: monorepo, multirepo, repository boundary, atomic change, change coupling, affected-project detection, dependency graph, path ownership, artifact registry, release manifest, hybrid repository model.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Branching strategies](branching-strategies.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Bash automation →](bash-automation.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
