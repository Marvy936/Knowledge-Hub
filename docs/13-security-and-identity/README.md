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

Nasledujúci blok rozšíri identity vrstvu o OAuth 2.0, OpenID Connect, SAML a Secrets management. Neskôr sekcia pokračuje cryptography, vulnerability management, supply-chain security, Policy as Code a Zero Trust.

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
