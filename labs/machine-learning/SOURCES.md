# Primárne technické zdroje

Lab používa stabilné scikit-learn abstractions a bezpečnostné hranice overené 5. augusta 2026 proti oficiálnej dokumentácii.

- [Common pitfalls and recommended practices](https://scikit-learn.org/stable/common_pitfalls.html) — preprocessing sa učí iba z training dát; `Pipeline` znižuje riziko inconsistent preprocessing a data leakage.
- [Pipelines and composite estimators](https://scikit-learn.org/stable/modules/compose.html) — `Pipeline` a `ColumnTransformer` viažu preprocessing a estimator do jedného fit/predict contractu.
- [Model persistence](https://scikit-learn.org/stable/model_persistence.html) — pickle/joblib artifact sa načítava iba z dôveryhodného zdroja a training/serving dependency versions majú byť zhodné.
- [Classification metrics](https://scikit-learn.org/stable/modules/model_evaluation.html#classification-metrics) — precision, recall, F1, ROC AUC a confusion matrix merajú odlišné vlastnosti classifiera.
- [Train/test split](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html) — stratified deterministic split potrebuje explicitný `random_state` a target pre `stratify`.

Tieto zdroje podporujú implementačný mechanizmus, ale nepreukazujú výsledok konkrétneho runu. Runtime evidence vzniká až vykonaním testov, training lifecycle-u, negative pathov a artifact read-backu v dedikovanom workflowe.
