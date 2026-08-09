# Knowledge Hub Practical v1 release-candidate gate

Tento dokument definuje posledný repository-wide runtime gate pred tým, než je možné začať finálny Practical v1 acceptance closeout. Samotný successful gate **nevytvára release tag** a nemení sekcie 18–21 na `User accepted`.

Canonical driver:

```text
scripts/run_practical_v1_release_candidate.py
```

Hosted workflow:

```text
.github/workflows/practical-v1-release-candidate.yml
```

## Prečo existuje samostatný RC gate

Jednotlivé flagship workflowy dokazujú vlastný bounded subject. Release candidate potrebuje navyše preukázať, že rovnaký exact Git commit dokáže prejsť všetkými povinnými Practical v1 vrstvami bez toho, aby sa evidence skladala z rôznych branchov alebo rôznych source generations.

RC lifecycle je:

```text
exact clean checkout
→ core repository/package contracts
→ MLOps post-retraining runtime chain
→ RAG clean-checkout runtime
→ live Keycloak + protected RAG/agent identity path
→ repository/runtime cleanup read-back
→ canonical release-candidate evidence bundle
```

Žiadny component sa v RC driveri reimplementuje. Root orchestrátor volá existujúce authoritative drivers.

## 1. Core component

RC spustí:

```text
scripts/practical_v1_core.py
```

Core evidence musí mať:

- exact `subject_sha`,
- celý expected stage set,
- `all_passed=true`,
- `cleanup_verified=true`,
- `worktree_verified=true`,
- canonical `evidence_id`.

Core obsahuje five-package contracts, repository-integrity gate a deterministic agent hard evaluation.

## 2. MLOps component

RC najprv vytvorí baseline Registry subjects existujúcim `run_registry_gate.sh` a následne spustí:

```text
run_post_retraining_runtime_chain.py
```

Required chain:

```text
live local ML training
→ live local MLflow new Registry version
→ exact release
→ actual local Docker build
→ non-root live HTTP pre nový model
→ immutable deployment equality
→ deterministic canary routing state
→ stale rollback refusal
→ exact rollback state
```

Final RC evidence musí zachovať MLOps proof boundary:

```text
new-model container = live local Docker/HTTP
canary = deterministic routing-state execution
remote OCI Registry = not claimed
production platform = not claimed
```

## 3. RAG component

RC spustí:

```text
run_clean_checkout_runtime.py
```

Required lifecycle:

```text
exact Git corpus
→ deterministic chunks/index
→ answered query + exact citations
→ explicit no-result/abstention
→ hard eval
→ direct + retrieved-context injection slices
→ prompt/config release
→ trace identities
→ cleanup
```

RC nesmie rozšíriť claim na semantic embedding/vector/generative provider. Practical v1 core RAG zostáva deterministic offline/extractive adapter bez externého API key.

## 4. Live identity/agent component

RC spustí canonical:

```text
run_live_identity_gate.py
```

Required path:

```text
live local Keycloak realm import
→ OIDC discovery + JWKS
→ live service-account Client Credentials token
→ resource-server signature/issuer/audience/scope/role validation
→ protected promoted RAG
→ promoted-retrieval-bound agent plan
→ separate exact approval
→ one local sandbox remediation
→ completed replay without duplicate mutation
→ live 401/403 negative token variants
→ cleanup
```

Browser/public-client boundary zostáva presne:

```text
live imported S256 PKCE configuration
+ real disposable PKCE session helper
+ no interactive Authorization Code exchange
```

Successful RC gate preto nesmie tvrdiť plne automatizovaný browser login.

## Same-subject rule

Všetky štyri component JSONs musia obsahovať rovnaký exact:

```text
subject_sha
```

Root orchestrátor odmietne evidence patriace inému commitu.

Evidence nie je možné „poskladať“ z posledného zeleného MLOps runu a iného zeleného RAG/Keycloak runu.

## Repository cleanliness

RC workflow inštaluje local packages ako wheel snapshots, nie editable installs. Dôvod je release hygiene: dependency bootstrap nesmie vytvoriť source-tree `.egg-info` state, ktorý by sa potom tváril ako súčasť runtime.

Pred RC driverom musí byť:

```text
git status --porcelain --untracked-files=all
→ empty
```

Po component runtime/cleanup musí zostať rovnaký clean checkout.

Disposable work root a virtual environment sú mimo Git checkoutu.

## Evidence bundle

Successful RC artifact obsahuje minimálne:

```text
core.json
mlops.json
rag.json
identity.json
release-candidate.json
artifact-manifest.json
```

Root `release-candidate.json` pinne:

- exact Git SHA,
- component evidence IDs,
- per-component evidence-file SHA-256/byte sizes,
- core stage/cleanup/worktree state,
- MLOps operation/version/deployment/image/canary/rollback identities,
- RAG snapshot/index/eval/release/answer/trace identities,
- Keycloak issuer/image + protected RAG/agent authority identities,
- explicit proof boundaries,
- canonical `release_candidate_id`.

Po outer runtime cleanup workflow doplní:

```text
workflow_cleanup_verified=true
```

Artifact manifest potom pinne SHA-256 a size každého JSONu.

## Čo successful RC gate neznamená

Ani successful exact-revision gate automaticky nepreukazuje:

- production readiness,
- live Kubernetes/cloud rollout,
- remote OCI Registry push/pull,
- live reverse-proxy/service-mesh canary,
- production business drift,
- production TLS/HA Keycloak,
- interactive browser Authorization Code exchange,
- external production approval authority,
- sekcie 18–21 ako `User accepted`.

## Tagging boundary

RC evidence vždy obsahuje:

```text
release_tag_created=false
user_acceptance_claimed=false
```

Workflow nemá `contents: write` a nevytvára Git tag.

`v1.0.0` sa môže vytvoriť až po:

1. successful exact-main alebo explicit release-candidate runtime gate,
2. read-backu canonical artifact/evidence identities,
3. kontrole výsledného repository diffu,
4. potvrdení release-note proof boundaries,
5. splnení sekcie 18–21 review pravidla z `PRACTICAL-V1-ROADMAP.md`,
6. explicitnom finálnom acceptance rozhodnutí.

Kým issue #151 blokuje GitHub Actions dispatch, RC gate je iba `Implemented`, nie `Runtime verified`.
