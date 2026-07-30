# Realm, client, user, group, role a session

Keycloak používa niekoľko objektov, ktoré sa v bežnej reči často zlejú do slova „account“ alebo „application“. Realm určuje identity a protocol namespace. Client reprezentuje aplikáciu alebo službu, ktorá žiada authentication alebo tokens. User je identity record v realm-e alebo projection external identity. Group organizuje users a môže prenášať attributes a role mappings. Role pomenúva permission alebo application responsibility. Session zachytáva konkrétny authentication a client-use lifecycle.

Tieto objekty nie sú iba administratívne priečinky. Ich vzťahy rozhodujú, ktoré credentials sa overia, aké roles sa stanú effective, čo sa vloží do tokenu alebo assertion, ktoré logout a revocation operácie majú effect a či rename, import alebo synchronization zachová identitu. Chybná voľba medzi group a role môže vytvoriť privilege inheritance, hoci každý jednotlivý object vyzerá správne.

## 1. Dominantný identity-to-effective-access model

```text
authoritative person alebo workload record
→ realm a identity-source selection
→ Keycloak user identity a lifecycle state
→ direct a inherited group membership
→ direct, group a composite role mappings
→ client a client-scope restriction
→ authentication transaction
→ user session a client session
→ token/assertion role projection
→ local account a application session
→ resource authorization
→ mover/leaver, revocation a second-login validation
```

Model oddeľuje entitlement desired state od token snapshotu. User môže byť odstránený zo skupiny, ale starý token môže ešte niesť predchádzajúcu role. Client môže mať správny role mapping, ale `Full Scope Allowed` publikovať aj unrelated roles. Prístup sa preto hodnotí cez celý chain.

## 2. Realm ako identity a protocol namespace

Realm spravuje vlastných users, credentials, roles, groups, clients, keys, sessions a policy configuration. User sa autentizuje voči konkrétnemu realm-u a OIDC issuer zahŕňa realm path. Dva realms môžu mať usera s rovnakým username a clienta s rovnakým `clientId`; stále ide o odlišné identities a trust namespaces.

Realm je vhodný pre výrazne oddelené identity populations, administration alebo protocol policies. Nie je však lacný organizačný tag. Veľký počet realms zvyšuje upgrade, key, client, flow, federation, event a automation complexity. Naopak jeden realm pre nesúvisiace trust domains môže vytvoriť broad roles, mapper coupling a veľký incident blast radius.

Exact realm subject zahŕňa:

```text
Keycloak deployment
+ realm internal ID
+ realm name
+ external issuer URL
+ realm configuration generation
+ active key set generation
+ authentication-flow generation
+ session/token policy generation
+ enabled identity providers a user-storage providers
```

Realm rename alebo import nie je iba URL edit. Issuer sa môže zmeniť, clients môžu odmietnuť tokens a external identity mappings môžu zostať viazané na starý namespace.

## 3. Client identity a registration lifecycle

Client v Keycloaku reprezentuje protocol consumer. Pri OIDC je `clientId` hodnota používaná v protocol requests a audience-related semantics. Pri SAML sa Client ID typicky zhoduje so SP entity ID. Keycloak interne používa aj UUID. Automation nesmie zamieňať mutable alebo human-readable `clientId` s internal identifierom používaným v Admin API paths.

Client registration má lifecycle:

```text
application ownership a protocol choice
→ stable clientId/entity ID
→ internal client UUID
→ redirects/endpoints a credentials
→ scopes, mappers, roles a flow overrides
→ enabled state a session settings
→ application deployment a trust bootstrap
→ secret/key rotation alebo metadata update
→ disable, revoke, delete a residual-session closure
```

Delete a recreate s rovnakým `clientId` môže vytvoriť nový internal client object a zmeniť linked scopes, secrets alebo session descendants. IaC alebo automation má používať stable lookup a compare-and-swap behavior, nie slepý create.

## 4. User identity, attributes a lifecycle

Keycloak user má internal ID, username, enabled state, attributes, credentials, group memberships, role mappings, required actions, federated identity links a sessions. Internal ID je stabilnejší identity key než email alebo username. Email môže byť zmenený alebo znovu pridelený; username môže podliehať normalization a realm policy.

Local user je spravovaný priamo v Keycloaku. Federated user môže pochádzať z LDAP/AD alebo custom storage provideru. Brokered identity vzniká cez external IdP a link. Každý model má inú authority a synchronization semantics. Attribute v Keycloak database môže byť authoritative, imported snapshot, read-only projection alebo local override.

Joiner-mover-leaver musí definovať:

- **joiner** — ako vznikne internal identity, credentials, groups, required actions a owner;
- **mover** — ktoré old memberships, roles, sessions a tokens sa odstránia pri zmene organizácie;
- **leaver** — kedy sa user disabled/deleted, ktoré sessions sa zrušia a ako sa zachová audit identity;
- **rejoin** — či sa obnoví starý internal ID alebo vznikne nový subject;
- **conflict** — čo sa stane pri duplicate username, email alebo external identifieri.

Delete usera môže poškodiť audit väzbu, ak downstream logy uchovávajú iba mutable username. Disabled state a tombstone/retention policy môžu byť vhodnejšie než okamžitý hard delete.

## 5. Group ako organizačný a inheritance model

Group je kolekcia users s attributes a role mappings. Groups môžu byť hierarchické. User v child group dedí attributes a role mappings parent groupov. Táto vlastnosť je užitočná pre organization structure, ale môže vytvoriť privilege inheritance, keď parent group nesie application role.

```text
/payments
  role: settlement-admin
  /partners
    /vega
      user: contractor-481
```

User v `/payments/partners/vega` môže zdediť `settlement-admin`, aj keď direct user mapping neexistuje. Audit, ktorý kontroluje iba direct mappings na userovi, preto vyhlási false negative.

Group path je human-readable hierarchy, nie nezmeniteľná identity. Rename alebo move groupy mení path. Automation má používať internal IDs a explicitne riešiť move/rename semantics. External directory synchronization môže vytvárať alebo meniť group tree; local manual edits môžu byť pri ďalšom sync-u prepísané.

Group je vhodná pre:

```text
organizational membership
→ team, department, partner cohort alebo managed population

shared attributes
→ hodnoty, ktoré majú rovnakú authority pre členov

role assignment
→ iba ak každý člen groupy skutočne potrebuje danú permission
```

Organizačná parent group nemá automaticky niesť high-risk application role. Často je bezpečnejšia dedicated access group s explicitným ownerom a approval lifecycle-om.

## 6. Realm roles, client roles a composite roles

Realm role existuje v realm-wide namespace. Client role patrí konkrétnemu clientovi. Realm role je vhodná pre cross-client capability iba vtedy, keď význam a authority sú skutočne realm-wide. Application-specific permission patrí typicky ako client role.

```text
realm role
→ význam naprieč realm-om a viacerými clients

client role
→ permission alebo responsibility konkrétnej aplikácie/služby

composite role
→ zoskupenie ďalších realm alebo client roles
```

Composite role rozširuje effective role graph. User s composite role dedí contained roles. Zmena composite membershipu môže okamžite zmeniť budúce tokens mnohým users, hoci direct mappings ostanú nezmenené. Role review preto potrebuje transitive closure, nie iba prvú úroveň.

Role name nie je business authorization sám osebe. `settlement-admin` musí mať ownera, resource scope, environment, approval a revocation contract. Rovnaký string v realm role a client role namespaces môže mať odlišný význam.

## 7. Direct, inherited a effective role

Effective role je výsledok viacerých ciest:

```text
direct user role
+ group role
+ parent-group inherited role
+ composite-role expansion
+ default role
→ user effective role set

user effective role set
∩ client role scope mappings
∩ linked client scopes
→ role projection eligible pre token/assertion
```

Táto intersection semantics je zásadná. User môže mať broad effective role, ale client ju nemusí dostať. Naopak `Full Scope Allowed` môže clientovi sprístupniť všetky user roles. Protocol mapper potom rozhodne, ktoré z nich a v akom claim formáte sa publikujú.

Troubleshooting otázka preto nie je iba „má user role?“. Je:

```text
odkiaľ role prišla
→ je direct, group, inherited alebo composite
→ je client oprávnený ju scope-nuť
→ ktorý mapper ju publikoval
→ ktorý token/assertion ju niesol
→ ako ju downstream aplikácia interpretovala
```

## 8. Default roles a default groups

Default role alebo default group sa môže priradiť novému alebo importovanému userovi. Mechanizmus znižuje onboarding toil, ale zároveň vytvára implicitný entitlement path. Zmena defaultu ovplyvní future users a podľa konkrétnej operácie nemusí retroaktívne zmeniť existujúcich.

Default má byť minimálny. Privileged role sa nemá udeľovať ako convenience baseline. Pri incident analysis treba zachovať user creation/import generation a default configuration platnú v tom čase.

## 9. Client scopes a role-scope boundary

Client scope je realm-level reusable configuration, ktorú možno linkovať k clients. Môže niesť protocol mappers a role scope mappings. Dedicated client scope obsahuje client-specific mappers a scope behavior. Default client scope sa aplikuje automaticky; optional scope sa typicky aktivuje requested `scope` hodnotou a policy.

Client scope nie je to isté ako OAuth authorization scope ani Keycloak Authorization Services scope. Názvy sa môžu prekrývať, ale mechanizmus je iný.

```text
Keycloak client scope
→ reusable protocol mapper a token-content configuration

role scope mapping
→ ktoré user roles môže client dostať

OAuth scope parameter
→ clientom požadované authorization scope names

Authorization Services scope
→ action nad protected resource v policy model-e
```

Zámena vedie k očakávaniu, že odstránenie jedného `scope` stringu automaticky odstráni role claim alebo resource permission.

## 10. Session taxonomy

Keycloak počas loginu vytvára authentication session. Po úspechu vzniká user session a client session pre navštívený client. Offline access môže vytvoriť dlhodobejší offline session state. OIDC access/refresh tokens alebo SAML assertion sú artifacts odvodené zo session a configuration snapshotu. Downstream aplikácia si často vytvorí vlastnú cookie session.

```text
authentication session
→ pending browser/login transaction

user session
→ realm-level authenticated user state

client session
→ konkrétny client pripojený k user session

offline session
→ long-lived delegated access state

token/assertion
→ signed snapshot s vlastnou validity

application session
→ downstream state mimo Keycloak servera
```

Session ID a token ID sú odlišné. Access token môže zostať validný po odstránení browser cookie, ak resource server používa local signature validation a nekontroluje revocation/not-before state pri každom requeste. Local application session môže prežiť Keycloak logout, ak client neimplementuje backchannel/frontchannel logout alebo vlastnú revocation.

## 11. Session timeout, idle, max a remember-me

Realm a client session settings určujú idle a maximum lifetime. Idle timeout sa predlžuje activity podľa session semantics; max timeout vytvára absolute boundary. Remember-me môže použiť odlišné hodnoty. Offline sessions majú vlastné policies. Access token lifespan je samostatný a zvyčajne kratší.

Dlhý SSO session znižuje login friction, ale predlžuje stale identity a stolen-cookie window. Krátky access token znižuje bearer exposure, ale zvyšuje refresh/token endpoint load. Client a resource server musia navrhnúť refresh, re-authentication a outage behavior spolu.

## 12. Logout a revocation graph

Logout môže ukončiť Keycloak user/client session a informovať clients. Nie každý client alebo protocol dostane rovnaký signal. Už vydané self-contained access tokens môžu zostať akceptované do expiry, pokiaľ verifier nekontroluje online state alebo relevantnú revocation generation. Application cookie môže zostať aktívna.

Kompletný incident response sleduje:

```text
affected user/credential/role generation
→ Keycloak user sessions
→ client sessions
→ refresh a offline descendants
→ access tokens podľa issuance interval-u
→ SAML local sessions a SessionIndex
→ downstream application sessions
→ cached authorization decisions
→ active business workflows
```

„Sign out all active sessions“ je jeden control, nie univerzálna revocation transakcia.

## 13. Connected incident `KC-PAY-65`

Contractor `contractor-481` bol členom `/payments/partners/vega`. Security review našiel nulové direct admin roles. Parent `/payments` však niesol realm role `settlement-admin`. Group inheritance vytvoril effective realm role.

Oba protocol clients mali `Full Scope Allowed`. OIDC token obsahoval:

```json
{
  "realm_access": {
    "roles": ["settlement-admin"]
  }
}
```

SAML mapper publikoval rovnakú effective role ako `Role=settlement-admin`. Downstream applications verili role stringu bez client-specific authority a tenant checku.

Po sign-out-e zmizla Keycloak browser session. OIDC access token a local SAML application session však pokračovali. Incident ukázal tri odlišné defects:

1. group hierarchy bola použitá ako permission hierarchy;
2. realm role bola použitá pre client-specific privilege;
3. session revocation sa skončila pri Keycloak SSO state-e.

## 14. Redesign role a session modelu

Nový model používa:

```text
organization group /payments/partners/vega
→ bez privileged parent role

dedicated access group /access/payments-admin/approvers
→ explicitný owner, approval a expiry

client role payments-admin:settlement-approve
→ application-specific semantics

client role scope
→ iba payments-admin OIDC client

SAML attribute mapper
→ partner-specific allowlisted role vocabulary

resource authorization
→ tenant + action + object + workflow state
```

Mover workflow odstraňuje old access group, zruší sessions/tokens vytvorené s old entitlement generation a vykoná second-login negative test. Role graph audit enumeruje direct, group, parent a composite paths.

## 15. Acceptance verdict

Model je prijatý, keď:

```text
realm a client identities sú stable a inventarizované
+ user authority a lifecycle sú explicitné
+ group hierarchy nemá neúmyselný privilege inheritance
+ realm/client/composite role graph je vysvetliteľný
+ client scope obmedzuje projected roles
+ token/assertion nesie iba intended entitlement
+ logout/revocation pokryje intended descendants
+ second user, second client a mover test prejdú
```

Kontrola iba Admin Console screenshotu nestačí. Potrebný je effective role graph, actual token/assertion a downstream authorization result.

## 16. Troubleshooting flow

Pri nesprávnej role:

```text
exact user internal ID
→ direct role mappings
→ direct group memberships
→ parent groups a inherited roles
→ composite expansion
→ default roles/groups
→ client Full Scope a role scope mappings
→ linked client scopes a mappers
→ actual token/assertion
→ application role mapping
→ resource authorization
```

Pri session probléme:

```text
authentication transaction
→ user session
→ client session
→ token/refresh/offline descendants
→ local application session
→ logout event delivery
→ verifier revocation behavior
```

Náhodné zníženie timeoutu neopraví broad role mapping. Vymazanie usera bez zachovania evidence môže znemožniť vysvetliť, z ktorej inheritance path privilege vznikla.

## 17. Anti-patterny

### Group equals role

Group reprezentuje population; role reprezentuje permission semantics. Ich kombinácia je možná, ale musí byť vedomá. Parent organizational group s admin role vytvára transitive privilege.

### Realm role pre každú application permission

Realm-wide namespace zvyšuje chance, že role bude scope-nutá ďalšiemu clientovi. Application-specific permission patrí typicky client role.

### Username alebo email ako immutable key

Mutable attribute nie je bezpečný join key pre audit, federation ani account linking. Použi internal ID a external issuer/subject contract.

### Direct-mapping-only audit

Effective access môže prísť z parent groupu, composite role alebo defaultu. Audit musí počítať transitive closure.

### Logout equals revocation

Logout state a bearer token validity sú odlišné. Revocation playbook musí pokryť descendants a downstream sessions.

## 18. Kontrolné otázky

1. Čo realm izoluje a čo stále zdieľa?
2. Aký je rozdiel medzi `clientId` a internal client UUID?
3. Prečo email nie je bezpečný user identity key?
4. Ako child group dedí parent role mappings?
5. Kedy použiť realm role a kedy client role?
6. Ako composite role mení effective role graph?
7. Čo znamená `Full Scope Allowed` pre role projection?
8. Aký je rozdiel medzi client scope, OAuth scope a Authorization Services scope?
9. Ako sa líši authentication session, user session a client session?
10. Prečo access token môže prežiť logout?
11. Ako incident `KC-PAY-65` vznikol bez direct admin role?
12. Čo musí overiť mover a leaver workflow?

## Glossary impact

Relevantné pojmy: realm subject, client internal UUID, Keycloak user identity, group inheritance, realm role, client role, composite role, effective role graph, default group, client scope, role scope mapping, authentication session, user session, client session, offline session, session descendant graph, entitlement generation.

## Primárne zdroje

- [Keycloak — Server Administration Guide](https://www.keycloak.org/docs/latest/server_admin/)
- [Keycloak — Managing users](https://www.keycloak.org/docs/latest/server_admin/#assembly-managing-users_server_administration_guide)
- [Keycloak — Assigning permissions using roles and groups](https://www.keycloak.org/docs/latest/server_admin/#assembly-managing-users_server_administration_guide)
- [Keycloak — Managing user sessions](https://www.keycloak.org/docs/latest/server_admin/#_user-session-management)
- [Keycloak — Upgrading Guide](https://www.keycloak.org/docs/latest/upgrading/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Keycloak architecture a responsibility boundary](keycloak-architecture-and-responsibility-boundary.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: OIDC clients, redirect URIs, scopes a PKCE →](oidc-clients-redirect-uris-scopes-pkce.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
