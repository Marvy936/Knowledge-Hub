# ResourceQuota a LimitRange

ResourceQuota a LimitRange sú namespaced governance mechanizmy. ResourceQuota obmedzuje súhrnnú spotrebu resources alebo počet objektov v namespace. LimitRange nastavuje alebo validuje minimá, maximá a defaulty pre jednotlivé Pods, containers alebo claims. Ani jeden mechanizmus nevytvára cluster capacity, negarantuje performance ani nenahrádza application-level rate limiting.

## 1. Prečo namespace governance

Bez limitov môže jeden tím alebo chybný controller:

- vytvoriť tisíce Podov alebo Jobs,
- spotrebovať všetok CPU/memory allocatable,
- vytvoriť veľké množstvo PVCs alebo LoadBalancer Services,
- zaplniť API server/etcd objektmi,
- zvýšiť cloud cost,
- zablokovať iné namespaces.

Governance potrebuje kombináciu:

- ResourceQuota,
- LimitRange,
- requests/limits,
- PriorityClass a fairness,
- autoscaling boundaries,
- cloud/account quotas,
- budget a cost observability.

## 2. ResourceQuota

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: production-quota
  namespace: production
spec:
  hard:
    requests.cpu: "20"
    requests.memory: 40Gi
    limits.cpu: "40"
    limits.memory: 80Gi
    pods: "100"
    persistentvolumeclaims: "20"
```

Status obsahuje:

- `hard` — platný limit,
- `used` — aktuálne účtovaná spotreba.

```bash
kubectl describe resourcequota -n production production-quota
```

## 3. Compute quota

Bežné quota keys:

- `requests.cpu`,
- `requests.memory`,
- `limits.cpu`,
- `limits.memory`,
- `requests.ephemeral-storage`,
- `limits.ephemeral-storage`,
- huge pages podľa veľkosti,
- extended resources podľa podporovaného modelu.

Quota počíta deklarované requests/limits, nie live utilization.

Pod s CPU requestom `500m`, ktorý používa iba `50m`, stále spotrebúva `500m` z `requests.cpu` quota.

## 4. Object count quota

```yaml
spec:
  hard:
    count/deployments.apps: "20"
    count/jobs.batch: "100"
    count/secrets: "200"
    services.loadbalancers: "5"
```

Object quotas chránia:

- API server a etcd,
- controller workload,
- cloud resources,
- namespace operability.

Limit počtu objektov nie je retention policy. CronJobs a Jobs stále potrebujú history/TTL cleanup.

## 5. Storage quota

Príklady:

```yaml
spec:
  hard:
    requests.storage: 2Ti
    persistentvolumeclaims: "50"
    fast.storageclass.storage.k8s.io/requests.storage: 500Gi
    fast.storageclass.storage.k8s.io/persistentvolumeclaims: "10"
```

StorageClass-scoped quota umožňuje odlišné hranice pre drahé alebo špeciálne storage tiers.

Quota nezaručuje, že backing storage je dostupné alebo provisionovateľné v požadovanej topology.

## 6. Scope

ResourceQuota môže mať scopes, napríklad podľa Pod lifecycle alebo QoS-related kategórie podľa podporovaného API:

```yaml
spec:
  scopes:
    - NotTerminating
```

Scope rozhoduje, ktoré objects sa do quota počítajú. Pred použitím over presné semantics a podporované resource combinations.

## 7. Scope selectors

`scopeSelector` umožňuje expresívnejší výber:

```yaml
spec:
  scopeSelector:
    matchExpressions:
      - scopeName: PriorityClass
        operator: In
        values: [high-priority]
```

Použitie:

- quota pre konkrétne PriorityClasses,
- oddelenie critical a bežných workloadov,
- governance podľa resource scope.

Nesprávne scope rules môžu vytvoriť nečakanú medzeru, v ktorej workload nespadá do plánovanej quota.

## 8. ResourceQuota admission

Pri create/update API requeste quota admission kontroluje, či nová deklarácia neprekročí hard limit.

Request môže byť odmietnutý napríklad:

```text
exceeded quota: production-quota,
requested: requests.cpu=2,
used: requests.cpu=19,
limited: requests.cpu=20
```

Quota je API admission control. Nezastaví už bežiaci Pod iba preto, že operator neskôr zníži hard limit pod aktuálne `used`.

## 9. Quota a chýbajúce requests/limits

Ak namespace quota vyžaduje `requests.cpu`, `requests.memory`, `limits.cpu` alebo `limits.memory`, Pod bez príslušných fields môže byť odmietnutý.

LimitRange môže doplniť default values, ale defaulting musí byť zámerný. Tichý default môže spôsobiť:

- prehnané reservation,
- nečakaný CPU throttling,
- HPA denominator zmenu,
- quota exhaustion.

## 10. LimitRange

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: container-defaults
  namespace: production
spec:
  limits:
    - type: Container
      defaultRequest:
        cpu: 100m
        memory: 128Mi
      default:
        cpu: 500m
        memory: 512Mi
      min:
        cpu: 50m
        memory: 64Mi
      max:
        cpu: "2"
        memory: 4Gi
      maxLimitRequestRatio:
        cpu: "10"
```

LimitRange sa uplatňuje pri admission-e nových alebo menených objects podľa podporovaného typu.

## 11. `default` a `defaultRequest`

Pre `type: Container`:

- `defaultRequest` doplní request, ak chýba,
- `default` doplní limit, ak chýba.

Kubernetes resource defaulting môže tiež odvodiť request z limitu podľa všeobecných resource pravidiel. Preto vždy over výsledný admitted Pod:

```bash
kubectl get pod -n production <pod> -o yaml
```

Manifest v Git-e nemusí byť identický s objektom po admission defaulting-u.

## 12. Min a max

LimitRange môže odmietnuť container, ktorý požaduje príliš málo alebo príliš veľa:

```yaml
min:
  cpu: 50m
max:
  cpu: "4"
```

Minimálny request môže chrániť scheduler accuracy, ale príliš vysoké minimum plytvá capacity pri drobných sidecaroch alebo Jobs.

Maximum chráni namespace pred jedným extrémnym workloadom, ale musí zohľadniť legitímne memory-intensive alebo batch workloads.

## 13. `maxLimitRequestRatio`

```yaml
maxLimitRequestRatio:
  cpu: "4"
```

Obmedzuje pomer limit/request. Príklad:

- request `100m`,
- limit `1000m`,
- ratio `10`,
- pri maxime `4` bude request odmietnutý.

Cieľom je obmedziť extrémny overcommit. Pomer však nie je univerzálna performance politika; CPU burst a memory behavior sa zásadne líšia.

## 14. Typy LimitRange

LimitRange môže podľa resource typu pracovať s:

- `Container`,
- `Pod`,
- `PersistentVolumeClaim`.

PVC príklad:

```yaml
spec:
  limits:
    - type: PersistentVolumeClaim
      min:
        storage: 1Gi
      max:
        storage: 500Gi
```

Storage min/max nehovorí nič o IOPS, throughput, topology alebo backup policy.

## 15. ResourceQuota vs. LimitRange

### ResourceQuota

Rieši agregovaný namespace strop:

```text
súčet všetkých Pod requests.cpu ≤ 20 CPU
```

### LimitRange

Rieši jednotlivý object/container contract:

```text
každý container CPU request ≥ 50m a limit ≤ 2 CPU
```

Používajú sa spolu. LimitRange nedokáže obmedziť celkový počet Podov a ResourceQuota sama neurčuje rozumný default pre jeden container.

## 16. Quota nie je reservation cluster capacity

Namespace quota `requests.cpu: 20` neznamená, že namespace má rezervovaných 20 CPU na Nodes.

Reálna schedulovateľnosť závisí od:

- Node allocatable,
- iných namespaces a workloads,
- PriorityClass/preemption,
- placement constraints,
- storage topology,
- aktuálneho cluster scale.

Pre garantovaný tenant capacity model potrebuješ ďalšie mechanizmy alebo dedicated capacity.

## 17. Quota nie je runtime throttling

ResourceQuota nepoužíva cgroups a netlmí proces po prekročení namespace agregátu. Runtime enforcement vykonávajú container limits, kubelet a kernel.

Quota zabraňuje admission-u nových deklarácií, ktoré by strop prekročili.

## 18. Autoscaling interakcie

HPA scale-up môže naraziť na:

- Pod-count quota,
- CPU/memory requests quota,
- PVC quota pri StatefulSete,
- object-count quota,
- LimitRange maximum/default.

HPA potom môže odporúčať viac replicas, ale workload controller nevytvorí ďalšie Pody. Alerting musí sledovať:

- HPA `ScalingLimited`,
- ReplicaFailure/FailedCreate Events,
- quota usage,
- Pending Pods a scheduler status.

## 19. Job a CronJob interakcie

Batch workload môže vyčerpať:

- Pod count,
- Job count,
- CPU/memory quota,
- ephemeral storage,
- PVC count.

Použi:

- `parallelism` limit,
- TTL-after-finished,
- CronJob history limits,
- samostatný namespace alebo scoped quota,
- external results/log retention.

## 20. PriorityClass-scoped quota

Bez scoped quota môže tenant označiť všetky workloady vysokou prioritou, ak má permission používať PriorityClass.

Kombinuj:

- RBAC/admission kontrolu PriorityClass,
- ResourceQuota scope podľa PriorityClass,
- limit počtu a resources high-priority workloadov,
- audit pre preemption udalosti.

## 21. Multi-tenancy

Pre každý namespace definuj:

- owner a cost center,
- CPU/memory/storage/object quotas,
- LimitRange defaults a bounds,
- autoscaling max,
- PriorityClass policy,
- network/security policy,
- exception workflow a expiry.

Rovnaká quota pre dev, batch a production často nedáva zmysel. Governance má odrážať SLO, cost a failure model.

## 22. Quota controller a eventual consistency

`used` status aktualizuje quota controller/admission coordination. Pri vysokom API concurrency môže byť interné účtovanie a reconciliation komplexné, ale API musí zabrániť jednoduchému prekročeniu hard limitu cez paralelné requests.

Pri diagnostike sleduj:

- `status.hard`,
- `status.used`,
- API admission chybu,
- controller-manager health,
- resources, ktoré sa nezmazali pre finalizer.

## 23. Zmeny policy nie sú retroaktívne

Nový LimitRange typicky nezmení resources existujúcich Podov. Nový ResourceQuota neevictne existujúce workloads.

Pre adoption:

1. audituj current state,
2. zvoľ defaults a limits,
3. testuj v staging namespace,
4. aplikuj policy,
5. rolloutni workloads s explicitnými resources,
6. monitoruj rejected admissions,
7. odstráň dočasné exceptions.

## 24. Observability

```bash
kubectl get resourcequota,limitrange -n production
kubectl describe resourcequota -n production
kubectl describe limitrange -n production
kubectl get events -n production --sort-by=.metadata.creationTimestamp
kubectl get pods -n production -o custom-columns=NAME:.metadata.name,CPU_REQ:.spec.containers[*].resources.requests.cpu,MEM_REQ:.spec.containers[*].resources.requests.memory
```

Sleduj:

- percento quota `used/hard`,
- odmietnuté admissions,
- namespaces blízko limitu,
- dominant resource,
- object count growth,
- defaults aplikované na nové workloads,
- HPA alebo Job failures spôsobené quota.

## 25. Troubleshooting

### Pod je rejected pre quota

Porovnaj requested delta, `status.used`, `status.hard` a všetky containers/init/sidecars resources.

### Manifest nemá limit, admitted Pod ho má

LimitRange alebo iný mutating admission doplnil default. Skontroluj resolved object.

### HPA neškáluje nad určitý počet

Over HPA max replicas, quota, FailedCreate Events, scheduler capacity a namespace object limits.

### PVC zostáva nevytvorené pre quota

Over `requests.storage`, PVC count a StorageClass-specific quota.

### Quota `used` zostáva vysoké po cleanup-e

Hľadaj terminating/finalized objects, zostávajúce Jobs/PVCs a controller-manager/quota reconciliation problém.

### LimitRange odmieta in-place resource resize

Nová hodnota porušuje min/max/ratio policy. Existujúci Pod zostáva na predchádzajúcich hodnotách podľa update semantics.

## 26. Anti-patterny

### Quota považovaná za rezervovanú kapacitu

Namespace môže mať quota, ale cluster nemá feasible Nodes.

### Default CPU limit pre každý workload bez testu

Spôsobí plošný throttling a probe latency.

### Veľký limit, malý request

Scheduler preplní Node a workload má nepredvídateľný burst/pressure behavior.

### Žiadna object-count quota

Chybný controller zaplaví API množstvom Jobs, Secrets alebo ConfigMaps.

### Quota bez alertingu

Prvý signál je až failed production rollout alebo HPA scale-up.

### Jedna univerzálna LimitRange pre všetky workloady

Batch, sidecars, databases a web services majú odlišné resource profily.

### Zníženie hard quota pod aktuálne used ako okamžitá remediation

Existujúce workloady pokračujú; zablokujú sa iba nové zmeny a recovery Pody.

## 27. Kontrolné otázky

1. Aký je rozdiel medzi ResourceQuota a LimitRange?
2. Čo znamenajú `hard` a `used`?
3. Prečo quota počíta requests a nie live usage?
4. Ako fungujú object-count quotas?
5. Načo slúži StorageClass-scoped quota?
6. Aký je rozdiel medzi `default` a `defaultRequest`?
7. Čo kontroluje `maxLimitRequestRatio`?
8. Prečo quota negarantuje schedulovateľnú capacity?
9. Ako quota ovplyvní HPA alebo CronJob?
10. Prečo nové policy nie sú automaticky retroaktívne?

## Glossary impact

Relevantné pojmy: ResourceQuota, quota hard limit, quota used status, compute quota, object-count quota, storage quota, quota scope, scope selector, PriorityClass-scoped quota, LimitRange, `defaultRequest`, default limit, minimum resource constraint, maximum resource constraint, `maxLimitRequestRatio`, namespace governance, quota admission a quota saturation.

## Oficiálna dokumentácia

- [Resource Quotas](https://kubernetes.io/docs/concepts/policy/resource-quotas/)
- [Limit Ranges](https://kubernetes.io/docs/concepts/policy/limit-range/)
- [Configure Memory and CPU Quotas](https://kubernetes.io/docs/tasks/administer-cluster/manage-resources/quota-memory-cpu-namespace/)
- [Configure CPU Constraints for a Namespace](https://kubernetes.io/docs/tasks/administer-cluster/manage-resources/cpu-constraint-namespace/)
