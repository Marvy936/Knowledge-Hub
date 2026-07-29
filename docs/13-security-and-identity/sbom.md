# SBOM

Software Bill of Materials — SBOM — je machine-readable inventory components a relationships viazaný na konkrétny software subject. Poskytuje transparency, nie automatický security verdict. Operational hodnota vzniká iba vtedy, keď document správne opisuje exact artifact, explicitne uvádza lifecycle stage a completeness, zachováva relationships a je prepojený s runtime inventory a remediation workflowom.

```text
immutable software subject
→ generation stage, method a evidence authority
→ component identities a relationships
→ completeness, accuracy a confidence
→ signature alebo attestation
→ registry distribution a promotion
→ schema validation, ingestion a normalization
→ vulnerability, VEX, license a supply-chain decisions
→ deployed a rollback mapping
→ remediation a fixed-runtime verification
```

SBOM file, ktorý existuje, ale nepatrí správnemu subjectu alebo nevidí final artifact, je false assurance.

## 1. Exact SBOM subject

SBOM musí odpovedať, ktoré bytes alebo system snapshot opisuje.

Strong subject identity môže obsahovať:

- OCI image index alebo platform manifest digest;
- package archive hash;
- firmware alebo VM image digest;
- source repository a exact revision pre source SBOM;
- product release a architecture;
- supplier, Package URL a distribution qualifiers;
- release alebo deployment snapshot pre continuously changing service.

```text
product name + version
→ human/release identity

cryptographic digest
→ concrete content identity
```

Mutable tag alebo filename nestačí. Ak sa tag `payments:7.24` presunie, SBOM viazaný iba na tag stratí jednoznačný subject.

## 2. Lifecycle stage

Nie každý BOM odpovedá na rovnakú otázku.

**Source SBOM** opisuje declared alebo resolved source dependencies. Vidí manifests, lockfiles a vendored source, ale nemusí zachytiť build environment alebo injected final content.

**Build-input alebo builder BOM** opisuje toolchain, runner image, compiler, actions, build helpers a ďalšie inputs, ktoré môžu ovplyvniť output, hoci nie sú v runtime artifacte.

**Build SBOM** vzniká počas build graphu a môže spájať resolved inputs s outputs.

**Analyzed alebo final-artifact SBOM** vzniká inspection final package, binary alebo image filesystemu. Je authoritative pre to, čo generator dokáže z final bytes identifikovať.

**Runtime inventory** opisuje exact digests a variants, ktoré skutočne bežia. Nie je náhradou immutable release SBOM-u, ale spája composition s ownerom a environmentom.

Tieto pohľady sa dopĺňajú:

```text
source SBOM
+ builder/toolchain BOM
+ final-artifact SBOM
+ provenance
+ runtime digest inventory
→ vysvetliteľný source-to-runtime composition chain
```

## 3. Producer, distributor a consumer

**Producer** generuje SBOM a deklaruje subject, lifecycle stage, method, tool a coverage limitations.

**Distributor** prenáša document alebo attestation spolu s artifactom a zachová subject binding, integrity a access policy.

**Consumer** validuje schema, signer, subject, semantics a quality a používa data na konkrétny decision.

Syntakticky validný document nemusí byť complete ani accurate. Validná signature dokazuje publisher authority a integrity documentu, nie správnosť detection výsledkov.

## 4. Minimum production contract

Praktický contract zahŕňa:

- SBOM document identity a specification version;
- primary subject a immutable digest;
- creator, tool version, configuration a timestamp;
- lifecycle stage a generation method;
- component identifiers, versions, suppliers/origins a hashes;
- dependency, containment a build relationships;
- architecture, distro a other qualifiers;
- explicit unknowns, completeness a detection confidence;
- signature alebo attestation authority;
- distribution, update a retention semantics.

Unknown sa nemá nahradiť guessed value. Vymyslený version alebo supplier zhoršuje matching viac než explicitná neistota.

## 5. SPDX 3.0.1

SPDX 3.0.1 je current system-oriented SPDX specification. Používa Core Profile a ďalšie profiles pre Software, Security, Build, Licensing, Dataset/AI a ďalšie domains.

Graph relationships umožňujú rozlíšiť:

- package alebo file obsiahnutý v artifacte;
- dependency potrebnú za runtime;
- build input alebo tool;
- output konkrétnej build instance;
- vulnerability a affected status;
- declared a concluded licensing evidence.

Consumer musí deklarovať podporovanú version, serialization a profiles. Tvrdenie `podporujeme SPDX` je neúplné, ak tool rozumie iba SPDX 2.3 a producer posiela SPDX 3.0.1 s Build a Security profilmi.

## 6. CycloneDX 1.7

CycloneDX 1.7 je current stable CycloneDX BOM specification a ECMA-424, 2nd Edition. Modeluje metadata, components, services, dependencies, compositions, formulation, vulnerabilities, cryptographic assets, AI a ďalšie transparency data.

Primary component v metadata určuje hlavný subject. `bom-ref` je lokálna graph identity, nie globálny package identifier.

Component v liste automaticky neznamená runtime dependency alebo reachability. Dependency graph, scope, compositions a formulation určujú vzťah k subjectu.

Consumer validuje exact `specVersion` a serialization. Lossy conversion medzi SPDX a CycloneDX musí byť viditeľná.

## 7. Component identity

Name a version nie sú globálne unikátne. Robustná identity kombinuje:

```text
ecosystem/package type
+ namespace
+ name
+ version
+ qualifiers, napríklad distro alebo architecture
+ supplier/origin
+ content digest
```

Package URL štandardizuje ecosystem identity. CPE môže pomôcť pri product-level advisories. Vendor backport a distribution revision môžu znamenať, že upstream-looking old version je fixed.

Hash musí uvádzať scope. Hash package archive-u, extracted directory, executable file-u a OCI manifestu nie sú porovnateľné subjecty.

Purl ani hash nie sú provenance. Nehovoria, kto bytes vytvoril a cez aký build process.

## 8. Relationships a scope

Flat component list nevysvetľuje, prečo component súvisí so subjectom.

Relevantné semantics zahŕňajú:

- contains alebo bundled — component je fyzicky súčasťou artifactu;
- depends on — execution alebo build graph dependency;
- generated/built from — output vznikol z inputu;
- uses tool — compiler alebo helper ovplyvnil build;
- variant of — architecture alebo distribution variant;
- distributed as — rovnaký software v inom artifact representation.

Direct, transitive, optional, test-only, build-only a runtime scopes majú odlišný risk význam.

Build helper nemusí patriť do runtime SBOM-u, ale musí byť viditeľný v builder/toolchain BOM-e alebo provenance. Injected JAR vo final image patrí do final-artifact SBOM-u bez ohľadu na to, či bol v source manifest-e.

## 9. Vendored, static a generated content

Manifest-based generator nemusí vidieť:

- source skopírovaný do repository;
- manually downloaded JAR alebo binary;
- statically linked library;
- generated bundle;
- build-time injected plugin;
- code pridaný do final stage mimo language resolvera.

Coverage preto často kombinuje resolver, build graph, package database, file/binary analysis a manual curation pre critical content.

Removal dependency zo source branchu nemení už vytvorený binary. SBOM musí patriť outputu, nie iba current source state-u.

## 10. Containers a multi-platform artifacts

OCI image index môže odkazovať na viac platform manifests s rozdielnymi packages a binaries.

Bezpečný model používa:

- release-level record viazaný na index digest;
- platform-specific final-artifact SBOM pre každý manifest digest;
- architecture a OS qualifiers;
- relationship index → platform variants;
- runtime inventory resolved platform digestu pre každý workload.

Aggregate list bez platform identity môže vytvoriť false finding alebo vynechať arm64-only affected component.

Base-image relationship pomáha zistiť, ktoré products treba rebuildnúť po fixed base release. Multi-stage build má odlišovať build tools od final runtime contentu.

## 11. Completeness, accuracy a freshness

**Completeness** opisuje, do akej miery document pokrýva intended subject, ecosystems, dependency depth a relationship graph.

**Accuracy** opisuje, či records správne identifikujú skutočný content.

**Freshness SBOM-u** znamená, že document zodpovedá konkrétnemu artifactu alebo snapshotu. **Freshness vulnerability assessmentu** znamená, že inventory bol nedávno porovnaný s aktuálnymi advisories.

Immutable artifact SBOM sa nemení pri novej CVE. Mení sa external vulnerability knowledge a VEX alebo local assessment.

Absencia componentu nie je dôkaz neprítomnosti, ak completeness je unknown alebo ecosystem unsupported.

## 12. Determinism a semantic diff

Rovnaký artifact a rovnaká generator configuration majú vytvoriť semanticky rovnaký inventory. Raw bytes môžu obsahovať timestamp, random document ID alebo ordering differences.

Semantic diff porovnáva:

- component added/removed;
- version alebo digest change;
- dependency path a scope change;
- supplier/origin correction;
- completeness alebo method change;
- generator-only metadata change.

Tool upgrade, ktorý nájde viac contentu, je evidence-generation change, nie automaticky software composition change.

## 13. Vulnerability matching a VEX

Vulnerability platforma porovnáva component identities s advisories a zachová:

- matched identifier a record;
- advisory source a affected range;
- matching method a confidence;
- affected subject digests;
- deployed environments a owners;
- fix alebo mitigation;
- VEX alebo local exploitability state.

SBOM dokazuje inventory claim, nie exploitation.

VEX vyjadruje vulnerability status konkrétneho product subjectu, napríklad affected, not affected, fixed alebo under investigation. `not affected` potrebuje authority a technical justification. `Fixed` musí byť viazané na exact product version alebo digest.

Supplier-signed VEX nie je automaticky authoritative pre organization risk. Consumer hodnotí issuer, scope, evidence a current deployment.

## 14. Signing a attestation

SBOM možno podpísať ako document alebo publikovať ako attestation s artifact subjectom.

Consumer overuje:

- exact subject digest;
- signer identity a issuer;
- signer authorization pre product;
- predicate alebo document format/version;
- generation method a tool podľa policy;
- integrity a schema;
- completeness/quality requirements.

Validná signature nemôže zmeniť source-only SBOM na final-artifact SBOM. Podpisuje claim; neopravuje jeho semantics.

## 15. OCI distribution a promotion

SBOM, provenance a signatures môžu byť related OCI artifacts viazané na subject digest. Registry Referrers API pomáha consumerovi related manifests objaviť.

```text
image digest
├─ platform SBOM
├─ provenance
├─ release signature
└─ vulnerability/VEX attestation
```

Referrers discovery neposkytuje trust samo osebe. Consumer stále validuje descriptor, subject, artifact type, issuer a claims.

Promotion alebo replication musí preniesť image aj required related artifacts. Copy iba layers a manifestu môže nechať production registry bez SBOM a provenance.

## 16. Ingestion a normalization

SBOM platforma spracúva untrusted documents. Potrebuje:

- payload, depth a graph-size limits;
- schema a version validation;
- safe XML/JSON processing;
- signature a subject verification;
- tenant isolation a access control;
- preservation raw documentu;
- transformation lineage;
- explicit lossy mappings a unknown fields.

Normalization nesmie ticho premeniť build tool na runtime dependency alebo zahodiť architecture qualifier. Incident responder potrebuje rozlíšiť source claim od normalized derivation.

## 17. Deployment mapping

Operational query je reverse graph:

```text
component alebo vulnerability
→ SBOM subject digests
→ running a rollback artifacts
→ workload, environment a tenant
→ owner
→ remediation a verification
```

Tag-based inventory je nepresný. Kubernetes a registry evidence majú zachytiť resolved platform digest.

Rollback catalog, scale templates a dormant release channels patria do exposure inventory. Critical component sa môže vrátiť aj po odstránení current Pods.

## 18. Worked incident `SEC-PAY-50`

Release `7.24.0` vytvorila image `sha256:pay7240`. Pipeline publikovala signed CycloneDX 1.7 SBOM s matching subject digestom. Security dashboard preto zobrazil `SBOM present` a admission gate prešiel.

Document však vznikol zo source lockfile-u pred final packagingom. Pipeline po build-e iba doplnila final image digest ako subject. SBOM neanalyzovala final filesystem a neuviedla lifecycle stage ani incomplete coverage.

Vulnerable builder `sha256:builder17` obsahoval `atlas-build-helper 2.4.1`. Crafted metadata zneužila helper a pridala `settlement-debug.jar` do final image po tests. Helper správne nepatril medzi runtime components aplikácie, ale mal byť viditeľný v builder/toolchain inventory. Injected JAR mal byť viditeľný vo final-artifact SBOM-e.

### Competing hypotheses

1. **Component v artifacte nie je.** Scanner alebo incident report je chybný.
2. **SBOM patrí inému digestu.** Subject binding alebo promotion sa rozpadli.
3. **Registry alebo normalizer related artifact stratil.** Generation bola správna, consumption nie.
4. **Generator nepodporoval embedded JAR.** Coverage limitation nebola deklarovaná.
5. **Pipeline vydávala source inventory za final-artifact SBOM.** Document semantics boli nesprávne.

### Discriminating evidence

- OCI referrer existoval a subject bol `sha256:pay7240`;
- signature a schema boli validné;
- raw document aj normalized graph injected JAR neobsahovali;
- final filesystem a independent binary scanner JAR našli;
- source lockfile ho neobsahoval;
- generator metadata ukázali source manifest mode, nie image analysis;
- builder-image inventory obsahoval vulnerable helper;
- production promotion referrer nestratila, takže root cause bol generation contract.

SBOM nebola missing. Bola subject-bound, signed a syntakticky validná, ale semanticky neúplná a nesprávne označená.

## 19. Evidence-preserving containment

- preserve-nuť raw SBOM, signature, provenance, generator logs a normalized representation;
- quarantine-nuť `sha256:pay7240` a affected builder outputs;
- zablokovať existence-only SBOM gate;
- mapovať digest na running a rollback deployments;
- spustiť independent final-binary/image analysis bez prepísania pôvodného evidence;
- zachovať tool version a configuration pre reprodukciu coverage gapu;
- nevydať retroaktívne upravenú SBOM pod rovnakou document identity bez lineage.

## 20. Authoritative recovery

1. zachovať source SBOM ako source-stage evidence s correct metadata;
2. vytvoriť builder/toolchain BOM pre pinned builder digest;
3. generovať platform-specific SBOM z každého final OCI manifest filesystemu;
4. vytvoriť release-level relationship k image index digestu;
5. pridať binary/JAR coverage a seeded detection fixture;
6. vydať signed attestations z approved evidence authority;
7. overiť subject, stage, completeness a semantic diff v CI;
8. zachovať referrers pri promotion a vykonať destination read-back;
9. ingestovať raw aj normalized documents s transformation lineage;
10. mapovať new digest na runtime a odstrániť old digest z rollback paths;
11. re-evaluovať historical artifacts vytvorené rovnakou chybnou generator configuration.

## 21. Acceptance verdict

SBOM remediation je uzavretá, keď:

- source, builder a final-artifact inventories sú explicitne oddelené;
- final SBOM subject sa zhoduje s platform manifest digestom;
- seeded embedded JAR je v final SBOM-e detected a správne related;
- build-only helper nie je nesprávne označený ako runtime component, ale zostáva v builder inventory;
- completeness a unsupported paths sú explicitné;
- wrong subject, wrong stage a unknown completeness policy odmietne;
- promotion zachová SBOM, provenance a signature referrers;
- normalization zachová purl, architecture, scope a original relationships;
- runtime mapping nájde všetky current aj rollback digests;
- old `sha256:pay7240` už nie je deployable ani running;
- druhý release vytvorí semanticky stabilný inventory a allowed business flow funguje.

## 22. CI/CD a quality gates

Gate nemá kontrolovať iba `sbom.json exists`. Pre critical release overuje:

- primary subject digest;
- required format/version/profile;
- lifecycle stage a generator method;
- supported ecosystem coverage;
- component identity quality;
- relationship a architecture completeness;
- approved signer/evidence authority;
- semantic diff a unexpected high-risk components;
- destination distribution a runtime mapping.

Exception má exact subject, ownera, expiry a plan na coverage gap. Permanentné `allow unknown completeness` ruší transparency control.

## 23. Procurement, SaaS a extended BOMs

Supplier contract môže definovať format/version, subject granularity, cadence, VEX process, retrieval channel a incident notification.

`SBOM available` bez väzby na konkrétny build alebo continuously deployed SaaS snapshot má nízku operational hodnotu.

CBOM inventarizuje cryptographic assets a pomáha crypto agility. AI BOM môže zachytiť models, datasets, frameworks a dependencies. Inventory však automaticky nehodnotí model behavior, safety alebo legal status data.

Zbieraj iba metadata, pre ktoré existuje owner a decision workflow.

## 24. Earlier controls

- required immutable digest subject;
- explicit source/build/final/runtime stage;
- separate builder/toolchain BOM;
- platform-specific final image analysis;
- seeded components pre coverage canary;
- completeness, accuracy a confidence policy;
- semantic diff namiesto raw JSON diffu;
- signed attestations s approved generation authority;
- registry referrers promotion/read-back test;
- raw document a normalization lineage;
- continuous advisory/VEX re-evaluation;
- digest-to-runtime a rollback mapping;
- wrong-stage a unknown-completeness negative tests.

## 25. Anti-patterny

### Checkbox SBOM

Document existuje, ale nikto nevaliduje subject, quality ani consumer use.

### Subject bez digestu

Product name alebo tag neidentifikuje bytes.

### Source inventory vydávaný za final artifact

Build-added, generated a injected content chýba.

### Flat list bez relationships

Consumer nevie scope, containment ani dependency path.

### Unknown interpretované ako absent

Coverage gap sa mení na false negative.

### Validná signature znamená complete SBOM

Signature chráni claim, nie accuracy generatora.

### Inventory bez runtime mappingu

Organization vie, čo buildla, ale nie čo beží alebo sa môže rollbacknúť.

## 26. Kontrolné otázky

1. Čo tvorí exact SBOM subject?
2. Ako sa source, builder, build a final-artifact SBOM líšia?
3. Čo producer, distributor a consumer dokazujú?
4. Prečo SPDX version/profile a CycloneDX specVersion patria do contractu?
5. Ako purl, CPE a digest riešia odlišné identity problémy?
6. Prečo relationships a dependency scope menia vulnerability verdict?
7. Ako modelovať builder helper oproti runtime componentu?
8. Ako multi-platform OCI release viaže SBOMs na variants?
9. Ako sa completeness, accuracy a freshness líšia?
10. Prečo VEX nie je náhrada SBOM-u?
11. Čo podpis SBOM-u dokazuje a čo nie?
12. Čo musí overiť SBOM acceptance verdict?

## Glossary impact

Relevantné pojmy: SBOM decision subject, lifecycle-stage declaration, builder/toolchain BOM, final-artifact SBOM, evidence-generation method, component-identity confidence, relationship completeness, semantic SBOM generation, subject-bound attestation, promotion preservation, normalization lineage, digest-to-runtime mapping, SBOM acceptance verdict a coverage recurrence.

## Primárne zdroje

- [SPDX Specification 3.0.1](https://spdx.github.io/spdx-spec/)
- [SPDX 3.0.1 conformance and profiles](https://spdx.github.io/spdx-spec/v3.0.1/conformance/)
- [CycloneDX Specification Overview](https://cyclonedx.org/specification/overview/)
- [CycloneDX 1.7 JSON Reference](https://cyclonedx.org/docs/1.7/json/)
- [Package URL specification](https://github.com/package-url/purl-spec)
- [NTIA Minimum Elements for an SBOM](https://www.ntia.gov/report/2021/minimum-elements-software-bill-materials-sbom)
- [CISA SBOM Resources Library](https://www.cisa.gov/topics/cyber-threats-and-advisories/sbom/sbomresourceslibrary)
- [OCI Distribution Specification — Referrers API](https://github.com/opencontainers/distribution-spec/blob/main/spec.md)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Supply-chain security](supply-chain-security.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Image signing →](image-signing.md)
<!-- KNOWLEDGE-NAVIGATION:END -->