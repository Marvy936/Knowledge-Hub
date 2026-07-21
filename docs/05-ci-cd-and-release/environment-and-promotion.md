# Environment a promotion

Environment nie je iba názov ako `dev`, `staging` alebo `production`. Je to konkrétny runtime kontext so svojou konfiguráciou, identitou, dátami, sieťou, dependencies, policy a prevádzkovým stavom. Promotion je riadený prechod overeného artifactu a jeho evidence do vyššieho environmentu bez zmeny samotného artifactu.

## 1. Čo tvorí environment

Environment typicky zahŕňa:

- compute platformu,
- network topology,
- DNS a ingress,
- runtime configuration,
- secrets a identities,
- backing services,
- databases a data state,
- observability,
- policies,
- deployment history,
- ownership a support model.

Dva environments s rovnakou verziou aplikácie nemusia poskytovať rovnaké správanie, ak sa líšia v týchto vrstvách.

## 2. Tradičné environmenty

Bežný model:

```text
development
→ integration/test
→ staging/pre-production
→ production
```

Každý ďalší environment má typicky:

- vyššiu fidelity,
- prísnejšie permissions,
- drahšie alebo dlhšie gates,
- menší povolený change rate,
- väčší blast radius.

Počet environmentov nie je cieľ. Každý musí mať jasný účel a odlišný typ dôkazu.

## 3. Ephemeral environment

Ephemeral environment vzniká pre branch, pull request alebo test run a po použití sa odstráni.

Výhody:

- izolácia paralelných zmien,
- realistické integration/E2E testy,
- jednoduchšia reprodukcia,
- menší shared-state conflict.

Riziká:

- vysoké náklady,
- dlhý provisioning,
- cleanup failures,
- nedostatočne realistické data alebo dependencies,
- secret a quota sprawl.

Ephemeral environment potrebuje TTL, ownership, tagging a idempotentný destroy.

## 4. Environment parity vs. equivalence

Úplná identita stagingu a produkcie je často nereálna. Dôležitejšia je **behavioral equivalence** relevantných vrstiev:

- rovnaký artifact,
- rovnaký deployment mechanizmus,
- kompatibilná konfigurácia schema,
- rovnaký protocol path,
- realistické resource limits,
- rovnaké security controls,
- reprezentatívne dependencies.

Staging s jednou instanciou nemusí odhaliť race, rolling-update alebo distributed-state problém produkcie.

## 5. Environment-specific configuration

Artifact má zostať environment-agnostic, pokiaľ je to možné. Rozdiely sa dodávajú ako runtime configuration:

```text
artifact digest: rovnaký
config: environment-specific
secret references: environment-specific
traffic policy: environment-specific
```

Build-time vloženie production credentials alebo endpointov spája artifact s environmentom a ruší promotion model.

## 6. Configuration contract

Application a environment config potrebujú explicitný kontrakt:

- required fields,
- types a allowed values,
- defaults,
- secret references,
- compatibility s artifact version,
- validation pred deploymentom.

Configuration drift je rovnako významný ako source drift.

## 7. Promotion

Promotion znamená, že ten istý overený artifact pokračuje do ďalšieho environmentu spolu s evidence:

```text
artifact digest
+ test results
+ security results
+ provenance
+ approvals/policy decisions
→ promotion
```

Promotion nie je rebuild. Je to zmena deployment state a environment assignment.

## 8. Artifact promotion

Možnosti:

- rovnaký artifact zostáva v jednej registry a mení sa iba environment manifest,
- artifact sa kopíruje medzi oddelenými registries bez zmeny digestu,
- release manifest odkazuje na immutable digests viacerých komponentov.

Pri kopírovaní treba overiť digest a provenance po prenose.

## 9. Environment promotion vs. release

Deployment do production environmentu nemusí znamenať okamžité sprístupnenie všetkým používateľom.

```text
deploy artifact
→ disabled feature flag
→ internal users
→ 5 % traffic
→ 100 % release
```

Environment promotion rieši, kde artifact beží. Release rieši, komu je behavior dostupný.

## 10. Promotion evidence

Promotion decision môže používať:

- test reports,
- coverage a quality gates,
- security findings,
- SBOM a provenance,
- artifact signature,
- policy evaluation,
- change record,
- canary metrics,
- previous environment validation.

Evidence musí byť naviazaná na konkrétny artifact digest, nie iba branch alebo pipeline name.

## 11. Protected environment

Protected environment obmedzuje, kto alebo čo môže deployment vykonať.

Controls:

- protected branches/tags,
- environment-scoped credentials,
- required approvals,
- deployment window,
- policy checks,
- concurrency lock,
- audit log.

Production credential nemá byť dostupný build jobu ani nedôveryhodnému pull-request pipeline.

## 12. Environment-scoped identity

Preferovaný model:

```text
job identity
→ short-lived federation
→ environment-specific role
→ minimal permissions
```

Namiesto dlhodobého cloud key používaj workload identity alebo OIDC federation s constraints na repository, branch, workflow a environment.

## 13. Promotion permissions

Rozlišuj:

- právo vytvoriť artifact,
- právo potvrdiť evidence,
- právo promotion do stagingu,
- právo production deploymentu,
- právo release zmeny používateľom.

Jedna univerzálna CI identity s admin právami ruší separation of duties a zvyšuje blast radius.

## 14. Deployment concurrency

Dva deploymenty do rovnakého environmentu môžu vytvoriť race:

```text
pipeline A deployuje v1
pipeline B deployuje v2
pipeline A dokončí neskôr a prepíše v2
```

Použi:

- environment lock,
- deployment queue,
- optimistic version check,
- superseded deployment cancellation,
- serialized state mutation.

## 15. Deployment record

Pre každý deployment uchovaj:

- artifact digest,
- environment,
- config version,
- commit/source identity,
- pipeline run,
- actor alebo workload identity,
- timestamps,
- result,
- rollback/roll-forward relation,
- release exposure.

Deployment history je prevádzkový a auditný zdroj pravdy.

## 16. Environment drift

Drift vzniká, keď runtime stav nezodpovedá deklarovanému desired state:

- manuálna config zmena,
- emergency hotfix,
- package update na hoste,
- resource vytvorený mimo IaC,
- secret rotation bez synchronizácie,
- policy zmena.

Promotion bez drift detection môže validovať artifact v jednom stave a nasadiť ho do iného.

## 17. Environment inventory

Potrebný je inventory alebo state model:

```text
environment
→ deployed artifact digests
→ config revision
→ infrastructure revision
→ secret versions/references
→ active feature flags
→ traffic policy
```

Bez neho nie je spoľahlivé určiť, čo skutočne beží.

## 18. Database a promotion

Databáza je shared mutable state a nemožno ju promotionovať rovnako ako immutable artifact.

Bezpečný model:

1. expand schema backward-compatible zmenou,
2. deploy code kompatibilný so starým aj novým stavom,
3. migrate/backfill data,
4. prepnúť reads/writes,
5. contract až po odstránení starých consumers.

Environment promotion musí kontrolovať schema compatibility a migration status.

## 19. Secrets medzi environments

Secrets sa nemajú kopírovať z testu do produkcie. Každý environment má vlastné:

- secret values,
- trust roots,
- identities,
- rotation lifecycle,
- access policy.

Promotion prenáša referenciu alebo requirement, nie secret material.

## 20. Data promotion

Test data sa typicky nepromotionujú do produkcie. Produkčné dáta môžu byť transformované do nižších environments iba pri splnení privacy a compliance podmienok.

Preferuj synthetic datasets a controlled fixtures.

## 21. Promotion gates

Príklad:

```text
build artifact
→ automated verification
→ deploy test
→ integration evidence
→ deploy staging
→ acceptance/performance/security evidence
→ production approval/policy
→ progressive rollout
```

Každý gate má riešiť nový risk, nie opakovať rovnaký test bez vyššej fidelity.

## 22. Promotion freeze a deployment window

Organizácia môže obmedziť deployment podľa:

- support coverage,
- business calendar,
- peak traffic,
- regulatory change window,
- incident state.

Freeze nie je náhradou bezpečného delivery systému. Dlhé freezes zväčšujú batch size po ich skončení.

## 23. Rollback

Rollback znamená návrat na predchádzajúci deployment state. Je možný iba ak:

- starý artifact je dostupný,
- config je kompatibilná,
- databázová zmena je backward-compatible,
- external contracts neboli nevratne zmenené,
- traffic/state migration to umožňuje.

Pre stateful zmeny býva bezpečnejší roll-forward.

## 24. Environment teardown

Pri ephemeral alebo retiring environment-e odstráň:

- compute a network resources,
- DNS records,
- temporary secrets,
- test identities,
- storage podľa retention policy,
- deployment locks,
- monitoring targets.

Teardown musí byť auditovateľný a bezpečný voči nesprávnemu environment identifieru.

## 25. Observability

Sleduj:

- environment provisioning time,
- promotion lead time,
- deployment success rate,
- drift findings,
- stale environments,
- deployment queue time,
- rollback/roll-forward rate,
- config-related incidents,
- secret/identity errors.

## 26. Troubleshooting

### Staging funguje, production nie

Porovnaj:

- artifact digest,
- config revision,
- network path,
- identity/permissions,
- dependency versions,
- data/schema state,
- resource limits,
- traffic pattern.

### Promotion použil iný artifact

Skontroluj, či deployment referencuje mutable tag alebo vykonal rebuild. Porovnaj digest a provenance.

### Deployment čaká

Over environment lock, protected-environment policy, approval state, deployment window a starší active deployment.

### Ephemeral environment zostal visieť

Over cleanup job, TTL controller, ownership tags, finalizers/dependencies a permissions destroy identity.

## 27. Časté omyly

### „Staging je malá produkcia“

Môže mať inú topology, data scale, traffic concurrency a external dependencies.

### „Promotion znamená rebuild pre ďalší environment“

Rebuild ruší dôkaz, že sa nasadzuje testovaný artifact.

### „Environment je iba namespace“

Namespace môže byť jedna technická boundary, ale environment zahŕňa aj identity, config, data, policies a dependencies.

### „Rollback je vždy jednoduchý“

Mutable state a external contracts ho môžu znemožniť.

## 28. Kontrolné otázky

1. Čo všetko tvorí environment?
2. Aký je rozdiel medzi parity a behavioral equivalence?
3. Čo znamená artifact promotion?
4. Prečo sa artifact nemá rebuildovať pre produkciu?
5. Aký je rozdiel medzi deploymentom a release?
6. Čo má obsahovať promotion evidence?
7. Ako funguje protected environment a environment-scoped identity?
8. Ako zabrániš racing deploymentom?
9. Prečo databázový state komplikuje promotion a rollback?
10. Ako diagnostikuješ rozdiel medzi staging a production behaviorom?

## Glossary impact

Relevantné pojmy: environment, ephemeral environment, environment parity, behavioral equivalence, promotion, artifact promotion, promotion evidence, protected environment, environment-scoped identity, deployment record, environment drift, deployment lock a expand-contract migration.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Trigger, artifact a cache](trigger-artifact-cache.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Quality gates a approvals →](quality-gates-and-approvals.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
