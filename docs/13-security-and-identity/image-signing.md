# Image signing

Image signing cryptographically viaže konkrétny OCI artifact digest na signing key alebo overenú signing identity. Consumer môže následne overiť, že signed payload nebol zmenený a že podpis vytvoril držiteľ príslušného private keyu alebo identity credentialu.

Podpis však nie je všeobecná známka bezpečnosti. Cryptographically valid signature môže patriť neautorizovanému signerovi, compromised workflowu alebo artifactu obsahujúcemu vulnerability. Reálny control preto kombinuje immutable subject identity, signature verification, signer authorization, provenance alebo ďalšie attestations a enforcement policy.

```text
OCI digest
→ signature a signer evidence
→ trust-root validation
→ identity a authorization policy
→ required attestations
→ promotion alebo deployment decision
```

## 1. Čo signature dokazuje a čo nedokazuje

Pri správnej verification signature dokazuje integrity signed payloadu a control nad signing credentialom. Ak payload obsahuje image manifest digest, consumer vie preukázať, že podpis patrí presne týmto bytes.

Signature sama nedokazuje:

- že source code bol reviewovaný;
- že builder bol izolovaný alebo dôveryhodný;
- že image neobsahuje vulnerabilities alebo malware;
- že signer mal oprávnenie podpisovať daný product;
- že artifact je vhodný pre konkrétny environment;
- že signing key alebo OIDC workflow nebol compromised.

Preto sa musia oddeliť dve otázky:

```text
Je signature cryptographically valid?
→ Kto ju vytvoril a smel tento signer podpísať tento subject v tomto kontexte?
```

Prvá otázka patrí cryptography. Druhá patrí authorization a supply-chain policy.

## 2. OCI content-addressable identity

OCI image nie je jeden archive súbor. Tvorí ho graph manifestov, configuration objectov a layers. Každý descriptor obsahuje digest a veľkosť target contentu.

Image manifest opisuje jednu platform-specific image variantu: config a filesystem layers. Image index môže odkazovať na viac manifests, napríklad `linux/amd64` a `linux/arm64`.

```text
image index digest
├─ linux/amd64 manifest digest
│  ├─ config digest
│  └─ layer digests
└─ linux/arm64 manifest digest
   ├─ config digest
   └─ layer digests
```

Digest manifestu alebo indexu je content identity vypočítaná z presných serialized bytes. Zmena descriptoru, layeru alebo configu zmení príslušný parent digest. Podpis preto musí jednoznačne uviesť, ktorý digest je subject.

## 3. Tag nie je immutable subject

OCI tag, napríklad `registry.example/app:1.4`, je mutable repository reference. Registry operator alebo oprávnený publisher ho môže presunúť na nový manifest.

Digest reference, napríklad `registry.example/app@sha256:...`, identifikuje konkrétny manifest content. Verification nástroj môže najprv resolve-nuť tag na digest, ale decision a cache musia byť viazané na resolved digest.

Ak pipeline overí tag `1.4` a deployment neskôr znovu resolve-ne rovnaký tag, môže stiahnuť iný artifact než ten, ktorý bol schválený. Bezpečný promotion contract preto prenáša immutable digest od buildu po deployment.

## 4. Subject pri multi-architecture image

Pri multi-platform image treba rozhodnúť, či dôverujeme indexu ako release unit alebo každej platform variante samostatne.

Podpísanie index digestu viaže signer-a na presný zoznam platform manifests. Ak sa zmení amd64 alebo arm64 descriptor, zmení sa index digest. To je vhodné, keď release policy schvaľuje celý multi-platform set.

Niektoré organizations zároveň vyžadujú platform-specific provenance alebo SBOM, pretože jednotlivé variants môžu byť vytvorené na rozdielnych builders a obsahovať rozdielne packages. Runtime alebo admission controller musí vedieť, ktorý platform manifest node skutočne pullne.

Policy má explicitne uviesť:

- či sa overuje index digest, manifest digest alebo obe vrstvy;
- či každá platform potrebuje vlastnú provenance a SBOM;
- či sú povolené všetky platforms v indexe;
- ako sa spracuje nová platform pridaná do release-u.

## 5. Základný signing flow

Key-based flow vyzerá takto:

```text
release workflow získa immutable digest
→ private key podpíše canonical payload
→ signature sa uloží ako related OCI artifact alebo samostatný bundle
→ consumer načíta public key alebo certificate
→ overí signature a subject digest
→ policy rozhodne, či je signer trusted pre daný use case
```

Signing operation má prebiehať až po tom, čo release workflow vie, ktorý digest schvaľuje. Podpisovanie tagu pred pushom alebo podpisovanie lokálneho image name bez overenia remote digestu vytvára ambiguity.

Consumer musí overiť celý cryptographic chain a následne policy. Úspešný CLI output „verified“ môže znamenať iba validnú signature, nie splnenie environment-specific authorization.

## 6. Key-based signing

Pri self-managed key modeli organization vytvorí asymmetric key pair. Private key zostáva signing authority; public key sa distribuuje verification clients.

Výhodou je jednoduchý a často offline-capable trust model. Organization kontroluje key lifecycle a nemusí závisieť od external OIDC alebo public transparency service.

Nevýhodou je dlhodobý secret lifecycle. Treba riešiť generation, storage, access policy, cryptoperiod, rotation, revocation, backup a compromise response. Shared key pre množstvo repositories znižuje attribution a zväčšuje blast radius.

Public key odpovedá „ktorý key podpísal payload“. Ak jeden key používa viac workflows, neodpovedá presne „ktorý repository, branch a workflow run artifact schválil“.

## 7. KMS a HSM signing

KMS alebo HSM umožňuje signing bez exportu private key materialu. CI workload odošle digest alebo payload do signing API a dostane signature.

KMS zlepšuje key custody, audit a authorization, ale nevie sám určiť, či workflow podpisuje správny artifact. Ak compromised CI identity má permission volať `Sign`, môže podpisovať malicious digests.

KMS policy preto musí byť viazaná na konkrétny workload, environment a purpose. Pre high-impact keys možno použiť approval, quorum, rate limits a delete protection.

Availability KMS je súčasť release dependency. Outage nemá viesť k tomu, že pipeline preskočí signing a publikuje unsigned production artifact cez fallback path.

## 8. Keyless Sigstore model

„Keyless“ signing nepoužíva permanentný user-managed signing key. Cryptographic keys stále existujú, ale signer vytvorí ephemeral key pair a identity authority viaže krátkodobý certificate na OIDC identity.

```text
CI workload získa OIDC token
→ vytvorí ephemeral key pair
→ Fulcio overí OIDC identity a vydá short-lived signing certificate
→ workload podpíše artifact
→ signature a transparency evidence sa publikujú
→ private ephemeral key sa zahodí
```

Výhodou je silnejšia väzba na workload identity a odstránenie dlhodobého signing secretu z CI. Trust sa však presúva na OIDC issuer, Fulcio, transparency infrastructure, trust-root distribution a correctness identity policy.

## 9. OIDC identity pri signing-u

OIDC token môže niesť claims o repository, workflow, branch, tag, event type alebo environment. Presné claims závisia od issuer-a a CI platformy.

Verification policy nemá dôverovať celému issuer-u. Napríklad dôvera v každý certificate vydaný pre GitHub Actions by umožnila podpísať artifact ľubovoľnému public repository workflowu.

Policy má obmedziť najmenej:

- expected OIDC issuer;
- certificate subject alebo SAN identity;
- organization a repository;
- workflow definition alebo reusable workflow identity;
- protected branch, tag alebo environment;
- event type a audience, ak sú decision-relevant.

Regex identity rules musia byť anchored a testované proti attacker-controlled podobným menám. Pattern `.*trusted-repo.*` môže povoliť repository `trusted-repo-malicious`.

## 10. Fulcio, Rekor a transparency evidence

Fulcio je Sigstore certificate authority, ktorá vydáva short-lived code-signing certificates po overení OIDC identity. Certificate obsahuje identity-relevant claims alebo extensions a viaže ich na ephemeral public key.

Rekor je transparency log pre signed software supply-chain entries. Append-only log poskytuje inclusion evidence a umožňuje monitorovať, či sa pod určitou identity neobjavili neočakávané signatures.

Transparency log nie je preventive authorization control. Nezabráni compromised, ale stále oprávnenému workflowu podpísať malicious artifact. Umožní však získať audit evidence a detegovať podpis pri správnom monitoringu.

Verification musí overiť certificate chain, identity claims, signature, subject a požadované transparency alebo timestamp evidence podľa použitého Sigstore profile-u.

## 11. Verification bundle a offline verification

Moderný Sigstore bundle môže obsahovať signature, certificate, certificate-chain material a proof transparency-log inclusion. Bundle uchová evidence potrebnú na neskoršiu verification bez okamžitého query remote logu.

Offline verification stále potrebuje trusted roots a policy. Bundle nie je self-authenticating; attacker by mohol vytvoriť vlastný certificate chain a log evidence, ak consumer nedôveruje správnym roots.

Historical verification musí používať semantics času podpisu. Krátkodobý signing certificate bude pri neskoršej kontrole expirovaný, ale transparency/timestamp evidence môže preukázať, že signature vznikla počas validity. Consumer musí používať implementáciu, ktorá tento model správne podporuje.

## 12. Trust roots a TUF

Verification clients potrebujú trust roots pre certificate authority, transparency log, timestamp authority alebo self-managed public keys. Initial bootstrap týchto roots je samostatná security boundary.

Sigstore tooling používa TUF metadata na bezpečnú distribúciu a rotation trust materialu. TUF používa role separation, expirations, versioning a threshold signatures na ochranu pred rollback, freeze a key-compromise scenarios.

Trust-root update nemá byť automatické stiahnutie neovereného súboru z rovnakého channelu ako artifact. Client musí validovať TUF chain alebo použiť organization-controlled root distribution.

Air-gapped environment potrebuje plán, ako pravidelne importovať aktualizované roots a ako reagovať na emergency revocation bez neobmedzeného internet accessu.

## 13. Cryptographic verification oproti authorization policy

Cryptographic verification odpovedá, či signature sedí k payloadu a či certificate/key chainuje k trusted rootu. Authorization policy odpovedá, či konkrétna identity smela podpísať konkrétny artifact pre daný environment.

Príklad: certificate môže byť validný a identity môže patriť repository `example/demo`. Production policy však povoľuje iba protected workflow v `example/payments`. Výsledok musí byť deny, hoci cryptography je správna.

Policy tiež môže vyžadovať viac evidence:

```text
valid signature
+ approved signer identity
+ expected OCI digest
+ SLSA provenance
+ SBOM attestation
+ žiadna active quarantine
→ deployment allowed
```

Tento decision patrí do [Policy as Code](policy-as-code.md) a má byť logovaný s policy revision.

## 14. Signing v CI/CD

Production signing job má bežať iba v trusted release context-e. Untrusted pull-request code nesmie získať production signing identity.

Bezpečný flow oddeľuje untrusted build/test od protected release:

```text
pull request
→ build a tests bez production signing permissions
→ merge do protected branch
→ trusted rebuild alebo verified artifact promotion
→ protected release approval
→ short-lived signing identity
→ signature a attestations
→ immutable publication
```

Ak release job spúšťa attacker-controlled scripts pred získaním identity, malicious code môže signing credential použiť na ľubovoľný digest. OIDC claim o trusted branch nepomôže, ak samotný workflow načíta a spustí nedôveryhodný content.

Signing permission má byť úzka: iba relevantný repository namespace, registry repository a signing purpose. Job nemá mať broad admin permission k registry ani policy roots.

## 15. Build a signing authority

Build system vytvára artifact. Signing authority schvaľuje, že artifact spĺňa release policy. Tieto roly môžu byť v jednom pipeline-e, ale ich trust assumptions majú byť explicitné.

Ak builder automaticky podpisuje každý output bez nezávislých checks, signature iba dokazuje „tento builder vytvoril artifact“. To môže byť stále hodnotná provenance, ale nie nevyhnutne release approval.

Organization môže používať viac signatures alebo attestations:

- builder identity podpisuje provenance;
- security scanner vydá scan attestation;
- protected release workflow podpisuje release approval;
- environment-specific authority schváli promotion.

Verification policy potom presne určuje, ktoré evidence sú potrebné pre staging a ktoré pre production.

## 16. Signature oproti attestation

Signature je cryptographic envelope alebo statement viazaný na subject. **Attestation** je signed claim o subjecte, napríklad ako vznikol, aké dependencies obsahuje alebo aký scan absolvoval.

in-toto Attestation Framework používa Statement obsahujúci subject descriptors a predicate type. Predicate nesie domain-specific data, napríklad SLSA provenance alebo vulnerability scan result.

DSSE — Dead Simple Signing Envelope — podpisuje payload type a payload spôsobom, ktorý oddeľuje signature envelope od konkrétnej serialization semantics. Consumer musí overiť envelope aj schema predicate-u.

Validná attestation neznamená pravdivý claim. Dôvera závisí od identity attestor-a a procesu, ktorý evidence vytvoril.

## 17. Provenance a SBOM attestations

Provenance vysvetľuje, z akého source, build definitionu a builder contextu artifact vznikol. SBOM opisuje components a relationships v artifacte. Ide o rozdielne evidence types.

Attestation musí byť viazaná na rovnaký immutable digest ako nasadzovaný image. SBOM pre tag alebo pre source tree nemožno automaticky považovať za inventory final runtime image-u.

Policy môže vyžadovať:

- provenance od approved builder identity;
- source repository a revision z trusted namespace;
- build parameters bez unsafe external inputs;
- SBOM od approved generatora;
- predicate schema a version, ktorú consumer podporuje.

Ak artifact promotion zmení image manifest, napríklad pridá metadata alebo repackage-ne layers, pôvodná attestation nemusí patriť novému digestu.

## 18. OCI artifacts, subject a Referrers API

OCI image manifest alebo index môže reprezentovať aj non-image artifacts. `artifactType` opisuje typ artifactu a `subject` descriptor vytvára väzbu na iný manifest digest.

Signature, SBOM alebo provenance artifact môže mať `subject` ukazujúci na image digest. OCI Distribution Specification 1.1 definuje Referrers API, ktorým consumer získa related manifests pre daný subject a voliteľne ich filtruje podľa `artifactType`.

```text
image digest
├─ signature artifact
├─ provenance attestation
└─ SBOM artifact
```

Referrers väzba je discoverability mechanism, nie trust decision. Attacker s registry write permission môže pridať vlastný referrer. Consumer musí každý related artifact cryptographically a semantically overiť.

Registries bez Referrers API môžu používať fallback tag schema. Promotion tools musia zachovať related artifacts aj ich subject relationships.

## 19. Registry promotion, replication a garbage collection

Build-once-promote-many znamená presúvať alebo replikovať ten istý content digest medzi environments bez rebuild-u. Signatures a attestations musia zostať dostupné v cieľovom registry.

Nie každý copy tool automaticky prenesie referrers. Ak sa skopíruje iba image manifest a layers, production verification nenájde signature alebo SBOM.

Garbage collection a retention policy musia rozumieť related artifacts. Odstránenie tagu nemá neúmyselne odstrániť signature potrebnú na historical audit, pokiaľ subject digest stále patrí k retained release-u.

Replication môže meniť repository name, ale digest contentu zostáva rovnaký, ak sa manifest nemení. Identity policy musí rozhodnúť, či signature viazaná na source repository reference zostáva platná v destination namespace.

## 20. Digest pinning a deployment contract

Deployment manifest má používať image digest alebo admission controller musí tag resolve-nuť a uložiť verified digest deterministicky. Inak vzniká time-of-check/time-of-use gap.

```yaml
image: registry.example/payments@sha256:...
```

Digest pinning zaručí content identity, nie dôveryhodnosť. Stále treba signature a policy. Naopak, signature verification nad tagom bez pinningu môže overiť jeden digest a runtime neskôr stiahnuť iný.

Rollout a rollback history majú uchovávať digests. „Rollback na tag `stable`“ nie je reproducible recovery, ak tag medzičasom ukazuje inde.

## 21. Admission verification

Kubernetes admission alebo deployment controller môže fungovať ako PEP. Zachytí workload object, resolve-ne image reference, overí signature/attestations a aplikuje environment policy pred persistence alebo rolloutom.

Ordering je dôležitý. Mutating component môže zmeniť image po skoršej verification. Final validation musí overiť digest, ktorý zostáva v stored objecte.

Policy scope musí pokryť všetky image-bearing fields: init containers, ephemeral containers a custom workload CRDs, ak ich controller neskôr prekladá na Pods.

Admission neoveruje images spustené mimo Kubernetes ani už running workloads pri neskoršej revocation. Background audit a runtime inventory dopĺňajú request-time verification.

## 22. Failure semantics a availability

Verification závisí od registry, trust roots, certificate/transparency evidence, policy data a niekedy external services. Každá dependency potrebuje timeout a failure behavior.

Production admission môže fail-closed pri neznámej signature, ale outage verification service-u môže zablokovať všetky deployments vrátane incident recovery. Návrh potrebuje local cache, verification bundles, replicated roots alebo auditovaný break-glass.

Cache musí byť viazaná na:

- subject digest;
- signer/trust policy revision;
- required attestation set;
- verification result time;
- revocation alebo quarantine generation.

Cached allow podľa tagu alebo repository name je unsafe. Po policy change alebo key compromise treba cache invalidovať.

## 23. Key a identity rotation

Key rotation pridá nový trusted key a postupne odstráni starý. Počas overlapu môže policy akceptovať oba keys, ale musí vedieť rozlíšiť new releases od historical signatures.

Keyless identity rotation môže znamenať zmenu OIDC issuer claims, workflow path, repository rename alebo Fulcio trust roots. Identity patterny a tests sa musia aktualizovať koordinovane.

Revocation signing keyu neznamená automaticky, že každý historical artifact je malicious. Organization potrebuje exposure interval a evidence o tom, ktoré signatures vznikli počas compromise window.

Pre production možno zablokovať nové deployments affected artifacts, zatiaľ čo running workloads prejdú risk-based quarantine alebo controlled replacement.

## 24. Artifact revocation a quarantine

OCI signature standards typicky nevytvárajú univerzálne „unsign“ tlačidlo. Artifact content a historical signature môžu zostať immutable. Authorization policy musí pridať deny alebo quarantine state.

Quarantine record má byť viazaný na digest a obsahovať reason, scope, owner, timestamp a recovery condition. Mutable tag removal nestačí, pretože digest možno stále pullnuť priamo.

Enforcement points musia dostať quarantine update rýchlo. Revocation latency je čas medzi security decisionom a skutočným odmietnutím artifactu vo všetkých deployment paths.

## 25. Compromised signing key alebo workflow

Incident response začína zastavením ďalšieho signing-u a identifikáciou trust scope-u.

```text
zablokovať signing identity alebo key
→ zachovať KMS/OIDC/CI/transparency evidence
→ určiť compromise interval
→ enumerovať signed digests v intervale
→ zablokovať nové deployments alebo quarantine artifacts
→ rotovať keys, trust roots alebo workflow identity
→ opraviť source compromise a rebuildnúť artifacts
→ overiť, že stará identity už nie je trusted
→ pridať regression policy a monitoring
```

Ak bol compromised iba repository workflow, nie celý OIDC issuer, revocation má byť čo najpresnejšia. Global distrust issuer-u môže spôsobiť rozsiahly outage.

Re-signing rovnakého malicious digestu novým keyom problém nevyrieši. Artifact musí byť rebuildnutý z dôveryhodného source a builder pathu.

## 26. Kompletný production flow

Príklad bezpečného release-u:

1. Protected build workflow checkoutne immutable source revision.
2. Isolated builder vytvorí multi-platform image a provenance.
3. SBOM generator analyzuje final variants a vytvorí digest-bound SBOMs.
4. Testy a security gates vyhodnotia release evidence.
5. Protected release job získa short-lived OIDC identity a podpíše image index digest.
6. Signature, provenance a SBOM artifacts sa publikujú cez OCI subject/referrers model.
7. Promotion skopíruje image aj related artifacts do production registry bez rebuild-u.
8. Deployment manifest používa index digest.
9. Admission policy overí signer identity, issuer, subject, provenance builder a required SBOMs.
10. Decision log zaznamená policy revision a evidence digests.
11. Runtime inventory sleduje nasadené platform manifests a reaguje na quarantine.

Každá šípka má samostatnú trust boundary. Podpis na konci nemôže opraviť compromised source alebo builder; iba viaže release authority na konkrétny výsledok.

## 27. Troubleshooting verification

Postupuj od subject identity k policy:

```text
resolved tag a digest
→ index alebo platform manifest subject
→ signature discovery
→ signature payload
→ certificate/public-key chain
→ OIDC issuer a signer identity
→ transparency/bundle evidence
→ attestations a predicate schemas
→ policy revision
→ enforcement result
```

Ak signature „neexistuje“, over Referrers API, fallback tag schema, repository namespace a promotion behavior. Ak cryptography je validná, ale policy deny, porovnaj exact identity claims, issuer, workflow path a subject digest.

Pri multi-arch probléme zisti, či signer podpísal index alebo iba jednu variantu a ktorý digest runtime vybral. Pri historical verification over trusted roots a časové evidence v bundle-i.

Pri admission timeout-e rozlíš registry latency, external Rekor/Fulcio dependency, policy engine outage a local cache. Nemeň fail-closed na global fail-open bez scope-u a incident evidence.

## 28. Časté anti-patterny

**Podpisovanie tagu bez digest contractu.** Tag sa po verification môže presunúť.

**Akceptovanie ľubovoľného validného certificate-u.** Cryptographic validity sa zamieňa za signer authorization.

**Broad OIDC regex.** Attacker-controlled repository alebo branch spĺňa neukotvený pattern.

**Production signing v pull-request jobe.** Untrusted code získa trusted signing identity.

**Jeden shared long-lived key.** Compromise zasiahne všetky products a attribution je slabá.

**Copy image bez referrers.** Promotion stratí signature, SBOM alebo provenance.

**Admission verification bez digest pinningu.** Runtime môže pullnúť iný content než overený.

**Transparency log ako preventive control.** Log poskytuje evidence, ale nezabráni oprávnenému signerovi podpísať zlý artifact.

**Re-signing bez rebuild-u.** Nový podpis nemení compromised content.

## 29. Kontrolné otázky

1. Čo presne signature dokazuje a ktoré security vlastnosti nedokazuje?
2. Prečo je OCI tag nevhodný ako immutable signed subject?
3. Aký je rozdiel medzi image index digestom a platform manifest digestom?
4. Čo „keyless“ znamená a ktoré cryptographic keys stále existujú?
5. Prečo dôvera v celý OIDC issuer nestačí?
6. Aké roly majú Fulcio, Rekor a TUF trust metadata?
7. Ako sa líši cryptographic verification od authorization policy?
8. Prečo build provenance a release signature môžu pochádzať od rozdielnych identities?
9. Čo je attestation a ako sa líši od obyčajnej signature?
10. Ako OCI `subject` a Referrers API spájajú image so signatures a SBOMs?
11. Ako zabrániš time-of-check/time-of-use problému pri deployment-e?
12. Čo musí obsahovať verification cache key?
13. Ako zablokuješ compromised digest, keď historical signature zostáva validná?
14. Ako vyšetríš compromise signing workflowu bez global distrust všetkých artifacts?
15. Navrhni end-to-end image verification pre multi-platform production release.

## Glossary impact

Relevantné pojmy: image signing, signed subject, OCI image digest, image index, image manifest, platform manifest, tag-to-digest resolution, key-based signing, signing-key lifecycle, keyless signing, signing identity, Fulcio, Rekor, transparency log, verification bundle, trust root, TUF trust metadata, identity policy, signing workflow, release authority, signature, attestation, in-toto Statement, DSSE, provenance attestation, SBOM attestation, OCI artifact, artifact type, OCI subject, OCI Referrers API, referrers tag schema, digest pinning, admission verification, verification cache, offline verification, artifact revocation, artifact quarantine a signing-key compromise.

## Primárne zdroje

- [Sigstore security model](https://docs.sigstore.dev/about/security/)
- [Cosign signing containers](https://docs.sigstore.dev/cosign/signing/signing_with_containers/)
- [Cosign verifying signatures](https://docs.sigstore.dev/cosign/verifying/verify/)
- [Cosign self-managed keys](https://docs.sigstore.dev/cosign/key_management/signing_with_self-managed_keys/)
- [Sigstore custom components and trust roots](https://docs.sigstore.dev/cosign/system_config/custom_components/)
- [Cosign attestations](https://docs.sigstore.dev/cosign/verifying/attestation/)
- [OCI Image Manifest Specification](https://github.com/opencontainers/image-spec/blob/main/manifest.md)
- [OCI Image Index Specification](https://github.com/opencontainers/image-spec/blob/main/image-index.md)
- [OCI Distribution Specification](https://github.com/opencontainers/distribution-spec/blob/main/spec.md)
- [in-toto Attestation Framework specifications](https://in-toto.io/docs/specs/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: SBOM](sbom.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Policy as Code →](policy-as-code.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
