# Security and Identity

Táto sekcia vysvetľuje bezpečnostné ciele, risk, identity, access control, directory služby, federation, cryptography, secrets, vulnerability management, supply-chain security a Zero Trust. Témy budujú najprv stabilné bezpečnostné princípy a až potom konkrétne protokoly, platformy a produkty.

Cieľom nie je vytvoriť checklist nástrojov. Každá kapitola má vysvetliť chránené assets, trust boundaries, threat model, authorization a identity lifecycle, failure modes, audit evidence, recovery a trade-offy medzi confidentiality, integrity a availability.

## Section-wide learning chain

Sekcia používa jeden súvislý security lifecycle. Začína chráneným business outcome-om a exact subjectom, pokračuje identity a trust transitions, effective enforcementom a auditom a končí revocation, recovery a forbidden-path validation.

```text
business/security objective a protected asset
→ exact identity, resource, release alebo cryptographic subject
→ trust, administrative, data a execution boundaries
→ authoritative identity/configuration/evidence generation
→ authentication, directory, federation alebo build transition
→ policy decision a complete enforcement coverage
→ runtime side effect a audit evidence
→ competing hypotheses a discriminating read-back
→ evidence-preserving containment
→ authoritative recovery a descendant revocation
→ allowed, forbidden, alternate-path a second-operation validation
```

Connected incidents `SEC-PAY-47` až `SEC-PAY-51` držia rovnaký Atlas Payments context. `SEC-PAY-47` spája CIA, AAA, least privilege a IAM/RBAC cez stale entitlement a delegated workload capability. `SEC-PAY-48` spája AD replication, replica-bound LDAP query, fresh Kerberos PAC a OAuth resource authorization. `SEC-PAY-49` spája OIDC, SAML, secrets a cryptographic key-purpose boundaries. `SEC-PAY-50` vedie od vulnerability a threat modelu cez compromised builder po stage-correct SBOM. `SEC-PAY-51` uzatvára exact OCI signing subject, policy enforcement coverage a continuous Zero Trust revocation.

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
15. [Supply-chain security](supply-chain-security.md)
16. [SBOM](sbom.md)
17. [Image signing](image-signing.md)
18. [Policy as Code](policy-as-code.md)
19. [Zero Trust](zero-trust.md)

Sekciu uzatvára Zero Trust. Security and Identity je týmto dokončená v aktuálnom rozsahu roadmapy; ďalšia hlavná sekcia pokračuje SRE and Operations.

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

### Supply-chain security

- modelovať source, dependencies, builder, registry, signing, promotion a runtime ako jeden trust graph,
- rozlíšiť source revision, branch, tag, artifact digest, signature, provenance a attestation,
- navrhnúť protected source workflow vrátane two-party review a control continuity,
- vysvetliť SLSA 1.2 Source a Build tracks a guarantees jednotlivých levels,
- chrániť dependency resolution pred confusion, typosquattingom, namespace takeoverom a mutable references,
- navrhnúť hosted alebo self-hosted runner isolation, ephemeral workers a CI workload identity,
- oddeliť untrusted pull-request execution od build, publish a signing authority,
- vysvetliť hermetic a reproducible builds a ich limity,
- používať platform-generated build provenance a consumer verification,
- vysvetliť TUF role separation a secure-update protections,
- aplikovať supplier due diligence a OpenSSF Scorecard ako evidence, nie certifikáciu,
- reagovať na compromised source, dependency, builder, registry alebo publish identity.

### SBOM

- vysvetliť SBOM ako component a relationship inventory viazaný na konkrétny immutable subject,
- rozlíšiť source, build, analyzed, deployed a runtime inventories,
- vysvetliť SPDX 3.0.1 a CycloneDX 1.7 models a versioned interoperability,
- používať Package URL, CPE, hashes, supplier data a dependency relationships,
- zachytiť direct, transitive, vendored, static-linked, OS a language components,
- správne modelovať container layers, base images a multi-architecture manifests,
- rozlíšiť completeness, accuracy, freshness a deterministic generation,
- odlíšiť SBOM, provenance, vulnerability scan, signature a VEX,
- navrhnúť signed/attested SBOM distribution cez OCI Referrers alebo trusted external channel,
- vybudovať ingestion, normalization, matching, diff a raw-evidence retention,
- mapovať component inventory na artifacts, deployments, owners a remediation,
- definovať quality metrics, procurement contract a correction workflow.

### Image signing

- vysvetliť image signing ako binding immutable OCI digestu na key alebo signing identity,
- rozlíšiť tag, image index, platform manifest, config a layer digests,
- navrhnúť key-based signing lifecycle cez KMS/HSM alebo keyless Sigstore model,
- vysvetliť OIDC identity, Fulcio certificate, Rekor transparency a verification bundle,
- vytvoriť presnú signer policy podľa issuer, repository, workflow, event a environment contextu,
- oddeliť build execution, release verification a signing authority,
- rozlíšiť signature, in-toto Statement, DSSE a predicate-specific attestation,
- viazať provenance a SBOM attestations na exact subject digest,
- používať OCI artifacts, `subject`, `artifactType` a Referrers discovery,
- navrhnúť registry copy, retention, garbage collection a multi-architecture verification,
- presadzovať digest pinning a signature/provenance policy pri promotion alebo admission,
- riešiť trust-root rotation, revocation, quarantine, offline verification a compromise response.

### Policy as Code

- vysvetliť policy intent, executable policy a celý policy lifecycle od authoring-u po retirement,
- rozlíšiť Policy Administration, Decision, Enforcement a Information Points,
- navrhnúť structured decision, explicitný default a combining semantics,
- používať versionované a signed policy bundles s rollout, rollback a revision observability,
- vysvetliť OPA, Rego, undefined result, partial evaluation a WebAssembly execution,
- testovať policies cez positive, negative, boundary, property a differential cases,
- kombinovať shift-left configuration testing s runtime enforcementom a auditom,
- vysvetliť Kubernetes ValidatingAdmissionPolicy, MutatingAdmissionPolicy a CEL failure semantics,
- navrhnúť Gatekeeper ConstraintTemplate/Constraint, audit a multi-enforcement-point model,
- používať aktuálne Kyverno policy types a rozlíšiť Policy Reports od historical audit logu,
- riadiť exceptions, break-glass, canary rollout, decision logs a sensitive-data masking,
- diagnostikovať input, data, revision, distribution, failure-policy a enforcement bypass failures.

### Zero Trust

- vysvetliť Zero Trust ako resource-centric architecture bez implicitnej dôvery podľa network location,
- rozlíšiť Policy Engine, Policy Administrator, Policy Enforcement Point, control plane a data plane,
- navrhnúť human, device a workload identity vrátane posture a attestation boundaries,
- vysvetliť SPIFFE ID, SVID, SPIRE, trust domains a workload federation,
- odlíšiť mTLS, service identity, delegation a application-level authorization,
- používať microsegmentation, egress policy, identity-aware proxy a ZTNA ako samostatné controls,
- aplikovať NIST SP 800-207A model na API gateways, service mesh a multi-cloud workloads,
- navrhnúť risk-adaptive access, step-up, bounded sessions a revocation latency,
- vysvetliť CISA Zero Trust pillars a cross-cutting visibility, automation a governance capabilities,
- plánovať staged migration s inventory, enforcement coverage a odstránením parallel bypass paths,
- navrhnúť degraded modes pre IdP, posture a workload-identity outages,
- reagovať na compromise identity providera, PEP alebo policy plane-u a obnoviť dôveryhodný stav.

## Section-level completion gate

Sekcia je pripravená na používateľskú kontrolu iba vtedy, keď platí celý nasledujúci contract:

1. všetkých 19 authoritative kapitol má dominantný lifecycle a exact security, identity, protocol, artifact alebo resource subject;
2. každá kapitola obsahuje aspoň dva executable protocol, CLI, policy alebo configuration príklady;
3. každý významný príkaz alebo artifact vysvetľuje mechanizmus, očakávaný read-back a hranicu toho, čo výsledok ešte nepreukazuje;
4. configured, published, loaded, effective, runtime a business states zostávajú explicitne oddelené;
5. komplexné failures používajú competing hypotheses, discriminating evidence, evidence-preserving containment a authoritative recovery;
6. recovery overuje allowed outcome, forbidden outcome, alternate alebo delegated path a second session, ticket, rotation, policy decision alebo release operation;
7. directory, federation, secret, cryptographic, supply-chain a policy descendants sú inventarizované a revoke-nuté, nie iba odstránené z jedného source-u;
8. Section 13 sa nenachádza v critical/high learning-depth review queue a zostávajúce low hints sa posudzujú manuálne;
9. navigation, glossary a centrálny review ledger sú synchronizované a dočasné audit artifacts sú odstránené.

Reprodukovateľný practical gate overil všetkých 19 kapitol samostatne. Každá obsahuje substantial connected prose, exact security/identity/protocol/artifact subject, najmenej dva executable protocol, CLI, policy alebo configuration examples a explicitné proof-boundary a recovery language. Section 13 sa nenachádza v critical/high learning-depth review queue; audit zostáva heuristickým review nástrojom, nie dôkazom runtime enforcementu alebo cryptographic correctness.

## Stav

Všetkých **19/19 authoritative kapitol prešlo chapter-by-chapter explanation-depth and practical-example revalidation** a sekcia je `Ready for user review`. Starý per-topic `L2` status scaffold bol odstránený; readiness sa eviduje na úrovni celej sekcie a v centrálnom review ledgeri. Existujúce identity, federation, cryptography, secrets, vulnerability, threat-model, supply-chain, SBOM, signing, Policy as Code a Zero Trust lifecycle-y, executable examples, incidents a descendant-revocation recovery zostali zachované. Repository gate overuje textový a executable inventory, navigation, glossary a audit; reálne directory/federation services, credentials, cryptographic modules, registries, admission/enforcement points ani revocation propagation neboli týmto documentation workflowom vykonané. Stav preto neznamená používateľské `Accepted`, runtime `Verified` ani produkčné `Stable`.
