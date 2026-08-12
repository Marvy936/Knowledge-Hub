# Practical v1 release evidence

> **Status: release-evidence pipeline runtime verified; final tag subject exact-head run pending.**

The permanent hosted workflow is `.github/workflows/practical-v1-release-evidence.yml`. It composes the canonical release-candidate lifecycle with exact dependency resolution, GitHub workflow/run provenance and post-cleanup artifact manifest verification.

## Verified baseline

On `789b5038b81b9342b1aef57b809bd3b67202ebde`:

- RC run `31542501323` succeeded,
- release-evidence run `31542501346` succeeded,
- `release_candidate_id=2e0a0754332864ca5898852b921d76d88e78d0c8209ea3dccfab7a92c6fe0778`,
- `dependency_resolution_id=e37285a9af7f2d53742fa8b29db91de07a6980ba1fad0c785dd60ed1c66a03dc`,
- `workflow_provenance_id=80221bfce87ce37820738fe41d9392bc639f8fce216a9b7df1f7d812396471aa`,
- `release_evidence_id=1bced14424764a890f8c8fbd346c49992c5ba1d2c7963d9f3b65485547c37b47`,
- `artifact_manifest_id=52f6c2c886c14d746f3fdd7c35fc82a93e24372570acea50f6a90cad08c6eca2`,
- `workflow_cleanup_verified=true`,
- `release_tag_created=false`,
- `user_acceptance_claimed=false`.

The workflow permission remains `contents: read`; it is evidence generation, not release/tag mutation authority.

## Canonical artifact contents

A successful final bundle contains at least:

- `core.json`,
- `mlops.json`,
- `rag.json`,
- `identity.json`,
- `release-candidate.json`,
- `dependency-resolution.json`,
- `workflow-provenance.json`,
- `release-evidence.json`,
- `artifact-manifest.json`.

The finalizer recalculates the canonical candidate/dependency/provenance identities before producing release evidence and the artifact manifest binds SHA-256/size of the complete JSON bundle after cleanup.

## Final tag-subject acceptance

Before `v1.0.0`, the current final `main` SHA must independently satisfy:

1. successful RC lifecycle,
2. successful release-evidence workflow,
3. exact subject SHA equality,
4. canonical IDs verified,
5. cleanup/worktree read-back verified,
6. `release_tag_created=false`,
7. `user_acceptance_claimed=false`.

The final run IDs live in GitHub Actions provenance. They are not committed after execution, because such a commit would create a new unverified Git subject.

## Proof boundary

Successful Practical v1 release evidence proves the bounded local/hosted profile defined by the repository. It does not automatically prove production Kubernetes/cloud readiness, production identity HA/federation, remote production Registry durability, real-browser PKCE exchange, GPU/distributed ML, external LLM quality or production remediation authority.
