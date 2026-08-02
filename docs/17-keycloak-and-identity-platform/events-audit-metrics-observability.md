# Events, audit, metrics a observability

Keycloak observability nie je jedna obrazovka ani jeden typ záznamu. User Events, Admin Events, server logs, HTTP access logs, metrics, health endpoints a traces vznikajú v odlišných subsystémoch, majú odlišnú retention a correlation identity a dokazujú rozdielne časti identity lifecycle-u. Login event môže potvrdiť, že konkrétny realm spracoval authentication transaction; nepreukazuje, že downstream API prijalo token. Admin Event môže potvrdiť prijatie mutation na resource path; nepreukazuje final configuration generation ani revokáciu už vydaných tokenov. Prometheus counter môže ukázať zvýšený počet login failures; neidentifikuje konkrétnu transakciu ani poškodeného usera.

Prevádzkový model preto začína presným observed subjectom a otázkou, ktorú má evidence zodpovedať. Pri incidente `user sa nevie prihlásiť` treba oddeliť request path, authentication session, user event, server error, cluster node, upstream identity provider, database/cache stav a downstream client outcome. Pri incidente `admin zmenil client` treba spojiť actor session, target realm, internal client UUID, Admin Event, read-back configuration, runtime endpoint metadata a druhú operáciu.

## 1. Dominantný evidence lifecycle

```text
identity, administration alebo runtime operation
→ exact request a deployment/realm/client/node generation
→ Keycloak processing stage
→ user event alebo admin event
→ server a HTTP access log
→ metric counter/histogram/gauge
→ optional trace/span context
→ external collection, delivery a retention
→ query, correlation a incident hypothesis
→ authoritative read-back a business acceptance
```

Každá šípka môže zlyhať samostatne. Event môže byť vytvorený, ale event listener ho nedoručí. Log môže vzniknúť na stdout, ale collector stratí Pod pred odoslaním. Metric môže byť správna na jednom node, ale Prometheus nescrapuje druhý node. Trace môže zachytiť server span, ale downstream application nepokračuje v rovnakom trace context-e. Observability verdict preto musí uviesť coverage, expected population, missing cohorts a časové okno.

## 2. Exact observability subject

Minimálny incident manifest pre `KC-PAY-69`:

```yaml
observabilitySubject:
  keycloak:
    deploymentGeneration: kc-2026-08-02-20
    version: 26.7.0
    realm: atlas-prod
    issuer: https://sso.atlas.example/realms/atlas-prod
    node:
      podUid: 8e24...
      hostname: keycloak-2
      startedAt: 2026-08-02T06:10:14Z
  operation:
    type: authorization-code-login
    clientId: settlement-admin-web
    clientInternalId: 2b2b...
    userId: 78f4...
    authenticationSessionId: 6e21...
    userSessionId: 4c71...
    requestId: req-9912
    traceId: 24f9...
    startedAt: 2026-08-02T07:03:18Z
  evidenceGeneration:
    realmEventConfigRevision: events-41
    eventListeners: [jboss-logging, audit-kafka-v3]
    metricsConfigRevision: metrics-17
    logConfigRevision: logs-22
    collectorConfigRevision: otel-51
    retentionPolicyRevision: retention-12
```

Bez node start time sa event-metric counter po restarte môže nesprávne interpretovať ako traffic drop. Bez listener/config generation sa chýbajúci audit záznam nedá odlíšiť od nezapnutého event type-u. Bez request/session IDs sa user event, access log a downstream business request spájajú iba podľa času, čo je pri špičke nepresné.

## 3. User Events

User Events reprezentujú identity a protocol operations, napríklad login, login error, logout, refresh token, code-to-token exchange, credential update, account linking alebo token exchange. Event obsahuje realm, event type, client, user, session, IP, error a detail fields podľa konkrétnej operácie.

```text
authorization request
→ authentication flow
→ LOGIN alebo LOGIN_ERROR event
→ code response
→ CODE_TO_TOKEN event
→ token issuance
→ downstream API request
```

`LOGIN` event nepreukazuje `CODE_TO_TOKEN`, pretože browser môže po redirecte zavrieť stránku alebo client môže zlyhať pri code exchange. `CODE_TO_TOKEN` nepreukazuje API acceptance. `REFRESH_TOKEN` nepreukazuje, že nový access token bol použitý. Incident query preto musí sledovať celý intended chain, nie iba prvý zelený event.

Realm event configuration určuje, či sa events ukladajú, ktoré typy a error events sa zachovávajú, aká je expiry a ktoré listeners sa volajú. Retention v Keycloak databáze nie je náhradou za central audit archive. High-volume event storage má database a query cost a musí byť dimenzované spolu s cleanup policy.

Read-only inventory cez Admin REST API:

```bash
kcadm.sh get events/config -r atlas-prod | jq '{eventsEnabled,eventsExpiration,enabledEventTypes,eventsListeners,adminEventsEnabled,adminEventsDetailsEnabled}'

kcadm.sh get events \
  -r atlas-prod \
  -q type=LOGIN \
  -q client=settlement-admin-web \
  -q dateFrom=2026-08-02 \
  | jq '[.[] | {time,type,realmId,clientId,userId,sessionId,ipAddress,error,details}]'
```

Prvý output preukazuje stored realm configuration. Druhý preukazuje retained events, ktoré zodpovedajú query. Ani jeden nepreukazuje, že listener doručil event do externého systému alebo že query pokrýva všetky nodes a časové zóny.

## 4. Admin Events

Admin Events vznikajú pri operáciách cez Admin Console a Admin REST API. Dôležité fields sú actor/auth details, realm, operation type, resource type, resource path, error a voliteľná representation. `adminEventsDetailsEnabled` zvyšuje diagnostickú hodnotu, ale môže ukladať citlivé configuration data. Representation retention preto potrebuje data-classification a redaction contract.

```text
admin/service-account request
→ authorization cez realm-management alebo FGAP
→ resource mutation attempt
→ Admin Event CREATE/UPDATE/DELETE/ACTION
→ HTTP response
→ authoritative GET read-back
→ runtime/session/token descendant verification
```

Admin Event `UPDATE clients/<uuid>` s úspechom znamená, že server operáciu nespracoval ako error. Neznamená, že caller poslal intended full representation, že cache/runtime už používa successor generation ani že existujúce sessions/tokens boli invalidované. Pri timeout-e môže mutation uspieť a client nedostane response; Admin Event a read-back sa používajú na unknown-outcome resolution pred retry.

```bash
kcadm.sh get admin-events \
  -r atlas-prod \
  -q resourceTypes=CLIENT \
  -q operationTypes=UPDATE \
  -q dateFrom=2026-08-02 \
  | jq '[.[] | {time,operationType,resourceType,resourcePath,error,authDetails,representation}]'
```

Query musí viazať target realm a internal UUID. Resource path s mutable `clientId` nestačí. Pri automatizácii sa Admin Event koreluje s pipeline runom, operation ID, desired-state commitom a následným configuration hashom.

## 5. Event listeners a delivery semantics

Event Listener SPI umožňuje spracovať user aj admin events a poslať ich do logu, SIEM, message brokera alebo custom audit store. Listener je plugin code bežiaci v Keycloak procese; jeho latency, exception a transaction semantics môžu ovplyvniť request path.

```text
Keycloak transaction
→ event object
→ configured listener chain
→ listener local processing
→ external producer/buffer
→ broker acknowledgement
→ durable consumer store
```

`listener method returned` nie je automaticky `audit durably stored`. Fire-and-forget producer môže stratiť event po process crashi. Synchronous durable delivery môže zvýšiť login latency alebo availability coupling. Návrh musí zvoliť loss, duplication, ordering a backpressure semantics. Externý audit consumer potrebuje idempotency key odvodený z event identity, nie iba timestamp.

Custom listener acceptance zahŕňa successful event, error event, duplicate delivery, broker timeout, Keycloak restart, listener exception, schema evolution a second event po recovery. Plugin artifact digest a provider generation patria do evidence manifestu.

## 6. Server logs a HTTP access logs

Server logs vysvetľujú internal mechanismus a exceptions. Nie sú totožné s realm events. Category `org.keycloak.events` môže logovať events, ale log level a listener configuration rozhodujú o obsahu. Structured JSON alebo ECS output uľahčuje parsing; MDC môže pridať realm a client context.

```bash
bin/kc.sh start \
  --log=console,syslog \
  --log-console-output=json \
  --log-console-json-format=ecs \
  --log-mdc-enabled=true \
  --log-mdc-keys=realmName,clientId \
  --log-level=info,org.keycloak.events:debug
```

Log configuration preukazuje intended handler/format. Acceptance musí čítať actual startup config a sample output z každého node. Async logging môže stratiť tail pri crashi; syslog UDP môže stratiť packets; truncation môže odrezať event details; debug/trace môže odhaliť citlivé údaje a zvýšiť volume.

HTTP access logs sledujú method, path, status, latency a network identity podľa configured formatu. Status `200` na token endpoint-e nepreukazuje least privilege token. Status `302` na authorization endpoint-e nepreukazuje úspešný callback. Access log sa spája s user eventom, request ID a trace contextom.

## 7. Metrics a cardinality

Metrics sa zapínajú build-time/runtime optionom a sú dostupné na management interface `/metrics`. User-event metrics sú voliteľné a vytvárajú counters podľa event type-u a erroru. Counters sú per instance a po reštarte sa resetujú; cluster view vyžaduje scrape všetkých instances a aggregation.

```bash
bin/kc.sh build --health-enabled=true --metrics-enabled=true
bin/kc.sh start \
  --event-metrics-user-enabled=true \
  --event-metrics-user-events=login,logout,refresh_token,code_to_token \
  --event-metrics-user-tags=realm

curl --fail --silent http://127.0.0.1:9000/metrics \
  | grep '^keycloak_user_events_total'
```

Default realm tag drží cardinality nižšie. `clientId` a `idp` tags sú užitočné v malom inventory, ale pri tisícoch clients alebo dynamic IdP aliases môžu zvýšiť memory a monitoring cost. User ID, session ID alebo error message nesmú byť metric labels.

Metric `keycloak_user_events_total{event="login",error="invalid_user_credentials"}` ukazuje count v scrape population a intervale. Neidentifikuje brute-force actor ani affected user. Alert musí používať rate, expected traffic a deployment restart markers.

## 8. Health a management interface

Health endpoints a metrics patria prednostne na management interface, default port `9000`, ktorý sa nemá publikovať cez public reverse proxy. Health model rozlišuje startup, liveness a readiness.

```text
/health/started
→ server initialization completed

/health/live
→ process je živý

/health/ready
→ instance je pripravená prijímať traffic podľa checks

/health
→ aggregate health view
```

Liveness nesmie závisieť od transient downstream failure spôsobom, ktorý vytvorí restart storm. Readiness môže odobrať node z trafficu, ale nepreukazuje, že všetky realm clients alebo external IdPs fungujú. Synthetic login alebo token test je samostatná end-to-end kontrola.

## 9. Tracing a correlation

Tracing sleduje request execution cez Keycloak a podporované external calls. Trace sampling znamená, že neprítomný trace nie je dôkaz neprítomnej operácie. Security/audit events sa nesmú spoliehať iba na sampled telemetry.

Correlation contract:

```text
edge request ID
→ Keycloak HTTP request/span
→ authentication session
→ user/admin event
→ user/client session
→ token jti/sid alebo SAML SessionIndex
→ downstream request ID/span
→ business operation ID
```

Tokens nemajú niesť interný trace ID ako stabilný claim. Request-level correlation môže používať headers/log context a downstream operation IDs. Sensitive authorization codes, tokens, passwords, OTP values a action-token URLs sa nesmú logovať.

## 10. Incident `KC-PAY-69`

Atlas dashboard ukazoval stabilný login success rate. Jeden Keycloak Pod sa však reštartoval a jeho event counters sa resetovali. Prometheus scrape target pre druhý Pod bol `down`, no dashboard agregoval iba dostupnú series. Zároveň custom Kafka listener mal plný buffer a zahadzoval Admin Events bez durable acknowledgement.

Operátor zmenil redirect URI na clientovi s rovnakým `clientId` v staging realm-e namiesto production internal UUID. Admin API vrátil `204`, lokálny access log ukázal success a dashboard nezaznamenal error. Production incident pokračoval, pretože audit pipeline nemala target realm/internal ID a chýbal configuration read-back.

```text
partial scrape population + counter reset
→ misleading stable rate

listener buffer overflow
→ audit delivery gap

ambiguous client lookup
→ successful mutation na wrong target
→ no successor-state read-back
→ incident remains
```

Recovery obnovila scrape coverage, pridala node start/restart context, listener delivery metrics a durable producer acknowledgements. Admin automation teraz zaznamenáva target realm, internal UUID, operation ID a predecessor/successor hash. Dashboard zobrazuje missing-target count a per-cluster population, nie iba success ratio.

## 11. Evidence-preserving recovery

Zachovaj raw events/logs s source node a ingest timestampom, event configuration, listener artifact/config generation, scrape target inventory, Prometheus rule/dashboard revision, collector queue/drop metrics, trace sampling policy a affected request/session/business IDs.

Containment môže zvýšiť retention, zapnúť focused categories, zastaviť risky admin automation a obnoviť missing scrape/listener target. Nezapínaj plošný trace logging bez data-classification. Recovery musí opraviť source, delivery aj query layer a následne vykonať fresh positive a forbidden operations.

## 12. Acceptance matrix

Positive:

```text
fresh login
→ user event stored a externally delivered
→ access log a trace correlation
→ event metric increment na correct node
→ downstream operation succeeds
```

Recovery:

```text
listener/broker outage
→ bounded queue alebo explicit drop signal
→ recovery bez tichého gapu
→ second event durably visible
```

Forbidden:

```text
public request na :9000/metrics alebo /health
→ network/proxy rejects

wrong-realm admin mutation
→ target guard rejects pred mutation

sensitive token/password/action URL
→ absent from logs a event representation
```

Second-operation test zopakuje rovnaký login/admin journey po node restarte a overí counter reset handling, collector continuity, target identity a authoritative read-back.

## Kontrolné otázky

- Ktorý exact deployment, node, realm, client, user/session a operation event opisuje?
- Je evidence source-generated, delivered, durable, queryable alebo iba visible v jednom UI?
- Pokrýva metric všetky nodes a zohľadňuje counter reset?
- Sú event tags cardinality-safe?
- Vie custom listener signalizovať drop, duplicate a backpressure?
- Je management interface neverejná?
- Korelujú sa events, logs, traces, tokens a business operations bez logovania secrets?
- Prešli positive, missing-node, restart, listener-outage, wrong-target, sensitive-data a second-operation testy?

## Primárne zdroje

- [Keycloak Server Administration Guide — Events](https://www.keycloak.org/docs/latest/server_admin/)
- [Keycloak Observability — Metrics](https://www.keycloak.org/observability/configuration-metrics)
- [Keycloak Observability — User event metrics](https://www.keycloak.org/observability/event-metrics)
- [Keycloak — Management interface](https://www.keycloak.org/server/management-interface)
- [Keycloak — Logging](https://www.keycloak.org/server/logging)
- [Keycloak Server Developer Guide — Event Listener SPI](https://www.keycloak.org/docs/latest/server_development/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Admin Console, Admin REST API a automation](admin-console-admin-rest-api-automation.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Themes, email templates a localization →](themes-email-templates-localization.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
