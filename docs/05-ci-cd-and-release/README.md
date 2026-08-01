# CI/CD and Release Engineering

Táto sekcia vysvetľuje celý release system od integračného kandidáta cez trusted build, immutable artifact, promotion evidence, deployment state machine a runtime exposure až po recovery shared-state compatibility. CI/CD sa tu neposudzuje podľa počtu pipeline jobov ani podľa zelenej ikony. Dôveryhodný výsledok vznikne iba vtedy, keď exact source, artifact, configuration, environment a runtime generation vedú k overenému technickému aj business outcome-u.

Sekcia sa po staršom strict passe znovu spracúva podľa rovnakého prose-first a practical-example štandardu ako Keycloak a novšie authoritative kapitoly. Silný existujúci obsah sa zachová tam, kde už vysvetľuje mechanizmus, no každá kapitola musí mať explicitný subject/generation model, reálne príkazy alebo konfiguráciu, vysvetlené read-back hranice, connected incident, authoritative recovery a allowed aj forbidden validation path.

## Section-wide release lifecycle

```text
business change a release intent
→ exact source, target a integration candidate
→ trusted workflow a resolved execution graph
→ pinned build inputs a immutable artifact
→ complete subject-bound verification evidence
→ release manifest a environment/configuration generation
→ deployment mutation a controller reconciliation
→ runtime cohort a traffic/feature exposure
→ technical, functional a business acceptance
→ rollback, roll-forward, compensation alebo restore
→ second-operation a forbidden-path validation
→ evidence closure, retirement a control improvement
```

Najdôležitejšie rozlíšenia zostávajú explicitné počas celej sekcie:

- source revision nie je build artifact;
- zelený job nie je complete candidate verdict;
- artifact tag nie je immutable digest;
- deployment nie je automaticky release ani traffic exposure;
- configured state nie je loaded ani effective runtime state;
- successful mutation response nepreukazuje konečný outcome;
- rollback application bytes nemusí byť kompatibilný so schema, events alebo external side effects;
- technical health nepreukazuje správny business výsledok.

## Predpoklady

Odporúča sa najprv dokončiť:

- [DevOps Foundations](../00-foundations/README.md),
- [Linux and Systems](../01-linux-and-systems/README.md),
- [Networking and Web Fundamentals](../02-networking-and-web/README.md),
- [Git and Automation Basics](../03-git-and-automation/README.md),
- [Testing and Software Quality](../04-testing-and-quality/README.md).

## Authoritative poradie — aktívne kapitoly

1. [Continuous Integration](continuous-integration.md)
2. [Continuous Delivery](continuous-delivery.md)
3. [Continuous Deployment](continuous-deployment.md)
4. [Pipeline, stage, job a runner](pipeline-stage-job-runner.md)
5. [Trigger, artifact a cache](trigger-artifact-cache.md)
6. [Environment a promotion](environment-and-promotion.md)
7. [Quality gates a approvals](quality-gates-and-approvals.md)
8. [Pipeline as Code](pipeline-as-code.md)
9. [Reusable a parallel pipelines](reusable-and-parallel-pipelines.md)
10. [Artifact versioning](artifact-versioning.md)
11. [Semantic Versioning](semantic-versioning.md)
12. [Release management](release-management.md)
13. [Recreate deployment](recreate-deployment.md)
14. [Rolling update](rolling-update.md)
15. [Blue-green deployment](blue-green-deployment.md)
16. [Canary deployment](canary-deployment.md)
17. [A/B testing](a-b-testing.md)
18. [Shadow deployment](shadow-deployment.md)
19. [Ring deployment](ring-deployment.md)
20. [Feature flags](feature-flags.md)
21. [Progressive delivery](progressive-delivery.md)
22. [Rollback a roll-forward](rollback-and-roll-forward.md)
23. [Databázová kompatibilita počas deploymentu](database-compatibility-during-deployment.md)
24. [Praktický CI/CD projekt od source change po overený production release](ci-cd-practical-walkthrough.md)

Po tejto sekcii nasleduje GitLab, kde sa všeobecné release princípy premietnu do projects, merge requests, protected branches/environments, GitLab CI/CD, runners, registries a security evidence.

## Hlavný praktický walkthrough

[Praktický CI/CD projekt od source change po overený production release](ci-cd-practical-walkthrough.md) vytvára vendor-neutral executable flow nad malou Python aplikáciou. Zachová exact commit/tree a build-script identity, spustí unit a forbidden test, vytvorí deterministic tar artifact pomenovaný SHA-256 digestom, publikuje release manifest a staging evidence a promovuje tie isté bytes do production. Candidate deployment, canary, atomický active-generation switch a business verification sú oddelené transitions.

Walkthrough obsahuje aj dve failure paths. Neoverený rebuild nedokáže použiť approval viazané na pôvodný digest a lost response po traffic switchi sa rieši read-backom active/candidate generation a ledgeru, nie blind retryom. Kapitola tak spája CI, delivery, deployment, progressive exposure a recovery bez závislosti od konkrétneho CI produktu.

## Connected learning scenarios

### `REL-PAY-66` — stale-green integration a nejednoznačný pipeline verdict

Prvý blok spája Continuous Integration, Continuous Delivery, Continuous Deployment a pipeline runtime. Atlas Payments vytvorí dva individuálne zelené pull requests, no ani jeden nebol revalidovaný proti aktuálnemu merge candidate-u. Persistent privileged runner zachová starý generated client a shared cache. Pipeline označí release za deployable, hoci artifact vznikol z iného candidate tree-u než evidence a produkčný deployment používa ďalšiu configuration generation.

```text
source A + stale target
→ branch-green evidence
→ warm workspace
→ rebuilt artifact po testoch
→ approval nad tagom
→ automatic production apply
→ runtime generation mismatch
→ settlement compatibility failure
```

Blok musí uzavrieť exact candidate identity, build-once, complete evidence, runner trust a rozdiel medzi delivery readiness a automatic deployment policy.

### `REL-PAY-67` — trigger confusion, cache poisoning a false promotion

Druhý blok spája trigger, artifact, cache, environment, promotion, gates a Pipeline as Code. Fork pull request zmení workflow, získa prístup k shared cache namespace-u a zapíše poisoned generated output. Neskorší trusted tag pipeline obnoví cache, publikuje artifact a promotion approval vidí iba release label, nie workflow revision, cache provenance ani target environment generation.

```text
untrusted trigger
→ mutable workflow/template input
→ poisoned shared cache
→ trusted build restore
→ artifact publication
→ approval bez complete subjectu
→ production promotion
```

Recovery musí oddeliť trigger trust, cache od artifact authority, source/rendered pipeline generation a target-environment effective state.

### `REL-PAY-68` — reusable workflow drift a chybný compatibility contract

Tretí blok spája reusable/parallel pipelines, artifact versioning, Semantic Versioning a release management. Shared workflow používa mutable ref, jeden matrix shard sa nevykoná a release automation označí breaking event-schema zmenu ako minor version. Tag, package metadata a OCI digest ukazujú rozdielne release identities. Release notes hovoria o jednom candidate, production však dostane iný multi-platform manifest.

```text
reusable workflow contract
→ resolved graph a shard manifest
→ immutable artifact graph
→ declared compatibility version
→ release manifest
→ support a communication lifecycle
```

Acceptance musí preukázať complete fan-in, exact artifact graph, explicitný public contract a jeden authoritative release manifest.

### `REL-PAY-69` — rollout strategy bez capacity a state contractu

Štvrtý blok spája recreate, rolling, blue-green a canary deployment. Atlas zvolí rolling update s `maxUnavailable` interpretovaným percentom nad desired replicas, no unavailable baseline už pred rolloutom porušuje capacity. Database migration nie je backward compatible, readiness kontroluje iba process health a canary cohort nie je stabilný. Pokus o rollback vracia staré Pods nad už contractnutou schema.

```text
release generation
→ deployment strategy parameters
→ capacity a shared-state preconditions
→ workload cohorts
→ eligibility a traffic assignment
→ observation window
→ promotion alebo abort
→ old-generation retirement
```

Každá stratégia musí vysvetliť vlastný state machine, traffic/data boundary a recovery eligibility, nie iba poradie vytvárania replík.

### `REL-PAY-70` — experiment, shadow a feature controls sa rozídu

Piaty blok spája A/B testing, shadow deployment, rings a feature flags. Experiment assignment sa vykonáva per request namiesto per user, shadow consumer vykonáva provider side effects, ring membership sa mení počas observation window a fail-open feature flag povolí nový settlement path mimo schválenej cohorty.

```text
business hypothesis alebo release-risk intent
→ stable subject assignment
→ primary, experimental alebo shadow execution
→ feature/ring/exposure generation
→ guardrails a outcome metrics
→ decision
→ cleanup a long-lived control retirement
```

Blok musí oddeľovať safety rollout od causálneho experimentu, neautoritatívny shadow result od business side effectu a deployment cohort od runtime flag cohorty.

### `REL-PAY-71` — progressive delivery a recovery nad zmeneným shared state-om

Záverečný blok spája progressive delivery, rollback/roll-forward a databázovú kompatibilitu. Traffic, feature, application a schema control planes ukazujú rozdielne generations. Timeout počas route transition vytvorí unknown outcome, stará application version už nevie čítať nové eventy a stale backfill prepíše novší live state. Automatický rollback obnoví image, ale nie business konzistenciu.

```text
rollout contract
→ multi-axis observed state
→ bounded exposure transition
→ subject-bound evidence
→ promotion/containment verdict
→ per-layer recovery eligibility
→ reconciliation alebo compensation
→ original, forbidden a second-operation validation
```

Sekcia sa uzatvára až vtedy, keď recovery rozhodnutie zahŕňa application, configuration, data, events, external side effects a business outcome.

## Výklad pojmov je integrovaný do release lifecycle-u

Integration candidate, pipeline execution, artifact, cache, digest, promotion, cohort, rollout a recovery sú vysvetlené súvislým textom v tom kroku lifecycle-u, kde menia stav alebo podporujú rozhodnutie. Príkazy a controller transitions sú spojené s vysvetlením vstupu, vykonanej mutácie, read-backu a dôkaznej hranice.

Opisné odrážkové dodatky boli nahradené explicitne napísanými odbornými podkapitolami. Zoznamy zostávajú pri presných porovnaniach deployment stratégií, acceptance podmienkach, zdrojoch a evidence inventories; nenahrádzajú základný výklad.

## Cieľ zvládnutia

Po dokončení sekcie má byť možné navrhnúť release chain, ktorý:

- identifikuje presný integration candidate a invaliduje stale evidence;
- používa trusted, reprodukovateľný build a build-once-promote-many;
- oddeľuje artifact, cache, deployment record, release manifest a runtime exposure;
- viaže každý gate na exact subject, policy generation a complete evidence inventory;
- modeluje pipeline ako versionovaný execution graph s explicitnými trust a failure boundaries;
- používa immutable artifact digest, SBOM, signature a provenance podľa rizika;
- navrhuje deployment stratégie podľa capacity, state, traffic a recovery contractu;
- rozlišuje canary safety, A/B causal inference, shadow execution, rings a feature flags;
- zachováva mixed-version kompatibilitu application, schema, events a caches;
- rieši unknown outcomes, partial completion, retries a external side effects;
- vyberá rollback, roll-forward, feature disable, compensation alebo restore podľa per-layer eligibility;
- overuje technical, functional, business, forbidden a second-operation outcome;
- premieňa defect escape na zmenu dependency, test, policy alebo platform modelu.

## Revalidation completion gate

Sekcia bude označená `Ready for user review` iba po splnení všetkých podmienok:

1. všetkých 24 authoritative kapitol používa Keycloak-style connected prose a dominantný lifecycle;
2. každá kapitola definuje exact source, artifact, release, deployment, cohort, data alebo recovery subject;
3. každá kapitola obsahuje aspoň dva reálne executable príkazy, konfigurácie alebo query walkthroughy tam, kde to téma umožňuje;
4. každý významný output vysvetľuje, čo preukazuje a čo nepreukazuje;
5. configured, resolved, published, loaded, effective, runtime a business states sa nezlievajú;
6. komplexné failures používajú competing hypotheses, discriminating evidence a evidence-preserving containment;
7. recovery obsahuje authoritative mutation alebo reconciliation a overenie forbidden aj second-operation pathu;
8. strict learning-depth audit pre všetkých 23 kapitol je `0/0/0` a practical gate nemá failures;
9. README, glossary, navigation a centrálny review ledger sú synchronizované;
10. dočasné auditné súbory a workflowy sú odstránené a čistý head prejde štandardným documentation workflowom.

## Aktuálny stav revalidácie

Všetkých 24 authoritative kapitol vrátane end-to-end CI/CD walkthroughu je pripravených na používateľskú kontrolu. Stav neznamená automatické používateľské schválenie ani runtime overenie každého deployment targetu.
