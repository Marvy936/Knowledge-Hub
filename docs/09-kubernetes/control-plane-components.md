# Control plane components

Kubernetes control plane prijíma API requests, uchováva cluster state, plánuje Pods a spúšťa controllers, ktoré implementujú Kubernetes API behavior. Jednotlivé komponenty majú oddelené responsibilities a failure modes. Pri diagnostike nestačí povedať „control plane nefunguje“; treba určiť, či zlyháva API serving, persistence, scheduling, reconciliation, cloud integration alebo supporting identity/network vrstva.

## 1. Hlavné komponenty

Core control plane tvorí najmä:

- `kube-apiserver`,
- `etcd`,
- `kube-scheduler`,
- `kube-controller-manager`,
- voliteľný `cloud-controller-manager`.

Súvisiace, ale samostatné vrstvy môžu zahŕňať:

- API load balancer,
- admission webhooks,
- aggregated API servers,
- DNS, metrics a policy add-ons,
- certificate authority a bootstrap tooling.

## 2. `kube-apiserver`

API server je front-end Kubernetes control plane-u.

Zodpovednosti:

- poskytuje Kubernetes HTTP API,
- API discovery,
- authentication,
- authorization,
- admission control,
- schema validation a defaulting,
- API version conversion,
- persistence cez etcd,
- list/watch streams,
- audit events podľa konfigurácie,
- proxy/streaming subresources pre niektoré operácie.

Ostatné components komunikujú so cluster state-om prevažne cez API server.

## 3. API request pipeline

Zjednodušený write request:

```text
TLS connection
→ authentication
→ authorization
→ mutating admission
→ schema/defaulting/conversion
→ validating admission
→ persistence
→ response
```

Presné interné poradie niektorých krokov závisí od operation a API implementation, ale diagnosticky treba rozlišovať:

- request sa k API serveru nedostal,
- identita sa neoverila,
- RBAC request zakázal,
- admission request odmietla alebo timeoutovala,
- schema bola neplatná,
- etcd write zlyhal.

## 4. Authentication

Authentication odpovedá:

```text
Kto posiela request?
```

Možné identity mechanisms podľa cluster konfigurácie:

- client certificates,
- bearer tokens,
- service account tokens,
- OIDC integration,
- authentication proxy,
- bootstrap tokens,
- webhook token authentication.

Výsledkom je user identity, groups a extra attributes.

Authentication sama neurčuje, čo identita môže robiť.

## 5. Authorization

Authorization odpovedá:

```text
Môže táto identita vykonať verb nad týmto resource/subresource v tomto scope?
```

Bežný model je RBAC, ale API server môže podporovať viac authorization modes.

Diagnostika:

```bash
kubectl auth can-i get pods -n production
kubectl auth can-i create pods/exec -n production
kubectl auth can-i --list -n production
```

`pods` a `pods/exec` sú odlišné authorization targets.

## 6. Admission control

Admission sa vykonáva po authentication a authorization pri relevantných create/update/delete requests.

### Mutating admission

Môže object doplniť alebo zmeniť.

Príklady use cases:

- defaults,
- sidecar injection,
- labels/annotations,
- security fields,
- image rewrite.

### Validating admission

Môže request povoliť alebo odmietnuť.

Príklady:

- security policy,
- naming rules,
- approved registries,
- resource requirements,
- tenancy constraints.

Admission webhook je synchronous dependency API write pathu. Jeho latency a availability priamo ovplyvňujú cluster operations.

## 7. API server availability

HA API layer typicky používa:

- viac API server instances,
- stable virtual endpoint alebo load balancer,
- health/readiness checks,
- spoločný alebo konzistentne nakonfigurovaný etcd backend,
- rovnaké trust roots a admission configuration,
- controlled version-skew počas upgrade.

API servers môžu aktívne obsluhovať requests súčasne. Load balancer musí odstrániť unhealthy instances bez skrytia systémového incidentu.

## 8. API server health endpoints

Podľa oprávnení a deploymentu sú relevantné endpoints:

- `/livez`,
- `/readyz`,
- `/healthz` pre compatibility,
- verbose variants.

Príklad:

```bash
kubectl get --raw='/readyz?verbose'
```

Readiness môže zlyhať napríklad pri probléme s etcd, informer sync alebo post-start hookom.

Nezamieňaj load balancer TCP success s plnou API readiness.

## 9. etcd

`etcd` uchováva authoritative Kubernetes API state.

Vlastnosti relevantné pre Kubernetes:

- konzistentný distributed key-value model,
- quorum-based writes,
- watch support,
- revision history,
- snapshots,
- leader election v etcd clusteri,
- citlivosť na disk latency a network partitions.

API server je jediný core component, ktorý má štandardne priamu väzbu na etcd data store.

## 10. etcd quorum

Pri clusteri s nepárnym počtom voting members je potrebná väčšina.

Príklady:

```text
3 members → quorum 2
5 members → quorum 3
```

Strata quorum znamená, že bezpečné writes nemôžu pokračovať. Samotné spustené workloads môžu dočasne bežať ďalej, ale control plane nedokáže spoľahlivo meniť desired state.

Viac etcd members nie je vždy lepšie; zvyšuje write coordination a operational complexity.

## 11. etcd storage a performance

Kritické faktory:

- stabilná nízka disk latency,
- dostatok disk capacity,
- dostatok IOPS,
- nízka network latency medzi members,
- compaction a defragmentation workflow,
- monitoring database size,
- backup a restore testy,
- oddelenie od noisy workloads.

Pomalé etcd sa môže prejaviť ako pomalé alebo timeoutujúce API requests, controller lag a leader instability.

## 12. etcd security

Chráň:

- peer a client TLS,
- member endpoints,
- snapshot files,
- filesystem permissions,
- backup storage,
- encryption keys,
- network access,
- restore procedure.

Kubernetes Secret uložený v etcd nie je automaticky bezpečne zašifrovaný iba preto, že API používa TLS. Encryption at rest je samostatná API server configuration.

## 13. etcd backup a restore hranica

Snapshot musí byť:

- pravidelný,
- šifrovaný,
- off-host/off-failure-domain,
- versionovo a procedurálne kompatibilný,
- testovaný reálnou obnovou,
- doplnený o certificates a cluster bootstrap informácie podľa platformy.

Restore mení cluster identity/state continuity. Nie je to bežná application-level rollback operácia.

## 14. `kube-scheduler`

Scheduler sleduje Pods, ktoré ešte nemajú pridelený Node.

Zjednodušený flow:

1. získa unscheduled Pod,
2. identifikuje feasible Nodes,
3. filtruje podľa hard constraints,
4. skóruje kandidátov,
5. vyberie Node,
6. zapíše binding/assignment cez API.

Scheduler nevytvára container a nečaká na jeho readiness.

## 15. Scheduling inputs

Scheduler posudzuje podľa pluginov a konfigurácie napríklad:

- resource requests vs. allocatable capacity,
- node selectors,
- node affinity,
- taints a tolerations,
- Pod affinity/anti-affinity,
- topology spread,
- volume topology a binding,
- host ports,
- preemption a priority,
- extension/plugin-specific constraints.

Aktuálne utilization metrics nemusia byť základom default scheduling decisionu; kľúčové sú deklarované requests a constraints.

## 16. Scheduling framework

Moderný scheduler používa plugin-oriented framework s extension points pre:

- queueing,
- pre-filter/filter,
- scoring,
- reserve/permit,
- pre-bind/bind/post-bind,
- preemption-related processing.

Custom scheduler behavior musí byť testované proti upgrade a fairness/capacity požiadavkám.

## 17. Scheduler HA

Viac scheduler instances môže používať leader election. Aktívny leader vykonáva scheduling pre daný scheduler name.

Multiple schedulers sú možné, ak Pods explicitne používajú správny `schedulerName`.

Riziká:

- Pod odkazuje na neexistujúci scheduler,
- custom scheduler nemá permissions,
- leader election zlyháva,
- queue je preťažená,
- scheduler profiles sa líšia medzi replicas.

## 18. Scheduler diagnostika

Pod bez node assignmentu:

```bash
kubectl describe pod <pod>
kubectl get events --field-selector involvedObject.name=<pod>
kubectl get nodes
kubectl describe node <node>
```

Hľadaj:

- `FailedScheduling`,
- insufficient CPU/memory,
- untolerated taint,
- affinity conflict,
- unbound PVC,
- host port collision,
- topology constraint,
- scheduler unavailable.

## 19. `kube-controller-manager`

Controller manager spúšťa sadu built-in controllers v jednom process-e alebo deployment unit-e.

Príklady:

- Node controller,
- Job controller,
- Deployment/ReplicaSet-related controllers,
- EndpointSlice controller,
- Namespace controller,
- ServiceAccount controller,
- garbage collector,
- attach/detach controller podľa architektúry,
- certificate controllers.

Každý controller sleduje konkrétne resources a približuje state požadovanému výsledku.

## 20. Controller manager HA

Viac replicas typicky používa leader election cez Lease.

Standby replicas:

- udržujú process dostupný,
- neznamenajú viacnásobnú throughput škálu všetkých loops,
- musia mať rovnakú configuration a permissions,
- potrebujú sledovať leader transitions a queue recovery.

Leader loss môže dočasne spomaliť reconciliation, ale nemá meniť desired state.

## 21. Controller work queues

Controllers používajú watch/cache/work queue patterns.

Dôležité metriky:

- queue depth,
- queue latency,
- work duration,
- retries,
- API errors,
- client throttling,
- generation lag.

Ak API funguje, ale objects sa dlhodobo nereconcile-ujú, problém môže byť v konkrétnom controlleri alebo jeho queue.

## 22. `cloud-controller-manager`

Cloud controller manager oddeľuje cloud-provider-specific control loops od core Kubernetes components.

Môže spravovať podľa providera:

- Node cloud identity/lifecycle,
- routes,
- Service load balancers,
- cloud-specific metadata.

Nie každý cluster ho používa. On-prem alebo iné platformy môžu mať odlišné integrations.

Cloud provider API outage môže blokovať LoadBalancer Services alebo Node initialization, hoci core API server je healthy.

## 23. Aggregated API servers

API aggregation umožňuje pridať ďalšie API groups cez `APIService` resources.

Použitie:

- metrics APIs,
- custom platform APIs,
- extension servers.

Failure aggregated API môže:

- spomaliť discovery,
- vracať unavailable API group,
- ovplyvniť clients, ktoré očakávajú daný resource.

Odlišuj CRD od aggregated API:

- CRD používa core API server storage/schema model,
- aggregated API má vlastný API server backend.

## 24. Admission webhooks ako control-plane dependency

Webhook configuration môže mať:

- broad resource matching,
- krátky alebo dlhý timeout,
- fail-open alebo fail-closed behavior,
- external DNS/network dependency,
- TLS trust dependency,
- side effects.

Produkčné zásady:

- vysoká dostupnosť,
- úzky match scope,
- nízka latency,
- žiadne dlhé remote calls,
- správne timeouty,
- observability,
- break-glass postup,
- kompatibilita počas cluster upgrade.

## 25. Certificates a time

Control plane závisí od:

- CA trust,
- server certificates,
- client certificates,
- service account signing keys,
- webhook certificates,
- etcd certificates,
- presného času.

Symptómy expiry alebo clock skew:

- TLS handshake errors,
- unauthorized requests,
- webhook failures,
- component communication failure,
- leader-election instability.

Certificate inventory a rotation musia byť súčasťou lifecycle managementu.

## 26. Static Pod deployment model

Kubeadm-like self-managed clusters často spúšťajú control plane components ako static Pods.

Charakteristiky:

- local manifest na control plane node-e,
- kubelet spravuje process lifecycle,
- mirror Pod je viditeľný v API,
- zmena sa vykonáva v local static Pod manifeste,
- container logs a host manifests sú kritické pri API outage.

Keď API server nefunguje, `kubectl logs` nemusí byť dostupné. Potrebuješ node-level runtime a filesystem access.

## 27. External control plane deployment

Iné distribúcie môžu používať:

- systemd services,
- dedicated VMs,
- managed provider control plane,
- containers mimo Kubernetes API ownershipu,
- stacked alebo external etcd.

Diagnostický postup sa musí prispôsobiť packagingu. Názov komponentu je rovnaký, ale log path, restart mechanism a health model sa líšia.

## 28. Stacked vs. external etcd

### Stacked etcd

etcd member beží na rovnakých control plane nodes ako ostatné components.

Výhody:

- jednoduchšia topológia,
- menej hostov.

Riziká:

- zdieľaný failure domain,
- resource contention,
- control plane node incident ovplyvní aj etcd membera.

### External etcd

etcd beží na samostatných hosts.

Výhody:

- oddelený failure/resource domain,
- samostatný lifecycle.

Riziká:

- viac systems na správu,
- network latency a security,
- zložitejší bootstrap/restore.

## 29. Upgrade sequencing

Control plane upgrade musí rešpektovať:

- supported version-skew policy,
- API deprecations,
- etcd compatibility,
- admission/webhook compatibility,
- CRD conversion,
- scheduler/controller configuration,
- certificates,
- rollback limitations.

Pred upgrade:

- zálohuj a over restore,
- skenuj deprecated APIs,
- over add-ons a webhooks,
- skontroluj capacity a HA,
- definuj validation a abort criteria.

## 30. Observability

### API server

Sleduj:

- request rate a latency,
- response codes,
- inflight requests,
- authentication/authorization failures,
- admission latency/rejections,
- watch count,
- audit pipeline,
- etcd request latency.

### etcd

Sleduj:

- leader changes,
- peer health,
- proposal failures,
- fsync/commit latency,
- database size,
- quota alarms,
- compaction/defragmentation,
- snapshot freshness.

### Scheduler

Sleduj:

- pending queue,
- scheduling attempts,
- scheduling latency,
- unschedulable Pods,
- plugin latency,
- preemption.

### Controller manager

Sleduj:

- leader status,
- work queues,
- reconcile errors,
- client rate limiting,
- controller-specific metrics.

## 31. Failure scenáre

### API server down, etcd healthy

State existuje, ale clients/controllers ho nemôžu používať cez API. Bežiace Pods môžu pokračovať, no management a nové reconciliation sú obmedzené.

### API server healthy, etcd pomalé

Requests majú vysokú latency alebo timeouty, watchers sa odpájajú a controllers zaostávajú.

### Scheduler down

Existujúce Pods bežia, ale nové unscheduled Pods ostávajú `Pending`.

### Controller manager down

API writes fungujú, ale higher-level resources nemusia vytvárať alebo opravovať dependents.

### Admission webhook down fail-closed

Relevantné create/update requests zlyhajú, hoci core API server a etcd sú healthy.

### Cloud controller down

Cloud load balancers, routes alebo Node cloud initialization môžu zaostávať.

## 32. Anti-patterny

### Všetky control plane components na jednom unrecoverable hoste

Vytvára single failure domain.

### etcd na pomalom zdieľanom disku

Disk latency destabilizuje celý control plane.

### Admission webhook volá pomalé externé API

Každý matching API write zdedí túto latency a availability.

### Direct writes do etcd mimo API servera

Obídu validation, conversion, admission a object invariants.

### Monitoring iba `kubectl get nodes`

Nevie odhaliť etcd latency, API saturation, scheduler queue ani admission failure.

### Restart všetkých control plane components naraz

Zničí dostupnosť a evidence; zmeny vykonávaj postupne podľa topológie.

## 33. Troubleshooting checklist

```text
[ ] API endpoint DNS/TCP/TLS
[ ] /readyz verbose
[ ] authentication a authorization
[ ] admission rejections/timeouts
[ ] API server logs a latency metrics
[ ] etcd endpoint health a quorum
[ ] etcd disk capacity/latency
[ ] scheduler leader, logs a pending queue
[ ] controller-manager leader, queues a errors
[ ] cloud-controller state
[ ] certificate validity a clock
[ ] static Pod manifests/runtime state
[ ] posledná config alebo upgrade zmena
```

## 34. Kontrolné otázky

1. Aké responsibilities má `kube-apiserver`?
2. Aký je rozdiel medzi authentication, authorization a admission?
3. Prečo je etcd disk latency kritická?
4. Čo znamená strata etcd quorum?
5. Aký je rozdiel medzi schedulerom a controller managerom?
6. Ako sa prejaví výpadok scheduleru?
7. Prečo admission webhook patrí do control-plane availability modelu?
8. Na čo slúži leader election pri scheduler/controller-manager replicas?
9. Ako sa líši CRD a aggregated API server?
10. Ako diagnostikuješ control plane v static Pod topológii pri nefunkčnom API?

## Glossary impact

Relevantné pojmy: API request pipeline, Kubernetes authentication, Kubernetes authorization, admission control, mutating admission, validating admission, API server readiness, etcd quorum, etcd snapshot, stacked etcd, external etcd, scheduler queue, scheduling framework, controller manager, cloud controller manager, API aggregation, APIService, admission webhook dependency, control plane certificate lifecycle a static control plane Pod.

## Oficiálna dokumentácia

- [Kubernetes components](https://kubernetes.io/docs/concepts/overview/components/)
- [`kube-apiserver`](https://kubernetes.io/docs/reference/command-line-tools-reference/kube-apiserver/)
- [`kube-scheduler`](https://kubernetes.io/docs/reference/command-line-tools-reference/kube-scheduler/)
- [`kube-controller-manager`](https://kubernetes.io/docs/reference/command-line-tools-reference/kube-controller-manager/)
- [Admission control](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/)
- [Scheduler configuration](https://kubernetes.io/docs/reference/scheduling/config/)
- [Operating etcd clusters for Kubernetes](https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/)
- [API aggregation layer](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/apiserver-aggregation/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Desired state a reconciliation loops](desired-state-reconciliation-loops.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Worker node components →](worker-node-components.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
