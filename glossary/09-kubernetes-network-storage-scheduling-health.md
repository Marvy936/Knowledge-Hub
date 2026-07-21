# Kubernetes network, storage, scheduling and health glossary entries

## Access mode — Kubernetes storage

PV/PVC contract opisujúci podporovaný spôsob mount accessu, napríklad ReadWriteOnce, ReadOnlyMany, ReadWriteMany alebo ReadWriteOncePod; nepredstavuje application-level locking ani databázový clustering. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Additive NetworkPolicy

Semantika, pri ktorej sa povolený traffic pre Pod skladá ako union pravidiel všetkých matching NetworkPolicies; neexistuje poradie pravidiel ani explicitné deny s vyššou prioritou v štandardnom API. Pozri [CNI a NetworkPolicy](docs/09-kubernetes/cni-networkpolicy.md).

## BestEffort QoS

Kubernetes QoS class pre Pod bez CPU a memory requests alebo limits podľa platných QoS calculation pravidiel; scheduler nemá deklarovanú potrebu a Pod je pri resource pressure typicky najzraniteľnejší. Pozri [Requests, limits a QoS](docs/09-kubernetes/requests-limits-qos.md).

## Binding — Kubernetes scheduling

Finálny scheduler krok zapisujúci vybraný Node do Podu; po bindingu kubelet na danom Node-e realizuje workload. Pozri [Scheduling](docs/09-kubernetes/scheduling.md).

## Burstable QoS

Kubernetes QoS class pre Pod, ktorý nie je Guaranteed a má aspoň niektorý relevantný CPU alebo memory request/limit. Pozri [Requests, limits a QoS](docs/09-kubernetes/requests-limits-qos.md).

## CNI

Container Network Interface specification a plugin contract používaný container runtime-om na vytvorenie, konfiguráciu a odstránenie Pod network interface-u. Pozri [CNI a NetworkPolicy](docs/09-kubernetes/cni-networkpolicy.md).

## CNI chaining

Model, v ktorom sa počas jedného Pod network setupu vykoná viac CNI plugins v poradí, napríklad connectivity, port mapping, tuning alebo bandwidth policy. Pozri [CNI a NetworkPolicy](docs/09-kubernetes/cni-networkpolicy.md).

## CNI `ADD` a `DEL`

CNI lifecycle operácie, ktorými runtime žiada plugin o vytvorenie alebo odstránenie network connectivity a súvisiaceho IPAM state-u pre Pod sandbox. Pozri [CNI a NetworkPolicy](docs/09-kubernetes/cni-networkpolicy.md).

## CPU millicore

Kubernetes CPU quantity, kde `1000m` predstavuje jednu CPU jednotku a `250m` štvrtinu CPU. Pozri [Requests, limits a QoS](docs/09-kubernetes/requests-limits-qos.md).

## CPU throttling

Obmedzenie CPU času containeru po vyčerpaní cgroup CPU quota; process nemusí byť ukončený, ale môže mať vyššiu latency a nižší throughput. Pozri [Requests, limits a QoS](docs/09-kubernetes/requests-limits-qos.md).

## CSI

Container Storage Interface contract oddeľujúci Kubernetes storage orchestration od vendor-specific provision, attach, mount, resize a snapshot implementation. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Default deny — NetworkPolicy

Policy pattern vyberajúci všetky Pody v namespace a nepovoľujúci žiadny traffic pre deklarovaný ingress alebo egress smer, kým ho nepovolí iná additive policy. Pozri [CNI a NetworkPolicy](docs/09-kubernetes/cni-networkpolicy.md).

## Default StorageClass

StorageClass označená clusterom ako default pre PVCs bez explicitného `storageClassName`; zmena defaultu môže zmeniť cost, topology a lifecycle nových volumes bez zmeny workload manifestu. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Dynamic provisioning — Kubernetes storage

Automatické vytvorenie backing storage a PV external provisionerom na základe PVC a StorageClass. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Egress-isolated Pod

Pod vybraný aspoň jednou NetworkPolicy pre egress, ktorého outbound traffic je povolený iba unionom matching egress pravidiel. Pozri [CNI a NetworkPolicy](docs/09-kubernetes/cni-networkpolicy.md).

## Ephemeral storage request

Deklarovaná požiadavka Podu alebo containeru na Node-local ephemeral storage používaná pri scheduling-u a resource accounting-u. Pozri [Requests, limits a QoS](docs/09-kubernetes/requests-limits-qos.md).

## Ephemeral volume — Kubernetes

Volume s lifecycle viazaným na Pod alebo konkrétnu projection, napríklad `emptyDir`, ConfigMap/Secret projection alebo generic ephemeral volume. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Exec probe

Kubernetes probe spúšťajúca command v container environment-e a vyhodnocujúca jeho exit status. Pozri [Probes](docs/09-kubernetes/probes.md).

## Extended resource — Kubernetes

Node resource s vendor alebo domain prefixom, napríklad GPU, publikovaný device pluginom alebo platform componentom a používaný schedulerom ako integer capacity. Pozri [Requests, limits a QoS](docs/09-kubernetes/requests-limits-qos.md).

## `FailedScheduling`

Kubernetes Event reason indikujúci, že scheduler nenašiel alebo nevedel bindnúť vhodný Node; message typicky agreguje resource, affinity, taint, topology, storage alebo port konflikty. Pozri [Scheduling](docs/09-kubernetes/scheduling.md).

## Feasible Node

Node, ktorý prešiel všetkými aktívnymi scheduler filter constraints pre konkrétny Pod a môže pokračovať do scoring fázy. Pozri [Scheduling](docs/09-kubernetes/scheduling.md).

## Filter plugin — Kubernetes scheduler

Scheduling Framework plugin vyhodnocujúci, či konkrétny Node spĺňa hard constraints Podu. Pozri [Scheduling](docs/09-kubernetes/scheduling.md).

## Flow log — CNI

Dataplane observability záznam o povolenom alebo zamietnutom network flowe vrátane source/destination identity, portu, policy a action metadata podľa CNI implementácie. Pozri [CNI a NetworkPolicy](docs/09-kubernetes/cni-networkpolicy.md).

## gRPC probe

Kubernetes probe používajúca gRPC Health Checking Protocol na overenie startup, liveness alebo readiness služby na Pod endpoint-e. Pozri [Probes](docs/09-kubernetes/probes.md).

## Guaranteed QoS

Kubernetes QoS class pre Pod, ktorého relevantné containers majú CPU a memory requests rovné limits podľa QoS pravidiel. Pozri [Requests, limits a QoS](docs/09-kubernetes/requests-limits-qos.md).

## HTTP probe

Kubernetes probe vykonávajúca HTTP alebo HTTPS request na Pod IP a nakonfigurovaný port/path z kubelet network perspektívy. Pozri [Probes](docs/09-kubernetes/probes.md).

## Huge pages — Kubernetes

Predalokované veľké memory pages publikované Node-om ako page-size-specific nekompresibilný resource. Pozri [Requests, limits a QoS](docs/09-kubernetes/requests-limits-qos.md).

## Ingress-isolated Pod

Pod vybraný aspoň jednou NetworkPolicy pre ingress, ktorého inbound traffic je povolený iba unionom matching ingress pravidiel. Pozri [CNI a NetworkPolicy](docs/09-kubernetes/cni-networkpolicy.md).

## IPAM

IP Address Management mechanizmus prideľujúci a uvoľňujúci jedinečné Pod IP adresy a súvisiace subnet/route metadata. Pozri [CNI a NetworkPolicy](docs/09-kubernetes/cni-networkpolicy.md).

## `ipBlock` — NetworkPolicy

CIDR-based NetworkPolicy peer určený najmä pre traffic k alebo z IP rozsahov mimo selector-based Pod identity modelu; výsledok môže ovplyvniť NAT a enforcement point. Pozri [CNI a NetworkPolicy](docs/09-kubernetes/cni-networkpolicy.md).

## Kubernetes volume

Pod-level mount alebo device source deklarovaný v `spec.volumes`, ktorého backing môže byť ephemeral, projected alebo persistent. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Liveness probe

Kubelet health test rozhodujúci, či je container v stave, z ktorého mu má pomôcť restart; opakované failure vedie k restartu containeru. Pozri [Probes](docs/09-kubernetes/probes.md).

## Local PersistentVolume

PV reprezentujúci storage fyzicky viazaný na konkrétny Node alebo topology domain, s vysokým výkonom, ale bez automatickej multi-node dostupnosti. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Memory limit — Kubernetes

Cgroup memory boundary containeru alebo Podu podľa podporovaného modelu, ktorej prekročenie môže viesť k OOM termination. Pozri [Requests, limits a QoS](docs/09-kubernetes/requests-limits-qos.md).

## NetworkPolicy

Namespaced Kubernetes API object deklarujúci povolený L3/L4 ingress a egress traffic pre Pods vybrané label selectorom; vyžaduje podporujúci dataplane. Pozri [CNI a NetworkPolicy](docs/09-kubernetes/cni-networkpolicy.md).

## Node allocatable

Množstvo Node resources dostupné pre Pods po odpočítaní systémových rezerv, eviction thresholds a ďalšieho platform overheadu. Pozri [Scheduling](docs/09-kubernetes/scheduling.md) a [Requests, limits a QoS](docs/09-kubernetes/requests-limits-qos.md).

## Node OOM

Host-level out-of-memory stav Node-u, pri ktorom kernel vyberá proces na ukončenie v širšom system context-e; je odlišný od container cgroup limit OOM. Pozri [Requests, limits a QoS](docs/09-kubernetes/requests-limits-qos.md).

## Nominated Node

Dočasný Pod status signal používaný schedulerom najmä pri preemption workflowe, ktorý označuje očakávaný kandidátny Node, ale nie je finálnym bindingom. Pozri [Scheduling](docs/09-kubernetes/scheduling.md).

## Overlay network — Kubernetes

Pod network model zapuzdrujúci cross-node Pod traffic do tunnel packetov, čím znižuje potrebu upstream route knowledge za cenu encapsulation a MTU overheadu. Pozri [CNI a NetworkPolicy](docs/09-kubernetes/cni-networkpolicy.md).

## PersistentVolume

Cluster-scoped Kubernetes object reprezentujúci konkrétny persistent storage resource a jeho capacity, access, topology, reclaim a CSI metadata. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## PersistentVolumeClaim

Namespaced Kubernetes request na persistent storage definujúci požadovanú capacity, access mode, volume mode a StorageClass. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Policy enforcement point — network

Miesto v packet path-e, kde CNI alebo iný dataplane vyhodnocuje a aplikuje network policy; jeho poloha voči NAT, Service translation a host trafficu ovplyvňuje pozorované addresses a semantics. Pozri [CNI a NetworkPolicy](docs/09-kubernetes/cni-networkpolicy.md).

## Policy peer — NetworkPolicy

Source alebo destination množina vyjadrená cez Pod selector, namespace selector, ich kombináciu alebo `ipBlock`. Pozri [CNI a NetworkPolicy](docs/09-kubernetes/cni-networkpolicy.md).

## Preemption — Kubernetes scheduling

Mechanizmus, pri ktorom scheduler môže iniciovať odstránenie nižšie prioritných Podov, aby vytvoril priestor pre unschedulable Pod s vyššou prioritou. Pozri [Scheduling](docs/09-kubernetes/scheduling.md).

## PriorityClass

Cluster-scoped Kubernetes resource definujúci numerickú Pod priority a preemption policy semantics. Pozri [Scheduling](docs/09-kubernetes/scheduling.md).

## Probe-level termination grace

`terminationGracePeriodSeconds` nastavené na startup alebo liveness probe pre špecifický grace period pri probe-triggered container termination. Pozri [Probes](docs/09-kubernetes/probes.md).

## Probe threshold

`failureThreshold` alebo `successThreshold` určujúci počet po sebe idúcich výsledkov potrebných na zmenu probe state-u alebo failure action. Pozri [Probes](docs/09-kubernetes/probes.md).

## Probe timeout

Maximum času jedného probe pokusu určené `timeoutSeconds`; príliš krátka hodnota môže pri load-e alebo CPU throttlingu vytvárať false failures. Pozri [Probes](docs/09-kubernetes/probes.md).

## Readiness gate

Pod-level custom condition, ktorá musí byť true spolu s container readiness, aby bol Pod považovaný za Ready. Pozri [Probes](docs/09-kubernetes/probes.md).

## Readiness probe

Kubelet test určujúci, či má Pod prijímať nový traffic; failure nereštartuje container, ale mení readiness a backend eligibility. Pozri [Probes](docs/09-kubernetes/probes.md).

## Reclaim policy — Kubernetes storage

PV lifecycle pravidlo `Delete` alebo `Retain` určujúce, čo sa má stať s PV a podľa drivera backing storage po uvoľnení claimu; nie je náhradou backup policy. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Resource limit — Kubernetes

Deklarované runtime maximum alebo enforcement boundary resource-u, napríklad CPU quota alebo memory cgroup limit. Pozri [Requests, limits a QoS](docs/09-kubernetes/requests-limits-qos.md).

## Resource overcommitment — Kubernetes

Stav, keď aggregate runtime potential alebo limits presahujú fyzickú kapacitu, zatiaľ čo scheduler placement vychádza z nižších requests; zvyšuje utilization aj pressure risk. Pozri [Requests, limits a QoS](docs/09-kubernetes/requests-limits-qos.md).

## Resource request — Kubernetes

Deklarované množstvo resource-u používané schedulerom na placement a platformou ako reservation alebo relative-share signal. Pozri [Requests, limits a QoS](docs/09-kubernetes/requests-limits-qos.md).

## Restart storm

Séria koordinovaných alebo opakovaných container restartov vyvolaná chybnou liveness/startup probe alebo spoločnou dependency failure, ktorá môže incident ďalej zhoršiť. Pozri [Probes](docs/09-kubernetes/probes.md).

## Routed Pod network

Pod network model, v ktorom sú Pod CIDRs alebo addresses priamo routovateľné medzi Nodes alebo upstream sieťou bez overlay encapsulation. Pozri [CNI a NetworkPolicy](docs/09-kubernetes/cni-networkpolicy.md).

## RuntimeClass overhead

CPU a memory overhead runtime sandboxu deklarovaný RuntimeClassom a zohľadnený pri Pod scheduling-u a resource accounting-u podľa podpory. Pozri [Requests, limits a QoS](docs/09-kubernetes/requests-limits-qos.md).

## Scheduler profile

Konfigurácia kube-scheduleru s vlastným `schedulerName`, aktívnymi Scheduling Framework plugins, weights a plugin arguments. Pozri [Scheduling](docs/09-kubernetes/scheduling.md).

## Scheduling Framework

Pluggable architektúra kube-scheduleru rozdeľujúca scheduling cycle na extension points ako QueueSort, Filter, Score, Reserve, Permit a Bind. Pozri [Scheduling](docs/09-kubernetes/scheduling.md).

## Scheduling queue

Interná scheduler štruktúra pre nové, backoff a unschedulable Pods čakajúce na ďalší scheduling attempt. Pozri [Scheduling](docs/09-kubernetes/scheduling.md).

## Score plugin — Kubernetes scheduler

Scheduling Framework plugin prideľujúci feasible Nodes relatívne skóre podľa soft preferencií a placement stratégie. Pozri [Scheduling](docs/09-kubernetes/scheduling.md).

## `schedulerName`

Pod spec field určujúci scheduler zodpovedný za binding Podu; ak zodpovedajúci scheduler nebeží, Pod zostane unscheduled. Pozri [Scheduling](docs/09-kubernetes/scheduling.md).

## Startup probe

Kubelet probe chrániaca pomaly štartujúci container tým, že odloží liveness a readiness hodnotenie, kým inicializácia neuspeje alebo neprekročí failure hranicu. Pozri [Probes](docs/09-kubernetes/probes.md).

## Static provisioning — Kubernetes storage

Model, v ktorom administrator vytvorí PV pre vopred existujúci storage asset a PVC sa naň následne bindne. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## StorageClass

Cluster-scoped Kubernetes policy object definujúci provisioner, parameters, reclaim policy, binding mode, expansion a topology defaults pre dynamicky provisioned volumes. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Synthetic monitoring

Externý opakovaný test user-facing request pathu cez DNS, load balancer, routing a application, odlišný od kubelet-local container probes. Pozri [Probes](docs/09-kubernetes/probes.md).

## TCP probe

Kubernetes probe overujúca úspešné otvorenie TCP connectionu na Pod IP a port bez overenia application protocol response alebo business correctness. Pozri [Probes](docs/09-kubernetes/probes.md).

## Volume binding mode

StorageClass policy určujúca, či sa dynamic volume provision/binding vykoná okamžite alebo sa odloží do scheduling kontextu cez `WaitForFirstConsumer`. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Volume mode — Kubernetes

PVC/PV contract určujúci, či workload dostane filesystem mount alebo raw block device. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## VolumeAttachment

Cluster-scoped storage API object reprezentujúci attach požiadavku alebo stav CSI volume-u voči konkrétnemu Node-u. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## `WaitForFirstConsumer`

StorageClass binding mode odkladajúci provisioning alebo PV binding, kým scheduler pozná Pod placement constraints a vie koordinovať storage topology s vybraným Node-om. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).
