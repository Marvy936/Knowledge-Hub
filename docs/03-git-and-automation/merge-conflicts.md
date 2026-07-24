# Konflikty

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Git and Automation Basics
- Predpoklady: [Merge a rebase](merge-and-rebase.md), [Working tree, staging area a repository](working-tree-staging-repository.md), [Cherry-pick a stash](cherry-pick-and-stash.md)
- Súvisiace témy: three-way merge, index stages, rename detection, merge drivers, rerere, semantic validation

## 1. Definícia

Konflikt vznikne, keď Git nedokáže z dostupných snapshots jednoznačne vytvoriť výsledný stav.

Git pozná:

```text
base    spoločný predok alebo syntetická merge base
ours    jedna strana operácie
theirs  druhá alebo replayovaná strana
```

Konflikt nie je poškodenie repository ani dôkaz chyby Git-u. Je to explicitné zastavenie automatizácie v bode, kde musí človek alebo domain-specific nástroj rozhodnúť o výslednom obsahu.

## 2. Textový a semantický konflikt

Rozlišuj:

- **detegovaný konflikt** — Git nevie automaticky zlúčiť snapshots a nechá unmerged index,
- **semantic conflict** — Git vytvorí textovo čistý výsledok, ale kombinované správanie je nesprávne.

Príklad semantic conflictu:

- branch A premenuje API field,
- branch B pridá nový consumer starého field-u,
- zmeny sú v rozdielnych súboroch,
- merge prejde bez markerov,
- runtime contract je nekompatibilný.

Preto „merge prešiel bez konfliktu“ nie je dôkaz správnej integrácie.

## 3. Conflict taxonomy

Konflikt nemusí byť iba prekrývajúca sa zmena riadkov.

Typické triedy:

- **modify/modify** — obe strany zmenili rovnaký obsah,
- **add/add** — obe strany vytvorili rovnakú path s odlišným obsahom,
- **modify/delete** — jedna strana path zmenila, druhá odstránila,
- **rename/modify** — jedna strana path premenovala, druhá ju zmenila,
- **rename/rename** — obe strany zvolili odlišný nový názov,
- **rename/delete** — jedna strana premenovala, druhá odstránila,
- **directory/file** — jedna strana potrebuje directory, druhá file na rovnakej path,
- **file-mode conflict** — rozdiel executable bitu alebo typu tree entry,
- **symlink conflict** — rozdiel medzi symlinkom a regular file,
- **submodule conflict** — gitlink ukazuje na nejednoznačné commits,
- **binary conflict** — obsah nemožno rozumne line-by-line zlúčiť.

Diagnostický postup musí zodpovedať typu konfliktu.

## 4. Najprv identifikuj operáciu

Pred resolution zisti, čo prebieha:

```bash
git status
git rev-parse --git-path MERGE_HEAD
git rev-parse --git-path REBASE_HEAD
git rev-parse --git-path CHERRY_PICK_HEAD
```

Možné kontexty:

- merge,
- rebase,
- cherry-pick,
- revert,
- stash apply/pop,
- checkout/switch s unmerged indexom.

Operácia určuje:

- význam `ours` a `theirs`,
- príkaz na pokračovanie,
- príkaz na abort,
- poradie replayovaných commitov,
- očakávaný výsledný graph.

## 5. Three-way model

Pri bežnom merge:

```text
base   = merge base
ours   = current branch tip
theirs = tip integrovanej branch
```

Git porovná:

```text
base → ours
base → theirs
```

Ak obe strany zmenili rovnaký logický región nekompatibilne, Git nevie vybrať výsledok.

Zobrazenie merge base:

```bash
git merge-base HEAD other-branch
git show $(git merge-base HEAD other-branch):path/to/file
```

Pri komplikovanom grafe môže merge stratégia vytvoriť virtuálnu base z viacerých common ancestors.

## 6. Index stages

Po konflikte index môže držať tri entries pre jednu path:

```text
stage 1 — base
stage 2 — ours
stage 3 — theirs
```

```bash
git ls-files -u
git show :1:path/to/file
git show :2:path/to/file
git show :3:path/to/file
```

`git ls-files -u` ukáže mode, object ID, stage a path. To je autoritatívnejšie než odhadovanie podľa conflict markerov v editore.

Po resolution:

```bash
git add path/to/file
```

nahradí stages 1–3 jednou stage-0 entry reprezentujúcou výsledný snapshot.

## 7. `ours` a `theirs` závisia od kontextu

Pri bežnom merge:

```text
ours   = current branch
theirs = branch, ktorú merge-uješ
```

Pri rebase:

```text
ours   = nový base + už replaynuté commits
theirs = práve replayovaný starý commit
```

Preto „vezmi theirs, lebo to je main“ môže pri rebase urobiť opak zámeru.

Pred automatickým výberom:

```bash
git show :2:path/to/file
git show :3:path/to/file
```

Moderné príkazy:

```bash
git restore --ours path/to/file
git restore --theirs path/to/file
```

Potom vždy review-ni obsah a stage-ni resolution.

## 8. Conflict markers

Bežný marker style:

```text
<<<<<<< HEAD
ours content
=======
theirs content
>>>>>>> feature
```

Marker zobrazuje iba konfliktnú pracovnú reprezentáciu. Base nemusí byť priamo viditeľná.

Užitočná konfigurácia:

```bash
git config merge.conflictStyle diff3
# alebo novšie:
git config merge.conflictStyle zdiff3
```

`diff3` pridá base sekciu:

```text
<<<<<<< ours
ours
||||||| base
base
=======
theirs
>>>>>>> theirs
```

Base často odhalí, čo presne každá strana zmenila. Marker však nepokrýva všetky conflict typy, napríklad binary alebo rename/delete.

## 9. Základný resolution workflow

```bash
git status
git diff --name-only --diff-filter=U
git ls-files -u
git diff
```

Pre každú path:

1. identifikuj typ konfliktu,
2. prečítaj base, ours a theirs,
3. pochop intent oboch commitov,
4. vytvor výslednú verziu,
5. odstráň conflict markers,
6. stage-ni path,
7. review-ni staged diff.

```bash
git add <resolved-path>
git diff --staged
git status
```

Pokračovanie:

```bash
git commit
git rebase --continue
git cherry-pick --continue
git revert --continue
```

## 10. Combined diff

Počas merge konfliktu:

```bash
git diff --cc
git diff --combined
```

Combined diff ukazuje vzťah výslednej pracovnej verzie k viacerým parentom. Je užitočný pri review merge resolution, pretože obyčajný dvojstranný diff nemusí ukázať, čo sa zachovalo z každej strany.

Po vytvorení merge commitu:

```bash
git show --cc HEAD
git show -m HEAD
```

- `--cc` — kombinovaný pohľad,
- `-m` — samostatný diff voči každému parentovi.

## 11. Modify/modify konflikt

Postup:

- nevyberaj automaticky dlhšiu alebo novšiu verziu,
- zisti, čo každá zmena riešila,
- spoj invarianty oboch strán,
- odstráň už neplatnú logiku,
- aktualizuj tests.

Príklad:

```text
base:   timeout = 10
ours:   timeout = config.request_timeout
theirs: timeout = 30
```

Správny výsledok nemusí byť ani jedna strana. Môže byť:

```text
timeout = config.request_timeout ?? 30
```

iba ak to zodpovedá zamýšľanému contractu a štýlu jazyka.

## 12. Add/add konflikt

Obe strany pridali rovnakú path.

Over:

```bash
git show :2:new-file
git show :3:new-file
```

Možnosti:

- zlúčiť obsah,
- ponechať jednu implementáciu,
- premenovať jednu path,
- rozdeliť zodpovednosti do dvoch files,
- odstrániť duplicitnú implementáciu.

Rozhodnutie musí zohľadniť imports, build manifesty, ownership a dokumentáciu.

## 13. Modify/delete konflikt

Jedna strana path odstránila, druhá ju zmenila.

Otázka nie je „ktorý súbor je novší“, ale:

```text
Je odstránenie stále platné a treba zmenu preniesť inde?
```

Možnosti:

```bash
git rm path/to/file          # potvrdiť odstránenie
git add path/to/file         # ponechať resolved file
```

Často treba preniesť užitočnú časť modifikácie do novej architektúry a pôvodnú path aj tak odstrániť.

## 14. Rename detection

Git neukladá „rename event“. Rename odvodzuje z podobnosti deleted a added obsahu.

```bash
git diff --find-renames
git diff --find-renames=50%
git log --follow -- path/to/file
```

Dôsledky:

- rename + veľký rewrite môže byť vyhodnotený ako delete/add,
- rename threshold ovplyvní zobrazenie a merge heuristiku,
- dve nezávislé renames môžu vytvoriť rename/rename conflict,
- directory rename inference môže meniť cieľ paths.

Praktický pattern:

1. samostatný mechanický rename commit,
2. samostatný behavior-change commit.

Tým sa zlepší detekcia, review aj budúca integrácia.

## 15. Directory/file conflict

Príklad:

```text
ours:   config        regular file
theirs: config/app.yml directory + file
```

Filesystem nemôže mať file a directory na rovnakej path. Git môže dočasne uložiť jednu stranu pod pomocným názvom.

Resolution vyžaduje zvoliť novú štruktúru a aktualizovať:

- imports,
- build scripts,
- deployment paths,
- documentation,
- ignore/attributes rules.

## 16. File mode a symlink konflikty

Tree entry obsahuje mode. Konflikt môže byť medzi:

```text
100644 regular file
100755 executable file
120000 symbolic link
```

Kontrola:

```bash
git ls-files --stage path
git diff --summary
git cat-file -p :2:path
git cat-file -p :3:path
```

Pri shell skripte môže strata executable bitu rozbiť CI aj bez zmeny textového obsahu. Pri symlink konflikte over aj bezpečnostný dopad a cieľ odkazu.

## 17. Binary conflicts

Git nevie všeobecne line-by-line zlúčiť binary obsah.

Možnosti:

- zvoliť jednu stranu,
- otvoriť obe verzie v domain-specific editore,
- znovu vygenerovať artifact zo zdrojových dát,
- použiť definovaný merge driver,
- odstrániť generovaný binary z repository a publikovať ho ako artifact.

```bash
git restore --ours file.bin
git restore --theirs file.bin
git add file.bin
```

Po výbere over, že binary je čitateľný a kompatibilný; úspešné `git add` neoveruje formát.

## 18. Submodule conflicts

Superproject ukladá submodule ako gitlink na konkrétny commit.

```bash
git ls-files --stage path/to/submodule
git submodule status
git -C path/to/submodule log --oneline --graph --all
```

Resolution môže znamenať:

- vybrať ours gitlink,
- vybrať theirs gitlink,
- nájsť descendant commit obsahujúci obe zmeny,
- merge-nuť históriu priamo v submodule repository,
- aktualizovať superproject na nový resolved submodule commit.

Samotné zvolenie vyššieho SHA nemá význam; commit IDs nie sú poradové čísla.

## 19. Lock files

Lock file konflikt nerieš mechanickým spájaním generovaných riadkov.

Bezpečný postup:

1. vyrieš source dependency declarations,
2. odstráň konfliktné markery v manifestoch,
3. spusti oficiálny package manager v podporovanej verzii,
4. regeneruj lock file,
5. review-ni dependency diff,
6. spusti reproducible install/build/tests.

Príklady source-of-truth:

```text
package.json → package-lock.json / pnpm-lock.yaml
gem manifest → lock file
pyproject.toml → resolved lock
```

Ručná kombinácia môže vytvoriť syntakticky validný, ale nereprodukovateľný dependency graph.

## 20. Generované files

Pri generovanom súbore musí byť jasné:

- ktorý source ho vytvára,
- ktorá verzia generatora je autoritatívna,
- či je output deterministický,
- či sa má commitovať,
- ako sa validuje drift.

Resolution:

1. vyrieš source files,
2. spusti generator,
3. porovnaj output,
4. stage-ni source aj generated artifact,
5. over clean regeneration.

```bash
./generate.sh
git diff --check
git diff --exit-code -- generated/
```

## 21. YAML, JSON a konfigurácia

Textové zlúčenie structured data musí overiť aj štruktúru.

Kontroluj:

- duplicate keys,
- type zmeny,
- list ordering,
- anchor/alias semantics,
- implicitné YAML typy,
- defaults,
- environment overlays,
- secrets a access policy.

Použi parser/schema validáciu, nie iba vizuálne review.

```bash
yq '.' config.yaml >/dev/null
jq empty config.json
```

Konkrétny nástroj musí zodpovedať používanej implementácii a schema contractu.

## 22. Infrastructure as Code konflikty

Pri Terraform, Kubernetes, Helm alebo cloud policy konfliktoch nestačí syntax.

Over:

- rendered manifest,
- provider/module version,
- resource identity,
- destructive replacement,
- security group/policy scope,
- ordering dependencies,
- plan výsledok,
- environment-specific values.

Príklady:

```bash
terraform fmt -check
terraform validate
terraform plan

helm template ...
kubectl apply --dry-run=server -f ...
```

Textovo malá resolution môže vyvolať produkčné delete/recreate operácie.

## 23. Merge drivers a `.gitattributes`

`.gitattributes` môže definovať merge správanie:

```gitattributes
*.generated merge=generated
*.lock merge=lockfile
```

Custom driver konfigurácia:

```ini
[merge "generated"]
    driver = ./scripts/merge-generated %O %A %B %P
```

Placeholder význam závisí od Git driver contractu; nástroj musí byť:

- deterministický,
- dostupný v lokálnom aj CI prostredí,
- bezpečný pre nedôveryhodný obsah,
- jasne versionovaný,
- schopný signalizovať failure exit codom.

Tichý „úspešný“ driver môže skryť semantic conflict horšie než explicitný marker.

## 24. Built-in `ours` merge driver vs. merge strategy

Často zamieňané:

```gitattributes
file merge=ours
```

custom/built-in driver správanie pre konkrétnu path nie je to isté ako:

```bash
git merge -s ours other
```

Stratégia `ours` ignoruje celý tree druhej branch a iba vytvorí ancestry merge. Path-specific driver ovplyvňuje vybraný file počas content merge.

Oba mechanizmy môžu skryť zmeny, preto musia mať dokumentovaný dôvod.

## 25. Mergetool

```bash
git mergetool
git mergetool path/to/file
```

Mergetool môže zobraziť base, local, remote a merged output. Konfigurácia závisí od nástroja.

Po použití:

```bash
git status
git diff --staged
git diff --check
```

Niektoré tools vytvárajú backup files ako `.orig`; tie netreba omylom commitnúť.

GUI nástroj nemení význam konfliktu. Stále treba pochopiť intent a výsledný contract.

## 26. `rerere`

Reuse Recorded Resolution:

```bash
git config rerere.enabled true
git rerere status
git rerere diff
```

Git uloží:

- normalized conflict pre-image,
- zvolenú post-image resolution.

Pri podobnom konflikte môže resolution znovu aplikovať.

Výhody:

- opakované rebases,
- dlhodobé release branches,
- test merge pred finálnym merge,
- rollback a opätovná integrácia.

Riziko: rovnaký textový conflict shape nemusí mať rovnaký semantický význam. Rerere output vždy review-ni a testuj.

## 27. Semantic conflict checklist

Po textovej resolution sa pýtaj:

- Zachoval sa intent oboch zmien?
- Zmenil sa public API alebo schema contract?
- Sú migration a aplikácia kompatibilné v rollout poradí?
- Nevznikla duplicate initialization alebo handler registration?
- Nezmenila sa authorization alebo secret scope?
- Sú timeout, retry a rate-limit vrstvy stále konzistentné?
- Nezdvojnásobil sa resource limit alebo workload?
- Zodpovedajú tests novému kombinovanému správaniu?

Semantic review je samostatná fáza po odstránení markerov.

## 28. Overenie resolution

Git-level checks:

```bash
git status
git diff --name-only --diff-filter=U
git diff --check
git diff --staged
git ls-files -u
```

`git ls-files -u` musí byť prázdne pred dokončením.

Engineering checks:

- formatter,
- linter/parser,
- unit tests,
- integration tests,
- build,
- schema/migration validation,
- rendered IaC plan,
- behavior-specific smoke test.

Review-ni výsledok voči obom parentom:

```bash
git diff HEAD...other-branch
# po merge commite:
git show -m --stat HEAD
git show --cc HEAD
```

## 29. Abort a recovery

Pred integráciou:

```bash
git status
git branch backup/pre-integration
```

Abort podľa operácie:

```bash
git merge --abort
git rebase --abort
git cherry-pick --abort
git revert --abort
```

Stash apply nemá rovnaký univerzálny abort lifecycle; pred apply je preto vhodný clean state alebo recovery branch.

Po nesprávne dokončenej, nepublikovanej integrácii:

```bash
git reflog --date=iso
git branch recovery/bad-resolution HEAD
git reset --hard <old-tip>
```

Na publikovanej branch preferuj revert merge/result commitov pred history rewriteom.

## 30. Uchovanie dôkazov

Pred abortom alebo resetom môže byť užitočné uložiť:

```bash
git diff > /tmp/conflict-working.patch
git diff --staged > /tmp/conflict-staged.patch
git ls-files -u > /tmp/conflict-stages.txt
git status --porcelain=v2 > /tmp/conflict-status.txt
```

Pri komplexnom incidente zachovaj aj:

- pôvodné tip SHAs,
- merge base,
- operáciu a options,
- generator/package-manager verziu,
- test failures,
- resolution rationale.

Tým sa z konfliktu stane auditovateľná integračná udalosť.

## 31. Minimalizácia konfliktov

Konflikty znižujú:

- malé branches a batches,
- častá integrácia,
- jasné ownership boundaries,
- oddelenie mechanického refactoru od behavior zmeny,
- stabilné formatting pravidlá,
- deterministické generátory,
- modularizácia často menených centrálnych files,
- komunikácia zmien shared contracts,
- contract a integration tests,
- feature flags pre oddelenie deploy a enable fázy.

Cieľ nie je nulový počet konfliktov. Cieľ je menší, zrozumiteľný conflict scope a bezpečná resolution.

## 32. Bezpečný resolution workflow

```bash
git status
git diff --name-only --diff-filter=U
git ls-files -u

# pre každú path:
git show :1:path/to/file
git show :2:path/to/file
git show :3:path/to/file
# uprav výsledok
git add path/to/file

# globálne overenie
git diff --name-only --diff-filter=U
git diff --check
git diff --staged
# formatter, parser, tests, build, plan

# dokončenie podľa operácie
git rebase --continue
# alebo git commit / cherry-pick --continue / revert --continue
```

## 33. Troubleshooting

### Conflict markers zostali po commite

```bash
git grep -n -E '^(<<<<<<<|=======|>>>>>>>)'
```

Pozor: `=======` môže legitímne existovať v dokumentácii. Použi review a context, nie slepé odstránenie.

Prevencia:

- pre-commit check,
- CI grep s rozumným patternom,
- parser/build tests.

### Git hlási unmerged paths, ale file vyzerá vyriešený

File ešte nie je stage-nutý:

```bash
git ls-files -u
git add path
git status
```

Resolution je pre Git dokončená až stage-0 index entry, nie iba odstránenie markerov.

### `--ours` zobral nesprávnu verziu

Pravdepodobne ide o rebase/cherry-pick kontext. Obnov stages alebo abortni operáciu a inspect-ni `:2:`/`:3:` obsah pred ďalším výberom.

### Merge bez konfliktu rozbil tests

Ide o semantic conflict alebo chýbajúcu integration dependency. Porovnaj combined changes voči merge base a obom parentom, nie iba posledný textový diff.

### Lock file po resolution stále mení veľa dependencies

Over:

- verziu package managera,
- source manifest diff,
- registry/config policy,
- platform-specific resolution,
- deterministic install mode.

Náhodné ručné editovanie lock file pravdepodobne nie je správna náprava.

## 34. Časté omyly

### „Konflikt znamená, že Git nevie merge-ovať“

Nie. Git vedome odmietol uhádnuť nejednoznačný výsledok.

### „Správna resolution je jedna z dvoch strán“

Často treba vytvoriť tretiu verziu zachovávajúcu oba intenty.

### „Ours je vždy moja feature branch“

Nie. Význam závisí od operácie a current state.

### „Žiadne markery znamenajú žiadny konflikt“

Binary, rename, submodule a semantic konflikty nemusia mať klasické markery.

### „Rename je uložený v commite“

Git ho odvodzuje z podobnosti snapshots.

### „Lock file stačí zlúčiť textovo“

Má sa regenerovať z resolved source declarations podporovaným nástrojom.

### „`git add` potvrdzuje funkčnú správnosť“

Potvrdzuje iba výslednú index entry.

### „Rerere resolution už netreba reviewnúť“

Treba. Automaticky zopakovaná textová resolution môže byť semanticky zastaraná.

## 35. Kontrolné otázky

1. Čo znamenajú index stages 1, 2 a 3?
2. Prečo konflikt nie je poškodenie repository?
3. Ako sa mení význam ours/theirs pri rebase?
4. Aké konflikty nemusia mať textové markery?
5. Ako Git deteguje rename?
6. Ako vyriešiš modify/delete konflikt podľa intentu?
7. Prečo sa lock file typicky regeneruje?
8. Čo je semantic conflict?
9. Ako combined diff pomáha pri review merge commitu?
10. Ako overíš, že resolution je Git-level aj funkčne dokončená?

## Glossary impact

Relevantné pojmy: merge conflict, semantic conflict, merge base, index stage, unmerged entry, ours, theirs, conflict marker, diff3, combined diff, rename detection, directory/file conflict, merge driver, mergetool, rerere.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Cherry-pick a stash](cherry-pick-and-stash.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Branching strategies →](branching-strategies.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
