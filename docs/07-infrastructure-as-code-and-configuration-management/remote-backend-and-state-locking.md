# Remote backend a state locking

Terraform backend určuje, kde sa uchováva persistentný state a podľa typu backendu aj ako sa koordinuje locking alebo remote execution. Produkčný team workflow potrebuje centralizovaný, chránený a obnoviteľný state model.

## 1. Čo je backend

Backend je Terraform Core komponent zodpovedný za state storage a súvisiace behavior.

Typicky rieši:

- umiestnenie state snapshotu,
- čítanie a zápis state,
- locking, ak ho backend podporuje,
- workspaces alebo state namespaces podľa backendu,
- prípadne remote operations pri špecializovaných backendoch/platformách.

Backend nie je provider. Provider spravuje infraštruktúrne objekty cez API; backend spravuje Terraform operational state.

## 2. Local backend

Default backend je `local`:

```text
configuration directory
└── terraform.tfstate
```

Local backend je jednoduchý, ale pri team workflowe má obmedzenia:

- state je viazaný na konkrétny filesystem,
- collaboration vyžaduje ručný prenos,
- bezpečný multi-writer model chýba,
- backup a access control závisia od hosta,
- CI runners môžu state stratiť po zániku workspace.

## 3. Remote backend

Remote backend ukladá state mimo lokálneho working directory, napríklad do:

- object storage,
- managed Terraform platformy,
- HTTP-compatible state service,
- cloud-native storage backendu,
- enterprise state service.

Výhody:

- central source state,
- team access,
- locking podľa capability,
- versioning a backups,
- audit,
- oddelenie state od ephemeral runnera.

Remote neznamená automaticky bezpečný. Security závisí od storage configuration, credentials, locking a recovery policy.

## 4. Backend block

Príklad všeobecného backend configuration:

```hcl
terraform {
  backend "example" {
    # backend-specific arguments
  }
}
```

Configuration môže mať iba jeden backend block.

Backend block sa vyhodnocuje skôr než bežné variables, locals, resources a data sources. Preto nemôže referencovať:

```hcl
var.bucket_name
local.state_key
data.example.current.id
```

Backend identity musí byť známa počas `terraform init`.

## 5. Partial backend configuration

Citlivé alebo environment-specific backend arguments možno dodať mimo source podľa podporovaného init workflowu:

```bash
terraform init -backend-config=backend-prod.hcl
```

Alebo cez environment/identity mechanismus backendu.

Do repository neukladaj backend credentials. Backend config môže byť zachytený v lokálnych metadata, plan files alebo logs; používaj short-lived identity a bezpečný runner.

## 6. `terraform init`

`terraform init`:

- inicializuje backend,
- overí alebo nakonfiguruje state access,
- nainštaluje providers,
- načíta modules,
- aktualizuje local working-directory metadata.

Pri zmene backend configuration je potrebné reinitialize.

Relevantné režimy podľa situácie zahŕňajú:

```bash
terraform init -reconfigure
terraform init -migrate-state
```

`-reconfigure` zabudne predchádzajúcu local backend initialization a použije novú configuration bez implicitného predpokladu migrácie.

`-migrate-state` pomáha presunúť existujúci state do nového backendu.

Pred migráciou vytvor backup a zastav všetky writers.

## 7. Backend migration

Bezpečný postup:

```text
freeze applies
→ identify source state
→ backup source snapshot
→ configure destination backend
→ verify destination access/security
→ terraform init -migrate-state
→ verify lineage/resources/outputs
→ run refresh/plan
→ enable pipelines
```

Riziká:

- migrácia nesprávneho workspace,
- prepísanie existujúceho destination state,
- rozdielne credentials,
- strata locking,
- incomplete copy,
- staré pipelines stále zapisujú do source backendu.

## 8. State locking

Ak backend podporuje locking, Terraform automaticky získa lock pri operáciách, ktoré môžu zapisovať state.

Model:

```text
writer A acquires lock
→ reads current state
→ plans/applies
→ writes new snapshot
→ releases lock
```

Writer B počas locku nemá pokračovať s konfliktujúcou state mutation.

Locking chráni state pred concurrent writers. Nechráni automaticky remote cloud objekty spravované inými states alebo tools.

## 9. Nie každý backend podporuje locking

Locking capability je backend-specific.

Pri výbere backendu over:

- podporu locking,
- consistency model,
- lock timeout/retry behavior,
- failure recovery,
- auditability,
- behavior pri network partition.

Remote storage bez locking môže centralizovať súbor, ale stále umožniť race condition medzi applies.

## 10. Lock acquisition failure

Ak Terraform nevie získať lock, write operácia nemá pokračovať.

Možné príčiny:

- aktívny apply,
- zaseknutý predchádzajúci run,
- network/API outage,
- permissions,
- lock record corruption,
- backend throttling.

Najprv identifikuj lock ownera, run ID, čas a environment. Nevypínaj locking ako rutinnú opravu.

## 11. Lock timeout

CLI operácie môžu podľa príkazu podporovať čakanie na lock:

```bash
terraform apply -lock-timeout=5m
```

Timeout má zodpovedať očakávanej queue/concurrency policy.

Dlhé náhodné čakanie bez pipeline serialization môže iba skryť zlý orchestration model.

## 12. `-lock=false`

Niektoré príkazy umožňujú vypnúť locking:

```bash
terraform apply -lock=false
```

Pri write operáciách je to nebezpečné. Môže vzniknúť:

```text
writer A reads serial 10
writer B reads serial 10
writer A writes serial 11
writer B writes conflicting serial 11/12
```

Výsledkom môže byť lost update, poškodený mapping alebo remote/state divergence.

Použitie bez locku má byť výnimočné a iba po preukázaní exclusive accessu.

## 13. Force unlock

```bash
terraform force-unlock <LOCK_ID>
```

Force unlock odstráni lock, ale neukončí pôvodný Terraform proces.

Pred použitím potvrď:

1. pôvodný run už nebeží,
2. žiadny writer nepracuje so state,
3. lock patrí správnemu backendu/workspace,
4. máš lock ID a audit evidence,
5. po unlocku spustíš čerstvý plan.

Ak pôvodný writer stále beží, force unlock umožní concurrent mutation.

## 14. Pipeline concurrency

Backend lock je posledná ochranná vrstva. CI/CD má navyše serializovať applies pre rovnaký state/environment.

Použi:

- environment deployment locks,
- resource groups/concurrency groups,
- remote run queue,
- one-active-apply policy,
- cancellation policy pre stale plans.

Plan jobs môžu podľa backend/provider behavioru tiež získavať lock alebo konkurovať refresh operáciám. Navrhni explicitný model.

## 15. State storage security

Remote backend musí chrániť:

- confidentiality,
- integrity,
- availability.

Controls:

- encryption in transit,
- encryption at rest,
- narrowly scoped identity,
- audit logs,
- private network path podľa rizika,
- bucket/container policy,
- object versioning,
- delete protection,
- retention,
- incident alerts.

State access je často ekvivalentný privileged infrastructure read accessu a niekedy obsahuje secrets.

## 16. Identity model

Oddel identities pre:

- developer read/plan,
- CI plan,
- CI apply,
- backend administration,
- break-glass recovery.

Apply identity nemá automaticky potrebovať oprávnenie meniť backend retention alebo mazať všetky snapshots.

Backend admin nemá automaticky potrebovať cloud provider admin permissions.

## 17. Short-lived credentials

Preferuj federovanú workload identity:

```text
CI job identity token
→ cloud/backend role exchange
→ short-lived scoped credential
→ state access
```

Výhody:

- bez dlhodobého access key v CI variables,
- audience a subject restrictions,
- kratší exposure window,
- lepší audit.

## 18. Encryption a key management

Encryption at rest môže používať provider-managed alebo customer-managed keys.

Pri customer-managed key over:

- kto smie decryptovať,
- key rotation,
- key deletion protection,
- cross-account access,
- disaster recovery,
- audit events.

State backup zašifrovaný kľúčom, ktorý bol zmazaný, nie je obnoviteľný.

## 19. Versioning a retention

Object/version history umožňuje návrat k staršiemu snapshotu pri:

- accidental overwrite,
- corruption,
- chybná state surgery,
- compromised pipeline,
- backend migration issue.

Retention musí vyvážiť:

- recovery window,
- storage costs,
- secret history,
- compliance deletion requirements.

Staré state versions môžu obsahovať už rotované secrets a stále musia byť chránené.

## 20. Backup vs. backend versioning

Versioning v rovnakom storage účte znižuje riziko accidental overwrite, ale nemusí chrániť pred:

- account compromise,
- policy misconfiguration,
- region-wide incidentom,
- destructive adminom,
- key loss.

Podľa kritickosti pridaj oddelený backup/recovery model s kontrolovaným prístupom.

## 21. State separation

Príklady state keys/boundaries:

```text
network/prod
platform/prod
application-a/prod
network/stage
```

Oddelenie podľa prefixu v jednom storage neznamená automaticky oddelené permissions. Backend IAM policy musí obmedziť konkrétne paths/workspaces.

## 22. Environment isolation

Produkčný state má mať:

- samostatnú identity boundary,
- jasný backend/workspace identifier,
- chránený apply workflow,
- prísnejšiu retention,
- audit,
- recovery ownera.

Názov environmentu z variable nie je dostatočná bezpečnostná izolácia.

## 23. Backend configuration a secrets

Backend block nemá obsahovať hardcoded secrets:

```hcl
terraform {
  backend "example" {
    access_key = "..." # zlé
  }
}
```

Použi native credential chain alebo external init configuration.

Niektoré backend arguments sa môžu uložiť do `.terraform` metadata a saved plans. Zaobchádzaj s nimi ako s citlivými údajmi.

## 24. Remote state access

`terraform_remote_state` data source umožňuje čítať root outputs iného state.

Riziká:

- consumer potrebuje backend credentials,
- access k outputs môže prakticky vyžadovať access k celému snapshotu,
- producer/consumer sú časovo coupled,
- output zmena je breaking contract,
- citlivé outputs sa môžu preniesť ďalej.

Pre silné security boundaries publikuj explicitné hodnoty do service discovery, parameter store alebo configuration registry.

## 25. Remote backend vs. remote execution

Remote state storage a remote Terraform execution sú odlišné capabilities.

Remote storage:

```text
CLI/pipeline executes locally
→ state stored remotely
```

Remote execution:

```text
configuration uploaded/connected
→ managed worker executes plan/apply
→ platform controls queue, state, variables and policy
```

Nevyvodzuj remote execution behavior iba z toho, že state je v remote backend-e.

## 26. Saved plans

Saved plan je viazaný na:

- configuration,
- provider/module selections,
- variables,
- prior state,
- refreshed observations.

Plan artifact môže obsahovať sensitive data. Chráň ho access controlom a krátkou retention.

Ak sa state zmení po vytvorení planu, plan môže byť stale a musí sa regenerovať.

## 27. Backend outage

Pri backend outage:

- nezačínaj apply s lokálnou kópiou bez riadeného recovery plánu,
- zastav automatické deploymenty,
- zachovaj error logs a request IDs,
- over storage a locking service zvlášť,
- neprepínaj narýchlo na nový backend bez migrácie lineage,
- po obnove over latest serial a lock records.

Remote infraštruktúra môže ďalej fungovať; problém je v change-control plane.

## 28. Network partition

Najrizikovejší scenár je nejasné, či write uspel:

```text
apply sends state write
→ connection interrupted
→ client nevie výsledok
```

Postup:

1. nepridávaj druhého writera,
2. over backend snapshot a serial,
3. over lock,
4. porovnaj remote objects,
5. spusti čerstvý refresh/plan,
6. pokračuj až po potvrdení authoritative state.

## 29. Backend migration rollback

Ak migrácia zlyhá:

- zachovaj source aj destination snapshoty,
- neumožni writes do oboch backendov,
- vyber authoritative backend,
- over lineage/serial/resources,
- prekonfiguruj všetky pipelines,
- zneplatni staré credentials až po potvrdení.

Dual-writer obdobie medzi backendmi je kritický incident risk.

## 30. Anti-patterny

### Remote state bez locking

Central storage nerieši concurrent writers.

### Force unlock ako bežná operácia

Pipeline concurrency alebo run cleanup sú chybné.

### Jeden backend admin key vo všetkých projects

Kompromitácia jedného jobu ohrozí všetky states.

### State bucket bez versioning/backupu

Accidental overwrite nemá recovery path.

### Secrets v backend config commite

Credential zostane v history.

### Development a production oddelené iba workspace názvom

Security boundary je príliš slabá.

### `terraform_remote_state` ako univerzálny service catalog

Vzniká široký access a tesný cross-state coupling.

## 31. Troubleshooting

### `Error acquiring the state lock`

Over active run, lock metadata, backend permissions a service availability. Force unlock až po potvrdení, že writer neexistuje.

### Terraform používa nesprávny state

Over backend type/config, workspace, init metadata, state key a pipeline environment.

### `init` chce migrovať state

Skontroluj source/destination, vytvor backup a potvrď, či ide o očakávanú backend zmenu alebo iba local metadata mismatch.

### State write zlyhal po apply

Zastav ďalšie runs. Zachovaj lokálny recovery snapshot, over remote serial a postupuj podľa backend recovery inštrukcií.

### CI nemá prístup, developer áno

Porovnaj identity, backend path permissions, network route, KMS decrypt permission a workspace mapping.

### Lock zostal po ukončení jobu

Over, či job naozaj skončil a či nebeží remote child process. Až potom použite lock ID na riadený force unlock.

## 32. Kontrolné otázky

1. Aký je rozdiel medzi backendom a providerom?
2. Prečo backend block nemôže používať variables?
3. Aký je rozdiel medzi `-reconfigure` a state migration workflowom?
4. Čo state locking chráni a čo nechráni?
5. Prečo je `-lock=false` rizikové?
6. Aké podmienky musia platiť pred force unlockom?
7. Ako CI/CD dopĺňa backend locking?
8. Aké security controls potrebuje state storage?
9. Aký je rozdiel medzi remote state a remote execution?
10. Ako riešiť nejasný state write po network partition?

## Glossary impact

Relevantné pojmy: Terraform backend, local backend, remote backend, backend configuration, backend migration, partial backend configuration, state locking, lock timeout, force unlock, remote state, remote execution, state versioning, backend lineage a multi-writer race.

## Oficiálna dokumentácia

- [Backend configuration](https://developer.hashicorp.com/terraform/language/backend)
- [Backends: state storage and locking](https://developer.hashicorp.com/terraform/language/state/backends)
- [State locking](https://developer.hashicorp.com/terraform/language/state/locking)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Terraform state](terraform-state.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
