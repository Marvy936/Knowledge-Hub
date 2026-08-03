# KServe alebo ekvivalentný Kubernetes model serving

KServe rozširuje Kubernetes o model-serving control plane. `InferenceService` vyjadruje desired serving intent, `ServingRuntime` alebo `ClusterServingRuntime` určuje runtime implementation a data plane obsluhuje skutočné inference requests. Produkčný dôkaz nevzniká vytvorením CRD ani stavom `Ready`; vzniká až vtedy, keď všetky relevantné repliky načítajú presnú composite release, prejdú warmupom, odpovedia podľa protocol contractu a zvládnu traffic v rámci latency, capacity a business boundaries.

V incidente `MLOPS-PAY-97` tím presunul classifier z Knative mode do Standard deployment mode, ale ponechal annotations a rollout očakávania zo starého režimu. `InferenceService` bol `Ready`, no HPA škáloval podľa CPU namiesto queue pressure, jedna replica načítala model z mutable `storageUri` po prepise a canary traffic sa vyhodnocoval podľa configured percenta, nie actual exposure. Pri rollbacku sa zmenil CRD, ale dve staré Pods zostali v service endpoints počas drainu. Root cause bolo zamieňanie control-plane intentu, resolved Kubernetes resources, loaded runtime generation a data-plane outcome.

## 1. Composite serving subject

Model serving subject zahŕňa viac než model URI. Runtime image, protocol, transformer, resource profile, deployment mode, autoscaling, networking a policy môžu zmeniť behavior.

```yaml
serving_subject:
  release_id: fraud-serving-2026-08-03.12
  model_digest: sha256:model...
  runtime_image: registry.example/sklearn-runtime@sha256:...
  runtime_name: kserve-sklearn
  protocol: v2
  transformer_image: registry.example/fraud-transformer@sha256:...
  feature_generation: fraud-features-v14
  deployment_mode: Standard
  resource_profile: gpu-none-cpu-4
  autoscaling_policy: fraud-serving-hpa-v6
  routing_policy: fraud-canary-v4
```

Mutable `storageUri`, runtime tag alebo ConfigMap mení subject aj bez zmeny `InferenceService` name. Release manifest sa preto rozlíši pred deployom a jeho digest sa loguje do Pod annotations, responses alebo trace contextu.

## 2. Control plane a data plane

KServe control plane reconciliuje CRDs do Kubernetes a networking resources. Data plane zahŕňa predictor, prípadný transformer/explainer, model runtime, sidecars a request path.

```text
InferenceService desired state
→ controller-resolved Deployment/Service/Revision
→ scheduled Pods a storage initialization
→ runtime model load
→ readiness a warmup
→ routed request
→ prediction alebo explicit fallback/error
→ business action
```

CRD `Ready=True` je control-plane evidence. Neoveruje, že všetky replicas majú rovnaký model digest, že external feature store je healthy ani že request dokončí business deadline.

## 3. Deployment modes

Aktuálny KServe rozlišuje Standard deployment mode a Knative mode. Standard používa bežné Kubernetes Deployments, Services a networking, typicky HPA a voliteľne KEDA. Je odporúčaný pre väčšinu production a LLM workloads, najmä pri persistent connections, predvídateľnom pod lifecycle a bez scale-to-zero cold pathu.

Knative mode používa Knative Service/Revision, queue proxy, request-driven autoscaling a native scale-to-zero. Prináša revision a traffic-splitting semantics, ale aj cold start, ďalší network hop a vyššiu operational complexity.

Mode je súčasť acceptance. Konfigurácia alebo runbook z jedného režimu sa neprenáša automaticky do druhého. Canary, autoscaling metrics, readiness path, queueing a rollback musia byť overené pre konkrétny mode a KServe version.

## 4. InferenceService a immutable model load

Základný predictive deployment môže vyzerať takto:

```yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: fraud-classifier
  namespace: fraud-prod
  annotations:
    serving.kserve.io/deploymentMode: Standard
spec:
  predictor:
    model:
      modelFormat:
        name: sklearn
      runtime: kserve-sklearn
      storageUri: s3://ml-models/fraud/184/
      resources:
        requests:
          cpu: "2"
          memory: 4Gi
        limits:
          cpu: "4"
          memory: 8Gi
    minReplicas: 3
    maxReplicas: 20
```

Príklad ukazuje interface, nie kompletnú production policy. `storageUri` musí smerovať na immutable prefix alebo obsahovať manifest s digestom. Storage initializer alebo runtime overí bytes pred readiness. Model load failure nesmie skončiť fallbackom na starý local file bez explicitného result classu.

## 5. ServingRuntime authority

`ServingRuntime` definuje model format support, container image, commands, ports a runtime behavior. Cluster-wide Runtime je shared platform authority. Jeho mutable update môže zmeniť mnoho InferenceServices naraz.

Runtime sa versionuje rovnako prísne ako application image. Deployment evidence zachytí selected Runtime name, generation, image digest a resolved Pod template. Admission policy môže zakázať mutable tags, privileged containers alebo nepovolené model formats.

Custom runtime potrebuje protocol conformance, health/readiness, graceful shutdown, model-load metrics, request limits a supply-chain evidence. „Container odpovedá na curl“ nie je ekvivalent KServe-compatible runtime.

## 6. Protocol a schema

Predictive serving používa štandardizovaný inference protocol, napríklad V2. Request/response schema, datatype, tensor shape, missing behavior a error mapping sú contract. Transformer môže meniť raw business input na tensor a output späť na domain response; tým sa stáva súčasťou model behavior a release identity.

Schema validation prebieha pred drahým inference. Invalid request má explicitnú 4xx class, nie HTTP 200 s nulovým prediction. Response obsahuje model/release identity alebo ju trace zachytí mimo user payloadu.

## 7. Readiness, startup a warmup

Kubernetes startup/readiness probes musia rozlišovať process alive od model loaded. Veľký model môže mať dlhý download a initialization. Startup probe chráni pred predčasným restartom; readiness odstráni Pod z trafficu, kým model a dependencies nie sú usable.

Warmup vykoná representative synthetic requests a môže naplniť kernel, graph alebo model caches. Readiness pred warmupom môže poslať prvý production request do cold pathu. Pri LLM workload-e sa meria model download, engine initialization, KV cache setup a first-token latency oddelene.

## 8. Autoscaling a useful capacity

Standard mode typicky používa HPA/KEDA; Knative mode KPA a queue proxy. CPU utilization nemusí korelovať s GPU alebo token-serving saturation. Scale metric sa vyberá podľa bottlenecku: concurrency, queue depth, request rate, token throughput, GPU utilization alebo custom capacity signal.

Replica capacity sa meria load testom pre konkrétny release, resources, batching a request mix. Autoscaler target pod physical saturation ponecháva headroom pre tail latency. Min replicas sa nastavujú podľa availability a cold-start budgetu. Scale-to-zero je vedomý business trade-off, nie bezplatná optimalizácia.

## 9. Networking a actual exposure

Gateway API, Ingress alebo Knative networking vytvárajú odlišný request path. TLS termination, auth, retries, timeouts a body limits musia byť zahrnuté v end-to-end teste. Service-level success bez ingress testu nepreukazuje client journey.

Canary alebo A/B vyhodnotenie používa actual exposure: requesty, ktoré naozaj dosiahli candidate a dostali jeho action. Configured 10 % nie je denominator, ak retries, sticky routing, eligibility alebo failed Pods zmenili distribution.

## 10. Transformer, explainer a InferenceGraph

Transformer a explainer sú samostatné execution units, nie dekorácie. Ich image, schema, latency a failure mode patria do composite release. Failure transformera môže obísť predictor alebo vrátiť fallback; monitoring preto používa result classes pre každý stage.

`InferenceGraph` môže skladať sequence, switch, ensemble alebo splitter behavior. Graph status nepreukazuje semantic compatibility medzi nodes. Každá edge potrebuje input/output contract, timeout a partial failure policy. Cyklus alebo unbounded fan-out sa nesmie skryť za „model orchestration“.

## 11. Observability

Per-request evidence zahŕňa release ID, runtime, result class, latency stages, queue time, batch size a actual routing variant. Prometheus labels zostávajú bounded; request ID ide do trace/log. Model-load digest a Pod generation sa exportujú ako info metric alebo inventory, nie high-cardinality label na každom sample.

Sleduje sa control plane reconciliation, pending Pods, image/model download, readiness flaps, queue depth, saturation, fallback, schema errors, timeout, OOM a telemetry loss. KServe metrics bez business outcome sú service evidence, nie model-quality proof.

## 12. Rollout a rollback

Rollout začína immutable candidate release a known-good control. Standard a Knative mode majú odlišnú traffic a revision mechaniku. Platforma najprv testuje shadow alebo synthetic path, potom bounded exposure a až potom plnú promotion.

Rollback mení routing/deployment desired state, ale recovery sa potvrdí až po endpoint convergence, loaded fingerprint parity a draining starých connections. Side effects vytvorené candidate modelom sa samostatne reconciliujú. Registry alias change bez KServe data-plane read-back nie je rollback.

## 13. Failure hypotheses

`Ready=False` môže znamenať invalid CRD, Runtime resolution, storage credentials, image pull, insufficient resources alebo probe failure. `Ready=True` s chybami môže znamenať schema mismatch, wrong model bytes, transformer failure, downstream dependency, overload alebo network timeout.

Mixed predictions medzi replicas indikujú mutable storage, partial rollout, stale cache alebo inconsistent Runtime. High p99 pri nízkom CPU môže byť queueing, GPU saturation, batch wait, model GC, network alebo cold path. Troubleshooting začína release a Pod fingerprints, nie všeobecným `kubectl restart`.

## 14. Recovery a acceptance

Containment zastaví traffic increase, zachová failed Pod/log evidence a môže route-nuť na known-good revision. Recovery znovu aplikuje immutable release, overí Runtime/image/model digests, warmup, synthetic request, bounded traffic a mature outcomes.

Pozitívna acceptance vyžaduje mode-specific control-plane convergence, loaded parity, protocol/schema test, capacity a autoscaling evidence, actual exposure, result classes a business verification. Forbidden acceptance je CRD `Ready`, existence Service, HTTP 200 health alebo configured canary percent bez loaded a request evidence.

Second-operation test opakovane aplikuje rovnaký release manifest. Reconciliation musí byť no-op a všetky Pods musia zostať na rovnakých digests. Druhý synthetic/load test nesmie závisieť od starej local cache alebo prepisovaného model URI.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Kubeflow Trainer a distributed training](kubeflow-trainer-distributed-training.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Amazon SageMaker a cloud MLOps mapping →](amazon-sagemaker-cloud-mlops-mapping.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
