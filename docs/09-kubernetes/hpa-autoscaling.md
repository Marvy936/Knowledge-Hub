# HPA a autoscaling

HorizontalPodAutoscaler mení desired počet replík workloadu podľa metrík. Nepridáva Node kapacitu, neopravuje pomalú aplikáciu a nepozná business bezpečnosť scale transitionu. HPA číta metrics API, vypočíta odporúčaný replica count a zapisuje scale subresource cieľového Deploymentu alebo iného podporovaného resource.

Pri `payments-api` chceme škálovať medzi šiestimi a tridsiatimi replikami podľa CPU a request queue. CPU signal reaguje na výpočtové zaťaženie, queue signal na nevybavenú prácu. Oba metrics musia patriť k správnym Pods a časovému oknu a workload musí mať dostatočné resources aj Node capacity.

## Základný HPA

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: payments-api
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: payments-api
  minReplicas: 6
  maxReplicas: 30
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 65
```

HPA používa scale subresource cieľa. Deployment template a rollout strategy zostávajú v Deployment controlleri. HPA typicky vlastní aktuálny replica count, preto GitOps nemá neustále vracať `.spec.replicas` na statickú hodnotu.

## CPU utilization závisí od requestu

CPU utilization sa pri resource metric targete počíta voči CPU requestu. Ak Pod používa 200m CPU a request je 250m, utilization je približne 80 %. Ak request zmeníme na 500m pri rovnakom usage, utilization klesne približne na 40 %.

Zmena requests preto mení autoscaling správanie aj bez zmeny trafficu.

Pods bez relevantného CPU requestu môžu byť z výpočtu vynechané alebo metric nebude použiteľná podľa HPA semantics. Production HPA potrebuje konzistentné requests vo všetkých cieľových Pods.

## Zjednodušený výpočet desired replicas

Základný vzťah:

```text
desiredReplicas = ceil(currentReplicas × currentMetric / desiredMetric)
```

Pri 6 replikách, aktuálnej priemernej utilization 97 % a cieli 65 %:

```text
ceil(6 × 97 / 65) = ceil(8.95) = 9
```

Skutočný controller zohľadňuje tolerance, chýbajúce metrics, not-yet-ready Pods, multiple metrics a behavior rules. Vzorec je mentálny základ, nie úplná implementácia.

## Metrics pipeline

Resource metrics typicky tečú:

```text
kubelet/cAdvisor alebo runtime source
→ metrics-server
→ metrics.k8s.io API
→ HPA controller
```

```bash
kubectl top pods -n production -l app=payments-api
kubectl get --raw='/apis/metrics.k8s.io/v1beta1/namespaces/production/pods' | jq .
```

Ak `kubectl top` nefunguje, HPA resource metric pravdepodobne nemá potrebné dáta. Metrics freshness a timestamp sú rovnako dôležité ako value.

Custom a external metrics používajú ďalšie adapters a API groups. Každá vrstva môže mať stale cache, label mismatch alebo query error.

## Multiple metrics

Autoscaling/v2 môže kombinovať viac metrics:

```yaml
metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 65
  - type: Pods
    pods:
      metric:
        name: payments_queue_depth
      target:
        type: AverageValue
        averageValue: "20"
```

Controller vypočíta odporúčanie pre každý metric a pri scale-up typicky použije najvyššie odporúčanie podľa semantics. Ak jeden metric chýba, scale-down môže byť konzervatívnejší, aby sa predišlo nebezpečnému zmenšeniu.

Queue metric musí mať správny význam. Celkový global backlog delený per-Pod average nemusí zodpovedať reálnej partition alebo consumer concurrency.

## Object a external metrics

Object metric môže sledovať konkrétny Kubernetes objekt, napríklad Ingress requests. External metric môže pochádzať mimo clusteru, napríklad cloud queue length.

External metrics adapter je security a correctness boundary. Nesprávny tenant, label selector alebo unit môže scale-nuť production podľa staging dát.

Metric contract má obsahovať:

```text
source a owner
unit
aggregation
window a delay
label cardinality
missing-data semantics
expected relation k replica capacity
```

## Scale behavior

```yaml
behavior:
  scaleUp:
    stabilizationWindowSeconds: 0
    policies:
      - type: Percent
        value: 100
        periodSeconds: 60
      - type: Pods
        value: 4
        periodSeconds: 60
    selectPolicy: Max
  scaleDown:
    stabilizationWindowSeconds: 300
    policies:
      - type: Percent
        value: 25
        periodSeconds: 60
```

Scale-up môže byť rýchly, ale cluster musí schedulovať nové Pods a dependencies musia zvládnuť connection burst. Scale-down býva pomalší, aby metric flapping nevytvoril oscillation a aby connections/queues stihli drain.

Stabilization window používa predchádzajúce odporúčania podľa controller semantics. Nie je to jednoduchý sleep.

## Readiness a not-yet-ready Pods

Nové Pods môžu mať vysoký startup CPU alebo chýbajúce metrics. HPA používa heuristiky, aby scale decisions neboli skreslené not-yet-ready workloadmi.

Startup CPU spike je lepšie oddeliť startup probe a initialization designom než ľubovoľne skrývať metrics. Pri JVM môže HPA bez rozumných initialization periods reagovať na warmup nepredvídateľne.

## HPA a Deployment rollout

Počas rolling update-u existujú old a new Pods s potenciálne odlišnou CPU efektivitou. HPA mení total replicas, Deployment rozdeľuje kapacitu medzi ReplicaSets podľa rollout strategy.

```text
HPA desired replicas
→ Deployment total desired
→ rolling strategy old/new split
→ scheduler a cluster capacity
```

Ak nová revision používa dvojnásobok CPU, HPA môže scale-upovať počas rollout-u. Surge Pods a HPA growth spolu zvýšia peak capacity nad bežný model.

Release gate má testovať HPA aj rollout interaction, nie iba steady state.

## HPA a Cluster Autoscaler

HPA vytvorí viac desired Pods. Ak sa nezmestia, zostanú Pending. Node autoscaler môže pridať Nodes, ak rozpozná, že Pod by sa po pridaní vhodnej Node group dal schedulovať.

```text
traffic rastie
→ HPA zvýši replicas
→ nové Pods Pending
→ Node autoscaler pridá správnu kapacitu
→ scheduler pridelí Pods
→ kubelet spustí runtime
→ readiness pridá capacity
```

Tento chain má oneskorenie. Min replicas a headroom musia pokryť čas do novej ready capacity.

Ak Pod blokuje volume topology alebo impossible affinity, pridanie všeobecného Node-u nepomôže.

## HPA a VPA

Vertical Pod Autoscaler môže odporúčať alebo meniť requests. Keď HPA používa CPU utilization voči requestu, VPA zmena requestu mení denominator a tým HPA signál.

Kombinácia potrebuje podporovaný a reviewovaný model. Často sa HPA používa na custom/external metric nezávislý od requestu, alebo VPA zostáva recommendation-only pre HPA-managed workload.

## HPA a quota

HPA môže požadovať viac replík, ale namespace ResourceQuota môže Pod create odmietnuť. HPA status ukáže desired vyššie, Deployment/ReplicaSet Events ukážu quota failure.

```bash
kubectl describe hpa payments-api -n production
kubectl get resourcequota -n production -o yaml
kubectl get events -n production --sort-by=.lastTimestamp
```

HPA controller nie je capacity reservation systém.

## Scale-down safety

Scale-down ukončuje Pods cez workload controller. Aplikácia potrebuje graceful termination, connection drain a idempotency. HPA nevie, že jeden Pod drží unique in-memory work bez durable checkpointu.

Queue consumers musia pred termination prestať prijímať novú prácu, dokončiť alebo requeue-nuť aktuálnu úlohu a bezpečne uvoľniť lease.

PodDisruptionBudget typicky nekontroluje všetky voluntary scale-down transitions rovnako ako drain; HPA safety musí byť navrhnutá na application úrovni.

## Observácia HPA

```bash
kubectl get hpa payments-api -n production
kubectl describe hpa payments-api -n production
kubectl get hpa payments-api -n production -o yaml
```

Sleduj current/desired replicas, current metrics, conditions `AbleToScale`, `ScalingActive`, `ScalingLimited` a reason/message. Condition musí byť interpretovaná s aktuálnou generation a metrics timestamps.

`ScalingLimited=True` môže znamenať min/max limit, nie controller failure.

## Incident: zníženie CPU requestu zdvojnásobilo repliky

Tím optimalizoval bin packing a znížil CPU request z 500m na 250m. Reálny usage ostal okolo 200m. HPA utilization sa zmenila zo 40 % na 80 % a scale-upovala z 10 na 16 replík.

Cluster cost stúpol a database connections prekročili bezpečný počet. Oprava revalidovala HPA target po zmene requestu a pridala connection budget.

## Incident: HPA bola zelená, ale nové Pods sa nespustili

HPA vypočítala 24 replík a zapísala scale. Deployment desired count sa zvýšil. Dvanásť nových Podov zostalo Pending pre namespace quota a required anti-affinity.

HPA fungovala správne. Serving capacity nerástla. Recovery dočasne zvýšila quota a pridala Nodes. Skorší control je end-to-end autoscaling test vrátane scheduling a readiness, nie iba HPA desired replicas.

## Incident: stale external metric spôsobila oscillation

Metrics adapter cache-oval queue depth päť minút, ale HPA vyhodnocovala každých niekoľko sekúnd. Po vyprázdnení queue stále videla vysokú hodnotu a scale-upovala. Po náhlom refreshi hodnota klesla na nulu a bez dostatočnej stabilization začal prudký scale-down.

Oprava definovala freshness SLO, odmietla príliš staré samples a pridala scale-down window. Metric status začal publikovať timestamp a source generation.

## Incident: scale-down prerušil payment

Worker spracovával payment po external authorization, ale pred local commitom. HPA znížila replicas a Pod dostal SIGTERM. Aplikácia ukončila process okamžite. Retry na inom Pode autorizoval platbu znova.

Oprava zaviedla graceful drain, idempotency key a transaction reconciliation. HPA behavior sa spomalil, ale correctness vznikla až v aplikácii.

## Model, ktorý si treba odniesť

HPA je controller scale subresource-u. Jeho rozhodnutie závisí od metric contractu, requests, freshness a behavior pravidiel. Desired replicas ešte musia prejsť Deploymentom, schedulerom, Node autoscalerom, kubeletom a readiness. Autoscaling je úspešný až keď rastie alebo klesá skutočná business capacity bez porušenia dependency, quota a termination contracts.

## Referencie

- [Horizontal Pod Autoscaling](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [HorizontalPodAutoscaler Walkthrough](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale-walkthrough/)
- [Resource Metrics Pipeline](https://kubernetes.io/docs/tasks/debug/debug-cluster/resource-metrics-pipeline/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Taints, tolerations, affinity a topology](taints-tolerations-affinity-topology.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: RBAC →](rbac.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
