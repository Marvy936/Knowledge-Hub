# Data leakage a train-serving skew

Data leakage nastáva, keď training alebo evaluation pipeline používa information, ktorá by pre intended prediction nebola legitímne dostupná, alebo keď evidence domains nie sú nezávislé. Train-serving skew nastáva, keď model v produkcii dostáva inú feature semantics, distribution alebo transformation path než počas trainingu. Obe chyby môžu vytvoriť vysoké offline score a zároveň zlý production outcome, pretože model sa naučil alebo očakáva information, ktorú reálny system nemá.

Leakage a skew nie sú synonymá. Leakage je porušenie information/evidence boundary pri trainingu alebo evaluation. Skew je rozdiel medzi training a serving pathom. Jedna feature môže byť leakage-free offline a predsa skewed online kvôli inému parseru, stale value alebo missing fallbacku. Naopak, training a serving môžu používať identickú future-derived feature; parity je technicky dobrá, ale model je stále invalidný pre prediction time.

Incident `ML-PAY-84` spojil oba mechanisms. Random split zdieľal merchant a retry information, transforms a selector videli test data, current-state aggregates používali future outcomes a online Java service vytváral iné vectors než offline Python pipeline. Dashboard ukazoval vysoký test score a zelený inference endpoint, ale žiadny z týchto verdictov nepreukazoval legitimitu ani parity model inputu.

## 1. Dominantný leakage/skew lifecycle

Diagnosis musí sledovať information od source eventu cez availability time, split, feature fit, artifact a online computation až po model input. Prvý chýbajúci alebo forbidden transition určuje mechanismus.

```text
real-world event a source authority
→ event/ingest/available time
→ dataset snapshot a sample/group identity
→ split membership
→ preprocessing/feature/selection fit domain
→ training vector a model artifact
→ serving raw request
→ online feature vector
→ loaded model input
→ prediction/action/outcome
```

Leakage questions sa pýtajú: „Kedy a komu bola táto information dostupná?“ Skew questions sa pýtajú: „Je training a serving representation pre rovnaký subject ekvivalentná?“ Obe vyžadujú exact IDs, timestamps, feature versions a artifacts.

## 2. Exact leakage a skew subject

Leakage a skew diagnosis potrebuje spojiť dva rozdielne comparison contracts. Prvý porovnáva feature availability a fit domain s intended prediction time a evidence splitom; druhý porovnáva offline a online representation toho istého sample-u. Bez exact modelu, splitu, preprocessing state-u a matched operation identity môže rovnaký symptom viesť k nesprávnej oprave — retrainingu pri implementation skew alebo serving rollbacku pri contaminated trainingu.

Incident manifest preto fixuje artifact generations aj jednu porovnateľnú operation. Preprocessing digest conflict signalizuje rozdielnu loaded transformáciu, zatiaľ čo split a prediction-time fields umožnia samostatne overiť, či training information bola vôbec legitímna. Jeden manifest tak nezamieňa parity verdict s leakage verdictom.

```yaml
incident_subject: ML-PAY-84
model_digest: sha256:91fe...0a22
split_manifest: SPLIT-ML-PAY-84-v1
prediction_subject: merchant_operation_id
prediction_time: authorization_received_at
training_feature_schema: model-input-v6
serving_feature_schema: model-input-v6
preprocessing_digest:
  training: sha256:5c82...1d9a
  serving: sha256:77b1...fa03
sample:
  operation_id: op-92117
  request_id: req-27a1
  offline_vector_hash: sha256:11c3...
  online_vector_hash: sha256:99af...
suspected_boundaries:
  - group overlap
  - post-outcome aggregate
  - selector fit domain
  - amount unit conversion
```

Rovnaký schema name s odlišným preprocessing digestom je conflict. Rovnaký vector hash nepreukazuje absence leakage; iba parity pre daný sample. Incident subject musí pokryť oba axes.

## 3. Target leakage

Target leakage vzniká, keď feature priamo alebo nepriamo obsahuje label alebo information vzniknutú po outcome. Príklady zahŕňajú `final_settlement_status`, post-review reason, refund created after fraud confirmation alebo aggregate počítaný z future labels.

```text
prediction time t0
→ feature available at t0 + 2d
→ target observed at t0 + 30d

feature cannot be used at t0
```

Column nemusí mať očividný názov. „Case status“, „investigation duration“ alebo „number of support contacts“ môžu vzniknúť až po decisione. Feature importance často leakage feature zvýrazní, ale high importance nie je dôkaz leakage; treba lineage a availability time.

Odstrániť direct label column nestačí, ak proxy alebo aggregate ho stále rekonštruuje.

## 4. Temporal leakage

Temporal leakage používa future data pri historical prediction. Vzniká current-state joinom, centered rolling windowom, random splitom time series, global normalization cez future periods alebo backfillom, ktorý rekonštruuje ideal history dostupnú až neskôr.

```text
historical row at Jan 10
joined merchant table as of Aug 2
→ future merchant state leaks into past prediction
```

Point-in-time correct join vyberá state known v prediction cutoff-e. Pri late-arriving events treba odlíšiť event time od actual availability. Model training na perfect event-time history môže byť optimistický, ak production vidí delayed data.

Time split je potrebný, ale nie sufficient. Future-derived feature môže byť prítomná v každom historical row.

## 5. Entity a group leakage

Related samples naprieč train/test umožnia modelu memorization alebo shared context. Retry attempts, multiple images jedného patienta, documents z jednej source, sessions jedného usera alebo operations jedného merchant-a môžu byť dependent.

```text
train: op-741 attempt 1, merchant M
 test: op-741 attempt 2, merchant M
```

Group leakage nemusí byť chyba, ak deployment predikuje nové events known entities a shared history je legitímna. Evaluation však musí mať explicitný scenario. Často sú potrebné known-entity future a unseen-entity cold-start tests.

Near duplicates alebo transformed copies môžu prejsť aj pri rozdielnom ID. Deduplication a similarity analysis patria pred split.

## 6. Preprocessing leakage

Fitted transform leakne, ak `.fit()` vidí validation/test population. Scaler means, imputer medians, encoder vocabulary, PCA components a outlier thresholds môžu preniesť distribution information. Target-aware transforms môžu preniesť labels ešte priamočiarejšie.

```python
# forbidden
X_all = scaler.fit_transform(X_all)
X_train, X_test = split(X_all)

# correct boundary
X_train, X_test = split(X_raw)
scaler.fit(X_train)
X_test = scaler.transform(X_test)
```

Leakage impact môže byť malý alebo veľký, ale contract je rovnaký. Pipeline v cross-validation zabezpečí fold-local fit, ak custom steps nepoužívajú external global state.

## 7. Feature-selection leakage

Feature selection používa labels alebo distribution na výber columns. Ak sa vykoná pred splitom alebo mimo fold pipeline, test information ovplyvní feature set. Aj keď final estimator nevidí test labels, design už áno.

```text
all-data labels
→ rank features
→ choose top 50
→ split
→ optimistic evaluation
```

Selector musí byť fitted v train/inner-validation domain. Pri wrapper selection a hyperparameter search treba nested alebo untouched final evidence. Repeated feature ideas podľa test errors sú human-mediated leakage.

## 8. Hyperparameter a test leakage

Každé rozhodnutie podľa test score prenáša test information do final model. Po stovkách experiments môže leaderboard overfitting nastať aj bez row access. Test sa stáva validation setom.

```text
model A test 0.80
model B test 0.81
feature C test 0.815
threshold D test 0.817
→ test drove selection
```

Riešením je oddeliť validation/search dashboard, obmedziť test access a vytvoriť nový untouched cohort pri contamination. Experiment ledger má evidovať datasets used for decision.

## 9. Leakage cez labels a delayed outcomes

Recent samples bez mature outcome môžu byť ticho označené negative. To je information error, ktorý mení target distribution. Naopak, selection iba fully resolved cases môže vytvoriť survivorship alebo censoring bias.

```text
no positive event yet
≠
authoritative negative
```

Label generation potrebuje horizon, maturity, reconciliation delay a unknown state. Ak intervention ovplyvní observed label, feedback loop môže vytvoriť selective labels. Reviewed cases majú richer truth než ignored cases.

## 10. Leakage cez cross-sample aggregates

Aggregate môže používať target alebo events iných samples z future/test domain. Group mean target, global frequency, graph features alebo neighbor labels musia byť vypočítané bez forbidden information.

Target encoding potrebuje out-of-fold/time-safe procedure. Graph split je komplexný: edges medzi train/test nodes môžu prenášať information. Exact deployment semantics určujú, ktoré neighbors sú dostupné.

```text
feature for sample i
must not use y_i
and must not use future/forbidden y_j
```

Stateless-looking lookup table môže byť fitted aggregate s hidden label lineage.

## 11. Train-serving schema skew

Schema skew znamená rozdiel v feature presence, type, shape, vocabulary alebo required/optional contract medzi training a serving. Labels sú legitímne iba v training environment; iné differences musia byť explicitné.

```text
training: amount_minor int64 required
serving:  amount string optional
```

Parser môže castnúť value alebo failnúť. Tiché fallbacky sú risk. TensorFlow Data Validation používa schema environments na vyjadrenie legitimate differences, napríklad label absent v serving, a identifikuje anomalies.

Schema name/version musí byť overený loaded runtimeom. API compatibility nie je iba syntactic JSON schema; semantic unit a time meaning tiež.

## 12. Feature skew

Feature skew znamená, že matched training a serving examples majú rozdielne feature values. Môže vzniknúť inou transformation implementation, rounding, window boundaries, late events, bugom alebo mutable source.

```text
same operation ID
training feature: 0.42
serving feature: 173.10
```

TFDV dokáže porovnávať matched examples podľa identifier features a detegovať feature skew. Practical implementation potrebuje sample matching, privacy-safe capture a tolerance pre floating point alebo accepted lag.

Feature skew diagnostic musí rozlíšiť expected recomputation difference od bug-u. Training record môže byť generated po neskorom backfill-e; serving value bola actual at decision time.

## 13. Distribution skew

Distribution skew znamená rozdiel aggregate distributions medzi training a serving data. Nemusí znamenať per-example mismatch. Population, seasonality alebo business policy sa mohli legitímne zmeniť.

```text
training country distribution
vs
serving country distribution
```

Distribution comparison pomáha zachytiť shift, ale neidentifikuje automaticky root cause ani performance impact. Feature môže driftovať bez model degradation alebo stabilná marginal distribution môže skryť changed correlations.

Training-serving distribution skew sa odlišuje od temporal drift medzi consecutive serving periods, hoci tools môžu používať podobné distance metrics.

## 14. Transformation skew

Transformation skew vzniká, keď training a serving implementujú „rovnakú“ logic odlišne. Python používa inclusive boundary, SQL exclusive; one service uppercases country code, druhý nie; Java integer division sa líši od float calculation; timezone/rounding sa rozchádza.

```text
training function f_train(raw)
serving function  f_serve(raw)
expected: equivalent under contract
```

Najsilnejšia prevention je shared/exported transform artifact. Ak cross-language implementácia musí existovať, canonical specification a generated/golden conformance tests pokrývajú edge cases.

Code review similarity nie je runtime parity evidence.

## 15. Feature availability a freshness skew

Offline data warehouse môže mať complete backfilled features, online store stale alebo missing. Training model sa učí z ideal values, serving dostáva delayed values. Aj rovnaká transformation logic vytvorí rozdiel.

```text
event occurs t0
warehouse backfill t0+1d
online feature available t0+10m
prediction t0+1m
```

Training example pre production realism má používať value available at `t0+1m`, nie final backfill. Availability timestamp a freshness age môžu byť explicitné features alebo acceptance constraints.

Fallback policy pre stale values musí byť trained/evaluated. Model validovaný iba na complete data nemusí bezpečne zvládnuť online missingness.

## 16. Label skew nie je serving skew

Serving request prirodzene nemá future label. Absence labelu nie je schema bug, ak environments to vyjadrujú. Problem je, keď serving omylom posiela label-like post-outcome field alebo training pipeline očakáva input, ktorý existuje iba po outcome.

```text
training-only:
y = confirmed_loss_within_30d

serving input:
features available at authorization time
```

Clear separation target/feature schemas zabraňuje tomu, aby export modelu vyžadoval label column alebo aby broad `SELECT *` ticho pridal target medzi features.

## 17. Training-serving pipeline parity patterns

Pattern A: serialize full preprocessing + model pipeline a loadovať rovnaký artifact v serving. Je jednoduchý pri jednom language/runtime, ale potrebuje secure artifact loading a version compatibility.

Pattern B: export transformation graph/spec spolu s learned state a použiť ho v training/serving. TensorFlow Transform je príklad.

Pattern C: feature store/materialization s shared definitions, point-in-time offline retrieval a online serving. Stále potrebuje parity validation a freshness evidence.

Pattern D: independent implementations s strict contract, golden tests a shadow comparison. Je najrizikovejší, ale niekedy nutný.

```text
one definition
+ one fitted state
+ explicit schema
+ parity telemetry
```

Žiadny pattern automaticky nerieši target/future leakage. Parity a legitimacy sú separate gates.

## 18. Leakage detection techniques

Detection kombinuje lineage review, time availability checks, split/group overlap tests, suspicious feature importance, ablations, shuffled-label tests a unexpectedly high performance investigation.

```text
feature available_after_prediction_time > 0
→ forbidden

group overlap count > 0
→ evaluate against split contract

shuffled labels still high score
→ pipeline leakage alebo duplicated structure suspicion
```

Shuffled-label test nie je complete proof; some leakage patterns alebo data imbalance môžu stále vyžadovať analysis. Ablation feature groupu môže ukázať hidden target proxy.

Manual table review a domain expert často nájde semantics, ktoré generic scanner nepozná.

## 19. Skew detection techniques

Skew detection má viac vrstiev:

```text
schema parity
→ feature presence/type/vocabulary

matched-example parity
→ exact/tolerant value comparison

distribution parity
→ statistics/distances by cohort/time

model behavior parity
→ score/prediction comparison

business parity
→ action/outcome comparison
```

Matched examples sú silné pre transform bugs. Distribution metrics pokrývajú population at scale. Model-output comparison môže ukázať, či numeric differences sú material. Business outcome zostáva final evidence.

Sampling musí pokryť rare/unknown/missing/outlier cohorts, nie iba random majority. Privacy a retention constraints určujú, čo možno logovať.

## 20. Drift oproti skew

Drift je change data alebo relationship v čase. Skew porovnáva training a serving representations/populations, často v rovnakom deployment period-e. Serving data môže driftovať od trainingu a preto vytvoriť distribution skew; terms sa prekrývajú, ale diagnosis potrebuje reference pair.

```text
training-serving skew:
train snapshot vs current serving

drift:
serving span N vs serving span N+1
```

Schema bug môže vytvoriť skew bez real-world driftu. Legitímna campaign môže vytvoriť drift/skew bez implementation bug-u. Response sa líši: repair pipeline versus retrain/recalibrate/policy adaptation.

## 21. Leakage a skew v RAG/LLM context-e

Aj keď sekcia sa sústredí na ML fundamentals, principles pokračujú do LLM. Evaluation corpus môže leaknúť do prompt examples alebo fine-tuning data. Retrieval index môže obsahovať answer keys. Production prompt/template alebo tokenizer sa môže líšiť od evaluation. Tool results môžu používať future state.

```text
eval item appears in training/few-shot context
→ benchmark leakage

same model, different system prompt/retrieval policy
→ serving generation skew
```

Preto exact system generation a contamination checks zostávajú potrebné aj bez klasickej feature matrix.

## 22. Worked incident `ML-PAY-84`

Atlas model mal štyri vrstvy leakage, ktoré sa navzájom zosilňovali. Každá vrstva preniesla inú forbidden information: shared entity context, future outcome, test distribution alebo test labels a human feedback. Preto nestačilo odstrániť jednu podozrivú column a znovu spustiť training.

1. Retry/entity leakage — random row split umiestnil attempts rovnakej operation a histories rovnakých merchantov do train aj test, takže model mohol využívať shared identity patterns namiesto generalization na nový decision subject.
2. Temporal leakage — current-state chargeback aggregate obsahoval outcomes a corrections, ktoré pri historical authorization time ešte neexistovali.
3. Preprocessing leakage — scaler a encoder boli fitnuté na all data, čím training transform získal means, variance a vocabulary aj z validation/test population.
4. Selection/test leakage — target-based selector videl all labels a repeated test dashboard viedol engineerov k ďalším feature changes, takže test prestal byť nezávislou acceptance population.

Serving potom pridal tri skew vrstvy. Tie už nemenili, čo sa model naučil, ale menili feature vector, ktorý loaded artifact dostal pre live operation. Vďaka tomu mohol model endpoint úspešne odpovedať a zároveň vykonávať úplne inú numeric function než pri offline evaluation.

1. Amount unit mismatch — jedna route poslala cents do transformácie očakávajúcej euros, takže scaled amount bol rádovo odlišný bez schema alebo shape erroru.
2. Category normalization mismatch — offline path uppercasoval country codes a mal fitted unknown policy, zatiaľ čo online lookup bol case-sensitive a legitimate categories mapoval do unknown bucketu.
3. Availability/freshness mismatch — offline history bola po backfill-e complete, kým online aggregates boli stale alebo missing a fallback ich ticho nahradil ordinary values.

```text
high offline score
+ model endpoint 200
- legitimate information boundary
- training-serving parity
= false confidence
```

Rollback iba weights nepomohol, pretože serving preprocessing a feature service zostali mismatchnuté. Tím musel obnoviť data/split/feature/pipeline/model system generation.

## 23. Evidence-preserving containment a recovery

Tím zachoval split manifests, source snapshots, feature lineage, preprocessing/selector state, offline/online matched vectors, runtime artifacts, score distributions a business actions. Automatické review routing bolo zablokované pre mismatched schema digest; fallback rules pokračovali.

Recovery prebiehala po vrstvách:

```text
remove forbidden future/target information
→ rebuild point-in-time dataset
→ create group/time split
→ fit transforms/selectors only in train/CV
→ publish unified transform/model artifact
→ shadow matched-example parity
→ distribution/cohort checks
→ business top-K validation
```

Každá oprava mala predecessor/successor digest. Old optimistic report zostal archived ako contaminated evidence, nie vymazaný.

## 24. Acceptance contract

Leakage positive acceptance znamená, že každá feature má availability pred alebo v prediction time, group/time split rules držia, fitted transforms/selectors videli iba allowed domain a test neovplyvnil development decisions. Lineage musí umožniť independent review.

Skew positive acceptance znamená, že serving schema/digest zodpovedá model contractu, matched examples majú equal/tolerated values, distribution differences sú vysvetlené a representative business path používa intended artifact.

Recovery path musí oddeliť repair implementation skew od model retraining pri legitimate drift. Fallback nesmie ticho používať stale/zero values, na ktorých model nebol validovaný.

Forbidden paths:

```text
post-outcome/label information enters features
related samples cross forbidden split boundary
all-data preprocessing/selection fit
repeated test feedback remains called untouched
training and serving share name but not semantics/digest
online stale/missing value silently becomes ordinary value
parity is accepted without prediction-time legitimacy
endpoint 200 is accepted without feature/business evidence
```

Second-operation test použije fresh operation s new category, missing/stale feature a representative history. Overí point-in-time legitimacy, offline/online vector parity, exact loaded artifact, safe fallback, no duplicate action a delayed outcome lineage. Second-time-window test overí, či skew/drift alerts rozlíšia legitimate population change od transform bug-u.

## Kontrolné otázky

1. Ako sa data leakage líši od train-serving skew?
2. Prečo perfect training-serving parity môže stále obsahovať leakage?
3. Čo je target a temporal leakage?
4. Kedy entity overlap je leakage a kedy intended scenario?
5. Ako scaler alebo encoder leakne test distribution?
6. Prečo feature selection patrí do fold/train pipeline?
7. Ako repeated test feedback kontaminuje evidence?
8. Prečo unknown recent label nie je negative?
9. Ako cross-sample aggregate leakne targets?
10. Čo je schema, feature, distribution a transformation skew?
11. Ako availability/freshness vytvára skew aj pri rovnakej logic?
12. Prečo absence labelu v serving nie je automaticky schema skew?
13. Aké parity architecture patterns existujú?
14. Ktoré tests pomáhajú odhaliť leakage?
15. Aké vrstvy skew detection treba kombinovať?
16. Ako sa drift líši od skew?
17. Prečo weights rollback nevyriešil `ML-PAY-84`?
18. Aké positive, recovery, forbidden a second-operation testy uzatvárajú leakage/skew contract?

## Glossary impact

Relevantné pojmy: data leakage, target leakage, temporal leakage, entity/group leakage, preprocessing leakage, feature-selection leakage, test contamination, cross-sample leakage, train-serving skew, schema skew, feature skew, distribution skew, transformation skew, availability skew, matched-example parity, prediction-time legitimacy, drift, TFDV schema environment a leakage/skew acceptance contract.

## Primárne zdroje

- [scikit-learn — Common pitfalls and recommended practices](https://scikit-learn.org/stable/common_pitfalls.html)
- [scikit-learn — Pipelines and composite estimators](https://scikit-learn.org/stable/modules/compose.html)
- [TensorFlow Data Validation guide](https://www.tensorflow.org/tfx/guide/tfdv)
- [TensorFlow Data Validation tutorial: drift and skew](https://www.tensorflow.org/tfx/tutorials/data_validation/tfdv_basic)
- [TensorFlow Data Validation — `DetectFeatureSkew`](https://www.tensorflow.org/tfx/data_validation/api_docs/python/tfdv/DetectFeatureSkew)
- [TensorFlow Transform preprocessing best practices](https://www.tensorflow.org/tfx/guide/tft_bestpractices)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Feature engineering a feature selection](feature-engineering-feature-selection.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Linear a logistic regression →](linear-logistic-regression.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
