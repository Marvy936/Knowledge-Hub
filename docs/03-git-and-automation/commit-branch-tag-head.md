# Commit, branch, tag a HEAD

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Git and Automation Basics
- Predpoklady: [Git object model](git-object-model.md), [Working tree, staging area a repository](working-tree-staging-repository.md)
- Súvisiace témy: refs, detached HEAD, annotated tags, ancestry, reflog

## 1. Štyri rozdielne koncepty

```text
commit  nemenný snapshot a metadata
branch  pohyblivý ref na commit
tag     stabilný ref, typicky označenie verzie
HEAD    aktuálna checkout pozícia
```

Ich zamieňanie vedie k chybnému chápaniu histórie a nebezpečným operáciám.

## 2. Commit

Commit objekt obsahuje root tree, parents, identities, timestamps a message.

```bash
git show --stat HEAD
git cat-file -p HEAD
```

Commit ID sa zmení pri zmene ľubovoľného commit obsahu vrátane message alebo parenta. Preto rebase a amend vytvárajú nové commits aj vtedy, keď výsledné files vyzerajú rovnako.

## 3. Author vs. committer

- author: kto pôvodne vytvoril zmenu,
- committer: kto vytvoril konkrétny commit objekt.

Pri rebase môže author zostať, ale committer a commit ID sa zmenia.

```bash
git log --format=fuller -1
```

## 4. Branch

Lokálna branch je ref pod:

```text
refs/heads/<name>
```

Branch ukazuje na tip commit. Pri novom commite sa aktuálna branch posunie.

```text
main → C

nový commit D

main → D
       parent → C
```

```bash
git branch
git branch --show-current
git show-ref --heads
```

Branch neobsahuje vlastnú kópiu files ani izolovaný adresár.

## 5. Vytvorenie a prepnutie branch

```bash
git switch -c feature/api-timeout
git switch main
git branch feature/api-timeout <start-point>
```

Nová branch je iba nový ref. Objects sa nekopírujú.

Názov branch má byť zmysluplný, ale nie je súčasťou commit identity.

## 6. HEAD

Normálny stav:

```text
HEAD → refs/heads/main → commit D
```

```bash
git symbolic-ref HEAD
```

Pri commite Git posunie ref, na ktorý HEAD symbolicky ukazuje.

## 7. Detached HEAD

Detached HEAD:

```text
HEAD → commit B
```

Vznikne napríklad:

```bash
git switch --detach <commit>
git checkout <tag>
```

Commity vytvorené v detached stave existujú, ale po odchode nemusia byť dostupné cez branch ref.

Bezpečné zachovanie:

```bash
git switch -c experiment/from-detached
```

Ak už commit „zmizol“:

```bash
git reflog
git branch recovery <commit-id>
```

## 8. Tag

Lightweight tag je ref priamo na objekt:

```bash
git tag v1.2.0 <commit>
```

Annotated tag vytvára tag object s taggerom, časom, message a možným podpisom:

```bash
git tag -a v1.2.0 -m 'release v1.2.0'
git show v1.2.0
```

Pre releases sa zvyčajne preferuje annotated alebo signed tag.

## 9. Tag nie je automaticky immutable

Git technicky umožňuje tag presunúť alebo zmazať:

```bash
git tag -f v1.2.0 <new-commit>
git tag -d v1.2.0
git push origin :refs/tags/v1.2.0
```

Takýto zásah mení release contract. Stabilitu zabezpečuje organizačná policy, permissions a release proces, nie samotný názov „tag“.

## 10. Remote-tracking refs

```text
refs/remotes/origin/main
```

`origin/main` je lokálna evidencia posledného fetchnutého stavu remote branch. Nie je to live query na server.

```bash
git fetch origin
git log --oneline main..origin/main
```

## 11. Upstream branch

Lokálna branch môže mať upstream:

```bash
git branch --set-upstream-to=origin/main main
git branch -vv
```

Upstream ovplyvňuje default správanie príkazov ako `git pull`, `git push`, `git status` ahead/behind výpočet.

## 12. Revision syntax

```text
HEAD^     prvý parent
HEAD^2    druhý parent merge commitu
HEAD~3    trikrát prvý parent
main^{}
v1.2.0^{} dereference annotated tag
```

```bash
git rev-parse HEAD~2
git show main:path/to/file
```

`^` a `~` nie sú ľubovoľné synonymá. Pri merge grafe vyjadrujú odlišné traversovanie.

## 13. Reachability a ancestry

```bash
git merge-base --is-ancestor A B
git branch --contains <commit>
git tag --contains <commit>
```

Branch „obsahuje“ commit, ak je commit reachable z jej tip-u cez parents.

## 14. Force update refs

Bežný branch update je fast-forward, keď starý tip je ancestor nového tip-u.

```text
A---B  old
     \
      C  new
```

Non-fast-forward update odstraňuje commits z branch-visible ancestry a server ho často blokuje.

```bash
git push --force-with-lease
```

`--force-with-lease` kontroluje očakávaný remote stav a je bezpečnejší než slepý `--force`, ale stále prepisuje zdieľanú históriu.

## 15. Reflog

Reflog eviduje lokálne pohyby refs a HEAD:

```bash
git reflog
git reflog show main
```

Umožňuje obnoviť commit po reset/rebase/delete branch, pokiaľ ešte nebol expirovaný a odstránený garbage collection.

Remote server nemusí poskytovať používateľovi ekvivalentný reflog.

## 16. Signed commits a tags

Kryptografický podpis môže preukázať, že objekt podpísal držiteľ konkrétneho kľúča.

```bash
git commit -S
git tag -s v1.2.0 -m 'release'
git verify-commit HEAD
git verify-tag v1.2.0
```

Dôvera stále vyžaduje správne mapovanie key identity, key lifecycle a policy enforcement.

## 17. Praktický graf

```bash
git log --graph --oneline --decorate --all
git show-ref
git branch -vv
git tag -n
```

`--decorate` vizualizuje refs okolo commit graphu. Commity zostávajú rovnaké objekty bez ohľadu na počet refs, ktoré na ne ukazujú.

## 18. Troubleshooting

### „Nie som na žiadnej branch“

```bash
git status
git rev-parse --abbrev-ref HEAD
git reflog -10
```

Ak chceš zachovať aktuálne commits:

```bash
git switch -c recovery/work
```

### Branch sa nezhoduje s remote

```bash
git fetch origin
git branch -vv
git log --graph --oneline --left-right main...origin/main
```

Najprv odlíš lokálny ref, remote-tracking ref a serverový ref.

## 19. Časté omyly

### „Branch obsahuje commits“

Branch je ref na tip; commits sú prepojené cez parents.

### „Tag sa nikdy nedá zmeniť“

Dá, ale zmena publikovaného tagu je závažné porušenie release integrity.

### „`origin/main` je aktuálny serverový stav“

Je aktuálny iba k poslednému fetchu.

### „Detached HEAD znamená poškodený repository“

Nie. Je to validný stav, iba commits nemajú automaticky branch ref.

## 20. Kontrolné otázky

1. Aký je rozdiel medzi commitom a branchou?
2. Ako sa HEAD správa v normálnom a detached stave?
3. Aký je rozdiel medzi lightweight a annotated tagom?
4. Prečo amend vytvorí nové commit ID?
5. Čo je remote-tracking ref?
6. Čo znamená fast-forward update?
7. Ako reflog pomáha pri recovery?
8. Čo podpis commit/tag dokazuje a čo nedokazuje?

## Glossary impact

Relevantné pojmy: branch, tag, annotated tag, HEAD, detached HEAD, ref, remote-tracking ref, upstream branch, fast-forward, reflog.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Working tree, staging area a repository](working-tree-staging-repository.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Clone, fetch, pull a push →](clone-fetch-pull-push.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
