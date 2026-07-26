# GitLab glossary entries

## Access path — GitLab

Konkrétna cesta, cez ktorú subject získal capability nad resource-om, napríklad direct membership, parent-group inheritance, group sharing, custom role, protected-resource rule alebo token scope. Pozri [Projects, groups a permissions](docs/06-gitlab/projects-groups-permissions.md).

## Approval rule — GitLab

GitLab pravidlo definujúce počet required approvals, eligible users alebo groups a branch/policy scope merge requestu. Pozri [Merge requests a approvals](docs/06-gitlab/merge-requests-and-approvals.md).

## Artifact subject — GitLab CI

Identita pipeline outputu tvorená projektom, pipeline source-om, source alebo candidate SHA, resolved configuration digestom, producer jobom a attemptom, variantom/platformou, runner/toolchain subjectom a content digestom. Pozri [Artifacts a cache](docs/06-gitlab/artifacts-and-cache.md).

## Atomic publication — GitLab registry

Publication protocol `upload immutable content → over digesty → vytvor manifest alebo package version → read-back completeness → atomicky publikuj release reference`, s idempotency a reconciliation pri unknown outcome. Pozri [Container a package registry](docs/06-gitlab/container-and-package-registry.md).

## Branch rule — GitLab

Policy objekt aplikovaný na konkrétny branch alebo pattern, ktorý môže riadiť push, merge, force-push a Code Owner požiadavky. Pozri [Protected branches a environments](docs/06-gitlab/protected-branches-and-environments.md).

## Cache trust namespace — GitLab CI

Oddelený cache key/prefix a write policy podľa trust contextu, napríklad fork, non-protected, protected alebo release. Zabraňuje tomu, aby menej dôveryhodný writer ovplyvnil citlivejší build. Pozri [Artifacts a cache](docs/06-gitlab/artifacts-and-cache.md).

## Cleanup-incomplete verdict — GitLab Runner

Execution verdict označujúci, že script alebo output môže mať známy výsledok, ale worker runtime, workspace, procesy alebo credentials neboli dôveryhodne odstránené. Vyžaduje containment a reconciliation pred retry alebo ďalším použitím poolu. Pozri [Runners a executors](docs/06-gitlab/runners-and-executors.md).

## Code Owner — GitLab

Používateľ alebo skupina priradená k paths v `CODEOWNERS`; pri správnej protected-branch konfigurácii môže byť jej approval required pred merge. Pozri [Merge requests a approvals](docs/06-gitlab/merge-requests-and-approvals.md).

## Configuration identity — GitLab CI

Reprodukčný subject pipeline zahŕňajúci source SHA, pipeline source, root CI revision, resolved configuration digest, include/component identities, policy a variable context a runner/executor identity. Pozri [GitLab CI/CD syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md).

## Continuous rescanning — GitLab

Opakované vyhodnotenie podporovaných package, SBOM a image digestov voči novej vulnerability intelligence bez potreby source zmeny, s následným mapovaním na releases, effective deployments, ownerov a exposure. Pozri [Security scanning](docs/06-gitlab/security-scanning.md).

## Deployed-artifact correlation — GitLab

Auditovateľná väzba `finding/advisory → component alebo image digest → release manifest → deployment record → effective runtime digest → environment, owner a exposure`. Umožňuje odlíšiť opravu v source od skutočne opraveného runtime-u. Pozri [Security scanning](docs/06-gitlab/security-scanning.md).

## Deployment state divergence — GitLab

Rozdiel medzi desired state-om, GitLab recorded state-om a effective runtime state-om deploymentu. Môže vzniknúť pri asynchrónnej reconciliation, nesprávnom targete, stale generation, partial mutation alebo drift-e. Pozri [Environments, deployments a releases](docs/06-gitlab/environments-deployments-releases.md).

## Deployment subject — GitLab

Presná identity runtime mutation tvorená artifact digestom, rendered config alebo infrastructure revision, trusted deployment job definition, target environmentom, actor/job identity a rollout policy. Pozri [Protected branches a environments](docs/06-gitlab/protected-branches-and-environments.md) a [Environments, deployments a releases](docs/06-gitlab/environments-deployments-releases.md).

## Direct membership — GitLab

Členstvo pridané priamo na konkrétny project alebo group, na rozdiel od accessu zdedeného z parent group alebo získaného sharingom. Pozri [Projects, groups a permissions](docs/06-gitlab/projects-groups-permissions.md).

## Effective access — GitLab

Výsledná množina capabilities subjectu nad konkrétnym resource-om po vyhodnotení všetkých direct, inherited, shared, tokenových, custom-role a resource-policy access paths. Pozri [Projects, groups a permissions](docs/06-gitlab/projects-groups-permissions.md).

## Effective branch policy — GitLab

Capability-specific výsledok všetkých project a inherited group branch rules, ktoré matchujú konkrétny branch alebo pattern. Nesmie sa odhadovať iba podľa jednej viditeľnej rule. Pozri [Protected branches a environments](docs/06-gitlab/protected-branches-and-environments.md).

## Effective role — GitLab

Najvyššia rola, ktorú používateľ získa zo všetkých relevantných direct, inherited a shared memberships na danom resource. Pozri [Projects, groups a permissions](docs/06-gitlab/projects-groups-permissions.md).

## Effective value — GitLab CI

Hodnota, ktorú konkrétny pipeline alebo job skutočne použije po vyhodnotení všetkých variable sources, precedence, protected/environment scope-u, availability phase a downstream forwarding-u. Pozri [Variables a secrets](docs/06-gitlab/variables-and-secrets.md).

## Eligible approver — GitLab

Používateľ, ktorého membership, role a approval-rule context oprávňujú poskytnúť approval započítaný pre konkrétny merge request. Pozri [Merge requests a approvals](docs/06-gitlab/merge-requests-and-approvals.md).

## Environment identity — GitLab

Kanonické mapovanie GitLab environment name a tieru na skutočný cloud account, cluster, namespace, region, data/config boundary, ownera, protection policy a runtime identity. Pozri [Environments, deployments a releases](docs/06-gitlab/environments-deployments-releases.md).

## Environment-scoped variable — GitLab

CI/CD variable dostupná iba jobs, ktorých deklarovaný environment zodpovedá nastavenému scope alebo patternu. Pozri [Protected branches a environments](docs/06-gitlab/protected-branches-and-environments.md).

## Expected job inventory — GitLab CI

Explicitný manifest jobs, child pipelines a reports, ktoré musia pre konkrétny pipeline subject existovať alebo preukázateľne nebyť applicable. Odlišuje complete pass od false-green runu s ticho chýbajúcou evidence. Pozri [GitLab CI/CD syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md).

## Expected output inventory — GitLab CI

Manifest artifacts, reports, shards, variants alebo platforms, ktoré musí konkrétny producer/fan-in workflow vytvoriť. Actual-only agregácia bez tohto manifestu môže ticho vyhodnotiť missing output ako pass. Pozri [Artifacts a cache](docs/06-gitlab/artifacts-and-cache.md).

## Expected scanner inventory — GitLab

Manifest security controls, analyzer jobs, reportov, componentov a platforiem, ktoré musia existovať alebo mať explicitný not-applicable/unsupported verdict pre konkrétny scan subject. Chýbajúca položka znamená incomplete evidence, nie clean result. Pozri [Security scanning](docs/06-gitlab/security-scanning.md).

## GitLab group

Namespace a organizačná boundary obsahujúca projects a subgroups, ktorá môže poskytovať zdedené membership, settings, variables, runners a governance. Pozri [Projects, groups a permissions](docs/06-gitlab/projects-groups-permissions.md).

## GitLab merge request

Workflow objekt spájajúci source a target branch, diff, commits, review, discussions, approvals, pipeline evidence a merge result. Pozri [Merge requests a approvals](docs/06-gitlab/merge-requests-and-approvals.md).

## GitLab namespace

Hierarchický path a ownership context pre user, group, subgroup alebo project resources v GitLabe. Pozri [Projects, groups a permissions](docs/06-gitlab/projects-groups-permissions.md).

## GitLab project

Základná GitLab pracovná jednotka obsahujúca repository a podľa konfigurácie merge requests, issues, CI/CD, variables, registries, environments, security a membership. Pozri [Projects, groups a permissions](docs/06-gitlab/projects-groups-permissions.md).

## GitOps deployment correlation — GitLab

Väzba medzi source pipeline, release manifestom, desired-state repository commitom, controller reconciliation ID, runtime targetom a effective digestom. Odlišuje úspešný configuration request od dokončeného deploymentu. Pozri [Environments, deployments a releases](docs/06-gitlab/environments-deployments-releases.md).

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

## Registry publication subject — GitLab

Presná identity publish rozhodnutia zahŕňajúca source/candidate SHA, resolved pipeline config, build jobs a attempts, artifact a platform digests, runner/toolchain provenance, version, SBOM/scan/signature evidence, publisher identity, namespace a release policy. Pozri [Container a package registry](docs/06-gitlab/container-and-package-registry.md).

## Release manifest — GitLab

Immutable alebo versionované mapovanie pomenovaného release-u na component digests/package checksums, config, infrastructure a schema revisions, security evidence a support metadata. Pozri [Environments, deployments a releases](docs/06-gitlab/environments-deployments-releases.md).

## Resolved configuration — GitLab CI

Výsledná GitLab CI konfigurácia po načítaní a zlúčení root súboru, includes a components a po aplikovaní konfiguračných semantics. Je skutočným review a provenance subjectom pipeline, nie iba root `.gitlab-ci.yml`. Pozri [GitLab CI/CD syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md).

## Review app — GitLab

Dočasný dynamic environment vytvorený pre branch alebo merge request na overenie zmeny pred merge, s vlastným URL a cleanup lifecycle. Pozri [Protected branches a environments](docs/06-gitlab/protected-branches-and-environments.md).

## Runner execution subject — GitLab

Identity job runtime-u zahŕňajúca source a resolved config, job attempt, runner manager/pool, worker ID a image digest, executor, helper image, architecture, cache/artifact inputs, credentials, network policy a resource limits. Pozri [Runners a executors](docs/06-gitlab/runners-and-executors.md).

## Runtime digest inventory — GitLab registry

Auditovateľné mapovanie requested image/package reference na resolved OCI index alebo package checksum, platform manifest digest, pull/mirror source a digest skutočne používaný aktívnym workloadom. Pozri [Container a package registry](docs/06-gitlab/container-and-package-registry.md).

## Security evidence verdict — GitLab

Výsledok, ktorý odlišuje complete clean scan, findings, incomplete scanner/report inventory, invalid subject, analyzer/tool error, unsupported coverage a approved skip. Zelený job bez complete report evidence nie je clean verdict. Pozri [Security scanning](docs/06-gitlab/security-scanning.md).

## Security scan subject — GitLab

Immutable source, resolved dependency graph, SBOM, package checksum, OCI platform digest, IaC plan alebo deployment identity, ku ktorej patria analyzer execution, report a finding evidence. Pozri [Security scanning](docs/06-gitlab/security-scanning.md).

## Stale approval — GitLab

Approval, ktorý bol udelený pre starší source SHA, target context, candidate alebo policy revision a už neposkytuje dôkaz pre aktuálny merge subject. Pozri [Merge requests a approvals](docs/06-gitlab/merge-requests-and-approvals.md).

## Subgroup — GitLab

Group vnorená v parent group, používaná na delegovanie ownershipu, členstva a policy pre podmnožinu projects. Pozri [Projects, groups a permissions](docs/06-gitlab/projects-groups-permissions.md).

## Vulnerability record — GitLab

Dlhšie žijúci spravovaný security risk odvodený z jedného alebo viacerých findings, s ownerom, contextual riskom, remediation SLA, exception/expiration a verification históriou. Pozri [Security scanning](docs/06-gitlab/security-scanning.md).