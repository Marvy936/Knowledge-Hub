# Threat modeling

Threat modeling je systematický proces, ktorým tím modeluje assets, actors, architecture, trust boundaries, threats, mitigations, verification a residual risk ešte pred incidentom. Nie je to jednorazový diagram ani brainstorming zoznamu útokov. Je to mechanizmus, ktorý premieňa security reasoning na konkrétne design decisions a testovateľné requirements.

## 1. Mentálny model

```text
security objectives a scope
→ assets a actors
→ architecture a data flows
→ trust boundaries a assumptions
→ threat enumeration
→ attack paths a risk
→ mitigations
→ security requirements
→ verification a negative tests
→ residual risk a ownership
→ update pri zmene alebo incidente
```

Dobrý threat model odpovedá:

- čo chránime,
- pred kým,
- cez aké boundaries,
- akým mechanizmom môže dôjsť k impactu,
- ktoré controls tomu zabránia alebo to odhalia,
- ako overíme, že controls fungujú,
- aký risk zostáva a kto ho vlastní.

## 2. Čo threat modeling nie je

Threat modeling nie je:

- iba penetration test,
- iba compliance checklist,
- automatický scanner,
- všeobecný zoznam OWASP Top 10,
- diagram bez threats,
- threats bez mitigations,
- mitigations bez verification,
- dokument vytvorený raz pred prvým release-om.

Scanner hľadá známu weakness v implementácii. Threat model analyzuje aj design flaws, trust assumptions, business abuse a failure behavior, ktoré nemusia mať CVE ani scanner signature.

## 3. Security objectives

Pred enumeráciou threats definuj požadované outcomes.

Príklady:

- iba správny tenant môže čítať svoje records,
- platobná suma a recipient sa nesmú po approval zmeniť,
- privileged deployment musí byť attributable a reviewovaný,
- compromise jedného workloadu nesmie odhaliť credentials všetkých services,
- výpadok identity providera nesmie spôsobiť unsafe authorization fallback,
- recovery musí obnoviť audit continuity v definovanom RTO.

Objective typu „systém musí byť bezpečný“ nie je testovateľný.

## 4. Scope

Scope definuje:

- system alebo feature,
- environments,
- users a workloads,
- data classes,
- external dependencies,
- administrative planes,
- lifecycle fázy,
- explicitné out-of-scope boundaries.

Príliš široký scope vytvorí povrchný model. Príliš úzky scope skryje critical dependency alebo cross-system attack path.

Praktické scopes:

- nový authentication flow,
- payment service,
- Kubernetes admission path,
- CI/CD pipeline,
- multi-tenant data export,
- secrets platform,
- disaster-recovery procedure.

## 5. Assets

Asset je čokoľvek, čo má hodnotiteľný security impact pri strate, zmene alebo nedostupnosti.

- identities a credentials,
- customer data,
- cryptographic keys,
- source code a artifacts,
- authorization policies,
- audit evidence,
- business transactions,
- service availability,
- model weights alebo proprietary prompts,
- trust a reputation.

Asset nemusí byť iba database table. CI signing identity alebo DNS zone môže mať väčší systemic impact než samotný application server.

## 6. Actors

Actors môžu byť:

- end users,
- administrators,
- developers,
- support operators,
- workloads,
- service accounts,
- external providers,
- malicious insiders,
- anonymous internet attackers,
- compromised users alebo devices,
- supply-chain attackers.

Actor musí mať definované capabilities a access, nie iba label „attacker“.

## 7. Attacker model

Attacker model opisuje:

- motiváciu,
- knowledge,
- budget a čas,
- initial access,
- network position,
- credentials alebo privileges,
- možnosť user interaction,
- control nad dependency,
- schopnosť opakovať útok,
- constraints.

Príklady:

- anonymous remote attacker bez credentialu,
- authenticated user jedného tenant-a,
- compromised Kubernetes Pod,
- malicious repository contributor,
- cloud account administrator,
- attacker s captured access tokenom,
- operator s legitimate decrypt permission.

Threat, ktorý predpokladá root access, má inú likelihood a mitigation než pre-auth remote attack.

## 8. Assumptions a dependencies

Assumption je tvrdenie, na ktorom design stojí:

- identity provider validuje MFA,
- gateway je jediný backend ingress,
- KMS key nie je exportovateľný,
- build runner je ephemeral,
- DNS odpoveď smeruje na trusted endpoint,
- backup account je administratívne oddelený.

Dependency je external component alebo service, ktorého behavior systém potrebuje.

Každá critical assumption potrebuje ownera a verification. Neoverená assumption je latentný threat.

## 9. Entry a exit points

Entry points:

- public API,
- browser form,
- webhook,
- message queue,
- file upload,
- admin endpoint,
- CI trigger,
- Kubernetes API,
- database import,
- support workflow.

Exit points:

- API response,
- data export,
- logs a telemetry,
- callback,
- artifact publish,
- email/SMS,
- backup,
- downstream command.

Modeluj aj asynchronous paths a background workers; threats sa neobmedzujú na HTTP request.

## 10. Trust boundary

Trust boundary je miesto, kde sa mení:

- identity authority,
- privilege level,
- tenant,
- administrative owner,
- network trust,
- cryptographic protection,
- data classification,
- validation assumption,
- execution isolation.

Boundary nemusí byť firewall. Príklady:

- browser ↔ backend,
- gateway ↔ internal service,
- Pod ↔ node kernel,
- tenant A ↔ shared database,
- CI job ↔ signing service,
- application ↔ KMS,
- production account ↔ backup account,
- human approval ↔ automated agent action.

Väčšina závažných threats vzniká pri nesprávnej validácii alebo autorite na boundary.

## 11. Data Flow Diagram — DFD

DFD používa:

- external entities,
- processes,
- data stores,
- data flows,
- trust boundaries.

```text
[Browser]
   │ OIDC code / session
   ▼
[Web gateway] ── access token ──> [Order service]
                                      │ SQL
                                      ▼
                                  [(Database)]
                                      │
                                      └──> [Payment provider]
```

DFD nie je deployment diagram so všetkými technickými detailmi. Má zobraziť security-relevant flows a boundaries dostatočne presne na threat reasoning.

## 12. Úroveň detailu

Model má byť dosť hlboký na odhalenie security decisions, ale nie tak detailný, že sa nedá udržiavať.

Vytvor viac vrstiev:

1. system context,
2. major services a stores,
3. critical flow detail,
4. implementation-specific model pre high-risk boundary.

Payment authorization alebo artifact signing potrebuje hlbší model než statický public content endpoint.

## 13. Data inventory v threat modeli

Pre každý významný flow urč:

- data type a classification,
- source a destination,
- identity context,
- integrity requirements,
- encryption boundary,
- retention,
- logging a derived copies,
- tenant ownership,
- failure behavior.

Model, ktorý ukazuje iba services bez dát, nevie správne vyhodnotiť confidentiality, integrity ani privacy threats.

## 14. Threat statement

Dobrý threat statement má štruktúru:

```text
actor
→ zneužije condition alebo boundary
→ vykoná action
→ zasiahne asset
→ spôsobí security impact
```

Príklad:

> Authenticated user tenant-a A zmení object ID v API requeste; service overí iba platnú session, nie ownership resource-u, a vráti objednávku tenant-a B, čo poruší tenant confidentiality.

Slabý statement „broken access control“ neurčuje actor-a, path, missing control ani impact.

## 15. Abuse cases a misuse cases

Use case opisuje zamýšľané behavior. Abuse alebo misuse case opisuje, ako actor použije feature proti security objective.

Príklady:

- user exportuje vlastné dáta → zmení tenant parameter a exportuje cudzie,
- support resetne credential → zneužije social engineering na reset admina,
- CI publikuje artifact → contributor modifikuje workflow a získa signing identity,
- webhook aktualizuje stav → attacker replay-ne starý signed callback.

Business abuse často nie je zachytený generic vulnerability scannerom.

## 16. STRIDE

STRIDE je categorization mnemonic:

- Spoofing,
- Tampering,
- Repudiation,
- Information Disclosure,
- Denial of Service,
- Elevation of Privilege.

Pomáha systematicky prejsť elements a flows. Nie je risk score ani kompletný threat catalog.

## 17. Spoofing

Spoofing znamená vydávanie sa za inú identity.

Príklady:

- stolen session token,
- forged service identity header,
- DNS redirection na rogue endpoint,
- workload s ukradnutým certificate,
- account takeover,
- unsigned webhook sender.

Mitigations:

- phishing-resistant authentication,
- issuer/audience/nonce validation,
- mTLS alebo signed requests,
- trusted proxy boundary,
- credential lifecycle a revocation.

## 18. Tampering

Tampering je neautorizovaná zmena dát, code-u, configuration alebo messages.

Príklady:

- zmena payment amount,
- modifikovaný container image,
- altered Terraform plan,
- replay alebo reorder message,
- policy edit bez review,
- ciphertext manipulation bez authentication tagu.

Mitigations:

- AEAD, MAC alebo signatures,
- immutable digests,
- protected branches,
- authorization a separation of duties,
- versioning a concurrency control,
- replay protection.

## 19. Repudiation

Repudiation znamená, že actor môže vierohodne poprieť action alebo systém nevie preukázať jej context.

Príklady:

- shared admin account,
- chýbajúci delegated actor,
- mutable audit logs,
- clock inconsistency,
- absent request correlation,
- action vykonaná cez automation bez initiator identity.

Mitigations:

- unique identities,
- tamper-resistant audit,
- actor + delegated identity,
- trusted time,
- correlation IDs,
- approval a evidence chain.

## 20. Information Disclosure

Information Disclosure je neautorizované odhalenie dát alebo metadata.

Príklady:

- cross-tenant read,
- secret v CI logu,
- verbose error,
- public snapshot,
- broad telemetry payload,
- token v URL,
- plaintext internal hop.

Mitigations:

- object-level authorization,
- encryption a key separation,
- data minimization,
- log redaction,
- network a storage isolation,
- least privilege.

## 21. Denial of Service

DoS znižuje availability alebo vyčerpáva bounded resource.

Príklady:

- request amplification,
- unbounded query alebo upload,
- connection/table exhaustion,
- KMS dependency saturation,
- lock contention,
- poison message crash loop,
- certificate expiry,
- audit sink failure blokujúci requests.

Mitigations:

- quotas a rate limits,
- bounded work,
- backpressure,
- timeouts a circuit breakers,
- isolation a capacity,
- degraded modes,
- tested recovery.

## 22. Elevation of Privilege

Elevation of Privilege umožní actorovi získať vyššiu authority.

Príklady:

- container escape,
- overly broad service account,
- CI job získa production credential,
- user-controlled role mapping,
- writable policy file,
- confused-deputy token propagation,
- support role môže meniť vlastné permissions.

Mitigations:

- least privilege,
- separation of duties,
- deny-by-default policy,
- privileged boundary isolation,
- signed/approved configuration,
- negative authorization tests.

## 23. STRIDE per element

Praktická heuristika:

- external entity: Spoofing, Repudiation,
- process: Spoofing, Tampering, Repudiation, Information Disclosure, DoS, Elevation,
- data flow: Tampering, Information Disclosure, DoS,
- data store: Tampering, Repudiation, Information Disclosure, DoS.

Heuristika pomáha coverage, ale nesmie nahradiť system-specific reasoning.

## 24. Attack trees

Attack tree začína attacker goalom a rozkladá ho na alternatívne alebo kombinované kroky.

```text
Goal: publikovať malicious production artifact
OR
├─ compromise maintainer credential
├─ modify protected workflow
└─ compromise signing service
   AND
   ├─ získať runner execution
   └─ získať sign permission
```

Attack tree je vhodný pre multi-step paths a porovnanie controls na rôznych bodoch.

## 25. Attack paths

Attack path prepája initial access, trust-boundary crossings, privilege transitions a impact.

Príklad:

```text
pull-request code execution
→ shared self-hosted runner
→ cached cloud credential
→ artifact registry write
→ production deployment
```

Lokálne slabý control môže byť kritický, ak otvára path k high-impact authority.

## 26. CAPEC, ATT&CK a threat libraries

CAPEC poskytuje reusable attack patterns. MITRE ATT&CK opisuje tactics a techniques pozorované v adversary behavior.

Použitie:

- doplnenie brainstormingu,
- overenie coverage,
- mapping detection opportunities,
- incident feedback.

Nemajú nahradiť vlastný architecture model. Generic library nevie, kde má tvoj systém trust boundary ani aký business impact má konkrétny flow.

## 27. Likelihood

Likelihood ovplyvňuje:

- attacker access a capability,
- exploit complexity,
- exposure,
- authentication/interaction requirements,
- known exploitation,
- detectability pre attacker-a,
- repeatability,
- existing controls.

Nepoužívaj pseudo-presné čísla bez evidence. Cieľom je konzistentné decision-making, nie matematický dojem istoty.

## 28. Impact

Impact hodnotí:

- confidentiality,
- integrity,
- availability,
- tenant blast radius,
- privileges a trust position,
- financial/business consequences,
- legal a regulatory exposure,
- recovery complexity,
- downstream systems.

Threat voči identity provideru alebo signing keyu má systemic impact, aj keď samotný component neobsahuje customer records.

## 29. Risk treatment

Možnosti:

- avoid — odstrániť feature alebo path,
- mitigate — zaviesť controls,
- transfer/share — napríklad contractual alebo insurance model,
- accept — explicitne prijať residual risk,
- monitor — dočasne sledovať pri neúplnej evidence.

Acceptance musí mať ownera, rationale, expiry alebo review trigger a známy impact.

## 30. Mitigations a control placement

Mitigation musí byť umiestnená tam, kde vie ovplyvniť attack path.

Typy:

- preventive,
- detective,
- corrective,
- recovery,
- compensating.

WAF môže znížiť jeden exploit path, ale neopraví broken object authorization. Encryption at rest nechráni pred application principalom s legitímnym decrypt accessom. Control label bez boundary reasoning je slabý.

## 31. Security requirements

Threat sa musí premeniť na testovateľný requirement.

Threat:

> User tenant-a A zmení order ID a získa record tenant-a B.

Requirement:

> Order service musí pre každý read overiť, že `order.tenant_id` zodpovedá authenticated tenant contextu; mismatch musí skončiť bez odhalenia existence resource-u a musí vytvoriť audit event.

Requirement určuje actor/context, operation, expected behavior a failure semantics.

## 32. Verification

Každá mitigation potrebuje evidence:

- unit alebo policy test,
- integration test,
- negative authorization test,
- architecture/config review,
- runtime observation,
- penetration test,
- failure injection,
- recovery exercise,
- audit query.

„Používame mTLS“ nie je evidence, že backend nie je dostupný plaintext bypass cestou.

## 33. Negative testing

Positive test overí povolený flow. Negative test overí, že zakázaný flow skutočne zlyhá.

Príklady:

- token pre API A nesmie fungovať na API B,
- tenant A nesmie čítať tenant B,
- unsigned callback musí byť odmietnutý,
- old certificate po revocation nesmie autentizovať workload,
- direct backend request s forged headerom musí zlyhať,
- deployment bez approval nesmie získať production authority.

Security control bez negative testu často overuje iba happy path.

## 34. Residual risk

Residual risk zostáva po controls. Dokumentuj:

- remaining attack conditions,
- expected impact,
- detection a response,
- ownera,
- acceptance decision,
- review trigger,
- dependencies.

Threat model nie je dokončený označením všetkých rows ako „mitigated“, ak controls nemajú evidence alebo zostávajú významné bypass paths.

## 35. Authentication threats

Modeluj:

- credential theft,
- phishing,
- MFA bypass a recovery,
- session fixation/replay,
- token audience/issuer confusion,
- account linking,
- service identity spoofing,
- logout/revocation latency,
- fail-open pri IdP outage.

Authentication success nie je resource authorization.

## 36. Authorization threats

Modeluj:

- horizontal access medzi users alebo tenants,
- vertical privilege escalation,
- missing object-level check,
- stale group/role membership,
- user-controlled attributes,
- confused deputy,
- broad wildcard permissions,
- indirect access cez export, search alebo background job,
- admin self-escalation.

Authorization sa musí vyhodnocovať pri každom relevantnom resource/action boundary, nie iba pri login-e alebo gateway-i.

## 37. Multi-tenant systems

Critical invariants:

- tenant context pochádza z trusted identity alebo server-side mappingu,
- resource ownership sa overuje server-side,
- cache a indexes sú tenant-scoped,
- queue messages nesú integrity-protected tenant context,
- KMS/decrypt operation je tenant-bound,
- administrators a support access sú auditované,
- data export a analytics zachovávajú isolation.

Tenant ID z request body nie je sám o sebe authorization evidence.

## 38. Cloud threat modeling

Modeluj:

- account a organization boundaries,
- IAM roles a trust policies,
- control plane vs data plane,
- public endpoints,
- cross-account grants,
- metadata/credential services,
- KMS a secrets dependencies,
- snapshots a backups,
- provider-managed components,
- region a service outages.

Security Group nie je jediná boundary; IAM a resource policies môžu vytvoriť alternate access path.

## 39. Kubernetes threat modeling

Zahrň:

- API server a admission,
- RBAC a service accounts,
- etcd a Secrets,
- node/kubelet boundary,
- container runtime a kernel,
- CNI/NetworkPolicy,
- image registry a admission policy,
- controllers/operators,
- volumes a CSI,
- ingress/egress,
- privileged Pods a host mounts.

Namespace nie je hard multi-tenant security boundary bez ďalších controls.

## 40. CI/CD threat modeling

Assets:

- source integrity,
- build environment,
- signing identity,
- artifacts,
- deployment credentials,
- approvals a provenance.

Threats:

- malicious contributor code,
- poisoned dependency,
- mutable action/tag,
- shared runner persistence,
- secret exfiltration,
- artifact substitution,
- approval bypass,
- environment confusion,
- compromised maintainer.

Pipeline má byť modelovaná ako privileged production system, nie iba automation script.

## 41. Secrets a cryptographic boundaries

Modeluj:

- secret zero,
- workload authentication,
- secret delivery,
- cache a memory,
- rotation/revocation,
- KMS/HSM policies,
- key/ciphertext separation,
- backup recovery,
- audit availability,
- fail behavior pri outage-u.

Short-lived secret znižuje exposure window, ale nevyrieši broad authority ani plaintext leakage v aplikácii.

## 42. Availability a dependency failure

Threat model musí obsahovať neúmyselné aj adversarial failure modes:

- IdP unavailable,
- KMS throttling,
- DNS failure,
- audit sink outage,
- queue poison message,
- database partition,
- certificate expiry,
- rate-limit exhaustion,
- dependency returning stale or malformed data.

Dôležitá otázka nie je iba „zlyhá systém?“, ale „zlyhá bezpečne?“

## 43. Fail-open a fail-closed

Fail-closed odmietne operation pri nedostupnom security dependency. Chráni policy, ale môže spôsobiť outage.

Fail-open pokračuje bez úplného overenia. Zachová availability, ale môže vytvoriť authorization alebo confidentiality breach.

Možné bezpečnejšie degraded modes:

- read-only,
- cached decision s bounded TTL,
- iba low-risk operations,
- explicit break-glass,
- queue-and-retry,
- stop new sessions, zachovať krátko platné existujúce.

Behavior musí byť navrhnutý a testovaný, nie náhodný výsledok exception handlingu.

## 44. Privacy threat modeling a LINDDUN

Security a privacy sa prekrývajú, ale nie sú totožné. LINDDUN kategórie zahŕňajú:

- Linkability,
- Identifiability,
- Non-repudiation,
- Detectability,
- Disclosure of information,
- Unawareness,
- Non-compliance.

Encrypted data môžu stále odhaľovať linkability cez identifiers, timing alebo metadata. Threat model má riešiť data minimization, purpose, consent, retention a user awareness tam, kde sú relevantné.

## 45. Observability ako security boundary

Modeluj:

- ktoré events musia vzniknúť,
- kto môže logy meniť alebo čítať,
- citlivé payloads,
- correlation identity,
- retention,
- alert path,
- audit sink failure,
- log injection,
- telemetry blind spots.

Logging môže byť detective control aj nový disclosure surface.

## 46. Recovery a incident response

Threat model má pokryť:

- backup isolation,
- recovery credentials,
- restore integrity,
- key a certificate dependencies,
- clean-room environment,
- audit continuity,
- revocation počas recovery,
- RPO/RTO,
- attacker persistence.

Backup, ktorý možno obnoviť iba pomocou compromised identity providera alebo strateného KMS keyu, nie je kompletný recovery model.

## 47. Human a AI-assisted workflows

Pri automation alebo AI agentoch modeluj:

- kto zadáva intent,
- aké tools a authority agent má,
- prompt alebo input injection,
- untrusted retrieved content,
- approval boundaries,
- action preview,
- audit actor vs delegated agent,
- bounded scope a rate,
- rollback,
- secret exposure,
- unsafe autonomous retry.

Model output nie je authorization decision ani trusted instruction bez policy enforcementu.

## 48. Threat-modeling workshop

Efektívny workshop potrebuje:

- facilitator-a,
- system ownera,
- developer/architect,
- operations/platform pohľad,
- security expertise,
- pripravený diagram a scope,
- decision log a ownerov.

Priebeh:

1. potvrdiť objectives a scope,
2. prejsť architecture a assumptions,
3. identifikovať assets a boundaries,
4. enumerovať threats,
5. zoskupiť attack paths,
6. prioritizovať,
7. definovať requirements a verification,
8. priradiť ownerov a residual risk.

Workshop nemá skončiť iba fotografiou whiteboardu.

## 49. Otázky počas review

- Odkiaľ pochádza identity a kto jej dôveruje?
- Kde sa mení privilege alebo tenant?
- Ktorý input je attacker-controlled?
- Čo sa stane pri replay?
- Čo sa stane pri stale cache?
- Dá sa obísť gateway, mesh alebo admission?
- Kto môže meniť policy alebo artifact?
- Kde sa objaví plaintext?
- Ako sa revoke-ne credential?
- Ako systém zlyhá pri dependency outage-u?
- Ako zistíme, že control bol obídený?
- Ako obnovíme dôveryhodný stav?

## 50. Model vo version control

Threat model má byť versionovaný spolu s architecture alebo codebase:

- diagrams ako text alebo export s source formátom,
- threat IDs,
- requirements a owners,
- links na tests a issues,
- assumptions a review date,
- residual-risk decisions.

Review diffu ukazuje, či architecture change pridala boundary, data flow alebo privilege.

## 51. Model-as-code

Model-as-code môže umožniť:

- versioning,
- linting,
- generated diagrams,
- traceability na controls,
- automated stale checks,
- reuse threat libraries.

Automation nesmie predstierať úplnosť. Tool nevie sám správne určiť business assets, attacker intent alebo hidden operational assumptions.

## 52. Kedy model aktualizovať

Triggers:

- nový public endpoint,
- authentication alebo authorization zmena,
- nový tenant model,
- nový data class,
- cloud account/region boundary,
- nový external provider,
- CI/CD alebo signing zmena,
- privilege expansion,
- incident alebo near miss,
- major dependency/architecture migration,
- nový failure/degraded mode.

Kalendárny review je doplnok, nie náhrada event-driven update-u.

## 53. Threat-model debt

Debt vzniká, keď:

- diagram nezodpovedá runtime,
- assumptions nie sú overené,
- threats nemajú owners,
- mitigations nemajú tests,
- exceptions expirovali,
- architecture sa zmenila bez review,
- incidents sa nevrátili do modelu.

Sleduj high-risk stale models a requirements bez verification evidence.

## 54. Design review, pen test a red team

Threat modeling riadi, čo treba overiť. Pen test a red team poskytujú empirical evidence a nové attack paths.

```text
threat model
→ hypotézy a test targets
→ pen test/red team
→ findings a observed behavior
→ update threats, controls a assumptions
```

Pen test nenahrádza model; je časovo obmedzený a pozoruje konkrétnu implementáciu.

## 55. Incident feedback

Po incidente aktualizuj:

- attacker model,
- initial access,
- attack path,
- failed assumptions,
- missing controls,
- detection gaps,
- recovery behavior,
- residual risk,
- verification tests.

Incident, ktorý skončí iba patchom bez zmeny modelu, môže opakovať rovnaký design failure inde.

## 56. Metrics

Užitočné metrics:

- percento high-risk systems s aktuálnym modelom,
- threats s ownerom,
- mitigations s verification evidence,
- open high-risk requirements po SLA,
- stale assumptions,
- architecture changes bez review,
- incidents mapované na known vs unknown threats,
- residual-risk decisions po expiry,
- čas od design change po model update.

Počet threats nie je kvalita. Model s 200 generic rows môže byť slabší než 20 konkrétnych attack paths s tests.

## 57. Governance

Organizácia potrebuje:

- scope criteria,
- risk classification,
- required participants,
- approved methods bez dogmatizmu,
- threat/requirement templates,
- ownership a escalation,
- residual-risk approval,
- storage/versioning standard,
- review triggers,
- integration s SDLC, incident response a testing,
- quality review.

## 58. Troubleshooting slabého modelu

### Threats sú príliš všeobecné

Doplň actor-a, boundary, condition, asset a impact.

### Diagram nezobrazuje trust boundaries

Rozdeľ network, identity, tenant, administrative a cryptographic boundaries.

### Všetko má rovnakú prioritu

Použi attack-path feasibility, exposure, privilege a asset impact.

### Controls sú iba názvy produktov

Popíš enforcement point, decision inputs, failure behavior a verification.

### Tím nevie model udržiavať

Zmenši scope, versionuj source, priraď ownera a napoj update na architecture-change workflow.

### Model neodhalil incident

To nie je dôvod model zahodiť. Aktualizuj attacker assumptions, libraries, boundaries a review process.

## 59. Anti-patterny

- modelovanie až po hotovej implementácii bez možnosti design change,
- STRIDE checklist bez architecture contextu,
- „internal network je trusted“,
- authentication považovaná za authorization,
- threat bez asset impactu,
- mitigation bez ownera,
- control bez negative testu,
- všetky residual risks označené ako accepted bez decision authority,
- diagram bez versioningu,
- model ignorujúci failure a recovery,
- tool-generated threats prezentované ako úplné,
- pen test použitý ako jediný threat model.

## 60. Mini príklad

Architecture:

```text
Browser
→ API gateway
→ Order service
→ PostgreSQL
→ Payment provider
→ OIDC provider
```

Assets:

- customer identity,
- orders,
- payment intent,
- tenant isolation,
- API availability.

Critical boundaries:

- browser ↔ gateway,
- gateway ↔ service,
- service ↔ database,
- service ↔ payment provider,
- OIDC provider ↔ application session.

Threats:

1. Stolen access token je použitý na API s nesprávnym audience.
2. User zmení order ID a číta cudziu objednávku.
3. Gateway posiela trusted identity header, ale backend je dostupný priamo.
4. Payment callback je replay-nutý.
5. Compromised Pod použije broad database credential na všetkých tenants.
6. KMS alebo IdP outage zastaví requests bez safe degraded mode.

Mitigations:

- validate issuer, audience a expiry,
- object-level authorization,
- backend isolation a mTLS,
- signed callback + replay cache,
- tenant-scoped database policy/credential,
- explicit timeout, cache a failure behavior.

Verification:

- negative audience test,
- cross-tenant integration test,
- direct-backend access test,
- callback replay test,
- compromised-workload tabletop,
- IdP/KMS failure injection.

## 61. Kontrolné otázky

1. Čo je cieľom threat modeling-u a čo ním nie je?
2. Ako definovať security objectives?
3. Čo je trust boundary a prečo nemusí byť firewall?
4. Aké elements obsahuje DFD?
5. Ako napísať testovateľný threat statement?
6. Čo znamenajú STRIDE categories?
7. Ako sa líši attack tree, CAPEC a ATT&CK?
8. Ako premeniť threat na requirement a test?
9. Čo je residual risk a kto ho vlastní?
10. Ako modelovať multi-tenant authorization?
11. Ktoré boundaries sú kritické v CI/CD?
12. Ako modelovať fail-open a fail-closed?
13. Prečo modelovať observability a recovery?
14. Kedy threat model aktualizovať?
15. Ako incident vracia knowledge späť do modelu?

## Glossary impact

Relevantné pojmy: threat modeling, security objective, scope, asset, actor, attacker model, assumption, dependency, entry point, exit point, trust boundary, Data Flow Diagram, external entity, process, data store, data flow, threat statement, misuse case, abuse case, STRIDE, Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege, attack tree, attack path, CAPEC, MITRE ATT&CK, threat library, likelihood, impact, risk treatment, mitigation, security requirement, negative testing, residual risk, LINDDUN, model-as-code a threat-model debt.

## Primárne zdroje

- [NIST SP 800-154 — Guide to Data-Centric System Threat Modeling](https://csrc.nist.gov/pubs/sp/800/154/ipd)
- [NIST SP 800-218 — Secure Software Development Framework](https://csrc.nist.gov/pubs/sp/800/218/final)
- [Microsoft Security Development Lifecycle](https://learn.microsoft.com/en-us/compliance/assurance/assurance-microsoft-security-development-lifecycle)
- [Microsoft Threat Modeling Security Fundamentals](https://learn.microsoft.com/en-us/training/paths/tm-threat-modeling-fundamentals/)
- [OWASP Threat Modeling](https://owasp.org/www-community/Threat_Modeling)
- [OWASP Threat Dragon](https://owasp.org/www-project-threat-dragon/)
- [MITRE CAPEC](https://capec.mitre.org/)
- [MITRE ATT&CK](https://attack.mitre.org/)
