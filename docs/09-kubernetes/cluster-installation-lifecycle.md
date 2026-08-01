# Cluster installation a lifecycle

Kubernetes cluster nie je hotový iba vtedy, keď odpovie API server a prvý Node má `Ready=True`. Produkčný cluster je zložený z control-plane endpointu, etcd, PKI, Nodes, runtime-u, CNI, CSI, DNS, admission, observability, backupu a identity integrations. Každá vrstva má vlastnú verziu, ownera a recovery model.

V Atlas scenári prevádzkujeme cluster `atlas-prod-eu1` cez tri failure domains. Control plane má tri repliky a external endpoint, worker Nodes vznikajú z immutable machine image-u a do serving poolu vstúpia až po capability canary. Workloads používajú pinned image digests a platform add-ons majú samostatné release generations.

## Managed a self-managed responsibility

Managed Kubernetes môže poskytovateľ spravovať control plane, etcd backup alebo upgrades. To však neznamená, že zákazník nemá zodpovednosť za Kubernetes objects, Nodes, add-ons, IAM, network, storage, version skew a application recovery.

Self-managed cluster pridáva priamu zodpovednosť za:

```text
control-plane hosts a endpoint
etcd membership a storage
PKI a certificate rotation
component flags/config
bootstrap a upgrades
backup/restore
host OS a runtime
```

Pred návrhom runbooku treba presne vedieť, čo platforma poskytuje a čo iba marketingovo označuje ako „managed“.

## Control-plane topology

HA control plane potrebuje viac než tri API server processes. External alebo virtual endpoint musí smerovať na ready API servery. Etcd members musia byť rozložené medzi failure domains s nízkou a stabilnou latency. Controller-manager a scheduler používajú leader election.

```text
client
→ stable control-plane endpoint
→ ready API server
→ etcd quorum
```

Strata jednej zone nemá zničiť endpoint ani etcd quorum. Na druhej strane natiahnutie etcd cez príliš vzdialené regions môže porušiť latency a availability.

## kubeadm bootstrap model

V kubeadm-style clustri prvý control-plane Node typicky vykoná `kubeadm init`. Nástroj pripraví PKI, kubeconfigy, static Pod manifests a bootstrap configuration podľa verzie a flags.

```bash
kubeadm init --config kubeadm-config.yaml
```

Tento príkaz nie je univerzálny recept. Config musí obsahovať správny control-plane endpoint, networking CIDRs, certificate SANs, Kubernetes version a runtime socket. Pred produkčným použitím sa uchová versionovaný kubeadm config a preflight output.

Ďalšie control-plane Nodes a workers sa pripájajú cez `kubeadm join` s krátkodobým bootstrap tokenom a discovery trustom.

```bash
kubeadm token create --print-join-command
```

Join command je credential a nemá sa ukladať do verejných logs.

## Static Pods control plane-u

Kubeadm často zapisuje manifests do `/etc/kubernetes/manifests`. Kubelet ich spúšťa ako static Pods. API server zobrazuje mirror Pods, ale desired source je lokálny súbor na každom control-plane Node-e.

```text
manifest na Node filesysteme
→ kubelet static Pod
→ mirror Pod v API
```

`kubectl edit pod kube-apiserver-...` neopraví manifest. Kubelet znovu vytvorí Pod z lokálneho source-u.

Rolling zmena control-plane manifestov sa robí po jednom Node-e a s quorum/endpoint guardrails.

## PKI

Cluster používa viac certifikátov a kľúčov:

```text
cluster CA
API serving certificate
API→etcd client certificate
etcd server/peer/client certificates
kubelet client/serving certificates
controller a scheduler kubeconfigs
service-account signing keys
front-proxy CA a clients podľa modelu
```

Každý artifact má purpose, ownera, expiry a rotation path. Obnova iba API serving certificate nepomôže, ak controller-manager client credential expiroval.

```bash
kubeadm certs check-expiration
```

Príkaz platí pre kubeadm-managed PKI a konkrétnu verziu. External CA alebo managed platforma môže mať iný lifecycle.

## Cluster networking bootstrap

Po init môže API fungovať, ale bežné Pods sa bez CNI nespustia správne. CNI installation musí zodpovedať Pod CIDR, kube-proxy alebo replacement dataplane-u, kernel prerequisites a NetworkPolicy requirements.

```text
API/control plane bootstrap
→ CNI controller/DaemonSet
→ Pod networking
→ CoreDNS readiness
→ workload scheduling
```

CoreDNS Pods môžu zostať Pending alebo NotReady, kým CNI nie je funkčné. To nie je dôvod meniť DNS config pred dokončením network bootstrapu.

## Runtime a cgroup contract

Kubelet a container runtime musia používať kompatibilný cgroup driver a CRI endpoint. Host kernel, cgroup v2, seccomp, AppArmor/SELinux a filesystem drivers sú súčasťou Node contractu.

Immutable Node image má pinovať:

```text
OS/kernel generation
container runtime version/config
kubelet version/config
CNI/CSI prerequisites
sysctls a modules
certificate/bootstrap agents
observability/security agents
```

Ručný patch jedného Node-u vytvára drift, ktorý sa pri replacement-e stratí.

## Node bootstrap a join

Nový Node najprv získa bootstrap identity, pošle CSR a dostane kubelet client credential podľa approval policy. Potom sa registruje ako Node a publikuje capacity/conditions.

Automatické CSR approval je security boundary. Broad approval pre ľubovoľný subject môže vpustiť neautorizovaný Node alebo vystaviť serving certificate.

```bash
kubectl get csr
kubectl get nodes -o wide
```

Node `Ready=True` neznamená, že critical DaemonSets, CNI policy, CSI, DNS a telemetry sú plne funkčné.

## Capability gate pre nový Node

Atlas necháva nový Node tainted:

```text
atlas.example/bootstrap=true:NoSchedule
```

Platform canary na ňom overí:

```text
CRI image pull a process start
same-Node a cross-Node CNI traffic
Service ClusterIP a DNS
allowed aj forbidden NetworkPolicy
CSI attach/mount
Pod Security/seccomp
logs a metrics delivery
Node pressure a time sync
```

Až potom controller odstráni bootstrap taint a Node prijme production workloads.

## Add-ons ako samostatné releases

CoreDNS, CNI, CSI, ingress/Gateway controller, metrics server, autoscaler a policy engine majú vlastné images, CRDs, RBAC a upgrade matrices. „Cluster version 1.x“ neidentifikuje ich generations.

Add-on upgrade môže meniť dataplane bez zmeny Kubernetes minor version. Inventory preto spája cluster, Node pool a add-on release IDs.

## Admission a policy bootstrap

Validating/mutating webhooks a admission policies môžu zablokovať aj system bootstrap, ak nemajú správne namespace selectors, failure policy alebo CA bundle.

Pri zavádzaní webhooku:

```text
nasadiť backend
→ overiť Service a TLS
→ vytvoriť webhook v audit/fail-open režime podľa rizika
→ overiť allowed/forbidden requests
→ až potom sprísniť enforcement
```

Fail-closed webhook bez dostupného backendu môže zablokovať vytvorenie Pods potrebných na opravu samotného webhooku.

## Lifecycle Nodes: cordon, drain, replace

Immutable Node maintenance:

```bash
kubectl cordon <node>
kubectl drain <node> --ignore-daemonsets --delete-emptydir-data=false
```

Cordon zastaví nové scheduling. Drain používa eviction API pre vhodné Pods a rešpektuje PDB podľa flags/semantics. Stateful Pods, local storage, DaemonSets a unmanaged Pods potrebujú osobitné rozhodnutie.

Po drain-e sa Node odstráni z infraštruktúry a clusteru podľa owner workflowu. Zmazanie Node objektu samo nevypne machine.

## Decommission

Cluster decommission nie je `kubectl delete namespace --all`. Potrebuje inventory:

```text
workloads a business data
PVs, snapshots a backups
LoadBalancers, DNS a IPs
cloud identities a credentials
certificate/key material
registry a release evidence
external webhooks/integrations
logs, audit a compliance retention
```

Najprv sa migruje alebo zastaví business traffic a dáta, potom sa odstraňujú dependents. Etcd snapshot po decommissione môže obsahovať Secrets a osobné údaje a potrebuje secure retention/destruction.

## Incident: cluster bol Ready, ale DNS nefungovalo

Kubeadm init prešiel, API server a worker Node boli Ready. CNI manifest bol aplikovaný s nesprávnym Pod CIDR. CNI agent bežal, ale routes nezodpovedali controller-manager cluster CIDR. CoreDNS Pods sa spustili, no cross-Node traffic zlyhával.

Oprava nebola restartovať CoreDNS. Tím zladil versionovaný networking config a znovu vytvoril test cluster. Produkčný bootstrap gate začal porovnávať kubeadm Pod CIDR, CNI config a actual Node routes.

## Incident: nový Node pool prijal traffic pred CNI inicializáciou

Node condition prešla na Ready a bootstrap taint sa odstraňoval iba podľa tejto condition. Application Pods sa schedulovali skôr, než CNI DaemonSet dokončil dataplane sync. Same-Node traffic fungoval, cross-Node intermittently zlyhával.

Oprava pridala capability canary a explicitný platform condition pred untaint. Node Ready ostala iba jedným vstupom.

## Incident: certifikáty boli obnovené iba na jednom control-plane Node-e

Operátor spustil kubeadm certificate renewal na jednom Node-e a reštartoval jeho static Pods. Ostatné API servery ďalej podávali starý expirovaný certificate za load balancerom. Klienti videli intermittent TLS failure.

Oprava vykonala riadenú per-Node renewal/restart sekvenciu a overila certificate fingerprint na každom backend-e aj cez stable endpoint.

## Incident: fail-closed webhook zablokoval vlastnú opravu

Validating webhook backend bežal v namespace, ktorý sám podliehal webhooku. Po expirovaní serving certificate API server nemohol zavolať webhook a odmietal nové Pods vrátane opraveného backendu.

Recovery použila pripravený break-glass postup s auditom a dočasnou úpravou webhook configuration. Skorší control je namespace exemption pre úzky bootstrap path, certificate monitoring a staged failurePolicy.

## Model, ktorý si treba odniesť

Cluster lifecycle zahŕňa control-plane endpoint, etcd, PKI, Nodes, runtime, CNI/CSI, add-ons, admission, observability a recovery. API a Node Ready sú iba čiastkové signals. Nová cluster alebo Node generation vstupuje do production až po capability tests a exact inventory. Údržba má preferovať versionované replacementy pred ručným driftom.

## Referencie

- [Creating a cluster with kubeadm](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/create-cluster-kubeadm/)
- [Highly Available Topology Options](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/ha-topology/)
- [PKI certificates and requirements](https://kubernetes.io/docs/setup/best-practices/certificates/)
- [Safely Drain a Node](https://kubernetes.io/docs/tasks/administer-cluster/safely-drain-node/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: ResourceQuota a LimitRange](resourcequota-limitrange.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: etcd backup a restore →](etcd-backup-restore.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
