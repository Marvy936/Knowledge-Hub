# Terraform state

Terraform state je persistentný identity a observation model, ktorý spája Terraform resource instances s konkrétnymi remote objektmi. Nie je to desired configuration ani obyčajná cache. Bez správneho state-u Terraform nevie, ktorý remote objekt patrí ku ktorej resource address-e, aký snapshot bol naposledy autoritatívne zapísaný a ako má bezpečne pokračovať po partial alebo neznámom výsledku.

Dominantný model tejto kapitoly je:

```text
configuration address a provider target
→ resource binding na remote object ID
→ versionovaný state snapshot
→ refresh a plan nad desired/known/actual state
→ remote mutation
→ nový snapshot alebo unknown state-write outcome
→ runtime a binding verification
→ recovery, surgery alebo ďalší reconciled plan
```

State troubleshooting preto nezačína otázkou „čo je v JSON-e“, ale otázkou: **ktorá address, provider identity, remote object, lineage a serial tvoria subject konkrétneho rozhodnutia?**

## 1. Atlas scenár: produkčná sieť ako state subject

Atlas Payments spravuje produkčnú VPC cez root module `payments-prod`. Resource instance má adresu:

```text
module.network.aws_vpc.main
```

AWS pozná objekt ako:

```text
account 7711 / region eu-central-1 / vpc-0a42
```

State uchováva binding:

```text
module.network.aws_vpc.main
+ provider aws.production
→ account 7711 / eu-central-1 / vpc-0a42
```

Tento binding je dôležitejší než podobnosť názvov. Ak zmizne alebo sa načíta iný backend/workspace, VPC môže stále existovať a obsluhovať produkciu, ale Terraform ju pri tejto address-e neuvidí. Nasledujúci plan potom môže navrhnúť duplicate create alebo deštrukciu úplne iného objektu.

## 2. Desired, known a actual state

Pri každom plan-e odlišuj tri vrstvy:

```text
desired state = configuration + resolved inputs
known state   = bindings a attributes v konkrétnom snapshot-e
actual state  = objekty a hodnoty pozorované cez provider API
```

Plan vzniká porovnaním všetkých troch:

```text
configuration C42
+ state lineage L-prod / serial 208
+ provider reads v account-e 7711
→ saved plan P209
```

Ak sa vrstvy rozídu, rozdiel nemusí znamenať obyčajný remote drift. Môže ísť o nesprávny backend, stratený binding, zmenu instance key, provider normalization, partial apply alebo manuálny ownership transfer. Správna náprava závisí od mechanizmu.

## 3. Resource binding ako ownership record

Resource binding prepája:

- úplnú resource instance address-u vrátane module pathu a `for_each` key alebo `count` indexu;
- provider configuration address a target identity;
- provider-specific remote object ID;
- známe attributes a schema metadata.

Príklad:

```text
module.network.aws_subnet.private["az-a"]
→ provider aws.production
→ subnet-0f18
```

State binding hovorí, ktorý objekt Terraform spravuje. Nehovorí, že objekt je zdravý, že má správny traffic ani že ho nespravuje aj iný writer. Ownership musí byť potvrdený configuration contractom a organizačnou policy.

Ak tú istú remote identitu spravujú dve resource addresses alebo dva states, oba workflows môžu striedavo prepisovať hodnoty alebo objekt odstrániť. Duplicate ownership je state-model incident, nie iba nepríjemný diff.

## 4. Snapshot, lineage a serial

State sa vyvíja cez snapshots. Snapshot typicky obsahuje:

- resource bindings;
- známe attributes a outputs;
- provider associations;
- Terraform/state format metadata;
- **lineage**;
- **serial**.

Lineage rozlišuje nezávislé state histórie. Serial monotónne identifikuje novší snapshot v jednej lineage:

```text
L-prod / serial 208
→ apply alebo state mutation
→ L-prod / serial 209
```

Vyšší serial z inej lineage nie je automaticky „novší produkčný state“. Recovery musí overiť obidve identity aj environment/backend subject. Prepísanie snapshotu iba podľa času súboru môže obnoviť nesúvisiaci environment.

State formát je interný implementation detail. Preferuj stabilné CLI/API operácie a backend snapshots pred vlastným parserom alebo ručnou editáciou JSON-u.

## 5. Refresh mení poznanie, nie intent

Provider read operácie aktualizujú observation model:

```text
prior state attributes
→ provider Read(account, region, remote ID)
→ refreshed actual attributes
```

Refresh môže odhaliť:

- manuálne zmenený firewall rule;
- chýbajúci remote objekt;
- platformou normalizovanú hodnotu;
- attribute zmenený iným controllerom;
- objekt v inom stave, než evidoval predchádzajúci snapshot.

Refresh nemení configuration intent. Až plan rozhodne, či bude rozdiel vrátený, adoptovaný, ignorovaný podľa explicitného ownership contractu alebo riešený importom či state repair-om.

## 6. State a saved plan freshness

Saved plan je viazaný minimálne na:

```text
configuration a resolved inputs
+ provider/module selections
+ backend/workspace identity
+ lineage a prior serial
+ refresh observations
+ target identity
```

Approval nad planom P209 schvaľuje práve tento subject. Ak medzi planom a apply vznikne serial 209 z iného runu, pôvodný plan už nereprezentuje aktuálny state. Bezpečný workflow ho odmietne a vytvorí nový plan.

Apply, ktorý namiesto schváleného saved planu potichu prepočíta nový plan, vykonáva iné rozhodnutie.

## 7. Apply nie je jedna state transakcia

Remote APIs a state storage netvoria jednu ACID transakciu. Typický operation path je:

```text
read snapshot S208
→ provider Create/Update/Delete
→ remote API dokončí alebo pokračuje asynchrónne
→ provider vráti remote ID a attributes
→ Terraform pripraví S209
→ backend zapíše S209
```

Failure môže vzniknúť medzi ľubovoľnými krokmi. Kritický stav je:

```text
remote mutation možno uspela
+ state write outcome je unknown alebo failed
```

Slepý retry potom môže vytvoriť duplicate object alebo zopakovať nevratný side effect. Recovery najprv pozoruje backend aj remote platformu.

## 8. Worked failure: remote create uspel, binding sa nezapísal

Atlas pridával produkčný NAT gateway. Provider odoslal create request a AWS vytvoril `nat-0913`. Pri zápise snapshotu S209 vypadla sieť medzi runnerom a backendom.

```text
configuration obsahuje NAT
→ remote API vytvorí nat-0913
→ state write connection reset
→ pipeline skončí failed
→ operátor spustí apply znova
→ plan navrhuje ďalší NAT
```

Príčina nie je neúspešný remote create, ale **stratená alebo nepotvrdená state binding transition**.

Správny recovery path:

1. zastaviť ďalších writers;
2. zachovať provider request ID, logs a lokálny recovery snapshot;
3. overiť latest backend lineage/serial;
4. vyhľadať remote objekt podľa request metadata, tags a account/region identity;
5. ak binding chýba, importovať alebo obnoviť správny snapshot;
6. vytvoriť čerstvý plan;
7. overiť, že existuje jediný NAT a správne route bindings.

## 9. Worked failure: restore vrátil starý binding

Po chybnej state surgery tím obnovil snapshot S204, hoci produkcia už bola na S208. Medzičasom sa subnet presunul z indexovej address-y na stabilný key.

```text
S204 obsahuje subnet[0] → subnet-old
S208 obsahuje subnet["az-a"] → subnet-current
→ restore S204
→ plan interpretuje current address ako nový objekt
→ navrhne create/destroy proti živej sieti
```

Backup bol čitateľný, ale nebol kompatibilný s aktuálnou configuration a remote realitou. Restore capability preto musí overovať lineage, serial, address migrations a actual inventory, nie iba úspešné načítanie JSON-u.

## 10. State inspection verzus state mutation

Inspection príkazy pomáhajú identifikovať subject:

```bash
terraform state list
terraform state show 'module.network.aws_subnet.private["az-a"]'
terraform show
terraform output
```

`state show` je známa state reprezentácia, nie záruka live health. Pri aktuálnom remote rozhodnutí použi bezpečný refresh/plan a platformové observation points.

Mutation príkazy menia management metadata:

```bash
terraform state mv
terraform state rm
terraform state replace-provider
terraform state pull
terraform state push
```

State mutation nemusí meniť remote objekt. Práve preto môže vytvoriť nebezpečný rozdiel medzi management modelom a runtime realitou.

## 11. State surgery protocol

Každá state surgery má mať tento lifecycle:

```text
freeze writers
→ identifikuj backend/workspace/lineage/serial
→ vytvor a chráň backup
→ inventory source/destination addresses a remote IDs
→ vykonaj najmenšiu mutation
→ čerstvý refresh/plan
→ remote a runtime verification
→ audit a odstránenie dočasného accessu
```

### `state mv`

Presúva binding medzi addresses bez remote create/delete:

```bash
terraform state mv aws_instance.old aws_instance.new
```

Pre versionovaný refaktoring preferuj `moved` block. Manuálny `state mv` je environment-specific zásah a pri viacerých consumers sa ľahko vykoná nekonzistentne.

### `state rm`

Odstráni binding, ale ponechá remote objekt:

```bash
terraform state rm aws_instance.legacy
```

Je legitímny pri explicitnom ownership transfere alebo oprave chybného bindingu. Ak configuration block zostane, ďalší plan môže navrhnúť duplicate create.

### `state pull` a `state push`

`state pull` môže vytvoriť recovery snapshot. `state push` manuálne prepisuje backend state a je posledná možnosť. Pred push musí byť overená lineage, serial, target backend, exclusive access a rollback snapshot. Force bypass nesmie slúžiť ako bežný workflow.

## 12. State boundaries a blast radius

Jeden state definuje spoločný:

- lock a writer queue;
- plan/apply lifecycle;
- apply permission scope;
- recovery unit;
- failure blast radius;
- cross-resource dependency graph.

Boundary navrhuj podľa ownershipu, environmentu, security domain, lifecycle cadence, failure domainu a recovery nezávislosti.

Príliš veľký state vytvára široké permissions, dlhý critical path a neprimerané incidenty. Príliš malé states vytvárajú množstvo cross-state contracts a orchestrácie.

Module boundary nie je automaticky state boundary. Samostatný state vzniká až samostatným root module/backend lifecycle-om.

## 13. Workspaces a environment identity

CLI workspace vyberá state instance pod jednou backend configuration. Je vhodný len vtedy, keď environments zdieľajú rovnaký configuration shape a governance model.

Produkciu nesmie chrániť iba názov workspace-u zapamätaný operátorom. Apply job má pred mutation overiť:

```text
backend host/bucket
state key alebo workspace
lineage
cloud account/subscription
region
apply identity
expected environment marker
```

Zlý workspace je schopný vytvoriť plan, ktorý je syntakticky platný, ale mieri na nesprávny state subject.

## 14. Cross-state contracts

Oddelené states si môžu publikovať úzke outputs cez parameter store, configuration registry, DNS/service discovery alebo iný explicitný contract.

Priamy remote-state access viaže consumera na:

- backend availability a permissions;
- producer output schema;
- producer apply cadence;
- potenciálne širší snapshot access, než potrebuje.

Silná security boundary má publikovať iba potrebnú hodnotu s ownerom, compatibility a freshness semantics, nie poskytovať všeobecné čítanie celého state-u.

## 15. Secrets a state access

State môže obsahovať passwords, private keys, tokens, connection strings a provider-returned sensitive attributes. `sensitive = true` obmedzuje presentation, nie storage.

State storage a recovery copies preto potrebujú:

- encryption in transit a at rest;
- narrowly scoped read/write identities;
- audit;
- versioning a retention;
- ochranu backupov a plan artifacts;
- kontrolovaný secret rotation a deletion lifecycle.

State sa nesmie publikovať ako bežný CI artifact ani pripájať k ticketu bez redakcie a access kontroly.

## 16. Backup a restore ako overiteľná capability

Dôveryhodný recovery model obsahuje:

```text
versionované snapshots
→ oddelená alebo chránená backup vrstva podľa rizika
→ restore do izolovaného test targetu
→ lineage/serial a schema validation
→ porovnanie s configuration
→ read-only remote reconciliation plan
→ dokumentovaný recovery verdict
```

Backup v rovnakom účte nemusí chrániť pred account compromise, destructive adminom alebo key loss. Snapshot zašifrovaný zmazaným KMS keyom nie je recovery asset.

## 17. Kauzálny diagnostický walkthrough

Symptom: po refaktoringu root module plánuje zničiť 84 produkčných resources, hoci MR mal iba premiestniť súbory a module calls.

### Krok 1 — stabilizuj subject

```text
configuration commit C47
backend/key payments/prod
workspace default
lineage L-prod / serial 208
provider aws.production / account 7711
saved plan digest P209
```

### Krok 2 — konkurenčné hypotézy

```text
H1: pipeline načítala nesprávny backend alebo workspace
H2: resource addresses sa zmenili bez moved mappings
H3: for_each keys alebo count indexy sa zmenili
H4: provider upgrade zmenil replacement behavior
H5: state snapshot bol obnovený alebo prepísaný staršou verziou
H6: remote objects boli odstránené mimo Terraformu
H7: plan používa inú provider target identity
```

### Krok 3 — diskriminačné observation points

- backend config, workspace a lineage testujú H1/H5;
- before/after addresses a moved chain testujú H2;
- instance key inventory testuje H3;
- lock file a provider schema diff testujú H4;
- cloud inventory a provider reads testujú H6;
- account/region/caller audit testuje H7.

Atlas zistí, že resource addresses sa presunuli do `module.platform`, ale `moved` blocks chýbajú. Remote IDs, provider target aj state sú správne; H2 vysvetľuje deštruktívny plan.

### Krok 4 — containment a recovery

Apply sa zablokuje. Tím pridá versionované `moved` mappings a nevykoná manuálne `state mv` iba v produkcii, pretože rovnaký upgrade musia bezpečne vykonať aj stage a disaster-recovery states.

### Krok 5 — over pôvodný outcome

Nový plan musí ukázať address moves bez remote replacementu. Po apply sa overí:

- rovnaký remote object inventory;
- nový state serial;
- správne resource addresses a bindings;
- nezmenený traffic a health;
- žiadne orphaned alebo duplicate resources.

### Krok 6 — skorší control

Finding sa mení na upgrade fixture test nad reprezentatívnym state-om, policy pre unexpected destroy/replace a povinný address-migration manifest pri refaktoringu.

## 18. Diagnostický runbook

1. Identifikuj backend, workspace, lineage, serial a configuration revision.
2. Zostav mapu resource address → provider target → remote object ID.
3. Oddeľ desired, known a actual state.
4. Over latest snapshot a lock/writer timeline.
5. Klasifikuj problém ako binding loss, wrong state subject, remote drift, address/key change, provider migration alebo unknown write.
6. Zastav ďalších writers pri nejasnej integrite.
7. Preferuj refresh/plan a minimálnu versionovanú opravu pred force pushom.
8. Pri surgery zachovaj backup a exact mapping.
9. Over remote inventory, runtime outcome a nový snapshot.
10. Zmeň incident na boundary, migration, backup alebo writer-control zlepšenie.

## 19. Referenčné pravidlá

- State je identity a observation model, nie desired configuration.
- Resource address a remote ID sú odlišné identity spojené bindingom.
- Lineage a serial sa musia posudzovať spolu s environment/backend subjectom.
- Saved plan je viazaný na konkrétny prior state.
- Remote mutation a state write nie sú jedna transakcia.
- Unknown state-write outcome sa nereparuje slepým retry.
- State surgery mení management metadata a potrebuje lock, backup a následný plan.
- Module nie je automaticky state boundary.
- Workspaces samy osebe nie sú production security isolation.
- Backup je dôveryhodný až po testovanom restore a reconciliation.
- Sensitive presentation neznamená, že state secret neobsahuje.

## 20. Časté omyly

### „State je iba cache, môžeme ho zmazať“

Remote infraštruktúra môže zostať, ale bindings sa stratia a plan môže vytvoriť duplicity alebo deštrukcie.

### „Vyšší serial je vždy správny“

Musí patriť správnej lineage, backendu a environmentu.

### „`state rm` odstráni infraštruktúru“

Odstráni management binding, nie remote objekt.

### „Backup sa dá obnoviť, lebo súbor existuje“

Môže byť starý, z inej lineage, nekompatibilný so schema alebo nezašifrovateľný po strate keya.

### „Plan po restore môžeme automaticky applynuť“

Najprv treba porovnať configuration, restored state a actual remote inventory.

## Zhrnutie

Dôveryhodný Terraform state lifecycle je:

```text
stable configuration address a provider target
→ explicitný remote binding
→ versionovaný lineage/serial snapshot
→ refreshed plan subject
→ remote mutation
→ potvrdený snapshot transition
→ runtime a binding verification
→ controlled recovery alebo migration
```

State incident sa rieši rekonštrukciou identity a timeline-u, nie náhodnou editáciou JSON-u. Bez správneho bindingu a snapshot transitionu nemôže byť ďalší plan považovaný za bezpečný.

## Oficiálna dokumentácia

- [Terraform state](https://developer.hashicorp.com/terraform/language/state)
- [Purpose of Terraform state](https://developer.hashicorp.com/terraform/language/state/purpose)
- [State workspaces](https://developer.hashicorp.com/terraform/language/state/workspaces)
- [Recover state](https://developer.hashicorp.com/terraform/cli/state/recover)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Expressions a dependency graph](expressions-and-dependency-graph.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Remote backend a state locking →](remote-backend-and-state-locking.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
