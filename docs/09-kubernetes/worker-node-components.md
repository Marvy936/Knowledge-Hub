# Worker node components

Worker Node je miesto, kde sa Kubernetes intent mení na Linux processes, network namespaces, mounts a cgroups. Control plane rozhodne, že Pod má bežať na konkrétnom Node-e, ale samotný Node musí ešte prijať Pod spec, pripraviť storage a network, stiahnuť image, spustiť containers, vykonávať probes a priebežne reportovať stav.

Pri `payments-api` sa budeme pozerať na Pod pridelený Node-u `worker-eu1-a-17`. Scheduler už zapísal `.spec.nodeName`, takže otázka „prečo Pod nebeží?“ sa presúva z placement vrstvy na kubelet, container runtime, CNI, CSI, host kernel a application process.

## Kubelet ako node agent

Kubelet sleduje cez API Pods pridelené jeho Node-u. Pre každý Pod zostaví lokálny desired runtime state a opakovane ho synchronizuje. Nečaká na jeden jednorazový „start command“. Ak container zlyhá a restart policy to povoľuje, kubelet ho spustí znova. Ak Pod objekt zmizne, kubelet odstráni lokálny runtime.

Základný pohľad z API:

```bash
kubectl get node worker-eu1-a-17 -o yaml
kubectl get pods -A --field-selector spec.nodeName=worker-eu1-a-17 -o wide
```

Node objekt obsahuje labels, taints, addresses, allocatable resources, conditions a system info. Je to control-plane pohľad na Node, nie úplný host diagnostic dump.

## Node registration a identita

Kubelet sa registruje pod Node menom a pravidelne obnovuje Lease. Node name musí byť stabilne previazané s host identity. Recyklovať meno pre nový machine lifetime bez jasného replacement procesu môže zmiešať starý a nový stav.

```bash
kubectl get node worker-eu1-a-17 \
  -o custom-columns='NAME:.metadata.name,UID:.metadata.uid,KERNEL:.status.nodeInfo.kernelVersion,RUNTIME:.status.nodeInfo.containerRuntimeVersion'
```

Node UID odlišuje nový objekt s rovnakým menom. V produkčnom inventári je vhodné korelovať Node UID s cloud instance ID, machine image generation, zone a node-pool revision.

## Kubelet prijme iba pridelené Pods

Scheduler zapíše Node assignment. Kubelet potom vyhodnotí lokálne podmienky: dostupné resources, volume limits, host ports, device availability a policy. Aj po úspešnom scheduling-u môže lokálna admission Pod odmietnuť, napríklad pre nedostatok ephemeral storage alebo chýbajúce zariadenie.

```bash
kubectl describe pod -n production <pod-name>
```

Ak Pod má Node assignment a Events pochádzajú od kubeletu, scheduler už nie je prvá chybná vrstva.

## Container Runtime Interface

Kubelet nepoužíva Docker Engine API. Komunikuje s CRI-compatible runtime-om, napríklad containerd alebo CRI-O. CRI oddeľuje Pod sandbox a jednotlivé containers.

Zjednodušený tok:

```text
kubelet SyncPod
→ RunPodSandbox
→ CNI pripraví network
→ PullImage podľa potreby
→ CreateContainer
→ StartContainer
→ ContainerStatus
```

Pod sandbox drží zdieľané runtime prvky Podu, najmä network namespace. Ak `RunPodSandbox` zlyhá, application container ešte nemusí existovať.

Node-local diagnostika podľa distribúcie často používa:

```bash
crictl pods
crictl ps -a
crictl inspectp <sandbox-id>
crictl inspect <container-id>
```

`crictl` musí smerovať na správny CRI socket. Výstup z nesprávneho runtime endpointu môže vyzerať ako „Pod neexistuje“.

## Image pull a content store

Runtime resolver vyberie platform manifest pre Node architecture, autentizuje sa voči registry, stiahne chýbajúce blobs a pripraví snapshot.

```text
image reference
→ registry resolution
→ platform manifest
→ blob download alebo local reuse
→ unpack/snapshot
→ container root filesystem
```

`ImagePullBackOff` je backoff stav po predchádzajúcich pull failures. Root cause môže byť neexistujúci digest, registry auth, DNS, TLS, rate limit, disk pressure alebo platform mismatch.

```bash
kubectl describe pod -n production <pod-name>
```

Event message je začiatok. Pri Node-specific chybe koreluj runtime logs, registry reachability a disk/inode stav na danom Node-e.

## CNI a Pod network

Po vytvorení sandboxu runtime alebo kubelet invokuje CNI plugin podľa implementácie. CNI pridelí Pod IP, vytvorí interfaces, routes a prípadné policy state.

```text
Pod sandbox network namespace
→ CNI ADD
→ IPAM allocation
→ veth alebo iný dataplane attachment
→ routes/policy
→ Pod IP reportovaný do statusu
```

Ak CNI ADD zlyhá, Pod môže zostať v `ContainerCreating` s `FailedCreatePodSandBox`. Reštart application containeru nepomôže, pretože process ešte nevznikol.

```bash
kubectl get pod -n production <pod-name> -o wide
kubectl describe pod -n production <pod-name>
```

Node-local CNI logs, IPAM state, routes a network namespace sú implementačne špecifické. Pred zásahom zachovaj Pod UID, sandbox ID a presný Node.

## CSI a volumes

Persistentné volumes môžu vyžadovať external provisioning, controller attach a node-stage/node-publish operácie. Kubelet koordinuje node-side mount cez CSI node plugin.

```text
PVC bound na PV
→ prípadný VolumeAttachment
→ CSI NodeStageVolume
→ CSI NodePublishVolume
→ mount v Pod namespace-e
```

`PVC Bound` preto neznamená, že volume je pripojený a mountnutý na cieľovom Node-e. Pri `FailedMount` alebo `FailedAttachVolume` sleduj PVC/PV identitu, VolumeAttachment, CSI controller, CSI node plugin a backend device state.

## Kube-proxy alebo alternatívny Service dataplane

Mnohé clustre používajú kube-proxy na programovanie Service rules cez iptables alebo IPVS. Iné implementácie používajú eBPF a kube-proxy nahrádzajú. Worker Node musí mať dataplane state zodpovedajúci Service a EndpointSlice objektom.

```text
Service/EndpointSlice watch
→ per-Node translation state
→ packet selection backendu
→ Pod network
```

Service objekt môže byť správny a EndpointSlice môže obsahovať ready Pod, ale jeden Node môže mať stale alebo partial dataplane. Preto pri intermittentných failures porovnávaj old a new Node generation, nie iba Kubernetes objekty.

## Probes a container lifecycle

Kubelet vykonáva startup, liveness a readiness probes. Readiness výsledok zapisuje do Pod conditions a ovplyvňuje EndpointSlice eligibility. Liveness môže reštartovať container. Startup probe odkladá liveness/readiness počas pomalého štartu.

```bash
kubectl get pod -n production <pod-name> \
  -o jsonpath='{.status.containerStatuses}' | jq .
```

Container `restartCount` patrí k jednému Pod UID. Nový Pod po replacement-e začne s novou históriou. Pri crash incidente používaj aj previous logs:

```bash
kubectl logs -n production <pod-name> -c api --previous
```

Ak container nikdy úspešne nezačal, previous logs nemusia existovať.

## Status report a Node conditions

Kubelet reportuje Node conditions ako `Ready`, `MemoryPressure`, `DiskPressure`, `PIDPressure` a `NetworkUnavailable` podľa platformy a komponentov. `Ready=True` neznamená, že všetky workloads na Node-e sú zdravé alebo že každý Service flow funguje.

```bash
kubectl get nodes
kubectl describe node worker-eu1-a-17
```

Node môže byť Ready, ale mať vysokú image filesystem latency, poškodenú jednu CNI mapu alebo problém iba s konkrétnym volume backendom.

## Resource accounting na Node-e

Scheduler používa requests a allocatable inventory. Kubelet a runtime nastavujú cgroups a sledujú local pressure. Reálny Node usage zahŕňa workload Pods, system daemons, kernel memory, image filesystem a eviction thresholds.

```bash
kubectl describe node worker-eu1-a-17
kubectl top node worker-eu1-a-17
kubectl top pod -A --field-selector spec.nodeName=worker-eu1-a-17
```

Metrics server poskytuje resource metrics, nie kompletné cgroup, PSI alebo disk diagnosis. Pri CPU throttling, OOM alebo inode exhaustion treba Node-local evidence.

## Eviction a graceful termination

Kubelet môže pri pressure evictovať Pods. Eviction vytvorí Pod failure a controller neskôr vytvorí replacement. Static alebo mirror Pods majú iný lifecycle. Node shutdown a drain používajú ďalšie mechanizmy.

```text
Node pressure
→ kubelet eviction decision
→ Pod termination
→ controller replacement
→ scheduler vyberie Node
```

Eviction nie je to isté ako container OOM. Pri OOM môže kubelet reštartovať container v tom istom Pode. Pri eviction Pod UID končí.

## Static Pods a node-local control

Static Pod manifests sleduje kubelet priamo z lokálneho zdroja. API server zobrazuje mirror Pod, ale desired state je na Node filesysteme, nie v bežnom API objekte.

To sa používa napríklad pri kubeadm control-plane komponentoch. `kubectl edit pod` mirror Pod neopraví; kubelet znovu realizuje lokálny manifest.

## Node logs a evidence

Pri worker-node incidente sa často hodia:

```text
kubelet logs
container runtime logs
CRI inspect
CNI/CSI node plugin logs
kernel journal a audit
cgroup/pressure/OOM evidence
mounts, devices a filesystem capacity
routes, rules, conntrack alebo eBPF state
```

Presné príkazy závisia od OS, runtime a platformy. Pred reštartom kubeletu alebo runtime-u zachovaj container IDs, sandbox ID, Pod UID, Node UID, timestamps a relevantný host state.

## Incident: Pod je Scheduled, ale container nevznikol

Nový `payments-api` Pod mal `PodScheduled=True` a Node assignment `worker-eu1-a-17`. Zostal však v `ContainerCreating`.

```bash
kubectl describe pod -n production <pod-name>
```

Events ukázali opakované `FailedCreatePodSandBox`. CNI plugin nedokázal prideliť IP, pretože lokálny IPAM state na jednom novom Node image bol inicializovaný s nesprávnym subnetom.

Scheduler bol funkčný a image nebol problém. Application logs neexistovali, pretože process sa nikdy nespustil. Containment vyradilo chybnú Node generation zo scheduling-u. Oprava vytvorila nový immutable Node image s opravenou CNI konfiguráciou. Recovery overila Pod sandbox, cross-Node traffic, Service path a forbidden NetworkPolicy flows.

## Incident: Node Ready, ale nové Pods padajú na disk

Node condition zostávala `Ready=True`, no nové image pulls a container creates zlyhávali. Root filesystem mal voľné gigabajty, ale image filesystem vyčerpal inodes.

Node-level `df -h` samotné nestačilo; `df -i`, runtime content-store inventory a kubelet eviction signals ukázali skutočný problém. Bezpečná remediation najprv zachovala evidence, potom odstránila nepoužívané content podľa platform policy a nakoniec nahradila driftujúci Node novou generation.

## Model, ktorý si treba odniesť

Scheduler končí Node assignmentom. Od tohto bodu kubelet, CRI runtime, CNI, CSI, Service dataplane a host kernel vytvárajú skutočný Pod runtime. Pri zlyhaní najprv urči, či vznikol sandbox, network, mount, image, container a process. Až potom diagnostikuj application readiness alebo business request.

## Referencie

- [Node Components](https://kubernetes.io/docs/concepts/overview/components/#node-components)
- [Nodes](https://kubernetes.io/docs/concepts/architecture/nodes/)
- [Container Runtime Interface](https://kubernetes.io/docs/concepts/architecture/cri/)
- [Debugging Kubernetes Nodes with crictl](https://kubernetes.io/docs/tasks/debug/debug-cluster/crictl/)
- [Node-pressure Eviction](https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Control plane components](control-plane-components.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Pod →](pod.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
