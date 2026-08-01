# Terraform testing a policy

Terraform configuration je executable specification, ktorá môže vytvoriť alebo odstrániť identity, meniť sieťové hranice, pristupovať k dátam a ovplyvniť produkčnú dostupnosť. Dôveryhodný quality gate preto nie je zoznam príkazov ani zelená pipeline. Je to evidence lifecycle, ktorý definuje presný change subject, očakávané dôkazy, vrstvy oracles, policy semantics, cleanup verdict a väzbu medzi schváleným saved planom a skutočne aplikovaným a runtime overeným výsledkom.

Kapitola uzatvára incident `IAC-PAY-77`. Atlas Payments vydáva module `payments-database 4.3.0`. Mock tests sú zelené, ale real-provider apply zlyhá na organization policy. Upgrade test neexistuje, takže chýbajúci `moved` block zostane neodhalený. Policy engine nedokáže načítať bundle, wrapper vytvorí prázdny report a gate ho interpretuje ako „0 violations“. Iný apply test síce prejde assertions, ale cleanup zanechá verejný bucket. Každý lokálny status vyzerá prijateľne, no complete evidence verdict musí byť `INCOMPLETE_OR_INVALID`, nie pass.

## 1. Dominantný risk-to-runtime evidence lifecycle

Nasledujúci model opisuje prechody jedného Terraform configuration, state a remote-resource subject, nie iba poradie krokov. Failure môže nastať v ktoromkoľvek bode reťazca resolved inputs a graph cez provider API mutation až po state binding a zanechať partial alebo unknown outcome. Každý transition preto potrebuje vlastný read-back a closure tvorí exact provider target, remote/state reconciliation a druhý no-op plan.

```text
exact change subject a risk class
→ expected evidence inventory
→ format, validate a static evidence
→ module contract a native plan tests
→ upgrade tests nad existujúcim state-om
→ real-provider apply/integration evidence
→ cleanup verdict
→ immutable production saved plan
→ machine-readable policy verdict a exception check
→ apply presne schváleného planu
→ state, remote, runtime a business verification
→ second no-op plan, drift registration a evidence closure
```

Každá vrstva odpovedá na inú otázku. Rýchlejší test nesmie predstierať dôkaz, ktorý môže poskytnúť iba provider API alebo runtime.

## 2. Exact Terraform evidence subject

Táto podsekcia definuje presný Terraform configuration, state a remote-resource subject. Názov alebo locator nestačí: subject musí niesť generation, authority a target identity potrebné na koreláciu reťazca resolved inputs a graph cez provider API mutation až po state binding. Až exact provider target, remote/state reconciliation a druhý no-op plan ukáže, že ďalší command alebo YAML patrí správnemu objektu.

```yaml
evidenceSubject:
  repository: atlas/terraform-modules
  sourceRevision: 8c91a42
  module:
    name: payments-database
    version: 4.3.0
    packageDigest: sha256:81bd...
  terraformVersion: 1.x-pinned
  providerLockDigest: sha256:4d5f...
  policyBundle:
    revision: 7a21c4e
    digest: sha256:9c11...
  fixtures:
    cleanInstall: prod-like-v3
    upgradeFrom:
      - 4.2.4
      - 4.1.9
  production:
    backendKey: payments/database/prod-eu.tfstate
    lineage: 17ef...
    startingSerial: 551
    account: "771100001234"
    region: eu-central-1
  savedPlanDigest: sha256:291a...
```

Zelený test nad inou module version, provider, fixture alebo target nie je automaticky evidence pre production subject. Každý report musí uviesť producer, tool/rules version, subject a validity status.

## 3. Expected evidence inventory

Risk class definuje, ktoré artifacts musia existovať:

```yaml
expectedEvidence:
  - id: fmt
    required: true
  - id: validate
    required: true
  - id: static-security
    required: true
  - id: contract-plan-tests
    required: true
  - id: upgrade-4.2.4-to-4.3.0
    required: true
  - id: real-provider-apply
    required: true
  - id: runtime-transaction
    required: true
  - id: cleanup
    required: true
  - id: production-plan-json
    required: true
  - id: policy-verdict
    required: true
  - id: approval-or-exception
    required: true
```

Ak `real-provider-apply` job nebol vytvorený pre chybu v pipeline `rules`, výsledok nie je „0 failures“. Je to missing required evidence.

Verdict classes:

```text
PASS
VIOLATION
TOOL_OR_INFRA_FAILURE
MISSING_OR_SKIPPED
STALE_SUBJECT
INVALID_REPORT
CLEANUP_INCOMPLETE
EXTERNAL_DEPENDENCY_OUTAGE
SUPERSEDED
```

## 4. Najlacnejšie vrstvy

Najlacnejšie checks poskytujú rýchlu spätnú väzbu, ale každá vrstva má úzky oracle. Formatting overuje canonical presentation podľa pinned Terraform CLI. `terraform validate` overuje configuration consistency voči dostupným module a provider schemas a JSON output umožní machine-readable verdict.

Validation však nekontaktuje production authority: nepreukazuje credentials, organization policy, quotas, remote API behavior, apply-time unknowns, eventual consistency, runtime connectivity, data migration ani cleanup. Tieto otázky patria plan, apply a runtime vrstvám.

Static analyzer môže nájsť public exposure, unpinned dependency alebo secret pattern, ale report je platný iba so scanner version/rulesetom, complete scanned inventory, parse/unsupported statusom a findings/baseline subjectom. Nula findings bez coverage je `MISSING_OR_INVALID_EVIDENCE`, nie pass.

Portfólio preto postupuje od lacných parser/schema checks cez plan assertions a policy k isolated apply-u a independent runtime oracle-u. Vyššia vrstva nenahrádza nižšiu; odpovedá na inú otázku.

### Formatting

Táto podsekcia vysvetľuje konkrétnu časť Terraform configuration, state a remote-resource subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inputs a graph cez provider API mutation až po state binding; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po exact provider target, remote/state reconciliation a druhý no-op plan.

```bash
terraform fmt -check -recursive
```

Preukazuje canonical formatting podľa použitej Terraform CLI. Nepreukazuje syntax completeness, provider compatibility, security ani runtime behavior.

### Validation

Táto podsekcia vysvetľuje konkrétnu časť Terraform configuration, state a remote-resource subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inputs a graph cez provider API mutation až po state binding; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po exact provider target, remote/state reconciliation a druhý no-op plan.

```bash
terraform init -backend=false -input=false
terraform validate -json > validate.json
```

Validation kontroluje configuration consistency voči dostupným module/provider schemas. JSON output umožní machine-readable spracovanie.

Transition eviduje credentials a authorization, cloud quotas a organization policy, remote API behavior, apply-time unknown values, eventual consistency a runtime connectivity.

Dopĺňa ho data migration a cleanup.

### Static analysis

Scanner môže nájsť public exposure, unpinned source, deprecated field alebo secret pattern. Dôveryhodný report potrebuje:

```text
analyzer identity/version
ruleset a policy revision
scanned file/resource inventory
parse errors a unsupported constructs
findings
baseline/exception subject
```

Successful scanner process nie je automaticky validný report. „Nula findings“ bez coverage a parse validity je neúplný dôkaz.

## 5. Invarianty priamo v Terraform contracte

Táto podsekcia vysvetľuje konkrétnu časť Terraform configuration, state a remote-resource subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inputs a graph cez provider API mutation až po state binding; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po exact provider target, remote/state reconciliation a druhý no-op plan.

```hcl
variable "database" {
  type = object({
    environment = string
    encrypted   = bool
    multi_az    = bool
  })

  validation {
    condition = (
      var.database.environment != "prod-eu" ||
      (var.database.encrypted && var.database.multi_az)
    )
    error_message = "Production database must be encrypted and multi-AZ."
  }
}
```

Resource preconditions/postconditions:

```hcl
resource "example_database" "payments" {
  replica_count = var.replica_count

  lifecycle {
    precondition {
      condition     = var.replica_count >= 2
      error_message = "Production requires at least two replicas."
    }

    postcondition {
      condition     = self.encrypted
      error_message = "Provider returned an unencrypted database."
    }
  }
}
```

Precondition overuje known assumption pred operation. Postcondition overuje provider-visible result. Ani jedna nepreukazuje, že Payments API vykoná transakciu alebo že restore funguje.

## 6. Native Terraform tests

Každá testovacia alebo policy vrstva má vlastný subject a oracle. Parser/schema pass nepreukazuje remote authorization, report existence nepreukazuje processing a isolated apply nepreukazuje production runtime. Gate preto odlišuje violation, missing/invalid evidence, tool failure a stale subject.

Test files používajú `*.tftest.hcl` alebo `*.tftest.json` a spúšťajú sa:

```bash
terraform test -json > terraform-test.json
```

Test subject obsahuje fixture, module/provider versions, run command, variables, target identity a cleanup outcome.

### Plan test

Každá testovacia alebo policy vrstva má vlastný subject a oracle. Parser/schema pass nepreukazuje remote authorization, report existence nepreukazuje processing a isolated apply nepreukazuje production runtime. Gate preto odlišuje violation, missing/invalid evidence, tool failure a stale subject.

```hcl
run "production_plan" {
  command = plan

  variables {
    environment   = "prod-eu"
    encrypted     = true
    multi_az      = true
    replica_count = 3
  }

  assert {
    condition     = output.replica_count == 3
    error_message = "Production topology is incorrect."
  }

  assert {
    condition     = output.encryption_enabled
    error_message = "Encryption must remain enabled."
  }
}
```

Plan test je vhodný pre input behavior, resource inventory, stable keys, outputs a known plan invariants. Neoverí real permissions, quotas, provider create/delete semantics ani runtime reachability.

### Forbidden fixture

Acceptance uzatvára celý Terraform configuration, state a remote-resource subject, nie iba posledný command. Positive path dokazuje požadovanú capability, forbidden path zachovanie ownership alebo security hranice a recovery/second-operation path stabilitu successor generation. Spoločným oracle-om je exact provider target, remote/state reconciliation a druhý no-op plan.

```hcl
run "reject_unencrypted_production" {
  command = plan

  variables {
    environment   = "prod-eu"
    encrypted     = false
    multi_az      = true
    replica_count = 3
  }

  expect_failures = [var.database]
}
```

Forbidden test preukazuje, že neplatná configuration je skutočne odmietnutá. Happy path s encryption enabled nepreukazuje enforcement sám.

## 7. Mocking a jeho hranice

Mock provider je užitočný pre module expressions, branches a computed values. Napríklad test môže kontrolovať, že output publikuje expected shape bez vytvorenia reálnej databázy.

Mock nepozná nič, čo explicitne nenamodelujeme:

```text
organization policy
IAM authorization
quota
remote naming uniqueness
API normalization
eventual consistency
provider waiter behavior
real cleanup
```

Worked failure:

```text
mock nastaví encrypted=true
→ assertions pass
→ real apply potrebuje customer-managed KMS key
→ test identity nemá kms:Encrypt/Decrypt
→ provider operation zlyhá
```

Záver nie je „mocky nepoužívať“. Správne portfólio vrstvy kombinuje:

```text
mock/plan test
→ real schema plan
→ apply v disposable targete
→ nezávislý runtime verifier
```

## 8. Apply/integration tests

Apply test vytvára reálne resources a môže pozorovať provider CRUD, IAM, organization policy, quota, API normalization a eventual consistency. Musí však bežať v explicitne izolovanom account-e alebo projecte s short-lived identity a unikátnym run namespace-om.

Cost, network a resource limits ohraničujú blast radius. Každý resource dostane immutable run labels, TTL a cleanup ownera; pri cleanup failure sa zachová state a remote inventory namiesto označenia jobu za úplne úspešný. Parallel runs nesmú zdieľať names ani state subject.

Provider output ako `available` je iba platform-visible condition. Po apply nasleduje independent application or network oracle a potom cleanup read-back. Test verdict preto rozlišuje capability pass, cleanup incomplete a external dependency outage.

Apply test vytvorí reálne resources:

```hcl
run "provider_apply" {
  command = apply

  variables {
    environment   = "test-isolated"
    encrypted     = true
    multi_az      = false
    replica_count = 1
  }

  assert {
    condition     = output.database_status == "available"
    error_message = "Provider did not report an available database."
  }
}
```

Dokáže pozorovať provider CRUD, organization policy, IAM, API normalization a eventual consistency. Potrebuje:

Transition eviduje isolated account/project, short-lived identity, unique run namespace, network/resource/cost limits, TTL a cleanup ownera.

Dopĺňa ho preserved state pri cleanup failure.

Provider output `available` stále nepreukazuje application transaction.

## 9. Runtime oracle

Po apply sa použije independent observation point:

```bash
set -euo pipefail

endpoint="$(terraform output -raw database_endpoint)"

psql "host=$endpoint dbname=payments sslmode=require" <<'SQL'
BEGIN;
CREATE TEMP TABLE verification(id text primary key, value text not null);
INSERT INTO verification(id, value) VALUES ('iac-test', 'ok');
SELECT value FROM verification WHERE id = 'iac-test';
ROLLBACK;
SQL
```

Výstup `ok` preukazuje, že verifier sa pripojil cez TLS, vykonal write/read v tejto session a databáza poskytla očakávanú základnú capability. Nepreukazuje multi-AZ failover, backup restore, produkčný IAM path ani performance pod loadom. Tie potrebujú osobitné oracles.

## 10. Upgrade test nad existujúcim state-om

Každá testovacia alebo policy vrstva má vlastný subject a oracle. Parser/schema pass nepreukazuje remote authorization, report existence nepreukazuje processing a isolated apply nepreukazuje production runtime. Gate preto odlišuje violation, missing/invalid evidence, tool failure a stale subject.

```text
apply module 4.2.4
→ zachovaj state a remote objects
→ zmeň source na 4.3.0
→ fresh upgrade plan
→ over moved/default/provider/output changes
→ apply
→ runtime verify
→ second no-op plan
→ cleanup
```

Clean install novej verzie neobsahuje old addresses ani state history a nedokáže odhaliť chýbajúci `moved` block.

Worked failure:

```text
clean 4.3.0 apply pass
→ upgrade 4.2.4 state obsahuje aws_db_instance.main
→ 4.3.0 používa module.database.aws_db_instance.main
→ no moved mapping
→ replacement production database
```

Upgrade fixture je povinná pre supported source versions.

## 11. Plan action assertions

Machine-readable plan umožní testovať destructive boundaries:

```bash
terraform plan -out=tfplan
terraform show -json tfplan > tfplan.json

jq -e '
  [
    .resource_changes[]
    | select(.address == "module.database.example_database.payments")
    | .change.actions
  ] == [["update"]]
' tfplan.json
```

Tento assertion preukazuje expected action v exact plan artifacte. Je krehký, ak provider legitimate behavior môže byť `no-op` alebo `update` podľa fixture. Stabilný oracle testuje documented contract, nie incidental plan text.

## 12. Cleanup je súčasť verdictu

Táto podsekcia vysvetľuje konkrétnu časť Terraform configuration, state a remote-resource subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inputs a graph cez provider API mutation až po state binding; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po exact provider target, remote/state reconciliation a druhý no-op plan.

Functional assertions môžu prejsť a destroy zlyhať:

```text
apply pass
→ verifier vloží object do public test bucketu
→ destroy bucketu zlyhá, lebo nie je empty
→ pipeline zahodí state
→ verejný resource prežíva bez ownera
```

Celkový verdict je `CLEANUP_INCOMPLETE`.

Transition eviduje state a remote IDs, logs/request IDs, ownera, TTL a janitor task, network/exposure containment a manual recovery path.

„Tests passed“ bez cleanup closure nie je úspešný ephemeral integration test.

## 13. Flakiness ako explicitný failure model

Nasledujúci model opisuje prechody jedného Terraform configuration, state a remote-resource subject, nie iba poradie krokov. Failure môže nastať v ktoromkoľvek bode reťazca resolved inputs a graph cez provider API mutation až po state binding a zanechať partial alebo unknown outcome. Každý transition preto potrebuje vlastný read-back a closure tvorí exact provider target, remote/state reconciliation a druhý no-op plan.

Recovery workflow eventual consistency, API throttling, shared target, mutable data source, name collision a provider incident.

Dopĺňa ho residue po cleanup failure a fixed sleep.

Preferuj condition-based polling:

```bash
for attempt in $(seq 1 30); do
  status="$(provider-cli get --id "$RESOURCE_ID" --query status --output text || true)"
  [[ "$status" == "ready" ]] && exit 0
  sleep 10
done

printf 'last_status=%s\n' "$status" >&2
exit 1
```

Bounded poll preukazuje posledný observed status v intervale. Nepreukazuje root cause, ak ready nenastane. Zachovaj request IDs a telemetry.

Quarantine potrebuje ownera, dôvod, expiry a compensating control. Permanentne skipped flaky test je missing evidence.

## 14. Production saved plan ako decision artifact

```bash
terraform plan -input=false -out=tfplan
sha256sum tfplan > tfplan.sha256
terraform show -json tfplan > tfplan.json
```

Saved plan je viazaný na source, selections, values, state observations a target. Môže obsahovať sensitive data, preto potrebuje restricted access a retention.

Apply:

```bash
sha256sum -c tfplan.sha256
terraform apply -input=false tfplan
```

Preukazuje artifact integrity a použitie saved planu. Nepreukazuje freshness, ak iný writer alebo remote drift zmenil subject. Backend/state semantics musia stale apply odmietnuť alebo workflow plán revalidovať.

## 15. Policy input

Policy decision môže používať:

```text
source metadata
+ module/provider manifest
+ plan JSON
+ environment/risk classification
+ change identity a ticket
+ exception inventory
+ external asset data
```

Policy nad HCL nevidí všetky resolved values. Policy nad planom nemusí vidieť apply-time unknown alebo runtime business behavior.

### Rego príklad: zakázaný public ingress

```rego
package terraform.network

default allow := false

public_ingress[resource] if {
  resource := input.resource_changes[_]
  resource.type == "aws_security_group_rule"
  resource.change.after.type == "ingress"
  resource.change.after.cidr_blocks[_] == "0.0.0.0/0"
}

allow if {
  count(public_ingress) == 0
}

deny contains message if {
  resource := public_ingress[_]
  message := sprintf(
    "%s exposes ingress to 0.0.0.0/0",
    [resource.address],
  )
}
```

Policy preukazuje behavior pre input schema a bundle revision. Nepreukazuje, že plan JSON je complete, že IPv6 `::/0` je tiež pokrytý alebo že runtime nemá alternate exposure path. Policy tests musia obsahovať allowed, IPv4/IPv6 denied, unknown/missing fields a schema-change fixtures.

## 16. Policy verdict classes

```text
VALID_PASS
VALID_VIOLATION
INVALID_INPUT
MISSING_REPORT
TOOL_FAILURE
BUNDLE_UNAVAILABLE
EXPIRED_EXCEPTION
SUPERSEDED_SUBJECT
```

Wrapper nesmie konvertovať prázdny file alebo analyzer crash na `VALID_PASS`.

Príklad strict shell wrappera:

```bash
set -euo pipefail

test -s tfplan.json
opa eval \
  --fail-defined \
  --data policy/ \
  --input tfplan.json \
  'data.terraform.network.deny' \
  > policy-result.json

test -s policy-result.json
jq -e '.result != null' policy-result.json
```

Konkrétna OPA exit semantics musí byť presne navrhnutá a testovaná; uvedený wrapper je ilustrácia validácie vstupu/výstupu, nie univerzálny policy runner.

## 17. Policy exceptions

Exception nie je text `approved`. Obsahuje:

```yaml
exception:
  policyId: terraform.network.public-ingress
  policyRevision: 7a21c4e
  planDigest: sha256:291a...
  resourceAddresses:
    - aws_security_group_rule.vendor_callback
  environment: prod-eu
  reason: bounded-vendor-migration
  owner: payments-platform
  approver: security-risk-owner
  compensatingControls:
    - provider-managed-ip-allowlist
    - request-authentication
  expiresAt: 2026-08-07T12:00:00Z
  remediation: migrate-to-private-connectivity
```

Exception je subject-bound, scoped a expiring. Globálny permanentný bypass je governance drift.

## 18. Worked incident: policy outage ako false clean

Plan pridáva public listener. Policy bundle fetch zlyhá. Wrapper vytvorí `{ "violations": [] }` a gate passne.

```text
policy evaluation nevznikla
→ tool error normalizovaný na empty findings
→ missing evidence sa tvári ako valid pass
→ public exposure schválená
```

Náprava:

```text
valid report schema a producer identity
+ explicitné tool/bundle error classes
+ critical policy fail-closed alebo incident fallback
+ cached signed bundle podľa policy
+ manual security review pri outage
```

## 19. Expected-versus-received evidence fan-in

Každá testovacia alebo policy vrstva má vlastný subject a oracle. Parser/schema pass nepreukazuje remote authorization, report existence nepreukazuje processing a isolated apply nepreukazuje production runtime. Gate preto odlišuje violation, missing/invalid evidence, tool failure a stale subject.

```bash
jq -e '
  (.expected | sort) as $expected
  | (.received | map(select(.valid == true) | .id) | sort) as $received
  | $expected == $received
' evidence-manifest.json
```

Rovnosť IDs preukazuje completeness len vtedy, keď každý received artifact prešiel schema, subject a validity checks. Fake alebo stale report s rovnakým ID nesmie uspokojiť inventory.

## 20. Competing hypotheses pri „green“ pipeline a failed production apply

Green pre-production pipeline a failed production apply môžu znamenať chýbajúcu real-policy coverage, odlišnú identity, quota, stale saved plan alebo neplatný/missing report. Každá hypotéza sa viaže na konkrétny subject a discriminating evidence; „testy prešli“ nie je jedna univerzálna premise.

Hypotézy sú navzájom konkurenčné vysvetlenia rovnakého symptómu. Každá musí predpovedať konkrétny observation result a zároveň výsledok, ktorý ju oslabí; inak nejde o discriminating test. Dôkazy sa viažu na rovnaký Terraform configuration, state a remote-resource subject a finálny verdict potvrdí exact provider target, remote/state reconciliation a druhý no-op plan.

Green pre-production pipeline a failed production apply môžu znamenať chýbajúcu real-policy coverage, odlišnú identity, quota, stale saved plan alebo neplatný/missing report. Každá hypotéza sa viaže na konkrétny subject a discriminating evidence; „testy prešli“ nie je jedna univerzálna premise.

```text
H1: production variables/target sa líšia od test fixture
H2: mock neobsahuje organization policy
H3: provider version/package sa líši
H4: required integration job bol skipped
H5: policy report je empty pre tool failure
H6: approved plan bol regenerated
H7: test cleanup residue ovplyvnilo quota/name
H8: credentials alebo external service sa zmenili
```

Subject manifests testujú H1/H3/H6, expected evidence inventory H4, policy producer/validity H5, real-provider audit H2/H8 a cleanup/state inventory H7.

Každá observation musí potvrdiť alebo oslabiť konkrétnu hypotézu nad rovnakou identity a časovou osou.

Rerun bez zachovania first-attempt evidence môže zničiť najlepší dôkaz.

## 21. Authoritative recovery incidentu `IAC-PAY-77`

Recovery najprv preklasifikuje každý gate result na `PASS`, `VIOLATION`, `TOOL_OR_INFRA_FAILURE`, `MISSING_OR_SKIPPED`, `STALE_SUBJECT` alebo `INVALID_REPORT`. Chýbajúci policy output sa nesmie normalizovať na prázdny clean report a fix sa musí overiť nad exact production-equivalent identity a policy bundle.

Incident sa rekonštruuje ako causal chain nad jedným Terraform configuration, state a remote-resource subject. Observations určujú prvý divergentný bod v reťazci resolved inputs a graph cez provider API mutation až po state binding; samy osebe nie sú success alebo failure verdictom. Recovery sa vyberá až po zachovaní evidence a uzatvára ju exact provider target, remote/state reconciliation a druhý no-op plan.

Recovery najprv preklasifikuje každý gate result na `PASS`, `VIOLATION`, `TOOL_OR_INFRA_FAILURE`, `MISSING_OR_SKIPPED`, `STALE_SUBJECT` alebo `INVALID_REPORT`. Chýbajúci policy output sa nesmie normalizovať na prázdny clean report a fix sa musí overiť nad exact production-equivalent identity a policy bundle.

Recovery workflow zastaví production apply, zachová plan, test/policy reports a first-attempt logs, označí verdict `INVALID_REPORT + MISSING_UPGRADE_EVIDENCE`, opraví policy wrapper tak, aby bundle outage nebol clean, pridá upgrade fixture `4.2.4 → 4.3.0` a moved mapping a spustí real-provider apply v izolovanom account-e s KMS policy.

Dopĺňa ho vykoná runtime DB transaction, uzavrie cleanup a overí resource inventory, vytvorí nový production saved plan, aplikuje presne jeho digest a overí runtime, second no-op plan a drift registration.

## 22. Acceptance a forbidden paths

Testing acceptance zahŕňa happy path, forbidden configuration, tool/report failure a cleanup failure. Gate musí odmietnuť missing evidence rovnako spoľahlivo ako policy violation a druhá operation musí potvrdiť, že fixed artifact a policy generation zostali stabilné.

Acceptance uzatvára celý Terraform configuration, state a remote-resource subject, nie iba posledný command. Positive path dokazuje požadovanú capability, forbidden path zachovanie ownership alebo security hranice a recovery/second-operation path stabilitu successor generation. Spoločným oracle-om je exact provider target, remote/state reconciliation a druhý no-op plan.

Testing acceptance zahŕňa happy path, forbidden configuration, tool/report failure a cleanup failure. Gate musí odmietnuť missing evidence rovnako spoľahlivo ako policy violation a druhá operation musí potvrdiť, že fixed artifact a policy generation zostali stabilné.

Testing/policy blok je prijatý, keď:

```text
expected evidence inventory je explicitné
+ reporty majú schema/producer/subject validity
+ fmt/validate/static/plan/apply/runtime vrstvy sú oddelené
+ mock-only evidence nie je production proof
+ supported upgrade paths majú stateful fixtures
+ cleanup failure zmení verdict
+ policy outage nie je pass
+ exceptions sú scoped a expiring
+ applied plan digest = approved plan digest
+ runtime business oracle prejde
+ second plan je no-op
```

Acceptance matrix pokrýva unencrypted production input, missing upgrade mapping, public IPv4 aj IPv6 exposure, missing/empty policy report, expired exception a regenerated plan digest.

Dopĺňa ho cleanup-incomplete run.

## 23. Anti-patterny

### „`validate` prešlo, infra je správna“

Táto podsekcia vysvetľuje konkrétnu časť Terraform configuration, state a remote-resource subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inputs a graph cez provider API mutation až po state binding; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po exact provider target, remote/state reconciliation a druhý no-op plan.

Validate nevolá production API ani business oracle.

### „Mock test je zelený, provider bude fungovať“

Každá testovacia alebo policy vrstva má vlastný subject a oracle. Parser/schema pass nepreukazuje remote authorization, report existence nepreukazuje processing a isolated apply nepreukazuje production runtime. Gate preto odlišuje violation, missing/invalid evidence, tool failure a stale subject.

Mock pokrýva iba namodelovaný behavior.

### „Scanner job success znamená clean“

Táto podsekcia vysvetľuje konkrétnu časť Terraform configuration, state a remote-resource subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inputs a graph cez provider API mutation až po state binding; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po exact provider target, remote/state reconciliation a druhý no-op plan.

Potrebujeme validný, complete a subject-bound report.

### „Assertions prešli, cleanup nie je súčasť testu“

Každá testovacia alebo policy vrstva má vlastný subject a oracle. Parser/schema pass nepreukazuje remote authorization, report existence nepreukazuje processing a isolated apply nepreukazuje production runtime. Gate preto odlišuje violation, missing/invalid evidence, tool failure a stale subject.

Zanechaný resource je test failure a operational risk.

### „Policy engine nefungoval, preto dočasne povoľme všetko“

Každá testovacia alebo policy vrstva má vlastný subject a oracle. Parser/schema pass nepreukazuje remote authorization, report existence nepreukazuje processing a isolated apply nepreukazuje production runtime. Gate preto odlišuje violation, missing/invalid evidence, tool failure a stale subject.

Fail behavior je explicitná risk policy s fallbackom, nie tichý empty report.

### „Apply znovu vypočíta rovnaký plan“

Táto podsekcia vysvetľuje konkrétnu časť Terraform configuration, state a remote-resource subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inputs a graph cez provider API mutation až po state binding; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po exact provider target, remote/state reconciliation a druhý no-op plan.

Nový plan je nový decision subject.

## 24. Kontrolné otázky

1. Prečo quality gate potrebuje exact evidence subject?
2. Ako sa pass líši od missing, invalid a cleanup-incomplete?
3. Čo `fmt` a `validate` preukazujú a čo nie?
4. Kedy je plan test vhodný a kedy treba apply test?
5. Aké limity má mock provider?
6. Prečo clean-install test nenahradí upgrade test?
7. Čo musí obsahovať disposable apply-test environment?
8. Prečo runtime oracle používa nezávislý observation point?
9. Čo saved plan digest preukazuje a čo nepreukazuje?
10. Aké fields musí policy exception obsahovať?
11. Ako sa zabráni konverzii tool failure na empty findings?
12. Aké forbidden fixtures musia existovať pre kritickú Terraform zmenu?

## Glossary impact

Relevantné pojmy: Terraform evidence subject, expected evidence inventory, native Terraform test, plan test, apply test, mock provider, upgrade fixture, oracle fidelity, cleanup verdict, saved plan, plan JSON, Policy as Code, Rego, policy exception, invalid report, missing evidence a evidence fan-in.

## Primárne zdroje

- [Terraform test](https://developer.hashicorp.com/terraform/cli/commands/test)
- [Terraform test files](https://developer.hashicorp.com/terraform/language/tests)
- [Terraform plan](https://developer.hashicorp.com/terraform/cli/commands/plan)
- [Terraform show JSON](https://developer.hashicorp.com/terraform/cli/commands/show)
- [Open Policy Agent documentation](https://www.openpolicyagent.org/docs/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Drift](drift.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Praktický Terraform projekt od prázdneho adresára po overený remote state →](terraform-practical-walkthrough.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
