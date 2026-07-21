# Infrastructure as Code principles

Infrastructure as Code (IaC) je spôsob navrhovania, vytvárania a prevádzky infraštruktúry pomocou versionovaného, automatizovane vyhodnocovaného kódu namiesto nezdokumentovaných manuálnych zásahov.

IaC nie je iba „skript, ktorý vytvorí server“. Je to prevádzkový model, v ktorom deklarácia, review, plán zmeny, vykonanie, evidencia a obnova tvoria jeden riadený lifecycle.

## 1. Aký problém IaC rieši

Manuálne vytváraná infraštruktúra typicky trpí problémami:

- nie je presne reprodukovateľná,
- skutočný stav sa líši od dokumentácie,
- zmeny nemajú auditovateľný diff,
- rollback závisí od pamäti operátora,
- prostredia sa postupne rozchádzajú,
- rovnaký krok vykonajú rôzni ľudia odlišne,
- ownership a schvaľovanie sú nejasné,
- incident recovery je pomalé.

IaC presúva infraštruktúrnu zmenu do podobného modelu, aký sa používa pri source code:

```text
change proposal
→ review
→ validation
→ plan
→ approval/policy
→ apply
→ verification
→ audit
```

## 2. Deklaratívny a imperatívny prístup

### Imperatívny prístup

Popisuje jednotlivé kroky:

```text
vytvor sieť
vytvor subnet
vytvor VM
pripoj disk
nastav firewall
```

Výsledok závisí od poradia, predchádzajúceho stavu a správneho ošetrenia každej výnimky.

### Deklaratívny prístup

Popisuje požadovaný stav:

```hcl
resource "example_network" "main" {
  cidr = "10.20.0.0/16"
}
```

Engine porovná deklaráciu so známym skutočným stavom a zostaví akčný plán.

Deklaratívnosť neznamená, že poradie neexistuje. Znamená, že dependency graph a provider určia poradie z objektových vzťahov namiesto ručne písanej sekvencie príkazov.

## 3. Desired state a reconciliation

Základný model:

```text
desired configuration
        +
known current state
        +
provider observations
        ↓
execution plan
        ↓
remote system mutations
        ↓
new observed state
```

Reconciliation sa snaží zmenšiť rozdiel medzi desired a actual state.

Nie každý IaC nástroj je permanentný controller. Terraform typicky vykonáva reconciliation počas explicitného `plan` a `apply`, zatiaľ čo Kubernetes controller pracuje kontinuálne. Mentálny model desired state je však podobný.

## 4. Idempotencia

Operácia je idempotentná, keď opakované vykonanie nad už dosiahnutým stavom nevytvorí ďalšiu zmenu.

```text
apply #1 → vytvorí infraštruktúru
apply #2 → no changes
```

IaC systém potrebuje idempotenciu na bezpečné retries, recovery a pravidelné overovanie driftu.

Idempotencia nie je absolútna vlastnosť celého nástroja. Môže ju porušiť:

- nestabilný provider,
- nondeterministická expression,
- timestamp použitý v resource argumente,
- mutable external dependency,
- provisioner s nevratným side effectom,
- API, ktoré nevracia konzistentný stav.

## 5. Reprodukovateľnosť

Reprodukovateľná infraštruktúra vyžaduje viac než uložený `.tf` súbor.

Treba verzionovať alebo presne identifikovať:

- Terraform CLI compatibility,
- provider source a version constraints,
- dependency lock file,
- module versions,
- policy a pipeline templates,
- artifacty použité infraštruktúrou,
- external configuration inputs,
- backend a workspace/state identity.

Mutable referencia ako `latest`, neobmedzený provider version range alebo branch bez commit SHA oslabuje reprodukovateľnosť.

## 6. Version control ako change ledger

IaC patrí do version control systému.

Commit a merge request poskytujú:

- návrh zmeny,
- diff,
- authora,
- review diskusiu,
- väzbu na issue/change request,
- pipeline evidence,
- históriu rozhodnutí.

Version control však neobsahuje runtime state ani secrets. Repository nie je backend ani secret manager.

## 7. Plan nie je garancia

Execution plan je predikcia zmien na základe:

- konfigurácie,
- aktuálneho state snapshotu,
- refresh výsledkov,
- provider logiky,
- permissions a API odpovedí.

Medzi `plan` a `apply` sa môže remote systém zmeniť. Môžu sa zmeniť aj credentials, quotas, policy alebo dostupnosť dependency.

Preto treba:

- aplikovať uložený a schválený plan tam, kde workflow podporuje saved plans,
- minimalizovať čas medzi planom a apply,
- serializovať konfliktujúce applies,
- pred apply overiť freshness evidence,
- po apply vykonať runtime verification.

## 8. Drift

Drift je rozdiel medzi stavom očakávaným konfiguráciou/state a stavom remote objektu.

Vzniká napríklad:

- manuálnou zmenou v konzole,
- externým controllerom,
- automatickou platformovou úpravou,
- incidentným break-glass zásahom,
- neúplne importovaným objektom,
- provider normalization behaviorom.

Drift detection musí byť pravidelný a action-oriented:

```text
scheduled plan
→ classify drift
→ adopt, revert alebo repair
→ zachytiť rozhodnutie v code/history
```

Permanentné ignorovanie driftu cez lifecycle výnimky vytvára neviditeľný ownership dlh.

## 9. State ako mapovanie identity

Deklarácia sama nevie, ktorý remote objekt zodpovedá resource adrese.

State typicky udržiava mapovanie:

```text
module.network.example_subnet.app["az-a"]
→ remote object ID subnet-123
```

State je kritický operational asset. Potrebuje:

- secure storage,
- access control,
- locking,
- encryption,
- versioning/backups,
- recovery test,
- jasný ownership.

## 10. Immutable a mutable infraštruktúra

### Mutable model

Existujúci objekt sa upravuje in-place.

Výhody:

- menšie náklady na replacement,
- vhodné pre stateful alebo drahé resources.

Riziká:

- kumulatívny drift,
- zložitejší rollback,
- hidden history zmien.

### Immutable model

Namiesto zásadnej úpravy sa vytvorí nový objekt alebo fleet a traffic/ownership sa presunie.

Výhody:

- jednoduchšia reprodukcia,
- menší configuration drift,
- jasnejší rollback target.

Riziká:

- vyššia dočasná capacity,
- data migration,
- identity a DNS/routing koordinácia.

IaC riešenie často kombinuje oba modely podľa typu resource.

## 11. Scope a blast radius

Jedna obrovská state boundary pre celú organizáciu prináša:

- dlhé plány,
- široké permissions,
- veľký lock contention,
- rozsiahly blast radius,
- komplikovaný ownership.

Príliš veľa malých states prináša:

- veľa cross-state contracts,
- duplikáciu,
- zložité dependency orchestration,
- viac backendov a pipelines.

Boundary navrhuj podľa:

- ownershipu,
- lifecycle cadence,
- security boundary,
- failure domain,
- environmentu,
- provider/API limits,
- potreby samostatného recovery.

## 12. Prostredia

Environment nie je iba premenná `environment = "prod"`.

Odlišuje sa:

- state identity,
- credentials,
- account/subscription/project,
- network boundary,
- policy,
- quotas,
- data sensitivity,
- approval a deployment workflow.

Produkcia nemá zdieľať rovnaké credentials alebo nekontrolovaný state s developmentom.

## 13. Modulárnosť a interfaces

Modul má byť komponent s explicitným kontraktom:

- inputs,
- outputs,
- required providers,
- compatibility/version policy,
- assumptions,
- lifecycle a ownership.

Modul nie je iba priečinok na skrátenie kódu.

Príliš generický modul vytvára:

- množstvo flags,
- nejasné behavior kombinácie,
- náročné testovanie,
- coupling všetkých consumers.

Preferuj modules reprezentujúce stabilnú capability alebo platform boundary.

## 14. Secrets a citlivé údaje

Do IaC source nepatria:

- passwords,
- private keys,
- API tokens,
- production certificates,
- citlivé customer values.

Aj hodnota označená `sensitive` môže byť uložená v state. `sensitive` primárne obmedzuje zobrazenie, nie storage encryption.

Bezpečný model používa:

- workload identity,
- external secret manager,
- short-lived credentials,
- minimum scope,
- secure backend,
- redaction a log controls.

## 15. Testing a validation vrstvy

IaC pipeline môže obsahovať:

```text
format
→ syntax/init validation
→ static analysis
→ security/policy checks
→ unit/module tests
→ plan
→ plan policy
→ approval
→ apply
→ post-deployment verification
```

Každá vrstva rieši iné riziko.

`terraform validate` nepotvrdzuje, že:

- credentials fungujú,
- quota stačí,
- policy dovolí zmenu,
- resource bude runtime healthy,
- architecture spĺňa business requirement.

## 16. Policy as Code

Policy as Code automatizuje pravidlá ako:

- povolené regions,
- povinné tags,
- zakázané public endpoints,
- encryption requirements,
- limit blast radiusu,
- povolené provider/module sources,
- approval podľa risk classification.

Policy má byť versionovaná, testovaná a vysvetliteľná. Nejasný blokujúci rule bez remediation guidance vedie k bypassom.

## 17. Change management

IaC nemení potrebu change managementu. Zlepšuje jeho evidence.

Dobrý change record viaže:

- source commit,
- resolved dependencies,
- plan,
- policy výsledky,
- approvals,
- apply identity,
- state version,
- post-apply verification,
- recovery postup.

## 18. Recovery

Pred apply treba vedieť:

- čo možno bezpečne rollbacknúť,
- čo vyžaduje roll-forward,
- ktoré resources sa pri zmene nahradia,
- či replacement stratí dáta alebo identity,
- ako obnoviť state,
- ako obnoviť remote data,
- kde je last known good konfigurácia.

Rollback Git commitu sám osebe nevráti remote infraštruktúru ani dáta.

## 19. Anti-patterny

### ClickOps ako primárny model

Kód prestáva byť authoritative source a drift rastie.

### Automatický apply každého commitu bez risk policy

Malá syntaktická zmena môže mať veľký runtime blast radius.

### Jedna admin identita pre všetky pipelines

Porušenie jedného workflowu kompromituje všetky environments.

### State v Git repository

State môže obsahovať secrets a nepodporuje bezpečnú concurrency.

### Copy-paste namiesto versionovaných modules

Fixy a policy sa rozchádzajú medzi prostrediami.

### Provisioners ako univerzálny escape hatch

Imperatívne side effects sú ťažko idempotentné, pozorovateľné a obnoviteľné.

### `ignore_changes` na všetko, čo driftuje

Skryje ownership konflikt namiesto jeho vyriešenia.

## 20. Rozhodovací rámec

1. Aký desired state a ownership boundary spravujeme?
2. Ktorý systém je authoritative source?
3. Aký state a identity model potrebujeme?
4. Aký je blast radius jedného apply?
5. Ktoré dependencies musia byť immutable alebo pinned?
6. Ktoré validácie musia prebehnúť pred apply?
7. Ktoré zmeny vyžadujú approval?
8. Ako detegujeme drift?
9. Ako obnovíme state a remote data?
10. Ktoré operácie sú rollback a ktoré roll-forward?

## 21. Kontrolné otázky

1. Aký je rozdiel medzi deklaratívnym a imperatívnym IaC?
2. Prečo desired state neznamená automaticky kontinuálnu reconciliation?
3. Čo môže porušiť idempotenciu?
4. Prečo plan nie je absolútna garancia apply výsledku?
5. Aký je rozdiel medzi configuration driftom a state stratou?
6. Ako navrhnúť state boundary podľa blast radiusu?
7. Prečo `sensitive` neznamená encrypted?
8. Kedy je vhodný immutable a kedy mutable model?
9. Aké evidence má zachovať IaC change workflow?
10. Prečo návrat Git commitu nemusí byť infra rollback?

## Glossary impact

Relevantné pojmy: Infrastructure as Code, desired state, reconciliation, idempotencia, drift, authoritative source, state boundary, blast radius, immutable infrastructure, mutable infrastructure, Policy as Code, ClickOps a plan/apply lifecycle.

## Oficiálna dokumentácia

- [Terraform language overview](https://developer.hashicorp.com/terraform/language)
- [Terraform style guide](https://developer.hashicorp.com/terraform/language/style)
- [Terraform state](https://developer.hashicorp.com/terraform/language/state)
