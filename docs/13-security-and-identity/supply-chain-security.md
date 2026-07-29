# Supply-chain security

Software supply-chain security chráni dôveryhodnosť software-u od source revision cez dependency resolution, build, evidence, distribution a deployment až po runtime. Nejde iba o scanning open-source packages. Supply chain tvorí každý principal, credential, service, configuration a artifact, ktorý môže zmeniť výsledné bytes alebo rozhodnutie, čo sa smie spustiť.

Dominantný model je source-to-runtime trust lifecycle:

```text
release intent a trust policy
→ exact source revision a source-control evidence
→ resolved dependencies, actions a build definition
→ builder identity, isolation a execution generation
→ immutable artifact digest
→ provenance, SBOM, signatures a test evidence
→ registry publication a promotion
→ consumer policy decision
→ deployed digest a runtime inventory
→ continuous re-evaluation, revocation a recovery
```

Každý edge musí zachovať subject identity. Source review nemá hodnotu, ak consumer nevie preukázať, že nasadené bytes vznikli práve z tejto revision na akceptovanom builderi.

## 1. Tri otázky dôvery

Consumer potrebuje odpovedať:

1. **Čo presne spúšťame?** — immutable digest alebo content hash.
2. **Ako a z čoho to vzniklo?** — provenance, source revision, build definition, builder a resolved inputs.
3. **Prečo tomu dôverujeme?** — policy nad source controls, builder guarantees, signer authority, SBOM quality, vulnerability state a environment requirements.

```text
hash
→ content identity

signature
→ kto kontroloval signing credential pre signed subject

provenance
→ claim o source a build process-e

SBOM
→ claim o composition

policy
→ či sú tieto claims sufficient pre konkrétny environment
```

Existencia evidence nie je trust verdict.

## 2. Supply chain je graph

Reálny artifact má viac upstream inputs:

```text
application source ───────┐
base image ────────────────┤
language dependencies ────┤
build helper a compiler ──┼→ builder → image digest
CI actions/workflows ─────┤             ├─ provenance
runner image a cache ─────┘             ├─ SBOM
                                        └─ signature
```

Každý node a edge potrebuje ownera, immutable identity, update path, write authority, verification, compromise impact a recovery.

Pinned application source nepomôže, ak builder image používa mutable tag. Hardened builder nepomôže, ak deployment prijíma mutable image tag alebo alternate direct path.

## 3. Exact release subject

Supply-chain decision má byť viazaný na complete release subject:

- repository identity a commit SHA;
- branch/source-policy generation a approvals;
- build definition a reusable workflow revisions;
- resolved dependency a action digests;
- runner identity, builder image digest a isolation class;
- external parameters a environment;
- output OCI index/platform digest;
- provenance, SBOM a signature subjects;
- registry source/destination a promotion record;
- deployment policy revision;
- actual runtime platform digest a owner.

Named references ako branch, Git tag, action tag alebo image tag sú routing aids, nie immutable release identity.

## 4. Authorities a trust boundaries

Critical authorities zahŕňajú:

- source change a review authority;
- branch-rule a repository administration;
- dependency namespace a package-publish authority;
- workflow a reusable-action authority;
- runner image, cache a build-control-plane authority;
- registry write/delete/tag authority;
- signing a provenance issuance authority;
- promotion a production deployment authority;
- trust-root a policy administration.

Attacker nemusí meniť application source. Stačí mu zmeniť reusable workflow, poisoned cache, runner toolchain, package namespace, registry tag alebo admission exception.

## 5. Source controls

Source revision má byť discrete a auditovateľná. Protected branch môže presadzovať review, required checks, restricted push a zákaz force-push.

Control je účinný iba pre exact revision. Approval alebo check z predchádzajúceho diffu sa nesmie preniesť na zmenený commit.

Two-party review znižuje unilateral authority, ale nezaručuje benign source. Compromised reviewers alebo malicious approved change zostávajú residual risk.

Repository administrator je privileged supply-chain actor. Branch-rule bypass, webhook a history changes potrebujú JIT administration, phishing-resistant MFA, audit export a emergency recovery.

## 6. Dependency resolution

Manifest, registries, lockfile a resolver rules tvoria executable resolution policy:

```text
manifest constraints
+ registry mapping a priority
+ available package versions
+ platform qualifiers
+ lockfile a integrity data
→ resolved dependency graph
```

Controls zahŕňajú:

- integrity-checked lockfiles;
- scoped alebo reserved namespaces;
- explicit private/public registry mapping;
- dependency source allowlist;
- digest pinning, keď ecosystem podporuje;
- semantic diff a owner review;
- controlled update automation;
- monitoring maintainer a namespace changes.

Dependency confusion využíva ambiguity medzi private a public namespace-om. Typosquatting využíva podobný názov. Namespace takeover mení publisher authority bez zmeny dependency name-u.

Digest pinning poskytuje content identity, nie security alebo origin. Pinovaná malicious alebo vulnerable dependency zostáva malicious alebo vulnerable.

## 7. CI actions a workflow code

Third-party action alebo reusable workflow je executable dependency. Môže čítať checkout, environment, tokens a secrets jobu.

Reference má byť pinovaná na exact revision, typicky full commit SHA, a update musí prejsť review. Tag môže byť presunutý.

Permissions sa definujú per job. Build job obvykle nepotrebuje repository administration ani production cloud authority. Release job nemá spúšťať untrusted code a zároveň držať signing alebo publish capability.

Untrusted metadata sa prenáša ako data. Interpolácia PR title, branch name-u alebo issue body do shell source-u vytvára workflow injection boundary.

## 8. Runner a builder isolation

Runner vykonáva build code a má workspace, process, filesystem, network a credential boundary.

Persistent self-hosted runner môže preniesť:

- process alebo cron persistence;
- modified compiler a helper;
- poisoned workspace alebo host directory;
- stolen credentials;
- shared cache output;
- altered Docker daemon alebo socket state.

Protected release má používať fresh isolated execution generation. Ephemeral lifecycle znižuje cross-run persistence, ale stále treba dôverovať runner image-u, hypervisoru, control plane-u a dependency inputs.

SLSA Build L3 (v1.2) vyžaduje hardened build platform s isolation medzi runs a ochranou provenance signing materialu pred tenant-controlled build steps. Level nie je všeobecný security score software-u.

## 9. Hermeticity, reproducibility a cache

**Hermetic build** používa deklarované, kontrolované inputs a nemá ambientný network alebo host state. Zlepšuje vysvetliteľnosť outputu.

**Reproducible build** umožňuje nezávisle vytvoriť bit-identical alebo definovane equivalent output z rovnakých inputs. Poskytuje tamper-detection evidence.

Hermeticity nepreukazuje benign dependencies. Reproducibility nepreukazuje correctness source-u.

Cache je performance optimization, nie authority. Untrusted a protected contexts majú oddelené namespaces. Release má byť možné vytvoriť clean buildom bez cache a porovnať output.

## 10. Build-once-promote-many

Artifact dostane immutable digest. Testy, scanning, signing, promotion a deployment sa viažu na ten istý digest.

```text
build once
→ test exact digest
→ scan exact digest
→ attach provenance a SBOM
→ sign exact digest
→ promote same digest
→ deploy same digest
```

Rebuild pre production ruší väzbu na staging evidence, aj keď source revision ostáva rovnaká. Dependency alebo runner generation sa mohla zmeniť.

Promotion musí potvrdiť destination digest a preniesť related signatures, provenance a SBOM artifacts.

## 11. Provenance a SLSA

Provenance je authenticated claim o tom, kde, kedy a ako subject vznikol. Consumer hodnotí:

- subject digest;
- builder identity;
- build type;
- source repository a revision;
- external parameters;
- resolved dependencies podľa available modelu;
- completeness a reproducibility claims;
- issuer a signature authority.

Provenance môže byť pravdivá a stále opisovať unsafe process. `Builder=untrusted-shell-runner` nie je bezpečný len preto, že claim je podpísaný.

SLSA 1.2 je current approved specification a oddeľuje Build a Source tracks. Build levels opisujú rastúce guarantees o provenance a builderi. Source levels opisujú vlastnosti vzniku source revision vrátane technicky presadzovaných controls a two-party review.

Source a Build tracks sa dopĺňajú:

```text
trusted source + compromised builder
→ nedôveryhodný artifact

malicious source + hardened builder
→ dôveryhodne vytvorený malicious artifact
```

## 12. in-toto, attestations a evidence semantics

Attestation je signed claim o subjecte. Predicate schema určuje, čo claim znamená.

in-toto model môže definovať expected steps a authorized actors a porovnať actual materials/products evidence s layoutom.

Rozlišuj:

- signature — binding identity/keyu k subjectu alebo payloadu;
- attestation — authenticated statement;
- provenance — build/source process claim;
- SBOM — composition claim;
- VEX — vulnerability-status claim;
- test attestation — claim o konkrétnom test execution subjecte.

Policy musí kontrolovať issuer, subject, predicate type, schema a claim values. `Má attestation` nie je sufficient rule.

## 13. Registry a update distribution

Registry alebo package repository je distributor a release authority boundary. Write permission k namespace-u môže obísť source controls, ak consumer akceptuje každý upload.

Controls zahŕňajú:

- digest addressing;
- release tag immutability;
- scoped short-lived publish credentials;
- deletion a overwrite protection;
- audit a retention;
- related-artifact/referrers preservation;
- replication read-back;
- continuous provenance/signature verification.

TUF používa signed Root, Targets, Snapshot a Timestamp metadata s role separation, versions a expiry na ochranu update distribution proti rollback, freeze a mix-and-match attacks. Nechráni correctness source-u alebo buildera.

## 14. Deployment policy

Consumer policy má rozhodovať na final deployment boundary. CI gate je early feedback, ale manual alebo alternate controller path ho môže obísť.

Production rule môže vyžadovať:

```text
immutable digest
+ approved signer identity
+ approved provenance issuer
+ approved builder and source repository
+ expected source revision policy
+ final-artifact SBOM with sufficient completeness
+ vulnerability/exception policy
+ promotion record
→ admit
```

Mutation ordering je dôležitý. Ak webhook zmení image po verification, final object musí byť znovu validovaný.

## 15. Runtime inventory a re-evaluation

Immutable artifact sa nemení, ale jeho trust status áno. Nová CVE, compromised builder, revoked signer alebo malicious dependency disclosure môže spätne ovplyvniť staré digests.

Runtime inventory mapuje:

```text
digest
→ platform variant
→ workload a environment
→ owner
→ rollback a autoscaling paths
```

Policy revocation musí vedieť zablokovať nové deployments, quarantine-nuť running artifacts podľa risku a merať propagation latency.

## 16. Worked incident `SEC-PAY-50`

Atlas Payments release `7.24.0` použil approved source revision `a81f2e9`. Branch protection, two-party review a application tests boli green.

Release job však bežal na persistentnom `runner-prod-17` z mutable builder tagu, ktorý sa resolve-nul na `sha256:builder17`. Builder obsahoval vulnerable `atlas-build-helper 2.4.1`. Crafted PR title bol v release-note step-e interpretovaný ako shell command a final image `sha256:pay7240` získal injected `settlement-debug.jar` po application testoch.

Pipeline vytvorila:

- release signature pre `sha256:pay7240`;
- provenance s matching subject digestom;
- SBOM pripojenú k digestu;
- green promotion a admission result.

### Prečo green controls nestačili

- signature preukázala, že release credential podpísal malicious digest;
- provenance vytvoril tenant-controlled job na compromised runneri;
- provenance policy nekontrolovala builder isolation ani builder image;
- SBOM vznikla zo source lockfile-u pred final packagingom;
- admission kontrolovalo iba existenciu predicate types;
- runtime používal digest, ale digest identifikoval nedôveryhodné bytes presne.

Digest pinning zabránilo nepozorovanej substitution po publish-i. Nezabránilo compromised builderu vytvoriť malicious digest.

## 17. Competing hypotheses a evidence

1. **Source compromise** — source revision alebo approval history boli zmenené.
2. **Dependency substitution** — resolver stiahol malicious package.
3. **Builder tampering** — persistent runner alebo toolchain zmenili output.
4. **Registry substitution** — artifact bol nahradený po build-e.
5. **Policy/subject mismatch** — evidence patrila inému digestu.

Discriminating evidence:

- source history a approvals zodpovedali `a81f2e9`;
- lockfile a dependency mirror digests sedeli;
- clean rebuild na fresh builderi injected JAR nevytvoril;
- runner process audit ukázal helper child shell;
- registry digest od publish-u zostal rovnaký;
- signature, provenance a SBOM subjects sedeli na `sha256:pay7240`;
- provenance issuer a SBOM generation method však nespĺňali intended trust contract.

Root cause bol compromised build execution path. Existence-only evidence policy a persistent runner boli primary control defects.

## 18. Evidence-preserving containment

- zastaviť affected build, provenance, signing a publish authorities;
- preserve-nuť source, workflow, runner disk, process, cache, network, registry a policy audit;
- quarantine-nuť builder digest, runner a všetky outputs z exposure intervalu;
- deny-nuť nové deployments `sha256:pay7240` a odstrániť ho z rollback catalogu;
- rotate-nuť credentials dostupné affected jobs;
- udržať service na last-known-good trusted digest-e;
- nezmazať registry evidence pred complete enumeration artifacts a referrers.

## 19. Authoritative recovery

1. obnoviť source a workflow z trusted revision;
2. vytvoriť pinned fixed builder image;
3. prejsť na fresh ephemeral isolated runner;
4. oddeliť provenance/signing service od tenant steps;
5. rebuildnúť exact source s pinned declared inputs;
6. vytvoriť final-artifact SBOM a independent binary diff;
7. publikovať nový digest, provenance, SBOM a signature;
8. overiť destination registry referrers po promotion;
9. nasadiť cez semantic admission policy;
10. odstrániť old digests, credentials a bypass paths;
11. re-evaluovať všetky artifacts z compromise intervalu;
12. vykonať second clean rebuild a deployment test.

Re-signing `sha256:pay7240` novým keyom by iba dalo nový podpis starým nedôveryhodným bytes.

## 20. Acceptance verdict

Supply-chain incident je uzavretý, keď:

- approved source revision a build definition sú explicitne viazané na nový digest;
- builder je pinned, fixed, fresh a izolovaný;
- untrusted metadata nemôžu ovplyvniť command graph;
- provenance vydáva approved platform identity mimo tenant steps;
- final-artifact SBOM obsahuje injected-content test fixture, ak sa fixture legitímne pridá;
- policy odmietne self-generated provenance, source-only SBOM a wrong builder;
- promotion zachová všetky required referrers;
- old artifact a builder digests sú denied vo všetkých deployment paths;
- runtime a rollback inventory obsahujú iba trusted generation;
- second independent rebuild vytvorí expected equivalent output;
- oprávnený settlement flow funguje a injected debug path zlyhá.

## 21. Supplier a open-source governance

Supplier evidence môže zahŕňať secure development process, vulnerability disclosure, SBOM/VEX, provenance, signing, incident notification a support lifecycle.

OpenSSF Scorecard je signal, nie trust verdict. High score nezaručuje benign package. Risk-tiered assessment zohľadňuje maintainer model, release process, project criticality, responsiveness a transitive reach.

Infrastructure modules, Helm charts, Ansible collections, policies, model weights a datasets sú tiež executable alebo behavior-determining supply-chain artifacts a potrebujú rovnakú identity, provenance a update governance.

## 22. Earlier controls

- source a build tracks hodnotené oddelene;
- exact revisions pre source, actions, workflows a builder images;
- minimal job permissions a no secrets for untrusted code;
- ephemeral isolated runners a adversarial isolation tests;
- untrusted/protected cache separation;
- build-once-promote-many;
- platform-generated digest-bound provenance;
- final-artifact a platform-specific SBOMs;
- semantic policy nad claim values, nie evidence existence;
- registry promotion read-back a referrers preservation;
- runtime digest inventory a authority-revocation drills;
- last-known-good source-to-runtime recovery chain.

## 23. Anti-patterny

### Scan source, trust binary

Neexistuje binding medzi reviewed source a deployed bytes.

### Pin tag, nie revision alebo digest

Named reference sa môže presunúť.

### Untrusted code so signing permission

Contribution získa release authority.

### Persistent shared runner

Jeden job ovplyvní budúci protected release.

### Provenance existence gate

Policy nehodnotí issuer, builder, source ani parameters.

### Build twice

Production artifact nie je ten, ktorý prešiel testami.

### Signature ako bezpečnostná známka

Signer môže oprávnene podpísať compromised output.

## 24. Kontrolné otázky

1. Prečo je supply chain graph?
2. Čo tvorí exact release subject?
3. Ako sa source revision líši od named reference?
4. Aké authority paths môžu obísť source review?
5. Ako dependency confusion využíva resolver policy?
6. Prečo action tag nie je immutable trust identity?
7. Ako persistent runner prenáša compromise medzi jobs?
8. Ako sa hermetic a reproducible build líšia?
9. Čo SLSA Build a Source tracks dokazujú a čo nie?
10. Prečo validná provenance môže opisovať unsafe process?
11. Ako sa signature, provenance, SBOM a VEX líšia?
12. Čo musí overiť supply-chain acceptance verdict?

## Glossary impact

Relevantné pojmy: release trust subject, source-to-runtime trust lifecycle, supply-chain authority, resolved-input generation, builder execution generation, protected build boundary, evidence semantics, provenance authority, semantic evidence policy, promotion preservation verdict, runtime trust re-evaluation, authority compromise interval, last-known-good chain a supply-chain acceptance verdict.

## Primárne zdroje

- [SLSA Specification 1.2](https://slsa.dev/spec/v1.2/)
- [SLSA Build Track Basics](https://slsa.dev/spec/v1.2/build-track-basics)
- [SLSA Source Track Requirements](https://slsa.dev/spec/v1.2/source-requirements)
- [SLSA Provenance](https://slsa.dev/spec/v1.2/provenance)
- [in-toto Specifications](https://in-toto.io/docs/specs/)
- [The Update Framework Overview](https://theupdateframework.io/docs/overview/)
- [GitHub Actions Secure Use Reference](https://docs.github.com/en/actions/reference/security/secure-use)
- [OpenSSF Scorecard](https://securityscorecards.dev/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Threat modeling](threat-modeling.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: SBOM →](sbom.md)
<!-- KNOWLEDGE-NAVIGATION:END -->