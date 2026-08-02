# Regression, classification, ranking a clustering

Regression, classification, ranking a clustering nie sú iba štyri algorithm menus. Sú to odlišné formulations otázky, ktorú systém kladie dátam. Regression odhaduje numeric quantity, classification vyberá class alebo odhaduje class probability, ranking optimalizuje relatívne poradie items v jednom context-e a clustering hľadá groups bez authoritative class labels. Nesprávne formulation môže vytvoriť model s dobrým offline score, ktorý nevie podporiť skutočné business rozhodnutie.

Incident `ML-PAY-83` to ukazuje priamo. Atlas potreboval denne vybrať najhodnotnejších `2 500` merchant operations na manuálny review. Tím však formuloval problém ako binary classification a reportoval overall accuracy pri default thresholde. Business operation bola v skutočnosti capacity-constrained ranking: kto má byť v top queue a v akom poradí. Classification probability mohla byť užitočný input, no sama neurčovala expected loss, capacity ani relatívnu utility review-u.

## 1. Dominantný task-formulation lifecycle

Task type sa vyberá podľa output semantics, unit of decision, comparison setu, available targetu a downstream actionu. Algorithm sa volí až po tom, čo je jasné, čo má jeden prediction znamenať a ako sa bude hodnotiť.

```text
business decision a action capacity
→ exact sample alebo query-item subject
→ target/learning signal
→ regression / classification / ranking / clustering
→ objective a estimator generation
→ raw output
→ post-processing, threshold alebo ordering policy
→ action
→ task-specific offline evidence
→ production outcome a recovery
```

Rovnaký source dataset môže podporiť viac tasks, ale outputs nie sú zameniteľné. Probability of loss, expected loss amount, rank position a cluster assignment majú odlišné units, calibration, metrics a failure semantics.

## 2. Regression: odhad numeric quantity

Regression predikuje continuous alebo ordered numeric target. Výstup môže byť amount, duration, demand, latency, probability-like calibrated quantity alebo iná hodnota s definovanou unit. Model sa hodnotí podľa errors medzi prediction a observed targetom, ale metric musí zodpovedať business consequence.

Atlas môže regresiou odhadovať `expected_recoverable_loss_minor`:

```text
features operationu
→ regression model
→ predicted recoverable loss v eurocentoch
```

Jednoduchý interface:

```python
from sklearn.ensemble import HistGradientBoostingRegressor

regressor = HistGradientBoostingRegressor(random_state=17)
regressor.fit(X_train, y_loss_minor_train)
predicted_loss_minor = regressor.predict(X_eval)
```

Numeric output neznamená, že každý decimal má rovnakú certainty. Model môže produkovať záporné values pre inherently non-negative target, zle reagovať na heavy tails alebo podhodnotiť rare high-loss cases. Post-processing clipping môže zlepšiť valid range, ale nesmie skryť modeling failure bez evidence.

## 3. Regression target distribution a error asymmetry

Mean absolute error, mean squared error, root mean squared error alebo quantile loss penalizujú errors odlišne. MSE silnejšie zvýrazňuje veľké chyby; MAE je robustnejšia voči outliers; quantile regression môže cieliť upper alebo lower conditional quantile. Jedna aggregate metric môže zakryť cohort-specific a tail failures.

```text
actual loss:      100000 cents
prediction A:       5000 cents
prediction B:      80000 cents

obe predictions môžu mať podobný average behavior na majority,
no high-loss miss má odlišný business consequence
```

Ak review benefit závisí od pravdepodobnosti lossu aj recoverable amountu, priame regression expected loss alebo product decomposition môže byť vhodnejšie než binary class. Target musí mať unit, horizon a censoring semantics.

## 4. Classification: priradenie class alebo class probability

Classification predikuje discrete class. Binary classification rozlišuje dve classes, multiclass jednu z viacerých a multilabel môže priradiť viac labels naraz. Mnohé classifiers poskytujú decision score alebo estimated class probabilities; final class vzniká až po threshold alebo decision rule.

```text
features X
→ classifier
→ score/probability
→ threshold policy
→ class/action
```

Atlas classifier môže odhadovať probability `confirmed_loss_within_30d = 1`:

```python
from sklearn.linear_model import LogisticRegression

classifier = LogisticRegression(max_iter=1000, random_state=17)
classifier.fit(X_train, y_loss_train)
loss_probability = classifier.predict_proba(X_eval)[:, 1]
```

`predict()` často použije default decision rule, ale production action nemusí. Threshold `0.5` nemá univerzálny business význam. Pri rare events, asymmetric costs a fixed capacity môže byť nesprávny.

## 5. Score, probability, class a action sú odlišné states

Raw model score nemusí byť calibrated probability. Probability nemusí byť final class. Class nemusí byť business action. Každý transition potrebuje authority a version.

```text
raw score:             2.17
calibrated probability: 0.81
class threshold v3:     positive pri p >= 0.72
business policy:        queue iba top 2500 eligible operations
final action:           manual review
```

Ak sa threshold zmení bez retrainingu, model artifact je rovnaký, ale system behavior nie. Audit musí zaznamenať calibration a threshold generation. Dashboard „model version v4“ bez active policy verzie nevysvetlí počet actions.

## 6. Classification metrics závisia od positive class a thresholdu

Accuracy je fraction correct class predictions, ale pri imbalanced population môže byť zavádzajúca. Ak positive rate je `0,4 %`, classifier predikujúci vždy negative má `99,6 %` accuracy a nulovú schopnosť zachytiť positives.

Precision odpovedá, aký podiel predicted positives bol skutočne positive. Recall odpovedá, aký podiel actual positives model zachytil. False-positive a false-negative consequences musia byť prepojené s business actionom.

```text
predicted review
├── true positive: recoverable loss case
└── false positive: analyst capacity + customer friction

not reviewed
├── true negative
└── false negative: missed recoverable loss
```

Threshold sweep a precision-recall behavior sú užitočnejšie než jedna class metric, ale stále nepreukazujú queue-level utility alebo amount captured.

## 7. Ranking: optimalizovať relatívne poradie v context-e

Ranking task dostane context alebo query a candidate items a vytvorí ordered list. Význam prediction je relatívny: item A má byť pred B pre konkrétny query/context. Search, recommendations a priority queues sú typické use cases.

Pre Atlas je context napríklad `review_day + analyst_pool` a candidates sú eligible merchant operations. Output je ordering, z ktorého capacity policy vezme top `K`.

```text
context: review queue 2026-08-02 / EU risk team
candidates: op-1 ... op-68000
→ ranking model/policy
→ ordered list
→ top 2500 selected
```

Ranking nie je iba sort classification probability, hoci to môže byť silný baseline. Ranking objective môže priamo zohľadňovať relevance grades, list position a pairwise ordering. Evaluation sa musí viazať na list/query groups a top positions.

## 8. Pointwise, pairwise a listwise ranking

Learning-to-rank approaches sa často delia podľa training objective.

Pointwise approach spracúva každý query-item pair ako samostatnú regression alebo classification observation a potom scores zoradí. Je jednoduchý, ale objective nemusí priamo optimalizovať relative ordering.

Pairwise approach sa učí, ktorý z dvoch items má byť vyššie. Training signal sú preferences alebo odvodené pairs.

Listwise approach pracuje s celým alebo sampled listom a objective viac zodpovedá list-level ordering metric.

```text
pointwise: score(item)
pairwise:  prefer(item_a, item_b)
listwise:  optimize ordered list for context
```

TensorFlow Ranking napríklad podporuje pointwise, pairwise a listwise losses a ranking metrics ako NDCG. Výber approachu musí rešpektovať label process, candidate generation, list size a serving constraints.

## 9. Ranking relevance, gain a position discount

Ranking label nemusí byť binary. Relevance grade môže reprezentovať expected review value, severity alebo graded utility. Metrics ako NDCG zohľadňujú gain relevantných items a vyššiu hodnotu správneho poradia na top positions.

```text
operation A: confirmed recoverable loss 500 EUR → grade 3
operation B: confirmed loss 20 EUR             → grade 1
operation C: no loss                           → grade 0
```

Také grades sú business design, nie prirodzená vlastnosť dát. Musia explicitne zachytiť amount, recoverability, review cost a harm. Ak grade používa outcome po actione, môže vzniknúť selective feedback podobne ako pri classification labels.

Ranking metric sa počíta per query/list a potom agreguje. Zmiešať candidates z rôznych dní alebo analyst pools do jedného listu môže vytvoriť nereálnu evaluation.

## 10. Candidate generation a ranking stage

Produkčný ranking často nevidí všetky možné items. Predchádza mu eligibility filter alebo candidate retrieval. Kvalita rankera nemôže obnoviť relevantný item, ktorý candidate stage vyradil.

```text
all operations
→ policy eligibility
→ candidate generation
→ model scoring/ranking
→ top K
→ analyst queue
```

Acceptance musí merať candidate recall aj ranking quality. „NDCG je vysoké“ nepreukazuje, že forbidden merchant cohort nebol omylom excluded alebo že candidate set obsahuje všetky high-loss operations.

Candidate generation je často deterministic policy a vlastní compliance/authorization constraints. Ranker nesmie obísť hard exclusions ani pridať item mimo allowed population.

## 11. Capacity-constrained ranking a expected utility

Keď downstream action má limit `K`, decision boundary je top-K, nie fixed probability threshold. Atlas potrebuje optimalizovať captured value v prvých `2 500` positions pri bounded analyst time.

Jednoduchý transparentný ranking baseline môže byť:

```python
review_utility = (
    calibrated_loss_probability
    * predicted_recoverable_loss_minor
    - predicted_review_cost_minor
)
ranking = eligible_operations.sort_values(
    "review_utility", ascending=False
)
selected = ranking.head(2500)
```

Tento formula nie je automaticky správny; ukazuje, že business policy kombinuje viac model outputs a costs. Každý term potrebuje units, uncertainty a ownership. Pri capacity change sa `K` môže zmeniť bez retrainingu a vytvoriť novú policy generation.

## 12. Clustering: partition bez authoritative class targetu

Clustering je unsupervised task, ktorý groupuje samples podľa similarity alebo density. Output cluster IDs nie sú predicted business classes. Clustering môže pomôcť segmentácii, exploration, compression alebo detection nových traffic patterns.

```python
from sklearn.cluster import HDBSCAN
from sklearn.preprocessing import StandardScaler

X_scaled = StandardScaler().fit_transform(X)
cluster_ids = HDBSCAN(min_cluster_size=100).fit_predict(X_scaled)
```

Aj keď cluster koreluje s lossom, nemusí byť stabilný medzi datasets. Cluster assignment môže používať features nevhodné pre production decision alebo dimensions dominated scalingom. External profiling a validation zostávajú potrebné.

## 13. Classification class oproti clusteru

Class má intended semantic definíciu a supervised labels. Cluster vzniká z algorithm objective a representation. Premenovať cluster na class vytvára semantic skok.

```text
classification class:
confirmed_loss_within_30d ∈ {0, 1}

cluster:
group 7 podľa distance/density v feature space v4
```

Cluster `7` môže obsahovať high-value traveling merchants, nie fraudsters. Ak sa použije ako feature do supervised modelu, pipeline musí versionovať clustering artifact a handling new samples. Ak sa použije iba pre exploration, nesmie byť ticho zapojený do action policy.

## 14. Multi-task a composed systems

Jeden business workflow môže používať viac task types. Atlas môže mať classifier probability, regression loss amount, ranking queue a clustering monitoring. Correctness vyžaduje explicitný composition contract.

```text
classification: P(loss within 30d)
regression:     E(recoverable amount | operation)
ranking:        order candidates by expected review utility
clustering:     discover/monitor traffic cohorts
```

Každý artifact má vlastný training data, target/objective, metric a refresh cadence. Spoločná feature platform neznamená spoločnú model generation. Rollback jedného componentu môže vyžadovať compatibility check s downstream formula.

## 15. Baseline a formulation comparison

Pred complex modelom treba vytvoriť baseline zodpovedajúci tasku. Pre regression môže byť median alebo simple linear model. Pre classification majority/dummy alebo logistic baseline. Pre ranking sort existujúceho interpretable score alebo amount. Pre clustering random/known business segmentation nie je vždy validný baseline, ale stability a no-cluster alternative sú dôležité.

```text
business baseline
→ simple statistical/model baseline
→ candidate model
→ incremental evidence a operational cost
```

Vyššie model complexity je odôvodnená iba merateľným gainom na relevantnej metric a production constraints. Ak ranking neural model zlepšuje NDCG o malú hodnotu, ale pridáva vysokú latency a nekompatibilný feature path, business trade-off môže favorizovať jednoduchý score formula.

## 16. Wrong-task failure modes

Wrong-task formulation môže vyzerať ako algorithm failure, hoci model optimalizuje presne zadaný objective. Diagnostic otázka preto nie je iba „ktorý estimator má lepšie score“, ale „má output rovnakú unit, comparison boundary a action semantics, akú potrebuje business operation?“. Každý z nasledujúcich omylov oddeľuje training objective od downstream decisionu iným spôsobom.

- classification namiesto ranking — model môže mať high overall accuracy, ale nevytvorí správne relatívne top-K poradie pre bounded capacity;
- regression bez action horizon — numerický odhad nemá jasnú dobu platnosti ani usable decision boundary;
- clustering interpretovaný ako classes — arbitrary groups podľa feature metric sa vydávajú za authoritative business truth;
- ranking bez candidate evaluation — relevantné items chýbajú ešte pred scorerom, takže dobrá list metric hodnotí iba neúplnú population;
- probability zamieňaná so utility — high risk s nízkym recoverable amountom môže vytlačiť hodnotnejší prípad a preplniť capacity;
- hard class threshold pri variable capacity — queue size a analyst load sa menia s prevalence a score distribution bez explicitného capacity ownera.

Spoločným mechanizmom je neviditeľný post-model transition: score sa mení na inú business quantity bez versionovanej policy a task-specific evaluation. Root cause sa preto neopraví automatickým hyperparameter tuningom. Najprv sa musí zmeniť task contract, baseline a acceptance tak, aby merali rovnaký decision, aký sa skutočne vykonáva.

## 17. Worked incident `ML-PAY-83`: classification score pre ranking problém

Atlas classifier dosiahol `96,8 %` accuracy na leaked random split-e. Po oprave datasetu score prirodzene kleslo. Tím sa sústredil na návrat accuracy, ale production symptom bol inde: top `2 500` queue obsahovala veľa duplicate low-amount retries a málo high-recoverable-loss operations.

Default `predict()` threshold vytváral variable počet positives podľa traffic mixu. Queue service potom vyberala prvých `2 500` podľa event arrival time, nie model score. Model probability teda iba filtrovala a final order určovala infraštruktúrna náhoda.

```text
classifier probability
→ threshold p >= 0.5
→ > 9000 positive operations
→ queue takes first 2500 by arrival time
```

Dashboard reportoval classification accuracy, ale business potreboval operation-level ranking utility. Recovery zmenila system contract:

```text
candidate eligibility
→ operation-level calibrated probability
+ predicted recoverable amount
+ review cost policy
→ deterministic utility score
→ ordered queue
→ top 2500
```

Classification model zostal componentom, nie final task authority. Tím pridal ranking metrics per day, captured recoverable loss at K, duplicate-operation rate, candidate coverage a analyst-time outcome.

## 18. Evidence-preserving containment a recovery

Po incidente tím zachoval raw classifier scores, probabilities, active threshold, queue insertion timestamps, rank/order fields, candidate manifests a final analyst outcomes. Zastavil arrival-time ordering a vrátil sa k poslednej deterministic risk-and-amount prioritization policy.

Recovery porovnala štyri alternatives nad rovnakým operation/time holdoutom. Porovnanie nebolo zoznamom model names, ale controlled experimentom s rovnakým candidate manifestom, capacity `K`, label maturity a cost assumptions. Tým sa zabránilo tomu, aby jeden variant získal výhodu lepším data coverage alebo iným evaluation windowom.

1. Classification probability sort použil calibrated probability ako jednoduchý ranking baseline a ukázal hodnotu samotného classifieru bez ďalšej amount policy.
2. Predicted expected-loss regression zoradila operations podľa numeric recoverable-loss targetu a odhalila sensitivity na heavy-tail errors.
3. Transparent composed utility score skombinoval probability, recoverable amount a review cost cez explicitnú versionovanú formulu, ktorú vedel risk owner auditovať.
4. Learned ranking model optimalizoval relatívne list order a musel preukázať incremental gain oproti transparentným baselines.

Každý variant dostal rovnaký candidate set a capacity `K`. Evaluation oddelila model metric od business metric, serving latency, operational complexity a recovery cost. Learned ranker nebol promoted iba preto, že mal najlepší offline NDCG; musel prejsť shadow queue, stability a cohort checks a mať schválený fallback na jednoduchšiu ordering policy.

## 19. Task-specific acceptance contract

Regression positive acceptance preukazuje unit/horizon targetu, error distribution, tail/cohort behavior a downstream interpretation. Forbidden je ticho používať out-of-range prediction alebo aggregate metric bez high-cost cohorts.

Classification positive acceptance preukazuje class semantics, score/probability calibration, threshold generation a action consequences. Forbidden je zamieňať score s probability, probability s class alebo class s business authority.

Ranking positive acceptance preukazuje query/context groups, candidate coverage, relevance/utility contract, top-K metrics a stable ordering/fallback. Forbidden je hodnotiť global rows bez list contextu alebo nechať implicitný arrival order rozhodovať ties a capacity.

Clustering positive acceptance preukazuje representation, metric/objective, stability a external interpretation. Forbidden je používať cluster ID ako authoritative class bez validation.

```text
positive ranking:
complete eligible candidates
→ pinned scores/policy
→ deterministic ordered list
→ top K
→ measured business outcome

recovery:
learned ranker unavailable
→ approved baseline ordering
→ preserved candidate/action audit

forbidden:
classification accuracy closes ranking acceptance
cluster number becomes fraud label
threshold changes without policy generation
candidate exclusion remains invisible
```

Second-operation test musí použiť nový context/list s novými operations, overiť deterministic tie policy, no duplicates, capacity `K`, fallback a complete audit lineage.

## Kontrolné otázky

1. Akú otázku rieši regression a akú classification?
2. Prečo numeric regression output potrebuje unit a horizon?
3. Ako metric mení regression objective a business trade-off?
4. Aký je rozdiel medzi raw score, probability, class a action?
5. Prečo default threshold `0.5` nemá univerzálny význam?
6. Ako imbalanced population zavádza accuracy?
7. Čo je ranking context/query a candidate list?
8. Ako sa pointwise, pairwise a listwise ranking líšia?
9. Čo preukazuje NDCG a čo nepreukazuje?
10. Prečo candidate generation patrí do ranking acceptance?
11. Ako fixed capacity mení classification problém na ranking decision?
12. Prečo cluster ID nie je class label?
13. Ako možno bezpečne skombinovať classification, regression, ranking a clustering?
14. Prečo hyperparameter tuning neopraví wrong-task formulation?
15. Ako arrival-time ordering znehodnotil classifier v `ML-PAY-83`?
16. Aké task-specific positive, recovery, forbidden a second-operation testy treba vykonať?

## Glossary impact

Relevantné pojmy: regression, numeric target, classification, binary/multiclass/multilabel classification, raw score, class probability, calibration, decision threshold, precision, recall, ranking, query/context, candidate set, learning to rank, pointwise/pairwise/listwise objective, relevance grade, NDCG, top-K, candidate recall, expected utility, clustering, cluster assignment, composed model system, task formulation a task-specific acceptance contract.

## Primárne zdroje

- [scikit-learn — Supervised learning](https://scikit-learn.org/stable/supervised_learning.html)
- [scikit-learn — Metrics and scoring](https://scikit-learn.org/stable/modules/model_evaluation.html)
- [scikit-learn — Tuning the decision threshold for class prediction](https://scikit-learn.org/stable/modules/classification_threshold.html)
- [scikit-learn — Clustering](https://scikit-learn.org/stable/modules/clustering.html)
- [TensorFlow Ranking](https://www.tensorflow.org/ranking)
- [TensorFlow Ranking — Overview](https://www.tensorflow.org/ranking/overview)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Supervised, unsupervised a reinforcement learning](supervised-unsupervised-reinforcement-learning.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
