# SBOM

Software Bill of Materials je machine-readable inventory komponentov a vzťahov, ktoré tvoria konkrétny software artifact alebo system. SBOM poskytuje transparency layer pre vulnerability response, license governance, procurement a supply-chain analysis. Nie je sama osebe dôkazom bezpečnosti ani úplnosti.

## 1. Mentálny model

```text
konkrétny software subject
→ components
→ versions a identifiers
→ dependency relationships
→ generation context
→ signed alebo attested SBOM
→ ingestion, matching a operational decisions
```

Základná otázka nie je „máme SBOM?“, ale:

```text
Ku ktorému presnému artifactu patrí?
→ Ako vznikla?
→ Aká je jej completeness, accuracy a freshness?
→ Ako ju consumer použije?
```

## 2. Definícia

SBOM je formálny záznam software components a supply-chain relationships.

Môže opisovať:

- application package,
- container image,
- firmware,
- virtual-machine image,
- operating-system image,
- library,
- appliance,
- deployed service alebo system.

Subject musí byť jednoznačne identifikovaný.

## 3. Čo SBOM nie je

SBOM nie je automaticky:

- vulnerability scan,
- VEX statement,
- build provenance,
- signature,
- license approval,
- malware analysis,
- source-code review,
- runtime inventory,
- guarantee completeness.

Tieto evidence types sa dopĺňajú, ale nemajú sa zamieňať.

## 4. Producer a consumer

### Producer

Generuje SBOM z source, dependency resolvera, build outputu alebo binary analysis.

### Consumer

Validuje subject, formát, signature, completeness a používa inventory na konkrétny decision.

### Distributor

Prenáša SBOM spolu s artifactom alebo cez samostatný trusted channel.

## 5. SBOM subject identity

Subject identity má obsahovať immutable reference:

```text
artifact digest
```

Doplniť možno:

- package URL,
- name a version,
- supplier,
- repository,
- platform,
- architecture,
- release identifier.

Tag alebo filename bez digestu nie je dostatočný binding.

## 6. Lifecycle stage

SBOM môže vzniknúť v rôznych stages:

- design SBOM,
- source SBOM,
- build SBOM,
- analyzed SBOM,
- deployed SBOM,
- runtime-observed inventory.

Tieto inventories nemusia byť identické. Build môže pridať generated code, static libraries, OS packages alebo bundled assets.

## 7. Generation time

Preferovaný production flow:

```text
resolve dependencies
→ build artifact
→ analyzuj final output
→ generuj SBOM
→ bind SBOM na artifact digest
→ sign alebo attest
→ publish spolu s artifactom
```

Source-only generation je rýchla, ale môže minúť post-build content.

## 8. Minimum data contract

Praktický baseline obsahuje:

- SBOM format a specification version,
- document namespace alebo serial identifier,
- creation timestamp,
- creator/tool identity,
- primary component alebo subject,
- component name,
- component version,
- supplier alebo origin, ak je známy,
- unique identifiers,
- hashes, ak sú dostupné,
- relationships/dependency graph,
- license fields podľa use case-u.

Unknown value má byť explicitný, nie vymyslený.

## 9. SPDX

SPDX 3.0.1 je system-oriented data model s Core a domain profiles.

Môže reprezentovať:

- software packages a files,
- relationships,
- licensing,
- security information,
- build a AI-related information podľa profiles,
- external identifiers a references.

SPDX 3.x sa výrazne líši od lineárnejšieho SPDX 2.x document modelu. Consumer musí deklarovať podporovanú verziu a serialization.

## 10. SPDX profiles a serialization

SPDX 3.0 používa profile-oriented model nad Core concepts.

Dáta možno serializovať napríklad ako JSON-LD alebo canonical JSON podľa specification.

Canonical serialization pomáha:

- deterministic hashing,
- signing,
- deduplication,
- stable comparison.

Producer nemá označiť výstup ako SPDX 3.0.1, ak tool v skutočnosti generuje SPDX 2.3.

## 11. CycloneDX

CycloneDX 1.7 je BOM štandard pre software, hardware, services, cryptographic assets a ďalšie supply-chain data.

Core model zahŕňa:

- metadata,
- components,
- services,
- dependency relationships,
- compositions,
- formulation,
- vulnerabilities,
- annotations a properties.

CycloneDX BOM môže byť širšia než klasická SBOM.

## 12. Výber formátu

Vyber podľa:

- ecosystem support,
- consumer requirements,
- required semantics,
- tool compatibility,
- signing a distribution model,
- license a vulnerability workflows,
- long-term interoperability.

„Podporujeme JSON“ nie je formátová kompatibilita. Potrebná je konkrétna specification version a schema validation.

## 13. Component identity

Component identity sa skladá z viacerých signals:

```text
ecosystem
+ namespace
+ name
+ version
+ qualifiers
+ digest
+ supplier/origin
```

Žiadne jedno pole nemusí byť globálne dostačujúce.

## 14. Package URL

Package URL štandardizuje package identity:

```text
pkg:type/namespace/name@version?qualifiers#subpath
```

Príklad:

```text
pkg:npm/%40example/orders@2.4.1
```

Purl pomáha pri vulnerability matchingu, ale nezaručuje, že bytes pochádzajú z očakávaného registry alebo supplier-a. Digest a provenance dopĺňajú identity.

## 15. CPE

Common Platform Enumeration sa používa najmä pri product/platform matchingu v vulnerability databázach.

Limity:

- nepresné vendor/product mappingy,
- slabá coverage language packages,
- version ambiguity,
- distribution backports.

Purl a CPE možno uchovávať súčasne pre rôzne matching use cases.

## 16. Cryptographic hashes

Hash viaže component record na konkrétny content.

Použi schválený algorithm a eviduj:

- algorithm,
- digest,
- scope hashovania,
- serialization alebo archive semantics.

Hash package archive-u sa môže líšiť od hash-u extracted files alebo registry manifestu.

## 17. Relationships

SBOM bez relationships je flat inventory.

Dôležité vzťahy:

- contains,
- dependsOn,
- dependencyOf,
- generatedFrom,
- builtFrom,
- bundledWith,
- variantOf,
- distributedAs.

Relationship semantics sa líšia podľa formátu. Consumer ich nesmie slepo prekladať.

## 18. Direct a transitive graph

```text
application
├─ direct dependency A
│  └─ transitive dependency C
└─ direct dependency B
   └─ transitive dependency D
```

Operational response potrebuje celý resolved graph, aby zistil:

- exposure,
- path k componentu,
- ownera priamej dependency,
- update path,
- počet affected artifacts.

## 19. Dependency scope

Rozlišuj:

- runtime,
- required,
- optional,
- development,
- test,
- build-only,
- provided/external.

Development dependency nemusí byť v runtime artifacte, ale môže ovplyvniť build integrity.

## 20. Bundled a vendored code

Vendored source, copied files a embedded libraries často uniknú manifest-based generatorom.

Controls:

- file/binary analysis,
- source inventory,
- repository policy,
- explicit bundled relationships,
- hash-level evidence,
- manual curation pre critical components.

## 21. Static linking

Static linking vkladá library code do výsledného binary.

Package manager inventory sama nemusí dokázať, ktorá verzia bola skutočne linked.

Použi:

- linker/build metadata,
- binary symbols,
- build provenance,
- compiler output,
- specialized analyzers.

## 22. Operating-system packages

Container alebo VM SBOM má zachytiť:

- distribution,
- package name,
- epoch/version/release,
- architecture,
- installed database,
- source package, ak je dostupný,
- vendor advisory context.

Generic upstream version matching môže označiť vendor-backported package ako vulnerable.

## 23. Language packages

Ecosystems sa líšia:

- npm package + lockfile,
- Maven coordinates,
- Python distribution vs import name,
- Go modules,
- NuGet packages,
- Cargo crates.

Generator musí rozumieť native resolver semantics.

## 24. Container image

Container SBOM môže opisovať:

- OCI manifest digest,
- image config,
- OS packages,
- language packages,
- application binaries,
- layers,
- base image relationship,
- architecture.

Scan iba posledného filesystem view môže stratiť layer provenance, ale runtime risk sa primárne viaže na final visible content.

## 25. Multi-architecture image

OCI image index môže odkazovať na viac platform manifests:

```text
index digest
├─ linux/amd64 manifest
└─ linux/arm64 manifest
```

SBOM musí jasne uviesť, či opisuje:

- celý index,
- jednu platform variant,
- každú variant samostatne.

Inak consumer môže použiť amd64 inventory pre arm64 artifact.

## 26. Source-based generation

Výhody:

- rýchla integrácia,
- presné manifest a lockfile semantics,
- visibility pred buildom.

Limity:

- generated artifacts,
- conditional dependencies,
- copied binaries,
- OS packages,
- compiler/linker transformations,
- removed alebo added build content.

## 27. Binary a artifact analysis

Výhody:

- vidí final content,
- odhalí undeclared packages,
- použiteľná bez source.

Limity:

- version inference,
- stripped binaries,
- static linking,
- false matches,
- stratené dependency intent,
- opaque proprietary formats.

Najvyššiu assurance často poskytuje kombinácia build-native a artifact analysis.

## 28. Completeness

Completeness opisuje, čo bolo zahrnuté alebo vylúčené.

CycloneDX composition alebo ekvivalentný contract môže vyjadriť, či inventory je complete, incomplete alebo unknown pre daný scope.

Bez completeness statementu consumer nevie rozlíšiť „component nie je prítomný“ od „generator ho nevedel nájsť“.

## 29. Accuracy

Accuracy znamená, že records zodpovedajú skutočnému artifactu.

Over:

- version,
- package ecosystem,
- architecture,
- supplier,
- digest,
- relationship,
- runtime presence.

Viac records nie je automaticky vyššia accuracy.

## 30. Freshness

SBOM musí byť generovaná pre každý immutable release artifact.

Stale SBOM môže vzniknúť, keď:

- artifact bol rebuildnutý,
- dependency lockfile sa zmenil,
- base image sa aktualizoval,
- registry tag sa presunul,
- SBOM bola skopírovaná medzi variants.

SBOM version a creation time nenahrádzajú digest binding.

## 31. Deterministic generation

Deterministic output znižuje noisy diffs.

Normalizuj:

- ordering,
- timestamps podľa policy,
- identifiers,
- paths,
- tool metadata,
- serialization.

Unique document identifier môže byť zámerne odlišný pri každej generácii; porovnanie preto potrebuje semantic normalization.

## 32. License information

SBOM môže obsahovať:

- declared licenses,
- concluded licenses,
- license expressions,
- copyright,
- notices,
- file-level findings.

Automatický scanner nemusí správne vyriešiť custom license alebo dual licensing. Legal decision zostáva samostatný workflow.

## 33. Vulnerability data

SBOM inventory umožňuje vulnerability matching, ale vulnerability status sa časom mení.

Neukladaj jediný scan result ako trvalú pravdu o SBOM. Oddeľ:

```text
immutable-ish component inventory
od
time-dependent vulnerability intelligence
```

## 34. VEX

Vulnerability Exploitability eXchange vyjadruje status konkrétnej vulnerability voči konkrétnemu productu alebo artifactu.

Typické statuses:

- affected,
- not affected,
- fixed,
- under investigation.

`not affected` potrebuje machine-readable justification a ownera. VEX nie je všeobecný ignore list.

## 35. Exploitability context

Vulnerability môže byť present, ale code path nemusí byť reachable alebo feature nemusí byť enabled.

Evidence môže zahŕňať:

- build configuration,
- execution path,
- linked symbols,
- runtime configuration,
- compensating control,
- platform variant.

Status musí mať expiry alebo revalidation trigger pri zmene artifactu.

## 36. SBOM signature a attestation

SBOM môže byť:

- signed ako samostatný blob,
- zabalená do attestation predicate,
- attached k OCI artifactu,
- distribuovaná cez vendor API.

Verification má viazať:

```text
SBOM bytes
+ producer identity
+ subject digest
+ predicate/schema
```

Signature nedokazuje completeness.

## 37. Build provenance vs SBOM

```text
SBOM       → čo artifact obsahuje
provenance → ako a z čoho artifact vznikol
```

Spoločné použitie umožní:

- overiť source revision,
- identifikovať dependencies,
- analyzovať build platform,
- reagovať na upstream incident.

## 38. OCI distribution

SBOM pre container image možno uložiť ako attached OCI artifact viazaný cez subject digest.

OCI Referrers model umožňuje nájsť related manifests, napríklad:

- signature,
- SBOM,
- provenance,
- vulnerability report.

Registry musí podporovať retention, copy a garbage collection attached artifacts.

## 39. External distribution

Alternatívy:

- release asset,
- package repository metadata,
- vendor portal,
- transparency service,
- customer API.

External index musí poskytovať unambiguous mapping na artifact digest a version.

## 40. Storage a indexing

Operational platforma potrebuje:

- raw SBOM retention,
- schema validation,
- normalized component graph,
- immutable subject mapping,
- version history,
- access control,
- query API,
- evidence origin,
- ingestion errors,
- deletion policy.

Normalized database nesmie nahradiť original signed document.

## 41. Ingestion pipeline

```text
receive
→ authenticate source
→ validate schema
→ verify signature/attestation
→ validate subject digest
→ normalize identifiers
→ resolve relationships
→ enrich vulnerability/license data
→ publish consumer views
```

Invalid SBOM má byť quarantined, nie silently partially imported.

## 42. Identity normalization

Rovnaký component môže mať:

- viac purls,
- CPE,
- supplier-specific ID,
- file hash,
- source repository,
- package alias.

Normalization musí zachovať original fields a confidence. Agresívne merge môže spojiť odlišné packages.

## 43. Vulnerability matching

Matching pipeline:

```text
component identity
→ ecosystem/vendor advisory
→ version semantics
→ affected range
→ platform/build context
→ VEX/exploitability
→ running asset
```

String comparison versionov je často nesprávna.

## 44. Operational incident response

Pri novej critical vulnerability:

```text
advisory identity
→ match SBOM corpus
→ potvrď affected versions
→ mapuj artifacts
→ mapuj deployments a owners
→ aplikuj VEX/context
→ prioritize
→ remediate
→ generuj nové SBOM
→ over runtime replacement
```

SBOM bez deployment mappingu odpovie „čo sme vyrobili“, nie „kde to beží“.

## 45. Procurement

Procurement contract môže požadovať:

- supported format a version,
- generation per release,
- direct a transitive components,
- completeness statement,
- subject digest,
- delivery SLA,
- vulnerability/VEX updates,
- license fields,
- signature,
- retention,
- correction process.

Požiadavka „dodaj SBOM“ bez acceptance criteria produkuje neporovnateľné outputs.

## 46. CI/CD integration

Gates:

- schema valid,
- primary component matches release,
- required identifiers present,
- no unknown critical packages podľa policy,
- completeness threshold,
- banned component/license,
- signature a provenance valid,
- artifact digest binding,
- diff review pre unexpected dependencies.

Gate nesmie blokovať na každom harmless metadata rozdiele.

## 47. SBOM diff

SBOM diff pomáha identifikovať:

- new dependencies,
- removed dependencies,
- version changes,
- supplier changes,
- license changes,
- graph changes,
- base image drift.

Diff musí byť semantic, nie line-based JSON diff.

## 48. Confidentiality

SBOM môže odhaľovať:

- proprietary component names,
- internal repository paths,
- architecture,
- product versions,
- supplier relationships.

Klasifikuj distribution:

- public,
- customer-restricted,
- internal,
- security-team only.

Confidentiality nesmie zničiť operational accessibility pre incident response.

## 49. SaaS a services

SaaS nemá vždy distributable binary pre zákazníka.

Service BOM môže popísať:

- services,
- endpoints,
- data flows,
- dependencies,
- providers,
- runtime components.

Consumer potrebuje contract, ako sa inventory aktualizuje pri continuous deployment.

## 50. AI, data a cryptographic BOM

Moderné BOM models môžu zachytiť:

- AI models a datasets,
- services,
- hardware,
- cryptographic assets,
- certificates a algorithms.

Tieto xBOMs dopĺňajú software component inventory, ale majú odlišné lifecycle a risk semantics.

## 51. Quality metrics

Sleduj:

- release coverage,
- subject-digest binding coverage,
- schema-valid rate,
- signature verification rate,
- component identity completeness,
- relationship coverage,
- unknown component rate,
- generation latency,
- SBOM-to-runtime mapping coverage,
- false-match rate,
- stale SBOM age,
- supplier correction time.

Počet komponentov nie je quality metric.

## 52. Governance

Definuj:

- approved formats a versions,
- generation stages,
- minimum fields,
- completeness contract,
- signing policy,
- distribution a access,
- retention,
- VEX ownership,
- consumer use cases,
- correction process,
- exception a escalation,
- tool qualification.

## 53. Troubleshooting

### SBOM neobsahuje známu library

Over static linking, vendoring, optional build path, stripped binary, generator scope a excluded paths.

### Dve tools dávajú iný počet components

Porovnaj lifecycle stage, dedup semantics, package vs file records, dev dependencies, layers a completeness.

### Vulnerability matcher hlási nesprávnu verziu

Over purl/CPE, distro backport, epoch/release, architecture, supplier advisory a alias normalization.

### SBOM sa nenašla po registry copy

Over OCI referrers support, attached-artifact copy, fallback tags, registry garbage collection a permissions.

### Signature platí, subject nesedí

SBOM bola podpísaná, ale nie je viazaná na overovaný artifact. Odmietni ju.

## 54. Anti-patterny

- jedna SBOM pre všetky platform variants,
- source manifest vydávaný za final artifact inventory,
- tag namiesto digest subjectu,
- flattened list bez relationships,
- unknown hodnoty nahradené odhadom,
- vulnerability results embedded ako permanentná truth,
- VEX `not affected` bez justification,
- root normalized database bez raw signed originalu,
- line-based diff,
- schema version ignorovaná,
- SBOM generovaná raz ročne,
- public SBOM s internými secrets alebo credentials.

## 55. Mini príklad

```text
subject:
  registry.example/orders@sha256:abc...

primary component:
  pkg:oci/orders@sha256:abc...?arch=amd64

components:
  pkg:deb/debian/openssl@3.0.x?arch=amd64
  pkg:npm/%40example/orders-core@2.4.1
  pkg:npm/express@5.1.0

relationships:
  orders contains orders-core
  orders-core dependsOn express
```

Validation:

- subject digest existuje v registry,
- SBOM signature identity je approved release workflow,
- platform je `linux/amd64`,
- dependency graph je complete podľa deklarovaného scope-u,
- raw SBOM je zachovaná,
- normalized records sa mapujú na running deployment.

## 56. Kontrolné otázky

1. Aký je rozdiel medzi SBOM, provenance, vulnerability scan a VEX?
2. Prečo musí byť SBOM viazaná na artifact digest?
3. Ako sa líši source, build a deployed SBOM?
4. Aké sú hlavné rozdiely SPDX a CycloneDX?
5. Na čo slúži Package URL?
6. Prečo flat component list nestačí?
7. Ako static linking ovplyvňuje generation?
8. Ako reprezentovať multi-architecture image?
9. Čo znamená completeness?
10. Prečo SBOM signature nedokazuje accuracy?
11. Ako sa vulnerability intelligence oddeľuje od inventory?
12. Kedy je VEX `not affected` dôveryhodný?
13. Ako sa SBOM distribuuje cez OCI?
14. Ako vyzerá incident-response query?
15. Ktoré quality metrics majú význam?

## Glossary impact

Relevantné pojmy: SBOM, SBOM subject, source SBOM, build SBOM, analyzed SBOM, deployed SBOM, runtime inventory, SPDX 3.0.1, SPDX profile, CycloneDX 1.7, primary component, Package URL, CPE, component relationship, dependency graph, dependency scope, bundled component, vendored component, static linking, multi-architecture SBOM, SBOM completeness, SBOM accuracy, SBOM freshness, VEX, exploitability status, SBOM attestation, OCI Referrers, SBOM ingestion, identity normalization, SBOM diff, SaaSBOM, xBOM a cryptographic BOM.

## Primárne zdroje

- [NTIA — The Minimum Elements for a Software Bill of Materials](https://www.ntia.gov/report/2021/minimum-elements-software-bill-materials-sbom)
- [SPDX Specification 3.0.1](https://spdx.github.io/spdx-spec/)
- [SPDX 3.0.1 Model and Serializations](https://spdx.github.io/spdx-spec/v3.0.1/serializations/)
- [SPDX Package URL Specification](https://spdx.github.io/spdx-spec/v3.0.1/annexes/pkg-url-specification/)
- [CycloneDX Specification Overview](https://cyclonedx.org/specification/overview/)
- [CycloneDX 1.7 JSON Reference](https://cyclonedx.org/docs/1.7/json/)
- [CycloneDX Capabilities](https://cyclonedx.org/capabilities/)
- [OCI Image Manifest Specification](https://specs.opencontainers.org/image-spec/manifest/)
- [ORAS Attached Artifacts and Referrers](https://oras.land/docs/concepts/reftypes/)
- [CISA Software Bill of Materials resources](https://www.cisa.gov/sbom)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Supply-chain security](supply-chain-security.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Image signing →](image-signing.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
