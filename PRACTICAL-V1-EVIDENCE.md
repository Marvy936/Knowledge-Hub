# Practical v1 evidence ledger

This ledger records executed evidence without turning source text into a substitute for runtime artifacts.

## 1. Combined release baseline

Subject: `789b5038b81b9342b1aef57b809bd3b67202ebde`

| Evidence | Value |
|---|---|
| Release-candidate run | `31542501323` — success |
| Release-evidence run | `31542501346` — success |
| `release_candidate_id` | `2e0a0754332864ca5898852b921d76d88e78d0c8209ea3dccfab7a92c6fe0778` |
| `dependency_resolution_id` | `e37285a9af7f2d53742fa8b29db91de07a6980ba1fad0c785dd60ed1c66a03dc` |
| `workflow_provenance_id` | `80221bfce87ce37820738fe41d9392bc639f8fce216a9b7df1f7d812396471aa` |
| `release_evidence_id` | `1bced14424764a890f8c8fbd346c49992c5ba1d2c7963d9f3b65485547c37b47` |
| `artifact_manifest_id` | `52f6c2c886c14d746f3fdd7c35fc82a93e24372570acea50f6a90cad08c6eca2` |
| Cleanup | `workflow_cleanup_verified=true`, core cleanup/worktree verified |
| Tag boundary | `release_tag_created=false` |
| Acceptance boundary | `user_acceptance_claimed=false` |

The baseline proves the bounded combined lifecycle across core contracts, MLOps post-retraining runtime, clean-checkout RAG and live Keycloak/protected RAG-agent identity composition.

## 2. RAG retrieved-context injection closeout

Subject: `8c861edac728e5d19e7dd6035e4b438b8e8f8c2a`

- workflow run `31636019897` — success,
- artifact `9157100163`,
- `evidence_id=b1db832a962fc2e4886dd59b13607b41a7a4cf276a19867098fd0232699c5116`,
- indirect runtime case ID `5ab930d70a11b9aec819860dc26bbd9048bb0310c4871eb57404bca43aed510d`,
- `attack_type=indirect`,
- malicious retrieved chunk classified `prompt_injection_detected`,
- safe chunk remained usable/cited,
- unsafe and cited chunk sets are disjoint,
- `retrieved_context_prompt_injection_eval=executed-synthetic-untrusted-document`,
- cleanup verified.

This closes the previous proof-boundary gap where indirect injection existed in unit/hard-eval coverage but was not represented in the canonical RAG runtime record.

## 3. Keycloak standalone hygiene

Run `31542501300` now concludes success on `run_attempt=2`. Attempt 1 failed during exact-subject checkout, so it did not execute the Keycloak runtime gate. The successful rerun removes that standalone CI ambiguity.

The automated identity proof still does not claim an actual interactive browser Authorization Code exchange; that remains an explicit proof boundary rather than a hidden success claim.

## 4. Repository hygiene closeout

Before the final tag-subject run, repository hygiene is part of the release subject itself:

- the remote branch set is reduced to `main` only,
- superseded draft PR #134 is closed without merge,
- temporary diagnostic/executor workflows are removed,
- the historical Section 18 one-shot remediation hook/helper is removed from the permanent documentation workflow,
- permanent release-evidence workflow remains read-only and does not create tags or claim user acceptance.

This section intentionally contains no future run ID. The commit containing this cleanup must itself become the subject of the final exact-head release lifecycle.

## 5. Final `v1.0.0` subject policy

The final release subject is **not** one of the historical subjects above. After repository metadata/workflow cleanup, the exact current `main` must run the canonical RC and release-evidence workflows again.

The final authoritative record is the GitHub Actions artifact bound to that exact SHA. No source commit may be made merely to copy the future run ID into this file, because doing so would create a different subject.

Required final artifact properties:

```text
subject_sha == tag target SHA
release candidate all_passed == true
core cleanup/worktree verified == true
workflow_cleanup_verified == true
canonical dependency/workflow provenance IDs valid
release_tag_created == false
user_acceptance_claimed == false
```

After read-back, explicit user acceptance may authorize creation of `v1.0.0` on that same SHA.
