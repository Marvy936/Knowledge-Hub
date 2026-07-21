# Projects, groups a permissions

GitLab organizuje source code, CI/CD, issues, security a deployment metadata do projektov, ktoré sú uložené v namespaces. Groups a subgroups poskytujú spoločné členstvo, policy, billing a organizačnú hierarchiu pre viac projektov.

## 1. Namespace model

```text
top-level group
├── subgroup
│   ├── project A
│   └── project B
└── project C
```

Project path je odvodený od namespace hierarchy:

```text
gitlab.example.com/platform/payments/api
```

Presun projektu alebo zmena group path môže meniť clone URL, registry paths, package coordinates a integračné odkazy. Redirects nemajú nahrádzať riadenú migráciu consumers.

## 2. Project

Project je základná pracovná jednotka obsahujúca podľa zapnutých features napríklad:

- Git repository,
- merge requests,
- issues a planning,
- CI/CD pipelines,
- variables,
- environments a deployments,
- container/package registry,
- security findings,
- wiki a snippets,
- project members a access policy.

Project boundary má zodpovedať ownershipu, release unit, security boundary a lifecycle komponentu, nie iba náhodnému priečinku zdrojového kódu.

## 3. Group a subgroup

Group poskytuje spoločný kontext pre projekty a ďalšie subgroups:

- membership a inherited access,
- group-level settings,
- shared runners a variables,
- compliance/security policy podľa tieru,
- group access tokens a service accounts podľa dostupnosti,
- project templates,
- audit a billing boundary.

Subgroups umožňujú delegovať ownership, ale príliš hlboká hierarchy komplikuje inheritance, discovery a policy reasoning.

## 4. Visibility

GitLab podporuje visibility úrovne podľa konfigurácie inštancie:

- private,
- internal,
- public.

Private project je dostupný iba oprávneným členom; samotná znalosť URL neposkytuje prístup. Visibility nie je náhradou za správne membership a protected-resource pravidlá.

Pri návrhu visibility zohľadni:

- source confidentiality,
- artifact a registry exposure,
- issue/MR metadata,
- pipeline logs,
- public forks,
- compliance,
- externých spolupracovníkov.

## 5. Membership sources

Používateľ môže získať access:

- priamym členstvom v projekte,
- členstvom v group,
- zdedením z parent group,
- zdieľaním projektu alebo group s inou group,
- custom role podľa licencie a konfigurácie,
- dočasným membershipom s expiration.

Pri audite nestačí pozerať iba direct project members. Potrebné je zistiť origin membershipu a všetky inherited paths.

## 6. Role model

GitLab role definujú rastúce oprávnenia. Aktuálny model môže podľa verzie a tieru zahŕňať napríklad:

- Guest,
- Planner,
- Reporter,
- Developer,
- Maintainer,
- Owner,
- Security Manager alebo custom roles tam, kde sú dostupné.

Konkrétne permissions sa môžu meniť medzi GitLab verziami a tiers. Pri citlivom návrhu over aktuálnu permissions matrix inštancie.

## 7. Highest effective role

Ak používateľ získa viac membershipov, efektívne oprávnenia zodpovedajú najvyššiemu prístupu, ktorý sa na resource vzťahuje.

Príklad:

```text
parent group: Maintainer
project direct membership: Developer
→ effective project access: Maintainer
```

Nižšia direct role neobmedzí vyšší inherited access. Na skutočné zníženie oprávnení treba odstrániť alebo zmeniť zdroj vyššieho membershipu.

## 8. Owner a Maintainer

### Owner

Owner je najvyššia business/administrative rola pre group alebo project ownership podľa modelu GitLabu. Má sa prideľovať obmedzenému počtu dôveryhodných identít.

### Maintainer

Maintainer typicky spravuje repository, merge requests, CI/CD nastavenia a project members, ale nemá automaticky predstavovať plnú organizačnú administráciu.

Nedávaj Owner iba preto, že používateľ potrebuje jednu chýbajúcu operáciu. Použi delegáciu, custom role alebo automatizačnú identitu s užším scope-om.

## 9. Human a non-human identities

Rozlišuj:

- bežných používateľov,
- external users,
- administrators,
- service accounts,
- project/group access tokens,
- deploy tokens,
- CI job identities,
- OAuth/application integrations.

Osobný access token vývojára nie je vhodná dlhodobá produkčná service identity.

## 10. Least privilege

Praktický postup:

1. definuj potrebnú operáciu,
2. urč resource scope,
3. vyber najnižšiu dostačujúcu rolu alebo token scope,
4. obmedz environment/branch/tag podľa potreby,
5. nastav expiration,
6. zapni audit a rotation,
7. pravidelne reviewuj nevyužité oprávnenia.

„Developer pre istotu“ alebo „Maintainer pre pipeline“ často skrýva nepochopený permission model.

## 11. Group-level membership

Výhody:

- centrálna správa tímu,
- konzistentný access vo viacerých projektoch,
- jednoduchší onboarding/offboarding,
- menší počet direct memberships.

Riziká:

- nečakaný inherited access,
- príliš široká parent-group rola,
- zdieľané projekty mimo pôvodnej hierarchy,
- ťažšie vysvetlenie efektívneho prístupu.

Preferuj group membership pre stabilné tímy a direct project membership pre explicitné výnimky s ownerom a expiry.

## 12. Group sharing

Project alebo group možno zdieľať s inou group. Pred zdieľaním over:

- kto sú direct members cieľovej group,
- aký maximum access level sa udeľuje,
- či sa access propaguje ďalej,
- viditeľnosť membershipu,
- external users,
- expiration a audit.

Zdieľanie s veľkou organizačnou group môže neúmyselne sprístupniť resource stovkám ľudí.

## 13. Custom roles

Custom role môže oddeliť konkrétne permission od širokej built-in role. Použi ju, keď:

- potrebuješ opakovateľnú organizačnú rolu,
- built-in rola je príliš široká,
- permission je podporovaná custom-role modelom,
- lifecycle a ownership role sú jasné.

Custom roles zvyšujú governance komplexitu. Každá potrebuje dokumentovaný účel, ownera, versionovanie a pravidelný review.

## 14. Expiration

Dočasný prístup má mať dátum skončenia. Typické prípady:

- externý dodávateľ,
- incident support,
- audit,
- migration project,
- dočasná elevated rola.

Expiration nenahrádza okamžité odobratie kompromitovaného alebo už nepotrebného accessu.

## 15. Project transfer a namespace zmeny

Pred presunom projektu over:

- permissions v target group,
- inherited CI variables,
- runner availability,
- registry/package paths,
- webhooks a integrations,
- protected branches/environments,
- security/compliance policies,
- Pages alebo external URLs,
- access tokens a deploy credentials.

Transfer je security a delivery zmena, nie iba organizačné upratanie.

## 16. Forks

Fork môže mať odlišnú visibility, members, CI trust a secrets boundary. Pri merge requestoch z fork-u:

- nedôveruj automaticky source pipeline kódu,
- neexponuj protected variables nedôveryhodnému refu,
- používaj target-project policy,
- kontroluj, kto môže spustiť pipeline v parent kontexte.

Fork workflow musí byť súčasťou threat modelu.

## 17. Audit

Pre citlivé groups/projects sleduj:

- membership add/remove/change,
- role elevation,
- group sharing,
- token creation/revocation,
- visibility changes,
- project transfer,
- protected-resource policy changes,
- owner count,
- expired a dormant access.

Audit log bez review procesu iba uchováva udalosti.

## 18. Access review

Pravidelne vyhodnocuj:

- kto má Owner/Maintainer,
- odkiaľ sa access dedí,
- nepoužívané direct memberships,
- service identities bez ownera,
- tokens bez expiry,
- external users,
- zdieľané groups,
- users po zmene tímu,
- citlivé projekty s príliš širokým scope-om.

Výstup review má viesť ku konkrétnym removals alebo risk acceptance.

## 19. Troubleshooting

### Používateľ má vyšší access než project membership ukazuje

Skontroluj parent groups, shared groups, custom roles a administrator status. Platí highest effective role.

### Používateľ nevidí private project

Over membership source, expiration, external-user obmedzenia, group visibility a project sharing.

### Po presune projektu pipeline stratila variables

Variables alebo runners boli zdedené zo starej group. Zmapuj dependencies pred transferom.

### Odobratá direct rola neznížila access

Vyšší access zostal inherited z group alebo sharingu.

### Service integration používa osobný token bývalého člena

Nahraď ho explicitnou non-human identity, rotuj secret a audituj použitie.

## 20. Anti-patterny

### Všetci sú Maintainers

Ruší separation of duties a zvyšuje blast radius chybnej alebo kompromitovanej identity.

### Direct membership v každom projekte

Onboarding/offboarding a audit sa stávajú nekonzistentné.

### Parent group Owner pre jednu úlohu

Príliš široký scope vzhľadom na potrebu.

### Token bez ownera a expiry

Nie je jasné, kto ho smie rotovať alebo zrušiť.

### Visibility sa považuje za jedinú security kontrolu

Nechráni protected refs, CI secrets ani deployment permissions.

## 21. Kontrolné otázky

1. Aký je rozdiel medzi projectom, group a subgroup?
2. Ako vzniká effective role pri viacerých memberships?
3. Prečo nižšia direct rola nezníži vyšší inherited access?
4. Kedy používať group a kedy direct project membership?
5. Aké riziká má group sharing?
6. Kedy má zmysel custom role?
7. Ako odlíšiť human a non-human identities?
8. Čo treba overiť pred project transferom?
9. Prečo sú fork pipelines samostatná trust boundary?
10. Čo má obsahovať pravidelný access review?

## Glossary impact

Relevantné pojmy: GitLab project, GitLab group, subgroup, namespace, direct membership, inherited membership, effective role, group sharing, custom role, external user, service account, project access token, group access token a project transfer.

## Oficiálna dokumentácia

- [Roles and permissions](https://docs.gitlab.com/user/permissions/)
- [User permissions](https://docs.gitlab.com/auth/user_permissions/)
- [Project and group visibility](https://docs.gitlab.com/user/public_access/)
