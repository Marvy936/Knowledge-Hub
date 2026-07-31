# SBOM

Software Bill of Materials — SBOM — je machine-readable inventory components a relationships viazaný na konkrétny software subject. Poskytuje transparency, nie automatický security verdict. Operational hodnota vzniká iba vtedy, keď document správne opisuje exact artifact, explicitne uvádza lifecycle stage a generation method, zachováva component relationships a je prepojený s runtime inventory, vulnerability decisions a remediation workflowom.

Podpísaná SBOM môže byť neúplná. SBOM pre source lockfile môže byť správna pre source stage a zároveň nesprávna ako final-container inventory. Package name/version bez package identity a artifact digestu môže mapovať na nesprávny advisory. „Máme SBOM“ preto nie je acceptance condition.

## Subject-to-remediation lifecycle

SBOM má operational hodnotu až vtedy, keď opisuje exact immutable artifact a deklaruje stage, method a evidence authority. Lifecycle preto vedie od generation cez completeness a correlation až po deployed digest a verified remediation.

```text
immutable software subject
→ lifecycle stage, generation method a evidence authority
→ component identities a relationships
→ completeness, accuracy a confidence
→ SBOM format a signed/attested publication
→ ingestion, normalization a correlation
→ vulnerability, VEX, license a policy decisions
→ deployed/rollback runtime mapping
→ remediation a fixed-artifact verification
→ retention, update a second-generation validation
```

Každá SBOM musí odpovedať: čo presne inventarizuje, kedy vznikla, ktorý nástroj/authority ju vytvoril, ktoré paths a package types pokrýva a čo zámerne nepokrýva.

## Exact SBOM subject SEC-PAY-50

Subject oddeľuje source revision, index, platform artifact, SBOM digest a generation method. Toto rozlíšenie odhaľuje document, ktorý je validný ako source inventory, ale nepravdivo sa vydáva za final-filesystem evidence.

```yaml
incident: SEC-PAY-50
release: payments-7.24.0
sourceRevision: a81f2e9
artifactIndex: sha256:pay7240
platformArtifact: sha256:pay7240-arm
sbomFormat: CycloneDX-1.7
sbomDigest: sha256:sbom884
observedMethod: source-lockfile-scan
claimedSubject: sha256:pay7240
requiredMethod: final-filesystem-plus-build-toolchain
missingComponent: settlement-debug.jar
builderComponent: atlas-build-helper@2.4.1
runtimeCluster: atlas-prod-euc1
```

Subject ukazuje core defect: document bol vytvorený zo source lockfile-u, ale označený digestom final artifactu. Signature zabezpečila integrity tohto nepravdivého claimu.

## Lifecycle stages

Source SBOM inventarizuje declared dependencies v repository alebo lockfiles. Build SBOM pridáva toolchain, compiler, plugins a materials. Final-artifact SBOM analyzuje skutočný filesystem/package graph výsledného image alebo binary. Runtime inventory mapuje deployed digest a loaded modules/processes. Žiadna stage automaticky nenahrádza ostatné.

Source SBOM môže zachytiť dependency intent, ale vynechať OS packages z base image, files skopírované počas build-u, generated artifacts, statically linked libraries alebo injected payload. Final image scan môže vynechať build toolchain, ktorý artifact kompromitoval. Preto policy potrebuje stage-specific evidence inventory.

## Generovanie final-artifact SBOM

```bash
syft registry.atlas.example/payments@sha256:pay7240-arm \
  -o cyclonedx-json=/tmp/pay7240-arm.cdx.json

jq '{bomFormat, specVersion, serialNumber, metadata: .metadata.component, components: (.components | length)}' \
  /tmp/pay7240-arm.cdx.json
```

Prvý command preukazuje, že konkrétna Syft generation analyzovala platform artifact a vytvorila CycloneDX document. Druhý zobrazuje metadata a count. Nepreukazujú complete detection všetkých custom/JAR/native components, correct package versions, benign contents ani runtime deployment.

Targeted check injected file/componentu:

```bash
jq -e '.components[]? | select(
  (.name == "settlement-debug") or
  (.properties[]?.value? | contains("settlement-debug.jar"))
)' /tmp/pay7240-arm.cdx.json
```

Finding preukazuje, že component alebo property je v documente. No-match nepreukazuje absence file-u v artifacte; scanner ho mohol neidentifikovať. Filesystem inventory alebo allowlisted artifact layout je ďalší control.

## SPDX a CycloneDX

SPDX a CycloneDX sú štandardné formats s odlišným modelom a ecosystems. Oba vedia opisovať components/packages, relationships, hashes, licenses a external references; detail a extensions sa líšia podľa version. Conversion medzi formats môže stratiť semantics, preto source format/version zostáva súčasťou evidence.

Format compliance znamená validnú schema, nie complete inventory. Parser success nepreukazuje, že `metadata.component` zodpovedá artifact digestu alebo že dependency relationships sú správne.

## Component identity

Package URL identifikuje ecosystem, namespace, name, version a qualifiers. CPE sa používa v niektorých vulnerability sources, ale matching je často ambiguous. Cryptographic hashes identifikujú exact files/artifacts. Supplier, namespace a download/source location pomáhajú odlíšiť homonyms.

Version string môže byť vendor-backported alebo generated. Component bez version/hash má nižšiu decision confidence. SBOM ingestion má zachovať original fields a confidence, nie agresívne normalizovať rozdielne packages do jednej identity.

## Relationships a dependency graph

Flat component list neukazuje, prečo component existuje ani ktorý root artifact ho obsahuje. Relationships ako `DEPENDS_ON`, `CONTAINS`, `GENERATED_FROM`, `BUILD_TOOL_OF` alebo format-specific equivalents podporujú blast-radius a remediation analysis.

Transitive dependency môže vstúpiť cez plugin alebo base image. Build helper môže artifact meniť bez toho, aby bol runtime component. Separate builder/toolchain BOM preto dopĺňa final-artifact SBOM. Incident `SEC-PAY-50` ukázal, že vulnerable helper bol causal, hoci production image ho nemusela obsahovať.

## Completeness a accuracy

Completeness sa hodnotí voči expected inventory. Tím definuje package ecosystems, filesystem paths, base image, application bundles, language locks, statically linked components, generated files a build tools. Scanner coverage report a known fixture pomáhajú overiť detection.

Praktický fixture môže do canary artifactu vložiť known packages/files a očakávať ich v SBOM. Úspech nepreukazuje coverage všetkých formats, ale odhalí regressions nástroja alebo configu.

Accuracy zahŕňa správny name/version/supplier/hash a relationship. False component identity môže spôsobiť false vulnerability alebo zmeškaný fix. Dismissal sa viaže na exact component identity a evidence generation.

## Signing a attestation

SBOM sa publikuje ako OCI referrer alebo iný immutable related artifact a podpisuje/attestuje. Signature chráni document integrity a authority. Subject binding musí potvrdiť, že SBOM opisuje exact digest, nie tag alebo iný platform manifest.

```bash
cosign attest \
  --predicate /tmp/pay7240-arm.cdx.json \
  --type cyclonedx \
  registry.atlas.example/payments@sha256:pay7240-arm

cosign verify-attestation \
  --type cyclonedx \
  --certificate-identity-regexp '^https://github.com/Marvy936/atlas-payments/.github/workflows/release.yml@refs/heads/main$' \
  --certificate-oidc-issuer 'https://token.actions.githubusercontent.com' \
  registry.atlas.example/payments@sha256:pay7240-arm
```

Verification preukazuje signed attestation subject a authorized identity podľa policy. Nepreukazuje generation method, completeness, scanner trust alebo absence malicious component. Predicate metadata musí obsahovať tool/version/method/stage a policy ich semantic-ky kontroluje.

## Vulnerability correlation a VEX

SBOM poskytuje component inventory pre vulnerability matching. VEX vyjadruje status, napríklad affected, not affected, fixed alebo under investigation, s justification a scope. VEX nie je scanner suppression; je signed/owned statement viazaný na exact product/component/vulnerability a evidence.

`not affected` pre unreachable code môže byť validné, ale zmena configuration alebo feature môže reachability zmeniť. VEX má expiry/update trigger a nesmie sa automaticky dediť na nový digest bez compatibility proof.

## License a policy decisions

SBOM môže obsahovať declared/concluded license a copyright data. License policy potrebuje context distribúcie a linking/use; string match nie je právny verdict. Unknown license je inventory gap, nie automaticky prohibited component.

Policy môže vyžadovať SBOM presence, allowed format/version, exact subject, authorized generator, minimum coverage a no forbidden license/risk. Existence-only gate podporuje prázdnu alebo source-only SBOM.

## Runtime a rollback mapping

SBOM musí byť prepojiteľná s deployed digestom. Cluster read-back:

```bash
kubectl get pods -A -o json \
  | jq -r '.items[] | .metadata.namespace as $ns | .metadata.name as $pod | .status.containerStatuses[]? | [$ns,$pod,.imageID] | @tsv'
```

Výstup preukazuje reported runtime imageIDs. Nepreukazuje host integrity, loaded libraries ani SBOM availability. Inventory service následne mapuje each digest na SBOM/provenance/signature a ownera.

Rollback manifests a cached artifacts musia mať rovnakú evidence. Fixed production digest nepomôže, ak autoscaler, disaster recovery alebo rollback stále môže nasadiť vulnerable old digest.

## Incident SEC-PAY-50

Signed CycloneDX SBOM bola vytvorená zo source lockfile-u a spätne označená final digestom. Neobsahovala `settlement-debug.jar`, pretože file vznikol post-test injectionom na runneri. Neobsahovala ani builder helper ako toolchain component. Admission kontrolovalo iba prítomnosť signed SBOM.

Root cause nebola chyba CycloneDX formatu. Bola to nesprávna lifecycle stage, method a evidence claim. Shared compromised pipeline vytvorila artifact aj evidence, takže signature iba chránila neúplný document.

## Containment, recovery a acceptance

Containment zachová original SBOM, scanner metadata a final artifact pre forensic comparison a zablokuje affected digests. Document sa neopravuje in place; new trusted rebuild dostane new artifact a new evidence.

Recovery generuje separate source, builder/toolchain a platform-specific final-artifact SBOMs cez controlled authorities. Final filesystem scan a artifact layout policy zachytia injected files. Admission overí exact platform subject, generator/method/stage a minimum expected components.

Acceptance vyžaduje, aby `settlement-debug.jar` bol v compromised artifact inventory alebo explicitnom filesystem evidence, absent v clean rebuild-e, builder helper 2.4.3 bol v toolchain BOM, runtime digest mapoval na correct SBOM a old digest bol denied. Negative fixture s known injected component musí gate zastaviť. Druhá platform build generation musí vytvoriť samostatnú, správne viazanú SBOM.

## Kontrolné otázky

1. Prečo source SBOM nie je final-artifact SBOM?
2. Čo podpis SBOM preukazuje a čo nepreukazuje?
3. Ako Package URL, CPE a hash riešia odlišné identity potreby?
4. Prečo relationships zvyšujú remediation hodnotu?
5. Ako sa VEX líši od scanner suppression?
6. Prečo runtime mapping musí zahŕňať platform digest a rollback paths?
7. Ktorý defect v SEC-PAY-50 bol method/stage problem, nie format problem?

## Referencie

- [SPDX specification](https://spdx.dev/specifications/)
- [CycloneDX specification](https://cyclonedx.org/specification/overview/)
- [CISA SBOM resources](https://www.cisa.gov/sbom)
- [Syft documentation](https://github.com/anchore/syft)
- [VEX overview](https://www.cisa.gov/resources-tools/resources/minimum-requirements-vulnerability-exploitability-exchange-vex)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Supply-chain security](supply-chain-security.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Image signing →](image-signing.md)
<!-- KNOWLEDGE-NAVIGATION:END -->