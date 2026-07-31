# Remote backend a state locking

Terraform backend je change-control boundary pre persistentný state. Produkčný backend nemá iba „uložiť `terraform.tfstate` do cloudu“. Musí jednoznačne identifikovať state subject, serializovať writers, chrániť integritu snapshotov, uchovať recovery history a umožniť určiť outcome pri timeoute alebo network partition. Lock je dôležitá časť tohto modelu, ale chráni iba writers nad tým istým backend/state subjectom. Správne získaný lock nad nesprávnym keyom stále povoľuje chybný apply.

Kapitola otvára incident `IAC-PAY-76`. Atlas Payments migruje produkčný network state do nového backendu. Hlavný pipeline používa nový key, no scheduled drift job zostane na starom keyi. Oba backendy poskytujú vlastný platný lock a oba writers sa považujú za exkluzívne. Remote objects však zdieľajú, takže vzniknú dve konzistentné state histórie, ktoré striedavo mutujú rovnakú infraštruktúru.

## 1. Dominantný backend-to-commit lifecycle

```text
writer identity a intended state subject
→ backend initialization
→ endpoint/key/workspace read-back
→ lock acquisition
→ authoritative lineage/serial read
→ plan/apply nad fresh snapshotom
→ provider remote mutation
→ conditional successor snapshot write
→ lock release
→ remote/runtime verification
→ versioning, restore a recovery closure
```

Backend musí odpovedať na štyri otázky:

1. **Ktorý state subject čítame a zapisujeme?**
2. **Kto je aktuálny writer a má exkluzívne oprávnenie?**
3. **Ktorý snapshot je authoritative predecessor?**
4. **Bol successor snapshot určite commitnutý, určite necommitnutý alebo je outcome neznámy?**

## 2. Backend verzus provider

```text
backend
→ state storage, locking, version history, prípadne run queue

provider
→ remote cloud/SaaS reads a mutations
```

Backend outage môže zastaviť change-control plane, zatiaľ čo produkcia beží. Provider outage môže zastaviť remote mutation, aj keď state storage funguje. Pri incidente ich observation points a recovery oddeľuj.

Apply identity môže mať dve capability sets:

```text
backend capability
→ read/write jeden state key, acquire/release lock

provider capability
→ mutate presný cloud account/region/resource scope
```

Ich oddelenie obmedzuje blast radius. Provider admin nemusí mať právo mazať state history a backend admin nemusí mať cloud mutation capability.

## 3. Backend initialization je subject selection

Backend sa inicializuje pred bežným Terraform graphom. Praktický production pattern:

```hcl
terraform {
  backend "s3" {}
}
```

Environment-specific values sa dodajú kontrolovaným súborom:

```hcl
# backend-prod-eu.hcl
bucket         = "atlas-iac-prod-state"
key            = "payments/network/prod-eu.tfstate"
region         = "eu-central-1"
encrypt        = true
use_lockfile   = true
```

```bash
terraform init -input=false -backend-config=backend-prod-eu.hcl
```

`init` success preukazuje, že Terraform dokázal nakonfigurovať a kontaktovať zadaný backend podľa svojich checks. Nepreukazuje, že key zodpovedá business intentu alebo že lineage je očakávaná. Pipeline musí read-backnúť backend subject cez kontrolovaný manifest a state metadata.

Backend credentials sa necommitujú do source. Používajú sa short-lived workload identities alebo native credential chainy. Niektoré backend parameters sa môžu objaviť v working-directory metadata alebo plan context-e, preto runner filesystem a artifacts patria do citlivej boundary.

## 4. Initialization modes nie sú zameniteľné

```bash
terraform init -reconfigure
terraform init -migrate-state
```

`-reconfigure` prijme novú backend configuration bez pokusu zachovať predchádzajúcu initialization association. `-migrate-state` vykonáva state ownership transition medzi backends. Migrácia nie je iba lokálna oprava `.terraform` metadata; je to production state cutover.

Každý init subject má obsahovať:

```yaml
backendInitialization:
  sourceRevision: 91ac...
  backendType: s3
  endpointOrAccount: atlas-iac-prod-state
  key: payments/network/prod-eu.tfstate
  workspace: default
  expectedLineage: 37fd...
  expectedMinimumSerial: 208
  identity: gitlab-iac-prod
  mode: normal
```

## 5. Lock ako writer lease

Terraform pri podporovanom backende automaticky lockuje operácie, ktoré môžu zapisovať state. Lock logicky chráni critical section:

```text
acquire
→ read current snapshot
→ calculate a execute transition
→ write successor snapshot
→ release
```

Lock metadata má umožniť identifikovať:

- backend/state subject;
- ownera alebo run ID;
- operation type;
- acquisition time;
- lock ID alebo lease token;
- miesto executionu.

Lock nepreukazuje, že writer vybral správny backend. Nechráni ani remote object pred iným state-om, ručným cloud zásahom alebo externým controllerom.

## 6. Pipeline queue pred backend lockom

Backend lock je integritná ochrana poslednej vrstvy. CI/CD má vytvoriť logickú queue:

```text
one environment/state subject
→ one eligible apply at a time
→ stale pending plans canceled alebo revalidated
→ backend lock
```

Bez queue sa veľa jobs preteká o lock, approvals starnú a operátori sú motivovaní lock vypínať. `-lock=false` nie je performance tuning. Odstraňuje ochranu pred concurrent state writers a vyžaduje nezávisle preukázaný exclusive access.

## 7. Multi-writer race nad jedným state-om

```text
writer A číta serial 208
writer B číta serial 208
A vytvorí object A a zapíše 209
B vytvorí object B a pokúsi sa zapísať successor z 208
```

Dobrý backend/lock model stale writer odmietne. Bez ochrany môže snapshot B prepísať binding A, hoci remote API obsahuje obe mutations.

Tento incident vytvára:

```text
remote objects A + B
state pozná iba B
→ ďalší plan navrhuje duplicate alebo destroy
```

## 8. Dvaja writers nad dvoma backendmi

Závažnejší incident `IAC-PAY-76`:

```text
nový pipeline
→ backend new/prod-eu, lock N1, lineage L-new

starý scheduled job
→ backend old/prod-eu, lock O1, lineage L-old

oba mutujú rovnaký cloud account/resources
```

Každý writer má platný lock, pretože locks sú nad odlišnými subjects. Locking systém funguje správne a napriek tomu nedokáže zabrániť ownership konfliktu.

Detection vyžaduje:

- canonical backend registry;
- pipeline search pre staré keys/endpoints;
- cloud audit correlation podľa writer identity;
- inventory remote IDs naprieč states;
- explicitné zneplatnenie source backend write pathu po migrácii.

## 9. Force unlock neukončuje writera

```bash
terraform force-unlock LOCK_ID
```

Force unlock odstráni lock record. Nezabije pôvodný Terraform proces a nezruší provider request, ktorý už beží.

Pred použitím musí byť potvrdené:

```text
lock patrí správnemu backend subjectu
+ pôvodný local alebo remote process už nebeží
+ provider mutation nepokračuje async
+ neexistuje child worker ani queued write
+ latest snapshot a serial sú známe
+ po unlocku vznikne fresh plan
```

### Worked failure

Apply A vytváral databázu a čakal na provider waiter. UI job stratil heartbeat, ale remote worker pokračoval. Operátor force-unlockol lock a spustil apply B.

```text
A stále mutuje remote DB
→ lock record odstránený
→ B získa nový lock a číta starý serial
→ A aj B dokončia odlišné remote/state transitions
```

Recovery najprv zastaví oboch writers, zachová logs a request IDs, určí latest state a remote object timeline a až potom vykoná binding reconciliation.

## 10. Conditional snapshot transition

Bezpečný state write je logicky compare-and-swap:

```text
ak current subject == lineage L / serial 208
→ zapíš successor serial 209
inak
→ odmietni stale writer
```

Konkrétna backend implementácia môže používať lock object, lease, transaction alebo platform queue. Dôležitý invariant je, že stale writer nesmie ticho prepísať novší snapshot.

## 11. Unknown backend write outcome

Network partition môže nastať po write requeste, ale pred response:

```text
provider mutation complete
→ client odošle state 209
→ connection reset
→ client nevie, či commit prebehol
```

Pipeline verdict je `UNKNOWN_STATE_WRITE_OUTCOME`, nie automaticky „write failed“.

Recovery:

```text
nepridávať druhého writera
→ prečítať backend object/version inventory
→ overiť lineage/serial
→ overiť lock
→ porovnať remote state s candidate snapshots
→ vybrať authoritative successor
→ fresh plan
```

Slepý retry môže prepísať novší state alebo zopakovať remote side effect.

## 12. Praktický backend identity gate

```bash
set -euo pipefail

expected_bucket="atlas-iac-prod-state"
expected_key="payments/network/prod-eu.tfstate"
expected_lineage="37fd-placeholder"

terraform init -input=false -backend-config=backend-prod-eu.hcl
terraform state pull > state.json

actual_lineage="$(jq -r '.lineage' state.json)"
actual_serial="$(jq -r '.serial' state.json)"

printf 'backend_bucket=%s\n' "$expected_bucket"
printf 'backend_key=%s\n' "$expected_key"
printf 'lineage=%s serial=%s\n' "$actual_lineage" "$actual_serial"

[[ "$actual_lineage" == "$expected_lineage" ]]
```

Tento gate preukazuje lineage snapshotu, ktorý backend vydal. Bucket/key values v príklade pochádzajú z orchestration manifestu; samotný `state pull` ich nemusí dôveryhodne potvrdiť. Preto sa backend config generation a pipeline input provenance auditujú samostatne.

## 13. Backend migration ako ownership cutover

Dôveryhodná migrácia:

```text
inventory všetkých writers a consumers
→ freeze source writes
→ source lineage/serial backup
→ pripraviť destination security/locking/versioning
→ migrate snapshot
→ destination read-back
→ fresh plan bez mutation
→ aktualizovať všetky pipelines
→ zneplatniť source credentials/write policy
→ enable destination queue
→ druhý no-op plan a drift check
```

Source backend nemá zostať „pre istotu“ zapisovateľný. Read-only retention môže byť potrebná pre audit, ale writer capability sa revokuje.

## 14. Migration validation

Po migrácii over:

```bash
terraform state pull > destination-state.json
jq '{lineage,serial}' destination-state.json
terraform state list | sort > destination-addresses.txt
terraform plan -detailed-exitcode
```

Expected výsledok je rovnaká lineage alebo explicitne zdokumentovaná migration semantics, správny serial, rovnaké bindings a no-op plan. No-op plan nepreukazuje, že starý backend už nemá writerov; na to treba IAM/audit/pipeline inventory.

## 15. Remote state verzus remote execution

Remote state:

```text
Terraform proces beží lokálne alebo v CI
→ state je vzdialený
```

Remote execution:

```text
platform prijme run subject
→ managed worker vykoná plan/apply
→ platform spravuje queue, variables, policy a state
```

Pri lock incidente musí byť známe, kde proces skutočne beží. Zrušenie CI wrapper jobu nemusí zrušiť remote run.

## 16. Backend security model

State môže obsahovať secrets a detailnú infra topology. Backend chráni confidentiality, integrity, availability a recovery.

Minimálne controls:

```text
short-lived identities
path/workspace-level least privilege
encryption in transit a at rest
versioning a delete protection
audit events
detekcia neštandardných writers
separácia apply a backend-admin roles
testovaný restore
```

Apply identity nemá mať oprávnenie mazať history alebo KMS key. Break-glass backend admin capability má ownera, approval, expiry a audit.

## 17. Encryption key a recovery dependency

Customer-managed key pridáva ďalší authoritative lifecycle:

```text
state snapshot
→ encryption key version
→ decrypt policy
→ backup/restore identity
```

Over deletion protection, rotation semantics, cross-account recovery a restore s reálnym key pathom. Backup zašifrovaný nedostupným keyom nie je recovery asset.

## 18. Versioning, retention a secret history

Backend versioning chráni pred accidental overwrite. Nemusí chrániť pred account compromise, destructive adminom alebo key lossom.

Staré snapshots zostávajú citlivé aj po rotation credentialu, pretože obsahujú historické secret material alebo topology. Retention policy musí kombinovať recovery window, compliance a secure deletion.

## 19. Cross-state consumption

`terraform_remote_state` môže sprístupniť outputs, ale často vyžaduje backend access širší než logický consumer contract. Consumer sa viaže na producer backend availability a output schema.

Silnejší boundary môže publikovať:

```text
network state output
→ versionovaný parameter/service-catalog record
→ consumer-specific read permission
```

Tak producer neodhaľuje celý state subject a môže definovať freshness/compatibility.

## 20. Competing hypotheses pri stale locku

Symptom: `Error acquiring the state lock`, no CI dashboard neukazuje aktívny apply.

```text
H1: local Terraform process stále beží
H2: remote worker pokračuje po ukončení wrapper jobu
H3: lock je orphaned po crashi
H4: caller nemá právo lock čítať alebo odstrániť
H5: backend/network/KMS je nedostupný
H6: requesting job inicializoval nesprávny key
H7: lock read je stale alebo throttled
```

Diskriminačné evidence:

- process/run inventory pre H1/H2;
- lock owner, ID a timestamp pre H1–H3;
- authorization audit pre H4;
- backend telemetry pre H5/H7;
- backend manifest, lineage a key pre H6.

Force unlock sa použije až po potvrdení H3 a vylúčení aktívneho writera.

## 21. Acceptance a forbidden paths

Backend blok je prijatý, keď:

```text
canonical backend endpoint/key/workspace sú explicitné
+ expected lineage/serial sa read-backnú
+ pipeline queue serializuje applies
+ backend lock je zapnutý
+ force-unlock vyžaduje process evidence
+ state history a restore sú testované
+ source backend write path po migrácii je revokovaný
+ alternate old-backend pipeline je odmietnutý
+ second plan nad destination je no-op
+ remote inventory nemá dual ownership
```

## 22. Anti-patterny

### „Remote state automaticky znamená locking“

Locking support závisí od backendu a configuration.

### „Mám lock, takže som jediný owner“

Lock chráni iba jeden state subject. Iný backend/state môže meniť rovnaký object.

### „Force unlock je bezpečný, keď job zmizol z UI“

Wrapper job a Terraform/provider process môžu mať rozdielny lifecycle.

### „Migrácia skončila po úspešnom copy“

Musí sa zavrieť starý write path a overiť bindings, plan a remote ownership.

### „Versioning v rovnakom bucket-e je kompletný backup“

Nechráni pred všetkými compromise, deletion a key-loss scenármi.

## 23. Kontrolné otázky

1. Prečo remote backend nie je iba centralizovaný súbor?
2. Aký rozdiel je medzi backend a provider capability?
3. Čo `terraform init` preukazuje a čo nepreukazuje?
4. Prečo lock nad nesprávnym keyom nechráni produkciu?
5. Aký rozdiel je medzi CI queue a backend lockom?
6. Prečo force unlock neukončuje writera?
7. Ako sa klasifikuje network partition po state write requeste?
8. Čo musí obsahovať backend migration cutover?
9. Ako sa dokáže, že starý backend už nemá writers?
10. Aký rozdiel je medzi remote state a remote execution?
11. Prečo encryption key patrí do restore testu?
12. Ako sa testuje forbidden alternate-backend path?

## Glossary impact

Relevantné pojmy: Terraform backend, remote state, backend initialization, state subject, lock, writer lease, force unlock, conditional state write, unknown write outcome, backend migration, dual writer, remote execution, state versioning, restore, canonical backend registry a alternate-backend path.

## Primárne zdroje

- [Terraform backend configuration](https://developer.hashicorp.com/terraform/language/backend)
- [Terraform remote state](https://developer.hashicorp.com/terraform/language/state/remote)
- [Terraform state locking](https://developer.hashicorp.com/terraform/language/state/locking)
- [Terraform state backends](https://developer.hashicorp.com/terraform/language/state/backends)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Terraform state](terraform-state.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Modules →](modules.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
