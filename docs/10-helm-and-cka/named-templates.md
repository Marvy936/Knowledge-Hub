# Named templates

Named template je reusable fragment Helm template logiky s globálnym menom. Používa sa na štandardizáciu labels, names, selectors, annotations, image references, ServiceAccount names a opakovaných YAML blocks. Helper však nie je bežná funkcia s typovaným signature; prijíma jeden scope object a vracia text. Jeho contract preto musí byť explicitný.

## 1. `define`

Named template sa deklaruje cez `define`:

```gotemplate
{{/* Common labels for application resources. */}}
{{- define "payments.labels" -}}
app.kubernetes.io/name: {{ include "payments.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}
```

`define` samo nevytvorí manifest output. Fragment sa vyrenderuje až pri zavolaní.

## 2. `_helpers.tpl`

Súbory v `templates/` začínajúce `_` sa nepovažujú za samostatné Kubernetes manifests. Konvenčné miesto helperov je:

```text
templates/_helpers.tpl
```

Veľký chart môže helpers rozdeliť:

```text
templates/
├── _names.tpl
├── _labels.tpl
├── _images.tpl
└── _validation.tpl
```

Názov súboru nie je namespace. Všetky named templates sú stále súčasťou globálneho template namespace-u release renderu.

## 3. Globálne mená

Parent chart a všetky subcharts sa kompilujú spolu. Dve definitions s rovnakým menom kolidujú; použitá môže byť definition načítaná ako posledná.

Nepoužívaj:

```gotemplate
{{ define "labels" }}
```

Preferuj chart-specific prefix:

```gotemplate
{{ define "payments.labels" }}
```

Pri nekompatibilnej zmene reusable helper contractu môže byť vhodný versioned názov:

```gotemplate
{{ define "platform.v2.podLabels" }}
```

Chart version v názve helpera nepoužívaj automaticky pri každom release; iba keď skutočne potrebuješ súbežné contracts.

## 4. `template` action

```gotemplate
metadata:
  labels:
    {{- template "payments.labels" . }}
```

`template` vloží output inline. Je to Go template action, nie pipeline function. Preto sa jeho output nedá pohodlne poslať do `nindent`, `quote` alebo ďalších transformácií.

Pri YAML fragments je preto často vhodnejší `include`.

## 5. `include` function

```gotemplate
metadata:
  labels:
{{ include "payments.labels" . | nindent 4 }}
```

`include` vráti output helpera ako string a možno ho použiť v pipeline.

Typické použitie:

```gotemplate
name: {{ include "payments.fullname" . }}
```

```gotemplate
selector:
{{ include "payments.selectorLabels" . | nindent 4 }}
```

```gotemplate
checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
```

## 6. Scope musí byť odovzdaný

Helper nedostane automaticky pôvodný root context:

```gotemplate
{{ template "payments.labels" }}
```

V helperi bude `.` bez požadovaného `.Chart`, `.Release` alebo `.Values` contextu.

Správne:

```gotemplate
{{ template "payments.labels" . }}
```

alebo:

```gotemplate
{{ include "payments.labels" . }}
```

Scope je súčasť helper contractu.

## 7. `$` nie je univerzálny globálny root

V named template sa `$` viaže na scope odovzdaný pri volaní.

Ak zavoláš:

```gotemplate
{{ include "payments.port" .Values.service }}
```

potom `.` aj `$` v helperi reprezentujú `.Values.service`, nie pôvodný chart root.

Helper, ktorý potrebuje root aj local value, má dostať explicitný dictionary argument.

## 8. Explicitný argument contract cez `dict`

Volanie:

```gotemplate
{{ include "payments.containerPort" (dict
    "root" .
    "port" .Values.service.port
    "name" "http"
) }}
```

Helper:

```gotemplate
{{- define "payments.containerPort" -}}
- name: {{ .name | quote }}
  containerPort: {{ required "port is required" .port }}
  protocol: TCP
{{- end -}}
```

Root sa používa cez:

```gotemplate
{{ .root.Release.Name }}
```

Takýto pattern vytvára čitateľnejší pseudo-signature než nezdokumentovaný polymorfný scope.

## 9. Naming helpers

Bežné helpers:

```gotemplate
{{- define "payments.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "payments.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name (include "payments.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
```

Naming contract musí zohľadniť:

- Kubernetes DNS limity,
- release uniqueness,
- upgrade stability,
- namespace scope,
- resource-name immutability,
- truncation collision,
- backward compatibility existujúcich resources.

Zmena fullname helpera môže počas upgrade vytvoriť nové resources namiesto aktualizácie existujúcich.

## 10. Selector labels vs. common labels

Selector labels musia zostať stabilné a zhodovať sa medzi workload selectorom a Pod template labels.

```gotemplate
{{- define "payments.selectorLabels" -}}
app.kubernetes.io/name: {{ include "payments.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}
```

Common labels môžu obsahovať aj mutable metadata:

```gotemplate
{{- define "payments.labels" -}}
helm.sh/chart: {{ include "payments.chart" . }}
{{ include "payments.selectorLabels" . }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}
```

Nedávaj chart version alebo app version do immutable Deployment selectoru.

## 11. Image helper

```gotemplate
{{- define "payments.image" -}}
{{- $registry := .Values.global.imageRegistry | default .Values.image.registry -}}
{{- $repository := required "image.repository is required" .Values.image.repository -}}
{{- $tag := .Values.image.tag | default .Chart.AppVersion -}}
{{- if $registry -}}
{{ printf "%s/%s:%s" $registry $repository $tag }}
{{- else -}}
{{ printf "%s:%s" $repository $tag }}
{{- end -}}
{{- end -}}
```

Helper musí mať jasný contract pre:

- tag vs. digest,
- registry prefix,
- empty `appVersion`,
- escaping/quoting,
- global overrides,
- immutable production references.

Digest a tag kombináciu generuj podľa OCI reference pravidiel, nie jednoduchým string concatenation bez testov.

## 12. ServiceAccount name helper

```gotemplate
{{- define "payments.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
{{ default (include "payments.fullname" .) .Values.serviceAccount.name }}
{{- else -}}
{{ required "serviceAccount.name is required when create=false" .Values.serviceAccount.name }}
{{- end -}}
{{- end -}}
```

Helper vyjadruje ownership contract:

- chart vytvára ServiceAccount,
- alebo používa external ServiceAccount.

Silent fallback na `default` ServiceAccount môže vytvoriť security regression.

## 13. Helper output type

Named template vždy produkuje text. Môže reprezentovať:

- scalar,
- YAML map,
- YAML list,
- celý resource fragment,
- JSON/YAML serializovaný object.

Caller musí vedieť, ktorý typ textu dostáva.

Dokumentuj helper napríklad:

```gotemplate
{{/*
payments.selectorLabels renders an unindented YAML map.
Input: root chart context.
Output: stable selector labels without a leading newline.
*/}}
```

## 14. Returning structured data

Helm helper priamo nevracia typed map. Možný workaround:

```gotemplate
{{- define "payments.defaultResources" -}}
requests:
  cpu: 100m
  memory: 128Mi
{{- end -}}

{{- $defaults := include "payments.defaultResources" . | fromYaml -}}
```

Tento pattern pridáva serialize/parse boundary. Používaj ho opatrne:

- YAML typing môže meniť hodnoty,
- parse error je menej čitateľný,
- helper contract je skrytý,
- native values object je často jednoduchší.

## 15. `block`

`block` definuje default template content a okamžite ho vykreslí:

```gotemplate
{{ block "payments.podAnnotations" . }}
example.com/managed: "true"
{{ end }}
```

Iná definition rovnakého mena ho môže nahradiť. V multi-chart renderi je override behavior citlivý na globálne names a load order.

Pre väčšinu application charts sú explicitné values alebo library-chart contracts čitateľnejšie než implicitné `block` override-y.

## 16. Library charts

Library chart poskytuje reusable helpers a primitives, ale sám nevytvára release workload resources ako bežný application chart.

Vhodné použitie:

- organizáciou štandardizované labels,
- Pod/container fragments,
- common security context,
- common workload templates,
- policy-conformant resource contracts.

Riziká:

- breaking change zasiahne veľa charts,
- globálne helper name collisions,
- príliš všeobecná abstraction,
- skrytý output a ťažký debugging,
- dependency upgrade mení rendered manifests bez zmeny parent templates.

Library chart versionuj ako API contract a testuj consumers.

## 17. Parent a subchart helpers

Templates parent chartu a subcharts zdieľajú globálny namespace, ale values scope ostáva oddelený podľa chart modelu.

Subchart helper nemá implicitný prístup ku všetkým parent values. Parent môže:

- override-nuť subchart values,
- použiť `global` values,
- volať globally named helper podľa dostupnosti,
- importovať library chart helpers.

Nespoliehaj sa na náhodný load order pri nahrádzaní helpera subchartu.

## 18. Indentation contract

Helper pre YAML map má typicky renderovať bez caller-specific indentation:

```gotemplate
{{- define "payments.selectorLabels" -}}
app.kubernetes.io/name: {{ include "payments.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}
```

Caller rozhodne:

```gotemplate
matchLabels:
{{ include "payments.selectorLabels" . | nindent 6 }}
```

Ak helper obsahuje hard-coded indentation, reuse v inom nesting leveli zlyhá.

## 19. Whitespace contract

Používaj trim markers konzistentne:

```gotemplate
{{- define "payments.name" -}}
{{- .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
```

Scalar helper nemá pridávať nečakané newlines. YAML fragment helper môže mať viac riadkov, ale caller musí vedieť, či output začína alebo končí newline.

Testuj cez:

```bash
helm template example ./chart --debug
```

## 20. Recursive a cyclic helpers

Named templates sa môžu volať navzájom. Cyklus:

```text
helper A → helper B → helper A
```

vedie k render failure alebo recursion problému. Helper graph udržuj acyklický a jednoduchý:

```text
primitive names
→ labels/selectors
→ resource fragments
→ manifests
```

## 21. Side effects a nondeterminism

Helper s `now`, random funkciou alebo `lookup` nie je čistý transform.

Dôsledky:

- output sa mení bez values zmeny,
- chart diff je nestabilný,
- release rollback nemusí reprodukovať pôvodný manifest,
- unit testy sú komplikované.

Core naming, labels a selector helpers majú byť deterministické.

## 22. Testing helpers

Over aspoň:

- default values,
- overrides,
- dlhé names,
- trailing hyphens,
- empty a missing values,
- boolean `false` a numeric `0`,
- subchart collision,
- multiple Kubernetes versions,
- stable selectors medzi chart revisions,
- exact rendered indentation.

Praktický test:

```bash
helm template release-a ./chart -f testdata/defaults.yaml > rendered.yaml
kubectl apply --dry-run=server -f rendered.yaml
```

Pre critical helper output používaj snapshot/golden testy a semantic assertions.

## 23. Debugging

Pri helper failure:

1. identifikuj názov helpera,
2. over odovzdaný scope,
3. vypíš relevantný typ/value iba bez secrets,
4. zjednoduš pipeline,
5. over whitespace a indentation,
6. renderuj iba konkrétny template cez `--show-only`,
7. skontroluj collision s dependency/library chartom.

Príklad:

```bash
helm template example ./chart \
  --show-only templates/deployment.yaml \
  --debug
```

## 24. Anti-patterny

### Helper s generickým globálnym názvom

`labels`, `name` alebo `fullname` môže kolidovať so subchartom.

### Helper očakáva nezdokumentovaný scope

Caller odovzdá `.Values` namiesto rootu a `.Release` je `nil`.

### Hard-coded indentation v helperi

Fragment nie je reusable v inom YAML nesting leveli.

### Jeden helper generuje celý komplexný workload

Abstraction zakrýva Kubernetes resource a komplikuje policy, diff a debugging.

### Mutable metadata v selector helperi

Upgrade zlyhá na immutable selector alebo vytvorí ownership mismatch.

### Override subchart helpera cez load-order trik

Správanie nie je robustný API contract.

### Helper obsahuje secrets v error message alebo debug outpute

Render/CI logs sa stanú exfiltration kanálom.

## 25. Kontrolné otázky

1. Prečo sú názvy Helm templates globálne?
2. Aký je rozdiel medzi `template` a `include`?
3. Prečo helper nedostane automaticky root scope?
4. Čo znamená `$` v named template?
5. Ako odovzdáš helperu viac explicitných argumentov?
6. Prečo musia selector labels zostať stabilné?
7. Aký indentation contract má reusable YAML fragment?
8. Kedy použiť library chart?
9. Prečo je `block` override rizikovejší než explicitné values?
10. Ako diagnostikuješ helper collision so subchartom?

## Glossary impact

Relevantné pojmy: named template — Helm, Helm partial, `_helpers.tpl`, global template namespace, `define`, `template`, `include`, `block`, helper scope, helper contract, chart-prefixed helper, selector-label helper, library chart a structured helper output.

## Oficiálna dokumentácia

- [Named Templates](https://helm.sh/docs/chart_template_guide/named_templates/)
- [Library Charts](https://helm.sh/docs/topics/library_charts/)
- [Subcharts and Global Values](https://helm.sh/docs/chart_template_guide/subcharts_and_globals/)
- [Chart Template Guide](https://helm.sh/docs/chart_template_guide/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Template functions a pipelines](template-functions-pipelines.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Chart dependencies →](chart-dependencies.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
