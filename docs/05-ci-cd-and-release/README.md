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

Nasledujúci blok rozšíri sekciu o pipeline/stage/job/runner model, triggers, artifacts, cache, environments, promotion, quality gates, approvals a Pipeline as Code.

## Cieľ zvládnutia

Po dokončení aktuálneho bloku má byť možné:

- vysvetliť Continuous Integration ako pracovný model častej integrácie, nie iba build server,
- navrhnúť rýchlu CI feedback loop od lacných kontrol po immutable artifact,
- vysvetliť mainline health, merge queue, build once, reproducible build a runner isolation,
- rozlíšiť pipeline cache od dôveryhodného artifactu,
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
- interpretovať deployment frequency, change lead time, change fail rate a recovery metrics ako spoločný systém.

## Stav

| Téma | Status | Úroveň |
|---|---|---|
| Continuous Integration | Learning | L2 |
| Continuous Delivery | Learning | L2 |
| Continuous Deployment | Learning | L2 |
