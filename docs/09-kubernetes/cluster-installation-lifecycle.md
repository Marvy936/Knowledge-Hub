# Cluster installation a lifecycle

Kubernetes cluster nie je výsledok jedného úspešného `kubeadm init`. Je to versionovaný platformový subject tvorený infraštruktúrou, failure domains, host image-om, PKI, etcd, control-plane endpointom, Node bootstrapom, CNI/CSI a ďalšími add-ons. Cluster je prijatý až vtedy, keď jeho management plane, workload plane, recovery set a day-2 ownership fungujú ako jeden lifecycle.

Táto kapitola používa jeden dominantný model:

```text
platform intent, SLO a ownership matrix
→ cluster architecture a immutable generation contract
→ infrastructure, network a host baseline
→ PKI, etcd a stable control-plane endpoint
→ control-plane bootstrap
→ worker join a Node identity
→ CNI/CSI/DNS/Service/policy add-on generations
→ capability a workload acceptance
→ certificate, Node, backup a upgrade lifecycle
→ replacement, disaster recovery a decommission closure
```

## 1. Atlas production cluster subject

Atlas Payments cluster `atlas-prod-eu2` je self-managed kubeadm platforma:

```text
Kubernetes minor/patch: pinned release generation
control-plane endpoint: api.atlas-prod.internal:6443
control-plane Nodes: 3, rozdelené medzi failure domains
etcd: stacked, 3-member quorum
Pod/Service CIDRs a cluster domain: immutable architecture fields
runtime/cgroup model: versionovaný Node image
CNI, CSI, CoreDNS a policy stack: pinned add-on matrix
PKI a ServiceAccount signing keys: explicitný owner
recovery set: etcd + PKI/encryption/add-on/infra/application data
```

Cluster generation nie je iba Kubernetes version. Obsahuje:

- infra a host-image release;
- kubeadm config;
- control-plane component images/configs;
- etcd topology/version;
- PKI a trust generation;
- CNI/CSI/DNS/Service dataplane versions;
- admission a security policy generations;
- Node pool templates;
- backup/restore runbook generation.

## 2. Ownership pred bootstrapom

Managed a self-managed platformy majú odlišný ownership, ale žiadna nie je „bez prevádzky“.

Pre každú capability urč:

| Capability | Provider | Platform team | Application team |
|---|---|---|---|
| Control-plane availability | | | |
| etcd backup/restore | | | |
| Node image a patching | | | |
| CNI/CSI/DNS | | | |
| cluster upgrades | | | |
| workload manifests | | | |
| application data backup | | | |
| identity/RBAC/policy | | | |
| incident escalation | | | |

Nejasný owner sa prejaví pri certifikáte, add-on upgrade, restore alebo cloud resource cleanup-e.

## 3. Architecture contract

Pred vytvorením hosts musí byť explicitné:

```text
supported Kubernetes version a upgrade path
control-plane endpoint a load-balancer ownership
stacked alebo external etcd
member/Node count a skutočné failure domains
Pod/Service CIDRs, IP families a cluster domain
runtime a cgroup driver
CNI, policy a Service dataplane
CSI, StorageClasses a topology
identity provider, CA a signing-key ownership
encryption-at-rest/KMS
backup RPO/RTO a restore target
decommission a credential-revocation model
```

CIDR, cluster domain, PKI root a storage topology majú vysoký migration cost. Nesmú vzniknúť ako náhodný default bootstrap toolu.

## 4. Infrastructure a host generation

Node musí vzniknúť z reprodukovateľného baseline-u:

- OS/kernel a security policy;
- container runtime a CRI socket;
- cgroup a resource-manager config;
- routes, firewall, DNS a time sync;
- disk/filesystem/inode capacity;
- CNI-required modules a sysctls;
- package/image mirror a signature policy;
- kubelet configuration a credential bootstrap.

Ručne opravený host je nová, často nezdokumentovaná generation. Preferuj immutable image alebo automatizovaný host convergence s conformance testom.

## 5. PKI a control-plane endpoint

Stable endpoint je cluster API identity. API server certificates, kubeconfigs, bootstrap discovery a load balancer musia používať rovnaký contract.

Dôležité trust subjects:

- Kubernetes CA;
- API server serving cert a SAN inventory;
- API server client identities pre kubelet a etcd;
- etcd peer/server/client PKI;
- front-proxy CA;
- ServiceAccount signing keys;
- administrator a controller kubeconfigs.

Certificate file na disku nie je loaded certificate. Rotation sa uzatvára až po reload-e všetkých consumers a testovaní old/new trust behavioru.

## 6. Etcd a failure domains

Stacked etcd zdieľa host a failure domain s control plane. External etcd oddeľuje lifecycle, ale pridáva hosts, PKI, networking a upgrade complexity.

Quorum availability závisí od majority a fyzického umiestnenia. Tri VM v jednej zone nie sú tri nezávislé failure domains.

Pred control-plane maintenance over:

```text
member list a health
leader a quorum margin
fsync/commit latency
snapshot freshness a restore rehearsal
API server backend inventory
certificate expiry
```

## 7. Control-plane bootstrap

Kubeadm typicky vytvorí PKI/kubeconfigs, static Pod manifests, stacked etcd, bootstrap/RBAC resources, CoreDNS a kube-proxy resources podľa configu. Nevytvorí však automaticky úplnú produkčnú platformu.

Authoritative input má byť versionovaný kubeadm config, nie jednorazový command line. Static Pod manifests pod `/etc/kubernetes/manifests` sú executable control-plane state; lokálna odlišná editácia vytvára component drift.

Bootstrap success nepreukazuje:

- Pod networking;
- storage provisioning;
- policy enforcement;
- external API endpoint failover;
- application data recovery;
- supported add-on matrix.

## 8. Node join a identity

Join je trust establishment:

```text
prepared host generation
→ discovery stable API endpointu a CA
→ bootstrap credential
→ CSR/Node identity
→ kubelet config a certificates
→ Node object
→ CNI/CSI/DaemonSet capability realization
→ workload acceptance
```

Bootstrap tokens majú byť krátkodobé, auditované a po použití zrušené alebo expirované. Node `Ready=True` je iba časť acceptance. Over CNI, Service dataplane, CSI, labels/taints, DNS, time, runtime a replacement behavior.

## 9. Add-on dependency graph

Prakticky použiteľný cluster potrebuje kompatibilnú zostavu:

```text
CNI/IPAM/policy
Service dataplane
CoreDNS alebo NodeLocal DNS
CSI a StorageClasses
metrics pipeline
Ingress/Gateway
admission/security policy
logging/monitoring
image/secret integrations
```

Add-on je cluster-critical release. Každý potrebuje image digest, config generation, supported Kubernetes matrix, staged rollout, observation points a recovery postup.

API server môže byť zelený, zatiaľ čo cluster nedokáže vytvoriť Pod sandbox, pripojiť volume alebo resolvovať Service.

## 10. Cluster acceptance matrix

Po bootstrap-e testuj capability, nie iba component process:

| Oblasť | Acceptance evidence |
|---|---|
| API | read, write, watch cez každý LB/backend path |
| etcd | quorum, leader, latency, snapshot |
| Nodes | join, Ready, restart a replacement |
| CNI | same/cross-Node flow, policy, MTU |
| Service/DNS | ClusterIP, EndpointSlice a DNS fresh lookup |
| CSI | provision, attach, mount, detach a restore |
| Security | RBAC, PSA a forbidden operation tests |
| Workload | rollout, drain, HPA a business journey |
| Recovery | real artifact restore rehearsal |

Cluster `Ready` je verdict nad touto maticou, nie jeden boolean.

## 11. Day-2 lifecycle

### Certificate rotation

Sleduj expiry, issuer, SANs, loaded generation a consumer restart. ServiceAccount signing-key rotation má odlišný overlap a token-validity model než TLS certificate renewal.

### Node replacement

```text
new versioned Node
→ join
→ capability conformance
→ workload admission
→ cordon/drain old Node
→ storage/network cleanup
→ delete Node identity a host
→ revoke credentials
```

`kubectl drain` musí rešpektovať PDB, StatefulSet/fencing, local data, volume detach a replacement capacity.

### Control-plane maintenance

Mení sa sekvenčne podľa quorum a endpoint capacity. Nikdy neodstavuj naraz majority etcd členov ani všetky API backends.

### Backup a upgrade

Backup scope zahŕňa etcd, PKI/encryption, configs, add-ons, infra a application data. Upgrade používa samostatnú kapitolu, ale patrí do cluster generation lifecycle-u od prvého dňa.

## 12. Decommission lifecycle

`kubeadm reset` čistí časť lokálneho kubeadm state-u. Neodstráni automaticky cloud VM, disks, LB, DNS, firewall, IAM ani application data.

Decommission subject musí uzavrieť:

1. traffic a nové writes;
2. final application backups a retention;
3. workloads/PVs/external resources;
4. Nodes a control-plane identities;
5. certificates, bootstrap tokens a cloud credentials;
6. LB, IP, DNS, firewall a IAM;
7. logs/audit/compliance evidence;
8. hosts, disks a encryption keys.

## 13. Causal walkthrough: časť API requestov zlyháva po control-plane replacement-e

### Symptom

Po výmene `cp-1` za `cp-4` prejde `kubectl get nodes` väčšinou úspešne, ale približne tretina nových TLS spojení na `api.atlas-prod.internal:6443` zlyhá. Existujúce workloads naďalej obsluhujú traffic.

### Exact subject

Fixuj:

- cluster generation a kubeadm config hash;
- stable endpoint, DNS a LB backend generation;
- všetky API server Pod UIDs/container IDs;
- serving certificate fingerprint/SAN/expiry loaded na každom backende;
- Node host image a clock generation;
- etcd member/leader/quorum state;
- client request timestamp a selected backend;
- admission/add-on state oddelene od TLS pathu.

### Competing hypotheses

1. LB stále smeruje na odstránený cp-1;
2. cp-4 API static Pod nebeží;
3. cp-4 serving cert nemá stable endpoint SAN;
4. cp-4 má expirovaný alebo iný CA-signed cert;
5. clock skew robí certifikát neplatný;
6. firewall blokuje iba cp-4;
7. cp-4 nevie komunikovať s etcd;
8. etcd stratilo quorum;
9. DNS vracia stale API address;
10. klient používa stale kubeconfig alebo proxy.

### Discriminating observations

Testuj TLS a `/readyz` cez každý backend samostatne, porovnaj cert fingerprints/SANs, static Pod manifesty, kubeadm config, host clocks, LB health a etcd health.

Finding:

```text
cp-4 vznikol zo stale kubeadm configu
→ local API cert bol vydaný iba pre cp-4 host/IP
→ LB health testoval TCP, preto backend označil healthy
→ klient s hostname api.atlas-prod.internal odmietol cert
→ iba requesty vybrané na cp-4 zlyhávali
```

API process a etcd boli zdravé; zlyhal endpoint identity contract.

### Containment

- odstráň cp-4 z LB rotation bez zmazania evidence;
- pozastav ďalšie control-plane replacementy;
- zachovaj certificates, manifests, kubeadm config a LB logs;
- over quorum margin pred zásahom;
- neznižuj TLS verification ani nemeníš klientsky hostname.

### Authoritative recovery

- obnov jeden canonical kubeadm/PKI source;
- vydať API cert s approved stable endpoint a Node SAN inventory;
- reloadni/reštartuj iba affected API server controlled spôsobom;
- over backend `/readyz`, etcd connectivity a LB semantic health;
- znovu pridaj cp-4 do rotation;
- zosúlaď host/bootstrap pipeline a odstráň stale config source.

### Verify original a forbidden outcomes

Over:

1. read/write/watch funguje cez každý backend;
2. klient overí rovnakú CA a stable endpoint SAN;
3. etcd quorum a latency sú zdravé;
4. scheduler/controller leadership a admission fungujú;
5. Node join, CNI, CSI a DNS sú nedotknuté;
6. payment rollout a end-to-end journey uspejú;
7. odstránený/stale backend a starý cert už nie sú používané;
8. ďalší Node replacement reprodukuje rovnaký cluster generation contract.

### Earlier controls

Použi immutable kubeadm config, preflight cert-SAN test, semantic LB health, per-backend synthetic, PKI inventory, control-plane conformance test, quorum-aware change gate a replacement rehearsal.

## 14. Ďalšie failure boundaries

### `kubeadm init` zlyhá v preflight

Oprav runtime, cgroups, ports, hostname, existing state alebo firewall. Ignorovanie checku bez cause modelu iba presunie failure ďalej.

### Node sa joinne, ale zostáva `NotReady`

Join/identity prešli. Over CNI config, Pod CIDR, runtime, kubelet a Node conditions.

### CoreDNS je `Pending`

Môže ísť o chýbajúci CNI, capacity, taints alebo scheduler constraint. DNS je downstream symptom cluster bootstrapu.

### Certifikát bol obnovený, ale component stále zlyháva

File generation sa zmenila, loaded generation nie. Over reload a všetky replicas/clients.

### Tri control-plane Nodes neprežijú jednu zone failure

Count nie je failure-domain diversity. Oprav topology a recovery plan, nie iba replica number.

### Add-on upgrade rozbije workload plane

API môže zostať healthy. Hodnoť CNI/CSI/DNS capability canaries a staged rollback.

## 15. Referenčný katalóg

### Cluster generation inventory

```text
infrastructure a host image
Kubernetes/control-plane/etcd versions
kubeadm/component configs
PKI a endpoint identity
Node pools a runtime
CNI/CSI/DNS/Service/policy add-ons
backup/recovery artifacts
ownership a support matrix
```

### Lifecycle operations

- bootstrap;
- Node/control-plane join;
- certificate renewal/rotation;
- Node replacement a drain;
- add-on change;
- backup/restore;
- upgrade;
- decommission.

## 16. Anti-patterny

- produkčný single-control-plane cluster bez recovery;
- tri replicas v jednom failure domain-e;
- mutable bootstrap URL alebo unpinned images;
- ručne odlišné control-plane Nodes;
- TCP-only API LB health;
- backup iba etcd bez PKI/encryption/application data;
- `kubeadm reset` považovaný za decommission;
- Node `Ready` považovaný za úplný cluster acceptance;
- add-ons bez compatibility a rollback modelu.

## 17. Kontrolné otázky

1. Čo tvorí exact cluster generation?
2. Ktoré architecture fields majú vysoký migration cost?
3. Prečo stable API endpoint musí byť v PKI aj LB contracte?
4. Ako sa líši count control-plane Nodes od failure-domain resilience?
5. Ktoré capability tests musia nasledovať po Node join-e?
6. Prečo kubeadm config nie je celý day-2 source of truth?
7. Ako odlíšiš API health od workload-plane health?
8. Čo musí obsahovať Node replacement closure?
9. Prečo etcd snapshot nestačí na cluster recovery?
10. Ako overíš cluster decommission bez orphan resources a credentials?

## Glossary impact

Relevantné pojmy: Kubernetes cluster generation, platform ownership matrix, architecture contract, host baseline generation, control-plane endpoint identity, PKI generation, add-on release matrix, cluster capability acceptance, Node replacement subject, certificate loaded generation, cluster recovery set, semantic API health, platform decommission subject a subject-bound cluster verification.

## Oficiálna dokumentácia

- [Production environment](https://kubernetes.io/docs/setup/production-environment/)
- [Bootstrapping clusters with kubeadm](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/)
- [Creating a cluster with kubeadm](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/create-cluster-kubeadm/)
- [Creating highly available clusters with kubeadm](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/high-availability/)
- [PKI certificates and requirements](https://kubernetes.io/docs/setup/best-practices/certificates/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: ResourceQuota a LimitRange](resourcequota-limitrange.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: etcd backup a restore →](etcd-backup-restore.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
