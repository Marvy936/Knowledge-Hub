# Performance, latency, throughput a cost monitoring

Výkon ML systému sa nedá zhrnúť jedným QPS, jedným percentilom ani cenou GPU hodiny. Produkčný outcome vzniká z kombinácie arrival rate, queueing, feature latency, model compute, fallback, downstream capacity a resource cost. Performance monitoring preto musí viazať presný release, traffic population, operation type a business deadline k správnemu denominatoru.

V incidente `MLOPS-PAY-95` tím optimalizoval cenu inference podľa priemernej ceny na request. Scale-to-zero a agresívne batching znížili provisioned GPU hours, no zvýšili cold starts a tail latency. Časť requestov prekročila deadline a prešla na fallback, ktorý bol lacnejší a vracal HTTP 200. Dashboard preto vykázal nižšiu cenu a rovnakú availability, hoci useful model throughput a business outcome sa zhoršili. Správny verdict vyžadoval oddeliť accepted requests, successful model predictions, fallback responses, deadline-successful actions a mature outcomes.

## 1. Exact performance subject

Performance run musí určiť composite release, workload mode, resource profile, traffic model, interval a acceptance policy. Benchmark bez model digestu, serving image, GPU/MIG profilu, batch policy a feature generation sa nedá porovnať s produkciou.

```yaml
performance_run_id: fraud-perf-2026-08-03.5
release_id: fraud-serving-2026-08-03.4
model_digest: sha256:31d7...
runtime_image: registry.example.com/fraud-server@sha256:8ab1...
resource_class: a100-mig-2g-v3
traffic:
  source: production-replay-v7
  arrival_pattern: burst
  request_count: 200000
  input_mix: merchant-segments-v4
serving:
  min_replicas: 2
  max_replicas: 12
  concurrency_target: 1
  batch_policy: dynamic-8-5ms
acceptance:
  deadline_ms: 150
  deadline_success_min: 0.99
  fallback_rate_max: 0.005
```

Configured values nie sú sufficient evidence. Run musí zachytiť resolved replicas, loaded release, actual request distribution, node/resource generation a monitoring coverage.

## 2. Latency decomposition

End-to-end latency sa rozkladá na queue, feature retrieval, preprocessing, batch wait, model compute, postprocessing, policy a downstream action. Zmena jednej vrstvy môže meniť ostatné: pomalší model zvýši concurrency, queue a retry traffic.

```text
end_to_end
= ingress_wait
+ serving_queue
+ feature_latency
+ batch_wait
+ model_compute
+ policy_latency
+ downstream_latency
```

Priemer skrýva tail. SLO používa deadline success a agregovateľné percentily. Prometheus histogram alebo native histogram zachová distribúciu a umožní agregovať replicated instances; priemerovanie per-instance summary quantiles je štatisticky nesprávne.

Cold a warm paths sa reportujú oddelene. Model load, node provisioning a prvá inference patria do cold budgetu. Warm p95 nemôže preukázať scale-to-zero SLO.

## 3. Throughput a useful work

Raw throughput počíta responses za sekundu. Useful throughput počíta operácie, ktoré prešli správnym release, splnili deadline a vyvolali platnú action. Fallback, duplicate retry alebo schema rejection sú samostatné result classes.

```text
accepted requests
→ eligible requests
→ model invocations
→ successful predictions
→ deadline-successful predictions
→ authoritative actions
→ mature successful outcomes
```

Každá konverzia má denominator. Ak sa fallback započíta medzi model successes, škálovanie môže vyzerať úspešne, hoci candidate model už traffic nespracúva.

Training throughput používa samples alebo tokens per second, ale musí reportovať effective global batch, data-loader wait, collective time a convergence evidence. Vyšší step throughput pri zmenenom batch alebo nižšej numerical precision nie je automaticky ekvivalentný training outcome.

## 4. Saturation a queueing

Saturation sa nečíta iba z CPU alebo GPU utilization. Potrebné sú in-flight requests, queue depth, oldest-request age, memory high-water mark, ready replicas, GPU sharing mode a downstream capacity. Queue age je často lepší user-impact signal než samotný queue count.

Littleov zákon pomáha spájať arrival rate, concurrency a response time, ale platí pre stabilný systém a správne ohraničenú population. Pri burstoch, retries alebo dropped trafficu treba pracovať s časovým priebehom a result classes.

Load shedding je súčasť capacity modelu. Explicitné odmietnutie alebo fallback môže chrániť deadline majority trafficu. Monitoring však musí takúto response oddeliť od model success.

## 5. Cost model a allocation

Cost má najmenej štyri vrstvy: provisioned asset cost, allocated Kubernetes resource cost, used resource cost a cost na useful operation alebo outcome. OpenCost definuje vendor-neutral allocation model pre Kubernetes assets a workloads; ML platforma k nemu pridáva model release, operation class a business denominator.

```text
asset cost
→ allocated workload cost
→ used serving/training cost
→ cost per successful prediction
→ cost per authoritative action
→ cost per mature business outcome
```

Idle GPU cost sa nesmie potichu stratiť. Report musí uviesť, či je idle cost oddelený alebo rozdelený medzi workloady. Shared node, MIG a time-slicing vyžadujú transparentnú allocation policy.

Príklad query boundary:

```text
window: 2026-08-03T09:00/10:00
aggregate: namespace, workload, release_id
include_idle: true
currency: EUR
denominator: deadline_successful_model_predictions
```

Cost per request môže klesnúť len preto, že lacný fallback nahradil drahú inference. Preto sa numerator aj denominator segmentujú podľa result class.

## 6. Capacity a cost trade-offs

Zvýšenie `minReplicas` znižuje cold latency, ale zvyšuje idle cost. Väčší batch zvyšuje throughput, ale pridáva queue delay. Time-slicing môže zvýšiť allocation density, ale zhoršiť isolation a tail latency. Rozhodnutie je multi-objective a viaže sa na risk tolerance.

Pareto frontier je užitočnejší než jeden „optimal score“. Candidate konfigurácie sa porovnávajú podľa deadline success, useful throughput, fallback, cost a recovery headroom. Konfigurácia, ktorá je lacnejšia iba pri warm steady trafficu, nemusí byť production winner.

Cost guardrail nesmie automaticky škálovať pod minimálnu safe capacity. FinOps policy je podriadená business a safety SLO, nie naopak.

## 7. Monitoring contract a PromQL

Metric labels musia byť bounded: service, release, revision, result class, coarse segment a resource class. Request ID patrí do trace. Recording rules zachovávajú jednotky a denominators.

```promql
histogram_quantile(
  0.99,
  sum by (le, release_id) (
    rate(ml_inference_latency_seconds_bucket[5m])
  )
)

sum by (release_id) (
  rate(ml_inference_deadline_success_total[5m])
)
/
sum by (release_id) (
  rate(ml_inference_eligible_total[5m])
)
```

Cost a performance windows musia byť časovo kompatibilné. Hodinový cloud allocation nemožno bez vysvetlenia deliť päťminútovým traffic spike denominatorom.

## 8. Failure hypotheses a recovery

Pri zhoršení latency sa skúma traffic mix, queue, feature service, model compute, resource sharing a downstream action. Pri raste cost sa skúma idle allocation, node fragmentation, retries, failed jobs, artifact transfer a fallback. Pri lepšom QPS a horšom outcome sa skúma result-class denominator a policy change.

Containment môže zvýšiť warm capacity, znížiť batch wait, oddeliť noisy tenant, zastaviť rollout alebo aktivovať known-good release. Pred zmenou sa zachytí performance manifest, loaded generation, traffic distribution a cost allocation.

Pozitívna acceptance vyžaduje warm aj cold latency, useful throughput, saturation, fallback a cost na správny denominator. Recovery acceptance vyžaduje ďalšie complete window bez ručnej korekcie. Forbidden acceptance je priemer, raw QPS, cluster utilization alebo cena za HTTP response bez business deadline a result-class evidence.

Second-operation test zopakuje load a cost window s rovnakým immutable subjectom. Ak výsledok závisí od warmed cache, jednorazového idle allocation alebo zmeneného traffic mixu, benchmark nie je reprodukovateľný.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Data drift, concept drift a prediction drift](data-drift-concept-drift-prediction-drift.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Feedback loops a ground-truth delay →](feedback-loops-ground-truth-delay.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
