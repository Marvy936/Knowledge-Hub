# Lifecycle, import a moved blocks

Terraform štandardne odvodzuje lifecycle managed resource z rozdielu medzi configuration, state a remote objektom. Niektoré zmeny však vyžadujú explicitnú kontrolu poradia, ochranu pred zničením, adopciu existujúcej infraštruktúry alebo bezpečné presunutie resource addressy.

Táto kapitola spája štyri príbuzné oblasti:

- lifecycle rules,
- replacement a ordering,
- import existujúcich objektov,
- refaktoring resource addresses cez `moved` blocks.

## 1. Resource lifecycle

Typický managed lifecycle:

```text
configuration added
→ create
→ read/refresh
→ update alebo replace
→ delete po odstránení z configuration
```

Provider schema určuje, ktoré zmeny možno vykonať in-place a ktoré vyžadujú replacement. Terraform Core následne zostaví dependency a operation graph.

## 2. `lifecycle` block

```hcl
resource "example_service" "this" {
  name = var.name

  lifecycle {
    create_before_destroy = true
    prevent_destroy       = true
  }
}
```

Lifecycle rules menia spôsob, akým Terraform naplánuje alebo povolí operácie. Nemajú slúžiť na skrytie nejasného ownership modelu.

## 3. `create_before_destroy`

Default replacement je typicky:

```text
destroy old
→ create new
```

`create_before_destroy` žiada opačné poradie:

```text
create new
→ verify/create dependencies
→ destroy old
```

Vhodné je to, keď:

- platforma povoľuje súbežnú existenciu oboch objektov,
- názvy alebo unique constraints nekolidujú,
- dočasná extra capacity je dostupná,
- routing alebo dependency switch je bezpečný.

Nie je to automatický zero-downtime deployment. Shared state, DNS, sessions, quotas a dependency behavior môžu stále spôsobiť výpadok.

## 4. `prevent_destroy`

```hcl
lifecycle {
  prevent_destroy = true
}
```

Terraform odmietne plan, ktorý by zničil resource, pokiaľ je rule prítomná v configuration.

Dôležité limity:

- nechráni objekt po úplnom odstránení resource blocku z configuration,
- nie je náhrada provider-side deletion protection,
- neochráni dáta pred manuálnym zásahom alebo kompromitovanou identitou,
- emergency postup potrebuje explicitný review a recovery plán.

Používaj ho pre kritické databázy, storage alebo identity resources spolu s remote ochrannými mechanizmami.

## 5. `ignore_changes`

```hcl
lifecycle {
  ignore_changes = [tags["last_modified_by"]]
}
```

Terraform pri update plánovaní ignoruje zmeny vybraných atribútov. Pri create sa hodnoty stále používajú.

Legitímne prípady:

- atribút zdieľane spravuje iný authoritative controller,
- platforma normalizuje hodnotu, ktorú provider nevie stabilne reprezentovať,
- transitional migration má explicitný owner a koniec.

Riziká:

- skrytý drift,
- nejasný ownership,
- zastaraná configuration,
- security zmena zostane bez remediation.

`ignore_changes = all` prakticky degraduje resource na create/delete wrapper a musí byť výnimočné, zdokumentované a časovo obmedzené.

## 6. `replace_triggered_by`

```hcl
resource "example_instance" "app" {
  # ...

  lifecycle {
    replace_triggered_by = [
      terraform_data.image_revision
    ]
  }
}
```

Rule vyžiada replacement, keď sa zmení referencovaný managed objekt alebo jeho atribút.

Použitie:

- immutable instance viazaná na image revision,
- certificate/resource pair, ktoré sa musia rotovať spolu,
- infra objekt, ktorého API nepodporuje bezpečný in-place update.

Pre obyčajnú hodnotu možno použiť `terraform_data`, aby vznikol resource lifecycle signal.

## 7. Preconditions a postconditions

Lifecycle môže obsahovať podmienky:

```hcl
resource "example_service" "this" {
  # ...

  lifecycle {
    precondition {
      condition     = var.replica_count >= 2
      error_message = "Production potrebuje aspoň dve replicas."
    }

    postcondition {
      condition     = self.status == "active"
      error_message = "Služba po apply nie je active."
    }
  }
}
```

- **precondition** overuje predpoklad pred operáciou,
- **postcondition** overuje výsledný stav po vyhodnotení objektu.

Podmienky majú produkovať actionable error message a nesmú duplikovať stabilnejšiu provider alebo policy validáciu bez dôvodu.

## 8. Replacement signal

Replacement môže vzniknúť z:

- zmeny provider atribútu označeného ako replace-only,
- resource taint/replace requestu,
- `replace_triggered_by`,
- zmeny identity cez `count`/`for_each`,
- zmeny resource type alebo address bez `moved` blocku,
- provider upgrade behavioru.

Pred apply analyzuj dôvod replacementu, nie iba počet `-/+` operácií.

## 9. Import: účel

Import spája existujúci remote objekt s Terraform resource addressou.

```text
remote object existuje
+ resource configuration existuje
+ import mapping
→ state binding
```

Import:

- nevytvára automaticky správny desired-state design,
- neoveruje, že configuration presne zodpovedá remote objektu,
- nepresúva ownership mimo existujúcich prevádzkových procesov,
- vyžaduje následný plan a reconciliation.

## 10. Configuration-driven import

```hcl
import {
  to = aws_s3_bucket.logs
  id = "company-prod-logs"
}

resource "aws_s3_bucket" "logs" {
  bucket = "company-prod-logs"
}
```

Výhody oproti ad-hoc CLI importu:

- mapping je reviewovateľný,
- môže byť súčasťou plan/apply workflowu,
- dá sa koordinovať viac importov,
- zostáva audit trail v Git-e.

Import block možno po úspešnom importe ponechať ako historickú deklaráciu alebo odstrániť podľa tímovej policy; resource binding zostáva v state-e.

## 11. CLI import

```bash
terraform import aws_s3_bucket.logs company-prod-logs
```

CLI import vykoná priamu state mutation. Bezpečný postup:

1. potvrď správny backend/workspace,
2. vytvor state backup,
3. zastav concurrent writers,
4. deklaruj destination resource address,
5. over provider identity a remote ID,
6. vykonaj import,
7. spusti fresh plan,
8. uprav configuration alebo remote state podľa rozhodnutia.

## 12. Import identity

Provider určuje, aký identifier alebo identity map import podporuje. Rovnaký remote objekt nesmie byť bežne importovaný do viacerých resource addresses v tom istom ownership modeli.

Duplicitné bindings môžu viesť k:

- konfliktujúcim updates,
- nečakanému delete,
- state corruption-like behavioru,
- nejasnému authoritative ownerovi.

## 13. Import s `for_each`

Configuration-driven import môže mapovať viac objektov:

```hcl
locals {
  buckets = {
    logs    = "company-logs"
    backups = "company-backups"
  }
}

resource "aws_s3_bucket" "this" {
  for_each = local.buckets
  bucket   = each.value
}

import {
  for_each = local.buckets
  to       = aws_s3_bucket.this[each.key]
  id       = each.value
}
```

Keys musia byť stabilné a destination addresses musia zodpovedať resource instances.

## 14. Post-import plan

Po importe môže plan ukázať:

- no-op,
- in-place update,
- replacement,
- removal provider defaults,
- neznáme nested blocks,
- security-impacting differences.

Nikdy automaticky neapplyuj prvý post-import plan bez review. Najprv rozhodni:

- adoptovať remote hodnotu do configuration,
- vrátiť remote objekt k desired state,
- rozdeliť ownership,
- import zrušiť a binding odstrániť.

## 15. `moved` block

```hcl
moved {
  from = aws_instance.app
  to   = module.compute.aws_instance.app
}
```

`moved` deklaruje, že objekt na starej address-e má pokračovať pod novou address-ou bez destroy/create iba kvôli refaktoringu configuration.

Terraform pri plane premapuje binding, ak sú typy a addresses kompatibilné.

## 16. Typické refaktoringy

### Premenovanie resource

```hcl
moved {
  from = aws_security_group.web
  to   = aws_security_group.application
}
```

### Presun do modulu

```hcl
moved {
  from = aws_vpc.main
  to   = module.network.aws_vpc.main
}
```

### Zmena module call name

```hcl
moved {
  from = module.vpc
  to   = module.network
}
```

### Presun instance

```hcl
moved {
  from = aws_instance.app[0]
  to   = aws_instance.app["primary"]
}
```

Každý refaktoring musí mať plan dokazujúci, že nevzniká nečakaný replacement.

## 17. `moved` vs. `terraform state mv`

### `moved` block

- versionovaný,
- reviewovateľný,
- opakovateľný pre viac environments,
- vhodný pre module consumers, ktorí upgradujú neskôr.

### `terraform state mv`

- okamžitá state surgery,
- environment-specific,
- vyžaduje presný backend a lock,
- vhodná najmä pre recovery alebo staršie workflowy.

Pre bežný refaktoring preferuj configuration-driven `moved` block.

## 18. Retention `moved` blocks

Pri reusable module môže consumer preskočiť viac releases. Ak module author odstráni `moved` block priskoro, neskorý upgrade môže vidieť destroy/create.

Policy má definovať:

- minimálne podporované upgrade paths,
- ako dlho sa moved history zachováva,
- kedy ide o breaking release,
- ako sa testujú upgrades z podporovaných versions.

## 19. Address changes bez `moved`

Terraform interpretuje:

```text
old address removed
new address added
```

Výsledok môže byť:

```text
destroy old remote object
create new remote object
```

Aj keď oba blocks opisujú rovnakú infraštruktúru, state identity je viazaná na address. Refaktoring configuration preto nie je iba kozmetická zmena.

## 20. Recovery a rollback

Pri lifecycle/import/move zmene zachovaj:

- prior state snapshot,
- reviewed plan,
- provider/module versions,
- mapping starých a nových addresses,
- remote object IDs,
- migration ownera,
- explicitný abort postup.

Návrat Git commitu po state move nemusí automaticky vrátiť state address. Recovery sa musí plánovať ako kombinácia configuration a state lifecycle.

## 21. Anti-patterny

### `ignore_changes` na každý driftujúci atribút

Skryje ownership konflikt.

### `prevent_destroy` ako jediná data protection

Nechráni pred remote deletion ani odstránením blocku.

### Import priamo v produkcii bez backupu

Chybná address alebo ID môže poškodiť ownership model.

### Prvý post-import plan sa automaticky applyne

Configuration môže prepísať kritické remote nastavenia.

### Rename resource bez `moved`

Terraform plánuje destroy/create.

### `state mv` ručne v každom environment-e

Vznikajú divergentné a ťažko auditovateľné migrations.

## 22. Troubleshooting

### `prevent_destroy` blokuje očakávanú zmenu

Zisti, prečo vznikol destroy/replace. Rule odstraň až po review data, dependency a recovery dopadu.

### `create_before_destroy` zlyhá na unique name

Nový a starý objekt nemôžu koexistovať. Použi generated name, explicitný cutover alebo inú deployment stratégiu.

### Import hlási, že objekt neexistuje

Over provider account/region, alias, remote ID format, permissions a API endpoint.

### Po importe je plán obrovský

Configuration nezodpovedá remote objectu alebo provider normalizuje hodnoty. Rozdeľ review podľa security a replacement dopadu.

### `moved` block sa neaplikuje

Over presnú old address v state-e, module path, instance key a type compatibility.

### Plan stále ukazuje destroy/create po move

Môže ísť o ďalšiu internú address zmenu, provider replacement alebo chýbajúci moved chain.

## 23. Kontrolné otázky

1. Čo mení `lifecycle` block?
2. Prečo `create_before_destroy` nezaručuje zero downtime?
3. Aké limity má `prevent_destroy`?
4. Kedy je legitímne `ignore_changes`?
5. Ako funguje `replace_triggered_by`?
6. Čo import robí a čo nerobí?
7. Prečo je post-import plan kritický?
8. Aký je rozdiel medzi `moved` blockom a `state mv`?
9. Prečo treba moved history zachovať v reusable module?
10. Prečo Git rollback nemusí obnoviť pôvodný state mapping?

## Glossary impact

Relevantné pojmy: lifecycle meta-argument, create before destroy, prevent destroy, ignore changes, replace triggered by, Terraform import, import block, post-import plan, moved block, address refactoring a moved history.

## Oficiálna dokumentácia

- [Meta-arguments](https://developer.hashicorp.com/terraform/language/meta-arguments)
- [Import block reference](https://developer.hashicorp.com/terraform/language/block/import)
- [Moved block reference](https://developer.hashicorp.com/terraform/language/block/moved)
- [Manage resource lifecycle](https://developer.hashicorp.com/terraform/tutorials/state/resource-lifecycle)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Modules](modules.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Drift →](drift.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
