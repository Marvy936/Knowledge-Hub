# Zero Trust

Zero Trust je súbor security princípov a architecture patterns, ktoré odstraňujú implicitnú dôveru založenú iba na network location, asset ownership alebo predchádzajúcom prístupe. Každý access request k enterprise resource-u sa má vyhodnotiť podľa identity, resource-u, device alebo workload posture, kontextu, policy a dostupnej telemetry.

Zero Trust nie je jeden produkt, VPN replacement ani synonymum pre MFA alebo microsegmentation.

```text
subject alebo workload
→ požiada o konkrétny resource a action
→ policy engine vyhodnotí identity, posture, context a risk
→ policy administrator pripraví enforcement decision
→ policy enforcement point povolí, obmedzí alebo odmietne session
→ telemetry priebežne ovplyvňuje ďalšie decisions
```

## 1. Mentálny model

```text
žiadna implicitná dôvera podľa siete
+ explicitná identity
+ resource-specific least privilege
+ device/workload posture
+ per-request alebo bounded-session authorization
+ continuous telemetry
+ predpoklad možného compromise
→ zmenšený blast radius a presnejšie decisions
```

Zero Trust nezaručuje nulové riziko. Znižuje neistotu a implicitné transitive trust paths.

## 2. Čo Zero Trust nie je

Zero Trust nie je:

- automatické nedôverovanie všetkým ľuďom,
- zákaz interných sietí,
- odstránenie firewallov,
- povinný service mesh,
- jedna identity platforma,
- iba remote-access proxy,
- iba microsegmentation,
- iba „never trust, always verify“ slogan.

Architecture musí riešiť identity, resources, policy, enforcement, telemetry, lifecycle a recovery.

## 3. Resource-centric protection

Tradičný perimeter model často chráni segment alebo network zone.

Zero Trust sa sústreďuje na resource:

- application,
- API,
- data object,
- database,
- workload,
- administrative interface,
- workflow,
- device capability.

Network segmentation zostáva control, ale network membership nie je dostatočný authorization dôkaz.

## 4. Žiadna implicitná network trust

Prítomnosť v LAN, VPC, VPN, clusteri alebo corporate Wi-Fi nesmie sama udeliť access.

Network location môže byť contextual signal, nie root identity.

```text
source IP alebo subnet
≠ overený user
≠ overený workload
≠ povolenie ku konkrétnemu resource-u
```

## 5. Assume breach

Assume breach znamená navrhovať s predpokladom, že:

- credentials môžu uniknúť,
- endpoint môže byť compromised,
- interný workload môže byť malicious,
- network path môže byť pozorovaný alebo manipulovaný,
- trusted service môže byť zneužitá ako deputy,
- attacker môže mať persistence.

Výsledkom majú byť kratšie trust paths, obmedzené sessions, detection a recovery, nie fatalizmus.

## 6. Least privilege per resource

Access má byť obmedzený podľa:

- subject identity,
- action,
- exact resource,
- data scope,
- environment,
- time,
- device/workload state,
- delegation context.

Broad network access po successful login je opakom resource-level Zero Trust.

## 7. Dynamic policy

Decision sa nemá opierať iba o statickú group membership.

Môže zahŕňať:

- authentication strength,
- device compliance,
- workload attestation,
- resource sensitivity,
- user risk,
- behavior anomalies,
- location a network,
- time,
- vulnerability state,
- active incident status.

Každý attribute potrebuje trusted source, freshness a failure semantics.

## 8. Discrete authentication a authorization

Authentication a authorization sú samostatné.

```text
authentication → kto alebo čo žiada

authorization  → či smie vykonať action na resource-e v danom context-e
```

Successful MFA neznamená automaticky access ku všetkým applications alebo data.

## 9. Session nie je permanentná dôvera

Po vytvorení session sa môžu zmeniť:

- device posture,
- risk signal,
- account status,
- resource classification,
- network path,
- credential revocation,
- incident state.

Session potrebuje bounded lifetime, re-evaluation triggers a revocation path.

## 10. Continuous verification

Continuous verification neznamená vykonať full authentication pri každom packet-e.

Znamená:

- krátke alebo primerané session lifetimes,
- re-evaluation pri významnej zmene,
- telemetry počas session,
- token/session revocation,
- step-up authentication,
- policy refresh.

Cadence musí zodpovedať risku a system performance.

## 11. Trust nie je jediné číslo

Niektoré implementácie používajú risk alebo trust score.

Jedno číslo môže zakryť:

- rozdielne resource risks,
- chýbajúce hard requirements,
- neporovnateľné signals,
- nejasnú calibration,
- attacker manipulation.

Preferuj explicitné policy conditions a vysvetliteľné risk signals; score môže byť doplnok.

## 12. NIST logical components

NIST SP 800-207 definuje core logical components:

- Policy Engine — PE,
- Policy Administrator — PA,
- Policy Enforcement Point — PEP.

```text
Policy Engine vyhodnotí policy
→ Policy Administrator vytvorí alebo ukončí communication path
→ Policy Enforcement Point presadí access
```

Tieto roly môžu byť implementované viacerými produktmi alebo services.

## 13. Policy Engine

Policy Engine rozhoduje o access-e podľa:

- enterprise policy,
- subject identity,
- asset/device state,
- resource attributes,
- threat intelligence,
- activity logs,
- contextual data.

PE musí byť chránený pred spoofed attributes a stale data.

## 14. Policy Administrator

Policy Administrator vykonáva decision control-plane action:

- vydá alebo nakonfiguruje session credential,
- nastaví PEP,
- povolí communication path,
- ukončí session,
- koordinuje authentication alebo token issuance.

PA nie je to isté ako Policy as Code PAP; názvy sa prekrývajú, ale architecture role je odlišná.

## 15. Policy Enforcement Point

PEP je boundary medzi subjectom a resource-om.

Príklady:

- identity-aware proxy,
- API gateway,
- host agent,
- service-mesh proxy,
- database proxy,
- application middleware,
- cloud access broker,
- Kubernetes admission alebo network enforcement component.

PEP musí byť umiestnený tak, aby resource nebol dostupný bypass pathom.

## 16. Control plane a data plane

```text
control plane
→ identity, policy, posture, decision, session setup

data plane
→ actual application alebo data traffic
```

Control-plane compromise môže udeliť široký access. Data-plane isolation sama neochráni compromised PE/PA alebo identity provider.

## 17. Enterprise identity

Human identity model potrebuje:

- authoritative source,
- lifecycle,
- phishing-resistant authentication,
- risk-based step-up,
- role/attribute governance,
- session management,
- recovery,
- revocation.

Zero Trust nad stale accounts a broad groups iba automatizuje existujúcu privilege chybu.

## 18. Phishing-resistant MFA

Pre high-value resources preferuj authenticators viazané na origin a cryptographic proof, napríklad FIDO2/WebAuthn.

SMS alebo push-only MFA môže byť lepšie než password-only, ale zostáva náchylné na phishing, fatigue alebo SIM risk podľa metódy.

Authentication strength má byť explicitný policy input.

## 19. Identity proofing a enrollment

Silná runtime authentication nevyrieši slabý enrollment.

Modeluj:

- kto môže vytvoriť identity,
- ako sa overuje osoba alebo workload,
- kto vydáva authenticator,
- recovery process,
- duplicate identities,
- delegated onboarding,
- device binding.

Compromised recovery path obchádza primárne MFA controls.

## 20. Device identity

Device identity môže byť založená na:

- managed certificate,
- hardware-backed key,
- MDM enrollment,
- TPM attestation,
- cloud instance identity,
- registered device record.

Device identity neznamená device health. Stolen alebo compromised managed device môže stále preukázať svoju identity.

## 21. Device posture

Posture signals môžu zahŕňať:

- OS a patch level,
- disk encryption,
- secure boot,
- EDR health,
- local firewall,
- screen lock,
- jailbreak/root state,
- certificate status,
- vulnerability a configuration state.

Posture data potrebujú freshness, anti-spoofing a explicitný behavior pri nedostupnom agentovi.

## 22. Managed oproti unmanaged devices

Unmanaged device nemusí byť vždy úplne zakázaný.

Policy môže povoliť:

- browser-isolated access,
- read-only data,
- low-sensitivity resource,
- no-download session,
- virtual desktop,
- stronger step-up,
- kratšiu session.

Resource classification určuje, či je takýto constrained access prijateľný.

## 23. Workload identity

Service-to-service Zero Trust potrebuje identity workloadu nezávislú od IP adresy.

Možnosti:

- cloud workload identity,
- Kubernetes ServiceAccount token s audience,
- mTLS certificate,
- SPIFFE ID a SVID,
- signed JWT assertion,
- platform-attested identity.

Shared static service credential neguje granularitu a attribution.

## 24. Workload attestation

Workload attestation overuje, že identity sa vydáva správnemu workloadu na správnom node/platform context-e.

Signals môžu zahŕňať:

- scheduler metadata,
- process attributes,
- container identity,
- node attestation,
- cloud instance document,
- binary measurement.

Attestation policy musí brániť tomu, aby compromised node vydával identity ľubovoľným workloads.

## 25. SPIFFE a SPIRE

SPIFFE definuje platform-agnostic workload identity model.

- SPIFFE ID identifikuje workload,
- X.509-SVID alebo JWT-SVID nesie verifiable identity,
- trust domain vymedzuje administrative/security boundary,
- Workload API poskytuje credentials workloads.

SPIRE je implementation, ktorá používa node a workload attestation na vydávanie SVIDs.

## 26. Trust domains a federation

Trust domain nie je iba DNS-like string. Je to trust a administrative boundary.

Federation potrebuje:

- explicitnú výmenu trust bundles,
- mapping identities,
- authorization policy,
- key rotation,
- revocation/failure model,
- tenant a environment isolation.

Federated identity neznamená automaticky federated authorization.

## 27. Service identity a mTLS

mTLS poskytuje mutual endpoint authentication a encrypted channel.

Neurčuje automaticky:

- ktorú business action smie service vykonať,
- tenant scope,
- user delegation,
- data authorization,
- request integrity nad application semantics.

Application alebo proxy policy musí mapovať service identity na resource-level permissions.

## 28. User-to-service delegation

Pri downstream calls rozlišuj:

- service koná vo vlastnom mene,
- service koná v mene usera,
- service má obmedzenú delegated authority.

Propagácia broad bearer tokenu cez všetky services zväčšuje blast radius. Použi audience restriction, token exchange alebo explicitný delegation context.

## 29. Resource inventory

Zero Trust potrebuje vedieť, čo chráni.

Inventory musí zahŕňať:

- applications a APIs,
- data stores,
- administrative interfaces,
- workloads,
- SaaS,
- devices,
- service owners,
- sensitivity,
- dependencies,
- access paths.

Neinventarizovaný resource zostáva mimo policy enforcementu.

## 30. Data classification

Resource-level policy závisí od data classification:

- public,
- internal,
- confidential,
- regulated,
- highly restricted.

Classification má ovplyvniť:

- authentication strength,
- device requirements,
- allowed actions,
- export/download,
- logging,
- session lifetime,
- encryption,
- approval.

## 31. Data-centric controls

Zero Trust sa nemá zastaviť pri connection allow/deny.

Data controls môžu zahŕňať:

- row/column-level authorization,
- tokenization,
- dynamic masking,
- download restrictions,
- DLP,
- usage monitoring,
- purpose-based access,
- retention.

Identity-aware proxy pred aplikáciou nevyrieši broken object-level authorization v aplikácii.

## 32. Network segmentation

Segmentation zostáva dôležitá pre:

- attack-surface reduction,
- lateral-movement containment,
- routing control,
- egress restriction,
- legacy isolation.

Zero Trust mení segmentation z primary trust source na defense-in-depth enforcement boundary.

## 33. Microsegmentation

Microsegmentation vytvára jemnejšie policy boundaries medzi workloads alebo resource groups.

Dobrý design používa:

- stable identities alebo labels,
- explicitné allowed flows,
- default deny podľa scope-u,
- observability,
- staged rollout,
- dependency discovery.

Príliš jemná segmentation bez ownershipu môže vytvoriť policy explosion a operational outage.

## 34. Egress policy

Zero Trust musí riešiť aj outbound access.

Kontroluj:

- ktoré workloads môžu volať external destinations,
- DNS identity a destination category,
- proxy bypass,
- data exfiltration,
- package/update endpoints,
- callback channels,
- SaaS APIs.

Inbound-only microsegmentation necháva exfiltration path otvorený.

## 35. Identity-aware proxy

Identity-aware proxy overuje subject a policy pred prístupom ku konkrétnej application.

Musí riešiť:

- direct backend bypass,
- trusted identity headers,
- header stripping,
- session binding,
- WebSocket/streaming,
- non-HTTP protocols,
- application authorization.

Backend má dôverovať identity contextu iba z authenticated proxy pathu.

## 36. ZTNA

Zero Trust Network Access poskytuje application-specific remote access namiesto broad network tunnelu.

Silný ZTNA model:

- neodhaľuje celý internal network,
- overuje user/device,
- viaže session na application,
- presadzuje least privilege,
- zaznamenáva decisions.

Produkt označený ZTNA môže byť stále iba proxy s broad group rules; architecture treba overiť.

## 37. VPN coexistence

VPN nemusí byť okamžite odstránená.

Migration môže:

- obmedziť VPN routes,
- presunúť moderné apps na ZTNA,
- chrániť legacy apps gatewayom,
- zaviesť per-application policies,
- monitorovať direct paths,
- postupne zrušiť network-wide trust.

VPN connection nesmie automaticky znamenať trusted session.

## 38. SSE a SASE

Security Service Edge — SSE typicky kombinuje cloud-delivered access a security capabilities, napríklad ZTNA, secure web gateway a CASB.

Secure Access Service Edge — SASE kombinuje networking a security service model.

Tieto architecture categories môžu implementovať časti Zero Trust, ale názov produktu nie je dôkaz resource-level policy, identity assurance alebo data governance.

## 39. API gateway

API gateway môže byť PEP pre:

- token validation,
- audience/scope,
- rate limiting,
- schema validation,
- external policy decisions,
- request logging.

Gateway nesmie byť jediný authorization layer, ak backend možno volať priamo alebo potrebuje object-level business policy.

## 40. Service mesh

Service mesh môže poskytovať:

- workload mTLS,
- service identity,
- traffic policy,
- telemetry,
- ingress/egress gateways.

Nerieši automaticky:

- end-user identity semantics,
- database authorization,
- business permissions,
- compromised application process,
- supply-chain trust.

## 41. NIST SP 800-207A cloud-native model

NIST SP 800-207A rozširuje Zero Trust access control pre cloud-native multi-cloud applications.

Zdôrazňuje kombináciu:

- application/service identities,
- API gateways,
- sidecar proxies,
- ingress/egress controls,
- identity-tier a network-tier policies,
- platform-independent workload identity.

Policy musí zostať konzistentná naprieč cloud a on-prem boundaries.

## 42. Kubernetes

Kubernetes Zero Trust model zahŕňa:

- API authentication a authorization,
- workload identity,
- admission policy,
- NetworkPolicy alebo service-mesh policy,
- secret access,
- image/provenance verification,
- namespace/tenant boundaries,
- node trust,
- audit.

Pod v rovnakom clusteri nie je automaticky trusted peer.

## 43. Node a control-plane trust

Compromised node môže:

- pozorovať workloads,
- zneužiť credentials,
- manipulovať network,
- spoofovať local services,
- ovplyvniť attestation podľa modelu.

Control plane a node bootstrap potrebujú strong identity, certificate lifecycle, admission, patching a isolation.

## 44. Cloud identity boundaries

V cloud-e oddeľ:

- human federation,
- workload roles,
- account/subscription/project boundaries,
- organization policy,
- resource policies,
- network paths,
- KMS/secrets permissions.

Jedna organization-wide administrator identity je anti-pattern aj pri strong MFA.

## 45. SaaS access

SaaS Zero Trust controls môžu zahŕňať:

- federated SSO,
- phishing-resistant MFA,
- SCIM lifecycle,
- conditional access,
- device posture,
- session controls,
- OAuth application governance,
- data sharing restrictions,
- audit export.

SaaS provider session a local application session lifecycle musia byť zosúladené.

## 46. Privileged access

Privileged access vyžaduje:

- separate admin identity,
- JIT/JEA,
- approval,
- strong device posture,
- phishing-resistant MFA,
- session recording podľa risku,
- command/resource scope,
- automatic expiry,
- emergency break-glass.

Permanentný domain/cloud admin access odporuje Zero Trust least privilege.

## 47. Machine administration

SSH, RDP, database consoles a management APIs sú high-value resources.

Preferuj:

- identity-aware bastion alebo broker,
- short-lived certificates/tokens,
- no shared passwords,
- session attribution,
- command/audit evidence,
- network isolation,
- no public exposure.

Bastion s broad static credentials iba centralizuje risk.

## 48. Legacy applications

Legacy app nemusí podporovať modernú identity.

Patterns:

- identity-aware proxy,
- protocol gateway,
- virtual desktop,
- network enclave s PEP,
- application modernization,
- constrained service account,
- compensating monitoring.

Gateway nesmie prenášať spoofable identity header po bypass-accessible network path-e.

## 49. IoT a OT

IoT/OT môže mať obmedzenú identity, patching a agent support.

Modeluj:

- device inventory,
- manufacturer identity,
- network behavior allowlist,
- gateway PEP,
- protocol-aware monitoring,
- lifecycle/EOL,
- safety constraints,
- fail-safe behavior.

Aggressive re-authentication alebo blocking môže mať physical availability impact.

## 50. Policy inputs

Zero Trust decision môže používať:

```text
subject identity
+ device/workload identity
+ authentication context
+ resource sensitivity
+ requested action
+ session history
+ threat intelligence
+ behavior telemetry
+ environmental context
```

Každý signal musí mať ownera, source a freshness.

## 51. Context poisoning

Attacker môže manipulovať policy inputs:

- spoofed device posture,
- attacker-controlled headers,
- stale group cache,
- forged geolocation,
- compromised EDR,
- poisoned threat feed,
- misclassified resource.

Policy confidence nemôže byť vyššia než confidence jeho inputs.

## 52. Risk-adaptive access

Risk-adaptive policy môže:

- povoliť,
- odmietnuť,
- vyžiadať step-up,
- obmedziť actions,
- skrátiť session,
- prepnúť na read-only,
- vyžiadať approval.

Risk engine musí byť vysvetliteľný, monitorovaný a chránený pred feedback loops alebo discriminatory proxy attributes.

## 53. Step-up authentication

Step-up sa spúšťa pri:

- sensitive action,
- vyššom transaction risku,
- novom device,
- posture degradation,
- unusual behavior,
- privileged escalation.

Policy musí viazať step-up event na konkrétnu session, action a maximálny vek authentication.

## 54. Token a session binding

Bearer token môže použiť každý držiteľ.

Silnejšie patterns:

- sender-constrained tokens,
- mTLS binding,
- DPoP,
- device-bound session,
- short lifetime,
- audience restriction.

Binding nezabráni zneužitiu compromised endpointu, ktorý má token aj key.

## 55. Continuous diagnostics

Telemetry sources:

- identity provider,
- endpoint management,
- EDR,
- network sensors,
- cloud control plane,
- application logs,
- policy decisions,
- data access,
- vulnerability management.

Telemetry musí byť normalized a correlation-ready bez vytvorenia neobmedzeného privacy surveillance systému.

## 56. Decision a telemetry loop

```text
access request
→ decision
→ session activity
→ telemetry
→ risk/context update
→ continue, constrain alebo terminate
```

Loop potrebuje bounded latency, false-positive management a recovery pri telemetry outage.

## 57. Session termination

Session má byť ukončená pri:

- credential revocation,
- account disable,
- device compromise,
- workload identity invalidation,
- policy change,
- anomalous activity,
- resource emergency lockdown.

Logout UI bez backend token/session revocation nie je dostatočný.

## 58. Policy revocation latency

Meraj čas od:

```text
risk alebo revocation event
→ source update
→ policy/PDP propagation
→ PEP enforcement
→ active session termination
```

Short token lifetime nepomôže, ak privileged session zostáva nezávisle aktívna.

## 59. Visibility a analytics

CISA maturity model uvádza visibility and analytics ako cross-cutting capability.

Potrebná je schopnosť:

- spájať identity, device, workload a resource events,
- detegovať bypass paths,
- merať policy outcomes,
- identifikovať lateral movement,
- spätne vysvetliť decision.

Centralizácia telemetry nesmie vytvoriť nechránenejší high-value data lake.

## 60. Automation a orchestration

Automation môže:

- revoke-nuť sessions,
- quarantine device,
- meniť PEP policy,
- znížiť privilege,
- izolovať workload,
- spustiť incident workflow.

High-impact automated response potrebuje confidence thresholds, approval boundaries, idempotency, rollback a audit.

## 61. Governance

Zero Trust governance zahŕňa:

- resource ownership,
- identity authority,
- policy standards,
- architecture patterns,
- exception process,
- data classification,
- telemetry use,
- privacy,
- vendor interoperability,
- metrics,
- funding a roadmap.

Bez governance vzniknú izolované „zero trust“ produkty bez end-to-end trust reduction.

## 62. CISA maturity model

CISA Zero Trust Maturity Model Version 2.0 používa päť pillars:

- Identity,
- Devices,
- Networks,
- Applications and Workloads,
- Data.

Cross-cutting capabilities:

- Visibility and Analytics,
- Automation and Orchestration,
- Governance.

Maturity model je planning aid, nie product certification ani univerzálny compliance score.

## 63. Maturity stages

CISA model používa maturity progression od tradičného stavu cez initial a advanced k optimal capabilities.

Organizácia môže mať rozdielnu maturity podľa pillar-u.

Priorizácia má vychádzať z risku a dependency orderu, nie z potreby dosiahnuť rovnaké skóre všade.

## 64. Migration strategy

```text
inventory a critical flows
→ identity a device foundations
→ vybrať high-value use case
→ zaviesť PEP a explicitnú policy
→ audit a staged enforcement
→ merať bypass a user impact
→ rozširovať po resource groups
→ odstrániť legacy implicit trust
```

Big-bang replacement perimeteru je vysoko rizikový.

## 65. Use-case prioritization

Dobré prvé use cases:

- internet-exposed admin interface,
- contractor access,
- privileged cloud console,
- high-value SaaS,
- production Kubernetes access,
- service-to-service identity pre critical API.

Vyber use case s jasným resource ownerom, merateľným riskom a kontrolovateľným access pathom.

## 66. Dependency order

Niektoré capabilities závisia od iných:

```text
identity lifecycle
→ strong authentication
→ resource inventory
→ policy a PEP
→ device/workload posture
→ telemetry
→ adaptive automation
```

Adaptive policy nad nepresným inventory a identity mappingom vytvára iba dynamickú nepresnosť.

## 67. Parallel access paths

Počas migrácie môže existovať:

- nový identity-aware path,
- starý VPN/direct path,
- emergency path,
- service account path.

Attacker použije najslabší path. Každý bypass musí byť inventarizovaný, monitorovaný a odstránený alebo explicitne risk-accepted.

## 68. Policy enforcement coverage

Coverage otázky:

- ktoré resources majú PEP,
- ktoré protocols obchádzajú proxy,
- ktoré users/devices nie sú federované,
- ktoré workloads používajú shared credentials,
- ktoré sessions nemožno revoke-nuť,
- ktoré data actions nie sú auditované.

Počet deployed agents nie je coverage resource accessu.

## 69. Availability

Zero Trust components sú availability dependencies:

- IdP,
- device posture service,
- PE/PA,
- PEP,
- certificate authority,
- workload identity system,
- telemetry pipeline.

Definuj degraded behavior per resource. Globálny fail-closed môže zastaviť enterprise; globálny fail-open môže odstrániť kontrolu.

## 70. Degraded modes

Možnosti:

- existing bounded sessions pokračujú,
- nové sessions sú odmietnuté,
- iba low-risk read-only access,
- cached policy s maximum age,
- local break-glass,
- manual approval.

Degraded mode musí mať expiration a alert, inak sa stane permanentným bypassom.

## 71. Identity provider outage

Pri IdP outage rozhodni:

- môžu existujúce sessions pokračovať,
- ako dlho,
- ktoré privileged actions sa zastavia,
- či offline/local emergency identity existuje,
- ako sa zabráni stale-account accessu,
- ako sa obnoví trust po recovery.

Cached authentication bez bounded lifetime neguje revocation.

## 72. Device-posture outage

Behavior môže závisieť od resource sensitivity:

- deny high-risk admin access,
- allow existing low-risk session krátko,
- require managed network a step-up,
- read-only fallback,
- explicit operator override.

„Posture unknown“ nie je to isté ako „device healthy“.

## 73. Workload identity outage

Short-lived SVID/certificate model potrebuje renewal resilience.

Definuj:

- pre-expiry refresh,
- cache,
- clock dependency,
- CA/server HA,
- trust-bundle distribution,
- behavior po expiry,
- emergency rotation.

Neobmedzené predĺženie expired identity znižuje compromise containment.

## 74. Privacy

Zero Trust môže zbierať rozsiahlu identity, device a behavior telemetry.

Governance musí riešiť:

- purpose limitation,
- data minimization,
- transparency,
- retention,
- employee monitoring boundaries,
- access k telemetry,
- automated decision review,
- jurisdiction.

Viac signals nie je automaticky lepšia security.

## 75. Incident response

Zero Trust capabilities môžu podporiť:

- rapid session revocation,
- device/workload quarantine,
- resource-specific lockdown,
- blast-radius analysis,
- identity path investigation,
- policy replay.

Incident response musí vedieť fungovať aj pri compromised IdP, PEP alebo policy plane.

## 76. Compromised identity provider

```text
izolovať issuer/admin path
→ revoke sessions a signing keys podľa scope-u
→ prepnúť critical resources na emergency trust path
→ identifikovať issued tokens/certificates počas windowu
→ obnoviť clean identity control plane
→ re-enroll authenticators podľa risku
→ overiť downstream caches a local sessions
```

Reset passwordov nestačí pri compromised token-signing keys alebo federation configuration.

## 77. Compromised PEP

Compromised PEP môže:

- bypass-nuť decisions,
- meniť identity headers,
- pozorovať plaintext po TLS termination,
- falšovať logs,
- umožniť direct path.

Použi hardened runtime, mutual authentication, configuration signing, attestation, monitoring a defense-in-depth authorization v resource-e.

## 78. Policy-plane compromise

Malicious PE/PA policy môže udeliť system-wide access.

Chráň:

- policy repository,
- review,
- signing/distribution,
- admin identities,
- change alerts,
- last-known-good rollback,
- independent audit.

Zero Trust control plane je high-value asset, nie inherentne trusted magic layer.

## 79. Recovery

Recovery potrebuje:

- offline trust roots,
- break-glass identities,
- clean-room admin devices,
- configuration backups,
- policy/version evidence,
- credential rotation,
- PEP re-enrollment,
- session invalidation,
- testované dependency order.

Backup policy database bez identity keys a trust configuration nemusí byť použiteľný.

## 80. NIST SP 1800-35

NIST SP 1800-35, finalizovaný v júni 2025, poskytuje practice guide s viacerými interoperabilnými Zero Trust example implementations a use cases.

Je to implementation reference a evidence source, nie jediná povinná product architecture.

Organizácia má mapovať patterns na vlastné assets, risks a existing systems.

## 81. Testing

Testuj:

- validný access,
- invalid identity,
- stale/revoked session,
- non-compliant device,
- direct backend bypass,
- cross-tenant access,
- workload identity spoofing,
- posture outage,
- IdP outage,
- policy propagation,
- session termination,
- break-glass.

Zero Trust bez negative a failure tests zostáva architecture claim.

## 82. Adversarial validation

Red-team alebo purple-team scenarios:

- stolen token z managed device,
- compromised internal workload,
- VPN user skúša direct subnet path,
- malicious insider mení posture data,
- PEP header spoofing,
- IdP admin takeover,
- service-mesh sidecar bypass,
- stale policy cache.

Výsledky sa majú vrátiť do threat modelu a migration roadmapy.

## 83. Observability

Sleduj:

- access decisions podľa resource a reason,
- authentication strength,
- posture unknown/fail rate,
- session revocation latency,
- direct-path attempts,
- identity/workload certificate issuance,
- PEP health,
- policy revision,
- fail-open/degraded events,
- cross-segment denied flows,
- break-glass usage.

Raw decision telemetry potrebuje privacy a cardinality controls.

## 84. Metrics

Užitočné metrics:

- percento critical resources za PEP,
- percento accessu viazaného na strong identity,
- device/workload posture coverage,
- standing privilege reduction,
- mean revocation latency,
- session lifetime distribution,
- direct bypass path count,
- legacy shared credential count,
- policy exception age,
- incident blast radius,
- degraded-mode duration.

Počet Zero Trust licenses alebo agents nie je outcome metric.

## 85. Troubleshooting access

```text
resource a action správne identifikované?
→ subject authentication platná?
→ device/workload identity platná?
→ posture data fresh?
→ PE dostal všetky attributes?
→ policy revision správna?
→ PA vytvoril session/path?
→ PEP configuration a health?
→ direct/backend route?
→ application-level authorization?
→ session cache/revocation?
```

## 86. Typické chyby

### User prešiel MFA, ale application vracia 403

Authentication je úspešná, ale resource authorization, tenant mapping alebo device policy odmieta action.

### Proxy povoľuje access, backend odmieta identity

Trusted header alebo token mapping je nekompatibilný, audience nesedí alebo backend správne vyžaduje ďalšiu authorization.

### Service mesh mTLS funguje, ale cross-tenant data unikajú

Channel a service identity sú validné, ale application object-level authorization chýba.

### Posture service outage zablokoval všetkých

Unknown posture bolo globálne mapované na deny bez resource-tier degraded modelu.

### Session zostáva aktívna po account disable

IdP disable sa nepropaguje do application session alebo token revocation pathu.

## 87. Governance model

Definuj:

- executive risk ownera,
- architecture authority,
- identity ownera,
- device/workload owners,
- resource owners,
- policy owners,
- telemetry/privacy governance,
- exception approval,
- migration portfolio,
- incident authority.

Zero Trust je enterprise operating model, nie iba network projekt.

## 88. Anti-patterny

- „internal = trusted“,
- VPN po MFA poskytujúca celý subnet,
- jeden global trust score,
- strong authentication bez resource authorization,
- device certificate považovaný za health,
- service mesh považovaný za kompletný Zero Trust,
- broad shared workload credentials,
- proxy s priamo dostupným backendom,
- posture unknown mapované na healthy,
- permanentný break-glass,
- telemetry bez privacy governance,
- big-bang migration,
- product label použitý ako maturity evidence.

## 89. Kontrolné otázky

1. Čo Zero Trust znamená a čo neznamená?
2. Prečo network location nie je dostatočný trust signal?
3. Aké roly majú Policy Engine, Policy Administrator a PEP?
4. Ako sa líši user, device a workload identity?
5. Prečo device identity nie je device posture?
6. Ako fungujú workload attestation, SPIFFE ID a SVID?
7. Čo mTLS rieši a čo nerieši?
8. Ako sa Zero Trust vzťahuje na microsegmentation a ZTNA?
9. Ako chrániť direct backend bypass?
10. Čo znamená continuous verification v praxi?
11. Ako navrhnúť degraded mode pri IdP alebo posture outage?
12. Aké pillars a cross-cutting capabilities používa CISA model?
13. Ako migrovať bez paralelného slabého access pathu?
14. Ako merať resource a enforcement coverage?
15. Ako obnoviť dôveru po compromise identity alebo policy plane-u?

## Glossary impact

Relevantné pojmy: Zero Trust, Zero Trust Architecture, implicit trust, resource-centric security, assume breach, continuous verification, Policy Engine, Policy Administrator, Zero Trust Policy Enforcement Point, control plane, data plane, device identity, device posture, workload identity, workload attestation, SPIFFE ID, SVID, SPIRE, trust domain, workload federation, identity-aware proxy, Zero Trust Network Access, Security Service Edge, Secure Access Service Edge, microsegmentation, egress policy, risk-adaptive access, step-up authentication, session binding, continuous diagnostics, revocation latency, CISA Zero Trust Maturity Model, Zero Trust pillar, visibility and analytics, automation and orchestration, Zero Trust governance, degraded access mode, direct access bypass, resource enforcement coverage a Zero Trust migration.

## Primárne zdroje

- [NIST SP 800-207 — Zero Trust Architecture](https://csrc.nist.gov/pubs/sp/800/207/final)
- [NIST SP 800-207A — Zero Trust for Cloud-Native Multi-Cloud Applications](https://csrc.nist.gov/pubs/sp/800/207/a/final)
- [NIST CSWP 20 — Planning for a Zero Trust Architecture](https://csrc.nist.gov/pubs/cswp/20/planning-for-a-zero-trust-architecture/final)
- [NIST SP 1800-35 — Implementing a Zero Trust Architecture](https://csrc.nist.gov/pubs/sp/1800/35/final)
- [CISA Zero Trust Maturity Model Version 2.0](https://www.cisa.gov/topics/cybersecurity-best-practices/executive-order-improving-nations-cybersecurity)
- [CISA Modern Approaches to Network Access Security](https://www.cisa.gov/news-events/alerts/2024/06/18/cisa-and-partners-release-guidance-modern-approaches-network-access-security)
- [CISA Microsegmentation in Zero Trust — Introduction and Planning](https://www.cisa.gov/news-events/alerts/2025/07/29/cisa-releases-part-one-zero-trust-microsegmentation-guidance)
- [SPIFFE Concepts](https://spiffe.io/docs/latest/spiffe/concepts/)
- [SPIRE Concepts](https://spiffe.io/docs/latest/spire-about/spire-concepts/)
- [SPIFFE Workload API](https://spiffe.io/docs/latest/spiffe-specs/spiffe_workload_api/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Policy as Code](policy-as-code.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
