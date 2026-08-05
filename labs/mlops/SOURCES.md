# Primárne technické zdroje

Overené 5. augusta 2026 proti oficiálnej MLflow dokumentácii:

- [Tracking experiments with a local database](https://mlflow.org/docs/latest/ml/tracking/tutorials/local-database) — SQLite tracking backend pre izolovaný lokálny workflow.
- [MLflow Model Registry](https://mlflow.org/docs/latest/ml/model-registry/) — registered models, versions, lineage, tags a aliases.
- [Model Registry workflows](https://mlflow.org/docs/latest/ml/model-registry/workflow/) — API promotion, `set_registered_model_alias` a alias read-back.
- [MLflow scikit-learn API](https://mlflow.org/docs/latest/api_reference/python_api/mlflow.sklearn.html) — model logging, signatures, input examples, `predict_proba` pyfunc contract a `skops` serialization.
- [Model signatures and input examples](https://mlflow.org/docs/latest/ml/model/signatures/) — explicit inference schema a example validation.
- [MLflow model serving](https://mlflow.org/docs/latest/ml/deployment/) — MLflow Model packaging, container boundary a standardized inference serving.
- [MLflow 3 migration guide](https://mlflow.org/docs/latest/genai/mlflow-3) — MLflow 3 model IDs a model URI behavior.
- [MLflow 3.14.0 release](https://mlflow.org/releases/3.14.0/) — pinned platform generation použitá týmto labom.

Zdrojová dokumentácia podporuje API a architektonický contract. Výsledok konkrétneho experimentu, registry mutation, serving requestu, drift gate-u alebo rollbacku preukáže až runtime evidence viazané na presný workspace a commit.
