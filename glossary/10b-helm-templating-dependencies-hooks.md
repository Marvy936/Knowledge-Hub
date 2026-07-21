# Helm templating, dependencies and hooks glossary entries

## `before-hook-creation` — Helm

Default hook cleanup behavior, pri ktorom Helm pred spustením nového hook resource-u odstráni predchádzajúci resource s rovnakou identity. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Chart-prefixed helper — Helm

Named template pomenovaný s chart-specific prefixom, napríklad `payments.labels`, aby sa znížilo riziko globálnej name collision s parent alebo dependency chartom. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Dependency alias — Helm

Local identity dependency chartu umožňujúca použiť rovnaký chart viackrát s oddelenými values a resource-name contracts. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Dependency condition — Helm

Boolean values path v dependency declaration, ktorý povoľuje alebo zakazuje načítanie konkrétneho subchartu. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Dependency constraint — Helm

Exact SemVer alebo version range v `Chart.yaml`, podľa ktorého `helm dependency update` vyberá kompatibilnú dependency version. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Dependency tag — Helm

Label priradený jednej alebo viacerým dependencies, ktorý umožňuje ich skupinové enable/disable cez top-level `tags` values. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Empty value — Helm

Hodnota považovaná template functions ako `default` alebo `coalesce` za neprítomnú, napríklad `nil`, prázdny string, nula, `false` alebo prázdna collection podľa typu. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Global template namespace — Helm

Spoločný namespace named templates kompilovaných z parent chartu a všetkých subcharts; rovnaké helper name môže byť prepísané inou definition. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Global value — Helm

Value uložená pod top-level `global`, ktorú môžu čítať parent chart aj subcharts; je vhodná iba pre explicitný cross-chart contract. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Helm chart dependency

Chart deklarovaný alebo vendored ako súčasť parent chartu, ktorého templates a resources sa agregujú do rovnakého Helm release-u. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Helm hook

Kubernetes resource template označený annotation `helm.sh/hook`, ktorý Helm vykoná v konkrétnom bode install, upgrade, rollback, delete alebo test lifecycle. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Helm merge

Template operation spájajúca dictionaries podľa konkrétnej direction a overwrite semantics; pri nested maps môže vyžadovať `deepCopy`, aby sa zabránilo neúmyselnej mutation vstupu. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Helm partial

Reusable template fragment, typicky uložený v underscore-prefixed súbore ako `_helpers.tpl`, ktorý sám nevytvára Kubernetes manifest. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Helm pipeline

Template expression, v ktorom sa výsledok ľavej časti posiela ako posledný argument nasledujúcej funkcie. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Helm subchart

Stand-alone chart vložený ako dependency parent chartu, s vlastným values scope-om a templates, ale spoločným výsledným release lifecycle. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Helm template function

Funkcia dostupná v Helm template engine z Go templates, Sprig alebo Helm-specific extension, ktorá transformuje input na textový alebo štruktúrovaný render output. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Helper contract — Helm

Dokumentovaný input scope, očakávané keys, output shape, whitespace a stability semantics named template helpera. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Helper scope — Helm

Object odovzdaný named template-u cez `template` alebo `include`, ktorý určuje význam `.` aj root symbolu `$` vo vnútri helpera. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Hook delete policy — Helm

Annotation `helm.sh/hook-delete-policy` určujúca cleanup hook resource-u pred ďalším spustením, po úspechu alebo po failure. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Hook idempotency — Helm

Vlastnosť hook operácie, pri ktorej opakované alebo čiastočne dokončené vykonanie bezpečne konverguje bez duplicitných side effects. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Hook lifecycle point — Helm

Konkrétny release moment, napríklad `pre-install`, `post-upgrade` alebo `pre-delete`, v ktorom Helm spustí označený hook resource. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Hook readiness — Helm

Podmienka, pri ktorej Helm považuje hook za dokončený; pri Job alebo Pod hooku čaká na úspešné completion, pri mnohých iných resource kinds stačí úspešné API načítanie. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Hook resource retention — Helm

Lifecycle rozhodnutie, ako dlho ponechať dokončený alebo failed hook resource pre audit a diagnostiku a kedy ho odstráni delete policy alebo Kubernetes TTL. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Hook side effect — Helm

Zmena external alebo durable state-u vykonaná hookom, napríklad database migration, backup alebo API registrácia, ktorú Helm manifest rollback nemusí automaticky zvrátiť. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Hook weight — Helm

Stringovo zapísané číslo v annotation `helm.sh/hook-weight`, podľa ktorého Helm vykonáva hooks od nižšej hodnoty k vyššej. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## `hook-failed` — Helm

Hook delete-policy hodnota požadujúca odstránenie hook resource-u po neúspešnom vykonaní; môže znížiť dostupnosť incident evidence. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## `hook-succeeded` — Helm

Hook delete-policy hodnota požadujúca odstránenie hook resource-u po úspešnom vykonaní. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## `import-values` — Helm

Dependency declaration mechanism prenášajúci vybrané exported alebo mapped child values do parent values scope-u. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Library chart — Helm

Chart typu `library`, ktorý poskytuje reusable template primitives a helpers pre iné charts bez bežného application resource lifecycle. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Named template — Helm

Globálne pomenovaný reusable template fragment deklarovaný cez `define` a použitý cez `template`, `include` alebo `block`. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Nondeterministic template — Helm

Template používajúci live lookup, čas, random generation alebo iný mutable input, takže rovnaký chart a values nemusia vytvoriť rovnaký manifest. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Pipeline last argument — Helm

Pravidlo, podľa ktorého pipeline odovzdá svoj ľavý výsledok ako posledný positional argument nasledujúcej template funkcie. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Selector-label helper — Helm

Named template generujúci stabilné labels použité workload selectorom aj Pod template-om; nesmie obsahovať mutable chart alebo application version metadata. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Single-release dependency graph — Helm

Model, v ktorom parent chart a všetky enabled first-level aj transitive subcharts vytvárajú jednu release revision a spoločný upgrade/rollback failure domain. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Structured helper output — Helm

Textový output named template-u, ktorý reprezentuje YAML/JSON object a caller ho môže parsovať cez `fromYaml` alebo `fromJson`; ide o serialize/parse contract, nie natívny typed return. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Test hook — Helm

Hook resource označený hodnotou `test`, ktorý sa vykoná cez `helm test` a má overiť release-specific invariant s explicitným exit statusom. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Transitive chart dependency — Helm

Dependency, ktorú parent chart získava nepriamo cez dependency vlastného subchartu; rozširuje render, hook, RBAC a supply-chain surface celého release-u. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Vendored chart — Helm

Dependency chart uložený priamo v parent `charts/` directory ako archive alebo unpacked directory namiesto stiahnutia počas build-u. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Whitespace control — Helm

Použitie trim markers `{{-` a `-}}` a indentation functions na riadenie whitespace a newline v renderovanom YAML. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## `_helpers.tpl`

Konvenčný underscore-prefixed súbor v `templates/` určený na definitions reusable named templates, ktorý sa sám nerenderuje ako Kubernetes manifest. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## `helm dependency build`

Command rekonštruujúci `charts/` podľa existujúceho `Chart.lock` bez nového version negotiation, pokiaľ lock existuje. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## `helm dependency update`

Command re-resolvujúci dependency constraints z `Chart.yaml`, aktualizujúci `charts/` a generujúci alebo meniaci `Chart.lock`. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## `Chart.lock`

Helm-generated lock file zachytávajúci resolved dependency graph a digest metadata pre reprodukovateľnú reconstruction dependencies. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## `block` — Helm

Go template action, ktorá definuje default named template content a zároveň ho vykreslí; globálna override semantics môže byť menej explicitná než values alebo library-chart contract. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## `coalesce` — Helm

Template function vracajúca prvú non-empty hodnotu zo zoznamu kandidátov podľa Helm/Sprig empty semantics. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## `default` — Helm

Template function vracajúca fallback, keď input je považovaný za empty; pri explicitnom `false` alebo `0` môže zmeniť zamýšľaný význam. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## `define` — Helm

Go template action deklarujúca named template pod globálnym menom bez okamžitého render outputu. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## `fail` — Helm

Template function okamžite ukončujúca render s chart-specific error message pri porušení explicitného invariantu. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## `hasKey` — Helm

Map function rozlišujúca neprítomný key od prítomnej hodnoty ako `false`, `0` alebo empty string. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## `include` — Helm

Helm function renderujúca named template do stringu, ktorý možno ďalej spracovať v pipeline napríklad cez `nindent` alebo `sha256sum`. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## `lookup` — Helm

Template function čítajúca live Kubernetes API počas server-connected renderu; zavádza RBAC dependency a cluster-state-dependent output. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## `nindent` — Helm

Template function pridávajúca newline a následne odsadzujúca každý riadok o zadaný počet spaces, vhodná pre vkladanie YAML blocks. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## `required` — Helm

Template function zlyhávajúca render, keď požadovaná hodnota je empty, a vracajúca explicitnú error message. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## `template` — Helm

Go template action vkladajúca named template inline; na rozdiel od `include` neposkytuje output ako pipeline string. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## `toYaml` — Helm

Template function serializujúca hodnotu do YAML textu, ktorý musí byť vložený s korektným indentation contractom. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## `tpl` — Helm

Function vyhodnocujúca string ako Helm template v odovzdanom scope-e; rozširuje input trust boundary a môže znížiť deterministickosť renderu. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).
