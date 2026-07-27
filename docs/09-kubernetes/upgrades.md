# Upgrades

Kubernetes upgrade nie je výmena jednej binárky. Je to riadený prechod celého clusteru z jednej podporovanej platformovej generácie do druhej. Control plane môže byť `Ready`, kým nový Node pool nemá funkčný Service dataplane, admission webhook nerozumie novému API objektu alebo operator používa odstránený endpoint. Upgrade je dokončený až po overení management plane-u, workload plane-u, dát, telemetry a business outcome-u.

Táto kapitola používa jeden dominantný lifecycle:

```text
support/security intent a target generation
→ current cluster a consumer inventory
→ compatibility graph a deprecated-API closure
→ pre-upgrade health, capacity a recovery gate
→ staged control-plane/etcd/API transition
→ add-on, Node a runtime transition
→ mixed-version a failure-domain containment
→ workload, data a business acceptance
→ roll-forward/rollback/recovery decision
→ retirement starej generácie a upgrade closure
```

## 1. Atlas upgrade subject

Atlas Payments prechádza z Kubernetes `1.35.x` na podporovanú `1.36.x` generáciu. Exact upgrade subject nie je iba cieľová verzia:

```text
cluster identity a stable API endpoint
current a target Kubernetes/control-plane/etcd generation
kubeadm, kubelet, kubectl a container-runtime versions
Node image, kernel, cgroup a package-repository generation
CNI, CSI, CoreDNS, Service dataplane a metrics generation
ingress/Gateway, admission, policy a secret controllers
CRD schemas, served/storage versions a conversion webhooks
workload image/API/schema compatibility
etcd snapshot, PKI/encryption a application backup generation
capacity, PDB, topology a abort criteria
```

Ak tento inventár nie je versionovaný, operator nevie odlíšiť plánovanú mixed-version fázu od náhodného driftu.

## 2. Prečo upgrade funguje ako compatibility graph

Každá vrstva je providerom aj consumerom kontraktov:

```text
API server
→ API discovery, schemas a storage/conversion semantics
→ controllers, operators, admission a clients

Node image/runtime/kubelet
→ CRI, cgroups, kernel a host-network/storage capabilities
→ CNI, CSI, Pods a probes

add-ons
→ DNS, Service, policy, storage, metrics a routing capabilities
→ workloads a platform automation
```

Komponent môže podporovať cieľový Kubernetes minor, ale nie nový kernel, cgroup mode, API storage version alebo susedný add-on. Preto nestačí samostatný zoznam „supported versions“. Potrebný je resolved compatibility graph pre presnú cieľovú generáciu.

## 3. Patch, minor a support lifecycle

Patch upgrade zostáva v rovnakom minor rade a typicky prináša bug a security opravy. Minor upgrade môže meniť API, defaults, feature gates, component config, metrics, runtime requirements a podporované version skew.

Pre kubeadm cluster platí:

- používaj dokumentáciu konkrétnej cieľovej minor verzie;
- nepreskakuj minor verzie;
- aktualizuj na vhodný aktuálny patch pred ďalším minor krokom;
- over upstream aj vendor/provider support window;
- ukonči upgrade skôr, než sa current generation stane nepodporovanou.

Support deadline je vstup do plánovania, nie dôvod preskočiť rehearsal alebo health gate.

## 4. Version skew ako dočasný transition contract

HA upgrade úmyselne vytvára mixed-version stav. Version skew policy definuje, ktoré combinations sú podporované, ale nepreukazuje application compatibility.

Praktické invarianty:

1. API server generácia vedie transition.
2. Kubelet nesmie byť novší než podporuje API server.
3. Control-plane replicas sa menia sekvenčne.
4. Worker Nodes sa menia až po prijatí control-plane transitionu.
5. Mixed-version interval má byť krátky, pozorovaný a ukončený.
6. Klient, operator alebo webhook môže mať prísnejšiu compatibility hranicu než upstream skew policy.

## 5. Current-state a consumer inventory

Pred zmenou zachyť:

```text
cluster/component/Node/add-on versions a digests
API server feature gates a component configs
etcd member topology, version, revision a health
Node pools, OS/kernel/runtime/cgroup generations
APIService, webhook, CRD a operator inventory
served/storage API versions a stored object generations
all deprecated API callers z audit evidence
PDB, topology, quota a spare-capacity envelope
certificate, backup a restore-rehearsal verdict
critical application releases, schemas a data generations
```

Manifest scanning nestačí. Removed alebo deprecated endpoint môže používať Helm hook, CI, operator, kubectl plugin, external automation alebo staršia client library. API audit a server warnings odhaľujú reálnych callers.

## 6. Deprecated API a CRD closure

API migration má tri samostatné boundaries:

```text
caller používa served endpoint
→ object je konvertovaný na storage version
→ controller a webhook rozumejú effective objectu
```

Pred odstránením starej verzie over:

- všetci callers používajú podporovaný endpoint;
- CRD má validnú target schema;
- conversion webhook je dostupný, HA a compatible;
- existujúce objects sú migrované na správnu storage version;
- controller rozumie starej aj novej generation počas transitionu;
- rollback alebo roll-forward hranica je explicitná.

Green static scan nepreukazuje, že external controller prestal volať staré API.

## 7. Pre-upgrade health a recovery gate

Neupgraduj už degraded cluster. Gate musí zahŕňať:

```text
API read/write/watch a semantic readiness
etcd quorum, latency, disk a alarms
scheduler/controller leadership a queue health
Node, CNI, CSI, DNS, Service a admission capabilities
certificate a credential expiry
spare capacity pre drain, surge a failover
current backup artifact a complete recovery set
úspešný recent restore rehearsal
critical workload a business SLO baseline
```

Etcd snapshot bez PKI, encryption history, external-state inventory a application backupu nie je úplný recovery point. Rollback stop point musí byť definovaný pred prvou irreversible storage/API zmenou.

## 8. Staging, canary a acceptance matrix

Rehearsal musí používať reprezentatívny compatibility graph, nie iba prázdny cluster. Testuj:

- API create/update/delete/watch;
- admission, aggregation a CRD conversion;
- Pod sandbox, DNS, Service a NetworkPolicy;
- PVC provision/attach/mount/snapshot;
- Deployment, StatefulSet, Job a HPA;
- Gateway/Ingress a certificate path;
- logs, metrics, Events a audit;
- Node drain, replacement a failure-domain loss;
- critical payment journey a duplicate-prevention behavior.

Canary Node pool má mať rovnaký target image, runtime, CNI/CSI a policy stack ako final fleet. Pod `Ready` na canary Node-e nie je dostatočný verdict.

## 9. Control-plane transition

Kubeadm-specific flow sa riadi dokumentáciou cieľovej verzie. Mechanicky však sleduje:

```text
upgrade kubeadm/planner na prvom control-plane Node-e
→ validate target a preflight
→ mutate local control-plane/etcd/static-Pod generation
→ wait for semantic endpoint acceptance
→ repeat one control-plane Node at a time
→ close mixed-version control-plane state
```

Po každom backende over:

- serving certificate a stable endpoint identity;
- `/readyz` vrátane etcd;
- read/write/watch cez konkrétny backend;
- etcd quorum a leader stability;
- scheduler/controller leadership;
- admission a API aggregation;
- load-balancer remove/add behavior.

Drained control-plane Node môže stále prevádzkovať static Pods. Drain preto nie je control-plane shutdown mechanizmus.

## 10. Add-on a Node transition

Add-on ordering vychádza z vendor compatibility matrix. Osobitne sleduj:

- CNI a Service dataplane;
- CSI controller/node sidecars a snapshot APIs;
- CoreDNS a NodeLocal DNS;
- metrics-server a adapters;
- ingress/Gateway, cert-manager a secret operators;
- admission, policy, service mesh a observability agents.

Worker transition preferuje immutable replacement:

```text
create target Node pool
→ join a identity validation
→ system DaemonSet a capability canaries
→ canary workload a business tests
→ controlled drain starej cohorty
→ remove old Node/infra/credentials
```

In-place upgrade musí stále zachovať exact pre/post Node generation, drain evidence a rollback boundary.

## 11. Capacity, PDB a stateful hranice

Upgrade potrebuje capacity pre:

- unavailable Node;
- Deployment surge;
- HPA burst;
- hard anti-affinity a topology spread;
- PDB;
- volume topology a attach limits;
- stateful quorum a fencing;
- system DaemonSets a temporary overlap.

PDB, ktorý blokuje drain, môže správne chrániť availability. `--force` alebo obídenie eviction API nie je oprava nedostatočnej capacity či zlého application disruption contractu.

## 12. Observability počas transitionu

Telemetry musí byť viazaná na upgrade cohort:

```text
cluster a upgrade operation ID
component/Node/add-on generation
old/new cohort a failure domain
API/etcd/controller/scheduler signals
Pod Pending/restart/eviction a probe verdicts
CNI/CSI/DNS/Service paths
application SLO a business transaction
```

Vopred definuj abort criteria, napríklad:

- API alebo etcd SLO burn;
- strata quorum margin;
- canary Node capability failure;
- rast admission/conversion errors;
- storage attach/mount failure;
- payment error alebo duplicate rate nad limit;
- telemetry pipeline strata, ktorá znemožní bezpečný verdict.

## 13. Causal walkthrough: control plane je green, ale traffic z nových Nodes zlyháva

### Symptom

Control plane a prvý nový Node pool boli aktualizované. API, Nodes aj system Pods vyzerajú green. Payments Pods na starých Nodes fungujú; Pods na target Node generation majú intermittent Service timeouty a cross-Node traffic failure.

### Exact subject

Fixuj:

- upgrade operation a target generation;
- old/new Node UID, image, kernel, runtime a cgroup generation;
- CNI/Service-dataplane DaemonSet revisions a loaded configs;
- Pod UID, sandbox, IPAM lease a endpoint cohort;
- source/destination Nodes a pre/post-NAT flow;
- route/tunnel/MTU/policy/conntrack state;
- canary acceptance výsledky a čas rollout-u.

### Competing hypotheses

1. Service selector alebo EndpointSlice cohort je chybný;
2. nový Node má inú CNI configuration;
3. CNI agent beží, ale host initialization zlyhala;
4. kernel alebo module generation je nekompatibilná;
5. MTU sa zmenilo medzi old/new pools;
6. NetworkPolicy program je stale;
7. kube-proxy/eBPF dataplane nemá current Service generation;
8. host firewall alebo forwarding policy sa zmenila;
9. image/runtime upgrade zmenil Pod sandbox behavior;
10. DNS alebo application connection pool maskuje skutočný packet failure.

### Discriminating observations

Porovnaj rovnaký fresh flow zo starej a novej cohorty. Sleduj Pod socket, netns, route/tunnel, policy verdict, Service translation, packet capture a reverse path. Porovnaj DaemonSet image/config, host init logs, kernel modules, MTU a dataplane maps/rules.

Finding:

```text
nový Node image neobsahuje host networking prerequisite
→ CNI agent process a shallow readiness sú green
→ host dataplane initialization je partial
→ same-Node/direct traffic môže fungovať
→ cross-Node a Service-translated flows zlyhávajú
→ control plane upgrade vyzerá úspešne, workload plane nie
```

### Containment

- zastav rollout nového poolu;
- cordon target cohort a drainni iba ak stateful/storage contract dovolí;
- zachovaj Node/CNI logs, rules/maps a packet evidence;
- neobchádzaj problém host networkingom, vypnutím policy alebo plošným firewall allow;
- chráň downstream pred retry amplification.

### Authoritative recovery

- oprav versionovaný Node image alebo CNI host prerequisite;
- vytvor novú Node generation namiesto ručného drift patchu;
- spusti CNI/Service capability canary;
- presuň bounded canary workload;
- over exact allowed aj forbidden flows;
- pokračuj rolloutom po failure domains;
- retire-ni chybnú a starú cohortu až po acceptance.

### Verify original a forbidden outcomes

Over:

1. API, etcd a control-plane capabilities zostali zdravé;
2. Pod sandbox/IPAM vzniká na každom target Node-e;
3. same-Node aj cross-Node Pod traffic fungujú;
4. ClusterIP, DNS, policy a Gateway paths fungujú;
5. forbidden NetworkPolicy flows zostávajú blokované;
6. storage a probes na target cohort-e fungujú;
7. payment journey uspeje bez duplicate retry side effects;
8. old Node a add-on generations už neobsluhujú workloady;
9. replacement ďalšieho Node-u reprodukuje rovnaký verdict.

### Earlier controls

Použi immutable Node image conformance, add-on compatibility lock, per-cohort capability canary, semantic DaemonSet health, packet-path test v rehearsal clustri, staged Node pool rollout a explicitný workload-plane abort gate.

## 14. Roll-forward, rollback a recovery

Roll-forward je vhodný, keď cluster zostáva operovateľný a oprava môže vytvoriť novú compatible generation. Rollback je prípustný iba po overení, že:

- old component je compatible s current API/storage state-om;
- old Node pool stále existuje a je bezpečný;
- CRD/storage migration neprekročila rollback boundary;
- workload/schema/external state sa dá vrátiť;
- version skew zostane podporovaný.

Etcd restore patrí až k strate authoritative API state-u alebo testovanému disaster-recovery scenáru. Nie je remediation bežnej CNI alebo chart chyby.

## 15. Upgrade closure

Upgrade je uzavretý až keď:

```text
všetky control-plane a Node subjects sú v target generation
mixed-version interval skončil
all add-ons/controllers/webhooks sú compatible a current
removed API callers sú nulové
storage/CRD migrations sú dokončené
telemetry a alerts fungujú na target metrics/log schemas
critical workloads a business SLO sú prijaté
old artifacts, pools a credentials sú bezpečne retired
actual duration, aborts, gaps a follow-up controls sú zaznamenané
```

## 16. Ďalšie failure boundaries

### `kubeadm upgrade plan` odmieta target

Over current/target minor, kubeadm version, repository, control-plane health a skew. Neobchádzaj preflight bez cause modelu.

### API funguje, CRD operations zlyhávajú

Over served/storage versions, conversion webhook cohort, certificates, schema a controller compatibility.

### Drain je blokovaný

PDB, topology, local data alebo stateful quorum môže správne zastaviť disruption. Oprav capacity alebo workload contract.

### Node je `Ready`, ale workloads zlyhávajú

Node heartbeat nepreukazuje CNI, CSI, DNS, Service, policy ani application capability. Použi acceptance matrix.

### Dashboards po upgrade zmizli alebo sú green bez dát

Metric names/labels alebo scrape authorization sa zmenili. Over raw targets, query results a SLO coverage; telemetry loss je upgrade failure boundary.

### Automatic managed-service upgrade rozbije application

Provider vlastní iba časť lifecycle-u. Application tím stále vlastní APIs, add-ons, PDB, Node pools, controllers, data a business acceptance.

## 17. Referenčný katalóg

### Upgrade evidence

```text
current a target generation manifest
compatibility/deprecation findings
health a recovery gate
per-step operation log a approver
per-cohort technical/business verdict
abort/recovery decisions
old-generation retirement proof
```

### High-cost boundaries

- etcd/API storage migration;
- CRD storage/conversion;
- PKI a ServiceAccount signing changes;
- CNI/CSI data-plane generation;
- Node OS/kernel/runtime generation;
- application schema a persistent data;
- external cloud/provider resources.

## 18. Anti-patterny

- preskočenie minor verzie;
- upgrade degraded clusteru;
- kontrola iba API `/readyz`;
- inventory iba z Git manifestov;
- mutable add-on alebo Node artifacts;
- všetky control-plane alebo Nodes naraz;
- force drain bez disruption/fencing analýzy;
- old/new telemetry bez cohort labelu;
- rollback zamieňaný za package downgrade;
- etcd restore ako prvá remediation;
- old generation ponechaná neurčito po „úspešnom“ upgrade-e.

## 19. Kontrolné otázky

1. Čo tvorí exact Kubernetes upgrade subject?
2. Prečo version skew nie je application compatibility verdict?
3. Ako odhalíš deprecated API caller mimo Git repository?
4. Ktoré podmienky tvoria pre-upgrade health a recovery gate?
5. Prečo `Node Ready` nestačí na Node-pool acceptance?
6. Ako PDB, topology a storage menia upgrade capacity?
7. Ktoré observation points odlíšia CNI failure od Service selector chyby?
8. Kedy je roll-forward bezpečnejší než rollback?
9. Prečo etcd restore nie je bežný upgrade rollback?
10. Ktoré dôkazy uzatvárajú retirement starej generácie?

## Glossary impact

Relevantné pojmy: Kubernetes upgrade subject, target platform generation, compatibility graph, deprecated API caller inventory, deprecated-API closure, mixed-version transition, upgrade recovery gate, canary capability verdict, Node-generation acceptance, workload-plane abort criterion, upgrade cohort, irreversible migration boundary, old-generation retirement a subject-bound upgrade closure.

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