# Working tree, staging area a repository

Developer zmení tri files: konfiguračný limit, schema a lokálny debug log. Do commitu patria iba prvé dva. Git preto oddeľuje working tree od indexu a object database. Working tree je editovateľný filesystem view. Index je pripravovaný snapshot ďalšieho commitu. Repository obsahuje immutable objekty a refs.

## Tri porovnania, nie jeden „diff“

`git status` syntetizuje viac stavov. Presnejšie otázky sú:

```bash
git diff                 # working tree oproti indexu
git diff --cached        # index oproti HEAD
git diff HEAD            # working tree oproti HEAD
git ls-files --stage     # presný obsah indexu
```

Ak `orders.yaml` je staged a potom ho developer znovu upraví, existujú tri verzie: HEAD, staged verzia a novšia working-tree verzia. `git commit` uloží index, nie automaticky posledný obsah na disku.

## Staging je zostavenie snapshotu

```bash
git add config/orders.yaml schemas/orders.schema.json
git diff --cached
```

`git add` nevkladá „súbor do fronty“. Aktualizuje index entry na blob vytvorený z aktuálneho obsahu. Ďalšia editácia working tree index nemení, kým sa nevykoná ďalší add.

Partial staging umožní vybrať iba časť jedného file-u:

```bash
git add -p config/orders.yaml
```

To je užitočné, keď file obsahuje funkčnú zmenu aj nesúvisiace formátovanie. Hunk selection však môže vytvoriť staged snapshot, ktorý na disku nikdy ako celok neexistoval. Pred commitom preto treba testovať staged subject, nie slepo working tree.

```bash
git diff --cached --check
git show :config/orders.yaml
```

Colon syntax číta file priamo z indexu.

## Untracked, ignored a tracked

Untracked file nie je v indexe ani HEAD. `.gitignore` zabráni bežnému pridaniu matching untracked files, ale neprestane sledovať už tracked file.

```bash
git status --short
git check-ignore -v logs/debug.log
```

Secrets nemajú byť „chránené“ iba `.gitignore`. Ak sa secret dostal do commitu, odstránenie z working tree alebo pridanie ignore rule nemení históriu. Credential treba revoke-nuť a podľa threat modelu vyčistiť history.

## Restore indexu a working tree

Ak bol file omylom staged:

```bash
git restore --staged config/orders.yaml
```

Tým sa index entry vráti podľa HEAD, working-tree editácia zostane. Ak sa má zahodiť working-tree zmena:

```bash
git restore config/orders.yaml
```

Druhá operácia je deštruktívna pre necommitnutý obsah. Pred ňou treba pozrieť diff alebo vytvoriť bezpečný patch.

## Index pri conflicte

Pri merge conflicte index neobsahuje jeden entry, ale stages:

```text
stage 1: merge base
stage 2: ours
stage 3: theirs
```

```bash
git ls-files -u
```

Working tree obsahuje conflict markers pre textový file, ale authoritative conflict inputs sú index stages. Po resolution `git add` nahradí tri unmerged entries jedným resolved blobom.

## Sparse a skip-worktree hranice

Veľké repositories môžu používať sparse checkout. Nie všetky tracked files musia byť materializované vo working tree. Index stále reprezentuje širší snapshot. `skip-worktree` nie je mechanizmus na lokálne tajné úpravy tracked configu; takýto pattern vedie k prekvapivým merge a deploy výsledkom.

```bash
git sparse-checkout list
git ls-files -v | head
```

## Incident: commit neobsahuje poslednú opravu

Alice stagedne `maxOrderAmount: 5000`, potom ho opraví na `5500` a spustí testy nad working tree. Testy prejdú, ale commit uloží staged hodnotu 5000. Review vidí starú hodnotu a pipeline zlyhá.

Root cause nie je Git cache. Testovaný subject a commitovaný subject boli odlišné. Prevencia používa `git diff --cached`, clean-tree gate alebo test nad exportovaným index snapshotom. Pred commitom sa explicitne overí:

```bash
git diff --cached
git diff
git status --short
```

## Zhrnutie

Working tree je editovateľný view, index je pripravovaný snapshot a repository drží immutable objects a refs. `git add` aktualizuje index, `git commit` zapisuje index a restore operácie menia presne zvolenú vrstvu. Bez tejto hranice sú partial staging, conflicts aj recovery nepredvídateľné.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Git object model](git-object-model.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Commit, branch, tag a HEAD →](commit-branch-tag-head.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
