# LDAP

Lightweight Directory Access Protocol — LDAP — je protokol na čítanie a zmenu hierarchickej directory. LDAP operation je dôkaz o jednom requeste voči jednej konkrétnej server/replica generation. Bind success, Search success alebo HTTP-like transport success nepreukazujú application eligibility, globálnu directory convergence ani správnu business authorization.

## 1. Dominantný lifecycle

```text
application identity alebo directory question
→ exact directory/replica/schema subject
→ DNS, endpoint a TLS identity
→ connection a Bind/SASL state
→ base DN, scope, filter a projection
→ ACL, schema, index a server controls
→ entry/result/referral generation
→ client mapping, cache a authorization consumer
→ replication/freshness verdict
→ allowed, forbidden a second-replica validation
```

Kľúčové rozlíšenia:

```text
TCP/TLS connection uspela
≠ Bind identity je správna
≠ Search našiel authoritative population
≠ selected replica je converged
≠ returned group znamená application permission
≠ application session bola po directory change-i revoke-nutá
```

## 2. Exact LDAP subject

Pri incidente zaznamenaj:

```text
directory product a version
server/replica hostname a identity
naming context a schema generation
Bind mechanism a Bind principal
TLS mode, certificate a trust path
base DN, scope, filter a requested attributes
controls, limits a referral policy
result code, entries a operational metadata
replication/freshness generation
client mapping/cache/session consumer
```

Connected Atlas subject:

```text
security incident: SEC-PAY-48
LDAP subject: LDAP-PAY-48
directory: AD DS LDAP
Bind principal: CN=svc-settlement-auth,OU=Services,DC=corp,DC=atlas,DC=example
search base: OU=Groups,DC=corp,DC=atlas,DC=example
privileged group: CN=GG-PAY-Settlement-Approvers,OU=Groups,...
origin replica: DC-BTS-01
stale replica: DC-FRA-02
consumer: Atlas Authorization Server
```

## 3. DIT, DN, RDN a stable identity

LDAP directory používa Directory Information Tree — DIT. Entry má Distinguished Name, ktorý určuje jeho pozíciu:

```text
CN=GG-PAY-Settlement-Approvers,OU=Groups,DC=corp,DC=atlas,DC=example
```

Relative Distinguished Name je prvá relatívna časť, napríklad `CN=GG-PAY-Settlement-Approvers`.

DN je structured value, nie bezpečný string fragment. Rename alebo move zmení DN; application preto nemá zamieňať aktuálnu path s nemennou identity. Podľa platformy používaj stable object GUID/UUID alebo iný explicitný immutable key.

Filter escaping a DN escaping majú odlišné pravidlá. Jedna generic string-escape funkcia nemusí bezpečne riešiť oba contexts.

## 4. Entry, schema, object classes a attributes

Entry je množina attributes riadená schema pravidlami. Object classes určujú required a allowed attributes, syntax, matching rules a inheritance.

```ldif
dn: uid=alice,ou=People,dc=example,dc=com
objectClass: inetOrgPerson
uid: alice
cn: Alice Example
sn: Example
mail: alice@example.com
```

Application contract musí pomenovať:

- stable identity attribute;
- authoritative status/eligibility attributes;
- single alebo multi-valued semantics;
- case/matching rules;
- rename/delete behavior;
- schema version a migration;
- attribute-level confidentiality.

`cn`, display name alebo email nemusia byť unique ani stabilné identity keys.

## 5. Connection a TLS boundary

LDAP môže použiť StartTLS alebo TLS od začiatku connectionu — často označované ako LDAPS. V oboch prípadoch musí client overiť server identity.

```text
DNS name
→ TCP endpoint
→ TLS mode
→ trusted CA chain
→ hostname/SAN match
→ protocol/cipher policy
→ authenticated LDAP connection
```

Encryption bez hostname verification chráni bytes pred pasívnym pozorovaním, ale nevytvára dôveryhodnú server identity. Silent fallback z TLS na plaintext je forbidden outcome.

Client musí odlíšiť:

- transport unavailable;
- TLS negotiation failure;
- certificate trust/identity failure;
- LDAP protocol result;
- Bind alebo operation authorization failure.

## 6. Bind nastavuje connection authentication state

Bind môže byť anonymous, simple alebo SASL. Simple Bind prenáša password-based credential a potrebuje chránený transport.

```text
connection
→ Bind request
→ server authentication policy
→ Bind result
→ authenticated connection state
```

Bind success dokazuje iba to, že directory akceptovala credential pre Bind principal na tejto connection. Nedokazuje:

- že end user je application-eligible;
- že service account smie čítať každý attribute;
- že group result bude aktuálny;
- že application smie povoliť konkrétnu resource action.

Po failed Bind-e alebo re-Bind-e musí client správne riadiť connection state; connection pool nesmie neúmyselne zdieľať user-authenticated state medzi requests.

## 7. Search request je presný query contract

Search obsahuje:

```text
base DN
+ scope: base / one-level / subtree
+ filter
+ requested attributes
+ size/time limits
+ controls
```

Example privileged membership lookup:

```text
base: CN=GG-PAY-Settlement-Approvers,OU=Groups,DC=corp,DC=atlas,DC=example
scope: base
filter: (objectClass=group)
attributes: member,objectGUID,uSNChanged,whenChanged
```

Search success s nulovým počtom entries nie je protokolový failure. Môže znamenať:

- objekt neexistuje pod zvoleným base/scope;
- filter nesedí;
- ACL entry skryla;
- referral nebola nasledovaná;
- replica je stale;
- limit alebo control zmenil výsledok.

## 8. Filters a LDAP injection

Filter je program nad directory attributes. User input vložený string concatenation môže zmeniť query semantics.

```text
intended:
(&(objectClass=person)(uid=<escaped-user>))

unsafe input:
*)(|(uid=*))
```

Controls:

- LDAP filter builder alebo správne RFC escaping;
- samostatné DN escaping;
- allowlist identity syntax;
- fixed base a scope;
- minimal Bind principal;
- negative injection fixtures;
- bounded error disclosure.

Escaping je potrebný aj vtedy, keď input „pochádza z interného systému“; compromised upstream alebo malformed identity môže stále zmeniť filter.

## 9. Projection a attribute confidentiality

Client má žiadať iba potrebné attributes. Broad projection zvyšuje latency, payload, coupling aj confidentiality blast radius.

Service account pre identity lookup typicky nepotrebuje:

- password hashes;
- recovery attributes;
- unrelated HR fields;
- write/delete permissions;
- celé directory subtree.

Attribute access môže byť citlivejší než entry access. `User existuje` a `service smie čítať sensitive credential-derived attribute` sú odlišné decisions.

## 10. ACL a authorization semantics

LDAP protokol neurčuje jeden univerzálny ACL language. OpenLDAP, AD DS a ďalšie servers používajú vlastné access-control models.

Directory decision môže závisieť od:

```text
Bind identity
→ target DN/attribute
→ operation
→ inheritance/order/model
→ connection/security context
→ allow, deny alebo hidden result
```

Application nesmie interpretovať `0 entries` automaticky ako `user neexistuje`; ACL môže existence skryť. Audit a troubleshooting potrebujú server-side decision/result evidence.

## 11. Controls, paging a referrals

Controls menia operation behavior, napríklad paged results, sorting, assertions alebo synchronization. Unsupported critical control musí operation zlyhať; tiché ignorovanie by zmenilo contract.

Referral môže odkázať na iný server alebo naming context. Automatic following potrebuje explicitnú policy pre:

- trusted endpoints a CAs;
- credential forwarding;
- tenant/naming-context boundary;
- loops a hop limit;
- partial-result handling;
- network availability.

Client nesmie poslať service credential arbitrary referral targetu iba preto, že referral prišla z trusted directory.

## 12. Replica identity a consistency

LDAP je request protocol; replication semantics patria konkrétnej directory implementation. Successful read z jednej replica nepreukazuje convergence.

```text
write na replica A
→ local acknowledgement
→ replication queue/topology
→ apply na replica B
→ client failover na B
→ potentially stale read
```

Client strategy musí určiť:

- preferred site/replica;
- read-after-write requirement;
- failover freshness tolerance;
- operational metadata použitú na freshness verdict;
- cache TTL a invalidation;
- správanie pri divergence.

Security-sensitive negative change — removal, disable, revocation — má prísnejší freshness contract než bežný profile update.

## 13. Group resolution a application mapping

LDAP group membership môže byť reprezentovaná member DNs, reverse references, nested groups alebo dynamic rules. Application musí explicitne definovať:

```text
authoritative edge
→ nested traversal a cycle limit
→ stable identity mapping
→ cache generation
→ application role/capability mapping
→ revocation trigger
```

Directory group nie je automaticky application permission. Organizačný rename, nested group alebo stale replica môže nečakane zmeniť access. High-risk application má mapovať directory state na vlastný versionovaný entitlement alebo JIT approval contract.

## 14. Authentication patterns

### Service search + user Bind

Application použije restricted service account na nájdenie user DN a následne skúsi Bind ako user. Directory overí password, ale application stále riadi session, MFA/step-up, eligibility a resource authorization.

### SASL/GSSAPI

Application môže použiť Kerberos-backed SASL a nepracovať s user passwordom. Stále však potrebuje správne service identity, channel protection a directory ACL.

### Modern federation

Nová browser/cloud application často používa OIDC/OAuth pred direct LDAP password processingom. Directory môže zostať authoritative source, ale application nedostane raw user password.

Password comparison po prečítaní hash attribute-u je spravidla neprimerane rizikový pattern.

## 15. Writes a unknown outcome

Modify, Add, Delete a Modify DN menia directory state. Timeout po odoslaní requestu vytvára unknown outcome:

```text
request bol odoslaný
→ server mohol commitnúť
→ response sa stratila
→ blind retry môže vytvoriť conflict alebo druhú mutation
```

Pred retry prečítaj exact object/attribute generation a porovnaj intended state. Assertion controls alebo stable operation identity môžu pomôcť, ale semantics závisia od servera a use case-u.

Write acknowledgement na origin replica neznamená global convergence ani downstream session revocation.

## 16. Indexes, limits a availability

Index strategy vychádza z reálnych filters, matching rules, cardinality a write rate. Missing index môže zmeniť login path na full-tree scan; príliš veľa indexes zvyšuje write a storage cost.

Operational contract zahŕňa:

- search latency a scanned entries;
- size/time/admin limits;
- active connections a worker saturation;
- TLS handshake failures;
- Bind lockout behavior;
- replication lag;
- cache hit/freshness;
- result codes podľa operation class.

Availability fix nesmie vypnúť ACL, TLS verification alebo limits bez explicitného risk decisionu.

## 17. Worked failure: Bind green, privilege state stale

### Symptom

Atlas Authorization Server o `08:12 UTC` úspešne Bind-ne a nájde Martinu ako member `GG-PAY-Settlement-Approvers`, hoci membership bola odstránená o `07:40 UTC`. Dashboard ukazuje LDAP availability `100 %` a p95 `18 ms`.

### Exact query subject

```text
LDAP subject: LDAP-PAY-48
endpoint pool: ldap.corp.atlas.example
selected server: DC-FRA-02
Bind principal: svc-settlement-auth
TLS server name: ldap.corp.atlas.example
base: privileged group DN
scope: base
filter: (objectClass=group)
projection: member,objectGUID,uSNChanged,whenChanged
client cache TTL: 5 min
```

### Competing hypotheses

1. application cache drží pre-removal result;
2. service Bind principal nemá právo vidieť removal;
3. query používa wrong group DN alebo base;
4. nested group udeľuje access inou cestou;
5. selected replica neobsahuje latest removal;
6. referral presunula query na iný naming context;
7. result parser zamieňa partial/empty result za allow.

### Discriminating evidence

```text
fresh process, empty client cache:
  query DC-FRA-02 → user SID present
  query DC-BTS-01 → user SID absent

Bind result na oboch DCs:
  success

TLS identity:
  valid na oboch paths

same base/filter/projection:
  rozdielny member attribute version

DC-FRA-02 replication metadata:
  pre-removal generation

referrals/limits:
  none
```

Fresh client s empty cache diskriminuje application-cache hypotézu. Bind, TLS, filter a ACL sú funkčné. Root cause je replica freshness, nie protocol availability.

### Evidence-preserving containment

- pinúť high-risk reads na known-converged replica iba ako krátke containment s monitoringom;
- zastaviť privileged token issuance z affected group resultu;
- preserve-nuť exact query, server, result, operational metadata, TLS a Bind audit;
- revoke-nuť sessions/tokens už vydané zo stale resultu;
- nevypínať TLS verification ani nepoužiť directory superuser account;
- nepredĺžiť cache ako „stabilizačný“ fix.

### Authoritative recovery

1. opraviť AD replication topology a subnet/site mapping;
2. potvrdiť attribute convergence na všetkých LDAP replicas v endpoint poole;
3. zmeniť client pool tak, aby logoval selected server a freshness generation;
4. zaviesť stricter negative-change convergence gate pre privileged groups;
5. mapovať group na short-lived/JIT application entitlement namiesto broad long-lived cache;
6. pri removal evente invalidovať cache a revoke-nuť derived sessions/grants;
7. testovať failover na každú replica a partial-result behavior.

### Acceptance verdict

- rovnaký exact Search na všetkých required replicas vráti rovnakú membership generation;
- removed principal nevznikne v result-e ani cez nested path;
- Bind principal stále prečíta iba allowlisted attributes;
- invalid certificate, plaintext fallback, injection a untrusted referral zlyhajú;
- oprávnený principal sa mapuje na správnu bounded capability;
- stale cache, session a OAuth grant sú neplatné;
- druhá controlled removal prejde origin-write, replica-read, failover a second-login testom.

## 18. Troubleshooting flow

### Connection a TLS

```text
DNS/endpoint
→ TCP
→ StartTLS alebo LDAPS mode
→ CA a hostname/SAN
→ protocol/cipher
→ LDAP protocol response
```

### Bind

```text
Bind identity a mechanism
→ account state/credential
→ TLS/channel
→ SASL mapping
→ server auth policy
→ selected replica
→ post-Bind connection state
```

### Search

```text
selected replica/freshness
→ base a scope
→ escaped filter
→ projection
→ ACL/schema
→ controls/limits/referrals
→ result parser
→ cache/mapping
→ application decision
```

## 19. Earlier controls

- log selected LDAP server a object generation pre high-risk lookup;
- per-replica synthetic membership canary;
- convergence SLO pre privileged negative changes;
- schema-tested query builders a injection fixtures;
- certificate-expiry a hostname-verification canary;
- minimal attribute allowlist pre service Bind;
- bounded cache s event-driven invalidation;
- explicit empty/partial/referral handling;
- second-replica a second-session acceptance test.

## 20. Anti-patterny

### Bind success = application access

Directory overila credential, nie business permission.

### Load balancer skryje replica identity

Troubleshooting nevie, ktorý state application čítala.

### `0 entries` = user neexistuje

Wrong base, ACL, referral, limit alebo stale replica môžu vytvoriť rovnaký result.

### Service account číta celý directory

Zvyšuje confidentiality blast radius bez potreby.

### Simple Bind bez overeného TLS

Credential môže byť zachytený alebo odoslaný wrong serveru.

### LDAP group priamo ako permanentná application role

Directory topology a organizational change sa menia na neauditovaný authorization plane.

## 21. Kontrolné otázky

1. Čo tvorí exact LDAP subject?
2. Prečo DN nie je vždy vhodná immutable identity?
3. Čo Bind success dokazuje a čo nedokazuje?
4. Ako sa StartTLS a LDAPS líšia od certificate verification?
5. Prečo Search success s nulovým resultom nie je jednoznačný verdict?
6. Ako sa filter escaping líši od DN escaping?
7. Ako selected replica mení security result?
8. Prečo group membership nie je automaticky application role?
9. Ako riešiť timeout po LDAP Modify bez blind retry?
10. Čo musí overiť LDAP acceptance verdict?

## Glossary impact

Relevantné pojmy: LDAP subject, replica-bound query, selected LDAP replica, directory freshness verdict, Bind-state generation, search-contract generation, partial-result verdict, attribute-projection contract, privileged negative-change lookup, LDAP-to-application mapping a LDAP acceptance verdict.

## Primárne zdroje

- [RFC 4511 — LDAP protocol](https://www.rfc-editor.org/rfc/rfc4511)
- [RFC 4513 — LDAP authentication and security mechanisms](https://www.rfc-editor.org/rfc/rfc4513)
- [RFC 4515 — LDAP search filters](https://www.rfc-editor.org/rfc/rfc4515)
- [RFC 4533 — LDAP content synchronization](https://www.rfc-editor.org/rfc/rfc4533)
- [OpenLDAP Administrator's Guide](https://www.openldap.org/doc/admin26/)
- [OpenLDAP access control](https://www.openldap.org/doc/admin26/access-control.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Active Directory](active-directory.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Kerberos →](kerberos.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
