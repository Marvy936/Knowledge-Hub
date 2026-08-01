# DevOps Foundations

Táto sekcia vytvára procesný a mentálny základ pre všetky ďalšie technické oblasti. Cieľom je pochopiť, prečo vznikli DevOps praktiky a nástroje, nie iba ako ich používať.

## Predpoklady

Táto sekcia nemá technické predpoklady. Je východiskovým bodom Knowledge Hubu.

## Authoritative poradie

1. [Software Development Life Cycle](sdlc.md)
2. [DevOps](devops.md)
3. [DevOps lifecycle](devops-lifecycle.md)
4. [CALMS framework](calms.md)
5. [Three Ways of DevOps](three-ways.md)
6. [Systems thinking](systems-thinking.md)
7. [Feedback loops](feedback-loops.md)
8. [Continuous improvement](continuous-improvement.md)
9. [T-shaped, I-shaped a π-shaped engineer](t-shaped-engineer.md)
10. [Ownership mindset](ownership-mindset.md)
11. [You build it, you run it](you-build-it-you-run-it.md)
12. [Automation mindset](automation-mindset.md)
13. [Declarative vs. imperative prístup](declarative-vs-imperative.md)
14. [Idempotencia](idempotency.md)
15. [Desired state a reconciliation](desired-state-and-reconciliation.md)
16. [Immutable vs. mutable infrastructure](immutable-vs-mutable-infrastructure.md)
17. [Toil a technical debt](toil-and-technical-debt.md)
18. [Value stream mapping](value-stream-mapping.md)
19. [DORA metrics](dora-metrics.md)
20. [DevOps anti-patterns](devops-anti-patterns.md)

Nadväzujúce témy `shift-left`, `shift-right`, CI/CD a deployment stratégie budú rozpracované v sekciách Testing and Software Quality a CI/CD and Release Engineering, pretože tam majú presnejší technický kontext.

Nasledujúca hlavná sekcia: [Linux and Systems](../01-linux-and-systems/README.md).

## Spôsob spracovania sekcie

Sekcia používa jeden prose-first learning chain od software lifecycle-u cez DevOps flow, feedback a systems thinking až po ownership, automation, state convergence, infrastructure lifecycle a meranie delivery outcome-u. Každá kapitola začína priamo vysvetlením mechanizmu; legacy `Metadata`, `Learning` a `L2` scaffold sa už nepoužíva.

Nosný section model je:

```text
business alebo user potreba
→ versionovaná zmena a value stream
→ flow, feedback a learning controls
→ ownership a automation boundary
→ desired/effective state transition
→ delivery a reliability evidence
→ system-level improvement alebo recovery
```

Príklady a zoznamy sumarizujú už vysvetlený model. Príkaz, metrika alebo procesný krok sa nepovažuje za dôkaz sám osebe; text oddeľuje vykonanú aktivitu, authoritative state, effective runtime a používateľský alebo business outcome. Aktuálny authoritative stav sekcie je **20/20 · Ready for user review** po odstránení legacy štruktúry a chapter-by-chapter explanation-depth passe.

## Cieľ zvládnutia

Po dokončení tejto sekcie má byť možné:

- vysvetliť celý tok zmeny od požiadavky po produkčnú prevádzku,
- rozlíšiť DevOps kultúru, praktiky a pracovnú rolu,
- identifikovať úzke miesta a slabé feedback loops v delivery procese,
- vysvetliť vzťah medzi automatizáciou, kvalitou, rýchlosťou a spoľahlivosťou,
- rozlíšiť deklaratívny a imperatívny model,
- vysvetliť idempotenciu a reconciliation loop,
- posúdiť trade-offs mutable a immutable infraštruktúry,
- identifikovať toil, technical debt a systémové anti-patterny,
- použiť value stream mapping a DORA metriky na riadenie zlepšenia,
- obhájiť, prečo konkrétny nástroj alebo proces v systéme existuje.
