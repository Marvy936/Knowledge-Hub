# Supply-chain security

Software supply-chain security chráni dôveryhodnosť software-u od source revision cez dependencies, build, signing, registry a deployment až po runtime. Nejde iba o kontrolu open-source packages. Každý systém, ktorý môže zmeniť alebo nahradiť výsledný artifact, metadata alebo deployment decision, je súčasťou supply chain.

## 1. Mentálny model

```text
source identity a revision
→ dependency resolution
→ build instructions a build platform
→ artifact a provenance
→ signing a release approval
→ registry alebo package repository
→ promotion a deployment policy
→ runtime verification a incident response
```

Supply-chain control musí odpovedať na tri otázky:

```text
Čo presne spúšťame?
→ Odkiaľ to vzniklo?
→ Prečo tomu dôverujeme?
```

Hash, signature, SBOM ani provenance samostatne neodpovedajú na všetky tri.

## 2. Čo je software supply chain

Software supply chain zahŕňa:

- source-control systems,
- maintainers, reviewers a administrators,
- package managers a dependency resolvers,
- upstream packages, modules, images, charts a actions,
- build scripts, compilers a toolchains,
- CI/CD workflows, runners, caches a artifact stores,
- registries a release repositories,
- signing identities, keys a transparency services,
- deployment controllers a admission policies,
- update clients a runtime environments.

Boundary nie je daná organizačným vlastníctvom. Externý package registry alebo hosted CI je stále súčasťou trust modelu.

## 3. Producer, distributor a consumer

### Producer

Vytvára source, build process, artifact a evidence.

### Distributor

Ukladá a doručuje artifact, signatures, SBOM a provenance.

### Consumer

Overuje identity, digest, policy a suitability pred použitím.

Jedna organizácia môže vykonávať všetky tri role, ale trust decisions majú zostať explicitné.

## 4. Chránené assets

Kritické assets zahŕňajú:

- source history a protected branches,
- release tags a source revisions,
- build definitions,
- dependency lockfiles,
- build runner identity a isolation,
- package-publish credentials,
- signing keys alebo workload identities,
- artifact digests,
- provenance a attestations,
- registry namespaces,
- deployment policies,
- audit evidence.

Útočník nepotrebuje meniť application source, ak vie zmeniť build script, cache, dependency, package namespace alebo published artifact.

## 5. Supply-chain graph

Lineárny pipeline diagram nestačí. Reálny model je graph:

```text
repository A ─┐
package B ────┼→ builder → image digest D → registry → deployment
base image C ─┤              ↑
action E ─────┘              provenance + SBOM + signature
```

Pre každý node a edge eviduj:

- ownera,
- identifier a version,
- trust root,
- write authority,
- verification mechanism,
- update path,
- compromise impact,
- recovery procedure.

## 6. Threat classes

Typické threat classes:

- malicious source contribution,
- maintainer alebo administrator account takeover,
- dependency confusion alebo typosquatting,
- compromised upstream release,
- mutable tag alebo branch substitution,
- CI workflow injection,
- runner alebo build-platform compromise,
- cache a artifact poisoning,
- package-publish credential theft,
- signature alebo provenance forgery,
- registry overwrite alebo deletion,
- policy bypass pri deploymente,
- rollback na starý vulnerable artifact,
- evidence omission alebo metadata mismatch.

Vulnerable dependency a malicious dependency sú odlišné incidenty. Prvý môže obsahovať neúmyselnú chybu; druhý môže vykonávať attacker intent aj bez známeho CVE.

## 7. Source identity

Source musí byť identifikovaný stabilným repository locatorom a immutable revision identifierom.

```text
repository identity + revision digest
```

Branch alebo tag je human-friendly reference, nie dostatočná immutable identity. Release evidence má ukazovať na konkrétnu revision.

## 8. Source-control governance

Minimálny model pre protected source:

- centralizovaná identity a MFA,
- least-privilege repository roles,
- protected default a release branches,
- pull request alebo merge request workflow,
- required status checks,
- zákaz force push a deletion,
- review po poslednej zmene,
- audit administratívnych zmien,
- break-glass proces,
- pravidelný access review.

Repository setting je security control iba vtedy, keď je jeho kontinuita monitorovaná a zmenu nemožno skryto obísť.

## 9. Code review

Review znižuje riziko chyby a unilateral malicious change.

Silný review contract určuje:

- kto je trusted reviewer,
- ktoré paths vyžadujú CODEOWNERS,
- koľko approvals je potrebných,
- či nový push invaliduje approval,
- či reviewer vidí generated artifacts a workflow diff,
- ako sa rieši emergency change,
- kto môže bypass-nuť pravidlo.

Dve approvals od dvoch účtov nie sú automaticky two-party control, ak ich ovláda tá istá osoba alebo automatizácia.

## 10. SLSA Source track

SLSA 1.2 Source track popisuje rastúce guarantees pre source revisions:

```text
Source L1 → version-controlled source
Source L2 → zachovaná history a source provenance
Source L3 → kontinuálne technical controls
Source L4 → two-party review
```

Level je claim o konkrétnej source revision a enforcemente, nie všeobecné označenie organizácie.

## 11. Maintainer identity compromise

Controls:

- phishing-resistant MFA,
- hardware-backed credentials,
- short-lived administrative elevation,
- separate daily a privileged accounts,
- protected recovery methods,
- alerting na nové tokens, keys a sessions,
- organization-wide session revocation,
- signed administrative audit trail,
- emergency repository lockdown.

Po takeover-e nestačí zmeniť password. Treba overiť source history, branch rules, workflows, secrets, release artifacts, deploy keys, webhooks a package registries.

## 12. Commit a tag signatures

Signed commit alebo tag môže dokazovať, že určitý key alebo identity podpísala konkrétny Git object.

Nedokazuje automaticky:

- že signer mal právo zmenu schváliť,
- že review prebehlo,
- že build použil daný commit,
- že artifact zodpovedá source,
- že key nebol kompromitovaný,
- že deployment prijal správny artifact.

Signature musí byť vyhodnotená policy engine-om s identity a authorization contextom.

## 13. Dependency trust

Pre každú dependency vyhodnoť:

- package ecosystem a namespace,
- supplier alebo maintainer,
- source repository,
- release process,
- version a digest,
- license,
- maintenance status,
- vulnerability a malicious-package signals,
- update cadence,
- transitive graph,
- replacement a removal cost.

Popularita nie je security assurance.

## 14. Direct a transitive dependencies

Direct dependency je explicitne deklarovaná application.

Transitive dependency je privedená inou dependency.

Risk sa môže nachádzať hlboko v graph-e:

```text
application
→ framework
→ serializer
→ parser
→ compromised utility
```

Lockfile a SBOM musia zachytiť resolved graph, nie iba top-level manifest.

## 15. Dependency confusion

Dependency confusion vzniká, keď resolver vyberie attacker-controlled package z public registry namiesto zamýšľaného private package-u.

Controls:

- oddelené a rezervované namespaces,
- explicitné registry routing,
- private registry authentication,
- zákaz nečakaného public fallbacku,
- internal package-name monitoring,
- lockfile a integrity hashes,
- egress restrictions pre builders,
- test na resolver precedence.

## 16. Typosquatting a namespace takeover

Typosquatting využíva podobný názov package-u.

Namespace takeover využíva opustený, expirovaný alebo nepridelený namespace.

Kontroluj:

- exact package identity,
- publisher history,
- repository link,
- release age,
- owner changes,
- unexpected install scripts,
- dependency graph delta,
- package digest.

## 17. Version constraints, lockfiles a digests

Version range vyjadruje compatibility intent.

Lockfile zaznamenáva konkrétny resolved graph.

Digest viaže consumera na konkrétny obsah.

```text
constraint → čo je povolené resolveru
lockfile   → čo resolver vybral
digest     → aké presné bytes sa očakávajú
```

Lockfile bez integrity fields môže zostať zraniteľný voči registry substitution. Digest pinning bez update automation vytvára stale dependencies.

## 18. Dependency update automation

Update bot má:

- minimálne permissions,
- oddelenú identity,
- bounded package scope,
- vytvárať reviewable pull requests,
- aktualizovať lockfile a SBOM,
- spúšťať testy a policy,
- neobchádzať review pri sensitive dependencies,
- nepublishovať releases priamo.

Automatizácia znižuje age, ale zároveň vytvára privileged contribution path.

## 19. Build definition

Build definition zahŕňa:

- workflow,
- Dockerfile alebo build script,
- compiler a toolchain,
- environment,
- flags,
- dependencies,
- source revision,
- target platform.

Build definition musí byť versionovaná a reviewovaná. UI-only pipeline changes sú hidden source.

## 20. Build platform ako trust boundary

Build platform má schopnosť:

- čítať source,
- získavať dependencies,
- vykonávať arbitrary code,
- čítať build secrets,
- vytvárať artifacts,
- generovať provenance,
- často publishovať.

Preto je builder security boundary porovnateľná s production deployment platformou.

## 21. Hosted a self-hosted runners

### Hosted runner

Výhodou je ephemeral lifecycle a provider-managed isolation. Rizikom je external trust a platform compromise.

### Self-hosted runner

Výhodou je kontrola prostredia. Riziká:

- persistent workspace,
- stale credentials,
- cross-job contamination,
- network access,
- privileged Docker socket,
- untrusted code na trusted hoste,
- nedostatočný patching.

Self-hosted neznamená automaticky dôveryhodnejší.

## 22. Ephemeral build isolation

Preferuj:

- fresh worker per job,
- immutable base image,
- no cross-job filesystem,
- no reusable credentials,
- scoped network access,
- unprivileged execution,
- isolated cache namespace,
- cleanup verification,
- workload-bound identity.

Ephemeral worker stále môže byť kompromitovaný počas jedného build runu. Potrebuje bounded authority.

## 23. CI workload identity

Preferuj short-lived federated identity viazanú na:

- repository,
- workflow,
- branch alebo environment,
- commit,
- job,
- audience,
- organization.

Cloud alebo registry trust policy musí validovať konkrétne claims. Samotný dôveryhodný OIDC issuer nestačí.

## 24. CI token permissions

Default má byť read-only.

Write permissions povoľ job-specifically:

- `contents`,
- packages,
- deployments,
- attestations,
- identity token,
- security reports.

Build job, ktorý spracúva untrusted source, nemá mať release alebo production authority.

## 25. Untrusted pull-request workflows

Nebezpečný pattern:

```text
privileged event
+ attacker-controlled checkout
+ write token alebo secrets
→ repository compromise
```

Oddel:

- untrusted test workflow bez secrets,
- trusted post-merge build,
- protected release workflow,
- manual alebo policy-gated promotion.

Untrusted metadata nevkladaj priamo do shell scriptu.

## 26. Third-party actions a plugins

CI action, plugin alebo orb je executable dependency.

Controls:

- allowlist,
- pinning na immutable commit digest,
- source a maintainer review,
- minimal inputs a permissions,
- network restrictions,
- update automation,
- removal of unused actions,
- provenance/signature verification, ak ecosystem podporuje.

Major-version tag je mutable convenience reference.

## 27. Build secrets

Build secret nesmie byť:

- dostupný pull-request code-u,
- baked do layeru,
- uložený v cache,
- vypísaný do logu,
- shared medzi repositories,
- dlhodobo platný bez revocation.

Použi ephemeral credential viazaný na konkrétny build purpose.

## 28. Cache poisoning

Cache key musí byť viazaný na relevantný trust context:

- repository,
- branch/trust level,
- dependency lock digest,
- toolchain version,
- target platform.

Untrusted branch nesmie zapisovať cache, ktorú bez validácie používa protected release build.

## 29. Artifact poisoning

Intermediate artifact potrebuje:

- immutable identifier,
- producer identity,
- source/build binding,
- integrity verification,
- retention,
- promotion policy.

Filename ako `app.zip` nie je artifact identity.

## 30. Hermetic build

Hermetic build získava všetky inputs cez deklarovaný a kontrolovaný mechanism bez nezdokumentovaného network alebo host dependency accessu.

Výhody:

- presnejšia provenance,
- menší dependency-confusion surface,
- reprodukovateľnosť,
- jednoduchší audit.

Hermetic neznamená, že deklarované inputs sú bezpečné.

## 31. Reproducible build

Reproducible build umožňuje nezávisle vytvoriť rovnaký output z rovnakých inputs.

Pomáha overovať buildera, ale vyžaduje kontrolu:

- timestamps,
- ordering,
- locale,
- paths,
- toolchain,
- network data,
- randomness,
- generated metadata.

Dva identické malicious buildy môžu byť reprodukovateľné. Reproducibility nie je intent validation.

## 32. Provenance

Build provenance spája artifact s build procesom a inputs:

```text
artifact digest
← builder identity
← build type
← source revision
← declared dependencies
← invocation a environment metadata
```

Provenance má byť generovaná build platformou, nie user-controlled build scriptom, ak má poskytovať tamper resistance.

## 33. Attestation

Attestation je signed statement o subjecte.

```text
subject digest
+ predicate type
+ predicate
+ signer alebo issuer identity
```

Príklady predicates:

- build provenance,
- SBOM,
- test result,
- vulnerability scan,
- policy decision,
- source verification summary.

Attestation je evidence. Consumer stále potrebuje policy.

## 34. in-toto

in-toto modeluje supply-chain steps, materials, products a authorized functionaries.

Pomáha vyjadriť:

- kto smie vykonať step,
- aké inputs očakáva,
- aké outputs vytvára,
- aké inspections musia prebehnúť.

Metadata bez enforcementu alebo správneho root of trust zostávajú iba dokumentáciou.

## 35. SLSA 1.2

SLSA 1.2 má samostatný Source a Build track.

Build track:

```text
Build L0 → bez guarantees
Build L1 → provenance existuje
Build L2 → signed provenance z hosted build platformy
Build L3 → hardened build platform s izoláciou
```

Source track pokrýva source history, provenance, technical controls a two-party review.

SLSA level musí byť overený pre konkrétny artifact a platformu. Logo alebo marketingové tvrdenie nie je verification.

## 36. SLSA Build L3 boundary

Build L3 vyžaduje silné controls, aby:

- build runs nemohli navzájom ovplyvňovať svoj stav,
- user-defined build steps nemali prístup k provenance signing materialu,
- provenance bola dôveryhodne viazaná na output.

L3 nerieši všetky dependency, source-intent, vulnerability ani deployment-policy threats.

## 37. Package a registry publishing

Publishing authority oddeľ od build execution.

Controls:

- protected environment,
- short-lived publish credential,
- namespace restriction,
- immutable version policy,
- digest verification,
- provenance/signature attachment,
- two-party release approval podľa risku,
- audit a anomaly alerting.

## 38. Immutable promotion

Build once, promote by digest:

```text
verified digest
→ development
→ staging
→ production
```

Rebuild per environment vytvára nové artifacts a nové supply-chain decisions.

Environment-specific configuration má byť oddelená od artifact identity.

## 39. Registry controls

Registry potrebuje:

- private/public namespace governance,
- immutable release tags alebo version policy,
- delete protection,
- replication integrity,
- vulnerability scanning,
- signature a attestation retention,
- least-privilege robot accounts,
- audit logs,
- retention a garbage-collection policy,
- break-glass recovery.

Registry admin môže byť schopný meniť alebo mazať evidence; preto je critical principal.

## 40. TUF

The Update Framework chráni software update systems proti rollback, freeze, mix-and-match a key-compromise scenárom.

Top-level roles:

```text
root
targets
snapshot
timestamp
```

TUF používa role separation, metadata expiration, delegated trust a threshold signatures. Artifact signature sama osebe nerieši secure update lifecycle tak komplexne ako TUF.

## 41. Supplier due diligence

Due diligence zahŕňa:

- supplier identity a ownership,
- secure-development process,
- source a build controls,
- vulnerability disclosure,
- SBOM a provenance support,
- incident notification,
- maintenance a EOL policy,
- key management,
- subcontractors a transitive suppliers,
- recovery a continuity.

Questionnaire bez evidence neposkytuje silné assurance.

## 42. OpenSSF Scorecard

Scorecard automatizovane hodnotí heuristics ako:

- branch protection,
- code review,
- dangerous workflows,
- token permissions,
- pinned dependencies,
- signed releases,
- security policy,
- dependency updates.

Score je triage signal, nie certifikácia. Tool nemusí vidieť private controls, business context ani hidden build infrastructure.

## 43. Kubernetes supply chain

Modeluj:

```text
source
→ image build
→ registry digest
→ signature/provenance/SBOM
→ admission policy
→ Pod spec
→ runtime image
```

Controls:

- digest pinning,
- allowed registries,
- image signature a provenance verification,
- namespace-specific policy,
- service-account separation,
- no mutable `latest`,
- runtime inventory,
- emergency quarantine.

## 44. Infrastructure a policy artifacts

Rovnaké princípy aplikuj na:

- Terraform modules a providers,
- Helm charts,
- Kubernetes manifests,
- Ansible collections,
- policy bundles,
- CI templates,
- base VM images,
- firmware.

Textový configuration artifact môže poskytnúť rovnakú privileged authority ako application binary.

## 45. AI a data supply chain

AI systém môže závisieť od:

- model weights,
- training a evaluation data,
- tokenizerov,
- adapters,
- code packages,
- prompts a policies,
- model registry,
- conversion a quantization tools.

Eviduj provenance, licenses, integrity, access, transformation steps a unsafe deserialization risks.

## 46. Consumer verification

Consumer workflow:

```text
resolve immutable artifact
→ over digest
→ over signature identity
→ over provenance a builder
→ vyhodnoť source revision a policy
→ ingestuj SBOM/VEX
→ rozhodni o promotion/deployment
→ zachovaj evidence
```

„Signature valid“ je iba jeden krok.

## 47. Policy enforcement points

Enforcement môže byť:

- dependency admission,
- merge gate,
- build gate,
- registry admission,
- release approval,
- deployment admission,
- runtime detection.

Control umiestni čo najbližšie k authority, ktorú chráni. Scanner po production deploymente nie je náhrada pre pre-deployment policy.

## 48. Supply-chain incident response

Pri podozrení na compromised component alebo pipeline:

```text
identifikovať affected source/artifact digests
→ zastaviť publish a promotion
→ revoke-nuť credentials a signing authority
→ zachovať source, logs, provenance a registry evidence
→ určiť exposure window a downstream consumers
→ quarantine artifacts
→ rebuildnúť v trusted environment
→ vydať fixed artifact a advisory
→ overiť deployments
→ opraviť trust boundary
```

Nemaž compromised artifacts skôr, než zachováš forensic evidence a downstream identity mapping.

## 49. Recovery

Recovery plán musí pokryť:

- source host compromise,
- package registry takeover,
- builder compromise,
- signing identity compromise,
- artifact-store corruption,
- transparency alebo KMS outage,
- dependency disappearance,
- forced history rewrite,
- malicious release rollback.

Rebuild z rovnakého compromised buildera nie je trusted recovery.

## 50. Audit a telemetry

Sleduj:

- protected-branch rule changes,
- privileged identity a token creation,
- workflow changes,
- runner image a configuration,
- unexpected network access,
- cache read/write lineage,
- build and publish identities,
- artifact digest transitions,
- provenance/signature generation,
- registry deletes/overwrites,
- policy allow/deny,
- deployment digest.

Logs nesmú obsahovať signing keys, tokens ani private package credentials.

## 51. Metrics

Užitočné metrics:

- percento releases via protected pipeline,
- percento artifacts s provenance, SBOM a signature,
- digest-pinned deployment coverage,
- unpinned CI dependencies,
- build runner isolation coverage,
- short-lived publish credential coverage,
- policy bypass count,
- mean time to quarantine compromised digest,
- supplier evidence freshness,
- transitive dependency inventory coverage,
- orphan artifacts bez ownera.

Aggregate score bez asset criticality môže skrývať critical gap.

## 52. Governance

Organizácia potrebuje:

- approved source a registry platforms,
- repository baseline,
- CI/CD security standard,
- dependency policy,
- trusted builder inventory,
- signing a attestation policy,
- promotion model,
- supplier due diligence,
- exception process,
- incident playbook,
- evidence retention,
- ownership a escalation.

## 53. Troubleshooting

### Provenance ukazuje nesprávny commit

Over checkout behavior, merge commit, submodules, generated source, shallow clone a builder predicate.

### Digest sa po promotion zmenil

Artifact bol rebuildnutý, transformovaný alebo registry copy zmenila manifest. Porovnaj exact manifest a platform variant.

### Release workflow nemá OIDC token

Over event type, environment protection, token permission, audience a provider trust policy.

### Cache obsahuje cudzie files

Over cache namespace, key inputs, restore prefixes, branch trust a write authority.

### Package zmizol

Over registry retention, yanked/deleted version, mirror, internal cache a vendor strategy. Neobchádzaj integrity kontrolu náhodným alternate source.

## 54. Anti-patterny

- dôvera v mutable tag,
- shared publish token vo všetkých workflows,
- self-hosted runner pre untrusted PR aj production release,
- signature bez identity policy,
- provenance generovaná application build scriptom a vydávaná za independent evidence,
- lockfile bez controlled registry,
- build-time network access bez inventory,
- cache shared medzi trusted a untrusted jobs,
- rebuild per environment,
- Scorecard score ako automatické supplier approval,
- emergency bypass bez expiry a audit,
- odstránenie compromised release bez downstream advisory.

## 55. Mini príklad

```text
Git repository
→ protected main + two reviews
→ ephemeral hosted builder
→ dependencies podľa lockfile a digestov
→ image digest
→ platform-generated SLSA provenance
→ SBOM
→ keyless signature z protected release workflow
→ registry
→ admission policy overí issuer, workflow identity a digest
→ production
```

Negative tests:

- untrusted PR nedostane publish identity,
- mutable tag nie je prijatý ako production identity,
- provenance z neapproved buildera je odmietnutá,
- signature z iného repository workflowu je odmietnutá,
- artifact bez SBOM neprejde policy,
- registry copy zachová digest a evidence.

## 56. Kontrolné otázky

1. Ktoré systems môžu zmeniť výsledný artifact bez zmeny application source?
2. Ako sa líši source identity, branch, tag a revision?
3. Prečo signed commit nestačí na dôveru v release?
4. Ako dependency confusion využíva resolver precedence?
5. Aký je rozdiel medzi lockfile a digest pinning?
6. Prečo je build platform critical trust boundary?
7. Ako oddeliť untrusted PR test od release authority?
8. Čo poskytuje hermetic a reproducible build?
9. Čo je provenance a kto ju má generovať?
10. Ako fungujú SLSA Source a Build tracks?
11. Čo Build L3 rieši a čo nerieši?
12. Prečo TUF používa viac rolí a expirácie?
13. Ako overovať supplier evidence?
14. Ako vyzerá consumer verification workflow?
15. Ako reagovať na compromised upstream package?

## Glossary impact

Relevantné pojmy: software supply chain, producer, distributor, consumer, source revision, protected branch, source provenance, SLSA Source track, SLSA Build track, dependency confusion, typosquatting, namespace takeover, lockfile, digest pinning, build definition, build platform, hosted runner, self-hosted runner, ephemeral runner, CI workload identity, hermetic build, reproducible build, build provenance, attestation, in-toto, SLSA Build L1, SLSA Build L2, SLSA Build L3, immutable promotion, TUF, OpenSSF Scorecard, supplier due diligence, artifact quarantine a supply-chain incident response.

## Primárne zdroje

- [NIST SP 800-161 Rev. 1 — Cybersecurity Supply Chain Risk Management Practices](https://csrc.nist.gov/pubs/sp/800/161/r1/final)
- [NIST SP 800-218 — Secure Software Development Framework 1.1](https://csrc.nist.gov/pubs/sp/800/218/final)
- [NIST SP 800-218 Rev. 1 Initial Public Draft — SSDF 1.2](https://csrc.nist.gov/pubs/sp/800/218/r1/ipd)
- [SLSA Specification 1.2](https://slsa.dev/spec/v1.2/)
- [SLSA Build Track Basics](https://slsa.dev/spec/v1.2/build-track-basics)
- [SLSA Source Track Requirements](https://slsa.dev/spec/v1.2/source-requirements)
- [in-toto Specification](https://in-toto.io/in-toto-spec/)
- [The Update Framework Specification](https://theupdateframework.github.io/specification/latest/)
- [OpenSSF Scorecard](https://github.com/ossf/scorecard)
- [OpenSSF Scorecard Checks](https://github.com/ossf/scorecard/blob/main/docs/checks.md)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Threat modeling](threat-modeling.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: SBOM →](sbom.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
