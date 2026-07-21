# Kubernetes architecture

Kubernetes je API-driven platforma na deklaratívne riadenie containerized workloads a súvisiacich resources. Cluster tvorí **control plane**, ktorý uchováva a vyhodnocuje požadovaný stav, a jeden alebo viac **worker nodes**, ktoré spúšťajú Pods. Kubernetes nie je iba vzdialený wrapper nad `docker run`; jeho jadrom je versionovaný object model, distribuované control loops a oddelenie rozhodovania od samotného vykonania workloadu.

## 1. Problém, ktorý Kubernetes rieši

Pri väčšom počte containerov nestačí vedieť ich iba spustiť. Platforma musí riešiť:

- na ktorom stroji workload pobeží,
- ako sa nahradí po zlyhaní,
- ako sa vykoná rollout novej verzie,
- ako sa workload identifikuje v sieti,
- ako dostane configuration, secrets a storage,
- ako sa riadia CPU a memory resources,
- ako sa presadzujú security a tenancy pravidlá,
- ako sa pozoruje požadovaný a aktuálny stav,
- ako sa platforma rozširuje o nové resource types a controllers.

Kubernetes tieto problémy rieši pomocou spoločného API a sady komponentov, ktoré reagujú na objekty uložené v API serveri.

## 2. Základný mentálny model

```text
používateľ / CI / controller
            ↓
      Kubernetes API
            ↓
       desired state
            ↓
 controllers + scheduler
            ↓
      node agents/runtime
            ↓
      running workloads
            ↑
        observed state
```

Používateľ typicky nehovorí platforme presnú sekvenciu shell príkazov. Vytvorí objekt, ktorý vyjadruje intent. Control loops potom priebežne približujú aktuálny stav požadovanému.

## 3. Cluster

Kubernetes cluster je logická platformová jednotka pozostávajúca z:

- control plane components,
- worker nodes,
- cluster network,
- storage integrations,
- identity a policy vrstiev,
- add-ons ako DNS, metrics alebo ingress/gateway implementation.

Cluster boundary ovplyvňuje:

- blast radius,
- tenancy,
- upgrade lifecycle,
- API availability,
- network a identity trust,
- operational ownership,
- compliance a data residency.

Cluster nie je automaticky security boundary vhodná pre všetky nedôveryhodné tenants. Izolácia závisí aj od node, runtime, network, RBAC, admission a workload security controls.

## 4. Control plane a worker plane

### Control plane

Control plane:

- exponuje Kubernetes API,
- autentifikuje a autorizuje requests,
- vykonáva admission,
- persistuje cluster state,
- plánuje nescheduled Pods,
- spúšťa controllers,
- koordinuje cluster-wide decisions.

### Worker nodes

Worker node:

- prijíma Pod assignments,
- pripravuje container images, namespaces, cgroups a mounts,
- spúšťa containers cez runtime,
- reportuje Node a Pod status,
- implementuje lokálnu service networking vrstvu podľa cluster architektúry,
- poskytuje compute, memory, network a local storage resources.

Control plane rozhoduje, **čo a kde** má bežať. Node components zabezpečujú, **že pridelený workload reálne beží**.

## 5. API-centric architektúra

Kubernetes API server je centrálny komunikačný hub.

Typické princípy:

- clients komunikujú s API serverom,
- controllers sledujú a menia objekty cez API,
- scheduler zapisuje binding/assignment rozhodnutia cez API,
- kubelet sleduje Pods pridelené svojmu node-u a zapisuje status,
- ostatné control plane components typicky neexponujú všeobecné vzdialené API pre nodes.

Tento model znižuje počet priameho component-to-component coupling-u a poskytuje spoločnú vrstvu pre:

- authentication,
- authorization,
- admission,
- audit,
- validation,
- object versioning,
- watch streams.

## 6. Hlavné komponenty

```text
Control plane
├─ kube-apiserver
├─ etcd
├─ kube-scheduler
├─ kube-controller-manager
└─ cloud-controller-manager (voliteľný)

Worker node
├─ kubelet
├─ container runtime
├─ network implementation / CNI
└─ kube-proxy alebo alternatívna service dataplane implementácia
```

Nie všetky distribúcie používajú identickú implementáciu dataplane-u alebo packaging. API contract však zostáva hlavnou integračnou hranicou.

## 7. Request flow pri vytvorení workloadu

Zjednodušený príklad:

```bash
kubectl apply -f deployment.yaml
```

Flow:

1. `kubectl` načíta kubeconfig a vyberie cluster/context/user.
2. Klient serializuje objekt a odošle request na `kube-apiserver`.
3. API server overí authentication.
4. Authorization rozhodne, či identita môže vykonať danú operáciu.
5. Mutating admission môže objekt doplniť alebo zmeniť.
6. Schema/defaulting/validation overia výsledný objekt.
7. Validating admission môže request povoliť alebo odmietnuť.
8. API server uloží objekt do etcd.
9. Controllers cez list/watch zistia nový desired state.
10. Deployment controller vytvorí alebo upraví ReplicaSet.
11. ReplicaSet controller vytvorí Pods.
12. Scheduler vyberie vhodný Node pre nescheduled Pods.
13. Kubelet na danom Node-e zistí assignment.
14. Kubelet cez container runtime a network/storage plugins pripraví Pod.
15. Kubelet a ďalšie components zapisujú status späť do API.

Jedna user operácia teda spustí viac nezávislých control loops.

## 8. etcd a persistentný cluster state

`etcd` je konzistentný distributed key-value store používaný ako backing store pre Kubernetes API data.

Obsahuje napríklad:

- object specs a metadata,
- statuses,
- RBAC resources,
- Secrets v API reprezentácii,
- leases,
- cluster configuration objects.

Kritické pravidlá:

- API server je štandardná brána k etcd,
- etcd availability a latency priamo ovplyvňujú control plane,
- backup musí byť testovaný obnovou,
- encryption at rest pre citlivé API data musí byť explicitne nakonfigurovaná,
- pri HA topológii treba rozumieť quorum a failure domains.

etcd nie je application database pre bežné workloads.

## 9. Control loops

Controller:

1. pozoruje relevantné resources,
2. porovná desired a observed state,
3. vykoná alebo požiada o zmenu,
4. aktualizuje status alebo vytvorí dependent objects,
5. proces opakuje.

Príklad:

```text
Deployment spec: replicas = 3
Observed Pods: 2
ReplicaSet controller: vytvorí ďalší Pod
```

Control loops sú navrhnuté tak, aby tolerovali opakovanie, oneskorenie a súbežné zmeny. Výsledok nemusí vzniknúť okamžite po prijatí API requestu.

## 10. Scheduler a execution sú oddelené

`kube-scheduler`:

- hľadá Pods bez prideleného node-u,
- filtruje nevhodné Nodes,
- skóruje kandidátov,
- vyberie Node,
- zaznamená assignment.

Scheduler nespúšťa container. To vykonáva kubelet na vybranom Node-e.

Toto oddelenie je dôležité pri diagnostike:

```text
Pod Pending + bez nodeName
→ scheduling problém

Pod assigned + ContainerCreating
→ node/runtime/network/storage problém
```

## 11. Node execution flow

Keď je Pod pridelený Node-u:

1. kubelet získa Pod spec,
2. overí local admission a resource podmienky,
3. pripraví potrebné volumes,
4. požiada runtime o image pull a sandbox/container lifecycle,
5. network plugin pripraví Pod networking,
6. spustia sa init containers a následne application containers,
7. kubelet vykonáva probes a lifecycle actions,
8. reportuje Pod status a Node heartbeats.

Presné interné poradie sa môže líšiť podľa runtime, pluginov a Pod specu, ale ownership jednotlivých vrstiev zostáva diagnosticky dôležitý.

## 12. Add-ons

Bežné add-ons alebo platformové služby:

- cluster DNS,
- metrics pipeline,
- ingress controller alebo Gateway API implementation,
- network policy implementation,
- storage CSI drivers,
- log collection,
- policy engines,
- certificate management,
- autoscaling components.

Add-on môže používať Kubernetes API, ale nie je automaticky súčasťou core control plane-u.

Pri probléme vždy rozlišuj:

- upstream Kubernetes component,
- distribution-specific component,
- managed-service integration,
- third-party add-on.

## 13. Extensibility

Kubernetes sa rozširuje cez:

- CustomResourceDefinitions,
- custom controllers/operators,
- admission webhooks,
- aggregated API servers,
- CNI/CSI/CRI integrations,
- scheduler plugins alebo alternate schedulers,
- device plugins,
- cloud provider integrations.

Rozšírenie musí rešpektovať API a reconciliation model. Custom resource bez controlleru je iba uložený intent bez automatizácie, pokiaľ ho nespracúva iný systém.

## 14. High availability

HA control plane typicky zahŕňa:

- viac API server instances za load balancerom,
- redundantný etcd cluster s quorum,
- viac scheduler/controller-manager instances,
- leader election pre components, ktoré majú mať jedného aktívneho leadera,
- rozloženie naprieč failure domains,
- zálohovanie a obnovu,
- monitoring certificates, latency, capacity a quorum health.

Viac replík bez nezávislých failure domains neposkytuje plnú dostupnosť. Tri control plane VMs na jednom fyzickom hoste nezvládnu výpadok hosta.

## 15. Leader election

Niektoré replicated control plane components používajú Kubernetes `Lease` objects na voľbu aktívneho leadera.

Cieľ:

- viac instances môže byť pripravených,
- iba zvolená instance vykonáva leader-only control loop,
- pri zlyhaní leadership prevezme iná instance.

API server môže byť aktívny vo viacerých replicas súčasne, zatiaľ čo scheduler alebo controller-manager typicky koordinujú leadership pre príslušné loops.

## 16. Failure domains

Rozlišuj:

- process failure,
- Pod/static Pod failure,
- Node failure,
- availability-zone failure,
- network partition,
- API server failure,
- etcd quorum loss,
- registry failure,
- DNS failure,
- storage backend failure,
- certificate alebo identity failure.

Kubernetes môže nahradiť workload po Node failure, ale nevyrieši automaticky:

- stratu jediného persistent volume-u,
- application-level split brain,
- nedostupný registry pri chýbajúcom local image,
- chybné desired state,
- nekompatibilnú databázovú migration,
- vyčerpaný celý cluster.

## 17. Self-managed a managed Kubernetes

### Self-managed

Tím vlastní:

- control plane lifecycle,
- etcd,
- certificates,
- upgrades,
- node images,
- networking/storage integrations,
- backup a recovery.

### Managed control plane

Cloud provider typicky vlastní časť control plane prevádzky, ale zákazník stále rieši:

- workloads,
- RBAC a identities,
- network/security policy,
- node pools alebo compute profile,
- add-ons,
- data protection,
- version compatibility,
- cost a capacity.

„Managed“ neznamená bez prevádzkovej zodpovednosti.

## 18. Trust boundaries

Kritické hranice:

- API server endpoint,
- kubeconfig a client credentials,
- etcd data,
- kubelet API,
- node OS a container runtime,
- CNI/CSI plugins s host privileges,
- admission webhooks,
- controller service accounts,
- image registry a supply chain,
- cloud provider credentials.

Kompromitovaný Node môže ohroziť workloads a credentials dostupné na danom Node-e. Kompromitovaná privilegovaná control-plane identity môže mať cluster-wide dopad.

## 19. Network communication model

Kubernetes používa API-centric hub-and-spoke model:

- nodes a Pods komunikujú s API serverom,
- control plane components používajú API server,
- API server komunikuje s kubeletom pre niektoré control-plane-to-node operácie,
- cluster networking zabezpečuje Pod-to-Pod a Service connectivity podľa implementácie.

API connectivity, workload networking a Service dataplane sú tri odlišné troubleshooting vrstvy.

## 20. Static Pods

Static Pods sú spravované priamo kubeletom na konkrétnom Node-e z local manifestu alebo iného local source-u. API server nad nimi nemá rovnaký controller ownership ako nad bežnými workload Pods.

Časté použitie:

- self-hosted control plane components pri kubeadm-like topológii.

Kubelet môže vytvoriť mirror Pod objekt v API, ale authoritative manifest zostáva na Node-e. Úprava mirror Podu nie je správny spôsob zmeny static Podu.

## 21. Pozorovanie architektúry

Základné príkazy:

```bash
kubectl cluster-info
kubectl get nodes -o wide
kubectl get pods -A -o wide
kubectl get --raw /readyz?verbose
kubectl get events -A --sort-by=.metadata.creationTimestamp
kubectl api-resources
```

Podľa prístupu môžeš sledovať:

- API request latency a error rate,
- etcd latency, size a leader/quorum health,
- scheduler pending queue a scheduling latency,
- controller work queues a retries,
- Node heartbeats a Leases,
- kubelet/runtime errors,
- CNI/CSI failures,
- admission webhook latency a availability.

## 22. Typické zlyhania podľa vrstvy

### `kubectl` nevie kontaktovať cluster

Over context, DNS, routing, TLS, API load balancer a credentials.

### API request je `Forbidden`

API je dostupné; problém je authorization/RBAC alebo admission policy.

### Objekt vznikol, ale nič sa nedeje

Over controller availability, object conditions, events a dependent resources.

### Pod ostáva `Pending`

Over scheduling constraints, capacity, PVC binding a admission.

### Pod je assigned, ale nevznikne container

Over kubelet, runtime, image pull, CNI, CSI, mounts a Node conditions.

### Cluster API funguje, ale Service nie

Over Service/EndpointSlice, kube-proxy alebo alternate dataplane, DNS, CNI, network policy a application listen socket.

## 23. Časté omyly

### Kubernetes spúšťa Docker containers priamo

Kubernetes používa CRI-compatible container runtime. Docker Engine nie je povinnou worker-node vrstvou.

### Control plane spúšťa application process

Control plane rozhoduje a zapisuje desired/assigned state; kubelet a runtime vykonávajú workload na Node-e.

### Viac control plane replicas automaticky znamená HA

Potrebné sú quorum, load balancing, leader election, failure-domain separation a recovery.

### Kubernetes vždy obnoví aplikáciu

Obnoví iba to, čo je vyjadrené v API a čo dependencies/capacity umožňujú. Chybný spec bude Kubernetes spoľahlivo reprodukovať.

### Pod IP alebo Node je trvalá application identity

Workloads sú nahraditeľné; stabilita sa buduje vyššími abstractions ako Service, StatefulSet identity alebo external registry.

## 24. Rozhodovací rámec pre cluster boundary

Pýtaj sa:

1. Aký blast radius je prijateľný?
2. Ktoré teams alebo tenants si navzájom dôverujú?
3. Aký upgrade cadence a version policy potrebujú?
4. Aké network a data residency hranice existujú?
5. Kto vlastní control plane a nodes?
6. Aký je RPO/RTO pre API a etcd?
7. Aké add-ons a CRDs budú cluster-wide?
8. Koľko capacity a operational overheadu unesie platform team?
9. Je potrebná samostatná compliance alebo billing boundary?
10. Ako sa bude cluster bootstrapovať a obnovovať?

## 25. Kontrolné otázky

1. Aké dve hlavné časti tvorí Kubernetes cluster?
2. Prečo je API server centrálnym integračným bodom?
3. Aký je rozdiel medzi schedulerom a kubeletom?
4. Čo sa stane po `kubectl apply` workload manifestu?
5. Akú úlohu má etcd?
6. Prečo je Kubernetes architektúra založená na control loops?
7. Aký je rozdiel medzi core componentom a add-onom?
8. Prečo viac replík bez failure-domain separation nemusí znamenať HA?
9. Kedy sú relevantné static Pods?
10. Ako rozlíšiš API, scheduling, node-runtime a Service-networking problém?

## Glossary impact

Relevantné pojmy: Kubernetes cluster, control plane, worker node, API-centric architecture, cluster state, kube-apiserver, etcd, kube-scheduler, kube-controller-manager, cloud-controller-manager, kubelet, container runtime, cluster add-on, leader election, Lease, failure domain, managed control plane a static Pod.

## Oficiálna dokumentácia

- [Kubernetes components](https://kubernetes.io/docs/concepts/overview/components/)
- [Cluster architecture](https://kubernetes.io/docs/concepts/architecture/)
- [Communication between Nodes and the control plane](https://kubernetes.io/docs/concepts/architecture/control-plane-node-communication/)
- [Controllers](https://kubernetes.io/docs/concepts/architecture/controller/)
- [Leases](https://kubernetes.io/docs/concepts/architecture/leases/)
- [Static Pods](https://kubernetes.io/docs/concepts/workloads/pods/static-pods/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Docker troubleshooting](../08-container-fundamentals-and-docker/docker-troubleshooting.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: API a object model →](api-object-model.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
