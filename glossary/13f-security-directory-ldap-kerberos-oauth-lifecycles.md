# Security directory, LDAP, Kerberos and OAuth lifecycle glossary entries

## AD acceptance verdict

Dôkaz, že security-relevant directory change convergoval na všetkých required DC/GC replicas, clients vyberajú intended DC, fresh sessions používajú správny group state a staré application/token paths už forbidden operation nepovoľujú. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## AD DS subject

Exact forest, domain, partition, object GUID/SID/DN, changed attribute alebo group edge, origin DC, replication metadata, selected client DC/KDC/LDAP replica, session generation a downstream authorization scope analyzovaného AD state-u. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## AD/SYSVOL generation pair

Matching directory metadata a SYSVOL content generation jedného Group Policy Objectu, ktoré musia byť dostupné a spracované spolu, aby client dostal intended policy. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## AS/TGS/AP verdict

Stage-specific rozhodnutie, či Kerberos zlyhal pri initial TGT issuance, service-ticket issuance alebo application exchange a ticket presentation. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Attribute-projection contract — LDAP

Allowlist LDAP attributes, ktoré smie konkrétny Bind principal čítať pre definovaný application use case bez zbytočného confidentiality exposure. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## Authorization-transaction generation — OAuth

Jednorazový client-side a Authorization-Server-side state viažuci expected issuer, redirect URI, `state`, PKCE challenge/verifier, requested resource/scope a callback na jednu authorization operáciu. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Bind-state generation

Authentication state konkrétnej LDAP connection po anonymous, simple alebo SASL Bind-e, ktorý nesmie byť neúmyselne zdieľaný medzi unrelated requests alebo users. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## Client-selected replica — AD DS

Domain controller, KDC alebo Global Catalog vybraný konkrétnym clientom cez DNS, site/subnet mapping a DC locator pre daný request alebo logon. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Derived-token graph

Lineage local session, refresh family, access tokens a token-exchange descendants odvodených z jedného OAuth grant alebo authentication contextu. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Directory convergence generation

Security-relevant directory state po aplikovaní exact originating change-u a jeho replication metadata na všetkých replicas required daným authentication, LDAP, Global Catalog alebo policy pathom. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Directory freshness verdict — LDAP

Rozhodnutie, či selected LDAP replica obsahuje required object/attribute generation pre current query a security decision, nie iba či server odpovedal. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## Fresh-but-stale Kerberos ticket

TGT alebo service ticket vydaný po security change-i, ale KDC ho vytvoril z neconverged directory state-u a authorization data preto nesie starú membership alebo eligibility generation. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Fresh-but-stale logon

Nová logon session vytvorená po identity change-i, ktorá napriek tomu používa starý group alebo policy state, pretože selected DC neobsahoval converged generation. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Grant-input generation — OAuth

Exact identity, authentication assurance, directory/group/JIT entitlement, consent a policy state použitý Authorization Serverom pri rozhodnutí vydať token. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Group-state generation — AD DS

Versionovaná direct a nested group-membership graph generation na konkrétnom DC/GC, z ktorej vzniká LDAP result, PAC alebo Windows access token. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## JIT-bound scope

OAuth scope vydaný iba spolu s aktuálnou, časovo obmedzenou approval alebo privilege-activation generation a overovaný Resource Serverom voči exact resource a workflow state-u. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## KDC-selected directory generation

Directory object, group a policy state lokálne dostupný KDC/domain controlleru pri vytváraní TGT, service ticketu alebo PAC. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Kerberos acceptance verdict

Dôkaz, že intended AS/TGS/AP flow, SPN-to-key ownership, KVNO/enctype, replay/freshness a application authorization fungujú, zatiaľ čo old ticket, wrong SPN, fallback a forbidden resource paths zlyhávajú. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Kerberos subject

Exact realm, KDC/DC, client principal, requested service principal, ticket stage, validity/flags, KVNO/enctype, cache/keytab, PAC generation, negotiated mechanism a application authorization scope. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## KVNO overlap generation

Bounded interval, počas ktorého service cohorta dokáže decryptovať tickets vydané old aj new Kerberos key versionou počas koordinovanej rotation. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## LDAP acceptance verdict

Dôkaz, že exact Bind a Search contract vracia converged result cez všetky required replicas/failover paths, minimal ACL zostáva účinná a TLS, injection, referral, stale-cache a forbidden-membership tests zlyhávajú správne. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## LDAP subject

Exact directory implementation, selected replica, naming context/schema, Bind identity/mechanism, TLS identity, base/scope/filter/projection, controls/referrals, result a client cache/mapping analyzovaného LDAP requestu. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## Local resource verdict — OAuth

Resource-Server decision nad validným tokenom, exact action/resource/tenant, current business state, JIT approval, separation-of-duties a ďalšími local authorization podmienkami. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Mechanism-fallback verdict — Kerberos

Explicitný výsledok, či GSS/SPNEGO použilo intended Kerberos mechanismus alebo fallback ako NTLM či spoofable header path. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## OAuth acceptance verdict

Dôkaz, že correct client/issuer transaction vydá resource-specific minimal token, Resource Server vykoná local authorization a removed/old/wrong-audience/refresh/exchanged paths sú po revocation forbidden. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## OAuth subject

Exact issuer, client registration, grant transaction, subject/actor, redirect/state/PKCE, audience/scope, access/refresh generation, sender binding, Resource Server operation a revocation scope. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Originating directory change

Object alebo attribute mutation identifikovaná origin DC, originating timestamp, version, USN a invocation ID, z ktorej sa odvodzuje replication a convergence. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## PAC group generation

Group a authorization-data snapshot vložený AD KDC infraštruktúrou do Kerberos PAC podľa directory state-u dostupného pri ticket issuance. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Partial-result verdict — LDAP

Rozhodnutie, či Search result reprezentuje complete intended population alebo bol obmedzený ACL, limitom, referralom, controlom, timeoutom či stale replica state-om. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## Privileged negative-change lookup

LDAP read contract pre disable, removal alebo revocation event, ktorý vyžaduje prísny convergence a freshness dôkaz pred ďalším privileged token/session issuance. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## Replica-bound query

LDAP request a jeho result viazaný na exact server/replica a lokálnu object generation, nie na abstraktnú predstavu globálne konzistentného directory endpointu. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## Resource-specific token

OAuth access token vydaný pre jeden explicitný Resource Server alebo úzku audience namiesto broad tokenu akceptovaného množstvom unrelated APIs. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Revocation-propagation verdict — OAuth

Dôkaz, že local session, grant, refresh family, access-token validation state, caches a exchanged descendants po revocation už forbidden operation nepovoľujú. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Search-contract generation — LDAP

Exact base DN, scope, escaped filter, requested attributes, controls, limits a referral policy jednej versionovanej LDAP query. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## Site/subnet coverage — AD DS

Verdikt, či všetky relevantné client network prefixes majú jednoznačné AD subnet-to-site mapovanie a preto používajú intended DC/KDC/GC affinity. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## SPN-to-key ownership

Versionovaný vzťah requested Kerberos service principalu k directory accountu, long-term key generation, KVNO a deployed service keytab/managed identity. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Subject-actor chain — OAuth

Auditovateľný rozdiel medzi initiating subjectom a clientom alebo downstream service actorom, ktorý vykonáva delegated alebo exchanged-token operation. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Ticket-generation identity

Exact KDC, client/service principal, issue time, validity, flags, KVNO, enctype a authorization-data generation jedného Kerberos ticketu. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Token authorization snapshot

Scopes a claims zachytené v self-contained access tokene pri issuance, ktoré môžu zostať cryptographically validné aj po neskoršej identity alebo entitlement zmene. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).
