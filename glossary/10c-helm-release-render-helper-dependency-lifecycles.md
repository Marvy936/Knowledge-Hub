# Helm release, render, helper and dependency lifecycle glossary entries

## Capability-conditioned render — Helm

Render generation, ktorej output závisí od explicitného Kubernetes/API capability inventory alebo live cluster discovery. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Dependency declaration generation — Helm

Versionovaný `Chart.yaml` dependency intent zahŕňajúci names, aliases, constraints, sources, conditions, tags a import contracts pred resolution. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Dependency decommission subject — Helm

Inventár resources, dát, CRDs, hooks, external assets a parent consumers, ktoré treba bezpečne vyradiť pri disable alebo odstránení dependency. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Dependency enablement generation — Helm

Konkrétny verdict conditions, tags, aliases a effective values určujúci, ktoré dependencies vstupujú do jedného release renderu. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Dependency graph subject — Helm

Exact parent chart, declaration, lock, first-level a transitive artifact digests, aliases, conditions a trust evidence pre jednu release generation. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Dependency ownership test — Helm

Rozhodnutie, či component zdieľa ownera, cadence, rollback, SLO, privilege a data lifecycle parent release-u, alebo patrí do samostatného release-u. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Deterministic dependency rebuild verdict

Dôkaz, že rovnaký source a reviewed lock v clean prostredí vytvoria rovnaký packaged dependency graph bez nového version negotiation alebo internet timing driftu. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Deterministic render verdict — Helm

Dôkaz, že fixný chart, dependency graph, values, release context, capabilities a engine vytvoria rovnaký semantic manifest output pri opakovanom renderi. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Dynamic template execution boundary — Helm

Trust boundary vytvorená funkciou ako `tpl`, ktorá mení values string z deklaratívnych dát na vykonateľný template input v odovzdanom scope-e. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Global helper resolution — Helm

Proces výberu effective named-template definition z globálneho namespace-u parent chartu a dependencies. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Helm empty semantics

Pravidlá, podľa ktorých template functions považujú `nil`, prázdny string, nulu, `false` alebo prázdnu collection za empty, čo môže aktivovať fallback. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Helm helper subject

Exact helper name, definition origin, caller, scope, argument dictionary, output shape/digest a target Kubernetes field. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Helper call graph — Helm

Directed graph volaní od primitive identity helpers cez reusable fragments po final manifest call sites. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Helper collision — Helm

Stav, keď parent alebo dependency chart definujú rovnaký global template name a effective definition zmení render bez zmeny call site-u. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Helper consumer compatibility — Helm

Dôkaz, že zmena helper provider chartu zachováva input, output-shape, identity, selector a semantic contracts všetkých consumer charts. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Helper definition origin — Helm

Chart name, version, digest a source file, z ktorých pochádza effective named-template definition. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Helper-driven resource identity migration

Lifecycle zmena, pri ktorej nový naming alebo selector helper mení Kubernetes resource identity a vyžaduje explicitný migration/rollback plán. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Helper output-shape contract — Helm

Dokumentovaný scalar/map/list/fragment textový output vrátane newline, indentation, quoting a stability semantics. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Helper pseudo-signature — Helm

Explicitný dictionary-based input contract named template-u s required keys, types, root/local scope a output shape. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Helper-output digest — Helm

Hash semantic alebo textovej helper output generation používaný na detekciu nečakanej zmeny reusable contractu medzi revisions. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Library-chart provider contract

Versionovaný reusable helper API poskytovaný library chartom vrátane names, scopes, output shapes, compatibility a consumer testov. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Library-chart source injection

Schopnosť library dependency meniť parent rendered resources prostredníctvom helpers, hoci sama nevytvára samostatný workload resource set. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Live-lookup render subject — Helm

Cluster endpoint, caller RBAC, queried object UID/resourceVersion a API response, ktoré vstupujú do manifestu pri použití `lookup`. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Locked packaged graph — Helm

Reprodukovateľný packaged parent chart a všetky dependency artifacts vytvorené podľa reviewed `Chart.lock` a overených digestov. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Lock-required release gate — Helm

CI policy odmietajúca release build, ak dependency declaration nemá synchronizovaný reviewed lock alebo artifacts nezodpovedajú lock identity. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Merge mutation boundary — Helm

Hranica, na ktorej `set`, `unset`, `merge` alebo `mergeOverwrite` môžu meniť shared map reference a ovplyvniť neskoršie templates bez `deepCopy`. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Rendered-field identity — Helm

Konkrétny Kubernetes resource path a value generation, ku ktorej sa viaže values-to-template transform a runtime dôsledok. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Resolved dependency artifact — Helm

Exact dependency chart version a digest zvolený resolverom z declaration constraintu a source repository state-u. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Serialization boundary — Helm

Prechod z Go/template objectu na YAML alebo JSON text a následne späť na parsed structure alebo final Kubernetes document. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Single-release failure domain — Helm

Spoločný install, upgrade, rollback, hook a revision blast radius parent chartu a všetkých enabled dependencies. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Source-to-field provenance — Helm

Korelačný chain od values source/pathu a helper/pipeline transformácie po exact rendered, live a process-loaded Kubernetes field. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Stable selector contract — Helm

Helper a values contract, ktorý zachováva immutable workload selector labels a ich zhodu s Pod a Service labels medzi podporovanými revisions. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Template type graph — Helm

Sekvencia Go runtime types a textových transformácií, ktoré konkrétna pipeline vykonáva od values inputu po rendered field. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Transitive render surface — Helm

Templates, helpers, CRDs, hooks, RBAC, images a values contracts získané nepriamo cez dependencies vlastných subcharts. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Typed render pipeline — Helm

Transformačný lifecycle od values presence/type validation cez functions, merge, serialization a indentation po final API field a runtime effect. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Values presence contract — Helm

Explicitné rozlíšenie missing key-u, `nil`, `false`, nuly, prázdneho stringu a prázdnej collection v chart configuration API. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).