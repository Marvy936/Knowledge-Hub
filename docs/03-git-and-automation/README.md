# Git and Automation Basics

Táto sekcia sleduje jednu zmenu od prvého upraveného riadku až po bezpečne vykonanú automatizáciu. Atlas tím pripravuje change `ORD-8421`, ktorý do služby `orders-api` pridáva konfiguračný limit `maxOrderAmount`. Zmena sa najprv objaví vo working tree, potom sa vyberie do indexu, uloží do content-addressed Git objektov, spojí s históriou cez commit a branch a nakoniec sa synchronizuje s remote repository. Druhá polovica sekcie ten istý change premení na automatizačný kontrakt `observe → plan → apply → verify`, ktorý pracuje so structured data, stabilnými exit codes, lockom, dry-runom a recovery hranicou.

Cieľom nie je memorovať názvy Git príkazov ani syntaktické triky troch jazykov. Čitateľ má vedieť určiť, ktorý stav práve mení: working tree, index, local object database, ref, remote-tracking ref, remote branch, runtime state alebo automatizačný plan. Každý príkaz je vysvetlený spolu s tým, čo mení, čo nemení a aký read-back dokáže jeho výsledok.

## Spoločný scenár

Sekcia používa repository `atlas-orders-delivery`:

```text
atlas-orders-delivery/
├── config/
│   └── orders.yaml
├── schemas/
│   └── orders.schema.json
├── scripts/
│   ├── release.sh
│   └── Release-Orders.ps1
├── tools/
│   └── atlasctl.py
├── state/
│   └── dev.json
└── tests/
    └── test_atlasctl.py
```

Konfiguračný change prechádza týmto reťazcom:

```text
editor buffer
→ working tree
→ index
→ blob a tree objects
→ commit
→ feature branch
→ remote-tracking a remote branch
→ review a integration
→ release tag
→ automation plan
→ locked apply
→ runtime state
→ verification a second no-op run
```

Sekcia dôsledne rozlišuje tieto identity:

```text
file content
≠ blob object
≠ pathname v tree objekte
≠ commit snapshot
≠ branch ref
≠ remote-tracking ref
≠ remote branch
≠ release tag
≠ automation plan
≠ applied runtime state
```

Dva commits môžu obsahovať rovnaký file content, ale mať odlišných parents alebo metadata. Dve branches môžu ukazovať na rovnaký commit. `origin/main` nie je živý pohľad na server; je to lokálny remote-tracking ref aktualizovaný fetchom. Zelený skript exit code nepreukazuje správny runtime outcome, ak nástroj neoveril stav, ktorý mal zmeniť.

## Authoritative poradie kapitol

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
15. [Praktický Git a automation projekt od prázdneho adresára po overený apply](git-automation-practical-walkthrough.md)

Prvých desať kapitol vysvetľuje Git ako databázu immutable objektov a systém pohyblivých refs. Ďalšie štyri kapitoly zostavia rovnaký automatizačný contract v Bash, PowerShelli a Pythone a vysvetlia hranice structured data a regexov. Záverečný walkthrough vytvorí bare remote, dve clones, divergence, konflikt, recovery, annotated release tag a executable plan/apply/verify nástroj.

## Výkladový štandard

Každá koncepčná kapitola najprv samostatne vysvetlí, čo daný pojem znamená, aký problém rieši, ktoré objekty alebo vrstvy stavu zahŕňa a aký mechanizmus vykonáva. Nasleduje jednoduchý neutrálny príklad, ktorý nepredpokladá znalosť Atlas projektu. Až potom kapitola prejde k sekcii `Atlas scenár a praktické použitie`, kde sa pojem aplikuje na change `ORD-8421`, doplnia sa CLI príkazy, read-back, failure path a recovery. Scenár teda upevňuje už vysvetlený model; nenahrádza definíciu ani všeobecný výklad.

Odrážky zostávajú iba pri krátkom inventári states, acceptance podmienok alebo porovnaní. Hlavný výklad nesú súvislé odseky. Pri history rewrite sa vždy pomenúva collaboration boundary. Pri automatizácii sa oddelí source configuration, observed state, plan subject, mutation outcome a verified state.

## Praktický walkthrough

Praktická kapitola používa iba lokálny filesystem a Git; nepotrebuje externý hosting. Vytvorí:

```text
bare origin repository
→ seed repository
→ clone alice
→ clone bob
→ dve paralelné changes
→ rejected non-fast-forward push
→ fetch a rebase conflict
→ semantic resolution a test
→ annotated release tag
→ accidental reset a reflog recovery
→ Python plan/apply/verify tool
→ Bash wrapper
→ PowerShell wrapper
→ stale-plan failure
→ second no-op apply
```

Python a Bash ukážky sú executable na Linuxe. PowerShell ukážka je syntakticky a mechanisticky auditovaná, ale repository workflow ju nevykonáva, pokiaľ runner nemá `pwsh`. Praktický nástroj používa JSON-compatible YAML subset, takže ho dokáže bezpečne načítať štandardná Python `json` knižnica bez externých dependencies; kapitola zároveň vysvetlí, že všeobecné YAML vyžaduje skutočný YAML parser.

## Stav

Všetkých pätnásť kapitol je po full prose rewritingu pripravených na používateľskú kontrolu. `Ready for user review` neznamená automatické používateľské schválenie ani overenie každého príkazu na každej platforme. Git/Python/Bash practical flow má samostatnú executable validation hranicu; PowerShell a hosting-specific protection rules zostávajú platformovou hranicou.
