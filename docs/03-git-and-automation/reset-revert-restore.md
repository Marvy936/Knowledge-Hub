# Reset, revert a restore

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Git and Automation Basics
- Predpoklady: [Working tree, staging area a repository](working-tree-staging-repository.md), [Commit, branch, tag a HEAD](commit-branch-tag-head.md), [Merge a rebase](merge-and-rebase.md)
- Súvisiace témy: index, reflog, history rewrite, compensation commit, recovery, unmerged state

## 1. Definícia

`restore`, `reset` a `revert` menia rozdielne vrstvy Git stavu:

```text
git restore  → obnovuje working tree a/alebo index zo zvoleného source
git reset    → mení current ref/HEAD a podľa režimu index a working tree
git revert   → nemení starú históriu; vytvorí nový commit s opačným efektom
```

Správny výber závisí od troch otázok:

1. Ktorý stav chcem meniť — working tree, index, branch ref alebo publikovaný graph?
2. Je história iba lokálna, alebo ju už používajú iní?
3. Potrebujem zahodiť stav, preusporiadať lokálnu prácu alebo vytvoriť auditovateľnú kompenzáciu?

## 2. Štyri referenčné stavy

Pri recovery rozlišuj:

```text
HEAD / current branch tip
index / staged snapshot
working tree / materializované súbory
untracked a ignored paths
```

`restore` a `reset` nepracujú automaticky so všetkými štyrmi vrstvami. Najmä untracked a ignored files nie sú bežným `reset --hard` odstránené.

Pred zásahom:

```bash
git status --short
git diff
git diff --staged
git log --oneline -5
git rev-parse HEAD
```

Pri rizikovej operácii vytvor recovery ref:

```bash
git branch backup/before-recovery
```

## 3. `git restore` — obnova obsahu bez pohybu branch

`git restore` nemení current branch ref. Kopíruje obsah zo source do indexu a/alebo working tree.

Predvolený source závisí od cieľa:

- pri obnove working tree je source typicky index,
- pri `--staged` je source typicky `HEAD`.

Preto sú tieto dve operácie rozdielne:

```bash
git restore app.conf
```

obnoví working-tree verziu z indexu, zatiaľ čo:

```bash
git restore --staged app.conf
```

obnoví index z `HEAD`, ale ponechá pracovný súbor nezmenený.

## 4. Restore working tree

Zahodenie unstaged zmien:

```bash
git restore path/to/file
```

Výsledok:

```text
source: index
change: working tree
branch: bez zmeny
index: bez zmeny
```

Pri súbore so staged aj unstaged zmenou sa zahodí iba unstaged časť; staged snapshot zostane.

Pred vykonaním vždy skontroluj:

```bash
git diff -- path/to/file
git diff --staged -- path/to/file
```

Necommitnutá unstaged zmena nemusí byť obnoviteľná cez reflog, pretože reflog eviduje refs, nie každý obsah editora.

## 5. Restore index — unstage

```bash
git restore --staged path/to/file
```

Výsledok:

```text
source: HEAD
change: index
working tree: ponechaný
branch: bez zmeny
```

Tým sa staged zmena zmení na unstaged. Obsah pracovného súboru zostane dostupný.

Pre presné review:

```bash
git diff --staged -- path/to/file
git restore --staged path/to/file
git diff -- path/to/file
```

Starší ekvivalent:

```bash
git reset HEAD -- path/to/file
```

Moderný `restore --staged` jasnejšie vyjadruje cieľ.

## 6. Explicitný restore source

Obsah možno obnoviť z ľubovoľného commitu alebo tree-ish:

```bash
git restore --source=HEAD~2 --worktree path/to/file
git restore --source=v1.4.0 --staged --worktree config/
```

Toto nevytvára commit ani nemení ancestry. Iba pripraví alebo zapíše zvolený snapshot.

Ak chceš historickú verziu následne publikovať, musíš ju reviewnúť, stage-nuť a commitnúť ako novú zmenu.

## 7. Partial restore

Interaktívna obnova hunks:

```bash
git restore -p path/to/file
```

Použitie:

- zahodiť iba chybnú časť unstaged zmien,
- unstage iba vybrané hunks cez `--staged -p`,
- oddeliť logické zmeny bez zahodenia celého súboru.

Partial restore je bezpečnejší než plošná obnova, ale stále môže zahodiť necommitnutý obsah. Pred potvrdením čítaj každý patch hunk.

## 8. Restore unmerged paths

Po merge konflikte index obsahuje stages 1–3. Pri explicitnom výbere strany:

```bash
git restore --ours path/to/file
git restore --theirs path/to/file
```

Význam `ours` a `theirs` závisí od operácie. Pri rebase sa môže javiť obrátene oproti používateľskej intuícii.

Autoritatívne overenie:

```bash
git ls-files -u
git show :1:path/to/file
git show :2:path/to/file
git show :3:path/to/file
```

Po zvolení obsahu musíš path označiť ako vyriešenú:

```bash
git add path/to/file
```

## 9. `git reset` — pohyb refu a synchronizácia stavov

Pri commit forme:

```bash
git reset [mode] <target>
```

Git môže vykonať tri kroky:

1. posunúť current branch alebo detached `HEAD` na target,
2. nastaviť index podľa target tree,
3. nastaviť tracked working tree podľa target tree.

Režim určuje, koľko z týchto krokov sa vykoná.

## 10. Soft reset

```bash
git reset --soft <target>
```

Mení:

```text
branch/HEAD: áno
index:       nie
working tree: nie
```

Príklad:

```text
pred:  A---B---C  main
po:    A---B      main
              C obsah zostáva staged
```

Použitie:

- zlúčiť viac lokálnych commitov do nového commitu,
- opraviť commit boundaries,
- zmeniť posledné commits pri zachovaní presného staged snapshotu.

`C` sa po pohybe branch môže stať unreachable z branch, ale zostáva dočasne dostupný cez reflog.

## 11. Mixed reset

```bash
git reset --mixed <target>
# default:
git reset <target>
```

Mení:

```text
branch/HEAD: áno
index:       nastaví podľa targetu
working tree: ponechá
```

Zmeny medzi starým tipom a targetom zostanú ako unstaged working-tree changes.

Použitie:

```bash
git branch backup/before-reset
git reset --mixed HEAD~3
git status
git diff
```

Takto odstrániš lokálne commits z branch history, ale ponecháš ich výsledný obsah na ďalšie rozdelenie a stageovanie.

## 12. Hard reset

```bash
git reset --hard <target>
```

Mení:

```text
branch/HEAD: áno
index:       áno
tracked working tree: áno
untracked files: typicky nie
```

Tracked súbory sa prepíšu podľa target tree. Untracked súbor môže byť odstránený, ak prekáža vytvoreniu tracked path z targetu, ale `reset --hard` nie je všeobecný cleanup untracked dát.

Riziko:

- staged aj unstaged tracked zmeny môžu zaniknúť,
- reflog obnoví staré commits, ale nie nutne necommitnutý obsah,
- editor alebo filesystem recovery môže byť jediná zostávajúca cesta.

Pred použitím:

```bash
git status --short
git diff
git diff --staged
git branch backup/before-hard-reset
```

## 13. Reset `--merge`

```bash
git reset --merge <target>
```

`--merge` aktualizuje index a working tree podobne ako read-tree merge, ale snaží sa zachovať lokálne zmeny, ktoré sa neprekrývajú s rozdielom medzi current `HEAD` a targetom.

Je užitočný pri:

- návrate po merge-like operácii,
- zachovaní niektorých unstaged zmien,
- situácii, kde `--hard` by bolo príliš deštruktívne.

Ak by reset prepísal lokálne zmenený súbor, operácia typicky zlyhá namiesto tichého zahodenia.

## 14. Reset `--keep`

```bash
git reset --keep <target>
```

`--keep` presunie ref a aktualizuje súbory, ale odmietne operáciu, ak by zmena medzi current `HEAD` a targetom prepísala lokálne working-tree modifications.

Rozdiel oproti `--merge` je v presných pravidlách indexu a lokálnych zmien. Obe možnosti sú ochranné režimy; pri nejasnosti vytvor commit/stash a testuj na recovery branchi.

## 15. Path reset

```bash
git reset <source> -- path/to/file
```

Path form:

- nepresúva branch ani `HEAD`,
- mení iba index pre vybrané paths,
- source je typicky `HEAD`, ale môže byť iný tree-ish.

Príklad:

```bash
git reset HEAD~1 -- config/app.yml
```

nastaví index verziou z `HEAD~1`, working tree ponechá. To môže pripraviť commit, ktorý selektívne obnoví historickú verziu path.

Zrozumiteľnejší moderný tvar:

```bash
git restore --source=HEAD~1 --staged config/app.yml
```

## 16. Reset v detached HEAD stave

V detached stave `reset <target>` presunie priamo `HEAD`, pretože neexistuje current branch ref, ktorý by sa mal posunúť.

Pred:

```text
HEAD → C
```

Po:

```bash
git reset --hard B
```

```text
HEAD → B
```

Ak chceš výsledok zachovať ako pomenovanú históriu:

```bash
git switch -c recovery/reset-result
```

## 17. Publikovaná história a reset

Reset mení viditeľný tip branch. Ak bol starý tip pushnutý, následný push bude non-fast-forward a vyžadoval by history rewrite:

```bash
git push --force-with-lease
```

Na zdieľanej alebo protected branch reset typicky nie je správny spôsob opravy. Použi `revert`, ktorý pridá auditovateľný kompenzačný commit.

## 18. `git revert` — kompenzačný commit

```bash
git revert <commit>
```

Revert:

1. vypočíta zmenu daného commitu voči jeho parentovi,
2. aplikuje inverznú zmenu na current `HEAD`,
3. vytvorí nový commit.

Graf:

```text
A---B---C---R  main
        ^   ^
        |   revert effect
        pôvodný commit zostáva
```

Revert zachová ancestry, auditné odkazy a commit IDs. Je preto štandardnou voľbou pre publikovanú históriu.

## 19. Revert nie je časový návrat

Revert neobnovuje repository automaticky do presného historického snapshotu. Inverzuje konkrétnu zmenu v kontexte current tree.

Ak neskoršie commits upravili rovnaký kód, môže vzniknúť konflikt alebo výsledok odlišný od starého snapshotu.

Pred revertom:

```bash
git show <commit>
git log --oneline --ancestry-path <commit>..HEAD
git diff <commit>^..<commit>
```

## 20. Revert rozsahu

Viac commitov:

```bash
git revert <commit1> <commit2>
```

Príprava viacerých revertov bez okamžitého commitu:

```bash
git revert --no-commit <oldest>^..<newest>
git diff --staged
git commit -m 'revert: disable faulty change set'
```

Poradie je dôležité. Pri závislých commitoch sa často revertuje od najnovšieho k najstaršiemu, ale správne poradie závisí od dependency graphu a požadovaného výsledku.

`--no-commit` umožní spoločné review a test, ale zlúči audit viacerých kompenzácií do jedného nového commitu.

## 21. Revert merge commitu

```bash
git revert -m 1 <merge-commit>
```

`-m 1` označuje parent 1 ako mainline. Git odoberie efekt, ktorý merge priniesol oproti tejto hlavnej línii.

Pred vykonaním:

```bash
git show --no-patch --pretty=raw <merge-commit>
git diff <merge-commit>^1..<merge-commit>
git diff <merge-commit>^2..<merge-commit>
```

Dôležitý dôsledok: revert merge commitu nemení ancestry. Budúci merge môže považovať pôvodné commits za už integrované. Opätovné zavedenie feature preto často vyžaduje revert pôvodného revertu alebo nové commits.

## 22. Revert sequencer

Pri sérii revertov alebo konflikte Git používa sequencer state.

```bash
git status
git revert --continue
git revert --skip
git revert --abort
```

Po konflikte:

```bash
# uprav konflikty
git add <paths>
git revert --continue
```

`--abort` obnoví stav pred začiatkom sekvencie, pokiaľ recovery nekomplikuje ďalší manuálny zásah.

## 23. `git commit --amend`

```bash
git commit --amend
```

Amend vytvorí nový commit s rovnakým parentom, ale novým snapshotom, message alebo metadata.

Použitie:

- doplniť zabudnutý staged súbor,
- opraviť poslednú commit message,
- znovu podpísať alebo upraviť lokálny commit.

Aj message-only amend mení object ID. Na publikovanej branch ide o history rewrite a vyžaduje koordináciu plus `--force-with-lease`.

## 24. `ORIG_HEAD`

Niektoré operácie ukladajú predchádzajúci tip do:

```text
ORIG_HEAD
```

Kontrola:

```bash
git show --no-patch ORIG_HEAD
```

Môže pomôcť po merge, reset alebo pull, ale:

- nie každá operácia ho aktualizuje rovnako,
- ďalšia operácia ho môže prepísať,
- nie je to história všetkých pohybov.

Reflog je spoľahlivejší všeobecný zdroj pre recovery refov.

## 25. Reflog recovery

```bash
git reflog --date=iso
git reflog show main
git show HEAD@{3}
```

Po chybnom resete:

```bash
git branch recovery/before-reset HEAD@{1}
```

Až po zachovaní recovery refu môžeš branch vedome presunúť späť:

```bash
git reset --hard recovery/before-reset
```

Reflog je lokálny a má obmedzenú retention. Remote server nemusí používateľovi sprístupniť ekvivalentný reflog.

## 26. Obnova necommitnutých zmien

Git spoľahlivo obnovuje objekty, ktoré boli zapísané do object database. Necommitnuté working-tree dáta nemusia existovať ako reachable alebo unreachable Git objekty.

Možné zdroje:

- staged blob po predchádzajúcom `git add`,
- dangling blob nájdený cez `git fsck --lost-found`,
- editor local history,
- filesystem snapshot alebo backup,
- IDE recovery,
- stash alebo WIP commit.

```bash
git fsck --full --no-reflogs --unreachable
```

Výstup môže obsahovať veľa unrelated objektov a neposkytuje filenames pre samostatné blobs. Nie je to garantovaný undo mechanizmus.

## 27. Untracked a ignored cleanup

`reset --hard` nie je plný cleanup.

Preview untracked files:

```bash
git clean -n
git clean -nd
```

Odstránenie:

```bash
git clean -fd
```

Ignored files vyžadujú `-x` alebo `-X`, čo môže zmazať build cache, lokálne databázy, `.env`, IDE state alebo iné nenahraditeľné dáta.

```bash
git clean -ndx
```

použi vždy ako preview pred deštruktívnou operáciou.

## 28. Rozhodovací model

```text
Chcem zahodiť unstaged zmenu v tracked súbore?
→ git restore <path>

Chcem unstage bez zmeny working tree?
→ git restore --staged <path>

Chcem pripraviť historickú verziu path do indexu/working tree?
→ git restore --source=<tree-ish> ...

Chcem presunúť iba lokálnu nepublikovanú branch?
→ git reset s vedome zvoleným mode

Chcem zachovať obsah, ale odstrániť lokálne commits?
→ git reset --mixed alebo --soft podľa želaného indexu

Chcem auditovateľne zrušiť publikovaný commit?
→ git revert

Chcem zrušiť publikovaný merge?
→ git revert -m <mainline>, až po overení parentov
```

## 29. Bezpečný lokálny reset workflow

```bash
git status
git diff
git diff --staged
git branch backup/before-reset
old=$(git rev-parse HEAD)

git reset --mixed HEAD~2

git status
git diff
git reflog -5
git show "$old"
```

Ak výsledok nie je správny, recovery branch stále ukazuje na pôvodný tip.

## 30. Bezpečný publikovaný revert workflow

```bash
git fetch origin
git switch main
git pull --ff-only
git show <bad-commit>
git revert --no-commit <bad-commit>
git diff --staged
# build/test/smoke test
git commit -m 'revert: disable faulty behavior'
git push origin main
```

Revert treba testovať ako novú zmenu. Inverzný patch môže v aktuálnom kontexte narušiť neskoršie opravy alebo dependencies.

## 31. Troubleshooting

### Reset zmenil viac files, než som čakal

```bash
git reflog -10
git diff HEAD@{1}^{tree} HEAD^{tree}
git status --short
```

Najprv vytvor recovery branch na starý tip. Potom rozhodni, či treba obnoviť branch, index, working tree alebo iba vybrané paths.

### Revert konfliktuje

```bash
git status
git show REVERT_HEAD
git ls-files -u
```

Konflikt znamená, že current tree sa od pôvodného kontextu zmenil. Vyrieš požadovaný súčasný výsledok, nie mechanickú „opačnú“ verziu starého súboru.

### `restore` nevrátil verziu z `HEAD`

Ak súbor mal staged zmenu, plain `git restore file` obnovuje z indexu. Pre explicitný `HEAD` source:

```bash
git restore --source=HEAD --worktree file
```

### Hard reset neodstránil build adresár

Build adresár je pravdepodobne untracked alebo ignored. Použi iba preview:

```bash
git clean -ndx
```

a over, či neobsahuje lokálne dáta.

## 32. Časté omyly

### „Restore je synonymum resetu“

Nie. Restore nemení branch ref; reset ho pri commit forme môže presunúť.

### „Reset vždy maže súbory“

Nie. `--soft` nemení index ani working tree, `--mixed` ponecháva working tree.

### „Hard reset vyčistí celý repository“

Nie. Untracked a ignored paths majú samostatný lifecycle.

### „Revert odstráni commit z histórie“

Nie. Pridá nový kompenzačný commit.

### „Revert vždy obnoví presný starý snapshot“

Nie. Inverzuje konkrétnu zmenu v current kontexte.

### „Reflog obnoví všetky necommitnuté zmeny“

Nie. Primárne eviduje pohyby refs a `HEAD`.

### „Amend upraví existujúci commit na mieste“

Nie. Vytvorí nový commit object.

## 33. Kontrolné otázky

1. Ktoré vrstvy mení `restore`, `reset` a `revert`?
2. Prečo plain `restore <path>` používa index ako source?
3. Aký je rozdiel medzi soft, mixed a hard resetom?
4. Kedy sú vhodné `reset --merge` a `reset --keep`?
5. Prečo path reset nepresúva branch?
6. Prečo je revert vhodný pre zdieľanú históriu?
7. Čo presne znamená `revert -m 1`?
8. Prečo revert merge ovplyvňuje budúce merges?
9. Čo dokáže obnoviť reflog a čo nemusí?
10. Ako bezpečne vyčistíš untracked files?

## Glossary impact

Relevantné pojmy: restore source, staged restore, soft reset, mixed reset, hard reset, reset --merge, reset --keep, path reset, revert, compensation commit, mainline parent, revert sequencer, amend, ORIG_HEAD, reflog recovery.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Merge a rebase](merge-and-rebase.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Cherry-pick a stash →](cherry-pick-and-stash.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
