# Git and Automation Basics

Táto sekcia vysvetľuje Git od content-addressable object database cez working tree, refs a distribuovanú synchronizáciu až po integráciu histórie, konflikty a repository stratégie. Cieľom nie je memorovať príkazy, ale vedieť predvídať, ktorý ref, object graph, index alebo working-tree stav konkrétna operácia zmení.

## Predpoklady

Odporúča sa najprv dokončiť [DevOps Foundations](../00-foundations/README.md), [Linux and Systems](../01-linux-and-systems/README.md) a [Networking and Web Fundamentals](../02-networking-and-web/README.md). Pre remote operácie sú dôležité najmä SSH, HTTPS/TLS, authentication a troubleshooting princípy.

## Odporúčané poradie

1. [Git object model](git-object-model.md)
2. [Working tree, staging area a repository](working-tree-staging-repository.md)
3. [Commit, branch, tag a HEAD](commit-branch-tag-head.md)
4. [Clone, fetch, pull a push](clone-fetch-pull-push.md)
5. [Merge a rebase](merge-and-rebase.md)
6. [Reset, revert a restore](reset-revert-restore.md)
7. [Cherry-pick a stash](cherry-pick-and-stash.md)
8. [Konflikty](merge-conflicts.md)
9. [Branching strategies](branching-strategies.md)
10. [Monorepo vs. multirepo](monorepo-vs-multirepo.md)

Ďalší blok tejto sekcie rozšíri Git o praktickú automatizáciu: Bash, PowerShell, Python, YAML, JSON a regular expressions.

## Cieľ zvládnutia

Po dokončení Git bloku má byť možné:

- vysvetliť blob, tree, commit a tag objects a cestu ref → commit → tree → blob,
- rozlíšiť working tree, index a repository a vedome pripravovať commit cez partial staging,
- interpretovať branch, tag, HEAD, detached HEAD, remote-tracking ref a reflog,
- vysvetliť clone, fetch, pull, push, refspec, upstream a non-fast-forward update,
- porovnať merge, rebase, squash merge a history rewrite vrátane ich auditných dôsledkov,
- bezpečne zvoliť medzi restore, reset a revert,
- používať cherry-pick a stash bez zamieňania patch replayu za ancestry integráciu,
- riešiť textové, rename, binary aj semantic conflicts a overiť výsledok tests a diffom,
- navrhnúť branching strategy podľa release cadence, CI capability, compliance a počtu podporovaných verzií,
- technicky obhájiť monorepo, multirepo alebo hybridný model podľa change coupling, ownership a build topology.

## Stav

| Téma | Status | Úroveň |
|---|---|---|
| Git object model | Learning | L2 |
| Working tree, staging area a repository | Learning | L2 |
| Commit, branch, tag a HEAD | Learning | L2 |
| Clone, fetch, pull a push | Learning | L2 |
| Merge a rebase | Learning | L2 |
| Reset, revert a restore | Learning | L2 |
| Cherry-pick a stash | Learning | L2 |
| Konflikty | Learning | L2 |
| Branching strategies | Learning | L2 |
| Monorepo vs. multirepo | Learning | L2 |
