# Kubernetes architecture

Kubernetes nie je vzdialený wrapper nad `docker run`. Je to distribuovaný control system, ktorý prijíma versionovaný intent cez API, rozdeľuje ownership medzi viac control loops a node agents a priebežne približuje effective workload state požadovanému výsledku.

Dominantný lifecycle tejto kapitoly:

```text
workload intent a cluster identity
→ authenticated API request
→ admitted a persisted object generation
→ controller-owned dependent graph
→ scheduler assignment
→ kubelet, runtime, CNI a CSI execution
→ Pod readiness a Service eligibility
→ application-level verification
→ continuous observation, replacement a recovery
```

Kľúčová diagnostická otázka nie je „funguje Kubernetes?“, ale:

```text
Ktorý subject a generation mali vzniknúť?
Ktorý component vlastní ďalší transition?
Čo už bolo prijaté, persistované, pridelené, vykonané a overené?
Kde sa desired, observed a effective state rozdelili?
```

## 1. Atlas scenár

Atlas Payments release `4.2.0` má bežať v production clusteri `atlas-prod-eu1`.

Release contract:

```text
Deployment: production/payments-api
Deployment UID: D42
metadata.generation: 12
image index digest: sha256:atlas420
replicas: 6
configuration epoch: C52
secret epoch: SE08
Service: production/payments-api
forbidden outcome: traffic na starý digest alebo staging dependency
required outcome: 6 ready Pods a úspešná payment authorization
```

Želaný end-to-end výsledok:

```text
API prijme generation 12
→ Deployment controller vytvorí nový ReplicaSet
→ ReplicaSet controller vytvorí 6 Pods
→ scheduler pridelí Pods vhodným Nodes
→ kubelet pripraví image, sandbox, network a volumes
→ process načíta C52 a SE08
→ readiness prejde
→ EndpointSlice obsahuje iba ready generation
→ Service traffic vykoná payment authorization exactly once
```

Každý šíp je samostatná ownership a failure boundary.

## 2. Architektúra ako rozdelenie rozhodovania a vykonania

Kubernetes má dve hlavné execution roviny.

### Control plane

Control plane:

- prijíma a chráni API requests;
- persistuje cluster state;
- vyhodnocuje desired state;
- vytvára dependent resources;
- robí scheduling a cluster-wide decisions;
- koordinuje cloud a platform integrations.

### Worker plane

Worker nodes:

- vykonávajú pridelené Pod specs;
- pripravujú images, sandboxes, networks, mounts a cgroups;
- spúšťajú application processes;
- vykonávajú probes a termination lifecycle;
- reportujú effective Node, Pod a container state.

Control plane nespúšťa application process priamo. Scheduler nespúšťa container. API server nevykonáva rollout. Kubelet nemení Deployment replicas. Každý component vlastní iba určitý transition.

## 3. API-centric integration model

Kubernetes components komunikujú o cluster state-e prevažne cez API server:

```text
users, CI a operators
         ↓
      API server
         ↕
        etcd
         ↑
controllers, scheduler, kubelets, add-ons
```

API server poskytuje spoločné boundaries pre:

- authentication;
- authorization;
- admission;
- validation a conversion;
- persistence;
- optimistic concurrency;
- list/watch;
- audit;
- subresources.

Dôsledok: priamy component-to-component call nie je automaticky authoritative state transition. Scheduler napríklad zapíše assignment do API; kubelet potom reaguje na pridelený Pod.

## 4. Jeden request, viac control loops

Pri:

```bash
kubectl apply -f deployment.yaml
```

nevznikne jedna synchronná deployment transakcia.

```text
kubectl context a caller identity
→ API request
→ authentication a authorization
→ mutating admission
→ schema/defaulting/conversion
→ validating admission
→ etcd persistence
→ Deployment watch/reconcile
→ ReplicaSet watch/reconcile
→ Pod creation
→ scheduler queue a binding
→ kubelet sync
→ runtime/CNI/CSI operations
→ Pod status a conditions
→ EndpointSlice eligibility
→ client traffic
```

API response po persistence potvrdzuje prijatie desired state-u. Nepotvrdzuje, že workload vznikol, je ready alebo je business-correct.

## 5. Cluster subject a failure boundary

Pred troubleshootingom zafixuj cluster subject:

```text
cluster name a immutable infrastructure identity
API endpoint a CA
control-plane topology
etcd cluster/member IDs
Kubernetes version
node pool generations
CNI/CSI/CRI implementations
admission a policy generation
critical add-on versions
failure-domain placement
```

Rovnaký kubeconfig context name môže po obnove alebo migrácii smerovať na iný cluster. Rovnaký object name môže označovať inú UID generation. Rovnaký image tag môže označovať iný digest.

## 6. API server a etcd

`kube-apiserver` je front-end control plane-u. `etcd` je authoritative backing store pre Kubernetes API state.

```text
valid request
→ API invariants
→ etcd quorum write
→ new resourceVersion
→ watches inform consumers
```

Ak API server nevie persistovať state, write transition nie je complete. Ak etcd stratí quorum, bezpečné writes sa zastavia, hoci už spustené Pods môžu dočasne pokračovať.

### Failure boundary: API funguje na TCP, ale nie je ready

Load balancer môže úspešne otvoriť TCP connection, no API server môže mať:

- etcd latency alebo failure;
- nedokončené post-start hooks;
- informer/cache sync problém;
- admission dependency failure;
- certificate alebo authentication problém.

Použi semantic readiness, nie iba open port.

## 7. Controllers a dependent object graph

Controllers menia top-level intent na nižšie resource contracts:

```text
Deployment D42 generation 12
→ ReplicaSet RS-new
→ Pods P1..P6
```

Dependent graph sa viaže cez:

- owner UID;
- labels a selectors;
- controller-specific status;
- generation a conditions;
- finalizers pri external state-e.

Controller nevykonáva celý workload lifecycle sám. Vytvorí alebo upraví ďalší object a ďalší owner pokračuje.

## 8. Scheduler assignment boundary

Scheduler sleduje Pods bez Node assignmentu.

```text
unscheduled Pod
→ candidate Node inventory
→ hard filters
→ scoring
→ reservation/permit podľa frameworku
→ binding
```

Scheduler posudzuje deklarované requests a constraints. Nespúšťa image, network ani process a nečaká na readiness.

Diagnostické rozdelenie:

```text
Pod Pending bez nodeName
→ scheduling boundary

Pod má nodeName, ale je ContainerCreating
→ kubelet/runtime/network/storage boundary
```

## 9. Node execution boundary

Keď je Pod pridelený Node-u, kubelet približne koordinuje:

```text
observe assigned Pod spec
→ local admission a Node preconditions
→ volume/device preparation
→ image resolution a pull
→ Pod sandbox a namespaces
→ CNI network
→ containers a init ordering
→ probes a lifecycle hooks
→ Pod status reporting
```

Kubelet používa CRI-compatible runtime. Docker Engine nie je povinná worker-node vrstva.

CNI, CSI a runtime plugins môžu mať host-level privileges. Ich failure alebo compromise má inú boundary než bežný application Pod.

## 10. Service eligibility nie je Pod existence

Kubernetes môže mať:

- uložený Deployment;
- vytvorený ReplicaSet;
- Running Pod;
- neúspešnú readiness probe;
- žiadny eligible EndpointSlice endpoint;
- nefunkčný business transaction.

```text
process exists
≠ Pod Ready
≠ Service endpoint eligible
≠ client path funguje
≠ business outcome je správny
```

Architektúra preto potrebuje status a verification na viacerých úrovniach.

## 11. Observed state a eventual consistency

Každý actor pozoruje state s určitým oneskorením:

- API object môže byť persistovaný skôr, než ho controller spracuje;
- informer cache môže krátko zaostávať;
- scheduler assignment môže predchádzať kubelet execution;
- kubelet status môže zaostávať za runtime processom;
- EndpointSlice alebo dataplane môže zaostávať za readiness zmenou;
- externý load balancer môže zaostávať za Service statusom.

Eventual consistency neznamená, že všetko sa „časom opraví“. Permanentný invalid intent, chýbajúca capacity alebo broken dependency môže zostať nekonvergentná bez zmeny vstupu.

## 12. High availability ako zachovanie konkrétnych transitions

HA nie je iba počet replík.

### API layer

Potrebuje:

- viac ready API server instances;
- stabilný endpoint/load balancer;
- rovnaké trust roots a policy;
- dostupný etcd quorum;
- failure-domain separation.

### etcd

Potrebuje:

- quorum;
- nízku a stabilnú disk/network latency;
- správnu member topológiu;
- snapshots a testovaný restore;
- capacity a certificate lifecycle.

### Scheduler a controller manager

Môžu používať viac replicas s leader election. Leader election vyberá active instance, ale neposkytuje exactly-once execution ani idempotenciu.

### Failure boundary: tri replicas v jednom fyzickom doméne

```text
3 control-plane VMs
→ všetky na jednom hypervisor hoste
→ host failure
→ všetky replicas zaniknú naraz
```

Replica count bez nezávislého failure-domain placementu nie je požadované HA.

## 13. Core components, integrations a add-ons

Pri incidente rozlišuj:

### Core control plane

- API server;
- etcd;
- scheduler;
- controller manager;
- cloud controller manager podľa topológie.

### Node execution

- kubelet;
- container runtime;
- CNI;
- CSI/node storage components;
- Service dataplane implementation.

### Add-ons a extensions

- DNS;
- metrics;
- ingress/Gateway controller;
- policy engine;
- certificate manager;
- custom controllers/operators;
- aggregated APIs.

Názov resource-u v API nehovorí, kto implementuje jeho behavior. CRD bez active controlleru je uložený intent bez automatizácie.

## 14. Static Pods a bootstrap boundary

V kubeadm-like topológii môžu control-plane components bežať ako static Pods.

```text
local manifest na control-plane Node-e
→ kubelet
→ runtime container
→ mirror Pod v API
```

Authoritative source static Podu je local manifest, nie mirror Pod object. Pri API outage nemusia fungovať `kubectl logs` ani API-based diagnostics; potrebný je node-level runtime, filesystem a journal access.

## 15. Trust boundaries

Kritické boundaries:

- API endpoint, kubeconfig a caller credentials;
- API server identities a signing keys;
- etcd data a snapshots;
- admission webhooks;
- controller service accounts;
- kubelet API a node credentials;
- node OS a runtime;
- CNI/CSI plugins;
- registry a image supply chain;
- cloud provider identities.

Cluster nie je automaticky silná isolation boundary pre vzájomne nedôveryhodných tenants. Node compromise môže sprístupniť workloads a credentials na Node-e; privilegovaná control-plane identity môže mať cluster-wide dopad.

## 16. Failure scenáre podľa transitionu

### API request sa k serveru nedostane

Možné boundaries: context, DNS, route, load balancer, TLS.

### API request je `Unauthorized` alebo `Forbidden`

Server je dostupný; zlyhala identity alebo authorization boundary.

### Request timeoutuje pri admission

Core API a etcd môžu byť healthy, ale synchronous webhook dependency blokuje matching writes.

### Object vznikol, dependent graph nie

Deployment alebo custom controller môže byť down, bez leadershipu, preťažený alebo bez permissions.

### Pods ostávajú `Pending`

Scheduler/capacity/constraints/PVC binding boundary.

### Pod je assigned, container nevznikne

Kubelet, image, runtime, CNI, CSI, mount alebo Node condition boundary.

### Pod je Ready, Service nefunguje

Selector, EndpointSlice, dataplane, DNS, network policy alebo application listen/client path boundary.

### API je unavailable, workload beží

Management plane je poškodená, ale existujúce processes môžu pokračovať. To nie je plné zdravie clusteru; nové scheduling, replacement a config changes sú obmedzené.

## 17. Worked failure: admission webhook zablokoval celý rollout

Atlas nasadil nový policy webhook fail-closed na všetky Pod create/update requests. Webhook mal jednu repliku a pri vlastnom rolling update prestal byť reachable.

```text
API server healthy
+ etcd healthy
+ controllers healthy
→ ReplicaSet controller vytvára Pod request
→ admission volá unavailable webhook
→ request timeout/reject
→ žiadne nové Pods
→ staré Pods zostanú
```

`kubectl get nodes` a API `/readyz` mohli vyzerať zdravo, ale workload write path bol nefunkčný pre konkrétny match scope.

Recovery nie je restart všetkých control-plane components. Potrebuje:

- identifikovať webhook configuration a match scope;
- obnoviť webhook endpoint alebo aktivovať reviewovaný break-glass;
- overiť CA/DNS/network/readiness;
- znovu reconcile-nuť blocked objects;
- zúžiť scope, timeout a failure policy;
- zabezpečiť independent availability webhooku.

## 18. Worked failure: etcd quorum loss pri stále bežiacich Pods

Tri etcd members boli rozdelené sieťovou partition tak, že žiadna strana nemala bezpečné quorum.

```text
existujúce containers pokračujú
→ kubelet môže dočasne udržať local workload
→ API writes timeoutujú alebo zlyhávajú
→ controllers nemôžu persistovať transitions
→ scheduler nemôže zapisovať nové assignments
→ self-healing je obmedzený
```

„Aplikácia stále odpovedá“ neznamená, že cluster je healthy alebo schopný recovery po ďalšom Node failure.

## 19. Causal troubleshooting walkthrough: Deployment je prijatý, ale release sa nehýbe

`kubectl apply` pre Atlas release `4.2.0` skončil úspešne. Deployment má generation 12, no šesť starých Pods naďalej obsluhuje traffic a nový ReplicaSet má nula Pods.

### 1. Zafixuj subject a pôvodný outcome

Zaznamenaj:

```text
cluster endpoint, CA a cluster UID/identity
caller a field manager
Deployment namespace/name/UID/generation/resourceVersion
spec image digest, replicas, strategy a selectors
status observedGeneration a conditions
old/new ReplicaSet UID a revisions
expected Pod template hash
admission configuration generation
controller-manager leader a version
scheduler/kubelet/runtime generations podľa ďalšej vrstvy
required business outcome a forbidden old/staging outcomes
```

### 2. Competing hypotheses

1. Apply smeroval na nesprávny cluster/context.
2. Mutating admission zmenila image, selector alebo Pod template.
3. Deployment controller nevidel generation 12.
4. Controller-manager nemá active leader alebo je preťažený.
5. New ReplicaSet existuje, ale selector/ownership je chybný.
6. Pod create requests blokuje admission webhook alebo quota.
7. ReplicaSet controller nemá permissions.
8. API/etcd writes zlyhávajú po create requeste.
9. Scheduler nie je relevantný, pretože Pods ešte nevznikli.
10. Status je stale a runtime už obsahuje inú generation.
11. Iný field manager okamžite vracia Pod template na starý digest.
12. Rollout je paused alebo blokovaný strategy invariants.

### 3. Discriminating observation points

- `kubectl config current-context` a server/CA identity;
- live Deployment YAML vrátane `managedFields`, generation a status;
- ReplicaSet ownerReferences, revisions, selectors a Pod template hashes;
- audit/admission rejection a latency evidence;
- controller-manager leader, queue depth a logs pre exact UID;
- API response codes a etcd write latency;
- ResourceQuota a policy verdicts;
- events zoradené podľa času;
- audit field-manager writes po pôvodnom apply;
- absence/presence Pod create requests.

Observation „žiadne nové Pods“ diskriminuje scheduling až vtedy, keď je potvrdené, že Pod objects vôbec vznikli.

### 4. Containment

- nezmaž starý ReplicaSet ani fungujúce Pods;
- pozastav ďalšie automation writes nad rovnakými fields;
- zachovaj audit, events, controller logs a live object YAML;
- neforce-ni conflicts bez ownership rozhodnutia;
- obmedz traffic iba vtedy, ak starý release porušuje forbidden outcome.

### 5. Recovery podľa boundary

- wrong context → zastav zmenu, audituj zasiahnutý cluster a aplikuj na správny subject;
- admission mutation/rejection → oprav policy/webhook a znovu validuj final admitted object;
- controller unavailable → obnov leader/permissions/queue processing;
- ownership conflict → definuj authoritative field managera a reconcile-ni current object;
- selector/owner mismatch → oprav versionovaný object contract bez manuálnej adopcie cudzích Pods;
- etcd/API latency → obnov persistence health pred ďalšími writes;
- paused/strategy constraint → vykonaj explicitný reviewovaný transition.

### 6. Over pôvodný outcome

Potvrď:

- Deployment observed generation 12;
- nový ReplicaSet s correct UID/template digest;
- šesť new-generation Pods;
- scheduler assignments a kubelet execution;
- C52 a SE08 loaded state;
- readiness a EndpointSlice eligibility;
- payment authorization exactly once;
- žiadny old digest ani staging dependency v active path-e.

### 7. Posuň control skôr

Pridaj:

- cluster-subject preflight;
- server-side dry run a admitted-object diff;
- controller generation-lag SLO;
- webhook availability a match-scope tests;
- field-ownership policy;
- rollout verification via UID/generation/digest chain;
- business synthetic via Service path.

## 20. Observation matrix

| Boundary | Subject | Kľúčové observations |
|---|---|---|
| Client/API endpoint | context, endpoint, caller | kubeconfig, TLS, API response |
| Admission | webhook/policy generation | mutation, reject, timeout, audit |
| Persistence | object UID/resourceVersion, etcd cluster | API latency, etcd quorum/write |
| Controller | owner UID/generation, queue key | observedGeneration, dependents, logs |
| Scheduler | Pod UID a constraint set | nodeName, FailedScheduling, queue |
| Node execution | Pod UID, Node, runtime sandbox | kubelet, runtime, CNI/CSI, status |
| Service path | EndpointSlice generation, client flow | readiness, selectors, dataplane, DNS |
| Business | request/operation ID | SLI, downstream audit, invariants |

Matrix neurčuje príčinu. Pomáha zvoliť observation point, ktorý odlíši competing hypotheses.

## 21. Managed a self-managed responsibility

Managed control plane typicky presúva časť ownershipu na providera, ale zákazník naďalej vlastní:

- workload specs a images;
- namespaces, RBAC a identities;
- policy a webhook configuration;
- node pools alebo compute profile podľa služby;
- CNI/CSI/add-on choices v podporovanom rozsahu;
- persistent data protection;
- application readiness a business verification;
- upgrade compatibility a deprecated APIs.

„Managed“ neznamená, že provider overí správnosť desired state-u alebo obnoví application data.

## 22. Referenčné pravidlá

- Kubernetes API success potvrdzuje accepted/persisted intent, nie workload readiness.
- Object, controller, scheduler, kubelet a application majú odlišné ownership boundaries.
- Scheduler priraďuje Node; kubelet vykonáva Pod.
- Running process, Ready Pod, eligible endpoint a correct business outcome sú odlišné states.
- etcd quorum chráni persistent cluster-state transitions.
- Leader election neposkytuje exactly-once execution.
- Static Pod mirror object nie je authoritative manifest.
- Add-on alebo webhook môže byť critical control-plane dependency bez toho, aby bol core componentom.
- Replica count bez failure-domain separation nie je HA.
- Kubernetes môže spoľahlivo reprodukovať chybný desired state.
- Troubleshooting začína exact cluster/object/generation subjectom a vlastníkom nasledujúceho transitionu.

## 23. Kontrolné otázky

1. Aký lifecycle spája API request s application business outcome-om?
2. Prečo API response po `apply` nepotvrdzuje rollout success?
3. Aký je rozdiel medzi controllerom, schedulerom a kubeletom?
4. Prečo `Pod Pending` bez `nodeName` patrí do inej boundary než `ContainerCreating`?
5. Čo znamená strata etcd quorum pre už bežiace a nové workloads?
6. Prečo viac control-plane replík nemusí znamenať HA?
7. Ako admission webhook ovplyvňuje write-path availability?
8. Prečo mirror Pod nie je authoritative source static Podu?
9. Aké observations odlíšia controller failure od scheduler failure?
10. Ako overíš pôvodný workload outcome po recovery?

## Glossary impact

Relevantné pojmy: Kubernetes control-chain subject, cluster subject, API-to-workload lifecycle, admitted object generation, controller ownership boundary, scheduler assignment subject, node execution subject, Service eligibility generation, management-plane/workload-plane split, control-plane write path, etcd quorum boundary, static Pod authority, application acceptance subject a Kubernetes architecture observation matrix.

## Oficiálna dokumentácia

- [Kubernetes components](https://kubernetes.io/docs/concepts/overview/components/)
- [Cluster architecture](https://kubernetes.io/docs/concepts/architecture/)
- [Communication between Nodes and the control plane](https://kubernetes.io/docs/concepts/architecture/control-plane-node-communication/)
- [Controllers](https://kubernetes.io/docs/concepts/architecture/controller/)
- [Leases](https://kubernetes.io/docs/concepts/architecture/leases/)
- [Static Pods](https://kubernetes.io/docs/concepts/workloads/pods/static-pods/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Docker troubleshooting](../08-container-fundamentals-and-docker/docker-troubleshooting.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: API a object model →](api-object-model.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
