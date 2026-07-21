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
17. [CNI a NetworkPolicy](cni-networkpolicy.md)
18. [Volumes, PV, PVC a StorageClass](volumes-pv-pvc-storageclass.md)
19. [Scheduling](scheduling.md)
20. [Requests, limits a QoS](requests-limits-qos.md)
21. [Probes](probes.md)
22. [Taints, tolerations, affinity a topology](taints-tolerations-affinity-topology.md)
23. [HPA a autoscaling](hpa-autoscaling.md)
24. [RBAC](rbac.md)
25. [SecurityContext a Pod Security](securitycontext-pod-security.md)
26. [ResourceQuota a LimitRange](resourcequota-limitrange.md)
27. [Cluster installation a lifecycle](cluster-installation-lifecycle.md)
28. [etcd backup a restore](etcd-backup-restore.md)
29. [Upgrades](upgrades.md)
30. [Logging, metrics a events](logging-metrics-events.md)
31. [Kubernetes troubleshooting](kubernetes-troubleshooting.md)

Kubernetes sekcia je obsahovo dokončená. Lineárna roadmapa ďalej pokračuje sekciou [Helm and CKA](../10-helm-and-cka/README.md).

## Cieľ zvládnutia

Po dokončení sekcie má byť možné:

- vysvetliť Kubernetes ako API-driven control system pre deklaratívne riadenie resources,
- popísať request a reconciliation flow od API requestu cez admission, controllers, scheduler a kubelet až po container process,
- rozlíšiť responsibilities API servera, etcd, scheduleru, controller-managera, kubeletu, runtime-u, CNI a CSI,
- pracovať s GVK/GVR, namespaced a cluster-scoped resources, `spec`, `status`, conditions, generations a field ownershipom,
- vysvetliť list/watch, informer cache, work queue, idempotentný reconcile, eventual consistency, ownerReferences a finalizers,
- diagnostikovať API server, etcd, scheduler, controller-manager, kubelet, runtime a Node conditions podľa správnej vrstvy,
- vysvetliť Pod ako lifecycle, network a scheduling envelope a rozlíšiť container restart od Pod replacementu,
- navrhnúť a diagnostikovať ReplicaSet, Deployment, StatefulSet, DaemonSet, Job a CronJob podľa ich identity a completion modelu,
- rozlíšiť ConfigMap a Secret, ich projection/update semantics, immutable configuration a credential rotation,
- používať ServiceAccounts, bound tokens, audience, RBAC a workload identity podľa least privilege,
- vysvetliť Service, EndpointSlice, ClusterIP, headless Service, NodePort a LoadBalancer dataplane,
- diagnostikovať Ingress alebo Gateway API chain od DNS a load balancera cez Route, Service a EndpointSlice až po Pod,
- vysvetliť cluster DNS, CoreDNS, FQDN, search domains, `ndots`, caching a UDP/TCP fallback,
- rozlíšiť CNI connectivity, IPAM, routing a NetworkPolicy L3/L4 enforcement,
- navrhnúť PV/PVC/StorageClass/CSI lifecycle vrátane topology, reclaim, snapshot, backup a restore hraníc,
- vysvetliť scheduler filter/score/bind flow, requests, taints, affinity, topology spread, priority a preemption,
- rozlíšiť requests, limits, CPU throttling, OOM, ephemeral storage a QoS classes,
- navrhnúť startup, liveness a readiness probes bez restart stormu alebo rollout deadlocku,
- používať taints/tolerations, node affinity, Pod affinity/anti-affinity a topology spread podľa placement účelu,
- vysvetliť HPA desired replica calculation, metrics APIs, stabilization a interakcie s VPA, quota a Node autoscalingom,
- navrhnúť Role, ClusterRole, RoleBinding a ClusterRoleBinding bez wildcard privilege escalation,
- používať SecurityContext, non-root runtime, capabilities, seccomp, SELinux/AppArmor a Pod Security Standards,
- rozlíšiť ResourceQuota a LimitRange a diagnostikovať admission, autoscaling a storage quota konflikty,
- navrhnúť managed alebo self-managed cluster lifecycle vrátane HA topology, PKI, control-plane endpointu, node replacementu a decommissioningu,
- vysvetliť kubeadm bootstrap hranice, static Pods, bootstrap tokens, CNI/add-on sequencing a certificate lifecycle,
- vytvoriť a overiť etcd snapshot, navrhnúť recovery set a vykonať testovaný restore bez zmiešania starého a obnoveného member state-u,
- koordinovať etcd restore s encryption keys, PKI, API server configuration, external resources a application data recovery,
- pripraviť patch alebo minor upgrade cez version skew, deprecation audit, health gate, canary, backup a add-on compatibility,
- vykonať sekvenčný control-plane a Node upgrade alebo immutable node-pool replacement s post-upgrade validation,
- rozlíšiť logs, resource/component/object-state metrics, Events, audit logs a traces,
- navrhnúť cluster-level logging, metrics scraping, cardinality, retention, security a SLO-oriented alerting,
- viesť Kubernetes incident cez presný symptóm, evidence preservation, failure-domain narrowing, controlled reproduction a overenú remediation,
- systematicky diagnostikovať Pod, controller, scheduler, Node, API/admission, DNS/Service, CNI, CSI, resources, probes, HPA a control-plane failures,
- rozpoznať, kedy je potrebný bežný roll-forward, Node replacement alebo skutočný etcd disaster recovery.

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
| CNI a NetworkPolicy | Learning | L2 |
| Volumes, PV, PVC a StorageClass | Learning | L2 |
| Scheduling | Learning | L2 |
| Requests, limits a QoS | Learning | L2 |
| Probes | Learning | L2 |
| Taints, tolerations, affinity a topology | Learning | L2 |
| HPA a autoscaling | Learning | L2 |
| RBAC | Learning | L2 |
| SecurityContext a Pod Security | Learning | L2 |
| ResourceQuota a LimitRange | Learning | L2 |
| Cluster installation a lifecycle | Learning | L2 |
| etcd backup a restore | Learning | L2 |
| Upgrades | Learning | L2 |
| Logging, metrics a events | Learning | L2 |
| Kubernetes troubleshooting | Learning | L2 |