# Merge a rebase

<!-- CONCEPT-FIRST:START -->
## Čo riešia merge a rebase

Keď dve lines of development vzniknú zo spoločného predka, Git musí ich výsledky integrovať. **Merge** a **rebase** riešia rovnaký vstupný problém odlišným spôsobom: merge spája ancestry, rebase prenáša sériu zmien na nový základ.

Three-way merge pracuje s tromi snapshots:

```text
merge base
current side
other side
```

Git vypočíta, čo sa od spoločného predka zmenilo na každej strane, a pokúsi sa vytvoriť kombinovaný snapshot. Ak sa zmeny neprekrývajú podľa merge algoritmu, výsledok vytvorí automaticky. Ak nevie bezpečne rozhodnúť, uloží konflikt do index stages a čaká na človeka alebo merge driver.

Pri divergovanej histórii merge typicky vytvorí commit s dvoma parents. Tento commit neobsahuje „magickú zmes diffov“; ukazuje na resolved root tree a zachováva oba parent tips. Ancestry preto ukazuje, že vývoj prebiehal paralelne.

Rebase najprv identifikuje commits, ktoré sú jedinečné pre presúvanú branch. Pre každý commit odvodí patch vzhľadom na jeho pôvodného parenta a replayne ho nad nový base. Preto vznikajú nové commits s novými parents, timestamps a object IDs. Rebase nemení staré objekty; vytvorí nový graph a posunie ref.

Neutrálny príklad:

```text
pred:
      F1---F2  feature
     /
C0---M1       main

merge:
      F1---F2
     /       \
C0---M1-------X

rebase:
C0---M1---F1'---F2'
```

Final tree môže byť pri oboch stratégiách rovnaký, ale história, commit identity a audit význam sú odlišné.

Fast-forward nie je skutočný three-way merge. Ak current tip je ancestor targetu, Git môže iba posunúť ref dopredu. Squash merge zase vytvorí jeden nový commit s výsledným snapshotom, ale nezachová feature commits ako parents.

Voľba merge alebo rebase preto nie je iba estetika logu. Ovplyvňuje collaboration, signatures, review anchors, bisect, release provenance a downstream clones. Rebase je prirodzený pre unpublished alebo koordinovane rewriteovateľný subject. Merge je bezpečnejší pre už zdieľanú stabilnú históriu.

Textovo bezkonfliktný výsledok stále nemusí byť správny. Semantic conflict vznikne, keď dve samostatne platné zmeny spolu porušia domain pravidlo, test alebo runtime contract. Git môže potvrdiť syntaktickú integráciu, nie business correctness.
<!-- CONCEPT-FIRST:END -->

## Atlas scenár a praktické použitie

Alice má feature commits nad starším `main`, Bob medzitým posunul `main`. Obe vetvy obsahujú platnú prácu. Git musí vytvoriť históriu, v ktorej sú obe zmeny reachable. Merge zachová pôvodné ancestry lines a vytvorí spoločný descendant. Rebase replay-ne commits nad novým base a vytvorí nové identities.

## Merge ako spojenie dvoch parents

```bash
git switch feature/ord-8421
git merge origin/main
```

Ak branches divergovali, merge vytvorí commit s dvoma parents:

```text
      A1---A2  feature
     /       \
C0---B1-------M
      main
```

M snapshot obsahuje resolved result. Pôvodné A1, A2 a B1 zostávajú nezmenené. Merge zachováva informáciu, ktoré commits vznikli paralelne.

Fast-forward merge nevytvorí merge commit, ak current tip je ancestor targetu. `--no-ff` možno použiť, keď tím vedome chce zachovať feature boundary, ale nemá sa používať mechanicky bez histórie a release modelu.

## Rebase ako replay

```bash
git switch feature/ord-8421
git rebase origin/main
```

Git nájde commits unikátne pre feature branch, vypočíta ich patches a aplikuje ich nad nový base:

```text
pred:
      A1---A2
     /
C0---B1

po:
C0---B1---A1'---A2'
```

A1' a A2' sú nové commits s novými parents a IDs. Pôvodné commits môžu zostať v reflogu, ale branch už ukazuje na nové.

## Ours a theirs menia význam

Pri merge je `ours` current branch a `theirs` mergovaná branch. Pri rebase Git dočasne checkoutuje nový base a replayuje feature commit; labels v konfliktných tools môžu byť pre používateľa intuitívne obrátené. Namiesto slepého výberu celej strany treba čítať merge base, intent a výsledný contract.

```bash
git show :1:config/orders.yaml
git show :2:config/orders.yaml
git show :3:config/orders.yaml
```

## Kedy merge a kedy rebase

Merge je vhodný, keď ancestry a paralelný vývoj majú hodnotu alebo keď sa integruje publikovaná shared history. Rebase je vhodný na lokálne alebo koordinovane zdieľané feature commits pred integráciou, keď tím chce lineárny review subject.

Rebase shared branch bez coordination rozbije downstream clones, review anchors a evidence. Pravidlo nie je „nikdy nerebase“, ale „nerewrite history, ktorú iní považujú za stabilnú“.

## Interactive rebase

```bash
git rebase -i origin/main
```

Interactive rebase môže reword, squash, fixup, reorder alebo drop commits. Je to editor lokálnej histórie pred publication. Po každej transformácii treba znovu spustiť tests, pretože zmena poradia môže meniť intermediate aj final semantics.

`git range-diff` porovná starú a novú commit sériu:

```bash
git range-diff origin/main...feature-before origin/main...feature-after
```

Je vhodnejší než porovnanie iba final diffu, keď review potrebuje vedieť, ako sa séria zmenila.

## Squash merge

Hosting platform môže zlúčiť celý pull request do jedného nového commit-u. Feature commits potom nie sú parents v main history. Výhodou je kompaktná main história; nevýhodou strata detailnej ancestry a zložitejšie mapovanie jednotlivých commit IDs.

Squash merge nie je to isté ako interactive squash na feature branch, hoci final snapshot môže byť rovnaký.

## Rerere

`git rerere` môže zaznamenať predchádzajúce conflict resolutions a znovu ich navrhnúť pri opakovanom merge/rebase. Šetrí prácu pri dlhých release branches, ale automaticky použitú resolution treba review-nuť a testovať; kontext sa mohol zmeniť.

```bash
git config rerere.enabled true
git rerere status
```

## Incident: rebase zmení správanie bez textového conflict-u

Feature A pridá default `maxOrderAmount=5000`. Nový main medzitým zmení currency rounding. Rebase aplikuje patch čisto, no kombinácia mení validation order a test začne zlyhávať. Git nemá textový conflict, pretože riadky sa neprekrývajú.

Toto je semantic conflict. Správny gate zahŕňa tests a review final diffu voči novému base:

```bash
git diff origin/main...HEAD
```

Clean rebase output nie je correctness verdict.

## Zhrnutie

Merge vytvára descendant s viacerými parents a zachováva ancestry. Rebase replayuje commits nad nový base a vytvára nové identities. Výber je collaboration a audit rozhodnutie. Textovo čistá integrácia stále môže obsahovať semantic conflict, preto je výsledok overený až tests a domain reviewom.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Clone, fetch, pull a push](clone-fetch-pull-push.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Reset, revert a restore →](reset-revert-restore.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
