# Remote backend a state locking

Terraform backend je change-control boundary pre persistentný state. Produkčný backend musí nielen uložiť snapshot, ale aj spoľahlivo identifikovať environment, serializovať writers, chrániť integritu a umožniť obnovu po nejasnom write outcome-e.

Dominantný model:

```text
writer identity a state target
→ backend initialization
→ lock acquisition
→ read authoritative lineage/serial
→ plan/apply nad fresh subjectom
→ remote mutation
→ conditional state snapshot write
→ unlock
→ audit, verification a recovery
```

Remote storage bez tohto lifecycle-u je iba centralizovaný súbor. Nezabraňuje lost updates, dual writers ani zápisu do nesprávneho environmentu.

## 1. Atlas scenár: produkčný state backend

Atlas Payments používa pre produkciu state subject:

```text
backend = object storage account atlas-iac-prod
key     = payments/network/prod.tfstate
lineage = L-prod
lock    = payments/network/prod
```

CI apply job získava short-lived identity viazanú na repository, protected ref a environment `production`. Táto identity smie:

- čítať a zapisovať iba daný state key;
- vytvoriť a uvoľniť iba zodpovedajúci lock;
- čítať version history;
- nesmie meniť retention, mazať backupy ani spravovať iné states.

Backend admin a provider apply identity sú samostatné capabilities. Kompromitácia cloud deploy jobu nemá automaticky umožniť zničiť state history.

## 2. Backend verzus provider

```text
backend  → state storage, lock, snapshot history, prípadne remote run queue
provider → číta a mutuje cloud/SaaS/runtime objects
```

Backend outage môže zastaviť change-control plane, zatiaľ čo produkčná infraštruktúra ďalej funguje. Provider outage môže zablokovať remote mutations, aj keď state storage je zdravý.

Pri incidente ich diagnostikuj oddelene.

## 3. Backend identity vzniká pri `init`

Backend configuration sa vyhodnocuje pred bežnými variables, locals, resources a data sources. Backend target musí byť známy počas:

```text
terraform init
→ backend handshake/configuration
→ local working-directory metadata
→ state access
```

Preto backend block nemôže bezpečne závisieť od `var.*` alebo resource outputov.

Environment-specific alebo citlivé argumenty dodávaj cez kontrolovaný init workflow, native credential chain alebo externú configuration:

```bash
terraform init -backend-config=backend-prod.hcl
```

Backend credentials nepatria do source. Niektoré backend hodnoty sa môžu objaviť v `.terraform` metadata alebo saved plan context-e, preto používaj short-lived identity a chránený runner.

## 4. Initialization subject

Pred planom musí byť rekonštruovateľné:

```text
configuration revision
backend type a endpoint
state key/workspace
expected lineage
caller identity
network/KMS context
init mode: normal | reconfigure | migrate-state
```

`-reconfigure` mení local initialization a prijme zadaný backend target. `-migrate-state` je ownership-presun snapshotu. Tieto operácie nie sú zameniteľné.

## 5. Lock ako writer lease

Lock chráni critical section:

```text
acquire lock
→ read current serial
→ calculate/apply
→ write successor snapshot
→ release lock
```

Lock metadata má umožniť identifikovať:

- backend/state subject;
- ownera alebo run ID;
- acquisition time;
- operation type;
- lease alebo recovery context podľa backendu.

Lock chráni writers nad jedným state-om. Nechráni remote objekt pred iným state-om, ručným cloud zásahom alebo externým controllerom.

## 6. Locking a pipeline serialization

Backend lock je posledná integritná vrstva. CI/CD má pred ním vytvoriť explicitnú queue:

```text
one state/environment
→ one eligible apply at a time
→ stale pending plans canceled alebo revalidated
→ backend lock
```

Bez pipeline serialization sa veľa jobs zbytočne preteká o lock, approvals starnú a operátori sú motivovaní používať `-lock=false` alebo force unlock.

Plan jobs môžu tiež čítať/refreshať state a podľa backendu získavať lock. Queue policy musí definovať, čo môže bežať paralelne a čo nie.

## 7. Multi-writer race

Ak locking chýba alebo sa vypne:

```text
writer A číta L-prod/S208
writer B číta L-prod/S208
A vytvorí remote object A a zapíše S209
B vytvorí remote object B a zapíše snapshot odvodený zo S208
→ binding A sa môže stratiť alebo vznikne konflikt
```

Remote API môže obsahovať obe zmeny, zatiaľ čo state pozná iba jednu. Ide o remote/state divergence a lost-update incident.

`-lock=false` je prípustné iba pri preukázanom exclusive access-e a operácii, ktorej failure semantics sú pochopené. Nie je to riešenie pomalého backendu.

## 8. Worked failure: force unlock uvoľnil stále aktívneho writera

Apply A bol pomalý pri vytváraní databázy. CI job stratil UI heartbeat, ale remote worker a Terraform proces ďalej bežali. Operátor predpokladal orphaned lock a spustil `terraform force-unlock`.

```text
writer A drží lock a čaká na DB create
→ force unlock odstráni lock record
→ writer B získa nový lock a číta starý serial
→ A dokončí remote mutation
→ B vykoná vlastný apply
→ dva writers sa pokúsia zapísať successor snapshot
```

Force unlock neukončuje pôvodný proces. Príčinou nebola chybná lock service, ale nesprávne určený execution state pôvodného writera.

Recovery:

1. zastaviť oboch writers a nové applies;
2. zachovať lock/run/backend logs;
3. overiť latest authoritative serial a version history;
4. inventory remote mutations oboch runs;
5. obnoviť alebo opraviť bindings najmenším zásahom;
6. fresh plan nad skutočným snapshotom;
7. runtime verification;
8. opraviť liveness/queue/force-unlock runbook.

## 9. Force unlock protocol

Pred `terraform force-unlock <LOCK_ID>` musí byť potvrdené:

```text
lock patrí správnemu backendu a state subjectu
+ pôvodný local/remote process už nebeží
+ provider mutation nepokračuje asynchrónne
+ neexistuje child worker alebo queued write
+ latest snapshot a serial sú známe
+ po unlocku sa vytvorí fresh plan
```

Neistota znamená, že unlock sa odkladá a najprv sa vykoná containment a observability.

## 10. Snapshot write ako conditional transition

Bezpečný backend write je logicky:

```text
ak current lineage/serial == L-prod/S208
zapíš successor L-prod/S209
inak odmietni stale writer
```

Konkrétny backend môže implementovať locking a consistency odlišne, ale workflow musí chrániť pred stale overwrite-om a unknown dual successom.

State object storage potrebuje konzistentný read/write model vhodný pre backend a overený behavior pri timeoutoch, retries a network partition.

## 11. Worked failure: network partition po state write requeste

Atlas apply úspešne zmenil route table a odoslal snapshot S209. Connection sa prerušilo pred odpoveďou.

```text
client nevie, či S209 bol commitnutý
→ pipeline je failed/inconclusive
→ retry môže čítať S208 alebo S209
→ remote route už je zmenená
```

Správna klasifikácia je **unknown backend write outcome**, nie automaticky failed write.

Postup:

1. nepridávať druhého writera;
2. prečítať backend object/version inventory a serial;
3. overiť lock stav;
4. porovnať remote route table s S208/S209 intentom;
5. zachovať lokálny recovery snapshot;
6. vytvoriť fresh refresh/plan až po určení authoritative snapshotu;
7. overiť traffic outcome.

Slepé opakovanie apply môže duplikovať side effect alebo prepísať novší snapshot.

## 12. Backend migration ako ownership cutover

Migrácia nie je iba copy súboru:

```text
freeze all writers
→ identifikuj source backend/workspace/lineage/serial
→ backup a integrity proof
→ priprav destination security, lock a versioning
→ migrate snapshot
→ read-back lineage/resources/outputs
→ fresh plan proti remote platforme
→ prekonfiguruj všetkých consumers
→ zneplatni source write path
→ enable destination writers
```

### Worked failure: dual-writer migrácia

Tím migroval state do nového backendu, ale jeden scheduled pipeline zostal nakonfigurovaný na starý key.

```text
nové applies zapisujú destination
+ scheduled drift job zapisuje source
→ vzniknú dve lineage vetvy s rovnakým pôvodom
→ oba backendy vyzerajú interne konzistentne
→ remote objects dostávajú konfliktné mutations
```

Recovery musí vybrať jeden authoritative backend podľa remote mutation timeline-u, zachovať oba snapshots, obnoviť bindings a definitívne zavrieť starý write path.

## 13. Remote state verzus remote execution

Remote state storage:

```text
lokálny alebo CI proces vykonáva Terraform
→ state je uložený vzdialene
```

Remote execution:

```text
platform queue prijme configuration/run subject
→ managed worker vykoná plan/apply
→ platform spravuje variables, policy, state a run lifecycle
```

Remote backend sám osebe neznamená remote worker ani central queue. Pri diagnostike identifikuj, kde skutočne beží Terraform proces a kto vlastní jeho liveness.

## 14. State storage security

State je často privileged infrastructure inventory a môže obsahovať secrets. Backend chráni:

- confidentiality;
- integrity;
- availability;
- recovery history.

Controls:

```text
short-lived scoped identities
encryption in transit a at rest
path/workspace-level authorization
audit a anomaly alerts
versioning a delete protection
retention a testovaný restore
separácia apply a backend-admin capabilities
```

Apply identity nemá mať právo zmazať snapshots alebo encryption keys. Backend admin nemusí mať cloud provider admin access.

## 15. Encryption a key lifecycle

Customer-managed encryption key pridáva recovery dependency. Over:

- decrypt permissions;
- rotation behavior;
- deletion protection;
- cross-account/region recovery;
- audit;
- restore test s reálnym key pathom.

Backup zašifrovaný zmazaným alebo nedostupným keyom je nepoužiteľný.

## 16. Versioning, backup a retention

Versioning v rovnakom storage chráni pred časťou accidental overwrite scenárov. Nemusí chrániť pred:

- account compromise;
- destructive adminom;
- region-wide incidentom;
- policy alebo key lossom.

Podľa kritickosti pridaj oddelenú backup vrstvu. Retention musí vyvažovať recovery window, secret history, compliance a storage cost. Staré snapshots obsahujú rotované secrets a zostávajú citlivé.

## 17. Environment a state separation

Príklady keys:

```text
network/prod
platform/prod
application-a/prod
network/stage
```

Prefix sám osebe nie je security boundary. IAM/KMS/network policy musí obmedziť presné paths a operations.

Produkčný state potrebuje canonical backend identity, environment-scoped apply identity, chránenú queue, prísnejšiu retention a recovery ownera. Variable `environment = "prod"` tieto controls nevytvára.

## 18. Remote-state consumption

`terraform_remote_state` poskytuje outputs iného state-u, ale môže vyžadovať access k celému snapshotu alebo backend credentials. Vytvára coupling na producer schema, cadence a backend availability.

Pre silnú boundary publikuj úzky contract do parameter store, service catalogu alebo configuration registry:

```text
producer output subject
→ explicitná publikácia/version
→ consumer-specific read access
```

## 19. Kauzálny diagnostický walkthrough

Symptom: pipeline hlási `Error acquiring the state lock`, ale dashboard neukazuje aktívny apply.

### Krok 1 — stabilizuj subject

```text
backend account atlas-iac-prod
key payments/network/prod
workspace default
lineage L-prod
lock ID K913
requesting run R522
```

### Krok 2 — konkurenčné hypotézy

```text
H1: existuje aktívny local alebo remote Terraform writer
H2: CI job skončil, ale child/remote process pokračuje
H3: lock record je orphaned po crashi
H4: requesting identity nemá read/delete lock permission
H5: locking service alebo network je nedostupná
H6: pipeline inicializovala nesprávny state key/workspace
H7: backend throttling alebo stale read zobrazuje neaktuálny stav
```

### Krok 3 — diskriminačné observation points

- CI a remote-run process inventory testuje H1/H2;
- lock owner/run ID a provider activity testujú H1–H3;
- backend authorization audit testuje H4;
- service/network telemetry testuje H5/H7;
- init metadata, key a lineage testujú H6.

Atlas zistí, že UI job bol canceled, ale remote execution run stále čakal na cloud API a držal lock. H2 vysvetľuje symptom.

### Krok 4 — containment

Nové applies zostanú blokované. Remote run sa korektne cancel-ne a čaká sa na ukončenie provider mutation. Lock sa neuvoľní ručne, kým platforma nepotvrdí termináciu writera.

### Krok 5 — over outcome

Po release locku sa overí latest serial, remote mutation timeline a vytvorí sa fresh plan. Apply queue pokračuje až po potvrdení, že state a remote objekty sú konzistentné.

### Krok 6 — skorší control

Finding sa mení na remote-run liveness panel, cancellation contract, alert pre orphaned lock a force-unlock approval vyžadujúci process evidence.

## 20. Diagnostický runbook

1. Urči backend endpoint, key/workspace, lineage, serial a lock ID.
2. Identifikuj writer identity, run ID a miesto executionu.
3. Oddeľ storage, locking, network, KMS a authorization observation points.
4. Over aktívne a child/remote processes pred force unlockom.
5. Pri unknown write outcome-e zastav ďalších writers.
6. Porovnaj backend version history s remote mutation timeline-om.
7. Pri migrácii over source aj destination a zavri dual-write path.
8. Vytvor fresh plan až po určení authoritative snapshotu.
9. Over runtime outcome a nový successor serial.
10. Oprav queue, identity, migration alebo recovery control.

## 21. Referenčné pravidlá

- Backend je state/change-control boundary, provider je remote-object boundary.
- Remote storage bez locking nie je bezpečný multi-writer model.
- Pipeline queue a backend lock sa dopĺňajú.
- Force unlock odstraňuje lock, nie pôvodný proces.
- Unknown state-write outcome sa najprv pozoruje, nie retryuje.
- Backend migration je writer cutover s jedným authoritative destinationom.
- State path prefix bez IAM policy nie je isolation.
- Remote state a remote execution sú odlišné capabilities.
- Versioning nie je automaticky disaster-recovery backup.
- Apply a backend-admin permissions majú byť oddelené.

## 22. Časté omyly

### „Remote backend automaticky rieši concurrency“

Iba ak konkrétny backend a workflow poskytujú účinné locking a serialization.

### „Lock je starý, môžeme ho force-unlocknúť“

Vek nepotvrdzuje, že pôvodný process ani provider mutation už nebežia.

### „State write timeout znamená, že sa nič nezapísalo“

Výsledok môže byť unknown; treba overiť snapshot history a serial.

### „Migráciu môžeme chvíľu prevádzkovať v oboch backendoch“

Dual writers vytvoria divergentné state histories a konfliktné remote mutations.

### „Backend credentials sú menej citlivé než cloud credentials“

Môžu odhaliť secrets, topology aj recovery snapshots a umožniť state corruption.

## Zhrnutie

Dôveryhodný backend lifecycle je:

```text
canonical state target a scoped writer
→ init identity
→ serialized queue a lock
→ fresh lineage/serial read
→ bounded remote mutation
→ conditional successor snapshot
→ verified unlock
→ audit, version history a tested recovery
```

Locking troubleshooting sa nesmie skončiť odstránením lock recordu. Musí preukázať stav pôvodného writera, authoritative snapshot a remote mutation outcome.

## Oficiálna dokumentácia

- [Backend configuration](https://developer.hashicorp.com/terraform/language/backend)
- [Backends: state storage and locking](https://developer.hashicorp.com/terraform/language/state/backends)
- [State locking](https://developer.hashicorp.com/terraform/language/state/locking)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Terraform state](terraform-state.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Modules →](modules.md)
<!-- KNOWLEDGE-NAVIGATION:END -->