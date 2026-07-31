# Lifecycle, import a moved blocks

Terraform lifecycle controls, import a `moved` blocks riešia tri odlišné transition classes:

```text
remote object lifecycle transition
ownership adoption existujúceho objectu
configuration address transition pri rovnakom objecte
```

Všetky pracujú s resource identity, ale menia inú vrstvu. `create_before_destroy` mení poradie remote replacementu. Import vytvára nový state binding k existujúcemu remote ID. `moved` mení address binding pri rovnakom remote objekte. Ich zámennosť môže z čisto konfiguračného refaktoru vytvoriť produkčný destroy/create alebo prevziať cudzí objekt do nesprávneho state-u.

Kapitola uzatvára incident `IAC-PAY-76`. Atlas presúva produkčnú VPC a load balancer do reusable module-u a súčasne adoptuje manuálne vytvorený log bucket. Module release chýba complete moved chain, operátor importuje bucket cez default provider do test accountu a `create_before_destroy` sa použije ako univerzálny „bezpečný“ fix pre plánované replacements. Výsledkom sú nové remote objekty namiesto zachovania existujúcich bindings.

## 1. Dominantný identity-transition lifecycle

```text
current configuration address
+ current state binding
+ provider target a remote ID
+ current owner
→ klasifikácia transition class
→ lifecycle/import/move contract
→ plan a destructive-risk review
→ remote mutation alebo binding-only mutation
→ successor state snapshot
→ remote/runtime verification
→ rollback alebo migration closure
```

Prvá otázka nie je „ktorý príkaz použiť“, ale:

```text
Má sa zmeniť remote object, ownership binding alebo iba configuration address?
```

## 2. Tri transition classes

### Remote lifecycle change

```text
same management address
→ provider update alebo replacement
→ remote object môže dostať nové ID
```

### Ownership adoption

```text
existujúci remote object bez current bindingu
→ import
→ nová Terraform address/remote-ID väzba
```

### Address refactor

```text
existujúci binding na old address
→ moved mapping
→ rovnaký remote ID na new address
```

Import ani `moved` samy osebe negarantujú no-op remote outcome. Následný plan môže odhaliť configuration mismatch, provider normalization alebo lifecycle rule, ktorá stále navrhne update/replacement.

## 3. Replacement je identity a availability event

Plan môže pre resource ukázať:

```text
no-op
update in-place
create
destroy
replace destroy→create
replace create→destroy
```

Replacement môže zmeniť:

- remote ID;
- IP, DNS alebo endpoint;
- attached policies;
- data alebo encryption identity;
- sessions a traffic;
- downstream references;
- rollback možnosti.

Praktické čítanie plan JSON:

```bash
terraform show -json tfplan > tfplan.json
jq -r '
  .resource_changes[]
  | select(.change.actions | index("delete"))
  | [.address, (.change.actions|join(",")), (.change.replace_paths // [])]
  | @json
' tfplan.json
```

Výstup preukazuje addresses a actions, ktoré plan artifact obsahuje. Nepreukazuje, že plan je fresh voči current state alebo že provider remote operation bude úspešná. Replacement reason sa musí spojiť s exact provider/module/state subjectom.

## 4. `create_before_destroy` mení poradie, nie risk model

```hcl
resource "aws_launch_template" "api" {
  name_prefix = "atlas-payments-api-"
  image_id    = var.ami_id

  lifecycle {
    create_before_destroy = true
  }
}
```

Default replacement môže byť:

```text
destroy old
→ create new
```

S `create_before_destroy`:

```text
create new
→ downstream cutover
→ destroy old
```

Rule negarantuje zero downtime. Musia byť splnené preconditions:

```text
objekty môžu koexistovať
+ naming umožňuje druhú identity
+ quota má dočasnú kapacitu
+ data alebo endpoint sa dá migrovať
+ downstream cutover je explicitný
+ old object sa môže bezpečne retire-nuť
```

## 5. Worked failure: unique name znemožnil create-first

Atlas menil object, ktorého provider vyžadoval replacement, ale remote API povoľovalo iba jedno globálne unique meno.

```text
create_before_destroy
→ create new so starým menom
→ API odmietne duplicate name
→ old object ostane
→ apply partial/failed
```

Rule nezhoršila data stav, ale nevytvorila bezpečný rollout. Správny design potrebuje nový generated name, data copy alebo dual-running strategy, consumer cutover a následný retirement.

## 6. `prevent_destroy` ako lokálny plan guard

```hcl
resource "aws_db_instance" "payments" {
  # ...

  lifecycle {
    prevent_destroy = true
  }
}
```

`prevent_destroy` blokuje plánovanú destroy/replacement action, kým rule existuje v configuration a resource je prítomný. Nechráni pred:

- manuálnym cloud deletion;
- compromised provider identity;
- odstránením resource blocku spolu s rule;
- data loss počas in-place update;
- wrong backend alebo state corruption;
- provider-side failure.

Je to posledný local guard, nie kompletná data protection. Kritické resources potrebujú provider deletion protection, backups, restore testy a high-risk approval.

Ak guard blokuje change, najprv vysvetli prečo plan obsahuje destroy. Odstránenie rule bez analýzy iba vypne alarm.

## 7. `ignore_changes` ako explicitný ownership handoff

```hcl
resource "aws_ecs_service" "api" {
  desired_count = 6

  lifecycle {
    ignore_changes = [desired_count]
  }
}
```

Legitímny contract:

```text
Terraform vlastní service object
→ autoscaler vlastní desired_count
→ ignore_changes deleguje update reconciliation
→ runtime monitoring a bounds overujú autoscaler
```

Bez ownera, monitoringu a recovery rule iba skryje drift. Každý ignored attribute má mať:

- authoritative writera;
- dôvod delegácie;
- acceptable bounds;
- monitoring;
- review alebo expiry;
- incidentný recovery path.

`ignore_changes = all` prakticky odoberá Terraformu update ownership a vyžaduje veľmi silný dôvod.

## 8. `replace_triggered_by` ako identity edge

```hcl
resource "terraform_data" "image_revision" {
  input = var.image_digest
}

resource "example_immutable_runtime" "api" {
  image = var.image_digest

  lifecycle {
    replace_triggered_by = [terraform_data.image_revision]
  }
}
```

Trigger je vhodný, keď upstream change skutočne invaliduje object identity. Mutable timestamp alebo noisy data source by vytvárali replacement pri každom plan-e.

Review musí vysvetliť:

```text
ktorý subject sa zmenil
→ prečo existing object nie je kompatibilný
→ prečo in-place update nestačí
→ ako sa overí cutover a old-object retirement
```

## 9. Preconditions a postconditions

```hcl
resource "aws_db_instance" "payments" {
  # ...

  lifecycle {
    precondition {
      condition     = var.backup_retention_days >= 14
      error_message = "Production database requires at least 14 days retention."
    }

    postcondition {
      condition     = self.storage_encrypted
      error_message = "Provider returned an unencrypted database."
    }
  }
}
```

Precondition overuje known assumption pred operation. Postcondition overuje attribute dostupný po provider evaluation/read. Nepreukazuje application connectivity, restore capability ani business transaction. Tie vyžadujú runtime oracle.

## 10. Import je ownership adoption

Configuration-driven import:

```hcl
import {
  to = aws_s3_bucket.logs
  id = "company-prod-logs"
}

resource "aws_s3_bucket" "logs" {
  bucket = "company-prod-logs"
}
```

Import vytvorí binding:

```text
Terraform address
+ provider configuration
+ remote ID
→ state ownership record
```

Nevytvorí automaticky úplnú configuration a nepotvrdí, že Terraform má prevziať všetky attributes. Post-import plan je authority reconciliation medzi manual reality a novým desired state-om.

## 11. Import subject

Pred adoption zaznamenaj:

```yaml
importSubject:
  destinationAddress: aws_s3_bucket.logs
  providerConfiguration: aws.production
  targetAccount: "771100001234"
  region: eu-central-1
  remoteId: company-prod-logs
  currentOwner: platform-operations
  newOwner: payments-iac
  otherWriters:
    - bucket-lifecycle-controller
  stateLineage: 37fd...
  stateSerial: 231
```

Názov resource-u alebo úspešný import command nepreukazuje target identity. Rovnaké meno môže existovať v inom account context-e alebo provider query môže mať odlišnú semantics.

## 12. CLI import verzus import block

```bash
terraform import aws_s3_bucket.logs company-prod-logs
```

CLI import vykoná okamžitú state mutation. Je vhodný pre recovery alebo legacy workflow, ale vyžaduje freeze writers, backup, exact backend/provider subject a fresh plan.

Import block:

- je versionovaný;
- prejde reviewom;
- môže byť súčasťou plan/policy evidence;
- koordinuje viac imports;
- zachová intent history.

Pre plánovanú adoption je configuration-driven import preferovaný.

## 13. Worked failure: import do nesprávneho accountu

Atlas chcel importovať `company-prod-logs`. Operátor použil default provider, ktorý smeroval do test accountu, kde existoval bucket s rovnakým názvom.

```text
CLI import success
→ state binding = test object
→ production desired policies apply na test bucket
→ skutočný prod bucket zostáva unmanaged
```

Recovery:

1. freeze writers;
2. backup state;
3. overiť remote IDs, account a audit timeline;
4. odstrániť chybný binding bez mazania remote test objectu;
5. použiť explicitný production provider mapping;
6. importovať správny object;
7. fresh plan a remote/runtime verification.

## 14. Post-import plan je povinný decision point

Po importe môže plan ukázať:

```text
no-op
provider normalization
in-place update
replacement
odstránenie nested rules
security/encryption mismatch
external-writer conflict
```

Prvý post-import plan sa neapplyuje automaticky. Tím rozhodne:

```text
adoptovať remote value do configuration
revertovať remote object k approved desired state
rozdeliť attribute ownership
zrušiť nesprávny import
```

## 15. `moved` block zachováva binding pri refaktore

```hcl
moved {
  from = aws_vpc.main
  to   = module.network.aws_vpc.main
}
```

Semantics:

```text
old address binding
→ same remote ID
→ new address binding
```

Bez mappingu Terraform vidí old address removed a new address added. Výsledkom môže byť destroy/create aj pri identickom resource configuration.

## 16. Premenovanie `for_each` keya

```hcl
moved {
  from = aws_subnet.private["az_a"]
  to   = module.network.aws_subnet.private["primary_a"]
}
```

Move musí presne pokryť module path aj instance key. Migration z `count` indexov na `for_each` keys často potrebuje mapping pre každú instance.

```hcl
moved {
  from = aws_subnet.private[0]
  to   = module.network.aws_subnet.private["az_a"]
}

moved {
  from = aws_subnet.private[1]
  to   = module.network.aws_subnet.private["az_b"]
}
```

## 17. `moved` verzus `terraform state mv`

### `moved` block

- versionovaný a reviewovateľný;
- opakovateľný naprieč environments;
- vhodný pre reusable module releases;
- podporuje neskorých consumers;
- je súčasťou plan evidence.

### `terraform state mv`

- okamžitá mutation jedného state subjectu;
- vyžaduje lock a backup;
- nie je automaticky reprodukovaná inde;
- vhodná pre recovery alebo jednorazovú legacy migration.

Plánovaný refactor patrí do code. Manuálna surgery v každom environment-e vytvára divergentnú migration history.

## 18. Retained moved chain

Consumer môže preskočiť releases:

```text
module 2.8.0 → 3.5.1
```

Ak latest module zachováva iba move z `3.4.0`, staršie addresses sa nepreložia. Support policy musí definovať minimum supported source version a retained moved chain.

Upgrade fixture matrix:

```text
2.8.x → 3.5.1
3.0.x → 3.5.1
3.4.x → 3.5.1
```

Každý fixture plan musí rozlíšiť moves od replacements.

## 19. Worked incident `IAC-PAY-76`: refactor bez complete moved chainu

Atlas presunul:

```text
aws_lb.api
→ module.service.module.edge.aws_lb.api
```

Release obsahovala iba move do `module.service.aws_lb.api`, nie druhý nested step.

```text
partial moved chain
→ old address sa preloží iba čiastočne
→ final address vyzerá ako nový object
→ plan replacement load balancera
→ endpoint a external attachments sú ohrozené
```

`create_before_destroy` by vytvoril nový load balancer, ale business intent bol zachovať remote ID. Správna oprava je complete address chain a consumer inventory, nie rollout strategy.

## 20. Recovery a reverse change

Po binding mutation nemusí Git revert stačiť. Ak state už používa new address a source sa vráti na old address, plan opäť uvidí identity mismatch.

Recovery package obsahuje:

```text
old/new source revisions
old/new state snapshots
address mapping manifest
remote-ID inventory
provider target
plan artifacts
runtime verification
reverse moved/forward-fix decision
```

Často je bezpečnejší forward fix s explicitným mappingom než slepý source revert.

## 21. Competing hypotheses pri mass replacement plane

Symptom: refactor do `module.network` plánuje 32 replacements.

```text
H1: moved blocks chýbajú
H2: module paths sú nesprávne
H3: for_each keys sa zmenili
H4: resource type/provider schema bráni move
H5: provider upgrade vyžaduje skutočný replacement
H6: state fixture má odlišné addresses
H7: duplicate binding vznikol po manuálnej surgery
H8: replace_triggered_by nezávisle vyžaduje replacement
```

Dôkazy:

```bash
terraform state list | sort > state-addresses.txt
terraform show -json tfplan > tfplan.json
jq -r '.resource_changes[] | [.address, (.change.actions|join(","))] | @tsv' tfplan.json
```

Address manifest testuje H1–H3/H6/H7, type/provider metadata H4/H5 a lifecycle-expanded plan H8.

## 22. Acceptance a forbidden paths

Transition blok je prijatý, keď:

```text
každá change je klasifikovaná ako remote lifecycle, adoption alebo address move
+ replacement reasons sú explicitné
+ lifecycle rules majú owner a preconditions
+ import používa správny provider/account/remote ID
+ post-import plan je reviewed
+ moved chain pokrýva supported old versions
+ remote IDs sa pri pure refactore nezmenia
+ wrong-account import fixture je odmietnutý
+ missing-move fixture je destructive-plan gateom odmietnutý
+ second plan je no-op
```

## 23. Anti-patterny

### „`create_before_destroy` je univerzálny zero-downtime switch“

Mení poradie replacementu; nerieši unique names, data, quotas ani cutover.

### „`prevent_destroy` je backup“

Je to plan guard, nie provider-side ani data recovery protection.

### „`ignore_changes` odstráni noise“

Bez explicitného external ownera skryje ownership konflikt.

### „Import úspešne prešiel, objekt je správny“

Import success nepreukazuje account, region, ownership ani configuration compatibility.

### „Rename resource labelu je kozmetika“

State identity je address-based. Bez move môže vzniknúť destroy/create.

## 24. Kontrolné otázky

1. Aké tri transition classes riešia lifecycle, import a moved blocks?
2. Prečo replacement nie je iba syntax `-/+`?
3. Kedy je `create_before_destroy` reálne vykonateľný?
4. Čo `prevent_destroy` chráni a čo nechráni?
5. Kedy je `ignore_changes` legitímny ownership contract?
6. Čo precondition a postcondition preukazujú?
7. Prečo import nevytvorí automaticky správnu configuration?
8. Aký rozdiel je medzi import blockom a CLI importom?
9. Čo `moved` block mení a čo nemení?
10. Prečo je `moved` vhodnejší než opakovaný `state mv`?
11. Ako sa testuje retained moved history?
12. Prečo Git revert po state transition nemusí stačiť?

## Glossary impact

Relevantné pojmy: Terraform lifecycle, replacement, `create_before_destroy`, `prevent_destroy`, `ignore_changes`, `replace_triggered_by`, precondition, postcondition, import, adoption, `moved` block, address transition, `state mv`, retained moved chain, migration fixture a destructive-plan gate.

## Primárne zdroje

- [Terraform lifecycle meta-argument](https://developer.hashicorp.com/terraform/language/meta-arguments/lifecycle)
- [Terraform import](https://developer.hashicorp.com/terraform/language/import)
- [Import block reference](https://developer.hashicorp.com/terraform/language/block/import)
- [Refactor Terraform resources](https://developer.hashicorp.com/terraform/language/modules/develop/refactoring)
- [Move Terraform state](https://developer.hashicorp.com/terraform/cli/state/move)

<!-- KNOWLEDGE-NAVIGATION:START -->
[← Predchádzajúca: Modules](modules.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Drift →](drift.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
