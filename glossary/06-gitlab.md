# GitLab glossary entries

## Access path — GitLab

Konkrétna cesta, cez ktorú subject získal capability nad resource-om, napríklad direct membership, parent-group inheritance, group sharing, custom role, protected-resource rule alebo token scope. Pozri [Projects, groups a permissions](docs/06-gitlab/projects-groups-permissions.md).

## Approval rule — GitLab

GitLab pravidlo definujúce počet required approvals, eligible users alebo groups a branch/policy scope merge requestu. Pozri [Merge requests a approvals](docs/06-gitlab/merge-requests-and-approvals.md).

## Branch rule — GitLab

Policy objekt aplikovaný na konkrétny branch alebo pattern, ktorý môže riadiť push, merge, force-push a Code Owner požiadavky. Pozri [Protected branches a environments](docs/06-gitlab/protected-branches-and-environments.md).

## Code Owner — GitLab

Používateľ alebo skupina priradená k paths v `CODEOWNERS`; pri správnej protected-branch konfigurácii môže byť jej approval required pred merge. Pozri [Merge requests a approvals](docs/06-gitlab/merge-requests-and-approvals.md).

## Configuration identity — GitLab CI

Reprodukčný subject pipeline zahŕňajúci source SHA, pipeline source, root CI revision, resolved configuration digest, include/component identities, policy a variable context a runner/executor identity. Pozri [GitLab CI/CD syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md).

## Deployment subject — GitLab

Presná identity runtime mutation tvorená artifact digestom, rendered config alebo infrastructure revision, trusted deployment job definition, target environmentom, actor/job identity a rollout policy. Pozri [Protected branches a environments](docs/06-gitlab/protected-branches-and-environments.md).

## Direct membership — GitLab

Členstvo pridané priamo na konkrétny project alebo group, na rozdiel od accessu zdedeného z parent group alebo získaného sharingom. Pozri [Projects, groups a permissions](docs/06-gitlab/projects-groups-permissions.md).

## Effective access — GitLab

Výsledná množina capabilities subjectu nad konkrétnym resource-om po vyhodnotení všetkých direct, inherited, shared, tokenových, custom-role a resource-policy access paths. Pozri [Projects, groups a permissions](docs/06-gitlab/projects-groups-permissions.md).

## Effective branch policy — GitLab

Capability-specific výsledok všetkých project a inherited group branch rules, ktoré matchujú konkrétny branch alebo pattern. Nesmie sa odhadovať iba podľa jednej viditeľnej rule. Pozri [Protected branches a environments](docs/06-gitlab/protected-branches-and-environments.md).

## Effective role — GitLab

Najvyššia rola, ktorú používateľ získa zo všetkých relevantných direct, inherited a shared memberships na danom resource. Pozri [Projects, groups a permissions](docs/06-gitlab/projects-groups-permissions.md).

## Eligible approver — GitLab

Používateľ, ktorého membership, role a approval-rule context oprávňujú poskytnúť approval započítaný pre konkrétny merge request. Pozri [Merge requests a approvals](docs/06-gitlab/merge-requests-and-approvals.md).

## Environment-scoped variable — GitLab

CI/CD variable dostupná iba jobs, ktorých deklarovaný environment zodpovedá nastavenému scope alebo patternu. Pozri [Protected branches a environments](docs/06-gitlab/protected-branches-and-environments.md).

## Expected job inventory — GitLab CI

Explicitný manifest jobs, child pipelines a reports, ktoré musia pre konkrétny pipeline subject existovať alebo preukázateľne nebyť applicable. Odlišuje complete pass od false-green runu s ticho chýbajúcou evidence. Pozri [GitLab CI/CD syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md).

## GitLab group

Namespace a organizačná boundary obsahujúca projects a subgroups, ktorá môže poskytovať zdedené membership, settings, variables, runners a governance. Pozri [Projects, groups a permissions](docs/06-gitlab/projects-groups-permissions.md).

## GitLab merge request

Workflow objekt spájajúci source a target branch, diff, commits, review, discussions, approvals, pipeline evidence a merge result. Pozri [Merge requests a approvals](docs/06-gitlab/merge-requests-and-approvals.md).

## GitLab namespace

Hierarchický path a ownership context pre user, group, subgroup alebo project resources v GitLabe. Pozri [Projects, groups a permissions](docs/06-gitlab/projects-groups-permissions.md).

## GitLab project

Základná GitLab pracovná jednotka obsahujúca repository a podľa konfigurácie merge requests, issues, CI/CD, variables, registries, environments, security a membership. Pozri [Projects, groups a permissions](docs/06-gitlab/projects-groups-permissions.md).

## Group sharing — GitLab

Udelenie accessu projektu alebo group členom inej group s definovaným maximum role scope-om. Pozri [Projects, groups a permissions](docs/06-gitlab/projects-groups-permissions.md).

## Inherited membership — GitLab

Access získaný cez membership v parent group alebo inom hierarchicky relevantnom namespace namiesto priameho pridania na project. Pozri [Projects, groups a permissions](docs/06-gitlab/projects-groups-permissions.md).

## Merge decision subject — GitLab

Presný obsah a context merge rozhodnutia: MR ID, source SHA, target alebo merge-base state, diff identity, merged-result alebo merge-train candidate a relevantná policy revision. Pozri [Merge requests a approvals](docs/06-gitlab/merge-requests-and-approvals.md).

## Merge train — GitLab

Queue model, ktorý overuje viac merge requests v predpokladanom poradí ich integrácie do target branch, aby chránil mainline health pri concurrency. Pozri [Merge requests a approvals](docs/06-gitlab/merge-requests-and-approvals.md).

## Protected branch — GitLab

Branch s policy obmedzujúcou push, merge, force push, deletion a podľa konfigurácie Code Owner alebo approval behavior. Pozri [Protected branches a environments](docs/06-gitlab/protected-branches-and-environments.md).

## Protected environment — GitLab

GitLab environment s obmedzeným allowed-to-deploy alebo approval modelom pre citlivé runtime targety, napríklad production. Pozri [Protected branches a environments](docs/06-gitlab/protected-branches-and-environments.md).

## Protected variable — GitLab

CI/CD variable sprístupnená iba pipeline contextom na protected refs podľa GitLab trust pravidiel; stále vyžaduje bezpečný runner a pipeline kód. Pozri [Protected branches a environments](docs/06-gitlab/protected-branches-and-environments.md).

## Resolved configuration — GitLab CI

Výsledná GitLab CI konfigurácia po načítaní a zlúčení root súboru, includes a components a po aplikovaní konfiguračných semantics. Je skutočným review a provenance subjectom pipeline, nie iba root `.gitlab-ci.yml`. Pozri [GitLab CI/CD syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md).

## Review app — GitLab

Dočasný dynamic environment vytvorený pre branch alebo merge request na overenie zmeny pred merge, s vlastným URL a cleanup lifecycle. Pozri [Protected branches a environments](docs/06-gitlab/protected-branches-and-environments.md).

## Stale approval — GitLab

Approval, ktorý bol udelený pre starší source SHA, target context, candidate alebo policy revision a už neposkytuje dôkaz pre aktuálny merge subject. Pozri [Merge requests a approvals](docs/06-gitlab/merge-requests-and-approvals.md).

## Subgroup — GitLab

Group vnorená v parent group, používaná na delegovanie ownershipu, členstva a policy pre podmnožinu projects. Pozri [Projects, groups a permissions](docs/06-gitlab/projects-groups-permissions.md).