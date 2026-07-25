# Merge requests a approvals

Merge request (MR) je GitLab decision object, ktorý spája source zmenu, review, automatizované evidence, approval policy a integráciu do target branch. Nie je to iba webový obal nad `git merge`. Je to auditovateľný lifecycle rozhodnutia:

```text
change intent
→ source commits a diff
→ review a discussions
→ pipeline evidence
→ approvals a policy
→ merge-result validation
→ integration
→ artifact a deployment traceability
```

Approval je iba jeden signál. Zelené approval count samo osebe neznamená, že zmena je aktuálna, správne otestovaná alebo mergeovateľná.

Konkrétne approval features, enforcement a eligibility sa môžu meniť podľa GitLab verzie, offeringu, tieru a project/group policy. Pri produkčnom návrhu over reálne nastavenie inštancie.

## 1. Mental model: subject, evidence a decision

Každé merge rozhodnutie má tri hlavné časti:

- **Subject —** presný source commit, target branch stav, diff a prípadný synthetic merge result.
- **Evidence —** review, discussions, CI výsledky, security reports, ownership a compatibility dôkazy.
- **Decision policy —** approval rules, branch rules, pipeline požiadavky, unresolved-thread policy a merge strategy.

```text
subject identity
+ complete and fresh evidence
+ applicable policy
→ mergeability verdict
```

Ak sa zmení source SHA, target branch, pipeline definition, approval rule alebo security evidence, časť predchádzajúceho rozhodnutia môže prestať platiť.

## 2. Merge request identity

MR obsahuje alebo odkazuje na:

- source project a source branch,
- target project a target branch,
- autora a ďalších účastníkov,
- source commit set,
- current diff,
- base alebo merge-base context,
- pipeline contexts,
- approvals a discussions,
- merge strategy a výsledný commit,
- súvisiace issues, milestones alebo change records.

MR number nie je úplná identity reviewovaného obsahu. Jeden MR môže počas lifecycle obsahovať viac source SHA a viac diff verzií.

Pre audit zachovaj:

```text
MR ID
+ reviewed source SHA
+ target SHA alebo merge-base
+ pipeline subject SHA
+ approval timestamps a identities
+ final merge/result SHA
```

## 3. Source diff verzus merge result

Source branch pipeline testuje branch v jej vlastnom stave. Nemusí odhaliť konflikt alebo behaviorálnu interakciu s aktuálnym target branchom.

Rozlišuj:

- **Source diff —** zmeny source branch voči target/base contextu.
- **Source branch SHA —** posledný commit branchu.
- **Synthetic alebo merged-result SHA —** výsledok predpokladanej integrácie source a aktuálneho targetu.
- **Final merge commit/result —** commit, ktorý sa reálne dostal do target branch po zvolenej merge stratégii.

Dôveryhodný integration gate má testovať stav čo najbližší reálnemu merge výsledku. Ak sa target branch zmení, starý merged-result evidence môže byť zastaraný.

## 4. MR lifecycle

Typický lifecycle:

```text
branch a change intent
→ otvorenie draft MR
→ priebežný review a CI
→ ready-for-review
→ required reviewers/owners
→ approvals a resolved discussions
→ fresh merge-result evidence
→ merge queue/train alebo merge
→ post-merge pipeline
→ artifact/deployment traceability
```

Každý transition má mať jasný význam. Označenie `Ready` nesmie automaticky znamenať, že všetka evidence je kompletná.

## 5. Draft stav

Draft MR je workflow signal pre skorú spoluprácu. Umožňuje:

- architektonickú diskusiu pred dokončením,
- zviditeľnenie rozpracovanej zmeny,
- skoré CI a static-analysis výsledky,
- koordináciu dependencies,
- priebežnú kontrolu scope-u.

Draft nie je security boundary. Protected branch, secrets policy, runner trust a approval rules musia platiť nezávisle od draft labelu.

Draft má byť aktualizovaný, keď sa mení intent alebo scope. Dlhodobo otvorený draft s nejasným cieľom zvyšuje review debt a conflict risk.

## 6. Review verzus approval

Review je proces získania znalosti o zmene. Zahŕňa čítanie diffu, diskusiu, reprodukciu, testovanie, threat reasoning a hodnotenie prevádzkového dopadu.

Approval je zaznamenané rozhodnutie identity, ktorú policy považuje za eligible.

```text
review môže existovať bez approval
approval môže byť neplatný bez eligibility
approval count môže byť zelený pri slabom review
```

Approval preto nie je metrika kvality review. Je evidence, že konkrétny approver prevzal definovanú rozhodovaciu zodpovednosť nad konkrétnym subjectom.

## 7. Approval rule contract

Approval rule má definovať:

- názov a chránené riziko,
- applicable target branches alebo project scope,
- eligible users, groups alebo ownership sources,
- počet požadovaných approvals,
- self-approval a committer restrictions,
- reset alebo invalidation správanie,
- vzťah ku Code Owners alebo security policy,
- bypass a exception model,
- unavailable-approver fallback.

Príklad viacrozmerného modelu:

```text
Service ownership
→ 1 approval od service owners

Database migration paths
→ 1 approval od database owners

Production deployment definitions
→ 1 approval od operations/platform

Critical security finding
→ explicitné security risk decision
```

Jedna univerzálna approval rule pre každý diff vytvára buď príliš slabý control, alebo delivery bottleneck.

## 8. Applicable rule a changed paths

Rule sa môže aplikovať podľa target branchu, changed paths, policy scope-u alebo security výsledku. Applicability musí byť vysvetliteľná.

Pri path-based pravidlách over:

- glob patterns a precedence,
- renamed a deleted files,
- generated manifests,
- symlinks alebo submodules podľa workflowu,
- files mimo očakávaného adresára, ktoré ovplyvnia rovnaký runtime,
- rozdiel medzi source path a rendered/deployed resource.

Path matching nie je kompletný dependency graph. Zmena shared library môže ovplyvniť service bez priameho zásahu do jej adresára.

## 9. Eligible approver resolution

Používateľ môže byť uvedený v approver group, ale jeho approval nemusí byť platný v každom kontexte. Eligibility môže závisieť od:

- direct alebo inherited membershipu,
- effective role,
- explicitného user/group assignmentu,
- Code Owner matchu,
- target branchu,
- project/group approval policy,
- security-policy contextu,
- self-approval alebo committer restriction,
- availability konkrétnej feature/tieru.

Pri diagnostike zachyť:

```text
approval identity
→ membership path
→ applicable rule
→ eligibility at approval time
→ subject SHA
```

Group name sama osebe nie je dôkaz eligibility.

## 10. Independence a separation of duties

Silnejší model môže vyžadovať, aby:

- autor nebol jediným approverom,
- používateľ, ktorý pridal commit, nebol jediným nezávislým reviewerom,
- security risk neprijal autor zmeny,
- production policy zmenu schválil iný capability owner,
- approval-rule administrátor nemohol jednostranne schváliť vlastnú zmenu.

Separation of duties má zodpovedať riziku. Pri malom tíme môže univerzálny dvojitý approval zastaviť delivery. Vtedy použite risk-based rules, rotating on-call approverov alebo explicitný break-glass proces namiesto tichého bypassu.

## 11. Approval freshness graph

Approval patrí konkrétnemu obsahu a contextu. Môže sa invalidovať, keď sa zmení:

- source commit alebo diff,
- conflict resolution,
- rebase result,
- target branch a merged-result SHA,
- relevantná pipeline definition,
- approval policy alebo Code Owners,
- security finding alebo dependency lock,
- deployment/configuration subject zahrnutý v MR.

```text
approval
→ reviewed source SHA
→ target context
→ applicable policy version
→ supporting evidence
```

Nový commit nemusí meniť reviewovanú oblasť, ale systém musí mať jasnú reset policy. Manual judgement „toto bola iba typo“ má byť auditovateľný, nie implicitný.

## 12. Pipeline freshness

MR môže mať viac pipeline typov:

- branch pipeline,
- merge-request pipeline,
- merged-results pipeline,
- merge-train pipeline,
- child alebo multi-project pipelines.

Required pipeline evidence musí odpovedať:

- ktorý SHA bol testovaný,
- aký target context sa použil,
- ktoré jobs boli required,
- či všetky shards a child pipelines dokončili,
- či pipeline použila aktuálnu configuration/policy,
- či výsledok patrí stále aktuálnemu diffu.

Zelená pipeline na starom source SHA nie je dôkaz aktuálneho MR.

## 13. Pipeline verdict taxonomy

Merge policy nemá rozlišovať iba green/red. Relevantné stavy:

- **Passed —** required checks sa kompletne vykonali nad správnym subjectom.
- **Failed —** check našiel porušenie alebo test failure.
- **Running/pending —** evidence ešte nie je dostupná.
- **Canceled/superseded —** run bol zastavený novšou zmenou alebo policy.
- **Skipped/not applicable —** job sa podľa rules nevytvoril; treba overiť správnosť applicability.
- **Infrastructure/tool error —** kontrola neprebehla dôveryhodne.
- **Incomplete —** chýba shard, report alebo downstream výsledok.

Tool error alebo missing job nesmie byť automaticky interpretovaný ako dôkaz kvality.

## 14. Discussions a unresolved threads

Discussion je evidence o identifikovanom probléme alebo otázke. Resolved status má znamenať, že outcome je známy.

Riziká:

- autor uzavrie thread bez opravy alebo dohody,
- komentár je viazaný na outdated line,
- diff sa zmení bez upozornenia pôvodného reviewera,
- dôležitý risk sa presunie do neformálneho chatu,
- thread sa uzavrie textom „neskôr“ bez issue a ownera.

Pre významnú pripomienku zachovaj jeden z outcome-ov:

```text
fixed in commit X
| accepted as designed with rationale
| deferred to issue Y with risk owner
| rejected with reviewer agreement
```

Resolved-discussion policy je užitočná iba vtedy, keď resolution semantics tím reálne dodržiava.

## 15. Code Owners

CODEOWNERS mapuje paths na ownership subjects. Je užitočný pre:

- security-sensitive source,
- deployment a infrastructure manifests,
- database migrations,
- shared CI templates,
- public API schemas,
- compliance alebo policy files.

Code Owner mechanizmus potrebuje:

- presné a testované patterns,
- dostupných owners a fallback,
- alignment s reálnym ownershipom,
- protected-target enforcement, ak má byť blocking,
- review po reorganizácii alebo transferoch,
- kontrolu, kto smie meniť samotný CODEOWNERS súbor.

CODEOWNERS nie je dependency graph ani záruka expertnej kvality. Priradený owner môže byť neaktuálny alebo nemusí rozumieť runtime dopadu indirect zmeny.

## 16. Mergeability verdict

MR je mergeovateľný až keď všetky relevantné vrstvy sú splnené:

```text
not draft
+ no unresolved merge conflict
+ fresh required pipeline evidence
+ applicable approvals satisfied
+ required discussions resolved
+ target branch policy permits merge
+ merge-result/queue state valid
→ mergeable
```

Možné blokátory:

- chýbajúci alebo neplatný approval,
- pipeline failure alebo incomplete evidence,
- source branch za targetom podľa policy,
- konflikt,
- unresolved thread,
- Code Owner rule,
- security approval policy,
- merge train alebo deployment freeze context,
- branch rule, ktorá nepovoľuje danému actorovi merge.

`Approved` a `mergeable` nie sú synonymá.

## 17. Merge strategy

Merge strategy určuje výslednú commit topology a ovplyvňuje traceability, rollback a CI behavior.

### Merge commit

Zachová source commits a vytvorí explicitný integration commit. Uľahčuje rozlíšenie branch boundaries, ale mainline môže byť komplexnejšia.

### Fast-forward alebo semi-linear model

Udržiava lineárnejšiu históriu, ale môže vyžadovať rebase a nové validation evidence.

### Squash merge

Vytvorí jeden výsledný commit. Zjednodušuje mainline a revert jednej logickej zmeny, no mení commit identity a môže stratiť granularitu.

### Rebase pred merge

Presunie commits na aktuálny target context. Mení SHA a môže invalidovať approvals alebo pipelines podľa policy.

Stratégiu vyber podľa:

- desired mainline topology,
- potreby signed commit traceability,
- backport a cherry-pick workflowu,
- release-note automation,
- revert semantics,
- merge queue a CI modelu.

## 18. Squash traceability

Pri squash merge zachovaj väzbu:

```text
source commits
→ MR a review history
→ squash result SHA
→ artifact provenance
→ deployment record
```

Squash message má identifikovať logickú zmenu a podľa potreby issue/MR. Nespoliehaj sa iba na source commit SHA, ktoré sa do mainline nedostali.

## 19. Merge when pipeline succeeds

Automatický merge po splnení gates znižuje manuálne čakanie. Bezpečný model potrebuje:

- fresh pipeline nad správnym subjectom,
- aktuálny target context,
- nezastaralé approvals,
- cancellation pri novom pushi,
- conflict handling,
- protected branch enforcement,
- audit actor/policy rozhodnutia.

Pri vysokej concurrency môže viac samostatne zelených MR navzájom poškodiť mainline. Vtedy treba merge queue alebo train.

## 20. Merge train

Merge train modeluje predpokladané poradie viacerých MR:

```text
main + MR-A
→ candidate A

main + MR-A + MR-B
→ candidate B
```

Keď skorší candidate zlyhá alebo sa zmení, downstream candidates sa musia prepočítať. Sleduj:

- candidate/result SHA,
- queue ordering,
- invalidáciu pri target zmene,
- failure attribution,
- pipeline duplication a capacity,
- cancellation a retry,
- approval freshness,
- final artifact identity.

Merge train rieši integration race, nie review kvalitu ani compatibility s produkčným state.

## 21. Security approval evidence

Approval založený na security výsledku potrebuje dôveryhodný chain:

```text
current MR subject
→ analyzer sa úspešne vykonal
→ report je úplný a autentický
→ finding je správne klasifikovaný ako new/existing
→ policy vyhodnotila applicability
→ eligible security approver rozhodol
```

Kontroluj:

- analyzer coverage a supported paths,
- tool/infrastructure failure,
- report provenance,
- target/base comparison,
- severity spolu s reachability a asset contextom,
- duplication alebo suppression,
- exception scope a expiration.

Scanner severity bez kontextu môže vytvárať noise; chýbajúci scanner nesmie vytvárať falošný green state.

## 22. Approval exception a bypass

Legitímna exception obsahuje:

- konkrétny MR, finding alebo rule scope,
- dôvod a risk ownera,
- nezávislého approvera podľa policy,
- compensating controls,
- expiration alebo jednorazový charakter,
- follow-up issue,
- audit actorov a timestamps.

Break-glass lifecycle:

```text
urgent need
→ explicitný privileged action
→ minimálne safety checks
→ merge/deployment evidence
→ následný review
→ doplnenie preskočených controls
→ oprava root cause bypassu
```

Rutinný Maintainer bypass znamená, že branch alebo approval policy neplní svoj účel.

## 23. Review quality model

Reviewer nemá iba hľadať syntax chyby. Podľa scope-u posudzuje:

- intent a requirement traceability,
- correctness a failure modes,
- security, authorization a data handling,
- API, event a database compatibility,
- performance a resource impact,
- observability a operability,
- migration, rollout a recovery,
- test evidence a gaps,
- documentation a unnecessary complexity.

Review depth má zodpovedať risku. Veľká zmena bez vysvetlenia zvyšuje kognitívnu záťaž a pravdepodobnosť povrchného approval.

## 24. Small merge requests a safe intermediate states

Menšie MR zvyčajne znižujú review latency, conflict risk a rollback scope. Nemajú však vytvárať nebezpečný medzistav.

Správne rozdelenie databázovej zmeny:

```text
MR 1: backward-compatible schema expand
MR 2: tolerant readers/writers
MR 3: backfill a switch
MR 4: contract po rollback window
```

Nesprávne rozdelenie môže dočasne nasadiť code, ktorý očakáva ešte neexistujúcu schema alebo odstráni compatibility path príliš skoro.

## 25. Post-merge evidence chain

MR lifecycle nekončí kliknutím na merge. Zachovaj traceability:

```text
issue/requirement
→ MR ID
→ reviewed source SHA
→ approvals a discussions
→ pipeline/merge-result evidence
→ final target SHA
→ artifact digest
→ deployment/release record
→ runtime validation
```

Ak squash, rebase alebo merge train zmení commit identity, release provenance musí stále vedieť ukázať späť na MR a reviewovaný obsah.

## 26. MR observability a governance metrics

Sleduj najmä:

- time to first review,
- total review/merge lead time,
- approval wait podľa rule,
- stale approval resets,
- unresolved-discussion age,
- merge-train queue a failure rate,
- bypass/exception frequency,
- reopened alebo post-merge defects,
- average diff size iba ako kontext,
- unavailable-owner bottlenecks,
- defect escapes napriek splneným rules.

Cieľom nie je maximalizovať approval count ani minimalizovať review čas za každú cenu. Cieľom je rýchle a dôveryhodné integračné rozhodnutie.

## 27. Troubleshooting

### MR má approvals, ale nemožno ho mergeovať

Skontroluj fresh required pipelines, conflicts, unresolved discussions, target branch rules, Code Owners, approval-rule applicability a merge-train state.

### Approval zmizol po pushi alebo rebase

Project alebo policy invalidovala approval pri zmene subject SHA. Over reset settings a či reviewer musí potvrdiť nový diff.

### Používateľ je v approver group, ale approval sa nepočíta

Over eligibility v konkrétnej rule, membership path, effective role, target branch, self/committer restrictions a dostupnosť feature.

### MR pipeline nevidí protected variables

Source/ref alebo fork context nie je trusted. Neobchádzaj trust boundary; oddeľ untrusted verification od privileged deployment workflowu.

### Code Owner approval sa nevyžaduje

Over pattern match, target branch protection, rule enforcement, ownership súbor a to, či changed path naozaj patrí do patternu.

### Merge train opakovane reštartuje pipeline

Target branch alebo skorší candidate sa mení. Sleduj invalidation reason, queue ordering, flaky jobs a pipeline capacity.

### Zelený MR po merge rozbil main

Source pipeline pravdepodobne netestovala aktuálny merge result alebo súbežné MRs vytvorili integration race. Použi merged-results pipelines a merge train/queue.

## 28. Typické anti-patterny

### Approval od autora ako jediný control

Neposkytuje nezávislé rozhodnutie ani separation of duties.

### Approval count bez definovaného rizika

Viac kliknutí nemusí zvýšiť kvalitu a môže vytvoriť mechanický bottleneck.

### Approval zostáva po zásadnej zmene

Reviewer rozhodol nad iným subjectom; evidence je stale.

### Review iba podľa zelenej pipeline

Automatické testy neoverujú celý intent, design, security ani operability.

### Required Code Owners bez dostupného fallbacku

Ownership model vytvorí permanentný delivery outage pri absencii ľudí.

### Maintainer bypass ako bežný postup

Platformová policy sa stane dekoráciou a audit prestane reprezentovať skutočný decision flow.

### Branch pipeline považovaná za merge-result dôkaz

Nekontroluje interakciu s aktuálnym target branchom.

### Resolved thread bez outcome

Risk zmizne z UI, ale nie zo systému.

## 29. Praktický rozhodovací rámec

Pre MR workflow odpovedz:

1. Aký presný subject sa reviewuje a testuje?
2. Ktoré zmeny invalidujú approvals a pipeline evidence?
3. Aké risks chránia jednotlivé approval rules?
4. Ako sa rieši approver eligibility a neprítomnosť?
5. Ktoré paths vyžadujú Code Owners a prečo?
6. Je merged-result evidence potrebná?
7. Aké pipeline stavy blokujú merge?
8. Kto smie resolve-nuť kritické discussions?
9. Akú merge strategy vyžaduje traceability a release model?
10. Potrebuje project merge train/queue?
11. Ako sa riešia security findings a scanner failure?
12. Ako funguje exception a break-glass lifecycle?
13. Ako sa final SHA mapuje na artifact a deployment?
14. Ktoré metriky odhaľujú slabý alebo pomalý review systém?

## 30. Kontrolný checklist

- MR intent a scope sú explicitné;
- current source SHA a target context sú známe;
- required evidence patrí aktuálnemu subjectu;
- approvals majú definovanú freshness policy;
- rules majú risk, scope a eligible approvers;
- author/committer restrictions zodpovedajú governance modelu;
- Code Owners patterns sú testované a owners dostupní;
- required discussions majú explicitný outcome;
- tool failure alebo incomplete pipeline nie sú pass;
- merge strategy zachováva potrebnú traceability;
- high-concurrency project používa merge queue/train podľa potreby;
- security report má coverage a provenance;
- exceptions majú scope, ownera, compensating controls a follow-up;
- final merge SHA sa mapuje na artifact a release record.

## 31. Kontrolné otázky

1. Prečo MR nie je iba webová forma `git merge`?
2. Aký je rozdiel medzi source SHA, merged-result SHA a final merge SHA?
3. Aký je rozdiel medzi review a approval?
4. Čo tvorí approval rule contract?
5. Ako sa určuje eligible approver?
6. Prečo approval potrebuje freshness graph?
7. Aké pipeline contexts môžu existovať pri MR?
8. Prečo branch pipeline nemusí byť dostatočný integration dôkaz?
9. Kedy je discussion skutočne resolved?
10. Čo Code Owners zabezpečujú a čo nezabezpečujú?
11. Čo môže blokovať merge aj po approvals?
12. Ako merge strategy ovplyvňuje commit identity a traceability?
13. Aký race rieši merge train?
14. Čo potrebuje security approval založený na scanner reporte?
15. Čo má obsahovať approval exception?

## Summary

GitLab merge request je evidence-driven integration decision nad konkrétnym source a target contextom. Dôveryhodný workflow oddeľuje review od approval, viaže approvals a pipelines na presný subject, vysvetľuje eligibility, vynucuje ownership a discussion outcomes a testuje reálny merge result. Merge strategy, merge train, security policy a exceptions musia zachovať traceability až po final SHA, artifact digest a deployment. Zelený approval count alebo source-branch pipeline samy osebe nedokazujú bezpečnú integráciu.

## Glossary impact

Relevantné pojmy: GitLab merge request, MR subject, source SHA, merged-result SHA, approval rule, eligible approver, stale approval, Code Owner, unresolved discussion, mergeability verdict, merge strategy, squash merge, merge train, security approval policy, approval exception a post-merge traceability.

## Oficiálna dokumentácia

- [Merge request approvals](https://docs.gitlab.com/user/project/merge_requests/approvals/)
- [Merge request approval rules](https://docs.gitlab.com/user/project/merge_requests/approvals/rules/)
- [Merge request approval settings](https://docs.gitlab.com/user/project/merge_requests/approvals/settings/)
- [Merge request approval policies](https://docs.gitlab.com/user/application_security/policies/merge_request_approval_policies/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Projects, groups a permissions](projects-groups-permissions.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Protected branches a environments →](protected-branches-and-environments.md)
<!-- KNOWLEDGE-NAVIGATION:END -->