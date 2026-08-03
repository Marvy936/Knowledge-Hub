# Model monitoring

Model monitoring je evidence systém, ktorý spája serving runtime, vstupné dáta, predikcie, rozhodnutia, fallbacky a neskoré business outcomes pre presnú produkčnú generáciu. Jeho cieľom nie je vyrobiť čo najviac dashboardov, ale odhaliť prvú významnú divergenciu a umožniť containment, reprodukciu a recovery. Monitoring, ktorý nevie povedať, ktorého release, segmentu, request population a časového okna sa metrika týka, môže vytvoriť presvedčivý, ale nesprávny verdict.

V incidente `MLOPS-PAY-94` infra dashboard ukazoval 99.95 % HTTP success a priemernú latency 80 ms. Nezachytával však, že 14 % requestov prekročilo business deadline a prešlo na fallback, pretože fallback response bola HTTP 200. Model dashboard zároveň porovnával prediction distribution candidate release s mesačným training datasetom, ale nemal actual exposure denominator ani oddelené segmenty. Alert na drift preto spustil retraining, hoci prvá divergencia bola GPU queue a fallback. Správny monitoring musel najprv obnoviť request-level release identity, result classes a outcome join.

## 1. Monitoring lifecycle a observation subject

Monitoring začína observation contractom. Každá metrika alebo event musí mať subject, generation, population, event time, processing time, result class a ownership. Pre model serving je základnou jednotkou inference operation, nie Pod ani model name.

```text
request accepted
→ features resolved
→ model invoked
→ prediction produced
→ policy decision
→ action/fallback
→ label alebo business outcome
→ monitoring window materialized
→ alert/verdict
```

Exact observation envelope môže vyzerať takto:

```json
{
  "operation_id": "op-4f93",
  "event_time": "2026-08-03T09:14:22.411Z",
  "release_id": "fraud-serving-2026-08-03.4",
  "model_digest": "sha256:31d7...",
  "revision": "fraud-predictor-00042",
  "feature_generation": "fraud-request-v11",
  "segment": "merchant_online_eu",
  "result_class": "fallback_timeout",
  "prediction": null,
  "action": "rules_review",
  "deadline_ms": 150,
  "latency_ms": 211,
  "trace_id": "ab91...",
  "label_status": "pending"
}
```

Prometheus metrics nebudú niesť `operation_id` ani `trace_id`; tie patria do logu alebo trace. Metrics používajú stabilné, bounded labels ako release, revision, result class a coarse segment. Raw features a osobné údaje podliehajú privacy policy a často sa ukladajú iba ako agregácie, hash/fingerprint alebo pointer do kontrolovaného evidence store.

## 2. Štyri monitoring vrstvy

Platform a resource vrstva sleduje Pod readiness, restarts, CPU, memory, GPU, storage a network. Service vrstva sleduje request rate, error/result classes, queue, latency, saturation a fallback. ML vrstva sleduje schema, feature freshness, missingness, prediction distribution, confidence/calibration proxies a neskôr realized performance. Business vrstva sleduje action distribution, review capacity, fraud loss, conversion, complaint alebo inú doménovú metriku.

Tieto vrstvy sa nesmú zlúčiť do jedného „model health“ semaforu bez vysvetlenia. Zelená infra môže koexistovať s nesprávnymi features. Stabilná prediction distribution môže koexistovať s concept driftom. Zlepšená offline accuracy môže zhoršiť review queue a business outcome.

Authority hierarchy pri incidente je:

```text
business outcome a action ledger
→ request-correlated inference/fallback evidence
→ feature a prediction events
→ serving/runtime metrics
→ control-plane status
```

Nižšia vrstva pomáha lokalizovať mechanizmus, ale vyššia rozhoduje, či user journey funguje.

## 3. Metrics, logs a traces

Metrics sú vhodné pre agregácie a alerting. Logs nesú diskrétne udalosti a vysokodimenzionálny context. Traces spájajú latency a causality cez feature service, model runtime, policy engine a downstream action. Jeden signál nenahrádza ostatné.

Prometheus histogram je vhodný pre agregovateľnú latency distribution. Pri replicated službe sa pre percentily nemajú priemerovať prepočítané quantiles zo summaries. Histogram umožní agregovať buckets alebo native histogram samples podľa release a result class.

Príklady PromQL:

```promql
sum by (release_id, result_class) (
  rate(ml_inference_requests_total[5m])
)

histogram_quantile(
  0.95,
  sum by (le, release_id) (
    rate(ml_inference_latency_seconds_bucket[5m])
  )
)

sum(rate(ml_inference_fallback_total[5m]))
/
sum(rate(ml_inference_requests_total[5m]))
```

Pri native histograms sa query prispôsobí použitému metric type. Recording rules majú zachovať denominator a unit. Alert `fallback_rate > 0.01` musí definovať minimálny traffic, window a excluded planned tests; inak bude pri malom počte requestov hlučný.

Log event musí byť idempotentný alebo deduplikovateľný. Retry inference loggera nesmie vytvoriť dvojité denominátory. Trace sampling musí zachovať errors, fallback a tail latency s vyššou prioritou než náhodné healthy requesty.

## 4. Result classes a denominator discipline

HTTP status nie je ML result class. Úspešná fallback response, abstention, schema rejection alebo stale-feature response môže byť HTTP 200, no má odlišný business význam. Monitoring contract preto používa mutually exclusive result classes:

```text
model_success
fallback_timeout
fallback_runtime_error
abstain_low_confidence
rejected_schema
rejected_policy
action_suppressed_capacity
```

Každá rate metrika musí mať denominator, ktorý zodpovedá otázke. Model error rate používa model invocations; end-to-end failure rate používa eligible business requests; label coverage používa exposed operations, ktoré mali do daného času dostať mature label. Zmiešanie denominátorov je častý zdroj falošného zlepšenia.

Actual exposure sa meria podľa requestov, ktoré candidate skutočne spracoval, nie podľa configured traffic percentage. Pri canary a A/B teste sa monitorujú eligible, assigned, routed, successfully scored a actioned populations oddelene.

## 5. Latency, throughput, saturation a cost

End-to-end latency sa rozkladá na routing/queue, feature fetch, preprocessing, model compute, postprocessing, policy a downstream action. Bez rozkladu môže tím škálovať model server, hoci bottleneck je feature store.

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

SLO používa deadline success a tail percentily, nie iba priemer. Throughput sa meria ako successful useful operations, nie všetky HTTP responses. Saturation zahŕňa queue age, concurrency, GPU memory a review capacity. Cost sa viaže na úspešnú inference alebo business action; cena za provisioned GPU hodinu bez traffic denominatora nevysvetľuje efektivitu.

Cold a warm paths sa oddeľujú. Scale-to-zero cold request môže byť malý podiel trafficu, ale dominantný podiel user-visible failures. Monitoring musí reportovať model load duration, first prediction a reason for cold activation.

## 6. Data a prediction evidence bez labels

Pred príchodom labels možno sledovať schema violations, missingness, ranges, category novelty, feature freshness, input distribution a prediction distribution. Tieto signály sú diagnostické, nie priamy dôkaz performance.

Reference population musí byť explicitná: training, validation, posledné stable production window alebo seasonally matched window odpovedajú na odlišné otázky. Monitoring run zaznamená reference dataset version, current interval, transform generation, segmentation a statistical method.

Prediction monitoring zahŕňa score distribution, class/action rate, confidence alebo abstention a calibration proxy, ak je dostupná. Zmena môže byť spôsobená data driftom, policy zmenou, feature outage, traffic mixom alebo reálnou zmenou prevalence. Automatický retrain iba na základe prediction drift alertu je forbidden action.

## 7. Ground truth, delayed labels a realized performance

Realized performance vyžaduje join prediction s mature labelom. Join používa stable operation/entity identity, event-time semantics, label source a maturity rule. Label, ktorý príde po troch dňoch, nesmie byť považovaný za missing v hodinovom window bez maturity adjustment.

Coverage sa reportuje:

```text
eligible predictions
→ labels expected by maturity cutoff
→ labels observed
→ labels valid
→ predictions successfully joined
```

Performance metric bez coverage a segment breakdown môže byť selektívne skreslená. Napríklad fraud labels vznikajú rýchlejšie pri manuálne reviewovaných prípadoch než pri automaticky schválených. Monitoring preto sleduje label propensity a action-conditioned coverage.

Champion a candidate sa porovnávajú na rovnakej exposure population alebo pomocou správne navrhnutého experimentu. Nezávislé časové okná môžu zamieňať seasonality za model difference.

## 8. Alert design a ownership

Alert musí viesť k akcii. Každý alert má ownera, severity, observation subject, threshold/window, minimum sample, runbook a containment. Page alerty sa rezervujú pre user-visible impact alebo bezprostredné riziko. Drift alebo label coverage môže byť ticket, ak nevyžaduje okamžitý zásah.

Príklad alert contractu:

```yaml
alert: FraudServingFallbackHigh
subject:
  service: fraud
  release_scope: loaded
condition:
  metric: fallback_rate
  threshold: 0.01
  window: 10m
  minimum_requests: 500
for: 5m
owner: fraud-platform-oncall
containment:
  - freeze rollout
  - verify queue and GPU capacity
  - route to known-good release if deadline impact persists
```

Multi-window burn-rate alerting je vhodnejšie než jeden statický threshold pre SLO, pretože rozlišuje rýchly a pomalý burn. ML-specific alert musí byť korelovaný so service a business signals, aby sa zabránilo retrainingu počas infra incidentu.

## 9. Monitoring pipeline reliability

Monitoring samotný môže zlyhať. Logger môže dropovať events, metrics scrape môže mať gap, join pipeline môže lagovať a dashboard môže použiť starú recording rule. Preto sa sleduje telemetry coverage, ingestion delay, duplicate rate, schema errors a last successful materialization timestamp.

Absencia alertu nie je dôkaz zdravia, ak monitoring pipeline nebeží. Exportovať timestamp posledného úspešného update a počítať age v query je bezpečnejšie než exportovať „seconds since“, ktorých updater sa môže zastaviť.

Monitoring changes sú verzované. Nové buckets, segment definitions alebo label maturity menia interpretáciu metrík. Dashboard a alert generation sa preto viažu na monitoring contract version, aby sa historické porovnania neprezentovali ako identické.

## 10. Troubleshooting, recovery a acceptance

Pri alert-e sa najprv overí telemetry freshness a denominator. Potom sa nájde prvá divergence medzi eligible traffic, routed requests, model invocations, result classes, actions a outcomes. Až následne sa skúmajú resources, features, model alebo policy.

Containment môže byť freeze rollout, zvýšenie ready capacity, vypnutie chybnej feature, fallback na known-good release alebo obmedzenie action. Pred reštartom sa uloží monitoring snapshot, request traces a loaded generation map.

Pozitívna acceptance vyžaduje request-correlated release identity, bounded metric labels, explicitné result classes, correct denominators, telemetry coverage a aspoň jeden end-to-end synthetic journey. Recovery acceptance vyžaduje návrat service aj business metrics a dobehnutie delayed label pipeline. Forbidden acceptance je zelený dashboard bez overenia freshness alebo model accuracy z neúplných labels.

Second-operation test overí ďalšie monitoring window po recovery. Ak prvé window bolo správne iba kvôli manuálnemu backfillu, ale ďalšie znovu stratí events alebo joins, recovery nie je uzavretá. Stabilný monitoring musí reprodukovať metrics, alert verdict a evidence linkage bez ručnej opravy.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: GPU scheduling, utilization a capacity](gpu-scheduling-utilization-capacity.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Data drift, concept drift a prediction drift →](data-drift-concept-drift-prediction-drift.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
