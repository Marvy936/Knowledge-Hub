# GitLab CI/CD and security glossary entries

## CI/CD component — GitLab

Versionovaný reusable pipeline contract publikovaný v GitLabe a používaný cez `include:component` s explicitnou verziou, inputs a definovaným behaviorom. Pozri [GitLab CI/CD syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md).

## Configuration subject — GitLab CI/CD

Presná identity pipeline compilation rozhodnutia tvorená source alebo candidate SHA, pipeline source, root CI revision, resolved include/component versions, resolved configuration digest, expected job inventory a relevantný runner/executor context. Pozri [GitLab CI/CD syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md).

## Container scanning — GitLab

Security scan konkrétneho container image digestu zameraný najmä na známe vulnerabilities v OS packages a podľa capability scanneru aj ďalšom image obsahu. Pozri [Security scanning](docs/06-gitlab/security-scanning.md).

## Continuous rescanning — security

Opakované vyhodnocovanie už známych SBOM components, dependencies alebo image digests po aktualizácii advisory databáz bez potreby source zmeny. Pozri [Security scanning](docs/06-gitlab/security-scanning.md).

## Dependency scanning — GitLab

Analýza direct a transitive software dependencies podľa manifestov, lockfiles alebo SBOM a ich porovnanie s vulnerability advisory databázou. Pozri [Security scanning](docs/06-gitlab/security-scanning.md).

## Deployment freeze — GitLab

Časovo definovaná GitLab policy obmedzujúca plánované deploymenty do citlivého environmentu, s explicitným emergency a exception modelom. Pozri [Environments, deployments a releases](docs/06-gitlab/environments-deployments-releases.md).

## Distributed cache — GitLab Runner

CI cache uložená v shared backend-e, typicky object storage, aby ju mohli používať viaceré alebo autoscaled runners. Pozri [Artifacts a cache](docs/06-gitlab/artifacts-and-cache.md).

## Docker executor — GitLab Runner

Executor, ktorý spúšťa každý job v containeri vytvorenom z definovaného image a môže pripájať service containers, volumes a cache. Pozri [Runners a executors](docs/06-gitlab/runners-and-executors.md).

## Dynamic child pipeline — GitLab

Child pipeline, ktorého CI configuration je vytvorená alebo zvolená počas parent pipeline podľa repository alebo runtime metadata. Pozri [GitLab CI/CD syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md).

## Dynamic environment — GitLab

Dočasný environment vytvorený pre branch, merge request alebo inú krátkodobú jednotku a ukončený stop jobom, TTL alebo reconcilerom. Pozri [Environments, deployments a releases](docs/06-gitlab/environments-deployments-releases.md).

## Ephemeral runner

Runner worker alebo execution instance vytvorená pre jeden job alebo krátky workload interval a po dokončení zrušená, čím sa znižuje cross-job state contamination. Pozri [Runners a executors](docs/06-gitlab/runners-and-executors.md).

## Executor — GitLab Runner

Mechanizmus určujúci runtime jobu, napríklad Docker container, Kubernetes pod, autoscaled instance alebo host shell. Pozri [Runners a executors](docs/06-gitlab/runners-and-executors.md).

## Expected job inventory — GitLab CI/CD

Strojovo overiteľná množina jobs, shards, child pipelines a reports, ktoré musia pre konkrétny configuration subject vzniknúť alebo byť explicitne označené ako not applicable. Odlišuje complete pass od false-green pipeline s chýbajúcou evidence. Pozri [GitLab CI/CD syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md).

## External secret provider — GitLab CI/CD

Secret-management systém, z ktorého job explicitne načíta citlivú hodnotu po overení federovanej alebo inej scoped identity. Pozri [Variables a secrets](docs/06-gitlab/variables-and-secrets.md).

## File-type variable — GitLab

CI/CD variable, ktorej hodnota je zapísaná do dočasného súboru a environment variable obsahuje path k tomuto súboru. Pozri [Variables a secrets](docs/06-gitlab/variables-and-secrets.md).

## GitLab cache

Odstrániteľná pipeline optimalizácia na znovupoužitie dependencies alebo intermediate dát; correctness pipeline nesmie závisieť od cache hitu. Pozri [Artifacts a cache](docs/06-gitlab/artifacts-and-cache.md).

## GitLab Container Registry

GitLab-integrovaný registry pre container alebo OCI images s project/group namespace, access controlom a CI/CD authentication workflowom. Pozri [Container a package registry](docs/06-gitlab/container-and-package-registry.md).

## GitLab deployment

Záznam úspešného alebo neúspešného nasadenia z pipeline jobu do konkrétneho GitLab environmentu, spojený s commitom, jobom, časom a statusom. Pozri [Environments, deployments a releases](docs/06-gitlab/environments-deployments-releases.md).

## GitLab environment

Pomenovaný runtime deployment target, ktorý môže mať URL, variables, protection, deployment history a static alebo dynamic lifecycle. Pozri [Environments, deployments a releases](docs/06-gitlab/environments-deployments-releases.md).

## GitLab job artifact

Súborový alebo reportový výstup konkrétneho CI/CD jobu uložený GitLabom na downstream použitie, diagnostiku alebo pipeline evidence. Pozri [Artifacts a cache](docs/06-gitlab/artifacts-and-cache.md).

## GitLab Package Registry

GitLab-integrovaný registry pre podporované package-manager formats a generic packages určené na versionovanú distribúciu dependencies a release assets. Pozri [Container a package registry](docs/06-gitlab/container-and-package-registry.md).

## GitLab pipeline configuration

Vyriešená deklarácia pipeline vytvorená z `.gitlab-ci.yml`, includes, defaults, rules, jobs, dependencies a execution metadata pri vzniku pipeline. Pozri [GitLab CI/CD syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md).

## GitLab Release

GitLab objekt viazaný typicky na Git tag, ktorý zhromažďuje release name, notes, timestamp, asset links a distribučno-prevádzkové metadata bez rebuildu artifactov. Pozri [Environments, deployments a releases](docs/06-gitlab/environments-deployments-releases.md).

## GitLab Runner

Agent, ktorý prijíma eligible CI/CD jobs z GitLabu a vykonáva ich pomocou nakonfigurovaného executora v definovanej trust boundary. Pozri [Runners a executors](docs/06-gitlab/runners-and-executors.md).

## GitLab SAST

Static Application Security Testing integrované do GitLab CI/CD na detekciu potenciálnych vulnerabilities v source code pomocou language-specific analyzers a rules. Pozri [Security scanning](docs/06-gitlab/security-scanning.md).

## Hidden job — GitLab CI/CD

Top-level CI configuration block s názvom začínajúcim bodkou, ktorý sa nespúšťa priamo a slúži ako reusable configuration pre `extends` alebo references. Pozri [GitLab CI/CD syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md).

## Hidden variable — GitLab

Masked CI/CD variable, ktorej hodnotu po uložení nemožno znovu zobraziť v GitLab UI; job s prístupom ju však stále môže použiť. Pozri [Variables a secrets](docs/06-gitlab/variables-and-secrets.md).

## ID token — GitLab CI/CD

Krátkodobý signed OIDC token vydaný jobu s definovaným audience a claims, používaný na federované overenie voči cloud alebo secret provideru. Pozri [Variables a secrets](docs/06-gitlab/variables-and-secrets.md).

## Job rules — GitLab

Zhora nadol vyhodnocované podmienky, ktoré pri vytvorení pipeline rozhodujú, či job vznikne a aké `when`, variables, `needs` alebo failure správanie dostane. Pozri [GitLab CI/CD syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md).

## Kubernetes executor — GitLab Runner

Executor, ktorý pre CI/CD job vytvorí Kubernetes pod s build, helper a podľa konfigurácie service containers. Pozri [Runners a executors](docs/06-gitlab/runners-and-executors.md).

## Latest successful artifact — GitLab

Artifact z najnovšieho úspešného pipeline na danom ref-e, ktorý môže GitLab podľa nastavenia uchovávať nezávisle od bežnej expiration policy. Pozri [Artifacts a cache](docs/06-gitlab/artifacts-and-cache.md).

## Masked variable — GitLab

CI/CD variable, ktorej hodnota spĺňajúca GitLab constraints sa pri výpise do job logu nahrádza maskovaným textom; masking nezabraňuje úmyselnej exfiltration jobom. Pozri [Variables a secrets](docs/06-gitlab/variables-and-secrets.md).

## `needs` DAG — GitLab

Explicitný directed acyclic graph job dependencies vytvorený cez `needs`, ktorý umožňuje jobs spustiť po skutočných upstream dependencies bez čakania na celé stages. Pozri [GitLab CI/CD syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md).

## Outdated deployment — GitLab

Deployment zo staršieho pipeline, ktorý sa pokúša prepísať environment po tom, čo už bol nasadený novší pipeline alebo artifact. Pozri [Environments, deployments a releases](docs/06-gitlab/environments-deployments-releases.md).

## Pipeline creation policy — GitLab CI/CD

Versionovaný `workflow:rules` contract určujúci, pre ktoré pipeline sources, refs a dostupný variable context má pipeline vzniknúť a aký účel daný run plní. Pozri [GitLab CI/CD syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md).

## Pipeline verdict completeness — GitLab

Vlastnosť pipeline verdictu dokazujúca, že všetky required jobs, shards, child/downstream pipelines, reports a artifacts pre daný subject vznikli a boli zahrnuté do gate rozhodnutia. Pozri [GitLab CI/CD syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md).

## Report artifact — GitLab

Machine-readable job artifact v podporovanej schéme, ktorý GitLab interpretuje pre test, coverage, code-quality, dotenv, SBOM alebo security výsledky. Pozri [Artifacts a cache](docs/06-gitlab/artifacts-and-cache.md).

## Resolved configuration — GitLab CI/CD

Konečný pipeline YAML model po spracovaní includes, components, defaults, inheritance, references a rules-relevantnej konfigurácie. Pozri [GitLab CI/CD syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md).

## Resource group — GitLab CI/CD

Pipeline mechanizmus serializujúci jobs, ktoré mutujú rovnaký environment alebo shared resource, aby sa zabránilo súbežným konfliktujúcim operáciám. Pozri [GitLab CI/CD syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md).

## Runner manager

Dlhšie žijúci GitLab Runner proces alebo service, ktorý polluje job queue a pomocou executora vytvára job runtimes alebo autoscaled workers. Pozri [Runners a executors](docs/06-gitlab/runners-and-executors.md).

## Runner system failure

Job failure spôsobený runnerom, executorom, infrastructure alebo prepare/cleanup vrstvou namiesto samotného user scriptu. Pozri [Runners a executors](docs/06-gitlab/runners-and-executors.md).

## Security report artifact — GitLab

Machine-readable analyzer report, ktorý GitLab spracúva na zobrazenie security findings v pipeline, merge requeste alebo vulnerability-management vrstvách. Pozri [Security scanning](docs/06-gitlab/security-scanning.md).

## Secret push protection — GitLab

Pre-receive alebo push-time kontrola, ktorá deteguje podporované secret patterns pred prijatím commitu a môže push zablokovať. Pozri [Security scanning](docs/06-gitlab/security-scanning.md).

## Shell executor — GitLab Runner

Executor spúšťajúci CI/CD job priamo na runner hoste s jeho používateľskými oprávneniami a slabou isolation medzi workloadom a hostom. Pozri [Runners a executors](docs/06-gitlab/runners-and-executors.md).

## Static environment — GitLab

Dlhodobo opakovane používaný environment s pevným názvom, napríklad staging alebo production. Pozri [Environments, deployments a releases](docs/06-gitlab/environments-deployments-releases.md).

## Vulnerability record — GitLab

Dlhodobejšie spravovaný security objekt odvodený zo scan findingu, ktorý má status, severity, location, identifiers, triage a remediation lifecycle. Pozri [Security scanning](docs/06-gitlab/security-scanning.md).

## `workflow:rules` — GitLab

Pipeline-level podmienky vyhodnotené pri vytvorení pipeline, ktoré rozhodujú, či pipeline vznikne pre konkrétny source, ref a dostupný variable context. Pozri [GitLab CI/CD syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md).

## Workload identity federation — CI/CD

Model, v ktorom job vymení krátkodobý signed identity token za scoped cloud alebo secret-provider credential bez uloženia dlhodobého access key v GitLabe. Pozri [Variables a secrets](docs/06-gitlab/variables-and-secrets.md).

## `CI_JOB_TOKEN`

Krátkodobá GitLab job identity používaná na podporované API, artifact, package, registry alebo cross-project operácie podľa explicitného access modelu. Pozri [Variables a secrets](docs/06-gitlab/variables-and-secrets.md).