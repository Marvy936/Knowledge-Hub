# Terraform state

Terraform state je persistentný identity, binding a observation model. Spája konkrétne Terraform resource instances s remote objektmi, uchováva známe attributes a umožňuje Core-u rozhodnúť, či má objekt vytvoriť, aktualizovať, nahradiť alebo odstrániť. State nie je desired configuration a nie je iba performance cache. Bez správneho state subjectu môže Terraform považovať existujúci produkčný objekt za chýbajúci alebo spravovať nesprávnu remote identitu.

Kapitola uzatvára incident `IAC-PAY-75`. Atlas pipeline načíta prázdny alternate backend, vytvorí druhú VPC a pri zápise nového snapshotu stratí spojenie. Remote create uspel, no state binding sa nezapísal. Nasledujúci run opäť navrhuje create. Správna recovery preto nezačína retryom ani ručnou editáciou JSON-u, ale identifikáciou backendu, lineage, serialu, resource address-y, provider targetu a remote object ID.

## 1. Dominantný address-to-outcome lifecycle

Nasledujúci model opisuje prechody jedného Terraform configuration, state a remote-resource subject, nie iba poradie krokov. Failure môže nastať v ktoromkoľvek bode reťazca resolved inputs a graph cez provider API mutation až po state binding a zanechať partial alebo unknown outcome. Každý transition preto potrebuje vlastný read-back a closure tvorí exact provider target, remote/state reconciliation a druhý no-op plan.

```text
configuration resource instance address
→ prior state binding a provider association
→ refresh remote objectu
→ desired/known/actual comparison
→ saved plan nad lineage/serial subjectom
→ provider remote mutation
→ new binding a attributes
→ backend state commit
→ runtime a ownership verification
→ backup, recovery alebo ďalší reconciled plan
```

State odpovedá na identity otázku:

```text
Ktorý remote objekt patrí tejto Terraform resource instance?
```

Neodpovedá automaticky na otázky:

```text
Je objekt zdravý?
Má správny traffic?
Je configuration business-correct?
Je Terraform jediný writer?
Neexistuje unmanaged duplicate?
```

Tieto otázky potrebujú provider-native a runtime observation points.

## 2. Resource instance address, provider a remote ID

Atlas VPC má configuration/state address:

```text
module.network.aws_vpc.main
```

Provider configuration:

```text
provider["registry.terraform.io/hashicorp/aws"].production
```

Remote identity:

```text
account 771100001234
region eu-central-1
vpc-0a42
```

State binding je:

```text
module.network.aws_vpc.main
+ provider aws.production
→ account 771100001234 / eu-central-1 / vpc-0a42
```

Názov tagu `atlas-prod-eu` nie je binding. Dva objekty môžu mať rovnaký tag. Terraform potrebuje provider-specific remote ID a správny provider target.

## 3. Desired, known a actual state

Desired state je HCL, resolved variables a selected module/provider behavior. Known state je snapshot resource addresses, provider associations, remote IDs a posledných známych attributes. Actual state sú objekty a hodnoty, ktoré provider API práve pozoruje v konkrétnom account-e a regione.

```text
configuration C71
+ state lineage L-prod / serial 208
+ provider reads v account-e 7711
→ saved plan P209
```

Create action môže znamenať, že objekt naozaj neexistuje, ale aj chýbajúci binding, wrong backend/workspace, zmenený key/address, iného ownera, wrong target/permission alebo predchádzajúci remote success bez state commitu. Jeden symbol `+` tieto mechanizmy nerozlišuje.

Diagnostika preto spája state address a provider association s remote inventory a audit trailom. Plan je verdict nad konkrétnym desired/known/observed subjectom, nie globálne tvrdenie o cloude.

Pri diagnostike vždy oddeľ:

```text
desired state
= HCL + resolved variables + module/provider selections

known state
= address bindings + posledné známe attributes v snapshot-e

actual state
= remote objects a values pozorované cez provider API
```

Plan vzniká približne z:

```text
configuration C71
+ state lineage L-prod / serial 208
+ provider reads v account-e 7711
→ saved plan P209
```

Objekt skutočne neexistuje, state binding chýba, načítal sa nesprávny backend/workspace, address/key sa zmenila, objekt vytvoril iný owner a provider read objekt nevidí pre account/region/permission mismatch.

Dopĺňa ho predchádzajúci remote create uspel, ale state write zlyhal.

Jeden plan symbol `+` nerozlišuje tieto mechanizmy.

## 4. State snapshot, lineage a serial

State sa vyvíja cez snapshots. Dve dôležité identity sú:

- **lineage** — identifikátor nezávislej state histórie;
- **serial** — monotónne rastúce číslo snapshotu v jednej lineage.

```text
lineage 37fd / serial 208
→ úspešný apply alebo state mutation
→ lineage 37fd / serial 209
```

Praktická inspection:

```bash
terraform state pull > state.json
jq '{lineage, serial, terraform_version}' state.json
sha256sum state.json
```

Výstup preukazuje obsah snapshotu, ktorý backend vydal aktuálnemu callerovi. Digest preukazuje integritu tejto lokálnej copy. Nepreukazuje, že snapshot je správny environment, že neexistuje novší snapshot v inom backend keyi alebo že remote objekty zodpovedajú známym attributes.

State JSON format je implementation detail. Preferuj CLI a backend versioning pred vlastným parserom alebo ručnou editáciou.

## 5. Refresh mení observation model, nie desired intent

Refresh použije state remote ID a effective provider target na Read operáciu a aktualizuje Terraform knowledge o remote attributes. Môže odhaliť manual firewall change, deletion, server-side normalization, attribute spravovaný iným controllerom, eventual-consistency stav alebo wrong-account `not found`.

Refresh tým nevytvára nový business intent. Až následný decision určí, či sa remote rozdiel revertuje, adoptuje configuration change-om, deleguje ownershipom alebo rieši ako binding recovery. `refresh-only apply` zapisuje nový known snapshot, ale desired HCL nemení.

Preto sa pred refresh-only commitom zachová predecessor lineage/serial a overí writer/intent. Inak môže operátor legitimizovať attacker alebo incidentný override iba tým, že ho zapíše do state knowledge.

Provider Read aktualizuje known attributes:

```text
state remote ID
→ provider Read(account, region, ID)
→ observed attributes
→ refreshed state model
```

Transition eviduje manuálne zmenený firewall rule, objekt odstránený mimo Terraformu, cloudom normalizovanú hodnotu, attribute spravovaný iným controllerom, eventual-consistency stav a wrong-account alebo permission-induced „not found“.

Refresh nevytvára nový desired intent. Plan až následne rozhoduje, či sa rozdiel vráti, prijme configuration change-om, deleguje ownershipom, importuje alebo rieši recovery.

## 6. State a saved plan freshness

Saved plan je viazaný na:

```text
configuration revision
+ effective variables
+ provider/module versions
+ backend/workspace
+ lineage a prior serial
+ refreshed observations
+ target identity
```

Ak iný run zapíše serial `209`, plan vytvorený nad `208` už nemusí byť fresh. Apply schváleného planu nesmie ticho prepočítať nový plan s inými actions.

Workflow:

```bash
terraform plan -out=tfplan
sha256sum tfplan
terraform show -json tfplan > tfplan.json
terraform apply tfplan
```

Preukazuje, že apply dostal rovnaký plan artifact. Backend a Terraform stále musia chrániť pred stale state transition podľa svojich semantics.

## 7. Remote mutation a state commit nie sú jedna transakcia

Operation path:

```text
read snapshot S208
→ provider Create/Update/Delete
→ remote API dokončí alebo pokračuje async
→ provider vráti ID/attributes
→ Terraform pripraví S209
→ backend zapíše S209
```

Failure môže vzniknúť medzi ľubovoľnými krokmi. Dôležité outcome classes:

```text
NO_MUTATION
KNOWN_PARTIAL
REMOTE_OUTCOME_UNKNOWN
REMOTE_COMPLETE_STATE_WRITE_FAILED
STATE_COMMITTED_RUNTIME_FAILED
COMPLETE_SUCCESS
```

Pipeline status `failed` neznamená `NO_MUTATION`. Provider timeout alebo backend connection reset môže nastať po úspešnom remote side effectu.

## 8. Worked incident: create uspel, binding sa nezapísal

Atlas pridával produkčný NAT gateway. Provider request vytvoril `nat-0913`, ale backend write zlyhal:

```text
configuration deklaruje NAT
→ provider Create request accepted
→ nat-0913 vznikne
→ runner stratí spojenie s backendom
→ serial 209 sa nezapíše
→ job failed
→ state 208 NAT nepozná
```

Slepý retry:

```text
state stále bez NAT bindingu
→ fresh plan navrhne ďalší create
→ vznikne duplicate cost a route ambiguity
```

Správna reakcia je freeze writers a remote reconciliation.

## 9. Evidence-preserving containment

Pri rozdiele medzi state a remote objektmi sa zastavia writers skôr, než ďalší refresh alebo apply prepíše volatile evidence. Zachová sa state snapshot, backend version ID, plan, provider request IDs a remote audit; až potom sa rozhoduje medzi restore, importom, moved transitionom alebo compensation.

Recovery workflow zastav všetky pipelines nad daným backend subjectom, zachovaj saved plan, plan JSON, provider logs, request IDs a lokálny recovery snapshot, read-only načítaj latest backend state, over lineage a serial, read-only queryuj remote platformu v správnom account/region context-e a identifikuj actual objects a ich creation identities.

Dopĺňa ho rozhodni, či treba import, restore, compensation alebo cleanup a až potom vytvor nový plan.

Containment nesmie začať destroyom objektu, kým nie je známe, či na ňom už závisí produkčný traffic alebo data.

## 10. State inspection commands

Táto podsekcia vysvetľuje konkrétnu časť Terraform configuration, state a remote-resource subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inputs a graph cez provider API mutation až po state binding; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po exact provider target, remote/state reconciliation a druhý no-op plan.

```bash
terraform state list
terraform state show 'module.network.aws_subnet.private["az_a"]'
terraform output -json
terraform show
```

`state list` preukazuje addresses v aktuálnom state subjecte, `state show` preukazuje known binding a attributes jednej instance, `output -json` preukazuje root outputs v snapshot-e a `show` zobrazuje state alebo plan podľa argumentu.

Žiadny z týchto výstupov sám nepreukazuje live runtime health.

Remote read-back:

```bash
aws ec2 describe-vpcs \
  --vpc-ids vpc-0a42 \
  --query 'Vpcs[0].{VpcId:VpcId,Cidr:CidrBlock,State:State,Tags:Tags}'
```

Preukazuje remote object visible danému callerovi v danom region context-e. Nepreukazuje Terraform ownership; na to treba binding a source contract.

## 11. State mutation commands menia management model

Nasledujúci model opisuje prechody jedného Terraform configuration, state a remote-resource subject, nie iba poradie krokov. Failure môže nastať v ktoromkoľvek bode reťazca resolved inputs a graph cez provider API mutation až po state binding a zanechať partial alebo unknown outcome. Každý transition preto potrebuje vlastný read-back a closure tvorí exact provider target, remote/state reconciliation a druhý no-op plan.

```bash
terraform state mv
terraform state rm
terraform state replace-provider
terraform state pull
terraform state push
```

Tieto príkazy nemusia meniť remote objekt. Práve preto sú nebezpečné: môžu zmeniť to, čo Terraform verí o ownership identity, bez runtime mutation.

### `state mv`

Táto podsekcia vysvetľuje konkrétnu časť Terraform configuration, state a remote-resource subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inputs a graph cez provider API mutation až po state binding; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po exact provider target, remote/state reconciliation a druhý no-op plan.

```bash
terraform state mv \
  'aws_subnet.private[0]' \
  'aws_subnet.private["az_a"]'
```

Presúva binding medzi addresses. Pre versionovaný refactor preferuj `moved` block, aby migration contract platil pre všetkých consumers.

### `state rm`

Táto podsekcia vysvetľuje konkrétnu časť Terraform configuration, state a remote-resource subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inputs a graph cez provider API mutation až po state binding; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po exact provider target, remote/state reconciliation a druhý no-op plan.

```bash
terraform state rm aws_s3_bucket.legacy
```

Odstráni binding, remote object zostane. Ak configuration block zostane, ďalší plan môže navrhnúť duplicate create. Legitímne použitie vyžaduje explicitný ownership transfer.

### `state push`

Manuálne prepíše backend state. Je to recovery nástroj poslednej možnosti. Vyžaduje backup, exclusive writer control, lineage/serial verifikáciu, peer review a následný refresh/plan.

## 12. State surgery protocol

Táto podsekcia vysvetľuje konkrétnu časť Terraform configuration, state a remote-resource subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inputs a graph cez provider API mutation až po state binding; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po exact provider target, remote/state reconciliation a druhý no-op plan.

```text
freeze writers
→ potvrď backend/workspace/lineage/serial
→ vytvor chránený backup
→ inventory addresses a remote IDs
→ over source a intended ownership
→ vykonaj najmenšiu binding mutation
→ fresh refresh/plan
→ remote a runtime read-back
→ second plan
→ audit a odstránenie dočasných oprávnení
```

„Ručne oprav JSON a pushni ho“ obchádza provider schemas, address semantics a ochranné kontroly. Používa sa iba v extrémnej recovery situácii s presným protokolom.

## 13. Import ako adoption binding

Existujúci remote objekt sa môže adoptovať:

```hcl
import {
  to = aws_vpc.main
  id = "vpc-0a42"
}
```

Configuration musí zároveň deklarovať resource:

```hcl
resource "aws_vpc" "main" {
  cidr_block = "10.40.0.0/16"
}
```

Import vytvorí binding. Nepreukazuje, že configuration presne zodpovedá actual attributes. Po importe je nutný fresh plan; provider defaults alebo neúplná konfigurácia môžu navrhnúť update alebo replacement.

## 14. Duplicate ownership

Najnebezpečnejší state model je rovnaký remote object v dvoch states:

```text
state A: aws_security_group.api → sg-123
state B: module.runtime.aws_security_group.api → sg-123
```

Oba workflows môžu meniť alebo odstrániť rovnaký objekt. Každý jednotlivo môže skončiť no-op po vlastnom apply, ale pri striedaní vytvárajú oscillation.

Detection vyžaduje inventory naprieč states a provider asset IDs, nie iba lokálny plan.

## 15. State boundaries a blast radius

Táto podsekcia vysvetľuje konkrétnu časť Terraform configuration, state a remote-resource subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inputs a graph cez provider API mutation až po state binding; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po exact provider target, remote/state reconciliation a druhý no-op plan.

Transition eviduje lock, writer identity, plan/apply lifecycle, dependency graph, recovery unit a permission scope.

Dopĺňa ho failure blast radius.

Boundary sa navrhuje podľa ownershipu, environmentu, security domainu, cadence, failure domainu a recovery nezávislosti.

Príliš veľký state:

```text
široké permissions
+ dlhý lock
+ veľký plan
+ široký incident
```

Príliš malé states:

```text
veľa cross-state contracts
+ orchestration complexity
+ eventual consistency medzi producers/consumers
```

Module boundary nie je automaticky state boundary.

## 16. Workspaces a environment identity

CLI workspace vyberá state instance v rámci backend configuration. Produkciu nesmie chrániť iba string `prod`.

Pre-apply identity gate overuje:

```text
backend bucket/host
state key alebo workspace
lineage
cloud account/subscription
region
apply identity
expected environment marker
```

```bash
terraform workspace show
aws sts get-caller-identity --query Account --output text
aws configure get region
```

Workspace output preukazuje selection v aktuálnom working directory. Nepreukazuje, že backend configuration samotná smeruje do správneho bucketu/keyu.

## 17. State obsahuje citlivé údaje

Táto podsekcia vysvetľuje konkrétnu časť Terraform configuration, state a remote-resource subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inputs a graph cez provider API mutation až po state binding; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po exact provider target, remote/state reconciliation a druhý no-op plan.

Transition eviduje passwords a tokens, private keys, connection strings, provider-returned sensitive attributes, internal endpoints a resource IDs a topology.

`sensitive = true` obmedzuje presentation, nie storage. Backend a recovery copies potrebujú encryption, narrow access, audit, versioning, retention a deletion lifecycle.

State sa neposiela do ticketu ani nepublikuje ako bežný CI artifact.

## 18. Backup a restore ako capability

Dôveryhodný backup model:

```text
versionované backend snapshots
→ chránená backup vrstva
→ restore do izolovaného test subjectu
→ lineage/serial/schema validation
→ porovnanie s configuration
→ read-only remote reconciliation
→ recovery verdict
```

Čitateľný JSON nie je dostatočný restore test. Snapshot musí byť kompatibilný s current configuration, provider schema, address migrations a remote reality.

## 19. Worked incident: starý restore vrátil neplatné addresses

Atlas obnovil serial `204`, hoci production bola na `208`. Medzičasom sa subnet migroval:

```text
S204: aws_subnet.private[0] → subnet-old
S208: aws_subnet.private["az_a"] → subnet-current
```

Restore S204 spôsobil, že plan považoval current address za nový objekt. Backup bol čitateľný, ale nebol správny recovery subject.

Recovery porovnala version history, configuration moved mappings, remote IDs a traffic. Správny snapshot sa obnovil a následný plan neobsahoval duplicate create.

## 20. Competing hypotheses pri duplicate create plane

Symptom: cloud obsahuje VPC, ale Terraform navrhuje `+ create`.

```text
H1: wrong backend key alebo workspace
H2: restore starého serialu
H3: address/key refactor bez moved mappingu
H4: remote create uspel, state write zlyhal
H5: object vytvoril iný owner
H6: provider číta iný account/region
H7: permissions maskujú object ako not found
```

Observation points:

```bash
terraform state pull > state.json
jq '{lineage,serial}' state.json
terraform state list
aws sts get-caller-identity
aws ec2 describe-vpcs --filters 'Name=tag:Application,Values=payments'
```

Backend/key audit testuje H1, version history H2, address diff H3, cloud request IDs H4/H5, account/region H6 a audit/authorization errors H7.

## 21. Authoritative recovery incidentu `IAC-PAY-75`

Incident sa rekonštruuje ako causal chain nad jedným Terraform configuration, state a remote-resource subject. Observations určujú prvý divergentný bod v reťazci resolved inputs a graph cez provider API mutation až po state binding; samy osebe nie sú success alebo failure verdictom. Recovery sa vyberá až po zachovaní evidence a uzatvára ju exact provider target, remote/state reconciliation a druhý no-op plan.

Atlas zistil, že orphaned VPC vznikla v `eu-west-1` a autoritatívna VPC zostala v `eu-central-1`.

Recovery:

```text
freeze oboch backend subjects
→ capture lineage/serial a cloud inventory
→ potvrď produkčný traffic na eu-central-1 VPC
→ obnov autoritatívny backend key
→ importuj iba intended objects, ak binding chýba
→ cleanup orphanu po dependency inventory
→ fresh plan
→ runtime network journey
→ second no-op plan
→ forbidden alternate-backend test
```

Acceptance:

```text
jeden intended VPC object
+ správny account/region
+ správna resource address/provider binding
+ latest serial v autoritatívnej lineage
+ žiadne orphaned routes/gateways
+ second plan no-op
+ wrong backend key odmietnutý pred plan/apply
```

## 22. Anti-patterny

### „State je cache, môžeme ho zmazať a znovu objaviť“

Táto podsekcia vysvetľuje konkrétnu časť Terraform configuration, state a remote-resource subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inputs a graph cez provider API mutation až po state binding; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po exact provider target, remote/state reconciliation a druhý no-op plan.

State obsahuje ownership bindings, ktoré remote discovery nemusí jednoznačne obnoviť.

### „Failed apply nič nezmenil“

Táto podsekcia vysvetľuje konkrétnu časť Terraform configuration, state a remote-resource subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inputs a graph cez provider API mutation až po state binding; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po exact provider target, remote/state reconciliation a druhý no-op plan.

Remote mutation a state commit sú oddelené failure boundaries.

### „Najnovší timestamp je správny backup“

Najnovšia object-store verzia môže patriť chybnému writerovi, wrong backend migration alebo už poškodenému successor snapshotu. Restore candidate sa vyberá podľa lineage, serial, writer/run identity a expected bindings a pred aktiváciou sa testuje offline planom a remote inventory.

Recovery potrebuje správnu lineage, serial, environment a compatibility.

### „Lock zabráni všetkým konfliktom“

Lock serializuje writers nad jedným backend subjectom. Nezabráni druhému state-u alebo manuálnemu writerovi meniť rovnaký remote object.

### „Import znamená, že configuration je správna“

Import vytvorí address-to-remote-ID binding. Neoverí, že HCL opisuje current object, provider target je správny alebo ownership má byť v tomto state-e. Po importe musí fresh plan vysvetliteľne smerovať k no-op alebo reviewed update bez neplánovaného replacementu.

Import vytvorí binding; fresh plan odhalí configuration/actual mismatch.

## 23. Kontrolné otázky

1. Prečo state nie je desired configuration ani obyčajná cache?
2. Aký rozdiel je medzi resource address, provider association a remote ID?
3. Čo znamenajú lineage a serial?
4. Čo state pull preukazuje a čo nepreukazuje?
5. Prečo refresh nemení desired intent?
6. Ako state serial ovplyvňuje saved plan freshness?
7. Aké outcomes môžu vzniknúť medzi provider mutation a state commitom?
8. Kedy je `state mv` legitímny a prečo je `moved` block často lepší?
9. Prečo `state rm` môže viesť k duplicate create?
10. Čo import preukazuje a čo nepreukazuje?
11. Ako sa deteguje duplicate ownership naprieč states?
12. Ako sa overí forbidden alternate-backend path a second operation?

## Glossary impact

Relevantné pojmy: Terraform state, state snapshot, resource binding, provider association, remote ID, lineage, serial, refresh, saved-plan freshness, state write failure, unknown outcome, state inspection, state surgery, import, duplicate ownership, workspace, state boundary, backup, restore a recovery subject.

## Primárne zdroje

- [Terraform state](https://developer.hashicorp.com/terraform/language/state)
- [Purpose of Terraform state](https://developer.hashicorp.com/terraform/language/state/purpose)
- [Terraform state backends](https://developer.hashicorp.com/terraform/language/state/backends)
- [Import existing resources](https://developer.hashicorp.com/terraform/language/import)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Expressions a dependency graph](expressions-and-dependency-graph.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Remote backend a state locking →](remote-backend-and-state-locking.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
