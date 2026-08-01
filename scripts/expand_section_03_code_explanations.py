from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SECTION = REPO / "docs/03-git-and-automation"
BRANCH = os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME")
if not BRANCH:
    raise SystemExit("Unable to resolve pull request branch")


def run(*args: str) -> None:
    print("+", " ".join(args), flush=True)
    subprocess.run(args, cwd=REPO, check=True)


def insert_before_incident(filename: str, block: str) -> None:
    path = SECTION / filename
    text = path.read_text(encoding="utf-8")
    marker = "## Incident:"
    if text.count(marker) != 1:
        raise RuntimeError(f"Expected one incident marker in {filename}, found {text.count(marker)}")
    heading = block.strip().splitlines()[0]
    if heading in text:
        raise RuntimeError(f"Expansion already exists in {filename}: {heading}")
    text = text.replace(marker, block.rstrip() + "\n\n" + marker, 1)
    path.write_text(re.sub(r"\n{3,}", "\n\n", text).rstrip() + "\n", encoding="utf-8")


run("git", "fetch", "origin", BRANCH)
run("git", "checkout", "-B", BRANCH, f"origin/{BRANCH}")

insert_before_incident(
    "git-object-model.md",
    r"""## Mechanický walkthrough: od bytes po commit bez porcelain skratiek

Nasledujúci experiment je vhodné vykonať v disposable repository. Ukazuje presne, ktoré objects vznikajú; nepoužíva working tree ako neviditeľnú skratku.

```bash
mkdir object-lab && cd object-lab
git init
printf 'hello\n' > message.txt
blob=$(git hash-object -w message.txt)
printf 'blob=%s\n' "$blob"
```

`git hash-object -w message.txt` načíta bytes file-u, vytvorí Git object header `blob <size>\0`, z headeru a obsahu vypočíta object ID a compressed object zapíše pod `.git/objects/`. Prepínač `-w` je mutation; bez neho command hash iba vypočíta. File `message.txt` sa nemení a zatiaľ neexistuje tree ani commit.

```bash
git cat-file -t "$blob"
git cat-file -s "$blob"
git cat-file -p "$blob"
```

`-t` číta type, `-s` logical payload size a `-p` pretty-printne payload. Úspech dokazuje, že lokálna object database obsahuje object s týmto ID. Nedokazuje, že je reachable z branchu alebo že bol pushnutý.

Tree sa vytvorí cez dočasný index. `GIT_INDEX_FILE` zabráni zmene reálneho staging area:

```bash
export GIT_INDEX_FILE="$PWD/lab.index"
git update-index --add --cacheinfo 100644,"$blob",message.txt
tree=$(git write-tree)
printf 'tree=%s\n' "$tree"
git cat-file -p "$tree"
```

`update-index --cacheinfo` vloží do indexu trojicu mode–blob ID–pathname. Mode `100644` znamená regular non-executable file. Index neobsahuje file contents; drží object IDs a metadata pre budúci snapshot. `write-tree` serializuje celý index do tree objectu. Ak zmeníš iba pathname alebo executable bit, tree ID sa zmení aj pri rovnakom blob-e.

Commit možno vytvoriť bez `git commit`:

```bash
commit=$(printf 'manual root commit\n' | git commit-tree "$tree")
printf 'commit=%s\n' "$commit"
git cat-file -p "$commit"
git update-ref refs/heads/lab "$commit"
```

`commit-tree` vytvorí commit object ukazujúci na tree. Keďže ide o root commit, nemá parent; pri ďalšom commite by sa pridal `-p <parent>`. Až `update-ref` vytvorí reachable branch identity. Táto operácia má byť preferovaná pred ručným zápisom do `.git/refs`, pretože rešpektuje ref locking a môže používať compare-and-swap old value.

```bash
git update-ref refs/heads/lab "$new_commit" "$expected_old_commit"
```

Tretí argument je precondition. Ak ref medzitým posunul iný writer, update zlyhá namiesto prepísania novšej práce. Rovnaký princíp sa neskôr objaví pri `--force-with-lease`, Terraform state serialoch alebo cloud `RevisionId`.

Nakoniec odstráň dočasný index:

```bash
unset GIT_INDEX_FILE
rm -f -- lab.index
```

Tento walkthrough vysvetľuje dôležitú hranicu: blob, tree a commit sú immutable content objects; branch je mutable meno. `git add` a `git commit` sú bezpečné porcelain commands, ktoré skladajú tieto primitives a posúvajú refs, ale object model pod nimi zostáva rovnaký.""",
)

insert_before_incident(
    "working-tree-staging-repository.md",
    r"""## Mechanický walkthrough: čo presne porovnávajú status a diff

Začni clean commitom a uprav jeden file:

```bash
printf 'maxOrderAmount: 4000\n' > config/orders.yaml
git add config/orders.yaml
git commit -m 'add initial order limit'
printf 'maxOrderAmount: 5000\n' > config/orders.yaml
```

V tomto momente sú tri relevantné snapshots:

```text
HEAD tree:      4000
index entry:    4000
working file:   5000
```

Preto:

```bash
git diff -- config/orders.yaml
```

porovná working tree s indexom a ukáže 4000 → 5000. Naopak:

```bash
git diff --cached -- config/orders.yaml
```

je prázdny, pretože index stále zodpovedá HEAD. `git diff HEAD -- path` porovná working tree priamo s HEAD a v tejto chvíli ukáže rovnaký rozdiel ako prvý command, ale po partial stagingu už nie.

```bash
git add config/orders.yaml
```

`git add` načíta aktuálne bytes, zapíše alebo reuse-ne blob a zmení index entry. Working file nepresúva do špeciálneho priečinka. Po add:

```text
HEAD tree:      4000
index entry:    5000
working file:   5000
```

Teraz je obyčajný `git diff` prázdny a `git diff --cached` ukazuje staged change. Ak file znovu upravíš na 5500, súčasne existujú staged aj unstaged changes:

```text
HEAD tree:      4000
index entry:    5000
working file:   5500
```

`git status --short` môže zobraziť `MM`: prvé písmeno opisuje index proti HEAD, druhé working tree proti indexu. Status nie je štvrtá databáza; je to zhrnutie dvoch porovnaní a untracked/conflict state-u.

Partial staging:

```bash
git add -p config/orders.yaml
```

Git rozdelí diff na hunks a pri každom sa pýta, či sa má aplikovať do indexu. Keď zvolíš `s`, skúsi hunk rozdeliť; `e` otvorí patch editor. Výsledok treba čítať oboma diffmi, pretože file môže obsahovať kombináciu staged a unstaged intentu.

```bash
git diff --cached
git diff
```

Pri citlivom commite je vhodný explicitný gate:

```bash
git diff --cached --check
git diff --cached --name-status
git diff --cached
```

`--check` hľadá vybrané whitespace chyby, nie business correctness. `--name-status` ukáže path-level actions a posledný command celý patch. Až potom `git commit` vytvorí tree z indexu; neberie automaticky všetko, čo editor momentálne zobrazuje.

Ak chceš staged file odstageovať bez straty working changes:

```bash
git restore --staged config/orders.yaml
```

Index sa vráti k HEAD, working file zostane. Ak chceš zahodiť working zmenu a obnoviť index version:

```bash
git restore config/orders.yaml
```

Tieto dve operácie majú opačný destination. Pred ich vykonaním si vždy povedz, ktorý snapshot je source a ktorú vrstvu chceš prepísať.""",
)

insert_before_incident(
    "commit-branch-tag-head.md",
    r"""## Mechanický walkthrough: ref pohyby a read-back po každom príkaze

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

Aj bez zmeny message môže byť ID nové, pretože commit metadata alebo tree/parent subject sa znovu serializujú. CI evidence viazané na `old` sa nesmie automaticky preniesť na `new`.""",
)

insert_before_incident(
    "clone-fetch-pull-push.md",
    r"""## Mechanický walkthrough: lokálne refs verzus serverový ref

Po clone si vypíš tri vrstvy konfigurácie:

```bash
git remote get-url origin
git config --get-all remote.origin.fetch
git branch -vv
git show-ref --heads --remotes
```

URL určuje transport endpoint. Fetch refspec typicky mapuje serverové `refs/heads/*` do lokálnych `refs/remotes/origin/*`. `branch -vv` ukáže upstream vzťah a ahead/behind podľa posledného lokálneho observation pointu. Žiadny z týchto výstupov nie je live query na server po tom, čo command skončil.

Bezpečný observation flow:

```bash
old_remote=$(git rev-parse --verify refs/remotes/origin/main)
git fetch --prune origin
new_remote=$(git rev-parse --verify refs/remotes/origin/main)
printf 'origin/main: %s -> %s\n' "$old_remote" "$new_remote"
git log --graph --oneline --decorate --left-right main...origin/main
```

Fetch najprv vyjedná objects, potom aktualizuje remote-tracking refs. `--prune` odstráni lokálne tracking refs pre serverové branches, ktoré server už neinzeruje; nemaže local branches. Ak transfer prejde, ale ref update zlyhá, object database môže obsahovať nové objects bez posunutého tracking refu.

`pull --ff-only` je zložená operácia:

```bash
git pull --ff-only origin main
```

Najprv vykoná fetch. Potom overí, či current branch tip je ancestor fetched tipu. Ak áno, posunie local branch bez nového commit-u. Ak branches divergovali, command skončí non-zero a working history nemá byť automaticky spojená. To je zámerný safety gate.

Pri pushi si priprav explicitné IDs:

```bash
local_tip=$(git rev-parse HEAD)
expected_remote=$(git rev-parse refs/remotes/origin/feature/ord-8421 2>/dev/null || true)
printf 'local=%s expected_remote=%s\n' "$local_tip" "$expected_remote"
git push origin HEAD:refs/heads/feature/ord-8421
```

Server prijme pack s chýbajúcimi objects a potom rozhodne o ref update-e. Ak hook alebo branch protection update odmietne, odoslané objects môžu na serveri dočasne existovať, ale branch sa neposunie. Push output preto čítaj ako ref verdict, nie iba network transfer.

Explicitný lease pri history rewrite:

```bash
git push \
  --force-with-lease=refs/heads/feature/ord-8421:"$expected_remote" \
  origin \
  HEAD:refs/heads/feature/ord-8421
```

Server prepíše ref iba ak jeho current old value stále zodpovedá `$expected_remote`. Ak Bob medzičasom pushol, lease zlyhá. Toto chráni observation–mutation race, ale nehovorí, že rewrite je organizačne povolený alebo že downstream users boli koordinovaní.

Po úspechu vykonaj nový fetch a read-back:

```bash
git fetch origin
test "$(git rev-parse refs/remotes/origin/feature/ord-8421)" = "$(git rev-parse HEAD)"
```

Test potvrdí lokálnu zhodu po novom server observation pointe. Neoveruje merge do main, CI ani artifact publication.""",
)

insert_before_incident(
    "merge-and-rebase.md",
    r"""## Mechanický walkthrough: merge a rebase ako dve state machines

Pred integráciou zachovaj oba tipy a merge base:

```bash
feature_before=$(git rev-parse feature/ord-8421)
main_before=$(git rev-parse origin/main)
base=$(git merge-base feature/ord-8421 origin/main)
printf 'base=%s feature=%s main=%s\n' "$base" "$feature_before" "$main_before"
```

`merge-base` vyberie best common ancestor pre graph, nie nevyhnutne „časovo posledný“ commit podľa dátumu. Three-way merge porovná stavy base→feature a base→main.

Merge walkthrough:

```bash
git switch feature/ord-8421
git merge --no-commit --no-ff origin/main
```

`--no-commit` zastaví pred vytvorením merge commit-u, ak merge nie je fast-forward. Index a working tree obsahujú navrhnutý integrated snapshot; `.git/MERGE_HEAD` drží druhý parent. Teraz možno čítať:

```bash
git status
git diff --cached
git rev-parse MERGE_HEAD
```

Ak výsledok nie je správny, `git merge --abort` obnoví pre-merge state, pokiaľ unrelated local changes nebránia bezpečnej obnove. Ak je správny, tests bežia ešte pred `git commit`. Nový merge commit dostane current HEAD ako first parent a MERGE_HEAD ako ďalší parent.

Rebase walkthrough:

```bash
git switch feature/ord-8421
git branch safety/ord-8421-before-rebase
git rebase origin/main
```

Rebase dočasne identifikuje commits reachable z feature, ale nie z upstreamu, checkout-ne nový base a replayuje ich v poradí. Pri každom replayi vytvorí nový commit. Safety branch drží starý graph pre `range-diff` a recovery.

Po rebase:

```bash
git range-diff \
  origin/main...safety/ord-8421-before-rebase \
  origin/main...feature/ord-8421

git diff origin/main...feature/ord-8421
```

`range-diff` porovná commit series a pomáha odhaliť, že počas conflict resolution sa patch zmenil alebo zmizol. Final `diff ...` ukáže výsledný feature change voči merge base. Ani jeden command nespustí domain tests.

Pri konflikte rebase index stages opisujú current replay context. `ours/theirs` labels môžu prekvapiť, pretože „ours“ je často nový upstream state a „theirs“ replayovaný commit. Namiesto file-level shortcutu čítaj:

```bash
git show :1:path
git show :2:path
git show :3:path
git status
```

Po resolution `git add` vloží jeden výsledný blob do stage 0 a `git rebase --continue` vytvorí nový replay commit. `--skip` odstráni celý aktuálny patch; nepoužívaj ho iba preto, že konflikt je nepríjemný.

Rozhodnutie medzi merge a rebase preto zahŕňa dve otázky: aký final snapshot chceme a aký ancestry/audit model má zostať publikovaný. Rovnaký tree hash neznamená rovnakú históriu alebo dôkaznú identitu.""",
)

insert_before_incident(
    "reset-revert-restore.md",
    r"""## Mechanický rozhodovací postup pred každou „návratovou“ operáciou

Najprv si zapíš štyri observations:

```bash
git status --short
git rev-parse HEAD
git diff
git diff --cached
```

Potom odpovedz: chceš zmeniť working file, index, branch ref alebo publikovanú históriu? Rovnaké slovo „undo“ nestačí.

### Obnova working file-u

```bash
git restore --source=HEAD --worktree -- config/orders.yaml
```

Source je HEAD tree, destination iba working tree. Index zostane nedotknutý. Ak bol staged obsah odlišný od HEAD, working file sa môže po restore líšiť od indexu. Explicitné `--source` a `--worktree` sú dlhšie, ale pri výučbe odstraňujú nejednoznačnosť.

### Odstageovanie

```bash
git restore --source=HEAD --staged -- config/orders.yaml
```

Destination je index. Working file zostane. Command nestratí edit, ale zmení budúci commit snapshot. Po ňom vždy pozri oba diffy.

### Soft/mixed/hard reset na commit

Predstav si:

```text
HEAD/main = C3
index     = tree C3 + staged S
worktree  = index + unstaged W
```

`git reset --soft C2` posunie iba `main/HEAD`; index a worktree ostanú. Rozdiel C2→index sa teda javí ako staged. `--mixed` navyše nastaví index na C2, takže všetky odchýlky ostanú iba vo working tree. `--hard` nastaví aj tracked working files na C2 a S/W stratí.

Bezpečný lab:

```bash
git branch safety/before-reset
git reset --soft HEAD~1
git status --short
git diff --cached
```

Safety branch nie je povinnosť Git-u; je to explicitný recovery ref. Ak overíš výsledok, môžeš ju neskôr zmazať.

### Revert publikovaného commit-u

```bash
git show --stat BAD_SHA
git revert --no-commit BAD_SHA
git diff --cached
```

`--no-commit` pripraví inverse patch v indexe a working tree bez okamžitého commit-u. To umožní test a prípadnú úpravu, ak neskorší code zmenil context. Po validácii vytvor nový commit. Ak inverse nie je bezpečný, `git revert --abort` obnoví sequencer state.

Pri merge commit-e:

```bash
git show --no-patch --format='%H parents=%P' MERGE_SHA
git revert -m 1 --no-commit MERGE_SHA
```

`-m 1` neznamená „revert first parent“. Hovorí, že parent 1 je mainline, ktorú chceme zachovať, a Git má odstrániť net effect merge-u voči nej. Nesprávny parent môže obrátiť opačnú ancestry line.

### Recovery po hard reset-e

Bez ďalších mutations:

```bash
git reflog --date=iso
old=$(git rev-parse 'HEAD@{1}')
git branch recovery/hard-reset "$old"
```

Najprv vytvor ref, až potom prezeraj a rozhoduj. `HEAD@{1}` je príklad, nie univerzálna hodnota; reflog treba čítať podľa timestampu a action. Reflog nechráni untracked bytes ani obsah, ktorý nikdy nebol objectom.

Rozhodovacia pomôcka:

| Požadovaný výsledok | Typický command | Mení históriu/ref | Riziko |
|---|---|---|---|
| zahodiť working edit | `restore --worktree` | nie | prepíše tracked working bytes |
| odstageovať | `restore --staged` | nie | zmení budúci commit snapshot |
| preformovať lokálny posledný commit | `reset --soft/mixed` | áno, lokálne | history rewrite |
| úplne vrátiť lokálny tracked stav | `reset --hard` | áno | stratí uncommitted tracked work |
| zrušiť publikovanú zmenu auditovateľne | `revert` | pridá nový commit | inverse môže mať semantic conflict |

Tabuľka je default, nie náhrada inspection. Paths, modes a operation state môžu semantics zmeniť.""",
)

insert_before_incident(
    "cherry-pick-and-stash.md",
    r"""## Mechanický walkthrough: čo sa replayuje a čo zostáva lokálne

Pred cherry-pickom over patch aj parent context:

```bash
source_commit=<sha>
git show --no-patch --format='commit=%H parent=%P tree=%T subject=%s' "$source_commit"
git diff "$source_commit^" "$source_commit"
```

Cherry-pick nereuse-ne commit object. Zoberie diff parent→source commit a skúsi ho aplikovať na current index/working tree. Preto commit s viacerými parents potrebuje mainline voľbu podobne ako revert merge-u.

```bash
git switch release/4.1
git branch safety/release-4.1-before-backport
git cherry-pick -x "$source_commit"
```

`-x` pridá traceability text do message iba pri clean command-line cherry-picku; cryptograficky nespája commits. Po úspechu porovnaj patch equivalence a testy:

```bash
new_commit=$(git rev-parse HEAD)
git patch-id --stable < <(git show "$source_commit")
git patch-id --stable < <(git show "$new_commit")
```

`patch-id` normalizuje diff a môže podporiť tvrdenie, že patches sú podobné. Neberie do úvahy parent runtime context, takže nie je compatibility oracle.

Pri range syntaxe:

```bash
git cherry-pick A^..C
```

shell odovzdá jednu revision expression a Git vyberie reachable set podľa revision walkeru; výsledné poradie nemusí byť zrejmé z názvov. Pred mutation zobraz presný zoznam:

```bash
git rev-list --reverse --topo-order A^..C
```

Stash walkthrough:

```bash
git status --short
git stash push -u -m 'WIP ORD-8421 validation'
git stash list
git stash show --stat stash@{0}
git stash show -p stash@{0}
```

`-u` pridá untracked files, ale nie ignored files. Stash zaznamená base, index a working state do commit-like objects a posunie `refs/stash` reflog. Potom obnoví tracked working tree/index; neznamená to cloud backup.

Bezpečnejšie obnovenie:

```bash
git stash apply --index stash@{0}
git status --short
git diff
git diff --cached
# až po review a testoch:
git stash drop stash@{0}
```

`apply --index` sa pokúsi obnoviť aj pôvodnú staged hranicu. Ak konflikt vznikne, stash entry zostáva. `pop` kombinuje apply a podmienený drop, čím skracuje čas na inspection; preto je pri dôležitej práci explicitný apply/drop čitateľnejší.

`git stash branch recovery/wip stash@{0}` najprv vytvorí branch na pôvodnom base commit-e stashu, checkout-ne ju a aplikuje entry. To často znižuje konflikt, pretože context je bližší momentu uloženia. Po úspechu stash odstráni; pred command-e preto poznaj entry identity a prípadne si vytvor ďalší ref.

Secrets a generated credentials nepatria do stashu. Stash objects sú súčasťou `.git`, môžu prežiť dlhšie než pracovný file a môžu sa dostať do backupu repository directory.""",
)

insert_before_incident(
    "merge-conflicts.md",
    r"""## Mechanický conflict-resolution walkthrough

Keď operácia zastane, najprv urč jej typ a rozsah:

```bash
git status
git diff --name-only --diff-filter=U
git ls-files -u
```

`status` pomenuje merge/rebase/cherry-pick sequencer a navrhne správne `--continue` alebo `--abort`. `diff-filter=U` ukáže unresolved paths. `ls-files -u` vypíše mode, blob ID, stage a pathname; jeden path môže mať stages 1/2/3, ale pri add/delete konflikte niektorá stage chýba.

Pre jeden textový file si vytiahni tri samostatné inputs:

```bash
git show :1:config/orders.yaml > /tmp/orders.base
git show :2:config/orders.yaml > /tmp/orders.ours
git show :3:config/orders.yaml > /tmp/orders.theirs
```

Ak niektorá stage neexistuje, command skončí non-zero; to je informácia o conflict type, nie dôvod vytvoriť prázdny file. Porovnaj:

```bash
diff -u /tmp/orders.base /tmp/orders.ours || true
diff -u /tmp/orders.base /tmp/orders.theirs || true
```

Teraz je viditeľný intent každej strany voči spoločnému base-u. Conflict markers vo working file-i sú iba convenience representation a môžu obsahovať viac hunkov.

Resolution vytvor ako nový celý file. Potom:

```bash
git add config/orders.yaml
git ls-files -u -- config/orders.yaml
git diff --cached -- config/orders.yaml
git diff --check
```

Po `git add` má `ls-files -u` pre path zostať prázdny, pretože index už drží iba stage 0 blob. To dokazuje syntaktické označenie „resolved“, nie domain správnosť. `diff --cached` je rozhodujúci review subject.

Pri merge výsledok porovnaj s oboma parents po vytvorení commit-u:

```bash
git diff HEAD^1 HEAD -- config/orders.yaml
git diff HEAD^2 HEAD -- config/orders.yaml
```

Prvý diff ukáže, čo merge pridal voči current line; druhý, čo pridal voči druhej strane. Ak file-level `--ours` zahodil unrelated validation, jeden z týchto diffov to odhalí.

Rename/delete konflikty čítaj cez status a raw diff:

```bash
git diff --raw --find-renames
git status --short
```

Rename je heuristika odvodená z podobnosti. Resolution môže vyžadovať `git rm OLD`, `git add NEW` alebo nový pathname; nepokúšaj sa iba odstrániť markers.

Po resolution spusti najnižší relevantný test a následne širší integration gate. Conflict je miesto, kde sa dve zmeny stretli; testovať iba jeden pôvodný feature path je slabý oracle.

Ak zistíš, že nemáš dosť domain informácií, abort je validný výsledok:

```bash
git merge --abort
# alebo
git rebase --abort
# alebo
git cherry-pick --abort
```

Použi command zodpovedajúci aktívnej state machine. Ručné mazanie `.git/MERGE_HEAD` alebo rebase directories môže zanechať index a refs v nekonzistentnom stave.""",
)

insert_before_incident(
    "branching-strategies.md",
    r"""## Praktický branch lifecycle a dôkazné body

Stratégia sa dá overiť iba konkrétnym ref transitionom. Krátko žijúca feature branch môže používať:

```bash
git fetch origin
git switch --create feature/ord-8421 --track origin/main
base=$(git rev-parse origin/main)
printf 'branch_base=%s\n' "$base"
```

`--track` nastaví upstream; neznamená, že feature sa bude automaticky synchronizovať. `base` je initial observation, ktorý treba pri review nahradiť current merge candidate identity.

Po malých commitoch:

```bash
git fetch origin
git log --oneline --left-right origin/main...HEAD
git diff --stat origin/main...HEAD
```

Triple-dot diff používa merge base a ukáže feature intent voči spoločnému predkovi. Left/right log ukáže divergence na oboch stranách. Ak main postúpil, branch evidence z predchádzajúceho CI runu môže byť stale.

Pred pushom a merge requestom:

```bash
git rebase origin/main       # iba ak tím povoľuje rewrite feature history
git push --force-with-lease  # iba po koordinovanom rebase
git range-diff safety/before...HEAD
```

Alternatívny tímový contract použije merge z main a obyčajný push. Dôležité je, aby history strategy bola explicitná a server policy ju podporovala.

Merge queue alebo merge-result pipeline má testovať exact candidate:

```text
source tip S
+ current target T
→ synthetic candidate C
→ required evidence bound to C
→ atomic ref update T → C
```

Ak target medzitým prejde na T2, evidence pre C sa invaliduje. Branch protection, ktorá iba vyžaduje zelený source-branch pipeline, túto race úplne nerieši.

Hotfix propagation si zapíš ako machine-readable matrix:

```yaml
hotfix: CVE-2026-8421
sourceCommit: abc123
requiredLines:
  main: pending
  release/4.2: applied
  release/4.1: not-applicable
```

Každý applied entry potrebuje vlastný commit/artifact/test identity. Cherry-pick message s `-x` pomáha traceability, ale matrix uzatvára až evidence pre všetky podporované lines.

Environment branches kontroluj otázkou: mení merge source bytes a vyvoláva rebuild, alebo iba desired release reference? Ak `prod` branch recompiluje source, nejde o promotion rovnakého artifactu. Bezpečnejší deployment repository mení immutable digest a environment configuration, pričom application source history zostáva oddelená.

Server-side controls treba read-backnúť cez hosting API a overiť negatívnym testom. Dokument „force push je zakázaný“ nemá enforcement hodnotu, ak branch setting povoľuje Maintainer bypass.""",
)

insert_before_incident(
    "monorepo-vs-multirepo.md",
    r"""## Praktický rozbor affected graphu a cross-repository transitionu

Changed paths nie sú dependency graph. V monorepe môže zmena v `libs/contracts` ovplyvniť služby, ktoré sa samy v diff-e nenachádzajú. Minimálny observation je:

```bash
base=$(git merge-base origin/main HEAD)
git diff --name-status "$base" HEAD
git diff --name-only "$base" HEAD > /tmp/changed-paths.txt
```

Tento zoznam je input pre build-graph tool, nie konečný affected set. Tool musí poznať edges, napríklad:

```text
libs/contracts
├── services/orders
├── services/payments
└── clients/web
```

Ak cache key používa iba hash vlastného directory, consumer môže reuse-nuť output vytvorený so starou shared library. Správny key zahŕňa transitive source/dependency/toolchain inputs alebo používa hermetic action graph.

Atomic source commit v monorepe stále neznamená atomic runtime. Predstav si commit, ktorý pridá optional response field a aktualizuje web client. Ak server deployne prvý, starý client musí field ignorovať. Ak client deployne prvý, starý server nesmie spôsobiť failure. Compatibility matrix je potrebný aj pri spoločnom commit-e.

Multirepo transition zapisuje versions explicitne:

```text
contract artifact: orders-schema 2.3.0 @ digest D23
producer tested with: 2.2.0, 2.3.0
consumer-web tested with: 2.2.0, 2.3.0
consumer-batch tested with: 2.2.0 only
retirement gate: no 2.2.0 traffic for 14 days
```

Pipeline jednotlivého repository má uložiť dependency lock/digest. Testovanie proti `latest` nevie spätne určiť, ktorý contract bol použitý. Cross-repo coordinator alebo release manifest potom skladá immutable versions do jedného integration subjectu.

Pri rozhodovaní o rozdelení zmeraj reálne change coupling:

```text
koľko PRs pravidelne mení oba komponenty
koľko incidentov vzniká z compatibility gapu
koľko CI času spotrebuje nepresný affected graph
kto potrebuje read/write access k celej histórii
či release a compliance lifecycle sú naozaj oddelené
```

Repo split nie je iba presun directories. Mení commit IDs, CODEOWNERS, secrets/tokens, CI provenance, package coordinates, issue links a release automation. Migračný plan potrebuje source-history mapping a obdobie, v ktorom staré repository už nie je writer.

Generated code sa publikuje ako artifact s source schema digestom a generator version. Ručné kopírovanie medzi repositories vytvára hidden source a znemožňuje zistiť, či consumer používa správnu generation.""",
)

insert_before_incident(
    "bash-automation.md",
    r"""## Mechanický rozbor kľúčových Bash vzorov

Táto časť rozoberá ukážky tak, ako ich interpretuje shell. Pri Bash bezpečnosti je často dôležitejší presný evaluation order než samotný počet riadkov.

### Čo robí `set -Eeuo pipefail`

```bash
set -Eeuo pipefail
```

- `-e` po vybranom neúspešnom simple command-e ukončí shell. Neplatí rovnako v `if`, `while`, ľavej strane `&&/||`, negácii `!` a rôznych subshell/pipeline kontextoch. Preto nie je exception mechanizmom.
- `-E` dedí `ERR` trap do functions, command substitutions a subshells, kde by sa inak nemusel spustiť. Nemá vplyv na `EXIT` trap.
- `-u` spôsobí chybu pri expanzii unset premennej. Optional hodnotu preto čítaj napríklad `${timeout_seconds:-30}`; `${value-}` a `${value:-}` sa líšia pri empty stringu.
- `pipefail` nastaví status pipeline na pravý najneskorší nenulový status, namiesto statusu posledného commandu. Stále treba vedieť, ktorý command zlyhal; array `${PIPESTATUS[@]}` treba zachytiť okamžite po pipeline.

Explicitný error branch:

```bash
if ! output=$(command-that-may-fail 2>&1); then
  rc=$?
  printf 'command failed rc=%s: %s\n' "$rc" "$output" >&2
  exit 4
fi
```

Tento zápis má jednu pascu: po `!` je `$?` status negovaného compound commandu, teda pri vstupe do branchu môže byť 0. Ak potrebuješ pôvodný status, nepouži `!` takto:

```bash
set +e
output=$(command-that-may-fail 2>&1)
rc=$?
set -e
if ((rc != 0)); then
  printf 'command failed rc=%s: %s\n' "$rc" "$output" >&2
  exit 4
fi
```

Ešte čitateľnejšie je dať command do `if`, keď stačí success/failure a nepotrebuješ pôvodný rc. Command-specific statusy ako grep 1 alebo git diff 1 však vyžadujú explicitnú klasifikáciu.

### Arrays zachovávajú argument boundaries

```bash
args=(plan --config "$config_path" --state "$state_path")
((dry_run)) && args+=(--dry-run)
python3 "$tool" "${args[@]}"
```

Pri assignment-e array elementy vzniknú už po quoting pravidlách. `"${args[@]}"` expanduje každý element ako jeden samostatný argument. Naproti tomu `${args[*]}` v quotes vytvorí jeden string spojený prvým znakom `IFS`; bez quotes znovu zapne word splitting a globbing.

Over si argumenty bez ich vykonania:

```bash
printf 'arg=<%q>\n' python3 "$tool" "${args[@]}"
```

`%q` vytvorí shell-escaped diagnostický zápis. Nie je to command na následné `eval`; slúži na audit boundaries.

### Argument parser krok po kroku

```bash
while (($#)); do
  case $1 in
    --config)
      (($# >= 2)) || { printf 'missing value for --config\n' >&2; exit 2; }
      config_path=$2
      shift 2
      ;;
```

`$#` je počet zostávajúcich positional parameters. `case $1` je bezpečný bez quotes v tejto syntaktickej pozícii, pretože `case` nevykonáva word splitting ako obyčajný command argument. Po kontrole minimálne dvoch arguments sa `$2` uloží a `shift 2` odstráni option aj value. Ak user zadá `--config --dry-run`, jednoduchý parser prijme `--dry-run` ako value; robustnejší contract môže odmietnuť value začínajúcu `-` alebo podporovať `--config=PATH`.

`--` ukončuje option parsing. Zostávajúce values možno interpretovať ako positional arguments. Ak ich script nepodporuje, po loop-e skontroluj `(($# == 0))`.

### Temporary directory a trap — pôvodná ukážka

```bash
tmp_dir=$(mktemp -d)
cleanup() {
  rc=$?
  rm -rf -- "$tmp_dir"
  exit "$rc"
}
trap cleanup EXIT INT TERM
```

Riadok `tmp_dir=$(mktemp -d)` spustí external command a zachytí jeho stdout bez trailing newlines. `mktemp -d` atomicky vytvorí unikátny directory podľa platformovej šablóny; je bezpečnejší než zostavenie `/tmp/my-script-$$`, ktoré môže byť predvídateľné alebo preexistovať. Pri `set -e` failure command substitution typicky ukončí assignment command, ale explicitný check je čitateľnejší.

V `cleanup` sa `rc=$?` musí vykonať ako prvý command. `$?` obsahuje status commandu alebo signalu, ktorý aktivoval trap. Keby najprv prebehol `printf` alebo `rm`, pôvodný status by sa prepísal.

`rm -rf -- "$tmp_dir"` používa quotes, aby path ostal jeden argument, a `--`, aby path začínajúci `-` nebol option. Samotné `-rf` je stále nebezpečné, ak `tmp_dir` môže byť empty, `/` alebo user-controlled shared path. V ukážke je hodnota vytvorená skriptom a nemení sa.

`trap cleanup EXIT INT TERM` registruje rovnakú function pre normal exit aj signals. Tu vzniká subtlety: handler pre `INT` alebo `TERM` zavolá `exit`, čo následne aktivuje aj `EXIT` trap. Cleanup preto môže prebehnúť dvakrát. `rm -rf` je v tomto prípade idempotentný, ale iný cleanup, napríklad revoke lease alebo upload evidence, nemusí byť.

Robustnejší vzor:

```bash
umask 077
tmp_dir=''
cleanup_running=0

cleanup() {
  rc=$?
  ((cleanup_running == 0)) || return "$rc"
  cleanup_running=1
  trap - EXIT INT TERM

  if [[ -n $tmp_dir && -d $tmp_dir && $tmp_dir == "${TMPDIR:-/tmp}"/* ]]; then
    rm -rf -- "$tmp_dir"
  fi
  exit "$rc"
}

trap cleanup EXIT INT TERM

tmp_dir=$(mktemp -d "${TMPDIR:-/tmp}/atlas-release.XXXXXXXX") || {
  printf 'unable to create temporary directory\n' >&2
  exit 4
}
```

`umask 077` spôsobí, že novo vytvorené files/directories budú defaultne dostupné iba ownerovi, pokiaľ command explicitne nenastaví širší mode. Prázdna initial value umožní bezpečný cleanup aj vtedy, keď failure nastane pred `mktemp`. Guard zabráni reentrancy a `trap -` odstráni handlers pred `exit`. Prefix check je defense-in-depth; ešte silnejšie je neumožniť žiadnu mutation premennej po create.

Signal-specific exit code možno zachovať samostatnými handlers, napríklad 130 pre INT a 143 pre TERM. `$?` v signal trap-e nemusí vždy reprezentovať shell convention, ktorú chce CLI publikovať.

Pri secrets:

```bash
set +x
secret_file="$tmp_dir/credential"
install -m 600 /dev/null "$secret_file"
# write secret without echoing it
```

`set +x` vypne xtrace pred secret-bearing commands. Treba ho vypnúť skôr, než sa secret objaví v expanded argumente. Temporary cleanup neodstraňuje secret, ktorý už unikol do process listu, CI trace alebo child environmentu.

### File lock a descriptor 9

```bash
exec 9>"$state_path.lock"
if ! flock -n 9; then
  printf 'another apply is running\n' >&2
  exit 3
fi
```

`exec` bez commandu aplikuje redirection na current shell. Shell otvorí lock file na write a priradí ho file descriptoru 9. Descriptor zostane otvorený do close alebo process exit-u. `flock -n 9` skúsi non-blocking exclusive lock viazaný na open file description.

Path file-u nie je samotný lock. Ochranu drží kernel lock na otvorenom descriptore. Zmazanie lock file-u iným processom môže vytvoriť nový inode a druhý nezávislý lock, preto cleanup nemá lock pathname mazať počas aktívnych writerov.

Explicitné close:

```bash
flock -u 9
exec 9>&-
```

Väčšinou sa lock drží cez observe recheck, mutation a verify a uvoľní sa pri exit-e. `flock` semantics na NFS alebo non-Linux platforme sa môžu líšiť; distribuovaný state potrebuje backend-native coordination.

### Plan, apply a verify a exit propagation

```bash
plan_file="$tmp_dir/plan.json"
python3 tools/atlasctl.py plan ... >"$plan_file"
```

Redirection file otvorí ešte pred spustením Pythonu. Ak command zlyhá, môže zostať prázdny alebo partial file. Apply ho preto nesmie používať iba preto, že path existuje. Python plan command musí zapisovať validný complete JSON a exit status 0 až po úspechu; wrapper môže navyše validovať `jq -e`.

```bash
if ! jq -e '.schemaVersion == 1 and .desiredFingerprint' "$plan_file" >/dev/null; then
  printf 'plan output is incomplete\n' >&2
  exit 3
fi
```

Pri dry-run `cat "$plan_file"` publikuje plán na stdout. Progress predtým musí ísť na stderr, inak stdout prestane byť jeden JSON document.

Apply success nepreukazuje verify. Wrapper musí zachytiť native exit code a verify spustiť samostatne. Ak apply vráti 3 pre stale plan, wrapper ho nemá premapovať na generic 4 bez zachovania classu.

### Pipeline status a `PIPESTATUS`

```bash
validate-config | tee validation.log
status=("${PIPESTATUS[@]}")
```

`PIPESTATUS` je array statusov poslednej foreground pipeline. Musí sa skopírovať okamžite; aj `printf` ho prepíše. S dvoma commands je `status[0]` validator a `status[1]` tee. `pipefail` nastaví `$?`, ale array ukáže presného vinníka.

```bash
if ((status[0] != 0)); then
  printf 'validator failed rc=%s\n' "${status[0]}" >&2
  exit 2
fi
if ((status[1] != 0)); then
  printf 'unable to persist validation log rc=%s\n' "${status[1]}" >&2
  exit 4
fi
```

Tieto failures majú odlišný význam: invalid config verzus evidence-storage failure.

### Signals a child process

Ak shell už nepotrebuje cleanup, `exec child ...` nahradí shell rovnakým PID a orchestrator signal ide priamo childovi. Ak cleanup potrebuje, spusti child na pozadí, ulož PID, forwarduj signals a `wait`-ni:

```bash
child_pid=''
forward_term() {
  [[ -n $child_pid ]] && kill -TERM "$child_pid" 2>/dev/null || true
}
trap forward_term TERM INT

python3 tools/atlasctl.py apply ... &
child_pid=$!
set +e
wait "$child_pid"
rc=$?
set -e
child_pid=''
exit "$rc"
```

Tento zjednodušený vzor stále nerieši process group a grandchildren. Pre komplexné supervision je vhodný runtime alebo programovací jazyk s explicitným subprocess modelom.""",
)

insert_before_incident(
    "powershell-fundamentals.md",
    r"""## Mechanický rozbor kľúčových PowerShell vzorov

### Object pipeline nie je vizuálna tabuľka

```powershell
Get-ChildItem -Path . -File |
    Where-Object Length -gt 1MB |
    Select-Object Name, Length
```

`Get-ChildItem` zapisuje do success streamu `FileInfo` objekty. Pipeline enumeruje každý object. Skrátená syntax `Where-Object Length -gt 1MB` bindne property `Length`, porovná integer bytes s hodnotou `1MB` a prepustí matching objects. `Select-Object` vytvorí nové projected objects iba s properties `Name` a `Length`.

Ak na koniec pridáš `Format-Table`, pipeline dostane formatting instruction objects určené hostu. Už nejde o pôvodné `FileInfo` a ďalšie `Where-Object Length` nebude mať očakávaný property. Formatting preto patrí až za machine-processing boundary.

Over type:

```powershell
$item = Get-ChildItem -Path . -File | Select-Object -First 1
$item.GetType().FullName
$item | Get-Member
```

Po remoting alebo JSON round-tripe môže type a methods zmiznúť. Consumer má používať explicitný serialization contract, nie predpoklad živého .NET objectu.

### Advanced parameter binding

```powershell
[CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'Medium')]
param(
    [Parameter(Mandatory)]
    [ValidateScript({ Test-Path -LiteralPath $_ -PathType Leaf })]
    [string]$ConfigPath
)
```

`CmdletBinding` mení script/function na advanced command a pridáva common parameters. `Mandatory` rieši prítomnosť inputu, nie jeho business platnosť. `ValidateScript` sa vykoná počas bindingu; `$_` je candidate value. Použitie `-LiteralPath` zabráni wildcard interpretácii.

Validation môže byť subjectom TOCTOU race: file existuje pri bindingu a zmení sa pred readom. Kritický apply musí po získaní locku znovu otvoriť/canonicalizovať file a overiť fingerprint.

### Streams a návratová hodnota

PowerShell automaticky zapisuje neassignnutý expression output do success streamu:

```powershell
function Get-Result {
    'starting'                       # toto je tiež success output
    [pscustomobject]@{ Status='OK' } # a toto tiež
}
```

Caller dostane array dvoch objects, nie jeden result. Progress používaj cez `Write-Verbose`, `Write-Information` alebo `Write-Host` podľa contractu a success stream nechaj iba pre data.

```powershell
function Get-Result {
    [CmdletBinding()]
    param()
    Write-Verbose 'Starting calculation'
    [pscustomobject]@{ Status='OK' }
}
```

Pri redirectoch poznaj stream numbers; napríklad `2>` je error stream a `*>` všetky streams. Zlúčenie všetkého do stdout môže zničiť JSON API rovnako ako v Bash.

### Terminating a non-terminating error

```powershell
try {
    $content = Get-Content -LiteralPath $ConfigPath -Raw -ErrorAction Stop
}
catch {
    Write-Error "Unable to read config: $($_.Exception.Message)"
    exit 2
}
```

`-ErrorAction Stop` zmení error record tohto cmdletu na terminating error, takže execution preskočí do `catch`. `catch` premenná `$_` je `ErrorRecord`, nie iba Exception. Obsahuje category, target object, invocation info a stack information.

`Write-Error` v catch môže samo vytvoriť non-terminating error podľa preference. Na CLI boundary je často čitateľnejšie zapísať bounded diagnostic na error stream a `return` stabilný code z `main`, než volať `exit` hlboko vo function.

```powershell
function Invoke-Main {
    try { ...; return 0 }
    catch [System.IO.IOException] { Write-Error $_; return 2 }
}
exit (Invoke-Main)
```

`finally` sa vykoná pri success aj exception. Cleanup nesmie prepísať primary error bez explicitnej policy.

### Native process a `$LASTEXITCODE`

```powershell
& git diff --quiet
$gitExit = $LASTEXITCODE
```

Call operator `&` spustí native executable alebo command path. `$LASTEXITCODE` musíš skopírovať okamžite, pretože ďalší native command ho zmení. `$?` je boolean success poslednej PowerShell pipeline a jeho správanie sa v rôznych versions/native preference nastaveniach môže líšiť.

Git contract:

```powershell
switch ($gitExit) {
    0 { $dirty = $false }
    1 { $dirty = $true }
    default { throw "git diff failed with exit code $gitExit" }
}
```

Exit 1 nie je tool crash; je „differences exist“. Mapovanie command-specific statuses je súčasť wrappera.

### `ShouldProcess` a nested mutations

```powershell
if ($PSCmdlet.ShouldProcess($StatePath, 'Apply Atlas desired state')) {
    Set-Content -LiteralPath $StatePath -Value $payload
}
```

Pri `-WhatIf` vráti `ShouldProcess` false a body sa nevykoná. Ak však helper pred gate-om už vytvoril directory, získal cloud token alebo zmenil temp state, dry-run nie je side-effect free. Najprv resolve/observe/plan, potom všetky mutácie umiestni za gate.

Nested function môže sama deklarovať `SupportsShouldProcess` a caller má forwardovať `-WhatIf:$WhatIfPreference`. Alternatívne nech iba top-level function vlastní mutation gate a helpers nemutujú mimo nej. Mixed model často vytvára dvojité prompts alebo neúplný WhatIf.

### JSON serialization a depth

```powershell
$json = $result | ConvertTo-Json -Depth 10 -Compress
$roundTrip = $json | ConvertFrom-Json
```

`-Depth` určuje, ako hlboko sa nested objects serializujú; príliš malá hodnota môže orezať data a vydať warning. `-Compress` mení whitespace, nie semantics. PowerShell numbers, DateTime, enums, hashtables a ordered dictionaries sa mapujú do JSON s možnou stratou type fidelity.

Pre fingerprint nepoužívaj náhodný property order z ľubovoľného object graphu. Vytvor explicitný ordered DTO a definuj string/date/number representation. Po serialization over schema alebo round-trip values.

### Atomic file mutation

`Set-Content` priamo na production path môže pri process crashi nechať partial alebo truncated file. Bezpečnejší local pattern:

```powershell
$directory = Split-Path -Parent $StatePath
$temp = Join-Path $directory ('.' + [IO.Path]::GetRandomFileName())
try {
    [IO.File]::WriteAllText($temp, $json, [Text.UTF8Encoding]::new($false))
    [IO.File]::Move($temp, $StatePath, $true)
}
finally {
    Remove-Item -LiteralPath $temp -Force -ErrorAction SilentlyContinue
}
```

Temporary file je na rovnakom filesysteme, aby rename/replace mal platformovo čo najsilnejšiu atomicitu. Windows file-sharing handles, ACL inheritance a antivirus môžu operation ovplyvniť. Po Move stále potrebuješ content fingerprint a runtime verify.""",
)

insert_before_incident(
    "python-for-automation.md",
    r"""## Mechanický rozbor Python automation ukážok

### Parser vytvára syntaktický model, nie validný domain object

```python
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="atlasctl")
    sub = parser.add_subparsers(dest="command", required=True)
```

Function vytvorí nový parser pri každom volaní, čo zjednodušuje tests. `dest="command"` uloží zvolený subcommand do namespace a `required=True` odmietne prázdne CLI. `parse_args()` pri chybe štandardne vypíše diagnostic a vyvolá `SystemExit(2)`. Preto domain unit testy nemajú byť schované priamo v parser actions; parser testuje syntax, domain functions hodnoty.

Path argument ako `str` ešte nie je canonical path ani existujúci file. Po parse sa vykoná explicitný resolve, allowed-root check a read pod lockom podľa risku.

### Frozen dataclass

```python
@dataclass(frozen=True)
class OrdersConfig:
    service: str
    environment: str
    release: str
    max_order_amount: int
    currency: str
```

Dataclass vygeneruje `__init__`, equality a representation. `frozen=True` blokuje bežné assignmenty na fields po vytvorení, ale nerobí deep immutability, ak field obsahuje mutable list/dict. Type annotations nekontrolujú runtime input; `OrdersConfig(max_order_amount="five")` sa bez vlastnej validation vytvorí.

Bezpečný loader najprv parse-ne external data, odmietne unknown keys, explicitne skonvertuje typy a overí invariants. Až potom vytvorí dataclass. Equality je užitočná pre plan/no-op tests.

### Canonical fingerprint krok po kroku

```python
encoded = json.dumps(
    value,
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False,
).encode("utf-8")
return hashlib.sha256(encoded).hexdigest()
```

`sort_keys=True` stabilizuje object key order. Compact separators odstránia presentation whitespace. `ensure_ascii=False` zachová Unicode characters a následné UTF-8 encoding je explicitné. SHA-256 potom identifikuje presné canonical bytes.

Toto nie je univerzálny JSON canonicalization štandard. Floats, Decimals, negative zero, Unicode normalization a custom objects potrebujú presný contract. Pre money používaj integer minor units alebo decimal string. Fingerprint má obsahovať iba state, ktorého zmena má invalidovať plan.

Pri apply porovnaj tri identities:

```text
plan.desiredFingerprint == freshly loaded desired
plan.observedFingerprint == freshly observed current state
plan.tool/schema generation == current implementation contract
```

Chýbajúca tretia väzba umožní starému planu prejsť po zmene planning semantics.

### Atomic write detailne

```python
fd, temp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
temp = Path(temp_name)
```

`mkstemp` atomicky vytvorí file a vráti otvorený OS descriptor aj pathname. Je bezpečnejší než `NamedTemporaryFile` v niektorých Windows replace scenároch a než predvídateľné meno. Directory je rovnaký ako target, aby `os.replace` neprekročil filesystem boundary.

```python
with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
```

`fdopen` prenesie ownership descriptoru file objectu; context manager ho zavrie. Ak exception nastane pred `fdopen`, treba descriptor explicitne zavrieť — production helper môže mať ešte širší try/finally než skrátená ukážka.

`flush()` presunie Python userspace buffer do OS. `os.fsync()` žiada persistenciu file data/metadata podľa filesystem contractu. `os.replace(temp, path)` atomicky zmení directory entry z pohľadu readers na podporovanom filesysteme a prepíše existujúci target.

Pre crash durability po rename môže byť potrebný fsync parent directory. Atomic visibility neznamená durable commit po power loss. ACL/owner/mode nového file-u tiež nemusia automaticky kopírovať target; nastav ich pred replace alebo použi platformový contract.

`finally: temp.unlink(missing_ok=True)` odstráni leftover temp file. Po úspešnom replace temp pathname už neexistuje, takže je to no-op. Cleanup exception nemá prekryť primary mutation error bez diagnostic policy.

### Exceptions na správnej vrstve

```python
try:
    config = load_config(path)
except json.JSONDecodeError as error:
    raise InvalidConfiguration(f"invalid JSON at line {error.lineno}") from error
```

Lower adapter preloží parser-specific exception na domain error a zachová cause cez `from error`. Top-level `main` mapuje `InvalidConfiguration` na exit 2 a píše bounded diagnostic na stderr. Neočakávanú exception neprehltí; traceback je evidence pre tool defect.

```python
def main() -> int:
    try:
        return run_command(...)
    except InvalidConfiguration as error:
        print(str(error), file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
```

Functions pod `main` nemajú volať `sys.exit`, pretože by komplikovali unit tests a cleanup.

### Retry a unknown outcome

Retry loop musí používať absolute deadline:

```python
deadline = time.monotonic() + 30.0
for attempt in range(1, 4):
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise DeadlineExceeded()
    try:
        return client.create_rollout(
            operation_id=operation_id,
            timeout=min(5.0, remaining),
        )
    except RetryableTransportError:
        if attempt == 3:
            raise
        time.sleep(min(2 ** (attempt - 1), max(0.0, deadline - time.monotonic())))
```

`time.monotonic()` nie je ovplyvnený wall-clock adjustmentom. Stabilný `operation_id` je rovnaký cez všetky pokusy. Transport exception po send/commit boundary nevie povedať, či server mutation vykonal; client má najprv query-nuť operation status alebo rely-nuť na server deduplication.

Retry iba na status/error classes označené ako transient. Validation, authorization a precondition failure sa retryom spravidla neopraví a môže zbytočne zaťažovať dependency.

### Dependency injection v teste

Namiesto globálneho `requests`/clock/filesystemu:

```python
def apply_plan(plan: Plan, client: RolloutClient, clock: Clock) -> Result:
    ...
```

Test dodá fake client, ktorý zaznamená calls a simuluje timeout po commite. Fake musí implementovať rovnaký behavior contract, nie iba vracať pohodlný success. Integration test s reálnym sandbox API potom kontroluje adapter a serialization boundary.""",
)

insert_before_incident(
    "yaml-json-regular-expressions.md",
    r"""## Mechanický rozbor parserov, serializácie a regex hraníc

### Duplicate-key rejection v JSON

```python
def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate key: {key}")
        result[key] = value
    return result

value = json.loads(text, object_pairs_hook=no_duplicates)
```

Bežný `dict` už duplicate informáciu stratil, preto hook dostáva ordered list `(key, value)` pairs skôr, než sa object zostaví. Function iteruje a odmietne druhý výskyt. Hook sa volá pre každý nested JSON object, takže kontrola nie je iba top-level.

Tento kód nerieši limits na document size, nesting alebo number precision. `json.loads` môže parse-nuť veľmi veľký integer, ale downstream JavaScript/DB ho môže stratiť. Pre peniaze a IDs definuj representation v schema a domain modeli.

Ak JSON pochádza z bytes:

```python
text = raw.decode("utf-8", errors="strict")
```

Strict decoding odmietne invalid bytes namiesto silent replacement characters. BOM a alternate encodings musia mať explicitnú policy.

### Safe YAML loading a effective types

Všeobecný YAML vyžaduje pinned library. Príklad s PyYAML:

```python
from pathlib import Path
import yaml

raw = Path("orders.yaml").read_text(encoding="utf-8")
value = yaml.safe_load(raw)
if not isinstance(value, dict):
    raise ValueError("root must be a mapping")
```

`safe_load` blokuje Python-specific object constructors, ale nie všetky resource-exhaustion risks a nevaliduje domain schema. Library/version určuje YAML schema a implicitné scalar types. Po parse si vypíš typy v teste:

```python
assert isinstance(value["release"], str)
assert isinstance(value["maxOrderAmount"], int)
```

Anchors a merge keys môžu vytvoriť effective mapping odlišný od lokálneho textu. Review tool má vedieť zobraziť resolved model. Alias count/nesting limits sú potrebné pri nedôveryhodnom inpute.

### Schema verzus domain validation

Schema example:

```json
{
  "type": "object",
  "required": ["environment", "maxOrderAmount"],
  "additionalProperties": false,
  "properties": {
    "environment": {"enum": ["dev", "staging", "prod"]},
    "maxOrderAmount": {"type": "integer", "minimum": 1}
  }
}
```

`additionalProperties: false` zachytí typo field, ale komplikuje forward compatibility; versioning contract musí povedať, kedy sú unknown fields povolené. Schema nevie automaticky, že production limit nad 20 % vyžaduje approval. Domain function pracuje nad už schema-valid modelom a vydá odlišný error class.

### Controlled serialization

```python
serialized = json.dumps(
    model,
    ensure_ascii=False,
    sort_keys=True,
    indent=2,
) + "\n"
Path("generated.json").write_text(serialized, encoding="utf-8", newline="\n")
```

Explicitný key order a newline znižujú noisy diffs. Pretty JSON nie je automaticky canonical hashing formát. Pri YAML round-tripe môže serializer odstrániť comments/anchors a zmeniť quoting; preto human source a generated artifact často majú byť oddelené files.

Pred prepísaním source porovnaj semantic model a vykonaj atomic write. Serializer success nepreukazuje, že target platform config prijme alebo application načíta.

### Regex full match a escaping

```python
pattern = re.compile(r"req-[0-9a-f]{4,32}")
match = pattern.fullmatch(value)
```

Raw string zabráni Pythonu interpretovať väčšinu backslashes; regex engine stále interpretuje pattern. `fullmatch` vyžaduje pokrytie celého stringu, takže nepotrebuje `^...$` a vyhne sa multiline anchor prekvapeniam.

Ak pattern prichádza z YAML:

```yaml
operationIdPattern: 'req-[0-9a-f]{4,32}'
```

single quotes v YAML minimalizujú backslash escapes. V double-quoted YAML stringu majú backslashes vlastnú escape vrstvu. Pattern, programming language string a shell command sú tri odlišné parsers.

Pre literal user fragment používaj `re.escape(fragment)`, nie string concatenation do regex syntaxe. To rieši regex injection, nie ReDoS z okolitého patternu.

### ReDoS test

Nebezpečný pattern `(a+)+$` môže pri inpute `aaaa...!` explorovať veľa backtracking paths. Bezpečnostný gate zahŕňa:

```text
maximálnu input dĺžku
pattern review bez nested ambiguous quantifiers
engine s lineárnym-time contractom, ak treba
execution timeout alebo isolation
positive aj near-match performance test
```

Regex correctness test s krátkymi matches neodhalí complexity failure.

### Prečo `sed` YAML edit nevie, čo mení

```bash
sed -i 's/maxOrderAmount:.*/maxOrderAmount: 5000/' config/orders.yaml
```

Shell najprv odovzdá single-quoted script bez expanzie. Sed potom matchne text na každom zodpovedajúcom riadku podľa implementácie. Nevidí indentation scope, comments, anchors ani duplicate keys. Môže zmeniť:

```yaml
# maxOrderAmount: 1000
examples:
  maxOrderAmount: 2500
production:
  maxOrderAmount: 4000
```

na viac nesprávnych miest. Parser-based mutation vyberie exact object path, overí pôvodnú expected value, zmení model, schema/domain-validuje a až potom serializuje. Pri potrebe zachovať comments použi round-trip YAML library s explicitným version/tool contractom.""",
)

# Update README and central ledger.
readme = SECTION / "README.md"
text = readme.read_text(encoding="utf-8")
marker = "## Výkladový štandard\n"
if text.count(marker) != 1:
    raise RuntimeError("Section 03 README standard marker mismatch")
addition = """## Rozšírené vysvetľovanie príkazov a kódu

Všetkých 14 koncepčných kapitol obsahuje mechanický rozbor kľúčových ukážok. Pri Git commands sa vždy pomenúva source snapshot alebo ref, destination vrstva, mutation a následný read-back. Pri Bash, PowerShell a Python ukážkach sa vysvetľuje evaluation order, argument a stream boundaries, exit/error model, cleanup, locking, atomic write, serialization a unknown-outcome recovery. YAML, JSON a regex príklady oddeľujú parsing, schema/domain validation, canonicalization a runtime verification.

Cieľom nie je komentovať každý syntaktický znak, ale odstrániť skok medzi ukážkou a záverom. Čitateľ má po príklade vedieť predpovedať zmenu stavu, interpretovať output a vysvetliť failure path.

"""
text = text.replace(marker, addition + marker, 1)
readme.write_text(text, encoding="utf-8")

ledger_path = REPO / "DOCUMENTATION-REVIEW-STATUS.md"
ledger = ledger_path.read_text(encoding="utf-8")
ledger = re.sub(
    r"^\| `03-git-and-automation`[^\n]*$",
    "| `03-git-and-automation` — Git and Automation Basics | 15/15 integrated full prose, practical and code-explanation revalidation | Ready for user review | 2026-08-01 | Všetkých 14 koncepčných kapitol bolo rozšírených o mechanický walkthrough príkazov a kódu. Git blok vysvetľuje object/index/ref mutations, fetch/push/refspec, merge/rebase state machines, restore/reset/revert, cherry-pick/stash, conflict stages, branch evidence a repository affected graph. Automation blok detailne rozoberá Bash expanzie/parser/trap/lock/pipeline/signals, PowerShell object pipeline/streams/errors/ShouldProcess/serialization, Python parser/model/fingerprint/atomic write/retry a YAML/JSON/regex parser a validation boundaries. Existing end-to-end walkthrough zostáva záverečnou integráciou. Navigation, glossary a full documentation audit boli synchronizované. |",
    ledger,
    count=1,
    flags=re.MULTILINE,
)
ledger_path.write_text(ledger, encoding="utf-8")

python_bin = os.environ.get("PYTHON_BIN", "python")
run(python_bin, "scripts/update_navigation.py", "--write")
run(python_bin, "scripts/update_glossary.py", "--write")
run(python_bin, "scripts/audit_learning_depth.py", "--all-docs", "--report", "DOCUMENTATION-AUDIT.md", "--json", "documentation-audit.json")

run("git", "config", "user.name", "github-actions[bot]")
run("git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
run("git", "add", "docs/03-git-and-automation", "DOCUMENTATION-REVIEW-STATUS.md", "DOCUMENTATION-AUDIT.md", "documentation-audit.json", "GLOSSARY.md", "glossary")
run("git", "commit", "-m", "docs(git): expand command and code explanations")
run("git", "push", "origin", f"HEAD:{BRANCH}")
