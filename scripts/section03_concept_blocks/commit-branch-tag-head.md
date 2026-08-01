## Čo sú commit, branch, tag a HEAD

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