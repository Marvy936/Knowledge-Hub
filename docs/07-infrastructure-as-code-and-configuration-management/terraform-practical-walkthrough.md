# Praktický Terraform projekt od prázdneho adresára po overený remote state

Táto kapitola materializuje Terraform model do jedného malého, ale uceleného projektu. Vytvoríme produkčne orientovanú AWS network capability: VPC, dve private subnets a security group bez inbound pravidiel. Nejde o kompletnú produkčnú sieť. Cieľom je na reálnom HCL ukázať, ako spolu súvisia provider selection, typed variables, module contract, stable resource identity, test, backend, saved plan, policy, apply, state a remote read-back.

Budeme sledovať tento lifecycle:

```text
HCL source a module contract
→ pinned Terraform/provider selection
→ typed environment inputs
→ backend a target identity
→ fmt, validate a native test
→ refreshed saved plan
→ plan JSON a policy decision
→ apply presne saved planu
→ successor state snapshot
→ AWS remote read-back
→ second no-op plan
→ drift a recovery closure
```

Každý zelený krok má inú dôkazovú hranicu. `terraform validate` nepreukazuje cloud permissions. Mock test nepreukazuje AWS API behavior. Plan je predikcia. Úspešný apply nepreukazuje, že aplikácia dokáže sieť použiť. Druhý no-op plan nepreukazuje budúcu absenciu driftu.

## 1. Výsledná štruktúra projektu

Vytvor adresáre:

```bash
mkdir -p atlas-network/modules/network
mkdir -p atlas-network/tests
mkdir -p atlas-network/policy
mkdir -p atlas-network/environments/prod
cd atlas-network
```

Výsledná štruktúra:

```text
atlas-network/
├── versions.tf
├── backend.tf
├── main.tf
├── variables.tf
├── outputs.tf
├── terraform.tfvars.example
├── environments/
│   └── prod/
│       ├── backend.hcl.example
│       └── terraform.tfvars.example
├── modules/
│   └── network/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
├── tests/
│   └── network.tftest.hcl
└── policy/
    └── network.rego
```

Adresár je iba configuration source. Nie je to state ani remote infraštruktúra. Exact Terraform change subject vznikne až kombináciou source revision, CLI/provider/module versions, effective variables, backend key, state lineage/serial, AWS account/region a workload identity.

## 2. `versions.tf`: toolchain a provider contract

Vytvor `versions.tf`:

```hcl
terraform {
  required_version = ">= 1.9.0, < 2.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = local.common_tags
  }
}
```

`required_version` definuje podporovaný Terraform CLI interval. Provider constraint `~> 5.0` povoľuje kompatibilné minor/patch releases v major verzii 5. Skutočný resolved provider build sa uloží do `.terraform.lock.hcl` po `terraform init`.

Constraint nie je lock. Dvaja operátori môžu bez committed lockfile resolve-nuť rozdielne provider verzie. Preto po prvom init-e commitni `.terraform.lock.hcl` a v CI overuj jeho zmenu rovnako ako zmenu HCL.

Provider block určuje region a default tags. AWS identity však pochádza z credential chainu procesu. HCL `region = "eu-central-1"` nepreukazuje, že job používa produkčný account.

Pred planom preto read-backni caller identity:

```bash
aws sts get-caller-identity
aws configure get region
```

Očakávaný produkčný subject môže byť:

```json
{
  "Account": "771100001234",
  "Arn": "arn:aws:sts::771100001234:assumed-role/terraform-prod/gitlab-98122"
}
```

Tento output preukazuje AWS principal aktuálneho CLI requestu. Nepreukazuje, že Terraform provider použije rovnaký credential chain, ak má provider alias alebo explicitné environment overrides. Pipeline má logovať provider target metadata bez secretov a porovnať ho s change subjectom.

## 3. `backend.tf`: state storage contract

Vytvor `backend.tf`:

```hcl
terraform {
  backend "s3" {}
}
```

Backend arguments nedávame priamo do source, pretože account-specific bucket a key patria environment configuration. Produkčná ukážka v `environments/prod/backend.hcl.example`:

```hcl
bucket  = "atlas-terraform-state-prod"
key     = "network/eu-central-1/terraform.tfstate"
region  = "eu-central-1"
encrypt = true
```

S3 bucket musí mať versioning, least-privilege access, audit a organizáciou schválený locking/concurrency model. Samotné `encrypt = true` nepreukazuje správnu KMS key policy, retention ani schopnosť restore-u.

Backend key je súčasť identity. Ak operátor omylom použije:

```text
network/dev/terraform.tfstate
```

Terraform môže navrhnúť vytvorenie druhej produkčnej VPC, pretože z pohľadu načítaného state-u žiadna neexistuje.

## 4. Root variables: typed environment contract

Vytvor `variables.tf`:

```hcl
variable "environment" {
  description = "Environment identity used in names and tags."
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be dev, staging, or prod."
  }
}

variable "aws_region" {
  description = "AWS region containing the network."
  type        = string
  default     = "eu-central-1"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string

  validation {
    condition     = can(cidrnetmask(var.vpc_cidr))
    error_message = "vpc_cidr must be a valid IPv4 CIDR."
  }
}

variable "private_subnets" {
  description = "Stable subnet keys mapped to AZ and CIDR."

  type = map(object({
    availability_zone = string
    cidr_block        = string
  }))

  validation {
    condition = alltrue([
      for subnet in values(var.private_subnets) :
      can(cidrnetmask(subnet.cidr_block))
    ])
    error_message = "Every private subnet must use a valid IPv4 CIDR."
  }

  validation {
    condition     = length(var.private_subnets) >= 2
    error_message = "At least two private subnets are required."
  }
}

variable "owner" {
  description = "Owning team recorded in tags."
  type        = string
}
```

Map keys budú resource identity:

```hcl
private_subnets = {
  az_a = {
    availability_zone = "eu-central-1a"
    cidr_block        = "10.40.10.0/24"
  }
  az_b = {
    availability_zone = "eu-central-1b"
    cidr_block        = "10.40.20.0/24"
  }
}
```

Kľúče `az_a` a `az_b` majú zostať stabilné. Ak ich premenuješ na `subnet_1` a `subnet_2` bez `moved` contractu, Terraform môže interpretovať zmenu ako odstránenie starých a vytvorenie nových instances.

## 5. Root locals a module call

Vytvor `main.tf`:

```hcl
locals {
  common_tags = {
    Environment = var.environment
    Owner       = var.owner
    ManagedBy   = "terraform"
    Repository  = "atlas/network"
  }
}

module "network" {
  source = "./modules/network"

  name            = "atlas-${var.environment}"
  vpc_cidr        = var.vpc_cidr
  private_subnets = var.private_subnets
  tags            = local.common_tags
}
```

Root module vlastní environment composition. Child module vlastní reusable network capability. Local `common_tags` pomenúva odvodenú hodnotu, ale neskrýva remote mutation. Source `./modules/network` je lokálna immutable revision v tom istom commit subjecte.

Pri registry alebo Git module source používaj immutable version/tag/commit podľa organization policy. Mutable branch ako `?ref=main` umožní, aby rovnaký root commit neskôr načítal iný child module.

## 6. Child module variables

`modules/network/variables.tf`:

```hcl
variable "name" {
  type = string
}

variable "vpc_cidr" {
  type = string
}

variable "private_subnets" {
  type = map(object({
    availability_zone = string
    cidr_block        = string
  }))
}

variable "tags" {
  type    = map(string)
  default = {}
}
```

Child module opakuje svoj verejný contract. Root validation je užitočná pre caller UX, no reusable module sa nemá spoliehať na to, že každý caller vykonal rovnakú validation.

## 7. Child module resources

`modules/network/main.tf`:

```hcl
resource "aws_vpc" "this" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = merge(var.tags, {
    Name = var.name
  })

}

resource "aws_subnet" "private" {
  for_each = var.private_subnets

  vpc_id                  = aws_vpc.this.id
  availability_zone       = each.value.availability_zone
  cidr_block              = each.value.cidr_block
  map_public_ip_on_launch = false

  tags = merge(var.tags, {
    Name = "${var.name}-private-${each.key}"
    Tier = "private"
  })
}

resource "aws_security_group" "workload" {
  name_prefix = "${var.name}-workload-"
  description = "Default workload security group without inbound access"
  vpc_id      = aws_vpc.this.id

  egress {
    description = "Temporary broad egress for the walkthrough"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, {
    Name = "${var.name}-workload"
  })
}
```

Reference `aws_vpc.this.id` vytvára implicit dependency z oboch resource typov na VPC. Nie je potrebný `depends_on`.

`for_each` vytvára addresses:

```text
aws_subnet.private["az_a"]
aws_subnet.private["az_b"]
```

Tieto addresses sa viažu v state na konkrétne AWS subnet IDs. Poradie mapy nie je identity; kľúč je identity.

Security group zámerne nemá ingress block. To neznamená, že celý VPC nemá inbound exposure. Iná security group, Network ACL, load balancer alebo peering path môžu vytvoriť alternate route. Policy nad týmto modulom kontroluje iba deklarované resources v svojom subjecte.

## 8. Module outputs

`modules/network/outputs.tf`:

```hcl
output "vpc_id" {
  description = "AWS VPC ID."
  value       = aws_vpc.this.id
}

output "vpc_cidr" {
  description = "Configured VPC CIDR."
  value       = aws_vpc.this.cidr_block
}

output "private_subnet_ids" {
  description = "Stable subnet keys mapped to AWS subnet IDs."
  value = {
    for key, subnet in aws_subnet.private :
    key => subnet.id
  }
}

output "private_subnet_count" {
  value = length(aws_subnet.private)
}

output "workload_security_group_id" {
  value = aws_security_group.workload.id
}
```

Root `outputs.tf` publikuje iba contract, ktorý potrebuje downstream consumer:

```hcl
output "vpc_id" {
  value = module.network.vpc_id
}

output "vpc_cidr" {
  value = module.network.vpc_cidr
}

output "private_subnet_ids" {
  value = module.network.private_subnet_ids
}

output "private_subnet_count" {
  value = module.network.private_subnet_count
}

output "workload_security_group_id" {
  value = module.network.workload_security_group_id
}
```

Nepublikujeme celý provider resource object. Taký output by coupling-oval consumerov na internú provider schema a sťažoval refaktor.

## 9. Environment values

`environments/prod/terraform.tfvars.example`:

```hcl
environment = "prod"
aws_region  = "eu-central-1"
owner       = "payments-platform"
vpc_cidr    = "10.40.0.0/16"

private_subnets = {
  az_a = {
    availability_zone = "eu-central-1a"
    cidr_block        = "10.40.10.0/24"
  }
  az_b = {
    availability_zone = "eu-central-1b"
    cidr_block        = "10.40.20.0/24"
  }
}
```

V reálnom repository vytvor environment-specific file bez secretov. Sensitive credentials sa nesmú ukladať do tfvars v Git-e. Terraform aj saved plan môžu sensitive values uložiť do state/plan artifactu aj vtedy, keď CLI output hodnotu rediguje.

## 10. Prvý `init` a lockfile

Inicializácia bez production backendu pre lokálnu statickú kontrolu:

```bash
terraform init -backend=false
terraform providers
```

Očakávaný výstup ukáže provider requirement rootu a module-u. `init -backend=false` preukazuje, že Terraform dokázal resolve-nuť modules/providers bez backend initialization. Nepreukazuje prístup k production state-u.

Pre production plan:

```bash
terraform init \
  -input=false \
  -reconfigure \
  -backend-config=environments/prod/backend.hcl
```

Pred týmto príkazom vytvor skutočný `backend.hcl` z bezpečného environment configuration source-u. Nepoužívaj automaticky `.example` file bez kontroly bucketu, key a accountu.

Po init-e skontroluj:

```bash
terraform version
terraform providers
sha256sum .terraform.lock.hcl
```

Lockfile digest patrí do plan subjectu.

## 11. Formatting a validation

Formatting a validation sú preflight checks nad source a resolved schemas. Nevytvárajú cloud plan ani remote operation, preto ich úspech nemožno preniesť na authorization, quota alebo runtime. Nasledujúce commands sa čítajú ako dva odlišné verdicts a ich outputs sa uchovávajú oddelene.

```bash
terraform fmt -check -recursive
terraform validate -json > validate.json
jq . validate.json
```

Očakávaný validation result:

```json
{
  "valid": true,
  "error_count": 0,
  "warning_count": 0,
  "diagnostics": []
}
```

Toto preukazuje configuration consistency voči načítaným schemas. Neoveruje AWS credentials, quotas, organization policy, CIDR overlap s existujúcou sieťou ani apply-time behavior.

## 12. Native test s mock providerom

`tests/network.tftest.hcl`:

```hcl
mock_provider "aws" {}

run "production_network_contract" {
  command = plan

  variables {
    environment = "prod"
    aws_region  = "eu-central-1"
    owner       = "payments-platform"
    vpc_cidr    = "10.40.0.0/16"

    private_subnets = {
      az_a = {
        availability_zone = "eu-central-1a"
        cidr_block        = "10.40.10.0/24"
      }
      az_b = {
        availability_zone = "eu-central-1b"
        cidr_block        = "10.40.20.0/24"
      }
    }
  }

  assert {
    condition     = output.vpc_cidr == "10.40.0.0/16"
    error_message = "The module changed the production VPC CIDR."
  }

  assert {
    condition     = output.private_subnet_count == 2
    error_message = "Production requires exactly two walkthrough subnets."
  }

  assert {
    condition = setequals(
      toset(keys(output.private_subnet_ids)),
      toset(["az_a", "az_b"]),
    )
    error_message = "Subnet identity keys are not stable."
  }
}

run "reject_single_subnet" {
  command = plan

  variables {
    environment = "prod"
    aws_region  = "eu-central-1"
    owner       = "payments-platform"
    vpc_cidr    = "10.40.0.0/16"

    private_subnets = {
      az_a = {
        availability_zone = "eu-central-1a"
        cidr_block        = "10.40.10.0/24"
      }
    }
  }

  expect_failures = [var.private_subnets]
}
```

Spusti:

```bash
terraform test -json > terraform-test.json
```

Mock test overuje HCL evaluation, module contract, addresses a assertions bez AWS mutation. Nepreukazuje, že availability zones existujú v target account-e, že IAM povoľuje create, že CIDR nekoliduje alebo že provider waiter dokončí operácie.

Forbidden test je dôležitý: happy path s dvoma subnetmi nepreukazuje, že module skutočne odmietne jednu subnet.

## 13. Saved plan pre produkčný subject

Najprv potvrď identity:

```bash
aws sts get-caller-identity > aws-caller.json
terraform workspace show
```

Potom vytvor saved plan:

```bash
terraform plan \
  -input=false \
  -var-file=environments/prod/terraform.tfvars \
  -out=tfplan

sha256sum tfplan > tfplan.sha256
terraform show -no-color tfplan > tfplan.txt
terraform show -json tfplan > tfplan.json
```

Plan file môže obsahovať sensitive hodnoty v clear form. Neukladaj ho do Git repository a chráň CI artifact access/retention.

Human-readable summary môže vyzerať:

```text
Plan: 4 to add, 0 to change, 0 to destroy.
```

Počet actions nie je risk verdict. Jedna IAM policy alebo database replacement môže byť rizikovejšia než desiatky tag updates.

## 14. Machine-readable kontrola planu

Skontroluj action inventory:

```bash
jq -r '
  .resource_changes[]
  | [.address, (.change.actions | join(","))]
  | @tsv
' tfplan.json
```

Očakávaný prvý plan:

```text
module.network.aws_security_group.workload	create
module.network.aws_subnet.private["az_a"]	create
module.network.aws_subnet.private["az_b"]	create
module.network.aws_vpc.this	create
```

Hard gate proti destroy/replacement:

```bash
jq -e '
  [
    .resource_changes[]
    | select(
        (.change.actions | index("delete")) != null
      )
  ]
  | length == 0
' tfplan.json
```

Exit code `0` preukazuje, že v tomto plan JSON nebol resource change s `delete` action. Nepreukazuje absenciu destructive side effectu ukrytého v provider update operácii ani correctness target accountu.

## 15. Rego policy nad plan JSON

`policy/network.rego`:

```rego
package atlas.terraform.network

import rego.v1

default allow := false

public_ingress contains address if {
  resource := input.resource_changes[_]
  resource.type == "aws_security_group"
  ingress := resource.change.after.ingress[_]
  ingress.cidr_blocks[_] == "0.0.0.0/0"
  address := resource.address
}

public_ipv6_ingress contains address if {
  resource := input.resource_changes[_]
  resource.type == "aws_security_group"
  ingress := resource.change.after.ingress[_]
  ingress.ipv6_cidr_blocks[_] == "::/0"
  address := resource.address
}

allow if {
  count(public_ingress) == 0
  count(public_ipv6_ingress) == 0
}

deny contains message if {
  address := public_ingress[_]
  message := sprintf("%s contains public IPv4 ingress", [address])
}

deny contains message if {
  address := public_ipv6_ingress[_]
  message := sprintf("%s contains public IPv6 ingress", [address])
}
```

Spusti cez Conftest:

```bash
conftest test tfplan.json --policy policy
```

Policy kontroluje resolved plan representation. Nevidí alternate security groups mimo tohto state-u ani runtime route path. Policy package revision a digest musia patriť do approval subjectu.

## 16. Apply presne schváleného plánu

Pred apply over digest:

```bash
sha256sum -c tfplan.sha256
```

Potom aplikuj saved plan:

```bash
terraform apply -input=false tfplan
```

Nepoužívaj po approvale:

```bash
terraform apply -auto-approve
```

bez plan file-u. Taký príkaz vytvorí nový implicitný plan nad novými observations a nemusí vykonať schválený subject.

Úspešný apply output môže skončiť:

```text
Apply complete! Resources: 4 added, 0 changed, 0 destroyed.
```

Tento verdict preukazuje, že Terraform dokončil svoj apply flow a zapísal successor state podľa backend semantics. Nepreukazuje aplikačnú použiteľnosť siete ani absenciu external driftu po apply.

## 17. State read-back

Po apply sa state číta ako successor knowledge snapshot, nie ako náhrada cloud verification. Read-back musí potvrdiť lineage/serial, expected addresses, provider association a immutable remote IDs a následne ich porovnať s AWS API a runtime capability.

```bash
terraform state list
terraform output -json > outputs.json
```

Očakávané addresses:

```text
module.network.aws_security_group.workload
module.network.aws_subnet.private["az_a"]
module.network.aws_subnet.private["az_b"]
module.network.aws_vpc.this
```

`terraform state list` preukazuje bindings v načítanom state snapshot-e. Nepreukazuje, že remote objekty stále existujú.

Získaj IDs:

```bash
VPC_ID="$(terraform output -raw vpc_id)"
SG_ID="$(terraform output -raw workload_security_group_id)"
terraform output -json private_subnet_ids > private-subnet-ids.json
```

## 18. Nezávislý AWS remote read-back

VPC:

```bash
aws ec2 describe-vpcs \
  --vpc-ids "$VPC_ID" \
  --query 'Vpcs[0].{VpcId:VpcId,Cidr:CidrBlock,State:State}' \
  --output json
```

Očakávané:

```json
{
  "VpcId": "vpc-0123456789abcdef0",
  "Cidr": "10.40.0.0/16",
  "State": "available"
}
```

Subnets:

```bash
jq -r 'to_entries[].value' private-subnet-ids.json |
while read -r subnet_id; do
  aws ec2 describe-subnets \
    --subnet-ids "$subnet_id" \
    --query 'Subnets[0].{Id:SubnetId,Vpc:VpcId,Az:AvailabilityZone,Cidr:CidrBlock,PublicIp:MapPublicIpOnLaunch}' \
    --output json
done
```

Security group ingress:

```bash
aws ec2 describe-security-groups \
  --group-ids "$SG_ID" \
  --query 'SecurityGroups[0].IpPermissions' \
  --output json
```

Očakávaný ingress output:

```json
[]
```

Prázdny ingress list preukazuje remote rule state tejto security group v čase observation. Nepreukazuje, že workload nie je dostupný cez inú security group, load balancer alebo network path.

## 19. Second no-op plan

Po apply vytvor fresh plan:

```bash
set +e
terraform plan \
  -input=false \
  -detailed-exitcode \
  -var-file=environments/prod/terraform.tfvars \
  -out=second.tfplan
status=$?
set -e

case "$status" in
  0)
    echo "No changes: configuration, state and refreshed observations converge."
    ;;
  2)
    echo "Unexpected changes detected."
    terraform show -no-color second.tfplan
    exit 1
    ;;
  *)
    echo "Plan execution failed."
    exit "$status"
    ;;
esac
```

`-detailed-exitcode` rozlišuje:

```text
0 → successful plan with no changes
2 → successful plan with changes
1 → error
```

No-op plan je silný idempotency/convergence check pre tento moment. Nepreukazuje, že o minútu nevznikne drift alebo že remote capability spĺňa business SLO.

## 20. GitLab pipeline pre plan a apply

Terraform walkthrough možno vložiť do GitLab-u takto:

```yaml
stages:
  - validate
  - test
  - plan
  - policy
  - apply
  - verify

variables:
  TF_IN_AUTOMATION: "true"
  TF_INPUT: "false"
  TF_ROOT: infra/network

terraform_validate:
  stage: validate
  image: hashicorp/terraform:1.9.8@sha256:<verified-terraform-image-digest>
  script:
    - cd "$TF_ROOT"
    - terraform init -backend=false
    - terraform fmt -check -recursive
    - terraform validate

terraform_test:
  stage: test
  image: hashicorp/terraform:1.9.8@sha256:<verified-terraform-image-digest>
  script:
    - cd "$TF_ROOT"
    - terraform init -backend=false
    - terraform test -json > terraform-test.json
  artifacts:
    when: always
    paths:
      - "$TF_ROOT/terraform-test.json"

terraform_plan_prod:
  stage: plan
  image: hashicorp/terraform:1.9.8@sha256:<verified-terraform-image-digest>
  tags: [terraform-prod]
  resource_group: terraform-network-prod
  id_tokens:
    AWS_OIDC_TOKEN:
      aud: https://gitlab.example.com
  script:
    - cd "$TF_ROOT"
    - ./scripts/exchange-aws-oidc.sh
    - aws sts get-caller-identity
    - terraform init -reconfigure -backend-config=environments/prod/backend.hcl
    - terraform plan -var-file=environments/prod/terraform.tfvars -out=tfplan
    - sha256sum tfplan > tfplan.sha256
    - terraform show -json tfplan > tfplan.json
  artifacts:
    expire_in: 24 hours
    access: developer
    paths:
      - "$TF_ROOT/tfplan"
      - "$TF_ROOT/tfplan.sha256"
      - "$TF_ROOT/tfplan.json"

terraform_policy_prod:
  stage: policy
  image: openpolicyagent/conftest:v0.56.0@sha256:<verified-conftest-digest>
  needs:
    - job: terraform_plan_prod
      artifacts: true
  script:
    - cd "$TF_ROOT"
    - conftest test tfplan.json --policy policy

terraform_apply_prod:
  stage: apply
  image: hashicorp/terraform:1.9.8@sha256:<verified-terraform-image-digest>
  tags: [terraform-prod]
  resource_group: terraform-network-prod
  needs:
    - job: terraform_plan_prod
      artifacts: true
    - job: terraform_policy_prod
  when: manual
  allow_failure: false
  environment:
    name: infrastructure/network-prod
  script:
    - cd "$TF_ROOT"
    - ./scripts/exchange-aws-oidc.sh
    - terraform init -reconfigure -backend-config=environments/prod/backend.hcl
    - sha256sum -c tfplan.sha256
    - terraform apply tfplan
    - terraform output -json > applied-outputs.json
  artifacts:
    expire_in: 7 days
    paths:
      - "$TF_ROOT/applied-outputs.json"
```

Plan a apply jobs používajú rovnaký backend, target identity class a serialized `resource_group`. Apply stiahne exact plan artifact a overí checksum.

CI artifact access musí byť obmedzený, pretože plan môže obsahovať sensitive data. `access: developer` je iba príklad; organizácia musí nastaviť vhodnú minimálnu rolu a retention.

## 21. Worked failure: správny HCL, nesprávny backend key

Operátor použije production credentials a production tfvars, ale backend file má dev key:

```text
AWS account = prod
variables = prod
backend key = network/dev/terraform.tfstate
```

Plan navrhne vytvorenie všetkých štyroch resources. HCL aj provider authentication sú validné, ale state subject je nesprávny.

Containment:

```text
zastaviť apply
→ zaznamenať backend config a caller identity
→ potvrdiť production state lineage/serial
→ re-init na správny key
→ vytvoriť nový plan
→ zneplatniť starý approval
```

Nikdy neopravuj takýto incident ručným kopírovaním state file-u bez potvrdenia lineage, versions a lock ownershipu.

## 22. Worked failure: premenovanie `for_each` key bez moved blocku

Zmena:

```hcl
private_subnets = {
  primary = { ... }
  secondary = { ... }
}
```

nahradí keys `az_a` a `az_b`. Terraform vidí nové addresses:

```text
old: aws_subnet.private["az_a"]
new: aws_subnet.private["primary"]
```

Bez migration contractu plan môže obsahovať delete/create. Ak ide iba o logical rename, pridaj versionované moved blocks v module:

```hcl
moved {
  from = aws_subnet.private["az_a"]
  to   = aws_subnet.private["primary"]
}

moved {
  from = aws_subnet.private["az_b"]
  to   = aws_subnet.private["secondary"]
}
```

Potom vytvor nový saved plan a over, že nevzniká remote replacement. `moved` mení Terraform address binding, nie AWS subnet ID.

## 23. Worked failure: apply vytvoril VPC, state write zlyhal

Možný partial outcome:

```text
AWS CreateVpc accepted
→ VPC vznikla
→ runner stratil backend connectivity
→ successor state sa nezapísal
→ job failed
```

Slepý retry môže vytvoriť druhú VPC. Recovery:

```text
zastaviť ďalšie applies
→ zachovať provider logs a request ID
→ read-only AWS search podľa tags/CIDR/timestamp
→ zálohovať current state
→ potvrdiť exact remote identity
→ importovať binding na správnu address
→ fresh plan
→ remote a second no-op verification
```

Príkaz importu je až posledná časť identity investigation:

```bash
terraform import module.network.aws_vpc.this vpc-0123456789abcdef0
```

Úspešný import preukazuje vytvorenie state bindingu. Nepreukazuje, že configuration opisuje všetky remote attributes správne; preto musí nasledovať fresh plan.

## 24. Diagnostický walkthrough

Diagnostika začína presným symptómom a immutable operation subjectom. H1/H2 testujú, či pipeline zvolila správny backend, workspace, lineage a serial. H3 a H7 porovnávajú configuration addresses so state inventory, aby odlíšili chýbajúci `moved` contract od lost bindingu.

CloudTrail alebo ekvivalentné request IDs testujú H4/H5: remote create mohol uspieť pred timeoutom alebo objekt mohol vytvoriť iný writer. Caller identity, provider alias/region a debug metadata bez secrets testujú H6, teda wrong target configuration. Každá observation má timestamp a account/region context.

Až po tomto rozlíšení sa vyberie recovery: backend correction, import, moved transition, remote cleanup alebo state restore. Slepý `terraform apply`, `state rm`, `force-unlock` alebo `-target` sú zakázané, kým nie je známy first divergent transition. Closure vyžaduje remote/state binding, runtime test, forbidden wrong-target fixture a druhý no-op plan.

Symptom: second plan navrhuje vytvoriť ďalšiu VPC.

Najprv stabilizuj subject:

```text
source commit
Terraform/provider lock digest
backend bucket/key
state lineage/serial
workspace
AWS caller account/role
region
variables digest
predchádzajúci plan/apply ID
```

Competing hypotheses:

```text
H1: nesprávny backend key
H2: state bol obnovený zo starého snapshotu
H3: resource address sa zmenila
H4: remote create uspel, state write zlyhal
H5: VPC vytvoril iný writer
H6: AWS CLI a provider používajú iný account/region
H7: state binding bol ručne odstránený
```

Backend config a lineage/serial testujú H1/H2, Git diff a `terraform state list` testujú H3/H7, CloudTrail/request IDs testujú H4/H5, caller identity a provider debug metadata testujú H6 a tags, timestamps a remote IDs spájajú objekt s konkrétnym runom.

Až po potvrdení hypotézy zvoľ import, state restore, configuration repair alebo odstránenie unmanaged duplicate objektu.

## 25. Acceptance checklist

Walkthrough je dokončený iba vtedy, keď vieš preukázať:

```text
Terraform CLI a provider selection sú pinned a read-backnuté
+ AWS account/role/region zodpovedajú target subjectu
+ backend bucket/key a state lineage/serial sú správne
+ fmt a validate prejdú
+ happy aj forbidden native test prejdú
+ saved plan má checksum a restricted artifact handling
+ plan JSON neobsahuje nepovolený destroy/replacement
+ policy číta presne saved plan JSON
+ apply používa presne schválený plan file
+ state obsahuje očakávané stable addresses
+ AWS remote IDs/CIDRs/AZs zodpovedajú outputs
+ security group nemá očakávaný forbidden ingress
+ second plan skončí exit code 0
+ chybný backend alebo renamed key nevie ticho obísť review
```

Týmto spôsobom sa Terraform neučí ako séria príkazov `init`, `plan`, `apply`. Učí sa ako identity, prediction, mutation, state a verification systém, v ktorom každý artifact a output odpovedá na inú otázku.

## Primárne zdroje

- [Terraform language documentation](https://developer.hashicorp.com/terraform/language)
- [Terraform providers](https://developer.hashicorp.com/terraform/language/providers)
- [Terraform modules](https://developer.hashicorp.com/terraform/language/modules)
- [Terraform test](https://developer.hashicorp.com/terraform/cli/commands/test)
- [Terraform test files](https://developer.hashicorp.com/terraform/language/files/tests)
- [Terraform plan](https://developer.hashicorp.com/terraform/cli/commands/plan)
- [Terraform show](https://developer.hashicorp.com/terraform/cli/commands/show)
- [Terraform JSON output format](https://developer.hashicorp.com/terraform/internals/json-format)
- [Terraform state](https://developer.hashicorp.com/terraform/language/state)
- [AWS EC2 VPC documentation](https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Terraform testing a policy](terraform-testing-and-policy.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Terraform troubleshooting →](terraform-troubleshooting.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
