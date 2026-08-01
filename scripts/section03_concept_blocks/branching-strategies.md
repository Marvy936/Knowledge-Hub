## Čo je branching strategy

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