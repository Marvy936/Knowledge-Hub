# Artifacts a cache

GitLab job artifact je identifikovateľný output konkrétneho pipeline execution subjectu. Môže niesť build bytes, test report, deployment plan, dotenv values, SBOM alebo provenance. Cache je odstrániteľný performance state. Pipeline correctness musí platiť pri cache miss-e a privileged consumer nesmie slepo dôverovať cache zapísanej nižším trust contextom.

Artifact a report tiež nie sú to isté. Generic artifact môže byť archive pre downstream job. Report artifact má GitLab-defined schema a platform ho môže spracovať do merge-request widgetu, vulnerability recordu, coverage alebo test UI. Successful upload generic file-u pod report filename nepreukazuje, že GitLab report parse-ol a použil.

## 1. Dominantný job-output model

Model má dve vetvy s odlišnou autoritou. Artifact/report branch prenáša identifikované bytes alebo evidence, ktoré downstream consumer musí overiť; cache branch prenáša odstrániteľný performance state, ktorého miss alebo eviction nesmie zmeniť correctness. Nasledujúci diagram preto nie je iba workflow, ale trust a retention contract.

```text
exact pipeline/job/artifact subject
→ output creation and local validation
→ checksum/provenance and artifact/report declaration
→ upload acknowledgement
→ GitLab storage/processing/access/retention
→ explicit downstream transfer
→ consumer subject validation
→ release/evidence use or expiration

cache branch:
job inputs/trust namespace
→ cache key and fallback policy
→ restore/validate or miss/recompute
→ optional bounded save
→ eviction without correctness change
```

## 2. Exact output subject

Output sa nedá identifikovať iba filename-om. Exact subject viaže bytes alebo report na project, pipeline, producer job, candidate SHA, digest, schema a retention class, aby consumer vedel odmietnuť output z iného execution contextu. YAML nižšie je lineage envelope pre build aj evidence outputs.

```yaml
outputSubject:
  projectId: 481
  pipelineId: 771184
  jobId: 881911
  candidateSha: d94e1c6
  artifactDigest: sha256:pay1000api
  outputs:
    build:
      path: dist/payments-api.tar.gz
      sha256: build1000
      type: generic-artifact
    junit:
      path: reports/junit.xml
      type: junit-report
      schemaGeneration: junit-supported-1
    sbom:
      path: reports/gl-sbom.cdx.json
      type: cyclonedx-report
      subjectDigest: sha256:pay1000api
  retentionClass: release-candidate-30d
```

Pipeline/job IDs, candidate a artifact digest spájajú bytes/evidence s execution. Filename bez digest/provenance môže byť overwritten alebo pochádzať z wrong job.

## 3. Artifact creation and checksum

Creation step najprv stabilizuje bytes a potom vytvorí samostatný integrity claim. Deterministic archive znižuje rozdiely spôsobené časom a ownership metadata; checksum následne umožní producerovi aj consumerovi porovnať presný byte stream. Ani jeden krok však sám nedokazuje, z akého source-u artifact vznikol alebo kto manifest autorizoval.

```bash
tar --sort=name --mtime='UTC 1970-01-01' \
  --owner=0 --group=0 --numeric-owner \
  -czf dist/payments-api.tar.gz build/
sha256sum dist/payments-api.tar.gz > dist/payments-api.tar.gz.sha256
sha256sum --check dist/payments-api.tar.gz.sha256
```

Checksum match preukazuje local byte equality. Nepreukazuje source/build provenance, safe archive paths ani GitLab upload/storage integrity. Consumer rechecks checksum from trusted manifest.

## 4. Artifact declaration and transfer

GitLab YAML deklaruje, ktoré paths má producer uploadnúť a ktorý consumer ich má cez DAG dostať. Toto je transfer intent, nie read-back uploadu ani autentifikácia obsahu. Consumer preto kontroluje producer identity, checksum/provenance a vlastný expected candidate pred použitím artifactu.

```yaml
build:
  stage: build
  script:
    - ./scripts/build.sh
  artifacts:
    name: "payments-${CI_COMMIT_SHA}"
    paths:
      - dist/payments-api.tar.gz
      - dist/payments-api.tar.gz.sha256
    expire_in: 30 days

verify:
  stage: test
  needs:
    - job: build
      artifacts: true
  script:
    - sha256sum --check dist/payments-api.tar.gz.sha256
    - ./scripts/test-artifact.sh dist/payments-api.tar.gz
```

YAML preukazuje intended upload and DAG transfer. Nepreukazuje upload completion, correct checksum authority ani test coverage. Job/API artifact metadata and consumer logs complete evidence.

## 5. Report artifacts and processing

```yaml
unit_tests:
  artifacts:
    when: always
    reports:
      junit: reports/junit.xml
    paths:
      - reports/junit.xml
```

`when: always` preserves report after test failure, but job status still depends on script exit. Upload success does not prove report schema validity or GitLab ingestion. Merge gate should distinguish job outcome, report presence and processing errors.

Security reports need expected analyzer inventory. If analyzer job fails before report creation, absence is `INCOMPLETE`, not no findings.

## 6. Artifact access and trust

Artifact download authorization may depend on project visibility, role, job token and access setting. Public/reporter-visible artifacts must not contain secrets, internal endpoints or unredacted logs. Protected pipeline artifact is not automatically inaccessible to every lower role.

Downstream jobs treat untrusted artifacts as data. Archive extraction protects path traversal/symlinks and privileged jobs do not execute embedded scripts without review/signature.

## 7. Retention and release authority

Pipeline artifacts may expire. Durable release artifacts belong in package/container registry or immutable object store with release manifest and support retention. GitLab Release can link assets, but expiring job URL is not durable release identity.

Retention classes reflect audit, regulatory, support and recovery requirements. Last-known-good artifact cannot expire before tested recovery replacement exists.

## 8. Cache key and namespace

```yaml
cache:
  key:
    files:
      - package-lock.json
    prefix: "npm-${CI_RUNNER_EXECUTABLE_ARCH}-node22-v3"
  paths:
    - .npm/
  policy: pull-push
```

Key intent includes lockfile and runtime dimensions. Nepreukazuje complete inputs, immutable entry or trust-safe writer. Protected/unprotected and fork/trusted caches should be separated; privileged release job can use `pull` from trusted namespace, not fallback to arbitrary untrusted prefix.

## 9. Cache poisoning

Cache can contain generated code, compiler outputs, executable scripts or symlinks. If untrusted MR writes key later restored by protected build, cache becomes supply-chain bridge.

Safe model:

```text
untrusted jobs
→ isolated or read-only cache namespace

trusted build
→ exact key, no broad fallback from untrusted writers
→ validate restored content
→ periodic cold build
```

Cache must never carry production credentials, signed release outputs or authoritative security reports.

## 10. Distributed cache and unknown state

Object-store upload timeout may leave cache present or absent. Correctness cannot depend on save acknowledgement. Artifact upload timeout is different: required output may make pipeline incomplete and needs read-back/retry with subject identity.

Cache eviction should affect duration only. If cold build fails, dependency declaration is incomplete.

## 11. `needs` and artifact lineage

Explicit `needs` limits which job outputs consumer receives and enables DAG execution. Broad downloading artifacts from all previous stages can mix outputs from unrelated jobs or names.

Consumer verifies artifact manifest:

```bash
jq -e --arg expected "$CI_COMMIT_SHA" '
  .candidateSha == $expected and
  .artifactDigest == "sha256:pay1000api"
' artifact-manifest.json
```

Predicate proves fields in manifest. It does not authenticate manifest; producer provenance/signature is still needed.

## 12. Connected incident `GL-PAY-74`

Fork MR job wrote generated client to shared cache key based only on `package-lock.json`. Protected tag pipeline restored cache, built and signed image. Unit test job uploaded JUnit XML, but arm64 compatibility job failed before report creation. Final gate read only present reports and declared complete success.

```text
untrusted cache write
→ trusted restore
→ compromised artifact
+ missing report interpreted as no failure
→ signed registry publication
```

Release artifact ZIP expired after seven days, so incident team could not reproduce original build inputs. Root cause was artifact/report/cache authority and retention, not one bad job.

## 13. Containment, recovery and acceptance

Containment blocks cache namespace, preserves object metadata/job artifacts, revokes affected digest and stops deployments. Recovery cold-builds from pinned inputs, requires static expected report inventory and publishes durable release subject.

Artifact/cache model is accepted only when:

```text
outputs carry exact pipeline/job/candidate/artifact subject
+ checksum/provenance is verified by consumer
+ report presence and GitLab processing are explicit
+ missing report is incomplete, not pass
+ artifact access/retention match classification
+ release artifacts are durable and immutable
+ cache key/input/trust namespace is bounded
+ cache miss preserves correctness
+ forbidden untrusted-cache-to-trusted-build path is tested
+ second cold build produces same contract outcome
```

## 14. Troubleshooting flow

Artifact incident sa lokalizuje po jednom transitione: vznik lokálneho outputu, upload, platform processing, retention/access a downstream download. Cache sa analyzuje oddelene podľa key-u, writer trustu a restore pathu, pretože cache hit nie je lineage evidence. Takýto ordering odlíši missing report od cache poisoning alebo expirovaného artifactu.

```text
producer job subject
→ local output/checksum
→ artifact/report declaration
→ upload/storage/processing
→ access/retention
→ needs/download consumer
→ cache key/writer/restore
→ release/runtime use
```

Competing hypotheses include upload failure, invalid report, wrong artifact name, expired output, job-token denial, cache fallback, poisoning, stale runner workspace or incomplete fan-in.

## 15. Anti-patterny

### Cache as job output

Cache je best-effort performance state s eviction a fallback semantics. Neposkytuje required hand-off, retention ani producer lineage, preto correctness nesmie závisieť od cache hitu. Required output sa prenáša artifactom alebo registry subjectom a testuje sa cold run.

### Generic artifact as processed report proof

Generic archive môže obsahovať file s názvom reportu, ale GitLab ho nemusí parse-nuť podľa report schema ani pripojiť k MR/security evidence. Upload acknowledgement preto nie je processing verdict. Gate kontroluje report declaration, schema, ingestion status a expected producer identity.

### Missing analyzer report equals zero findings

Chýbajúci report neobsahuje tvrdenie „zero findings“; znamená, že očakávané pozorovanie nevzniklo. Analyzer mohol byť omitted rules, crashnúť alebo zlyhať pred uploadom. Fan-in porovnáva static expected inventory s valid received reports a pri rozdiele vracia `INCOMPLETE`.

### Release asset linked to expiring job artifact

Expiring job artifact môže zmiznúť počas support alebo incident window-u a jeho URL nie je immutable release identity. Release manifest má odkazovať na durable package/container/object subject s vlastnou retention a checksum/provenance. Job artifact môže zostať krátkodobou evidence kópiou, nie jediným release byte source-om.

### Broad cache fallback across trust classes

Fallback key, ktorý prepája fork alebo untrusted MR writera s protected build consumerom, mení cache na supply-chain bridge. Privileged job môže restore-núť generated code alebo executable state, ktoré nikdy nevytvoril trusted producer. Cache namespace, writer policy a consumer validation musia zachovať jednosmerný trust.

## 16. Kontrolné otázky

1. How artifact, report and cache differ?
2. What forms exact output subject?
3. What checksum proves and does not prove?
4. How `needs` changes artifact lineage?
5. Why upload success is not report-processing proof?
6. How missing reports are classified?
7. Why release artifact needs durable registry?
8. How cache key and namespace relate to trust?
9. What happened in `GL-PAY-74`?
10. How forbidden cache poisoning path is tested?
11. What retention is required for recovery?
12. What cold second build proves?

## Glossary impact

Relevantné pojmy: job artifact, generic artifact, report artifact, artifact subject, checksum, artifact lineage, artifact processing, artifact access, artifact retention, release artifact, cache key, cache namespace, fallback key, distributed cache, cache poisoning and cold build.

## Primárne zdroje

- [GitLab Docs — Job artifacts](https://docs.gitlab.com/ci/jobs/job_artifacts/)
- [GitLab Docs — Job artifact reports](https://docs.gitlab.com/ci/yaml/artifacts_reports/)
- [GitLab Docs — Caching](https://docs.gitlab.com/ci/caching/)
- [GitLab Docs — Job token](https://docs.gitlab.com/ci/jobs/ci_job_token/)
- [SLSA specification](https://slsa.dev/spec/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Variables a secrets](variables-and-secrets.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Container a package registry →](container-and-package-registry.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
