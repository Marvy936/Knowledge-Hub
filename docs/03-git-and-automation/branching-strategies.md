# Branching strategies

Branching strategy je tímový contract určujúci, kde vzniká zmena, ako dlho sa branch diverguje, akými gates prejde, ako sa integruje a ako sa udržiavajú podporované release lines. Nie je to iba diagram názvov branchí.

Každá dlhšie žijúca branch vytvára divergence debt. Počas divergenčného času sa mení base, dependencies, schemas aj assumptions. Čím neskôr sa zmeny integrujú, tým väčší je priestor pre konflikty a neplatné dôkazy.

**Trunk-based development** používa jednu hlavnú integračnú line a krátko žijúce branches alebo priamu integráciu s veľmi silným CI. Neúplná funkcia sa často oddeľuje feature flagom, nie dlhodobou source branchou.

**GitHub/GitLab flow** typicky používa feature branch, pull/merge request, review, CI a integráciu do hlavnej branch. Deployment model môže byť continuous alebo environment-based; názov flow sám neurčuje release policy.

**GitFlow-like model** používa dlhšie žijúce develop a release branches. Môže byť užitočný pri viacerých podporovaných verziách a formálnych release windows, ale zvyšuje merge a hotfix propagation complexity.

Neutrálny lifecycle:

```text
change intent
→ branch alebo trunk slot
→ pravidelná synchronizácia s base
→ automated evidence
→ review
→ integration
→ immutable artifact
→ release/promotion
→ prípadný hotfix backport
```

Strategy musí definovať aj to, čo sa deje po hotfixe. Oprava aplikovaná iba na production release branch sa môže stratiť z budúcej verzie. Backport a forward-port ownership je súčasťou modelu.

Branch protection, required checks a merge queue chránia ref transition. Nezaručujú, že výsledný commit bol testovaný proti presne rovnakému base, ak queue nevytvorí alebo neoverí aktuálny merge candidate. Correctness teda závisí od vzťahu medzi review subjectom, tested subjectom a integrated subjectom.

Dobrá strategy minimalizuje batch size a divergence pri zachovaní požadovaného release a compliance modelu. Nemá sa kopírovať podľa popularity bez analýzy cadence, CI času, coupling, rollbacku a počtu podporovaných línií.

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

## Praktický branch lifecycle a dôkazné body

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

Server-side controls treba read-backnúť cez hosting API a overiť negatívnym testom. Dokument „force push je zakázaný“ nemá enforcement hodnotu, ak branch setting povoľuje Maintainer bypass.

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
