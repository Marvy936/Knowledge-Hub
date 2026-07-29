# Image signing

Image signing cryptographically viaže konkrétny OCI subject na signing key alebo overenú signing identity. Production control však nevznikne tým, že príkaz vypíše `Verified OK`. Consumer musí preukázať, že overený podpis patrí presne tomu digestu, ktorý sa má spustiť, signer bol oprávnený pre daný product a environment, required attestations opisujú ten istý subject a všetky deployment paths výsledok skutočne presadzujú.

Dominantný model kapitoly je **subject-to-runtime trust lifecycle**:

```text
release intent a exact OCI subject
→ signing authority a issuance context
→ signature alebo attestation
→ trust-root, certificate a time evidence
→ signer a subject authorization
→ registry publication a promotion
→ policy decision na final deployment boundary
→ resolved runtime digest
→ re-evaluation, quarantine a revocation
→ allowed aj forbidden second-release validation
```

Podpis je jeden dôkaz v tomto lifecycle-e. Neopraví compromised source, builder ani nesprávny policy input.

## 1. Exact signing subject

Pred podpisom treba identifikovať:

- repository a release unit;
- OCI image index alebo platform manifest digest;
- architecture a OS variant;
- source revision a builder generation;
- signer purpose a environment;
- required provenance, SBOM a approval evidence;
- registry namespace a promotion path;
- policy revision a enforcement points;
- runtime a rollback scope.

Tag, filename ani marketingová verzia nie sú immutable subject. Subjectom je descriptor digest konkrétnych serialized bytes.

```text
registry.atlas.example/payments:7.24.0
→ mutable reference

registry.atlas.example/payments@sha256:pay7240
→ exact image-index subject
```

## 2. OCI graph a multi-platform contract

OCI image index odkazuje na platform manifests; manifests odkazujú na config a layers.

```text
index sha256:pay7240
├─ linux/amd64 manifest sha256:pay7240-amd
└─ linux/arm64 manifest sha256:pay7240-arm
```

Podpis indexu schvaľuje exact set descriptors. Podpis iba amd64 manifestu nehovorí nič o arm64 variante. Production contract musí preto explicitne určiť:

- či sa podpisuje index, každý manifest alebo obe vrstvy;
- ktoré platforms sú povolené;
- či každá platform potrebuje vlastnú provenance a SBOM;
- ako admission zistí platform digest, ktorý runtime reálne použije;
- čo sa stane pri pridaní novej platformy.

## 3. Čo signature dokazuje

Pri správnej verification signature dokazuje:

1. signed payload nebol po podpise zmenený;
2. podpis vytvoril držiteľ príslušného private keyu alebo ephemeral keyu viazaného na certificate;
3. payload obsahuje deklarovaný subject.

Signature sama nedokazuje:

- correctness alebo review source-u;
- isolation buildera;
- absence malware-u alebo vulnerabilities;
- pravdivosť attestation predicate-u;
- oprávnenie signer-a pre konkrétny repository, workflow alebo environment;
- zhodu signed subjectu s deployed digestom;
- úplnosť multi-platform release-u.

```text
cryptographic validity
≠ signer authorization
≠ evidence semantics
≠ deployment eligibility
```

## 4. Signing authority

Signing authority je capability vytvoriť evidence, ktorému consumer môže dôverovať. Môže byť reprezentovaná:

- long-lived private keyom;
- KMS alebo HSM `Sign` permission;
- short-lived keyless OIDC identity;
- release approval workflowom;
- environment-specific promotion authority.

Builder identity a release authority nemusia byť rovnaké. Builder môže vydať provenance „tento output som vytvoril“, zatiaľ čo protected release workflow vydá samostatný approval „tento digest smie do production“.

Authority musí byť scoped podľa productu, repository, workflowu, branch/tagu, environmentu a purpose-u. Shared signer pre všetky products zväčšuje blast radius a zhoršuje attribution.

## 5. Key-based signing

Pri key-based modeli organization spravuje asymmetric key pair. Private key potrebuje celý lifecycle:

```text
generation
→ storage alebo non-exportable custody
→ authorization
→ signing
→ public-key distribution
→ rotation
→ revocation
→ archival alebo destruction
```

KMS/HSM znižuje extraction risk, ale nezabráni oprávnenému compromised workflowu volať `Sign` nad malicious digestom. KMS policy preto musí chrániť caller identity, purpose aj operation scope.

## 6. Keyless Sigstore model

Keyless signing nepoužíva permanentný user-managed signing key. Ephemeral cryptographic key však stále existuje.

```text
CI workload získa OIDC token
→ vytvorí ephemeral key pair
→ Fulcio overí identity a vydá short-lived certificate
→ workload podpíše subject
→ signature a transparency/time evidence sa publikujú
→ private ephemeral key sa zahodí
```

Trust sa presúva na:

- OIDC issuer a presné claims;
- Fulcio trust chain;
- Rekor alebo bundle evidence;
- trusted-root distribution;
- identity authorization policy;
- correctness release workflowu.

Dôvera v celý OIDC issuer je príliš široká. Policy musí obmedziť exact repository, workflow identity, ref alebo protected environment a event context.

## 7. Fulcio, Rekor, bundle a TUF

Fulcio vydáva short-lived code-signing certificates viazané na overenú identity. Rekor poskytuje append-only transparency evidence a inclusion proof. Transparency log zlepšuje audit a detection; nezabráni oprávnenému workflowu podpísať zlý artifact.

Verification bundle môže niesť signature, certificate, chain a log/timestamp evidence pre neskoršiu alebo offline verification. Bundle nie je self-authenticating: consumer stále potrebuje správne trusted roots a policy.

Sigstore trust material sa distribuuje a rotuje cez TUF model. Root bootstrap, expiry, version a emergency rotation sú samostatné security boundaries.

## 8. Signature oproti attestation

**Signature** cryptographically viaže identity na payload alebo subject. **Attestation** je signed claim so subjectom a predicate type-om.

```text
signature
→ kto podpísal subject

provenance attestation
→ ako subject vznikol

SBOM attestation
→ čo subject obsahuje

release approval
→ prečo subject smie postúpiť
```

in-toto Statement a DSSE oddeľujú subject, predicate a signing envelope. Consumer musí validovať signature aj predicate schema a význam claimov. Validne podpísaná nepravdivá alebo neúplná SBOM zostáva zlým evidence.

## 9. OCI subject a Referrers

Signature, provenance a SBOM môžu byť publikované ako related OCI artifacts s `subject` descriptorom smerujúcim na image digest. Referrers API umožní tieto artifacts objaviť.

```text
sha256:pay7240
├─ release signature
├─ provenance attestation
└─ SBOM attestation
```

Referrers sú discoverability mechanism, nie trust decision. Registry writer môže pridať vlastný referrer; každý related artifact sa musí cryptographically aj semantically overiť.

Promotion musí preniesť image aj required referrers a následne vykonať destination read-back. Copy iba manifestu a layers môže v production stratiť evidence.

## 10. Signer authorization generation

Cryptographic verifier odpovedá, či signature sedí. Authorization policy odpovedá, či signer smel podpísať tento subject.

Exact keyless policy typicky kontroluje:

- certificate issuer;
- subject/SAN identity;
- organization a repository;
- workflow path a reusable workflow;
- protected ref alebo environment;
- event type a audience;
- subject digest;
- required predicate types a authorities;
- quarantine generation.

Regex musí byť anchored a testovaný proti podobným attacker-controlled names. `.*payments.*` nie je identity contract.

## 11. Promotion a time-of-check/time-of-use

Build-once-promote-many zachováva rovnaký digest medzi staging a production. Rebuild alebo manifest rewrite vytvorí nový subject a pôvodné signatures už nemusia platiť.

Deployment má používať digest:

```yaml
image: registry.atlas.example/payments@sha256:pay7240
```

Ak admission overí tag a runtime tag neskôr znovu resolve-ne, vznikne time-of-check/time-of-use gap. Verification cache musí byť viazaná minimálne na digest, signer-policy revision, required evidence set, result time a quarantine generation.

## 12. Admission a runtime enforcement

Kubernetes admission alebo deployment controller môže byť Policy Enforcement Point. Musí:

1. zachytiť všetky relevantné API paths;
2. získať alebo uložiť final resolved digest;
3. overiť signature a exact subject;
4. vyhodnotiť signer a attestation policy;
5. validovať final object po mutation;
6. zapísať decision s policy revision;
7. doplniť background/runtime re-evaluation.

Scope zahŕňa containers, init containers, ephemeral containers a custom workload CRDs. Admission nechráni direct node runtime, external orchestrator ani už running workload po neskoršej revocation.

## 13. Worked incident `SEC-PAY-51`

Release `7.24.0` z predchádzajúceho incidentu mal:

```text
index:  sha256:pay7240
amd64:  sha256:pay7240-amd
arm64:  sha256:pay7240-arm
bundle: SIG-PAY-7240-A
```

Protected release job získal keyless certificate pre:

```text
issuer  = https://token.actions.githubusercontent.com
subject = https://github.com/atlas/payments/.github/workflows/release.yml@refs/heads/main
```

Job omylom podpísal iba `sha256:pay7240-amd`. Arm64 variant obsahovala injected `settlement-debug.jar` z compromised builder pathu `SEC-PAY-50`.

Production verifier:

- resolve-nul tag na index `sha256:pay7240`;
- našiel platnú signature v rovnakom registry repository;
- neoveril, že signature subject je index alebo selected arm64 manifest;
- cache-oval allow podľa `repository:tag`;
- povolil rollout na arm64 nodes.

Cryptography fungovala. Root cause bol **subject misbinding a neúplný multi-platform signing contract**. Broad signer regex, repository-level evidence lookup a tag-based cache boli amplifiers.

## 14. Discriminating evidence

Kauzálny walkthrough:

1. production Pods bežali na arm64 nodes;
2. kubelet resolved digest bol `sha256:pay7240-arm`;
3. bundle payload uvádzal `sha256:pay7240-amd`;
4. certificate chain, OIDC issuer a signature boli validné;
5. pre index ani arm64 manifest neexistovala accepted signature;
6. admission decision log neobsahoval signed-subject digest;
7. cache key obsahoval tag, nie digest;
8. nový tag resolve po quarantine stále dostal cached allow.

Tým sa vylúčili hypotézy o broken signature algorithm-e alebo registry layer corruption. Failure vznikol medzi validnou signature a nesprávnym authorization/enforcement bindingom.

## 15. Containment a recovery

Evidence-preserving containment:

- freeze signing a promotion workflow;
- preserve OIDC token claims, Fulcio certificate, bundle, transparency proof, registry manifests a admission logs;
- quarantine index aj obe platform manifests;
- zablokovať nové deployments bez mazania forensic artifacts;
- identifikovať všetky runtime a rollback references.

Authoritative recovery:

1. opraviť a znovu vybudovať release z trusted buildera;
2. vytvoriť nový index a platform digests;
3. podpísať exact index a podľa policy aj jednotlivé manifests;
4. vydať platform-specific provenance a SBOM;
5. zaviesť exact signer a subject authorization;
6. invalidovať tag-based verification cache;
7. zachovať referrers pri promotion a vykonať read-back;
8. rolloutovať nový digest a odstrániť old digest z runtime a rollback catalogu;
9. overiť, že old workflow alebo subject už neprejde.

Re-signing `sha256:pay7240-arm` novým keyom by compromised content iba znovu schválilo; nie je to recovery.

## 16. Rotation, revocation a quarantine

Routine rotation pridáva novú signing authority s bounded overlapom a potom odstráni starú. Compromise response potrebuje exposure interval a presnejší scope:

```text
compromised key alebo workflow
→ zastaviť nové issuance/signing
→ enumerovať signatures a subjects v intervale
→ quarantine affected digests
→ aktualizovať trust a policy generations
→ rebuildnúť trusted artifacts
→ overiť rejection old identity a artifacts
```

Historical signature môže zostať immutable. Quarantine je policy state viazaný na digest, reason, scope, owner a recovery condition. Enforcement latency od decisionu po všetky PEPs je merateľná security property.

## 17. Failure semantics

Verification závisí od registry, trust roots, bundles, policy data a evaluatorov. Production model má explicitne rozhodnúť:

- ktoré dependencies sú potrebné request-time;
- čo možno bezpečne cache-ovať;
- kedy sa deployment fail-closed;
- ako funguje oddelený break-glass pre known-good digest;
- ako sa deferred decisions po outage znovu vyhodnotia.

Global `allow unsigned on timeout` mení availability incident na supply-chain bypass.

## 18. Signature acceptance verdict

Release je akceptovaný až keď:

- deployment používa exact digest;
- signature subject sa zhoduje s indexom alebo selected platform manifestom podľa contractu;
- issuer a signer identity sú exact a authorized;
- bundle/trust-root/time evidence sú validné;
- required provenance a SBOM patria rovnakému subjectu;
- promotion zachovala referrers;
- active policy revision výsledok presadila na každom path-e;
- resolved runtime digest sa zhoduje s accepted subjectom;
- quarantine a old-identity updates sa prejavili v bounded čase;
- validná signature na wrong subjecte, unsigned platform a old digest sú odmietnuté;
- druhý čistý release aj rollback test prejdú.

## 19. Troubleshooting flow

```text
requested image reference
→ tag-to-digest resolution
→ index a selected platform manifest
→ discovered signature/attestation subjects
→ signature payload a certificate chain
→ OIDC issuer a signer claims
→ bundle/transparency/time evidence
→ required predicate schemas a authorities
→ active policy revision a cache key
→ final stored object
→ runtime resolved digest
→ quarantine/revocation state
```

`Verified` bez subject comparison je neúplná diagnostika. Pri multi-arch failure vždy porovnaj index, platform a runtime digests.

## 20. Earlier controls

- build-once-promote-many s digest read-backom;
- explicitný index/platform signing contract;
- keyless identity scoped na exact workflow a environment;
- non-exportable key custody pre key-based signing;
- platform-generated provenance mimo tenant steps;
- digest-bound platform SBOMs;
- semantic verification policy;
- referrer-preserving promotion test;
- digest a quarantine-aware cache;
- runtime digest inventory;
- wrong-subject, wrong-signer a unsigned-platform negative fixtures;
- revocation a second-release rehearsal.

## 21. Anti-patterny

### Podpisujeme tag

Tag je mutable reference; decision musí patriť resolved digestu.

### Ľubovoľná validná signature stačí

Cryptographic validity sa zamieňa za signer a subject authorization.

### Podpis jednej platformy schvaľuje index

Unsigned alebo odlišná platform variant zostáva mimo evidence.

### Transparency log je preventive control

Log poskytuje evidence, nie oprávnenie.

### Re-signing bez rebuild-u

Nový podpis nemení compromised bytes.

### Admission bez runtime inventory

Later quarantine nevie nájsť ani odstrániť running a rollback digests.

## 22. Kontrolné otázky

1. Čo tvorí exact image-signing subject?
2. Ako sa index, platform manifest, config a layer digest líšia?
3. Čo signature dokazuje a čo nedokazuje?
4. Prečo keyless neznamená bez cryptographic keys?
5. Ktoré boundaries tvoria Fulcio, Rekor, bundle a TUF?
6. Ako sa signature líši od provenance a SBOM attestation?
7. Prečo Referrers API nie je trust decision?
8. Ako zabrániť tag time-of-check/time-of-use gapu?
9. Ako policy viaže signer identity na exact subject?
10. Prečo podpis amd64 manifestu nepokrýva arm64?
11. Ako funguje digest-bound quarantine?
12. Čo musí overiť signature acceptance verdict?

## Glossary impact

Relevantné pojmy: image-signing subject, subject-to-runtime trust lifecycle, multi-platform signing contract, signing authority, signer authorization generation, verification-bundle generation, signature-to-runtime chain, digest-bound quarantine, revocation propagation, signature acceptance verdict a wrong-subject negative test.

## Primárne zdroje

- [Sigstore documentation](https://docs.sigstore.dev/)
- [Cosign signing overview](https://docs.sigstore.dev/cosign/signing/overview/)
- [Cosign signature verification](https://docs.sigstore.dev/cosign/verifying/verify/)
- [Cosign attestation verification](https://docs.sigstore.dev/cosign/verifying/attestation/)
- [Sigstore custom trust components](https://docs.sigstore.dev/cosign/system_config/custom_components/)
- [OCI Image Manifest Specification](https://github.com/opencontainers/image-spec/blob/main/manifest.md)
- [OCI Image Index Specification](https://github.com/opencontainers/image-spec/blob/main/image-index.md)
- [OCI Distribution Specification](https://github.com/opencontainers/distribution-spec/blob/main/spec.md)
- [in-toto Attestation Framework](https://in-toto.io/docs/specs/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: SBOM](sbom.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Policy as Code →](policy-as-code.md)
<!-- KNOWLEDGE-NAVIGATION:END -->