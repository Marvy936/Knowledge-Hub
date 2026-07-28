# AWS Systems Manager

AWS Systems Manager je operations control plane pre fleet nodes a AWS resources. Spája registration, identity, remote command delivery, interactive access, desired-state associations, patching, inventory, automation a parameter storage. Nezaručuje však, že control-plane request bol doručený, že script vykonal správnu zmenu, že target set bol správny ani že application po zmene funguje.

Dominantný fleet-operation lifecycle:

```text
operational alebo compliance intent
→ exact target, document a configuration generation
→ managed-node registration a eligibility
→ caller a execution authorization
→ resolved target manifest
→ rate-controlled delivery/execution
→ per-node alebo per-step result
→ resource reconciliation a reboot/drain
→ application a business validation
→ compliance/evidence publication
→ rollback, replacement alebo escalation
→ operation acceptance a closure
```

Najväčšia chyba je zameniť `Command status = Success`, `Automation step = Success` alebo `Patch compliance = COMPLIANT` za dôkaz, že správne nodes dostali správnu zmenu a production outcome zostal zdravý.

## 1. Exact fleet-operation subject

Atlas Payments používa subject `OPS-PAY-42`:

```text
management account = 100000000042
target account = 100000000142
Region = eu-central-1
application = payments-api
release = 7.18.1
load-balancer generation = ALB-PAY-19
Auto Scaling Group generation = ASG-PAY-28
AMI generations =
  canary = AMI-PAY-2026-07-28.1
  stable = AMI-PAY-2026-07-21.4

fleet inventory =
  36 production EC2 instances
  3 AZs
  4 approved canary nodes
  32 stable nodes

managed-node contract =
  SSM Agent generation = AGENT-SSM-17
  host-management configuration = DHMC-PROD-9
  instance profile generation = ROLE-EC2-PAY-23
  SSM endpoint set generation = VPCE-SSM-12
  inventory association = ASSOC-INV-18

patch operation =
  policy generation = PATCH-POL-PAY-14
  baseline generation = PATCH-BL-PAY-22
  target selector = PatchRing=prod-canary
  resolved approved target manifest = TARGET-PAY-4-NODES
  scan document/version = AWS-RunPatchBaseline / pinned version
  install operation generation = PATCH-EXEC-91
  max concurrency = 25%
  max errors = 1
  reboot option = RebootIfNeeded

automation =
  runbook = Atlas-PatchAndValidate
  version = 11
  content hash = sha256:runbook-pay-11
  assume role = ROLE-SSM-AUTO-PAY-8
  change ticket = CHG-2026-884

required outcome =
  only four approved canary nodes are patched
  nodes drain before reboot and rejoin only after application validation
  one failed canary stops the production rollout
  evidence ties caller, target, document version, patch state and business result

forbidden outcomes =
  mutable tag expands target set after approval
  100% fleet receives the patch concurrently
  command delivery success is treated as application success
  interactive privileged access bypasses audit and session policy
  State Manager repeats a non-idempotent side effect
  compliance data from an old scan is treated as current
  Automation can pass an arbitrary high-privilege role
```

Incident evidence musí zachovať caller/session, target resolution time, exact managed-node IDs, tags and generation, document name/version/hash, command or Automation execution IDs, rate controls, per-node stdout/stderr/exit status, reboot/drain timeline, patch snapshot, load-balancer eligibility a payment smoke/business results.

## 2. Managed node je realizovaný contract

Machine sa nestáva použiteľným managed node-om iba tým, že je EC2 instance. Potrebuje:

```text
supported OS a running machine
→ SSM Agent
→ machine/instance identity
→ correct account a Region registration
→ DNS, time a TLS trust
→ route/NAT alebo required VPC endpoints
→ endpoint a resource policies
→ service-side registration/heartbeat
→ capability-specific dependencies
```

Pri EC2 môže identity poskytovať instance profile alebo Default Host Management Configuration podľa zvoleného modelu. Non-EC2 nodes používajú podporovaný hybrid registration model.

`Online` znamená, že control plane nedávno videl funkčnú agent communication path. Neznamená, že node má dostatok disku, že package repository funguje, že document je kompatibilný ani že application je zdravá.

## 3. Default Host Management Configuration mení enrollment model

Default Host Management Configuration umožňuje Systems Manager spravovať vhodné EC2 instances v account/Region scope bez individuálne pripojeného instance profile-u so starším explicitným SSM permission modelom. Používa service role a Instance Identity Credentials podľa service contractu.

Prevádzkový subject stále potrebuje:

- exact account a Region, kde je configuration enabled;
- zvolenú service role;
- SSM Agent compatibility;
- metadata access a instance identity;
- endpoint connectivity;
- exclusion alebo precedence pri existujúcom instance profile;
- audit zmeny configuration;
- validation, že intended instances sa skutočne zaregistrovali.

Central enablement nie je okamžitý dôkaz úplného fleet coverage. Quick Setup alebo organization rollout môže byť successful iba v časti accounts/Regions.

## 4. Endpoint path závisí od použitej capability

Private node môže komunikovať cez NAT alebo interface VPC endpoints. Required endpoint set sa mení podľa Regionu, agent generation a capability. Systems Manager, messaging channels, S3 package/output access, CloudWatch Logs a KMS môžu tvoriť samostatné dependencies.

Diagnostický path:

```text
SSM Agent
→ DNS resolution
→ source subnet route
→ node Security Group/NACL
→ interface endpoint ENI alebo NAT
→ endpoint Security Group
→ endpoint policy
→ service authorization
→ response channel
```

Jeden vytvorený endpoint nie je všeobecná odpoveď „SSM networking je hotový“. Session channel môže fungovať, zatiaľ čo S3 output alebo patch repository path zlyháva.

## 5. SSM document je versionovaný execution contract

SSM document definuje command, session, policy alebo Automation behavior. Bezpečný operation manifest viaže:

```text
document name
+ exact version
+ content hash
+ parameters a allowed values
+ platform preconditions
+ execution role
+ target manifest
+ timeout/rate controls
+ validation a rollback
```

Použitie default version bez pinning-u môže spustiť iný content pri neskoršom execution. Broad string parameter môže umožniť command injection alebo neplánovanú resource selection.

AWS-managed documents znižujú authoring burden, ale ich behavior, parameters, supported OS a current version treba stále overiť pre exact operation.

## 6. Run Command oddeľuje delivery od script resultu

Run Command vykonáva command document na managed nodes bez interactive loginu.

Lifecycle:

```text
SendCommand accepted
→ targets resolved
→ command queued
→ agent receives invocation
→ plugin/script starts
→ exit status a output
→ command acknowledgement
→ external/application state validation
```

Stavy majú rozdielny význam:

- `Pending` alebo `Delayed` môže znamenať, že invocation ešte nebola doručená;
- `DeliveryTimedOut` znamená delivery failure, nie script failure;
- `ExecutionTimedOut` znamená, že plugin/script prekročil execution limit;
- `Failed` vyžaduje per-plugin exit/output;
- `Success` môže znamenať iba exit code 0, nie správny business outcome.

Script, ktorý vykoná `systemctl restart payments-api` a vráti 0, nedokazuje, že service sa pripojila k DB, prešla health checkom a prijala platbu.

## 7. Resolved target manifest je bezpečnostná a correctness boundary

Targets možno vyberať cez instance IDs, resource groups alebo tags podľa capability. Tag selector je dynamický query, nie immutable manifest.

```text
selector PatchRing=prod-canary
→ resolve v čase execution
→ konkrétny set managed-node IDs
→ per-node operation
```

Ak iná automation zmení tags medzi approval a execution, target set sa zmení. Ak principal smie zároveň meniť target tags a spúšťať privileged Run Command, získava nepriamu privilege-escalation cestu.

High-impact operation má pred execution materializovať a uložiť resolved target manifest, porovnať ho s approved inventory a odmietnuť nečakaný count, environment, AZ alebo ownership.

## 8. Rate controls obmedzujú blast radius

Run Command a fleet Automation používajú concurrency a error threshold podľa capability.

```text
approved target count
→ canary batch
→ max concurrency
→ per-target outcome
→ max-errors verdict
→ next wave alebo stop
```

`maxConcurrency=100%` je rýchle iba v healthy scenári. Pri zlom patchi, command-e alebo selector-e odstráni recovery cohort.

`maxErrors` nie je application error budget, pokiaľ sa počíta iba command exit status. Runbook musí previesť application smoke failure na execution failure alebo zastaviť ďalšiu wave explicitnou assertion.

Percentuálny limit pri malom fleet-e treba prepočítať na skutočný počet nodes. Zaokrúhľovanie a target-count drift môžu zmeniť intended canary size.

## 9. Output a audit evidence majú vlastný delivery path

Run Command môže posielať output do CloudWatch Logs alebo S3 podľa configuration. Control plane môže zobraziť iba skrátený output.

Evidence path potrebuje:

- destination identity;
- IAM a bucket/log-group policy;
- KMS authorization;
- network access;
- retention;
- redaction;
- command/instance/plugin correlation;
- failure alert, ak output delivery neprešla.

Citlivé environment variables, command parameters alebo secrets sa nesmú objaviť v stdout. Chýbajúci central output neznamená automaticky, že command nebežal; node-side agent a plugin logs sú diskriminačný observation point.

## 10. Session Manager je privileged access workflow

Session Manager umožňuje shell alebo podporovaný port-forwarding bez inbound SSH/RDP portu.

Lifecycle:

```text
caller authorization
→ session document a preferences
→ node eligibility/channel
→ local OS user a shell profile
→ interactive actions
→ session termination
→ API audit a podporovaný content logging
```

CloudTrail zaznamenáva session API lifecycle, nie automaticky každý shell command. Session content logging závisí od session type, encryption a configuration; pri niektorých port-forwarding alebo encrypted patterns nie je obsah dostupný na rovnaké logovanie.

Bezpečný model potrebuje:

- resource-scoped `StartSession`;
- approved session documents;
- controlled OS user/privilege;
- KMS a log destinations;
- session duration a idle timeout;
- alerts na privileged sessions;
- oddelený break-glass proces;
- zákaz broad port forwarding, ak obchádza intended network controls.

Session Manager znižuje potrebu long-lived SSH keys a bastionov. Neodstraňuje OS authorization ani potrebu sledovať, čo privileged operator zmenil.

## 11. State Manager je periodický reconciliation loop

Association opakovane aplikuje document na targets podľa schedule alebo trigger modelu.

```text
desired association generation
→ target resolution
→ periodic execution
→ current state observation
→ idempotent apply
→ compliance/result
→ ďalšia reconciliation
```

Document musí byť idempotentný. Command `append user to file`, `create payment entry` alebo `restart on every run` môže pri každej association vytvárať ďalší side effect.

State Manager je vhodný na agent/config baseline, inventory, package/configuration state alebo recurring validation. Nie je náhradou za immutable image pipeline, ak fleet operating model používa replacement.

## 12. Inventory je observation, nie automaticky CMDB truth

Systems Manager Inventory zbiera configured metadata o applications, files, network, OS a custom inventory.

Evidence freshness závisí od:

```text
association/configuration
→ agent collection
→ successful upload
→ aggregation/query
→ collection timestamp
```

Inventory môže byť stale, neúplné alebo schema-incompatible. „Package sa nachádza v Inventory“ nedokazuje, že je loaded, bezpečný alebo používaný. CMDB alebo vulnerability workflow musí zachovať source, timestamp a coverage.

## 13. Patch Manager oddeľuje scan, approval, install a application validity

Patch lifecycle:

```text
OS/repository inventory
→ patch baseline/policy resolution
→ scan applicability a approval
→ compliance snapshot
→ canary install
→ reboot decision
→ application validation
→ controlled waves
→ fresh rescan/compliance
→ exception alebo replacement
```

**Scan** zistí applicable a approved patch state. **Install** mení node. `COMPLIANT` sa vzťahuje na baseline a scan snapshot, nie na všeobecné security ani application zdravie.

Patch baseline určuje approval, rejection a delay semantics. Patch policy cez Quick Setup pomáha aplikovať organization/account/Region-scale schedule a targeting. Central policy potrebuje deployment-status a target-coverage kontrolu.

## 14. Patch compliance má timestamp a generation

Compliance verdict musí niesť:

- node identity;
- OS/platform;
- baseline/policy generation;
- scan/install operation;
- snapshot alebo repository context;
- scan time;
- installed/missing/failed state;
- reboot pending;
- exceptions;
- application acceptance.

Node môže byť `NON_COMPLIANT`, pretože scan objavil approved missing patch, nie preto, že posledný install command zlyhal. Opačne starý `COMPLIANT` scan môže maskovať nové patches alebo zmenu baseline-u.

## 15. Immutable a mutable fleet používajú odlišnú patch recovery

Pre immutable EC2 fleet je preferovaný lifecycle často:

```text
patched base/image build
→ image scan/test
→ immutable AMI generation
→ canary instances
→ application acceptance
→ ASG instance refresh
→ old instance retirement
```

In-place Patch Manager ostáva vhodný pre long-lived nodes, emergency response alebo systémy, kde image replacement nie je aktuálny operating model.

Rollback package-u nemusí byť spoľahlivý: patch môže zmeniť filesystem, kernel, database format alebo dependent packages. Immutable replacement zo známého AMI je často authoritative recovery, ale potrebuje externalized state a capacity.

## 16. Maintenance Window je scheduler, nie business approval

Maintenance Window definuje čas, targets, tasks, priority a rate controls. Nevykoná automaticky:

- change approval;
- load-balancer drain;
- application quiesce;
- dependency coordination;
- business smoke test;
- rollback decision.

Window duration a cutoff musia pokrývať command, reboot, reconnection a validation. Node, ktorý začne neskoro, nesmie zostať v nejasnom partially changed state bez follow-up.

## 17. Automation runbook je explicitná state machine

Automation spája AWS API actions, scripts, commands, waits, branches, approvals a assertions.

```text
input a preconditions
→ exact resource/target subject
→ step execution
→ output a state transition
→ branch/wait/assert
→ side-effect boundary
→ postcondition
→ success, rollback alebo escalation
```

Každý step má definovať:

- input type a allowed scope;
- execution identity;
- timeout/retry;
- idempotency;
- expected output;
- failure handling;
- irreversible side effect;
- evidence;
- postcondition.

AWS-managed runbook je reusable mechanism, nie automatické schválenie jeho použitia na production target.

## 18. Automation assume role a `iam:PassRole`

Automation môže používať caller permissions alebo explicitnú service/assume role podľa runbooku.

Explicitná role vytvára stabilnejší permission contract. Treba však chrániť:

```text
kto smie spustiť runbook
+ ktorý runbook/version
+ akú role smie pass-nuť
+ ktoré resources môže role meniť
+ ktoré parameters ovplyvňujú scope
```

Broad `iam:PassRole` spolu s editovateľným runbookom alebo arbitrary target parameterom môže viesť k privilege escalation.

Approver nesmie byť obídený zmenou default version alebo spustením rovnakej action cez iný document.

## 19. Automation success potrebuje external postcondition

AWS API môže vrátiť success pri prijatí requestu, zatiaľ čo resource sa ešte reconciliuje.

```text
automation API step success
→ controller transition
→ eventual resource state
→ runtime readiness
→ business outcome
```

Runbook musí wait/assert-nuť authoritative state a potom vykonať application validation. Pri ECS force deployment-e nestačí `UpdateService` success; treba deployment completion, target eligibility a payment smoke.

Nie všetky actions sú reverzibilné. Runbook má označiť point of no return a vybrať rollback, compensation, restore, replacement alebo manual escalation.

## 20. Parameter Store je configuration contract

Parameter Store uchováva hierarchické `String`, `StringList` a KMS-protected `SecureString` parameters.

Exact parameter subject:

```text
name/path
→ tier/type
→ version
→ value generation
→ KMS key
→ resource/IAM policy
→ consumer cache
→ runtime acceptance
```

Path-based IAM musí byť testovaný aj s recursive APIs. Principal s accessom k parent path môže podľa API/policy modelu získať descendants; explicit denies a resource patterns musia byť overené prakticky.

`SecureString` vyžaduje SSM read permission aj KMS decrypt authorization. Parameter Store nie je automatická náhrada Secrets Manager lifecycle-u, ak requirement zahŕňa managed rotation, staging labels a service-specific rotation workflow.

## 21. Quick Setup je distributed rollout

Quick Setup môže nasadiť host management, patch policies a ďalšie supported configurations naprieč accounts a Regions.

```text
central configuration
→ target OU/accounts/Regions
→ StackSets alebo service deployment
→ local roles/resources/associations
→ node enrollment/execution
→ coverage a drift validation
```

Central configuration status nesmie zakryť partial account/Region failure. Evidence má obsahovať expected target inventory, successful deployment, local effective configuration a managed-node/application result.

## 22. Hybrid a multicloud nodes

Non-EC2 machine potrebuje supported registration identity, agent a outbound connectivity.

Riziká:

- activation/registration credential lifecycle;
- cloned machine identity;
- proxy a TLS inspection;
- wrong Region;
- stale agent;
- unsupported OS;
- duplicate node IDs;
- data residency;
- deregistration pri retirement.

Cloning image po registration môže vytvoriť viac machines s rovnakou local agent identity. Golden image sa má zachytiť pred unique registration state alebo ho pri boot-e bezpečne regenerovať podľa service guidance.

## 23. Worked failure: mutable tag rozšíri patch na celý fleet

Change `CHG-2026-884` schváli patch štyroch canary nodes. Runbook používa selector `PatchRing=prod-canary`. Krátko pred execution však provisioning automation omylom priradí tento tag všetkým 36 production instances.

### Competing hypotheses

1. patch package je chybný;
2. patch repository alebo network path zlyháva;
3. SSM Agent doručuje commands oneskorene;
4. maintenance window sa prekrýva s deploymentom;
5. target selector resolve-nul wrong fleet;
6. reboot prešiel, ale application startup/dependency zlyhala.

### Discriminating evidence

CloudTrail ukáže `CreateTags` z role `ROLE-ASG-BOOTSTRAP-6` dve minúty pred `StartAutomationExecution`. Automation execution input stále obsahuje iba selector, nie approved instance manifest.

Resolved execution targets obsahujú 36 nodes. Rate control sa pri refactore zmenil na `maxConcurrency=100%`. Patch plugin na 34 nodes vráti exit code 0 a spustí reboot. Systems Manager preto vykazuje prevažne `Success`.

Load balancer evidence však ukáže, že všetky tri AZ cohorts súčasne prešli do unhealthy/draining. Dve nodes zlyhajú na package conflict; ostatné po reboot-e čakajú na secret refresh a DB connection storm. Payment success klesne.

Root cause nie je iba „zlý patch“. Je to zlyhanie target authority, absent resolved manifest, nebezpečný rate control a chýbajúca application postcondition.

### Evidence-preserving containment

- zostávajúce Automation/Run Command executions sa stopnú alebo cancel-nu podľa podporovaného state-u;
- tag mutation role sa dočasne zablokuje pre `PatchRing`;
- žiadny healthy/unpatched node sa neodstaví;
- ALB, SSM a node logs sa zachovajú;
- affected nodes sa rozdelia podľa patch/reboot/application state;
- traffic sa smeruje iba na preukázateľne healthy cohort;
- ďalší broad command sa nespúšťa „na opravu všetkého“.

### Authoritative recovery

1. approved four-node target manifest sa obnoví ako exact instance IDs/generation;
2. production tags sa vrátia podľa authoritative inventory;
3. affected stateless nodes sa nahradia z last-known-good AMI generation;
4. replacement sa vykoná po AZ waves s capacity headroomom;
5. DB/proxy connection ramp sa obmedzí;
6. nový canary AMI/patch generation sa testuje na štyroch nodes;
7. runbook version 12 používa `maxConcurrency=1`, `maxErrors=1`, drain, reboot wait, agent reconnect, ALB health a payment smoke;
8. ďalšia wave vyžaduje explicitný acceptance verdict.

Package rollback sa použije iba ak vendor/package semantics a filesystem state dokazujú bezpečnú reverzibilitu. Inak je authoritative recovery immutable replacement.

### Operation acceptance verdict

Incident je uzavretý až keď:

- exact intended four-node manifest zodpovedá approval-u;
- tag selector s neočakávaným countom operation zastaví;
- všetkých 36 nodes má známu AMI, patch, agent a application generation;
- každá AZ má healthy capacity a failure headroom;
- SSM command success koreluje s ALB eligibility a payment smoke;
- fresh patch scan/compliance nesie correct baseline a timestamp;
- Session/Run Command/Automation audit identifikuje caller a role chain;
- forbidden test dokáže, že principal s `SendCommand` nevie meniť target tags ani pass-nuť arbitrary role;
- old runbook version 11 a unsafe 100% rate control sú vyradené.

Skorší control: pred high-impact fleet mutation sa selector resolve-ne do immutable manifestu, policy overí environment/count/AZ, approval sa viaže na hash manifestu a documentu a runtime gate vyžaduje bounded concurrency, stop threshold a application postcondition.

## 24. Troubleshooting managed node offline

Postup:

```text
exact account/Region/node identity
→ machine power/OS state
→ SSM Agent process a local logs
→ instance profile/DHMC/hybrid identity
→ time/DNS/TLS
→ route/NAT/endpoints
→ SG/NACL/endpoint policy
→ registration a heartbeat
→ capability-specific dependencies
```

Wrong Region a cloned identity sa často javia ako „agent beží, ale node nevidím“. Endpoint test z iného hosta nedokazuje node path ani identity.

## 25. Troubleshooting Run Command a Automation

### `Pending`, `Delayed` alebo `DeliveryTimedOut`

Over node online timeline, agent channel, target resolution, quota a delivery timeout. Script ešte nemusel začať.

### `Failed` alebo `ExecutionTimedOut`

Použi exact plugin step, stdout/stderr, exit code, OS user, working directory, parameters, timeout a local resources. Wrapper script môže prehltnúť native exit code.

### Partial fleet success

Porovnaj target manifest s OS/AMI/agent/network/AZ cohorts. Neopakuj command na celý fleet; replay iba unresolved targets s idempotency a current-state checkom.

### Automation step `Success`, outcome wrong

Pokračuj do controller/resource state, runtime, health a business postcondition. Over runbook version, assume role a output-to-next-step binding.

## 26. Troubleshooting Session Manager

Rozlíš:

```text
caller IAM deny
→ session document/resource policy
→ node offline/channel
→ client/plugin
→ local OS user/profile
→ KMS/log destination
→ target application/port
```

`StartSession` API success a nefunkčný shell môže znamenať local profile alebo OS-user failure. Port-forward session môže úspešne vzniknúť, ale destination port/path zostane nedostupný.

## 27. Troubleshooting patching

Rozlišuj:

- patch nie je applicable;
- nie je approved v baseline/policy;
- repository alebo proxy je nedostupný;
- snapshot/package metadata drift;
- disk je plný;
- package dependency conflict;
- reboot je pending;
- agent sa po reboot-e nevrátil;
- application health zlyhala;
- compliance snapshot je stale;
- wrong target set bol patched.

Najprv zachovaj per-node patch snapshot a execution output. Blind rescan alebo retry môže zmeniť evidence a package repository state.

## 28. Security a cost boundaries

Najcitlivejšie permissions:

- `ssm:SendCommand`;
- `ssm:StartSession`;
- document create/update/default-version changes;
- Automation execute/stop;
- `iam:PassRole`;
- Parameter Store reads;
- target-tag mutation;
- Quick Setup/organization rollout;
- output/log destination access.

Cost drivers:

```text
advanced/on-prem managed-node tier podľa modelu
+ Automation steps/executions
+ Parameter Store tier/API usage
+ CloudWatch Logs/S3 output
+ NAT/interface endpoints
+ patch/download transfer
+ operational labor a replacement capacity
```

Lacný broad command môže mať extrémny outage cost. Rate control, target proof a validation sú ekonomické controls, nie iba procesná réžia.

## 29. Kontrolné otázky

1. Čo tvorí exact fleet-operation subject?
2. Kedy je machine skutočne eligible managed node?
3. Čo mení Default Host Management Configuration?
4. Prečo `SendCommand` success nie je script ani application success?
5. Ako sa tag selector stáva privilege a blast-radius boundary?
6. Čo musí obsahovať resolved target manifest?
7. Prečo patch compliance potrebuje timestamp a baseline generation?
8. Kedy je vhodnejšie immutable replacement než in-place rollback?
9. Ako sa líši Session Manager API audit od session-content loggingu?
10. Aký dôkaz uzatvára Automation ako úspešnú production operáciu?

## Glossary impact

Relevantné pojmy: fleet-operation subject, managed-node eligibility, document generation, resolved target manifest, targeting authority boundary, execution-delivery verdict, rate-controlled fleet mutation, patch compliance freshness, Automation side-effect boundary a operational acceptance verdict.

## Oficiálna dokumentácia

- [AWS Systems Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/what-is-systems-manager.html)
- [Setting up managed nodes](https://docs.aws.amazon.com/systems-manager/latest/userguide/managed-instances.html)
- [Default Host Management Configuration](https://docs.aws.amazon.com/systems-manager/latest/userguide/managed-instances-default-host-management.html)
- [Systems Manager Quick Setup](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-quick-setup.html)
- [Run Command](https://docs.aws.amazon.com/systems-manager/latest/userguide/run-command.html)
- [Run Command status](https://docs.aws.amazon.com/systems-manager/latest/userguide/monitor-commands.html)
- [Run commands at scale](https://docs.aws.amazon.com/systems-manager/latest/userguide/run-command-rate-control.html)
- [Session Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html)
- [State Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-state.html)
- [Patch Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/patch-manager.html)
- [Patch policies](https://docs.aws.amazon.com/systems-manager/latest/userguide/patch-manager-policies.html)
- [Systems Manager Automation](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-automation.html)
- [Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: CloudWatch a CloudTrail](cloudwatch-cloudtrail.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: KMS a Secrets Manager →](kms-secrets-manager.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
