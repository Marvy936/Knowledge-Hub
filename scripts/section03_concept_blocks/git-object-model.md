## Čo je Git object model

Git object model je vnútorný dátový model, ktorým Git reprezentuje obsah a históriu repository. Git neukladá projekt ako postupnosť celých adresárov ani ako databázu názvov súborov s očíslovanými verziami. Ukladá immutable objekty adresované hashom ich obsahu a medzi nimi vytvára odkazy. Základné typy sú `blob`, `tree`, `commit` a annotated `tag`.

**Blob** obsahuje bytes jedného súboru, ale nepozná jeho názov ani umiestnenie. **Tree** priraďuje názvy a file modes blobom alebo ďalším trees, takže vytvára snapshot adresárovej štruktúry. **Commit** ukazuje na jeden root tree, na svojho parenta alebo parents a obsahuje author, committer, čas a message. **Annotated tag** je samostatný objekt, ktorý pomenúva iný objekt a pridáva tagger metadata, message a prípadne cryptographic signature.

Z toho vyplýva dôležitý rozdiel:

```text
obsah súboru
→ blob

pathname + mode + blob
→ tree entry

celý snapshot + parent graph + metadata
→ commit
```

Git preto nesleduje „súbor“ ako stabilný objekt počas celého jeho života. Rename je odvodený záver z podobnosti medzi dvoma snapshots. Ak sa rovnaké bytes nachádzajú pod dvoma názvami, môžu používať rovnaký blob. Ak sa zmení iba parent alebo commit message, vznikne nový commit ID, aj keď root tree zostane rovnaký.

Content-addressing znamená, že object ID vzniká z typu, veľkosti a obsahu objektu. Object ID slúži ako identita a integrity check v Git databáze; nie je to dôkaz autorstva. Dôvera v pôvod zmeny sa buduje cez signed commits alebo tags, chránené refs, review a repository permissions.

Jednoduchý neutrálny príklad:

```text
README.md s obsahom "Hello"
→ blob B1

root tree:
README.md → B1
→ tree T1

commit:
tree T1
parent C0
message "Add README"
→ commit C1
```

Keď sa branch posunie z `C0` na `C1`, starý commit sa nemení. Mení sa iba ref, ktorý ukazuje na nový immutable graph. Tento model je základom pre staging, commits, branches, merge, rebase, reset aj recovery.