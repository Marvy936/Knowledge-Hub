# Machine Learning Fundamentals flagship runtime evidence

Tento dokument je immutable evidence summary pre syntetický end-to-end lab sekcie 18. Oddeľuje presný vykonaný subject, resolved runtime, test a model evidence, cleanup a hranicu toho, čo run nepreukazuje.

## Authoritative execution subject

Runtime gate bol vykonaný v existujúcom a preukázateľne aktívnom workflowe `Knowledge documentation`:

- workflow run: **1998**
- GitHub run ID: `31037119011`
- job ID: `92411983199`
- runner: self-hosted `MARVY`
- pull-request test merge subject: `0e434e9cfa68173f3e3b76a61b93d08201474c81`
- feature revision, z ktorej vznikol test merge subject: `6b325080307c594ff74c1ca97273e6bb15431967`
- inventory closeout commit vytvorený po úspechu: `07cfe2a883b901b40e7e0d266a00ff9a3fd12d4f`

Gate použil dočasný branch-scoped import hook iba na vetve `agent/ml-runtime-evidence-contract`. Po úspešnom runtime a inventory update sa hook sám odstránil; výsledný branch už neobsahuje `scripts/argparse.py`. Samostatný nový workflow, ktorý nevytvoril pozorovateľný run, bol takisto odstránený namiesto toho, aby bol prezentovaný ako overený gate.

## Resolved runtime

Izolovaný virtual environment bol vytvorený znovu v runner temp priestore:

```text
Python        3.12.13
pip           26.2.1
NumPy         2.4.6
pandas        3.0.5
scikit-learn  1.9.0
joblib        1.5.3
pytest        9.1.1
```

NumPy contract bol po prvom úspešnom rune zúžený na `>=2.3,<2.5`. Dôvodom bolo osem `joblib` deprecation warningov pri NumPy `2.5.1`. Finálny run spustil pytest s `DeprecationWarning` povýšeným na error a skončil:

```text
5 passed in 7.99s
```

Tým sa preukázalo, že finálny dependency resolution už uvedený compatibility warning nevytvára.

## Dataset evidence

Generátor vytvoril presne 1 200 rows so seedom `20260805`:

```text
class 0:          896
class 1:          304
positive fraction: 0.253333
```

Missingness bola `0.02` pre `monthly_spend_eur`, `days_since_last_login` a `region`; ostatné feature columns mali `0.0`. Dataset prešiel schema, identity, class-support, range, category a missingness validáciou.

```text
dataset SHA-256:
08e795494731fa4c22f566769549240bf05413a918e34f9b0323091aa79cc3d6
```

Rovnaký hash vznikol aj v predchádzajúcom izolovanom rune, čo potvrdilo byte-level reprodukovateľnosť pre rovnaký seed, row count a source generation.

## Experiment a model selection evidence

Gate fitol preprocessing iba na train subsete a na validation sete porovnal dummy baseline, logistic regression a random forest. Vybraný candidate:

```text
selected model:      logistic_regression
decision threshold:  0.72
```

Validation evidence:

```text
accuracy:   0.837500
precision:  0.703704
recall:     0.622951
F1:         0.660870
ROC AUC:    0.854382
confusion:  [[163, 16], [23, 38]]
```

Jednorazový test-set verdict:

```text
accuracy:   0.829167
precision:  0.700000
recall:     0.573770
F1:         0.630631
ROC AUC:    0.843209
confusion:  [[164, 15], [26, 35]]
```

Test F1 prešiel gate `>=0.55`, test recall prešiel gate `>=0.55`, selected validation F1 prekonal dummy baseline a validation threshold splnil požadovaný recall gate.

Packaged model identity:

```text
model SHA-256:
34de60e4a5254a98b262abead6ccbca9b09a0c5c549328f37e88c6f21b7b19e9
```

## Inference evidence

Strict sample request prešiel feature-contract, manifest-schema, artifact-type, model-checksum a exact-runtime-version kontrolou pred deserializáciou modelu.

```text
probability:  0.977716
prediction:   1
threshold:    0.72
model:        logistic_regression
```

Inference read-back obsahoval rovnaký dataset a model SHA-256 ako training manifest.

## Negative a forbidden paths

Dataset doplnený o post-outcome field `future_refund_30d` bol odmietnutý ako známy leakage field aj ako neočakávaná schema zmena.

```text
negative leakage exit code: 2
```

Tamper test v unit suite zmenil `model.joblib` a loader ho odmietol na checksum boundary ešte pred `joblib.load()`. Unit suite zároveň overila byte-reproducible dataset, non-numeric feature refusal a kompletný package/inference lifecycle.

## Cleanup evidence

Po positive aj negative paths sa odstránil runtime dataset, model artifact a celý izolovaný virtual environment:

```text
runtime_exists: false
venv_exists:    false
```

Temporary hook bol v closeout commite odstránený a nie je súčasťou výsledného repository state-u.

## Proof boundary

Run 1998 preukazuje, že presný pull-request test merge subject vykonal deklarovaný syntetický Section 18 lifecycle na uvedenom runneri a resolved dependency sete. Preukazuje dataset contract, leakage refusal, model comparison, threshold selection, acceptance gates, artifact integrity, strict inference a cleanup.

Run nepreukazuje kvalitu alebo reprezentatívnosť reálneho datasetu, production train-serving consistency, calibration po drifte, causal business impact, fairness v reálnych kohortách, bezpečnosť nedôveryhodného pickle artifactu ani production readiness. Tieto tvrdenia vyžadujú samostatné datasety, environmenty, rollout a business acceptance evidence.
