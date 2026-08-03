# Batch, online a streaming inference

Batch, online a streaming inference používajú fitted model na nové observations, ale majú odlišnú operation identity, latency, ordering, state, retry a evidence semantics. Rovnaké model weights preto nevytvárajú automaticky rovnaký systém. Batch job môže spracovať immutable snapshot s hodinovou latenciou, online endpoint musí odpovedať pre jeden request v milisekundách a streaming consumer spracúva nekonečný event flow s watermarkmi, duplicates a out-of-order events.

Platform tím musí odlíšiť model package od inference mode a business actionu. HTTP 200 z online servera, `Job Complete` pri batchi alebo committed offset pri streame dokazujú inú vrstvu. Žiadny z týchto statusov sám nepotvrdzuje správne features, prediction, downstream action ani mature outcome.

Incident `MLOPS-PAY-93` pokračuje tromi odlišnými prejavmi. Nightly batch scoring čítal snapshot podľa processing time a zahrnul operácie po business cutoff-e. Online endpoint pri timeout-e feature store použil fallback s inou units transformáciou. Streaming consumer po rebalance znovu spracoval events a dvakrát vytvoril review action, pretože prediction bola idempotentná, ale downstream mutation nie. Všetky tri paths používali model 141, no vytvárali rozdielne business výsledky.

## 1. Spoločný inference lifecycle

```text
observation identity
→ feature retrieval alebo transform
→ model package a runtime
→ prediction request
→ raw output
→ postprocessing a policy
→ business action
→ telemetry, reconciliation a outcome
```

Inference mode mení spôsob, akým observation vstupuje do lifecycle-u. Batch používa collection a interval, online používa request/response operation a streaming používa event, partition, offset a event time. Exact subject musí túto identitu zachovať až po action.

## 2. Exact inference subject

```yaml
inference_subject: MLOPS-PAY-INF-2026-08-r31
model_digest: sha256:6a11...90fd
serving_image: sha256:91ce...101a
feature_service: risk_features_v7
policy_digest: sha256:2f91...0aa7
mode: online
observation_unit: payment_operation_id
request_schema: risk-request-v6
response_schema: risk-response-v4
fallback_policy: fail-closed-to-manual-review-v3
```

Batch subject pridáva logical interval, input manifest a output partition. Streaming subject pridáva topic, partition, offset range, event-time watermark, consumer-group generation a idempotency key. Bez týchto polí sa retry a reconciliation nedajú bezpečne vykonať.

## 3. Batch inference

Batch inference spracúva bounded collection. Vhodná je pre periodic scoring, backfill, large offline enrichment alebo prípady, kde latency nie je request-level požiadavka. Batch job potrebuje immutable input manifest a logical interval; directory path alebo SQL query bez snapshotu nestačí.

```yaml
batch_operation: risk-score-2026-08-02-v3
input_manifest: sha256:992a...113e
logical_interval:
  start: 2026-08-02T00:00:00Z
  end_exclusive: 2026-08-03T00:00:00Z
model_digest: sha256:6a11...90fd
output_prefix: s3://ml-prod/predictions/risk-score-2026-08-02-v3/
expected_rows: 1829944
```

Kubernetes Job success preukazuje, že Pod-y skončili podľa controller semantics. Output acceptance potrebuje row count, unique observation IDs, checksums, schema, rejected-record ledger a second-run behavior. Pri parallel batchi sa shards publikujú do temporary paths a canonical manifest vznikne až po kompletnosti.

Retry celého batch jobu môže duplikovať output alebo downstream actions. Content-addressed output a operation ledger umožňujú no-op alebo safe replacement. Partial output sa nesmie javiť ako complete iba preto, že prefix existuje.

## 4. Online inference

Online inference obsluhuje individuálny request s nízkou latency. Request potrebuje operation ID, authenticated caller, deadline, feature timestamps a release fingerprint. Server musí vedieť odmietnuť incompatible schema skôr, než vytvorí nejasnú prediction.

```http
POST /v2/models/risk/infer
X-Operation-Id: payment-8891-risk-r31
X-Release-Subject: MLOPS-PAY-RISK-PROD-2026-08-r31
Content-Type: application/json
```

KServe a ďalšie runtimes používajú štandardizované inference protocols; KServe dokumentácia odporúča V2 pre lepšiu štandardizáciu a performance, zatiaľ čo V1 zostáva dostupný pre flexibilnejšie schemas. Protocol choice je súčasť release contractu, pretože clients, batching a error semantics sa líšia.

Deadline budget sa rozdelí medzi gateway, feature retrieval, preprocessing, model compute, postprocessing a downstream policy. Server-side timeout nemusí znamenať, že caller request neprijal alebo že downstream action nevznikla. Prediction a business mutation majú oddelené idempotency keys.

## 5. Online fallback a degradation

Feature timeout, model load failure alebo resource saturation potrebuje explicitný fallback. Fallback môže odmietnuť request, použiť last-known features, baseline rules alebo poslať prípad na manuálny review. Každý variant má inú risk a musí byť samostatne evaluovaný.

Tichá default value je nebezpečná, pretože endpoint zostane green a prediction distribution sa zmení. Response a telemetry preto obsahujú fallback reason, feature freshness a actual model digest.

```json
{
  "score": 0.71,
  "release_subject": "MLOPS-PAY-RISK-PROD-2026-08-r31",
  "feature_fallback": true,
  "fallback_reason": "online_store_timeout",
  "action_authority": "manual_review_only"
}
```

## 6. Streaming inference

Streaming inference spracúva unbounded events. Consumer číta partitions, udržiava offsets alebo checkpoints, pracuje s event time a môže vidieť duplicates alebo out-of-order records. „Exactly once“ býva end-to-end vlastnosť iba pri konkrétnom transactional design-e; broker delivery guarantee sama nepreukazuje exactly-once business action.

```yaml
stream_subject: risk-events-v5
consumer_group: risk-inference-prod-r31
partition: 7
offset_start: 918201
offset_end_exclusive: 918900
watermark: 2026-08-03T10:00:00Z
release_subject: MLOPS-PAY-RISK-PROD-2026-08-r31
```

Event ID a model release vytvoria deterministic prediction key. Downstream action používa stable business operation ID, aby replay alebo rebalance nevytvorili duplicate review ticket. Offset sa commitne až po durable prediction a action ledger update podľa zvoleného transaction boundary.

## 7. Event time, processing time a late events

Event time určuje, kedy business event nastal. Processing time určuje, kedy ho system spracoval. Feature windows a policy musia používať správny čas. Late event môže zmeniť historical aggregate po tom, čo online prediction už vznikla.

Streaming path potrebuje allowed lateness a correction semantics. Correction môže vytvoriť novú prediction generation, ale nemá automaticky opakovať nezvratný action. Reconciliation rozhodne, či je potrebná human review, compensation alebo iba monitoring update.

Batch backfill a stream correction musia používať rovnaké feature definitions a point-in-time semantics. Inak offline replay nevysvetľuje live behavior.

## 8. Micro-batching

Micro-batching zhromažďuje requests alebo events počas krátkeho okna, aby zlepšil throughput. Zvyšuje queue latency a môže meniť ordering. Dynamic batching v serving runtime je operational optimization, ale batch formation, maximum delay a padding ovplyvňujú SLO a resource use.

Request-level telemetry musí zachovať identitu aj v batch tensor-e. One bad item nesmie nejasne zneplatniť ostatné bez per-item error contractu. Retry celého batchu môže duplikovať successful items, ak downstream nemá idempotency.

## 9. Schema a protocol compatibility

Input schema zahŕňa field names, order, types, shapes, units, nullability a semantic meaning. V2 tensor protocol môže byť strict, zatiaľ čo custom JSON wrapper je flexibilnejší, ale zvyšuje custom code a compatibility responsibility.

Model signature a server contract sa testujú s positive, malformed, missing, extra a oversized requests. Compatibility môže vyžadovať versioned endpoints alebo adapter. Adapter digest je súčasť release subjectu.

Output contract oddeľuje raw score, calibrated probability, class, explanation a action suggestion. Client nesmie interpretovať raw score ako probability bez contractu.

## 10. Consistency medzi modes

Batch, online a stream môžu zdieľať model package, no potrebujú parity tests pre rovnaké observation IDs. Matched-request replay porovná features, preprocessing, prediction a policy output.

```text
same observation + same point-in-time features + same release
→ expected equivalent raw prediction
```

Business action môže byť odlišná podľa mode, napríklad batch vytvára next-day queue a online real-time priority. Táto odlišnosť je explicitná policy, nie neviditeľný skew.

Parity tolerance berie do úvahy numeric runtime differences. Large mismatch sa najprv diagnostikuje na input a preprocessing vrstve, nie retrainingom.

## 11. Capacity a backpressure

Batch má deadline a throughput target. Online má latency SLO a concurrency. Streaming má consumer lag a event-time freshness. Všetky modes potrebujú backpressure.

Online overload môže používať queue limit a load shedding. Streaming consumer môže spomaliť a lag narastie; autoscaling bez dostatočnej downstream capacity presunie bottleneck. Batch môže prekročiť completion window a kolidovať s ďalším runom.

Capacity symptom sa nesmie zamieňať za model regression. Release telemetry musí oddeľovať model compute, feature wait, queueing a downstream action latency.

## 12. Security a privacy

Online endpoint autentizuje caller a autorizuje use case. Batch job má bounded dataset access. Stream consumer číta iba allowed topics a tenant partitions. Prediction logs nesmú nekontrolovane ukladať citlivé raw features.

Request/response logging používa sampling, redaction a retention. Debug capture je incident-controlled a auditované. Model output môže byť sensitive derived data a patrí pod rovnakú governance.

## 13. Evidence hierarchy

Batch: Job spec → Pod attempts → output manifests → reconciliation. Online: deployment → loaded fleet fingerprint → request traces → action ledger. Streaming: consumer deployment → group generation → partition/offset processing → state/checkpoint → action ledger.

```bash
kubectl get job risk-score-2026-08-02-v3 -n ml-batch -o yaml
kubectl get isvc risk-model -n ml-prod -o yaml
kubectl logs deploy/risk-stream-consumer -n ml-stream --since=10m
```

Tieto commands poskytujú runtime evidence, nie model quality. Matched request a business outcome sú ďalšie vrstvy.

## 14. Competing failure hypotheses

Batch row deficit môže pochádzať z input snapshotu, sharding, filter policy, failed attempt alebo partial publication. Online latency môže byť gateway, feature store, model compute, queue alebo downstream dependency. Streaming duplicates môžu pochádzať z broker replay, offset commit, consumer rebalance alebo non-idempotent action.

First divergence sa hľadá podľa mode-specific identity. Rovnaký high-level symptom „príliš veľa reviews“ môže byť duplicate stream action, online threshold, batch double import alebo model behavior. Retraining bez tejto identity je nesprávna prvá mutation.

## 15. Recovery a acceptance

Containment môže zastaviť batch publication, odpojiť online traffic alebo pause-nuť stream partitions. Evidence sa zachová pred resetom offsets alebo deletion outputov. Recovery obnoví exact release a operation ledger, potom vykoná mode-specific replay.

Pozitívny test overí complete batch manifest, online request s exact fingerprintom a stream event s durable single action. Forbidden test odmietne mutable model URI, missing operation ID a incompatible schema. Recovery test simuluje partial batch, feature timeout a consumer rebalance. Second-operation test zopakuje rovnaký batch interval, online operation a stream event bez duplicate side effectu.

Inference mode je prijatý až vtedy, keď execution, prediction, action a outcome zostávajú korelovateľné cez retries, replays a failures. Model digest je nutná, ale nie postačujúca identita.

## Primárne zdroje

- [Kubernetes — Jobs](https://kubernetes.io/docs/concepts/workloads/controllers/job/)
- [KServe — Data plane](https://kserve.github.io/website/docs/0.17/concepts/architecture/data-plane)
- [KServe — Inference Protocol V1 and V2 guidance](https://kserve.github.io/website/docs/concepts/architecture/data-plane/v1-protocol)
