# AWS protection, recovery, architecture-risk and value lifecycle glossary entries

## Protected-value subject — AWS

Versionovaná identita business value alebo credentialu, KMS key/materialu, secret version/stage, target credentialu, consumer-loaded state-u a required business outcome-u použitá pri encryption a secret lifecycle reasoning. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## KMS logical key identity

Dlhodobá KMS key identity viazaná na key ID/ARN, policy, state, usage, origin, aliases a grants; môže prežiť viac key-material rotations. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Key-material generation — KMS

Konkrétna cryptographic-material generation používaná KMS key-om po creation alebo rotation, pričom logical key ID môže zostať nezmenené. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Envelope-encryption subject

Exact payload/ciphertext, plaintext a encrypted data-key identity, protecting KMS key/material, encryption context a caller/service path potrebné na encrypt/decrypt reasoning. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Cryptographic authorization verdict — KMS

Effective allow alebo deny výsledok z caller/session identity, IAM/SCP/boundary/session policies, key policy, grant constraints, key state, encryption context, endpoint policy a service calling pathu. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Encryption-context binding

Cryptographic väzba ciphertext operation na exact non-secret key-value context, ktorý musí byť zhodný pri decrypt a môže byť použitý v KMS policy/grant conditions. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Key dependency manifest — KMS

Versionovaný inventory encrypted resources, ciphertext/data-key histories, grants, aliases, cross-account consumers, backups a recovery paths potrebný pred disable alebo deletion KMS key-u. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Secret lifecycle subject

Exact secret ARN, metadata/KMS generation, version IDs, staging labels, rotation workflow, target credential principals, consumer cohorts a loaded-state evidence. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Target credential generation

Credential value a principal state, ktoré target database, provider alebo service aktuálne akceptuje; nemusí sa zhodovať so secret version označenou `AWSCURRENT`. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Consumer-loaded secret state

Secret version a credential generation skutočne načítaná konkrétnym processom, taskom, Lambda environmentom, sidecarom alebo connection poolom. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Staging-label transition — Secrets Manager

Riadený presun labelov ako `AWSPENDING`, `AWSCURRENT` a `AWSPREVIOUS` medzi immutable secret versions; nepreukazuje sám target ani consumer state. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Rotation split-brain — secret lifecycle

Failure stav, v ktorom secret-store labels, target-valid credentials a consumer-loaded generations ukazujú na odlišné values alebo principals. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Consumer refresh gate — secret rotation

Evidence gate vyžadujúci, aby intended consumer cohorts načítali novú secret version, obnovili connections a úspešne autentizovali pred revocation old credentialu. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Credential overlap window

Riadené obdobie, počas ktorého old a new credentials môžu byť súčasne platné, aby sa dokončil mixed-cohort refresh bez outage-u; musí mať bounded duration a revocation verdict. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Secret recovery acceptance verdict

Closure dôkaz, že current labels, target credentials, consumer-loaded state, privileges, replicas a business authentication journey sú zosúladené a retired credentials zlyhávajú. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Key retirement verdict

Rozhodnutie, že nový encrypt path je active, všetky retained ciphertext/backups majú tested decrypt path, grants/consumers sú inventoried a old KMS key možno bezpečne disable-nuť alebo delete-nuť. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Recovery subject — AWS Backup

Versionovaná identita workload data, RPO/RTO, backup plan/assignment, recovery points, copy/vault/key lineage, recovery manifest, restore target a business validation. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Protected-resource generation — AWS Backup

Exact source resource ARN/configuration/data generation, ktorá má byť vybraná effective backup assignmentom a zachytená konkrétnym jobom. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Effective backup coverage

Dôkaz, že authoritative critical-resource inventory je skutočne vybraný current plan/assignmentom, má fresh source recovery point, required isolated copy a restore-test coverage. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Recovery-point generation

Konkrétny service-specific captured state s recovery-point ARN, source identity, timestamps, vault, encryption, retention a restore metadata. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Isolated-copy acceptance

Dôkaz, že required cross-account/Region alebo locked-vault copy job dokončil intended destination recovery point s correct key, retention a restore access. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Clean recovery candidate

Recovery point alebo manifest set preukázateľne vytvorený pred corruption/compromise boundary a vhodný pre business recovery po zohľadnení RPO a reconciliation. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Business-dirty recovery point

Technicky validný a restore-nuteľný recovery point, ktorý už obsahuje logical corruption, attacker changes alebo business-inconsistent state. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Recovery manifest — AWS

Immutable mapping exact database restore time/log markerov, object versions/checksums, filesystem points, artifact/schema, keys/secrets, IaC a reconciliation cursoru do jednej recoverable generation. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Distributed recovery consistency

Požiadavka, aby independently captured database, object, file, queue a external-system states tvorili logicky kompatibilný business checkpoint. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Restore generation — AWS

Nový resource topology vytvorený z exact recovery pointu a restore metadata s vlastnou network, identity, encryption, schema a initialization state identity. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Restore authority

Time-bound principal, role a approval scope oprávnený vybrať recovery manifest, vytvoriť resources s protected data a rozhodnúť o validation/promotion. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Recovery fencing

Mechanizmus, ktorý zabráni corrupted alebo old production writers spracúvať nové writes/side effects počas restore, reconciliation a traffic cutoveru. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Realized RPO — AWS recovery

Skutočná data-loss exposure odvodená od incident/corruption boundary, selected clean recovery generation, capture/copy gaps a unreconciled external side effects. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Realized RTO — AWS recovery

End-to-end interval od detection/decision cez access, restore, initialization, dependencies, validation, reconciliation a cutover po business acceptance. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Restore-validation contract

Explicitné technical, data, schema, business, performance, isolation a cleanup checks, ktoré musia prejsť po restore-testing alebo incident restore jobe. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Logically air-gapped restore access

Controlled temporary path, cez ktorý recovery account môže restore-nuť recovery points z logically air-gapped vaultu po required authorization/approval. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Multi-party recovery approval

Workflow vyžadujúci súhlas viacerých independent trusted approvers pred high-impact restore-access operáciou nad logically air-gapped vaultom. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Recovery acceptance verdict — AWS

Closure dôkaz, že selected recovery generation je clean a consistent, application/business invariants fungujú v RTO/RPO, old writers sú fenced a forbidden exposure/duplicate outcomes nevznikajú. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Workload-review subject — Well-Architected

Versionovaná identita business workloadu, release/topology, owners, constraints, lens/review generation, evidence window a expected outcomes hodnotená Well-Architected reviewom. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Evidence cut-off — architecture review

Časová hranica určujúca, ktoré configuration, telemetry, test, incident, cost a policy evidence patria do konkrétnej review generation. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Expected evidence inventory — review

Vopred definované observation sources, owners, freshness limits a allowed/forbidden outcomes potrebné na zodpovedanie review questions. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Applicability verdict — Well-Architected

Explicitné rozhodnutie, či best practice je implemented, partial, missing, not applicable s evidence alebo unknown pre chýbajúce dôkazy. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Configured control

Policy, resource, alarm, redundancy alebo runbook, ktorý existuje v deklarovanom/current state-e, ale ešte nemusí byť preukázane effective. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Effective control

Control otestovaný alebo pozorovaný proti intended threat/failure a preukázane vytvárajúci required technical a business outcome. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Risk-closure lifecycle

Flow od evidence-backed failure scenario a risk decisionu cez owned improvement change, validation a residual-risk verdict po milestone a re-review. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Causal risk statement

Risk description spájajúci cause, failure mechanism a konkrétny business/technical impact namiesto vágneho control alebo checklist findingu. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Cross-pillar decision — Well-Architected

Versionované architecture rozhodnutie zaznamenávajúce benefit, trade-offs, guardrails a validation naprieč reliability, security, performance, operations, cost a sustainability outcomes. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Expiring risk acceptance

Explicitné prijatie residual risku accountable ownerom s rationale, compensating controls, expiry a re-review triggers. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Improvement validation — Well-Architected

Subject-bound test a evidence, ktoré preukazujú, že implemented improvement odstránil failure mechanism bez vytvorenia forbidden outcomes. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Milestone generation — Well-Architected

Immutable snapshot konkrétnej review/risk/evidence state generácie používaný na porovnanie progressu, nie ako perpetual current-state proof. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Review-staleness trigger

Zmena release-u, topology, provider, SLO/RTO/RPO, incident, test failure alebo risk expiry, ktorá invaliduje affected Well-Architected answers a vyžaduje re-review. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Business-outcome lens

Custom Well-Architected lens, ktorá pridáva domain-specific failure scenarios, evidence a acceptance criteria viazané na business capability. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Risk closure verdict — Well-Architected

Dôkaz, že improvement bol nasadený, intended failure scenario bol otestovaný, forbidden outcomes nevznikli a residual risk je odstránený alebo explicitne accepted. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Continuous Well-Architected loop

Priebežné prepájanie architecture decisions, deployment evidence, SLO/security/cost signals, failure drills, findings, improvements, validation a milestones. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## FinOps subject

Versionovaná identita payer/workloadu, billing period/dataset, pricing, allocation, commitments, business unit, owners, SLO guardrails a expected value outcome. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Billing-generation identity

Exact billing dataset, period, payer scope, pricing/discount rules, cost metric a finalized/estimated state použitý pri cost reasoning. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Cost-data cut-off

Timestamp freshness boundary, po ktorú sú line items a adjustments zahrnuté v konkrétnej cost report alebo incident analysis generácii. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Unit-definition contract — FinOps

Explicitná definícia validnej business jednotky, napríklad successful settled payment, ktorá zabraňuje zlepšeniu unit costu cez počítanie retry alebo failed worku ako value. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Attributed unit cost

Total spoľahlivo allocated workload cost vydelený validným business outcome volume-om v comparable period a cost view. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Allocation-rule generation

Versionovaná sada tag, account, Cost Category a shared-cost rules použitá na mapovanie billing line items k owners/products. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Effective allocation coverage

Podiel in-scope spendu priradený správnemu ownerovi cez dôveryhodné a validné dimensions, nie iba syntakticky vložený do default bucketu. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Shared-cost driver

Measured alebo business-agreed usage dimension, napríklad bytes, requests, vCPU-hours alebo build minutes, použitá na rozdelenie shared platform costu. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Cost-view identity

Exact unblended, blended, amortized, net amortized alebo invoice perspective použitá v report-e; zmena view môže zmeniť trend bez zmeny usage. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Recommendation-to-realization gap

Rozdiel medzi estimated savings recommendation a skutočne implemented, stable a normalized measured financial outcome. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Normalized realized savings

Post-change cost reduction očistená o business volume, seasonality, pricing/commitments, migration cost a secondary impacts. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Commitment baseline — AWS cost

Forecast stabilného useful eligible usage po odstránení incident, retry, migration a temporary waste, používaný pred Savings Plan alebo reservation purchase. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Incident usage — FinOps

Metered compute, request, transfer, storage alebo telemetry volume vytvorený failure amplification, attackom alebo remediation a nevhodný ako normal commitment alebo forecast baseline. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Cost containment verdict

Rozhodnutie, že bounded action zastavila rastúci spend driver bez neprimeraného business, recovery, security alebo evidence damage. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Financial data freshness

Informácia o delay, estimated/finalized state a late adjustments cost datasetu potrebná pred budget, anomaly alebo incident decisionom. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Cross-pillar optimization guardrail

SLO, security, recovery, performance alebo capacity condition, ktorá musí zostať splnená počas cost optimization change-u. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## FinOps closure verdict

Dôkaz, že cost driver bol kauzálne identifikovaný, change bezpečne nasadený, business/SLO guardrails zachované a normalized realized value potvrdená v complete data periods. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).