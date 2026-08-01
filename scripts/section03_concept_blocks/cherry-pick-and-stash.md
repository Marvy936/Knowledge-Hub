## Čo sú cherry-pick a stash

**Cherry-pick** prenesie zmenu reprezentovanú vybraným commitom na aktuálnu branch. Git vezme rozdiel medzi commitom a jeho parentom, aplikuje ho na aktuálny `HEAD` a pri úspechu vytvorí nový commit. Neprenáša pôvodnú ancestry; nový commit má iného parenta a nový object ID.

Používa sa pri selektívnom backporte, hotfixe alebo prenose konkrétnej opravy medzi release lines. Nie je náhradou za pravidelnú integráciu branchí. Ak sa veľká séria commitov cherry-pickuje opakovane, vzniká duplicate history a komplikované budúce merges.

Neutrálny príklad:

```text
main:    C1---C2
release: C1---R1
```

`git cherry-pick C2` na release vytvorí nový commit `C2'`:

```text
release: C1---R1---C2'
```

C2 a C2' môžu mať podobný patch, ale nie sú tým istým commitom.

**Stash** uloží dočasný snapshot pracovného stavu mimo bežnej branch histórie a obnoví working tree podľa zvoleného baseline. Stash entry je implementačne sada commit-like objektov a reflog pod `refs/stash`, nie magická schránka. Môže obsahovať staged a unstaged changes a voliteľne untracked files.

`git stash apply` aplikuje entry a ponechá ho v stash liste. `git stash pop` aplikuje a pri úspechu entry odstráni. Ak vznikne konflikt, entry nemusí byť odstránený. Preto je bezpečnejšie najprv overiť výsledok a až potom stash zmazať.

Stash je vhodný pre krátkodobé prerušenie práce. Nie je reviewovateľná, zdieľaná ani dlhodobá forma uloženia. Ak práca potrebuje prežiť, byť zálohovaná alebo zdieľaná, lepší je WIP commit na branchi.

Pri cherry-picku aj stash apply Git vykonáva merge-like aplikáciu voči odlišnému kontextu. Textovo úspešná aplikácia stále potrebuje diff a tests, pretože nový baseline môže zmeniť semantics.