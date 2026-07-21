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

Ďalší blok sekcie doplní performance/load/stress tests, security a infrastructure tests, static analysis, coverage a quality gates, test doubles, flaky tests a test data, shift-left, shift-right a chaos testing.

## Cieľ zvládnutia

Po dokončení aktuálneho bloku má byť možné:

- rozlíšiť verification od validation a navrhnúť traceability od požiadavky cez riziko po dôkaz,
- definovať test oracle a posúdiť false-positive a false-negative riziko,
- používať test pyramid alebo test trophy ako risk-based model, nie ako fixnú percentuálnu kvótu,
- zvoliť najnižší test scope, ktorý spoľahlivo odhalí daný failure mode,
- rozlíšiť unit, integration a component test podľa reálnych boundaries a dependencies,
- navrhnúť hermetic, paralelizovateľné testy s deterministickým setupom a cleanupom,
- používať reálne dependencies, stubs, fakes a mocks podľa rizika integrácie,
- rozlíšiť API test od contract testu a používať producer-driven aj consumer-driven contracts,
- posúdiť backward/forward compatibility API alebo event schema,
- testovať authorization, idempotency, pagination a optimistic concurrency,
- navrhnúť kritické E2E journeys, acceptance criteria, test data a failure artifacts,
- rozlíšiť UAT, operational acceptance a produkčnú validation,
- vytvoriť krátky deployment smoke gate a risk-based regression suite,
- spravovať flaky tests, baselines, test selection a post-incident regression bez rerun-until-green anti-patternu.

## Stav

| Téma | Status | Úroveň |
|---|---|---|
| Verification vs. validation | Learning | L2 |
| Test pyramid | Learning | L2 |
| Unit, integration a component tests | Learning | L2 |
| Contract a API tests | Learning | L2 |
| End-to-end a acceptance tests | Learning | L2 |
| Smoke a regression tests | Learning | L2 |