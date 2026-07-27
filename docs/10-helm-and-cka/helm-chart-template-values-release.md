# Helm chart, template, values a release

Helm je package, render a release-lifecycle nástroj pre Kubernetes. Jeho hlavná hodnota nie je iba skrátenie YAML-u. Spája versionovaný chart artifact, values contract, release identity a cluster capabilities do konkrétnej sady Kubernetes objektov a uchováva históriu tejto operácie.

Helm však nevlastní runtime reconciliation workloadu. Po prijatí manifestov preberajú stav Kubernetes API server, controllers, scheduler, kubelet, CNI, CSI a samotná aplikácia. Preto úspešný Helm command nepreukazuje správny rollout, správnu effective konfiguráciu ani business outcome.

## 1. Dominantný lifecycle

```text
release intent a outcome contract
→ immutable release subject
→ chart a dependency resolution
→ effective values resolution
→ template render generation
→ schema, API a admission validation
→ Helm release mutation
→ Kubernetes reconciliation
→ live/effective/application verification
→ revision evidence a support state
→ rollback, roll-forward alebo decommission
```

Každý krok mení inú vrstvu. Pri incidente musí byť jasné, v ktorej vrstve vznikol nesúlad.

## 2. Atlas Payments release subject

Sekcia používa jeden prepojený scenár:

```text
cluster: atlas-prod-eu1
cluster generation: K136
namespace: atlas-payments-prod
release: payments-prod
current release revision: 17
target release revision: 18
chart: atlas-payments
chart version: 2.7.0
chart OCI digest: CH57
dependency lock digest: D57
values bundle digest: V57
rendered manifest digest: M57
application image digest: I57
source commit: C57
business operation: payment authorization P-884
```

Release cieľ je:

```text
nasadiť image I57
vypnúť legacy authorizer
zachovať presne-once authorization
nezmeniť Service identity ani persistent data
```

Zakázané výsledky sú:

- legacy authorizer zostane aktívny;
- release použije iný chart, dependency alebo image artifact;
- vzniknú duplicate payment authorizations;
- Service stratí eligible endpointy;
- plaintext credentials sa objavia v values alebo release storage;
- uninstall alebo rollback poškodí dáta.

## 3. Chart artifact

Chart je versionovaný balík. Typicky obsahuje:

```text
atlas-payments/
├── Chart.yaml
├── Chart.lock
├── values.yaml
├── values.schema.json
├── charts/
├── crds/
├── templates/
│   ├── _helpers.tpl
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   └── NOTES.txt
└── .helmignore
```

Chart source directory nie je automaticky release artifact. Production subject má identifikovať packaged chart alebo OCI manifest podľa immutable digestu, nie iba mutable repository pathu alebo tagu.

```text
Git source C57
→ dependency build podľa D57
→ lint, render a tests
→ package atlas-payments-2.7.0.tgz
→ publish OCI artifact CH57
→ promote ten istý digest
```

Ak sa chart pri každom prostredí znovu balí alebo dependency graph znovu resolve-ne, environment promotion už nie je promotion rovnakého artifactu.

## 4. `Chart.yaml`, chart version a application version

Príklad:

```yaml
apiVersion: v2
name: atlas-payments
version: 2.7.0
appVersion: "3.12.0"
kubeVersion: ">=1.32.0-0"
```

Rozlišuj:

```text
chart version
≠ application version
≠ image tag alebo digest
≠ Helm release revision
≠ Kubernetes Deployment revision
```

`version` identifikuje package contract chartu. Zmena templates, defaults, dependencies alebo schema má vytvoriť novú chart version.

`appVersion` je metadata. Sama nemení image reference. Ak chart používa `appVersion` ako fallback tag, musí to byť explicitný, testovaný contract, nie predpoklad operátora.

## 5. Helm client a major-version subject

Helm client version a apply mode patria do release subjectu. Helm major verzie môžu meniť command behavior, apply semantics, plugin rozhrania alebo storage detaily, aj keď chart format zostáva kompatibilný.

Production evidence preto obsahuje:

```text
Helm version
command a relevant flags
apply mode
plugins a post-renderers
Kubernetes API endpoint a context
storage driver
```

Nepoužívaj historický Helm 2/Tiller model na opis moderného Helm release-u. Pri Helm 3 a Helm 4 používaj dokumentáciu pre konkrétnu major/minor verziu a pinuj toolchain v CI.

## 6. Values ako public configuration contract

`values.yaml` definuje default interface chartu:

```yaml
replicaCount: 4

image:
  repository: registry.example.com/atlas/payments
  digest: ""

legacyAuthorizer:
  enabled: true

service:
  port: 8080
```

Values contract zahŕňa:

- názov a path každého inputu;
- typ a allowed values;
- default;
- ownership;
- sensitivity;
- compatibility pri upgrade;
- vzťah k výslednému Kubernetes fieldu;
- či zmena vyžaduje Pod replacement, data migration alebo external action.

Values nie sú iba template variables. Sú verejné API chartu.

## 7. Effective values resolution

Effective values vznikajú merge-om viacerých zdrojov:

```text
chart defaults
→ parent/subchart values podľa scope-u
→ prvý -f file
→ ďalší -f file
→ --set / --set-string / --set-file
→ operation-specific computed context
```

Atlas release používa:

```bash
helm upgrade --install payments-prod \
  oci://registry.example.com/charts/atlas-payments \
  --version 2.7.0 \
  -f values-prod.yaml \
  -f values-prod-eu1.yaml \
  --set-string image.digest=sha256:I57 \
  --namespace atlas-payments-prod
```

Source inventory musí zachytiť poradie files aj exact CLI overrides. Samotný `values-prod.yaml` nie je effective configuration.

Pre incident-safe evidence ukladaj:

- redacted effective values;
- values source revisions a digest V57;
- schema validation result;
- explicitný zoznam secret references bez secret payloadu;
- mapping kritických values na rendered fields.

## 8. Values schema a semantic invariants

`values.schema.json` môže validovať typy, required fields, enums a štruktúru. Nenahrádza však semantic pravidlá.

Príklady semantic invariants:

```text
legacyAuthorizer.enabled=false
→ legacy endpoint, env a policy resources sa nesmú renderovať

serviceAccount.create=false
→ serviceAccount.name musí byť explicitný

image.digest je nastavený
→ mutable tag nesmie určovať runtime artifact
```

Validácia musí odlíšiť:

```text
input je syntakticky platný
≠ input je semanticky konzistentný
≠ rendered manifest je validný
≠ live workload dosiahol požadovaný outcome
```

## 9. Render generation

Helm kombinuje:

```text
chart CH57
+ dependency graph D57
+ values V57
+ release name/namespace
+ capabilities/API inventory
+ Helm engine/version
+ optional live lookup a post-renderer
→ rendered manifest M57
```

Relevantné built-in objects:

- `.Values` — effective values;
- `.Chart` — chart metadata;
- `.Release` — release identity a operation context;
- `.Capabilities` — API/Kubernetes capability view;
- `.Files` — packaged files;
- `.Template` — current template metadata.

Render je vlastná evidence generation. Rovnaký chart version nemusí vytvoriť rovnaký M57, ak sa zmení values, dependency artifact, capabilities, live `lookup`, random/time function, plugin alebo post-renderer.

## 10. Render validation ladder

Použi viac vrstiev:

```text
chart structure a dependency lock
→ values schema
→ template execution
→ YAML parse
→ Kubernetes object schema
→ API discovery
→ admission mutation a validation
→ apply/update semantics
→ controller rollout
→ application/business outcome
```

Príklady:

```bash
helm dependency build ./chart
helm lint ./chart -f values-prod.yaml
helm template payments-prod ./chart \
  -f values-prod.yaml \
  -f values-prod-eu1.yaml > rendered.yaml
kubectl apply --dry-run=server -f rendered.yaml
kubectl diff -f rendered.yaml
```

Local render nepreukazuje live admission, permissions, current immutable fields, controller behavior ani business correctness.

## 11. Release identity

Helm release je pomenovaná inštancia chartu v namespace-e:

```text
release name + namespace + cluster identity
```

`payments-prod` v dvoch clusteroch sú dve odlišné releases. Rovnaký name v inom namespace-e je tiež iný release subject.

Pred write operáciou over:

```bash
kubectl config current-context
helm list -A
helm status payments-prod -n atlas-payments-prod
helm history payments-prod -n atlas-payments-prod
```

Context name sám nestačí. Pre high-risk release zaznamenaj API endpoint, CA/cluster identity a environment generation.

## 12. Release mutation nie je jedna transakcia

Zjednodušený flow:

```text
Helm resolve a render
→ API requests pre resource set
→ Helm čaká podľa command flags
→ Kubernetes controllers pokračujú v reconciliation
→ release state dostane revision/status
```

Môžu existovať partial states:

- časť objektov bola aktualizovaná, ďalší API request zlyhal;
- hook vykonal durable side effect, ale release skončil failed;
- timeout nastal, no rollout pokračuje;
- release je `deployed`, ale aplikácia je business-incorrect;
- API objekty sú healthy, no external DNS alebo database contract nie.

Timeout alebo non-zero exit preto neznamená automaticky, že žiadna zmena neprebehla. Pred retry read-back-ni release history, live objects, hooks a external side effects.

## 13. Release revision a evidence

Revision je Helm lifecycle identity:

```bash
helm history payments-prod -n atlas-payments-prod
helm status payments-prod -n atlas-payments-prod
helm get values payments-prod -n atlas-payments-prod --all
helm get manifest payments-prod -n atlas-payments-prod
helm get hooks payments-prod -n atlas-payments-prod
```

Revision 18 nie je Git commit C57 ani Deployment revision. Release evidence musí vytvoriť koreláciu:

```text
C57 → CH57 + D57 + V57 → M57 → Helm revision 18
→ Kubernetes object UID/generation
→ Pod image I57 a process-loaded config
→ request P-884 outcome
```

Helm release storage môže obsahovať chart/config/manifests. Preto je citlivý RBAC subject a nie je náhradou za Git, artifact registry, secret manager ani application-data backup.

## 14. Live state a field ownership

Po apply môže live object zmeniť:

- API defaulting;
- mutating admission;
- HPA;
- operator/controller;
- GitOps reconciler;
- manual edit;
- iný field manager;
- server-side alebo client-side apply behavior.

Porovnávaj:

```text
versionovaný source
→ effective values
→ rendered manifest M57
→ Helm-stored manifest revision 18
→ admitted live object
→ controller status
→ process-loaded effective state
```

Drift nie je jedna kategória. Niektorý drift je očakávaný controller-owned status alebo replicas field. Iný je konflikt dvoch authoritative writers.

## 15. Worked failure: green release, zakázaná funkcia aktívna

CI vykonalo release revision 18. Helm command skončil úspešne. Deployment bol Available a syntetický health endpoint bol green. Payment audit však ukázal, že request P-884 stále použil legacy authorizer, hoci `V57` explicitne obsahoval:

```yaml
legacyAuthorizer:
  enabled: false
```

### Exact subject

```text
cluster K136
release payments-prod revision 18
chart CH57
lock D57
values V57
manifest M57
Deployment UID/generation
Pods s image I57
request P-884
```

### Competing hypotheses

1. CI použilo nesprávny values file alebo override poradie.
2. `--set` alebo inherited value prepísal `false`.
3. Template transformácia zmenila explicitné `false` na default `true`.
4. Dependency helper vyrenderoval starý config fragment.
5. Admission webhook doplnil legacy env/config.
6. Pods neboli recreated a používajú starú process-loaded konfiguráciu.
7. Traffic stále smeruje na old-generation Pods.
8. Audit request patrí inému clusteru alebo release subjectu.

### Discriminating observation points

| Hypotéza | Observation |
|---|---|
| wrong values inventory | CI command record, values digests a `helm get values --all` |
| pipeline zmenila `false` | render relevantného template s exact V57 a manifest M57 |
| helper/dependency drift | packaged chart CH57, lock D57 a helper call graph |
| admission mutation | dry-run/server response, audit a live managed fields |
| stale Pod generation | Deployment/ReplicaSet UID, config checksum, Pod creation time |
| old traffic cohort | EndpointSlices, Pod labels, request trace a image digest |
| wrong cluster | kubeconfig endpoint/CA a release storage identity |

`helm status: deployed` nediskriminuje žiadnu z týchto príčin.

### Finding

Template obsahoval:

```gotemplate
legacyAuthorizerEnabled: {{ .Values.legacyAuthorizer.enabled | default true }}
```

Helm/Sprig považovalo explicitné `false` za empty, takže render M57 obsahoval `true`. Helm a Kubernetes vykonali presne chybný desired state.

### Containment

- zastav ďalšie automatic releases nad rovnakou release identity;
- zachovaj CH57, D57, V57, M57, revision storage, audit a Pod evidence;
- obmedz legacy path cez úzky versionovaný config/policy change, ak je bezpečný;
- chráň payment idempotency a downstream pred retries;
- nemaž release history ani Pods pred získaním process-loaded evidence.

### Authoritative recovery

1. oprav template contract tak, aby rozlišoval missing a explicitné `false`;
2. pridaj schema a render test pre boolean false;
3. vytvor nový chart artifact CH58 a manifest M58;
4. vykonaj server-side validation a admitted-object diff;
5. rolloutni novú release revision 19;
6. over exact Pod generation, config checksum a image digest;
7. požiadaj business synthetic o legacy aj current authorization path.

### Verify original a forbidden outcomes

Potvrď:

- request P-884-like synthetic používa nový authorizer;
- legacy endpoint/env/config nie je v rendered ani live state-e;
- všetky active endpoints patria revision 19 generation;
- payment authorization vznikne presne raz;
- druhý render rovnakého subjectu vytvorí rovnaký M58;
- opakovaný upgrade je bounded no-op alebo vysvetliteľná reconciliation;
- starý broken chart digest už nie je promotion target.

### Earlier controls

- values schema a contract tests;
- golden render pre `false`, `0`, empty a missing;
- release manifest digest v provenance;
- admitted-object diff;
- business synthetic s forbidden-outcome assertion;
- release acceptance via chart/values/manifest/image identity chain.

## 16. Secrets a release storage

Helm values nie sú secret manager. Secret môže uniknúť cez:

- values Git history;
- CLI history a CI logs;
- rendered manifest;
- Helm release storage;
- `helm get values` a `helm get manifest`;
- debug output;
- Kubernetes Secret bez primeraného encryption/RBAC modelu.

Preferuj reference na external secret, encrypted source workflow alebo workload identity. Evidence archivuj redacted a porovnávaj cez epoch, resourceVersion alebo checksum bez publikovania payloadu.

## 17. Uninstall a decommission

```bash
helm uninstall payments-prod -n atlas-payments-prod
```

Uninstall je iba časť decommission lifecycle-u. Analyzuj:

```text
Helm-managed resources
+ hooks a retained resources
+ CRDs a cluster-scoped objects
+ PVC/PV a application data
+ external DNS/LB/IAM
+ operator-created dependents
+ credentials a release history
+ backups, audit a legal retention
```

Helm labels a release state nie sú univerzálny Kubernetes ownerReference garbage-collection graph. `uninstall` nesmie byť použitý ako neanalyzovaný data cleanup.

## 18. Rollback a roll-forward boundary

Rollback na staršiu revision obnovuje Helm-stored chart/config/manifest intent v rámci Helm mechanizmu. Nemusí vrátiť:

- database schema;
- CRD storage version;
- hook side effects;
- external resources;
- immutable field transitions;
- credentials;
- data zapísané novou aplikáciou.

Rozhodnutie musí vychádzať z current durable state-u, nie iba z existencie starej revision.

## 19. Referenčný release record

```text
release intent a approver
cluster endpoint/CA/generation
namespace a release name
Helm version, apply mode, plugins/post-renderers
source commit
chart version a digest
Chart.lock a dependency digest
values sources, order a redacted effective digest
rendered manifest digest
server/admission validation evidence
release revision a timestamps
live object UID/generation inventory
image/config/secret epochs
hooks a external side effects
technical a business acceptance
rollback/roll-forward boundary
retirement/decommission evidence
```

## 20. Anti-patterny

- chart version, appVersion a release revision považované za jednu identitu;
- mutable chart reference bez digestu alebo version policy;
- `helm dependency update` počas release bez review locku;
- effective values rekonštruované iba z jedného file-u;
- plaintext secret v values;
- local render považovaný za server/admission/runtime verdict;
- Helm `deployed` považovaný za business success;
- timeout okamžite retryovaný bez read-backu;
- manual live patch bez rozhodnutia o authoritative writerovi;
- rollback považovaný za zvrátenie durable side effects;
- uninstall považovaný za kompletný decommission.

## 21. Kontrolné otázky

1. Ktoré identity tvoria immutable Helm release subject?
2. Prečo chart source directory nie je automaticky production artifact?
3. Ako sa líši chart version, appVersion, Helm revision a Deployment revision?
4. Ako vznikajú effective values a prečo záleží na poradí?
5. Ktoré inputs môžu meniť rendered manifest bez zmeny chart version?
6. Čo preukazuje `helm status: deployed` a čo nepreukazuje?
7. Ako odlíšiš rendered, admitted, live a process-loaded state?
8. Prečo timeout Helm operácie nemusí znamenať nulový side effect?
9. Ktoré boundaries musí posúdiť rollback?
10. Aké dôkazy uzatvárajú release acceptance a decommission?

## Glossary impact

Relevantné pojmy: Helm release subject, chart artifact generation, values bundle generation, effective values, render generation, rendered-manifest digest, release mutation boundary, Helm revision evidence, admitted/live/process-loaded state chain, release acceptance, forbidden release outcome, Helm unknown-operation outcome a Helm decommission subject.

## Oficiálna dokumentácia

- [Helm documentation](https://helm.sh/docs/)
- [Charts](https://helm.sh/docs/topics/charts/)
- [Chart Template Guide](https://helm.sh/docs/chart_template_guide/)
- [Values Files](https://helm.sh/docs/chart_template_guide/values_files/)
- [Helm 4 Overview](https://helm.sh/docs/overview/)
- [Helm Version Support Policy](https://helm.sh/docs/topics/version_skew/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Kubernetes troubleshooting](../09-kubernetes/kubernetes-troubleshooting.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Template functions a pipelines →](template-functions-pipelines.md)
<!-- KNOWLEDGE-NAVIGATION:END -->