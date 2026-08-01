# Upgrades

Kubernetes upgrade je koordinovaný prechod clusteru, Nodes, add-ons a API consumers na novú podporovanú generáciu. Nie je to iba zmena binary verzie control plane-u. Upgrade môže odstrániť deprecated API, zmeniť defaulty, webhook compatibility, kubelet/runtime contract, CNI alebo CSI behavior a Node kernel prerequisites. Úspešný `kubectl get nodes` po upgrade preto nie je konečný verdict.

V Atlas clustri upgradeujeme z podporovanej current generation na nasledujúcu schválenú minor verziu. Najprv sa upraví control plane, potom canary Node pool, platform add-ons a nakoniec ostatné Nodes. `payments-api` a ďalšie kritické workloads zostávajú dostupné a počas mixed-version okna musia fungovať na starej aj novej Node generation.

## Presný current a target inventory

Pred plánom treba zaznamenať:

```text
Kubernetes server a client versions
API server, controller, scheduler a etcd versions
kubelet a container runtime versions po Node pooloch
CNI, CSI, CoreDNS, kube-proxy alebo replacement dataplane
Ingress/Gateway, metrics, autoscaler a policy engines
CRDs, conversion/admission webhooks a operators
OS/kernel a Node image generations
používané/deprecated API versions
backup, restore a rollback capabilities
```

```bash
kubectl version
kubectl get nodes \
  -o custom-columns='NAME:.metadata.name,KUBELET:.status.nodeInfo.kubeletVersion,RUNTIME:.status.nodeInfo.containerRuntimeVersion,KERNEL:.status.nodeInfo.kernelVersion'
kubectl get crd
```

Názov „cluster 1.x“ nezachytí add-on a Node rozdiely.

## Version skew

Kubernetes publikuje version-skew policy pre jednotlivé komponenty. Control plane sa typicky upgraduje pred kubeletmi a kubelety môžu počas bounded okna zaostávať podľa podporovaných pravidiel. Presné povolené rozdiely sa menia s verziou a musia sa overiť proti target release dokumentácii.

Neplánuj upgrade iba z pamäti. Zaznamenaj current→target matrix pre API server, etcd, kubelet, kube-proxy/dataplane a `kubectl` automation.

Viac-minor skok môže vyžadovať sekvenčné upgrady. Preskočenie intermediárnej verzie môže obísť migration alebo deprecation boundary.

## API deprecation a removal

Objekt uložený v etcd sa môže dať čítať cez novú storage version, ale klient, manifest alebo webhook môže stále volať odstránený endpoint. Pred upgradeom potrebujeme inventory API requests, nie iba YAML v jednom repozitári.

```bash
kubectl api-resources
kubectl get --raw /metrics | grep apiserver_requested_deprecated_apis
```

Dostupnosť konkrétnych metrics a audit fields závisí od verzie a konfigurácie. API audit logs môžu odhaliť caller identity a deprecated GVR.

Server-side dry-run proti target-like clusteru:

```bash
kubectl apply --server-side --dry-run=server -f manifests/ -o yaml
```

Jeden directory apply nemusí pokryť Helm render, operators, generated Jobs ani external clients. Inventory musí zahŕňať všetkých consumers.

## CRDs a conversion webhooks

CRD môže podporovať viac served versions a jednu storage version. Upgrade Kubernetes alebo operatora môže vyžadovať schema a conversion zmenu.

```bash
kubectl get crd <name> -o yaml
```

Skontroluj:

```text
served/storage versions
storedVersions status
structural schema
conversion strategy a webhook service
webhook certificate a CA bundle
existing object migration
```

Ak conversion webhook nie je dostupný, API reads alebo writes custom resources môžu zlyhať a zablokovať upgrade alebo controllers.

## Admission webhooks

Webhook musí podporovať target AdmissionReview versions a API semantics. `failurePolicy: Fail` môže pri nekompatibilite zablokovať cluster mutations.

Pred upgradeom otestuj webhook backend na target clusteri a over:

```text
Service a TLS
CA bundle
admissionReviewVersions
namespace/object selectors
timeout a failure policy
bootstrap/break-glass path
```

Upgrade control plane-u bez compatible policy engine-u môže vytvoriť partial outage: reads fungujú, no nové Pods alebo Nodes sa nedajú vytvoriť.

## Backup a recovery gate

Pred control-plane upgradeom vytvor a over etcd snapshot podľa platform contractu. Zároveň skontroluj application data backup, pretože etcd restore nevráti databases a volumes.

Backup nie je automatická rollback cesta pre bežný upgrade problem. Etcd restore je cluster-wide DR operácia a môže vrátiť API state do minulosti. Používa sa až keď control-plane state nemožno bezpečne opraviť alebo roll-forwardnúť.

Upgrade gate má obsahovať posledný úspešný restore test, nie iba timestamp snapshotu.

## Health a capacity gate

Neupgraduj cluster, ktorý už má nevysvetlený degraded state. Pred upgradeom over:

```bash
kubectl get --raw='/readyz?verbose'
kubectl get nodes
kubectl get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded
kubectl get events -A --sort-by=.lastTimestamp
```

Tieto príkazy potrebujú interpretáciu; nie každý non-Running Pod je incident. Zároveň over etcd latency/quorum, controller queues, certificate expiry, CNI/CSI health, DNS, storage capacity a telemetry coverage.

Node replacement potrebuje surge compute kapacitu a PDB-compatible drain. Bez headroomu môže upgrade zablokovať alebo porušiť availability.

## Control-plane upgrade

V managed clustri provider riadi veľkú časť sekvencie, ale používateľ stále nastavuje maintenance window, target version, add-on compatibility a post-checks.

V kubeadm-style clustri sa upgrade typicky vykonáva po jednom control-plane Node-e podľa `kubeadm upgrade` workflowu a version-specific dokumentácie. Jeden Node aktualizuje cluster configuration a ostatné potom local components.

Nikdy neaplikuj generický sequence bez kontroly exact verzie. Uchovaj:

```text
preflight output
selected target packages/images
static Pod manifest diff
certificate state
API endpoint backend health
etcd member health
```

Po každom Node-e over stable endpoint a komponenty, nie iba local host.

## Mixed-version control plane

Počas rolling upgrade-u môžu API server replicas krátko používať rozdielne compatible versions. Load balancer posiela requests na viac generations. Clients a webhooks musia fungovať s celým supported overlapom.

Ak jeden API server podáva odlišné discovery alebo certificate behavior, incident môže byť intermittent. Testuj každý backend aj stable endpoint.

Control-plane downgrade po storage/schema migration nemusí byť podporovaný. Roll-forward je často bezpečnejší než pokus vrátiť binaries.

## Add-ons

CoreDNS, CNI, CSI, kube-proxy alebo eBPF dataplane a metrics components majú vlastné compatibility matrices. Neupgraduj ich automaticky všetky naraz s control plane-om bez oddeleného verdictu.

Pre každý add-on zachovaj:

```text
source manifest/chart/operator version
image digest
CRD/RBAC/config generation
Node prerequisites
upgrade a rollback path
capability tests
```

CNI upgrade môže zmeniť existujúci Node dataplane. CSI upgrade môže ovplyvniť provision, attach alebo snapshot. CoreDNS upgrade mení cluster-wide resolution.

## Node upgrade cez immutable replacement

Atlas vytvára nový Node image namiesto in-place patchovania:

```text
nový OS/kernel/runtime/kubelet image
→ nový canary Node pool s bootstrap taintom
→ platform DaemonSets a capability tests
→ bounded application canary
→ postupný cordon/drain starých Nodes
→ workload reschedule
→ old pool retirement
```

Tento model poskytuje čistú rollback hranicu: zastaviť rollout nového poolu a ponechať starú generation, pokiaľ workload/data compatibility dovolí.

In-place kubelet upgrade môže byť vhodný v inom prostredí, ale musí mať rovnaké preflight, drain a recovery controls.

## Cordon a drain

```bash
kubectl cordon <old-node>
kubectl drain <old-node> \
  --ignore-daemonsets \
  --delete-emptydir-data=false
```

Drain používa eviction API a môže byť blokovaný PDB. `emptyDir` a local storage vyžadujú explicitné rozhodnutie. Stateful Pods potrebujú storage attachment a fencing model.

Force flags môžu obísť safety contracts a nemajú byť defaultom. Ak PDB blokuje drain, najprv zisti, či cluster nemá dostatočnú ready kapacitu alebo PDB neodráža reálny availability model.

## Canary Node generation

Pred všeobecným schedulingom zostáva nový Node tainted. Capability canary overí:

```text
Pod sandbox a image pull
DNS a Service
same/cross-Node traffic
NetworkPolicy allow/deny
CSI attach/mount/snapshot podľa potreby
seccomp/Pod Security
metrics, logs a audit coverage
Node pressure a time sync
```

Potom sa na malej cohort-e spustí `payments-api` canary s rovnakým image/configom ako na starých Nodes. Porovná sa request success, latency, throttling, DNS, network a logs.

## Workload compatibility

Kubernetes upgrade môže zmeniť defaulted fields, topology alebo runtime behavior aj bez zmeny workload manifestu. Testuj reprezentatívne workload classes:

```text
stateless Deployment
StatefulSet s zonálnym PVC
DaemonSet s host accessom
Job/CronJob
Gateway/Ingress path
HPA a metrics
Pod Security/admission forbidden path
```

`payments-api` syntetika overí exactly-once payment outcome a loaded generations.

## Upgrade observability

Dashboardy majú byť rozdelené podľa generation:

```text
old/new control-plane backend
old/new Node image pool
old/new CNI/CSI agent
old/new workload revision
zone
```

Cluster-wide priemer môže skryť, že iba nová Node cohorta má 20 % packet loss. Central telemetry musí pokrývať novú generation skôr, než jej zveríme production traffic.

## Rollback hranice

Node pool rollout možno často zastaviť a nové Nodes odstrániť. Add-on rollback závisí od CRD/data migration a dataplane state-u. Control-plane binary downgrade môže byť nepodporovaný. Etcd restore je posledná DR možnosť, nie štandardný rollback.

Pred každou vrstvou definuj:

```text
čo sa dá vrátiť
čo sa už migrovalo
aký state zostáva forward-only
ako sa overí compatibility starej generation
```

Application rollbacks musia byť kompatibilné s database a events vytvorenými počas upgrade windowu.

## Incident: control plane prešiel, Nodes nie

API server upgrade bol úspešný. Staré kubelety boli v podporovanom skew okne. Nový Node image však používal kernel bez modulu vyžadovaného CNI dataplane-om. CNI Pod bol Running a shallow readiness zelená, ale cross-Node traffic zlyhával.

Containment zastavilo Node pool rollout a cordonovalo canary Nodes. Control plane sa nevracal, pretože nebol root cause. Oprava vytvorila nový Node image s prerequisite a rozšírila capability canary.

## Incident: odstránené API používal nočný Job

Repository manifests už používali novú API verziu. Audit však ukázal, že externý backup script raz denne vytváral resource cez starý odstránený endpoint. Pre-upgrade test počas pracovného dňa ho nezachytil.

Po upgrade-e Job zlyhal a backup nevznikol. Recovery opravila client a okamžite vytvorila backup. Skorší control je dlhšie API usage observation window a caller inventory z audit logs.

## Incident: webhook zablokoval Node replacement

Policy webhook podporoval staršiu AdmissionReview verziu a po control-plane upgrade-e prestal odpovedať validne. `failurePolicy: Fail` zablokovala Pods critical DaemonSetov na nových Nodes. Staré Nodes fungovali.

Break-glass postup dočasne izoloval webhook z bootstrap namespace-u s auditom. Opravený webhook sa nasadil a forbidden policy tests sa zopakovali. Skorší control je target-version conformance test webhooku.

## Incident: observability bola slepá iba na novej Node generácii

Nový runtime ukladal container logs do inej path/config generácie. Collector DaemonSet bol Ready, ale sledoval starý path. Workload incident na canary Node-e nemal central logs a diagnóza sa oneskorila.

Oprava zladila collector config a pridala telemetry coverage test do Node capability gate-u. Chýbajúce logs boli control failure, nie príčina aplikačného incidentu.

## Model, ktorý si treba odniesť

Kubernetes upgrade je viacvrstvový transition: API, etcd, control plane, webhooks/CRDs, add-ons, Nodes a workloads. Každá vrstva má compatibility a rollback hranicu. Bezpečný postup používa deprecation inventory, backup/restore proof, health/capacity gate, control-plane sequencing, immutable canary Nodes, capability tests, cohort-aware telemetry a business validation. Etcd restore zostáva DR nástrojom, nie bežným rollbackom.

## Referencie

- [Version Skew Policy](https://kubernetes.io/releases/version-skew-policy/)
- [Upgrading kubeadm clusters](https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-upgrade/)
- [Deprecated API Migration Guide](https://kubernetes.io/docs/reference/using-api/deprecation-guide/)
- [Safely Drain a Node](https://kubernetes.io/docs/tasks/administer-cluster/safely-drain-node/)
