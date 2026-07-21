# Drift

**Drift** je rozdiel medzi deklarovaným desired state, Terraform state a skutočným remote stavom infraštruktúry. Nie každý rozdiel má rovnakú príčinu ani rovnakú remediation stratégiu.

Terraform drift management nie je iba príkaz `plan`. Je to ownership, detection, classification, decision a reconciliation workflow.

## 1. Tri relevantné pohľady

```text
configuration
↕
Terraform state
↕
remote infrastructure
```

- **configuration** opisuje desired state,
- **state** uchováva bindings a naposledy známe attributes,
- **remote infrastructure** je aktuálny stav z provider API.

Plan môže správne rozhodovať iba vtedy, keď provider dokáže remote objekt načítať a identity/permissions smerujú na správne prostredie.

## 2. Typy driftu

### Remote drift

Objekt bol zmenený mimo Terraform workflowu.

### Configuration drift

Branches, environments alebo repositories používajú rozdielne deklarácie bez vedomej policy.

### State drift

State binding alebo snapshot nezodpovedá skutočnému ownershipu či identite objektu.

### Provider interpretation drift

Provider upgrade, API normalizácia alebo schema zmena spôsobí iné čítanie rovnakého remote objektu.

### Dependency drift

Externá dependency zmení behavior bez priamej zmeny managed resource, napríklad image tag, policy attachment alebo data source result.

## 3. Drift vs. unmanaged infrastructure

Terraform automaticky nevie o každom objekte v účte alebo clustri. Objekt vytvorený mimo configuration nie je automaticky „drift“ konkrétneho state-u, pokiaľ:

- nemá existujúci binding,
- neovplyvní managed object,
- nie je explicitne objavený data source alebo policy scanom.

Discovery unmanaged resources potrebuje inventory, cloud asset query alebo policy tooling nad rámec jedného Terraform planu.

## 4. Ako Terraform drift deteguje

Pri bežnom `terraform plan` Terraform typicky:

1. načíta configuration a prior state,
2. refreshne managed resources cez providers,
3. aktualizuje working in-memory view,
4. porovná desired configuration s refreshed stavom,
5. navrhne create/update/replace/delete operácie.

Plan môže ukázať poznámku, že objekty sa zmenili mimo Terraformu.

## 5. Refresh-only mode

```bash
terraform plan -refresh-only
```

Refresh-only plan ukáže, ako by sa state zmenil podľa remote reality bez plánovania zmien remote infraštruktúry k desired configuration.

Použitie:

- vyšetrovanie manuálnej zmeny,
- provider/API normalizácia,
- potvrdenie deleted alebo changed objektu,
- rozhodovanie, či drift adoptovať alebo revertovať.

```bash
terraform apply -refresh-only
```

Zapíše refreshed remote hodnoty do state-u bez zmeny remote infraštruktúry. To je ownership rozhodnutie, nie neutrálna technická oprava.

## 6. `terraform refresh`

Samostatný `terraform refresh` priamo aktualizuje state a neposkytuje rovnaký review model ako refresh-only plan/apply workflow.

Preferuj:

```text
plan -refresh-only
→ review
→ apply -refresh-only, iba ak je adopcia rozhodnutá
```

## 7. Reconciliation možnosti

Pri drift-e existujú štyri základné rozhodnutia.

### Revert remote zmenu

Configuration zostáva authoritative a Terraform vráti infraštruktúru k desired state.

### Adopt remote zmenu

Configuration sa upraví tak, aby nový stav bol deklarovaný a reviewovaný.

### Zmeniť ownership

Atribút alebo objekt prevezme iný controller; Terraform contract sa explicitne upraví.

### Odstrániť management

Binding sa riadene odstráni zo state-u alebo resource zanikne podľa migration plánu.

„Apply bez analýzy“ nie je univerzálna drift remediation.

## 8. Drift classification

Každý drift klasifikuj podľa:

- resource a ownera,
- security dopadu,
- availability dopadu,
- data-loss rizika,
- scope/blast radiusu,
- či bol autorizovaný,
- či configuration alebo remote stav je správny,
- či je drift dočasný alebo trvalý,
- či môže remediation spôsobiť replacement.

## 9. Manual emergency change

Emergency zmena môže byť legitímna, ale musí mať closed-loop lifecycle:

```text
incident
→ autorizovaný break-glass change
→ zaznamenanie identity a dôvodu
→ stabilizácia
→ update configuration alebo revert
→ fresh plan
→ review a closure
```

Bez posledných krokov sa emergency zásah stáva permanentným ClickOps driftom.

## 10. Shared ownership

Niektoré atribúty mení platforma alebo iný controller:

- autoscaler mení replica count,
- cloud service dopĺňa computed fields,
- security controller pridáva managed rules,
- scheduler mení placement,
- external operator spravuje tags alebo members.

Shared ownership musí byť explicitný:

- kto zapisuje ktorý field,
- čo Terraform ignoruje,
- aký je conflict resolution,
- ako sa zmena audituje,
- kedy sa ownership vracia.

## 11. `ignore_changes` a drift

`ignore_changes` potlačí remediation vybraného rozdielu pri update plánovaní. Neznamená, že drift neexistuje.

Potrebné je stále:

- externé monitorovanie atribútu,
- owner,
- policy limits,
- security guardrails,
- dokumentovaný dôvod.

Použiť `ignore_changes` na každý nestabilný field je potlačenie signálu, nie drift management.

## 12. Deleted resource

Ak remote objekt zmizne, refresh odstráni alebo označí jeho binding a bežný plan môže navrhnúť recreate.

Pred apply over:

- či deletion bola úmyselná,
- či data/resource možno bezpečne obnoviť,
- či rovnaké meno/ID stále nepatrí inému objektu,
- či dependencies a secrets zostali platné,
- či incident vyžaduje restore namiesto recreate.

## 13. Drift a replacements

Malý remote rozdiel môže viesť k replacementu, ak provider atribút nepodporuje in-place update.

Pri review sleduj:

- `-/+` a `+/-` semantics,
- changed ForceNew-like attributes,
- `create_before_destroy`,
- unique constraints,
- data persistence,
- dependency rewiring,
- quota a capacity.

## 14. Drift detection cadence

Cadence vyber podľa rizika:

- kritická identity/network/security infra: častejšie,
- stabilné non-production resources: menej často,
- po incidente alebo emergency change: okamžite,
- po provider upgrade: explicitne,
- pred release/deployment: podľa dependency.

Príliš častý full refresh môže zaťažovať APIs, naraziť na rate limits a vytvoriť noise.

## 15. CI drift job

Typický scheduled workflow:

```text
checkout pinned configuration
→ initialize pinned providers/modules
→ authenticate short-lived identity
→ acquire read/plan permissions
→ terraform plan -detailed-exitcode
→ archive plan summary
→ classify changes
→ notify owner
```

`-detailed-exitcode` rozlišuje:

- `0`: bez zmien,
- `1`: chyba,
- `2`: plan obsahuje zmeny.

Exit code `2` nie je automaticky incident; potrebuje klasifikáciu.

## 16. Plan identity

Drift detector musí používať správny:

- backend,
- workspace/state key,
- provider account/subscription/project,
- region,
- credentials scope,
- variable set,
- module/provider versions.

Plan voči nesprávnemu environmentu môže vyzerať ako masívny drift alebo destroy plan.

## 17. Sensitive plans

Plan a state môžu obsahovať:

- IDs,
- network topology,
- policy documents,
- computed secrets alebo sensitive values,
- resource metadata.

Drift artifacts potrebujú:

- access control,
- encryption,
- retention,
- redaction pre notifications,
- audit downloadov.

## 18. Drift noise

Časté zdroje noise:

- provider normalizácia ordering-u,
- server-side defaults,
- timestamps,
- unordered collections modelované ako list,
- eventual consistency,
- transient API fields,
- mutable external data sources.

Riešenie:

- provider upgrade alebo bug fix,
- presnejšia schema/modeling,
- stabilné sorting/sets,
- bounded retry po eventual consistency,
- explicitný ownership,
- minimálne cielené `ignore_changes`.

## 19. Provider upgrade drift

Provider upgrade môže zmeniť:

- defaults,
- diff suppression,
- schema types,
- read normalization,
- replacement behavior,
- deprecated attributes.

Upgrade workflow má oddeliť:

```text
provider-induced plan changes
od
remote manual driftu
od
configuration changes
```

Preto provider upgrade nemiešaj s veľkým feature changeom.

## 20. Drift a import

Ak je remote zmena novým objektom, ktorý má Terraform spravovať:

1. deklaruj resource,
2. navrhni stable address,
3. importuj binding,
4. reviewni post-import plan,
5. rozhodni desired values,
6. odstráň pôvodný manual creation path.

Import bez odstránenia paralelného ownera vytvára multi-writer konflikt.

## 21. Drift a state recovery

Ak rozdiel vznikol stratou alebo poškodením state-u:

- neapplyuj recreate plan,
- zastav writers,
- obnov posledný validný snapshot,
- over lineage a serial,
- porovnaj remote identities,
- importuj chýbajúce bindings podľa recovery plánu,
- vytvor fresh plan.

State loss nie je bežný configuration drift.

## 22. Policy

Policy môže kontrolovať:

- zakázaný public access,
- nešifrované storage,
- neapproved regions,
- destructive changes,
- príliš veľký replacement count,
- chýbajúce tags/owners,
- drift na kritických security fields.

Policy nemá automaticky adoptovať alebo revertovať drift; má zviditeľniť porušenie a vynútiť rozhodovací workflow.

## 23. Observability

Sleduj:

- počet states s driftom,
- čas od detekcie po rozhodnutie,
- čas do reconciliation,
- percent autorizovaných emergency changes uzavretých v Git-e,
- drift podľa resource type/ownera,
- false-positive/noise rate,
- failed refresh rate,
- stale alebo nefunkčné detector jobs.

„Žiadny hlásený drift“ môže znamenať aj nefunkčnú detekciu.

## 24. Anti-patterny

### Automatický scheduled apply na každý drift

Neznáma zmena môže byť incident response alebo legitímna migration.

### `ignore_changes = all`

Terraform prestáva vynucovať desired attributes.

### Drift job používa admin credentials

Read-only detection má zbytočne veľký blast radius.

### Plan output sa posiela celý do verejného chatu

Môže obsahovať citlivú topológiu alebo hodnoty.

### Každý exit code `2` je incident

Plánovaná configuration zmena tiež vytvára diff.

### Manuálna oprava bez update configuration

Drift sa pri ďalšom apply vráti.

## 25. Troubleshooting

### Plan ukazuje zmeny pri každom run-e

Over provider normalization, unordered fields, server defaults, computed timestamps a eventual consistency.

### Refresh zlyhá na permissions

Detection identity nemá read access alebo smeruje na nesprávny account/project.

### Resource sa chce recreate po manuálnej zmene

Zmenil sa replace-only atribút. Rozhodni adopt/revert a priprav downtime/data recovery.

### Scheduled plan nehlási známy drift

Over správny backend, variables, refresh behavior, credentials, conditional pipeline rules a či resource patrí do state-u.

### Drift bol adoptovaný, ale configuration zostala stará

Refresh-only apply zmenil state, nie desired configuration. Ďalší bežný plan môže zmenu vrátiť.

## 26. Rozhodovací rámec

1. Ktorý resource a field driftuje?
2. Kto je authoritative owner?
3. Bola zmena autorizovaná?
4. Aký je security/data/availability dopad?
5. Je správne remote stav revertovať alebo adoptovať?
6. Vyvolá reconciliation update alebo replacement?
7. Je state a provider observation dôveryhodný?
8. Treba import, ownership migration alebo recovery?
9. Aké approvals a evidence sú potrebné?
10. Ako zabránime opakovaniu driftu?

## 27. Kontrolné otázky

1. Aké tri pohľady Terraform porovnáva?
2. Aký je rozdiel medzi remote driftom a unmanaged resource?
3. Čo robí refresh-only plan?
4. Prečo refresh-only apply nie je neutrálna operácia?
5. Aké štyri základné remediation rozhodnutia existujú?
6. Ako má skončiť emergency ClickOps change?
7. Prečo `ignore_changes` nie je drift detection?
8. Čo znamená exit code `2` pri detailed plan-e?
9. Ako provider upgrade vytvára drift-like diff?
10. Ktoré metriky dokazujú, že drift proces reálne funguje?

## Glossary impact

Relevantné pojmy: Terraform drift, remote drift, configuration drift, state drift, provider interpretation drift, refresh-only plan, drift reconciliation, drift noise, unmanaged infrastructure a drift detection cadence.

## Oficiálna dokumentácia

- [Manage resource drift](https://developer.hashicorp.com/terraform/tutorials/state/resource-drift)
- [Manage Terraform state](https://developer.hashicorp.com/terraform/tutorials/state)
- [Terraform state](https://developer.hashicorp.com/terraform/language/state)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Lifecycle, import a moved blocks](lifecycle-import-moved-blocks.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Terraform testing a policy →](terraform-testing-and-policy.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
