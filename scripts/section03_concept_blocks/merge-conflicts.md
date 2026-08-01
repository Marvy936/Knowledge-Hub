## Čo je konflikt

Konflikt vzniká, keď Git pri merge-like operácii nedokáže jednoznačne vytvoriť výsledný snapshot. Nie je to automaticky chyba developera ani poškodenie repository. Je to explicitné priznanie, že mechanický algoritmus nemá dostatok domain informácií na bezpečný verdict.

Pri textovom three-way merge používa Git merge base a dve sides. Pre konfliktný pathname index drží stages:

```text
stage 1: merge base
stage 2: ours
stage 3: theirs
```

Working tree môže obsahovať conflict markers, ale authoritative informácia nie je iba text medzi `<<<<<<<` a `>>>>>>>`. Rename/delete, binary, mode, submodule alebo directory/file conflict môže mať inú reprezentáciu.

Konflikt sa rieši vytvorením správneho výsledného súboru, jeho stageovaním a pokračovaním operácie. „Vybrať ours“ alebo „vybrať theirs“ znamená zahodiť druhú stranu pre daný path; nie je to univerzálne riešenie. Často treba skombinovať oba intents alebo vytvoriť tretí výsledok.

Neutrálny príklad:

```text
base:   timeout = 10
ours:   timeout = 20
theirs: timeout = 30
```

Git nevie, či výsledok má byť 20, 30, maximum, minimum alebo úplne nový model. Odpoveď patrí vlastníkovi configuration contractu.

**Textový konflikt** je iba jedna trieda. **Semantic conflict** môže prejsť bez markerov: jedna branch premenuje field a druhá pridá validator pracujúci so starým názvom. Merge je čistý, ale program nefunguje. Preto resolution zahŕňa final diff, build, tests, schema checks a podľa rizika runtime verification.

Počas merge alebo rebase musíš vedieť, ktorú operáciu dokončuješ. `git merge --abort`, `git rebase --abort` a `git cherry-pick --abort` obnovujú odlišné sequencer states. Pred ručným mazaním `.git` files je bezpečnejšie použiť operation-aware commands.

Conflict resolution je nový change. Má mať reviewovateľný výsledok a dôkaz, že zachováva požadovaný intent oboch strán alebo vedome jednu odmieta.