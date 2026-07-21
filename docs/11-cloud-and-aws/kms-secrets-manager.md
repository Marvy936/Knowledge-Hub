# KMS a Secrets Manager

AWS Key Management Service a AWS Secrets Manager riešia súvisiace, ale odlišné problémy. KMS riadi cryptographic keys a oprávnenia na cryptographic operations. Secrets Manager riadi lifecycle secret values, ich retrieval, versions, rotation a integráciu s aplikáciami. Secret uložený v Secrets Manageri je chránený cez KMS, ale KMS nie je secret database a Secrets Manager nie je všeobecný cryptographic API.

## 1. Mentálny model

```text
KMS key
→ key policy, IAM, grants a cryptographic operations
→ data key alebo service integration
→ encrypted application/service data

Secrets Manager secret
→ metadata + versions + staging labels + rotation
→ KMS envelope encryption
→ authorized runtime retrieval
```

Rozlišuj:

- **KMS key** — logical key resource a policy boundary,
- **key material** — cryptographic material chránený KMS/HSM modelom,
- **data key** — symmetric key použitý na šifrovanie application data,
- **envelope encryption** — data key šifruje dáta, KMS key šifruje data key,
- **secret** — secret metadata a versioned values,
- **rotation** — zmena credentials v secret store aj target systéme.

## 2. KMS key types

AWS KMS podporuje podľa use case:

- symmetric encryption keys,
- asymmetric encryption keys,
- asymmetric signing keys,
- HMAC keys,
- multi-Region keys,
- AWS managed a customer managed keys,
- imported alebo external key material podľa podporovaného modelu.

Najbežnejší AWS service encryption model používa symmetric customer-managed alebo AWS-managed KMS key.

## 3. AWS owned, AWS managed a customer managed keys

### AWS owned keys

AWS ich vlastní a spravuje naprieč viacerými accounts. Zákazník ich priamo nevidí ani nespravuje.

### AWS managed keys

Sú v zákazníckom account-e, ale policy a lifecycle spravuje AWS service. Typicky majú alias ako `aws/<service>`.

### Customer managed keys

Zákazník spravuje:

- key policy,
- aliases,
- enable/disable,
- rotation configuration,
- deletion schedule,
- grants a monitoring.

Customer managed key poskytuje väčšiu kontrolu, ale aj vyšší operations a lockout risk.

## 4. Envelope encryption

KMS nie je určený na priame šifrovanie veľkých dát.

Typický flow:

```text
GenerateDataKey
→ plaintext data key + encrypted data key
→ aplikácia zašifruje dáta plaintext data keyom
→ plaintext key odstráni z memory
→ uloží ciphertext + encrypted data key

Decrypt
→ KMS decrypt-ne encrypted data key
→ aplikácia decrypt-ne dáta
```

Výhody:

- veľké dáta sa šifrujú lokálne efektívnym symmetric algoritmom,
- master KMS key neopúšťa KMS boundary,
- access možno auditovať a centrálne zablokovať,
- jeden KMS key môže chrániť veľa data keys.

## 5. Key policy

Každý KMS key má key policy. Na rozdiel od mnohých AWS resources je key policy fundamentálny authorization contract.

No principal nemá automatické právo key používať iba preto, že key vytvoril. Access musí vyplývať z key policy, IAM policy alebo grant modelu a nesmie byť explicitne denied.

Key policy má oddeľovať:

- key administrators,
- key users,
- service integrations,
- cross-account principals,
- grants management,
- deletion/disable operations.

Key administrator nemusí mať `kms:Decrypt`.

## 6. IAM policies a KMS

IAM policy môže udeľovať KMS permissions iba v súlade s key policy modelom. Pre customer managed key sa často používa key-policy statement, ktorý umožní account IAM delegation.

Pri `AccessDenied` over:

- skutočný principal/session,
- key ARN a Region,
- key policy,
- IAM policy,
- SCP/RCP/boundary/session policy,
- grant,
- VPC endpoint policy,
- encryption context/condition,
- service-specific calling model.

## 7. KMS grants

Grant poskytuje dočasnejší alebo programatický permission model na konkrétny key.

AWS services často používajú grants na encrypted resources.

Rizikové permission:

- `kms:CreateGrant`,
- broad grantee principal,
- chýbajúce constraints,
- stale grants po resource deletion.

Používaj `kms:GrantIsForAWSResource` a encryption-context constraints podľa service contractu, keď sú vhodné.

## 8. Encryption context

Encryption context je non-secret key-value context kryptograficky viazaný na operation pri podporovanom symmetric model-e.

Použitie:

- integrity binding,
- policy conditions,
- audit context,
- oddelenie tenants/resources.

Pri decrypt musí byť context totožný s encrypt contextom. Context sa môže objaviť v CloudTrail, preto doň nepatria secrets alebo osobné údaje.

## 9. KMS aliases

Alias je human-readable pointer na KMS key.

Použitie:

- stable application reference,
- controlled key replacement,
- environment naming.

Alias nie je key identity. Policies a audit často potrebujú key ARN/ID. Zmena alias targetu neprešifruje existujúce dáta.

## 10. Key rotation

Rozlišuj:

- automatic rotation key materialu pre podporovaný customer managed key model,
- on-demand rotation podľa aktuálnych capabilities,
- vytvorenie nového key a re-encryption migration,
- imported/external key material rotation,
- application credential rotation.

Rotácia KMS key materialu nemení key ID a staré key material zostáva dostupné na decrypt starších ciphertextov. Zmena aliasu na nový key sama neumožní decrypt dát chránených starým keyom.

## 11. Disable a deletion

Disable key okamžite blokuje väčšinu cryptographic use. Scheduled deletion je high-impact operácia s waiting periodom.

Pred disable/delete:

- identifikuj encrypted resources,
- analyzuj CloudTrail use,
- over grants a aliases,
- testuj recovery,
- zachovaj rollback window,
- použij approvals a alerts.

Zmazaný KMS key môže spôsobiť nenávratnú stratu dát.

## 12. Multi-Region keys

Multi-Region keys majú related key material v rôznych Regions, ale každý key resource má vlastnú policy, grants a lifecycle.

Použitie:

- client-side encryption/decryption v rôznych Regions,
- applications vyžadujúce rovnaký key identity/material contract.

Nie sú automatickou replikáciou encrypted data ani všeobecnou DR konfiguráciou služby.

## 13. KMS service integration

AWS services používajú KMS cez odlišné calling patterns:

- service volá KMS v mene principalu,
- service používa grant,
- service-linked role,
- resource policy a encryption context,
- direct application call.

Preto `kms:Decrypt` na IAM role nemusí stačiť. Over service documentation, key policy, source ARN/account conditions a grants.

## 14. KMS observability

Sleduj:

- CloudTrail KMS API calls,
- `AccessDenied`, disabled/pending deletion,
- key policy/grant changes,
- unusual decrypt volume,
- cross-account usage,
- rotation state,
- alias changes,
- imported key material expiration.

CloudTrail event môže obsahovať encryption context; klasifikuj ho ako audit metadata.

## 15. Secrets Manager secret model

Secret obsahuje:

- ARN a name,
- metadata/tags,
- KMS key association,
- versions,
- staging labels,
- rotation configuration,
- optional resource policy,
- replication configuration.

Secret value môže byť string alebo binary podľa API.

Secrets Manager šifruje secret value envelope encryption modelom. Secret name, description, tags a niektoré metadata nie sú secret ciphertext; nedávaj citlivé hodnoty do názvov a tagov.

## 16. Secret versions a staging labels

Každá zmena value vytvorí version.

Bežné labels:

- `AWSCURRENT`,
- `AWSPREVIOUS`,
- `AWSPENDING` počas rotation.

Aplikácia typicky číta `AWSCURRENT`. Rotation workflow presúva labels medzi versions.

Hardcode konkrétne version ID iba pri explicitnom immutable recovery alebo test use case.

## 17. Retrieval

Aplikácia potrebuje:

- `secretsmanager:GetSecretValue`,
- KMS decrypt permission podľa key modelu,
- network path alebo VPC endpoint,
- resource policy/cross-account alignment,
- error a cache strategy.

Retrieve pri každom requeste je často zbytočne pomalé a drahé. Použi client-side caching s TTL a rotation-aware refreshom.

Cache nesmie držať secret dlhšie než akceptované revocation/rotation window.

## 18. Rotation

Rotation musí zmeniť secret value aj credentials v target service.

Aktuálne Secrets Manager podporuje podľa secret typu:

- managed rotation,
- managed external secret rotation,
- Lambda-based rotation.

Lambda-based rotation typicky používa kroky:

```text
createSecret
→ setSecret
→ testSecret
→ finishSecret
```

Workflow musí byť idempotentný, bezpečný pri retry a schopný rozlíšiť `AWSPENDING` version.

## 19. Single-user a alternating-users rotation

### Single-user

Rotuje credentials jedného principalu. Rotation function potrebuje existujúce oprávnenia na zmenu credentials.

### Alternating users

Strieda dve identities, aby aplikácia mohla pokračovať počas rotation. Vyžaduje master/admin secret a zložitejší privilege model.

Výber závisí od target service, availability a security requirements.

## 20. Rotation schedule

Secrets Manager podporuje rate alebo cron schedule s rotation window. Aktuálna dokumentácia umožňuje pri podporovanom modeli rotáciu až každé štyri hodiny.

Schedule v UTC a window semantics musia byť zosúladené s maintenance, downstream availability a monitoringom.

Častá rotácia bez client cache refreshu môže zvyšovať authentication failures.

## 21. Secret resource policy

Resource policy môže umožniť cross-account access.

Bezpečný model potrebuje:

- konkrétny principal,
- organization/account conditions,
- KMS key cross-account policy,
- identity-based allow v caller account-e,
- blokovanie public/broad policy,
- CloudTrail monitoring.

AWS managed key `aws/secretsmanager` nie je vhodný pre cross-account secret access; typicky potrebuješ customer managed KMS key.

## 22. Secret replication

Secret možno replikovať do ďalších Regions podľa podporovaného modelu.

Rieš:

- per-Region KMS key,
- replication status,
- rotation source-of-truth,
- application failover config,
- resource policy,
- Region-specific endpoint,
- deletion/recovery behavior.

Replicated secret sám neprepne application traffic ani nereplikuje target database credentials mimo rotation designu.

## 23. Deletion a recovery window

Secret deletion používa recovery window podľa konfigurácie. Počas scheduled deletion nie je secret normálne dostupný.

Pred deletion:

- over consumers cez CloudTrail a inventory,
- disable rotation/integrations podľa workflowu,
- test application replacement,
- zachovaj recovery window,
- alert na force deletion.

## 24. Secrets Manager oproti Parameter Store

### Secrets Manager

- natívny secret lifecycle,
- versions/staging labels,
- automatic rotation,
- managed database integrations,
- cross-Region replication podľa capability.

### Parameter Store

- configuration hierarchy,
- String/StringList/SecureString,
- jednoduchšie config a secret use cases,
- Systems Manager integration,
- odlišný pricing/tier/throughput model.

Voľ podľa lifecycle contractu, nie iba podľa toho, že oba vedia uložiť encrypted string.

## 25. Application design

Aplikácia má:

- používať workload identity, nie bootstrap access keys,
- načítať secret cez SDK/provider,
- cache-ovať s bezpečným TTL,
- refresh-nuť po authentication failure kontrolovaným spôsobom,
- neloggovať secret,
- podporovať overlapping credentials počas rotation podľa modelu,
- mať timeout a circuit breaker,
- alarmovať retrieval/rotation failures.

Secret injection do environment variable môže zanechať hodnotu v process environment a deployment metadata surfaces. Runtime retrieval poskytuje lepší rotation model, ale pridáva dependency.

## 26. Troubleshooting KMS `AccessDenied`

Postup:

```text
správny account/Region/key ARN
→ key enabled a nie pending deletion
→ skutočný caller
→ key policy
→ IAM allow
→ SCP/boundary/session policy
→ grant
→ encryption context/conditions
→ VPC endpoint policy
→ service-specific calling path
```

Bežná chyba je overiť iba IAM policy a ignorovať key policy.

## 27. Troubleshooting encrypted AWS resource

Príklad EBS/RDS/S3 failure:

- key disabled,
- service grant chýba,
- key policy neumožňuje service/caller,
- cross-account snapshot/resource používa iný key,
- source Region/key mismatch,
- principal vie resource vytvoriť, ale nevie použiť key,
- alias smeruje na iný key.

Zachovaj resource event, KMS CloudTrail request a exact key ARN.

## 28. Troubleshooting secret retrieval

### `AccessDeniedException`

Over Secrets Manager IAM/resource policy, KMS key policy, SCP, endpoint policy a version stage.

### Timeout

Over DNS, NAT/interface endpoint, SG/NACL, endpoint policy a SDK timeout.

### Aplikácia používa staré credentials

Over cache TTL, connection pool, `AWSCURRENT`, rotation completion a target service state.

### Rotation `Failed`

Over Lambda/managed rotation logs, `AWSPENDING`, target connectivity, admin credentials, KMS permissions a idempotency.

### Secret existuje v inom Regione

Secrets Manager je regional service. Over Region, replication a application config.

## 29. Rotation incident workflow

1. zastav automatické retries, ak preťažujú target,
2. zachovaj secret versions/staging labels a rotation logs,
3. identifikuj credentials platné v target service,
4. over consumers a cache,
5. dokonči alebo bezpečne rollback-ni pending version,
6. obnov `AWSCURRENT` consistency,
7. testuj authentication,
8. re-enable rotation až po root-cause oprave.

Ručné presúvanie staging labels bez overenia target credentials môže odstaviť všetkých consumers.

## 30. SOA-C03 mapovanie

- **Domain 1** — KMS/Secrets CloudTrail monitoring, rotation alarms a retrieval analysis.
- **Domain 2** — multi-Region keys/secrets, recovery, deletion windows a credential continuity.
- **Domain 3** — key/secret provisioning, aliases, rotation automation a IaC.
- **Domain 4** — hlavná kapitola pre encryption, key policy, grants, secrets, least privilege a compliance.
- **Domain 5** — private endpoints, cross-account/Region connectivity a service integrations.

Praktické drilly:

- encrypted EBS launch zlyhá pre KMS key policy,
- Secrets Manager retrieval blokuje endpoint policy,
- rotation Lambda nevie dosiahnuť private RDS,
- application cache drží staré credentials,
- cross-account secret používa AWS-managed key,
- KMS key je pending deletion,
- alias bol premapovaný bez re-encryption plánu.

## 31. Anti-patterny

### KMS key admin má automaticky decrypt všetkých dát

Porušuje separation of duties.

### Broad `kms:*` na `*`

Umožňuje high-impact key administration a cryptographic use naprieč keys.

### Key deletion ako cleanup

Môže nenávratne zničiť prístup k dátam.

### Secret v environment variable bez rotation modelu

Aplikácia drží starú hodnotu až do restartu a môže ju leak-nuť.

### Secret načítaný pri každom requeste

Zvyšuje latency, cost a dependency pressure.

### Rotation zapnutá bez testu consumers

Target credentials sa zmenia, ale clients nevedia refresh-nuť.

### Citlivé dáta v secret name/tag alebo encryption context

Tieto metadata môžu byť viditeľné v audit/configuration surfaces.

## 32. Kontrolné otázky

1. Čo je envelope encryption?
2. Ako sa líši AWS managed a customer managed KMS key?
3. Prečo key policy nemožno ignorovať?
4. Kedy sa používajú KMS grants?
5. Čo robí encryption context?
6. Prečo alias change nere-encryptuje dáta?
7. Ako fungujú secret versions a staging labels?
8. Čo musí rotation zmeniť okrem secret value?
9. Kedy použiť Secrets Manager a kedy Parameter Store?
10. Ktoré vrstvy preveríš pri secret retrieval `AccessDenied`?

## Glossary impact

Relevantné pojmy: AWS KMS, KMS key, customer managed key, AWS managed key, key policy, KMS grant, envelope encryption, data key, encryption context, KMS alias, key rotation, multi-Region key, AWS Secrets Manager, secret version, staging label, `AWSCURRENT`, `AWSPENDING`, secret rotation, managed rotation, Lambda rotation, secret resource policy, secret replication a recovery window.

## Oficiálna dokumentácia

- [AWS KMS Developer Guide](https://docs.aws.amazon.com/kms/latest/developerguide/overview.html)
- [AWS KMS concepts](https://docs.aws.amazon.com/kms/latest/developerguide/concepts-intro.html)
- [Key policies](https://docs.aws.amazon.com/kms/latest/developerguide/key-policies.html)
- [KMS grants](https://docs.aws.amazon.com/kms/latest/developerguide/grants.html)
- [KMS cryptography essentials](https://docs.aws.amazon.com/kms/latest/developerguide/kms-cryptography.html)
- [AWS Secrets Manager User Guide](https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html)
- [Secrets Manager encryption](https://docs.aws.amazon.com/secretsmanager/latest/userguide/security-encryption.html)
- [Rotate Secrets Manager secrets](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html)
- [Secrets Manager best practices](https://docs.aws.amazon.com/secretsmanager/latest/userguide/best-practices.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Systems Manager](systems-manager.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
