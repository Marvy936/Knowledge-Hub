# Clone, fetch, pull a push

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Git and Automation Basics
- Predpoklady: [Commit, branch, tag a HEAD](commit-branch-tag-head.md)
- Súvisiace témy: remote, refspec, tracking branch, fast-forward, authentication, partial clone

## 1. Distribuovaný model

Každý bežný Git clone obsahuje vlastnú object database, refs a históriu. Remote repository nie je centrálna databáza, ktorú lokálny Git priebežne priamo upravuje.

```text
local repository ← fetch/pull → remote repository
local repository → push → remote repository
```

Remote je pomenovaná konfigurácia URL a ref mappingu.

```bash
git remote -v
git remote get-url origin
```

## 2. Clone

`git clone` typicky:

1. vytvorí nový repository,
2. nakonfiguruje remote `origin`,
3. prenesie reachable objects a refs,
4. vytvorí remote-tracking refs,
5. vytvorí a checkoutne lokálnu branch.

```bash
git clone https://example.com/team/repo.git
git clone --branch release/1.x --single-branch <url>
```

Clone nie je iba download working files. Obsahuje históriu a metadata podľa zvoleného clone režimu.

## 3. Fetch

`git fetch` komunikuje s remote, prenesie chýbajúce objects a aktualizuje remote-tracking refs.

```bash
git fetch origin
git fetch --all --prune
```

Fetch štandardne nemení aktuálny working tree ani lokálnu branch.

Po fetchi:

```bash
git log --oneline main..origin/main
git diff main...origin/main
git branch -vv
```

## 4. Refspec

Refspec mapuje source ref na destination ref.

Typický fetch refspec:

```text
+refs/heads/*:refs/remotes/origin/*
```

```bash
git config --get-all remote.origin.fetch
```

`+` povoľuje non-fast-forward aktualizáciu remote-tracking refu, pretože ten má zrkadliť stav remote branch po fetchi.

## 5. Prune

Remote branch môže byť zmazaná, ale lokálny remote-tracking ref môže zostať, kým sa neprune-ne.

```bash
git fetch --prune
git remote prune origin
```

Prune nemaže automaticky lokálnu branch s rovnakým názvom.

## 6. Pull

`git pull` je zložená operácia:

```text
git fetch
+
merge alebo rebase podľa konfigurácie
```

Možnosti:

```bash
git pull --ff-only
git pull --rebase
git pull --no-rebase
```

Pre predvídateľnosť je vhodné explicitne zvoliť policy:

```bash
git config pull.ff only
# alebo
git config pull.rebase true
```

`pull` môže meniť working history a vytvoriť konflikty. Nie je ekvivalent čistého downloadu.

## 7. Fast-forward pull

Ak lokálny tip je ancestor remote tip-u:

```text
A---B  local
     \
      C---D  remote
```

lokálna branch sa môže iba posunúť na `D` bez merge commitu.

```bash
git pull --ff-only
```

`--ff-only` zlyhá pri divergence namiesto automatického rozhodnutia.

## 8. Divergence

```text
      C---D  local
     /
A---B
     \
      E---F  remote
```

Možnosti:

- merge zachová oba ancestry smery,
- rebase vytvorí nové lokálne commits nad remote tipom,
- manuálna integrácia podľa tímovej policy.

Najprv analyzuj:

```bash
git fetch origin
git log --graph --oneline --left-right HEAD...@{upstream}
```

## 9. Push

`git push` prenesie objects a požiada remote o aktualizáciu refs.

```bash
git push origin main
git push -u origin feature/api-timeout
```

Remote server vykoná authorization, hooks a branch policy. Push môže byť odmietnutý aj keď je lokálny repository validný.

## 10. Upstream a push defaults

```bash
git branch -vv
git config push.default
git config remote.pushDefault
```

`git push -u` nastaví upstream tracking. Potom `git status` vie zobrazovať ahead/behind a príkazy môžu použiť default remote/branch.

Nejasná upstream konfigurácia je častá príčina pushu na nesprávnu branch.

## 11. Non-fast-forward rejection

Remote odmietne push, keď by update odstránil z branch ancestry commits, ktoré server už obsahuje.

```text
remote: A---B---C
local:  A---B---D
```

Bezpečný postup:

```bash
git fetch origin
git log --graph --oneline --left-right main...origin/main
```

Potom merge alebo rebase podľa policy.

## 12. Force push

```bash
git push --force-with-lease
```

Lease overuje, že remote ref má očakávanú hodnotu. Chráni pred prepísaním neznámej cudzej zmeny, ale stále zámerne mení publikovanú históriu.

Nepoužívaj slepý `--force` na zdieľané protected branches.

## 13. Tags

Tags sa nemusia pushnúť automaticky s branchou.

```bash
git push origin v1.2.0
git push origin --tags
git fetch --tags
```

`--tags` môže publikovať všetky lokálne tags, čo nemusí byť zámer. Release pipeline má pushovať explicitný release tag.

## 14. Delete remote refs

```bash
git push origin --delete feature/old
git push origin :refs/heads/feature/old
```

Zmazanie remote branch nemaže lokálne clones ani commits reachable cez iné refs.

## 15. Authentication vs. authorization

Transport môže používať:

- SSH keys/certificates,
- HTTPS token alebo credential helper,
- workload identity v CI.

Authentication dokazuje identitu. Authorization rozhoduje, či identita môže čítať alebo meniť konkrétny ref.

Secrets neukladaj do remote URL ani repository config v plaintext forme.

## 16. Shallow clone

```bash
git clone --depth 1 <url>
git fetch --deepen 50
git fetch --unshallow
```

Shallow clone má obmedzenú ancestry históriu. Môže ovplyvniť:

- merge-base,
- version calculation,
- changelog generation,
- blame,
- tools očakávajúce plný graph.

Je vhodný len pri vedomom trade-offe medzi prenosom a funkčnosťou.

## 17. Partial clone a filter

```bash
git clone --filter=blob:none <url>
```

Partial clone môže odložiť prenos niektorých objects a načítať ich na požiadanie. Vyžaduje server support a mení performance/failure model buildov bez network accessu.

## 18. Mirror a bare repository

Bare repository nemá working tree:

```bash
git clone --bare <url>
```

Mirror prenáša širší set refs a config:

```bash
git clone --mirror <url>
git push --mirror <new-url>
```

`--mirror` je silná operácia: môže na cieli zmazať refs, ktoré v source neexistujú.

## 19. Praktický bezpečný sync workflow

```bash
git status
git fetch --prune origin
git log --graph --oneline --left-right HEAD...origin/main
git rebase origin/main   # alebo merge podľa policy
git push --force-with-lease  # iba ak rebase publikovanej feature branch je povolený
```

Pred sync operáciou musí byť jasné:

- ktorá lokálna branch je aktuálna,
- ktorý upstream sleduje,
- či je working tree čistý,
- či história už bola zdieľaná.

## 20. Troubleshooting

### Push rejected

```bash
git status
git branch -vv
git remote -v
git fetch origin
git log --graph --oneline --left-right HEAD...@{upstream}
```

Rozlíš:

- non-fast-forward,
- authentication failure,
- authorization/branch protection,
- server hook alebo policy,
- príliš veľký object,
- secret scanning rejection.

### Fetch nevidí očakávanú branch

```bash
git ls-remote --heads origin
git config --get-all remote.origin.fetch
git fetch origin refs/heads/name:refs/remotes/origin/name
```

Môže ísť o obmedzený refspec alebo single-branch clone.

## 21. Časté omyly

### „Pull je fetch“

Pull vykoná fetch a následnú integráciu.

### „`origin/main` je vždy aktuálny remote“

Iba po fetchi.

### „Force-with-lease je úplne bezpečný“

Je bezpečnejší, ale stále prepisuje históriu.

### „Shallow clone je plnohodnotný clone s menším diskom“

Má obmedzený graph a odlišné správanie niektorých operácií.

## 22. Kontrolné otázky

1. Čo presne vykoná clone?
2. Aký je rozdiel medzi fetch a pull?
3. Čo je refspec?
4. Prečo remote-tracking ref nie je live serverový stav?
5. Kedy je pull fast-forward?
6. Prečo remote odmietne non-fast-forward push?
7. Čo kontroluje `--force-with-lease`?
8. Aké trade-offy prináša shallow a partial clone?

## Glossary impact

Relevantné pojmy: remote, origin, fetch, pull, push, refspec, upstream branch, remote-tracking ref, shallow clone, partial clone, bare repository, mirror.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Commit, branch, tag a HEAD](commit-branch-tag-head.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Merge a rebase →](merge-and-rebase.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
