# Working tree, staging area a repository

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Git and Automation Basics
- Predpoklady: [Git object model](git-object-model.md)
- Súvisiace témy: index, checkout, diff, ignored files, sparse checkout

## 1. Tri pracovné stavy

Bežná Git práca prebieha medzi tromi hlavnými stavmi:

```text
Working tree
   ↓ git add
Staging area / index
   ↓ git commit
Repository / object database
```

Working tree je aktuálny checkout súborov. Index je pripravovaný snapshot nasledujúceho commitu. Repository obsahuje objekty, refs a históriu.

## 2. Working tree

Working tree sú súbory, ktoré používateľ a nástroje priamo čítajú a menia.

Môžu byť:

- tracked a nezmenené,
- tracked a modified,
- staged,
- untracked,
- ignored.

```bash
git status --short
```

Typické dvojstĺpcové statusy:

```text
 M file.txt   zmenené iba vo working tree
M  file.txt   zmenené v indexe
MM file.txt   staged verzia aj ďalšia unstaged zmena
?? file.txt   untracked
```

## 3. Index nie je iba „zoznam súborov“

Index je binárna dátová štruktúra, ktorá drží pripravovaný tree snapshot vrátane:

- path,
- mode,
- object ID blobu,
- stat cache,
- conflict stages pri merge konflikte.

```bash
git ls-files --stage
```

Po `git add file.txt` Git vytvorí blob aktuálneho obsahu a index naň odkáže.

## 4. `git add`

```bash
git add file.txt
git add directory/
git add -A
git add -p
```

`git add -p` umožňuje stage iba vybrané hunks. Jeden working-tree súbor tak môže mať:

- časť zmien staged,
- časť zmien unstaged.

To podporuje malé logické commity.

## 5. Tri dôležité diffy

### Working tree vs. index

```bash
git diff
```

Ukazuje unstaged changes.

### Index vs. HEAD

```bash
git diff --staged
```

Ukazuje obsah budúceho commitu.

### Working tree vs. HEAD

```bash
git diff HEAD
```

Ukazuje všetky lokálne zmeny oproti poslednému commitu.

Pred commitom je autoritatívna kontrola:

```bash
git diff --staged
```

## 6. Commit používa index

`git commit` nevytvorí commit priamo z ľubovoľného working tree. Vytvorí tree podľa indexu.

Preto:

```bash
printf 'v1\n' > app.txt
git add app.txt
printf 'v2\n' > app.txt
git commit -m 'commit staged v1'
```

commit obsahuje `v1`, zatiaľ čo working tree zostáva na `v2` ako unstaged change.

## 7. Untracked a ignored files

Untracked file nie je v indexe ani v HEAD.

`.gitignore` určuje, ktoré untracked paths sa štandardne nezobrazujú a nepridávajú.

```gitignore
.env
build/
*.log
```

Dôležité: `.gitignore` neprestane sledovať súbor, ktorý už je tracked.

```bash
git rm --cached .env
```

Citlivý údaj však ostáva v histórii. Samotné odstránenie zo súčasného tree nie je history purge.

## 8. Ignore vrstvy

- repository `.gitignore`,
- directory-specific `.gitignore`,
- `.git/info/exclude`,
- globálny excludes file.

Diagnostika:

```bash
git check-ignore -v path/to/file
```

## 9. Checkout a restore

Checkout pracovného stromu zapisuje snapshot z commitu alebo indexu do filesystemu.

Moderné rozdelenie príkazov:

```bash
git switch branch
git restore file.txt
git restore --staged file.txt
```

- `switch` mení branch/HEAD,
- `restore` obnovuje working tree alebo index.

Starší `git checkout` vie robiť obe kategórie operácií, čo zvyšuje nejednoznačnosť.

## 10. File modes a line endings

Git typicky sleduje iba executable bit, nie kompletné permissions.

Line-ending transformácie môžu ovplyvňovať working tree:

```bash
git config core.autocrlf
git check-attr -a file.txt
```

`.gitattributes` môže definovať text normalization:

```gitattributes
* text=auto
*.sh text eol=lf
*.ps1 text eol=crlf
```

Bez konzistentnej policy môžu vzniknúť celé súbory označené ako zmenené iba pre CRLF/LF konverziu.

## 11. Clean a reset working tree

Untracked files:

```bash
git clean -n
git clean -fd
```

Najprv vždy dry-run `-n`. Ignored files vyžadujú ďalšie options a môžu obsahovať lokálne dáta.

Tracked changes:

```bash
git restore file.txt
git restore --source=HEAD --staged --worktree file.txt
```

Tieto operácie môžu zahodiť necommitnuté zmeny.

## 12. Conflict stages v indexe

Po konflikte môže index držať viac verzií jednej path:

```text
stage 1 merge base
stage 2 ours
stage 3 theirs
```

```bash
git ls-files -u
```

Po vyriešení konfliktu `git add path` nahradí conflict stages jednou resolved verziou.

## 13. Sparse checkout

Veľký repository môže checkoutnúť iba podmnožinu paths:

```bash
git sparse-checkout init --cone
git sparse-checkout set services/api docs
```

Object database môže stále obsahovať širšiu históriu; sparse checkout primárne mení working-tree materialization.

## 14. Submodules a gitlinks

Submodule path je v superproject tree uložená ako gitlink na konkrétny commit iného repository.

Working tree submodulu má vlastný Git stav.

```bash
git submodule status
git submodule update --init --recursive
```

Zmena obsahu v submodule a zmena gitlinku v parent repository sú dve oddelené operácie.

## 15. Praktický bezpečný commit workflow

```bash
git status --short
git diff
git add -p
git diff --staged
git commit -m 'fix: validate configuration input'
git status
```

Cieľom je presne vedieť, čo je:

- vo working tree,
- v indexe,
- v commite.

## 16. Troubleshooting

### Súbor sa nechce pridať

```bash
git check-ignore -v path
git status --untracked-files=all
git ls-files path
```

### Commit neobsahuje poslednú zmenu

Pravdepodobne bola zmena vykonaná po `git add`. Skontroluj:

```bash
git diff
git diff --staged
```

### Celý súbor je zmenený bez viditeľného dôvodu

Kontroluj line endings, encoding, formatter a file mode:

```bash
git diff --ignore-space-at-eol
git diff --summary
git check-attr -a file
```

## 17. Časté omyly

### „`git add` iba označí súbor“

Vytvorí blob aktuálneho obsahu a aktualizuje index.

### „Commit vezme všetko, čo vidím v editore“

Commituje index, nie automaticky celý working tree.

### „`.gitignore` odstráni secret z histórie“

Nie.

### „Untracked file je bezpečne zálohovaný Gitom“

Nie je v repository.

## 18. Kontrolné otázky

1. Aký je rozdiel medzi working tree, indexom a repository?
2. Čo ukazuje `git diff --staged`?
3. Prečo môže byť súbor zároveň staged aj modified?
4. Čo presne vykoná `git add`?
5. Prečo `.gitignore` neovplyvní tracked file?
6. Ako index reprezentuje merge conflict?
7. Aký problém rieši `.gitattributes`?
8. Prečo je `git clean` rizikový?

## Glossary impact

Relevantné pojmy: working tree, staging area, index, tracked, untracked, ignored file, partial staging, conflict stages, sparse checkout.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Git object model](git-object-model.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Commit, branch, tag a HEAD →](commit-branch-tag-head.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
