# Systems Manager

AWS Systems Manager poskytuje centralizované nástroje na správu nodes a AWS resources naprieč accounts, Regions, on-premises a multicloud prostrediami. Nie je to jeden agent ani jeden patching tool; je to sada capabilities pre inventory, remote operations, session access, patching, compliance, automation, parameter storage a fleet governance.

## 1. Mentálny model

```text
managed node alebo AWS resource
→ identity, agent/network a registration
→ Systems Manager control plane
→ document/runbook/configuration
→ command, session, patch alebo automation execution
→ output, compliance, audit a remediation
```

Rozlišuj:

- **managed node** — EC2 alebo non-EC2 machine zaregistrovaná v Systems Manager,
- **SSM Agent** — node-side component pre podporované node operácie,
- **SSM document** — versionovaný command/session/policy/automation contract,
- **Automation runbook** — workflow nad AWS APIs a nodes,
- **Run Command** — one-time remote command na managed nodes,
- **Session Manager** — auditovateľný shell/port-forwarding access bez inbound SSH/RDP,
- **Patch Manager** — patch policy, scan/install a compliance,
- **State Manager** — periodická desired-state association.

## 2. Managed node prerequisites

Node potrebuje:

- podporovaný a spustený SSM Agent,
- IAM instance profile alebo hybrid activation identity,
- network path k potrebným Systems Manager endpoints,
- správny Region,
- time synchronization,
- DNS a TLS trust,
- dostatočný disk/CPU pre agent a operácie.

Private subnet môže používať NAT alebo interface VPC endpoints podľa required service setu. Jeden endpoint často nestačí; over presné Systems Manager, messaging, logs, S3 a KMS dependencies použitej capability.

## 3. Fleet Manager

Fleet Manager poskytuje central view a operational actions pre managed nodes.

Použitie:

- OS a node metadata,
- filesystem/process/user visibility podľa capabilities,
- remote management,
- troubleshooting fleet enrollment,
- cross-account/Region operations podľa governance modelu.

Inventory visibility nie je automaticky real-time CMDB. Data freshness, agent health a collection configuration musia byť monitorované.

## 4. Inventory

Systems Manager Inventory zbiera metadata, napríklad:

- applications,
- AWS components,
- network configuration,
- files,
- Windows updates/roles,
- custom inventory.

Inventory je vhodné pre asset discovery a compliance evidence, ale nezaručuje, že package je bezpečný alebo správne nakonfigurovaný.

## 5. Run Command

Run Command vykonáva command document na jednom alebo viacerých managed nodes bez interactive loginu.

Capabilities:

- targets cez instance IDs alebo tags,
- concurrency a error controls,
- command timeout,
- output do S3/CloudWatch Logs podľa konfigurácie,
- notifications,
- per-node execution status.

Run Command je vhodný pre:

- one-time configuration,
- collection logs,
- service restart,
- controlled remediation,
- package/script execution.

Nie je vhodné používať ho ako neauditovaný ad-hoc shell bez versioned documentu a validation.

## 6. Run Command rate controls

Pri fleet operácii nastav:

- **max concurrency** — koľko nodes beží paralelne,
- **max errors** — koľko failures je tolerovaných pred zastavením distribúcie,
- target batches podľa environmentu/AZ,
- timeout,
- output retention,
- post-command validation.

`100%` concurrency pri chybnom príkaze môže poškodiť celý fleet naraz.

## 7. Session Manager

Session Manager umožňuje remote access bez inbound management portu a bez bežného bastion modelu.

Výhody:

- IAM-based authorization,
- žiadne long-lived SSH keys ako základný model,
- CloudTrail audit API session lifecycle,
- optional session logs do S3/CloudWatch Logs podľa session type/configuration,
- port forwarding a shell capabilities.

Hranice:

- encrypted session obsah nie je pri všetkých session typoch logovateľný rovnakým spôsobom,
- IAM permission na `StartSession` musí byť resource-scoped,
- document a session preferences sú security contract,
- local user/OS privilege na node stále rozhoduje,
- KMS/log destinations musia byť dostupné.

## 8. State Manager

State Manager associations periodicky aplikujú document na target nodes.

Použitie:

- agent/config baseline,
- recurring scripts,
- security configuration,
- package state,
- inventory collection.

Association musí byť idempotentná. Non-idempotentný command spustený periodicky vytvorí drift alebo opakované side effects.

## 9. Patch Manager

Patch Manager automatizuje scan a inštaláciu patches na managed nodes.

Aktuálna AWS dokumentácia odporúča patch policies cez Quick Setup pre organization/account/Region-scale konfiguráciu.

Kľúčové pojmy:

- patch baseline,
- patch group/tag targeting,
- scan oproti install,
- maintenance window alebo patch policy schedule,
- reboot option,
- compliance state,
- approval delay,
- rejected/approved patches.

Patching nie je iba „install all updates“; potrebuje rollout rings, application validation a rollback/replacement model.

## 10. Patch rollout stratégia

```text
inventory a baseline
→ scan
→ non-production/canary ring
→ application smoke tests
→ controlled production waves
→ compliance verification
→ exception/remediation
```

Pre immutable fleets môže byť vhodnejšie vytvoriť novú patched AMI a vykonať instance refresh. Patch Manager zostáva relevantný pre long-lived nodes alebo emergency patching podľa operating modelu.

## 11. Maintenance Windows

Maintenance Window definuje čas, targets, tasks, priority a concurrency/error controls.

Použitie:

- patching,
- commands,
- Automation,
- Lambda/Step Functions integrations podľa task type-u.

Maintenance window nie je business approval ani application drain. Pred taskom môže byť potrebné vyradiť node z load balancera a po tasku vykonať health validation.

## 12. Automation runbooks

Automation runbook je YAML/JSON workflow so sequential steps a outputs.

Môže používať actions pre:

- AWS API calls,
- scripts,
- approvals,
- branching,
- resource creation/update,
- command execution,
- waits a assertions.

AWS poskytuje predefined runbooks; custom runbook má mať versioning, review, test a ownera.

## 13. Automation execution role

Automation môže bežať:

- v kontexte initiator permissions,
- cez explicitný assume role/service role.

Explicitný automation role znižuje závislosť na broad permissions používateľa a umožňuje presný audited contract.

Chráň:

- `iam:PassRole`,
- runbook update permissions,
- high-impact actions,
- cross-account assume role,
- approval bypass,
- parameter injection.

## 14. Automation rate controls

Automation supports targets, concurrency a error threshold.

Použitie:

- postupná remediation naprieč fleetom,
- zastavenie po failure prahu,
- canary wave,
- account/Region rollout,
- adaptívna concurrency podľa aktuálnych service capabilities.

Každý runbook má mať explicitnú success validation; API call success nemusí znamenať healthy application.

## 15. Automation rollback

Rollback môže byť:

- explicitný reverse step,
- conditional branch,
- restore zo snapshotu,
- redeploy previous resource version,
- manual escalation.

Nie všetky actions sú reverzibilné. Runbook má označiť durable side effects, point of no return a required approval.

## 16. Parameter Store

Systems Manager Parameter Store uchováva configuration a secrets podľa parameter type-u:

- `String`,
- `StringList`,
- `SecureString` s KMS.

Use cases:

- runtime config,
- shared IDs/ARNs,
- feature settings,
- bootstrap parameters,
- menej komplexné secret use cases.

Secrets Manager je vhodnejší, keď je potrebná natívna secret rotation, version-stage workflow a service-specific secret lifecycle.

## 17. Parameter hierarchy a policies

Hierarchické names umožňujú environment/application scope.

Príklad:

```text
/prod/payments/api/url
/prod/payments/db/password
```

IAM môže obmedziť path, ale recursive APIs a explicit deny behavior treba testovať. Parameter policies môžu podľa tier/capability riešiť expiration alebo notifications.

## 18. SecureString a KMS

`SecureString` potrebuje:

- Parameter Store permission,
- `kms:Decrypt` na relevantný KMS key,
- key policy/IAM alignment,
- encryption context a cross-account model podľa use case.

Používateľ, ktorý vie čítať ciphertext parameter, nemusí automaticky vedieť decrypt-nuť hodnotu.

## 19. Quick Setup

Quick Setup pomáha aplikovať organization/account/Region-wide Systems Manager configurations.

Použitie:

- host management baseline,
- patch policies,
- inventory,
- agent/update konfigurácie,
- service-specific setup podľa aktuálnych capabilities.

Over StackSets/deployment status, target OUs/accounts/Regions a drift. Central setup môže zlyhať iba v časti organization.

## 20. Change Manager a OpsCenter

Podľa dostupnosti a operating modelu môže Systems Manager poskytovať change-request a operations-item workflows.

Dôležité je oddeliť:

- detection,
- approval,
- execution,
- evidence,
- post-change validation,
- incident/problem management.

Tooling nenahrádza jasný ownership a escalation proces.

## 21. Hybrid a multicloud nodes

Non-EC2 machines možno registrovať pomocou hybrid activation alebo novšieho podporovaného registration modelu.

Rieš:

- identity lifecycle,
- activation expiration/limit,
- network/proxy,
- duplicate machine identity pri cloning,
- OS support,
- certificate/credential rotation,
- data residency.

## 22. Security model

Chráň najmä:

- `ssm:SendCommand`,
- `ssm:StartSession`,
- document create/update,
- Automation execution,
- `iam:PassRole`,
- Parameter Store reads,
- target selection cez tags,
- session/command log destinations.

Tag-based targeting môže byť privilege-escalation boundary, ak používateľ vie zároveň meniť target tags.

## 23. Audit a observability

Zachovaj:

- CloudTrail API events,
- command/automation execution IDs,
- document name a version,
- caller/session identity,
- targets,
- output/log destination,
- per-step/node status,
- approval record,
- change ticket/correlation ID,
- post-action validation.

Node local logs SSM Agenta sú dôležité, keď control plane ukazuje iba timeout alebo delivery failure.

## 24. Troubleshooting managed node offline

Postup:

```text
správny account a Region
→ node existuje a beží
→ SSM Agent service/logs
→ instance profile/hybrid identity
→ DNS/time/TLS
→ route/NAT/VPC endpoints
→ endpoint policy/SG/NACL
→ registration a service status
```

Časté príčiny:

- missing instance profile,
- agent stopped/outdated,
- private subnet bez required endpoints,
- proxy/TLS inspection,
- disk full,
- cloned node identity,
- wrong Region.

## 25. Troubleshooting Run Command

### `Pending` alebo `Delayed`

Over agent connectivity, target online state, service quotas a delivery timeout.

### `Failed`

Over per-node stdout/stderr, exit code, document parameters, OS compatibility a permissions.

### `DeliveryTimedOut`

Command nebol doručený v limite; nejde automaticky o script failure.

### Čiastočný fleet success

Analyzuj tags/targets, OS variants, agent versions, network segments a max-errors threshold.

## 26. Troubleshooting Session Manager

Over:

- user IAM a session document,
- node online state,
- SSM Agent version,
- plugin/client,
- KMS/log bucket/log group permissions,
- shell profile,
- endpoint path.

Session API môže uspieť, ale shell initialization zlyhať pre OS user alebo profile command.

## 27. Troubleshooting patching

Rozlišuj:

- patch nebol applicable,
- nebol approved v baseline,
- repository unreachable,
- insufficient disk,
- package conflict,
- reboot pending,
- application health failure po patchi,
- stale compliance data.

Compliance `NON_COMPLIANT` nehovorí automaticky, že install command práve zlyhal; over scan time a detailed state.

## 28. SOA-C03 mapovanie

- **Domain 1** — fleet health, inventory, compliance, command output a remediation.
- **Domain 2** — patching, maintenance, backup/recovery runbooks a operational continuity.
- **Domain 3** — Automation, documents, State Manager, Quick Setup a repeatable provisioning.
- **Domain 4** — Session Manager, least privilege, audit, Parameter Store a patch compliance.
- **Domain 5** — managed-node endpoint connectivity, hybrid nodes, DNS/proxy/VPC endpoints.

Praktické drilly:

- private EC2 node je offline pre chýbajúci endpoint,
- Run Command role nevie zapisovať output do S3,
- patch policy zasiahne production bez canary ring-u,
- Automation role nemá dependent permission,
- Session Manager logging blokuje KMS key policy,
- State Manager association nie je idempotentná,
- hybrid node clone používa duplicitnú identity.

## 29. Anti-patterny

### Run Command ako neobmedzený root shell

Obchádza versioning, review a least privilege.

### Patching 100 % fleetu naraz

Jedna chybná aktualizácia môže spôsobiť plošný výpadok.

### Session Manager bez logs a alerts

Znižuje auditability privileged accessu.

### Parameter Store ako náhrada každého secret managera

Chýba požadovaný rotation a secret lifecycle model.

### Automation runbook bez assume role

Výsledok závisí od náhodne broad permissions initiatora.

### Tags ako target selector bez tag governance

Útočník alebo chybná automation môže presmerovať privileged command.

## 30. Kontrolné otázky

1. Čo robí node managed node-om?
2. Ako sa líši Run Command od Session Manager?
3. Kedy použiť State Manager?
4. Čo znamenajú concurrency a max-errors?
5. Ako navrhneš bezpečný patch rollout?
6. Aký je rozdiel medzi Command documentom a Automation runbookom?
7. Prečo je Automation assume role dôležitá?
8. Kedy použiť Parameter Store a kedy Secrets Manager?
9. Ktoré vrstvy overíš pri offline managed node-e?
10. Prečo je tag-based targeting security boundary?

## Glossary impact

Relevantné pojmy: AWS Systems Manager, managed node, SSM Agent, SSM document, Run Command, Session Manager, State Manager, Patch Manager, patch policy, patch baseline, Maintenance Window, Automation runbook, Automation assume role, rate controls, Fleet Manager, Systems Manager Inventory, Parameter Store, SecureString, Quick Setup a hybrid activation.

## Oficiálna dokumentácia

- [AWS Systems Manager Documentation](https://docs.aws.amazon.com/systems-manager/)
- [Run Command](https://docs.aws.amazon.com/systems-manager/latest/userguide/run-command.html)
- [Session Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html)
- [Systems Manager Automation](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-automation.html)
- [Automation runbooks](https://docs.aws.amazon.com/systems-manager/latest/userguide/automation-documents.html)
- [Patch Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/patch-manager.html)
- [Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html)
