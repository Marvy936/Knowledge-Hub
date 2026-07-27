# Kubernetes node, Pod, ReplicaSet and Deployment glossary entries

Tento section-specific doplnok rozširuje Kubernetes glossary o identity, ownership, execution a recovery pojmy použité pri strict revalidation kapitol Worker node components, Pod, ReplicaSet a Deployment.

## Active replica subject

Versionovaný inventory ReplicaSetom vlastnených Pod UIDs, ich lifecycle classification, readiness, availability a template equivalence pre konkrétnu ReplicaSet UID/generation. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Admitted Pod snapshot

Effective immutable alebo prevažne immutable Pod spec po API conversion, defaulting, mutation, validation a persistence, z ktorej kubelet vytvára runtime state konkrétneho Pod UID. Pozri [Pod](docs/09-kubernetes/pod.md).

## Adoptable Pod

Pod, ktorý matchuje ReplicaSet selector a nemá conflicting controller ownerReference, takže ho controller môže podľa ownership pravidiel adoptovať. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Adoption event — ReplicaSet

Controller transition, pri ktorom ReplicaSet zapíše controller ownerReference na matching adoptable Pod a začne ho započítavať do desired replica setu. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Assigned-Pod execution subject

Identita Node-side realizácie zahŕňajúca cluster, Pod UID a admitted spec, Node UID, kubelet/runtime/CNI/CSI generations, sandbox, images, mounts, probes, status a business outcome. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## Availability timing subject — Deployment

Pod UID a časový interval, počas ktorého Pod zostáva Ready podľa `minReadySeconds` a ďalších rollout conditions pred započítaním ako available replica. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## Child-ReplicaSet ownership

Vzťah, v ktorom Deployment vlastní ReplicaSet revision a autoritatívne riadi jej scale počas rollout-u; manual write na child ReplicaSet môže vyšší controller prepísať. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md) a [Deployment](docs/09-kubernetes/deployment.md).

## CNI/IPAM operation subject

Identita Pod network setup alebo cleanup operácie zahŕňajúca Pod UID, sandbox/container ID, Node, CNI generation, network attachment, IPAM lease, interface, routes, request/result a cleanup verdict. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## Container-restart subject — Kubernetes

Lifecycle jedného container instance restartu v rámci rovnakého Pod UID a spravidla rovnakého sandboxu, Pod IP a Pod-scoped volumes. Pozri [Pod](docs/09-kubernetes/pod.md).

## Controlled Pod

Pod, ktorého controller ownerReference odkazuje na konkrétny ReplicaSet UID a ktorý controller autoritatívne započítava do replica reconciliation. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## CRI capability subject

Versionovaný stav kubelet-to-runtime capability zahŕňajúci runtime endpoint, configuration generation, sandbox/container/image operations, latency, errors, content store a test outcome. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## CSI node-publish subject

Identita node-side storage transitionu zahŕňajúca Pod UID, volume/device ID, Node, CSI generation, stage/publish target, mount options, filesystem, operation result a cleanup state. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## Deployment release subject

Immutable alebo rekonštruovateľná identita rollout-u zahŕňajúca cluster, Deployment UID/generation, admitted Pod template, field ownership, old/new ReplicaSet UIDs, image/config/secret generations, strategy budgets a business outcome. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## Deployment scale ownership

Contract určujúci authoritative writera Deployment `/scale` alebo `.spec.replicas`, napríklad HPA, GitOps, manual workflow alebo custom autoscaler. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## Direct-Pod recovery boundary

Failure boundary Podu vytvoreného bez higher-level workload controlleru, pri ktorom Node failure alebo Pod deletion nemá automatický replica replacement owner. Pozri [Pod](docs/09-kubernetes/pod.md).

## Effective image identity — Kubernetes node

Konkrétny platform manifest a runtime `imageID`/digest použitý na Node-e, odlíšený od mutable source tagu alebo pôvodnej textovej image reference. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## EndpointSlice eligibility subject

Versionovaný stav Pod UID v EndpointSlice vrátane targetRef, addresses a readiness/serving/terminating conditions pre konkrétny Service a workload generation. Pozri [Pod](docs/09-kubernetes/pod.md).

## EndpointSlice revision cohort

Množina endpoint Pod UIDs patriacich jednej Deployment/ReplicaSet revision, používaná na koreláciu trafficu a telemetry s konkrétnym template digestom. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## Foreign Pod — ReplicaSet

Pod, ktorý matchuje selector, ale vlastní ho iný controller alebo nespĺňa adoption pravidlá, takže ho konkrétny ReplicaSet nemá autoritatívne riadiť. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Init side-effect boundary

Hranica určujúca, či init container vykonáva iba bezpečnú local prípravu alebo durable/shared external side effect vyžadujúci singleton, idempotency a recovery protocol. Pozri [Pod](docs/09-kubernetes/pod.md).

## Kubelet reconciliation subject

Identita jedného kubelet Pod-sync rozhodnutia zahŕňajúca Pod UID/spec, Node UID, local admission, runtime/volume/network dependencies, observed local state a status write outcome. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## Local admission boundary — kubelet

Node-side rozhodnutie, či pridelený Pod môže byť realizovaný vzhľadom na aktuálnu Node capacity, capabilities, RuntimeClass, devices, volumes, pressure a local configuration. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## Node capability verdict

Dôkaz, že konkrétny worker Node bezpečne zvláda required kubelet, CRI, CNI, CSI, image, cgroup a Service-dataplane transitions, nie iba že reportuje `Ready=True`. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## Node execution generation

Versionovaný bundle node image, kubelet, runtime, CNI, CSI, cgroup a supporting configuration použitý na konkrétnej Node inštancii. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## Node recovery verdict

Dôkaz, že po node incidente fungujú sandbox create/delete, CNI/IPAM, CSI mount/unmount, image resolution, cgroup enforcement, probes, Service path, cleanup a pôvodný business outcome. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## Orphaned Pod — ReplicaSet

Pod bez aktuálneho controller ownera, napríklad po orphan deletion alebo manual ownership zásahu, ktorý môže ďalej bežať, prijímať traffic alebo byť adoptovaný. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Partitioned-node execution

Stav, keď Node alebo kubelet stratil spojenie s control plane-om, ale local workload processes pokračujú a môžu sa prekrývať s replacement Pods vytvorenými inde. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## Pod acceptance verdict

Verdikt, že konkrétny Pod UID má správny admitted spec, image/config/secret state, sandbox a mounts, containers, probes, readiness gates, EndpointSlice eligibility a business outcome. Pozri [Pod](docs/09-kubernetes/pod.md).

## Pod replacement subject

Lifecycle nového Pod UID vytvoreného workload controllerom po deletion, eviction, rollout alebo failure predchádzajúceho Podu, s novým sandboxom a execution chainom. Pozri [Pod](docs/09-kubernetes/pod.md).

## Pod runtime-envelope subject

Identita jednej Pod repliky zahŕňajúca owner/revision, Pod UID, admitted spec, shared network/volume boundary, containers, Node assignment, conditions, endpoint eligibility a termination state. Pozri [Pod](docs/09-kubernetes/pod.md).

## Pod sandbox subject

Identita CRI runtime sandboxu konkrétneho Pod UID vrátane Node, sandbox ID, network namespace, Pod IP, CNI result, runtime generation a lifecycle state. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## Pod-template revision subject

Admitted Deployment Pod template, jeho hash, image/config/security content a ReplicaSet UID tvoriace jednu rollout revision. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## Pod UID generation

Jedna disposable workload-replica identity viazaná na owner revision a admitted Pod spec; replacement s podobným menom je nový subject s novým UID. Pozri [Pod](docs/09-kubernetes/pod.md).

## Probe control signal

Startup, liveness alebo readiness observation, ktorej výsledok spúšťa konkrétnu kubelet alebo routing action a preto musí zodpovedať failure mechanizmu, ktorý táto action dokáže ovplyvniť. Pozri [Pod](docs/09-kubernetes/pod.md).

## Process-loaded configuration

Effective config alebo secret epoch, ktorú application process skutočne načítal a používa, odlíšená od source ConfigMap/Secret objectu alebo mounted bytes. Pozri [Pod](docs/09-kubernetes/pod.md).

## Projected-data subject — Kubernetes Pod

Väzba source ConfigMap, Secret, service-account token alebo Downward API field-u na Pod volume/environment snapshot, kubelet materialization a process consumption. Pozri [Pod](docs/09-kubernetes/pod.md).

## Readiness-gate subject

Custom Pod condition contract zahŕňajúci Pod UID, gate type, owning controller, external registration generation, condition state a cleanup behavior. Pozri [Pod](docs/09-kubernetes/pod.md).

## Recreate exclusivity boundary

Deployment strategy boundary, pri ktorej old Pods majú zaniknúť pred vytvorením new Pods, ale application/external fencing musí samostatne preukázať, že old writer už nekoná. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## Replica-set acceptance verdict

Dôkaz, že ReplicaSet vlastní presný desired Pod inventory, všetky Pods sú template-equivalentné a Ready/Available, Service vyberá správne UIDs a next reconcile je no-op. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## ReplicaSet reconciliation subject

Identita ReplicaSet control-loop rozhodnutia zahŕňajúca ReplicaSet UID/generation, desired replicas, selector, template hash, matching Pod UID inventory, ownerReferences, lifecycle classes a higher-level owner. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Revision-to-traffic lifecycle

Deployment transition od admitted Pod template revision cez ReplicaSet capacity exchange a Pod readiness po EndpointSlice cohort, Service traffic a business acceptance. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## Rollback compatibility subject

Inventory old application artifactu a current database, event, cache, config, secret, feature a external state-u potrebný na rozhodnutie, či návrat k starej Deployment template revision je bezpečný. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## Rolling capacity exchange

Opakovaný Deployment protocol scale-up new ReplicaSetu, readiness/availability verification a bounded scale-down old ReplicaSetu podľa surge a unavailable budgetov. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## Rollout acceptance verdict

Dôkaz, že latest Deployment generation je observed, canonical ReplicaSet a Pod digests sú správne, capacity/availability/traffic transitions skončili a critical business aj forbidden-outcome checks prešli. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## Rollout progress verdict

Generation-bound Deployment condition a supporting evidence určujúce, či rollout postupuje, stagnuje alebo prekročil deadline; nie je automatickou recovery action. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## Selector control boundary — ReplicaSet

Namespace-scoped label selector, ownership a adoption contract určujúci candidate Pod množinu, nad ktorou ReplicaSet počíta a reconcile-uje desired replicas. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Selector overlap — ReplicaSet

Failure stav, pri ktorom selectors viacerých controllers vyberajú rovnaké Pods a vytvárajú conflicting replica alebo ownership instructions. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Service-to-ReplicaSet selection drift

Rozdiel medzi Pod inventory vlastneným ReplicaSetom a Pod inventory vybraným Service selectorom, ktorý môže smerovať traffic na foreign, old alebo debug Pods. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Shared-port contract — Pod

Dohoda o listener addresses, ports, startup ordering a proxy pathoch medzi containers, ktoré zdieľajú jeden Pod network namespace. Pozri [Pod](docs/09-kubernetes/pod.md).

## Sidecar lifecycle contract

Definovaný startup, readiness, resource, failure, completion a shutdown behavior auxiliary containeru vo vzťahu k main application containerom jedného Podu. Pozri [Pod](docs/09-kubernetes/pod.md).

## Surge-capacity subject

Node a cluster capacity, topology, ports, volumes a terminating overlap potrebné na realizáciu Deployment `maxSurge` bez porušenia availability budgetu. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## Template-equivalence verdict — ReplicaSet

Dôkaz, že controlled alebo adoptovaný Pod zodpovedá expected ReplicaSet template-u v image, config, secret, security, resources, probes a relevantných labels, nie iba selectorom. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Terminating-replica overlap

Dočasný stav Deployment rollout-u, keď terminating old Pods stále držia resources, connections, ports alebo volumes popri active desired a surge Pods. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## Termination-budget subject — Pod

Pod UID, grace period, PreStop duration, signal timeline, connection drain, in-flight work, force-kill deadline a cleanup outcome tvoriace graceful termination contract. Pozri [Pod](docs/09-kubernetes/pod.md).

## Unavailable budget — Deployment

Maximálny reviewovaný počet desired replicas, ktoré môžu byť počas rollout-u nedostupné podľa `maxUnavailable`, odlíšený od business capacity alebo PDB eviction budgetu. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## Worker-node observation matrix

Mapovanie assignment, kubelet, runtime, CNI, CSI, image, resources, Service dataplane a business boundaries na ich subjects a diskriminačné observations. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).
