# Lifecycle, import a moved blocks

Terraform lifecycle controls, import a `moved` blocks riešia tri odlišné zmeny:

```text
remote lifecycle transition
ownership adoption
configuration address transition
```

Ich spoločným subjectom je resource instance identity a binding. Nesprávne použitý lifecycle rule môže skryť drift; nesprávny import môže prevziať cudzí objekt; rename bez `moved` mappingu môže zmeniť čisto konfiguračný refaktor na remote destroy/create.

Dominantný model:

```text
current address, binding a remote owner
→ klasifikácia zamýšľanej transition
→ lifecycle/import/move plan
→ identity a destructive-risk review
→ chránená state alebo remote mutation
→ nový binding a actual-state verification
→ recovery a migration closure
```

## 1. Atlas scenár: refaktoring a adopcia produkčného storage

Atlas Payments má produkčný log bucket spravovaný manuálne. Súčasne presúva sieťové resources z root module-u do reusable `network` module-u.

Sú to dve odlišné operácie:

```text
bucket existuje mimo Terraform ownershipu
→ import/adoption do novej resource address-y

VPC už je spravovaná starou address-ou
→ moved mapping na novú address-u
```

Import vytvára nový binding k existujúcemu remote objektu. `moved` zachováva existujúci binding pri zmene configuration address-y. Ani jedna operácia sama osebe nemení remote behavior; následný plan však môže odhaliť configuration rozdiel, ktorý by remote objekt zmenil alebo nahradil.

## 2. Resource lifecycle a replacement subject

Terraform porovná configuration, state binding, provider schema a remote observations. Výsledok pre resource môže byť:

```text
no-op
in-place update
replace: destroy → create
replace: create → destroy
create
destroy
```

Replacement nie je iba syntaktická značka `-/+`. Môže meniť:

- remote object ID;
- IP/DNS alebo endpoint;
- data a encryption identity;
- attached policies;
- dependency graph a routing;
- availability a rollback možnosti.

Pred apply treba identifikovať, **prečo** replacement vznikol: provider replace-only field, instance key zmena, address refactor bez move, explicitný trigger alebo provider upgrade.

## 3. `create_before_destroy` ako operation ordering

Default replacement často znamená:

```text
destroy old
→ create new
```

`create_before_destroy` žiada:

```text
create new
→ pripraviť dependents/cutover
→ destroy old
```

Je bezpečný iba ak môžu objekty koexistovať a existuje explicitný cutover model. Limity:

- unique name alebo singleton constraint;
- quota a dočasná extra capacity;
- shared IP, data alebo identity;
- downstream references;
- sessions, traffic a DNS propagation;
- provider/API behavior.

Rule negarantuje zero downtime. Iba mení operation graph.

## 4. Worked failure: `create_before_destroy` narazil na unique name

Atlas menil encryption configuration storage bucketu. Provider vyžadoval replacement a tím pridal `create_before_destroy`.

```text
new bucket má rovnaký globálne unique name
→ create new zlyhá
→ old bucket ostáva
→ apply je partial/failed
→ migrácia dát ani cutover sa nezačali
```

Príčina nie je poradie samo osebe, ale nemožnosť súbežnej identity. Bezpečná stratégia potrebuje nový generated name, data copy, verification, consumer cutover a až potom retirement starého objektu.

## 5. `prevent_destroy` ako plan guard

`prevent_destroy` blokuje planovanú deštrukciu, kým je rule prítomná v configuration. Je to lokálny change-control guard, nie úplná data protection.

Nechráni pred:

- manuálnym remote deletion;
- kompromitovanou cloud identity;
- odstránením celého resource blocku a následným planom;
- provider-side data loss pri in-place update;
- state corruption alebo wrong backendom.

Používaj ho spolu s provider-side deletion protection, backups, scoped identity a explicitným high-risk workflowom.

Ak rule blokuje change, najprv vysvetli, prečo plan obsahuje destroy/replace. Odstránenie rule bez tejto analýzy ruší posledný guard bez pochopenia rizika.

## 6. `ignore_changes` ako ownership contract

`ignore_changes` hovorí, že Terraform nemá pri update reconciliation riadiť vybrané attributes.

Legitímny model:

```text
Terraform vlastní resource
external controller vlastní explicitný attribute X
→ ignore_changes[X]
→ monitoring overuje controller ownership
```

Bez ownera a observation pointu rule iba skrýva drift. Security-significant field môže zostať nesprávny bez viditeľného planu.

Každý ignored attribute má mať:

- authoritative writera;
- dôvod;
- runtime monitoring;
- expiry alebo review;
- incident/recovery postup.

`ignore_changes = all` prakticky odoberá Terraformu update ownership a má byť výnimočné.

## 7. `replace_triggered_by` ako explicitný lifecycle edge

`replace_triggered_by` vyjadruje, že resource identity alebo implementation musí byť obnovená pri zmene iného managed subjectu:

```hcl
lifecycle {
  replace_triggered_by = [terraform_data.image_revision]
}
```

Je vhodný napríklad pre immutable compute viazaný na image revision. Trigger má reprezentovať skutočnú incompatibility alebo rotation boundary. Ak sa naviaže na hlučnú či mutable hodnotu, každý plan môže spôsobovať replacement.

## 8. Preconditions a postconditions

Precondition blokuje operáciu pri nesplnenom predpoklade. Postcondition kontroluje providerom pozorovaný výsledok resource-u.

```text
precondition
→ mutation
→ provider read
→ postcondition
```

Postcondition nie je kompletná runtime validation. Provider attribute `status = active` nemusí dokazovať traffic, data integrity ani business outcome. Kritické zmeny stále potrebujú nezávislý verification krok.

## 9. Import je ownership adoption

Import spája existujúci remote objekt s Terraform address-ou:

```text
remote object ID
+ destination resource address
+ provider target identity
→ new state binding
```

Import sám nevytvorí správnu configuration. Neurčí, či Terraform smie meniť všetky attributes, či objekt nespravuje iný system ani či prvý plan nebude deštruktívny.

Adoption contract musí potvrdiť:

- remote owner a dôvod transferu;
- presný account/region/provider alias;
- remote object ID;
- destination address a instance key;
- configuration completeness;
- shared/external writers;
- post-import plan a rollback.

## 10. Configuration-driven import

Versionovaný import block je reviewovateľný:

```hcl
import {
  to = aws_s3_bucket.logs
  id = "company-prod-logs"
}
```

Výhody:

- mapping je súčasť change proposal-u;
- môže prejsť plan/policy workflowom;
- viac imports sa dá koordinovať;
- zostáva auditovateľná intent history.

CLI import je okamžitá state mutation. Je vhodný pre riadenú recovery alebo workflowy, ktoré import blocks nepoužívajú, ale potrebuje freeze writers, backup a následný plan.

## 11. Worked failure: import prevzal správny názov v nesprávnom account-e

Atlas chcel importovať `company-prod-logs`. Operátor použil default provider namiesto `aws.production`. Rovnaký názov existoval v test account-e.

```text
import command uspeje
→ state binding ukazuje test bucket
→ production configuration obsahuje production policies
→ post-import apply mení test objekt
→ skutočný production bucket ostáva unmanaged
```

Názov a úspešný import nedokazujú target identity. Import subject musí zahŕňať provider configuration address, account, region a remote ID. Post-import verification musí potvrdiť actual production object.

## 12. Post-import plan je ownership reconciliation

Prvý plan po importe môže ukázať:

- no-op;
- provider normalization;
- in-place changes;
- replacement;
- odstránenie existujúcich nested rules;
- security alebo encryption rozdiel;
- attributes spravované iným controllerom.

Rozhodnutie:

```text
adopt remote value do configuration
revert remote object k approved desired state
rozdeliť attribute ownership
zrušiť chybný binding/import
```

Prvý post-import plan sa nesmie automaticky applynuť. Je to moment, keď sa manual reality stretne s novým authoritative modelom.

## 13. `moved` block ako versionovaný binding transition

```hcl
moved {
  from = aws_vpc.main
  to   = module.network.aws_vpc.main
}
```

`moved` hovorí:

```text
old address a remote binding
→ same remote object
→ new address
```

Terraform môže potom zmeniť state mapping bez remote destroy/create iba kvôli refaktoringu. Kompatibilita závisí od resource type, instance identity a presných module paths.

## 14. Address refactoring nie je kozmetika

Bez `moved` mappingu Terraform vidí:

```text
old address removed
new address added
→ destroy old + create new
```

Aj keď HCL blocks opisujú rovnaký objekt, state identity je address-based. Premenovanie resource labelu, module callu alebo `count` indexu na `for_each` key môže byť deštruktívna change bez migration contractu.

## 15. Worked failure: rename security group bez moved mappingu

Atlas premenoval:

```text
aws_security_group.web
→ aws_security_group.application
```

Plan navrhol vytvoriť novú group a zmazať starú. Starú group však používali external workloads mimo Terraform graphu.

```text
configuration refactor
→ new remote security group
→ managed attachments sa presunú
→ old group delete zlyhá alebo odpojí external consumers
```

Príčina bola chýbajúca address migration a neúplný consumer inventory. `moved` block zachová remote ID; external dependency inventory overí, že refaktor nemení effective authorization.

## 16. `moved` verzus `state mv`

### `moved` block

- versionovaný a reviewovateľný;
- opakovateľný pre viac states/environments;
- vhodný pre reusable module consumers;
- umožňuje retained upgrade path.

### `terraform state mv`

- okamžitá mutation konkrétneho state-u;
- potrebuje exact backend, lock a backup;
- nepropaguje sa automaticky ďalším environments;
- vhodný pre recovery alebo legacy migration.

Bežný refaktoring patrí do configuration-driven `moved` history. Ručná surgery v každom state-e vytvára divergentný migration stav.

## 17. Moved history a supported upgrade paths

Consumer môže preskočiť viac module releases:

```text
2.8.0 → 3.5.0
```

Ak latest release zachováva iba move z `3.4.0`, staršia address nemá chain a consumer uvidí destroy/create.

Retention policy musí definovať:

- najstaršiu podporovanú source version;
- celý moved chain pre supported upgrades;
- fixture states;
- breaking release moment;
- deprecation a retirement komunikáciu.

## 18. Lifecycle a state recovery

Lifecycle, import a move zmeny môžu meniť remote object, state binding alebo oboje. Recovery preto nemôže byť iba Git revert.

Zachovaj:

```text
prior configuration a module versions
prior state snapshot
old/new address a remote-ID manifest
reviewed plan
provider target identity
mutation logs
runtime verification
```

Po state move môže Git revert obnoviť staré HCL addresses, ale state už používa nové. Recovery potrebuje explicitný reverse mapping alebo forward fix.

## 19. Kauzálny diagnostický walkthrough

Symptom: po presune resources do `module.network` plán ukazuje 32 destroy/create operácií, hoci remote infraštruktúra sa nemá meniť.

### Krok 1 — stabilizuj subject

```text
configuration C61
state L-prod/S231
old root addresses
new module.network addresses
provider aws.production/account 7711
module upgrade 4.1.0 → 5.0.0
```

### Krok 2 — konkurenčné hypotézy

```text
H1: moved blocks chýbajú alebo používajú nesprávne module paths
H2: for_each keys sa zmenili počas refaktoringu
H3: resource type/schema zmena znemožňuje move
H4: provider upgrade spôsobuje skutočný replacement
H5: state používa staršie/odlišné addresses než migration fixtures
H6: import alebo state surgery vytvorili duplicate binding
H7: lifecycle trigger nezávisle vyžaduje replacement
```

### Krok 3 — diskriminačné observation points

- state list a old/new address manifest testujú H1/H5/H6;
- instance key diff testuje H2;
- type/provider schema a replacement reasons testujú H3/H4;
- lifecycle-expanded plan testuje H7;
- remote-ID mapping overuje, či ide o rovnaké objekty.

Atlas zistí, že moved mappings pokrývajú VPC a subnets, ale nie module instances vytvorené cez staré numeric `count` addresses. H1/H2 vysvetľujú zvyšné replacements.

### Krok 4 — containment a oprava

Apply sa zastaví. Tím doplní presný chain z indexových addresses na stabilné keys. Nepoužije `create_before_destroy` ako maskovanie identity chyby; to by vytvorilo nové remote objekty namiesto zachovania bindings.

### Krok 5 — over outcome

Nový plan musí ukázať moves/no-op pre všetky intended objects. Po apply sa overí:

- rovnaký remote-ID inventory;
- nový state serial a nové addresses;
- nulové orphaned/duplicate resources;
- nezmenený routing, security a runtime health.

### Krok 6 — skorší control

Finding sa mení na state-address fixture test, automated destructive-plan gate a povinný migration manifest pri module major release.

## 20. Diagnostický runbook

1. Urči current address, provider target, remote ID a ownera.
2. Klasifikuj zmenu ako remote lifecycle, adoption alebo address transition.
3. Pri replacement-e zisti presný trigger a co-existence constraints.
4. Pri import-e over provider target, ID, configuration completeness a existujúcich writers.
5. Pri move porovnaj state addresses, instance keys a full moved chain.
6. Zastav apply pri nečakanom destroy/replace.
7. Použi versionovaný mapping pred environment-specific surgery.
8. Zachovaj prior snapshot a recovery manifest.
9. Over state bindings aj effective runtime outcome.
10. Aktualizuj ownership, upgrade fixtures a destructive-change controls.

## 21. Referenčné pravidlá

- Lifecycle rule mení operation semantics, nie ownership realitu.
- `create_before_destroy` negarantuje co-existence ani zero downtime.
- `prevent_destroy` je plan guard, nie úplná data protection.
- `ignore_changes` potrebuje explicitného authoritative writera a monitoring.
- Import je ownership adoption, nie iba technické načítanie ID.
- Post-import plan je povinná reconciliation boundary.
- `moved` zachováva binding pri address refaktoringu.
- Address a instance key sú state identity.
- `state mv` je konkrétna surgery, nie reusable migration contract.
- Git revert sám nemusí obnoviť state mapping alebo remote object.
- Supported module upgrades potrebujú retained moved history.

## 22. Časté omyly

### „`create_before_destroy` vyrieši každý výpadok“

Objekty nemusia môcť koexistovať a traffic/data cutover zostáva samostatný problém.

### „`ignore_changes` opravuje drift“

Iba ho odstráni z Terraform reconciliation; bez ownership contractu ho skrýva.

### „Import znamená, že configuration je správna“

Import vytvorí binding. Až post-import plan ukáže rozdiel medzi code a remote objectom.

### „Rename resource je iba refaktor“

Bez `moved` mappingu je to odstránenie starej address-y a pridanie novej.

### „Git rollback vráti neúspešný move“

State address transition už mohla prebehnúť a potrebuje vlastný recovery mapping.

## Zhrnutie

Dôveryhodný lifecycle/adoption/refactor model je:

```text
identified current binding a owner
→ presne klasifikovaná transition
→ reviewed lifecycle/import/move plan
→ protected mutation
→ verified new binding a remote outcome
→ retained migration a recovery evidence
```

Terraform lifecycle troubleshooting sa nekončí pridaním meta-argumentu. Musí preukázať, či problém patrí remote operation poradiu, ownership adoptionu alebo state address identity.

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