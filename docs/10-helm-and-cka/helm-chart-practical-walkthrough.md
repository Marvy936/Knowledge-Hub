# Praktický Helm chart od prázdneho adresára po overený release

Táto kapitola materializuje pojmy z kapitoly [Helm chart, template, values a release](helm-chart-template-values-release.md) do malého, ale reálneho chartu. Cieľom nie je iba skopírovať YAML. Pri každom súbore a príkaze vysvetľuje, aký vstup vytvára, čo Helm vyrenderuje, čo následne prijme Kubernetes a čo daný zelený výsledok ešte nedokazuje.

Budeme nasadzovať HTTP aplikáciu `payments-api` ako Deployment a Service. Chart bude podporovať immutable image digest, resources, probes, environment configuration a voliteľný ServiceAccount. Použijeme release `payments-dev` v namespace `payments-dev`.

## 1. Vytvorenie adresárovej štruktúry

Najprv vytvor pracovný adresár:

```bash
mkdir -p atlas-payments/templates
cd atlas-payments
```

Výsledná štruktúra bude:

```text
atlas-payments/
├── Chart.yaml
├── values.yaml
├── values.schema.json
└── templates/
    ├── _helpers.tpl
    ├── deployment.yaml
    ├── service.yaml
    ├── serviceaccount.yaml
    └── tests/
        └── test-connection.yaml
```

Chart source v tomto adresári ešte nie je release. Je to authoring input. Release vznikne až kombináciou chartu, effective values, release name, namespace, Helm verzie a capabilities cieľového clusteru.

## 2. `Chart.yaml`: identita balíka

Vytvor `Chart.yaml`:

```yaml
apiVersion: v2
name: atlas-payments
description: Helm chart pre ukážkovú payments API
type: application
version: 0.1.0
appVersion: "1.4.2"
kubeVersion: ">=1.30.0-0"
```

`version` je verzia chart package-u. Mení sa pri zmene templates, values contractu alebo chart metadata. `appVersion` je iba informačný údaj; Helm podľa neho automaticky nezmení image. Skutočný artifact určíme vo values cez repository a digest.

Over syntax a základnú štruktúru:

```bash
helm lint .
```

Očakávaný výsledok je približne:

```text
==> Linting .
1 chart(s) linted, 0 chart(s) failed
```

Tento výsledok dokazuje, že Helm vedel chart načítať a nenašiel vybrané statické problémy. Nedokazuje, že templates vytvoria validné objekty pre cieľový cluster, že image existuje ani že aplikácia bude pripravená.

## 3. `values.yaml`: configuration API chartu

Vytvor `values.yaml`:

```yaml
replicaCount: 2

image:
  repository: ghcr.io/example/atlas-payments
  digest: sha256:1111111111111111111111111111111111111111111111111111111111111111
  pullPolicy: IfNotPresent

serviceAccount:
  create: true
  name: ""

service:
  type: ClusterIP
  port: 80
  targetPort: 8080

containerPort: 8080

config:
  logLevel: info
  legacyAuthorizerEnabled: false

resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 256Mi

probes:
  readiness:
    path: /readyz
    initialDelaySeconds: 3
    periodSeconds: 5
  liveness:
    path: /healthz
    initialDelaySeconds: 10
    periodSeconds: 10
```

Tu je dôležité, že `legacyAuthorizerEnabled: false` je platná explicitná hodnota. Template ju nesmie zameniť za „hodnota chýba“. Preto neskôr nepoužijeme výraz `default true`, ktorý považuje boolean `false` za empty.

Image je viazaný digestom. Tag ako `1.4.2` môže registry presmerovať na iné bytes; digest identifikuje konkrétny image manifest.

## 4. `values.schema.json`: typy a povinné hodnoty

Vytvor `values.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["replicaCount", "image", "service", "config"],
  "properties": {
    "replicaCount": {
      "type": "integer",
      "minimum": 1,
      "maximum": 20
    },
    "image": {
      "type": "object",
      "required": ["repository", "digest", "pullPolicy"],
      "properties": {
        "repository": {"type": "string", "minLength": 1},
        "digest": {
          "type": "string",
          "pattern": "^sha256:[a-f0-9]{64}$"
        },
        "pullPolicy": {
          "type": "string",
          "enum": ["Always", "IfNotPresent", "Never"]
        }
      },
      "additionalProperties": false
    },
    "config": {
      "type": "object",
      "required": ["logLevel", "legacyAuthorizerEnabled"],
      "properties": {
        "logLevel": {
          "type": "string",
          "enum": ["debug", "info", "warn", "error"]
        },
        "legacyAuthorizerEnabled": {"type": "boolean"}
      },
      "additionalProperties": false
    }
  }
}
```

Skús zámerne chybnú hodnotu:

```bash
helm template payments-dev . \
  --namespace payments-dev \
  --set replicaCount=0
```

Helm má render odmietnuť ešte pred vytvorením manifestu, pretože schema vyžaduje minimálne jednu repliku. Schema zachytí typ, rozsah a formát. Nezachytí však každý významový vzťah, napríklad či `service.targetPort` zodpovedá skutočne otvorenému portu procesu.

## 5. `_helpers.tpl`: stabilné názvy a labels

Vytvor `templates/_helpers.tpl`:

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

{{- define "atlas-payments.labels" -}}
app.kubernetes.io/name: {{ include "atlas-payments.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" }}
{{- end -}}

{{- define "atlas-payments.selectorLabels" -}}
app.kubernetes.io/name: {{ include "atlas-payments.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "atlas-payments.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
{{- default (include "atlas-payments.fullname" .) .Values.serviceAccount.name -}}
{{- else -}}
{{- required "serviceAccount.name je povinné, keď serviceAccount.create=false" .Values.serviceAccount.name -}}
{{- end -}}
{{- end -}}
```

Selector labels musia byť stabilné počas upgrade-u. Ak helper pridá do selectora chart version alebo image digest, nový Deployment môže naraziť na immutable selector alebo Service prestane vyberať starú a novú cohortu podľa očakávania.

`required` zabezpečí, že chart nevyrenderuje prázdne meno existujúceho ServiceAccountu. Je to render-time guard, nie Kubernetes authorization test.

## 6. `serviceaccount.yaml`

Vytvor `templates/serviceaccount.yaml`:

```gotemplate
{{- if .Values.serviceAccount.create }}
apiVersion: v1
kind: ServiceAccount
metadata:
  name: {{ include "atlas-payments.serviceAccountName" . }}
  labels:
    {{- include "atlas-payments.labels" . | nindent 4 }}
{{- end }}
```

`nindent 4` najprv vloží nový riadok a potom odsadenie. Bez správneho odsadenia môže výsledok zostať textovo platný template, ale neplatný YAML.

## 7. `deployment.yaml`: hlavný runtime contract

Vytvor `templates/deployment.yaml`:

```gotemplate
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "atlas-payments.fullname" . }}
  labels:
    {{- include "atlas-payments.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "atlas-payments.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "atlas-payments.selectorLabels" . | nindent 8 }}
      annotations:
        atlas.example/config-generation: {{ printf "%s:%v" .Values.config.logLevel .Values.config.legacyAuthorizerEnabled | sha256sum }}
    spec:
      serviceAccountName: {{ include "atlas-payments.serviceAccountName" . }}
      containers:
        - name: payments-api
          image: "{{ .Values.image.repository }}@{{ .Values.image.digest }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: {{ .Values.containerPort }}
          env:
            - name: LOG_LEVEL
              value: {{ .Values.config.logLevel | quote }}
            - name: LEGACY_AUTHORIZER_ENABLED
              value: {{ ternary "true" "false" .Values.config.legacyAuthorizerEnabled | quote }}
          readinessProbe:
            httpGet:
              path: {{ .Values.probes.readiness.path }}
              port: http
            initialDelaySeconds: {{ .Values.probes.readiness.initialDelaySeconds }}
            periodSeconds: {{ .Values.probes.readiness.periodSeconds }}
          livenessProbe:
            httpGet:
              path: {{ .Values.probes.liveness.path }}
              port: http
            initialDelaySeconds: {{ .Values.probes.liveness.initialDelaySeconds }}
            periodSeconds: {{ .Values.probes.liveness.periodSeconds }}
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
```

Výraz `ternary "true" "false" ...` zachová explicitné `false`. Toto je bezpečnejšie než:

```gotemplate
{{ .Values.config.legacyAuthorizerEnabled | default true }}
```

`default true` by pre boolean `false` vrátil `true`. To je presne typ chyby, pri ktorej Helm aj Kubernetes úspešne vykonajú nesprávny manifest.

Annotation s hashom configuration inputs zmení Pod template pri zmene konfigurácie. Controller preto vytvorí nový ReplicaSet. Hash však nie je dôkaz, že proces hodnotu naozaj použil; to musí overiť runtime telemetry alebo business test.

## 8. `service.yaml`: stabilný network endpoint

Vytvor `templates/service.yaml`:

```gotemplate
apiVersion: v1
kind: Service
metadata:
  name: {{ include "atlas-payments.fullname" . }}
  labels:
    {{- include "atlas-payments.labels" . | nindent 4 }}
spec:
  type: {{ .Values.service.type }}
  selector:
    {{- include "atlas-payments.selectorLabels" . | nindent 4 }}
  ports:
    - name: http
      port: {{ .Values.service.port }}
      targetPort: {{ .Values.service.targetPort }}
      protocol: TCP
```

Service selector musí byť identický s Pod selector labels. `targetPort: 8080` môže byť číslo alebo pomenovaný port. V produkčnom charte je často bezpečnejšie použiť meno `http`, aby Service nebola naviazaná na duplikované číslo vo values.

## 9. Render a vysvetlenie výsledku

Vyrenderuj chart bez mutácie clusteru:

```bash
helm template payments-dev . \
  --namespace payments-dev \
  --debug \
  > /tmp/payments-rendered.yaml
```

Skontroluj konkrétne časti:

```bash
grep -nE '^(kind:|  name:|          image:|            - name: LEGACY|              value:)' \
  /tmp/payments-rendered.yaml
```

Over, že explicitné `false` zostalo zachované:

```bash
yq 'select(.kind == "Deployment")
  | .spec.template.spec.containers[0].env[]
  | select(.name == "LEGACY_AUTHORIZER_ENABLED")
  | .value' /tmp/payments-rendered.yaml
```

Očakávaný výstup:

```text
false
```

`helm template` dokazuje úspešný lokálny render pre zadané capabilities. Neoveruje serverové defaulting, admission policies, RBAC, immutable-field konflikt ani existenciu image-u.

## 10. Server-side dry-run

Najprv vytvor namespace:

```bash
kubectl create namespace payments-dev \
  --dry-run=client -o yaml | kubectl apply -f -
```

Potom pošli vyrenderované objekty na serverovú validáciu bez uloženia:

```bash
kubectl apply \
  --server-side \
  --dry-run=server \
  -f /tmp/payments-rendered.yaml
```

Tento krok testuje API discovery, schema a admission v aktuálnom clusteri s identity používateľa, ktorý príkaz vykonal. Stále však nespustí controller rollout ani application proces.

## 11. Inštalácia release-u

Nainštaluj release:

```bash
helm upgrade --install payments-dev . \
  --namespace payments-dev \
  --create-namespace \
  --atomic \
  --wait \
  --timeout 5m \
  --history-max 10
```

Význam flags:

- `--install` vytvorí release, ak ešte neexistuje;
- `--atomic` pri zlyhaní upgrade-u požiada Helm o rollback a automaticky zapína čakanie;
- `--wait` čaká na vybrané Kubernetes readiness conditions;
- `--timeout` ohraničí čakanie, nie celý business recovery čas;
- `--history-max` obmedzí počet uložených revisions.

Po úspechu načítaj Helm evidence:

```bash
helm status payments-dev -n payments-dev
helm history payments-dev -n payments-dev
helm get values payments-dev -n payments-dev --all
helm get manifest payments-dev -n payments-dev > /tmp/release-manifest.yaml
```

Potom Kubernetes evidence:

```bash
kubectl get deployment,replicaset,pod,service,endpointslice \
  -n payments-dev \
  -o wide

kubectl rollout status deployment/payments-dev-atlas-payments \
  -n payments-dev \
  --timeout=2m
```

Helm `STATUS: deployed` a úspešný rollout dokazujú iba release a controller boundaries. Ešte treba overiť serving path.

## 12. Runtime test cez Service

Spusť dočasný testovací Pod:

```bash
kubectl run curl \
  -n payments-dev \
  --rm -i --restart=Never \
  --image=curlimages/curl:8.10.1 \
  -- curl -fsS http://payments-dev-atlas-payments/readyz
```

Očakávaný response je application-specific, napríklad:

```json
{"status":"ready"}
```

Tento test dokazuje DNS, Service selector, EndpointSlice, Pod network path, listener a readiness endpoint. Nedokazuje ešte autorizáciu platby, idempotenciu ani správne spracovanie konfigurácie.

Over configuration generation v active Podoch:

```bash
kubectl get pods -n payments-dev \
  -l app.kubernetes.io/instance=payments-dev \
  -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.metadata.annotations.atlas\.example/config-generation}{"\n"}{end}'
```

Všetky active Pody majú niesť rovnaký hash. Potom aplikácia potrebuje bezpečnú telemetry, ktorá uvedie loaded configuration generation bez logovania secrets.

## 13. Upgrade s vlastným values súborom

Vytvor `values-dev.yaml`:

```yaml
replicaCount: 3
config:
  logLevel: debug
  legacyAuthorizerEnabled: false
```

Najprv zobraz diff, ak máš plugin nainštalovaný:

```bash
helm diff upgrade payments-dev . \
  -n payments-dev \
  -f values-dev.yaml
```

Bez pluginu môžeš porovnať render manuálne:

```bash
helm template payments-dev . \
  -n payments-dev \
  -f values-dev.yaml \
  > /tmp/payments-next.yaml

diff -u /tmp/release-manifest.yaml /tmp/payments-next.yaml
```

Potom vykonaj upgrade:

```bash
helm upgrade payments-dev . \
  -n payments-dev \
  -f values-dev.yaml \
  --atomic \
  --wait \
  --timeout 5m
```

Over, že vznikla nová Helm revision a nový ReplicaSet:

```bash
helm history payments-dev -n payments-dev
kubectl get rs,pods -n payments-dev \
  -l app.kubernetes.io/instance=payments-dev \
  --sort-by=.metadata.creationTimestamp
```

Zmena `replicaCount` mení Deployment desired count. Zmena configuration hash annotation mení Pod template a vytvorí nový ReplicaSet. Samotná zmena `values-dev.yaml` bez prepojenia do Pod template by nemusela Pody nahradiť.

## 14. Diagnostika neúspešného release-u

Pri timeout-e alebo non-zero výsledku nezačni okamžite rovnakým `helm upgrade`. Najprv zachovaj unknown-outcome evidence:

```bash
helm status payments-dev -n payments-dev
helm history payments-dev -n payments-dev
helm get manifest payments-dev -n payments-dev > /tmp/failed-release.yaml

kubectl get events -n payments-dev \
  --sort-by=.metadata.creationTimestamp

kubectl get pods -n payments-dev -o wide
kubectl describe deployment payments-dev-atlas-payments -n payments-dev
kubectl describe pods -n payments-dev \
  -l app.kubernetes.io/instance=payments-dev
```

Pre jednotlivé Pody:

```bash
kubectl logs -n payments-dev POD_NAME -c payments-api
kubectl logs -n payments-dev POD_NAME -c payments-api --previous
```

`ImagePullBackOff` smeruje vyšetrovanie na image reference, registry authorization, network a architecture. `CrashLoopBackOff` znamená, že container sa spustil a opakovane skončil; treba analyzovať exit code, logs, command, configuration a dependencies. `Pending` bez vytvoreného containeru smeruje skôr na scheduler, resources, taints, PVC alebo quota.

## 15. Bezpečný rollback a jeho hranice

Zobraz históriu:

```bash
helm history payments-dev -n payments-dev
```

Rollback na revision 1:

```bash
helm rollback payments-dev 1 \
  -n payments-dev \
  --wait \
  --timeout 5m
```

Rollback vytvorí ďalšiu Helm revision. Obnoví starší chart/config/manifest intent, ale nevráti database migráciu, externý provider side effect, zmenený secret ani eventy už publikované novou verziou. Pred rollbackom preto treba preukázať compatibility starého workloadu s aktuálnym durable state-om.

Po rollbacku opakuj rollout, Service a business validáciu. Nestačí iba `helm status`.

## 16. Chart test

Vytvor adresár a `templates/tests/test-connection.yaml`:

```gotemplate
apiVersion: v1
kind: Pod
metadata:
  name: "{{ include "atlas-payments.fullname" . }}-test-connection"
  labels:
    {{- include "atlas-payments.labels" . | nindent 4 }}
  annotations:
    "helm.sh/hook": test
spec:
  restartPolicy: Never
  containers:
    - name: curl
      image: curlimages/curl:8.10.1
      command:
        - sh
        - -ec
        - |
          curl -fsS "http://{{ include "atlas-payments.fullname" . }}:{{ .Values.service.port }}/readyz"
```

Spusť test:

```bash
helm test payments-dev -n payments-dev --logs
```

Test overí connection z test Podu na Service a readiness endpoint. Nie je automaticky business E2E testom. Pre payments workload by samostatný bezpečný canary musel overiť autorizáciu, idempotency a forbidden legacy path bez reálneho finančného side effectu.

## 17. Package a immutable promotion

Pred publikovaním obnov dependencies a skontroluj lock:

```bash
helm dependency update .
helm dependency build .
helm lint .
```

Zabaľ chart:

```bash
helm package . --destination dist/
sha256sum dist/atlas-payments-0.1.0.tgz
```

OCI publikácia:

```bash
helm push dist/atlas-payments-0.1.0.tgz \
  oci://registry.example.com/helm
```

Production promotion má používať rovnaký packaged digest, ktorý prešiel testami. Rebuild rovnakého source-u neskôr môže načítať iné dependencies alebo toolchain a nie je automaticky rovnakým artifactom.

## 18. Cleanup a decommission

Odstráň release:

```bash
helm uninstall payments-dev -n payments-dev
```

Skontroluj zvyšky:

```bash
kubectl get all,cm,secret,sa,pvc -n payments-dev
kubectl get crd | grep -i atlas || true
```

`helm uninstall` nemusí odstrániť CRDs, retained hook resources, PVC/PV, external load balancers, DNS records, IAM identities, secrets ani backupy. Decommission je uzavretý až po inventári a negative tests, že starý endpoint, writer a credentials už nie sú použiteľné.

## 19. Čo má čitateľ po cvičení vedieť vysvetliť

Po prejdení kapitoly má byť zrejmé, prečo chart version, image digest, effective values, rendered manifest, Helm revision, Deployment generation a serving Pod nie sú jedna identita. Čitateľ má vedieť ukázať, čo konkrétne dokazujú `helm lint`, `helm template`, server dry-run, `helm upgrade --wait`, `kubectl rollout status`, `helm test` a business canary. Zároveň má vedieť diagnostikovať rozdiel medzi render chybou, API/admission odmietnutím, scheduler problémom, image pull failure, process crashom, readiness problémom a nesprávnym business výsledkom.

## Oficiálna dokumentácia

- [Helm chart template guide](https://helm.sh/docs/chart_template_guide/)
- [Helm values files](https://helm.sh/docs/chart_template_guide/values_files/)
- [Helm template](https://helm.sh/docs/helm/helm_template/)
- [Helm upgrade](https://helm.sh/docs/helm/helm_upgrade/)
- [Helm test](https://helm.sh/docs/topics/chart_tests/)
- [Kubernetes Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Helm chart, template, values a release](helm-chart-template-values-release.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Template functions a pipelines →](template-functions-pipelines.md)
<!-- KNOWLEDGE-NAVIGATION:END -->