# Konflikty

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Git and Automation Basics
- Predpoklady: [Merge a rebase](merge-and-rebase.md), [Working tree, staging area a repository](working-tree-staging-repository.md)
- Súvisiace témy: three-way merge, index stages, semantic conflict, rerere

## 1. Čo je konflikt

Konflikt vznikne, keď Git nevie automaticky vytvoriť jednoznačný výsledok z base, ours a theirs.

Nie každý konflikt je textový overlap. Môže ísť aj o:

- modify/modify,
- add/add,
- delete/modify,
- rename/rename,
- directory/file conflict,
- submodule conflict,
- binary file conflict.

## 2. Three-way model

```text
base    spoločný predok
ours    verzia aktuálnej strany operácie
theirs  verzia integrovanej/replayovanej strany
```

```bash
git merge-base HEAD other
git ls-files -u
```

Index pri konflikte drží stages:

```text
1 base
2 ours
3 theirs
```

## 3. Conflict markers

```text
<<<<<<< HEAD
lokálny obsah
=======
prichádzajúci obsah
>>>>>>> feature
```

Správne riešenie nemusí byť výber jednej strany. Často treba vytvoriť tretiu, semanticky správnu verziu.

## 4. Základný workflow

```bash
git status
git diff --name-only --diff-filter=U
git diff
# upraviť súbory
git add <resolved-paths>
git diff --staged
```

Dokončenie podľa operácie:

```bash
git commit                 # merge
git rebase --continue
git cherry-pick --continue
```

Zrušenie:

```bash
git merge --abort
git rebase --abort
git cherry-pick --abort
```

## 5. Ours a theirs nie sú absolútne pojmy

Pri merge je `ours` typicky current branch a `theirs` integrovateľná branch.

Pri rebase Git replayuje commits na nový base, preto môže byť intuitívna interpretácia obrátená. Pred použitím:

```bash
git checkout --ours file
git checkout --theirs file
```

over stage obsah:

```bash
git show :1:file
git show :2:file
git show :3:file
```

## 6. Semantic conflict

Git môže merge vykonať bez textového konfliktu, ale výsledok môže byť logicky chybný.

Príklady:

- jedna branch premenuje API field, druhá pridá consumer starého názvu,
- dve branches zvýšia limits nezávisle a výsledná kombinácia preťaží systém,
- schema a aplikácia sa merge-nú v nekompatibilnom poradí,
- dependency versions sa textovo zlúčia, ale runtime contract sa zmení.

Preto úspešný merge neznamená správnu integráciu. Potrebné sú tests, linting a review.

## 7. Rename detection

Git neukladá rename ako objektovú operáciu. Rename odvodzuje podobnosťou pri diff/merge.

```bash
git diff --find-renames
git log --follow -- path
```

Veľký rewrite spojený s rename môže znížiť detekciu a vytvoriť zložitejší conflict.

Praktický pattern: oddeliť mechanický rename a obsahovú zmenu do samostatných commitov.

## 8. Binary conflicts

Git nevie bežne line-by-line zlúčiť binary files.

Možnosti:

- zvoliť jednu verziu,
- vygenerovať nový artifact zo source dát,
- použiť domain-specific merge driver,
- odstrániť generované binaries z repository.

```bash
git checkout --ours file.bin
git checkout --theirs file.bin
git add file.bin
```

## 9. Merge drivers a attributes

`.gitattributes` môže definovať merge správanie:

```gitattributes
*.lock merge=ours
*.generated merge=custom
```

Custom driver musí byť deterministický a dostupný všetkým relevantným prostrediam. Nesprávny driver môže vytvoriť tichý semantic conflict bez markerov.

## 10. Rerere

```bash
git config rerere.enabled true
```

Git zaznamená pre-image konfliktu a resolution a môže ho neskôr znovu aplikovať.

Kontroluj výsledok:

```bash
git rerere status
git diff
git diff --staged
```

Rerere zrýchľuje opakované konflikty, ale nenahrádza review.

## 11. Lock files a generované súbory

Lock files sú často zámerne commitované a konflikty sa nemajú riešiť ručným spojením jednotlivých riadkov bez regenerácie.

Bezpečný postup:

1. vyriešiť source dependency declarations,
2. spustiť oficiálny package manager,
3. regenerovať lock file,
4. validovať build/tests.

Generované files majú mať jasný source-of-truth a reprodukovateľný generator.

## 12. Konflikty v konfigurácii a IaC

Pri YAML, Terraform alebo Kubernetes manifestoch kontroluj:

- syntaktickú validitu,
- duplicate keys,
- výsledné defaults,
- ordering dependencies,
- environment-specific values,
- security policy,
- plan/diff výsledok.

Textovo validné zlúčenie môže zmeniť produkčný desired state.

## 13. Minimalizácia konfliktov

- malé branches a malé batches,
- častá integrácia,
- jasné ownership boundaries,
- oddeliť mechanické refactory od behavior changes,
- stabilné formatting rules,
- generovať artifacts deterministicky,
- modularizovať často menené centrálne files,
- komunikovať zmeny shared contracts.

## 14. Konflikt nie je súťaž o „víťaznú stranu“

Cieľom nie je zachovať čo najviac lines z ours alebo theirs. Cieľom je zachovať intent oboch zmien alebo vedome rozhodnúť, ktorý intent už neplatí.

Pri nejasnosti kontaktuj autorov alebo preskúmaj issue, tests a commit messages.

## 15. Overenie resolution

```bash
git diff --check
git diff --staged
git status
```

Následne:

- formatter,
- parser/linter,
- unit/integration tests,
- build,
- behavior-specific validation,
- review výsledného diffu proti obom stranám.

## 16. Recovery

Pred zložitou integráciou:

```bash
git branch backup/pre-integration
```

Po nesprávnom dokončení:

```bash
git reflog
git reset --hard <old-tip>
```

Na publikovanej branch môže byť vhodnejší revert než reset.

## 17. Časté omyly

### „Žiadne conflict markers znamenajú správny merge“

Nie. Semantic conflict môže zostať.

### „Ours je vždy moja feature branch“

Závisí od operácie a current contextu.

### „Rename je explicitne uložený v commite“

Git ho odvodzuje porovnaním.

### „Lock file sa vyrieši vybraním dlhšej verzie“

Má sa regenerovať oficiálnym nástrojom podľa resolved source declarations.

## 18. Kontrolné otázky

1. Čo reprezentujú index stages 1, 2 a 3?
2. Prečo ours/theirs závisí od operácie?
3. Čo je semantic conflict?
4. Ako Git deteguje rename?
5. Prečo sú binary conflicts odlišné?
6. Kedy pomáha rerere?
7. Ako bezpečne riešiť lock file conflict?
8. Ako overíš, že resolution je funkčne správna?

## Glossary impact

Relevantné pojmy: merge conflict, conflict marker, index stage, ours, theirs, semantic conflict, rename detection, merge driver, rerere.
