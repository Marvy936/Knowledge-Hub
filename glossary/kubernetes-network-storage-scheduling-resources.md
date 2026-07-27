# Kubernetes network, storage, scheduling and resource glossary entries

## Admission resource generation

Versionovaná množina defaultov, LimitRange pravidiel a ďalších admission mutations, ktoré zmenili source resource intent na effective Pod requests/limits. Pozri [Requests, limits a QoS](../docs/09-kubernetes/requests-limits-qos.md).

## Application data generation — Kubernetes storage

Application-level identita mounted dát, napríklad tenant, schema, checkpoint, replication epoch a backup lineage; nie je odvodená iba z PVC alebo PV phase. Pozri [Volumes, PV, PVC a StorageClass](../docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Application-consistent backup — Kubernetes storage

Backup generation vytvorená po koordinovanom application checkpoint-e, flushi alebo quiesce a následne overená clean restore testom. Pozri [Volumes, PV, PVC a StorageClass](../docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Backing-volume identity

External storage asset identifikovaný napríklad CSI `volumeHandle`, provider volume ID, zone a encryption-key generation, ktorý PV reprezentuje v Kubernetes API. Pozri [Volumes, PV, PVC a StorageClass](../docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Binding subject — Kubernetes scheduling

Exact Pod-to-Node placement transition po reserve, permit a pre-bind krokoch, typicky reprezentovaná zápisom Node mena do Podu. Pozri [Scheduling](../docs/09-kubernetes/scheduling.md).

## Cgroup memory OOM subject

Konkrétny Pod/container cgroup, memory boundary, usage a `memory.events` generácia, v ktorej kernel ukončil process pre local cgroup memory limit. Pozri [Requests, limits a QoS](../docs/09-kubernetes/requests-limits-qos.md).

## Cgroup runtime generation

Effective CPU, memory a ďalšie resource controls realizované kubeletom/runtime-om pre konkrétny Pod a container ID. Pozri [Requests, limits a QoS](../docs/09-kubernetes/requests-limits-qos.md).

## CNI chain generation

Versionovaná kombinácia CNI configuration, plugin poradia a per-Node agent/dataplane state-u použitá pri `ADD` alebo `DEL` operácii. Pozri [CNI a NetworkPolicy](../docs/09-kubernetes/cni-networkpolicy.md).

## CNI operation subject

Konkrétne CNI `ADD`, `CHECK` alebo `DEL` vykonanie viazané na runtime sandbox/container ID, network namespace, interface name a configuration generation. Pozri [CNI a NetworkPolicy](../docs/09-kubernetes/cni-networkpolicy.md).

## CPU throttling subject

Konkrétny container cgroup, CPU quota/period a time window, v ktorom process vyčerpal quota a čakal napriek prípadnej voľnej CPU kapacite na Node-e. Pozri [Requests, limits a QoS](../docs/09-kubernetes/requests-limits-qos.md).

## Destructive reclaim subject

Exact PVC UID, PV UID, reclaim policy a backend volume identity, nad ktorými môže deletion transition odstrániť authoritative storage asset. Pozri [Volumes, PV, PVC a StorageClass](../docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Effective NetworkPolicy generation

Policy program reálne načítaný konkrétnym Node/dataplane enforcement pointom po selector resolution a controller reconciliation; môže zaostávať za API object generation. Pozri [CNI a NetworkPolicy](../docs/09-kubernetes/cni-networkpolicy.md).

## Effective resource contract

Admitted requests a limits konkrétneho Podu po defaultingu, LimitRange, policy mutation, init/sidecar calculation a RuntimeClass overhead. Pozri [Requests, limits a QoS](../docs/09-kubernetes/requests-limits-qos.md).

## Enforcement-point verdict — Kubernetes networking

Allow alebo drop rozhodnutie pre exact packet/flow v konkrétnom pre-NAT alebo post-NAT observation pointe dataplane-u. Pozri [CNI a NetworkPolicy](../docs/09-kubernetes/cni-networkpolicy.md).

## Feasible-Node set

Množina Nodes, ktoré po aplikovaní všetkých hard scheduler constraints môžu hostiť konkrétny Pod scheduling subject. Pozri [Scheduling](../docs/09-kubernetes/scheduling.md).

## Flow subject — Kubernetes networking

Exact communication identity obsahujúca source a destination Pod/Node identity, protocol, ports, direction, pre/post-NAT tuple, policy generations a connection state. Pozri [CNI a NetworkPolicy](../docs/09-kubernetes/cni-networkpolicy.md).

## Hard-constraint intersection

Prienik resource, affinity, taint, topology, storage, port, device a ďalších hard placement podmienok; ak je prázdny, Pod je unschedulable. Pozri [Scheduling](../docs/09-kubernetes/scheduling.md).

## HPA denominator subject

Konkrétny request a metric generation použitý ako denominator pri výpočte resource utilization pre Horizontal Pod Autoscaler. Pozri [Requests, limits a QoS](../docs/09-kubernetes/requests-limits-qos.md).

## IPAM allocation subject

Jedinečná väzba medzi IP pool/PodCIDR generation, runtime sandboxom, Pod UID, pridelenou adresou a lease lifecycle-om. Pozri [CNI a NetworkPolicy](../docs/09-kubernetes/cni-networkpolicy.md).

## Kubernetes storage lifecycle subject

Súvislý identity chain od logical data generation cez PVC, PV, StorageClass a backing volume po attachment, mount, backup a reclaim verdict. Pozri [Volumes, PV, PVC a StorageClass](../docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Logical data identity — Kubernetes

Application-owned identita persistentného datasetu, oddelená od Pod mena, PVC mena, PV phase a physical volume assetu. Pozri [Volumes, PV, PVC a StorageClass](../docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Mount generation — Kubernetes storage

Konkrétna väzba Pod UID, Node UID, VolumeAttachment/backend session, stage/publish operácií, mount options a filesystem identity. Pozri [Volumes, PV, PVC a StorageClass](../docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Network acceptance verdict

Verdikt, že current sandbox/IPAM/dataplane/policy generations poskytujú požadovaný packet aj reverse path, application identity a business outcome a zároveň blokujú forbidden flows. Pozri [CNI a NetworkPolicy](../docs/09-kubernetes/cni-networkpolicy.md).

## Network observation matrix

Mapa identity a evidence cez Pod sandbox, IPAM, route/tunnel, Service translation, policy selection, enforcement, connection a application boundaries. Pozri [CNI a NetworkPolicy](../docs/09-kubernetes/cni-networkpolicy.md).

## Node candidate inventory

Versionovaný zoznam Node UIDs a ich labels, taints, conditions, allocatable, reservations, ports, devices a storage constraints pre jeden scheduling attempt. Pozri [Scheduling](../docs/09-kubernetes/scheduling.md).

## Node pressure/eviction subject

Konkrétny Node UID, pressure condition, kubelet threshold, resource signal, victim Pod UID a eviction generation. Pozri [Requests, limits a QoS](../docs/09-kubernetes/requests-limits-qos.md).

## Policy revocation generation — Kubernetes networking

Transition z allow policy/connection state-u na deny state vrátane overenia nových aj existujúcich flows a prípadného session/credential cleanupu. Pozri [CNI a NetworkPolicy](../docs/09-kubernetes/cni-networkpolicy.md).

## Policy selection subject — Kubernetes networking

Exact source alebo destination Pod UID, namespace/Pod labels, direction a matching NetworkPolicy UID/generation inventory použitý na vytvorenie allow unionu. Pozri [CNI a NetworkPolicy](../docs/09-kubernetes/cni-networkpolicy.md).

## Pod effective request

Scheduler-visible resource request Podu po započítaní bežných containers, init/restartable sidecars, Pod-level resources a RuntimeClass overhead podľa current API semantics. Pozri [Requests, limits a QoS](../docs/09-kubernetes/requests-limits-qos.md).

## Pod network identity

Runtime network identity konkrétneho Podu tvorená Pod UID, sandbox/container ID, network namespace, interface a IPAM allocation; workload label alebo Pod meno ju nenahrádza. Pozri [CNI a NetworkPolicy](../docs/09-kubernetes/cni-networkpolicy.md).

## Pod network realization subject

Súvislý CNI/IPAM/interface/route/policy state vytvorený pre konkrétny Pod sandbox na konkrétnom Node-e. Pozri [CNI a NetworkPolicy](../docs/09-kubernetes/cni-networkpolicy.md).

## Pod scheduling attempt

Jedno scheduler vyhodnotenie konkrétneho Pod UID cez queue, active profile, filter, score a binding cycle. Pozri [Scheduling](../docs/09-kubernetes/scheduling.md).

## Pre/post-NAT flow identity

Rozlíšenie packet tuple pred Service/NAT translation a po nej; NetworkPolicy alebo firewall enforcement môže pozorovať iba jednu z týchto identít. Pozri [CNI a NetworkPolicy](../docs/09-kubernetes/cni-networkpolicy.md).

## Preemption recovery subject

Pending high-priority Pod, candidate Node, victim inventory, termination state a post-victim feasibility, ktoré určujú, či preemption môže vytvoriť validný placement. Pozri [Scheduling](../docs/09-kubernetes/scheduling.md).

## PVC claim subject

Namespaced PVC UID, effective request, StorageClass, access/volume mode a binding state používané ako workload storage claim. Pozri [Volumes, PV, PVC a StorageClass](../docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## PV asset subject

Cluster-scoped PV UID, claimRef, topology, reclaim policy a CSI volumeHandle reprezentujúce konkrétny storage asset. Pozri [Volumes, PV, PVC a StorageClass](../docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## QoS verdict — Kubernetes

QoS class odvodená z effective CPU/memory requests a limits relevantných containers alebo Pod-level resources; ovplyvňuje resource/eviction behavior, ale nie je SLA. Pozri [Requests, limits a QoS](../docs/09-kubernetes/requests-limits-qos.md).

## Reserve/permit subject — Kubernetes scheduling

Dočasný scheduler state medzi výberom Node-u a bindingom vrátane resource reservation, permit decision a prípadného `Unreserve` rollbacku. Pozri [Scheduling](../docs/09-kubernetes/scheduling.md).

## Resolved placement evidence

Evidence spájajúca admitted Pod contract, scheduler profile generation, feasible-Node set, score vector a final Pod-to-Node binding. Pozri [Scheduling](../docs/09-kubernetes/scheduling.md).

## Resource acceptance verdict

Verdikt, že admitted requests/limits, scheduler reservation, cgroup realization, runtime throttling/OOM/eviction, autoscaling a application SLO zodpovedajú reviewed contractu. Pozri [Requests, limits a QoS](../docs/09-kubernetes/requests-limits-qos.md).

## Resource lifecycle subject — Kubernetes

Súvislý chain od workload demand cez source/admitted resource contract, scheduling reservation a cgroup enforcement po QoS, pressure, autoscaling a business outcome. Pozri [Requests, limits a QoS](../docs/09-kubernetes/requests-limits-qos.md).

## Resource metric definition

Presný význam resource metricu vrátane subjectu, units, working-set/RSS/cache alebo usage semantics, scrape freshness, aggregation a request/limit denominatora. Pozri [Requests, limits a QoS](../docs/09-kubernetes/requests-limits-qos.md).

## Resource observation matrix

Mapa evidence cez demand, source/admission, Pod calculation, scheduling reservation, cgroup, usage, failure, QoS, autoscaling a business boundaries. Pozri [Requests, limits a QoS](../docs/09-kubernetes/requests-limits-qos.md).

## Scheduler profile generation

Versionovaná kube-scheduler konfigurácia určujúca active plugins, weights, added affinity a ďalšie resolved placement semantics pre daný `schedulerName`. Pozri [Scheduling](../docs/09-kubernetes/scheduling.md).

## Scheduler score vector

Per-Node výsledky active scoring plugins a ich váh po tom, čo hard filtering vytvoril feasible-Node set. Pozri [Scheduling](../docs/09-kubernetes/scheduling.md).

## Scheduler reservation subject

Node allocatable a súčet admitted Pod requests/overhead rezervovaných schedulerom pre placement; nie je totožný s live usage. Pozri [Requests, limits a QoS](../docs/09-kubernetes/requests-limits-qos.md).

## Scheduling acceptance verdict

Verdikt, že current Pod generation bola umiestnená podľa reviewed constraints, bezpečne realizovaná kubeletom a prijatá z pohľadu failure-domain a business availability. Pozri [Scheduling](../docs/09-kubernetes/scheduling.md).

## Scheduling lifecycle subject

Súvislý chain od Pod placement intentu cez queue/profile, filtering, scoring a binding po kubelet execution a workload acceptance. Pozri [Scheduling](../docs/09-kubernetes/scheduling.md).

## Scheduling observation matrix

Mapa exact subjects a evidence cez Pod intent, queue, profile, Node inventory, reservations, storage, filter, score, binding a execution boundaries. Pozri [Scheduling](../docs/09-kubernetes/scheduling.md).

## Storage acceptance verdict

Verdikt, že správny PVC/PV/backing asset je bezpečne attached a mounted, obsahuje accepted data generation, má jediného oprávneného writera a obnoviteľný backup. Pozri [Volumes, PV, PVC a StorageClass](../docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Storage fencing epoch

Monotónna application alebo storage-provider generation určujúca, ktorý writer smie aktuálne meniť persistentné dáta po failoveri alebo replacement-e. Pozri [Volumes, PV, PVC a StorageClass](../docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Storage observation matrix

Mapa evidence cez data identity, claim, StorageClass, PV, backend asset, scheduling, attachment, mount, application, backup a cleanup boundaries. Pozri [Volumes, PV, PVC a StorageClass](../docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## StorageClass generation

Versionovaný provisioning contract zahŕňajúci CSI provisioner, parameters, reclaim policy, binding mode, expansion a allowed topology. Pozri [Volumes, PV, PVC a StorageClass](../docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Topology-binding subject

Koordinované rozhodnutie medzi Pod constraints, scheduler selected Node/topology, StorageClass binding mode a provisioned PV affinity. Pozri [Volumes, PV, PVC a StorageClass](../docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## VolumeAttachment generation

Konkrétny Kubernetes attach intent a status medzi CSI volumeHandle a Node UID, oddelený od external provider attachment session. Pozri [Volumes, PV, PVC a StorageClass](../docs/09-kubernetes/volumes-pv-pvc-storageclass.md).