# Helm chart, template, values a release

Helm je package manager a templating/release tool pre Kubernetes. **Chart** je versionovaný balík Kubernetes templates a metadata. **Values** sú vstupy do renderovania. **Release** je konkrétna inštalovaná inštancia chartu v clustri s menom, namespace, revision history a effective configuration. Helm nevytvára nový workload controller; renderuje a aplikuje Kubernetes API objekty a uchováva release state.

## 1. Mentálny model

```text
chart artifact
+ values
+ release identity
+ cluster capabilities
        ↓ render
Kubernetes manifests
        ↓ install/upgrade
Kubernetes API objects
        ↓
Helm release revision
```

Rozlišuj:

- chart source a chart version,
- application version,
- values files,
- rendered manifest,
- live Kubernetes objects,
- Helm release metadata/history.

Tieto vrstvy sa môžu dostať do driftu.

## 2. Chart

Chart je directory alebo packaged archive s definovanou štruktúrou:

```text
example/
├── Chart.yaml
├── values.yaml
├── values.schema.json
├── charts/
├── crds/
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── _helpers.tpl
│   └── NOTES.txt
└── .helmignore
```

Nie každý file je povinný. Základ tvorí `Chart.yaml` a `templates/` podľa účelu chartu.

## 3. `Chart.yaml`

Typické metadata:

```yaml
apiVersion: v2
name: example
version: 1.4.0
appVersion: "2.8.1"
description: Example application
```

### Chart `version`

Verzia package contractu. Zmena templates, defaults, dependencies alebo metadata má vytvoriť novú chart verziu.

### `appVersion`

Informačná verzia aplikácie. Nie je automaticky image tag ani chart version.

Nezamieňaj:

```text
chart version ≠ application version ≠ release revision
```

## 4. Template

Files v `templates/` Helm spracuje cez Go template language, Helm functions a Sprig functions.

Príklad:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "example.fullname" . }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app.kubernetes.io/name: {{ include "example.name" . }}
  template:
    metadata:
      labels:
        app.kubernetes.io/name: {{ include "example.name" . }}
    spec:
      containers:
        - name: app
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
```

Template output musí byť validný Kubernetes manifest. Úspešné textové renderovanie ešte nepreukazuje API schema, admission ani runtime správnosť.

## 5. Built-in objects

V template sú dostupné napríklad:

- `.Values` — merged user/default values,
- `.Chart` — metadata z `Chart.yaml`,
- `.Release` — release name, namespace a operation context,
- `.Capabilities` — Kubernetes version a dostupné API versions,
- `.Files` — files zabalené v charte,
- `.Template` — current template metadata.

Príklad:

```yaml
metadata:
  labels:
    app.kubernetes.io/instance: {{ .Release.Name }}
    helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version }}
```

## 6. Values

Default values sú v:

```text
values.yaml
```

Príklad:

```yaml
replicaCount: 2

image:
  repository: registry.example.com/example
  tag: "2.8.1"
  pullPolicy: IfNotPresent

service:
  port: 8080
```

Templates pristupujú cez `.Values`.

Values sú public chart interface. Názvy, typy a defaults musia byť stabilné, dokumentované a validované.

## 7. Values precedence

Zjednodušene majú vyššiu prioritu neskoršie explicitné overrides:

1. chart `values.yaml`,
2. parent/dependency defaults podľa merge modelu,
3. files cez `-f`/`--values` v uvedenom poradí,
4. command-line overrides ako `--set`, `--set-string`, `--set-file`.

Príklad:

```bash
helm upgrade --install example ./chart \
  -f values-production.yaml \
  -f values-production-eu.yaml \
  --set image.tag=2.8.2
```

Effective values nie sú iba jeden file. Pred release ich renderuj a archivuj bez secretov.

## 8. Value typing

YAML implicit typing môže zmeniť význam:

```yaml
port: 8080
version: "1.0"
enabled: true
```

Command-line `--set` má vlastné parsing semantics. Pre hodnoty, ktoré musia zostať string, používaj vhodnú quoting/`--set-string` stratégiu.

Komplexné structures preferuj v versionovanom values file namiesto dlhého `--set` commandu.

## 9. Values schema

`values.schema.json` môže validovať values pred render/install/upgrade.

Môže definovať:

- required fields,
- types,
- enums,
- ranges,
- object structure,
- patterns.

Schema znižuje tiché chyby, ale nenahrádza semantic a Kubernetes runtime testy.

## 10. Release

Release je konkrétne nasadenie chartu:

```bash
helm install payments ./payments-chart \
  --namespace production \
  --create-namespace
```

Tu:

- `payments` je release name,
- chart môže byť použitý viackrát,
- namespace je súčasť release scope-u,
- prvá úspešná inštalácia vytvorí release revision.

Moderný Helm uchováva release information v Kubernetes, štandardne cez release Secrets podľa storage drivera/configurácie.

## 11. Release revision

Každý úspešný alebo zaznamenaný release lifecycle krok môže vytvoriť novú revision.

```bash
helm history payments -n production
helm status payments -n production
```

Revision nie je Deployment revision ani Git commit. Koreluj ich cez labels, annotations a release evidence.

## 12. Install

```bash
helm install payments oci://registry.example.com/charts/payments \
  --version 1.4.0 \
  -f values-production.yaml \
  --namespace production
```

Production install má pinovať:

- Helm major/minor podľa support policy,
- chart version alebo digest/provenance policy,
- image digests/tags podľa artifact modelu,
- values source revision,
- target cluster/context/namespace.

## 13. Upgrade

```bash
helm upgrade payments ./payments-chart \
  -f values-production.yaml \
  --namespace production
```

Upgrade môže zmeniť:

- chart version,
- values,
- rendered manifests,
- release revision.

Pred upgrade porovnaj:

```bash
helm template ...
helm diff ...       # plugin alebo external workflow
kubectl diff ...
```

Presné diff capabilities závisia od tooling-u. Helm core a plugins nepredstavujú rovnaký trust boundary.

## 14. `upgrade --install`

Idempotentnejší deployment entry point:

```bash
helm upgrade --install payments ./payments-chart \
  -f values-production.yaml \
  --namespace production \
  --create-namespace
```

Znižuje branch medzi first install a update, ale nerieši:

- concurrent releases,
- drift,
- failed hooks,
- immutable-field conflicts,
- schema migrations,
- secret management.

## 15. Renderovanie

```bash
helm template payments ./payments-chart \
  -f values-production.yaml \
  --namespace production
```

Local render umožňuje:

- review manifests,
- schema/lint checks,
- policy/security scanning,
- Git/CI artifact,
- test rôznych values.

Limit: local render nemusí presne reprodukovať cluster API discovery, lookup calls, admission defaulting alebo server-side validation bez vhodných flags/capabilities a live clusteru.

## 16. Lint a server validation

```bash
helm lint ./payments-chart -f values-production.yaml
helm template ... | kubectl apply --dry-run=server -f -
```

Vrstvy:

- Helm lint/template syntax,
- values schema,
- YAML/Kubernetes schema,
- API availability,
- admission policies/webhooks,
- runtime tests.

Jedna zelená vrstva nepreukazuje ďalšie.

## 17. Release state a Secrets

Release state môže obsahovať:

- chart metadata/content,
- effective configuration,
- rendered manifest,
- revision/status metadata.

Dôsledky:

- RBAC nad release Secrets je citlivé,
- values nesmú obsahovať plaintext secrets bez bezpečnostného modelu,
- namespace deletion môže odstrániť release history,
- external Git/source zostáva potrebný pre disaster recovery,
- release storage nie je backup application dát.

## 18. Secrets

Helm values nie sú secret manager.

Riziká:

- values v Git-e,
- CI logs a command history,
- rendered manifest,
- Helm release storage,
- `helm get values`/`helm get manifest`,
- Kubernetes Secrets bez encryption/RBAC.

Preferuj external secret integration, encrypted Git workflow alebo runtime identity podľa platformy. Do chart defaults nepatria reálne credentials.

## 19. Namespace a ownership

Release spravidla vlastní resources cez labels/annotations a release state, ale Kubernetes ownerReferences medzi release Secretom a všetkými resources nie sú univerzálny garbage-collection model.

Pred uninstallom analyzuj:

- PVC/PV a data retention,
- CRDs a cluster-scoped resources,
- hooks,
- external load balancers,
- shared resources,
- finalizers.

## 20. Uninstall

```bash
helm uninstall payments -n production
```

Odstráni resources spravované release lifecycle podľa Helm behavioru, ale nemusí odstrániť:

- CRDs,
- retained resources,
- PVC/PV/external storage,
- external DNS/LB/IAM resources,
- resources vytvorené hooks alebo operators,
- data backups.

Uninstall nie je automatický bezpečný decommission.

## 21. Drift

Live resources sa môžu líšiť od posledného Helm manifestu kvôli:

- manual edit,
- mutating admission,
- operator/controller,
- HPA scale,
- server-side defaults,
- GitOps controller,
- external policy.

Helm upgrade môže časť driftu prepísať alebo zachovať podľa field ownership a update behavioru. Definuj authoritative writer pre každý field.

## 22. Chart artifact distribution

Chart možno distribuovať cez:

- HTTP chart repository,
- OCI registry,
- packaged `.tgz`,
- local/VCS source v CI.

Production workflow potrebuje:

- immutable versioning,
- registry/repository auth,
- integrity/provenance alebo signature policy,
- retention,
- dependency locking,
- promotion bez rebuild-u.

## 23. Compatibility

Over:

- Helm client support voči Kubernetes version,
- chart `kubeVersion` constraint,
- API versions v templates,
- CRDs a controller version,
- Helm major-version behavior,
- plugins a post-renderers,
- OCI/chart repository support.

Používaj dokumentáciu pre konkrétnu Helm major verziu. Starý Helm 2/Tiller obsah nie je aktuálny architecture model.

## 24. Anti-patterny

### Chart a release považované za to isté

Jeden chart môže mať viac releases s odlišnými values a revisions.

### `appVersion` použitá ako automatický image tag bez contractu

Metadata field sám runtime image nemení.

### Všetko konfigurované cez `--set`

Deployment nie je reprodukovateľný ani reviewable.

### Secret v `values.yaml`

Môže skončiť v Git-e, CI logs, rendered manifeste a release storage.

### Mutable chart reference bez verzie

Rovnaký deployment command môže neskôr renderovať iný content.

### Helm install úspech považovaný za application readiness

API prijatie resources nepreukazuje rollout, probes ani user path.

### Uninstall bez storage/CRD analýzy

Môže zanechať alebo odstrániť kritický state podľa nejasného lifecycle.

## 25. Troubleshooting

### Template render zlyhá

Použi `helm lint`, `helm template --debug`, over values path/type a template scope.

### Manifest renderuje, API ho odmieta

Použi server-side dry-run, over API version, schema, RBAC, admission a immutable fields.

### Release name už existuje

Over namespace, release status/history a či ide o failed/pending release alebo iný owner.

### Upgrade visí alebo zlyhá

Over hooks, workload rollout, admission, Jobs, timeouts, release status a Kubernetes Events.

### Live object sa líši od template

Over admission mutation, controllers, HPA, manual drift a field ownership.

### Release history existuje, workloads nie

Resources mohli byť ručne zmazané alebo controllerom odstránené. Release metadata nie je záruka live state-u.

## 26. Kontrolné otázky

1. Aký je rozdiel medzi chartom, values, rendered manifestom a release-om?
2. Ako sa líši chart version, appVersion a release revision?
3. Ktoré built-in objects sú dostupné v template?
4. Ako funguje values precedence?
5. Čo `helm template` preukazuje a čo nie?
6. Kde Helm uchováva release state a prečo je citlivý?
7. Prečo Helm values nie sú secret manager?
8. Ako vzniká drift medzi release manifestom a live objectom?
9. Prečo uninstall nie je kompletný decommission?
10. Ktoré compatibility vrstvy overíš pred chart upgrade-om?

## Glossary impact

Relevantné pojmy: Helm, Helm chart, chart version, appVersion, Helm template, values, values precedence, values schema, Helm release, release revision, release state, rendered manifest, `upgrade --install`, chart repository a OCI chart.

## Oficiálna dokumentácia

- [Introduction to Helm](https://helm.sh/docs/intro/introduction/)
- [Charts](https://helm.sh/docs/topics/charts/)
- [Chart Template Guide](https://helm.sh/docs/chart_template_guide/)
- [Values Files](https://helm.sh/docs/chart_template_guide/values_files/)
- [Helm Version Support Policy](https://helm.sh/docs/topics/version_skew/)
