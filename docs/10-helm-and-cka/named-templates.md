# Named templates

Named template je reusable Helm template fragment. Centralizuje naming, labels, selectors, image references, ServiceAccount ownership a opakované YAML contracts. Nie je to však typovaná funkcia: prijíma jeden scope object, vracia text a jeho meno žije v globálnom template namespace-e parent chartu aj dependencies.

Preto helper potrebuje explicitný input, output, stability a compatibility contract.

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

Pre Atlas Payments release:

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
+ call-site template
+ caller scope identity
+ argument dictionary
+ output shape a digest
+ target Kubernetes field
```

Príklad:

```text
helper: atlas-payments.selectorLabels
origin: parent chart CH57
caller: templates/deployment.yaml
scope: root release context payments-prod
output: stable YAML map SL57
field: Deployment.spec.selector.matchLabels
```

Rovnaké textové meno bez originu a output identity nestačí.

## 3. `define`, partials a global namespace

```gotemplate
{{/* Stable labels used by workload selectors. */}}
{{- define "atlas-payments.selectorLabels" -}}
app.kubernetes.io/name: {{ include "atlas-payments.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}
```

`define` samo nevytvára manifest output. Fragment vznikne až pri zavolaní. Konvenčné miesto je `templates/_helpers.tpl`; underscore-prefixed file sa nerenderuje ako samostatný resource.

Názov súboru ale nevytvára namespace. Parent a subcharts sa kompilujú do jedného globálneho template namespace-u. Dve definitions s rovnakým menom môžu kolidovať.

```text
parent helper H1
+ dependency helper H2 s rovnakým menom
→ effective global definition je H2
→ caller vyrenderuje iný output
→ manifest sa zmení bez zmeny call site-u
```

Používaj chart-specific prefix:

```gotemplate
{{ define "atlas-payments.labels" }}
```

Pri súbežných nekompatibilných contracts môže byť vhodné versioned meno, napríklad `atlas-platform.v2.podSecurityContext`.

## 4. `template` vs. `include`

`template` vloží output inline:

```gotemplate
metadata:
  labels:
    {{- template "atlas-payments.labels" . }}
```

`include` vráti text použiteľný v pipeline:

```gotemplate
metadata:
  labels:
{{ include "atlas-payments.labels" . | nindent 4 }}
```

Pre YAML fragments je `include` zvyčajne vhodnejší, pretože caller vlastní indentation a ďalšiu transformáciu.

## 5. Scope je argument

```gotemplate
{{ include "atlas-payments.labels" . }}
```

Tu `.` reprezentuje root odovzdaný callerom.

Ak caller použije:

```gotemplate
{{ include "atlas-payments.port" .Values.service }}
```

potom `.` aj `$` vo vnútri helpera reprezentujú service subtree, nie pôvodný chart root. `$` nie je univerzálny parent root.

Helper, ktorý potrebuje viac údajov, má dostať explicitný dictionary contract:

```gotemplate
{{ include "atlas-payments.containerPort" (dict
    "root" .
    "name" "http"
    "port" .Values.service.port
) }}
```

```gotemplate
{{- define "atlas-payments.containerPort" -}}
- name: {{ required "containerPort.name is required" .name | quote }}
  containerPort: {{ required "containerPort.port is required" .port }}
  protocol: TCP
{{- end -}}
```

Pseudo-signature:

```text
input keys: root, name, port
required types: root context, string, integer
output: unindented single-item YAML list
side effects: none
determinism: required
```

## 6. Output-shape contract

Named template vždy vracia text. Text môže reprezentovať scalar, YAML map, YAML list, resource fragment, serialized object alebo empty output.

Dokumentuj:

```gotemplate
{{/*
atlas-payments.selectorLabels
Input: root chart context.
Output: unindented YAML map without a leading newline.
Stability: values remain stable for existing workload selectors.
*/}}
```

Caller musí poznať:

- output shape;
- leading/trailing newline contract;
- required indentation;
- quoting contract;
- mutable vs. stable metadata.

Bez toho je helper iba textová makro vrstva bez API contractu.

## 7. Naming helper a resource identity

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

Naming contract ovplyvňuje create-vs-update identity, immutable references, Services, PVCs, external resources, truncation collisions a rollback compatibility.

Zmena fullname helpera môže vytvoriť nový resource namiesto aktualizácie existujúceho. To je lifecycle migration, nie kozmetický refactor.

## 8. Stable selector vs. mutable common labels

```gotemplate
{{- define "atlas-payments.selectorLabels" -}}
app.kubernetes.io/name: {{ include "atlas-payments.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}
```

```gotemplate
{{- define "atlas-payments.labels" -}}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" }}
{{ include "atlas-payments.selectorLabels" . }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}
```

Chart version, app version ani image digest nepatria do immutable Deployment selectoru. Selector helper musí zostať stabilný medzi podporovanými revisions a zhodovať sa medzi workload selectorom, Pod labels a Service selection contractom.

## 9. Ownership helpers

ServiceAccount helper vyjadruje, kto resource vytvára:

```gotemplate
{{- define "atlas-payments.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
{{ default (include "atlas-payments.fullname" .) .Values.serviceAccount.name }}
{{- else -}}
{{ required "serviceAccount.name is required when create=false" .Values.serviceAccount.name }}
{{- end -}}
{{- end -}}
```

Silent fallback na `default` ServiceAccount je security regression.

Production image helper má používať explicitný immutable contract:

```gotemplate
{{- define "atlas-payments.image" -}}
{{- $repository := required "image.repository is required" .Values.image.repository -}}
{{- $digest := required "image.digest is required" .Values.image.digest -}}
{{ printf "%s@%s" $repository $digest }}
{{- end -}}
```

## 10. Serialization, indentation a call graph

Helper môže vrátiť YAML a caller ho parsovať cez `fromYaml`, ale tým vzniká serialize/parse boundary s implicitným typingom a hidden output schema. Native values object je často jednoduchší.

Helper pre YAML mapu má renderovať bez caller-specific indentation. Caller použije `nindent` podľa cieľovej pozície.

Udržuj jednoduchý acyklický graph:

```text
primitive identity helpers
→ selector/common labels
→ image/ServiceAccount/resource fragments
→ manifests
```

Cyklus alebo veľmi hlboký graph komplikuje render failure, source-to-field provenance a compatibility review.

## 11. Library chart ako API provider

Library chart poskytuje reusable helpers bez bežného workload lifecycle-u. Môže však meniť parent output vrátane names, selectors, images, securityContext a RBAC.

Potrebuje:

```text
versioned helper contracts
consumer compatibility matrix
rendered output fixtures
dependency lock
changelog a migration guide
canary consumers
```

Library chart nie je neviditeľný bezpečný doplnok. Je source-code dependency celej release render generation.

## 12. Worked failure: dependency helper prepíše selector contract

Parent chart definoval generické meno:

```gotemplate
{{- define "common.selectorLabels" -}}
app.kubernetes.io/name: {{ include "atlas-payments.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}
```

Aktualizovaná library dependency definovala rovnaké meno a pridala mutable chart version:

```gotemplate
{{- define "common.selectorLabels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version }}
{{- end -}}
```

Caller sa nezmenil. Effective definition sa však po dependency resolution zmenila.

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

1. Values zmenili name alebo release identity.
2. Parent helper source sa zmenil.
3. Dependency collision zmenila effective definition.
4. Helper dostal nesprávny scope.
5. Whitespace/indentation zmenili YAML shape.
6. Admission mutovalo labels.
7. Service a Deployment používajú odlišné helper outputs.

### Discriminating observations

| Hypotéza | Observation |
|---|---|
| values/name change | effective values a old/new helper input |
| parent source | packaged parent chart diff |
| collision | inventory všetkých `define "common.selectorLabels"` v packaged graph-e |
| wrong scope | redacted `.Chart/.Release` identity a call site |
| whitespace | isolated final YAML parse |
| admission | server dry-run response a managedFields |
| divergent callers | semantic diff selectorov a Pod labels |

### Finding

Dependency library chart prepísal global helper. New output pridal `helm.sh/chart` do immutable selectoru.

```text
unreviewed helper collision
→ selector output SL56 sa zmení na SL57
→ rendered Deployment selector sa zmení
→ API odmietne immutable update
→ Helm release skončí failed
→ časť ďalších operations už mohla prebehnúť
```

### Containment

- zastav retry release-u;
- zachovaj packaged graph, M57, API error, history a live object;
- ponechaj starý Deployment/Pods v prevádzke;
- nemaž Deployment a nepouži `--force` bez identity/outage analýzy;
- zastav dependency re-resolution.

### Authoritative recovery

1. premenuj helper na `atlas-payments.selectorLabels`;
2. library helpers pomenuj provider/version prefixom;
3. oddeľ stable selector a mutable common labels;
4. pinni dependency cez reviewed lock;
5. pridaj duplicate-definition scanner;
6. snapshot-ni old/new selector outputs;
7. server-side validuj upgrade proti existujúcemu Deployment UID.

### Verify original a forbidden outcomes

- selector zostáva semantic stable medzi revisions;
- Pod a Service labels sa zhodujú;
- mutable metadata nie je v selector contracte;
- dependency nevie potichu prepísať helper;
- rollout aktualizuje workload bez replacementu identity;
- old generic helper už v graph-e neexistuje;
- druhý render a upgrade sú deterministic a bounded.

### Earlier controls

- chart-prefixed names;
- duplicate `define` scanner;
- helper fixtures a output digests;
- selector stability test;
- server-side upgrade test;
- dependency lock review;
- library consumer canary.

## 13. Ďalšie failure boundaries

- Caller odovzdá `.Values` namiesto rootu a helper stratí `.Release`/`.Chart`.
- Fullname refactor vytvorí nové Service/PVC/Secret identities.
- Hard-coded indentation funguje iba v jednom call site-e.
- Structured helper output zmení map/list type.
- `block` override závisí od globálneho mena a load orderu.
- Nondeterministic naming helper vytvára perpetual diff alebo replacement.

## 14. Test matrix

```text
default values a overrides
dlhé names a truncation collisions
missing, empty, false a zero
root vs. local scope
all helper call sites
exact whitespace/indentation
stable selectors medzi revisions
ServiceAccount create/external modes
tag/digest image combinations
parent + dependency definition inventory
multiple dependency versions
deterministic repeated render
server-side upgrade proti previous release
```

## 15. Debugging workflow

```text
fix exact helper name
→ enumerate all definitions a origins
→ identify dependency graph
→ fix caller a scope
→ inspect helper output in isolation
→ inspect final target field
→ compare old/new output digest
→ server validate against live object
→ verify runtime/service outcome
```

```bash
helm template payments-prod ./chart \
  -f values-prod.yaml \
  --show-only templates/deployment.yaml \
  --debug
```

Nevypisuj celý root scope; môže obsahovať sensitive values.

## 16. Anti-patterny

- generické global helper names;
- implicitný helper contract;
- predpoklad, že `$` je pôvodný root;
- polymorfný nezdokumentovaný scope;
- mutable version metadata v selector helperi;
- fullname refactor bez migration analýzy;
- hard-coded caller indentation;
- helper generujúci celý komplexný workload;
- `block` override založený na load orderi;
- library chart update bez consumer testu;
- nondeterministic identity helper;
- collision riešená force/delete zásahom do live resource-u.

## 17. Kontrolné otázky

1. Ktoré identity tvoria exact helper subject?
2. Prečo je template namespace globálny?
3. Ako sa líši `template` od `include`?
4. Čo znamená `.` a `$` po odovzdaní local scope-u?
5. Ako dokumentuješ pseudo-signature a output shape?
6. Prečo musí caller vlastniť indentation?
7. Ktoré labels musia byť stabilné?
8. Ako library chart mení supply-chain surface?
9. Ktoré observations odhalia helper collision?
10. Ako preukážeš stable resource identity medzi revisions?

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
