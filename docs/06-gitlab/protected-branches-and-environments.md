# Protected branches a environments

Protected branches, protected tags a protected environments chránia rozdielne časti delivery systému. Branch a tag policy chráni Git refs a source-to-build trust. Environment policy chráni runtime mutation a production exposure. Bez oboch môže byť mainline dôsledne reviewovaná, ale neoprávnený job alebo používateľ stále dokáže nasadiť ľubovoľný artifact do produkcie.

```text
protected branch/tag
→ kto smie meniť dôveryhodný source alebo release ref

protected environment
→ kto smie meniť citlivý runtime target
```

Konkrétne capabilities, rule precedence a dostupnosť environment approvals sa môžu meniť podľa GitLab verzie, offeringu, tieru a konfigurácie. Produkčná policy musí byť overená na konkrétnej inštancii.

## 1. Mental model: dve authorization boundaries

Source a runtime authorization sú samostatné:

```text
source actor
→ push alebo merge do protected ref
→ pipeline vytvorí immutable artifact

runtime actor/job identity
→ promotion evidence
→ deployment do protected environmentu
```

Dôležitý dôsledok: používateľ oprávnený mergeovať source nemusí byť oprávnený nasadiť produkciu. Naopak, deployment automation nemá automaticky dostať právo meniť source alebo branch policy.

## 2. Protected branch subject

Protected branch rule sa vzťahuje na konkrétny ref alebo pattern. Chráni najmä:

- priamy push,
- merge do branchu,
- force push a history rewrite,
- deletion alebo neúmyselnú zmenu kritického refu,
- Code Owner alebo approval enforcement v kombinácii s MR policy,
- dôveryhodný trigger pre pipeline, variables alebo release flow.

Protection nie je vlastnosť názvu `main`. Je to výsledok aktuálne aplikovateľných branch rules.

## 3. Branch-rule resolution

Rule môže cieliť presný branch, default branch alebo wildcard pattern. Pri viacerých matching rules treba explicitne určiť effective policy.

Auditný postup:

```text
branch name
→ všetky matching project rules
→ všetky relevantné group/inherited rules
→ capability-specific combination
→ effective push/merge/force/unprotect behavior
```

Nespoliehaj sa na intuitívne „najprísnejšie pravidlo určite vyhrá“. Kombinačná semantics sa môže líšiť podľa settingu a GitLab verzie. Prekrývajúce patterns preto testuj reprezentatívnymi identities.

Príklad rizikového overlapu:

```text
release/* → iba release managers
*         → Developers môžu pushovať
```

Ak effective combination ostane príliš permissive, všeobecné pravidlo môže oslabiť zamýšľanú release ochranu.

## 4. Allowed to push verzus allowed to merge

Tieto capabilities majú rozdielny význam.

### Allowed to push

Umožňuje aktualizovať protected ref priamo. Môže obísť:

- merge-request review,
- approval rules,
- unresolved discussions,
- merge-result pipeline,
- merge train alebo queue,
- path-based ownership controls.

### Allowed to merge

Umožňuje dokončiť MR po splnení ostatných policy podmienok. Neznamená automaticky právo pushovať priamo.

Bezpečný default pre kritický mainline:

```text
direct push: nobody alebo úzko scoped automation
merge: eligible role cez MR
force push: disabled
unprotect: silne obmedzené
```

Automation identity s direct-push právom musí mať explicitný účel, immutable input, audit a obmedzenie na konkrétny workflow.

## 5. Direct-push bypass

Ak actor smie pushovať priamo, branch protection môže formálne existovať, ale review lifecycle je obíditeľný.

Pre každú direct-push výnimku eviduj:

- identity a jej ownera,
- povolený use case,
- branch scope,
- token alebo workload-identity scope,
- allowed commit/source provenance,
- audit a alerting,
- expiration alebo pravidelnú recertifikáciu.

Príklady legitímnej automation:

- bot aktualizujúci striktne definovaný generated file,
- release automation vytvárajúca chránený manifest,
- mirror alebo synchronization workflow s overeným source.

Aj vtedy môže byť bezpečnejšie vytvoriť bot MR než priamy push.

## 6. Force push a history rewrite

Force push môže zmeniť commit graph, odstrániť commits a narušiť väzbu medzi approval, pipeline a source identity.

Riziká:

- schválený SHA prestane byť reachable,
- release tag alebo artifact provenance ukazuje na odstránenú históriu,
- audit a incident reconstruction sa skomplikujú,
- downstream branches a forks sa rozídu,
- malicious actor môže skryť predchádzajúcu zmenu.

Ak je force push výnimočne potrebný:

```text
incident/change record
→ úzky actor scope
→ backup pôvodného refu
→ vykonanie a audit
→ validation nového refu
→ obnova ochrany
→ downstream communication
```

Rutinný force push na default alebo release branch je anti-pattern.

## 7. Unprotect ako capability escalation

Actor schopný odstrániť protection môže následne vykonať operáciu, ktorú pôvodná policy zakazovala. Unprotect je preto vyššia capability než samotný push alebo merge.

Audituj:

- project a group Owners,
- custom roles s policy-management capabilities,
- API automation tokens,
- administrator identities,
- break-glass accounts,
- kto môže zmeniť branch rules a znovu ich aplikovať.

Dočasný unprotect musí mať:

- explicitný dôvod a subject,
- schválenie podľa rizika,
- automatický alebo overený restoration krok,
- audit refs zmenených počas okna,
- post-event review.

Unprotect bez dôkazu opätovného zapnutia vytvára configuration drift.

## 8. Protected tags

Tag môže byť release trigger, package version alebo auditný pointer. Protected tags riadia, kto smie vytvárať alebo meniť relevantné tag refs.

Chráň najmä tags používané na:

- production release pipelines,
- artifact/package publication,
- version a changelog automation,
- signing alebo provenance workflows,
- support a backport lines.

Tag nie je content identity. Release record má stále zachovať commit SHA a artifact digest.

Bezpečný tag lifecycle:

```text
validated release subject
→ authorized tag creation
→ tag pipeline overí subject a policy
→ immutable artifact publication
→ release record
```

Prepísateľný alebo široko vytvárateľný release tag môže nasadiť iné bytes, než boli reviewované.

## 9. Code Owner enforcement

CODEOWNERS súbor sám osebe nemusí blokovať merge. Blocking behavior závisí od:

- target branch protection,
- matching path patternu,
- eligible Code Owner membershipu,
- branch/approval rule nastavenia,
- dostupnej GitLab capability.

Testuj aspoň:

- bežný source path,
- nested a wildcard path,
- rename/delete operáciu,
- samotný CODEOWNERS súbor,
- absent ownera,
- viac matching ownership rules.

Ak owner nie je dostupný, policy potrebuje riadený fallback, nie Maintainer bypass bez evidence.

## 10. Protected environment subject

Environment je runtime target a deployment-history boundary, nie synonymum branchu.

```text
artifact digest
+ config revision
+ deployment job identity
+ target environment
+ rollout policy
→ deployment subject
```

Protected environment obmedzuje, kto alebo čo smie vykonať runtime mutation. Môže zahŕňať allowed deployers, deployment approvals alebo ďalšie controls podľa dostupných features.

```text
main branch ≠ production environment
```

Rovnaký mainline artifact môže prechádzať stagingom a produkciou. Produkčný environment môže prijímať iba konkrétny promoted digest bez ohľadu na branch name.

## 11. Environment identity a názov

GitLab environment identity vzniká z názvu deklarovaného deployment jobom. Nekonzistentné alebo útočne zvolené názvy môžu obísť očakávanú policy.

Rizikové varianty:

```text
production
prod
Production
production-new
prod/us-east
```

Preto definuj:

- kanonické environment naming rules,
- environment tier metadata,
- allowed patterns v shared deployment template,
- lint/policy kontrolu job definitions,
- zákaz ľubovoľného runtime mena z nedôveryhodného inputu,
- inventory aktívnych environments.

Protected `production` nepomôže, ak job nasadí rovnaký runtime pod novým neprotected názvom.

## 12. Allowed to deploy

Allowed-to-deploy policy odpovedá, ktorá human alebo CI identity môže vykonať deployment do konkrétneho environmentu.

Vyhodnocuj:

- actor alebo job identity,
- project/group membership path,
- protected ref context,
- environment name match,
- manual job ownership,
- service-account scope,
- approval state,
- emergency policy.

Právo spustiť pipeline alebo manual job nie je automaticky právo deployovať. Deployment job musí prejsť protected-environment authorization pri reálnom targete.

## 13. Deploy job ako privileged program

Deployment job je privilegovaný program. Jeho trust závisí od:

- pipeline definition revision,
- source/ref contextu,
- included templates a scripts,
- runner/executor trustu,
- effective variables a credentials,
- artifact digestu,
- environment declaration,
- cloud alebo cluster identity.

Bezpečný model oddeľuje:

```text
untrusted branch/MR verification
→ immutable artifact
→ trusted deployment entrypoint
→ short-lived environment identity
→ protected environment
```

Branch pipeline nemá dostať produkčné cloud credentials len preto, že obsahuje job s názvom `deploy-production`.

## 14. Protected variables

Protected variable je dostupná iba v určenom trusted ref context-e podľa GitLab semantics. Nie je to univerzálny secret-isolation mechanizmus.

Stále existujú riziká:

- malicious pipeline code na trusted ref,
- kompromitovaný included template alebo action,
- log, artifact alebo cache leakage,
- príliš široký runner host access,
- downstream pipeline forwarding,
- static credential s veľkým external scope-om.

Protected variable chráni distribution context, nie následné použitie hodnoty. Preferuj short-lived workload identity a external secret manager pred dlhodobým cloud key.

## 15. Environment-scoped variables

Environment scope obmedzuje, pre ktoré environment names je variable dostupná.

```text
production
staging
review/*
```

Treba overiť:

- exact a wildcard matching,
- precedence pri viacerých variables s rovnakým key,
- fallback na broader scope,
- environment name vytvorený jobom,
- child/downstream pipeline behavior,
- protected-status kombináciu.

Effective variable resolution model:

```text
variable key
+ source level
+ protected status
+ environment scope
+ pipeline/ref context
+ precedence
→ effective value alebo absence
```

Nesprávny scope môže odhaliť production credential review app alebo nasadiť produkciu so staging hodnotou.

## 16. Deployment approval

Deployment approval má hodnotu pri vysokorizikovom alebo neautomatizovateľnom rozhodnutí. Approval packet má obsahovať:

- immutable artifact digest,
- configuration/infrastructure revision,
- target environment,
- risk classification,
- test/security/promotion evidence,
- rollout a observation plan,
- rollback/roll-forward eligibility,
- known exceptions,
- maximálny blast radius.

Approval musí mať freshness policy. Zmena digestu, configu, deployment jobu alebo environment state môže rozhodnutie invalidovať.

Manuálne kliknutie bez decision contextu je ceremónia, nie control.

## 17. Deployment record

Deployment job má vytvoriť alebo zachovať záznam:

```text
artifact digest
+ source/release identity
+ environment
+ config revision
+ pipeline/job ID
+ deployer identity
+ timestamps
+ result
+ previous/next deployment relation
+ release exposure
```

Job, ktorý mení produkciu mimo GitLab environment/deployment metadata, oslabuje audit, outdated-deployment prevenciu a incident reconstruction.

## 18. Deployment concurrency

Dva pipeline runs môžu súčasne meniť ten istý environment:

```text
run A deployuje version A
run B deployuje version B
run A dokončí neskôr
→ environment sa vráti na starší desired state
```

Ochrany:

- resource group alebo deployment lock,
- serialized environment mutation,
- cancellation superseded runs,
- optimistic check current deployment generation,
- prevention outdated deployment,
- idempotentný deployment workflow.

Lock musí mať ownera, timeout a recovery pri stuck jobe.

## 19. Outdated deployment prevention

Deployment musí overiť, či jeho subject je stále aktuálny. Starší pipeline run nemá po dlhom čakaní prepísať novší úspešný release.

Model:

```text
candidate generation G
→ acquire environment lock
→ compare with current generation
→ deploy only if still eligible
→ record new generation
```

Retry starého deployment jobu musí rešpektovať aktuálny environment state, nie slepo zopakovať mutation.

## 20. Review apps

Review app je dynamic environment pre branch alebo MR. Je to runtime boundary pre nedôveryhodný alebo ešte neschválený code.

Potrebuje:

- unique a nefalšovateľné environment/resource names,
- izolované namespaces/accounts,
- žiadne production credentials,
- obmedzené network egress a dependencies,
- synthetic alebo anonymizované test data,
- quotas a resource limits,
- TTL, auto-stop a idempotentný teardown,
- ownership a cleanup audit,
- ochranu pred fork pipeline code.

Použitie rovnakého deployment template neznamená, že review app má dostať rovnaké identity ako production.

## 21. Environment tiers

Environment tier klasifikuje runtime význam nezávisle od voľného názvu. Pomáha:

- interpretovať deployment metrics,
- aplikovať governance a reporting,
- rozlíšiť review/testing/staging/production targets,
- analyzovať frequency a change-failure rate.

Tier metadata musí zodpovedať realite. Environment nazvaný `customer-live` označený ako development vytvára reporting a policy blind spot.

## 22. Deployment freeze

Freeze window obmedzuje plánované deploymenty v citlivom čase. Nie je náhradou za:

- protected branch a environment,
- fresh quality gates,
- progressive rollout,
- recovery capability,
- incident change process.

Freeze policy potrebuje timezone, applicability a break-glass model. Dlhé freezes zvyšujú batch size a risk po ich skončení.

## 23. Separation of duties

Možný capability model:

```text
Developer
→ vytvára source zmenu a MR

Reviewer/Code Owner
→ schvaľuje intent a implementation risk

Build identity
→ vytvára immutable artifact

Promotion/deployment identity
→ používa environment-scoped credentials

Environment approver
→ prijíma high-risk exposure rozhodnutie
```

Nie každý tím potrebuje samostatného človeka pre každú fázu. Dôležité je, aby jedna kompromitovaná bežná identita nemohla nekontrolovane meniť source, policy, secrets a production naraz.

## 24. Break-glass lifecycle

Emergency workflow nemá znamenať vypnutie všetkých ochrán.

```text
urgent risk
→ explicitná break-glass identity alebo workflow
→ strong authentication
→ úzky resource a časový scope
→ immutable change/deployment subject
→ audit a alert
→ stabilizácia
→ obnova policy a rotation
→ post-event review
```

Po incidente over:

- či branch/environment ostali protected,
- ktoré refs, variables a deployments sa zmenili,
- či temporary tokens expirovali,
- či chýbajúce reviews/gates boli doplnené,
- aký root cause vyžadoval bypass.

## 25. Policy as Code a drift detection

Branch, tag a environment policy možno auditovať alebo vynucovať cez GitLab API a central governance mechanizmy.

Kontroluj:

- protected branch/tag patterns,
- direct-push, merge a force-push capabilities,
- Code Owner enforcement,
- allowed deployers,
- environment protection,
- variable scopes,
- deployment concurrency controls,
- exception metadata.

Automation má byť idempotentná a musí rozlišovať:

```text
intended policy
| approved exception
| unauthorized drift
```

Automatické „opravenie“ bez evidence môže prepísať legitímnu emergency zmenu skôr, než sa incident stabilizuje.

## 26. Troubleshooting

### Developer môže pushnúť priamo na main

Vyhodnoť všetky matching project/group rules, exact/wildcard patterns, allowed-to-push capability a aktuálny protected status.

### Code Owner approval sa nevyžaduje

Over pattern, target branch protection, eligible ownership membership, enforcement setting a approval-rule interaction.

### Production deploy job je nedostupný

Skontroluj environment name, protected-environment match, allowed deployer eligibility, manual-job actor, ref trust a current deployment approval.

### Protected variable chýba

Over protected ref context, environment scope, precedence, fork/downstream pipeline context a to, či job vznikol v trusted project context-e.

### Review app dostala production credential

Okamžite rotuj credential, zastav environment, audituj logs/artifacts/cache, oprav variable scope a deployment template trust model.

### Starší pipeline prepísal novší deployment

Chýba environment serialization alebo outdated-deployment check. Zastav súbežné jobs, obnov intended version a zaveď generation/lock control.

### Break-glass skončil, ale protection je vypnutá

Ide o configuration drift a otvorenú security boundary. Obnov policy, revokuj temporary access a vykonaj post-event audit refs a deployments.

## 27. Typické anti-patterny

### Protected main, ale production môže deployovať každý Developer

Source boundary je chránená, runtime boundary nie.

### Allowed to push a allowed to merge sa považujú za to isté

Direct push obchádza MR a approval lifecycle.

### Maintainer môže unprotect, push a re-protect bez auditovateľného procesu

Jedna identita môže ticho obísť policy.

### Chránený branch, ale nechránený release tag

Útočník alebo chyba môže spustiť release iného subjectu.

### Production secrets na každom protected ref-e

Kompromitovaný release/support branch získava neprimeraný external access.

### Protection iba podľa environment mena bez naming policy

Job vytvorí podobný neprotected environment a obíde control.

### Review app zdedí produkčné identity

Untrusted code dostane produkčný blast radius.

### Deployment bez serialization

Staršie a novšie runs prepisujú environment v nepredvídateľnom poradí.

### Emergency znamená globálne vypnutie ochrán

Zvyšuje incident blast radius a ruší rekonštruovateľnosť.

## 28. Praktický rozhodovací rámec

1. Ktoré branches a tags sú trusted source/release boundaries?
2. Kto smie pushovať, mergeovať, force-pushovať a meniť protection?
3. Ako sa riešia overlapping rules?
4. Ktoré automation identities potrebujú direct ref mutation?
5. Ako Code Owner enforcement nadväzuje na MR policy?
6. Aké tag patterns spúšťajú release alebo publication?
7. Aké kanonické environment names a tiers existujú?
8. Kto smie deployovať do každého environmentu?
9. Aký trusted deployment entrypoint používa artifact digest?
10. Ako sa riešia protected a environment-scoped variables?
11. Ako sa deployment approvals invalidujú pri zmene subjectu?
12. Ako sa serializuje environment mutation a blokuje outdated deployment?
13. Ako sú review apps izolované a čistené?
14. Aký break-glass proces obnoví policy a credentials?
15. Ako sa deteguje drift group/project policy?

## 29. Kontrolný checklist

- critical branches a release tags majú explicitné rules;
- direct push je zakázaný alebo úzko odôvodnený;
- force push a unprotect sú silne obmedzené;
- overlapping rules boli testované;
- Code Owner enforcement je overené reprezentatívnymi paths;
- production environment má kanonické meno a tier;
- allowed deployers sú oddelení od bežného pipeline triggeru;
- deployment job používa immutable artifact a trusted definition;
- static production secrets sú minimalizované;
- protected/environment-scoped variables majú testovanú precedence;
- deployment approval patrí digestu, configu a environmentu;
- environment mutations sú serializované;
- outdated deployment nemôže prepísať novší state;
- review apps nemajú production trust a majú TTL cleanup;
- break-glass obnovuje protections a revokuje temporary access;
- policy drift je auditovaný a vysvetliteľný.

## 30. Kontrolné otázky

1. Prečo sú protected branch a protected environment dve rozdielne boundaries?
2. Ako sa určuje effective policy pri viacerých branch rules?
3. Aký je rozdiel medzi allowed to push a allowed to merge?
4. Prečo je unprotect vyššia capability než push?
5. Prečo treba chrániť aj release tags?
6. Kedy Code Owner approval skutočne blokuje merge?
7. Čo tvorí deployment subject?
8. Ako možno environment-name spoofingom obísť policy?
9. Čo protected variable chráni a čo nechráni?
10. Ako sa počíta effective environment-scoped variable?
11. Čo má obsahovať deployment approval packet?
12. Aký race rieši environment lock a outdated-deployment prevention?
13. Prečo review app potrebuje samostatnú trust boundary?
14. Ako má vyzerať break-glass restoration?
15. Čo musí Policy as Code rozlíšiť od unauthorized driftu?

## Summary

Protected branches a tags chránia dôveryhodné Git refs; protected environments chránia runtime deployment boundary. Bezpečný GitLab model oddeľuje push, merge, force-push, unprotect a deploy capabilities, testuje effective rule resolution a viaže production deployment na immutable artifact, trusted job definition a environment-scoped identity. Protected variables nie sú úplná secret boundary a environment názov nie je bezpečný bez naming policy. Deploymenty musia byť serializované, chránené pred outdated runs a auditované. Break-glass musí po stabilizácii obnoviť policy, revokovať temporary access a uzavrieť evidence.

## Glossary impact

Relevantné pojmy: protected branch, branch rule, protected tag, allowed to push, allowed to merge, force push, unprotect permission, protected environment, environment identity, allowed to deploy, protected variable, environment-scoped variable, deployment approval, deployment lock, outdated deployment, review app, environment tier, deployment freeze a break-glass restoration.

## Oficiálna dokumentácia

- [Protected branches](https://docs.gitlab.com/user/project/repository/branches/protected/)
- [Protected environments](https://docs.gitlab.com/ci/environments/protected_environments/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Merge requests a approvals](merge-requests-and-approvals.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: GitLab CI/CD syntax →](gitlab-ci-cd-syntax.md)
<!-- KNOWLEDGE-NAVIGATION:END -->