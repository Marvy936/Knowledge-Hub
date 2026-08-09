# Post-retraining runtime chain

Tento gate skladá tri už existujúce MLOps authority vrstvy do jednej exact-subject runtime reťaze:

```text
live controlled retraining
→ exact new candidate/release/Registry version
→ actual local Docker build + live HTTP pre nový model
→ immutable post-retraining deployment handoff
→ deterministic canary routing state
→ exact rollback state
```

Neimplementuje druhý training, Registry, container serving ani routing algoritmus. Orchestrátor iba prepája ich authoritative outputs a odmietne detached lineage.

Authoritative source:

```text
labs/mlops/scripts/run_post_retraining_runtime_chain.py
```

Dedicated hosted workflow:

```text
.github/workflows/mlops-post-retraining-runtime-chain.yml
```

## 1. Baseline Registry

Workflow najprv spustí existujúci:

```text
labs/mlops/scripts/run_registry_gate.sh
```

Tým vzniknú exact baseline subjects vrátane SQLite-backed MLflow Registry, numeric model version, `champion` aliasu, candidate identity a artifact read-backu.

## 2. Live controlled retraining

Chain následne volá:

```text
labs/mlops/scripts/run_live_retraining_runtime.py
```

Gate musí preukázať:

- deterministic `drift_detected`,
- exact `approval_required` proposal,
- forged proposal approval refusal,
- samostatný validný approval artifact,
- fresh deterministic dataset snapshot,
- live Machine Learning training,
- presne jednu novú MLflow Registry version,
- `champion` alias read-back na novú version,
- exact-version model load,
- completed replay bez duplicate Registry side effectu,
- provider stop.

Chain nepreberá iba CLI stdout. Číta canonical evidence a exact artifacts z durable controlled-retraining outputu.

## 3. Exact post-retraining container runtime

Container runtime driver má dva input modes.

Default standalone mode používa baseline Registry outputs. Post-retraining chain používa fail-closed explicit mode:

```text
--candidate
--registry-evidence
--artifact-dir
--release
```

Ak sa zadá iba časť explicitných inputs alebo chýba `--release`, driver odmietne run. Dôvod je lineage: controlled-retraining release obsahuje aj `previous_candidate_id` a nesmie sa potichu pregenerovať ako nový baseline release.

Explicit mode overí:

- candidate source revision,
- Registry candidate/version/model identity,
- artifact manifest dataset/model/source identity,
- model byte size a SHA-256,
- provided release candidate/dataset/model/evaluation/policy/source identity.

Až potom existujúci container gate vykoná:

```text
Dockerfile.serving build
→ local content-addressed Docker image ID
→ immutable deployment manifest
→ read-only mount preparation
→ docker run by exact image ID
→ uid=10001
→ live /healthz
→ live /readyz
→ live /v1/predict
→ invalid request 422
→ wrong runtime image digest startup refusal
→ container/image cleanup
```

Evidence musí mať:

```text
input_mode=explicit-subjects
release_source=provided-release
```

## 4. Exact deployment equality

Po live container teste ostane immutable deployment JSON, hoci disposable local image object už bol cleanupnutý.

Chain potom spustí existujúci:

```text
labs/mlops/scripts/run_post_retraining_handoff.py
```

s presne rovnakými:

- release,
- Registry evidence,
- service name,
- generation,
- image reference,
- image digest.

Handoff musí z týchto subjects deterministicky rebuildnúť deployment, ktorý je JSON-equal live-tested deploymentu.

```text
handoff.deployment == live_tested_deployment
```

Ak sa líši candidate, release, Registry version, model SHA, image digest/reference alebo generation, chain zlyhá.

## 5. Canary routing state

Pred handoffom chain vytvorí current routing state:

```text
stable = pre-retraining current deployment
canary = none
canary_basis_points = 0
```

Handoff potom compare-before-change vytvorí:

```text
stable = previous deployment
canary = exact live-tested post-retraining deployment
canary_basis_points = 2500
previous_routing_state_id = exact current routing state
```

Chain deterministicky hľadá jeden routing key pre stable a jeden pre canary a oba musí prečítať späť cez `route_request()`.

Toto je real execution deterministic routing-state contractu. Nie je to live reverse proxy alebo platform load balancer.

## 6. Rollback

Najprv sa zámerne skúsi stale rollback s nesprávnym expected routing-state ID. Musí byť odmietnutý.

Potom sa rollback vykoná proti exact canary state:

```text
stable = original deployment
canary = none
canary_basis_points = 0
previous_routing_state_id = exact canary routing state
```

Následný route probe musí vybrať pôvodný stable deployment.

Rollback teda nepoužíva mutable Registry alias ani "latest" model resolution.

## Canonical evidence

Finálny chain JSON pinne minimálne:

- exact Git SHA,
- live-retraining evidence/operation/state IDs,
- new candidate/release/Registry evidence/version/model identities,
- container evidence ID,
- exact Docker image ID,
- live-tested deployment ID,
- handoff ID,
- current a canary routing-state IDs,
- deterministic stable/canary route probes,
- stale rollback refusal,
- rollback routing-state ID a stable read-back,
- explicit proof boundaries,
- canonical chain evidence ID.

Workflow pred cleanupom uchová aj component evidence:

- live retraining JSON,
- container runtime JSON,
- handoff JSON,
- rollback routing JSON,
- live-tested deployment JSON.

Po odstránení complete runtime/venv/Docker residue pridá:

```text
workflow_cleanup_verified=true
```

A vytvorí artifact manifest s SHA-256 a byte size každého evidence JSONu.

## Proof boundary

Successful exact-revision workflow run preukáže:

```text
live local retraining
→ live local MLflow new version
→ exact new release
→ actual local Docker image build
→ non-root live HTTP pre nový model
→ immutable deployment equality
→ deterministic canary routing state
→ exact rollback state
→ cleanup read-back
```

Nepreukáže:

- live previous/stable container v tom istom chain gate,
- live reverse proxy alebo service-mesh traffic split,
- remote OCI Registry push/pull alebo registry manifest digest,
- Kubernetes/cloud rollout,
- production traffic,
- production telemetry/business drift,
- HA alebo disaster recovery.

Pred-retraining stable deployment image zostáva v tomto gate explicitne control-plane-only subject. New post-retraining deployment má actual local Docker/live-HTTP evidence.

Kým `.github/workflows/mlops-post-retraining-runtime-chain.yml` nevytvorí successful authoritative run, tento chain je `Implemented`, nie `Runtime verified`.
