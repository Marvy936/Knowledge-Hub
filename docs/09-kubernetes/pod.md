# Pod

Pod je najmenší deployable compute object v Kubernetes, ale nie je synonymom containeru ani malou VM. Je to versionovaný runtime envelope pre jednu workload repliku: scheduler ho pridelí jednému Node-u, kubelet z jeho immutable specu vytvorí sandbox, mounts a containers a vyššie controllers ho pri strate nahradia novým Pod UID.

Dominantný lifecycle tejto kapitoly:

```text
controller Pod template a release intent
→ admitted Pod UID a spec snapshot
→ scheduling a Node assignment
→ local admission, sandbox, network a volumes
→ projected configuration a image resolution
→ init, sidecar a application startup
→ startup/liveness/readiness evaluation
→ Pod conditions a EndpointSlice eligibility
→ steady execution, restart alebo degradation
→ graceful termination a cleanup
→ controller-managed replacement a outcome verification
```

Pri diagnostike sa nepýtaj iba „aký má Pod status?“. Pýtaj sa:

```text
Ktorý Pod UID a template generation skúmam?
Ktoré časti specu sú immutable snapshoty?
Vznikol sandbox, mount, image a application process?
Je process Running, container Ready, Pod Ready a endpoint eligible?
Ide o restart toho istého Podu alebo replacement novou UID?
```

## 1. Atlas Pod subject

Atlas Payments release `4.2.0` má Pod:

```text
Deployment UID/generation: D42/12
ReplicaSet UID: RS42
Pod: production/payments-api-7d6f9d8b7b-k4m2p
Pod UID: P42
Pod template hash: 7d6f9d8b7b
Node UID: N7
image digest: sha256:4a20...
config generation: C52
secret epoch: SE08
service account: payments-api
readiness gate: atlas.example/lb-registered
termination grace: 45 s
```

Pôvodný outcome:

- application a sidecar používajú správny digest a config;
- init úloha dokončí iba idempotentnú local prípravu;
- Pod sa stane Ready až po application readiness a external LB registration;
- Service pošle traffic iba na new-generation endpoint;
- graceful termination prestane prijímať nové requests a dokončí in-flight payment;
- replacement novým Pod UID nevytvorí duplicate authorization ani nestratí durable state.

## 2. Pod je runtime envelope jednej repliky

Pod zoskupuje containers, ktoré musia zdieľať placement a lifecycle.

Typicky zdieľajú:

- jeden Node;
- Pod network namespace, IP a port space;
- loopback `localhost`;
- explicitne mountované Pod volumes;
- scheduling a disruption boundary;
- Pod-level identity, service account a časť security contextu.

Každý container stále môže mať vlastný image, command, environment, mounts, cgroup resources, probes a container-level security context.

Správny dôvod pre multi-container Pod je silný runtime coupling:

```text
musí byť co-scheduled
+ musí zdieľať localhost alebo volume
+ má spoločný replacement lifecycle
+ nezávislé škálovanie nedáva zmysel
```

Dve nezávislé business services s odlišným scalingom alebo rolloutom nemajú byť v jednom Pode.

## 3. Pod identity a immutable instance

Pod identity jednej inštancie tvorí najmä:

```text
cluster
+ namespace/name
+ metadata.uid
+ ownerReferences
+ template hash/revision
+ effective admitted spec
```

Controller replacement vytvorí nový Pod:

- s novým UID;
- často s novým generated name;
- potenciálne na inom Node-e;
- typicky s novou Pod IP;
- s novými container a sandbox IDs;
- bez pôvodnej writable layer a `emptyDir` dát.

Meno alebo label nestačí na lifetime identity. Diagnostika, log correlation a external registration majú používať Pod UID alebo vyšší release subject.

## 4. Pod spec je prevažne snapshot, update je často replacement

Mnohé Pod fields sa po vytvorení nedajú bezpečne alebo vôbec meniť in-place. Bežný update model je:

```text
zmena Pod template-u vyššieho controlleru
→ nový template hash/revision
→ nový Pod UID
→ starý Pod graceful termination
```

Dôsledky:

- zmena ConfigMap/Secret použitá cez environment nemení už bežiaci process environment;
- oprava súboru vo writable layer nie je súčasťou template-u;
- ručný zásah do containeru sa pri replacement-e stratí;
- mutable image tag bez template transitionu nevytvára spoľahlivú release identity.

## 5. Creation chain

```text
Pod template
→ API conversion/defaulting/admission
→ persisted Pod UID a spec
→ scheduler assignment
→ kubelet local admission
→ volumes a projected data
→ CRI sandbox a CNI
→ image pull/unpack
→ init containers
→ sidecars/application containers
→ probes a status
```

Každý transition má iného vlastníka. `Pending` bez Node assignmentu patrí scheduler boundary. `ContainerCreating` po assignment-e patrí worker-node dependencies. `Running` s `Ready=False` patrí runtime/probe/readiness contractu.

## 6. Shared network identity

Containers v jednom Pode používajú rovnaký Pod IP a port namespace.

```text
main container → localhost:15000 → proxy sidecar
```

Dôsledky:

- dva containers nemôžu bindovať rovnakú adresu a port;
- `localhost` neoznačuje iba aktuálny container;
- network policy a Service routing typicky pracujú s Pod endpointom;
- kompromitovaný sidecar môže pozorovať alebo meniť Pod-local traffic podľa architektúry;
- `hostNetwork` presúva workload do host network boundary a mení exposure aj scheduling constraints.

Pod IP nie je stabilná service identity. Stabilnejší routing poskytuje Service, prípadne StatefulSet/headless Service pre per-replica model.

## 7. Pod sandbox a readiness na štart containers

Runtime sandbox drží zdieľané runtime resources Podu, najmä network namespace.

```text
CRI RunPodSandbox
→ CNI setup a Pod IP
→ volume/projected-data readiness
→ init a application containers
```

Ak sandbox nevznikne, application troubleshooting je predčasný. Pod môže mať `FailedCreatePodSandBox`, IPAM, CNI, runtime alebo Node disk problém.

Niektoré clustre reportujú samostatnú Pod condition pre pripravenosť sandboxu a networku na štart containers. Pri jej použití vždy viaž interpretáciu na konkrétnu cluster verziu a feature configuration.

## 8. Volumes a data lifecycle

Pod definuje volumes a containers ich mountujú do vlastných filesystem views.

Dôležité lifecycle rozdiely:

```text
emptyDir
→ prežije container restart
→ neprežije zánik Pod UID

PVC-backed volume
→ môže prežiť Pod replacement
→ potrebuje attach/mount a application consistency contract

projected ConfigMap/Secret/token
→ node materialization a update semantics podľa source/mount typu
→ process nemusí automaticky reloadnúť obsah

hostPath
→ host-specific data a vysoká security/portability väzba
```

Persistentný volume nechráni pred application-level corruption. `emptyDir` nie je cache vhodná na jedinú durable kópiu výsledku.

## 9. Configuration a secret effective state

Source object, mounted bytes a process-loaded state sú tri odlišné subjects.

```text
Secret SE09 existuje v API
→ kubelet/projected volume môže aktualizovať súbor
→ application stále používa connection vytvorenú zo SE08
```

Pri environment variables je snapshot vytvorený pri container start-e. Pri mounted súboroch sa obsah môže aktualizovať, ale application musí mať správny reload contract.

Rollout verdict má overiť:

- source ConfigMap/Secret generation;
- Pod spec reference;
- mounted checksum alebo file identity podľa bezpečného modelu;
- process-loaded config/secret epoch bez vypísania tajomstva;
- downstream authentication a old-credential revocation podľa secret lifecycle-u.

## 10. Init containers

Regular init containers bežia postupne pred application containers a každý musí úspešne skončiť.

Vhodné úlohy:

- lokálna príprava shared volume;
- schema alebo config validation bez durable side effectu;
- fetch immutable artifactu s overením digestu;
- bounded dependency preflight.

Riziká:

- nekonečný dependency wait maskuje permanentný problém;
- ne-idempotentná migrácia sa zopakuje po Pod replacement-e;
- marker súbor vznikne pred dokončením operácie;
- init container má odlišnú identity alebo network policy než application;
- veľké init requests ovplyvnia scheduling/resource calculation.

Cluster-wide alebo shared database migration potrebuje external coordination; Pod init container nie je automaticky singleton.

## 11. Sidecar containers

Sidecar je pomocný container so spoločným placementom a Pod lifecycle-om. Môže poskytovať proxy, telemetry, config sync alebo local security službu.

Jeho contract musí definovať:

- podporovanú startup a shutdown semantics konkrétneho Kubernetes API;
- localhost port ownership;
- resources a failure behavior;
- readiness príspevok;
- log/metric ownership;
- behavior pri main-container completion alebo restart-e.

Failure boundaries:

- sidecar bindne port skôr než application;
- proxy je Ready, ale main application nie;
- sidecar memory leak vyvolá Pod pressure/OOM;
- shutdown sidecaru blokuje alebo predlžuje Pod termination;
- sidecar používa širšie credentials než main container.

## 12. Ephemeral containers a debugging

Ephemeral container je break-glass diagnostický zásah do existujúceho Podu, nie trvalá oprava desired state-u.

```bash
kubectl debug pod/<pod> -n <namespace> -it --image=<approved-debug-image>
```

Kontroluj:

- RBAC na ephemeral-container subresource;
- approved image a supply chain;
- namespace/process visibility;
- secret a network exposure;
- audit trail;
- cleanup a následnú opravu v source/template vrstve.

Diagnostický container nemení fakt, že poškodený Pod môže byť disposable a jeho manual fix zanikne.

## 13. Pod phase, conditions a container states

Tri rozdielne evidence vrstvy:

```text
Pod phase
→ high-level lifecycle summary

Pod conditions
→ structured readiness/scheduling/initialization facts

container state/status
→ Waiting, Running alebo Terminated + reason/exit/restarts/imageID
```

Príklad:

```text
phase=Running
ContainersReady=True
Ready=False
```

Možné vysvetlenie: všetky containers sú ready, ale custom readiness gate chýba alebo je `False`.

`CrashLoopBackOff`, `ContainerCreating` a `Terminating` nie sú samostatné Pod phases. Sú to reasons alebo CLI presentation states, ktoré treba rozložiť na underlying conditions a container states.

## 14. Startup, liveness a readiness

```text
startup probe
→ chráni pomalý štart pred liveness rozhodnutím

liveness probe
→ rozhoduje o restart-e containeru

readiness probe
→ rozhoduje o container/Pod traffic eligibility
```

Probe je control signal, preto musí testovať mechanizmus, ktorý jej action dokáže napraviť.

Nesprávna liveness závislá od vzdialenej databázy:

```text
databáza má incident
→ liveness zlyhá na všetkých Pods
→ kubelet restartuje zdravé application processes
→ kapacita klesne a load na databázu rastie
→ restart storm zosilní incident
```

Readiness môže dependency zohľadniť opatrnejšie, ale úplné odpojenie všetkých replicas pri shared dependency incidente môže tiež zhoršiť recovery. Probe contract musí vychádzať z application failure modelu.

## 15. Readiness gates a Service eligibility

Custom readiness gate pridáva external/platform condition do Pod readiness.

```text
containers ready
+ všetky readiness gates True
+ Node readiness rules
→ Pod Ready
→ EndpointSlice ready endpoint
```

Ak condition chýba, gate je nesplnená. Controller, ktorý gate vlastní, potrebuje:

- stabilný Pod UID correlation;
- generation-aware external registration;
- cleanup pri Pod deletion;
- failure a timeout condition;
- leader/retry/idempotency model.

Pod `Ready=True` ešte nepreukazuje správny Service selector, dataplane ani business response.

## 16. Resource requests, limits a Pod-level result

Requests ovplyvňujú placement a resource shares; limits ovplyvňujú enforcement.

Pod footprint zahŕňa:

- všetky application containers;
- sidecars;
- init-container scheduling calculation;
- sandbox/runtime overhead;
- volumes, logs a kernel buffers;
- RuntimeClass overhead podľa konfigurácie.

Failure boundaries:

- CPU throttling pri nízkej priemernej utilization;
- cgroup OOM pri voľnej Node memory;
- sidecar spotrebuje väčšinu Pod budgetu;
- `emptyDir` alebo logs vyvolajú DiskPressure;
- BestEffort/Burstable workload je skôr evictovaný pri pressure.

## 17. Security a workload identity

Pod-level a container-level security contract môže zahŕňať:

- service account a projected token;
- runAsUser/runAsGroup/fsGroup;
- capabilities a privilege escalation;
- read-only root filesystem;
- seccomp, SELinux a ďalšie runtime controls;
- host namespaces, devices a hostPath;
- image identity a executable ownership.

`runAsNonRoot` alebo numeric UID nestačia, ak image files alebo mounted volume nemajú kompatibilné ownership/permissions. `privileged` ako rýchla oprava odstraňuje viac isolation controls naraz a mení threat boundary celého Node-u.

## 18. Container restart vs. Pod replacement

```text
container restart
→ rovnaký Pod UID
→ spravidla rovnaký sandbox, Pod IP a emptyDir
→ rastie restart count

Pod replacement
→ nový Pod UID
→ nový sandbox/processes
→ často iný Node/IP
→ emptyDir a writable layer sa stratia
```

CrashLoopBackOff je kubelet backoff pri opakovanom container failure. Vyšší controller môže súčasne považovať Pod za existujúcu repliku, hoci nie je Ready.

## 19. Pod disruption a recovery owner

Pod môže zaniknúť pre:

- Deployment rollout alebo scale-down;
- Node drain či pressure eviction;
- preemption;
- Node failure/partition;
- user deletion;
- Job completion;
- autoscaling;
- policy alebo platform recovery.

Pod sám si nevytvorí replacement na inom Node-e. Recovery owner je workload controller. Priamo vytvorený Pod po Node failure nemá bežný replica replacement contract.

PDB obmedzuje iba určitú triedu voluntary disruptions. Nechráni pred Node failure, application crashom ani chybným rolloutom.

## 20. Graceful termination lifecycle

Zjednodušený flow:

```text
delete/eviction intent a grace period
→ Pod označený na termination
→ endpoint readiness/traffic transition
→ PreStop, ak existuje
→ termination signal container PID 1
→ application drain a flush
→ force kill po grace period
→ CNI/CSI/runtime cleanup
→ object a external-registration cleanup
```

Pod termination grace countdown zahŕňa aj čas `PreStop`. Ak hook spotrebuje celý budget, application môže dostať minimum času na vlastný shutdown.

Application musí:

- prestať prijímať novú prácu;
- dokončiť alebo bezpečne odovzdať in-flight operácie;
- flushnúť relevantný state;
- reagovať na termination signal;
- mať bounded shutdown;
- tolerovať hard kill a retry podľa business invariantov.

## 21. Static, mirror a direct Pods

### Direct Pod

Je vytvorený priamo cez API bez higher-level controlleru. Vhodný je hlavne na learning alebo diagnostiku; nemá rollout a replica replacement model.

### Static Pod

Autoritatívny manifest je na konkrétnom Node-e a kubelet ho reconcile-uje lokálne. Mirror Pod v API je observability reprezentácia, nie source of truth.

### Controller-managed Pod

Owner chain vedie na ReplicaSet, StatefulSet, DaemonSet, Job alebo iný controller. Desired state sa mení na vyššej vrstve, nie ručnou opravou Podu.

## 22. Worked failure: Secret sa zmenil, Pod používal starú credential epoch

API Secret bol aktualizovaný z `SE08` na `SE09`. Pod používal Secret cez environment variable a nebol nahradený.

```text
Secret object generation sa zmení
→ bežiaci process environment zostane snapshot SE08
→ dashboard sleduje iba source Secret
→ rollout vyzerá „aktualizovaný“
→ downstream po revokácii SE08 odmieta requests
```

Recovery vyžaduje nový container/Pod subject a overenie process-loaded epoch. Ručný refresh source Secretu bez consumer rollout-u nie je rotation completion.

## 23. Worked failure: liveness probe vytvorila restart storm

Liveness endpoint vracal failure pri nedostupnej shared databáze.

```text
dependency outage
→ všetky liveness probes fail
→ všetky main containers restartujú
→ readiness a capacity klesnú na nulu
→ reconnect burst zaťaží databázu po návrate
```

Fix nie je iba zvýšiť `failureThreshold`. Treba oddeliť process deadlock/liveness od dependency readiness a navrhnúť reconnect/backoff behavior.

## 24. Worked failure: PreStop spotreboval celý termination budget

Pod mal 30-sekundový grace period a `PreStop` vykonával 30-sekundový sleep. Main process potom nestihol dokončiť in-flight payment a dostal force kill.

```text
grace countdown začne
→ PreStop spotrebuje budget
→ termination signal príde neskoro
→ application nemá čas na drain
→ request retry vytvorí duplicate risk
```

Recovery musí zväčšiť alebo lepšie rozdeliť termination budget a overiť end-to-end draining, nie iba hook completion.

## 25. Worked failure: sidecar a main container súťažili o port

Proxy sidecar a application sa pokúsili bindovať `0.0.0.0:8443` v spoločnom Pod network namespace. Sidecar vyhral race a main process skončil s `address already in use`.

Pod zostal v CrashLoopBackOff, hoci network a image pull boli healthy. Observation port listenera v Pod namespace odlíšila runtime configuration od CNI alebo Service failure.

## 26. Causal troubleshooting walkthrough: Pod je Running, ale nie je Ready

Pod `P42` má:

```text
phase=Running
ContainersReady=True
Ready=False
restartCount=0
Node N7 Ready=True
```

Service ešte posiela traffic iba na starú revision.

### 1. Zafixuj subject a pôvodný outcome

Zaznamenaj:

```text
cluster, namespace/name/Pod UID
owner ReplicaSet/Deployment UID a generation
template hash a image digest
Node UID a Pod IP
container imageIDs, states a restart counts
C52 a SE08 effective-state evidence
startup/liveness/readiness probe spec a results
readinessGates a Pod conditions
EndpointSlice targetRef UID/conditions
external LB registration subject
required payment transaction outcome
```

### 2. Competing hypotheses

1. Application readiness probe zlyháva.
2. Sidecar container nie je ready, hoci main container je.
3. Custom readiness gate chýba alebo je `False`.
4. Gate controller koreluje podľa mena namiesto Pod UID.
5. Node readiness alebo control-plane observation je stale.
6. Pod condition status patrí predchádzajúcemu sandbox/container pokusu.
7. Mutating admission pridala gate alebo sidecar, ktorý source manifest neobsahoval.
8. Application process načítal starú config/secret epoch a readiness to správne odmieta.
9. EndpointSlice controller zaostáva; Pod už je Ready, ale endpoint ešte nie.
10. Service selector nevyberá nový Pod, čo je odlišné od Pod readiness.
11. Readiness endpoint kontroluje external dependency a je v global outage.
12. Probe ide na nesprávny port/path kvôli shared-port alebo proxy contractu.

### 3. Discriminating observation points

- live admitted Pod YAML, UID, conditions a readiness gates;
- per-container `ready`, state, imageID a last state;
- kubelet probe Events/logs a direct probe z rovnakého network contextu;
- listeners a localhost path v Pod network namespace;
- main/sidecar loaded config generation a secret epoch;
- gate-controller logs, owner UID a external registration ID;
- Node Lease/condition timeline;
- EndpointSlice targetRef UID a readiness/serving/terminating conditions;
- Service selector match;
- audit/admission mutation evidence.

`ContainersReady=True` diskriminuje základnú per-container readiness, ale nevylučuje custom readiness gate. `Ready=True` bez EndpointSlice match by posunulo problém za Pod boundary.

### 4. Containment

- ponechaj staré Ready replicas a traffic;
- nezmaž Pod pred zachovaním conditions, Events, logs a external registration evidence;
- neodstraňuj readiness gate naslepo;
- nezmeň liveness tak, aby maskovala deadlock;
- zastav conflicting automation nad probe/gate fields;
- obmedz rollout scale-down, kým nový Pod nie je accepted.

### 5. Recovery podľa boundary

- probe contract → oprav path/port/timeout alebo application readiness semantics;
- sidecar readiness → oprav sidecar startup/resources/health;
- missing gate → obnov gate controller a nastav condition pre exact Pod UID;
- stale external registration → cleanup-ni old UID a zaregistruj P42 idempotentne;
- old config/secret → vytvor nový Pod s correct consumer snapshot;
- EndpointSlice lag → obnov controller path a over targetRef;
- selector mismatch → oprav higher-level immutable selection contract bezpečným rolloutom;
- global dependency outage → použite reviewovaný degradation model namiesto restart stormu.

### 6. Over pôvodný outcome

Potvrď:

- Pod UID P42 alebo jeho reviewovaný replacement má správny digest, C52 a SE08;
- všetky required containers sú ready;
- všetky readiness gates sú `True` a viazané na správny UID;
- EndpointSlice obsahuje iba správne new-generation ready endpoints;
- traffic prechádza cez Service/proxy path;
- payment authorization prejde presne raz;
- old revision sa začne scale-downovať až po acceptance;
- termination test dokončí in-flight request bez force killu.

### 7. Posuň control skôr

Pridaj:

- admitted-Pod diff v release evidence;
- UID-aware readiness-gate controller testy;
- probe contract tests pri dependency outage a overload-e;
- process-loaded config/secret epoch metric;
- EndpointSlice targetRef verification;
- graceful termination experiment;
- immutable image digest a template-generation correlation.

## 27. Pod observation matrix

| Boundary | Subject | Kľúčové observations |
|---|---|---|
| API/template | owner UID/generation, Pod UID | admitted spec, template hash, managed fields |
| Scheduling | Pod UID, Node UID | nodeName, scheduling conditions/Events |
| Sandbox | Pod UID, sandbox ID | PodReadyToStartContainers podľa clusteru, CRI/CNI |
| Data/config | volume/source/process snapshot | mounts, checksum, loaded epoch |
| Containers | container ID/imageID | state, exit, restart, logs, cgroup evidence |
| Probes | probe generation/target | results, kubelet Events, listener/path |
| Readiness | Pod UID/conditions/gates | ContainersReady, Ready, gate owner |
| Service | EndpointSlice targetRef UID | selector, endpoint conditions, dataplane |
| Termination | Pod UID/deletion subject | grace, PreStop, signals, drain, cleanup |
| Business | operation ID | SLI, downstream audit, exactly-once invariant |

## 28. Referenčné príkazy

```bash
kubectl get pod <pod> -n <namespace> -o wide
kubectl get pod <pod> -n <namespace> -o yaml
kubectl describe pod <pod> -n <namespace>
kubectl logs <pod> -n <namespace> -c <container>
kubectl logs <pod> -n <namespace> -c <container> --previous
kubectl get events -A --sort-by=.metadata.creationTimestamp
kubectl get endpointslice -n <namespace> -o yaml
```

Príkazy poskytujú observations. Root cause vznikne až porovnaním subject identity, timeline a mechanizmu.

## 29. Referenčné pravidlá

- Pod je runtime envelope jednej workload repliky, nie stabilná service identity.
- Pod name bez UID nie je lifetime subject.
- Pod spec a process environment sú snapshoty; source object update nemusí zmeniť effective state.
- Sandbox, container process, readiness a Service eligibility sú odlišné transitions.
- Containers v Pode zdieľajú port space a localhost.
- `Running` neznamená `Ready`; `Ready` neznamená business-correct.
- Liveness má opravovať process failure, nie zosilňovať dependency outage.
- Readiness gate potrebuje UID-aware external controller.
- Container restart nie je Pod replacement.
- `emptyDir` prežije container restart, nie Pod UID replacement.
- PreStop sa vykonáva v rámci termination grace budgetu.
- Priamy alebo static Pod má iný recovery owner než Deployment-managed Pod.
- Manual debug zmena musí skončiť opravou authoritative template-u.

## 30. Kontrolné otázky

1. Aký lifecycle vytvára z Pod template-u business-ready endpoint?
2. Prečo je Pod UID dôležitejší než meno?
3. Ktoré resources containers v Pode zdieľajú a ktoré nie?
4. Ako sa líši source Secret, mounted value a process-loaded secret?
5. Prečo init container nie je automaticky bezpečné miesto pre databázovú migráciu?
6. Ako odlíšiš Running, ContainersReady, Ready a Service eligibility?
7. Prečo liveness závislá od shared databázy vytvára restart storm?
8. Ako sa líši container restart od Pod replacementu?
9. Čo sa môže stratiť pri replacement-e Pod UID?
10. Čo musí Pod recovery verdict overiť?

## Glossary impact

Relevantné pojmy: Pod runtime-envelope subject, admitted Pod snapshot, Pod UID generation, Pod sandbox transition, shared-port contract, projected-data subject, process-loaded configuration, init side-effect boundary, sidecar lifecycle contract, probe control signal, readiness-gate subject, EndpointSlice eligibility subject, container-restart subject, Pod replacement subject, termination-budget subject, direct-Pod recovery boundary, Pod observation matrix a Pod acceptance verdict.

## Oficiálna dokumentácia

- [Pods](https://kubernetes.io/docs/concepts/workloads/pods/)
- [Pod lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)
- [Pod conditions](https://kubernetes.io/docs/concepts/workloads/pods/pod-condition/)
- [Init containers](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/)
- [Sidecar containers](https://kubernetes.io/docs/concepts/workloads/pods/sidecar-containers/)
- [Ephemeral containers](https://kubernetes.io/docs/concepts/workloads/pods/ephemeral-containers/)
- [Container lifecycle hooks](https://kubernetes.io/docs/concepts/containers/container-lifecycle-hooks/)
- [Liveness, readiness and startup probes](https://kubernetes.io/docs/concepts/workloads/pods/probes/)
- [Configure a security context](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Worker node components](worker-node-components.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: ReplicaSet →](replicaset.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
