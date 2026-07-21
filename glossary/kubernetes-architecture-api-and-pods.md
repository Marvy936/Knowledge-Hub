# Kubernetes architecture, API and Pod glossary entries

## Actual state — Kubernetes

Reálny stav clusteru alebo external systému v konkrétnom okamihu, napríklad existujúce Pods, bežiace processes, attached volumes alebo cloud resources; controller ho nemusí okamžite celý pozorovať. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Admission control — Kubernetes

Request-time vrstva Kubernetes API, ktorá po authentication a authorization mutuje alebo validuje relevantné create, update a delete requests pred persistence. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## Admission webhook dependency

Synchronous external alebo in-cluster dependency API write pathu, ktorej latency, TLS, availability a failure policy priamo ovplyvňujú matching Kubernetes requests. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## Annotation — Kubernetes

Neidentifikačné key/value metadata objektu určené pre tool, controller alebo human context, nie na efektívnu selection objects. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## API aggregation — Kubernetes

Mechanizmus rozšírenia Kubernetes API o ďalší API server registrovaný cez `APIService`, odlišný od resource schema uloženého cez CRD. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## API discovery — Kubernetes

Schopnosť klienta zistiť dostupné API groups, versions, resources, scopes a podporované verbs z konkrétneho clusteru. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## API group — Kubernetes

Logická family Kubernetes resource types, napríklad core group alebo `apps`, používaná spolu s API version a kindom. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## API request pipeline — Kubernetes

Sekvencia TLS, authentication, authorization, admission, schema/defaulting/conversion a persistence krokov spracúvajúcich Kubernetes API request. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## APIService — Kubernetes

Cluster-scoped object registrujúci aggregated API group/version a service, ktorá ju obsluhuje. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## Cluster add-on — Kubernetes

Platformová služba nasadená nad core clusterom, napríklad DNS, metrics, ingress/gateway, policy alebo log collection, ktorá nie je automaticky core control-plane componentom. Pozri [Kubernetes architecture](docs/09-kubernetes/kubernetes-architecture.md).

## Cluster-scoped resource — Kubernetes

Kubernetes resource, ktorého identity a API scope nie sú viazané na namespace, napríklad Node, Namespace alebo ClusterRole. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Cloud controller manager

Voliteľný Kubernetes control-plane component spúšťajúci cloud-provider-specific controllers pre Node, route alebo load-balancer integrations podľa platformy. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## Condition — Kubernetes

Štruktúrovaný status signál s typom, boolean-like stavom, reason, message a transition time, ktorý opisuje aktuálne významný aspekt resource state-u. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Container Runtime Interface — CRI

gRPC contract medzi kubeletom a container runtime implementation pre Pod sandbox, container a image lifecycle. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## Controller cache — Kubernetes

Lokálna cache napĺňaná typicky cez list/watch, ktorú controller používa na efektívne reads; môže krátkodobo zaostávať za najnovším persisted stavom. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Controller chaining — Kubernetes

Model, v ktorom vyšší controller vytvára desired state pre nižší resource a ďalšie controllers ho postupne realizujú, napríklad Deployment → ReplicaSet → Pod → kubelet. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Control plane — Kubernetes

Sada komponentov poskytujúca API, persistence, scheduling a reconciliation cluster-wide desired state-u. Pozri [Kubernetes architecture](docs/09-kubernetes/kubernetes-architecture.md).

## CustomResourceDefinition — CRD

Cluster-scoped Kubernetes object, ktorý pridáva nový custom resource type, group/version/schema a scope do API; sám osebe neposkytuje reconciliation logic. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Deletion timestamp — Kubernetes

Serverom nastavený čas označujúci, že object bol prijatý na deletion a čaká na graceful termination alebo finalizer cleanup. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Desired state — Kubernetes

Intent deklarovaný v Kubernetes object `spec` alebo odvodený vyšším controllerom, ku ktorému control loops približujú aktuálny stav. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Direct Pod

Pod vytvorený bez vyššieho workload controlleru; po strate alebo Node failure nemá automatický replica replacement a rollout model. Pozri [Pod](docs/09-kubernetes/pod.md).

## Ephemeral container

Diagnostický container pridaný do existujúceho Podu na troubleshooting, ktorý nie je trvalou súčasťou pôvodného workload contractu. Pozri [Pod](docs/09-kubernetes/pod.md).

## etcd quorum

Väčšina voting members potrebná na bezpečné potvrdenie etcd consensus operations; strata quorum blokuje spoľahlivé Kubernetes API writes. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## etcd snapshot

Point-in-time backup etcd data store-u používaný v testovanom Kubernetes control-plane recovery postupe. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## Event — Kubernetes

Časovo obmedzený diagnostický API object opisujúci významnú udalosť okolo iného resource-u, napríklad scheduling, image pull, probe alebo volume failure; nie je trvalým audit logom. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Eventual consistency — Kubernetes

Model, v ktorom API write uloží desired state okamžite, ale controllers, scheduler, kubelet a external systems ho realizujú asynchrónne a stav sa zhoduje až po čase. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Field manager — Kubernetes

Identita declarative alebo programmatic writera zaznamenaná v `managedFields`, ktorá vlastní konkrétne object fields pri server-side apply. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Finalizer — Kubernetes

Qualified metadata string blokujúci finálne odstránenie objectu, kým zodpovedný controller nedokončí cleanup a finalizer neodstráni. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Garbage collection — Kubernetes

Control-plane proces odstraňujúci dependent objects podľa owner references a deletion propagation policy. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Generation — Kubernetes

Server-managed číslo reprezentujúce verziu relevantného desired state-u objektu; controller ho môže porovnávať s observed generation. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Generation lag

Rozdiel medzi aktuálnym `metadata.generation` a generáciou reportovanou controllerom ako spracovanou, signalizujúci zaostávajúcu reconciliation. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## GroupVersionKind — GVK

Trojica API group, version a kind identifikujúca schema Kubernetes objectu, napríklad `apps/v1, Deployment`. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## GroupVersionResource — GVR

Trojica API group, version a REST resource name identifikujúca Kubernetes API endpoint, napríklad `apps/v1/deployments`. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Idempotent reconcile

Controller behavior, pri ktorom opakované spracovanie rovnakého desired a actual state-u nevytvára neplánované duplicity alebo ďalšie side effects. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## ImageService — CRI

Časť CRI používaná kubeletom na image pull, list, status a removal operácie v container runtime. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## Informer — Kubernetes

Client-side mechanism kombinujúci list/watch, local cache a event handlers na efektívne sledovanie Kubernetes resources pre controllers. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Init container

Container, ktorý musí úspešne dokončiť prípravnú úlohu pred spustením bežných application containers v Pode. Pozri [Pod](docs/09-kubernetes/pod.md).

## Kubernetes API

Versionované HTTP rozhranie, cez ktoré users, clients, controllers a node components čítajú a menia Kubernetes resources a cluster state. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Kubernetes cluster

Logická platformová jednotka pozostávajúca z control plane-u, worker nodes, cluster networku, storage a supporting integrations. Pozri [Kubernetes architecture](docs/09-kubernetes/kubernetes-architecture.md).

## Kubernetes controller

Control loop sledujúci resources a vykonávajúci alebo požadujúci zmeny, ktoré približujú observed state k desired state-u. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Kubernetes object

Persistentná inštancia Kubernetes resource type-u reprezentujúca desired alebo observed cluster state cez API. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Kubernetes resource

API-exposed resource type s group/version, REST endpointom, schema, scope a podporovanými verbs. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## kube-apiserver

Core control-plane server exponujúci Kubernetes API a koordinujúci authentication, authorization, admission, validation, conversion a persistence. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## kube-controller-manager

Control-plane process spúšťajúci sadu built-in Kubernetes controllers, napríklad Node, Job, namespace a garbage-collection loops. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## kube-proxy

Bežný node component implementujúci časť Kubernetes Service dataplane-u z Service a EndpointSlice state-u; môže byť nahradený alternatívnou implementáciou. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## kube-scheduler

Control-plane component vyberajúci vhodný Node pre Pods, ktoré ešte nemajú assignment; samotné containers nespúšťa. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## kubelet

Primary worker-node agent sledujúci Pods pridelené Node-u a koordinujúci runtime, volumes, probes, status a node resource lifecycle. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## Label — Kubernetes

Indexovateľné key/value metadata určené na grouping a selection Kubernetes objects. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Leader-elected controller

Controller nasadený vo viacerých instances, ktoré cez Lease koordinujú aktívneho leadera; stále musí tolerovať retries a nie je exactly-once systémom. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Lease — Kubernetes

Lightweight object v `coordination.k8s.io` používaný napríklad na Node heartbeats alebo leader election components. Pozri [Kubernetes architecture](docs/09-kubernetes/kubernetes-architecture.md).

## Level-based reconciliation

Controller model, ktorý pri každom reconcile vyhodnocuje aktuálny desired a observed state namiesto závislosti na jedinom nevynechanom evente. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## List/watch pattern — Kubernetes

API klient najprv získa collection snapshot cez list a následne sleduje zmeny cez watch od príslušného resourceVersion. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Managed control plane

Kubernetes control plane, ktorého časť lifecycle-u a availability prevádzkuje provider, zatiaľ čo zákazník zostáva zodpovedný za workload, identity, policy, data a značnú časť cluster configuration. Pozri [Kubernetes architecture](docs/09-kubernetes/kubernetes-architecture.md).

## Mirror Pod

API-visible reprezentácia static Podu, ktorú kubelet vytvorí pre observability; authoritative configuration zostáva na konkrétnom Node-e. Pozri [Pod](docs/09-kubernetes/pod.md).

## Mutating admission

Admission fáza schopná zmeniť alebo doplniť incoming Kubernetes object pred jeho finálnou validáciou a persistence. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## Namespaced resource — Kubernetes

Kubernetes resource, ktorého object identity a policy scope zahŕňajú namespace. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Node allocatable

Časť Node capacity dostupná pre scheduling Pods po odpočítaní resources rezervovaných pre operating system a Kubernetes components podľa configuration. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## Node condition

Štruktúrovaný status signál Node-u, napríklad Ready, MemoryPressure, DiskPressure alebo PIDPressure. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## Node Lease

Lease v namespace `kube-node-lease` používaný ako lightweight heartbeat konkrétneho Kubernetes Node-u. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## Object UID — Kubernetes

Server-generated immutable identity konkrétnej object inštancie; znovu vytvorený object s rovnakým menom dostane nové UID. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Observed generation — Kubernetes

Status hodnota signalizujúca, ktorú verziu object desired state-u controller alebo agent už spracoval. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Observed state — Kubernetes

Stav, ktorý controller alebo agent aktuálne vidí cez API cache, runtime alebo external systém a používa ho pri reconciliation. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## OwnerReference — Kubernetes

Metadata väzba dependent objectu na owner object pomocou owner UID, používaná controllers a garbage collectorom. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Partial failure — controller

Stav, keď controller dokončí iba časť distribuovanej operácie, napríklad vytvorí external resource, ale nestihne uložiť jeho identity do statusu, a musí sa bezpečne zotaviť pri retry. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Pod

Najmenší deployable Kubernetes compute object predstavujúci jeden alebo viac co-scheduled containers so spoločnou Pod network identity, lifecycle boundary a volumes. Pozri [Pod](docs/09-kubernetes/pod.md).

## Pod condition

Štruktúrovaný Pod status signal, napríklad Scheduled, Initialized, ContainersReady alebo Ready, ktorý je odlišný od high-level Pod phase. Pozri [Pod](docs/09-kubernetes/pod.md).

## Pod phase

High-level summary lifecycle state-u Podu: Pending, Running, Succeeded, Failed alebo Unknown; reasons ako CrashLoopBackOff nie sú samostatné phases. Pozri [Pod](docs/09-kubernetes/pod.md).

## Pod readiness gate

Custom condition zahrnutá do Pod readiness rozhodnutia, ktorú musí nastavovať zodpovedný external alebo platform controller. Pozri [Pod](docs/09-kubernetes/pod.md).

## Pod sandbox

Runtime prostredie Podu vytvorené cez CRI, ktoré drží najmä shared network namespace a infra lifecycle pre Pod containers. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md) a [Pod](docs/09-kubernetes/pod.md).

## Pod template

Embedded desired Pod metadata a spec v workload controller resource-e, z ktorého controller vytvára nové Pod instances. Pozri [Pod](docs/09-kubernetes/pod.md).

## Reconciliation key

Stabilná identity resource-u, typicky `namespace/name`, vložená do controller work queue, podľa ktorej worker načíta najnovší object state. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Reconciliation loop

Opakovaný proces observe, compare, act a report, ktorý približuje actual state Kubernetes alebo external systému k desired state-u. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## ResourceVersion — Kubernetes

Opaque storage version objektu alebo collection snapshotu používaná na optimistic concurrency a list/watch continuity, nie ako business version. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## RuntimeService — CRI

Časť CRI používaná kubeletom na Pod sandbox a container create, start, stop, remove, status a streaming lifecycle. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## Selector — Kubernetes

Výraz vyberajúci objects podľa labels a tvoriaci kritický contract pre controllers, Services, policy alebo CLI queries. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Server-side apply — Kubernetes

Deklaratívny API update model, pri ktorom API server merge-uje intent a sleduje field ownership jednotlivých managers. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Service dataplane — Kubernetes

Node alebo cluster networking vrstva implementujúca virtual Service IP a forwarding na EndpointSlice backends, napríklad cez kube-proxy alebo alternatívny eBPF dataplane. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## Sidecar container

Auxiliary container bežiaci v rovnakom Pode ako hlavná aplikácia a zdieľajúci jej placement, network a Pod lifecycle boundary. Pozri [Pod](docs/09-kubernetes/pod.md).

## Static Pod

Pod spravovaný priamo kubeletom na konkrétnom Node-e z local manifestu, bez bežného scheduler/controller ownershipu. Pozri [Kubernetes architecture](docs/09-kubernetes/kubernetes-architecture.md) a [Pod](docs/09-kubernetes/pod.md).

## Storage version — Kubernetes

Interná API verzia, v ktorej API server persistuje konkrétny resource type, pričom externé clients môžu používať iné podporované versions s conversion. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Subresource — Kubernetes

Samostatný API endpoint pre vybranú časť alebo operáciu resource-u, napríklad `/status`, `/scale`, `/log`, `/exec` alebo `/eviction`. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Validating admission

Admission fáza, ktorá po relevantnej mutácii a validácii rozhodne, či Kubernetes API request povolí alebo odmietne. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## Work queue — Kubernetes controller

Fronta reconciliation keys s deduplication, retry a rate-limiting behavior používaná controller workers na bounded spracovanie zmien. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Worker node — Kubernetes

Fyzický alebo virtuálny server poskytujúci resources a node components potrebné na spúšťanie Pods pridelených control plane-om. Pozri [Kubernetes architecture](docs/09-kubernetes/kubernetes-architecture.md) a [Worker node components](docs/09-kubernetes/worker-node-components.md).
