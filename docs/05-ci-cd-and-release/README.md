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

Nasledujúci blok rozšíri sekciu o artifact versioning, Semantic Versioning, release management a konkrétne deployment stratégie od recreate a rolling update cez blue-green, canary, ring a shadow deployment až po feature flags, progressive delivery a rollback/roll-forward.

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
- používať matrix pipelines, test sharding a pipeline concurrency bez race conditions a combinatorial explosion.

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
