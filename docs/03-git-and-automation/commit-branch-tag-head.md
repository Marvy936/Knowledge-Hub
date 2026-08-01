# Commit, branch, tag a HEAD

Po pripravení indexu vytvorí Alice commit pre `ORD-8421`. Commit je immutable snapshot s parentom. Branch je pohyblivý ref. HEAD opisuje, čo je aktuálne checkoutnuté. Tag pomenúva konkrétny release subject. Tieto pojmy sa často zobrazujú v jednom logu, ale majú odlišný lifecycle.

## Commit z indexu

```bash
git commit -m 'ORD-8421 add maximum order amount'
```

Git vytvorí tree z indexu, commit object s parentom `HEAD` a potom posunie aktuálnu branch. Working-tree zmeny, ktoré neboli staged, commit neobsahuje.

```bash
git show --stat --decorate HEAD
git cat-file -p HEAD
git rev-parse HEAD^{tree}
```

Commit message má vysvetliť intent a dôvod, nie iba zopakovať diff. Issue ID pomáha traceability, ale nenahrádza zmysluplný subject.

## Branch je ref, nie kópia repository

```bash
git switch -c feature/ord-8421
```

Nová branch spočiatku ukazuje na rovnaký commit ako pôvodná. Vytvorenie branch nekopíruje files ani objekty. Keď vznikne nový commit, posunie sa iba aktuálna branch.

```text
main    → C3
feature → C4 → C3
```

Branch name môže byť odstránený bez okamžitého odstránenia commitov, ak sú dostupné iným refom alebo reflogom. Delete je preto ref mutation, nie okamžité zmazanie histórie.

## HEAD symbolický a detached

Bežne HEAD obsahuje symbolický odkaz:

```bash
git symbolic-ref HEAD
```

Výsledok môže byť `refs/heads/feature/ord-8421`. Pri checkout-e konkrétneho commitu alebo tagu je HEAD detached:

```bash
git switch --detach v4.1.0
```

Nové commits v detached stave existujú, ale neposúva sa branch ref. Pred odchodom treba vytvoriť branch alebo commit zachovať iným refom:

```bash
git switch -c investigation/from-v4.1.0
```

Detached HEAD nie je chyba; je to explicitný state vhodný pre build, bisect alebo investigation. Riziko vzniká, keď používateľ nevie, že commit nie je na branchi.

## Amend vytvára nový commit

```bash
git commit --amend
```

Amend nemení existujúci commit. Vytvorí nový commit s novým ID a posunie branch. Ak bol pôvodný commit publikovaný, amend je history rewrite a vyžaduje coordination.

```text
pred: feature → C4 → C3
po:   feature → C4' → C3
```

C4 môže určitý čas zostať v reflogu. Review comments alebo CI evidence viazané na C4 nemusia automaticky platiť pre C4'.

## Tag ako release identity

Lightweight tag je jednoduchý ref:

```bash
git tag build-test
```

Annotated tag je vhodnejší pre release:

```bash
git tag -a v4.2.0 -m 'Atlas Orders 4.2.0'
git show v4.2.0
```

Signed tag pridáva cryptographic provenance, ale dôveryhodnosť závisí od key managementu a verification policy. Tag sa nemá presúvať na nový commit po publikovaní. Opravený release dostane novú verziu.

## Reflog ako lokálny pohyb refs

```bash
git reflog show HEAD
git reflog show feature/ord-8421
```

Reflog zaznamenáva lokálne pohyby refov: commit, rebase, reset, checkout. Nie je distribuovanou históriou a nemusí existovať na remote. Je výborný recovery nástroj, ale nie dlhodobý audit alebo backup.

## Incident: release job buildne inú branch

Pipeline checkoutne tag `v4.2.0`, čím je HEAD detached. Skript však verziu odvodzuje z `git branch --show-current`, dostane prázdny string a použije default `main`. Artifact má nesprávne metadata, hoci source snapshot je správny.

Oprava nevyžaduje nútené vytvorenie branch. Build contract používa immutable commit ID a tag identity:

```bash
commit=$(git rev-parse HEAD)
tag=$(git describe --exact-match --tags HEAD)
```

Metadata explicitne zaznamenajú oba subjects.

## Zhrnutie

Commit je immutable snapshot a ancestry node. Branch je mutable ref, HEAD opisuje checkout state a annotated tag vytvára release identity. Amend, rebase a reset vytvárajú alebo presúvajú refs; nemenia staré objekty. Pri publikovanom history rewrite treba chrániť collaboration a evidence boundary.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Working tree, staging area a repository](working-tree-staging-repository.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Clone, fetch, pull a push →](clone-fetch-pull-push.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
