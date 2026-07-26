# Container a package registry

## Metadata

- Status: Learning
- Level: L2
- Domain: GitLab

GitLab Container Registry a Package Registry sú supply-chain boundaries. Spájajú build output s immutable content identity, publication authorization, evidence, dependency resolution, runtime consumption, retention a revocation.

```text
trusted build subject
→ immutable content a variant inventory
→ tests/scans/SBOM/provenance
→ authorized atomic publication
→ immutable version alebo digest
→ promotion/channel alias
→ verified consumer resolution
→ runtime inventory
→ support, cleanup, yanking alebo revocation
```

Registry path alebo tag je iba reference. Dôveryhodný release chain musí vždy vedieť, ktoré konkrétne bytes boli publikované, schválené, stiahnuté a spustené.

## 1. Nosný model: publication-to-consumption protocol

Registry workflow má dve odlišné trust boundaries:

```text
publication
→ kto smie zapísať aký content pod akú identity

consumption
→ z ktorého registry a podľa akej policy sa content vyberie a overí
```

Publisher môže byť dôveryhodný a consumer resolver stále vybrať zlý registry. Consumer môže pinovať digest, ale digest mohol vzniknúť na kompromitovanom builderi. Preto sa identity, integrity, provenance a policy nesmú zlievať do jednej kontroly.

## 2. Nosný scenár: Atlas Payments release 3.12.0

Atlas vytvára multi-platform image:

```text
release subject R120
source SHA S42
resolved CI config C19
amd64 manifest digest D-amd64
arm64 manifest digest D-arm64
OCI index digest D-index
package version 3.12.0
SBOM B42
provenance A42
signature SIG42
```

Publication lifecycle:

```text
platform builds vytvoria immutable manifests
→ každý variant prejde tests a scanom
→ fan-in overí expected inventory {amd64, arm64}
→ OCI index D-index sa vytvorí z oboch digestov
→ publisher overí release eligibility
→ publikuje version 3.12.0 a immutable index
→ alias stable sa CAS-presunie old→D-index
→ deployment manifest používa D-index
→ runtime inventory potvrdí platform-specific digests
```

Package a image sa nerebuildnú pri promotion do production.

## 3. Namespace je ownership a dependency coordinate

Registry path určuje:

- ownership a access scope;
- naming a collision boundary;
- lifecycle a cleanup policy;
- dependency coordinate;
- audit context;
- cross-project token policy.

Project transfer alebo group rename môže zmeniť image/package coordinates, includes, consumers a OIDC/token claims. Redirect nie je úplná migrácia; treba inventory a post-transfer verification.

## 4. Tag, version, manifest a digest nie sú synonymá

Pre container:

```text
repository path
→ tag alebo digest reference
→ OCI index/manifest
→ platform manifest
→ blobs/layers
```

- **Tag:** mutable alebo policy-immutable pointer.
- **Digest:** content-derived identity manifestu/indexu.
- **OCI index:** mapuje platformy na platform manifests.
- **Layer/blob digest:** identifikuje časť image contentu.

Pre package:

```text
registry scope + package name + version + variant/classifier + checksum
```

Human-readable version komunikuje release význam. Checksum/digest identifikuje bytes.

## 5. Publication subject

Publish decision patrí:

```text
source/candidate SHA
resolved pipeline config
build jobs a attempts
artifact a variant digests
runner/toolchain provenance
version
SBOM/scan/signature identities
publisher identity
target registry namespace
release policy revision
```

Job nemá buildnúť nový content tesne pred publishom. Ak sa digest zmení, vznikol nový subject a predchádzajúce tests alebo approvals sa nemusia preniesť.

## 6. Publish eligibility je odvodený verdict

Atlas povoľuje publish iba keď:

```text
trusted pipeline/ref context
+ immutable version ešte neexistuje
+ expected variant inventory complete
+ artifact digests patria approved build subjectu
+ required tests/scans complete a fresh
+ SBOM/provenance/signature patria rovnakým digestom
+ publisher má minimum write scope
+ target namespace je správny
+ release record možno uzavrieť
→ ELIGIBLE
```

Missing arm64 scan, parser failure alebo chýbajúca provenance znamenajú incomplete, nie clean release.

## 7. Atomic publication a unknown outcome

Safe publication:

```text
upload immutable blobs
→ over digests
→ vytvor platform manifests
→ vytvor OCI index/package version
→ over registry read-back a completeness
→ atomicky publishni release reference/alias
```

Pri timeout-e response nemusí byť známe, či write prešiel. Retry sa najprv reconciliuje podľa version, digestu a idempotency keya. Blind republish môže naraziť na collision alebo prepísať alias novším/nesprávnym digestom.

Write-once version collision s odlišným digestom je hard failure.

## 8. Build once, promote many

Promotion znamená prácu s rovnakým obsahom:

```text
D-index candidate
→ tests/scans/signature nad D-index
→ staging deployment D-index
→ release approval D-index
→ production deployment D-index
```

Môže sa pridať nový immutable release tag, kopírovať content do chráneného namespace-u alebo posunúť channel alias. Rebuild pre environment vytvára iné bytes a invaliduje evidence.

## 9. Publisher identities sú oddelené podľa capability

Atlas oddeľuje:

- branch/ephemeral publish;
- release publish;
- signing;
- alias movement;
- cleanup/delete;
- runtime pull;
- policy administration.

Release publisher nemá automaticky právo mazať blobs alebo meniť cleanup policy. Untrusted MR pipeline smie publikovať iba do izolovaného TTL namespace-u, nie do release pathu.

Personal token človeka nie je trvalá supply-chain identity.

## 10. Build a signing trust

Container build je privileged operation podľa buildera. Atlas používa:

- explicitný build context a `.dockerignore`;
- pinned base-image digests;
- isolated ephemeral builder;
- secret mounts, nie copy do layers;
- restricted network;
- identified runner/toolchain;
- provenance generation.

Signing identity podpisuje presný digest a nie je dostupná build/MR jobom. Podpis dokazuje integritu a signer identity, nie funkčnosť alebo absenciu vulnerabilities.

## 11. Multi-platform completeness

Fan-in pozná expected inventory:

```text
expected = linux/amd64, linux/arm64
received = manifest digests + test/scan evidence per platform
```

OCI index sa nevytvorí, ak:

- variant chýba;
- variant patrí inému source alebo config subjectu;
- platform metadata nesedí;
- scan/test report chýba;
- duplicate platform má viac nejednoznačných digestov.

Úspešný amd64 image nie je complete multi-platform release.

## 12. SBOM, provenance, scan a signature sa viažu na digest

- **SBOM:** inventory komponentov final image/package-u.
- **Provenance:** source, pipeline, builder, toolchain a inputs, ktoré digest vytvorili.
- **Scan:** findings a analyzer/database freshness pre konkrétny digest/platformu.
- **Signature:** kryptografická väzba signer identity na digest.

Source-tree SBOM nemusí zodpovedať final image. Scan tagu môže po pohybe aliasu opisovať iný content. Evidence musí používať immutable digest.

## 13. Consumer resolution je samostatná policy

Consumer určuje:

```text
allowed registries a priority
package scope
version range alebo pin
lockfile
checksum/signature/provenance policy
proxy/cache behavior
public fallback
```

Dependency confusion vzniká, keď interný package name môže resolver vybrať z verejného registry. Ochrany zahŕňajú scoped namespaces, explicitný endpoint, no-public-fallback pre private scope, lockfile, checksums a egress policy.

Dependency proxy zvyšuje availability a cache efficiency, ale neprepisuje origin trust. Consumer musí vedieť, či používa interný content alebo cached upstream.

## 14. Runtime consumption potrebuje effective digest inventory

Deployment record uchováva D-index, ale runtime na platforme používa konkrétny platform manifest digest.

```text
release index D-index
→ amd64 nodes resolve D-amd64
→ arm64 nodes resolve D-arm64
```

Atlas sleduje:

- requested reference;
- resolved index/manifest digest;
- node/platform;
- pull/mirror source;
- running workload digest;
- deployment/release relation.

Mutable alias ako `stable` nesmie byť jedinou runtime identity.

## 15. Mutable aliases sú release transitions

Alias movement:

```text
expected current digest D-old
→ authorized CAS move
→ new digest D-index
→ read-back verification
→ audit old→new
→ consumer/runtime observation
```

Alias potrebuje ownera, allowed publishera, rollback policy a atomic semantics. Concurrent jobs nemajú „posledný write vyhrá“ meniť production channel.

## 16. Retention a cleanup používajú reference roots

Zachovaj content referencovaný:

- active deploymentom;
- supported releaseom;
- rollback windowom;
- release manifestom;
- incidentom alebo forensic holdom;
- air-gapped/offline consumers;
- support/EOL policy.

Tag regex a vek nie sú complete graph. Odstránenie tagu nemusí odstrániť manifest/blob a garbage collection môže odstrániť content stále potrebný nepriamou reference.

GC je data-loss-sensitive storage transition s backup a restore contractom.

## 17. Yanking, revocation a deletion majú odlišný význam

- **Deprecation:** verzia sa neodporúča alebo má obmedzenú podporu.
- **Yanking:** resolver ju nemá vyberať pre nové installs, no locknuté consumers ju môžu potrebovať.
- **Revocation:** policy musí blokovať content ako kompromitovaný/neakceptovateľný.
- **Deletion:** fyzicky sa odstráni reference alebo content.

Delete tagu nezastaví bežiace workloads ani node caches. Security response potrebuje digest revocation, consumer inventory a runtime replacement.

## 18. Worked failure: production tag bol prepísaný novým rebuildom

Release `3.12.0` prešiel tests ako digest `D42`. Production publish job namiesto promotion znovu buildol image a prepísal tag `3.12.0` na `D43`.

```text
source SHA rovnaký
→ base image tag sa medzitým posunie
→ rebuild vytvorí D43
→ tag 3.12.0 ukazuje na D43
→ approval a scan stále patria D42
→ nové nodes pullnú D43, staré cache používajú D42
```

### Príčina

Tag/version sa považovali za identity contentu a production publish obsah rebuildoval. Version nebola write-once.

### Dôsledok

Jedna release version reprezentovala dve sady bytes a fleet sa rozdelila podľa pull času.

### Trvalá náprava

```text
build once
→ immutable digest D42
→ evidence viazaná na D42
→ package/image version collision s iným digestom hard fail
→ promotion iba rovnakého contentu
→ runtime digest inventory
```

## 19. Worked failure: multi-platform index bol publikovaný bez arm64

Arm64 build skončil runner system failure-om. Fan-in iteroval iba cez existujúce manifests a vytvoril OCI index s amd64.

```text
amd64 manifest existuje
→ arm64 output absent
→ index creation success
→ tag 3.12.0 published
→ amd64 deployment prejde
→ arm64 nodes hlásia no matching manifest
```

### Príčina

Actual variant inventory bolo zamieňané za expected release inventory. Publication gate nevyžadoval per-platform evidence.

### Náprava

Expected platform manifest je immutable input release contractu. Missing variant alebo scan vytvára `INCOMPLETE` a publication sa nevykoná.

## 20. Worked failure: delete tagu nevyradil kompromitovaný image

Publisher token bol kompromitovaný a alias `stable` bol krátko presunutý na škodlivý digest `D-bad`. Tím tag vymazal a považoval incident za uzavretý.

```text
niektoré nodes už pullli D-bad
→ tag sa odstráni
→ running containers a node cache ostanú
→ deployment manifest stále používa digest D-bad
→ ďalšie restarty z lokálnej cache pokračujú
```

### Príčina

Deletion sa zamieňala za revocation a runtime remediation. Chýbal digest-centric consumer inventory.

### Recovery

Atlas revoke-ol publisher/signing identities, zablokoval D-bad v admission/deployment policy, inventarizoval workloads a caches, nasadil opravený digest a overil runtime replacement.

## 21. Kauzálny diagnostický walkthrough

Symptom: dva production nodes používajú odlišné digests, hoci oba deployments deklarujú tag `3.12.0`.

### Krok 1 — stabilizuj publication a consumption subjects

```text
release version/tag
current a historical tag→digest mapping
release-approved digest
OCI index a platform manifests
node architectures
pull/mirror/cache source
running workload digests
publisher/audit timeline
```

### Krok 2 — konkurenčné hypotézy

```text
H1: tag bol prepísaný alebo alias sa posunul
H2: nodes riešia rôzne platform manifests rovnakého OCI indexu
H3: registry mirror/replication je stale
H4: local node cache používa starý digest
H5: deployment manifest alebo imagePullPolicy sa líši
H6: neautorizovaný publisher zmenil registry state
```

### Krok 3 — observation points

- tag history a audit testujú H1/H6;
- index manifest a architecture testujú H2;
- registry/mirror digest read-back testuje H3;
- runtime/container a local cache inventory testuje H4;
- rendered deployment config testuje H5.

Atlas zistí, že tag `3.12.0` bol prepísaný z D42 na D43; starý node používa cached D42 a nový pullol D43. H1/H4 sú potvrdené.

### Krok 4 — contain-ni publication boundary

Publisher identity sa pause-ne, mutable version sa zablokuje a ďalšie rollouts sa zastavia. D42 aj D43 sa uchovajú ako evidence.

### Krok 5 — obnov jeden dôveryhodný subject

Atlas zvolí schválený digest D42 alebo nový opravený immutable release podľa security/compatibility stavu, explicitne ho nasadí a overí všetky runtime platform digests.

### Krok 6 — vráť learning

Finding sa mení na write-once package policy, CAS alias movement, registry audit alert a runtime digest drift detection.

## 22. Registry compromise a recovery

Pri compromise:

```text
stop publishing a alias movement
→ revoke publisher/signing identities
→ preserve audit, tags, versions a digests
→ porovnaj trusted release manifests/provenance
→ block unverified digests
→ inventory deployments, caches, mirrors a consumers
→ republish iba verified content
→ replace runtime
→ rotate downstream credentials
```

Backup musí obnoviť metadata aj blobs, permissions, tags, attestations a digest integrity. Blob backup bez registry metadata nemusí vytvoriť použiteľný registry.

## 23. Diagnostický runbook

1. Urči host, namespace, coordinates, version/tag a digest.
2. Zostav publication subject a publisher identity.
3. Over version immutability, tag history a atomic publish outcome.
4. Porovnaj expected a actual platform/package variant inventory.
5. Viaž tests, scan, SBOM, provenance a signature na digest.
6. Pri pull-e over resolver registry priority, lockfile, proxy a checksum policy.
7. Porovnaj requested reference, resolved digest a runtime digest.
8. Skontroluj yanking/revocation/cleanup/GC state a consumer roots.
9. Pri nejasnej integrite zastav publication/deployment a zachovaj evidence.
10. Zmeň finding na publication, identity, resolver, retention alebo revocation control.

## 24. Referenčné pravidlá

- Registry je publication aj consumption trust boundary.
- Tag je pointer; digest je content identity.
- Package/release version má byť write-once.
- Publish subject zahŕňa build attempt, varianty, evidence a publishera.
- Atomic publish potrebuje idempotency a read-back verification.
- Build once, promote many zachováva rovnaký digest.
- Multi-platform release potrebuje expected variant inventory.
- SBOM, scan, provenance a signature patria immutable digestu.
- Consumer registry priority a fallback sú security policy.
- Runtime inventory používa resolved digests.
- Cleanup rešpektuje deployment/support/rollback roots.
- Revocation nie je deletion.

## 25. Časté omyly

### „Version tag identifikuje bytes“

Ak je prepísateľný, môže reprezentovať viac digestov.

### „Publish job je green, release je kompletný“

Variant, evidence alebo registry read-back môžu chýbať.

### „Podpísaný image je bezpečný“

Podpis nepreukazuje funkčnosť ani vulnerability status.

### „Dependency proxy je trusted source“

Je to cache/proxy; origin a verification policy zostávajú dôležité.

### „Delete kompromitovaného tagu vyrieši incident“

Running workloads, caches, lockfiles a mirrors môžu content ďalej používať.

## 26. Zhrnutie

Dôveryhodný Atlas registry lifecycle je:

```text
identified trusted build subject
→ complete immutable variant content
→ digest-bound tests/scans/SBOM/provenance/signature
→ authorized atomic write-once publication
→ controlled alias/promotion
→ verified resolver a runtime digest inventory
→ reference-aware retention
→ explicit yanking/revocation/recovery
```

Registry troubleshooting nesmie zostať pri názve tagu alebo HTTP chybe. Musí rekonštruovať publication identity, actual content graph, resolver path a runtime digest a potom overiť, že recovery odstránila nežiaduce bytes zo všetkých aktívnych consumers.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Artifacts a cache](artifacts-and-cache.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Environments, deployments a releases →](environments-deployments-releases.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
