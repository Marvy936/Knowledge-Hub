# Model serving a autoscaling

Model serving je produkčný runtime, ktorý načíta presnú modelovú generáciu, prijíma inference požiadavky a vracia predikcie v rámci dohodnutého latency, availability a correctness kontraktu. Autoscaling je iba mechanizmus, ktorým platforma mení počet alebo veľkosť serving replík podľa pozorovaného zaťaženia. Nezaručuje, že replika načítala správny model, že request dostal správne features ani že škálovanie stihlo absorbovať burst pred vypršaním business deadline.

V incidente `MLOPS-PAY-94` bol nový fraud model nasadený ako KServe `InferenceService`. Control plane hlásil Ready a pri nulovej prevádzke sa deployment zmenšil na nulu. Prvý ranný burst preto čakal na node scale-up, image pull, model download a GPU initialization. Autoscaler zároveň používal request concurrency, hoci jedna replika dokázala bezpečne spracovať iba dve súbežné GPU batches. Pri nastavení `containerConcurrency: 16` sa požiadavky síce prijímali, ale hromadili sa v runtime queue, prekračovali deadline a prechádzali na fallback. Dashboard ukazoval rast replík a zelenú availability, no business cesta používala prevažne fallback model. Root cause preto nebol „autoscaler nefunguje“, ale nesprávne definovaný serving subject, neúplný capacity model a chýbajúci dôkaz o loaded a exercised generation.

## 1. Serving lifecycle a authoritative subject

Serving lifecycle začína immutable release manifestom, nie názvom modelu alebo Registry aliasom. Manifest musí určiť model package digest, serving image digest, runtime a protocol generation, feature contract, preprocessing/postprocessing code, fallback policy, resource profile a rollout identity. Až z tohto subjectu môže control plane vytvoriť desired state a platforma resolved workload.

```text
release manifest
→ desired InferenceService
→ resolved Deployment/Revision
→ scheduled Pod
→ image a model bytes loaded
→ runtime initialized
→ readiness gate passed
→ request routed
→ feature contract applied
→ prediction returned
→ action alebo fallback
→ business outcome
```

Jednotlivé kroky majú odlišnú authority. Registry potvrdzuje model version a metadata. OCI registry potvrdzuje serving image bytes. Kubernetes API potvrdzuje desired a observed workload state. Runtime endpoint alebo loaded-model metric potvrdzuje, čo proces skutočne načítal. Request trace potvrdzuje, ktorou revision požiadavka prešla. Business systém potvrdzuje, či prediction vyvolala očakávanú action. Žiadna z týchto vrstiev sama osebe nepreukazuje celý outcome.

Praktický release manifest môže vyzerať takto:

```yaml
release_id: fraud-serving-2026-08-03.4
model:
  registry_name: fraud-prod
  version: 184
  package_digest: sha256:31d7...
serving:
  image: registry.example.com/fraud-server@sha256:8ab1...
  runtime: sklearnserver-0.17.0
  protocol: kserve-v2
  min_replicas: 2
  max_replicas: 12
  container_concurrency: 2
  target_concurrency: 1
features:
  service: fraud-request-v11
  fallback_policy: rules-v6
resources:
  accelerator: nvidia.com/gpu
  profile: mig-2g.20gb
acceptance:
  warm_p95_ms: 120
  cold_p99_ms: 4000
  fallback_rate_max: 0.005
```

Mutable alias ako `models:/fraud@champion` môže byť promotion control, ale deployment ho musí pri vytvorení rozlíšiť na immutable version a digest. Ak si každá replika rieši alias sama pri štarte, rolling update alebo restart môže vytvoriť mixed generation bez zmeny Kubernetes manifestu.

## 2. KServe deployment modes a resolved runtime

KServe oddeľuje control plane od data plane. `InferenceService` je desired-state API, z ktorého controller vytvorí konkrétne runtime objekty. Presné objekty a autoscaling semantics závisia od deployment mode. Serverless mode typicky používa Knative revision a Knative Pod Autoscaler; standard mode používa Kubernetes `Deployment`, `Service` a HPA alebo podľa konfigurácie ďalšie autoscaling integrácie. Prevádzkový runbook preto nesmie hovoriť iba „KServe autoscaler“. Musí pomenovať mode, controller, metric source, target a scale-to-zero semantics.

Príklad serverless predictive služby s explicitným concurrency kontraktom:

```yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: fraud
  namespace: ml-prod
  annotations:
    serving.kserve.io/deploymentMode: Serverless
    autoscaling.knative.dev/metric: concurrency
    autoscaling.knative.dev/target: "1"
spec:
  predictor:
    minReplicas: 2
    maxReplicas: 12
    containerConcurrency: 2
    model:
      modelFormat:
        name: sklearn
      storageUri: s3://ml-artifacts/fraud/184/
      resources:
        limits:
          cpu: "4"
          memory: 8Gi
```

`containerConcurrency` je hard limit prijímaných súbežných requestov na repliku. Autoscaler target je žiadaná prevádzková úroveň, pri ktorej má škálovať. Ak je hard limit vyšší než reálna runtime capacity, requesty sa môžu dostať do podu, ale stráviť väčšinu deadline v internej queue. Ak je target príliš nízky, systém môže vytvárať zbytočné repliky a zvyšovať GPU cost. Hodnota sa preto neurčuje z CPU aplikácie ani podľa počtu worker threads, ale load testom presného modelu, batcheru, GPU profilu a request distribution.

Resolved stav sa kontroluje cez viac vrstiev:

```bash
kubectl -n ml-prod get inferenceservice fraud -o yaml
kubectl -n ml-prod get revisions,deployments,pods -l serving.kserve.io/inferenceservice=fraud
kubectl -n ml-prod describe pod <pod>
kubectl -n ml-prod logs <pod> --all-containers
```

Readiness musí zahŕňať model load a runtime initialization. TCP socket alebo HTTP process health pred dokončením model loadu vytvára false-ready okno. Pri remote-loaded modeloch je potrebné logovať package digest a úspešnú checksum verifikáciu, nie iba storage URI.

## 3. Capacity model: arrival rate, service time a concurrency

Autoscaling potrebuje merateľnú väzbu medzi trafficom a kapacitou. Základný model používa arrival rate \(\lambda\), priemerný alebo distribučný service time \(S\) a efektívnu concurrency \(C\). Littleov zákon \(L = \lambda W\) pomáha vysvetliť, prečo rast počtu in-flight requestov môže byť dôsledok pomalšieho service time, nie iba vyššieho arrival rate. Pri GPU serving navyše service time závisí od batch size, input shape, memory pressure, model warmup a zdieľania akcelerátora.

Kapacita replík sa nemeria jedným maximálnym QPS. Potrebné sú aspoň tieto režimy: steady warm traffic, cold start, burst, mixed input sizes, downstream feature latency, partial dependency failure a fallback. Každý režim musí reportovať throughput, queue time, compute time, end-to-end latency, error a fallback rate, memory high-water mark a cost na úspešnú inference.

Príklad load-test acceptance:

```text
warm steady:
  2 concurrent requests per replica
  p95 end-to-end <= 120 ms
  p99 queue <= 25 ms
  fallback <= 0.5 %

burst:
  20× arrival rate for 90 s
  no OOM
  deadline success >= 99 %
  replicas converge <= 60 s

cold:
  image cached and uncached measured separately
  model download checksum verified
  first successful prediction <= 4 s
```

Average latency nie je dostatočný dôkaz. Dlhý tail môže aktivovať retries, zvýšiť concurrency a vytvoriť pozitívnu spätnú väzbu. Preto sa latency instrumentuje histogramom a analyzuje podľa revision, result class a request size bucket. Request ID alebo entity ID nesmie byť Prometheus label, pretože by vytvoril neobmedzenú cardinality; patrí do trace alebo logu.

## 4. Scale to zero a cold-start budget

Scale to zero je cost optimization s explicitným availability trade-offom. Pri `minReplicas: 0` môže prvý request čakať na aktiváciu revision, scheduling, image pull, storage download, model deserializáciu, CUDA context a warmup. Ak cluster autoscaler zároveň musí pridať GPU node, cold start môže byť rádovo dlhší než samotná inference.

Cold-start budget sa rozkladá:

```text
request activation
+ queue to schedulable capacity
+ node provisioning
+ image pull
+ model artifact transfer
+ checksum a deserialization
+ accelerator initialization
+ warmup
= first useful prediction
```

Nie všetky kroky rieši pod autoscaler. KPA alebo HPA môže žiadať viac replík, ale nepridá GPU node okamžite, neoptimalizuje artifact locality a nevie, či model warmup potrebuje reprezentatívny input. Preto treba oddeliť pod autoscaling od node autoscaling a artifact-distribution stratégie.

Produkčná služba s tvrdým subsekundovým deadline zvyčajne potrebuje nenulové `minReplicas`, prewarmed pool alebo explicitný fallback. Scale to zero môže byť vhodný pre interné, asynchrónne alebo low-traffic endpointy, ak business akceptuje cold latency. Zakázaná acceptance je označiť scale-to-zero službu za SLO compliant iba podľa warm benchmarku.

## 5. Autoscaling metrics a control-loop stability

Autoscaler je feedback controller. Meria signal, porovnáva ho s targetom, vypočíta desired replicas a po oneskorení pozoruje nový stav. Nestabilita vzniká, keď signal nereprezentuje bottleneck, sampling window je príliš krátke, startup je pomalší než control period alebo viac controllerov mení tú istú kapacitu.

CPU môže byť pre GPU inference slabý signal: pod má nízke CPU, ale GPU queue je plná. GPU utilization môže byť tiež zavádzajúca: vysoká utilization môže znamenať efektívnu saturáciu, no nízka utilization môže byť dôsledok memory-bound modelu, malých batchov alebo čakania na features. Pre praktický scaling contract sa kombinujú request concurrency alebo queue depth s deadline success a GPU/memory headroom.

Custom metric musí mať jasný denominator. `queue_depth=40` bez počtu replík, request age a service rate nehovorí, či treba jednu alebo desať replík. Dobré recording rules vytvárajú signály ako queue na ready repliku, oldest request age alebo utilization podľa loaded release.

Osciláciu obmedzujú stabilization windows, rate limits, min/max replicas a oddelenie emergency load shedding od bežného scalingu. Pri náhlom overload-e je často bezpečnejšie odmietnuť časť requestov s explicitným retry-after alebo použiť známu fallback cestu, než pripustiť neobmedzenú queue, ktorá zničí deadline všetkých requestov.

## 6. Model loading, batching a request correctness

Serving runtime môže používať dynamic batching. Batcher čaká krátke okno, zoskupí kompatibilné requesty a vykoná jednu akcelerovanú operáciu. Vyšší batch zvyšuje throughput, ale pridáva queue delay a môže prekročiť GPU memory. Batch policy je preto súčasť release generation.

Request correctness zahŕňa schema, dtype, shape, units a semantic constraints. V2 inference protocol môže overiť tensor names a shapes, ale nezistí, že suma je v centoch namiesto eur alebo timestamp v processing time namiesto event time. Tieto kontroly patria do feature a request contractu.

Každá response by mala niesť alebo umožniť dohľadať:

```json
{
  "request_id": "req-8d1",
  "release_id": "fraud-serving-2026-08-03.4",
  "model_version": "184",
  "model_digest": "sha256:31d7...",
  "revision": "fraud-predictor-00042",
  "feature_generation": "fraud-request-v11",
  "fallback_used": false,
  "prediction": 0.873,
  "latency_ms": 82
}
```

Citlivé features sa nemusia logovať v surovej forme. Stále však treba request-correlated fingerprint, schema verdict a lineage pointer, aby sa dala reprodukovať alebo aspoň ohraničiť konkrétna inference.

## 7. Failure hypotheses a troubleshooting

Pri raste latency sa hypotézy delia podľa prvej divergencie. Ak request čaká pred podom, skúma sa routing, activator, queue proxy, autoscaler a schedulable capacity. Ak čaká v pode, skúma sa runtime queue, batching a worker concurrency. Ak compute čas rastie, skúma sa GPU sharing, memory pressure, input shape a kernel behavior. Ak inference je rýchla, ale end-to-end cesta pomalá, príčina môže byť feature service, policy engine alebo downstream action.

Praktický read-back:

```bash
kubectl -n ml-prod get inferenceservice fraud \
  -o jsonpath='{.status.conditions}'

kubectl -n ml-prod get pods \
  -l serving.kserve.io/inferenceservice=fraud -o wide

kubectl -n ml-prod top pod
kubectl -n ml-prod logs <pod> -c kserve-container --since=15m
```

K týmto údajom sa pripájajú Prometheus latency/queue metrics, GPU telemetry a request traces. Restart podu pred zachytením loaded digest, queue state a GPU metrics môže odstrániť rozhodujúci dôkaz. Recovery preto začína containmentom: zastavenie rollout-u, zníženie trafficu, aktivácia fallbacku alebo zvýšenie `minReplicas`, nie slepým restartom všetkých replík.

## 8. Recovery a acceptance

Component recovery potvrdzuje, že nová alebo rollback replika načítala správny package digest, readiness je pravdivá a syntetická inference prešla. Journey recovery potvrdzuje feature fetch, model prediction, policy action a fallback semantics na reprezentatívnych requestoch. Business recovery sleduje deadline success, action distribution a mature outcome.

Pozitívna acceptance vyžaduje, aby všetky ready repliky reportovali rovnaký release fingerprint, warm aj cold SLO boli merané, autoscaling target zodpovedal load-test capacity a burst nespôsobil neobmedzený fallback. Recovery acceptance vyžaduje rollback celého composite release a následný second-operation test. Forbidden acceptance je `InferenceService Ready`, počet replík alebo priemerná latency bez request-correlated evidence.

Druhý apply rovnakého immutable manifestu musí byť no-op. Druhý syntetický request musí prejsť bez opätovného model downloadu alebo neočakávaného cold pathu. Ak sa alias, storage URI alebo runtime dependency medzi operáciami zmení, release nebol reprodukovateľný a nemožno ho označiť za stabilný.
