# Feature engineering a feature selection

Feature engineering určuje, akú informáciu model z raw observations vôbec dostane. Feature selection určuje, ktorú časť dostupnej representation pipeline ponechá pre fitted estimator. Ani jeden krok nie je neutrálne „vylepšenie dát“. Môže zaviesť future information, identity memorization, unstable categories, proxy discrimination, vysokú serving latency alebo target leakage. Feature sa preto posudzuje ako versionovaný information contract s event-time, source authority, computation a production-availability hranicou.

V incidente `ML-PAY-84` Atlas pridal stovky merchant, device a behavior features, aby získal späť score po oprave splitu. Selector sa fitol na všetkých labels vrátane test setu. Niekoľko top features boli post-review counters, current-state aggregates a merchant identifiers. Offline model vyzeral silný, ale online path nevedel niektoré values vypočítať v prediction time a high-cardinality IDs umožnili zapamätať historical merchants. Zlyhanie nebolo iba „príliš veľa features“; chýbal feature lifecycle a selection evidence.

## 1. Dominantný feature lifecycle

Feature lifecycle začína business mechanismom a prediction-time otázkou. Potom sa určí source event/entity, computation window, transformations, freshness, missingness, cost a serving path. Selection sa vykonáva iba v training/validation loop-e a final feature set sa publikuje ako schema generation spolu s preprocessing a model artifactom.

```text
business hypothesis
→ raw source a event/entity identity
→ point-in-time feature definition
→ offline/online computation
→ validation a lineage
→ candidate feature inventory
→ selection fit iba na allowed train domain
→ locked feature schema/order
→ estimator artifact
→ serving parity, monitoring a retirement
```

Feature engineering mení information space; selection mení model dependency graph. Obe operácie môžu overfitnúť validation feedback a musia byť súčasťou experiment lineage.

## 2. Exact feature subject

```yaml
feature_subject: merchant_decline_rate_1h-v4
entity: merchant_id
prediction_subject: merchant_operation_id
source_events: authorization_attempt-v7
source_authority: payments-event-ledger
window:
  event_time: (prediction_time - 1h, prediction_time]
  watermark: 5m
numerator: declined_attempts
denominator: all_attempts
zero_denominator: null
late_event_policy: exclude_after_watermark
unit: ratio
freshness_slo: 2m
offline_implementation: spark:git-7f4d11
online_implementation: feature-service:release-91
validation:
  range: [0, 1]
  required_identifiers: [merchant_id, prediction_time]
owner: risk-feature-team
```

Feature name `decline_rate_1h` nestačí. Window inclusion, attempt deduplication, late events a denominator semantics môžu meniť value. Version sa musí zmeniť pri semantic change, aj keď output dtype zostane float.

## 3. Feature engineering ako business representation

Feature engineering prevádza raw observations na representation relevantnú pre task. Môže používať domain aggregates, ratios, interactions, time since event, cyclical time, text vectors, image embeddings alebo graph relationships. Dobrá feature znižuje burden modelu, ale zároveň kodifikuje assumptions.

```text
raw:
operation amount, merchant history, attempts, device events

engineered:
amount relative to merchant median
retry count before prediction time
unique devices in past 24h
seconds since merchant first seen
```

Každá derived feature musí byť computable z information dostupnej v prediction time. `amount / merchant_median_30d` potrebuje point-in-time median excluding current/future events podľa contractu. Current warehouse aggregate môže obsahovať celý future month a vytvoriť leakage.

## 4. Aggregates a windows

Window features majú time axis, entity key, event inclusion, late-data a reset semantics. „Count last 24 hours“ je neúplné bez toho, či ide o event time alebo processing time, inclusive boundaries, unique operations alebo attempts a či current event vstupuje do countu.

```sql
SELECT
  o.merchant_operation_id,
  COUNT(DISTINCT h.merchant_operation_id) AS merchant_ops_24h
FROM operations o
LEFT JOIN operations h
  ON h.merchant_id = o.merchant_id
 AND h.authorization_received_at >= o.authorization_received_at - INTERVAL '24 hours'
 AND h.authorization_received_at <  o.authorization_received_at
GROUP BY o.merchant_operation_id;
```

Upper boundary vylučuje current operation, ak contract meria previous history. Iný use case môže current event zahrnúť. Query semantics musia byť rovnaké offline aj online.

Window features sú citlivé na late events a backfill. Recomputed historical feature po príchode late eventu môže byť správnejšia než value, ktorú production poznala v reálnom čase. Pre training treba rozhodnúť, či modelovať ideal event-time alebo actual available-at-time state. Serving realism často vyžaduje latter.

## 5. Ratios, denominators a small-sample instability

Ratio môže normalizovať scale, ale denominator vytvára instability. Merchant s jedným pokusom a jedným decline má rate 100 %, rovnako ako merchant s tisíc declines z tisíc attempts, no uncertainty je odlišná.

```text
merchant A: 1/1 = 1.0
merchant B: 1000/1000 = 1.0
```

Feature set môže pridať denominator count, smoothing alebo Bayesian prior. Smoothing parameters musia byť fitted/pinned a nesmú používať future labels, ak ide o target-related statistic.

Zero denominator má explicitný missing/undefined state. Tiché `0` tvrdí, že rate bola measured a nulová.

## 6. Interactions a polynomial features

Interaction feature reprezentuje combined effect inputs, ktorý jednoduchý model nemusí zachytiť. Napríklad high amount môže byť risk iba pri new device alebo cross-border context-e.

```python
from sklearn.preprocessing import PolynomialFeatures

interactions = PolynomialFeatures(
    degree=2,
    interaction_only=True,
    include_bias=False,
)
```

Polynomial expansion môže dramaticky zvýšiť dimensionality a collinearity. Fit pipeline musí udržať feature names/order a selection/regularization. Tree a neural models môžu interactions naučiť implicitne, ale explicitná feature môže stále zlepšiť sample efficiency alebo interpretability.

Interaction hypothesis má domain rationale a validation. Enumerovať všetky combinations bez cost/overfit kontroly nie je automatická feature engineering stratégia.

## 7. Time a cyclical features

Hour, weekday, month alebo seasonality majú cyclic structure. Integer hour `23` a `0` sú numericky ďaleko, hoci časovo susedia. Sine/cosine encoding môže zachytiť cycle.

```python
import numpy as np

hour = timestamp.hour
hour_sin = np.sin(2 * np.pi * hour / 24)
hour_cos = np.cos(2 * np.pi * hour / 24)
```

Timezone a daylight-saving policy sú súčasťou feature contractu. UTC hour a merchant-local hour odpovedajú na iné otázky. Locale lookup musí byť point-in-time a available online.

Seasonal feature môže byť proxy pre campaign alebo policy changes. Model môže zlyhať pri new period mimo training coverage.

## 8. Identity, memorization a high cardinality

Customer, merchant, device alebo document IDs môžu umožniť modelu zapamätať historical target rather than generalize. Niekedy identity effect je legitímny — existing merchant history je predictive — ale use case musí odlíšiť known-entity a cold-start performance.

Naive one-hot merchant ID vytvorí high-dimensional sparse feature a unseen merchants all-zero/unknown. Target encoding merchant ID môže priamo leaknúť labels bez out-of-fold/time-safe procedure.

```text
identity feature value
→ historical association
→ memorization risk
→ poor unseen-entity generalization
```

Safer alternatives môžu byť point-in-time aggregates s minimum support, learned embeddings s regularization alebo hierarchical features. Stále treba unseen entity test a privacy/security review.

Raw identifiers môžu byť potrebné na joins/groups/audit, ale nemusia vstupovať do model inputu. „Je v datasete“ neznamená „je feature“.

## 9. Proxy features a fairness/security boundary

Feature môže byť proxy pre protected alebo sensitive attribute aj bez explicitného field-u. Postal code, language, device price alebo behavior môže korelovať so socioeconomic alebo demographic group. Feature selection podľa predictive power môže proxy zvýhodniť.

Responsible use vyžaduje purpose, legal/policy review, cohort evaluation a possible constraints. Odstránenie explicitnej protected feature samo nezaručuje fairness. Naopak, protected attribute môže byť potrebný pre audit/evaluation, ale nesmie vstúpiť do modelu alebo serving response podľa contractu.

Security risk zahŕňa adversarial manipulation. Feature ľahko kontrolovateľná attackerom môže byť gaming vector. Stable server-observed features môžu byť robustnejšie, no majú latency/cost a privacy consequences.

## 10. Feature extraction oproti feature selection

Feature extraction vytvára novú representation z raw alebo existing features, napríklad TF-IDF, PCA alebo embeddings. Feature selection vyberá subset existing dimensions alebo groups. Extraction môže byť fitted a meniť interpretability; selection zachová selected dimensions, ale môže byť unstable.

```text
feature extraction:
raw text → 50k token dimensions → 256 latent components

feature selection:
50k token dimensions → selected 5k dimensions
```

PCA components nie sú pôvodné features a ich signs/order môžu mať algorithmic indeterminacy. Selection output musí uchovať names a mapping. Obe operácie patria do pipeline fit boundary.

## 11. Filter methods

Filter methods hodnotia features podľa statistic relationship k targetu alebo intrinsic properties nezávisle od final estimatoru. Príklady: variance threshold, univariate correlation, ANOVA F, mutual information alebo chi-squared score.

```python
from sklearn.feature_selection import SelectKBest, mutual_info_classif

selector = SelectKBest(
    score_func=mutual_info_classif,
    k=50,
)
```

Ak selector vidí all data labels pred split/cross-validation, leakne selection information. Musí byť krok pipeline fitnutý iba na fold-train. Univariate method môže prehliadnuť feature užitočnú iba v interaction a vybrať redundantné correlated features.

Statistical score nepreukazuje causal relevance ani production availability.

## 12. Wrapper methods

Wrapper methods opakovane fitujú estimator na rôznych feature subsets a vyberajú podľa validation performance. Recursive feature elimination je príklad. Sú computationally drahé a môžu silno overfitnúť validation/CV pri veľkom search space.

```python
from sklearn.feature_selection import RFECV

selector = RFECV(
    estimator=base_estimator,
    step=5,
    min_features_to_select=20,
    cv=group_cv,
    scoring="average_precision",
)
```

CV splitter musí rešpektovať group/time. Whole RFECV patrí do outer selection loopu; final performance estimate potrebuje untouched test alebo nested evaluation. Feature stability naprieč folds je dôležitá diagnostic evidence.

## 13. Embedded methods

Embedded methods vykonávajú selection počas model fitu, napríklad L1 regularization alebo tree importance threshold. Selection závisí od estimatoru, regularization, feature scale a correlated alternatives.

```python
from sklearn.feature_selection import SelectFromModel
from sklearn.linear_model import LogisticRegression

selector = SelectFromModel(
    LogisticRegression(
        penalty="l1",
        solver="liblinear",
        C=0.1,
    )
)
```

Pri correlated features môže model arbitrarily vybrať jednu a vyradiť druhú. To nepreukazuje, že vyradená feature je business irrelevant. Importances môžu byť biased podľa cardinality/model structure a musia sa interpretovať opatrne.

Embedded selector je fitted state a musí sa package-núť spolu s estimatorom.

## 14. Feature groups a dependency-aware selection

Niektoré features zdieľajú source, transform alebo serving dependency. Vybrať jednu feature môže stále vyžadovať celý drahý external lookup. Selection podľa column count neoptimalizuje latency/cost.

```yaml
feature_group: merchant_velocity
source: online-aggregate-store
latency_budget_ms: 8
features:
  - ops_5m
  - ops_1h
  - declines_1h
  - unique_devices_24h
```

Group selection môže odstrániť celý dependency alebo zachovať coherent set. Cost-aware objective zvažuje predictive gain, compute/storage/latency, freshness, availability a operational ownership.

Model s o 0,1 % lepšou metric a critical cross-region lookupom môže mať horší production outcome.

## 15. Feature freshness a availability

Feature môže existovať offline, ale byť príliš stale alebo pomalá online. Contract potrebuje feature timestamp, materialization delay a maximum age. Serving musí rozhodnúť, čo robiť pri stale/missing value.

```text
feature event time
→ ingestion
→ aggregation/materialization
→ online store
→ inference read
```

Freshness lag je part of input. Model training na perfectly recomputed history a serving na 10-minute stale aggregates vytvára skew. Training examples môžu potrebovať simulation actual historical availability.

Fallback na previous value môže byť validný iba s age indicatorom a accepted horizon. Tiché reuse stale value maskuje outage.

## 16. Feature selection stability

Selected subset môže meniť pri small data perturbation, fold alebo seed, najmä pri correlated features a weak signals. Stability analysis porovná selected features naprieč resamples/time windows.

```text
feature selected in 5/5 folds → stable evidence
feature selected in 1/5 folds → fragile alebo cohort-specific
```

Stability nie je jediný criterion; rare-cohort feature môže byť legitímne selected len v folds s daným cohortom. Výsledok treba prepojiť s group/time composition.

Frequent churn komplikuje serving schema, monitoring a explainability. Feature schema promotion môže vyžadovať minimum stability alebo explicitný rationale.

## 17. Feature registry a lineage

Feature registry/catalog môže uchovať name, version, entity, source, owner, transformation, freshness, schema a consumers. Registry entry je intended contract; production read-back musí potvrdiť actual loaded implementation a value behavior.

```text
feature definition commit
→ batch/stream job generation
→ materialized values
→ dataset snapshot
→ model dependency
→ online service lookup
```

Lineage umožňuje odpovedať, ktoré models ovplyvní source/schema change a ktoré feature versions možno retire-nuť. Registry nesmie vytvoriť illusion, že online/offline parity je automatická.

## 18. Monitoring selected features

Monitoruje sa availability, missing/unknown rate, freshness, schema/range, distribution, parity, latency a model dependence. Features s high importance a low reliability môžu byť operational single point of failure.

Feature alert musí uviesť affected model versions, populations a fallback. Distribution shift môže byť legitimate; source outage môže vyzerať ako shift. Pair raw/source metrics s model input metrics.

```text
feature missing spike
+ source success drop
→ pipeline incident

feature distribution shift
+ source healthy
→ population/business change alebo semantic drift
```

## 19. Worked incident `ML-PAY-84`

Atlas candidate inventory mal 640 features. Target-based selector bol fitnutý nad full datasetom vrátane test labels a vybral post-review aggregates, current merchant chargeback rate a hashed merchant ID. Features dosiahli vysoký univariate score, pretože obsahovali future outcomes alebo memorized entities.

Online service nemal post-review data a nahradil values nulou. Current chargeback aggregate sa batchovo aktualizoval raz denne, kým offline recomputation používala final history. Hashed merchant ID fungoval pre known merchants, ale cold-start cohort sa prepadol.

Selection report ukazoval iba top scores, nie availability, source, time semantics alebo fold stability. Pri opravenom point-in-time/grouped pipeline väčšina top features stratila signal. To neznamenalo, že selector zlyhal; optimalizoval contaminated information space.

Root causes:

```text
feature definitions bez prediction-time contractu
selection fitnutá mimo fold/train boundary
identity memorization bez cold-start acceptance
offline-only/current-state aggregates
column score bez serving dependency/cost
```

## 20. Evidence-preserving containment a recovery

Tím zachoval candidate inventory, selector fitted state, rankings, source queries, feature vectors a online availability logs. Promotion bol zastavený a serving sa vrátil k approved feature schema v4.

Recovery zaviedla feature manifest s source/time/freshness/owner fields, point-in-time materialization, pipeline-contained selection a outer untouched evaluation. Candidate features sa rozdelili do groups podľa serving dependencies. Každý selected feature prešiel availability a parity gate.

```text
business hypothesis
→ feature contract + point-in-time implementation
→ train-only selector
→ fold stability
→ cost/latency/availability review
→ locked schema
→ shadow parity
```

Cold-start a known-merchant cohorts dostali samostatné metrics. Identifier-derived features boli odstránené alebo nahradené support-aware history features.

## 21. Acceptance contract

Positive path musí preukázať prediction-time availability, exact feature definitions, train-only selection, locked output schema a online/offline parity. Selected set musí mať documented metric gain, stability alebo business rationale a accepted serving cost.

Recovery path musí umožniť vypnúť feature/group, použiť compatible fallback alebo rollback schema/model generation bez silent zero fill. Source outage musí byť visible a bounded.

Forbidden paths:

```text
future/post-outcome information vstúpi do feature
selector vidí validation/test labels mimo allowed loopu
raw ID memorization sa vydáva za generalization
unknown/stale feature sa ticho zmení na ordinary zero
selected column vyžaduje unowned/unavailable online dependency
feature semantics sa zmení bez version bumpu
importance/selection sa vydáva za causal alebo fairness proof
```

Second-feature test pridá new category/entity/time window a overí correct feature computation, selection schema, cold-start fallback a no unsafe action. Second-build test nad pinned inputs potvrdí selected feature inventory/digest alebo vysvetlenú stochastic variability.

## Kontrolné otázky

1. Čo musí obsahovať exact feature contract?
2. Ako sa feature engineering líši od preprocessing?
3. Prečo window boundary a late-event policy menia feature meaning?
4. Aký problem majú ratios s malým denominatorom?
5. Kedy interactions pomáhajú a aký cost pridávajú?
6. Prečo timezone patrí do cyclical time feature contractu?
7. Ako ID features vedú k memorization a cold-start failure?
8. Prečo odstránenie protected attribute nezaručí fairness?
9. Čím sa feature extraction líši od selection?
10. Ako filter method leakne test labels?
11. Čo wrapper method optimalizuje a prečo môže overfitnúť validation?
12. Ako embedded selection závisí od modelu a correlated features?
13. Prečo sa má selection niekedy robiť po feature groups?
14. Ako freshness a historical availability vytvárajú skew?
15. Čo ukazuje feature selection stability?
16. Čo preukazuje registry a čo nie?
17. Prečo top features v `ML-PAY-84` zmizli po oprave boundaries?
18. Aké positive, recovery, forbidden a second-feature testy uzatvárajú feature lifecycle?

## Glossary impact

Relevantné pojmy: feature engineering, feature definition, point-in-time feature, window aggregate, ratio smoothing, interaction, polynomial features, cyclical encoding, identity memorization, high cardinality, proxy feature, feature extraction, filter/wrapper/embedded selection, feature group, feature freshness, selection stability, feature registry, feature lineage, cold-start cohort a feature acceptance contract.

## Primárne zdroje

- [scikit-learn — Feature extraction](https://scikit-learn.org/stable/modules/feature_extraction.html)
- [scikit-learn — Feature selection](https://scikit-learn.org/stable/modules/feature_selection.html)
- [scikit-learn — `SelectKBest`](https://scikit-learn.org/stable/modules/generated/sklearn.feature_selection.SelectKBest.html)
- [scikit-learn — `RFECV`](https://scikit-learn.org/stable/modules/generated/sklearn.feature_selection.RFECV.html)
- [scikit-learn — `SelectFromModel`](https://scikit-learn.org/stable/modules/generated/sklearn.feature_selection.SelectFromModel.html)
- [scikit-learn — `PolynomialFeatures`](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.PolynomialFeatures.html)
- [TensorFlow Data Validation](https://www.tensorflow.org/tfx/guide/tfdv)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Data preprocessing, normalization a encoding](data-preprocessing-normalization-encoding.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Data leakage a train-serving skew →](data-leakage-train-serving-skew.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
