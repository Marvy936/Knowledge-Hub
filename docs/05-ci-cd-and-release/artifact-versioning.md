# Artifact versioning

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

## 1. Definícia

Artifact versioning je systém identifikácie, publikovania a správy build výstupov tak, aby bolo možné jednoznačne určiť, ktoré bytes boli vytvorené, testované, schválené, nasadené, stiahnuté, zneplatnené alebo použité na rollback.

Versioning nie je iba formát názvu súboru. Dôveryhodná artifact identity prepája viac vrstiev:

```text
logical release version
+ artifact name a namespace
+ immutable content digest
+ target platform/variant
+ build provenance
+ evidence manifest
→ release identity
```

Čitateľná verzia komunikuje ľuďom release význam. Digest identifikuje konkrétny obsah. Provenance vysvetľuje, ako obsah vznikol. Release record viaže tento obsah na schválenie, konfiguráciu a deployment state.

## 2. Artifact verzus source

Artifact je výstup build alebo packaging procesu určený na ďalšie overenie, distribúciu alebo execution. Môže to byť:

- container image alebo OCI artifact,
- binary, executable alebo library,
- package pre language ecosystem,
- archive alebo installer,
- VM image alebo firmware,
- Helm chart alebo deployment bundle,
- static web bundle,
- database migration bundle,
- model alebo data package,
- SBOM, provenance attestation alebo signature bundle.

Source commit nie je automaticky artifact identity. Rovnaký commit môže vytvoriť rozdielne bytes pri zmene:

- toolchainu,
- dependency resolutionu,
- base image,
- OS alebo architecture,
- build flags,
- timestamps,
- locale alebo timezone,
- environment variables,
- external network inputu.

Preto commit vysvetľuje source revision, ale digest vysvetľuje skutočný build output.

## 3. Tri typy identity

Je užitočné oddeliť tri vrstvy:

### Logical version

Ľudsky čitateľné označenie release významu:

```text
2.8.1
2026.07.24
build-18422
```

### Content identity

Kryptografická identita konkrétnych bytes:

```text
sha256:4f2c...
```

### Deployment identity

Konkrétny runtime state:

```text
artifact digest
+ config revision
+ infrastructure revision
+ schema state
+ feature exposure
+ target environment
```

Incidentný tím potrebuje všetky tri. Samotné `2.8.1` nehovorí, ktoré bytes registry v danom čase poskytla. Samotný digest zas nemusí vysvetliť compatibility alebo release intent.

## 4. Artifact name a namespace

Verzia je významná iba v správnom namespace.

```text
payments/api:2.8.1
payments/worker:2.8.1
```

Obe položky môžu mať rovnaké číslo verzie a pritom ide o iné artifacts. Plná logical identity typicky obsahuje:

- registry alebo repository,
- organization/project namespace,
- package alebo artifact name,
- logical version,
- variant/platform podľa potreby.

Globálne nejednoznačný build number ako `18422` je použiteľný iba spolu s pipeline/project identity.

## 5. Content digest

Content digest je hash kanonického alebo registry-defined obsahu. Pri OCI image môže digest identifikovať manifest alebo index, nie iba filesystem layers.

Vlastnosti digestu:

- zmena jedného bytu vytvorí inú identity,
- deployment môže presne pinovať obsah,
- registry alebo transport môže overiť integrity,
- evidence sa môže viazať na immutable subject,
- tag movement nemení pôvodný digest.

Hash dokazuje identitu obsahu, nie jeho dôveryhodnosť. Útočník môže publikovať škodlivý artifact a správne vypočítať jeho hash.

## 6. Logical version

Logical version komunikuje release intent alebo poradie. Môže používať:

- Semantic Versioning,
- Calendar Versioning,
- monotónny release number,
- commit-derived alebo distance-derived version,
- kombinovaný interný formát.

Logical version musí mať definovaný namespace, ordering a immutability policy. Ak sa vydaná verzia prepíše novými bytes, stráca auditnú aj dependency-resolution hodnotu.

## 7. Versioning schémy

### Semantic Versioning

```text
2.8.1
```

Vhodné, keď artifact publikuje jasný compatibility contract.

### Calendar Versioning

```text
2026.07.24
2026.07.24.1
```

Vhodné pri časovo orientovanom release cadence. Dátum sám o sebe nevyjadruje compatibility.

### Monotónny build alebo release number

```text
18422
```

Jednoduché ordering v rámci jedného systému. Pri migrácii CI treba zachovať namespace alebo mapovanie.

### Commit-derived version

```text
8a71c9d
```

Dobrá source traceability, ale neidentifikuje build configuration ani bytes.

### Hybrid

```text
2.8.1-rc.2+build.18422.sha.8a71c9d
```

Spája release intent s technickou stopou. Build metadata však podľa konkrétneho ecosystemu nemusí ovplyvňovať ordering alebo dependency resolution.

## 8. Pre-release identity

Pre-release identifikátory odlišujú kandidátov:

```text
2.8.1-alpha.3
2.8.1-beta.2
2.8.1-rc.1
```

Každý candidate musí byť immutable. `rc.1` dnes a `rc.1` zajtra nesmie označovať rozdielne bytes.

Bezpečný flow:

```text
build artifact D
→ priraď candidate version
→ testuj a skenuj D
→ schváľ D
→ vytvor final release alias na D
```

Finalizácia release nemá rebuildovať source. Môže pridať metadata, signature alebo alias, ale subject digest musí zostať rovnaký.

## 9. Build metadata

Metadata pomáhajú reprodukcii, diagnostike a policy verification. Typicky obsahujú:

- source repository a commit SHA,
- branch/tag alebo release request,
- pipeline a job run ID,
- builder/workload identity,
- pipeline definition revision,
- resolved template/policy version,
- toolchain a compiler versions,
- dependency lock hash,
- base image digests,
- target OS/architecture,
- build flags a feature set,
- timestamp a build environment,
- SBOM reference,
- provenance a signatures.

Metadata, ktoré sú vložené priamo do artifactu, môžu ovplyvniť digest a reproducibility. Rozlišuj runtime metadata od external attestations viazaných na digest.

## 10. Build once, promote many

Dôveryhodný model:

```text
source + pinned inputs
→ build artifact D
→ verify D
→ staging deploy D
→ production deploy D
```

Rizikový model:

```text
source
→ staging build D1
→ production rebuild D2
```

Aj keď `D1` a `D2` vznikli z rovnakého commitu, nejde o rovnaký testovaný subject. Promotion má meniť environment assignment alebo release status, nie bytes artifactu.

## 11. Rebuild verzus reprodukovateľný build

Rebuild je nový execution attempt. Reproducible build znamená, že pri rovnakých deklarovaných vstupoch nový build vytvorí ekvivalentný alebo identický výsledok.

Tieto koncepty sa nesmú zamieňať:

- produkčný release má použiť pôvodný schválený digest,
- nezávislý rebuild môže overiť reproducibility,
- zhodný digest zvyšuje dôveru v kontrolu vstupov,
- nezhodný digest neznamená automaticky kompromitáciu; môže odhaliť nondeterministický timestamp alebo toolchain drift,
- ani zhodný rebuild nenahrádza provenance pôvodného artifactu.

Reproducibility je verification mechanizmus, nie promotion mechanizmus.

## 12. Publication contract

Publikovanie artifactu je state transition s explicitnými pravidlami:

```text
build output
→ validate identity
→ upload temporary/staging object
→ verify checksum/digest
→ atomic publish immutable version
→ publish metadata/attestations
```

Publication contract má definovať:

- namespace a version ownership,
- create-only alebo write-once behavior,
- atomicitu publication,
- collision behavior,
- retry a idempotency key,
- signature/provenance timing,
- cleanup partial uploadu,
- who may publish, tag, yank alebo revoke.

## 13. Publication race

Dva jobs môžu súčasne publikovať rovnakú logical version.

Riziká:

- last writer prepíše prvý artifact,
- metadata patria inému digestu,
- tag smeruje na náhodného winnera,
- consumers stiahnu rozdielny obsah podľa času.

Ochrany:

- registry create-if-absent/write-once policy,
- unique candidate version per build,
- environment alebo release lock,
- optimistic comparison očakávaného state,
- atomic tag update,
- kontrola, že existujúca version už smeruje na rovnaký digest.

## 14. Mutable tag a alias

Tagy ako `latest`, `stable`, `production` alebo `main` sú aliases/pointers. Sú vhodné na discovery alebo channel semantics, nie ako jediná deployment identity.

Bezpečný model:

```text
stable → digest D
production record → digest D
```

Pri posune aliasu uchovaj:

- starý a nový digest,
- actor alebo workload identity,
- čas,
- dôvod/promotion record,
- policy result,
- target channel.

Deployment má resolve-nuť alias na digest a zaznamenať digest. Neskorší pohyb aliasu nesmie meniť význam historického deployment recordu.

## 15. Immutable tag

Niektoré registry podporujú immutable tags. Vydaná verzia `2.8.1` sa potom nedá prepísať.

To chráni pred náhodným alebo úmyselným replacementom, ale stále treba:

- kontrolovať publisher identity,
- overovať provenance a signature,
- riešiť nesprávne publikovaný artifact cez yank/revocation, nie prepísanie,
- uchovať retention roots,
- auditovať zmeny aliases.

## 16. Multi-platform artifacts

Jeden release môže mať viac platformových variantov:

```text
release 2.8.1
→ OCI index digest I
   ├─ linux/amd64 digest A
   ├─ linux/arm64 digest B
   └─ windows/amd64 digest C
```

Index alebo manifest list má vlastný digest. Deployment platforma vyberie konkrétny child manifest podľa platformy.

Evidence musí rozlišovať:

- index digest,
- variant digests,
- build provenance každého variantu,
- test results podľa platformy,
- spoločné release metadata.

Úspešný test `linux/amd64` nie je dôkazom `linux/arm64` variantu.

## 17. Release manifest alebo BOM

Komplexný systém môže pozostávať z viacerých artifacts. Release identity potom potrebuje manifest:

```yaml
release: 2026.07.24.1
components:
  api: sha256:aaa...
  worker: sha256:bbb...
  web: sha256:ccc...
  migrations: sha256:ddd...
config_schema: 7
```

Release manifest musí byť:

- immutable alebo content-addressed,
- podpísaný podľa policy,
- prepojený na component provenance,
- použitý promotion aj rollback procesom,
- validovaný proti compatibility rules.

Bez manifestu môže environment kombinovať komponenty, ktoré jednotlivo existujú, ale spolu neboli testované.

## 18. Evidence binding

Test, scan, approval a deployment evidence musí byť viazaná na immutable subject:

- artifact digest,
- variant digest,
- release-manifest digest,
- config/infrastructure revision podľa typu dôkazu.

Branch name alebo logical version nestačí, ak sa môže pohnúť. Evidence manifest má uviesť:

- subject identity,
- check type a version,
- result/verdict,
- timestamp a freshness scope,
- environment alebo test context,
- producer identity,
- report digest/reference.

## 19. Provenance

Provenance odpovedá:

```text
kto artifact vytvoril?
z akého source?
ktorou pipeline definíciou?
s akými deklarovanými inputs?
v akom builder environment-e?
```

Policy môže požadovať:

- povolený repository a commit/ref context,
- protected branch alebo trusted release trigger,
- schválenú builder identity,
- pinované build dependencies,
- konkrétny workflow,
- nepoužitie nedôveryhodného runnera,
- platný attestation a signature chain.

Provenance zvyšuje supply-chain dôveru, ale sama nedokazuje funkčnosť ani neprítomnosť zraniteľnosti.

## 20. Signatures

Signature viaže publisher alebo signer identity k artifact digestu alebo attestationu.

Verification musí kontrolovať:

- čo bolo podpísané,
- kto podpis vytvoril,
- či identity a certificate chain sú povolené,
- čas a validity/revocation stav,
- repository/workflow claims,
- policy pre keyless alebo key-based signing.

Podpis logical tagu bez digest bindingu môže byť slabý. Signer tiež môže legitímne podpísať chybný artifact; signature nie je quality gate sama osebe.

## 21. SBOM a dependency identity

SBOM opisuje components zahrnuté v artifacte. Musí byť viazaný na konkrétny digest a generovaný v bode, ktorý reprezentuje final artifact.

Riziká:

- SBOM vytvorený zo source neobsahuje build-time alebo base-image dependencies,
- SBOM patrí predošlému rebuildu,
- multi-platform variants majú rozdielne dependencies,
- mutable package references sa nedajú neskôr presne resolve-nuť.

SBOM môže byť embedded alebo external attestation; dôležitá je subject identity a integrity.

## 22. Configuration a deployment versioning

Artifact je iba jedna časť runtime state:

```text
runtime state
= artifact/release manifest
+ rendered config
+ secret references/versions
+ infrastructure revision
+ schema/data state
+ feature flag/exposure state
```

Release alebo deployment record má zachovať relevantné revisions. Rovnaký artifact digest môže v dvoch environments fungovať odlišne pre inú config, IAM policy alebo database state.

## 23. Yanking

Yank znamená, že vydaná version zostáva identifikovateľná a historicky dostupná, ale nové dependency resolution alebo bežná discovery ju nemá vyberať.

Použitie:

- release obsahuje závažný bug,
- metadata alebo compatibility declaration je chybná,
- package sa nemá používať pre nové installs,
- existujúci lockfile musí zostať reprodukovateľný.

Yank nemá prepisovať bytes. Musí mať dôvod, actor identity a audit trail.

## 24. Revocation

Revocation je silnejšie bezpečnostné alebo prevádzkové rozhodnutie, že artifact už nie je dôveryhodný alebo povolený na deployment.

Môže spustiť:

- policy denial nových deployments,
- alert pre environments, kde artifact beží,
- incident a rotation credentials,
- rollback alebo roll-forward,
- update trust metadata,
- quarantine v registry.

Fyzické zmazanie nemusí byť okamžite správne, pretože môže zničiť forenznú stopu alebo recovery schopnosť. Rozlišuj „nesmie sa používať“ od „musí sa odstrániť“.

## 25. Retention roots

Garbage collection nesmie rozhodovať iba podľa veku tagu. Artifact môže byť retention root, ak je:

- aktívne nasadený,
- podporovaná production release,
- rollback candidate,
- referencovaný release manifestom,
- predmet incidentu alebo legal hold,
- potrebný pre audit/compliance,
- base dependency pre reprodukciu.

Registry inventory musí vedieť vyhodnotiť references a deployment records. Artifact používaný v produkcii sa nesmie odstrániť preto, že pôvodný CI run expiroval.

## 26. Retention classes

Rozlišuj minimálne:

- transient branch artifacts,
- pull-request candidates,
- failed-build diagnostics,
- release candidates,
- active production releases,
- rollback window,
- supported historical releases,
- revoked/quarantined artifacts,
- compliance/legal evidence.

Každá class má inú retention, access a deletion policy.

## 27. Legal hold a incident hold

Artifact, reports a provenance môžu byť počas vyšetrovania alebo právnej požiadavky chránené pred garbage collection.

Hold record má obsahovať:

- presný scope/digests,
- dôvod,
- ownera,
- čas začiatku,
- access restrictions,
- release podmienku,
- audit zmien.

Hold nemá byť implementovaný iba mutable tagom, ktorý môže niekto odstrániť.

## 28. Registry replication a disaster recovery

Release artifact uložený iba v jednom registry môže byť single point of failure.

Kontroluj:

- replication integrity podľa digestu,
- metadata a signature replication,
- consistency lag,
- access policy v secondary registry,
- restore test,
- behavior aliases pri failoveri,
- retention parity,
- audit logs.

Backup existencie objektu nie je dôkaz, že celý release manifest a všetky variants sa dajú obnoviť.

## 29. Rollback eligibility

Starší artifact je rollback candidate iba vtedy, keď:

- jeho bytes a provenance sú dostupné,
- signature/trust policy ho stále povoľuje,
- config je kompatibilná,
- database/event schema ostala backward-compatible,
- external contracts a data side effects umožňujú návrat,
- deployment tool ho vie nasadiť,
- potrebné secrets/keys/certificates sú dostupné,
- post-rollback validation je definovaná.

Version label bez artifactu alebo compatibility dôkazu nie je rollback capability.

## 30. Artifact deletion

Deletion musí byť chránená operácia. Pred odstránením over:

- active deployments,
- release-manifest references,
- rollback windows,
- legal/incident holds,
- replication state,
- dependency references,
- support policy.

Preferuj staged lifecycle:

```text
mark unreferenced
→ quarantine/deletion candidate
→ grace period
→ final GC
```

## 31. Release notes a artifact identity

Release notes majú odkazovať na konkrétnu logical version aj immutable release/artifact digest. Pri multi-component release majú používať release manifest.

To umožní odpovedať:

- ktoré changes sú v nasadených bytes,
- či hotfix vytvoril nový artifact,
- či rovnaké release notes neboli omylom priradené inému digestu,
- ktoré variants a migrations release obsahuje.

## 32. Typické anti-patterny

### Prepísanie vydanej verzie

`2.8.1` obsahuje iné bytes než pri pôvodnom release. Audit, dependency locks a rollback sú neplatné.

### Production používa iba `latest`

Nie je možné dokázať, čo bolo resolve-nuté v čase deploymentu.

### Rebuild pri promotion

Produkcia nedostáva artifact, ktorý bol testovaný a schválený.

### Version je iba CI run number

Bez project/registry namespace je nejednoznačná a pri migrácii systému stráca význam.

### Signature bez provenance policy

Vieme, kto podpísal digest, ale nevieme, či build vznikol z povoleného source a workflowu.

### SBOM bez subject digestu

Nie je možné dokázať, ku ktorému buildu zoznam dependencies patrí.

### Zmazanie revoked artifactu bez forenznej stopy

Odstráni sa evidence potrebná na incident analýzu.

### Jeden logical version pre rozdielne platform variants bez indexu

Consumers nevedia presne identifikovať, ktorý variant dostali.

### Retention podľa veku pipeline

Môže odstrániť aktívny alebo rollback artifact.

## 33. Diagnostický postup

Pri nejasnosti artifact identity:

1. zisti plný registry/package namespace;
2. resolve-ni logical version alebo tag na digest;
3. porovnaj digest s deployment a evidence recordom;
4. identifikuj manifest/index a platform variant;
5. over source commit, builder, pipeline a provenance;
6. skontroluj publication audit a prípadný tag movement;
7. over signature a trust policy;
8. porovnaj SBOM/report subject digests;
9. skontroluj yanked/revoked/quarantine stav;
10. over retention, replication a rollback eligibility;
11. pri rozdielnom rebuilde porovnaj všetky deklarované a nondeterministické inputs.

## 34. Troubleshooting scenáre

### Rovnaká verzia má dva digesty

Hľadaj mutable publication, parallel race, rebuild, rozdielny platform variant alebo registry replication inconsistency. Vydaná logical version má mať jednoznačný release record.

### Tag ukazuje na iný digest než deployment

Tag sa pohol. Historický deployment diagnostikuj podľa uloženého digestu, nie aktuálneho aliasu.

### Produkcia nevie stiahnuť rollback artifact

Over retention roots, GC, registry replication, credentials, trust/revocation policy a release-manifest references.

### Reproducible rebuild sa nezhoduje

Porovnaj toolchain, base-image digests, dependency locks, timestamps, locale, environment, file ordering, network downloads a random seed.

### Multi-platform release zlyháva iba na arm64

Over child variant digest, provenance, platform-specific SBOM, emulation/cross-build setup a test evidence pre arm64. Index-level scan nemusí pokryť všetky varianty.

## 35. Praktický rozhodovací rámec

1. Aký je artifact namespace a logical version contract?
2. Aký digest identifikuje konkrétny subject?
3. Je version write-once a publication atomic?
4. Ako sa rieši parallel publication collision?
5. Používa promotion pôvodný digest bez rebuildu?
6. Ako sa version mapuje na source, toolchain a build inputs?
7. Aké provenance a signature claims policy vyžaduje?
8. Ako sú viazané SBOM, scans a approvals?
9. Existujú platform variants alebo multi-component release manifest?
10. Ktoré aliases sú mutable a ako sa auditujú?
11. Ako funguje yank a revocation bez prepísania artifactu?
12. Ktoré deployment/config/schema revisions tvoria runtime identity?
13. Aké artifacts sú retention roots?
14. Aká je rollback eligibility a support window?
15. Ako sa registry obnoví pri strate alebo failoveri?

## 36. Kontrolný checklist

Pred release over:

- artifact má plný namespace a logical version,
- content digest je uložený v release recorde,
- publication je create-only alebo write-once,
- candidate nebol pre final release rebuildnutý,
- aliases sú oddelené od immutable identity,
- source, builder a workflow provenance sú dostupné,
- signatures sú overené proti policy,
- SBOM a scan evidence patria rovnakému digestu,
- multi-platform index aj child digests sú známe,
- multi-component release používa immutable manifest,
- config, infra a schema revisions sú zaznamenané,
- rollback artifact a compatibility sú overené,
- retention chráni active, rollback a held artifacts,
- yanking/revocation majú audit trail,
- registry replication a restore sú testované.

## 37. Kontrolné otázky

1. Aký je rozdiel medzi logical version, digestom a deployment identity?
2. Prečo commit SHA nestačí ako úplná artifact identity?
3. Čo znamená plný artifact namespace?
4. Prečo sa release candidate nesmie rebuildovať pri finalizácii?
5. Aký je rozdiel medzi rebuildom a reproducible build verification?
6. Ako sa zabráni parallel publication race?
7. Kedy je mutable alias prijateľný?
8. Ako sa identifikuje multi-platform release?
9. Načo slúži release manifest alebo BOM?
10. Prečo musí byť evidence viazaná na digest?
11. Čo provenance dokazuje a čo nedokazuje?
12. Aký je rozdiel medzi yankingom a revocation?
13. Prečo revoked artifact nemusí byť okamžite zmazaný?
14. Čo je retention root?
15. Kedy je starší artifact skutočne rollback-eligible?
16. Ktoré vrstvy okrem artifactu tvoria runtime version?

## Summary

Artifact versioning spája ľudsky čitateľnú logical version s immutable content digestom, build provenance a deployment evidence. Dôveryhodný lifecycle používa write-once publication, build once/promote many, explicitné multi-platform alebo multi-component manifests, digest-bound signatures, SBOM a gates. Mutable aliases slúžia na discovery, nie na historickú identity. Retention, yanking, revocation, legal hold, registry recovery a rollback eligibility musia byť súčasťou rovnakého lifecycle; samotný názov verzie bez zachovaných bytes a compatibility dôkazu nie je release ani recovery mechanizmus.

## Glossary impact

Relevantné pojmy: artifact version, artifact namespace, logical version, content digest, deployment identity, immutable publication, publication race, release candidate, build metadata, reproducible build, mutable alias, immutable tag, multi-platform index, release manifest, evidence binding, provenance attestation, signature, SBOM, yank, revocation, retention root, legal hold a rollback eligibility.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Reusable a parallel pipelines](reusable-and-parallel-pipelines.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Semantic Versioning →](semantic-versioning.md)
<!-- KNOWLEDGE-NAVIGATION:END -->