# Protected branches a environments

Protected branches a protected environments sú dve odlišné GitLab policy boundaries. Prvá chráni Git refs a merge flow. Druhá chráni deployment do citlivého runtime targetu. Bez oboch môže byť source history chránená, ale produkcia stále nasaditeľná neoprávneným jobom alebo používateľom.

## 1. Protected branch

Protected branch riadi najmä:

- kto môže pushovať,
- kto môže mergeovať,
- či je povolený force push,
- či sa vyžaduje Code Owner approval,
- ochranu kritických refs pred náhodnou zmenou alebo deletion,
- väzbu na approval a security policy.

Default branch je v GitLabe typicky chránená už pri vytvorení projektu, ale konkrétne pravidlá treba overiť.

## 2. Branch rules

Aktuálne GitLab UI sústreďuje ochranu branches do branch rules. Rule môže cieliť:

- presný branch name,
- wildcard pattern,
- default branch,
- všetky protected branches podľa konkrétnej policy.

Pri viacerých matching rules treba rozumieť ich kombinačnému správaniu. Pre niektoré nastavenia môže výsledok byť najviac permissive kombinácia, preto prekrývajúce sa group a project pravidlá audituj explicitne.

## 3. Push vs. merge permission

Rozlišuj:

### Allowed to push and merge

Umožňuje priamo aktualizovať protected ref a môže obísť merge request review flow.

### Allowed to merge

Umožňuje dokončiť MR do protected branch po splnení ďalších podmienok.

Bezpečný default pre hlavný branch je často:

```text
direct push: nobody alebo veľmi obmedzené automation identities
merge: Maintainers/eligible roles cez MR
force push: disabled
```

Konkrétna policy závisí od veľkosti tímu a incident/release modelu.

## 4. Force push

Force push prepisuje ref history a môže odstrániť commits, approvals alebo auditovateľnú väzbu. Povolenie má byť výnimočné a viazané na:

- konkrétny use case,
- obmedzené identities,
- audit,
- incident postup,
- ochranu tags a release refs.

Rutinný force push na default branch je anti-pattern.

## 5. Protected tags

Branch a tag môžu mať rovnaký názov. Ak chrániš release branch alebo pattern, zváž zodpovedajúcu ochranu tagov.

Protected tags riadia, kto môže vytvárať alebo meniť refs používané na:

- release pipelines,
- artifact versioning,
- production deployment,
- package publishing,
- compliance evidence.

Mutable alebo neautorizovaný release tag môže spustiť deployment iných bytes, než boli schválené.

## 6. Group-level branch protection

Top-level group môže podľa GitLab capability definovať branch rules platné pre projekty v group. Výhody:

- konzistentný default,
- centrálna governance,
- menší configuration drift,
- jednoduchší audit.

Riziká:

- nečakané prekrývanie s project rules,
- príliš všeobecný wildcard,
- nemožnosť lokálne opraviť nesprávnu group policy,
- rozdielne potreby legacy a moderných projektov.

Group policy potrebuje versionovaný rollout a exception lifecycle.

## 7. Code Owner approval

Protected branch môže vyžadovať approval od Code Owners pre zmenené paths. Fungovanie závisí od:

- správneho `CODEOWNERS` matchu,
- eligible Code Owner membershipu a role,
- protected target branch,
- branch-rule nastavenia,
- approval rules a tieru.

CODEOWNERS file bez branch enforcementu môže poskytovať iba reviewer suggestion.

## 8. Merge request enforcement

Ak chceš všetky zmeny viesť cez MR:

- zakáž direct push na protected branch,
- nastav required approvals podľa rizika,
- vyžaduj úspešnú pipeline,
- rieš unresolved discussions,
- obmedz force push,
- používaj merge train/queue pri concurrency,
- chráň automation tokeny.

Branch protection sama nemusí vyžadovať kvalitný review; musí byť kombinovaná s merge policy.

## 9. Unprotect permission

Používateľ schopný branch unprotect môže následne obísť ochranu. Preto audituj:

- kto môže meniť/unprotect rules,
- group vs. project ownership,
- API automation,
- custom roles,
- break-glass identities,
- audit events.

Pri regulovaných projektoch môže byť potrebné obmedziť unprotect na úzky okruh alebo central automation.

## 10. Protected environment

Protected environment obmedzuje, kto môže deployovať do konkrétneho environmentu, napríklad production.

Typicky riadi:

- allowed to deploy users/groups/roles,
- deployment approvals podľa dostupnosti,
- environment-specific permissions,
- access k protected variables v spojení s ref policy,
- production deployment boundary.

Protected environments sú podľa aktuálnej GitLab dokumentácie Premium/Ultimate capability.

## 11. Environment nie je branch

Branch reprezentuje source/ref state. Environment reprezentuje runtime target a deployment history.

Nesprávny model:

```text
main branch = production environment
```

Lepší model:

```text
commit/artifact digest
→ pipeline evidence
→ deploy job
→ protected production environment
→ deployment record
```

Ten istý branch môže produkovať deploymenty do viacerých environmentov a rovnaký environment môže prijímať artifacts z riadeného promotion flow.

## 12. Allowed to deploy

Allowed-to-deploy policy má zohľadniť:

- human vs. CI identity,
- environment tier,
- change risk,
- protected ref,
- manual job ownership,
- group membership inheritance,
- service account scope,
- emergency process.

Používateľ schopný spustiť pipeline nemusí automaticky dostať právo deployovať production job.

## 13. Protected variables

CI/CD variable môže byť označená protected, aby bola dostupná iba pipelines na protected refs podľa GitLab trust modelu.

Ochrana variable nerieši všetko:

- malicious pipeline code na trusted ref,
- príliš široké runner permissions,
- log leakage,
- downstream job artifacts,
- environment scope,
- long-lived cloud credentials.

Preferuj short-lived federation a environment-scoped identity pred statickým produkčným secretom.

## 14. Environment-scoped variables

Environment scope môže obmedziť variable napríklad na:

```text
production
review/*
staging
```

Over wildcard precedence, matching a fallback. Nesprávny scope môže:

- odhaliť production secret review app,
- spôsobiť deployment s chýbajúcou hodnotou,
- použiť staging credential v produkcii.

Variable scope musí byť testovaný ako policy.

## 15. Deployment approvals

Deployment approval má byť použitý pre neautomatizovateľné alebo vysokorizikové rozhodnutia. Potrebuje:

- jasného eligible approvera,
- evidence summary,
- separation of duties,
- väzbu na artifact digest a environment,
- expiry/freshness,
- audit trail,
- emergency override.

Mechanické kliknutie bez evidence nepridáva významnú bezpečnosť.

## 16. Deployment jobs

Deployment job má deklarovať environment a zachovať:

- artifact digest,
- environment name/tier,
- external URL podľa potreby,
- action a deployment status,
- pipeline/job identity,
- config revision,
- rollout strategy.

Job, ktorý mení produkciu bez GitLab environment metadata, oslabuje deployment history a audit.

## 17. Review apps

Dynamic environments pre branches/MRs potrebujú:

- unique names a URLs,
- izolované credentials,
- quotas,
- auto-stop/cleanup,
- safe test data,
- network isolation,
- protection pred untrusted fork code.

Review app nesmie zdediť production secrets iba preto, že používa rovnaký deployment template.

## 18. Environment tiers

Environment names môžu byť ľubovoľné, preto environment tier pomáha klasifikovať production, staging, testing, development a ďalšie targety.

Tier ovplyvňuje interpretáciu deployment metrics a governance. Nekonzistentné názvy/tier metadata znižujú spoľahlivosť reportingu.

## 19. Deployment freeze

Freeze window môže zabrániť plánovaným deploymentom počas citlivého obdobia. Nemá nahrádzať:

- branch protection,
- protected environment,
- quality gates,
- emergency process,
- recovery capability.

Freeze bez break-glass postupu môže blokovať kritickú opravu.

## 20. Separation of duties

Možný model:

```text
Developer: vytvára zmenu a MR
Reviewer/Code Owner: schvaľuje source zmenu
Pipeline: vytvára a overuje artifact
Release/Operations identity: promotionuje artifact
Protected environment approver: povoľuje high-risk production exposure
```

Nie každý tím potrebuje päť ľudí, ale jedna kompromitovaná identita by nemala nekontrolovane meniť source, policy, secrets aj production.

## 21. Emergency access

Break-glass workflow potrebuje:

- úzky scope,
- strong authentication,
- explicitný dôvod,
- časové obmedzenie,
- audit a alert,
- povinný post-event review,
- následnú rotation/revocation.

Dočasné unprotect bez obnovenia policy je závažný configuration drift.

## 22. Policy as Code

GitLab API alebo security/compliance policy možno použiť na audit a enforcement:

- protected branches/tags,
- approval rules,
- environment protection,
- allowed deployers,
- variable scope,
- project settings.

Automatizácia musí byť idempotentná a rozlišovať intended exception od driftu.

## 23. Troubleshooting

### Developer môže pushnúť priamo na main

Over všetky matching branch rules, allowed-to-push settings, group rules a unprotect status.

### Code Owner approval sa nevyžaduje

Over protected target branch, CODEOWNERS match, eligible membership a require-Code-Owner setting.

### Production deploy job je pre používateľa nedostupný

Skontroluj protected environment allowed-to-deploy policy, role inheritance, manual job trigger identity a environment name match.

### Protected variable chýba

Pipeline ref nemusí byť protected, variable environment scope nesedí alebo ide o fork/untrusted context.

### Group rule a project rule dávajú nečakané oprávnenie

Vyhodnoť všetky matching rules a ich combinačné správanie; nepredpokladaj, že prísnejšie pravidlo automaticky vyhrá.

### Review app dostala production credential

Okamžite rotuj secret, oprav environment scope a audituj všetky job logs/artifacts.

## 24. Anti-patterny

### Protected main, ale production job môže spustiť každý Developer

Source boundary je chránená, runtime boundary nie.

### Maintainer môže unprotect, push, re-protect bez auditu

Policy je ľahko obíditeľná jednou identitou.

### Production secrets na všetkých protected branches

Release branch alebo kompromitovaný protected ref môže získať neprimeraný access.

### Environment protection podľa názvu, ktorý job nepoužíva konzistentne

Deployment môže vytvoriť nový neprotected environment s podobným názvom.

### Emergency = vypnutie všetkých ochrán

Zvyšuje incident blast radius a ruší traceability.

## 25. Kontrolné otázky

1. Aký je rozdiel medzi protected branch a protected environment?
2. Prečo oddeliť allowed-to-push od allowed-to-merge?
3. Aké riziko prináša force push?
4. Prečo treba chrániť aj release tags?
5. Ako sa kombinujú group a project branch rules?
6. Kedy Code Owner approval skutočne blokuje merge?
7. Ako fungujú protected a environment-scoped variables?
8. Čo má obsahovať deployment approval?
9. Prečo review apps potrebujú samostatnú trust boundary?
10. Ako navrhnúť break-glass bez trvalého oslabenia policy?

## Glossary impact

Relevantné pojmy: protected branch, branch rule, protected tag, allowed to push, allowed to merge, force push, unprotect permission, protected environment, allowed to deploy, protected variable, environment-scoped variable, deployment approval, review app, environment tier a deployment freeze.

## Oficiálna dokumentácia

- [Protected branches](https://docs.gitlab.com/user/project/repository/branches/protected/)
- [Protected environments](https://docs.gitlab.com/ci/environments/protected_environments/)
