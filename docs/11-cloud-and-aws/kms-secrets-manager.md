# KMS a Secrets Manager

AWS Key Management Service (KMS) a AWS Secrets Manager chránia súvisiace, ale odlišné typy state-u. KMS riadi cryptographic key resources, key material a authorization pre cryptographic operations. Secrets Manager riadi versionované secret values, staging labels, retrieval, replication a rotation credentials v target systéme.

Najčastejšia prevádzková chyba vzniká vtedy, keď sa tieto vrstvy zredukujú na vetu „secret je zašifrovaný“. Bezpečný výsledok závisí od celého lifecycle-u:

```text
business protected-value alebo credential intent
→ exact key, secret, target a consumer subject
→ authorization a key state
→ cryptographic alebo secret retrieval operation
→ target credential mutation
→ staging-label transition
→ consumer refresh a loaded state
→ old generation revocation
→ application a business validation
→ audit, recovery a retirement
```

KMS operation success neznamená, že application načítala správny secret. `AWSCURRENT` neznamená, že rovnaké credentials sú platné v target database. Úspešná rotation neznamená, že všetky warm processes, connection pools a replicas opustili starú generation.

## 1. Exact protected-value subject

Atlas Payments používa subject `SEC-PAY-42`:

```text
account = 100000000042
Region = eu-central-1
workload = CAP-PAY-42

KMS key ARN = arn:aws:kms:eu-central-1:100000000042:key/key-pay-17
KMS logical generation = KMS-PAY-17
key-material rotation generation = MAT-9
alias = alias/prod/payments-secrets
key-policy generation = KPOL-31
active grants = GRANTSET-12
key state = Enabled

secret ARN = arn:aws:secretsmanager:eu-central-1:100000000042:secret:prod/payments/provider
secret metadata generation = SEC-PROVIDER-22
AWSCURRENT = version v42
AWSPREVIOUS = version v41
rotation candidate = version v43 / AWSPENDING
rotation model = alternating users
rotation workflow generation = ROT-14

target system = payment-provider gateway
credential principals = atlas-pay-a, atlas-pay-b
credential generation accepted by target = CRED-42

consumers =
  ECS payments-api release 7.18.0
  Lambda settlement-consumer release 5.4.0
  reconciliation worker release 3.2.1

consumer cache contract = 5 min TTL + refresh on authentication failure
consumer loaded-version evidence = secret version ID + process/task identity

business outcome =
  every authorized consumer authenticates with the intended credential generation
  payment P-884 is settled exactly once

forbidden outcomes =
  key administrator can decrypt every secret by default
  alias remap is treated as data re-encryption
  AWSCURRENT points to credentials invalid in the target
  old credentials are revoked before all consumer cohorts refresh
  secret value or encryption context leaks through logs or tags
  key deletion destroys the only decrypt path for retained data
```

Incident evidence musí viazať request na exact key ARN, key-policy generation, caller session, encryption context, secret ARN, version ID/staging labels, rotation execution, target credential state, consumer process/task identity, loaded secret version, connection-pool state a business operation.

## 2. Štyri identity, ktoré sa nesmú zameniť

### KMS key resource

KMS key je logical AWS resource s key ID/ARN, policy, state, origin, usage, aliases, grants a key-material history. Key ARN je dlhodobá authorization a audit identity.

### KMS key material

Key material je cryptographic material používaný konkrétnou generation. Pri podporovanej KMS rotation zostáva key ID rovnaký a mení sa material generation. KMS si zachová potrebný starší material na decrypt ciphertextov vytvorených pred rotation podľa key modelu.

### Secret version

Secret version je immutable secret value identifikovaná version ID. Staging label ako `AWSCURRENT`, `AWSPREVIOUS` alebo `AWSPENDING` je pohyblivý pointer, nie samotná value.

### Consumer-loaded state

Application process, Lambda execution environment, ECS task, sidecar, connection pool alebo external agent môže držať value načítanú skôr. Secrets Manager control plane preto môže byť správny, zatiaľ čo runtime stále používa starú credential generation.

Operational reasoning musí vždy odpovedať:

```text
ktorý KMS key a material chránil ciphertext?
ktorá secret version bola označená ako current?
ktoré credentials sú reálne platné v target systéme?
ktorú version načítal konkrétny consumer a jeho connection?
```

## 3. Envelope encryption journey

KMS nie je určený na priame šifrovanie veľkých application payloadov. Bežný model je envelope encryption:

```text
application alebo AWS service požiada o data key
→ KMS autorizuje GenerateDataKey
→ vráti plaintext data key a encrypted data key
→ plaintext key zašifruje dáta lokálne
→ plaintext key sa odstráni z použiteľnej memory
→ uloží sa ciphertext + encrypted data key + required context

pri čítaní:
encrypted data key + exact encryption context
→ KMS Decrypt authorization
→ plaintext data key
→ local payload decryption
→ plaintext key retirement
```

KMS key neopúšťa KMS security boundary. CloudTrail zaznamenáva control a cryptographic API activity podľa event modelu, ale application stále vlastní bezpečné spracovanie plaintext data key-u, payloadu a memory lifetime.

### Failure boundary: key rotation nie je re-encryption

Rotation KMS key materialu:

- nemení key ID ani ARN;
- nemení aliases a policy;
- neprešifruje existujúce payloady;
- nerotuje data keys uložené pri payloads;
- neopraví kompromitovaný plaintext data key.

Ak requirement vyžaduje nový logical key, novú policy boundary alebo re-encryption dát, ide o migration workflow:

```text
nový key a policy
→ consumer/service authorization
→ re-encryption alebo copy podľa service contractu
→ read-back/decrypt validation
→ inventory closure
→ starý key disable observation window
→ až potom deletion decision
```

## 4. KMS authorization je viacvrstvový verdict

Pre customer managed key nestačí skontrolovať jednu IAM policy. Effective verdict vzniká z:

```text
actual caller a STS session
→ identity policy
→ permissions boundary a session policy
→ SCP/RCP a explicit denies
→ KMS key policy
→ grant a grant constraints
→ key state, Region, usage a origin
→ encryption-context conditions
→ VPC endpoint policy
→ service-specific calling path
→ cryptographic result
```

Key policy je fundamentálna resource-policy boundary. Môže povoliť priamych principals, umožniť account IAM delegation alebo obmedziť service integration. Key administrator nemusí a spravidla nemá automaticky dostať `kms:Decrypt`.

### Grants

Grant poskytuje konkrétnemu grantee principalovi vybrané cryptographic operations. AWS services ich často vytvárajú pri práci s encrypted resources. `kms:CreateGrant` je preto high-impact permission.

Bezpečný grant model viaže:

- exact grantee principal;
- povolené operations;
- retiring principal;
- encryption-context constraints;
- service/resource scope;
- lifecycle a cleanup.

Stale grant po odstránení resource-u rozširuje authorization surface aj vtedy, keď application policy už vyzerá čisto.

## 5. Encryption context je integrity a authorization input

Encryption context je non-secret key-value map kryptograficky viazaná k podporovaným symmetric KMS operations. Pri decrypt musí caller poskytnúť exact context.

Používa sa na:

- väzbu ciphertextu na tenant alebo resource identity;
- key-policy a grant conditions;
- audit correlation;
- ochranu proti presunu ciphertextu do nesprávneho contextu.

Do encryption contextu nepatria secrets, access tokens ani citlivé osobné údaje. Context môže byť viditeľný v auditných surfaces.

### Worked micro-scenario

Ciphertext pre payment tenant `tenant-42` bol vytvorený s contextom:

```text
{"application":"payments","tenant":"tenant-42","purpose":"provider-token"}
```

Copy ciphertextu do `tenant-43` storage nestačí. Decrypt s iným contextom zlyhá, a policy môže navyše vyžadovať exact tenant value. Správny failure dokazuje, že cryptographic binding funguje; nie je to náhodný KMS outage.

## 6. Key types, ownership a rotation

Rozlišuj:

- AWS owned keys — zákazník ich priamo nevidí ani nespravuje;
- AWS managed keys — existujú v account-e pre service integration, ale policy/lifecycle spravuje AWS service;
- customer managed keys — zákazník vlastní policy, aliases, grants, enablement, rotation a deletion lifecycle.

Podľa use case-u KMS podporuje symmetric encryption, asymmetric encryption/signing, HMAC, multi-Region a rôzne key-material origins.

### Automatic a on-demand rotation

Automatic rotation sa používa pri podporovaných symmetric customer managed keys s AWS-generated materialom a môže mať definovaný rotation period. On-demand rotation je dostupná iba pre podporované symmetric models; presný origin a key-type support treba overiť v aktuálnej KMS dokumentácii.

Pre related multi-Region keys sa rotation riadi z primary key podľa service contractu. Každý regional key resource si však zachováva vlastnú policy, grants a operational state.

### Manual rotation

Asymmetric, HMAC, custom-key-store alebo iný nepodporovaný model potrebuje nový logical key a controlled migration. Alias možno presmerovať, ale alias transition sám:

- nere-encryptuje existujúce ciphertexty;
- nemení key ID uložený v service metadata;
- neoveruje, že consumers majú access na nový key;
- neumožňuje vypnúť starý key bez dependency inventory.

## 7. Disable a deletion sú recovery decisions

`DisableKey` zablokuje väčšinu cryptographic operations. Scheduled deletion po waiting period odstráni key material a môže vytvoriť permanentnú data loss.

Pred disable/delete vytvor dependency manifest:

```text
key ARN a aliases
→ encrypted S3/EBS/RDS/backup/secret resources
→ ciphertext a data-key inventory
→ service grants
→ cross-account consumers
→ retained recovery points
→ legal retention
→ tested decrypt/restore path
```

Bezpečný postup je najprv odstrániť nové encrypt uses, sledovať decrypt activity, otestovať recovery, udržať rollback window a až potom rozhodnúť o deletion. Absencia recent CloudTrail events nie je úplný dôkaz, že neexistuje quarterly restore alebo dormant archive dependency.

## 8. Secrets Manager lifecycle

Secret obsahuje metadata, KMS association, versions, staging labels, rotation configuration, resource policy a voliteľné replicas. Citlivé hodnoty nepatria do name, description ani tags, pretože tieto metadata nie sú secret ciphertext.

Credential rotation musí koordinovať tri systémy:

```text
secret store
+ target service credential state
+ consumer-loaded state
```

Správny lifecycle:

```text
vytvor novú candidate version
→ priraď AWSPENDING
→ vytvor alebo zmeň credentials v target service
→ autentizuj sa candidate credentials
→ over least privilege a business-safe operation
→ presuň AWSCURRENT
→ consumers refreshnú value a connections
→ monitoruj mixed cohort
→ revokuj old target credential
→ odstráň stale cache/connections
→ uzavri audit a recovery evidence
```

Lambda-based rotation typicky používa kroky `createSecret → setSecret → testSecret → finishSecret`. Workflow musí byť idempotentný, pretože step alebo celá rotation môže byť retryovaná.

Secrets Manager môže pri podporovaných typoch používať managed rotation, partner-managed external secret rotation alebo zákaznícku Lambda rotation. Management model nemení potrebu overiť target a consumer state.

## 9. Single-user a alternating-users rotation

### Single-user

Jedna identity dostane novú credential value. Je jednoduchšia, ale target zmena môže okamžite invalidovať starú value. Stale consumers preto môžu stratiť access ešte pred refreshom.

### Alternating users

Dve identities sa striedajú. Nová alebo neaktívna identity sa pripraví, otestuje a publikuje, zatiaľ čo predchádzajúca môže zostať dočasne validná. Model znižuje cutover risk, ale potrebuje admin secret, presný privilege-equivalence contract a kontrolované old-user disable.

Voľba je availability a privilege rozhodnutie, nie iba rotation template.

## 10. Staging labels nie sú target truth

`AWSCURRENT` odpovedá, ktorú secret version má bežný retrieval vrátiť. Neodpovedá automaticky:

- či target service túto credential value akceptuje;
- či value má správne privileges;
- či všetky consumers načítali túto version;
- či existujúce pooled sessions používajú staré credentials;
- či regional replica už obsahuje rovnakú generation.

Rovnako `AWSPREVIOUS` neznamená, že old credential je stále platná. Pri rollbacku treba najprv zistiť authoritative target credential state a až potom meniť labels.

## 11. Runtime retrieval, caching a connection pools

Retrieval path obsahuje:

```text
consumer workload identity
→ Secrets Manager endpoint a resource policy
→ GetSecretValue authorization
→ KMS decrypt path
→ version-stage selection
→ SDK/provider cache
→ process memory
→ client alebo connection pool
→ target authentication
```

Načítanie pri každom business requeste zvyšuje latency, API cost a dependency pressure. Nekonečný cache zase predlžuje credential exposure a blokuje rotation.

Cache contract má definovať:

- maximum TTL;
- refresh jitter;
- refresh pri authentication failure;
- single-flight ochranu pred refresh stormom;
- behavior pri Secrets Manager outage;
- loaded version ID v bezpečnej telemetry;
- connection-pool eviction po credential change;
- maximum accepted old-generation lifetime.

Secret sa nesmie logovať. Bezpečne možno logovať secret ARN hash, version ID, stage, cache age, consumer release a authentication result bez value.

## 12. Cross-account a multi-Region secret model

Cross-account retrieval potrebuje identity allow v caller account-e, secret resource policy, customer managed KMS key policy a neexistenciu explicit deny. AWS managed key `aws/secretsmanager` nie je všeobecný cross-account key contract.

Secret replication vytvára regional replicas secret value podľa service modelu. Nevytvára:

- replica target database usera;
- application failover;
- DNS/traffic cutover;
- rovnakú key policy v každom Regione;
- okamžitú consumer refresh garanciu.

DR manifest musí viazať regional secret replica na regional target credential, KMS key, application configuration a failover authority.

## 13. Worked failure: rotation split-brain medzi store, targetom a consumers

### Planned change

Rotation `ROT-14` pripravuje version `v43` pre principal `atlas-pay-b`. Candidate credentials prejdú target authentication testom a workflow presunie `AWSCURRENT` z `v42` na `v43`.

Deployment team očakáva, že všetky consumers refreshnú secret do piatich minút. Starý principal `atlas-pay-a` má byť deaktivovaný po desiatich minútach.

### Symptom

Po deactivation starého principalu:

- nové ECS tasks spracúvajú payments;
- staršie tasks vracajú provider authentication failures;
- Lambda warm environments zlyhávajú iba pri niektorých shards;
- Secrets Manager ukazuje rotation `Succeeded`;
- `AWSCURRENT` je `v43`;
- provider dashboard ukazuje validný `atlas-pay-b`.

On-call ručne presunie `AWSCURRENT` späť na `v42`, ale incident sa zhorší. `atlas-pay-a` je už v target systéme disabled, takže nové retrievals dostanú neplatnú old value.

### Competing hypotheses

1. `v43` má nesprávnu value;
2. KMS alebo secret resource policy odmieta retrieval;
3. iba časť consumers drží stale `v42`;
4. target privileges `atlas-pay-b` nie sú ekvivalentné;
5. regional replica alebo endpoint vracia inú generation;
6. connection pools po refreshi stále používajú sessions vytvorené cez `v42`.

### Discriminating evidence

- direct controlled authentication s `v43` uspeje;
- CloudTrail `GetSecretValue` ukazuje, že affected tasks secret po rotation vôbec nenačítali;
- process telemetry viaže failures na loaded version `v42`;
- niektoré processes načítali `v43`, ale pool neevictol old connections;
- KMS decrypt calls sú úspešné, takže key policy nie je root cause;
- failure cohort koreluje s task start time, nie s AZ alebo Regionom.

Root cause je porušený consumer-refresh contract. Rotation workflow uzavrel store a target transition, ale nečakal na runtime loaded-state evidence. Manuálny label rollback potom vytvoril opačný mismatch: store ukazoval na credential, ktorú target už odmietal.

### Containment

1. zastav automatic rotation retries a manual label changes;
2. obmedz event-source concurrency, aby authentication retry storm nepreťažil provider;
3. zachovaj secret versions, labels, rotation logs, CloudTrail a consumer cohort inventory;
4. udrž `atlas-pay-b` ako jedinú authoritative write credential;
5. nastav `AWSCURRENT` na `v43`;
6. force-refreshni cache a evictni connection pools postupne po cohorts;
7. izoluj consumers, ktoré nevedia preukázať loaded version.

### Authoritative recovery

- redeploy/recycle stale ECS a Lambda cohorts bounded waves;
- over `v43` retrieval aj target authentication s production workload identity;
- over provider privileges a forbidden admin operations;
- reconcile payment attempts podľa idempotency keys;
- drain backlog pri controlled concurrency;
- potvrď, že žiadny process nepoužíva `v42`;
- až potom odstráň alebo expire old credential a uprav rotation workflow.

### Acceptance verdict

Recovery je ukončené až keď:

- exact approved consumers načítali `v43`;
- target prijíma `atlas-pay-b` a odmieta retired `atlas-pay-a`;
- allowed payment journey funguje;
- forbidden admin/decrypt paths zlyhávajú;
- nevznikli duplicate settlements;
- regional replicas a DR manifest ukazujú compatible generation;
- ďalšia canary rotation preukáže consumer-loaded-state gate.

## 14. Troubleshooting podľa observation pointu

### KMS `AccessDenied`

```text
exact caller/session
→ key ARN a Region
→ key state/usage/origin
→ key policy
→ IAM/SCP/boundary/session policy
→ grant
→ encryption context
→ endpoint policy
→ service calling path
```

Zachovaj CloudTrail request ID, error code, key ARN a context. Test s admin role môže maskovať production identity failure.

### Encrypted AWS resource sa nevytvorí alebo neobnoví

Over source a destination key, service grants, snapshot/copy ownership, cross-account policy, key state a restore role. Resource create permission neznamená permission použiť encryption key.

### Secret retrieval timeout

Over DNS, route, NAT/interface endpoint, SG/NACL, endpoint policy, SDK timeout a connection reuse. Timeout nie je IAM deny.

### Application používa staré credentials

Over secret stage a version, consumer cache age, process-loaded version, pool/session lifetime, target accepted principals a regional replica status.

### Rotation zlyhá

Over exact step, `AWSPENDING`, idempotency token, target connectivity, admin credential, KMS permissions, target mutation, test semantics a finish-label transition.

## 15. Security a operational controls

- workload identity namiesto static bootstrap keys;
- separate key administrators, key users a secret operators;
- scoped `kms:CreateGrant`, `kms:Decrypt`, `GetSecretValue` a `PutResourcePolicy`;
- block-public-policy validation pre secrets;
- private endpoint policies viazané na exact resources;
- secret values mimo logs, tags, names a tracing attributes;
- CloudTrail alerts na key disable/deletion, alias/policy/grant a secret-policy/rotation changes;
- rotation canary a consumer refresh evidence;
- dependency manifest pred key retirement;
- break-glass s time-bound session a post-use review.

## 16. Cost a performance model

Cost a latency ovplyvňujú KMS API volume, Secrets Manager retrievals, rotation Lambda/managed workflow, replicas, VPC endpoints a CloudTrail/log processing. Cache môže cost výrazne znížiť, ale jej TTL je security a availability parameter.

Optimization nesmie odstrániť audit evidence, predĺžiť revocation window bez rozhodnutia ani zmeniť rotation na neoverený manual process.

## 17. SOA-C03 mapovanie

- **Domain 1** — KMS/Secrets telemetry, rotation/retrieval alarms a incident correlation.
- **Domain 2** — regional replicas, key availability, credential continuity a recovery windows.
- **Domain 3** — key/secret provisioning, policies, grants, aliases, rotation a IaC.
- **Domain 4** — encryption, key policy, least privilege, secrets a auditability.
- **Domain 5** — endpoints, cross-account access a private target connectivity.

## 18. Anti-patterny

### Key rotation považovaná za re-encryption

Existujúce payloads a data keys zostávajú chránené podľa pôvodného cryptographic history.

### Alias ako key identity

Alias je mutable pointer. Incident a recovery evidence musí obsahovať key ARN/ID.

### `AWSCURRENT` ako dôkaz úspešnej rotation

Label nepreukazuje target validity ani consumer-loaded state.

### Old credential revoke-nutá podľa času

Fixed delay bez cohort evidence môže odstaviť stale processes.

### Secret načítaný pri každom requeste

Zvyšuje latency, cost a failure amplification.

### Secret uložený navždy v environment variable

Rotation sa prejaví až po process replacement a value môže unikať cez process/deployment surfaces.

### Key deletion ako cleanup

Môže nenávratne zničiť retained data a backups.

## 19. Kontrolné otázky

1. Aký je rozdiel medzi KMS key resource a key material generation?
2. Prečo KMS rotation nere-encryptuje existujúce dáta?
3. Ako vzniká effective KMS authorization verdict?
4. Na čo slúži encryption context?
5. Prečo alias nie je bezpečná audit identity?
6. Ktoré tri stavy musí koordinovať secret rotation?
7. Čo `AWSCURRENT` preukazuje a čo nepreukazuje?
8. Ako sa líši single-user a alternating-users rotation?
9. Ako overíš consumer-loaded secret version bez logovania value?
10. Aký acceptance verdict potrebuje rotation incident?

## Glossary impact

Relevantné pojmy: protected-value subject, KMS logical key identity, key-material generation, envelope-encryption subject, cryptographic authorization verdict, encryption-context binding, key dependency manifest, secret lifecycle subject, target credential generation, consumer-loaded secret state, staging-label transition, rotation split-brain, consumer refresh gate, credential overlap window, secret recovery acceptance verdict a key retirement verdict.

## Oficiálna dokumentácia

- [AWS KMS Developer Guide](https://docs.aws.amazon.com/kms/latest/developerguide/overview.html)
- [AWS KMS concepts](https://docs.aws.amazon.com/kms/latest/developerguide/concepts-intro.html)
- [Key policies](https://docs.aws.amazon.com/kms/latest/developerguide/key-policies.html)
- [KMS grants](https://docs.aws.amazon.com/kms/latest/developerguide/grants.html)
- [Rotate AWS KMS keys](https://docs.aws.amazon.com/kms/latest/developerguide/rotate-keys.html)
- [Multi-Region keys](https://docs.aws.amazon.com/kms/latest/developerguide/multi-region-keys-overview.html)
- [AWS Secrets Manager User Guide](https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html)
- [Rotate secrets](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html)
- [Managed external secrets](https://docs.aws.amazon.com/secretsmanager/latest/userguide/managed-external-secrets.html)
- [Secrets Manager best practices](https://docs.aws.amazon.com/secretsmanager/latest/userguide/best-practices.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Systems Manager](systems-manager.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: AWS Backup →](aws-backup.md)
<!-- KNOWLEDGE-NAVIGATION:END -->