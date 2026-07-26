# Projects, groups a permissions

GitLab project nie je iba Git repository. Spája source, merge requests, pipelines, registries, variables, environments, releases a security evidence. Permission rozhodnutie preto môže ovplyvniť celý delivery chain.

Nosný model kapitoly je access graph:

```text
subject
→ jedna alebo viac access paths
→ role, token scope alebo resource policy
→ effective capability nad konkrétnym resource
→ vykonaná operácia
→ audit, expiration a revocation lifecycle
```

Samotná project role nevysvetľuje výsledok. Používateľ môže získať vyšší access z parent group, shared group, custom role, tokenu, protected-resource pravidla alebo administrátorskej identity. Pri incidentoch treba rekonštruovať cestu capability, nie iba prečítať jeden riadok v zozname členov.

Konkrétne role, capabilities a dostupné governance controls sa menia podľa GitLab verzie, offeringu, tieru a konfigurácie inštancie. Stabilný je model subjectu, resource-u, access pathu a effective decisionu.

## 1. Priebežný scenár: Atlas Payments

GitLab hierarchy Atlasu vyzerá takto:

```text
atlas
├── platform
│   ├── ci-components
│   └── observability
├── regulated-products
│   └── payments
│       ├── api
│       └── worker
└── product-teams
    └── storefront
```

Vývojár Martin má v `atlas/regulated-products/payments/api` direct rolu `Developer`. Zároveň je členom top-level group `atlas` s rolou `Maintainer` kvôli staršej platformovej úlohe.

```text
atlas: Martin = Maintainer
└── regulated-products
    └── payments
        └── api: Martin = Developer
```

Effective access nad projektom `api` zahŕňa vyššie capabilities zdedené z parent group. Keď administrátor odstráni Martinovo direct project membership, jeho reálny access sa nezmení. Odstránil jednu cestu, nie zdroj capability.

Neskôr sa projekt presunie z `regulated-products` do `product-teams`. Repository funguje, ale pipeline stratí inherited protected variables a trusted runner pool. Súčasne sa zmení namespace používaný v registry coordinates, includes a workload-identity claims.

Tento scenár spája hlavné témy kapitoly:

```text
namespace hierarchy
→ membership inheritance
→ effective capability
→ human/non-human identity
→ project transfer
→ audit a revocation
```

## 2. Resource, subject a access path

Každé access rozhodnutie začni troma otázkami.

### Resource

Resource je objekt, nad ktorým sa operácia vykonáva:

- group alebo subgroup;
- project;
- branch alebo tag;
- environment;
- container/package registry;
- pipeline, job artifact alebo schedule;
- variable, token alebo security finding.

Dva resources v rovnakom projekte nemusia mať rovnakú protection boundary. Človek môže mergeovať source, ale nesmie deployovať do production environmentu.

### Subject

Subject je identita žiadajúca operáciu:

- human user;
- external user;
- service account;
- project alebo group access token;
- deploy token;
- CI job token alebo workload identity;
- administrator alebo break-glass identity.

### Access path

Access path vysvetľuje, prečo subject capability získal:

```text
direct project membership
parent-group inheritance
invited/shared group
custom member role
protected-resource rule
token scope a role
instance-level privilege
```

Výsledný verdict je odvodený:

```text
subject identity
+ všetky applicable access paths
+ resource-specific policy
+ current context
→ effective capability
```

## 3. Namespace je administratívna a security boundary

Namespace určuje viac než URL. Parent groups môžu ovplyvniť:

- membership a role inheritance;
- group sharing;
- variables a access tokens;
- runner scope;
- CI includes a components;
- security/compliance policy;
- project creation a transfer;
- registry a package coordinates.

Subgroup má zmysel, keď sa mení aspoň jedna významná boundary:

```text
ownership
security/compliance policy
maximálny access scope
release alebo operational lifecycle
project-administration responsibility
```

Hierarchia kopírujúca krátkodobý org chart vytvára časté transfery a neprehľadný inheritance graph. Stabilnejšie je modelovať dlhodobý ownership, risk a delivery lifecycle.

## 4. Project ako delivery boundary

Project typicky spája:

```text
repository
→ merge a pipeline policy
→ artifact/registry
→ environment a deployment history
→ release a security evidence
```

Dobrá project boundary odpovedá:

1. Kto vlastní source a release contract?
2. Čo je samostatná release unit?
3. Ktoré secrets, runners a environments patria k rovnakému trust scope-u?
4. Aký je blast radius transferu, archivácie alebo policy chyby?

Príliš veľký project môže spojiť nesúvisiace tímy a produkčné identities. Príliš jemné delenie vytvára veľa cross-project tokens, triggers a dependency contracts.

## 5. Membership graph a highest effective access

Human access môže vzniknúť:

- direct project membershipom;
- direct group membershipom;
- inheritance z ancestor group;
- project/group sharingom;
- synchronizovaným enterprise alebo directory membershipom podľa inštancie.

Ak subject získava viac paths, nižšia direct rola spravidla neobmedzí vyšší inherited access.

```text
parent group: Maintainer
shared group: Reporter
project direct: Developer

→ effective project access zahŕňa Maintainer capabilities
```

Access model nie je firewall s implicitným lokálnym deny. Ak treba užšiu boundary, musí sa odstrániť alebo rozdeliť zdroj širokého accessu.

## 6. Group membership, direct výnimka a sharing

Stabilný tím patrí do group membershipu, pretože onboarding, offboarding a recertifikácia majú jeden owner a lifecycle.

Direct project membership je vhodná úzka výnimka:

```text
external specialist
→ Reporter iba v jednom projekte
→ dôvod + owner
→ expiration o tri týždne
→ usage review a removal
```

Group sharing pridáva celý ďalší membership graph. Ak `payments/api` zdieľa access s `atlas/contractors`, zmena membershipu v `contractors` môže rozšíriť project access bez zmeny projektu.

Sharing potrebuje:

- inventory cieľovej group;
- maximálny access level;
- ownera oboch strán;
- expiration alebo review cadence;
- audit zmien membershipu.

## 7. Rola je balík capabilities, nie cieľ návrhu

Namiesto otázky „akú rolu mu dáme?“ postupuj:

```text
požadovaná operácia
→ konkrétny resource
→ potrebná capability
→ najnižší vhodný role/policy mechanizmus
→ expiration a audit
```

Release engineer, ktorý potrebuje spustiť production deployment, nemusí dostať `Maintainer` nad repository. Vhodnejší model môže kombinovať:

```text
minimum project visibility
+ allowed-to-deploy nad protected environmentom
+ deployment approval
+ short-lived cloud identity pre job
```

Custom role má hodnotu, keď sa rovnaká úzka capability opakuje. Jej capability contract však musí byť versionovaný a znovu overený pri GitLab upgrade-e.

## 8. Human a non-human identities

Automatizácia nemá používať osobný účet vývojára ako skrytú service identity.

```text
human user
→ interaktívny lifecycle, MFA, onboarding/offboarding

service account alebo resource token
→ jasný owner, účel, scope, expiration, rotation, usage telemetry

CI job identity
→ krátkodobý context konkrétneho projektu, pipeline a jobu
```

Personal token v produkčnej integrácii spája availability s pracovným pomerom človeka. Pri offboardingu pipeline zlyhá; pri incidente sa nedá spoľahlivo oddeliť human a automation activity.

Každá non-human identita potrebuje:

- ownera a business purpose;
- minimum role/scope;
- expiration alebo explicitnú výnimku;
- rotation a revocation;
- usage telemetry;
- závislosti, ktoré po revokácii zlyhajú.

## 9. Pipeline trust nie je odvodený iba z private projektu

CI job vykonáva repository-defined code. Trust sa mení podľa contextu:

```text
protected default branch po review
feature branch
merge-request pipeline
external fork
included template z iného projektu
manual release workflow
```

Untrusted contributor môže upraviť script tak, aby odoslal secrets alebo publikoval artifact. Preto sa oddelí:

```text
untrusted verification
→ immutable evidence/artifact
→ trusted publication/deployment entrypoint
```

Protected variables, runner isolation, token scope a environment authorization musia korelovať s pipeline contextom.

## 10. Access lifecycle

### Onboarding

Definuj tím, group membership, minimálnu rolu, silnú autentizáciu a expiration dočasných výnimiek.

### Role change

Odstráň staré access paths pred alebo súčasne s pridaním nových. Inak sa permissions kumulujú.

### Offboarding

Kontroluj celý graph:

```text
memberships a shared groups
personal/impersonation/access tokens
SSH a signing keys
OAuth a integration ownership
pipeline schedules a bot workflows
break-glass access
external cloud identities
```

### Recertifikácia

Výsledkom nie je export členov, ale rozhodnutie:

```text
retain with evidence
| reduce
| expire
| remove
| rotate
| temporary risk acceptance
```

## 11. Project transfer je delivery a security migrácia

Pred presunom Atlas projektu vytvorí dependency inventory:

- clone, submodule a API URLs;
- registry/package coordinates;
- CI includes a multi-project triggers;
- inherited variables, runners a policies;
- project/group access tokens;
- workload-identity subject/claims;
- webhooks, Pages a external integrations;
- protected branches, tags a environments.

Po transfere nestačí otvoriť repository. Treba overiť:

```text
trusted pipeline
registry pull/push
resolved includes
runner eligibility
protected variables
deployment identity
effective memberships a sharing paths
```

## 12. Break-glass je dočasný state transition

```text
incident alebo urgentný risk
→ explicitná elevated identity/workflow
→ úzky resource a časový scope
→ silná autentizácia
→ audit a alert
→ zásah
→ revokácia a obnova policy
→ post-event review
```

Incident nie je uzavretý, kým access model nie je späť v schválenom stave. Permanentný Owner vytvorený kvôli jednej havárii je neuzavretý incident control.

## 13. Worked failure: direct membership bolo odstránené, deployment access zostal

Po Martinovom presune administrátor odstránil jeho `Developer` membership z `payments/api`. O týždeň Martin stále dokázal spustiť production deployment.

### Nesprávna hypotéza

```text
GitLab cache ešte nepropagovala removal
```

Opakované odoberanie direct membershipu nič nezmenilo.

### Skutočný mechanizmus

```text
Martin je Maintainer v parent group atlas
→ capability sa dedí do payments/api
→ protected environment povoľuje Maintainers
→ direct project membership nebol rozhodujúci path
```

### Dôsledok

Offboarding ticket bol označený ako hotový, ale production capability zostala. Audit evidoval správneho aktora, no tím najprv analyzoval nesprávny membership source.

### Trvalá náprava

- odstrániť alebo zúžiť parent-group membership;
- oddeliť platform a product administration boundaries;
- používať deployment-specific capability namiesto širokého Maintainer accessu;
- access review musí zobrazovať origin každého membership pathu;
- offboarding overuje konkrétne sensitive operations, nie iba zoznam direct members.

## 14. Worked failure: transfer zachoval source, ale rozbil trusted delivery

Projekt sa presunul z `regulated-products/payments` do `product-teams/payments`.

```text
repository transfer prejde
→ clone redirect funguje
→ pipeline vznikne
→ inherited protected variables chýbajú
→ job sa presunie na iný runner pool
→ workload identity claim používa nový namespace
→ production deploy zlyhá
```

### Príčina

Transfer plan považoval project za repository. Nezahŕňal inherited delivery a identity dependencies.

### Recovery

Atlas pause-nul release, porovnal effective configuration pred a po transfere, obnovil explicitné trusted dependencies, aktualizoval OIDC trust a až potom zopakoval deployment.

### Trvalá náprava

Project transfer dostal machine-readable dependency manifest a post-transfer validation vrátane registry, runnera, variables, policies, tokens a environment authorization.

## 15. Kauzálny diagnostický walkthrough

Symptom: používateľ, ktorý už nie je direct project member, stále dokáže spustiť production deployment.

### Krok 1 — identifikuj presnú operáciu a subject

```text
operation = play deployment job D882
runtime target = production
actor = Martin human identity
project = atlas/regulated-products/payments/api
```

Bez presnej operácie by sa mohol zameniť project read access, pipeline trigger a environment deployment capability.

### Krok 2 — formuluj konkurenčné hypotézy

```text
H1: inherited parent-group membership
H2: invited/shared group membership
H3: custom role alebo protected-environment rule
H4: job používa service identity nezávislú od Martinovho accessu
H5: Martin je administrator alebo používa iný token/session
H6: audit zobrazuje trigger actor, ale deployment vykonal iný authorized job subject
```

### Krok 3 — vyber diskriminačné observation points

- membership origin a ancestor graph testujú H1;
- invited-group sources testujú H2;
- effective environment deploy rules testujú H3;
- pipeline/job token a cloud identity audit testujú H4/H6;
- session/token/admin audit testuje H5.

Atlas zistí parent `Maintainer` membership a environment rule povoľujúcu Maintainers. Job aj cloud audit patria legitímnej CI identity, ale právo spustiť privileged transition získal Martin cez H1/H3.

### Krok 4 — odstráň skutočný path

Zníženie project direct role nemá efekt. Atlas odstráni parent membership, pridá úzky environment deployment workflow a invaliduje aktívne sessions/tokens podľa potreby.

### Krok 5 — over pôvodný outcome

```text
Martin nevidí privileged play action
API attempt je denied
žiadny alternatívny shared/inherited path neostáva
production job naďalej funguje pre určeného release engineera
cloud workload identity ostáva job-scoped
```

### Krok 6 — vráť learning do control modelu

Finding sa mení na effective-access report, operation-based offboarding test a pravidlo, že parent-group Maintainer nesmie byť implicitný production deployer.

## 16. Diagnostický runbook

1. Urči actor, operation, resource a čas.
2. Rozlíš human trigger identity od job/token/runtime identity.
3. Zostav direct, inherited, shared, custom-role a token paths.
4. Vyhodnoť resource-specific policy a protected context.
5. Over administrator, impersonation a break-glass state.
6. Nájdite path, ktorý skutočne poskytol capability.
7. Odstráň alebo zúž tento path, nie iba viditeľnú direct rolu.
8. Rotuj/revokuj credentials a sessions podľa incident scope-u.
9. Over denied aj legitímny allowed outcome.
10. Aktualizuj onboarding, transfer alebo offboarding control.

## 17. Referenčné pravidlá

- Effective access je výsledok access graphu.
- Project role bez origin pathu nie je úplné vysvetlenie.
- Namespace hierarchy je delivery a security boundary.
- Stabilné tímy patria do groups; direct membership je riadená výnimka.
- Group sharing pridáva celý cudzí membership graph.
- Rola je balík capabilities, nie návrhový cieľ.
- Human a service identities majú oddelený lifecycle.
- Private project nie je automaticky trusted pipeline context.
- Project transfer musí validovať inherited delivery dependencies.
- Break-glass končí revokáciou a obnovou policy.

## 18. Časté omyly

### „Odstránili sme direct membership, access zmizol“

Inherited alebo shared path môže zostať.

### „External user je automaticky izolovaný“

Treba analyzovať všetky applicable membership a sharing paths.

### „Dajme mu Maintainer, aby vedel spustiť jeden job“

Široká project capability nie je náhrada úzkej environment operácie.

### „Private project znamená bezpečné CI“

Untrusted branch alebo included code môže stále získať privilegovaný runtime.

### „Transfer je iba zmena URL“

Mení inheritance, identities, includes, registry coordinates a policies.

## 19. Zhrnutie

Dôveryhodný GitLab access model je:

```text
stabilná namespace boundary
→ explicitné resources a subjects
→ rekonštruovateľné access paths
→ najnižšia potrebná capability
→ oddelený human/service lifecycle
→ effective-state audit
→ operation-based revocation a verification
```

Permission troubleshooting sa nekončí vetou „má Maintainer“. Končí identifikáciou konkrétneho pathu, ktorý capability poskytol, jeho odstránením alebo obmedzením a overením, že zakázaná operácia už neprejde bez poškodenia legitímneho delivery flowu.

## Kontrolné otázky

1. Prečo effective access nemožno odvodiť iba z direct project role?
2. Aký je rozdiel medzi resource, subjectom a access pathom?
3. Ako namespace ovplyvňuje delivery a security?
4. Prečo nižšia direct rola neobmedzí vyšší inherited access?
5. Kedy použiť group membership a kedy direct výnimku?
6. Aký blast radius vytvára group sharing?
7. Prečo je osobný token nevhodná service identity?
8. Čo treba overiť po project transfere?
9. Ako sa odlišuje pipeline trigger actor od runtime identity?
10. Kedy je break-glass lifecycle uzavretý?

## Oficiálna dokumentácia

- [Roles and permissions](https://docs.gitlab.com/user/permissions/)
- [Project members](https://docs.gitlab.com/user/project/members/)
- [Sharing projects and groups](https://docs.gitlab.com/user/project/members/sharing_projects_groups/)
- [Groups](https://docs.gitlab.com/user/group/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Databázová kompatibilita počas deploymentu](../05-ci-cd-and-release/database-compatibility-during-deployment.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Merge requests a approvals →](merge-requests-and-approvals.md)
<!-- KNOWLEDGE-NAVIGATION:END -->