# Practical v1 release evidence

Status: **source-level implemented only; runtime evidence pending**.

Tento dokument definuje poslednú evidence vrstvu nad existujúcim `Practical v1 release candidate` gate-om.

## Dve rozdielne identity

`release_candidate_id` identifikuje all-passed runtime kandidáta zloženého z:

- Practical v1 core,
- MLOps post-retraining runtime chain,
- RAG clean-checkout lifecycle,
- live Keycloak + bounded-agent identity path.

`release_evidence_id` je vyššia identita. Pinne:

```text
release_candidate_id
+ exact dependency resolution
+ exact GitHub workflow/run provenance
+ exact subject SHA
+ explicit no-tag/no-user-acceptance boundary
```

Pre finálny hosted release dôkaz je authoritative až `release_evidence_id`.

## Authoritative source

Finalizer:

```text
scripts/finalize_practical_v1_release_evidence.py
```

Hosted workflow:

```text
.github/workflows/practical-v1-release-evidence.yml
```

Nižší component gate zostáva:

```text
.github/workflows/practical-v1-release-candidate.yml
```

Nový workflow ho nenahrádza novou business logikou. Spúšťa ten istý root RC driver a pridáva iba release provenance/attestation vrstvu.

## Dependency resolution

Workflow inštaluje lokálne lab balíky z byte-copied source snapshotov uložených mimo Git checkoutu v `runner.temp`. Tým package build metadata nemusí zapisovať do checkoutu.

Dependency evidence pinne minimálne:

- Python version,
- Python executable,
- Python implementation,
- platform a machine,
- pip version,
- canonical sorted installed distribution names a versions,
- exact Git subject SHA,
- canonical `dependency_resolution_id`.

Finalizer vyžaduje prítomnosť všetkých piatich lokálnych distributions:

- `knowledge-hub-ml-flagship-lab`,
- `knowledge-hub-mlops-flagship-lab`,
- `knowledge-hub-rag-flagship-lab`,
- `knowledge-hub-bounded-ops-agent`,
- `knowledge-hub-keycloak-ai-api`.

## Workflow provenance

Workflow provenance pinne:

- workflow name `Practical v1 release evidence`,
- exact `subject_sha`,
- GitHub `run_id`,
- `run_attempt`,
- event name,
- repository,
- GitHub run SHA,
- ref,
- canonical run URL,
- `workflow_provenance_id`.

`run_id` a `run_attempt` musia byť kladné celé čísla. Event musí byť jeden z bounded profilov:

```text
workflow_dispatch
push
pull_request
```

Pre pull request môže GitHub run SHA reprezentovať synthetic merge subject; `subject_sha` zostáva exact head SHA, ktorý workflow checkoutol a runtime gate overil.

## Final release evidence

Finalizer najprv znovu overí canonical `release_candidate_id`. Nestačí, že pole iba vyzerá ako SHA-256; musí zodpovedať aktuálnemu RC JSON payloadu.

Rovnako prepočíta:

- `dependency_resolution_id`,
- `workflow_provenance_id`.

Až potom vytvorí:

```text
release_evidence_id = SHA256(canonical final release-evidence payload)
```

Finálny artifact bundle obsahuje minimálne:

- `core.json`,
- `mlops.json`,
- `rag.json`,
- `identity.json`,
- `release-candidate.json`,
- `dependency-resolution.json`,
- `workflow-provenance.json`,
- `release-evidence.json`,
- `artifact-manifest.json`.

Artifact manifest pinne SHA-256 a byte size všetkých JSON artifacts a obsahuje `release_evidence_id`, `release_candidate_id`, dependency/provenance IDs a workflow run ID.

## Cleanup boundary

Pred vytvorením artifact manifestu musí byť odstránené:

- disposable RC work root,
- copied package source root,
- temporary dependency snapshot,
- Python venv,
- `.runtime`,
- disposable MLOps Docker containers/images,
- disposable Keycloak Compose project/volumes.

Git checkout musí byť po cleanup-e čistý.

## Čo úspešný run stále neznamená

Ani successful `Practical v1 release evidence` run automaticky neznamená:

- `User accepted`,
- vytvorený `v1.0.0` tag,
- production Kubernetes/cloud readiness,
- production identity platform readiness,
- remote OCI Registry proof,
- live proxy/service-mesh canary,
- browser Authorization Code exchange.

Workflow má repository permission iba:

```text
contents: read
```

Tag preto technicky nevytvára.

## Runtime acceptance

Kým GitHub Actions nevytvorí reálny run s čitateľnými jobs a artifact bundle, táto vrstva je iba `Implemented`.

Finálny release evidence gate možno označiť `Runtime verified` až po kontrole:

1. exact run ID a exact subject SHA,
2. successful job result,
3. `release-evidence.json`,
4. canonical `release_evidence_id`,
5. dependency resolution ID,
6. workflow provenance ID,
7. artifact manifest ID,
8. cleanup/worktree read-back,
9. explicit `release_tag_created=false`,
10. explicit `user_acceptance_claimed=false`.

Až následná samostatná user review/acceptance fáza môže meniť `User accepted` a až potom sa rieši immutable tag `v1.0.0`.
