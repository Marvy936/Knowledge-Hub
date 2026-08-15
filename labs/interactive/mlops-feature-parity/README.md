# MLOps Training-Serving Feature Parity

This challenge models a production model whose package and deployment are healthy while the serving feature vector no longer matches the representation used during training.

The offline training path uses the current `payment-risk-features-v6` contract. The serving path was copied from an older implementation and drifted: it reports a stale contract identity, handles minor currency units differently, rounds one feature differently, and compares country values without the contract normalization rule.

Work on `/workspace/serving_transform.py`.

Your repaired serving path must satisfy this contract:

- load and report the exact `contract_id` from `/workspace/feature_contract.json`;
- report the SHA-256 of the exact contract bytes actually used;
- preserve the contract `schema_id` and `feature_order`;
- produce the same vector as the offline training path for the same logical operation;
- convert minor currency units to major units according to the contract;
- apply the same country normalization and cross-border semantics as training;
- reject malformed requests instead of silently coercing incompatible input types;
- do not change the feature contract, shared runtime, offline transform, or matched incident evidence to make both sides agree on a new meaning.

Useful inspection commands:

```bash
cat feature_contract.json
cat offline_transform.py
cat serving_transform.py
cat matched-requests.json
printf '%s\n' '{"operation_id":"demo","amount_minor":12345,"merchant_velocity_minor_7d":765432,"customer_country":" sk ","merchant_country":"SK"}' | offline
printf '%s\n' '{"operation_id":"demo","amount_minor":12345,"merchant_velocity_minor_7d":765432,"customer_country":" sk ","merchant_country":"SK"}' | serve
check
```

The strongest repair is to make serving consume the same versioned feature contract and shared transform runtime rather than maintaining a second hand-copied implementation. Independent implementations can be valid in real systems, but then they need equivalent contract binding and conformance evidence.

Key idea:

```text
raw operation
     |
     +--------------------------+
     |                          |
     v                          v
offline training path      online serving path
     |                          |
     +------ exact contract ----+
     +------ schema/order ------+
     +------ semantics ---------+
     +------ matched values ----+
                |
                v
           model input
```

A green endpoint or matching schema name is not parity evidence. The lab accepts the repair only when exact contract identity and behavior agree across production-like matched examples, edge cases, and invalid inputs.

Lab commands: `offline`, `serve`, `status`, `check`, `hint`, `reset`.
