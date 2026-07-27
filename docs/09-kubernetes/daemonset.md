# DaemonSet

DaemonSet je Kubernetes workload controller pre node-local capability. Jeho desired state nie je „N zameniteľných replík“, ale „na každom eligible Node-e má existovať správna Pod generation poskytujúca konkrétnu node capability“.

Typické capabilities sú CNI alebo Service dataplane agent, CSI node plugin, log collector, monitoring alebo security agent, device plugin a ďalšia funkcia, ktorej correctness závisí od konkrétneho Node-u.

Dominantný lifecycle:

```text
fleet capability intent a Node inventory
→ DaemonSet UID, generation a eligibility policy
→ per-Node placement subject
→ Pod create a Node binding
→ host/runtime/network/storage prerequisites
→ node-local process a capability readiness
→ fleet-wide rollout a blast-radius control
→ Node join, drain, reboot alebo retirement
→ per-Node a business verification
→ rollback, cleanup a acceptance verdict
```

Kľúčová otázka nie je iba „koľko DaemonSet Podov je Ready?“, ale:

```text
Ktoré Nodes sú podľa aktuálnej policy eligible?
Aká Pod revision a host capability generation na každom z nich reálne beží?
Je Node schopný poskytovať pôvodnú platformovú alebo workload funkciu?
```

## 1. Atlas scenár

Atlas používa DaemonSet `atlas-net-agent` ako node-local network a policy agent na production worker Nodes.

```text
DaemonSet: platform-system/atlas-net-agent
DaemonSet generation: 27
release: 2.8.0
image digest: NET280
eligible fleet: linux production workers
excluded: control-plane, build a isolated-payment-hsm Nodes
expected: presne jeden accepted agent Pod na každý eligible Node
host resources: eBPF, network namespace a bounded host mounts
node capability: Pod networking, policy a flow telemetry
```

Acceptance contract:

- eligible Node inventory je explicitný a versionovaný;
- každý eligible Node má presne jeden accepted Pod UID na current revision;
- žiadny ineligible Node nemá misscheduled agent;
- host permissions sú minimálne a očakávané;
- node-local dataplane capability prejde canary testom;
- rollout neodstaví naraz príliš veľkú časť fleet-u;
- nový Node neprijme application traffic pred capability acceptance;
- staré host artifacts, sockets, programs a credentials sú odstránené.

## 2. DaemonSet subject

Pre rollout alebo incident zaznamenaj:

```text
cluster a namespace
DaemonSet name, UID, generation a resourceVersion
current/update ControllerRevision
template image, config, ServiceAccount a security context
nodeSelector, affinity, tolerations a schedulerName
updateStrategy, maxUnavailable/maxSurge podľa API
eligible Node UIDs, labels, taints, OS, architecture a pool generation
per-Node Pod UID, revision, imageID, status a host resource bindings
node capability version a local readiness result
misscheduled a unavailable inventory
business flows ovplyvnené každým Node-om
```

Desired count je odvodený výsledok eligibility policy nad aktuálnym Node inventory. Nie je to samostatná statická pravda.

## 3. Eligibility lifecycle

Pre každý Node controller vyhodnocuje:

```text
Node existuje a je v target fleet-e?
→ labels a required affinity matchujú?
→ taints sú tolerované zámerne?
→ OS/architecture a runtime sú podporované?
→ host devices, ports a paths existujú?
→ Pod môže byť admitted a scheduled?
→ node-local capability môže bezpečne fungovať?
```

Rozlišuj:

- **eligible Node** — podľa desired placement policy má mať Pod;
- **scheduled Node** — Pod bol vytvorený a boundnutý;
- **ready agent** — container a probes sú green;
- **capability-ready Node** — pôvodná node funkcia reálne funguje;
- **accepted fleet member** — Node môže prijímať workload podľa platformového contractu.

DaemonSet status typicky pokrýva prvé tri vrstvy. Capability a workload acceptance potrebujú samostatný test.

## 4. Node identity a per-Node Pod

DaemonSet Pod patrí konkrétnemu Node-u. Subject chain:

```text
DaemonSet UID/generation
→ eligible Node UID a pool generation
→ DaemonSet Pod UID
→ admitted Pod spec
→ kubelet/runtime generation
→ host mounts, devices, ports a sockets
→ node-local capability generation
→ Node acceptance verdict
```

Node name bez UID alebo provider identity nemusí bezpečne odlíšiť znovu vytvorený stroj. Pri autoscalingu alebo reprovisioningu môže rovnaké human meno skrývať inú kernel, image, runtime alebo device generation.

## 5. Scheduling a bootstrap

DaemonSet controller vytvorí Pod s placementom zacieleným na konkrétny Node. Scheduler a kubelet následne realizujú Pod podľa výsledného specu.

Core node agent môže vytvoriť bootstrap loop:

```text
Node má byť Ready až po network/storage agentovi
→ agent Pod potrebuje runtime, image pull a časť node connectivity
→ application scheduling môže začať skôr než capability acceptance
```

Bootstrap contract musí určiť:

- ktoré taints držia nový Node mimo bežného workload scheduling-u;
- ktoré critical agents ich tolerujú;
- aké minimum network/storage/identity potrebuje agent na štart;
- kto odstráni bootstrap taint;
- aký canary dôkaz potvrdzuje capability;
- čo sa stane pri partial bootstrap-e.

`Node Ready=True` nemusí preukazovať, že konkrétny DaemonSet capability je funkčná, ak readiness pipeline tieto signály neintegruje.

## 6. Tolerations ako blast-radius policy

DaemonSety často potrebujú tolerovať niektoré Node conditions alebo dedicated taints. Broad toleration:

```yaml
tolerations:
  - operator: Exists
```

môže rozšíriť agent na:

- control-plane Nodes;
- security-isolated Nodes;
- workloady s odlišným kernelom alebo device contractom;
- Nodes, kde host mount alebo socket prístup predstavuje väčší blast radius.

Toleration nie je iba scheduling convenience. Je to súčasť fleet authorization policy.

## 7. Host authority

Node agents môžu požadovať:

- `hostNetwork`, `hostPID` alebo host IPC;
- host paths;
- runtime, CNI alebo CSI sockets;
- devices a eBPF permissions;
- privileged mode alebo capabilities;
- host ports;
- cloud/node identity.

Taký Pod je bezpečnostne bližšie host service než bežnému application containeru. Effective authority posudzuj podľa celej kombinácie:

```text
process UID a capabilities
+ namespaces
+ host mounts a sockets
+ devices
+ seccomp/LSM
+ ServiceAccount/RBAC
+ network egress
+ node/cloud credentials
```

Read-only runtime socket alebo host filesystem môže stále poskytovať citlivé metadata alebo control authority podľa konkrétneho API a mountu.

## 8. Node-local capability readiness

Kubelet readiness probe môže overovať local process. Fleet acceptance však môže vyžadovať:

- CNI: sandbox create/delete, IPAM a Pod-to-Pod flow;
- Service dataplane: ClusterIP a reverse path;
- CSI node plugin: stage/publish/unpublish test;
- log agent: end-to-end event v central sinku;
- security agent: policy load a enforcement test;
- device plugin: advertised resource a test allocation;
- monitoring agent: expected Node identity a fresh sample.

Plytká `/healthz` odpoveď môže byť green, zatiaľ čo host program, socket, route, mount alebo downstream registration patrí starej generation.

## 9. Update revision a rollout

Relevantná template zmena vytvorí novú DaemonSet revision.

### RollingUpdate

Controller postupne nahrádza Pods podľa availability budgetu. `maxUnavailable` obmedzuje počet Node agentov, ktoré môžu byť nedostupné podľa controller statusu. Neposkytuje automaticky:

- failure-domain separation;
- node capability test;
- business-flow canary;
- host cleanup proof;
- rollback safety;
- ochranu pred rovnakou chybou na každom Node-e.

### Surge

Ak cluster/API podporuje DaemonSet surge, dve revisions môžu dočasne existovať na jednom Node-e. To je nebezpečné pri:

- host portoch;
- singleton sockets alebo lockoch;
- CNI/CSI ownership;
- eBPF programoch;
- device plugins;
- rovnakom host state directory;
- agentoch, ktoré nesmú súčasne vykonávať control writes.

Surge je bezpečný iba s explicitným same-node coexistence contractom.

### OnDelete

`OnDelete` je vhodný, keď node-by-node runbook musí pred replacementom:

- cordon-nuť Node;
- drain-nuť citlivé workloady;
- odstrániť starý host state;
- vykonať kernel/runtime compatibility check;
- nasadiť nový agent;
- overiť capability;
- až potom vrátiť Node do fleet-u.

## 10. Fleet rollout subject

Rollout nemožno prijať iba podľa `updatedNumberScheduled`.

Potrebný inventory:

```text
Node UID a failure domain
old/new Pod UID a revision
imageID a loaded configuration
effective host authority
capability canary result
application traffic cohort na Node-e
cleanup old host artifacts
rollout decision a rollback eligibility
```

Pri kritickom agentovi používaj rings, napríklad:

```text
1 canary Node
→ 1 Node per zone
→ small percentage per pool
→ remaining fleet
```

Každý ring potrebuje technical aj workload outcome, nie iba Pod readiness.

## 11. Node join

Nový Node lifecycle:

```text
instance/bootstrap
→ Node object a labels/taints
→ DaemonSet eligibility
→ agent Pod create/bind
→ host capability initialization
→ node capability canary
→ remove bootstrap taint alebo publish acceptance
→ application scheduling
```

Ak automation odstráni bootstrap taint iba podľa Node `Ready`, application Pods môžu byť umiestnené skôr než network, storage, security alebo logging agent reálne funguje.

## 12. Node drain, reboot a retirement

DaemonSet Pods sa pri drain-e spracúvajú odlišne, pretože controller ich chce na tom istom eligible Node-e znovu vytvoriť.

Maintenance contract má určiť:

- či agent musí bežať počas drain-u;
- ako ukončí host hooks a buffers;
- čo prežije reboot;
- ako zistí stale host state;
- či Node po reboot-e potrebuje novú acceptance generation;
- kedy sa odstráni Pod a host data pri retirement-e.

`--ignore-daemonsets` neznamená, že agent lifecycle je vyriešený. Znamená iba, že drain nebude čakať na ich bežné eviction odstránenie.

## 13. Resource amplification

Per-Node request sa násobí fleet size:

```text
250 Nodes × 300 MiB request = 75 000 MiB reserved memory
```

Sleduj:

- fixed CPU/memory overhead;
- per-Node log/cache/disk growth;
- image pull burst;
- control-plane object a Event load;
- kernel memory alebo eBPF map consumption;
- agent leak vynásobený počtom Nodes;
- capacity, ktorú critical priority odoberie application workloadom.

Malý per-Node drift môže byť veľký cluster-wide incident.

## 14. Worked failure: broad toleration rozšírila privileged agent

Nová template pridala `operator: Exists`, aby agent bežal na bootstrap Nodes. Agent mal host network, runtime socket a writable host state path.

```text
broad toleration
→ eligibility sa rozšíri aj na control-plane a isolated Nodes
→ privileged authority sa nasadí mimo threat modelu
→ DaemonSet status vyzerá lepšie, pretože desired/ready count rastie
→ blast radius a credential exposure sa zväčšia
```

Root cause nie je iba „príliš široká toleration“. Je to neautorizovaná zmena fleet capability subjectu bez explicitného eligible-Node inventory a authority reviewu.

## 15. Worked failure: surge spustil dve verzie CNI agenta na jednom Node-e

Rollout povolil surge. Starý a nový Pod súčasne menili rovnaký host socket, IPAM state a eBPF programy.

Výsledok:

- host lock collision;
- partial program replacement;
- nové Pod sandboxy zlyhávali;
- existujúce flows dočasne pokračovali;
- readiness oboch agentov bola nejednoznačná.

Surge zlepšuje availability iba vtedy, ak dve instances môžu bezpečne zdieľať host authority. Pri singleton node capability môže byť správnejší bounded unavailable window alebo application-aware OnDelete runbook.

## 16. Worked failure: nový Node bol Ready, ale nemal accepted dataplane

Autoscaler vytvoril Node `N9`. DaemonSet Pod vznikol a process odpovedal na liveness. Bootstrap automation odstránila taint a scheduler umiestnil Payments Pod na N9.

```text
process healthy
≠ policy a routes loaded
≠ ClusterIP/reverse path funkčný
→ Payments Pod je Ready lokálne
→ klientské requesty na N9 timeoutujú
```

Node acceptance musí obsahovať capability canary, nie iba process health.

## 17. Causal troubleshooting walkthrough: traffic zlyháva iba na jednom novom Node-e

Po scale-out-e zlyháva časť payment requestov. Všetky affected Pods bežia na N9. `atlas-net-agent` Pod je `Running` a `Ready`.

### 1. Zafixuj subject a outcome

Zaznamenaj:

```text
DaemonSet UID/generation/current revision
N9 Node UID, pool/image/kernel/runtime generation
N9 labels, taints a bootstrap timeline
agent Pod UID, admitted spec, imageID a config generation
host mounts, sockets, capabilities a eBPF/program IDs
CNI/IPAM, routes, policy a Service-dataplane generation
healthy comparison Node N8
Payments Pod/EndpointSlice UIDs a client flow tuple
expected request outcome a forbidden bypass path
```

### 2. Competing hypotheses

1. N9 nebol podľa policy eligible a agent je misscheduled alebo foreign.
2. Pod je na starej revision pre OnDelete alebo failed rollout.
3. Mutable tag/cache spustili iný digest.
4. Admission zmenila security context alebo host mount.
5. Kernel alebo architecture nie sú kompatibilné s novým agentom.
6. Host socket/port/path patrí stale procesu po bootstrap-e.
7. CNI config alebo eBPF program sa nenačítal, hoci process žije.
8. Service dataplane/conntrack je poškodený iba na N9.
9. IPAM alebo route generation je neúplná.
10. Policy registration v control plane zaostáva.
11. Readiness kontroluje iba local HTTP endpoint.
12. Payments failure je application/config problém korelovaný s N9, nie agent.

### 3. Discriminating observations

- DaemonSet eligible inventory a `numberMisscheduled`;
- Pod revision label, UID, imageID a admitted security context;
- Node kernel, modules, cgroup, runtime a OS image difference;
- host process/socket/lock a mount ownership;
- CNI config, IPAM lease, routes a interfaces;
- eBPF/program/map alebo equivalent dataplane state;
- ClusterIP, direct Pod IP a external path tests;
- conntrack, drops, MTU a reverse path;
- agent control-plane registration a policy generation;
- comparison s N8 pre ten istý exact flow.

Observation `agent Ready=True` nevylučuje nefunkčný dataplane. Observation `Pod-to-Pod funguje` nevylučuje Service dataplane failure.

### 4. Containment

- cordon-ni N9 a odstráň ho z application placementu;
- presuň alebo drain-ni affected Payments Pods podľa availability budgetu;
- pozastav ďalší node-pool scale-out a DaemonSet rollout;
- zachovaj host, kubelet, runtime a agent evidence;
- nereštartuj všetky network components naraz;
- nevypínaj policy alebo security controls ako prvý fix;
- ponechaj healthy Nodes v service.

### 5. Recovery podľa boundary

- wrong eligibility/labels → oprav fleet policy a Node metadata;
- stale revision → vykonaj bounded replacement a verify imageID;
- host stale state → audited cleanup konkrétneho socketu/programu/lease;
- kernel/runtime incompatibility → oprav node image alebo deploy compatible agent;
- incomplete dataplane → znovu inicializuj presný capability subject;
- readiness gap → pridaj capability canary a acceptance gate;
- application-only failure → oprav workload, nie node agent.

### 6. Over pôvodný outcome

Potvrď:

- N9 má správny agent Pod UID, revision a authority;
- CNI, policy a Service paths prejdú v oboch smeroch;
- žiadny stale host process, socket, map alebo lease nezostal;
- Payments Pod na N9 je Ready a jeho EndpointSlice UID je správny;
- payment authorization prejde presne raz cez N9;
- ďalší nový Node prejde rovnakým bootstrap canary;
- fleet dashboard odlišuje Pod readiness od capability acceptance.

### 7. Posuň control skôr

Pridaj:

- versionovaný eligible-Node inventory;
- admission test pre tolerations a host authority;
- native kernel/runtime compatibility preflight;
- node capability canary pred odstránením bootstrap taintu;
- ring rollout podľa zones/pools;
- same-node coexistence test pred surge;
- per-Node image/config/program generation telemetry;
- automatic cordon pri capability verdict failure.

## 18. Observation matrix

| Boundary | Subject | Kľúčové observations |
|---|---|---|
| Fleet policy | DS UID/generation + Node inventory | labels, taints, affinity, eligibility |
| Placement | Node UID ↔ Pod UID | binding, misscheduled, revision |
| Runtime | Pod/container/image subject | imageID, status, host dependencies |
| Authority | host mount/socket/device subject | effective permissions, owner, audit |
| Capability | node-local service generation | CNI/CSI/policy/log/device tests |
| Rollout | old/new per-Node revision | ring, unavailable/surge, cleanup |
| Bootstrap | Node acceptance generation | taint removal, canary, scheduling |
| Business | Node + workload flow | SLI, packet/request outcome, forbidden path |

## 19. Referenčné príkazy

```bash
kubectl get daemonset <name> -n <namespace> -o yaml
kubectl describe daemonset <name> -n <namespace>
kubectl get pods -n <namespace> -l '<selector>' -o wide
kubectl get nodes --show-labels
kubectl get controllerrevision -n <namespace>
kubectl get events -A --sort-by=.metadata.creationTimestamp
```

Node-level incident vyžaduje aj host, kubelet, runtime a agent-specific observations.

## 20. Referenčné pravidlá

- DaemonSet desired count je výsledok eligibility policy nad Node inventory.
- Eligible, scheduled, Ready a capability-accepted Node sú odlišné states.
- Tolerations sú fleet authorization policy, nie iba convenience.
- Node agent s host authority je bezpečnostne blízko host service.
- Process health nepreukazuje node capability correctness.
- `numberMisscheduled` je ownership/placement evidence, nie automatická root cause.
- Rolling budget nepreukazuje failure-domain alebo business safety.
- Surge vyžaduje same-node coexistence contract.
- `OnDelete` môže byť správny pre node-by-node application-aware runbook.
- Drain ignorujúci DaemonSet nevyrieši jeho host cleanup lifecycle.
- Per-Node overhead a drift sa násobia veľkosťou fleet-u.
- Recovery musí overiť Node capability aj workload outcome.

## 21. Kontrolné otázky

1. Aký lifecycle spája DaemonSet generation s accepted node capability?
2. Ako sa určuje eligible Node inventory?
3. Prečo Ready agent nemusí znamenať funkčný dataplane alebo plugin?
4. Ako tolerations menia bezpečnostný blast radius?
5. Kedy je DaemonSet surge nebezpečný?
6. Čo musí nový Node splniť pred prijatím workloadu?
7. Ako sa líši Pod rollout od host-state cleanupu?
8. Prečo `--ignore-daemonsets` nie je agent maintenance plan?
9. Ako odlíšiš node-agent failure od application failure?
10. Čo musí DaemonSet acceptance verdict overiť?

## Glossary impact

Relevantné pojmy: DaemonSet fleet-capability subject, eligible-Node inventory, per-Node placement subject, node capability generation, node acceptance generation, bootstrap capability gate, toleration authorization boundary, host-authority subject, same-node coexistence contract, DaemonSet rollout ring, misscheduled Pod subject, per-Node capability canary, fleet observation matrix a DaemonSet acceptance verdict.

## Oficiálna dokumentácia

- [DaemonSet](https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/)
- [Perform a rolling update on a DaemonSet](https://kubernetes.io/docs/tasks/manage-daemon/update-daemon-set/)
- [Safely drain a Node](https://kubernetes.io/docs/tasks/administer-cluster/safely-drain-node/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: StatefulSet](statefulset.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Job a CronJob →](job-cronjob.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
