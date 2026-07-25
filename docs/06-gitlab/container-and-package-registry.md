# Container a package registry

## Metadata

- Status: Learning
- Level: L2
- Domain: GitLab

GitLab Container Registry a Package Registry distribuujú build outputs medzi pipelines, deploymentmi a consumers. Registry nie je iba storage. Je to publication, identity, access, retention a supply-chain boundary, ktorá musí zachovať väzbu medzi source, buildom, immutable obsahom, evidence a runtime použitím.

## 1. Mental model

```text
source a resolved inputs
→ trusted build
→ immutable content
→ scan / SBOM / provenance / signature
→ authorized publication
→ registry identity
→ promotion alebo dependency resolution
→ runtime consumption
→ retention / yanking / revocation / recovery
```

Každý krok musí pracovať s konkrétnym artifact subjectom, nie iba s mutable názvom.

## 2. Registry namespaces

Registry path je odvodený od GitLab namespace a projektu. Namespace je zároveň:

- ownership boundary,
- authorization scope,
- naming scope,
- lifecycle boundary,
- dependency coordinate,
- audit kontext.

Project transfer alebo group rename môže ovplyvniť image paths, package coordinates, consumers, deploy manifests a token policies. Redirect alebo alias nemá nahradiť riadenú migráciu.

## 3. Artifact identity

Pre container rozlišuj:

- registry host,
- repository path,
- tag,
- manifest,
- OCI index/manifest list,
- platform manifest,
- content digest,
- blob/layer digest.

Pre package rozlišuj:

- registry scope,
- package name,
- version,
- variant/classifier,
- checksum,
- metadata.

Human-readable version komunikuje význam. Digest alebo checksum identifikuje konkrétny obsah.

## 4. Tag verzus digest

Príklad:

```text
registry.example.com/team/app:2.4.1
registry.example.com/team/app@sha256:...
```

Tag je pointer. Digest je content identity. Mutable tags ako `latest`, `main`, `stable` alebo `production` môžu byť vhodné pre discovery alebo channel, ale deployment record musí zachovať digest.

Tag movement musí byť auditovateľný a autorizovaný.

## 5. Package version immutability

Publikovaná package version má byť write-once. Prepísanie verzie mení dependency output bez zmeny consumer source alebo lockfile.

Ak `2.4.1` obsahuje chybu:

- nepíš nové bytes pod `2.4.1`,
- označ verziu ako deprecated/yanked podľa ecosystemu,
- publikuj `2.4.2` alebo novú pre-release verziu,
- aktualizuj advisories a consumers.

Immutability je základ reprodukovateľnosti a auditu.

## 6. Publication subject

Publish job má pracovať s presným subjectom:

- source commit alebo merged-result SHA,
- resolved pipeline configuration,
- build job a attempt,
- artifact digest,
- platform/variant inventory,
- version,
- provenance/SBOM identity,
- publisher identity,
- target namespace.

Job nemá rebuildovať release output tesne pred publishom.

## 7. Publish eligibility

Pred publishom over:

1. pipeline context je oprávnený,
2. ref/tag je chránený podľa policy,
3. version alebo immutable tag ešte neexistuje,
4. artifact digest zodpovedá schválenému build outputu,
5. required tests/scans sú kompletné a čerstvé,
6. package/image metadata je validná,
7. SBOM a provenance patria tomu istému subjectu,
8. publisher identity má minimum scope,
9. target namespace je správny,
10. release record sa dá vytvoriť.

## 8. Atomic publication

Publication môže zlyhať po časti uploadu alebo pri súbežnom jobe.

Bezpečný model:

```text
upload immutable blobs/content
→ verify checksums
→ vytvor manifest/package version
→ over completeness
→ atomicky publikuj release pointer/tag
```

Riadiť treba:

- concurrent publishers,
- duplicate version race,
- partial manifests,
- retry idempotency,
- temporary/staging namespace,
- cleanup orphaned blobs.

„Push job skončil zeleno“ nie je úplný publication oracle, ak registry entry nie je čitateľná a kompletná.

## 9. Build once, promote many

Správny flow:

```text
build content once
→ publish immutable digest/version
→ test a scan konkrétny obsah
→ promotionuj rovnaký digest
→ deploy alebo distribuuj rovnakú identity
```

Promotion môže znamenať:

- pridanie release tagu k rovnakému digestu,
- kopírovanie immutable contentu do chráneného namespace,
- vytvorenie release manifestu,
- zmenu channel aliasu.

Rebuild pre production ruší predchádzajúcu evidence.

## 10. Publisher identity

Oddeľ identity pre:

- development/branch publish,
- release publish,
- signing,
- cleanup/deletion,
- runtime pull,
- cross-project dependency read.

Preferuj:

- job-scoped token tam, kde stačí,
- project/group access token s minimálnym scope,
- deploy token pre obmedzený pull/publish use case,
- workload identity alebo isolated signing service,
- expiration a audit.

Personal token človeka nemá byť trvalá production registry identity.

## 11. Push, pull, delete a policy administration

Tieto capabilities oddeľ:

- publish content,
- move mutable alias,
- pull content,
- delete tag/version,
- delete underlying content,
- meniť cleanup policy,
- meniť access policy.

Identity schopná publishovať release nemá automaticky spravovať cleanup alebo meniť retention roots.

## 12. Untrusted pipelines

Merge-request alebo fork pipeline nemá:

- publishovať do release namespace,
- vytvárať chránené version tags,
- používať signing identity,
- prepísať shared package version,
- meniť cleanup policy.

Môže publikovať do izolovaného ephemeral namespace s TTL, ak to workflow potrebuje.

## 13. Container build trust

Image build job môže byť privilegovaný. Preferuj:

- rootless builder,
- dedikovaný ephemeral pool,
- žiadny host Docker socket,
- pinned base images,
- explicitný build context,
- secret mounts namiesto copy do layers,
- network allowlist,
- reproducible alebo aspoň fully traceable inputs,
- provenance generation.

`.dockerignore` je jedna ochrana. Build context, generated files a multi-stage copy musia byť auditované.

## 14. Base images

Tag base image môže zmeniť obsah bez zmeny Dockerfile.

Riadený model:

- pin digest,
- používaj approved catalog,
- automatizuj kontrolované updates,
- rebuildni dependent images pri security patchi,
- sleduj provenance a license,
- testuj compatibility.

Starý digest je reprodukovateľný, nie automaticky bezpečný. Patching a reproducibility musia fungovať spolu.

## 15. Multi-platform images

OCI index mapuje platformy na konkrétne manifests:

```text
release tag / index digest
├── linux/amd64 digest
├── linux/arm64 digest
└── windows/amd64 digest
```

Fan-in job musí poznať expected platform inventory a overiť:

- všetky required variants existujú,
- každá patrí rovnakému source/release subjectu,
- platform metadata je správna,
- scan/test evidence existuje per variant,
- duplicate alebo missing variant spôsobí incomplete verdict.

Úspešný amd64 build nedokazuje arm64 release.

## 16. SBOM

SBOM má byť viazaný na konkrétny digest alebo package checksum. Uchovaj:

- format/version,
- generator identity,
- source artifact identity,
- component inventory,
- creation timestamp,
- completeness limitations.

SBOM pre source tree nemusí zodpovedať dependencies skutočne zabudovaným do final image.

## 17. Provenance a attestations

Provenance odpovedá:

- kto build vykonal,
- z akého source,
- akou pipeline konfiguráciou,
- na akom runner/toolchain-e,
- s akými vstupmi,
- aký digest vznikol.

Deployment alebo consumer policy môže požadovať dôveryhodného buildera, protected source, konkrétny workflow a platnú attestation.

## 18. Signing a verification

Podpis dokazuje integritu a podpisujúcu identity podľa použitého modelu. Nedokazuje funkčnosť ani neprítomnosť zraniteľností.

Signing identity:

- nesmie byť dostupná untrusted jobom,
- má byť krátkodobá alebo izolovaná,
- potrebuje audit,
- má podpisovať presný digest,
- musí mať revocation/rotation model.

Verification patrí pred promotion a deployment, nie iba pri publishnutí.

## 19. Container scanning

Scan viaž na digest a platformu. Rozlišuj:

- analyzer success,
- database freshness,
- OS a language package coverage,
- findings,
- severity a fix availability,
- exception/waiver,
- continuous re-evaluation po update vulnerability databázy.

Absencia reportu nie je čistý image.

## 20. Package publishing

Publish workflow pre package má overiť:

- version syntax,
- package coordinates,
- version non-existence,
- checksum,
- metadata a dependencies,
- test evidence,
- publisher identity,
- release notes/changelog podľa potreby,
- support policy.

Package manager-specific metadata je súčasť contractu. Nesprávny dependency range alebo classifier môže rozbiť consumers aj pri správnom binary.

## 21. Generic packages

Generic registry je vhodný pre release bundles, CLI binaries alebo assets bez natívneho ecosystem protocolu.

Aj generic package potrebuje:

- názov a immutable version,
- digest/checksum,
- platform/variant,
- content type,
- provenance,
- retention a access,
- consumer documentation.

Generic package nemá byť anonymný file dump.

## 22. Dependency resolution

Consumer musí určiť:

- allowed registries,
- priority/order,
- package scope,
- version range alebo pin,
- lockfile,
- checksum/signature,
- proxy/cache behavior,
- fallback policy.

Registry publishing a consuming sú dve odlišné trust boundaries.

## 23. Dependency confusion

Ak interný názov existuje aj vo verejnom registry, resolver môže zvoliť útočníkov package.

Ochrany:

- scoped namespaces,
- explicitný registry endpoint a priority,
- interná rezervácia názvov,
- lockfiles a checksums,
- no-public-fallback policy pre private scope,
- egress control,
- dependency allowlist,
- provenance verification.

## 24. Dependency Proxy a virtual registries

Proxy alebo virtual registry môže znížiť upstream rate-limit a availability risk.

Nevytvára automaticky dôveru. Riadiť treba:

- povolené upstreams,
- cache identity a invalidáciu,
- provenance pôvodu,
- mutable upstream tags,
- namespace collision,
- malware/vulnerability policy,
- retention.

Consumer má vedieť, či používa interný artifact alebo cached external content.

## 25. Cross-project access

Job-token alebo access-token policy pre cross-project pull/publish má byť explicitná:

- source project,
- target registry/package scope,
- read verzus write,
- protected context,
- expiration,
- audit,
- dependency ownership.

Group-wide read môže byť primeraný pre shared libraries; group-wide write je podstatne citlivejší.

## 26. Mutable aliases a channels

Tags/channels ako `latest`, `stable`, `beta` alebo `production` môžu byť užitočné, ale potrebujú:

- ownera,
- allowed publishera,
- atomic movement,
- audit old→new digest,
- rollback policy,
- consumer expectations,
- zákaz používať alias ako jedinú deployment identity.

Channel movement je release event.

## 27. Yanking, deprecation a revocation

Rozlišuj:

- **Deprecation —** verzia je podporovaná obmedzene alebo sa neodporúča pre nové použitie.
- **Yanking —** resolver ju nemá vybrať pre nové installs, ale existujúce lockfiles ju môžu stále potrebovať.
- **Revocation —** obsah je známy ako kompromitovaný alebo neakceptovateľný a policy má jeho použitie blokovať.
- **Deletion —** content alebo reference sa fyzicky odstráni.

Security incident často vyžaduje revocation a consumer notification, nie iba delete tagu.

## 28. Revocation propagation

Pri kompromitovanom artifacte:

1. identifikuj všetky tags/versions a digests,
2. zablokuj nový pull/deploy podľa policy,
3. zisti aktívne deployments a consumers,
4. publikuj opravenú version,
5. rotuj signing/publish credentials podľa potreby,
6. aktualizuj advisory a release records,
7. over runtime replacement,
8. zachovaj forensic evidence.

Registry delete samo neodstráni image z bežiaceho node cache alebo nainštalovaný package.

## 29. Cleanup roots

Cleanup policy musí zachovať content referencovaný:

- aktívnym deploymentom,
- podporovaným releaseom,
- rollback window,
- release manifestom,
- aktívnym release candidate,
- legal/compliance holdom,
- security/incident vyšetrovaním,
- downstream consumers podľa support policy.

Regex podľa tagu bez referenčného inventory je nedostatočný.

## 30. Tags, manifests a garbage collection

Odstránenie tagu nemusí odstrániť manifest alebo blobs. Garbage collection musí rešpektovať všetky references.

Over:

- soft-delete/retention obdobie,
- concurrent pulls/pushes,
- active manifests/indexes,
- registry replication,
- object storage consistency,
- backup a recovery.

GC je storage operation s data-loss rizikom, nie iba housekeeping.

## 31. Consumer inventory

Pred yankingom alebo cleanupom potrebuješ vedieť:

- ktoré pipelines package používajú,
- ktoré lockfiles/verzie sú aktívne,
- ktoré deployments používajú digest,
- ktoré offline clients ešte potrebujú package,
- support a EOL policy,
- mirrors a air-gapped environments.

Bez consumer inventory je deletion risk rozhodnutie naslepo.

## 32. Registry availability

Registry je kritická delivery dependency. Sleduj:

- push/pull latency a error rate,
- authentication failures,
- storage a object-store health,
- manifest/blob consistency,
- replication lag,
- certificate expiration,
- queue/backlog,
- backup/restore,
- cleanup/GC failures.

Runtime má používať immutable references a lokálne pull policies primerané dostupnosti; nemá závisieť od pohybu mutable tagu pri každom štarte.

## 33. Backup a replication

Pre release registry over:

- metadata a blob backup,
- konzistenciu medzi databázou a object storage,
- encryption keys,
- restore test,
- replication topology,
- RPO/RTO,
- obnovu permissions, tags a attestations,
- schopnosť overiť digests po restore.

Backup blobs bez registry metadata nemusí obnoviť použiteľný registry.

## 34. Registry compromise response

Pri podozrení na kompromitáciu:

- zastav alebo obmedz publishing,
- revokuj publisher a signing identities,
- identifikuj zmenené tags/versions a digests,
- porovnaj audit log, provenance a trusted manifests,
- blokuj neoverené content,
- audituj deployments a consumers,
- obnov registry/control plane z dôveryhodného stavu,
- republishni alebo znovu podpíš iba overené artifacts,
- rotuj downstream credentials,
- dokumentuj affected window.

Tag history a immutable digest inventory sú kľúčové pre scope incidentu.

## 35. Diagnostický postup

Keď publish alebo pull zlyhá:

1. identifikuj registry host, namespace a artifact coordinates,
2. over token type, scope, expiration a subject,
3. over protected pipeline context,
4. rozlíš tag, version, manifest a digest,
5. skontroluj platform variant,
6. over certificate, DNS a object storage,
7. porovnaj registry digest s release/deployment recordom,
8. over cleanup/yank/revocation state,
9. pri package resolution skontroluj registry priority a lockfile,
10. uchovaj audit pred retry alebo republishom.

## 36. Typické anti-patterny

### Rebuild pod rovnakým release tagom

Produkcia dostáva iné bytes než tie, ktoré prešli testami.

### Prepísateľná package version

Consumer build sa mení bez zmeny lockfile alebo source.

### Untrusted pipeline publikuje do release namespace

Nedôveryhodný kód vstupuje priamo do supply chainu.

### Signing key na shared runneri

Iný job môže kľúč zneužiť alebo exfiltrovať.

### Multi-platform tag bez completeness checku

Niektorá platforma chýba alebo patrí inému build subjectu.

### Cleanup iba podľa veku alebo regexu

Odstráni active deployment alebo rollback artifact.

### Delete kompromitovaného tagu bez revocation

Bežiace systémy a cached consumers pokračujú v používaní obsahu.

### Personal token ako runtime pull identity

Dostupnosť aplikácie závisí od účtu človeka.

## 37. Praktický rozhodovací rámec

Pre každý registry workflow odpovedz:

1. Aký je artifact subject a immutable identity?
2. Kto smie publishovať, aliasovať, mazať a meniť policy?
3. Ako sa zabráni prepísaniu version/tagu?
4. Je publication atomická a retry-safe?
5. Sú všetky platform/variant outputs kompletné?
6. Aké SBOM, provenance, scan a signature evidence existuje?
7. Ako consumer overuje pôvod a integrity?
8. Ako sa rieši dependency confusion?
9. Ktoré retention roots chránia obsah?
10. Ako sa verzia deprecates, yanks alebo revokes?
11. Ako sa registry zálohuje a obnovuje?
12. Aký je postup pri kompromitácii publishera alebo registry?

## 38. Kontrolný checklist

- registry paths zodpovedajú ownershipu;
- release versions a immutable tags sú write-once;
- deployment používa digest;
- publication používa oprávnenú non-human identity;
- untrusted pipelines nemajú release write access;
- multi-platform fan-in kontroluje inventory;
- SBOM/provenance/signature patria rovnakému digestu;
- consumeri používajú lock/checksum/policy;
- dependency sources a priority sú explicitné;
- aliases majú audit old→new digest;
- yanking, revocation a deletion sú rozlíšené;
- cleanup používa retention roots;
- registry má restore-tested backup;
- compromise response zahŕňa deployments a consumers.

## 39. Kontrolné otázky

1. Aký je rozdiel medzi tagom, digestom, manifestom a OCI indexom?
2. Prečo package version musí byť immutable?
3. Čo tvorí publication subject?
4. Ako funguje atomic publish?
5. Čo znamená build once, promote many v registry?
6. Ktorá identity má smieť publishovať release?
7. Ako overiť completeness multi-platform image?
8. Prečo SBOM musí byť viazaný na final digest?
9. Aký je rozdiel medzi signing a security verification?
10. Ako vzniká dependency confusion?
11. Aký je rozdiel medzi deprecation, yanking, revocation a deletion?
12. Čo sú cleanup roots?
13. Prečo delete tagu neodstráni bežiaci kompromitovaný image?
14. Čo musí obsahovať registry recovery plán?

## Summary

GitLab registry je supply-chain boundary od publication cez promotion až po runtime consumption. Bezpečný model používa immutable package versions a content digests, autorizovaného publishera, atomic publish, build-once-promote-many, per-platform completeness, SBOM, provenance, signing a verification. Consumers potrebujú explicitný registry a dependency policy. Cleanup musí rešpektovať deploymenty, support a rollback roots. Yanking, revocation a deletion majú rozdielny účel a registry compromise response musí pokryť aj všetky nasadené a cached copies.

## Glossary impact

Relevantné pojmy: GitLab Container Registry, GitLab Package Registry, registry namespace, OCI digest, image tag, manifest, OCI index, package coordinates, immutable version, atomic publication, dependency proxy, virtual registry, dependency confusion, artifact yanking, revocation, cleanup root a registry recovery.

## Oficiálna dokumentácia

- [Packages and registries](https://docs.gitlab.com/user/packages/)
- [Container Registry](https://docs.gitlab.com/user/packages/container_registry/)
- [Package Registry](https://docs.gitlab.com/user/packages/package_registry/)
- [Dependency Proxy](https://docs.gitlab.com/user/packages/dependency_proxy/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Artifacts a cache](artifacts-and-cache.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Environments, deployments a releases →](environments-deployments-releases.md)
<!-- KNOWLEDGE-NAVIGATION:END -->