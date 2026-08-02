# Machine Learning Fundamentals

Sekcia vysvetľuje machine learning z pohľadu DevOps, platform a operations roly. Cieľom nie je nahradiť matematický alebo data-science odbor, ale presne rozumieť tomu, aký dataset, feature contract, model artifact a evaluation verdict vzniká, čo daný dôkaz preukazuje a prečo sa offline úspech nemusí preniesť do produkčného outcome-u.

## Predpoklady

Odporúčané predchádzajúce oblasti:

- Testing and Software Quality
- Databases and Distributed Systems
- Observability
- Security and Identity

## Plánované authoritative poradie

Nasledujúci inventory je schválený plán sekcie. Položka sa zmení na aktívny Markdown link až v pracovnom bloku, ktorý vytvorí a validuje príslušnú kapitolu. Tým sa plánovaný obsah nezamieňa za hotovú dokumentáciu.

1. [Artificial intelligence, machine learning, deep learning a generative AI](artificial-intelligence-machine-learning-deep-learning-generative-ai.md)
2. [Dataset, sample, feature, label a target](dataset-sample-feature-label-target.md)
3. [Supervised, unsupervised a reinforcement learning](supervised-unsupervised-reinforcement-learning.md)
4. [Regression, classification, ranking a clustering](regression-classification-ranking-clustering.md)
5. [Train, validation a test split](train-validation-test-split.md)
6. [Data preprocessing, normalization a encoding](data-preprocessing-normalization-encoding.md)
7. [Feature engineering a feature selection](feature-engineering-feature-selection.md)
8. [Data leakage a train-serving skew](data-leakage-train-serving-skew.md)
9. [Linear a logistic regression](linear-logistic-regression.md)
10. [Decision trees, random forests a gradient boosting](decision-trees-random-forests-gradient-boosting.md)
11. [Neural network fundamentals](neural-network-fundamentals.md)
12. [Loss functions a optimization](loss-functions-optimization.md)
13. Gradient descent, learning rate a convergence
14. Overfitting, underfitting, bias a variance
15. Regularization a early stopping
16. Hyperparameters a hyperparameter optimization
17. Classification metrics
18. Regression metrics
19. Imbalanced datasets a threshold selection
20. Cross-validation
21. Calibration a uncertainty
22. Explainability a feature importance
23. Data quality, bias a responsible AI
24. Reproducibility a random seeds
25. Offline evaluation oproti production outcome
26. ML troubleshooting mental model

## Authoring a evidence štandard

Každá kapitola bude používať rovnaký prose-first štandard ako sekcie 00–17:

```text
business alebo user outcome
→ exact data/model/prompt/agent subject a generation
→ authority, trust a ownership boundary
→ internal lifecycle alebo mutation path
→ authoritative read-back a proof boundary
→ failure a competing hypotheses
→ containment a recovery
→ positive, forbidden a second-operation acceptance
```

Rýchlo sa meniace produkty, API a protokoly sa pri každom bloku znovu overia proti aktuálnym primárnym zdrojom. Dokumentácia nesmie zamieňať offline eval, control-plane status alebo úspešný tool call za produkčný business outcome.

## Praktická vrstva

Nosný end-to-end smer sekcie:

```text
raw dataset → validation a preprocessing → baseline model → train/validation/test evaluation → experiment comparison → packaged inference artifact
```

Samostatné laby a troubleshooting drilly sa aktivujú až po dostatočnom koncepčnom základe. Dokumentačný workflow môže overiť súbory, príkazy a konzistenciu modelu, ale nepreukazuje vykonanie tréningu, inference, agentického side effectu ani produkčného outcome-u.

## Stav

Aktuálny authoritative stav sekcie je **12/26 · In progress**. Tretí blok uzatvára linear/logistic model form, tree ensembles, neural architecture a loss/optimizer lifecycle. Kapitoly 13–26 zostávajú plánovaným inventorym a nesmú sa interpretovať ako hotová dokumentácia. Po tejto sekcii nasleduje **MLOps and ML Platforms**.
