# Artifact versioning

Artifact versioning spája ľudsky čitateľný release význam s presnou content identity bytes. Logical version pomáha ľuďom, dependency resolverom a support procesu hovoriť o kompatibilite. Digest identifikuje konkrétny artifact. Provenance vysvetľuje, z akého source, build definition a buildera vznikol. Release manifest viaže viac artifacts, configuration generations a contracts do jednej podporovanej release unit.

Tieto identity sa nesmú zamieňať. Tag `10.0.0` môže byť mutable locator. OCI image index digest identifikuje multi-platform graph, ale nie jeden platform manifest. Package version môže byť immutable v jednom registry a prepísateľná v inom. Release ID môže zahŕňať API, worker, migrations a configuration, ktoré nemajú rovnaký individuálny version lifecycle.

## 1. Dominantný source-to-release-identity model

```text
exact candidate a pinned build inputs
→ immutable artifact bytes
→ content digest a media/platform identity
→ write-once publication
→ signature, SBOM a provenance viazané na digest
→ logical version a compatibility metadata
→ multi-artifact release manifest
→ promotion a deployment records
→ support, revocation, retention a recovery
```

Versioning nie je iba naming convention. Musí umožniť odpovedať, ktoré exact bytes boli testované, podpísané, nasadené, zraniteľné, podporované alebo potrebné na recovery.

## 2. Artifact identity layers

Atlas rozlišuje:

```text
source version
→ commit alebo candidate identity

logical artifact version
→ napríklad 10.0.0 alebo 10.0.0-rc.4

locator
→ registry repository + tag alebo package coordinate

content identity
→ digest/checksum konkrétnych bytes

release identity
→ manifest viacerých artifacts a configuration contracts
```

Rovnaký logical version nesmie odkazovať na viac odlišných bytes v jednom trusted release channeli. Rovnaký digest môže mať viac locatorov alebo tags, no jeho content sa nemení.

## 3. Exact artifact subject

```yaml
artifactSubject:
  name: payments-api
  type: oci-image-index
  logicalVersion: 10.0.0-rc.4
  repository: registry.atlas.example/payments-api
  indexDigest: sha256:pay1000api
  platforms:
    linux-amd64:
      manifestDigest: sha256:pay1000api-amd64
      configDigest: sha256:cfg-amd64-1000
    linux-arm64:
      manifestDigest: sha256:pay1000api-arm64
      configDigest: sha256:cfg-arm64-1000
  sourceCandidateSha: d94e1c6
  buildDefinitionSha: 18ab442
  builderIdentity: atlas-build/prod
  sbomDigest: sha256:sbom-pay1000api
  provenanceDigest: sha256:prov-pay1000api
  signatureBundleDigest: sha256:sig-pay1000api
```

Per-platform identity je nevyhnutná pri multi-architecture images. Index signature môže viazať celý graph, no platform-specific tests a SBOM musia byť korelované s konkrétnymi manifests podľa evidence modelu.

## 4. Praktický OCI read-back

Mutable tag sa resolve-ne na digest:

```bash
ref='registry.atlas.example/payments-api:10.0.0-rc.4'
index_digest="$(crane digest "$ref")"
printf 'index=%s@%s\n' "${ref%:*}" "$index_digest"
```

Výstup preukazuje registry mapping v čase query. Nepreukazuje, že tag zostane immutable ani že runtime použije rovnaký platform digest. Manifest graph sa prečíta:

```bash
crane manifest "${ref%:*}@${index_digest}" | jq '{mediaType,manifests:[.manifests[]|{digest,platform}]}'
```

Output preukazuje descriptors publikovaného indexu. Nepreukazuje dostupnosť všetkých layers, správnosť binary ani matching attestations. Platform pull a runtime test sú samostatné evidence.

## 5. Checksums pre file artifacts

Pre archive alebo migration bundle:

```bash
sha256sum dist/payments-migrations-10.0.0-rc.4.tar.gz \
  > dist/payments-migrations-10.0.0-rc.4.tar.gz.sha256

sha256sum --check dist/payments-migrations-10.0.0-rc.4.tar.gz.sha256
```

Successful check preukazuje local byte equality s checksum file-om. Nepreukazuje, že checksum pochádza z trusted release manifestu alebo že archive je safe na extraction. Signature/provenance a content policy dopĺňajú integrity.

## 6. Tags a write-once publication

Tag je vhodný ako human locator, pokiaľ registry policy zabráni overwrite v release repository. Candidate tags môžu byť mutable iba v explicitne non-authoritative namespace; promotion sa aj tak viaže na digest.

```text
candidate-d94e1c6
→ convenient build locator

10.0.0-rc.4
→ release-candidate locator

10.0.0
→ supported release locator

sha256:...
→ immutable content identity
```

Policy má odmietnuť tag mutation po publication. Ak registry nemá immutability, release system môže compare-nuť existing digest a failnúť pri konflikte.

## 7. Artifact graph a release manifest

Application release často obsahuje viac outputs:

```yaml
releaseManifest:
  releaseId: payments-10.0.0-rc.4
  version: 10.0.0-rc.4
  sourceCandidateSha: d94e1c6
  artifacts:
    api: registry.atlas.example/payments-api@sha256:pay1000api
    worker: registry.atlas.example/payments-worker@sha256:pay1000worker
    migrations: object://releases/payments-migrations@sha256:mig1000
    chart: oci://registry.atlas.example/charts/payments@sha256:chart1000
  configurationContract:
    schemaVersion: 7
    featureContractSha: 8b11f20
  compatibility:
    database: settlement-schema-v42-expand
    events: settlement-events-v18-compatible
  evidenceBundleDigest: sha256:evidence1000rc4
```

Release manifest je authoritative unit promotion a supportu. Samostatný image tag nepreukazuje matching worker, migration alebo chart. Manifest má byť immutable a integrity-protected.

## 8. Evidence binding

SBOM, signature, vulnerability report a provenance musia odkazovať na exact artifact subject. Report nad tagom je ambiguous, ak sa tag zmení. Evidence inventory má rozlišovať index-level a platform-level artifacts.

```bash
cosign verify-attestation \
  --type slsaprovenance \
  'registry.atlas.example/payments-api@sha256:pay1000api'

cosign verify-attestation \
  --type spdxjson \
  'registry.atlas.example/payments-api@sha256:pay1000api'
```

Successful verification môže preukázať cryptographic trust a subject binding podľa verifier policy. Nepreukazuje completeness SBOM ani correctness provenance claims. Predicate content a evidence authority sa musia hodnotiť.

## 9. Version uniqueness a registry replication

Copy medzi registries musí zachovať content graph. Tag copy bez digest verification môže resolve-núť source pred a destination po odlišne.

```bash
src='registry.build.example/payments-api@sha256:pay1000api'
dst='registry.prod.example/payments-api@sha256:pay1000api'
crane copy "$src" "$dst"

test "$(crane digest "$src")" = "$(crane digest "$dst")"
```

Rovnosť index digestov preukazuje graph identity na descriptor úrovni. Referrers, signatures a retention policies sa musia overiť podľa registry behavior.

## 10. Retention, revocation a recovery

Artifact lifecycle nekončí deploymentom. Supported release potrebuje retention minimálne počas support a recovery window. Last-known-good artifacts nesmú byť garbage-collected skôr než sa overí náhradná recovery cesta.

Revocation record vysvetľuje, že digest sa už nesmie promovať alebo spustiť:

```yaml
revocation:
  subjectDigest: sha256:pay1000api
  reason: compromised-generated-client-cache
  effectiveAt: 2026-07-31T13:10:00Z
  affectedReleases:
    - payments-10.0.0-rc.4
  requiredAction: rebuild-and-redeploy
```

Delete registry tagu nie je revocation. Existujúce deployments môžu naďalej používať digest a mirrors môžu držať content. Admission/promotion policy a runtime inventory musia revocation presadiť.

## 11. Version collisions a reproducibility

Ak dva buildy publikujú rovnaký logical version s odlišným digestom, vzniká version collision. Correct response nie je prepis starého artifactu. Pipeline má zastaviť publication a vyšetriť build inputs, registry state alebo unauthorized mutation.

Reproducible build môže vytvoriť rovnaké bytes, ale nie každý artifact format je deterministický bez explicitných timestamp, ordering a compression controls. Non-identical rebuild neznamená automaticky compromise; znamená, že digest identity je jediná presná authority a reproducibility assumptions treba overiť.

## Ako checksum, digest, podpis a provenance chránia artifact

Hash function číta bytes a deterministicky z nich vypočíta hodnotu pevnej dĺžky. SHA-256 vytvára 256-bitový výsledok, ktorý sa bežne zapisuje ako 64 hexadecimálnych znakov. Aj malá zmena vstupu vedie k inému hashu. Keď sa táto hodnota používa na identifikáciu obsahu, hovoríme často o **digest-e**; názov **checksum** sa používa najmä pri kontrole, či sa file počas prenosu alebo uloženia nezmenil.

Pre migration archive možno vytvoriť checksum file:

```bash
sha256sum dist/payments-migrations-10.0.0-rc.4.tar.gz \
  > dist/payments-migrations-10.0.0-rc.4.tar.gz.sha256

sha256sum --check \
  dist/payments-migrations-10.0.0-rc.4.tar.gz.sha256
```

Prvý command otvorí archive, vypočíta SHA-256 a shell uloží digest spolu s filename-om. Druhý command načíta očakávanú hodnotu, znovu vypočíta hash aktuálnych bytes a porovná ich. Výsledok `OK` preukazuje zhodu archive-u s daným checksum file-om. Nepreukazuje však, kto checksum vytvoril. Útočník, ktorý nahradí archive aj `.sha256`, môže dosiahnuť rovnaký success.

**Signature** pridáva kryptografické tvrdenie, že konkrétny subject podpísal držiteľ private key alebo identity akceptovanej verifier policy. **Provenance** opisuje source revision, build definition, buildera a vstupy, z ktorých artifact vznikol. Podpis môže viazať provenance k digestu, ale verifier stále musí skontrolovať obsah claims a dôveryhodnosť identity.

Ani platný digest a podpis nepreukazujú, že archive je bezpečný na extraction alebo funkčne správny. Tar môže obsahovať `../` path traversal, symlink mimo targetu, nečakané permissions alebo executable files. Content policy, sandbox extraction a testy dopĺňajú integrity a authenticity.

Logical version pomáha ľuďom hovoriť o kompatibilite, no exact bytes identifikuje digest. Release manifest preto viaže version, artifacts, platform manifests, configuration contract, SBOM, signature a provenance do jednej immutable release unit.

## 12. Connected incident `REL-PAY-68`

Atlas release automation vytvorila version `10.0.0-rc.4`. API amd64 a arm64 images vznikli v parallel jobs. Arm64 shard chýbal, no reusable workflow bol green. Release job publikoval tag `10.0.0-rc.4` najprv na amd64-only index. Neskorší retry pridal arm64 manifest a prepísal ten istý tag na nový index digest.

Release manifest ukladal iba tag a logical version. Staging nasadilo prvý digest; production resolve-la tag po retry a dostala druhý digest. Evidence a approval patrili starému graphu.

```text
logical version 10.0.0-rc.4
→ index digest A v staging
→ mutable tag rewrite
→ index digest B v production
→ rovnaký release label, rozdielne bytes a platform graph
```

Production arm64 manifest navyše nemal matching native-module test. 14 Pods crashovalo a support nedokázal okamžite určiť, ktorý graph bol „10.0.0-rc.4“.

Root cause bol artifact/release identity contract, nie iba tag mutation.

## 13. Recovery a acceptance verdict

Containment zablokuje tag overwrite, zachová registry events a inventarizuje deployed per-platform digests. Recovery vytvorí nový release candidate `10.0.0-rc.5`, publikuje complete index write-once, viaže platform evidence a vytvorí signed release manifest.

Artifact versioning je prijaté iba vtedy, keď:

```text
logical version má jeden authoritative immutable release subject
+ každý artifact má content digest a provenance
+ multi-platform graph obsahuje per-platform identity/evidence
+ tags sú locators, nie promotion authority
+ release manifest viaže všetky artifacts a contracts
+ copy overuje digest a evidence preservation
+ collision neprepisuje existujúci release
+ revocation blokuje promotion aj runtime policy
+ recovery artifacts majú retention
+ second registry a second platform resolve-nú rovnaký graph
```

## 14. Troubleshooting flow

Pri otázke „čo vlastne beží pod version 10.0?“ sleduj:

```text
logical version a release ID
→ release manifest digest
→ artifact locators a content digests
→ index/platform graph
→ evidence subjects
→ registry replication history
→ deployment/runtime image IDs
→ support/revocation state
```

Competing hypotheses môžu byť mutable tag, incomplete index, registry mirror lag, wrong platform selection, evidence bound na tag, artifact overwrite, release manifest drift alebo runtime cache. Názov version samostatne nie je diskriminačný dôkaz.

## 15. Anti-patterny

### Version ako jediná identity

Logical version komunikuje význam, ale neidentifikuje exact bytes bez immutable publication contractu.

### Tag promotion bez digestu

Target environment môže resolve-núť iný content než source evidence.

### Jeden image digest ako celá release unit

Worker, migrations, chart a configuration môžu byť odlišné generations.

### Delete tagu ako revocation

Running digest a mirrors zostávajú použiteľné.

### Rebuild a overwrite rovnakej version

Tým sa zničí audit a dependency resolver dostane nejednoznačný contract.

## 16. Kontrolné otázky

1. Aký rozdiel je medzi logical version, locatorom a digestom?
2. Čo identifikuje OCI index digest a čo platform manifest digest?
3. Prečo checksum samostatne nie je provenance?
4. Čo musí obsahovať multi-artifact release manifest?
5. Ako sa evidence viaže na artifact subject?
6. Čo preukazuje digest equality pri registry copy?
7. Ako vzniká version collision?
8. Prečo tag delete nie je revocation?
9. Aký identity split vznikol v `REL-PAY-68`?
10. Prečo staging a production dostali rozdielne bytes pod rovnakou version?
11. Ako retention súvisí s recovery?
12. Ako sa overí second-platform identity?

## Glossary impact

Relevantné pojmy: logical artifact version, artifact locator, content digest, OCI image index, platform manifest digest, release manifest, artifact graph, version collision, write-once publication, evidence subject binding, registry replication, artifact revocation, recovery retention a runtime image identity.

## Primárne zdroje

- [OCI Image Specification](https://github.com/opencontainers/image-spec)
- [OCI Distribution Specification](https://github.com/opencontainers/distribution-spec)
- [OCI Artifacts](https://github.com/opencontainers/artifacts)
- [Sigstore Cosign documentation](https://docs.sigstore.dev/cosign/)
- [SLSA specification](https://slsa.dev/spec/)
- [in-toto Attestation Framework](https://github.com/in-toto/attestation)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Reusable a parallel pipelines](reusable-and-parallel-pipelines.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Semantic Versioning →](semantic-versioning.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
