# Infrastructure as Code principles

Infrastructure as Code (IaC) je versionovaný change-control a reconciliation systém nad vzdialenými objektmi. Repository neobsahuje samotnú sieť, databázu ani IAM policy. Obsahuje deklaráciu požadovaného stavu, dependency contracty a rozhodovacie vstupy, z ktorých nástroj vytvorí plán remote operácií. Dôveryhodný výsledok preto nevzniká tým, že HCL prejde parserom. Vzniká až vtedy, keď presná konfigurácia, toolchain, state, target, identity a remote observation vedú k overenému technickému a business outcome-u.

Kapitola používa incident `IAC-PAY-75`. Atlas Payments pripravuje zmenu produkčného environmentu `prod-eu`: novú private sieť, dva subnets, load balancer a runtime service. Pipeline však načíta nesprávny backend key, default provider smeruje do iného regionu a po úspešnom remote create zlyhá state write. Každý jednotlivý krok môže vyzerať lokálne správne, ale celý authority chain vytvorí duplicitnú infraštruktúru mimo zamýšľaného subjectu.

## 1. Dominantný intent-to-outcome lifecycle

```text
business alebo platform intent
→ exact ownership a mutable attribute boundary
→ immutable source revision
→ pinned Terraform, providers a modules
→ resolved variables, backend a target identity
→ refresh a dependency graph
→ saved plan a policy/approval evidence
→ serialized scoped apply
→ provider remote operations
→ state commit alebo unknown outcome
→ independent runtime a business verification
→ drift, recovery a second-operation closure
```

Tento chain oddeľuje šesť otázok, ktoré sa pri slabom IaC procese často zlejú do jedného zeleného jobu:

1. **Čo sa má zmeniť?** Business intent a desired state.
2. **Kto smie atribút meniť?** Authoritative writer a ownership boundary.
3. **Nad čím sa plánuje?** Exact configuration, inputs, state a target.
4. **Čo nástroj predikuje?** Saved plan a risk evidence.
5. **Čo sa naozaj stalo?** Provider requesty, remote objekty a state commit.
6. **Je výsledok správny?** Runtime capability a business journey.

IaC sa stáva nebezpečným vtedy, keď sa jedna z týchto otázok nahradí implicitným predpokladom. Napríklad „plan je iba create“ nehovorí, či create smeruje do správneho účtu, či vznikne druhý objekt alebo či state pozná existujúci objekt.

## 2. Exact IaC change subject

Atlas označí zmenu ako `CHG-IAC-314`. Subject nie je iba Git commit. Obsahuje celý rozhodovací kontext:

```yaml
changeSubject:
  repository: atlas/platform-live
  sourceRevision: 71c4f2a
  rootModule: environments/prod-eu
  terraformVersion: 1.x-pinned
  providerLockDigest: sha256:4d5f...
  moduleManifestDigest: sha256:2c91...
  inputManifestDigest: sha256:0ea8...
  backend:
    type: s3
    key: payments/prod-eu/platform.tfstate
    lineage: 37fd...
    serial: 208
  target:
    account: "771100001234"
    region: eu-central-1
  workloadIdentity: gitlab-iac-prod
  savedPlanDigest: sha256:9abc...
  policyBundle: platform-policy@8f21c9e
```

Takýto manifest neobsahuje secret values. Obsahuje identity a fingerprints potrebné na reprodukciu a audit. Ak approval vidí iba názov branch-e alebo ľudský label `prod`, nevie určiť, ktorý backend, account, provider selection alebo variable set skutočne schválil.

Praktický read-back môže vyzerať takto:

```bash
terraform version
sha256sum .terraform.lock.hcl
terraform workspace show
aws sts get-caller-identity
aws configure get region
```

Výstupy preukazujú verziu CLI, digest lock file-u, zvolený workspace a observed AWS caller/region v tomto jobe. Nepreukazujú, že backend key je správny, že child modules používajú očakávané provider aliases ani že saved plan vznikol z rovnakého subjectu. Preto sa kontroluje aj backend configuration a plan metadata.

## 3. Desired, known a actual state

Terraform pracuje minimálne s troma odlišnými modelmi:

```text
desired state
= configuration + resolved inputs

known state
= resource addresses + remote bindings + posledné známe attributes

actual remote state
= objekty a hodnoty pozorované cez provider API
```

Plan nevzniká iba porovnaním HCL s cloudom. Terraform potrebuje state bindings, aby vedel, že napríklad:

```text
module.network.aws_vpc.main
→ account 7711 / eu-central-1 / vpc-0a42
```

Ak pipeline načíta prázdny alebo nesprávny state, cloud môže stále obsahovať produkčnú VPC, ale Terraform pre danú address-u binding nevidí. Výsledok `+ create` preto nepreukazuje, že objekt chýba. Preukazuje iba, že v aktuálnom configuration/state/observation subjecte neexistuje binding, ktorý by create eliminoval.

## 4. Authoritative source a writer ownership

Git repository môže byť authoritative pre desired declaration, ale nie automaticky pre každý mutable runtime atribút. Atlas definuje ownership napríklad takto:

```text
VPC CIDR a route tables          → Terraform network state
Kubernetes replica count         → deployment controller
DNS health failover              → DNS controller
incidentný WAF deny override     → incident controller s expiry
runtime secrets                  → secret manager a workload identity
```

Dôležité je slovo **jeden** authoritative writer pre konkrétny mutable atribút. Ak Terraform, autoscaler a operátor upravujú ten istý replica count, neexistuje jedna desired state authority. Systém bude oscilovať alebo bude jeden writer ticho rušiť rozhodnutia druhého.

`ignore_changes` môže byť legitímny, keď explicitne deleguje atribút inému controlleru:

```hcl
resource "example_service" "payments" {
  desired_count = 6

  lifecycle {
    ignore_changes = [desired_count]
  }
}
```

Tento blok však sám nepreukazuje, kto atribút vlastní, aké má limity alebo ako sa obnoví po chybe. Bez dokumentovaného autoscaling contractu iba skryje drift a odstráni Terraformu schopnosť odhaliť neželanú zmenu.

## 5. Deklaratívny model stále vykonáva imperatívne operácie

Konfigurácia:

```hcl
resource "aws_vpc" "main" {
  cidr_block           = "10.40.0.0/16"
  enable_dns_hostnames = true

  tags = {
    Application = "payments"
    Environment = "prod-eu"
    ManagedBy   = "terraform"
  }
}
```

opisuje požadovaný object state. Terraform Core a provider však stále vykonajú konkrétny sequence:

```text
resolve provider configuration
→ Read existujúceho bindingu
→ Create/Update/Delete request
→ poll alebo retry
→ normalize response
→ uložiť remote ID a attributes do state-u
```

Deklaratívnosť neodstraňuje side effects, eventual consistency ani partial failure. Presúva ich z ručne napísaného shell scriptu do graphu, provider implementation a state transition modelu.

## 6. Idempotencia, convergence a reproducibility

Tieto vlastnosti nie sú synonymá.

**Idempotencia** znamená, že opakovanie už dosiahnutého desired state-u nevytvorí ďalšiu zmenu. **Convergence** znamená, že reconciliation približuje actual state k desired state-u. **Reproducibility** znamená, že rovnaký explicitný subject vedie k porovnateľnému planu a výsledku.

Atlas očakáva:

```bash
terraform plan -out=tfplan
terraform apply tfplan
terraform plan -detailed-exitcode
```

Druhý plan má pri stabilnom systéme skončiť exit code `0`. Exit code `0` preukazuje, že Terraform v aktuálnom configuration/state/provider observation subjecte nevidí navrhovanú zmenu. Nepreukazuje, že runtime je zdravý, že neexistujú unmanaged objekty ani že iný controller nemení atribúty mimo Terraform modelu.

Reproducibility narúšajú najmä:

```text
mutable module ref
mutable provider selection
latest image data source
skryté TF_VAR_* overrides
iný backend alebo workspace
iný cloud account/region
provider/API normalizácia
remote drift medzi planom a apply
```

## 7. Plan je subject-bound predikcia

Saved plan je výsledok konkrétnej kombinácie:

```text
source revision
+ Terraform/provider/module versions
+ resolved variables
+ backend lineage/serial
+ refreshed remote observations
+ caller identity a target
→ plan artifact
```

Production workflow má zachovať túto identitu:

```bash
terraform plan -out=tfplan
sha256sum tfplan > tfplan.sha256
terraform show -json tfplan > tfplan.json
```

`tfplan` je executable decision artifact. `tfplan.json` je machine-readable evidence pre policy a review. SHA-256 preukazuje integritu konkrétnych bytes počas transferu. Nepreukazuje, že plan je stále fresh voči novému state serialu alebo remote driftu. Apply musí preto odmietnuť stale plan podľa state a platform semantics.

Human-readable summary:

```text
Plan: 12 to add, 3 to change, 0 to destroy.
```

nie je dostatočný risk model. Jediný IAM privilege expansion alebo stateful resource replacement môže mať vyššie riziko než stovky tag updates.

## 8. Apply nie je jedna ACID transakcia

Terraform graph môže obsahovať desiatky remote operácií. Cloud API a state backend netvoria jednu transakciu. Reálne outcomes zahŕňajú:

```text
no mutation
known partial mutation
remote request accepted, outcome unknown
remote mutation complete, state write failed
state committed, runtime verification failed
complete success
```

Provider timeout po create requeste neznamená, že objekt nevznikol. Backend write failure po remote success znamená, že actual state a known state sa rozdelili.

Evidence-preserving containment pri neznámom outcome-e je:

```text
zastaviť ďalších writers
→ zachovať plan, logs, request IDs a recovery state
→ read-only overiť backend lineage/serial
→ read-only overiť remote inventory
→ rozhodnúť import/restore/compensation
→ nový fresh plan
→ runtime a business verification
```

Slepý retry môže vytvoriť duplicate NAT gateway, druhú DNS mutation alebo opakovať nevratný external side effect.

## 9. State boundary je zároveň blast-radius boundary

Jeden Terraform state zdieľa:

- lock a writer queue;
- apply identity a permissions;
- plan/recovery lifecycle;
- dependency graph;
- incident blast radius;
- backup a restore unit.

Samostatný module nie je automaticky samostatný state. Module je code/interface boundary. State boundary vzniká samostatným root module, backend subjectom a execution lifecycle-om.

Atlas oddeľuje network, shared data platform a application runtime vtedy, keď majú rozdielny ownership, security domain, cadence a recovery. Nerozdeľuje ich iba preto, aby mal viac adresárov. Príliš veľký state vytvára široké permissions a lock contention; príliš malé states vytvárajú krehké cross-state contracts.

## 10. Worked incident `IAC-PAY-75`

Atlas pipeline mala aplikovať zmenu v `prod-eu`. Partial backend configuration však použila key:

```text
payments/prod-eu/platform-v2.tfstate
```

namiesto autoritatívneho:

```text
payments/prod-eu/platform.tfstate
```

Nový key obsahoval prázdny state. Default provider zároveň zdedil `AWS_REGION=eu-west-1`, hoci produkčný network mal byť v `eu-central-1`.

```text
správny source revision
+ nesprávny backend key
+ validná production identity
+ nesprávny default region
→ plan ukáže čistý create
→ policy vidí 0 destroy
→ apply vytvorí druhú VPC v eu-west-1
→ backend write zlyhá po remote create
→ job skončí failed bez bindingu
```

Všetky lokálne signály mohli zavádzať:

- HCL bolo validné;
- credentials boli platné;
- plan neobsahoval destroy;
- cloud create uspel;
- pipeline skončila failed, takže operátor predpokladal, že sa nič nevytvorilo.

Skutočný root cause bol nesprávny IaC subject a neuzavretý state transition.

## 11. Competing hypotheses a diskriminačné dôkazy

Symptom: cloud console ukazuje dve VPC s podobnými tags, Terraform plan stále navrhuje create.

```text
H1: pipeline používa nesprávny backend key
H2: správny state bol obnovený zo starého snapshotu
H3: resource address sa zmenila bez moved/import contractu
H4: remote create uspel, ale state write zlyhal
H5: objekt vytvoril iný owner mimo Terraformu
H6: konzola zobrazuje iný account alebo region
```

Diskriminačné observation points:

```bash
terraform workspace show
terraform state pull > recovery-state.json
jq '{lineage,serial}' recovery-state.json
aws sts get-caller-identity
aws ec2 describe-vpcs \
  --filters 'Name=tag:Application,Values=payments' \
  --query 'Vpcs[].{VpcId:VpcId,Cidr:CidrBlock,Tags:Tags}'
```

State lineage/serial a backend key testujú H1/H2. Git diff a resource addresses testujú H3. Cloud audit request ID a creation identity testujú H4/H5. Caller account a region testujú H6.

`describe-vpcs` preukazuje remote inventory dostupný danému callerovi v zvolenom regione. Nepreukazuje Terraform ownership ani správny state binding. `state pull` preukazuje backend snapshot, nie live health objektov.

## 12. Authoritative recovery

Atlas recovery postupuje bez okamžitého destroy:

1. zastaví všetky applies nad oboma candidate backend keys;
2. zachová plan, state snapshots, provider logs a cloud audit request IDs;
3. identifikuje správnu produkčnú VPC podľa accountu, regionu, CIDR, routes a runtime trafficu;
4. identifikuje orphaned VPC vytvorenú chybným runom;
5. obnoví správny backend configuration a state lineage;
6. podľa remote reality vykoná import alebo kontrolovaný cleanup orphanu;
7. vytvorí nový saved plan nad správnym subjectom;
8. overí network path a kritickú payment journey;
9. spustí druhý plan a zakázaný alternate-backend test.

Acceptance nie je iba `terraform plan = no changes`. Zahŕňa:

```text
správny backend key a lineage
+ správny account/region
+ jediný intended network object
+ správne state bindings
+ zdravé routes a service connectivity
+ second plan no-op
+ forbidden backend/region mismatch odmietnutý pred mutation
```

## 13. Praktický pipeline gate

Minimálny pre-apply shell gate môže explicitne overiť target:

```bash
set -euo pipefail

expected_account="771100001234"
expected_region="eu-central-1"

actual_account="$(aws sts get-caller-identity --query Account --output text)"
actual_region="$(aws configure get region)"

[[ "$actual_account" == "$expected_account" ]]
[[ "$actual_region" == "$expected_region" ]]

terraform init -input=false -backend-config=backend-prod-eu.hcl
terraform workspace show | grep -Fx 'default'
terraform plan -input=false -out=tfplan
terraform show -json tfplan > tfplan.json
```

Tento gate zastaví jednoduchý account/region mismatch. Nepreukazuje správnu lineage, resource ownership ani runtime outcome. Tie vyžadujú ďalšie state, policy a post-apply observations.

## 14. Anti-patterny

### „Git je source of truth, preto cloud console ignorujeme“

Git je authoritative pre desired declaration. Remote API a state sú nevyhnutné observation a identity vrstvy.

### „Plan nemá destroy, takže je bezpečný“

Duplicate create, privilege expansion, wrong-region mutation alebo stateful replacement môžu byť kritické bez destroy countu.

### „Apply failed, teda sa nič nezmenilo“

Remote mutation môže uspieť pred timeoutom alebo state-write failure.

### „Drift automaticky revertujeme“

Najprv treba klasifikovať intent a ownership. Break-glass containment môže byť legitímny dočasný desired state.

### „Idempotentný nástroj vyrieši retry“

Idempotencia závisí od správnej identity a bindingu. Retry nad prázdnym state-om môže vytvoriť ďalší objekt.

## 15. Kontrolné otázky

1. Prečo Git commit nie je úplný IaC change subject?
2. Aký je rozdiel medzi desired, known a actual state?
3. Čo state binding preukazuje a čo nepreukazuje?
4. Prečo deklaratívny nástroj stále potrebuje failure model pre imperatívne remote operácie?
5. Kedy je `ignore_changes` legitímny ownership contract a kedy iba skrytie driftu?
6. Čo preukazuje saved plan digest a čo nepreukazuje?
7. Prečo `0 to destroy` nie je bezpečnostný verdict?
8. Aké outcomes môžu vzniknúť medzi provider mutation a state commitom?
9. Prečo module boundary nie je automaticky state boundary?
10. Ktoré observation points odlíšia wrong backend od lost state write-u?
11. Ako sa overí forbidden alternate-account alebo alternate-backend path?
12. Prečo musí acceptance obsahovať druhý operation alebo no-op plan?

## Glossary impact

Relevantné pojmy: Infrastructure as Code, desired state, known state, actual state, authoritative writer, reconciliation, idempotencia, convergence, reproducibility, change subject, saved plan, remote mutation, partial outcome, unknown outcome, state binding, lineage, serial, blast radius, evidence-preserving containment a second-operation validation.

## Primárne zdroje

- [Terraform language overview](https://developer.hashicorp.com/terraform/language)
- [Terraform state](https://developer.hashicorp.com/terraform/language/state)
- [Purpose of Terraform state](https://developer.hashicorp.com/terraform/language/state/purpose)
- [Terraform backends](https://developer.hashicorp.com/terraform/language/state/backends)

<!-- KNOWLEDGE-NAVIGATION:START -->
[← Predchádzajúca: Security scanning](../06-gitlab/security-scanning.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Terraform providers, resources a data sources →](terraform-providers-resources-data-sources.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
