# CI/CD and Release Engineering

Táto sekcia vysvetľuje cestu od integrovanej source zmeny cez reprodukovateľný build, immutable artifact, automatizované quality gates a environment promotion až po bezpečný produkčný rollout a release lifecycle.

Cieľom nie je memorovať syntax konkrétnej CI platformy. Dôležité je rozumieť oddeleniu source, build, artifact, deployment a release, dôveryhodným hraniciam pipeline, promotion evidence, rollout stratégiám a recovery mechanizmom.

## Predpoklady

Odporúča sa najprv dokončiť:

- [DevOps Foundations](../00-foundations/README.md),
- [Linux and Systems](../01-linux-and-systems/README.md),
- [Networking and Web Fundamentals](../02-networking-and-web/README.md),
- [Git and Automation Basics](../03-git-and-automation/README.md),
- [Testing and Software Quality](../04-testing-and-quality/README.md).

## Odporúčané poradie

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

Posledný blok sekcie doplní canary, A/B, shadow a ring deployment, feature flags, progressive delivery, rollback/roll-forward a databázovú kompatibilitu počas deploymentu.

## Cieľ zvládnutia

Po dokončení aktuálneho bloku má byť možné:

- vysvetliť Continuous Integration ako pracovný model častej integrácie, nie iba build server,
- navrhnúť rýchlu CI feedback loop od lacných kontrol po immutable artifact,
- vysvetliť mainline health, merge queue, build once, reproducible build a runner isolation,
- definovať Continuous Delivery a deployable state,
- navrhnúť deployment pipeline s artifact a environment promotion,
- oddeliť deployment od release,
- vysvetliť protected environments, evidence-based approvals a separation of duties,
- navrhovať backward-compatible databázové delivery cez expand-contract,
- rozlíšiť rollback a roll-forward podľa state compatibility,
- definovať Continuous Deployment a jeho predpoklady,
- navrhnúť progressive exposure, canary analysis a risk-based deployment policy,
- používať feature flags bez trvalého lifecycle dlhu,
- prepojiť deployment decisions so SLO, error budgetom a produkčnou observability,
- interpretovať deployment frequency, change lead time, change fail rate a recovery metrics ako spoločný systém,
- rozlíšiť pipeline, stage, job, step, runner a executor a navrhnúť ich trust boundaries,
- používať DAG dependencies, fan-out/fan-in a critical-path analýzu bez zbytočných stage barriers,
- zvoliť hosted, self-hosted, container alebo VM runner model podľa isolation a capacity požiadaviek,
- navrhnúť job timeouts, cleanup, retry a cancellation semantics,
- rozlíšiť trigger contexts a bezpečne spracovať push, merge-request, schedule, manual a upstream events,
- rozlíšiť dôveryhodný artifact od oportunistickej cache,
- navrhnúť artifact identity, retention, integrity, provenance a build-once-promote-many flow,
- vytvoriť bezpečný cache key, invalidation a trust namespace bez cache poisoning-u,
- definovať environment ako runtime kombináciu artifactu, configu, identity, dát, dependencies a policy,
- navrhnúť artifact promotion, promotion evidence, deployment records a environment drift detection,
- používať environment-scoped short-lived identities a protected environment controls,
- rozlíšiť check, blocking/advisory quality gate a ľudský approval,
- navrhnúť ratcheting, evidence freshness, risk-based approvals, exception a break-glass lifecycle,
- spravovať pipeline definície ako versionovaný a testovaný code s pinningom, least privilege a Policy as Code,
- testovať reusable templates, dynamic/child pipelines a resolved pipeline configuration,
- navrhnúť reusable job/workflow contract s versioningom a backward compatibility,
- používať matrix pipelines, test sharding a pipeline concurrency bez race conditions a combinatorial explosion,
- rozlíšiť logical artifact version od content digestu a navrhnúť immutable artifact identity,
- používať build metadata, provenance, podpisy, multi-platform manifests a retention policy na podporu auditu a rollbacku,
- aplikovať build-once-promote-many bez rebuildu release candidate počas promotion,
- vysvetliť Semantic Versioning ako compatibility kontrakt a správne interpretovať MAJOR, MINOR, PATCH, pre-release a build metadata,
- identifikovať public API aj mimo programového rozhrania a navrhnúť deprecation a migration lifecycle,
- navrhnúť release unit, release record, cadence, candidate, manifest, approvals, communication a support lifecycle,
- oddeliť build, deployment a release a riadiť emergency release bez obídenia identity a evidence,
- posúdiť recreate deployment podľa downtime budgetu, startup/readiness, maintenance režimu a recovery schopnosti,
- navrhnúť rolling update s vhodným batchom, surge/unavailable limitmi, mixed-version compatibility a graceful termination,
- používať version-level telemetry, topology-aware rollout, pause/abort a bezpečný rolling rollback alebo roll-forward,
- navrhnúť blue-green deployment s environment parity, riadeným traffic cutoverom, warm standby a routing rollbackom,
- koordinovať databázu, cache, sessions, background workers a scheduled jobs medzi blue a green prostrediami.

## Stav

| Téma | Status | Úroveň |
|---|---|---|
| Continuous Integration | Learning | L2 |
| Continuous Delivery | Learning | L2 |
| Continuous Deployment | Learning | L2 |
| Pipeline, stage, job a runner | Learning | L2 |
| Trigger, artifact a cache | Learning | L2 |
| Environment a promotion | Learning | L2 |
| Quality gates a approvals | Learning | L2 |
| Pipeline as Code | Learning | L2 |
| Reusable a parallel pipelines | Learning | L2 |
| Artifact versioning | Learning | L2 |
| Semantic Versioning | Learning | L2 |
| Release management | Learning | L2 |
| Recreate deployment | Learning | L2 |
| Rolling update | Learning | L2 |
| Blue-green deployment | Learning | L2 |
