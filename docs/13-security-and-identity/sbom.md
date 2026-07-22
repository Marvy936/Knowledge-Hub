# SBOM

Software Bill of Materials — SBOM — je machine-readable inventory software components a relationships viazaný na konkrétny software subject. Subjectom môže byť package, container image, firmware, VM image alebo celý distribuovaný product. SBOM vytvára transparency layer: umožňuje zistiť, z čoho artifact pozostáva, odkiaľ components pochádzajú a ktoré ďalšie artifacts alebo systems môžu byť ovplyvnené novou vulnerability, license problémom alebo supply-chain incidentom.

SBOM nie je security score ani automatický vulnerability verdict. Je to dátový základ, ktorý musí byť presne viazaný na artifact, dostatočne úplný, aktualizovaný a prepojený s deployed inventory. Bez týchto vlastností vznikne formálne správny dokument, ktorý nedokáže odpovedať na operational otázku „kde tento component reálne používame?“

```text
immutable software subject
→ component identities
→ dependency a containment relationships
→ generation context a completeness
→ signature alebo attestation
→ ingestion a normalization
→ vulnerability, license a supply-chain decisions
→ deployment owner a remediation
```

## 1. Problém, ktorý SBOM rieši

Moderná application nevzniká iba z kódu napísaného jedným tímom. Obsahuje language packages, OS packages, generated code, statically linked libraries, container base image, vendored source a build tools. Pri novej vulnerability organizácia často nevie, ktoré produkty obsahujú affected component, v akej verzii a cez akú dependency path.

Bez SBOM sa investigation začína manuálnym prehľadávaním repositories, lockfiles, images a running systems. Tento proces je pomalý a neúplný, najmä keď component prichádza transitively alebo je zabalený do binary bez zachovaného package manifestu.

SBOM umožňuje pripraviť inventory v čase buildu a neskôr ho opakovane porovnávať s novými vulnerability intelligence. Rovnaký artifact sa nemusí rebuildovať pri každej novej CVE; mení sa external knowledge, nie jeho immutable composition.

## 2. Subject identity je základ celého modelu

SBOM musí odpovedať, ku ktorému presnému software subjectu patrí. Názov produktu a marketingová verzia sú užitočné pre človeka, ale nemusia jednoznačne identifikovať bytes.

Pre build artifact je najsilnejší binding cryptographic digest. Pri OCI image môže ísť o image index alebo platform manifest digest. Pri package môže ísť o hash distribuovaného archive-u. Subject record môže dopĺňať Package URL, supplier, repository, architecture a release identifier.

```text
product name + version
→ ľudská a release identity

artifact digest
→ konkrétna content identity
```

Tag alebo filename bez digestu je mutable alebo nejednoznačný. Ak SBOM patrí tagu `app:1.4` a tag sa presunie na nový manifest, consumer nevie, ku ktorému obsahu dokument pôvodne patril.

## 3. SBOM nie je jeden univerzálny inventory snapshot

Software možno pozorovať v rôznych lifecycle stages a výsledné inventories nemusia byť rovnaké.

**Source SBOM** opisuje dependencies deklarované alebo resolved zo source repository. Vidí lockfiles a vendored source, ale nemusí zachytiť packages pridané build environmentom.

**Build SBOM** vzniká počas build procesu a môže zachytiť skutočné resolved inputs, generated artifacts a build metadata.

**Analyzed SBOM** vzniká inspection final binary, package alebo image filesystemu. Dokáže nájsť embedded alebo OS components, ktoré source manifest neuvádza, ale nemusí poznať presnú dependency intent alebo supplier metadata.

**Deployed alebo runtime inventory** opisuje, čo je skutočne nasadené a načítané v konkrétnom environment-e. Je dôležité pre remediation, ale môže byť časovo premenlivé a nemusí byť vhodné ako immutable release evidence.

Tieto pohľady sa dopĺňajú. Organizácia má uviesť, ktorý lifecycle stage dokument reprezentuje a akú completeness možno očakávať.

## 4. Producer, distributor a consumer

**Producer** generuje SBOM z dependency resolvera, build graphu, final artifactu alebo runtime scan-u. Musí vedieť, aký subject analyzuje, aké sources použil a ktoré časti nevedel pokryť.

**Distributor** prenáša SBOM spolu s artifactom alebo cez samostatný transparency channel. Musí zachovať väzbu na subject, integrity a access policy.

**Consumer** dokument validuje, normalizuje a používa na konkrétny decision. Consumer môže byť vulnerability platforma, procurement systém, license scanner, deployment policy alebo incident-response workflow.

Producer a consumer majú rozdielne povinnosti. Producer nemôže predpokladať, že consumer pozná proprietary naming conventions. Consumer zase nesmie považovať každý syntakticky validný SBOM za úplný a dôveryhodný.

## 5. Minimálny dátový contract

NTIA minimum elements rozdelili SBOM baseline na data fields, automation support a practices/processes. Praktický production contract musí obsahovať viac než iba zoznam package names.

Základné oblasti sú:

- identity SBOM dokumentu a jeho specification version;
- creator alebo tool identity a creation timestamp;
- jednoznačná identity primary subjectu;
- component name, version, supplier alebo origin, ak je známy;
- ecosystem-specific identifiers, napríklad Package URL;
- cryptographic hashes, keď existuje stabilný content representation;
- dependency, containment alebo build relationships;
- explicitné unknown hodnoty a completeness statement;
- lifecycle stage a generation method;
- distribution, integrity a update semantics.

Unknown hodnota sa nemá nahrádzať guessed supplierom alebo versionom. Vymyslené metadata zlepšia apparent completeness, ale zhoršia matching a dôveru.

## 6. SPDX 3.0.1 mentálny model

SPDX 3.0.1 je system-oriented data model pre BOM information. Namiesto jedného lineárneho document schema používa Core concepts a samostatné profiles.

Core Profile je povinný a definuje foundational elements, relationships, creation information a integrity concepts. Ďalšie profiles rozširujú model podľa domain-u:

- Software Profile reprezentuje packages, files, snippets a software relationships;
- Security Profile reprezentuje vulnerabilities, severity a affected status;
- Build Profile opisuje build instance, inputs, outputs, tools a environment;
- Licensing profiles pokrývajú declared a concluded licenses;
- Dataset a AI profiles rozširujú model o datasets a AI systems;
- Lite a Extension profiles riešia zjednodušené alebo domain-specific use cases.

Consumer musí deklarovať, ktoré profiles a serialization podporuje. Tvrdenie „podporujeme SPDX“ je neúplné, ak tool rozumie iba SPDX 2.3 tag-value, ale producer posiela SPDX 3.0.1 JSON-LD so Security a Build profilom.

## 7. SPDX relationships a graph

SPDX elements sú prepojené typed relationships. Software component môže obsahovať files, závisieť od packages, vzniknúť buildom alebo byť distribuovaný ako iný artifact.

Graph model umožňuje oddeliť identity entities od ich vzťahov. Build element môže mať `hasInput`, `hasOutput`, `usesTool`, `invokedBy` a `hasHost` relationships. Consumer tak vie rozlíšiť component obsiahnutý v artifacte od toolu, ktorý bol iba použitý pri build-e.

Nesprávne relationship semantics vedú k falošným vulnerability výsledkom. Build-only compiler nemá rovnaký runtime exposure ako library linked do application. Flat export, ktorý všetky records označí ako „dependency“, túto informáciu stratí.

## 8. CycloneDX 1.7 mentálny model

CycloneDX 1.7 je aktuálna stabilná BOM specification a ECMA-424, 2nd Edition. Je navrhnutá pre software, hardware, services, cryptographic assets, AI models a ďalšie transparency use cases.

CycloneDX BOM obsahuje metadata, components, services, dependency graph, compositions, formulation, vulnerabilities, annotations a properties. Primary component v metadata určuje hlavný subject dokumentu. Každý component môže mať `bom-ref`, ktorý slúži ako lokálna graph identity.

CycloneDX rozlišuje inventory records od dependency graphu. Component v `components` liste ešte automaticky neznamená, že je reachable z primary componentu; väzba patrí do `dependencies` alebo compositions.

Specification podporuje JSON, XML a Protocol Buffers. Consumer musí validovať konkrétnu `specVersion`, nie iba `bomFormat: CycloneDX`.

## 9. Výber medzi SPDX a CycloneDX

SPDX a CycloneDX sa výrazne prekrývajú, ale majú odlišnú históriu, model a ecosystem tooling. Výber nemá byť založený iba na osobnej preferencii alebo extension súboru.

Rozhodujúce otázky sú:

- aký format a version vyžaduje consumer alebo contract;
- či treba detailnú licensing, build, security, service alebo cryptographic semantics;
- ktoré generators vytvárajú kvalitné outputy pre daný ecosystem;
- či registry, procurement a vulnerability tools zachovajú relationships;
- ako sa dokument signuje, distribuuje a dlhodobo archivuje;
- či organization dokáže validovať schema a compatibility pri upgrades.

Organization môže interne normalizovať oba formáty do graph database. Nemá však slepo konvertovať fields, ktorých semantics nie sú ekvivalentné. Lossy conversion musí byť viditeľná.

## 10. Component identity nie je iba name a version

Rovnaký názov package-u môže existovať vo viacerých ecosystems alebo distributions. Version string `1.2.3` nie je globálne unikátny a vendor backport môže zmeniť security content bez zmeny upstream version semantics.

Robustná identity kombinuje:

```text
ecosystem alebo package type
+ namespace
+ name
+ version
+ qualifiers, napríklad distro alebo architecture
+ supplier alebo origin
+ content digest
```

Každý signal rieši inú ambiguity. Package URL štandardizuje ecosystem identity. Digest viaže record na bytes. Supplier a repository pomáhajú rozlíšiť origin. CPE môže pomôcť pri product-level vulnerability matchingu.

## 11. Package URL

Package URL — purl — používa syntax:

```text
pkg:type/namespace/name@version?qualifiers#subpath
```

`type` určuje ecosystem, napríklad `npm`, `maven`, `pypi`, `deb` alebo `rpm`. Namespace a qualifiers majú type-specific semantics. Purl je štandardizovaný v ECMA-427 a používa sa v SPDX, CycloneDX aj vulnerability databases.

Príklad:

```text
pkg:deb/debian/curl@7.88.1-10?arch=amd64&distro=debian-12
```

Purl zlepšuje matching, ale nie je provenance. Nezaručuje, že bytes boli stiahnuté z očakávaného registry alebo že package nebol upravený. Túto hranicu dopĺňa digest a build provenance.

## 12. CPE a product matching

Common Platform Enumeration — CPE — identifikuje products a platforms v mnohých vulnerability datasets. Je užitočná pre appliances, operating systems a commercial products, ale language-package ecosystems často presnejšie reprezentuje purl.

CPE matching môže zlyhať pre:

- nepresné vendor alebo product names;
- rozdielne naming conventions medzi supplierom a NVD;
- distributions s backported patches;
- version ranges, ktoré nezodpovedajú package-manager semantics;
- forked alebo repackaged software.

Purl a CPE sa môžu v jednom recorde dopĺňať. Consumer má vedieť, ktorý identifier použil na finding a aká confidence bola pri matchingu.

## 13. Cryptographic hashes

Hash môže viazať component record na konkrétny archive, file, manifest alebo binary. Musí byť jasné, čo presne bolo hashované.

Hash package archive-u sa líši od hash-u extracted directory, executable file-u alebo OCI manifestu. Bez scope semantics nemožno dva digests porovnať.

Producer má uviesť algorithm a digest a používať collision-resistant algorithm primeraný use case-u. Consumer nesmie považovať rovnaké name/version s rozdielnymi hashes za automaticky rovnaký content.

Hash neposkytuje origin ani trust. Attacker môže dodať malicious bytes aj ich správny hash. Provenance a signature odpovedajú na inú otázku: kto content vytvoril alebo schválil.

## 14. Dependency a containment relationships

SBOM bez relationships je flat inventory. Consumer síce vie, že component sa niekde v dokumente nachádza, ale nevie, prečo tam je ani ako sa dostal do primary subjectu.

Dôležité relation types zahŕňajú:

- `contains` — artifact fyzicky obsahuje component;
- `dependsOn` — component potrebuje ďalší component;
- `generatedFrom` alebo `builtFrom` — output vznikol z inputu;
- `bundledWith` — components sú distribuované spolu;
- `variantOf` — artifact je variantou iného subjectu;
- `distributedAs` — rovnaký software je reprezentovaný inou distribution formou.

Presné názvy sa líšia medzi formats. Pri normalization musí platform zachovať pôvodnú semantics alebo označiť mapping ako approximate.

## 15. Direct, transitive a optional dependencies

Direct dependency deklaruje application tím. Transitive dependency prichádza cez inú package. Incident response potrebuje obe, pretože vulnerability sa často nachádza hlboko v graph-e.

```text
application
├─ direct dependency A
│  └─ transitive dependency C
└─ direct dependency B
   └─ optional dependency D
```

Dependency scope mení risk interpretation. Runtime-required library má iný exposure než test-only tool. Build-only dependency nemusí byť prítomná v final artifacte, ale môže ovplyvniť supply-chain integrity.

„Optional“ neznamená automaticky „unreachable“. Component môže byť nainštalovaný a aktivovaný konfiguráciou. Consumer potrebuje rozlišovať package-manager scope, actual inclusion a runtime reachability.

## 16. Vendored, copied a bundled code

Manifest-based generator vidí packages spravované dependency resolverom. Nemusí vidieť source skopírovaný do repository, manually downloaded JAR, embedded JavaScript bundle alebo library statically linked do binary.

Takýto content potrebuje kombináciu source inventory, file alebo binary analysis, repository policy a manual curation pre critical components.

Vendored component má byť identifikovaný podľa upstream originu a local modifications. Ak organization forkne library a odstráni version metadata, vulnerability matching podľa filename-u bude nepresné.

Explicitný `bundled` alebo `contains` relationship pomáha consumerovi rozlíšiť, že component je súčasťou distributed artifactu, nie iba build environmentu.

## 17. Static linking a compiled languages

Pri static linking sa library code stane súčasťou executable-u a samostatný package file nemusí v runtime filesysteme existovať. OS package inventory ho preto nemusí nájsť.

Build system má zachytiť linker inputs, compiler metadata a resolved module graph. Binary analysis môže hľadať symbols, build IDs alebo embedded package metadata, ale accuracy sa líši podľa language a optimization.

Removal source dependency z manifestu nemusí odstrániť code z už vytvoreného binary. SBOM musí patriť konkrétnemu build outputu, nie iba current source branchu.

## 18. OS packages a vendor backports

Container alebo VM image obsahuje OS distribution packages. Vulnerability scanner nesmie porovnávať iba upstream semantic version.

Linux distribution môže backportovať security patch do staršej package version a ponechať upstream-like version number doplnený distribution revision. Scanner musí používať správny distro advisory source a package epoch/release semantics.

SBOM má preto uchovať distribution, architecture a package-manager identifiers. Generic CPE match môže vytvoriť false positive, ak ignoruje vendor fix status.

## 19. Container images a base-image relationships

Container image SBOM má identifikovať image manifest alebo index digest a components vo final filesysteme. Base image tag nestačí, pretože je mutable.

Build môže použiť multi-stage Dockerfile. Build stage obsahuje compiler a dependencies, ktoré sa do final stage nekopírujú. Final runtime SBOM ich nemá automaticky označiť ako runtime components, ale supply-chain record môže zachovať build relationship.

Base-image relationship umožňuje zistiť, ktoré products treba rebuildnúť po vydaní patched base image. Rebuild je potrebný aj vtedy, keď application dependencies zostali rovnaké, pretože final image digest a OS layers sa zmenia.

## 20. Multi-architecture OCI images

Image index môže odkazovať na viac platform manifests s rozdielnymi OS packages a binaries. Jeden aggregate SBOM môže skryť platform differences.

Bezpečný model viaže:

- release-level SBOM alebo metadata na index digest;
- platform-specific SBOM na každý manifest digest;
- relationships medzi indexom a variants;
- architecture a OS qualifiers pri component identities.

Runtime inventory musí vedieť, ktorú variantu konkrétny node pullol. Vulnerability v arm64-only package nemá automaticky znamenať, že amd64 deployment je affected, ale release governance môže stále vyžadovať opravu celého multi-platform productu.

## 21. Completeness

Completeness opisuje, do akej miery SBOM pokrýva zamýšľaný subject a dependency depth. Nie je to iba počet records.

CycloneDX compositions umožňujú vyjadriť, či je assembly complete, incomplete alebo unknown. Podobnú informáciu možno reprezentovať aj organization-specific quality metadata.

Producer má vysvetliť:

- či analyzoval source, build graph alebo final binary;
- či zahŕňa transitive dependencies;
- či pokrýva OS packages, vendored code a static libraries;
- ktoré paths alebo ecosystems tool nepodporuje;
- či relationships sú complete alebo iba partial.

Consumer nemá interpretovať absenciu componentu ako dôkaz, že v artifacte nie je, ak completeness je unknown.

## 22. Accuracy a false identity

Accuracy znamená, že records správne opisujú skutočný content. Generator môže nájsť filename `log4j-core.jar`, ale nesprávne odhadnúť version. Taký record zvyšuje apparent coverage, no vedie k chybnému CVE matchingu.

Evidence confidence môže závisieť od source:

- lockfile poskytuje silnú declared a resolved package identity;
- package database poskytuje installed package identity;
- binary fingerprint poskytuje content evidence, ale môže mať ambiguous version;
- filename alebo string heuristic má nižšiu confidence.

Platforma má uchovať detection method a confidence, ak format alebo internal model umožňuje. Manuálna correction musí byť auditovateľná a nesmie sa pri ďalšom build-e ticho stratiť.

## 23. Freshness a immutable artifact

SBOM pre immutable artifact sa obsahovo nemení len preto, že pribudla nová CVE. Component inventory ostáva rovnaký; mení sa vulnerability intelligence a VEX status.

Freshness SBOM znamená, že dokument zodpovedá aktuálne distribuovanému artifactu a bol vytvorený pri relevantnom build-e. Freshness vulnerability assessment znamená, že inventory bol nedávno znovu vyhodnotený proti aktuálnym databases.

Tieto timestamps sa nemajú zamieňať. Starší SBOM môže byť stále presný pre historický digest, ale jeho scan result môže byť zastaraný.

## 24. Deterministic generation a semantic stability

Rovnaký artifact a rovnaký generator configuration by mali produkovať semanticky rovnaký inventory. Raw file bytes však môžu obsahovať timestamps, random document IDs alebo odlišné ordering.

Deterministic alebo canonical serialization pomáha pri hashingu, signing-u a diff-e. Ak format používa unique document serial number, organization musí rozlíšiť identity dokumentu od identity jeho semantic contentu.

Generator upgrade môže zmeniť detection accuracy, relationship model alebo component naming bez zmeny artifactu. Taký diff treba označiť ako tooling change, nie automaticky ako software composition change.

## 25. License information

SBOM môže obsahovať declared license, concluded license, copyright notices a license expressions. License scanner však nevytvára právne rozhodnutie automaticky.

Declared license pochádza od package authora alebo metadata. Concluded license je výsledok analysis organizácie alebo toolu. Rozdiel a evidence musia zostať zachované.

License obligations závisia od distribution modelu, linking-u, modifications a jurisdiction. SBOM poskytuje inventory a evidence, ale approval patrí do license governance procesu.

## 26. Vulnerability matching je samostatný dynamický proces

Vulnerability platforma porovná component identities a versions s advisories. Matching môže používať purl, CPE, vendor advisory, OSV ranges, package-manager semantics alebo hashes.

Finding nie je iba CVE číslo. Mal by obsahovať:

- matched component record a identifier;
- advisory source a version range;
- confidence a matching method;
- affected artifact digests;
- deployed environments a owners;
- fix alebo mitigation information;
- VEX alebo local exploitability assessment.

New advisory môže ovplyvniť artifacts vytvorené mesiace predtým. Preto treba uchovávať SBOM corpus a continuous re-evaluation, nie iba scan v CI pri build-e.

## 27. Reachability a exploitability

Prítomnosť vulnerable componentu neznamená automaticky exploitable application. Code path nemusí byť reachable, vulnerable feature môže byť vypnutá alebo component nemusí byť v runtime artifacte.

Naopak, „not reachable“ analysis môže byť neúplná pri reflection, plugins, dynamic loading alebo configuration-specific behavior. Reachability je risk signal, nie absolútny dôkaz vo všetkých languages.

Operational prioritization kombinuje presence, runtime deployment, exposure, reachability, exploit evidence, asset criticality a compensating controls. SBOM poskytuje component presence a graph, ale ďalšie data pochádzajú z runtime a vulnerability managementu.

## 28. VEX

Vulnerability Exploitability eXchange — VEX — je machine-readable statement o stave konkrétnej vulnerability voči konkrétnemu productu alebo componentu. Typický use case je vyjadriť, že product je affected, not affected, fixed alebo under investigation.

VEX nie je zoznam všetkých components; to je úloha SBOM. VEX môže používať SBOM identifiers, ale oba documents môžu existovať samostatne.

```text
SBOM
→ component X je prítomný v artifacte

vulnerability advisory
→ component X môže byť affected CVE-Y

VEX
→ product digest Z je alebo nie je affected CVE-Y a prečo
```

VEX statement potrebuje issuer, timestamp, product identity, vulnerability identity, status a podľa statusu justification alebo action statement.

## 29. VEX status a justification

`not_affected` musí mať technicky obhájiteľný dôvod, napríklad component nie je prítomný, vulnerable code nie je reachable, vulnerable configuration sa nepoužíva alebo inline mitigation zabraňuje exploitation.

`fixed` znamená, že konkrétna product version alebo digest obsahuje remediation. Nemá sa používať iba preto, že supplier vydal patch pre inú variantu.

`under_investigation` je dočasný stav s ownerom a review cadence. Permanentné under-investigation iba odkladá risk decision.

VEX issuer môže byť supplier alebo tretia strana. Consumer musí posúdiť authority a scope issuer-a. Self-asserted `not_affected` bez evidence nemusí spĺňať risk policy high-impact environmentu.

## 30. SBOM, provenance, VEX a signature

Tieto evidence types odpovedajú na rozdielne otázky:

```text
SBOM
→ čo artifact obsahuje

provenance
→ z akých inputs, na akom builderi a ako vznikol

VEX
→ aký je vulnerability status pre konkrétny product

signature alebo attestation
→ kto cryptographically schválil subject alebo claim
```

Jeden dokument nemá byť automaticky interpretovaný ako náhrada ostatných. CycloneDX alebo SPDX môžu reprezentovať viac typov informácií, ale semantics musia zostať oddelené.

## 31. Signing a attestation SBOM

SBOM možno podpísať ako standalone document alebo publikovať ako attestation viazanú na artifact digest. Signature chráni integrity a publisher authenticity.

Consumer musí overiť:

- signed subject alebo attestation subject digest;
- signer identity a issuer;
- supported SBOM format a version;
- document integrity;
- authorization signer-a generovať SBOM pre daný artifact;
- required generation method alebo tool identity podľa policy.

Validná signature nezaručuje completeness. Compromised alebo zle nakonfigurovaný generator môže podpísať neúplný inventory.

## 32. Distribution cez OCI artifacts

SBOM pre container image možno uložiť ako OCI artifact s `subject` descriptorom smerujúcim na image digest. Registry Referrers API umožňuje consumerovi objaviť related SBOM, provenance a signature manifests.

```text
image digest
├─ SBOM attestation
├─ provenance attestation
└─ release signature
```

Registry write permission neznamená automatickú dôveru k referrer artifactu. Consumer musí overiť signature a predicate type.

Promotion alebo replication musí preniesť image aj related artifacts. Copy iba layers a manifestu môže nechať production registry bez SBOM, hoci source registry ho obsahovala.

## 33. Ingestion, normalization a indexing

Enterprise platforma prijíma SBOMs od rôznych suppliers a tools. Najprv musí validovať schema, size limits, signatures a subject identity. Následne normalizuje identifiers a relationships do internal graphu.

Normalization musí zachovať raw source document a transformation evidence. Ak converter zmení purl, zjednoduší relationships alebo zahodí unknown fields, incident responder potrebuje vedieť, čo bolo pôvodné a čo odvodené.

Indexing podľa component identity umožňuje reverse query:

```text
component alebo vulnerability
→ affected SBOM subjects
→ deployed artifacts
→ services a environments
→ owner a remediation status
```

Bez tejto väzby je SBOM archive iba document store.

## 34. Semantic diff

Raw JSON diff je hlučný, pretože ordering, timestamps alebo tool metadata sa môžu meniť bez composition change. Semantic diff porovnáva normalized component identities, relationships, scopes a completeness.

Useful categories sú:

- component added alebo removed;
- version alebo digest changed;
- dependency path changed;
- scope changed z build-only na runtime;
- supplier alebo identifier corrected;
- completeness alebo generation method changed;
- format/tool-only metadata changed.

Release review môže použiť semantic diff na odhalenie neočakávanej novej transitive dependency alebo base-image change.

## 35. Deployment a runtime mapping

Najdôležitejší operational krok je prepojiť artifact digest s deploymentom. SBOM corpus vie, ktoré artifacts obsahujú component. Runtime inventory vie, kde tieto artifacts bežia.

```text
CVE alebo package identity
→ SBOM subject digests
→ Kubernetes Pods, VMs, Lambda versions alebo devices
→ environment a tenant
→ service owner
→ remediation workflow
```

Tag-based deployment inventory je nedostatočný, ak tagy sú mutable. Kubernetes, registry a cloud telemetry majú zachytávať resolved digests.

Runtime mapping tiež musí riešiť artifacts, ktoré sa už nenasadzujú, ale zostávajú dostupné na rollback. Critical vulnerability môže vyžadovať odstránenie affected digestu z rollback catalogu.

## 36. CI/CD gates

SBOM generation v CI má byť viazaná na final artifact digest. Pipeline má validovať schema, subject binding, required ecosystems a minimum quality thresholds.

Gate nemá iba kontrolovať, že súbor `sbom.json` existuje. Má overiť napríklad:

- primary subject digest sa zhoduje s release artifactom;
- generator úspešne pokryl podporované package managers;
- required direct dependencies majú identifiers a versions;
- completeness nie je unknown pre critical release;
- SBOM je podpísaný approved identity;
- semantic diff neobsahuje neapproved high-risk component.

Príliš rigidný completeness gate môže blokovať ecosystem, ktorý tool nepodporuje. Exception musí mať ownera, scope a remediation plan, nie trvalé vypnutie kontroly.

## 37. Procurement a supplier exchange

Pri nákupe software nestačí požadovať „SBOM available“. Contract má definovať format/version, delivery channel, update cadence, supported product versions, VEX process a notification pri supply-chain incidente.

Consumer musí vedieť, či SBOM opisuje generic product, konkrétny build alebo deployed SaaS release. Supplier môže zdieľať document iba authenticated customers pre ochranu citlivých architecture details.

Access restriction je kompatibilná s machine-readable exchange, ak existuje automatizovaný a spoľahlivý retrieval mechanism. PDF export alebo screenshot component listu nepodporuje continuous matching.

## 38. SaaS a continuously changing systems

SaaS nemá vždy jeden downloadable immutable package. Provider priebežne mení services a dependencies. Transparency preto potrebuje service identity, release alebo deployment snapshot, timestamp a customer-relevant scope.

SaaSBOM môže opisovať services, endpoints, dependencies a trust boundaries. Consumer však typicky nevidí interný artifact digest každého microservice-u.

Provider má vysvetliť update model a ako oznámi, že customer-relevant composition alebo vulnerability status sa zmenil. Jednorazový annual SBOM pre continuously deployed SaaS má nízku operational hodnotu.

## 39. xBOM, CBOM a AI BOM

SBOM je jedna BOM variety. CycloneDX a SPDX rozširujú model aj na hardware, services, cryptographic assets, datasets a AI models.

**CBOM** inventarizuje cryptographic algorithms, keys, certificates alebo protocols a pomáha pri crypto-agility a post-quantum migration.

**AI BOM** môže zachytiť models, datasets, frameworks a dependencies. Neopisuje automaticky model behavior, safety alebo training-data legality.

Rozšírenie inventory scope-u má zmysel iba vtedy, keď existuje consumer use case. Collect-all metadata bez ownera a decision workflowu zvyšujú cost a privacy risk.

## 40. Security a privacy SBOM platformy

SBOM môže prezradiť interné product names, obsolete components, architecture alebo exact versions. Distribution a storage potrebujú access control, encryption, tenant isolation a audit.

Parser spracúva untrusted documents. Musí mať size limits, schema validation, safe XML configuration, bounded recursion a protection pred decompression alebo graph-explosion attacks.

Supplier signature chráni document integrity, ale platforma musí chrániť aj normalized database a mappings. Attacker, ktorý zmení deployed-artifact mapping, môže skryť affected production service bez zmeny pôvodného SBOM.

## 41. Incident response pomocou SBOM

Pri novej critical vulnerability postupuje organization od identifieru k reálnemu deploymentu.

```text
normalizovať vulnerability identifiers a affected ranges
→ query component graph
→ overiť matching confidence a vendor backports
→ nájsť subject digests
→ mapovať ich na running a rollback deployments
→ získať VEX, reachability a exposure evidence
→ prioritizovať owners a environments
→ rebuildnúť alebo patchnúť artifacts
→ overiť nové digests a nové SBOMs
→ potvrdiť odstránenie starých deployments
```

SBOM skracuje discovery, ale nezbavuje potreby verification. False identity alebo incomplete graph môže vynechať affected product. Incident tím má kombinovať SBOM s binary scanom, runtime inventory a supplier advisories.

## 42. Troubleshooting SBOM pipeline

Pri missing alebo nepresnom inventory postupuj po generation a consumption chain-e:

```text
source a lockfiles
→ dependency resolver
→ build graph
→ final artifact filesystem/binary
→ SBOM generator a configuration
→ schema validation
→ subject digest binding
→ signature/attestation
→ registry distribution
→ ingestion a normalization
→ vulnerability matching
→ deployment mapping
```

Ak component chýba, zisti, či bol vendored, statically linked, pridaný v multi-stage build-e alebo ignorovaný unsupported ecosystemom. Ak scanner hlási nesprávnu version, porovnaj evidence source a distribution metadata.

Ak SBOM existuje v source registry, ale nie v production, skontroluj Referrers API a promotion tool. Ak finding nemá ownera, problém je v deployment mappingu, nie v SBOM parseri.

## 43. Časté anti-patterny

**Checkbox SBOM.** Pipeline vytvorí file, ale nikto ho nevaliduje, neingestuje ani nepoužíva.

**Subject bez digestu.** Dokument je viazaný iba na product name alebo mutable tag.

**Source-only inventory vydávaný za final artifact SBOM.** Build-added OS alebo embedded components chýbajú.

**Flat list bez relationships.** Consumer nevie dependency path, scope ani containment.

**Unknown interpretované ako absent.** Neúplnosť sa zamieňa za dôkaz neprítomnosti.

**Každý match je exploitable.** SBOM presence sa zamieňa za runtime reachability a impact.

**VEX bez authority a evidence.** `not_affected` sa používa na zníženie backlogu bez technického justification.

**Copy image bez related artifacts.** Production registry stratí SBOM a attestations.

**Inventory bez deployment mappingu.** Organization vie, čo kedysi buildla, ale nevie, čo teraz beží.

## 44. Kompletný production príklad

Predstavme si multi-platform payment API image.

1. Dependency resolver vytvorí locked application graph.
2. BuildKit vytvorí amd64 a arm64 manifests z pinovaného base image-u.
3. Generator analyzuje každý final filesystem a vytvorí platform-specific CycloneDX 1.7 SBOM viazaný na manifest digest.
4. Release metadata vytvoria aggregate record viazaný na image index digest a relationships k variants.
5. CI validuje schemas, purls, direct dependencies, completeness a semantic diff.
6. SBOMs sa publikujú ako signed OCI attestations spolu s provenance.
7. Promotion prenesie image index, manifests, layers a referrers do production registry.
8. Admission policy overí subject, signer a required SBOM predicate.
9. Runtime inventory zaznamená resolved platform manifest digest pre každý Pod.
10. Vulnerability platform priebežne re-evaluuje SBOM corpus a mapuje findings na namespaces, services a owners.
11. Supplier VEX alebo local analysis môže zmeniť exploitability status, ale pôvodný immutable SBOM ostáva zachovaný.
12. Rebuild s patched base image vytvorí nové digests, nové SBOMs a deployment verification potvrdí odstránenie affected variants.

Tento flow ukazuje, že SBOM nie je izolovaný file. Je súčasť artifact identity, registry distribution, policy, vulnerability managementu a runtime inventory.

## 45. Kontrolné otázky

1. Prečo product name a version nestačia na jednoznačný SBOM subject?
2. Ako sa líšia source, build, analyzed a runtime inventory?
3. Aké roly majú producer, distributor a consumer?
4. Ako fungujú SPDX 3.0.1 profiles a prečo nestačí tvrdiť iba „podporujeme SPDX“?
5. Čo predstavuje `bom-ref` a dependency graph v CycloneDX?
6. Aký problém rieši Package URL a čo stále nedokazuje?
7. Prečo sa CPE a purl môžu dopĺňať?
8. Ako rozlíšiš build-only, runtime a optional dependency?
9. Prečo manifest-based generator nemusí vidieť vendored alebo statically linked code?
10. Ako modelovať SBOM pre multi-architecture OCI image?
11. Aký je rozdiel medzi completeness, accuracy a freshness?
12. Prečo nový CVE nemení immutable SBOM, ale vyžaduje nový vulnerability assessment?
13. Ako sa líšia SBOM, provenance, VEX a signature?
14. Čo musí technicky podporovať dôveryhodný `not_affected` VEX status?
15. Ako OCI Referrers API pomáha distribuovať SBOM a akú trust vlastnosť neposkytuje?
16. Prečo raw JSON diff nie je vhodný release review?
17. Ako prepojíš component finding s konkrétnym running workloadom a ownerom?
18. Aké controls potrebuje SBOM ingestion platforma pri spracovaní untrusted documents?
19. Ako by si vyšetril, prečo component chýba vo final image SBOM?
20. Navrhni end-to-end SBOM flow pre container release vrátane CI, registry, policy a runtime remediation.

## Glossary impact

Relevantné pojmy: Software Bill of Materials, SBOM subject, source SBOM, build SBOM, analyzed SBOM, deployed SBOM, runtime inventory, SBOM producer, SBOM consumer, SPDX 3.0.1, SPDX profile, CycloneDX 1.7, primary component, BOM reference, Package URL, Common Platform Enumeration, component identity, component hash, dependency relationship, direct dependency, transitive dependency, dependency scope, vendored code, static linking, base-image relationship, multi-architecture SBOM, SBOM completeness, SBOM accuracy, SBOM freshness, deterministic SBOM, semantic SBOM diff, Vulnerability Exploitability eXchange, VEX status, VEX justification, SBOM attestation, SBOM ingestion, SBOM normalization, SBOM corpus, deployment mapping, SaaSBOM, cryptographic BOM, AI BOM a SBOM quality gate.

## Primárne zdroje

- [SPDX Specification 3.0.1](https://spdx.github.io/spdx-spec/)
- [SPDX 3.0.1 conformance and profiles](https://spdx.github.io/spdx-spec/v3.0.1/conformance/)
- [CycloneDX Specification Overview](https://cyclonedx.org/specification/overview/)
- [CycloneDX 1.7 JSON Reference](https://cyclonedx.org/docs/1.7/json/)
- [Package URL specification](https://github.com/package-url/purl-spec)
- [NTIA Minimum Elements for an SBOM](https://www.ntia.gov/report/2021/minimum-elements-software-bill-materials-sbom)
- [CISA SBOM Resources Library](https://www.cisa.gov/topics/cyber-threats-and-advisories/sbom/sbomresourceslibrary)
- [CISA Minimum Requirements for VEX](https://www.cisa.gov/sites/default/files/2023-04/minimum-requirements-for-vex-508c.pdf)
- [CycloneDX VEX capability](https://cyclonedx.org/capabilities/vex/)
- [OCI Distribution Specification — Referrers API](https://github.com/opencontainers/distribution-spec/blob/main/spec.md)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Supply-chain security](supply-chain-security.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Image signing →](image-signing.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
