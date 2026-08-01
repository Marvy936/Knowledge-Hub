# ResourceQuota a LimitRange

ResourceQuota a LimitRange riadia namespace consumption a defaulty. ResourceQuota obmedzuje celkový súčet resources alebo počet objektov. LimitRange nastavuje default, minimum, maximum alebo pomer pre jednotlivé Pods, containers alebo PVCs podľa podporovaných typov. Obe sa vyhodnocujú pri admission. Ak request zlyhá na quota, Pod objekt nemusí vôbec vzniknúť a scheduler ani kubelet nemajú čo riešiť.

Pri `payments-api` chceme, aby namespace `production` mal dostatočnú kapacitu pre šesť replík, rollout surge, HPA scale-up a kritické Jobs, ale aby jedna chybná aplikácia nemohla vyčerpať celý cluster. Quota preto musí vychádzať z prevádzkového a rollout modelu, nie iba zo steady-state sumy requests.

## ResourceQuota pre compute

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: production-compute
  namespace: production
spec:
  hard:
    requests.cpu: "20"
    requests.memory: 40Gi
    limits.cpu: "60"
    limits.memory: 80Gi
    pods: "200"
```

Status ukazuje hard a used:

```bash
kubectl get resourcequota production-compute -n production -o yaml
```

`used` je admission/accounting state, nie reálny usage. Namespace môže mať used memory requests 30 Gi a reálne používať 10 Gi alebo 50 Gi podľa trafficu a limits.

## Object count quota

Quota môže obmedziť počet konkrétnych resources:

```yaml
hard:
  count/secrets: "100"
  count/configmaps: "200"
  persistentvolumeclaims: "50"
  services.loadbalancers: "5"
```

Object count chráni API a external costs, ale príliš nízky limit môže zablokovať rollout, secret rotation alebo controller-created child objects.

Versionované ConfigMaps a Secrets potrebujú retention cleanup. Inak namespace narazí na quota aj pri správnom immutable model-e.

## Storage quota

Quota možno viazať na storage requests a StorageClass:

```yaml
hard:
  requests.storage: 2Ti
  fast-zonal.storageclass.storage.k8s.io/requests.storage: 1Ti
  fast-zonal.storageclass.storage.k8s.io/persistentvolumeclaims: "20"
```

Presné resource names závisia od API contractu. Storage quota kontroluje PVC requesty, nie reálny backend snapshot count, orphaned disks alebo cloud spend mimo Kubernetes objects.

## Scope a ScopeSelector

Quota môže cieliť na vybrané skupiny, napríklad BestEffort alebo určité PriorityClasses podľa podporovaných scopes.

```yaml
spec:
  scopeSelector:
    matchExpressions:
      - scopeName: PriorityClass
        operator: In
        values:
          - production-critical
```

Viac quotas v namespace sa uplatňuje spoločne. Pod musí spĺňať všetky relevantné constraints.

## LimitRange defaults

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: production-defaults
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
        cpu: 25m
        memory: 32Mi
      max:
        cpu: "4"
        memory: 8Gi
```

Ak container resources chýbajú, admission môže doplniť defaults. Source manifest a admitted Pod template sa potom líšia.

```bash
kubectl apply --dry-run=server -f deployment.yaml -o yaml
```

Server-side dry-run ukáže efektívne hodnoty pred persistovaním. CI má kontrolovať admitted model, nie iba source YAML.

## Default limit môže vytvoriť throttling alebo OOM

Legacy aplikácia bez CPU limitu môže po zavedení LimitRange dostať default 500m. Pods sa úspešne vytvoria, no pri burstoch CPU throttling zvýši latency. Default memory limit môže zase spôsobiť OOM.

LimitRange je admission default, nie performance tuning. Zmena namespace defaultov musí prejsť workload inventory a canary.

## LimitRange pre PVC

```yaml
limits:
  - type: PersistentVolumeClaim
    min:
      storage: 1Gi
    max:
      storage: 500Gi
```

Tým sa zabráni extrémne malým alebo veľkým claims podľa policy. Neurčuje StorageClass, access mode ani data lifecycle.

## Quota a Deployment rollout

Steady state:

```text
6 Pods × 250m CPU request = 1.5 CPU
```

Rolling update s `maxSurge: 2` potrebuje dočasne až:

```text
8 Pods × 250m = 2 CPU
```

Ak quota povoľuje presne 1.5 CPU, nový ReplicaSet Pod create zlyhá. Pri `maxUnavailable: 0` rollout nemôže odstrániť starý Pod a zastane.

Quota design musí zahŕňať surge, terminating Pods podľa accounting semantics, Jobs, sidecars a emergency headroom.

## Quota a HPA

HPA môže zvýšiť desired replicas na 30. Deployment zmení scale, no ReplicaSet create requests môžu zlyhať na quota.

```bash
kubectl describe hpa payments-api -n production
kubectl describe replicaset -n production <rs-name>
kubectl get events -n production --sort-by=.lastTimestamp
```

HPA môže byť `AbleToScale=True`, ale reálna ready capacity nerastie. Quota je samostatná admission boundary.

## Quota a controller-created objects

CronJob vytvára Jobs a Jobs Pods. StatefulSet vytvára PVCs. Certificate controller vytvára Secrets. Operator môže vytvárať CRs alebo Services.

Quota planning musí zahŕňať dependent graph, nie iba objekty deklarované priamo v Git repozitári.

Ak quota zablokuje child create, parent controller typicky zapíše condition alebo Event. Parent object existence nie je dôkaz complete realization.

## Priority a quota

Vyššia PriorityClass neobchádza ResourceQuota. Môže ovplyvniť scheduling/preemption po vytvorení Podu, ale admission request musí najprv prejsť quota.

ScopeSelector môže rezervovať oddelenú quota pre critical priority, no treba zabrániť tomu, aby bežný používateľ mohol svojvoľne používať critical PriorityClass.

## Namespace tenancy

Quota pomáha férovému rozdeleniu clusteru, ale nie je tvrdá Node isolation. Dva namespaces môžu zdieľať Nodes, kernel, storage backend a network dataplane. Quota neobmedzí každý external API call alebo cloud spend.

Tenant model potrebuje RBAC, admission, NetworkPolicy, Pod Security, node placement, storage a observability hranice.

## Aktualizácia quota

Zvýšenie quota povoľuje budúce admission requests. Nevyvolá automaticky nový controller attempt okamžite vo všetkých prípadoch, ale controllers zvyčajne reconcile-nu blocked state po watch/resync. Over progress cez Events a child objects.

Zníženie hard limitu pod aktuálne `used` typicky neodstráni existujúce objekty. Zablokuje ďalší rast, kým usage neklesne. Preto zmena quota nie je eviction alebo scale-down nástroj.

## Incident: rollout nevedel vytvoriť nový Pod

Deployment generation 12 a nový ReplicaSet existovali. ReplicaSet Event uvádzal:

```text
exceeded quota: production-compute, requested: requests.cpu=250m, used: requests.cpu=2, limited: requests.cpu=2
```

Scheduler dashboard bol zelený, pretože Pod object nikdy nevznikol. Oprava zvýšila quota podľa schváleného surge budgetu. Skorší control je server-side admitted resource sum a quota preflight pred releaseom.

## Incident: LimitRange potichu pridala CPU limit

Namespace dostal nový LimitRange default. Aplikácia bez explicitného limitu pri ďalšom rollout-e dostala 500m CPU limit. New revision mala vysokú throttling, old Pods nie, takže incident vyzeral ako code regression.

Source Deployment diff neobsahoval resources. Admitted Pod YAML a cgroup metrics odhalili default. Oprava pridala explicitné reviewované values a zmenu LimitRange podrobila impact auditu.

## Incident: Secret rotation zlyhala na object quota

Versionované Secrets sa roky nečistili a namespace dosiahol `count/secrets`. Rotation controller nedokázal vytvoriť nový Secret `SE09`. Starý credential sa blížil k expiry.

Oprava odstránila iba bezpečne nepoužívané generácie po consumer inventory a potom vytvorila nový Secret. Skorší control je retention owner a alert pred quota exhaustion.

## Incident: HPA desired=30, ready=12

Traffic spike zvýšil HPA target na 30. Namespace quota dovolila iba 12 Pod requests. HPA status ukazoval požadovaný scale, ale ReplicaSet Events opakovali quota errors a Service capacity nerástla.

Recovery dočasne zvýšila quota a cluster capacity. Neskôr platforma pridala autoscaling envelope, ktorý zosúladil HPA maxReplicas, quota, database connections a Node autoscaler limity.

## Model, ktorý si treba odniesť

ResourceQuota obmedzuje namespace súčty a object counts. LimitRange mení alebo validuje jednotlivé resource requests pri admission. Obe pôsobia pred schedulingom. Pri rollout-e a autoscalingu treba počítať surge, sidecars, Jobs, PVCs a child objects. Source YAML nemusí obsahovať admitted defaults, preto používaj server-side dry-run a overuj allowed aj quota-blocked paths.

## Referencie

- [Resource Quotas](https://kubernetes.io/docs/concepts/policy/resource-quotas/)
- [Limit Ranges](https://kubernetes.io/docs/concepts/policy/limit-range/)
- [Configure Memory and CPU Quotas for a Namespace](https://kubernetes.io/docs/tasks/administer-cluster/manage-resources/quota-memory-cpu-namespace/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: SecurityContext a Pod Security](securitycontext-pod-security.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Cluster installation a lifecycle →](cluster-installation-lifecycle.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
