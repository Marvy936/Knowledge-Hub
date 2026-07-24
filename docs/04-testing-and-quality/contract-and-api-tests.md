# Contract a API tests

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Testing and Software Quality
- Predpoklady: [Unit, integration a component tests](unit-integration-component-tests.md), [REST APIs a WebSockets](../02-networking-and-web/rest-apis-and-websockets.md)
- Súvisiace témy: OpenAPI, AsyncAPI, consumer-driven contracts, schema evolution, idempotency, compatibility matrix

## 1. Dve rozdielne vrstvy dôkazu

Contract test a API test riešia rozdielne riziká:

```text
contract test
→ producer a consumer majú kompatibilné očakávania

API test
→ konkrétna runtime implementácia sa cez verejné rozhranie správa správne
```

Contract test môže overiť compatibility bez reálnej siete, databázy alebo celého distribuovaného systému. API test vykonáva endpoint alebo message interface a overuje observable behavior, side effects a error semantics konkrétneho komponentu alebo nasadenia.

Potrebné sú oba typy dôkazu. Kompatibilná schema nezaručuje správnu runtime konfiguráciu a zelený API happy path nezaručuje, že zmena zostala kompatibilná so všetkými aktívnymi consumers.

## 2. Mentálny model: interface ako distribuovaná dohoda

Rozhranie je dohoda medzi autonómnymi stranami. Producer vlastní implementáciu poskytovaného behavioru, consumer vlastní spôsob používania a deployment platforma rozhoduje, ktoré verzie spolu v danom čase komunikujú.

```text
producer implementation
  ↕ musí zodpovedať
published contract
  ↕ musí pokrývať
consumer expectations
  ↕ musia byť kompatibilné s
reálnou deployment topology
```

Zlyhanie môže vzniknúť v ktorejkoľvek väzbe: specification je neaktuálna, provider ju nesplní, consumer sa spolieha na nezdokumentované behavior alebo sa do produkcie dostane kombinácia verzií, ktorá nebola overená.

## 3. Čo tvorí API kontrakt

API kontrakt nie je iba method, URL a status. Obsahuje všetko, na čom závisí správne a bezpečné správanie consumerov.

Typické dimenzie:

- operation identity — method, path, event name alebo command určujú, akú operáciu consumer žiada;
- request contract — fields, typy, constraints, headers, media type a povinné identity metadata;
- response contract — status codes, response schema, headers, pagination a error model;
- behavior semantics — význam fields, povolené state transitions, ordering a consistency;
- security semantics — authentication, authorization, tenant isolation a citlivé error details;
- delivery semantics — timeout, retry, idempotency, deduplication a acknowledgement;
- lifecycle — versioning, deprecation, compatibility window a support policy;
- operational limits — rate limits, payload size, concurrency a resource-cost boundaries.

Nezdokumentované behavior, na ktoré sa consumer dlhodobo spolieha, sa stáva de facto kontraktom. Jeho odstránenie môže byť breaking change aj vtedy, keď formálna schema zostala rovnaká.

## 4. API test

API test volá verejné rozhranie a overuje observable behavior. Môže byť component, integration alebo E2E test podľa toho, čo je za rozhraním skutočne spustené.

API test typicky overuje:

- happy path — správny status, payload a side effects pre platný request;
- input boundaries — required fields, typy, ranges, media types a size limits;
- state transitions — povolené a zakázané operácie podľa aktuálneho resource state;
- authentication a authorization — identity, scope, ownership a tenant boundary;
- concurrency — version tokens, ETags a lost-update ochranu;
- idempotency — behavior pri timeoutoch, retries a duplicate requests;
- pagination a filtering — ordering, cursors, limits a authorization každej stránky;
- failure semantics — stabilný error model, retryability a absence interných leaks;
- observability — correlation ID, audit event a relevantné telemetry metadata.

Silný API test nekontroluje iba shape response. Overuje aj význam výsledku a stav systému po operácii.

## 5. Contract test

Contract test overuje, že dve strany interpretujú rozhranie kompatibilne. Nemusí testovať celý business workflow ani reálny transport; jeho scope je presná dohoda na boundary.

Contract test môže overovať:

- provider implementáciu voči OpenAPI alebo AsyncAPI specification;
- consumer parser voči publikovaným examples a schema variants;
- consumer-driven interaction voči provider implementation;
- backward/forward compatibility dvoch schema versions;
- generated client alebo SDK voči server contractu;
- event producer a consumer voči registry policy a semantic invariants.

Contract test nevie sám potvrdiť DNS, TLS, runtime credentials, deployment routing ani reálny dependency state. Tieto riziká patria do integration, component alebo deployment testov.

## 6. Schema validation verzus semantic assertions

Schema overuje tvar a základné constraints. Nevie automaticky pochopiť všetky business invarianty.

Schema-validný, ale nesprávny payload:

```json
{
  "status": "paid",
  "amount": -100,
  "currency": "EUR"
}
```

Ak schema povoľuje ľubovoľné number, typy sú platné, ale finančný invariant je porušený. Preto API test kombinuje:

- schema assertion — payload má očakávaný shape a types;
- semantic assertion — values a vzťahy medzi fields dávajú business zmysel;
- state assertion — persisted alebo emitted stav zodpovedá operácii;
- side-effect assertion — nevznikla duplicita, nesprávny event alebo audit gap;
- security assertion — výsledok neporušuje identity alebo tenant boundary.

Schema je potrebná, ale nie dostatočná vrstva oraclu.

## 7. Producer-driven contract

Pri producer-driven modeli provider publikuje autoritatívnu specification, napríklad OpenAPI, GraphQL schema, protobuf definition alebo AsyncAPI. Pipeline overuje, že implementácia contract dodržiava a že navrhovaná zmena spĺňa compatibility policy.

Výhody:

- centrálne popísané rozhranie podporuje dokumentáciu, generation a linting;
- provider môže validovať request/response a operation coverage;
- compatibility diff vie odhaliť časť breaking changes pred release;
- SDK a mocks sa môžu generovať z rovnakého source-of-truth.

Limity:

- provider nemusí vedieť, ktoré fields a semantics consumers skutočne používajú;
- specification môže driftovať od runtime implementácie;
- schema diff neodhaľuje každú business alebo performance zmenu;
- generovaný client môže mať vlastné serialization alebo language-specific problémy.

Producer-driven contract potrebuje consumer feedback a runtime usage telemetry, inak môže formálne kompatibilná zmena poškodiť reálne použitie.

## 8. Consumer-driven contract

Consumer-driven contract zachytáva konkrétne interaction patterns, ktoré consumer potrebuje. Consumer vytvorí contract artifact, publikuje ho do brokeru alebo registry a provider ho overí proti svojej implementácii.

```text
consumer test vytvorí expectation
→ contract artifact sa publikuje s consumer verziou
→ provider verifier pripraví provider state
→ provider overí interaction
→ výsledok sa publikuje
→ deployment policy vyhodnotí kompatibilitu verzií
```

Výhody:

- contract reprezentuje reálne používané behavior;
- provider vidí breaking change pred nasadením;
- tímy môžu vyvíjať a deployovať nezávislejšie;
- nepotrebuje permanentné shared E2E prostredie.

Riziká:

- consumer môže over-specifikovať nepodstatné values a zmraziť implementáciu;
- neaktívny alebo zrušený consumer môže stale contractom blokovať evolúciu;
- provider-state setup môže byť pomalý alebo nestabilný;
- broker potrebuje ownership, retention a environment/version metadata.

## 9. Provider states

Provider state opisuje podmienky, v ktorých interaction dáva zmysel. Napríklad používateľ existuje, objednávka je pending, token je expired alebo účet nemá potrebný scope.

Provider-state setup má byť:

- deterministický — rovnaký state name vytvorí rovnakú relevantnú podmienku;
- izolovaný — parallel verification sa navzájom neovplyvní;
- idempotentný — opakovaný setup nevytvorí nekontrolované duplicity;
- minimálny — nevytvára celý produkčný dataset pre jednoduchú interaction;
- diagnostikovateľný — failure rozlíši setup chybu od contract mismatchu;
- bezpečný — nepoužíva produkčné dáta ani široké credentials.

State nemá diktovať internú implementáciu providera. Má pomenovať business predpoklad, nie napríklad konkrétny SQL insert sequence.

## 10. Matching rules a správna prísnosť

Contract musí rozlíšiť presné hodnoty od typov, patternov a invariantov. Príliš presný matcher vytvára brittle contract; príliš voľný matcher prepustí breaking behavior.

Nevhodne presné:

```text
createdAt musí byť presne 2026-01-01T00:00:00Z
requestId musí byť presne abc-123
```

Lepšie:

```text
createdAt je platný UTC timestamp
requestId je neprázdny identifier v definovanom formáte
```

Naopak `amount` nemá byť kontrolovaný iba ako number, ak consumer potrebuje nezápornú hodnotu s konkrétnou menou a presnosťou. Matcher má vyjadriť contract semantics, nie náhodné fixture values.

## 11. Backward, forward a full compatibility

Backward compatibility znamená, že novší producer alebo schema ostáva použiteľná starším consumerom. Forward compatibility znamená, že staršia strana toleruje vybrané novšie dáta alebo behavior.

Full compatibility kombinuje oba smery v definovanom rozsahu verzií. V praxi závisí od rollout modelu, pretože počas rolling deploymentu môžu súčasne komunikovať staré aj nové instances.

Príklady JSON zmien:

- pridanie optional field — často backward compatible, ak consumers tolerujú unknown fields;
- odstránenie alebo premenovanie field — typicky breaking pre consumer, ktorý ho používa;
- zmena typu alebo nullability — breaking, aj keď názov zostáva;
- zúženie povolených hodnôt — breaking pre existujúce dáta alebo requests;
- pridanie enum value — môže rozbiť exhaustive consumer parser;
- zmena defaultu — môže byť semantic breaking change bez schema diffu;
- zmena ordering-u — môže rozbiť pagination, podpisy alebo consumer assumptions.

Compatibility policy musí uvádzať, ktoré verzie a typy zmien podporuje, nie iba všeobecné tvrdenie „API je backward compatible“.

## 12. Tolerant reader

Tolerant reader ignoruje neznáme optional fields a sústreďuje sa na dáta, ktoré potrebuje. Tento prístup znižuje coupling a umožňuje producerovi pridávať informácie bez synchronizovaného release všetkých consumerov.

Tolerancia však nesmie skryť:

- chýbajúci required field;
- neplatný typ alebo formát;
- neznámu security-relevant enum hodnotu;
- porušený business invariant;
- nečakanú verziu alebo semantic zmenu.

Consumer má byť tolerantný voči rozšíreniu, ale prísny voči podmienkam potrebným pre bezpečný a správny výsledok.

## 13. OpenAPI lifecycle

OpenAPI specification môže byť spec-first alebo code-first. V oboch modeloch musí byť jasné, ktorý artifact je autoritatívny a ako sa drift odhaľuje.

Spec-first flow:

```text
review specification change
→ compatibility a lint checks
→ generate server/client artifacts podľa potreby
→ implement behavior
→ verify runtime responses voči spec
```

Code-first flow:

```text
implement annotated/API model
→ generate specification
→ diff voči publikovanej verzii
→ review compatibility
→ publish versioned contract
```

Kontroluj:

- request aj response schemas pre všetky relevantné statusy;
- nullable verzus optional semantics;
- security schemes a scopes;
- examples zodpovedajúce schemas;
- error model a headers;
- operation IDs stabilné pre generated clients;
- deprecation metadata a lifecycle;
- implementácia vracia to, čo specification deklaruje.

## 14. Generated clients a SDK

Generated client znižuje manuálny boilerplate, ale nie je automaticky správny contract dôkaz. Generation závisí od template verzie, language mappingu, nullable semantics, date/number reprezentácie a runtime transportu.

Testuj:

- generation je reprodukovateľná z pinned toolchainu;
- generated package sa skompiluje a má očakávané public API;
- serialization/deserialization funguje na representative payloads;
- error responses sa mapujú konzistentne;
- unknown fields a enum values majú definované správanie;
- publishnutá SDK verzia odkazuje na správny contract digest;
- aspoň kritické calls prejdú proti provider component testu.

SDK versioning je samostatný lifecycle od server deploymentu. Compatibility musí zohľadniť aj klientov, ktorí sa aktualizujú pomalšie.

## 15. GraphQL contracts

GraphQL schema poskytuje silný typový contract, ale schema-validita neoveruje resolver behavior, authorization ani performance.

Breaking alebo rizikové zmeny:

- odstránenie field alebo argumentu;
- zmena nullability;
- zmena argumentu na required;
- odstránenie enum value;
- zmena resolver semantics;
- field-level authorization alebo visibility;
- výrazné zhoršenie query costu.

Persisted-query alebo operation registry umožňuje zistiť, ktoré operations consumers reálne používajú. Schema diff potom možno kombinovať s usage dátami a contract tests konkrétnych queries.

## 16. Event-driven contracts

Event contract zahŕňa viac než payload schema. Producer a consumer môžu zlyhať napriek schema kompatibilite, ak sa rozídu v delivery alebo ordering assumptions.

Contract má popísať:

- event identity a version — consumer musí vedieť, aký typ udalosti spracúva;
- payload schema — fields, typy, optionality a semantic meaning;
- key/partition — určuje ordering a distribution;
- delivery semantics — at-most-once, at-least-once alebo iný model;
- acknowledgement a retry — definuje, kedy sa message považuje za spracovanú;
- deduplication identity — umožňuje idempotentné opakovanie;
- ordering assumptions — pomenúvajú, ktoré events musia byť spracované sekvenčne;
- retention a replay — určujú, ako sa nový alebo obnovený consumer dostane k histórii;
- dead-letter behavior — opisuje handling trvalo chybných messages.

Schema registry overí časť shape compatibility. Neoverí, že `OrderCreated` príde pred `PaymentCaptured`, že consumer je idempotentný alebo že partition key zachová potrebné ordering.

## 17. API authentication tests

Authentication určuje identitu. Testy majú pokryť:

- chýbajúci credential;
- neplatný podpis alebo certificate chain;
- expired alebo not-yet-valid token;
- nesprávny issuer, audience alebo client identity;
- revoked credential podľa podporovaného modelu;
- rozdiel medzi user a workload identity;
- bezpečné logovanie bez token leakage.

Výsledný status a error body majú byť konzistentné s protocol contractom a nemajú odhaľovať interné validation detaily.

## 18. API authorization tests

Authorization rozhoduje, čo autentifikovaná identity smie vykonať nad konkrétnym resource. Pozitívny role test nestačí; potrebné sú negatívne a cross-boundary scenáre.

Overuj:

- role alebo scope bez potrebného oprávnenia;
- resource ownership;
- tenant isolation;
- field-level alebo action-level policy;
- object identifiers patriace inej identity;
- bulk a pagination endpoints, ktoré môžu obísť filter;
- side effects a audit pri odmietnutej operácii.

`401` a `403` majú rozdielny význam. API test má overiť aj to, že unauthorized odpoveď neprezradí existenciu alebo citlivé vlastnosti resource.

## 19. Idempotency test

Pri write operácii s idempotency key testuj celý ambiguity scenár:

1. prvý request vytvorí presne jeden business výsledok;
2. rovnaký key a rovnaký payload vráti konzistentný výsledok bez ďalšieho side effectu;
3. rovnaký key s iným payloadom je odmietnutý podľa contractu;
4. súbežné requests s rovnakým key nevytvoria duplicitu;
5. server commitne zmenu, ale response sa klientovi stratí;
6. retry po tomto timeout-e vráti pôvodný výsledok;
7. po retention expiry je behavior explicitne definovaný.

HTTP method semantics samy osebe negarantujú business exactly-once. Test musí overiť persistentný stav, eventy, platby a audit, nie iba response status.

## 20. Optimistic concurrency

API môže používať ETag a `If-Match`, version field alebo compare-and-swap token. Test má vytvoriť skutočný race alebo stale-write scenár:

```text
client A načíta version 5
client B úspešne zapíše version 6
client A pošle update s version 5
→ server odmietne stale write
→ stav verzie 6 zostane zachovaný
```

Overuj status, error model, nezmenený persisted state a možnosť bezpečne načítať novú version. Bez takéhoto testu môže API potichu strácať súbežné zmeny.

## 21. Pagination a collection contract

Pagination contract obsahuje ordering, page size, cursor semantics a behavior pri concurrent writes. Testuj:

- empty collection a jedinú stránku;
- prvú, strednú a poslednú stránku;
- maximum/default page size;
- deterministic ordering a tie-breaker;
- invalid, tampered alebo expired cursor;
- duplicate alebo missing items pri relevantnom mutation modeli;
- filter a authorization zachované na každej stránke;
- cursor viazaný na query parameters alebo tenant, ak to contract vyžaduje.

Offset a cursor pagination majú rozdielne failure modes. Contract má povedať, akú konzistenciu consumer môže očakávať počas meniacich sa dát.

## 22. Async operations

API, ktoré vracia `202 Accepted`, ešte nepotvrdilo dokončenie práce. Contract musí definovať operation resource, status transitions, polling alebo callback, timeout, cancellation a retention výsledku.

Testuj:

```text
submit request
→ 202 + operation location
→ pending/running state
→ completed alebo failed terminal state
→ result/error contract
```

Over aj duplicate submit, retry po nejasnom timeoute, authorization operation statusu a cleanup starých operation resources. API test má čakať s deadline a diagnostickým pollingom, nie nekonečne.

## 23. Negative API tests

Negatívne scenáre overujú failure contract:

- malformed JSON alebo nepodporovaný media type;
- chýbajúci required field alebo unknown forbidden field;
- oversized body, header alebo collection request;
- neplatná identity a nedostatočné oprávnenie;
- neexistujúci resource a invalid state transition;
- duplicate request, stale version a conflict;
- rate limit a `Retry-After` semantics;
- dependency timeout alebo unavailable upstream;
- cancellation a client disconnect;
- nebezpečný input bez stack trace alebo interného leak-u.

Error response je verejný contract. Má stabilný machine-readable code, bezpečný detail, correlation ID a jasnú retryability.

## 24. Contract publication lifecycle

Contract artifact má vlastný lifecycle podobný buildu:

```text
create alebo generate
→ lint a validate
→ version a attach provenance
→ publish do registry/brokeru
→ provider verification
→ publish verification result
→ deployment compatibility decision
→ deprecate a expire
```

Artifact má obsahovať consumer/provider identity, source commit, branch alebo environment, contract version a toolchain metadata. Bez provenance nemožno spoľahlivo rozhodnúť, či zelený verification výsledok patrí ku konkrétnemu deployment kandidátovi.

## 25. Contract broker a deployment decision

Contract broker uchováva contracts a provider verification výsledky. Deployment policy môže vykonať rozhodnutie typu „can I deploy?“ pre konkrétnu kombináciu verzií a environmentu.

Rozhodnutie musí zohľadniť:

- ktoré consumer versions sú v cieľovom prostredí aktívne;
- ktoré provider buildy ich contracts overili;
- rolling deployment, kde staré a nové instances koexistujú;
- rollback na predchádzajúcu provider alebo consumer verziu;
- contracts z feature branches verzus production lines;
- zrušené consumers a retention stale contracts.

Kontrola latest-provider verzus latest-consumer nestačí. Reálny deployment topology môže obsahovať viac generácií naraz.

## 26. Versioning a deprecation

Versioning nevyrieši compatibility bez lifecycle policy. Organizácia musí definovať:

- čo sa považuje za breaking change;
- koľko major alebo release lines podporuje;
- ako dlho trvá deprecation window;
- ako sa consumers upozornia a meria ich migrácia;
- aký telemetry dôkaz povoľuje odstránenie field alebo endpointu;
- či rollback zostáva kompatibilný s novými dátami;
- kto schvaľuje exception a akú má expiráciu.

Nová API verzia vytvorená pre každú malú zmenu presúva complexity na routing, dokumentáciu a consumers. Preferuj kompatibilnú evolúciu a explicitnú major boundary pre skutočne breaking behavior.

## 27. Contract test verzus integration test

Contract test odpovedá: „Sú očakávania strán kompatibilné?“ Integration test odpovedá: „Funguje konkrétna runtime spolupráca cez reálnu boundary?“

```text
contract test
→ request/response alebo event dohoda je kompatibilná

integration test
→ transport, credentials, config a dependency skutočne spolupracujú
```

Provider môže prejsť consumer contractom, ale produkčný client zlyhá na TLS, DNS alebo nesprávnom base URL. Naopak integration happy path môže fungovať pre jeden payload, ale breaking field removal zostane nezachytený pre iného consumera.

## 28. API test verzus E2E test

API test opisuje vstupný protokol, nie automaticky scope. API component test môže spúšťať jeden komponent s kontrolovanými externými systems; API E2E test môže prejsť cez viac služieb, databáz a asynchrónne spracovanie.

V dokumentácii testu preto uvádzaj:

- endpoint alebo event boundary;
- reálne spustené komponenty;
- nahradené dependencies;
- environment a artifact versions;
- oracle a side effects;
- blind spots.

## 29. Failure artifacts a observability

Contract failure má zachytiť:

- consumer a provider version/commit;
- contract artifact digest;
- konkrétnu interaction a mismatch path;
- matcher verzus actual value;
- provider state a setup result;
- verifier/toolchain version;
- compatibility policy, ktorá rozhodla.

API runtime failure navyše potrebuje request/response metadata s redaction, correlation/trace ID, target instance, logs, persisted state a dependency failure. Bez týchto artifacts sa contract drift zamieňa s test-data alebo environment chybou.

## 30. Diagnostika contract failure

Postup:

1. identifikuj presné consumer/provider versions a environment;
2. otvor contract interaction a mismatch, nie iba všeobecný job status;
3. rozlíš schema, matcher, provider-state a runtime implementation failure;
4. over, či contract reprezentuje aktívne použitie a nie stale test;
5. porovnaj specification, generated artifact a runtime response;
6. zisti, či zmena je skutočne breaking alebo contract over-specifikovaný;
7. rozhodni medzi opravou providera, migráciou consumera, compatibility shimom alebo novou verziou;
8. over deployment a rollback matrix pred publikovaním;
9. pridaj regression contract alebo API test pre uniknutý failure mode.

## 31. Diagnostika API runtime failure

API test môže zlyhať pred dosiahnutím application behavior. Rozlišuj:

```text
DNS/TCP/TLS failure
routing alebo authentication failure
request validation failure
application/domain failure
dependency alebo persistence failure
oracle/test-data failure
```

Použi correlation ID, exact request, target IP/instance, server logs a persisted state. Rerun bez zachovania prvého attemptu môže odstrániť dôkaz timeoutu, race alebo idempotency chyby.

## 32. Anti-patterny

### Snapshot celého response bez semantics

Veľký snapshot sa rozbije pri nepodstatnom formatting alebo field-order rozdiele a kritická hodnota sa stratí v diffe. Použi cielené schema a semantic assertions.

### Mock server oddelený od contractu

Consumer testuje ručne vytvorený fake, ktorý sa môže rozísť s provider specification aj runtime behaviorom. Mock alebo stub má byť generovaný alebo contract-verified.

### Consumer contract ako kópia provider response

Expectation overuje všetky fields a exact values, hoci consumer používa iba dve. Contract potom blokuje bezpečné rozšírenie a refaktoring.

### Iba schema compatibility

Schema diff neodhaľuje zmenu defaultu, ordering-u, authorization, rate limitu alebo latency. Potrebné sú semantic a behavior tests.

### Latest-to-latest verification

Pipeline ignoruje staršie aktívne instances a rollback verzie. Zelený výsledok nepredstavuje reálnu deployment topology.

### Contract broker bez lifecycle

Stale feature contracts, zrušení consumers a nejasná provenance blokujú releases alebo vytvárajú false confidence. Broker potrebuje retention, tagging a ownership.

## 33. Rozhodovací rámec

Pre každú interface zmenu:

1. pomenuj producerov, consumerov a aktívne versions;
2. definuj autoritatívny contract source;
3. klasifikuj schema, semantic, security a delivery zmenu;
4. urč backward/forward compatibility požiadavky;
5. aktualizuj contract artifacts a generated clients;
6. pridaj provider a consumer verification;
7. otestuj runtime happy, negative a concurrency paths;
8. over rolling deployment aj rollback combinations;
9. publikuj provenance a compatibility result;
10. sleduj usage a deprecation telemetry;
11. odstráň starý behavior až po dôkaze migrácie.

## 34. Kontrolný checklist

- contract obsahuje shape aj behavior semantics;
- API test overuje side effects, nie iba status;
- provider implementation sa testuje voči publikovanej specification;
- consumer expectations používajú primerané matchers;
- provider states sú deterministické a izolované;
- compatibility policy zohľadňuje enum, defaults a ordering;
- authn/authz negatívne paths sú pokryté;
- write operations majú idempotency a concurrency tests;
- event contract opisuje delivery, ordering a deduplication;
- contract artifacts majú version a provenance;
- deployment decision používa aktívnu version matrix;
- failure artifacts umožnia lokalizovať drift;
- deprecation má ownera, telemetry a deadline.

## 35. Časté omyly

### „OpenAPI schema je celý API contract“

Nie. Neobsahuje automaticky všetky business semantics, ordering assumptions, performance limity alebo deployment compatibility.

### „Contract test nahradí integration test“

Nie. Contract overí dohodu; integration test overí reálny transport, config, credentials a runtime boundary.

### „Pridanie optional field je vždy bezpečné“

Nie. Consumer môže používať strict parser, podpis payloadu, exhaustive mapping alebo size-sensitive behavior.

### „Consumer-driven contract znamená, že consumer diktuje implementáciu“

Nemá. Consumer opisuje potrebný observable behavior; provider si ponecháva internú implementáciu a môže odmietnuť over-specifikované expectations.

### „Schema registry garantuje event compatibility“

Nie. Neoveruje ordering, delivery, idempotency, partition key ani business invariants.

## 36. Kontrolné otázky

1. Aký je rozdiel medzi contract testom a API testom?
2. Ktoré dimenzie okrem schema tvoria API contract?
3. Prečo schema validation nestačí ako oracle?
4. Aký je rozdiel medzi producer-driven a consumer-driven contractom?
5. Načo slúžia provider states?
6. Ako zvoliť správnu prísnosť matchera?
7. Aký je rozdiel medzi backward, forward a full compatibility?
8. Čo znamená tolerant reader a kde musí zostať prísny?
9. Ako testovať idempotency pri strate response po server-side commit-e?
10. Čo musí obsahovať event-driven contract?
11. Prečo latest-to-latest verification nestačí?
12. Aké metadata potrebuje contract artifact a broker?

## 37. Zhrnutie

API test overuje runtime behavior verejného rozhrania. Contract test overuje, že producer a consumers zostávajú kompatibilní bez potreby spustiť celý distribuovaný systém.

Dôveryhodná interface stratégia prepája specification, provider implementation, consumer expectations, contract artifacts, runtime API tests a reálnu deployment matrix. Schema je iba jedna časť dohody; rovnako dôležité sú semantics, security, idempotency, ordering, delivery a lifecycle evolúcie.

## Glossary impact

Relevantné pojmy: API contract, API test, contract test, producer-driven contract, consumer-driven contract, provider state, matcher, backward compatibility, forward compatibility, tolerant reader, contract broker, compatibility matrix, schema registry a deprecation lifecycle.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Unit, integration a component tests](unit-integration-component-tests.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: End-to-end a acceptance tests →](end-to-end-and-acceptance-tests.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
