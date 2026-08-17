# MLOps Release Delivery Integrity Incident

A model promotion gate has already approved one exact payment-risk release. The delivery controller reports `Ready`, its health endpoint returns HTTP 200, and the unsafe starter therefore declares the release verified and requests 100% traffic.

That is not sufficient delivery authority.

Repair `/workspace/deliver.py` so delivery verification proves that the **exact immutable promoted release** was rendered into the deployment specification, reconciled by the controller, and loaded by every expected serving instance. Delivery verification must remain separate from canary or rollout authority.

## Incident

The approved release subject is:

```text
MLOPS-PAY-RISK-PROD-2026-08-r31
```

Its immutable release manifest pins:

- model family `payment-risk`;
- registry version `128`;
- exact model package SHA-256;
- exact serving image by OCI digest, never `:latest`;
- feature contract `payment-risk-features-v6` and exact registry digest;
- preprocessing digest;
- decision policy `review-capacity-v4` and exact policy digest;
- inference protocol `v2`;
- environment `production`;
- initial canary routing intent of 5%;
- exact upstream promotion evidence;
- `promotion_authorized=true`.

The independent delivery approval binds the exact bytes of that release manifest to:

- delivery policy `ml-delivery-prod-v3`;
- operation `MLOPS-PAY-92-DEPLOY-R31`;
- environment `production`;
- expected current release `MLOPS-PAY-RISK-PROD-2026-07-r29`.

The canonical deployment specification itself is exact and immutable. The controller also reports the correct spec digest, generation and `Ready=true`.

However, one of the three serving instances reports `payment-risk-features-v5` instead of `payment-risk-features-v6`.

The canonical correct result is therefore:

```text
blocked / fleet_fingerprint_mismatch
delivery_verified=false
rollout_authorized=false
```

The starter is intentionally unsafe. It trusts only `controller.ready == true` and HTTP 200, writes a successful delivery report, sets `rollout_authorized=true`, and creates `traffic-change-request.json`.

## Authority boundary

This lab deliberately separates four different statements:

```text
promotion approved exact release
!= deployment spec rendered correctly
!= controller reconciled that spec
!= complete fleet loaded the same release fingerprint
!= rollout / canary authority
```

`mlops-model-promotion` owns the earlier promotion decision. This lab starts from an already promoted immutable release. `mlops-canary-rollback` owns later traffic-exposure and guardrail decisions. A successful repair here may prove `delivery_verified=true`, but it must still emit `rollout_authorized=false`.

## Workspace

```text
/workspace/
  deliver.py
  delivery-contract.json
  release-manifest.json
  release-approval.json
  deployment-spec.json
  controller-state.json
  fleet-readback.json
  current-runtime.json
```

The evidence files are protected canonical inputs. The validator also creates isolated modified cases to prove fail-closed behavior, idempotency and authority separation.

## Commands

```bash
help
status
check
hint
deliver
reset
self-test
```

Inspect the evidence:

```bash
cat /workspace/release-manifest.json
cat /workspace/release-approval.json
cat /workspace/deployment-spec.json
cat /workspace/controller-state.json
cat /workspace/fleet-readback.json
sha256sum /workspace/release-manifest.json /workspace/deployment-spec.json
```

Run the current implementation:

```bash
deliver
```

Edit it:

```bash
nano /workspace/deliver.py
```

Then validate:

```bash
check
```

## Acceptance contract

The validator proves that your repaired delivery gate:

1. supports only delivery contract `payment-risk-delivery-v3`;
2. requires the exact model family, environment, delivery policy, feature contract and inference protocol;
3. requires an already promoted release instead of deriving promotion from delivery state;
4. validates every declared SHA-256 identifier structurally;
5. rejects mutable serving-image tags and requires an image digest;
6. binds the delivery approval to the SHA-256 of the actual release-manifest bytes;
7. binds approval subject, environment, policy and operation ID to the release;
8. enforces the configured maximum initial routing percentage;
9. derives the exact content-addressed model URI from the promoted model digest;
10. requires the complete deployment specification to be an exact render of the promoted release and approval;
11. prevents `latest`, aliases or foreign feature/policy generations from entering deployment;
12. checks optimistic concurrency against the exact expected current release before accepting delivery;
13. binds controller observation to the exact operation, release subject and deployment-spec SHA-256;
14. requires controller observed and reconciled generations to agree;
15. treats `Ready=true` and HTTP 200 as necessary but not sufficient;
16. requires fleet evidence for the exact release subject and operation;
17. requires the expected number of serving instances to be present;
18. rejects duplicate serving instance identities;
19. requires every instance to report the exact model, image, feature, preprocessing, policy and protocol fingerprint;
20. requires every instance to be ready and actually exercised by request-correlated evidence;
21. blocks the canonical mixed-generation fleet;
22. verifies a fully exact fleet deterministically;
23. writes exact evidence digests and a deterministic release fingerprint in the verified report;
24. makes exact replay byte-for-byte idempotent;
25. refuses to overwrite conflicting pre-existing report state;
26. rejects foreign, malformed or mismatched evidence without creating a report;
27. never creates `traffic-change-request.json` after repair;
28. always keeps `rollout_authorized=false`, even when delivery is fully verified;
29. preserves all protected canonical input bytes.

The objective is the model delivery proof boundary: **an approved release is not safely delivered merely because the control plane is green. The exact composite release must survive rendering, reconciliation and fleet loading without mutation, and delivery verification must not silently become traffic authority.**
