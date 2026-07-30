# Praktický Helm chart — od prázdneho adresára po overený release

Táto kapitola materializuje predchádzajúci výklad do jedného malého, ale reálne použiteľného chartu. Cieľom nie je iba skopírovať YAML. Každý súbor má vysvetlenú authority, každý príkaz má pomenovanú hranicu, ktorú overuje, a výsledok sa sleduje od values cez render až po live workload.

Použijeme jednoduchú aplikáciu `atlas-api`, ktorá počúva na porte `8080`, vystavuje `/readyz`, číta log level z ConfigMapy a pri upgrade môže spustiť idempotentný schema-expand Job. Chart nepoužíva plaintext secret values. Secret sa referencuje iba menom.

## 1. Vytvorenie skeletonu a kontrola toolchainu

Najprv si over klienta a cluster context. Rovnaký chart renderovaný inou Helm major verziou alebo aplikovaný do nesprávneho contextu nie je rovnaký release subject.

```bash
helm version
kubectl config current-context
kubectl cluster-info
```

Prvý príkaz identifikuje Helm toolchain. Druhý ukáže aktívny kubeconfig context. Tretí potvrdí API endpoint, ale ešte nepreukazuje, že máš správny namespace alebo oprávnenia na release.

Vytvor chart skeleton:

```bash
helm create atlas-api
cd atlas-api
find . -maxdepth 3 -type f | sort
```

`helm create` vytvorí ukážkový chart. Pre náš walkthrough odstráň nepotrebné templates a nechaj túto štruktúru:

```text
atlas-api/
├── Chart.yaml
├── values.yaml
├── values.schema.json
└── templates/
    ├── _helpers.tpl
    ├── configmap.yaml
    ├── deployment.yaml
    ├── service.yaml
    ├── schema-expand-job.yaml
    ├── tests/
    │   └── test-connection.yaml
    └── NOTES.txt
```

Tento strom už ukazuje rozdiel medzi package metadata, configuration API a manifest templates. `Chart.yaml` identifikuje chart. `values.yaml` definuje defaults. `values.schema.json` odmieta typovo alebo štrukturálne neplatný input. `templates/` generuje Kubernetes resources.

## 2. `Chart.yaml` — identita chartu, nie aplikácie

```yaml
apiVersion: v2
name: atlas-api
description: Teaching chart for the Atlas API workload
type: application
version: 0.1.0
appVersion: "1.4.2"
kubeVersion: ">=1.30.0-0"
```

`version` je verzia chart package-u. Zvyšuje sa pri zmene templates, values contractu alebo packagingu. `appVersion` je informačný údaj o aplikácii. Helm ho automaticky nepoužije ako image tag, pokiaľ ho template explicitne nečíta. Preto produkčný image stále identifikujeme samostatne cez repository a digest.

`kubeVersion` je predbežná compatibility podmienka. Neoveruje admission webhooks, CRDs ani runtime správanie cieľového clusteru. Je to prvý gate, nie posledný.

Over metadata:

```bash
helm show chart .
```

Očakávaš, že výstup obsahuje presne `name: atlas-api`, `version: 0.1.0` a `appVersion: 1.4.2`. Tento príkaz neparsuje všetky templates a nekontaktuje cluster.

## 3. `values.yaml` — verejné configuration API chartu

```yaml
replicaCount: 2

image:
  repository: ghcr.io/example/atlas-api
  digest: sha256:1111111111111111111111111111111111111111111111111111111111111111
  pullPolicy: IfNotPresent

service:
  port: 80
  targetPort: 8080

config:
  logLevel: info
  legacyAuthorizerEnabled: false

secretRef:
  name: atlas-api-runtime

schemaExpand:
  enabled: false
  operationId: ""

resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 256Mi
```

Image používame cez digest, aby rovnaký values bundle vždy identifikoval rovnaké bytes. `legacyAuthorizerEnabled` je skutočný boolean. Nesmie sa template-ovať cez `default true`, pretože Sprig považuje explicitné `false` za empty value. Secret value nie je v chart values; chart obsahuje iba reference name.

Production override môže vyzerať takto:

```yaml
# values-prod.yaml
replicaCount: 4

image:
  digest: sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa

config:
  logLevel: warn
  legacyAuthorizerEnabled: false

schemaExpand:
  enabled: true
  operationId: schema-expand-2026-07-30-01
```

Poradie values files je súčasťou release subjectu. Neskorší file prepisuje skorší:

```bash
helm template atlas-api . \
  -f values-prod.yaml \
  -f values-prod-eu1.yaml
```

Ak oba files nastavujú `replicaCount`, platí hodnota z `values-prod-eu1.yaml`. Samotné otvorenie `values-prod.yaml` preto nepreukazuje effective configuration.

## 4. `values.schema.json` — typový gate pred renderom

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["replicaCount", "image", "service", "config", "secretRef"],
  "properties": {
    "replicaCount": {
      "type": "integer",
      "minimum": 1,
      "maximum": 20
    },
    "image": {
      "type": "object",
      "additionalProperties": false,
      "required": ["repository", "digest", "pullPolicy"],
      "properties": {
        "repository": { "type": "string", "minLength": 1 },
        "digest": {
          "type": "string",
          "pattern": "^sha256:[a-f0-9]{64}$"
        },
        "pullPolicy": {
          "type": "string",
          "enum": ["IfNotPresent", "Always", "Never"]
        }
      }
    },
    "service": {
      "type": "object",
      "additionalProperties": false,
      "required": ["port", "targetPort"],
      "properties": {
        "port": { "type": "integer", "minimum": 1, "maximum": 65535 },
        "targetPort": { "type": "integer", "minimum": 1, "maximum": 65535 }
      }
    },
    "config": {
      "type": "object",
      "additionalProperties": false,
      "required": ["logLevel", "legacyAuthorizerEnabled"],
      "properties": {
        "logLevel": {
          "type": "string",
          "enum": ["debug", "info", "warn", "error"]
        },
        "legacyAuthorizerEnabled": { "type": "boolean" }
      }
    },
    "secretRef": {
      "type": "object",
      "additionalProperties": false,
      "required": ["name"],
      "properties": {
        "name": { "type": "string", "minLength": 1 }
      }
    },
    "schemaExpand": {
      "type": "object",
      "additionalProperties": false,
      "required": ["enabled", "operationId"],
      "properties": {
        "enabled": { "type": "boolean" },
        "operationId": { "type": "string" }
      }
    },
    "resources": { "type": "object" }
  }
}
```

Schema zachytí napríklad string namiesto booleanu:

```bash
helm lint . --set-string config.legacyAuthorizerEnabled=false
```

`--set-string` úmyselne vytvorí string `"false"`. Očakávaný výsledok je chyba typu podobná:

```text
config.legacyAuthorizerEnabled: Invalid type. Expected: boolean, given: string
```

Tento test dokazuje, že configuration API odmieta zlý typ. Nedokazuje, že boolean `false` template správne interpretuje. Na to potrebujeme render test.

## 5. `_helpers.tpl` — pomenované templates s jasným vstupom

```gotemplate
{{- define "atlas-api.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "atlas-api.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name (include "atlas-api.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{- define "atlas-api.labels" -}}
app.kubernetes.io/name: {{ include "atlas-api.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" }}
{{- end -}}

{{- define "atlas-api.selectorLabels" -}}
app.kubernetes.io/name: {{ include "atlas-api.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}
```

`include` vráti rendered string, takže ho možno ďalej odsadiť alebo spracovať pipeline-om. Do helpera posielame celý root context `.`. Ak by sme z `range` alebo `with` poslali iba vnútorný object, `.Chart` a `.Release` by nemuseli byť dostupné.

Selector helper obsahuje iba stabilné labels. Chart version ani image digest do selectoru nepatria, pretože ich zmena by vytvorila immutable selector diff a rozdelila Service/Deployment identity.

## 6. ConfigMap a bezpečné spracovanie booleanu

```gotemplate
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "atlas-api.fullname" . }}
  labels:
    {{- include "atlas-api.labels" . | nindent 4 }}
data:
  LOG_LEVEL: {{ .Values.config.logLevel | quote }}
  LEGACY_AUTHORIZER_ENABLED: {{ ternary "true" "false" .Values.config.legacyAuthorizerEnabled | quote }}
```

`ternary` dostane explicitný boolean test. Hodnota `false` preto zostane `"false"`; nepoužívame `default true`.

Render iba tohto template-u:

```bash
helm template atlas-api . \
  --show-only templates/configmap.yaml \
  --set config.legacyAuthorizerEnabled=false
```

V rendered YAML musí byť:

```yaml
data:
  LOG_LEVEL: "info"
  LEGACY_AUTHORIZER_ENABLED: "false"
```

Toto je golden-render assertion. Dokazuje template output pre konkrétny input. Ešte nedokazuje, že Pod načíta ConfigMap alebo že application hodnotu použije.

## 7. Deployment — artifact, configuration a runtime identity

```gotemplate
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "atlas-api.fullname" . }}
  labels:
    {{- include "atlas-api.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 0
      maxSurge: 1
  selector:
    matchLabels:
      {{- include "atlas-api.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "atlas-api.selectorLabels" . | nindent 8 }}
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
    spec:
      containers:
        - name: atlas-api
          image: "{{ .Values.image.repository }}@{{ .Values.image.digest }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: {{ .Values.service.targetPort }}
          envFrom:
            - configMapRef:
                name: {{ include "atlas-api.fullname" . }}
            - secretRef:
                name: {{ required "secretRef.name is required" .Values.secretRef.name }}
          readinessProbe:
            httpGet:
              path: /readyz
              port: http
            initialDelaySeconds: 3
            periodSeconds: 5
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
```

Image reference používa digest. `checksum/config` vloží digest rendered ConfigMapy do Pod template annotations. Keď sa ConfigMap zmení, zmení sa Pod template a Deployment vytvorí nový ReplicaSet. Bez tohto mechanizmu môže live ConfigMap obsahovať novú hodnotu, ale staré Pody ju pri env-based configuration nikdy nenačítajú.

`required` vytvorí render error, ak secret name chýba. Neoverí však existenciu Secretu v clusteri. To zachytí server/runtime validation.

Render a skontroluj presný image:

```bash
helm template atlas-api . -f values-prod.yaml > /tmp/atlas-api.yaml

yq '.spec.template.spec.containers[0].image' \
  <(yq 'select(.kind == "Deployment")' /tmp/atlas-api.yaml)
```

Očakávaš `repository@sha256:...`, nie mutable tag. Ak `yq` nie je dostupné, použi:

```bash
awk '/image:/{print}' /tmp/atlas-api.yaml
```

Textový grep je slabší dôkaz, pretože môže zachytiť image v hooku alebo test Pode. Structured query je presnejšia.

## 8. Service — stabilná sieťová identita

```gotemplate
apiVersion: v1
kind: Service
metadata:
  name: {{ include "atlas-api.fullname" . }}
  labels:
    {{- include "atlas-api.labels" . | nindent 4 }}
spec:
  selector:
    {{- include "atlas-api.selectorLabels" . | nindent 4 }}
  ports:
    - name: http
      port: {{ .Values.service.port }}
      targetPort: http
```

Service selector sa musí presne zhodovať s Pod labels. `targetPort: http` odkazuje na pomenovaný container port. To znižuje riziko, že Service a Deployment budú používať rozdielne číselné hodnoty.

Po apply neoveruj iba existenciu Service. Over EndpointSlices:

```bash
kubectl -n atlas-api-prod get svc atlas-api-prod-atlas-api -o yaml
kubectl -n atlas-api-prod get endpointslice \
  -l kubernetes.io/service-name=atlas-api-prod-atlas-api -o wide
```

Service bez ready endpoints nedoručuje traffic. Green `kubectl get svc` preto nie je serving verdict.

## 9. Idempotentný pre-upgrade hook

```gotemplate
{{- if .Values.schemaExpand.enabled }}
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "atlas-api.fullname" . }}-schema-expand-{{ .Release.Revision }}
  annotations:
    "helm.sh/hook": pre-upgrade
    "helm.sh/hook-weight": "-10"
    "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
spec:
  backoffLimit: 1
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: schema-expand
          image: "{{ .Values.image.repository }}@{{ .Values.image.digest }}"
          args:
            - migrate
            - expand
            - --operation-id
            - {{ required "schemaExpand.operationId is required when enabled" .Values.schemaExpand.operationId | quote }}
          envFrom:
            - secretRef:
                name: {{ .Values.secretRef.name }}
{{- end }}
```

Job name obsahuje Helm revision, ale business idempotency nevychádza z názvu Jobu. `operationId` musí byť durable key v migration ledgeri. Pri timeout-e alebo opakovanom upgrade musí aplikácia vedieť rozpoznať už dokončenú operáciu a skončiť no-op verification výsledkom.

Pozri rendered hook:

```bash
helm template atlas-api . -f values-prod.yaml \
  --show-only templates/schema-expand-job.yaml
```

Ak `schemaExpand.enabled=false`, výstup bude prázdny. Ak je `true` a `operationId` chýba, render musí zlyhať. To je žiaduci fail-fast behavior.

## 10. Helm test Pod

```gotemplate
apiVersion: v1
kind: Pod
metadata:
  name: {{ include "atlas-api.fullname" . }}-test-connection
  annotations:
    "helm.sh/hook": test
spec:
  restartPolicy: Never
  containers:
    - name: curl
      image: curlimages/curl:8.10.1
      args:
        - --fail
        - --silent
        - --show-error
        - http://{{ include "atlas-api.fullname" . }}:{{ .Values.service.port }}/readyz
```

Tento test overí DNS, Service routing a readiness endpoint z cluster networku. Neoverí external ingress, authorization ani payment business flow. `helm test` preto ostáva technický integration oracle, nie celá release acceptance.

## 11. Validation ladder s konkrétnymi príkazmi

Najprv package a syntax:

```bash
helm lint . -f values-prod.yaml
```

Green výstup znamená, že chart sa načítal, schema prešla a lint nenašiel podporované problémy. Neznamená server compatibility.

Render do súboru:

```bash
helm template atlas-api . \
  --namespace atlas-api-prod \
  -f values-prod.yaml \
  --debug > /tmp/atlas-api-rendered.yaml
```

Potom klientská Kubernetes validácia:

```bash
kubectl apply --dry-run=client -f /tmp/atlas-api-rendered.yaml
```

Klientský dry-run overí lokálne parse/schema schopnosti `kubectl`, ale neaktivuje aktuálne admission webhooks ani authorization target clusteru.

Server-side dry-run:

```bash
kubectl --context atlas-prod-eu1 \
  --namespace atlas-api-prod \
  apply --server-side --dry-run=server \
  -f /tmp/atlas-api-rendered.yaml
```

Tento príkaz kontaktuje API server, vykoná authorization, current API validation a admission bez perzistentnej mutation. Stále neoverí rollout, image pull, CNI ani application behavior.

Pre chart používajúci `lookup` je relevantný aj server render:

```bash
helm upgrade atlas-api-prod . \
  --install \
  --namespace atlas-api-prod \
  --create-namespace \
  -f values-prod.yaml \
  --dry-run=server \
  --debug
```

Lokálny `helm template` môže pri `lookup` vrátiť iný výsledok než server dry-run. Preto dynamic templates zvyšujú testovaciu a reprodukčnú náročnosť.

## 12. Inštalácia alebo upgrade

Najprv zobraz plánovaný diff cez render a live manifest. Bez Helm diff pluginu možno použiť:

```bash
helm get manifest atlas-api-prod -n atlas-api-prod > /tmp/current.yaml
helm template atlas-api-prod . -n atlas-api-prod -f values-prod.yaml > /tmp/desired.yaml
diff -u /tmp/current.yaml /tmp/desired.yaml || true
```

Raw diff obsahuje aj formatting alebo generated metadata rozdiely, takže ho treba interpretovať. Dôležité sú zmeny image digestu, Pod template, Service selectoru, RBAC, storage a hooks.

Upgrade pre pinned Helm 4 toolchain:

```bash
helm upgrade atlas-api-prod . \
  --install \
  --namespace atlas-api-prod \
  --create-namespace \
  -f values-prod.yaml \
  --wait \
  --rollback-on-failure \
  --timeout 5m
```

Pri Helm 3 sa podobný automatický rollback typicky zapína `--atomic`; presný command musí zodpovedať pinned major verzii. `--wait` čaká na vybrané Kubernetes readiness conditions. Nečaká na ľubovoľný business outcome. `--rollback-on-failure` alebo `--atomic` tiež nevrátia external side effects hooku či aplikácie.

Po upgrade zachovaj revision identity:

```bash
helm history atlas-api-prod -n atlas-api-prod
helm status atlas-api-prod -n atlas-api-prod --show-resources
helm get values atlas-api-prod -n atlas-api-prod --all
helm get manifest atlas-api-prod -n atlas-api-prod
helm get hooks atlas-api-prod -n atlas-api-prod
```

Tieto príkazy odpovedajú na odlišné otázky. `history` ukazuje release revisions. `get values --all` ukazuje computed values uložené pre release. `get manifest` ukazuje Helm-rendered manifest, nie nutne admission-mutated live object. `get hooks` izoluje hook resources.

## 13. Runtime overenie

Skontroluj rollout a artifact:

```bash
kubectl -n atlas-api-prod rollout status deploy/atlas-api-prod-atlas-api --timeout=3m
kubectl -n atlas-api-prod get rs,pod -l app.kubernetes.io/instance=atlas-api-prod -o wide
kubectl -n atlas-api-prod get pods \
  -l app.kubernetes.io/instance=atlas-api-prod \
  -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[0].image}{"\n"}{end}'
```

Každý serving Pod musí používať approved digest. Potom over checksum/config annotation a loaded environment:

```bash
kubectl -n atlas-api-prod get deploy atlas-api-prod-atlas-api \
  -o jsonpath='{.spec.template.metadata.annotations.checksum/config}{"\n"}'

POD=$(kubectl -n atlas-api-prod get pod \
  -l app.kubernetes.io/instance=atlas-api-prod \
  -o jsonpath='{.items[0].metadata.name}')

kubectl -n atlas-api-prod exec "$POD" -- printenv LOG_LEVEL LEGACY_AUTHORIZER_ENABLED
```

`printenv` je už process-container observation, nie iba ConfigMap read-back. Pri aplikácii, ktorá configuration načíta a transformuje interne, je ešte lepší bezpečný diagnostic endpoint alebo structured startup log s configuration generation.

Spusť Helm test:

```bash
helm test atlas-api-prod -n atlas-api-prod --logs
```

A nakoniec business canary podľa reálnej aplikácie. Pre náš demo workload môže ísť o port-forward a HTTP request:

```bash
kubectl -n atlas-api-prod port-forward svc/atlas-api-prod-atlas-api 18080:80
curl --fail --show-error http://127.0.0.1:18080/readyz
```

Port-forward obchádza external ingress a časť production network pathu. Je vhodný na izoláciu Service/application boundary, nie na potvrdenie celého user journey.

## 14. Úmyselne chybný boolean template a jeho dôkaz

Zmeň dočasne ConfigMap template na chybný výraz:

```gotemplate
LEGACY_AUTHORIZER_ENABLED: {{ .Values.config.legacyAuthorizerEnabled | default true | quote }}
```

Potom renderuj s explicitným `false`:

```bash
helm template atlas-api . \
  --show-only templates/configmap.yaml \
  --set config.legacyAuthorizerEnabled=false
```

Výstup bude obsahovať `"true"`. Helm ani Kubernetes v tomto bode nerobia chybu. Template program dostal boolean `false`, Sprig `default` ho vyhodnotil ako empty a vybral fallback. Tento experiment presne ukazuje, prečo schema test a lint nestačia. Potrebuješ semantic fixture pre dôležité values.

Vráť bezpečný `ternary` alebo priamy boolean render a test zopakuj. Druhý render musí vrátiť `"false"`.

## 15. Rollback, unknown outcome a read-back

Zisti revisions:

```bash
helm history atlas-api-prod -n atlas-api-prod
```

Rollback na revision 3:

```bash
helm rollback atlas-api-prod 3 \
  --namespace atlas-api-prod \
  --wait \
  --timeout 5m
```

Rollback vytvorí novú Helm revision. Nevymaže historickú revision 4. Nevráti automaticky schema migration, provider request ani event, ktorý už nový release vytvoril.

Ak upgrade skončí timeoutom, nepredpokladaj, že sa nič nezmenilo. Najprv vykonaj read-back:

```bash
helm history atlas-api-prod -n atlas-api-prod
helm status atlas-api-prod -n atlas-api-prod
helm get manifest atlas-api-prod -n atlas-api-prod
kubectl -n atlas-api-prod get deploy,rs,pod,job -o wide
kubectl -n atlas-api-prod get events --sort-by=.lastTimestamp | tail -40
```

Potom identifikuj, či hook commitol operation, či vznikla nová revision, ktoré ReplicaSets existujú a ktorá cohorta prijíma traffic. Až potom rozhodni retry, rollback alebo roll-forward.

## 16. Dependency lock — `update` a `build` nie sú rovnaké

Ak chart používa dependency, `Chart.yaml` môže obsahovať:

```yaml
dependencies:
  - name: common
    version: "1.6.3"
    repository: "oci://ghcr.io/example/charts"
```

Pri authoring update:

```bash
helm dependency update .
```

Helm resolve-ne dependency podľa `Chart.yaml`, stiahne chart do `charts/` a vytvorí alebo zmení `Chart.lock`. Toto je dependency-selection operácia.

V reproducible CI:

```bash
helm dependency build .
```

`build` obnoví `charts/` podľa existujúceho locku. CI má následne overiť, že Git working tree alebo packaged digest sa nezmenili nečakaným resolve-om:

```bash
helm dependency build .
git diff --exit-code -- Chart.lock charts/
```

Ak lock chýba, `dependency build` môže podľa Helm behavioru prejsť do resolution podobného update-u. Preto absence locku musí byť samostatný gate, nie tichý fallback.

## 17. Minimálny CI script

```bash
#!/usr/bin/env bash
set -euo pipefail

chart_dir="atlas-api"
release="atlas-api-prod"
namespace="atlas-api-prod"
values_file="values-prod.yaml"
rendered="$(mktemp)"
trap 'rm -f "$rendered"' EXIT

helm version
helm dependency build "$chart_dir"
git diff --exit-code -- "$chart_dir/Chart.lock" "$chart_dir/charts"

helm lint "$chart_dir" -f "$values_file"

helm template "$release" "$chart_dir" \
  --namespace "$namespace" \
  -f "$values_file" \
  > "$rendered"

kubectl apply --dry-run=client -f "$rendered"

kubectl --context atlas-prod-eu1 \
  --namespace "$namespace" \
  apply --server-side --dry-run=server \
  -f "$rendered"

grep -q 'LEGACY_AUTHORIZER_ENABLED: "false"' "$rendered"
! grep -Eq 'image: .*:[[:alnum:]_.-]+$' "$rendered"
```

Posledné dva riadky sú jednoduché semantic gates. Prvý chráni explicitné `false`. Druhý sa pokúša odmietnuť tag-only image references. V produkčnom pipeline je vhodnejšie parsovať YAML structured nástrojom a kontrolovať konkrétne workload fields, pretože grep môže mať false positives aj false negatives.

## 18. Čo tento walkthrough preukazuje

Kompletný release dôkaz vyzerá takto:

```text
Chart.yaml + locked dependencies + ordered values
→ schema verdict
→ exact rendered manifest
→ server dry-run a admission verdict
→ Helm revision
→ live object generation
→ ReplicaSet a Pod artifact/config generation
→ Service endpoints
→ technical test
→ business canary
→ forbidden legacy path test
```

Žiadny jednotlivý príkaz túto reťaz nepreukazuje. `helm lint` nevie nič o target admission. `helm template` nevie nič o runtime. `kubectl rollout status` nevie nič o business correctness. `helm test` testuje iba to, čo test Pod skutočne vykoná. Učenie Helm preto znamená vedieť, ktorú hranicu každý súbor a príkaz reprezentuje, nie iba zapamätať syntax.

## Kontrolné úlohy

1. Zmeň `legacyAuthorizerEnabled` na string a vysvetli, ktorý gate zlyhá ako prvý.
2. Odstráň `checksum/config`, zmeň ConfigMap a pozoruj rozdiel medzi live ConfigMapou a process-loaded environmentom.
3. Zmeň Service selector tak, aby nematchoval Pody, a porovnaj Service, EndpointSlice a direct PodIP test.
4. Nastav chybný image digest a lokalizuj failure od Helm revision cez Pod Events po `ImagePullBackOff`.
5. Spusť schema hook dvakrát s rovnakým `operationId` a over, že druhý attempt je bezpečný no-op.
6. Vykonaj upgrade, ktorý timeoutne počas hooku, a rozhodni ďalší krok iba z read-back evidence.
7. Porovnaj `helm dependency update` a `helm dependency build` na chýbajúcom a existujúcom `Chart.lock`.
8. Vytvor semantic CI test, ktorý odmietne mutable image tag aj explicitné `false` zmenené na `true`.

## Oficiálna dokumentácia

- [Chart Template Guide](https://helm.sh/docs/chart_template_guide/)
- [Charts](https://helm.sh/docs/topics/charts/)
- [Values Files](https://helm.sh/docs/chart_template_guide/values_files/)
- [Template Functions and Pipelines](https://helm.sh/docs/chart_template_guide/functions_and_pipelines/)
- [Named Templates](https://helm.sh/docs/chart_template_guide/named_templates/)
- [Debugging Templates](https://helm.sh/docs/chart_template_guide/debugging/)
- [Helm dependency commands](https://helm.sh/docs/helm/helm_dependency/)
- [helm upgrade](https://helm.sh/docs/helm/helm_upgrade/)
- [helm rollback](https://helm.sh/docs/helm/helm_rollback/)
- [helm test](https://helm.sh/docs/helm/helm_test/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: CKA troubleshooting drills](cka-troubleshooting-drills.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: IaaS, PaaS a SaaS →](../11-cloud-and-aws/iaas-paas-saas.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
