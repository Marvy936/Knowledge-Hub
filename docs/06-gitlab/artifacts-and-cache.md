# Artifacts a cache

## Metadata

- Status: Learning
- Level: L2
- Domain: GitLab

GitLab artifacts a cache prenášajú súbory medzi jobmi a behmi pipeline, ale majú odlišný kontrakt. Artifact je identifikovateľný výstup konkrétneho execution subjectu a môže byť dôkazom, build outputom alebo release kandidátom. Cache je odstrániteľný a potenciálne nedôveryhodný performance state, ktorý musí byť možné bezpečne znovu vytvoriť.

## 1. Mental model

```text
artifact
→ producer job a pipeline identity
→ konkrétny output alebo evidence
→ explicitný consumer
→ retention / promotion / audit

cache
→ compatibility key a trust namespace
→ opportunistic restore
→ validation
→ use
→ optional write-back
→ eviction
```

Ak cache miss alebo eviction zmení correctness, daný obsah nie je cache, ale chýbajúci artifact alebo dependency source.

## 2. Artifact subject

Artifact má byť viazaný minimálne na:

- project,
- pipeline ID a source,
- commit alebo merged-result SHA,
- job name a attempt,
- build variant,
- platform/architecture,
- producer configuration revision,
- obsahový digest podľa významu.

Názov archive súboru je iba presentation. Subject identity musí umožniť určiť, čo artifact vytvorilo a na aký source/evidence sa vzťahuje.

## 3. Typy artifacts

Rozlišuj:

- **Build artifact —** binary, bundle alebo iný výstup build-u.
- **Report artifact —** strojovo interpretovaný výsledok testu, coverage alebo scanneru.
- **Evidence artifact —** plan, manifest, SBOM, provenance alebo audit packet.
- **Diagnostic artifact —** logs, dump, screenshot alebo trace pre troubleshooting.
- **Deployment artifact —** manifest alebo package použitý deploy jobom.
- **Release artifact —** dlhšie podporovaný immutable výstup publikovaný do registry alebo release lifecycle.

Nie každý job artifact je vhodný ako release artifact.

## 4. Publication contract

Producer má definovať:

- presné paths,
- podmienku uploadu,
- artifact name,
- format,
- digest/checksum podľa potreby,
- retention,
- access,
- consumer inventory,
- obsah, ktorý je zakázaný.

Použitie celého workspace alebo `untracked` zvyšuje riziko secrets, nepotrebných súborov a nepredvídateľnej veľkosti.

## 5. Upload pri success a failure

Artifacts môžu byť potrebné aj pri neúspechu:

```yaml
artifacts:
  when: always
  paths:
    - test-results/
    - screenshots/
  reports:
    junit: test-results/junit.xml
```

Failure artifact má pomáhať diagnostike, ale nesmie obsahovať production dataset, credentials alebo neobmedzený memory dump bez review.

## 6. Report artifacts

GitLab interpretuje report formats, napríklad JUnit, coverage, code quality, dotenv, security reports a SBOM.

Report pipeline potrebuje rozlíšiť:

- report bol vytvorený a validný,
- report je validný, ale obsahuje findings/failures,
- report chýba,
- report je neúplný,
- parser/analyzer zlyhal,
- report patrí inému subjectu.

Chýbajúci security alebo test report nie je „nula findings“.

## 7. Report completeness

Pri parallel/sharded jobs potrebuje aggregation vedieť expected inventory:

```text
expected shards: 1..8
received: 1,2,3,4,5,7,8
→ incomplete evidence
```

Aggregation job má zlyhať alebo vrátiť explicitný incomplete verdict, ak chýba povinný shard, platforma alebo component.

## 8. Producer-consumer binding

Downstream job nemá sťahovať všetky artifacts z predchádzajúcich stages implicitne. Explicitný DAG transfer:

```yaml
test:
  needs:
    - job: build
      artifacts: true
```

Consumer má overiť:

- správneho producer joba,
- pipeline a commit identity,
- variant/platformu,
- digest alebo manifest,
- completeness,
- expiration/access.

Filename collision nesmie rozhodovať o tom, ktorý output sa použije.

## 9. `needs`, `dependencies` a stages

`needs` definuje execution dependency a môže explicitne preniesť artifacts. `dependencies` obmedzuje artifact download v stage modeli.

Pri DAG pipeline preferuj čitateľný `needs` graph. Kombinácia viacerých mechanizmov bez jasného modelu môže:

- stiahnuť nesprávne artifacts,
- skryť chýbajúcu dependency,
- blokovať job zbytočnou stage barrier,
- vytvoriť race pri optional jobe.

## 10. Child a downstream pipelines

Artifact transfer medzi parent, child a multi-project pipeline potrebuje explicitný contract:

- upstream pipeline/project identity,
- artifact subject a digest,
- job a attempt,
- access token alebo job-token policy,
- retention dostatočnú pre downstream,
- status propagation,
- ochranu pred zamenením branch artifactu za release artifact.

Pipeline ID alebo ref `main` bez digestu môže po čase ukazovať na iný output.

## 11. Artifact naming

Human-friendly name môže obsahovať:

- component,
- version,
- commit SHA,
- platform,
- build variant,
- pipeline ID.

Názov `app-latest.zip` neposkytuje immutable identity. Pre correctness používaj digest a release manifest.

## 12. Artifact integrity a provenance

Release-relevantný artifact má byť prepojený s:

- content digestom,
- source commitom,
- resolved pipeline configuration,
- builder/runner identity,
- toolchain a dependency inputs,
- SBOM,
- provenance attestation,
- signature alebo verification policy podľa assurance modelu.

Checksum dokazuje, že obsah sa nezmenil. Nedokazuje, že bol vytvorený dôveryhodným buildom.

## 13. Artifact access

Artifact môže obsahovať interné alebo citlivé informácie:

- source maps,
- scanner findings,
- Terraform plan,
- debug logs,
- test data,
- topology a endpointy.

Access policy má zodpovedať obsahu. Zároveň platí, že access control nenahrádza odstránenie secrets z artifactu.

## 14. Retention lifecycle

Retention navrhni podľa purpose:

- krátka pre transient diagnostics,
- stredná pre MR/release-candidate evidence,
- dlhšia pre audit a support,
- registry alebo durable storage pre release artifacts,
- explicitná legal/compliance retention.

Artifact použitý v produkcii alebo potrebný pre rollback nesmie zmiznúť len preto, že job `expire_in` vypršal.

## 15. Retention roots

Pred cleanupom zachovaj artifacts referencované:

- aktívnym deploymentom,
- podporovaným releaseom,
- rollback window,
- otvoreným incidentom,
- compliance/legal holdom,
- release manifestom,
- aktívnym review alebo auditom.

Latest-success retention podľa refu nie je úplný release inventory.

## 16. Promotion do registry

Dlhodobo spotrebovaný package alebo image patrí do package, container alebo generic registry.

Bezpečný flow:

```text
job artifact / build output
→ over digest a evidence
→ publish immutable registry version
→ vytvor release manifest
→ deploy alebo distribuuj registry identity
```

Promotion nemá artifact rebuildovať. Má publikovať alebo aliasovať rovnaký obsah.

## 17. Artifact collision

Parallel jobs môžu vytvoriť rovnaké názvy. Ochrany:

- per-shard directories,
- unique artifact names,
- platform suffix,
- explicitný aggregation job,
- manifest expected outputs,
- failure pri duplicate alebo missing položke.

„Posledný download prepíše súbor“ nie je deterministic merge strategy.

## 18. Artifact attempt identity

Retry joba môže vytvoriť nový output. Zachovaj:

- job attempt,
- first-attempt verdict,
- digest každého pokusu,
- policy, ktorý attempt je authoritative,
- dôvod retry.

Retry nesmie potichu nahradiť chybný report zeleným artifactom bez audit trailu.

## 19. Cache purpose

Cache je vhodná pre:

- downloaded dependencies,
- package-manager cache,
- compiler incremental state,
- precomputed intermediate dáta,
- tool downloads,
- objekty, ktoré možno overiť alebo znovu vytvoriť.

Finálny release binary, test result alebo Terraform plan nie je cache.

## 20. Cache key

Key má reprezentovať compatibility-relevantné inputs:

- OS a architecture,
- runtime/compiler/toolchain version,
- lockfile alebo dependency manifest,
- build flags,
- package source/config,
- project/component,
- trust namespace,
- prípadne ref alebo protected status.

Chýbajúci input vytvára stale alebo nekompatibilný restore.

## 21. Content-derived keys

Key odvodený z lockfile hash-u invaliduje dependencies pri jeho zmene. Stále môže chýbať:

- base image digest,
- compiler version,
- package registry URL,
- environment flag,
- build-system config,
- system library.

Cache key je compatibility contract, nie iba optimalizačný názov.

## 22. Fallback keys

Fallback key zvyšuje hit rate, ale môže rozšíriť trust alebo compatibility scope.

Príklad rizika:

```text
feature-specific cache miss
→ fallback na shared-main cache
→ obsah pochádza z iného toolchainu alebo trust contextu
```

Každý fallback musí byť bezpečný pre daný consumer a nesmie prepojiť untrusted writera s trusted readerom.

## 23. Cache policy

Rozlišuj:

- `pull` — job iba obnovuje,
- `push` — job publikuje,
- `pull-push` — obnovuje a následne zapisuje.

Bezpečný model často používa:

- trusted default-branch job ako shared writer,
- feature jobs ako readers alebo oddelení writers,
- untrusted fork bez write accessu do trusted namespace,
- release build s clean alebo read-only verified cache.

## 24. Cache write timing

Cache sa nemá publikovať z nevalidného alebo canceled jobu bez jasného dôvodu. Zápis po partial dependency install môže vytvoriť poškodený shared state.

Definuj:

- podmienku write-back,
- atomic publish alebo temporary key,
- validation pred promotion keya,
- concurrent-writer behavior,
- cleanup partial uploadu.

## 25. Protected a non-protected namespaces

Oddeľ cache podľa trustu:

- protected a non-protected refs,
- internal a fork pipelines,
- project/group boundaries,
- release a development pools,
- architecture/toolchain.

Zjednotenie namespace kvôli hit rate môže vytvoriť cache-poisoning path.

## 26. Distributed cache

Autoscaled a multi-runner pools používajú object storage alebo iný shared backend.

Riadiť treba:

- scoped credentials,
- bucket/prefix isolation,
- encryption,
- lifecycle,
- upload/download integrity,
- consistency a concurrent writers,
- size limits,
- egress a latency,
- outage behavior.

Cache backend outage nemá zablokovať correctness, ak je možné dependencies bezpečne získať z authoritative source.

## 27. Partial, stale a corrupt cache

Consumer musí zvládnuť:

- miss,
- partial archive,
- stale entries,
- corrupt download,
- eviction,
- incompatible permissions,
- backend timeout.

Po restore vykonaj primeranú validation, napríklad package checksum, manifest alebo compiler-state compatibility.

## 28. Cache poisoning

Poisoning vzniká, keď writer uloží škodlivý alebo neplatný obsah pod key, ktorý neskôr dôveruje citlivejší job.

Ochrany:

- oddelené trust namespaces,
- write restrictions,
- immutable dependency checksums/signatures,
- content-derived keys,
- pinned package sources,
- read-only cache pre release jobs,
- periodic clean builds,
- incidentné zneplatnenie namespace.

## 29. Clean-build verification

Pravidelne spúšťaj pipeline bez cache alebo s novým namespace. Overuje:

- úplnosť dependency deklarácií,
- reproducibility,
- cache-independent correctness,
- skryté workspace dependencies,
- poškodený shared state.

Cold build je kontrola cache modelu, nie iba performance benchmark.

## 30. Secret a privacy safety

Pred uploadom artifactu alebo cache skontroluj:

- `.env` a secret files,
- tokens a cloud profiles,
- kubeconfig,
- certificates,
- Terraform state,
- production data,
- debug dump,
- package auth files.

Cache často má širší a menej viditeľný access než artifacts. Neukladaj do nej secrets.

## 31. Storage governance

Sleduj:

- artifact a cache storage podľa projektu,
- priemernú veľkosť,
- upload/download traffic,
- retention effectiveness,
- stale refs,
- latest-success roots,
- orphaned caches,
- cache hit rate,
- cleanup failures,
- release artifacts zostávajúce iba v CI storage.

Optimalizácia storage nesmie odstrániť recovery evidence.

## 32. Incident pri cache poisoning-u

Postup:

1. zastav trusted consumers alebo vypni restore,
2. identifikuj namespace, keys a writers,
3. zneplatni alebo odstráň zasiahnuté entries,
4. spusti clean builds,
5. over artifacts vytvorené z kompromitovanej cache,
6. rotuj credentials, ak mohli uniknúť,
7. audituj registry pushes a deployments,
8. oprav trust/write policy,
9. pridaj integrity verification.

Vymazanie jednej cache položky nemusí stačiť, ak rovnaký writer ovplyvnil viac keys.

## 33. Diagnostický postup

Keď downstream job nemá správny output:

1. identifikuj producer pipeline/job/attempt,
2. over, či artifact vznikol a upload prebehol,
3. over `needs`/`dependencies` a job inclusion,
4. over retention a access,
5. porovnaj subject, variant a digest,
6. skontroluj collisions a missing shards,
7. odlíš artifact od cache restore,
8. pri cache spusti clean retry,
9. over backend a key resolution,
10. uchovaj evidence pred cleanupom.

## 34. Typické anti-patterny

### Release binary iba ako expirovateľný job artifact

Rollback a support závisia od krátkodobého pipeline storage.

### Chýbajúci report = čistý report

Scanner alebo parser failure sa interpretuje ako nulový počet findings.

### Všetky artifacts sa sťahujú všade

Dependency graph, cost aj exposure sú nejasné.

### Shared cache pre fork a release jobs

Untrusted writer môže ovplyvniť trusted build.

### Cache obsahuje build output bez validácie

Stale alebo partial output sa stáva implicitným source of truth.

### Retry prepíše first-attempt evidence

Flaky alebo infra failure zmizne z auditného obrazu.

### Cleanup podľa názvu bez retention roots

Odstráni sa artifact aktívneho releaseu alebo rollback candidate.

## 35. Praktický rozhodovací rámec

Pre každý ukladaný output odpovedz:

1. Je to artifact, report, release output alebo cache?
2. Aký je jeho subject a producer identity?
3. Ktorý consumer ho potrebuje?
4. Ako sa overí completeness a integrity?
5. Aký access a retention potrebuje?
6. Má byť promotionovaný do registry?
7. Môže obsahovať secrets alebo citlivé dáta?
8. Ak ide o cache, aké inputs a trust namespace tvorí key?
9. Kto smie cache zapisovať?
10. Funguje pipeline po miss alebo clean build-e?

## 36. Kontrolný checklist

- artifacts majú producer a subject identity;
- report absence nie je pass;
- DAG transfer je explicitný;
- parallel outputs majú inventory a unique paths;
- retry attempts zostávajú auditovateľné;
- release outputs sú publikované do durable registry;
- retention rešpektuje deploymenty a rollback window;
- cache keys zahŕňajú compatibility inputs;
- fallback keys neprekračujú trust boundary;
- untrusted jobs nezapisujú trusted cache;
- partial/stale cache sa validuje;
- periodic clean build overuje correctness;
- artifacts a cache neobsahujú secrets.

## 37. Kontrolné otázky

1. Aký je rozdiel medzi artifactom a cache?
2. Čo tvorí artifact subject identity?
3. Prečo chýbajúci report nie je nulový report?
4. Ako sa overuje completeness shardovaných results?
5. Prečo má byť artifact transfer explicitný?
6. Kedy output patrí do registry namiesto job artifacts?
7. Čo sú retention roots?
8. Ktoré inputs patria do cache key?
9. Aké riziko prinášajú fallback keys?
10. Kto má smieť zapisovať shared cache?
11. Ako vzniká cache poisoning?
12. Čo dokazuje clean build bez cache?

## Summary

Artifact je výstup a evidence viazaná na konkrétny pipeline subject; cache je odstrániteľný performance state. Dôveryhodný GitLab workflow používa explicitný producer-consumer graph, completeness checks, digest/provenance, primeraný access a retention. Release artifacts sa promotionujú do durable registry bez rebuildu. Cache musí byť oddelená podľa compatibility a trustu, validovaná po restore a zapisovaná iba oprávnenými jobs. Pipeline musí zostať korektná aj bez cache.

## Glossary impact

Relevantné pojmy: GitLab job artifact, report artifact, artifact subject, artifact provenance, artifact retention, retention root, `needs:artifacts`, GitLab cache, cache key, fallback key, cache policy, distributed cache, cache poisoning a clean build.

## Oficiálna dokumentácia

- [Job artifacts](https://docs.gitlab.com/ci/jobs/job_artifacts/)
- [Caching in GitLab CI/CD](https://docs.gitlab.com/ci/caching/)
- [CI/CD YAML syntax](https://docs.gitlab.com/ci/yaml/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Variables a secrets](variables-and-secrets.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Container a package registry →](container-and-package-registry.md)
<!-- KNOWLEDGE-NAVIGATION:END -->