from __future__ import annotations

BLOCKS: dict[str, str] = {
    "docs/04-testing-and-quality/verification-vs-validation.md": r'''## Ako sa z pozorovania stane testovací verdikt

Test nevytvára verdikt iba tým, že spustí kód. Najprv potrebuje presne pomenovaný subject, vstupné podmienky a pozorovanie, ktoré sa bude porovnávať s očakávaním. Pravidlo, podľa ktorého sa z pozorovania stane `PASS` alebo `FAIL`, sa nazýva **test oracle**. Oraclom môže byť konkrétna hodnota, invariant, schema, referenčný model alebo business pravidlo. Dôležité je, aby bolo jasné, prečo práve toto pravidlo predstavuje správnosť pre daný test scope.

Assertion je technický zápis oraclu. Keď test overí `actual_total == expected_total`, runner iba vykoná porovnanie; dôveryhodnosť výsledku závisí od toho, či `expected_total` vznikol z nezávislého a správneho pravidla. Ak test odvodí očakávanú hodnotu rovnakým chybným algoritmom ako produkčný kód, môže byť zelený aj pri defekte. Preto sa pri významných invariantov používa jednoduchší referenčný model, explicitný príklad alebo business pravidlo, ktoré nie je iba kópiou implementácie.

Slabý oracle vytvára dva typy omylov. **False positive** znamená, že kontrola hlási problém, hoci požadované správanie je správne. **False negative** znamená, že kontrola prejde, hoci subject porušuje dôležitý kontrakt. HTTP test, ktorý kontroluje iba status `200`, môže mať false negative pri nesprávnej cene, chýbajúcom audit evente alebo duplicitnom side effecte. Silnejší verdikt preto spája transportný výsledok s business hodnotou, počtom side effectov a následným read-backom state-u.

Verification a validation používajú rovnakú logiku dôkazu, ale porovnávajú výsledok s inou autoritou. Verification sa pýta, či subject spĺňa deklarovaný kontrakt. Validation sa pýta, či tento kontrakt a výsledok riešia skutočnú používateľskú alebo prevádzkovú potrebu. Zelená verification preto ešte neznamená, že systém prináša správnu hodnotu; a pozitívna používateľská skúsenosť neospravedlňuje porušenie bezpečnostného alebo dátového kontraktu.

Traceability uzatvára reťazec `riziko → požiadavka → kontrola → oracle → evidence → rozhodnutie`. Pri každom výsledku musí byť možné povedať, pre ktorý artifact, konfiguráciu, prostredie a čas platí. Bez tejto väzby je zelený test iba izolovaná udalosť, nie použiteľný release dôkaz.

''',
    "docs/04-testing-and-quality/test-pyramid.md": r'''## Ako vybrať správny test scope

Test pyramid nie je príkaz, aby každá codebase mala presný počet unit, integration a end-to-end testov. Je to heuristika o cene spätnej väzby. Čím väčší scope test vykonáva, tým viac reálnych hraníc môže pozorovať, ale zároveň rastie čas, množstvo setupu, počet možných príčin zlyhania a náročnosť diagnostiky. Malý test býva rýchly a presný, no neposkytuje dôkaz o konfigurácii, sieti alebo spolupráci procesov.

Správna otázka preto nie je „do ktorej vrstvy patrí tento test podľa názvu frameworku“, ale „aký najmenší scope dokáže zachytiť konkrétny failure mode“. Výpočet ceny alebo authorization decision možno overiť unit testom, pretože riziko leží v lokálnej logike. SQL transakcia, serializácia eventu alebo správanie retry klienta potrebuje reálny adapter a integration scope. Kritická používateľská cesta potrebuje niekoľko end-to-end kontrol, pretože jej riziko vzniká až spojením identity, routingu, aplikácie, databázy a side effectu.

Fidelity označuje, do akej miery testované prostredie a závislosti reprodukujú mechanizmus, o ktorom chceme rozhodovať. Fake databáza môže byť vhodná pre domain workflow, ale nevie potvrdiť isolation level, index behavior alebo engine-specific SQL. Vyššia fidelity však sama osebe nevytvára lepší test. End-to-end test s neurčitým oraclom môže byť menej hodnotný než malý component test, ktorý presne kontroluje invariant a forbidden outcome.

Portfólio preto vzniká od rizík. Veľa lacných testov chráni lokálnu logiku a hraničné prípady, menší počet integračných testov chráni technologické kontrakty a úzky súbor vyšších testov overuje najdôležitejšie cesty. Keď vyšší test odhalí defect, tím sa má pýtať, či možno rovnaký failure mode zachytiť skôr a lacnejšie. To neznamená odstrániť pôvodný end-to-end dôkaz, ale doplniť rýchlejšiu regresnú kontrolu na vhodnej hranici.

Pyramid sa mení podľa architektúry. Služba s bohatou domain logikou bude mať inú skladbu než tenký integračný gateway alebo dátová pipeline. Dôležité je, aby žiadne kritické riziko nezostalo pokryté iba pomalým, flaky alebo slabo diagnostickým testom.

''',
    "docs/04-testing-and-quality/unit-integration-component-tests.md": r'''## Ako určiť hranicu unit, integration a component testu

Názov testu neurčuje framework, ale hranica subjectu a reálnych závislostí. **Unit test** vykonáva malú logickú jednotku v jednom procese a nahrádza externé hranice kontrolovanými vstupmi. Jeho cieľom je rýchlo a presne overiť pravidlo, nie simulovať celý runtime. Ak test spúšťa Spring, reálnu databázu a broker, nie je unit testom iba preto, že testuje jednu metódu.

**Integration test** overuje konkrétne spojenie medzi komponentom a reálnou technologickou hranicou. Môže ísť o SQL schema a transakciu, HTTP klienta proti sandbox serveru, serializáciu do skutočného brokera alebo načítanie configuration parserom, ktorý používa produkcia. Jeho hodnota je práve v tom, že nebezpečnú hranicu nenahrádza pohodlným fake-om. Zároveň má zostať úzky, aby bolo pri zlyhaní jasné, ktorý adapter alebo contract je podozrivý.

**Component test** spúšťa väčšiu časť služby ako celok, typicky cez jej verejné API, ale okolité služby nahrádza riadenými simulátormi. Takýto test dokáže overiť routing v procese, dependency injection, persistence adaptery, background worker a business workflow bez nestability celého distribuovaného prostredia. Component scope je vhodný, keď defect vzniká spoluprácou viacerých modulov jednej služby, ale nie je potrebné nasadiť celý produkt.

Setup, action a assertion musia rešpektovať túto hranicu. Test najprv vytvorí známy state, potom vykoná operáciu cez rovnaký vstupný bod ako produkcia a napokon overí výsledok aj forbidden side effects. Pri databázovom teste nestačí skontrolovať návratovú hodnotu repository; read-back má potvrdiť commitnuté rows, constraints a stav po opakovaní operácie. Pri component teste nestačí HTTP `202`; treba overiť, či workflow skončil v správnom terminal state a či simulator zaznamenal očakávaný počet volaní.

Test doubles sa používajú iba za hranicou, ktorú daný test nechce dokazovať. Ak je predmetom testu SQL transakcia, databáza nemôže byť mock. Ak je predmetom retry state machine, dependency môže byť programovateľný fake, ktorý vie v presnom poradí vrátiť timeout, success a duplicate response. Hranica testu tak priamo určuje, ktoré dôkazy výsledok poskytuje a ktoré musia dodať ďalšie vrstvy portfólia.

''',
    "docs/04-testing-and-quality/contract-and-api-tests.md": r'''## Ako čítať API contract a runtime dôkaz

API contract nie je iba tvar JSON dokumentu. Zahŕňa operation identity, HTTP metódu a path, status codes, headers, authentication, authorization, idempotency, error semantics, ordering, pagination a význam jednotlivých fields. Schema môže potvrdiť, že `amount` je číslo, ale nevie automaticky potvrdiť menu, rounding pravidlo alebo to, či opakovaný request vytvorí druhú platbu.

Contract test porovnáva producer alebo consumer s explicitnou verziou tohto rozhrania. Producer test overí, že implementácia dokáže splniť podporované očakávania. Consumer test zachytí, ktoré časti rozhrania klient skutočne používa. Consumer-driven contract je užitočný pri koordinácii služieb, ale jeho úspech nepreukazuje, že inventory consumerov je úplný ani že runtime routing posiela traffic na testovanú generation.

Runtime API test vykonáva request cez reálny listener, middleware a deployment path. Napríklad:

```bash
response="$(curl --fail-with-body \
  -H 'Idempotency-Key: order-8421' \
  -H 'Content-Type: application/json' \
  -d '{"amount":5000,"currency":"EUR"}' \
  https://api.atlas.example/orders)"

jq -e '.status == "ACCEPTED" and .currency == "EUR"' <<<"$response"
```

`curl` s úspešným exit statusom preukazuje, že transport a HTTP policy považovali odpoveď za úspešnú. `jq -e` pridáva oracle nad vybranými fields. Stále však nepreukazuje final completion, presný počet side effectov ani správanie pri opakovaní. Silnejší test odošle rovnaký idempotency key druhýkrát, prečíta order state a overí, že provider alebo ledger eviduje iba jednu business operáciu.

Backward compatibility sa posudzuje voči existujúcim consumerom, nie iba voči novej OpenAPI schéme. Odstránenie optional field-u, zmena enumu alebo odlišný error code môže byť breaking change aj pri syntakticky validnej odpovedi. Preto contract evidence potrebuje verziu contractu, producer artifact, consumer population a výsledky negatívnych scenárov. Až kombinácia statického contractu, runtime requestu a business read-backu poskytne použiteľný release dôkaz.

''',
    "docs/04-testing-and-quality/end-to-end-and-acceptance-tests.md": r'''## Ako ohraničiť end-to-end a acceptance dôkaz

End-to-end test sleduje operáciu cez viac vrstiev systému. Jeho „end“ musí byť pomenovaný: môže začínať na verejnom API alebo v browseri a končiť final state-om v databáze, odoslaným eventom či potvrdeným externým side effectom. Test, ktorý skončí pri HTTP `202`, nie je end-to-end dôkazom asynchrónneho workflowu, ak skutočný používateľský výsledok vzniká až po spracovaní queue a provider response.

Acceptance test odpovedá na inú otázku. Posudzuje, či výsledok spĺňa používateľské alebo business pravidlo. Môže byť vykonaný end-to-end, ale nemusí; business pravidlo možno často overiť aj component testom s vysokou fidelity. Naopak technický end-to-end smoke test môže potvrdiť routing a persistence bez toho, aby dokazoval, že workflow je pre používateľa správny alebo zrozumiteľný.

Vyšší scope potrebuje disciplinovaný setup. Test data musí mať unikátnu identity, tenant a cleanup policy. Identity, feature flags, time, dependencies a environment generation musia byť zaznamenané, inak failure nie je reprodukovateľný. Pri paralelných runoch nesmú testy zdieľať rovnaký order ID alebo meniť globálnu konfiguráciu bez izolácie.

Oracle má sledovať finálny outcome aj forbidden outcomes. Pri objednávke nestačí nájsť row so stavom `COMPLETED`; test má overiť cenu, tenant ownership, jeden audit event, jeden provider side effect a absenciu duplicitnej operácie po retry. Ak test zlyhá, evidence má zachovať request ID, trace, deployment generation a relevantné state transitions pred cleanupom.

End-to-end testy sú drahé a citlivé na okolité systémy, preto nemajú niesť celé regresné portfólio. Používajú sa na kritické reťazce a integračné predpoklady, ktoré nižšie scope-y nevedia pozorovať. Defect zistený na tejto vrstve sa má doplniť menším testom tam, kde vznikla najskoršia diskriminačná hranica, zatiaľ čo vyšší test zostane dôkazom celého workflowu.

''',
    "docs/04-testing-and-quality/smoke-and-regression-tests.md": r'''## Ako rozdeliť smoke a regression kontrolu

Smoke test je malá, rýchla kontrola, či je nová generation vôbec spôsobilá na ďalšie testovanie alebo expozíciu. Neoveruje celý produkt. Vyberá niekoľko kritických schopností, napríklad načítanie konfigurácie, spojenie s databázou, autentizovaný request a jednu bezpečnú business operáciu. Jeho úlohou je rýchlo zastaviť očividne chybný deployment skôr, než sa spustí drahšia suite alebo zvýši traffic.

Dobré smoke kritérium je viazané na konkrétny environment a release subject. Process `Running` alebo health endpoint `200` nestačí, ak používateľský request prechádza cez inú route, identity policy alebo dependency. Smoke preto kombinuje technický read-back s úzkym business synthetikom. Výsledok hovorí, že vybrané kritické cesty fungovali v danom okamihu; nehovorí, že všetky funkcie a okrajové prípady sú bez defectu.

Regression testing chráni už podporované správanie pred neúmyselnou zmenou. Portfólio nevzniká tak, že pri každom incidente pridáme iba ďalší pomalý end-to-end test. Najprv sa identifikuje uniknutý failure mode a najnižšia vrstva, kde ho možno spoľahlivo zachytiť. Incident s chybným roundingom potrebuje unit alebo property test, zmena SQL constraintu integration test a chýbajúca production route vyšší smoke alebo synthetic test.

Regression suite sa vyberá podľa affected graphu a rizika, ale required controls nesmú byť preskočené iba preto, že diff vyzerá malý. Zmena dependency, schema, build image alebo konfigurácie môže ovplyvniť nezmenené moduly. Selection logic preto musí byť versionovaná a jej rozhodnutie patrí do evidence.

Smoke a regression sa môžu prekrývať v konkrétnom scenári, no majú odlišný účel. Smoke rozhoduje, či má candidate pokračovať do ďalšej fázy. Regression rozhoduje, či zmena zachovala podporované správanie. Zelený smoke preto nesmie byť prezentovaný ako úplný regresný verdikt.

''',
    "docs/04-testing-and-quality/performance-load-stress-tests.md": r'''## Ako čítať workload, percentily a saturation

Performance test je kontrolovaný experiment, nie iba veľký počet requestov. **Latency** meria čas jednej operácie medzi presne zvoleným začiatkom a koncom. **Throughput** vyjadruje počet dokončených operácií za čas, zatiaľ čo **concurrency** opisuje rozpracované operácie. **Saturation** nastáva vtedy, keď práca čaká na resource, queue alebo limit. Tieto hodnoty sa musia čítať spolu: throughput môže vyzerať stabilne aj v čase, keď backlog rastie a používatelia čakajú čoraz dlhšie.

Percentile `p95` je hodnota, pod ktorou skončilo približne 95 percent nameraných latencies. Neznamená priemer ani maximálnu dobu. Jeho význam závisí od sample countu, operation type, result class a histogramu. Ak sa do jednej distribúcie zmiešajú rýchle errors so successful requests, p95 sa môže zlepšiť práve preto, že systém zlyháva rýchlejšie. Preto sa latency reportuje pre samostatné operácie a výsledkové triedy.

Workload model určuje, akú realitu experiment simuluje. Open model plánuje arrivals nezávisle od response time; closed model používa pevný počet users, ktorí čakajú na odpoveď. Keď closed generator pri spomalení odošle menej requestov, vzniká coordinated omission: práca, ktorá by v produkcii prišla a čakala, sa vôbec nezmeria. Pre verejné API je preto často vhodnejší arrival-rate model.

```javascript
export const options = {
  scenarios: {
    orders: {
      executor: 'constant-arrival-rate',
      rate: 100,
      timeUnit: '1s',
      duration: '10m',
      preAllocatedVUs: 50,
      maxVUs: 300,
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<400'],
  },
};
```

Konfigurácia žiada od k6 začínať sto iterations za sekundu. Virtuálni users sú workers, ktorých generator potrebuje na udržanie tohto tempa. Ak `maxVUs` nestačí, test nedodá plánovaný workload a výsledok nemožno interpretovať ako limit servera. Threshold `p(95)<400` je oracle nad konkrétnou metrikou; bez tags môže miešať rôzne endpointy a payloady.

Client metrics sa pri diagnóze spájajú s queue depth, pool waitom, CPU throttlingom, lockmi, I/O, broker lagom a downstream quotas. Prvý rastúci wait signal často odhalí bottleneck skôr než utilization dosiahne sto percent. Experiment sa uzatvára až po ramp-down a recovery: backlog sa musí vyprázdniť, retries skončiť a delayed side effects sa musia reconciliovať. Prežitie peak-u bez návratu do stabilného stavu nie je úspešný performance verdikt.

''',
    "docs/04-testing-and-quality/security-and-infrastructure-tests.md": r'''## Ako spojiť threat, control a security evidence

Security test začína hrozbou a chráneným assetom. Bez threat modelu sa suite ľahko zmení na zoznam scannerov, ktorých nálezy nemajú jasný vzťah k reálnemu riziku. Tím najprv pomenuje, kto môže útočiť, akú identity alebo network pozíciu má, čo sa snaží získať a ktorý design control má útoku zabrániť alebo ho odhaliť.

Kontrola potom overuje konkrétny control. Authorization test napríklad nevykoná iba povolený request; skúsi aj cross-tenant identity, chýbajúci scope a priamy prístup na nižšiu route. Pozitívny scenár dokazuje, že legitímna cesta funguje. Negatívny alebo forbidden scenár dokazuje, že ochranná hranica odmieta nežiaduce správanie. Obe časti sú potrebné, pretože policy, ktorá všetko blokuje, je bezpečnostne nepoužiteľná, a policy, ktorá pustí všetko, môže mať zelený happy-path test.

Infrastructure testy musia rozlišovať deklaráciu, plán, apply a runtime. Policy nad Terraform planom môže potvrdiť, že plánovaný security group neobsahuje `0.0.0.0/0`, ale nepreukazuje, že apply prebehol, že iný writer pravidlo nezmenil alebo že packet path neobchádza kontrolu. Runtime probe a cloud read-back preto dopĺňajú source-level evidence.

Scanner result je signál, nie automatický verdikt. SAST, dependency scan, image scan alebo IaC policy majú vlastný model, databázu pravidiel a limity. Finding potrebuje exact artifact, rule generation, severity policy a triage. Suppression musí mať dôvod, ownera a expiry, inak sa z nej stane trvalá diera v dôkaznom reťazci.

Bezpečnostný test musí byť bezpečný aj prevádzkovo. Aktívne DAST alebo permission testy používajú sandbox identity, bounded rate, allowlisted target a cleanup. Výsledok sa uzatvára nielen nálezom, ale authoritative opravou, opakovaným forbidden testom a potvrdením, že legitímny flow zostal funkčný.

''',
    "docs/04-testing-and-quality/static-analysis-linting-type-checking.md": r'''## Ako interpretovať statický nález

Statická analýza skúma source alebo odvodený model bez vykonania cieľového systému. Parser najprv vytvorí syntax tree, symbol table alebo intermediate representation. Nad týmto modelom linter, type checker alebo security analyzer aplikuje pravidlá. Nález teda nie je priamym pozorovaním runtime chyby; je výsledkom modelu a rule generation, ktoré treba poznať pri interpretácii.

Formatter rieši deterministickú reprezentáciu textu. Linter hľadá syntax, style a vybrané correctness patterns. Type checker overuje, či operácie zodpovedajú deklarovanému alebo inferovanému type modelu. SAST sa pokúša sledovať data flow, taint alebo nebezpečné API. Tieto nástroje sa môžu prekrývať, ale každý poskytuje inú hranicu dôkazu.

Nález má exact location, rule ID, tool version a severity. `PASS` znamená, že daná konfigurácia nástroja nenašla podporovaný pattern v analyzovanom scope. Neznamená to, že kód je bez runtime defectov alebo zraniteľností. Naopak finding nemusí byť exploitable; môže byť false positive, neaktívna path alebo bezpečne obalené API. Triage musí vyhodnotiť reálny data/control flow.

Suppressions sú súčasťou source contractu. Inline ignore bez vysvetlenia môže zneviditeľniť budúcu zmenu. Bezpečná suppression je čo najužšia, odkazuje na dôvod, má ownera a podľa rizika expiry. Pri upgrade toolu sa baseline znovu vyhodnotí, pretože pravidlá a parser semantics sa môžu zmeniť bez zmeny aplikačného kódu.

Statické kontroly dávajú rýchly feedback a patria skoro do workflowu, ale musia byť doplnené dynamickými testami. Type-safe HTTP client stále môže volať nesprávny endpoint; validný manifest stále môže byť v runtime odmietnutý admission policy alebo načítať chybnú configuration generation.

''',
    "docs/04-testing-and-quality/code-coverage-and-quality-gates.md": r'''## Ako čítať coverage a quality gate

Coverage opisuje, ktoré programové prvky test počas vykonania navštívil. Line coverage používa ako denominator merateľné riadky, branch coverage jednotlivé výsledky rozhodnutí a function coverage volateľné funkcie. Percento bez uvedenia denominatoru, scope-u, exclusions a source revision je neúplné. Rovnakých osemdesiat percent môže znamenať veľmi odlišný dôkaz podľa toho, či chýbajú generated getters alebo authorization branches.

Vykonanie riadku neznamená, že test overil jeho význam. Test môže prejsť cez chybnú vetvu bez assertion alebo iba skontrolovať, že process nespadol. Coverage je preto mapa pozorovaných a nepozorovaných častí, nie dôkaz correctness. Chýbajúca branch coverage pomáha nájsť slabé miesto; prítomná coverage nenahrádza oracle.

Mutation testing skúša silu oraclu tým, že nástroj vytvorí malú semantic zmenu, napríklad nahradí `>` za `>=` alebo odstráni authorization condition. Ak suite zlyhá, mutant bol „killed“ a testy zmenu rozpoznali. Preživší mutant môže ukazovať chýbajúci scenár alebo slabú assertion, ale môže byť aj semanticky ekvivalentný, preto výsledok potrebuje triage.

Quality gate kombinuje viac evidence a aplikuje versionovanú policy. Môže vyhodnotiť test results, blocking findings, diff coverage, mutation score a povinné kritické scenáre. Gate musí rozlišovať `FAIL`, keď subject porušil kontrolu, `ERROR`, keď kontrola nevedela korektne bežať, a `MISSING`, keď evidence nebola dodaná. Fail-open preklad chýbajúceho reportu na success ničí dôveryhodnosť required controlu.

Dobrá policy nezaobchádza so všetkým kódom rovnako. Authorization, money, destructive automation a recovery potrebujú explicitné scenáre nezávisle od globálneho percenta. Differential gate chráni nový diff, zatiaľ čo absolute gate sleduje celý repository; oba musia používať správny merge base a complete report z relevantných shardov.

''',
    "docs/04-testing-and-quality/mocks-stubs-fakes.md": r'''## Ako vybrať test double bez skreslenia testu

Test double nahrádza dependency, ktorú daný test nechce alebo nemôže použiť priamo. **Stub** vracia vopred pripravené odpovede a pomáha dostať subject do zvoleného scenára. **Fake** implementuje zjednodušenú, ale funkčnú verziu rozhrania, napríklad in-memory repository. **Mock** overuje očakávanú interakciu, teda či bolo volanie vykonané s konkrétnymi argumentmi a poradím. **Spy** zaznamenáva skutočné volania a umožňuje ich neskoršie assertions. Dummy hodnota iba vypĺňa parameter, ktorý scenár nepoužíva.

Voľba double-u musí zodpovedať otázke testu. Ak testujeme výsledný state workflowu, príliš presný mock call order môže zviazať test s implementačným detailom a rozbiť sa pri bezpečnom refaktoringu. Ak je však contractom presne jedno odoslanie payment requestu s rovnakým idempotency key, interaction assertion je súčasťou business correctness.

Fake musí modelovať tie semantics, na ktorých rozhodnutie závisí. In-memory map nedokáže zastúpiť SQL isolation, unique constraint alebo transaction rollback. Ak test prejde iba preto, že fake toleruje správanie, ktoré produkčná dependency odmietne, vzniká false confidence. Preto sa doubles dopĺňajú contract a integration testami proti reálnej technológii.

Programovateľný fake je užitočný pre timeouty a retries, pretože vie simulovať success, transient error, unknown outcome aj oneskorenú odpoveď. Test potom overí nielen počet calls, ale final state, použitú operation identity a reconciliation. Double nemá iba „vrátiť error“; má reprezentovať failure boundary, ktorú produkčný systém musí zvládnuť.

Čím viac správania fake obsahuje, tým väčšie je riziko driftu. Interface verzia, shared contract tests a pravidelné integration runs chránia pred tým, aby testovacia náhrada opisovala iný systém než produkčná dependency.

''',
    "docs/04-testing-and-quality/flaky-tests-and-test-data.md": r'''## Ako rozlíšiť flaky test od skutočného defectu

Flaky test vracia odlišný verdikt nad rovnakým deklarovaným subjectom bez relevantnej zmeny vstupov. Príčina však nemusí byť iba v teste. Nedeterministické môže byť aj produkčné správanie, race condition, eventual consistency alebo resource pressure. Automatický retry, ktorý druhý pokus označí za success, zničí first-attempt evidence a môže skryť skutočný defect.

Vyšetrovanie začína exact identitou runu: source revision, artifact, environment, seed, time, test data, dependency versions a worker. Prvý neúspešný pokus sa zachová spolu s logs, trace, screenshotom a state read-backom. Až potom možno porovnávať opakované behy a hľadať meniacu sa premennú.

Častým zdrojom flakiness je čas. Test, ktorý čaká pevné dve sekundy, predpokladá scheduler a dependency latency. Lepší test čaká na explicitnú podmienku s deadline a pri timeout-e vypíše posledný observed state. Hodiny sa pri domain logike injektujú; integračný test zaznamená timezone a clock source.

Test data potrebuje unikátnu identity a lifecycle. Zdieľaný tenant, globálny feature flag alebo opakovane používaný order ID vytvára interference medzi paralelnými runmi. Setup má byť idempotentný alebo vytvoriť nový izolovaný subject; cleanup nesmie zmazať evidence skôr, než sa failure klasifikuje. Pri produkčných synthetics sa používajú jasne označené účty a bezpečné business operácie.

Quarantine môže dočasne zabrániť blokovaniu delivery, ale nie je opravou. Musí mať ownera, deadline a viditeľný stav. Required security alebo data-integrity control sa nemá jednoducho vypnúť; pipeline môže oddeliť `TEST_DEFECT`, `PRODUCT_DEFECT` a `ENVIRONMENT_ERROR`, no každý stav potrebuje reakciu a návrat do dôveryhodného gate-u.

''',
    "docs/04-testing-and-quality/shift-left.md": r'''## Ako presunúť feedback skôr bez straty fidelity

Shift-left znamená posunúť vhodný dôkaz bližšie k vzniku rozhodnutia. Neznamená presunúť všetky produkčné testy na laptop ani očakávať, že statická analýza nahradí runtime. Cieľom je odhaliť defect v najskoršom bode, kde už existuje dostatočný model jeho príčiny.

Design review môže zachytiť chýbajúcu idempotency boundary ešte pred kódom. Schema validation a type checking odhalia nekompatibilný tvar dát pred spustením služby. Unit a component testy dávajú rýchlu spätnú väzbu o logike, contract tests o rozhraní a policy-as-code o plánovanej infraštruktúre. Každá kontrola však zostáva viazaná na svoju fidelity; validný Terraform plan nepreukazuje applied cloud state a mockovaný API test nepreukazuje reálnu TLS alebo authorization cestu.

Shift-left je účinný, keď testovateľnosť vzniká v designe. Explicitné interfaces, deterministické functions, injectable clock, local emulators a versionované schemas znižujú cenu skorých testov. Ak architektúra skrýva state v globálnych singletons alebo vyžaduje celý cluster pre každú business rule, problémom nie je iba chýbajúci test, ale slabá testovateľnosť systému.

Defect zistený neskoro sa používa na zlepšenie skoršieho controlu. Produkčný incident môže viesť k novému invariant testu, contractu alebo policy. Nemá však automaticky zrušiť vyšší runtime dôkaz, pretože rovnaký failure mode môže závisieť od konfigurácie alebo interakcie, ktorú skorý model nevie vidieť.

Kvalitný shift-left preto optimalizuje čas do diskriminačného dôkazu, nie iba počet kontrol pred mergeom. Rýchly, hlučný scanner bez ownera môže spomaliť feedback viac než menší súbor presných kontrol.

''',
    "docs/04-testing-and-quality/shift-right.md": r'''## Ako získavať produkčný dôkaz bezpečne

Shift-right používa runtime a produkčné prostredie na otázky, ktoré pre-production model nedokáže úplne zodpovedať. Reálny traffic, topology, identity, data distribution a dependencies odhaľujú failure modes, ktoré sa v stagingu nemusia objaviť. Nejde však o ospravedlnenie chýbajúcich testov; ide o riadené doplnenie evidence po deploymente.

Synthetics vykonávajú známu bezpečnú operáciu a poskytujú stabilný oracle. Canary porovnáva obmedzenú cohortu novej generation so stable baseline. Shadow traffic posiela kópiu requestu kandidátovi bez autoritatívneho side effectu. Observability a business reconciliation sledujú final outcomes. Každá technika má iný subject a nemá sa zamieňať so všeobecným „monitorovaním“.

Produkčný experiment potrebuje blast radius, allowlisted target, identity, privacy policy a abort criteria. Test data sa musí dať odlíšiť od používateľských dát a nesmie spúšťať nevratné externé operácie bez explicitného contractu. No-data alebo pokazená telemetry cesta nie je success; je to `MISSING` alebo `ERROR` verdict.

Runtime dôkaz sa viaže na release, configuration, region, cohort a časové okno. Globálny dashboard môže skryť problém jedného tenanta alebo AZ. Request a operation IDs musia umožniť prepojiť ingress, application state, eventy a downstream side effects. Pri asynchrónnom workflowe sa analysis window nekončí pri rýchlej HTTP odpovedi, ale pri terminal business outcome-e.

Shift-right kontrola sa uzatvára containmentom a recovery. Ak canary zlyhá, treba zastaviť novú expozíciu, zachovať evidence a reconciliovať in-flight operations. Samotný návrat route weightu na nulu nepreukazuje, že pending alebo unknown side effects boli vyriešené.

''',
    "docs/04-testing-and-quality/chaos-testing.md": r'''## Ako zostaviť riadený chaos experiment

Chaos testing je riadený experiment nad odolnosťou systému, nie náhodné vypínanie komponentov. Začína hypotézou o pozorovateľnom outcome-e. Napríklad: ak zanikne jedna z troch API replík, úspešnosť idempotentných objednávok zostane nad 99,9 percenta a p95 final completion latency pod 800 ms. Takáto hypotéza pomenúva fault aj používateľský oracle.

Pred experimentom sa overí **steady state**, teda merateľný normálny stav. Nestačí veta „služba je zdravá“. Baseline môže obsahovať success rate, queue depth, reconciliation lag a business invariant. Ak baseline neplatí už pred faultom, experiment nevie oddeliť existujúci problém od vyvolaného efektu.

Fault injection musí mať exact target, trvanie a blast radius. Príkaz:

```bash
kubectl delete pod payments-api-abc123 -n payments
```

preukazuje prijatie delete requestu na konkrétny objekt. Nepreukazuje, že Pod zanikol, že controller vytvoril náhradu, EndpointSlice odstránil starý endpoint alebo že traffic zostal úspešný. Read-back preto sleduje workload convergence, dataplane a syntetickú business operáciu.

Abort criteria chránia systém pri neočakávanom rozšírení dopadu. Fault automation musí mať nezávislú stop cestu a nesmie závisieť iba od služby, ktorú poškodzuje. Experiment sa zastaví napríklad pri strate druhej AZ, prekročení queue limitu alebo zlyhaní observability.

Odstránenie faultu nie je koniec. Recovery fáza overí backlog drain, ukončenie retry stormu, resource release, reconciliáciu unknown outcomes a návrat business invariantov. Ak requests počas faultu uspeli, ale backlog po obnove nekontrolovane rastie, experiment odhalil latentný recovery failure a nemôže byť označený za úspešný.

''',
}
