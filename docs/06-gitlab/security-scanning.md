# Security scanning

GitLab security scanning je evidence a risk-decision systém. Scanner sám o sebe nevytvára bezpečnostný verdict. Dôveryhodný lifecycle musí vedieť, ktoré analyzers a subjects boli očakávané, čo sa skutočne analyzovalo, akú schema a producer generation report používa, ako GitLab evidence spracoval, ako sa finding kontextualizoval a či vulnerable artifact reálne beží.

„Security pipeline passed“ môže znamenať, že analyzers nevytvorili blocking findings. Môže však znamenať aj to, že analyzer job nevznikol pre `rules`, image sa nedala stiahnuť, report bol invalidný, scan použil source namiesto final artifactu alebo finding bol dismissed bez revocation. Absence findings je významná iba pri complete expected scanner inventory a valid subject-bound reports.

## 1. Dominantný attack-surface-to-runtime model

```text
attack surface and change-risk model
→ exact source/artifact/configuration/deployed subjects
→ expected analyzer and report inventory
→ analyzer execution with trusted version/config
→ report schema/integrity/subject validation
→ GitLab ingestion and finding correlation
→ contextual risk, exception or remediation decision
→ fixed artifact verification
→ deployed-digest and secret-revocation closure
→ continuous rescanning and runtime inventory
```

Different scanners answer different questions. SAST does not scan container packages, dependency scan does not prove runtime reachability, secret detection does not revoke leaked key and DAST does not cover every authenticated workflow.

## 2. Exact scan subject

```yaml
scanSubject:
  projectId: 481
  pipelineId: 771184
  candidateSha: d94e1c6
  releaseManifestDigest: sha256:release1000rc4
  artifacts:
    apiIndexDigest: sha256:pay1000api
    migrationDigest: sha256:mig1000
  configurationSha: 71ac290
  deployedTargets:
    productionEu: sha256:pay993
  expectedAnalyzers:
    - sast
    - dependency-scanning
    - secret-detection
    - container-scanning-amd64
    - container-scanning-arm64
    - iac-scanning
    - api-dast
  policyBundleSha: security-policy-66
```

Candidate/source and artifact/runtime subjects are separate. A source fix is not production remediation until fixed digest is deployed and vulnerable digest removed/revoked.

## 3. Expected analyzer inventory

Expected analyzers derive from attack surface and changes, not from jobs that happened to appear. Example:

```json
{
  "expected": [
    "sast",
    "dependency-scanning",
    "secret-detection",
    "container-scanning-amd64",
    "container-scanning-arm64",
    "iac-scanning",
    "api-dast"
  ],
  "received": [
    "sast",
    "dependency-scanning",
    "secret-detection",
    "container-scanning-amd64",
    "iac-scanning"
  ]
}
```

```bash
jq -e '(.expected | sort) == (.received | sort)' scanner-inventory.json
```

Mismatch proves missing/extra IDs in the JSON. It does not prove report validity or analyzer success. Missing arm64 and DAST evidence is `INCOMPLETE`, not clean.

## 4. Analyzer and report generation

GitLab security templates/components can create analyzer jobs and report artifacts. Exact behavior depends on GitLab/analyzer version and configuration. Pinning supported versions and recording image digest improve reproducibility.

```yaml
container_scanning:
  variables:
    CS_IMAGE: "$CI_REGISTRY_IMAGE@sha256:pay1000api-amd64"
  artifacts:
    reports:
      container_scanning: gl-container-scanning-report.json
```

YAML proves intended artifact input/report declaration. It does not prove analyzer processed correct platform manifest, report schema validity or GitLab ingestion.

## 5. Report validation and processing

Security report needs supported schema, scan metadata, analyzer identity, subject/location and findings. Generic JSON with same filename is not enough.

```bash
jq -e '
  .version != null and
  .scan.analyzer.id != null and
  .scan.scanner.id != null and
  (.vulnerabilities | type == "array")
' gl-container-scanning-report.json
```

Predicate validates selected fields locally. It does not guarantee full GitLab schema or ingestion. Job logs and MR/security UI/API processing status complete evidence.

## 6. SAST and code models

SAST finds patterns/data flows in source or compiled representation. It can have false positives/negatives and language/framework coverage limits. Result applies to source/candidate and analyzer configuration, not final container unless build lineage is proven.

Generated/vendor code exclusions can hide attack surface. Exclusion policy is reviewed and visible in evidence.

## 7. Dependency and container scanning

Dependency scan uses manifests/lockfiles/package inventories. Container scan should scan exact image digest and all supported platforms. Index-level scan that resolves only local architecture can miss arm64 packages.

SBOM improves inventory but vulnerability matching still depends on package identity, database freshness and exploitability context. Scan time and database generation are evidence fields.

## 8. Secret detection and revocation

Secret finding is not closed by deleting value from latest commit. Git history, forks, artifacts, caches, logs and local clones may retain it. Most importantly, target provider credential must be revoked/rotated and descendants invalidated.

```text
secret detected
→ preserve evidence and identify authority/target
→ revoke target credential/session
→ rotate and update consumers
→ remove/prevent copies as appropriate
→ test old credential forbidden
→ validate new second operation
```

History rewrite can reduce exposure but has coordination/audit consequences and does not revoke secret.

## 9. IaC and configuration scanning

IaC scan evaluates source/rendered configuration according to rules. Source Terraform or Helm values may differ from resolved plan/render/admitted/live state. Security gate should know which layer report describes.

Policy finding over source does not prove runtime vulnerable; runtime misconfiguration can also exist despite clean source due drift or admission/defaults. Effective-state read-back is needed for high-risk controls.

## 10. DAST and API coverage

DAST executes requests against deployed target and observes responses. It needs exact environment/release, authentication role, API inventory, data safety and cleanup. Unauthenticated scan may miss privileged paths; broad production scan can create harmful side effects.

DAST success proves tested endpoints/payloads in window, not complete application security. API schema and critical journey inventory define expected coverage.

## 11. Vulnerability decision

Finding decision includes severity, confidence, reachability, affected subject, environment exposure, compensating controls, owner and remediation SLA. Dismissal requires reason and evidence; it does not erase raw finding.

Exception is scoped to digest/version/environment and expires. New artifact does not inherit exception automatically if dependencies or reachability changed.

## 12. Merge and deployment policies

Merge gate may block new critical findings or incomplete scans. Deployment gate should validate artifact-bound evidence and current vulnerability policy. Source branch scan alone is insufficient if release artifact rebuilt or mutable tag changed.

Security policy enforcement must cover normal, manual, scheduled, API and emergency deployment paths.

## 13. Remediation closure

Closure states:

```text
source fixed
→ candidate verified
→ fixed immutable artifact built/scanned/signed
→ fixed artifact deployed to affected environment
→ runtime digest read-back
→ vulnerable digest removed/revoked
→ business/security control validation
```

For secret, include target revocation and consumer reload. For package CVE, include all platform manifests and old Pod/node cache cohorts.

## 14. Connected incident `GL-PAY-74`

Atlas analyzer job for arm64 failed on infrastructure timeout and produced no report. Expected inventory was built from received reports, so gate passed. Secret detection found provider key in generated artifact, but finding was dismissed after source file deletion; provider key remained active.

Default branch then built fixed code, but production GitOps controller failed and runtime stayed on vulnerable digest. GitLab dashboard showed MR security clean, vulnerability dismissed and Release fixed.

```text
missing analyzer report treated as no finding
+ secret dismissal without revocation
+ source fix without deployed-digest correlation
→ false security closure
```

Attacker used old provider key for 37 minutes; production arm64 still ran vulnerable native library.

## 15. Containment, recovery and acceptance

Containment blocks releases, preserves analyzer/report/ingestion/audit data, revokes secret/provider sessions and inventories runtime digests. Recovery rebuilds/scans all platforms, deploys fixed digest, verifies runtime and removes affected artifact.

Security scanning is accepted only when:

```text
attack surface and expected analyzers are explicit
+ all reports are present, valid, processed and subject-bound
+ source/artifact/config/runtime layers are distinguished
+ all platform manifests and critical paths are covered
+ findings retain raw evidence and scoped decisions
+ secret closure includes provider revocation and old-key forbidden test
+ fixed artifact is verified and deployed
+ vulnerable runtime digest is removed/revoked
+ alternate deploy paths enforce policy
+ continuous rescan/second operation confirms closure
```

## 16. Troubleshooting flow

```text
expected analyzer inventory
→ job/rules/runner execution
→ analyzer image/config/database generation
→ report creation/schema/upload/processing
→ finding correlation/decision
→ artifact/release/deployment subject
→ runtime digest/credential state
→ remediation closure
```

Competing hypotheses include job absent, tool failure, invalid report, unsupported language, wrong image/platform, stale vulnerability DB, broad exclusion, source/artifact mismatch, dismissal or deployment drift.

## 17. Anti-patterny

### Successful analyzer job equals valid evidence

Report may be missing/invalid/unprocessed.

### No report equals no findings

It is incomplete coverage.

### Source scan equals artifact scan

Build can add packages/generated content.

### Secret removed from Git equals revoked

Target credential and copies remain.

### Fixed main equals fixed production

Runtime may still use vulnerable digest.

## 18. Kontrolné otázky

1. What forms exact scan subject?
2. How expected analyzer inventory is determined?
3. What report validation proves?
4. Why source and artifact scans differ?
5. How multi-platform images affect container scanning?
6. What closes secret finding?
7. How IaC source and effective state differ?
8. What DAST proves and does not prove?
9. What happened in `GL-PAY-74`?
10. How fixed artifact deployment is verified?
11. How alternate deployment paths are covered?
12. What continuous rescanning adds?

## Glossary impact

Relevantné pojmy: security analyzer, expected analyzer inventory, security report, report processing, scan subject, SAST, dependency scanning, container scanning, secret detection, IaC scanning, DAST, vulnerability decision, security exception, artifact-bound evidence, deployed-digest correlation, credential revocation and remediation closure.

## Primárne zdroje

- [GitLab Docs — Application security](https://docs.gitlab.com/user/application_security/)
- [GitLab Docs — Security scanner integration](https://docs.gitlab.com/development/integrations/secure/)
- [GitLab Docs — Security report schemas](https://gitlab.com/gitlab-org/security-products/security-report-schemas)
- [GitLab Docs — Secret detection](https://docs.gitlab.com/user/application_security/secret_detection/)
- [GitLab Docs — Container scanning](https://docs.gitlab.com/user/application_security/container_scanning/)
- [GitLab Docs — DAST](https://docs.gitlab.com/user/application_security/dast/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Environments, deployments a releases](environments-deployments-releases.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: GitLab troubleshooting →](gitlab-troubleshooting.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
