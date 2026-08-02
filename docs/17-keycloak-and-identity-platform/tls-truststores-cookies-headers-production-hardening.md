# TLS, truststores, cookies, headers a production hardening

Production Keycloak hardening nie je jeden prepínač `HTTPS=true`. Inbound TLS určuje, ako Keycloak alebo reverse proxy preukazuje server identity klientom. Outbound truststore určuje, ktorým certifikačným autoritám Keycloak dôveruje pri LDAP, SMTP, identity brokeringu, token exchange alebo webhook/plugin komunikácii. Browser cookies reprezentujú session continuity a security headers obmedzujú, ako môže browser stránku načítať, vložiť alebo odoslať. Tieto vrstvy majú odlišné keys, stores, rotation a failure modes.

Najčastejší incident vznikne pri nesprávnom spájaní hraníc. Import internej CA do outbound truststore neopraví certificate chain, ktorý Keycloak prezentuje browseru. Rotácia HTTPS certificate nezruší user sessions ani už vydané tokens. `Secure` cookie nie je bezpečná, ak proxy podvrhne scheme alebo ak je HTTP listener verejne dostupný. CSP header nepomôže, ak custom theme načítava untrusted script cez povolenú domain. Production acceptance preto fixuje exact certificate/key/truststore generation, proxy termination mode, hostname, cookie attributes, header policy, management listener a session/token descendants.

## 1. Dominantný trust-to-session lifecycle

```text
release a security intent
→ exact Keycloak image/configuration generation
→ inbound certificate/private-key alebo keystore generation
→ proxy TLS termination/re-encryption/passthrough path
→ browser/client certificate and hostname validation
→ Keycloak request scheme/host resolution
→ security-header a cookie generation
→ authentication/user/client session
→ access/refresh/offline token descendants
→ outbound TLS call a truststore validation
→ certificate/trust rotation
→ session/token/application acceptance po rotácii
```

Úspešný TLS handshake preukazuje iba vyjednaný transport medzi dvoma endpoints. Nepreukazuje correct realm issuer, client authorization, cookie policy ani downstream business operation. Úspešný outbound LDAP handshake nepreukazuje správnu directory identity alebo mapper result. Security verdict musí prepájať transport, identity a application layers bez ich zlievania.

## 2. Exact hardening subject

```yaml
hardeningSubject:
  keycloak:
    deploymentGeneration: kc-2026-08-02-20
    imageDigest: sha256:9ce4...
    version: 26.7.0
    realm: atlas-prod
    hostname: https://sso.atlas.example
  inboundTls:
    termination: reencrypt
    edgeCertificateGeneration: edge-cert-88
    edgeCertificateFingerprint: sha256:71a2...
    keycloakCertificateGeneration: kc-cert-31
    keycloakCertificateFingerprint: sha256:2c7e...
    keycloakPrivateKeyGeneration: kc-key-31
    protocols: [TLSv1.3, TLSv1.2]
    cipherPolicyRevision: tls-policy-17
  outboundTrust:
    truststoreGeneration: trust-42
    truststoreHash: sha256:4d83...
    trustedCaSubjects:
      - CN=Atlas Internal Root CA 02
      - CN=Corporate Partner Issuing CA 07
  browser:
    proxyRevision: edge-209
    cookiePolicyRevision: cookie-16
    headerPolicyRevision: headers-28
    themeArtifact: atlas-keycloak-theme-7.4.1@sha256:7f2e...
  management:
    port: 9000
    externallyPublished: false
    certificateGeneration: mgmt-cert-12
  operation:
    clientId: settlement-admin-web
    userSessionId: 4c71...
    tokenJti: 91ae...
    requestId: req-1244
```

Bez certificate fingerprint sa názov Secretu nedá spojiť s bytes prezentovanými na wire. Bez private-key generation nevieme, či všetky Pods používajú successor key. Bez truststore content inventory sa `truststore updated` nedá odlíšiť od importu nesprávneho CA. Bez proxy/header generation sa cookie a redirect behavior iba odhaduje.

## 3. Inbound TLS: PEM a keystore

Keycloak môže načítať certificate a private key ako PEM:

```bash
bin/kc.sh start \
  --https-certificate-file=/etc/keycloak/tls/tls.crt \
  --https-certificate-key-file=/etc/keycloak/tls/tls.key
```

Alebo z keystore:

```bash
bin/kc.sh start \
  --https-key-store-file=/etc/keycloak/tls/keycloak.p12 \
  --https-key-store-password="${KC_HTTPS_KEY_STORE_PASSWORD}" \
  --https-key-store-type=PKCS12
```

Ak sú configured PEM files aj keystore, explicitný PEM certificate/key path má prednosť pre server identity. Deployment contract nemá poskytovať oba modely bez zámeru; komplikuje to rotáciu a incident read-back.

Certificate file musí obsahovať complete server chain v správnom poradí podľa deployment contractu. Private key musí patriť k leaf certificate. Key permissions a mount ownership musia obmedziť read access na Keycloak process.

```bash
openssl x509 -in tls.crt -noout -subject -issuer -serial -dates -fingerprint -sha256
openssl pkey -in tls.key -pubout -outform DER | sha256sum
openssl x509 -in tls.crt -pubkey -noout \
  | openssl pkey -pubin -outform DER \
  | sha256sum
```

Zhodné public-key hashes preukazujú key/certificate pair. Nepreukazujú, že running Pod načítal tieto files alebo že edge proxy prezentuje rovnaký certificate.

## 4. TLS protocols, ciphers a client compatibility

Production policy typicky povoľuje TLS 1.3 a TLS 1.2 a zakazuje deprecated protocols. Cipher configuration musí byť kompatibilná s JVM/providerom a intended clients.

```bash
bin/kc.sh start \
  --https-protocols=TLSv1.3,TLSv1.2 \
  --https-cipher-suites=TLS_AES_256_GCM_SHA384,TLS_AES_128_GCM_SHA256,TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
```

Hardcoded cipher allowlist sa môže stať nekompatibilnou po JDK alebo Keycloak upgrade. Policy má mať ownera, client matrix a review cadence. FIPS alebo custom security provider mení available algorithms a potrebuje samostatný build/runtime evidence.

```bash
openssl s_client -connect sso.atlas.example:443 \
  -servername sso.atlas.example \
  -tls1_3 </dev/null

openssl s_client -connect sso.atlas.example:443 \
  -servername sso.atlas.example \
  -tls1_2 </dev/null
```

Handshake output preukazuje external listener negotiation pre konkrétnu route. Re-encrypt topology vyžaduje samostatný test proxy → Keycloak backend TLS.

## 5. Certificate hostname a chain validation

Client validuje certificate chain, validity interval, key usage a hostname/SAN. Canonical hostname `sso.atlas.example` musí byť v SAN certificate, ktorý prezentuje external edge. Backend certificate musí zodpovedať SNI/name, ktorý používa proxy pri re-encryption, alebo musí mať explicitný internal trust/name contract.

```text
external client
→ validates edge certificate for sso.atlas.example

reverse proxy
→ validates Keycloak backend certificate for keycloak.identity-prod.svc alebo configured SNI
```

Proxy option `verify none` alebo application `-k` odstraňuje backend server-authentication boundary a nemá byť production recovery. Private CA je legitímna iba vtedy, keď je presne importovaná do proxy/client truststore a certificate name sa validuje.

## 6. Certificate rotation

Safe rotation má predecessor a successor generation:

```text
publish successor certificate/key
→ ensure trust chain is already trusted
→ roll or reload controlled server/proxy cohort
→ wire read-back fingerprint per endpoint/Pod
→ test old and new client cohorts
→ retire predecessor key/certificate
```

Nie každá Keycloak/TLS configuration sa automaticky hot-reloadne v každom deployment modeli. Ak contract vyžaduje restart/rollout, plán musí počítať s active sessions a graceful draining. Secret update bez Pod rollout nemusí zmeniť certificate na wire.

Certificate rotation nemení signing keys realm-u, token issuer ani sessions. Naopak realm signing-key rotation nemení HTTPS certificate. Incidenty musia tieto key families odlíšiť.

## 7. Reverse-proxy TLS modes

Re-encrypt, edge a passthrough majú odlišné responsibilities:

```text
reencrypt
edge owns public certificate
Keycloak owns backend certificate
proxy validates backend identity

edge
edge owns public certificate
Keycloak receives trusted HTTP
network isolation protects backend

passthrough
Keycloak owns public certificate
L4 proxy nevidí HTTP headers/path
```

Pri edge termination musí byť `http-enabled=true`, ale backend HTTP listener nesmie byť dostupný mimo proxy network. Pri passthrough sa `proxy-headers` nepoužívajú ako náhrada L4 source identity; podľa potreby sa používa PROXY protocol.

HSTS patrí na external HTTPS response. Ak ho nastavuje proxy aj Keycloak, výsledná policy musí byť deterministická a testovaná. Duplicated/conflicting headers môžu mať neočakávanú browser semantics.

## 8. Outbound truststore

Keycloak používa truststore pri outbound HTTPS/LDAPS/SMTP TLS connections podľa subsystemu a configured Java/Keycloak trust modelu. Truststore obsahuje CA certificates, nie server private keys.

```bash
bin/kc.sh start \
  --truststore-paths=/etc/keycloak/trust/atlas-root-ca.pem,/etc/keycloak/trust/partners.p12 \
  --truststore-password="${KC_TRUSTSTORE_PASSWORD}"
```

`truststore-paths` môže načítať files alebo directories. Inventory musí zafixovať obsah, typ a hashes. Broad import celého corporate CA bundle zväčšuje trust domain pre každý outbound subsystem, ktorý store používa.

```bash
keytool -list -v \
  -keystore /etc/keycloak/trust/partners.p12 \
  -storepass "${KC_TRUSTSTORE_PASSWORD}" \
  | grep -E 'Alias name:|Owner:|Issuer:|Serial number:|SHA256:'
```

Výpis preukazuje store content na filesysteme. Nepreukazuje, že running process ho načítal alebo že konkrétny provider používa tento truststore namiesto vlastného override-u.

## 9. Outbound HTTP client a subsystem overrides

Identity providers, token exchange, UserInfo, remote JWKS a custom providers používajú outbound HTTP client. LDAP a SMTP môžu mať vlastné TLS settings. X.509 client authentication alebo mTLS môže potrebovať client keystore s private keyom, čo je iný artifact než CA truststore.

```text
outbound server authentication
→ truststore/hostname validation

outbound client authentication
→ client certificate/private key generation
```

Nesprávne spojenie vedie k importu private keys do broad store alebo k vypnutiu hostname validation. Každý external dependency má mať expected DNS name, CA chain, optional client certificate, timeout a retry contract.

## 10. Management-interface TLS

Management interface default port `9000` môže dediť main HTTPS configuration alebo mať samostatné certificate/key/trust settings podľa deployment configuration. Oddelený management certificate je vhodný, ak monitoring používa internú PKI.

```text
public frontend :8443 alebo proxy :443
→ public certificate/route contract

management :9000
→ internal monitoring certificate/route contract
→ never public
```

Ak monitoring klient nedôveruje management CA, scrape/health zlyhá. Riešením je správny CA trust, nie `insecureSkipVerify`. Management listener nemá hostovať Admin Console ani public protocol endpoints.

## 11. Client certificate a X.509 authentication

Pri X.509 user authentication môže TLS terminovať priamo na Keycloaku alebo na reverse proxy. Ak proxy forwarduje client certificate v headeri, Keycloak dôveruje proxy ako assertion authority. Proxy musí validovať certificate chain a odstrániť inbound spoofed certificate headers.

```text
client certificate
→ trusted proxy mTLS validation
→ canonical forwarded certificate header
→ Keycloak X.509 authenticator
→ user identity mapping
```

Broad trusted proxy range alebo neodstránený header umožní spoofing. Certificate subject/issuer mapping na usera musí byť explicitný a unikátny. Revoked certificate behavior závisí od CRL/OCSP alebo upstream validation contractu.

Forbidden test pošle forged certificate header z untrusted workloadu a musí zlyhať pred user mappingom.

## 12. Keycloak session cookies

Keycloak používa viac cookies pre authentication transaction, user session, identity a restart/remember-me flows. Presné names a semantics sa môžu meniť medzi verziami; policy sa má overovať na wire, nie iba podľa historického zoznamu.

Security attributes:

```text
Secure
→ browser posiela cookie iba cez HTTPS

HttpOnly
→ client-side JavaScript ju nevie čítať

SameSite
→ obmedzuje cross-site cookie sending podľa flow contractu

Path/Domain
→ určuje endpoint scope
```

OIDC/SAML/broker redirects sú cross-site journeys. Príliš striktné SameSite nastavenie môže rozbiť legitimate callback; príliš voľné nastavenie zväčšuje CSRF surface. Keycloak a browser používajú transaction-bound `state`, `nonce`, SAML request correlation a cookies spolu.

```bash
curl -skD - -o /dev/null \
  'https://sso.atlas.example/realms/atlas-prod/protocol/openid-connect/auth?client_id=settlement-admin-web&response_type=code&scope=openid&redirect_uri=https%3A%2F%2Fsettlement-admin.atlas.example%2Foauth%2Fcallback&state=test&nonce=test&code_challenge=test&code_challenge_method=S256' \
  | grep -i '^set-cookie:'
```

Tento diagnostic request nepreukazuje complete valid authorization flow. Používa sa iba na attribute inspection v non-production test realm-e.

## 13. Proxy scheme a Secure cookies

Keycloak musí správne vedieť, že external request je HTTPS. Pri edge termination to pochádza z trusted `Forwarded` alebo `X-Forwarded-Proto`. Ak proxy pošle `http`, cookies alebo redirects môžu byť nesprávne. Ak Keycloak dôveruje spoofed headeru, attacker môže ovplyvniť scheme/client IP.

```text
external HTTPS
→ proxy overwrites X-Forwarded-Proto=https
→ Keycloak trusts only proxy source
→ Secure cookies a https redirects
```

Acceptance testuje external route, direct backend route, spoofed headers a alternate proxy cohort. Browser DevTools screenshot nestačí; raw `Set-Cookie` headers a actual cookie sending behavior sú potrebné.

## 14. Security headers

Keycloak realm security defenses a reverse proxy môžu nastavovať headers ako:

```text
Content-Security-Policy
Content-Security-Policy-Report-Only
X-Frame-Options alebo frame-ancestors v CSP
Strict-Transport-Security
X-Content-Type-Options
Referrer-Policy
```

CSP musí pokryť custom theme resources a nesmie byť oslabená broad `*`, `unsafe-eval` alebo neobmedzenými external scripts. Clickjacking defense musí zodpovedať intended iframe use; Admin/login pages sa typicky nemajú vkladať do cudzích origins. HSTS má zmysel iba na HTTPS hostname a jeho dlhý max-age/includeSubDomains/preload má vysoký rollback cost.

```bash
curl --fail --silent --show-error -D - -o /dev/null \
  https://sso.atlas.example/realms/atlas-prod/account \
  | grep -Ei '^(content-security-policy|strict-transport-security|x-frame-options|x-content-type-options|referrer-policy):'
```

Header existence nepreukazuje effective browser behavior. CSP report-only neblokuje. Conflicting duplicate CSP headers sa kombinujú reštriktívne a môžu rozbiť page. Proxy rewrite môže odstrániť Keycloak header alebo pridať slabší/odlišný policy set.

## 15. CORS, origins a headers nie sú jedno

CORS na clientovi určuje, ktoré browser origins môžu čítať cross-origin responses. Nie je náhradou redirect URI allowlistu, CSP, SameSite cookies ani resource-server authorization.

```text
redirect URI
→ kam authorization server smie poslať browser response

web origins/CORS
→ ktorý browser origin smie čítať response

CSP
→ odkiaľ stránka smie načítať resources a kam smie odosielať

cookie SameSite
→ kedy browser pripojí cookie pri cross-site requeste
```

Wildcard Web Origins alebo `+` inheritance musí byť reviewované spolu s redirect URIs a actual frontend architecture.

## 16. Secrets, private keys a filesystem hardening

Private keys, keystore passwords, truststore passwords, database credentials a SMTP/client secrets patria do controlled secret store. Environment variables môžu byť viditeľné v process/container diagnostics; CLI arguments v process listing a logs. Mounted files potrebujú restrictive mode, ownership a read-only filesystem/mount.

```text
secret source generation
→ encrypted storage
→ workload identity authorization
→ bounded delivery
→ mounted file alebo process configuration
→ no log/history/image-layer exposure
→ rotation a predecessor retirement
```

Base image a container runtime hardening zahŕňa non-root user, read-only filesystem kde je kompatibilný, minimal capabilities, immutable providers/themes, controlled `/opt/keycloak/data`, network egress allowlist a oddelené admin/management routes.

## 17. Session a token descendants po security zmene

TLS certificate rotation nemení Keycloak sessions. Cookie policy zmena nemusí invalidovať už uložené browser cookies. Client secret alebo realm signing-key rotation má vlastné descendants. Incident closure preto mapuje:

```text
HTTPS certificate/key descendants
→ live listeners a client TLS caches

cookie/header policy descendants
→ existing browser cookies, pages a service-worker/cache state

realm/client security descendants
→ user sessions, client sessions, refresh/offline/access tokens

application descendants
→ local sessions a business operations
```

Pri compromise server TLS private key môže byť potrebná certificate revocation a incident response, ale token signing keys nie sú automaticky kompromitované. Pri compromise signing key je HTTPS rotation nedostatočná.

## 18. Incident `KC-PAY-72`

Atlas edge proxy prezentoval nový public certificate, ale re-encrypt backend stále akceptoval Keycloak certificate bez hostname validation. Útočník s accessom do shared internal networku presmeroval backend connection na vlastný TLS endpoint s certificate od rovnakej broad corporate CA.

Outbound truststore obsahoval celú corporate root hierarchy. Custom identity-provider hostname bol chybne prekonfigurovaný na attacker-controlled internal DNS name, ale TLS validation prešla. Zároveň public ingress prepísal CSP na `default-src * 'unsafe-inline'`, aby opravil custom theme, a povoľoval spoofed `X-Forwarded-Proto`. Časť login responses preto nevytvárala expected Secure-cookie behavior.

```text
broad CA trust + missing backend hostname validation
→ proxy-to-Keycloak identity substitution

broad outbound trust + wrong DNS target
→ valid TLS k wrong service

weakened CSP + spoofed scheme
→ browser/session hardening downgrade
```

Recovery zaviedla exact backend SNI/name validation, service-specific CA bundles, egress/DNS allowlist, immutable CSP compatible s minimal theme a strict trusted proxy addresses. Certificate rotation sa oddelila od session/token review a všetky active browser/session cohorts prešli reauthentication podľa incident scope-u.

## 19. Evidence-preserving containment a recovery

Zachovaj presented certificate chains a fingerprints z external aj backend paths, certificate/key Secret generations, proxy TLS config, SNI/backend validation, truststore inventory/hash, DNS answers, outbound target URLs, cookie raw headers, security headers, realm browser security config, active session/token inventory a affected request/business IDs.

Containment môže zablokovať compromised route/CA/target, stiahnuť public admin/management access, vynútiť trusted proxy path a prepnúť na known-good built-in theme/header policy. Nevypínaj TLS alebo hostname validation ako recovery. Successor certificate/trust/header/cookie generation sa nasadí canary-first a read-backne na wire.

## 20. Acceptance matrix

Positive:

```text
external TLS handshake
→ valid canonical hostname a chain
→ secure login
→ expected cookie/header policy
→ intended token/application operation succeeds
```

Recovery:

```text
certificate/truststore rotation
→ successor loaded on every endpoint/Pod
→ predecessor retired podľa overlap contractu
→ outbound dependencies and second login succeed
```

Forbidden:

```text
expired/wrong-host/untrusted certificate
→ TLS rejects

spoofed forwarded client-certificate alebo scheme header
→ rejects/no identity influence

public HTTP/backend/management/admin bypass
→ network rejects

CSP-violating external script alebo iframe origin
→ browser policy blocks
```

Second-client test zahŕňa modern browser, automation client, proxy backend, LDAP/IdP/SMTP dependency a monitoring client. Second-session test overí existing a fresh browser session po cookie/header/route zmene.

## Kontrolné otázky

- Ktorý exact certificate, private key, keystore a truststore generation sa používa?
- Kto terminates public TLS a kto validates backend identity?
- Je hostname/SNI validácia zapnutá na každom TLS hop-e?
- Je outbound truststore service-specific alebo zbytočne broad?
- Sú client authentication keys oddelené od CA trust anchors?
- Majú cookies expected Secure, HttpOnly, SameSite, Path a Domain behavior cez každý proxy path?
- Kto vlastní CSP/HSTS/frame/referrer headers a nevznikajú konflikty?
- Sú secrets mimo CLI, logs, image layers a broad filesystem accessu?
- Ktoré sessions/tokens/application descendants treba po security zmene zrušiť?
- Prešli wrong-host, expired, untrusted-CA, spoofed-header, direct-backend, CSP, certificate-rotation a second-session tests?

## Primárne zdroje

- [Keycloak — Configuring TLS](https://www.keycloak.org/server/enabletls)
- [Keycloak — Configuring trusted certificates for outgoing requests](https://www.keycloak.org/server/keycloak-truststore)
- [Keycloak — Configuring outgoing HTTP requests](https://www.keycloak.org/server/outgoinghttp)
- [Keycloak — Using a reverse proxy](https://www.keycloak.org/server/reverseproxy)
- [Keycloak — Management interface](https://www.keycloak.org/server/management-interface)
- [Keycloak Server Administration Guide — Realm security defenses and cookies](https://www.keycloak.org/docs/latest/server_admin/)
- [OWASP — Transport Layer Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Security_Cheat_Sheet.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Keycloak server configuration, hostname a reverse proxy](keycloak-server-configuration-hostname-reverse-proxy.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
