# Konflikty

Alice zmení `maxOrderAmount` na 5000 a Bob na 7500. Git nevie automaticky rozhodnúť, ktorá business hodnota je správna. Textový conflict je viditeľný, ale mnohé nebezpečné konflikty sa zlúčia bez markerov. Conflict resolution je preto domain integration, nie mechanické odstránenie `<<<<<<<` riadkov.

## Three-way merge

Git porovnáva tri snapshots:

```text
merge base
ours
other side
```

Ak obe strany zmenili rovnakú oblasť od merge base odlišne, index dostane unmerged stages a working tree conflict markers:

```yaml
<<<<<<< HEAD
maxOrderAmount: 5000
=======
maxOrderAmount: 7500
>>>>>>> origin/main
```

Markers sú iba presentation. Skutočné inputs možno čítať:

```bash
git show :1:config/orders.yaml
git show :2:config/orders.yaml
git show :3:config/orders.yaml
git ls-files -u
```

## Resolution je nový obsah

Správny výsledok môže byť 5000, 7500, iná hodnota alebo nový model s environment overrides. Po editácii:

```bash
git add config/orders.yaml
git diff --cached
git status
```

`git add` označí file ako resolved tým, že do indexu vloží jeden blob. Git nevie, či je resolution business správna. Tests, schema validation a review musia overiť výsledný snapshot.

## Rename a delete conflicts

Ak jedna strana file premenuje a druhá ho upraví, Git sa pokúsi detegovať rename podľa podobnosti. Rename nie je uložený ako explicitná operácia v commit object-e; je to diff interpretácia. Pri veľkom rewrite môže detekcia zlyhať.

Delete/modify conflict vznikne, keď jedna strana file odstráni a druhá zmení. Resolution musí rozhodnúť, či capability zanikla, presunula sa alebo má zostať.

## Binary conflicts

Git nevie riadkovo merge-nuť väčšinu binary formátov. Resolution vyberie jednu verziu alebo vytvorí nový artifact z authoritative source. Generated binaries by nemali byť ručne reconciled bez provenance.

Git LFS mení repository obsah na pointer files a blobs ukladá mimo Git object database. Conflict pointerov a dostupnosť LFS objectov sú dve samostatné hranice.

## Semantic conflict bez markerov

Alice zvýši limit, Bob zmení currency z EUR na JPY. Textové riadky sú odlišné a merge prejde čisto, no limit 5000 má úplne inú hodnotu v JPY. To je semantic conflict.

Ďalší príklad: jedna branch premenuje JSON field a druhá pridá consumer, ktorý používa staré meno. Git vidí čistý merge; runtime contract je pokazený.

Prevencia používa tests, schema compatibility, code owners a review final diffu proti merge base:

```bash
git diff --merge-base origin/main HEAD
```

## Conflict počas rebase

Rebase rieši conflicts commit po commite. Po resolution:

```bash
git rebase --continue
```

Ak ďalší replay commit znova mení rovnakú oblasť, conflict sa môže opakovať. `rerere` môže pomôcť, ale každá automaticky znovu použitá resolution sa overí.

Abort:

```bash
git rebase --abort
```

Skip:

```bash
git rebase --skip
```

Skip zahodí konkrétny replay commit a môže odstrániť potrebnú zmenu. Používa sa iba po overení, že patch je redundantný alebo nežiaduci.

## Mergetool a custom drivers

```bash
git mergetool
```

Visual tool zlepšuje porovnanie base/ours/theirs. `.gitattributes` môže definovať merge driver pre špecifické formáty. Custom driver je code execution a correctness boundary; musí mať tests a nesmie ticho označiť neplatný výstup ako resolved.

Pre lockfiles alebo generated manifests je často bezpečnejšie znovu generovať output z reconciled source než ručne merge-nuť generated lines.

## Incident: konflikt bol „vyriešený“ výberom ours

Developer použije `git checkout --ours config/orders.yaml` a pokračuje. Tým odstráni Bobovu security validation, ktorá bola v rovnakom file, hoci viditeľný conflict sa týkal iba limitu. Pipeline unit tests neobsahujú forbidden case a merge prejde.

Root cause je file-level side selection bez domain diffu. Recovery obnoví chýbajúci control, pridá regression test a review policy vyžaduje inspection resolved diffu voči obom parents:

```bash
git diff HEAD^1 HEAD
git diff HEAD^2 HEAD
```

## Zhrnutie

Git conflict znamená, že automatický three-way merge nemá jednoznačný textový výsledok. Resolution je nový integrated snapshot, ktorý musí rešpektovať intent oboch strán. Rename, binary a semantic conflicts môžu vyžadovať iné tools a tests. Absencia markerov nepreukazuje absenciu konfliktu.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Cherry-pick a stash](cherry-pick-and-stash.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Branching strategies →](branching-strategies.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
