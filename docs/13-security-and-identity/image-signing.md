# Image signing

Image signing cryptographically viaže container image digest na signing identity alebo key a umožňuje consumerovi vyhodnotiť, či artifact spĺňa jeho trust policy. Signature je evidence o presnom obsahu a signerovi; nie je automatickou zárukou bezpečného source, build procesu ani absence vulnerabilities.

## 1. Mentálny model

```text
immutable image digest
→ signature alebo keyless certificate
→ signer identity a trust root
→ transparency/bundle evidence
→ verification policy
→ admission alebo promotion decision
```

Správna otázka nie je iba „je image podpísaný?“, ale:

```text
Kto podpísal ktorý digest?
→ V akom autorizovanom kontexte?
→ Aké claims a evidence overujeme?
→ Čo sa stane pri zlyhaní verification?
```

## 2. Čo signature dokazuje

Pri správnej verification signature dokazuje:

- integrity signed payloadu,
- control nad private keyom alebo ephemeral signing identity,
- binding na konkrétny image digest,
- voliteľné signed claims.

Nedokazuje automaticky:

- že image je bez vulnerabilities,
- že source bol reviewovaný,
- že builder bol izolovaný,
- že signer bol oprávnený,
- že artifact je vhodný pre daný environment,
- že key nebol kompromitovaný.

## 3. Content-addressable identity

OCI artifact identity je digest manifestu:

```text
registry.example/app@sha256:...
```

Digest sa zmení pri zmene signed manifest bytes.

Image tag:

```text
registry.example/app:1.4
```

je mutable reference. Verification a policy majú byť vyhodnocované nad resolved digestom.

## 4. Tag, manifest a config digest

Rozlišuj:

- tag → mutable name,
- image index digest → multi-platform manifest list,
- image manifest digest → konkrétna platform variant,
- config digest,
- layer digests.

Signature musí jasne určiť subject. Podpísanie indexu nemusí znamenať samostatný policy statement pre každý platform manifest.

## 5. Multi-architecture images

```text
index digest
├─ linux/amd64 manifest digest
├─ linux/arm64 manifest digest
└─ windows/amd64 manifest digest
```

Policy rozhodne, či vyžaduje:

- signature indexu,
- signature každej platform variant,
- obe vrstvy,
- platform-specific provenance a SBOM.

Consumer musí overiť digest, ktorý runtime skutočne pullne.

## 6. Signature payload

Signature typicky chráni:

- subject digest,
- artifact identity alebo reference,
- optional claims/annotations,
- signature metadata.

Unsigned registry tag alebo external metadata sa nesmie považovať za cryptographically bound claim.

## 7. Key-based signing

Key-based model:

```text
private signing key
→ podpis image digestu
→ public key alebo certificate
→ consumer trust store
```

Výhody:

- jednoduchý offline trust model,
- kontrola nad key lifecycle,
- použiteľnosť bez public identity provider.

Riziká:

- key distribution,
- long-lived compromise window,
- rotation a revocation,
- shared key attribution,
- backup/recovery.

## 8. Signing-key lifecycle

Definuj:

- generation alebo import,
- ownera a purpose,
- storage,
- authorized workloads,
- cryptoperiod,
- rotation,
- revocation,
- audit,
- backup,
- destruction,
- compromise response.

Signing key nemá byť uložený ako plaintext CI secret.

## 9. KMS a HSM

KMS/HSM model umožňuje signing bez exportu private keyu.

Controls:

- workload-specific authorization,
- key usage restriction,
- audit operations,
- region/account boundary,
- quorum alebo approval pre critical keys,
- rate limits,
- disable/delete protection,
- recovery.

KMS chráni key material, ale nevaliduje, či build job podpisuje správny digest.

## 10. Shared key vs identity

Jeden shared key pre viac projects znižuje attribution a zväčšuje blast radius.

Preferuj identity alebo keys oddelené podľa:

- organization,
- repository,
- release pipeline,
- environment,
- product risk.

Public key odpovedá „ktorý key“, nie vždy „ktorý workflow a source context“.

## 11. Keyless signing

Sigstore keyless model používa:

```text
OIDC identity
→ ephemeral key pair
→ short-lived signing certificate
→ signature
→ transparency evidence alebo verification bundle
```

Private key je krátkodobý a nemusí byť dlhodobo uložený.

„Keyless“ neznamená bez cryptographic keys; znamená bez manuálne spravovaného long-lived signing keyu pre každého signera.

## 12. OIDC identity

OIDC provider autentizuje workload alebo používateľa.

Verification policy má obmedziť:

- issuer,
- subject alebo certificate identity,
- repository,
- workflow,
- branch/tag/environment,
- organization,
- event type,
- audience podľa implementation.

Dôvera v celý issuer bez identity restriction je príliš široká.

## 13. Fulcio

V Sigstore public-good architecture Fulcio vydáva short-lived code-signing certificates pre overenú OIDC identity.

Consumer dôveruje:

- Fulcio trust root,
- OIDC issuer/identity claims,
- certificate validity a extensions,
- signed artifact binding.

Certificate issuance nie je application authorization; policy určuje, ktoré identities smú podpisovať konkrétny artifact.

## 14. Rekor

Rekor je transparency log pre signed software supply-chain metadata.

Transparency poskytuje:

- append-only evidence,
- inclusion proof,
- discoverability,
- detection unexpected signing.

Transparency log nezabráni signerovi podpísať malicious artifact. Umožní však audit a odhalenie podľa monitoringu a policy.

## 15. Verification bundle

Moderný bundle môže uchovať:

- signature,
- signing certificate,
- certificate chain,
- transparency inclusion evidence,
- timestamp-related material.

Bundle umožňuje neskoršiu alebo offline verification bez závislosti na okamžite dostupnom remote logu, ak trust roots a policy sú dostupné.

## 16. Trust root

Consumer potrebuje trusted roots pre:

- certificate authority,
- transparency log,
- timestamp service,
- self-managed public keys,
- TUF-distributed trust metadata.

Trust root bootstrap je mimo samotnej artifact signature. Musí byť distribuovaný a aktualizovaný bezpečným channelom.

## 17. TUF pre trust metadata

TUF môže distribuovať a rotovať trusted keys a metadata s:

- root role,
- targets,
- snapshot,
- timestamp,
- threshold signatures,
- expirations.

Pomáha chrániť verification clients pred rollback a freeze útokmi pri trust-root updates.

## 18. Identity policy

Príklad policy intentu:

```text
accept image iba ak:
- signature je cryptographically valid,
- OIDC issuer je approved,
- signer identity patrí protected release workflowu,
- subject digest sa zhoduje,
- source repository je approved,
- release event je protected,
- required provenance a SBOM sú validné.
```

Regex musí byť anchored a presne testovaný. Príliš široká identity pattern môže povoliť attacker-controlled repository alebo branch.

## 19. Signing v CI/CD

Signing job má:

- bežať po trusted build verification,
- používať protected environment,
- mať short-lived identity,
- podpisovať resolved digest,
- nevykonávať untrusted build code,
- mať minimálne registry permissions,
- generovať audit evidence,
- publikovať signature atomicky s release workflowom.

## 20. Untrusted pull requests

Pull-request workflow nesmie získať signing identity pre production namespace.

Threat:

```text
attacker-controlled source
+ trusted signing permission
→ validne podpísaný malicious artifact
```

Policy musí viazať identity na trusted event, branch a environment, nie iba repository name.

## 21. Build a signing separation

Oddelenie:

```text
build job → vytvorí digest a provenance
verification/release job → overí evidence
signing job → podpíše approved digest
```

Znižuje riziko, že arbitrary build step priamo použije signing authority.

Separation nie je účinná, ak build môže meniť digest po approval.

## 22. Release approval

High-risk release môže vyžadovať:

- protected environment approval,
- two-person review,
- change ticket,
- provenance verification,
- vulnerability exception approval,
- exact digest confirmation.

Human approval nemá byť click bez zobrazenia subject digestu a evidence.

## 23. Annotations a claims

Signed annotations môžu niesť:

- repository,
- commit,
- workflow,
- release channel,
- environment,
- build ID.

Nepoužívaj free-form annotation ako jediný authorization source, ak authoritative claims existujú v certificate alebo provenance.

## 24. Signature vs attestation

```text
signature   → signer schválil alebo podpísal subject/payload
attestation → signer tvrdí konkrétny predicate o subjecte
```

Príklady attestations:

- SLSA provenance,
- SBOM,
- vulnerability scan,
- test result,
- policy verification summary.

Signature a attestation môžu používať rovnaký cryptographic infrastructure, ale majú odlišnú semantics.

## 25. in-toto Statement

in-toto Statement model:

```json
{
  "_type": "...Statement...",
  "subject": [{"name": "image", "digest": {"sha256": "..."}}],
  "predicateType": "...",
  "predicate": {}
}
```

Consumer musí validovať:

- statement schema,
- subject digest,
- predicate type,
- signer identity,
- predicate-specific policy.

## 26. DSSE

Dead Simple Signing Envelope oddeľuje payload type, payload bytes a signatures.

DSSE chráni proti cross-protocol confusion cez pre-authentication encoding.

Envelope nerieši dôveryhodnosť predicate ani authorization signer-a.

## 27. Provenance attestation

Provenance policy môže overovať:

- approved builder identity,
- build type,
- source repository,
- source revision,
- invocation parameters,
- dependencies,
- completeness,
- build environment properties.

Artifact signature bez provenance nevysvetľuje, ako artifact vznikol.

## 28. SBOM attestation

SBOM attestation viaže SBOM predicate na image digest.

Consumer overí:

- signer,
- subject,
- format/schema,
- primary component,
- platform,
- generation tool,
- completeness policy.

Podpísaná chybná SBOM zostáva chybná.

## 29. OCI artifact storage

Signatures a attestations možno uložiť v OCI registry ako related artifacts.

OCI manifest môže používať:

- `artifactType`,
- `subject`,
- descriptors,
- annotations.

Consumer potrebuje registry API alebo fallback mechanism na discovery related artifacts.

## 30. OCI Referrers

Referrers query vracia manifests, ktoré referencujú subject digest.

Use cases:

```text
image digest
← signature
← SBOM
← provenance
← scan report
```

Registry support, retention a copy semantics musia byť otestované end to end.

## 31. Tag-based fallback

Staršie registries môžu ukladať signatures pod convention-based tags odvodenými z digestu.

Riziká:

- tag mutability,
- collisions/conventions,
- garbage collection,
- copy tools, ktoré tags neprenesú,
- namespace pollution.

Preferuj native OCI subject/referrers support, keď je interoperabilný v celom path-e.

## 32. Registry garbage collection

Garbage collector môže odstrániť unattached alebo neviditeľné signature/attestation manifests.

Testuj:

- push,
- discovery,
- replication,
- retention,
- garbage collection,
- deletion subjectu,
- restore.

Evidence lifecycle musí byť aspoň taký dlhý ako artifact lifecycle a incident-retention požiadavky.

## 33. Registry replication a mirror

Pri copy/mirror over:

- digest preservation,
- platform indexes,
- signatures,
- attestations,
- referrers,
- media types,
- annotations,
- repository identity claims.

Niektoré signatures môžu viazať repository name alebo registry reference; promotion model musí rozumieť claim semantics.

## 34. Digest pinning

Digest pinning zabezpečí, že workload pullne presné bytes.

Signing zabezpečí, že digest bol schválený dôveryhodnou identity.

```text
digest pinning → čo presne
signature      → kto/čo to schválilo
provenance     → ako to vzniklo
policy         → či je to prijateľné
```

Potrebné sú kombinovane.

## 35. Verification stages

Verification môže prebehnúť:

- pri registry promotion,
- v deployment pipeline,
- admission controllerom,
- node/runtime agentom,
- periodickým inventory auditom.

Čím neskôr sa control uplatní, tým väčší je exposure window.

## 36. Admission policy

Kubernetes admission control môže odmietnuť Pod, ak image:

- nie je digest-pinned,
- nemá approved signature,
- má nesprávneho issuer/signer-a,
- nemá required provenance/SBOM,
- pochádza z neapproved registry,
- porušuje environment policy.

Policy má fail behavior explicitne definovaný.

## 37. Mutation a verification order

Ak admission webhook prepíše tag na digest alebo registry mirror, verification musí používať final effective subject.

Ordering problém:

```text
verify original reference
→ mutation zmení reference
→ runtime pullne iný artifact
```

Preferuj deterministic resolution a jasné admission ordering.

## 38. Policy as Code boundary

Verification policy má byť:

- versionovaná,
- reviewovaná,
- testovaná positive/negative cases,
- oddelená od artifact producer-a,
- auditovaná,
- rolloutovaná cez observe/enforce phases,
- chránená proti bypassu.

Detailný policy-engine model patrí do nasledujúcej kapitoly Policy as Code.

## 39. Offline verification

Offline alebo disconnected environment potrebuje:

- artifact,
- signature/bundle,
- trusted roots,
- identity policy,
- revocation/expiry semantics,
- required attestations.

„Offline“ nesmie znamenať vypnutie transparency alebo certificate validation; potrebné evidence sa prenesú vopred.

## 40. Verification cache

Cache môže znížiť latency a outage impact.

Cache key musí obsahovať:

- subject digest,
- signature/attestation digest,
- policy version,
- trust-root version,
- verifier version,
- decision time/expiry.

Cache iba podľa image tagu je nebezpečná.

## 41. Availability a fail behavior

Pri nedostupnom registry, transparency logu alebo identity metadata:

- fail closed pre nové production artifacts,
- použi validný bounded cache,
- allow existing verified workloads,
- degraded read-only operations,
- explicit break-glass s expiry.

Neobmedzený fail-open neguje verification.

## 42. Certificate expiry

Keyless certificate môže byť expired v čase neskoršej verification, ale signature môže zostať overiteľná, ak bundle a transparency/timestamp evidence dokazujú, že podpis vznikol počas platnosti.

Consumer musí používať správny historical verification model, nie iba porovnať aktuálny čas s certificate expiry.

## 43. Revocation

Revocation môže znamenať:

- revoke key/certificate authority,
- odstrániť identity trust,
- deny konkrétny digest,
- deny repository/workflow,
- quarantine artifact,
- update policy.

Transparency log entry sa nemaže; policy musí vedieť odmietnuť formerly valid signature.

## 44. Key a identity rotation

Rotation plán:

```text
pridať nový trust
→ začať podpisovať novým identity/keyom
→ overiť dual-trust obdobie
→ zastaviť staré signing
→ odstrániť starý trust
→ zachovať historical verification evidence
```

Náhla removal môže zneplatniť recovery alebo verification starších releases.

## 45. Compromised signing key

Postup:

```text
disable/revoke key
→ zastaviť release pipeline
→ identifikovať všetky signatures keyu
→ určiť compromise window
→ mapovať artifacts a deployments
→ quarantine neoverené digests
→ obnoviť signing z trusted environment
→ rotate trust policy
→ vydať advisory
→ monitorovať reuse
```

Re-signing compromised artifact novým keyom bez rebuild/forensics nie je remediation.

## 46. Compromised OIDC workflow identity

Over:

- repository a workflow changes,
- branch/environment rules,
- reusable workflows,
- token claims,
- cloud/registry trust policies,
- runner compromise,
- issued certificates/signatures,
- organization account takeover.

Keyless model presúva lifecycle z private-key storage na identity a workload policy security.

## 47. Artifact quarantine

Quarantine môže:

- zakázať promotion,
- deny digest v admission policy,
- odstrániť mutable tags,
- obmedziť registry pull,
- označiť artifact ako revoked,
- alertovať owners,
- zachovať forensic copy.

Samotné delete môže poškodiť evidence a neodstrániť cached/running copies.

## 48. Audit a telemetry

Sleduj:

- signing identity,
- issuer,
- repository/workflow/event claims,
- subject digest,
- signature and bundle location,
- transparency inclusion,
- policy version,
- verification result a reason,
- bypass/break-glass,
- registry copy/delete,
- trust-root rotation,
- admission decision,
- runtime digest.

Neloguj private keys, OIDC tokens ani secret KMS material.

## 49. Metrics

Užitočné metrics:

- signed production image coverage,
- keyless/KMS signing coverage,
- identity-policy precision,
- digest-pinned deployment coverage,
- required-attestation coverage,
- verification failure reasons,
- policy bypass count,
- unsigned artifact age,
- time to revoke compromised identity,
- registry referrer retention success,
- cached-decision age,
- runtime image verification drift.

## 50. Governance

Definuj:

- approved signing models,
- signer identities a namespaces,
- trust roots,
- key lifecycle,
- protected release workflows,
- required attestations,
- verification stages,
- environment-specific policies,
- break-glass,
- revocation/quarantine,
- historical verification retention,
- registry compatibility baseline.

## 51. Troubleshooting

### `no matching signatures`

Over subject digest, repository, signature discovery, referrers/fallback tag, media type a registry permissions.

### Certificate identity mismatch

Over exact OIDC issuer, subject claims, repository/workflow rename, reusable workflow identity a regex anchoring.

### Signature valid, policy deny

Cryptography je správna, ale signer, builder, source alebo environment nie je approved. Neobchádzaj policy cez „signature predsa platí“.

### Signature zmizla po mirrorovaní

Copy tool nepreniesol referrers alebo fallback tags. Porovnaj source/destination registry APIs a GC.

### Admission timeout

Over verifier availability, registry latency, trust metadata, cache a webhook failure policy. Nenastav trvalý `Ignore` bez risk decisionu.

### Multi-arch workload zlyháva iba na arm64

Over signature a attestations konkrétneho platform manifestu, nie iba indexu alebo amd64 variantu.

## 52. Anti-patterny

- verify tag namiesto resolved digestu,
- jeden shared signing key pre celú organizáciu,
- private key ako CI secret,
- keyless trust na celý OIDC issuer,
- untrusted PR s signing permission,
- regex identity bez anchors,
- signature bez subject match,
- admission `fail-open` bez bounded cache,
- registry copy bez attestations,
- delete compromised artifact bez deny policy,
- signature považovaná za vulnerability approval,
- current certificate expiry použitá na odmietnutie historicky validného bundled podpisu bez správneho time modelu.

## 53. Mini príklad

```text
source revision abc123
→ protected build workflow
→ image index digest sha256:index
→ platform provenance + SBOM
→ protected release workflow získa OIDC identity
→ keyless podpis digestu
→ signature/bundle + attestations v registry
→ deployment resolves digest
→ admission overí:
   issuer
   workflow identity
   repository
   subject digest
   provenance builder/source
   SBOM presence
→ Pod admitted
```

Negative tests:

- signature z fork repository je odmietnutá,
- signature z pull-request workflowu je odmietnutá,
- copied tag s iným digestom je odmietnutý,
- image podpísaný approved identity, ale bez required provenance, je odmietnutý,
- arm64 manifest bez evidence je odmietnutý,
- revoked digest zostane odmietnutý aj s historicky validnou signature.

## 54. Kontrolné otázky

1. Čo image signature dokazuje a čo nedokazuje?
2. Prečo je digest silnejšia identity než tag?
3. Aký je rozdiel medzi image index a platform manifest?
4. Ako funguje key-based a keyless signing?
5. Akú úlohu majú OIDC, Fulcio a Rekor?
6. Čo musí identity policy validovať?
7. Prečo untrusted PR nesmie mať signing authority?
8. Ako sa líši signature a attestation?
9. Čo je in-toto Statement a DSSE?
10. Ako OCI Referrers viažu evidence na image?
11. Prečo registry copy môže stratiť signatures?
12. Ako sa kombinuje digest pinning, signing a provenance?
13. Ako navrhnúť fail behavior admission verification?
14. Ako sa overuje historical keyless signature po expiry certificate?
15. Ako reagovať na compromised signing identity?

## Glossary impact

Relevantné pojmy: image signing, signed subject, OCI image digest, image index, platform manifest, key-based signing, keyless signing, signing key lifecycle, Sigstore, Cosign, Fulcio, Rekor, transparency log, verification bundle, signing identity policy, trust root, DSSE, in-toto Statement, provenance attestation, SBOM attestation, OCI artifact, artifactType, OCI subject, OCI Referrers, signature discovery, admission verification, verification cache, artifact revocation a artifact quarantine.

## Primárne zdroje

- [Sigstore Overview](https://docs.sigstore.dev/about/overview/)
- [Cosign Signing Containers](https://docs.sigstore.dev/cosign/signing/signing_with_containers/)
- [Cosign Verifying Signatures](https://docs.sigstore.dev/cosign/verifying/verify/)
- [Cosign Signing Blobs and Bundles](https://docs.sigstore.dev/cosign/signing/signing_with_blobs/)
- [Sigstore Security Model](https://docs.sigstore.dev/about/security/)
- [in-toto Attestation Framework](https://github.com/in-toto/attestation)
- [DSSE Protocol](https://github.com/secure-systems-lab/dsse)
- [OCI Image Manifest Specification](https://specs.opencontainers.org/image-spec/manifest/)
- [OCI Distribution Specification](https://specs.opencontainers.org/distribution-spec/)
- [ORAS Attached Artifacts and Referrers](https://oras.land/docs/concepts/reftypes/)
- [The Update Framework Specification](https://theupdateframework.github.io/specification/latest/)
- [SLSA Provenance](https://slsa.dev/spec/v1.2/provenance)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: SBOM](sbom.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Policy as Code →](policy-as-code.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
