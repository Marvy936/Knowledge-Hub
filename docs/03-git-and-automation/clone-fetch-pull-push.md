# Clone, fetch, pull a push

Alice a Bob pracujú s rovnakým serverovým repository, ale každý má vlastnú object database, branches, index a working tree. Git nie je klient s permanentne živou serverovou branch. Distribuovaná synchronizácia explicitne prenáša objekty a aktualizuje refs.

## Clone vytvorí lokálne repository

```bash
git clone ssh://git@code.atlas.example/platform/atlas-orders-delivery.git
```

Clone prenesie dostupné objects a refs, vytvorí remote `origin`, remote-tracking refs a checkoutne default branch. `origin` je iba konfiguračné meno. Nemá špeciálnu protocol semantics.

```bash
git remote -v
git branch -vv
git show-ref --heads --remotes
```

Local `main` a `origin/main` sú odlišné refs. `origin/main` je posledný stav remote branch známy po fetchi, nie real-time server view.

## Fetch prenáša objekty a aktualizuje remote-tracking refs

```bash
git fetch origin --prune
```

Fetch vyjedná chýbajúce objects a podľa refspecu aktualizuje napríklad `refs/remotes/origin/main`. Neintegruje automaticky zmenu do local `main` a nemení working tree.

```bash
git log --oneline --left-right --graph main...origin/main
```

Po fetchi môže local branch byť ahead, behind alebo diverged. Toto je bezpečný observation krok pred integráciou.

## Pull je fetch plus integration

`git pull` najprv fetchne a potom merge-ne alebo rebase-ne podľa configuration a flags. Preto je presnejšie hovoriť, akú integráciu používame:

```bash
git pull --ff-only
```

`--ff-only` posunie branch iba vtedy, keď local nemá vlastnú divergence. Nevytvorí implicitný merge commit. Pre feature branch môže tím používať:

```bash
git fetch origin
git rebase origin/main
```

Oddelenie fetch a integration poskytuje čas na inspection.

## Push navrhuje update remote refu

```bash
git push -u origin feature/ord-8421
```

Client odošle chýbajúce objects a požiada server, aby aktualizoval remote ref. Server môže odmietnuť update kvôli non-fast-forwardu, protection rule, permission, hooku alebo policy.

Push success znamená prijatý ref update. Neznamená merge do main, úspešné CI ani deployment.

## Fast-forward a non-fast-forward

Fast-forward nastane, keď starý remote tip je ancestor nového tipu:

```text
remote main: C3
new tip:     C5 → C4 → C3
```

Remote ref sa môže bezpečne posunúť na C5 bez straty reachable history. Ak Bob už pushol D4 a Alice má C4 nad starým C3, update by jednu vetvu odpojil:

```text
      C4  Alice
     /
C3
     \
      D4  remote
```

Server správne odmietne bežný push. Alice musí fetch-nuť a integrovať D4.

## Force-with-lease

Po koordinovanom rebase feature branch sa remote history musí prepísať. `--force-with-lease` overí, že remote ref stále ukazuje na commit, ktorý klient očakáva:

```bash
git push --force-with-lease origin feature/ord-8421
```

Je bezpečnejší než `--force`, ale nie absolútne bezpečný. Ak background fetch aktualizoval local remote-tracking ref, lease expectation sa môže zmeniť. Pri citlivej operácii možno uviesť explicitný expected old SHA.

Protected shared branches sa typicky nerewrite-ujú vôbec.

## Refspec a explicitnosť

Syntax:

```text
<src>:<dst>
```

```bash
git push origin HEAD:refs/heads/feature/ord-8421
```

Explicitný refspec je užitočný v automation, pretože nespolieha na current branch magic. Delete remote branch možno vyjadriť:

```bash
git push origin --delete feature/ord-8421
```

Delete je remote ref mutation; commits môžu zostať reachable cez merge commit, tag alebo iný ref.

## Authentication a transport

Git môže používať SSH alebo HTTPS. Network, DNS, TLS a credential boundaries z predchádzajúcej sekcie platia aj tu. Authentication success nepreukazuje authorization na konkrétny ref. Credential helper, SSH agent a CI token majú odlišný lifecycle a scope.

Secrets sa nemajú vkladať do remote URL alebo logs. Automation používa short-lived credentials a server-side branch policy.

## Incident: `git pull` vytvorí neočakávaný merge

Bob má lokálny commit a spustí default `git pull`. Konfigurácia použije merge a vytvorí merge commit, hoci tím vyžaduje lineárnu feature history. Technicky nič nie je poškodené, ale review diff a policy sa zmenia.

Prevencia nastaví explicitný mode:

```bash
git config pull.ff only
```

alebo tímový rebase contract. Dôležité je, aby pull nebol neurčitá skratka, ale vedomý fetch plus konkrétna integration strategy.

## Zhrnutie

Clone vytvorí samostatné lokálne repository. Fetch aktualizuje lokálny pohľad na remote refs, pull pridáva integration a push navrhuje serverový ref update. `origin/main` nie je server branch a push success nie je release success. Non-fast-forward je ochrana graphu, nie náhodná prekážka.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Commit, branch, tag a HEAD](commit-branch-tag-head.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Merge a rebase →](merge-and-rebase.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
