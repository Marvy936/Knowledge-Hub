# CI/CD and Release Engineering

Táto sekcia vysvetľuje cestu od integrovanej source zmeny cez reprodukovateľný build, immutable artifact, automatizované quality gates a environment promotion až po bezpečný produkčný rollout, release lifecycle a recovery.

Cieľom nie je memorovať syntax konkrétnej CI platformy. Dôležité je rozumieť oddeleniu source, build, artifact, deployment a release, dôveryhodným hraniciam pipeline, promotion evidence, rollout stratégiám, shared-state kompatibilite a obnoveniu služby.

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
16. [Canary deployment](canary-deployment.md)
17. [A/B testing](a-b-testing.md)
18. [Shadow deployment](shadow-deployment.md)
19. [Ring deployment](ring-deployment.md)
20. [Feature flags](feature-flags.md)
21. [Progressive delivery](progressive-delivery.md)
22. [Rollback a roll-forward](rollback-and-roll-forward.md)
23. [Databázová kompatibilita počas deploymentu](database-compatibility-during-deployment.md)

Po tejto sekcii nasleduje GitLab. Všeobecné pipeline a release princípy sa tam premietnu do projects, merge requests, protected branches/environments, GitLab CI/CD, runners, variables, registries a security scanningu.

## Cieľ zvládnutia

Po dokončení sekcie má byť možné:

- rozlíšiť Continuous Integration, Continuous Delivery a Continuous Deployment,
- navrhnúť rýchlu CI feedback loop a udržiavať mainline v deployable stave,
- oddeliť build, artifact, deployment, release a runtime exposure,
- používať build-once-promote-many s immutable artifact digestom a provenance,
- rozlíšiť pipeline, stage, job, step, runner a executor a navrhnúť ich trust boundaries,
- používať DAG dependencies, fan-out/fan-in, matrix jobs a test sharding bez race conditions,
- navrhnúť timeouts, cancellation, retry, cleanup a runner isolation,
- bezpečne spracovať push, merge-request, schedule, manual a upstream triggers,
- rozlíšiť dôveryhodný artifact od oportunistickej cache a chrániť cache pred poisoningom,
- navrhnúť environment, artifact promotion, promotion evidence, deployment record a drift detection,
- používať protected environments, short-lived identities, least privilege a separation of duties,
- navrhnúť blocking/advisory quality gates, risk-based approvals, exceptions a break-glass lifecycle,
- spravovať pipeline definície ako versionovaný a testovaný code s pinningom a Policy as Code,
- navrhnúť reusable workflow contract, child/multi-project pipeline a backward-compatible template lifecycle,
- rozlíšiť logical artifact version, mutable/immutable tag a content digest,
- používať Semantic Versioning ako explicitný compatibility contract pre deklarované public API,
- navrhnúť release unit, candidate, manifest, cadence, communication, support a emergency lifecycle,
- posúdiť recreate deployment podľa downtime budgetu a recovery schopnosti,
- navrhnúť rolling update s batchom, surge/unavailable limitmi, readiness a mixed-version kompatibilitou,
- navrhnúť blue-green deployment s environment parity, traffic cutoverom, warm standby a routing rollbackom,
- navrhnúť canary cohort, stabilný traffic assignment, observation window, promotion a abort criteria,
- rozlíšiť canary safety rollout od A/B experimentu a správne definovať experiment unit, exposure a guardrails,
- používať shadow traffic bez user-facing response a bez neplánovaných side effects,
- navrhnúť stabilné deployment rings, release channels a promotion contract podľa rastúceho rizika,
- používať feature flags s bezpečným evaluation, failure defaultom, auditom, expiry a cleanup lifecycle,
- skladať canary, rings, flags, shadowing a automatizovanú analysis do progressive delivery systému,
- zvoliť rollback alebo roll-forward podľa application, configuration, data a external-side-effect kompatibility,
- vytvoriť recovery package, last-known-good identity a testovaný rollback/restore postup,
- navrhovať databázové zmeny cez expand-contract, compatible readers/writers, dual write, reconciliation a bounded backfill,
- udržiavať application-schema compatibility matrix počas canary, rolling, ring aj blue-green rolloutov,
- prepojiť promotion a recovery rozhodnutia so SLO, error budgetom, business metrikami a version-level observability.

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
| Canary deployment | Learning | L2 |
| A/B testing | Learning | L2 |
| Shadow deployment | Learning | L2 |
| Ring deployment | Learning | L2 |
| Feature flags | Learning | L2 |
| Progressive delivery | Learning | L2 |
| Rollback a roll-forward | Learning | L2 |
| Databázová kompatibilita počas deploymentu | Learning | L2 |
