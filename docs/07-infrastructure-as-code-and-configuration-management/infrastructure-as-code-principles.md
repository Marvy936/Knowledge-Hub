# Infrastructure as Code principles

Infrastructure as Code (IaC) je prevádzkový model, v ktorom sa infraštruktúrny desired state, jeho zmeny, vyhodnotenie, vykonanie a obnova riadia versionovaným kódom a automatizovaným change-control workflowom. IaC nie je iba skript na vytvorenie servera. Je to spôsob, ako prepojiť návrh, review, plán, policy, identity, remote mutation, runtime verification a audit do jedného reprodukovateľného lifecycle.

## 1. Aký problém IaC rieši

Manuálne spravovaná infraštruktúra typicky nemá spoľahlivý answer na otázky:

- **Čo má existovať?** Dokumentácia a skutočný stav sa môžu rozchádzať.
- **Kto a prečo to zmenil?** Konzolový zásah nemusí mať review, diff ani change record.
- **Aký presný vstup zmenu vytvoril?** Tool versions, credentials a manuálne parametre sa často neevidujú.
- **Dá sa prostredie zopakovať?** Rovnaký postup môžu dvaja operátori vykonať odlišne.
- **Ako sa zistí drift?** Bez authoritative deklarácie nie je jasné, čo je odchýlka a čo schválený stav.
- **Ako sa zmena obnoví?** Rollback závisí od ľudskej pamäti a skrytých side effects.

IaC vytvára riadený tok:

```text
change proposal
→ review
→ validation
→ plan
→ risk/policy decision
→ apply
→ runtime verification
→ state a evidence update
→ drift/recovery lifecycle
```

## 2. Mental model: tri stavy

Pri IaC treba rozlišovať tri odlišné stavy:

- **Desired state —** stav deklarovaný v konfigurácii a schválených vstupoch.
- **Known state —** stav, ktorý nástroj eviduje vo svojom state alebo inventory modeli.
- **Actual remote state —** stav, ktorý reálne existuje v cloud API, hypervisore, sieti alebo inom riadenom systéme.

```text
desired configuration
        +
known state bindings
        +
provider observations
        ↓
proposed execution plan
        ↓
remote mutations
        ↓
new actual state
        +
updated known state
```

Tieto tri vrstvy sa môžu rozísť. Configuration môže požadovať resource, state môže obsahovať jeho staré ID a remote API môže objekt už nepoznať. Správna diagnostika najprv určí, ktorá vrstva je nepravdivá alebo neaktuálna.

## 3. Deklaratívny verzus imperatívny prístup

Imperatívny postup predpisuje sekvenciu operácií:

```text
vytvor sieť
→ vytvor subnet
→ vytvor VM
→ pripoj disk
→ nastav firewall
```

Výsledok závisí od poradia, počiatočného stavu a správneho ošetrenia každej partial failure.

Deklaratívny model opisuje požadovaný objektový stav:

```hcl
resource "example_network" "main" {
  cidr = "10.20.0.0/16"
}
```

Engine a provider odvodia potrebné operácie z rozdielu medzi desired, known a observed state. Deklaratívnosť neodstraňuje poradie ani side effects. Presúva ich do dependency graphu, provider logiky a lifecycle pravidiel.

Imperatívne kroky zostávajú legitímne pre jednorazové procedúry, recovery alebo orchestráciu, ale musia mať explicitnú idempotenciu, retry a audit semantics.

## 4. Authoritative source a ownership

IaC funguje iba vtedy, keď je jasné, ktorý systém je oprávnený meniť konkrétny atribút.

Príklad ownership konfliktu:

```text
Terraform spravuje firewall rule
+ operátor ju mení v konzole
+ security controller ju automaticky prepisuje
→ tri writery, neurčitý desired state
```

Pre každý mutable attribute definuj:

- authoritative source,
- write identity,
- povolené emergency zásahy,
- spôsob detekcie a reconciliation driftu,
- ownership pri shared resources.

IaC repository je authoritative iba pre deklaráciu. Remote state, secrets a runtime health zostávajú v špecializovaných systémoch.

## 5. Reconciliation

Reconciliation je proces znižovania rozdielu medzi desired a actual state. Nie každý nástroj reconciliuje kontinuálne.

- **Terraform —** typicky vykonáva reconciliation počas explicitného `plan` a `apply`.
- **Kubernetes controller —** vyhodnocuje desired a actual state opakovane.
- **Ansible —** vykoná zvolený playbook proti inventory a potom skončí.

To ovplyvňuje drift latency. Ak sa Terraform pipeline spustí iba pri commite, manuálna remote zmena môže zostať neodhalená celé týždne. Scheduled plan alebo continuous validation dopĺňa chýbajúcu periodickú kontrolu.

## 6. Idempotencia, convergence a reproducibility

Tieto pojmy nie sú synonymá.

- **Idempotencia —** opakovanie rovnakej operácie nad dosiahnutým stavom nevytvorí ďalšiu zmenu.
- **Convergence —** opakované vykonávanie približuje systém k desired state.
- **Reproducibility —** rovnaké explicitné vstupy vytvoria porovnateľný výsledok v inom čase alebo prostredí.

```text
apply #1 → vytvorí resource
apply #2 → no changes
```

Idempotenciu môže porušiť:

- timestamp alebo náhodná hodnota v managed argumente,
- provider s nestabilnou normalizáciou,
- mutable module alebo image tag,
- provisioner s nevratným side effectom,
- API, ktoré vracia hodnoty v nekanonickom poradí,
- viac writerov nad rovnakým atribútom.

Reproducibility navyše vyžaduje pinované toolchain, providers, modules, policies a artifacts.

## 7. Configuration a resolved inputs

Samotný `.tf` alebo YAML súbor nie je úplný vstup. Výsledok môže závisieť od:

- CLI a provider verzie,
- dependency lock file,
- module source a revision,
- variables a environment variables,
- backend identity,
- workspace/state identity,
- credentials a account/region contextu,
- external data sources,
- policy a pipeline templates,
- image alebo package digestov.

Dôveryhodný workflow uchová resolved input manifest alebo aspoň umožní spätne zostaviť, s čím bol plan vytvorený.

## 8. Plan ako predikcia, nie garancia

Plan je predikcia nad konkrétnym subjectom:

```text
configuration revision
+ resolved dependencies
+ variable set
+ state snapshot/version
+ refresh observations
+ provider versions
+ identity a target context
```

Plan môže zostať neplatný, keď sa zmení:

- configuration alebo input,
- state serial,
- remote object,
- provider alebo policy,
- account permissions,
- quota,
- external dependency,
- target environment.

Preto musí mať plan:

- identity a checksum,
- subject metadata,
- freshness pravidlá,
- schválený risk verdict,
- kontrolovaný transfer do apply jobu.

Apply nového implicitne prepočítaného planu nie je vykonanie pôvodne schváleného rozhodnutia.

## 9. Apply nie je transakcia

Infraštruktúrne API zvyčajne neposkytujú jednu ACID transakciu pre celý graph. Apply môže skončiť po tom, čo:

- časť resources vznikla,
- iná časť zlyhala,
- remote operácia pokračuje asynchrónne,
- state update sa nepodaril,
- provider stratil spojenie po úspešnej remote mutation,
- timeout nastal pred konečným stavom.

Výsledkom môže byť partial state. Bezpečný workflow potrebuje:

1. zachovať logs a apply evidence,
2. znovu načítať state a remote observations,
3. odlíšiť neúspešný request od neznámeho výsledku,
4. vytvoriť nový plan,
5. rozhodnúť medzi retry, repair, import, rollback a roll-forward,
6. overiť runtime outcome.

Slepé opakovanie apply môže pri nejasnej idempotencii vytvoriť duplicitný objekt alebo side effect.

## 10. State ako identity binding

State nie je iba cache. Udržiava väzbu medzi resource adresou a remote identitou:

```text
module.network.example_subnet.app["az-a"]
→ subnet-123
```

Môže obsahovať:

- remote IDs,
- posledné známe atribúty,
- dependencies,
- sensitive hodnoty,
- lineage a serial,
- provider metadata.

State potrebuje secure storage, locking, versioning, backup, audit a testovaný restore. Strata state nemusí zmazať remote infraštruktúru, ale nástroj stratí identity bindings a môže navrhnúť duplicitné vytvorenie alebo deštrukciu.

## 11. State boundary a blast radius

Jedna state boundary určuje:

- čo sa plánuje a zamyká spolu,
- aké permissions potrebuje apply identity,
- aký rozsah zasiahne chybná konfigurácia,
- kto vlastní zmenu a recovery,
- aký veľký je dependency graph.

Príliš veľký state vytvára široký blast radius, dlhé plány a lock contention. Príliš malé states vytvárajú množstvo cross-state contracts a orchestrácie.

Boundary navrhuj podľa:

- ownershipu,
- lifecycle cadence,
- environmentu a security boundary,
- failure domainu,
- provider/API limitov,
- citlivosti dát,
- potreby nezávislého recovery.

State boundary nemá byť určená iba štruktúrou repository priečinkov.

## 12. Environment isolation

Environment nie je iba variable `environment = "prod"`. Produkcia má mať samostatnú identitu a control boundary:

- account/subscription/project,
- state a backend key,
- credentials alebo workload identity,
- network a data boundary,
- policies a approvals,
- quotas a recovery plán.

Zámena environmentu je kritický failure mode. Apply job má pred mutation overiť target account, region, state key a expected environment identity.

## 13. Managed, observed a unmanaged objekty

Rozlišuj:

- **Managed resource —** IaC vlastní lifecycle a zapisuje desired attributes.
- **Observed data source —** IaC číta objekt spravovaný iným ownerom.
- **Imported resource —** existujúci objekt sa vedome pripojí k managed address.
- **Unmanaged infrastructure —** existuje mimo deklarovaného ownershipu.

Data source nevytvára ownership. Import nie je iba technický príkaz; je to rozhodnutie, že od daného momentu bude konkrétny state a configuration spravovať remote objekt.

Pred importom over ownera, úplnosť konfigurácie, drift a destroy/replacement riziko.

## 14. Drift taxonomy

Drift nie je jedna kategória.

- **Remote drift —** remote objekt sa zmenil mimo authoritative workflowu.
- **Configuration drift —** rôzne environments alebo branches deklarujú neúmyselne odlišný stav.
- **State drift —** state binding alebo hodnoty nezodpovedajú remote realite.
- **Provider drift —** nová provider verzia interpretuje rovnaký objekt odlišne.
- **Dependency drift —** mutable module, image alebo external data zmenili výsledok.
- **Ownership drift —** atribút začal meniť nový controller bez aktualizácie contractu.

Drift workflow:

```text
scheduled refresh/plan
→ classify
→ determine owner and intent
→ revert | adopt | repair | transfer ownership
→ code/state update
→ verification
```

Automatické adoptovanie každého remote stavu legitimizuje ClickOps. Automatické revertovanie každého driftu môže zrušiť incidentný zásah. Najprv treba určiť intent.

## 15. Change classification

Nie každý plan má rovnaké riziko. Klasifikuj minimálne:

- počet a typ actions,
- create/update/replace/destroy,
- stateful alebo identity-bearing resources,
- IAM a network exposure,
- data migration,
- cross-environment alebo shared dependency,
- reversibility,
- novelty a incident history.

Príklad policy:

```text
metadata-only update
→ automatický apply po štandardných gates

IAM privilege expansion
→ security approval

production database replacement
→ block alebo explicitný high-risk change plan
```

Počet zmien sám osebe nestačí. Jedna zmena route table môže mať väčší dopad než vytvorenie desiatok tags.

## 16. Identity a least privilege

Plan a apply môžu potrebovať odlišné capabilities.

- **Validation identity —** číta source a dependencies.
- **Plan identity —** číta state a remote objekty, prípadne vykonáva provider-specific validation.
- **Apply identity —** mutuje presne definovaný target scope.
- **State administration identity —** vykonáva výnimočné recovery alebo state-surgery operácie.

Preferuj short-lived workload identity viazanú na repository, ref, environment a job purpose. Jedna permanentná admin credential pre všetky environments ruší blast-radius kontrolu.

## 17. Secrets a sensitive values

Do source nepatria passwords, private keys ani static cloud credentials. Hodnota označená ako `sensitive` môže stále skončiť v state alebo provider requeste. `sensitive` obmedzuje presentation, nie automaticky storage a transport.

Bezpečný model používa:

- external secret manager,
- short-lived identity,
- secure backend,
- minimum scope,
- encryption a audit,
- redaction logs a planov,
- kontrolovaný secret rotation lifecycle.

Vyhýbaj sa posielaniu secretu ako resource argumentu, keď provider podporuje referenciu na secret ID alebo runtime retrieval.

## 18. Modules ako contracts

Module má reprezentovať stabilnú capability alebo platform boundary, nie iba skrátiť kód. Contract zahŕňa:

- typované inputs,
- stabilné outputs,
- required providers,
- assumptions a invariants,
- supported upgrade path,
- versioning,
- ownership a support.

Príliš generický module s desiatkami boolean flags vytvára neotestovateľný state space. Príliš tenký wrapper môže iba skrývať provider syntax bez pridanej policy alebo capability hodnoty.

## 19. Testing a policy layers

IaC evidence sa vrství:

```text
format
→ syntax/init/validate
→ static analysis
→ security a policy checks
→ module/native tests
→ plan
→ plan policy
→ approval
→ apply
→ post-apply verification
→ scheduled drift validation
```

Každá vrstva odpovedá na inú otázku.

- `validate` nepotvrdí cloud permissions ani quota.
- Plan nepotvrdí runtime health.
- Static policy nemusí vidieť provider defaults alebo effective organization policy.
- Post-apply smoke test nepotvrdí dlhodobý recovery behavior.

Gate musí rozlišovať finding, tool failure, incomplete evidence a stale plan.

## 20. Policy as Code

Policy as Code môže kontrolovať:

- povolené regions a providers,
- public exposure,
- encryption,
- povinné ownership metadata,
- IAM privilege expansion,
- destroy/replacement limits,
- approved module sources,
- environment-specific approvals.

Policy potrebuje versionovanie, test fixtures, ownera, vysvetliteľný finding a exception lifecycle. Policy iba nad source nemusí vidieť rendered plan; policy iba nad planom nemusí vidieť runtime drift. Obe vrstvy sa dopĺňajú.

## 21. Break-glass a ClickOps

Emergency manuálna zmena môže byť správna, keď automatizovaný path nie je dostupný alebo je príliš pomalý na containment incidentu. Musí však mať lifecycle:

```text
strongly authenticated emergency action
→ audit a alert
→ explicitný owner a expiry
→ incident stabilization
→ capture remote diff
→ code/state reconciliation
→ credential revocation
→ post-event review
```

Break-glass bez následnej reconciliation mení dočasnú výnimku na permanentný drift.

## 22. Recovery model

Pred apply definuj:

- last known compatible configuration a artifacty,
- state backup a restore postup,
- resources, ktoré sa pri zmene nahradia,
- data a identity, ktoré replacement zachová alebo stratí,
- rollback verzus roll-forward možnosti,
- compensating operations,
- external side effects,
- RPO/RTO pre stateful resources.

Návrat Git commitu iba zmení desired configuration. Remote infraštruktúru ani dáta automaticky nevráti. Nový plan môže namiesto obnovy navrhnúť ďalšie deštruktívne actions.

## 23. Evidence a audit

Dôveryhodný IaC change record prepája:

```text
change request
→ source commit
→ resolved dependency versions
→ variable/config identity
→ state version
→ saved plan digest
→ policy verdicts
→ approvals
→ apply identity and logs
→ new state version
→ runtime verification
→ recovery decision
```

Evidence musí byť immutable alebo aspoň integrity-protected a uchovávaná podľa rollback a compliance potreby.

## 24. Metriky účinnosti

Užitočné metriky:

- plan-to-apply lead time,
- apply success a partial-failure rate,
- drift age a recurrence,
- emergency/ClickOps frequency,
- destructive-change count,
- stale plan rejection rate,
- state lock contention,
- rollback/restore success,
- policy exception age,
- percent changes s post-apply verification,
- mean time to reconcile break-glass zásah.

Rýchlejší apply nie je zlepšenie, ak rastie drift alebo partial-recovery debt.

## 25. Diagnostický postup

Keď IaC výsledok nezodpovedá očakávaniu:

1. **Identifikuj subject —** repository revision, variables, backend, workspace a target account.
2. **Over toolchain —** CLI, provider, module a policy versions.
3. **Over state —** lineage, serial, lock a resource binding.
4. **Refreshni observations —** zisti actual remote state bez neuváženého apply.
5. **Klasifikuj rozdiel —** configuration, remote, state, provider alebo ownership drift.
6. **Skontroluj plan actions —** update, replacement, destroy a unknown values.
7. **Over identity a policy —** capabilities, organization controls a quotas.
8. **Zhodnoť partial failure —** ktoré remote mutations prebehli a či bol state uložený.
9. **Vyber recovery —** retry, import, state repair, rollback, roll-forward alebo restore.
10. **Over runtime a evidence —** health, data integrity, new state a audit record.

## 26. Typické anti-patterny

### ClickOps ako primárny model

Kód prestáva byť authoritative source a remote zmeny nemajú stabilný review ani recovery contract.

### Automatický apply každého commitu

Malý diff môže vytvoriť replacement, IAM expansion alebo data loss. Apply policy musí používať plan a risk context.

### Jedna admin identita pre všetko

Kompromitovaný workflow získava celú organizáciu a environment separation je iba názov.

### State v Git repository

State môže obsahovať secrets, mení sa mimo source review cadence a nepotrebuje iba verzionovanie, ale aj locking a atomic writes.

### `ignore_changes` ako riešenie driftu

Skryje ownership konflikt a odstráni kontrolu nad atribútom bez explicitného transferu zodpovednosti.

### Provisioners ako univerzálny escape hatch

Imperatívne side effects sú ťažko idempotentné, pozorovateľné a obnoviteľné.

### Plan bez subject identity

Nie je jasné, ktorú configuration, state a target kombináciu approval schválil.

### Apply success bez runtime verification

Provider dokončil API request, ale služba môže byť nedostupná, nekompatibilná alebo dátovo poškodená.

## 27. Praktický rozhodovací rámec

1. Aký desired state a ownership boundary spravujeme?
2. Ktorý systém je authoritative writer pre každý atribút?
3. Aké sú desired, known a actual state identities?
4. Aký je state a blast-radius boundary?
5. Ktoré inputs a dependencies musia byť pinované?
6. Aký presný subject reprezentuje plan?
7. Kedy plan expiruje alebo sa invaliduje?
8. Ktoré zmeny sú destruktívne, nevratné alebo data-bearing?
9. Ktoré identity smú planovať, aplikovať a opravovať state?
10. Ako sa deteguje a klasifikuje drift?
11. Ako funguje break-glass a následná reconciliation?
12. Aký recovery, restore a roll-forward plán existuje?
13. Aký runtime oracle potvrdí úspešný apply?
14. Aké evidence zostáva pre audit a budúcu diagnostiku?

## 28. Kontrolný checklist

- authoritative source a writer ownership sú explicitné;
- desired, known a actual state sa nezamieňajú;
- state boundary zodpovedá ownershipu a blast radiusu;
- environments majú samostatný backend a identity boundary;
- toolchain, providers, modules a artifacts sú pinované;
- plan má subject, digest a freshness pravidlo;
- apply vykonáva schválený saved plan, keď to workflow umožňuje;
- conflicting applies sú serializované;
- partial failure má recovery postup;
- state je šifrovaný, versionovaný, zamykaný a zálohovaný;
- secrets nie sú commitnuté ani nekontrolovane logované;
- policy rules majú testy, ownera a exception lifecycle;
- drift detection vedie k adopt/revert/repair rozhodnutiu;
- break-glass sa uzatvára reconciliation a revokáciou;
- post-apply verification kontroluje skutočný runtime outcome;
- recovery a state restore sú pravidelne testované.

## 29. Kontrolné otázky

1. Aký je rozdiel medzi desired, known a actual state?
2. Prečo deklaratívny model stále obsahuje poradie a side effects?
3. Aký je rozdiel medzi idempotenciou, convergence a reproducibility?
4. Prečo IaC repository nie je state backend?
5. Čo tvorí subject execution planu?
6. Prečo apply nie je jedna transakcia?
7. Ako state viaže resource address na remote identitu?
8. Podľa čoho sa navrhuje state boundary?
9. Aký je rozdiel medzi managed resource, data source a importom?
10. Aké typy driftu treba rozlišovať?
11. Prečo počet plan actions nie je dostatočný risk metric?
12. Čo `sensitive` chráni a čo nechráni?
13. Ako sa uzatvára break-glass zmena?
14. Prečo Git revert nie je automatický infra rollback?
15. Aké evidence dokazujú, čo sa reálne aplikovalo?

## Summary

Infrastructure as Code je riadený reconciliation a change-control model nad desired, known a actual state. Dôveryhodný workflow identifikuje všetky vstupy, vytvára čerstvý a auditovateľný plan, aplikuje ho scoped identitou, zvláda partial failure, chráni state, overuje runtime výsledok a pravidelne rieši drift. IaC nezaručuje idempotenciu, bezpečnosť ani rollback samo osebe; tieto vlastnosti vznikajú z jasného ownershipu, pinovaných dependencies, state boundaries, policy, evidence a testovaného recovery lifecycle.

## Glossary impact

Relevantné pojmy: Infrastructure as Code, desired state, known state, actual state, reconciliation, idempotencia, convergence, reproducibility, authoritative source, resource ownership, execution plan, plan subject, partial apply, state binding, state boundary, blast radius, drift taxonomy, Policy as Code, ClickOps, break-glass a plan/apply lifecycle.

## Oficiálna dokumentácia

- [Terraform language overview](https://developer.hashicorp.com/terraform/language)
- [Terraform style guide](https://developer.hashicorp.com/terraform/language/style)
- [Terraform state](https://developer.hashicorp.com/terraform/language/state)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Security scanning](../06-gitlab/security-scanning.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Terraform providers, resources a data sources →](terraform-providers-resources-data-sources.md)
<!-- KNOWLEDGE-NAVIGATION:END -->