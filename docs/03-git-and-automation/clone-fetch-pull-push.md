# Clone, fetch, pull a push

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Git and Automation Basics
- Predpoklady: [Commit, branch, tag a HEAD](commit-branch-tag-head.md)
- Súvisiace témy: remote, refspec, tracking branch, fast-forward, authentication, partial clone

## 1. Definícia

Git je distribuovaný systém: každý bežný clone má vlastnú object database, local refs, reflogy a working state. Remote repository nie je databáza, ktorú lokálny Git priebežne priamo upravuje.

Synchronizácia má dve oddelené vrstvy:

```text
object transfer
  prenes chýbajúce commits, trees, blobs a tags

ref update
  zmeň pomenované tips, napríklad refs/heads/main
```

Hlavné operácie:

```text
clone  bootstrap nového lokálneho repozitára z remote
fetch  stiahni objects a aktualizuj lokálnu evidenciu remote refs
pull   fetch + integruj upstream do aktuálnej branch
push   pošli objects + požiadaj server o ref update
```

## 2. Remote ako lokálna konfigurácia

Remote je lokálne pomenovaný súbor nastavení:

- fetch URL,
- prípadne odlišná push URL,
- fetch refspecs,
- tag a pruning policy,
- partial-clone metadata,
- ďalšie transportné options.

```bash
git remote -v
git remote get-url origin
git remote get-url --push origin
git config --get-regexp '^remote\.origin\.'
```

`origin` je iba konvenčný názov. Nie je súčasťou Git protokolu a možno ho premenovať:

```bash
git remote rename origin upstream
```

## 3. URL a transport

Git remote URL môže používať napríklad:

```text
https://host/org/repo.git
ssh://git@host/org/repo.git
git@host:org/repo.git
file:///path/to/repo
```

Transport ovplyvňuje:

- authentication,
- proxy a firewall path,
- credential handling,
- host identity verification,
- performance a protocol capabilities.

Remote URL nemá obsahovať long-lived token v plaintext forme. HTTPS má používať credential helper alebo workload credential; SSH host key musí byť overený cez dôveryhodný `known_hosts` model.

## 4. Čo vykoná `git clone`

Bežný clone typicky:

1. vytvorí local repository,
2. nakonfiguruje remote `origin`,
3. zistí server refs a default branch,
4. vyjedná a prenesie potrebné objects,
5. vytvorí remote-tracking refs,
6. vytvorí local branch s upstream konfiguráciou,
7. nastaví `HEAD`, index a working tree.

```bash
git clone https://example.com/team/repo.git
git -C repo remote -v
git -C repo branch -vv
```

Clone nie je iba download posledných files. Podľa režimu bootstrapuje históriu, refs a synchronization config.

## 5. Default branch discovery

Remote repository môže publikovať symbolic `HEAD`, napríklad:

```text
HEAD → refs/heads/main
```

Klient podľa toho vyberie initial branch. Ak remote `HEAD` chýba alebo ukazuje na neexistujúci ref, clone môže necheckoutnúť očakávanú branch.

Diagnostika:

```bash
git ls-remote --symref origin HEAD
git remote show origin
```

Lokálna evidencia remote default branch môže byť:

```text
refs/remotes/origin/HEAD → refs/remotes/origin/main
```

Aktualizácia:

```bash
git remote set-head origin --auto
```

## 6. Clone varianty

### Konkrétna branch

```bash
git clone --branch release/1.x <url>
```

### Single branch

```bash
git clone --single-branch --branch release/1.x <url>
```

Môže nakonfigurovať užší fetch refspec, takže neskorší fetch neuvidí všetky branches.

### Bez checkoutu

```bash
git clone --no-checkout <url>
```

Objects a refs sa prenesú, ale working tree sa nematerializuje.

### Bare clone

```bash
git clone --bare <url>
```

Nemá bežný working tree a používa sa pre serverové alebo integračné účely.

## 7. Fetch ako object + remote-tracking update

`git fetch`:

1. kontaktuje remote,
2. zistí advertised refs a capabilities,
3. vyjedná, ktoré objects chýbajú,
4. stiahne packfile alebo potrebné objects,
5. overí object integrity,
6. aktualizuje destination refs podľa fetch refspecu,
7. zapíše `FETCH_HEAD` a reflog updates.

```bash
git fetch origin
git fetch --all
```

Štandardný fetch nemení current local branch, index ani working tree. Mení však object database a remote-tracking refs.

## 8. Remote-tracking refs

Po fetchi môže existovať:

```text
refs/remotes/origin/main
```

`origin/main` je lokálna evidencia remote branch v čase posledného zodpovedajúceho fetchu.

```bash
git rev-parse origin/main
git log main..origin/main
git branch -r
```

Nie je to live server query. Aktuálny server ref možno zistiť:

```bash
git ls-remote origin refs/heads/main
```

Aj `ls-remote` je iba okamžitý observation point; server ref sa môže po odpovedi zmeniť.

## 9. Fetch refspec

Refspec mapuje source ref na local destination ref:

```text
[+]<source>:<destination>
```

Typický fetch refspec:

```text
+refs/heads/*:refs/remotes/origin/*
```

```bash
git config --get-all remote.origin.fetch
```

Význam:

- source wildcard vyberá remote branches,
- destination vytvára remote-tracking namespace,
- `+` povoľuje non-fast-forward update lokálnej remote-tracking evidencie.

Remote branch môže byť rebased alebo force-pushed; remote-tracking ref má po fetchi zrkadliť nový stav, preto je forced update bežný.

## 10. Explicitný fetch refspec

Konkrétnu branch možno stiahnuť:

```bash
git fetch origin refs/heads/feature:refs/remotes/origin/feature
```

Dočasný fetch bez persistent config môže uložiť result iba do `FETCH_HEAD`:

```bash
git fetch origin refs/heads/feature
```

Pred zápisom priamo do local branch treba vedieť, či branch nie je checkoutnutá a či update neprepíše lokálnu prácu. Bežný model používa remote-tracking ref a následnú explicitnú integráciu.

## 11. Negative refspec

Fetch config môže vylúčiť refs cez negative refspec:

```text
^refs/heads/archive/*
```

```bash
git config --get-all remote.origin.fetch
```

To je užitočné pri veľkých namespaces, ale môže vysvetľovať, prečo očakávaná branch nie je fetchovaná, hoci server ju publikuje.

## 12. Object negotiation

Klient a server sa snažia preniesť iba objects, ktoré klient nemá.

Zjednodušene:

```text
client wants: D
client has:  B
server sends objects potrebné pre B..D
```

Prenos môže používať:

- packfiles,
- delta compression,
- bitmaps,
- negotiation algorithms,
- protocol v2 commands a capability negotiation.

Používateľ zvyčajne nemusí riadiť detaily, ale pri performance probléme je dôležité vedieť, že pomalý fetch nemusí byť iba bandwidth: môže ísť o server-side object traversal, veľký ref namespace, delta computation alebo antivirus/filesystem overhead.

## 13. `FETCH_HEAD`

Po fetchi Git zapisuje `.git/FETCH_HEAD` s informáciou o fetchnutých tips a ich účele.

```bash
cat .git/FETCH_HEAD
git show FETCH_HEAD
```

`FETCH_HEAD` je dočasný integration reference, nie stabilná branch. Ďalší fetch ho môže prepísať.

Pri manuálnom workflow:

```bash
git fetch origin main
git merge FETCH_HEAD
```

je bezpečnejšie vedieť, ktorý konkrétny fetch result sa integruje.

## 14. Pruning remote-tracking refs

Ak server branch zmaže, local remote-tracking ref môže zostať stale.

```bash
git fetch --prune origin
git remote prune origin --dry-run
git remote prune origin
```

Prune odstráni lokálne remote-tracking refs, ktoré už remote podľa refspecu nepublikuje.

Neodstráni automaticky:

- local branch rovnakého mena,
- commits reachable z iných refs,
- working tree,
- nefetchované refs mimo config scope.

## 15. Tag fetching

Tag behavior má vlastné pravidlá. Fetch môže automaticky nasledovať tags, ktoré ukazujú na fetchnuté commits, alebo tags fetchovať explicitne.

```bash
git fetch --tags origin
git fetch --no-tags origin
git config --get remote.origin.tagOpt
```

Po prepísaní publikovaného tagu nemusí local fetch automaticky presunúť existujúci local tag bez forced refspecu. To je zámerná ochrana pred tichou zmenou release identity.

## 16. Pull je orchestration, nie transport synonymum

`git pull` je typicky:

```text
fetch
+
integrácia fetchnutého upstreamu do current branch
```

Integrácia môže byť:

- fast-forward,
- merge,
- rebase,
- odmietnutie pri `--ff-only`.

```bash
git pull --ff-only
git pull --rebase
git pull --no-rebase
```

Pull môže zmeniť local history, index aj working tree a môže vytvoriť conflicts. Nie je to read-only download.

## 17. Ktorý upstream pull používa

Current local branch môže mať:

```text
branch.main.remote = origin
branch.main.merge  = refs/heads/main
```

```bash
git branch -vv
git config --get-regexp '^branch\.main\.'
git rev-parse '@{upstream}'
```

Bez upstreamu musí používateľ uviesť remote a branch alebo nastaviť tracking.

```bash
git branch --set-upstream-to=origin/main main
```

Nejasná upstream konfigurácia môže integrovať nesprávny ref.

## 18. Pull fast-forward

Ak local tip je ancestor upstream tipu:

```text
A---B local
     \
      C---D upstream
```

local branch sa môže posunúť na `D` bez nového merge commitu.

```bash
git pull --ff-only
```

`--ff-only` je predvídateľná policy: pri divergence zlyhá a vyžaduje vedomé rozhodnutie.

## 19. Pull merge

Pri divergencii:

```text
      C---D local
     /
A---B
     \
      E---F upstream
```

merge vytvorí nový commit s oboma tips ako parents, ak nie je zvolený iný merge behavior.

```bash
git pull --no-rebase
```

Výsledok zachová obe ancestries. Môže vytvoriť konflikty a nový merge commit.

## 20. Pull rebase

```bash
git pull --rebase
```

typicky fetchne upstream a replayne local-only commits nad upstream tip.

```text
pred:
      C---D local
     /
A---B---E---F upstream

po:
A---B---E---F---C'---D'
```

Local commits dostanú nové IDs. Ak už boli publikované, následný push môže vyžadovať history rewrite.

## 21. Pull policy

Explicitná config znižuje nečakané správanie:

```bash
git config pull.ff only
# alebo
git config pull.rebase true
# alebo
git config pull.rebase false
```

Ďalšie relevantné settings:

```bash
git config --get rebase.autoStash
git config --get branch.main.rebase
```

Auto-stash môže dočasne ukryť working changes, ale následná re-apply môže konfliktovať. Čistý working tree je pred synchronizáciou stále najjasnejší model.

## 22. Push lifecycle

`git push` typicky:

1. kontaktuje remote receive service,
2. autentifikuje transport identity,
3. zistí aktuálne remote refs a capabilities,
4. vypočíta objects potrebné pre proposed updates,
5. odošle packfile,
6. požiada o jeden alebo viac ref updates,
7. server vykoná authorization, hooks a branch policy,
8. server prijme alebo odmietne commands,
9. klient zobrazí per-ref result.

Objects môžu byť prenesené, ale ref update odmietnutý. To sú dve oddelené fázy.

## 23. Push refspec

Explicitný push refspec:

```text
<local-source>:<remote-destination>
```

```bash
git push origin refs/heads/main:refs/heads/main
git push origin HEAD:refs/heads/feature/api-timeout
```

Krátky zápis:

```bash
git push origin main
```

je pohodlný, ale automatizácia má často používať explicitné refs, aby sa znížila závislosť od `push.default`, upstreamu a current branch.

## 24. `push.default`

```bash
git config --get push.default
```

Bežné modely zahŕňajú:

- `simple` — push current branch na upstream branch s bezpečnostnou kontrolou mena,
- `current` — push current branch na branch rovnakého mena,
- `upstream` — push na configured upstream,
- `matching` — širší historický model, rizikovejší bez jasného intentu.

Default behavior nie je vhodné predpokladať medzi rôznymi strojmi alebo CI runners.

## 25. `git push -u`

```bash
git push -u origin feature/api-timeout
```

Pushne branch a nastaví upstream config pre current local branch.

Následne:

```bash
git status
git branch -vv
git pull
git push
```

môžu používať tracking information. `-u` nie je potrebné opakovať pri každom pushi.

## 26. Server-side fast-forward validation

Bežný server odmietne branch update, ak starý remote tip nie je ancestor nového tipu.

```text
remote: A---B---C
local:  A---B---D
```

Taký push by odstránil `C` z visible ancestry remote branch.

Diagnostika:

```bash
git fetch origin
git log --graph --oneline --left-right main...origin/main
git merge-base --is-ancestor origin/main main
```

Riešenie nie je automaticky force push. Najprv treba integrovať remote change alebo potvrdiť oprávnený rewrite workflow.

## 27. Force push a lease

```bash
git push --force-with-lease origin feature
```

Lease overuje, že remote ref má očakávané ID. Ak ho medzitým zmenil iný aktér, push sa odmietne.

Explicitný lease:

```bash
git push \
  --force-with-lease=refs/heads/feature:<expected-id> \
  origin HEAD:refs/heads/feature
```

Je presnejší pri background fetch tooloch, ktoré môžu nečakane posunúť local remote-tracking ref.

Lease nerieši:

- organizačnú oprávnenosť rewrite,
- downstream clones používajúce staré IDs,
- artifacts postavené zo starej histórie,
- tag/release consistency.

## 28. Atomic push

Viac ref updates možno požiadať atomicky:

```bash
git push --atomic origin main v1.2.0
```

Ak server capability podporuje, všetky updates uspejú alebo všetky zlyhajú.

To je dôležité pri release flow, kde branch a tag nesmú zostať v čiastočne aktualizovanom stave.

## 29. Push options a server policy

Niektoré servery podporujú push options:

```bash
git push -o ci.skip origin feature
```

Význam nie je štandardný business contract Git jadra; určuje ho server alebo hooks. Automatizácia musí vedieť, či option obchádza alebo mení required process.

Server môže odmietnuť push pre:

- protected branch,
- required pull request,
- missing signed commits,
- failed status checks,
- secret scanning,
- file size limits,
- hook validation,
- authorization.

## 30. Push tags

Explicitný release tag:

```bash
git push origin refs/tags/v1.2.0
```

Všetky local tags:

```bash
git push origin --tags
```

`--tags` môže publikovať experimentálne alebo lokálne tags, ktoré nepatria na server. Release pipeline má pushovať konkrétny tag a overiť jeho peeled commit.

Možnosť:

```bash
git push --follow-tags origin main
```

typicky zahŕňa relevantné annotated tags reachable z pushovaných commits, nie ľubovoľný tag namespace.

## 31. Delete remote ref

```bash
git push origin --delete feature/old
git push origin :refs/heads/feature/old
```

Server spracuje delete ako ref update na „žiadny object“. Branch protection alebo authorization ho môže odmietnuť.

Delete remote branch:

- nevymaže local branches v clones,
- nevymaže okamžite objects,
- môže zneplatniť otvorený workflow,
- potrebuje následný prune remote-tracking refs.

## 32. Authentication verzus authorization

Authentication odpovedá:

```text
Kto sa pripája?
```

Authorization odpovedá:

```text
Môže táto identita čítať repository alebo meniť tento ref?
```

Transport môže úspešne overiť SSH key, no server môže push odmietnuť pre branch policy. Naopak nesprávny token alebo SSH host key zlyhá ešte pred Git ref operáciou.

## 33. SSH remote diagnostika

```bash
ssh -vT git@host
git ls-remote git@host:org/repo.git
GIT_SSH_COMMAND='ssh -vvv' git fetch origin
```

Kontroluj:

- DNS a TCP port,
- SSH host key,
- použitý private key/agent,
- server account mapping,
- repository path,
- read/write permissions.

Neobchádzaj host key verification ako „opravu“ bez overenia server identity.

## 34. HTTPS remote diagnostika

```bash
GIT_TRACE=1 GIT_CURL_VERBOSE=1 git fetch origin
```

Kontroluj:

- proxy a `NO_PROXY`,
- TLS certificate/trust store,
- redirecty,
- credential helper,
- token scope a expiry,
- server status,
- HTTP authentication challenge.

Trace output môže obsahovať citlivé metadata. Nezdieľaj ho bez sanitizácie.

## 35. Credential helpers

```bash
git config --show-origin --get-all credential.helper
```

Credential helper môže používať OS keychain, manager alebo cache. Riziká:

- plaintext store helper,
- credential pre nesprávny host/path,
- expirovaný token v cache,
- CI home directory zdieľaný medzi jobs,
- secret v remote URL.

Pri CI preferuj short-lived workload identity alebo scoped ephemeral token.

## 36. Shallow clone

```bash
git clone --depth 1 <url>
git fetch --deepen 50
git fetch --shallow-since='2026-01-01'
git fetch --unshallow
```

Shallow repository má skrátenú ancestry a `.git/shallow` boundaries.

Dopad:

- neúplný merge-base,
- obmedzený `git describe`, blame a changelog,
- nesprávny version calculation,
- problémy s history-based analyzérmi,
- odlišný push/fetch behavior.

`depth 1` nie je „plný clone s menším diskom“. Je to zámerne neúplný graph.

## 37. Single-branch clone verzus shallow clone

```bash
git clone --single-branch --branch main <url>
```

obmedzuje fetch ref scope. Nemusí obmedziť ancestry current branch.

```bash
git clone --depth 1 <url>
```

obmedzuje ancestry depth.

Tieto options sa často kombinujú, ale riešia odlišné osi:

```text
single-branch  ktoré refs sledujem
shallow        koľko ancestry mám
```

## 38. Partial clone

```bash
git clone --filter=blob:none <url>
```

Partial clone môže stiahnuť commits a trees, ale blobs načítať až pri potrebe.

Dopad:

- checkout alebo diff môže spustiť network fetch,
- offline build môže zlyhať,
- performance závisí od request patternu,
- server musí podporovať filter/promisor model,
- missing promisor object nie je automaticky corruption.

```bash
git config --get remote.origin.promisor
git config --get remote.origin.partialclonefilter
```

## 39. Sparse checkout nie je clone filter

Sparse checkout obmedzuje materializované paths. Partial clone obmedzuje lokálne objects. Shallow clone obmedzuje ancestry.

```text
sparse   working-tree view
partial  object availability
shallow  commit graph depth
```

Pri veľkom monorepe možno použiť kombináciu, no tooling musí podporovať všetky tri semantics.

## 40. Bare a mirror clone

Bare:

```bash
git clone --bare <url>
```

vytvorí repository bez working tree a typicky kopíruje branches do local heads namespace vhodného pre server storage.

Mirror:

```bash
git clone --mirror <url>
```

kopíruje širší ref namespace a nastaví mirror fetch behavior.

```bash
git push --mirror <new-url>
```

môže vytvoriť, prepísať aj zmazať refs na cieli tak, aby zodpovedali source. Je to migrácia/replication operácia s veľkým blast radiusom, nie bežný push.

## 41. Bundle ako offline transport

Git bundle môže preniesť refs a objects bez online remote:

```bash
git bundle create repo.bundle --all
git bundle verify repo.bundle
git clone repo.bundle repo-copy
```

Incremental bundle potrebuje prerequisite history na prijímajúcej strane.

Bundle je vhodný pre air-gapped transfer alebo backup jednej vrstvy, no neobsahuje working-tree untracked files ani automaticky server permissions/hooks.

## 42. Submodules pri clone/fetch

Superproject clone neprenáša automaticky obsah všetkých submodule repositories bez explicitného kroku.

```bash
git clone --recurse-submodules <url>
git submodule update --init --recursive
```

Submodule URLs a commits sú samostatný trust a availability model. Parent commit môže ukazovať na submodule commit, ktorý server už neposkytuje alebo ku ktorému klient nemá access.

## 43. Bezpečný fetch-first workflow

Pred integráciou:

```bash
git status --short
git fetch --prune origin
git branch -vv
git log --graph --oneline --left-right HEAD...@{upstream}
```

Potom zvoľ:

- fast-forward only,
- merge,
- rebase,
- žiadnu integráciu, iba review.

Fetch-first oddeľuje observation od mutation. Používateľ si môže prezrieť remote state pred zmenou local branch.

## 44. Bezpečný push workflow

```bash
git status
git branch -vv
git fetch origin
git log --graph --oneline --left-right HEAD...@{upstream}
# spusti tests a over commit
git push origin HEAD:refs/heads/<target>
```

Pred pushom musí byť jasné:

- source commit,
- destination ref,
- current server tip,
- fast-forward/non-fast-forward charakter,
- branch policy,
- či sa pushujú tags,
- aký artifact/provenance workflow sa spustí.

## 45. Diagnostika: push rejected

```bash
git remote -v
git branch -vv
git fetch origin
git log --graph --oneline --left-right HEAD...@{upstream}
git ls-remote origin
```

Klasifikuj failure:

- transport/DNS/TLS/SSH,
- authentication,
- repository authorization,
- non-fast-forward,
- protected branch,
- server hook,
- secret/file-size policy,
- missing required signature,
- target ref mismatch.

Error text treba čítať od prvej relevantnej server response, nie iba posledný všeobecný `failed to push some refs` riadok.

## 46. Diagnostika: fetch nevidí branch

```bash
git ls-remote --heads origin
git config --get-all remote.origin.fetch
git remote show origin
git branch -r
```

Možné príčiny:

- branch na serveri neexistuje,
- názov alebo case mismatch,
- single-branch refspec,
- negative refspec,
- permission filtering,
- iný remote URL,
- branch je mimo heads namespace.

Explicitný fetch:

```bash
git fetch origin refs/heads/name:refs/remotes/origin/name
```

## 47. Diagnostika: pull vytvoril nečakaný merge

Over:

```bash
git reflog -10
git log --graph --oneline --decorate -20
git config --show-origin --get pull.rebase
git config --show-origin --get pull.ff
git config --get branch.$(git branch --show-current).rebase
```

Pull policy mohla byť definovaná v system, global, local alebo branch-specific config.

Ak merge ešte nie je dokončený:

```bash
git merge --abort
```

Ak pull už vytvoril commit, recovery závisí od toho, či bol publikovaný a či má working tree ďalšie zmeny. Reflog poskytne pre-pull state.

## 48. Diagnostika: clone je neúplný

```bash
git rev-parse --is-shallow-repository
git config --get remote.origin.partialclonefilter
git config --get-all remote.origin.fetch
git sparse-checkout list
```

Rozlíš:

- shallow ancestry,
- single-branch ref scope,
- partial object filter,
- sparse working-tree view,
- submodule initialization.

„Chýba história“ môže mať štyri úplne odlišné príčiny.

## 49. Failure modes

### Fetch uspel, ale current branch sa nezmenila

Očakávané: fetch aktualizuje remote-tracking refs, nie local branch.

### Push preniesol veľký pack a potom zlyhal

Object transfer mohol uspieť, ale server ref update odmietol policy alebo race.

### Existing `origin/main` ukazuje starý commit

Remote-tracking ref nebol fetchnutý alebo fetch refspec branch nezahŕňa.

### `git pull --rebase` vyžaduje force push

Rebase zmenil IDs local commits, ktoré už boli publikované.

### CI changelog je prázdny

Shallow clone nemá dostatočnú ancestry alebo fetch refspec neobsahuje base branch.

### Mirror migrácia zmazala refs na cieli

`push --mirror` synchronizuje celý ref namespace vrátane deletions.

### HTTPS funguje lokálne, nie v CI

Odlišný trust store, proxy, credential helper alebo token scope.

## 50. Časté omyly

### „Clone je iba download files“

Bootstrapuje repository objects, refs, remote config a checkout podľa režimu.

### „Fetch je pull bez checkoutu“

Fetch prenáša objects a aktualizuje remote-tracking refs. Pull pridáva integračný krok nad current branch.

### „`origin/main` je server branch“

Je lokálna evidencia posledného fetchu.

### „Push uploadne working tree“

Push prenáša objects reachable z push source refu. Uncommitted files nie sú súčasťou pushu.

### „Authentication success znamená write permission“

Authorization a branch policy sa vyhodnocujú samostatne.

### „Force-with-lease je bezpečný force“

Je bezpečnejší voči race, no stále mení zdieľanú históriu.

### „Shallow a partial clone sú to isté“

Shallow skracuje ancestry; partial odkladá niektoré objects.

### „`--tags` publikuje iba release tag“

Publikuje všetky matching local tags.

## 51. Diagnostický checklist

Pred synchronizáciou zisti:

- Ktorý remote URL sa používa na fetch a push?
- Aký je fetch refspec?
- Je clone single-branch, shallow, partial alebo sparse?
- Ktorý local branch a upstream sú aktuálne?
- Je remote-tracking ref čerstvý?
- Čo ukazuje server cez `ls-remote`?
- Aký je divergence graph?
- Akú pull integration policy má config?
- Aký explicitný push source a destination ref sa použijú?
- Je update fast-forward?
- Ak treba rewrite, aké expected remote ID chráni lease?
- Ktorá server policy alebo hook môže update odmietnuť?
- Prenášajú sa branches, tags alebo celý mirror namespace?
- Sú credentials short-lived a správne scoped?

## 52. Zhrnutie

Clone vytvára lokálny distribuovaný uzol. Fetch aktualizuje object database a local remote-tracking evidence. Pull nad fetch výsledkom vykonáva merge, rebase alebo fast-forward. Push prenáša objects a žiada server o kontrolovaný ref update.

Kľúčový model:

```text
fetch:
remote refs → local remote-tracking refs

pull:
fetch result → current local branch integration

push:
local source ref → server destination ref
```

Keď sa object transfer oddelí od ref updates a local refs od server refs, je možné presne diagnostikovať stale `origin/main`, non-fast-forward, protected branch, partial clone aj transport authentication bez náhodného pull/force workflowu.

## 53. Kontrolné otázky

1. Aké dve hlavné vrstvy má Git synchronizácia?
2. Čo všetko typicky nastaví `git clone`?
3. Čo presne zmení `git fetch` a čo štandardne nezmení?
4. Ako fetch refspec mapuje remote branch na local remote-tracking ref?
5. Prečo `origin/main` nie je live server state?
6. Načo slúži `FETCH_HEAD`?
7. Aký je rozdiel medzi fetch a pull?
8. Ako sa líši `pull --ff-only`, merge pull a rebase pull?
9. Aký je rozdiel medzi upstream a push remote?
10. Čo obsahuje push refspec?
11. Prečo server odmieta non-fast-forward branch update?
12. Čo kontroluje explicitný force-with-lease?
13. Prečo je atomic push relevantný pre release?
14. Aký je rozdiel medzi shallow, single-branch, partial a sparse clone?
15. Prečo môže object transfer uspieť, ale ref update zlyhať?
16. Ako odlíšiš authentication failure od authorization alebo branch policy rejection?

## Glossary impact

Relevantné pojmy: remote, fetch URL, push URL, clone, fetch, pull, push, object negotiation, advertised ref, refspec, fetch refspec, push refspec, remote-tracking ref, `FETCH_HEAD`, upstream branch, push remote, fast-forward, non-fast-forward, force-with-lease, atomic push, prune, shallow clone, single-branch clone, partial clone, promisor remote, bare repository, mirror repository, bundle, credential helper.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Commit, branch, tag a HEAD](commit-branch-tag-head.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Merge a rebase →](merge-and-rebase.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
