# Artifact versioning

Artifact versioning je systém jednoznačnej identifikácie build výstupov tak, aby bolo možné presne určiť, čo bolo zostavené, testované, schválené, nasadené a prípadne rollbacknuté.

Verzia artifactu nie je iba názov súboru. Je súčasťou release identity, provenance, promotion evidence a incidentnej diagnostiky.

## 1. Čo je artifact

Artifact je immutable alebo aspoň jednoznačne identifikovateľný výstup build procesu, napríklad:

- container image,
- binary alebo executable,
- package,
- archive,
- VM image,
- Helm chart,
- firmware,
- static web bundle,
- database migration bundle,
- Software Bill of Materials.

Source commit nie je automaticky deployovateľný artifact. Rovnaký source môže pri rozdielnom toolchaine, dependencies alebo build konfigurácii vytvoriť rozdielne bytes.

## 2. Požiadavky na dobrú artifact identity

Artifact identity má byť:

- jednoznačná,
- nemenná,
- strojovo spracovateľná,
- auditovateľná,
- spätne mapovateľná na source a build,
- vhodná pre promotion aj rollback,
- nezávislá od názvu environmentu.

Príklad stabilnej identity:

```text
registry.example.com/payments/api@sha256:4f2c...
```

Ľudsky čitateľný tag môže byť:

```text
payments-api:2.8.1
```

Digest však identifikuje konkrétny obsah. Tag môže byť v niektorých registry systémoch prepísateľný.

## 3. Logical version vs. content identity

Rozlišuj:

```text
logical version
→ 2.8.1

content identity
→ sha256:4f2c...
```

Logical version komunikuje release význam a compatibility očakávania. Digest dokazuje konkrétne bytes.

Bezpečný release record typicky obsahuje oboje:

```text
version: 2.8.1
artifact: registry.example.com/payments/api
artifact_digest: sha256:4f2c...
source_commit: 8a71c9d
pipeline_run: 18422
```

## 4. Build metadata

Artifact metadata môžu zahŕňať:

- source repository,
- commit SHA,
- branch alebo tag,
- build timestamp,
- pipeline run ID,
- builder identity,
- toolchain versions,
- dependency lock hash,
- target OS/architecture,
- build configuration,
- SBOM,
- provenance attestation,
- signatures.

Metadata nemajú meniť runtime obsah spôsobom, ktorý ničí reproducibility, ak to nie je zámerné.

## 5. Versioning schémy

Bežné možnosti:

### Semantic version

```text
2.8.1
```

Vhodný pre verejné alebo stabilné compatibility kontrakty.

### Calendar version

```text
2026.07.21
```

Vhodný pre pravidelný release cadence alebo dátumovo orientované produkty.

### Incrementing build number

```text
18422
```

Jednoduchý interný identifikátor, ale bez významu mimo konkrétneho pipeline systému.

### Commit-based version

```text
8a71c9d
```

Silná väzba na source, ale commit sám neidentifikuje build prostredie ani výsledné bytes.

### Hybridná verzia

```text
2.8.1+build.18422.sha.8a71c9d
```

Spája release význam a technickú traceability.

## 6. Pre-release artifacts

Pre-release identifikátory môžu rozlišovať:

```text
2.8.1-alpha.3
2.8.1-beta.2
2.8.1-rc.1
```

Pre-release artifact musí byť stále immutable. Release candidate sa nemá po schválení rebuildovať pod rovnakou verziou.

Bezpečný flow:

```text
build immutable artifact
→ priraď candidate identity
→ testuj digest
→ schváľ digest
→ pridaj release alias/tag na ten istý digest
```

Nie:

```text
testuj RC
→ rebuildni source
→ publikuj nové bytes ako final
```

## 7. Mutable tags

Tagy ako:

```text
latest
stable
production
main
```

sú pointers, nie spoľahlivá artifact identity.

Môžu byť užitočné pre discovery, ale deployment record musí zachovať digest alebo inú immutable identity.

Riziká mutable tagov:

- nejasný rollback,
- cache inconsistency,
- deployment drift,
- nemožnosť dokázať, čo bolo nasadené,
- race medzi promotion a pullom,
- supply-chain substitution.

## 8. Build once, promote many

Odporúčaný model:

```text
source commit
→ build artifact A
→ test A
→ security scan A
→ staging deploy A
→ production deploy A
```

Neodporúčaný model:

```text
source commit
→ build staging artifact
→ neskôr rebuild production artifact
```

Aj pri rovnakom source môžu vzniknúť rozdielne dependencies, timestampy alebo toolchain outputs.

## 9. Multi-platform artifacts

Container alebo package release môže obsahovať viac variantov:

```text
linux/amd64
linux/arm64
windows/amd64
```

Release version môže smerovať na manifest alebo index, ktorý mapuje platformu na konkrétny digest.

Test evidence musí byť platformovo explicitná. Úspešný test `linux/amd64` nedokazuje správnosť `linux/arm64` variantu.

## 10. Artifact repository a registry

Artifact repository má poskytovať:

- immutable publishing alebo write-once policy,
- access control,
- checksum verification,
- retention rules,
- metadata search,
- vulnerability scan integration,
- signatures a provenance,
- replication a backup,
- audit logs.

Artifacty nemajú byť závislé iba od krátkodobého CI storage.

## 11. Retention a garbage collection

Retention policy musí rozlišovať:

- aktívne production releases,
- rollback candidates,
- supported versions,
- pre-release artifacts,
- branch builds,
- orphaned artifacts,
- právne alebo auditné požiadavky.

Artifact používaný v produkcii sa nesmie odstrániť iba preto, že pipeline run expiroval.

## 12. Provenance a podpisovanie

Provenance odpovedá:

```text
kto artifact zostavil?
z akého source?
akým build procesom?
s akými vstupmi?
bolo build prostredie dôveryhodné?
```

Podpis môže potvrdiť integritu a identitu publishera. Samotný podpis však nedokazuje, že artifact je bezpečný alebo funkčný.

Verification policy môže vyžadovať:

- povolenú builder identity,
- trusted source repository,
- protected branch,
- konkrétny workflow,
- neprítomnosť neoverených dependencies,
- platný podpis a provenance.

## 13. Artifact a configuration versioning

Deployment identity nie je iba application artifact:

```text
runtime state = artifact + config + secrets references + infrastructure + data schema
```

Release record má zachovať minimálne:

- artifact digest,
- config revision,
- infrastructure revision,
- database schema/migration state,
- feature-flag state alebo relevantnú snapshot reference.

## 14. Rollback requirements

Rollback potrebuje:

- dostupný starší artifact,
- jeho metadata a provenance,
- kompatibilnú konfiguráciu,
- kompatibilnú databázovú schému,
- známu deployment procedúru,
- overený restore alebo roll-forward plán.

Version label bez zachovaného artifactu nie je rollback capability.

## 15. Typické anti-patterny

### Prepísanie vydanej verzie

`2.8.1` dnes obsahuje iné bytes než včera. Audit a rollback sú nedôveryhodné.

### Production používa `latest`

Deployment nie je deterministický.

### Version je iba pipeline number

Pri migrácii CI systému sa stratí význam a globálna jednoznačnosť.

### Rebuild pri promotion

Produkcia nedostáva artifact, ktorý prešiel testami.

### Artifact bez source mappingu

Incidentný tím nevie určiť obsah a ownera zmeny.

### Neobmedzená retention

Registry rastie bez kontroly nákladov a lifecycle pravidiel.

## 16. Troubleshooting

### Rovnaká verzia má rôzny checksum

Skontroluj:

- mutable repository policy,
- paralelné publish jobs,
- timestampy v archive,
- nezapinned dependencies,
- rozdielny toolchain,
- platform-specific variant,
- rebuild počas promotion.

### Deployment nevie stiahnuť starý artifact

Over retention, garbage collection, repository replication a referencie na digest.

### Tag ukazuje na iný digest než deployment record

Tag bol prepísaný. Deployment diagnostikuj podľa digestu, nie podľa aktuálneho tagu.

### Reproducible build sa nezhoduje

Hľadaj nedeterministické vstupy: čas, locale, filesystem order, network dependencies, random seed a toolchain drift.

## 17. Kontrolné otázky

1. Aký je rozdiel medzi logical version a content digestom?
2. Prečo commit SHA nestačí ako úplná artifact identity?
3. Čo znamená build once, promote many?
4. Prečo je rebuild release candidate pred produkciou rizikový?
5. Kedy je mutable tag prijateľný?
6. Čo má obsahovať artifact metadata?
7. Ako versionovať multi-platform release?
8. Ako retention policy súvisí s rollbackom?
9. Aký je rozdiel medzi podpisom a dôkazom bezpečnosti?
10. Ktoré časti runtime state treba zachytiť okrem artifactu?

## Glossary impact

Relevantné pojmy: artifact version, logical version, content digest, immutable tag, mutable tag, build metadata, release candidate, calendar versioning, provenance attestation, artifact retention, multi-platform manifest a build once, promote many.
