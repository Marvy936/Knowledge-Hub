# Image signing

Image signing cryptographically viaže konkrétny OCI subject na signing key alebo overenú signing identity. Production control však nevznikne tým, že príkaz vypíše `Verified OK`. Consumer musí preukázať, že podpis patrí presne digestu, ktorý sa má spustiť, signer bol oprávnený pre daný product a environment, required attestations opisujú ten istý subject a všetky deployment paths výsledok skutočne presadzujú.

Podpis chráni authenticity a integrity subjectu od signing momentu. Nehovorí, že source je bezpečný, builder dôveryhodný, artifact bez vulnerabilities alebo runtime vybral rovnaký platform digest. Signature policy je preto jedna vrstva source-to-runtime trustu.

## Subject-to-runtime trust lifecycle

Signature verdict má význam iba vtedy, keď sa zachová exact OCI subject od podpisu až po platform digest zvolený runtime-om. Lifecycle preto oddeľuje signing identity, registry publication, consumer policy, cache a runtime read-back.

```text
release intent a exact OCI subject
→ signing authority a issuance context
→ signature alebo attestation
→ trust root, certificate identity a time evidence
→ signer authorization pre product/environment
→ registry publication a referrer preservation
→ consumer policy na final deployment boundary
→ selected platform manifest a runtime digest
→ continuous re-evaluation a quarantine
→ revocation, replacement a second-release validation
```

Tag, index digest, platform manifest digest a config/layer digests sú odlišné identities. Policy, ktorá overí ľubovoľný podpis v repository, nemusí chrániť artifact vybraný runtime-om.

## Exact signing subject SEC-PAY-51

Subject rozlišuje index, amd64 a arm64 manifests, signer identity, policy generation a cache key. Toto rozlíšenie je nevyhnutné, aby validný podpis jedného platform artifactu nemohol autorizovať iný runtime digest.

```yaml
incident: SEC-PAY-51
releaseTag: payments:7.24.0
imageIndex: sha256:pay7240
platforms:
  linux-amd64: sha256:pay7240-amd
  linux-arm64: sha256:pay7240-arm
signedSubjectObserved: sha256:pay7240-amd
runtimePlatform: linux-arm64
runtimeDigest: sha256:pay7240-arm
signingIdentity: https://github.com/Marvy936/atlas-payments/.github/workflows/release.yml@refs/heads/main
policyGenerationExpected: POL-IMG-18
policyGenerationLoaded: POL-IMG-16
cacheKeyObserved: tag-payments-7.24.0
forbidden:
  - repository-level-any-signature-match
  - tag-based-allow-cache
  - unsigned-selected-platform
```

Subject ukazuje misbinding: validný amd64 podpis bol použitý ako dôkaz pre compromised arm64 runtime.

## Key-based a keyless signing

Key-based signing používa private key, ktorej custody, purpose, rotation a verifier trust spravuje organizácia. Keyless signing používa krátkodobý certificate vydaný po OIDC identity proofe a transparent/time evidence. „Keyless“ neznamená bez cryptographic keys; mení issuance a identity lifecycle.

Pri keyless verification policy kontroluje certificate issuer, exact workflow/repository/ref identity, subject digest a čas/transparency evidence podľa trust modelu. Broad regex pre všetky workflows organizácie môže autorizovať untrusted pipeline.

## Signing exact digestu

```bash
cosign sign \
  --yes \
  registry.atlas.example/payments@sha256:pay7240-arm
```

Command vytvorí signature pre exact arm64 manifest subject podľa configured signing identity. Nepreukazuje, že signer workflow bol authorized, artifact vznikol na trusted builderi, registry referrers sa zachovali alebo cluster signature overí.

Verification:

```bash
cosign verify \
  --certificate-identity-regexp '^https://github.com/Marvy936/atlas-payments/.github/workflows/release.yml@refs/heads/main$' \
  --certificate-oidc-issuer 'https://token.actions.githubusercontent.com' \
  registry.atlas.example/payments@sha256:pay7240-arm
```

Successful output preukazuje cryptographic signature a certificate identity pre exact requested subject podľa Cosign trust materialu. Nepreukazuje semantic authorization všetkých claims, provenance/SBOM completeness, vulnerability policy alebo running digest.

## Multi-platform images

OCI index je manifest list, ktorý odkazuje na platform-specific manifests. Podpísanie indexu chráni graph references, ak policy a tooling podpis/verifikáciu indexu správne podporujú. Podpísanie iba amd64 manifestu nechráni arm64. Niektoré organizations podpisujú index aj každý platform manifest a vyžadujú platform-specific attestations.

Platform graph inspection:

```bash
cosign triangulate registry.atlas.example/payments@sha256:pay7240-arm

docker buildx imagetools inspect \
  registry.atlas.example/payments@sha256:pay7240
```

Prvý command ukáže signature artifact reference podľa registry modelu. Druhý ukáže index/platform descriptors. Nepreukazujú signature policy acceptance ani runtime selection; cluster/node platform a pulled `imageID` sa overujú samostatne.

## Attestations a semantic verification

Signature hovorí „authorized identity podpísala subject“. Attestation pridáva predicate, napríklad provenance, SBOM alebo vulnerability scan. Consumer musí overiť predicate type, authority, subject a relevantné fields. Prítomnosť jednej attestation ľubovoľného typu nie je complete evidence.

```bash
cosign verify-attestation \
  --type slsaprovenance \
  --certificate-identity-regexp '^https://github.com/Marvy936/atlas-payments/.github/workflows/release.yml@refs/heads/main$' \
  --certificate-oidc-issuer 'https://token.actions.githubusercontent.com' \
  registry.atlas.example/payments@sha256:pay7240-arm
```

Verification preukazuje signature a requested predicate type. Policy ešte kontroluje builder identity, source revision, build definition, parameters, materials a evidence authority. Matching malicious digest od compromised buildera môže mať validnú attestation.

## Trust roots, time a transparency

Verifier potrebuje trusted root/certificate chain, OIDC issuer policy a podľa mode-u transparency/time evidence. Offline verification musí mať current trust bundle a defined behavior pri nedostupnom logu. Fail-open pri verification dependency outage vytvára unsigned deployment path; fail-closed bez recovery capacity môže zablokovať urgentný safe release.

Signing certificate expiration neznamená, že historical signature bola neplatná v signing čase, ak existuje trusted timestamp/transparency proof. Revoked signer identity alebo compromised workflow však môže vyžadovať quarantine všetkých outputs z exposure interval-u, aj keď cryptographic signatures zostávajú matematicky validné.

## Registry promotion a evidence preservation

Promotion medzi registries musí kopírovať exact digest graph a related referrers. Retag bez digest read-backu alebo tool, ktorý neprenesie OCI artifacts, môže oddeliť image od signatures/attestations. Consumer policy má zlyhať, ak required evidence chýba, nie hľadať podobný artifact v source repository.

Unknown copy outcome sa overuje destination digestom a referrer inventory. Blind retry alebo rebuild pod rovnakým tagom môže zmeniť subject.

## Admission a runtime enforcement

Admission policy dostane resolved image subject a overí signature/evidence pred create/update. Coverage zahŕňa native workloads, Jobs, CronJobs, custom controllers, debug/ephemeral containers, direct node paths a recovery workflows. Policy iba na primary Deployment API nebráni custom controlleru vytvoriť unsigned Pod.

Runtime read-back:

```bash
kubectl get pods -A -o json \
  | jq -r '.items[] | .metadata.namespace as $ns | .metadata.name as $pod | .status.containerStatuses[]? | [$ns,$pod,.imageID] | @tsv'
```

Výstup preukazuje imageIDs reported bežiacimi containers. Nepreukazuje signature verdict history, node runtime integrity ani to, že tag-based admission cache použila current policy.

## Cache semantics

Verification cache musí byť viazaná minimálne na immutable digest, policy generation, trust-root generation, quarantine/revocation state a required evidence set. Cache key `repository:tag` umožní, aby mutable tag po prvom allow ukazoval na iný digest. Cache iba na digest môže byť stale po signer revocation alebo policy tightening.

Negative cache a dependency outage behavior sú rovnako explicitné. Timeout sa nesmie automaticky interpretovať ako allow bez approved, bounded exception subjectu.

## Revocation a quarantine

OCI signature štandardne nezmizne len preto, že signer už nie je trusted. Revocation policy môže odstrániť signer/workflow authorization, pridať digest do quarantine listu, revoke-nuť certificates/keys a zablokovať deployment/rollback. Running workloads sa musia re-evaluovať a podľa risku nahradiť; admission iba zabráni novým creates.

## Incident SEC-PAY-51

Release index `sha256:pay7240` obsahoval amd64 a arm64 manifests. Keyless bundle podpísal iba `sha256:pay7240-amd`. Production arm64 nodes vybrali compromised `sha256:pay7240-arm`. Verifier nehľadal signature pre selected subject; našiel ľubovoľnú validnú signature v repository a cache-oval allow podľa tagu `payments:7.24.0`.

Cryptography fungovala. Root cause bol subject misbinding a incomplete consumer policy. Multi-platform ambiguity a tag cache boli amplifiers. Running arm64 artifact nikdy nemal required signature/evidence.

Competing hypotheses boli registry mutation, signature-referrer loss, wrong platform selection, unsigned arm64, stale policy a verifier cache defect. Index inspection, Cosign subject, node platform a runtime `imageID` ukázali exact mismatch.

## Containment a authoritative recovery

Containment quarantinuje index aj affected arm64 digest, zastaví rollout/rollback, zachová registry graph, signatures, admission decisions, cache keys a runtime inventory a nahradí workload trusted previous/new digestom podľa business recovery.

Recovery rebuildne new index/platform digests, podpíše exact contract, pridá platform-specific provenance/SBOM, nasadí immutable policy generation `POL-IMG-18` a invaliduje tag-based cache. Policy input používa resolved digest a selected platform; native aj custom-controller paths musia prejsť rovnakým PEP-om.

Acceptance vyžaduje successful signed amd64 aj arm64 canary, deny unsigned selected platformu, deny signature z wrong workflow/environment, deny quarantined old digest a running new digest na nodes. Mutable tag change nesmie reuse-nuť allow cache. Druhý multi-platform release musí prejsť exact-subject verification bez repository-level fallbacku.

## Kontrolné otázky

1. Čo image signature preukazuje a čo nepreukazuje?
2. Prečo multi-platform index a platform manifests potrebujú explicitný contract?
3. Ako keyless signing mení, ale neodstraňuje key trust?
4. Prečo existence attestation nestačí bez semantic predicate validation?
5. Ktoré fields musí obsahovať safe verification cache key?
6. Ako revocation ovplyvní už running workloads?
7. Prečo SEC-PAY-51 nebol cryptographic failure?

## Referencie

- [Sigstore Cosign](https://docs.sigstore.dev/cosign/)
- [OCI Image Specification](https://github.com/opencontainers/image-spec)
- [OCI Distribution Specification](https://github.com/opencontainers/distribution-spec)
- [SLSA provenance](https://slsa.dev/spec/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: SBOM](sbom.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Policy as Code →](policy-as-code.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
