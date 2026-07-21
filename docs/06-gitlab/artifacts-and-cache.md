# Artifacts a cache

GitLab artifacts a cache ukladajú súbory vytvorené počas CI/CD jobov, ale majú rozdielny účel. Artifact je identifikovateľný výstup pipeline a môže byť súčasťou correctness, test evidence alebo release procesu. Cache je odstrániteľná performance optimalizácia.

## 1. Základný rozdiel

```text
artifact
→ výstup konkrétneho jobu/pipeline
→ testovanie, report, distribúcia alebo deployment

cache
→ znovupoužiteľné dependency/intermediate dáta
→ zrýchlenie rovnakých alebo budúcich jobs
```

Pipeline musí zostať korektná pri cache miss. Bez požadovaného artifactu môže byť downstream job nekorektný.

## 2. Job artifacts

Job môže publikovať súbory:

```yaml
build:
  script:
    - ./build.sh
  artifacts:
    name: "app-$CI_COMMIT_SHA"
    paths:
      - dist/
    expire_in: 14 days
```

Artifact paths sú relatívne k project working directory.

## 3. Artifact use cases

Artifacts sú vhodné pre:

- compiled binaries,
- packages,
- test reports,
- coverage reports,
- SBOM,
- security scan reports,
- generated documentation,
- Terraform plan,
- deployment manifest,
- failure diagnostics.

Nie každý artifact je release artifact. Test screenshot môže byť diagnostický artifact s krátkou retention.

## 4. Report artifacts

GitLab vie interpretovať špecifické report formats a zobraziť výsledky v pipeline alebo merge request UI.

Príklady:

- JUnit,
- coverage,
- code quality,
- dotenv,
- SAST,
- DAST,
- dependency scanning,
- container scanning,
- CycloneDX SBOM.

Report artifact má strojový contract. Nevalidný report môže spôsobiť chýbajúce alebo neúplné UI výsledky.

## 5. Artifact transfer

Bez explicitného obmedzenia môžu jobs v neskorších stages sťahovať artifacts z predchádzajúcich stages.

Presnejší model:

```yaml
test:
  needs:
    - job: build
      artifacts: true
```

Výhody explicitného transferu:

- menší network a disk cost,
- jasná dependency,
- menšie riziko filename collision,
- rýchlejší DAG execution.

## 6. Artifact naming

Názov má obsahovať relevantnú identity:

- project/component,
- version,
- commit SHA alebo digest,
- platform/architecture,
- build variant.

Nepoužívaj samotné `latest` ako jedinú identity.

## 7. Retention

Definuj retention podľa účelu:

- krátka pre transient test diagnostics,
- stredná pre audit a release candidates,
- dlhšia alebo samostatný registry pre release artifacts,
- compliance retention podľa policy.

`expire_in` znižuje storage debt, ale nesmie odstrániť jediný recovery artifact pred koncom support alebo rollback window.

## 8. Latest successful artifacts

GitLab môže zachovávať artifacts z najnovšieho úspešného pipeline pre ref aj pri expiration policy. To je praktické, ale môže zvyšovať storage usage.

Storage policy musí zohľadniť:

- počet branches,
- artifact size,
- pipeline frequency,
- retention overrides,
- stale refs.

## 9. Artifact access

Citlivé artifacts obmedz podľa role a workflowu. Artifact môže obsahovať:

- source map,
- scan findings,
- infrastructure plan,
- test data,
- debug dump,
- internal endpointy.

Artifact access control nenahrádza odstránenie secrets z obsahu.

## 10. Artifact integrity

Pre release-relevantné artifacts zachovaj:

- checksum alebo digest,
- provenance,
- signature podľa assurance modelu,
- source commit,
- builder identity,
- dependency metadata,
- pipeline/job identity.

Job artifact archive s mutable názvom nie je dostatočná release identity.

## 11. Cache

Cache sa zapína explicitne:

```yaml
cache:
  key:
    files:
      - package-lock.json
  paths:
    - .npm/
```

Cache je vhodná pre downloaded dependencies alebo drahé intermediate dáta, ktoré možno bezpečne znovu vytvoriť.

## 12. Cache key

Cache key musí reprezentovať všetky compatibility-relevantné inputs:

- OS,
- architecture,
- runtime/toolchain version,
- lockfile hash,
- build flags,
- dependency source,
- security/trust namespace.

Príklad:

```yaml
cache:
  key: "$CI_JOB_NAME-$CI_COMMIT_REF_SLUG"
```

Per-branch key znižuje cross-branch contamination, ale prvý pipeline branchu bude cold.

## 13. Content-based keys

`cache:key:files` alebo ekvivalentný content-derived key automaticky invaliduje cache pri zmene dependency lockfile.

Pozor na inputs mimo lockfile:

- compiler version,
- OS packages,
- environment variables,
- feature flags,
- package registry configuration.

## 14. Cache policy

Jobs môžu podľa konfigurácie cache:

- pull,
- push,
- pull-push.

Bezpečný pattern:

- trusted default-branch job publikuje shared cache,
- feature jobs cache primárne čítajú alebo používajú oddelený namespace,
- untrusted fork nesmie poisonovať trusted cache.

## 15. Protected a non-protected cache

GitLab štandardne oddeľuje cache pre protected a non-protected refs, ak konfigurácia neurčí inak.

Toto oddelenie zachovaj, keď protected jobs používajú citlivejší build alebo release workflow.

## 16. Distributed cache

Pri viacerých alebo autoscaled runners potrebuje cache shared backend, napríklad object storage.

Treba riadiť:

- credentials,
- bucket isolation,
- encryption,
- lifecycle rules,
- egress a latency,
- concurrency,
- stale objects,
- cache poisoning.

## 17. Cache correctness

Pipeline musí vedieť zvládnuť:

- cache miss,
- partial cache,
- stale cache,
- corrupt cache,
- eviction,
- backend outage.

Najlepší test cache correctness je občasný clean pipeline bez cache.

## 18. Cache poisoning

Útočník alebo chybný job môže uložiť škodlivé dependencies alebo build outputs pod key, ktorý neskôr použije trusted job.

Ochrany:

- oddelený trust namespace,
- immutable dependency verification,
- checksums/signatures,
- restricted push policy,
- protected runner/cache,
- content-derived key,
- clean release builds.

## 19. Artifacts vs. package registry

Job artifacts sú viazané na pipeline/job lifecycle. Dlhodobo spotrebovávaný package alebo release binary patrí skôr do package, container alebo generic registry.

Registry poskytuje:

- versioned distribution,
- dependency consumption,
- release-oriented retention,
- package-manager protocol,
- oddelenie od pipeline UI.

## 20. Failure artifacts

Pri neúspechu zachovaj podľa potreby:

```yaml
artifacts:
  when: always
  paths:
    - test-results/
    - screenshots/
  reports:
    junit: test-results/junit.xml
```

Failure artifact nemá obsahovať secrets alebo kompletný production dataset.

## 21. Artifact collision

Parallel jobs môžu vytvoriť rovnaké filename a downstream download ich prepíše.

Použi:

- unique artifact names,
- per-shard directories,
- aggregation job,
- explicitné `needs`,
- validation completeness.

Aggregation musí zlyhať pri chýbajúcom sharde.

## 22. Storage governance

Sleduj:

- artifact storage podľa projektu,
- average artifact size,
- cache storage,
- expiration effectiveness,
- orphan/stale data,
- download traffic,
- cache hit rate,
- failure artifact retention.

Neobmedzené `artifacts:untracked` a dlhá retention sú častý zdroj nákladov.

## 23. Troubleshooting

### `No files to upload`

Path je nesprávny, súbor nevznikol alebo job pracuje v inom directory.

### Downstream job nemá artifact

Over stage/DAG, `needs:artifacts`, `dependencies`, expiration a upstream success.

### Artifact z parallel jobu sa prepísal

Použi unique paths/names a explicitnú aggregáciu.

### Cache sa nikdy nepoužije

Over key, runner/backend sharing, architecture, policy a path.

### Cache spôsobuje náhodné build chyby

Spusti clean build, zmeň namespace, over dependency integrity a všetky key inputs.

### Storage rastie

Over latest-success retention, expiration, stale refs, report size a cache lifecycle.

## 24. Kontrolné otázky

1. Aký je rozdiel medzi artifactom a cache?
2. Kedy použiť report artifact?
3. Ako `needs:artifacts` mení transfer?
4. Čo musí obsahovať release artifact identity?
5. Ako navrhnúť retention podľa účelu?
6. Ktoré inputs patria do cache key?
7. Ako vzniká cache poisoning?
8. Prečo pipeline musí fungovať bez cache?
9. Kedy presunúť výstup do package registry?
10. Ako riešiť artifacts z parallel shards?

## Glossary impact

Relevantné pojmy: GitLab job artifact, report artifact, artifact retention, artifact access, GitLab cache, cache policy, distributed cache, cache key, cache poisoning a latest successful artifact.

## Oficiálna dokumentácia

- [Job artifacts](https://docs.gitlab.com/ci/jobs/job_artifacts/)
- [Caching in GitLab CI/CD](https://docs.gitlab.com/ci/caching/)
- [CI/CD YAML syntax](https://docs.gitlab.com/ci/yaml/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Variables a secrets](variables-and-secrets.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Container a package registry →](container-and-package-registry.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
