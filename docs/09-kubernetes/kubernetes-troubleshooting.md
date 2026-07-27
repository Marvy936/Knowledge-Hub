# Kubernetes troubleshooting

Kubernetes troubleshooting nie je postupné spustenie všetkých známych `kubectl` príkazov. Je to riadené zúženie incidentu od používateľského symptómu k presnému cluster, release, object, process, data alebo packet subjectu. Cieľom je získať diskriminačný dôkaz skôr, než remediation zničí evidence alebo rozšíri blast radius.

Táto záverečná kapitola používa jeden dominantný incident lifecycle:

```text
user alebo business symptom
→ scope, timeline a recent-change correlation
→ exact cluster/release/object/process/data/flow subject
→ volatile evidence preservation
→ expected control-plane a data-plane path
→ competing causal hypotheses
→ najlacnejší diskriminačný observation point
→ containment
→ authoritative repair, reconciliation, replacement alebo recovery
→ original aj forbidden outcome verification
→ adjacent-cohort a recurrence checks
→ earlier control a incident closure
```

## 1. Symptom musí byť falsifikovateľný

Nedostatočný opis:

```text
Kubernetes nefunguje.
```

Použiteľný incident statement:

```text
Od 14:05 UTC približne 20 % payment requests vracia 502.
Zlyhania vznikajú iba na Pods umiestnených na Node pool-e np-136-v1.
Control plane, Deployment availability a readiness sú green.
Posledná zmena bol Kubernetes/Node-pool upgrade.
Retries môžu vytvoriť duplicate authorization risk.
```

Dobrý statement obsahuje:

- pôvodný používateľský alebo business outcome;
- začiatok a časovú zónu;
- affected a unaffected cohort;
- permanentnosť alebo intermittency;
- posledné zmeny;
- čo stále funguje;
- data, security a retry riziko;
- akceptačný cieľ recovery.

## 2. Incident subject pred príkazom

Pred diagnostikou fixuj identities, ktoré sa nesmú počas vyšetrovania potichu meniť:

```text
cluster/context/API endpoint a operator identity
incident a upgrade/deployment operation ID
release, image digest a workload revision
object kind/namespace/name/UID/generation
Pod UID, container ID, restart a process-loaded config generation
Node UID, host image, runtime a add-on generation
Service UID, EndpointSlice cohort a backend Pod UIDs
PVC/PV/backend/data/fencing identity
request/trace/payment ID
timestamp a telemetry coverage generation
```

Názov `payments-api-abc` bez UID neodlišuje starý a nový Pod. Tag `latest` neodlišuje artifact. PVC `Bound` neodlišuje správnu data generation.

## 3. Preserve-first boundary

Pred restartom, delete, rollbackom, drainom alebo force-detach zachovaj podľa incidentu:

- object spec/status/conditions/managed fields a owner graph;
- Events a audit records;
- current aj previous container logs;
- runtime/container ID a Node-local logs;
- controller, scheduler, kubelet, CNI, CSI a admission evidence;
- cgroup/OOM/pressure a packet/conntrack state;
- Service/EndpointSlice a flow tuples;
- mount, attachment, data a writer identities;
- exact recent changes, images, configs a certificates;
- external provider operation/audit state;
- metrics/traces a absent-evidence stav.

`kubectl delete pod`, Node reboot, collector restart alebo `etcd restore` môžu odstrániť jediný causal dôkaz.

## 4. Control path a data path

Každý incident mapuj na očakávaný mechanizmus.

### Control path

```text
client intent
→ API endpoint/authentication/authorization/admission
→ persisted object generation
→ controller reconciliation
→ scheduler binding
→ kubelet/runtime/CNI/CSI execution
→ status, readiness a EndpointSlice update
```

### Request/data path

```text
client DNS/TLS/edge
→ Gateway/Ingress/LB
→ Service a per-Node dataplane
→ EndpointSlice backend
→ Pod socket/process/config/resources
→ dependency/storage/data
→ response/reverse path
→ business commit
```

Ak Pod object neexistuje, scheduler a kubelet ešte nie sú relevantné. Ak direct Pod IP funguje, ale ClusterIP nie, application process pravdepodobne nie je prvá failure boundary.

## 5. Observation matrix

Vyber observation point, ktorý najlepšie rozdelí hypotézy:

| Boundary | Dôkaz | Čo oddeľuje |
|---|---|---|
| API request | status code, audit, admission | auth/RBAC/policy/quota vs. persistence |
| Object/controller | generation, conditions, owner graph | stale intent vs. reconcile failure |
| Scheduler | PodScheduled, Events, feasible set | absent capacity/constraint vs. Node execution |
| Kubelet/runtime | sandbox, image, mount, container state | Node/runtime/CNI/CSI vs. process |
| Process/config | PID, loaded config, logs, cgroup | runtime contract vs. application |
| Service path | EndpointSlices, translation, packet | selector/readiness/dataplane |
| Storage | PVC/PV/attachment/mount/data ID | provisioning/attach/mount/data correctness |
| Business | trace, idempotency, commit ledger | technical green vs. user outcome |

Najlepší test eliminuje viac hypotéz pri minimálnom riziku. Najhlasnejší log nemusí byť root cause.

## 6. Cohort differential diagnosis

Intermittent incidenty často vznikajú iba v jednej generácii alebo failure domain-e. Rozdeľ výsledky podľa:

- old/new release;
- old/new Node image alebo Kubernetes generation;
- zone, Node alebo runtime;
- Pod template/config/secret generation;
- Service endpoint a edge instance;
- storage backend alebo data generation;
- authenticated identity;
- request type alebo tenant;
- telemetry-covered a blind cohort.

Porovnanie jedného úspešného a jedného zlyhávajúceho subjectu je často silnejšie než cluster-wide dump.

## 7. Causal walkthrough: green cluster, intermittent payment failures

### Incident

Po upgrade-e na target Node pool `np-136-v1` približne 20 % payment requests končí `502`. Deployment má desired a available replicas, Pods sú `Running/Ready` a control plane je green. Zlyhania sa objavujú iba pri backendoch na target Nodes. Central logs z týchto Nodes chýbajú, ale `kubectl logs` funguje.

### Exact subject

Fixuj:

- payment/request/trace ID a presný timestamp;
- cluster a upgrade operation;
- release/image digest a Deployment/ReplicaSet generation;
- selected EndpointSlice a backend Pod UID;
- Pod sandbox, IP, container ID a loaded config;
- source/destination Node UID a Node-image/runtime generation;
- CNI/Service-dataplane revision a config;
- pre/post-NAT flow tuple, route, policy a conntrack state;
- collector generation, local log source a query tenant.

### Competing hypotheses

1. edge alebo Gateway instance má stale route;
2. Service selector obsahuje nesprávny backend;
3. readiness je plytká a target Pods nie sú funkčné;
4. target cohort používa inú config/secret epoch;
5. CPU throttling alebo OOM vytvára timeout;
6. DNS/application cache smeruje na stale endpoint;
7. NetworkPolicy blokuje flow iba na target Nodes;
8. CNI route/tunnel/MTU alebo host firewall je partial;
9. Service dataplane/conntrack má stale generation;
10. databáza alebo storage zlyháva iba z target cohorty;
11. collector blind spot skrýva application alebo CNI evidence;
12. retries zosilňujú downstream failure a menia symptóm.

### Discriminating observation order

1. Zachyť jeden zlyhaný request a backend Pod UID.
2. Porovnaj úspešný old-Node a zlyhaný target-Node Pod s rovnakým image/configom.
3. Over EndpointSlice cohort, conditions a targetRef UID.
4. Testuj local process socket, direct Pod IP, ClusterIP a edge path oddelene.
5. Porovnaj same-Node a cross-Node flow.
6. Sleduj packet pred Service translationom, po translatione a na destination Node-e.
7. Porovnaj CNI config, host routes/tunnels, MTU, policy a dataplane state old/new Nodes.
8. Čítaj Node-local application/CNI logs cez runtime, aj keď central pipeline je slepá.
9. Over cgroup, config/secret epoch a downstream connection audit.

Finding:

```text
Node image np-136-v1 neobsahuje expected host-networking prerequisite
→ CNI agent process a shallow health endpoint sú green
→ host dataplane initialization je partial
→ direct/same-Node test môže uspieť
→ cross-Node a Service-translated traffic intermittentne zlyháva
→ application retries zvyšujú 502 a DB pressure

zároveň collector sleduje iba legacy runtime log path
→ central evidence z target cohorty chýba
→ diagnóza sa oneskorí, ale nejde o payment root cause
```

Root cause a evidence-control failure sú dva rozdielne subjects. Oprava collector pipeline sama neopraví packet path.

### Containment

- pozastav Node-pool a workload rollout;
- cordon target cohortu a bezpečne ju vyber z serving pathu;
- drain vykonaj iba po PDB, storage a stateful/fencing kontrole;
- zachovaj Nodes, Pods, runtime logs, routes/maps/rules a packet captures;
- obmedz client/application retries a chráň idempotency;
- nevypínaj NetworkPolicy, host firewall ani TLS validation plošne;
- nepatchuj každý Node ručne bez versionovaného replacement planu.

### Authoritative recovery

- oprav versionovaný Node image a host-networking prerequisite;
- vytvor novú Node generation `np-136-v2`;
- spusti CNI, Service, DNS, policy, storage a telemetry capability canary;
- nasuň bounded Payments canary;
- over old/new cohort differential a external journey;
- rolloutni po failure domains;
- oprav collector path/config a coverage SLO;
- retire-ni chybnú aj starú Node generation a ich credentials.

### Verify original a forbidden outcomes

Over:

1. rovnaký payment request class funguje na každom target Node-e;
2. payment commit vznikne exactly once;
3. direct, ClusterIP, DNS a Gateway paths fungujú;
4. same-Node aj cross-Node flows fungujú;
5. forbidden NetworkPolicy flows zostávajú blokované;
6. EndpointSlice neobsahuje stale alebo chybnú cohortu;
7. CPU, config, storage a downstream state sú správne;
8. central aj node-local telemetry pokrýva target cohortu;
9. replacement a druhý reconciliation cycle nezmenia verdict;
10. retry/duplicate rate a business SLO sa vrátia do normálu.

### Earlier controls

Použi immutable Node conformance, per-generation packet-path a telemetry canary, cohort-aware dashboards, upgrade abort gate, expected-source coverage SLO, request idempotency, packet-flow observability a pravidelný Node replacement game day.

## 8. Symptom-to-boundary patterns

### Pod object nevznikol

Sleduj controller create request, admission, quota, Pod Security, webhook a API error. Scheduler nie je relevantný, kým Pod neexistuje.

### Pod je `Pending`

Rozlišuj `PodScheduled=False`, PVC binding, hard constraints, requests/capacity, taints/topology a scheduler profile. Live Node utilization nie je scheduler reservation.

### Pod je `ContainerCreating`

Sleduj sandbox/CNI, image pull/unpack, projected config, volume attach/mount a Node runtime. Application liveness ešte nie je vstup.

### Pod je `Running`, ale nie `Ready`

Over exact probe generation, sidecars, readiness gates, loaded config a EndpointSlice propagation. `Running` neznamená traffic eligibility.

### Pod je `Ready`, ale business zlyháva

Readiness môže byť plytká alebo testovať inú request class. Over actual dependency, data, identity, configuration, traffic a transaction outcome.

### `CrashLoopBackOff`

Fixuj container ID/restart generation, `lastState`, previous logs, exit signal, OOM/cgroup, startup/liveness a config. Delete Podu iba reprodukuje chybný contract.

### Object ostáva `Terminating`

Over deletionTimestamp, finalizers, owner/controller, external cleanup, kubelet/Node a storage detach. Odstránenie finalizeru bez cleanup verdictu môže orphanovať resource.

## 9. API, controller a etcd boundaries

HTTP/API verdict orientuje ďalší krok:

- `401` — credential/authentication;
- `403` — effective authorization graph;
- `409` — optimistic concurrency/field ownership;
- `422` — schema/validation alebo semantic request;
- timeout pred persistence — admission, API alebo etcd write path;
- successful request s absent outcome — controller/reconciliation/external operation.

Ak API reads fungujú, ale writes timeoutujú, existujúce workloads môžu maskovať degraded management plane. Over per-endpoint readiness, admission latency, etcd quorum/fsync/commit a controller queues. Etcd restore nie je prvý troubleshooting krok, ak quorum alebo repair cesta stále existuje.

## 10. Service, DNS a edge boundary

Použi exact chain:

```text
client resolver/cache
→ DNS answer a address generation
→ edge/LB/Gateway route a certificate
→ Service UID/ports
→ full EndpointSlice cohort
→ per-Node Service dataplane
→ backend Pod socket
→ application response a reverse path
```

Direct Pod IP success nepreukazuje Service dataplane. DNS success nepreukazuje ready backend. Edge `503` môže vzniknúť pred Service alebo v backende; identifikuj response producer a selected route/backend.

## 11. Storage a stateful boundary

Sleduj:

```text
logical data identity
→ PVC UID
→ PV UID a volumeHandle
→ backend asset/topology
→ VolumeAttachment a Node
→ stage/publish/mount
→ filesystem a application data generation
→ writer/fencing epoch
```

PVC `Bound` nepreukazuje správne dáta. Pri Multi-Attach po Node partition nepoužívaj force-detach, kým starý writer nie je hard-fenced a application membership overené.

## 12. Resources, probes a autoscaling boundary

Rozlišuj:

```text
source resource intent
→ admitted requests/limits
→ scheduler reservation
→ cgroup runtime enforcement
→ usage/throttling/OOM/pressure
→ probe verdict
→ HPA recommendation
→ serving capacity
```

`kubectl top` je current sample, nie historický OOM alebo throttling dôkaz. HPA môže správne zvýšiť desired replicas, ale quota, scheduling, readiness alebo downstream capacity môžu zabrániť business scale-upu.

## 13. Security a identity boundary

Pri access alebo permission incidente fixuj:

- credential generation a authenticated subject/groups;
- exact verb/group/resource/subresource/namespace;
- všetky bindings a aggregated rules;
- admission a runtime consequences;
- external credential alebo secret už získaný pred revokáciou.

Nepridávaj `cluster-admin`, privileged Pod, hostNetwork alebo široký hostPath ako diagnostický shortcut. Debug capability musí mať ownera, scope, audit a expiry.

## 14. Unknown operation outcome

Timeout neznamená, že mutation neprebehla. Pri controller/cloud/storage/identity operácii:

```text
operation request s idempotency/owner key
→ external side effect
→ response sa stratí
→ Kubernetes status ostane stale
```

Pred retry najprv read-back-ni authoritative external state podľa stable owner/operation identity. Blind retry môže vytvoriť duplicate load balancer, disk, certificate alebo payment.

## 15. Controlled reproduction

Najmenší bezpečný test zachová relevantné boundaries:

- rovnaký namespace, ServiceAccount a policies;
- rovnaký Node/failure-domain alebo target cohort;
- server-side dry-run pre admission;
- direct Pod vs. Service vs. edge test;
- read-only data verification;
- approved ephemeral debug container;
- isolated restore alebo upgrade lab.

Test nesmie vytvoriť nevratné business side effects. Použi synthetic IDs, idempotency keys alebo read-only request class.

## 16. Remediation decision

Vyber podľa authoritative state:

1. **Reconcile deklaratívny drift**, ak desired state je správny a controller vstup chýba.
2. **Roll-forward**, ak nová immutable generation môže bezpečne opraviť image/config/Node/add-on.
3. **Rollback**, iba ak stará generácia je compatible s current API/data/external state-om.
4. **Replace Pod/Node**, ak lifecycle je disposable a state/fencing je overený.
5. **Repair external dependency**, ak Kubernetes state je správny, ale provider asset je chybný.
6. **Compensate**, ak side effect už prebehol a nemožno ho jednoducho vrátiť.
7. **Restore**, iba pri strate authoritative state-u a s complete recovery setom.

Restart je experiment iba vtedy, keď má explicitnú hypotézu, scope a následné recurrence overenie.

## 17. Verification a incident closure

Technická remediation nie je closure. Over:

```text
original user/business outcome
exact accepted artifact/config/data/identity generations
allowed aj forbidden network/security operations
replacement/restart/failover behavior
adjacent Nodes/zones/releases/tenants
second reconciliation alebo retry no-op
telemetry coverage a alert recovery
old broken/stale generations retired
follow-up control s ownerom a termínom
```

Incident timeline musí oddeľovať fakt, hypotézu, test a zmenu:

```text
14:07 — request P-884 skončil 502 na Pod UID X, Node UID N7 (fakt)
14:09 — target Node dataplane je kandidát (hypotéza)
14:12 — packet vstúpil na source Node, nedorazil do tunnel peeru (dôkaz)
14:25 — target cohort odstránená z trafficu (containment)
15:10 — np-136-v2 canary prešiel packet/business testom (recovery evidence)
```

## 18. Referenčná failure-domain mapa

```text
context/identity
API/auth/RBAC/admission
etcd/persistence/watch
controller/owner/finalizer
scheduler/capacity/topology
kubelet/runtime/cgroups
CNI/Service/DNS/Gateway
CSI/storage/data/fencing
config/secret/process-loaded state
application/dependency/business transaction
telemetry/evidence pipeline
external provider resources
```

Mapa sumarizuje mechanizmy z celej sekcie. Nie je povinným poradím príkazov.

## 19. Anti-patterny

- restart alebo delete pred evidence preservation;
- meniť viac vrstiev naraz;
- dashboard považovaný za authoritative runtime state;
- Pod name, mutable tag alebo PVC name považované za úplnú identity;
- `nodeName`, hostNetwork alebo privileged mode ako rýchla oprava;
- vypnutie NetworkPolicy, Pod Security alebo TLS verification plošne;
- `chmod 777` bez identity/LSM analýzy;
- force delete alebo force detach stateful subjectu bez fencing;
- `cluster-admin` pre `Forbidden`;
- etcd restore pri bežnom application/add-on incidente;
- green readiness považovaná za business acceptance;
- absent logs považované za absent failure;
- retry po unknown outcome bez read-backu;
- incident uzavretý bez forbidden a adjacent-cohort testu.

## 20. Praktický incident record

```text
symptom a business impact
scope/cohorts/timeline
recent change inventory
exact subject identities
expected control/data path
competing hypotheses
observation/test/result log
preserved evidence locations
containment a approver
root cause a contributing control failures
authoritative recovery
original/forbidden/adjacent verification
RTO/RPO/data-loss/duplicate outcome
follow-up control, owner a deadline
```

## 21. Kontrolné otázky

1. Ako preložíš používateľský symptóm na exact Kubernetes subjects?
2. Ktoré evidence musíš zachovať pred Pod/Node restartom?
3. Ako control path odlíšiš od request/data pathu?
4. Prečo cohort comparison často zrýchli intermittent incident?
5. Ktorý test odlíši application failure od Service dataplane failure?
6. Ako rozlíšiš root cause od telemetry blind spotu?
7. Kedy je scheduler irelevantný pre chýbajúci Pod?
8. Prečo timeout external operácie neznamená, že side effect nevznikol?
9. Kedy je replacement bezpečný a kedy potrebuje fencing?
10. Ktoré dôkazy tvoria subject-bound incident closure?

## Glossary impact

Relevantné pojmy: Kubernetes incident subject, symptom-to-subject translation, control/data-path map, cohort differential diagnosis, discriminating observation boundary, volatile evidence envelope, telemetry blind-spot subject, containment generation, unknown-operation outcome, authoritative remediation subject, original-outcome verification, forbidden-outcome verification, adjacent-cohort verification, second-reconciliation verdict a subject-bound incident closure.

## Oficiálna dokumentácia

- [Monitoring, logging and debugging](https://kubernetes.io/docs/tasks/debug/)
- [Troubleshooting clusters](https://kubernetes.io/docs/tasks/debug/debug-cluster/)
- [Debug running Pods](https://kubernetes.io/docs/tasks/debug/debug-application/debug-running-pod/)
- [Debug Services](https://kubernetes.io/docs/tasks/debug/debug-application/debug-service/)
- [Troubleshooting kubeadm](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/troubleshooting-kubeadm/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Logging, metrics a events](logging-metrics-events.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Helm chart, template, values a release →](../10-helm-and-cka/helm-chart-template-values-release.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
