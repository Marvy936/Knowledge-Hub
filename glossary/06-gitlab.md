# GitLab glossary entries

## Approval rule — GitLab

GitLab pravidlo definujúce počet required approvals, eligible users alebo groups a branch/policy scope merge requestu. Pozri [Merge requests a approvals](docs/06-gitlab/merge-requests-and-approvals.md).

## Branch rule — GitLab

Policy objekt aplikovaný na konkrétny branch alebo pattern, ktorý môže riadiť push, merge, force-push a Code Owner požiadavky. Pozri [Protected branches a environments](docs/06-gitlab/protected-branches-and-environments.md).

## Code Owner — GitLab

Používateľ alebo skupina priradená k paths v `CODEOWNERS`; pri správnej protected-branch konfigurácii môže byť jej approval required pred merge. Pozri [Merge requests a approvals](docs/06-gitlab/merge-requests-and-approvals.md).

## Direct membership — GitLab

Členstvo pridané priamo na konkrétny project alebo group, na rozdiel od accessu zdedeného z parent group alebo získaného sharingom. Pozri [Projects, groups a permissions](docs/06-gitlab/projects-groups-permissions.md).

## Effective role — GitLab

Najvyššia rola, ktorú používateľ získa zo všetkých relevantných direct, inherited a shared memberships na danom resource. Pozri [Projects, groups a permissions](docs/06-gitlab/projects-groups-permissions.md).

## Eligible approver — GitLab

Používateľ, ktorého membership, role a approval-rule context oprávňujú poskytnúť approval započítaný pre konkrétny merge request. Pozri [Merge requests a approvals](docs/06-gitlab/merge-requests-and-approvals.md).

## Environment-scoped variable — GitLab

CI/CD variable dostupná iba jobs, ktorých deklarovaný environment zodpovedá nastavenému scope alebo patternu. Pozri [Protected branches a environments](docs/06-gitlab/protected-branches-and-environments.md).

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

## Merge train — GitLab

Queue model, ktorý overuje viac merge requests v predpokladanom poradí ich integrácie do target branch, aby chránil mainline health pri concurrency. Pozri [Merge requests a approvals](docs/06-gitlab/merge-requests-and-approvals.md).

## Protected branch — GitLab

Branch s policy obmedzujúcou push, merge, force push, deletion a podľa konfigurácie Code Owner alebo approval behavior. Pozri [Protected branches a environments](docs/06-gitlab/protected-branches-and-environments.md).

## Protected environment — GitLab

GitLab environment s obmedzeným allowed-to-deploy alebo approval modelom pre citlivé runtime targety, napríklad production. Pozri [Protected branches a environments](docs/06-gitlab/protected-branches-and-environments.md).

## Protected variable — GitLab

CI/CD variable sprístupnená iba pipeline contextom na protected refs podľa GitLab trust pravidiel; stále vyžaduje bezpečný runner a pipeline kód. Pozri [Protected branches a environments](docs/06-gitlab/protected-branches-and-environments.md).

## Review app — GitLab

Dočasný dynamic environment vytvorený pre branch alebo merge request na overenie zmeny pred merge, s vlastným URL a cleanup lifecycle. Pozri [Protected branches a environments](docs/06-gitlab/protected-branches-and-environments.md).

## Subgroup — GitLab

Group vnorená v parent group, používaná na delegovanie ownershipu, členstva a policy pre podmnožinu projects. Pozri [Projects, groups a permissions](docs/06-gitlab/projects-groups-permissions.md).
