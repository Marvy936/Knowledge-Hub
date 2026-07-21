# Contract a API tests

Contract tests overujú dohodu medzi producerom a consumerom bez potreby spustiť celý distribuovaný systém. API tests overujú správanie rozhrania cez jeho verejný protokol a kontrakt.

Tieto vrstvy riešia rozdielne riziká:

```text
contract test
→ rozhranie producer/consumer ostáva kompatibilné

API test
→ konkrétny endpoint sa pri runtime správa podľa kontraktu
```

## 1. Čo tvorí API kontrakt

Kontrakt nie je iba URL a HTTP status.

Zahŕňa napríklad:

- methods a paths,
- request a response schemas,
- required a optional fields,
- typy a constraints,
- status codes,
- error model,
- headers,
- authentication a authorization semantics,
- idempotency,
- pagination,
- rate limits,
- timeout a retry expectations,
- event schema a delivery semantics.

Nezdokumentované behavior, na ktoré sa consumer spolieha, sa môže stať de facto kontraktom.

## 2. API test

API test volá verejné rozhranie komponentu a overuje observable behavior.

Môže testovať:

- happy path,
- invalid input,
- authorization,
- not-found a conflict semantics,
- idempotency,
- pagination,
- concurrency control,
- error body,
- side effects,
- audit events.

API test môže byť component test, integration test alebo E2E test podľa toho, čo je za endpointom reálne spustené.

## 3. Schema validation nestačí

Schema overí tvar dát, ale nie vždy business semantics.

Príklad:

```json
{
  "status": "paid",
  "amount": -100
}
```

Dáta môžu zodpovedať typom, ale porušovať invariant.

Preto kombinuj:

- schema assertions,
- semantic assertions,
- state assertions,
- authorization assertions,
- side-effect assertions.

## 4. Producer-driven contract

Producer publikuje kontrakt, napríklad OpenAPI alebo AsyncAPI, a testuje implementáciu voči vlastnej špecifikácii.

Výhody:

- centralizovaný popis API,
- generovanie klientov a dokumentácie,
- schema validation,
- linting compatibility pravidiel.

Limit:

- producer nemusí vedieť, ktoré časti response consumer skutočne používa,
- špecifikácia môže byť neúplná alebo neaktuálna.

## 5. Consumer-driven contract testing

Consumer deklaruje očakávania voči providerovi. Tieto kontrakty sa publikujú a provider ich overuje vo vlastnom pipeline.

Flow:

```text
consumer test vytvorí expectation
→ contract sa publikuje
→ provider overí contract proti implementácii
→ deployment policy skontroluje kompatibilitu versions
```

Výhody:

- testuje reálne používané interaction patterns,
- zachytí breaking changes pred integráciou,
- umožní nezávislé pipelines.

Riziká:

- príliš detailné expectations môžu zmraziť implementáciu,
- zastarané consumers môžu blokovať evolúciu,
- contract broker potrebuje lifecycle a ownership.

## 6. Pact-style interaction

Consumer-driven contract často opisuje:

- provider state,
- request,
- expected response,
- matching rules.

Dôležitý je rozdiel medzi presnou hodnotou a matcherom.

Zlé:

```text
createdAt musí byť presne 2026-01-01T00:00:00Z
```

Lepšie:

```text
createdAt musí byť platný ISO-8601 timestamp
```

Contract má overovať semantics, nie náhodné test data.

## 7. Provider states

Provider verification potrebuje reprodukovať stav, v ktorom interaction platí.

Príklady:

- používateľ existuje,
- objednávka je pending,
- token je expirovaný,
- účet nemá oprávnenie.

Provider-state setup musí byť:

- deterministický,
- izolovaný,
- idempotentný,
- rýchlo obnoviteľný,
- bez väzby na shared production-like test data.

## 8. Backward a forward compatibility

### Backward compatibility

Nový producer funguje so starým consumerom.

### Forward compatibility

Starší producer alebo consumer zvládne vybrané novšie dáta alebo behavior.

Praktické pravidlá pre JSON API:

- pridanie optional field je často kompatibilné,
- odstránenie field je breaking,
- zmena typu je breaking,
- zúženie allowed enum values je breaking,
- pridanie enum value môže rozbiť consumera s exhaustive parsingom,
- zmena default behavior môže byť breaking aj bez schema zmeny.

## 9. Tolerant reader

Consumer nemá zlyhať na neznámom optional field-e, ak kontrakt nevyžaduje strict rejection.

Tolerant reader podporuje evolúciu, ale nesmie skryť:

- chýbajúce required field,
- neplatný typ,
- bezpečnostne významnú zmenu,
- business invariant violation.

## 10. OpenAPI testing

OpenAPI môže podporiť:

- request/response schema checks,
- operation coverage,
- generated clients,
- breaking-change diff,
- fuzzing,
- documentation validation.

Kontroluj:

- implementácia vs. specification,
- specification vs. consumer use,
- examples vs. schemas,
- security schemes,
- error responses,
- nullable/optional semantics.

Spec-first a code-first model majú oba riziko driftu. Pipeline musí definovať autoritatívny source a generovanie.

## 11. GraphQL kontrakty

GraphQL schema poskytuje silný typový kontrakt, ale kompatibilitu ovplyvňuje:

- odstránenie field,
- zmena nullability,
- odstránenie enum value,
- argument requirements,
- resolver performance,
- authorization na field úrovni.

Persisted queries alebo operation registry umožňujú overiť, ktoré operations consumers používajú.

## 12. Event-driven contracts

Pri messaging systémoch kontrakt zahŕňa:

- topic alebo routing key,
- event name a version,
- payload schema,
- key/partition semantics,
- ordering assumptions,
- delivery semantics,
- deduplication identity,
- retention a replay behavior.

Schema registry môže overovať compatibility, ale neoverí všetky business assumptions.

Príklad breaking zmeny:

```text
consumer predpokladá, že event `OrderCreated` príde pred `PaymentCaptured`
```

Payload schema môže byť kompatibilná, ale ordering contract bol porušený.

## 13. Negative API tests

Overuj:

- chýbajúce required fields,
- malformed payload,
- oversized input,
- unsupported media type,
- invalid authentication,
- insufficient authorization,
- duplicate request,
- stale version token,
- rate limit,
- dependency timeout,
- invalid state transition.

Error response má byť stabilný kontrakt, nie náhodný stack trace.

## 14. Authentication vs. authorization tests

Authentication testuje identitu:

- missing token,
- invalid signature,
- expired token,
- wrong issuer alebo audience.

Authorization testuje oprávnenie:

- role,
- scope,
- ownership,
- tenant isolation,
- resource policy.

HTTP 401 a 403 majú rozdielny význam. Testy majú overovať aj neúnik citlivých detailov.

## 15. Idempotency a retry

Pre retryable write API over:

1. prvý request vytvorí výsledok,
2. rovnaký idempotency key nezdvojí side effect,
3. rovnaký key s iným payloadom je odmietnutý alebo presne definovaný,
4. concurrent retries sú bezpečné,
5. failure po server-side commit-e a pred response nevedie k duplicite.

Samotný HTTP method semantics nestačí pre business exactly-once výsledok.

## 16. Pagination tests

Testuj:

- prvú a poslednú stránku,
- empty result,
- page size limits,
- stable ordering,
- duplicate/missing items pri concurrent writes,
- invalid alebo expired cursor,
- authorization scope v každej stránke.

Offset pagination a cursor pagination majú rozdielne failure modes.

## 17. Concurrency control

Optimistic concurrency môže používať:

- ETag a `If-Match`,
- version field,
- compare-and-swap token.

Test:

```text
client A načíta version 5
client B zmení resource na version 6
client A skúsi update s version 5
→ server vráti conflict/precondition failure
```

Bez tohto testu môže dochádzať k lost updates.

## 18. Contract test vs. integration test

Contract test môže používať controlled verifier a neoverovať reálnu sieť alebo databázu.

Integration test overuje konkrétnu runtime integráciu.

Potrebné sú oba:

```text
contract test
→ interfaces sú kompatibilné

integration test
→ konfigurácia, transport a runtime spolupracujú
```

## 19. Deployment compatibility

Pred deploymentom provider verzie treba vedieť:

- ktoré consumer versions sú aktívne,
- ktoré contracts overili provider build,
- či existuje rollback-compatible database/API model,
- či staré instances budú chvíľu bežať spolu s novými.

Kompatibilita sa posudzuje voči reálnemu deployment topology, nie iba latest-to-latest.

## 20. Anti-patterny

### Snapshot celého response bez semantics

Každá nepodstatná zmena rozbije test a kritická chyba môže byť schovaná v obrovskom diff-e.

### Mock server ručne odlišný od kontraktu

Consumer testuje falošné API, ktoré provider nikdy neposkytuje.

### Contract ako kópia implementácie

Test overuje interné fields a method calls namiesto verejného behavior.

### Iba happy path

Chýba authorization, invalid state, timeout a retry behavior.

### Breaking-change checker ako jediná ochrana

Schema diff neodhalí zmenu business semantics alebo performance behavior.

## 21. Diagnostický postup

Pri contract failure:

1. identifikuj consumer a provider versions,
2. zobraz presnú interaction a mismatch,
3. rozlíš schema, value matcher a provider-state problém,
4. over, či contract nie je zastaraný,
5. skontroluj, či ide o skutočný breaking behavior,
6. rozhodni medzi opravou providera, consumer migráciou a versioningom,
7. over deployment compatibility matrix.

Pri API runtime failure navyše kontroluj:

- DNS/network/TLS,
- routing,
- authentication,
- database state,
- dependency response,
- logs a trace ID.

## 22. Kontrolné otázky

1. Aký je rozdiel medzi contract testom a API testom?
2. Prečo schema validation nestačí?
3. Čo je consumer-driven contract?
4. Načo slúžia provider states?
5. Aký je rozdiel medzi backward a forward compatibility?
6. Čo znamená tolerant reader?
7. Ktoré JSON zmeny bývajú breaking?
8. Čo musí obsahovať event-driven contract?
9. Ako testovať API idempotency pri retries?
10. Ako contract tests podporujú nezávislé deployments?

## Glossary impact

Relevantné pojmy: API contract, contract test, consumer-driven contract, provider state, backward compatibility, forward compatibility, tolerant reader, schema registry, API test a compatibility matrix.