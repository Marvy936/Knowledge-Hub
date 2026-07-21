# Worker node components

Worker node poskytuje compute prostredie, v ktorom Kubernetes spúšťa Pods. Control plane pridelí Pod na Node, ale samotné image pull, container lifecycle, network namespace, mounts, probes, resource controls a status reporting vykonávajú node-level components. Pri diagnostike treba oddeliť kubelet, container runtime, CNI, service dataplane, CSI, operating system a samotnú aplikáciu.

## 1. Node ako API objekt a reálny stroj

`Node` je Kubernetes object reprezentujúci fyzický alebo virtuálny stroj.

Reálny worker node obsahuje:

- operating system a kernel,
- kubelet,
- CRI-compatible container runtime,
- CNI plugin a node network components,
- kube-proxy alebo alternatívny Service dataplane,
- CSI node plugins podľa storage architektúry,
- local filesystem a image/content store,
- system services a security controls.

Node object je reportovaný pohľad v API. Nie je samotný server.

## 2. Hlavný execution flow

Keď scheduler pridelí Pod na Node:

1. Pod `.spec.nodeName` alebo binding ukazuje na Node.
2. Kubelet cez watch/list zistí pridelený Pod.
3. Kubelet vyhodnotí local admission a dependencies.
4. Volume manager pripraví mounts a CSI operácie.
5. Kubelet požiada runtime cez CRI o Pod sandbox.
6. Runtime a CNI pripravia network namespace a interface.
7. Runtime pullne images podľa policy.
8. Spustia sa init containers.
9. Spustia sa application a sidecar containers podľa lifecycle semantics.
10. Kubelet vykonáva probes a reportuje status.
11. Pri deletion alebo failure vykoná termination/cleanup.

## 3. kubelet

Kubelet je primary node agent.

Zodpovednosti:

- registrácia Node-u,
- Node status a heartbeat reporting,
- sledovanie Pods pridelených Node-u,
- Pod admission na Node-e,
- koordinácia container runtime,
- volume mount lifecycle,
- probes,
- container restart podľa Pod policy,
- Pod status updates,
- static Pods,
- image garbage collection coordination,
- eviction pri node pressure,
- cgroup/resource management podľa configuration.

Kubelet nescheduluje Pods medzi Nodes. Vykonáva Pods, ktoré mu boli pridelené alebo ktoré sú static Pods.

## 4. Node registration

Node môže byť do API pridaný:

- self-registration kubeletom,
- manuálne alebo bootstrap automation.

Kubelet potrebuje:

- cluster CA trust,
- client identity,
- API server endpoint,
- node name contract,
- authorization na Node a Pod operations,
- správnu runtime/network configuration.

Duplicitné alebo meniace sa node names môžu vytvoriť nejasnú identity a orphan Node objects.

## 5. Node status

Dôležité oblasti:

- `addresses`,
- `conditions`,
- `capacity`,
- `allocatable`,
- system info,
- images podľa API/reporting behavior.

Príkazy:

```bash
kubectl get nodes -o wide
kubectl describe node <node>
kubectl get node <node> -o yaml
```

`capacity` je hrubá kapacita. `allocatable` je časť dostupná pre Pods po odpočítaní system a kube reservations podľa konfigurácie.

## 6. Node conditions

Bežné conditions:

- `Ready`,
- `MemoryPressure`,
- `DiskPressure`,
- `PIDPressure`,
- `NetworkUnavailable` podľa implementácie.

Condition je reportovaný signál, nie kompletná root cause.

Príklad:

```text
Ready=False
```

môže znamenať kubelet heartbeat problém, runtime issue, network partition, certificate failure alebo node shutdown.

## 7. Heartbeats a Leases

Node availability sa sleduje cez:

- updates Node `.status`,
- Lease object v namespace `kube-node-lease`.

Lease poskytuje lightweight heartbeat s menším write overheadom.

Node controller v control plane vyhodnocuje heartbeats a pri ich absencii mení Node conditions a podľa policy spracúva Pods.

Network partition môže viesť k tomu, že workload na Node-e stále beží, ale control plane ho považuje za nedostupný.

## 8. kubelet configuration

Kubelet behavior ovplyvňujú napríklad:

- API/kubeconfig,
- CRI endpoint,
- cgroup driver,
- cluster DNS a domain,
- eviction thresholds,
- image garbage collection,
- authentication a authorization pre kubelet API,
- certificate rotation,
- reserved resources,
- max Pods,
- static Pod path,
- feature gates podľa verzie.

Configuration má byť versionovaná a validovaná. Rozdiely medzi Nodes vytvárajú heterogénne runtime behavior.

## 9. Kubelet API

Kubelet exponuje API pre operations ako:

- logs,
- exec,
- attach,
- port-forward related streams,
- metrics/status podľa endpointu a configuration.

API server môže proxy-ovať niektoré requests ku kubeletu.

Kubelet API je citlivá node-level trust boundary. Anonymous alebo broad authorization môže viesť k workload alebo node compromise.

## 10. Container Runtime Interface — CRI

CRI je gRPC interface medzi kubeletom a container runtime implementation.

Hlavné časti:

- RuntimeService,
- ImageService.

Kubelet používa CRI na:

- Pod sandbox lifecycle,
- container create/start/stop/remove,
- image pull/list/remove,
- exec/attach/port-forward endpoints,
- status a stats.

Kubernetes worker node nepotrebuje Docker Engine. Používa CRI-compatible runtime, napríklad containerd alebo CRI-O podľa distribúcie.

## 11. Pod sandbox

Pod sandbox vytvára zdieľané runtime prostredie Podu, najmä network namespace a infra lifecycle.

Containers v jednom Pode typicky zdieľajú:

- network namespace,
- Pod IP,
- port space,
- localhost,
- volumes podľa mounts,
- IPC alebo process namespace iba podľa explicitnej konfigurácie.

Runtime môže používať infra/pause container ako držiteľa namespace lifecycle-u.

Ak sandbox creation zlyhá, application container sa nemusí vôbec vytvoriť.

## 12. containerd/CRI-O a OCI runtime

Zjednodušená vrstva:

```text
kubelet
  ↓ CRI
containerd / CRI-O
  ↓
OCI runtime
  ↓
container process
```

Runtime:

- spravuje image/content store,
- snapshots,
- sandbox a container metadata,
- volá OCI runtime,
- koordinuje logs a streaming endpoints podľa implementation.

OCI runtime vytvorí low-level process isolation, mounts, capabilities, seccomp a cgroups podľa generated runtime spec.

## 13. `crictl`

`crictl` je diagnostický CLI pre CRI.

Príklady:

```bash
crictl info
crictl ps -a
crictl pods
crictl images
crictl inspect <container-id>
crictl inspectp <pod-sandbox-id>
crictl logs <container-id>
```

Používaj správny runtime endpoint a rešpektuj node root privileges.

Docker CLI nemusí vidieť Kubernetes containers, ak Node nepoužíva Docker Engine ako backend.

## 14. CNI

Container Network Interface integruje Pod network setup.

CNI plugin pri Pod sandbox lifecycle typicky:

- vytvorí alebo nakonfiguruje interface,
- priradí IP,
- nastaví routes,
- pripojí namespace do node/cluster dataplane-u,
- vykoná cleanup pri delete.

Kubernetes definuje network expectations, ale konkrétny dataplane implementuje CNI solution.

CNI failure sa často prejaví ako:

```text
FailedCreatePodSandBox
```

## 15. Pod network requirements

Klasický Kubernetes network model očakáva, že Pods majú routovateľnú identity v cluster networku bez application-managed NAT medzi každou dvojicou Pods, hoci konkrétna implementation môže interne používať encapsulation, routing, eBPF alebo NAT na boundaries.

Node musí mať:

- správny Pod CIDR alebo IPAM contract,
- route/overlay connectivity,
- MTU,
- firewall pravidlá,
- DNS reachability,
- CNI config a binaries.

## 16. kube-proxy

`kube-proxy` je bežný node component implementujúci časť Service virtual IP modelu.

Môže programovať dataplane cez platform-specific modes, napríklad iptables alebo nftables podľa podporovanej konfigurácie.

Responsibilities:

- Service ClusterIP/port forwarding,
- EndpointSlice-derived backend rules,
- NodePort handling,
- session affinity podľa modelu.

Niektoré CNI/eBPF platforms nahrádzajú kube-proxy alternate Service dataplane-om. Preto neprítomnosť kube-proxy nemusí byť chyba, ak architektúra používa náhradu.

## 17. Service dataplane vs. Pod networking

Rozlišuj:

- CNI/Pod networking — Pod IP a Pod-to-Pod connectivity,
- Service dataplane — virtual Service IP/port na backends,
- DNS — name-to-Service discovery,
- ingress/gateway — external/application routing.

Pod-to-Pod môže fungovať, ale ClusterIP nemusí, ak je poškodený Service dataplane.

## 18. CSI node component

Container Storage Interface node plugin môže vykonávať:

- stage/unstage volume,
- publish/unpublish volume do Pod pathu,
- mount operations,
- filesystem setup,
- node capability reporting.

Control-plane CSI controller a node plugin majú odlišné responsibilities.

Volume attach môže byť úspešný v cloud API, ale node mount môže zlyhať kvôli filesystemu, device pathu, credentials alebo pluginu.

## 19. Device plugins

Device plugin umožňuje Nodes reportovať a prideľovať špeciálne devices, napríklad GPU.

Node-level responsibilities:

- device discovery,
- health reporting,
- allocation instructions,
- runtime device mounts/environment.

Scheduler rozhoduje podľa advertised resources a requests, ale samotné device setup vykonávajú node components/runtime.

## 20. Cgroups a resource enforcement

Scheduler používa resource requests na placement. Node runtime/kubelet používajú limits a QoS policy na enforcement.

Node musí mať konzistentný cgroup model medzi:

- systemd/kernel,
- kubelet,
- container runtime.

Cgroup driver mismatch alebo nekompatibilná configuration môže spôsobiť Node startup alebo resource-accounting problémy.

## 21. CPU

Node-level CPU behavior zahŕňa:

- requests pre scheduling/share,
- limits a CFS quota/throttling podľa platformy,
- CPU manager policy pre pinned CPUs,
- host contention,
- steal time vo VM,
- system reserved workloads.

Pod môže mať nízky CPU utilization a stále vysokú latency kvôli throttlingu alebo single-thread saturation.

## 22. Memory

Memory limit môže viesť ku cgroup OOM kill.

Rozlišuj:

- container cgroup OOM,
- Pod-level behavior podľa cgroup hierarchy/features,
- host-wide OOM,
- kubelet eviction pri MemoryPressure,
- application self-termination.

`OOMKilled=true` je silný signál, ale root cause potrebuje memory metrics, limits, working set a kernel/runtime evidence.

## 23. PID pressure

Každý process/thread spotrebúva PID namespace/host resources.

Node môže reportovať `PIDPressure` pri nedostatku PIDs.

Riziká:

- fork bomb,
- zombie processes,
- application leak,
- príliš veľa containers,
- nízke pid limits.

Symptómy môžu vyzerať ako náhodné zlyhania process creation.

## 24. Disk pressure a storage vrstvy

Node storage spotrebúva:

- container images,
- writable layers,
- container logs,
- emptyDir volumes,
- runtime metadata,
- kubelet state,
- CNI/CSI logs,
- OS logs.

Sleduj bytes aj inodes.

Kubelet môže vykonať image/container garbage collection alebo Pod eviction pri pressure. GC nie je náhrada capacity planningu a log rotation.

## 25. Image pull

Kubelet/runtime posudzuje:

- image reference,
- `imagePullPolicy`,
- local cache,
- registry authentication,
- platform manifest,
- network/DNS/TLS,
- disk capacity.

Typické statuses:

- `ErrImagePull`,
- `ImagePullBackOff`.

Mutable tag a cached image môžu viesť k rozdielnym digests medzi Nodes podľa pull policy a timing. Production artifacts majú mať kontrolovanú identity.

## 26. Container logs

Kubernetes logging model typicky očakáva application output na stdout/stderr.

Kubelet/runtime zabezpečuje local log files a rotation podľa configuration.

`kubectl logs` číta logs cez API server/kubelet path.

Riziká:

- local disk exhaustion,
- log loss po Node failure,
- multiline parsing,
- secret leakage,
- rotation bez central shippingu.

Node log collector je add-on, nie automatická trvalá vlastnosť Kubernetes.

## 27. Probes

Kubelet vykonáva:

- startup probes,
- liveness probes,
- readiness probes.

Dôsledky:

- liveness failure môže viesť k container restartu,
- readiness failure odstráni Pod z ready endpointov,
- startup probe môže odložiť liveness/readiness počas inicializácie.

Probe execution patrí kubeletu, ale endpoint/command implementuje application/image.

## 28. Container restart

Kubelet podľa Pod `restartPolicy` a workload state-u spúšťa container znovu v tom istom Pode.

To nie je vytvorenie nového Podu.

```text
container restart
→ rovnaký Pod UID, Pod IP a volumes môžu zostať

Pod replacement
→ nový Pod UID a typicky nová Pod IP
```

CrashLoopBackOff je backoff behavior pri opakovanom container failure, nie samostatná Pod phase.

## 29. Static Pods

Kubelet môže sledovať local static Pod manifests.

Vlastnosti:

- viazané na konkrétny Node,
- nie sú spravované bežným workload controllerom,
- kubelet ich reštartuje podľa local manifestu,
- API môže obsahovať mirror Pod.

Pri static Pod probléme kontroluj local manifest path a runtime, nie iba API object.

## 30. Eviction

Kubelet môže evictovať Pods pri node pressure podľa thresholds a QoS/priority pravidiel.

Signals:

- memory available,
- node filesystem/image filesystem capacity/inodes,
- PID availability.

Eviction nie je to isté ako cgroup OOM kill. Pri eviction Pod status/events zvyčajne reportujú dôvod a vyšší controller vytvorí replacement podľa desired state-u.

## 31. Graceful node shutdown

Pri podporovanej konfigurácii môže kubelet koordinovať Pod termination počas OS shutdownu.

Potrebné je:

- system manager integration,
- dostatočný shutdown budget,
- priority-aware ordering podľa policy,
- application graceful termination,
- workload controller replacement.

Hard power loss graceful flow neumožní.

## 32. Node maintenance

Bežný workflow:

```bash
kubectl cordon <node>
kubectl drain <node> --ignore-daemonsets --delete-emptydir-data
# maintenance
kubectl uncordon <node>
```

`cordon` zabráni novému scheduling-u.

`drain` používa eviction/delete workflow pre existing Pods podľa flags a policy.

Pred drainom over:

- PodDisruptionBudgets,
- local/emptyDir data,
- DaemonSets,
- unmanaged Pods,
- stateful storage,
- capacity na ostatných Nodes.

## 33. Node security

Chráň:

- OS a kernel,
- kubelet credentials,
- kubelet API,
- container runtime socket,
- CNI/CSI sockets a binaries,
- host filesystem,
- cloud instance identity/metadata,
- privileged Pods,
- device access,
- SSH/admin access,
- local logs a image credentials.

Node compromise môže umožniť čítanie memory, volumes alebo credentials workloadov na danom Node-e.

## 34. Taints pri node stave

Control plane môže pridať taints podľa Node conditions, napríklad pri unreachable/not-ready stave.

Taints ovplyvňujú scheduling a eviction podľa tolerations.

Node condition, taint a Pod eviction sú súvisiace, ale odlišné mechanisms.

## 35. Heterogénne Nodes

Cluster môže obsahovať Nodes s odlišnými:

- architecture,
- OS,
- kernel,
- runtime version,
- GPU/devices,
- zone/region,
- instance type,
- labels/taints,
- storage/network capabilities.

Workload potrebuje správne image manifests a scheduling constraints.

„Funguje na jednom Node-e“ nemusí znamenať cluster-wide kompatibilitu.

## 36. Observability

### Kubelet

Sleduj:

- health a startup,
- Pod sync latency/errors,
- runtime operation latency/errors,
- PLEG/runtime state podľa implementation,
- volume operation errors,
- probe failures,
- eviction signals,
- certificate rotation.

### Runtime

Sleduj:

- sandbox/container create failures,
- image pulls,
- snapshot/content storage,
- task exits,
- runtime daemon health.

### Node OS

Sleduj:

- CPU, memory, load,
- pressure stall information,
- disk bytes/inodes/latency,
- network errors/drops/MTU,
- conntrack,
- kernel OOM,
- filesystem a mount errors,
- clock a certificates.

## 37. Troubleshooting workflow

```text
Pod status/Event
→ Pod assigned Node?
→ Node Ready/conditions/taints
→ kubelet logs
→ CRI sandbox/container state
→ CNI network setup
→ CSI/mount state
→ image/content store
→ cgroups/resources
→ host kernel/network/storage
```

Príkazy:

```bash
kubectl get pod <pod> -o wide
kubectl describe pod <pod>
kubectl describe node <node>
crictl pods
crictl ps -a
journalctl -u kubelet
journalctl -u containerd
```

Service names a log paths sa líšia podľa distribúcie.

## 38. Typické zlyhania

### Node `NotReady`

Over heartbeat/Lease, kubelet, runtime, CNI, certificate, disk pressure a API connectivity.

### `FailedCreatePodSandBox`

Over runtime sandbox, CNI config/binaries, IPAM, network namespace, routes a disk.

### `ContainerCreating` dlho

Over image pull, volume attach/mount, Secret/ConfigMap projection, sandbox a runtime events.

### `CrashLoopBackOff`

Over previous logs, exit code, command, configuration, probes, permissions, dependencies a resource limits.

### `ImagePullBackOff`

Over image name/digest, credentials, registry DNS/TLS/network, rate limits, platform a disk.

### Pod evicted

Over Node pressure signals, requests/limits/QoS, local storage, logs a capacity trend.

### ClusterIP nefunguje len na jednom Node-e

Over kube-proxy/alternate dataplane, EndpointSlices, firewall, conntrack a node routes.

## 39. Anti-patterny

### Ručné spúšťanie workload containerov cez runtime CLI

Kubelet ich nepozná a nereconcile-uje.

### Docker CLI ako jediný node diagnostic tool

Node môže používať containerd/CRI-O bez Docker Engine-u.

### Restart kubeletu ako prvý krok

Môže odstrániť evidence a spustiť ďalšie reconciliation bez root cause.

### `chmod 777` pri volume probléme

Maskuje UID/GID, SELinux alebo mount policy problém.

### Disable probes alebo security controls bez analýzy

Odstráni symptom, nie príčinu.

### Všetky Nodes bez reservations a eviction planningu

System daemons súťažia s Pods a Node môže destabilizovať.

## 40. Kontrolné otázky

1. Aký je rozdiel medzi Node objektom a reálnym worker serverom?
2. Aké hlavné responsibilities má kubelet?
3. Čo rieši CRI?
4. Čo je Pod sandbox?
5. Aký je rozdiel medzi CNI a kube-proxy/Service dataplane-om?
6. Ako sa líši container restart a Pod replacement?
7. Čo znamená `allocatable`?
8. Aký je rozdiel medzi OOM kill a kubelet eviction?
9. Prečo Node Lease existuje popri Node status updates?
10. Ako diagnostikuješ `FailedCreatePodSandBox`?

## Glossary impact

Relevantné pojmy: Kubernetes Node, Node capacity, Node allocatable, Node condition, node heartbeat, Node Lease, kubelet, kubelet API, Container Runtime Interface, RuntimeService, ImageService, Pod sandbox, pause container, CRI runtime, `crictl`, CNI, kube-proxy, Service dataplane, CSI node plugin, device plugin, cgroup driver, Node pressure, kubelet eviction, image garbage collection, static Pod mirror, cordon, drain a graceful node shutdown.

## Oficiálna dokumentácia

- [Nodes](https://kubernetes.io/docs/concepts/architecture/nodes/)
- [Kubernetes components](https://kubernetes.io/docs/concepts/overview/components/)
- [Node status](https://kubernetes.io/docs/reference/node/node-status/)
- [Container Runtime Interface](https://kubernetes.io/docs/concepts/architecture/cri/)
- [Installing and using crictl](https://kubernetes.io/docs/tasks/debug/debug-cluster/crictl/)
- [Node-pressure eviction](https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/)
- [Safely drain a Node](https://kubernetes.io/docs/tasks/administer-cluster/safely-drain-node/)
- [Communication between Nodes and control plane](https://kubernetes.io/docs/concepts/architecture/control-plane-node-communication/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Control plane components](control-plane-components.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Pod →](pod.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
