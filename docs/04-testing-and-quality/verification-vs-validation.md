# Verification vs. validation

Verification a validation sú dve odlišné otázky kvality. **Verification** skúma, či systém alebo artefakt zodpovedá špecifikácii, designu alebo explicitnému contractu. **Validation** skúma, či výsledný systém rieši správny používateľský alebo business problém v reálnom kontexte.

Zjednodušene:

```text
verification:
Postavili sme systém správne podľa definovaných pravidiel?

validation:
Postavili sme správny systém pre skutočnú potrebu?
```

Verification môže overiť, že API vracia schema-valid JSON a používa správny status code. Validation môže zistiť, že používateľ napriek tomu nedokáže dokončiť objednávku alebo že workflow rieši nesprávny problém.

Každý test potrebuje **oracle**: pravidlo alebo zdroj pravdy, podľa ktorého sa rozhodne pass/fail. Oracle môže byť presná hodnota, invariant, schema, referenčný model, business rule, user acceptance criterion alebo pozorovaný production baseline. Slabý oracle môže vytvárať false positives alebo false negatives aj pri technicky správnom test runneri.

Traceability spája:

```text
požiadavka alebo riziko
→ očakávané správanie
→ test subject a scope
→ oracle
→ evidence
→ rozhodnutie
```

Bez tejto väzby môže suite obsahovať veľa testov, ale nepokrývať najdôležitejšie riziko.

Neutrálny príklad: kalkulačka má requirement, že delenie nulou musí vrátiť definovanú chybu. Unit test, ktorý overí konkrétny error type, je verification. Používateľské testovanie môže odhaliť, že text chyby je pre cieľovú skupinu nezrozumiteľný; to je validation.

Verification ani validation nie sú jednorazové fázy na konci projektu. Prebiehajú na rôznych úrovniach od requirements reviewu cez static checks a tests až po produkčné business outcomes. Dôkaz musí vždy pomenovať, pre ktorý subject, verziu, prostredie a čas platí.

## 1. Dve rozdielne otázky o kvalite

Verification a validation odpovedajú na dve rozdielne otázky:

```text
Verification: Vytvorili sme systém správne podľa definovaného kontraktu?
Validation:   Vytvorili sme správny systém pre reálnu potrebu a kontext?
```

Verification porovnáva pozorovaný stav s explicitným očakávaním, napríklad so špecifikáciou, schémou, politikou alebo invariantom. Validation posudzuje, či výsledok prináša zamýšľanú používateľskú, prevádzkovú alebo obchodnú hodnotu v prostredí, kde sa systém skutočne používa.

Obe disciplíny sú potrebné. Systém môže presne implementovať nesprávnu požiadavku alebo môže riešiť správny problém spôsobom, ktorý porušuje bezpečnostný, dátový alebo prevádzkový kontrakt.

## 2. Mentálny model: potreba, kontrakt, dôkaz a rozhodnutie

Kvalitná kontrola nezačína výberom test frameworku. Začína pomenovaním toho, aké rozhodnutie má výsledok podporiť a aký dôkaz je na toto rozhodnutie dostatočný.

```text
potreba alebo riziko
  ↓
explicitný kontrakt a očakávaný výsledok
  ↓
kontrola alebo experiment
  ↓
pozorovanie a test oracle
  ↓
dôkaz s obmedzeniami
  ↓
rozhodnutie: prijať, blokovať, opraviť, monitorovať alebo experimentovať
```

Verification sa sústreďuje najmä na väzbu medzi kontraktom a pozorovaním. Validation sa sústreďuje najmä na väzbu medzi potrebou a reálnym výsledkom. V praxi sa ich dôkazy prekrývajú a jeden test môže podporovať obe otázky, ale nikdy nie automaticky.

## 3. Verification: správnosť voči explicitnému kontraktu

Verification vyžaduje referenciu, voči ktorej sa výsledok porovnáva. Referenciou môže byť požiadavka, API kontrakt, invariant, bezpečnostná policy, dátová schéma, architektonické rozhodnutie alebo presný akceptačný príklad.

Príklady verification:

- unit test — overí, že čistá funkcia pre definovaný vstup vracia očakávaný výstup a zachováva invarianty;
- schema validation — overí, že JSON alebo YAML má povolenú štruktúru, typy a povinné polia;
- contract test — overí, že producer a consumer interpretujú rozhranie kompatibilne;
- policy-as-code — overí, že plánovaná infraštruktúra neporušuje pravidlá pre public access, encryption alebo identity;
- deployment smoke test — overí, že nasadená verzia odpovedá cez reálnu routing, TLS a runtime cestu;
- restore procedure check — overí, že runbook obsahuje potrebné kroky, oprávnenia a nástroje.

Verification môže byť statická alebo dynamická. Rozhodujúce nie je, či sa systém spustí, ale či existuje explicitné očakávanie a reprodukovateľný spôsob jeho porovnania s výsledkom.

## 4. Validation: užitočnosť v reálnom kontexte

Validation skúma, či systém rieši zamýšľaný problém pre používateľov a prevádzku. Potrebuje preto reprezentatívny kontext, realistické správanie a metriky, ktoré opisujú výsledok, nie iba internú aktivitu systému.

Príklady validation:

- používateľská cesta — používateľ dokáže dokončiť objednávku správne, zrozumiteľne a bez neprimeraného času;
- operability — alert vedie službukonajúceho operátora ku konkrétnej diagnóze a akcii, nie iba k ďalšiemu dashboardu;
- kapacita — autoscaling udrží požadovanú tail latency pri realistickom profile trafficu a závislostí;
- recovery — po regionálnom alebo dátovom zlyhaní sa služba obnoví v rámci deklarovaného RTO a stratí najviac dáta povolené RPO;
- delivery improvement — automatizovaný workflow skutočne zníži lead time alebo chybovosť, nie iba presunie manuálnu prácu do iného tímu;
- business outcome — nová funkcionalita zlepší zamýšľanú mieru úspešného dokončenia bez neprijateľného nárastu fraudu alebo support kontaktov.

Validation môže používať automatizované acceptance testy, ale často potrebuje aj synthetics, reálnu telemetriu, používateľský výskum, canary rollout, experiment, game day alebo pravidelný restore test. Test environment je model reality, nie jej úplná náhrada.

## 5. Prečo sa pojmy zamieňajú

V bežnej technickej reči sa slovo „validation“ často používa pre syntaktickú alebo vstupnú kontrolu, napríklad JSON Schema validation. Z pohľadu tejto kapitoly ide prevažne o verification voči schéme, pretože otázka znie, či dáta spĺňajú explicitný formálny kontrakt.

Namiesto sporu o terminológiu vždy pomenuj tri veci:

```text
Čo je objekt kontroly?
Voči akej referencii ho porovnávame?
Aké rozhodnutie má výsledok podporiť?
```

Takto sa odlíši kontrola správneho formátu od dôkazu, že formátované dáta vedú k správnemu používateľskému alebo prevádzkovému výsledku.

## 6. Statická verification

Statická verification nevyžaduje vykonanie cieľového systému. Analyzuje source, konfiguráciu, typy, dependency graph alebo plánovaný desired state a môže preto poskytovať veľmi rýchly feedback.

Typické kontroly:

- compiler a type checker — odhaľujú porušenie jazykových a typových kontraktov pred runtime;
- linter a formatter check — presadzujú vybrané pravidlá čitateľnosti, correctness patternov a konzistencie;
- schema a policy validation — overujú tvar dát a povolené vlastnosti konfigurácie alebo infraštruktúrneho plánu;
- SAST, secret scanning a dependency analysis — hľadajú známe rizikové patterny, credentials alebo zraniteľné komponenty;
- code review — posudzuje zmenu, jej zámer, hranice a dôsledky, ktoré automatický nástroj nemusí modelovať.

Statická kontrola nepozoruje reálnu runtime interakciu. Môže potvrdiť, že manifest deklaruje readiness probe, ale nie že probe správne reprezentuje schopnosť aplikácie obslúžiť používateľský request.

## 7. Dynamická verification

Dynamická verification vykonáva kód alebo systém a porovnáva jeho správanie s očakávaním. Je schopná zachytiť interakcie, runtime konfiguráciu, serializáciu, sieťové cesty a resource behavior, ktoré statický model nevidí.

Typické kontroly:

- unit a component tests — vykonávajú izolované správanie alebo väčší komponent s kontrolovanými hranicami;
- integration a contract tests — overujú spoluprácu s databázou, brokerom, API alebo iným procesom;
- E2E a acceptance tests — overujú kritickú cestu cez viac vrstiev systému;
- performance a resilience tests — overujú správanie pri konkrétnom workloade, tlaku alebo zlyhaní;
- runtime security tests — skúšajú authorization, input boundaries alebo reálnu sieťovú a identity policy.

Dynamický test je iba taký silný, ako jeho setup, reprezentatívnosť vstupu a oracle. Test, ktorý spustí veľa kódu, ale kontroluje iba návratový status, môže mať nižšiu dôkaznú hodnotu než malý test so silnými invariantmi.

## 8. Requirement a risk traceability

Traceability prepája potrebu a riziko s konkrétnym dôkazom. Jej cieľom nie je vytvoriť administratívnu tabuľku pre každý riadok kódu, ale zabrániť tomu, aby kritické riziko zostalo bez kontroly alebo aby test suite rástla bez jasného účelu.

```text
business alebo prevádzková potreba
  ↓
merateľná požiadavka
  ↓
failure mode a dopad
  ↓
design control
  ↓
verification a validation dôkazy
  ↓
owner a reakcia na failure
```

Príklad pre multi-tenant API:

```text
Potreba: tenant vidí iba vlastné dáta.
Failure mode: cross-tenant data exposure.
Design controls: tenant-scoped query, authorization policy, audit event.
Verification: policy unit tests, DB integration tests, API negative tests.
Validation: produkčná audit analýza, synthetic cross-tenant probe, incident drill.
```

Jedno riziko môže potrebovať viac vrstiev dôkazu. Unit test potvrdí logiku policy, ale nepreukáže, že všetky runtime cesty policy skutočne používajú.

## 9. Test oracle

Test oracle je mechanizmus, ktorý rozhoduje, či pozorovaný výsledok zodpovedá očakávaniu. Bez oraclu test iba vykonáva aktivitu a jeho zelený status nemusí znamenať nič podstatné.

Oraclom môže byť:

- presná hodnota — vhodná pre deterministický výpočet alebo serializáciu;
- invariant — vlastnosť, ktorá musí platiť pre širšiu množinu vstupov, napríklad zachovanie celkovej sumy;
- schéma alebo contract — definuje povolený tvar, typy a semantics rozhrania;
- referenčná implementácia — porovná výsledok s dôveryhodným, hoci možno pomalším modelom;
- model alebo property — generuje vstupy a overuje všeobecné pravidlo;
- business rule — posudzuje význam výsledku, napríklad správnu cenu, oprávnenie alebo stav objednávky;
- SLI threshold — určuje, či reálne správanie spĺňa prevádzkovú úroveň.

Slabý oracle overí iba, že request vrátil HTTP `200`. Silnejší oracle overí schému, business hodnoty, presný počet side effects, authorization boundary, audit event a stav po opakovaní requestu.

## 10. Oracle problem a neistota

Pri niektorých systémoch nie je presný správny výstup vopred známy. Platí to napríklad pri distribuovaných workflowoch, optimalizácii, strojovom učení alebo komplexnom recovery procese.

Vtedy sa používajú kombinované oracles:

- metamorphic relations — zmena vstupu musí viesť k predvídateľnej zmene vlastnosti výsledku;
- invariants — výsledok musí zachovať bezpečnostné, finančné alebo konzistenčné pravidlá;
- differential testing — viac implementácií alebo verzií sa porovná na rovnakých vstupoch;
- statistical bounds — výsledok sa hodnotí podľa intervalov, distribúcie a opakovateľnosti;
- human review — expert posudzuje prípady, ktoré nemožno dostatočne formalizovať.

Takýto dôkaz má explicitne uviesť neistotu a toleranciu. Arbitrárny threshold bez odôvodnenia iba skryje nejasný oracle do čísla.

## 11. False positive a false negative

False positive znamená, že kontrola hlási chybu, hoci posudzovaný systém je správny voči zamýšľanému kontraktu. Časté false positives blokujú delivery, podporujú rerun-until-green správanie a znižujú dôveru v celú suite.

False negative znamená, že kontrola prejde napriek relevantnej chybe. Je nebezpečnejší pri bezpečnosti, dátovej integrite a finančných operáciách, pretože poskytuje formálny zelený signál bez reálneho pokrytia rizika.

Trade-off závisí od dopadu:

- pre formatter check môže byť primerané preferovať citlivosť a opravu automatizovať;
- pre produkčný deployment gate musí byť false-positive rate nízka, pretože blokovanie má vysokú cenu;
- pre kritickú authorization kontrolu je potrebné minimalizovať false negatives, aj za cenu širšieho testovania;
- pre advisory scanner možno tolerovať viac kandidátov, pokiaľ existuje efektívna triage a suppression lifecycle.

Kvalita kontroly sa preto neposudzuje iba podľa počtu nálezov. Sleduje sa presnosť, stabilita, čas feedbacku, diagnostikovateľnosť a schopnosť zachytiť skutočný failure mode.

## 12. Dôkazná sila a scope

Dôkaz je platný iba pre podmienky, v ktorých vznikol. Unit test s in-memory fake databázou je silný dôkaz aplikačnej logiky, ale slabý dôkaz kompatibility s reálnym SQL dialektom, isolation levelom alebo migration stateom.

Pri každom výsledku pomenuj:

- scope — ktoré komponenty, vrstvy a cesty boli skutočne vykonané;
- environment — aké verzie, konfigurácia, dáta a dependencies boli použité;
- oracle — čo presne rozhodlo o úspechu;
- representativeness — ako sa workload a vstupy podobajú realite;
- blind spots — ktoré failure modes kontrola vedome nepokrýva;
- freshness — ku ktorému commitu, artifactu a deploymentu sa dôkaz viaže.

Zelený test z iného commitu alebo z iného artifactu nie je dôkazom pre aktuálny deployment. Provenance testovaného a nasadeného obsahu musí byť dohľadateľná.

## 13. Environment fidelity

Vyššia fidelity znamená, že test environment sa viac podobá cieľovému runtime, nie automaticky že test je lepší. Fidelity zvyšuje schopnosť odhaliť integračné a konfiguračné chyby, ale prináša vyššiu cenu, pomalší feedback a viac zdrojov nestability.

Rozumné vrstvenie:

```text
lokálne a hermetické kontroly
→ CI s reálnymi procesmi a ephemeral dependencies
→ staging s produkčne podobnou topológiou
→ canary alebo shadow traffic
→ produkčné SLI, business metrics a user feedback
```

Každá vrstva má zachytiť riziká, ktoré lacnejšia vrstva nevie spoľahlivo modelovať. Nie je efektívne presúvať jednoduchú input validáciu do drahého E2E testu ani predstierať, že hermetický unit test overil cloud IAM policy.

## 14. Verification a validation počas delivery lifecycle

Kontroly sa rozmiestňujú podľa času feedbacku a fidelity:

| Fáza | Typický dôkaz | Hlavná otázka |
|---|---|---|
| editor/pre-commit | formatter, lint, type check, unit test | Je lokálna zmena konzistentná so základnými pravidlami? |
| pull request CI | build, integration, contract, security checks | Je kandidát technicky integrovateľný a bezpečný? |
| pre-release | E2E, acceptance, migration, performance baseline | Spĺňa artifact release kontrakt v reprezentatívnom prostredí? |
| deployment | readiness, smoke, synthetic transaction | Je nová verzia dostupná cez reálnu runtime cestu? |
| canary/progressive rollout | SLI, error rate, business guardrails | Správa sa nová verzia správne na reálnom trafficu? |
| stabilná produkcia | SLO, RUM, audit, user feedback, experiments | Prináša systém dlhodobo zamýšľaný výsledok? |

Validation sa nekončí pred deploymentom. Reálny traffic, používatelia, data distribution a dependency failure modes vytvárajú podmienky, ktoré staging nemusí presne reprodukovať.

## 15. Quality gate ako rozhodovací mechanizmus

Quality gate je automatizované alebo formálne rozhodnutie, ktoré môže zmenu zastaviť, povoliť alebo posunúť do manuálnej triage. Gate má byť naviazaný na konkrétne riziko, nie na metriku používanú iba preto, že ju nástroj poskytuje.

Blocking gate je primeraný, keď:

- failure signal je spoľahlivý a reprodukovateľný;
- kontrolované riziko má významný dopad;
- autor alebo owner vie z výstupu určiť ďalší krok;
- runtime a cena kontroly zodpovedajú miestu v pipeline;
- existuje auditovateľný exception proces s ownerom a expiráciou.

Advisory kontrola je vhodnejšia pri novom alebo noisy signále. Dáta sa môžu najprv zbierať, kalibrovať a až po dosiahnutí potrebnej presnosti zmeniť na blocking policy.

## 16. Príklad: API zmena

Predstavme si zmenu response poľa z `total` na `amount`.

Verification dôkazy:

1. schema test potvrdí nový tvar response;
2. consumer-driven contract overí, ktoré consumers stále vyžadujú `total`;
3. unit a integration testy overia mapovanie dát;
4. compatibility test potvrdí prechodné poskytovanie oboch polí;
5. deployment smoke test overí route, TLS a response reálneho artifactu.

Validation dôkazy:

1. telemetry ukáže, že consumers prešli na nové pole;
2. chybovosť a latency sa po canary nezhoršili;
3. business transakcie majú rovnaké finančné výsledky;
4. deprecated pole možno po dohodnutom období bezpečne odstrániť.

Samotný schema-green výsledok neodpovedá na otázku, či reálni consumers zostali funkční.

## 17. Príklad: Infrastructure as Code

Pre zmenu load balancera možno vykonať viac vrstiev kontroly.

Verification:

- parser a schema potvrdia syntakticky platný manifest;
- policy engine overí TLS, public exposure a povinné logovanie;
- plan review ukáže presné create/update/delete operácie;
- test deployment potvrdí, že provider API deklarovaný stav prijme.

Validation:

- povolený klient dosiahne službu cez očakávaný hostname;
- nepovolená sieťová cesta je reálne blokovaná;
- health check správne odoberie chybný backend;
- load balancer zvládne realistický traffic a failover;
- access logs a metriky umožnia incident diagnostiku.

Existencia správneho security group pravidla je verification konfigurácie. Reálny negatívny connectivity test je silnejší dôkaz účinnosti celej enforcement cesty.

## 18. Príklad: backup a disaster recovery

Backup job môže byť úspešne nakonfigurovaný a pravidelne vytvárať objekty. To ešte nepotvrdzuje, že objekty sú úplné, dešifrovateľné, dostupné správnemu recovery tímu a obnoviteľné v požadovanom čase.

Verification zahŕňa schedule, retention, encryption, permissions, success status a integritu backup artifactu. Validation vyžaduje restore do kontrolovaného prostredia, kontrolu aplikačnej konzistencie, meranie RPO/RTO a overenie, že služba po obnove vykoná kritickú používateľskú operáciu.

## 19. Failure modes slabej testovacej stratégie

### Contract bez reálnej potreby

Tím presne overuje implementáciu požiadavky, ktorá už nezodpovedá používateľskému alebo prevádzkovému problému. Testy zostávajú zelené, ale produkt vytvára nulovú alebo negatívnu hodnotu.

### Activity bez oraclu

Test spustí request, workflow alebo deployment, ale neoverí relevantný výsledok a side effects. Zelený status znamená iba to, že test framework nedostal neošetrenú chybu.

### Vysoká fidelity bez izolácie

Všetko sa testuje v jednom zdieľanom E2E prostredí. Výsledkom je pomalý feedback, konflikty test data, vysoká flakiness a nízka schopnosť lokalizovať príčinu.

### Coverage bez risk traceability

Tím maximalizuje percento vykonaných riadkov, ale kritické authorization, concurrency alebo recovery failure modes zostanú bez assertionu. Coverage opisuje vykonanie, nie dôkaz správnosti.

### Produkčné monitorovanie ako jediná ochrana

Incidenty, ktoré možno lacno zachytiť pred release, sa nechávajú na používateľov a alerty. Shift-right validation je doplnok pre realitu, nie náhrada základnej verification.

## 20. Diagnostika zlyhanej kontroly

Pri zlyhaní najprv nerozhoduj, že systém je chybný. Rozlíš štyri možnosti:

```text
produkt porušil kontrakt
kontrola alebo oracle je chybný
prostredie alebo test data sú nekonzistentné
kontrakt už nezodpovedá zamýšľanej potrebe
```

Evidence-first postup:

1. identifikuj commit, artifact, environment a presný čas kontroly;
2. zaznamenaj vstupy, fixture verzie a relevantnú konfiguráciu;
3. over, čo oracle skutočne meral a akú toleranciu použil;
4. zopakuj najmenší diskriminačný test v izolovanom prostredí;
5. porovnaj zdravý a chybný prípad s jednou menenou premennou;
6. skontroluj, či failure reprodukuje používateľský alebo prevádzkový dopad;
7. oprav produkt, test, fixture alebo kontrakt podľa získaného dôkazu;
8. uchovaj diagnostické artifacts a over first-attempt pass po náprave.

Rerun bez analýzy môže zmeniť červený signál na zelený bez odstránenia príčiny.

## 21. Praktický návrhový workflow

Pre každú významnú zmenu:

1. pomenuj používateľský alebo prevádzkový výsledok;
2. definuj explicitné kontrakty a zakázané stavy;
3. identifikuj failure modes, dopad a pravdepodobnosť;
4. zvoľ najnižší scope, ktorý failure mode spoľahlivo odhalí;
5. definuj setup, vstup, oracle, cleanup a failure artifacts;
6. rozhodni, kde sa kontrola spustí a aký má mať čas feedbacku;
7. urč, či výsledok blokuje, varuje alebo iba zbiera baseline;
8. prepoj dôkaz s commitom, artifactom a environmentom;
9. doplň produkčnú validation pre riziká závislé od reality;
10. pravidelne odstráň redundantné, flaky alebo bezúčelné kontroly.

## 22. Kontrolný checklist

Pred označením kontroly za dôveryhodnú over:

- kontrolované riziko je explicitne pomenované;
- očakávaný výsledok je merateľný;
- oracle overuje význam, nie iba úspešné vykonanie;
- setup a test data sú deterministické alebo je neistota modelovaná;
- failure výstup umožní lokalizovať problém;
- scope a blind spots sú zdokumentované;
- dôkaz sa viaže na konkrétny commit a artifact;
- false-positive a false-negative náklady sú primerane vyvážené;
- kontrola má ownera a jasnú reakciu na failure;
- produkčné validation signály dopĺňajú predprodukčné testy.

## 23. Časté omyly

### „Verification je iba unit testing“

Nie. Zahŕňa akúkoľvek kontrolu voči explicitnému kontraktu, od compileru cez policy-as-code až po runtime recovery invariant.

### „Validation sa nedá automatizovať“

Dá sa čiastočne automatizovať pomocou acceptance tests, synthetics, SLI a experimentov. Stále však musí reprezentovať reálnu potrebu a nemôže sa zredukovať na internú technickú metriku.

### „HTTP 200 je dôkaz správnosti“

Nie. Potvrdzuje iba úspešný HTTP status podľa servera; neoveruje business výsledok, authorization, side effects, dátovú konzistenciu ani skúsenosť používateľa.

### „Keď test zlyhal, produkt je chybný“

Nie automaticky. Chybný môže byť produkt, oracle, fixture, prostredie alebo samotný kontrakt.

### „Keď všetky testy prešli, release je bezpečný“

Testy poskytujú dôkaz v konkrétnom scope a prostredí. Reziduálne riziko, neznáme kombinácie a produkčné podmienky zostávajú, preto sú potrebné observability a bezpečný rollout.

## 24. Kontrolné otázky

1. Aký je rozdiel medzi verification a validation?
2. Aké štyri prvky obsahuje model potreba → kontrakt → dôkaz → rozhodnutie?
3. Prečo je JSON Schema validation prevažne verification?
4. Aký je rozdiel medzi statickou a dynamickou verification?
5. Čo je test oracle a prečo je HTTP `200` slabý oracle?
6. Ako traceability prepája potrebu, failure mode, control a dôkaz?
7. Aký je rozdiel medzi false positive a false negative?
8. Prečo vysoká environment fidelity automaticky neznamená lepší test?
9. Kedy má byť quality gate blocking a kedy advisory?
10. Ako sa verification a validation líšia pri backupe a restore?
11. Čo znamená provenance testovacieho dôkazu?
12. Ako rozlíšiš chybný produkt od chybného testu alebo kontraktu?

## Ako sa z pozorovania stane testovací verdikt

Test nevytvára verdikt iba tým, že spustí kód. Najprv potrebuje presne pomenovaný subject, vstupné podmienky a pozorovanie, ktoré sa bude porovnávať s očakávaním. Pravidlo, podľa ktorého sa z pozorovania stane `PASS` alebo `FAIL`, sa nazýva **test oracle**. Oraclom môže byť konkrétna hodnota, invariant, schema, referenčný model alebo business pravidlo. Dôležité je, aby bolo jasné, prečo práve toto pravidlo predstavuje správnosť pre daný test scope.

Assertion je technický zápis oraclu. Keď test overí `actual_total == expected_total`, runner iba vykoná porovnanie; dôveryhodnosť výsledku závisí od toho, či `expected_total` vznikol z nezávislého a správneho pravidla. Ak test odvodí očakávanú hodnotu rovnakým chybným algoritmom ako produkčný kód, môže byť zelený aj pri defekte. Preto sa pri významných invariantov používa jednoduchší referenčný model, explicitný príklad alebo business pravidlo, ktoré nie je iba kópiou implementácie.

Slabý oracle vytvára dva typy omylov. **False positive** znamená, že kontrola hlási problém, hoci požadované správanie je správne. **False negative** znamená, že kontrola prejde, hoci subject porušuje dôležitý kontrakt. HTTP test, ktorý kontroluje iba status `200`, môže mať false negative pri nesprávnej cene, chýbajúcom audit evente alebo duplicitnom side effecte. Silnejší verdikt preto spája transportný výsledok s business hodnotou, počtom side effectov a následným read-backom state-u.

Verification a validation používajú rovnakú logiku dôkazu, ale porovnávajú výsledok s inou autoritou. Verification sa pýta, či subject spĺňa deklarovaný kontrakt. Validation sa pýta, či tento kontrakt a výsledok riešia skutočnú používateľskú alebo prevádzkovú potrebu. Zelená verification preto ešte neznamená, že systém prináša správnu hodnotu; a pozitívna používateľská skúsenosť neospravedlňuje porušenie bezpečnostného alebo dátového kontraktu.

Traceability uzatvára reťazec `riziko → požiadavka → kontrola → oracle → evidence → rozhodnutie`. Pri každom výsledku musí byť možné povedať, pre ktorý artifact, konfiguráciu, prostredie a čas platí. Bez tejto väzby je zelený test iba izolovaná udalosť, nie použiteľný release dôkaz.

## 25. Zhrnutie

Verification overuje správnosť voči explicitnému kontraktu; validation overuje správnosť zvoleného výsledku v reálnom kontexte. Dôveryhodná testovacia stratégia prepája potrebu, riziko, control, test oracle, environment a rozhodnutie a otvorene uvádza scope aj slepé miesta dôkazu.

Cieľom nie je maximalizovať počet zelených testov. Cieľom je získať najrýchlejší a dostatočne silný dôkaz pre rozhodnutie, pričom predprodukčné kontroly dopĺňa produkčná validation a observability.

## Glossary impact

Relevantné pojmy: verification, validation, test oracle, requirement traceability, risk traceability, false positive, false negative, environment fidelity, evidence provenance, quality gate, acceptance test, SLI a SLO.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Praktický Git a automation projekt od prázdneho adresára po overený apply](../03-git-and-automation/git-automation-practical-walkthrough.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Test pyramid →](test-pyramid.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
