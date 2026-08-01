# Commit, branch, tag a HEAD

**Commit** je immutable snapshot projektu spojený s parent graphom a metadata. Nie je to branch a nie je to iba diff. Diff je odvodené porovnanie dvoch snapshots; commit sám ukazuje na celý root tree.

**Branch** je pohyblivý ref, zvyčajne uložený pod `refs/heads/`. Obsahuje object ID jedného commit-u. Keď na branchi vytvoríš nový commit, Git vytvorí nový commit object a posunie branch ref naň. Staršie commits zostávajú v graph-e cez parent odkazy.

**Tag** je stabilné meno používané najmä pre release alebo významný bod histórie. Lightweight tag je ref priamo na objekt. Annotated tag je objekt s vlastnými metadata a voliteľným podpisom. Publikovaný release tag by sa nemal presúvať, pretože by rovnaký názov označoval iný source subject.

**HEAD** opisuje aktuálnu checkout pozíciu. Bežne je symbolic ref na branch:

```text
HEAD → refs/heads/main → C4
```

V detached HEAD stave ukazuje priamo na commit:

```text
HEAD → C4
```

Detached HEAD nie je poškodenie repository. Znamená iba, že nový commit automaticky neposunie lokálnu branch. Ak chceš novú prácu zachovať stabilným menom, vytvoríš branch alebo tag.

Neutrálny graph:

```text
C1---C2---C3  main
          \
           C4  feature
```

`main` a `feature` sú mená ukazujúce na rôzne commits. Ak obe ukazujú na `C3`, branches sú odlišné refs, hoci majú rovnaký tip. Zmazanie branchu nemaže okamžite commits; odstraňuje jeden ref. Reachability môže zostať cez inú branch, tag alebo reflog.

Commit identity závisí aj od parenta. Preto cherry-pick alebo rebase vytvorí nový commit ID, aj keď výsledný patch alebo tree vyzerá rovnako. Branch identity je zase lokálna v konkrétnom repository. `main` v dvoch clones môže ukazovať na odlišné commits, kým sa nesynchronizujú.

Reflog zaznamenáva lokálne pohyby refs a HEAD. Je to recovery pomôcka, nie distribuovaná história ani dlhodobý backup. Remote repository bežne nepozná tvoj lokálny reflog.

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

## Mechanický walkthrough: ref pohyby a read-back po každom príkaze

Vytvorenie branchu možno overiť bez domnienky, že Git skopíroval repository:

```bash
before=$(git rev-parse HEAD)
git switch -c feature/ord-8421
after=$(git rev-parse HEAD)
branch_ref=$(git symbolic-ref HEAD)
printf 'before=%s after=%s HEAD=%s\n' "$before" "$after" "$branch_ref"
```

`before` a `after` sú rovnaké, pretože branch creation zatiaľ iba vytvorila `refs/heads/feature/ord-8421` na current commit a nastavila HEAD ako symbolic ref na toto meno. Working tree sa checkout-ne podľa rovnakého snapshotu, takže nemusí vzniknúť filesystem diff.

Po zmene a commite:

```bash
git add config/orders.yaml
git commit -m 'ORD-8421 raise limit'
git show --no-patch --format='commit=%H%nparents=%P%ntree=%T%nsubject=%s' HEAD
git rev-parse refs/heads/feature/ord-8421
```

Commit command vykoná tri logické kroky: zapíše tree z indexu, vytvorí commit s parentom na predchádzajúci HEAD a atomicky posunie current branch ref. `git show` číta immutable commit fields; `rev-parse` potvrdí, že mutable branch teraz ukazuje na nový ID.

Detached HEAD experiment:

```bash
git switch --detach HEAD~1
git symbolic-ref -q HEAD || printf 'HEAD is detached at %s\n' "$(git rev-parse HEAD)"
```

`symbolic-ref -q` v detached stave vráti non-zero, čo je očakávaný outcome, nie poškodenie repository. Ak tu vytvoríš commit, zapíše sa object a HEAD sa posunie priamo naň. Žiadny branch ref ho však nepomenuje:

```bash
printf 'investigation\n' > notes.txt
git add notes.txt
git commit -m 'temporary investigation'
new_tip=$(git rev-parse HEAD)
git branch recovery/investigation "$new_tip"
```

Posledný command vytvorí stabilný ref pred prepnutím preč. Bez neho môže commit po reflog expiry stratiť reachability.

Annotated tag:

```bash
git tag -a v4.2.0 -m 'Atlas Orders 4.2.0' "$new_tip"
git cat-file -t v4.2.0
git cat-file -p v4.2.0
git rev-parse v4.2.0^{}
```

Prvé `cat-file` ukáže type `tag`, druhé tagger/message/target a `^{}` dereferencuje tag object na commit. Lightweight tag by mal type target objectu priamo. Pri release evidence preto zaznamenaj tag object ID aj dereferencovaný commit, ak používaš annotated alebo signed tag.

Pri amend:

```bash
old=$(git rev-parse HEAD)
git commit --amend --no-edit
new=$(git rev-parse HEAD)
printf 'old=%s new=%s\n' "$old" "$new"
```

Aj bez zmeny message môže byť ID nové, pretože commit metadata alebo tree/parent subject sa znovu serializujú. CI evidence viazané na `old` sa nesmie automaticky preniesť na `new`.

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
