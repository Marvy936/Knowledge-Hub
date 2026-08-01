# Contract a API tests

API test a contract test nie sú synonymá. **API test** posiela request na runtime rozhranie a overuje jeho aktuálne správanie: status, headers, body, authorization, side effects alebo latency. **Contract test** overuje kompatibilitu medzi producerom a consumerom podľa explicitnej dohody o messages a semantics.

Provider contract môže byť OpenAPI, AsyncAPI, protobuf schema, event schema alebo iný versioned artifact. Schema však zachytí iba časť contractu. Dôležité sú aj required/optional fields, error semantics, ordering, idempotency, authorization a lifecycle.

Consumer-driven contract zachytáva interactions, ktoré konkrétny consumer reálne potrebuje. Provider ich verifikuje voči svojej implementácii. Producer-driven contract vychádza z providerom publikovanej špecifikácie a consumers sa testujú proti nej. Obe stratégie potrebujú version a deployment compatibility model.

Neutrálny príklad:

```text
consumer očakáva:
GET /items/42
→ 200
→ JSON s required fieldmi id a price

provider zmena:
price sa premenuje na amount
```

Provider môže mať lokálne zelené API testy pre nový response, no contract test odhalí, že existujúci consumer stále potrebuje `price`.

Backward compatibility znamená, že nový provider funguje so starým consumerom. Forward compatibility môže znamenať, že starší provider alebo consumer toleruje nové additive data podľa contractu. Reálna deployment matrix môže obsahovať viac súčasných verzií než iba latest/latest.

Contract test nepreukazuje dostupnosť runtime prostredia, routing ani reálny database side effect. API test zase nemusí odhaliť, že zmena rozbije consumer, ak testuje iba providerov vlastný pohľad. Preto sa kombinujú contract artifact, provider verification, consumer tests a vybrané runtime API journeys.

Pri event-driven systéme treba testovať nielen schema, ale aj key, ordering, duplicate, retry a evolution semantics. Syntakticky validný event môže byť semanticky nekompatibilný.

## 1. Cieľ kapitoly

Contract test a API test poskytujú dva odlišné dôkazy o tej istej interface boundary:

```text
contract test
→ producer a consumer majú kompatibilné očakávania

API test
→ konkrétna runtime implementácia sa cez verejné rozhranie správa správne
```

Ani jeden dôkaz nestačí samostatne. Kompatibilná schema nezaručuje správny routing, authorization, side effects ani runtime config. Zelený API happy path nezaručuje kompatibilitu so všetkými aktívnymi consumers.

Nosný lifecycle kapitoly:

```text
interface intent
→ autoritatívny contract
→ producer implementation
→ consumer expectations
→ versioned contract artifacts
→ compatibility verification
→ runtime API behavior
→ deployment version matrix
→ usage telemetry a deprecation
```

## 2. Nosný scenár: Atlas `CreateOrder`

Atlas poskytuje operáciu:

```http
POST /orders
Authorization: Bearer <token>
Idempotency-Key: 9d42...
Content-Type: application/json
```

Request:

```json
{
  "customerId": "cus-742",
  "currency": "USD",
  "lines": [
    {
      "sku": "book-01",
      "quantity": 2,
      "unitPrice": "29.95"
    }
  ]
}
```

Úspešná response:

```http
HTTP/1.1 201 Created
Location: /orders/ord-391
Content-Type: application/json
```

```json
{
  "id": "ord-391",
  "status": "pending_payment",
  "amount": "59.90",
  "currency": "USD",
  "version": 1
}
```

Po commite služby vznikne event:

```text
OrderCreated
→ billing-worker
→ analytics-consumer
→ notification-worker
```

Interface preto nie je iba JSON shape. Consumers závisia aj od identity, authorization, state transition, idempotency, event delivery a lifecycle-u fields.

## 3. Interface ako distribuovaná dohoda

Pri distribuovanom systéme neexistuje jeden spoločný runtime snapshot všetkých strán.

```text
producer source a artifact
↕
publikovaný contract
↕
consumer source, parser a assumptions
↕
reálne nasadené versions
```

Failure môže vzniknúť, keď:

- specification driftuje od providera;
- provider zmení behavior bez schema zmeny;
- consumer sa spolieha na nezdokumentovaný detail;
- contract matcher je príliš presný alebo príliš voľný;
- pipeline overí iba latest-to-latest, ale produkcia obsahuje staršie verzie;
- rollback verzia už nevie spracovať nové dáta;
- event schema je kompatibilná, ale zmení sa ordering alebo delivery semantics.

Contract strategy musí preto pracovať s verziami a deployment topology, nie iba s jedným súborom OpenAPI.

## 4. Čo tvorí contract operácie

Pre `CreateOrder` contract zahŕňa:

### Operation identity

```text
POST /orders
OrderCreated event
```

### Request

- media type;
- required a optional fields;
- typy a ranges;
- string/decimal representation;
- tenant a identity context;
- `Idempotency-Key`;
- size limits.

### Response

- status codes;
- response schema;
- `Location` header;
- error model;
- correlation ID;
- retryability.

### Behavior

- presný význam `pending_payment`;
- amount a currency invariant;
- povolené state transitions;
- presne jeden business výsledok pri duplicate requeste;
- optimistic concurrency cez `version` alebo ETag.

### Security

- authentication;
- tenant isolation;
- resource ownership;
- bezpečné error details;
- audit event.

### Lifecycle

- contract version a provenance;
- backward/forward compatibility;
- deprecation window;
- usage telemetry;
- rollback matrix.

Schema pokrýva iba časť tejto dohody.

## 5. Contract test verzus API test

Contract test sa pýta:

```text
Dokáže provider splniť očakávania consumera
pre konkrétnu kombináciu verzií?
```

API test sa pýta:

```text
Správa sa spustený provider správne
cez verejnú runtime boundary?
```

Príklad:

- consumer contract overí, že response obsahuje `id`, `amount`, `currency` a podporovaný `status`;
- provider verification spustí interaction proti implementácii;
- API component test pošle request cez HTTP socket a overí authorization, persisted order, outbox event a audit metadata;
- deployment smoke test overí DNS, TLS, routing a skutočný artifact.

Contract test nemusí mať reálny DNS/TLS path. API component test nemusí poznať contracts všetkých aktívnych consumers. Dôkazy sa dopĺňajú.

## 6. Autoritatívny contract source

Atlas používa OpenAPI pre HTTP boundary a AsyncAPI alebo schema registry artifact pre events.

Musí byť explicitné, či je flow:

### Spec-first

```text
review contract change
→ compatibility diff
→ generate models/stubs
→ implement provider a consumers
→ verify runtime proti spec
```

### Code-first

```text
implement typed public model
→ generate specification
→ diff voči publikovanému contractu
→ review compatibility
→ publish versioned artifact
```

V oboch prípadoch pipeline musí odhaliť drift:

```text
published contract
≠ generated contract
≠ runtime request/response behavior
```

Autoritatívny artifact musí mať version, source commit, toolchain identity a digest.

## 7. Schema assertion a semantic oracle

Schema-validná response môže byť business nesprávna:

```json
{
  "id": "ord-391",
  "status": "paid",
  "amount": "-59.90",
  "currency": "USD",
  "version": 1
}
```

Silný API oracle preto vrství:

```text
HTTP/protocol assertion
→ schema assertion
→ semantic assertion
→ persisted-state assertion
→ side-effect assertion
→ security a audit assertion
```

Pre `CreateOrder` over:

- `201` a správny media type;
- response zodpovedá publikovanej schéme;
- amount je presná nezáporná decimal hodnota v rovnakej currency ako request;
- order existuje presne raz v správnom tenante;
- outbox obsahuje presne jeden `OrderCreated`;
- response a event majú rovnaké order ID a amount;
- audit obsahuje identity, tenant, operation a výsledok;
- neunikli interné stack traces ani secrets.

## 8. Producer-driven contract

Producer-driven model publikuje autoritatívnu specification. Je vhodný pre:

- dokumentáciu;
- generovanie SDK;
- linting;
- request/response validation;
- compatibility diff;
- operation coverage.

Jeho blind spot:

```text
provider vie, čo deklaruje,
ale nemusí vedieť,
čo konkrétni consumers skutočne potrebujú
```

Optional field môže byť formálne odstrániteľný podľa neúplnej policy, ale reálny consumer ho môže používať ako business invariant. Preto producer-driven model potrebuje consumer tests a usage telemetry.

## 9. Consumer-driven contract

Consumer-driven contract zachytáva observable behavior potrebný konkrétnym consumerom.

Pre `checkout-web` môže interaction hovoriť:

```text
Given: authenticated tenant and valid cart
When: POST /orders
Then:
- status 201
- response has order id
- amount is a decimal string
- currency is USD
- status is pending_payment
```

Lifecycle:

```text
consumer test vytvorí contract artifact
→ artifact sa publikuje s consumer version
→ provider pripraví business provider state
→ provider overí interaction
→ výsledok sa publikuje
→ deployment policy vyhodnotí version matrix
```

Consumer nemá diktovať internú SQL schému ani presné timestampy. Má vyjadriť minimálny observable contract, ktorý potrebuje.

## 10. Provider states a matcher prísnosť

Provider state pomenúva business predpoklad:

```text
tenant exists and may create orders
customer is active
idempotency key was already committed
order version is stale
```

Nemá opisovať interný setup typu „insertni tri rows do tabuliek X a Y“.

State setup musí byť:

- deterministický;
- izolovaný;
- idempotentný;
- minimálny;
- diagnostikovateľný;
- bezpečný.

Matcher má rozlišovať fixture detail od contract semantics.

Príliš presné:

```text
id musí byť ord-391
createdAt musí byť presne konkrétny timestamp
```

Primerané:

```text
id je neprázdny order identifier
createdAt je platný UTC timestamp
amount je decimal string s povolenou scale
status patrí do consumerom podporovanej množiny
```

Príliš voľný matcher typu „amount je string“ by prepustil zápornú alebo nečíselnú hodnotu.

## 11. API component test jedného flowu

API test pre `CreateOrder` môže spustiť jeden `orders-api` komponent, PostgreSQL a fake broker.

```text
HTTP client
→ real socket
→ orders-api artifact
→ authn/authz middleware
→ domain logic
→ PostgreSQL
→ fake broker/outbox observer
```

Test overí:

1. validný request vytvorí presne jeden order;
2. response a persisted state sa zhodujú;
3. event vznikne až po úspešnom commite;
4. neplatný request nevytvorí side effect;
5. identity iného tenantu nemôže order čítať ani odvodiť jeho existenciu;
6. duplicate request zachová business idempotency;
7. logs a audit používajú correlation ID;
8. artifact/version endpoint dokazuje testovanú build identity.

Toto je runtime behavior evidence, nie automaticky contract coverage všetkých consumerov.

## 12. Worked compatibility change: `total` → `amount`

Atlas chce premenovať response field:

```text
total
→ amount
```

Priame odstránenie je breaking change pre starších consumers.

Bezpečný expand-and-contract flow:

```text
1. publikovať contract s amount aj deprecated total
2. provider vracia obe hodnoty z jedného autoritatívneho výpočtu
3. provider contract tests overia rovnosť total == amount
4. consumers migrujú na amount
5. deployment policy overuje staré aj nové consumer versions
6. usage telemetry potvrdí, že total sa nepoužíva
7. odstrániť total až po deprecation deadline
8. overiť rollback kompatibilitu
```

Schema diff je iba prvý signál. Potrebný je consumer dôkaz a reálna version matrix.

## 13. Worked contract failure: latest-to-latest false green

Pipeline pôvodne overila iba:

```text
checkout-web latest
↔ orders-api latest
```

Obe najnovšie verzie používali `amount`, takže verification bola zelená. V produkcii však zostala staršia mobilná verzia, ktorá vyžadovala `total`.

Deployment:

```text
orders-api bez total
+ mobile consumer v2 stále aktívny
→ parser failure
→ checkout completion zlyhá iba časti používateľov
```

Root cause nebol chýbajúci unit test providera. Chýbala deployment-aware compatibility matrix.

Contract broker alebo registry decision musí vyhodnotiť:

- aktívne consumer versions;
- provider build a jeho verification výsledky;
- rolling deployment kombinácie;
- rollback provider/consumer versions;
- stale contracts a zrušených consumers.

## 14. Authentication a authorization contract

Authentication overuje identity. Authorization rozhoduje, čo identity smie vykonať nad konkrétnym resource.

Pre Atlas testuj:

### Authentication

- chýbajúci credential;
- expired/not-yet-valid token;
- nesprávny issuer alebo audience;
- neplatný podpis;
- user verzus workload identity;
- žiadny token leak v logoch.

### Authorization

- tenant bez oprávnenia vytvoriť order;
- user z tenantu B číta order tenantu A;
- bulk/list endpoint zachová tenant filter;
- idempotency key je scoped na tenant a operation;
- odmietnutá operácia nevytvorí persisted ani event side effect;
- error neprezradí existenciu cudzieho resource.

`401`, `403` a `404` majú odlišnú protocol a information-disclosure semantics podľa zvoleného contractu.

## 15. Idempotency a unknown outcome

Test idempotency musí simulovať najnebezpečnejší flow:

```text
server commitne order a outbox
→ response sa stratí
→ klient vidí timeout
→ klient zopakuje request s rovnakým key
```

Oracle overí:

1. prvý request vytvoril presne jeden business outcome;
2. retry s rovnakým key a payloadom vráti pôvodný výsledok;
3. nevznikne druhý order, payment ani event;
4. rovnaký key s iným payloadom je odmietnutý;
5. concurrent requests s rovnakým key sa serializujú alebo bezpečne konfliktujú;
6. retention expiry má explicitný contract.

HTTP method alebo schema sama negarantuje exactly-once business behavior.

## 16. Optimistic concurrency

Update objednávky môže používať `version`, ETag alebo `If-Match`.

Test vytvorí skutočný stale-write scenár:

```text
client A načíta version 1
client B aktualizuje order na version 2
client A pošle update s version 1
→ server odmietne stale write
→ version 2 a jej side effects zostanú zachované
```

Over:

- conflict status a machine-readable error;
- persisted state sa nezmenil;
- nevznikol event pre odmietnutú mutation;
- klient môže načítať aktuálnu version;
- audit rozlíši conflict od authorization failure.

## 17. Event contract ako viac než schema

`OrderCreated` contract zahŕňa:

```text
event identity a version
payload schema a semantics
partition/order key
delivery model
acknowledgement a retry
deduplication identity
ordering assumptions
retention/replay
dead-letter behavior
```

Schema registry môže potvrdiť shape compatibility. Nepotvrdí:

- že `OrderCreated` predchádza `PaymentCaptured`;
- že partition key zachová ordering jedného orderu;
- že consumer je idempotentný;
- že redelivery nevytvorí druhú platbu;
- že replay starej udalosti je bezpečný.

Pre event flow kombinuj contract test, broker integration test a consumer component test.

## 18. Async operation a pagination ako contract decisions

Niektoré interface mechanizmy majú vlastný lifecycle.

### `202 Accepted`

```text
submit
→ operation resource
→ pending/running
→ completed alebo failed
→ result/error retention
```

Contract musí definovať polling, timeout, cancellation, authorization a duplicate submit behavior.

### Pagination

Contract musí definovať:

- ordering a tie-breaker;
- page size;
- cursor identity a expiry;
- behavior pri concurrent writes;
- authorization každej stránky;
- duplicate/missing item guarantees.

Tieto mechanizmy sa netestujú iba schema snapshotom. Potrebujú stateful API scenáre.

## 19. Generated clients a SDK

Generated SDK je ďalší consumer artifact. Testuj:

```text
pinned generator
→ reproducible SDK source/package
→ compile/type check
→ representative serialization
→ error mapping
→ component call proti provideru
→ publish s contract digestom
```

Rizikové rozdiely:

- nullable verzus optional;
- decimal/date mapping;
- unknown enum behavior;
- language-specific integer precision;
- generated method/operation IDs;
- SDK release cadence pomalšia než server.

Zelené generovanie nie je dôkaz, že publikovaný SDK artifact funguje proti provideru.

## 20. Contract publication a provenance

Contract artifact má build-like lifecycle:

```text
create/generate
→ lint a schema validation
→ semantic/compatibility review
→ attach source commit a toolchain
→ publish immutable artifact
→ provider verification
→ publish verification result
→ deployment decision
→ deprecate a expire
```

Potrebné metadata:

- producer/consumer identity;
- source commit;
- artifact version a digest;
- branch/environment intent;
- provider state a interaction identity;
- verifier/toolchain version;
- compatibility policy version;
- verification timestamp/result.

Bez provenance nemožno spojiť zelený contract result s konkrétnym deployment kandidátom.

## 21. Deprecation a usage evidence

Versioning nevyrieši lifecycle automaticky. Pre odstránenie `total` Atlas potrebuje:

- ownera deprecated field-u;
- dokumentovaný replacement;
- deadline;
- warning alebo documentation signal;
- usage telemetry podľa consumer version;
- aktívnu compatibility matrix;
- rollback plán;
- exception proces s expiráciou.

Field sa neodstraňuje preto, že „už je starý“. Odstraňuje sa po dôkaze, že podporované consumers ho nepotrebujú a rollout/rollback kombinácie zostanú bezpečné.

## 22. Failure artifacts

Contract failure musí uchovať:

- consumer/provider versions;
- contract artifact digest;
- interaction a mismatch path;
- matcher verzus actual value;
- provider state setup result;
- verifier version;
- compatibility policy a deployment matrix.

API runtime failure navyše potrebuje:

- exact request a response s redaction;
- target instance/artifact digest;
- correlation/trace ID;
- server logs;
- persisted state;
- emitted events;
- dependency status;
- timing a retry attempts.

## 23. Diagnostika contract failure

Postup:

1. identifikuj presné producer a consumer versions;
2. otvor konkrétnu interaction a mismatch;
3. rozlíš schema, matcher, provider-state a semantic failure;
4. over, či publikovaný contract zodpovedá source commitu;
5. over, či provider runtime zodpovedá testovanému artifactu;
6. zisti, či consumer expectation nie je over-specifikovaná;
7. klasifikuj zmenu ako compatible, breaking alebo policy exception;
8. over rolling deployment a rollback matrix;
9. pridaj regression contract alebo runtime test pre uniknutý failure mode.

## 24. Diagnostika API runtime failure

Lokalizuj boundary:

```text
DNS/TCP/TLS
routing
authentication/authorization
request parsing/schema
application/domain logic
persistence/dependency
oracle/test data
```

Použi correlation ID, target instance, exact request, server logs, persisted state a event identity. Rerun bez zachovania first attemptu môže odstrániť dôkaz timeoutu, race-u alebo idempotency failure.

## 25. Referenčné pravidlá

- Contract test overuje kompatibilitu očakávaní; API test runtime behavior.
- API contract obsahuje shape, semantics, security, delivery aj lifecycle.
- Schema assertion doplň business a side-effect oraclom.
- Provider states pomenúvajú business predpoklady, nie interný setup.
- Matchers majú byť prísne podľa semantics, nie fixture detailov.
- Contract artifacts musia byť immutable, versioned a provenance-linked.
- Deployment decision musí používať aktívnu version matrix, nie latest-to-latest.
- Write APIs testuj pri duplicate, timeout a concurrent flowoch.
- Event contract zahŕňa ordering, delivery, deduplication a replay.
- Deprecated behavior odstráň až po usage evidence.
- Fakes/stubs generuj alebo overuj voči contractu.

## 26. Časté omyly

### „OpenAPI je celý API contract“

Nie. Neobsahuje automaticky všetky business, security, delivery a performance semantics.

### „Contract test nahradí integration test“

Nie. Contract overí dohodu; integration test reálny transport, credentials a dependency behavior.

### „API test je automaticky E2E test“

Nie. API opisuje vstupnú boundary. Scope závisí od reálne spustených komponentov.

### „Optional field možno vždy bezpečne pridať“

Nie. Strict parser, exhaustive enum mapping, signatures alebo payload limits môžu zmenu spraviť breaking.

### „Consumer-driven contract diktuje implementáciu“

Nemá. Vyjadruje minimálny observable behavior potrebný consumerom.

### „Latest-to-latest green znamená bezpečný deployment“

Nie. Produkcia a rollback môžu obsahovať viac verzií naraz.

### „Schema registry garantuje event kompatibilitu“

Nie. Nepokrýva ordering, delivery, idempotency ani business invariants.

## Ako čítať API contract a runtime dôkaz

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

## 27. Zhrnutie

Pre Atlas `CreateOrder` je dôveryhodný interface chain:

```text
OpenAPI/AsyncAPI contract
→ provider implementation
→ consumer expectations
→ versioned contract artifacts
→ provider verification
→ API component/integration tests
→ deployment version matrix
→ runtime usage a deprecation evidence
```

Contract test dokazuje, že autonómne strany majú kompatibilnú dohodu. API test dokazuje, že konkrétny artifact túto dohodu a business behavior reálne vykonáva. Silná stratégia potrebuje oba dôkazy a explicitne ich viaže na versions, artifacts a deployment topology.

## 28. Kontrolné otázky

1. Aký je rozdiel medzi contract testom a API testom?
2. Ktoré dimenzie okrem schema tvoria `CreateOrder` contract?
3. Prečo schema-validná response nemusí byť business správna?
4. Aký je rozdiel medzi producer-driven a consumer-driven contractom?
5. Načo slúži provider state?
6. Ako zvoliť správnu prísnosť matchera?
7. Prečo latest-to-latest verification vytvorila Atlas false green?
8. Ako bezpečne migrovať field `total` na `amount`?
9. Ako sa testuje idempotency pri strate response po commite?
10. Čo musí overiť tenant authorization test?
11. Ako optimistic concurrency chráni pred lost update?
12. Čo okrem payload schema tvorí event contract?
13. Aké metadata potrebuje contract artifact?
14. Kedy možno deprecated field odstrániť?
15. Ako rozlíšiš contract mismatch od runtime API failure?

## Glossary impact

Relevantné pojmy: API contract, API test, contract test, producer-driven contract, consumer-driven contract, provider state, matcher, OpenAPI, AsyncAPI, backward compatibility, forward compatibility, tolerant reader, contract broker, compatibility matrix, idempotency key, optimistic concurrency, schema registry, event delivery semantics, contract provenance a deprecation lifecycle.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Unit, integration a component tests](unit-integration-component-tests.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: End-to-end a acceptance tests →](end-to-end-and-acceptance-tests.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
