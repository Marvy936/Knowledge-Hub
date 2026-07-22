# LDAP

Lightweight Directory Access Protocol (LDAP) je aplikačný protokol na prístup k hierarchickým directory službám. Umožňuje clients vyhľadávať, čítať, pridávať, meniť a mazať directory entries a vykonať Bind alebo ďalšie authentication mechanisms. LDAP sám nie je kompletný identity provider, authorization framework ani šifrovací protokol.

## 1. Mentálny model

```text
client
→ TCP/TLS connection
→ Bind alebo anonymous/authenticated session
→ Distinguished Name a search base
→ filter + scope + requested attributes
→ directory server
→ schema a access controls
→ entries/result codes/referrals
```

Directory je optimalizovaná na čítanie a hierarchickú organizáciu identities a resources, nie na všeobecné transactional application dáta.

## 2. Directory Information Tree

LDAP directory používa Directory Information Tree (DIT).

Príklad:

```text
dc=example,dc=com
├── ou=People
│   ├── uid=alice
│   └── uid=bob
├── ou=Groups
└── ou=Services
```

Každý entry má Distinguished Name (DN), ktorý jednoznačne určuje jeho pozíciu.

## 3. DN a RDN

### Distinguished Name

Celá cesta entry v DIT:

```text
uid=alice,ou=People,dc=example,dc=com
```

### Relative Distinguished Name

Prvá časť relatívna k parentovi:

```text
uid=alice
```

DN je štruktúrovaná hodnota. Nemá sa skladať nebezpečným string concatenation bez správneho escaping.

## 4. Entries, object classes a attributes

Entry je množina attributes definovaných schema pravidlami.

Príklad LDIF:

```ldif
dn: uid=alice,ou=People,dc=example,dc=com
objectClass: top
objectClass: person
objectClass: organizationalPerson
objectClass: inetOrgPerson
uid: alice
cn: Alice Example
sn: Example
mail: alice@example.com
```

Object classes určujú required a allowed attributes.

Schema definuje:

- attribute syntax,
- matching rules,
- single/multi-valued semantics,
- object class inheritance,
- OIDs.

## 5. LDAP operations

Základné operations:

- Bind,
- Unbind,
- Search,
- Compare,
- Add,
- Delete,
- Modify,
- Modify DN,
- Extended operations,
- Abandon.

Search je najčastejšia operation, ale write a administrative lifecycle musí byť navrhnutý rovnako dôsledne.

## 6. Bind

Bind vytvorí authentication state LDAP connection.

Možnosti:

- anonymous bind,
- simple bind s DN a passwordom,
- SASL mechanisms,
- certificate-based SASL EXTERNAL podľa implementácie.

Simple bind bez TLS môže vystaviť password. Production návrh má používať TLS a overovať server identity.

Bind success dokazuje iba, že directory akceptovala credentials pre bind identity. Neznamená automaticky, že user smie použiť application alebo konkrétny resource.

## 7. StartTLS a LDAPS

### StartTLS

Client otvorí LDAP connection a cez extended operation prejde na TLS.

### LDAPS

TLS je vytvorené od začiatku connection, typicky na samostatnom porte.

OpenLDAP podporuje oba modely.

Kontroluj:

- trusted CA,
- hostname/SAN verification,
- protocol/cipher policy,
- certificate expiration,
- client certificates podľa potreby,
- downgrade/fallback správanie.

`Encryption enabled` bez certificate verification môže stále umožniť man-in-the-middle attack.

## 8. Search request

Search obsahuje:

- base DN,
- scope,
- filter,
- requested attributes,
- size/time limits,
- optional controls.

Scopes:

- base object,
- one level,
- whole subtree.

Zlý base alebo scope môže spôsobiť missing results alebo drahý full-tree search.

## 9. LDAP filters

Príklady:

```text
(uid=alice)
(&(objectClass=person)(mail=alice@example.com))
(|(uid=alice)(uid=bob))
(!(accountStatus=disabled))
```

User input musí byť escaped podľa LDAP filter syntax. Inak vzniká LDAP injection.

Filter by mal používať indexed attributes pre očakávaný query pattern.

## 10. Attributes a projection

Client má žiadať iba potrebné attributes.

Riziká broad reads:

- zbytočný network a server load,
- exposure sensitive attributes,
- väčšie responses,
- nejasný application contract.

Operational attributes môžu mať odlišné retrieval semantics než bežné user attributes.

## 11. Controls a extensions

LDAP controls rozširujú operation behavior.

Príklady:

- paged results,
- server-side sorting,
- assertion controls,
- synchronization controls podľa implementation.

Client musí vedieť, či control je critical. Unsupported critical control má viesť k failure, nie tichému ignorovaniu.

## 12. Referrals

Directory server môže vrátiť referral na inú LDAP URL alebo naming context.

Riziká:

- credentials forwarding,
- trust iný server/CA,
- loops,
- partial results,
- network/firewall.

Client má mať explicitnú referral policy.

## 13. Access control

Directory authorization rozhoduje:

- kto smie čítať entry/attribute,
- kto smie meniť konkrétny attribute,
- kto smie vytvárať alebo mazať entries,
- kto smie meniť DN,
- aké operations sú anonymous.

OpenLDAP ACLs a AD DS ACLs majú odlišný configuration model. LDAP protokol neurčuje univerzálny authorization policy language.

Attribute-level access je dôležitý: používateľ môže smieť čítať meno, ale nie password hashes alebo sensitive HR attributes.

## 14. Authentication cez LDAP v aplikáciách

Bežné patterns:

### Direct user bind

Application bindne ako user DN s predloženým passwordom.

Výhoda:

- directory overí password.

Riziká:

- application spracúva user password,
- treba nájsť správny DN,
- lockout/error leakage,
- TLS je kritické.

### Service bind + password verify pattern

Application použije service account na search user DN a potom skúsi user bind.

Service account má mať iba read attributes potrebné na identity lookup.

### Password comparison

Application číta password attribute/hash a porovnáva ho lokálne. Toto je často nevhodné a vyžaduje veľmi citlivý read access.

Pre nové web/cloud aplikácie býva vhodnejší OIDC/OAuth federation než priame spracovanie LDAP passwordov.

## 15. Group membership

Group modely sa líšia:

- group entry obsahuje member DNs,
- user entry obsahuje group references,
- nested groups,
- dynamic groups podľa server capability.

Aplikácia musí definovať:

- authoritative membership attribute,
- nested resolution,
- cycle handling,
- caching a propagation,
- deleted/renamed DN behavior.

Group membership nie je automaticky application role mapping.

## 16. Indexes

Directory indexes znižujú cost častých searches.

Index strategy vychádza z:

- equality filters,
- substring/presence queries,
- sort,
- dataset size,
- write rate.

Príliš málo indexes spôsobí expensive scans. Príliš veľa indexes zvyšuje write cost a storage.

## 17. Replication

LDAP je protokol; replication je capability konkrétnej directory implementation.

OpenLDAP môže používať syncrepl a rôzne provider/consumer topologies. AD DS má vlastný multimaster replication model.

Treba rozlíšiť:

- LDAP request success na jednom serveri,
- convergence do ďalších replicas,
- conflict resolution,
- read-after-write expectations,
- failover behavior.

## 18. Password storage a policies

Directory môže ukladať password-derived data alebo integrovať externý authentication source.

Controls:

- modern password hashing podľa platformy,
- write-only password change path,
- password policy,
- lockout/rate limiting,
- secure reset,
- no password logging,
- replication protection.

LDAP search account nemá mať read access k password hashes.

## 19. Service account pre LDAP integration

Minimal permissions:

- bind,
- search base iba v potrebnom subtree,
- read allowlist attributes,
- žiadne write/delete,
- short/rotated credential podľa capability,
- network restriction,
- audit ownera a use.

Service account DN a password nepatria do source code ani image.

## 20. High availability

Client strategy môže zahŕňať:

- viac LDAP endpoints,
- DNS SRV discovery,
- load balancer podľa server semantics,
- health checks,
- retry s idempotency awareness,
- site/region affinity.

Write retry po uncertain timeout môže vytvoriť duplicate alebo conflict. Nie všetky LDAP operations sú bezpečne retryable bez kontroly výsledku.

## 21. Observability

Sleduj:

- connection rate/errors,
- Bind success/failure a lockouts,
- search rate/latency,
- filter/base/scope classes bez sensitive values,
- result codes,
- active connections,
- thread/worker saturation,
- cache/index behavior,
- replication lag/failures,
- database/disk,
- TLS expiration/errors,
- size/time limit hits.

## 22. Troubleshooting connection a TLS

```text
DNS a endpoint?
→ TCP port/firewall?
→ StartTLS/LDAPS mode?
→ CA trust?
→ hostname/SAN?
→ protocol/cipher?
→ client certificate/SASL?
→ server logs a result code?
```

Testujte s tools ako `ldapsearch` a explicitným TLS verification. `-x` znamená simple authentication, nie automaticky secure transport.

## 23. Troubleshooting Bind

```text
správny Bind DN alebo identity mapping?
→ account enabled/locked?
→ password/credential?
→ TLS?
→ SASL mechanism?
→ time/certificate?
→ server ACL a auth policy?
→ replica consistency?
```

Nezobrazuj clientovi rozdiel medzi `user neexistuje` a `password nesprávny`, ak to umožní enumeration.

## 24. Troubleshooting Search

```text
base DN?
→ scope?
→ filter escaping/syntax?
→ requested attributes?
→ ACL?
→ size/time limit?
→ index?
→ referral/partial result?
→ replica freshness?
```

Search success s nulovým výsledkom nie je protokolový error. Môže ísť o nesprávny base/filter alebo access control, ktorý entries skryje.

## 25. LDAP injection

LDAP injection vzniká pri vložení neescaped inputu do filteru alebo DN.

Controls:

- parameterized/builder API,
- správne escaping pre filter a DN osobitne,
- allowlist syntax,
- minimal service account,
- negative tests,
- error handling bez leakage.

Escaping rules pre filter a DN nie sú totožné.

## 26. LDAP oproti AD DS

- LDAP je protocol.
- AD DS je directory platforma, ktorá LDAP implementuje spolu s Kerberos, DNS, Group Policy a Windows authorization.
- OpenLDAP je LDAP directory software.

`Používame LDAP` nestačí na určenie identity platformy, schema, replication alebo security modelu.

## 27. LDAP oproti OIDC

LDAP:

- directory queries a binds,
- persistent connection/client-server protocol,
- často internal network integration,
- aplikácia môže spracúvať password.

OIDC:

- federated web/API authentication,
- browser redirects a signed ID tokens,
- identity provider spracúva authentication,
- relying party overuje assertion.

Nová cloud application nemusí priamo hovoriť s LDAP, aj keď authoritative users pochádzajú z directory.

## 28. Anti-patterny

### Simple Bind bez TLS

Credentials môžu byť odhalené.

### `cn` ako unique login bez contractu

Meno nemusí byť unique ani stabilné.

### Service account s read accessom na celé directory

Zvyšuje confidentiality blast radius.

### Neescaped filter

Vzniká LDAP injection.

### Predpoklad okamžitej replication

Failover replica môže mať dočasne starý state.

### LDAP groups priamo ako application permissions bez mapping vrstvy

Directory reorganizácia nečakane zmení access.

### Certificate verification vypnuté

TLS neposkytuje dôveryhodnú server authentication.

## 29. Kontrolné otázky

1. Čo je DIT, DN a RDN?
2. Ako schema, object classes a attributes súvisia?
3. Čo robí Bind a čo nedokazuje?
4. Ako sa líši StartTLS a LDAPS?
5. Čo obsahuje Search request?
6. Ako vzniká LDAP injection?
7. Ako fungujú referrals a controls?
8. Ako navrhnúť minimal LDAP service account?
9. Prečo LDAP nie je synonymum AD DS ani OIDC?
10. Ako diagnostikuješ Bind alebo Search failure?

## Glossary impact

Relevantné pojmy: LDAP, Directory Information Tree, entry, Distinguished Name, Relative Distinguished Name, object class, attribute, schema, OID, Bind, simple bind, SASL, StartTLS, LDAPS, search base, search scope, LDAP filter, LDAP control, referral, LDIF, LDAP injection, syncrepl a directory index.

## Primárne zdroje

- [OpenLDAP Software 2.6 Administrator's Guide](https://www.openldap.org/doc/admin26/)
- [OpenLDAP schema specification](https://www.openldap.org/doc/admin26/schema.html)
- [OpenLDAP access control](https://www.openldap.org/doc/admin26/access-control.html)
- [OpenLDAP LDAP result codes](https://www.openldap.org/doc/admin26/appendix-ldap-result-codes.html)
- [RFC 4511 — LDAP protocol](https://www.rfc-editor.org/rfc/rfc4511)
- [RFC 4515 — LDAP search filters](https://www.rfc-editor.org/rfc/rfc4515)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Active Directory](active-directory.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Kerberos →](kerberos.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
