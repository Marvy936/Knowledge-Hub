# Merge requests a approvals

Merge request (MR) je GitLab objekt, v ktorom tím rozhoduje, či sa konkrétna zmena môže stať súčasťou target branchu. Spája source commits, diff, review, diskusie, CI evidence, ownership pravidlá, approvals a výslednú merge stratégiu.

Nie je to iba webová forma príkazu `git merge`. Príkaz dokáže spojiť históriu; MR má dokázať, prečo bolo spojenie povolené.

```text
change intent
→ source commits a diff
→ review a diskusie
→ automatizované evidence
→ approval a branch policy
→ merge-result validation
→ final merge SHA
→ artifact a deployment traceability
```

Konkrétne GitLab features sa môžu meniť podľa verzie, offeringu a tieru. Stabilný princíp je, že každé merge rozhodnutie musí byť viazané na presný obsah, aktuálne evidence a aplikovateľnú policy.

## 1. Priebežný scenár: jedna zmena od branchu po produkciu

Vývojárka Jana mení payment API. Vytvorí branch `feature/idempotency`, upraví aplikačný kód, databázovú migráciu a CI test. Potom otvorí MR do `main`.

Pri prvom otvorení je MR draft. Branch pipeline prejde, pretože testuje Janin branch. Počas review však target branch dostane inú zmenu, ktorá upravila rovnaký request model. Janina pôvodná zelená pipeline už nehovorí, či obe zmeny fungujú spolu.

GitLab preto vytvorí merged-result candidate: syntetický výsledok spojenia aktuálneho `main` a Janinho source SHA. Nad týmto kandidátom sa zopakujú required testy. Databázový súbor aktivuje Code Owner approval od database tímu a zmena CI konfigurácie approval od platform tímu.

Jana následne pridá commit opravujúci pripomienku. Tým sa zmení source SHA a predchádzajúce approval alebo pipeline evidence môžu prestať platiť. Po novom review sa MR zaradí do merge trainu. Ten ho testuje v poradí spolu s ďalšími čakajúcimi MR.

Po merge vznikne final target SHA, z ktorého sa vytvorí artifact digest. Deployment record musí vedieť ukázať späť na MR, reviewovaný source SHA a pipeline candidate.

Tento scenár obsahuje celý problémový priestor kapitoly: identitu zmeny, freshness evidence, vlastníctvo, integration race, commit topology a post-merge traceability.

## 2. Mental model: subject, evidence a decision policy

Každé merge rozhodnutie má tri vrstvy.

**Subject** je presný obsah a kontext, o ktorom sa rozhoduje. Zahŕňa source SHA, target branch stav, diff a podľa pipeline modelu aj synthetic merge-result SHA.

**Evidence** sú informácie, ktoré hovoria, či je zmena prijateľná. Patria sem ľudský review, resolved discussions, testy, security reports, compatibility checks a ownership potvrdenia.

**Decision policy** určuje, ktoré evidence sú povinné a kto smie rozhodnúť. Zahŕňa approval rules, protected-branch nastavenia, Code Owners, pipeline požiadavky, discussion policy a merge strategy.

```text
presný subject
+ úplné a čerstvé evidence
+ aplikovateľná policy
→ mergeability verdict
```

Ak sa zmení subject, evidence alebo policy, staré rozhodnutie nemusí zostať platné. To je dôvod, prečo sa approvals resetujú a pipelines opakujú.

## 3. MR číslo nie je identity reviewovaného obsahu

MR `!142` môže počas svojho života obsahovať desať rôznych source SHA. Reviewer mohol schváliť tretiu verziu diffu, zatiaľ čo merge prebieha nad desiatou.

Pre audit preto nestačí uchovať iba MR ID. Potrebná je väzba:

```text
MR ID
+ reviewed source SHA
+ target alebo merge-base context
+ pipeline candidate SHA
+ approval identities a timestamps
+ final merge/result SHA
```

Source branch name je tiež iba pohyblivý pointer. Po novom pushi ukazuje na iný commit. Dôveryhodné evidence sa viažu na immutable SHA alebo na jednoznačne identifikovaný candidate.

## 4. Source diff, source SHA a merge result

Tieto pojmy opisujú odlišné objekty.

**Source SHA** je posledný commit source branchu. Branch pipeline typicky testuje stav repository na tomto commite.

**Diff** je množina zmien medzi source a zvoleným base/target contextom. Keď sa target branch posunie, rovnaký source SHA môže mať iný diff.

**Merged-result SHA** je syntetický commit alebo candidate reprezentujúci predpokladaný výsledok spojenia source a aktuálneho targetu.

**Final merge SHA** je commit, ktorý sa po merge stratégii reálne dostane do target branchu. Pri squash alebo rebase modeli nemusí byť totožný so žiadnym pôvodným source commitom.

```text
source branch SHA
       +
aktuálny target SHA
       ↓
merged-result candidate
       ↓
final merge strategy
       ↓
final target SHA
```

Branch pipeline môže byť zelená a merged-result pipeline červená. Nie je to rozpor; testujú odlišný subject.

## 5. MR lifecycle a význam stavov

Typický lifecycle vyzerá takto:

```text
change intent
→ draft MR
→ skorý review a CI
→ ready for review
→ required owners a approvals
→ fresh merge-result evidence
→ merge queue alebo merge train
→ final merge
→ post-merge build a deployment traceability
```

Každý stav má vyjadrovať skutočný decision progress. `Ready` znamená, že autor považuje zmenu za pripravenú na formálny review. Neznamená automaticky, že pipeline je kompletná alebo že všetky approvals existujú.

Draft je collaboration signal, nie security boundary. Aj draft pipeline musí rešpektovať pravidlá pre secrets, runner trust a fork context.

## 6. Review a approval nie sú to isté

Review je poznávací proces. Reviewer číta diff, kontroluje intent, premýšľa nad failure modes, testuje správanie a diskutuje trade-offs.

Approval je zaznamenané rozhodnutie eligible identity. Hovorí, že konkrétny človek alebo rola prevzali zodpovednosť za definovaný typ rizika nad konkrétnym subjectom.

```text
review bez approval
→ užitočná diskusia, ale policy nemusí byť splnená

approval bez kvalitného review
→ formálne kliknutie bez silného dôkazu
```

Počet approvals preto nie je metrika kvality. Dve mechanické approvals môžu byť slabšie než jeden hlboký review od relevantného ownera.

## 7. Čo má chrániť approval rule

Approval rule nemá existovať iba preto, že „dve approvals sú best practice“. Má chrániť konkrétne riziko.

Príklad:

```text
zmena aplikačnej logiky
→ service-owner review

databázová migrácia
→ database-owner review

zmena production deployment definície
→ platform/operations review

nový kritický security risk
→ explicitné security rozhodnutie
```

Rule preto potrebuje názov, scope, eligible approvers, počet approvals, self-approval obmedzenia, invalidation správanie a exception model. Ak rule nemá definovaný risk, tím nevie, čo má approver vlastne overovať.

Jedna univerzálna rule pre každý diff býva buď príliš slabá, alebo vytvorí zbytočnú review queue.

## 8. Applicability podľa paths a kontextu

Code Owner alebo approval rule sa často aktivuje podľa changed paths. Path match však nie je dependency graph.

Zmena v `shared/auth/` môže ovplyvniť payment service bez toho, aby sa dotkla adresára `payments/`. Generated manifest môže vzniknúť z template mimo deployment directory. Rename alebo delete môže mať iné matching správanie než bežná editácia.

Path-based policy preto potrebuje testované patterns a lokálne vysvetlenie toho, aké riziko pattern reprezentuje. Pri kritických oblastiach zváž aj rendered output, dependency mapu alebo širšiu ownership hranicu.

## 9. Eligible approver

Byť členom group s názvom `database-owners` ešte nemusí znamenať, že approval sa započíta. Eligibility môže závisieť od membership pathu, effective role, target branchu, self-approval restrictions, Code Owner matchu alebo aktuálnej policy.

Pri diagnostike approval rozhodnutia sleduj:

```text
approver identity
→ membership/access path
→ applicable rule
→ eligibility v čase approval
→ subject SHA
```

Ak sa členstvo alebo policy neskôr zmení, audit má stále vedieť vysvetliť, prečo bol approval v danom okamihu platný.

## 10. Separation of duties

Nezávislý review znižuje riziko, že autor prehliadne vlastný predpoklad. Neznamená to, že každý MR potrebuje veľký approval board.

Risk-based model môže vyžadovať, aby autor nebol jediným approverom, security risk neprijal jeho pôvodca a zmenu produkčnej policy schválil iný capability owner.

Malý tím môže mať iba dvoch alebo troch ľudí. V takom prípade rigidná požiadavka na viac nezávislých špecialistov vytvorí permanentný bottleneck. Riešením je jasne obmedzený break-glass, rotačný owner alebo dodatočný review pri vysokorizikových zmenách, nie tichý Maintainer bypass.

## 11. Prečo approvals starnú

Approval je rozhodnutie nad obsahom a kontextom. Keď sa zmení source SHA, reviewer už nemusí poznať aktuálny diff. Keď sa zmení target branch, môže vzniknúť nová integration interakcia.

Freshness graph môže zahŕňať:

```text
approval
→ reviewed source SHA
→ target context
→ Code Owner a approval policy version
→ supporting pipeline/security evidence
```

Nie každá malá zmena musí vyžadovať kompletný review od nuly. Systém však potrebuje explicitnú reset policy. Rozhodnutie „bol to iba preklep“ má byť viditeľné a auditovateľné.

## 12. Pipeline contexts pri MR

Jeden MR môže mať viac druhov pipelines.

**Branch pipeline** testuje source branch. Je rýchly feedback pre autora, ale nemusí reprezentovať integráciu s targetom.

**Merge-request pipeline** používa MR context a môže mať iné rules alebo variables než obyčajný branch run.

**Merged-results pipeline** testuje synthetic integration candidate. Je silnejším dôkazom, že source a aktuálny target spolu fungujú.

**Merge-train pipeline** testuje candidate v poradí s ďalšími čakajúcimi MR. Rieši race medzi zmenami, ktoré boli samostatne zelené.

Child alebo multi-project pipelines môžu poskytovať ďalšie evidence. Required gate musí vedieť, či dokončili všetky potrebné downstream runs a shards.

## 13. Zelená pipeline musí patriť správnemu subjectu

Zelený badge nestačí. Merge policy musí vedieť:

- ktorý SHA bol testovaný;
- aký target context sa použil;
- ktoré jobs boli povinné;
- či dokončili všetky shards a child pipelines;
- či pipeline použila aktuálnu CI konfiguráciu a policy;
- či výsledok stále patrí aktuálnemu diffu.

Pipeline na starom source SHA je historické evidence, nie dôkaz aktuálnej verzie MR.

## 14. Pipeline nemá iba green a red stav

Rozhodovací model potrebuje rozlišovať príčinu neprítomného alebo neplatného dôkazu.

- **Passed —** všetky required checks sa kompletne vykonali nad správnym subjectom.
- **Failed —** test alebo kontrola našli porušenie.
- **Pending/running —** rozhodnutie ešte nemá všetky vstupy.
- **Canceled alebo superseded —** run bol nahradený novším subjectom.
- **Skipped/not applicable —** job sa nevytvoril podľa rules; treba potvrdiť správnosť applicability.
- **Tool alebo infrastructure error —** kontrola neprebehla dôveryhodne.
- **Incomplete —** chýba shard, report alebo downstream výsledok.

`Tool error` a `incomplete` nie sú úspech. Ak ich platforma zobrazuje podobne ako neblokujúci stav, policy musí ich význam výslovne opraviť.

## 15. Discussions a význam resolved stavu

Diskusia zachytáva otázku alebo identifikovaný risk. `Resolved` má znamenať, že outcome je známy, nie že komentár zmizol z aktívneho zoznamu.

Platný outcome môže byť:

```text
opravené v commite X
| akceptované s vysvetleným trade-offom
| odložené do issue Y s ownerom a riskom
| zamietnuté po dohode s reviewerom
```

Komentár viazaný na outdated line môže stále opisovať platný problém. Významná pripomienka nemá byť uzavretá iba textom „neskôr“ bez issue alebo vlastníka.

## 16. Code Owners

CODEOWNERS mapuje paths na ownership subjects. Pomáha automaticky privolať správnych reviewerov pre citlivé oblasti, napríklad databázové migrácie, deployment manifests, shared CI templates alebo public API schemas.

Mechanizmus funguje iba vtedy, keď:

- patterns zodpovedajú reálnemu layoutu;
- owners majú platný a dostatočný access;
- target branch policy Code Owner approval skutočne vyžaduje;
- existuje fallback pri neprítomnosti ľudí;
- zmena samotného CODEOWNERS súboru je chránená.

CODEOWNERS nie je dependency graph ani dôkaz odbornosti. Shared library môže mať nepriamy dopad mimo matched pathu a formálny owner môže byť organizačne neaktuálny.

## 17. Mergeability je výsledok viacerých vrstiev

MR môže byť approved a stále nemergeovateľný.

```text
nie je draft
+ nemá konflikt
+ required pipelines sú fresh a complete
+ applicable approvals sú splnené
+ required discussions sú resolved
+ protected-branch policy povoľuje actorovi merge
+ merge-result alebo queue candidate je platný
→ mergeable
```

Mergeability je odvodený verdict. Keď sa zmení target branch alebo candidate, môže sa vrátiť do blocked stavu bez toho, aby sa zmenil source branch.

## 18. Merge strategy a výsledná história

Merge strategy určuje, aký commit vznikne v target branchi a ako sa bude zmena neskôr sledovať alebo vracať.

**Merge commit** zachová source commits a pridá explicitný integration commit. História lepšie ukazuje branch boundary, ale môže byť zložitejšia.

**Fast-forward alebo semi-linear model** udržiava lineárnejšiu mainline. Často vyžaduje rebase na aktuálny target, čím sa zmenia source SHA a evidence.

**Squash merge** vytvorí jeden výsledný commit. Zjednodušuje revert logickej zmeny, ale source SHA sa do mainline nemusia dostať.

Pri squash musí traceability vyzerať takto:

```text
source commits
→ MR a review history
→ squash result SHA
→ artifact provenance
→ deployment record
```

Stratégia sa vyberá podľa release, backport, signed-commit, rollback a audit požiadaviek, nie iba podľa vizuálnej preferencie histórie.

## 19. Merge when pipeline succeeds

Automatický merge po splnení gates odstraňuje manuálne čakanie. Bezpečný je iba vtedy, keď sa zruší pri novom pushi, používa aktuálny target context, rešpektuje approval freshness a audit zaznamená, ktorá policy merge vykonala.

Pri vysokej concurrency nestačí, že každý MR samostatne prešiel. Dva kandidáty môžu meniť rovnaký contract a po spojení rozbiť mainline.

## 20. Merge train a integration race

Merge train testuje predpokladané poradie čakajúcich MR.

```text
main + MR-A
→ candidate A

main + MR-A + MR-B
→ candidate B
```

Ak candidate A zlyhá alebo sa zmení, candidate B už nestojí na platnom základe a musí sa prepočítať. Merge train preto potrebuje queue ordering, candidate SHA, invalidation reason, capacity a jasnú failure attribution.

Merge train rieši integration race. Nezlepší slabý review, chýbajúci test ani nekompatibilnú databázovú migráciu.

## 21. Security approval potrebuje celý evidence chain

Security approval nemá byť iba reakcia na červenú ikonu. Dôveryhodný chain vyzerá takto:

```text
aktuálny MR subject
→ applicable analyzer sa úspešne vykonal
→ report je úplný a viazaný na správny subject
→ finding je klasifikovaný ako nový alebo existujúci
→ risk sa posúdi podľa severity, reachability a exposure
→ policy určí potrebné rozhodnutie
→ eligible security approver rozhodne
```

Ak scanner chýbal, zlyhal alebo nepokrýva daný jazyk, výsledok nemá byť interpretovaný ako „žiadne vulnerabilities“.

## 22. Approval exception a break-glass

Urgentná oprava môže vyžadovať obídenie štandardného kroku. Exception však musí zostať úzka a rekonštruovateľná.

Obsahuje konkrétny MR alebo rule scope, dôvod, risk ownera, compensating controls, jednorazový alebo expirovateľný charakter a follow-up.

```text
urgentná potreba
→ explicitný privileged action
→ minimálne safety checks
→ merge a deployment evidence
→ dodatočný review
→ doplnenie preskočených kontrol
→ oprava príčiny bypassu
```

Ak Maintainer bypassuje pravidlá každý týždeň, nejde o emergency workflow. Policy alebo delivery systém je zle navrhnutý.

## 23. Čo má reviewer skutočne posudzovať

Review nemá byť iba syntax kontrola. Hĺbka závisí od scope-u a risku, ale typicky spája:

- intent a requirement;
- correctness a error handling;
- security, authorization a data handling;
- API, event a databázovú kompatibilitu;
- performance a resource dopad;
- observability a operability;
- migration, rollout a recovery;
- kvalitu test evidence;
- zbytočnú komplexitu.

Autor pomáha kvalitnému review tým, že vysvetlí intent, risk a spôsob overenia. Veľký diff bez navigácie zvyšuje pravdepodobnosť povrchného approval.

## 24. Menšie MR a bezpečné medzistavy

Menší MR skracuje review a znižuje počet možných príčin failure-u. Zmena sa však nesmie rozdeliť tak, že jednotlivé kroky vytvoria nebezpečný runtime stav.

Bezpečný databázový sequence môže byť:

```text
MR 1: backward-compatible schema expand
MR 2: tolerant readers a writers
MR 3: backfill a traffic switch
MR 4: contract po skončení rollback window
```

Rozdelenie podľa počtu riadkov by mohlo nasadiť writer, ktorý očakáva ešte neexistujúcu schema. Dôležitá je samostatná deployability každého medzistavu.

## 25. MR nekončí merge kliknutím

Po merge musí zostať evidence chain:

```text
issue alebo requirement
→ MR ID
→ reviewed source SHA
→ approvals a diskusie
→ merged-result evidence
→ final target SHA
→ artifact digest
→ deployment a release record
→ runtime validation
```

Pri squash, rebase alebo merge train modeli sa commit identity mení. Release provenance preto musí explicitne mapovať final artifact na MR a reviewovaný obsah.

## 26. Metriky review systému

Metriky majú odhaľovať flow a kvalitu, nie motivovať k mechanickému klikaníu.

Sleduj time to first review, celkový merge lead time, čakanie na konkrétne approval rules, vek unresolved discussions, merge-train queue, počet bypassov a post-merge defects.

Pri interpretácii spoj rýchlosť s výsledkom. Kratší review čas pri rastúcom počte escaped defects nie je zlepšenie. Vyšší approval count bez zníženia risku tiež nie je úspech.

## 27. Kompletný príklad merge rozhodnutia

Jana pridala idempotency handling, databázovú migráciu a zmenu `.gitlab-ci.yml`.

1. Source branch pipeline overí lokálne unit testy.
2. MR policy aktivuje service-owner, database-owner a platform-owner review.
3. Target branch sa posunie, preto sa vytvorí nový merged-result candidate.
4. Pipeline overí aplikáciu, migration compatibility a resolved CI graph.
5. Jana pridá opravu; predchádzajúce approvals sa podľa policy resetujú.
6. Revieweri potvrdia nový diff a všetky významné threads dostanú outcome.
7. Merge train testuje kandidáta za predchádzajúcim MR.
8. Squash merge vytvorí final SHA.
9. Build publikuje artifact digest a provenance obsahuje MR ID aj candidate evidence.
10. Production deployment record overí, že nasadený digest pochádza z final SHA.

Takýto workflow nepridáva controls pre ich počet. Každý krok rieši konkrétny risk: correctness, ownership, integration race alebo traceability.

## 28. Troubleshooting

### MR má approvals, ale nemožno ho mergeovať

Approval je iba jedna vrstva. Over pipeline freshness, conflicts, unresolved discussions, Code Owners, target branch policy a merge-train candidate.

### Approval zmizol po pushi alebo rebase

Zmenil sa subject SHA. Skontroluj reset policy a zisti, ktoré časti diffu musí reviewer znovu potvrdiť.

### Používateľ je v approver group, ale approval sa nepočíta

Over applicable rule, membership path, effective role, target branch a self/committer restrictions. Group membership sama osebe nedokazuje eligibility.

### MR pipeline nevidí protected variables

Pipeline context nie je považovaný za trusted. Neobchádzaj boundary sprístupnením secretu; oddeľ untrusted validation od privileged post-merge alebo deployment workflowu.

### Code Owner approval sa nevyžaduje

Over pattern match, target branch protection, enforcement setting, owner eligibility a to, či zmena skutočne patrí do matched pathu.

### Merge train opakovane spúšťa nové pipelines

Mení sa target branch alebo skorší candidate. Skontroluj invalidation reason, flaky jobs, queue ordering a runner capacity.

### Zelený MR po merge rozbil main

Branch pipeline pravdepodobne netestovala aktuálny merge result alebo súbežné MRs vytvorili integration race. Zaveď merged-results pipeline a merge queue/train podľa potreby.

## 29. Typické anti-patterny

### Approval od autora ako jediný control

Neposkytuje nezávislý pohľad ani separation of duties.

### Approval count bez definovaného rizika

Viac kliknutí vytvorí queue, ale nemusí zvýšiť kvalitu rozhodnutia.

### Approval zostáva po zásadnej zmene

Reviewer rozhodol nad iným subjectom; evidence je stale.

### Review iba podľa zelenej pipeline

Automatické testy neoverujú celý intent, architecture, security ani operability.

### Required Code Owners bez fallbacku

Ownership policy sa pri absencii jedného človeka zmení na delivery outage.

### Maintainer bypass ako normálny workflow

Platformová policy prestáva reprezentovať skutočný decision flow.

### Branch pipeline považovaná za merge-result dôkaz

Nekontroluje interakciu source zmeny s aktuálnym target branchom.

### Resolved thread bez outcome

Komentár zmizne z UI, ale risk zostane v systéme.

## 30. Praktický rozhodovací rámec

Pre MR workflow odpovedz:

1. Aký presný subject sa reviewuje a testuje?
2. Ktoré zmeny invalidujú approvals a pipelines?
3. Aký risk chráni každá approval rule?
4. Ako sa určuje eligible approver a fallback?
5. Ktoré paths vyžadujú Code Owners a prečo?
6. Potrebujeme merged-result pipeline alebo merge train?
7. Ako sa rozlišuje failed, incomplete a tool-error evidence?
8. Čo znamená resolved discussion?
9. Aká merge strategy zachová požadovanú traceability?
10. Ako sa security finding mení na risk decision?
11. Ako funguje exception a break-glass lifecycle?
12. Ako sa final SHA mapuje na artifact a deployment?

## 31. Kontrolný checklist

- MR intent a scope sú explicitné;
- current source SHA a target context sú známe;
- required evidence patrí aktuálnemu subjectu;
- approvals majú definovanú reset a freshness policy;
- každá rule chráni pomenovaný risk;
- eligible approver resolution je vysvetliteľný;
- Code Owners patterns sú testované a owners majú fallback;
- významné discussions majú explicitný outcome;
- tool failure a incomplete pipeline nie sú pass;
- merge strategy zachováva potrebnú traceability;
- concurrency model rieši integration race;
- security report má coverage, subject a provenance;
- exception má scope, ownera, compensating controls a follow-up;
- final merge SHA sa mapuje na artifact a release record.

## 32. Kontrolné otázky

1. Prečo MR nie je iba webová forma `git merge`?
2. Čo je subject merge rozhodnutia?
3. Aký je rozdiel medzi source SHA, diffom, merged-result SHA a final SHA?
4. Prečo branch pipeline nemusí dokazovať bezpečnú integráciu?
5. Aký je rozdiel medzi review a approval?
6. Čo musí definovať approval rule?
7. Ako vzniká stale approval?
8. Ako sa určuje eligible approver?
9. Kedy je discussion skutočne resolved?
10. Čo Code Owners zabezpečujú a čo nezabezpečujú?
11. Prečo `approved` nie je synonymom `mergeable`?
12. Ako merge strategy mení traceability?
13. Aký race rieši merge train?
14. Čo potrebuje security approval založený na scanner reporte?
15. Ako má vyzerať auditovateľný approval bypass?

## Summary

GitLab merge request je evidence-driven integration decision nad presným source a target contextom. Dôveryhodný workflow oddeľuje review od approval, viaže approvals a pipelines na aktuálny subject, vysvetľuje eligibility, vynucuje ownership a discussion outcomes a podľa potreby testuje merged-result candidate. Merge strategy a merge train riešia commit identity a integration race, zatiaľ čo post-merge provenance zachováva väzbu od reviewovaného diffu až po artifact a deployment. Zelený approval count alebo branch pipeline samy osebe nedokazujú bezpečnú integráciu.

## Glossary impact

Relevantné pojmy: GitLab merge request, MR subject, source SHA, diff, merged-result SHA, final merge SHA, approval rule, eligible approver, stale approval, Code Owner, unresolved discussion, mergeability verdict, merge strategy, squash merge, merge train, security approval policy, approval exception a post-merge traceability.

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