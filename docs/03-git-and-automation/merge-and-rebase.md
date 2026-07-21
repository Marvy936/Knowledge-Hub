# Merge a rebase

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Git and Automation Basics
- Predpoklady: [Commit, branch, tag a HEAD](commit-branch-tag-head.md), [Clone, fetch, pull a push](clone-fetch-pull-push.md)
- Súvisiace témy: merge base, three-way merge, history rewrite, conflict resolution

## 1. Dva integračné modely

Merge a rebase integrujú prácu z rozdielnych commit graph vetiev, ale vytvárajú odlišnú históriu.

```text
merge:  zachová pôvodné commits a vytvorí merge commit
rebase: znovu vytvorí commits nad novým base
```

## 2. Merge base

Git najprv určí spoločného predka:

```bash
git merge-base main feature
```

Three-way merge porovná:

```text
base
ours
 theirs
```

Výsledok závisí od zmien od base, nie iba od porovnania dvoch tipov.

## 3. Fast-forward merge

Ak current branch nemá vlastné nové commits:

```text
A---B  main
     \
      C---D  feature
```

`git merge feature` môže iba posunúť `main` na `D`.

```bash
git merge --ff-only feature
```

Nevznikne merge commit.

## 4. True merge

Pri divergence:

```text
      C---D  main
     /
A---B
     \
      E---F  feature
```

merge vytvorí commit `M` s dvoma parents:

```text
      C---D---M
     /       /
A---B       /
     \     /
      E---F
```

```bash
git merge --no-ff feature
```

Merge commit zachová integráciu ako explicitnú udalosť.

## 5. Rebase

```bash
git switch feature
git rebase main
```

Git nájde commits unikátne pre feature, aplikuje ich na nový base a vytvorí nové commits:

```text
pred:
A---B---C---D  main
     \
      E---F    feature

po:
A---B---C---D---E'---F'  feature
```

`E'` a `F'` majú nové IDs.

## 6. Rebase nie je presun existujúcich commitov

Rebase typicky:

1. určí merge base,
2. identifikuje patches unikátne pre branch,
3. resetne branch na nový base,
4. aplikuje zmeny po jednej,
5. vytvorí nové commit objects.

Preto signatures a commit IDs starých commitov neplatia pre nové objekty.

## 7. Kedy použiť merge

Merge je vhodný, keď:

- chceš zachovať skutočnú topology histórie,
- branch je zdieľaná,
- integrácia je významná udalosť,
- nechceš prepisovať publikované commits,
- release alebo audit model používa merge commits.

## 8. Kedy použiť rebase

Rebase je vhodný, keď:

- upratuješ vlastnú nepublikovanú branch,
- chceš lineárnu feature históriu,
- aktualizuješ feature branch na aktuálny main pred merge,
- tímová policy to explicitne podporuje.

Základné pravidlo:

```text
nerebasuj zdieľanú históriu bez dohody a koordinácie
```

## 9. Interactive rebase

```bash
git rebase -i HEAD~5
```

Operácie:

```text
pick     ponechať
reword   zmeniť message
edit     zastaviť a upraviť
squash   zlúčiť s predchádzajúcim commitom
fixup    zlúčiť bez zachovania message
drop     odstrániť commit
```

Interactive rebase je history rewrite. Všetky dotknuté commits a ich descendants dostanú nové IDs.

## 10. Rebase onto

```bash
git rebase --onto new-base old-base feature
```

Význam:

```text
vezmi commits reachable z feature, ktoré nie sú reachable z old-base,
a aplikuj ich na new-base
```

Je silný pri presune časti branch, ale nesprávne hranice môžu vynechať alebo duplikovať zmeny.

## 11. Conflicts počas merge a rebase

Merge konflikt vyriešiš raz pre výsledný merge.

Rebase môže konfliktovať pri každom replayovanom commite:

```bash
git status
# upraviť files
git add <paths>
git rebase --continue
```

Zrušenie:

```bash
git merge --abort
git rebase --abort
```

Pri rebase sa význam `ours` a `theirs` môže javiť opačne než používateľ očakáva, pretože current base a replayovaný commit majú inú rolu. Nespoliehaj sa iba na názvy; over obsah stages.

## 12. Merge strategies a options

Bežné options:

```bash
git merge --ff-only
git merge --no-ff
git merge --squash
git merge -Xours
```

`-Xours` preferuje ours iba pri konfliktných hunks. Nie je to isté ako stratégia `-s ours`, ktorá ignoruje obsah druhej vetvy a iba zaznamená ancestry merge.

## 13. Squash merge

```bash
git merge --squash feature
git commit
```

Výsledný commit nemá feature tip ako parent. Obsah sa integruje, ale commit graph nezaznamená skutočný merge relationship.

To ovplyvňuje:

- budúce merge-base správanie,
- audit commitov,
- spätné dohľadanie jednotlivých feature commitov,
- revert celej feature.

## 14. Rerere

Git môže zapamätať resolution konfliktov:

```bash
git config rerere.enabled true
```

`rerere` je užitočné pri opakovaných rebases alebo dlhodobých branches. Resolution treba stále reviewnúť, pretože rovnaký conflict shape nemusí mať rovnaký business význam.

## 15. Overenie výsledku

Po merge alebo rebase:

```bash
git status
git log --graph --oneline --decorate --all
git diff <old-tip>..<new-tip>
git range-diff <old-range> <new-range>
```

`git range-diff` je vhodný na porovnanie série commitov pred a po rebase.

## 16. Recovery

Pred operation si môžeš uložiť tip:

```bash
git branch backup/feature-before-rebase
```

Po chybe:

```bash
git reflog
git reset --hard <old-tip>
```

Recovery musí zohľadniť necommitnuté zmeny; hard reset ich môže zničiť.

## 17. Časté omyly

### „Rebase iba uprace graf bez zmeny commitov“

Vytvára nové commits.

### „Merge je vždy bezpečný a rebase vždy nebezpečný“

Riziko závisí od zdieľania histórie, review procesu a zvolených options.

### „Squash merge je to isté ako merge commit“

Nie. Nezachová merge ancestry.

### „`-Xours` zahodí celú druhú branch“

Nie. Preferuje ours iba pri konfliktoch.

## 18. Kontrolné otázky

1. Čo je merge base?
2. Kedy je merge fast-forward?
3. Prečo rebase mení commit IDs?
4. Kedy je vhodný merge commit?
5. Aký je rozdiel medzi squash merge a true merge?
6. Prečo môže rebase vyriešiť viac konfliktov postupne?
7. Čo robí `rebase --onto`?
8. Ako overíš ekvivalenciu série po rebase?

## Glossary impact

Relevantné pojmy: merge base, three-way merge, fast-forward merge, merge commit, rebase, interactive rebase, squash merge, history rewrite, rerere, range-diff.
