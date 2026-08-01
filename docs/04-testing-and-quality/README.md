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

Každá kapitola najprv samostatne vysvetlí, čo daný testovací typ, technika alebo stratégia znamená, aký failure mode alebo riziko rieši, aký subject a scope používa, akú fidelity potrebuje a aký oracle vytvára pass/fail verdict. Nasleduje neutrálny príklad a hranica dôkazu — teda čo test preukazuje a čo z neho nemožno odvodiť. Až potom kapitola prejde k sekcii `Atlas scenár a praktické použitie`, kde sa model aplikuje na Atlas Orders release, doplnia sa artifacts, failure path, diagnosis a recovery. Scenár upevňuje všeobecný výklad; nenahrádza ho.

Hlavný výklad nesú súvislé odseky. Inventáre, matice a checklisty zostávajú iba tam, kde pomáhajú presne porovnať scope, evidence alebo acceptance podmienky.

## Cieľ zvládnutia

Po dokončení sekcie má byť možné:

- rozlíšiť verification od validation a navrhnúť traceability od požiadavky cez riziko po dôkaz,
- definovať test oracle a posúdiť false-positive a false-negative riziko,
- používať test pyramid alebo test trophy ako risk-based model, nie ako fixnú percentuálnu kvótu,
- zvoliť najnižší test scope, ktorý spoľahlivo odhalí daný failure mode,
- rozlíšiť unit, integration a component test podľa reálnych boundaries a dependencies,
- navrhnúť hermetic, paralelizovateľné testy s deterministickým setupom a cleanupom,
- rozlíšiť API test od contract testu a používať producer-driven aj consumer-driven contracts,
- posúdiť backward/forward compatibility API alebo event schema,
- navrhnúť kritické E2E journeys, acceptance criteria, test data a failure artifacts,
- vytvoriť krátky deployment smoke gate a risk-based regression suite,
- rozlíšiť load, stress, spike, soak, capacity a scalability test,
- navrhnúť realistický open alebo closed workload model a interpretovať tail latency, throughput, concurrency a saturation,
- korelovať performance výsledky s CPU, memory, I/O, network, queue a dependency metrics,
- navrhovať threat-informed security tests pre application, supply chain, IAM, network a infrastructure boundaries,
- vrstviť IaC syntax, policy, plan a runtime verification,
- rozlíšiť SAST, DAST, IAST, SCA a artifact scanning a triagovať findings podľa reachability a impactu,
- používať formatter, linter, type checker a data-flow analysis bez zamieňania statického signálu za runtime dôkaz,
- interpretovať line, branch, condition a diff coverage bez používania coverage ako priamej metriky kvality,
- navrhnúť blocking/advisory quality gates, ratcheting a auditovateľný exception lifecycle,
- zvoliť medzi dummy, stub, fake, spy, mock a reálnou dependency podľa testovaného rizika,
- minimalizovať contract drift a over-specification test doubles,
- diagnostikovať flaky tests, izolovať test data a odstrániť timing, shared-state a order dependencies,
- spravovať quarantine, retries, first-attempt pass rate a failure artifacts bez rerun-until-green anti-patternu,
- posúvať kontroly doľava podľa rizika, fidelity, času feedbacku a maintenance costu,
- navrhovať developer feedback loops, golden paths a autoritatívne CI guardrails,
- používať shift-right produkčnú validáciu, synthetics, RUM, canary, feature flags a progressive delivery,
- rozlíšiť technickú, funkčnú a business validáciu po deploymente,
- definovať steady-state hypothesis, experiment contract, blast radius a abort criteria,
- navrhnúť bezpečný chaos experiment pre process, network, dependency, resource alebo data failure,
- overiť recovery, graceful degradation, RPO/RTO a previesť výsledok experimentu na trvalú kontrolu.

## Stav

| Téma | Status | Úroveň |
|---|---|---|
| Verification vs. validation | Learning | L2 |
| Test pyramid | Learning | L2 |
| Unit, integration a component tests | Learning | L2 |
| Contract a API tests | Learning | L2 |
| End-to-end a acceptance tests | Learning | L2 |
| Smoke a regression tests | Learning | L2 |
| Performance, load a stress tests | Learning | L2 |
| Security a infrastructure tests | Learning | L2 |
| Static analysis, linting a type checking | Learning | L2 |
| Code coverage a quality gates | Learning | L2 |
| Mocks, stubs a fakes | Learning | L2 |
| Flaky tests a test data | Learning | L2 |
| Shift-left | Learning | L2 |
| Shift-right | Learning | L2 |
| Chaos testing | Learning | L2 |
