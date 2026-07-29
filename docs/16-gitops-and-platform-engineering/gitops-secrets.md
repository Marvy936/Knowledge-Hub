# GitOps secrets

GitOps secrets riešia konflikt medzi dvoma požiadavkami. Desired state má byť versionovaný, reviewovateľný a reprodukovateľný, ale secret value nesmie byť voľne čitateľná každému, kto môže čítať repository, CI log, controller artifact alebo Git history. Riešením nie je predstierať, že Secret uložený v base64 je šifrovaný. Potrebný je explicitný secret authority, encryption alebo external-reference model, decryption/retrieval identity a celý lifecycle od vytvorenia po revocation.

GitOps môže bezpečne riadiť secret intent, nie nevyhnutne plaintext value. Git môže obsahovať encrypted payload, reference na external secret manager, required key schema, rotation policy a workload binding. Plaintext vzniká až na definovanej runtime boundary a iba identities, ktoré ho potrebujú, majú dostať access.

## 1. Dominantný model

Secret lifecycle prechádza viacerými authority a plaintext boundaries. Model preto sleduje nielen to, kde je value deklarovaná, ale aj kto ju smie vytvoriť, decryptovať alebo načítať a kedy je stará generation skutočne nepoužiteľná.

Každá transition vytvára odlišný failure mode: Git môže obsahovať správny ciphertext, controller nemusí dostať KMS access, target Secret môže zostať stale a running process môže držať starú value aj po úspešnom update-e Kubernetes objectu.

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

Exact subject oddeľuje logical secret purpose od konkrétnej credential generation a jej consumers. Bez neho sa provider version, Git payload, Kubernetes Secret a process-loaded value môžu javiť ako jeden stav, hoci každý z nich má inú identity a lifecycle.

Rozmery subjectu spolu určujú, kto je autorita, kde môže vzniknúť plaintext, aký je tenant a environment scope a podľa čoho sa rotation považuje za dokončenú. Vynechanie ktoréhokoľvek rozmeru vytvára blind spot pri revocation alebo incident recovery.

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

Base64 mení textovú reprezentáciu bytes, nie ich confidentiality. Reader nepotrebuje secret key ani permission k ďalšiemu systému; stačí mu repository content a štandardný decoder.

Riziko sa násobí tým, že Git a delivery tooling vytvárajú viac trvalých kópií. Každý clone, diff, cache alebo export rozširuje reader graph a môže prežiť odstránenie value z current branch-e.

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

- **Local clones a developer backups** — kopírujú secret bytes mimo central repository controls a môžu zostať na unmanaged diskoch aj po odstránení current file-u.
- **Pull request diffs a notifications** — distribuujú value reviewerom, botom a email systems, ktoré majú vlastnú retention a access policy.
- **CI workspaces, caches a artifacts** — môžu plaintext uložiť na runner disk alebo do dlhodobo dostupného artifact store-u s širším reader scope-om.
- **Search indexes** — extrahujú text pre full-text query a môžu sprístupniť secret actorom, ktorí nemajú priamy clone access.
- **Git object history** — zachováva blob v reachable alebo reflog/mirror history aj po odstránení z current tree-u, takže bežný follow-up commit exposure neuzatvorí.
- **Forks, mirrors a audit exports** — vytvárajú ďalšie administratívne domains, v ktorých sa deletion a access revocation vykonávajú nezávisle.

Repository visibility sama osebe nie je cryptographic control. Private repository znižuje exposure, ale kompromitovaný account, token, runner alebo backup stále odhalí plaintext.

## 5. Dva hlavné GitOps modely

Oba modely versionujú secret intent, ale authority a availability umiestňujú na inú boundary. Encrypted-in-Git drží ciphertext spolu s application desired state-om a potrebuje decryption key pri reconciliation; external reference drží value v providerovi a potrebuje provider identity a availability pri refreshi.

Voľba preto nie je súboj nástrojov. Je to rozhodnutie o reprodukovateľnosti, runtime dependency, rotation cadence, audit authority a blast radius, pričom v oboch prípadoch treba samostatne vyriešiť Kubernetes a workload plaintext lifecycle.

### Encrypted secret value v Git-e

Ciphertext je súčasťou immutable desired generation, takže Git diff a rollback dokážu identifikovať jeho zmenu bez zverejnenia plaintextu. Decryption však presúva vysokú dôveru na controller identity a key management: kto môže otvoriť payload, môže potenciálne čítať všetky secrets vo svojom scope.

Versioning zlepšuje audit a offline reproducibility, ale nemení fakt, že plaintext vzniká v controller memory a zvyčajne aj v Kubernetes API. Preto sa repository encryption musí doplniť runtime RBAC, key rotation, redaction a consumer convergence.

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

External-reference model ponecháva value a authoritative versions v secret providerovi. Git deklaruje retrieval policy a target mapping, zatiaľ čo controller alebo workload resolve-ne current alebo pinned provider generation pomocou runtime identity.

Model centralizuje rotation a revocation, ale pridáva distributed consistency problém. Provider, ExternalSecret status, Kubernetes Secret a running process môžu každý ukazovať inú generation a mutable provider alias môže zmeniť effective value bez nového Git commit-u.

Repository obsahuje declaration, ktoré provider object/key/version sa má načítať. Controller alebo workload používa workload identity na read.

```text
Git ExternalSecret/reference
→ controller authorization
→ provider fetch
→ Kubernetes Secret alebo direct mount
```

Výhody:

- **No value payload in Git** — repository drží iba logical provider reference a target mapping, takže compromise Git readera priamo neodhalí credential bytes.
- **Central provider authority** — provider priraďuje versions, vykonáva rotation a revocation a produkuje audit events nad jedným authoritative lifecycle-om.
- **Short-lived credentials a leases** — môžu byť generované alebo obnovované providerom bez commitu každej ephemeral value do Git history.

Riziká:

- **Provider availability a IAM dependency** — reconciliation alebo workload refresh zlyhá, ak external API, network, workload identity alebo authorization nie sú dostupné.
- **Broad SecretStore scope** — tenant-controlled ExternalSecret môže zneužiť shared provider role na čítanie pathu mimo svojho namespace alebo business boundary.
- **Mutable provider alias** — alias ako `current` môže resolve-nuť novú version bez Git change-u, takže exact effective generation musí byť zachytená v runtime evidence.
- **Stale materialization alebo consumer** — provider už môže mať new version, zatiaľ čo controller, Kubernetes Secret alebo application cache stále používajú old value.
- **Provider retention boundary** — deleted alebo unavailable historical version znamená, že Git reference sama nedokáže obnoviť predchádzajúcu credential generation.

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

SOPS decryption je samostatná trust transition medzi source artifactom a final manifestom. Controller najprv musí získať workload identity, KMS alebo age mechanismus musí autorizovať otvorenie data key-u a až potom môže build pokračovať s plaintextom v memory.

Failure list preto pokrýva odlišné boundaries: cryptographic identity, cloud authorization, availability, encryption selection, logging a target placement. Úspešný Git fetch nevylučuje ani jednu z nich.

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

- **Wrong KMS key alebo encryption context** — ciphertext je validný, ale cryptographic authorization subject nezodpovedá key policy alebo additional authenticated contextu.
- **Workload-identity trust mismatch** — projected token je vydaný, no cloud role odmietne namespace, service account, issuer alebo audience a controller data key neotvorí.
- **KMS outage alebo throttling** — source artifact zostáva dostupný, ale render nemôže vzniknúť a aggressive retry môže zosilniť provider pressure.
- **Incomplete encrypted-field selection** — nesprávny `encrypted_regex` ponechá citlivú value čitateľnú v Git-e aj napriek tomu, že file obsahuje SOPS metadata.
- **Broad decrypt policy** — shared controller alebo compromised tenant môže otvoriť ciphertext iného environmentu, hoci Kubernetes target RBAC vyzerá oddelene.
- **Shared global private credential** — jeden age key alebo static cloud key spája všetky tenants do jedného compromise a rotation blast radiusu.
- **Plaintext logging** — decryption alebo template error môže preniesť secret z transient memory do persistent logs, support bundles a alert systems.
- **Wrong target namespace** — cryptographically správna value sa materializuje do nesprávneho authorization domainu a stáva sa čitateľnou cudzím workloads.

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

Refresh policy určuje, ktorá udalosť premení provider state na nový target Secret. Nejde iba o interval alebo optimalizáciu API volaní; policy definuje consistency, audit a promotion model medzi mutable external authority a Git-managed declaration.

Periodic sleduje provider automation, OnChange vyžaduje explicitný desired-state trigger a CreatedOnce chráni initial bootstrap value pred nečakaným prepisom. Každý režim má preto iný stale-value a recovery behavior.

### `Periodic`

Controller periodicky číta provider a aktualizuje target. Hodí sa pre pravidelnú rotation, ale vytvára provider dependency a delay do `refreshInterval`.

### `OnChange`

Target sa aktualizuje pri zmene ExternalSecret metadata/spec. Provider value môže byť zmenená bez refreshu, kým Git alebo metadata nevytvoria nový trigger. Je vhodné, keď rotation má byť explicitný desired-state transition.

### `CreatedOnce`

Controller vytvorí secret a bežne ho neobnovuje. Recreate ExternalSecretu však resetuje status a môže value znovu vygenerovať alebo prepísať. Pri bootstrap credentials, ktoré application uloží do vlastnej databázy, môže regenerácia vytvoriť permanentný mismatch.

Refresh policy nie je iba performance setting. Určuje consistency model medzi provider authority a target Secretom.

## 12. Target creation a deletion semantics

Target policy je ownership contract nad Kubernetes Secretom. Určuje, či operator vlastní celý object alebo iba vybrané keys, ako reaguje na missing provider property a či deletion desired declarationu odstráni aj materialized credential.

Tieto decisions menia availability aj security. Fail-open môže ponechať revoked value, fail-closed môže spôsobiť outage a shared target s viacerými writers môže oscillovať bez jasného authoritative ownera.

Target policy rozhoduje, kto vlastní Kubernetes Secret a čo sa stane pri delete alebo conflict-e.

Questions:

- **Whole-object create verzus key merge** — whole-object ownership zjednodušuje convergence, kým merge umožní shared target, ale zavádza per-key writers a conflict semantics.
- **Deletion coupling** — owner-based deletion odstráni credential spolu s declaration, zatiaľ čo orphan policy zachová availability za cenu stale secret debt-u.
- **Multiple key writers** — ak ďalší controller alebo human mení rovnaký key, systém potrebuje precedence contract; inak target oscilluje alebo silently overwrituje values.
- **Missing provider property** — policy musí rozhodnúť medzi fail-closed deletion/invalid state a zachovaním last-known value s explicitným stale warningom.
- **Stale-target behavior** — availability a security trade-off musí byť explicitný, pretože ponechaná revoked credential zlyháva inak než okamžite odstránený Secret.
- **Target immutability** — immutable Secret vyžaduje replace/new-name rollout namiesto in-place update-u a mení rotation aj cleanup ordering.

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

Workload identity nahrádza long-lived bootstrap key krátkodobým credentialom odvodeným z overeného service-account subjectu. Bez úzkej trust policy by však iba presunula broad privilege z Kubernetes Secretu do cloud role.

Issuer, audience, subject, provider resource scope a TTL sa preto vyhodnocujú ako jeden chain. Audit musí vedieť spojiť cloud decrypt alebo read request s konkrétnou controller reconciliation a tenant boundary.

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

- **Issuer a audience validation** — cloud provider musí akceptovať token iba od trusted cluster issueru a pre intended federation endpoint, nie generic bearer token.
- **Subject-bound trust policy** — namespace a service-account claims sa viažu na konkrétny controller/tenant a wildcard nesmie rozšíriť assume-role na celý cluster.
- **Provider resource restrictions** — role smie decryptovať alebo čítať iba environment/tenant key a secret paths potrebné pre daný reconciliation subject.
- **Short token a credential TTL** — obmedzuje usefulness ukradnutej identity a núti pravidelné reauthorization namiesto permanentného bootstrap secretu.
- **Audit correlation** — cloud request ID, assumed role session a Kubernetes service account sa musia spojiť s Flux/ExternalSecret operation identity.
- **Fail-closed identity error** — controller nesmie pri federation failure použiť shared fallback key alebo stale broad credential, ktorý obíde tenant boundary.

Ak controller beží ako cluster-admin a používa jednu cloud role pre všetky tenants, Kubernetes RBAC segmentation sama neochráni provider secrets.

## 15. Kubernetes Secret boundary

Po materialization sa ochrana presúva z Git/KMS modelu na Kubernetes control a node plane. Secret môže byť encrypted v etcd a zároveň čitateľný broad API principalom, node administratorom alebo actorom s `exec` do workloadu.

Jednotlivé controls preto chránia odlišné paths: RBAC chráni API, etcd encryption storage bytes, namespace a admission target placement a process isolation runtime consumption. Žiadna z týchto vrstiev sama neposkytuje end-to-end confidentiality.

Po decryption alebo fetchi sa plaintext často uloží do Kubernetes Secretu. Ochrana potom závisí od:

- **API authorization a RBAC** — obmedzujú principals, ktoré môžu list/get/watch Secret objects alebo ich získavať nepriamo cez Pod create a service-account bindings.
- **Admission a namespace isolation** — zabraňujú materialization do wrong targetu a presadzujú allowed Secret types, labels, mounts a workload relationships.
- **etcd encryption at rest** — chráni persisted control-plane bytes a backups pred raw storage readerom, ale nie pred legitímnym API server decryptom.
- **Control-plane backups** — obsahujú historical plaintext-equivalent secret data a potrebujú encryption, access, retention a secure disposal ako production secret store.
- **Audit logs** — majú zaznamenať metadata o Secret access-e bez request/response bodies, ktoré by samy vytvorili ďalší plaintext archive.
- **Node a kubelet access** — privileged node actor môže čítať mounted Secret alebo container state, preto scheduling a node administration patria do confidentiality modelu.
- **Container runtime a process isolation** — chránia environment, files a memory pred susedným workloadom, debug toolingom a host compromise-om.
- **Debug, exec a ephemeral-container permissions** — môžu obísť application API a priamo čítať mounted files alebo process environment, preto sú secret-reader privileges.

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

Secret observability musí dokazovať generation flow bez reprodukovania citlivej value. Provider version IDs, ciphertext digests, resource versions a operation identities umožňujú koreláciu, ale neposkytujú credential použiteľný na autentizáciu.

Safe a unsafe fields tvoria boundary contract pre controllery, CI, portal aj support tooling. Redaction po persistencii je neskoro; plaintext sa nesmie dostať do pôvodného log eventu, rendered diffu ani error response-u.

Secret system potrebuje evidence bez plaintextu.

Bezpečné fields:

- **Logical secret ID a version/generation** — umožňujú korelovať rotation bez zverejnenia value a musia pochádzať z authoritative provider/controller metadata.
- **Ciphertext digest** — odlišuje encrypted payload generations a dokazuje, ktorý Git blob controller spracoval, no neslúži ako hash plaintextu.
- **Provider object coordinate alebo bezpečný opaque ID** — identifikuje authority object; path sa má maskovať, ak jeho názov odhaľuje tenant alebo business context.
- **Controller operation ID** — spája fetch/decrypt/materialize attempt s logs, status conditions a downstream API requestmi.
- **Refresh timestamp a result** — ukazujú freshness a posledný úspešný/failed provider sync bez tvrdenia, že workload value už načítal.
- **Target Secret resourceVersion** — dokazuje Kubernetes object update a umožňuje zistiť, ktoré Pods vznikli pred alebo po materialization.
- **Workload loaded generation** — application endpoint alebo metric potvrdzuje value používanú processom, čo Secret resourceVersion sama nevie.
- **Revocation status** — provider authority potvrdzuje, či old generation je ešte akceptovaná a či negative test má zlyhať.
- **KMS key ID a audit request ID** — dokazujú, ktorý cryptographic authority decision otvoril data key a umožňujú incident correlation.

Nebezpečné fields:

- **Raw values** — nikdy nepatria do logu, diffu ani eventu, pretože observability store by sa stal ďalším neautorizovaným secret managerom.
- **Complete rendered Secret manifests** — obsahujú všetky data keys a môžu uniknúť cez CI preview, controller debug alebo support export.
- **Environment dumps** — kopírujú process-loaded secrets spolu s unrelated diagnostics a často sa uchovávajú dlhšie než credential TTL.
- **Provider API responses** — môžu obsahovať value, lease token alebo sensitive metadata a majú sa parsovať/redactovať pred loggingom.
- **Templating errors s input contextom** — nesmú serializovať decrypted document alebo substituted value do exception message-u.
- **Debug command history** — shell, terminal recording a ticket copy môžu zachovať plaintext aj po ukončení incident session.

Redaction musí byť applied pred log persistence. Hash secret value pre correlation môže byť tiež citlivý pri low-entropy secrets a umožniť offline guessing; lepšie je používať provider-assigned version ID.

## 20. Multi-tenancy

Secret multi-tenancy je end-to-end property. Namespace filter v portali alebo Kubernetes RBAC nestačia, ak shared controller role môže decryptovať všetky KMS keys alebo načítať ľubovoľný provider path.

Tenant subject musí zostať rovnaký v Git declaration, decryption/retrieval identity, provider authorization, target namespace aj workload binding. Slabá jediná boundary môže z trusted controllera urobiť confused deputy.

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

- **Cross-namespace decryption reference** — tenant môže získať key material alebo controller capability spravovanú v inom trust boundary.
- **Broad `ClusterSecretStore` role** — namespaced requester môže cez cluster-scoped store čítať provider paths, ktoré Kubernetes namespace policy sama neobmedzuje.
- **Arbitrary remote key path** — untrusted `remoteRef.key` zmení controller na confused deputy a obíde catalog alebo UI ownership checks.
- **Cluster-wide KMS decrypt** — compromise jedného controller processu alebo tenant-controlled ciphertextu ohrozuje všetky environment keys.
- **Cross-tenant target placement** — materializuje plaintext tam, kde ho môžu čítať cudzie service accounts alebo workloads.
- **Metadata disclosure v portali** — provider paths, versions a ownership môžu odhaliť topology alebo business relationships aj bez plaintext value.
- **Mixed-tenant backup alebo support bundle** — export obíde runtime namespace boundaries a vytvorí shared reader/retention domain.

Least privilege musí byť enforced na provider boundary, nie iba v UI alebo Git reviewe.

## 21. Backup, restore a disaster recovery

Recovery musí obnoviť celý secret access graph, nie iba declarative YAML. Potrebný je desired payload alebo reference, key/provider availability, workload identity, target materialization a functional consumer test.

Restore zároveň nesmie automaticky reaktivovať historickú credential. Provider authority a incident context určia, či old generation zostáva validná, musí zostať revoked alebo sa nahradí úplne novou generation.

Secret recovery sa líši podľa modelu.

### Encrypted-in-Git

Pri encrypted-in-Git modeli je retained Git history nepoužiteľná bez decryption key-u, controller trust a target bootstrapu. Tieto dependencies tvoria jeden recovery graph a musia sa testovať spolu.

Recovery proof nekončí pri úspešnom decrypt-e. Test workload musí dostať materialized value, načítať ju a úspešne sa autentizovať bez toho, aby evidence alebo logs obsahovali plaintext.

Potrebné sú:

- **Git history** — musí uchovať required ciphertext generation a repository trust evidence; samotný current branch nemusí obsahovať rollback candidate.
- **Decryption key alebo KMS availability** — recovery cluster potrebuje authorization otvoriť historical data key bez použitia broad emergency credentialu.
- **Controller manifests a identity trust** — obnovujú exact decryption implementation, service account a cloud federation contract, ktoré ciphertext spracujú.
- **Target cluster bootstrap** — musí bezpečne vytvoriť namespaces, RBAC, KMS trust a Git source skôr, než sa plaintext materializuje.
- **Functional decryption a consumer test** — overuje nielen cryptographic open, ale aj target Secret, workload load a úspešnú autentizáciu expected version.

### External provider

External-provider restore závisí od provider version retention a od obnovenia presne scoped workload identity. Git reference bez jedného z týchto predpokladov zostane iba nefunkčnou deklaráciou.

Provider audit musí potvrdiť, či restore candidate je ešte validný. Obnovenie revoked historical value bez explicitného decisionu by zmenilo security incident na recovery-induced credential reuse.

Potrebné sú:

- **Provider backup a version retention** — určujú, či logical reference ešte resolve-ne required generation a či provider dokáže obnoviť metadata a value.
- **IAM a workload-identity restore** — obnovujú subject-bound provider read bez static break-glass key-u alebo cross-tenant wildcardu.
- **`SecretStore` a `ExternalSecret` desired state** — rekonštruujú provider, authentication, property, refresh a target ownership contract.
- **Target Secret reconstruction** — musí vytvoriť správny namespace/name/schema a spustiť consumer reload podľa application consumption mode.
- **Validity decision pre historical credential** — provider a incident policy určia, či old version možno používať, zostáva revoked alebo sa musí nahradiť new generation.

### Sealed Secrets

Potrebný je controller private key backup a secure restore. Nový cluster s novým keyom existujúce SealedSecrets neotvorí bez re-encryption alebo old key-u.

DR test nemá vypisovať plaintext. Má overiť, že test workload získa credential, autentizuje sa a audit koreluje expected version.

## 22. Connected incident `GITOPS-PAY-62`

Secret incident je writer a generation race, nie iba nesprávne načasovaný restart. Provider, Git ciphertext, Kubernetes Secret a running process mali štyri odlišné states a manual patch zmenil iba jednu z nich.

Jednotlivé body nižšie vysvetľujú, ako shared decryption authority a chýbajúci rollout/reload contract zabránili bezpečnej rotation. Flux potom správne obnovil starý desired payload, čím emergency patch zvrátil.

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

- **Shared age recipient** — rovnaký private key mohol otvoriť staging aj production payloady a vytvoril spoločný compromise a rotation boundary.
- **Broad controller decryption identity** — jeden controller Secret a service account obchádzali environment isolation pri každom renderi.
- **Materialized target zostal na `pv-42`** — Kubernetes object zodpovedal old Git desired state-u pred emergency rotation.
- **Manual target patch bez authoritative transitionu** — `pv-43` sa objavil iba v live objecte a controller ho pri ďalšom reconcile považoval za drift.
- **Pods držali startup snapshot `pv-42`** — target Secret update nemenil process environment a bez rollout-u nevznikla consumer convergence.
- **Predčasná provider revocation** — old credential prestala fungovať skôr, než telemetry potvrdila, že všetky Pods používajú `pv-43`.
- **Incomplete health oracle** — readiness dokazovala available Pods a Secret object, nie loaded credential generation ani provider authentication.
- **Chýbajúca generation telemetry** — portal nemohol rozlíšiť materialized `pv-43` od process-loaded `pv-42` a oznámil false success.

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

Redesign obnovuje rotation ako jednu authoritative state machine. Provider vytvorí new generation, GitOps desired state ju identifikuje, controller ju materializuje a workload telemetry preukáže consumer convergence skôr, než provider zruší old generation.

Tým sa odstráni dual-writer oscillation medzi manual patchom a Fluxom. Emergency operátor už nemení iba target Secret; mení alebo pozastaví authoritative flow a recovery sa uzavrie negative testom revoked credentialu.

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

Acceptance musí prepojiť confidentiality, authority a liveness. Secret môže byť správne zašifrovaný, ale nepoužiteľný pre workload; môže byť správne materializovaný, ale už revoked providerom; alebo môže fungovať, no byť čitateľný cudzím tenant principalom.

Verdict preto pokrýva repository a KMS boundary, target materialization, process-loaded generation, rotation, revocation a restore. Platí iba pre exact environment, tenant, provider version a consumer cohort.

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

Troubleshooting začína pri provider authority, pretože tá rozhoduje, ktorá generation je aktívna alebo revoked. Potom sleduje desired reference, controller authorization, materialization a consumer loading, až kým nájde prvú boundary s odlišnou generation alebo failed operation.

Po náprave nestačí pozrieť Kubernetes Secret. Každý workload cohort musí reportovať new loaded generation, provider audit musí potvrdiť jej použitie a old generation musí zlyhať podľa revocation contractu.

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
