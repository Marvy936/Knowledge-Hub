# HPA a autoscaling

Kubernetes autoscaling mení počet replík, resource requests alebo počet Nodes podľa pozorovaného dopytu a policy. Horizontal Pod Autoscaler (HPA) upravuje replica count škálovateľného workloadu. Vertical Pod Autoscaler (VPA) odporúča alebo mení Pod resources a Node autoscaling mení cluster capacity. Tieto slučky musia byť navrhnuté spoločne, inak môžu bojovať o rovnaký systém alebo prenášať bottleneck na inú vrstvu.

## 1. Horizontal scaling

HPA typicky škáluje:

- Deployment,
- StatefulSet,
- iný resource so `/scale` subresource.

HPA nie je určený pre DaemonSet, pretože jeho replica count vyplýva z počtu eligible Nodes.

```text
metrics
→ HPA controller
→ desired replicas
→ scale subresource workloadu
→ workload controller
→ nové alebo odstránené Pody
→ scheduler a Nodes
```

HPA nevytvára Nodes ani nezabezpečuje, že nové Pody budú schedulovateľné.

## 2. Základný HPA objekt

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web
  minReplicas: 3
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 65
```

HPA zapisuje požadovaný replica count cieľového resource-u cez scale subresource.

## 3. Resource metrics pipeline

CPU a memory resource metrics typicky poskytuje `metrics.k8s.io` API, často cez Metrics Server.

Over:

```bash
kubectl top pods -n production
kubectl get --raw /apis/metrics.k8s.io/v1beta1/namespaces/production/pods
kubectl describe hpa -n production web
```

Metrics Server nie je plnohodnotný dlhodobý monitoring systém. Poskytuje resource metrics pre autoscaling a `kubectl top`, nie historické SLI alebo capacity analytics.

## 4. CPU utilization a requests

Pri targete `averageUtilization` sa CPU utilization počíta relatívne k CPU requestu Pod containers zahrnutých do výpočtu.

Príklad:

- request: `500m`,
- usage: `250m`,
- utilization: približne 50 %.

Bez správnych CPU requests môže resource-utilization autoscaling chýbať, byť nepresný alebo sa správať inak, než operator očakáva.

## 5. Zjednodušený algoritmus

HPA používa pomer aktuálnej a cieľovej metriky:

```text
desiredReplicas = ceil(currentReplicas × currentMetric / desiredMetric)
```

Príklad:

```text
current replicas = 4
current utilization = 90 %
target utilization = 60 %

desired = ceil(4 × 90 / 60) = 6
```

Reálny controller zohľadňuje tolerance, missing metrics, not-yet-ready Pody, stabilization a rate policies.

## 6. Typy metrík

`autoscaling/v2` podporuje viac modelov:

- `Resource` — CPU alebo memory resource metrics,
- `ContainerResource` — resource metric konkrétneho containeru,
- `Pods` — priemerná custom metric na Pod,
- `Object` — metric súvisiaca s jedným Kubernetes objektom,
- `External` — metric mimo Kubernetes objektového modelu.

Custom a external metrics vyžadujú príslušné aggregated API adapters a dôveryhodnú metrics pipeline.

## 7. Priemer vs. absolútna hodnota

Target môže byť napríklad:

- `Utilization` — percento requestu,
- `AverageValue` — priemerná absolútna hodnota na Pod,
- `Value` — celková alebo object-specific hodnota podľa typu metric.

Výber musí zodpovedať business modelu. Queue depth `100` môže znamenať:

- 100 položiek celkovo,
- 100 na repliku,
- 100 na partition,
- 100 iba pre konkrétny tenant.

## 8. Viac metrík

HPA môže vyhodnocovať viac metrics. Typicky zvolí odporúčanie, ktoré vedie k najvyššiemu potrebnému replica countu, ak sú metrics dostupné a policy to umožňuje.

Príklad:

- CPU odporúča 5 replík,
- request rate odporúča 8,
- výsledok je 8.

Pri čiastočnom metric failure môže byť scale-down konzervatívnejší. Sleduj HPA conditions a Events, nie iba current replica count.

## 9. Scale-up behavior

```yaml
spec:
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 0
      selectPolicy: Max
      policies:
        - type: Percent
          value: 100
          periodSeconds: 60
        - type: Pods
          value: 4
          periodSeconds: 60
```

Policies obmedzujú rýchlosť zmeny. Príliš pomalý scale-up zvyšuje latency a queue backlog; príliš rýchly môže spôsobiť:

- image-pull storm,
- connection storm na databázu,
- thundering herd,
- cluster capacity exhaustion,
- neúmerný cloud cost.

## 10. Scale-down stabilization

```yaml
spec:
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 25
          periodSeconds: 60
```

Stabilization window používa predchádzajúce odporúčania na tlmenie flapping-u. Defaultné správanie a controller flags over podľa verzie a cluster konfigurácie.

Scale-down musí zohľadniť:

- traffic drain,
- in-flight work,
- queue partitioning,
- connection pools,
- cache warm-up,
- PDB a termination grace period.

## 11. Startup a readiness

Nový Pod môže mať vysoké CPU počas inicializácie alebo ešte nemusí byť Ready. HPA má mechanizmy na konzervatívnejšie spracovanie not-yet-ready Podov a CPU initialization period, ale správny workload stále potrebuje:

- startup probe,
- readiness probe,
- reprezentatívne requests,
- bounded warm-up,
- metric bez bootstrap spike distortion.

## 12. Minimum a maximum replicas

`minReplicas` je availability a baseline-capacity rozhodnutie. `maxReplicas` je ochranná hranica, nie garancia dostatočnej kapacity.

Pri `maxReplicas` dosiahnutom pod rastúcim loadom musí monitoring upozorniť na saturation. HPA status môže byť „funkčný“, zatiaľ čo aplikácia už nestíha.

## 13. Manual scaling a GitOps konflikt

HPA vlastní `spec.replicas` cieľového workloadu. Ak GitOps controller alebo pipeline neustále zapisuje statickú hodnotu, vzniká field ownership alebo reconciliation konflikt:

```text
HPA nastaví replicas=10
GitOps vráti replicas=3
HPA znovu nastaví replicas=10
```

Riešenie:

- HPA-managed workloads nemajú mať statický replicas drift enforcement,
- deklaruj HPA ako autoritatívneho vlastníka scale field-u,
- oddeľ initial/bootstrap replica nastavenie od runtime autoscaling policy.

## 14. HPA a Deployment rollout

Počas rollout-u HPA škáluje Deployment, zatiaľ čo Deployment rozdeľuje replicas medzi starý a nový ReplicaSet podľa rollout strategy.

Riziká:

- surge zvyšuje krátkodobú capacity potrebu,
- metrika sa mieša medzi revisions,
- nová verzia má inú resource efficiency,
- readiness znižuje počet dostupných backendov,
- rollback nemení HPA policy.

Canary s oddeleným Deploymentom potrebuje samostatný autoscaling model alebo vedomé fixed-capacity pravidlo.

## 15. HPA a StatefulSet

HPA môže škálovať StatefulSet, ale application musí podporovať:

- dynamický membership,
- per-replica storage provisioning,
- scale-down bez straty quorum alebo dát,
- bezpečné odstránenie najvyšších ordinalov,
- rebalancing a bootstrap nových členov.

Kubernetes nevie z CPU metriky odvodiť bezpečný database cluster membership model.

## 16. Queue-based autoscaling

Pre workers je často vhodnejšia business metric:

```text
backlog per ready worker
oldest message age
processing latency
```

Samotná queue depth môže byť zavádzajúca, ak sa mení:

- priemerný processing time,
- počet partitions,
- retry/dead-letter traffic,
- downstream rate limit,
- batch size.

Exactly-once a work distribution zostávajú application/queue zodpovednosťou.

## 17. Event-driven autoscaling

Ekosystémové controllery, napríklad KEDA, môžu škálovať podľa event sources a podporovať scale-to-zero modely. Nie sú súčasťou core HPA API a vyžadujú vlastný lifecycle, security, CRDs, upgrades a metrics trust model.

Scale-to-zero potrebuje riešiť:

- cold start,
- activation metric,
- lost wake-up prevention,
- minimum processing concurrency,
- event-source credentials.

## 18. VPA

Vertical Pod Autoscaler je samostatne inštalovaný controller a API, ktorý môže:

- odporúčať requests,
- aplikovať nové resources pri Pod replacement-e alebo podporovanom update modeli,
- pomôcť rightsizing-u.

VPA a HPA na tej istej CPU/memory signalizácii môžu vytvárať feedback loop. Bežný model:

- HPA škáluje podľa external/business metric,
- VPA odporúča alebo upravuje CPU/memory requests,
- policy určuje, kto vlastní ktoré fields.

## 19. Node autoscaling

Node autoscaler reaguje na schedulovateľnosť a capacity potrebu clusteru, nie priamo na application latency.

Typický chain:

```text
load rastie
→ HPA vytvorí viac replicas
→ Pody zostanú Pending pre nedostatok capacity
→ node autoscaler pridá Node
→ scheduler bindne Pody
→ kubelet stiahne image a spustí workload
```

Celková reakcia zahŕňa metric delay, HPA interval, provisioning Node-u, bootstrap, image pull a Pod readiness.

## 20. Scale-to-zero a minimum capacity

Core HPA typicky pracuje s minimálne jednou replikou v bežnom workload modeli; scale-to-zero závisí od konkrétnej API/metric/controller podpory.

Pre latency-sensitive služby drž baseline capacity, ktorá absorbuje load počas autoscaling delay.

## 21. Metrics security a correctness

Metrics adapter je control-plane vstup. Falošná alebo manipulovateľná metric môže:

- vytvoriť denial of wallet,
- znížiť replicas počas útoku,
- preťažiť downstream,
- obísť tenant capacity policy.

Chráň:

- metrics API RBAC,
- adapter credentials,
- query definitions,
- tenant label isolation,
- metric freshness,
- audit a alerting.

## 22. Observability

```bash
kubectl get hpa -n production
kubectl describe hpa -n production web
kubectl get deployment -n production web
kubectl get events -n production --sort-by=.metadata.creationTimestamp
kubectl top pods -n production
```

Sleduj:

- current a desired replicas,
- current/target metrics,
- `AbleToScale`, `ScalingActive`, `ScalingLimited` conditions,
- metric fetch errors,
- čas na Ready po scale-up,
- saturation pri max replicas,
- scale events a flapping,
- Pending Pods a node provisioning latency.

## 23. Troubleshooting

### HPA ukazuje `<unknown>`

Over metrics API, Metrics Server/adapter health, RBAC, selector, metric name a freshness.

### CPU HPA neškáluje

Over CPU requests, current metric, tolerance, min/max replicas, startup/readiness a HPA conditions.

### HPA škáluje, ale latency rastie

Over cold start, downstream bottleneck, queueing, load balancing, readiness, Node capacity a max replicas.

### Neustále scale up/down

Over noisy metric, krátke windows, cache warm-up, request spikes, percent policy a metric aggregation interval.

### Nové Pody zostávajú Pending

HPA funguje; zlyháva scheduler/capacity/storage/placement vrstva. Over `FailedScheduling` a node autoscaler.

### Scale-down prerušuje prácu

Over readiness drain, preStop, termination grace, PDB, queue acknowledgment a connection handling.

## 24. Anti-patterny

### CPU target bez CPU requests

Utilization nemá správny denominator.

### HPA nad bottleneckom, ktorý sa neškáluje

Viac Podov iba zvýši tlak na databázu alebo external API.

### Statický `replicas` neustále vynucovaný GitOps-om

Vzniká reconciliation fight.

### Memory utilization ako jediný signal pre leak

HPA pridá ďalšie leakujúce Pody namiesto odstránenia chyby.

### Príliš nízke `maxReplicas`

Autoscaling narazí na strop bez dostatočnej alerting signalizácie.

### Príliš vysoké `maxReplicas`

Application môže vyčerpať database connections, quota alebo budget.

### Scale-down bez idempotencie a draining-u

In-flight práca sa stratí alebo vykoná duplicitne.

## 25. Kontrolné otázky

1. Čo HPA mení a čo nemení?
2. Prečo CPU utilization závisí od requests?
3. Ako sa približne vypočíta desired replica count?
4. Aké metric types podporuje `autoscaling/v2`?
5. Načo slúži stabilization window?
6. Ako HPA interaguje s Deployment rolloutom?
7. Prečo HPA a GitOps môžu bojovať o `spec.replicas`?
8. Ako sa líši HPA, VPA a Node autoscaling?
9. Prečo viac replicas nemusí znížiť latency?
10. Ako diagnostikuješ HPA, ktoré vytvorilo Pending Pody?

## Glossary impact

Relevantné pojmy: Horizontal Pod Autoscaler, scale subresource, resource metric, custom metric, external metric, average utilization, desired replica calculation, HPA tolerance, scale-up policy, scale-down stabilization, `ScalingLimited`, Metrics Server, metrics adapter, Vertical Pod Autoscaler, Node autoscaling, event-driven autoscaling, scale-to-zero a autoscaling feedback loop.

## Oficiálna dokumentácia

- [Horizontal Pod Autoscaling](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/)
- [Autoscaling Workloads](https://kubernetes.io/docs/concepts/workloads/autoscaling/)
- [Vertical Pod Autoscaling](https://kubernetes.io/docs/concepts/workloads/autoscaling/vertical-pod-autoscale/)
- [Node Autoscaling](https://kubernetes.io/docs/concepts/cluster-administration/node-autoscaling/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Taints, tolerations, affinity a topology](taints-tolerations-affinity-topology.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: RBAC →](rbac.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
