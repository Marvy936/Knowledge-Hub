# End-to-end a acceptance tests

End-to-end tests overujú celý používateľský alebo systémový workflow cez viac vrstiev. Acceptance tests overujú, či systém spĺňa dohodnuté business alebo používateľské kritériá.

Tieto pojmy sa môžu prekrývať, ale nie sú totožné:

```text
E2E opisuje scope a technickú cestu.
Acceptance opisuje účel a rozhodnutie o prijateľnosti.
```

## 1. End-to-end test

E2E test sleduje request alebo workflow cez produkčne relevantné boundaries.

Príklad:

```text
browser
→ DNS/TLS
→ reverse proxy
→ frontend
→ API
→ database
→ message broker
→ worker
→ email sandbox
→ výsledok v UI
```

Nie každý E2E test musí zahŕňať všetky systémy. Scope musí byť explicitný.

## 2. Acceptance test

Acceptance test vychádza z business requirement alebo akceptačného kritéria.

Príklad:

```text
Given zákazník má aktívny účet
When odošle objednávku s dostupným produktom
Then objednávka je prijatá presne raz
And zákazník vidí potvrdenie
And skladová rezervácia je vytvorená
```

Acceptance test môže byť:

- unit-level executable specification,
- API-level scenario,
- UI E2E test,
- manuálne user acceptance testing,
- operational acceptance test.

## 3. User acceptance testing

User Acceptance Testing (UAT) vykonáva alebo schvaľuje business používateľ, product owner alebo reprezentatívny stakeholder.

Overuje napríklad:

- použiteľnosť workflow,
- správnosť business rules,
- fit s reálnym procesom,
- reporting,
- legislatívne alebo organizačné očakávania.

UAT nemá nahrádzať technické testy. Stakeholder nemá manuálne odhaľovať chyby, ktoré mala zachytiť automatizovaná suite.

## 4. Operational acceptance testing

Operational acceptance overuje, či je systém prevádzkovateľný.

Oblasti:

- monitoring a alerting,
- logging a tracing,
- backup a restore,
- failover,
- capacity,
- runbooks,
- deployment a rollback,
- access control,
- patching,
- support ownership.

Aplikácia môže spĺňať funkčné acceptance criteria a stále nebyť pripravená na produkciu.

## 5. Kritické user journeys

E2E suite má prioritizovať kritické cesty:

- registrácia a login,
- checkout a payment,
- vytvorenie a spracovanie objednávky,
- reset hesla,
- administratívne schválenie,
- export alebo compliance report,
- disaster-recovery workflow.

Nie každý detail UI potrebuje E2E test. Kritickosť určuje business dopad a pravdepodobnosť regresie.

## 6. Čierna, sivá a biela skrinka

### Black-box E2E

Používa iba verejné rozhrania. Má vysokú fidelity, ale slabšiu diagnostiku a náročnejší setup.

### Gray-box E2E

Používa verejný workflow, ale test môže cez interné API pripraviť dáta alebo čítať diagnostický stav.

### White-box systémový test

Pozná interné komponenty a overuje ich koordináciu.

Gray-box prístup býva praktický kompromis, ak pomocné rozhrania neobchádzajú samotné behavior, ktoré testujeme.

## 7. Test environment fidelity

Produkčne podobné prostredie má zodpovedať kritickým vlastnostiam:

- rovnaké build artifacts,
- podobné network boundaries,
- rovnaké identity a authorization modely,
- kompatibilné database a broker versions,
- podobná konfigurácia TLS a proxy,
- realistické feature flags,
- rovnaký deployment mechanism.

Nemusí mať rovnakú kapacitu. Musí však zachovať vlastnosti relevantné pre testované riziko.

## 8. Test data management

E2E test data musia byť:

- identifikovateľné,
- izolované,
- opakovateľne vytvoriteľné,
- bezpečne čistiteľné,
- bez reálnych osobných údajov,
- kompatibilné s paralelnými behmi.

Preferuj API alebo fixture factory namiesto priameho SQL, ak testuješ systém, ktorého invariants sa vytvárajú cez aplikačnú vrstvu.

Priama databázová príprava je vhodná iba vtedy, keď je explicitne súčasťou gray-box stratégie a neobchádza testované pravidlo.

## 9. Deterministické čakanie

Pevné sleep-y sú častým zdrojom flaky E2E testov.

Zlé:

```text
sleep 10 sekúnd a potom skontroluj výsledok
```

Lepšie:

```text
poll s timeoutom
→ kontroluj konkrétnu podmienku
→ zaznamenaj posledný pozorovaný stav
→ skonči okamžite po úspechu
```

Asynchrónne workflow potrebuje definovaný eventual-consistency contract.

## 10. Browser automation

UI testy musia používať stabilné selectors:

- semantic roles,
- accessible names,
- explicit test IDs tam, kde je to potrebné.

Krehké selectors:

- CSS podľa vizuálnej hierarchie,
- generované class names,
- presná pozícia elementu,
- text, ktorý nie je súčasťou kontraktu.

Test má čakať na stav aplikácie, nie na náhodný čas.

## 11. Page object a screen model

Page object abstrahuje interakciu s UI:

```text
LoginPage.login(user, password)
CheckoutPage.submit_order()
```

Výhody:

- centralizované selectors,
- čitateľnejšie scenáre,
- jednoduchšia údržba.

Riziko:

- príliš generický framework schová behavior,
- page objects obsahujú assertions aj business logiku bez jasných hraníc.

## 12. Service virtualization

Externé služby môžu byť nahradené controlled simulátorom:

- payment sandbox,
- email catcher,
- fake identity provider,
- stub external API.

Tým sa znižuje cena a nondeterminism, ale stráca sa časť fidelity.

Pre kritické externé integrácie doplň:

- contract tests,
- periodické sandbox tests,
- produkčné synthetics,
- monitoring skutočnej integrácie.

## 13. Acceptance criteria

Dobré kritérium je:

- pozorovateľné,
- jednoznačné,
- merateľné,
- viazané na business výsledok,
- testovateľné bez znalosti internej implementácie.

Slabé:

```text
Systém má byť používateľsky prívetivý.
```

Silnejšie:

```text
Používateľ s platnými údajmi dokončí registráciu bez podpory a do 2 minút dostane potvrdenie.
```

Aj silnejšie kritérium môže potrebovať kombináciu automatizácie a usability validation.

## 14. BDD a executable specifications

Behavior-Driven Development používa jazyk zameraný na behavior:

```gherkin
Given ...
When ...
Then ...
```

Výhody:

- spoločný jazyk medzi product, QA a engineering,
- traceability na requirement,
- čitateľné scenarios.

Anti-pattern:

- Gherkin používaný na opis každého kliknutia,
- obrovské scenáre s technickými detailmi,
- step definitions ako duplicita aplikačného kódu.

BDD je collaboration a discovery practice, nie iba syntax test frameworku.

## 15. E2E suite segmentation

Rozdeľ testy podľa účelu:

- PR critical path,
- deployment smoke,
- full regression,
- browser compatibility,
- nightly cross-service,
- pre-release acceptance.

Tagy bez ownershipu sa časom menia na nejasnú taxonómiu. Každá skupina potrebuje definovaný trigger a rozhodnutie.

## 16. Parallelization a sharding

E2E tests možno zrýchliť cez:

- paralelné workers,
- shard podľa historického trvania,
- izolované tenants,
- unikátne identifiers,
- pre-created environment pool.

Riziká:

- zdieľané rate limits,
- rovnaké test accounts,
- environment saturation,
- poradie dependent tests,
- neizolovaný cleanup.

Rýchlejší beh nesmie zmeniť test na nondeterministický load test.

## 17. Failure artifacts

Pri E2E failure uchovaj:

- screenshot,
- video alebo trace,
- browser console,
- network log,
- request/trace ID,
- server logs,
- environment version,
- test data identifiers,
- presný timestamp.

Bez artifacts sa failure často nedá reprodukovať po zániku ephemeral environmentu.

## 18. Flaky E2E tests

Typické príčiny:

- fixed sleeps,
- shared state,
- nestabilné selectors,
- asynchrónne race conditions,
- external dependency,
- environment saturation,
- clock a timezone,
- náhodné poradie dát.

Rerun môže pomôcť diagnostike, ale nesmie automaticky zmeniť červený výsledok na zelený bez evidencie flaky failure.

## 19. Production validation

Niektoré vlastnosti sa overia až v produkcii:

- skutočný identity federation,
- reálny traffic distribution,
- latency medzi regiónmi,
- provider quotas,
- používateľské správanie,
- business conversion.

Použi:

- synthetic transactions,
- canary release,
- feature flags,
- SLI/SLO,
- business metrics,
- session replay podľa privacy pravidiel.

Produkčný experiment potrebuje guardrails a rollback.

## 20. Anti-patterny

### E2E testuje každú kombináciu

Suite exploduje a feedback je nepoužiteľný. Kombinatoriku presuň do unit/property tests.

### Testy závisia od poradia

Samostatný rerun zlyhá alebo vytvorí iný stav.

### Shared admin account

Paralelné testy si navzájom menia permissions a dáta.

### UI test obchádza kritickú vrstvu

Priamy DB insert môže obísť behavior, ktoré mal workflow overovať.

### UAT ako posledná QA fáza

Business feedback prichádza príliš neskoro namiesto priebežnej collaboration.

## 21. Rozhodovací rámec

1. Aký používateľský alebo operačný journey chránime?
2. Ktoré boundaries musia byť reálne?
3. Ktoré dependencies môžeme virtualizovať?
4. Aké acceptance criterion rozhoduje o úspechu?
5. Ako pripravíme a izolujeme test data?
6. Ako budeme čakať na asynchrónny výsledok?
7. Aké artifacts potrebujeme pri failure?
8. Kde sa test spustí a aké rozhodnutie blokuje?
9. Aký je runtime a maintenance budget?
10. Čo sa musí validovať až v produkcii?

## 22. Kontrolné otázky

1. Aký je rozdiel medzi E2E a acceptance testom?
2. Čo je UAT a čo nemá nahrádzať?
3. Čo zahŕňa operational acceptance?
4. Aký je rozdiel medzi black-box a gray-box E2E testom?
5. Ako definovať environment fidelity?
6. Prečo sú pevné sleep-y problematické?
7. Aké selectors sú stabilné pre browser testy?
8. Čo je service virtualization?
9. Prečo BDD nie je iba Gherkin syntax?
10. Aké dôkazy treba zachovať pri E2E failure?

## Glossary impact

Relevantné pojmy: end-to-end test, acceptance test, UAT, operational acceptance testing, critical user journey, service virtualization, BDD, executable specification, page object, synthetic transaction a failure artifact.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Contract a API tests](contract-and-api-tests.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Smoke a regression tests →](smoke-and-regression-tests.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
