# Named templates

Named template je reusable Helm template fragment. Jeho hodnota nie je v skrátení source-u, ale v centralizácii identity, labels, selectors, image references, ServiceAccount ownershipu a opakovaných YAML contracts.

Helper však nie je typovaná funkcia. Prijíma jeden scope object, vracia text a jeho meno žije v globálnom template namespace-e parent chartu aj dependencies. Preto musí mať explicitný input, output, stability a compatibility contract.

## 1. Dominantný lifecycle

```text
reuse a compatibility intent
→ global helper name resolution
→ caller scope a argument contract
→ helper call graph evaluation
→ text/output-shape generation
→ caller pipeline a indentation
→ rendered resource identity
→ Kubernetes ownership/immutability effect
→ consumer tests a versioned evolution
```

Helper je bezpečný iba vtedy, keď sa dá preukázať, ktorá definition bola použitá, aký scope dostala a aký exact output vložila do konkrétneho resource fieldu.

## 2. Atlas helper subject

Pre Atlas Payments release používame:

```text
chart artifact: CH57
dependency lock: D57
rendered manifest: M57
release: payments-prod revision 18
```

Kritický helper subject:

```text
global helper name
+ definition origin chart/version/digest
+ call site template
+ caller scope identity
+ argument dictionary
+ output shape a digest
+ target Kubernetes field
```

Príklad:

```text
helper: atlas-payments.selectorLabels
origin: parent chart CH57\caller: templates/deployment.yaml
scope: root release context payments-prod
output: stable YAML map SL57
field: Deployment.spec.selector.matchLabels
```

Rovnaké textové meno bez originu a output identity nestačí.

## 3. `define` a partial files

Definition:

```gotemplate
{{/* Stable labels used by workload selectors. */}}
{{- define "atlas-payments.selectorLabels" -}}
app.kubernetes.io/name: {{ include "atlas-payments.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}
```

`define` samo nevytvára manifest output. Fragment vznikne až pri zavolaní.

Konvenčné miesto:

```text
templates/_helpers.tpl
```

Underscore-prefixed template file sa nerenderuje ako samostatný Kubernetes manifest. Názov súboru však nevytvára namespace. Všetky definitions z parent chartu a subcharts sa kompilujú do jedného globálneho template namespace-u.

## 4. Global name resolution

Rizikový helper:

```gotemplate
{{ define "labels" }}
```

Bezpečnejší helper:

```gotemplate
{{ define "atlas-payments.labels" }}
```

Ak parent a dependency definujú rovnaké meno, jedna definition môže prepísať druhú podľa load behavioru. Source call site pritom zostáva nezmenený.

```text
parent helper H1
+ dependency helper H2 s rovnakým menom
→ globálny namespace obsahuje iba effective definition
→ caller vyrenderuje H2
→ manifest sa zmení bez zmeny call site-u
```

Chart-specific prefix je minimálny contract. Pri nekompatibilnej evolúcii reusable platform helpera môže byť potrebné paralelné versioned meno:

```gotemplate
{{ define "atlas-platform.v2.podSecurityContext" }}
```

Version suffix nepoužívaj pri každej chart release. Použi ho iba vtedy, keď musia súbežne existovať nekompatibilné helper contracts.

## 5. `template` vs. `include`

`template` je action:

```gotemplate
metadata:
  labels:
    {{- template "atlas-payments.labels" . }}
```

Output vloží inline a nie je prakticky transformovateľný ďalšou pipeline.

`include` je Helm function:

```gotemplate
metadata:
  labels:
{{ include "atlas-payments.labels" . | nindent 4 }}
```

`include` vráti text, ktorý možno poslať do `nindent`, `quote`, `sha256sum` alebo `fromYaml`.

Pre YAML fragmenty je `include` zvyčajne vhodnejší, pretože caller explicitne vlastní indentation a ďalšiu transformáciu.

## 6. Scope je argument

Helper nedostane automaticky root context:

```gotemplate
{{ include "atlas-payments.labels" . }}
```

tu `.` reprezentuje callerom odovzdaný root.

Ak caller urobí:

```gotemplate
{{ include "atlas-payments.port" .Values.service }}
```

potom `.` aj `$` vo vnútri helpera reprezentujú service subtree, nie pôvodný chart root.

Preto je nesprávne považovať `$` za univerzálny parent root.

## 7. Explicitný pseudo-signature cez `dict`

Volanie:

```gotemplate
{{ include "atlas-payments.containerPort" (dict
    "root" .
    "name" "http"
    "port" .Values.service.port
) }}
```

Helper:

```gotemplate
{{- define "atlas-payments.containerPort" -}}
- name: {{ required "containerPort.name is required" .name | quote }}
  containerPort: {{ required "containerPort.port is required" .port }}
  protocol: TCP
{{- end -}}
```

Root je dostupný cez:

```gotemplate
{{ .root.Release.Name }}
```

Contract dokumentuj:

```text
input keys: root, name, port
required types: root context, string, integer
output: unindented single-item YAML list
side effects: none
determinism: required
```

Dictionary nie je skutočný typed signature, ale robí input surface explicitný a testovateľný.

## 8. Output shape contract

Named template vždy vracia text. Text môže reprezentovať:

- scalar;
- YAML map;
- YAML list;
- resource fragment;
- serialized JSON/YAML object;
- empty output.

Dokumentovaný helper:

```gotemplate
{{/*
atlas-payments.selectorLabels
Input: root chart context.
Output: unindented YAML map without a leading newline.
Stability: values must remain stable for existing workload selectors.
*/}}
```

Caller musí vedieť:

```text
output shape
+ leading/trailing newline contract
+ required indentation
+ whether quoting is already applied
+ whether mutable metadata is included
```

Bez toho sa helper stáva textovou makro vrstvou bez API contractu.

## 9. Naming helper a resource identity

```gotemplate
{{- define "atlas-payments.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "atlas-payments.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name (include "atlas-payments.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
```

Naming contract ovplyvňuje:

- resource create vs. update identity;
- immutable names a references;
- selector/service coupling;
- PVC a external resource names;
- release uniqueness;
- truncation collision;
- rollback compatibility.

Zmena fullname helpera môže namiesto update-u vytvoriť nový resource a ponechať starý. To je lifecycle migration, nie kozmetický refactor.

## 10. Stable selector vs. mutable common labels

Stable selector helper:

```gotemplate
{{- define "atlas-payments.selectorLabels" -}}
app.kubernetes.io/name: {{ include "atlas-payments.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}
```

Common labels:

```gotemplate
{{- define "atlas-payments.labels" -}}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" }}
{{ include "atlas-payments.selectorLabels" . }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}
```

Použitie:

```gotemplate
spec:
  selector:
    matchLabels:
{{ include "atlas-payments.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
{{ include "atlas-payments.labels" . | nindent 8 }}
```

Chart version, app version ani image digest nepatria do immutable Deployment selectoru. Mutable metadata môže byť na Pod labels, ak Service selector zostane stabilný a cardinality/lifecycle sú prijateľné.

## 11. ServiceAccount ownership helper

```gotemplate
{{- define "atlas-payments.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
{{ default (include "atlas-payments.fullname" .) .Values.serviceAccount.name }}
{{- else -}}
{{ required "serviceAccount.name is required when create=false" .Values.serviceAccount.name }}
{{- end -}}
{{- end -}}
```

Helper vyjadruje ownership boundary:

```text
chart vytvára a spravuje ServiceAccount
alebo
release používa external ServiceAccount
```

Silent fallback na `default` ServiceAccount je security regression, nie pohodlný default.

## 12. Image reference helper

```gotemplate
{{- define "atlas-payments.image" -}}
{{- $repository := required "image.repository is required" .Values.image.repository -}}
{{- $digest := required "image.digest is required" .Values.image.digest -}}
{{ printf "%s@%s" $repository $digest }}
{{- end -}}
```

Production helper contract má odlíšiť:

- repository;
- registry override;
- tag;
- digest;
- platform/index identity;
- quoting;
- mutable-development a immutable-production policy.

Neskladaj OCI reference len intuitívnou string concatenation bez tests pre empty registry, port, nested repository, tag a digest combinations.

## 13. Structured output cez serialize/parse boundary

Helper môže vrátiť YAML:

```gotemplate
{{- define "atlas-payments.defaultResources" -}}
requests:
  cpu: 100m
  memory: 128Mi
{{- end -}}
```

Caller:

```gotemplate
{{- $defaults := include "atlas-payments.defaultResources" . | fromYaml -}}
```

Tento pattern vytvára:

```text
helper logic
→ YAML text
→ YAML parse
→ map
```

Riziká:

- implicitné YAML typing;
- menej čitateľné parse errors;
- hidden output schema;
- whitespace a serialization coupling;
- zbytočná abstraction oproti native values objectu.

Používaj ho iba vtedy, keď reusable structured contract prináša jasnú hodnotu a má semantic tests.

## 14. Indentation a whitespace contract

Helper pre YAML mapu má renderovať bez caller-specific indentation:

```gotemplate
{{- define "atlas-payments.selectorLabels" -}}
app.kubernetes.io/name: {{ include "atlas-payments.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}
```

Caller rozhodne:

```gotemplate
matchLabels:
{{ include "atlas-payments.selectorLabels" . | nindent 6 }}
```

Scalar helper nemá pridávať nečakaný newline. Multi-line helper musí mať explicitný leading/trailing newline contract.

Hard-coded indentation v helperi viaže output na jedno miesto v YAML tree a znemožňuje bezpečný reuse.

## 15. Helper call graph

Udržuj jednoduchý acyklický graph:

```text
primitive identity helpers
→ selector/common labels
→ image/ServiceAccount/resource fragments
→ manifests
```

Cyklus:

```text
A → B → A
```

vedie k render failure alebo recursion problému.

Veľmi hlboký helper graph je síce acyklický, ale môže zakrývať source hodnoty a output ownership. Pre každý critical field má byť dohľadateľná krátka cesta od values k helperu a manifest call site-u.

## 16. `block` a implicit override

```gotemplate
{{ block "atlas-payments.podAnnotations" . }}
atlas.example/managed: "true"
{{ end }}
```

`block` definuje default content a zároveň ho vyrenderuje. Iná definition rovnakého mena ho môže nahradiť.

V multi-chart renderi je override citlivý na global names a load order. Explicitné values alebo versionovaný library-chart helper contract sú zvyčajne čitateľnejšie než implicitný block override.

## 17. Library chart

Library chart poskytuje reusable helpers a primitives bez bežného application resource lifecycle-u.

Vhodné use cases:

- organization labels;
- security context primitives;
- workload/container fragments;
- policy-conformant metadata;
- common image/reference logic.

Library chart je API provider. Jeho zmena môže zmeniť output desiatok consumer charts bez zmeny ich templates.

Preto potrebuje:

```text
versioned helper names/contracts
consumer compatibility matrix
rendered output fixtures
dependency lock
changelog a migration guide
canary consumers
```

Library chart nesmie byť neviditeľný source code injection bez ownershipu.

## 18. Parent a subchart scope

Parent a subcharts zdieľajú global helper namespace, ale nie automaticky values scope.

Subchart helper môže dostať parent root, ak ho parent explicitne zavolá s týmto scope-om. Inak používa scope podľa svojho call site-u.

Nespoliehaj sa na:

- náhodný load order;
- generické helper names;
- implicitný prístup k parent values;
- override dependency helpera bez explicitného contractu.

## 19. Determinism a side effects

Core identity helpers majú byť pure a deterministic.

Rizikové inputs:

- `now`;
- random functions;
- `lookup`;
- mutable external values;
- map mutation;
- dependency helper collision.

Naming alebo selector helper s nondeterminismom môže pri každom renderi meniť resource identity a vytvárať perpetual diff alebo replacement.

## 20. Worked failure: dependency helper prepíše selector contract

Parent chart 2.7.0 historicky používal generické meno:

```gotemplate
{{- define "common.selectorLabels" -}}
app.kubernetes.io/name: {{ include "atlas-payments.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}
```

Library dependency po update obsahovala rovnaké global meno:

```gotemplate
{{- define "common.selectorLabels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version }}
{{- end -}}
```

Caller sa nezmenil:

```gotemplate
matchLabels:
{{ include "common.selectorLabels" . | nindent 6 }}
```

Po dependency resolution sa effective definition zmenila. Selector teraz obsahoval mutable chart version.

### Exact subject

```text
helper name: common.selectorLabels
definition origins: parent CH57 a library dependency LD58
lock/dependency graph: D57
call sites: Deployment selector, Pod labels, Service selector
caller scope: parent root payments-prod
old output digest: SL56
new output digest: SL57
live Deployment UID/generation
```

### Competing hypotheses

1. Values zmenili `nameOverride` alebo release identity.
2. Parent helper source sa zmenil.
3. Dependency definition collision zmenila effective helper.
4. Helper dostal nesprávny local scope namiesto rootu.
5. `nindent` alebo whitespace vložili iný YAML shape.
6. Admission mutation zmenila labels/selectors.
7. Helm update strategy alebo server-side apply vyhodnotili immutable field inak.
8. Service a Deployment používajú odlišné helper outputs.

### Discriminating observation points

| Hypotéza | Observation |
|---|---|
| values/name change | effective values a old/new helper input |
| parent source change | packaged parent chart diff |
| collision | inventory všetkých `define "common.selectorLabels"` v packaged graph-e |
| wrong scope | debug helper s redacted `.Chart/.Release` identity a call site |
| whitespace | isolated `--show-only` final YAML parse |
| admission | server dry-run response a live managedFields |
| immutable update | API error na exact Deployment UID/selector |
| divergent callers | semantic diff Deployment selector, Pod labels a Service selector |

### Finding

Dependency library chart zaviedol rovnaké global helper meno. Effective definition pridala `helm.sh/chart` do selector outputu. Upgrade chart version 2.6.4 → 2.7.0 preto menil immutable Deployment selector.

```text
unreviewed helper collision
→ output SL56 sa zmení na SL57
→ rendered Deployment selector sa zmení
→ API odmietne immutable field update
→ Helm revision skončí failed
→ časť ostatných resources alebo hooks už mohla byť zmenená
```

### Containment

- zastav retry rovnakej release revision;
- zachovaj packaged chart/dependencies, M57, API error, release history a live object;
- ponechaj starý Deployment/Pods v prevádzke;
- nevymaž Deployment, aby upgrade „prešiel“;
- nepouži `--force` bez resource identity a outage analýzy;
- zastav automatické dependency re-resolution.

### Authoritative recovery

1. premenuj parent helper na `atlas-payments.selectorLabels`;
2. library helper pomenuj versionovaným provider prefixom;
3. oddeľ stable selector labels od mutable common labels;
4. pinni dependency cez reviewed `Chart.lock`;
5. pridaj test na duplicate global definitions;
6. snapshot-ni old/new selector outputs;
7. vytvor nový chart artifact a release revision;
8. server-side validuj upgrade proti existujúcemu Deployment UID.

### Verify original a forbidden outcomes

- Deployment selector zostáva byte/semantic stable medzi podporovanými revisions;
- Pod template a Service selector obsahujú matching stable labels;
- mutable chart/app metadata nie je v selector contracte;
- dependency upgrade bez parent source zmeny nevie potichu prepísať helper;
- rollout vytvorí nové Pods bez replacementu identity celého Deploymentu;
- old helper name sa už v packaged graph-e nenachádza;
- druhý render a upgrade sú deterministic a bounded.

### Earlier controls

- chart-prefixed global names;
- duplicate `define` scanner;
- helper contract fixtures;
- selector stability test naprieč revisions;
- server-side upgrade test proti previous release;
- dependency lock review;
- library chart consumer canary.

## 21. Ďalšie failure boundaries

### Caller odovzdá `.Values` namiesto rootu

Helper očakáva `.Release` a `.Chart`, ale dostane iba mapu. Render zlyhá alebo použije empty fallback a vytvorí chybnú identity.

### Naming helper refactor

Zmena fullname outputu vytvorí nový Service/PVC/Secret namiesto update-u existujúceho resource-u.

### Mutable metadata v selector helperi

Chart alebo app version mení immutable selector pri každom upgrade.

### Hard-coded indentation

Helper funguje v jednom call site-e, ale v inom vytvorí sibling field alebo neplatný YAML.

### Library helper breaking change

Consumer templates sa nezmenili, no dependency update zmení desiatky rendered resources.

### Structured output parse drift

Helper YAML output sa zmení typovo a `fromYaml` caller dostane inú map/list shape.

## 22. Helper test matrix

Minimálne testuj:

```text
default values
nameOverride a fullnameOverride
dlhé names a truncation collision
missing, empty, false a zero
root vs. local scope
all helper call sites
exact whitespace/indentation
stable selectors medzi revisions
ServiceAccount create/external modes
tag/digest image combinations
parent + dependency global-name inventory
multiple dependency versions
multiple Kubernetes/API capabilities
deterministic repeated render
```

Testing layers:

```text
isolated helper fixture
→ rendered template snapshot
→ semantic manifest assertions
→ server-side upgrade validation
→ live rollout/business verification
```

## 23. Debugging workflow

```text
fix exact helper name
→ enumerate all definitions a origins
→ identify effective dependency graph
→ fix caller a scope
→ inspect helper output in isolation
→ inspect final target field
→ compare old/new output digest
→ server validate against live object
→ verify runtime/service outcome
```

Príklad:

```bash
helm template payments-prod ./chart \
  -f values-prod.yaml \
  --show-only templates/deployment.yaml \
  --debug
```

Nevypisuj celý root scope, pretože môže obsahovať sensitive values.

## 24. Anti-patterny

- generické global helper names;
- helper contract definovaný iba implicitne call sites;
- predpoklad, že `$` je pôvodný root;
- helper s polymorfným nezdokumentovaným scope-om;
- mutable version metadata v selector helperi;
- fullname refactor bez resource migration analýzy;
- hard-coded caller indentation;
- jeden helper generujúci celý komplexný workload;
- structured output bez schema/tests;
- `block` override založený na load orderi;
- library chart update bez consumer compatibility testu;
- nondeterministic identity helper;
- duplicate helper name riešený `--force` alebo delete-nutím live resource-u.

## 25. Kontrolné otázky

1. Ktoré identity tvoria exact helper subject?
2. Prečo je template namespace globálny naprieč dependencies?
3. Ako sa líši `template` od `include`?
4. Čo znamená `.` a `$` po odovzdaní local scope-u?
5. Ako dokumentuješ pseudo-signature cez `dict`?
6. Prečo musí caller vlastniť indentation?
7. Ktoré labels môžu byť mutable a ktoré nie?
8. Ako library chart mení supply-chain a compatibility surface?
9. Ktoré observations odhalia helper collision?
10. Ako preukážeš stable resource identity naprieč chart revisions?

## Glossary impact

Relevantné pojmy: Helm helper subject, global helper resolution, helper definition origin, helper pseudo-signature, helper output-shape contract, helper call graph, stable selector contract, helper collision, library-chart provider contract, helper consumer compatibility, helper-output digest a helper-driven resource identity migration.

## Oficiálna dokumentácia

- [Named Templates](https://helm.sh/docs/chart_template_guide/named_templates/)
- [Templates Best Practices](https://helm.sh/docs/chart_best_practices/templates/)
- [Library Charts](https://helm.sh/docs/topics/library_charts/)
- [Subcharts and Global Values](https://helm.sh/docs/chart_template_guide/subcharts_and_globals/)
- [Chart Template Guide](https://helm.sh/docs/chart_template_guide/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Template functions a pipelines](template-functions-pipelines.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Chart dependencies →](chart-dependencies.md)
<!-- KNOWLEDGE-NAVIGATION:END -->