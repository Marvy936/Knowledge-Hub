# Offline evaluation oproti production outcome

Offline evaluation meria model alebo model-building procedure na historickom, replay alebo holdout datasete. Production outcome vzniká až po spojení live population, feature availability, serving path, calibration a threshold policy, queue capacity, human alebo automated action, downstream response, delayed labels a feedback loops. Dobré offline score je potrebný dôkaz pre promotion, ale nie je to production business verdict. Rovnako slabý production outcome nemusí automaticky znamenať zhoršené model weights; môže vzniknúť coverage failure, stale features, policy drift, queue truncation, action non-compliance alebo zmeneným environmentom.

Incident `ML-PAY-89` uzatvára sekciu Machine Learning Fundamentals. Atlas Payments promotion gate schválil nový fraud model, pretože average precision, calibrated log loss a captured recoverable loss pri simulovanom top-K prekonali baseline. Po rollout-e však recovered loss klesol, review latency narástla a campaign cohort mal viac false blocks. Offline dataset obsahoval iba successfully joined a mature-labeled operations. Production serving pri vysokom trafficu padal do default-low-risk fallbacku, queue aplikovala iný merchant boost než replay a reviewers spracovali iba časť admitted cases. Labels dozrievali 21 dní a nový model zmenil, ktoré cases získali investigation, takže prvý online dashboard miešal incomplete outcomes s policy-induced selective labels. Kapitola preto spája offline evidence s live system, action a business outcome lifecycle-om.

## 1. Dominantný offline-to-production lifecycle

Model value nevzniká pri `predict()`. Offline experiment vyberie candidate procedure a vytvorí immutable artifact. Deployment ho prenesie cez serving a policy vrstvy k action. Monitoring následne oddeľuje input, prediction, decision, action a outcome evidence.

```text
intended business outcome
→ historical population, label a split contract
→ offline training a evaluation
→ candidate artifact + calibration + policy generation
→ packaging, deployment a serving compatibility
→ live eligibility a feature retrieval
→ prediction, threshold/ranking a queue decision
→ automated alebo human action
→ downstream system/customer response
→ mature label a realized business outcome
→ monitoring, attribution, recovery a successor experiment
```

Každá šípka môže zlyhať bez zmeny upstream modelu. Promotion contract preto nemá dokazovať iba offline score, ale aj kompatibilitu a observability celého chainu.

## 2. Exact production-evaluation subject

Production report musí identifikovať composite generation. Model digest bez policy, feature a rollout identity nevysvetľuje observed outcome.

```yaml
production_evaluation_subject: ML-PAY-PROD-2026-08-v6
business_intent:
  primary: recovered_loss_eur_per_eligible_operation
  constraints:
    false_block_rate_max: 0.0015
    review_latency_p95_minutes_max: 45
model:
  digest: sha256:1f92...b0c4
  preprocessing_digest: sha256:6b19...445e
  calibration_digest: sha256:8a17...71e3
policy:
  queue_generation: ML-PAY-QUEUE-2026-08-v8
  threshold: 0.183
  daily_capacity: 2500
  merchant_boost: merchant-priority-v3
serving:
  image_digest: sha256:9d34...118e
  feature_contract: risk-v9
  fallback_policy: low_risk_with_audit_v2
rollout:
  experiment_id: ML-PAY-ONLINE-2026-08-v3
  allocation_unit: merchant_id
  candidate_share: 0.10
population:
  eligibility_generation: eu-cnp-policy-2026-08-v4
  label_maturity_days: 21
```

Composite subject zabraňuje tomu, aby sa outcome z jednej queue generation pripísal inému modelu alebo aby sa shadow prediction report zamieňal s acted-on policy.

## 3. Offline metric ako estimand

Offline metric odhaduje výkon na population a label distribution definovanej evaluation datasetom. Platnosť prenosu do produkcie vyžaduje, aby sa deployment scenario zhodoval v observation unit, target, feature timing, population, decision policy a action capacity.

```text
offline metric = function(
  historical rows,
  mature labels,
  stored/reconstructed features,
  model predictions,
  simulated policy
)
```

Historický test často nevie zachytiť budúci product mix, latency failures, service fallbacks, reviewer behavior ani feedback. Preto sa výsledok označuje ako offline estimate s limitations, nie expected guaranteed production value.

## 4. Replay a counterfactual boundary

Replay spúšťa candidate model nad historical requests alebo feature snapshots. Je silnejší než jednoduchý table evaluation, ak reprodukuje preprocessing a request path, ale stále nepozoruje outcomes alternatívnych actions.

```text
historical request
→ replay candidate prediction
→ simulated candidate policy
→ compare with historical label/action
```

Ak historical policy nikdy neposlala low-score case na investigation, candidate counterfactual positive môže nemať authoritative label. Replaying new threshold preto nevytvorí missing outcome. Causal alebo off-policy evaluation potrebuje logged propensities, exploration alebo assumptions, ktoré sa nesmú skryť za termínom „backtest“.

Replay tiež nemusí zachytiť concurrency, cache, network timeout a dynamic feature freshness. Online shadow alebo load validation dopĺňa, nie nahrádza label-based offline test.

## 5. Feature parity a point-in-time correctness

Offline features sa musia rekonštruovať tak, ako boli dostupné pri prediction time. Latest-state join môže používať future information a produkovať optimistické score.

```text
entity event at t
→ feature values with event_time <= t
→ processing state available by t
→ prediction
```

Production parity potrebuje rovnakú transformation semantics, units, missing handling, category vocabulary a freshness rules. Identický column name nepreukazuje identický value. Training-serving skew sa monitoruje cez paired sample re-computation a feature lineage.

Offline dataset často filtruje rows s failed joins; production musí pre tieto rows zvoliť fallback alebo error. Evaluation denominator zahŕňa aj coverage, inak score opisuje iba successful subset.

## 6. Serving metrics oproti model metrics

Serving health zahŕňa availability, latency, throughput, error rate, resource saturation, model loading a schema compatibility. Model health zahŕňa prediction distributions, calibration, ranking/error metrics a cohort behavior. Obe vrstvy sa spájajú, ale nemajú sa zamieňať.

```yaml
serving_signals:
  - request_rate
  - success_rate
  - latency_p50_p95_p99
  - feature_fetch_error_rate
  - fallback_rate
  - model_load_failure
model_signals:
  - score_distribution
  - predicted_positive_rate
  - calibration_after_maturity
  - cohort_precision_recall
  - coverage_and_abstention
```

Low latency s chybným fallbackom je serving success a business failure. High model score pri 70 % inference coverage nie je end-to-end acceptance.

## 7. Shadow deployment

Shadow deployment posiela live inputs candidate modelu bez ovplyvnenia action. Umožňuje overiť schema, feature retrieval, latency, resource use, prediction distribution a parity s offline replay.

```text
live request
├─ authoritative model → production action
└─ shadow candidate → logged prediction only
```

Shadow nevytvára candidate-induced outcomes a nemeria customer/reviewer response. Ak logs obsahujú sensitive features alebo predictions, potrebujú access a retention controls. Candidate shadow load nesmie poškodiť authoritative serving.

Acceptance porovnáva matched request IDs, missing-feature rate, latency a predictions. Rozdiel môže byť correct, ak online feature freshness je intended; root cause sa určuje cez feature-level evidence.

## 8. Canary rollout

Canary routuje malú časť eligible trafficu na candidate action path. Allocation unit musí zabrániť contamination, napríklad celý merchant alebo account zostáva v jednej variant-e.

```yaml
canary:
  allocation_unit: merchant_id
  candidate_share: 0.05
  sticky: true
  exclusion: [regulatory_high_risk, unresolved_incident]
  abort:
    serving_error_rate: 0.01
    false_block_guardrail: 0.002
```

Random row allocation môže viesť k tomu, že ten istý customer dostane inconsistent actions alebo variants ovplyvnia spoločnú queue. Canary evidence je krátkodobá a early labels často incomplete. Slúži na safety a compatibility, nie automaticky na finálny long-term business verdict.

## 9. A/B experiment a experimentálna jednotka

Online experiment porovná variants pod controlled allocation. Experimentálna jednotka sa volí podľa interference a action scope. Ak model ovplyvňuje merchant operations, randomizácia payments môže porušiť independence.

```text
eligible units
→ deterministic assignment
→ exposure log
→ variant policy
→ action
→ outcome
```

Exposure log musí dokazovať, že unit skutočne prešla variant path. Assignment bez successful model/policy exposure nie je treatment. Sample-ratio mismatch, crossover a missing exposure sú experiment incidents.

Business metrics sa predefinujú pred results. Novelty, learning effect a reviewer adaptation môžu meniť outcome v čase. Experiment duration musí pokryť label maturity a representative cycles.

## 10. Interference a shared capacity

Variants môžu súťažiť o spoločnú queue, budget alebo inventory. Candidate, ktorý posiela viac alerts, vytlačí baseline cases a mení ich outcome. Standard independent-unit analysis potom zlyháva.

```text
variant A alerts + variant B alerts
→ shared reviewer queue
→ capacity truncation
→ treatment of one unit affects another
```

Riešenie môže používať isolated capacity, cluster-level randomization alebo explicitnú system simulation. Ak izolácia nie je možná, limitation sa dokumentuje a causal claim sa zúži.

Atlas candidate zvýšil above-threshold volume; shared queue zahadzovala late-day cases oboch variants. Observed baseline outcome sa preto tiež zmenil.

## 11. Policy compliance a action rate

Prediction nemá business effect, ak downstream action nie je vykonaná. Monitoruje sa policy eligibility, admitted action, attempted action, successful completion a rejection/override.

```text
100000 eligible
→ 5200 above threshold
→ 2500 admitted to queue
→ 2200 reviewed
→ 1600 actions taken
→ 900 outcomes matured
```

Každý denominator odpovedá na inú otázku. Model recall nad eligible population sa nesmie nahradiť precision medzi reviewed cases. Human override môže byť benefit alebo signal poor explanation/usability; potrebuje reason and outcome analysis.

## 12. Business outcome hierarchy

Model metric je proxy. Business hierarchy oddeľuje leading technical signals od realized outcomes.

```yaml
outcome_hierarchy:
  technical:
    - inference_coverage
    - latency
    - prediction_distribution
  decision:
    - queue_admission
    - false_block_guardrail
    - reviewer_override
  operational:
    - review_latency
    - cases_completed
  business:
    - recovered_loss_eur
    - customer_churn
    - merchant_approval_rate
  harm:
    - false_block
    - appeal_overturn
```

Candidate nemá prejsť iba preto, že leading metric rastie. Lagging business outcomes môžu byť oneskorené, preto rollout používa predeclared staged gates a abort rules.

## 13. Delayed labels a maturity

Outcome môže dozrievať dni alebo mesiace. Report pred maturity podhodnocuje positives a môže differential ovplyvniť variants, ak candidate mení review speed.

```text
event time
→ action time
→ outcome observation window
→ label maturity cutoff
→ authoritative evaluation
```

Dashboard rozlišuje provisional a mature metrics. Vintage analysis porovnáva cohorts podľa event date a age. Late-arriving labels sa nepripisujú dnešnému trafficu bez event-time linkage.

Early proxy môže podporiť safety decision, ale musí byť validovaný voči mature outcome. Proxy drift sa monitoruje.

## 14. Selective labels a feedback

Model policy ovplyvňuje, ktoré observations získajú label. Reviewed cases majú potvrdený fraud častejšie než unreviewed cases, pretože process vytvára measurement.

```text
score
→ review selection
→ authoritative investigation label
→ future training data
```

Online precision medzi reviewed cases je conditional na policy. Zmena threshold-u mení population a metric. Exploration sample, delayed external labels alebo propensity-aware analysis môžu rozšíriť evidence. Bez toho sa model môže uzatvoriť do self-confirming loop-u.

## 15. Distribution a concept drift

Data drift znamená zmenu input/prediction distribution. Concept drift znamená zmenu relationship medzi inputs a target. Neither sa nedokazuje jedným distance metricom.

```text
input distribution changed
prediction distribution changed
label prevalence changed
conditional performance changed
```

Drift signal spúšťa hypothesis, nie automatický retrain. Product launch môže legitímne zmeniť geography distribution bez zhoršenia outcome. Concept drift potrebuje mature labels alebo trusted proxy.

Cohort a time analysis oddeľuje broad shift od localized incidentu. Reference window a binning sú versionované.

## 16. Training-serving skew a prediction parity

Paired parity test vezme production request a znovu ho spracuje trusted offline pipeline. Porovná intermediate features, preprocessing output a prediction.

```text
same request ID
→ online feature vector
→ offline reconstructed feature vector
→ feature diff
→ prediction diff
```

Rozdiel sa kategorizuje ako expected freshness, unavailable historical state, code/version mismatch, serialization precision alebo bug. Aggregate correlation môže skryť critical feature mismatch.

## 17. Fallbacks a degraded modes

Serving failure často aktivuje fallback: previous model, rules, default score, cached prediction alebo abstention. Fallback je policy generation s vlastným outcome.

```yaml
fallback:
  trigger: feature_timeout_or_model_unavailable
  action: route_to_manual_review
  max_rate: 0.005
  audit: required
```

Default-low-risk fallback môže zlepšiť latency a znížiť alerts, ale zvýšiť missed fraud. Reporting musí priradiť outcomes k actual decision path. Hidden fallback traffic sa nesmie zahrnúť ako candidate model prediction.

## 18. Human workflow a operational adoption

Model value závisí od toho, či ľudia rozumejú outputu, dôverujú správne, majú capacity a môžu konať. Training, UI, explanation a escalation sú system components.

Reviewer môže ignorovať candidate alerts pre low-quality reason codes alebo byť preťažený. Adoption metric bez correctness môže odmeňovať automation bias. Hodnotí sa action agreement, override, handling time, outcome a cohort burden.

Rollout zahŕňa operational readiness: runbook, owner, alerts, rollback, support a incident communication.

## 19. Offline-online metric mapping

Každá offline metric má explicitnú online counterpart alebo limitation.

```yaml
metric_mapping:
  offline_average_precision:
    online: mature_label_average_precision_on_all_scored_eligible
  offline_precision_at_2500:
    online: daily_queue_precision_at_capacity
  offline_captured_loss:
    online: recovered_loss_after_action_and_maturity
  offline_latency_benchmark:
    online: end_to_end_prediction_latency_p95
```

Mapping určuje denominator a delay. Ak online counterpart neexistuje, offline metric zostáva model-selection evidence a nesmie sa prezentovať ako realized value.

## 20. Baseline a counterfactual

Production outcome sa porovnáva s relevantným baseline: previous model/policy, control variant alebo expected outcome bez action. Pre-post comparison je citlivý na seasonality a external changes.

```text
candidate period outcome
- baseline/control counterfactual
≠ raw candidate outcome alone
```

Model môže recoverovať viac strát v absolútnom čísle len preto, že traffic alebo fraud prevalence narástla. Normalization, experiment alebo causal design je potrebný podľa claimu.

## 21. Rollback a roll-forward authority

Rollback nie je iba deployment revert. Composite model includes feature schema, calibrator, threshold, queue a UI. Compatibility môže brániť návratu starého artifactu.

```yaml
rollback_subject:
  model_digest: previous-approved
  preprocessing: risk-v8
  calibration: cal-v4
  policy: queue-v7
  feature_contract_compatible: true
```

Unknown-outcome deployment operation potrebuje authoritative read-back pred retry. Rollback trigger môže vychádzať zo serving guardrail alebo business harm; late metric incident môže vyžadovať freeze expansion a manual containment namiesto okamžitého model revertu.

## 22. Worked incident `ML-PAY-89`

Atlas offline test používal mature successfully joined operations. Candidate dosiahol vyššiu AP, nižší log loss a väčší simulated captured loss pri top 2 500. Replay však aplikoval `merchant-priority-v2`, zatiaľ čo production queue používala v3 s extra campaign penalty.

Po canary rollout-e live feature store pri špičke timeoutoval pre new merchants. Serving fallback nastavoval low-risk score, takže inference success dashboard ostal zelený, ale 8 % campaign traffic neprešlo candidate modelom. Shared queue prijala 2 500 cases, reviewers spracovali iba 2 100 a late-day campaign cases mali vyššiu drop rate.

```text
offline successful-join population
→ candidate score improvement
→ production feature timeout
→ hidden low-risk fallback
→ different queue boost
→ capacity and reviewer truncation
→ selective mature labels
→ lower realized recovery
```

Prvé online porovnanie počítalo precision iba medzi reviewed mature cases. Candidate tak vyzeral lepšie, pretože unreviewed false negatives nemali label. Recovered loss klesol, ale raw traffic a fraud prevalence sa tiež zmenili. Root cause nebol izolovaný model regression; išlo o skew, fallback, policy mismatch, capacity a denominator failure.

## 23. Competing failure hypotheses

Offline-online gap sa diagnostikuje podľa najskoršej vrstvy, kde sa evidence odchýli. Najprv sa overí population a feature coverage, potom prediction parity, policy/action execution a nakoniec labels/outcome attribution.

- population mismatch — production eligibility alebo cohort mix sa líši od offline testu;
- point-in-time leakage — offline features používajú future alebo latest state;
- feature skew — online value, transformation, freshness alebo missing handling sa líši;
- serving coverage failure — errors, timeout, fallback alebo abstention odstraňujú traffic z model path;
- artifact mismatch — deployed model/preprocessing/calibrator digest nie je evaluated subject;
- policy mismatch — threshold, ranking, boost, rule alebo tie-breaker sa líši od simulation;
- capacity interference — queue, budget alebo reviewer throughput mení admitted actions;
- action non-compliance — downstream system alebo human nevykoná intended action;
- delayed-label bias — provisional metrics používajú immature outcomes;
- selective-label bias — labels vznikajú prevažne pre acted-on cases;
- drift — population, prevalence alebo conditional relationship sa zmenila;
- counterfactual error — raw outcome sa porovnáva bez valid control/baseline;
- metric mapping failure — offline proxy nemá rovnaký online denominator alebo meaning;
- feedback loop — deployed policy mení future data a labels.

Stabilné matched-request predictions s odlišnou queue membership podporujú policy hypothesis. Rozdiel už v feature vectoroch ukazuje skew. Rovnaké actions s odlišnými mature outcomes podporujú drift alebo external response zmenu.

## 24. Evidence-preserving containment a recovery

Containment zmrazí rollout expansion a zachová exposure, request, feature, prediction, policy, queue, action a outcome logs. Nemá sa okamžite retrainovať, kým nie je známe, ktorá vrstva zlyhala.

```text
freeze expansion
→ preserve composite generations and end-to-end IDs
→ reconcile eligibility and coverage
→ run matched online/offline parity
→ reconcile policy and queue decisions
→ verify action completion
→ wait/recompute mature labels
→ test competing hypotheses
→ rollback component or issue successor generation
→ staged second-window acceptance
```

Ak zlyhal feature store, model artifact môže zostať approved a serving recovery vytvorí successor. Ak replay policy bola chybná, offline verdict sa invaliduje. Ak concept drift je confirmed, retraining používa nový independent acceptance window.

## 25. Acceptance contract

Positive acceptance spája offline model evidence s serving, policy, action a business metrics. Exact composite subject, exposure log, coverage denominator, label maturity, cohort guards, rollback a owner sú povinné.

Recovery acceptance preukazuje, že corrected layer zlepšila matched parity a mature production outcome bez vytvorenia nového harmu. Forbidden paths zahŕňajú promotion iba podľa offline average, filtrovanie failed inference, shadow outcome ako business effect, provisional labels ako final verdict, pre-post comparison bez baseline, metric iba na reviewed cases, hidden fallback a attribution production loss iba model weights bez layer evidence.

Second-operation test reprodukuje offline-to-serving parity pre uložené requests. Second-window test používa novšie mature outcomes. Rollout test prechádza shadow, canary a controlled expansion s predeclared abort rules.

```yaml
acceptance:
  offline_subject_and_limitations: passed
  deployed_composite_identity: passed
  serving_and_feature_coverage: passed
  policy_action_and_capacity_parity: passed
  mature_business_and_harm_outcomes: passed
  rollback_and_ownership: passed
  second_window: passed
```

## Kontrolné otázky

1. Prečo offline score nie je production business outcome?
2. Aké vrstvy spájajú model artifact s realized outcome?
3. Čo replay dokazuje a aký counterfactual nevie vytvoriť?
4. Prečo failed feature joins patria do evaluation denominatora?
5. Aký je rozdiel medzi serving a model health?
6. Čo shadow deployment overuje a čo neoveruje?
7. Ako canary a A/B experiment odlišujú safety od long-term impactu?
8. Prečo experimentálna jednotka a interference matter?
9. Ako queue capacity mení effective model metric?
10. Prečo delayed a selective labels skresľujú early online report?
11. Aký je rozdiel medzi data a concept drift?
12. Ako paired parity test izoluje training-serving skew?
13. Prečo fallback musí mať vlastnú outcome lineage?
14. Ako human adoption a action completion vstupujú do model value?
15. Prečo pre-post comparison bez controlu nemusí identifikovať model effect?
16. Čo pokazilo lifecycle v `ML-PAY-89`?
17. Aké positive, recovery, forbidden, rollout a second-window testy uzatvárajú offline-online contract?

## Glossary impact

Relevantné pojmy: offline evaluation, production outcome, replay, counterfactual, point-in-time correctness, feature parity, serving metric, model metric, shadow deployment, canary rollout, online experiment, experimental unit, exposure log, interference, policy compliance, action rate, delayed label, label maturity, selective label, data drift, concept drift, prediction parity, fallback policy, metric mapping, business outcome hierarchy, control variant, rollout abort, composite rollback a offline-production acceptance contract.

## Primárne zdroje

- [Google — Rules of Machine Learning](https://developers.google.com/machine-learning/guides/rules-of-ml)
- [Hidden Technical Debt in Machine Learning Systems](https://papers.nips.cc/paper/5656-hidden-technical-debt-in-machine-learning-systems)
- [The ML Test Score](https://research.google/pubs/the-ml-test-score-a-rubric-for-ml-production-readiness-and-technical-debt-reduction/)
- [scikit-learn — Common pitfalls and recommended practices](https://scikit-learn.org/stable/common_pitfalls.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Reproducibility a random seeds](reproducibility-random-seeds.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: ML troubleshooting mental model →](ml-troubleshooting-mental-model.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
