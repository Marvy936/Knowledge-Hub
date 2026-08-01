# Working tree, staging area a repository

Bežné Git repository má tri odlišné vrstvy stavu. **Working tree** je checkoutnutá podoba projektu na filesystéme, ktorú upravuje editor, formatter alebo build tool. **Index**, často nazývaný staging area, je binárny Git súbor obsahujúci návrh tree snapshotu pre nasledujúci commit. **Repository** v adresári `.git` obsahuje object database, refs, konfiguráciu, reflogs a ďalšie metadata.

Tieto vrstvy nie sú tri kópie rovnakého adresára. Každá odpovedá na inú otázku:

```text
HEAD commit
Čo je aktuálne zapísané v histórii?

index
Čo presne bude obsahovať nasledujúci commit?

working tree
Čo je momentálne na disku?
```

`git diff` bez ďalších argumentov porovnáva working tree s indexom. `git diff --cached` porovnáva index s `HEAD`. `git status` kombinuje oba pohľady, ale stále je iba read-back; nič nestageuje ani necommitne.

Príkaz `git add` nekopíruje „súbor“ do osobitného adresára. Prečíta aktuálne bytes, vytvorí alebo nájde blob a aktualizuje index entry pre daný pathname. Ak súbor po `git add` znova upravíš, index drží staršiu staged verziu a working tree novšiu unstaged verziu. Jeden pathname tak môže súčasne existovať v troch odlišných stavoch.

Neutrálny príklad:

```text
HEAD:    timeout = 10
index:   timeout = 20
working: timeout = 30
```

Commit by zapísal hodnotu `20`, nie `30`. `git restore --staged` mení index, zatiaľ čo `git restore` bez `--staged` mení working tree. Rozlíšenie targetu je preto dôležitejšie než memorovanie príkazu.

Index podporuje aj partial staging. Jeden fyzický súbor môže obsahovať dve logické zmeny, z ktorých iba jedna patrí do commitu. `git add -p` umožní pripraviť coherent snapshot bez dočasného prepisovania working tree. Táto schopnosť je základom reviewovateľných commitov.

Pri merge konflikte index používa viac stages pre rovnaký pathname: merge base, ours a theirs. Index teda nie je iba „čakáreň“, ale dátová štruktúra, nad ktorou Git zostavuje nový tree.

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

## Mechanický walkthrough: čo presne porovnávajú status a diff

Začni clean commitom a uprav jeden file:

```bash
printf 'maxOrderAmount: 4000\n' > config/orders.yaml
git add config/orders.yaml
git commit -m 'add initial order limit'
printf 'maxOrderAmount: 5000\n' > config/orders.yaml
```

V tomto momente sú tri relevantné snapshots:

```text
HEAD tree:      4000
index entry:    4000
working file:   5000
```

Preto:

```bash
git diff -- config/orders.yaml
```

porovná working tree s indexom a ukáže 4000 → 5000. Naopak:

```bash
git diff --cached -- config/orders.yaml
```

je prázdny, pretože index stále zodpovedá HEAD. `git diff HEAD -- path` porovná working tree priamo s HEAD a v tejto chvíli ukáže rovnaký rozdiel ako prvý command, ale po partial stagingu už nie.

```bash
git add config/orders.yaml
```

`git add` načíta aktuálne bytes, zapíše alebo reuse-ne blob a zmení index entry. Working file nepresúva do špeciálneho priečinka. Po add:

```text
HEAD tree:      4000
index entry:    5000
working file:   5000
```

Teraz je obyčajný `git diff` prázdny a `git diff --cached` ukazuje staged change. Ak file znovu upravíš na 5500, súčasne existujú staged aj unstaged changes:

```text
HEAD tree:      4000
index entry:    5000
working file:   5500
```

`git status --short` môže zobraziť `MM`: prvé písmeno opisuje index proti HEAD, druhé working tree proti indexu. Status nie je štvrtá databáza; je to zhrnutie dvoch porovnaní a untracked/conflict state-u.

Partial staging:

```bash
git add -p config/orders.yaml
```

Git rozdelí diff na hunks a pri každom sa pýta, či sa má aplikovať do indexu. Keď zvolíš `s`, skúsi hunk rozdeliť; `e` otvorí patch editor. Výsledok treba čítať oboma diffmi, pretože file môže obsahovať kombináciu staged a unstaged intentu.

```bash
git diff --cached
git diff
```

Pri citlivom commite je vhodný explicitný gate:

```bash
git diff --cached --check
git diff --cached --name-status
git diff --cached
```

`--check` hľadá vybrané whitespace chyby, nie business correctness. `--name-status` ukáže path-level actions a posledný command celý patch. Až potom `git commit` vytvorí tree z indexu; neberie automaticky všetko, čo editor momentálne zobrazuje.

Ak chceš staged file odstageovať bez straty working changes:

```bash
git restore --staged config/orders.yaml
```

Index sa vráti k HEAD, working file zostane. Ak chceš zahodiť working zmenu a obnoviť index version:

```bash
git restore config/orders.yaml
```

Tieto dve operácie majú opačný destination. Pred ich vykonaním si vždy povedz, ktorý snapshot je source a ktorú vrstvu chceš prepísať.

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
