# Keycloak server configuration, hostname a reverse proxy

Keycloak server configuration neurčuje iba port a databázu. Určuje, z ktorých hodnôt vznikne issuer URL, authorization endpoint, token endpoint, action-token link, Admin Console URL, backchannel URL, management interface a trusted proxy identity. Chybný hostname alebo proxy-header model môže vytvoriť kryptograficky platné tokeny s nesprávnym issuerom, password-reset email s attacker-controlled hostom alebo Admin REST API dostupné cez verejnú cestu. Production acceptance preto sleduje exact configuration generation, loaded runtime options, edge/proxy generation, effective frontend a backchannel URLs a skutočne publikované routes.

Najčastejší omyl je považovať `--hostname` za kozmetický redirect setting. Hostname je protocol authority. Keycloak ho používa pri discovery metadata, token issueri, redirects a absolute links. Druhý omyl je predpokladať, že `--hostname-admin` zablokuje Admin REST API na frontend hoste. Tento option určuje generované admin URL, nie network access control. Oddelenie administration path musí presadiť reverse proxy, firewall alebo samostatná network boundary.

## 1. Dominantný configuration-to-endpoint lifecycle

```text
release a deployment intent
→ Keycloak binary/image a build-time option generation
→ configuration sources a precedence
→ runtime option resolution
→ hostname/frontend/backchannel/admin URL model
→ proxy mode, trusted headers a source-address validation
→ listener a management-interface binding
→ reverse-proxy route publication
→ discovery/action-link/token issuer output
→ browser, client a resource-server validation
→ rollout, rollback a second-endpoint test
```

Každá fáza má vlastný evidence boundary. `kc.conf` obsahuje intended value, ale environment variable alebo CLI option ju môže prepísať. Startup log môže ukázať resolved hostname, ale edge proxy môže posielať nesprávny `X-Forwarded-Proto`. Discovery dokument môže mať správny issuer, ale password-reset email môže byť generovaný z iného frontend contextu. Public login môže fungovať, zatiaľ čo backchannel alebo Admin Console používa nesprávnu cestu.

## 2. Exact server configuration subject

```yaml
serverConfigurationSubject:
  artifact:
    image: registry.atlas.example/identity/keycloak@sha256:9ce4...
    keycloakVersion: 26.7.0
    optimizedBuildGeneration: kc-build-37
    providerSetHash: sha256:814a...
  deployment:
    clusterUid: 27c7...
    namespace: identity-prod
    statefulSetUid: 63a1...
    podUid: a028...
    rolloutRevision: 52
  configuration:
    kcConfHash: sha256:51d2...
    environmentRevision: secret-config-83
    cliArgumentsRevision: args-41
    keystoreConfigGeneration: config-keystore-12
  endpoints:
    hostname: https://sso.atlas.example
    hostnameAdmin: https://sso-admin.atlas.example
    hostnameBackchannelDynamic: true
    httpRelativePath: /
    managementPort: 9000
  proxy:
    mode: reencrypt
    headers: xforwarded
    trustedAddresses: [10.40.12.0/24]
    loadBalancerRevision: edge-209
    routeSetRevision: routes-81
  operation:
    realm: atlas-prod
    clientId: settlement-admin-web
    requestId: req-1138
```

Bez image/build generation sa nedá zistiť, či option bol dostupný a zapracovaný do optimized buildu. Bez source precedence sa effective value iba odhaduje. Bez route generation nevieme, ktoré paths proxy skutočne publikoval. Bez Pod identity sa mixed rollout môže tváriť ako náhodný redirect loop.

## 3. Configuration sources a precedence

Keycloak číta configuration z viacerých sources. Praktický precedence model je:

```text
CLI options
→ environment variables
→ configuration keystore
→ conf/keycloak.conf
→ built-in defaults
```

Vyšší source prepíše nižší. Rovnaká hodnota môže mať odlišný názov podľa source-u:

```properties
# conf/keycloak.conf
hostname=https://sso.atlas.example
proxy-headers=xforwarded
http-enabled=true
```

```bash
export KC_HOSTNAME='https://sso.atlas.example'
export KC_PROXY_HEADERS='xforwarded'
export KC_HTTP_ENABLED='true'

bin/kc.sh start --hostname=https://sso-canary.atlas.example
```

Posledný CLI option vyhrá nad environment aj `kc.conf`. Incident evidence preto nesmie kopírovať iba ConfigMap. Musí zachytiť actual process arguments, environment source revisions a startup-resolved configuration.

Sensitive values ako database password alebo keystore password nepatria do command line ani plaintext ConfigMap. Configuration keystore a secret injection znižujú exposure, ale stále treba sledovať secret generation, mount/env delivery a process visibility.

## 4. Build-time a runtime options

Quarkus-based Keycloak rozlišuje build-time options a runtime options. Optimized image sa vytvára cez `kc.sh build`; následný `kc.sh start --optimized` predpokladá compatible build generation.

```bash
bin/kc.sh build \
  --db=postgres \
  --health-enabled=true \
  --metrics-enabled=true

bin/kc.sh start --optimized \
  --hostname=https://sso.atlas.example \
  --proxy-headers=xforwarded
```

Build command preukazuje intended augmentation inputs. Nepreukazuje image digest ani to, že runtime spustil práve tento build. Runtime option zmena nemá automaticky prebudovať provider/index generation. Pri custom providers/themes treba zachovať artifact set a build timestamp/digest.

Mixed fleet, kde časť Pods používa nový build a časť starý, môže mať odlišné endpoints alebo provider behavior. Rollout acceptance číta startup log a endpoint metadata z každého Pod cohortu.

## 5. Hostname v2 ako protocol authority

Explicitný `hostname` fixuje frontend authority. Môže byť iba hostname alebo úplná URL so scheme, portom a pathom. Production preferuje explicitnú URL tam, kde edge topology nie je triviálna.

```bash
bin/kc.sh start \
  --hostname=https://sso.atlas.example
```

Discovery read-back:

```bash
curl --fail --silent \
  https://sso.atlas.example/realms/atlas-prod/.well-known/openid-configuration \
  | jq '{issuer,authorization_endpoint,token_endpoint,jwks_uri,end_session_endpoint}'
```

Tento output preukazuje externally visible OIDC metadata pre daný route a realm. Nepreukazuje, že všetky Pods generujú rovnakú hodnotu, že SAML metadata alebo email links sú correct ani že resource servers prijímajú issuer.

Explicitný hostname bráni tomu, aby untrusted `Host` header určoval issuer alebo action-link origin. Dynamic hostname model zvyšuje flexibility, ale rozširuje trust na proxy/headers a potrebuje striktnejšie source validation.

## 6. Admin hostname a network isolation

```bash
bin/kc.sh start \
  --hostname=https://sso.atlas.example \
  --hostname-admin=https://sso-admin.atlas.example
```

`hostname-admin` určuje generated Admin Console a administration URL. Nezakazuje `/admin/` na frontend listeneri. Reverse proxy musí publikovať admin paths iba na admin hoste a z trusted networku.

```text
public host sso.atlas.example
→ publish /realms/, /resources/ a intended broker paths
→ reject /admin/ a management paths

admin host sso-admin.atlas.example
→ publish required admin paths
→ require corporate network/mTLS/access proxy
```

Security test musí skúsiť Admin REST API priamo cez public hostname, alternate Host header, origin address a NodePort/Ingress bypass. UI redirect na admin host nie je access-control proof.

## 7. Backchannel hostname

Backchannel endpoints používajú server-to-server clients. `hostname-backchannel-dynamic=true` umožní dynamické backchannel URLs, ale vyžaduje explicitný frontend hostname. Consumer musí stále validovať issuer podľa realm contractu.

```bash
bin/kc.sh start \
  --hostname=https://sso.atlas.example \
  --hostname-backchannel-dynamic=true
```

Internal backchannel optimalizácia nesmie meniť issuer identity. Token endpoint môže byť internou cestou dostupný na inom network endpoint-e, ale issued token `iss` zostáva canonical realm issuer. Split-horizon DNS alebo service mesh musí zachovať TLS name/trust contract.

Acceptance testuje external browser discovery, internal client token request, resource-server issuer validation a failover na druhý network path.

## 8. Reverse-proxy termination modes

Tri základné topológie:

```text
reencrypt
client TLS → proxy TLS termination → nový TLS → Keycloak HTTPS

edge
client TLS → proxy TLS termination → HTTP → Keycloak HTTP

passthrough
client TLS → proxy TCP pass-through → Keycloak TLS termination
```

Re-encrypt zachová encryption aj medzi proxy a Keycloakom a je preferovaný pre untrusted/shared network. Edge vyžaduje `http-enabled=true` a trusted internal network. Passthrough znamená, že Keycloak vidí TLS priamo; HTTP proxy headers sa typicky nepoužívajú.

```bash
# Edge termination
bin/kc.sh start \
  --hostname=https://sso.atlas.example \
  --http-enabled=true \
  --proxy-headers=xforwarded
```

`http-enabled=true` nesmie náhodne publikovať port 8080 mimo trusted proxy network. NetworkPolicy/security group musí povoliť iba edge proxy cohort.

## 9. Forwarded a X-Forwarded headers

`proxy-headers=forwarded` používa RFC 7239 `Forwarded`. `proxy-headers=xforwarded` používa `X-Forwarded-For`, `X-Forwarded-Proto`, `X-Forwarded-Host` a `X-Forwarded-Port`.

```bash
bin/kc.sh start --proxy-headers=xforwarded
```

Proxy musí odstrániť inbound client-supplied forwarding headers a zapísať vlastné authoritative values. Pri X-Forwarded modeli má `X-Forwarded-Port` prioritu pred portom v `X-Forwarded-Host`; nesprávna hodnota vedie k redirectom na interný port.

```nginx
proxy_set_header Host $host;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_set_header X-Forwarded-Host $host;
proxy_set_header X-Forwarded-Port $server_port;
```

Tento snippet nie je bezpečný verdict bez `proxy-trusted-addresses`, source-network boundary a header overwrite behavioru konkrétneho proxy/load balancera.

## 10. Trusted proxy addresses

`proxy-trusted-addresses` obmedzuje, od ktorých source IPs Keycloak dôveruje proxy headers.

```bash
bin/kc.sh start \
  --proxy-headers=xforwarded \
  --proxy-trusted-addresses=10.40.12.0/24,10.40.18.11
```

CIDR musí reprezentovať actual last-hop proxy addresses, nie celý VPC. Pri proxy chain-e treba vedieť, ktorý hop prepíše headers a z akej adresy sa pripája ku Keycloaku. NAT, mesh sidecar alebo ingress controller upgrade môže source identity zmeniť.

Negative test posiela spoofed `X-Forwarded-Proto/Host/For` priamo z untrusted Podu a očakáva, že neovplyvní generated URL ani client IP evidence.

## 11. Context path a forwarded prefix

Ak Keycloak beží pod `/auth`, konfigurácia musí byť konzistentná:

```bash
bin/kc.sh start \
  --hostname=https://sso.atlas.example/auth \
  --http-relative-path=/auth
```

Alternatívne proxy môže používať `X-Forwarded-Prefix`, ak je zvolený proxy-header model a server ho dôveryhodne spracuje. Nejasná kombinácia rewrite-u, relative path a hostname pathu spôsobuje redirect loop, broken resources a nesprávne action links.

Acceptance číta discovery, SAML metadata, login form action, email action link, account/admin resources a logout redirect cez external aj internal route.

## 12. Public endpoint allowlist

Production reverse proxy nemá publikovať všetky Keycloak paths. Verejne potrebné sú najmä realm protocol endpoints a static resources. Admin a management endpoints patria do oddelenej boundary.

```text
public allowlist
/realms/<realm>/...
/resources/...
/robots.txt podľa potreby

restricted
/admin/...
/metrics
/health
/health/*
/realms/master/... podľa architecture
```

Presná allowlist závisí od OIDC/SAML/broker/registration features. Overly broad deny môže rozbiť backchannel logout alebo broker callback; overly broad allow zverejní management/admin surface. Test musí byť feature-specific.

Management interface default port `9000` sa nemá proxyovať na public host. Ak `http-management-relative-path` alebo port zmeníš, monitoring a security rules musia sledovať successor values.

## 13. PROXY protocol

L4 load balancer môže preniesť source address cez PROXY protocol:

```bash
bin/kc.sh start --proxy-protocol-enabled=true
```

PROXY protocol nie je HTTP header. Listener očakáva binary/text preamble pred TLS/HTTP. Pri passthrough topology môže byť vhodný, ale nesmie sa bez validácie kombinovať s HTTP proxy-header trust modelom. Priamy client bez PROXY preamble zlyhá; untrusted source nesmie mať direct access na listener.

Acceptance zahŕňa correct load balancer, direct connection rejection, source IP read-back a failover listener.

## 14. Sticky sessions, draining a topology

Keycloak môže fungovať bez sticky sessions v podporovanom cluster modeli, ale affinity znižuje remote cache access a latency. Sticky cookie alebo load-balancer policy nesmie byť použitá ako náhrada správnej cluster/session configuration.

Rollout:

```text
mark Pod unready
→ stop new connections
→ drain existing requests
→ preserve/distribute session state podľa cache modelu
→ terminate Pod
→ clients retry na successor Pod
```

Load balancer health môže byť green skôr než realm caches/providers sú operational. Readiness, graceful shutdown a rollout surge/unavailable settings musia byť testované s active authorization code, login session, refresh token a backchannel requestom.

## 15. Hostname debug a read-back

Hostname debug page sa zapína iba dočasne:

```bash
bin/kc.sh start \
  --hostname-debug=true
```

Potom je dostupná debug informácia pod realm hostname pathom. Môže odhaliť request/header/topology details, preto sa po diagnostike vypína a nesmie byť verejne ponechaná.

Praktický read-back zahŕňa:

```bash
curl -skI https://sso.atlas.example/realms/atlas-prod/account
curl -sk https://sso.atlas.example/realms/atlas-prod/.well-known/openid-configuration | jq .issuer
curl -skI https://sso.atlas.example/admin/
curl -skI https://sso-admin.atlas.example/admin/
curl -skI https://sso.atlas.example/metrics
```

`-k` je iba diagnostický príklad na oddelenie route od trust failure; production acceptance musí prejsť bez vypnutej TLS validácie.

## 16. Incident `KC-PAY-71`

Atlas migroval z edge proxy na re-encrypt, ale ponechal `KC_PROXY_HEADERS=xforwarded` a trustoval celý VPC CIDR. Jeden internal workload sa pripojil priamo na Keycloak service, poslal `X-Forwarded-Host: attacker.example` a vyvolal password-reset email s nesprávnym absolute linkom. Explicitný `hostname` nebol nastavený.

Admin Console používala `hostname-admin`, no public ingress stále publikoval `/admin/`. Operátori považovali redirect na admin host za izoláciu. Navyše `X-Forwarded-Port: 8443` prepisoval external port 443 a OIDC callbacky sa náhodne vracali na interný port.

```text
broad trusted proxy range + dynamic hostname
→ spoofed forwarding headers
→ incorrect action-link origin

hostname-admin bez route isolation
→ public Admin REST exposure

wrong forwarded port
→ redirect mismatch a login failures
```

Recovery nastavila explicitný frontend hostname, zúžila trusted addresses na ingress Pods, zakázala direct service access, opravila header overwrite a port, oddelila admin ingress a management port. Second-proxy test zopakoval journeys cez každý ingress/load-balancer cohort aj z untrusted Podu.

## 17. Evidence-preserving recovery

Zachovaj image/build digest, `kc.conf`, environment/CLI source revisions, process args, startup resolved config, hostname debug output, discovery/SAML metadata, proxy/load-balancer config a version, route inventory, trusted-source CIDRs, raw forwarded headers, certificate/SNI, DNS answers a affected action-link/token issuer hashes.

Containment môže zablokovať direct service access, stiahnuť admin/public routes, zúžiť proxy trust a pozastaviť email action links. Recovery nasadí successor server/proxy configuration ako coordinated generation, canary-nuje route a následne overí issuer, redirects, email links, admin isolation, management isolation a backchannel.

## 18. Acceptance matrix

Positive:

```text
external browser login
→ canonical issuer/redirect/action URLs
→ callback succeeds
→ token issuer accepted
```

Recovery:

```text
proxy alebo Pod failover
→ same public/admin/backchannel authority
→ active journey retry succeeds
→ no mixed generation
```

Forbidden:

```text
spoofed Host/X-Forwarded headers z untrusted source
→ no URL/client-IP influence

public /admin, :9000, /metrics alebo /health
→ network/proxy reject

direct port 8080/8443 bypass mimo intended path
→ reject
```

Second-proxy test vykoná login, reset email, Admin API a backchannel token request cez každý edge cohort. Second-Pod test porovná discovery a generated links z každého rollout revision.

## Kontrolné otázky

- Ktoré configuration sources existujú a ktorý má precedence?
- Ktoré options sú build-time a ktorý image ich obsahuje?
- Je hostname explicitná protocol authority?
- Oddeľuje hostname-admin URL generation od skutočného network isolationu?
- Ktorý proxy mode a header model sa používa?
- Ktoré exact source addresses smú určovať forwarded headers?
- Je port/path rewrite konzistentný v discovery, forms, emails a logout?
- Sú management/admin/direct listeners neverejné?
- Prešli spoofed-header, wrong-port, alternate-host, direct-service, proxy-failover a second-Pod tests?

## Primárne zdroje

- [Keycloak — Configuring Keycloak](https://www.keycloak.org/server/configuration)
- [Keycloak — Configuring the hostname](https://www.keycloak.org/server/hostname)
- [Keycloak — Using a reverse proxy](https://www.keycloak.org/server/reverseproxy)
- [Keycloak — Management interface](https://www.keycloak.org/server/management-interface)
- [Keycloak — Configuring Keycloak for production](https://www.keycloak.org/server/configuration-production)
- [RFC 7239 — Forwarded HTTP Extension](https://www.rfc-editor.org/rfc/rfc7239.html)
