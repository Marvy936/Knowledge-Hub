# Test pyramid

Test pyramid je model rozdelenia automatizovaných testov podľa scope, rýchlosti, ceny, fidelity a diagnostickej hodnoty.

Klasická interpretácia:

```text
        E2E
     Integration
        Unit
```

Nejde o presný počet testov ani univerzálny pomer. Pointou je mať veľa rýchlych a izolovaných kontrol, menšiu vrstvu integračných testov a iba nevyhnutný počet drahých end-to-end scenárov.

## 1. Prečo pyramída vznikla

Komplexné systémy potrebujú overovať:

- lokálnu logiku,
- spoluprácu komponentov,
- externé kontrakty,
- reálny používateľský workflow.

Jeden typ testu nedokáže optimalizovať všetko naraz. Čím širší scope testu, tým typicky rastie:

- čas vykonania,
- počet závislostí,
- variabilita prostredia,
- náročnosť diagnostiky,
- cena test data setupu,
- riziko flaky výsledku.

Pyramída preto rozdeľuje riziká medzi vrstvy.

## 2. Spodná vrstva: unit tests

Unit test overuje malú jednotku správania s minimom externých závislostí.

Silné vlastnosti:

- milisekundový až sekundový feedback,
- presná lokalizácia chyby,
- jednoduché edge cases,
- lacný paralelný beh,
- vhodnosť pre property-based testing.

Limity:

- neoveruje wiring,
- neoveruje serializáciu,
- neoveruje reálnu databázu alebo sieť,
- môže byť príliš previazaný na implementáciu.

## 3. Stredná vrstva: integration a component tests

Táto vrstva overuje spoluprácu reálnych častí systému:

- aplikácia a databáza,
- service a message broker,
- repository a filesystem,
- API adapter a reálny serializer,
- viac modulov v jednom procese,
- celý komponent s fake externými službami.

Je pomalšia než unit tests, ale zachytáva chyby, ktoré mocks neodhalia:

- schema mismatch,
- transaction semantics,
- connection configuration,
- encoding,
- timeouty,
- reálne constraints.

## 4. Vrchná vrstva: end-to-end tests

E2E test sleduje workflow cez väčšiu časť produkčne podobného systému.

Príklad:

```text
browser
→ reverse proxy
→ API
→ database
→ message broker
→ worker
→ výsledok v UI
```

Výhody:

- vysoká fidelity,
- kontrola kritických používateľských ciest,
- overenie deployment wiring-u.

Nevýhody:

- pomalé,
- drahé,
- citlivé na test data a timing,
- zlyhanie má veľa možných príčin,
- zle sa škálujú.

## 5. Test trophy

Pri frontendových a distribuovaných aplikáciách sa používa aj model test trophy, ktorý kladie väčší dôraz na integration tests:

```text
       E2E
   Integration
      Unit
 Static checks
```

Tento model reaguje na problém, že veľmi izolované unit tests môžu overovať internú implementáciu, ale nie skutočné správanie komponentov.

Pyramid a trophy nie sú protiklady. Obe hovoria, že širšie testy majú byť vzácnejšie a že statické a integračné kontroly poskytujú vysokú hodnotu.

## 6. Test diamond a ice cream cone

### Test diamond

Viac integration/component tests, menej unit aj E2E testov. Môže byť rozumný pri systéme, kde hlavné riziko leží v integrácii protokolov a storage.

### Ice cream cone

Veľa manuálnych alebo E2E testov a málo nižších vrstiev.

Dôsledky:

- pomalý feedback,
- dlhé regresné cykly,
- vysoká cena údržby,
- časté flaky failures,
- nejasný root cause.

Ice cream cone je typický anti-pattern.

## 7. Scope nie je to isté ako procesná hranica

Unit nemusí znamenať jedna function. Unit je izolovaná jednotka správania.

Integration nemusí znamenať dve microservices. Môže ísť o jednu aplikáciu a skutočnú databázu.

E2E nemusí vždy zahŕňať celý podnikový ekosystém. Má pokryť definovanú end-to-end cestu relevantnú pre risk.

## 8. Fidelity vs. determinism

Test s vysokou fidelity používa viac produkčných komponentov, ale môže byť menej deterministický.

Test s vysokým determinismom izoluje dependencies, ale môže prehliadnuť runtime rozdiely.

Dobrá stratégia kombinuje:

- deterministické unit tests pre logiku,
- reálne integration tests pre hranice,
- contract tests pre distribuované rozhrania,
- malý počet E2E tests pre kritické journeys,
- produkčné synthetic a SLO signály pre reálne prostredie.

## 9. Rýchlosť feedbacku

Test patrí čo najnižšie v pyramíde, kde ešte spoľahlivo zachytí dané riziko.

Príklady:

- invalid enum: unit alebo schema test,
- SQL constraint: database integration test,
- consumer/provider mismatch: contract test,
- nesprávny reverse-proxy route: deployment smoke alebo E2E,
- nefunkčný checkout journey: E2E/acceptance.

Presun chyby do nižšej vrstvy skracuje feedback a znižuje náklady.

## 10. Redundancia nie je automaticky zlá

Rovnaké kritické invarianty môžu byť overené vo viacerých vrstvách.

Príklad authorization:

- unit test policy logiky,
- integration test repository scope,
- API test forbidden response,
- E2E test tenant isolation.

Redundancia je užitočná, keď vrstvy chránia proti rozdielnym failure modes. Zbytočná je vtedy, keď desiatky pomalých testov kopírujú rovnaký assertion bez novej fidelity.

## 11. Test suite ako portfolio rizík

Test suite sa nemá navrhovať podľa percentuálneho cieľa, ale podľa rizík:

- business criticality,
- pravdepodobnosť chyby,
- blast radius,
- frekvencia zmeny,
- zložitosť integrácie,
- schopnosť observability,
- cena zlyhania.

Kritická payment idempotency potrebuje viac vrstiev než statická stránka s nízkym dopadom.

## 12. Časové rozpočty

Praktický pipeline model:

```text
pre-commit: sekundy
PR fast lane: jednotky minút
full integration: desiatky minút
nightly/system suite: dlhší beh
pre-release: cielené E2E a performance
production: synthetic a SLO validation
```

Dlhší test nepatrí automaticky iba do nightly jobu. Kritický gate musí byť pred rozhodnutím, ktoré chráni.

## 13. Quarantine a flaky tests

Flaky test nemá zostať bez vlastníka v blocking suite.

Možnosti:

- okamžitá oprava,
- dočasná quarantine s issue a deadline,
- stabilizácia test data a clocku,
- odstránenie sleep-based synchronizácie,
- zníženie scope,
- presun assertionu do vhodnejšej vrstvy.

Ignorovaný flaky test degraduje celý feedback systém.

## 14. Infrastructure testing pyramid

Pre infraštruktúru môže pyramída vyzerať takto:

```text
statická syntax/schema/policy
→ unit test modulov a renderingu
→ plan a integration test v sandboxe
→ deployment smoke test
→ failover/restore/game day
```

Príklady:

- `terraform validate` a policy checks,
- testovanie modul outputs,
- apply do ephemeral accountu,
- network connectivity probe,
- disaster-recovery validation.

## 15. Anti-patterny

### Pyramída ako kvóta

„Musíme mať 70 % unit, 20 % integration, 10 % E2E“ bez väzby na riziko.

### Všetko cez browser

UI testy overujú detaily, ktoré by boli stabilnejšie a rýchlejšie na API alebo unit úrovni.

### Všetko mockované

Suite je rýchla, ale neoverí reálne rozhrania a runtime constraints.

### Duplicitné assertiony bez novej hodnoty

Rovnaký edge case je kopírovaný v desiatkach E2E testov.

### Pomalá suite bez segmentácie

Každá drobná zmena čaká na kompletné systémové testy bez affected-test selection.

## 16. Rozhodovací rámec

Pre nový test sa opýtaj:

1. Aké riziko test pokrýva?
2. Aký najmenší scope ho spoľahlivo odhalí?
3. Potrebuje reálnu databázu, sieť alebo externú službu?
4. Aký je test oracle?
5. Ako rýchlo musí poskytnúť feedback?
6. Aký je setup a cleanup cost?
7. Ako sa diagnostikuje failure?
8. Bude test deterministický?
9. Dupľuje už existujúci test alebo pridáva novú fidelity?
10. Kto ho vlastní?

## 17. Kontrolné otázky

1. Čo je základná myšlienka test pyramid?
2. Prečo E2E testy nemajú tvoriť väčšinu suite?
3. Aký je rozdiel medzi test pyramid a test trophy?
4. Čo je ice cream cone anti-pattern?
5. Prečo scope testu nie je definovaný iba počtom procesov?
6. Ako súvisí fidelity s determinismom?
7. Kedy je redundancia medzi vrstvami užitočná?
8. Ako navrhneš test portfolio podľa rizika?
9. Čo znamená presun testu do nižšej vrstvy?
10. Ako by vyzerala test pyramid pre Infrastructure as Code?

## Glossary impact

Relevantné pojmy: test pyramid, test trophy, test diamond, ice cream cone, test scope, fidelity, determinism, test portfolio a quarantine.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Verification vs. validation](verification-vs-validation.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Unit, integration a component tests →](unit-integration-component-tests.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
