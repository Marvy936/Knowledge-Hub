# Branching strategies

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Git and Automation Basics
- Predpoklady: [Merge a rebase](merge-and-rebase.md), [Konflikty](merge-conflicts.md)
- Súvisiace témy: trunk-based development, Git Flow, release branches, feature flags, CI/CD

## 1. Definícia

Branching strategy je súbor pravidiel určujúcich:

- kde vznikajú zmeny,
- ako dlho branches žijú,
- ako sa integrujú,
- ktoré branches sú releasable,
- ako sa opravujú produkčné chyby,
- aké quality gates chránia zdieľanú históriu.

Nie je to iba naming convention. Je to súčasť delivery architecture.

## 2. Cieľ stratégie

Dobrá stratégia má minimalizovať:

- integračný delay,
- veľkosť merge konfliktov,
- počet paralelných verzií,
- nejasnosť release source,
- manuálne backporty,
- rozdiel medzi testovaným a nasadeným commitom.

Zároveň musí podporovať audit, recovery a požadovaný release cadence.

## 3. Trunk-based development

Vývojári integrujú často do jednej hlavnej branch (`main`, `trunk`). Feature branches sú krátke alebo sa zmeny commitujú priamo cez silné CI gates.

Typické mechanizmy:

- malé batches,
- branch lifetime hodiny až málo dní,
- feature flags,
- backward-compatible migrations,
- pre-merge CI,
- branch protection,
- automatizované deploymenty.

Výhoda: krátky feedback a nízka divergence. Riziko: bez kvalitného CI a modularity môže trunk často zlyhávať.

## 4. Feature branch workflow

Každá zmena vzniká na samostatnej branch a integruje sa cez pull/merge request.

```text
main ────────────────M
       \ feature ───/
```

Výhody:

- izolovaný review context,
- CI pre konkrétnu zmenu,
- jednoduché approvals,
- ochrana main.

Riziká:

- dlhé branches,
- veľké batches,
- late integration,
- „green branch, broken combination“.

Feature branch workflow je kompatibilný s trunk-based modelom iba vtedy, keď branches žijú krátko.

## 5. Git Flow

Git Flow používa dlhodobé branches ako:

```text
main/master
 develop
 release/*
 hotfix/*
 feature/*
```

Bol navrhnutý pre release model s oddelenými stabilizačnými fázami a verziami.

Výhody:

- explicitné release a hotfix línie,
- podpora viacerých vydaní,
- jasné stabilizačné branches.

Nevýhody:

- zložité merges a backports,
- dlhá integračná spätná väzba,
- viac places of truth,
- nevhodnosť pre vysokofrekvenčný continuous delivery bez úprav.

Git Flow nie je univerzálny default.

## 6. GitHub/GitLab Flow

Zjednodušený model:

```text
short-lived branch
→ pull/merge request
→ CI/review
→ main
→ deployment
```

Environment promotion sa často riadi artifactom alebo deployment metadata, nie dlhodobou environment branch.

## 7. Release branches

Release branch môže byť vhodná, keď treba:

- podporovať viac produkčných verzií,
- vykonávať stabilizáciu bez zastavenia main,
- backportovať security fixes,
- udržiavať enterprise/LTS líniu.

Pravidlá musia definovať:

- source release branch,
- smer merge/backportu,
- versioning,
- ownership,
- dobu podpory,
- test matrix.

Bez týchto pravidiel vzniká patch drift.

## 8. Environment branches

Branches `dev`, `test`, `stage`, `prod` často vedú k tomu, že každé prostredie obsahuje odlišnú históriu a merges reprezentujú promotion.

Riziká:

- nejasné, ktorý artifact je rovnaký,
- merge conflicts počas promotion,
- environment-specific code drift,
- zmena binárneho obsahu medzi stages.

Preferovaný model v CI/CD:

```text
jeden immutable artifact
→ promotion cez environment configuration a deployment record
```

Environment branches môžu mať zmysel pre deklaratívny GitOps config, ale nie automaticky pre source-code promotion.

## 9. Feature flags

Feature flag oddeľuje deployment od release.

Umožňuje:

- integrovať incomplete code bezpečne,
- postupný rollout,
- experiment,
- rýchle vypnutie behavioru.

Riziká:

- kombinatorická zložitosť,
- stale flags,
- security exposure,
- rozdielne testované stavy.

Flag potrebuje ownera, expiry/removal plán a observability.

## 10. Branch protection

Typické controls:

- required review,
- required CI checks,
- signed commits alebo verified identity,
- zákaz direct push,
- zákaz force push,
- linear history policy,
- merge queue,
- CODEOWNERS.

Protection má vynucovať delivery policy, nie iba administratívnu formalitu.

## 11. Merge methods

### Merge commit

Zachová branch topology a jednotlivé commits.

### Squash merge

Vytvorí jeden commit na main. Zjednoduší históriu, ale stráca ancestry detail.

### Rebase merge

Replayuje jednotlivé commits lineárne na main. Mení IDs a vyžaduje čistú commit sériu.

Tím má zvoliť metódu konzistentne podľa audit, revert a release potrieb.

## 12. Merge queue

Pri viacerých paralelných pull requests môže každý CI run testovať branch proti starému main. Merge queue testuje kandidátov v plánovanom integračnom poradí.

Pomáha zabrániť:

```text
PR A green
PR B green
A + B spolu broken
```

Queue zvyšuje confidence, ale potrebuje rozumnú CI duration a flaky-test control.

## 13. Hotfix workflow

Produkčná oprava musí mať definovaný tok:

```text
incident branch z produkčného commitu
→ fix + tests
→ deployment
→ merge/cherry-pick späť do main a podporovaných release branches
```

Častá chyba: hotfix sa nasadí, ale nevráti do main, takže ďalší release ho odstráni.

## 14. Výber stratégie podľa kontextu

Zohľadni:

- release frequency,
- počet podporovaných verzií,
- veľkosť tímu,
- CI duration a spoľahlivosť,
- reguláciu a approvals,
- architektúru produktu,
- schopnosť používať feature flags,
- potrebu emergency patches,
- dependency medzi tímami.

## 15. Anti-patterny

### Dlhodobé feature branches

Zvyšujú divergence, konflikt a integračné riziko.

### Branch per environment pre application source

Mieša promotion a code integration.

### Nejasný hotfix smer

Vedie k strate opravy v ďalšej verzii.

### Manual bypass main protection

Rozbíja audit a vytvára netestovaný stav.

### Stratégia bez merania

Sleduj lead time, branch age, conflict rate, failed merges, revert rate a CI queue time.

## 16. Praktická odporúčaná baseline

Pre väčšinu moderných služieb:

```text
main je vždy potenciálne releasable
short-lived feature branches
pull request + automated checks
merge queue podľa potreby
squash alebo rebase/merge policy konzistentne
immutable artifact promotion
feature flags pre incomplete alebo staged behavior
release branches iba pri reálnej podpore viacerých verzií
```

## 17. Kontrolné otázky

1. Aký je rozdiel medzi trunk-based development a dlhodobými feature branches?
2. Kedy má Git Flow opodstatnenie?
3. Prečo environment branches často komplikujú promotion?
4. Ako feature flags oddeľujú deployment od release?
5. Čo rieši merge queue?
6. Aké riziko má squash merge?
7. Ako má vyzerať hotfix spätná integrácia?
8. Ktoré metriky odhalia nefunkčnú branching strategy?

## Glossary impact

Relevantné pojmy: trunk-based development, feature branch, Git Flow, release branch, hotfix branch, feature flag, branch protection, merge queue, squash merge.
