# Explainability a feature importance

Explainability je súbor otázok, artifacts a metód, nie jedna univerzálna hodnota. Globálna feature importance opisuje, na ktorých vstupoch sa konkrétny fitted model spolieha pre konkrétnu population a metric. Local attribution rozkladá jednu prediction podľa zvolenej explainer procedure a background/reference distribution. Partial dependence ukazuje average model response pri syntetickej zmene feature, nie kauzálny efekt reálnej intervencie. Coefficient alebo tree split count môže byť technicky reprodukovateľný a pritom zavádzajúci pre stakeholdera, ktorý ho číta ako dôvod, spravodlivosť alebo business pravidlo.

Incident `ML-PAY-88` pokračoval pri Atlas Payments decision platforme. Dashboard označil `merchant_country` za „najdôležitejšiu príčinu fraudu“, pretože tree impurity importance bola vysoká. Feature mala vysokú cardinality a zároveň zastupovala niekoľko correlated operational signals. Permutation importance na random row-level validation ostala vysoká, no po group/time-safe evaluation klesla. SHAP-like local report použil background sample z trainingu s odlišnou prevalence a vysvetlenie jedného blocked paymentu sa interpretovalo ako kauzálne odôvodnenie. PDP pre transaction amount vytváral combinations, ktoré v reálnych merchant cohorts neexistovali. Kapitola preto oddeľuje model reliance, attribution, response surface, causal claim a governance explanation.

## 1. Dominantný explainability lifecycle

Explainability začína otázkou a audience. Debugging modelu, regulatory notice, feature validation a analyst investigation potrebujú odlišný artifact. Exact model, preprocessing a population sa uzamknú, potom sa vyberie method s explicitným reference/background datasetom a scoring function. Výsledok sa validuje stability, fidelity, cohort a human-interpretation testami pred použitím v rozhodnutí.

```text
explanation question a audience
→ exact model/preprocessing/policy subject
→ exact population, background/reference a metric
→ global inspection alebo local attribution method
→ generated explanation artifact
→ fidelity, stability, plausibility a cohort checks
→ comparison with competing explanations
→ debugging, notice, review alebo governance action
→ drift, recovery a second-operation acceptance
```

Tento chain zabraňuje tomu, aby sa jeden global bar chart recykloval ako local reason code alebo causal evidence. Explanation artifact je dependent output konkrétneho modelu a datasetu; po zmene jedného z nich môže byť stale aj pri rovnakom názve feature.

## 2. Exact explanation subject

Reprodukovateľný explanation report identifikuje model digest, preprocessing feature space, explainer method, dataset, metric, background a output semantics.

```yaml
explanation_subject: ML-PAY-XAI-2026-08-v4
model:
  run_id: ML-PAY-HPO-2026-08-v8
  digest: sha256:1f92...b0c4
  preprocessing_digest: sha256:6b19...445e
  output: calibrated_probability_recoverable_loss
population:
  evaluation_manifest: eu-cnp-mature-2026w28-w30-v4
  observation_unit: payment_operation_id
method:
  family: permutation_importance
  scoring: average_precision
  repeats: 30
  random_state: 31
  max_samples: 0.8
reference:
  background_manifest: eu-cnp-reference-2026w25-w27-v2
  feature_grouping: semantic-feature-groups-v3
slices:
  - campaign_traffic
  - new_merchant
  - country
```

Model output musí byť explicitný. Explanation raw logit, calibrated probability a final policy decision môže mať odlišné attributions. Ak downstream policy pridáva threshold, queue boost alebo rule override, model explanation sama nevysvetľuje final action.

## 3. Explanation question a audience

Najprv sa určí, čo má explanation zodpovedať:

- model debugging — ktoré inputs a interactions riadia chyby alebo unexpected behavior;
- global model understanding — ako sa fitted function správa na relevantnej population;
- local prediction analysis — ktoré feature values prispeli k jednému model outputu podľa zvolenej attribution procedure;
- data-quality audit — či model používa proxy, leakage alebo unstable feature;
- human-review support — aké evidence má reviewer preskúmať, bez predstierania kauzality;
- external notice — dôvody formulované podľa policy/legal contractu, ktoré nemusia byť totožné s raw feature attributions.

Technicky presný attribution vector môže byť nevhodný pre end usera, ak používa transformed feature names, hash buckets alebo embeddings. Preklad do semantic reason codes je ďalšia versionovaná policy a potrebuje fidelity test.

## 4. Intrinsic a post-hoc explainability

Intrinsic interpretable model má structure, ktorú možno priamo analyzovať, napríklad sparse linear model alebo malý decision tree. Post-hoc method vysvetľuje už fitted model bez zmeny jeho prediction function.

```text
intrinsic:
model structure → coefficients/rules → prediction

post-hoc:
fitted model + reference data + explainer assumptions → explanation artifact
```

„Interpretable model“ nie je binary property. Linear model s tisíckami correlated encoded features nie je prakticky jednoduchý. Malý tree môže byť ľahko čitateľný, ale preprocessing a ensemble policy ho môžu skomplikovať. Post-hoc explanation neprenáša automaticky fidelity; approximation error sa musí merať.

## 5. Linear coefficients

Pri linear modeloch coefficient vyjadruje zmenu model outputu pri jednotkovej zmene feature, keď ostatné vstupy zostávajú fixné v model equation. Interpretation závisí od scaling, encoding, interactions, regularization a output link function.

```python
coefficient_table = {
    name: value
    for name, value in zip(feature_names, model.coef_.ravel())
}
```

Logistic-regression coefficient pôsobí na log-odds, nie priamo na probability. Standardized a raw features majú odlišnú unit scale. One-hot category coefficient sa interpretuje voči omitted/reference category. Pri correlated features môže fit rozdeliť alebo presúvať weight medzi substitute predictors; coefficient magnitude preto nie je stabilná universal importance.

Regularization zámerne shrinkuje alebo selektuje coefficients. Zmena coefficientu medzi runs môže vzniknúť collinearity alebo sampling variability aj pri podobných predictions. Report preto obsahuje bootstrap/fold stability a semantic groups.

## 6. Tree impurity-based feature importance

Tree ensembles často poskytujú `feature_importances_` založenú na cumulative impurity decrease priradenej splitom. Je lacná a intrinsic pre fitted trees, ale môže favorizovať high-cardinality alebo continuous features s viacerými možnosťami splitu.

```python
importance = dict(
    zip(feature_names, forest.feature_importances_)
)
```

Tento score nehovorí, či feature generalizuje na unseen data. Training leakage alebo noisy high-cardinality feature môže dostať vysokú impurity importance. Correlated substitutes si môžu rozdeliť importance neintuitívne. Hodnota je relative v rámci modelu a normalization, nie percent causal contribution.

V Atlas incidente `merchant_country` niesla vysokú importance, pretože encoder a tree splits využívali mnoho category boundaries. To nepreukázalo, že country „spôsobuje fraud“ ani že odstránenie feature automaticky zlepší fairness.

## 7. Permutation feature importance

Permutation importance zmeria pokles zvoleného score po náhodnom preusporiadaní jednej feature v konkrétnom datasete. Rozbije väzbu feature s targetom a ostatnými rows, pričom model zostáva fixed.

```python
from sklearn.inspection import permutation_importance

result = permutation_importance(
    fitted_pipeline,
    X_eval,
    y_eval,
    scoring="average_precision",
    n_repeats=30,
    random_state=31,
    n_jobs=4,
    max_samples=0.8,
)
```

Method je model-agnostic a môže sa počítať na holdout-e, čo oddeľuje model reliance od training overfit. Najprv však musí byť model predictive; low importance pre zlý model nie je dôkaz, že features sú zbytočné. Importance závisí od metricu: feature môže byť dôležitá pre recall, ale menej pre log loss.

`n_repeats` vytvára distribution permutation drops, nie independent population experiments. `random_state` riadi permutations. `max_samples` mení compute a variance. Sample weights a cohort filtering menia estimand a patria do subjectu.

## 8. Correlated features a grouped permutation

Ak dve features obsahujú podobnú informáciu, permutácia jednej môže spôsobiť malý score drop, pretože model využije druhú. Obe sa potom javia málo dôležité napriek spoločnej predictive value.

```text
feature A ≈ proxy feature B
permute A → model still uses B
permute B → model still uses A
individual importance appears low
```

Group permutation premieša semantic group spoločne a zmeria shared reliance. Group definition je policy: napríklad all merchant-history features alebo all device-risk variants. Príliš široká group skombinuje viac mechanisms a príliš úzka skryje substitution.

Permutation môže vytvoriť unrealistic feature combinations, najmä pri correlated, temporal alebo constrained features. Conditional permutation methods sa snažia rešpektovať dependency, ale prinášajú ďalší model a assumptions. Report musí uviesť, či importance znamená marginal alebo conditional intervention v explainer procedure.

## 9. Drop-column a retraining importance

Drop-column analysis odstráni feature alebo group, refituje celý pipeline a porovná performance. Odpovedá na inú otázku než permutation: ako dobre sa model-building procedure adaptuje bez feature.

```text
baseline full pipeline fit
vs.
successor pipeline without feature group
→ same split, budget and selection procedure
→ paired evaluation
```

Je výpočtovo drahšia a môže zmeniť hyperparameter optimum, feature selection a regularization. Jednoduchý refit s pôvodnými hyperparameters môže podhodnotiť substitute information. Full HPO per feature je drahé a spotrebúva selection evidence. Drop-column result preto nesmie byť zamieňaný s local explanation.

## 10. Partial dependence

Partial dependence pre feature hodnotí average model response, keď sa feature nastaví na grid values a ostatné features sa čerpajú z reference datasetu. Ide o model response surface, nie observed causal effect.

```python
from sklearn.inspection import PartialDependenceDisplay

PartialDependenceDisplay.from_estimator(
    fitted_pipeline,
    X_reference,
    features=["transaction_amount"],
    kind="average",
    grid_resolution=50,
)
```

PDP pri correlated features môže vytvoriť synthetic combinations mimo data manifold, napríklad vysokú transaction amount pre merchant segment, kde taká hodnota nikdy nevzniká. Average môže prekryť heterogénne subgroups. Percentile range a grid resolution menia zobrazený region.

Current scikit-learn podporuje brute a recursion computation s estimator-specific hranicami. `sample_weight` alebo ICE behavior môže vynútiť brute method. Exact method sa loguje, pretože niektoré boosting initialization semantics môžu ovplyvniť recursion output.

## 11. Individual conditional expectation

ICE zobrazuje model response pre každý sample samostatne pri zmene feature. Odhaľuje heterogeneity a interactions, ktoré average PDP skryje.

```python
PartialDependenceDisplay.from_estimator(
    fitted_pipeline,
    X_reference_sample,
    features=["transaction_amount"],
    kind="both",
    method="brute",
)
```

Veľký dataset vytvorí nečitateľný chart; sampling musí byť deterministic a cohort-aware. Centered ICE zvýrazňuje shape rozdiely, ale odstráni absolute level. Rovnako ako PDP, ICE môže hodnotiť unrealistic points. Heterogeneous lines sú hypothesis pre interaction alebo segmentation, nie automatický causal discovery.

## 12. Local surrogate explanations

Local surrogate fituje jednoduchý interpretable model okolo jednej observation na synteticky perturbovaných samples. Explanation fidelity závisí od neighborhood kernelu, perturbation distribution, interpretable representation a model outputu.

```text
selected observation
→ generate local perturbations
→ query black-box model
→ weight by locality
→ fit sparse surrogate
→ report local coefficients + fidelity
```

Ak perturbations porušujú feature constraints, surrogate vysvetľuje model v nereálnom okolí. Small kernel môže byť nestabilný; large kernel prestane byť local. Random seed a number of samples menia result. Report bez local fidelity score a repeated stability nie je authoritative.

Local surrogate coefficient nie je parameter original modelu a nemá sa prezentovať ako internal logic bez qualifiera.

## 13. Additive attributions a SHAP-like semantics

Additive feature attribution rozkladá difference medzi model outputom pre observation a expected/background outputom na feature contributions podľa zvolenej game-theoretic alebo approximation procedure.

```text
model_output(x) = baseline(background) + sum(feature_attribution_i)
```

Baseline závisí od background distribution. Training population, recent production cohort alebo policy-eligible subset vytvoria odlišné attributions pre rovnakú observation. Raw-logit a probability explanations sa líšia. Correlated features vyžadujú rozhodnutie, či sa dependency ignoruje, modeluje alebo sa používa interventional assumption.

Tree-specific exact/optimized algorithms, kernel approximations a deep explainers majú odlišné supported models a assumptions. Názov „SHAP value“ bez explainer type, model output a background manifest nie je reprodukovateľný subject.

Additivity môže overiť algebraic consistency vo zvolenom output space, ale nepreukazuje causal meaning, fairness ani human comprehensibility.

## 14. Global summary z local attributions

Mean absolute local attribution cez population sa často používa ako global importance. Absolútna hodnota odstráni direction a priemer môže zvýrazniť feature s veľkými contributions iba v malom cohort-e.

```python
mean_abs = abs(attributions).mean(axis=0)
```

Report potrebuje distribution, sign, cohort a interaction context. Feature s nízkym global mean môže byť decisive pre protected alebo operationally critical subgroup. Aggregate ranking sa nesmie používať na feature deletion bez performance a policy evaluation.

## 15. Feature interactions

Interaction znamená, že effect jednej feature v model function závisí od druhej. Two-dimensional PDP, ICE heterogeneity alebo attribution interaction values môžu vytvoriť hypothesis.

```text
amount effect for known merchant
≠ amount effect for new merchant
```

Interaction chart môže byť spôsobený sparse support alebo correlated features. Before interpretation sa kontroluje joint density/reference support. High-order interactions sa ťažko vizualizujú a explanation complexity môže prekročiť audience capacity.

Model interaction nie je automatically real-world mechanism. Môže odrážať leakage, sampling alebo proxy.

## 16. Local reason codes a final decision

Production action často kombinuje model output, calibration, threshold, queue prioritization a business rules. Model attribution vysvetľuje iba jednu vrstvu.

```text
raw model score
→ calibrated probability
→ policy threshold
→ merchant boost
→ capacity truncation
→ final action
```

Reason code pre final action musí identifikovať, či decision vznikla modelom, hard rule, missing data fallback alebo capacity policy. Ak blocked payment bolo odmietnuté hard sanction rule, generovať top model features ako dôvod je nesprávne.

Mapping hundreds transformed features do niekoľkých human reason codes môže spájať positive a negative contributions. Resolver potrebuje deterministic aggregation, sign handling, minimum materiality a conflict rules.

## 17. Explanation stability

Explanation môže byť nestabilná pri malých zmenách inputu, seed-u, backgroundu alebo model retrainingu aj keď prediction ostáva podobná. Stability je samostatný quality dimension.

```yaml
stability_tests:
  repeated_permutation_seeds: 20
  background_resamples: 10
  neighboring_input_perturbations: enabled
  retrain_seeds: [11, 23, 37, 53, 71]
  cohort_rank_correlation_min: 0.75
```

Úplná stability nie je vždy žiaduca; skutočná model change má explanation zmeniť. Cieľom je odlíšiť expected sensitivity od arbitrary explainer variance. Acceptance definuje toleranciu podľa use case-u.

## 18. Fidelity, plausibility a usefulness

Fidelity znamená, či explanation verne reprezentuje model behavior v deklarovanom scope. Plausibility znamená, či dáva ľuďom zmysel; plausible explanation môže byť faithful alebo úplne falošná. Usefulness znamená, či podporuje správnu action.

```text
faithful but incomprehensible
comprehensible but unfaithful
stable but causally wrong
useful for debugging but unsuitable for notice
```

Evaluation potrebuje technical tests aj user/workflow tests. Human preference pre jednoduché explanation nie je dôkaz fidelity. Reviewer success rate môže byť ovplyvnený automation bias a potrebuje controlled comparison.

## 19. Explainability, leakage a proxies

High importance pre suspicious feature je signal na investigation, nie verdict. Feature môže byť direct leakage, legitimate predictor, proxy protected attribute alebo proxy operational process.

```text
importance signal
→ trace feature lineage and availability time
→ inspect correlation and cohort behavior
→ ablation/permutation/group tests
→ legal/domain review
→ retrain or constrain if necessary
```

Odstránenie jednej proxy nemusí odstrániť encoded information z correlated features. Fairness sa nepreukazuje nízkou importance protected attribute. Model môže vykazovať disparate outcomes cez other variables a interactions.

## 20. Worked incident `ML-PAY-88`

Atlas dashboard čítal impurity-based importance ako „causal fraud drivers“. `merchant_country` mala mnoho encoded categories a silnú association s traffic source. Random row split zdieľal merchants naprieč train/eval, takže permutation importance bola vysoká. Pri unseen-merchant temporal holdout-e importance klesla a feature group sa ukázala ako proxy campaign routing.

Local explanation pre blocked operation použila background z oversampled training population. Baseline probability bola preto vyššia než natural production base rate a contribution signs sa líšili od reportu s production backgroundom. PDP pre amount kombinoval values s merchant types mimo observed support.

```text
biased global importance
+ mismatched local background
+ off-manifold PDP
→ explanation presented as causal reason
→ analyst and customer receive inconsistent story
```

Root cause bol explanation-subject failure: method, metric, background, output space, split a final policy layer neboli identifikované.

## 21. Competing failure hypotheses

Explainability incident sa diagnostikuje cez exact artifact a question. Najprv sa určí, či problém je v model reliance, explainer assumptions, reference data, transformation mapping alebo interpretation/presentation.

- wrong output explained — attribution sa počíta pre raw score, ale prezentuje ako calibrated probability alebo final action;
- reference/background mismatch — baseline population nereprezentuje intended cohort a posúva local contributions;
- high-cardinality bias — impurity importance favorizuje feature s mnohými split points;
- correlated-substitute masking — permutation jednej feature ukáže nízku importance, pretože substitute ostáva;
- off-manifold perturbation — permutation, PDP alebo local surrogate vytvára invalid feature combinations;
- low model quality — explanation detailne opisuje model, ktorý nemá acceptable predictive power;
- explainer approximation failure — local surrogate alebo sampled attribution má nízku fidelity;
- instability — ranking alebo local reasons sa menia pri seed/background perturbation bez material prediction change;
- preprocessing mapping bug — transformed columns sa nesprávne mapujú späť na semantic features;
- aggregation masking — global mean abs attribution prekryje sign, subgroup alebo interaction;
- policy-layer omission — final decision vznikla rule/queue override, ale report ukazuje iba model features;
- causal overclaim — association/model response sa prezentuje ako effect reálnej intervencie.

Ak raw model a predictions sú identické, ale local explanation sa zmení po background swap-e, ide o explainer subject, nie model drift. Ak importance zmizne na group/time-safe holdout-e, split leakage alebo population dependency je silnejšia hypothesis než random explainer failure.

## 22. Evidence-preserving containment a recovery

Containment zastaví publikovanie problematického explanation artifactu, nie nevyhnutne celý model, pokiaľ prediction risk nie je dotknutý. Zachová model/preprocessing digest, input row, output, explainer config, background/reference manifests, seeds a rendered reason codes.

```text
freeze explanation publication
→ preserve model, input and explainer artifacts
→ reproduce output and attribution
→ verify semantic feature mapping
→ test reference, metric, correlation and off-manifold hypotheses
→ compare alternate methods and ablations
→ correct explainer/reason policy or retrain model
→ independent-cohort and human-workflow acceptance
```

Ak explanation bola nefaithful, historical notices/reports sa označia invalid podľa governance policy. Ak high importance odhalí leakage, dependent model artifact musí byť retrained. Ak problém je iba visualization label, recovery stále vytvorí successor report generation a audit trail.

## 23. Acceptance contract

Positive acceptance identifikuje question, audience, exact model/output, preprocessing, population, reference/background, method, metric, random state a presentation mapping. Global methods sa validujú na acceptable model performance; local methods majú fidelity/additivity a stability evidence. Correlated/off-manifold risks a policy overrides sú explicitné.

Recovery acceptance reprodukuje corrected explanation a ukazuje, že semantic reason codes zodpovedajú final decision path. Forbidden paths zahŕňajú impurity importance ako causal claim, feature importance z training setu bez generalization contextu, PDP pri correlated features bez support analýzy, local attribution bez background manifestu, explanation raw score ako explanation final action, fairness claim z low protected-feature importance a odstranenie feature iba podľa jedného importance ranku.

Second-operation test vytvorí rovnaký explanation artifact z immutable model/input/reference manifests a musí zachovať output, baseline, contribution aggregation a reason-code mapping v tolerancii. Second-cohort test overí global ranking, local stability a usefulness na novom time/group cohort-e.

```yaml
acceptance:
  question_and_audience_defined: passed
  model_output_and_reference_exact: passed
  fidelity_and_stability: passed
  correlated_and_off_manifold_analysis: passed
  final_policy_reason_mapping: passed
  no_causal_overclaim: passed
  second_cohort: passed
```

## Kontrolné otázky

1. Prečo explainability nie je jedna univerzálna metrika?
2. Aký je rozdiel medzi global importance a local attribution?
3. Ako scaling a link function menia interpretation linear coefficientu?
4. Prečo impurity importance favorizuje high-cardinality features?
5. Čo permutation importance meria a od akého metricu závisí?
6. Ako correlated substitute features skresľujú permutation importance?
7. Aký je rozdiel medzi permutation a drop-column analysis?
8. Prečo PDP a ICE nie sú kauzálne efekty?
9. Ako local surrogate fidelity závisí od perturbation neighborhoodu?
10. Prečo SHAP-like attribution potrebuje background manifest a output space?
11. Ako global mean absolute attribution môže prekryť cohort alebo sign?
12. Prečo model explanation nemusí vysvetliť final policy action?
13. Aký je rozdiel medzi fidelity, plausibility a usefulness?
14. Prečo low importance protected attribute nepreukazuje fairness?
15. Čo pokazilo explanation lifecycle v `ML-PAY-88`?
16. Aké positive, recovery, forbidden a second-cohort testy uzatvárajú explainability contract?

## Glossary impact

Relevantné pojmy: explainability, interpretability, explanation subject, intrinsic model, post-hoc explanation, global feature importance, local attribution, coefficient interpretation, impurity-based importance, permutation importance, grouped permutation, drop-column importance, partial dependence plot, individual conditional expectation, local surrogate, additive feature attribution, background distribution, baseline output, feature interaction, reason code, explanation fidelity, stability, plausibility, usefulness, proxy feature, off-manifold perturbation a explainability acceptance contract.

## Primárne zdroje

- [scikit-learn — Inspection](https://scikit-learn.org/stable/api/sklearn.inspection.html)
- [scikit-learn — Permutation feature importance](https://scikit-learn.org/stable/modules/permutation_importance.html)
- [scikit-learn — `permutation_importance`](https://scikit-learn.org/stable/modules/generated/sklearn.inspection.permutation_importance.html)
- [scikit-learn — Partial dependence](https://scikit-learn.org/stable/modules/generated/sklearn.inspection.partial_dependence.html)
- [scikit-learn — `PartialDependenceDisplay`](https://scikit-learn.org/stable/modules/generated/sklearn.inspection.PartialDependenceDisplay.html)
- [SHAP documentation](https://shap.readthedocs.io/en/latest/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Calibration a uncertainty](calibration-uncertainty.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Data quality, bias a responsible AI →](data-quality-bias-responsible-ai.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
