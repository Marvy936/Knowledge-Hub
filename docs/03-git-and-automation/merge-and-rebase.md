# Merge a rebase

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Git and Automation Basics
- Predpoklady: [Commit, branch, tag a HEAD](commit-branch-tag-head.md), [Clone, fetch, pull a push](clone-fetch-pull-push.md)
- Súvisiace témy: commit graph, merge base, three-way merge, history rewrite, conflicts, reflog

## 1. Definícia

Merge a rebase sú dva rozdielne spôsoby integrácie zmien z odlišných vetiev commit graphu.

- **merge** — spojí ancestry oboch vetiev; pri skutočnej divergencii typicky vytvorí merge commit s viacerými parentmi,
- **rebase** — vyberie sériu commitov, vypočíta ich zmeny voči pôvodnej báze a vytvorí nové commits nad novou bázou.

Obe operácie môžu vytvoriť rovnaký výsledný filesystem snapshot, ale nie rovnakú históriu. Rozdiel ovplyvňuje audit, budúce merge-base výpočty, revertovanie, podpisy, review aj spôsob synchronizácie so zdieľaným remote.

## 2. Najprv analyzuj commit graph

Pred integráciou zisti:

```bash
git status
git fetch --prune origin
git log --graph --oneline --decorate --all
git log --left-right --cherry-pick --oneline main...feature
git merge-base main feature
```

Dôležité otázky:

- Je working tree a index čistý?
- Ktorá branch je current branch a ktorá sa integruje?
- Existuje divergencia alebo je možný fast-forward?
- Sú commits už publikované a používané inými ľuďmi?
- Vyžaduje tím merge commit, squash alebo lineárnu históriu?
- Sú na commitoch podpisy alebo release/audit väzby?

Integrácia bez znalosti grafu vedie k náhodnému výberu príkazu namiesto vedomého rozhodnutia.

## 3. Merge base

Merge base je najlepší spoločný predok dvoch tipov — bod, od ktorého Git posudzuje nezávislé zmeny oboch strán.

```bash
git merge-base main feature
```

Zjednodušený graf:

```text
       C---D  main
      /
A---B
      \
       E---F  feature
```

`B` je merge base. Git neposudzuje iba rozdiel medzi `D` a `F`; porovnáva:

```text
base:   B
ours:   D
 theirs: F
```

To umožní rozlíšiť, ktoré riadky zmenila iba jedna strana, ktoré zmenili obe strany a ktoré zmeny možno spojiť automaticky.

Pri zložitejšom criss-cross grafe môže existovať viac merge bases. Moderná merge stratégia vytvorí vhodnú virtuálnu bázu namiesto mechanického výberu jedného predka.

## 4. Three-way merge

Three-way merge integruje dve množiny zmien voči spoločnej báze:

```text
base → ours
base → theirs
```

Ak sa zmeny nedotýkajú rovnakého logického obsahu, Git ich typicky spojí automaticky. Konflikt vznikne, keď automatický algoritmus nevie bezpečne určiť výsledok, nie preto, že by bol repository poškodený.

Moderný Git používa pre bežný dvojvetvový merge stratégiu `ort`. Okrem textového obsahu zohľadňuje aj rename detection, directory renames, file modes a typy paths.

Výsledok automatického merge je stále potrebné reviewnúť. Syntakticky bezkonfliktný výsledok môže byť semanticky chybný.

## 5. Fast-forward update

Ak current branch nemá commits mimo ancestry druhej vetvy:

```text
A---B  main
     \
      C---D  feature
```

`main` možno posunúť priamo na `D`:

```bash
git switch main
git merge --ff-only feature
```

Výsledok:

```text
A---B---C---D  main, feature
```

Nevznikne nový commit; zmení sa iba branch ref. Fast-forward zachová lineárny graph a nemení existujúce commit IDs.

`--ff-only` je bezpečná politika, keď nechceš, aby Git pri nečakanej divergencii automaticky vytvoril merge commit.

## 6. True merge a merge commit

Pri divergencii:

```text
       C---D  main
      /
A---B
      \
       E---F  feature
```

merge vytvorí nový commit `M`:

```text
       C---D------M  main
      /          /
A---B            /
      \          /
       E---F-----   feature
```

`M` má typicky dvoch parentov:

```text
parent 1 = predchádzajúci tip current branch
parent 2 = tip integrovanej branch
```

Poradie parentov je významné. Ovplyvňuje first-parent log, revision syntax `M^1`/`M^2` a revert merge commitu.

```bash
git merge --no-ff feature
git show --no-patch --pretty=raw HEAD
git log --first-parent --oneline main
```

Merge commit zaznamenáva integráciu ako explicitnú udalosť. To je vhodné, keď feature/release branch predstavuje auditovateľnú jednotku alebo keď chce tím zachovať skutočnú topológiu spolupráce.

## 7. Fast-forward policy

Bežné politiky:

```bash
git merge --ff-only feature   # iba posun refu
git merge --no-ff feature     # vytvor merge commit aj keď je možný FF
git merge feature             # použije konfiguračnú/default policy
```

Trade-off:

- `--ff-only` — čistý lineárny graph, ale nezachytí branch integráciu ako samostatnú udalosť,
- `--no-ff` — explicitná hranica feature, ale viac merge commitov,
- implicitná policy — pohodlná, ale menej predvídateľná, ak tím nemá spoločnú konfiguráciu.

Repository policy má určovať požadovaný graph, nie osobný zvyk jednotlivca.

## 8. Rebase ako replay commitov

Rebase nepresúva existujúce commits. Vytvorí nové commit objects.

Pred:

```text
A---B---C---D  main
     \
      E---F    feature
```

Príkaz:

```bash
git switch feature
git rebase main
```

Po:

```text
A---B---C---D---E'---F'  feature
```

Zjednodušený lifecycle:

1. Git určí old base a commits unikátne pre feature.
2. Uloží zmeny jednotlivých commitov v poradí.
3. Presunie pracovnú bázu na nový base.
4. Aplikuje každú zmenu.
5. Vytvorí nový commit s novým parentom a committer metadata.
6. Posunie branch ref na posledný nový commit.

Aj pri rovnakom tree obsahu majú `E'` a `F'` nové IDs, pretože sa zmenili parent, committer timestamp alebo ďalšie commit metadata.

## 9. Patch identity a cherry ekvivalencia

Starý a nový commit po rebase nemajú rovnaké object ID, ale môžu reprezentovať ekvivalentnú zmenu.

Užitočné nástroje:

```bash
git patch-id --stable
git log --cherry-pick --left-right old-tip...new-tip
git range-diff old-base..old-tip new-base..new-tip
```

`git range-diff` porovnáva dve série commitov a pomáha overiť, či rebase zachoval zamýšľanú zmenu, či commit nezmizol alebo či sa počas riešenia konfliktu nezmenil jeho význam.

Rovnaký patch však nie je rovnaká ancestry udalosť. Rebase mení históriu aj vtedy, keď obsah zostane ekvivalentný.

## 10. Kedy je merge vhodnejší

Merge je zvyčajne vhodnejší, keď:

- commits už používa viac ľudí,
- branch je publikovaná a nie je dohodnutý rewrite,
- treba zachovať ancestry a integráciu ako auditnú udalosť,
- release alebo compliance proces odkazuje na pôvodné commit IDs,
- signatures alebo attestations musia zostať viazané na pôvodné objekty,
- pravidelne sa spájajú dlhšie žijúce release branches.

Merge je aditívny: pridá nový commit a nemení existujúce objekty.

## 11. Kedy je rebase vhodnejší

Rebase je zvyčajne vhodný, keď:

- upratuješ vlastnú nepublikovanú feature branch,
- chceš rozbiť alebo zlúčiť lokálne work-in-progress commits,
- aktualizuješ branch na nový base pred review alebo integráciou,
- tím používa lineárnu históriu a explicitne povoľuje rewrite feature branches,
- potrebuješ presunúť vybranú sériu na inú bázu.

Základná bezpečnostná otázka nie je „je rebase zlý?“, ale:

```text
Kto už používa commit IDs, ktoré sa chystám nahradiť?
```

## 12. Interactive rebase

```bash
git rebase -i HEAD~5
```

Typické operácie:

```text
pick     ponechať commit
reword   zmeniť message
edit     zastaviť a upraviť commit
squash   zlúčiť s predchádzajúcim a upraviť message
fixup    zlúčiť bez zachovania samostatnej message
drop     odstrániť commit
exec     spustiť príkaz medzi krokmi
break    zastaviť sekvenciu
```

Interactive rebase môže:

- zmeniť poradie commitov,
- rozdeliť jeden commit,
- zlúčiť fixup commits,
- opraviť messages,
- vložiť testy cez `exec`,
- odstrániť omylom commitnutý obsah.

Každý dotknutý commit a každý jeho následník dostane nové ID.

Pred rewrite si ulož pôvodný tip:

```bash
git branch backup/feature-before-rebase
```

## 13. Autosquash

Commity vytvorené ako:

```bash
git commit --fixup=<target-commit>
git commit --squash=<target-commit>
```

možno automaticky usporiadať:

```bash
git rebase -i --autosquash <base>
```

Autosquash znižuje manuálne presúvanie todo listu, ale stále ide o history rewrite. Po dokončení treba overiť diff aj testy.

## 14. `rebase --onto`

Všeobecný tvar:

```bash
git rebase --onto <new-base> <upstream-boundary> <branch>
```

Význam:

```text
vyber commits reachable z <branch>,
ktoré nie sú reachable z <upstream-boundary>,
a replayni ich na <new-base>
```

Príklad presunu feature branch z nesprávnej bázy:

```text
A---B---C---D  main
     \
      E---F    old-base
           \
            G---H  feature
```

```bash
git rebase --onto main old-base feature
```

Nesprávne hranice môžu vynechať commit, znovu aplikovať už integrovanú zmenu alebo presunúť väčší rozsah, než bol zámer. Pred operáciou si rozsah zobraz:

```bash
git log --oneline old-base..feature
```

## 15. Merge conflicts a index stages

Po konflikte index drží:

```text
stage 1 — merge base
stage 2 — ours
stage 3 — theirs
```

```bash
git status
git ls-files -u
git show :1:path/to/file
git show :2:path/to/file
git show :3:path/to/file
```

Pri bežnom merge:

- `ours` je current branch,
- `theirs` je integrovaná branch.

Pri rebase je mentálny model zradnejší:

- `ours` typicky predstavuje nový base s už replaynutými commitmi,
- `theirs` predstavuje práve replayovaný starý commit.

Nespoliehaj sa iba na názvy. Over konkrétny obsah stages a zamýšľaný výsledok.

Po vyriešení:

```bash
git add <path>
git merge --continue       # ak Git danú verziu podporuje, inak git commit
git rebase --continue
```

Preskočenie rebase commitu:

```bash
git rebase --skip
```

použi iba vtedy, keď je jeho zmena už skutočne obsiahnutá alebo už nie je žiaduca. Inak ticho stratíš funkčnosť.

## 16. Abort a state files

Rozpracovaná operácia má stav v `.git`, napríklad:

- `MERGE_HEAD`,
- `ORIG_HEAD`,
- `REBASE_HEAD`,
- `rebase-merge/` alebo `rebase-apply/`.

Bezpečné zrušenie:

```bash
git merge --abort
git rebase --abort
```

Abort sa snaží obnoviť predoperačný stav, ale necommitnuté zmeny existujúce pred operáciou môžu recovery komplikovať. Preto začínaj s čistým working tree alebo vytvor explicitný commit/stash.

`ORIG_HEAD` často ukazuje na predchádzajúci významný tip, ale reflog je všeobecnejší recovery zdroj.

## 17. Merge options a stratégie

Často zamieňané voľby:

```bash
git merge -Xours feature
git merge -Xtheirs feature
git merge -s ours feature
```

- `-Xours` — pri konfliktných hunks preferuje našu stranu; neignoruje všetky nekonfliktné zmeny druhej vetvy,
- `-Xtheirs` — pri konfliktných hunks preferuje druhú stranu,
- `-s ours` — vytvorí merge ancestry, ale výsledný tree ponechá z current branch; obsah druhej vetvy sa ignoruje.

Automatická preferencia strany môže vytvoriť syntakticky čistý, ale funkčne chybný výsledok. Používaj ju iba pri jasnom invariantnom dôvode.

## 18. Squash merge

```bash
git switch main
git merge --squash feature
git commit -m 'feat: integrate feature'
```

Squash pripraví kombinovaný obsah zmien v indexe, ale nevytvorí merge ancestry.

```text
feature: E---F
main:    C---S
```

`S` nemá `F` ako parent. Dôsledky:

- Git nepovažuje feature commits za ancestry integrované,
- neskorší merge tej istej branch môže znovu vidieť staré zmeny,
- jednotlivé feature commit IDs nie sú súčasťou first-parent release histórie,
- revertuje sa výsledný squash commit, nie merge relationship,
- review platforma môže feature branch po merge zmazať, hoci jej commits nie sú ancestry mainu.

Squash je vhodný, keď je feature branch pracovný detail a cieľom je jeden kurátorovaný commit.

## 19. Rebase merges

Bežný rebase linearizuje vybranú sériu. Ak treba zachovať vnútorné merge štruktúry, existuje:

```bash
git rebase --rebase-merges <new-base>
```

Aj v tomto režime vznikajú nové commits a nové merge commits. Výslednú topológiu treba reviewnúť; nejde o zachovanie pôvodných object IDs.

## 20. Signatures, attestations a audit

Rebase, amend a squash vytvárajú nové commit objekty. Pôvodné commit signatures sa neprenesú ako platné podpisy nových objektov.

Dôsledky:

- signed commit musí byť po rewrite znovu podpísaný,
- CI attestation viazaná na staré SHA sa nevzťahuje na nové SHA,
- externé odkazy na commit ID môžu prestať ukazovať na publikovanú branch,
- auditný systém musí rozlišovať authora pôvodnej zmeny a committera rewritten objektu.

History policy preto nie je iba estetická voľba.

## 21. Revertovanie merge commitu

Merge commit má viac parentov, preto revert potrebuje určiť mainline parent:

```bash
git revert -m 1 <merge-commit>
```

`-m 1` znamená: zachovaj pohľad parenta 1 ako hlavnej línie a odober efekt integrovanej strany.

Revert merge nevymaže ancestry. Git si stále pamätá, že vetvy boli spojené. Neskoršie opätovné zavedenie rovnakej feature môže vyžadovať revert pôvodného revertu alebo novú zmenu. Toto je častý dôvod, prečo treba parent order a graph chápať pred zásahom.

## 22. `rerere`

Reuse Recorded Resolution si pamätá konflikt shape a zvolený výsledok:

```bash
git config rerere.enabled true
git rerere status
git rerere diff
```

Je užitočný pri:

- opakovaných rebase cykloch,
- dlhodobých release branches,
- testovaní merge výsledku pred finálnou integráciou.

Automaticky znovu použitú resolution vždy reviewni. Rovnaký textový konflikt nemusí mať rovnaký business význam po zmene okolitého kódu.

## 23. Overenie výsledku

Po merge:

```bash
git status
git show --stat --summary HEAD
git diff HEAD^1..HEAD
git log --graph --oneline --decorate --all
```

Po rebase:

```bash
git status
git range-diff backup/feature-before-rebase...feature
git diff <old-tip>^{tree} <new-tip>^{tree}
git log --graph --oneline --decorate --all
```

Potom spusti:

- formatter/linter,
- unit a integračné testy,
- build,
- relevantný používateľský scenár.

Čistý `git status` dokazuje iba dokončený Git stav, nie funkčnú správnosť integrácie.

## 24. Publikovanie rewritten branch

Ak bola feature branch po rebase už na remote a policy rewrite povoľuje:

```bash
git fetch origin
git push --force-with-lease origin feature
```

`--force-with-lease` chráni pred prepísaním neznámeho nového remote tip-u. Stále však nahrádza publikovanú ancestry. Pred pushom:

```bash
git log --left-right --graph --oneline origin/feature...feature
```

Na protected alebo zdieľanej branch preferuj merge/revert pred nekoordinačným rewrite.

## 25. Recovery

Pred rizikovou operáciou:

```bash
git status
git branch backup/feature-before-integration
git rev-parse HEAD
```

Po nežiaducom výsledku:

```bash
git reflog --date=iso
git show <old-tip>
git branch recovery/integration <old-tip>
```

Až po zachovaní starého tipu môžeš vedome presunúť branch:

```bash
git reset --hard <old-tip>
```

`reset --hard` zahodí tracked working-tree a index zmeny. Nie je to prvý diagnostický krok.

Ak už bol chybný merge publikovaný na zdieľanej branch, bezpečnejší býva `git revert` než reset a force push.

## 26. Bezpečný integračný workflow

```bash
git status
git fetch --prune origin
git switch feature
git branch backup/feature-before-integration
git log --graph --oneline --left-right feature...origin/main

# vyber jednu tímom povolenú operáciu:
git rebase origin/main
# alebo
git switch main && git merge --no-ff feature

# overenie
git status
git log --graph --oneline --decorate --all
git diff --check
# test suite / build / smoke test
```

Konkrétny príkaz je až posledný krok. Najprv musí byť jasný požadovaný graph, vlastníctvo histórie a recovery cesta.

## 27. Troubleshooting

### Rebase hlási, že commit bol skipped

Možné vysvetlenia:

- ekvivalentný patch už existuje v novej báze,
- commit bol predtým cherry-picknutý,
- patch-id heuristika ho vyhodnotila ako ekvivalentný,
- nesprávne zvolený upstream rozsah.

Over:

```bash
git log --cherry-pick --left-right --oneline old-base...new-base
git range-diff <old-range> <new-range>
```

### Merge vytvoril neočakávaný commit

Skontroluj:

```bash
git show --no-patch --pretty=raw HEAD
git config --get merge.ff
git reflog -5
```

Ak ešte nebol publikovaný a chceš operáciu vrátiť, najprv zachovaj tip a potom použi reflog/`ORIG_HEAD` podľa situácie.

### Po rebase chýba zmena

```bash
git reflog
git range-diff <old-base>..<old-tip> <new-base>..<new-tip>
git diff <old-tip>^{tree} <new-tip>^{tree}
```

Náprava nie je automaticky „rebase zopakovať“. Najprv identifikuj konkrétny stratený commit alebo nesprávne vyriešený konflikt.

## 28. Časté omyly

### „Merge a rebase menia iba vizuálny graf“

Nie. Rebase vytvára nové objekty; merge môže vytvoriť nový snapshot a ancestry vzťah.

### „Rebase presunie commits“

Nie. Replayne ich zmeny a vytvorí nové commits.

### „Merge bez konfliktu je automaticky správny“

Nie. Git kontroluje textovú/štrukturálnu zlúčiteľnosť, nie business invarianty.

### „Squash merge je true merge s jedným commitom“

Nie. Squash commit nemá feature tip ako parent.

### „`-Xours` bezpečne vezme celú našu verziu“

Preferuje našu stranu iba pri konfliktných hunks; ostatné zmeny druhej vetvy sa stále integrujú.

### „`--force-with-lease` nerobí history rewrite“

Robí. Iba overuje očakávaný remote tip pred jeho nahradením.

## 29. Kontrolné otázky

1. Prečo Git potrebuje merge base?
2. Aký je rozdiel medzi fast-forward update a merge commitom?
3. Prečo rebase vytvára nové commit IDs?
4. Čo porovnáva `git range-diff`?
5. Kedy je merge bezpečnejší než rebase?
6. Aký je rozdiel medzi `-Xours` a `-s ours`?
7. Prečo squash merge nezaznamená feature ancestry?
8. Prečo sa `ours` a `theirs` pri rebase môžu javiť obrátene?
9. Ako podpisy a attestations ovplyvňuje history rewrite?
10. Ako obnovíš pôvodný tip po chybnom rebase?

## Glossary impact

Relevantné pojmy: merge base, three-way merge, fast-forward, merge commit, parent order, rebase, replay, patch identity, interactive rebase, autosquash, squash merge, history rewrite, rerere, range-diff.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Clone, fetch, pull a push](clone-fetch-pull-push.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Reset, revert a restore →](reset-revert-restore.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
