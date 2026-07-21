# GitLab

Táto sekcia aplikuje všeobecné Git, testing a CI/CD princípy na konkrétny GitLab platform model. Cieľom nie je memorovať polohu nastavení v UI, ale rozumieť namespaces, inheritance, trust boundaries, merge policy, protected resources, pipeline execution a artifact/release lifecycle.

GitLab features, role permissions a dostupnosť niektorých controls sa menia podľa verzie, offeringu a tieru. Pri produkčnom návrhu treba vždy overiť aktuálnu dokumentáciu a konfiguráciu konkrétnej inštancie.

## Predpoklady

Odporúča sa najprv dokončiť:

- [Git and Automation Basics](../03-git-and-automation/README.md),
- [Testing and Software Quality](../04-testing-and-quality/README.md),
- [CI/CD and Release Engineering](../05-ci-cd-and-release/README.md).

## Odporúčané poradie

1. [Projects, groups a permissions](projects-groups-permissions.md)
2. [Merge requests a approvals](merge-requests-and-approvals.md)
3. [Protected branches a environments](protected-branches-and-environments.md)

Ďalší blok doplní GitLab CI/CD syntax, runners/executors, variables/secrets, artifacts/cache, container/package registry, environments/deployments/releases a security scanning.

## Cieľ zvládnutia

Po dokončení aktuálneho bloku má byť možné:

- vysvetliť rozdiel medzi GitLab project, group, subgroup a namespace,
- navrhnúť group hierarchy podľa ownershipu, security boundary a lifecycle namiesto náhodnej organizačnej štruktúry,
- rozlíšiť direct, inherited a shared membership a vypočítať highest effective role,
- používať built-in alebo custom roles podľa least-privilege a governance požiadaviek,
- oddeliť human users, external users, service accounts, access tokens a CI identities,
- navrhnúť onboarding, expiration, access review a project-transfer kontrolný proces,
- vysvetliť merge request ako väzbu source diffu, review, approvals, pipeline evidence a merge policy,
- rozlíšiť reviewer, approver, eligible approver, Code Owner a security-policy approver,
- navrhnúť approval rules, reset/freshness správanie, unresolved-discussion policy a exception lifecycle,
- rozlíšiť branch, merge-request, merged-results a merge-train pipeline context,
- vybrať merge/squash/rebase stratégiu podľa traceability a mainline modelu,
- vysvetliť protected branch, branch rule, protected tag a unprotect permission,
- oddeliť allowed-to-push od allowed-to-merge a zabrániť direct-push bypassu,
- vysvetliť protected environment ako samostatnú runtime deployment boundary,
- navrhnúť allowed-to-deploy, deployment approval, protected variable a environment-scoped variable policy,
- používať review apps bez exposure produkčných secrets a bez neobmedzeného resource lifecycle,
- navrhnúť separation of duties a auditovateľný break-glass postup.

## Stav

| Téma | Status | Úroveň |
|---|---|---|
| Projects, groups a permissions | Learning | L2 |
| Merge requests a approvals | Learning | L2 |
| Protected branches a environments | Learning | L2 |
