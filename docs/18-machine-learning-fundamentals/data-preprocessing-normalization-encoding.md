# Data preprocessing, normalization a encoding

Raw business data nie je automaticky model input. Preprocessing prevádza source values na representation, ktorú estimator dokáže bezpečne a konzistentne spracovať. Tento krok zahŕňa typovanie, parsing, missing-value semantics, scaling, normalization, category encoding, text alebo time transformations a niekedy learned statistics. Ak sa preprocessing fitne na nesprávnej population alebo sa v serving implementuje inak, model dostane inú feature generation než tú, na ktorej bol validovaný.

V incidente `ML-PAY-84` Atlas používal jednu notebook transformáciu pre training a samostatný Java service pre online inference. Notebook fitol `StandardScaler` nad celým datasetom pred splitom, one-hot vocabulary sa vytvorila z train aj test categories a missing values sa dopĺňali nulou. Serving service používal iné rounding, category fallback a amount unit. Model endpoint zostal zelený, no loaded feature vectors už nepatrili k training contractu.

## 1. Dominantný preprocessing lifecycle

Preprocessing sa navrhuje ako versionovaný transform graph medzi raw schema a model feature schema. Každý transform musí určiť, či je stateless alebo fitted, aké input semantics očakáva, čo uloží ako state, ako spracuje unknown/missing/out-of-range values a ako sa rovnaká logic dostane do training aj serving pathu.

```text
raw source record + prediction time
→ parsing a type/unit validation
→ missing/invalid state handling
→ stateless transformations
→ fitted transformations learned iba z train
→ encoded feature vector + schema/order
→ model inference
→ feature read-back a parity evidence
```

Preprocessing nie je iba „čistenie dát“. Mení geometry, distance, coefficient meaning, category space a model compatibility. Fitted scaler alebo encoder je súčasťou model artifact generation a musí byť publikovaný, rollbackovaný a auditovaný spolu s estimatorom.

## 2. Exact preprocessing subject

```yaml
preprocessing_subject: PREP-ML-PAY-84-v4
raw_schema: payment-operation-event-v7
prediction_time: authorization_received_at
pipeline_code: git:4a91c7d
runtime: python:3.12-sklearn:1.9
steps:
  - validate_types_units
  - derive_operation_age_seconds
  - numeric_imputer: median-from-train
  - numeric_scaler: standard-scaler-from-train
  - categorical_encoder:
      type: one-hot
      vocabulary: fitted-from-train
      unknown: infrequent_bucket
  - feature_order: model-input-v6
fitted_state_digest: sha256:5c82...1d9a
output_schema_digest: sha256:9e31...702f
serving_implementation: serialized-pipeline-artifact
```

Subject oddeľuje source schema od output feature schema a code od fitted state. Rovnaký code s iným training windowom môže vytvoriť iné means, medians alebo category vocabulary. Rovnaký fitted state v inom runtime/library version môže mať compatibility alebo numeric differences.

## 3. Stateless a fitted transformations

Stateless transform používa iba hodnotu aktuálneho sample-u a explicitnú configuration. Napríklad prevod cents na euros, logarithm s pinned policy alebo extraction hour z timestampu môže byť stateless, ak nepotrebuje population statistics.

Fitted transform sa učí state z training data. `StandardScaler` sa učí mean a variance, imputer median, one-hot encoder categories a feature selector relationship k targetu. Jeho `.fit()` authority musí byť obmedzená na training subset alebo fold-train.

```text
stateless:
amount_minor / 100

fitted:
(amount - mean_train) / std_train
```

Rozdiel určuje leakage risk aj deployment packaging. Stateless code stále môže byť nesprávne versionovaný alebo mať unit bug, ale fitted transform navyše nesie learned state, ktorý musí byť uložený a read-backnutý.

## 4. Parsing, data types a units

Preprocessing začína ešte pred numerickým scalingom. String timestamp musí mať timezone, amount unit a currency, boolean tri-state semantics, integer range a category normalization policy. Tichý cast môže vytvoriť validný typ s nesprávnym meaningom.

```python
from decimal import Decimal

amount_minor = int(record["amount_minor"])
if amount_minor < 0:
    raise ValueError("amount_minor must be non-negative")

amount_eur = Decimal(amount_minor) / Decimal(100)
```

Float nie je vždy vhodný pre authoritative money computation, aj keď model features môžu nakoniec používať float. Business amount a model representation sa oddeľujú. Currency conversion potrebuje rate source a timestamp; nemožno spojiť EUR a USD amounts bez explicitnej transformácie.

Timezone-naive timestamp môže meniť hour/day features. Locale-specific decimal alebo category normalization môže viesť k iným values v batch a online parseri.

## 5. Missing value nie je jedna vec

Missing môže znamenať, že property neexistuje, ešte nebola observed, source zlyhal, value bola redacted, entity nemá history alebo feature pipeline nestihla update. Jedna sentinel nula môže tieto states nebezpečne zlúčiť.

```text
merchant_decline_rate_1h = null
possible meanings:
- no attempts in window
- feature service unavailable
- late event processing
- new merchant
- access denied
```

Imputation policy musí byť feature-specific a môže pridať missing indicator. Median imputation z training data je fitted state. „Unknown category“ a missing category môžu mať odlišný meaning.

```python
from sklearn.impute import SimpleImputer

imputer = SimpleImputer(
    strategy="median",
    add_indicator=True,
)
```

Imputer success nepreukazuje, že missingness mechanism zostal rovnaký v produkcii. Spike missing indicators môže byť incident, nie ordinary model input.

## 6. Scaling a standardization

Scaling mení numeric features na comparable range alebo distribution. Standardization typicky odčíta training mean a delí training standard deviation. `StandardScaler` používa fitted mean/variance pre následný `transform`.

```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_validation_scaled = scaler.transform(X_validation)
```

Validation/test sa nesmú použiť pri `.fit()`. Their values sa transformujú stateom z train. Mean a variance sú artifact, nie environment-wide constants.

Scaling je dôležitý pre algorithms citlivé na magnitude, distance alebo gradient optimization, napríklad linear models s regularization, SVM, k-nearest neighbors a neural networks. Tree-based split methods často scaling nepotrebujú, pretože ordering jedného feature zostáva rovnaký, hoci preprocessing môže byť stále potrebný pre missing/categories.

## 7. Normalization a terminologická hranica

„Normalization“ sa používa nejednotne. Môže znamenať min-max scaling features, transformáciu sample vectoru na unit norm alebo všeobecné uvedenie hodnôt do standard formy. Dokumentácia musí uviesť exact operation.

Feature-wise min-max scaling:

```text
x' = (x - min_train) / (max_train - min_train)
```

Sample-wise L2 normalization:

```text
x' = x / ||x||₂
```

Tieto operácie menia inú axis. Min-max používa training population extrema a je citlivý na outliers aj future values mimo range. Sample normalization mení relative magnitude features v jednej row a môže odstrániť dôležitú scale information.

Termín bez formula/state nie je reprodukovateľný contract.

## 8. Robust, nonlinear a distribution transforms

Outliers alebo skewed distributions môžu motivovať robust scaling, logarithm, quantile alebo power transforms. Každý transform nesie domain assumptions.

```python
import numpy as np

log_amount = np.log1p(amount_minor)
```

`log1p` vyžaduje input `>= -1`; pri non-negative amount je domain jasná. Clipping outliers môže stabilizovať model, ale tiež skryť legitímne high-value operations. Boundaries musia byť learned/pinned, monitored a business-reviewed.

Quantile transform fitted na training distribution môže mapovať serving extremes na boundary values. Pri drift-e môže compressovať novú information. Transform selection sa hodnotí v pipeline, nie len podľa krajšieho histogramu.

## 9. Categorical encoding

Mnohé estimators vyžadujú numeric representation categories. One-hot encoding vytvorí binary column pre categories. Ordinal encoding priradí integer codes, ktoré môžu neúmyselne implikovať ordering. Target encoding používa relationship s labelom a má vysoký leakage risk.

```python
from sklearn.preprocessing import OneHotEncoder

encoder = OneHotEncoder(
    handle_unknown="infrequent_if_exist",
    min_frequency=100,
    sparse_output=True,
)
X_train_cat = encoder.fit_transform(train_categories)
X_serving_cat = encoder.transform(serving_categories)
```

Vocabulary sa fituje na train. Unknown category policy musí byť explicitná. `handle_unknown="ignore"` typicky vytvorí all-zero vector pre unseen category, čo môže byť zameniteľné s dropped baseline alebo missing state. Model a monitoring musia tento meaning poznať.

High-cardinality IDs často nie sú vhodné na naive one-hot. Môžu viesť k memorization, huge sparse matrix a unseen categories. Hashing alebo learned embeddings majú vlastné collision, stability a serving contracts.

## 10. Ordinal encoding a false ordering

OrdinalEncoder je vhodný, keď categories majú skutočné poradie alebo estimator interpretuje codes iba ako categories bezpečným spôsobom. Priradiť `DE=0, FR=1, SK=2` linear modelu vytvára artificial distance a order medzi countries.

```text
country code 0, 1, 2
≠
DE < FR < SK
```

Pre ordered categories ako risk tier `low < medium < high` musí mapping zostať pinned. Pridanie novej category medzi existujúce môže zmeniť codes a model compatibility. Category vocabulary je schema generation.

Tree model môže splitovať integer codes spôsobom závislým od arbitrary orderu, ak nemá native categorical semantics.

## 11. Target encoding a leakage

Target encoding nahrádza category statisticou targetu, napríklad average positive rate. Ak sa vypočíta nad rovnakou row alebo celým datasetom, priamo prenáša label information do feature.

```text
merchant category target mean
= average y pre merchant
```

Training target encoding potrebuje out-of-fold alebo leave-one-out-like procedure, smoothing a handling unseen categories. Validation/test sa transformujú mappings fitnutými iba na train. V time-based use case mapping nesmie používať future labels.

Target encoding artifact zahŕňa category counts, smoothing prior, label horizon a fit population. Je to learned model-like state, nie obyčajný lookup table.

## 12. Text, timestamps a structured extraction

Text preprocessing môže zahŕňať tokenization, vocabulary, n-grams, TF-IDF alebo embeddings. Vocabulary a inverse document frequency sú fitted state. Timestamp features môžu byť hour/day, elapsed time alebo cyclical encoding; musia rešpektovať timezone a prediction time.

```python
from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer = TfidfVectorizer(
    ngram_range=(1, 2),
    min_df=20,
)
X_train_text = vectorizer.fit_transform(train_text)
X_test_text = vectorizer.transform(test_text)
```

Text môže obsahovať labels, post-outcome notes, PII alebo analyst decisions. Preprocessing pipeline musí filterovať forbidden fields pred vocabulary fitom. Redaction po vectorization môže byť neskoro, pretože vocabulary alebo artifact už môže obsahovať sensitive tokens.

## 13. ColumnTransformer a heterogeneous schema

Tabulárny dataset často kombinuje numeric a categorical features. `ColumnTransformer` umožňuje explicitne priradiť pipelines columns a zachovať feature names/order.

```python
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

numeric = make_pipeline(
    SimpleImputer(strategy="median", add_indicator=True),
    StandardScaler(),
)
categorical = make_pipeline(
    SimpleImputer(strategy="most_frequent"),
    OneHotEncoder(handle_unknown="ignore"),
)

preprocessor = ColumnTransformer(
    [
        ("num", numeric, numeric_columns),
        ("cat", categorical, categorical_columns),
    ],
    remainder="drop",
)
```

Explicit `remainder="drop"` zabraňuje, aby nový raw column ticho vstúpil do modelu. Column lists a output feature names musia byť versionované. Selection by dtype môže pri schema change nečakane pridať alebo vyradiť field.

## 14. Pipeline ako fit/transform a packaging boundary

Scikit-learn `Pipeline` spája preprocessing a estimator tak, aby cross-validation fitla transforms iba na fold-train a serving použil rovnaký fitted object.

```python
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression

pipeline = make_pipeline(
    preprocessor,
    LogisticRegression(max_iter=1000),
)
pipeline.fit(X_train, y_train)
probabilities = pipeline.predict_proba(X_test)[:, 1]
```

Pipeline znižuje risk manuálneho orderu, ale custom transformer môže stále používať global state, current database alebo target leak. Serializovaný object môže byť nebezpečný pri untrusted source a library compatibility. Artifact musí mať provenance, digest a supported load environment.

Production serving môže embednúť transform graph do model artifactu alebo používať shared transformation service/library. Dve ručne prepisované implementations vytvárajú parity risk.

## 15. Online a offline preprocessing parity

Offline training často používa SQL/Spark/Python, online serving Java/Go/feature store. Rovnaké feature names nepreukazujú rovnaké values. Rozdiely vznikajú v rounding, timezone, window boundaries, missing fallback, category normalization, late events a floating-point behavior.

```text
same raw operation
→ offline transform vector
→ online transform vector
→ compare feature-by-feature + schema/order
```

Golden examples s pinned raw input a expected vectorom sú užitočné, ale nepokrývajú population. Shadow logging/replay môže porovnať sample online features s offline recomputation. Raw sensitive data a feature vectors vyžadujú access/retention controls.

TensorFlow Transform rieši tento problém exportom transform graphu a learned statistics na použitie v training aj serving. Principle je všeobecný: one definition + one fitted state, nie dve „rovnaké“ codebases.

## 16. Schema, ordering a dtype compatibility

Model input array často neobsahuje names. Ak serving zmení column order, všetky values môžu mať validný dtype a shape, ale patriť nesprávnym features.

```text
training order:
[amount_scaled, decline_rate_scaled, country_DE, country_SK]

serving order:
[decline_rate_scaled, amount_scaled, country_DE, country_SK]
```

Model endpoint môže vrátiť score bez exception. Input schema digest, feature names/order a dtype/shape checks musia byť súčasťou artifact contractu.

Sparse/dense representation tiež ovplyvňuje memory a compatibility. One-hot output s vysokou cardinality môže pri neúmyselnom densify spôsobiť OOM.

## 17. Fit state read-back

Preprocessing artifact musí byť inspectable. Relevantné read-backs zahŕňajú scaler means/scales, imputer statistics, encoder categories, output feature names, schema digest a artifact/library versions.

```python
scaler = pipeline.named_steps["columntransformer"] \
    .named_transformers_["num"] \
    .named_steps["standardscaler"]
print(scaler.mean_)
print(scaler.scale_)
```

Tento output preukazuje loaded fitted state objektu, nie source dataset lineage. Treba ho spojiť s training manifestom a artifact digestom. Production process má exportovať loaded pipeline/model generation, nie raw sensitive state bez kontroly.

## 18. Preprocessing monitoring

Monitoring sleduje raw schema violations, missing rates, unknown categories, clipped/out-of-range values, transform failures, output sparsity, feature distributions a online/offline parity. Model score drift bez feature evidence je ťažko diagnostikovateľný.

```text
unknown_category_rate ↑
→ legitimate new business segment alebo stale vocabulary

missing_indicator ↑
→ source/feature pipeline incident alebo population change

scaled values extreme
→ drift, unit bug alebo stale fitted statistics
```

Alert threshold musí rešpektovať population a seasonality. Unknown category nie je automaticky failure, ak contract má safe bucket; môže však signalizovať reduced model validity.

## 19. Worked incident `ML-PAY-84`

Atlas notebook vykonal:

```python
X_all_scaled = scaler.fit_transform(X_all)
X_all_encoded = encoder.fit_transform(categories_all)
X_train, X_test = train_test_split(X_all_encoded)
```

Scaler videl test distribution a encoder vocabulary future categories. Missing `merchant_history_days` sa doplnil nulou, čo spojilo new merchant so source outage. Online Java service očakával `amount_eur` float, no event schema posielala `amount_minor`; conversion sa pri jednom route vynechal. Category normalization používala uppercase offline a case-sensitive lookup online.

Model server dostal správny vector length a vrátil HTTP `200`. Scores sa však posunuli. Feature parity sample ukázal:

```text
feature                 offline      online
amount_scaled            0.42       173.10
country_SK               1            0
country_unknown          0            1
history_missing          0            1
```

Tím pôvodne rollbackoval estimator weights, ale problem zostal, pretože preprocessing service generation bola independent. Root cause bol system artifact mismatch.

## 20. Evidence-preserving containment a recovery

Tím zachoval raw request IDs, redacted source records, offline/online vectors, fitted scaler/encoder state, model digest, code/runtime versions a serving route cohort. Stopped automatic actions pre vectors s mismatched schema digest a prešiel na approved baseline rules.

Recovery zabalila preprocessing a estimator do jedného immutable pipeline artifactu pre Python serving path. Pre cross-language consumers vytvorila canonical transformation specification, generated conformance tests a loaded schema handshake. Amount unit, timezone, missing categories a unknown handling boli explicitné.

```text
source schema v7
→ canonical transform implementation v4
→ fitted state digest
→ output schema v6
→ model digest
→ serving container digest
```

Training a serving používali rovnaký output schema hash. Shadow parity porovnala vectors na representative cohorts pred promotion.

## 21. Acceptance contract

Positive path musí preukázať raw schema/unit validity, fit transforms iba na allowed training domain, exact fitted state, deterministic output schema/order a production parity pre representative samples.

Recovery path musí umožniť rollback preprocessing + model compatible generations alebo forward fix bez tichého mixu. Unknown/invalid input má aktivovať explicitný reject/fallback, nie nezdokumentovanú nulu.

Forbidden paths:

```text
scaler/imputer/encoder fitne validation alebo test
label vstúpi do input transformu
unknown category mapuje na unrelated known category
amount/timezone/unit sa líši training vs serving
column order/dtype sa zmení bez schema generation
two implementations sa považujú za equal bez conformance evidence
model 200 sa vydáva za feature correctness
```

Second-record test použije novú operation z adjacent cohortu s missing/unknown/out-of-range values a overí exact fallback, vector schema, no exception/unsafe action a audit. Second-build test z rovnakých pinned inputs potvrdí rovnaký fitted state digest alebo vysvetlený numeric nondeterminism.

## Kontrolné otázky

1. Čím sa stateless transform líši od fitted transformu?
2. Prečo fitted preprocessing patrí k model artifactu?
3. Ako parsing typov, units a timezone mení model input?
4. Prečo missing value nie je automaticky nula?
5. Čo sa učí `StandardScaler` a z akej population?
6. Aké rôzne významy môže mať normalization?
7. Kedy scaling pomáha a kedy tree modelu často netreba?
8. Aké risks má one-hot encoding unknown categories?
9. Prečo ordinal codes môžu vytvoriť false ordering?
10. Ako target encoding leakne labels?
11. Prečo text vocabulary a IDF sú fitted state?
12. Ako `ColumnTransformer` a `Pipeline` chránia fit boundary?
13. Prečo dve ručne implementované transformácie nie sú parity evidence?
14. Ako input column order môže zlyhať bez exception?
15. Ktoré preprocessing state treba read-backnúť?
16. Ktoré metrics odhaľujú preprocessing drift alebo outage?
17. Prečo estimator rollback nevyriešil `ML-PAY-84`?
18. Aké positive, recovery, forbidden a second-record testy uzatvárajú preprocessing contract?

## Glossary impact

Relevantné pojmy: preprocessing, stateless transform, fitted transform, parsing, unit contract, missingness semantics, imputation, standardization, normalization, min-max scaling, sample normalization, robust transform, one-hot encoding, ordinal encoding, target encoding, category vocabulary, unknown category, `ColumnTransformer`, `Pipeline`, output feature schema, training-serving parity, conformance test a preprocessing acceptance contract.

## Primárne zdroje

- [scikit-learn — Preprocessing data](https://scikit-learn.org/stable/modules/preprocessing.html)
- [scikit-learn — `StandardScaler`](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html)
- [scikit-learn — `OneHotEncoder`](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.OneHotEncoder.html)
- [scikit-learn — `OrdinalEncoder`](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.OrdinalEncoder.html)
- [scikit-learn — Pipelines and composite estimators](https://scikit-learn.org/stable/modules/compose.html)
- [scikit-learn — Common pitfalls and recommended practices](https://scikit-learn.org/stable/common_pitfalls.html)
- [TensorFlow Transform — preprocessing best practices](https://www.tensorflow.org/tfx/guide/tft_bestpractices)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Train, validation a test split](train-validation-test-split.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Feature engineering a feature selection →](feature-engineering-feature-selection.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
