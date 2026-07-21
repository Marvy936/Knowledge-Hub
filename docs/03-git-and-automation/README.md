# Git and Automation Basics

Táto sekcia vysvetľuje Git od content-addressable object database cez working tree, refs a distribuovanú synchronizáciu až po integráciu histórie, konflikty a repository stratégie. Následne rozširuje základ o praktickú automatizáciu v Bash, PowerShelli a Pythone a o bezpečnú prácu s YAML, JSON a regular expressions. Cieľom nie je memorovať príkazy, ale vedieť predvídať zmenu stavu, definovať stabilný kontrakt automatizácie a diagnostikovať zlyhanie na správnej vrstve.

## Predpoklady

Odporúča sa najprv dokončiť [DevOps Foundations](../00-foundations/README.md), [Linux and Systems](../01-linux-and-systems/README.md) a [Networking and Web Fundamentals](../02-networking-and-web/README.md). Pre remote operácie sú dôležité najmä SSH, HTTPS/TLS, authentication a troubleshooting princípy. Pre automation blok sú potrebné process, filesystem, environment, exit-status a structured-data fundamenty.

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
11. [Bash automation](bash-automation.md)
12. [PowerShell fundamentals](powershell-fundamentals.md)
13. [Python for automation](python-for-automation.md)
14. [YAML, JSON a regular expressions](yaml-json-regular-expressions.md)

Po tejto sekcii nasleduje Testing and Software Quality. Git a automation mechanizmy sa tam použijú pri test execution, quality gates, fixtures, test data a CI integrácii.

## Cieľ zvládnutia

Po dokončení sekcie má byť možné:

- vysvetliť blob, tree, commit a tag objects a cestu ref → commit → tree → blob,
- rozlíšiť working tree, index a repository a vedome pripravovať commit cez partial staging,
- interpretovať branch, tag, HEAD, detached HEAD, remote-tracking ref a reflog,
- vysvetliť clone, fetch, pull, push, refspec, upstream a non-fast-forward update,
- porovnať merge, rebase, squash merge a history rewrite vrátane ich auditných dôsledkov,
- bezpečne zvoliť medzi restore, reset a revert,
- používať cherry-pick a stash bez zamieňania patch replayu za ancestry integráciu,
- riešiť textové, rename, binary aj semantic conflicts a overiť výsledok tests a diffom,
- navrhnúť branching strategy podľa release cadence, CI capability, compliance a počtu podporovaných verzií,
- technicky obhájiť monorepo, multirepo alebo hybridný model podľa change coupling, ownership a build topology,
- navrhnúť Bash skript s bezpečným quotingom, arrays, error handlingom, cleanupom, lockingom a idempotentnými mutations,
- rozlíšiť PowerShell object pipeline, success/error streams, terminating a non-terminating errors a native process exit codes,
- vytvoriť testovateľný Python CLI nástroj s explicitnými dependencies, timeouts, retries, loggingom a graceful shutdown,
- zvoliť medzi Bash, PowerShellom a Pythonom podľa complexity, platformy a požadovaného dátového modelu,
- bezpečne parsovať, validovať a serializovať YAML a JSON s explicitným encodingom a schema kontraktom,
- navrhovať regexy s vedomím dialectu, anchors, escaping vrstiev, Unicode semantics a ReDoS rizika,
- oddeľovať plan, apply, verify a recovery fázu automatizácie,
- definovať stabilné vstupy, výstupy, exit codes, dry-run, observability a security boundaries automatizačného nástroja.

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
| Bash automation | Learning | L2 |
| PowerShell fundamentals | Learning | L2 |
| Python for automation | Learning | L2 |
| YAML, JSON a regular expressions | Learning | L2 |
