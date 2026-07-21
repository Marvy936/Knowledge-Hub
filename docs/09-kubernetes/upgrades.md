# Upgrades

Kubernetes upgrade je koordinovaná zmena control plane, etcd, Nodes, container runtime, APIs, add-ons a workloads. Nie je to iba výmena binárky `kubelet` alebo image tagu. Bez compatibility analýzy môže byť API server healthy, ale CNI, CSI, admission webhooks, controllers alebo aplikácie prestanú fungovať.

## 1. Upgrade scope

Rozlišuj:

- Kubernetes control-plane version,
- etcd version,
- kubeadm a kubelet,
- kubectl clients,
- container runtime,
- CNI a Service dataplane,
- CSI drivers,
- CoreDNS a metrics pipeline,
- ingress/Gateway controllers,
- admission webhooks a operators,
- CRDs a custom resources,
- node OS/kernel,
- workload images a APIs.

Každá vrstva má vlastnú support matrix.

## 2. Patch a minor upgrade

### Patch upgrade

Typicky zachováva rovnakú minor verziu a prináša bug/security fixes.

### Minor upgrade

Mení napríklad `1.35 → 1.36` a môže priniesť:

- API removals,
- feature-gate zmeny,
- component flag/config changes,
- metrics/logging zmeny,
- cgroup/runtime requirements,
- add-on compatibility zmeny.

Pri kubeadm je preskakovanie minor verzií nepodporované. Upgrade vykonávaj po jednej minor verzii a podľa version-specific dokumentácie.

## 3. Version skew

Kubernetes definuje podporovaný skew medzi API serverom, kubeletmi, controller-managerom, schedulerom, kube-proxy a kubectl. Deployment tool môže mať prísnejšie pravidlá.

Princípy:

- API servers v HA clustri musia zostať v podporovanom vzájomnom skew,
- kubelet nemá byť novší než API server,
- control plane sa aktualizuje pred worker Nodes,
- kubeadm version musí zodpovedať cieľovému upgrade kroku,
- klientský skew nie je nekonečná backward compatibility.

Pred každým upgrade over aktuálnu Version Skew Policy, nie historickú poznámku v runbooku.

## 4. Support window

Platforma musí poznať:

- release cadence,
- podporované minor verzie,
- end-of-life dátumy,
- provider support window,
- add-on a OS support,
- security patch SLA.

Upgrade plán nemá začať až po skončení podpory aktuálnej verzie.

## 5. Pre-upgrade inventory

Zaznamenaj:

```bash
kubectl version
kubectl get nodes -o wide
kubectl get --raw /version
kubectl get pods -A
kubectl get apiservices
kubectl get validatingwebhookconfigurations,mutatingwebhookconfigurations
kubectl get crd
```

Ďalej inventarizuj:

- control-plane a etcd topology,
- Node pools a OS images,
- CNI/CSI/CoreDNS versions,
- ingress/Gateway a operators,
- deprecated API usage,
- feature gates a component config,
- admission dependencies,
- critical PDBs a capacity,
- backup a rollback možnosti.

## 6. Release notes a deprecations

Prečítaj:

- release notes aktuálnej aj cieľovej verzie,
- Version Skew Policy,
- Deprecated API Migration Guide,
- kubeadm upgrade guide,
- provider/vendor advisories,
- CNI/CSI/operator compatibility matrix.

Hľadaj najmä:

- removed APIs,
- removed flags a feature gates,
- default behavior changes,
- storage/API conversion requirements,
- metrics removals alebo renames,
- security hardening zmeny,
- known issues.

## 7. Deprecated API detection

Manifest v Git-e nemusí byť jediný caller. Deprecated API môže používať:

- Helm chart,
- operator/controller,
- CI pipeline,
- kubectl plugin,
- external automation,
- starý CRD conversion webhook,
- klientská knižnica.

Použi:

- API server audit logs,
- deprecation warning metrics/logs,
- static manifest scanning,
- server-side dry-run proti cieľovej API verzii,
- staging cluster na cieľovej verzii.

Objekt uložený v etcd môže byť čitateľný cez novšiu served API, ale klient používajúci odstránený endpoint zlyhá.

## 8. Pre-upgrade health gate

Neupgraduj cluster, ktorý už je degraded.

Over:

- etcd quorum a latency,
- API `/readyz`,
- scheduler/controller-manager leadership,
- všetky Nodes Ready,
- CNI/CSI/CoreDNS health,
- Pending/CrashLooping system Pods,
- certificate expiry,
- disk/inode capacity,
- working backup a restore rehearsal,
- spare workload capacity.

Upgrade zhoršuje diagnostiku existujúceho incidentu.

## 9. Backup a rollback boundary

Pred control-plane upgrade:

- vytvor a over etcd snapshot,
- zachovaj PKI/encryption config,
- exportuj/versionuj component configuration,
- zaznamenaj current images/packages,
- over workload/application backups,
- definuj rollback stop point.

Rollback po API/storage migration nemusí byť jednoduché package downgrade. Musí zostať v podporovanom skew a API compatibility okne.

## 10. Staging a canary

Najprv over upgrade na:

- disposable test clustri,
- staging clustri s reprezentatívnymi add-ons,
- canary node pool,
- malej skupine workloadov podľa failure domainu.

Testuj:

- create/update/delete APIs,
- CNI a Service traffic,
- CSI provision/attach/mount,
- DNS,
- ingress/Gateway,
- admission webhooks,
- autoscaling,
- logging/metrics,
- operators a CRDs,
- node drain/replacement.

## 11. Kubeadm control-plane upgrade

Version-specific flow typicky zahŕňa:

1. upgrade package `kubeadm` na prvom control-plane Node-e,
2. `kubeadm upgrade plan`,
3. `kubeadm upgrade apply <target-version>`,
4. upgrade kubelet/kubectl package podľa plánu,
5. restart kubelet a health validation,
6. na ďalších control-plane Nodes `kubeadm upgrade node`,
7. sekvenčnú validáciu každého endpointu.

Príkazy a repository paths sa menia podľa minor verzie a OS. Používaj konkrétnu dokumentáciu cieľovej verzie.

## 12. Control-plane sequencing

V HA clustri:

- aktualizuj jeden control-plane Node naraz,
- zachovaj API server availability,
- neohroz etcd quorum,
- sleduj load-balancer health,
- over leader election,
- po každom kroku vykonaj health gate.

Po upgrade prvého API servera cluster dočasne beží v podporovanom mixed-version stave. Minimalizuj jeho trvanie.

## 13. Worker Node upgrade

Typický flow:

```bash
kubectl cordon <node>
kubectl drain <node> --ignore-daemonsets
# upgrade OS/runtime/kubeadm/kubelet
sudo kubeadm upgrade node
sudo systemctl restart kubelet
kubectl uncordon <node>
```

Presný sled závisí od distribúcie a node-image modelu.

Pred drain over:

- PDB,
- replacement capacity,
- local data,
- volume attach topology,
- StatefulSet/quorum,
- DaemonSets a static Pods,
- graceful termination.

## 14. Immutable Node replacement

Pri managed node groups alebo immutable infraštruktúre je často bezpečnejšie:

1. vytvoriť nový pool s cieľovou verziou,
2. overiť CNI/CSI/system DaemonSets,
3. presunúť canary workloady,
4. postupne drainnuť starý pool,
5. odstrániť staré Nodes a infraštruktúru.

Výhody:

- jednoduchší rollback cez starý pool,
- menší host drift,
- test nového OS/runtime obrazu,
- jasnejší audit.

## 15. Add-on upgrade ordering

Poradie závisí od compatibility matrix. Typicky analyzuj:

- CNI pred alebo po control-plane upgrade podľa vendor pokynov,
- CSI sidecars a snapshot CRDs,
- CoreDNS a kube-proxy,
- metrics-server,
- ingress/Gateway controllers,
- cert-manager a secret operators,
- policy/admission systems,
- service mesh a observability agents.

Nespoliehaj sa na to, že chart install úspešne prešiel. Validuj dataplane.

## 16. CRDs a conversion

CRD upgrade môže meniť:

- served versions,
- storage version,
- schema a defaulting,
- conversion webhook,
- controller expectations.

Pred odstránením starej version:

- over všetkých clients,
- migruj stored objects,
- over conversion webhook availability,
- testuj rollback hranicu,
- zachovaj compatible controller.

Nedostupný conversion webhook môže blokovať list/get/update custom resources a tým aj namespace deletion alebo cluster upgrade.

## 17. Admission webhooks

Upgrade môže naraziť na webhook, ktorý:

- nepodporuje nový API object,
- má expirovaný certificate,
- nie je Ready počas Node drainu,
- používa starú client library,
- fail-closed blokuje system components.

Pred upgrade over:

- replicas a topology spread,
- Service/EndpointSlices,
- CA bundle a cert expiry,
- timeout a failurePolicy,
- compatibility s cieľovou verziou,
- emergency bypass runbook.

## 18. PDB a upgrade capacity

PDB môže správne blokovať drain, ak by narušil availability. To nie je chyba drain-u.

Over:

- počet ready replicas,
- `maxUnavailable` alebo `minAvailable`,
- rollout surge capacity,
- zone failure domains,
- HPA minimum,
- anti-affinity/topology constraints.

Násilné obídenie PDB môže zmeniť plánovanú údržbu na outage.

## 19. Storage počas upgrade

Testuj:

- PVC bind/provision,
- volume attach/detach,
- CSI node registration,
- mount/unmount,
- topology a zone behavior,
- snapshot/restore,
- filesystem compatibility.

Node upgrade môže meniť kernel, multipath, filesystem tools alebo device plugins aj bez zmeny Kubernetes API.

## 20. Metrics a alert compatibility

Kubernetes component metrics a labels sa môžu deprecovať alebo meniť podľa stability policy.

Pred upgrade:

- porovnaj metrics changes,
- over scraping a RBAC,
- testuj dashboards a recording rules,
- aktualizuj alerts pred odstránením starej metric,
- zachovaj dual-query transition, ak je potrebný.

Neplatný dashboard nie je iba kozmetika; môže skryť degraded control plane.

## 21. Upgrade validation

Po každej fáze over:

```bash
kubectl get --raw='/readyz?verbose'
kubectl get nodes
kubectl get pods -A
kubectl get events -A --sort-by=.metadata.creationTimestamp
kubectl get apiservices
```

Funkčné testy:

- create/delete Pod,
- Service a DNS,
- NetworkPolicy,
- PVC provision a mount,
- Deployment rollout,
- Job completion,
- HPA metric a scale,
- ingress/Gateway request,
- Secret/ConfigMap projection,
- audit/log/metric pipeline.

## 22. Rollback vs. roll-forward

### Roll-forward

Preferovaný, ak:

- problém má známu opravu,
- cluster zostáva dostupný,
- API/storage state už používa novú verziu,
- downgrade by porušil skew alebo compatibility.

### Rollback

Možný iba v testovanej a podporovanej hranici. Môže zahŕňať:

- starý Node pool,
- staršiu add-on verziu,
- workload rollback,
- v krajnom prípade etcd disaster recovery.

Etcd restore kvôli bežnej add-on chybe je neprimerane deštruktívny krok.

## 23. Managed Kubernetes upgrade

Provider môže riadiť control plane, ale používateľ musí riešiť:

- maintenance window,
- Node pool compatibility,
- deprecated APIs,
- add-ons a controllers,
- admission a workload readiness,
- PDB/capacity,
- provider-specific feature changes,
- application smoke tests.

„Automatic upgrade“ neznamená automatickú application compatibility.

## 24. Observability počas upgrade

Sleduj:

- API latency/error rate,
- etcd leader/latency,
- scheduler/controller queue,
- Node Ready a kubelet errors,
- Pod Pending/eviction/restart rate,
- CNI/CSI/DNS errors,
- webhook latency/rejection,
- Service traffic success,
- workload SLO a business metrics.

Vopred definuj abort criteria.

## 25. Troubleshooting

### `kubeadm upgrade plan` odmieta verziu

Over kubeadm version, package repository, current cluster version a podporovanú minor cestu.

### Drain je blokovaný

Over PDB, unmanaged Pod, local storage, DaemonSet a replacement capacity. Nezačni automaticky `--force`/`--disable-eviction`.

### Node po upgrade zostáva `NotReady`

Over kubelet, runtime, CNI, cgroup driver, certificates, Node conditions a version skew.

### API funguje, ale CRD requests zlyhávajú

Over conversion webhook, served/storage versions, controller compatibility a APIService/webhook certificates.

### Workloady sa neškálujú

Over metrics pipeline, HPA conditions, quota, Pending Pods a Node capacity.

### Service networking zlyhá iba na nových Nodes

Over CNI/Service dataplane DaemonSets, kernel modules, MTU, routes, firewall a kube-proxy/eBPF state.

## 26. Anti-patterny

### Upgrade priamo z unsupported verzie s preskočením minors

Nie je testovaná compatibility cesta.

### Upgrade bez etcd snapshotu a restore testu

Control-plane rollback nemá dôveryhodný recovery bod.

### Ignorovanie deprecated API callers mimo Git-u

Operator alebo CI prestane fungovať až po odstránení endpointu.

### Všetky Nodes naraz

Stratí sa kapacita, quorum alebo celé failure domainy.

### Force drain bez application analýzy

Obíde PDB a môže poškodiť stateful workload.

### Control plane updated, add-ons „neskôr“ bez kompatibility

Cluster je formálne novší, ale dataplane je nefunkčný.

### Upgrade považovaný za rollback mechanizmus

Restore staršej package verzie nevráti API/storage/external state.

## 27. Kontrolné otázky

1. Ktoré vrstvy okrem Kubernetes control plane patria do upgrade scope-u?
2. Prečo sa pri kubeadm nepreskakujú minor verzie?
3. Čo znamená version skew?
4. Ako odhalíš deprecated API callers mimo manifestov?
5. Prečo sa neupgraduje degraded cluster?
6. Aké sú výhody immutable Node replacementu?
7. Ako PDB ovplyvňuje drain?
8. Prečo CRD conversion webhook môže zablokovať upgrade?
9. Čo patrí do post-upgrade validation?
10. Kedy je roll-forward bezpečnejší než downgrade?

## Glossary impact

Relevantné pojmy: Kubernetes version skew, patch upgrade, minor upgrade, deprecated API caller, upgrade health gate, canary node pool, immutable node replacement, mixed-version control plane, add-on compatibility, storage version migration, upgrade abort criterion a unsupported cluster version.

## Oficiálna dokumentácia

- [Upgrade a cluster](https://kubernetes.io/docs/tasks/administer-cluster/cluster-upgrade/)
- [Upgrading kubeadm clusters](https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-upgrade/)
- [Version Skew Policy](https://kubernetes.io/releases/version-skew-policy/)
- [Deprecated API Migration Guide](https://kubernetes.io/docs/reference/using-api/deprecation-guide/)
- [Kubernetes Deprecation Policy](https://kubernetes.io/docs/reference/using-api/deprecation-policy/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: etcd backup a restore](etcd-backup-restore.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Logging, metrics a events →](logging-metrics-events.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
