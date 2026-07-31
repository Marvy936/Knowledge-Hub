# Container a package registry

GitLab Container Registry a Package Registry sú supply-chain boundaries. Spájajú build output s content identity, publication authorization, evidence, dependency resolution, runtime consumption, retention a revocation. Registry nie je iba file server. Je to authority, ktorá mapuje repository/tag/version locators na immutable artifacts a určuje, kto ich môže publishovať, čítať, mazať alebo používať ako dependency.

Tag alebo package version je human/dependency locator. OCI digest alebo package checksum identifikuje bytes. GitLab Release môže linkovať package, ale release record nevytvára immutability. Build-once-promote-many vyžaduje, aby staging a production použili ten istý content subject a aby copy/promotion zachovala signatures, SBOM a provenance.

## 1. Dominantný build-to-runtime registry model

```text
trusted build and exact candidate
→ immutable package/image bytes
→ content digest/checksum
→ authenticated write-once publication
→ registry manifest/version read-back
→ signature, SBOM and provenance subject binding
→ environment promotion/copy by digest
→ deployment/runtime pull and platform selection
→ support, scan, retention, revocation and cleanup
```

Successful `push` response does not prove complete multi-platform graph, evidence publication, immutable tag policy or runtime use.

## 2. Exact registry subject

```yaml
registrySubject:
  projectId: 481
  releaseId: payments-10.0.0-rc.4
  container:
    repository: registry.atlas.example/atlas/payments/settlement-api
    tag: 10.0.0-rc.4
    indexDigest: sha256:pay1000api
    platforms:
      linux-amd64: sha256:pay1000api-amd64
      linux-arm64: sha256:pay1000api-arm64
  package:
    type: generic
    name: migrations
    version: 10.0.0-rc.4
    sha256: mig1000
  evidence:
    sbomDigest: sha256:sbom1000
    provenanceDigest: sha256:prov1000
    signatureBundleDigest: sha256:sig1000
  publicationJobId: 881911
  sourceCandidateSha: d94e1c6
```

Repository path and tag alone are mutable locator. Subject includes exact graph and producer.

## 3. Publication identity

Preferred publication uses short-lived job identity scoped to project/package repository and candidate namespace. CI_JOB_TOKEN, deploy token, project access token or external federation have different capabilities. Write identity should not be reused by untrusted test jobs.

Container login example:

```bash
printf '%s' "$CI_REGISTRY_PASSWORD" | docker login \
  --username "$CI_REGISTRY_USER" \
  --password-stdin "$CI_REGISTRY"
```

Successful login proves credential accepted for registry endpoint. It does not prove minimum scopes, token lifetime or allowed repositories. Publication attempt and registry audit/API read-back verify effective capability.

## 4. Multi-platform build and push

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --provenance=true \
  --sbom=true \
  --tag "$CI_REGISTRY_IMAGE:10.0.0-rc.4" \
  --push .

index_digest="$(crane digest "$CI_REGISTRY_IMAGE:10.0.0-rc.4")"
printf 'index_digest=%s\n' "$index_digest"
```

Digest read-back proves current tag mapping. It does not prove tag immutability, per-platform test coverage or evidence validity. Manifest inspection enumerates descriptors:

```bash
crane manifest "$CI_REGISTRY_IMAGE@$index_digest" \
  | jq '{mediaType,manifests:[.manifests[]|{digest,platform}]}'
```

## 5. Write-once version policy

Trusted release versions must not be overwritten. If registry allows tag mutation, pipeline performs compare-and-fail:

```text
if tag/version absent
→ publish exact subject
if present with same digest
→ idempotent success
if present with different digest
→ collision, stop and investigate
```

Package registry may enforce duplicate rules differently by package type/tier. Policy must be verified for current instance.

## 6. Package registry

Package coordinate typically contains package type, namespace/name and version. Lockfiles should resolve immutable checksums where ecosystem supports them. Internal packages need provenance and retention just like containers.

Generic package upload:

```bash
curl --fail --header "JOB-TOKEN: $CI_JOB_TOKEN" \
  --upload-file dist/payments-migrations.tar.gz \
  "$GITLAB_URL/api/v4/projects/$CI_PROJECT_ID/packages/generic/migrations/10.0.0-rc.4/payments-migrations.tar.gz"
```

HTTP success proves endpoint accepted request. It does not prove checksum, immutability or correct package version content. Download and checksum read-back complete publication.

## 7. Evidence subject binding

Signature, SBOM and provenance must reference digest, not mutable tag. Successful verification proves cryptographic/identity policy for subject, not correctness/completeness of claims.

```bash
cosign verify "$CI_REGISTRY_IMAGE@sha256:pay1000api" \
  --certificate-identity-regexp='^https://gitlab.atlas.example/atlas/payments/' \
  --certificate-oidc-issuer='https://gitlab.atlas.example'
```

Verifier policy must bind exact trusted pipeline identity and environment/ref where relevant. Broad issuer-only trust is insufficient.

## 8. Build once and promotion

Promotion copies exact digest or changes environment release manifest to reference same digest. Rebuild per environment invalidates earlier tests and signatures.

```bash
crane copy \
  registry.build.example/payments-api@sha256:pay1000api \
  registry.prod.example/payments-api@sha256:pay1000api

test "$(crane digest registry.build.example/payments-api@sha256:pay1000api)" = \
     "$(crane digest registry.prod.example/payments-api@sha256:pay1000api)"
```

Digest equality proves index identity. Referrers/evidence retention and destination policy need separate verification.

## 9. Runtime consumption

Kubernetes should use digest references for authoritative release:

```bash
kubectl -n payments get pods -l app=settlement-api \
  -o jsonpath='{range .items[*]}{.metadata.uid}{" "}{.spec.containers[0].image}{" "}{.status.containerStatuses[0].imageID}{"\n"}{end}'
```

Spec image and runtime `imageID` prove desired locator and resolved content per Pod. They do not prove application config or business correctness. Multi-platform nodes may use different platform manifest digests under same index; release evidence must cover all.

## 10. Dependency confusion and namespace

Internal package name can collide with public registry. Package manager resolution, registry order and namespace ownership must ensure internal dependency cannot be replaced by public higher version. Lockfile and repository policy matter.

CI should use explicit registry URL and credentials scoped read-only for dependencies. Public fallback should be intentional and audited.

## 11. Retention and cleanup

Cleanup policy must not delete:

- supported release artifacts;
- deployed digests;
- last-known-good recovery subjects;
- artifacts under incident/legal hold;
- evidence referenced by release manifest.

Tag-based cleanup can delete untagged but deployed digests if runtime uses digest and tag was removed. Runtime inventory and release catalog must protect content.

## 12. Revocation

Deleting tag is not revocation. Deployed digest and mirrors remain. Revocation record blocks promotion/admission and triggers runtime inventory/redeployment.

```yaml
revocation:
  digest: sha256:pay1000api
  reason: poisoned-shared-cache
  effectiveAt: 2026-07-31T13:10:00Z
  actions:
    - block-promotion
    - block-new-deploy
    - inventory-runtime
    - rebuild-and-redeploy
```

## 13. Connected incident `GL-PAY-74`

Protected tag pipeline restored poisoned cache and built image. Tag `10.0.0-rc.4` first pointed to amd64-only index A. Arm64 retry later overwrote same tag with index B. Staging had A, production B. Signature verification used tag at verification time and passed for B, while staging evidence belonged A.

Cleanup policy then removed untagged index A, although staging still ran it. Incident response could not retrieve exact artifact or SBOM.

```text
cache-poisoned build
→ mutable tag A
→ tag overwrite B
→ evidence split
→ deployed untagged A deleted
```

Root cause was registry identity, immutability and retention contract.

## 14. Containment, recovery and acceptance

Containment freezes publication/cleanup, revokes affected digests, preserves registry events and inventories runtime platform digests. Recovery publishes new write-once release, binds evidence by digest and redeploys all affected cohorts.

Registry model is accepted only when:

```text
publication identity is trusted and scoped
+ release versions are write-once
+ multi-platform graph/evidence is complete
+ tags are locators and digest is authority
+ package checksums/provenance are verified
+ promotion preserves exact digest and evidence
+ runtime imageID correlates with release manifest
+ cleanup protects deployed/support/recovery subjects
+ revocation blocks new use and drives redeployment
+ second registry/platform resolves same artifact graph
```

## 15. Troubleshooting flow

```text
release/version locator
→ registry mapping history
→ index/platform/package digests
→ publication identity/job
→ signatures/SBOM/provenance
→ copy/mirror state
→ deployment/runtime image IDs
→ retention/revocation
```

Competing hypotheses include mutable tag, incomplete index, wrong package version, failed evidence publication, mirror lag, dependency confusion, cleanup deletion or runtime cache.

## 16. Anti-patterny

### Mutable release tag

Same version can mean different bytes and evidence.

### Successful push as complete publication

Platforms/referrers may be missing.

### Rebuild per environment

Staging evidence no longer applies to production bytes.

### Cleanup by tag only

Untagged deployed digest may be deleted.

### Delete tag as revocation

Running/mirrored content remains usable.

## 17. Kontrolné otázky

1. How locator, version and digest differ?
2. What forms exact registry subject?
3. What login success proves?
4. How to verify multi-platform graph?
5. How write-once collision is handled?
6. What generic package upload does not prove?
7. Why evidence binds digest?
8. How build-once promotion is verified?
9. What happened in `GL-PAY-74`?
10. Why cleanup deleted needed artifact?
11. How revocation differs from deletion?
12. What second-registry/platform test proves?

## Glossary impact

Relevantné pojmy: Container Registry, Package Registry, registry subject, package coordinate, image index digest, platform manifest digest, write-once version, publication identity, registry collision, evidence referrer, build-once promotion, dependency confusion, cleanup policy, deployed digest and revocation.

## Primárne zdroje

- [GitLab Container Registry](https://docs.gitlab.com/user/packages/container_registry/)
- [GitLab Package Registry](https://docs.gitlab.com/user/packages/package_registry/)
- [GitLab Generic packages API](https://docs.gitlab.com/user/packages/generic_packages/)
- [OCI Image Specification](https://github.com/opencontainers/image-spec)
- [OCI Distribution Specification](https://github.com/opencontainers/distribution-spec)
- [Sigstore Cosign documentation](https://docs.sigstore.dev/cosign/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Artifacts a cache](artifacts-and-cache.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Environments, deployments a releases →](environments-deployments-releases.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
