# Reset, revert a restore

<!-- CONCEPT-FIRST:START -->
## Čo menia reset, revert a restore

Tieto tri commands sa často zamieňajú, pretože všetky môžu „vrátiť zmenu“. V skutočnosti pracujú s odlišnými vrstvami.

**Restore** kopíruje obsah zo zvoleného source tree alebo indexu do working tree a voliteľne do indexu. Je určený najmä na obnovu pathov. Nehýbe branch refom a nevytvára commit.

**Reset** posúva aktuálnu branch alebo `HEAD` na iný commit a podľa mode môže zároveň prepísať index a working tree. Je to ref/index/worktree transformácia. Na unpublished lokálnej branch je veľmi užitočný; na zdieľanej histórii môže vytvoriť divergence a vyžadovať force push.

**Revert** nevpisuje starý stav priamo do minulosti. Vypočíta inverse change vybraného commit-u a vytvorí nový commit nad aktuálnou históriou. Zachováva audit trail a je preto bežnou voľbou pre už publikované commits.

Reset modes:

```text
--soft
posunie ref, index a working tree nechá

--mixed
posunie ref, index nastaví podľa targetu, working tree nechá

--hard
posunie ref, index aj working tree nastaví podľa targetu
```

Neutrálny príklad:

```text
C1---C2---C3  main
```

`git reset --hard C1` posunie lokálny `main` na `C1` a zhodí staged aj working changes, ktoré nie sú v `C1`. Commits C2 a C3 môžu dočasne zostať recoverable cez reflog, ale ref ich už nedrží.

`git revert C3` naopak vytvorí `C4`, ktorého patch ruší efekt C3:

```text
C1---C2---C3---C4
```

História zostáva append-only. Pri revertovaní merge commit-u treba určiť mainline parent, pretože Git musí vedieť, voči ktorej ancestry line má efekt merge-u obrátiť. Neskoršie opätovné mergovanie môže byť prekvapivé, pretože merge commit zostáva súčasťou ancestry.

Pred deštruktívnou operáciou je vhodné vytvoriť recovery ref a pozrieť `git status`, `git diff`, `git diff --cached` a `git reflog`. Recovery nie je argument pre bezhlavé používanie `--hard`; reflog má retention a untracked files nemusí chrániť.
<!-- CONCEPT-FIRST:END -->

## Atlas scenár a praktické použitie

Git ponúka viac operácií, ktoré sa v bežnej reči opisujú ako „vráť zmenu“. Menia však odlišné vrstvy. `restore` pracuje s working tree alebo indexom. `reset` posúva branch alebo HEAD a podľa mode môže meniť index a working tree. `revert` vytvára nový commit, ktorý aplikuje inverznú zmenu. Bez určenia vrstvy je príkaz nebezpečne nejednoznačný.

## Restore working tree alebo indexu

Ak Alice upravila file a chce zahodiť iba necommitnutú zmenu:

```bash
git restore config/orders.yaml
```

Git obnoví working-tree file podľa indexu. Ak bol file staged omylom:

```bash
git restore --staged config/orders.yaml
```

Index sa obnoví podľa HEAD, working-tree obsah zostane. Source možno zvoliť explicitne:

```bash
git restore --source=HEAD~1 -- config/orders.yaml
```

Tým sa do working tree vloží staršia verzia file-u. Neznamená to návrat branch na starší commit.

## Reset posúva ref a voliteľne ďalšie vrstvy

`git reset <target>` mení current branch tip alebo detached HEAD position. Mode určuje ďalší dopad.

```bash
git reset --soft HEAD~1
```

Branch sa posunie späť, index a working tree zostanú ako pred resetom. Posledný commit sa zmení na staged changes.

```bash
git reset --mixed HEAD~1
```

Default mixed reset posunie branch a obnoví index podľa targetu, working-tree edits ponechá ako unstaged.

```bash
git reset --hard HEAD~1
```

Hard reset posunie branch a prepíše index aj tracked working-tree files. Je deštruktívny pre necommitnutý obsah. Untracked files typicky nezmaže, ale kombinácia s clean môže odstrániť aj tie.

## Path reset neposúva branch

Historická syntax:

```bash
git reset HEAD -- config/orders.yaml
```

mení index entry pre path, neposúva branch. Moderný ekvivalent je čitateľnejší:

```bash
git restore --staged config/orders.yaml
```

To ukazuje, prečo sa reset nemá vysvetľovať jednou vetou. Jeho správanie závisí od targetu, mode a toho, či dostal paths.

## Revert zachováva publikovanú históriu

Ak chybný commit už existuje na shared `main`, bezpečná korekcia typicky používa:

```bash
git revert <bad-commit>
```

Vznikne nový commit s inverse patchom. Pôvodný commit zostáva v histórii a audit ukáže zavedenie aj odstránenie zmeny.

Revert merge commitu potrebuje mainline parent:

```bash
git revert -m 1 <merge-commit>
```

`-m 1` hovorí, ktorý parent reprezentuje hlavnú líniu, voči ktorej sa vypočíta inverzia. Nesprávny parent môže odstrániť nesprávnu časť integrácie.

## Revert nie je časový stroj

Ak neskoršie commits závisia od zlej zmeny, revert môže mať conflict alebo vytvoriť nefunkčný snapshot. Treba overiť final tree a business outcome. Opätovné merge-nutie pôvodnej branch po reverte môže byť prekvapivé, pretože Git považuje ancestry za už integrovanú. Často je potrebný revert reversion alebo nový opravný commit.

## Recovery cez reflog

Alice omylom vykoná:

```bash
git reset --hard HEAD~3
```

Ak commits neboli garbage-collected, reflog zachytí starý tip:

```bash
git reflog
git branch recovery/ord-8421 <old-sha>
```

Najprv sa vytvorí recovery branch, až potom sa rozhoduje o ďalšom reset-e. Reflog je lokálny a expirovateľný. Ak bol untracked alebo necommitnutý obsah prepísaný, Git ho nemusí vedieť obnoviť.

## ORIG_HEAD a safety refs

Niektoré operácie zapisujú predchádzajúci tip do `ORIG_HEAD`:

```bash
git show ORIG_HEAD
```

Je užitočný po merge, pull alebo reset-e, ale nie je garantovaným univerzálnym backupom. Ďalšia operácia ho môže prepísať. Pri riskantnej zmene je explicitná safety branch čitateľnejšia:

```bash
git branch backup/before-history-edit
```

## Incident: shared main bol hard-resetnutý a force-pushnutý

Operátor chce odstrániť chybný commit z produkčnej branch a vykoná hard reset plus force push. Tým odpojí nielen chybný commit, ale aj dva následné commits iných tímov. Ich clones a CI refs sa rozídu.

Containment zablokuje ďalšie pushes a z remote reflogu, hosting audit-u alebo clone-u obnoví pôvodný tip. Branch sa vráti cez protected ref procedure. Chybná zmena sa potom odstráni revert commitom. Root control je branch protection, zákaz force pushu a dokumentovaný incident recovery proces.

## Zhrnutie

`restore` mení working tree alebo index. `reset` presúva ref a podľa mode môže meniť index a working tree. `revert` vytvára nový history-preserving commit. Pre shared history je revert zvyčajne bezpečnejší; pre lokálnu nepublikovanú prácu môže byť reset vhodný. Pred každou operáciou treba pomenovať vrstvu a zachovať recovery ref.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Merge a rebase](merge-and-rebase.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Cherry-pick a stash →](cherry-pick-and-stash.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
