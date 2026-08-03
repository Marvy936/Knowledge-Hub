# Model packaging a reproducible environments

Model packaging premieňa training output na explicitný inference artifact s definovaným interfaceom, dependencies, code a load semantics. Samotný weights file spravidla nestačí. Produkčný consumer potrebuje preprocessing, feature order, serialization format, runtime libraries, custom code, input/output schema a často aj native alebo accelerator dependencies. Reproducible environment znamená, že tieto vstupy možno znovu zostaviť alebo načítať s predvídateľným behaviorom; neznamená iba zoznam troch top-level Python packages.

V incidente `MLOPS-PAY-91` Atlas opravil partial artifact upload, no nový model stále zlyhával iba v production image. Training notebook mal `scikit-learn` importovaný z environmentu s novšou minor version, zatiaľ čo automaticky inferred `requirements.txt` zachytil neúplný dependency set. Custom transformer bol definovaný v notebook `__main__` scope a serializovaný cez cloudpickle. Na jednom hoste sa načítal vďaka leftover source fileu, na clean containeri chýbal. Model bytes boli durable, ale package nebol prenosný.

## 1. Dominantný packaging lifecycle

Packaging začína exact trained artifactom a končí až validated deployable unitom. Export alebo conversion je nová operation, ktorá môže zmeniť numeriku aj interface. Build containeru je ďalšia generation. Každý krok potrebuje lineage, digest a parity evidence.

```text
trained checkpoint alebo fitted object
→ explicit preprocessing a inference contract
→ serialization/export operation
→ model package + code + environment metadata
→ package integrity a load test
→ optional conversion/optimization
→ container alebo serving bundle build
→ clean-environment inference parity
→ signed immutable release artifact
```

Training environment nie je automaticky správny serving environment. Obsahuje kompilátory, notebooks, test tools a credentials, ktoré inference nepotrebuje. Serving package má byť minimálny, no musí obsahovať všetko potrebné pre load a predict. Minimalizácia bez complete dependency discovery vytvára runtime failure; kopírovanie celého training image zvyšuje attack surface a size.

## 2. Exact model package subject

Package subject zahŕňa model bytes, format, flavors alebo loaders, input/output signature, preprocessing, code dependencies, environment manifests a artifact digest. Container image je samostatný subject, ktorý package embeduje alebo z neho model načíta.

```yaml
package_id: payment-risk-mlflow-sha256:b8ae...7d22
source_run_id: 6f7b8fa3b5ad4aaead859f1a5d771301
source_checkpoint_digest: sha256:9c11...a087
format: mlflow-model
flavors:
  - sklearn
  - python_function
signature: risk-inference-v6
input_schema:
  - name: amount_eur
    type: double
    required: true
  - name: merchant_velocity_7d
    type: double
    required: false
output_schema:
  - name: confirmed_loss_probability
    type: double
code_digest: sha256:18aa...b900
requirements_digest: sha256:e21a...1b40
python_version: 3.12.4
artifact_manifest_digest: sha256:b8ae...7d22
serving_image: registry.example/risk-serving@sha256:80cd...7810
```

Model name a Registry version nie sú package identity. Alias sa môže presunúť a Registry version je record. Digest identifikuje exact package bytes. Signature identifikuje expected logical interface, no consumer stále musí validate actual request.

## 3. MLflow Model format a flavors

MLflow Model je directory s root súborom `MLmodel` a arbitrary ďalšími files. `MLmodel` opisuje jeden alebo viac flavors. Framework-specific flavor môže načítať model cez pôvodnú knižnicu; `python_function` flavor poskytuje spoločný `predict()` interface pre deployment tools.

```text
model/
├── MLmodel
├── model.pkl
├── python_env.yaml
├── requirements.txt
├── conda.yaml
└── input_example.json
```

Flavor je loader contract, nie automatická portability guarantee. PyFunc wrapper umožní jednotné volanie, ale custom Python code, native libraries a external artifacts stále musia byť dostupné. Consumer musí vedieť, ktorý flavor použil; framework-specific a PyFunc inference môžu mať odlišné preprocessing alebo return-type behavior.

`MLmodel` metadata a package files tvoria jeden versionovaný celok. Manuálna editácia requirements po vytvorení modelu mení package generation a vyžaduje nový digest aj validation. Registry record sa nemá potichu prepojiť na upravený directory.

## 4. Serialization a code boundary

Pickle a cloudpickle zachytávajú Python object graph, nie celý OS a package environment. Cloudpickle vie serializovať lokálne funkcie alebo triedy, ale external files, database connections, dynamic libraries a neimportované runtime dependencies nemusia byť zahrnuté. Deserializácia môže vykonať code, preto package musí pochádzať z dôveryhodného build pathu.

Custom transformer definovaný v notebooku môže fungovať pri immediate load-e v tom istom process-e a zlyhať v clean worker-i. Bezpečnejší pattern presunie implementation do versionovaného module/package, zahrnie ho cez package dependency alebo explicitný `code_paths` a vykoná clean-process load test.

```python
import mlflow.sklearn

mlflow.sklearn.log_model(
    sk_model=pipeline,
    name="model",
    input_example=input_example,
    signature=signature,
    pip_requirements="requirements.lock.txt",
)
```

Example ukazuje explicitnú signature, input example a requirements. Nezaručuje, že lockfile obsahuje OS libraries alebo že model je bezpečný na deserializáciu z nedôveryhodného source.

## 5. Dependency inference oproti dependency locking

MLflow vie pri logovaní modelu inferovať Python dependencies a zapisuje environment files ako `requirements.txt`, `python_env.yaml` a `conda.yaml`. Inference je užitočný baseline, ale závisí od executed/imported code paths. Optional alebo lazy dependency použitá až pri rare requeste sa nemusí objaviť.

Exact direct versions stále nemusia lockovať transitive graph. Aktuálny MLflow podporuje dependency locking cez `MLFLOW_LOCK_MODEL_DEPENDENCIES=true`; ak je dostupné `uv`, môže resolve-nuť a pinovať transitive dependencies. MLflow tiež vie pracovať s existujúcim `uv.lock` projectom. Tieto mechanizmy majú rozdielnu semantiku: on-the-fly resolution nemusí reprodukovať exact už nainštalované versions, zatiaľ čo existing lockfile vyjadruje project resolution.

```bash
export MLFLOW_LOCK_MODEL_DEPENDENCIES=true
python train_and_log.py
```

Lockfile zvyšuje reproducibility Python graphu, ale nezachytáva kernel, glibc, system packages, CPU instructions, CUDA driver ani remote service behavior. Complete environment identity preto kombinuje model package, container image digest a runtime/hardware contract.

## 6. Input example, signature a schema enforcement

Input example pomáha dependency inference a dokumentuje shape. Model signature opisuje expected columns/types a outputs. Signature validation zachytí missing columns alebo incompatible types pred model code pathom, ale nepreukazuje semantic correctness. `amount_eur` s hodnotou v centoch môže typovo prejsť.

Feature order je kritický pri array-based interfaces. DataFrame signature s named columns znižuje riziko, no preprocessing musí explicitne mapovať names. Optional fields, null semantics, timezone, encoding, tensor shape a batch dimension patria do interface contractu.

Schema evolution potrebuje compatibility policy. Additive optional field môže byť backward-compatible. Rename alebo zmena units je breaking. Model serving release má odmietnuť incompatible producer schema, nie silently reorder alebo fill values bez auditovateľnej fallback policy.

## 7. Preprocessing a post-processing v package

Train-serving skew často vzniká tým, že training pipeline používa fitted scaler, encoder alebo feature selection, kým serving implementuje transformáciu osobitne. Najsilnejší pattern package-uje preprocessing spolu s estimatorom, napríklad ako scikit-learn `Pipeline`, alebo ho viaže na versionovaný feature contract.

Post-processing, calibration a threshold sú odlišné. Calibration môže byť súčasť model package, ak je fitted artifact. Business threshold alebo top-K capacity policy často patrí mimo model, pretože sa mení nezávisle. Package manifest musí ukázať boundary, aby Registry promotion modelu nepredstierala promotion policy.

## 8. Reproducible environment layers

Reproducibility má viac vrstiev:

```text
language environment:
Python + packages + wheels

system environment:
OS image + native libraries + locale + timezone

accelerator environment:
CUDA/ROCm + drivers + architecture + precision capabilities

execution configuration:
threads + environment variables + model_config + resource limits

external dependencies:
feature service + tokenizer files + lookup tables + remote endpoints
```

Container image digest dobre zachytí language a system user-space, nie host kernel/driver ani external service state. GPU image môže byť kompatibilný iba s určitým driver range. CPU model môže meniť performance podľa BLAS implementation a thread count.

Environment record preto uvádza compatibility requirements a loaded runtime evidence. „Built successfully“ nepreukazuje, že image beží na target node alebo že rare code path načíta native library.

## 9. Container packaging

MLflow vie buildovať Docker image pre model pomocou `mlflow models build-docker` alebo API. Container štandardizuje server process a dependencies. Produkčný build má byť reproducible: pinned base image digest, deterministic dependency install, immutable model package digest, non-root runtime, SBOM, signature a vulnerability policy.

```dockerfile
FROM python:3.12-slim@sha256:<base-digest>

COPY requirements.lock.txt /tmp/requirements.lock.txt
RUN pip install --require-hashes -r /tmp/requirements.lock.txt

COPY model/ /opt/model/
COPY service/ /opt/service/

USER 65532
ENTRYPOINT ["python", "-m", "service"]
```

`--require-hashes` vyžaduje lock s package hashes a chráni resolution integrity. Dockerfile stále potrebuje multi-platform strategy a system-package pinning. Ak sa model sťahuje pri štarte namiesto embedovania, image digest neidentifikuje loaded model; deployment subject musí obsahovať oboje a init/load read-back.

## 10. Embedovaný oproti remote-loaded modelu

Embedovaný model vytvára jeden OCI image digest pre code, dependencies a model. Rollout a rollback sú jednoduché, ale každý model update rebuildne veľký image. Remote-loaded pattern používa generic serving image a exact model URI/digest. Znižuje rebuilds, ale pridáva startup network, credentials, cache a two-artifact compatibility.

Hybridný pattern môže prebuildovať environment image a model mountovať immutable. Bez ohľadu na pattern sa musí loaded model digest reportovať. Registry alias resolution pri každom štarte bez pinning-u je nebezpečná: dva Pody rovnakej deployment generation môžu načítať rôzne model versions, ak sa alias medzi štartmi presunie.

## 11. Export a optimized runtime

ONNX, TorchScript, TensorRT alebo quantized artifact nie je iba „rovnaký model v inom obale“. Export môže meniť supported operations, precision, dynamic shapes a numeriku. Vzniká nový derived artifact s vlastným digestom, environmentom a parity testom.

```text
source model digest A
→ export run E
→ ONNX digest B
→ quantization run Q
→ optimized digest C
→ serving image digest I
```

Production Registry alebo release musí ukazovať na C, nie iba na A. Evaluation nad A sa nedá automaticky preniesť na C. Parity používa representative a adversarial inputs, output tolerance, latency a resource evidence.

## 12. Supply-chain a serialization security

Model package je software supply-chain artifact. Môže obsahovať executable code, templates, native libraries alebo tokenizer files. Build pipeline overuje source, dependencies, licenses, vulnerabilities, SBOM a provenance. Signature sa viaže na package alebo OCI digest.

Pickle-based package sa načíta iba v sandboxed/controlled runtime z approved producer identity. Malware scan nie je úplná ochrana pred logic bombou v serialized objecte. Preferovaný bezpečný format závisí od frameworku a threat modelu; „portable“ neznamená „safe“.

External dependency download pri model load-e musí byť pinovaný a ideally prefetchovaný v build phase. Runtime internet access môže zmeniť artifact po promotion alebo umožniť exfiltráciu.

## 13. Failure walkthrough incidentu MLOPS-PAY-91

Po oprave artifact durability Atlas vytvoril clean Pod a dostal `ModuleNotFoundError` pre custom transformer. Pôvodný smoke test bežal na training worker-i, kde repository checkout zostal na `PYTHONPATH`. Package mal cloudpickle object, ale neobsahoval definujúci module ani pinned project wheel.

Druhá hypotéza bola scikit-learn compatibility. Dependency diff ukázal minor mismatch, no po inštalácii správnej version zlyhanie zostalo. Prvá divergence bola code availability. Tím vytvoril versionovaný Python wheel, pridal ho do lockfile, znovu package-oval model a použil fresh container bez repository mountu.

Nový package dostal nový digest a Registry version. Starý package sa neopravoval in-place. Parity test overil named input schema, missing optional feature aj batch behavior. Rare path test aktivoval custom transformer a odhalil ďalšiu lazy dependency ešte pred rolloutom.

## 14. Recovery a acceptance

Component recovery načíta package v clean environment-e a overí dependencies, signature a model interface. Journey recovery pošle representative request cez actual serving server vrátane preprocessing a post-processing. Business recovery porovná outputs a downstream actions s approved model/policy evidence.

Positive test buildne environment bez local cache a vykoná inference. Forbidden test odmietne mutable base tag, unpinned model URI, missing signature alebo package s custom code mimo approved source. Compatibility test spustí supported CPU/GPU targets. Negative schema test odmietne wrong units/type/shape. Second-build test overí, či rovnaké inputs vytvoria rovnaký image/package digest alebo vysvetlenú reproducible variation.

```bash
mlflow models build-docker \
  --model-uri "models:/prod.risk.payment@candidate" \
  --name "registry.example/risk-serving:${GIT_SHA}"

docker run --rm \
  -v "$PWD/tests:/tests:ro" \
  "registry.example/risk-serving@sha256:<digest>" \
  python /tests/parity.py
```

Alias v prvom commande je pohodlný control-plane reference, ale build record musí uložiť resolved model version a package digest. Druhý command preukazuje isolated container execution pre test, nie produkčný feature alebo business outcome.

## 15. Kontrolné otázky

1. Prečo weights file nie je kompletný model package?
2. Aké hranice má automatic dependency inference?
3. Čo container image digest nezachytáva z runtime environmentu?
4. Prečo export alebo quantization vytvára nový model subject?
5. Kedy je Registry alias nebezpečný pri remote model loading-u?

## 16. Primárne zdroje

- [MLflow Models](https://mlflow.org/docs/latest/ml/model)
- [Managing Dependencies in MLflow Models](https://mlflow.org/docs/latest/ml/model/dependencies/)
- [MLflow PyFunc API](https://mlflow.org/docs/latest/api_reference/python_api/mlflow.pyfunc.html)
- [MLflow Model Serving](https://mlflow.org/docs/latest/deployment/)

Reproducible package je necessary bridge medzi experimentom a serving-om. Produkčný verdict však vznikne až po loaded digest, request parity, policy/action a mature outcome evidence.
