# Testing and Software Quality

Táto sekcia vysvetľuje testovanie ako systém spätnej väzby a riadenia rizika. Cieľom nie je maximalizovať počet testov alebo coverage, ale zvoliť správnu kontrolu, scope, prostredie a oracle tak, aby chyba bola zachytená čo najskôr a výsledok bol diagnostikovateľný.

## Predpoklady

Odporúča sa najprv dokončiť [DevOps Foundations](../00-foundations/README.md), [Linux and Systems](../01-linux-and-systems/README.md), [Networking and Web Fundamentals](../02-networking-and-web/README.md) a [Git and Automation Basics](../03-git-and-automation/README.md).

Znalosť Git workflow, automatizácie, HTTP/API kontraktov, databázových hraníc a CI princípov je potrebná na správne umiestnenie testov v delivery pipeline.

## Odporúčané poradie

1. [Verification vs. validation](verification-vs-validation.md)
2. [Test pyramid](test-pyramid.md)
3. [Unit, integration a component tests](unit-integration-component-tests.md)
4. [Contract a API tests](contract-and-api-tests.md)
5. [End-to-end a acceptance tests](end-to-end-and-acceptance-tests.md)
6. [Smoke a regression tests](smoke-and-regression-tests.md)
7. [Performance, load a stress tests](performance-load-stress-tests.md)
8. [Security a infrastructure tests](security-and-infrastructure-tests.md)
9. [Static analysis, linting a type checking](static-analysis-linting-type-checking.md)
10. [Code coverage a quality gates](code-coverage-and-quality-gates.md)
11. [Mocks, stubs a fakes](mocks-stubs-fakes.md)
12. [Flaky tests a test data](flaky-tests-and-test-data.md)
13. [Shift-left](shift-left.md)
14. [Shift-right](shift-right.md)
15. [Chaos testing](chaos-testing.md)

Po tejto sekcii nasleduje CI/CD and Release Engineering. Testovacie stratégie sa tam premenia na konkrétne pipeline stages, quality gates, promotion rules a progressive delivery mechanizmy.

## Výkladový štandard

Každá kapitola začína priamo výkladom testovacieho typu, techniky alebo stratégie. Vysvetľuje subject, scope, failure mode, potrebnú fidelity, oracle a hranicu dôkazu a následne tieto pojmy priebežne aplikuje na Atlas Orders. Kapitola je jeden súvislý odborný text bez samostatnej learning alebo metadata vrstvy.

Konkrétne testy, konfigurácia, výsledky a failure artifacts sa objavujú pri rozhodnutí, ktoré podporujú. Výklad pokračuje od všeobecného mechanizmu cez experiment alebo test contract k Atlas incidentu, diagnosis, recovery a skoršiemu controlu. Inventáre, matice a checklisty zostávajú iba tam, kde presne porovnávajú scope, evidence alebo acceptance podmienky.

## Výklad pojmov je súčasťou príbehu kapitoly

Každá kapitola vysvetľuje odborné pojmy, setup, príkazy a výsledky súvislými odsekmi priamo pred scenárom alebo failure, v ktorom sa používajú. Nový text nie je oddelený ako slovník ani postavený na opisných odrážkach. Zoznamy zostávajú iba tam, kde sú prirodzeným porovnaním, acceptance contractom, kontrolnými otázkami alebo inventárom evidence.

Kód a konfigurácia sú vložené pri mechanizme, ktorý demonštrujú. Nasledujúci text vždy vysvetľuje, čo sa pri vykonaní stane, čo výsledok preukazuje a ktorú časť runtime alebo business správania ešte treba overiť iným testom.

## Čo má čitateľ po sekcii vedieť

Čitateľ má vedieť začať od rizika alebo failure mode-u a zvoliť najnižší test scope, ktorý poskytne dostatočný dôkaz. Musí odlíšiť verification od validation, pomenovať oracle a jeho false-positive alebo false-negative riziko a vysvetliť, pre ktorý artifact, prostredie, konfiguráciu a čas výsledok platí.

Má vedieť navrhnúť unit, integration, component, contract, API, E2E, acceptance, smoke a regression kontroly bez zamieňania ich boundaries. Pri performance experimente musí vedieť definovať workload model, tail-latency a saturation oracle; pri security a infrastructure testoch zase threat, control, plan a runtime evidence. Coverage, static analysis a quality gate má interpretovať ako ohraničený signál, nie ako priamy dôkaz kvality.

Pri nedeterministických alebo produkčných kontrolách má vedieť zachovať first-attempt evidence, izolovať test data, rozlíšiť flaky test od skutočného defectu a bezpečne používať shift-right a chaos experimenty. Výsledok sa uzatvára až recovery, business reconciliation a trvalým regression controlom.

## Stav

Všetkých pätnásť kapitol je po integrovanom full prose rewritingu pripravených na používateľskú kontrolu. Tento stav neznamená automatické používateľské schválenie ani runtime overenie každého nástroja a experimentu.
