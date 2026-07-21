# Testing and Software Quality glossary entries

## Acceptance test

Test overujúci, či systém spĺňa dohodnuté business alebo používateľské acceptance criteria. Môže bežať na API, UI alebo inej vrstve. Pozri [End-to-end a acceptance tests](docs/04-testing-and-quality/end-to-end-and-acceptance-tests.md).

## API contract

Dohoda o observable API behavior zahŕňajúca paths, methods, schemas, status codes, errors, authentication, compatibility a ďalšie semantics. Pozri [Contract a API tests](docs/04-testing-and-quality/contract-and-api-tests.md).

## API test

Runtime test verejného API rozhrania overujúci response, semantics, authorization a side effects. Jeho scope môže byť component, integration alebo E2E. Pozri [Contract a API tests](docs/04-testing-and-quality/contract-and-api-tests.md).

## BDD — Behavior-Driven Development

Collaboration a discovery prístup používajúci príklady správania a spoločný jazyk na spresnenie požiadaviek; Gherkin je iba jedna možná reprezentácia. Pozri [End-to-end a acceptance tests](docs/04-testing-and-quality/end-to-end-and-acceptance-tests.md).

## Build Verification Test

Krátky smoke test nad novým buildom overujúci, či je artifact spustiteľný a vhodný na drahšie testovanie. Pozri [Smoke a regression tests](docs/04-testing-and-quality/smoke-and-regression-tests.md).

## Component test

Test celého deployovateľného komponentu cez jeho verejné rozhranie, pričom externé dependencies môžu byť nahradené controlled doubles. Pozri [Unit, integration a component tests](docs/04-testing-and-quality/unit-integration-component-tests.md).

## Consumer-driven contract

Kontrakt definovaný consumerom podľa interactions, ktoré reálne potrebuje, a overovaný providerom v jeho pipeline. Pozri [Contract a API tests](docs/04-testing-and-quality/contract-and-api-tests.md).

## Contract test

Test kompatibility producer/consumer rozhrania bez potreby spustiť celý distribuovaný systém. Pozri [Contract a API tests](docs/04-testing-and-quality/contract-and-api-tests.md).

## End-to-end test

Test workflow prechádzajúci cez viac produkčne relevantných vrstiev alebo procesných hraníc od vstupu po observable výsledok. Pozri [End-to-end a acceptance tests](docs/04-testing-and-quality/end-to-end-and-acceptance-tests.md).

## Executable specification

Príklad alebo pravidlo zapísané vo forme, ktorú možno automaticky spustiť ako dôkaz behavior. Pozri [End-to-end a acceptance tests](docs/04-testing-and-quality/end-to-end-and-acceptance-tests.md).

## Failure artifact

Diagnostický dôkaz zachovaný pri zlyhaní testu, napríklad screenshot, trace, log, packet capture, request ID alebo environment metadata. Pozri [End-to-end a acceptance tests](docs/04-testing-and-quality/end-to-end-and-acceptance-tests.md).

## False negative — testing

Výsledok, pri ktorom test prejde, hoci systém obsahuje chybu relevantnú pre testovaný risk. Pozri [Verification vs. validation](docs/04-testing-and-quality/verification-vs-validation.md).

## False positive — testing

Výsledok, pri ktorom test hlási chybu, hoci testované správanie je správne. Pozri [Verification vs. validation](docs/04-testing-and-quality/verification-vs-validation.md).

## Hermetic test

Test, ktorý kontroluje všetky významné vstupy a nespolieha sa na nepredvídateľný externý stav. Môže používať disposable reálne dependencies. Pozri [Unit, integration a component tests](docs/04-testing-and-quality/unit-integration-component-tests.md).

## Integration test

Test reálnej spolupráce komponentov alebo systému s technickou dependency, napríklad databázou, brokerom, filesystemom alebo cloud API. Pozri [Unit, integration a component tests](docs/04-testing-and-quality/unit-integration-component-tests.md).

## Mutation testing

Technika zámerne meniaca produkčný kód a overujúca, či test suite tieto mutácie zachytí. Pozri [Unit, integration a component tests](docs/04-testing-and-quality/unit-integration-component-tests.md).

## Operational acceptance testing

Overenie, že systém je prevádzkovateľný: má monitoring, recovery, backup/restore, capacity, runbooks, access controls a deployment/rollback mechanizmy. Pozri [End-to-end a acceptance tests](docs/04-testing-and-quality/end-to-end-and-acceptance-tests.md).

## Provider state

Deterministicky pripravený stav providera potrebný na overenie konkrétnej consumer-driven contract interaction. Pozri [Contract a API tests](docs/04-testing-and-quality/contract-and-api-tests.md).

## Quarantine — testing

Dočasné oddelenie nestabilného testu z blocking suite s explicitným ownerom, issue a termínom opravy; nie trvalé ignorovanie failure. Pozri [Test pyramid](docs/04-testing-and-quality/test-pyramid.md).

## Regression test

Test chrániaci existujúce funkčné alebo nefunkčné správanie pred nechcenou zmenou. Pozri [Smoke a regression tests](docs/04-testing-and-quality/smoke-and-regression-tests.md).

## Requirement traceability

Väzba od business potreby a požiadavky cez risk a control až po test a dôkaz výsledku. Pozri [Verification vs. validation](docs/04-testing-and-quality/verification-vs-validation.md).

## Sanity test

Krátka cielená kontrola konkrétnej zmeny alebo opravy. Význam sa medzi tímami líši, preto musí mať explicitný scope. Pozri [Smoke a regression tests](docs/04-testing-and-quality/smoke-and-regression-tests.md).

## Service virtualization

Nahradenie externého systému kontrolovaným simulátorom alebo sandboxom tak, aby bol test deterministickejší a lacnejší. Pozri [End-to-end a acceptance tests](docs/04-testing-and-quality/end-to-end-and-acceptance-tests.md).

## Smoke test

Krátky široký test overujúci, či je build alebo deployment dostatočne funkčný na pokračovanie ďalších kontrol alebo prevádzky. Pozri [Smoke a regression tests](docs/04-testing-and-quality/smoke-and-regression-tests.md).

## Synthetic monitoring

Pravidelné spúšťanie kontrolovaného produkčného scenára z definovanej lokality na overenie používateľskej cesty. Pozri [Smoke a regression tests](docs/04-testing-and-quality/smoke-and-regression-tests.md).

## Test double

Kontrolovaná náhrada dependency používaná v teste; zahŕňa napríklad stub, fake, mock alebo spy. Pozri [Unit, integration a component tests](docs/04-testing-and-quality/unit-integration-component-tests.md).

## Test fidelity

Miera, do akej test zachováva produkčne relevantné komponenty, protokoly, konfiguráciu a failure modes. Pozri [Test pyramid](docs/04-testing-and-quality/test-pyramid.md).

## Test oracle

Mechanizmus alebo pravidlo rozhodujúce, či je pozorovaný test result správny. Pozri [Verification vs. validation](docs/04-testing-and-quality/verification-vs-validation.md).

## Test pyramid

Model test portfolio s veľkou vrstvou rýchlych úzkych kontrol, menšou integračnou vrstvou a obmedzeným počtom drahých E2E testov. Pozri [Test pyramid](docs/04-testing-and-quality/test-pyramid.md).

## Test trophy

Alternatívny model zvýrazňujúci static checks a integration tests ako hlavný zdroj hodnoty, s menšou unit a E2E vrstvou. Pozri [Test pyramid](docs/04-testing-and-quality/test-pyramid.md).

## UAT — User Acceptance Testing

Acceptance activity vykonaná alebo schválená reprezentatívnym business používateľom či stakeholderom na overenie fitu s reálnym procesom. Pozri [End-to-end a acceptance tests](docs/04-testing-and-quality/end-to-end-and-acceptance-tests.md).

## Unit test

Rýchly test malej izolovanej jednotky správania s úzkym diagnostickým scope-om. Pozri [Unit, integration a component tests](docs/04-testing-and-quality/unit-integration-component-tests.md).

## Validation — testing

Overenie, či systém rieši správny používateľský alebo business problém v reálnom kontexte. Pozri [Verification vs. validation](docs/04-testing-and-quality/verification-vs-validation.md).

## Verification — testing

Overenie, či systém alebo artifact zodpovedá explicitnej špecifikácii, kontraktu alebo pravidlu. Pozri [Verification vs. validation](docs/04-testing-and-quality/verification-vs-validation.md).