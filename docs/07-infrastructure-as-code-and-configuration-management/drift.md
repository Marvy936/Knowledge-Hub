# Drift

Terraform drift nie je synonymum pre „plan ukazuje diff“. Drift je rozdiel medzi deklarovaným desired state-om, Terraformom evidovaným binding/observation modelom a remote stavom, ktorý provider práve pozoruje. Rovnaký diff môže znamenať neautorizovanú ClickOps zmenu, legitímny incidentný override, nový external controller, provider normalization, stratený state binding, mutable dependency alebo jednoducho plán spustený proti nesprávnemu backendu. Automatické `apply` bez klasifikácie preto môže odstrániť bezpečnostné containment pravidlo alebo naopak adoptovať útočníkovu zmenu.

Kapitola otvára incident `IAC-PAY-77`. Počas platobného incidentu security engineer cez break-glass pridá dočasnú WAF deny rule a diagnostický endpoint s ownerom a dvojhodinovou expiráciou. Scheduled Terraform job však pozná iba repository desired state. Rozdiel klasifikuje ako drift a automaticky ho revertuje. O desať minút neskôr sa škodlivý traffic vráti a diagnostika zmizne. Problém nebol v tom, že Terraform reconcilioval; problémom bol chýbajúci authority a exception lifecycle.

## 1. Dominantný observation-to-reconciliation lifecycle

Drift lifecycle začína subject verification, pretože diff nad nesprávnym backendom alebo targetom nie je evidence o production. Authoritative configuration a attribute ownership sa porovnajú s presným state lineage/serialom a current provider observation.

```text
authoritative configuration a ownership contract
+ exact backend/state/provider target
+ current remote observation
→ subject-verified difference
→ origin, intent, risk a writer classification
→ revert | adopt | transfer ownership | remove management | recover state
→ fresh reviewed plan
→ bounded transition
→ state, remote, runtime a business verification
→ second plan a exception closure
```

Detector musí pomenovať resource address/remote ID, writer, authorization/expiry a authoritative layer pre každý changed attribute. Až táto klasifikácia rozhodne, či sa rozdiel revertuje, adoptuje, deleguje alebo rieši ako lost binding. Automatický apply bez nej môže odstrániť incident containment alebo legitimizovať attacker mutation.

## 2. Exact drift detection subject

Scheduled run musí publikovať subject napríklad takto:

```yaml
driftDetectionSubject:
  repository: atlas/platform-live
  sourceRevision: 91ac447
  rootModule: environments/prod-eu/network
  terraformVersion: 1.x-pinned
  providerLockDigest: sha256:4d5f...
  backend:
    key: payments/network/prod-eu.tfstate
    lineage: 37fd...
    startingSerial: 418
  target:
    account: "771100001234"
    region: eu-central-1
  identity: gitlab-iac-prod-drift-reader
  refreshTime: 2026-07-31T04:00:00Z
  expectedCriticalAddresses:
    - aws_wafv2_web_acl.payments
    - aws_security_group.api
    - aws_lb.api
```

Bez subjectu môže `0 changes` znamenať iba to, že job úspešne preskenoval stage workspace alebo prázdny alternate backend. Expected critical-address inventory je dôležitý, pretože plan nad nesprávnym state-om môže byť technicky úspešný a zároveň úplne nerelevantný.

## 3. Desired, known a actual state

```text
desired
= configuration + resolved inputs + ownership rules

known
= state bindings a posledné známe attributes

actual
= provider/API observation remote objektov
```

Príklad incidentnej rule:

```text
configuration:
  diagnostics rule absent

state serial 418:
  diagnostics rule absent

remote API:
  diagnostics rule present
  tag Incident=INC-8421
  tag ExpiresAt=2026-07-31T06:00:00Z
```

Tento rozdiel nehovorí sám, či je remote stav chybný. Potrebujeme writer audit a intent metadata.

## 4. Refresh nie je remediation

Bežný plan načíta configuration a state, providerom refreshne bound objects a vytvorí change graph. Refresh-only mode izoluje otázku, ako by sa zmenilo Terraform knowledge pri prijatí remote observation:

```bash
terraform plan -refresh-only -out=refresh.tfplan
terraform show -json refresh.tfplan > refresh.json
```

Refresh-only plan remote objekty nemení. `terraform apply -refresh-only` už zapíše nový state snapshot, takže mení evidence foundation pre budúce plans.

```text
refresh-only plan
→ observation a review
→ ownership/adoption decision
→ refresh-only apply iba pri schválenej knowledge transition
```

Refresh-only apply neaktualizuje desired configuration. Ak remote autoscaling minimum je `10`, state po refresh-only môže poznať `10`, ale configuration stále požaduje `6`; ďalší normálny plan navrhne návrat na `6`.

## 5. Drift taxonomy podľa mechanizmu

Taxonómia oddeľuje podobný plan diff podľa príčiny a správnej recovery. Remote drift, configuration divergence, binding drift, provider interpretation, dependency drift, delegated mutation a unmanaged asset majú odlišného ownera aj bezpečný next step; spoločný symbol `~` alebo `+` ich nerozlišuje.

### Remote drift

Bound remote objekt zmenil writer mimo autoritatívneho Terraform workflowu.

```text
configuration port 443
state port 443
remote port 8443
```

Najprv identifikuj writera a intent.

### Configuration divergence

Dve branches alebo repositories deklarujú odlišné desired states. Remote objekt môže byť v súlade s jedným source-om a driftovať voči druhému.

### State alebo binding drift

State address, provider association alebo remote ID nezodpovedajú current ownershipu. Príčina môže byť starý restore, lost state write, neúplný move alebo wrong backend.

### Provider interpretation drift

Nová provider verzia alebo API normalization interpretuje rovnaký remote object odlišne a vytvára perpetual diff alebo replacement.

### Dependency drift

Mutable data source, image tag, policy package alebo external catalog zmení resolved input bez source diffu.

### Delegovaná zmena

Iný controller legitímne vlastní konkrétny attribute, napríklad autoscaler `desired_count`. Nie je to chyba, ak ownership a guardrails sú explicitné.

### Unmanaged infrastructure

Remote object bez bindingu nie je automaticky drift daného state-u. Potrebuje asset inventory a prípadný import/adoption lifecycle.

## 6. Scheduled detection workflow

Praktický job:

```bash
set -euo pipefail

terraform init -input=false -backend-config=backend-prod-eu.hcl
terraform state pull > state-before.json
jq '{lineage,serial}' state-before.json

set +e
terraform plan \
  -detailed-exitcode \
  -out=drift.tfplan
status=$?
set -e

case "$status" in
  0) verdict="NO_CHANGES" ;;
  1) verdict="INVALID_OR_TOOL_FAILURE" ;;
  2) verdict="CHANGES_DETECTED" ;;
  *) verdict="UNEXPECTED_EXIT" ;;
esac

printf 'drift_verdict=%s\n' "$verdict"
terraform show -json drift.tfplan > drift.json
```

`-detailed-exitcode` rozlišuje no-change, error a changes. Exit code `2` nepreukazuje harmful drift. Exit code `0` nepreukazuje správny subject ani scanner completeness. Job musí pred verdictom overiť lineage, target identity a expected address inventory.

## 7. Plan JSON ako classification evidence

```bash
jq -r '
  .resource_changes[]
  | select(.change.actions != ["no-op"])
  | {
      address,
      actions: .change.actions,
      before: .change.before,
      after: .change.after,
      replace_paths: .change.replace_paths
    }
' drift.json
```

Plan JSON poskytuje machine-readable before/after/actions pre exact saved plan. Môže obsahovať sensitive values a potrebuje restricted access. Neobsahuje automaticky identity external writera ani business intent. Tie pochádzajú z cloud audit logu, incident systému a ownership registry.

## 8. Worked incident: automatic revert odstránil containment

Incidentný workflow:

```text
security engineer pridá deny rule
→ cloud audit zaznamená break-glass identity
→ rule obsahuje ticket/owner/expiry
→ incident sa stabilizuje
```

Scheduled Terraform workflow:

```text
remote observation != configuration
→ diff klasifikovaný iba ako drift
→ automatic apply odstráni rule
→ malicious traffic sa vráti
```

Root cause bol chýbajúci exception channel medzi incident controllerom a Terraform reconciliation.

Správny lifecycle:

```text
strongly authenticated break-glass mutation
→ incident record, scope, owner, expiry
→ pause conflicting auto-apply
→ drift detector označí KNOWN_AUTHORIZED_EXCEPTION
→ incident stabilization
→ permanent adoption alebo reviewed revert
→ exception closure a credential revocation
```

## 9. Break-glass override contract

Dočasná mutation potrebuje minimálne:

```yaml
emergencyOverride:
  incident: INC-8421
  resourceId: waf-payments-prod
  attribute: denyRules[malicious-cidr]
  writer: security-break-glass
  reason: active-exploitation-containment
  createdAt: 2026-07-31T04:10:00Z
  expiresAt: 2026-07-31T06:10:00Z
  reconciliationMode: paused
  owner: security-oncall
```

Metadata v tagoch môže pomôcť, ale nie je jedinou authority. Útočník alebo neautorizovaný writer môže tags sfalšovať. Audit identity a incident authorization sú rozhodujúce.

## 10. Shared ownership a `ignore_changes`

```hcl
resource "aws_autoscaling_group" "api" {
  min_size         = 2
  max_size         = 20
  desired_capacity = 6

  lifecycle {
    ignore_changes = [desired_capacity]
  }
}
```

Legitímny contract:

```text
Terraform vlastní ASG shape a bounds
→ autoscaler vlastní desired_capacity
→ metrics/policy určujú effective value
→ monitoring overuje min/max a health
```

`ignore_changes` sám nevytvorí autoscaler, monitoring ani conflict resolution. Bez external guardrail-u iba odstráni visibility z Terraform planu.

## 11. False clean nad nesprávnym workspace-om

Security tím vie, že production firewall bol otvorený, ale dashboard ukazuje `NO_CHANGES`.

Observed subject:

```text
workspace stage
account stage
state resources 38
expected production resources 117
```

Pipeline technicky prešla. Dôkaz bol pre nesprávny subject.

Pre-run assertions:

```bash
workspace="$(terraform workspace show)"
account="$(aws sts get-caller-identity --query Account --output text)"
resource_count="$(terraform state list | wc -l)"

[[ "$workspace" == "default" ]]
[[ "$account" == "771100001234" ]]
[[ "$resource_count" -ge 100 ]]
terraform state list | grep -Fx 'aws_wafv2_web_acl.payments'
```

Resource-count threshold je pomocný sanity check, nie úplný inventory proof. Kritické addresses a lineage sú silnejšie.

## 12. Provider noise a signal integrity

Perpetual diff môže vzniknúť zo server-side defaultov, unordered fields modelovaných ako list, transient timestamps, eventual consistency, provider normalization, mutable external data alebo unstable generated values. Každý mechanizmus má inú opravu: canonical configuration, správny set/list model, bounded read-after-write retry, provider fix/upgrade alebo immutable dependency pinning.

Noise nie je iba ergonomický problém. Keď reviewer rutinne ignoruje stovky známych diffs, znižuje sa pravdepodobnosť odhalenia novej IAM alebo network expansion. Suppression preto potrebuje ownera a independent guardrail; široké `ignore_changes` iba odstraňuje evidence.

Signal integrity sa overí tak, že rovnaký successor state vytvorí druhý no-op plan a zároveň external writer test stále vyvolá alert. Cieľom nie je nulový počet riadkov za každú cenu, ale vysoká diskriminačná hodnota každého zostávajúceho diffu.

## 13. Reconciliation decision matrix

### Revert

Configuration je stále authoritative. Reviewed apply vráti remote value.

### Adopt

Remote intent je správny. Najprv sa aktualizuje configuration, potom sa vytvorí fresh plan. Samotný refresh-only apply desired state nezmení.

### Transfer ownership

Iný controller preberá attribute alebo object. Configuration, lifecycle rules, monitoring, permissions a support contract sa zmenia spolu.

### Remove management

Binding sa odstráni iba pri explicitnom ownership transfere alebo retirement-e. Resource block nesmie zostať a následne vytvoriť duplicate object.

### Recover state

Rozdiel vznikol stratou bindingu, restore alebo wrong backendom. Najprv sa obnoví identity model, nie remote object.

### Compensate alebo restore

Pri data-bearing alebo external-side-effect zmene nemusí obyčajný Terraform revert obnoviť business state.

## 14. Harmful auto-remediation gate

Automatický apply je primeraný iba pre úzko definovanú, reversible a subject-verified class. Napríklad canonical tag correction môže byť automatizovateľná, ak:

```text
resource identity je exact
+ writer intent nie je emergency exception
+ change nie je IAM/network/data/destructive
+ saved plan je fresh
+ rollback je známy
+ runtime verifier existuje
```

Unknown writer, unknown outcome, replacement, privilege expansion, data change alebo active incident musí smerovať na manual owner decision.

## 15. Causal troubleshooting: rovnaký diff po každom apply

Symptom: listener port sa po každom úspešnom apply objaví opäť v plane.

Hypotézy:

```text
H1: provider normalizuje hodnotu inak
H2: druhý writer ju po apply prepíše
H3: apply a plan používajú iný target
H4: state write zlyhal alebo bol prepísaný
H5: mutable data source mení input
H6: eventual consistency vracia stale read
```

Diskriminačné evidence:

- plan JSON before/after a replace paths;
- provider debug/request IDs bez secrets;
- cloud audit writer identity a timestamp;
- state serial pred/po apply;
- remote value bezprostredne a po propagation intervale;
- resolved data-source ID/digest;
- account/region v oboch jobs.

Containment zastaví auto-apply. `ignore_changes` sa nepridá, kým nie je známy owner a security dopad.

## 16. Authoritative recovery incidentu `IAC-PAY-77`

Recovery musí najprv obnoviť incidentnú authority a až potom normálnu Terraform reconciliation. Scheduled auto-apply zostáva pozastavený, kým sa neuzavrie, či dočasná WAF rule bude adoptovaná alebo reviewed revertovaná; inak by rovnaký mechanismus znova odstránil containment.

Atlas recovery:

1. pozastaví scheduled auto-apply pre affected state;
2. zachová drift plan, state snapshot, WAF audit events a incident metadata;
3. znovu nasadí deny rule cez incident-authorized path;
4. overí traffic containment a diagnostiku;
5. rozhodne, či rule patrí do permanent configuration alebo sa po incidente odstráni;
6. aktualizuje repository alebo vykoná reviewed revert;
7. uzavrie exception a revokuje break-glass session;
8. spustí fresh plan a druhý no-op plan;
9. otestuje, že neznámy manual change nie je automaticky adoptovaný ani revertovaný bez klasifikácie.

## 17. Acceptance a forbidden paths

Drift acceptance testuje tri triedy rozdielu: harmful unauthorized mutation, authorized expiring override a provider noise. Systém ich musí rozlíšiť a nesmie automaticky adoptovať ani revertovať unknown writer. Po closure fresh aj druhý plan potvrdia successor state bez potlačenia budúcej detekcie.

Drift blok je prijatý, keď:

```text
detection subject obsahuje backend/lineage/target
+ expected critical addresses sú prítomné
+ exit 0/1/2 sa správne klasifikuje
+ plan JSON a audit writer sú korelované
+ emergency override má owner/expiry
+ unknown drift nevyvolá automatic apply
+ authorized exception sa nerevertuje pred expiry
+ expired exception sa uzavrie reviewed reconciliation
+ second plan je no-op
+ runtime/business journey prejde
```

Forbidden fixtures:

- wrong workspace s `0 changes` musí zlyhať subject gate;
- policy engine alebo provider read error nesmie byť clean;
- unknown manual IAM expansion nesmie byť auto-adoptovaná;
- active incident rule nesmie byť auto-revertovaná.

## 18. Anti-patterny

### „Každý drift treba okamžite revertovať“

Najprv treba poznať writer intent a ownership. Incidentná mutation môže byť správny temporary desired state.

### „Refresh-only odstránil drift“

Aktualizoval known state; desired configuration ostala rovnaká.

### „Exit code 0 znamená čistú produkciu“

Iba ak subject, refresh a inventory boli validné.

### „`ignore_changes` vyrieši noise“

Môže skryť security-significant ownership konflikt.

### „Unmanaged object je Terraform drift“

Bez bindingu patrí do asset-discovery/adoption procesu.

## 19. Kontrolné otázky

1. Prečo drift diff nie je remediation verdict?
2. Čo musí obsahovať drift detection subject?
3. Aký rozdiel je medzi desired, known a actual state?
4. Čo robí refresh-only plan a apply?
5. Ako sa remote drift líši od state driftu a dependency driftu?
6. Prečo authorized break-glass change nesmie byť automaticky revertovaný?
7. Čo `ignore_changes` deleguje a čo nevytvára?
8. Prečo `detailed-exitcode=0` nemusí byť clean proof?
9. Ako sa odlíši provider normalization od druhého writera?
10. Kedy je auto-remediation primeraná?
11. Ako sa testuje forbidden wrong-workspace a unknown-drift path?
12. Prečo acceptance obsahuje second plan a business verification?

## Glossary impact

Relevantné pojmy: Terraform drift, drift detection subject, remote drift, configuration divergence, state drift, provider interpretation drift, dependency drift, delegated ownership, refresh-only, break-glass override, auto-remediation, adoption, reconciliation, perpetual diff a second no-op plan.

## Primárne zdroje

- [Terraform plan](https://developer.hashicorp.com/terraform/cli/commands/plan)
- [Refresh-only mode](https://developer.hashicorp.com/terraform/tutorials/state/refresh)
- [Terraform show JSON](https://developer.hashicorp.com/terraform/cli/commands/show)
- [Manage resource drift](https://developer.hashicorp.com/terraform/tutorials/state/resource-drift)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Lifecycle, import a moved blocks](lifecycle-import-moved-blocks.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Terraform testing a policy →](terraform-testing-and-policy.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
