# Terraform vs. Ansible

Terraform a Ansible sa prekrývajú v tom, že oba menia infraštruktúru a configuration, ale ich dominantné state a identity modely sú odlišné:

- Terraform je resource lifecycle engine s persistentnými bindings, dependency graphom a plan/apply transitionom.
- Ansible je target-oriented automation engine, ktorý pri run-e skladá inventory, values a ordered per-host operations.

Správna otázka preto nie je „ktorý nástroj je lepší“, ale:

```text
aký objekt alebo attribute má lifecycle?
→ akú stabilnú identitu potrebuje?
→ kto je authoritative writer?
→ ako vzniká proposed change a evidence?
→ aký narrow contract prechádza medzi tools?
→ ako sa overí combined runtime outcome?
→ ako sa obnoví partial alebo conflicting state?
```

Dominantný hybridný lifecycle:

```text
capability intent a object/attribute inventory
→ assign authoritative ownership
→ Terraform resource change subject
→ plan, policy, apply a state/runtime verification
→ publish narrow readiness/inventory contract
→ Ansible run subject a host convergence
→ combined service verification
→ drift, upgrade a recovery closure
```

## 1. Atlas scenár

Atlas Payments release 3.13.0 potrebuje:

### Terraform-owned state

- VPC, subnets a routes;
- dvanásť VM instances;
- instance profiles a IAM bindings;
- security groups;
- load balancer a target group;
- DNS record;
- image ID `ami-atlas-313`;
- Terraform state lineage `L17`, serial `228`.

### Ansible-owned state

- package `atlas-payments-3.13.0`;
- application user a directories;
- configuration artifact `C44`;
- runtime secret epoch `SE02`;
- systemd service state;
- process-level verification;
- bounded host registration workflow podľa published contractu.

Cross-tool contract `HC313` obsahuje iba:

```text
stable instance ID
inventory hostname
management address
environment
region/AZ
service role
image ID
readiness generation
load-balancer target identity
```

Ansible nečíta celý Terraform state. Terraform nespravuje application config file.

Úspešný combined outcome:

```text
Terraform resources existujú pod správnymi identities
+ state bindings a runtime inventory sú konzistentné
+ HC313 obsahuje všetkých 12 ready hosts
+ Ansible dosiahne package/config/service state na všetkých 12 hosts
+ application transaction prejde cez production DNS a load balancer
+ fresh Terraform plan je no-op
+ second Ansible converge nemá unintended changes
```

## 2. Dva odlišné state stroje

### Terraform resource lifecycle

```text
configuration
+ provider target identity
+ prior state bindings
+ refreshed remote observations
→ dependency graph
→ saved plan
→ create/update/replace/destroy/read
→ successor state snapshot
→ runtime verification
```

Terraform stabilizuje resource identity cez address, provider context a remote object binding.

### Ansible host convergence lifecycle

```text
playbook a execution environment
+ resolved inventory
+ effective variables/facts
→ ordered per-host tasks
→ module/API observations a mutations
→ changed/failure/handler transitions
→ loaded-runtime a fleet verification
```

Ansible nemá univerzálny persistentný binding pre každý file, package, service a API object. Current state typicky zisťuje konkrétny module pri run-e.

Dôsledok:

- Terraform je silný tam, kde create/update/delete/replacement a dlhodobá object identity tvoria hlavný lifecycle.
- Ansible je silný tam, kde hlavný lifecycle tvorí host alebo device configuration a ordered orchestration.

## 3. Ownership sa prideľuje objektom a atribútom

Boundary „Terraform infra, Ansible config“ je užitočný začiatok, ale nestačí. Ownership musí byť presný na úroveň mutable objectu alebo attribute.

Príklad:

| Objekt alebo attribute | Authoritative writer | Consumer |
|---|---|---|
| VM lifecycle a image ID | Terraform | Ansible target |
| Security-group ingress | Terraform | Ansible read-only |
| Host package version | Ansible | runtime verifier |
| Application config file | Ansible | service process |
| Load-balancer object | Terraform | Ansible orchestration consumer |
| Temporary target registration state | jeden explicitný owner podľa workflowu | druhý tool read/coordinate |
| DNS record | Terraform | application/verifier |

Jeden attribute nemá mať dvoch nezávislých authoritative writers.

Ownership contract obsahuje:

```text
object/attribute identity
writer tool a team
read-only consumers
desired-state source
mutation permissions
drift detector
recovery owner
migration/transfer path
```

## 4. Tool selection podľa lifecycle-u

Použi Terraform, keď hlavný problém je:

```text
stable resource identity
+ dependency graph
+ persistent binding/state
+ plan create/update/replace/destroy
+ import/refactor/drift lifecycle
```

Použi Ansible, keď hlavný problém je:

```text
resolved target fleet
+ host/device current-state reads
+ ordered operations a conditions
+ batches/handlers/retries
+ loaded-runtime convergence
```

Použi oba, keď capabilities prirodzene prechádzajú dvoma boundaries a contract je explicitný.

Nástroj nevyberaj podľa popularity alebo jednej syntax feature. Cloud resource možno vytvoriť Ansible modulom a config file možno zapísať Terraform provisionerom; otázka je, či tým vznikne zrozumiteľný dlhodobý identity, drift, retry a recovery model.

## 5. Provisioning-to-configuration contract

Terraform output nemá byť neobmedzený access k celému state-u.

Nevhodný model:

```text
Ansible dostane read access k production state backendu
→ číta interné resource addresses a citlivé attributes
→ Terraform refactor zmení internú štruktúru
→ inventory alebo host mapping sa rozbije
```

Vhodnejší model:

```text
Terraform verified resource inventory
→ publish versioned narrow host contract HC313
→ inventory validation
→ Ansible target manifest
```

Contract potrebuje:

- schema version;
- immutable producer subject;
- stable host/resource identity;
- environment a readiness state;
- required fields a null semantics;
- consumer compatibility;
- publication generation;
- access policy;
- retirement/deprecation path.

## 6. Readiness je samostatný transition

Terraform apply success môže znamenať, že VM a network resources vznikli. Neznamená automaticky:

- boot dokončený;
- cloud-init úspešný;
- management identity pripravená;
- SSH host identity stabilná;
- route/firewall path funkčný;
- package manager dostupný;
- host registrovaný v authoritative inventory.

Hybrid pipeline potrebuje explicitný readiness gate:

```text
Terraform apply success
→ instance identity exists
→ bootstrap completion observed
→ management channel verified
→ host contract published as ready
→ Ansible may target host
```

Sleep nie je readiness model. Použi condition-based observation s bounded timeoutom a failure evidence.

## 7. Bootstrap boundary

Minimálny bootstrap môže vytvoriť:

- management identity/channel;
- trusted CA alebo host certificate;
- základný runtime potrebný pre Ansible;
- inventory/CMDB registration;
- minimum security baseline pred prvým connectionom.

Dlhodobý application configuration lifecycle neukladaj do jednorazového user-data scriptu. User data má slabý re-run, partial failure a observation model.

Terraform provisioner má podobný problém:

```text
resource create
→ remote-exec side effect
→ side effect nie je samostatný managed resource binding
→ retry/recovery sa viaže na resource lifecycle
```

Provisioner je výnimočný bridge alebo bootstrap, nie defaultná náhrada configuration-management systému.

## 8. Plan a check mode nie sú ekvivalenty

Terraform saved plan identifikuje konkrétny resource transition subject:

```text
configuration + dependencies + inputs + state serial + refresh + target
→ proposed actions
```

Ansible check mode je module-specific predikcia:

```text
resolved play/task path
→ module best-effort current-state model
→ predicted changed/skipped/result
```

Niektoré Ansible modules check mode nepodporujú alebo nevedia predikovať external side effects. Terraform plan zas nemusí poznať post-apply application behavior.

Hybrid approval preto potrebuje dve odlišné assurances:

- Terraform plan/policy pre resource lifecycle;
- Ansible syntax, contract, representative check/diff a canary evidence pre host convergence.

## 9. Combined pipeline

Atlas používa:

```text
1. build/test immutable machine image ami-atlas-313
2. Terraform init/validate/test
3. Terraform saved plan + policy + approval
4. apply exact plan
5. verify state serial, remote resources a readiness
6. publish HC313
7. validate inventory schema, identity, count a readiness generation
8. Ansible syntax/lint/contract checks
9. canary converge
10. canary loaded-runtime verification
11. fleet rollout
12. full service transaction
13. fresh Terraform no-op plan
14. second Ansible converge
15. publish combined release evidence
```

Každý krok má vlastnú identity, permissions, artifacts, retry semantics a recovery ownera.

## 10. Failure boundaries

### Terraform failure

Môže zanechať:

- partial remote mutations;
- unknown API outcome;
- successor state commit failure;
- resource created but not ready;
- valid infrastructure s nefunkčným application pathom.

### Contract/publication failure

Môže zanechať:

- host existuje, ale inventory ho neobsahuje;
- stale destroyed host zostáva targetom;
- wrong environment alebo address;
- schema mismatch;
- readiness generation, ktorá nezodpovedá resource subjectu.

### Ansible failure

Môže zanechať:

- časť hosts zmenenú;
- file update bez handleru;
- package/config mismatch;
- partial external side effect;
- green run nad incomplete target setom.

Recovery musí najprv určiť, v ktorej boundary sa aktuálny effective state nachádza.

## 11. Worked failure: dva tools menia rovnaký security-group attribute

Terraform deklaruje production ingress iba z load balancera. Ansible incident runbook pridáva do rovnakej security group temporary admin CIDR cez cloud module.

```text
Ansible pridá rule
→ Terraform drift plan ju vidí ako unmanaged difference
→ scheduled apply rule odstráni
→ incident runbook ju znovu pridá
→ tools vytvoria oscillation
```

Problém nie je „Terraform je príliš deklaratívny“. Problém je chýbajúci ownership a break-glass adoption/expiry contract.

Možnosti:

- Terraform zostáva owner a incident zmena ide cez versionovaný emergency input;
- samostatný explicitne shared attribute model s expiry a reconciliation;
- ownership transfer na iný controller.

Tichý druhý writer nie je prijateľný.

## 12. Worked failure: inventory sa publikoval pred readiness

Terraform apply vytvoril dvanásť VMs a okamžite publikoval IP addresses. Ansible začal, kým cloud-init ešte menil SSH configuration a host keys.

```text
resource exists
→ contract označí host ready bez readiness evidence
→ Ansible vidí unreachable/host-key mismatch
→ pipeline interpretuje failure ako config problém
→ operator navrhne VM replacement
```

Infrastructure existence, bootstrap completion a configuration readiness sú tri odlišné states. Recovery nemá automaticky nahrádzať resource; najprv over boot, identity, network a management channel.

## 13. Worked failure: consumer čítal interný Terraform state

Ansible dynamic inventory používal internú addressu:

```text
module.compute.aws_instance.app[0]
```

Terraform refactor prešiel na `for_each` a `moved` blocks. Remote instances zostali zachované, ale consumer parser addressu prestal fungovať.

```text
Terraform ownership migration je správna
→ interný state layout sa zmení
→ undocumented consumer coupling sa rozbije
→ inventory je prázdny
→ Ansible skončí green no-op
```

Narrow versioned contract má používať stable instance IDs a explicitnú schema, nie interné state addresses.

## 14. Worked failure: golden image a runtime Ansible majú dvoch owners package-u

Ansible image build publikuje image s package 3.13.0. Runtime role používa `state: latest` a pri boot-e ho aktualizuje na 3.13.1.

```text
Terraform deploys immutable image subject 3.13.0
→ runtime Ansible mutates base package
→ fleet už nezodpovedá image identity
→ replacement a in-place configuration model sa rozchádzajú
```

Ownership musí určiť, či package patrí image artifactu alebo runtime configuration. Security update workflow môže buildnúť nový image alebo vykonať explicitný bounded runtime patch, ale nie oba implicitne.

## 15. Causal troubleshooting walkthrough: Terraform je green, Ansible nevie nakonfigurovať štyri hosts

Terraform apply a state verification prešli. HC313 obsahuje dvanásť hosts. Ansible nakonfiguroval osem a štyri sú unreachable.

### 1. Zafixuj cross-tool subject

Zaznamenaj:

- Terraform source, plan digest, state lineage/serial a target identity;
- remote instance IDs, image IDs a bootstrap status;
- HC313 schema, generation a producer digest;
- Ansible inventory resolution subject a target manifest;
- management addresses, host identity evidence a credentials;
- per-host connection results a cloud-init/boot timeline.

### 2. Súťažiace hypotézy

1. Terraform vytvoril resources, ale bootstrap ešte nebol complete.
2. HC313 označil host ready príliš skoro.
3. Contract obsahuje nesprávnu management address alebo environment.
4. Dynamic inventory cache používa stale generation.
5. Security group, route alebo NACL blokuje management path.
6. SSH host key/certificate sa po publication zmenil.
7. Ansible credential alebo become policy neplatí pre nový image.
8. Štyri VMs bootli z iného image ID.
9. Ansible target identity koliduje so starými destroyed hosts.
10. Infrastructure je healthy a chyba je iba v controller network boundary.

### 3. Diskriminačné observation points

- Terraform remote IDs a live instance lifecycle state;
- cloud-init/bootstrap completion marker a logs;
- exact HC313 generation a field values;
- `ansible-inventory --host` a cache age;
- route/firewall flow evidence z controllera k hostu;
- host certificate/key identity;
- image ID a management-user contract;
- connection failure type: DNS, timeout, auth, host-key, Python/runtime;
- destroyed/current instance-ID comparison.

### 4. Containment

Pozastav ďalší Ansible batch a nepublikuj incomplete hosts do service trafficu. Nevynucuj Terraform replacement, kým nie je potvrdená infrastructure lifecycle chyba.

### 5. Recovery

- bootstrap incomplete → počkaj condition-based alebo oprav bootstrap a publish new readiness generation;
- wrong contract field → publish corrected HC314 a invalidate inventory cache;
- network path → oprav Terraform-owned route/security resource cez fresh plan;
- host identity → obnov trusted identity path, nie `StrictHostKeyChecking=no`;
- image mismatch → replace alebo repair podľa image ownership policy;
- Ansible runtime contract → oprav user/interpreter/credential mapping a canary verify;
- stale destroyed identity → odstráň ju z contractu a audituj collision.

### 6. Over pôvodný outcome

Potvrď všetkých dvanásť stable instance IDs, readiness generation, management connection, Ansible loaded config C44, service health a end-to-end transaction. Následný Terraform plan má byť no-op a druhý Ansible run bez unintended changes.

### 7. Posuň control skôr

Pridaj explicitný readiness state machine, contract schema test, cache-generation gate, stable host-identity validation a combined release verifier.

## 16. Drift a continuous reconciliation

Terraform drift sa typicky objaví v fresh plan-e voči configuration, state a remote observations.

Ansible drift sa objaví pri module current-state read-e, scheduled validation alebo external compliance kontrole.

Combined monitoring má korelovať:

```text
Terraform resource inventory
↔ published host contract
↔ Ansible expected/resolved/verified fleet
↔ application runtime inventory
```

Príklady divergence:

- Terraform state má 12 instances, contract 11;
- contract má 12, Ansible verified 10;
- Ansible verified 12 files, runtime inventory 11 processes;
- Terraform image ID 3.13.0, runtime package 3.13.1.

## 17. Secrets a identity boundaries

Terraform a Ansible majú odlišné secret exposure paths.

Terraform secret môže skončiť v variables, saved plan-e, state-e, provider logs alebo outputs. Ansible secret môže skončiť vo variables/Vault, module arguments, rendered files, callbacks alebo registered results.

Cross-tool pipeline nemá používať jednu širokú admin identity.

Oddeľ:

- Terraform plan read identity;
- Terraform apply writer identity;
- contract publisher identity;
- inventory reader identity;
- Ansible host configuration identity;
- runtime verifier identity.

Narrow contract nemá prenášať secrets, ak consumer potrebuje iba host identity a readiness.

## 18. Versioning a upgrades

Versionuj a testuj samostatne:

- Terraform modules a providers;
- state/backend schema assumptions;
- cross-tool contract schema;
- machine image;
- Ansible roles/collections;
- execution environment;
- inventory plugin;
- combined release workflow.

Upgrade môže meniť boundary bez priameho diffu v druhom repository, napríklad:

- Terraform output type alebo hostname normalization;
- Ansible inventory plugin parsing;
- image bootstrap user;
- provider-computed address;
- role expectation voči image package layoutu.

Consumer compatibility a migration path patria do contract release-u.

## 19. Referenčné pravidlá

- Terraform a Ansible majú rozdielne identity, state a execution modely.
- Ownership sa prideľuje objektu alebo attribute, nie iba celému „infra“ alebo „config“ svetu.
- Jeden mutable attribute má mať jedného authoritative writera.
- Terraform state nie je všeobecné consumer API.
- Cross-tool integration používa narrow versioned contract.
- Resource existence, bootstrap completion a configuration readiness sú odlišné states.
- Terraform saved plan a Ansible check mode nie sú ekvivalentné assurances.
- Provisioner a user data sú bootstrap bridges, nie defaultný dlhodobý config lifecycle.
- Terraform backend lock nechráni Ansible writer a opačne.
- Combined success potrebuje resource, contract, fleet a application-runtime verification.
- Recovery začína identifikáciou failure boundary, nie automatickým replacementom alebo retry.
- Golden image a runtime configuration potrebujú explicitný attribute ownership.

## 20. Kontrolné otázky

1. Ako sa líši Terraform resource binding od Ansible current-state detection?
2. Prečo sa ownership prideľuje na úroveň objectu alebo attribute?
3. Čo má obsahovať narrow Terraform-to-Ansible contract?
4. Prečo apply success neznamená host readiness?
5. Prečo Terraform plan nie je ekvivalent Ansible check mode?
6. Kedy je provisioner iba prijateľný bootstrap bridge?
7. Ako vzniká oscillation pri dvoch authoritative writers?
8. Prečo Ansible nemá čítať interné Terraform state addresses?
9. Ako golden-image model mení ownership package configuration?
10. Aké evidence lokalizujú failure medzi resource, contract, inventory a host runtime boundary?

## Glossary impact

Relevantné pojmy: cross-tool ownership subject, authoritative attribute writer, provisioning-to-configuration contract, host contract generation, readiness boundary, combined release subject, Terraform resource lifecycle, Ansible host convergence, cross-tool drift correlation, bootstrap boundary, golden-image ownership a combined recovery boundary.

## Oficiálna dokumentácia

- [What is Terraform](https://developer.hashicorp.com/terraform/intro)
- [Terraform core workflow](https://developer.hashicorp.com/terraform/intro/core-workflow)
- [Integrate Terraform with Ansible Automation Platform](https://developer.hashicorp.com/validated-patterns/terraform/terraform-integrate-ansible-automation-platform)
- [Ansible playbooks](https://docs.ansible.com/projects/ansible/latest/playbook_guide/index.html)
- [Ansible concepts](https://docs.ansible.com/projects/ansible/latest/getting_started/basic_concepts.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Ansible idempotencia](ansible-idempotency.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Containers vs. virtual machines →](../08-container-fundamentals-and-docker/containers-vs-virtual-machines.md)
<!-- KNOWLEDGE-NAVIGATION:END -->