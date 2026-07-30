# GitOps secrets

GitOps secrets riešia dve požiadavky, ktoré sa nesmú zameniť. Secret intent má byť versionovaný, reviewovateľný a reprodukovateľný, no plaintext value nesmie byť dostupná každému readerovi Git repository, CI logu, controller cache alebo backupu. Git preto môže byť autoritou nad encrypted payloadom, external reference, key schema, rotation policy a target bindingom; secret provider zostáva autoritou nad credential generation a revocation.

```text
secret requirement a authority
→ encrypted payload alebo versioned provider reference
→ reviewed desired-state transition
→ scoped decrypt/fetch identity
→ target materialization
→ workload load alebo reload
→ provider-functional verification
→ overlap rotation a old-generation revocation
→ leak recovery a second rotation
```

`Secret exists` nie je acceptance verdict. Treba odlíšiť provider authority state, Git desired state, Kubernetes Secret state, mounted file alebo environment snapshot a generation, ktorú application process reálne používa.

## 1. Exact secret subject a plaintext boundaries

Secret subject obsahuje business purpose, provider alebo key authority, environment a tenant, logical name a data schema, encrypted file alebo provider object/version, recipients alebo KMS key, decryption/retrieval principal, target namespace a Secret, delivery mode, refresh a rotation policy, consumer reload behavior, audit a emergency revocation contract.

Tvrdenie `payments používa pv-43` môže opisovať štyri odlišné veci:

```text
provider authority: pv-43 active
Git desired:        reference alebo ciphertext pre pv-43
Kubernetes Secret:  bytes pv-43
running process:    loaded pv-42
```

Plaintext môže vzniknúť v developer/CI encryption workflowe, GitOps controller memory, Kubernetes API/etcd, kubelet alebo CSI path, Pod volume, process environment, application cache, diagnostic dump a provider client. Každá boundary potrebuje reader identity, retention, logging a revocation model. Encryption v Git-e nechráni plaintext po decryption ani workload, ktorý credential zbytočne kopíruje do logs.

## 2. Base64, private repository a history

Kubernetes Secret `data` používa base64 reprezentáciu, nie encryption. Reader repository alebo rendered manifestu ho dekóduje bez keyu. Private repository znižuje počet readerov, ale nemení secret na cryptographically protected object. Compromised account, CI token, search index, mirror alebo backup stále získa value.

Plaintext commit sa replikuje do Git objects, clones, pull-request diffs, CI workspaces, caches, notifications, mirrors a audit exports. Follow-up commit, ktorý file odstráni, neodvolá credential ani nezmaže všetky kópie. Incident response musí najprv revoke/rotate value, potom riešiť history cleanup a downstream copies. Hash plaintextu v logu môže byť tiež citlivý pri low-entropy secret-e; na koreláciu je vhodnejší provider-assigned version ID alebo opaque generation.

## 3. Encrypted-in-Git a external-reference model

Encrypted-in-Git model ukladá ciphertext spolu s desired state-om. Git diff a rollback identifikujú encrypted generation, no controller musí mať decryption authority. Compromise tejto identity alebo master keyu môže otvoriť všetky payloads v jej scope. Plaintext vzniká pri reconciliation a zvyčajne sa materializuje do Kubernetes Secretu.

```text
plaintext creation
→ encrypt pre environment recipient/KMS
→ ciphertext commit
→ Flux decrypt
→ Secret apply
→ workload reload
```

External-reference model necháva value v Vault, cloud secret manageri alebo inom providerovi. Git obsahuje provider object, property, version/alias, target mapping a refresh policy. Controller alebo workload používa runtime identity. Model zlepšuje central rotation a short-lived credentials, no pridáva availability a consistency boundary. Provider môže mať novú version, zatiaľ čo controller, Kubernetes Secret a process používajú starú.

Ani jeden model nie je automaticky lepší. Rozhoduje authority, availability, recovery, rotation cadence, tenant isolation a požadovaná reproducibility. Mutable alias ako `current` môže zmeniť effective secret bez Git commit-u; acceptance evidence preto musí zachytiť resolved provider generation.

## 4. SOPS envelope model a recipient policy

SOPS typicky generuje data encryption key, šifruje ním vybrané values a tento data key zašifruje pre age, PGP alebo KMS recipients. File obsahuje ciphertext, recipient metadata a integrity metadata, zatiaľ čo resource identity a nešifrované structural fields môžu zostať reviewovateľné.

```text
secret values
→ random data key
→ symmetric encryption
→ data key wrapped pre environment recipients
→ ciphertext + metadata v Git-e
```

`.sops.yaml` je policy input, nie neomylný enforcement. Developer alebo automation môže použiť nesprávny config či recipient. CI má preto kontrolovať, že sensitive fields sú encrypted, recipients patria správnemu environmentu/tenantu, KMS encryption context je správny a production payload nie je decryptovateľný staging keyom.

Flux Kustomization môže vykonať SOPS decryption cez controller identity alebo objektovo určenú service account/workload identity podľa podporovanej konfigurácie. Decryption principal je production credential. Má mať iba potrebný KMS/Vault decrypt scope, bez možnosti čítať unrelated tenant payloads. Shared age private key v `flux-system` vytvára jeden compromise, backup a rotation boundary pre všetky payloads, ktoré dokáže otvoriť.

## 5. Materialization, consumption a loaded generation

Kubernetes Secret update neznamená consumer convergence. Mounted Secret volumes sa môžu časom aktualizovať, ale application musí file znovu načítať. Environment variables sú process-start snapshot; zmena Secret objectu ich v existujúcom procese nezmení. SubPath mounts a application caches majú ďalšie refresh semantics.

Secret contract preto musí uviesť consumption mode a reload mechanizmus:

```text
Secret generation annotation pv-43
→ checksum alebo reloader vyvolá rollout
→ new Pods vzniknú po Secret update-e
→ application endpoint/metric hlási pv-43
→ provider audit potvrdí pv-43 usage
```

Generic Pod readiness nestačí. Application môže byť `Ready` a opakovane dostávať provider `401`, pretože probe neoveruje credential path. Safe observability publikuje logical secret ID, target resourceVersion, loaded generation a provider authentication result bez plaintextu.

## 6. Rotation ako distributed state machine

Bezpečná rotation nie je `update Secret` ani okamžitá revokácia old credentialu. Potrebuje overlap a explicitnú consumer convergence:

```text
create pv-43, pv-42 ostáva dočasne validný
→ update authoritative desired state
→ decrypt/fetch a materialize pv-43
→ trigger workload reload alebo rollout
→ verify všetky required consumers na pv-43
→ verify provider-functional success
→ revoke pv-42
→ negative test old generation
→ odstrániť old desired/reference material
```

Rotation states majú byť `Planned`, `NewGenerated`, `DesiredUpdated`, `Materialized`, `ConsumersConverging`, `NewVerified`, `OldRevoked` a `Closed`. Vedľajšie states sú `Blocked`, `Partial`, `Unknown` a `ReconciliationRequired`. Revocation pred convergence vytvára outage; ponechanie old value po convergence predlžuje exposure.

Rollback secretu nie je vždy prípustný. Provider môže old credential už revoke-nuť alebo delete-nuť. Obnovenie old Git ciphertextu potom vytvorí materialized, ale nefunkčný Secret. Recovery musí čítať provider authority, nie predpokladať, že Git history je kompletný rollback mechanismus.

## 7. One-writer authority a emergency changes

GitOps controller považuje Git desired state za authority. Manual patch target Secretu bez zmeny authoritative source vytvorí drift a ďalšia reconciliation ho môže vrátiť. Emergency workflow preto nesmie meniť iba live object a dúfať, že sa Git opraví neskôr.

Bezpečný break-glass path je:

```text
incident approval a scoped temporary identity
→ suspend alebo koordinovať reconciler pre exact subject
→ create provider generation
→ update authoritative Git/reference
→ materialize a reload
→ verify
→ resume reconciliation
→ revoke temporary identity
→ second drift/rotation test
```

Pri lost response-e sa najprv read-backne provider version, Git commit, Secret resourceVersion a workload generation. Blind retry môže vytvoriť druhú credential alebo prebiť novší rotation state.

## 8. Multi-tenancy, provider boundary a confused deputy

Tenant isolation musí byť zachovaná cez celý path:

```text
tenant Git source
→ Flux/Argo object
→ decrypt alebo retrieval identity
→ KMS/provider object
→ target namespace
→ workload service account
```

Namespace RBAC nestačí, ak shared controller role môže decryptovať všetky KMS keys alebo čítať arbitrary provider paths. Broad `ClusterSecretStore`, cross-namespace references a tenant-controlled `remoteRef.key` môžu z controllera urobiť confused deputy. Least privilege sa musí enforce-nuť v KMS alebo secret provider authorization, nie iba v portal form-e.

Backups a support bundles sú ďalší reader domain. Mixed-tenant etcd snapshot, controller Secret backup alebo debug export môže obísť runtime isolation. Recovery test má overiť funkčné získanie credentialu a audit correlation bez vypísania plaintextu.

## 9. Leak response a disaster recovery

Pri plaintext exposure sa credential okamžite považuje za compromised. Postup je preserve evidence bez ďalšieho šírenia, identifikovať provider object a consumer graph, vytvoriť new generation, convergence, revoke old, invalidate sessions/derived tokens a podľa potreby vyčistiť Git history, caches a mirrors. History rewrite je hygiene, nie revocation.

Encrypted-in-Git DR potrebuje retained ciphertext, decryption key/KMS availability, controller manifests a identity trust, target bootstrap a functional consumer test. External-provider DR potrebuje provider version retention, workload identity, SecretStore/reference desired state, target materialization a rozhodnutie, či historical credential môže byť znovu aktivovaný. Restore revoked credentialu bez explicitného security decisionu je recovery-induced vulnerability.

## 10. Connected incident `GITOPS-PAY-62`

Release `payments 9.1` používal SOPS-encrypted provider credential `pv-42`. Staging aj production payloady boli decryptovateľné jedným shared age private keyom v `flux-system`. Provider neskôr vytvoril `pv-43`, ale rotation nebola authoritative Git transition. On-call patchla Kubernetes Secret priamo, zatiaľ čo Git stále obsahoval ciphertext pre `pv-42`.

```text
Git desired:        pv-42 ciphertext
manual live Secret: pv-43
Flux reconcile:     obnoví pv-42
running processes:  startup snapshot pv-42
provider authority: pv-43 active, pv-42 revoked
```

Pods čítali Secret cez environment variables a neprebehol rollout. Provider revoke-ol `pv-42` pred consumer convergence. Flux teda správne opravil live drift späť na old desired state a následný Pod restart znovu načítal revoked credential. `61` provider calls zlyhalo a retry flow vytvoril `14` unknown outcomes.

Root cause nebola iba chýbajúca automatická rotácia. Rotation nemala jednu authority, overlap window, loaded-generation oracle ani provider-functional gate. Shared decryption key zväčšila blast radius a manual patch bojoval s Flux ownershipom.

## 11. Authoritative redesign a acceptance paths

Produkčný redesign používa environment-scoped KMS alebo Vault/OpenBao decryption identity. Provider vytvorí `pv-43` s overlapom, SOPS payload alebo external reference sa zmení v reviewed Git transitione, Flux materializuje Secret s generation metadata, checksum/reloader spustí rollout, application hlási loaded `pv-43` a provider audit potvrdí úspešné používanie. Až potom sa `pv-42` revoke-ne a negative test musí zlyhať.

Positive path dokazuje confidentiality aj function. Rotation path overí overlap a všetky consumer cohorts. Recovery path obnoví controller a target bez opätovnej aktivácie revoked value. Leak path revoke-ne credential pred history hygiene. Forbidden path odmietne plaintext/base64-only Git, shared cross-environment decryption key, broad provider path, manual dual writer, revocation pred convergence, false success podľa `Secret exists` a logs obsahujúce decrypted value.

## 12. Troubleshooting a kontrolné otázky

Pri authentication failure sa mapuje provider active/revoked generations, Git ciphertext/reference revision, decrypt/fetch principal a audit, target Secret resourceVersion/generation, Pod creation time, delivery mode, application-loaded generation, provider request evidence a rotation operation state. Prvá nezhoda určí, či zlyhala authority, decryption, materialization, reload alebo provider acceptance.

Kontrolné otázky: Prečo base64 nie je encryption? Kde vzniká plaintext v encrypted-in-Git modeli? Ako mutable provider alias mení reproducibility? Prečo Secret update nemení environment variables? Kedy možno revoke-nuť old credential? Ako sa emergency patch koordinuje s reconcilerom? Čo musí prejsť pri second rotation a DR teste?

## Glossary impact

Relevantné pojmy: secret subject, secret authority generation, encrypted-in-Git, external secret reference, SOPS recipient, decryption identity, plaintext boundary, materialized secret generation, workload-loaded generation, rotation overlap, consumer convergence, one-writer secret authority, confused deputy, revoked-generation restore a GitOps secret acceptance verdict.

## Primárne zdroje

- [Flux — Manage Kubernetes secrets with SOPS](https://fluxcd.io/flux/guides/mozilla-sops/)
- [Flux — Kustomization decryption](https://fluxcd.io/flux/components/kustomize/kustomizations/)
- [Flux — Workload identity](https://fluxcd.io/flux/installation/configuration/workload-identity/)
- [Flux — Security best practices](https://fluxcd.io/flux/security/best-practices/)
- [SOPS](https://getsops.io/)
- [Kubernetes — Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Application promotion](application-promotion.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Internal Developer Platform →](internal-developer-platform.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
