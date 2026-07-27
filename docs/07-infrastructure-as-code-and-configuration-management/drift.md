# Drift

Terraform drift nie je iba „plan ukazuje diff“. Je to rozdiel medzi tým, čo má byť autoritatívne deklarované, čo Terraform eviduje v state-e a čo provider skutočne pozoruje na remote objekte. Dôveryhodný drift proces musí najprv dokázať, že porovnáva správny subject, potom určiť pôvod a intent rozdielu a až následne zvoliť reconciliation.

Táto kapitola používa jeden priebežný scenár. Atlas Payments spravuje produkčný load balancer, security groups a autoscaling cez Terraform state `payments-network/prod`. Po incidente operátor cez break-glass dočasne pridá firewall rule pre diagnostický endpoint. Scheduled drift job neskôr uvidí rozdiel. Jeho úlohou nie je automaticky kliknúť `apply`, ale bezpečne uzavrieť lifecycle tejto odchýlky.

## 1. Dominantný model: evidence-to-reconciliation lifecycle

```text
authoritative configuration a ownership contract
+ state lineage, serial a resource binding
+ current provider observation
→ subject-verified difference
→ origin, intent a risk classification
→ revert | adopt | transfer ownership | remove management | recover state
→ fresh reviewed plan
→ bounded mutation alebo metadata transition
→ runtime a state verification
→ closure, recurrence control a audit
```

Drift detection je iba prvá polovica procesu. Kým nie je známy správny environment, resource identity, writer a dôvod zmeny, diff nie je bezpečný príkaz na remediation.

## 2. Atlas drift subject

Scheduled job musí vedieť spätne dokázať, čo presne porovnával:

```text
repository revision: 7f42...
Terraform/provider/module versions
resolved variable set: payments-prod
backend key: payments-network/prod
state lineage: L-PROD-NET
state serial: 418
provider target: production account, eu-central-1
workload identity: drift-reader/payments-network
refresh time: 2026-07-27T05:00Z
```

Toto je **drift detection subject**. Bez neho sa nedá odlíšiť reálny remote drift od plánu spusteného proti nesprávnemu workspace-u, účtu, regionu, module version alebo stale state snapshotu.

## 3. Tri stavy a ich mechanizmus

Terraform porovnáva tri rozdielne pohľady:

```text
configuration = desired state
state = binding a posledné Terraform knowledge
remote API = current observed state
```

Príklad:

```text
configuration:
  aws_security_group_rule.diagnostics absent

state serial 418:
  rule absent

remote API:
  rule sgr-incident-42 present
```

Rozdiel môže znamenať:

- neautorizovaný ClickOps zásah;
- legitímny incidentný break-glass change;
- zmenu iného autoritatívneho controllera;
- neaktuálny alebo poškodený state;
- provider/API normalizáciu;
- nesprávny detection subject.

Rovnaký vizuálny diff preto môže vyžadovať opačné rozhodnutia.

## 4. Detection: refresh nie je remediation

Bežný `terraform plan` typicky:

```text
načíta configuration a prior state
→ provider prečíta bound remote objects
→ Terraform vytvorí refreshed working view
→ porovná desired a observed hodnoty
→ navrhne change graph
```

`terraform plan -refresh-only` izoluje otázku:

> Ako by sa zmenilo Terraform knowledge, keby sme remote realitu prijali do state-u bez remote mutation?

```bash
terraform plan -refresh-only
```

`terraform apply -refresh-only` už zapisuje nový snapshot. Nie je to neutrálne „upratanie“. Mení evidence, z ktorej vznikne ďalší plan, a preto musí nasledovať až po ownership rozhodnutí.

Samostatný `terraform refresh` neposkytuje rovnaký reviewed plan/apply contract. Pre produkčný workflow preferuj:

```text
refresh-only plan
→ review subjectu a rozdielu
→ rozhodnutie o adopcii
→ refresh-only apply iba pri schválenej adopcii knowledge
```

## 5. Pôvod rozdielu

Taxonómia pomáha iba vtedy, keď vedie k odlišnej náprave.

### Remote drift

Bound objekt alebo jeho atribút zmenil writer mimo autoritatívneho Terraform workflowu.

```text
configuration: port 443
state: port 443
remote: port 8443
```

Najprv identifikuj writera a intent. Až potom rozhodni adopt/revert.

### Configuration divergence

Rôzne branches, repositories alebo environments deklarujú neúmyselne odlišný stav. Remote objekt môže byť presne v súlade s jednou konfiguráciou a driftovať voči druhej.

### State/binding drift

State adresa, provider context alebo remote ID nezodpovedá aktuálnemu ownershipu. Príkladom je restore starého snapshotu, stratený binding alebo neúplný address move.

### Provider interpretation drift

Nová provider verzia alebo API normalization načíta rovnaký objekt odlišne. Dôsledkom môže byť perpetual diff alebo nový replacement signal bez manuálnej remote zmeny.

### Dependency drift

Mutable data source, image tag, policy attachment alebo external catalog zmení resolved input. Managed resource nemusí byť manuálne upravený, no výsledný plan sa zmení.

### Unmanaged infrastructure

Objekt bez bindingu nie je automaticky drift konkrétneho state-u. Jeho discovery vyžaduje cloud asset inventory, CMDB alebo policy scan. Ak sa má stať managed, potrebuje ownership adoption a import lifecycle.

## 6. Worked failure: automatický revert incidentnej rule

Počas incidentu operátor pridá diagnostickú ingress rule s ticketom `INC-8421` a expiráciou o dve hodiny. Scheduled pipeline o päť minút neskôr uvidí remote drift a automaticky vykoná bežný plan/apply.

Mechanizmus failure:

```text
legitímny dočasný writer
→ remote change ešte stabilizuje incident
→ detector vidí iba rozdiel, nie intent/expiry
→ automatic apply považuje configuration za jedinú pravdu
→ rule odstráni
→ diagnostický path zanikne uprostred incidentu
```

Problémom nie je, že Terraform reconcilioval. Problémom je chýbajúci closed-loop break-glass contract.

Správny lifecycle:

```text
strongly authenticated break-glass action
→ ticket, owner, scope a expiry
→ drift detector klasifikuje known exception
→ incident stabilization
→ adopt alebo revert cez reviewed configuration change
→ fresh plan a runtime verification
→ exception closure a credential revocation
```

Policy má brániť nekontrolovanému auto-apply neznámeho driftu, nie skryť samotný rozdiel.

## 7. Worked failure: refresh-only „adopcia“ bez configuration zmeny

Autoscaling operátor dočasne zmení minimum instances z `6` na `10`. Operátor spustí `apply -refresh-only`, aby „odstránil drift“, ale configuration zostane na hodnote `6`.

Výsledok:

```text
remote = 10
state knowledge = 10
configuration = 6
→ nasledujúci bežný plan stále navrhne návrat na 6
```

Refresh-only apply prijal remote observation do state snapshotu, ale nezmenil desired state. Skutočná adopcia vyžaduje reviewovanú configuration zmenu alebo explicitný transfer ownershipu daného atribútu.

## 8. Shared ownership a `ignore_changes`

Niektoré polia legitimne mení iný controller:

- autoscaler spravuje replica count;
- security controller pridáva platform rules;
- cloud platforma normalizuje computed fields;
- scheduler spravuje placement;
- external operator riadi membership.

Shared ownership musí definovať field-level contract:

```text
attribute
→ authoritative writer
→ allowed range
→ observation source
→ conflict resolution
→ expiry alebo ownership-return condition
```

`ignore_changes` môže zabrániť Terraform remediation vybraného atribútu, ale:

- neodstráni security risk;
- nevytvorí monitoring;
- neurčí ownera;
- neoverí povolený rozsah;
- nevyrieši multi-writer konflikt.

```hcl
lifecycle {
  ignore_changes = [desired_capacity]
}
```

Takýto contract potrebuje externú kontrolu, že autoscaler neprekročí bezpečné minimum alebo maximum. `ignore_changes = all` zvyčajne znamená, že Terraform už nevynucuje významný desired state.

## 9. Deleted a nahrádzaný objekt

Keď provider nenájde bound remote objekt, bežný plan môže navrhnúť recreation. Pred apply treba odlíšiť:

- úmyselnú deletion;
- incident alebo compromise;
- state smerujúci na nesprávny target;
- provider/API visibility problém;
- objekt vyžadujúci restore dát namiesto prázdnej recreation.

Malý drift na replace-only atribúte môže vytvoriť celý replacement graph. Review musí sledovať:

```text
changed field
→ provider replacement semantics
→ old/new coexistence
→ identity a data persistence
→ dependency rewiring
→ capacity/quota
→ runtime cutover a recovery
```

Počet diff riadkov nie je risk metric.

## 10. Drift detection pipeline

Dôveryhodný scheduled workflow:

```text
checkout pinned configuration
→ initialize pinned providers/modules
→ resolve canonical backend a target identity
→ authenticate read/plan identity
→ record starting lineage/serial
→ run refresh a detailed plan
→ validate expected state/resource inventory
→ classify configuration, remote, state a provider changes
→ publish redacted subject-bound evidence
→ route owner decision
```

`terraform plan -detailed-exitcode` vracia:

- `0` — bez plánovaných changes;
- `1` — chyba alebo neplatná evidence;
- `2` — plan obsahuje changes.

Exit code `2` nie je automaticky incident. Exit code `0` tiež nie je dôkaz clean state-u, ak refresh zlyhal, job použil nesprávny backend alebo expected resources neboli v state-e.

## 11. Worked failure: false clean pre nesprávny workspace

Security tím vie, že produkčná rule bola manuálne otvorená, ale drift dashboard ukazuje `0 changes`.

Skutočný detection subject:

```text
workspace: stage
provider account: stage
state resources: 38
expected production resources: 117
```

Pipeline technicky prešla. Skenovala však inú infraštruktúru.

Skoršie controls:

- canonical environment identity assertion;
- expected lineage a backend key;
- expected resource/critical-address inventory;
- provider account/region assertion;
- notification obsahujúca subject metadata, nie iba počet changes.

## 12. Drift noise a signal integrity

Perpetual diff môže vzniknúť z:

- unordered fields modelovaných ako list;
- server-side defaults;
- transient timestamps;
- eventual consistency;
- provider normalization;
- mutable external data;
- nestabilných generated values.

Noise nie je iba ergonomický problém. Ak pipeline ukazuje rovnakých 200 neškodných zmien každý deň, reviewer môže prehliadnuť jednu novú IAM privilege expansion.

Riešenie musí odstrániť príčinu:

```text
provider fix/upgrade
| schema a set modeling
| deterministic sorting
| bounded read-after-write retry
| pinning external dependency
| explicit ownership contract
| úzko cielený ignore_changes s external guardrailom
```

Provider upgrade oddeľ od feature change-u, aby bolo možné rozlíšiť provider-induced reinterpretation od remote a configuration driftu.

## 13. Reconciliation decisions

Po overení subjectu a intentu existuje päť hlavných ciest.

### Revert

Configuration zostáva autoritatívna a reviewed apply vráti remote objekt do desired state-u.

### Adopt

Remote intent je správny. Najprv sa aktualizuje configuration, potom sa vytvorí fresh plan, ktorý potvrdí nový desired state.

### Transfer ownership

Iný controller prevezme objekt alebo atribút. Terraform configuration, lifecycle rules, monitoring a support contract sa upravia spolu.

### Remove management

Binding sa riadene odstráni iba pri vedomom ownership transfere alebo retirement-e. Resource block nesmie zostať tak, aby ďalší plan vytvoril duplicate objekt.

### Recover state

Ak rozdiel vznikol stratou, restore alebo poškodením state-u, riešením nie je automatický apply. Najprv sa obnovia alebo zrekonštruujú bindings a overí remote identity.

## 14. Causal troubleshooting walkthrough: rovnaký diff pri každom plane

Atlas pipeline pri každom run-e tvrdí, že load balancer listener treba aktualizovať. Predchádzajúci apply je zelený, ale ďalší plan ukáže rovnakú zmenu.

### 1. Zafixuj subject

Zaznamenaj:

- final source revision;
- provider/module versions;
- variables;
- backend key, lineage a serial;
- provider account/region;
- resource address a remote ID.

### 2. Súťažiace hypotézy

1. Provider normalizuje hodnotu inak, než ju configuration zapisuje.
2. Druhý writer po apply hodnotu prepisuje.
3. Apply smeruje na iný target než následný plan.
4. State write po apply zlyhal alebo bol nahradený stale snapshotom.
5. Mutable data source dáva pri každom run-e inú hodnotu.
6. Eventual consistency spôsobí dočasný stale read.

### 3. Diskriminačné observation points

- plan JSON `before/after` a replacement reason;
- provider debug/request IDs bez secrets;
- cloud audit log writer identity a timestamp;
- backend serial pred a po apply;
- exact remote value bezprostredne po apply a po propagation intervale;
- resolved data-source result a dependency digest;
- account/region identity v oboch jobs.

### 4. Containment

Pozastav automatický apply na affected state. Nepridávaj `ignore_changes`, kým nie je známy owner a security dopad.

### 5. Recovery podľa dôkazu

- provider normalization → upgrade/fix alebo canonical configuration;
- second writer → odstránenie konfliktu alebo transfer ownershipu;
- wrong target → oprava provider/backend identity a audit zasiahnutého prostredia;
- state failure → authoritative snapshot recovery a fresh plan;
- mutable input → pinning immutable identity;
- eventual consistency → bounded condition-based retry.

### 6. Over pôvodný outcome

Spusti apply, počkaj na definovaný convergence interval a vykonaj druhý fresh plan. Úspech znamená:

```text
runtime invariant je splnený
+ state binding/serial je správny
+ nový plan je no-op
+ conflict writer sa neobjavil
```

### 7. Posuň control skôr

Pridaj regression test provider behavioru, writer audit alert, subject assertion alebo immutable dependency control podľa zistenej príčiny.

## 15. Policy, evidence a observability

Policy môže blokovať alebo eskalovať:

- public exposure;
- IAM privilege expansion;
- destructive replacement kritického objektu;
- nešifrované storage;
- drift na protected fields;
- neznámy writer alebo expired exception.

Policy však sama neurčuje intent remote zmeny. Musí viesť k owner decision workflowu.

Uchovávaná evidence má obsahovať:

```text
detection subject
→ starting state lineage/serial
→ refreshed resource inventory
→ redacted change summary
→ origin/owner classification
→ decision a approvals
→ plan/apply identity
→ ending state serial
→ runtime verification
→ exception alebo incident closure
```

Sleduj minimálne:

- drift age a recurrence;
- čas od detekcie po owner decision;
- čas do reconciliation;
- failed alebo missing detector runs;
- expected states bez čerstvej evidence;
- noise rate;
- break-glass changes bez closure;
- replacements spôsobené driftom;
- percent remediation s runtime verification.

„Žiadny hlásený drift“ môže znamenať aj nefunkčný detector.

## 16. Referenčné pravidlá

- Najprv over detection subject, až potom interpretuj diff.
- Refresh-only apply mení state knowledge, nie desired configuration.
- Neznámy drift sa automaticky neapplyuje.
- `ignore_changes` je ownership mechanizmus, nie detektor ani security control.
- Unmanaged objekt potrebuje discovery a adoption workflow.
- Provider upgrade môže vytvoriť drift-like diff bez remote writera.
- State loss sa rieši recovery/importom, nie hromadnou recreation.
- Každé rozhodnutie sa uzatvára fresh planom, runtime verification a auditom.

## 17. Kontrolné otázky

1. Čo tvorí drift detection subject?
2. Prečo rovnaký diff môže znamenať legitímny break-glass aj neautorizovaný ClickOps?
3. Čo zmení `apply -refresh-only` a čo nezmení?
4. Ako sa líši remote drift od state/binding driftu?
5. Prečo exit code `0` nemusí dokazovať clean produkciu?
6. Kedy je `ignore_changes` legitímne a aké controls potrebuje?
7. Ako noise oslabuje detekciu skutočného risku?
8. Kedy treba drift adoptovať, revertovať alebo preniesť ownership?
9. Aké observation points odlíšia second writera od provider normalization?
10. Ako sa dokáže, že remediation obnovila pôvodný runtime outcome?

## Glossary impact

Relevantné pojmy: drift detection subject, remote drift, configuration divergence, state/binding drift, provider interpretation drift, dependency drift, unmanaged infrastructure, refresh-only plan, drift evidence, drift reconciliation, shared ownership, drift noise a break-glass closure.

## Oficiálna dokumentácia

- [Manage resource drift](https://developer.hashicorp.com/terraform/tutorials/state/resource-drift)
- [Manage Terraform state](https://developer.hashicorp.com/terraform/tutorials/state)
- [Terraform state](https://developer.hashicorp.com/terraform/language/state)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Lifecycle, import a moved blocks](lifecycle-import-moved-blocks.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Terraform testing a policy →](terraform-testing-and-policy.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
