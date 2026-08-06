# Identity-bound container serving

Táto vrstva pridáva HTTP inference service a Dockerfile nad immutable deployment manifestom. Service pri štarte nevyhľadáva MLflow alias ani „najnovšiu“ model version.

```text
actual pulled image digest
+ immutable deployment manifest
+ mounted trusted ML artifact
→ startup binding verification
→ readiness identity
→ strict HTTP prediction
→ response with deployment provenance
```

## Startup contract

Container vyžaduje:

- `MLOPS_DEPLOYMENT_MANIFEST`, predvolene `/runtime/deployment.json`,
- `MLOPS_ARTIFACT_DIR`, predvolene `/runtime/artifact`,
- `MLOPS_IMAGE_DIGEST`, bez predvolenej hodnoty.

Startup odmietne runtime, ak:

- deployment manifest nemá validný canonical `deployment_id`,
- model URI používa alias namiesto numeric Registry version,
- artifact `model_sha256` nesedí s deployment subjectom,
- artifact `dataset_sha256` nesedí s deployment subjectom,
- artifact source revision nesedí s deployment subjectom,
- `MLOPS_IMAGE_DIGEST` chýba alebo sa nezhoduje s deployment image digestom,
- Machine Learning artifact integrity alebo exact library-version check zlyhá.

`MLOPS_IMAGE_DIGEST` musí byť digest skutočne spusteného image subjectu, ktorý runtime platforma prečítala po pull/create. Samotná environment variable nie je dôkazom, že image engine spustil tieto bytes. Tento dôkaz musí dodať container runtime gate.

## HTTP surface

Service vystavuje iba:

- `GET /healthz` — proces je živý,
- `GET /readyz` — model a identity binding prešli startupom,
- `POST /v1/predict` — strict churn inference request.

OpenAPI, Swagger UI a ReDoc sú v image vypnuté. Prediction schema odmieta extra fields, hodnoty mimo rozsahu a neznáme kategórie.

Úspešná odpoveď obsahuje:

- prediction a probability,
- decision threshold,
- service name,
- exact `deployment_id`, generation a `release_id`,
- `candidate_id` a model SHA-256,
- exact numeric Registry URI,
- image digest.

Tým je každá odpoveď spätne priraditeľná ku konkrétnemu deployment subjectu. Odpoveď však sama nedokazuje, že upstream router poslal request podľa authoritative routing state-u.

## Dockerfile

`Dockerfile.serving`:

- používa oficiálny `python:3.12-slim` base image,
- inštaluje Machine Learning a MLOps packages z repository source,
- používa FastAPI 0.141.1 a Uvicorn 0.52.1,
- spúšťa jeden Uvicorn process,
- beží ako non-root UID 10001,
- nepribaľuje model, deployment manifest ani secrets,
- očakáva read-only runtime mount,
- obsahuje liveness healthcheck.

Base-image digest zatiaľ nie je pinovaný, pretože tento PR nevykonal build ani resolution. Finálny image build gate musí zapísať exact base digest, dependency resolution, výsledný OCI manifest digest a platform.

## Build contract

Z koreňa repozitára:

```bash
docker build \
  --file labs/mlops/Dockerfile.serving \
  --tag knowledge-hub/churn-serving:candidate \
  .
```

Po build-e sa musí získať immutable digest. Tag nie je deployment identity.

```bash
docker image inspect knowledge-hub/churn-serving:candidate
```

Deployment manifest sa vytvorí až po známom image digeste. Runtime potom dostane rovnaký digest cez `MLOPS_IMAGE_DIGEST` a deployment/artifact paths cez read-only mount.

## Testovaná source hranica

Source tests preukazujú:

- exact deployment/artifact/image binding,
- health a readiness response,
- successful strict HTTP prediction,
- provenance fields v odpovedi,
- refusal extra fields a out-of-range values,
- bounded 422 pri feature-contract refusal.

Source tests nepoužívajú skutočný Docker engine ani produkčný model artifact. Preto nepreukazujú:

- Dockerfile buildability na clean runneri,
- actual OCI digest,
- non-root filesystem behavior v containery,
- mount permissions,
- live Uvicorn process v containery,
- resource limits, termination alebo concurrent traffic,
- dve reálne serving generations,
- canary proxy a workload rollback.

Tieto dôkazy zostávajú ďalším runtime blokom a Practical v1 serving checklist ostáva otvorený.
