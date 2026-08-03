# ML supply-chain security

ML supply chain zahŕňa zdrojový kód, datasety, labels, notebooks, dependencies, base images, build runners, model artifacts, Registry metadata, deployment manifests a telemetry komponenty. Útočník nemusí poraziť model matematicky. Stačí zmeniť dependency, training input, serialized artifact, container image alebo promotion reference tak, aby platforma dôveryhodne nasadila nesprávne bytes.

V incidente `MLOPS-PAY-96` bol model zaregistrovaný z úspešného runu, ale serving image vznikol neskôr na inom runneri z mutable base tagu. Requirements neobsahovali transitive hashes, model artifact bol uložený pod prepisovateľným pathom a admission kontrola overovala iba image signature, nie väzbu medzi image, model digest a training provenance. Každá zložka vyzerala samostatne legitímne, no composite release nemal overiteľný chain of custody.

## 1. Supply-chain subject a trust graph

Supply-chain manifest musí pomenovať všetky inputs a transformations, ktoré vytvorili deployable release. Git commit alebo image digest sám nestačí, pretože model môže byť remote-loaded a dataset môže byť mimo repository.

```yaml
release_id: fraud-serving-2026-08-03.5
source:
  repository: git.example.com/ml/fraud
  commit: 5e3a...
data:
  training_snapshot: fraud-train-2026-07-31
  manifest_digest: sha256:data...
build:
  builder_identity: gha://fraud/model-build@v4
  workflow_digest: sha256:workflow...
  provenance_digest: sha256:prov...
model:
  artifact_digest: sha256:model...
  format: mlflow-pyfunc
image:
  digest: sha256:image...
dependencies:
  lock_digest: sha256:lock...
  sbom_digest: sha256:sbom...
signatures:
  model_attestation: sha256:model-att...
  image_bundle: sha256:sigstore-bundle...
```

Trust graph spája source → build → model → image → deployment. Verifikácia musí zlyhať, ak ktorýkoľvek edge chýba alebo ukazuje na inú generation.

## 2. Threats naprieč lifecycle

Source threat zahŕňa compromised account, malicious pull request alebo mutable third-party code. Build threat zahŕňa poisoned runner, secret exfiltration a substitution outputu. Dependency threat zahŕňa typosquatting, compromised release alebo unreviewed transitive update. Data threat zahŕňa source spoofing a poisoning. Artifact threat zahŕňa overwrite, deserialization payload a Registry tampering. Deployment threat zahŕňa tag drift a bypass admission policy.

Každý threat má authority boundary a evidence. Branch protection chráni repository mutation, ale nie downloaded dataset. Image signature chráni image identity, ale nie nutne training data. Registry RBAC chráni alias mutation, ale nie compromised builder, ktorý vytvoril podpísaný škodlivý artifact.

## 3. Hermetic a reproducible inputs

Build používa pinned source commit, immutable dataset manifest, locked dependencies, digest-pinned base image a versioned build definition. Network access počas build/trainingu sa obmedzí alebo auditovane proxyuje, aby dependency resolution neťahala neznáme latest packages.

ML training nemusí byť bit-for-bit deterministický, ale supply-chain reproducibility stále vyžaduje resolvable inputs a vysvetliteľnú variability. Run zaznamená framework, accelerator, seeds, nondeterminism flags a output digest. Nezhoda outputu pri rovnakých inputs je investigation signal, nie automaticky attack proof.

Notebook execution musí byť prevedený na versioned pipeline alebo exportovať exact notebook digest, environment a data inputs. Interaktívna bunka mimo commitnutého state je neauthoritative source.

## 4. Dependency locking a secure install

Direct version pin bez transitive locku nestačí. Lockfile obsahuje exact versions a hashes. MLflow dokumentácia pre secure installs odporúča pip hash-checking mode a môže obmedziť source distributions, aby install nespúšťal nečakaný build code.

```bash
pip-compile --generate-hashes \
  --output-file requirements.txt requirements.in

pip install \
  --require-hashes \
  --only-binary :all: \
  -r requirements.txt
```

Upload-time filtering môže zmraziť dependency universe k auditovanému času. Absolútny timestamp je reprodukovateľnejší než rolling „exclude newer 7 days“, ktorý sa každý deň mení.

Private index musí mať authentication, immutability/retention a malware/vulnerability process. Dependency confusion sa obmedzuje namespace policy a explicitnými indexmi. Build log nesmie vypisovať repository token.

## 5. SLSA provenance a build trust

SLSA Build track odlišuje existenciu provenance, hosted build platform a hardened build environment. Level nie je marketingový label; musí sa viazať na konkrétny artifact a splnené requirements. SLSA 1.2 zároveň znovu zavádza Source track, takže source a build assurance sa nemajú zamieňať.

Provenance opisuje builder identity, build definition, inputs a output subject digest. Musí byť generovaná build platformou, nie post-hoc textom od rovnakého scriptu, ktorý mohol output zameniť.

```text
source policy
→ reviewed immutable ref
→ hosted isolated builder
→ declared dependencies
→ build output digest
→ signed provenance
→ independent verification
```

Hardened builder minimalizuje persistent state, izoluje jobs, chráni signing identity a neumožní user code ľubovoľne meniť provenance.

## 6. SBOM, model BOM a dataset manifest

SBOM inventarizuje software packages, no ML release potrebuje aj model a data context. Model BOM môže uvádzať framework, flavor, serialization, code paths, external weights, license a expected loader. Dataset manifest uvádza sources, snapshots, schema, label definition a checksums bez nutnosti vložiť citlivé raw data do verejného attestation.

Inventár nie je vulnerability verdict. Vulnerability scanner môže nájsť CVE v package, ale tím musí posúdiť reachability a exposure. Naopak, neznámy custom model loader nemusí mať CVE a stále je kritický executable path.

SBOM a manifests sa content-addressujú a viažu na release. Neskoršie prepisovanie „current SBOM“ ničí incident evidence.

## 7. Signing, Sigstore a attestations

Signature dokazuje, že držiteľ identity/key podpísal konkrétny digest; nedokazuje, že artifact je bezpečný. Keyless Sigstore verification viaže certificate identity a OIDC issuer a môže používať transparency log. Policy musí kontrolovať očakávanú identity, issuer, repository/workflow a subject digest.

```bash
cosign verify \
  --certificate-identity-regexp \
    '^https://github.com/example/fraud/.github/workflows/build.yml@refs/heads/main$' \
  --certificate-oidc-issuer \
    'https://token.actions.githubusercontent.com' \
  registry.example.com/fraud@sha256:image
```

Attestation nesie predicate, napríklad provenance alebo vulnerability scan. `cosign verify-attestation` overí podpis; samostatná policy musí validovať predicate fields a subject.

```bash
cosign verify-attestation \
  --type slsaprovenance \
  --certificate-identity-regexp '...' \
  --certificate-oidc-issuer '...' \
  registry.example.com/fraud@sha256:image
```

Model artifact mimo OCI môže byť zabalený ako OCI artifact alebo mať podpísaný digest manifest. Dôležitá je väzba model ↔ image ↔ release, nie konkrétny transport.

## 8. Artifact immutability a retention

Object-store path `models/fraud/latest/` je mutable control, nie identity. Publication používa versioned prefix, checksums, committed manifest a read-after-write z fresh klienta. Registry version odkazuje na immutable model digest.

Retention policy musí zachovať current, previous known-good, incident hold a audit evidence. Garbage collection používa reachability z release manifests a Registry, nie iba age. Rollback artifact, ktorý bol odstránený alebo ktorého dependency wheel už nie je dostupný, nie je recovery target.

Delete a overwrite permissions sa oddeľujú od uploadu. Production promotion service nepotrebuje právo meniť historické bytes.

## 9. Serialization a model loading

Pickle-compatible artifact môže pri load vykonať code. Loader preto pracuje v sandboxed/minimal runtime bez broad credentials a načítava iba verified artifact z trusted source. Preferovaný bezpečnejší formát stále potrebuje parser hardening, size limits a compatibility test.

MLflow model môže obsahovať code paths a dependencies. Package inspection overí `MLmodel`, environment files, model signature, artifact list a unexpected executable files. Remote URI sa rozlíši na digest pred deploymentom.

Model scan nie je absolútna záruka. Dynamic Python code môže skryť behavior. Provenance, trusted builder a runtime isolation sú silnejšie než samotný static scan.

## 10. CI/CD identity a secret boundary

Build, evaluation a promotion používajú rozdielne identities. Training job môže zapisovať candidate artifacts, ale nemá meniť production alias. Evaluation job môže zapisovať evidence, ale nie prepisovať model. Promotion service vykoná compare-and-set až po approvals.

OIDC workload identity a short-lived credentials znižujú riziko leaked static secrets. Signing identity sa vydá iba schválenému workflow/ref a chráni pred pull-request code pathom. Self-hosted runner potrebuje ephemeral cleanup, isolation a patching.

Logs, artifacts a cache sa považujú za možný exfiltration channel. Cache key viaže dependency lock a trusted scope; untrusted fork nesmie obnoviť alebo zapisovať privileged cache.

## 11. Admission a deployment verification

Admission policy pred vytvorením workloadu overí image digest, signature/provenance, approved builder a release manifest. Runtime init môže navyše overiť remote-loaded model digest a signature. Iba image verification nestačí, ak model sa sťahuje pri starte.

```text
Git desired release
→ policy verifies manifest
→ image signature/provenance verified
→ model digest/attestation verified
→ workload admitted
→ runtime reports loaded fingerprint
→ synthetic inference
```

Policy decision sa loguje s input digestom a rule version. Emergency bypass je time-bound a auditovaný. Offline cluster potrebuje trusted roots a bundle material bez tichého vypnutia transparency/revocation checks.

## 12. Vulnerability a incident response

Vulnerability response začína inventory query: ktoré releases, runs, images a loaded runtimes obsahujú affected component? Ak SBOM nie je viazaný na deployed digest, impact analysis sa mení na odhad.

Containment môže freeze promotion, revoke builder identity, quarantine artifacts, rotate credentials, block digest alebo nasadiť known-good release. Rebuild z rovnakého compromised source bez opravy trust rootu nie je recovery.

Incident review overí source, builder, provenance, transparency log, Registry mutations, object-store audit a runtime fingerprints. Supply-chain incident môže vyžadovať obnoviť aj datasets a evaluation evidence, nie iba image.

## 13. Acceptance boundaries

Pozitívna acceptance vyžaduje pinned inputs, locked/hashed dependencies, trusted isolated builder, artifact digests, signed provenance/attestations, independent verification, least-privilege promotion a runtime loaded fingerprint. Recovery acceptance vyžaduje nové trusted build, revocation/quarantine starých subjects, complete impact inventory a second deployment.

Forbidden acceptance je signed `latest` tag, SBOM bez väzby na digest, provenance generovaná neovereným artifactom, alebo image verification pri neoverenom remote modeli. Second-operation test vytvorí ďalší build z rovnakého immutable subjectu a overí provenance aj deployment. Ak potrebuje mutable package index, long-lived secret alebo manuálne dopísaný digest, chain of custody nie je reprodukovateľný.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Privacy, security a adversarial ML](privacy-security-adversarial-ml.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: MLflow experiment tracking a Model Registry →](mlflow-experiment-tracking-model-registry.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
