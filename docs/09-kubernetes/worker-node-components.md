# Worker node components

Worker node nie je iba server, na ktorom „beží container“. Je to execution boundary, ktorá z prideleného Pod objectu vytvorí konkrétny sandbox, network identity, mounts, cgroups a processes, priebežne reportuje ich stav a pri termination alebo pressure vykoná cleanup či eviction.

Dominantný lifecycle tejto kapitoly:

```text
assigned Pod UID a immutable spec snapshot
→ kubelet observation a local admission
→ Node capacity, identity a dependency preflight
→ volume, device a projected-data príprava
→ CRI Pod sandbox
→ CNI network a Service-dataplane prerequisites
→ image resolution a container creation
→ init, sidecar a application execution
→ probes, cgroups, status a Node heartbeats
→ EndpointSlice a application-path verification
→ restart, termination, eviction, replacement a cleanup
```

Pri diagnostike sa nepýtaj iba „je Node Ready?“. Pýtaj sa:

```text
Ktorý Pod UID bol pridelený ktorému Node UID?
Ktorý node component vlastní ďalší transition?
Bol vytvorený sandbox, network, mount, image a process?
Ktorý reportovaný stav je ešte aktuálny a ktorý je stale?
Je poškodená iba execution vrstva, Service dataplane alebo celý Node?
```

## 1. Atlas node-execution subject

Atlas Payments release `4.2.0` vytvoril Pod:

```text
cluster: atlas-prod-eu1
Pod: production/payments-api-7d6f9d8b7b-k4m2p
Pod UID: P42
Pod template hash: 7d6f9d8b7b
assigned Node: atlas-worker-a7
Node UID: N7
image: registry.atlas.example/payments-api@sha256:4a20...
config generation: C52
secret epoch: SE08
service account: payments-api
expected port: 8443
```

Pôvodný outcome nie je iba `Running`. Potrebné je overiť:

- sandbox a Pod IP vznikli na Node `N7`;
- init krok dokončil prípravu konfigurácie;
- application process načítal digest, C52 a SE08;
- startup a readiness contract prešli;
- EndpointSlice obsahuje Pod UID `P42` ako ready backend;
- request cez Service vykoná payment authorization presne raz;
- žiadna staging dependency ani starý digest nie sú v active path-e.

## 2. Node object a reálny server sú odlišné subjects

`Node` object v API je reportovaný a controller-observed pohľad. Reálny worker je host s kernelom, kubeletom, runtime-om, network a storage plugins a lokálnym stavom.

```text
Node object
├─ metadata.name a UID
├─ labels, taints a addresses
├─ capacity a allocatable
├─ conditions a Lease heartbeat
└─ system/runtime information

reálny worker
├─ operating system a kernel
├─ kubelet a credentials
├─ CRI runtime a content/snapshot store
├─ CNI a Service dataplane
├─ CSI/device plugins
├─ cgroups, mounts a namespaces
└─ bežiace Pod sandboxy a processes
```

`Ready=True` môže byť krátkodobo stale. Naopak network partition môže ponechať processes bežať, hoci control plane označí Node ako nedostupný. Preto verdict vždy viaž na Node UID, heartbeat timeline a konkrétny execution subject.

## 3. Ownership jednotlivých transitionov

| Transition | Primárny vlastník | Typické evidence |
|---|---|---|
| Pod-to-Node assignment | scheduler/API binding | `.spec.nodeName`, scheduling Events |
| pridelený Pod zistený na Node | kubelet | Pod worker/sync logs, kubelet metrics |
| local admission | kubelet | allocatable, limits, admission reason |
| sandbox a containers | CRI runtime | `crictl`, runtime logs a metadata |
| Pod network | CNI/IPAM/dataplane | CNI result, namespace, interface, routes |
| volume mount | kubelet/CSI node plugin | attach/mount Events, device a mount state |
| image content | runtime/registry path | resolved digest, pull status, content store |
| probes a status | kubelet + application endpoint | probe results, Pod conditions |
| Service forwarding | kube-proxy alebo alternatívny dataplane | Service/EndpointSlice rules a packet flow |
| pressure eviction | kubelet | Node pressure signals, eviction Events |
| replacement na inom Node | workload controller + scheduler | nový Pod UID a assignment |

Komponent môže byť healthy ako process a stále neplniť konkrétnu capability. Napríklad kubelet môže posielať heartbeats, ale jeho runtime endpoint môže timeoutovať.

## 4. Assignment nie je execution

Scheduler ukončí svoju hlavnú úlohu zápisom Node assignmentu. Potom začína node lifecycle:

```text
Pod P42 bez nodeName
→ scheduler vyberie N7
→ API persistuje assignment
→ kubelet N7 pozoruje P42
→ local admission
→ dependencies a sandbox
→ containers
```

Dôležité rozlíšenie:

```text
Pod Pending bez nodeName
→ scheduling boundary

Pod má nodeName, ale sandbox nevznikol
→ worker-node boundary
```

Kubelet nesmie byť diagnostikovaný pre Pod, ktorý ešte nebol pridelený jeho Node-u.

## 5. Kubelet ako node reconciler

Kubelet priebežne porovnáva pridelené Pod specs s local runtime state-om. Jeho práca nie je jednorazový `run` príkaz.

```text
observe assigned Pods
→ reconstruct Pod execution subject
→ local admission a dependency checks
→ ensure sandbox, volumes a containers
→ run probes a lifecycle actions
→ report Pod a Node status
→ repeat pri evente, timeri alebo runtime zmene
```

Kubelet zabezpečuje najmä:

- Node registration, status a Lease heartbeats;
- synchronizáciu Pods pridelených Node-u;
- local admission proti Node capabilities a limits;
- CRI, volume a probe orchestration;
- container restart v rámci existujúceho Pod UID;
- pressure eviction a garbage collection;
- static Pod lifecycle podľa local authority.

Kubelet však nevytvára náhradný Pod na inom Node-e. To je úloha vyššieho controlleru a schedulera.

## 6. Node identity, bootstrap a configuration generation

Kubelet potrebuje stabilný contract:

```text
Node name + Node UID continuity
cluster CA a API endpoint
node/client identity
CRI endpoint
cgroup driver a hierarchy
CNI/CSI paths a versions
reserved resources a eviction policy
certificate rotation
```

Ak autoscaling alebo reprovisioning znovu použije meno pri inom hoste, tools nesmú zamieňať starú a novú Node inštanciu. Pri audite používaj aj provider ID, system UUID alebo inú platformovú identity podľa prostredia.

Node pool má mať versionovaný **node execution generation**, napríklad:

```text
image generation: NI27
kubelet config: KC14
runtime config: RC09
CNI generation: CN18
CSI generation: CS11
```

„Všetky Nodes sú Ready“ nepreukazuje, že používajú rovnakú generation.

## 7. Local admission a allocatable

`capacity` je fyzická alebo reportovaná hrubá kapacita. `allocatable` je časť dostupná pre Pods po rezerváciách pre OS a Kubernetes components.

Kubelet môže odmietnuť alebo nedokázať realizovať pridelený Pod kvôli:

- local resource alebo topology constraints;
- max Pods alebo PID limits;
- chýbajúcemu RuntimeClass/device capability;
- volume alebo mount preconditions;
- cgroup incompatibility;
- node pressure;
- policy implementovanej node vrstvou.

Scheduler rozhoduje z API-visible inputs. Kubelet rozhoduje z aktuálneho local state-u. Medzi nimi môže byť časový alebo capability rozdiel.

## 8. Volume, projected data a device preflight

Pred application štartom môže Node potrebovať:

```text
volume attachment
→ CSI node staging/publish
→ filesystem a mount options
→ ownership/SELinux relabeling
→ Secret/ConfigMap/projected token materialization
→ device allocation
→ container mount namespace
```

Failure boundaries:

- cloud disk je attached, ale node mount zlyhal;
- PVC je Bound, ale device alebo filesystem na Node-e nie je použiteľný;
- Secret existuje, ale kubelet ho nemôže načítať kvôli API alebo authorization problému;
- projected token vznikol, ale application načítala starý súbor alebo environment snapshot;
- device plugin resource bol schedulovateľný, ale device setup na Node-e zlyhal.

`ContainerCreating` preto nie je jedna príčina. Je to fáza s viacerými vlastníkmi.

## 9. CRI, sandbox a container runtime

CRI je gRPC contract medzi kubeletom a runtime-om. Zjednodušený chain:

```text
kubelet
→ CRI RuntimeService/ImageService
→ containerd, CRI-O alebo iný CRI runtime
→ OCI runtime
→ namespaces, mounts, capabilities, seccomp a cgroups
→ container process
```

Pod sandbox drží najmä spoločnú network identity Podu. Ak sandbox nevznikne, application containers ešte nemajú kde bežať.

Observation points:

```bash
crictl info
crictl pods
crictl ps -a
crictl inspectp <sandbox-id>
crictl inspect <container-id>
crictl logs <container-id>
```

Runtime CLI je observation tool, nie alternatívny workload manager. Ručne vytvorený container mimo kubelet contractu nebude controllerom považovaný za Pod repliku.

## 10. CNI a Pod network

CNI setup typicky vykoná:

```text
network namespace
→ interface
→ IPAM allocation
→ routes a MTU
→ node/overlay/routed dataplane
→ policy hooks
→ result späť runtime-u/kubeletu
```

Dve odlišné failure triedy:

```text
sandbox nemá Pod IP alebo route
→ CNI/IPAM/network setup

Pod IP funguje, ale ClusterIP nie
→ Service dataplane, EndpointSlice alebo policy
```

CNI `ADD` alebo cleanup môže mať unknown outcome. Po timeoute over namespace, IPAM lease, interface a routes pred slepým retry alebo ručným uvoľnením adresy.

## 11. Image resolution a runtime content

Runtime musí vyriešiť image reference na konkrétny platform manifest a digest, autentifikovať sa, stiahnuť chýbajúce blobs a pripraviť snapshot.

Failure boundaries:

- tag ukazuje na iný digest než release contract;
- Node má cached content a odlišnú pull policy;
- platform index nemá správnu architecture;
- registry DNS/TLS/auth funguje na jednom Node-e, nie na inom;
- image store má voľné bytes, ale nemá inodes;
- unpack alebo snapshot zlyhá po úspešnom pull-e.

Runtime evidence musí obsahovať effective `imageID`, nie iba pôvodný tag.

## 12. Init, sidecar a application execution

Kubelet a runtime realizujú ordering definovaný Pod lifecycle-om:

```text
sandbox a mounts ready
→ regular init containers postupne
→ supported sidecar semantics podľa Pod specu
→ application containers
→ startup/readiness/liveness evaluation
```

Jedna neukončená init úloha môže držať Pod mimo application execution. Sidecar môže spotrebovať resources, bindovať port, meniť localhost path alebo spomaľovať shutdown. Preto je Pod execution subject celý Pod, nie iba „main container“.

## 13. Probes, conditions a reportovaný stav

Kubelet vykonáva probes, ale probe target implementuje application alebo image.

```text
startup success
→ liveness aktivovaná
→ container process continuity

readiness success
→ container ready
→ Pod readiness + readiness gates
→ EndpointSlice eligibility
```

`Running` neznamená Ready. `Ready` neznamená, že Service dataplane alebo business path je správny. Status môže navyše krátkodobo zaostávať za runtime-om.

## 14. Resource enforcement a pressure

Rozlišuj tri mechanizmy:

```text
container cgroup limit
→ napríklad CPU throttling alebo cgroup OOM

Node pressure
→ kubelet eviction na uvoľnenie resources

host/kernel failure
→ host-wide OOM, disk alebo PID exhaustion
```

Príklad:

```text
host má 24 GiB free
Pod limit je 512 MiB
container prekročí svoj cgroup limit
→ OOMKilled
```

Voľná host memory nevylučuje cgroup-local OOM. Naopak evicted Pod nemusí mať `OOMKilled=true`.

Sleduj:

- CPU throttling a single-thread saturation;
- memory working set, limit a kernel OOM evidence;
- MemoryPressure, DiskPressure a PIDPressure;
- filesystem bytes, inodes a latency;
- image, writable-layer, log a `emptyDir` consumption;
- conntrack, packet drops a MTU;
- system reservations a noisy system daemons.

## 15. Node heartbeats, partitions a replacement

Node availability chain:

```text
kubelet Lease/Node status
→ Node controller observation
→ Ready/Unknown condition a taints
→ Pod eviction/replacement policy
→ nový Pod UID na inom Node-e
```

Pri partition môže starý process stále bežať, zatiaľ čo control plane vytvorí replacement inde. Aplikácie so single-writer alebo exactly-once požiadavkou potrebujú external fencing, lease alebo idempotency; samotná Pod replacement logika nezaručuje, že starý process prestal konať.

## 16. Service dataplane na Node-e

Pod-to-Pod connectivity, DNS a Service forwarding sú samostatné vrstvy.

```text
client Pod
→ DNS name
→ Service VIP/port
→ node Service dataplane
→ EndpointSlice backend Pod IP
→ application listen socket
```

Kube-proxy alebo alternatívna implementácia môže byť poškodená iba na jednom Node-e. Potom:

- direct Pod IP funguje;
- ClusterIP z konkrétneho Node-u zlyháva;
- application a readiness môžu byť healthy;
- problém je node-local forwarding, conntrack, firewall alebo route state.

## 17. Termination, restart, eviction a replacement

Tieto operácie nie sú zameniteľné:

```text
container restart
→ rovnaký Pod UID a sandbox

Pod termination
→ graceful lifecycle a cleanup konkrétneho UID

kubelet eviction
→ ukončenie Podu kvôli Node pressure

controller replacement
→ nový Pod UID, často iný Node a IP
```

Node cleanup zahŕňa container stop/remove, unmount/unpublish, CNI delete a sandbox removal. Unknown alebo partial cleanup môže zanechať mount, IPAM, namespace alebo runtime metadata leak.

## 18. Maintenance a graceful node shutdown

Bezpečný maintenance flow:

```text
capacity a disruption preflight
→ cordon
→ drain cez eviction API
→ Pod shutdown a replacement verification
→ node maintenance
→ node execution-generation validation
→ uncordon
→ business-path verification
```

Pred drainom over PDB, DaemonSets, unmanaged Pods, local data, volume topology a voľnú kapacitu. Hard power loss neumožní graceful shutdown ani `preStop`.

## 19. Node security boundary

Kompromitovaný Node môže ohroziť workloads a credentials dostupné na danom hoste. Chráň najmä:

- kubelet a bootstrap credentials;
- kubelet API authorization;
- runtime, CNI a CSI sockets;
- host filesystem a kernel;
- cloud instance identity;
- image pull credentials;
- privileged Pods, host namespaces, devices a hostPath;
- local logs, crash dumps a projected secrets.

Read-only prístup k runtime socketu nemusí byť neškodný, ak API umožňuje privileged operations alebo čítanie workload state-u.

## 20. Worked failure: Node je Ready, runtime však neprijíma nové sandboxy

Node `N7` obnovuje Lease a `Ready=True`, ale všetky nové Pods na ňom zostávajú v `ContainerCreating`.

Mechanizmus:

```text
kubelet process a API connectivity healthy
→ Lease updates pokračujú
→ runtime metadata database alebo socket je stuck
→ CRI RunPodSandbox timeoutuje
→ Pod sandbox nevznikne
→ Node môže zostať Ready
```

`Ready=True` preto nie je dôkaz všetkých execution capabilities. Recovery musí obnoviť runtime capability a následne overiť nové sandbox create/delete, nie iba restartovať kubelet.

## 21. Worked failure: cgroup OOM bol zamieňaný za Node MemoryPressure

Pod `P42` mal memory limit `512Mi`, host mal voľnú memory a Node nemal `MemoryPressure`. Process bol opakovane `OOMKilled`.

```text
application working set > 512Mi
→ cgroup-local OOM
→ container termination
→ kubelet restart podľa policy
→ CrashLoopBackOff
```

Zvýšenie Node size bez zmeny Pod limitu by problém nevyriešilo. Potrebná je application memory analýza a review request/limit contractu.

## 22. Worked failure: Service nefunguje iba z jedného Node-u

Payments Pods boli Ready a direct Pod IP fungovalo. Requesty z Node `N9` cez ClusterIP timeoutovali, z ostatných Nodes nie.

```text
Service a EndpointSlice correct
+ backend Pod listen correct
+ Pod network route correct
→ node-local Service rule alebo conntrack state na N9 poškodený
```

Restart application Podov by iba menil backends. Recovery patrí do Service-dataplane boundary na `N9` a musí overiť forward aj reverse path.

## 23. Causal troubleshooting walkthrough: Pod je assigned, ale application container nevznikne

Pod `P42` je 12 minút v `ContainerCreating` na `N7`. Sesterský Pod rovnakej revision na `N6` je Ready.

### 1. Zafixuj subject a pôvodný outcome

Zaznamenaj:

```text
cluster endpoint a CA
Pod namespace/name/UID/resourceVersion
Pod template hash a effective admitted spec
assigned Node name/UID/provider identity
Node execution generations NI/KC/RC/CN/CS
image digest a platform
volume/PVC/attachment IDs
C52 a SE08 projected-data subjects
sandbox/container IDs, ak existujú
CNI request/IPAM identity
required Service a business outcome
```

### 2. Competing hypotheses

1. Pod je v skutočnosti pridelený inému Node-u alebo starej Node inštancii s rovnakým menom.
2. Kubelet nepozoroval najnovší Pod resourceVersion.
3. Local admission odmietlo Pod kvôli resources, max Pods alebo RuntimeClass.
4. Volume attach prešiel, ale CSI node mount zlyhal.
5. Kubelet nevie načítať Secret alebo projected data.
6. CRI runtime je nedostupný alebo jeho content/snapshot store je poškodený.
7. Sandbox vznikol, ale CNI `ADD` zlyhal alebo má unknown outcome.
8. Image pull, platform selection alebo unpack zlyhal.
9. Init container opakovane zlyháva; application container preto ešte nemal vzniknúť.
10. Node má disk/inode/PID pressure bez správne reportovanej condition.
11. Admission alebo mutating webhook vytvorili Node-incompatible effective spec.
12. Sesterský Pod používa iný digest, config alebo node generation.

### 3. Discriminating observation points

- live Pod `nodeName`, UID, conditions, init/container statuses a Events;
- Node UID, provider ID, Lease age, conditions, allocatable a taints;
- kubelet logs korelované podľa Pod UID;
- `crictl pods`, `inspectp`, `ps -a` a runtime logs;
- sandbox/network namespace/interface/IPAM lease;
- CSI node plugin logs, device, mount table a filesystem evidence;
- effective image reference a runtime `imageID`;
- filesystem bytes, inodes, PID a kernel logs;
- admitted Pod spec vs. sesterský Pod;
- Node execution-generation rozdiel medzi N7 a N6.

Observation `Pod má nodeName` vylučuje základnú scheduler boundary. Observation `sandbox ID neexistuje` posúva diagnózu pred application start a probe vrstvu.

### 4. Containment

- zastav scheduling ďalších Pods na N7 cez cordon, ak failure scope nie je známy;
- nereštartuj naraz kubelet, runtime, CNI a CSI;
- zachovaj kubelet/runtime/plugin logs, Events a namespace/mount state;
- nevytváraj containers ručne mimo kubeletu;
- neuvoľňuj IPAM alebo detach volume bez overenia ownershipu;
- ponechaj zdravé replicas a traffic na N6/N8.

### 5. Recovery podľa boundary

- stale/wrong Node identity → odstráň bootstrap/name collision a znovu registruj správny subject;
- local capacity/config → oprav node generation alebo reschedule na compatible Node;
- CSI mount → oprav device/filesystem/plugin a dokonči idempotentný publish;
- projected data → obnov API/authorization path a recreate Pod, ak process snapshot musí byť nový;
- CRI/runtime → obnov runtime store/socket a over sandbox create/remove;
- CNI unknown outcome → lookup podľa Pod UID/container ID, oprav alebo cleanup-ni presný lease/interface a retry;
- image → oprav digest/platform/auth/disk a over effective imageID;
- init failure → oprav init contract, nie application probe.

### 6. Over pôvodný outcome

Potvrď:

- Pod P42 alebo jeho reviewovaný replacement má správny Node a UID chain;
- sandbox, Pod IP, routes, mounts a image digest sú správne;
- init containers skončili úspešne;
- application process načítal C52 a SE08;
- Pod je Ready a EndpointSlice odkazuje na správny UID;
- payment authorization cez Service prejde presne raz;
- N7 zvládne ďalší canary sandbox create/delete bez leakov;
- žiadna stará IPAM lease, mount alebo sandbox metadata nezostala.

### 7. Posuň control skôr

Pridaj:

- versionovaný node execution manifest a drift report;
- canary Pod pre CRI/CNI/CSI capability po node bootstrap/upgrade;
- alerts na sandbox, mount a image operation latency;
- disk bytes/inodes/PID a cgroup-specific observability;
- immutable digest a platform preflight;
- Node UID/provider-ID koreláciu;
- cordon-before-repair runbook s evidence-preservation krokom.

## 24. Observation matrix

| Boundary | Subject | Kľúčové observations |
|---|---|---|
| Assignment | Pod UID, Node UID | nodeName, Events, binding |
| Kubelet | Pod UID, KC generation | sync logs, local admission, status writes |
| Runtime | sandbox/container ID, RC generation | CRI calls, task state, content/snapshot store |
| Network | Pod UID/IPAM/CN generation | namespace, interface, routes, MTU, policy |
| Storage | volume/device/CS generation | attach, stage/publish, mount, filesystem |
| Image | manifest/digest/platform | pull, imageID, unpack, disk/inodes |
| Resources | Pod cgroup, Node pressure | throttling, OOM, eviction, PID/disk signals |
| Service path | Service/EndpointSlice + Node dataplane | VIP rules, conntrack, forward/reverse packets |
| Business | request/operation ID | SLI, downstream audit, exactly-once invariant |

## 25. Referenčné diagnostické príkazy

```bash
kubectl get pod <pod> -n <namespace> -o wide
kubectl get pod <pod> -n <namespace> -o yaml
kubectl describe pod <pod> -n <namespace>
kubectl get node <node> -o yaml
kubectl describe node <node>
kubectl get lease -n kube-node-lease <node> -o yaml
crictl info
crictl pods
crictl ps -a
journalctl -u kubelet
journalctl -u containerd
```

Názvy services, paths a runtime tooling závisia od distribúcie. Príkaz je observation point, nie diagnóza.

## 26. Referenčné pravidlá

- Node object a reálny host sú odlišné subjects.
- Assignment nie je sandbox ani process execution.
- `Ready=True` nepreukazuje každú node capability.
- Kubelet reconcile-uje pridelené Pods; nescheduluje ich medzi Nodes.
- CRI, CNI, CSI a Service dataplane majú odlišné ownership boundaries.
- Pod sandbox failure nastáva pred application-container troubleshootingom.
- Effective image identity je digest a runtime `imageID`, nie mutable tag.
- Container restart, Pod eviction a controller replacement sú odlišné transitions.
- Voľná host memory nevylučuje cgroup-local OOM.
- PVC `Bound` nepreukazuje úspešný node mount.
- Network partition môže ponechať starý process aktívny po replacement-e.
- Recovery musí overiť cleanup aj pôvodný Service/business outcome.

## 27. Kontrolné otázky

1. Aký lifecycle spája Pod assignment s business-ready application processom?
2. Prečo Node `Ready=True` nemusí preukazovať funkčný CRI runtime?
3. Ako odlíšiš scheduling failure od worker-node failure?
4. Aký je rozdiel medzi Pod sandboxom a application containerom?
5. Ako sa líši CNI Pod networking od Service dataplane-u?
6. Prečo PVC `Bound` neznamená, že mount na Node-e prešiel?
7. Ako odlíšiš cgroup OOM, host OOM a kubelet eviction?
8. Čo treba zachovať pred restartom kubeletu alebo runtime-u?
9. Ako môže network partition vytvoriť dva aktívne application processes?
10. Čo musí node recovery verdict overiť?

## Glossary impact

Relevantné pojmy: assigned-Pod execution subject, Node execution generation, kubelet reconciliation subject, local admission boundary, Pod sandbox subject, CRI capability subject, CNI/IPAM operation subject, CSI node-publish subject, effective image identity, node capability verdict, node pressure subject, Service dataplane subject, partitioned-node execution, worker-node observation matrix a node recovery verdict.

## Oficiálna dokumentácia

- [Nodes](https://kubernetes.io/docs/concepts/architecture/nodes/)
- [Kubernetes components](https://kubernetes.io/docs/concepts/overview/components/)
- [Container Runtime Interface](https://kubernetes.io/docs/concepts/containers/cri/)
- [Installing and using crictl](https://kubernetes.io/docs/tasks/debug/debug-cluster/crictl/)
- [Node-pressure eviction](https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/)
- [Safely drain a Node](https://kubernetes.io/docs/tasks/administer-cluster/safely-drain-node/)
- [Communication between Nodes and the control plane](https://kubernetes.io/docs/concepts/architecture/control-plane-node-communication/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Control plane components](control-plane-components.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Pod →](pod.md)
<!-- KNOWLEDGE-NAVIGATION:END -->