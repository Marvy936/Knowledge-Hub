# Identity-bound container serving

Táto vrstva pridáva HTTP inference service a Dockerfile nad immutable deployment manifestom. Service pri štarte nevyhľadáva MLflow alias ani „najnovšiu“ model version.

```text
exact local container image subject
+ immutable deployment manifest
+ mounted trusted ML artifact
→ startup binding verification
→ readiness identity
→ strict HTTP prediction
→ response with deployment provenance
```

Practical v1 local runtime gate používa content-addressed Docker image ID `sha256:<64-hex>` získaný z local Docker engine po build-e. Tento subject je immutable pre konkrétny local image object, ale nie je to OCI distribution/registry manifest digest. Remote Registry push/pull alebo Kubernetes image resolution preto zostávajú samostatnou proof boundary.

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
- `MLOPS_IMAGE_DIGEST` chýba alebo sa nezhoduje s deployment image subjectom,
- Machine Learning artifact integrity alebo exact library-version check zlyhá.

`MLOPS_IMAGE_DIGEST` musí byť exact image subject, ktorý runtime gate resolvoval z engine a následne skutočne použil pri `docker run`. Samotná environment variable nie je dôkazom, že image engine spustil rovnaký subject. Local gate preto:

1. buildne image,
2. prečíta jeho content-addressed Docker image ID,
3. vytvorí deployment manifest s týmto ID,
4. container spustí **podľa image ID**, nie podľa mutable tagu,
5. rovnaké ID prečíta späť z readiness/prediction provenance.

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
- image subject.

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

Base-image distribution digest zatiaľ nie je súčasťou bounded local evidence subjectu. Dedicated local runtime gate preukazuje výsledný local Docker image ID a skutočný container execution; neprezentuje tento ID ako OCI Registry manifest digest.

## Executable local container runtime gate

Authoritative source driver:

```text
labs/mlops/scripts/run_containerized_inference_runtime.py
```

Dedicated hosted workflow:

```text
.github/workflows/mlops-containerized-inference-runtime.yml
```

Driver nezačína druhý training alebo Registry lifecycle. Očakáva artifacts z existujúceho `run_registry_gate.sh` a nad nimi vykoná:

```text
exact candidate + Registry evidence
→ immutable release
→ Dockerfile.serving build
→ docker image inspect → content-addressed image ID
→ immutable deployment subject
→ explicit read-only mount permissions
→ docker run by image ID
→ uid=10001 read-back
→ /healthz
→ /readyz exact identity
→ /v1/predict exact identity
→ malformed request → 422
→ wrong MLOPS_IMAGE_DIGEST → startup refusal
→ container/image cleanup read-back
```

Mountované `deployment.json`, artifact `manifest.json` a `model.joblib` sú pred container startom explicitne nastavené na `0444`. Model SHA-256 sa po permission transition znova overí; file mode sa teda nesmie stať spôsobom, ako obísť byte identity.

Workflow navyše odstráni disposable Registry/Python runtime, uloží canonical evidence JSON ako Actions artifact a na successful `main` push publikuje connector-readable statusy. Source existencia workflowu však nie je executed evidence.

## Build contract

Z koreňa repozitára je základný image build stále:

```bash
docker build \
  --file labs/mlops/Dockerfile.serving \
  --tag knowledge-hub/churn-serving:candidate \
  .
```

Tag nie je deployment identity. Local runtime gate získa image ID cez engine inspect a následne image spúšťa podľa tohto ID.

Remote OCI distribution contract by navyše potreboval registry push/pull a manifest digest read-back. To aktuálny local gate netvrdí.

## Source-test hranica

Pure/source tests preukazujú:

- exact deployment/artifact/image binding,
- health a readiness response,
- successful strict HTTP prediction,
- provenance fields v odpovedi,
- refusal extra fields a out-of-range values,
- bounded 422 pri feature-contract refusal,
- image-ID format validation,
- exact readiness/prediction subject validation,
- explicit `0444` mount preparation bez zmeny model bytes.

Tieto testy samy nepoužívajú Docker engine. Skutočný Docker build, non-root container, live Uvicorn a wrong-digest startup refusal preukáže až dedicated runtime workflow, keď sa skutočne vykoná.

Preto až do authoritative successful runu zostávajú nepreukázané:

- actual clean-runner Dockerfile build,
- live non-root filesystem/mount behavior,
- live Uvicorn HTTP request v containery,
- remote OCI Registry manifest/digest a pull read-back,
- resource limits, termination alebo concurrent traffic,
- dve reálne container serving generations,
- platform canary proxy alebo Kubernetes/load-balancer rollback.

Practical v1 container runtime status preto zostáva `Pending`, kým exact workflow evidence neexistuje.
