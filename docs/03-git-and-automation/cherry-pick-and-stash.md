# Cherry-pick a stash

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Git and Automation Basics
- Predpoklady: [Commit, branch, tag a HEAD](commit-branch-tag-head.md), [Merge a rebase](merge-and-rebase.md), [Reset, revert a restore](reset-revert-restore.md)
- Súvisiace témy: patch replay, backport, sequencer, patch identity, temporary work, reflog recovery

## 1. Dve odlišné operácie

`cherry-pick` a `stash` riešia iné problémy:

```text
cherry-pick → replay zmeny vybraného commitu na aktuálny tip
stash       → dočasne uloží index/working-tree stav do Git objektov
```

Cherry-pick pracuje s commit history a vytvára nový commit. Stash primárne pracuje s rozpracovaným lokálnym stavom a uloží ho pod `refs/stash`.

## 2. Cherry-pick — definícia

```bash
git cherry-pick <commit>
```

Git vezme zmenu reprezentovanú commitom voči jeho parentovi, aplikuje ju na current `HEAD` a vytvorí nový commit.

Výsledný commit má:

- nový parent,
- nové object ID,
- typicky zachovaného autora,
- nového committera a committer timestamp,
- podobný patch intent,
- nový kontext v commit graph-e.

Cherry-pick teda neprenáša objekt. Replayuje zmenu.

## 3. Commit graph dôsledok

```text
source: A---B---C

target: X---Y
              \
               C'
```

`C'` nemá ancestry vzťah k `C`. Môžu mať ekvivalentný patch, ale sú to dva rozdielne commits.

Dôsledky:

- source branch sa nepovažuje za merge-nutú,
- neskorší merge môže naraziť na ekvivalentnú alebo čiastočne ekvivalentnú zmenu,
- commit signatures a attestations pôvodného objektu sa nevzťahujú na nový objekt,
- audit musí vedieť rozlíšiť origin commit a backport commit.

## 4. Typické použitia

Cherry-pick je vhodný najmä pre:

- backport opravy do podporovanej release branch,
- prenos izolovaného fixu bez celej feature branch,
- obnovu commitov z detached HEAD alebo zmazanej branch,
- prenos hotfixu medzi paralelnými release líniami,
- zostavenie kurátorovanej série z viacerých zdrojov.

Nie je vhodný ako dlhodobá náhrada merge alebo rebase celej branch. Opakovaný manuálny cherry-pick veľkých sérií vytvára duplicate-patch a dependency riziká.

## 5. Pred cherry-pickom analyzuj commit

```bash
git show --stat --summary <commit>
git show --format=fuller <commit>
git log --oneline --decorate <commit>^..<commit>
git branch --contains <commit>
```

Over:

- má commit jedného parenta alebo je merge commit,
- závisí od skorších commitov,
- obsahuje migration/schema/config zmenu,
- bol už ekvivalentný patch prenesený,
- je target branch kompatibilná s API a dátovým modelom zmeny,
- vyžaduje samostatný test alebo rollout krok.

Izolovaný textový patch nemusí byť izolovaná funkčná zmena.

## 6. Dependency ordering

Ak commit `C` závisí od `B`, samotný cherry-pick `C` môže:

- konfliktovať,
- prejsť bez konfliktu, ale nekompilovať,
- vytvoriť runtime chybu,
- obísť bezpečnostný invariant zavedený v `B`.

Pred sériou:

```bash
git log --reverse --oneline A^..C
git show --stat A B C
```

Commity aplikuj v dependency poradí, nie podľa náhodného výberu zo stránky pull requestu.

## 7. Revision ranges

```bash
git cherry-pick A B C
git cherry-pick A..C
git cherry-pick A^..C
```

Rozdiel:

- `A B C` — explicitný zoznam v zadanom poradí,
- `A..C` — commits reachable z `C`, ktoré nie sú reachable z `A`; typicky nezahŕňa `A`,
- `A^..C` — rozsah môže zahrnúť aj `A`.

Pred operáciou vždy zobraz presný výber:

```bash
git rev-list --reverse --oneline A..C
git log --reverse --oneline A^..C
```

Revision range je množina commitov podľa reachability, nie automaticky lineárny textový interval.

## 8. Poradie replayu

Pri viacerých commits Git používa sequencer a replayuje ich v zvolenom poradí.

Bezpečný explicitný postup:

```bash
commits=$(git rev-list --reverse A^..C)
git cherry-pick $commits
```

V shell automatizácii treba dávať pozor na quoting a veľkosť zoznamu. Pri produkčnom backporte je často lepší explicitný reviewovaný zoznam SHA než dynamický rozsah.

## 9. `-x` pre audit backportu

```bash
git cherry-pick -x <commit>
```

Do commit message pridá pôvodný commit ID, typicky v tvare:

```text
(cherry picked from commit <sha>)
```

Výhody:

- dohľadanie origin fixu,
- rozlíšenie backportu od nezávislej podobnej zmeny,
- jednoduchšie porovnanie podporovaných release branches,
- lepší incident a security audit.

`-x` nedokazuje, že patch zostal nezmenený počas riešenia konfliktov. Výsledný diff treba stále overiť.

## 10. No-commit režim

```bash
git cherry-pick --no-commit <commit>
# skrátene
git cherry-pick -n <commit>
```

Zmena sa aplikuje do indexu a working tree, ale nevytvorí sa commit.

Použitie:

- skombinovať viac malých source commitov do jedného backportu,
- manuálne upraviť patch pre staršiu release branch,
- otestovať výsledok pred vytvorením commitu.

Riziká:

- stráca sa one-to-one audit,
- staged state môže obsahovať aj staršie lokálne zmeny,
- výsledná message musí uviesť všetky source commits,
- partial failure série sa diagnostikuje ťažšie.

Pred `-n` začínaj s čistým indexom a working tree.

## 11. Cherry-pick merge commitu

Merge commit má viac parentov, preto Git nevie automaticky, voči ktorému parentovi má vypočítať zmenu.

```bash
git show --no-patch --pretty=raw <merge-commit>
git cherry-pick -m 1 <merge-commit>
```

`-m 1` znamená: vypočítaj efekt merge commitu voči parentovi 1.

Pred výberom mainline porovnaj:

```bash
git diff <merge>^1..<merge>
git diff <merge>^2..<merge>
```

Nesprávny mainline môže aplikovať opačnú alebo podstatne širšiu zmenu, než bol zámer.

Cherry-pick merge commitu nevytvorí nový merge relationship. Výsledný commit má bežne jedného parenta.

## 12. Empty cherry-pick

Commit môže byť pri replayi prázdny, pretože:

- jeho patch už target branch obsahuje,
- neskoršie zmeny ho prekonali,
- conflict resolution odstránila celý efekt,
- commit pôvodne obsahoval iba metadata alebo empty tree change.

Git môže zastaviť s informáciou o empty result.

Možnosti závisia od verzie a zámeru:

```bash
git cherry-pick --skip
git commit --allow-empty -C <source-commit>
```

Empty commit zachovaj iba vtedy, keď má význam ako auditná/migračná udalosť. Inak `--skip` použi až po overení, že požadovaný efekt je skutočne prítomný.

## 13. Conflict lifecycle

Pri konflikte:

```bash
git status
git ls-files -u
git show CHERRY_PICK_HEAD
```

Postup:

```bash
# uprav konfliktné paths
git add <paths>
git cherry-pick --continue
```

Zrušenie celej sekvencie:

```bash
git cherry-pick --abort
```

Preskočenie aktuálneho commitu:

```bash
git cherry-pick --skip
```

`--skip` nie je náhrada riešenia konfliktu. Použi ho iba po dôkaze, že commit je redundantný alebo nežiaduci.

## 14. Sequencer state

Počas série Git udržiava sequencer metadata v `.git/sequencer/` a referencie ako `CHERRY_PICK_HEAD`.

Dôležité príkazy:

```bash
git status
git cherry-pick --continue
git cherry-pick --skip
git cherry-pick --abort
git cherry-pick --quit
```

Rozdiel:

- `--abort` — pokúsi sa obnoviť stav pred sekvenciou,
- `--quit` — odstráni sequencer state, ale nepokúša sa vrátiť už vykonané zmeny.

`--quit` používaj iba pri vedomom manuálnom prevzatí rozpracovaného stavu.

## 15. Patch identity a duplicate changes

Na porovnanie ekvivalentných patchov:

```bash
git cherry -v target source
git log --cherry-pick --left-right --oneline target...source
git patch-id --stable
```

`git cherry` označuje patches, ktoré majú alebo nemajú ekvivalent na druhej strane. Je to heuristika založená na patch identity, nie dôkaz funkčnej ekvivalencie.

Pri neskoršom merge pôvodnej branch môže Git:

- automaticky vyhodnotiť obsah bez konfliktu,
- konfliktovať pre odlišný kontext,
- neaplikovať text duplicitne, ale zachovať duplicate business event,
- znova spustiť migration alebo release automatizáciu viazanú na commit/branch.

## 16. Overenie cherry-picku

Po jednom commite:

```bash
git show --stat --summary HEAD
git diff HEAD^..HEAD
git range-diff <source>^..<source> HEAD^..HEAD
```

Po sérii:

```bash
git log --oneline --reverse <old-target>..HEAD
git range-diff <source-range> <old-target>..HEAD
git diff --check
```

Potom spusti build, tests a relevantný smoke test. Úspešný cherry-pick iba dokazuje, že Git vytvoril commit, nie že backport je kompatibilný so staršou release branch.

## 17. Cherry-pick recovery

Pred sériou:

```bash
git branch backup/before-cherry-pick
git rev-parse HEAD
```

Po zlom dokončenom výsledku, ktorý ešte nebol publikovaný:

```bash
git reflog
git branch recovery/cherry-pick <old-tip>
git reset --hard <old-tip>
```

Po publikovaní na zdieľanej branch preferuj `git revert` nových cherry-picked commitov pred resetom a force pushom.

## 18. Stash — definícia

```bash
git stash push -m 'wip: api timeout'
```

Stash uloží rozpracovaný Git stav do commit-like objektov, aktualizuje `refs/stash` a typicky obnoví working tree/index do čistejšieho stavu.

Stash je:

- lokálny,
- nepomenovaný stabilnou branchou,
- spravovaný cez reflog syntax `stash@{n}`,
- vhodný na krátkodobé odloženie práce,
- nevhodný ako jediný dlhodobý backup.

## 19. Stash interný model

Typický stash má commit topology reprezentujúcu:

- working-tree snapshot,
- index snapshot,
- pôvodný `HEAD` base,
- voliteľne untracked/ignored snapshot.

Kontrola:

```bash
git cat-file -p stash@{0}
git log --graph --oneline --decorate --reflog refs/stash
git show --stat stash@{0}
```

Stash entry je teda graph Git objektov, nie zip súbor ani jednoduchý patch file.

## 20. Čo defaultný stash zahŕňa

Default:

```bash
git stash push
```

ukladá tracked staged a tracked unstaged changes.

Nezahŕňa automaticky:

- untracked files,
- ignored files.

Untracked:

```bash
git stash push --include-untracked
# skrátene -u
```

Ignored aj untracked:

```bash
git stash push --all
# skrátene -a
```

`--all` môže uložiť veľké build outputs, caches, lokálne databázy alebo secrets. Pred operáciou:

```bash
git status --short --ignored
```

## 21. Pathspec a partial stash

Vybrané paths:

```bash
git stash push -- path/to/a path/to/b
```

Interaktívne hunks:

```bash
git stash push --patch
```

Partial stash môže ponechať zvyšok zmien vo working tree. Po dokončení over:

```bash
git status --short
git stash show --stat stash@{0}
git stash show -p stash@{0}
```

Bez kontroly sa ľahko pomýli, ktorá časť práce je uložená a ktorá zostala lokálne.

## 22. `--keep-index`

```bash
git stash push --keep-index
```

Stash zaznamená pracovný stav, ale staged changes ponechá v indexe/working tree podľa semantics konkrétnej verzie Git.

Typické použitie:

1. stage-ni hotovú logickú zmenu,
2. stash-ni zvyšnú rozpracovanú prácu,
3. otestuj a commitni staged snapshot.

Predtým:

```bash
git diff --staged
git diff
```

Po stash:

```bash
git status
git diff --staged
```

## 23. `--staged`

```bash
git stash push --staged
```

Uloží primárne staged zmeny a ponechá unstaged prácu. Je užitočný, keď chceš dočasne odložiť pripravený commit, ale pokračovať v inej pracovnej zmene.

Semantika môže interagovať s partial stagingom a konfliktným indexom. Pred použitím vždy review-ni obidva diffy.

## 24. Apply, pop a drop

```bash
git stash apply stash@{0}
git stash pop stash@{0}
git stash drop stash@{0}
```

- `apply` — aplikuje stash a entry ponechá,
- `pop` — aplikuje stash a pri úspechu ho odstráni,
- `drop` — odstráni entry bez aplikovania.

Pre významnú prácu:

```bash
git stash apply stash@{0}
# over diff, build a tests
git stash drop stash@{0}
```

je bezpečnejšie než okamžitý `pop`.

Pri konflikte `pop` typicky stash entry ponechá, pretože apply nebol úplne úspešný. Stav vždy over cez `git stash list`.

## 25. Obnova indexu cez `--index`

```bash
git stash apply --index stash@{0}
```

Git sa pokúsi obnoviť nielen working-tree obsah, ale aj pôvodné staged/unstaged rozdelenie.

Môže zlyhať, ak:

- current index je nekompatibilný,
- paths sa medzičasom zmenili,
- stash vznikol z konfliktného alebo zložitého partial state,
- target branch má výrazne odlišný tree.

Ak staging hranice nie sú kritické, môže byť jednoduchšie aplikovať bez `--index` a zmeny znova vedome stage-nuť.

## 26. `stash branch`

```bash
git stash branch recovery/stashed-work stash@{0}
```

Git:

1. vytvorí branch z pôvodného base commitu stashu,
2. checkoutne ju,
3. aplikuje stash,
4. pri úspechu stash entry odstráni.

Výhoda: zmena sa aplikuje v pôvodnom kontexte, takže je menej konfliktov než pri aplikovaní na výrazne posunutú current branch.

Pre dôležitú alebo staršiu stash entry je to často najbezpečnejší recovery postup.

## 27. Stash konflikt

Pri konflikte:

```bash
git status
git ls-files -u
git stash show -p stash@{0}
```

Stash apply nemá univerzálny `stash --abort` ekvivalent ako merge/rebase. Recovery postup:

- vyrieš konflikty a commitni výsledok,
- alebo obnov predoperačný stav cez recovery branch/commit/reset podľa toho, čo bolo zmenené,
- stash entry pri `apply` ponechaj, kým výsledok nie je overený.

Preto pred rizikovým apply:

```bash
git branch backup/before-stash-apply
git status
```

## 28. Stash list a naming

```bash
git stash list --date=local
git stash show -p stash@{2}
```

Index `stash@{0}` je relatívny a po `drop` alebo novom stash pushi sa môže zmeniť. Pri dlhšej práci si zaznamenaj object ID:

```bash
git rev-parse stash@{0}
```

Ešte lepšie je vytvoriť pomenovanú branch:

```bash
git branch wip/saved-work stash@{0}
```

Tým vytvoríš stabilný ref na stash working-tree commit, ale interné index/untracked parents treba pri recovery stále chápať.

## 29. Dropnutý alebo clear-nutý stash

```bash
git stash drop stash@{0}
git stash clear
```

odstráni refs/reflog entries, nie nevyhnutne okamžite všetky objekty. Pred GC môže byť recovery možný:

```bash
git fsck --unreachable --no-reflogs
git fsck --lost-found
```

Hľadanie kandidátov:

```bash
git log --all --reflog --oneline --decorate
git show <candidate-commit>
```

Recovery nie je garantovaný. Po garbage collection môžu byť objekty odstránené.

## 30. Kedy radšej WIP branch a commit

Preferuj branch a commit, keď:

- práca je hodnotná alebo trvá dlhšie,
- potrebuje remote backup,
- potrebuješ ju zdieľať,
- chceš CI alebo review,
- stash list je neprehľadný,
- pracuješ na viacerých témach,
- potrebuješ audit a stabilný názov.

```bash
git switch -c wip/api-timeout
git add -A
git commit -m 'wip: preserve timeout investigation'
git push -u origin wip/api-timeout
```

WIP commits možno neskôr upratať interactive rebaseom. Remote branch je výrazne spoľahlivejší backup než lokálny stash.

## 31. Bezpečný backport workflow

```bash
git fetch --prune origin
git switch release/1.x
git pull --ff-only
git branch backup/release-before-backport

git show <source-commit>
git cherry-pick -x <source-commit>

git show --stat HEAD
git diff HEAD^..HEAD
git range-diff <source>^..<source> HEAD^..HEAD
# build, tests, migration validation, smoke test
```

Pri konflikte dokumentuj, prečo bola resolution odlišná od source branch.

## 32. Bezpečný stash workflow

```bash
git status
git diff
git diff --staged
git stash push -u -m 'wip: investigate timeout'
git stash list
git stash show --stat stash@{0}
```

Obnova:

```bash
git switch -c recovery/timeout-work
git stash apply --index stash@{0}
git status
# test a review
git stash drop stash@{0}
```

## 33. Troubleshooting

### Cherry-pick tvrdí, že commit je empty

```bash
git log --cherry-pick --left-right --oneline HEAD...<source-branch>
git diff <source>^..<source>
git diff HEAD
```

Over, či patch už existuje alebo či ho conflict resolution odstránila. Nepoužívaj `--skip` bez vysvetlenia.

### Cherry-pick aplikoval nesprávny rozsah

```bash
git reflog
git log --oneline <old-tip>..HEAD
git branch recovery/after-wrong-pick HEAD
```

Ak ešte nie je publikovaný, môžeš branch obnoviť na old tip a zopakovať explicitný zoznam commitov.

### Stash apply nič nezmenil

Možné príčiny:

- zmena už v target tree existuje,
- aplikoval sa iný `stash@{n}` po posune reflogu,
- stash obsahoval iba index alebo iba iné paths,
- clean/smudge filter zmenil working-tree reprezentáciu.

```bash
git rev-parse stash@{0}
git stash show -p stash@{0}
git cat-file -p stash@{0}
```

### Po pop nevidím stash entry

Ak apply uspel, `pop` ho odstránil. Skontroluj reflog/object candidates čo najskôr a zastav GC/deštruktívne cleanup operácie.

## 34. Časté omyly

### „Cherry-pick zachová rovnaký commit“

Nie. Vytvorí nový commit s novým parentom a ID.

### „Cherry-pick vytvorí merge ancestry“

Nie. Replayne patch bez spojenia branch graphov.

### „Commit bez konfliktu je bezpečný backport“

Nie. Môže chýbať dependency alebo byť nekompatibilný s release branch.

### „`-x` dokazuje identický patch“

Nie. Je to auditný odkaz v message.

### „Stash je obyčajný patch“

Nie. Typicky ide o viac commit-like objektov pre working tree, index a voliteľne untracked stav.

### „Stash zahŕňa všetky files“

Defaultne nie untracked ani ignored files.

### „Pop je bezpečnejší než apply“

Nie. Apply ponechá recovery entry, kým výsledok neoveríš.

### „Stash je remote backup“

Nie. Je lokálny a podlieha reflog/GC lifecycle.

## 35. Kontrolné otázky

1. Prečo cherry-picked commit dostane nové ID?
2. Prečo cherry-pick nevytvára ancestry integráciu?
3. Ako overíš dependency ordering série commitov?
4. Čo znamená `-m 1` pri cherry-picku merge commitu?
5. Kedy môže cherry-pick skončiť ako empty?
6. Načo slúži `-x` pri backporte?
7. Aké snapshots typicky reprezentuje stash?
8. Aký je rozdiel medzi `apply`, `pop` a `stash branch`?
9. Čo robia `--keep-index`, `--staged`, `-u` a `-a`?
10. Ako sa pokúsiš obnoviť dropnutý stash?

## Glossary impact

Relevantné pojmy: cherry-pick, patch replay, backport, mainline parent, sequencer, empty cherry-pick, patch identity, stash commit, stash reflog, keep-index, staged stash, stash apply, stash pop, stash branch, WIP commit.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Reset, revert a restore](reset-revert-restore.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Konflikty →](merge-conflicts.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
