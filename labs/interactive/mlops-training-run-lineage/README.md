# MLOps Training Run Lineage Incident

A payment-risk retraining request has already passed the Continuous Training trigger gate. The platform starts a training job, the job finishes `succeeded`, and the starter lineage gate immediately registers its output as a candidate.

That is not sufficient candidate authority. Your task is to repair `/workspace/lineage_gate.py` so candidate registration happens only when the **actual loaded training execution** can be bound back to the exact approved retraining subject and the exact output artifact bytes.

## Incident

The upstream approved request pins:

- retraining subject `MLOPS-PAY-CT-2026-08-16-028`;
- operation `ct-op-7d1d41d319be` and request `train-request-pay-2026-08-16-042`;
- model family `payment-risk` and baseline `risk-serving-r39`;
- dataset generation `pay-train-2026-08-g42` plus its immutable data-manifest digest;
- label contract `confirmed_loss_within_30d-v2`;
- `promotion_mode=validation-required` and `promotion_authorized=false`.

The training-lineage contract additionally pins the execution environment:

- exact source revision;
- exact trainer image **digest**, not a mutable image tag;
- exact dependency-lock digest;
- exact trainer-config bytes and config ID;
- exact random seed and entrypoint;
- required output artifact type and filename.

The canonical training job reports `status=succeeded`, uses the right dataset and produces a model artifact, but its loaded source revision and trainer image digest do **not** match the approved contract. The correct outcome is therefore rejection with no `candidate-manifest.json`.

The starter is intentionally unsafe. It trusts `status=succeeded` plus the artifact digest reported by the run, declares `lineage_verified=true`, and registers a candidate without proving what actually ran.

A valid repair must distinguish:

```text
approved retraining request
!= scheduled training job
!= actual loaded dataset/code/image/config
!= successful process exit
!= exact output artifact lineage
!= validated candidate
!= promotion authority
```

## Workspace

```text
/workspace/
  lineage_gate.py
  training-lineage-contract.json
  approved-training-request.json
  training-run.json
  trainer-config.json
  model.bin
```

All five evidence/config/artifact inputs are protected canonical files. A correct canonical decision must not create `/workspace/candidate-manifest.json`. Exact valid synthetic evidence used by the validator may create one deterministic candidate manifest. The lab must never create `promotion-request.json`.

## Commands

```bash
help
status
check
hint
attest
reset
self-test
```

Run the current lineage gate:

```bash
attest
```

Inspect the execution evidence:

```bash
cat /workspace/approved-training-request.json
cat /workspace/training-lineage-contract.json
cat /workspace/training-run.json
sha256sum /workspace/trainer-config.json /workspace/model.bin
```

Edit the learner implementation:

```bash
nano /workspace/lineage_gate.py
```

Then validate:

```bash
check
```

## Acceptance contract

The validator proves that your implementation:

1. supports only the expected training-lineage contract generation;
2. binds the approved request to the exact retraining subject, request ID, operation ID, model family and baseline;
3. binds dataset generation, immutable data-manifest digest and label contract exactly;
4. rejects an upstream request that claims promotion authority or bypasses `validation-required`;
5. verifies trainer-config bytes against the pinned SHA-256, not only a config name;
6. verifies the config ID and random seed against the execution contract;
7. requires the training run to be `succeeded`, while treating success as necessary but not sufficient;
8. binds the run to the exact approved-request SHA-256;
9. binds actual source revision to the approved revision;
10. binds the trainer container by immutable image digest;
11. binds the exact dependency-lock digest;
12. binds trainer config ID/digest, random seed and entrypoint to what actually ran;
13. binds output artifact type and filename;
14. hashes the actual `/workspace/model.bin` bytes and refuses to trust only the digest claimed by run metadata;
15. creates a candidate only after all configured, resolved, loaded and output evidence agrees;
16. records contract, request and training-run evidence digests in the candidate manifest;
17. makes exact replay deterministic and byte-for-byte idempotent;
18. refuses to overwrite conflicting pre-existing candidate state;
19. rejects foreign/malformed/mismatched evidence without candidate side effects;
20. records `evaluation_required=true`, `promotion_mode=validation-required` and `promotion_authorized=false`;
21. never creates `promotion-request.json` or changes the production baseline;
22. preserves every protected canonical input byte-for-byte.

The validator also exercises a fully valid run, exact replay, candidate-state conflict, foreign subject/request/operation, dataset and manifest mismatches, wrong label contract, wrong request digest, wrong source/image/dependency/config/seed/entrypoint, failed training, wrong artifact metadata, tampered config/model bytes, forbidden promotion authority, and generated valid executions.

The objective is the training execution authority boundary: **a candidate is not justified by “job succeeded”; candidate lineage must prove the exact approved information state was actually loaded and that the exact resulting bytes belong to that run. Evaluation and promotion remain separate authorities.**
