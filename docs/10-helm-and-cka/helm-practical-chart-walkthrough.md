# Praktický Helm chart od zdroja po release

Táto kapitola vytvorí malý, ale kompletný chart `demo-api` a pri každom kroku vysvetlí, čo príkaz alebo manifest dokazuje a čo ešte nedokazuje.

## Štruktúra

```text
demo-api/
├── Chart.yaml
├── values.yaml
└── templates/
    ├── _helpers.tpl
    ├── deployment.yaml
    ├── service.yaml
    └── tests/smoke-test.yaml
```

```bash
helm create demo-api
```

Príkaz vytvorí skeleton. Neoveruje render ani Kubernetes kompatibilitu.

## Chart.yaml

```yaml
apiVersion: v2
name: demo-api
description: Example HTTP API chart
type: application
version: 0.1.0
appVersion: "1.4.0"
kubeVersion: ">=1.30.0-0"
```

`version` je verzia chartu. `appVersion` je informačná verzia aplikácie; Helm ju nepoužije ako image tag automaticky. Release revision vznikne až pri install alebo upgrade.

## values.yaml

```yaml
replicaCount: 2

image:
  repository: ghcr.io/example/demo-api
  tag: "1.4.0"
  digest: ""
  pullPolicy: IfNotPresent

service:
  port: 80
  targetPort: 8080

config:
  logLevel: info

resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

Values sú vstupom renderu, nie live stavom. Zmena súboru v Gite nemení existujúci release, kým neprebehne nový upgrade.

## Helpery

```gotemplate
{{- define "demo-api.fullname" -}}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end }}

{{- define "demo-api.selectorLabels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "demo-api.image" -}}
{{- if .Values.image.digest -}}
{{ printf "%s@%s" .Values.image.repository .Values.image.digest }}
{{- else -}}
{{ printf "%s:%s" .Values.image.repository .Values.image.tag }}
{{- end -}}
{{- end }}
```

Image helper centralizuje rozhodnutie tag verzus digest. Bez neho môže Deployment a Job použiť inú image generation.

## Deployment

```gotemplate
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "demo-api.fullname" . }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "demo-api.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "demo-api.selectorLabels" . | nindent 8 }}
    spec:
      containers:
        - name: api
          image: {{ include "demo-api.image" . | quote }}
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: {{ .Values.service.targetPort }}
          readinessProbe:
            httpGet:
              path: /readyz
              port: http
          livenessProbe:
            httpGet:
              path: /livez
              port: http
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
```

`include` vloží helper output. `nindent` pridá nový riadok a odsadenie. `toYaml` serializuje mapu z values. Readiness rozhoduje o prijímaní trafficu; liveness o reštarte containeru. Ani jedna probe nedokazuje business correctness.

## Service

```gotemplate
apiVersion: v1
kind: Service
metadata:
  name: {{ include "demo-api.fullname" . }}
spec:
  selector:
    {{- include "demo-api.selectorLabels" . | nindent 4 }}
  ports:
    - name: http
      port: {{ .Values.service.port }}
      targetPort: {{ .Values.service.targetPort }}
```

Service existence nedokazuje, že má endpoints. Selector musí presne zodpovedať Pod labels.

## Render a validácia

```bash
helm lint ./demo-api
helm template demo ./demo-api --namespace demo --debug > rendered.yaml
```

`helm lint` zachytí časť chart a template chýb. `helm template` ukáže manifest pre konkrétne values a Helm toolchain. Ani jeden príkaz nezapája API server alebo admission webhooks.

Server-side dry run:

```bash
kubectl apply --dry-run=server --namespace demo -f rendered.yaml
```

Tento krok overuje Kubernetes API, schema, authorization a admission pre daný cluster. Nevytvorí controllers ani runtime procesy.

## Install

```bash
helm upgrade --install demo ./demo-api \
  --namespace demo \
  --create-namespace \
  --atomic \
  --wait \
  --timeout 5m
```

`--wait` čaká na vybrané readiness podmienky. `--atomic` pri zlyhaní vykoná rollback alebo cleanup podľa typu operácie. Úspešný exit code stále nepreukazuje funkčnosť celej používateľskej cesty.

## Read-back a runtime overenie

```bash
helm status demo -n demo
helm history demo -n demo
helm get values demo -n demo --all
helm get manifest demo -n demo > release-manifest.yaml
kubectl rollout status deployment/demo-demo-api -n demo
kubectl get pods,endpointslices -n demo
```

`helm get manifest` ukazuje manifest uložený v release recorde. Live objekt mohol byť manuálne zmenený, preto treba porovnať aj `kubectl get ... -o yaml`.

Runtime request:

```bash
kubectl run curl-check \
  --rm -i --restart=Never \
  --namespace demo \
  --image=curlimages/curl:8.12.1 \
  -- http://demo-demo-api/readyz
```

Tento test overí Pod DNS, Service routing, endpoint a HTTP readiness. Neoverí external ingress, autentizáciu ani doménovú operáciu.

## Upgrade a rollback

Pred upgrade-om porovnaj nový render:

```bash
helm get manifest demo -n demo > current.yaml
helm template demo ./demo-api -n demo > candidate.yaml
diff -u current.yaml candidate.yaml
```

Upgrade:

```bash
helm upgrade demo ./demo-api -n demo --atomic --wait --timeout 5m
```

Rollback:

```bash
helm history demo -n demo
helm rollback demo 1 -n demo --wait --timeout 5m
```

Rollback vytvorí novú Helm revision s predchádzajúcim manifestom. Nevracia databázové migrácie, queue events ani external side effects.

## Troubleshooting

Render jednej šablóny:

```bash
helm template demo ./demo-api \
  --namespace demo \
  --show-only templates/deployment.yaml \
  --debug
```

Release a Kubernetes evidence:

```bash
helm status demo -n demo
kubectl get events -n demo --sort-by=.lastTimestamp
kubectl describe deployment demo-demo-api -n demo
kubectl get pods -n demo -o wide
kubectl logs -n demo deployment/demo-demo-api --all-containers
```

Postup ide od renderu cez release verdict, API/controller stav, Pod startup a až potom application behavior. `helm status=failed` samo neurčuje failure boundary.

## Acceptance

Chart je pripravený až keď lint a render prejdú, server-side dry run akceptuje manifest, install vytvorí správnu revision, Pods sú ready, Service má endpoints, runtime request funguje a rollback eligibility je vyhodnotená aj pre durable side effects.
