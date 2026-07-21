# Cherry-pick a stash

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Git and Automation Basics
- Predpoklady: [Commit, branch, tag a HEAD](commit-branch-tag-head.md), [Merge a rebase](merge-and-rebase.md)
- Súvisiace témy: patch replay, duplicate changes, temporary work, recovery

## 1. Cherry-pick

`git cherry-pick` aplikuje zmenu reprezentovanú vybraným commitom na aktuálny tip a vytvorí nový commit.

```bash
git cherry-pick <commit>
```

Výsledný commit má:

- nový parent,
- nový object ID,
- typicky rovnaký patch intent,
- často zachovaného autora,
- nového committera a čas.

## 2. Cherry-pick nie je presun commitu

```text
source: A---B---C

target: X---Y
              \
               C'
```

`C'` nie je ten istý commit ako `C`. Git nevytvorí ancestry link medzi source branch a target branch.

## 3. Typické použitia

- backport opravy do release branch,
- prenesenie jedného izolovaného commitu,
- obnova commitu z detached alebo zmazanej branch,
- dočasný výber z väčšej série pred reorganizáciou.

Nie je vhodný ako náhrada systematickej integrácie celých dlhodobých branches.

## 4. Rozsah commitov

```bash
git cherry-pick A B C
git cherry-pick A..C
git cherry-pick A^..C
```

`A..C` typicky nezahŕňa `A`. Revision range treba vždy overiť:

```bash
git log --oneline A..C
```

## 5. `-x` pre backport audit

```bash
git cherry-pick -x <commit>
```

Pridá do message odkaz na pôvodný commit ID. Je vhodný pre public backports, pretože zjednodušuje dohľadateľnosť.

## 6. No-commit mode

```bash
git cherry-pick -n <commit>
```

Aplikuje zmenu do indexu a working tree bez okamžitého commitu. Umožní skombinovať viac zmien, ale stráca sa one-to-one audit, ak sa použije bez jasného dôvodu.

## 7. Cherry-pick merge commitu

Merge commit má viac parents, preto treba mainline:

```bash
git cherry-pick -m 1 <merge-commit>
```

Výsledok reprezentuje rozdiel merge commitu voči zvolenému parentu. Nesprávna mainline môže aplikovať neočakávaný obsah.

## 8. Konflikt a pokračovanie

```bash
git status
# vyriešiť files
git add <paths>
git cherry-pick --continue
```

Zrušenie:

```bash
git cherry-pick --abort
```

Preskočenie aktuálneho commitu:

```bash
git cherry-pick --skip
```

Skip môže potichu vynechať potrebnú zmenu; používaj ho iba po overení, že patch je už obsiahnutý alebo nepotrebný.

## 9. Duplicate patch problém

Ak cherry-pickneš commit a neskôr merge-neš pôvodnú branch, Git vidí rozdielne commit IDs. Three-way merge často rozpozná výsledný obsah, ale môžu vzniknúť konflikty alebo duplicitné semantic changes.

Na porovnanie patch identity:

```bash
git cherry -v target source
git log --cherry-pick --left-right target...source
```

## 10. Stash

Stash uloží pracovný stav do Git objektov a refu `refs/stash`, potom typicky obnoví čistejší working tree.

```bash
git stash push -m 'wip: api timeout'
git stash list
git stash show -p stash@{0}
```

Stash nie je externý backup. Je lokálny a podlieha reachability/reflog lifecycle.

## 11. Čo stash obsahuje

Defaultne tracked staged a unstaged changes. Untracked files vyžadujú:

```bash
git stash push -u
```

Ignored files:

```bash
git stash push -a
```

`-a` môže zachytiť veľké build outputs alebo lokálne dáta; treba vedieť, čo sa ukladá.

## 12. Apply vs. pop

```bash
git stash apply stash@{0}
git stash pop stash@{0}
```

- `apply` ponechá stash entry,
- `pop` sa pokúsi apply a následne entry odstrániť pri úspechu.

Pri dôležitej práci je bezpečnejšie najprv `apply`, overiť výsledok a až potom `drop`.

## 13. Stash branch

```bash
git stash branch recovery/stashed-work stash@{0}
```

Vytvorí branch z pôvodného base commitu stashu a aplikuje zmenu. Znižuje konflikty, ak sa aktuálna branch medzičasom výrazne posunula.

## 14. Partial stash

```bash
git stash push -p
git stash push --keep-index
git stash push --staged
```

Umožňuje oddeliť pripravenú zmenu od rozpracovanej. Pred použitím treba skontrolovať index a working tree, aby sa nesprávna časť práce nestratila z aktuálneho kontextu.

## 15. Stash internals

Stash je typicky séria commit-like objektov reprezentujúcich working tree, index a prípadne untracked files.

```bash
git log --graph --oneline --all --reflog
git cat-file -p stash@{0}
```

Pre používateľa je dôležité, že stash je verzovaný Git stav, ale nie zdieľaná branch s jasným názvom a review workflow.

## 16. Kedy radšej commit než stash

Preferuj dočasnú branch a WIP commit, keď:

- práca je významná,
- potrebuje backup cez remote,
- chceš ju zdieľať,
- stashov je veľa,
- potrebuješ audit a CI.

```bash
git switch -c wip/api-timeout
git add -A
git commit -m 'wip: investigate timeout handling'
```

WIP commit sa dá neskôr upratať interactive rebase.

## 17. Troubleshooting

### Stash apply konfliktuje

```bash
git status
git stash show -p stash@{0}
```

Vyrieš conflict ako bežný merge conflict. Stash entry pri `apply` zostáva dostupný.

### Stash bol omylom dropnutý

Skús:

```bash
git fsck --unreachable --no-reflogs
git reflog show stash
```

Recovery nie je garantovaný. Dôležitú prácu neuchovávaj dlhodobo iba v stash.

## 18. Časté omyly

### „Cherry-pick zachová ten istý commit“

Vytvorí nový commit s novým parentom.

### „Cherry-pick vytvorí merge relationship“

Nevytvorí.

### „Stash je bezpečný cloud backup“

Je lokálny Git stav.

### „Pop je vždy lepší než apply“

Apply je bezpečnejší, keď chceš najprv overiť výsledok.

## 19. Kontrolné otázky

1. Prečo má cherry-picked commit nové ID?
2. Načo slúži `cherry-pick -x`?
3. Aké riziko vzniká pri neskoršom merge source branch?
4. Čo defaultný stash nezahŕňa?
5. Aký je rozdiel medzi apply a pop?
6. Kedy je vhodnejší WIP commit na dočasnej branch?
7. Ako `stash branch` znižuje konflikty?

## Glossary impact

Relevantné pojmy: cherry-pick, backport, mainline parent, patch identity, stash, stash apply, stash pop, WIP commit.
