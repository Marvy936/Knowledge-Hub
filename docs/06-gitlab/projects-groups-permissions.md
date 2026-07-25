# Projects, groups a permissions

GitLab spája source code, merge requests, CI/CD, registries, security findings a deployment metadata do projektov uložených v namespaces. Group hierarchy pritom nie je iba navigačný strom. Určuje inheritance membershipu, policy scope, identity dosah, ownership, billing, audit a blast radius administratívnej zmeny.

Cieľom permission modelu nie je iba priradiť používateľovi rolu. Cieľom je vedieť dokázať:

```text
kto alebo čo
→ získalo akú capability
→ cez ktorý membership alebo token path
→ nad ktorým resource scope
→ na aký čas
→ s akým vlastníkom a auditom
```

Konkrétne názvy rolí, capabilities a dostupnosť custom roles sa môžu meniť podľa verzie, offeringu, tieru a konfigurácie GitLab inštancie. Pri produkčnom návrhu preto over aktuálnu permission matrix konkrétnej inštancie.

## 1. Mental model: resources, subjects a access paths

GitLab access vzniká kombináciou troch vrstiev:

- **Resource —** project, group, subgroup, branch, tag, environment, registry, package alebo iný chránený objekt.
- **Subject —** človek, external user, service account, access token, CI job identity alebo integrácia.
- **Access path —** direct membership, inherited membership, group sharing, token scope, administrator capability alebo policy viazaná na konkrétny resource.

Efektívne oprávnenie preto nemožno spoľahlivo určiť pohľadom na jednu obrazovku project members.

```text
subject
├─ direct project membership
├─ parent-group inheritance
├─ shared-group membership
├─ custom-role capability
├─ token alebo CI identity
└─ instance-level privilege

→ effective access nad konkrétnym resource
```

Pri audite sa nepýtaj iba „akú rolu používateľ vidí“. Pýtaj sa „cez ktorý path získal capability, ktorú práve vykonal“.

## 2. Namespace model

Namespace poskytuje adresu a organizačný kontext pre project alebo group.

```text
top-level group
├── platform
│   ├── payments
│   │   ├── api
│   │   └── worker
│   └── observability
└── product
    └── storefront
```

Project path je odvodený od hierarchy:

```text
gitlab.example.com/platform/payments/api
```

Namespace ovplyvňuje viac než clone URL. Môže meniť alebo určovať:

- **Inheritance —** členstvo a niektoré settings sa prenášajú z parent groups.
- **Registry coordinates —** container a package paths často obsahujú namespace.
- **Policy scope —** security, compliance, runners, variables alebo templates môžu byť definované vyššie v strome.
- **Ownership —** group môže reprezentovať tím, platformu, produkt alebo regulačnú boundary.
- **Lifecycle —** transfer alebo rename zasahuje consumers, integrations a deployment automation.

Hierarchy navrhuj podľa dlhodobého ownershipu a security boundaries, nie podľa dočasného organizačného diagramu. Príliš hlboký strom sťažuje vysvetlenie inheritance; príliš plytký strom vedie k príliš širokým permissions a policy scope-u.

## 3. Project ako delivery boundary

Project je základná pracovná jednotka, ktorá môže obsahovať:

- Git repository a refs,
- merge requests, approvals a discussions,
- issues a planning metadata,
- CI/CD pipelines, schedules a variables,
- runners a job artifacts,
- environments, deployments a releases,
- container a package registry,
- security findings a vulnerability records,
- wiki, snippets a Pages,
- project members, tokens a integrations.

Project boundary má zodpovedať kombinácii:

- **Ownershipu —** jeden tím vie rozumne rozhodovať o source, pipeline a release lifecycle.
- **Release unit —** artifact alebo komponent možno versionovať a nasadzovať s jasnou identitou.
- **Security boundary —** citlivé variables, runners a environments majú primeraný scope.
- **Lifecycle —** archivácia, transfer alebo deletion nevyžaduje neprimerane koordinovaný zásah.
- **Failure blast radiusu —** chybná project-level konfigurácia neohrozí nesúvisiace služby.

Project nevytvára automaticky bezpečnostnú izoláciu všetkých runtime systémov. CI identity, shared runners, group variables alebo external integrations môžu hranicu prekračovať.

## 4. Group a subgroup ako policy boundary

Group poskytuje spoločný kontext pre projekty a ďalšie subgroups. Môže centralizovať:

- membership a inherited roles,
- spoločné settings a templates,
- runners, variables alebo access tokens,
- compliance a security policy podľa dostupných features,
- audit, billing a usage governance,
- service accounts a organizačné integrations,
- project creation a transfer policy.

Subgroup je vhodná, keď treba delegovať ownership alebo oddeliť policy scope. Nie je vhodná iba preto, aby URL kopírovala org chart.

Príklad rozumného rozdelenia:

```text
company
├─ shared-platform       # centrálne platformové capabilities
├─ regulated-products   # prísnejšie policy a audit
└─ product-teams        # delegované ownership
```

Každá group má mať definované:

- účel a ownera,
- kto môže vytvárať projekty a subgroups,
- ktoré settings sa majú dediť,
- maximum prijateľného access scope-u,
- policy pre external users a sharing,
- lifecycle rename, transfer, archive a deletion.

## 5. Visibility nie je permission model

GitLab môže podľa konfigurácie podporovať private, internal alebo public visibility. Visibility určuje základný discovery a access model, ale neodpovedá na všetky otázky ochrany.

Pri visibility rozhodnutí zohľadni:

- source confidentiality,
- issue a merge-request metadata,
- pipeline logs a job artifacts,
- container/package registry exposure,
- Pages, wiki a snippets,
- forks a downstream pipelines,
- security findings,
- externých spolupracovníkov a compliance.

Public project nemusí znamenať, že každý smie pushovať alebo deployovať. Private project zase nie je automaticky bezpečný, ak široká parent group udeľuje Maintainer access alebo CI job publikuje citlivý artifact verejne.

## 6. Membership sources

Subjekt môže získať project access viacerými cestami:

- direct project membership,
- direct group membership,
- inheritance z parent group,
- project alebo group sharing s inou group,
- custom role naviazaná na základnú rolu,
- administrator alebo instance-level capability,
- dočasný membership s expiration,
- token alebo CI identity s konkrétnym scope-om.

Access review musí zachytiť minimálne:

```text
subject
+ source membershipu
+ granted role/capabilities
+ resource scope
+ expiration
+ granting actor
+ business owner
+ last use
```

Direct membership list bez inherited a shared paths je neúplný dôkaz.

## 7. Built-in role verzus konkrétna capability

Built-in role je balík capabilities. Nie je univerzálnym popisom všetkého, čo subjekt môže vykonať v každom kontexte.

GitLab môže podľa verzie a konfigurácie obsahovať role ako Guest, Planner, Reporter, Developer, Maintainer a Owner, prípadne custom alebo špecializované role. Konkrétne oprávnenia sa musia overiť v aktuálnej matrix.

Pri návrhu používaj tento postup:

1. Urči presnú operáciu, napríklad merge do protected branch alebo deployment do production.
2. Urči resource boundary, na ktorej sa operácia vykonáva.
3. Zisti, či capability vyplýva z role, protected-resource pravidla, token scope-u alebo kombinácie.
4. Vyber najnižší dostatočný access.
5. Zaveď expiration, audit a revocation cestu.

„Potrebuje Maintainer, lebo pipeline nefunguje“ je symptóm neanalyzovaného capability modelu.

## 8. Highest effective access

Keď subjekt získava prístup viacerými cestami, nižšia direct rola spravidla neobmedzí vyšší prístup získaný iným pathom.

```text
parent group: Maintainer
project direct membership: Developer
→ effective project access: Maintainer
```

Preto odobranie direct membershipu nemusí zmeniť reálne oprávnenia. Treba identifikovať všetky paths:

```text
project direct
+ subgroup
+ parent group
+ shared group
+ custom role
+ administrator state
→ effective capabilities
```

Dôležitý dôsledok: deny-like očakávanie nemožno automaticky odvodiť z nižšej role. Permission model treba navrhovať tak, aby široký parent access nevytváral potrebu „odoberania“ na každom child projekte.

## 9. Owner a Maintainer blast radius

Najvyššie role majú veľký organizačný a supply-chain blast radius. Môžu ovplyvniť members, protected resources, pipeline settings, integrations, variables alebo release proces podľa konkrétnej konfigurácie.

Owner používaj iba pre obmedzený počet dôveryhodných human alebo riadených non-human identities. Maintainer tiež nemá byť default rola celého tímu, ak vývojári potrebujú iba bežný source workflow.

Pri elevated access definuj:

- business dôvod,
- resource scope,
- permanentný alebo dočasný charakter,
- schvaľujúceho ownera,
- expiration alebo review interval,
- break-glass alternatívu,
- audit kritických operácií.

Jedna chýbajúca capability nemá viesť k parent-group Owner roli.

## 10. Group membership verzus direct membership

Group membership je vhodný pre stabilné tímy a opakovateľné access patterns. Prináša:

- centrálne onboarding/offboarding,
- konzistentný prístup vo viacerých projektoch,
- menší počet individuálnych assignments,
- jednoduchšiu pravidelnú recertifikáciu.

Riziká:

- príliš široká parent rola,
- nečakaný inherited access do nových projektov,
- access cez sharing mimo pôvodnej hierarchy,
- veľký blast radius nesprávnej membership zmeny.

Direct project membership používaj pre explicitnú výnimku alebo úzky scope. Každá výnimka má mať ownera, dôvod a podľa potreby expiration.

## 11. Group sharing

Project alebo group možno sprístupniť členom inej group. Sharing je druhý access graph, ktorý môže obísť očakávania založené iba na namespace strome.

Pred sharingom over:

- členstvo cieľovej group vrátane inherited a external users,
- maximálny udeľovaný access level,
- kto môže meniť membership cieľovej group,
- expiration a pravidelný review,
- citlivosť source, logs, artifacts a registry,
- možnosť ďalšieho nepriameho exposure,
- audit a revocation postup.

Zdieľanie s veľkou organizačnou group môže jedným kliknutím rozšíriť access na stovky identít. Preto má byť group sharing inventory súčasťou access review.

## 12. Custom roles

Custom role môže oddeliť konkrétnu capability od príliš širokej built-in role, ak ju daná GitLab verzia a tier podporujú.

Použi ju, keď:

- potreba je opakovateľná vo viacerých projektoch,
- built-in role udeľuje neprimerané capabilities,
- custom capability je platformou podporovaná a testovaná,
- existuje owner, dokumentácia a migration policy.

Custom role je vlastné security API. Potrebuje:

- stabilný názov a účel,
- versionovaný capability set,
- test nad reprezentatívnym projektom,
- pravidelný access review,
- kontrolu zmien a backward compatibility,
- postup pri zániku alebo nahradení role.

Neudržiavané custom roles môžu byť menej zrozumiteľné než opatrne použitá built-in rola.

## 13. Human a non-human identities

Rozlišuj minimálne:

- **Human user —** osobná identita viazaná na človeka, jeho lifecycle a MFA/SSO policy.
- **External user —** obmedzená identita mimo bežnej organizačnej dôveryhodnej populácie.
- **Service account —** riadená non-human identita s explicitným ownerom a účelom.
- **Project/group access token —** token viazaný na resource scope a definované token capabilities.
- **Deploy token —** identita určená na obmedzený registry/package alebo deployment prístup podľa konfigurácie.
- **CI job identity —** krátkodobý runtime subject odvodený od pipeline contextu.
- **OAuth alebo application integration —** externá aplikácia s delegovaným scope-om.

Osobný token vývojára nepoužívaj ako dlhodobú produkčnú integráciu. Offboarding človeka, zmena role alebo expirácia tokenu by inak nepredvídateľne zastavili službu.

## 14. Token lifecycle

Token je autentifikačný materiál a zároveň identity contract. Pre každý token eviduj:

- typ a resource scope,
- capabilities/scopes,
- ownera a účel,
- vytvorenie a expiration,
- rotation postup,
- posledné použitie,
- storage location,
- revocation a incident response.

Preferovaný model:

```text
pipeline/job identity
→ short-lived federated credential
→ minimum-scope external role
→ automatická expirácia
```

Dlhodobý static token používaj iba tam, kde nie je dostupná bezpečnejšia federácia, a zaveď kratšiu expiráciu, rotation a usage monitoring.

## 15. CI identities a fork trust boundary

Pipeline kód môže byť nedôveryhodný, najmä pri merge requestoch z fork-u alebo pri branches, ktoré menia CI konfiguráciu.

Threat model musí odpovedať:

- ktorá pipeline definícia sa vykonáva,
- v ktorom project kontexte,
- aké variables a tokens sú dostupné,
- či runner obsahuje persistentný state,
- kto môže spustiť pipeline v parent projekte,
- či job smie writeovať repository, registry alebo environment,
- ako sa odlišuje protected a unprotected ref.

Fork nesmie automaticky zdediť produkčné secrets alebo privileged runner context. Trust decision má byť vynútený platformovou policy, nie iba očakávaním reviewera.

## 16. Expiration a just-in-time access

Dočasný access má mať automatický koniec. Typické prípady:

- externý dodávateľ,
- incident alebo migration support,
- krátkodobý audit,
- elevated troubleshooting,
- zastupovanie ownera.

Expiration nie je náhrada okamžitej revokácie pri kompromitovaní. Ide o ochranu proti zabudnutému oprávneniu.

Pre citlivé capabilities preferuj just-in-time alebo time-bounded elevation:

```text
request
→ approval podľa rizika
→ krátky elevated access
→ audit operácií
→ automatické odobratie
→ následný review pri break-glass použití
```

## 17. Onboarding, role change a offboarding

Identity lifecycle musí pokrývať viac než prvotné pridanie používateľa.

### Onboarding

- priraď access cez správnu group,
- over least privilege,
- nastav SSO/MFA a external-user status podľa policy,
- urč ownera výnimiek,
- nedávaj permanentný direct access „dočasne“.

### Role alebo team change

- odstráň staré group memberships,
- znovu vyhodnoť direct access a tokens,
- over ownership projektov a approvals,
- skontroluj inherited permissions z bývalej organizačnej vetvy.

### Offboarding

- deaktivuj human identity podľa identity-provider procesu,
- revokuj personal tokens a sessions,
- prenes ownership schedules, bots a integrations,
- nahraď osobné credentials service identities,
- over audit kritických operácií pred odchodom.

## 18. Project transfer a rename

Transfer alebo namespace rename je identity, security a delivery migrácia.

Pred zmenou vytvor inventory:

- clone a API URLs,
- container/package coordinates,
- Pages a external URLs,
- inherited variables a runners,
- project/group access tokens,
- webhooks a integrations,
- protected branches, tags a environments,
- security/compliance policy,
- deployment identities a OIDC claims,
- downstream/upstream pipeline references,
- CODEOWNERS a approval groups.

Bezpečný lifecycle:

```text
inventory a dependency map
→ target-group permission review
→ migration plan
→ controlled transfer/rename
→ update consumers
→ verify CI, registry a deployment
→ monitor redirects
→ remove legacy references
```

Redirect je transition aid, nie trvalý dependency contract.

## 19. Effective-access review

Pravidelný review má začínať citlivými capabilities, nie abecedným zoznamom používateľov.

Kontroluj:

- Owner a Maintainer identities,
- kto môže meniť protected refs a environments,
- kto môže používať production credentials,
- group sharing a inherited access,
- external a dormant users,
- direct memberships bez ownera,
- custom roles a ich aktuálny capability set,
- service accounts a tokens bez expiration,
- nepoužívané credentials,
- projects s nejasným business ownerom.

Výstup reviewu musí byť akčný:

```text
remove
| reduce
| expire
| rotate
| document risk acceptance
| retain with evidence
```

Samotný export zoznamu členov nie je access review.

## 20. Audit a provenance administratívnej zmeny

Pre citlivé namespaces sleduj minimálne:

- membership add/remove/change,
- role elevation,
- group sharing,
- token creation, rotation a revocation,
- visibility change,
- project transfer/rename,
- protected-resource policy zmenu,
- owner count a custom-role zmenu,
- use of break-glass alebo administrator capability.

Audit event potrebuje ownera, retention a review proces. Log, ktorý nikto nevyhodnocuje, nepôsobí ako preventívny ani detekčný control.

## 21. Troubleshooting effective permissions

### Používateľ má vyšší access než project membership ukazuje

1. Skontroluj parent a ancestor groups.
2. Skontroluj group sharing.
3. Skontroluj custom role a špecializované capabilities.
4. Over administrator alebo instance-level state.
5. Zisti presný resource, na ktorom bola operácia vykonaná.

### Odobraná direct rola neznížila access

Vyšší inherited alebo shared path zostal aktívny. Odstráň zdroj vyššej capability; nižšia direct rola ho neprepisuje.

### Používateľ nevidí private project

Over membership source, expiration, external-user policy, group visibility, sharing a prípadné SSO/group-sync obmedzenia.

### Pipeline po transfere stratila variables alebo runner

Pôvodný project dedil group-level resources. Porovnaj starý a nový effective environment: variables, runner scope, policies, tokens a OIDC claims.

### Integrácia prestala po offboardingu človeka

Pravdepodobne používala personal token alebo osobnú OAuth identity. Nahraď ju riadenou non-human identitou a rotuj credentials.

## 22. Typické anti-patterny

### Všetci sú Maintainers

Ruší least privilege a separation of duties. Kompromitovaný účet môže zasiahnuť source, CI/CD aj deployment controls.

### Direct membership v každom projekte

Onboarding, offboarding a recertifikácia sa rozídu. Stabilné tímy spravuj cez groups a výnimky cez expirovateľný direct access.

### Parent-group Owner kvôli jednej operácii

Resource scope je neprimeraný potrebe. Použi užšiu rolu, custom capability alebo riadený workflow.

### Group sharing bez membership inventory

Nie je známe, koľko a akých identít prístup získalo.

### Osobný token ako produkčný service account

Identity lifecycle človeka sa stáva skrytou availability dependency.

### Token bez ownera, expiration a usage monitoringu

Nie je jasné, kto ho môže rotovať, či je ešte potrebný ani ako reagovať pri úniku.

### Visibility ako jediný security control

Visibility nechráni protected refs, CI secrets, registry writes ani production deployment permissions.

### Audit bez remediation procesu

Udalosti sa ukladajú, ale nevedú k revokácii, oprave policy ani risk acceptance.

## 23. Praktický rozhodovací rámec

Pri návrhu GitLab namespace a access modelu odpovedz:

1. Aký resource a lifecycle má project reprezentovať?
2. Ktoré boundaries patria na top-level group a ktoré na subgroup?
3. Aké policies a resources sa dedia?
4. Ktoré stabilné tímy majú group membership?
5. Ktoré direct memberships sú výnimky a kedy expirujú?
6. Ako sa počíta effective access cez všetky paths?
7. Ktoré capabilities sú najcitlivejšie?
8. Je built-in rola primeraná alebo treba custom role/workflow?
9. Ktoré non-human identities existujú a kto ich vlastní?
10. Môžu sa static credentials nahradiť federovanou job identity?
11. Ako sa oddelí trusted a untrusted pipeline context?
12. Čo sa stane pri team change a offboardingu?
13. Aký audit a review interval zodpovedá riziku?
14. Ako sa bezpečne vykoná transfer alebo rename?

## 24. Kontrolný checklist

- namespace hierarchy zodpovedá ownershipu a security boundaries;
- project boundary má jasný release a lifecycle model;
- effective access sa vyhodnocuje cez direct, inherited aj shared paths;
- Owner a Maintainer sú obmedzené a pravidelne reviewované;
- stable teams používajú group membership;
- direct výnimky majú ownera a expiration;
- custom roles majú versionovaný capability contract;
- external users majú explicitnú policy;
- non-human identities nie sú osobné účty vývojárov;
- tokens majú scope, ownera, expiration, rotation a usage audit;
- fork/branch pipeline nemá implicitný production trust;
- onboarding, role change a offboarding sú zdokumentované;
- project transfer má dependency inventory a validation plán;
- audit events vedú k remediation alebo risk decision.

## 25. Kontrolné otázky

1. Aký je rozdiel medzi projectom, group, subgroup a namespace?
2. Prečo group hierarchy predstavuje security a policy boundary?
3. Ako vzniká effective access pri viacerých membership paths?
4. Prečo nižšia direct rola neobmedzí vyšší inherited access?
5. Kedy je vhodnejší group membership a kedy direct membership?
6. Aké riziká vytvára group sharing?
7. Čo je rozdiel medzi built-in rolou a konkrétnou capability?
8. Kedy má zmysel custom role?
9. Prečo osobný token nie je vhodná service identity?
10. Čo musí obsahovať token lifecycle?
11. Prečo je fork pipeline samostatná trust boundary?
12. Čo sa musí vykonať pri zmene tímu alebo offboardingu?
13. Prečo je project transfer delivery a security migrácia?
14. Ako má vyzerať akčný access review?
15. Prečo audit log bez review procesu nestačí?

## Summary

GitLab permission model je graf subjects, resources a access paths, nie jednoduchý zoznam project roles. Group hierarchy určuje inheritance, policy scope a administratívny blast radius; effective access môže vzniknúť direct membershipom, parent groups, sharingom, custom role alebo non-human identitou. Dôveryhodný model vyžaduje least privilege, oddelenie human a service identities, expirovateľný access, token lifecycle, fork-pipeline trust policy, pravidelný effective-access review a auditovateľné transfery. Každú capability treba vedieť spätne vysvetliť konkrétnym access pathom a ownerom.

## Glossary impact

Relevantné pojmy: GitLab project, group, subgroup, namespace, resource scope, subject, direct membership, inherited membership, effective access, highest effective role, group sharing, built-in role, custom role, external user, service account, project access token, group access token, deploy token, CI job identity, access review a project transfer.

## Oficiálna dokumentácia

- [Roles and permissions](https://docs.gitlab.com/user/permissions/)
- [User permissions](https://docs.gitlab.com/auth/user_permissions/)
- [Project and group visibility](https://docs.gitlab.com/user/public_access/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Databázová kompatibilita počas deploymentu](../05-ci-cd-and-release/database-compatibility-during-deployment.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Merge requests a approvals →](merge-requests-and-approvals.md)
<!-- KNOWLEDGE-NAVIGATION:END -->