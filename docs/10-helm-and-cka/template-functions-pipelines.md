# Template functions a pipelines

Helm template engine premieňa hodnoty a release context na text, ktorý sa následne interpretuje ako YAML a Kubernetes objekty. Funkcia alebo pipeline preto nie je iba syntaktická pomôcka. Je to compiler boundary, ktorá môže zmeniť typ, význam, dôvernosť, deterministickosť aj lifecycle výsledného resource-u.

Kľúčová otázka nie je „ktorú funkciu poznám“, ale:

```text
aký input subject vstupuje
→ akú transformáciu vykonávam
→ aký typ/text vzniká
→ do ktorého YAML a Kubernetes fieldu sa vloží
→ aký runtime a business dôsledok má výsledok
```

## 1. Dominantný lifecycle

```text
values path a presence contract
→ type/schema validation
→ function alebo pipeline evaluation
→ normalization a merge
→ serialization a whitespace
→ rendered field identity
→ YAML/API/admission validation
→ runtime effect
→ deterministic replay a evidence
```

Pipeline je bezpečná iba vtedy, keď je pri každom kroku jasný vstupný typ, výstupný typ, empty semantics a trust boundary.

## 2. Atlas transform subject

Atlas release používa subject z predchádzajúcej kapitoly:

```text
chart CH57
values bundle V57
manifest M57
release payments-prod revision 18
cluster K136
```

Kritické values:

```yaml
legacyAuthorizer:
  enabled: false

image:
  digest: sha256:I57

podAnnotations:
  atlas.example/release: C57
```

Kritické rendered fields:

```text
ConfigMap data.legacy-authorizer-enabled
Deployment container image
Pod template annotations
Service a Deployment selectors
```

Transform evidence musí spájať konkrétny values path s konkrétnym rendered fieldom. Nestačí vedieť, že „chart sa vyrenderoval“.

## 3. Funkcia a pipeline

Funkcia:

```gotemplate
{{ quote .Values.logLevel }}
```

Pipeline:

```gotemplate
{{ .Values.logLevel | lower | quote }}
```

Pipeline posiela výsledok ľavej časti ako posledný argument ďalšej funkcie:

```gotemplate
{{ .Values.name | repeat 3 | quote }}
```

je konceptuálne:

```gotemplate
{{ quote (repeat 3 .Values.name) }}
```

Pri viacargumentových funkciách môže nesprávny mentálny model vytvoriť validný, ale semanticky chybný output.

## 4. Pipeline ako typed transformačný graph

Čitateľná pipeline má typicky kroky:

```text
source
→ presence/default rozhodnutie
→ type conversion alebo normalization
→ escaping/quoting
→ serialization
→ indentation
```

Príklad:

```gotemplate
{{ .Values.podAnnotations | default dict | toYaml | nindent 8 }}
```

Implicitný type graph:

```text
map alebo nil
→ map
→ YAML string
→ newline + indented YAML string
```

Ak sa tento graph nedá jednoducho vysvetliť, pipeline rozdeľ na pomenované intermediate variables alebo named helper.

## 5. Tri typing vrstvy

Helm chart pracuje minimálne s troma typing vrstvami:

```text
YAML/CLI values parsing
→ Go template runtime types
→ rendered YAML + Kubernetes OpenAPI schema
```

Príklad:

```yaml
replicas: 3
version: "3"
enabled: false
```

A:

```bash
--set replicas=3
--set-string version=3
```

môžu vytvoriť odlišné Go types a následne odlišný YAML output.

String field:

```yaml
env:
  - name: LOG_LEVEL
    value: {{ .Values.logLevel | quote }}
```

Numeric Kubernetes field:

```yaml
replicas: {{ .Values.replicaCount }}
```

Všeobecné pravidlo „všetko quote-ni“ je rovnako nesprávne ako „nič nequote-ni“. Typ určuje cieľový API contract.

## 6. Presence, empty a explicitná hodnota

Helm/Sprig empty semantics považuje podľa typu za empty napríklad:

- `nil`;
- prázdny string;
- `0`;
- `false`;
- prázdny list alebo mapu.

To vytvára zásadný rozdiel:

```text
key chýba
≠ key je false
≠ key je 0
≠ key je prázdny string
```

Tieto stavy môžu mať odlišný business význam.

## 7. `default` ako policy decision

```gotemplate
{{ .Values.service.port | default 8080 }}
```

`default` použije fallback pri empty inpute. Preto:

```gotemplate
{{ .Values.legacyAuthorizer.enabled | default true }}
```

nevie odlíšiť explicitné `false` od chýbajúcej hodnoty.

Static defaults patria primárne do `values.yaml`. `default` používaj pre computed fallback alebo pre contract, kde všetky empty hodnoty skutočne znamenajú to isté.

Bezpečný boolean contract môže použiť schema s defaultom alebo explicitnú presence logiku:

```gotemplate
{{- if hasKey .Values.legacyAuthorizer "enabled" -}}
{{ .Values.legacyAuthorizer.enabled }}
{{- else -}}
true
{{- end -}}
```

Ešte lepšie je mať schema/default contract, ktorý nevyžaduje duplicitu v template.

## 8. `required`, `fail` a schema boundaries

Required value:

```gotemplate
{{ required "image.digest is required" .Values.image.digest }}
```

Semantic invariant:

```gotemplate
{{- if and .Values.ingress.enabled (empty .Values.ingress.host) }}
{{- fail "ingress.host must be set when ingress.enabled=true" }}
{{- end }}
```

Rozdelenie zodpovedností:

```text
values.schema.json
→ typy, required fields, enum, štruktúra

required/fail
→ chart-specific cross-field invariant pri renderi

Kubernetes API/admission
→ resource schema a platform policy

runtime test
→ controller a application outcome
```

Error message nesmie obsahovať secret payload alebo celý sensitive object.

## 9. `coalesce` a fallback chains

```gotemplate
{{ coalesce .Values.serviceAccount.name .Values.global.serviceAccountName (include "atlas-payments.fullname" .) }}
```

`coalesce` vyberie prvú non-empty hodnotu. Je vhodný iba pri explicitnej precedence, ktorú operator dokáže rekonštruovať.

Dlhý fallback chain vytvára hidden configuration:

```text
local value
→ global value
→ chart metadata
→ computed release name
→ live lookup
```

Incident potom nevie určiť authoritative source. Kritické identity a credentials majú mať kratší, dokumentovaný contract.

## 10. Type conversion

Príklady:

```gotemplate
{{ int .Values.service.port }}
{{ toString .Values.externalId | quote }}
{{ toJson .Values.policy | quote }}
```

Explicitná conversion môže byť správna, ak vstupný contract pripúšťa viac source formats. Nemá však maskovať invalid input.

```text
silent coercion
→ render succeeds
→ API prijme nečakaný typ alebo string formu
→ application interpretuje inú hodnotu
```

Schema validation je bezpečnejšia než široké coercion rules roztrúsené po templates.

## 11. Map access a missing intermediate objects

Dot notation:

```gotemplate
{{ .Values.image.repository }}
```

Problematic key:

```gotemplate
{{ index .Values.annotations "atlas.example/key" }}
```

Nested fallback:

```gotemplate
{{ dig "service" "port" 8080 .Values }}
```

Dlhý dot chain môže zlyhať na chýbajúcom intermediate objecte. Najprv fixni alebo default-ni mapu, nie iba posledný leaf.

```gotemplate
{{- $service := .Values.service | default dict -}}
port: {{ get $service "port" | default 8080 }}
```

Aj tu platí, že `0` môže byť explicitná hodnota a `default` ju zmení.

## 12. Dictionaries, mutation a copy boundary

```gotemplate
{{- $labels := dict
      "app.kubernetes.io/name" (include "atlas-payments.name" .)
      "app.kubernetes.io/instance" .Release.Name
}}
```

`set` a `unset` mutujú mapu. Nested mapy môžu byť zdieľané references. Preto merge workflow potrebuje explicitný copy contract:

```gotemplate
{{- $merged := mergeOverwrite (deepCopy .Values.defaults) .Values.overrides -}}
```

Bez `deepCopy` môže helper zmeniť input, ktorý neskôr používa iný template. Výsledok potom závisí od evaluation orderu a je ťažko reprodukovateľný.

## 13. Merge semantics

Pred použitím `merge` alebo `mergeOverwrite` fixni:

- ktorý source má prioritu;
- čo znamená `null`;
- ako sa správajú nested maps;
- či arrays nahrádzajú alebo skladajú;
- čo sa deje s `false` a `0`;
- či input maps zostávajú immutable.

Test matrix:

```text
missing leaf
explicit false
explicit zero
empty map
null
nested override
list replacement
```

Merge contract nesmie byť založený na názve funkcie alebo odhade direction semantics.

## 14. Serialization boundary

```gotemplate
{{- with .Values.podSecurityContext }}
securityContext:
{{ toYaml . | nindent 2 }}
{{- end }}
```

`toYaml` vracia text. Po serializácii už template engine nepozná semantic typ výsledného YAML subtree-u.

Potential chain:

```text
Go map
→ YAML string
→ indentation
→ outer YAML parse
→ Kubernetes object
```

Chyba môže vzniknúť v každej hranici. Preto testuj final rendered document, nie iba helper output.

## 15. `indent`, `nindent` a whitespace

`indent N` odsadí riadky. `nindent N` najprv pridá newline a potom odsadí.

```gotemplate
metadata:
  labels:
{{ include "atlas-payments.labels" . | nindent 4 }}
```

Whitespace trim markers:

```gotemplate
{{- if .Values.enabled }}
enabled: true
{{- end }}
```

Agresívny trim môže spojiť YAML tokeny:

```text
food: "PIZZA"mug: "true"
```

Indentation a whitespace sú súčasť output contractu. Helper nemá hard-code-núť caller-specific nesting.

## 16. `include` ako string boundary

```gotemplate
{{ include "atlas-payments.labels" . | nindent 4 }}
```

`include` vyrenderuje named template do stringu, ktorý možno ďalej transformovať. To je praktické, ale vytvára textový boundary:

```text
helper scope
→ helper text output
→ pipeline transform
→ caller YAML position
```

Caller musí poznať output shape: scalar, YAML map, list alebo celý fragment.

## 17. `tpl` ako rozšírenie execution boundary

```gotemplate
{{ tpl .Values.extraConfig . }}
```

`tpl` vyhodnotí string ako template. Values sa tým menia z dát na executable render input.

Riziká:

- caller môže používať sprístupnený scope;
- môže volať functions vrátane cluster-aware operations podľa Helm/version contextu;
- escaping a debugging sú zložitejšie;
- GitOps a policy review nevidia iba deklaratívny value;
- tenant alebo untrusted pull request môže rozšíriť render capability.

`tpl` používaj iba pre trusted, versionovaný contract. Nevyhodnocuj neoverený user payload v deployment pipeline s production cluster credentials.

## 18. `lookup` a live cluster dependency

```gotemplate
{{- $existing := lookup "v1" "Secret" .Release.Namespace "database-credentials" -}}
```

`lookup` číta live API pri server-connected renderi. Zavádza:

```text
cluster identity
+ Helm caller RBAC
+ live object UID/resourceVersion
+ current API availability
→ render input
```

Dôsledky:

- local render môže vytvoriť iný output;
- rovnaký chart a values nemusia dať rovnaký manifest;
- restore do nového clusteru sa správa inak;
- render potrebuje širšie RBAC;
- timeout alebo API error zlyhá template processing;
- live object môže byť stale alebo vlastnený iným controllerom.

Preferuj explicitné values alebo controller reconciliation. `lookup` používaj iba pri jasnom lifecycle dôvode a fixni observed object identity v evidence.

## 19. Nondeterminism

Nondeterministické inputs:

- `now`;
- random generators;
- generated certificates;
- live `lookup`;
- mutable `.Capabilities` assumptions;
- plugins/custom functions;
- unordered alebo mutation-dependent map processing.

Causal failure:

```text
rovnaký source a values
→ nový random secret pri upgrade
→ Pod credentials sa zmenia
→ downstream credential ostane starý
→ rollout je green, authentication zlyháva
```

Generated identity vytvor raz v controlled lifecycle-e, ulož ju v authoritative secret systeme a pri ďalšom renderi používaj stabilnú reference.

## 20. `.Capabilities` a target platform

```gotemplate
{{- if .Capabilities.APIVersions.Has "policy/v1/PodDisruptionBudget" }}
apiVersion: policy/v1
{{- else }}
{{- fail "policy/v1 PodDisruptionBudget is required" }}
{{- end }}
```

Local render capabilities závisia od flags a Helm defaults. Production test má používať explicitný target Kubernetes/API inventory alebo server validation proti reprezentatívnemu clusteru.

Compatibility fallback nie je vždy správna voľba. Ak staré API už nie je podporovaným platformovým contractom, fail je bezpečnejší než tiché renderovanie legacy variantu.

## 21. Worked failure: explicitné `false` sa zmení na `true`

Atlas values V57 obsahovali:

```yaml
legacyAuthorizer:
  enabled: false
```

Template:

```gotemplate
legacy-authorizer-enabled: {{ .Values.legacyAuthorizer.enabled | default true | quote }}
```

Rendered M57:

```yaml
data:
  legacy-authorizer-enabled: "true"
```

### Subject identity

```text
values source/path: V57 / legacyAuthorizer.enabled
Go runtime value: bool(false)
pipeline: default true → quote
rendered field: ConfigMap/data/legacy-authorizer-enabled
manifest: M57
Pod config generation: checksum CFG57
request: P-884
```

### Competing hypotheses

1. Effective values neobsahujú `false`.
2. CLI override vytvoril string `"false"` alebo `true`.
3. Pipeline empty semantics aktivovali fallback.
4. Helper alebo merge prepísal subtree.
5. ConfigMap bola správna, ale Pod používa starý projection/env snapshot.
6. Application parsuje string opačne alebo používa iný key.
7. Traffic ide na old-generation Pod.

### Discriminating observations

```text
helm get values --all
→ potvrdí effective value

type-focused render test
→ potvrdí bool false pred pipeline

helm template --show-only templates/configmap.yaml
→ ukáže rendered field

live ConfigMap + managedFields
→ odlíši admission/manual mutation

Pod template checksum a creation time
→ odlíši stale Pod generation

process-loaded config endpoint alebo redacted startup log
→ odlíši delivery od application parse

request trace + Pod UID
→ odlíši traffic cohort
```

### Finding

Root cause je `default` empty semantics. `false` je empty, preto fallback `true` vyhral. Quote iba serializovalo už chybný boolean verdict.

### Containment

- zastav promotion M57;
- zachovaj exact values, render a live/process evidence;
- vypni legacy path cez úzky authoritative control, ak je možné bez ďalšieho driftu;
- nevkladaj debug payload s celými values alebo Secrets do CI logu;
- nepatchuj iba live ConfigMap bez opravy source/template writera.

### Recovery

```gotemplate
{{- if hasKey .Values.legacyAuthorizer "enabled" -}}
legacy-authorizer-enabled: {{ .Values.legacyAuthorizer.enabled | quote }}
{{- else -}}
legacy-authorizer-enabled: "true"
{{- end -}}
```

Alebo presuň default do schema/default contractu a renderuj value priamo.

Potom:

1. pridaj golden tests pre missing, `false` a `true`;
2. pridaj semantic assertion nad rendered ConfigMap;
3. vytvor CH58/M58;
4. vykonaj server validation;
5. rolloutni novú Pod generation;
6. over process-loaded state a request P-884-like business path.

### Original a forbidden outcome verification

- legacy flag je `false` v effective values, renderi, live ConfigMap aj procese;
- explicitné `true` stále funguje;
- missing value používa dokumentovaný default;
- rovnaký input vytvorí rovnaký manifest digest;
- old Pod generation už nie je endpoint eligible;
- payment operation vznikne presne raz.

### Earlier controls

- schema tests;
- values presence/type matrix;
- helper/pipeline unit tests;
- rendered semantic assertions;
- deterministic render gate;
- source-to-field provenance pre critical flags.

## 22. Ďalšie failure boundaries

### `toYaml` + nesprávny `nindent`

Validný subtree sa vloží na zlú úroveň. YAML môže byť syntakticky validný, ale field skončí mimo očakávaného objectu.

### `mergeOverwrite` bez copy boundary

Jeden helper zmutuje shared mapu a neskorší template dostane iný input podľa evaluation orderu.

### `tpl` nad untrusted inputom

PR values získajú template execution capability a môžu používať production caller scope alebo live API reads.

### `lookup` ako source of truth

Release render závisí od live objectu, ktorý nie je versionovaný s chartom. Restore alebo diff nevie reprodukovať rovnaký desired state.

### Random credential v každom renderi

Upgrade vykoná neplánovanú rotation a rollback nevytvorí pôvodný credential subject.

### `Capabilities` z lokálneho defaultu

CI vyrenderuje API variant, ktorý nezodpovedá target clusteru.

## 23. Referenčný function catalog

### Presence a policy

- `default`;
- `required`;
- `fail`;
- `empty`;
- `hasKey`;
- `coalesce`.

### Types a structures

- `int`, `int64`, `toString`;
- `dict`, `list`;
- `get`, `index`, `dig`;
- `set`, `unset`;
- `deepCopy`, `merge`, `mergeOverwrite`.

### Serialization a formatting

- `quote`, `squote`;
- `toYaml`, `fromYaml`;
- `toJson`, `fromJson`;
- `indent`, `nindent`;
- whitespace trim markers.

### Dynamic execution a cluster context

- `tpl`;
- `lookup`;
- `.Capabilities.APIVersions.Has`;
- `include`.

Catalog je reference. Pri návrhu začni typovým a lifecycle modelom, nie výberom funkcie.

## 24. Debugging workflow

```text
exact values sources a types
→ isolate smallest template/field
→ inspect each intermediate value
→ render exact target capabilities
→ parse final YAML
→ server-side validate/admission diff
→ compare live object
→ verify process-loaded a business state
```

Príkazy:

```bash
helm lint ./chart -f values-test.yaml
helm template payments-prod ./chart \
  -f values-prod.yaml \
  --show-only templates/configmap.yaml \
  --debug
helm install payments-prod ./chart \
  -f values-prod.yaml \
  --dry-run=server \
  --debug \
  -n atlas-payments-prod
```

Debug output rediguj. `--debug` môže exponovať rendered sensitive fields.

## 25. Anti-patterny

- pipeline bez vysvetliteľného type graphu;
- `default true` nad explicitným booleanom;
- silent coercion namiesto schema validation;
- nested dot chain bez presence guardu;
- map mutation bez copy contractu;
- merge semantics bez test matrix;
- `toYaml` bez final rendered YAML testu;
- hard-coded indentation v helper outpute;
- `tpl` nad untrusted values;
- `lookup` ako hlavný desired-state source;
- random/time function v stable resource identity;
- local capabilities považované za target-cluster verdict;
- incident debugging cez dump celých values alebo Secrets.

## 26. Kontrolné otázky

1. Aký type graph vytvára konkrétna pipeline?
2. Prečo `false` a `0` nie sú to isté ako missing key?
3. Kedy je `default` správny policy mechanism a kedy nie?
4. Ako rozdelíš schema, `required`/`fail` a API validation zodpovednosti?
5. Prečo map mutation potrebuje copy boundary?
6. Čo sa stráca pri `toYaml` serialization boundary?
7. Ako `tpl` mení trust model values?
8. Ktoré identity pridáva `lookup` do render subjectu?
9. Ako preukážeš deterministic render?
10. Ktoré observation points odlíšia render chybu od stale Pod konfigurácie?

## Glossary impact

Relevantné pojmy: typed render pipeline, values presence contract, Helm empty semantics, rendered-field identity, template type graph, merge mutation boundary, serialization boundary, deterministic render verdict, dynamic template execution boundary, live-lookup render subject, capability-conditioned render a source-to-field provenance.

## Oficiálna dokumentácia

- [Template Functions and Pipelines](https://helm.sh/docs/chart_template_guide/functions_and_pipelines/)
- [Template Function List](https://helm.sh/docs/chart_template_guide/function_list/)
- [Flow Control](https://helm.sh/docs/chart_template_guide/control_structures/)
- [Debugging Templates](https://helm.sh/docs/chart_template_guide/debugging/)
- [Chart Development Tips and Tricks](https://helm.sh/docs/howto/charts_tips_and_tricks/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Helm chart, template, values a release](helm-chart-template-values-release.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Named templates →](named-templates.md)
<!-- KNOWLEDGE-NAVIGATION:END -->