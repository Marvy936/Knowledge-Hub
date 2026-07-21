# Kubernetes

Táto sekcia vysvetľuje Kubernetes od cluster architektúry, API object modelu a reconciliation loops cez workloads, networking, storage, scheduling, security a autoscaling až po cluster lifecycle, upgrades, observability a troubleshooting. Cieľom nie je memorovať `kubectl` príkazy alebo YAML fields, ale rozumieť tomu, ktorý component vlastní konkrétny stav, ako sa desired state mení na running workload a kde hľadať failure evidence.

Kubernetes nadväzuje na Linux namespaces/cgroups, container runtime a OCI model, networking, storage, security, CI/CD, Infrastructure as Code a observability. Docker je užitočný základ pre images a local container lifecycle, ale Kubernetes používa vlastný API, scheduler, controllers, CRI/CNI/CSI integrations a multi-node failure model.

## Predpoklady

Odporúča sa najprv dokončiť:

- [Linux and Systems](../01-linux-and-systems/README.md),
- [Networking and Web Fundamentals](../02-networking-and-web/README.md),
- [CI/CD and Release Engineering](../05-ci-cd-and-release/README.md),
- [Infrastructure as Code and Configuration Management](../07-infrastructure-as-code-and-configuration-management/README.md),
- [Container Fundamentals and Docker](../08-container-fundamentals-and-docker/README.md).

## Odporúčané poradie

1. [Kubernetes architecture](kubernetes-architecture.md)
2. [API a object model](api-object-model.md)
3. [Desired state a reconciliation loops](desired-state-reconciliation-loops.md)
4. [Control plane components](control-plane-components.md)
5. [Worker node components](worker-node-components.md)
6. [Pod](pod.md)
7. [ReplicaSet](replicaset.md)
8. [Deployment](deployment.md)
9. [StatefulSet](statefulset.md)
10. [DaemonSet](daemonset.md)
11. [Job a CronJob](job-cronjob.md)
12. [ConfigMap a Secret](configmap-secret.md)
13. [ServiceAccount](serviceaccount.md)
14. [Service a EndpointSlice](service-endpointslice.md)
15. [Ingress a Gateway API](ingress-gateway-api.md)
16. [Cluster DNS](cluster-dns.md)

Nasledujúci blok prejde na CNI a NetworkPolicy, volumes/PV/PVC/StorageClass, scheduling, requests/limits/QoS a probes. Potom sekcia rozvinie taints, affinity, topology, autoscaling, RBAC, Pod security, quotas, cluster lifecycle, etcd recovery, upgrades, observability a troubleshooting.

## Cieľ zvládnutia

Po dokončení aktuálneho bloku má byť možné:

- vysvetliť Kubernetes ako API-driven control system pre deklaratívne riadenie workloads a resources,
- rozlíšiť control plane, worker nodes, cluster add-ons a external integrations,
- popísať celý request/reconciliation flow od `kubectl apply` cez API, controllers, scheduler a kubelet až po container process,
- vysvetliť API-centric hub-and-spoke communication model,
- rozlíšiť responsibilities `kube-apiserver`, etcd, `kube-scheduler`, `kube-controller-manager`, cloud-controller-manager, kubelet, runtime a network/storage plugins,
- vysvetliť etcd quorum, disk-latency, backup, restore a encryption-at-rest hranice,
- rozlíšiť scheduler placement decision od kubelet execution,
- vysvetliť cluster failure domains, HA control plane, leader election a Lease objects,
- rozlíšiť self-managed a managed control plane ownership,
- vysvetliť static Pods a mirror Pods v self-hosted control-plane topológii,
- rozlíšiť Kubernetes resource type a konkrétny object,
- používať Group/Version/Kind a Group/Version/Resource mentálny model,
- rozlíšiť namespaced a cluster-scoped resources,
- vysvetliť `apiVersion`, `kind`, `metadata`, `spec` a `status`,
- pracovať s object identity cez name, namespace, UID, resourceVersion a generation,
- rozlíšiť labels/selectors a annotations,
- vysvetliť list/watch, optimistic concurrency a API discovery,
- interpretovať `observedGeneration`, conditions, Events a managedFields,
- vysvetliť server-side apply a field ownership konflikty,
- rozlíšiť subresources ako `/status`, `/scale`, `/exec` a `/log`,
- vysvetliť ownerReferences, garbage collection, deletion propagation a finalizers,
- rozlíšiť CRD schema od controller/operator behavior,
- vysvetliť desired, observed a actual state,
- popísať level-based reconciliation cez list/watch, informer/cache a work queue,
- navrhnúť idempotentný reconcile s retry, backoff a partial-failure recovery,
- vysvetliť eventual consistency a controller chaining,
- rozlíšiť synchronous admission od asynchronous reconciliation,
- interpretovať generation lag, reconcile queue pressure a stuck finalizer,
- vysvetliť API request pipeline cez authentication, authorization, admission, validation a persistence,
- diagnostikovať API server readiness, etcd latency/quorum, scheduler queue a controller-manager lag,
- vysvetliť admission webhook ako synchronous control-plane dependency,
- rozlíšiť stacked a external etcd a statické/externé control-plane deployment modely,
- vysvetliť Node object, capacity, allocatable, conditions, heartbeats a Leases,
- popísať kubelet responsibilities a Pod sync lifecycle,
- vysvetliť Container Runtime Interface, Pod sandbox, CNI, kube-proxy/alternate Service dataplane a CSI node plugin,
- používať `crictl` ako CRI diagnostickú vrstvu namiesto predpokladu Docker Engine-u,
- rozlíšiť Node pressure, cgroup OOM, kubelet eviction, disk/inode exhaustion a image garbage collection,
- vykonať bezpečný cordon/drain/uncordon maintenance workflow,
- diagnostikovať `NodeNotReady`, `FailedCreatePodSandBox`, `ContainerCreating`, `ImagePullBackOff` a node-local Service failure,
- vysvetliť Pod ako co-scheduling, network a lifecycle envelope pre jeden alebo viac containers,
- rozlíšiť Pod identity, Pod sandbox, Pod IP, container state, Pod phase a Pod conditions,
- vysvetliť init, sidecar a ephemeral containers a ich lifecycle/security trade-offy,
- rozlíšiť container restart a Pod replacement,
- navrhnúť commands/args, environment, resources, security context, volumes a ServiceAccount pre Pod,
- vysvetliť startup, liveness a readiness probes a Pod readiness gates,
- popísať graceful Pod termination, lifecycle hooks a termination grace period,
- rozlíšiť priamo vytvorený Pod, controller-managed Pod, Pod template a static Pod,
- systematicky diagnostikovať Pod podľa fázy `Pending`, `ContainerCreating`, `Running/NotReady`, `CrashLoopBackOff`, `ImagePullBackOff`, `Terminating` alebo `Evicted`,
- vysvetliť ReplicaSet ako controller požadovaného počtu matching Podov,
- navrhnúť stabilný selector a rozlíšiť Pod adoption, orphaning a controller ownership,
- rozlíšiť container restart od replacement Podu a replica count od readiness/availability,
- vysvetliť ownership chain Deployment → ReplicaSet → Pod,
- rozlíšiť RollingUpdate a Recreate Deployment stratégie,
- navrhnúť `maxSurge`, `maxUnavailable`, `minReadySeconds` a progress deadline podľa capacity a availability požiadaviek,
- interpretovať rollout revisions, conditions, pause/resume, history a rollback hranice,
- vysvetliť vplyv readiness, termination overlap, PDB, HPA a mixed-version compatibility na Deployment rollout,
- vysvetliť StatefulSet ordinal, stable network identity, headless Service a per-replica PVC,
- rozlíšiť `OrderedReady`, `Parallel`, `RollingUpdate`, `OnDelete` a partitioned rollout,
- navrhnúť StatefulSet storage, PVC retention, topology, quorum, fencing, backup a upgrade model,
- rozlíšiť stabilnú logical identity od Pod UID, IP a process identity,
- vysvetliť DaemonSet desired count odvodený od eligible Nodes,
- navrhnúť node selectors, affinity, tolerations, priority a rolling update pre node-local agent,
- vyhodnotiť host mounts, devices, host networking, per-node resource overhead a bootstrap dependencies DaemonSetu,
- diagnostikovať desired/current/ready/available/misscheduled DaemonSet status,
- vysvetliť Job completion, `parallelism`, `completions`, retry, backoff a deadline semantics,
- rozlíšiť NonIndexed, Indexed a work-queue batch model,
- navrhnúť idempotentnú batch prácu s checkpointom, deduplication a bezpečnými side effects,
- vysvetliť CronJob schedule, time zone, starting deadline, concurrency policy, suspend a history limits,
- odôvodniť, prečo Job/CronJob neposkytujú end-to-end exactly-once execution,
- rozlíšiť ConfigMap a Secret podľa citlivosti, API semantics a consumer contractu,
- používať `data`, `binaryData`, `stringData`, environment injection, `envFrom` a volume projections,
- vysvetliť rozdiel medzi environment a mounted-file update semantics vrátane `subPath` limitu,
- navrhnúť immutable/versioned configuration a explicitný checksum-driven Pod rollout,
- vysvetliť, prečo base64 nie je encryption a prečo Secret vyžaduje RBAC, etcd encryption, audit a node security,
- navrhnúť credential rotation, TLS Secret a imagePullSecret lifecycle bez plaintext leakage,
- vyhodnotiť external secret provider a workload identity trade-offy,
- vysvetliť ServiceAccount ako namespaced workload identity oddelenú od RBAC permissions,
- používať bound projected tokens, TokenRequest, audience, expiry a token rotation,
- rozhodnúť, kedy vypnúť `automountServiceAccountToken`,
- diagnostikovať `401` authentication oproti `403` authorization failure,
- navrhnúť least-privilege ServiceAccount a external workload identity federation,
- vysvetliť Service ako stabilnú logical network identity pre meniacu sa Pod population,
- rozlíšiť Service selector, port, targetPort a EndpointSlice backend model,
- vysvetliť ClusterIP, NodePort, LoadBalancer, ExternalName a headless Service,
- interpretovať EndpointSlice readiness, serving, terminating, topology a address-family metadata,
- vysvetliť kube-proxy alebo alternate Service dataplane a oddeliť DNS od packet forwarding-u,
- diagnostikovať Service cez selector → EndpointSlice → readiness → targetPort → dataplane → application chain,
- vysvetliť Ingress, IngressClass a controller/dataplane dependency,
- navrhnúť host/path/TLS routing bez neauditovaných implementation-specific annotations,
- rozlíšiť GatewayClass, Gateway, listener a Route resources,
- používať `parentRefs`, `backendRefs`, `allowedRoutes`, ReferenceGrant a Route status conditions,
- porovnať Ingress a Gateway API podľa role separation, portability, protocols a traffic-policy capabilities,
- diagnostikovať routing cez DNS/load-balancer → Gateway/Ingress → Service → EndpointSlice → Pod,
- vysvetliť cluster DNS request path cez Pod resolver, DNS Service, CoreDNS a upstream resolver,
- používať Service FQDN, namespace search domains, `ndots`, headless records a SRV records,
- rozlíšiť DNS policies `ClusterFirst`, `Default`, `ClusterFirstWithHostNet` a `None`,
- vyhodnotiť caching, negative caching, UDP/TCP fallback, NodeLocal DNSCache a resolver loop failure,
- systematicky odlíšiť cluster-local DNS, upstream DNS, Service dataplane a application connectivity problém.

## Stav

| Téma | Status | Úroveň |
|---|---|---|
| Kubernetes architecture | Learning | L2 |
| API a object model | Learning | L2 |
| Desired state a reconciliation loops | Learning | L2 |
| Control plane components | Learning | L2 |
| Worker node components | Learning | L2 |
| Pod | Learning | L2 |
| ReplicaSet | Learning | L2 |
| Deployment | Learning | L2 |
| StatefulSet | Learning | L2 |
| DaemonSet | Learning | L2 |
| Job a CronJob | Learning | L2 |
| ConfigMap a Secret | Learning | L2 |
| ServiceAccount | Learning | L2 |
| Service a EndpointSlice | Learning | L2 |
| Ingress a Gateway API | Learning | L2 |
| Cluster DNS | Learning | L2 |