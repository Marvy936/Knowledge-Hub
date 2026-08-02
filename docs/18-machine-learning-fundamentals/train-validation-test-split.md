# Train, validation a test split

Train, validation a test split nie sú tri náhodné percentá jedného CSV súboru. Sú to tri odlišné evidence populations s rozdielnou authority. Training set smie meniť fitted parameters a learned preprocessing state. Validation set smie ovplyvniť výber model family, features, hyperparameters, threshold a ďalšie design decisions. Test set má zostať nedotknutý až do finálneho odhadu generalization pre vopred definovaný deployment scenario. Ak sa tá istá entity, future information alebo opakovane použitý test verdict prenesie cez tieto hranice, reported score prestáva byť nezávislým dôkazom.

Incident `ML-PAY-84` vznikol pri successor modeli Atlas Payments. Tím odstránil najviditeľnejší future feature z predchádzajúceho incidentu, ale následne rozdelil payment-attempt rows náhodne 80/10/10. Retry attempts jednej merchant operation a history rovnakého merchant-a skončili vo viacerých splits. Preprocessing a feature selection boli fitnuté nad celým datasetom a test set sa používal po každej iterácii. Výsledné „test AUC“ bolo v skutočnosti súčasťou development feedback loopu, nie nezávislý verdict.

## 1. Dominantný split lifecycle

Split design začína intended deploymentom. Najprv sa určí prediction time, entity/group identity, time horizon, production population a spôsob, akým sa model bude retrainovať. Až potom sa vytvorí immutable assignment samples do train, validation a test evidence domains.

```text
business deployment scenario
→ sample, group a time identity
→ leakage a dependency analysis
→ immutable split policy
→ train fit domain
→ validation selection domain
→ frozen test acceptance domain
→ production shadow/canary evidence
→ delayed outcome read-back
```

Split assignment musí vzniknúť pred akýmkoľvek transformom, ktorý sa učí z population statistics alebo labels. Raw records môžu byť fyzicky uložené spolu, ale logical membership a allowed operations musia byť explicitné. Reproducibility vyžaduje split manifest, nie iba `random_state=42` bez stable input orderu a dataset digestu.

## 2. Exact split subject

Tvrdenie „použili sme 80/10/10“ nehovorí, čo bolo izolované. Exact subject musí pomenovať dataset generation, sample key, grouping unit, time boundaries, stratification, label maturity, assignment algorithm, seed alebo hash policy a intended use každej subsety.

```yaml
split_subject: SPLIT-ML-PAY-84-v3
dataset_manifest: DATASET-ML-PAY-83-v2
sample_key: merchant_operation_id
group_key: merchant_id
prediction_time: authorization_received_at
label_mature_through: 2026-06-30T23:59:59Z
strategy: grouped-temporal
train:
  prediction_time: 2025-01-01..2026-03-31
validation:
  prediction_time: 2026-04-01..2026-04-30
  purpose: model, feature, hyperparameter and threshold selection
test:
  prediction_time: 2026-05-01..2026-05-31
  purpose: one final pre-production generalization estimate
group_policy: merchant_id must not cross train/validation/test
embargo_gap: 7d
manifest_digest: sha256:83c1...7e11
```

Taký split reprezentuje future deployment na novšom time windowe a zároveň zabraňuje, aby merchant-specific history presiakla medzi evidence domains. Nemusí byť vhodný pre každý use case, ale jeho assumptions sú auditovateľné.

## 3. Training set ako fit authority

Training set je jediná population, z ktorej sa počas developmentu učia model parameters a fitted state transformov. Zahŕňa to weights, tree splits, cluster centers, normalization means, category vocabularies, imputation values, selected features a target encodings.

```text
train raw samples
→ fit preprocessing state
→ transform train
→ fit estimator
→ fitted pipeline candidate
```

Training metric odpovedá, ako candidate model fituje data, ktoré mohol použiť pri učení. Neodhaduje sama generalization. Veľký rozdiel medzi training a validation performance môže signalizovať overfitting, ale podobné score tiež nepreukazuje, že split je nezávislý; leakage môže nafúknuť obe.

Augmentation alebo resampling sa typicky vykonáva iba v training domain. Synthetic alebo duplicated training examples nesmú byť následne rozdelené do validation/test, pretože by vytvorili priamych relatives naprieč evidence hranicou.

## 4. Validation set ako design-feedback authority

Validation set sa používa na rozhodnutia, ktoré nie sú learned parameters jedného fitu, ale stále formujú final system. Výber model family, preprocessing variantu, feature setu, regularization strength, early stopping epoch, calibration method, threshold alebo ranking formula používa validation evidence.

```text
candidate A/B/C
→ fit iba na train
→ evaluate na validation
→ design decision
→ nový candidate
```

Každé opakované pozretie na validation score adaptuje development k tejto sete. Validation set sa tým postupne stáva súčasťou optimization loopu, aj keď estimator `.fit()` nikdy priamo nedostal jej rows. Pri mnohých experimentoch môže tím overfitnúť validation verdict cez human/model selection.

Preto sa má evidovať experiment count, decision rationale a final locked configuration. Ak je search rozsiahly, cross-validation alebo nested evaluation môže lepšie oddeliť tuning od final estimate, ale ani to nenahrádza deployment-representative untouched test alebo production evidence.

## 5. Test set ako obmedzená acceptance authority

Test set má poskytovať posledný nezávislý offline odhad pre locked pipeline generation. Nemá sa používať na feature selection, threshold tuning, debugging ani rozhodovanie, ktorý model publikovať. Ak tím po test score zmení model a znovu testuje na rovnakých rows, test sa stal ďalším validation setom.

```text
freeze:
data contract + split + preprocessing + features + model + threshold
→ fit final candidate podľa vopred definovaného post-selection postupu
→ evaluate raz na test
→ accept/reject podľa predeclared criteria
```

„Raz“ nie je matematická absolútna podmienka, ale governance boundary. Bug v evaluation code môže vyžadovať rerun, no dôvod a zmena musia byť zaznamenané. Opakované model tweaks podľa test resultu degradujú jeho nezávislosť a môžu vyžadovať nový untouched test cohort.

Test metric nepreukazuje production outcome. Reprezentuje iba defined samples, labels, horizon a offline execution. Shadow/canary, serving parity, latency, capacity, delayed labels a human/tool behavior zostávajú ďalšie acceptance vrstvy.

## 6. Random split a jeho assumptions

`train_test_split` alebo shuffled K-fold predpokladá, že samples sú dostatočne independent a exchangeable pre intended deployment. Je vhodný, keď row order nenesie deployment-relevant time, neexistujú groups s shared information a future samples majú podobnú distribution.

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=17,
    stratify=y,
)
```

Tento kód zabezpečí reprodukovateľné pseudonáhodné rozdelenie pre rovnaké ordered inputs. Nezabezpečí entity isolation, point-in-time correctness ani future deployment realism. Ak input order alebo rows zmenia generation, rovnaký seed môže priradiť iné samples.

Random split v `ML-PAY-84` rozdelil retries a merchant history. Model sa na teste stretol s veľmi podobnými patterns, ktoré už videl v trainingu. Reported score meral interpolation medzi related rows, nie generalization na nové operations alebo future merchants.

## 7. Stratification a class proportions

Stratified split sa snaží zachovať class proportions medzi subsets. Je užitočný pri rare classes, aby validation/test neobsahovali náhodne príliš málo positives. Stratification však nie je leakage prevention a nemusí rešpektovať groups alebo time.

```text
global positive rate: 0.4 %
random small test bez stratification:
possible positives: veľmi málo alebo nevyvážene
```

Presné zachovanie prevalence môže byť dokonca nerealistické, ak production prevalence seasonálne mení. Cieľom je stabilná evaluácia a relevantný scenario, nie kozmeticky rovnaké percento.

Pri grouped split-e môže byť nemožné presne zachovať proportions a zároveň izolovať groups. Group isolation má prednosť, ak shared entity information spôsobuje leakage. Metric uncertainty a sample counts treba reportovať otvorene.

## 8. Group-aware split

Group-aware splitting drží related samples v jednej evidence domain. Group môže byť patient, merchant, customer, device, document source, site, household alebo session. Choice group keyu vychádza z toho, aká shared information by umožnila modelu zapamätať si identity alebo context, ktorý sa v deployment scenario nemá zdieľať.

```python
from sklearn.model_selection import GroupShuffleSplit

splitter = GroupShuffleSplit(
    n_splits=1,
    test_size=0.2,
    random_state=17,
)
train_idx, test_idx = next(
    splitter.split(X, y, groups=merchant_ids)
)
```

Group split izoluje merchant identities, ale ak production predikuje budúce operations existujúcich merchantov, úplná merchant isolation môže byť príliš prísny alebo iný scenario než intended. Môžu byť potrebné dve evaluations: future operations known merchants a cold-start unseen merchants.

Group key nesmie byť odvodený až po leakage. Hash podobnosti, shared account ownership alebo retries môžu vytvárať hidden groups, ktoré explicitný merchant ID nezachytí.

## 9. Time-based split

Time-based split simuluje training na minulosti a evaluation na budúcnosti. Je nevyhnutný, keď patterns, policy, labels alebo population menia čas, alebo keď production model vždy predikuje future events.

```python
train = data[data.prediction_time < "2026-04-01"]
validation = data[
    (data.prediction_time >= "2026-04-01")
    & (data.prediction_time < "2026-05-01")
]
test = data[
    (data.prediction_time >= "2026-05-01")
    & (data.prediction_time < "2026-06-01")
]
```

Scikit-learn `TimeSeriesSplit` poskytuje increasing historical train windows a later test windows pre equally spaced samples. V event data však treba často vlastný splitter, pretože events nie sú equally spaced, labels majú delay a groups sa prekrývajú.

Time split sám nezaručuje point-in-time features. Future-derived aggregates môžu byť prítomné aj v historical row. Takisto nezaručuje group isolation: long-lived merchant sa môže objaviť v train aj test, čo môže byť intended alebo leakage podľa use case.

## 10. Gap, embargo a label overlap

Pri rolling windows môžu training features alebo labels časovo prekrývať evaluation period. Ak target sleduje outcome 30 dní po prediction time, training sample z 25. apríla používa label events až do 25. mája. Test začínajúci 1. mája môže byť ovplyvnený rovnakým real-world episode alebo data correction.

```text
train prediction: Apr 25
label window:      Apr 25 — May 25

test prediction:  May 01
```

Gap alebo embargo oddeľuje periods, aby sa znížilo overlap leakage a umožnila label maturity. Dĺžka vychádza z feature windows, target horizon, delayed reconciliation a entity behavior, nie z arbitrary jedného dňa.

Purging môže odstrániť training observations, ktorých label window prekrýva test interval. Táto policy musí byť súčasťou split manifestu a reprodukovateľná.

## 11. Spatial, site a cohort split

Niektoré deploymenty generalizujú na nové locations, hospitals, countries, devices alebo business units. Random rows naprieč sites môžu zdieľať site-specific calibration, process alebo identity. Site holdout ukáže transfer na unseen environment.

```text
train: sites A–H
validation: site I
test: site J
```

Taký test môže mať vysokú variance, pretože jedna site reprezentuje konkrétnu population. Opakované leave-one-group-out evaluations alebo viac held-out sites môžu poskytnúť broader picture. Stále treba reportovať, čo presne test population reprezentuje.

## 12. Cross-validation a jeho role

Cross-validation opakovane vytvára train/validation folds, aby odhadla variability a využila data efektívnejšie. Každý fold musí fitnúť celý learned pipeline iba na fold-train a transformovať fold-validation. Preprocessing mimo pipeline môže leaknúť aj pri správnom splitter-i.

```python
from sklearn.model_selection import GroupKFold, cross_validate
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

pipeline = make_pipeline(
    StandardScaler(),
    LogisticRegression(max_iter=1000),
)
cv = GroupKFold(n_splits=5)
results = cross_validate(
    pipeline,
    X,
    y,
    groups=merchant_ids,
    cv=cv,
    scoring=["roc_auc", "average_precision"],
    return_estimator=True,
)
```

Cross-validation results nie sú nezávislé samples v štatistickom zmysle; folds zdieľajú data. Report treba interpretovať ako variability naprieč defined partitions, nie ako päť produkčných deployments.

## 13. Nested cross-validation

Nested cross-validation oddeľuje inner model/hyperparameter selection od outer performance estimation. Inner folds vyberú configuration, outer held-out fold odhadne generalization celého selection procedure.

```text
outer train
├── inner train/validation search
└── selected configuration
→ outer test score
```

Je užitočná pri malom datasete a rozsiahlej selection. Je computationally expensive a stále musí používať správny group/time splitter. Nested random K-fold neopraví nesprávny deployment scenario ani point-in-time leakage.

Final production model sa po evaluation môže refitnúť na väčšom approved data windowe. Potom však fitted artifact nie je totožný s outer-fold estimators; jeho acceptance sa opiera o validated procedure a nový artifact lineage, nie o tvrdenie, že bol priamo testovaný na rovnaký untouched set.

## 14. Refit po selection

Po výbere pipeline sa často train a validation data spoja a final estimator sa refitne pred testom alebo deploymentom. Tento postup je validný iba ak bol vopred definovaný a test zostáva untouched.

```text
selection:
train → candidates
validation → choose locked pipeline

final fit:
train + validation → final artifact

test:
final artifact → one acceptance evaluation
```

Ak preprocessing statistics alebo category vocabulary vzniknú pri final refit-e, sú novou fitted generation. Manifest musí zaznamenať final fit population a artifact digest. Test results patria tomuto final artifactu, nie predchádzajúcemu candidate fitu.

Pri time series môže spojenie train+validation pred testom realisticky používať všetku históriu dostupnú pred test windowom. Pri groups treba zachovať isolation voči test groups.

## 15. Split reproducibility a stable assignment

Random seed nestačí, ak source order a row inventory nie sú immutable. Stabilnejší assignment môže používať hash stable sample/group keyu a split salt/version. Time/group policy však často vyžaduje explicitné rules.

```python
import hashlib

def bucket(key: str, salt: str = "split-v3") -> int:
    digest = hashlib.sha256(f"{salt}:{key}".encode()).digest()
    return int.from_bytes(digest[:8], "big") % 100
```

Hash assignment umožňuje, aby nový sample dostal deterministic subset bez prehadzovania starých rows. Môže však meniť time realism a class balance. Split policy musí riešiť append-only updates, corrections, deleted samples a new groups.

Manifest má obsahovať explicitné sample/group counts a membership digest. Read-back musí potvrdiť, že training job načítal rovnaký split artifact, nie recomputed mutable view.

## 16. Test contamination cez human feedback

Data nemusí fyzicky prejsť do trainingu, aby test kontaminoval development. Ak engineer opakovane číta errors na test rows, pridáva features pre konkrétne patterns alebo mení threshold podľa test score, information sa preniesla cez človeka.

```text
look at test failures
→ design feature
→ refit model
→ test again on same rows
```

Test sa stal validation feedback. Riešením nie je zakázať debugging, ale správne pomenovať evidence domain a vytvoriť nový untouched acceptance cohort po rozsiahlej adaptácii. Experiment ledger má zaznamenať, ktoré datasets ovplyvnili decisions.

Public benchmarks majú podobný problem: repeated community optimization môže overfitnúť hidden test distribution. Produkčný acceptance preto nemá stáť iba na benchmark leaderboard-e.

## 17. Split a preprocessing order

Learned preprocessing sa fituje iba na training subset v každom evaluation context-e. Nesprávny postup:

```python
X_scaled = scaler.fit_transform(X_all)
X_train, X_test = train_test_split(X_scaled)
```

Scaler means a variances už videli test population. Správny pipeline postup:

```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=17
)
pipeline.fit(X_train, y_train)
score = pipeline.score(X_test, y_test)
```

Pri cross-validation pipeline zabezpečí, že každý transformer `.fit()` vidí iba fold-train. Custom transforms musia rešpektovať rovnaký fit/transform contract.

## 18. Split acceptance metrics a uncertainty

Report musí uviesť sample a group counts, time ranges, prevalence/target distribution, cohorts, confidence/uncertainty a missing-label policy. Jedna metric bez denominatora nevysvetľuje, či test obsahoval dostatok positives alebo relevantných groups.

```json
{
  "test_samples": 1482201,
  "test_merchants": 19044,
  "positives": 5612,
  "prediction_window": "2026-05",
  "label_mature_through": "2026-06-30",
  "unseen_merchant_share": 0.17
}
```

Confidence intervals alebo bootstrap musia rešpektovať dependence groups/time. Row bootstrap môže podhodnotiť uncertainty, ak retries alebo merchant observations korelujú.

## 19. Worked incident `ML-PAY-84`

Atlas pipeline vytvorila `84.2M` attempt rows. `train_test_split(..., stratify=y)` zachoval positive rate a dashboard vyzeral profesionálne. Retry attempts a merchant histories však prekročili hranice. `StandardScaler`, category vocabulary a target-based feature selector boli fitnuté pred splitom. Test score sa zobrazoval pri každom pull requeste a tím podľa neho iteroval features.

Reported test ROC AUC `0.94` sa po operation/group/time split-e znížil na `0.78`. Average precision a captured loss at K klesli ešte výraznejšie. Rozdiel neznamenal, že nový split „pokazil model“; odstránil information, ktorá v intended future deployment-e nemala byť dostupná.

Root causes:

```text
row-random split namiesto operation/group/time evidence
learned transforms fitnuté nad all data
feature selection videla test labels
repeated test inspection menila development
```

Tím už nemal untouched May cohort, preto final acceptance použila neskorší mature June window. May zostal diagnostic/validation evidence a bol tak aj označený.

## 20. Evidence-preserving containment a recovery

Tím zmrazil original split assignments, model artifacts, preprocessing state, experiment histories a test accesses. Nevymazal old score; označil ho ako contaminated estimate. Automatické promotion gates boli zastavené, kým nevznikol nový split manifest.

Recovery zaviedla:

```text
operation-level sample keys
group isolation podľa merchant identity
chronological train/validation/test windows
label-maturity cutoff a embargo gap
pipeline-local fit transformov a selectorov
separate validation dashboard
test access iba pre locked candidate
```

Split tests sa stali executable invariants: no sample overlap, no forbidden group overlap, time ordering, mature labels a expected counts. Final test report obsahoval artifact a split digests.

## 21. Acceptance contract

Positive path musí preukázať, že split policy zodpovedá intended deployment scenario, membership je immutable a všetok learned state bol fitnutý iba v allowed train domain. Validation decisions musia byť zaznamenané a test musí patriť locked pipeline generation.

Recovery path musí umožniť reprodukovať split z pinned datasetu a manifestu, vysvetliť corrections a vytvoriť nový untouched test pri contamination. Old contaminated reports sa nemažú; zostávajú evidence s opraveným statusom.

Forbidden paths:

```text
same operation alebo forbidden group crosses split
future samples train model pre past test
label window overlaps test bez purging/embargo contractu
scaler/encoder/selector fitne test data
engineer iteruje podľa test score a stále ho volá untouched
random seed bez dataset/order identity sa vydáva za reproducibility
```

Second-split test pridá nové operations alebo nový time span a overí deterministic assignment bez presunu existujúcich members, zachovanie group/time rules a správnu label maturity. Second-model test použije rovnaký frozen split a potvrdí, že experiment porovnáva candidates na identickej evidence population.

## Kontrolné otázky

1. Akú authority má training, validation a test set?
2. Prečo validation set ovplyvňuje model aj bez priameho `.fit()`?
3. Kedy sa test set stane ďalším validation setom?
4. Aké assumptions má random split?
5. Prečo stratification nezabraňuje leakage?
6. Ako sa vyberá group key?
7. Čo simuluje time-based split a čo nezaručuje?
8. Prečo target horizon môže vyžadovať embargo alebo purging?
9. Aký je rozdiel medzi group a site holdoutom?
10. Ako pipeline zabraňuje preprocessing leakage v cross-validation?
11. Čo oddeľuje nested cross-validation?
12. Kedy možno refitnúť na train + validation?
13. Prečo seed sám negarantuje reproducible membership?
14. Ako human inspection kontaminuje test?
15. Ktoré metadata patria do split reportu?
16. Prečo pokles score po oprave `ML-PAY-84` neznamenal horší evaluation design?
17. Aké positive, recovery, forbidden a second-split testy uzatvárajú split contract?

## Glossary impact

Relevantné pojmy: training set, validation set, test set, fit authority, selection feedback, untouched test, random split, stratification, group-aware split, time-based split, site holdout, gap, embargo, purging, cross-validation, nested cross-validation, refit, split manifest, stable hash assignment, test contamination, deployment scenario a split acceptance contract.

## Primárne zdroje

- [scikit-learn — Cross-validation: evaluating estimator performance](https://scikit-learn.org/stable/modules/cross_validation.html)
- [scikit-learn — `train_test_split`](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html)
- [scikit-learn — `GroupShuffleSplit`](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupShuffleSplit.html)
- [scikit-learn — `GroupKFold`](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupKFold.html)
- [scikit-learn — `TimeSeriesSplit`](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html)
- [scikit-learn — Common pitfalls and recommended practices](https://scikit-learn.org/stable/common_pitfalls.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Regression, classification, ranking a clustering](regression-classification-ranking-clustering.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Data preprocessing, normalization a encoding →](data-preprocessing-normalization-encoding.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
