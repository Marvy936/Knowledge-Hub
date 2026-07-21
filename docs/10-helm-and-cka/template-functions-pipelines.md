# Template functions a pipelines

Helm templates nie sú samostatný programovací jazyk. Spájajú Go `text/template`, Helm built-in objects, Helm-specific helpers a veľkú časť Sprig function library. Výsledkom templating-u musí byť deterministický, validný a bezpečný Kubernetes manifest. Funkcie a pipelines preto nie sú iba skrátený zápis; tvoria transformačnú vrstvu medzi typed values a YAML outputom.

## 1. Funkcia

Základná syntax:

```gotemplate
{{ functionName argument1 argument2 }}
```

Príklad:

```yaml
metadata:
  name: {{ printf "%s-api" .Release.Name }}
```

Helm vyhodnotí argumenty, zavolá funkciu a vloží jej textový výsledok do renderovaného outputu.

## 2. Pipeline

Pipeline posiela výsledok ľavej časti ako **posledný argument** nasledujúcej funkcie:

```gotemplate
{{ .Values.image.repository | default "nginx" | lower | quote }}
```

Je to ekvivalent približne:

```gotemplate
{{ quote (lower (default "nginx" .Values.image.repository)) }}
```

Pri viacargumentovej funkcii je poradie podstatné:

```gotemplate
{{ .Values.name | repeat 3 | quote }}
```

Výsledok `.Values.name` je posledný argument funkcie `repeat`.

## 3. Pipeline ako transformačný reťazec

Čitateľná pipeline má zvyčajne tento tvar:

```text
source value
→ default/validation
→ normalization
→ serialization
→ indentation
```

Príklad:

```gotemplate
{{ .Values.podAnnotations | default dict | toYaml | nindent 8 }}
```

Každý krok má mať jasný typ vstupu a výstupu. Príliš dlhá pipeline je ťažko testovateľná; rozdeľ ju cez premenné alebo named helper.

## 4. Quoting a YAML typing

String value renderuj explicitne:

```yaml
env:
  - name: LOG_LEVEL
    value: {{ .Values.logLevel | quote }}
```

Numeric Kubernetes fields však nemajú byť automaticky quoted:

```yaml
replicas: {{ .Values.replicaCount }}
```

YAML parser, Helm values parser a Kubernetes OpenAPI schema tvoria tri odlišné typing vrstvy. `"3"` a `3` nemusia byť zameniteľné.

## 5. `default`

```gotemplate
{{ .Values.service.port | default 8080 }}
```

`default` použije fallback pri hodnote považovanej za empty. Do empty kategórie patria podľa typu napríklad `0`, `false`, prázdny string, prázdny list/map alebo `nil`.

Dôsledok:

```gotemplate
{{ .Values.feature.enabled | default true }}
```

nedokáže spoľahlivo odlíšiť explicitné `false` od chýbajúcej hodnoty. Pre boolean tri-state contract používaj `hasKey`, explicitný object alebo schema.

Statické defaults patria primárne do `values.yaml`. `default` je vhodný najmä pre computed fallback alebo backward-compatible transition.

## 6. `required` a `fail`

Povinná hodnota:

```gotemplate
{{ required "image.repository is required" .Values.image.repository }}
```

Explicitná business validácia:

```gotemplate
{{- if and .Values.ingress.enabled (empty .Values.ingress.host) }}
{{- fail "ingress.host must be set when ingress.enabled=true" }}
{{- end }}
```

`required` a `fail` zlyhajú počas renderovania. Nenahrádzajú `values.schema.json`, Kubernetes API validation ani admission policy; dopĺňajú ich pre chart-specific invariants.

## 7. Logic a comparison functions

Go template operators sú funkcie:

```gotemplate
{{ if and .Values.enabled (gt .Values.replicaCount 1) }}
```

Bežné funkcie:

- `and`, `or`, `not`,
- `eq`, `ne`, `lt`, `le`, `gt`, `ge`,
- `empty`,
- `coalesce`,
- `ternary`.

Komplexný boolean výraz radšej ulož do pomenovanej premennej:

```gotemplate
{{- $haEnabled := and .Values.ha.enabled (ge (int .Values.replicaCount) 3) }}
```

## 8. `coalesce`

Vyberie prvú non-empty hodnotu:

```gotemplate
{{ coalesce .Values.serviceAccount.name .Values.global.serviceAccountName (include "app.fullname" .) }}
```

Používaj ho pri jasnej precedence. Príliš veľa fallback vrstiev vytvára skrytú konfiguráciu, ktorú operator nevie jednoducho vysvetliť.

## 9. String functions

Typické:

```gotemplate
{{ .Values.name | lower | replace "_" "-" | trunc 63 | trimSuffix "-" }}
```

Bežné funkcie:

- `lower`, `upper`, `title`,
- `trim`, `trimSuffix`, `trimPrefix`,
- `replace`,
- `contains`, `hasPrefix`, `hasSuffix`,
- `printf`,
- `trunc`.

Kubernetes name helper musí okrem dĺžky rešpektovať DNS naming pravidlá a collision model. Truncation môže odstrániť rozlišujúci suffix; hash alebo release identity navrhni explicitne.

## 10. Type conversion

Values môžu prísť z YAML, CLI `--set`, JSON alebo external automation. Pri nejednoznačnosti konvertuj explicitne:

```gotemplate
{{ int .Values.service.port }}
{{ toString .Values.externalId | quote }}
{{ toJson .Values.policy | quote }}
```

Funkcie typu `atoi`, `int`, `int64`, `float64`, `toString`, `toStrings` môžu zlyhať alebo vytvoriť nečakaný výsledok pri nesprávnom inpute. Schema validation je bezpečnejšia než tiché coercion.

## 11. Map access: dot, `index`, `get`, `dig`

Dot notation:

```gotemplate
{{ .Values.image.repository }}
```

Dynamický alebo problematický key:

```gotemplate
{{ index .Values.annotations "example.com/key" }}
```

Map helper:

```gotemplate
{{ get .Values.labels "team" }}
```

Nested lookup s fallbackom:

```gotemplate
{{ dig "service" "port" 8080 .Values }}
```

Pri optional nested objects nepoužívaj dlhé dot chains bez guardu; intermediate `nil` môže renderovanie prerušiť.

## 12. `hasKey`

Rozlišuje neprítomný key od prítomnej empty hodnoty:

```gotemplate
{{- if hasKey .Values.feature "enabled" }}
enabled: {{ .Values.feature.enabled }}
{{- else }}
enabled: true
{{- end }}
```

Je dôležitý pri booleanoch, nule a prázdnych collections, kde `default` mení význam explicitnej hodnoty.

## 13. Lists a dictionaries

Vytvorenie dictionary:

```gotemplate
{{- $labels := dict
      "app.kubernetes.io/name" (include "app.name" .)
      "app.kubernetes.io/instance" .Release.Name
}}
```

List:

```gotemplate
{{- $ports := list 8080 9090 }}
```

Bežné operácie:

- `dict`, `list`,
- `set`, `unset`,
- `keys`, `values`,
- `append`, `prepend`, `concat`,
- `uniq`, `sortAlpha`,
- `has`.

`set` modifikuje mapu a vracia ju. Side effects v template logic používaj opatrne; komplikujú reasoning a reuse.

## 14. Merge semantics

```gotemplate
{{- $merged := mergeOverwrite (deepCopy .Values.defaults) .Values.overrides }}
```

Rozlišuj:

- `merge` — priorita závisí od direction semantics funkcie,
- `mergeOverwrite` — neskoršie zdroje prepisujú skoršie podľa semantics,
- `deepCopy` — zabraňuje neúmyselnej mutation shared nested map.

Pred použitím merge funkcie vytvor test s nested maps, arrays, booleans a null hodnotami. Merge contract nesmie byť založený na odhade.

## 15. YAML serialization

```gotemplate
{{- with .Values.podSecurityContext }}
securityContext:
{{ toYaml . | nindent 2 }}
{{- end }}
```

Užitočné funkcie:

- `toYaml`,
- `toYamlPretty`,
- `fromYaml`,
- `fromYamlArray`,
- `toJson`, `fromJson`.

Serializovaný output vždy vizuálne over. Zlé odsadenie vytvorí syntakticky neplatný alebo semanticky iný YAML.

## 16. `indent` a `nindent`

`indent N` odsadí každý riadok. `nindent N` najprv vloží newline a potom odsadí.

Typický pattern:

```gotemplate
metadata:
  labels:
{{ include "app.labels" . | nindent 4 }}
```

`nindent` je vhodný pre block YAML. `indent` je vhodný, keď newline už existuje. Výsledok kontroluj cez `helm template`, nie iba pohľadom na source template.

## 17. Whitespace control

```gotemplate
{{- if .Values.enabled }}
enabled: true
{{- end }}
```

Pomlčka pri delimiteri odstraňuje whitespace na príslušnej strane. Agresívne trimovanie môže spojiť dva YAML tokeny:

```text
food: "PIZZA"mug: "true"
```

Whitespace je súčasť výsledného manifestu. Pri helperoch kombinuj trim markers s `nindent` konzistentne.

## 18. `tpl`

`tpl` vyhodnotí string ako Helm template:

```gotemplate
{{ tpl .Values.extraConfig . }}
```

Použitie:

- templated config file,
- user-provided annotations alebo snippets,
- environment-specific string composition.

Riziká:

- values sa menia na executable template input,
- caller môže pristupovať k sprístupnenému scope-u,
- `lookup` alebo iné functions môžu rozšíriť cluster read surface,
- debugging a escaping sa komplikujú.

`tpl` používaj iba s jasným trust boundary a dokumentovaným contractom. Nevyhodnocuj neoverený tenant input v privilegovanom deployment pipeline.

## 19. `lookup`

```gotemplate
{{- $existing := lookup "v1" "Secret" .Release.Namespace "database-credentials" }}
```

`lookup` číta live Kubernetes API. Pri nenájdenom objekte vracia empty value; API/RBAC chyba zlyhá renderovanie.

Dôsledky:

- local `helm template` nemusí reprodukovať výsledok,
- render závisí od cluster state a identity,
- GitOps diff môže byť nedeterministický,
- required RBAC sa rozširuje,
- restore do nového clusteru môže vytvoriť iný manifest.

Preferuj deklaratívne values alebo external controller. `lookup` používaj iba pri explicitnom lifecycle dôvode a testuj cez server-connected dry-run.

## 20. Nondeterministic functions

Funkcie ako random generators, `now` alebo certificate generation môžu meniť output pri každom renderi.

Riziká:

- perpetual diff,
- upgrade mení credentials alebo annotations,
- GitOps neustále reconciliuje,
- rollback nevytvorí pôvodný artifact,
- testy sú nestabilné.

Ak potrebuješ generated secret alebo identifier:

1. vytvor ho mimo chartu,
2. ulož ho v secret manageri alebo controlled release inpute,
3. versionuj jeho ownership a rotation,
4. nerenderuj novú hodnotu pri každom upgrade.

## 21. Cryptographic a encoding functions

Helm/Sprig poskytujú hashing, encoding a niektoré certificate helpers.

Rozlišuj:

- encoding (`b64enc`) nie je encryption,
- checksum annotation nie je digital signature,
- hash citlivého low-entropy secretu môže byť brute-forceable,
- generated certificate bez PKI lifecycle nie je production trust model.

Checksum helper je vhodný napríklad na rollout pri zmene ConfigMap:

```gotemplate
checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
```

Musí však byť stabilný pre semanticky rovnaký input a nesmie exponovať secret material.

## 22. `include` ako funkcia

```gotemplate
{{ include "app.labels" . | nindent 4 }}
```

`include` vráti rendered named template ako string, takže ho možno poslať do pipeline. Je preferovaný pre reusable YAML fragments, ktoré potrebujú indentation alebo ďalšiu transformáciu.

Detaily named templates sú v nasledujúcej kapitole.

## 23. `Capabilities`

Podmienenie podľa podporovaného API:

```gotemplate
{{- if .Capabilities.APIVersions.Has "policy/v1/PodDisruptionBudget" }}
apiVersion: policy/v1
{{- else }}
{{- fail "policy/v1 PodDisruptionBudget is required" }}
{{- end }}
```

`Capabilities` pri local renderi závisí od Helm flags a default assumptions. Pre CI nastav explicitné Kubernetes/API versions alebo používaj server validation proti representative clusteru.

## 24. Debugging

Základ:

```bash
helm lint ./chart
helm template example ./chart -f values-test.yaml --debug
helm install example ./chart --dry-run=server --debug -n test
```

Pri probléme oddel:

1. values typing,
2. template execution,
3. YAML parsing,
4. Kubernetes schema,
5. API availability,
6. admission,
7. runtime behavior.

## 25. Anti-patterny

### Dlhá pipeline bez pomenovaných intermediate values

Nie je jasné, ktorý krok mení typ alebo zlyháva.

### `default true` nad explicitným booleanom

Môže prepísať zámerné `false`.

### `toYaml` bez správneho `nindent`

Vytvorí neplatnú alebo zle vnorenú štruktúru.

### `tpl` nad neovereným inputom

Rozširuje template execution a cluster-read surface.

### `lookup` ako hlavný source desired state

Render závisí od náhodného live state-u a nie je reprodukovateľný.

### Random secret pri každom upgrade

Spôsobí credential rotation bez koordinácie.

### Silent type coercion

Chybná hodnota prejde renderom a zlyhá až v API alebo runtime.

## 26. Kontrolné otázky

1. Kam pipeline posiela výsledok predchádzajúceho kroku?
2. Prečo je `default` problematický pri `false` a `0`?
3. Kedy použiť `required` a kedy `values.schema.json`?
4. Aký je rozdiel medzi `indent` a `nindent`?
5. Ako odlíšiš chýbajúci key od prítomnej empty hodnoty?
6. Prečo môže byť `tpl` bezpečnostné riziko?
7. Ako `lookup` ovplyvňuje reprodukovateľnosť renderu?
8. Prečo nondeterministic functions spôsobujú GitOps drift?
9. Načo slúži `deepCopy` pri merge operáciách?
10. Ktoré validačné vrstvy nasledujú po úspešnom Helm renderi?

## Glossary impact

Relevantné pojmy: Helm template function, Helm pipeline, pipeline last argument, empty value — Helm, `default`, `required`, `fail`, `coalesce`, `hasKey`, `dict`, `list`, Helm merge, `toYaml`, `nindent`, whitespace control, `tpl`, `lookup`, nondeterministic template a Helm Capabilities.

## Oficiálna dokumentácia

- [Template Functions and Pipelines](https://helm.sh/docs/chart_template_guide/functions_and_pipelines/)
- [Template Function List](https://helm.sh/docs/chart_template_guide/function_list/)
- [Flow Control](https://helm.sh/docs/chart_template_guide/control_structures/)
- [Debugging Templates](https://helm.sh/docs/chart_template_guide/debugging/)
