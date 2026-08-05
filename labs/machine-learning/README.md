# Machine Learning Fundamentals flagship lab

Tento lab implementuje praktický lifecycle sekcie 18 ako jeden lokálny, reprodukovateľný classification workflow:

```text
raw dataset
→ schema, range a leakage validation
→ split pred preprocessingom
→ dummy baseline + logistic regression + random forest
→ threshold selection iba na validation sete
→ jednorazové test-set evaluation
→ acceptance gate
→ checksum-bound model artifact + manifest
→ strict local inference
```

Scenár predikuje, či zákazník odíde v nasledujúcich 30 dňoch. Dataset je syntetický a deterministický; lab nepotrebuje cloud, externé API ani sťahovanie produkčných dát. Cieľom nie je dosiahnuť maximálne skóre, ale preukázať správne boundaries medzi datasetom, splitom, preprocessing fitom, experimentom, evaluation verdictom a inference artifactom.

## Čo sa vykonáva

`generate-data` vytvorí stabilný CSV dataset z explicitného seedu. Identita `customer_id` sa nepoužíva ako feature. Target `churned_next_30d` vzniká pred zámerne vloženou feature missingness, takže validator môže rozlíšiť prípustné chýbajúce vstupy od chýbajúceho labelu.

`validate-data` odmietne chýbajúce alebo neočakávané columns, duplicate identities, nebinárny target, nedostatočnú podporu tried, hodnoty mimo kontraktu, neznáme kategórie, nadmernú missingness a známe post-outcome leakage fields. Validator nepreukazuje, že dáta reprezentujú budúcu produkciu; preukazuje iba splnenie deklarovaného lokálneho dataset contractu.

`train` najprv vytvorí stratified train/validation/test split. Imputation, scaling a one-hot encoding sú súčasťou každého scikit-learn `Pipeline`, preto sa ich state učí iba z train subsetu. Dummy model vytvára minimálnu baseline. Logistic regression a random forest sú porovnané na validation sete. Decision threshold sa vyberie na validation sete s recall gate; test set sa použije iba raz pre finálny acceptance verdict.

Po úspechu vznikne:

```text
artifact/
├── model.joblib
├── manifest.json
└── evaluation.json
```

Manifest viaže artifact na dataset SHA-256, seed, split sizes, model a threshold, validation/test metrics, source revision a presné runtime library versions. Inference pred deserializáciou overí checksum a odmietne version mismatch.

## Bezpečnostná hranica model artifactu

`joblib` používa pickle semantics. Checksum odhalí poškodenie alebo neautorizovanú zmenu model file, ale nezmení nedôveryhodný pickle na bezpečný obsah. `model.joblib` sa smie načítať iba z dôveryhodného lokálneho training runu alebo kontrolovaného artifact store. Cudzí artifact sa nenačítava ani vtedy, keď má vlastný manifest.

## Spustenie

Z koreňa repozitára:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e "labs/machine-learning[dev]"

python -m ml_lab generate-data \
  --output labs/machine-learning/.runtime/data/customers.csv \
  --rows 1200 \
  --seed 20260805

python -m ml_lab validate-data \
  --input labs/machine-learning/.runtime/data/customers.csv

python -m ml_lab train \
  --input labs/machine-learning/.runtime/data/customers.csv \
  --output-dir labs/machine-learning/.runtime/artifact \
  --seed 20260805

python -m ml_lab infer \
  --artifact-dir labs/machine-learning/.runtime/artifact \
  --input labs/machine-learning/data/sample-request.json

pytest labs/machine-learning/tests -q
```

V PowerShelli sa virtual environment aktivuje cez:

```powershell
.venv\Scripts\Activate.ps1
```

Ostatné Python príkazy ostávajú rovnaké.

## Očakávaný dôkaz

Úspešný training command vypíše `accepted_and_packaged`, selected model, threshold, validation metrics, test metrics a model SHA-256. Úspešný inference command vypíše probability, binary prediction, použitý threshold a hashes modelu aj datasetu.

Presné metriky sú viazané na dependency versions zaznamenané v manifeste. Očakávané invarianty sú:

- selected model nie je dummy baseline,
- test F1 je aspoň `0.55`,
- test recall je aspoň `0.55`,
- model checksum pred inference sedí,
- runtime versions sa presne zhodujú s training environmentom,
- rovnaký seed a row count vytvoria byte-identický CSV dataset.

## Failure paths

Validator musí odmietnuť napríklad `future_refund_30d`, pretože vzniká až po predikovanom outcome-e. Training musí odmietnuť neúmyselné prepísanie existujúceho artifact directory bez `--overwrite`. Inference musí odmietnuť chýbajúce alebo extra fields, tampered model file a artifact vytvorený inou verziou runtime dependencies.

Zelený CI run preukazuje, že tento syntetický workflow prebehol na deklarovanom runneri. Nepreukazuje kvalitu reálneho customer datasetu, produkčný train-serving contract, calibration pod reálnym driftom, business impact ani production readiness.

## Cleanup

Runtime output je zámerne mimo Git history:

```bash
rm -rf labs/machine-learning/.runtime
```

PowerShell:

```powershell
Remove-Item -Recurse -Force labs/machine-learning/.runtime
```

Cleanup je dokončený až vtedy, keď `.runtime` neexistuje. Zdrojový kód, tests a sample request zostávajú nezmenené.
