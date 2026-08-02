# Custom providers, SPI a extension lifecycle

Keycloak Service Provider Interface nie je sandboxovaný plugin systém. Provider JAR v `providers/` beží v rovnakom server process-e, používa spoločný classloader a môže čítať server configuration vrátane credentials, pristupovať k databáze, meniť authentication/authorization behavior, registrovať endpoints a ovplyvniť každú request transaction. Custom provider preto patrí do trusted computing base Keycloaku a potrebuje rovnakú supply-chain, secure-coding, transaction, concurrency, observability, upgrade a incident-response disciplínu ako samotný server.

Najčastejší anti-pattern je „malý listener“ bez lifecycle ownershipu. EventListener môže blokovať login pri pomalom brokeri, logovať tokens, držať mutable state medzi requests alebo po upgrade zlyhať na dependency conflict. Druhý anti-pattern je provider postavený proti internal classom: compile prejde, ale target release zmení method alebo model semantics. Provider registry success a Pod readiness nepreukazujú správnu transaction, cache, failure alebo security semantics.

## 1. Dominantný source-to-runtime-extension lifecycle

```text
business extension requirement
→ choose built-in configuration alebo justified SPI
→ exact source/dependency/API generation
→ Provider/ProviderFactory a service-loader registration
→ tests, security review a artifact provenance
→ JAR/dependencies copied do providers/
→ optimized Keycloak build a provider registry
→ immutable image deployment
→ runtime create/init/postInit/close lifecycle
→ request transaction/cache/external effects
→ observability, rollback a target-version rebuild
```

Každá šípka môže zlyhať samostatne. Service descriptor môže chýbať. JAR sa môže načítať, ale default provider selection zostane built-in. Provider môže fungovať pri jednom requeste, ale zdieľať non-thread-safe factory state. Database transaction môže rollbacknúť, zatiaľ čo external event už bol odoslaný. Image rollback môže byť nekompatibilný s custom JPA schema alebo persisted component configuration.

## 2. Exact extension subject

```yaml
extensionSubject:
  keycloak:
    version: 26.7.0
    imageDigest: sha256:2a81...
    optimizedBuildGeneration: kc-build-45
    deploymentGeneration: kc-2026-08-02-31
  provider:
    spiId: eventListener
    providerId: atlas-audit-kafka
    implementationVersion: 4.3.1
    sourceCommit: 9f8e2d7
    jar: atlas-keycloak-audit-4.3.1.jar
    jarSha256: 71cd...
    serviceDescriptor: META-INF/services/org.keycloak.events.EventListenerProviderFactory
    providerRegistryGeneration: registry-72
  dependencies:
    - artifact: kafka-clients-4.0.0.jar
      sha256: 4b0e...
    - artifact: atlas-audit-schema-2.1.0.jar
      sha256: aa93...
  configuration:
    providerEnabled: true
    configRevision: provider-config-58
    secretGeneration: audit-kafka-credential-18
  runtime:
    podUid: f31a...
    factoryInstanceGeneration: factory-10
    requestId: req-1402
    transactionId: tx-a19e...
  externalEffect:
    brokerCluster: audit-kafka-prod
    eventId: kc-event-80122
    schemaVersion: 2
```

Bez Keycloak target version a source/dependency hashes sa binary nedá reprodukovať. Bez SPI/provider ID sa neidentifikuje runtime selection. Bez build/provider-registry generation sa file-on-disk zamieňa s loaded providerom. Bez transaction a external event IDs sa retry/duplicate behavior nedá uzavrieť.

## 3. Najprv posúď, či custom kód treba

Preferuj built-in:

```text
client scopes a protocol mappers
authentication flow configuration
client policies
Authorization Services
LDAP/IdP mappers
Event Listener built-ins
Theme CSS/messages
Admin REST automation
```

Custom SPI je oprávnené, ak requirement nemožno bezpečne vyjadriť built-in contractom. Každá extension zväčšuje upgrade a security surface. „Je jednoduchšie napísať Java“ nie je business justification.

Decision record uvádza requirement, rejected built-in options, data/secret access, transaction semantics, external dependencies, ownera a retirement plan.

## 4. Provider a ProviderFactory

Typický SPI implementuje `Provider` a `ProviderFactory`:

```java
public final class AtlasAuditProvider implements EventListenerProvider {
    private final KeycloakSession session;
    private final AuditPublisher publisher;

    AtlasAuditProvider(KeycloakSession session, AuditPublisher publisher) {
        this.session = session;
        this.publisher = publisher;
    }

    @Override
    public void onEvent(Event event) {
        publisher.publish(AuditEnvelope.from(event, session));
    }

    @Override
    public void onEvent(AdminEvent event, boolean includeRepresentation) {
        publisher.publish(AuditEnvelope.from(event, includeRepresentation, session));
    }

    @Override
    public void close() {
    }
}
```

```java
public final class AtlasAuditProviderFactory
        implements EventListenerProviderFactory {

    private volatile AuditPublisher publisher;

    @Override
    public EventListenerProvider create(KeycloakSession session) {
        return new AtlasAuditProvider(session, publisher);
    }

    @Override
    public void init(Config.Scope config) {
        this.publisher = AuditPublisher.from(config);
    }

    @Override
    public void postInit(KeycloakSessionFactory factory) {
    }

    @Override
    public void close() {
        publisher.close();
    }

    @Override
    public String getId() {
        return "atlas-audit-kafka";
    }
}
```

Factory môže byť shared a concurrent; request provider typicky drží session-scoped state. Mutable factory fields musia byť thread-safe. `KeycloakSession` sa nesmie ukladať do static/factory state alebo používať mimo request/transaction lifecycle-u.

## 5. Service-loader registration

JAR musí obsahovať descriptor:

```text
META-INF/services/org.keycloak.events.EventListenerProviderFactory
```

Obsah:

```text
com.atlas.identity.audit.AtlasAuditProviderFactory
```

Custom SPI navyše registruje `org.keycloak.provider.Spi`. Typo alebo shading descriptorov môže provider skryť. CI rozbalí JAR a porovná expected descriptors/classes.

```bash
jar tf atlas-keycloak-audit-4.3.1.jar | sort
unzip -p atlas-keycloak-audit-4.3.1.jar \
  META-INF/services/org.keycloak.events.EventListenerProviderFactory
```

File existence nepreukazuje optimized registry alebo runtime selection.

## 6. Single a multiple provider types

Niektoré SPIs používajú jednu active/default implementation, iné umožňujú viac providers súčasne. EventListener môže mať viac listeners; hostname/email-template selection môže mať active provider.

```bash
bin/kc.sh build \
  --spi-email-template--provider=atlas-email

bin/kc.sh build \
  --spi-email-template--atlas-email--enabled=true
```

Provider ID musí zodpovedať `getId()`. Používaj dvojité `--` v canonical option formáte, aby build správne detegoval reaugmentation. Wrong selection môže ponechať built-in provider bez explicitného erroru, ak je fallback validný.

## 7. Packaging a optimized build

Provider artifact sa nestáva aktívnym iba skopírovaním JAR-u do filesystemu. Build musí spojiť exact Keycloak base, provider a dependency bytes, service descriptors a build-time SPI selection do jednej immutable optimized image generation. Až runtime registry a behavior test dokazujú, že nasadený server používa intended provider namiesto built-in fallbacku alebo stale predecessor registry.

```Dockerfile
FROM quay.io/keycloak/keycloak:26.7.0 AS builder
ENV KC_DB=postgres
COPY --chown=keycloak:keycloak target/atlas-keycloak-audit-4.3.1.jar /opt/keycloak/providers/
COPY --chown=keycloak:keycloak target/lib/kafka-clients-4.0.0.jar /opt/keycloak/providers/
RUN /opt/keycloak/bin/kc.sh build \
  --spi-events-listener--atlas-audit-kafka--enabled=true

FROM quay.io/keycloak/keycloak:26.7.0
COPY --from=builder /opt/keycloak/ /opt/keycloak/
ENTRYPOINT ["/opt/keycloak/bin/kc.sh"]
```

Pin base image digest a dependencies. Running `start --optimized` bez build po JAR change nepoužije current registry. Mutable volume injection do `providers/` po build je forbidden.

## 8. Single classloader a dependency conflicts

Provider JARs nie sú izolované classloadermi. Classes/resources môžu konfliktovať s Keycloak built-ins alebo inými providers; provider JARs môžu mať precedence. Untrusted JAR môže nahradiť library/resource a vykonať arbitrary server-process actions.

```text
same package/class v Keycloak a provider dependency
→ class-resolution ambiguity
→ startup alebo runtime incompatibility
```

Minimalizuj dependencies, používaj target Keycloak BOM/API a analyzuj duplicate classes/resources. Shading/relocation môže pomôcť pre third-party library, ale service descriptors, logging a security updates sa musia testovať.

```bash
find /opt/keycloak/providers -name '*.jar' -print0 \
  | xargs -0 sha256sum
```

## 9. Provider configuration a secrets

Configuration formát:

```text
spi-<spi-id>--<provider-id>--<property>
```

```bash
bin/kc.sh start --optimized \
  --spi-events-listener--atlas-audit-kafka--bootstrap-servers=audit-kafka:9093 \
  --spi-events-listener--atlas-audit-kafka--topic=keycloak-events
```

Secret nesmie byť CLI literal. Použi environment/keystore/Secret file a provider configuration resolution s redaction. `Config.Scope` value validation má fail-fast pri missing/invalid settings; silent defaults pre endpoint alebo tenant sú risk.

## 10. Lifecycle methods

Lifecycle určuje, ktoré resources sú process-wide, ktoré request-scoped a kedy je bezpečné ich vytvoriť alebo zatvoriť. Factory môže obsluhovať concurrent requests a nesie iba thread-safe shared state; provider instance používa konkrétny `KeycloakSession` a nesmie prežiť jeho transaction. Nasledujúce callbacks preto tvoria ownership a cleanup contract, nie iba poradie frameworkových metód.

```text
factory init
→ read immutable configuration a create shared resources

factory postInit
→ interact s initialized KeycloakSessionFactory/provider registry

factory create
→ request/session-scoped provider instance

provider close
→ request-scoped cleanup

factory close
→ shared resource shutdown
```

Provider nesmie spúšťať unmanaged non-daemon threads alebo leakovať clients/executors. Shutdown musí mať bounded timeout a nesmie blokovať graceful Pod termination.

## 11. Transaction boundary

Keycloak request beží v transaction lifecycle. Provider používa `KeycloakSession` a model APIs v correct transaction. External effect nie je súčasť database atomicity.

```text
DB/model mutation
→ EventListener publish
→ transaction commit alebo rollback
```

Listener timing môže vidieť event pred/po commit podľa SPI semantics; provider musí poznať contract. Pri critical delivery zváž outbox alebo after-completion callback, nie blind synchronous send v request thread-e.

```java
session.getTransactionManager().enlistAfterCompletion(
    new AbstractKeycloakTransaction() {
        @Override protected void commitImpl() {
            publisher.publish(envelope);
        }
        @Override protected void rollbackImpl() {
        }
    }
);
```

Konkrétne API/lifecycle treba overiť proti target version; internal helpers môžu byť unstable. External duplicate/retry potrebuje event ID a idempotent consumer.

## 12. Blocking a asynchronous behavior

Custom REST endpoints majú nasledovať blocking synchronous transaction-per-request model. `AsyncResponse`, `CompletableFuture` alebo `CompletionStage` nie sú supported path pre built-in transaction lifecycle.

Long external call v authentication/REST thread-e zvyšuje login latency a pool saturation. Timeout, circuit breaker a bulkhead musia byť bounded. Fire-and-forget thread môže stratiť context/event a uniknúť shutdownu.

## 13. Custom REST endpoints

Implementujú `RealmResourceProviderFactory` a `RealmResourceProvider`. JAX-RS resource potrebuje `META-INF/beans.xml` a `@jakarta.ws.rs.ext.Provider` podľa guide.

```java
@Path("atlas-audit-status")
@jakarta.ws.rs.ext.Provider
public final class AuditStatusResource {
    private final KeycloakSession session;

    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response status() {
        requireRealmAdmin(session);
        return Response.ok(Map.of("status", "ready")).build();
    }
}
```

Endpoint path, authentication a authorization musia byť explicitné. Realm path neznamená automatic admin protection. Validuj bearer token issuer/audience/client/roles alebo používaj Keycloak admin permission model. CORS, CSRF a rate limits sa riešia podľa caller type.

## 14. Custom JPA entities a schema

Provider môže pridať JPA entities/liquibase changes podľa extension API. Tým vzniká vlastná schema lifecycle a rollback boundary.

```text
provider version
→ changelog generation
→ migration owner
→ custom tables/data
→ provider/runtime compatibility
```

Provider uninstall bez data migration môže zanechať tables alebo orphan references. Keycloak DB backup musí zahŕňať custom schema. Provider rollback môže byť incompatible s successor data.

## 15. User Storage SPI

User Storage provider môže vyhľadávať users, validovať credentials a meniť external state. Capabilities určujú, ktoré methods Keycloak volá. External user ID stability, cache invalidation, transaction/external effect a federated-storage ownership sú critical.

```text
Keycloak lookup
→ provider external query
→ adapter model
→ optional imported local user
→ credential validation
→ cache/session/token
```

Provider nesmie vracať mutable username/email ako stable identity key. Timeout/failure policy nesmie fallbacknúť na nesprávneho usera alebo silently create local duplicate.

## 16. Authenticator a RequiredAction SPI

Custom authenticator vstupuje do login security path. `success()`, `challenge()`, `failure()` a attempted semantics musia zodpovedať flow requirement. Custom required action mutuje credential/profile/consent state a musí riešiť action-token/session descendants.

```text
condition false
→ skip branch according to flow contract

provider exception
→ fail closed pre privileged path
```

Provider UI/template musí byť CSP/accessibility compatible a chrániť secrets. Negative tests zahŕňajú replay, missing credential, cancelled action a remembered SSO.

## 17. Protocol mappers a token claims

Custom mapper je assertion authority. Claim name/type/audience/token placements a source ownership sú API pre consumers. Mapper musí byť deterministic a bounded; external lookup počas token issuance zvyšuje availability coupling.

```text
same user/client/session generation
→ same mapper inputs
→ stable claim type/semantics
```

Never publish secrets alebo unbounded group/resource lists. Mapper upgrade potrebuje old/new token fixture comparison a consumer compatibility.

## 18. Event Listener SPI

Listener môže spracovať User a Admin Events. Logovanie raw representation/tokens môže odhaliť secrets. Delivery semantics musia explicitne zvoliť sync/async, retry, duplicate, ordering, buffer a backpressure.

```text
listener broker unavailable
→ bounded timeout
→ explicit failure/drop metric
→ request impact podľa policy
```

Tiché dropy sú forbidden pre required audit. Synchronous hard dependency môže znefunkčniť login; rozhodnutie vychádza z audit/compliance objective.

## 19. Cache a cluster behavior

Provider shared state nesmie byť iba static JVM map, ak behavior musí byť cluster-wide. Použi Keycloak model/database, supported cache SPI alebo external system s consistency contractom.

```text
Pod A provider config/state mutation
→ authoritative store
→ invalidation/visibility
→ Pod B same result
```

Rolling upgrade s dvoma provider versions nad shared data potrebuje compatibility. Java serialization medzi versions je high risk.

## 20. Observability a redaction

Provider emituje:

```text
provider/version/build identity
request/realm/client correlation
latency a timeout
success/failure/drop/retry counts
external dependency state
transaction outcome correlation
```

Labels nesmú obsahovať user/session/token IDs s high cardinality alebo PII. Logs nesmú obsahovať passwords, OTP, authorization codes, refresh/access tokens, client secrets alebo full admin representations.

## 21. Testing ladder

Provider testovanie musí postupne zvyšovať realizmus, pretože compile ani mocked session neodhalia shared classloader, optimized registry, database transaction, cache alebo external backpressure behavior. Každý stupeň pridáva nový failure domain a uchováva exact target Keycloak/provider/dependency generation. Release môže prejsť až po node/upgrade a target-next-version rehearsal, nie po prvom úspešnom requeste.

```text
unit tests proti public SPI contracts
→ target-version compile
→ provider archive/descriptors/dependency scan
→ optimized image build
→ Keycloak startup/provider registry
→ positive/forbidden flow tests
→ transaction rollback/unknown external effect
→ concurrency/load/backpressure
→ node failure/rolling upgrade
→ target-next-version rehearsal
```

Mocked `KeycloakSession` tests nepreukazujú transaction/cache behavior. Testcontainers alebo isolated Keycloak/database/broker environment poskytuje integration proof.

## 22. Supply-chain a security

Provider repository má code owners, signed commits/releases, SBOM, dependency/license/vulnerability scans a artifact signing. Build runner nesmie mať production secrets. Runtime image policy pin-ne provider and base digests.

Untrusted provider JAR je equivalent arbitrary code execution v Keycloak process-e. There is no sandbox. Marketplace/download artifact sa nesmie inštalovať bez source/provenance/security review.

## 23. Upgrade a compatibility

Každý Keycloak upgrade rebuild-ne provider proti target version. Public SPI môže byť stabilnejšie než internal model classes, no migration guide je authority. Compile success nestačí; behavior tests a data migration sú mandatory.

```text
source Keycloak/provider generation
→ target compile/dependency diff
→ migration/data plan
→ mixed-version compatibility decision
→ canary/full rollout
```

Provider version sa uvádza v logs/health/metrics alebo custom info endpoint-e bez secrets. Admin Console Provider Info pomáha registry inventory, ale nie behavior proof.

## 24. Uninstall a rollback

Uninstall:

```text
stop usage/config references
→ migrate/retire data
→ remove JAR/dependencies
→ rebuild optimized image
→ rollout
→ verify provider absent a fallback intended
```

Odstránenie JAR bez build môže ponechať stale registry/build. Rollback providera musí zohľadniť schema/data/config changes a mixed Pods. Fallback na built-in provider môže zmeniť security semantics; explicitne testuj.

## 25. Incident `KC-PAY-79`

Atlas nasadil custom Event Listener a Realm REST endpoint v jednom JAR-e. Provider bundloval inú verziu Jacksonu a prebil built-in class. Startup prešiel, ale Admin REST serialization občas zlyhávala. Listener používal static non-thread-safe producer a pri broker outage-i vytváral unbounded queue v heap-e.

Custom REST endpoint bol pod realm pathom, no nekontroloval audience ani admin permissions; ľubovoľný validný realm token mohol čítať audit status s internal topology. Upgrade na 26.7 zmenil internal model method a prvý Admin Event vyvolal `NoSuchMethodError`. Image rollback vrátil JAR, ale custom database table zostala successor schema.

```text
single classloader conflict
+ unbounded async side effect
+ endpoint without explicit authorization
+ internal API dependency
+ provider/schema partial rollback
→ server-wide availability a privilege incident
```

Recovery odstránila conflicting dependency cez target BOM/relocation, zaviedla bounded delivery a explicitný event loss contract, endpoint admin authorization, public-SPI-only API review a provider-specific migration/rollback plan. Supply-chain gate teraz považuje provider za privileged server binary.

## 26. Evidence-preserving containment a recovery

Zachovaj source commit, build logs/SBOM/signatures, JAR/dependency hashes, service descriptors, Keycloak target version/image digest, provider configuration/secret generation, registry/startup logs, thread/heap evidence, database/custom schema state, events/request IDs a affected security/business operations.

Containment môže disable-nuť provider cez config/build successor, odobrať endpoint route alebo rollback-nuť entire known-compatible image. Neinjectuj live replacement JAR do running Podu. Recovery vytvorí immutable rebuilt image, reconciles data/external effects a vykoná second rollout.

## 27. Acceptance matrix

Positive:

```text
signed provider artifact
→ optimized build/registry
→ intended request/transaction
→ authoritative state/external effect once
```

Recovery:

```text
provider/dependency/external failure
→ bounded fail-safe behavior
→ immutable successor or compatible rollback
→ second request succeeds
```

Forbidden:

```text
untrusted JAR alebo mutable providers volume
→ supply-chain/admission rejects

custom endpoint bez explicit issuer/audience/permission
→ security test rejects

provider uses internal API bez approved compatibility plan
→ release gate rejects

unbounded thread/queue alebo secret logging
→ load/security gate rejects
```

Second-node test overí cluster consistency. Second-version test rebuildne a spustí provider na target-next Keycloak. Second-transaction test overí commit, rollback a duplicate external effect.

## Kontrolné otázky

- Je custom provider skutočne potrebný oproti built-in configuration?
- Ktorý exact SPI/provider ID, target Keycloak, source a dependency generation beží?
- Obsahuje JAR correct service descriptors a optimized registry?
- Je factory/provider state thread-safe a session/transaction-scoped?
- Čo sa stane s external effectom pri DB rollbacku alebo timeout-e?
- Má custom REST endpoint explicitnú authentication, audience a permission policy?
- Sú dependencies compatible so shared classloaderom?
- Používa provider public SPI alebo unstable internal APIs?
- Má vlastnú schema/cache/data migration a uninstall/rollback plan?
- Prešli concurrency, backpressure, node failure, upgrade, second-version a security testy?

## Primárne zdroje

- [Keycloak — Server Developer Guide](https://www.keycloak.org/docs/latest/server_development/)
- [Keycloak — Configuring providers](https://www.keycloak.org/server/configuration-provider)
- [Keycloak — Server Container Image](https://www.keycloak.org/server/containers)
- [Keycloak — Upgrading Guide](https://www.keycloak.org/docs/latest/upgrading/)
- [Keycloak — Configuring distributed caches](https://www.keycloak.org/server/caching)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Upgrades, migration guides a rollback boundaries](upgrades-migration-guides-rollback-boundaries.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Securing APIs, microservices a MCP servers cez Keycloak →](securing-apis-microservices-mcp-servers.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
