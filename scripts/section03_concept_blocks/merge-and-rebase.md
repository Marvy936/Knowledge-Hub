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