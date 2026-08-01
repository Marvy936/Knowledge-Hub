## Čo sú working tree, index a repository

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