# GitOps secrets

GitOps secrets riešia konflikt medzi dvoma požiadavkami. Desired state má byť versionovaný, reviewovateľný a reprodukovateľný, ale secret value nesmie byť voľne čitateľná každému, kto môže čítať repository, CI log, controller artifact alebo Git history. Riešením nie je predstierať, že Secret uložený v base64 je šifrovaný. Potrebný je explicitný secret authority, encryption alebo external-reference model, decryption/retrieval identity a celý lifecycle od vytvorenia po revocation.

GitOps môže bezpečne riadiť secret intent, nie nevyhnutne plaintext value. Git môže obsahovať encrypted payload, reference na external secret manager, required key schema, rotation policy a workload binding. Plaintext vzniká až na definovanej runtime boundary a iba identities, ktoré ho potrebujú, majú dostať access.

## 1. Dominantný model

```text
application secret requirement
→ exact secret subject a authority boundary
→ creation alebo external provider generation
→ encrypted payload alebo versioned secret reference
→ reviewed Git desired-state transition
→ controller authentication a decrypt/fetch decision
→ Kubernetes Secret, volume alebo direct workload delivery
→ workload load/reload a functional verification
→ rotation, revocation, expiry a consumer convergence
→ leak response, audit a second-rotation closure
```

Secret acceptance verdict nemôže skončiť pri `Secret exists`. Musí dokázať, ktorá authority generation bola intended, ktorú generation controller materializoval, ktorú value workload skutočne načítal a či external provider považuje túto credential generation za aktívnu.

## 2. Exact secret subject

Secret subject zahŕňa:

- business purpose — napríklad provider API credential, database password alebo signing key;
- secret authority — systém, ktorý value vytvára, verziuje, rotuje a revokuje;
- environment, tenant a workload scope — komu value patrí a kde smie byť použitá;
- logical name a key schema — názov Secretu, required data keys, formát a encoding;
- encrypted-file alebo external-provider identity — path, object ID, version, stage alebo alias;
- encryption recipients alebo KMS key IDs — kto môže decryptovať encrypted payload;
- retrieval/decryption principal — controller alebo workload identity;
- materialization target — Kubernetes Secret, CSI volume, file, environment variable alebo direct API fetch;
- refresh/rotation semantics — period, trigger, overlap, expiry a revocation order;
- consumer reload behavior — či workload sleduje file, používa SDK cache alebo potrebuje restart;
- audit a leak-response contract — logs, ownership, emergency revocation a Git-history cleanup.

Tvrdenie `payments používa secret pv-43` je neúplné, ak Kubernetes Secret už obsahuje `pv-43`, ale running Pods stále majú v environment variables načítané `pv-42`.

## 3. Secret authority, desired state a materialized state

Treba rozlišovať tri vrstvy:

```text
secret authority state
→ provider/KMS/Vault generation, active/revoked versions a leases

Git secret desired state
→ encrypted payload alebo reference, policy a target declaration

materialized/effective secret state
→ Kubernetes Secret bytes, mounted file a value načítaná workloadom
```

Git môže správne deklarovať reference na provider version `AWSCURRENT`, ale External Secrets controller môže byť bez credentials a target Secret zostane stale. Kubernetes Secret môže byť aktualizovaný, ale application process používa starú environment snapshot. Provider môže starú credential revokovať skôr, než všetci consumers načítajú novú.

Secret lifecycle je preto distributed state transition, nie update jedného YAML field-u.

## 4. Prečo base64 nie je ochrana

Kubernetes Secret manifest:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: provider-api
type: Opaque
data:
  token: c2VjcmV0LXZhbHVl
```

`data` je base64 encoding, ktorý rieši bezpečný transport arbitrary bytes v YAML/JSON. Každý s read accessom ho vie dekódovať. Plaintext Secret v Git-e sa replikuje do:

- local clones a developer backups;
- pull request diffs a email notifications;
- CI workspaces, caches a artifacts;
- search indexov;
- Git object history aj po odstránení z current branch;
- forks, mirrors a audit exports.

Repository visibility sama osebe nie je cryptographic control. Private repository znižuje exposure, ale kompromitovaný account, token, runner alebo backup stále odhalí plaintext.

## 5. Dva hlavné GitOps modely

### Encrypted secret value v Git-e

Repository obsahuje ciphertext. GitOps controller ho pri reconciliation dešifruje a vytvorí Kubernetes Secret.

```text
plaintext creation
→ encrypt pre environment recipients/KMS
→ ciphertext commit
→ controller decrypt
→ target Secret apply
```

Výhody:

- encrypted desired value je versionovaná spolu s application configom;
- rollback a diff môžu identifikovať secret generation;
- source je dostupný aj pri dočasnom výpadku external secret API, ak KMS/decryption funguje.

Riziká:

- decryption identity má prístup k plaintextu všetkých payloads vo svojom scope;
- ciphertext a metadata zostávajú v Git history;
- key compromise môže spätne odhaliť všetky stále dešifrovateľné versions;
- rotation vyžaduje commit a consumer convergence;
- controller memory a Kubernetes Secret sa stávajú plaintext boundaries.

### External secret reference v Git-e

Repository obsahuje declaration, ktoré provider object/key/version sa má načítať. Controller alebo workload používa workload identity na read.

```text
Git ExternalSecret/reference
→ controller authorization
→ provider fetch
→ Kubernetes Secret alebo direct mount
```

Výhody:

- plaintext value nemusí byť v Git-e ani encrypted formou;
- provider môže centralizovať generation, rotation, audit a revocation;
- short-lived credentials a leases sú prirodzenejšie.

Riziká:

- provider availability a IAM sú runtime dependencies;
- broad SecretStore môže umožniť tenantovi načítať cudzie secrets;
- reference na mutable alias môže meniť effective value bez Git commit-u;
- target Secret a consumer môžu zostať stale;
- provider restore alebo version deletion môže znemožniť rollback.

Oba modely môžu byť správne. Voľba závisí od authority, availability, rotation cadence, audit requirements a blast radius.

## 6. SOPS interný model

SOPS šifruje values v YAML, JSON, ENV, INI alebo binary file. Typicky vytvorí náhodný data key, zašifruje ním secret values a data key zašifruje pre jedného alebo viacerých master-key recipients, napríklad age identity alebo cloud KMS key.

Zjednodušený model:

```text
plaintext values
→ random data encryption key
→ symmetric encryption values
→ encrypt data key pre KMS/age recipients
→ store ciphertext + recipient metadata + integrity MAC
```

Výhoda envelope modelu je, že veľký file sa nešifruje priamo každým KMS keyom. KMS alebo age chráni malý data key. SOPS zároveň ponecháva vybrané structural fields čitateľné, aby Git diff ukázal resource identity a schema.

Príklad `.sops.yaml`:

```yaml
creation_rules:
  - path_regex: clusters/production/.*\.enc\.yaml$
    kms:
      - arn: arn:aws:kms:eu-central-1:123456789012:key/prod-payments
        context:
          Environment: production
          Service: payments
    encrypted_regex: '^(data|stringData)$'
```

Creation rule je policy input. Ak developer použije iný config alebo explicitný CLI recipient, môže ciphertext zašifrovať pre nesprávny key. CI má validovať recipients, encryption context, encrypted fields a neprítomnosť plaintext patterns.

## 7. SOPS key ownership a rotation

SOPS rozlišuje rotation data key-u a zmenu master-key recipients.

### Data-key rotation

`sops rotate` vytvorí nový data key a znovu zašifruje file content. Je vhodná po periodickej rotation alebo pri podozrení na exposure data key-u.

### Recipient update

`sops updatekeys` zosúladí file recipients s `.sops.yaml`. Pri odobratí človeka alebo environment key-u nestačí iba zmeniť config; existujúce files musia byť re-encrypted/update-nuté.

Dôležitá hranica:

```text
remove recipient from future creation rule
≠ recipient už nevie decryptovať historický ciphertext
```

Ak mal actor private age key alebo KMS decrypt permission a historické files zostávajú dostupné, môže dešifrovať versions, ktoré boli preň zašifrované. Incident response môže vyžadovať secret value rotation, nie iba recipient update.

## 8. Flux SOPS decryption

Flux `Kustomization` môže deklarovať:

```yaml
spec:
  decryption:
    provider: sops
    serviceAccountName: payments-sops
```

Pri cloud KMS môže controller použiť service-account-bound workload identity. Decryption authorization potom môže byť viazaná na production namespace a konkrétny KMS key.

Pipeline:

```text
source-controller artifact
→ kustomize-controller path
→ SOPS metadata parse
→ workload identity token
→ KMS decrypt data key
→ plaintext manifest in memory
→ build/validation
→ Kubernetes Secret apply
```

Failure modes:

- wrong KMS key alebo encryption context;
- workload identity trust policy nepovoľuje service account;
- KMS outage/throttling;
- encrypted regex nechala citlivý field plaintext;
- key policy povoľuje príliš broad decrypt;
- shared global credential obchádza tenant boundary;
- controller log alebo debug output vypíše decrypted content;
- decrypted Secret sa aplikuje do wrong namespace.

Decryption identity má byť chápaná ako production secret-reader principal, nie ako technický detail controllera.

## 9. Sealed Secrets model

Sealed Secrets používa public-key encryption. Developer alebo CI zašifruje Secret pre controller public certificate a commitne `SealedSecret`. Controller s private keyom v clusteri ho dešifruje a vytvorí Kubernetes Secret.

```text
cluster/controller public key
→ seal plaintext pre name/namespace scope
→ commit SealedSecret
→ controller private-key decrypt
→ target Secret
```

Scope môže kryptograficky viazať ciphertext na name a namespace. Copy do iného namespace potom nemá byť automaticky decryptovateľná.

Dôležité trade-offy:

- private key je cluster recovery-critical asset;
- loss private key-u môže znemožniť decryption existing manifests;
- compromise private key-u môže odhaliť historické ciphertexts dostupné útočníkovi;
- certificate renewal neznamená automatickú re-encryption všetkých manifests;
- Git diff nad ciphertextom neukazuje semantic secret value change;
- target Secret rotation stále potrebuje workload reload.

Sealed Secrets rieši encryption-to-cluster, nie central secret authority, dynamic lease alebo automatic provider revocation.

## 10. External Secrets Operator model

`ExternalSecret` opisuje, čo sa má načítať a ako vytvoriť target Kubernetes Secret.

```yaml
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata:
  name: provider-api
  namespace: payments
spec:
  refreshPolicy: Periodic
  refreshInterval: 5m
  secretStoreRef:
    kind: SecretStore
    name: payments-provider
  target:
    name: provider-api
    creationPolicy: Owner
  data:
    - secretKey: token
      remoteRef:
        key: prod/payments/provider
        property: token
        version: pv-43
```

Reconciliation:

```text
ExternalSecret spec
→ SecretStore resolution
→ provider authentication
→ remote object/version fetch
→ transform/template
→ target Secret create/update
→ status refreshTime/synced version
```

`SecretStore` je namespaced authority boundary. `ClusterSecretStore` je cluster-wide a môže zväčšiť blast radius. Store credentials alebo workload role musia obmedzovať provider paths, nie iba Kubernetes namespace.

## 11. ExternalSecret refresh policies

### `Periodic`

Controller periodicky číta provider a aktualizuje target. Hodí sa pre pravidelnú rotation, ale vytvára provider dependency a delay do `refreshInterval`.

### `OnChange`

Target sa aktualizuje pri zmene ExternalSecret metadata/spec. Provider value môže byť zmenená bez refreshu, kým Git alebo metadata nevytvoria nový trigger. Je vhodné, keď rotation má byť explicitný desired-state transition.

### `CreatedOnce`

Controller vytvorí secret a bežne ho neobnovuje. Recreate ExternalSecretu však resetuje status a môže value znovu vygenerovať alebo prepísať. Pri bootstrap credentials, ktoré application uloží do vlastnej databázy, môže regenerácia vytvoriť permanentný mismatch.

Refresh policy nie je iba performance setting. Určuje consistency model medzi provider authority a target Secretom.

## 12. Target creation a deletion semantics

Target policy rozhoduje, kto vlastní Kubernetes Secret a čo sa stane pri delete alebo conflict-e.

Questions:

- vytvorí operator celý Secret alebo merge-ne iba vybrané keys?
- odstráni sa target pri delete ExternalSecretu?
- smie iný controller meniť rovnaké keys?
- čo sa stane, ak provider property zmizne?
- má stale target zostať dostupný alebo sa odstrániť?
- je target immutable?

Owner reference a creation policy môžu uľahčiť cleanup, ale accidental prune ExternalSecretu môže následne odstrániť production Secret. `Orphan` znižuje delete coupling, ale môže ponechať stale credential bez ownera. Potrebný je explicitný decommission a failure policy.

## 13. Mutable provider alias vs. pinned version

Reference môže ukazovať na mutable alias ako `AWSCURRENT` alebo na exact version.

```text
Git unchanged
provider alias AWSCURRENT: pv-42 → pv-43
→ effective secret changes bez Git commit-u
```

To môže byť zámerné pri automated rotation. Git potom nie je authority nad exact value, ale nad retrieval policy. Acceptance evidence musí zachytiť resolved provider version a rotation event.

Pinned version zlepšuje reproducibility a staged rollout, ale vyžaduje Git promotion pri každej rotation a provider musí version udržať. Pri emergency revocation môže byť pinned old version okamžite neplatná.

## 14. Workload identity a secret-zero problem

Controller potrebuje credential na Git, KMS alebo external secret provider. Uložiť long-lived cloud access key do Kubernetes Secretu iba presúva secret-zero problém.

Preferovaný model:

```text
Kubernetes ServiceAccount
→ projected OIDC token
→ cloud IAM trust evaluation
→ short-lived role credentials
→ scoped KMS/secret read
```

Workload identity znižuje potrebu static keys a umožňuje viazať access na namespace/service account. Stále potrebuje:

- issuer a audience validation;
- trust policy bez wildcardov;
- provider resource restrictions;
- token/credential TTL;
- audit correlation;
- fail-closed behavior pri identity error.

Ak controller beží ako cluster-admin a používa jednu cloud role pre všetky tenants, Kubernetes RBAC segmentation sama neochráni provider secrets.

## 15. Kubernetes Secret boundary

Po decryption alebo fetchi sa plaintext často uloží do Kubernetes Secretu. Ochrana potom závisí od:

- API authorization a RBAC;
- admission a namespace isolation;
- etcd encryption at rest;
- control-plane backups;
- audit logs;
- node/kubelet access;
- container runtime a process isolation;
- debug, exec a ephemeral-container permissions.

Kubernetes Secret nie je automaticky end-to-end encrypted pred cluster administrators alebo workload node boundary. Encryption at rest chráni etcd bytes, ale API server ich legitímne dešifruje oprávnenému readerovi.

## 16. Workload consumption a reload

Secret môže byť konzumovaný:

### Environment variable

Value sa kopíruje do process environment pri container start-e. Secret update nezmení existujúci process. Potrebný je rollout alebo application restart.

### Mounted Secret volume

Kubelet periodicky aktualizuje projected files. Application však musí file znovu čítať alebo watchovať. Otvorený file descriptor, internal cache alebo library behavior môže držať starú value.

### CSI/provider volume

Driver môže mountovať provider content bez trvalého Kubernetes Secretu. Rotation behavior závisí od drivera a application reloadu.

### Direct SDK/API fetch

Application číta provider sama a môže používať cache/lease renewal. Znižuje plaintext v Kubernetes API, ale každá application implementuje identity, retry, refresh a failure behavior.

Secret rotation je úspešná až keď všetci relevantní consumers používajú new generation a old generation je bezpečne revokovaná.

## 17. Rotation state machine

Bezpečná credential rotation často používa overlap:

```text
create new generation N+1
→ authorize N aj N+1
→ materialize N+1
→ roll/reload consumers
→ verify all consumers on N+1
→ revoke N
→ observe auth failures
→ delete/expire N
```

Pri key pair alebo signing keys môže verifier potrebovať old public key počas validity starých tokens. Pri database passworde server môže dočasne podporovať dual credentials. Nie každý provider overlap podporuje; vtedy je potrebný coordinated cutover a bounded outage plan.

Rotation interval bez consumer-generation telemetry vytvára false confidence. Potrebný je endpoint, metric alebo audit dokazujúci, ktorou key/credential generation workload request podpísal alebo použil.

## 18. Revocation a leak response

Ak plaintext unikne do Git-u:

```text
detect leak
→ classify secret scope a provider authority
→ revoke/disable credential
→ rotate dependent secrets
→ identify accessed clones/logs/artifacts
→ remove from current files
→ rewrite history iba ako exposure reduction
→ invalidate caches/mirrors where possible
→ verify consumers on new generation
→ root-cause a preventive control
```

Odstránenie commit-u alebo history rewrite nie je náhrada za revocation. Secret mohol byť už skopírovaný. History cleanup znižuje future accidental exposure a scanner noise, ale credential sa musí považovať za compromised.

Pri encryption-key compromise treba vyhodnotiť, ktoré historical ciphertexts sú dešifrovateľné a ktoré secret values sú ešte aktívne.

## 19. Logging, diff a observability

Secret system potrebuje evidence bez plaintextu.

Bezpečné fields:

- secret logical ID a version/generation;
- ciphertext digest;
- provider object ARN/path hash;
- controller operation ID;
- refresh timestamp a result;
- target Secret resourceVersion;
- workload loaded generation;
- revocation status;
- KMS key ID a audit request ID.

Nebezpečné fields:

- raw values;
- complete rendered Secret manifests;
- environment dumps;
- provider API responses;
- templating errors obsahujúce secret;
- debug command history.

Redaction musí byť applied pred log persistence. Hash secret value pre correlation môže byť tiež citlivý pri low-entropy secrets a umožniť offline guessing; lepšie je používať provider-assigned version ID.

## 20. Multi-tenancy

Tenant isolation musí pokryť celý path:

```text
tenant Git source
→ Flux/Argo object
→ decryption/retrieval identity
→ provider path
→ target namespace
→ workload service account
```

Chyby:

- cross-namespace reference na shared decryption Secret;
- ClusterSecretStore s broad provider role;
- tenant môže zvoliť arbitrary remote key path;
- controller používa cluster-wide KMS decrypt;
- target Secret možno vytvoriť v inom namespace;
- catalog/portal ukáže secret metadata cudziemu tenantovi;
- backup alebo support bundle mieša namespaces.

Least privilege musí byť enforced na provider boundary, nie iba v UI alebo Git reviewe.

## 21. Backup, restore a disaster recovery

Secret recovery sa líši podľa modelu.

### Encrypted-in-Git

Potrebné sú:

- Git history;
- decryption key/KMS availability;
- controller manifests a identity trust;
- target cluster bootstrap;
- test, že historical required payload sa dá decryptovať.

### External provider

Potrebné sú:

- provider backup/version retention;
- IAM a workload identity restore;
- SecretStore/ExternalSecret desired state;
- target Secret reconstruction;
- decision, či restored old credential je ešte validná.

### Sealed Secrets

Potrebný je controller private key backup a secure restore. Nový cluster s novým keyom existujúce SealedSecrets neotvorí bez re-encryption alebo old key-u.

DR test nemá vypisovať plaintext. Má overiť, že test workload získa credential, autentizuje sa a audit koreluje expected version.

## 22. Connected incident `GITOPS-PAY-62`

Secret contract mal byť:

```text
SOPS-encrypted provider credential pv-42
→ production-scoped KMS decrypt
→ Kubernetes Secret provider-api
→ Pod rollout
→ application reports loaded pv-42
→ rotate to pv-43 with overlap
→ verify consumers
→ revoke pv-42
```

Skutočnosť:

- ciphertext bol zašifrovaný pre shared age recipient;
- private age key bol uložený v `flux-system/sops-age` a broad kustomize-controller ho používal pre staging aj production;
- production Secret obsahoval `pv-42`;
- emergency operator vytvoril `pv-43` a zmenil Secret, ale neexistoval rollout trigger;
- running Pods používali environment variable snapshot `pv-42`;
- provider revokoval `pv-42` pred consumer convergence;
- Flux health check videl healthy Deployment a existujúci Secret;
- LaunchPad nemal loaded-secret-generation signal.

State:

```text
Git encrypted desired: ciphertext for pv-42
Kubernetes Secret:     pv-43 po manual patch
Flux next reconcile:   obnovil pv-42 z Git-u
running processes:     pv-42
provider authority:    pv-43 active, pv-42 revoked
```

Manual patch a GitOps reconciliation vytvorili oscillation. On-call videla, že Secret má chvíľu `pv-43`, ale Flux ho vrátil na encrypted desired `pv-42`. Následný Pod restart načítal opäť revoked credential.

### Secret root cause

Rotation nebola desired-state transition a nemala dual-generation consumer convergence. Shared decryption key zväčšila blast radius, manual target patch bojoval s Flux ownershipom a acceptance nekontrolovala loaded/provider generation.

### Redesign

```text
provider creates pv-43 with overlap
→ SOPS file re-encrypted cez production KMS recipient
→ PR validates recipients a ciphertext-only fields
→ Flux production service account decrypts
→ target Secret generation annotation pv-43
→ checksum/secret-reloader triggers rollout
→ application endpoint reports pv-43
→ provider audit confirms pv-43 use by all Pods
→ revoke pv-42
→ negative auth test
→ remove old encrypted payload/version
```

Alternatívny design s External Secrets používa exact provider version `pv-43`, production-scoped SecretStore role a `OnChange` promotion. V oboch prípadoch je consumer convergence explicitná.

## 23. GitOps secret acceptance verdict

Secret design je prijatý, keď:

- secret authority, scope, schema a lifecycle sú explicitné;
- Git neobsahuje plaintext ani base64-only sensitive value;
- encrypted payload alebo external reference má jasný source-of-truth contract;
- SOPS/Sealed Secrets/provider keys a recipients sú environment/tenant scoped;
- decryption/retrieval používa short-lived workload identity a least privilege;
- provider version resolution a mutable alias behavior sú observable;
- target creation, merge, deletion a immutable semantics sú explicitné;
- Kubernetes RBAC, etcd encryption, backups a node access zodpovedajú threat modelu;
- workload reload behavior je známy a testovaný;
- rotation používa overlap alebo coordinated cutover a consumer-generation evidence;
- revocation predpokladá possible disclosure a nečaká na Git cleanup;
- logs, errors, diffs a support bundles neobsahujú plaintext;
- backup/restore obnoví secret functionality bez uncontrolled disclosure;
- GitOps reconciliation a emergency rotation nemajú dual-writer oscillation;
- KMS/provider outage, expired lease, wrong recipient, missing property, stale target, Pod non-reload, controller restart a second-rotation tests prejdú;
- cross-tenant decrypt/read, plaintext commit, revoked credential reuse a false-Secret-ready outcomes sú odmietnuté.

## 24. Troubleshooting flow

```text
Workload sa nevie autentizovať alebo používa wrong secret generation
→ exact workload/environment/secret subject
→ provider authority active/revoked versions
→ Git encrypted payload alebo external reference revision
→ controller decryption/retrieval identity
→ KMS/provider audit result
→ ExternalSecret/Kustomization observed generation
→ target Secret resourceVersion + generation metadata
→ Pod creation time a consumption mode
→ loaded application generation
→ provider request audit
→ writer/rotation timeline
→ authoritative rotation/recovery + second refresh
```

## 25. Anti-patterny

### Secret je v private Git-e, takže je bezpečný

Private access nie je encryption a Git history sa replikuje do clones, CI a backups.

### Base64 je dostatočné

Base64 je reversible encoding bez secret key-u.

### SOPS vyrieši celý secret lifecycle

SOPS chráni repository payload. Nevyrieši target RBAC, workload reload, provider revocation ani consumer convergence.

### Shared decryption key zjednoduší operations

Zjednoduší bootstrap, ale spája tenant/environment blast radius a komplikuje revocation.

### External Secrets znamená, že Secret nie je v clusteri

Ak operator vytvára Kubernetes Secret, plaintext v clusteri stále existuje. Pri CSI/direct fetch modeli môže byť hranica iná.

### Secret sa zmenil, application ho používa

Nie pri environment variables a nie pri application cache bez reloadu.

### Emergency patchneme Secret

Ak GitOps controller vlastní target, patch môže byť revertovaný. Emergency path musí koordinovať suspension alebo authoritative update.

### History rewrite odstránilo incident

Nie. Compromised credential treba revokovať a rotovať.

## 26. Kontrolné otázky

1. Ako sa secret authority state líši od Git desired a effective workload secret state-u?
2. Prečo base64 nechráni Secret v Git-e?
3. Aké sú trade-offy encrypted-in-Git a external-reference modelu?
4. Ako SOPS envelope encryption používa data key a master recipients?
5. Čo je rozdiel medzi SOPS data-key rotation a recipient update?
6. Prečo je Flux decryption service account production secret-reader identity?
7. Aké recovery riziko má Sealed Secrets private key?
8. Ako ExternalSecret refresh policy mení consistency model?
9. Prečo mutable provider alias môže meniť effective state bez Git commit-u?
10. Ako workload identity rieši secret-zero problém a kde má limity?
11. Prečo update Kubernetes Secretu nemusí zmeniť running process?
12. Ako vyzerá bezpečná overlap rotation?
13. Čo treba urobiť po plaintext leaku do Git-u?
14. Ako sa multi-tenant isolation presadzuje na provider path boundary?
15. Prečo `GITOPS-PAY-62` po manual patchi znovu načítal revoked `pv-42`?
16. Čo musí preukázať second-rotation test po controller restarte?

## Glossary impact

Relevantné pojmy: GitOps secret subject, secret authority, secret desired state, materialized secret state, encrypted-in-Git secret, external secret reference, SOPS data key, SOPS recipient, decryption identity, SealedSecret, ExternalSecret, SecretStore, ClusterSecretStore, refresh policy, secret materialization, loaded secret generation, secret overlap rotation, consumer convergence, secret-zero problem, secret revocation a GitOps secret acceptance verdict.

## Primárne zdroje

- [Kubernetes — Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
- [Kubernetes — Encrypting Confidential Data at Rest](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/)
- [SOPS — Official Repository and Documentation](https://github.com/getsops/sops)
- [Flux — Manage Kubernetes Secrets with SOPS](https://fluxcd.io/flux/guides/mozilla-sops/)
- [Flux — Kustomization Decryption](https://fluxcd.io/flux/components/kustomize/kustomizations/#decryption)
- [Sealed Secrets — Official Repository](https://github.com/bitnami-labs/sealed-secrets)
- [External Secrets Operator — ExternalSecret](https://external-secrets.io/latest/api/externalsecret/)
- [External Secrets Operator — SecretStore](https://external-secrets.io/latest/api/secretstore/)
- [External Secrets Operator — AWS Secrets Manager](https://external-secrets.io/latest/provider/aws-secrets-manager/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Application promotion](application-promotion.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Internal Developer Platform →](internal-developer-platform.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
