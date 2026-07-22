# Security and Identity

Táto sekcia vysvetľuje bezpečnostné ciele, risk, identity, access control, directory služby, federation, cryptography, secrets, vulnerability management, supply-chain security a Zero Trust. Témy budujú najprv stabilné bezpečnostné princípy a až potom konkrétne protokoly, platformy a produkty.

Cieľom nie je vytvoriť checklist nástrojov. Každá kapitola má vysvetliť chránené assets, trust boundaries, threat model, authorization a identity lifecycle, failure modes, audit evidence, recovery a trade-offy medzi confidentiality, integrity a availability.

## Predpoklady

Odporúča sa najprv dokončiť:

- [DevOps Foundations](../00-foundations/README.md),
- [Linux and Systems](../01-linux-and-systems/README.md),
- [Networking and Web Fundamentals](../02-networking-and-web/README.md),
- [CI/CD and Release Engineering](../05-ci-cd-and-release/README.md),
- [Infrastructure as Code and Configuration Management](../07-infrastructure-as-code-and-configuration-management/README.md),
- [Kubernetes](../09-kubernetes/README.md),
- [Cloud and AWS](../11-cloud-and-aws/README.md),
- [Observability](../12-observability/README.md).

## Odporúčané poradie

1. [CIA triáda](cia-triad.md)
2. [Authentication, authorization a auditing](authentication-authorization-auditing.md)
3. [Least privilege](least-privilege.md)
4. [IAM a RBAC](iam-rbac.md)
5. [Active Directory](active-directory.md)
6. [LDAP](ldap.md)
7. [Kerberos](kerberos.md)
8. [OAuth 2.0](oauth-2.md)
9. [OpenID Connect](openid-connect.md)
10. [SAML](saml.md)
11. [Secrets management](secrets-management.md)
12. [Encryption at rest a in transit](encryption-at-rest-and-in-transit.md)
13. [Vulnerability a patch management](vulnerability-and-patch-management.md)
14. [Threat modeling](threat-modeling.md)

Aktuálny blok uzatvára Threat modeling. Nasledujúci blok rozšíri sekciu o Supply-chain security, SBOM a Image signing; neskôr pokračuje Policy as Code a Zero Trust.

## Cieľ zvládnutia

Po dokončení aktuálneho bloku má byť možné:

### Security goals a risk

- vysvetliť Confidentiality, Integrity a Availability ako samostatné bezpečnostné ciele,
- analyzovať trade-offy medzi jednotlivými osami CIA,
- identifikovať assets, threats, vulnerabilities, impacts a risks,
- rozlíšiť preventívne, detekčné, corrective, recovery a compensating controls,
- vysvetliť rozdiel medzi existenciou controlu a assurance o jeho účinnosti,
- aplikovať CIA na data at rest, in transit a in use,
- vytvoriť CIA matrix pre application, cloud, Kubernetes, CI/CD, observability a AI systém.

### Authentication, authorization a auditing

- rozlíšiť identity proofing, enrollment, authentication, authorization, accounting a auditing,
- vysvetliť identity, account, subject, principal, credential, authenticator, session a token,
- navrhnúť credential a session lifecycle vrátane rotation, revocation a recovery,
- odlíšiť human a workload authentication a rozpoznať phishing-resistant MFA,
- modelovať authorization decision cez principal, action, resource a context,
- vysvetliť Policy Administration, Decision, Enforcement a Information Points,
- rozlíšiť ACL, RBAC, ABAC, relationship a policy-based access control,
- navrhnúť audit records s actor, delegated identity, action, target, result a correlation,
- oddeliť authentication success od resource authorization,
- diagnostikovať authentication, authorization a audit-pipeline failures.

### Least privilege a IAM governance

- navrhnúť least privilege cez action, resource, data, environment a time scope,
- rozlíšiť standing privilege, just-in-time access a just-enough administration,
- používať separation of duties, permissions boundaries, access reviews a break-glass model,
- identifikovať privilege creep, indirect privilege escalation a stale credentials,
- aplikovať least privilege na Linux, Kubernetes, cloud, CI/CD a AI agents,
- vysvetliť IAM ako širší lifecycle než samotný RBAC,
- navrhnúť joiner-mover-leaver proces a authoritative identity source,
- vykonávať role engineering bez role explosion,
- kombinovať RBAC a ABAC s dôveryhodnými attributes,
- vysvetliť Kubernetes Role, ClusterRole, RoleBinding a ClusterRoleBinding,
- testovať IAM/RBAC policies positive aj negative cases a vysvetliť effective access path.

### Active Directory

- vysvetliť forest, domain, OU, domain controller, partitions a Global Catalog,
- odlíšiť forest security boundary od domain a OU administrative scope-u,
- vysvetliť DNS, DC locator, sites, subnets a client affinity,
- pomenovať a vysvetliť FSMO roles,
- vysvetliť multimaster replication, metadata, topology a convergence,
- rozlíšiť Kerberos authentication, LDAP directory access a Windows authorization,
- navrhnúť group scopes, delegation, Group Policy a service-account lifecycle,
- vysvetliť privileged tiering, backup, DSRM a forest recovery,
- odlíšiť AD DS, Microsoft Entra ID a Microsoft Entra Domain Services,
- diagnostikovať domain logon, replication a Group Policy failures.

### LDAP

- vysvetliť DIT, DN, RDN, entries, object classes, attributes a schema,
- používať Bind, Search, Modify a LDAP result-code model,
- rozlíšiť StartTLS a LDAPS a validovať certificate identity,
- navrhnúť search base, scope, filter, projection, controls a referrals,
- zabrániť LDAP injection cez správne DN/filter escaping,
- navrhnúť minimal service account a attribute-level access,
- vysvetliť group resolution, indexes, replication a consistency trade-offy,
- rozlíšiť LDAP protocol, OpenLDAP, AD DS a OIDC integration,
- diagnostikovať connection, TLS, Bind, Search, limit a replication failures.

### Kerberos

- vysvetliť realm, principal, KDC, AS, TGS a application exchange,
- rozlíšiť TGT, service ticket, authenticator, credential cache a keytab,
- vysvetliť KVNO, encryption types, pre-authentication a mutual authentication,
- analyzovať dependencies na čas, DNS, service principal names a KDC availability,
- navrhnúť ticket lifetime, renewal, forwarding a delegation podľa risku,
- vysvetliť cross-realm trust, AD integration, PAC a NTLM fallback,
- odlíšiť Kerberos authentication od LDAP directory access, TLS a application authorization,
- chrániť keytabs a reagovať na service-key alebo KDC compromise,
- diagnostikovať AS, TGS, service-side, SPN, clock-skew, enctype a KVNO failures.

### OAuth 2.0

- rozlíšiť resource ownera, clienta, authorization server a resource server,
- vysvetliť Authorization Code + PKCE vrátane `state`, redirect URI a transaction bindingu,
- rozlíšiť access token, authorization code, refresh token a client credential,
- navrhnúť scope a audience podľa least privilege a confused-deputy threatu,
- odlíšiť opaque a JWT access tokens a ich introspection/revocation trade-offy,
- používať refresh-token rotation a reuse detection,
- rozlíšiť public a confidential clients a správne client authentication metódy,
- vysvetliť Client Credentials, Device Authorization a token-exchange use cases,
- odlíšiť bearer a sender-constrained tokens cez mTLS alebo DPoP,
- rozpoznať deprecated implicit a resource-owner-password patterns,
- diagnostikovať authorization, token exchange, `401` a `403` failures.

### OpenID Connect

- vysvetliť OpenID Connect ako authentication vrstvu nad OAuth 2.0,
- rozlíšiť ID Token, access token, UserInfo a application session,
- validovať `iss`, `sub`, `aud`, `azp`, `exp`, `iat` a `nonce`,
- používať identity key `issuer + subject` namiesto emailu,
- vysvetliť public a pairwise subject identifiers,
- používať discovery a JWKS s dôveryhodným issuer bootstrapom,
- navrhovať claims mapping, ACR, AMR, `auth_time` a step-up authentication,
- rozlíšiť local, front-channel a back-channel logout,
- bezpečne riešiť account linking a multi-tenant federation,
- vysvetliť workload identity federation cez krátkodobé OIDC assertions,
- diagnostikovať issuer, signature, audience, nonce, claims a session failures.

### SAML

- rozlíšiť assertion, protocol, binding a profile,
- vysvetliť IdP, SP, AuthnRequest, Response a Assertion Consumer Service,
- rozlíšiť SP-initiated a IdP-initiated browser SSO,
- používať metadata, entity ID a certificate rollover ako trust contract,
- validovať XML signature, issuer, audience, destination, recipient, čas a `InResponseTo`,
- chrániť RelayState a používať replay cache,
- vysvetliť NameID, SubjectConfirmation, Conditions, authentication context a attributes,
- rozpoznať XML Signature Wrapping, XXE a XML parsing riziká,
- odlíšiť signing a XML encryption key lifecycle,
- navrhnúť local session a realistické Single Logout semantics,
- diagnostikovať signature, ACS, audience, clock-skew a attribute-mapping failures.

### Secrets management

- klasifikovať static, dynamic, authentication, cryptographic a recovery secrets,
- vysvetliť secret zero a preferovať workload identity pred shared bootstrap credentials,
- navrhovať celý secret lifecycle od issuance po secure destruction,
- rozlíšiť rotation, revocation, versioning, lease a renewal,
- vyhodnotiť environment, file, sidecar, CSI a direct-API delivery patterns,
- navrhnúť cache a fail-open/fail-closed model podľa secret type-u,
- vysvetliť Kubernetes Secret hranice, etcd encryption a indirect Pod access,
- používať dynamic database credentials, short-lived certificates a transit cryptography,
- vysvetliť Vault auth methods, policies, tokens, secrets engines a audit devices,
- vysvetliť seal, Shamir shares, recovery keys, auto unseal a KMS/HSM dependency,
- navrhnúť Vault HA, snapshot, DR a application behavior počas outage-u,
- reagovať na secret leakage v Git-e, CI logs, images alebo Terraform state.

### Encryption at rest a in transit

- rozlíšiť data at rest, in transit a in use a priradiť im správne threat boundaries,
- odlíšiť encryption od encoding, hashingu, MAC a digital signature,
- vysvetliť symmetric, asymmetric a hybrid cryptography,
- používať AEAD a vysvetliť nonce, IV, authentication tag a AAD,
- navrhnúť DEK, KEK a envelope-encryption model s oddelenými permissions,
- riadiť key lifecycle, cryptoperiod, rotation, rekey, re-encryption, rewrap a revocation,
- vyhodnotiť full-disk, volume, file, database, object-storage a backup encryption boundaries,
- vysvetliť TLS handshake, certificate chain, hostname validation a forward secrecy,
- navrhnúť certificate lifecycle, mTLS, TLS termination a interný service-to-service encryption model,
- vysvetliť Kubernetes etcd encryption at rest a KMS dependency,
- pripraviť crypto inventory, agility a post-quantum migration model,
- diagnostikovať key access, corrupted ciphertext, certificate, trust-chain, SNI a protocol failures.

### Vulnerability a patch management

- rozlíšiť vulnerability, weakness, exposure, misconfiguration, patch, mitigation a upgrade,
- vysvetliť vulnerability-management lifecycle od inventory po verified remediation,
- vytvoriť asset a software inventory použiteľný na ownership, prioritization a runtime verification,
- vysvetliť CVE, CNA, NVD, CPE, Package URL a limity version-based detection,
- rozlíšiť scanner finding, false positive, false negative a vendor backport,
- používať CVSS v4.0, EPSS, KEV, exploit evidence, exposure a asset criticality ako samostatné risk signals,
- navrhnúť routine a emergency patching cez test, rings, maintenance, rollback a verification,
- patchovať immutable images, containers, Kubernetes nodes, managed services, firmware a dependencies,
- riešiť EOL assets, vulnerability exceptions, virtual patching a remediation debt,
- odlíšiť patch deployment od effective runtime remediation,
- prepojiť active exploitation s incident response a persistence investigation,
- merať risk reduction, SLA age, exposure window, reopen rate a inventory coverage bez metric gamingu.

### Threat modeling

- definovať security objectives, scope, assets, actors, attacker model, assumptions a dependencies,
- identifikovať entry points, exit points a trust boundaries vrátane identity a administrative boundaries,
- vytvoriť Data Flow Diagram s external entities, processes, data stores a data flows,
- písať konkrétne threat statements s actorom, condition, assetom a impactom,
- používať abuse cases, misuse cases, STRIDE, attack trees, CAPEC a ATT&CK primerane ich účelu,
- rozlíšiť likelihood, impact, risk treatment, mitigation a residual risk,
- premeniť threats na testovateľné security requirements a negative tests,
- modelovať authentication, authorization, multi-tenancy, cloud, Kubernetes, CI/CD a secrets boundaries,
- zahrnúť availability, privacy, observability, recovery a unsafe fallback behavior,
- udržiavať threat model vo version control a aktualizovať ho pri architecture, trust alebo incident changes,
- prepojiť threat modeling s design review, pen testingom, red teamingom a incident learnings,
- diagnostikovať nejasný scope, chýbajúce boundaries, generic threats a controls bez verification evidence.

## Stav

| Téma | Status | Úroveň |
|---|---|---|
| CIA triáda | Learning | L2 |
| Authentication, authorization a auditing | Learning | L2 |
| Least privilege | Learning | L2 |
| IAM a RBAC | Learning | L2 |
| Active Directory | Learning | L2 |
| LDAP | Learning | L2 |
| Kerberos | Learning | L2 |
| OAuth 2.0 | Learning | L2 |
| OpenID Connect | Learning | L2 |
| SAML | Learning | L2 |
| Secrets management | Learning | L2 |
| Encryption at rest a in transit | Learning | L2 |
| Vulnerability a patch management | Learning | L2 |
| Threat modeling | Learning | L2 |
