# Git object model

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Git and Automation Basics
- Predpoklady: [Filesystem hierarchy, inodes a links](../01-linux-and-systems/filesystem-hierarchy-inodes-links.md), [Hashovanie a nemenné artifacts](../00-foundations/immutable-vs-mutable-infrastructure.md)
- Súvisiace témy: content-addressable storage, commit graph, refs, garbage collection, integrity

## 1. Definícia

Git je distribuovaný version control system postavený nad content-addressable object database. Jeho jadrom nie je zoznam príkazov ani postupnosť textových patchov, ale nemenný graf objektov, ktorých identita je odvodená z ich typu a obsahu.

Základné typy objektov sú:

```text
blob    bytes obsahu súboru
tree    snapshot jedného adresára
commit  root tree + parent commits + metadata
tag     anotovaný objekt odkazujúci na iný Git objekt
```

Bežná cesta od používateľského názvu k obsahu vyzerá takto:

```text
branch alebo tag ref
  ↓ object ID
commit
  ↓ tree field
root tree
  ↓ entries
nested trees a blobs
```

Tento model vysvetľuje, prečo je branch lacný pointer, prečo commit reprezentuje snapshot, prečo možno stratený commit často obnoviť z reflogu a prečo rewrite histórie vytvára nové commits namiesto úpravy existujúcich.

## 2. Problém, ktorý objektový model rieši

Version control potrebuje uchovávať viac súvisiacich stavov projektu a vedieť odpovedať na otázky:

- Aký presný obsah patril ku konkrétnemu commitu?
- Ktorý commit je rodičom iného commitu?
- Ktoré súbory sa medzi dvoma stavmi zmenili?
- Ktoré objekty sú ešte súčasťou nejakej pomenovanej histórie?
- Ako overiť, že uložený obsah nebol ticho zmenený?
- Ako preniesť iba chýbajúce objekty medzi dvoma repozitármi?

Git oddeľuje dve veci:

```text
immutable data graph    objects: blob, tree, commit, tag
mutable naming layer    refs: branches, remote-tracking refs, tags, HEAD
```

Objekty zachytávajú obsah a ancestry. Refs poskytujú ľudské mená a pohyblivé vstupné body do grafu.

## 3. Content-addressable storage

Object ID sa vypočíta z canonical representation objektu. Zjednodušený model je:

```text
header  = "<type> <size>\0"
object  = header + content
object ID = hash(object)
```

Dôsledky:

- **Rovnaký canonical obsah vedie k rovnakému object ID** — dva blobs s rovnakými bytes môžu byť deduplikované.
- **Zmena jediného byte vytvorí nové ID** — pôvodný objekt zostáva nezmenený.
- **Typ je súčasťou identity** — rovnaké bytes uložené ako blob a tree nie sú rovnaký objekt.
- **Veľkosť je súčasťou headera** — objekt má jednoznačnú serializáciu.
- **Hash je adresa aj integrity check** — poškodený obsah už nezodpovedá svojmu menu.

Historicky Git používa SHA-1 object IDs. Git podporuje aj repository format so SHA-256, ale repository má definovaný object format; nejde o ľubovoľnú zmes identifikátorov v jednej databáze.

Kolízna odolnosť hashovania je dôležitá, no hash sám neposkytuje dôveru v autora ani bezpečnosť obsahu. Dokazuje väzbu medzi identifikátorom a canonical bytes objektu.

## 4. Fyzický object record

Git pred hashovaním neprenáša iba raw file content. Objekt má typovaný header:

```text
blob 6\0hello\n
```

Praktická kontrola:

```bash
printf 'hello\n' | git hash-object --stdin
printf 'hello\n' | git hash-object --stdin -t blob
```

Zapísanie loose objectu:

```bash
printf 'hello\n' | git hash-object -w --stdin
```

Typ a veľkosť možno overiť:

```bash
git cat-file -t <object-id>
git cat-file -s <object-id>
git cat-file -p <object-id>
```

`git cat-file -p` zobrazuje human-readable interpretáciu tam, kde ju Git pozná. Nie je to vždy doslovný raw byte stream uloženého objektu.

## 5. Blob: obsah bez mena

Blob reprezentuje bytes obsahu súboru. Neuchováva:

- filename,
- parent directory,
- filesystem path,
- ownera a group,
- creation alebo modification timestamp,
- väčšinu POSIX permission bits,
- informáciu, v koľkých cestách sa obsah používa.

Preto môžu dve rôzne paths odkazovať na rovnaký blob:

```text
Tree entry: docs/a.txt → blob X
Tree entry: copy/a.txt → blob X
```

Premenovanie súboru nevytvára špeciálny „rename object“. Nový tree jednoducho obsahuje rovnaký blob pod iným názvom. Rename detection je heuristika odvodená pri porovnaní snapshotov.

```bash
git diff --find-renames <old> <new>
```

To je dôvod, prečo Git neuchováva „históriu súboru“ ako samostatnú identitu. História konkrétnej path je odvodená z postupnosti tree snapshotov a similarity heuristík.

## 6. Tree: adresár ako snapshot

Tree objekt mapuje názvy položiek na modes a object IDs. Jedna entry obsahuje konceptuálne:

```text
mode + name + object ID
```

Typické modes:

```text
100644  regular non-executable file
100755  regular executable file
120000  symbolic link
040000  nested tree
160000  gitlink, typicky submodule commit
```

Príklad:

```bash
git ls-tree HEAD
git ls-tree -r HEAD
git cat-file -p HEAD^{tree}
```

Tree poskytuje:

- filename,
- adresárovú hierarchiu,
- vybraný file mode,
- referenciu na blob, ďalší tree alebo gitlink.

Git nesleduje kompletné POSIX ACL, owner/group ani všeobecné timestamps. Symlink je tree entry s mode `120000`; jeho blob obsahuje text cieľovej path, nie obsah cieľového súboru.

## 7. Snapshot celého projektu

Commit ukazuje na jeden root tree. Root tree cez nested trees a blobs určuje celý versionovaný stav projektu v danom momente.

```text
commit C
  ↓
root tree T0
  ├── README.md → blob B1
  ├── src        → tree T1
  │   ├── app.py → blob B2
  │   └── lib.py → blob B3
  └── tests      → tree T2
      └── ...
```

Ak sa medzi dvoma commitmi zmení iba `src/app.py`, nové objekty budú typicky:

- nový blob pre `app.py`,
- nový tree pre `src`,
- nový root tree, pretože odkaz na `src` tree sa zmenil,
- nový commit.

Nezmenené blobs a trees môžu zostať zdieľané. Git preto logicky uchováva celé snapshots bez nutnosti duplikovať všetky bytes pri každom commite.

## 8. Commit objekt

Commit obsahuje minimálne:

- object ID root tree,
- zero alebo viac parent commitov,
- autora a author timestamp,
- committera a committer timestamp,
- commit message.

Môže obsahovať aj ďalšie headers, napríklad podpisové metadata.

```bash
git cat-file -p HEAD
git show --no-patch --pretty=raw HEAD
```

Typický commit:

```text
tree <tree-id>
parent <parent-id>
author ...
committer ...

commit message
```

Dôležité dôsledky:

- Prvý commit nemá parent.
- Bežný lineárny commit má jeden parent.
- Merge commit má viac parentov.
- Commit neobsahuje názov branch.
- Commit ID závisí aj od metadata a parenta, nie iba od snapshotu.

Dva commits môžu ukazovať na rovnaký tree, ale mať rôzne ID pre odlišných parentov, timestamps, identitu alebo message.

## 9. Author verzus committer

Author metadata opisuje, kto pôvodnú zmenu vytvoril. Committer metadata opisuje, kto konkrétny commit objekt zostavil alebo prepísal do aktuálnej histórie.

Pri bežnom commite sú identity často rovnaké. Pri operáciách ako rebase alebo cherry-pick môže zostať author pôvodný, ale committer a committer time sa zmenia.

```bash
git log --format=fuller -1
```

To vysvetľuje, prečo rewrite histórie mení commit IDs aj vtedy, keď patch a author zostanú rovnakí: zmení sa parent chain alebo committer metadata.

## 10. Parent edges a commit graph

Parent fields vytvárajú directed acyclic graph — DAG.

```text
A---B---C---D
     \     /
      E---F
```

Šípka je konceptuálne smerom od novšieho commitu k parentovi. História sa preto prechádza dozadu od refu cez parent links.

Graf umožňuje:

- ancestry queries,
- výpočet merge base,
- rozlíšenie fast-forward a divergent history,
- topologické logovanie,
- reachability analýzu,
- výber objektov pri fetch/push,
- garbage collection rozhodovanie.

```bash
git log --graph --oneline --decorate --all
git merge-base main feature
git merge-base --is-ancestor A B
git rev-list --ancestry-path A..B
```

Commit graph nie je zoradený iba timestampom. Hodiny môžu byť nepresné; ancestry určuje parent relation.

## 11. Merge commit a význam parent order

Merge commit má typicky dva parenty:

```text
parent 1 = branch, na ktorej merge prebehol
parent 2 = branch, ktorá sa integrovala
```

Poradie parentov je významné pre operácie ako:

```bash
git show --first-parent
git log --first-parent
git revert -m 1 <merge-commit>
```

Merge commit môže mať tree, ktorý nie je identický ani s jedným parentom. Obsahuje výsledný snapshot po trojcestnej integrácii a prípadnom manuálnom riešení konfliktov.

## 12. Annotated tag objekt

Annotated tag je samostatný Git objekt. Obsahuje:

- target object ID,
- target type,
- tag name,
- tagger identity a čas,
- message,
- voliteľný kryptografický podpis.

```bash
git cat-file -p refs/tags/v1.0.0
git verify-tag v1.0.0
```

Lightweight tag nie je tag objekt; je to priamo ref ukazujúci na iný objekt.

```text
lightweight tag: refs/tags/v1.0.0 → commit
annotated tag:   refs/tags/v1.0.0 → tag object → commit
```

Annotated tag je vhodnejší pre release identity, message a podpis. Samotný názov `refs/tags/...` však stále môže byť serverom alebo lokálne prepísaný, ak policy tomu nezabráni.

## 13. Refs: mená nad objektovým grafom

Ref je pomenovaný pointer na object ID, zvyčajne commit alebo tag object.

Príklady:

```text
refs/heads/main
refs/remotes/origin/main
refs/tags/v1.0.0
refs/stash
```

```bash
git show-ref
git for-each-ref
git rev-parse refs/heads/main
git update-ref refs/heads/main <new-id> <expected-old-id>
```

Ref je mutable. Commit nie. Keď vznikne nový commit na branchi, Git vytvorí nový commit objekt a posunie branch ref.

```text
pred commitom: main → C
po commite:    main → D → C
```

Bezpečné ref update môže používať očakávané staré ID ako compare-and-swap ochranu. Rovnaký princíp je základom non-fast-forward kontroly na remote serveri.

## 14. Symbolic refs a HEAD

`HEAD` typicky nie je priamo commit ID, ale symbolic ref:

```text
HEAD → refs/heads/main → commit C
```

```bash
git symbolic-ref HEAD
git rev-parse HEAD
```

Pri detached HEAD ukazuje `HEAD` priamo na commit:

```text
HEAD → commit C
```

Nový commit v detached HEAD stave je platný objekt, ale neposunie bežnú local branch. Ak sa nevytvorí ref a reflog entry expiruje, commit sa môže neskôr stať unreachable a byť odstránený garbage collection.

Záchrana pred odchodom:

```bash
git switch -c rescue-branch
```

## 15. Revision expressions

Git príkazy často neprijímajú iba object ID, ale revision expressions:

```text
HEAD           aktuálny commit
HEAD^          prvý parent
HEAD^2         druhý parent merge commitu
HEAD~3         trikrát prvý parent
main^{tree}    tree objekt commitu main
v1.0.0^{}      dereference annotated tagu
HEAD:path      objekt pre path v danom tree
```

```bash
git rev-parse HEAD^
git rev-parse HEAD~3
git rev-parse v1.0.0^{}
git show HEAD:config/app.yml
```

`^` a `~` nie sú všeobecne zameniteľné pri merge graphe. `~N` sleduje first-parent chain; `^N` vyberá konkrétneho parenta jedného commitu.

## 16. Reachability

Objekt je reachable, ak ho možno dosiahnuť z rootov, ktoré Git aktuálne považuje za živé, napríklad:

- local branches,
- remote-tracking refs,
- tags,
- `HEAD`,
- reflogs,
- stash,
- dočasné refs používané operáciami,
- serverové alebo implementačné roots.

Reachability sa šíri grafom:

```text
ref → commit → parents
             → tree → nested trees → blobs
             → tag target
```

```bash
git rev-list --objects --all
git fsck --unreachable
git fsck --dangling
```

`dangling` objekt je typicky unreachable objekt, na ktorý neodkazuje iný unreachable objekt. Unreachable neznamená okamžite odstránený.

## 17. Reflog ako lokálny ref journal

Reflog zaznamenáva lokálne zmeny refov a často aj `HEAD`:

```bash
git reflog
git reflog show main
git show HEAD@{2}
```

Príklad:

```text
main@{0}: reset: moving to HEAD~2
main@{1}: commit: add feature
```

Reflog umožňuje obnoviť commits po:

- chybnom reset,
- rebase,
- amend,
- prepnutí branch,
- detached HEAD práci.

Nie je to globálna ani garantovaná záloha:

- typicky sa neprenáša pri clone/fetch,
- má expiration policy,
- môže byť manuálne vyčistený,
- remote server môže mať odlišné logovanie refs.

## 18. Loose objects

Loose object je samostatný komprimovaný súbor pod `.git/objects`:

```text
.git/objects/aa/bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
```

Prvé dva hex znaky object ID tvoria directory. Zvyšok je filename.

Loose object je zvyčajne zlib-compressed canonical object record. Pri bežnej práci vznikajú nové objekty najprv loose a neskôr sa môžu zabaliť.

```bash
git count-objects -v
```

Do `.git/objects` sa nemá zasahovať ručne bez forenznej kópie a presného recovery plánu.

## 19. Packfiles a delta compression

Git balí veľa objektov do packfiles:

```text
.git/objects/pack/*.pack
.git/objects/pack/*.idx
```

Packfile môže ukladať objekt:

- celý,
- ako delta voči inému objektu v packu,
- ako delta voči objektu identifikovanému mimo aktuálneho packu.

```bash
git verify-pack -v .git/objects/pack/<pack>.idx
git index-pack --verify <packfile>
```

Delta compression je fyzická storage optimalizácia. Logický objekt je po rekonštrukcii stále blob, tree, commit alebo tag s vlastným canonical ID.

Preto súčasne platí:

```text
Git logicky uchováva snapshots.
Git fyzicky môže komprimovať podobné objekty deltami.
```

## 20. Alternates a shared object stores

Repository môže čítať objekty aj z alternatívneho object directory, napríklad pri niektorých shared clone modeloch.

To šetrí disk, ale vytvára dependency: ak alternatívny object store odstráni objekty, dependent repository môže byť poškodené.

Kontrola:

```bash
cat .git/objects/info/alternates
```

Pri migrácii alebo archivácii treba vedieť, či repository vlastní všetky potrebné objekty alebo sa spolieha na external object store.

## 21. Shallow clone a neúplná ancestry

Shallow repository má zámerne skrátenú históriu. Boundary commits sa správajú ako dočasné roots, aj keď v plnej histórii parentov majú.

```bash
git rev-parse --is-shallow-repository
cat .git/shallow
git fetch --deepen=100
git fetch --unshallow
```

Dôsledky:

- ancestry query môže byť neúplná,
- merge-base nemusí byť dostupný,
- blame a log sa zastavia na shallow boundary,
- push alebo server policy môže mať obmedzenia,
- CI optimalizácia môže rozbiť nástroje očakávajúce plnú históriu.

Shallow commit nie je iný typ objektu; neúplnosť je repository metadata.

## 22. Partial clone a promisor objects

Partial clone môže mať kompletnú commit/tree históriu, ale nie všetky blobs lokálne. Chýbajúce objekty sú sľúbené promisor remote a stiahnu sa podľa potreby.

```bash
git clone --filter=blob:none <url>
git rev-parse --is-shallow-repository
git config --get remote.origin.promisor
```

To je odlišné od corruption:

```text
missing object + promisor metadata   môže byť legitímny lazy fetch
missing object bez sľubu             môže byť poškodenie
```

Offline operácie nad chýbajúcim blobom môžu zlyhať, hoci commit a tree existujú.

## 23. Replace refs a historické prepojenia

`git replace` môže lokálne nahradiť objekt iným objektom pri rev-walk operáciách:

```bash
git replace <old-object> <new-object>
git replace -l
```

Pôvodný objekt sa nemení. Vznikne ref pod `refs/replace/`.

Použitie:

- dočasná oprava alebo experiment,
- prepojenie importovaných histórií,
- forenzná analýza.

Riziko: používateľ môže vidieť inú ancestry než kolega, ak replace refs nie sú zdieľané. Pri audite treba overiť:

```bash
git replace -l
git --no-replace-objects log --graph --oneline
```

## 24. Object integrity verzus autenticita

Object ID pomáha potvrdiť, že canonical bytes objektu zodpovedajú menu. Neodpovedá však na otázky:

- Kto zmenu autorizoval?
- Je author identity pravdivá?
- Prešiel commit review a CI?
- Je obsah bezpečný?
- Je branch ref dôveryhodný?

Ďalšie vrstvy:

- **Signed commit/tag** — kryptografická väzba na signing identity.
- **Protected branch** — serverová authorization a update policy.
- **Required reviews/checks** — procesný trust.
- **Trusted build provenance** — väzba medzi source refom a artifactom.

Aj podpísaný commit môže obsahovať chybu. Podpis autentifikuje podpisujúcu identitu a obsah objektu, nie jeho kvalitu.

## 25. Object transfer medzi repozitármi

Fetch a push prenášajú objekty potrebné na dosiahnutie požadovaného ref update. Obe strany vyjednávajú, ktoré commits a objects už majú.

Zjednodušene:

```text
want: commit D
have: commit B
→ pošli objekty potrebné pre B..D
```

Prenos používa packfile a môže zahŕňať deltified objects. Ref update je samostatný krok: prijatie objektov ešte nemusí znamenať, že server branch posunul.

Preto možno mať situáciu:

```text
objects boli prenesené
ref update bol odmietnutý branch policy
```

Objekty môžu zostať na serveri dočasne unreachable a neskôr ich odstráni GC.

## 26. Garbage collection

Garbage collection optimalizuje storage a odstraňuje objekty, ktoré zostali unreachable po uplynutí ochranných lehôt.

```bash
git gc
git maintenance run
git repack
git prune --dry-run
```

GC môže:

- zabaliť loose objects,
- prepočítať delta chains,
- aktualizovať auxiliary indexes,
- expirovať reflog entries,
- odstrániť dostatočne staré unreachable objects.

`git prune` sa nemá používať ako rutinný „cleanup“ bez pochopenia retention a recovery dopadu. Agresívny prune môže zničiť poslednú lokálnu možnosť obnovy unpublished commitov.

## 27. Commit-graph a auxiliary indexes

Git môže vytvoriť commit-graph file, ktorý zrýchľuje ancestry a reachability queries. Môže používať generation numbers a ďalšie predpočítané informácie.

```bash
git commit-graph write --reachable
git commit-graph verify
git maintenance run
```

Commit-graph nie je zdroj pravdy pre commits. Je odvodený index. Pri poškodení ho možno znovu vytvoriť z object database.

Podobne bitmap indexes a multi-pack-index zrýchľujú rev-list, fetch a object lookup, ale nemenia logický object model.

## 28. Diagnostika poškodeného repozitára

Pri hlásení `missing blob`, `bad object` alebo `corrupt loose object`:

1. **Zastav deštruktívne operácie** — nespúšťaj agresívny prune alebo cleanup.
2. **Vytvor filesystem kópiu repozitára vrátane `.git`** — zachovaj incident evidence.
3. **Spusť integrity kontrolu**:

```bash
git fsck --full
git status
git show-ref
git reflog --all
```

4. **Urči typ a reachability chýbajúceho objektu** — commit, tree alebo blob majú iný dopad.
5. **Over partial-clone/promisor kontext** — chýbajúci blob nemusí byť corruption.
6. **Porovnaj dôveryhodný clone alebo remote**:

```bash
git remote -v
git fetch --all --prune
```

7. **Obnov publikované objekty z remote** — iba ak remote obsahuje správnu históriu.
8. **Obnov unpublished objekty z reflogu, backupu alebo iného clone**.
9. **Po oprave znovu spusti `git fsck --full` a over working tree**.

Nahradenie celého lokálneho clone novým clone je často najbezpečnejšie pre publikovanú históriu, ale najprv treba zachrániť necommitnutú prácu a lokálne commits.

## 29. Praktická explorácia objektového grafu

Vytvor malý repository:

```bash
git init object-lab
cd object-lab
printf 'one\n' > file.txt
git add file.txt
git commit -m 'add file'
```

Zisti objects:

```bash
commit=$(git rev-parse HEAD)
tree=$(git rev-parse HEAD^{tree})
blob=$(git rev-parse HEAD:file.txt)

printf 'commit: %s\n' "$commit"
printf 'tree:   %s\n' "$tree"
printf 'blob:   %s\n' "$blob"

git cat-file -p "$commit"
git cat-file -p "$tree"
git cat-file -p "$blob"
```

Zmeň iba názov:

```bash
git mv file.txt renamed.txt
git commit -m 'rename file'

git rev-parse HEAD:renamed.txt
git log --follow -- renamed.txt
```

Over, či blob zostal rovnaký. Potom zmeň content a sleduj, ktoré IDs sa zmenili.

## 30. Failure modes

### Commit existuje, ale branch ho neukazuje

Commit môže byť reachable iba z reflogu, stashu, inej branch alebo vôbec nie z bežného refu.

```bash
git reflog --all
git branch --contains <commit>
git fsck --lost-found
```

### `git log --all` neukazuje detached commit

`--all` prechádza refs, nie všetky existujúce objects. Použi reflog alebo fsck.

### Rovnaký source snapshot má iný commit ID

Commit ID zahŕňa parentov, autora/committera, timestamps a message. Porovnaj trees:

```bash
git rev-parse A^{tree}
git rev-parse B^{tree}
```

### Clone je malý a niektoré blobs chýbajú

Môže ísť o partial clone. Over promisor konfiguráciu a network dostupnosť.

### História sa líši iba u jedného používateľa

Over replace refs, grafts, shallow boundary a local refs.

## 31. Časté omyly

### „Git ukladá iba diffy“

Logicky ukladá typované snapshots. Packfile môže objekty fyzicky komprimovať deltami.

### „Commit je kópia celého pracovného adresára“

Commit ukazuje na tree snapshot iba versionovaných paths. Neobsahuje ignored alebo untracked files ani filesystem metadata mimo Git modelu.

### „Branch obsahuje commits“

Branch je ref na jeden commit. História je dostupná cez parent graph.

### „Commit pozná svoju branch“

Commit object neobsahuje branch name. Rovnaký commit môže byť reachable z viacerých branches a tags.

### „Object ID dokazuje autora“

Object ID viaže canonical bytes na identifikátor. Author field je metadata a bez podpisu ho možno deklarovať ľubovoľne.

### „Unreachable objekt je okamžite stratený“

Môže ešte existovať a byť zachytený reflogom alebo grace period. Po expiracii a prune však môže byť definitívne odstránený.

### „Reflog je remote backup“

Reflog je prevažne lokálny journal ref updates s obmedzenou retention.

## 32. Diagnostický checklist

Pri analýze objektového modelu zisti:

- Ktorý ref alebo revision expression používam?
- Na aký object type sa resolveuje?
- Aký commit a root tree je výsledkom?
- Je objekt reachable z branches, tags alebo iba reflogu?
- Je repository shallow alebo partial?
- Existujú replace refs alebo alternates?
- Je problém v source objects alebo iba v odvodenom indexe?
- Obsahuje remote chýbajúcu publikovanú históriu?
- Boli pred zásahom zachované unpublished commits a working tree?

## 33. Zhrnutie

Git oddeľuje nemenné content-addressed objects od pohyblivých refs. Blob drží bytes, tree pomenúva obsah v adresárovej štruktúre, commit viaže snapshot na parent graph a annotated tag pridáva release metadata a podpis. Diff, rename detection, branch history aj merge base sú odvodené z tohto grafu.

Keď používateľ rozumie trase:

```text
ref → commit → tree → blob
```

vie predvídať dôsledky resetu, rebase, fetchu, garbage collection aj recovery. Git potom prestáva byť súborom magických príkazov a stáva sa manipuláciou s explicitným immutable graphom a jeho menami.

## 34. Kontrolné otázky

1. Z akých bytes sa vypočíta Git object ID?
2. Prečo filename nie je súčasť blob objektu?
3. Ktoré metadata obsahuje tree entry?
4. Prečo dva commits s rovnakým tree môžu mať odlišné IDs?
5. Ako parent fields vytvárajú commit graph?
6. Aký je rozdiel medzi annotated a lightweight tagom?
7. Aký je rozdiel medzi object ID, refom a symbolic refom?
8. Čo presne znamená reachability?
9. Prečo reflog môže zachrániť commit po resete, ale nie je backup?
10. Ako sa líši shallow clone od partial clone?
11. Prečo delta compression neznamená, že Git logicky ukladá iba patchy?
12. Ako by si postupoval pri hlásení missing object bez straty unpublished práce?

## Glossary impact

Relevantné pojmy: object database, canonical object representation, blob, tree, commit object, annotated tag, object ID, content-addressable storage, parent graph, reachability, ref, symbolic ref, HEAD, reflog, loose object, packfile, delta compression, shallow clone, partial clone, promisor object, replace ref, commit-graph, garbage collection.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Network troubleshooting](../02-networking-and-web/network-troubleshooting.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Working tree, staging area a repository →](working-tree-staging-repository.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
