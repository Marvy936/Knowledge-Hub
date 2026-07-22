# Supply-chain security

Software supply-chain security chráni dôveryhodnosť software-u od vzniku source revision cez dependency resolution, build, signing, distribution a deployment až po runtime. Nejde iba o scanning open-source packages. Súčasťou supply chain je každý človek, credential, service alebo artifact, ktorý môže ovplyvniť výsledné bytes, ich identity, metadata alebo rozhodnutie, čo sa nasadí.

Základný problém je zachovať dôveru medzi analýzou source a artifactom, ktorý consumer skutočne spustí. Source môže prejsť review a testami, ale compromised builder, mutable dependency, package-publish credential alebo registry tag môže neskôr nahradiť výsledok.

```text
source revision a change history
→ dependency resolution
→ build definition a build platform
→ immutable artifact
→ provenance, SBOM a signatures
→ registry a promotion
→ deployment policy
→ runtime inventory a incident response
```

## 1. Tri otázky supply-chain dôvery

Každý consumer by mal vedieť odpovedať:

1. **Čo presne spúšťame?** Odpoveď vyžaduje immutable artifact identity, napríklad package hash alebo OCI digest.
2. **Odkiaľ artifact vznikol?** Odpoveď poskytuje provenance viazaná na source revision, build definition, dependencies a builder identity.
3. **Prečo mu dôverujeme?** Odpoveď vzniká policy decisionom nad source controls, build guarantees, signer identities, attestations a environment requirements.

Hash odpovedá iba na content identity. Signature odpovedá, kto podpísal subject. SBOM opisuje components. Provenance opisuje build. Žiadny z týchto artifacts samostatne nevytvára kompletný trust decision.

## 2. Software supply chain je graph, nie lineárna pipeline

Reálny artifact má množstvo vstupov. Application repository používa language dependencies, base image, compiler, reusable CI workflow, third-party actions a build service. Každý dependency artifact má vlastnú supply chain.

```text
application repository ─┐
base image ──────────────┤
package dependencies ───┼→ build platform → image digest
compiler a toolchain ────┤                      │
CI actions/workflows ────┘                      ├→ provenance
                                                ├→ SBOM
                                                └→ signature
```

Graph model odhaľuje transitive trust. Pinovaný application source nepomôže, ak build stiahne mutable installer script. Hardened builder nepomôže, ak deployment používa neoverený tag namiesto digestu.

Pre každý node a edge treba poznať ownera, immutable identifier, update path, write authority, verification mechanism, compromise impact a recovery procedure.

## 3. Producer, distributor a consumer

**Producer** spravuje source, build process a release evidence. Môže byť interný tím alebo upstream open-source project.

**Distributor** ukladá a doručuje packages, images, signatures, SBOMs a provenance. Registry alebo package repository nemusí byť pôvodným producerom.

**Consumer** rozhoduje, či artifact použije. Consumer musí overiť identity, integrity, provenance a compatibility so svojou policy; nemá automaticky preberať trust decision producer-a.

Jedna organizácia môže vykonávať všetky tri role, ale trust boundaries zostávajú. Internal registry account compromise je stále distribution threat. Internal CI administrator je stále privileged actor voči build platforme.

## 4. Chránené assets a authority

Supply-chain security chráni viac než source files. Kritické assets zahŕňajú:

- repository history, protected branches a release revisions;
- branch protection, CODEOWNERS a approval rules;
- dependency manifests, lockfiles a registry configuration;
- build definitions, reusable workflows a actions;
- runner images, compilers, toolchains a build caches;
- package-publish, registry a signing credentials;
- artifact digests, provenance, SBOMs a signatures;
- registry namespaces, release channels a promotion records;
- deployment policies, trust roots a audit evidence.

Authority je schopnosť meniť alebo schváliť tieto assets. Attacker nemusí editovať application source, ak vie zmeniť workflow, presunúť release tag, publikovať package do prehľadávaného namespace-u alebo prepísať deployment manifest.

## 5. Threat classes podľa supply-chain stage

Threaty sa ľahšie analyzujú podľa boundary, ktorú napádajú.

**Source threats** zahŕňajú malicious contribution, account takeover, history rewrite a bypass review controls.

**Dependency threats** zahŕňajú dependency confusion, typosquatting, namespace takeover, compromised maintainer release a mutable version resolution.

**Build threats** zahŕňajú workflow injection, compromised runner, cross-tenant contamination, cache poisoning, secret theft a malicious compiler alebo toolchain.

**Distribution threats** zahŕňajú package overwrite, tag substitution, registry compromise, mirror inconsistency, rollback a deletion signatures alebo attestations.

**Deployment threats** zahŕňajú policy bypass, direct deployment path, neoverený digest, stale trust roots a unauthorized promotion.

Threat model má určiť, ktoré controls bránia jednotlivým attacks a ktoré iba poskytujú evidence po incidente.

## 6. Source revision oproti named reference

Git commit SHA identifikuje konkrétnu source revision. Branch a mnohé tags sú named references, ktoré možno presunúť.

```text
main
→ pohyblivý reference

commit 4f2a...
→ konkrétna revision
```

Build z `main` bez zaznamenania resolved commit SHA nie je reproducible ani auditovateľný. Release tag môže byť intended immutable, ale Git technicky umožňuje jeho force-update; platform policy musí immutability presadiť.

Consumer provenance má overovať revision identifier a expected repository identity, nie iba branch name.

## 7. Protected branches a change-management controls

Protected branch chráni process vzniku source revision. Typické controls sú mandatory review, required checks, signed changes podľa risku, restricted push, linear history alebo merge queue a zákaz force-push.

Control je účinný iba vtedy, ak ho administrator alebo automation nemôže potichu obísť. Bypass permissions musia byť minimálne, auditované a používané iba cez break-glass process.

Required check musí byť viazaný na správny commit. Ak approval alebo test result zostane platný po zmene diff-u, attacker môže vložiť code po review.

Branch protection nezaručuje correctness source-u. Reviewer môže schváliť malicious zmenu alebo compromised trusted account môže konať v rámci svojich permissions. Znižuje však unilateral change authority a zlepšuje evidence.

## 8. CODEOWNERS a two-party review

CODEOWNERS mapuje paths na teams alebo reviewers, ktorí rozumejú príslušnej security boundary. Workflow, authentication code a deployment policy môžu vyžadovať odlišných owners než application UI.

Two-party review znamená, že author nemôže sám vytvoriť aj schváliť protected revision. SLSA Source L4 používa review ako ochranu pred insider threats a compromised individual accountom.

Review nesmie byť iba kliknutie. Reviewer potrebuje diff, generated artifacts, test evidence a informáciu o transitive changes, napríklad updated lockfile alebo reusable workflow SHA.

Emergency self-merge môže existovať ako break-glass, ale musí byť explicitne logovaný, časovo obmedzený a následne reviewed.

## 9. Source-control administrator threat

Repository administrator môže meniť branch rules, users, webhooks alebo history. Preto je source-control system súčasťou trusted computing base.

Controls zahŕňajú phishing-resistant MFA, just-in-time administration, separate admin identities, audit export, change alerts a recovery ownership mimo jedného accountu.

Ak attacker získa admin account, môže vytvoriť technically valid revision bez obvyklého review. Source provenance alebo audit musí umožniť zistiť, ktoré controls boli pri vytvorení revision skutočne presadené.

## 10. Dependency resolution je executable policy

Manifest vyjadruje desired dependency constraints. Resolver spolu s registries, lockfile-om a platform-specific rules rozhoduje, ktoré exact artifacts build použije.

```text
manifest constraints
+ registry priority
+ available versions
+ platform qualifiers
+ lockfile state
→ resolved dependency graph
```

Nejasná version range alebo chýbajúci lockfile umožňuje, aby rovnaký source neskôr resolve-nul iné bytes. To môže byť legitímny update, ale znižuje reproducibility a mení trust without source diff.

Lockfile má byť reviewovaný a viazaný na integrity hashes, ak ecosystem podporuje. Update automation musí vytvárať oddelené, testovateľné changes namiesto neviditeľného resolution pri release build-e.

## 11. Dependency confusion

Dependency confusion vzniká, keď resolver vyberie attacker-controlled public package namiesto intended private package s rovnakým názvom. Príčinou je kombinácia namespace ambiguity, registry priority a version selection.

Príklad:

```text
internal manifest: company-utils >= 1.0
public registry: attacker publikuje company-utils 99.0
resolver preferuje najvyššiu verziu
→ malicious package vstúpi do buildu
```

Controls sú private namespace reservation, explicitná registry mapping, scoped package names, lockfiles, allowlisted sources a monitoring neočakávaných public names.

Iba block public internetu nemusí stačiť, ak build používa proxy registry, ktorá namespaces mieša.

## 12. Typosquatting a namespace takeover

Typosquatting používa podobný názov package-u, napríklad zamenené písmeno alebo separator. Developer package pridá vedome, ale vyberie attacker-controlled project.

Namespace takeover nastáva, keď abandoned alebo expired namespace získa nový owner. Existing dependency name zostáva rovnaký, ale authority sa zmení.

Controls zahŕňajú dependency review, registry owner monitoring, popularity-independent allowlists, package signatures a automated detection podobných names. High-impact dependencies majú mať explicitného ownera a replacement plan.

## 13. Version pinning a digest pinning

Version pinning obmedzuje resolver na konkrétnu release version. Digest pinning viaže dependency na exact content.

Version môže byť mutable v ecosystemoch, ktoré povoľujú overwrite alebo republish. Digest poskytuje silnejšiu content identity, ale stále nedokazuje, že content je bezpečný alebo authorized.

Pinning znižuje neplánované changes, ale zvyšuje povinnosť pravidelne aktualizovať. Permanentne pinovaná vulnerable dependency nie je bezpečná iba preto, že je reproducible.

Správny model kombinuje immutable resolution, update automation, testy, vulnerability monitoring a controlled promotion.

## 14. Dependency update automation

Bots môžu pravidelne vytvárať pull requests pre dependency updates. Automatizácia skracuje exposure window, ale môže zahltiť reviewers alebo zlúčiť malicious upstream release príliš rýchlo.

Update workflow má:

- oddeliť dependencies podľa risku;
- zachovať changelog, diff a provenance evidence;
- spustiť tests a policy checks;
- používať cooldown pre neočakávané upstream releases podľa risku;
- neauto-mergeovať major alebo high-impact changes bez review;
- overiť registry, maintainer a artifact identity.

Automation je consumer, nie trust oracle. Musí aplikovať organization policy.

## 15. Third-party CI actions a reusable workflows

CI action alebo reusable workflow je executable dependency s prístupom k checkoutu, environmentu, tokens a často secrets. Compromised action môže meniť artifact alebo exfiltrovať credentials.

GitHub odporúča pin third-party actions na full-length commit SHA, pretože tag môže byť presunutý. SHA pinning zaručí exact Git object, ale nie bezpečnosť jeho code-u.

Consumer má reviewovať source, minimalizovať permissions a používať allowlist actions. Dependabot alebo iný update mechanism môže pripravovať controlled SHA upgrades.

Reusable workflow reference musí byť hodnotená rovnako ako application dependency. Workflow, ktorý vydáva production artifact, je súčasť trusted build definitionu.

## 16. Workflow injection

Workflow injection vzniká, keď untrusted data vstúpia do generated shell scriptu alebo command line bez bezpečného data channelu.

Napríklad pull-request title vložený priamo do `run:` bloku môže uzavrieť string a spustiť attacker command. Environment variable alebo action input oddeľuje data od script source-u, ale called program stále musí bezpečne spracovať argument.

Untrusted pull requests nesmú dostať production secrets, signing identities ani write tokens. Eventy ako `pull_request_target` vyžadujú zvláštnu opatrnosť, pretože workflow môže bežať v trusted base context-e nad attacker-controlled code.

## 17. CI token permissions

CI job dostáva identity a permissions podľa platformy. Default broad write token zväčšuje blast radius každého compromised step-u.

Permissions majú byť explicitné per workflow alebo job. Build job typicky potrebuje read source a write do isolated artifact store, nie administration repository. Release job môže potrebovať registry write a OIDC token, ale nemá spúšťať untrusted code.

Short-lived workload identity je lepšia než static cloud key. Trust policy však musí obmedziť repository, workflow, branch, environment a audience.

## 18. Hosted a self-hosted runners

Runner vykonáva untrusted build code a má access k workspace, networku a credentials jobu. Je to silná trust boundary.

Ephemeral hosted runner sa po jobe zahodí, čo znižuje persistence medzi builds. Self-hosted runner môže mať internú connectivity a persistent disk; malicious job môže zanechať process, modify toolchain alebo ukradnúť credentials budúceho jobu.

Self-hosted runner pre public alebo untrusted pull requests potrebuje silnú izoláciu a ephemeral lifecycle. Shared long-lived shell runner nemá byť použitý na miešanie untrusted a production signing jobs.

Runner labels nie sú security boundary samy osebe. Policy musí kontrolovať, kto môže spustiť job na danom runner group-e.

## 19. Build isolation

Build isolation zabraňuje, aby jeden build ovplyvnil iný build alebo platform control plane. Zahŕňa filesystem, process, network, secret a cache boundaries.

SLSA Build L3 vyžaduje hardened build platform, ktorá bráni runs ovplyvňovať sa navzájom a chráni provenance signing material pred user-defined steps.

Container isolation môže byť nedostatočná pri privileged builds, mounted Docker sockete alebo shared host directories. Vyšší-risk builds môžu potrebovať VM, microVM alebo dedicated ephemeral node.

Isolation treba overovať adversarial tests, nie iba architecture diagramom.

## 20. Build definition a trusted control plane

Build definition určuje steps, inputs, tools, environment a outputs. Ak je definition súčasť source repository, source controls chránia aj build process.

Build platform control plane interpretuje definition, prideľuje runner, injectuje credentials a generuje provenance. Jeho compromise môže meniť outputs bez source change.

Trusted control plane nemá byť ovplyvniteľný user-defined build steps. Signing provenance key alebo OIDC issuance patrí mimo tenant processu.

Version platform components, runner images a reusable workflows má byť zaznamenaná v provenance alebo operations inventory podľa capability.

## 21. Hermetic build

Hermetic build používa deklarované a kontrolované inputs a nečíta neočakávaný network, host filesystem alebo ambient environment state.

Hermeticity zlepšuje reproducibility a audit. Ak build môže stiahnuť `latest` package z internetu, provenance top-level source revision nestačí na rekonštrukciu outputu.

Úplná hermeticity môže byť nákladná. Praktický model používa pre-populated dependency mirror, declared network allowlist a build sandbox a potom postupne znižuje ambient dependencies.

Hermetic build nezaručuje, že declared dependency je bezpečná. Zaručuje najmä, že dependency set je kontrolovaný a pozorovateľný.

## 22. Reproducible build

Reproducible build znamená, že nezávislé buildy z rovnakých declared inputs vytvoria bit-identical alebo definovane equivalent outputs.

Rozdiely môžu spôsobovať timestamps, random IDs, filesystem ordering, compiler paths alebo non-deterministic concurrency.

Reproducibility je silná tamper-detection evidence: independent rebuilder môže porovnať digest s published artifactom. Nie je to automatický proof correctness source-u ani builder-u; dva builds môžu reprodukovať rovnaký malicious source.

Organization má definovať, čo znamená equivalence pre artifacts, ktoré obsahujú unavoidable metadata.

## 23. Build cache poisoning

Cache zrýchľuje build, ale môže prenášať attacker-controlled output medzi trust contexts. Cache key collision, broad restore prefix alebo shared writable cache umožní nahradiť dependency alebo compiled object.

Cache nemá byť authoritative artifact. Release output má byť možné vytvoriť clean buildom bez cache a porovnať výsledok.

Cache namespaces majú oddeľovať untrusted pull requests, protected branches a release builds. Write permissions majú byť užšie než read a integrity checks majú byť viazané na declared inputs.

## 24. Build secrets

Build môže potrebovať registry token, license server credential alebo signing identity. Secret nesmie skončiť v source, image layer, build log, cache ani provenance parameters.

BuildKit secret mounts alebo platform-specific ephemeral secret injection sprístupnia secret iba počas konkrétneho step-u bez persistencie do layeru. Build script však môže secret úmyselne skopírovať alebo exfiltrovať.

Preto production secrets nedávaj untrusted code-u. Oddel build bez secrets od release alebo promotion jobu s úzkymi permissions.

## 25. Artifact identity a build-once-promote-many

Artifact po build-e dostane immutable digest. Test, scan, signing a deployment decisions majú byť viazané na tento digest.

Build-once-promote-many znamená, že staging a production používajú rovnaký content. Promotion mení environment metadata alebo registry location, nie application bytes.

Rebuild pre production ruší väzbu medzi testovaným a nasadeným artifactom. Aj identický source môže vytvoriť iný output pre zmenenú dependency, runner image alebo timestamp.

Promotion musí zachovať signatures, SBOM a provenance a overiť destination digest.

## 26. Provenance

Provenance je verifiable information o tom, kde, kedy a ako artifact vznikol. Typicky obsahuje subject digest, builder identity, build type, external parameters a resolved dependencies.

Provenance umožňuje consumerovi porovnať actual build s expectation:

```text
subject digest sa zhoduje
+ builder je approved
+ source repository a revision sú expected
+ build definition je trusted
+ parameters neobsahujú unsafe override
→ artifact môže pokračovať
```

Provenance môže byť pravdivá, ale opisovať unsafe process. Policy musí vyhodnotiť claims, nie iba existenciu attestation.

## 27. SLSA Build Track

SLSA 1.2 Build Track definuje rastúce guarantees o provenance a build platforme.

**Build L0** nemá SLSA guarantees.

**Build L1** vyžaduje provenance opisujúcu, ako artifact vznikol. Je užitočná pre inventory a mistakes, ale môže byť ľahko forge-nutá.

**Build L2** používa hosted build platform, ktorá sama generuje a podpisuje provenance. Consumer overuje authenticity a chráni sa pred tamperingom po build-e.

**Build L3** vyžaduje hardened platform s isolation medzi runs a ochranou provenance signing materialu pred tenant build steps. Znižuje tampering počas buildu.

Vyšší level nie je všeobecný security rating software-u. SLSA nerieši všetky source, dependency, vulnerability alebo deployment threats.

## 28. SLSA Source Track

SLSA 1.2 Source Track opisuje, ako dôveryhodne vznikla source revision.

- **Source L1** — source je version-controlled a má discrete revisions.
- **Source L2** — change history je zachovaná a source control system vydáva source provenance.
- **Source L3** — organization priebežne technicky presadzuje deklarované source controls.
- **Source L4** — changes vyžadujú two-party review.

Source level je claim o process-e od určitého onboarding revisionu, nie retroaktívne o celej histórii. Consumer má overovať Source VSA alebo provenance voči organization expectation.

Source Track a Build Track sa dopĺňajú. Trusted source process bez hardened build-u stále umožňuje build tampering. Hardened build z malicious source vytvorí dôveryhodne malicious artifact.

## 29. in-toto model

in-toto chráni integrity supply-chain steps pomocou signed layoutu a link metadata. Project owner definuje expected steps a authorized functionaries. Každý step zaznamená materials, products a command evidence.

```text
signed layout
→ expected steps a authorized actors

signed links
→ čo jednotliví actors vykonali a aké inputs/outputs použili

verification
→ porovná actual chain s layoutom
```

in-toto Attestation Framework poskytuje general statement model používaný aj SLSA predicates. Attestation je authenticated claim; consumer musí dôverovať issuerovi a rozumieť predicate schema.

## 30. Signature, attestation, provenance a SBOM

Tieto artifacts majú odlišné semantics:

- signature — cryptographic binding identity/keyu na subject alebo payload;
- attestation — signed claim o subjecte;
- provenance — claim o build/source process-e;
- SBOM — inventory components a relationships;
- VEX — vulnerability status productu.

Policy môže požadovať kombináciu. Validná release signature bez provenance nevysvetlí build. Provenance bez SBOM nevysvetlí composition. SBOM bez signature nemusí byť dôveryhodne viazaný na artifact.

## 31. Registry a package repository security

Registry chráni namespaces, manifests, blobs, tags a related artifacts. Write permission k repository je release authority.

Controls zahŕňajú immutable tags pre releases, digest addressing, scoped tokens, deletion protection, audit, retention, replication a garbage collection aware signatures/referrers.

Package-publish credential theft môže obísť source a build controls, ak consumer akceptuje každý artifact v namespace. Provenance verification znižuje tento risk: malicious upload bez expected builder attestation je odmietnutý.

## 32. TUF update security

The Update Framework pridáva signed metadata a role separation do software update systems. Chráni nielen artifact authenticity, ale aj rollback, freeze, mix-and-match a key-compromise scenarios.

Štyri top-level roles sú:

- **Root** — definuje trusted keys a thresholds ostatných roles;
- **Targets** — viaže downloadable files na hashes a metadata;
- **Snapshot** — poskytuje consistent view versions targets metadata;
- **Timestamp** — krátkodobé online metadata signalizujú freshness snapshotu.

Delegated targets roles rozdeľujú authority podľa paths alebo products. Expirations a version numbers umožňujú clientovi odmietnuť stale alebo rollback metadata.

TUF nerieši bezpečnosť samotného source alebo buildu; chráni update distribution a trust-root rotation.

## 33. Artifact promotion a environment policy

Promotion je decision, že konkrétny artifact digest smie postúpiť do environmentu. Nemá byť rebuildom ani copy bez verification.

Promotion evidence môže obsahovať tests, vulnerability status, provenance verification, approvals a error-budget policy. Environment-specific rule môže byť prísnejšia pre production než staging.

Destination registry musí potvrdiť digest a related attestations. Promotion record má zachytiť source, destination, actor, time, policy revision a subject digest.

## 34. Deployment verification

Deployment manifest alebo controller musí používať immutable digest a overovať signatures/provenance na final boundary.

CI gate je skorý feedback, ale môže byť obídený manual deploymentom. Admission policy alebo deployment controller chráni actual runtime path.

Mutation ordering je dôležitý: ak component zmení image po verification, final object musí prejsť validation znova. Custom workload controllers a direct node paths musia byť zahrnuté do threat modelu.

## 35. Runtime inventory a continuous re-evaluation

Runtime inventory mapuje artifact digests na workloads, environments a owners. Umožňuje zistiť, kde beží artifact, ktorého key, builder alebo dependency bol neskôr compromised.

Provenance a SBOM sa re-evaluujú proti novým policies a vulnerability intelligence. Immutable artifact sa nemení, ale jeho trust status sa môže zmeniť.

Quarantine policy môže zablokovať nové deployments a postupne nahradiť running instances. Runtime enforcement musí dostať revocation updates s meranou latency.

## 36. Open-source supplier assessment

OpenSSF Scorecard automatizuje checks source, build, dependency, testing a maintenance practices. Výstup je signal, nie complete risk assessment.

High score nezaručuje, že package je bezpečný. Low score nemusí znamenať malicious project. Consumer má zohľadniť maintainer model, release process, responsiveness, project criticality a transitive reach.

Supplier assessment má byť risk-tiered. Critical cryptographic library potrebuje hlbší review než low-impact development tool.

## 37. Vendor a supplier due diligence

Commercial supplier assessment zahŕňa secure development process, vulnerability disclosure, SBOM/VEX delivery, build provenance, signing, incident notification, recovery a support lifecycle.

Contract má definovať, ktoré artifacts a versions sú covered, ako sa evidence doručuje a čo sa stane pri key alebo build compromise.

Certifikácia alebo questionnaire je point-in-time evidence. Organization potrebuje continuous monitoring a product-specific trust policy.

## 38. Infrastructure a configuration supply chain

Terraform modules, Helm charts, Ansible collections, Kubernetes manifests a policy bundles sú executable supply-chain artifacts. Môžu meniť cloud resources, RBAC alebo admission.

Version pinning, source review, artifact signing a provenance platia rovnako ako pri application binaries. Mutable Git branch module source alebo Helm chart tag môže zmeniť production bez local source diffu.

Rendered configuration a plan majú byť viazané na input revisions a approved workflow identity.

## 39. AI a model supply chain

AI system môže závisieť od model weights, datasets, tokenizerov, frameworks, plugins a external APIs. Model artifact je executable alebo behavior-determining input.

Threaty zahŕňajú poisoned dataset, substituted weights, malicious serialized model, compromised model registry a untrusted plugin.

Digest, provenance, model/dataset inventory a sandboxed loading sú potrebné, ale nevysvetľujú model behavior alebo safety. Evaluation evidence tvorí ďalšiu vrstvu.

## 40. Incident response pri supply-chain compromise

Response začína identifikáciou compromised authority a všetkých odvodených artifacts.

```text
zastaviť source/build/publish/signing authority
→ zachovať audit, provenance, registry a transparency evidence
→ určiť compromise interval
→ enumerovať revisions a digests
→ zablokovať promotion a nové deployments
→ mapovať affected runtime
→ rotovať credentials a trust roots
→ opraviť source/platform
→ rebuildnúť z trusted inputs
→ overiť nové evidence a invaliditu starého pathu
```

Ak bol compromised package-publish token, artifacts s expected trusted provenance môžu zostať validné; neočakávané uploads sa quarantine-nú. Ak bol compromised builder, aj validne signed provenance z affected interval-u môže byť nedôveryhodná.

## 41. Recovery a last-known-good chain

Recovery potrebuje last-known-good source revision, build definition, builder platform, dependencies, signing identity a deployment policy. Samotný artifact backup nestačí, ak organization nevie preukázať jeho origin.

Rebuild po incidente musí používať rotated credentials a fixed infrastructure. Re-signing starého potentially compromised digestu nevytvára dôveryhodný artifact.

Recovery test má preukázať, že staré credentials, mutable tags a bypass paths už nefungujú.

## 42. Kompletný production flow

1. Source revision vznikne na protected branch s two-party review a passing checks.
2. Dependencies sa resolve-nú z approved registries do integrity-checked lockfile-u.
3. Hosted isolated builder checkoutne exact revision a declared inputs.
4. Build platform vytvorí immutable OCI digest a signed SLSA provenance.
5. Generator vytvorí digest-bound SBOM.
6. Protected release workflow overí tests, provenance, SBOM a policy.
7. Keyless signing identity podpíše release digest.
8. Registry uloží image, signature a attestations cez subject/referrers model.
9. Promotion kopíruje rovnaký digest do production registry.
10. Admission policy overí signer, builder, source revision a required evidence.
11. Runtime inventory zaznamená resolved digest, ownera a environment.
12. Continuous monitoring re-evaluuje SBOM a provenance pri nových vulnerabilities alebo revoked authorities.

Každý step má explicitnú identity, artifact a failure behavior. To je podstata supply-chain security: nie „máme scanner“, ale overiteľný trust chain.

## 43. Troubleshooting supply-chain evidence

Pri verification failure postupuj od subjectu späť k source:

```text
deployed digest
→ registry manifest a referrers
→ signature a signer identity
→ provenance subject a builder
→ source repository a revision
→ build definition
→ resolved dependencies
→ policy expectation
```

Ak provenance chýba, over promotion a registry copy. Ak subject digest nesedí, artifact bol rebuildnutý alebo transformed. Ak signer je validný, ale policy deny, porovnaj exact OIDC claims a environment.

Pri reproducibility failure porovnaj declared dependencies, timestamps, toolchain versions a ambient network. Pri unexpected dependency zisti resolver source a lockfile diff.

## 44. Časté anti-patterny

**Scan source, trust binary.** Review a SAST prebehli, ale neexistuje binding na deployed digest.

**Pin tags, nie revisions.** Branch, image alebo action tag sa môže presunúť.

**Untrusted code so signing permission.** Pull request job získa production OIDC identity.

**Shared persistent runner.** Malicious job ovplyvní budúci release build.

**Cache ako source truth.** Poisoned cache vstúpi do artifactu bez clean-build verification.

**Provenance existence gate.** Policy nekontroluje builder, source ani parameters.

**Build twice.** Production artifact nie je ten, ktorý prešiel testami.

**Registry copy bez attestations.** Production verification stratí signatures, SBOM alebo provenance.

**SLSA level ako universal score.** Build guarantees sa zamieňajú za source, dependency a runtime security.

## 45. Kontrolné otázky

1. Prečo je software supply chain graph a nie lineárny zoznam steps?
2. Aký je rozdiel medzi source revision a named reference?
3. Ktoré threats branch protection rieši a ktoré nerieši?
4. Ako dependency confusion využíva resolver a registry priority?
5. Prečo digest pinning nezaručuje bezpečnosť dependency?
6. Ako third-party CI action získava supply-chain authority?
7. Aké boundaries musí chrániť self-hosted runner?
8. Ako sa líši hermetic a reproducible build?
9. Čo znamená SLSA Build L1, L2 a L3?
10. Ako sa Source Track dopĺňa s Build Trackom?
11. Čo je in-toto layout a link evidence?
12. Aký je rozdiel medzi provenance, SBOM, signature a attestation?
13. Ako TUF chráni pred rollback a freeze attacks?
14. Prečo build-once-promote-many zlepšuje trust?
15. Ako by si reagoval na compromise package-publish credentialu oproti compromise builderu?
16. Ako preukážeš, že runtime artifact je ten, ktorý prešiel review a tests?
17. Navrhni trust policy pre production OCI image.
18. Ktoré controls musia byť fail-closed a kde potrebuješ degraded mode?
19. Ako obnovíš last-known-good supply chain po compromise CI platformy?
20. Vytvor threat model pre repository → GitHub Actions → registry → Kubernetes flow.

## Glossary impact

Relevantné pojmy: software supply chain, supply-chain graph, producer, distributor, consumer, source revision, named reference, protected branch, CODEOWNERS, two-party review, dependency confusion, typosquatting, namespace takeover, dependency pinning, digest pinning, CI action dependency, workflow injection, build isolation, hermetic build, reproducible build, cache poisoning, build secret, build-once-promote-many, provenance, SLSA Build Track, SLSA Source Track, Source VSA, in-toto layout, in-toto link, attestation, release authority, artifact promotion, registry namespace, TUF Root, TUF Targets, TUF Snapshot, TUF Timestamp, runtime inventory, artifact quarantine a supply-chain recovery.

## Primárne zdroje

- [SLSA Specification 1.2](https://slsa.dev/spec/v1.2/)
- [SLSA Build Track Basics](https://slsa.dev/spec/v1.2/build-track-basics)
- [SLSA Source Track Requirements](https://slsa.dev/spec/v1.2/source-requirements)
- [SLSA Provenance](https://slsa.dev/spec/v1.2/provenance)
- [in-toto Specifications](https://in-toto.io/docs/specs/)
- [in-toto Getting Started](https://in-toto.io/docs/getting-started/)
- [The Update Framework Overview](https://theupdateframework.io/docs/overview/)
- [TUF Roles and Metadata](https://theupdateframework.io/docs/metadata/)
- [OpenSSF Scorecard](https://securityscorecards.dev/)
- [GitHub Actions Secure Use Reference](https://docs.github.com/en/actions/reference/security/secure-use)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Threat modeling](threat-modeling.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: SBOM →](sbom.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
