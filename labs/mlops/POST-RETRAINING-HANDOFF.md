# Post-retraining deployment handoff

Táto vrstva oddeľuje úspešné dokončenie controlled retrainingu od nasadenia novej generácie. Completed training alebo Registry version samy osebe nemenia serving traffic.

```text
completed controlled-retraining state
+ exact operation
+ release manifest
+ Registry evidence
+ current deployment
+ current stable-only routing state
+ built image reference a digest
→ immutable new deployment
→ bounded canary routing state
→ post-retraining handoff ID
```

## Povinný completed subject

Handoff vyžaduje state vo fáze `completed`. State musí patriť exact operation a jeho artifact identities sa musia zhodovať s dodanými súbormi:

- release ID,
- candidate ID,
- model SHA-256,
- Registry evidence ID,
- numeric Registry version.

Neukončený, upravený alebo inej operácii patriaci state sa odmietne.

## Release a Registry väzba

Release musí:

- používať candidate z completed state-u,
- používať model digest z completed state-u,
- používať source revision operation subjectu,
- ukazovať `previous_candidate_id` na candidate aktuálneho deploymentu,
- predstavovať nový candidate.

Registry evidence musí patriť tomu istému candidate, source revision a model digestu. Deployment používa exact numeric URI, nie mutable alias.

## Image boundary

Handoff vyžaduje image reference aj `sha256:` digest. Digest je explicitný vstup a súčasť deployment ID.

Táto source vrstva image nestavia a nepreukazuje, že deklarovaný digest existuje v Registry. Actual build, digest read-back, signature/provenance a container startup ostávajú samostatný runtime gate.

## Routing boundary

Aktuálny routing state musí:

- patriť rovnakému service,
- mať current deployment ako stable subject,
- nemať otvorený canary deployment,
- zhodovať sa s exact `expected_current_routing_state_id`.

Post-retraining handoff nevytvára full cutover. Canary musí dostať 1 až 9 999 basis points. Nula by nebola canary a 10 000 by odstránilo stable comparison subject.

Výsledný routing state zachová current deployment ako stable a novú generation pridá ako canary.

## Canonical handoff

Bundle obsahuje:

- operation ID,
- completed state ID,
- previous deployment ID,
- previous routing-state ID,
- celý immutable nový deployment manifest,
- celý compare-before-change canary routing state,
- canonical `post_retraining_handoff_id`.

Validátor znovu overí deployment, routing predecessor, stable/canary väzbu, bounded traffic a canonical ID.

## Executable driver

```bash
python labs/mlops/scripts/run_post_retraining_handoff.py \
  --operation labs/mlops/.runtime/retraining-operation.json \
  --completed-state labs/mlops/.runtime/retraining-state.json \
  --release labs/mlops/.runtime/controlled-retraining/release.json \
  --registry-evidence labs/mlops/.runtime/controlled-retraining/registry-evidence.json \
  --current-deployment labs/mlops/.runtime/current-deployment.json \
  --current-routing-state labs/mlops/.runtime/current-routing.json \
  --service-name churn \
  --generation retrained-canary-2 \
  --image-reference example/churn:2 \
  --image-digest sha256:<exact-image-digest> \
  --canary-basis-points 1000 \
  --expected-current-routing-state-id <exact-routing-state-id> \
  --output labs/mlops/.runtime/post-retraining-handoff.json
```

Refusal skončí exit code `2` a handoff output nevznikne.

## Overená source hranica

Izolovaná reconstruction prešla:

- Python `compileall`,
- **6/6 pytest cases**.

Testy pokrývajú pozitívny completed-operation handoff, exact numeric Registry version, neukončený state, release ktorý nenadväzuje na current candidate, existujúci canary, stale routing subject, canonical tampering a CLI subject exposure.

## Neoverená hranica

Tento blok nepreukazuje actual OCI build, image existence alebo signature, container startup, platform route mutation, live canary traffic, post-handoff monitoring, rollback ani business outcome. Practical v1 serving/canary gate ostáva otvorený do runtime read-backu.
