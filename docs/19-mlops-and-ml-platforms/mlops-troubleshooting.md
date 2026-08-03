# MLOps troubleshooting

MLOps troubleshooting je disciplína určovania prvej odchýlky medzi intended, configured, resolved, loaded, exercised a outcome state. Nie je to zoznam náhodných restartov. ML systém obsahuje viac časových osí, mutable control pointers, asynchronous jobs, caches, distributed workers, external stores a oneskorený ground truth. Bez exact subjectu a evidence preservation môže každý „fix“ vytvoriť nový experiment a zničiť príčinu.

V incidente `MLOPS-PAY-98` alert hlásil rast false positives a p99 latency. Operátor presunul Registry alias späť, reštartoval KServe Pods a spustil KFP pipeline znova. Latency klesla, ale false positives zostali a vznikli dva nové Model Packages. Neskôr sa ukázalo, že jedna feature materialization bola stale, jeden serving Pod mal starý Runtime image a feedback join zahadzoval delayed labels. Reštarty zmenili tri subjects naraz a odstránili časť logs. Správny postup mal najprv zmraziť mutations, zachytiť release/Pod/data generations a nájsť prvú divergence.

## 1. Symptom nie je root cause

Symptom je pozorovaný jav: failed pipeline, Pending TrainJob, mixed predictions, drift alert alebo cost spike. Root cause je mechanizmus, ktorý vytvoril prvú nesprávnu state transition. Jednému symptómu zodpovedá viac competing hypotheses.

```text
p99 latency rastie
├─ traffic mix alebo payload size
├─ cold start alebo rollout
├─ queue/concurrency saturation
├─ GPU memory pressure
├─ feature dependency latency
├─ fallback/retry amplification
└─ telemetry calculation error
```

Troubleshooting začína hypotheses, ktoré sa dajú odlíšiť authoritative evidence. „Kubernetes je pomalý“ alebo „model driftuje“ nie sú testovateľné príčiny.

## 2. Exact incident subject

Pred zásahom sa zapíše incident manifest:

```yaml
incident_id: MLOPS-PAY-98
time_window:
  start: 2026-08-03T10:15:00Z
  end: open
affected_journey: online-fraud-decision
expected_release: fraud-2026-08-03.18
observed:
  kfp_run_id: 4f0...
  train_job: fraud-train-184
  registry_version: fraud-prod/184
  serving_release_ids:
    - fraud-2026-08-03.18
    - fraud-2026-07-29.11
  feature_generation: unknown
  label_snapshot: immature
change_freeze: true
```

Time window používa event time aj processing/observation time. Exact IDs sa získajú z API, nie z názvu screenshotu. Ak subject nemožno zostaviť, to je samostatný platform incident.

## 3. State ladder a first divergence

Každý subsystem sa skúma rovnakým ladderom:

```text
intended
→ configured
→ controller-resolved
→ loaded
→ exercised
→ business outcome
```

Prvá vrstva, kde actual state nesedí s expected, určuje ďalší smer. Ak Git manifest je správny, ale resolved Deployment má iný image, problém je rendering/reconciliation. Ak Pod má správny image, ale načítal iný model digest, problém je storage/runtime load. Ak prediction je správna, ale action chybná, problém je downstream policy.

Preskakovanie rovno na outcome alebo restart skrýva first divergence.

## 4. Evidence preservation a change freeze

Pred restartom, retry alebo rollbackom sa vytvorí evidence bundle, ktorý zachováva každú vrstvu state ladderu. Source commit a release manifest ukazujú intended generation. API objects vrátane `generation`, `observedGeneration`, conditions a resolved specs dokazujú configured a controller-resolved stav. Task a job attempts, Kubernetes events, Pod specs, image digests a node/device assignment vysvetľujú, čo orchestrátor skutočne spustil a kde.

Logs a traces sa ukladajú s presným time rangeom, clock contextom a release identity, aby sa dali spojiť s requestmi a attempts. Artifact manifests, object versions a digests dokazujú, aké bytes vznikli alebo boli načítané; cache hit/miss evidence vysvetľuje, či sa výpočet vykonal alebo znovu použil starší output. Monitoring query sa archivuje spolu s filtrom, denominatorom, samplingom a dashboard transformáciou, pretože samotný screenshot neumožňuje reprodukciu alarmu. External side-effect state sa číta priamo z Registry, deployment targetu, databázy alebo queue, aby timeout nebol nesprávne interpretovaný ako neúspech.

Change freeze neznamená úplné zastavenie businessu. Znamená zákaz nekorelovaných mutations, ktoré by zmenili viac hypotheses naraz alebo prepísali dôkaz. Emergency containment sa loguje ako nová operation s jasným subjectom, actorom, dôvodom a expected effectom.

## 5. Unknown outcome a read-before-retry

Timeout neznamená failure. API mutation mohla uspieť a odpoveď sa stratiť. Blind retry je hlavný zdroj duplicate model versions, pipeline runs, deployments a notifications.

Postup:

```text
request timeout
→ query target podľa idempotency key alebo expected subjectu
→ compare actual state
→ accept success, reconcile partial state alebo retry
```

Ak target nepodporuje idempotency key, platforma udržiava operation ledger a deterministické names. Retry bez read-back je forbidden pri external mutations.

## 6. Pipeline troubleshooting

Pri KFP alebo inom orchestrátore sa kontroluje compiled graph/version, parameters, pipeline root, service account, task attempts, cache status a outputs. Run `Succeeded` s chybným artifactom smeruje na hidden dependency, mutable input, incorrect branch alebo validation bug.

Failed task sa nerozoberá iba podľa poslednej log line. Kontroluje sa Pod event, exit code, OOM/eviction, artifact upload a controller state. Missing output môže byť workload failure alebo post-execution publication failure.

Re-run sa klasifikuje. Rovnaký IR a inputs je retry/reproduction. Zmenený image, parameter alebo dataset je nový subject a nesmie sa vydávať za potvrdenie pôvodnej hypotézy.

## 7. Training troubleshooting

Pending TrainJob sa rozkladá na queue admission, quota, scheduler topology, node taints, GPU allocatable a image/data access. Running Pods bez progressu smerujú na rendezvous, collective, data loader, storage alebo divergent rank path.

Quality regression po successful training vyžaduje porovnať dataset snapshot, shard coverage, global batch, world size, seeds, code, Runtime generation a checkpoint. GPU utilization sama nepreukazuje useful training.

Pri distributed hang sa zachytia logs všetkých ranks, process-group generation a node/device health. Restart jedného worker-a bez framework-level recovery contractu môže vytvoriť inú training generation.

## 8. Artifact, Registry a lineage troubleshooting

Ak Registry version existuje, ale model sa nedá načítať, kontroluje sa artifact URI, credentials, object existence, completeness, digest a package environment. Metadata-only success je častá competing hypothesis.

Mixed Registry/serving identity vzniká pri mutable alias, independent resolution per replica, stale cache alebo partial rollout. Rozhodujúci je loaded fingerprint z data plane.

Lineage gap sa hľadá po edges: source → data → run → artifact → version → release → deployment. Chýbajúca edge sa nedopĺňa odhadom; označí sa unknown a promotion/recovery sa podľa risku zablokuje.

## 9. Feature a data troubleshooting

Data incident sa oddeľuje na schema, content, interval, completeness, freshness, duplication a semantics. Rovnaký row count nepreukazuje rovnakú population.

Feature parity skúma definition digest, offline snapshot, online materialization watermark, entity key, event time, TTL a fallback. Stale online value môže pochádzať z materialization delay, failed stream write, clock skew alebo wrong feature service.

Pri backfill-e sa vytvorí nový data operation subject. Prepis existujúceho partitionu bez versiony ničí incident evidence.

## 10. Serving troubleshooting

KServe, Kubernetes alebo cloud endpoint sa skúma od desired state cez resolved workload, model load, readiness, networking, request a business action. `Ready`/`InService` s errors smeruje na schema, model bytes, transformer, dependency, overload alebo routing.

Mixed outputs vyžadujú per-replica release/model fingerprint. Tail latency sa dekomponuje na ingress, queue, preprocessing, inference, postprocessing a downstream action. CPU/GPU aggregate môže skryť jednu hot replica alebo request-mix skew.

Restart je containment iba pri jasnom transient state a zachovanom evidence. Ak mutable URI načíta po reštarte nové bytes, restart je zároveň deployment.

## 11. Monitoring a drift troubleshooting

Alert sa najprv reprodukuje z uloženého query manifestu. Kontroluje sa time window, release filter, denominator, label coverage, sampling, missing telemetry a dashboard transform.

Drift signal sa rozkladá na data drift, prediction drift, label shift, concept drift, pipeline change a observation bias. Bez labels nemožno potvrdiť concept drift. Jeden score nesmie automaticky spustiť retraining.

Ak alert zmizne po zmene baseline-u, neznamená to recovery. Baseline mutation je nový monitoring subject a musí byť odôvodnená.

## 12. Feedback a ground-truth troubleshooting

Quality metric môže klesnúť pre model alebo pre label pipeline. Kontroluje sa maturity horizon, join coverage, right censoring, action-conditioned observation, human-review selection a label definition generation.

Available labels sa porovnávajú s eligible predictions. Missing population sa explicitne kvantifikuje. Backfill alebo corrected labels vytvoria nový evaluation snapshot, nie tiché prepísanie starého verdictu.

## 13. Security a supply-chain troubleshooting

Pri neočakávanom image/model digest-e sa zastaví promotion a overí source, build provenance, signature, registry retention a admission logs. Valid signature nad nesprávnym digestom nie je recovery.

Credential incident vyžaduje revocation/rotation, audit mutationov a re-verification artifacts. Rebuild z trusted source sa vykoná v clean builderi. Existing runtime sa nepovažuje za clean iba po Pod restart-e.

Privacy incident zachováva minimum citlivého evidence podľa incident policy. Logs/traces sa nezdieľajú nekontrolovane počas diagnosis.

## 14. Cost a capacity troubleshooting

Cost spike sa rozkladá na traffic, retries, idle capacity, queueing, failed jobs, storage, egress a monitoring overhead. Unit cost používa useful work denominator.

Low GPU utilization môže byť data starvation, small batch, synchronization, fragmentation alebo telemetry gap. Zvýšenie replica/node count bez bottleneck proof môže cost zhoršiť a latency nezmeniť.

Capacity change je experiment s before/after subjectom a load profile. Autoscaler config bez representative load testu je slabá hypotéza.

## 15. Cross-system timeline

MLOps incidenty potrebujú unified timeline z CI, orchestratorov, Kubernetes/cloud APIs, stores, serving a feedbacku. Hodiny a event timestamps sa normalizujú; processing delay sa zachová.

```text
10:12 source merge
10:15 pipeline submit
10:41 model publication
10:43 alias mutation timeout
10:44 retry creates second version
10:48 serving rollout
10:52 feature materialization lag
11:03 first quality alert
```

Timeline odhaľuje causality candidates, ale časová blízkosť sama osebe nie je dôkaz. Každý transition sa potvrdí IDs a read-backom.

## 16. Hypothesis table a experiment

Incident commander vedie malú hypothesis table:

| Hypotéza | Predikovaný dôkaz | Query/test | Výsledok |
|---|---|---|---|
| mixed model replicas | dva loaded digests | inventory endpoint | confirmed |
| concept drift | quality drop pri mature labels | delayed eval | unknown |
| feature staleness | watermark za request time | materialization read-back | confirmed |

Test mení jednu premennú, ak je to možné. Ak containment mení viac vrstiev, výsledok sa nepoužíva ako čisté potvrdenie root cause.

## 17. Containment, recovery a correction

Containment znižuje škodu: stop traffic increase, disable mutation, use safe fallback alebo freeze retraining. Recovery obnoví known-good composite state a overí journey. Corrective action odstráni mechanizmus, napríklad complete cache key, runtime versioning alebo idempotency.

Rollback nie je root-cause fix. Po recovery sa incident stále analyzuje a druhá operation testuje, že corrective control funguje.

## 18. Runbooks a automation

Runbook obsahuje prerequisites, exact commands/API queries, expected outputs, branching decisions, evidence paths a stop conditions. „Restartni deployment“ nie je runbook.

Príklady queries:

```bash
kubectl get inferenceservice fraud-classifier -n fraud-prod -o yaml
kubectl get pods -n fraud-prod -l serving.kserve.io/inferenceservice=fraud-classifier -o wide
kubectl describe pod <pod> -n fraud-prod
kubectl logs <pod> -n fraud-prod --all-containers --previous
```

Cloud path používa exact account/Region a `Describe*` APIs. Commands sa vykonávajú read-only, kým nie je schválený containment. Automation môže zozbierať evidence bundle, ale nesmie automaticky vymazať failed resources potrebné pre RCA.

## 19. Post-incident learning

Postmortem rozlišuje trigger, first divergence, detection gap, containment, recovery a systemic causes. Action item má owner, due date a acceptance test. „Viac monitoringu“ bez konkrétneho signal/denominatora nie je dobrá akcia.

Incident examples sa prenášajú do chaos/game-day a second-operation testov. Platform docs sa aktualizujú, ak mental model alebo authority boundary nebol jasný.

## 20. Acceptance

Pozitívna troubleshooting acceptance znamená exact subject, preserved evidence, explicit competing hypotheses, potvrdenú first divergence, bounded containment, composite recovery a mature outcome verification. Recovery acceptance vyžaduje druhú operation a reconciliation všetkých nejasných side effects.

Forbidden acceptance je „po reštarte je to zelené“, alias rollback bez loaded parity, rerun so zmenenými inputs ako reprodukcia alebo zmiznutý alert po prepise baseline-u. Troubleshooting je ukončený až vtedy, keď je vysvetlený mechanizmus, obnovený known-good state a preventívny control prešiel acceptance testom.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: MLOps platform architecture](mlops-platform-architecture.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Generative AI, foundation model a large language model →](../20-llm-and-genai-engineering/generative-ai-foundation-model-llm.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
