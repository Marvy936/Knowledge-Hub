# LDAP

Lightweight Directory Access Protocol — LDAP — je protokol na čítanie a zmenu hierarchickej directory. LDAP operation je dôkaz o jednom requeste voči jednej konkrétnej server a replica generation. Bind success, Search success ani transport-level success nepreukazujú application eligibility, globálnu directory convergence alebo správnu business authorization.

LDAP sa preto číta ako request lifecycle: client musí vybrať endpoint, vytvoriť dôveryhodný TLS channel, autentizovať connection, definovať search base, scope, filter a projection, spracovať result codes a controls a až potom mapovať entries na application identity alebo authorization input. Každý krok má inú failure boundary.

## Replica-bound query lifecycle

```text
application directory question
→ exact directory, replica a schema subject
→ DNS a endpoint selection
→ TCP/TLS a certificate identity
→ Bind state a service principal
→ base DN, scope, filter, attributes a controls
→ server ACL, schema, index a limits
→ entries, referrals a result code
→ client mapping, cache a authorization input
→ replica freshness a second-replica validation
```

LDAP je protocol boundary, nie konkrétny product. OpenLDAP, Active Directory Domain Services a cloud directory proxy môžu podporovať odlišné controls, schema, ACL semantics, referrals a consistency behavior. Runbook musí pomenovať exact server type a generation.

## Exact LDAP subject

LDAP result je platný iba pre konkrétny endpoint, Bind identity, query a replica generation. Subject preto zachováva exact base, scope, filter, projection a porovnávané replicas, aby sa freshness dala reprodukovať.

```yaml
incident: SEC-PAY-48
client: settlement-approval-api
clientIp: 10.48.24.31
directory: AD-DS corp.atlas.example
requestedIdentity: urn:atlas:human:7421
baseDn: DC=corp,DC=atlas,DC=example
scope: subtree
filter: (&(objectClass=user)(sAMAccountName=7421))
projection:
  - objectGUID
  - objectSid
  - memberOf
selectedReplica: DC-FRA-02
comparisonReplica: DC-BTS-01
queryTime: 2026-07-29T08:10:00Z
expectedRemoval: GG-PAY-Settlement-Approvers
```

Subject zachováva client, exact query a replica. Bez týchto údajov veta „LDAP stále vracia group“ nie je reprodukovateľná.

## DIT, DN, RDN a schema

Directory Information Tree organizuje entries hierarchicky. Distinguished Name opisuje aktuálnu pozíciu entry, napríklad `CN=Marcel Novak,OU=Finance,DC=corp,DC=atlas,DC=example`. Relative Distinguished Name je lokálna časť `CN=Marcel Novak`. Move entry zmení DN, ale stabilný identity key má používať immutable identifier, napríklad `objectGUID` alebo application-owned subject mapping.

Object classes určujú povinné a povolené attributes. Schema nie je iba dokumentácia; server ňou validuje Modify/Add a klient podľa nej interpretuje syntax. Application, ktorá mapuje usera podľa mutable emailu alebo DN, môže po rename alebo federation collision spojiť nesprávne účty.

## TLS pred Bind

Simple Bind bez chráneného channelu odhaľuje credential. StartTLS začína na LDAP porte a povýši existujúce spojenie; LDAPS vytvára TLS od začiatku. Bez ohľadu na pattern musí client validovať chain, hostname/SAN, trust anchor a policy pre protocol/cipher generation.

```bash
openssl s_client \
  -connect dc-fra-02.corp.atlas.example:636 \
  -servername dc-fra-02.corp.atlas.example \
  -verify_return_error </dev/null
```

Výstup preukazuje TLS handshake a certificate validation z konkrétneho observation pointu. Nepreukazuje LDAP Bind, directory ACL, replica freshness ani application authorization.

## Bind nie je user authorization

Bind nastaví authentication state LDAP connectionu. Anonymous, simple a SASL/GSSAPI Bind majú odlišné assurance a credential boundaries. Service account má mať minimálne práva na presné attributes a subtrees; broad directory read môže odhaliť sensitive groups, service identities a organizational metadata.

```bash
ldapwhoami -H ldaps://dc-fra-02.corp.atlas.example:636 \
  -D 'CN=svc-settlement-directory,OU=Service Accounts,DC=corp,DC=atlas,DC=example' \
  -W
```

`ldapwhoami` preukazuje effective LDAP authorization identity po Bind-e. Nepreukazuje, že account smie čítať intended attributes, že heslo nie je shared alebo že application používa rovnaký endpoint a trust store.

## Search: base, scope, filter a projection

Search request má base DN, scope `base|one|sub`, filter, requested attributes, size/time limits a optional controls. Broad subtree query s `memberOf=*` môže byť funkčne správna, ale nákladná a privacy-neprimeraná. Projection má obsahovať iba fields potrebné pre konkrétnu decision.

Replica-specific query incidentu:

```bash
ldapsearch -LLL \
  -H ldaps://dc-fra-02.corp.atlas.example:636 \
  -D 'CN=svc-settlement-directory,OU=Service Accounts,DC=corp,DC=atlas,DC=example' \
  -W \
  -b 'DC=corp,DC=atlas,DC=example' \
  -s sub \
  '(&(objectClass=user)(sAMAccountName=7421))' \
  objectGUID objectSid memberOf
```

Výstup preukazuje attributes videné cez `DC-FRA-02` v čase query. Nepreukazuje state na `DC-BTS-01`, nested/transitive membership, SIDHistory, Global Catalog projection, application cache ani issued sessions.

Rovnaká query proti obom replicas je diskriminačný experiment. Ak BTS membership nevracia a FRA ju vracia, problém nie je client-side cache; existuje replica divergence alebo product-specific projection difference.

## Filter escaping a LDAP injection

LDAP filter a DN majú odlišné escaping rules. String concatenation z user inputu môže zmeniť filter semantics, napríklad `*)(|(objectClass=*))`. Parameter binding alebo správna RFC escaping knižnica je mandatory. Input validation nie je náhrada escaping-u, pretože legitímne hodnoty môžu obsahovať špeciálne znaky.

Bezpečný application flow oddeľuje user-supplied identifier od filter template, limituje base/scope/projection a používa exact-result expectation. Query, ktorá očakáva jeden account a vráti viac entries, musí zlyhať closed namiesto výberu prvého výsledku.

## ACL, indexing, limits a referrals

LDAP server môže vrátiť success, ale skryť attributes podľa ACL. Absence `memberOf` preto nemusí znamenať, že membership neexistuje. Application musí rozlišovať absent value, insufficient access, partial results a schema behavior.

Index ovplyvňuje latency a server load, nie semantics intended query. Unindexed broad filter môže vyčerpať size/time limit alebo spôsobiť operational incident. Paged results control pomáha bounded enumeration, no nezaručuje snapshot isolation počas concurrent changes.

Referrals a chase policy menia trust boundary. Client nesmie automaticky poslať Bind credential na neznámy referred endpoint. Multi-domain/forest query musí explicitne definovať trusted referral targets a identity mapping.

## Modify a unknown outcome

LDAP Modify je state transition. Timeout po odoslaní requestu vytvára unknown outcome: change mohol byť commitnutý, zatiaľ čo client response nedostal. Blind retry môže byť benigný pri idempotentnom replace, ale nebezpečný pri add/remove alebo external side effects.

```ldif
dn: CN=Marcel Novak,OU=Finance,DC=corp,DC=atlas,DC=example
changetype: modify
delete: memberOf
memberOf: CN=GG-PAY-Settlement-Approvers,OU=Groups,DC=corp,DC=atlas,DC=example
-
```

Tento LDIF ilustruje intent, ale v AD `memberOf` je back-link a membership sa mení na group `member` attribute, nie priamym zápisom user `memberOf`. Product-specific schema a write authority preto musia byť explicitné. Generic LDIF snippet bez product semantics môže byť nesprávny recovery návod.

## Incident `SEC-PAY-48`

Membership removal sa o 07:40 commitol na `DC-BTS-01`, no chybná site-link schedule zabránila convergence na `DC-FRA-02`. Chýbajúci subnet-to-site mapping spôsobil výber stale FRA replica. Application vyčistila cache a vykonala fresh LDAP Search; stále dostala privileged membership, pretože query bola fresh iba voči stale replica generation.

Competing hypotheses boli application cache, wrong filter, ACL hiding, removal nesprávneho group objectu, nested membership, SIDHistory a replication lag. Direct replica-bound queries a AD attribute metadata ukázali rozdiel medzi BTS a FRA. Root cause bola directory divergence, nie LDAP protocol failure.

Fresh query následne poslúžila ako authorization input pre ďalší systém. Tým sa stale directory state rozšíril do fresh Kerberos ticketu a OAuth tokenu. „Cache disabled“ preto nie je freshness proof, ak authority itself nie je converged.

## Containment a recovery

Containment zablokuje privileged business operation a zachová exact LDAP requests, endpoints, TLS identities, result codes, returned attributes a replica metadata. Nemení filter ani ACL naslepo a nevykoná force replication pred uložením divergence evidence.

Recovery opraví site topology a subnet mapping, nechá membership removal convergovať a opakuje exact query proti všetkým required replicas. Application cache sa invaliduje až po authority convergence. Potom sa revoke-nú sessions a tokens vytvorené zo stale resultu.

Acceptance vyžaduje rovnaký immutable object identity, absent privileged membership na required replicas, správny selected DC, fresh application query bez stale claimu a denied resource action. Negative fixture s escaped malicious filterom musí vrátiť nula alebo presne intended entry, nie broad result set. Druhý membership change musí prejsť rovnakým convergence intervalom bez manual force syncu.

## Kontrolné otázky

1. Prečo fresh LDAP query nie je automaticky fresh directory truth?
2. Aký rozdiel je medzi Bind identity a application authorization?
3. Čo replica-specific `ldapsearch` preukazuje a čo nie?
4. Prečo absent attribute nemusí znamenať absent value?
5. Ako sa filter escaping líši od DN escaping-u?
6. Prečo referral chasing mení credential trust boundary?
7. Ktoré dôkazy uzatvárajú replica convergence aj downstream revocation?

## Referencie

- [RFC 4511 — LDAP protocol](https://www.rfc-editor.org/rfc/rfc4511)
- [RFC 4513 — LDAP authentication and security](https://www.rfc-editor.org/rfc/rfc4513)
- [Microsoft LDAP overview](https://learn.microsoft.com/en-us/previous-versions/windows/desktop/ldap/lightweight-directory-access-protocol-ldap-api)
- [OWASP LDAP Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/LDAP_Injection_Prevention_Cheat_Sheet.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Active Directory](active-directory.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Kerberos →](kerberos.md)
<!-- KNOWLEDGE-NAVIGATION:END -->