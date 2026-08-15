# MLOps Model Promotion and Artifact Provenance

This challenge models the release gate between model evaluation and a production model release.

The candidate has a model artifact, package manifest and evaluation report. The starter `/workspace/promote.py` makes a common MLOps mistake: it promotes a candidate when one aggregate F1 metric is high enough, without proving that the evaluated subject is the exact artifact being released.

Repair `promote.py` so promotion is bound to immutable evidence rather than a mutable candidate name or a generic `quality_passed` idea.

Your promotion gate must require all of these conditions before it changes `/workspace/release/current.json`:

- the SHA-256 of the actual `candidate/model.json` bytes matches the artifact digest in the manifest;
- the evaluation report is bound to that same exact artifact digest;
- manifest, evaluation and the local evaluation dataset agree on the approved dataset ID and SHA-256;
- manifest and evaluation agree on an exact lowercase 40-hex source revision;
- the model package format and feature schema match the promotion policy;
- the evaluator generation matches the promotion policy;
- aggregate F1 meets the configured threshold;
- every required segment is present and meets the segment threshold;
- a rejected candidate leaves the existing release byte-for-byte unchanged;
- a successful release records immutable digests and a deterministic release ID.

Do not solve the lab by hard-coding the supplied model digest. The validator creates modified candidate copies and expects the gate to recompute and reconcile the actual subjects.

Useful commands:

```bash
cat promote.py
cat candidate/manifest.json
cat candidate/evaluation.json
cat promotion-policy.json
promote
check
```

The candidate model is a tiny JSON scoring artifact so the exercise remains fully offline and deterministic. This lab teaches the promotion/provenance boundary, not predictive-model quality or MLflow itself.

The production mental model is:

```text
exact model bytes
+ package manifest
+ exact evaluation dataset
+ evaluation report bound to those bytes
+ schema/evaluator/threshold policy
        |
        v
pre-promotion reconciliation
        |
        +-- reject -> current release unchanged
        |
        `-- accept -> immutable release manifest
```

Lab commands: `promote`, `status`, `check`, `hint`, `reset`.
