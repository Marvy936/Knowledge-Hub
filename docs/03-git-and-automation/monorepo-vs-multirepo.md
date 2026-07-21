# Monorepo vs. multirepo

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Git and Automation Basics
- Predpoklady: [Branching strategies](branching-strategies.md), [Value Stream Mapping](../00-foundations/value-stream-mapping.md)
- Súvisiace témy: repository boundaries, ownership, CI graph, dependency management, platform engineering

## 1. Definícia

Monorepo ukladá viac projektov, služieb alebo knižníc do jedného repository. Multirepo ich rozdeľuje medzi viac repositories.

Rozhodnutie nie je iba o počte Git repozitárov. Určuje:

- hranice zmien,
- ownership,
- dependency workflow,
- CI/CD topology,
- access control,
- release coordination,
- developer experience.

## 2. Monorepo

Príklad:

```text
repo/
├── services/api
├── services/worker
├── libs/auth
├── infrastructure
└── tools
```

Výhody:

- atomické cross-project changes,
- jednotné tooling a policy,
- jednoduchšie refactoringy,
- centrálna code search,
- konzistentné dependency upgrades,
- jeden review context.

Riziká:

- veľký clone/index,
- zložitejší selective CI,
- široký blast radius tooling zmeny,
- jemnejšia access control je náročná,
- central build system môže byť kritická dependency.

## 3. Multirepo

Príklad:

```text
api-repo
worker-repo
auth-library-repo
infrastructure-repo
```

Výhody:

- jasné ownership a permissions boundaries,
- menšie repositories,
- nezávislý lifecycle a tooling,
- izolované CI/CD,
- jednoduchšie oddelenie externých a interných projektov.

Riziká:

- koordinované zmeny nie sú atomické,
- dependency version drift,
- opakované konfigurácie,
- cross-repo discovery a refactoring sú náročnejšie,
- release orchestration potrebuje explicitné contracts.

## 4. Atomická zmena

V monorepe môže jeden commit zmeniť producer, consumer, tests aj deployment config.

V multirepe potrebuješ sekvenciu kompatibilných zmien:

```text
1. producer pridá backward-compatible contract
2. publish version
3. consumers adoptujú
4. odstráni sa starý contract
```

To nie je automaticky nevýhoda. Núti explicitne riešiť compatibility a rollout.

## 5. Dependency management

Monorepo môže používať source dependencies alebo central lock graph. Potrebuje jasné pravidlá:

- visibility,
- ownership,
- versioning interných modules,
- hermetic builds,
- cache keys,
- affected-project detection.

Multirepo typicky potrebuje:

- artifact registry,
- semantic versioning alebo iný contract,
- dependency update automation,
- compatibility testing,
- deprecation policy.

## 6. CI v monorepe

Naivné „testuj všetko pri každej zmene“ sa pri veľkom monorepe neškáluje.

Potrebné mechanizmy:

```text
change detection
→ dependency graph
→ affected targets
→ remote/local cache
→ parallel execution
```

Riziko: chybný dependency graph vynechá test a vytvorí false green pipeline.

Pre kritické zmeny môže byť potrebný širší periodic alebo pre-release validation run.

## 7. CI v multirepe

Každý repository má samostatnú pipeline, ale cross-repo integrácia vyžaduje:

- contract tests,
- versioned artifacts,
- integration environment,
- downstream triggers alebo dependency updates,
- release metadata.

Anti-pattern je buildovať consumer vždy z náhodného latest commitu dependency bez immutable version.

## 8. Ownership a CODEOWNERS

Monorepo potrebuje path-based ownership:

```text
/services/api/      @api-team
/libs/auth/         @security-team
/infrastructure/    @platform-team
```

Path ownership však nie je plná security boundary. Používateľ s repository read accessom typicky vidí celý obsah.

Multirepo poskytuje prirodzenejšiu repository-level access boundary.

## 9. Release model

Monorepo nemusí znamenať jeden release train. Možnosti:

- unified versioning,
- independent versions per project,
- commit-SHA based artifacts,
- release manifest mapujúci commit na artifacts.

Multirepo prirodzene podporuje nezávislé versions, ale cross-product release potrebuje explicitnú bill of materials alebo environment manifest.

## 10. Repository size a Git performance

Problémy veľkého repository:

- veľký object graph,
- veľký index,
- množstvo files vo working tree,
- pomalý status/checkout,
- veľké binary artifacts.

Mechanizmy:

```bash
git clone --filter=blob:none
git sparse-checkout init --cone
git sparse-checkout set services/api libs/auth
```

Ďalšie nástroje: filesystem monitor, commit graph, multi-pack-index, LFS. Architektúra však nemá spoliehať iba na klientské optimalizácie.

## 11. Binary a generated artifacts

Veľké binaries nezaraďuj automaticky do monorepa. Použi:

- artifact registry,
- object storage,
- Git LFS, ak je vhodný,
- reprodukovateľný build zo source.

Repository nie je všeobecný package registry.

## 12. Shared tooling

Monorepo uľahčuje centralizáciu:

- linters,
- formatters,
- build rules,
- CI templates,
- dependency policy.

Riziko je „global breaking change“ v tooling. Preto treba versioned rules, migration tooling a staged rollout.

Multirepo potrebuje reusable templates alebo platform service, inak vzniká copy-paste drift.

## 13. Kedy preferovať monorepo

Silné signály:

- časté atomické cross-component changes,
- úzko previazaný product,
- spoločné tooling a jazykový ekosystém,
- schopnosť investovať do build graphu a cache,
- široko zdieľaný code access je prijateľný.

## 14. Kedy preferovať multirepo

Silné signály:

- nezávislé products a release lifecycles,
- rozdielne access/compliance boundaries,
- externí partneri,
- výrazne rozdielne technologické stacky,
- stabilné versioned contracts medzi systémami.

## 15. Hybridný model

Praktické organizácie často používajú viac domain monorepos:

```text
product-platform-monorepo
mobile-monorepo
infrastructure-config-repo
shared-open-source-repos
```

Cieľom nie je maximalizovať alebo minimalizovať počet repositories, ale zvoliť hranice zodpovedajúce ownership a change coupling.

## 16. Rozhodovací rámec

Posúď:

1. Ako často sa komponenty menia spolu?
2. Potrebujú atomický commit?
3. Aké sú security boundaries?
4. Ako sa versions a artifacts publikujú?
5. Aká je veľkosť source a history?
6. Máme build graph a cache?
7. Kto vlastní shared tooling?
8. Ako prebieha cross-repo refactoring?
9. Ako meriame lead time a failure rate?
10. Aký migration cost rozhodnutie vytvorí?

## 17. Anti-patterny

### Monorepo bez build-system investície

Vedie k pipeline „test everything“ a rastúcemu feedback time.

### Multirepo bez contract/version discipline

Vedie k `latest` dependencies a nepredvídateľným integráciám.

### Repository boundary podľa organizačného diagramu

Tímy sa menia. Boundary má odrážať dlhodobejší domain a change coupling.

### Shared config copy-paste

Vytvára drift. Použi reusable automation alebo central platform capability.

## 18. Kontrolné otázky

1. Aké problémy rieši atomická cross-project zmena?
2. Prečo monorepo potrebuje dependency graph?
3. Aké mechanizmy nahrádzajú atomický commit v multirepe?
4. Prečo CODEOWNERS nie je plná security boundary?
5. Ako môže monorepo podporovať independent releases?
6. Kedy je hybridný model vhodnejší?
7. Aké metriky by si sledoval po zmene repository stratégie?

## Glossary impact

Relevantné pojmy: monorepo, multirepo, atomic change, affected-project detection, dependency graph, path ownership, artifact registry, hybrid repository model.
