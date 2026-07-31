# Supply-chain security

Software supply-chain security chráni dôveryhodnosť software-u od source revision cez dependency resolution, build, evidence, distribution a deployment až po runtime. Nejde iba o scanning open-source packages. Supply chain tvorí každý principal, credential, service, configuration a artifact, ktorý môže zmeniť výsledné bytes alebo rozhodnutie, čo sa smie spustiť.

Podpísaný artifact môže byť malicious, ak signer autorizoval compromised builder output. Reproducible build môže deterministicky reprodukovať malicious source. SBOM môže byť validne podpísaná a pritom inventarizovať nesprávny lifecycle stage. Supply-chain assurance preto spája immutable subject, evidence authority, semantic policy a runtime read-back.

## Source-to-runtime trust lifecycle

Supply-chain assurance vzniká iba vtedy, keď sa source, builder, evidence authority, artifact graph a runtime digest dajú spojiť jedným immutable subjectom. Lifecycle oddeľuje tieto trust transitions, aby podpis alebo provenance nemohli zakryť compromised builder.

```text
release intent a trust policy
→ exact source revision a source controls
→ resolved dependencies, actions a toolchain
→ builder identity, isolation a execution generation
→ immutable artifact digest a platform graph
→ provenance, SBOM, signatures a test evidence
→ registry publication a promotion
→ semantic consumer policy
→ selected platform/runtime digest
→ continuous re-evaluation, revocation a recovery
```

Každá boundary môže zmeniť trust. Protected branch nepreukazuje builder integrity. Build success nepreukazuje publication. Registry tag nepreukazuje digest. Admission allow nepreukazuje, že runtime vybral signed platform manifest.

## Exact release subject SEC-PAY-50

Release subject pomenúva source, build definition, dependency graph, builder, index, platform manifests, evidence authority a runtime. Bez neho by tag alebo source revision neumožnili quarantine všetkých outputs z compromised execution window.

```yaml
release: payments-7.24.0
sourceRepository: Marvy936/atlas-payments
sourceRevision: a81f2e9
buildDefinition: .github/workflows/release.yml@sha256:workflow44
resolvedDependencies: deps-lock-884
builderImage: sha256:builder17
runner: runner-prod-17
artifactIndex: sha256:pay7240
platforms:
  linux-amd64: sha256:pay7240-amd
  linux-arm64: sha256:pay7240-arm
provenanceAuthority: tenant-controlled-job
sbomMethod: source-lockfile-only
signatureSubject: sha256:pay7240
runtimeDigest: sha256:pay7240-arm
incident: SEC-PAY-50
```

Subject oddeľuje source, builder, index, platform manifest a runtime. „Image pay:7.24.0“ by neumožnila presnú investigation ani revocation.

## Source controls a review continuity

Source trust zahŕňa repository identity, protected refs, required reviews/checks, signed or attributable changes, merge queue, admin bypass a emergency workflow. Two-party review je účinný iba vtedy, keď reviewed diff je presne to, čo build konzumuje. Mutable branch alebo generated source po review môže prerušiť control continuity.

Untrusted pull request nesmie získať production secrets, signing authority ani write access k protected registry. Workflow running in target repository context môže byť privileged aj pri contribution z fork-u; trigger a checkout semantics musia byť explicitné. PR title, branch name, commit message a artifact metadata sú untrusted inputs rovnako ako files.

## Dependency resolution

Lockfile, checksum a pinned digest znižujú ambiguity, ale dependency resolver stále používa registry, namespace, platform a transitive graph. Dependency confusion vzniká, keď internal name možno resolve-nuť z public registry. Typosquatting využíva podobný názov; namespace takeover mení trust po expiracii accountu alebo domain-u.

Dependencies, CI actions, base images, compilers, package managers a installer scripts sa pinujú immutable references. Version range alebo Git tag je mutable intent. Mirror/proxy policy má kontrolovať upstream identity, integrity metadata, quarantine a retention. Offline cache bez provenance môže konzervovať compromised package dlhšie než upstream.

## Builder a runner trust

Builder je security principal a execution environment, nie iba command. Trusted build potrebuje pinned builder/toolchain, isolated worker, bounded network a filesystem, controlled secrets, clean state a platform-generated identity. Persistent self-hosted runner môže preniesť malware, modified toolchain, credentials alebo cache medzi jobs.

Ephemeral runner znamená, že worker state sa po jednom jobe zahodí. Neznamená automaticky hermetic build: network môže stále sťahovať mutable dependencies a privileged job môže kompromitovať control plane. Hosted runner redukuje niektoré operations risks, ale trust sa presúva na provider a image generation.

Untrusted test a trusted release build majú oddelené authority. PR môže spustiť tests bez registry/signing credentials. Release job po approved merge používa fresh worker a immutable source. Signing/provenance generuje platform boundary mimo tenant-controlled shell steps.

## Hermetic a reproducible builds

Hermetic build deklaruje všetky inputs a nepoužíva undeclared network/host state. Reproducible build umožní nezávisle vytvoriť rovnaký alebo semantically equivalent output. Hermeticity zlepšuje explainability; reproducibility zvyšuje confidence, ale ani jedno nepreukazuje benign source alebo compiler.

Bit-for-bit reproducibility môže byť nepraktická pre timestamps alebo signatures. Tím definuje normalizované porovnanie a vysvetlí allowed differences. „Second build differs“ je finding, nie automatický compromise verdict; „second build matches“ je evidence, nie absolútny proof.

## Provenance ako claim od authority

Provenance viaže artifact digest na source, build definition, builder identity, parameters a materials. Hodnota závisí od authority, ktorá evidence vytvorila. Ak tenant-controlled step po compromise vygeneruje vlastnú provenance, matching digest iba potvrdzuje, že compromised job opísal svoj malicious output.

Verification example:

```bash
cosign verify-attestation \
  --type slsaprovenance \
  --certificate-identity-regexp '^https://github.com/Marvy936/atlas-payments/.github/workflows/release.yml@refs/heads/main$' \
  --certificate-oidc-issuer 'https://token.actions.githubusercontent.com' \
  registry.atlas.example/payments@sha256:pay7240
```

Výstup preukazuje validnú attestation matching subject a certificate identity podľa verifier policy. Nepreukazuje approved builder isolation, complete materials, correct parameters, final platform selection ani benign source. Predicate sa musí semantic-ky skontrolovať, nie iba overiť signature.

```bash
cosign download attestation \
  registry.atlas.example/payments@sha256:pay7240 \
  | jq -r '.payload' \
  | base64 -d \
  | jq '{subject, predicateType, builder: .predicate.builder, buildType: .predicate.buildType, invocation: .predicate.invocation, materials: .predicate.materials}'
```

Read-back ukáže claims v attestation. Nepreukazuje ich pravdivosť mimo dôvery k issuerovi/builder authority a independent controls.

## SLSA a assurance levels

SLSA poskytuje Source a Build tracks a konkrétne requirements pre source integrity, build platform a provenance. Level nie je všeobecná certifikácia produktu ani záruka absence vulnerabilities. Tím mapuje, ktoré threats daný level redukuje a ktoré zostávajú, napríklad malicious approved source alebo vulnerable runtime dependency.

## Registry, promotion a referrers

Registry uchováva manifests, layers a related artifacts. Tag je mutable pointer; digest je immutable content identity. Multi-platform index odkazuje na platform manifests, ktoré majú vlastné digests. Promotion má kopírovať exact digest graph a zachovať signatures, provenance a SBOM referrers.

Unknown publication outcome po timeout-e sa rieši registry read-backom. Blind push pod rovnakým tagom môže zmeniť subject. Garbage collection a retention nesmú odstrániť evidence alebo rollback artifact pred policy windowom.

## Semantic consumer policy

Consumer policy nekontroluje iba existenciu signature. Overuje subject digest, authorized signer/workflow, provenance authority, source repo/ref, builder, build type, materials, platform-specific SBOM, vulnerability/risk policy a exception generation. Policy input musí obsahovať final resolved runtime digest.

Admission na tagu alebo repository-level signature môže povoliť unsigned arm64 manifest, ak verifier nájde validnú amd64 signature niekde v rovnakom repository. Runtime read-back je preto posledný trust step.

## TUF a secure updates

The Update Framework oddeľuje root, targets, snapshot a timestamp roles, chráni proti rollback, freeze, mix-and-match a key compromise cez threshold/signing/expiry model. TUF rieši update metadata a client freshness; nenahrádza build provenance ani artifact vulnerability assessment.

## Supplier due diligence

Supplier evidence zahŕňa ownership, release practices, security response, maintainer risk, provenance, signing, dependency health a incident history. OpenSSF Scorecard môže signalizovať project practices, ale nie je certifikácia ani proof bezpečnosti. Critical dependency potrebuje contingency, mirror/retention a replacement plan.

## Incident SEC-PAY-50

Approved source revision `a81f2e9` bol čistý. Vulnerable helper na persistentnom privileged runneri interpretoval crafted PR title ako shell a po tests vložil `settlement-debug.jar` do final image. Tenant job potom publikoval digest, vygeneroval matching provenance a podpísal artifact. Source SCA a source-lockfile SBOM zostali green.

Root cause bol compromised builder trust domain a evidence authority. Source controls, signature a provenance existovali, ale neboli nezávislé od compromised execution. Admission kontrolovalo prítomnosť artifacts, nie semantic subject/builder/method.

## Containment a authoritative recovery

Containment quarantinuje runner, builder, credentials a všetky outputs z exposure interval-u. Registry policy zablokuje affected index/platform digests aj rollback refs. Evidence sa zachová pred reimage.

Recovery používa pinned fixed helper, fresh ephemeral worker, immutable source, isolated publish authority, platform-generated provenance, final-artifact SBOM a semantic admission. New digest sa rebuildne a deployne; old artifacts, caches, tags a rollback paths sa retire-nú. Signer credentials sa rotujú podľa exposure.

Acceptance vyžaduje trusted provenance authority, exact source/build/builder claims, platform-specific evidence, absence injected file-u, running approved digest a deny old/wrong-platform artifactu. Adversarial PR metadata nesmie spustiť command. Druhý independent build musí prejsť defined reproducibility/semantic comparison.

## Kontrolné otázky

1. Prečo protected branch nepreukazuje builder integrity?
2. Ako sa hermetic a reproducible build líšia?
3. Prečo matching provenance od compromised jobu nie je dôveryhodná?
4. Aký rozdiel je medzi image indexom a platform manifestom?
5. Čo semantic admission kontroluje navyše oproti existencii signature?
6. Ktoré threats rieši TUF a ktoré nie?
7. Prečo runner quarantine zahŕňa všetky outputs z exposure intervalu?

## Referencie

- [SLSA specification](https://slsa.dev/spec/)
- [The Update Framework](https://theupdateframework.io/)
- [Sigstore Cosign](https://docs.sigstore.dev/cosign/)
- [OpenSSF Scorecard](https://scorecard.dev/)
- [NIST Secure Software Development Framework](https://csrc.nist.gov/publications/detail/sp/800-218/final)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Threat modeling](threat-modeling.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: SBOM →](sbom.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
