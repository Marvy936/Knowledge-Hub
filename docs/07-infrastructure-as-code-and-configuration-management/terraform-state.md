# Terraform state

Terraform state je persistentný model, ktorý spája resource addresses v konfigurácii s konkrétnymi remote objektmi a uchováva metadata potrebné na plánovanie ďalších zmien.

State nie je náhrada konfigurácie ani všeobecná inventory databáza. Je to kritický operational asset Terraform execution modelu.

## 1. Prečo Terraform potrebuje state

Konfigurácia obsahuje deklarovanú adresu:

```text
module.network.aws_vpc.main
```

Cloud API pozná remote identitu:

```text
vpc-0123456789abcdef0
```

State uchováva mapovanie medzi nimi.

Bez tohto mapovania by Terraform nevedel spoľahlivo určiť:

- ktorý objekt má aktualizovať,
- ktorý objekt už existuje,
- ktoré instances patria ku `count` alebo `for_each`,
- ktoré objekty boli presunuté medzi adresami,
- ktoré provider configuration a schema metadata sa použili.

## 2. State nie je desired state

Desired state je konfigurácia.

State reprezentuje Terraformom známy snapshot spravovaných objektov a ich identity/attributes z posledného úspešného alebo čiastočne úspešného runu.

Remote systém je actual state.

```text
configuration = desired
state snapshot = Terraform knowledge
remote APIs = actual
```

Plan porovnáva všetky tri vrstvy.

## 3. Resource binding

Príklad:

```hcl
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}
```

State binding:

```text
aws_vpc.main
→ provider registry.terraform.io/hashicorp/aws
→ remote ID vpc-0123456789
→ known attributes
```

Ak state binding zmizne, remote objekt môže naďalej existovať, ale Terraform ho už nepovažuje za spravovaný touto adresou.

## 4. State snapshot

State sa vyvíja cez snapshots. Snapshot obsahuje okrem resources aj metadata ako:

- Terraform/state format version,
- lineage,
- serial,
- outputs,
- provider associations,
- resource instance data,
- dependency-related metadata podľa formátu a verzie.

State format je interný implementation detail. Nespoliehaj sa na ručné parsovanie interného JSON tam, kde existuje stabilné CLI alebo API.

## 5. Lineage

Lineage identifikuje históriu konkrétneho state-u.

Dva states s rozdielnym lineage typicky vznikli nezávisle. Terraform používa lineage ako ochranu pred prepísaním nesúvisiaceho state snapshotu.

Pri disaster recovery treba overiť, že obnovuješ správny lineage pre správny environment a configuration boundary.

## 6. Serial

Serial je monotónne rastúce číslo snapshotu.

Vyšší serial znamená novšiu známu state verziu v rovnakej lineage.

Pri manuálnom push Terraform kontroluje, či sa operátor nepokúša prepísať novší snapshot starším. Force bypass je nebezpečný a môže spôsobiť stratu zmien.

## 7. Local state

Bez nakonfigurovaného remote backendu Terraform používa local backend a typicky uloží state do:

```text
terraform.tfstate
```

Môže vytvoriť aj backup predchádzajúcej verzie.

Local state je vhodný pre:

- učenie,
- izolovaný experiment,
- jedného operátora bez collaboration požiadaviek.

Nie je vhodný ako produkčný team model, pretože chýba central access, robustná locking/concurrency boundary a spravovaný recovery lifecycle.

## 8. State môže obsahovať secrets

Provider attributes, outputs a resource arguments môžu skončiť v state.

Príklady:

- generated passwords,
- connection strings,
- private keys,
- tokens,
- database credentials,
- sensitive configuration.

`sensitive = true` obmedzuje zobrazovanie, ale state hodnotu môže stále obsahovať.

State storage preto potrebuje:

- encryption at rest a in transit,
- least-privilege access,
- audit logging,
- versioning/backups,
- secure CI handling,
- zákaz publikovania ako bežný artifact.

## 9. Refresh

Terraform používa provider read operácie na aktualizáciu poznania o remote objektoch.

Pri planning workflowe refresh odhalí napríklad:

- manuálne zmenený argument,
- chýbajúci remote objekt,
- platformou zmenený computed attribute,
- novú normalizovanú hodnotu.

Refresh nemení desired configuration. Aktualizuje known actual state pre plan rozhodnutie.

## 10. Drift

Drift vznikne, keď remote objekt nezodpovedá konfigurácii/state očakávaniu.

Plan môže navrhnúť:

- vrátiť remote objekt ku konfigurácii,
- adoptovať platformovú normalized hodnotu bez zmeny,
- znovu vytvoriť chýbajúci objekt,
- nahradiť objekt pri nekompatibilnej zmene.

Drift musí mať ownership rozhodnutie:

```text
revert remote change
adopt change into code
import/adopt object
remove object from management
repair provider/configuration mismatch
```

## 11. State a plan

Plan používa:

```text
configuration
+ prior state
+ refreshed remote observations
+ provider schemas
= proposed changes
```

Saved plan je viazaný na konkrétny state a configuration context. Ak sa state medzi plan a apply zmení, apply môže odmietnuť stale plan alebo vyžadovať nový plan podľa workflowu.

## 12. Partial apply a state

Apply môže zlyhať po vykonaní časti operácií:

```text
resource A created
resource B created
resource C failed
```

Terraform sa snaží zapísať state pre úspešne dokončené operácie. Nasledujúci plan má vyhodnotiť nový partial stav a pokračovať alebo navrhnúť recovery.

Neopakuj slepo celý external workflow mimo Terraformu, ak už vznikli side effects.

## 13. State commands

Bezpečnejšie inspection príkazy:

```bash
terraform state list
terraform state show <address>
terraform show
terraform output
```

Manipulačné príkazy:

```bash
terraform state mv
terraform state rm
terraform state replace-provider
terraform state pull
terraform state push
```

Manipulačné príkazy menia management metadata, nie vždy remote objekt.

Každá state surgery má mať:

- backup,
- exclusive lock,
- peer review,
- presný source/target address,
- následný plan,
- audit trail.

## 14. `terraform state list`

Zobrazí resource instance addresses v aktuálnom state:

```bash
terraform state list
```

Použitie:

- overenie správneho workspace/backendu,
- nájdenie module paths,
- príprava `state mv`,
- diagnostika missing bindingu.

Výstup nemusí dokazovať, že remote objekt stále existuje alebo je healthy.

## 15. `terraform state show`

```bash
terraform state show 'module.network.aws_subnet.private["a"]'
```

Zobrazuje známu state reprezentáciu konkrétnej instance.

Nie je to vždy live API query v momente spustenia. Pre aktuálny remote stav použi čerstvý refresh/plan podľa bezpečného workflowu.

## 16. `terraform state mv`

Presúva binding medzi resource addresses:

```bash
terraform state mv aws_instance.old aws_instance.new
```

Použitie:

- refactor resource name,
- presun do module,
- zmena instance address.

Preferuj versionované `moved` blocks pre opakovateľné refaktorizácie zdieľanej konfigurácie. Manuálne `state mv` je operatívny zásah viazaný na konkrétny state.

## 17. `terraform state rm`

Odstráni binding zo state bez zmazania remote objektu:

```bash
terraform state rm aws_instance.legacy
```

Po operácii Terraform objekt nespravuje. Ak resource block zostane v konfigurácii, ďalší plan sa môže pokúsiť vytvoriť nový objekt.

Použi iba pri vedomom ownership transfere alebo oprave state modelu.

## 18. `terraform state pull` a `push`

`state pull` načíta aktuálny snapshot:

```bash
terraform state pull > backup.tfstate
```

`state push` manuálne prepíše backend snapshot a je vysoko rizikový.

Pred push:

- zastav všetky applies,
- získaj lock,
- over lineage a serial,
- vytvor backup remote state,
- validuj obsah,
- priprav recovery,
- po push spusti refresh/plan.

Force push používaj iba pri presne diagnostikovanej recovery situácii.

## 19. Manuálna editácia JSON

Priame otvorenie a ručná úprava `terraform.tfstate` je posledná možnosť.

Riziká:

- poškodená schema,
- nesprávny serial/lineage,
- stratené provider metadata,
- citlivé údaje v editor backupoch,
- nesúlad s remote backendom,
- nevratná strata bindingu.

Preferuj:

- `moved` blocks,
- import blocks/commands,
- `terraform state` príkazy,
- provider-supported migrations,
- obnovenie snapshotu.

## 20. State boundaries

Samostatný state vytvára:

- samostatný lock,
- samostatný blast radius,
- samostatné permissions,
- samostatný plan/apply lifecycle,
- explicitné cross-state contracts.

Boundary navrhuj podľa:

- environmentu,
- ownershipu,
- security domain,
- lifecycle cadence,
- failure domain,
- resource count a provider limits.

## 21. Workspaces

CLI workspaces umožňujú viac state instances pre jednu backend configuration.

Nie sú univerzálnou náhradou za:

- samostatné accounts/subscriptions,
- oddelené credentials,
- environment-specific policy,
- odlišné module composition,
- bezpečnostné boundaries.

Použi ich, keď states zdieľajú rovnakú configuration shape a backend governance. Produkčné prostredie nemá byť oddelené od developmentu iba ľahko prehliadnuteľným workspace selectionom bez ďalších controls.

## 22. Cross-state dependencies

Oddelené states môžu zdieľať údaje cez outputs alebo external registry.

Priamy remote-state access vytvára coupling na:

- backend availability,
- state permissions,
- output schema,
- producer apply cadence.

Consumer nemá dostávať širší state access, než potrebuje. Pri citlivých boundaries publikuj explicitný contract do vhodného systému.

## 23. State backup a recovery

Recovery plán má obsahovať:

- backend versioning,
- retention,
- immutable alebo chránené backups,
- restore procedure,
- lineage/serial validation,
- test restore,
- ownera,
- incident audit.

Backup bez pravidelne overeného restore nie je dôveryhodná recovery capability.

Po obnove state vždy porovnaj:

```text
restored state
vs. configuration
vs. remote actual state
```

## 24. State loss

Pri strate state remote infraštruktúra nemusí zmiznúť.

Možnosti recovery:

1. obnoviť backend snapshot,
2. obnoviť lokálny backup,
3. importovať existujúce objekty,
4. rekonštruovať bindings po častiach,
5. vedome odstrániť/recreate infraštruktúru.

Hromadný apply s prázdnym state môže vytvoriť duplicity alebo naraziť na name conflicts.

## 25. State corruption

Symptómy:

- invalid JSON alebo schema,
- provider address mismatch,
- duplicate bindings,
- serial/lineage konflikt,
- state odkazuje na neexistujúce instances,
- backend snapshot je čiastočne zapísaný.

Postup:

1. zastav writes,
2. zachovaj všetky snapshots a logs,
3. identifikuj posledný known-good serial,
4. over remote infraštruktúru,
5. obnov alebo oprav najmenší možný rozsah,
6. spusti read-only inspection a plan,
7. zdokumentuj incident.

## 26. Provider upgrade a state

Provider môže vykonať internal state schema migration.

Riziká:

- downgrade nemusí rozumieť novému state formátu,
- computed/default behavior sa zmení,
- resource identity migration môže zlyhať,
- nový provider navrhne unexpected diff.

Pred významným upgrade zachovaj backend snapshot a testuj plan na reprezentatívnom state.

## 27. Deletion remote objektu mimo Terraformu

Ak operátor zmaže managed objekt manuálne, refresh ho označí ako chýbajúci a plan typicky navrhne recreation.

Pred apply over:

- či deletion bola zámerná,
- či objekt má byť odstránený aj z konfigurácie,
- či recreation nestratí data/identity,
- či dependents zostali konzistentné.

## 28. Anti-patterny

### State commitnutý do Git-u

Môže obsahovať secrets a nepodporuje bezpečný multi-writer model.

### Jeden state pre celú organizáciu

Lock, permissions a blast radius sú neprimerane široké.

### Pravidelný manuálny `state push`

Backend workflow a ownership sú zásadne chybné.

### `state rm` ako oprava každého driftu

Terraform prestane objekt spravovať, ale problém ownershipu zostane.

### Workspace selection podľa manuálnej pamäti

Apply môže zasiahnuť nesprávne prostredie.

### Backup bez restore testu

Počas incidentu sa môže ukázať ako nečitateľný alebo zastaraný.

## 29. Troubleshooting

### Terraform chce vytvoriť objekt, ktorý existuje

State neobsahuje binding alebo používaš nesprávny backend/workspace. Over `state list`, import/adoption plán a remote identity.

### Plan chce zmazať veľa resources

Zastav apply. Over backend configuration, workspace, state lineage, credentials, module source a `for_each` keys.

### State je locked

Over aktívny run a lock owner. Nevykonávaj force unlock, kým nie je potvrdené, že pôvodný writer skončil.

### Provider hlási unsupported state

Over provider version, lock file, upgrade/downgrade históriu a dostupný pre-upgrade snapshot.

### Output obsahuje starú hodnotu

Over posledný apply, refresh, output expression a backend/workspace selection.

## 30. Kontrolné otázky

1. Prečo Terraform potrebuje state?
2. Aký je rozdiel medzi configuration, state a actual remote stavom?
3. Na čo slúžia lineage a serial?
4. Prečo môže state obsahovať secrets?
5. Čo sa stane pri partial apply?
6. Aký je rozdiel medzi `state mv` a remote API mutation?
7. Kedy je `state rm` bezpečný?
8. Ako navrhnúť state boundary?
9. Ako sa obnovuje stratený state?
10. Prečo backup bez restore testu nestačí?

## Glossary impact

Relevantné pojmy: Terraform state, state snapshot, resource binding, lineage, serial, refresh, state surgery, state boundary, local state, CLI workspace, state backup, state recovery, partial apply a cross-state dependency.

## Oficiálna dokumentácia

- [Terraform state](https://developer.hashicorp.com/terraform/language/state)
- [Purpose of Terraform state](https://developer.hashicorp.com/terraform/language/state/purpose)
- [State workspaces](https://developer.hashicorp.com/terraform/language/state/workspaces)
- [Recover state](https://developer.hashicorp.com/terraform/cli/state/recover)
