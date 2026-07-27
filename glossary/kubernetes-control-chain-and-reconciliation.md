# Kubernetes control-chain and reconciliation glossary entries

Tento section-specific doplnok rozširuje existujúci súbor `kubernetes-architecture-api-and-pods.md` o identity a recovery pojmy použité pri strict revalidation prvých štyroch kapitol Kubernetes sekcie.

## Admitted object — Kubernetes

Effective Kubernetes object po decoding, conversion, defaulting, mutating admission, validation a policy gates, ktorý bol prijatý na persistence; nemusí byť byte-for-byte zhodný so source manifestom. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Admitted object generation

Konkrétna object generation vzniknutá po server-side mutation a persistence, viazaná na object UID, field ownership a admission configuration generation. Pozri [Kubernetes architecture](docs/09-kubernetes/kubernetes-architecture.md) a [API a object model](docs/09-kubernetes/api-object-model.md).

## API request subject — Kubernetes

Rekonštruovateľná identita requestu zahŕňajúca cluster endpoint a CA, caller identity, verb, GVR, namespace/name alebo subresource, request digest, field manager, preconditions, admission generation a response/persistence outcome. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## API-to-workload lifecycle

End-to-end transition od authenticated a admitted API requestu cez persisted object generation, controller graph, scheduler assignment, node execution a Service eligibility až po application business outcome. Pozri [Kubernetes architecture](docs/09-kubernetes/kubernetes-architecture.md).

## API write-path subject

Subject-bound evidence jedného Kubernetes write-u od endpointu a caller identity cez authentication, authorization a admission po etcd revision, response, audit a watch publication. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## Application acceptance subject — Kubernetes

Spoločná identita clusteru, top-level object UID/generation, dependent resources, Pod image/config/secret generations, eligible endpoints a business verification potrebná na prijatie rollout-u. Pozri [Kubernetes architecture](docs/09-kubernetes/kubernetes-architecture.md).

## Bounded reconcile transition

Jeden obmedzený, rekonštruovateľný krok control loopu, napríklad ensure finalizer, create/adopt external resource, update owned fields alebo verify cleanup, po ktorom sa state znovu pozoruje. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Cache-sync boundary — Kubernetes controller

Prechod, pri ktorom controller potvrdí initial list/informer synchronization pred spustením workers alebo leader-ready behavior; nedodržanie môže interpretovať neúplnú cache ako chýbajúci state. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Cluster subject — Kubernetes

Identita clusteru zahŕňajúca API endpoint a CA, cluster/infrastructure identity, control-plane a etcd topológiu, Kubernetes version, node-pool generations, CRI/CNI/CSI, admission/policy a critical add-ons. Pozri [Kubernetes architecture](docs/09-kubernetes/kubernetes-architecture.md).

## Cloud reconciliation subject

Identita cloud-controller alebo provider operation zahŕňajúca cluster, controller identity, object UID/generation, cloud account/region, external resource ID, request ID, desired fields a provider API outcome. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## Controller convergence verdict

Verdikt, že latest desired generation bola spracovaná, owned Kubernetes aj external state zodpovedá contractu, status je generation-current, subsequent reconcile je no-op a pôvodný workload outcome bol overený. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Controller ownership boundary

Rozhranie určujúce, ktoré resource types, object UIDs, fields, dependents a external resources môže konkrétny controller autoritatívne pozorovať, meniť, reportovať a čistiť. Pozri [Kubernetes architecture](docs/09-kubernetes/kubernetes-architecture.md).

## Controller queue subject

Identita controller processing state-u zahŕňajúca controller/version, active leader, reconciliation key, object UID/generation, queue attempt, queue age, backoff a relevantný output transition. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## Control-plane capability subject

Versionovaný stav konkrétnej Kubernetes control-plane capability, napríklad API write/read/watch, etcd persistence, scheduling alebo controller reconciliation, vrátane component instances, leader, configuration, dependencies, metrics a test outcome-u. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## Control-plane observation matrix

Mapovanie endpoint, identity, admission, persistence, scheduler, controller, cloud, certificate a packaging boundaries na ich subjects a diskriminačné observations. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## Control-plane recovery verdict

Dôkaz, že po incidente fungujú semantic API readiness, read/write/watch, etcd quorum a latency, admission, scheduler binding, controller progress a pôvodný workload/business outcome. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## Control-plane write path

Synchronous a durable transition od client endpointu cez API server identity/policy/admission vrstvy po etcd commit, response a následné watch visibility. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## Deletion subject — Kubernetes

Identita deletion lifecycle-u zahŕňajúca cluster, object UID, deletionTimestamp, propagation policy, finalizers, dependent inventory, external bindings a cleanup verdict. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## etcd latency amplification loop

Reinforcing failure loop, v ktorom pomalé etcd commits zvyšujú API latency, watch reconnects a controller retries, čím rastie ďalší API a storage pressure. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## etcd persistence subject

Identita Kubernetes persistence transitionu zahŕňajúca etcd cluster/member IDs, leader, revision, quorum, API request, object/resourceVersion, disk/network health a commit outcome. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## External binding subject — Kubernetes controller

Versionovaná väzba medzi Kubernetes owner UID/generation a external resource ID, operation/idempotency key, owned fields, provider target a cleanup status. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Field ownership subject — Kubernetes

Rekonštruovateľný inventory field managers, owned object paths, subresources, conflicts, force transfers a authoritative team/controller pre konkrétnu object UID/generation. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Finalizer-before-create invariant

Controller invariant vyžadujúci durable finalizer/cleanup ownership pred vytvorením external state-u, aby delete alebo crash nemohli zanechať resource bez recoverable ownera. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Finalizer cleanup contract

Contract medzi object deletion a controllerom určujúci exact external/dependent inventory, cleanup operation, verification a podmienku bezpečného odstránenia finalizeru. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Generation closure

Stav, keď controller observed generation, dependent object graph, effective runtime a acceptance evidence všetky zodpovedajú aktuálnemu `metadata.generation`. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Kubernetes control-chain subject

Spoločná identita clusteru, caller requestu, admitted top-level objectu, dependent/controller generations, scheduler assignment, node execution a Service/business verification. Pozri [Kubernetes architecture](docs/09-kubernetes/kubernetes-architecture.md).

## Kubernetes object subject

Identita konkrétnej object inštancie zahŕňajúca cluster, GVK/GVR, namespace/name, UID, resourceVersion, generation, field ownership, status generation, dependents a deletion state. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Level-based control protocol

Controller protocol, ktorý pri každom reconcile rekonštruuje latest subject a porovná desired, observed a external effective state namiesto závislosti od jednorazovej event sekvencie. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Management-plane/workload-plane split — Kubernetes

Stav, keď API, persistence, scheduling alebo reconciliation capability je degradovaná, ale už spustené workload processes môžu dočasne pokračovať; workload success preto nepreukazuje recovery control plane-u. Pozri [Kubernetes architecture](docs/09-kubernetes/kubernetes-architecture.md) a [Control plane components](docs/09-kubernetes/control-plane-components.md).

## Multi-controller oscillation

Nekonvergentný stav, pri ktorom dva individuálne idempotentné controllers autoritatívne zapisujú rozdielne hodnoty rovnakého fieldu alebo external resource-u. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Name-reuse collision — Kubernetes

Failure, pri ktorom automation alebo external binding zamení zmazaný a znovu vytvorený object s rovnakým namespace/name, ale odlišným UID. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Node execution subject — Kubernetes

Identita prideleného Podu a jeho Node-side realizácie zahŕňajúca Pod UID/spec generation, Node, kubelet/runtime/CNI/CSI generations, sandbox, image, mounts, probes, status a process outcome. Pozri [Kubernetes architecture](docs/09-kubernetes/kubernetes-architecture.md).

## Object UID generation

Jedna lifetime identity objectu vyjadrená UID spolu s konkrétnou desired-state generation; odlišuje name reuse aj viac zmien v rámci jednej object inštancie. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Owner-dependent graph subject

Inventory Kubernetes ownerReferences, owner/dependent UIDs, selectors, revisions, propagation policy a current lifecycle state pre konkrétnu top-level object generation. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Reconciliation hot loop

Failure stav, pri ktorom controller bez semantic progressu opakovane enqueue-uje alebo zapisuje rovnaký subject, spotrebúva CPU/API/etcd capacity a blokuje ďalšie keys. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Reconciliation subject

Rekonštruovateľná identita jedného control-loop rozhodnutia zahŕňajúca controller/version/leader, cluster, object UID/generation/resourceVersion, queue attempt, dependents, external bindings, credentials a reconcile ID. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Scheduler assignment subject

Identita scheduling rozhodnutia zahŕňajúca Pod UID/spec, schedulerName/profile/leader, queue attempt, Node inventory, requests/constraints, plugin verdicts a binding outcome. Pozri [Kubernetes architecture](docs/09-kubernetes/kubernetes-architecture.md).

## Scheduler capability subject

Versionovaný stav scheduling capability zahŕňajúci active leader, profiles/plugins, pending a unschedulable queues, API connectivity, Node/PVC inventory a binding tests. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## Selector ownership contract

Stable label/selector schema určujúca, ktoré objects controller vlastní, Service routuje alebo policy zasahuje, vrátane collision a migration pravidiel. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Semantic API readiness

Readiness verdict API server instance založený na schopnosti bezpečne obsluhovať relevantné API operations a dependencies, nie iba na otvorenom TCP porte alebo živom process-e. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## Semantic status transition

Status alebo condition update vykonaný iba pri významnej zmene observed state-u, nie pri každom retry attempt-e; chráni API/etcd pred self-trigger loops. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Service eligibility generation — Kubernetes

Versionovaný inventory ready Pod/endpoint UIDs vybraných Service/EndpointSlice contractom pre konkrétnu workload generation a dataplane state. Pozri [Kubernetes architecture](docs/09-kubernetes/kubernetes-architecture.md).

## Static control-plane authority

Authoritative local manifest, kubelet a runtime state pre control-plane component spúšťaný ako static Pod, odlíšený od API-visible mirror Podu. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## Unknown reconcile outcome

Stav, keď controller nevie, či external alebo API mutation neprebehla, prebehla čiastočne alebo uspela bez zaznamenaného binding/statusu; pred retry vyžaduje lookup a reconciliation podľa stable identity. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).