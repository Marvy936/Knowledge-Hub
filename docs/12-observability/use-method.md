# USE method

USE je resource-oriented performance metodika. Pre každý relevantný bounded resource skúma **Utilization**, **Saturation** a **Errors**. Jej sila nie je v troch paneloch, ale v discipline: najprv vytvoriť úplný resource inventory, potom identifikovať skutočnú enforcement boundary a až následne rozhodnúť, či resource vysvetľuje user-facing degradáciu.

RED a Golden Signals ukážu, ktorá operation alebo service degraduje. USE pomôže zistiť, či mechanizmus vzniká na CPU scheduler-i, memory pressure, connection poole, disk queue, network linke, quota alebo inom bounded resource. Vysoké utilization samo osebe nie je incident; resource môže pracovať efektívne bez čakania. Saturation je často silnejší causal signal, pretože zachytáva queued, throttled alebo odmietnutú prácu.

## Investigation lifecycle

```text
user alebo business symptom
→ exact operation a affected cohort
→ dependency/component path
→ complete resource inventory
→ resource subject a enforcement boundary
→ effective capacity generation
→ utilization, saturation a errors
→ competing bottleneck hypotheses
→ discriminating observation
→ bounded containment alebo capacity change
→ original a forbidden outcome validation
```

Resource inventory musí zahŕňať aj limits mimo hosta. Application môže mať 40 % CPU a súčasne čakať na database pool s limitom 20 connections. Pod môže mať voľnú memory, ale namespace quota alebo subnet IP pool blokuje ďalší replica. USE sa preto nevykonáva iba cez `top`.

## Exact resource subject

Atlas Payments používa subject `RES-PAY-43`:

```yaml
service: payments-api
release: 7.19.0
operation: payment.settle
cohort: eu-central-1b / enterprise
resourceInventory:
  cpuCgroupLimit: 2 cores
  memoryCgroupLimit: 2Gi
  dbPoolMax: 40 connections per Pod
  providerConcurrencyLimit: 120 per cohort
  natPath: NAT-B
  subnet: SUB-PB
  queueConsumerConcurrency: 80
requiredOutcome: final settlement within 2.5s
```

Každá capacity value potrebuje generation a scope. `dbPoolMax=40` per Pod má iný blast radius než database global connection limit. CPU utilization hosta má iný meaning než cgroup throttling konkrétneho containeru.

## Utilization

Utilization vyjadruje, akú časť dostupnej capacity resource používa. Pri CPU možno sledovať busy time alebo usage voči cgroup limitu. Pri memory je „percent used“ menej priamočiare, pretože page cache a reclaimable memory majú odlišný význam. Pri connection poole môže utilization znamenať active connections / configured maximum.

CPU utilization pre container cohort:

```promql
sum by (pod) (
  rate(container_cpu_usage_seconds_total{
    namespace="payments",
    container="payments-api"
  }[5m])
)
/
sum by (pod) (
  kube_pod_container_resource_limits{
    namespace="payments",
    container="payments-api",
    resource="cpu",
    unit="core"
  }
)
```

Query preukazuje observed CPU usage voči declared Kubernetes limitu pre Pods, ktoré majú obe series. Nepreukazuje CPU wait, throttling alebo host contention. Ak limit chýba, denominator population sa zmení a query môže Pods potichu vynechať.

Database pool utilization:

```promql
max by (pod) (
  db_pool_active_connections{
    service="payments-api"
  }
/
  db_pool_max_connections{
    service="payments-api"
  }
)
```

Hodnota 1.0 znamená obsadený configured pool, nie automaticky preťaženú databázu. Saturation a acquisition latency ukážu, či requests skutočne čakajú.

## Saturation

Saturation je množstvo práce, ktorú resource nemôže okamžite obslúžiť. Môže sa prejaviť ako run queue, pool waiters, disk queue depth, throttled CPU periods, memory reclaim/stall, queue age alebo rate-limit backlog.

Cgroup CPU throttling:

```promql
sum by (pod) (
  rate(container_cpu_cfs_throttled_periods_total{
    namespace="payments",
    container="payments-api"
  }[5m])
)
/
sum by (pod) (
  rate(container_cpu_cfs_periods_total{
    namespace="payments",
    container="payments-api"
  }[5m])
)
```

Výsledok preukazuje podiel observed scheduling periods, v ktorých cgroup narazila na quota. Nepreukazuje, že throttling je príčinou user latency; koreluje sa s operation duration a affected cohortom.

Pool saturation:

```promql
histogram_quantile(
  0.95,
  sum by (le, pod) (
    rate(db_pool_acquire_duration_seconds_bucket{
      service="payments-api"
    }[5m])
  )
)
```

Rast p95 acquisition time pri plnom poole je diskriminačný dôkaz čakania pred database operation. Nízka database query latency potom nevyvracia pool bottleneck, pretože wait vzniká pred získaním connection.

Na Linux hoste možno overiť CPU run queue a disk path:

```bash
vmstat 1 10

iostat -xz 1 10
```

`vmstat` stĺpec `r` ukazuje runnable tasks v jednotlivých samples; sám nepreukazuje cgroup-specific impact. `iostat` poskytuje device utilization, queue a latency evidence; nepovie, ktorá application alebo query I/O vytvorila. Output sa koreluje s process/cgroup a request trace.

## Errors

Resource errors sú explicitné failures na enforcement boundary: allocation failure, OOM kill, connection timeout, disk I/O error, packet drop, quota rejection alebo rate-limit response. Application `500` je service error; resource error môže byť jeho mechanizmus.

Kubernetes memory evidence:

```bash
kubectl get pod -n payments -l app=payments-api \
  -o custom-columns='NAME:.metadata.name,PHASE:.status.phase,RESTARTS:.status.containerStatuses[0].restartCount,LAST_REASON:.status.containerStatuses[0].lastState.terminated.reason'

kubectl describe pod -n payments payments-api-7f8d9c6b7b-abcde
```

Prvý príkaz preukazuje current Pod/container lifecycle summary a last termination reason uložený v status-e. Druhý pridá Events, resources a scheduling/runtime context. `OOMKilled` dokazuje termination mechanizmus, nie automaticky memory leak; môže ísť o príliš nízky limit, burst alebo node pressure.

Network errors môžu vzniknúť pred alebo po NAT. Packet drop metric bez interface a direction identity je slabý dôkaz. Database `too many connections` musí byť priradené exact serveru/proxy a fleet connection budgetu.

## Capacity je effective, nie deklarovaná

Declared limit nemusí byť effective capacity. CPU node má reserved system capacity. Disk môže mať IOPS aj throughput cap. Connection pool môže byť 40, ale database proxy multiplexing alebo transaction pinning mení backend demand. NAT capacity závisí aj od destination tuple concentration.

Capacity model pre scale-out:

```text
workload replicas
× pool max per replica
× expected active fraction
+ migration/admin/recovery reserve
≤ safe database connection budget
```

Ak HPA zdvojnásobí replicas, môže zdvojnásobiť potential pool demand a zhoršiť database incident. Scale-out je preto mutation celej dependency chain, nie lokálna CPU oprava.

## Worked incident: nízka CPU, vysoká settlement latency

Po release `7.19.0` stúpne enterprise settlement p99 na 11 sekúnd iba v `eu-central-1b`. CPU Pods je 45 %, memory 62 % a provider latency normálna. Prvý dashboard preto neukazuje obvious resource saturation.

Competing hypotheses zahŕňajú queue backlog, provider timeout, database lock, pool saturation, NAT port pressure a telemetry delay. RED ukáže, že queue wait je 40 ms a provider span rýchly, ale trace má 8-sekundovú medzeru pred database spanom.

Pool queries ukážu active/max ratio 1.0, 76 waiters a acquire p95 7.8 s. Database server CPU je iba 38 % a query p95 po získaní connection 55 ms. Root cause je application pool exhaustion, nie database compute.

Loaded configuration inventory odhalí, že release `7.19.0` zvýšil provider worker concurrency z 40 na 120, ale pool ostal 40. Viac concurrent operations čaká na malý pool a client retry pridáva ďalšie waiters.

Containment zníži worker concurrency a pozastaví scale-out affected cohortu. Plošné zvýšenie pool max je zakázané bez global database budgetu, pretože 24 Pods × vyšší pool by mohlo preťažiť writer.

Recovery vypočíta fleet budget, nastaví bounded concurrency 50, pool max 50 a acquisition timeout s explicitným overload outcome. Canary overí logical settlement rate, pool wait, database connections a one-operation-one-settlement invariant. Traffic sa vracia po vlnách.

Acceptance vyžaduje acquire p95 pod 100 ms, end-to-end p99 pod 2.5 s, žiadnych waiters pri baseline load-e, zachovaný database failure headroom a forbidden load test, pri ktorom application vytvorí controlled overload response namiesto nekonečného waitu alebo connection stormu.

## USE a ostatné metódy

RED začal user operation a lokalizoval medzeru pred database spanom. USE identifikoval pool utilization a saturation. Trace ukázal časovú boundary a config event vysvetlil recent change. Žiadna metóda sama neposkytla celý causal chain.

USE sa vykonáva systematicky nad inventory, aby tím nepozoroval iba známe bottlenecks. CPU, memory, storage, network, connection pools, threads, queues, quotas a external concurrency limits musia mať ownera a evidence source. Resource bez metric môže vyžadovať nový bounded instrumentation contract.

## Kontrolné otázky

1. Prečo vysoká utilization nemusí byť incident?
2. Čo saturation zachytáva navyše oproti utilization?
3. Prečo CPU hosta a cgroup CPU nie sú rovnaký subject?
4. Čo throttling ratio preukazuje a čo ešte treba korelovať?
5. Ako odlíšiš pool bottleneck od pomalej database query?
6. Čo `OOMKilled` dokazuje a čo nepreukazuje?
7. Prečo HPA scale-out môže zhoršiť database incident?
8. Ako sa počíta safe fleet connection budget?
9. Ktoré evidence lokalizovali incident na application pool?
10. Aký forbidden load test uzatvára recovery?

## Oficiálna dokumentácia

- [The USE Method](https://www.brendangregg.com/usemethod.html)
- [Prometheus query functions](https://prometheus.io/docs/prometheus/latest/querying/functions/)
- [Kubernetes resource management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: RED method](red-method.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Golden Signals →](golden-signals.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
