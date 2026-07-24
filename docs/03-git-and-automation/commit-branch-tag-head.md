# Commit, branch, tag a HEAD

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Git and Automation Basics
- Predpoklady: [Git object model](git-object-model.md), [Working tree, staging area a repository](working-tree-staging-repository.md)
- Súvisiace témy: refs, detached HEAD, annotated tags, ancestry, reflog

## 1. Definícia

Commit, branch, tag a `HEAD` patria do dvoch odlišných vrstiev Git modelu:

```text
immutable object graph
  commit
  annotated tag object

mutable naming layer
  branch ref
  tag ref
  remote-tracking ref
  symbolic ref HEAD
```

Ich základný význam:

```text
commit  nemenný snapshot + parents + metadata
branch  pohyblivý ref, typicky na tip vývojovej línie
tag     pomenovanie stabilného bodu alebo objektu
HEAD    aktuálny checkout context
```

Branch nie je adresár s commitmi a commit nepozná názov branch. Refs iba poskytujú mená vstupným bodom do commit graphu.

## 2. Commit ako nemenný graph node

Commit object obsahuje:

- root tree,
- zero alebo viac parent commitov,
- author identity a time,
- committer identity a time,
- commit message,
- prípadné signature headers.

```bash
git cat-file -p HEAD
git show --no-patch --pretty=raw HEAD
```

Keď sa zmení parent, tree, message alebo commit metadata, vznikne nové commit ID. Existujúci commit sa neprepíše.

Preto:

- `commit --amend` vytvorí nový commit,
- rebase vytvára nové commits s novými parentmi,
- cherry-pick vytvára nový commit z aplikovaného patchu,
- rovnaký source tree môže patriť viacerým commitom.

## 3. Author a committer

Author opisuje pôvodného tvorcu zmeny. Committer opisuje aktéra, ktorý zostavil konkrétny commit object v aktuálnej histórii.

```bash
git log --format=fuller -1
```

Pri normálnom lokálnom commite sú často rovnakí. Pri rebase alebo cherry-pick môže author zostať pôvodný, ale committer, committer time a parent chain sa zmenia.

Tieto identity sú textové metadata. Bez kryptografického podpisu ich možno deklarovať ľubovoľne.

## 4. Branch ako ref

Local branch je ref pod:

```text
refs/heads/<branch-name>
```

Príklad:

```text
refs/heads/main → commit C
```

Nový commit na checkoutnutej branchi vytvorí nový commit a atomicky posunie ref:

```text
predtým: main → C

nový commit D, parent C

potom:  main → D → C
```

```bash
git branch --show-current
git show-ref --heads
git rev-parse refs/heads/main
```

Branch nevlastní osobitnú kópiu files. Vytvorenie branch je lacný ref update.

## 5. Ref storage

Refs môžu byť uložené:

- ako files pod `.git/refs/...`,
- v `.git/packed-refs`,
- v backend-e, ktorý Git používa pre ref storage.

Preto sa refs nemajú spoľahlivo zisťovať iba čítaním directory.

Používaj:

```bash
git show-ref
git for-each-ref
git rev-parse <ref>
```

Pri bezpečnom programovom update:

```bash
git update-ref refs/heads/main <new-id> <expected-old-id>
```

`expected-old-id` poskytuje compare-and-swap ochranu pred prepísaním refu, ktorý medzitým zmenil iný proces.

## 6. Validita názvu branch

Git ref names majú syntaktické pravidlá. Branch name nesmie obsahovať určité sekvencie alebo viesť k nejednoznačnej revision syntax.

```bash
git check-ref-format --branch 'feature/api-timeout'
```

Dobrý názov branch vyjadruje účel, no nie je súčasťou commit object identity. Rename branch preto nemení commits.

```bash
git branch -m old-name new-name
```

Remote branch sa tým automaticky nepremenuje; treba push nového refu a prípadne delete starého.

## 7. Vytvorenie branch

Vytvorenie bez checkoutu:

```bash
git branch feature/api-timeout <start-point>
```

Vytvorenie a prepnutie:

```bash
git switch -c feature/api-timeout <start-point>
```

Objekty sa nekopírujú. Nová branch a pôvodný ref môžu ukazovať na rovnaký commit:

```text
main    ─┐
feature ─┴→ C
```

Až ďalšie commits vytvoria divergenciu.

## 8. `HEAD` ako checkout context

V bežnom stave je `HEAD` symbolic ref:

```text
HEAD → refs/heads/main → commit D
```

```bash
git symbolic-ref HEAD
git rev-parse HEAD
git branch --show-current
```

Pri `git commit` Git:

1. vytvorí nový commit s parentom `HEAD`,
2. posunie branch ref, na ktorý `HEAD` symbolicky ukazuje,
3. aktualizuje reflog branch a `HEAD`.

`HEAD` teda určuje, ktorý ref sa pri commite posúva.

## 9. Unborn branch

Po `git init` môže `HEAD` symbolicky ukazovať na branch, ktorá ešte nemá commit:

```text
HEAD → refs/heads/main
refs/heads/main ešte neexistuje
```

Tento stav sa nazýva unborn branch.

```bash
git symbolic-ref HEAD
git rev-parse --verify HEAD
```

`git rev-parse --verify HEAD` zlyhá, pretože commit ešte neexistuje, hoci branch name je známy.

Prvý commit vytvorí root commit bez parenta a založí branch ref.

## 10. Detached HEAD

Detached `HEAD` ukazuje priamo na commit:

```text
HEAD → commit B
```

Vznikne napríklad:

```bash
git switch --detach <commit>
git switch --detach v1.2.0
```

Je to validný stav vhodný na:

- build historického commitu,
- read-only inspection,
- experiment,
- bisect,
- CI checkout konkrétneho SHA.

Nové commits sa vytvoria, ale neposúvajú bežnú branch.

## 11. Zachovanie detached práce

Pred odchodom z detached `HEAD`:

```bash
git switch -c experiment/from-detached
```

Ak už používateľ odišiel:

```bash
git reflog --all
git branch recovery/detached <commit-id>
```

Commit nie je okamžite zmazaný, ale bez refu alebo reflog retention sa môže stať unreachable a po GC zaniknúť.

## 12. Branch switch ako viacvrstvová operácia

`git switch target` nemení iba `HEAD`. Git musí zosúladiť:

- symbolic `HEAD`,
- index,
- working tree.

Ak by checkout prepísal necommitnutú zmenu, Git ho typicky odmietne.

```bash
git status --short
git switch target
```

Možnosti:

- commitnúť,
- stashnúť,
- vytvoriť ďalší worktree,
- vedome zahodiť lokálne zmeny.

Branch switch nie je iba ref pointer change, pretože používateľ očakáva materializovaný target snapshot.

## 13. Tag ref

Tag ref je pod:

```text
refs/tags/<name>
```

Tag môže odkazovať na ľubovoľný Git object, hoci releases typicky označujú commit.

```bash
git show-ref --tags
git rev-parse refs/tags/v1.2.0
```

Tag sa z konvencie používa ako stabilné pomenovanie verzie. Technicky je ref mutable, ak policy update nezakáže.

## 14. Lightweight tag

Lightweight tag je ref priamo na target object:

```bash
git tag v1.2.0 <commit>
```

Model:

```text
refs/tags/v1.2.0 → commit C
```

Neobsahuje vlastného taggera, message ani tag-object podpis.

Je vhodný pre dočasné lokálne značky, no pre oficiálny release často chýba audit metadata.

## 15. Annotated tag

Annotated tag vytvorí tag object:

```bash
git tag -a v1.2.0 -m 'release v1.2.0'
```

Model:

```text
refs/tags/v1.2.0 → tag object T → commit C
```

Tag object obsahuje:

- target object ID,
- target type,
- tag name,
- tagger identity a time,
- message,
- voliteľný signature block.

```bash
git cat-file -p v1.2.0
git show v1.2.0
```

## 16. Tag peeling

Niektoré príkazy potrebujú dereferencovať annotated tag na target:

```bash
git rev-parse v1.2.0
git rev-parse v1.2.0^{}
git rev-parse v1.2.0^{commit}
```

- Bez suffixu môže výsledok byť tag object ID.
- `^{}` rekurzívne dereferencuje tag object.
- `^{commit}` zároveň overí, že target sa dá interpretovať ako commit.

Pri automatizácii release artifactu je dôležité vedieť, či sa eviduje tag object alebo peeled commit.

## 17. Tag mutability a release contract

Git technicky dovolí tag presunúť:

```bash
git tag -f v1.2.0 <new-commit>
git push --force origin refs/tags/v1.2.0
```

Publikovaný tag však môže byť súčasťou:

- artifact versioningu,
- package provenance,
- deployment manifestu,
- SBOM,
- zákazníckeho release contractu.

Presun tagu spôsobí, že rovnaký názov označuje iný source. Stabilitu preto zabezpečujú server permissions, immutable release policy a podpisy, nie samotná Git syntax.

Bezpečnejšie je vydať nový tag, napríklad `v1.2.1`, než prepísať `v1.2.0`.

## 18. Branch verzus tag lifecycle

Branch je typicky pohyblivá:

```text
main → C → neskôr D → neskôr E
```

Release tag je typicky stabilný:

```text
v1.2.0 → C navždy
```

Obe sú refs. Rozdiel je policy a význam.

Branch deletion môže byť normálna po merge. Tag deletion môže zmeniť release discoverability a audit trail.

## 19. Remote branch a remote-tracking ref

Server môže mať branch:

```text
refs/heads/main
```

Lokálny clone jej stav po fetchi eviduje ako remote-tracking ref:

```text
refs/remotes/origin/main
```

`origin/main` nie je live query na server. Je lokálna cache posledného úspešne fetchnutého stavu.

```bash
git fetch origin
git rev-parse origin/main
git ls-remote origin refs/heads/main
```

`git ls-remote` sa pýta servera; `origin/main` číta lokálny ref.

## 20. Remote name nie je server branch

`origin` je lokálny názov remote konfigurácie:

```bash
git remote -v
git config --get-regexp '^remote\.'
```

Obsahuje URL a fetch refspec. Názov `origin` nemá špeciálnu serverovú identitu a možno ho premenovať:

```bash
git remote rename origin upstream
```

Remote-tracking refs sa spravujú podľa konfigurácie fetchu, nie podľa magického globálneho namespace.

## 21. Upstream branch

Local branch môže mať nakonfigurovaný upstream:

```bash
git branch --set-upstream-to=origin/main main
git branch -vv
```

Konfigurácia typicky používa:

```text
branch.main.remote
branch.main.merge
```

Upstream ovplyvňuje:

- ahead/behind v `git status`,
- default target `git pull`,
- default push behavior podľa `push.default`,
- `@{upstream}` revision syntax.

```bash
git rev-parse '@{upstream}'
git log --left-right --graph HEAD...@{upstream}
```

Upstream nie je parent relation v commit objecte. Je to local configuration pre synchronizačný workflow.

## 22. Push remote verzus upstream

Branch môže fetchovať/upstreamovať z jedného remote a pushovať na iný.

Relevantné nastavenia môžu zahŕňať:

- `branch.<name>.remote`,
- `branch.<name>.merge`,
- `branch.<name>.pushRemote`,
- `remote.pushDefault`,
- `push.default`.

```bash
git remote get-url --push origin
git config --get push.default
git config --get branch.main.pushRemote
```

Pred automatizovaným pushom je bezpečnejšie uviesť explicitný remote a refspec.

## 23. Fast-forward update

Ref update je fast-forward, ak starý tip je ancestor nového tipu.

```text
A---B---C old
         \
          D---E new
```

```bash
git merge-base --is-ancestor <old> <new>
```

Fast-forward zachová všetky commits, ktoré boli reachable zo starého refu. Ref sa iba posunie dopredu po existujúcom graph path.

Server typicky povoľuje fast-forward branch updates, ak ďalšia policy nevyžaduje pull request alebo checks.

## 24. Non-fast-forward update

Non-fast-forward update posunie ref na commit, z ktorého starý tip nie je reachable.

```text
      C---D old
     /
A---B---E new
```

Po update commits `C` a `D` prestanú byť viditeľné z branch refu.

Vzniká pri:

- rebase publikovanej branch,
- reset branch dozadu,
- nahradení histórie iným graphom,
- force pushi.

Neznamená automaticky stratu objektov, ale mení zdieľaný contract ancestry.

## 25. `--force` verzus `--force-with-lease`

Slepý force push:

```bash
git push --force origin feature
```

povie serveru, aby prijal non-fast-forward update bez ochrany pred novou prácou iného používateľa.

Bezpečnejší variant:

```bash
git push --force-with-lease origin feature
```

overí očakávaný remote stav. Ak server branch medzitým posunul niekto iný, push sa odmietne.

Presný lease možno uviesť explicitne:

```bash
git push --force-with-lease=refs/heads/feature:<expected-id> origin feature
```

`--force-with-lease` nezaručuje, že rewrite je organizačne povolený alebo že nikto nepostavil artifact zo starej histórie. Chráni pred konkrétnym lost-update scenárom.

## 26. Atomic ref updates

Niektoré operácie potrebujú aktualizovať viac refs ako jeden celok.

```bash
git push --atomic origin main v1.2.0
```

Ak server atomic push podporuje, buď sa prijmú všetky ref updates, alebo žiadny. To je dôležité napríklad pri koordinovanom pushi release branch a tagu.

Bez atomicity môže jeden ref uspieť a druhý zlyhať, čím vznikne neúplný release state.

## 27. Branch deletion

Local branch:

```bash
git branch -d feature
git branch -D feature
```

- `-d` kontroluje, či je branch tip integrovaný podľa Git ancestry pravidiel.
- `-D` vynúti delete bez tejto ochrany.

Remote branch:

```bash
git push origin --delete feature
```

Delete odstráni ref, nie okamžite commits. Recovery môže byť možná cez:

- reflog local branch/HEAD,
- inú branch alebo tag,
- remote clone,
- pull request ref,
- server audit/retention.

## 28. Branch containment nie je ownership

```bash
git branch --contains <commit>
git tag --contains <commit>
```

Branch „contains“ commit, ak je commit reachable z jej tipu cez parent graph.

Rovnaký commit môže byť contained v mnohých branches. Branch nevlastní commit a merge commit môže sprístupniť celú ancestry feature branch v `main`.

## 29. Revision ranges

Dôležité expressions:

```text
A..B   commits reachable z B, nie z A
A...B  commits reachable z jedného, nie z oboch; symmetric difference
```

```bash
git log main..feature
git log --left-right main...feature
git diff main...feature
```

Pozor: `git diff A...B` typicky porovná merge base s B, čo nie je rovnaký význam ako symmetric-difference commit set v `git log`.

Pri diagnostike treba uviesť konkrétny príkaz, nie iba zápis troch bodiek.

## 30. Parent revision syntax

```text
HEAD^    prvý parent
HEAD^2   druhý parent merge commitu
HEAD~3   trikrát first parent
```

```bash
git rev-parse HEAD^
git rev-parse HEAD^2
git rev-parse HEAD~3
```

Pri lineárnej histórii môžu niektoré výsledky pôsobiť rovnako. Pri merge grafe sú rozdiely zásadné.

## 31. Reflog branch a `HEAD`

Reflog zaznamenáva lokálne ref transitions:

```bash
git reflog
git reflog show main
git reflog show --all
```

`HEAD` reflog zachytáva checkout context changes, commits, rebases a resets. Branch reflog zachytáva pohyby konkrétneho branch refu.

Revision syntax:

```bash
git show HEAD@{1}
git show main@{yesterday}
```

Timestamp lookup závisí od reflog entries a local clock.

## 32. Recovery po reset/rebase/delete

Typický postup:

1. zastav ďalšie rewrite a GC,
2. pozri reflog:

```bash
git reflog --date=iso
```

3. identifikuj správny commit,
4. vytvor recovery branch:

```bash
git branch recovery/lost-work <commit-id>
```

5. porovnaj snapshots a ancestry,
6. až potom oprav pôvodný branch ref.

Recovery branch vytvorí stabilný ref a chráni commit pred neskoršou GC.

## 33. Reflog limity

Reflog:

- je prevažne lokálny,
- nie je súčasť bežného fetch/push protokolu,
- má expiration policy,
- môže byť vypnutý alebo odlišný v bare/server repository,
- nemusí zachytiť zmenu vykonanú mimo ref update mechanizmu pri manuálnom poškodení files.

Pre zdieľanú obnovu sú dôležité remote refs, backups, pull request refs a server audit logs.

## 34. Signed commits

Commit možno podpísať:

```bash
git commit -S -m 'change'
git verify-commit HEAD
```

Podpis sa stane súčasťou commit objectu, a teda ovplyvní commit ID.

Overenie musí riešiť:

- kryptografickú validitu,
- mapping key → osoba alebo workload,
- key expiry/revocation,
- policy, ktoré identity sú povolené,
- ochranu branch refu po podpise.

Podpísaný commit môže byť neskôr odstránený force pushom, ak branch policy tomu nezabráni.

## 35. Signed annotated tags

```bash
git tag -s v1.2.0 -m 'release v1.2.0'
git verify-tag v1.2.0
```

Tag signature chráni tag object a target object ID. Ak sa tag ref presunie na iný tag object, starý podpis môže zostať kryptograficky validný, ale názov tagu už označuje nový objekt.

Release verification preto potrebuje:

- očakávaný tag name,
- tag object/signature,
- peeled commit ID,
- server/ref provenance,
- artifact provenance.

## 36. Notes a metadata mimo commit identity

Git notes umožňujú pridať metadata ku commitom bez zmeny commit objectu:

```bash
git notes add -m 'reviewed by security' <commit>
git notes show <commit>
```

Notes sú samostatné refs, napríklad `refs/notes/commits`. Neprenášajú sa vždy automaticky a ich trust model je oddelený.

Nie sú náhradou required review alebo immutable provenance policy, ak server notes ref nechráni.

## 37. Namespaces a hidden refs

Server alebo tooling môže používať refs mimo bežných heads/tags:

```text
refs/pull/...       pull request refs
refs/changes/...    review system refs
refs/replace/...    replacement objects
refs/notes/...      notes
```

```bash
git for-each-ref
git show-ref
```

`git branch` a `git tag` nezobrazujú všetky ref namespaces. Pri reachability alebo recovery analýze treba vedieť, ktoré refs existujú.

## 38. Symbolic refs mimo `HEAD`

Git môže technicky používať symbolic refs aj mimo `HEAD`, hoci bežný workflow sa sústreďuje na `HEAD`.

```bash
git symbolic-ref refs/heads/current refs/heads/main
```

Takéto riešenia môžu byť nekompatibilné s očakávaniami nástrojov. Pre štandardný branch workflow sa používajú direct refs.

## 39. Practical graph inspection

```bash
git log --graph --oneline --decorate --all
git show-ref
git for-each-ref --format='%(refname) %(objecttype) %(objectname)'
git branch -vv
git tag -n
git reflog --all --date=iso
```

`--decorate` zobrazuje mená refs pri graph nodes. Commity sú tie isté objects bez ohľadu na to, koľko refs ich označuje.

## 40. Diagnostika: „nie som na branchi“

```bash
git status
git branch --show-current
git symbolic-ref -q HEAD || echo detached
git rev-parse HEAD
git reflog -10
```

Ak je práca dôležitá:

```bash
git switch -c recovery/current-work
```

Najprv vytvor ref. Až potom rieš, kam commit zaradiť merge/rebase/cherry-pick operáciou.

## 41. Diagnostika: local branch sa nezhoduje s remote

Najprv obnov lokálnu informáciu:

```bash
git fetch origin
```

Potom:

```bash
git branch -vv
git log --graph --oneline --left-right main...origin/main
git merge-base main origin/main
git rev-list --left-right --count main...origin/main
```

Rozlíš:

- local branch `main`,
- local remote-tracking ref `origin/main`,
- aktuálny server ref cez `git ls-remote`,
- configured upstream,
- working tree a index stav.

## 42. Diagnostika: force push bol odmietnutý

Otázky:

- Je server branch protected?
- Používa sa správny remote a refspec?
- Zmenil remote branch niekto iný?
- Je lease založený na aktuálnom remote-tracking refe?
- Je rewrite vôbec povolený workflowom?

```bash
git fetch origin
git log --left-right --graph HEAD...origin/feature
git ls-remote origin refs/heads/feature
```

Ak rewrite je oprávnený, explicitný lease viazaný na overené ID je presnejší než slepé `--force`.

## 43. Diagnostika: tag ukazuje iný commit u kolegu

```bash
git rev-parse v1.2.0
git rev-parse v1.2.0^{}
git ls-remote --tags origin v1.2.0
git show --no-patch --decorate v1.2.0
```

Možné príčiny:

- tag bol presunutý,
- local tag nebol fetchovaný alebo prepísaný,
- lightweight verzus annotated tag confusion,
- kolega používa iný remote,
- tag name je ambiguous s iným refom.

Publikovaný tag conflict sa nemá vyriešiť tichým force updateom bez release incident procesu.

## 44. Failure modes

### Commit je podpísaný, ale branch history nie je dôveryhodná

Branch ref mohol byť force-updatovaný alebo server policy obídená. Object signature a ref governance sú odlišné vrstvy.

### `origin/main` je starý

Remote-tracking ref sa aktualizuje fetchom, nie automaticky pri každom server update.

### Branch delete údajne zmazal commits

Odstránil ref. Commity môžu byť reachable z iných refs alebo reflogu.

### Tag checkout vytvoril detached HEAD

Tag nie je local branch. Je to očakávané správanie.

### `git branch -d` odmieta delete po squash merge

Squash commit nemá ancestry pôvodných feature commitov. Obsah môže byť integrovaný, ale graph containment check neprejde.

### `--force-with-lease` zlyhá po fetchi vykonanom background toolom

Implicitný lease môže byť založený na remote-tracking refe, ktorý background fetch posunul. Pri kritickom rewrite používaj explicitné expected ID.

## 45. Časté omyly

### „Branch obsahuje commits“

Branch je ref na tip. História je parent graph reachable z tipu.

### „Commit patrí jednej branchi“

Rovnaký commit môže byť reachable z mnohých branches a tags.

### „Tag je nemenný objekt“

Annotated tag object je nemenný, ale tag ref možno technicky presunúť.

### „`HEAD` je vždy branch“

`HEAD` môže byť symbolic ref, direct detached commit alebo unborn branch context.

### „`origin/main` je server“

Je lokálny remote-tracking ref aktualizovaný fetchom.

### „Force-with-lease je úplne bezpečný“

Chráni pred určitým lost-update scenárom, nie pred organizačne nesprávnym history rewrite.

### „Signed tag dokazuje, že artifact je správny“

Dokazuje podpis tag objectu. Artifact build a provenance sú ďalšie kroky.

## 46. Diagnostický checklist

Pri probléme s branch/tag/HEAD zisti:

- Na čo presne ukazuje `HEAD`?
- Je branch born, unborn alebo detached context?
- Ktorý local ref sa posúva pri commite?
- Aký je upstream a push remote?
- Je `origin/main` čerstvý po fetchi?
- Aký je server ref podľa `ls-remote`?
- Je update fast-forward?
- Ktoré commits by non-fast-forward update odstránil z visible ancestry?
- Existuje reflog recovery point?
- Ide o lightweight alebo annotated tag?
- Aký je tag object ID a peeled commit ID?
- Sú signatures validné a identities trusted?
- Chráni server branch/tag refs pred neoprávneným updateom?

## 47. Zhrnutie

Commit je nemenný graph node. Branch je pohyblivý ref. Tag je ref používaný ako stabilné pomenovanie a môže smerovať priamo na commit alebo na annotated tag object. `HEAD` určuje aktuálny checkout context a pri normálnej práci symbolicky ukazuje na local branch.

Kľúčový model:

```text
HEAD → local branch → commit graph
remote-tracking ref → posledný fetchnutý serverový stav
tag ref → commit alebo tag object → target
```

Keď sa oddelí objektový graf od naming vrstvy, detached HEAD, force push, branch deletion, tag peeling, upstream a reflog recovery sa dajú vysvetliť ako explicitné pohyby refs, nie ako záhadné zmeny „obsahu branch“.

## 48. Kontrolné otázky

1. Aký je rozdiel medzi commit objectom a branch refom?
2. Čo presne posunie `git commit` pri symbolic `HEAD`?
3. Čo je unborn branch?
4. Ako sa správa detached `HEAD` pri novom commite?
5. Aký je rozdiel medzi lightweight a annotated tagom?
6. Čo znamená tag peeling?
7. Prečo publikovaný tag nie je automaticky immutable?
8. Aký je rozdiel medzi server branch a remote-tracking refom?
9. Čo presne konfiguruje upstream branch?
10. Kedy je ref update fast-forward?
11. Čo chráni `--force-with-lease` a čo nechráni?
12. Prečo môže `git branch -d` odmietnuť branch po squash merge?
13. Ako reflog umožní recovery po resete alebo delete branch?
14. Čo podpis commit/tagu dokazuje a aké trust vrstvy ešte chýbajú?

## Glossary impact

Relevantné pojmy: commit object, branch ref, direct ref, symbolic ref, HEAD, unborn branch, detached HEAD, lightweight tag, annotated tag, tag peeling, remote, remote-tracking ref, upstream branch, push remote, fast-forward, non-fast-forward, force-with-lease, atomic push, reflog, ref namespace, signed commit, signed tag.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Working tree, staging area a repository](working-tree-staging-repository.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Clone, fetch, pull a push →](clone-fetch-pull-push.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
