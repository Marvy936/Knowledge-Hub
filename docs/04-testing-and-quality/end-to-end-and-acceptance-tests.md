# End-to-end a acceptance tests

End-to-end test overuje celý kritický flow cez viac reálnych komponentov a boundaries podobne, ako ho používa externý actor. Acceptance test rozhoduje, či systém spĺňa explicitné business alebo používateľské acceptance criteria. Tieto kategórie sa môžu prekrývať, ale nie sú identické.

E2E subject je celý journey, nie jedna funkcia. Môže zahŕňať UI alebo API gateway, identity, viac služieb, databázu, messaging a externú dependency. Jeho výhodou je vysoká integračná fidelity; nevýhodou pomalosť, drahý setup a slabšia lokalizácia failure.

Acceptance criterion musí byť merateľný a pozorovateľný. „Objednávka funguje“ nie je oracle. Lepší contract je:

```text
Given platný zákazník a dostupný produkt
When zákazník odošle objednávku
Then vznikne presne jedna objednávka
And používateľ dostane potvrdenie
And sklad sa zníži o jednu jednotku
```

Acceptance test môže byť vykonaný na nižšom scope-e, ak criterion nevyžaduje celý systém. E2E test zase môže byť technický journey, ktorý nie je priamym business acceptance testom, napríklad overenie login redirect chainu.

Neutrálny príklad cestovnej aplikácie: browser vyhľadá spoj, vytvorí rezerváciu, simuluje platbu a overí vydaný lístok. Jeden test prejde cez kritické boundaries, ale pri failure potrebuje artifacts: screenshot, trace, network log, backend correlation ID a database/event evidence.

E2E suite má zostať malá a risk-based. Duplikovanie každého input variantu na najvyššom scope-e vytvára pomalú a flaky pyramídu. Varianty patria nižšie; E2E overuje unikátne journeys a wiring.

Test data a environment musia byť kontrolované. Zdieľané účty, časovo citlivé inventory alebo neizolované payment sandboxy vytvárajú nondeterminism. Cleanup musí rešpektovať business side effects a unknown outcome.

End-to-end test a acceptance test odpovedajú na dve rozdielne otázky:

```text
E2E scope
→ cez ktoré reálne boundaries test prešiel?

Acceptance purpose
→ aký používateľský, business alebo prevádzkový výsledok musí byť prijateľný?
```

Jeden test môže byť súčasne E2E aj acceptance testom. Nie každý acceptance dôkaz však potrebuje celý systém a nie každý široký E2E tok má dostatočný oracle na prijatie release-u.

## 1. Cieľ kapitoly

Nosný model kapitoly je:

```text
potreba alebo kritický výsledok
→ acceptance criterion
→ kritická journey
→ reálne a nahradené boundaries
→ kontrolovaný počiatočný stav
→ vykonanie konkrétneho artifactu
→ technický a business oracle
→ dôkaz s blind spots
→ merge, release alebo prevádzkové rozhodnutie
```

Široký test má zmysel iba vtedy, keď vykonáva boundary, ktorú lacnejší scope nevie dôveryhodne reprezentovať.

## 2. Nosný scenár: Atlas objednávka

Atlas pripravuje release `orders-api` 3.9.0. Kritická používateľská potreba znie:

> Autentifikovaný zákazník odošle objednávku raz, sklad sa rezervuje, platba sa autorizuje, potvrdenie sa zobrazí a systém zachová auditnú stopu aj pri opakovanom requeste.

Acceptance criterion:

```gherkin
Given zákazník patrí do tenanta A a produkt je dostupný
And checkout používa idempotency key K
When zákazník odošle objednávku
Then vznikne presne jedna objednávka
And vznikne najviac jedna platobná autorizácia
And skladová rezervácia patrí tenantovi A
And zákazník uvidí potvrdenie do 30 sekúnd
And audit obsahuje customer ID, tenant ID a correlation ID
```

Táto journey spája technické hranice s prijateľným výsledkom:

```text
browser
→ public DNS a TLS
→ reverse proxy
→ frontend
→ orders-api
→ PostgreSQL transaction/outbox
→ broker
→ worker
→ payment sandbox
→ používateľské potvrdenie a audit
```

## 3. E2E scope nie je acceptance oracle

E2E opisuje vykonanú cestu. Ak test prejde cez browser, proxy, API a databázu, poskytuje dôkaz o wiring-u a spolupráci týchto vrstiev.

Acceptance opisuje význam výsledku. HTTP `200`, viditeľná stránka alebo vytvorený DB riadok samy osebe nedokazujú, že objednávka vznikla presne raz, patrí správnemu tenantovi a nevytvorila duplicitnú platbu.

Pre Atlas sú potrebné oba pohľady:

```text
E2E evidence
→ request prešiel reálnou deployment cestou

Acceptance evidence
→ výsledný business state spĺňa dohodnuté invariants
```

## 4. Výber kritickej journey

E2E suite nemá kopírovať každú kombináciu business pravidiel. Kritická journey je vhodná, keď:

- jej zlyhanie má vysoký finančný, bezpečnostný alebo prevádzkový dopad;
- prechádza boundary, ktorú nižší test nevykonáva reálne;
- kombinuje routing, identity, persistence alebo asynchronous processing;
- historicky zlyhávala pri deploymente alebo integrácii;
- výsledok ovplyvňuje release alebo prevádzkové prijatie;
- rovnaký dôkaz nemožno lacnejšie získať v unit, integration, component alebo contract scope-e.

Výpočet dane patrí primárne do unit testov. PostgreSQL constraint do integration testu. Globálny checkout journey má overiť iba reprezentatívne kritické varianty.

## 5. Journey contract

Každý E2E alebo acceptance test má explicitne uviesť:

```text
journey identity
→ business/operational owner
→ testovaný requirement alebo risk
→ počiatočný stav
→ reálne boundaries
→ nahradené dependencies
→ kroky
→ očakávané side effects
→ oracle a deadline
→ artifact a environment identity
→ failure artifacts
→ rozhodovací význam
```

Bez tejto mapy názov „E2E“ nehovorí, čo test skutočne dokazuje.

## 6. Artifact a environment provenance

Zelený výsledok je platný iba pre konkrétny vykonaný obsah. Atlas run zaznamená:

- source commit a release version;
- immutable image digest;
- deployment revision;
- databázovú schema verziu;
- feature-flag snapshot;
- proxy, identity a dependency konfiguráciu relevantnú pre journey;
- browser/runtime a test-tool version;
- environment a test-run identity.

Ak test používa mutable tag `latest`, ktorý sa medzi testom a promotion zmenil, evidence sa nedá priradiť k releasovanému artifactu.

## 7. Fidelity podľa testovaného rizika

Test environment nemusí kopírovať produkciu vo všetkom. Musí zachovať vlastnosti relevantné pre failure mode.

Pre Atlas journey sú kritické:

- rovnaký image digest a entrypoint;
- reálny proxy route, Host a TLS/SNI behavior;
- rovnaký identity a tenant-authorization model;
- kompatibilný PostgreSQL engine a migrácie;
- reálny broker delivery model;
- payment sandbox alebo contract-verified simulator;
- rovnaký outbox a worker lifecycle.

Rozdiely sa evidujú:

```text
produkčná vlastnosť
→ testovacia náhrada
→ riziko rozdielu
→ kompenzačný contract, sandbox alebo production signal
```

## 8. Počiatočný stav a fixtures

Fixture má vytvoriť minimálny možný stav bez obídenia predmetu testu.

Legitímne:

- vytvoriť zákazníka cez test-only identity API;
- seednúť produkt a zásobu cez versioned fixture boundary;
- použiť payment sandbox;
- prideliť unikátny tenant, order prefix a correlation ID.

Nelegitímne pre túto journey:

- vložiť finálnu objednávku priamo do DB;
- označiť platbu za autorizovanú bez vykonania payment boundary;
- zapísať finálny event priamo do consumer databázy;
- obísť authorization middleware interným admin endpointom.

Gray-box setup je prijateľný, iba ak nevytvára nemožný stav a nepreskakuje boundary, ktorú test deklaruje ako dôkaz.

## 9. Test data a bezpečnosť

Každý run používa:

- unikátny tenant alebo namespace;
- test-only identity s minimálnymi oprávneniami;
- syntetické dáta;
- idempotency a correlation keys;
- resource tags alebo TTL;
- cleanup obmedzený na vlastnené resources.

Destruktívny alebo finančný journey musí zlyhať zatvorene, ak target environment nie je explicitne povolený. Test nesmie odoslať reálnu platbu, email alebo objednávku.

## 10. Synchronný a asynchrónny oracle

Prvá response potvrdzuje iba prijatie requestu. Atlas journey potrebuje viac pozorovaní:

```text
POST /orders
→ response contract
→ persisted order a idempotency record
→ outbox event
→ broker delivery
→ payment authorization
→ terminal order state
→ confirmation v UI/API
→ audit event
```

Asynchrónne čakanie používa condition-based polling s deadline:

```text
opakuj diskriminačný probe
→ krátky interval
→ posledný pozorovaný stav
→ skonči pri splnení podmienky alebo po 30 s
```

Pevný `sleep` je súčasne pomalý aj flaky. Failure musí uviesť posledný terminal/non-terminal state, correlation ID a elapsed time.

## 11. Silný acceptance oracle

Atlas oracle overuje:

- zákazník vidí správny order ID a konečný stav;
- objednávka patrí tenantovi A;
- existuje presne jeden business order;
- rovnaký idempotency key nevytvorí ďalší side effect;
- skladová rezervácia a platobná autorizácia korešpondujú s order ID;
- event a audit obsahujú správnu identity a correlation;
- nevznikol zakázaný side effect v inom tenantovi;
- výsledok vznikol v deklarovanom deadline.

Priame čítanie interných tabuliek používaj iba na diagnostiku alebo na invariant, ktorý verejná boundary nevie pozorovať. Test sa nemá viazať na nepodstatné interné kroky.

## 12. Browser a verejný contract

UI test používa stabilné selectors:

- semantic role;
- accessible name;
- form label;
- explicitný test ID iba tam, kde význam nemožno vyjadriť semanticky.

Domain-oriented test API má vyjadriť zámer:

```text
customer.sign_in()
customer.place_order(product)
customer.wait_for_confirmation(order_id)
```

Nemá prehĺtať failures ani implementovať druhú verziu business logiky.

## 13. Externé dependencies

Payment provider možno reprezentovať viacerými dôkazmi:

```text
consumer/provider contract test
→ deterministický simulator pre failure paths
→ periodický test proti oficiálnemu sandboxu
→ produkčná telemetry a synthetic guardrail
```

Simulator zvyšuje determinism, ale nepreukazuje reálny provider networking, credentials, quotas ani nezdokumentované behavior. Blind spot musí byť explicitný.

## 14. User a operational acceptance

User Acceptance Testing overuje, či workflow zodpovedá reálnej práci a doménovým pravidlám. Nemá nahrádzať automatizované testy authorization, schema alebo retry logiky.

Operational Acceptance Testing overuje, či je release prevádzkovateľný:

- artifact možno bezpečne nasadiť a identifikovať;
- alerts a traces vedú k diagnóze;
- rollback alebo roll-forward je vykonateľný;
- on-call identity má potrebné oprávnenia;
- backup/restore, failover alebo degraded mode spĺňajú svoj contract;
- recovery je merateľná.

Funkčne správny systém bez diagnostiky a recovery nie je prijateľný pre produkciu.

## Ako ohraničiť end-to-end a acceptance dôkaz

End-to-end test sleduje operáciu cez viac vrstiev systému. Jeho „end“ musí byť pomenovaný: môže začínať na verejnom API alebo v browseri a končiť final state-om v databáze, odoslaným eventom či potvrdeným externým side effectom. Test, ktorý skončí pri HTTP `202`, nie je end-to-end dôkazom asynchrónneho workflowu, ak skutočný používateľský výsledok vzniká až po spracovaní queue a provider response.

Acceptance test odpovedá na inú otázku. Posudzuje, či výsledok spĺňa používateľské alebo business pravidlo. Môže byť vykonaný end-to-end, ale nemusí; business pravidlo možno často overiť aj component testom s vysokou fidelity. Naopak technický end-to-end smoke test môže potvrdiť routing a persistence bez toho, aby dokazoval, že workflow je pre používateľa správny alebo zrozumiteľný.

Vyšší scope potrebuje disciplinovaný setup. Test data musí mať unikátnu identity, tenant a cleanup policy. Identity, feature flags, time, dependencies a environment generation musia byť zaznamenané, inak failure nie je reprodukovateľný. Pri paralelných runoch nesmú testy zdieľať rovnaký order ID alebo meniť globálnu konfiguráciu bez izolácie.

Oracle má sledovať finálny outcome aj forbidden outcomes. Pri objednávke nestačí nájsť row so stavom `COMPLETED`; test má overiť cenu, tenant ownership, jeden audit event, jeden provider side effect a absenciu duplicitnej operácie po retry. Ak test zlyhá, evidence má zachovať request ID, trace, deployment generation a relevantné state transitions pred cleanupom.

End-to-end testy sú drahé a citlivé na okolité systémy, preto nemajú niesť celé regresné portfólio. Používajú sa na kritické reťazce a integračné predpoklady, ktoré nižšie scope-y nevedia pozorovať. Defect zistený na tejto vrstve sa má doplniť menším testom tam, kde vznikla najskoršia diskriminačná hranica, zatiaľ čo vyšší test zostane dôkazom celého workflowu.

## 15. Worked failure: fixture vytvorila false green

Atlas E2E test pripravoval objednávku interným fixture endpointom:

```text
fixture vytvorila order v stave PAID
→ UI otvorilo detail objednávky
→ test videl potvrdenie
→ suite bola zelená
```

V produkcii však reálny flow zlyhal:

```text
POST /orders
→ DB commit
→ outbox event chýbal
→ worker nikdy nevolal payment provider
→ používateľ čakal bez potvrdenia
```

### Root cause

Fixture preskočila presne tie boundaries, ktoré mal test dokazovať: command handler, transaction/outbox, broker a worker.

### Náprava

- fixture vytvára iba zákazníka, produkt a zásobu;
- journey spúšťa objednávku verejným API alebo UI;
- condition-based oracle čaká na terminal state;
- test overí order, outbox/event, payment sandbox a audit;
- nižší integration test samostatne chráni atomicitu order + outbox.

E2E test má vykonávať kritickú cestu, nie iba kontrolovať jej konečný obraz.

## 16. Worked failure: product alebo environment?

Po deploymente test zlyhal na TLS ešte pred aplikáciou. Rerun z interného cluster runnera prešiel.

Observation points:

```text
external runner
→ public DNS OK
→ TLS certificate hostname mismatch
→ proxy/application neboli dosiahnuté

cluster runner
→ internal service DNS
→ bez public certificate boundary
→ test prešiel
```

Failure bol environment/deployment wiring problém, nie business logic. Release sa napriek tomu nemohol považovať za prijateľný, pretože používateľská cesta zostala nefunkčná.

## 17. Failure artifacts

Pri failure uchovaj:

- testovaný artifact a environment revision;
- presný krok a first-attempt result;
- screenshot alebo response payload;
- browser/network trace podľa scope-u;
- request, correlation a trace ID;
- relevantné server logs a event timeline;
- order, payment a broker identifiers;
- fixture a feature-flag snapshot;
- posledný stav pri polling-u;
- timestamps v jednotnej timezone.

Artifacts musia byť redigované a viazané na konkrétny attempt.

## 18. Diagnostický postup

1. Potvrď artifact digest, environment revision a feature flags.
2. Over, že fixture vytvorila očakávaný počiatočný stav.
3. Nájdite prvý odlišný observation point, nie posledný UI symptóm.
4. Koreluj browser/client čas, request ID, trace a events.
5. Rozlíš runner/test-code, fixture/data, environment a product failure.
6. Over deadline a posledný pozorovaný asynchronous state.
7. Reprodukuj najmenším scope-om, ktorý ponechá podozrivú boundary reálnu.
8. Zachovaj artifacts pred cleanupom.
9. Oprav root cause alebo dočasne quarantine s ownerom a expiráciou.
10. Po náprave over first-attempt pass na rovnakom artifacte.

Rerun bez analýzy nevytvára nový dôkaz o pôvodnom failure.

## 19. Segmentácia podľa rozhodnutia

```text
PR critical journey
→ krátky blocking dôkaz pre merge

deployment journey
→ artifact, routing a základný business tok

pre-release acceptance
→ formálne funkčné a operational criteria

scheduled broader journey
→ compatibility, recovery alebo dlhší asynchronous tok

production synthetic/canary
→ realita identity, trafficu a dependency pathu
```

Každá skupina má trigger, time budget, ownera, blocking význam a retention artifacts.

## 20. Referenčné pravidlá

- E2E scope a acceptance účel vždy pomenúvaj oddelene.
- Vyber iba journeys s unikátnou cross-boundary dôkaznou hodnotou.
- Väčšinu business kombinácií testuj nižšie.
- Testuj immutable artifact s jasnou environment identity.
- Fixture nesmie obísť predmet dôkazu.
- Asynchrónny oracle používa condition a deadline, nie sleep.
- Acceptance oracle overuje business state aj zakázané side effects.
- Destruktívne testy používajú allowlist a fail-closed target check.
- First-attempt failure a artifacts sa nikdy neprepisujú rerunom.
- Produkčná validation dopĺňa, nie nahrádza predprodukčný dôkaz.

## 21. Časté omyly

### „E2E znamená celý podnikový stack“

Nie. Scope má definovaný začiatok, koniec a explicitne nahradené dependencies.

### „Acceptance test musí ísť cez browser“

Nie. Acceptance opisuje účel a oracle; môže bežať v API, component alebo inom vhodnom scope-e.

### „Stránka sa zobrazila, journey prešla“

UI render nepreukazuje business invariants ani side effects.

### „Priama DB fixture iba zrýchľuje test“

Môže odstrániť boundary, ktorú mal test vykonať.

### „Produkčne podobné prostredie je automaticky dostatočné“

Dostatočné je iba pre explicitne zachované vlastnosti a známe blind spots.

### „Rerun prešiel, failure bol flaky“

Rerun neklasifikuje príčinu. Intermittent product race môže prejsť na druhý pokus.

## 22. Zhrnutie

Dôveryhodný E2E a acceptance test je decision-oriented journey:

```text
kritická potreba
→ acceptance criterion
→ reálne boundaries
→ konkrétny artifact a environment
→ kontrolovaný setup
→ journey execution
→ technický + business oracle
→ evidence a blind spots
→ release alebo operational decision
```

Atlas objednávka potrebuje široký test iba na potvrdenie cross-boundary toku. Lokálne pravidlá, SQL atomicita a interface kompatibilita zostávajú v nižších, rýchlejších vrstvách.

## 23. Kontrolné otázky

1. Aký je rozdiel medzi E2E scope-om a acceptance účelom?
2. Prečo acceptance test nemusí byť E2E testom?
3. Ktoré failure modes odôvodňujú kritickú journey?
4. Čo musí obsahovať journey contract?
5. Prečo je artifact provenance súčasťou dôkazu?
6. Kedy gray-box fixture obchádza predmet testu?
7. Ako sa testuje eventual consistency bez pevného sleepu?
8. Aké business a technické assertions potrebuje Atlas objednávka?
9. Ako service virtualization mení fidelity?
10. Čo navyše dokazuje Operational Acceptance Testing?
11. Ako rozlíšiš product failure od environment failure?
12. Prečo rerun-until-green ničí gate?

## Glossary impact

Relevantné pojmy: end-to-end test, acceptance test, critical journey, journey contract, User Acceptance Testing, Operational Acceptance Testing, black-box test, gray-box fixture, artifact provenance, environment fidelity, eventual consistency, condition-based waiting, service virtualization, synthetic transaction, failure artifact a quarantine.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Contract a API tests](contract-and-api-tests.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Smoke a regression tests →](smoke-and-regression-tests.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
