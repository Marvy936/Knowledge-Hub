# Branching strategies

Branching strategy nie je diagram názvov branches. Je to dohoda o tom, kde vzniká zmena, ako rýchlo dostane integration evidence, ktoré refs sú stabilné, ako sa podporujú staršie releases a ako sa hotfix propaguje. Nesprávna stratégia zväčšuje divergence debt: čím dlhšie branches žijú oddelene, tým viac assumptions a conflicts sa nahromadí.

## Trunk-based development

Trunk-based model drží `main` releasable a používa malé krátko žijúce branches alebo priamu integráciu za silnými gates. Nehotová funkcionalita sa skrýva za feature flagom, nie dlhodobou source branch.

```text
small change
→ fast review
→ complete CI
→ merge queue
→ main
→ immutable artifact
→ controlled release
```

Model vyžaduje rýchle tests, backward-compatible changes a schopnosť oddeliť deployment od exposure. Bez týchto capabilities sa „trunk-based“ môže zmeniť na nestabilný main.

## GitHub/GitLab flow

Feature branch vznikne z main, prejde review a CI a merge-ne späť. Deployment môže nasledovať main alebo release tag. Je to praktický variant pre web/cloud produkty s jednou hlavnou podporovanou líniou.

Dôležitá je branch freshness a merge queue. Zelený pipeline výsledok na starom base nepreukazuje, že change prejde po integrácii s novším main. Merge queue vytvorí candidate v poradí a testuje skutočný budúci tip.

## Release branches

Ak Atlas podporuje 4.1 a 4.2 súčasne, môže mať `release/4.1` a main pre budúcu verziu. Release branch prijíma iba schválené fixes. Každý hotfix má propagation matrix:

```text
security fix
→ main
→ release/4.2
→ release/4.1, ak applicable
→ artifacts a verification pre každú líniu
```

Cherry-pick IDs sa líšia a tests musia bežať pre každú codebase. Release branch nemá byť skládka features, ktoré sa nestihli integrovať inde.

## Git Flow

Klasický Git Flow používa `develop`, release, feature a hotfix branches. Môže podporiť periodické packaged releases, ale vytvára viac integration boundaries a back-merge povinností. V prostredí continuous delivery býva často zbytočne ťažký.

Problém nie je počet branches sám o sebe, ale dlhodobá divergence a nejasný source of truth. Každý permanentný ref potrebuje ownera, vstupné pravidlá, exit criteria a retirement lifecycle.

## Environment branches ako anti-pattern

Branches `dev`, `staging` a `prod` často miešajú source promotion s environment configuration. Merge medzi nimi vytvára environment drift, history conflicts a nejasný artifact identity.

Bezpečnejší model buildne immutable artifact raz a promotuje rovnaký digest cez environment-specific desired state. Git branch môže držať deklaráciu prostredia, ale nemá predstierať, že recompilovaný source je ten istý release.

## Branch protection

Shared branches potrebujú server-side controls:

```text
no direct push
required reviews
required status checks
merge queue alebo up-to-date requirement
signed commits/tags podľa threat modelu
no force push
delete restrictions
code-owner review pre citlivé paths
```

Protection config je runtime policy. README opis nestačí. Controls treba read-backnúť cez hosting API a testovať forbidden operation vhodným test accountom.

## Commit granularity

Branching strategy funguje lepšie, keď commits majú coherent intent a sú buildable alebo aspoň reviewable. Obrovská branch s refactorom, schema migration a behavior changeom vytvára vysokú integration risk.

Stacked changes môžu rozdeliť veľkú zmenu do závislých reviews, ale potrebujú tooling na base updates a merge order. Každý stack node má vlastný evidence subject.

## Incident: hotfix sa stratí medzi branches

Production 4.1 dostane urgentný fix priamo na release branch. Main ho neobsahuje a o mesiac release 4.2 regresiu znovu zavedie. Tím síce mal branch diagram, ale nemal propagation state machine.

Oprava zavádza hotfix record s applicability, source commit, backport commits, release artifacts a closure gate pre každú podporovanú líniu. Automation upozorní na chýbajúci propagation, no domain owner rozhoduje, či je patch relevantný.

## Zhrnutie

Branching strategy má minimalizovať feedback latency a divergence pri zachovaní release a support potrieb. Trunk-based, feature branches a release branches sú nástroje, nie identity tímu. Dôležité sú freshness gates, merge queue, immutable artifact promotion, hotfix propagation a server-side protection.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Konflikty](merge-conflicts.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Monorepo vs. multirepo →](monorepo-vs-multirepo.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
