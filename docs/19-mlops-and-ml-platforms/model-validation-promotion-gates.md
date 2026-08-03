# Model validation a promotion gates

Model validation rozhoduje, či candidate spĺňa presne definované technické, štatistické, business, bezpečnostné a governance podmienky. Promotion gate následne rozhoduje, či sa tento validated candidate môže stať release inputom pre konkrétny environment. Successful evaluation job, vysoká aggregate metric alebo registrácia modelu nie sú samy osebe promotion verdict.

Gate musí byť viazaný na exact candidate, baseline, dataset, evaluator, thresholds, segmenty, package a policy generation. Ak sa zmení iba threshold policy alebo feature service, model weights môžu zostať rovnaké, ale release potrebuje novú validation generation. Naopak, rerun rovnakého evaluatora nad rovnakým immutable subjectom má vytvoriť rovnaký verdict alebo vysvetlenú nondeterministic odchýlku.

V incidente `MLOPS-PAY-93` Atlas candidate 141 prekonal production model v aggregate ROC AUC. Evaluation však používala dataset s inou fraud prevalence, neobsahovala high-value merchant cohort, calibration report bol z predchádzajúceho runu a action-capacity simulation použila 5 000 denných reviews namiesto reálnych 2 500. Pipeline vyhodnotila jediný threshold ako green a posunula Registry alias. Candidate bol lepší v rankingu, ale horší v top-K precision pri skutočnej kapacite a vytvoril neakceptovateľný segmentový harm.

## 1. Dominantný validation lifecycle

Validation je reproducible decision, nie vizuálna kontrola leaderboardu.

```text
candidate + baseline
→ exact evaluation dataset a cohorts
→ evaluator a metric generation
→ technical/package checks
→ statistical a business metrics
→ segment, calibration, robustness a harm guardrails
→ threshold/policy simulation
→ complete validation bundle
→ gate decision
→ promotion eligibility pre konkrétny environment
```

Gate môže skončiť ako pass, fail, blocked alebo manual-review-required. Missing mature labels, incomplete artifact alebo neplatný baseline nie sú automatický fail modelu; sú blocked verdict, pretože dôkaz nie je dostatočný.

## 2. Exact validation subject

Validation subject spája všetky authority, ktoré môžu zmeniť verdict. Candidate a baseline určujú porovnávané artifacts, evaluation dataset určuje population a labels, evaluator určuje výpočet a policy určuje rozhodnutie. Ak čo i len jedna z týchto generácií zostane implicitná, rovnaké modely môžu pri ďalšom spustení dostať iný výsledok bez vysvetliteľnej príčiny. Manifest preto nie je administratívny zoznam; je to reprodukčný contract, podľa ktorého sa dajú znovu zostaviť predictions, metrics aj promotion decision.

```yaml
validation_subject: MLOPS-PAY-VAL-2026-08-03-141
candidate:
  registered_model: dev.ml_team.risk_model
  version: 141
  package_digest: sha256:6a11...90fd
baseline:
  release_subject: MLOPS-PAY-RISK-PROD-2026-07-r29
  package_digest: sha256:1f20...aa77
evaluation_dataset: sha256:cc82...109e
split_generation: temporal-out-of-time-v4
evaluator_image: registry.example/ml/evaluator@sha256:909a...11bc
metric_policy: risk-promotion-policy-v8
business_capacity: 2500_reviews_per_day
feature_service: risk_features_v7
required_segments:
  - high_value_merchants
  - new_merchants
  - countries_eu
  - countries_non_eu
```

Validation bundle musí obsahovať aj raw prediction table alebo durable reference, sample membership, metrics, plots, threshold simulation a gate reasons. Screenshot dashboardu nie je reprodukovateľný artifact.

## 3. Candidate, baseline a challenger identity

Candidate je exact model package. Baseline môže byť production release, posledný accepted candidate alebo business rule. Tieto baseline-y odpovedajú na odlišné otázky. Porovnanie s posledným experimentom nepreukazuje zlepšenie oproti live systému.

Production baseline musí používať rovnakú evaluation population a evaluator generation. Ak starý model nevie načítať nové feature schema, porovnanie potrebuje compatibility adapter alebo historický feature contract. Adapter je súčasťou subjectu, pretože môže meniť výsledky.

Challenger môže prejsť absolute minimum, ale neprekonať baseline o required margin. Iný use case môže akceptovať non-inferiority, ak candidate výrazne znižuje latency alebo cost. Gate policy preto kombinuje metric quality s operational objectives.

## 4. Dataset a evaluation estimand

Gate musí vysvetliť, čo dataset reprezentuje. Random test split, out-of-time population, replay, curated edge cases a post-deployment shadow sample merajú odlišné estimands. Jeden dataset nemôže automaticky pokryť všetky.

Evaluation manifest uvádza observation unit, eligibility, event-time interval, label cutoff, exclusion rules, duplicate policy a cohort denominators. Test data nesmie byť opakovane používaná na tuning bez acknowledgment-u, pretože sa stáva de facto validation setom.

Candidate a baseline dostanú identické samples a feature semantics. Ak jeden model používa fallback alebo chýbajúce feature, validation to zaznamená ako system behavior, nie iba ako model metric.

## 5. Metric thresholds a baseline comparison

MLflow classic evaluation poskytuje `mlflow.models.evaluate()` a samostatné `mlflow.validate_evaluation_results()`. Current API používa `MetricThreshold` pre absolute threshold, minimum absolute change a minimum relative change.

```python
import mlflow
from mlflow.models import MetricThreshold

candidate_result = mlflow.models.evaluate(
    candidate_uri,
    eval_data,
    targets="label",
    model_type="classifier",
)
baseline_result = mlflow.models.evaluate(
    baseline_uri,
    eval_data,
    targets="label",
    model_type="classifier",
)

thresholds = {
    "roc_auc": MetricThreshold(
        threshold=0.82,
        min_absolute_change=0.01,
        greater_is_better=True,
    ),
    "log_loss": MetricThreshold(
        threshold=0.42,
        greater_is_better=False,
    ),
}

mlflow.validate_evaluation_results(
    validation_thresholds=thresholds,
    candidate_result=candidate_result,
    baseline_result=baseline_result,
)
```

API success preukazuje iba zadané metrics a thresholds. Nepreukazuje segmenty, capacity, uncertainty ani business outcome, pokiaľ neboli explicitne zahrnuté.

## 6. Aggregate metric oproti decision metric

ROC AUC hodnotí ranking across thresholds. Production action môže používať top-K queue alebo fixed threshold. Gate preto musí simulovať actual decision policy.

```text
candidate probability
→ calibration alebo raw score
→ threshold/ranking policy
→ capacity truncation
→ human/action completion
→ business outcome
```

Pri capacity 2 500 reviews denne sa hodnotí precision@2500, recall captured, recoverable value, cohort representation a queue stability. Candidate môže mať vyššiu AUC a horší top-K result. Promotion podľa nesprávneho estimandu je policy failure, nie paradox metricu.

## 7. Segment a harm guardrails

Aggregate pass nesmie zakryť slabý segment. Gate definuje required cohorts, minimum sample a acceptable degradation. Small cohort s vysokou uncertainty môže vyžadovať manual review alebo additional data, nie automatické pass/fail podľa noisy point estimate.

```yaml
segment_gates:
  high_value_merchants:
    precision_at_capacity_min: 0.62
    recall_drop_vs_baseline_max: 0.01
  new_merchants:
    false_positive_rate_max: 0.08
  countries_non_eu:
    calibration_error_max: 0.04
```

Sensitive alebo proxy attributes majú governance boundary. Segment evaluation nie je oprávnenie používať attribute v serving decisione. Access, retention a reporting musia byť oddelené.

## 8. Calibration, uncertainty a stability

Ak action interpretuje score ako probability, gate zahŕňa calibration na relevantnej population. Reliability diagram, Brier decomposition alebo calibration error sa viažu na dataset a binning generation.

Uncertainty sa nepoužíva ako dekoratívny interval. Gate určí method, assumptions a decision rule. Multi-seed training stability alebo bootstrap interval môže odhaliť, že apparent improvement je menší než variance. Jeden lucky seed nemá automaticky dostať production promotion.

Stability gate môže vyžadovať minimum performance across seeds alebo confidence, že candidate nie je horší než baseline o defined margin. Compute cost je vyšší, preto sa expensive stability test môže spustiť až pre finalists.

## 9. Robustness a failure behavior

Validation zahŕňa missing values, unknown categories, out-of-range inputs, schema changes, adversarial alebo corrupted records a dependency failures. Model server má reagovať definovaným errorom alebo fallbackom. Tichá imputácia môže byť validná iba ak je súčasťou package a evaluation.

```text
normal input
+ edge cases
+ malformed request
+ stale feature
+ unavailable optional dependency
→ expected output alebo explicitné odmietnutie
```

Robustness test nepreukazuje všetky future conditions, ale chráni known failure contract. Fallback quality sa hodnotí osobitne; fallback activation rate je production guardrail.

## 10. Package, signature a runtime gates

Candidate metric je irelevantná, ak package sa nedá bezpečne načítať. Gate overuje artifact checksums, signature, dependencies, model signature, serialization trust, clean-environment load a protocol request.

Runtime gate overí latency, memory, startup, concurrency a output parity na target-like hardware. Performance threshold sa viaže na exact server config a request shape. Single-request local timing nie je production capacity proof.

Supply-chain controls zahŕňajú image digest, SBOM, vulnerability policy a provenance. Security exception musí byť explicitne approved a expirovať.

## 11. Policy a gate generations

Promotion policy je versionovaný artifact. Zmena thresholdov alebo required cohorts mení verdict aj bez zmeny modelu. Starý validation result sa nesmie automaticky interpretovať podľa novej policy.

```yaml
policy_generation: risk-promotion-policy-v8
rules_digest: sha256:55dd...a901
evaluator_compatibility: evaluator-v12
valid_for_environments:
  - staging
expires_after: 14d
```

Production gate môže byť prísnejší než staging. Reuse bundle je možné iba ak environment policy explicitne akceptuje jeho evidence a ešte neexpirovala data freshness.

## 12. Human approval a separation of duties

Automated gates spracujú deterministic rules. Human approval rieši risk acceptance, business trade-off alebo incomplete evidence. Approver vidí exact release subject, failed/waived rules a expected exposure.

Approval nie je editovateľná poznámka bez scope-u. Record obsahuje approvera, role, timestamp, candidate digest, policy generation, waiver a expiry. Osoba, ktorá vytrénovala model, nemusí mať sama authority schváliť production promotion.

Waiver nezmení fail na technický pass. Verdict zostáva failed-with-approved-exception, aby audit vedel rekonštruovať rozhodnutie.

## 13. Unknown outcomes a idempotency

Timeout pri zápise validation resultu alebo Registry tagu vytvára unknown outcome. Operation ID a conditional state zabraňujú duplicate promotion.

```yaml
operation_id: MLOPS-PAY-93-PROMOTE-141
expected_alias_generation: 52
candidate_version: 141
validation_bundle_digest: sha256:3e20...c741
```

Po timeout-e pipeline prečíta Registry tags, alias history a audit. Ak mutation prebehla, vráti pôvodný result. Ak alias posunul iný operation, starý request nesmie prepisovať novší state.

## 14. Competing failure hypotheses

Keď candidate zlyhá gate, príčinou môže byť skutočne slabší model, dataset mismatch, stale baseline, evaluator defect, wrong threshold policy, missing segment, package/runtime regression alebo incomplete evidence. Gate report musí ukázať first failed layer.

Retraining nie je default response na package-load failure ani wrong capacity simulation. Oprava evaluatora a rerun vytvoria novú validation generation nad rovnakým candidate-om. Zmena modelu pred odstránením evidence chyby ničí atribúciu.

## 15. Recovery a acceptance

Containment zastaví promotion a zachová candidate aj bundle. Recovery opraví jednu authority: dataset, evaluator, policy alebo package. Nový verdict odkazuje na superseded result.

Pozitívny test potvrdí všetky required metrics, segments, package a runtime gates. Forbidden test odmietne missing baseline, iný dataset medzi models, aggregate-only pass a approval pre iný digest. Recovery test simuluje evaluator defect a overí nový bundle bez retrainingu. Second-operation test zopakuje promotion request a očakáva no-op.

Validation je prijatá, keď každý pass má reprodukovateľný dôkaz, každý fail ukazuje konkrétnu rule a promotion sa viaže na immutable candidate a environment policy. Gate má znižovať uncertainty, nie iba produkovať zelenú ikonu.

## Primárne zdroje

- [MLflow — Model evaluation](https://mlflow.org/docs/latest/ml/evaluation)
- [MLflow — Model API and MetricThreshold](https://mlflow.org/docs/latest/api_reference/python_api/mlflow.models.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Continuous Training a retraining triggers](continuous-training-retraining-triggers.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Batch, online a streaming inference →](batch-online-streaming-inference.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
