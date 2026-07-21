# GitLab

Táto sekcia aplikuje všeobecné Git, testing a CI/CD princípy na konkrétny GitLab platform model. Cieľom nie je memorovať polohu nastavení v UI, ale rozumieť namespaces, inheritance, trust boundaries, merge policy, protected resources, pipeline execution, registries, deployment lifecycle a security scanning.

GitLab features, role permissions, syntax a dostupnosť niektorých controls sa menia podľa verzie, offeringu a tieru. Pri produkčnom návrhu treba vždy overiť aktuálnu dokumentáciu a konfiguráciu konkrétnej inštancie.

## Predpoklady

Odporúča sa najprv dokončiť:

- [Git and Automation Basics](../03-git-and-automation/README.md),
- [Testing and Software Quality](../04-testing-and-quality/README.md),
- [CI/CD and Release Engineering](../05-ci-cd-and-release/README.md).

## Odporúčané poradie

1. [Projects, groups a permissions](projects-groups-permissions.md)
2. [Merge requests a approvals](merge-requests-and-approvals.md)
3. [Protected branches a environments](protected-branches-and-environments.md)
4. [GitLab CI/CD syntax](gitlab-ci-cd-syntax.md)
5. [Runners a executors](runners-and-executors.md)
6. [Variables a secrets](variables-and-secrets.md)
7. [Artifacts a cache](artifacts-and-cache.md)
8. [Container a package registry](container-and-package-registry.md)
9. [Environments, deployments a releases](environments-deployments-releases.md)
10. [Security scanning](security-scanning.md)

Po tejto sekcii nasleduje Infrastructure as Code and Configuration Management. GitLab pipeline, registry, identity a environment model sa tam použije na validáciu, plánovanie a bezpečné aplikovanie Terraform a Ansible zmien.

## Cieľ zvládnutia

Po dokončení sekcie má byť možné:

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
- navrhnúť separation of duties a auditovateľný break-glass postup,
- vysvetliť GitLab pipeline configuration lifecycle od `include` cez `workflow:rules`, job rules a DAG až po runner scheduling,
- používať `stages`, `needs`, `rules`, `default`, hidden jobs, `extends` a versionované CI/CD components bez nečitateľného inheritance modelu,
- diagnostikovať duplicate pipelines, missing jobs, invalid DAG a mutable include dependencies,
- rozlíšiť GitLab Runner od executora a navrhnúť runner scope, tags, protected context a concurrency,
- porovnať Docker, Kubernetes, autoscaling, instance a shell executor podľa isolation, capacity, costu a trust boundary,
- navrhnúť ephemeral runner, workload identity, resource limits, egress policy a bezpečný image-build model,
- rozlíšiť public configuration, CI/CD variable, secret, ID token a short-lived credential,
- používať masked, hidden, protected, file-type a environment-scoped variables bez falošného pocitu bezpečnosti,
- integrovať external secret provider cez OIDC claims a minimum-scope workload identity,
- rozlíšiť job artifact, report artifact, release artifact a cache,
- navrhnúť artifact identity, access, retention a explicitný DAG transfer,
- vytvoriť cache key, distributed cache a trust namespace bez cache poisoning-u,
- používať Container a Package Registry s immutable versions, digests, scoped identities a cleanup policy,
- aplikovať build-once-promote-many, SBOM, provenance, signatures a multi-platform image workflow,
- rozlíšiť environment, deployment, review app, deployment record a GitLab Release,
- navrhnúť protected deployment, concurrency, outdated-deployment prevention, cleanup a release asset lifecycle,
- vrstviť SAST, dependency scanning, secret detection, container scanning, DAST, API a IaC scanning podľa attack surface,
- rozlíšiť security finding, vulnerability record, report artifact, policy, gate a exception lifecycle,
- overovať scan coverage, analyzer success, continuous rescanning a väzbu findings na reálne nasadené artifacts.

## Stav

| Téma | Status | Úroveň |
|---|---|---|
| Projects, groups a permissions | Learning | L2 |
| Merge requests a approvals | Learning | L2 |
| Protected branches a environments | Learning | L2 |
| GitLab CI/CD syntax | Learning | L2 |
| Runners a executors | Learning | L2 |
| Variables a secrets | Learning | L2 |
| Artifacts a cache | Learning | L2 |
| Container a package registry | Learning | L2 |
| Environments, deployments a releases | Learning | L2 |
| Security scanning | Learning | L2 |
