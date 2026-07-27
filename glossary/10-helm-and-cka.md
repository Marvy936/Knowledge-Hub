# Helm and CKA glossary entries

## Application version — Helm

Version aplikácie deklarovaná chart metadata fieldom `appVersion`; je informačná a nie je automaticky chart version, image tag ani release revision. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Chart artifact generation

Immutable packaged alebo OCI chart artifact vytvorený z konkrétneho source commit-u, dependency locku a build workflowu a identifikovaný version/digest identity. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Chart repository — Helm

HTTP repository model pre publikovanie packaged Helm charts a index metadata, alternatívny k OCI registry distribution. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Chart version — Helm

Semantic version package contractu uvedená v `Chart.yaml`, ktorá identifikuje konkrétnu verziu templates, defaults, metadata a dependencies. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Effective values — Helm

Výsledná redigovaná konfigurácia po aplikovaní chart defaults, parent/subchart scope-u, zoradených values files a CLI overrides pre konkrétnu release operáciu. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Forbidden release outcome

Explicitne zakázaný výsledok Helm release-u, napríklad aktivovaný legacy path, mutable artifact, duplicate business side effect, chýbajúci endpoint alebo secret leak. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Helm

Kubernetes package, templating a release-lifecycle tool, ktorý renderuje charts na Kubernetes manifests a uchováva release metadata bez vlastného serverového Tiller componentu. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Helm chart

Versionovaný balík obsahujúci `Chart.yaml`, default values, Kubernetes templates, voliteľné CRDs, dependencies a pomocné files. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Helm decommission subject

Kompletný inventár Helm-managed, retained, hook-created, cluster-scoped, storage a external resources, credentials, dát a evidence potrebný na bezpečné ukončenie release-u. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Helm release

Konkrétna pomenovaná inštancia chartu nasadená do Kubernetes namespace-u s effective values, rendered manifestom, statusom a revision history. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Helm release acceptance

Verdikt spájajúci chart, dependency, values, manifest, release revision, live object, workload artifact a business outcome identity po install alebo upgrade operácii. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Helm release revision

Sekvenčné číslo konkrétnej install, upgrade alebo rollback verzie Helm release-u; nie je to Kubernetes Deployment revision ani Git commit. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Helm release state

Metadata, chart/configuration a rendered manifest uložené Helm storage driverom v clustri pre konkrétnu release revision. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Helm release subject

Exact cluster, namespace, release name, Helm tool/apply mode, chart/dependency/values/manifest identities, target revision a business operation, ku ktorým sa viaže release verdict. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Helm revision evidence

Korelačný záznam spájajúci source commit, chart a dependency artifacts, effective values, rendered manifest, Helm revision, Kubernetes object generations a runtime/business outcome. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Helm template

Go-template source file v chart `templates/` directory, ktorý Helm renderuje s values, release metadata a cluster capabilities na Kubernetes manifest. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Helm unknown-operation outcome

Stav, keď Helm command timeoutol alebo zlyhal, ale časť API requests, hooks, rolloutov alebo external side effects mohla prebehnúť; pred retry je potrebný read-back. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## OCI chart

Helm chart artifact distribuovaný cez OCI-compatible registry s version/digest identity a registry authentication modelom. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Admitted/live/process-loaded state chain — Helm

Porovnanie rendered intentu s API-admitted objektom, current live resource-om a konfiguráciou skutočne načítanou application procesom. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Release mutation boundary — Helm

Hranica, na ktorej Helm mení viac Kubernetes objektov a hooks bez garancie jednej atomickej transakcie alebo automatického zvrátenia durable side effects. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Render generation — Helm

Konkrétny výpočet chartu, dependency graphu, effective values, release contextu, capabilities, Helm engine-u a voliteľných dynamic inputs na rendered manifest. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Rendered manifest — Helm

Výsledný Kubernetes YAML vytvorený kombináciou chart templates, effective values, release contextu a capabilities pred aplikovaním na API server. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Rendered-manifest digest

Hash alebo iná immutable identity final rendered manifest setu používaná na koreláciu source inputs, Helm revision a live deployment evidence. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Values — Helm

Konfiguračné vstupy chart templates získané z default `values.yaml`, override files a command-line overrides. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Values bundle generation

Versionovaný a redigovaný inventár všetkých values sources, ich poradia, overrides, schema verdictu a digestu pre jednu release operáciu. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Values precedence — Helm

Merge a override poradie, v ktorom neskoršie values files a explicitné command-line overrides prepisujú chart defaults a skoršie values. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Values schema — Helm

Voliteľný `values.schema.json` contract validujúci typy, required fields, enums a štruktúru Helm values pred render/install/upgrade. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## `upgrade --install` — Helm

Helm deployment pattern, ktorý vytvorí release, ak neexistuje, alebo aktualizuje existujúcu release; nerieši automaticky concurrency, migrations, drift ani secret management. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).