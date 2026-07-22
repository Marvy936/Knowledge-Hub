# Threat modeling

Threat modeling je systematický engineering proces, ktorým tím analyzuje security a privacy vlastnosti návrhu ešte pred incidentom. Vytvára model assets, actors, data flows, trust boundaries a assumptions, z neho odvodzuje konkrétne attack paths a premieňa ich na mitigations, testovateľné security requirements a residual-risk decisions.

Threat model nie je iba diagram, scanner report ani zoznam OWASP kategórií. Hodnota vzniká v reasoning chain-e:

```text
security objectives a scope
→ system model
→ assets, actors a attacker capabilities
→ trust boundaries a assumptions
→ threat statements a attack paths
→ risk treatment
→ security requirements
→ negative tests a operational evidence
→ residual risk a owner
→ aktualizácia pri zmene alebo incidente
```

## 1. Problém, ktorý threat modeling rieši

Testing a vulnerability scanning pozorujú konkrétnu implementáciu. Mnohé závažné problémy však vzniknú skôr ako design decision: backend dôveruje gateway headeru, všetci tenants zdieľajú broad database credential, recovery flow obchádza MFA alebo build workflow dáva production signing identity untrusted pull requestu.

Takéto flaws nemusia mať CVE ani scanner signature. Threat modeling núti tím pomenovať, komu a čomu dôveruje, čo sa stane pri compromise a ako sa security objective technicky presadí.

Dobrý model tiež znižuje neproduktívny „security brainstorming“. Namiesto nekonečného zoznamu možných útokov sa tím sústreďuje na konkrétny system, actors, boundaries a impacts.

## 2. Threat model ako živý engineering artifact

Threat model je výsledok reasoning procesu, nie jednorazový compliance dokument. Má sa meniť pri novej architecture boundary, identity flow, data class, deployment path, supplier dependency alebo incident finding-u.

Aktualizácia neznamená vždy prekresliť celý system. Tím môže udržiavať stabilný context model a samostatné detailed models pre high-risk flows, napríklad payment approval, artifact signing alebo account recovery.

Model má ownera, review date, source revision alebo architecture version a explicitné open risks. Bez lifecycle-u sa diagram rýchlo odpojí od reality.

## 3. Security objectives

Pred enumeráciou threats definuj, čo má system chrániť. Objective musí byť konkrétny a overiteľný.

Slabý objective:

```text
Systém musí byť bezpečný.
```

Silnejšie objectives:

- tenant A nesmie čítať ani meniť objects tenant-a B;
- payment amount a recipient sa po approval nesmú zmeniť bez nového approval-u;
- production deployment musí byť viazaný na approved source revision a immutable artifact digest;
- compromise jedného workloadu nesmie odhaliť credentials ostatných services;
- výpadok identity providera nesmie spôsobiť broad fail-open access;
- audit trail privileged operation musí identifikovať human initiator-a aj executing workload.

Objective sa neskôr mení na security requirement a negative test. Ak sa nedá overiť, je príliš vágny.

## 4. Scope a jeho hranice

Scope určuje, čo modelujeme teraz: system, feature, flow, environment, data classes, external dependencies a lifecycle stages. Explicitné out-of-scope položky zabraňujú nedorozumeniu, ale nesmú skrývať critical dependency.

Príliš široký scope vytvorí povrchný model typu „internet → cloud → database“. Príliš úzky scope môže ignorovať account recovery, CI/CD alebo backup, cez ktoré sa rovnaký asset dá kompromitovať.

Praktický scope môže byť:

- nový OIDC login a session lifecycle;
- multi-tenant export endpoint;
- Kubernetes image admission;
- secrets delivery do workloads;
- payment approval workflow;
- disaster-recovery restore path.

Scope má uviesť production a non-production rozdiely. Development identity alebo test dataset môže mať iné threats a controls.

## 5. Assets a security impact

Asset je čokoľvek, čo má hodnotiteľný impact pri strate confidentiality, integrity, availability, authenticity alebo accountability.

Assets nie sú iba stored data. Zahŕňajú identities, cryptographic keys, policy, source history, artifacts, audit evidence, business transactions, service availability, model weights, DNS zones a reputation.

Pri každom assete urč:

- ownera;
- required security properties;
- classification a business impact;
- kde vzniká, tečie, ukladá sa a zaniká;
- ktoré copies alebo derivatives existujú;
- recovery requirements.

CI signing identity môže mať väčší systemic impact než jeden application server, pretože umožňuje vytvoriť trusted artifacts pre množstvo environments.

## 6. Actors a principals

Actor je človek, workload, organization alebo external system, ktorý interaguje so scope-om. Principal je identity, pod ktorou system actor-a rozpoznáva pri konkrétnej operation.

Actors môžu byť end users, administrators, support staff, developers, CI robots, services, cloud providers, partners, malicious insiders alebo anonymous attackers.

Label „attacker“ nestačí. Model musí uviesť capability a starting position. Authenticated tenant user má iné paths než cloud administrator alebo compromised Kubernetes Pod.

Treba rozlišovať legitimate actor zneužívajúci allowed feature od external actor-a obchádzajúceho control. Business abuse často vykonáva platne authenticated user.

## 7. Attacker model

Attacker model opisuje, čo adversary vie a môže robiť. Typické dimensions sú:

- initial access a network position;
- credentials, roles alebo stolen tokens;
- knowledge source code-u a architecture;
- control nad clientom, device-om alebo dependency;
- budget, čas a schopnosť opakovať útok;
- insider privileges;
- ability ovplyvniť usera alebo support process;
- persistence po prvom prístupe.

Threat „attacker získa root na všetkých nodes“ má inú usefulness než „authenticated tenant zmení object ID“. Modeluj realistic capabilities a označ extrémne assumptions ako separate scenario.

## 8. Assumptions

Assumption je tvrdenie, na ktorom design stojí, ale system ho nemusí priamo presadzovať.

Príklady:

- gateway je jediný ingress k backendu;
- identity provider správne overuje phishing-resistant MFA;
- build runner je ephemeral a izolovaný;
- KMS private key nie je exportovateľný;
- backup account má oddelenú administration boundary;
- queue zachová message authenticity;
- support operator nemôže sám resetnúť privileged account.

Každá critical assumption potrebuje ownera, evidence a failure consequence. „Gateway je jediný ingress“ sa overuje network topology a direct-backend negative testom. Neoverená assumption je latentný threat.

## 9. Dependencies

Dependency je external component alebo service, ktorého behavior system potrebuje. Môže to byť IdP, KMS, DNS, package registry, cloud control plane, payment provider alebo human approval process.

Pre dependency modeluj:

- identity a trust bootstrap;
- data a privileges, ktoré jej odovzdávaš;
- availability a latency dependency;
- compromise impact;
- update a version lifecycle;
- degraded mode a recovery;
- evidence dostupnú pri incidente.

„Managed service“ neznamená out-of-scope risk. Mení responsibility boundary, nie potrebu threat modelu.

## 10. Entry points a exit points

Entry point je miesto, kde data, command alebo identity vstupujú do scope-u. Exit point je miesto, kde data alebo side effect scope opúšťajú.

Entry points zahŕňajú HTTP API, webhooks, queues, file uploads, admin console, CI trigger, Kubernetes API, database import a support request. Exit points zahŕňajú responses, exports, logs, callbacks, emails, artifact publish, backups a downstream commands.

Modeluj synchronous aj asynchronous paths. Validácia na public API nepomôže, ak rovnakú operation možno spustiť cez queue message alebo internal admin endpoint bez ekvivalentnej authorization.

## 11. Trust boundary

Trust boundary je miesto, kde sa mení identity authority, privilege, tenant, administrative owner, execution isolation, data classification alebo cryptographic protection.

Boundary nemusí byť firewall. Príklady:

- browser ↔ web gateway;
- gateway ↔ backend;
- Pod ↔ node kernel;
- tenant A ↔ shared database;
- CI job ↔ signing service;
- application ↔ KMS;
- production account ↔ backup account;
- human approval ↔ autonomous agent action.

Na boundary sa pýtaj: kto vydal identity, čo system validuje, ktoré fields sú attacker-controlled, aké privilege sa mení a čo sa stane pri bypass-e.

## 12. Administrative a identity boundaries

Network diagram často skryje najdôležitejšie control-plane paths. Threat model má explicitne zobraziť administration a identity systems.

Cloud console, CI platform, source-control organization, certificate authority a MDM môžu meniť trust pre množstvo data-plane resources. Ich compromise má iný blast radius než compromise jedného service-u.

Identity federation vytvára boundary medzi issuerom a relying service. Valid signature nestačí; consumer overuje issuer, audience, subject, tenant a authentication context podľa use case-u.

## 13. Data Flow Diagram

Data Flow Diagram — DFD — reprezentuje external entities, processes, data stores, data flows a trust boundaries. Je to security reasoning model, nie detailný infrastructure inventory.

```text
[Browser]
   │ OIDC code / application requests
   ▼
[Gateway] ── delegated token ──> [Order service]
                                      │ tenant-scoped SQL
                                      ▼
                                  [(Database)]
                                      │ payment request
                                      ▼
                              [Payment provider]
```

Každý flow má uvádzať data type, protocol, identity context a protection. Arrow „API call“ bez informácie o credentiale alebo tenant context-e skrýva relevantné threats.

## 14. Úroveň detailu modelu

Použi hierarchiu modelov:

1. system context — users, major external systems a high-level boundaries;
2. service model — major processes, stores a identity flows;
3. critical-flow model — detailed steps pre high-impact operation;
4. implementation model — fields, tokens, queues alebo state transitions, keď sú security-relevant.

Payment approval potrebuje detailnejší model než static content endpoint. Detail má byť dostatočný na nájdenie rozhodnutí, ale stále udržateľný.

## 15. Data inventory v modeli

Pre každý významný flow urč:

- data class a tenant ownership;
- source, destination a derived copies;
- identity/delegation context;
- integrity a ordering requirements;
- encryption boundary;
- retention a deletion;
- logging a redaction;
- failure behavior.

Model bez dát nevie analyzovať confidentiality, integrity ani privacy. „Service A volá Service B“ nestačí, ak nevieme, či prenáša public metadata alebo decrypt key.

## 16. State a lifecycle

Mnohé threats vznikajú pri state transition, nie pri statickom component-e. Modeluj creation, activation, renewal, revocation, deletion a recovery.

Príklady:

- authorization code sa mení na tokens a local session;
- draft payment sa mení na approved a executed;
- secret sa vydá, renew-ne, revoke-ne a rotate-ne;
- artifact postúpi z build-u do production;
- account recovery vydá nový authenticator.

Pri každom transition urč actor-a, preconditions, idempotency, replay protection a audit.

## 17. Threat statement

Konkrétny threat statement spája actor-a, condition, action, asset a impact.

```text
actor
→ zneužije boundary alebo chýbajúcu condition
→ vykoná action
→ zasiahne asset
→ spôsobí security impact
```

Príklad:

> Authenticated user tenant-a A zmení object ID v API requeste. Service overí platnú session, ale nie ownership objectu, a vráti order tenant-a B, čím poruší tenant confidentiality.

Statement „broken access control“ je iba category. Neurčuje attack path, missing control ani test.

## 18. Abuse a misuse cases

Use case opisuje zamýšľané behavior. Abuse case opisuje, ako actor použije legitímnu feature proti security objective. Misuse môže byť úmyselné alebo neúmyselné nesprávne použitie.

Príklady:

- user exportuje vlastné data → zmení tenant parameter a exportuje cudzie;
- support resetne credential → attacker použije social engineering na reset admin accountu;
- CI publikuje artifact → contributor zmení workflow a získa signing identity;
- webhook aktualizuje state → attacker replay-ne starý signed callback.

Business abuse sa často nenájde generickým scannerom, pretože request je syntakticky validný.

## 19. STRIDE ako elicitation mnemonic

STRIDE pomáha systematicky klásť otázky nad DFD elements a flows:

- **Spoofing** — môže sa actor vydávať za inú identity?
- **Tampering** — môže neautorizovane meniť data, code alebo state?
- **Repudiation** — môže action poprieť alebo chýba attribution?
- **Information Disclosure** — môžu data uniknúť nesprávnemu actorovi?
- **Denial of Service** — môže attacker vyčerpať alebo zablokovať capability?
- **Elevation of Privilege** — môže získať permissions mimo intended role?

STRIDE nie je risk score ani kompletný catalog. Pomáha nájsť threats; tím ich stále musí formulovať konkrétne.

## 20. Spoofing podrobne

Spoofing je nepravdivé preukázanie identity alebo originu. Môže ísť o stolen session, forged proxy header, rogue DNS endpoint, ukradnutý workload certificate alebo unsigned webhook.

Mitigation závisí od boundary:

- phishing-resistant MFA a session binding pre human identity;
- issuer, audience, nonce a signature validation pre tokens;
- mTLS alebo signed requests pre services;
- trusted-proxy configuration pre identity headers;
- credential expiration, rotation a revocation;
- request authentication pre webhooks.

Threat test nemá iba overiť invalid password. Má skúsiť replay tokenu pre nesprávnu audience, direct backend header injection alebo expired workload identity.

## 21. Tampering podrobne

Tampering je neautorizovaná zmena data, code, configuration alebo message sequence. Príkladom je zmena payment amountu, container image substitution, altered Terraform plan alebo policy edit bez review.

Controls môžu byť AEAD/MAC/signature, immutable digest, protected branch, authorization, versioning, concurrency control a replay protection.

Integrity musí pokryť celý semantic object. Signature webhook body nepomôže, ak recipient alebo timestamp ostáva unsigned. Digest artifactu nepomôže, ak deployment používa mutable tag.

## 22. Repudiation a accountability

Repudiation threat vzniká, keď actor môže vierohodne poprieť action alebo system nevie spojiť operation s identity a contextom.

Audit record má zachytiť initiator-a, delegated actor-a, action, target, result, timestamp, policy revision a correlation ID. Shared admin account alebo shared service credential ničí attribution.

Log integrity, time synchronization a retention sú súčasť controlu. Application log pod kontrolou compromised administratora nemusí byť dostatočný evidence source.

## 23. Information disclosure

Disclosure môže nastať cez response, logs, error messages, backups, caches, metrics labels, side channels alebo overbroad data export.

Modeluj nielen primary data store, ale aj derived copies. Secret odstránený z database môže zostať v debug logu, trace attribute alebo Terraform state.

Controls zahŕňajú authorization, data minimization, encryption, redaction, tenant isolation, output encoding a retention. Encryption at rest nevyrieši overprivileged application query.

## 24. Denial of Service

DoS nie je iba vysoký request rate. Môže zneužiť expensive query, regex backtracking, queue growth, lock contention, dependency timeout, unbounded cardinality alebo control-plane quota.

Modeluj resource boundary a asymmetry: malý attacker input môže vyvolať veľký server cost.

Controls zahŕňajú rate limits, quotas, bounded work, timeouts, circuit breakers, backpressure, isolation a capacity reserve. Rate limit na gateway nepomôže proti authenticated tenantovi spúšťajúcemu expensive internal job.

## 25. Elevation of Privilege

Elevation znamená získanie authority mimo intended role. Môže ísť o RBAC wildcard, confused deputy, container escape, policy bypass, role chaining alebo ability meniť code executed privileged pipeline-ou.

Threat model má sledovať indirect privilege. User nemusí mať cloud admin permission, ak môže zmeniť Terraform module, ktorý privileged pipeline automaticky aplikuje.

Controls sú least privilege, separation of duties, permission boundaries, sandboxing, approval a explicitný delegation contract.

## 26. Attack trees

Attack tree začína impact goalom a rozkladá ho na alternative alebo combined attack paths.

```text
Goal: nasadiť malicious production image
├─ ukradnúť release signing identity
├─ kompromitovať trusted builder
├─ presunúť mutable production tag
└─ obísť admission policy
   ├─ direct node runtime access
   └─ privileged exception bez expiry
```

OR branches predstavujú alternatívne paths; AND branches vyžadujú kombináciu steps. Tree pomáha hľadať weakest path a spoločné mitigations.

Attack tree nie je probability model automaticky. Likelihood potrebuje evidence o capabilities a controls.

## 27. CAPEC, ATT&CK a ďalšie knowledge bases

CAPEC je catalog common attack patterns: opisuje, ako adversaries využívajú weaknesses. Pomáha rozšíriť threat enumeration a nájsť známe mechanisms.

MITRE ATT&CK opisuje observed adversary tactics a techniques najmä pre operational intrusion behavior. Je užitočný pri detection a post-compromise paths.

Knowledge base nie je náhrada system modelu. Vyberaj relevantné patterns podľa assets a boundaries. Copy celého ATT&CK matrixu vytvorí veľký, ale neakčný threat list.

## 28. Privacy threat modeling a LINDDUN

Security a privacy používajú rovnaký system model, ale objectives sa líšia. System môže byť secure proti unauthorized accessu a stále porušovať privacy nadmerným collection, linkingom alebo nejasným purpose-om.

LINDDUN používa privacy threat categories ako Linking, Identifying, Non-repudiation, Detecting, Data Disclosure, Unawareness a Non-compliance. Metódy GO, PRO a MAESTRO majú rozdielnu hĺbku.

Privacy model analyzuje data minimization, purpose limitation, transparency, consent, retention a inference. Je vhodné robiť security a privacy analysis paralelne nad rovnakým DFD.

## 29. Likelihood a impact

Risk prioritization kombinuje likelihood a impact, ale obidve veličiny musia mať transparentné assumptions.

Likelihood závisí od attacker capability, exposure, exploit complexity, preconditions a strength controls. Impact závisí od asset value, scope, blast radius, detectability, recovery a legal/business consequences.

Jedno číslo môže skryť uncertainty. Použi qualitative bands s rationale alebo scenario-specific quantitative model, keď sú data dostupné.

Critical low-likelihood control-plane threat môže stále vyžadovať mitigation pre extrémny systemic impact.

## 30. Risk treatment

Pre každý threat zvoľ treatment:

- **mitigate** — znížiť likelihood alebo impact controlom;
- **avoid** — odstrániť unsafe feature alebo path;
- **transfer/share** — preniesť časť financial alebo operational impact, nie responsibility za design;
- **accept** — vedomé rozhodnutie risk ownera;
- **monitor** — získať evidence, keď immediate mitigation nie je primeraná.

Treatment má ownera, deadline a verification. „Accepted“ bez ownera a expiry je iba unresolved threat.

## 31. Mitigation ako mechanism

Mitigation musí uviesť, kde sa presadzuje, aký input používa a ktorý threat step blokuje.

Slabé:

```text
Použiť encryption.
```

Silnejšie:

> API gateway používa TLS server authentication a backend overuje gateway mTLS identity. Application však naďalej vykonáva tenant authorization, pretože TLS nechráni pred overprivileged authenticated gateway requestom.

Defense in depth je užitočná, keď controls zlyhávajú nezávisle. Dve rules v rovnakom compromised policy engine-u nemusia byť nezávislé vrstvy.

## 32. Security requirement

Threat sa má preložiť do testovateľného requirementu.

Threat:

> Tenant A získa object tenant-a B zmenou ID.

Requirement:

> Každá read a write operation musí filtrovať resource podľa authenticated tenant ID v server-side authorization layer. Client-supplied tenant ID nesmie byť authoritative.

Negative test:

> Token tenant-a A požiada o known object ID tenant-a B a dostane deny bez disclosure existence alebo fields.

Requirement má identifikovať scope, enforcement point a expected behavior.

## 33. Negative tests a abuse-case verification

Positive test dokazuje, že intended user journey funguje. Negative test overuje, že prohibited path zlyhá správne.

Testuj:

- cross-tenant object access;
- expired alebo wrong-audience token;
- direct backend bypass gateway;
- replay signed callbacku;
- unauthorized workflow signing;
- missing posture data;
- restore bez required encryption key;
- quota exhaustion a partial failure.

Expected result zahŕňa deny, audit evidence a absence partial side effects. `403` bez kontroly, či data neunikli v response timing alebo logs, môže byť neúplný test.

## 34. Residual risk

Residual risk je risk zostávajúci po controls. Každá mitigation má limitations, dependencies a possible bypass.

Napríklad mTLS znižuje spoofing service identity, ale nerieši malicious authenticated service. Rate limit znižuje request flood, ale nemusí chrániť expensive authenticated query.

Residual risk má business ownera, review trigger a monitoring. Neuvádzaj iba „low“; vysvetli, čo môže stále zlyhať a prečo je to prijateľné.

## 35. Operational evidence a detection

Threat model má určovať, akú evidence potrebujeme počas incidentu. Preventive control bez visibility môže zlyhávať potichu.

Pre critical threats definuj:

- decision logs a audit identity;
- security-relevant metrics;
- detection rule alebo alert;
- correlation IDs;
- evidence retention a integrity;
- runbook a escalation;
- recovery validation.

Threat „signing identity zneužitá“ potrebuje monitoring unexpected signatures, nie iba protected key.

## 36. Fail-open, fail-closed a degraded mode

Dependency outage môže zmeniť security behavior. Threat model musí explicitne analyzovať failure semantics.

Production authorization PDP môže fail-closed, ale outage zablokuje users. Low-risk read-only feature môže použiť short cached decision. Emergency administration môže používať separate break-glass path.

Implicitný fallback „ak security service neodpovedá, allow“ je threat. Degraded mode má obmedzený scope, duration, audit a recovery trigger.

## 37. Multi-tenant systems

Multi-tenancy vytvára logical trust boundary v shared processes, databases, queues a caches. Threat model musí sledovať tenant context na každom flowe.

Časté threats:

- object-level authorization bypass;
- cache key bez tenant dimension;
- shared queue message bez tenant bindingu;
- background job s broad database credentialom;
- logs alebo metrics labels odhaľujúce cross-tenant data;
- administrator alebo support tool bez scoped impersonation.

Isolation môže byť logical alebo physical podľa risku. Dôležité je overiť negative paths a blast radius.

## 38. Cloud, Kubernetes a CI/CD models

Cloud threat model musí obsahovať organization/account boundaries, IAM trust, control-plane APIs, network paths, KMS a managed-service responsibilities.

Kubernetes model musí rozlišovať API authorization, admission, scheduler, kubelet, node kernel, CNI, CSI a application authorization. Namespace nie je automaticky strong tenant boundary.

CI/CD model sleduje source revisions, workflow code, runner isolation, caches, signing identities, registry a deployment policy. Privileged pipeline je indirect admin interface.

Tieto domains majú vlastné technical models, ale rovnaký reasoning process.

## 39. AI-assisted systems

AI/LLM system pridáva model, prompts, retrieval data, tools, agent permissions a third-party providers. Threats zahŕňajú prompt injection, data poisoning, sensitive context disclosure, tool abuse a unsafe autonomous actions.

Model output je untrusted input, aj keď model prevádzkuje organization. Tool call potrebuje schema validation, authorization a bounded permissions.

Human approval musí byť meaningful: approver potrebuje vidieť action, target a impact, nie iba generický „confirm“ button.

## 40. Workshop execution

Effective workshop potrebuje product ownera, architecta, engineers, operations a security facilitatora. Privacy alebo compliance expert sa pridáva podľa data scope-u.

Praktický postup:

1. potvrdiť objectives a scope;
2. walkthrough architecture a critical journeys;
3. označiť assets a boundaries;
4. formulovať threats cez abuse cases a STRIDE;
5. rozložiť high-impact goals na attack paths;
6. priradiť mitigations a requirements;
7. definovať tests, owners a residual risks;
8. zaznamenať unknowns a follow-up evidence.

Facilitator nemá byť jediný autor threats. Engineers poznajú hidden state a failure paths.

## 41. Model-as-code a automation

Threat model možno reprezentovať ako versionované diagrams, YAML/JSON entities, relationships, threats a controls. Automation môže kontrolovať missing owners, stale reviews alebo coverage requirements.

Tools môžu generovať STRIDE questions, ale nedokážu spoľahlivo pochopiť business abuse alebo nezdokumentovaný bypass bez ľudského contextu.

Model-as-code má zmysel, keď znižuje drift a integruje sa s architecture changes. Ak schema núti tím vyplniť stovky fields bez decision value, stáva sa toilom.

## 42. Trigger na aktualizáciu

Threat model aktualizuj pri:

- novej trust boundary alebo external dependency;
- zmene identity, authorization alebo recovery flow;
- novom data type alebo tenant model-e;
- deployment architecture change;
- supplier alebo build-platform change;
- incident, penetration-test alebo red-team finding-u;
- významnej zmene attacker capabilities;
- control retirement alebo exception.

Pull-request template môže pýtať „mení táto zmena trust boundary, sensitive data alebo privileged operation?“ Positive answer spustí targeted review.

## 43. Threat-model debt

Threat-model debt vzniká, keď architecture sa mení rýchlejšie než security reasoning. Symptoms sú outdated diagrams, unowned risks, controls bez tests a repeated incident surprises.

Debt prioritizuj podľa critical flows a change frequency. Nečakaj na perfektný enterprise model; oprav high-impact paths a vytvor udržateľný update process.

Metric „počet threat models“ je slabá. Lepšie metrics sú coverage critical systems, age models, open high risks, requirements with negative tests a findings caused outdated assumptions.

## 44. Kompletný príklad

System:

```text
Browser
→ OIDC provider
→ API gateway
→ Order service
→ PostgreSQL
→ Payment provider
```

Objective: tenant isolation a integrity payment amountu.

Threat 1: tenant A zmení order ID a číta order B. Mitigation: server-side tenant-scoped query. Test: cross-tenant ID returns deny and no data.

Threat 2: attacker replay-ne payment callback. Mitigation: signature covers body, timestamp a event ID; replay cache enforces uniqueness. Test: duplicate valid callback creates no second side effect.

Threat 3: direct access obíde gateway identity header. Mitigation: backend mTLS trusts only gateway workload identity a ignores public client-supplied headers. Test: request z internal network bez gateway certificate is rejected.

Threat 4: IdP outage aktivuje broad fallback. Mitigation: new privileged sessions fail-closed; existing short sessions expire; read-only degraded mode is scoped. Test: inject IdP failure and verify allowed/denied actions.

Residual risk: compromised gateway môže posielať authenticated malicious requests; application-level tenant authorization zostáva independent control.

## 45. Troubleshooting threat modelu

Keď model neprináša actionable findings, skontroluj:

- objectives nie sú príliš všeobecné;
- diagram obsahuje identities a data, nie iba boxes;
- attacker má capabilities, nie iba label;
- boundaries zodpovedajú real topology;
- threats sú statements, nie categories;
- mitigations uvádzajú mechanism a enforcement;
- requirements majú negative tests;
- accepted risks majú ownera;
- model sa viaže na current architecture revision.

Ak pen test opakovane nachádza „neočakávané“ design flaws, model pravdepodobne neobsahuje relevantný flow alebo assumption.

## 46. Časté anti-patterny

**Diagram bez threats.** Architecture documentation nie je threat model.

**STRIDE checklist bez contextu.** Categories sa odškrtajú, ale nevzniknú concrete attack paths.

**Threat bez impactu.** Tím nevie prioritizovať ani vybrať treatment.

**Mitigation ako slogan.** „Use encryption“ neurčuje boundary ani threat step.

**Scanner ako threat model.** Implementation findings nenahrádzajú design reasoning.

**Security-only authoring.** Model neobsahuje hidden operational a business flows.

**Accepted risk bez ownera.** Unresolved threat sa premenoval na acceptance.

**One-time review.** Model sa po architecture change stáva false assurance.

## 47. Kontrolné otázky

1. Ako sa security objective líši od všeobecného security goalu?
2. Ako zvoliť scope bez skrytia critical dependencies?
3. Prečo asset nie je iba stored data?
4. Čo musí obsahovať attacker model?
5. Ako sa assumption líši od dependency a ako ju overiť?
6. Čo je trust boundary mimo network firewallu?
7. Aké data musí niesť DFD flow pre security reasoning?
8. Ako napísať konkrétny threat statement?
9. Ako STRIDE pomáha a aké má limity?
10. Kedy použiť attack tree, CAPEC alebo ATT&CK?
11. Ako sa privacy modeling cez LINDDUN dopĺňa so security modelingom?
12. Ako z threatu vytvoriť testovateľný requirement a negative test?
13. Čo je residual risk a kto ho vlastní?
14. Ako analyzovať fail-open a degraded behavior?
15. Aké cross-tenant threats vznikajú v shared cache a queue?
16. Prečo privileged CI pipeline patrí do threat modelu?
17. Ako modelovať AI tool use a prompt injection?
18. Kedy treba model aktualizovať?
19. Ako merať threat-model quality bez metric gamingu?
20. Vytvor threat model pre OIDC login, payment callback alebo artifact-signing flow.

## Glossary impact

Relevantné pojmy: threat modeling, security objective, threat-model scope, asset, actor, principal, attacker model, assumption, dependency, entry point, exit point, trust boundary, administrative boundary, identity boundary, Data Flow Diagram, data inventory, state transition, threat statement, abuse case, misuse case, STRIDE, spoofing, tampering, repudiation, information disclosure, denial of service, elevation of privilege, attack tree, attack path, CAPEC, MITRE ATT&CK, LINDDUN, likelihood, impact, risk treatment, mitigation, security requirement, negative security test, residual risk, degraded mode, multi-tenant threat, model-as-code a threat-model debt.

## Primárne zdroje

- [OWASP Threat Modeling Project](https://owasp.org/www-project-threat-modeling/)
- [OWASP Threat Modeling Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html)
- [Microsoft Introduction to Threat Modeling](https://learn.microsoft.com/en-us/training/modules/tm-introduction-to-threat-modeling/)
- [Microsoft Threat Modeling Tool](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool)
- [MITRE CAPEC](https://capec.mitre.org/)
- [MITRE ATT&CK](https://attack.mitre.org/)
- [LINDDUN Privacy Engineering](https://linddun.org/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Vulnerability a patch management](vulnerability-and-patch-management.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Supply-chain security →](supply-chain-security.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
