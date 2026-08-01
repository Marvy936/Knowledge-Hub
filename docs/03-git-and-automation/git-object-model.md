# Git object model

Atlas developer upraví `config/orders.yaml` a pridá `maxOrderAmount: 5000`. Na disku je to obyčajný file content. Git ho však neukladá ako „verziu súboru s názvom orders.yaml“. Najprv vytvorí blob objekt z bytes, potom tree objekt priradí blob k pathu a commit ukáže na root tree spolu s parents a metadata. Git história je preto graf immutable snapshots, nie databáza patchov.

## Od bytes k blobu

Obsah možno vložiť do object database bez vytvorenia commitu:

```bash
blob=$(git hash-object -w config/orders.yaml)
printf '%s\n' "$blob"
git cat-file -t "$blob"
git cat-file -s "$blob"
git cat-file -p "$blob"
```

`hash-object -w` vytvorí objekt v `.git/objects`. Blob nepozná pathname, branch ani autora. Rovnaké bytes vytvoria rovnaký object ID v rovnakom object format-e. Premenovanie súboru preto nemusí duplikovať obsah; nový tree môže rovnaký blob priradiť k inému menu.

Object ID je content-derived identity, nie security signature autora. Hash chráni internú integritu grafu a adresovanie objektov, ale dôveryhodnosť pôvodu vyžaduje signed commits/tags, protected refs a repository trust controls.

## Tree pridáva pathname a mode

Index možno zapísať do tree objektu:

```bash
tree=$(git write-tree)
git cat-file -p "$tree"
```

Tree obsahuje entries s mode, menom a object ID. Directory je ďalší tree. Root tree tak vytvára hierarchický snapshot:

```text
root tree
├── config/      → tree
│   └── orders.yaml → blob
├── schemas/     → tree
└── tools/       → tree
```

Tree nepozná parent commit ani čas. Dve commits môžu ukazovať na rovnaký tree a líšiť sa iba históriou alebo metadata. To sa stane napríklad pri cherry-picku, ktorý vytvorí rovnaký výsledný snapshot nad iným parentom.

## Commit spája snapshot s históriou

Commit object obsahuje root tree, parent alebo parents, author, committer a message:

```bash
git cat-file -p HEAD
```

Zjednodušený obsah:

```text
tree <tree-id>
parent <parent-commit-id>
author Alice <alice@atlas.example> ...
committer Alice <alice@atlas.example> ...

ORD-8421 add maximum order amount
```

Prvý commit nemá parent. Bežný commit má jeden parent. Merge commit má najmenej dvoch parents a zachováva oba ancestry lines. Commit ID sa zmení pri zmene tree, parenta, message, author/committer metadata alebo timestampu. Preto amend a rebase vytvárajú nové commits aj vtedy, keď diff vyzerá rovnako.

## Annotated tag je objekt

Lightweight tag je ref priamo na objekt. Annotated tag vytvára tag object s taggerom, message a voliteľným podpisom:

```bash
git tag -a v4.2.0 -m 'Atlas Orders 4.2.0'
git cat-file -t v4.2.0
git cat-file -p v4.2.0
```

Release tag môže ukazovať na commit, ale je samostatnou identity. Retagging existujúcej verzie mení význam už publikovaného release subjectu a rozbíja reproducibility. Release versions sa majú považovať za immutable.

## Loose objects, packfiles a reachability

Nové objekty môžu byť uložené ako loose files. Git ich neskôr zabalí do packfile a môže použiť delta compression. Storage representation nemení logický object model; blob zostáva blobom s rovnakým ID.

```bash
git count-objects -v
git gc
git verify-pack -v .git/objects/pack/*.idx | head
```

Garbage collection pracuje s reachability. Objekt dostupný z branch, tagu, reflogu alebo iného refu zostáva živý. Unreachable objekt môže určitý čas prežiť a neskôr byť odstránený. Reflog preto často umožní recovery po reset-e, ale nie je večný backup contract.

## Refs sú pohyblivé mená

Branch `main` je ref obsahujúci commit ID. Keď vznikne nový commit, Git vytvorí immutable commit object a posunie ref:

```text
pred commitom:
main → C3

po commite:
main → C4 → C3
```

Objekt C3 sa nemení. Mutable časť systému je ref. To vysvetľuje fast-forward update, force push aj reflog: operácie primárne menia ukazovatele na immutable graph.

```bash
git show-ref --heads --tags
git rev-parse main
git rev-parse main^{tree}
```

## Incident: rovnaký diff, iný commit ID

Alice a Bob nezávisle aplikujú rovnakú textovú zmenu. Ich blob a výsledný tree môžu byť identické, no commits majú odlišných parents a timestamps. CI cache viazaná na commit ID ich preto považuje za odlišné subjects, hoci build input tree môže byť rovnaký.

Správny záver nie je „Git poškodil hash“. Commit identity reprezentuje snapshot aj ancestry. Ak build reproducibility závisí iba od source tree, pipeline môže evidovať tree ID alebo explicitný build-context digest popri commit provenance. Commit sa však nesmie zameniť za tree.

## Zhrnutie

Git ukladá blobs, trees, commits a tag objects do content-addressed databázy. Blob sú bytes bez mena, tree mapuje path a mode, commit spája snapshot s parent graphom a annotated tag pridáva release identity. Branches a ďalšie refs sa pohybujú; objekty zostávajú immutable. Táto hranica vysvetľuje všetky neskoršie operácie nad working tree, históriou a remotes.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Network troubleshooting](../02-networking-and-web/network-troubleshooting.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Working tree, staging area a repository →](working-tree-staging-repository.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
