# Zero Trust

Zero Trust je resource-centric security architecture, ktorá neudeľuje implicitnú dôveru iba podľa network location, ownership alebo predchádzajúceho loginu. Každý access sa viaže na exact principal, action, resource a context; rozhodnutie sa presadí na všetkých relevantných paths, session zostáva bounded a zmena identity, posture, policy alebo incident state-u môže existujúcu dôveru zrušiť.

Dominantný model kapitoly je **resource-access lifecycle**:

```text
business operation a protected resource
→ human/workload/device identities a assurance
→ exact action, data a environment scope
→ trusted posture, policy a threat context
→ resource-specific decision
→ bounded session alebo communication path
→ enforcement na každom access path-e
→ continuous evidence a re-evaluation
→ revocation, containment a trust recovery
→ allowed, forbidden a bypass validation
```

Zero Trust nie je produkt. Je to vlastnosť celého access chain-u.

## 1. Resource-centric objective

Začni resource-om a business outcome-om, nie network zone-ou.

Príklad:

```text
resource = prod-eu1/payments-api release state
 action  = deploy exact OCI digest
 subject = approved human request + attested CI workload
 outcome = iba schválený artifact beží v intended clusteri
```

Resource môže byť API operation, database row, secret, deployment, queue, admin console, SaaS tenant alebo recovery workflow. Policy musí vedieť, čo chráni, kto je owner, aký impact má zlyhanie a ktoré priame aj nepriame paths k resource-u existujú.

## 2. Explicit access subject

Zero Trust access subject zahŕňa:

- human, workload a device identity;
- issuer, authenticator a session generation;
- delegation chain;
- requested action a exact resource;
- tenant, data, environment a time scope;
- device/workload posture generation;
- policy a supporting-data revision;
- Policy Engine, Administrator a Enforcement Point;
- created session/credential/path;
- audit a revocation descendants.

```text
principal + action + resource + context → structured decision
```

Interná IP, VPN membership alebo Kubernetes namespace môžu byť contextual signals. Nie sú stabilnou root identity ani všeobecným entitlementom.

## 3. Čo Zero Trust nie je

Zero Trust nie je samotné:

- MFA;
- VPN alebo ZTNA proxy;
- service mesh a mTLS;
- microsegmentation;
- device-management agent;
- policy engine;
- SIEM alebo risk score;
- nákup jedného security produktu.

MFA neoveruje resource permission. mTLS nepozná tenant ani business intent. Microsegmentation nevyrieši broad application credential. Policy bez complete PEP coverage je iba deklarácia.

## 4. Assume breach bez permanentnej nedôvery

`Assume breach` znamená navrhovať s predpokladom, že účet, endpoint, workload, dependency alebo interný path môže byť kompromitovaný. Neznamená to odmietnuť každú operation.

Design preto:

- minimalizuje standing privilege;
- viaže credentials na audience, purpose a short lifetime;
- segmentuje blast radius;
- zachováva attribution;
- sleduje odvodené sessions a credentials;
- umožňuje rýchlu quarantine/revocation;
- testuje direct a alternate paths.

## 5. NIST Policy Engine, Policy Administrator a PEP

NIST SP 800-207 rozlišuje tri logické roly:

**Policy Engine — PE** vyhodnotí enterprise policy a contextual data a vytvorí decision.

**Policy Administrator — PA** zrealizuje control-plane kroky: vydá credential, nakonfiguruje path alebo session ukončí.

**Policy Enforcement Point — PEP** stojí na access path-e a decision reálne presadí.

```text
PE rozhodne
→ PA vytvorí alebo zruší access path
→ PEP povolí, obmedzí alebo odmietne operation
```

NIST Policy Administrator nie je Policy Administration Point z Policy as Code. Názov je podobný, architektonická rola odlišná.

Ak backend zostáva dostupný mimo PEP, správny decision na proxy nie je complete control.

## 6. Control plane a data plane

Control plane spravuje identity, trust roots, posture, policy, issuance, revocation a PEP configuration. Data plane prenáša actual application traffic alebo vykonáva operation.

Control-plane compromise môže meniť access k množstvu resources. Data-plane encryption neochráni pred malicious policy revision. Silný control plane zase nepomôže, ak direct network, local socket, controller alebo node path obíde PEP.

Assurance vyžaduje zhodu:

```text
intended policy generation
= loaded PE/PA/PEP configuration
= observed access-path behavior
```

## 7. Human identity a session lifecycle

Human access potrebuje:

```text
authoritative eligibility
→ identity proofing a account
→ authenticator enrollment
→ authentication event a assurance
→ resource authorization
→ bounded session
→ re-evaluation a revocation
→ recovery alebo offboarding
```

Phishing-resistant WebAuthn zvyšuje assurance authentication eventu. Nevyrieši stale group membership, broad authorization, compromised recovery alebo stolen active session.

Privileged actions môžu vyžadovať fresh step-up, managed admin device, JIT entitlement, approval a explicitný case/change identifier. Step-up token musí byť viazaný na intended application/action a nesmie sa stať broad bearer credentialom.

## 8. Device identity a posture

**Device identity** určuje, o ktorý endpoint ide. **Device posture** opisuje jeho current security state.

Signals môžu zahŕňať:

- managed certificate alebo hardware-backed key;
- OS a patch generation;
- disk encryption a secure boot;
- EDR health;
- local firewall alebo jailbreak/root state;
- measurement time a confidence.

Platný device certificate neznamená healthy device. Fresh posture bez dôveryhodnej device identity nemusí patriť správnemu assetu.

Policy potrebuje source authority, freshness a explicitný behavior pri unavailable alebo conflicting posture data. Privileged administration typicky fail-closed; low-risk read-only operation môže použiť krátko cached restricted mode.

## 9. Workload identity a attestation

Workload identity má identifikovať actual execution context, nie recyklovateľnú IP adresu alebo shared password.

```text
process/Pod požiada local identity agent
→ node a workload evidence vytvoria selectors
→ registration policy overí expected context
→ issuer vydá short-lived credential
→ resource overí identity, audience a authorization
```

Attestation je issuance-time decision, či caller skutočne zodpovedá intended workloadu. Node attestation overuje host/agent boundary; workload attestation konkrétny process alebo Pod.

Short-lived credential znižuje static-secret risk, ale issuance authority, renewal, revocation a node-compromise assumptions zostávajú critical.

## 10. SPIFFE, SVID a SPIRE

SPIFFE definuje platform-neutral workload identity model.

- **SPIFFE ID** je identity v trust domain-e, napríklad `spiffe://prod.atlas.example/payments/settlement-api`;
- **SVID** je cryptographically verifiable X.509 alebo JWT identity document;
- **Workload API** poskytuje workloads short-lived identities a trust bundles;
- **SPIRE** je implementation SPIFFE APIs s Serverom, Agents, registration a attestation.

Trust domain je administrative a cryptographic boundary. Development issuer nesmie automaticky vydávať production identities. Federation vymieňa trust a authentication capability; local resource authorization zostáva samostatná.

## 11. Authentication, mTLS a authorization

mTLS poskytuje encrypted channel a endpoint authentication. Certificate `settlement-api` však nepreukazuje právo refundovať ľubovoľnú platbu.

```text
workload authentication
→ kto vytvoril connection

user delegation
→ v mene koho service koná

resource authorization
→ ktorú action na ktorom resource-e smie vykonať
```

Downstream má overiť workload identity aj delegated user/action context. Propagovanie broad bearer tokenu cez celý service chain zväčšuje blast radius a ničí audience boundaries.

## 12. Least privilege a JIT

Zero Trust realizuje least privilege vo viacerých dimenziách:

- subject;
- action;
- exact resource;
- tenant a data scope;
- environment;
- time a session lifetime;
- authentication assurance;
- device/workload posture;
- delegation;
- network path;
- incident state.

JIT activation má maximum envelope. Approval nemá zmeniť `deploy one digest to prod-eu1` na broad cloud administratora na osem hodín.

## 13. Resource inventory, classification a paths

Organization nemôže chrániť neznámy resource alebo path. Inventory spája:

- resource identity a ownera;
- sensitivity a business impact;
- users a workloads;
- direct, delegated, recovery a automation paths;
- network a application boundaries;
- PEP coverage;
- sessions, credentials a dependencies;
- degraded a break-glass modes.

Data classification musí meniť technický decision: masking, no-download, tenant filter, approval, stronger authentication alebo audit. Label bez enforcementu je iba metadata.

## 14. Network controls a microsegmentation

Segmentation a microsegmentation znižujú reachable attack surface a lateral movement. Stabilnejší model používa workload identity, application role a service relationship namiesto iba IP addresses.

```text
frontend
→ smie volať iba required backend API

backend
→ smie pristupovať iba k svojej database

release runner
→ nemá data-plane path k production database
```

Network allow neznamená business authorization. Application musí stále presadzovať tenant, object a action rules.

## 15. ZTNA, gateways a service mesh

ZTNA alebo identity-aware proxy sprostredkuje access ku konkrétnej application namiesto broad network connectivity. VPN môže coexistovať počas migration, ale nesmie zostať paralelným broad bypassom.

API gateway môže byť PEP pre north-south traffic. Service mesh môže poskytovať workload identity, mTLS a network-tier policy pre east-west traffic. NIST SP 800-207A kombinuje identity-tier a network-tier policies v cloud-native architectures.

Žiadna z týchto vrstiev sama nepozná všetky application/data semantics.

## 16. Dynamic policy a signal contract

Dynamic policy môže používať:

- authentication method a age;
- device/workload posture;
- resource sensitivity;
- vulnerability alebo quarantine state;
- user a behavior risk;
- location alebo network context;
- active incident generation;
- data-classification a tenant attributes.

Každý signal potrebuje provenance, freshness, confidence, failure semantics a ownera. Jedno aggregate trust score nesmie prekryť hard requirement, napríklad missing phishing-resistant step-up pre critical action.

## 17. Continuous verification

Continuous verification neznamená full authentication pri každom packet-e. Znamená:

- bounded session/token lifetime;
- re-evaluation pri high-impact operation;
- event-driven reaction na disable, posture alebo incident change;
- telemetry počas session;
- function revocation path;
- forbidden old-session test.

Session vytvorená za validných podmienok sa môže stať neplatnou. Access model musí vedieť, ktoré sessions, credentials a PEP caches z decisionu vznikli.

## 18. Worked incident `SEC-PAY-51`

Release operation mala tieto identities:

```text
human:       urn:atlas:human:9182
session:     sess-rel-51, WebAuthn, 8 h
admin device: PAW-OPS-17
workload:    spiffe://prod.atlas.example/ci/payments-release
resource:    prod-eu1/payments-api
 action:     deploy sha256:pay7240
policy:      POL-IMG-17
```

Deklarovaný flow používal identity-aware release portal a image admission. Skutočný state:

1. VPN source network a group `release-operators` poskytovali broad access k internal controller endpointu;
2. portal vydal osemhodinový bearer token použiteľný aj na controller API;
3. EDR označil `PAW-OPS-17` ako compromised 19 minút po login-e, no session sa nere-evaluovala;
4. release workflow a digest boli quarantined po `SEC-PAY-50`, ale policy cache a existing token ostali usable;
5. internal `AtlasRelease` controller mal broad ServiceAccount a path mimo intended image PEP;
6. stale `POL-IMG-16` replica a fail-open timeout povolili operation;
7. arm64 runtime spustil `sha256:pay7240-arm`.

Root cause bol **implicit trust v internal network/controller path a one-time authorization bez complete resource enforcement a revocation**. Malicious artifact bol trigger; broad token, stale policy, direct path a 47-minútová revocation latency boli amplifiers.

## 19. Causal evidence

- human authentication a WebAuthn boli validné;
- device posture event existoval, ale nebol naviazaný na session revocation;
- controller call prišiel z VPN/internal path bez identity-aware proxy decision ID;
- bearer token audience zahŕňala portal aj controller;
- workload credential nebol viazaný na exact artifact alebo cluster action;
- policy logs ukázali stale revision a cache hit;
- Kubernetes audit ukázal controller ServiceAccount ako actor, ale human initiator chýbal;
- runtime digest sa líšil od signed subjectu;
- quarantine sa prejavila na new portal requests, nie na direct controller path-e.

Incident preto nebol failure MFA ani mTLS. Failure bol v continuity identity, delegation, resource policy, PEP coverage a revocation.

## 20. Evidence-preserving containment

- zablokovať new deployment issuance a controller writes;
- preserve human/session, EDR, OIDC/SPIFFE, policy, admission, controller a runtime evidence;
- quarantine index a platform digests;
- revoke human session, bearer token a workflow credentials;
- remove controller ServiceAccount broad bindings;
- isolate affected arm64 workloads/nodes podľa forensic potreby;
- zachovať audit correlation pred rebuildom alebo credential rotation.

Blocking IP address alone would not invalidate derived identities or alternate paths.

## 21. Authoritative recovery

1. obnoviť human entitlement a fresh WebAuthn/JIT flow;
2. viazať privileged session na managed admin device a short lifetime;
3. používať workload attestation a audience-bound credential pre exact release service;
4. oddeliť human request, approval a executing workload v audit chain-e;
5. policy vyhodnotí exact action/resource/artifact/cluster generation;
6. všetky portal, controller, CRD, admission a direct API paths prejdú equivalentným PEP;
7. odstrániť network-location trust a broad bearer token;
8. pridať event-driven posture, signer, policy a quarantine revocation;
9. rebuildnúť a podpísať new digest z trusted chain-u;
10. rolloutovať new runtime a retire old digest, sessions, caches a rollback paths;
11. vykonať second operation a bypass tests.

## 22. Degraded mode a break-glass

Identity, posture, policy a workload-identity services sú availability dependencies. Behavior musí byť explicitný.

Príklad production deployment outage:

```text
policy alebo signer verifier unavailable
→ nové production deployments fail-closed
→ existing verified workloads pokračujú
→ known-good recovery digest môže použiť separate break-glass
→ break-glass vyžaduje fresh strong identity, narrow resource a audit
→ po obnovení sa deferred state re-evaluuje
```

Break-glass nesmie používať ten istý compromised policy/control plane ani broad permanent credential. Low-risk read-only resources môžu mať iný bounded degraded mode.

## 23. Revocation a trust recovery

Compromise response sleduje graph:

```text
identity/posture/policy/signer incident
→ new issuance block
→ sessions a tokens
→ delegated credentials
→ workload certificates
→ PE/PA/PEP caches
→ resource paths
→ runtime artifacts
→ trust roots a policy data
```

Recovery je hotová až keď authoritative identity, policy, trust a enforcement generations znovu súhlasia a old credentials, direct paths a quarantined artifacts sú forbidden.

## 24. CISA maturity model a migration

CISA Zero Trust Maturity Model Version 2.0 používa päť pillars:

- Identity;
- Devices;
- Networks;
- Applications and Workloads;
- Data.

Cross-cutting capabilities sú Visibility and Analytics, Automation and Orchestration a Governance. Model je planning aid, nie certification alebo product score.

Migration order:

```text
critical resource inventory
→ identities a access-path map
→ stale privilege removal
→ strong human/workload identity
→ PEP placement a bypass closure
→ audit/observe
→ cohort enforcement
→ revocation/recovery tests
→ old VPN/shared-secret paths retirement
```

Najväčší migration risk je paralelný slabý path.

## 25. Metrics

Meraj outcome a coverage:

- percentage critical resources with complete PEP path inventory;
- human/workload managed identity coverage;
- standing privilege a JIT ratio;
- session/credential revocation latency;
- policy/trust generation convergence;
- direct bypass findings;
- allowed/denied decision explainability;
- stale posture acceptance rate;
- quarantined artifact enforcement latency;
- second-session a second-operation failure rate.

Každá metric potrebuje denominator a scope. `90 % apps use SSO` nehovorí nič o service accounts, direct database access alebo recovery paths.

## 26. Zero Trust acceptance verdict

Architecture spĺňa intended objective, keď:

- protected resources, actions, owners a all paths sú inventoried;
- human, workload a device identities majú authoritative lifecycle;
- authentication, posture, delegation a authorization sú oddelené;
- exact resource/action/data/environment vstupujú do decisionu;
- PE, PA a všetky PEPs používajú intended generations;
- sessions a credentials sú scoped, bounded a attributable;
- network location nie je root authorization;
- direct, controller, recovery a legacy paths nemajú weaker control;
- posture, entitlement, signer, policy a incident events revoke-nú derived trust v bounded čase;
- degraded a break-glass modes sú narrow a tested;
- allowed business operation funguje;
- wrong identity, stale posture, wrong artifact, stale policy, direct path a old session sú odmietnuté;
- druhý login, second operation a recovery drill prejdú.

## 27. Troubleshooting flow

```text
business operation a exact resource
→ human/workload/device principal chain
→ credential issuer, audience a assurance
→ posture/context generation
→ requested action, data a delegation
→ policy inputs a active revision
→ PE decision
→ PA-created session/credential/path
→ PEP enforcement a topology
→ runtime/business result
→ caches, revocation a alternate paths
```

`401` ukazuje authentication alebo credential boundary. `403` môže byť správny authorization deny. `allow` v PE logu pri blocked operation smeruje k PA/PEP alebo data-plane problému. Úspešná operation bez decision logu signalizuje bypass alebo local fallback.

## 28. Earlier controls

- resource/action/data inventory;
- authoritative JML a session lifecycle;
- phishing-resistant step-up pre privileged actions;
- managed admin devices a fresh posture;
- attested short-lived workload identity;
- audience-bound delegation;
- application-level tenant/object authorization;
- identity-aware PEP na všetkých paths;
- microsegmentation bez network trust;
- active-generation telemetry;
- event-driven revocation a quarantine;
- bounded degraded modes;
- direct-path, stale-session a second-operation tests.

## 29. Anti-patterny

### Interná sieť je trusted

Compromised endpoint alebo workload dostane broad reachability a authority.

### MFA equals access

Silná authentication nepreukazuje resource permission ani device health.

### Service mesh equals Zero Trust

mTLS bez business authorization iba autentizuje broad communication graph.

### Dynamic policy zo stale data

Contextual decision nereaguje na current compromise.

### PEP pred hostname, backend otvorený

Attacker použije direct alebo controller path.

### Short-lived token bez revocation graphu

Exposure môže byť kratšia, ale stale session a derived credentials stále prežijú.

### Marketing maturity score

Počet products nahrádza resource coverage a forbidden-path evidence.

## 30. Kontrolné otázky

1. Čo tvorí exact Zero Trust access subject?
2. Prečo network location nie je identity ani entitlement?
3. Ako sa PE, PA a PEP líšia?
4. Ako sa device identity líši od posture?
5. Čo workload attestation overuje pri issuance?
6. Ako SPIFFE, SVID a SPIRE súvisia?
7. Prečo mTLS nevyrieši user delegation a business authorization?
8. Ako resource inventory odhalí parallel weak path?
9. Čo continuous verification znamená a čo neznamená?
10. Ako navrhnúť bounded degraded mode?
11. Ako revocation graph spája sessions, workloads, policy caches a artifacts?
12. Čo musí overiť Zero Trust acceptance verdict?

## Glossary impact

Relevantné pojmy: Zero Trust access subject, resource-access lifecycle, identity-posture generation, explicit resource decision, enforcement-path inventory, parallel trust path, continuous access verdict, delegated-actor continuity, posture-triggered revocation, trust-recovery generation, Zero Trust revocation closure, Zero Trust acceptance verdict a second-operation validation.

## Primárne zdroje

- [NIST SP 800-207 — Zero Trust Architecture](https://csrc.nist.gov/pubs/sp/800/207/final)
- [NIST SP 800-207A — Zero Trust for Cloud-Native Applications](https://csrc.nist.gov/pubs/sp/800/207/a/final)
- [NIST CSWP 20 — Planning for a Zero Trust Architecture](https://csrc.nist.gov/pubs/cswp/20/planning-for-a-zero-trust-architecture/final)
- [NIST SP 1800-35 — Implementing a Zero Trust Architecture](https://csrc.nist.gov/pubs/sp/1800/35/final)
- [CISA Zero Trust Maturity Model Version 2.0](https://www.cisa.gov/sites/default/files/2023-04/zero_trust_maturity_model_v2_508.pdf)
- [CISA Microsegmentation in Zero Trust](https://www.cisa.gov/sites/default/files/2025-07/ZT-Microsegmentation-Guidance-Part-One_508c.pdf)
- [SPIFFE Concepts](https://spiffe.io/docs/latest/spiffe/concepts/)
- [SPIRE Concepts](https://spiffe.io/docs/latest/spire-about/spire-concepts/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Policy as Code](policy-as-code.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->