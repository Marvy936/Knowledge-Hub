# Cherry-pick a stash

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

Release branch `release/4.1` potrebuje malý bezpečnostný fix z main, ale nie celý nový feature set. Alice zároveň pracuje na rozrobenej lokálnej zmene a potrebuje rýchlo prepnúť context. Cherry-pick a stash riešia tieto dve situácie, no ani jeden mechanizmus nie je náhradou za normálnu integráciu ancestry.

## Cherry-pick replayne patch na nový parent

```bash
git switch release/4.1
git cherry-pick <hotfix-commit>
```

Git vezme zmenu vyjadrenú commitom a aplikuje ju na current HEAD. Vznikne nový commit s novým ID:

```text
main:        H1 → ...
release/4.1: H1' → R3
```

H1 a H1' môžu mať podobný patch, ale odlišný parent a snapshot context. Cherry-pick nevytvára ancestry vzťah medzi branches. Neskorší merge môže znovu naraziť na súvisiaci semantic conflict.

## `-x` a traceability

Pri backporte je užitočné:

```bash
git cherry-pick -x <commit>
```

Git pridá do message pôvodný commit ID. To pomáha auditovať, odkiaľ fix prišiel. Neoveruje však, že patch má rovnaký efekt na staršej codebase. Backport potrebuje vlastné tests a release evidence.

## Range a poradie

Viac commits možno replay-nuť:

```bash
git cherry-pick A^..C
```

Poradie ovplyvňuje intermediate state a conflicts. Ak commits nie sú samostatne buildable, cherry-pick iba časti série môže vytvoriť nefunkčný branch. Pred selection treba poznať dependency graph change-u.

## Conflict a abort

Pri conflicte:

```bash
git status
git diff --name-only --diff-filter=U
# resolve + test
git add <resolved-files>
git cherry-pick --continue
```

Ak backport nie je bezpečný:

```bash
git cherry-pick --abort
```

Abort obnoví pre-operation state. Neodstráni unrelated untracked work, preto je clean working tree stále vhodný gate.

## Stash ako lokálny commit-like object

```bash
git stash push -m 'WIP ORD-8421 validation'
```

Stash uloží tracked working-tree a index state do commit-like objektov a obnoví pracovný strom. Untracked files sa pridajú iba s `-u`; ignored files s `-a`.

```bash
git stash list
git stash show -p stash@{0}
```

Stash je lokálny ref a nie je automaticky zdieľaný ani backupovaný. Dlhodobá dôležitá práca patrí skôr na WIP branch s commitom.

## Apply, pop a branch

```bash
git stash apply stash@{0}
```

Apply ponechá stash entry aj po úspechu. `pop` ho po úspešnom apply odstráni, no pri conflicte entry typicky zostane. Bezpečnejší workflow pri starom stash-i:

```bash
git stash branch recovery/wip stash@{0}
```

Git vytvorí branch z pôvodného base commit-u stashu a aplikuje zmeny tam. Tým znižuje conflicts spôsobené posunom current branch.

## Index state v stash-i

Stash môže zachovať staged a unstaged rozdiel. Pri obnove:

```bash
git stash apply --index stash@{0}
```

sa Git pokúsi obnoviť aj index. Bez `--index` sa môže pôvodná staging hranica stratiť. Ak staged snapshot mal zvláštny význam, treba ho po apply skontrolovať cez cached diff.

## Autostash

`git rebase --autostash` dočasne odloží dirty working tree, vykoná rebase a zmeny znovu aplikuje. Znižuje trenie, ale neznižuje semantic risk. Conflict môže vzniknúť až pri opätovnom apply WIP zmien a používateľ musí riešiť dve vrstvy naraz.

Pre kritické history transforms je explicitný WIP commit alebo branch čitateľnejší.

## Incident: hotfix sa opraví iba v release branch

Tím cherry-pickne security fix do `release/4.1`, ale zabudne ho integrovať do main. Neskorší release 4.2 znovu obsahuje zraniteľnosť.

Root cause je neúplný propagation contract. Hotfix lifecycle musí definovať source branch, podporované release branches, mainline propagation a verification matrix. Automation môže sledovať original a backport commit IDs, ale rozhodnutie o applicability zostáva domain review.

## Zhrnutie

Cherry-pick vytvára nový commit replayom patchu a je vhodný pre vedomý backport alebo selektívny transfer. Stash dočasne uchová lokálny working/index state, nie zdieľanú históriu. Oba mechanizmy potrebujú explicitný base, conflict handling a tests. Dôležitá práca a release propagation sa nemajú skrývať v lokálnom stash alebo izolovanom cherry-picku.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Reset, revert a restore](reset-revert-restore.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Konflikty →](merge-conflicts.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
