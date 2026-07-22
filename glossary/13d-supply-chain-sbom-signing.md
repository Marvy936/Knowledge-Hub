# Supply-chain, SBOM and image-signing glossary entries

## Software supply chain

Súbor ľudí, identities, source repositories, dependencies, build systems, tools, registries, release procesov a deployment controls, ktoré môžu ovplyvniť výsledný software artifact. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Source revision

Konkrétny logicky immutable snapshot repository identifikovaný revision ID, napríklad Git commit SHA, spolu s relevantnou version-control metadata. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Source provenance

Attestation opisujúca, ako konkrétna source revision vznikla, kto a aký process ju vytvoril a ktoré source-control controls boli presadené. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## SLSA Source track

SLSA track definujúci rastúce guarantees pre version-controlled source, history, source provenance, kontinuálne technical controls a two-party review. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## SLSA Build track

SLSA track definujúci guarantees pre build provenance, hosted build platform a hardened build isolation. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Dependency confusion

Supply-chain attack, pri ktorom dependency resolver vyberie attacker-controlled package z iného registry alebo namespace namiesto zamýšľaného interného package-u. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Typosquatting — package

Publikovanie malicious alebo deceptive package-u s názvom podobným legitimate dependency s cieľom využiť chybu používateľa alebo automatizácie. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Namespace takeover — package

Získanie kontroly nad opusteným, expirovaným alebo nesprávne rezervovaným package namespace-om a jeho použitie na distribúciu attacker-controlled contentu. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Lockfile — dependency resolution

Versionovaný záznam konkrétneho resolved dependency graphu, často vrátane integrity hashes, ktorý stabilizuje opakovanie dependency resolution. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Digest pinning

Viazanie dependency, action, image alebo artifact reference na immutable cryptographic content digest namiesto mutable tagu alebo version range. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Build definition

Versionovaný contract build procesu zahŕňajúci workflow, scripts, toolchain, environment, flags, inputs a target platform. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Build platform

Systém vykonávajúci build definitions, získavajúci inputs a vytvárajúci artifacts a provenance; predstavuje kritickú supply-chain trust boundary. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Ephemeral runner

Build worker vytvorený pre obmedzený job alebo run a následne zničený, aby sa znížilo cross-job contamination a persistence risk. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Hermetic build

Build, ktorý získava všetky inputs cez deklarovaný a kontrolovaný mechanism bez nezdokumentovaného host alebo network dependency accessu. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Reproducible build

Build property umožňujúca nezávisle vytvoriť rovnaký output z rovnakých inputs a definovaného environmentu. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Build provenance

Attestation viažuca artifact digest na builder identity, build type, source revision, inputs a relevantné invocation metadata. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Attestation — supply chain

Signed statement, ktorý viaže subject digest na konkrétny predicate a identity vydávajúcu dané tvrdenie. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## in-toto

Framework a metadata model pre zaznamenanie a overenie supply-chain steps, materials, products a autorizovaných functionaries. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## SLSA Build L1

SLSA Build level, pri ktorom pre artifact existuje automaticky generovaná provenance, ale nemusí poskytovať silnú tamper resistance. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## SLSA Build L2

SLSA Build level vyžadujúci signed provenance generovanú hosted build platformou a consumer-side authenticity verification. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## SLSA Build L3

SLSA Build level vyžadujúci hardened build platformu s izoláciou build runs a oddelením provenance signing materialu od user-defined build steps. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## TUF — The Update Framework

Framework pre secure software updates používajúci role separation, threshold signatures, metadata expiration a rollback, freeze a mix-and-match ochrany. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## OpenSSF Scorecard

Automatizovaný nástroj hodnotiaci vybrané open-source project security heuristics; jeho score je triage signal, nie security certifikácia. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Supplier due diligence

Risk-based overovanie identity, procesov, controls, evidence, maintenance, incident response a transitive dependencies software supplier-a. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Artifact quarantine

Riadené zablokovanie promotion, pull alebo deploymentu konkrétneho artifact digestu pri zachovaní forensic evidence. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md) a [Image signing](docs/13-security-and-identity/image-signing.md).

## SBOM

Machine-readable inventory software components a relationships viazaný na konkrétny software artifact alebo system. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## SBOM subject

Konkrétny artifact alebo system, ktorý SBOM opisuje, preferovane identifikovaný immutable digestom a doplňujúcimi package metadata. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## Source SBOM

SBOM generovaná zo source manifests, lockfiles a repository contentu pred vytvorením final artifactu. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## Build SBOM

SBOM generovaná počas build procesu z resolved dependencies, build metadata a vytváraného artifactu. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## Analyzed SBOM

SBOM odvodená analýzou existujúceho binary, package, image alebo filesystemu bez plnej závislosti na source metadata. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## Deployed SBOM

Inventory komponentov viazaný na artifact alebo system nasadený v konkrétnom environment kontexte. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## SPDX 3.0.1

Verzia System Package Data Exchange specification s profile-oriented modelom pre software, licensing, security, build a ďalšie system information. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## CycloneDX 1.7

Verzia CycloneDX BOM specification pre components, services, dependency graphs, formulation, vulnerabilities, cryptographic assets a ďalšie transparency data. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## Primary component — SBOM

Hlavný product, application alebo artifact, ktorého composition daná SBOM opisuje. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## Component relationship — SBOM

Machine-readable väzba medzi SBOM elements, napríklad `dependsOn`, `contains`, `generatedFrom` alebo `distributedAs`. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## Dependency scope — SBOM

Klasifikácia účelu componentu, napríklad runtime, development, test, optional, build-only alebo externally provided. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## Vendored component

External code alebo binary skopírovaný priamo do repository alebo artifactu namiesto štandardnej package-manager dependency. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## Multi-architecture SBOM

SBOM model, ktorý explicitne rozlišuje OCI image index a jednotlivé platform manifests a ich odlišné component inventories. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## SBOM completeness

Deklarovaný rozsah a miera, do akej SBOM zachytáva všetky components a relationships v definovanom subjecte. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## SBOM accuracy

Miera, do akej component identities, versions, digests, suppliers a relationships zodpovedajú skutočnému artifactu. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## SBOM freshness

Vzťah SBOM ku konkrétnemu aktuálnemu immutable release artifactu a času jeho generation; creation timestamp bez digest bindingu freshness nedokazuje. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## VEX

Vulnerability Exploitability eXchange statement vyjadrujúci affected, not affected, fixed alebo under-investigation status vulnerability voči konkrétnemu productu. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## Exploitability status

Machine-readable tvrdenie o tom, či a prečo je konkrétna vulnerability relevantná pre konkrétny artifact alebo product context. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## SBOM attestation

Signed supply-chain statement, ktorý viaže SBOM predicate na konkrétny artifact digest a producer identity. Pozri [SBOM](docs/13-security-and-identity/sbom.md) a [Image signing](docs/13-security-and-identity/image-signing.md).

## OCI Referrers

OCI distribution model na discovery manifests, ktoré cez `subject` odkazujú na artifact digest, napríklad signatures, SBOMs alebo provenance. Pozri [SBOM](docs/13-security-and-identity/sbom.md) a [Image signing](docs/13-security-and-identity/image-signing.md).

## SBOM ingestion

Pipeline na authentication source-u, schema validation, signature verification, subject binding, normalization a indexing prijatej SBOM. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## SBOM diff

Semantic comparison dvoch SBOM versions zamerané na component, version, relationship, supplier a license changes namiesto textového JSON diffu. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## SaaSBOM

Bill of Materials opisujúci software-as-a-service components, services, providers a dependencies v continuously deployed service modeli. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## xBOM

Zastrešujúci pojem pre rôzne Bill of Materials domains, napríklad software, hardware, AI, services alebo cryptographic assets. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## Cryptographic BOM — CBOM

Inventory cryptographic algorithms, keys, certificates, protocols a dependencies používaný na crypto governance a migration planning. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## Image signing

Cryptographic binding container image digestu na signing key alebo identity, ktorý consumer vyhodnocuje podľa verification policy. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Signed image subject

OCI image index alebo platform manifest digest, ku ktorému sa signature alebo attestation explicitne viaže. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Key-based signing

Signing model používajúci dlhodobejší private key a distribuovaný public key alebo certificate ako trust anchor. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Keyless signing

Identity-based signing model používajúci OIDC authentication, ephemeral key pair a short-lived signing certificate namiesto manuálne spravovaného long-lived signing keyu. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Sigstore

Open-source ecosystem pre software signing, identity-bound certificates, transparency a verification tooling. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Cosign

Sigstore nástroj na signing a verification container images, blobs a supply-chain attestations. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Fulcio

Sigstore certificate authority vydávajúca short-lived code-signing certificates pre overené OIDC identities. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Rekor

Sigstore transparency log pre signed software supply-chain metadata a inclusion evidence. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Verification bundle — Sigstore

Prenositeľný súbor obsahujúci signature, certificate chain a transparency alebo timestamp evidence potrebnú na neskoršiu verification. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Signing identity policy

Authorization pravidlá určujúce, ktoré issuers, identities, repositories, workflows a contexts smú podpisovať konkrétne artifacts. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## DSSE

Dead Simple Signing Envelope; envelope format viažuci payload type a payload bytes k signatures s ochranou proti cross-protocol confusion. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## in-toto Statement

Supply-chain attestation structure obsahujúca subject digest, predicate type a predicate. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Provenance attestation

Signed statement viažuci artifact na builder, source revision, build type a inputs podľa definovaného provenance predicate-u. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## OCI artifact

Non-container alebo auxiliary content distribuovaný cez OCI manifest a registry semantics, napríklad signature, SBOM alebo provenance. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## `artifactType` — OCI

OCI manifest field opisujúci semantic media type artifactu, najmä keď config descriptor neposkytuje dostatočnú type informáciu. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## `subject` — OCI manifest

OCI descriptor viažuci artifact manifest na iný manifest digest, ktorý predstavuje jeho subject. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Signature discovery

Proces nájdenia signatures a attestations súvisiacich s artifact digestom cez OCI Referrers alebo ecosystem-specific fallback convention. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Admission verification

Pre-deployment policy decision, ktorý validuje image digest, signature identity, attestations a environment rules pred prijatím workloadu. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Artifact revocation

Policy decision zneplatňujúci predtým akceptovaný artifact digest, signing identity alebo trust path bez nutnosti odstrániť historickú transparency evidence. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).
