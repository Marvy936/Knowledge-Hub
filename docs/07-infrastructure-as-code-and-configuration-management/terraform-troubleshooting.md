# Terraform troubleshooting

Terraform troubleshooting nie je hľadanie príkazu, ktorý „odomkne apply“. Je to rekonštrukcia presného change subjectu a prechodu medzi configuration, provider schema, input values, dependency graphom, backend/state bindingom, remote API mutations a state commitom. Najnebezpečnejší incident je ten, pri ktorom provider mutation uspela, no process stratil response alebo state write zlyhal. Vtedy Terraform state ani exit code samostatne nehovoria, čo v remote systéme skutočne existuje.

Preserve-first model:

```text
symptom a intended target
→ tool/provider/module/configuration identity
→ backend, workspace, lineage a serial
→ effective variables a credentials
→ plan subject a graph
→ apply events a provider requests
→ remote read-back
→ state binding comparison
→ containment a recovery
→ druhý no-op plan a business verification
```

## Exact subject pred prvým zásahom

Pri incidente zaznamenaj:

```text
repository a commit/tree
Terraform CLI version
provider source, version a checksums
module source a immutable revision
backend type, key/path, workspace
state lineage a serial
cloud account/subscription/project a region
effective variable-set fingerprint
saved plan checksum
CI job/run identity
UTC timeline a request IDs
```

```bash
terraform version
terraform providers
terraform workspace show
terraform show -json plan.tfplan | jq '.terraform_version,.format_version'
```

`terraform version` a `providers` opisujú local/resolved toolchain. Nepotvrdzujú backend ani cloud target. Target identity sa read-backuje samostatne, napríklad cez STS alebo provider-specific API.

## 1. `init` zlyháva alebo inicializuje nesprávny backend

`terraform init` rieši backend, modules a providers. Failure classes treba oddeliť:

```text
backend authentication alebo network/TLS
backend config alebo nesprávny key
state migration prompt/partial migration
module source resolution
provider registry/mirror/checksum
platform binary availability
lockfile mismatch
```

Useful read-backs:

```bash
terraform init -reconfigure
grep -n '' .terraform.lock.hcl
terraform providers lock -platform=linux_amd64 -platform=linux_arm64
```

`-reconfigure` zabudne local backend initialization metadata a znovu použije aktuálnu configuration. Nie je bezpečným univerzálnym riešením, ak nevieš, ktorý state subject má byť authoritative. `-migrate-state` je data transition a potrebuje source/destination backup, lineage/serial comparison a explicitné approval.

Ak pipeline pozerá do prázdneho state-u, plan môže legitímne navrhnúť vytvorenie celej produkcie. Pred applyom over resource inventory a backend identity:

```bash
terraform state pull > /tmp/state.json
jq '{lineage,serial,resources:(.resources|length)}' /tmp/state.json
terraform state list | head -50
```

Prázdny list nie je dôkaz, že remote infraštruktúra neexistuje. Môže znamenať nesprávny backend alebo chýbajúce bindings.

## 2. Provider alebo module sa resolve-ol inak

Provider source address, version constraints a lockfile spolu určujú selected package. Module version alebo Git ref má rovnaký supply-chain význam. Mutable branch/tag môže zmeniť graph bez zmeny root code-u.

```bash
terraform providers
terraform get -update=false
sha256sum .terraform.lock.hcl
find .terraform/modules -maxdepth 2 -type f -name modules.json -print -exec cat {} \;
```

Pri checksum error nevymazávaj automaticky lockfile. Najprv rozlíš zmenu platformy, mirror corruption, upstream package replacement, proxy alebo legitímny dependency update. Regenerovanie locku bez review mení approved input graph.

## 3. Configuration validation prejde, plan zlyhá

`terraform validate` kontroluje syntax a internú configuration consistency dostupnú bez reálneho remote planu. Neoveruje všetky credentials, quotas, organization policy, live data sources ani target-specific constraints.

```bash
terraform fmt -check -recursive
terraform validate
TF_LOG=INFO terraform plan -out=plan.tfplan
```

Pri plan failure rozlíš:

```text
expression/type/validation
provider configuration
credential/authorization
remote data-source query
state refresh
API throttling/network
unknown value v nepovolenom kontexte
cycle alebo invalid graph
```

`TF_LOG` môže obsahovať citlivé values a headers. Zapínaj ho v kontrolovanom scope-e, presmeruj do chráneného file-u a po incidente ho spravuj ako secret-bearing artifact.

## 4. Plan ukazuje prekvapivý create, destroy alebo replacement

Najprv nepoužívaj `-target` ani apply. Ulož saved plan a analyzuj machine-readable actions:

```bash
terraform plan -out=plan.tfplan
terraform show -json plan.tfplan > plan.json
jq -r '
  .resource_changes[] |
  [.address, (.change.actions|join(","))] | @tsv
' plan.json
```

Competing hypotheses:

```text
nesprávny backend/workspace/region/account
resource address refactor bez `moved`
`for_each` key alebo list index sa zmenil
ForceNew provider attribute
tainted/deposed object
import/binding chýba
provider default/tag zmenil diff
refresh zistil drift
module/provider upgrade zmenil schema
```

Detail:

```bash
jq '.resource_changes[] | select(.address=="module.vpc.aws_subnet.private[\"az-a\"]") | .change' plan.json
terraform state show 'module.vpc.aws_subnet.private["az-a"]'
```

Sensitive fields môžu byť redacted. Plan JSON je predikcia nad konkrétnym state serialom a remote observations. Ak sa target zmení, saved plan môže byť stale a apply ho musí odmietnuť alebo znovu prejsť eligibility gateom.

## 5. Lock timeout alebo stale lock

Lock chráni jeden backend state subject pred podporovanými writers. Nechráni iný backend key, direct cloud API writer ani nástroj, ktorý locking nepoužíva.

Pri lock incidente zaznamenaj lock ID, owner, operation, timestamp, backend key a aktívne CI jobs. Najprv zisti, či writer stále beží. `terraform force-unlock` odstráni koordináciu; neukončí vzdialený apply a nevráti mutations.

```bash
terraform force-unlock LOCK_ID
```

Použi ho až keď je preukázané, že owner process skončil, neexistuje ďalší apply a remote/state evidence je zachované. Po unlocku sprav refresh-only plan a remote read-back pred novou mutation.

## 6. Apply zlyhal uprostred

Non-zero apply môže znamenať:

```text
nič sa nezmenilo
časť resources sa zmenila a state sa zapísal
remote mutation uspela, read-after-write zlyhal
remote mutation uspela, state commit zlyhal
provider request timeout vytvoril unknown outcome
postcondition alebo provisioner zlyhal po create
```

Ulož output a current state bez ďalšieho apply:

```bash
terraform state pull > state-after.json
terraform show -json > state-view.json
terraform plan -refresh-only -out=refresh.tfplan
terraform show -json refresh.tfplan > refresh.json
```

Potom použi provider-native read-back s request/resource identity. Pri AWS napríklad:

```bash
aws sts get-caller-identity
aws ec2 describe-vpcs --filters Name=tag:Name,Values=atlas-prod
```

Ak remote object existuje, ale state binding chýba, ďalší apply môže vytvoriť duplicate alebo zlyhať na name conflict. Recovery môže používať configuration-driven import block alebo kontrolovaný `terraform import`; najprv však over exact remote identity a ownership.

## 7. State obsahuje nesprávny binding

State command mení Terraform bookkeeping a môže byť rovnako rizikový ako remote mutation.

```bash
terraform state list
terraform state show ADDRESS
terraform state mv OLD NEW
terraform state rm ADDRESS
terraform import ADDRESS REMOTE_ID
```

`state mv` mení address binding bez zmeny remote objectu. `state rm` prestane object spravovať; nemaže ho. `import` vytvorí binding k existujúcemu remote objectu. Každá operácia potrebuje state backup, configuration match a následný plan.

Preferuj versionované `moved` a `import` blocks, keď je transition súčasťou opakovateľného repository contractu. Ad-hoc state surgery je incident tool, nie bežný refactor workflow.

## 8. Drift a refresh

Drift je rozdiel medzi configuration intentom, state-recorded observation a remote reality. Nie každý drift je unauthorized: autoscaler, provider default, emergency change alebo delegated controller môže byť legitimate writer.

```bash
terraform plan -refresh-only
terraform plan -detailed-exitcode
```

Pri `-detailed-exitcode` znamená 0 no diff, 2 diff a 1 error. CI musí tieto classes zachovať. Automatický apply každého driftu môže odstrániť incident containment alebo prebiť delegated ownera.

Klasifikácia:

```text
Git-owned drift → reconcile alebo reviewed source update
legitimate delegated drift → ignore/ownership contract
emergency drift → adopt, revert alebo časovo obmedzená exception
unknown drift → preserve evidence a investigate
```

## 9. `-target` a ďalšie skratky

`-target` mení graph scope a môže obísť súvisiace outputs, policies a dependencies. Je vhodný iba ako výnimočný recovery nástroj s následným full planom. Rovnaké upozornenie platí pre `-refresh=false`, manual state edit a široké `ignore_changes`.

Skratka môže odstrániť symptom, ale vytvoriť hidden debt. Closure vždy obsahuje full graph plan, remote verification a second no-op plan.

## 10. Provider crash alebo inconsistent result

Provider je samostatný process/plugin. Crash log, protocol error alebo `inconsistent result after apply` môže znamenať provider defect, API eventual consistency, normalization diff alebo nesprávnu schema semantics.

Zachovaj:

```text
Terraform/provider versions a checksums
minimal redacted configuration
plan/state before a after
provider request IDs
remote API result
debug log s controlled secret handling
```

Neopakuj apply slepo. Najprv zisti remote outcome. Upgrade/downgrade provideru je dependency change a vyžaduje nový plan nad rovnakým targetom.

## Connected incident: apply vytvoril VPC, state write zlyhal

Pipeline používala správny cloud account, no backend credential expiroval po provider create. AWS VPC `vpc-0abc` vznikla, state serial sa nezvýšil a job skončil non-zero. Retry nad prázdnym bindingom plánoval druhú VPC.

Recovery:

```text
zastaviť ďalšie applies a zamknúť environment
→ uložiť plan, logs, backend state a AWS request IDs
→ AWS read-backom potvrdiť vpc-0abc a jeho tags/CIDR
→ porovnať configuration identity
→ obnoviť backend write capability
→ importnúť exact VPC do expected addressu
→ planovať dependent resources
→ aplikovať saved/reviewed recovery plan
→ full refresh a no-op plan
→ overiť routing a forbidden public path
```

Root cause sa neopraví iba importom. Credential lifetime a apply duration, backend auth refresh a unknown-outcome runbook musia byť súčasťou platform controlu.

## Acceptance po recovery

Terraform incident je uzatvorený až keď:

```text
backend/workspace/lineage/serial sú správne
cloud identity a region zodpovedajú intentu
configuration/provider/module/variables sú pinned
state bindings zodpovedajú remote objectom
full plan nemá nečakané destructive actions
apply alebo binding recovery je auditovateľná
remote capability funguje
forbidden path zostáva zakázaná
druhý full plan je no-op alebo vysvetlený delegated drift
```

Najlepší Terraform troubleshooting nástroj nie je `force-unlock` ani `state rm`. Je to presná korelácia configuration, state a remote reality, ktorá umožní zvoliť mutation, binding repair alebo source correction bez vytvorenia ďalšieho writera.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Praktický Terraform projekt od prázdneho adresára po overený remote state](terraform-practical-walkthrough.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Ansible architecture →](ansible-architecture.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
