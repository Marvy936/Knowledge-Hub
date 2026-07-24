# Working tree, staging area a repository

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Git and Automation Basics
- Predpoklady: [Git object model](git-object-model.md)
- Súvisiace témy: index, checkout, diff, ignored files, sparse checkout

## 1. Definícia

Bežná Git práca prebieha medzi tromi odlišnými stavmi:

```text
HEAD / repository snapshot
        ↕
      index
        ↕
   working tree
```

- **Working tree** — materializované súbory, ktoré číta a mení používateľ, editor, compiler alebo testy.
- **Index / staging area** — binárny pripravovaný snapshot ďalšieho commitu.
- **Repository** — object database, refs, reflogs a história; `HEAD` typicky označuje aktuálny commit.

Príkazy Git často nekopírujú „súbor“ jedným smerom, ale menia konkrétnu hranicu medzi týmito stavmi. Bez tejto mapy sa `add`, `restore`, `reset`, `checkout` a `commit` javia ako nesúvisiace alebo nebezpečne magické operácie.

## 2. Základný state model

Najjednoduchší tok je:

```text
edit vo filesysteme
  ↓ git add
index entry ukazuje na nový blob
  ↓ git commit
nový tree + commit podľa indexu
```

Opačný smer môže byť:

```text
HEAD tree
  ↓ git restore --staged
index
  ↓ git restore
working tree
```

Dôležité je, že každá vrstva môže obsahovať inú verziu rovnakej path:

```text
HEAD:         app.conf = v1
index:        app.conf = v2
working tree: app.conf = v3
```

Vtedy je súbor súčasne staged aj modified.

## 3. Working tree

Working tree je filesystem view konkrétneho checkoutu. Obsahuje:

- tracked paths materializované z indexu alebo commitu,
- lokálne zmenené tracked paths,
- untracked files,
- ignored files,
- build outputs, caches a ďalší lokálny stav,
- prípadne iba časť repozitára pri sparse checkout.

Working tree nie je celý repository. `.git` alebo samostatný git directory drží metadata a object database.

```bash
git rev-parse --show-toplevel
git rev-parse --git-dir
git rev-parse --is-inside-work-tree
```

Bare repository nemá bežný working tree:

```bash
git rev-parse --is-bare-repository
```

## 4. Tracked, untracked a ignored nie sú tri verzie toho istého

Path môže byť:

- **Tracked** — existuje v indexe; Git ju porovnáva s working tree a `HEAD`.
- **Untracked** — existuje vo filesysteme, ale nie v indexe.
- **Ignored** — untracked path, ktorú ignore policy štandardne skryje pred bežným `status` a `add`.

Tracked path môže byť zároveň modified alebo staged. „Ignored“ neznamená, že Git z histórie odstránil už sledovaný súbor.

```bash
git ls-files --error-unmatch path
git status --short --untracked-files=all
git check-ignore -v path
```

## 5. Index je pripravovaný tree, nie zoznam checkboxov

Index je binárny súbor, typicky `.git/index`, ktorý obsahuje entries pre paths pripravovaného snapshotu.

Entry typicky drží:

- path,
- object ID blobu alebo gitlinku,
- Git file mode,
- stage number,
- stat cache fields,
- flags ako `assume-unchanged`, `skip-worktree` alebo intent-to-add.

```bash
git ls-files --stage
git ls-files --debug
git ls-files -v
```

Index reprezentuje flat path map. Tree objects sa z neho zostavia pri `write-tree` alebo `commit`.

```bash
git write-tree
```

## 6. `git add` ako content capture

`git add` typicky:

1. načíta working-tree content,
2. aplikuje clean filters a line-ending normalization podľa attributes,
3. vytvorí alebo znovu použije blob object,
4. aktualizuje index entry na nový object ID a mode.

```bash
git add file.txt
git ls-files --stage file.txt
git rev-parse :file.txt
```

Preto `git add` nie je iba „označenie súboru“. Zachytí konkrétnu verziu bytes do object database a indexu.

Ak sa súbor po `git add` znovu zmení, staged blob sa automaticky neaktualizuje.

## 7. Rozsah `git add`

Časté varianty:

```bash
git add file.txt
git add directory/
git add -u
git add -A
git add .
```

- **Explicit path** — aktualizuje zadanú path.
- **`-u`** — aktualizuje modifications a deletions už tracked paths, ale nepridá nové untracked paths.
- **`-A`** — zohľadní additions, modifications aj deletions v zadanom rozsahu.
- **`.`** — pathspec od aktuálneho directory; význam rozsahu závisí od pozície v strome.

Pred širokým add je vhodné overiť:

```bash
git status --short
git diff --stat
```

## 8. Tri základné diff hranice

### Working tree verzus index

```bash
git diff
```

Ukazuje unstaged changes: čo je vo working tree iné než staged snapshot.

### Index verzus `HEAD`

```bash
git diff --staged
git diff --cached
```

Ukazuje presný obsah pripravovaného commitu oproti aktuálnemu `HEAD`.

### Working tree verzus `HEAD`

```bash
git diff HEAD
```

Ukazuje kombináciu staged aj unstaged tracked zmien.

Mental model:

```text
git diff           working tree ↔ index
git diff --staged  index        ↔ HEAD
git diff HEAD      working tree ↔ HEAD
```

## 9. Status ako dvojrozmerný výsledok

Short status má typicky dva stĺpce:

```text
XY path
```

- `X` — index verzus `HEAD`.
- `Y` — working tree verzus index.

Príklady:

```text
 M file.txt   working tree modified, index nezmenený
M  file.txt   staged modification
MM file.txt   staged verzia + ďalšia unstaged zmena
A  file.txt   staged nový súbor
D  file.txt   staged deletion
?? file.txt   untracked
!! file.txt   ignored pri --ignored
```

```bash
git status --short
git status --porcelain=v2
```

Porcelain format je stabilnejší pre automatizáciu než human-readable text.

## 10. Commit používa index

Bežný `git commit` zostaví tree z indexu, nie priamo z aktuálneho working tree.

```bash
printf 'v1\n' > app.txt
git add app.txt
printf 'v2\n' > app.txt
git commit -m 'commit staged v1'
```

Výsledok:

```text
commit:       v1
index:        v1
working tree: v2
```

Overenie:

```bash
git show HEAD:app.txt
cat app.txt
git diff
```

Výnimky ako `git commit -a` majú vlastnú staging logiku pre tracked files, no stále netreba predpokladať, že commit berie všetko viditeľné v editore.

## 11. Partial staging

`git add -p` umožňuje rozhodovať po hunkoch:

```bash
git add -p
git diff
git diff --staged
```

Jeden súbor môže obsahovať dve logické zmeny, z ktorých iba jedna patrí do commitu.

Bezpečný workflow:

1. rozdeľ veľké hunks cez `s`,
2. prípadne manuálne edituj patch cez `e`,
3. over `git diff --staged`,
4. spusti test relevantný pre staged kombináciu.

Riziko: staged snapshot nemusí byť rovnaký ako aktuálny working tree, na ktorom test práve prebehol. Pri kritickom commite možno staged tree otestovať cez dočasný worktree alebo stash unstaged časti.

## 12. Interaktívny restore a reset hunks

Staged hunks možno odstrániť z indexu bez zmeny working tree:

```bash
git restore --staged -p
git reset -p
```

Unstaged hunks možno zahodiť z working tree:

```bash
git restore -p
```

Tieto dve operácie majú odlišný rizikový profil:

```text
restore --staged   zmení index, working bytes zostanú
restore            zmení working bytes, môže zahodiť prácu
```

Pred working-tree restore si pozri patch a zváž stash alebo externú kópiu.

## 13. Intent-to-add

`git add -N` alebo `--intent-to-add` vytvorí index entry signalizujúcu, že path má byť pridaná, ale ešte nestageuje jej plný content ako bežné `git add`.

```bash
git add -N new-file.txt
git status --short
git diff -- new-file.txt
```

Použitie:

- zahrnúť nový súbor do diff review,
- partial staging nového súboru cez `git add -p`,
- pripraviť path bez okamžitého plného stage.

Intent-to-add nie je commit-ready blob s očakávaným obsahom. Pred commitom treba index overiť.

## 14. Deletions a renames

Ak tracked file zmizne z working tree:

```bash
rm old.txt
git status --short
git add -u
```

Index potom zaznamená, že path v ďalšom tree nebude.

`git mv` je convenience kombinácia filesystem move a index update:

```bash
git mv old.txt new.txt
```

Git však neuchováva rename ako objektový event. Diff následne podobnosťou vyhodnotí delete/add ako rename.

```bash
git diff --staged --find-renames
```

## 15. Ignore policy a jej vrstvy

Ignore rozhodovanie môže pochádzať z:

- `.gitignore` v root alebo podadresároch,
- `.git/info/exclude`,
- global excludes file z `core.excludesFile`,
- command-specific exclude patterns.

```bash
git check-ignore -v path/to/file
git config --get core.excludesFile
```

Rule precedence závisí od source a poradia patternov. Negation pattern `!` môže znovu zahrnúť path, ale parent directory musí byť traversable; ignorovanie celého parent directory môže zabrániť opätovnému zahrnutiu child path bez vhodnejších patterns.

## 16. Tracked secret a `.gitignore`

Keď je secret už tracked, pridanie patternu do `.gitignore` nezmení index.

```bash
git rm --cached .env
printf '.env\n' >> .gitignore
git add .gitignore
git commit
```

Tým sa secret odstráni iba z budúcich trees. Stále môže existovať:

- v predchádzajúcich commit objects,
- v remote clones,
- v pull request diffs,
- v CI logs alebo artifacts,
- v caches a backups.

Správna reakcia zahŕňa okamžitú rotáciu credentialu. History rewrite je samostatný koordinovaný incidentný krok, nie náhrada rotácie.

## 17. Index stat cache

Git index obsahuje stat metadata, ktoré pomáhajú rýchlo rozhodnúť, či treba working file znovu čítať a hashovať.

Kontrolujú sa napríklad:

- size,
- timestamps,
- inode/device metadata podľa platformy,
- mode.

```bash
git ls-files --debug path
git update-index --refresh
git status
```

Stat cache je optimalizácia, nie zdroj pravdy pre obsah. Pri podozrivom filesysteme, clock granularity alebo tooling edge case môže Git vykonať detailnejšiu kontrolu.

`git update-index --really-refresh` môže pomôcť obnoviť stat informácie, no nemá slúžiť na maskovanie reálnych zmien.

## 18. `assume-unchanged`

Flag `assume-unchanged` je výkonový hint: používateľ tvrdí, že working path sa nebude meniť, aby Git obmedzil kontroly.

```bash
git update-index --assume-unchanged config.local
git ls-files -v config.local
git update-index --no-assume-unchanged config.local
```

Nie je to bezpečný mechanizmus na lokálnu konfiguráciu ani ignore tracked file. Operácie ako checkout alebo merge môžu stále potrebovať path zmeniť a flag sa môže stať zdrojom skrytých rozdielov.

## 19. `skip-worktree`

`skip-worktree` primárne podporuje sparse-checkout semantics: working tree nemusí materializovať path, hoci index ju pozná.

```bash
git ls-files -v
git update-index --skip-worktree path
git update-index --no-skip-worktree path
```

Ani tento flag nie je všeobecný „lokálne ignoruj tracked config“ nástroj. Git môže flag prehodnotiť, keď path v working tree existuje alebo ju potrebuje aktualizovať.

Rozdiel:

```text
assume-unchanged  optimalizačný predpoklad o nezmenenom súbore
skip-worktree     očakávanie, že path nemusí byť vo working tree
```

## 20. Conflict stages v indexe

Normálna resolved path má stage `0`. Pri konflikte môže index držať tri entries:

```text
stage 1  merge base
stage 2  ours
stage 3  theirs
```

```bash
git ls-files -u
git show :1:path
git show :2:path
git show :3:path
```

Po manuálnom vyriešení:

```bash
git add path
git ls-files --stage path
```

`git add` nahradí conflict stages jednou stage-0 entry pre resolved content. Conflict markers vo working file nie sú autoritatívny conflict state; index stages sú.

## 21. Checkout a materializácia

Checkout alebo switch musí zosúladiť:

- `HEAD`,
- target branch ref,
- index,
- working tree.

```bash
git switch feature
git switch --detach <commit>
```

Git odmietne checkout, ak by prepísal lokálne zmeny, ktoré nevie bezpečne zachovať. To nie je náhodná prekážka, ale data-loss ochrana.

Pred switchom:

```bash
git status --short
git diff
git diff --staged
```

Možnosti sú commit, stash, samostatný worktree alebo vedomé zahodenie zmien.

## 22. `git restore` zdroj a cieľ

`git restore` má explicitný source a destination model.

Working tree z indexu:

```bash
git restore path
```

Index z `HEAD`:

```bash
git restore --staged path
```

Index aj working tree z konkrétneho commitu:

```bash
git restore --source=<commit> --staged --worktree path
```

Predvolený source sa líši podľa toho, či sa mení index. Preto je bezpečnejšie pri rizikových operáciách source uviesť explicitne.

## 23. `git checkout -- path` ako historická syntax

Starší príkaz:

```bash
git checkout -- path
```

obnovuje working tree podľa indexu. Iná forma `git checkout branch` mení `HEAD`, index aj working tree.

Táto dvojitá funkcia je dôvodom, prečo moderný Git rozdelil intent na:

```text
git switch   branch/HEAD operácie
git restore  path/index/working-tree operácie
```

Pri dokumentácii a automatizácii je explicitné rozdelenie menej náchylné na chyby.

## 24. File modes

Git typicky sleduje:

- regular non-executable `100644`,
- regular executable `100755`,
- symlink `120000`,
- gitlink `160000`.

```bash
git diff --summary
git ls-files --stage script.sh
git update-index --chmod=+x script.sh
```

Nesleduje celý POSIX mode, ACL, ownera ani group. Deploy permissions musia byť riadené packagingom, image buildom, configuration managementom alebo installation procesom.

Na filesystémoch, ktoré executable bit nesprostredkujú spoľahlivo, môže `core.fileMode` ovplyvniť detekciu working-tree zmien.

## 25. Line endings a clean/smudge pipeline

Bytes vo working tree nemusia byť identické s blob bytes. Attributes a configuration môžu pri add/checkout aplikovať transformácie.

Príklad:

```gitattributes
* text=auto
*.sh text eol=lf
*.ps1 text eol=crlf
```

Kontrola:

```bash
git check-attr -a -- path
git ls-files --eol path
git config --show-origin --get core.autocrlf
```

Model:

```text
working tree
  ↓ clean filter / EOL normalization pri add
canonical blob
  ↓ smudge filter / EOL materialization pri checkout
working tree
```

Nekonzistentná policy môže spôsobiť full-file diffs, build chyby alebo script execution problémy.

## 26. Custom filters

`.gitattributes` môže definovať custom clean/smudge filter:

```gitattributes
*.secret filter=decrypt
```

Taký filter je executable dependency pracovného prostredia. Riziká:

- checkout bez filtra vytvorí nečakaný content,
- filter môže zlyhať alebo byť nedeterministický,
- secret handling môže uniknúť do process listu/logov,
- repository nemusí byť reprodukovateľné bez external tooling.

Filter má mať jasný contract, failure behavior a onboarding dokumentáciu.

## 27. Sparse checkout

Sparse checkout obmedzuje, ktoré tracked paths sa materializujú vo working tree.

```bash
git sparse-checkout init --cone
git sparse-checkout set services/api docs
git sparse-checkout list
```

Index a object database môžu stále reprezentovať širší repository. Sparse checkout mení working-tree view, nie nevyhnutne históriu dostupnú lokálne.

Dôležité rozlíšenia:

- **Sparse checkout** — obmedzí paths vo working tree.
- **Shallow clone** — obmedzí commit ancestry.
- **Partial clone** — môže odložiť stiahnutie niektorých objects.

Tieto mechanizmy možno kombinovať, no diagnostika musí vedieť, ktorá vrstva je neúplná.

## 28. Sparse index

Pri veľmi veľkom monorepe môže sparse index reprezentovať celé necheckoutnuté directory jednou tree entry namiesto jednotlivých files.

```bash
git sparse-checkout init --cone --sparse-index
git ls-files --sparse
```

Sparse index je optimalizácia. Nie všetky staršie nástroje alebo Git verzie musia byť kompatibilné s každou operáciou. Pri probléme možno index expandovať:

```bash
git sparse-checkout reapply --no-sparse-index
```

## 29. Multiple worktrees

`git worktree` umožňuje viac pracovných stromov zdieľajúcich jednu object database:

```bash
git worktree add ../repo-feature feature
git worktree list
```

Každý worktree má vlastný:

- `HEAD`,
- index,
- working tree,
- časť worktree-specific metadata.

Zdieľa objects a väčšinu refs. Rovnaká local branch nemôže byť bežne checkoutnutá vo viacerých worktrees súčasne, pretože dva pracovné stromy by nekontrolovane posúvali rovnaký ref.

Worktree je vhodný na test staged snapshotu, paralelnú opravu alebo release branch bez stashovania aktuálnej práce.

## 30. Submodules a gitlinks

Superproject tree neukladá celý obsah submodulu. Path s mode `160000` ukazuje na konkrétny commit iného repository.

```bash
git ls-tree HEAD path/to/submodule
git submodule status
git -C path/to/submodule status
```

Existujú dva oddelené stavy:

```text
submodule repository working state
superproject index gitlink target
```

Commit v submodule automaticky neaktualizuje parent repository. Treba stageovať nový gitlink:

```bash
git add path/to/submodule
```

Dirty submodule môže znamenať odlišný checkout commit alebo lokálne zmeny vo vnútri submodule.

## 31. Nested repositories a embedded `.git`

Ak `git add` objaví iný repository v podadresári bez správnej submodule konfigurácie, môže vytvoriť gitlink alebo varovanie o embedded repository.

Pred pridaním vendor alebo generated source treba rozhodnúť:

- normálne tracked files,
- submodule,
- subtree/import,
- package dependency,
- ignored external checkout.

Náhodné vnorenie `.git` môže spôsobiť, že parent repository necommitne očakávaný obsah.

## 32. Untracked cleanup

`git clean` odstraňuje untracked paths, nie tracked modifications.

Dry-run:

```bash
git clean -n
git clean -nd
git clean -ndX
git clean -ndx
```

Apply:

```bash
git clean -fd
```

Rozdiely:

- `-d` — zahrnie untracked directories.
- `-X` — iba ignored paths.
- `-x` — aj ignored paths.

Ignored directories môžu obsahovať lokálne databases, credentials, package caches alebo test data. `git clean -fdx` je deštruktívna operácia bez Git recovery, pretože tieto files nikdy neboli objects.

## 33. Obnova tracked working changes

Pred zahodením:

```bash
git diff -- path
git diff --staged -- path
```

Zahodenie unstaged working changes:

```bash
git restore path
```

Obnova working tree aj indexu z `HEAD`:

```bash
git restore --source=HEAD --staged --worktree path
```

Ak zmeny neboli staged, committed, stashed ani zachytené editorom/filesystem snapshotom, Git ich typicky nevie obnoviť.

## 34. Index corruption a rebuild

Pri poškodenom indexe môže working tree a object database zostať v poriadku.

Symptómy:

```text
index file corrupt
index uses unsupported extension
fatal: .git/index: index file smaller than expected
```

Bezpečný postup:

1. vytvor kópiu `.git/index`,
2. zachovaj working tree,
3. over `HEAD` a object integrity,
4. rebuild index z `HEAD`,
5. znovu stageuj zamýšľané changes.

Konceptuálne:

```bash
mv .git/index .git/index.backup
git reset --mixed HEAD
git status
```

`reset --mixed` obnoví index podľa `HEAD`, working tree ponechá. Pôvodné partial staging a conflict stages sa však stratia; preto je backup indexu dôležitý.

## 35. Racy Git a timestamp hranice

Ak sa súbor zmení tak rýchlo, že stat metadata vyzerajú nezmenene v granularite filesystem timestampu, Git môže potrebovať content overenie. Git má ochrany proti tzv. racy-clean situáciám, no veľmi netypické filesystems, clock správanie alebo external tooling môžu diagnostiku komplikovať.

Pri podozrení:

```bash
git update-index --really-refresh
git diff-files --raw
git hash-object path
```

Riešením nemá byť plošné používanie `assume-unchanged`, ktoré problém iba skryje.

## 36. Bezpečný commit workflow

Odporúčaný tok:

```bash
git status --short
git diff
git add -p
git diff --staged
git diff --check
# spusti relevantné testy
git commit -m 'fix: validate configuration input'
git status
```

Pre obzvlášť citlivý commit:

- over staged tree bez unstaged zmien,
- skontroluj secrets a generated files,
- over file modes a line endings,
- skontroluj submodule gitlinks,
- porovnaj commit po vytvorení:

```bash
git show --stat --oneline HEAD
git show --check HEAD
```

## 37. Diagnostický postup: commit neobsahuje očakávanú zmenu

1. Over working tree verzus index:

```bash
git diff -- path
```

2. Over index verzus `HEAD`:

```bash
git diff --staged -- path
```

3. Over blob v indexe:

```bash
git show :path
git rev-parse :path
```

4. Over commit content:

```bash
git show HEAD:path
```

5. Skontroluj filters/attributes:

```bash
git check-attr -a -- path
git ls-files --eol path
```

Najčastejšie bola zmena vykonaná po poslednom `git add` alebo bola stageovaná iba časť hunku.

## 38. Diagnostický postup: file sa nechce pridať

```bash
git status --untracked-files=all
git check-ignore -v path
git ls-files --stage path
git ls-files -v path
```

Otázky:

- Je path ignored?
- Je už tracked a iba skrytá flagom?
- Je v sparse-checkout view?
- Je parent directory nested repository?
- Aplikuje clean filter chybu?
- Je path mimo repository root?
- Obsahuje filesystem unsupported name alebo permission problém?

Force add:

```bash
git add -f path
```

má byť vedomá výnimka, nie prvý diagnostický krok.

## 39. Diagnostický postup: celý súbor sa javí zmenený

```bash
git diff --ignore-space-at-eol -- path
git diff --word-diff -- path
git diff --summary -- path
git ls-files --eol path
git check-attr -a -- path
file path
```

Možné príčiny:

- LF/CRLF transformácia,
- encoding alebo BOM,
- formatter,
- executable-bit zmena,
- generated content,
- clean/smudge filter,
- neviditeľné whitespace characters.

Neaplikuj normalization commit spolu s funkčnou zmenou bez jasného dôvodu; zhorší review a blame.

## 40. Failure modes

### `MM` status po commit príprave

Index obsahuje staršiu staged verziu a working tree ďalšiu zmenu. Pred commitom pozri oba diffy.

### Súbor je v `.gitignore`, ale stále sa zobrazuje modified

Je tracked. Ignore policy sa týka primárne untracked paths.

### `git restore` zahodil prácu

Working-tree change nebola object ani stash. Git ju nemusí vedieť obnoviť.

### `git clean` odstránil lokálne dáta

Untracked/ignored files nie sú v object database. Obnova závisí od filesystemu alebo backupu.

### Script je v Git mode `100755`, ale po deploymente nie je executable

Packaging alebo target filesystem zmenil mode. Git mode sám negarantuje deployment semantics.

### Sparse checkout ukazuje, že súbor chýba

Path môže existovať v `HEAD` a indexe, ale nie je materializovaná vo working tree.

## 41. Časté omyly

### „Working tree je Git história“

Je iba aktuálny filesystem checkout plus lokálny stav.

### „Staging area je dočasný zoznam filenames“

Index je pripravovaný snapshot s object IDs, modes, flags a conflict stages.

### „Commit automaticky vezme všetko z editora“

Bežný commit vytvorí tree podľa indexu.

### „`git add` presunie súbor“

Working file zostáva. Git zapíše blob a aktualizuje index.

### „`.gitignore` chráni secret“

Chráni iba pred náhodným pridaním untracked path. Neodstraňuje existujúcu históriu ani nerotuje credential.

### „`assume-unchanged` je lokálny ignore“

Je to optimalizačný hint a môže vytvoriť neviditeľné problémy.

### „Untracked file je obnoviteľný cez reflog“

Reflog sleduje refs, nie ľubovoľné filesystem files.

## 42. Diagnostický checklist

Pred commitom alebo recovery zisti:

- Aký je `HEAD` snapshot?
- Čo presne je v indexe?
- Čo je navyše iba vo working tree?
- Existujú untracked alebo ignored dáta, ktoré nie sú zálohované?
- Je path ovplyvnená `.gitattributes` alebo filters?
- Má index conflict stages, intent-to-add alebo special flags?
- Používa repository sparse checkout, sparse index alebo multiple worktrees?
- Ide o normálny file, symlink alebo submodule gitlink?
- Ktorý príkaz zmení index a ktorý fyzické bytes?
- Existuje bezpečná recovery cesta pred deštruktívnou operáciou?

## 43. Zhrnutie

Working tree, index a `HEAD` sú tri samostatné snapshot hranice. `git add` zachytáva working content do indexu, `git commit` vytvára commit z indexu a `git restore` alebo checkout materializujú zvolený source späť do indexu alebo filesystemu.

Presná diagnostika preto vždy začína tromi otázkami:

```text
Čo je v HEAD?
Čo je v indexe?
Čo je vo working tree?
```

Keď sú odpovede explicitné, partial staging, conflicts, sparse checkout, submodules, line endings aj recovery sa dajú vysvetliť ako konkrétne state transitions namiesto pokusov naslepo.

## 44. Kontrolné otázky

1. Aký je rozdiel medzi working tree, indexom a `HEAD` snapshotom?
2. Čo presne vykoná `git add`?
3. Ako čítať dva stĺpce short statusu?
4. Prečo môže byť jedna path súčasne staged aj modified?
5. Ktoré tri diff hranice treba rozlišovať?
6. Ako index reprezentuje merge conflict?
7. Aký je rozdiel medzi intent-to-add a normálne staged file?
8. Prečo `.gitignore` neovplyvní už tracked path?
9. Aký je rozdiel medzi `assume-unchanged` a `skip-worktree`?
10. Ako line-ending normalization mení working bytes oproti blobu?
11. Aký je rozdiel medzi sparse checkout, shallow clone a partial clone?
12. Prečo `git clean -fdx` nemožno považovať za bezpečný reset?
13. Ako obnovíš poškodený index bez zahodenia working-tree zmien?
14. Ako overíš presný obsah budúceho commitu?

## Glossary impact

Relevantné pojmy: working tree, staging area, index, tracked path, untracked path, ignored path, index entry, stat cache, stage 0/1/2/3, partial staging, intent-to-add, assume-unchanged, skip-worktree, clean filter, smudge filter, sparse checkout, sparse index, worktree, gitlink, porcelain status.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Git object model](git-object-model.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Commit, branch, tag a HEAD →](commit-branch-tag-head.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
