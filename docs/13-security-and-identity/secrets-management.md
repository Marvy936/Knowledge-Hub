# Secrets management

Secrets management je lifecycle disciplína pre credentials, private keys, tokens, recovery material a ďalšie capabilities. Cieľom nie je iba uložiť value do encrypted database. Cieľom je vedieť, prečo capability existuje, kto ju smie získať alebo použiť, ktorý target jej dôveruje, ktorá generation je načítaná v consumers, ako sa obnovuje a ako sa definitívne zneplatní.

Secret je hodnotný preto, že ho cieľový systém akceptuje. Private signing key môže vytvárať dôveryhodné tokens alebo assertions. Database password vytvorí sessions. Refresh token vydáva ďalšie access tokens. Zmazanie jednej copy preto nie je revocation; incident sa uzavrie až po odstránení target trustu, cached copies, sessions a descendants.

## Capability-to-revocation lifecycle

Secret lifecycle sa nekončí storage readom ani vytvorením novej version. Musí sledovať target trust, consumer-loaded generation, sessions a všetky descendants až po preukázanú revocation starej capability.

```text
business purpose a target trust
→ exact secret subject, owner a consumers
→ generation alebo import
→ authoritative storage a protection boundary
→ bootstrap identity a authorization
→ distribution alebo mediated use
→ consumer-loaded generation
→ lease, renewal alebo rotation
→ target mutation a cutover
→ old generation revocation
→ copies, sessions a descendants cleanup
→ audit, recovery a second-rotation validation
```

Configured secret version, successful read a healthy secret store sú rozdielne stavy. Consumer môže ďalej používať starú value v memory, connection poole alebo local file aj po tom, čo store ukazuje novú version.

## Exact secret subject SEC-PAY-49

Secret subject musí spojiť value alebo key reference s účelom, target trustom, všetkými consumers a loaded generations. V incidente je toto rozlíšenie rozhodujúce, pretože jedna exportovateľná key mala štyri odlišné federation purposes a storage encryption tento coupling neodhalila.

```yaml
incident: SEC-PAY-49
secretId: FED-SIGN-07
purposeObserved:
  - oidc-production-signing
  - oidc-staging-signing
  - saml-production-signing
  - saml-staging-signing
storage: Kubernetes Secret idp-signing-key
namespace: identity-platform
consumerServiceAccount: system:serviceaccount:identity-platform:idp-runtime
indirectActor: staging-debug-principal
loadedConsumers:
  - production-oidc-signer
  - staging-oidc-signer
  - production-saml-signer
  - staging-saml-signer
forbidden:
  - cross-environment-key-reuse
  - cross-protocol-key-reuse
  - exportable-runtime-private-key
```

Subject odhaľuje, že jedna value mala štyri odlišné trust purposes. Encryption storage neoddeľuje purpose ani consumers.

## Typy secrets a ich revocation boundary

Static credential existuje dlhšie a target ho overuje priamo. Dynamic credential má lease a vzniká pre konkrétneho consumera. Authentication secret preukazuje identity; cryptographic key vykonáva signing/decryption; recovery secret odomyká alebo obnovuje trust root. Každý typ má inú revocation.

Database dynamic user sa revoke-ne v database engine a lease systéme. JWT signing key sa revoke-ne odstránením verifier trustu a ukončením token/session window. Refresh token potrebuje family revocation. KMS/HSM key môže byť disabled, ale ciphertext recovery plan musí stále existovať. „Rotate all secrets“ bez dependency inventory môže zničiť availability a nevyriešiť kompromitované descendants.

## Secret zero a workload identity

Secret zero je credential, ktorým workload prvýkrát autentizuje secret store. Static bootstrap token v image alebo environment-e iba presúva problém. Preferovaný model používa platform workload identity: Kubernetes ServiceAccount token s audience, cloud workload identity, mTLS certificate alebo signed CI assertion. Secret store potom vydá krátkodobú, consumer-specific capability.

Workload identity sama nie je least privilege. Ak principal môže čítať všetky production paths alebo impersonovať iný ServiceAccount, short-lived token má stále broad blast radius. Auth method, role mapping, namespace/cluster binding, audience a TTL sa auditujú ako jeden contract.

## Delivery patterns a plaintext boundary

Environment variable je jednoduchá, ale môže prežiť v process dump-e, debug outpute alebo child processoch a zvyčajne sa neaktualizuje bez restartu. File projection podporuje atomic symlink/version swap, no application môže file načítať iba pri štarte. Sidecar/agent môže obnovovať lease, ale vytvára local plaintext a availability dependency. Direct API read poskytuje explicitný lifecycle, no application musí bezpečne riešiť auth, cache, retry a unknown outcome.

CSI alebo Kubernetes volume projection nevykonáva automaticky application reload. Store generation, mounted file generation a loaded in-memory generation sa overujú samostatne. Symlink zmenený na new file neznamená, že existujúci TLS context alebo connection pool používa nový credential.

## Kubernetes Secrets a indirect access

Kubernetes Secret je API resource; base64 v manifestoch nie je encryption. Etcd encryption at rest chráni storage boundary, TLS transport a RBAC API access, ale kubelet môže secret premietnuť do Podu. Principal s `create pods` a možnosťou vybrať ServiceAccount môže získať indirect access aj bez direct `get secrets`.

```bash
kubectl auth can-i get secrets \
  --namespace identity-platform \
  --as=urn:atlas:human:staging-debug

kubectl auth can-i create pods \
  --namespace identity-platform \
  --as=urn:atlas:human:staging-debug
```

Výsledok `no` a `yes` je warning, nie safe verdict. Príkazy preukazujú direct RBAC requests; nepreukazujú admission restrictions, ServiceAccount selection, existing Pod exec alebo custom-controller paths.

Secret manifest bez plaintext v Git môže používať external reference:

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: production-oidc-signer
  namespace: identity-platform
spec:
  refreshInterval: 5m
  secretStoreRef:
    name: identity-vault
    kind: SecretStore
  target:
    name: production-oidc-signer
  data:
    - secretKey: key-reference
      remoteRef:
        key: federation/production/oidc/signer
```

Manifest preukazuje desired source path a refresh intent. Nepreukazuje store auth, fetched version, Kubernetes Secret contents, consumer reload ani non-exportable key use. Pri private signing key-u je mediated KMS/HSM signing často bezpečnejšie než export do Kubernetes Secretu.

## Vault auth, policy a dynamic secrets

Vault-style system oddeľuje auth methods, policies, tokens, leases a secrets engines. Policy má viazať workload identity na exact paths a operations. Dynamic database credential vytvára unikátneho usera s TTL a auditovateľným lease.

```bash
vault write auth/kubernetes/login \
  role=payments-api \
  jwt="$KUBERNETES_SERVICE_ACCOUNT_TOKEN"

vault read database/creds/payments-readonly
```

Prvý command preukazuje auth-method response pre konkrétny token a role. Druhý preukazuje vydanie credentialu a lease metadata. Nepreukazujú, že database user má intended grants, consumer credential načítal, old lease bol revoke-nutý alebo audit device bezpečne doručil event.

Lease revocation:

```bash
vault lease revoke database/creds/payments-readonly/LEASE_ID
```

Successful response preukazuje secret-store revocation workflow. Nepreukazuje okamžité ukončenie už otvorených database sessions; database-side kill alebo bounded session lifetime môže byť samostatný control.

## Rotation ako coordinated state transition

Rotation nie je overwrite jednej value. Bezpečný lifecycle vytvorí novú generation, pripraví target acceptance, distribuuje new credential, overí loaded consumers, prejde traffic alebo sessions a až potom revoke-ne old generation. Pri single-key systems môže byť potrebný planned outage alebo dual-trust overlap.

Unknown outcome po target mutation je kritický. Ak secret manager timeoutne po zmene database passwordu, store a target môžu byť split-brain. Recovery musí najprv read-backnúť target state alebo použiť idempotentný rotation transaction, nie blind retry s ďalšou generation.

## Caching, outage a fail-open/fail-closed

Cache znižuje secret-store dependency a latency, ale predlžuje revocation. Application musí definovať maximum stale age a správanie pri renewal failure. Read-only database credential môže krátko pokračovať z cache, kým production signing key alebo revoked admin token môže vyžadovať fail-closed.

Secret-store outage nie je dôvod logovať plaintext alebo fallbacknúť na hard-coded shared credential. Graceful degradation sa navrhuje podľa secret type-u a business risku. Monitoring sleduje lease age, renewal errors, loaded generation a target acceptance, nie iba store uptime.

## Seal, unseal, HA a recovery

Secret store chráni storage encryption key cez seal boundary. Shamir shares alebo recovery keys majú oddelenú custody; auto-unseal presúva dependency na KMS/HSM a jeho identity/availability. Unseal nie je application secret recovery a recovery key nie je bežný admin credential.

HA zabezpečuje service availability, nie automaticky DR. Snapshot musí byť konzistentný, encrypted a pravidelne restore-nutý do isolated environmentu. Recovery test overí auth methods, policies, leases, audit a target integrations. Restore starého store snapshotu môže znovu publikovať revoke-nuté credentials, ak target state a revocation ledger nie sú reconciled.

## Incident SEC-PAY-49

`FED-SIGN-07` bol uložený ako exportable Kubernetes Secret a používaný naprieč environmentmi aj protocols. Staging debug principal nemal direct `get secret`, ale mohol vytvoriť Pod, vybrať `idp-runtime` ServiceAccount, mountnúť Secret a vykonať `exec`. Etcd KMS a TLS fungovali správne; nechránili authorized runtime plaintext.

Attacker získal key a vytvoril validne podpísané OIDC a SAML artifacts. Root cause bol shared exportable key a neoddelený purpose/consumer contract. Indirect workload access bol acquisition path; wrong issuer/entity validation a direct role mapping boli downstream amplifiers.

## Containment, recovery a acceptance

Containment zablokuje old key v verifier truste, izoluje affected workloads, revoke-ne sessions/tokens/assertions a zachová Kubernetes audit, Secret versions, signer logs a federation artifacts. Secret sa necommitne do incident ticketu ani bežného logu.

Recovery vytvorí štyri oddelené non-exportable keys alebo signing services pre production/staging a OIDC/SAML, zúži workload identities a odstráni arbitrary Pod/exec path. Coordinated rollover overí signer loaded generation, verifier trust, successful canary a old-key rejection. All copies, backups, CI variables, Terraform state a local debug files sa inventarizujú podľa exposure window.

Acceptance vyžaduje, aby current signers používali intended key references, old key nedokázal vytvoriť accepted OIDC ani SAML artifact, staging identity nemala production path, direct aj indirect secret access zlyhal a legitimate production signing zostal dostupný. Druhá rotation musí prejsť bez split-brain a old session descendants musia zostať revoke-nuté.

## Kontrolné otázky

1. Prečo encrypted secret store nevyrieši consumer a target trust?
2. Ako sa revocation private signing key-u líši od zmazania jeho copy?
3. Prečo `get secrets = no` nie je úplný Kubernetes verdict?
4. Aké stavy oddeľujú store version, mounted file a loaded credential?
5. Čo dynamic lease revocation nepreukazuje pre otvorené sessions?
6. Ako cache mení availability a revocation latency?
7. Prečo restore secret-store snapshotu môže obnoviť zakázaný old trust?

## Referencie

- [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
- [Kubernetes KMS encryption](https://kubernetes.io/docs/tasks/administer-cluster/kms-provider/)
- [HashiCorp Vault documentation](https://developer.hashicorp.com/vault/docs)
- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: SAML](saml.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Encryption at rest a in transit →](encryption-at-rest-and-in-transit.md)
<!-- KNOWLEDGE-NAVIGATION:END -->