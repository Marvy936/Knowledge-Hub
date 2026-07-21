# Trigger, artifact a cache

Pipeline potrebuje vedieť, **prečo** sa spustila, **aký dôveryhodný výstup** vytvorila a **ktoré dočasné dáta** môže znovu použiť na zrýchlenie ďalšieho runu. Trigger, artifact a cache riešia tri rozdielne problémy a nesmú sa zamieňať.

## 1. Trigger

Trigger je udalosť alebo explicitný pokyn, ktorý vytvorí pipeline run.

Typické triggers:

- push na branch,
- vytvorenie alebo aktualizácia merge requestu,
- tag alebo release event,
- schedule,
- manuálny dispatch,
- API alebo webhook,
- upstream/parent pipeline,
- zmena v inom repository,
- environment alebo deployment event.

Trigger určuje runtime context:

```text
event
→ pipeline definition
→ commit/ref
→ identity
→ variables a permissions
→ jobs
```

## 2. Event payload nie je dôveryhodný automaticky

Event payload môže obsahovať:

- branch a commit SHA,
- actor identity,
- changed paths,
- pull request metadata,
- repository fork informáciu,
- tag name,
- custom parameters.

Nedôveryhodný používateľ môže ovplyvniť source code, branch name, commit message alebo pull-request fields. Nepoužívaj ich bez quoting-u a validácie v shell commands, paths alebo deployment names.

## 3. Push vs. merge-request pipeline

Push pipeline overuje branch tip. Merge-request pipeline môže overovať:

- source branch SHA,
- merge request head,
- synthetic merge result so súčasným target branch,
- merge train alebo merge queue result.

Najhodnotnejší je stav, ktorý sa čo najviac podobá skutočnému budúcemu mainline commitu.

## 4. Duplicate pipelines

Rovnaký commit môže spustiť push aj merge-request pipeline. Dôsledky:

- dvojité náklady,
- duplicated status checks,
- racing deployments,
- nejasný autoritatívny result.

Pravidlá workflowu majú explicitne určiť, ktorý event vytvára ktorý pipeline typ.

## 5. Path-based triggers

Monorepo môže používať changed paths:

```text
services/api/**
→ API checks

services/web/**
→ frontend checks
```

Riziká:

- zmena shared library ovplyvní viac služieb,
- rename alebo generated files uniknú jednoduchému globu,
- build tooling zmena môže ovplyvniť všetko,
- base commit pre diff môže byť nesprávny.

Path filtering má byť založený na dependency graph-e, ak change coupling nie je triviálny.

## 6. Scheduled pipelines

Schedule je vhodný pre:

- širšie regression tests,
- dependency update checks,
- certificate alebo secret expiry checks,
- drift detection,
- periodic security scans,
- cleanup.

Schedule nesmie byť jediný spôsob, ako odhaliť chybu, ktorá mala blokovať merge.

## 7. Manual trigger

Manuálny trigger má mať typed a validované inputs:

```text
environment: staging | production
artifact_digest: sha256:...
change_ticket: string
```

Free-form command alebo branch name odovzdaný priamo do shellu vytvára injection risk.

## 8. Trigger permissions

Rovnaká pipeline definícia môže dostať odlišné permissions podľa triggeru:

- fork pull request: read-only, bez secrets,
- protected branch: build a publish rights,
- protected tag: release signing,
- manual production deployment: environment-scoped identity.

Secrets nemajú byť dostupné iba preto, že pipeline používa rovnaký YAML.

## 9. Artifact

Artifact je versionovaný a identifikovateľný výstup pipeline určený na ďalšie overenie, distribúciu alebo deployment.

Príklady:

- container image,
- binary package,
- archive,
- Helm chart,
- SBOM,
- signed provenance,
- deployment manifest bundle,
- test report,
- generated documentation.

## 10. Build once, promote many

Správny model:

```text
source commit
→ build
→ immutable artifact
→ verify
→ staging
→ production
```

Nesprávny model:

```text
source commit
→ build for staging
→ later rebuild for production
```

Rebuild môže použiť iné dependencies, base image, compiler, timestamp alebo network response. Produkcia potom nedostane artifact, ktorý bol testovaný.

## 11. Artifact identity

Artifact má mať stabilnú identity:

- content digest,
- immutable version,
- commit SHA,
- build run ID,
- source repository,
- builder identity,
- timestamp,
- dependency/provenance metadata.

Tag `latest` nie je dostatočná identity. Mutable tag môže smerovať na iný obsah bez zmeny deployment konfigurácie.

## 12. Artifact repository

Artifact repository alebo registry poskytuje:

- upload a download,
- access control,
- retention,
- immutability,
- checksums,
- metadata,
- vulnerability scanning,
- replication,
- audit log.

Pipeline-local artifact storage je vhodný pre krátkodobé reports. Release artifact potrebuje durable registry s jasným lifecycle.

## 13. Artifact retention

Retention policy musí rozlišovať:

- temporary diagnostic artifacts,
- pull-request builds,
- release candidates,
- production releases,
- compliance evidence.

Artifact potrebný na rollback nesmie expirovať skôr než podporované rollback window.

## 14. Artifact integrity a authenticity

Checksum odhaľuje zmenu bytes. Signature a provenance môžu dokazovať:

- ktorý builder artifact vytvoril,
- z akého source commitu,
- s akým workflowom,
- v akom trusted environment-e.

Integrity nie je automaticky authenticity. Hash z nedôveryhodného zdroja iba presne identifikuje nedôveryhodný obsah.

## 15. Reports ako špeciálny artifact

Reports môžu byť:

- JUnit,
- coverage,
- SAST/SCA,
- performance results,
- deployment evidence,
- SBOM.

Pri failure používaj `when: always` alebo ekvivalent, aby sa diagnostický report zachoval aj pri neúspešnom jobe.

## 16. Cache

Cache je optimalizácia na znovupoužitie draho získaných alebo vypočítaných dát. Nie je autoritatívnym release outputom.

Príklady:

- package-manager download cache,
- compiler cache,
- dependency directory,
- build-system intermediate data,
- container build layers.

Cache môže byť:

- missing,
- stale,
- evicted,
- partially restored,
- shared medzi runs.

Pipeline musí byť korektná aj bez cache.

## 17. Artifact vs. cache

| Vlastnosť | Artifact | Cache |
|---|---|---|
| Účel | dôveryhodný výstup | zrýchlenie |
| Identity | explicitná a stabilná | odvodená z cache key |
| Correctness | downstream na ňom závisí | nesmie byť potrebný na správnosť |
| Retention | podľa release/evidence lifecycle | oportunistická |
| Immutability | preferovaná alebo povinná | často nahraditeľná |
| Missing stav | môže blokovať workflow | má viesť k recompute |

## 18. Cache key

Cache key má reprezentovať všetky vstupy ovplyvňujúce cached obsah:

```text
OS + architecture + toolchain version + lockfile hash + relevant config
```

Slabý key:

```text
python-dependencies
```

Silnejší key:

```text
python-linux-amd64-3.12-${hash(requirements.lock)}
```

## 19. Exact a fallback restore

Praktický model:

1. skúsiť exact key,
2. prípadne bezpečný prefix fallback,
3. validovať alebo doplniť obsah,
4. uložiť nový exact cache.

Fallback z inej branch môže zrýchliť download, ale nesmie spôsobiť použitie nesprávnej dependency verzie bez overenia lockfileom.

## 20. Cache poisoning

Útočník alebo nedôveryhodný pipeline môže uložiť cache, ktorú neskôr použije privileged pipeline.

Ochrany:

- oddeliť cache namespaces podľa trust levelu,
- nepovoliť fork pipeline zapisovať do protected cache,
- zahrnúť toolchain a lockfile identity,
- overovať package integrity,
- nepoužívať cache ako executable source bez validation,
- preferovať read-only cache pre nedôveryhodné runs.

## 21. Cache invalidation

Cache invaliduj pri zmene:

- dependency lockfile,
- compiler/toolchain,
- build flags,
- OS image,
- architecture,
- relevant environment variables,
- generated-code schema.

Príliš častá invalidácia ruší benefit. Nedostatočná invalidácia vytvára nejasné a nereprodukovateľné failures.

## 22. Dependency cache vs. vendoring

Dependency cache iba urýchľuje download. Lockfile alebo vendored dependencies definujú verzie. Cache nesmie nahrádzať dependency resolution policy.

Pipeline musí overovať checksums/signatures, ak ecosystem podporuje integrity metadata.

## 23. Container layer cache

Container build cache môže znovu použiť vrstvy podľa build contextu a instruction cache key. Riziká:

- mutable base tag,
- secret zahrnutý do layeru,
- nepresný build context,
- stale package metadata,
- cross-project leakage.

Používaj pinned base image digest, secret mounts a explicitný cache scope.

## 24. Artifact fan-out

Jeden build artifact môžu paralelne používať:

```text
build artifact
├─> unit/package verification
├─> security scan
├─> integration tests
├─> SBOM/provenance
└─> staging deployment
```

Downstream jobs majú používať rovnaký digest, nie každý vytvárať vlastnú verziu.

## 25. Trigger-to-artifact traceability

Pre release musí byť možné odpovedať:

- ktorý event spustil pipeline,
- ktorý commit bol buildnutý,
- aký workflow a runner ho spracoval,
- aké gates prešli,
- aký artifact digest vznikol,
- do ktorých environments bol promotion vykonaný.

Toto je základ auditovateľného software supply chainu.

## 26. Troubleshooting

### Cache sa nikdy nenájde

Over:

- key a hashing,
- branch/trust namespace,
- runner architecture,
- cache retention,
- upload podmienky,
- path relatívny k workspace.

### Cache hit, ale build zlyhá

Cache môže byť stale alebo key neobsahuje všetky relevantné vstupy. Spusti čistý build a porovnaj.

### Artifact downstream chýba

Over:

- či upload job prešiel,
- `when` policy,
- retention,
- dependency declaration,
- artifact name/path,
- access permissions.

### Produkcia má iný image než staging

Porovnaj content digest, nie tag. Pravdepodobne došlo k rebuildu alebo mutable tag update-u.

## 27. Časté omyly

### „Cache je artifact“

Cache je odstrániteľná optimalizácia. Artifact je identifikovateľný výstup workflowu.

### „Tag jednoznačne identifikuje image“

Iba immutable digest jednoznačne identifikuje obsah.

### „Schedule pipeline nahrádza merge checks“

Neskorý feedback neochráni mainline pred známou triedou chyby.

### „Fork pipeline môže používať rovnaké secrets a cache“

Nedôveryhodný source context potrebuje oddelenú trust policy.

## 28. Kontrolné otázky

1. Aké hlavné trigger typy poznáš a aký context prinášajú?
2. Prečo môže push a merge-request pipeline testovať rozdielny commit?
3. Ako zabrániš duplicate pipelines?
4. Aký je rozdiel medzi artifactom a cache?
5. Prečo je build once, promote many dôležitý?
6. Prečo mutable tag nie je artifact identity?
7. Čo má obsahovať bezpečný cache key?
8. Ako vzniká cache poisoning?
9. Ktoré artifacts musia prežiť release rollback window?
10. Ako vytvoríš traceability od triggeru po production deployment?

## Glossary impact

Relevantné pojmy: trigger, event payload, push pipeline, merge-request pipeline, scheduled pipeline, manual dispatch, artifact, artifact digest, artifact repository, retention, build once promote many, cache, cache key, cache poisoning, cache invalidation a provenance.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Pipeline, stage, job a runner](pipeline-stage-job-runner.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Environment a promotion →](environment-and-promotion.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
