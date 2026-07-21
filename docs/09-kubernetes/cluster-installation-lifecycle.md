# Cluster installation a lifecycle

Kubernetes cluster nevzniká jedným príkazom. Je výsledkom viacerých samostatných lifecycle vrstiev: infrastructure provisioning, host configuration, PKI, control-plane bootstrap, etcd, worker-node bootstrap, CNI/CSI, add-ons, access management, backup, upgrades a decommissioning. Nástroj ako kubeadm vytvorí alebo aktualizuje Kubernetes bootstrap vrstvu, ale nepreberá automaticky celý platformový lifecycle.

## 1. Installation modely

### Managed Kubernetes

Cloud alebo platform provider typicky vlastní časť alebo celý control plane lifecycle:

- API server, scheduler a controller-manager,
- etcd availability a backup podľa služby,
- control-plane patching a upgrade orchestration,
- integration s load balancermi, identity a storage,
- časť observability a support boundary.

Používateľ stále vlastní najmä:

- worker node pools podľa služby,
- Kubernetes resources a workload security,
- add-ons, ktoré provider nespravuje,
- version compatibility applications, controllers a CRDs,
- data backup, restore a business continuity,
- RBAC, network policy, image a supply-chain controls.

Managed neznamená bezprevádzkový.

### Self-managed cluster

Platform team vlastní:

- compute, network, load balancer a DNS,
- host OS a kernel,
- container runtime,
- control plane a etcd,
- certificates a credentials,
- CNI, CSI, DNS a ďalšie add-ons,
- backup, restore, upgrades a incident response.

### Local learning cluster

Nástroje ako kind alebo minikube sú vhodné na učenie, CI a lokálny development. Ich failure domains, storage, load balancer a lifecycle sa nezhodujú s produkčným multi-node clusterom.

## 2. Deployment tools

Bežné prístupy:

- **kubeadm** — bootstrap a upgrade Kubernetes clusteru na už pripravených hosts,
- **Cluster API** — deklaratívny lifecycle clusters a machines cez Kubernetes-style APIs,
- cloud-specific managed services a provisioning tools,
- kOps, Kubespray alebo vendor distributions,
- immutable node images a autoscaling node pools.

Nástroj vyberaj podľa:

- support a upgrade policy,
- HA a failure-domain modelu,
- air-gapped požiadaviek,
- cloud/on-prem integration,
- ownershipu OS, PKI a etcd,
- automation a rollback capability,
- compliance a support boundary.

## 3. Predinštalačné rozhodnutia

Pred bootstrapom musí byť explicitné:

- Kubernetes minor a patch verzia,
- control-plane endpoint a load-balancer model,
- stacked alebo external etcd,
- počet control-plane a worker nodes,
- zones/racks a quorum failure domains,
- Pod a Service CIDRs,
- IPv4, IPv6 alebo dual-stack,
- CNI a NetworkPolicy implementation,
- container runtime a cgroup driver,
- CSI/storage classes,
- cluster DNS domain,
- identity provider a administrator access,
- certificate authority ownership,
- encryption-at-rest konfigurácia,
- backup a restore cieľ,
- upgrade a decommission proces.

CIDR, cluster domain, PKI a storage topology sa menia podstatne ťažšie než bežný Deployment manifest.

## 4. Host prerequisites

Každý Node potrebuje kompatibilné:

- OS a kernel,
- container runtime s CRI endpointom,
- cgroups a resource controllers,
- networking, routes a firewall,
- time synchronization,
- DNS a hostname resolution,
- disk capacity, filesystem a inodes,
- kernel modules a sysctls podľa CNI/runtime,
- package repositories alebo immutable image pipeline.

Over:

```bash
uname -r
systemctl status containerd
crictl info
ip address
ip route
ss -lntup
free -h
df -h
df -i
timedatectl
```

Swap, cgroup verzia, SELinux/AppArmor a firewall musia byť riešené podľa konkrétnej Kubernetes verzie, kubelet konfigurácie a distribúcie. Nevypínaj security control iba preto, že bootstrap zlyhal.

## 5. Version pinning

Kubernetes packages a images majú byť explicitne pinované na schválenú verziu.

Kontroluj samostatne:

- kubeadm,
- kubelet,
- kubectl,
- control-plane images,
- etcd,
- CoreDNS,
- CNI/CSI a ďalšie add-ons,
- container runtime.

Package repository, image registry a artifact mirror sú supply-chain dependencies. Air-gapped cluster potrebuje vopred synchronizované packages, images, signatures a version metadata.

## 6. PKI a trust roots

Kubernetes používa TLS a client certificates medzi control-plane, etcd, kubelets a administrátormi.

Kubeadm typicky spravuje alebo používa files pod:

```text
/etc/kubernetes/pki
```

Dôležité identity:

- API server serving certificate,
- API server → kubelet client,
- API server → etcd client,
- etcd peer a server certificates,
- front-proxy CA a clients,
- ServiceAccount signing keys,
- kubeconfig client certificates.

CA private keys sú kritický root of trust. Ich strata, exfiltrácia alebo neplánovaná výmena môže spôsobiť cluster-wide incident.

## 7. Control-plane endpoint

HA cluster potrebuje stabilný endpoint pred API server replicas:

```text
kubernetes-api.example.internal:6443
```

Endpoint môže používať:

- external load balancer,
- virtual IP,
- cloud load balancer,
- iný HA frontend.

Musí mať:

- health checking,
- správne API server certificate SANs,
- connection timeout a failover behavior,
- firewall rules,
- DNS lifecycle a monitoring.

Bootstrap node IP nemá byť dlhodobá cluster API identity.

## 8. HA topológie

### Stacked etcd

Každý control-plane Node prevádzkuje aj etcd member.

Výhody:

- menej hosts,
- jednoduchšia infraštruktúra.

Nevýhody:

- control-plane a etcd failure domain sa prekrývajú,
- resource contention na rovnakom Node-e,
- údržba musí rešpektovať etcd quorum.

### External etcd

Etcd members bežia oddelene od API server nodes.

Výhody:

- oddelené failure a resource domains,
- samostatný etcd lifecycle.

Nevýhody:

- viac systémov a PKI,
- vyššia operational complexity,
- samostatné load/network a upgrade požiadavky.

Tri etcd members tolerujú výpadok jedného člena. Počet control-plane replicas a etcd members navrhuj podľa quorum a skutočných failure domains, nie iba podľa počtu VM.

## 9. `kubeadm init`

`kubeadm init` typicky:

1. vykoná preflight checks,
2. vytvorí alebo načíta PKI,
3. vytvorí kubeconfig files,
4. zapíše static Pod manifests control-plane components,
5. spustí local etcd pri stacked topológii,
6. čaká na control-plane health,
7. vytvorí bootstrap/config resources,
8. nastaví RBAC a bootstrap token workflow,
9. pripraví CoreDNS a kube-proxy resources podľa konfigurácie,
10. vypíše join command.

Preferuj versionovaný kubeadm config namiesto dlhého neauditovateľného command line-u.

```bash
sudo kubeadm init --config kubeadm-config.yaml
```

Kubeadm nevytvorí plne funkčný Pod network dataplane bez následnej inštalácie CNI.

## 10. Static Pods

Kubeadm typicky uloží control-plane manifests pod:

```text
/etc/kubernetes/manifests
```

Kubelet sleduje tento directory a spúšťa static Pods pre:

- kube-apiserver,
- kube-controller-manager,
- kube-scheduler,
- local etcd pri stacked topológii.

Zmena manifestu spôsobí restart príslušného componentu. Súbor upravuj iba cez riadený lifecycle; typo môže odstaviť API server alebo etcd.

## 11. CNI bootstrap

Po `kubeadm init` Node často zostáva `NotReady`, kým nie je nainštalovaná kompatibilná CNI implementation.

CNI configuration musí zodpovedať:

- Pod CIDR,
- IP family,
- MTU a overlay/routing modelu,
- NetworkPolicy požiadavkám,
- kube-proxy alebo eBPF Service dataplane-u,
- kernel a host firewall capabilities.

CNI manifest alebo operator je cluster-critical release. Potrebuje version pinning, staged rollout a recovery postup.

## 12. Joining Nodes

Worker join typicky používa:

```bash
sudo kubeadm join <endpoint>:6443 \
  --token <bootstrap-token> \
  --discovery-token-ca-cert-hash sha256:<hash>
```

Control-plane join pridáva ďalšie PKI a etcd kroky.

Bootstrap token:

- má byť časovo obmedzený,
- nesmie byť uložený v dlhodobom logu alebo repository,
- musí overovať CA identity,
- po použití má byť zrušený alebo expirovať.

Po join over:

```bash
kubectl get nodes -o wide
kubectl describe node <node>
kubectl get csr
```

## 13. Add-ons

Minimum usable cluster typicky potrebuje:

- CNI,
- cluster DNS,
- Service dataplane,
- storage/CSI podľa workloadov,
- metrics pipeline,
- ingress/Gateway implementation podľa exposure modelu,
- logging a monitoring,
- policy/admission controls,
- image registry a secret integration.

Add-on compatibility matrix je súčasťou cluster version supportu.

## 14. Bootstrap configuration vs. day-2 configuration

Kubeadm bootstrap configuration nie je univerzálny cluster configuration manager.

Rozlišuj:

- host image a OS config,
- kubeadm ClusterConfiguration,
- kubelet config,
- component flags/config files,
- static Pod manifests,
- Kubernetes API resources,
- external load balancer, DNS a firewall,
- CNI/CSI/operator configuration.

Každá vrstva potrebuje autoritatívny source a change workflow. Ručné zmeny priamo na jednom control-plane Node-e vytvárajú drift.

## 15. Certificate lifecycle

Sleduj expiration všetkých control-plane, etcd a client certificates.

```bash
sudo kubeadm certs check-expiration
```

Renewal môže používať kubeadm alebo external CA workflow podľa architektúry.

Po renewal môže byť potrebné:

- restartovať static Pods/components,
- distribuovať aktualizované kubeconfigs,
- overiť SANs a trust chain,
- zachovať staré/new trust overlap podľa rotation modelu.

ServiceAccount signing-key rotation je samostatný token lifecycle problém.

## 16. Node lifecycle

Bežná údržba:

```bash
kubectl cordon <node>
kubectl drain <node> --ignore-daemonsets
# OS/runtime/kubelet maintenance
kubectl uncordon <node>
```

Drain musí rešpektovať:

- PodDisruptionBudgets,
- local storage,
- DaemonSets,
- static Pods,
- StatefulSet identity,
- volume detach/attach,
- replacement capacity,
- application graceful termination.

Cordon iba zastaví nové scheduling rozhodnutia; nepresunie existujúce Pody.

## 17. Node replacement

Preferuj repeatable replacement pred dlhodobým ručným patchovaním.

Workflow:

1. vytvor nový Node z versionovaného image/configu,
2. joinni ho do clusteru,
3. over Ready, CNI, CSI, labels a taints,
4. presuň workloady cez controlled drain,
5. zmaž starý Node object a cloud/host resource,
6. zruš credentials, disks a DNS podľa lifecycle.

Node object deletion sama nezmaže VM ani attached data.

## 18. Control-plane maintenance

Pred zásahom over:

- počet healthy API servers,
- etcd member health a quorum,
- active leader components,
- load balancer backends,
- snapshot a restore test,
- certificate expiry,
- admission webhooks a critical add-ons.

Control-plane Nodes aktualizuj sekvenčne. Neodstavuj naraz väčšinu etcd členov ani všetky API server endpoints.

## 19. Backup scope

Cluster recovery potrebuje viac než etcd snapshot:

- etcd snapshot,
- encryption configuration a keys,
- CA a required private keys,
- kubeadm/component configuration,
- external DNS/LB/firewall/IAM configuration,
- CNI/CSI/add-on manifests a versions,
- workload source manifests/GitOps repository,
- persistent application data backups,
- image registry artifacts,
- restore runbook a credentials.

Etcd snapshot neobsahuje persistent volume content ani external cloud resources.

## 20. Cluster decommission

Decommission musí byť explicitný:

1. zastav nové deployments a backupni authoritative data,
2. zruš external traffic a DNS,
3. odstráň workloads s retention rozhodnutím,
4. over PV/reclaim policy a cloud disks,
5. zruš node/control-plane identities a certificates,
6. odstráň load balancers, IPs, firewall a DNS,
7. zruš registry a external secret integrations,
8. archivuj audit, backup a compliance evidence,
9. odstráň hosts a disks bezpečným spôsobom.

`kubeadm reset` čistí časť lokálneho bootstrap state-u; nie je kompletný cloud/network/storage deprovisioning nástroj.

## 21. Managed-service ownership matrix

Pre každú platformu zdokumentuj:

| Oblasť | Provider | Platform team | Application team |
|---|---|---|---|
| Control plane availability | | | |
| etcd backup/restore | | | |
| Version upgrade | | | |
| Node image a patching | | | |
| CNI/CSI | | | |
| Workload manifests | | | |
| Application data backup | | | |
| RBAC a identity | | | |
| Incident support | | | |

Nejasný ownership sa pri incidente zmení na oneskorenie recovery.

## 22. Observability

Sleduj:

- API server health, latency a errors,
- etcd quorum, latency, database size a leader changes,
- scheduler a controller-manager health,
- Node Ready/pressure conditions,
- certificate expiration,
- kubelet/runtime/CNI/CSI health,
- add-on versions a rollout,
- backup freshness a restore-test výsledok,
- unsupported version/deprecation exposure.

Cluster `Ready` nie je jeden boolean; je to súbor nezávislých control-plane, node a add-on stavov.

## 23. Troubleshooting

### `kubeadm init` zlyhá v preflight

Neobchádzaj check bez príčiny. Over ports, swap/cgroups, runtime endpoint, hostname, existing manifests, certificates a firewall.

### API server static Pod padá

Over kubelet a runtime logs, manifest syntax, certificates, bind address, etcd connectivity a host ports.

### Node sa joinne, ale zostáva `NotReady`

Over CNI, Pod CIDR, runtime, kubelet config, Node conditions a network plugin logs.

### CoreDNS zostáva `Pending`

Cluster môže nemať schedulovateľný Node, CNI alebo tolerations/resources. DNS problém je downstream symptóm bootstrapu.

### Ďalší control-plane Node sa nepripojí

Over control-plane endpoint, certificate SANs, uploaded/manual certificates, etcd peer connectivity a quorum.

### Certifikát expiroval

Over presne ktorý certificate a component ho používa. Renewal bez reloadu alebo distribúcie nemusí obnoviť funkčnosť.

## 24. Anti-patterny

### Produkčný single-control-plane cluster bez recovery plánu

Jedna VM je control-plane failure domain aj maintenance bottleneck.

### `kubeadm init` command bez versionovaného configu

Cluster intent nie je auditovateľný ani reprodukovateľný.

### CNI nainštalovaná z mutable URL

Bootstrap závisí od nezafixovaného externého obsahu.

### Ručné rozdielne úpravy na control-plane Nodes

Vzniká configuration drift a nepredvídateľný failover.

### Backup iba etcd snapshotu bez PKI/encryption keys

Restore môže byť technicky nemožný alebo dáta nečitateľné.

### Upgrade bez add-on compatibility kontroly

API server môže fungovať, ale CNI, CSI, admission alebo monitoring zlyhá.

### `kubeadm reset` považovaný za bezpečný decommission

External disks, load balancers, DNS, credentials a cloud resources zostanú.

## 25. Kontrolné otázky

1. Aké vrstvy cluster lifecycle kubeadm rieši a ktoré nerieši?
2. Ako sa líši managed a self-managed ownership?
3. Aký je rozdiel medzi stacked a external etcd topológiou?
4. Prečo cluster potrebuje stabilný control-plane endpoint?
5. Čo približne vykoná `kubeadm init`?
6. Prečo Node po bootstrap-e môže zostať `NotReady`?
7. Ktoré artifacts okrem etcd snapshotu potrebuje disaster recovery?
8. Ako vyzerá bezpečný Node replacement workflow?
9. Prečo PKI a ServiceAccount signing keys potrebujú samostatný lifecycle?
10. Čo musí obsahovať cluster decommission runbook?

## Glossary impact

Relevantné pojmy: cluster bootstrap, kubeadm, control-plane endpoint, stacked etcd, external etcd, static Pod manifest, bootstrap token, cluster lifecycle, node replacement, certificate lifecycle, cluster add-on, managed control plane, ownership matrix a cluster decommission.

## Oficiálna dokumentácia

- [Production environment](https://kubernetes.io/docs/setup/production-environment/)
- [Bootstrapping clusters with kubeadm](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/)
- [Creating a cluster with kubeadm](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/create-cluster-kubeadm/)
- [Creating highly available clusters with kubeadm](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/high-availability/)
- [PKI certificates and requirements](https://kubernetes.io/docs/setup/best-practices/certificates/)
