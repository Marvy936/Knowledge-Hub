# Kubernetes security, governance, cluster lifecycle and recovery glossary entries

## Admitted security contract

Resolved Pod a container security configuration po defaultingu a admission policy, ktorá sa stáva vstupom pre runtime. Nie je totožná so source manifestom ani s effective process authority. Pozri [SecurityContext a Pod Security](../docs/09-kubernetes/securitycontext-pod-security.md).

## API-state generation

Konzistentná Kubernetes object-state generácia viazaná na etcd cluster identity, revision, encryption configuration a čas recovery pointu. Pozri [etcd backup a restore](../docs/09-kubernetes/etcd-backup-restore.md).

## Architecture contract — Kubernetes cluster

Versionovaný súbor rozhodnutí o endpoint identity, etcd topology, failure domains, CIDRs, runtime, CNI/CSI, PKI, storage, backup a upgrade modeli. Pozri [Cluster installation a lifecycle](../docs/09-kubernetes/cluster-installation-lifecycle.md).

## Capability inventory — Kubernetes workload security

Explicitný zoznam kernel, filesystem, network, device, host a API operations, ktoré workload potrebuje; používa sa na odvodenie minimálneho runtime authority contractu. Pozri [SecurityContext a Pod Security](../docs/09-kubernetes/securitycontext-pod-security.md).

## Certificate loaded generation

Certificate/trust material skutočne načítaný konkrétnym API serverom, kubeletom, etcd memberom alebo klientom; môže zaostávať za file generation na disku. Pozri [Cluster installation a lifecycle](../docs/09-kubernetes/cluster-installation-lifecycle.md).

## Cluster capability acceptance

Verdikt, že current cluster generation poskytuje API read/write/watch, etcd quorum, Node execution, CNI/CSI/DNS, security policy, workload rollout a recovery capabilities. Pozri [Cluster installation a lifecycle](../docs/09-kubernetes/cluster-installation-lifecycle.md).

## Cluster generation — Kubernetes

Exact platform release tvorený infra/host image-om, Kubernetes a etcd verziami, kubeadm/component configom, PKI, Node pools, add-ons, policy a recovery-set generations. Pozri [Cluster installation a lifecycle](../docs/09-kubernetes/cluster-installation-lifecycle.md).

## Cluster recovery set

Koordinovaný súbor etcd snapshotu, PKI, encryption/KMS materialu, component configs, infra/add-on source, image artifacts, application-data backups a runbooku potrebný na obnovu. Pozri [Cluster installation a lifecycle](../docs/09-kubernetes/cluster-installation-lifecycle.md) a [etcd backup a restore](../docs/09-kubernetes/etcd-backup-restore.md).

## Control-plane endpoint identity

Stable API hostname/address, load-balancer backend inventory a serving-certificate SAN/trust contract používaný klientmi a Node bootstrapom. Pozri [Cluster installation a lifecycle](../docs/09-kubernetes/cluster-installation-lifecycle.md).

## Cross-system recovery generation

Koordinovaná časová a compatibility väzba medzi restored Kubernetes API state-om, application data, queues, external resources, secrets a deployment/schema generations. Pozri [etcd backup a restore](../docs/09-kubernetes/etcd-backup-restore.md).

## Effective process authority — Kubernetes

Skutočná runtime autorita procesu po aplikovaní UID/GID/groups, capabilities, `no_new_privs`, seccomp, LSM, mounts, devices, host namespaces a runtime socketov. Pozri [SecurityContext a Pod Security](../docs/09-kubernetes/securitycontext-pod-security.md).

## External-state reconciliation — etcd recovery

Post-restore porovnanie restored Kubernetes objects s cloud disks, load balancermi, DNS, certificates, IAM, databases a ďalšími external resources pred povolením controller mutations a trafficu. Pozri [etcd backup a restore](../docs/09-kubernetes/etcd-backup-restore.md).

## Filesystem access verdict — Kubernetes

Výsledok kombinácie process UID/GID/groups, Unix permissions/ACL, mount flags, CSI ownership, user-namespace mapping a SELinux/AppArmor policy pre exact path a operation. Pozri [SecurityContext a Pod Security](../docs/09-kubernetes/securitycontext-pod-security.md).

## Forbidden-authority verification

Negatívny recovery test dokazujúci, že workload po remediation nevie použiť host namespaces, runtime sockets, devices, forbidden capabilities, privileged Pod creation alebo staré credentials. Pozri [SecurityContext a Pod Security](../docs/09-kubernetes/securitycontext-pod-security.md).

## Governance acceptance verdict — Kubernetes namespace

Verdikt, že LimitRange/ResourceQuota policy poskytuje správne admitted resources, fairness, rollout/HPA/recovery headroom, object bounds a business SLO bez neželaných defaultov. Pozri [ResourceQuota a LimitRange](../docs/09-kubernetes/resourcequota-limitrange.md).

## Host baseline generation — Kubernetes

Versionovaný Node OS/kernel/runtime/cgroup/network/storage/security/kubelet baseline používaný pri join-e a replacement-e. Pozri [Cluster installation a lifecycle](../docs/09-kubernetes/cluster-installation-lifecycle.md).

## Host-control mount

Mounted path alebo socket, napríklad container-runtime API, ktorý poskytuje authority nad Node-om alebo inými workloads aj pri read-only filesystem mount flags. Pozri [SecurityContext a Pod Security](../docs/09-kubernetes/securitycontext-pod-security.md).

## Informer relist boundary — recovery

Bod, v ktorom controller/client po etcd restore zahodí stale watch assumptions a načíta fresh authoritative object set, typicky po compaction/revision semantics. Pozri [etcd backup a restore](../docs/09-kubernetes/etcd-backup-restore.md).

## Kernel enforcement generation — Kubernetes

Exact seccomp, AppArmor, SELinux a related Node/runtime policy state použitý pre konkrétny Pod/container operation. Pozri [SecurityContext a Pod Security](../docs/09-kubernetes/securitycontext-pod-security.md).

## LimitRange generation

UID/generation a resolved ruleset, ktorý pri admission-e doplnil alebo validoval requests, limits alebo PVC bounds pre konkrétny object request. Pozri [ResourceQuota a LimitRange](../docs/09-kubernetes/resourcequota-limitrange.md).

## Namespace capacity envelope

Súčet baseline, rollout surge, HPA burst, Node-drain replacement, batch overlap a emergency recovery capacity, ktorú quota aj cluster musia umožniť. Pozri [ResourceQuota a LimitRange](../docs/09-kubernetes/resourcequota-limitrange.md).

## Namespace governance subject

Exact namespace UID, owner, quota/LimitRange generations, workload request, admitted delta, usage state a downstream capacity context. Pozri [ResourceQuota a LimitRange](../docs/09-kubernetes/resourcequota-limitrange.md).

## Node replacement subject — Kubernetes cluster

Controlled transition medzi old a new Node generation vrátane join identity, capability conformance, drain, storage/network cleanup, object deletion a credential revocation. Pozri [Cluster installation a lifecycle](../docs/09-kubernetes/cluster-installation-lifecycle.md).

## Platform decommission subject

Cluster/Node/infra/data/credential inventory a verified cleanup transition, ktorý uzatvára traffic, resources, identities, backups, audit a external infrastructure. Pozri [Cluster installation a lifecycle](../docs/09-kubernetes/cluster-installation-lifecycle.md).

## Platform ownership matrix — Kubernetes

Explicitné rozdelenie zodpovednosti za control plane, etcd, Nodes, add-ons, upgrades, identity, application data, recovery a incident support medzi provider/platform/application owners. Pozri [Cluster installation a lifecycle](../docs/09-kubernetes/cluster-installation-lifecycle.md).

## Privileged exception subject

Exact namespace/workload/image/owner/capability/Node/RBAC/expiry contract povoľujúci authority nad štandardný Pod Security profil. Pozri [SecurityContext a Pod Security](../docs/09-kubernetes/securitycontext-pod-security.md).

## PSA admission verdict

`enforce`, `audit` alebo `warn` výsledok pre exact Pod request, namespace policy level a pinned Pod Security Standards version. Pozri [SecurityContext a Pod Security](../docs/09-kubernetes/securitycontext-pod-security.md).

## PSS policy generation

Pod Security Standards level a version používané ako konkrétny admission contract pre namespace alebo cluster policy. Pozri [SecurityContext a Pod Security](../docs/09-kubernetes/securitycontext-pod-security.md).

## Quota accounting subject

ResourceQuota UID/generation, current `hard`/`used`, exact admitted request delta, scope a allow/reject decision v jednom admission time window. Pozri [ResourceQuota a LimitRange](../docs/09-kubernetes/resourcequota-limitrange.md).

## Quota admission verdict

Server-side rozhodnutie, či effective create/update delta prekračuje matching namespace quota; nastáva pred schedulingom a runtime execution. Pozri [ResourceQuota a LimitRange](../docs/09-kubernetes/resourcequota-limitrange.md).

## Quota recovery headroom

Časť namespace quota zámerne ponechaná pre rollout surge, Node loss, HPA burst, Job overlap a emergency repair/replacement workloads. Pozri [ResourceQuota a LimitRange](../docs/09-kubernetes/resourcequota-limitrange.md).

## Recovery closure — etcd

Verdikt po restore, ktorý potvrdzuje etcd/API/controller convergence, external/application consistency, traffic/business outcome, forbidden old-state outcomes a zaznamenané RPO/RTO. Pozri [etcd backup a restore](../docs/09-kubernetes/etcd-backup-restore.md).

## Recovery-set binding

Trusted väzba snapshotu na PKI, encryption keys, configs, infra/add-ons, application-data backups a restore runbook potrebné pre danú cluster generation. Pozri [etcd backup a restore](../docs/09-kubernetes/etcd-backup-restore.md).

## Repair-versus-restore verdict

Rozhodnutie, či incident pri zachovanom quorum a healthy state-e riešiť member/network/disk/TLS opravou alebo vykonať destructive cluster-state rollback zo snapshotu. Pozri [etcd backup a restore](../docs/09-kubernetes/etcd-backup-restore.md).

## Restored logical cluster

Nová etcd cluster/member identity a clean data-directory generation vytvorená zo snapshotu; nesmie sa neplánovane miešať so starým member state-om. Pozri [etcd backup a restore](../docs/09-kubernetes/etcd-backup-restore.md).

## Revision high-water mark

Najvyššia pre-incident etcd revision, ktorú mohli controllers/clients pozorovať; používa sa pri návrhu bezpečného restore revision bump-u. Pozri [etcd backup a restore](../docs/09-kubernetes/etcd-backup-restore.md).

## Runtime authority generation — Kubernetes

Effective OCI/container runtime security configuration pre konkrétny Pod UID, container ID, Node a RuntimeClass generation. Pozri [SecurityContext a Pod Security](../docs/09-kubernetes/securitycontext-pod-security.md).

## Security evidence matrix — Kubernetes workload

Mapa source manifestu, admitted Podu, runtime configu, process identity/capabilities, kernel audit, mounts/devices, allowed operations, forbidden operations a business outcome. Pozri [SecurityContext a Pod Security](../docs/09-kubernetes/securitycontext-pod-security.md).

## Semantic API health — Kubernetes cluster

Per-backend overenie TLS identity, API read/write/watch, etcd dependency a admission pathu; je silnejšie než TCP listener alebo process health. Pozri [Cluster installation a lifecycle](../docs/09-kubernetes/cluster-installation-lifecycle.md).

## Snapshot evidence manifest

Metadata viažuce snapshot na source cluster/member, revision, hash, key count, size, tool version, time, encryption/PKI generation, storage location a restore-test verdict. Pozri [etcd backup a restore](../docs/09-kubernetes/etcd-backup-restore.md).

## Source-to-admitted resource diff

Porovnanie resources v Git/source Pod template s effective values po LimitRange a ďalších admission mutations. Pozri [ResourceQuota a LimitRange](../docs/09-kubernetes/resourcequota-limitrange.md).

## Traffic-reopen verdict — recovery

Explicitné rozhodnutie otvoriť production traffic až po API, controller, external-resource, application-data, credential a business consistency overení. Pozri [etcd backup a restore](../docs/09-kubernetes/etcd-backup-restore.md).
