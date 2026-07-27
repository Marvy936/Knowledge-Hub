# ResourceQuota a LimitRange

ResourceQuota a LimitRange nie sú iba tabuľky limitov. Tvoria admission a governance chain medzi tenantovým SLO/cost modelom, defaultmi jednotlivých workloadov, agregovaným namespace budgetom, autoscalingom, schedulerom a skutočnou serving capacity. Policy môže správne odmietnuť nový Pod a zároveň spôsobiť produkčný incident, ak default alebo quota nezodpovedá recovery a rollout potrebám.

Táto kapitola používa jeden dominantný lifecycle:

```text
namespace owner, SLO, cost a fairness intent
→ versionovaný LimitRange a ResourceQuota contract
→ create/update request a source resource intent
→ LimitRange defaulting/validation
→ effective admitted resource delta
→ ResourceQuota accounting a allow/reject verdict
→ workload controller, scheduler a runtime realization
→ HPA/Job/PVC/object lifecycle feedback
→ quota usage, cleanup a policy reconciliation
→ business, recovery a cost verification
```

## 1. Atlas Payments governance subject

Namespace `payments-production` prevádzkuje API, settlement Jobs a retry-ledger PVC. Reviewed contract:

```text
namespace UID a owner: exact tenant subject
baseline replicas: 6
rollout surge: 2
HPA range: 6–20
per-Pod effective CPU request: 500m
per-Pod effective memory request: 768Mi
recovery reserve: minimálne 4 ďalšie Pods
PVC a Job count: bounded
high-priority workload: samostatná scoped quota
```

Quota musí umožniť bežnú prevádzku, rollout, Node replacement aj incident recovery. Ak je `used` tesne pod `hard`, namespace môže fungovať, ale nemá žiadny recovery headroom.

## 2. Tri odlišné policy subjects

Pri diagnostike oddeľuj:

```text
source workload resources
→ admitted effective object contract
→ namespace quota accounting delta
```

Source Deployment môže nemať limit, no LimitRange ho doplní. ResourceQuota potom účtuje admitted requests/limits, nie Git YAML ani live CPU usage.

Exact subject obsahuje:

- cluster, namespace UID a policy owner;
- ResourceQuota UID/generation, `spec.hard` a `status.used`;
- LimitRange UID/generation a všetky matching rules;
- workload object UID/generation a Pod template;
- admitted Pod resources pre application, sidecars a init containers;
- HPA/Job/StatefulSet desired count;
- rejected API request, requested delta a timestamp;
- finalizers/terminating objects ovplyvňujúce `used`;
- Node capacity a scheduler state ako samostatnú downstream boundary.

## 3. LimitRange: per-object admission contract

LimitRange môže pre podporované object types:

- doplniť `defaultRequest`;
- doplniť default limit;
- odmietnuť hodnotu pod `min` alebo nad `max`;
- obmedziť `maxLimitRequestRatio`;
- obmedziť PVC storage request.

Default je mutation na admission boundary. Nový Pod preto môže mať iné requests/limits než stará replika z rovnakého Deploymentu, ak sa policy medzi generáciami zmenila.

Dôsledky tichého defaultu:

```text
vyšší request
→ vyššie quota used
→ menší feasible-Node set
→ iný HPA denominator

nižší CPU limit
→ cgroup throttling
→ probe failures a latency
```

Policy musí mať ownera, versioning, rollout plan a admitted-object test.

## 4. ResourceQuota: agregovaný admission budget

ResourceQuota porovnáva current účtovaný stav a delta nového requestu s `hard` limitom. Môže obmedziť:

- CPU, memory, ephemeral storage a extended resources;
- počet Pods, Jobs, Secrets, ConfigMaps a ďalších API objects;
- PVC count a cumulative storage;
- LoadBalancer Services;
- selected PriorityClass alebo ďalšie scopes.

Quota je API admission control. Nie je:

- rezervovaná Node capacity;
- runtime cgroup limit pre celý namespace;
- application rate limiter;
- cloud-provider quota;
- retention alebo backup policy.

Zníženie `hard` pod current `used` neevictne existujúce workloads. Zablokuje budúce creates/updates, často práve replacement alebo recovery Pody.

## 5. Quota accounting a lifecycle

Admission request pre nový Pod sa účtuje podľa effective resources. Pri controller-managed workloade je chain:

```text
HPA alebo rollout zvýši desired replicas
→ Deployment/StatefulSet vytvorí Pod request
→ LimitRange defaulting/validation
→ quota delta calculation
→ Pod create allowed alebo rejected
→ scheduler až po úspešnom admission-e
```

`desired replicas=20` preto neznamená, že vzniklo 20 Podov. HPA môže byť funkčné, ale Deployment bude hlásiť `FailedCreate` pre quota.

Object-count quota musí zohľadniť cleanup. Finished Jobs, terminating resources, finalizers alebo retained PVCs môžu držať `used` aj po tom, čo operator považuje workflow za ukončený.

## 6. Capacity, fairness a recovery headroom

Quota chráni iné tenants, ale sama negarantuje tomuto namespace-u capacity. Reálna dostupnosť závisí od:

```text
quota allow verdict
+ cluster allocatable
+ placement/topology
+ priority/preemption
+ storage capacity
+ Node-autoscaler templates
```

Critical namespace potrebuje explicitný recovery envelope:

- baseline capacity;
- maximum rollout surge;
- HPA scale-up burst;
- Node-drain replacement;
- Job alebo migration overlap;
- emergency debug/repair workload;
- PVC snapshot/restore objects podľa platformy.

Quota nastavená presne na steady state je availability risk.

## 7. Scopes a PriorityClass governance

Scope alebo `scopeSelector` môže vytvoriť samostatný budget pre high-priority workloads. To však funguje iba spolu s:

- RBAC/admission kontrolou použitia PriorityClass;
- exact matching scope semantics;
- bounded high-priority object/resource budgetom;
- preemption auditom.

Ak tenant môže ľubovoľne označiť všetko ako high priority, scoped quota ani PriorityClass nevytvoria férovosť.

## 8. Storage a object governance

Storage quota môže rozlišovať StorageClass. Stále však nepreukazuje:

- že backend má voľnú capacity;
- že volume vznikne v správnej zone;
- IOPS alebo throughput;
- backup a restore;
- správnu application data identity.

Object-count quota chráni API server, etcd a controllers pred floodom. CronJob history, TTL a finalizer hygiene zostávajú samostatným lifecycle contractom.

## 9. Causal walkthrough: HPA chce škálovať, ale nové Pods nevznikajú

### Symptom

Payments latency rastie. HPA odporúča 18 replík, Deployment má 14. Events ukazujú `exceeded quota: requests.cpu`. Dashboard pritom uvádza quota `used=19.5`, `hard=20` CPU a source Deployment deklaruje 500m na hlavný container.

### Exact subject

Fixuj:

- HPA UID/generation, metric a desired replicas;
- Deployment/ReplicaSet generation a rejected Pod create request;
- ResourceQuota UID/generation, `hard` a `used` v rovnakom čase;
- LimitRange UID/generation;
- source a admitted resources každého containeru/init containeru;
- old/new Pod cohorty;
- terminating Pods, Jobs a finalizers;
- Node capacity oddelene od quota.

### Competing hypotheses

1. HPA max replicas je 14;
2. scheduler nemá CPU capacity;
3. Deployment controller nereaguje;
4. quota `used` je stale;
5. terminating Pods stále spotrebúvajú quota;
6. nový sidecar dostal default request;
7. init container zvýšil effective request;
8. iný workload alebo Job spotreboval namespace budget;
9. scope selector účtuje workload do nesprávnej quota;
10. Git manifest a admitted Pod sa líšia pre zmenu LimitRange.

### Discriminating observations

Porovnaj HPA conditions, Deployment `ReplicaFailure`, create Events, exact API error, ResourceQuota status, všetky active/terminating Pods a admitted resource specs old/new cohorty.

Finding:

```text
nový logging sidecar nemá explicitný request
→ LimitRange generation LR-12 doplní 500m
→ nový Payments Pod účtuje 1 CPU namiesto 500m
→ quota zostáva iba 500m headroom
→ Pod create je odmietnutý
→ HPA desired rastie, serving capacity nie
→ latency a retries rastú
```

Scheduler nebol observation boundary, pretože Pod objekt vôbec nevznikol.

### Containment

- pozastav ďalší rollout alebo batch launch, ktorý spotrebúva quota;
- neznižuj existujúce requests bez performance evidence;
- nemaž náhodné Pody, čím by si znížil serving capacity;
- zachovaj rejected request, policy generations a old/new admitted specs;
- obmedz retry amplification a chráň downstream.

### Authoritative recovery

- nastav explicitný tested request/limit pre sidecar;
- oprav alebo rozdeli LimitRange podľa workload class;
- zvýš quota iba ak existuje cluster a budget capacity;
- uvoľni stale Jobs/objects cez bezpečný lifecycle cleanup;
- zachovaj recovery headroom;
- rolloutni novú Pod generation a nechaj HPA znovu reconcile-ovať.

### Verify original a forbidden outcomes

Over:

1. HPA recommendation vedie k admitted Pod creates;
2. nové Pods sú Scheduled, Ready a serving;
3. per-Pod effective requests zodpovedajú reviewed contractu;
4. CPU throttling a memory behavior sú prijateľné;
5. quota má definovaný recovery headroom;
6. iný namespace nemôže spotrebovať tento namespace quota, ale cluster fairness zostáva zachovaná;
7. batch flood alebo object flood je stále blokovaný;
8. payment latency a duplicate rate sa vrátia do SLO.

### Earlier controls

Použi admission dry-run test, source-vs-admitted diff, quota capacity model pre baseline/surge/HPA/recovery, policy canary namespace, alert na `used/hard`, `FailedCreate` a object growth, explicitné sidecar resources a periodický Node-drain/HPA scale game day.

## 10. Ďalšie failure boundaries

### Manifest nemá limit, admitted Pod ho má

LimitRange alebo iný admission controller doplnil default. Zdroj pravdy pre runtime je admitted object.

### Quota `used` zostáva vysoké po cleanup-e

Hľadaj terminating objects, finalizers, retained Jobs/PVCs a quota-controller health. Neupravuj `status.used` ručne.

### HPA škáluje, ale Pods sú Pending

Quota boundary už prešla. Pokračuj scheduler/capacity/storage diagnostikou.

### Zníženie hard quota blokuje recovery

Existing workloads pokračujú, ale replacement sa nevytvorí. Pred policy zmenou simuluj Node loss, rollout a failover.

### PVC create je rejected

Rozlišuj cumulative `requests.storage`, PVC count a StorageClass-scoped quota. Quota success stále nepreukazuje provisioning.

### In-place resize je odmietnutý

Nová effective hodnota porušuje LimitRange alebo quota. Over update semantics a current admitted contract.

## 11. Referenčný katalóg

### ResourceQuota oblasti

- compute requests/limits;
- object counts;
- PVC/storage a StorageClass-scoped limits;
- Services a ďalšie API-specific quotas;
- scopes a scope selectors.

### LimitRange oblasti

- `defaultRequest` a default limit;
- `min` a `max`;
- `maxLimitRequestRatio`;
- Container, Pod a PVC rules podľa podporovaného API.

### Governance evidence

```text
policy UID/generation
source request
admitted effective object
delta charged to quota
hard/used verdict
controller create result
scheduler/runtime result
business/cost outcome
```

## 12. Anti-patterny

- quota považovaná za reserved cluster capacity;
- quota presne na steady-state spotrebu;
- default CPU limit pre všetko bez load testu;
- jedna LimitRange pre web, batch, database a sidecars;
- žiadna object-count quota;
- HPA bez quota saturation alertu;
- zníženie `hard` ako okamžitá remediation;
- ručné mazanie Pods namiesto opravy policy/template-u;
- source manifest považovaný za admitted resource truth.

## 13. Kontrolné otázky

1. Ktoré tri policy subjects musíš oddeliť pri quota incidente?
2. Ako LimitRange zmení HPA denominator a quota usage?
3. Prečo ResourceQuota nie je runtime throttling ani capacity reservation?
4. Kedy HPA funguje správne, ale serving capacity nerastie?
5. Prečo policy zmena nie je retroaktívna pre existujúce Pody?
6. Ako finalizers a finished Jobs ovplyvnia `used`?
7. Čo musí obsahovať recovery headroom model?
8. Ako sa líši storage quota od backend capacity a backupu?
9. Prečo PriorityClass-scoped quota potrebuje access control?
10. Ako overíš business a forbidden outcomes po quota recovery?

## Glossary impact

Relevantné pojmy: namespace governance subject, LimitRange generation, admitted resource delta, quota accounting subject, quota admission verdict, quota recovery headroom, object-count lifecycle, scoped quota subject, policy adoption generation, quota saturation incident, source-to-admitted resource diff, namespace capacity envelope a subject-bound governance verification.

## Oficiálna dokumentácia

- [Resource Quotas](https://kubernetes.io/docs/concepts/policy/resource-quotas/)
- [Limit Ranges](https://kubernetes.io/docs/concepts/policy/limit-range/)
- [Configure Memory and CPU Quotas](https://kubernetes.io/docs/tasks/administer-cluster/manage-resources/quota-memory-cpu-namespace/)
- [Configure CPU Constraints for a Namespace](https://kubernetes.io/docs/tasks/administer-cluster/manage-resources/cpu-constraint-namespace/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: SecurityContext a Pod Security](securitycontext-pod-security.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Cluster installation a lifecycle →](cluster-installation-lifecycle.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
