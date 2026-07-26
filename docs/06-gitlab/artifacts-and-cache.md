# Artifacts a cache

## Metadata

- Status: Learning
- Level: L2
- Domain: GitLab

GitLab artifact je identifikovateľný output konkrétneho pipeline execution subjectu. Môže niesť build bytes, test report, deployment plan alebo provenance. Cache je odstrániteľný performance state, ktorému consumer nesmie slepo dôverovať a bez ktorého musí pipeline zostať korektná.

```text
artifact contract
→ identified producer execution
→ bounded publication
→ integrity a completeness verification
→ explicit consumer binding
→ promotion/retention/recovery lifecycle

cache contract
→ compatibility + trust key
→ opportunistic restore
→ validation
→ bounded use
→ controlled write-back
→ eviction alebo invalidation
```

Ak cache miss zmení correctness alebo cache obsah je jedinou kópiou release outputu, storage model je nesprávny.

## 1. Nosný model: output trust chain

Dôveryhodný pipeline output vzniká cez:

```text
producer subject
→ output inventory
→ upload attempt
→ immutable content identity
→ completeness verdict
→ consumer selection
→ use/promotion
→ retention root alebo expiry
```

Každý transition môže zlyhať samostatne. Script môže prejsť a artifact upload zlyhať. Sedem z ôsmich test shards môže publikovať report a aggregate job môže nesprávne považovať actual inventory za complete. Retry môže vytvoriť iný digest pod rovnakým filename-om.

## 2. Nosný scenár: Atlas Payments release outputs

Pipeline `P812` pre release `3.12.0` vytvára:

```text
build_release
→ payments-api.tar digest D42
→ build manifest M42
→ SBOM B42

integration shards 1..8
→ JUnit reports J1..J8

security jobs
→ SAST, dependency a image reports

release_gate
→ expected evidence manifest E42

publish_release
→ registry image/package viazaný na D42
```

Zároveň používa cache:

```text
package cache key
= project + linux/amd64 + toolchain T9 + lockfile hash L17 + trust namespace protected
```

Release build môže cache čítať, ale dependencies overuje checksumami a pravidelný cold build dokazuje cache-independent correctness.

## 3. Artifact subject je viac než filename

Atlas artifact identity obsahuje:

```text
project
pipeline ID a source
source/candidate SHA
resolved config digest
producer job a attempt
variant/platform
runner/toolchain subject
content digest
```

`payments-api-latest.tar` je iba presentation name. Dva súbory s rovnakým názvom môžu patriť inému source-u, platforme alebo retry attemptu.

Consumer má používať manifest alebo digest, nie „posledný artifact z mainu“.

## 4. Typ outputu určuje lifecycle

- **Build artifact:** intermediate alebo final binary/bundle.
- **Report artifact:** JUnit, coverage, scanner alebo SBOM formát interpretovaný gate-om.
- **Evidence artifact:** manifest, plan, attestation alebo approval packet.
- **Diagnostic artifact:** trace, screenshot, dump alebo logs.
- **Deployment artifact:** rendered manifest alebo package použitý deploy jobom.
- **Release artifact:** immutable podporovaný obsah publikovaný do durable registry.

Job artifact s krátkym `expire_in` nie je vhodný ako jediný production rollback source.

## 5. Publication contract

Producer definuje:

```text
presné paths
expected files a variants
upload condition
content type/format
name a digest
access
retention
forbidden content
consumer inventory
```

`untracked` alebo celý workspace môže zahrnúť secrets, cache, temporary config a nesúvisiace outputs. Explicitné paths znižujú nepredvídateľný obsah aj veľkosť.

Artifact upload je samostatná fáza. Script success bez publication success znamená incomplete output, nie complete pass.

## 6. Expected inventory odlišuje pass od incomplete

Pre 8 test shards:

```text
expected = {1,2,3,4,5,6,7,8}
actual   = {1,2,3,4,5,7,8}
→ INCOMPLETE
```

Fan-in nemá iterovať iba cez existujúce reports a predpokladať, že chýbajúci shard bol not applicable. Každá položka expected inventory musí skončiť ako:

- present/pass;
- present/findings alebo failure;
- explicitne not applicable s dôvodom;
- missing/incomplete;
- tool/infrastructure failure.

Absencia reportu nie je nula findings.

## 7. Producer-consumer binding je explicitný DAG contract

Consumer určuje:

```text
producer job
attempt policy
pipeline/source subject
variant/platform
artifact name + digest/manifest
required completeness
access a expiry
```

`needs: artifacts` môže preniesť output po DAG edge-i, ale syntax sama nedokazuje, že správny artifact vznikol. Consumer musí overiť manifest a expected identity.

Implicitné stiahnutie všetkých artifacts z predchádzajúcich stages znejasňuje dependency graph a zvyšuje exposure.

## 8. Retry vytvára nový execution attempt

Job attempt A1 môže zlyhať po vytvorení partial outputu. Retry A2 môže vytvoriť nový digest.

```text
job name build_release
attempt A1 → digest D41, upload unknown/partial
attempt A2 → digest D42, pass
```

Record zachová oba attempts, first verdict a pravidlo, ktorý output je authoritative. Consumer nesmie filename collision-om alebo „latest successful job“ potichu zameniť A1/A2.

Retry je nový execution subject, nie prepis histórie.

## 9. Promotion oddeľuje CI storage od release storage

Bezpečný flow:

```text
build D42 raz
→ test/scanuj D42
→ over complete evidence E42
→ publishni rovnaký D42 do immutable registry version
→ release manifest referencuje D42
→ deployni D42
```

Production publish nesmie rebuildovať bytes. Job artifacts slúžia na pipeline transport; registry nesie durable release identity, support a rollback lifecycle.

## 10. Retention je referenčný graph

Pred cleanupom zachovaj artifacts referencované:

- active deploymentom;
- supported releaseom;
- rollback windowom;
- otvoreným incidentom;
- release manifestom;
- legal/compliance holdom;
- aktívnym review alebo auditom.

Retention podľa veku alebo latest-success refu nepozná všetky roots. Artifact môže byť starý, ale stále jediný dôveryhodný rollback candidate.

## 11. Cache key je compatibility a trust contract

Atlas cache key zahŕňa:

```text
project/component
trust namespace
OS + architecture
runtime/compiler/toolchain
base image alebo worker revision
lockfile/dependency manifest hash
build flags a package source
```

Chýbajúci input umožní restore nekompatibilného state-u. Fallback key môže zvýšiť hit rate, ale nesmie rozšíriť writer trust alebo zamlčať toolchain mismatch.

`feature → main fallback` je bezpečný iba ak main cache je kompatibilná a feature job nemôže zapisovať do trusted namespace-u.

## 12. Cache writer a reader majú odlišnú autoritu

Bezpečný model:

```text
trusted default-branch job
→ validuje dependencies
→ atomicky publikuje shared protected cache

feature/MR jobs
→ read-only alebo vlastný namespace

fork jobs
→ žiadny write do internal trusted cache

release build
→ clean alebo verified read-only restore
```

Cache write po partial install, canceled jobe alebo neoverenom outpute môže otráviť ďalšie builds. Write-back potrebuje temporary key, validation a atomic promotion.

## 13. Restore nie je trust decision

Po cache restore consumer overí podľa typu:

- package checksums/signatures;
- manifest completeness;
- compiler-state compatibility;
- permissions a architecture;
- expected source registry;
- archive integrity.

Musí bezpečne zvládnuť miss, eviction, partial archive, corruption, backend timeout a stale entry.

Cache backend outage nemá blokovať correctness, ak authoritative dependency source funguje.

## 14. Worked failure: missing shard vytvoril false-green release gate

Shard 6 zlyhal pri runner provisioning-u a report nevznikol. Aggregate job mal optional edge a čítal iba dostupné JUnit files.

```text
expected shards sa nikde nezaznamenali
→ actual reports J1..J5,J7,J8 sa agregujú
→ všetky prítomné tests sú green
→ gate vyhodnotí PASS
→ artifact D42 sa publikuje
```

### Príčina

Actual inventory bolo zamieňané za expected inventory. Infrastructure failure jedného producenta sa stratila v artifact graph-e.

### Dôsledok

Release evidence nepokrývala jednu test partition, hoci UI ukazovalo zelený fan-in.

### Trvalá náprava

```text
expected evidence manifest E42
→ každý shard publikuje status/report identity
→ aggregate odmietne missing položku
→ optional edge iba pri explicitnej applicability
→ gate verdict INCOMPLETE pri producer failure
```

## 15. Worked failure: fork MR otrávil cache release buildu

Fork pipeline mala write access do cache keya odvodeného iba z lockfile hash-u. Útočný job vložil modifikovaný compiler helper.

```text
fork writer publikuje trusted-looking cache
→ protected release build restore-ne rovnaký key
→ helper sa spustí pred checksum kontrolou výsledku
→ release artifact obsahuje payload
→ source a lockfile sú nezmenené
```

### Príčina

Cache key pokrýval compatibility, ale nie trust namespace. Release build považoval restore za trusted input.

### Recovery

Atlas zastavil publication, invalidoval celý affected namespace, spustil clean builds a auditoval artifacts, registry pushes a deployments z compromise windowu.

### Trvalá náprava

- fork/non-protected/protected namespaces;
- untrusted readers bez shared write;
- read-only cache pre release;
- integrity overenie dependencies/tools;
- periodic clean-room build comparison.

## 16. Worked failure: cleanup odstránil rollback artifact

Storage cleanup mazal job artifacts staršie než 30 dní. Produkcia však stále používala release `3.10.4` a jeho rollback package existoval iba v CI storage.

```text
age-based cleanup
→ artifact zmizne
→ current release incident
→ previous supported package nie je dostupný
→ rollback RTO sa výrazne predĺži
```

### Príčina

Cleanup nemal deployment/support retention roots a release output nebol promotionovaný do durable registry.

### Náprava

Release manifest vytvára registry root, supported versions majú explicitný lifecycle a CI artifacts môžu expirovať až po potvrdenej durable publication.

## 17. Kauzálny diagnostický walkthrough

Symptom: release artifact z cached buildu má iný digest než cold build nad rovnakým source SHA.

### Krok 1 — stabilizuj oba subjects

```text
source/candidate SHA
resolved config digest
producer job + attempts
runner/toolchain/platform
artifact manifests
effective cache key, fallback a namespace
```

### Krok 2 — konkurenčné hypotézy

```text
H1: artifacts patria iným attempts alebo platformám
H2: source/config/toolchain sa líši
H3: cache key vynechal compatibility input
H4: cache bola partial/corrupt
H5: untrusted writer otrávil namespace
H6: build je nondeterministic aj bez cache
```

### Krok 3 — observation points

- manifest a attempt identity testujú H1;
- source/config/runner inventories testujú H2;
- key derivation a restored manifest testujú H3;
- archive integrity/download logs testujú H4;
- cache writer audit a trust scope testujú H5;
- opakované clean builds testujú H6.

Atlas zistí, že fallback key neobsahoval compiler revision a bol zapisovateľný non-protected jobs. H3/H5 vysvetľujú rozdiel.

### Krok 4 — contain-ni output trust chain

Release publication sa blokuje, cache restore pre trusted builds sa vypne a affected artifacts sa označia ako nedôveryhodné.

### Krok 5 — obnov outcome

D42 sa vytvorí clean buildom na pinned runneri, všetky tests/scans sa zopakujú nad rovnakým digestom a artifact sa promotionuje do registry.

### Krok 6 — vráť learning

Finding sa mení na versioned cache-key contract, writer policy, clean-build gate a artifact manifest s runner/toolchain provenance.

## 18. Diagnostický runbook

1. Urči producer pipeline, job, attempt a artifact subject.
2. Porovnaj expected a actual output/report inventory.
3. Over upload status, access, retention a content digest.
4. Trace-ni explicitný consumer edge a selection policy.
5. Rozlíš job artifact, registry release output a cache restore.
6. Pri cache urč key inputs, fallback, namespace a posledného writera.
7. Validuj archive/content po restore a spusti cold comparison.
8. Contain-ni publication alebo trusted consumers pri nejasnej integrite.
9. Over podporované retention roots pred cleanupom.
10. Zmeň finding na inventory, provenance, namespace alebo lifecycle control.

## 19. Referenčné pravidlá

- Artifact patrí konkrétnemu execution subjectu.
- Filename nie je immutable identity.
- Script success bez output publication môže byť incomplete.
- Expected inventory odlišuje complete evidence od actual-only agregácie.
- Retry vytvára nový attempt a digest lineage.
- Release output patrí do durable registry bez rebuildu.
- Retention sa riadi references, nie iba vekom.
- Cache je odstrániteľný performance state.
- Cache key zahŕňa compatibility aj trust.
- Untrusted writer nesmie ovplyvniť trusted cache consumera.
- Restore potrebuje integrity/compatibility validation.
- Cold build je correctness control.

## 20. Časté omyly

### „Artifact existuje, teda je správny“

Treba overiť producer subject, attempt, digest a completeness.

### „Chýbajúci report znamená žiadne findings“

Môže ísť o absent job, upload failure alebo incomplete shard.

### „Cache je interná, teda dôveryhodná“

Writer scope a shared namespace môžu vytvoriť poisoning path.

### „Retry iba opraví infra chybu“

Môže vytvoriť nový output a zakryť first-attempt evidence.

### „Staré artifacts možno vymazať“

Aktívny release, rollback alebo audit ich môže stále referencovať.

## 21. Zhrnutie

Dôveryhodný Atlas output lifecycle je:

```text
identified producer subject
→ explicitný expected output inventory
→ bounded publication
→ digest + provenance + completeness
→ explicitný consumer binding
→ registry promotion alebo reference-aware retention

cache:
trust/compatibility key
→ validated opportunistic restore
→ controlled writer
→ cold-build-verifiable correctness
```

Artifact troubleshooting hľadá prvú stratenú identity alebo completeness boundary. Cache troubleshooting hľadá neúplný key, neprimeraného writera alebo chýbajúcu validation. Ani jedno sa nesmie skončiť vetou „súbor tam bol“.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Variables a secrets](variables-and-secrets.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Container a package registry →](container-and-package-registry.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
