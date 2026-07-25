# Projects, groups a permissions

GitLab spája source code, merge requests, CI/CD, registries, security findings a deployment metadata do projektov uložených v namespaces. Permission model preto nechráni iba čítanie repository. Jedna príliš široká rola môže umožniť meniť pipeline, sprístupniť secrets, publikovať release artifact alebo zasiahnuť produkčný environment.

Cieľom kapitoly nie je zapamätať si tabuľku rolí. Cieľom je vedieť pri každej operácii vysvetliť:

```text
kto alebo čo
→ vykonáva akú capability
→ nad ktorým resource
→ cez ktorý access path
→ s akou platnosťou, zodpovednosťou a auditom
```

Konkrétne názvy rolí a capabilities sa môžu meniť podľa GitLab verzie, offeringu, tieru a konfigurácie inštancie. Mentálny model resource, subject a access path však zostáva stabilný.

## 1. Priebežný scenár: od členstva po produkčný dosah

Predstav si project `company/payments/api`. Vývojár Martin je priamo v projekte uvedený ako `Developer`. Na prvý pohľad by teda nemal meniť chránené settings ani spravovať production deployment policy.

Martin je však zároveň členom parent group `company` s rolou `Maintainer`. Táto rola sa zdedí do subgroup `payments` a následne do projektu `api`. Jeho effective access preto nie je `Developer`, ale vyšší access získaný z parent group.

```text
company: Martin = Maintainer
└── payments
    └── api: Martin = Developer

výsledok nad api:
Maintainer capability získaná inheritance cestou
```

Keď administrátor odstráni Martinovo direct project membership, jeho reálne oprávnenia sa nezmenia. Odstránil iba jednu cestu, nie zdroj vyššieho accessu. Tento príklad ukazuje základnú vlastnosť GitLab permission modelu: access je graf, nie jeden riadok v zozname project members.

## 2. Mental model: resources, subjects a access paths

Každé permission rozhodnutie kombinuje tri otázky.

**Resource** je objekt, nad ktorým sa operácia vykonáva. Môže ísť o group, project, branch, tag, environment, registry repository, package, job artifact alebo security finding. Dva resources v rovnakom projekte nemusia mať rovnakú ochranu: používateľ môže mať právo mergeovať source, ale nemusí mať právo deployovať do production environmentu.

**Subject** je identita, ktorá operáciu žiada. Nemusí to byť človek. Subjectom môže byť používateľ, external user, service account, project access token, group access token, deploy token, CI job token alebo integračná identita.

**Access path** vysvetľuje, prečo subject capability získal. Access môže prísť priamym membershipom, inheritance z parent group, zdieľaním s inou group, custom rolou, token scope-om, protected-resource pravidlom alebo instance-level administrátorskou právomocou.

```text
subject
├── direct project membership
├── parent-group inheritance
├── group sharing
├── custom-role capability
├── token alebo CI identity
└── instance-level privilege

→ effective capability nad konkrétnym resource
```

Pri audite sa preto nepýtaj iba „akú rolu používateľ vidí“. Pýtaj sa „cez ktorý path získal capability, ktorú práve vykonal“.

## 3. Namespace nie je iba časť URL

Namespace je adresný a administratívny priestor, v ktorom existuje project alebo group. Hierarchia môže vyzerať takto:

```text
company
├── shared-platform
│   ├── ci-components
│   └── observability
├── regulated-products
│   └── payments
│       ├── api
│       └── worker
└── product-teams
    └── storefront
```

Project path `company/regulated-products/payments/api` je iba viditeľný dôsledok tejto hierarchie. Dôležitejšie je, že parent groups môžu ovplyvniť membership, runners, variables, access tokens, templates, security policies, project creation a ďalšie settings.

Ak `regulated-products` reprezentuje prísnejšiu regulačnú boundary, presunutie projektu z tejto group do `product-teams` nie je kozmetická zmena URL. Projekt môže stratiť zdedenú security policy, protected variables alebo runner pool a súčasne získať iné membership paths.

Hierarchy preto navrhuj podľa dlhodobého ownershipu, bezpečnostnej hranice a lifecycle-u. Org chart sa môže zmeniť každého pol roka; namespace migration zasahuje clone URLs, registry coordinates, OIDC claims, integrations aj deployment automation.

## 4. Group a subgroup ako policy boundaries

Group centralizuje spoločný kontext viacerých projektov. Stabilný tím môže dostať membership na group a automaticky získať primeraný access do jej projektov. Platformový tím môže na group úrovni poskytovať runners alebo CI components. Security tím môže podľa dostupných features aplikovať policy na celý subtree.

Subgroup má zmysel vtedy, keď sa mení aspoň jedna významná boundary:

- ownership rozhodnutí,
- maximálny scope oprávnení,
- security alebo compliance policy,
- spoločný release či operational lifecycle,
- zodpovednosť za vytváranie a transfer projektov.

Samotná potreba „mať pekne usporiadané URL“ nie je dostatočný dôvod. Každá ďalšia úroveň inheritance komplikuje vysvetlenie effective accessu.

### Praktický návrh

V predchádzajúcej hierarchii `regulated-products` môže udeľovať iba úzky Owner access, vyžadovať centrálne security policies a zakázať nekontrolované group sharing. `product-teams` môže delegovať väčšiu administratívnu autonómiu jednotlivým subgroups.

Takéto rozdelenie zachytáva rozdielny risk model. Nekopíruje iba názvy oddelení.

## 5. Project ako delivery boundary

Project je pracovná jednotka, ktorá typicky spája repository, merge requests, CI/CD, registries, environments, releases, findings a identities. To z neho robí prirodzenú delivery boundary, ale nie automaticky izolovanú bezpečnostnú zónu.

Dobrá project boundary zodpovedá štyrom otázkam:

1. **Kto vlastní zmenu?** Jeden tím vie rozhodovať o source, pipeline a release contracte.
2. **Čo je release unit?** Artifact alebo komponent možno versionovať a nasadzovať s jednoznačnou identitou.
3. **Aký je security scope?** Secrets, runners a environments možno obmedziť bez neprimeraného zdieľania.
4. **Aký je lifecycle a blast radius?** Transfer, archivácia alebo chybná project-level zmena nezasiahnu nesúvisiace produkty.

Príliš veľký monorepo project môže spojiť mnoho tímov, citlivých variables a release tokov do jednej administratívnej boundary. Príliš jemné delenie zas vytvára množstvo cross-project tokens, pipelines a package dependencies. Správna hranica je trade-off medzi samostatnosťou a koordinačnými nákladmi.

## 6. Visibility nie je kompletný permission model

Visibility určuje základnú discoverability a prístup k obsahu podľa konfigurácie inštancie. Neurčuje však, kto smie meniť protected branch, spustiť privilegovaný job alebo deployovať do production.

Public project môže mať prísne chránený write a deployment flow. Private project môže byť rizikový, ak parent group udeľuje stovkám ľudí Maintainer access alebo ak CI job publikuje citlivé artifacts na verejný endpoint.

Pri visibility rozhodnutí posudzuj samostatne:

- source a issue metadata,
- pipeline logs a artifacts,
- package a container registry,
- security findings,
- Pages, wiki a snippets,
- fork a downstream-pipeline behavior.

Visibility je jedna vrstva exposure, nie náhrada least privilege.

## 7. Ako vzniká membership

Human access môže vzniknúť direct project membershipom alebo membershipom v group. Group membership je vhodný pre stabilné tímy, pretože onboarding, offboarding a recertifikácia sa vykonávajú centrálne.

Direct project membership je vhodný pre úzku výnimku. Napríklad externý špecialista môže dostať trojtýždňový Reporter access iba do jedného projektu. Výnimka má mať dôvod, ownera a expiration; inak sa po skončení spolupráce zmení na dormant access.

Group sharing vytvára ďalšiu cestu. Project alebo group môže byť sprístupnený členom inej group. Tým sa do access graphu nepridáva iba názov cieľovej group, ale celý jej membership vrátane inherited a external users.

### Príklad nečakaného rozšírenia

Project `payments/api` sa zdieľa s group `company/contractors` na úrovni Reporter. O mesiac neskôr niekto pridá do `contractors` novú partnerskú subgroup. Bez zmeny samotného projektu sa rozšíri počet identít, ktoré vidia repository, issues alebo artifacts.

Sharing preto potrebuje inventory cieľovej group, maximálny access level, expiration a pravidelný review.

## 8. Rola je balík capabilities

Built-in rola nie je univerzálna odpoveď na otázku, čo používateľ smie. Je to balík capabilities, ktorého reálny efekt závisí od resource contextu, protected rules a feature setu GitLabu.

Namiesto otázky „akú rolu mu dáme?“ postupuj takto:

```text
požadovaná operácia
→ konkrétny resource
→ potrebná capability
→ dostupný role/policy mechanizmus
→ najnižší dostatočný access
→ expiration a audit
```

Ak človek potrebuje spustiť jeden deployment job, riešením nemusí byť Maintainer rola nad celým projektom. Vhodnejší môže byť protected-environment permission, úzky custom role model alebo riadený release workflow.

Custom role má význam, keď sa rovnaká úzka capability opakuje vo viacerých projektoch a built-in rola je neprimerane široká. Custom role však sama potrebuje versionovaný capability contract. Platform update môže zmeniť dostupné oprávnenia a tým aj praktický význam role.

## 9. Highest effective access

Ak subject získava prístup viacerými cestami, nižšia direct rola spravidla neobmedzí vyššiu capability získanú iným pathom.

```text
parent group: Maintainer
shared group: Reporter
project direct: Developer

→ effective capabilities obsahujú Maintainer oprávnenia
```

Permission model teda nefunguje ako firewall rule set, kde lokálny deny automaticky prepisuje parent allow. Ak potrebuješ užšiu boundary, musíš zmeniť zdroj širokého accessu alebo organizačné rozdelenie.

### Diagnostická metóda

Pri nečakanej operácii rekonštruuj:

1. presný resource a operáciu;
2. subject identity použitú pri operácii;
3. direct membership;
4. parent a ancestor memberships;
5. group sharing paths;
6. custom roles a protected-resource rules;
7. token scopes alebo administrator state.

Výsledkom nemá byť iba „má Maintainer“. Výsledkom má byť konkrétny path, ktorý možno odstrániť alebo obmedziť.

## 10. Owner a Maintainer blast radius

Najvyššie role môžu meniť membership, CI/CD settings, protected resources, variables, integrations alebo release controls podľa konkrétnej konfigurácie. Jedna kompromitovaná identita tak môže zasiahnuť source aj delivery supply chain.

Owner a Maintainer preto nemajú byť default odpoveďou na každý problém s oprávnením. Pri elevated access zaznamenaj:

- prečo je potrebný,
- nad akým resource scope-om,
- či je permanentný alebo dočasný,
- kto ho schválil,
- kedy sa znovu skontroluje,
- aká je break-glass alternatíva.

Malý tím môže mať viac ľudí s vysokou rolou z praktických dôvodov. To nemení potrebu MFA, auditovania citlivých zmien a oddelenia production credentials od bežného source workflowu.

## 11. Human a non-human identities

Automatizácia nemá používať osobný účet vývojára ako skrytú service identity. Keď človek odíde alebo mu expiruje token, pipeline zlyhá. Pri kompromitácii navyše nie je jasné, ktoré akcie vykonal človek a ktoré automatizácia.

Rozlišuj minimálne:

- **Human user —** interaktívna identita podliehajúca onboarding/offboarding procesu.
- **External user —** používateľ s obmedzeným organizačným trustom a explicitnou access policy.
- **Service account —** riadená neľudská identita s vlastníkom a jasným účelom.
- **Project alebo group access token —** token viazaný na resource scope a role/capabilities.
- **Deploy token —** úzka distribučná identita pre registry alebo package operácie podľa scope-u.
- **CI job identity —** krátkodobý context konkrétneho jobu, projektu a pipeline.

Každá non-human identita potrebuje ownera, minimum scope, expiration, rotation, usage telemetry a revocation postup. „Token nesmie expirovať, lebo by pipeline prestala fungovať“ iba presúva availability riziko do budúcnosti.

## 12. CI identities a trust context

Pipeline job je vykonávanie repository-defined code-u. To, že job patrí private projektu, ešte neznamená, že má dostať production credentials.

Trust závisí od toho, čo sa vykonáva:

- kód z chráneného default branchu po review,
- kód z feature branchu,
- merge-request pipeline,
- pipeline z externého forku,
- included template z iného projektu,
- manuálne spustený release workflow.

Fork pipeline je samostatná trust boundary. Nedôveryhodný contributor môže upraviť build script tak, aby odoslal všetky dostupné secrets. Ochrana preto musí kombinovať pipeline context, protected variables, runner isolation a environment permissions.

## 13. Onboarding, zmena roly a offboarding

Access lifecycle sa nezačína pridaním používateľa a nekončí odstránením jedného membershipu.

Pri onboardingu definuj tím, group membership, minimálnu rolu, expiration dočasných výnimiek a potrebné silné autentizačné controls. Pri zmene pracovnej náplne odstráň staré access paths pred alebo súčasne s pridelením nových.

Offboarding musí kontrolovať:

```text
human memberships
+ shared-group paths
+ personal a impersonation tokens
+ SSH/GPG keys
+ OAuth/integration ownership
+ schedules a bot workflows
+ break-glass membership
```

Ak po odchode človeka prestane fungovať produkčná integrácia, systém pravdepodobne používal osobnú identitu tam, kde mala byť riadená service identity.

## 14. Expiration a dormant access

Expiration je control iba vtedy, keď je nastavená primerane a systém sleduje blížiace sa ukončenie. Permanentný direct access pre krátky projekt vytvára dormant privilege, ktorý si nikto nemusí všimnúť roky.

Pri pravidelnom review kombinuj membership s usage evidence. Nepoužitý privileged access nemusí byť automaticky neoprávnený, ale vyžaduje vysvetlenie. Naopak nedávne použitie nie je dôkaz, že scope je stále primeraný.

Výsledok reviewu musí byť akčný:

```text
retain with evidence
| reduce
| expire
| remove
| rotate
| document temporary risk acceptance
```

Export zoznamu členov bez rozhodnutia nie je access review.

## 15. Project transfer a rename

Transfer mení namespace a môže zmeniť effective prostredie projektu. Pred presunom vytvor dependency inventory:

- clone a submodule URLs,
- container a package coordinates,
- CI includes a multi-project triggers,
- group variables, runners a policies,
- project/group access tokens,
- OIDC subject alebo claims,
- webhooks a external integrations,
- Pages, environments a deployment automation.

Po transfere nestačí overiť, že repository sa otvorí. Spusti trusted pipeline, over registry pull/push, protected resources, environment access a audit membershipov.

Project transfer je delivery a security migrácia, nie administratívne premenovanie.

## 16. Break-glass a administratívny bypass

Incident môže vyžadovať dočasné zvýšenie oprávnení. Bez definovaného procesu však tím často urobí parent-group Ownera, vypne ochrany a zabudne ich obnoviť.

Break-glass workflow potrebuje:

1. explicitný incident alebo dôvod;
2. úzky resource scope;
3. krátku platnosť;
4. silnú autentizáciu;
5. audit a okamžitý alert;
6. povinné obnovenie policy a revokáciu;
7. post-event review.

Úspešný incident zásah nekončí opravou služby. Končí až vtedy, keď je access model znovu v schválenom stave.

## 17. Audit a provenance administratívnej zmeny

Citlivá administratívna udalosť má odpovedať na otázky kto, čo, nad čím, kedy a prečo. Sleduj najmä role elevation, membership zmeny, group sharing, token lifecycle, visibility, transfer, protected-resource policy a použitie break-glass capability.

Audit log sám osebe nič nevynucuje. Potrebuje retention, ownera a proces, ktorý z relevantnej udalosti vytvorí remediation alebo risk decision.

## 18. Kompletný príklad access rozhodnutia

Tím potrebuje, aby release engineer mohol spustiť production deployment, ale nemohol meniť source ani CI configuration.

Slabé riešenie:

```text
release engineer → project Maintainer
```

Tým získa rozsiahle capabilities nad repository, variables a settings.

Silnejší návrh:

```text
release engineer
→ minimálna project visibility potrebná na evidence
→ allowed-to-deploy nad protected production environmentom
→ deployment approval alebo manual action podľa risku
→ short-lived cloud workload identity pre konkrétny job
→ audit deploymentu a expiration ľudského accessu
```

Tento model oddeľuje source permission, GitLab deployment permission a cloud runtime authorization. Kompromitácia jednej vrstvy neudeľuje automaticky plnú kontrolu nad všetkými ostatnými.

## 19. Troubleshooting effective permissions

### Používateľ má vyšší access než ukazuje project membership

Najprv over parent a ancestor groups, potom group sharing a custom roles. Následne skontroluj token alebo administrator context. Neznižuj iba direct project rolu; tá nemusí byť zdrojom capability.

### Odobranie direct membershipu nič nezmenilo

Subjekt naďalej získava access iným pathom. Rekonštruuj celý access graph a odstráň skutočný zdroj vyššej capability.

### Pipeline po transfere stratila variables alebo runner

Projekt dedil resources zo starej group. Porovnaj effective konfiguráciu pred a po transfere: variables, runner scope, policies, tokens, includes a OIDC claims.

### Integrácia prestala po offboardingu človeka

Integrácia používala personal token alebo osobnú OAuth identitu. Nahraď ju service accountom alebo resource-scoped tokenom, rotuj credential a skontroluj audit použitia.

### External user vidí viac projektov, než sa očakávalo

Skontroluj parent membership a group sharing. External flag sám osebe nevytvára deny nad každou inherited cestou.

## 20. Typické anti-patterny

### Všetci sú Maintainers

Least privilege sa nahradí dôverou v to, že nikto neurobí chybu. Kompromitovaný účet môže zasiahnuť source aj delivery controls.

### Direct membership v každom projekte

Onboarding, offboarding a recertifikácia sa rozídu. Stabilné tímy patria do groups; direct membership má byť explicitná výnimka.

### Parent-group Owner kvôli jednej operácii

Scope je neprimeraný potrebe. Hľadaj konkrétnu capability alebo riadený workflow.

### Group sharing bez inventory

Nie je známe, koľko identít access získalo ani kto mení membership cieľovej group.

### Osobný token ako production service account

Lifecycle človeka sa stane skrytou availability a security dependency.

### Visibility ako jediný security control

Visibility nechráni protected refs, CI secrets, registry writes ani production deployments.

### Audit bez remediation

Udalosti sa ukladajú, ale nevedú k revokácii, oprave policy ani risk acceptance.

## 21. Praktický rozhodovací rámec

Pri návrhu namespace a access modelu odpovedz:

1. Aký business a delivery lifecycle project reprezentuje?
2. Ktoré boundaries patria do top-level group a ktoré do subgroup?
3. Ktoré memberships, variables, runners a policies sa dedia?
4. Aká konkrétna capability je potrebná a nad ktorým resource?
5. Cez ktoré paths môže subject access získať?
6. Je built-in rola primeraná, alebo je potrebný užší workflow?
7. Ktoré identity sú human a ktoré non-human?
8. Majú tokens ownera, expiration, rotation a usage audit?
9. Ako sa oddeľuje trusted a untrusted pipeline context?
10. Ako funguje onboarding, role change a offboarding?
11. Čo sa zmení pri transferi alebo rename projektu?
12. Ako sa break-glass access obnoví do normálneho stavu?

## 22. Kontrolný checklist

- namespace hierarchy zodpovedá ownershipu a security boundaries;
- project má jasný release a lifecycle model;
- effective access sa vyhodnocuje cez direct, inherited aj shared paths;
- vysoké role sú obmedzené a periodicky reviewované;
- stabilné tímy používajú group membership;
- direct výnimky majú dôvod, ownera a expiration;
- custom roles majú dokumentovaný capability contract;
- non-human identities nie sú osobné účty vývojárov;
- tokens majú minimum scope, expiration, rotation a revocation;
- fork pipeline nemá implicitný production trust;
- project transfer má dependency inventory a validačný plán;
- break-glass končí obnovením policy;
- audit udalosti vedú k rozhodnutiu alebo remediation.

## 23. Kontrolné otázky

1. Prečo GitLab permission model nie je iba zoznam project roles?
2. Aký je rozdiel medzi resource, subjectom a access pathom?
3. Ako namespace hierarchy ovplyvňuje security a delivery?
4. Prečo nižšia direct rola neobmedzí vyšší inherited access?
5. Kedy použiť group membership a kedy direct membership?
6. Aké riziko vytvára group sharing?
7. Prečo je rola iba balík capabilities?
8. Kedy môže byť custom role lepšia než Maintainer?
9. Prečo osobný token nie je vhodná service identity?
10. Ako sa líši fork-pipeline trust od protected-branch pipeline?
11. Čo musí zahŕňať offboarding okrem membershipu?
12. Prečo je project transfer bezpečnostná a delivery migrácia?
13. Ako má vyzerať akčný access review?
14. Kedy je break-glass workflow skutočne ukončený?
15. Prečo audit log bez remediation procesu nestačí?

## Summary

GitLab access je graf subjects, resources a access paths. Group hierarchy určuje inheritance, policy scope a administratívny blast radius; effective capability môže vzniknúť direct membershipom, parent group, sharingom, protected-resource pravidlom alebo tokenom. Dôveryhodný model používa least privilege, oddelenie human a non-human identít, expirovateľné výnimky, rekonštruovateľný access path, pravidelnú recertifikáciu a auditovateľný break-glass. Každú citlivú operáciu treba vedieť spätne vysvetliť konkrétnym subjectom, resource-om, capability a ownerom.

## Glossary impact

Relevantné pojmy: GitLab project, group, subgroup, namespace, resource, subject, access path, direct membership, inherited membership, effective access, highest effective role, group sharing, built-in role, custom role, external user, service account, project access token, group access token, deploy token, CI job identity, access review a project transfer.

## Oficiálna dokumentácia

- [Roles and permissions](https://docs.gitlab.com/user/permissions/)
- [User permissions](https://docs.gitlab.com/auth/user_permissions/)
- [Project and group visibility](https://docs.gitlab.com/user/public_access/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Databázová kompatibilita počas deploymentu](../05-ci-cd-and-release/database-compatibility-during-deployment.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Merge requests a approvals →](merge-requests-and-approvals.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
