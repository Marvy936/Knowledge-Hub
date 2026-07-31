# Terraform vs. Ansible

Terraform a Ansible sa prekrývajú v tom, že oba dokážu meniť cloud resources, files, services alebo API objekty. Ich dominantný identity a state model je však odlišný. Terraform je resource-lifecycle engine s persistentnými address-to-remote bindings, dependency graphom a plan/apply transitionom. Ansible je target-oriented configuration a orchestration engine, ktorý pri každom run-e skladá inventory, variables, facts a ordered per-host operations. Správna otázka preto nie je „ktorý nástroj je lepší“, ale ktorý nástroj má byť autoritatívnym writerom konkrétneho objektu alebo atribútu a aký úzky contract odovzdá druhému.

Kapitola uzatvára incident `IAC-PAY-79`. Terraform vlastní production security group a povoľuje ingress iba z load balancera. Ansible incident runbook pridáva temporary admin CIDR priamo cez cloud module. Scheduled Terraform apply rule odstráni, runbook ju opäť pridá a oba nástroje individuálne konvergujú k vlastnému desired state-u. Súčasne Ansible inventory číta interné Terraform state addresses, takže po správnom `count → for_each` refaktore vráti prázdny target set. Root cause je chýbajúci ownership a provisioning-to-configuration contract.

## 1. Dominantný capability-to-combined-outcome lifecycle

```text
business/platform capability intent
→ inventory objektov a mutable attributes
→ jeden authoritative writer pre každý attribute
→ Terraform resource change subject
→ saved plan, policy, apply a state/remote verification
→ explicitný readiness transition
→ versionovaný narrow host/capability contract
→ Ansible run subject a per-host convergence
→ combined service/business verification
→ Terraform second no-op plan
→ Ansible second no-change converge
→ drift, ownership transfer a recovery closure
```

## 2. Dva odlišné state stroje

### Terraform

```text
configuration
+ provider target
+ prior state bindings
+ remote refresh
→ dependency graph
→ saved plan
→ create/update/replace/destroy
→ successor state snapshot
→ runtime verification
```

Terraform je silný tam, kde stabilná resource identity, lifecycle a persistent binding tvoria hlavný problém.

### Ansible

```text
playbook a execution environment
+ resolved inventory
+ effective variables/facts
→ ordered per-host tasks
→ module/API state observations a mutations
→ changed/failure/handler transitions
→ loaded runtime a fleet verification
```

Ansible je silný tam, kde hlavný problém tvorí configuration hostov/devices a ordered orchestration.

## 3. Ownership na úrovni objektu alebo atribútu

Boundary „Terraform infra, Ansible config“ je iba začiatok. Potrebujeme presnú maticu:

| Objekt alebo atribút | Autoritatívny writer | Read-only consumer |
|---|---|---|
| VM lifecycle a image ID | Terraform | Ansible inventory |
| VPC, subnet, route | Terraform | Ansible diagnostika |
| Security-group ingress | Terraform | Ansible read-only |
| Host package version | Ansible alebo image build, nie obaja implicitne | runtime verifier |
| Application config file | Ansible | service process |
| Runtime service state | Ansible | monitoring |
| Load-balancer object | Terraform | Ansible orchestration |
| Per-host LB membership počas rollout-u | jeden explicitný owner/controller | druhý tool coordinate/read |
| DNS record | Terraform | business verifier |

Ownership contract:

```yaml
ownership:
  subject: security-group/payments-api/ingress
  writer:
    tool: terraform
    repository: atlas/platform-live
    stateKey: payments/network/prod-eu.tfstate
  readers:
    - ansible-incident-diagnostics
  emergencyMutation:
    path: terraform-emergency-input
    owner: security-oncall
    expiryRequired: true
  driftOwner: payments-network
```

## 4. Tool selection podľa lifecycle-u

Terraform je prirodzený, keď potrebujeme:

```text
stable remote object identity
persistent binding
create/update/replacement/destruction plan
resource dependency graph
import/move/drift lifecycle
```

Ansible je prirodzený, keď potrebujeme:

```text
resolved target fleet
host/device current-state reads
ordered conditions/loops/handlers
batch rollout
loaded-runtime convergence
```

To, že cloud resource možno vytvoriť Ansible module-om alebo file zapísať Terraform provisionerom, ešte neznamená, že výsledný ownership a recovery model je dobrý.

## 5. Terraform-owned platform example

```hcl
resource "aws_instance" "payments" {
  for_each = var.instances

  ami                    = var.image_id
  instance_type          = each.value.instance_type
  subnet_id              = var.subnet_ids[each.value.az]
  vpc_security_group_ids = [aws_security_group.payments.id]

  tags = {
    Name        = each.key
    Environment = "prod-eu"
    Role        = "payments_app"
  }
}
```

Terraform owns instance identity, image and network bindings. It does not need to install application packages through `remote-exec`.

## 6. Ansible-owned host configuration example

```yaml
- name: Configure Payments runtime
  hosts: payments_app:&production:!maintenance
  serial: 2
  become: true

  roles:
    - role: atlas.platform.payments_runtime
      atlas_payments_release: payments-v43
      atlas_payments_config_version: C44
      atlas_payments_secret_epoch: 2026-07-31-02
```

Ansible owns package/config/service convergence. It does not create a second cloud lifecycle for VM identity or security groups.

## 7. Narrow provisioning-to-configuration contract

Ansible nemá čítať celý production Terraform state ani interné addresses. Terraform publikuje versionovaný host contract:

```json
{
  "schemaVersion": "atlas.host-contract/v1",
  "producer": {
    "terraformSourceRevision": "91ac447",
    "stateLineage": "37fd",
    "stateSerial": 419,
    "contractGeneration": "HC-313"
  },
  "environment": "prod-eu",
  "hosts": [
    {
      "inventoryHostname": "payments-app-a1",
      "instanceId": "i-0abc123",
      "managementAddress": "10.40.11.21",
      "availabilityZone": "eu-central-1a",
      "role": "payments_app",
      "imageId": "ami-atlas-313",
      "readiness": "ready"
    }
  ]
}
```

Contract obsahuje iba fields potrebné consumerovi. Nepublikuje backend secrets, provider internals ani resource address layout.

## 8. Contract schema a validation

Consumer validuje:

```text
schema version
producer subject
expected environment
unique inventoryHostname/instanceId
required fields
readiness generation
host count/AZ distribution
expiry/freshness
```

Príklad jednoduchého validation shellu:

```bash
jq -e '
  .schemaVersion == "atlas.host-contract/v1"
  and .environment == "prod-eu"
  and (.hosts | length == 12)
  and ([.hosts[].instanceId] | unique | length == 12)
  and ([.hosts[].readiness] | all(. == "ready"))
' host-contract.json
```

Preukazuje listed JSON invariants. Nepreukazuje SSH connectivity, host-key identity ani runtime package state.

## 9. Inventory generation z contractu

```python
#!/usr/bin/env python3
import json
from pathlib import Path

contract = json.loads(Path("host-contract.json").read_text())

inventory = {
    "all": {
        "children": {
            "production": {
                "children": {
                    "payments_app": {"hosts": {}}
                }
            }
        }
    }
}

hosts = inventory["all"]["children"]["production"]["children"]["payments_app"]["hosts"]
for host in contract["hosts"]:
    if host["readiness"] != "ready":
        continue
    hosts[host["inventoryHostname"]] = {
        "ansible_host": host["managementAddress"],
        "atlas_instance_id": host["instanceId"],
        "atlas_image_id": host["imageId"],
        "atlas_availability_zone": host["availabilityZone"],
    }

print(json.dumps(inventory))
```

Generator je executable dependency a potrebuje versioning/tests. Output sa porovná s expected manifestom pred Ansible runom.

## 10. Readiness ako samostatný state

Terraform apply success môže znamenať, že VM exists. Neznamená:

- cloud-init complete;
- host certificate ready;
- management route functional;
- SSH identity stable;
- required Python/runtime available;
- host safe for configuration.

Readiness chain:

```text
resource created
→ boot/cloud-init complete
→ management identity published
→ route/firewall verified
→ host-key/certificate verified
→ bootstrap capability probe
→ contract status ready
```

Fixed sleep nie je readiness proof. Použi bounded condition-based observation a preserve last failure evidence.

## 11. Bootstrap boundary

Minimálny bootstrap môže vytvoriť:

- trusted management identity/channel;
- CA/host certificate;
- minimum Python/runtime;
- inventory registration;
- base security pre first connection.

Application configuration nemá zostať v one-shot user data bez re-run a observation modelu.

Terraform provisioner je podobne slabý default:

```hcl
provisioner "remote-exec" {
  inline = ["/opt/bootstrap.sh"]
}
```

Side effect nemá samostatný Terraform resource binding a retry/recovery sa viažu na parent resource lifecycle. Provisioner je výnimočný bridge, nie replacement configuration managementu.

## 12. Plan verzus check mode

Terraform saved plan:

```text
configuration + inputs + state serial + refresh + target
→ exact proposed resource actions
```

Ansible check mode:

```text
resolved task path + module-specific support
→ best-effort predicted per-host change
```

Nie sú ekvivalenty. Check mode nemusí podporovať task alebo downstream registered flow; Terraform plan nepreukazuje application runtime behavior. Hybrid approval potrebuje obe vrstvy a reálnu canary evidence. citeturn329472search0

## 13. Combined pipeline

```text
1. build/test immutable machine image
2. Terraform fmt/validate/test
3. saved plan + plan JSON + policy
4. approval exact plan digest
5. apply exact plan
6. verify state serial, remote resources a readiness
7. publish signed/versioned host contract
8. validate contract and resolved inventory
9. Ansible syntax/contract/check evidence
10. canary first converge
11. loaded-runtime/business verification
12. fleet rollout
13. full business transaction
14. fresh Terraform no-op plan
15. second Ansible converge
16. combined evidence closure
```

## 14. Combined evidence manifest

```yaml
combinedReleaseEvidence:
  release: payments-v43
  terraform:
    planDigest: sha256:291a...
    appliedStateSerial: 419
    secondPlan: no-op
  hostContract:
    generation: HC-313
    hosts: 12
  ansible:
    runId: gitlab-98231
    convergedHosts: 12
    secondRunChangedTasks: 0
  runtime:
    healthyHosts: 12
    businessTransaction: pass
```

Každá field má vlastný producer a proof boundary.

## 15. Failure boundaries

### Terraform boundary

Partial remote mutation, unknown API outcome, state-write failure alebo resource exists-but-not-ready.

### Contract boundary

Stale host, wrong address/environment, schema mismatch, incorrect readiness, missing host.

### Ansible boundary

Partial fleet, file without handler, package/config mismatch, secret epoch mismatch, external API duplicate.

### Business boundary

Infrastructure a hosts sú healthy, ale payment transaction alebo data correctness zlyhá.

Recovery najprv identifikuje boundary; nesprávny VM replacement nemusí opraviť inventory alebo Ansible variable failure.

## 16. Worked incident: security-group oscillation

Terraform:

```hcl
resource "aws_security_group_rule" "lb_to_app" {
  type                     = "ingress"
  from_port                = 8443
  to_port                  = 8443
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.lb.id
  security_group_id        = aws_security_group.app.id
}
```

Ansible incident task pridáva admin CIDR priamo cez cloud API.

```text
Ansible adds rule
→ Terraform removes drift
→ Ansible re-adds rule
```

Riešenie:

```text
Terraform remains owner
→ emergency access expressed as versioned/scoped Terraform input
→ owner, incident, expiry
→ reviewed apply
→ incident close removes input
```

alebo explicitný ownership transfer. Nie tichý second writer.

## 17. Worked incident: consumer čítal interný state layout

Inventory parser očakával:

```text
module.compute.aws_instance.app[0]
```

Terraform migroval na:

```text
module.compute.aws_instance.app["az-a-01"]
```

`moved` block správne zachoval remote VM, ale undocumented parser vrátil empty inventory a Ansible skončil no-host success.

Narrow contract so stable instance IDs by refactor prežil.

## 18. Worked incident: inventory publikované pred readiness

VMs vznikli a contract okamžite obsahoval IPs. Cloud-init ešte menil SSH host keys.

```text
resource exists
→ readiness falsely ready
→ Ansible host-key mismatch/unreachable
→ operator navrhne VM replacement
```

Recovery najprv overí boot/identity/network. Resource replacement je až výsledok potvrdenej infrastructure lifecycle chyby.

## 19. Worked incident: image a runtime package dual ownership

Image build obsahuje package 3.13.0. Runtime role používa `state: latest` a aktualizuje na 3.13.1.

```text
immutable image subject says 3.13.0
→ Ansible mutates package to 3.13.1
→ fleet no longer matches image identity
```

Vyber jeden model:

- package vlastní immutable image a runtime Ansible ho iba verifikuje;
- alebo package vlastní Ansible s explicitnou version a image je bootstrap base.

Implicitný hybrid ničí reproducibility.

## 20. Ownership transfer lifecycle

Keď sa attribute presúva z Terraformu do Ansible alebo opačne:

```text
inventory current owner a consumers
→ define target owner a desired-state source
→ freeze conflicting writes
→ migrate state/binding/configuration
→ revoke old writer permission
→ fresh plan/converge
→ forbidden old-writer test
→ monitoring a recovery owner update
```

Odstránenie Terraform resource/attribute bez explicitného handoffu môže spôsobiť destroy alebo unmanaged object. Pridanie Ansible tasku bez odobratia Terraform ownershipu vytvorí oscillation.

## 21. Competing hypotheses pri Terraform green / Ansible unreachable

```text
H1: resource exists, bootstrap incomplete
H2: contract readiness je false-positive
H3: wrong management address/environment
H4: inventory cache stale
H5: route/firewall blocks controller
H6: host key/certificate changed
H7: credential/become mismatch
H8: wrong image/bootstrap capability
H9: stale destroyed host identity
H10: controller network issue
```

Dôkazy:

- remote VM lifecycle/bootstrap logs H1/H2/H8;
- contract fields/generation H2/H3/H9;
- inventory resolution/cache H4;
- flow/connectivity H5/H10;
- host identity H6;
- auth logs H7.

## 22. Evidence-preserving containment a recovery

```text
pause contract publication/Ansible rollout
→ preserve Terraform plan/state/remote evidence
→ preserve contract generation/inventory resolution
→ keep unready hosts out of traffic
→ classify infrastructure vs readiness vs inventory vs credential failure
→ repair authoritative boundary
→ republish new contract generation
→ canary Ansible converge
→ runtime/business verify
→ Terraform no-op + Ansible second run
```

## 23. Acceptance a forbidden paths

```text
každý mutable attribute má one writer
+ old writer permissions sú revoked po transfer
+ Terraform apply publishes only ready verified hosts
+ contract schema/generation is validated
+ Ansible target manifest equals contract
+ no internal state-address coupling
+ image/package ownership is explicit
+ emergency rule uses one authority path
+ Terraform second plan is no-op
+ Ansible second run has no unintended changes
+ business transaction passes
```

Forbidden tests:

- Ansible direct mutation Terraform-owned SG rule;
- contract with `readiness != ready`;
- empty inventory from internal state refactor;
- runtime package `latest` against image-owned package;
- old writer still authorized after ownership transfer.

## 24. Anti-patterny

### „Terraform robí infra, Ansible config — tým je boundary hotová“

Treba presný object/attribute ownership.

### „Ansible môže dočasne opraviť cloud resource“

Bez emergency ownership contractu vytvorí druhého writera.

### „Ansible môže čítať celý Terraform state“

Vytvára sensitive a interný-layout coupling.

### „Terraform apply success znamená host ready“

Resource existence, bootstrap a management readiness sú odlišné states.

### „Provisioner je jednoduchší než Ansible“

Side effect nemá samostatný lifecycle/binding/recovery model.

## 25. Kontrolné otázky

1. Aký je dominantný state model Terraformu a Ansible?
2. Prečo ownership treba definovať per object/attribute?
3. Čo má obsahovať provisioning-to-configuration contract?
4. Prečo Ansible nemá čítať interné Terraform state addresses?
5. Aký rozdiel je medzi resource existence a host readiness?
6. Kedy je Terraform provisioner primeraný?
7. Prečo plan a check mode nie sú ekvivalenty?
8. Ako dva idempotentné tools vytvoria oscillation?
9. Ako sa rieši emergency mutation Terraform-owned resource-u?
10. Čo musí obsahovať ownership transfer?
11. Aké evidence uzatvárajú combined release?
12. Ako sa testuje forbidden second-writer a stale-contract path?

## Glossary impact

Relevantné pojmy: Terraform–Ansible boundary, authoritative writer, attribute ownership, host contract, readiness generation, provisioning-to-configuration handoff, bootstrap, provisioner, combined evidence, dual writer, oscillation, ownership transfer, contract schema a combined convergence.

## Primárne zdroje

- [Terraform language](https://developer.hashicorp.com/terraform/language)
- [Terraform provisioners](https://developer.hashicorp.com/terraform/language/resources/provisioners/syntax)
- [Ansible architecture](https://docs.ansible.com/projects/ansible/latest/dev_guide/overview_architecture.html)
- [How to build your inventory](https://docs.ansible.com/projects/ansible/latest/inventory_guide/intro_inventory.html)
- [Check mode and diff mode](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_checkmode.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Ansible idempotencia](ansible-idempotency.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Containers vs. virtual machines →](../08-container-fundamentals-and-docker/containers-vs-virtual-machines.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
