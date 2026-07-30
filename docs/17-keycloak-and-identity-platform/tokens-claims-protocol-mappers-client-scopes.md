# Tokens, claims, protocol mappers a client scopes

Keycloak token nie je všeobecný kontajner identity a permissions. Je to protokolový artifact vydaný konkrétnym realm issuerom pre konkrétny client, grant, subject, audience, scopes, session a mapper generation. Jeho signature dokazuje pôvod a integritu. Nedokazuje, že token obsahuje najmenší potrebný claim set, správnu audience, current tenant mapping ani authorization pre konkrétnu business operation.

```text
identity alebo workload authentication outcome
→ exact realm, client, grant a session subject
→ requested/default/optional client scopes
→ effective role scope mappings
→ protocol mapper evaluation
→ token type, audience a claim projection
→ signature a lifetime
→ client alebo resource-server validation
→ local tenant/resource authorization
→ refresh, revocation a second-token validation
```

Najdôležitejšia otázka nie je, či je JWT validný, ale prečo presne tento claim vznikol, pre ktorý consumer bol vydaný a či smie tento consumer podľa neho vykonať túto action.

## 1. Exact token subject

Token incident alebo acceptance verdict potrebuje realm issuer URL a deployment/configuration generation, client internal ID a `clientId`, grant type, authenticated principal, user/service-account/client session, requested `scope`, linked default a optional client scopes, dedicated client scope, effective protocol mappers, role scope mappings, signing key `kid`, token type, `iat/exp`, `aud`, `azp` alebo client identity, `sub`, `sid`, tenant a authorization claims.

Dva JWT s rovnakým `sub` môžu mať iný meaning, ak vznikli pre odlišný client, audience alebo session. Rovnaký mapper name môže mať inú configuration generation. Rovnaký realm role sa môže v jednom clientovi premietnuť do `realm_access`, v inom do custom claimu a v treťom sa nemusí objaviť vôbec.

```text
issuer atlas-payments-prod
+ client settlement-ops
+ grant client_credentials
+ service-account subject
+ effective scopes roles, atlas-common
+ mapper generation M-442
+ signing key kid K-31
→ access token T-991
```

## 2. Access token, ID token, refresh token a UserInfo

Access token je credential pre resource server. Resource server validuje issuer, signature, lifetime, token type, audience a local authorization inputs. Access token nemá byť používaný ako browser identity session len preto, že obsahuje meno alebo email.

ID token je OIDC statement pre client/Relying Party o authentication evente. Jeho audience je client. Nie je automaticky API authorization token. Claim, ktorý patrí iba API, nemá byť bez dôvodu kopírovaný do ID tokenu a vystavený browser/front-channel surface-u.

Refresh token umožňuje clientovi získať nové tokens podľa session, client a policy lifecycle-u. Nie je určený resource serveru. Je dlhšie žijúci a jeho theft alebo reuse má väčší blast radius. Rotation a revocation sa hodnotia podľa descendants, nie iba podľa jedného access tokenu.

UserInfo je endpoint chránený bearer access tokenom, ktorý vracia claims o authenticated userovi podľa OIDC contractu. Nie je náhradou za local resource authorization ani spôsobom, ako resource server spätne opraví nesprávnu audience.

Keycloak môže používať aj lightweight access tokens, ktoré redukujú PII a mapper-controlled claims. Aj lightweight token zostáva signed JWT s core claims. Consumer musí vedieť, či required claim získava z tokenu, introspection alebo token exchange flowu; nesmie ticho fallbacknúť na absent claim ako broad allow.

## 3. Claim authority a semantics

Claim môže pochádzať zo stable user ID, username/emailu, user attribute, group membership, realm role, client role, authentication session note, client session, service-account attribute, hardcoded mappera alebo external identity source. Každý source má inú authority, mutability a revocation latency.

`tenant_id=orion` je bezpečnostne významný iba vtedy, keď source je authoritative, mapping je unambiguous a resource server overí, že requested object patrí rovnakému tenantovi. User-editable profile attribute nie je tenant authorization. Email je mutable a recyklovateľný identifier. Group path môže byť organization projection, nie permission.

Claim contract uvádza name, JSON type, cardinality, source authority, normalization, token surfaces, absence semantics, privacy classification a consumer. String `admin` a array `[admin]` nie sú kompatibilné. Boolean `false` ako string môže byť truthy v chybnom consumerovi. Missing claim nesmie byť interpretovaný ako global scope.

## 4. Protocol mapper ako transformation boundary

Protocol mapper transformuje Keycloak identity/session/client context na OIDC claim alebo SAML attribute. Mappers môžu byť client-specific v dedicated client scope alebo shared cez realm client scope. Effective mapper set je union podľa linked scopes a requestu, nie iba to, čo administrator vidí v jednom Mappers tabu.

Mapper configuration rozhoduje o claim name, source, JSON type, multivalued behavior a surfaces ako access token, ID token, UserInfo, introspection alebo lightweight token. Pridať claim do všetkých surfaces pre istotu zvyšuje disclosure a coupling. API role v ID token-e môže viesť browser app k local UI authorizationu, ktorý sa rozíde s resource serverom.

Hardcoded audience mapper môže pridať resource server do `aud`. Audience Resolve mapper ju môže odvodiť z client roles, ktoré token skutočne obsahuje. Ani jeden mechanismus však nenahrádza explicitný service-to-service delegation model. Token s audiences `service1` aj `service2` môže byť použiteľný priamo voči obom services; ak to nie je intended, potrebný je užší initial token a token exchange/delegation boundary.

## 5. Client scopes: default, optional a dedicated

Client scope v Keycloak-e je reusable configuration pre protocol mappers a role scope mappings. Nie je totožný s OAuth Authorization Services resource scope a jeho názov v `scope` claim-e nemusí automaticky znamenať business permission.

Default client scope sa aplikuje pri token issuance vždy, keď je linked s clientom, bez ohľadu na requested OAuth `scope`. Optional client scope sa aplikuje iba vtedy, keď ho client requestne a subject je oprávnený ho použiť. Dedicated client scope reprezentuje mappers a role scope mappings priamo priradené konkrétnemu clientovi; v Admin Console je to abstraction nad client configuration a nemožno ho zdieľať s iným clientom.

Realm default client scopes sa automaticky linkujú novým clients. To je creation-time default, nie permanentná forced inheritance. Administrator ich môže odpojiť. Zmena shared default scope však môže zmeniť tokens mnohých existujúcich clients bez editovania každého clienta, preto potrebuje consumer inventory, compatibility test a staged rollout.

`Include in token scope` riadi, či sa scope name objaví v `scope` claim-e. Protocol mappers sa môžu aplikovať aj keď scope name nie je publikovaný. Consumer preto nemá inferovať complete mapper set iba z textového `scope` claimu.

## 6. Role scope mappings a `Full Scope Allowed`

Assigned role a projected role sú odlišné states. User alebo service account môže mať mnoho effective roles, no client má dostať iba intersection s role scope mappings. Client scopes môžu pridať ďalšie role scope mappings. Composite roles sa pri evaluation rozbalia.

`Full Scope Allowed` rozširuje scope tak, že client môže získať všetky role mappings subjectu. Je užitočný pre development, ale production least privilege vyžaduje explicitné role scopes. Vypnutie prepínača bez definovania scope mappings môže naopak odstrániť required roles; zmena potrebuje token fixtures a API canary.

Keycloak client-scope Evaluate view pomáha zobraziť effective mappers, role scopes a simulated access/ID/UserInfo outputs pre konkrétneho usera a requested optional scopes. Simulation je design evidence. Final acceptance stále potrebuje actual issued token pre exact grant a resource-server decision.

## 7. Audience, authorized party a resource server

`aud` identifikuje intended recipients. `azp` typicky identifikuje authorized party/client, ktorému bol token vydaný. Resource server nemá akceptovať token iba preto, že signature a `iss` sú validné. Musí byť intended audience a podľa threat modelu kontrolovať calling client, grant/machine identity, token type a tenant context.

Token vydaný web clientovi s `aud=settlement-api` nemusí automaticky oprávňovať web client na všetky API operations. Role/scope je iba jedna authorization dimension. API potrebuje action, resource, tenant, workflow/current state a risk context.

Broad audience je capability amplification. Service, ktorý dostane multi-audience bearer token, ho môže replaynúť voči ďalšiemu audience. Sender-constrained tokens, token exchange a service-specific scopes môžu blast radius znížiť, ale local authorization zostáva povinná.

## 8. Token lifetime, refresh a revocation evidence

Access token je self-contained snapshot. Odstránenie role alebo mappera nezmení už vydaný token. Client secret rotation zastaví nové client authentications so starým secretom, no už vydaný access token môže zostať platný do expiry alebo kým resource server nepoužije active introspection, not-before/epoch alebo explicitný deny mechanismus.

Krátky lifespan znižuje exposure, ale zvyšuje token request load a nevyrieši incorrect claim počas jeho platnosti. Refresh token môže vytvoriť nový token po configuration change podľa current session/policy semantics; incident tím musí sledovať refresh/offline descendants a local application/API caches.

Revocation acceptance obsahuje old-token denial na všetkých API replicas, new-token least privilege, refresh denial alebo corrected descendants a second issuance test. Admin Console session count nie je token revocation oracle.

## 9. Connected incident `KC-PAY-66`

Atlas client `settlement-ops` zmiešal desktop CLI, batch automation a API access. Client authentication bolo zapnuté, Standard Flow aj Service Accounts boli enabled a secret `s-ops-17` bol distribuovaný v CLI balíku `4.6`. Shared default scope `atlas-common` obsahoval mappery:

```text
user/service-account attribute tenant_id → tenant_id
realm roles → realm_access.roles
client roles → resource_access
hardcoded audience → settlement-api
```

Service-account user mal `tenant_id=orion` a composite realm role `settlement-operator`, ktorá zahŕňala client roles `settlement-api.reconcile` a `settlement-api.export`. Client mal `Full Scope Allowed`.

O `09:17 UTC` bol secret extrahovaný z CLI. O `09:21 UTC` útočník použil `client_credentials`. Vydaný token obsahoval `preferred_username=service-account-settlement-ops`, `aud=settlement-api`, `tenant_id=orion` a broad role projections. Resource server kontroloval signature, expiry, audience a role, ale nekontroloval expected machine client ani operation-specific tenant/resource binding.

Do revokácie credentials o `10:08 UTC` bolo dostupných `6 420` settlement records, `1 148` bolo exportovaných a `83` reconciliation commands bolo prijatých. Administrator pôvodne považoval browser MFA flow za ochranu clienta, no `client_credentials` neautentizuje human usera a browser flow sa na tento grant nevykonáva.

Root cause token projectionu bol mixed-purpose client, broad role scope, default shared mapper set a audience bez caller/action bindingu. Platné tokens presne reprezentovali nesprávny client contract.

## 10. Authoritative redesign a acceptance paths

Redesign oddeľuje clients. `settlement-ops-cli` je public interactive client bez client secretu a service accountu. `settlement-batch` je confidential machine client s private-key alebo mTLS/federated client authentication a jedinou client role `settlement.reconcile.batch`. `settlement-api` je resource-server/bearer-only registration bez interactive grants.

Dedicated scope `settlement-batch-api` pridáva access-token-only audience `settlement-api` a minimal machine claims. `Full Scope Allowed` je vypnuté. Tenant sa odvodzuje z authoritative service-account/client registration a resource server viaže `azp/client_id`, service-account `sub`, audience, role, tenant a requested operation/object.

Positive token fixture overí exact claims a absenciu unrelated roles/PII v ID token-e. Optional-scope test dokáže, že absent request nepridá mapper. Revocation test odmietne old secret aj old access token podľa incident policy. Wrong audience/client/tenant/action tests zlyhajú. Second client nedostane shared claims iba preto, že vznikol po realm default scope zmene.

## 11. Troubleshooting a anti-patterny

Pri missing alebo broad claim-e sa sleduje exact realm/client/grant/subject, linked default/optional scopes, requested `scope`, dedicated scope, effective role graph, `Full Scope Allowed`, mapper source/type/surfaces, actual token header/payload a resource-server decision log. Client-scope Evaluate sa porovná s actual issuance; rozdiel môže ukázať iný user, grant, optional scope alebo loaded configuration.

Anti-patterny sú: `valid JWT = authorized`, `scope text = complete mapper inventory`, `ID token ako API token`, `všetky roles do všetkých tokens`, `hardcoded multi-audience pre pohodlie`, `user attribute ako tenant authority`, `secret rotation = okamžitá token revokácia` a `Admin Console preview = runtime acceptance`.

## Glossary impact

Relevantné pojmy: Keycloak token subject, access token, ID token, refresh token, lightweight access token, claim authority, protocol mapper generation, default/optional/dedicated client scope, role scope mapping, Full Scope Allowed, effective mapper set, audience mapper, authorized party a token acceptance matrix.

## Primárne zdroje

- [Keycloak — Server Administration Guide: Protocol mappers, role mappings and client scopes](https://www.keycloak.org/docs/latest/server_admin/)
- [Keycloak — Securing applications and services with OpenID Connect](https://www.keycloak.org/securing-apps/oidc-layers)
- [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html)
- [RFC 9068 — JWT Profile for OAuth 2.0 Access Tokens](https://www.rfc-editor.org/rfc/rfc9068.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: SAML clients, metadata, assertions a bindings](saml-clients-metadata-assertions-bindings.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Public, confidential a bearer-only client model →](public-confidential-and-bearer-only-clients.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
