# Git object model

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Git and Automation Basics
- Predpoklady: [Filesystem hierarchy, inodes a links](../01-linux-and-systems/filesystem-hierarchy-inodes-links.md), [Hashovanie a nemenné artifacts](../00-foundations/immutable-vs-mutable-infrastructure.md)
- Súvisiace témy: content-addressable storage, commit graph, refs, garbage collection, integrity

## 1. Definícia

Git je distribuovaný version control system postavený nad content-addressable object database. Neuchováva primárne sekvenciu textových rozdielov. Uchováva nemenné objekty identifikované hashom ich obsahu a metadata.

Základné typy objektov:

```text
blob    obsah jedného súboru
tree    adresár: mená, modes a odkazy na blobs alebo ďalšie trees
commit  snapshot root tree + parent commits + author/committer metadata
tag     anotovaný odkaz na objekt, typicky commit
```

## 2. Content-addressable storage

Object ID je odvodené z typu a obsahu objektu.

Zjednodušene:

```text
object id = hash("<type> <size>\0<content>")
```

Dôsledky:

- rovnaký obsah vytvorí rovnaký object ID v rámci použitého hash algoritmu,
- zmena jedného byte vytvorí iný objekt,
- objekt sa po vytvorení nemení; nová verzia je nový objekt,
- hash prepája integritu aj adresovanie.

Historicky Git používa SHA-1. Moderný Git podporuje aj repository format so SHA-256, ale repository nemožno chápať ako ľubovoľnú zmes oboch formátov.

## 3. Blob

Blob obsahuje iba bytes súboru. Neobsahuje:

- filename,
- path,
- timestamps,
- owner/group,
- väčšinu filesystem metadata.

```bash
echo 'hello' | git hash-object --stdin
```

Zapísanie do object database:

```bash
echo 'hello' | git hash-object -w --stdin
```

Preto dva súbory s rovnakým obsahom môžu odkazovať na ten istý blob.

## 4. Tree

Tree vytvára snapshot adresárovej štruktúry.

Položka tree obsahuje:

```text
mode + type + object id + name
```

Príklad:

```bash
git ls-tree HEAD
git ls-tree -r HEAD
```

Typické modes:

```text
100644 regular file
100755 executable file
120000 symbolic link
040000 tree
160000 gitlink/submodule
```

Git sleduje executable bit, ale nie kompletné POSIX permissions.

## 5. Commit

Commit obsahuje:

- root tree snapshotu,
- zero alebo viac parent commits,
- author identity a čas,
- committer identity a čas,
- commit message,
- voliteľné podpisové metadata.

```bash
git cat-file -p HEAD
```

Prvý commit nemá parent. Bežný commit má jeden parent. Merge commit má dva alebo viac parents.

Commit neobsahuje branch name. Branch je samostatný ref ukazujúci na commit.

## 6. Snapshot model

Git logicky eviduje snapshoty celého stromu.

```text
Commit A → Tree A
Commit B → Tree B
Commit C → Tree C
```

Nezmenené súbory nemusia byť duplikované: nové trees môžu odkazovať na existujúce blobs. Diff je odvodený porovnaním snapshotov.

```bash
git diff A B
git diff-tree -r A B
```

Tvrdenie „commit je patch“ je nepresné. Patch je reprezentácia rozdielu medzi dvoma stavmi.

## 7. Commit graph

Parents vytvárajú directed acyclic graph.

```text
A---B---C---D
     \     /
      E---F
```

Graf umožňuje:

- ancestry queries,
- merge-base výpočet,
- branch divergence,
- reachability,
- garbage collection rozhodovanie.

```bash
git log --graph --oneline --decorate --all
git merge-base main feature
```

## 8. Refs

Ref je pohyblivé meno ukazujúce na object ID, typicky commit.

Príklady:

```text
refs/heads/main
refs/remotes/origin/main
refs/tags/v1.0.0
```

```bash
git show-ref
git rev-parse main
git rev-parse HEAD^{tree}
```

Refs môžu byť uložené ako samostatné files alebo v packed-refs.

## 9. HEAD

`HEAD` typicky obsahuje symbolic ref na aktuálnu branch:

```text
ref: refs/heads/main
```

V detached HEAD stave ukazuje priamo na commit ID.

```bash
git symbolic-ref HEAD
git rev-parse HEAD
```

## 10. Object storage

Loose objects sú typicky pod:

```text
.git/objects/aa/bbbbb...
```

Pri optimalizácii sa ukladajú do packfiles:

```text
.git/objects/pack/*.pack
.git/objects/pack/*.idx
```

Packfile môže používať delta compression, ale logický model objektov zostáva snapshotový a content-addressed.

```bash
git count-objects -v
git verify-pack -v .git/objects/pack/<file>.idx
```

## 11. Reachability a garbage collection

Objekt je reachable, ak sa k nemu dá dostať z refu, reflogu alebo ďalšieho rootu cez object graph.

Unreachable objekt nemusí byť okamžite odstránený.

```bash
git fsck --unreachable
git reflog
git gc
```

Reflog môže dočasne zachrániť commit po chybnom reset/rebase, ale nie je náhradou remote backupu a jeho retention je obmedzený.

## 12. Integrity vs. trust

Hash pomáha odhaliť poškodenie alebo zmenu objektu. Nehovorí automaticky:

- kto commit vytvoril,
- či je autor dôveryhodný,
- či obsah nie je škodlivý,
- či branch policy bola dodržaná.

Na autenticitu slúžia napríklad signed commits/tags a trusted CI policy. Na autorizáciu slúži serverová access control a branch protection.

## 13. Praktická explorácia

```bash
git init object-lab
cd object-lab
printf 'one\n' > file.txt
git add file.txt
git commit -m 'add file'

blob=$(git rev-parse HEAD:file.txt)
tree=$(git rev-parse HEAD^{tree})
commit=$(git rev-parse HEAD)

git cat-file -t "$blob"
git cat-file -p "$blob"
git cat-file -p "$tree"
git cat-file -p "$commit"
```

Cieľom je sledovať cestu:

```text
branch ref → commit → root tree → nested tree → blob
```

## 14. Troubleshooting

Repository hlási missing alebo corrupt object:

```bash
git fsck --full
git status
git remote -v
```

Možný postup:

1. zastaviť ďalšie deštruktívne zásahy,
2. vytvoriť kópiu `.git`,
3. identifikovať chýbajúci object a jeho reachability,
4. skúsiť fetch z dôveryhodného remote,
5. porovnať zdravý clone,
6. obnoviť lokálne nepublikované objekty z reflogu, backups alebo iného clone,
7. neprepisovať históriu bez pochopenia dopadu.

## 15. Časté omyly

### „Git ukladá iba diffy“

Logicky ukladá snapshots. Packfile delta compression je storage optimalizácia.

### „Branch je kontajner commitov“

Branch je pohyblivý ref na jeden commit; história je dostupná cez parents.

### „Commit obsahuje názov branch“

Neobsahuje.

### „Hash dokazuje, že autor je dôveryhodný“

Hash dokazuje väzbu identity objektu na obsah, nie ľudskú alebo organizačnú dôveryhodnosť.

## 16. Kontrolné otázky

1. Aký je rozdiel medzi blob, tree, commit a tag objektom?
2. Prečo filename nie je súčasť blobu?
3. Prečo je Git snapshotový systém, hoci zobrazuje diffy?
4. Ako parents vytvárajú commit graph?
5. Aký je rozdiel medzi object ID a refom?
6. Čo znamená reachability?
7. Načo slúži reflog?
8. Prečo hash nie je autentifikácia autora?

## Glossary impact

Relevantné pojmy: blob, tree, commit object, object ID, content-addressable storage, ref, reachability, packfile, reflog.
