# Authoritative CI/CD progressive-delivery glossary overrides

## A/B testing

Riadený experiment porovnávajúci control a treatment variant na súbežných skupinách používateľov podľa vopred definovaných outcome a guardrail metrík. Pozri [A/B testing](docs/05-ci-cd-and-release/a-b-testing.md).

## Canary deployment

Deployment stratégia postupne zvyšujúca produkčnú exposure novej verzie pri súbežnom porovnávaní so stable baseline a explicitných promotion/abort kritériách. Pozri [Canary deployment](docs/05-ci-cd-and-release/canary-deployment.md).

## Expand-contract

Viacfázový model databázovej alebo contract zmeny: najprv sa pridá kompatibilná nová štruktúra, migrujú readers/writers a dáta, a až po rollback window sa odstráni stará štruktúra. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Feature flag

Runtime control oddeľujúci deployment kódu od sprístupnenia capability pomocou versionovaného evaluation pravidla. Pozri [Feature flags](docs/05-ci-cd-and-release/feature-flags.md).

## Progressive delivery

Evidence-driven riadenie postupnej produkčnej exposure pomocou rollout stratégie, segmentácie, observability, promotion policy a recovery mechanizmov. Pozri [Progressive delivery](docs/05-ci-cd-and-release/progressive-delivery.md).

## Ring deployment

Progressive rollout cez stabilné deployment rings s rastúcou reprezentatívnosťou alebo kritickosťou a samostatnými entry, observation a promotion podmienkami. Pozri [Ring deployment](docs/05-ci-cd-and-release/ring-deployment.md).

## Roll-forward

Recovery stratégia nasadzujúca nový opravný artifact alebo migration namiesto návratu na starú verziu, často pre nekompatibilný alebo už zmenený shared state. Pozri [Rollback a roll-forward](docs/05-ci-cd-and-release/rollback-and-roll-forward.md).

## Rollback — deployment

Recovery stratégia obnovujúca predchádzajúci kompatibilný artifact, konfiguráciu, traffic target alebo infraštruktúrny state. Neznamená automaticky návrat dát a external side effects. Pozri [Rollback a roll-forward](docs/05-ci-cd-and-release/rollback-and-roll-forward.md).

## Shadow deployment

Deployment, ktorý spracúva kópiu produkčného workloadu bez autoritatívnej response a s blokovanými alebo izolovanými side effects. Pozri [Shadow deployment](docs/05-ci-cd-and-release/shadow-deployment.md).
