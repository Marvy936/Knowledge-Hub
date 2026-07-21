# Reset, revert a restore

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Git and Automation Basics
- Predpoklady: [Working tree, staging area a repository](working-tree-staging-repository.md), [Commit, branch, tag a HEAD](commit-branch-tag-head.md)
- Súvisiace témy: history rewrite, reflog, recovery, index, destructive operations

## 1. Rozdiel v jednej mape

```text
git restore  mení working tree a/alebo index
git reset    presúva current branch/HEAD a voliteľne mení index a working tree
git revert   vytvára nový commit, ktorý ruší efekt staršieho commitu
```

Tieto príkazy riešia odlišné vrstvy stavu.

## 2. Restore

Obnova working tree z indexu:

```bash
git restore file.txt
```

Unstage súboru bez zmeny working tree:

```bash
git restore --staged file.txt
```

Obnova z konkrétneho commitu:

```bash
git restore --source=HEAD~1 --worktree file.txt
```

Restore štandardne nemení branch ref ani históriu.

## 3. Reset modes

### Soft

```bash
git reset --soft <commit>
```

Presunie branch/HEAD, ale ponechá index aj working tree.

Použitie: prepracovanie posledných commitov bez straty staged snapshotu.

### Mixed

```bash
git reset --mixed <commit>
# alebo git reset <commit>
```

Presunie branch a nastaví index podľa target commitu. Working tree ponechá.

### Hard

```bash
git reset --hard <commit>
```

Presunie branch, index aj tracked working-tree files podľa target commitu.

Môže nenávratne zahodiť necommitnuté tracked zmeny.

## 4. Reset path vs. reset commit

```bash
git reset HEAD file.txt
```

Pri path form reset nepresúva branch. Mení index pre konkrétnu path. Moderný zrozumiteľnejší ekvivalent:

```bash
git restore --staged file.txt
```

## 5. Revert

```bash
git revert <commit>
```

Git vytvorí nový commit s inverznou zmenou.

```text
A---B---C---R
        ^   revert C
```

Pôvodný commit zostáva v histórii. Preto je revert vhodný pre publikovanú zdieľanú históriu.

## 6. Revert merge commitu

Merge commit má viac parents. Treba určiť mainline parent:

```bash
git revert -m 1 <merge-commit>
```

`-m 1` neznamená „revert prvý commit“. Znamená, že parent 1 sa považuje za hlavnú líniu.

Revert merge commitu ovplyvňuje budúce merges: Git si pamätá, že ancestry už bola integrovaná, aj keď obsah bol revertovaný.

## 7. Amend

```bash
git commit --amend
```

Amend vytvorí nový commit s rovnakým parentom, ale novým snapshotom alebo message. Je to history rewrite.

Publikovaný amend typicky vyžaduje force push a koordináciu.

## 8. Recovery cez reflog

Po nesprávnom reset:

```bash
git reflog
git branch recovery <old-head>
```

Reflog často drží starý tip. Necommitnuté zmeny zahodené hard resetom však nemusia byť obnoviteľné cez Git.

## 9. ORIG_HEAD

Niektoré riskantné operácie ukladajú predchádzajúci HEAD do `ORIG_HEAD`:

```bash
git show ORIG_HEAD
git reset --hard ORIG_HEAD
```

Nie je to univerzálna ani dlhodobá recovery evidencia. Reflog je širší nástroj.

## 10. Bezpečný rozhodovací strom

```text
Chcem zahodiť unstaged working-tree zmenu?
→ restore

Chcem unstage bez zmeny súboru?
→ restore --staged

Chcem presunúť lokálnu nepublikovanú branch?
→ reset

Chcem zrušiť publikovaný commit auditovateľne?
→ revert
```

## 11. Troubleshooting scenár

Posledné tri lokálne commits boli omyl, ale files chceš ponechať:

```bash
git branch backup/before-reset
git reset --mixed HEAD~3
git status
git diff
```

Publikovaný chybný commit:

```bash
git revert <commit>
git push
```

## 12. Časté omyly

### „Reset vždy zmaže files“

Závisí od mode.

### „Revert odstráni commit z histórie“

Nie. Pridá nový inverzný commit.

### „Hard reset vyčistí aj všetky untracked files“

Nie automaticky; na tie slúži `git clean`, ktorý je samostatne rizikový.

### „Amend iba upraví text existujúceho commitu“

Vytvorí nový commit object.

## 13. Kontrolné otázky

1. Ktoré stavy mení soft, mixed a hard reset?
2. Prečo je revert vhodný pre shared branch?
3. Aký je rozdiel medzi path reset a commit reset?
4. Čo znamená `revert -m 1`?
5. Ako reflog pomáha po chybnom reset?
6. Prečo amend mení commit ID?

## Glossary impact

Relevantné pojmy: reset, soft reset, mixed reset, hard reset, restore, revert, mainline parent, amend, ORIG_HEAD.
