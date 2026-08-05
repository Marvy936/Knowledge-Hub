# Runtime evidence contract

Machine Learning Fundamentals flagship lab oddeľuje source review, lokálne execution evidence a authoritative repository runtime evidence.

## Pull request gate

Zmena pod `labs/machine-learning/`, Section 18 README alebo future implementation inventory spustí štandardný `pull_request` workflow. Tento gate vykoná päť unit/integrity testov, positive generate → validate → train → infer lifecycle, negative leakage path, manifest acceptance a cleanup.

Úspešný pull-request run preukazuje iba správanie presného testovacieho merge subjectu na GitHub-hosted Python 3.12 runneri. Nie je dôkazom, že rovnaký commit už existuje na `main`.

## Main gate

Po merge sa workflow zopakuje na exact `main` commit SHA. Samostatný no-checkout reporter zapíše connector-readable commit statuses:

- `knowledge-hub/ml-flagship-runtime` — celkový výsledok testov a lifecycle-u,
- `knowledge-hub/ml-metrics` — selected model, threshold, test F1 a recall,
- `knowledge-hub/ml-dataset-sha256` — SHA-256 deterministického datasetu,
- `knowledge-hub/ml-model-sha256` — SHA-256 packaged modelu,
- `knowledge-hub/ml-runtime-versions` — presné Python a library versions.

Každý status odkazuje na authoritative workflow run. Status success neznamená reálnu production data quality, train-serving consistency, business impact ani production readiness; preukazuje iba deklarovaný syntetický lab contract.

## Closure rule

Praktická vrstva Section 18 sa v implementation inventory označí ako vykonaná až vtedy, keď:

1. pull-request runtime gate je zelený,
2. merge commit má úspešný `knowledge-hub/ml-flagship-runtime` status,
3. metrics a hashes sú dostupné na rovnakom commit SHA,
4. dokumentácia zachováva production proof boundary.
