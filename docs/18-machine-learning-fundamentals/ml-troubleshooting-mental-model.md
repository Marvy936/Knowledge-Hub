# ML troubleshooting mental model

Machine-learning incident sa nesmie začať náhodnou zmenou hyperparameteru, retrainingom ani všeobecným tvrdením, že „model driftoval“. ML system je chain dát, labels, features, code, training procedure, artifactov, serving, policy, action a delayed outcomes. Rovnaký symptom môže mať viac konkurenčných príčin: pokles recall môže vzniknúť label maturity, population shiftom, stale feature, iným thresholdom, queue truncation alebo reálnym model regression. Troubleshooting preto potrebuje presný subject, evidence ordering, hypothesis tree, containment a acceptance, ktoré oddeľujú control-plane úspech od business closure.

Incident `ML-PAY-89` pokračuje po zistení offline-online gapu. Atlas tím najprv spustil retraining s vyšším class weightom, pretože online recovered loss klesol. Nový run použil dataset vytvorený po rollout-e, v ktorom boli labels selektívne dostupné pre reviewed cases. Candidate zlepšil recall na tomto datasete, ale zvýšil queue overload. Iný tím súčasne znížil threshold a platform tím navýšil feature timeout. Tri mutations zmenili model, policy aj serving naraz, takže nikto nevedel, ktorá zmena pomohla. Kapitola vytvára jednotný evidence-first mental model od business symptómu po exact layer, generation, recovery a second-operation proof.

## 1. Dominantný troubleshooting lifecycle

Troubleshooting postupuje od outcome k subjectu a od najskoršej authoritative vrstvy k downstream efektu. Mutácia sa robí až po vytvorení falzifikovateľnej hypotézy.

```text
business alebo technical symptom
→ exact affected subject, time, population a generation
→ containment bez zničenia evidence
→ end-to-end evidence timeline
→ first divergence a competing hypotheses
→ discriminating test alebo read-back
→ minimal corrective mutation
→ component recovery
→ end-to-end positive, negative a second-operation acceptance
→ RCA, prevention a monitoring update
```

Ak evidence chýba, správny verdict je „unknown“ alebo „insufficient evidence“, nie najpravdepodobnejší príbeh vydávaný za fact.

## 2. Exact incident subject

Incident record identifikuje business journey aj všetky relevantné generations.

```yaml
incident_subject: ML-PAY-89
symptom:
  first_seen: 2026-08-03T06:15:00Z
  business: recovered_loss_eur_down_18_percent
  technical: campaign_fallback_rate_up_8_percent
scope:
  population: eu_cnp_campaign_traffic
  observation_unit: payment_operation_id
  regions: [eu-central]
model:
  digest: sha256:1f92...b0c4
  preprocessing: risk-v9
  calibration: cal-v5
policy:
  queue: ML-PAY-QUEUE-2026-08-v8
serving:
  image: sha256:9d34...118e
  feature_contract: risk-v9
labels:
  generation: recoverable-loss-21d-v4
  maturity_cutoff: 2026-07-13
changes:
  - rollout_candidate_to_10_percent
  - feature_store_timeout_200_to_120_ms
```

Incident bez exact time a generation ľahko spojí predecessor a successor evidence. Scope sa aktualizuje ako hypothesis, ale pôvodné observations zostávajú zachované.

## 3. Symptom taxonomy

Symptom sa najprv zaradí podľa vrstvy, kde bol pozorovaný:

- data/label — missing records, schema drift, delayed labels, changed prevalence;
- feature — freshness, join coverage, transformation alebo training-serving skew;
- training — divergence, failed trials, unstable seeds, checkpoint/resume problém;
- artifact — wrong digest, incompatible preprocessing, corrupt serialization;
- serving — availability, latency, resource saturation, fallback alebo partial rollout;
- prediction — score distribution, calibration, class/cohort performance;
- policy — threshold, top-K, rules, queue alebo override;
- action — downstream execution, human compliance, capacity alebo latency;
- outcome — business value, harm, appeal, churn alebo missed event.

Taxonomy neurčuje root cause. Pomáha iba nájsť first observed failure a nasledujúce authoritative reads.

## 4. First divergence principle

End-to-end chain sa porovnáva s healthy baseline a hľadá sa najskoršia vrstva, kde sa current a expected evidence rozchádzajú.

```text
same eligible request?
→ same feature values?
→ same preprocessing output?
→ same model prediction?
→ same policy decision?
→ same action execution?
→ same mature outcome distribution?
```

Ak feature vector už nesedí, nie je efektívne začať SHAP analysis modelu. Ak predictions sú identické a decision sa líši, model weights nie sú root cause. First divergence znižuje search space a bráni downstream symptómu prekryť upstream failure.

## 5. Authority hierarchy

Evidence má rôznu authority. Dashboard aggregate je index, nie vždy source of truth. Troubleshooting definuje autoritatívny read pre každú vrstvu.

```yaml
authority:
  dataset_membership: immutable_manifest_and_row_ids
  feature_value: event_time_feature_log_or_recomputed_as_of
  model_identity: artifact_registry_digest
  prediction: request_correlated_prediction_log
  policy: versioned_decision_config_and_trace
  action: downstream_transaction_or_review_record
  outcome: mature_adjudicated_label
```

Derived dashboard môže byť stale alebo používať odlišný denominator. Autoritatívny read musí byť korelovateľný exact request/entity ID a time.

## 6. Evidence preservation

Prvá mutation často zničí dôkaz. Pred rollbackom alebo retrainingom sa zachová:

- affected a healthy request IDs;
- raw inputs, feature vectors a timestamps;
- model, preprocessing, calibration a policy digests;
- serving logs, errors, fallback a resource metrics;
- predictions, explanations a decision traces;
- queue membership, human overrides a actions;
- labels vrátane unknown/maturity;
- recent changes, deployment events a attempts.

Sensitive artifacts sa ukladajú podľa privacy a access policy. Preservation neznamená nekontrolované kopírovanie production data.

## 7. Timeline a change correlation

Incident timeline kombinuje symptom, deployments, data pipeline runs, config changes, external events a label arrivals.

```text
05:50 feature-store rollout
06:00 traffic campaign starts
06:10 timeout policy changes
06:15 fallback rate rises
06:20 queue composition changes
06:30 recovered-loss proxy falls
```

Temporal correlation vytvára hypotézu, nie kauzalitu. Change môže byť latentný a symptom sa prejaví až po cache expiry alebo label maturity. Absencia deploymentu nevylučuje source-data alebo external population change.

## 8. Healthy comparator

Comparator môže byť predecessor model, unaffected cohort, region, node, time window alebo replay. Musí sa líšiť čo najmenším počtom relevantných dimensions.

```text
bad campaign/new-merchant traffic
vs.
healthy non-campaign/new-merchant traffic
```

Porovnanie rôznych populations môže vytvoriť falošný difference. Matched requests, group/time controls a same-policy traces majú vyššiu diagnostic value než globálne before/after averages.

## 9. Data a label troubleshooting

Data investigation začína membership funnelom:

```text
source events
→ extraction
→ eligibility
→ joins
→ feature rows
→ label resolution
→ split/sample
```

Kontroluje sa row count, unique entity, duplicates, event time, source version, schema, distribution, missingness, label maturity a unknown state. Rovnaký count nepreukazuje rovnakú membership.

Label incident môže vyzerať ako model regression. Ak recent positives ešte nedozreli, recall denominator je neúplný. Ak guideline zmenila positive definition, historical a current scores nie sú porovnateľné. Dataset rebuild dostane nový manifest a dependent experiments sa invalidujú podľa lineage.

## 10. Feature troubleshooting

Feature sa sleduje od raw source po online value.

```text
source event
→ transformation
→ feature store write
→ freshness/TTL
→ online read
→ preprocessing
→ model input
```

Pre affected IDs sa porovnajú values, availability time, units, defaults a transformation code. Aggregate drift nemusí odhaliť constant default v jednom cohort-e. Feature freshness sa meria event-time age, nie iba successful read.

Training-serving skew test používa rovnaký request a trusted recomputation. Rozdiel sa lokalizuje po feature groups a intermediate transformations.

## 11. Training troubleshooting

Training incidenty zahŕňajú diverging loss, NaN, OOM, stalled convergence, unstable seeds, poor generalization a wrong resume. Diagnostika rozlišuje data/config/code/environment generations.

```text
same dataset + same config + same environment
→ compare batch sequence
→ loss/gradient trajectory
→ optimizer/scheduler state
→ checkpoints
→ validation predictions
```

Loss curve sama neidentifikuje príčinu. NaN môže vzniknúť invalid inputom, overflow, loss domain alebo optimizer state. OOM môže byť batch, sequence length, activation, parallelism alebo leak. Retry bez attempt identity nesmie prepísať evidence.

## 12. Artifact troubleshooting

Artifact registry metadata sa porovná s deployed runtime. Overuje sa digest, signature/provenance, framework version, preprocessing/calibrator inclusion, class order, feature schema a load test.

```text
approved artifact
→ package manifest
→ deployed image/config
→ loaded runtime digest
→ prediction smoke test
```

Filename alebo model version string nie je authority. Partial download alebo stale cache môže načítať predecessor. Serialization success nepreukazuje semantic compatibility.

## 13. Serving troubleshooting

Serving investigation používa RED/USE-like signals doplnené o ML-specific coverage.

```yaml
serving:
  rate: requests_per_second
  errors: inference_feature_timeout_schema_error
  duration: p50_p95_p99
  utilization: cpu_gpu_memory_queue
  coverage: model_success_fallback_abstention
```

Latency sa rozkladá na feature fetch, preprocessing, inference, postprocessing a policy. P95 aggregate môže skryť cohort-specific timeout. Autoscaling môže zvýšiť replicas, ale model load a cache warm-up zhoršia first-request behavior.

Fallback outcome sa meria samostatne. Circuit breaker môže chrániť latency a zároveň meniť business risk.

## 14. Prediction a calibration troubleshooting

Prediction distribution change sa rozloží podľa inputs, model a calibration/policy scale. Overuje sa raw score, calibrated probability, class order, threshold a cohort.

```text
raw score stable + probability changed
→ calibrator or class mapping hypothesis

raw score changed + feature changed
→ upstream feature/population hypothesis

probability stable + action changed
→ policy/capacity hypothesis
```

Metric sa prepočíta z immutable predictions a labels. Dashboard implementation, sample weights a denominator sa validujú pred model conclusion.

## 15. Policy a queue troubleshooting

Policy trace ukazuje všetky stages: eligibility, threshold, boost, rule, ranking, capacity, tie-breaker a override.

```yaml
decision_trace:
  eligible: true
  probability: 0.241
  threshold_passed: true
  merchant_boost: -0.04
  final_priority: 0.201
  queue_rank: 2712
  capacity: 2500
  admitted: false
```

Model predicted positive môže byť queue negative. Offline confusion matrix nad thresholdom preto nemusí opisovať production action. Config read-back a policy digest sa porovnajú medzi replicas.

## 16. Human a downstream action troubleshooting

Ak intended action nevznikla, skúma sa UI, queue, permissions, training, workload, override reason, downstream API a transaction outcome.

```text
model decision
→ task created
→ visible reviewerovi
→ opened
→ action selected
→ downstream mutation succeeded
→ business effect
```

Task-created metric nepreukazuje completed action. Human disagreement môže indikovať model error, explanation problem alebo guideline conflict. Reviewer feedback nie je automaticky ground truth.

## 17. Outcome troubleshooting

Business outcome sa normalizuje population, exposure a external factors. Kontroluje sa event-time linkage, maturity, control/baseline a causal scope.

```text
raw recovered loss down
could mean:
- less fraud prevalence
- less traffic
- fewer reviewed cases
- worse targeting
- slower label maturity
- lower recovery success
```

Outcome decomposition oddeľuje quantity, rate, value per action a downstream conversion. Model nemusí ovplyvniť každý factor.

## 18. Hypothesis tree

Hypothesis tree je usporiadaný podľa vrstiev a predikovaných evidence patterns.

```text
symptom: recovered loss down
├─ population/data
│  ├─ traffic mix changed
│  └─ labels immature
├─ feature/serving
│  ├─ join timeout
│  └─ stale/default feature
├─ model
│  ├─ ranking regression
│  └─ calibration regression
├─ policy/action
│  ├─ threshold/boost changed
│  ├─ queue capacity truncation
│  └─ reviewers did not act
└─ external outcome
   ├─ fraud prevalence changed
   └─ recovery process changed
```

Každý leaf obsahuje test, expected result a falsifier. Tree sa aktualizuje evidence, nie intuíciou.

## 19. Discriminating tests

Dobrý test odlišuje viac hypotéz naraz. Matched online/offline feature a prediction parity napríklad rozdelí data/skew od model/policy paths.

```yaml
test:
  subject: 1000 matched affected requests
  operation: recompute features and predictions offline
  supports:
    feature_skew: feature_diff_rate > 0
    model_mismatch: same_features_but_prediction_diff
  falsifies:
    policy_only: divergence_before_policy
```

Test nesmie meniť production state, pokiaľ ide o diagnosis. Ak mutation je potrebná, používa controlled canary a attempt identity.

## 20. One-variable mutation principle

Počas incidentu sa minimalizuje počet concurrent zmien. Model retrain, threshold change a infrastructure tuning naraz zničia attribution.

```text
contain
→ choose highest-evidence hypothesis
→ mutate one bounded layer
→ observe predeclared signals
→ accept/reject
→ next mutation
```

Urgent safety incident môže vyžadovať broad rollback. Aj vtedy sa composite generation a evidence zachová. Po containment-e sa components testujú izolovane.

## 21. Rollback matrix

Každá vrstva má vlastnú rollback alebo roll-forward možnosť.

```yaml
rollback_matrix:
  data_pipeline: restore_previous_snapshot_or_fix_successor
  feature: disable_feature_or_restore_transform
  model: previous_approved_digest
  calibration: previous_calibrator
  policy: previous_threshold_queue_generation
  serving: previous_image_or_disable_candidate
  action: manual_review_or_safe_abstention
```

Rollback môže byť incompatible s current schema alebo downstream state. Pre-check overí predecessor dependencies. Unknown outcome mutation potrebuje read-back pred retry.

## 22. Recovery layers

Recovery sa uzatvára v troch vrstvách:

1. component recovery — chybná vrstva vracia expected evidence;
2. journey recovery — end-to-end request prejde feature, prediction, policy a action;
3. business recovery — mature outcome a harm guardrails sa vrátia do accepted range.

Component green bez journey/business proof je partial recovery. Business recovery môže byť delayed; interim containment ostáva aktívny.

## 23. Positive, negative a second-operation tests

Positive test overí intended valid path. Negative test overí forbidden alebo degraded path. Second-operation test odhaľuje stale cache, non-idempotency, exhausted state a incomplete recovery.

```text
first request after fix → success
second request same entity → no stale predecessor
second node/region → same generation
fallback trigger → safe bounded action
rollback then reapply → deterministic state
```

ML-specific second tests zahŕňajú second cohort, second seed, second time window, second threshold decision a resumed training attempt.

## 24. Unknown outcome a idempotency

Deployment, feature write, registry promotion alebo queue action môže timeoutnúť po server-side success. Blind retry môže vytvoriť duplicate alebo mixed generation.

```text
mutation request
→ timeout
→ authoritative read-back by operation ID/digest
→ decide success, failure alebo unknown
→ retry only if safe/idempotent
```

Training run retry dostáva attempt ID. Promotion pointer update používa compare-and-set predecessor. Business action používa idempotency key.

## 25. Observability gaps ako incident findings

Ak root cause nemožno určiť pre chýbajúcu koreláciu alebo denominator, to je samostatný production-readiness finding. Nemá sa nahradiť confident guessom.

```yaml
observability_gap:
  missing: fallback_reason_by_request_id
  impact: cannot_attribute_unscored_campaign_cases
  containment: disable_silent_low_risk_fallback
  owner: ml_platform
  due: 2026-08-10
```

Po incidente sa pridávajú signals, ale iba s bounded cardinality, privacy a retention. Log everything nie je udržateľná stratégia.

## 26. Worked incident `ML-PAY-89`

Tím videl pokles recovered loss a predpokladal model underfit. Bez preservation spustil retrain s vyšším class weightom nad post-rollout datasetom. Dataset obsahoval mature labels prevažne pre reviewed cases; unreviewed campaign operations boli unknown mapované na negative. Súčasne risk tím znížil threshold a platform tím zvýšil timeout.

```text
business symptom
→ premature model hypothesis
→ selective-label retrain
+ threshold mutation
+ serving timeout mutation
→ queue overload
→ no attribution
```

Evidence-first replay našiel first divergence vo feature coverage: affected campaign requests používali low-risk fallback. Pre successfully scored matched requests boli raw predictions zhodné s offline artifactom. Druhá divergence bola policy: production merchant boost a capacity sa líšili od offline simulation. Tretia bola action: reviewer completion klesla pri overload. Mature outcome ešte nebol complete.

Containment vrátil queue policy, zmenil fallback na explicitnú manual-review abstention pre high-value campaign cases a zmrazil retrain promotion. Feature timeout sa opravil samostatne. Recomputed matched parity, second-node test a controlled canary prešli; business recovery sa uzavrela až po 21-dňovej maturity.

## 27. Competing failure hypotheses

Pre každý ML incident sa udržiava minimum competing hypotheses across layers:

- observation failure — dashboard, query, window alebo denominator je chybný;
- data population failure — membership, duplicates, sampling alebo eligibility sa zmenili;
- label failure — maturity, definition, authority alebo selective observation zlyhali;
- feature failure — source, transform, join, freshness, default alebo skew;
- training failure — config, optimization, seed, resource, checkpoint alebo selection;
- artifact failure — wrong/corrupt/incompatible model alebo preprocessing;
- serving failure — load, latency, error, fallback, cache alebo partial rollout;
- model behavior failure — ranking, calibration, cohort alebo uncertainty regression;
- policy failure — threshold, rule, boost, capacity, tie-breaker alebo override;
- action failure — human/system nevykonal intended decision;
- outcome attribution failure — external factor, control alebo maturity chýba;
- feedback failure — deployed policy zmenila labels a future training distribution.

Hypotéza bez predicted evidence nie je troubleshooting unit. „Model je zlý“ je príliš broad na bezpečnú mutation.

## 28. Runbook structure

ML runbook sa organizuje podľa symptomov a authority, nie podľa jedného toolu.

```yaml
runbook:
  symptom: predicted_positive_rate_drop
  immediate_containment:
    - freeze_rollout
    - preserve_request_ids
  authoritative_reads:
    - deployed_digests
    - feature_coverage
    - raw_score_distribution
    - policy_trace
  hypotheses:
    - population_shift
    - feature_timeout
    - artifact_mismatch
    - threshold_change
  recovery:
    - component_specific
  acceptance:
    - parity
    - second_node
    - mature_cohort
```

Runbook obsahuje stop conditions a escalation. Príkaz bez vysvetlenia subjectu a expected read-back je nebezpečný.

## 29. RCA a prevention

RCA oddeľuje trigger, contributing factors, missing controls a latent conditions. „Human error“ alebo „bad model“ nie je dostatočný root cause.

```text
trigger: feature timeout reduced
contributor: silent low-risk fallback
missing control: fallback-rate cohort alert
latent condition: offline test excluded failed joins
impact amplifier: shared queue capacity
```

Prevention môže byť data contract, lineage, test, policy gate, observability, idempotency, safer default alebo ownership. Každá action má ownera a verification.

## 30. Section-wide ML mental model

Celá sekcia sa dá zhrnúť jedným chainom:

```text
business question
→ population a observation unit
→ sample, feature, label a target
→ point-in-time split a leakage boundary
→ preprocessing a feature contract
→ model family, loss a optimization
→ regularization, HPO a cross-validation
→ metrics, calibration, uncertainty a explanations
→ responsible-AI a reproducibility evidence
→ immutable artifact
→ serving, policy a action
→ mature production outcome
→ evidence-first troubleshooting
```

Každý stage vytvára generation a proof boundary. Upstream validity nepreukazuje downstream outcome. Recovery sa uzatvára až po second operation a relevantnom business evidence.

## 31. Acceptance contract

Positive troubleshooting acceptance identifikuje exact symptom, scope, generation, first divergence, root/contributing causes, corrective mutation a end-to-end tests. Evidence je korelovateľná request/entity/operation IDs.

Recovery acceptance preukazuje component, journey a business recovery. Forbidden paths zahŕňajú retrain-first diagnosis, concurrent uncontrolled mutations, threshold tweak bez policy lineage, seed change until pass, filtered failed requests, dashboard-only authority, blind retry po timeout-e, unknown→negative coercion a closure iba podľa green serving health.

Second-operation acceptance zahŕňa repeat request, second node/cohort/window, fallback path, rollback/reapply a mature outcome. RCA actions majú verified completion.

```yaml
acceptance:
  exact_incident_subject: passed
  evidence_preserved: passed
  first_divergence_identified: passed
  competing_hypotheses_falsified: passed
  minimal_mutation: passed
  component_journey_business_recovery: passed
  second_operation_and_mature_window: passed
  prevention_actions_verified: passed
```

## Kontrolné otázky

1. Prečo ML incident nemá začínať retrainingom?
2. Čo musí obsahovať exact incident subject?
3. Ako symptom taxonomy pomáha bez predstierania root cause?
4. Čo znamená first divergence principle?
5. Prečo dashboard nie je vždy authoritative read?
6. Aké evidence sa zachová pred mutation?
7. Ako healthy comparator znižuje search space?
8. Ako sa data, label a feature incidenty odlišujú?
9. Čo overuje artifact identity chain?
10. Ako serving coverage a fallback menia model outcome?
11. Ako raw score, calibration a policy traces oddeľujú vrstvy?
12. Prečo task creation nepreukazuje completed action?
13. Ako hypothesis tree a discriminating test fungujú spolu?
14. Prečo concurrent model, threshold a infrastructure changes ničia attribution?
15. Aký je rozdiel medzi component, journey a business recovery?
16. Prečo second-operation test odhaľuje neúplnú recovery?
17. Ako unknown-outcome mutation používa read-back a idempotency?
18. Kedy je observability gap samostatným incident findingom?
19. Čo pokazilo troubleshooting v `ML-PAY-89`?
20. Aké positive, recovery, forbidden a second-operation testy uzatvárajú ML incident?

## Glossary impact

Relevantné pojmy: ML troubleshooting, incident subject, symptom taxonomy, first divergence, authority hierarchy, evidence preservation, healthy comparator, hypothesis tree, discriminating test, one-variable mutation, rollback matrix, component recovery, journey recovery, business recovery, second-operation test, unknown outcome, attempt identity, idempotency key, observability gap, ML runbook, root-cause analysis, contributing factor, feedback failure a ML troubleshooting acceptance contract.

## Primárne zdroje

- [Google — Rules of Machine Learning](https://developers.google.com/machine-learning/guides/rules-of-ml)
- [Hidden Technical Debt in Machine Learning Systems](https://papers.nips.cc/paper/5656-hidden-technical-debt-in-machine-learning-systems)
- [The ML Test Score](https://research.google/pubs/the-ml-test-score-a-rubric-for-ml-production-readiness-and-technical-debt-reduction/)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
