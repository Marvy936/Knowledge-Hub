# Policy as Code and Zero Trust glossary entries

## Admission policy

Machine-readable pravidlo vyhodnocované v API admission path-e pred persistence alebo mutation resource-u. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Assume breach

Zero Trust design assumption, že identity, endpoint, workload alebo interná network path môžu byť kompromitované, a preto treba obmedziť trust paths, sessions a blast radius. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Automation and orchestration — Zero Trust

Cross-cutting capability prepájajúca identity, device, network, workload a data signals s riadenými response actions, napríklad revocation alebo quarantine. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Break-glass policy

Oddelený, časovo obmedzený a auditovaný policy path pre emergency access pri zlyhaní alebo nevhodnosti bežného enforcementu. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## CEL policy

Policy vyjadrená pomocou Common Expression Language, napríklad v Kubernetes ValidatingAdmissionPolicy alebo MutatingAdmissionPolicy. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## CISA Zero Trust Maturity Model

Planning model Version 2.0 používajúci päť pillars a tri cross-cutting capabilities na hodnotenie a rozvoj Zero Trust capabilities. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Conftest

Nástroj používajúci OPA/Rego na testovanie structured configuration, napríklad YAML, JSON alebo Terraform planov, pred runtime enforcementom. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Constraint — Gatekeeper

Kubernetes custom resource, ktorý instanciuje Gatekeeper ConstraintTemplate s konkrétnymi parameters, match scope a enforcement behavior. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## ConstraintTemplate — Gatekeeper

Gatekeeper resource definujúci reusable validation logic a parameter schema pre odvodené Constraints. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Continuous diagnostics — Zero Trust

Priebežné získavanie identity, endpoint, workload, network, cloud a application telemetry pre aktualizáciu access contextu a risk decisions. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Continuous verification — Zero Trust

Opakované alebo event-driven prehodnocovanie identity, posture, session a contextu počas bounded access lifecycle-u namiesto permanentnej dôvery po prvom prihlásení. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Control plane — Zero Trust

Vrstva zodpovedná za identity, policy evaluation, posture, access decisions a vytvorenie alebo ukončenie communication pathu. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Data plane — Zero Trust

Vrstva prenášajúca actual application alebo data traffic po tom, čo control plane pripravil a PEP presadil access decision. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Decision log — policy

Audit event zachytávajúci policy query, result, policy revision, decision ID, relevantný context a PDP instance. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Declarative policy

Policy opisujúca požadovaný decision alebo invariant bez imperatívneho control flow-u, typicky nad structured inputom a data. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Default deny — policy

Combining alebo fallback semantics, pri ktorých neznámy, undefined alebo explicitne nepovolený prípad končí odmietnutím. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Degraded access mode — Zero Trust

Explicitný obmedzený access model počas outage-u identity, posture, policy alebo enforcement dependency, napríklad bounded existing sessions alebo low-risk read-only operations. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Device identity

Cryptographically alebo administratívne overená identita endpointu, ktorá sama osebe nedokazuje jeho aktuálny security posture. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Device posture

Aktuálne security attributes zariadenia, napríklad patch level, encryption, EDR health alebo secure boot, používané ako contextual policy inputs. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Differential policy testing

Vyhodnotenie rovnakého corpus-u inputs cez starú a novú policy revision s kontrolou semantic decision rozdielov. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Direct access bypass — Zero Trust

Alternatívna network alebo application cesta, ktorá umožňuje dostať sa ku resource-u bez zamýšľaného identity-aware PEP a policy evaluation. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Egress policy — Zero Trust

Resource alebo workload-specific pravidlá určujúce povolené outbound destinations, protocols a data flows s cieľom obmedziť exfiltration a command-and-control paths. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Executable policy

Machine-readable formalizácia policy intentu s presným input schema, scope, decision a failure semantics. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Failure policy — admission

Pravidlo určujúce, či evaluation error alebo nedostupná admission dependency request zablokuje alebo prepustí. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Gatekeeper

Kubernetes-native policy controller využívajúci OPA Constraint Framework na validation, mutation, audit a viac enforcement points. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Gatekeeper audit

Periodické vyhodnotenie existujúcich Kubernetes resources proti Gatekeeper constraints na detekciu pre-existing alebo drifted violations. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Identity-aware proxy

Proxy acting as PEP, ktorá autentizuje subject, vyhodnotí policy a sprostredkuje access ku konkrétnej application bez implicitnej network trust. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Implicit trust

Access alebo authority udelená bez explicitného resource-specific decisionu iba na základe location, ownership, previous login alebo membership v broad zone. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Infrastructure policy

Policy vyhodnocujúca infrastructure source, plan, configuration alebo runtime state podľa security, compliance, cost a operational guardrails. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Kyverno

Kubernetes-native policy engine poskytujúci policy types pre validation, mutation, generation, cleanup a image verification. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Microsegmentation

Jemnozrnná isolation a traffic policy medzi workloadmi alebo resource groups, ktorá obmedzuje lateral movement bez považovania segmentu za automaticky trusted. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## MutatingAdmissionPolicy

Kubernetes in-process declarative policy resource používajúci CEL na riadené mutation API objects počas admission. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Open Policy Agent — OPA

General-purpose policy engine vyhodnocujúci Rego policies nad structured inputom a supporting data. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Partial evaluation — policy

Predvýpočet policy nad známymi data s vytvorením residual query pre runtime input, používaný na optimalizáciu alebo embedded enforcement. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy Administrator — Zero Trust

NIST Zero Trust logical component, ktorý na základe Policy Engine decisionu vytvára, konfiguruje alebo ukončuje communication path cez PEP. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Policy Administration Point — Policy as Code

Governance a delivery funkcia spravujúca policy authoring, approval, publication, rollout, rollback, exceptions a retirement. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy artifact

Immutable distribuovateľný package policy modules, data, manifestu, revision a integrity metadata. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy as Code

Prístup vyjadrujúci automatizovateľné policy decisions ako versionované, testovateľné a auditovateľné machine-readable rules. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy bundle

Versionovaný package policy a supporting data určený na atomickú distribúciu a activation v policy engine. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy bypass

Access alebo operation vykonaná mimo zamýšľaného enforcement pointu, cez exception, fail-open stav alebo alternatívny path. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy canary

Staged rollout novej policy revision na obmedzenú množinu namespaces, tenants, workloads alebo requests pred širším enforcementom. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy composition

Mechanizmus kombinovania výsledkov viacerých policies podľa explicitných semantics, napríklad deny-overrides alebo all-must-pass. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy conflict

Stav, keď dve alebo viac policies vytvárajú nezlučiteľné decisions, invariants alebo mutations pre rovnaký scope. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy coverage

Miera, do akej sú relevantné resources, actions, environments a enforcement points skutočne chránené konkrétnymi policies; odlišná od test code coverage. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy data

Supporting reference state používaný policy decisionom, napríklad approved registries, identity groups alebo resource classifications. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy Decision Point — Policy as Code

Komponent vyhodnocujúci policy nad inputom a supporting data a vracajúci structured decision. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy distribution skew

Dočasný stav, keď distributed PDP alebo PEP instances používajú rozdielne policy revisions pre asynchronous rollout alebo activation failure. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy Enforcement Point — Policy as Code

Komponent zachytávajúci chránenú operation a presadzujúci policy decision voči callerovi alebo resource-u. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy Engine — Zero Trust

NIST Zero Trust logical component vyhodnocujúci enterprise policy a contextual data pre access ku konkrétnemu resource-u. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Policy exception

Explicitný, scoped, approved a expirovateľný object povoľujúci dokumentovanú odchýlku od konkrétnej policy s compensating controls. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy Information Point — Policy as Code

Zdroj identity, device, asset, vulnerability alebo ďalších contextual attributes poskytovaných policy decisionu. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy input

Request-specific structured document obsahujúci operation, resource a context vyhodnocovaný policy engine-om. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy intent

Ľudsky formulovaný security, compliance alebo operational cieľ, ktorý sa pri Policy as Code formalizuje do executable decision contractu. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy lifecycle

Proces definície intentu, formalizácie, review, testovania, staged rollout-u, monitoring-u, exception managementu a retirementu policy. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy obligation

Dodatočná povinnosť v decision result-e, ktorú PEP musí vykonať spolu s accessom, napríklad masking, step-up alebo audit event. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy Report — Kyverno

Kubernetes custom resource obsahujúci current evaluation results matching resources pre Kyverno policies; nejde o kompletný historical admission log. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy revision

Immutable alebo jednoznačne versionovaná identita konkrétneho policy setu použitá pri decisione, rolloute a audite. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy unit test

Automatizovaný positive, negative alebo boundary scenario overujúci expected policy decision pre konkrétny input a data. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy WebAssembly

Skompilovaná policy vykonávaná ako WebAssembly module v embedded PEP alebo application runtime. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Rego

Deklaratívny OPA policy jazyk inšpirovaný Datalogom a určený na reasoning nad nested structured data. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Resource-centric security

Zero Trust prístup chrániaci konkrétne applications, APIs, data a workflows namiesto udeľovania broad trust celému network segmentu. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Resource enforcement coverage — Zero Trust

Podiel a kvalita access paths ku critical resources, ktoré skutočne prechádzajú identity-aware policy evaluation a neobíditeľným PEP. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Revocation latency — Zero Trust

Čas od identity, posture alebo policy revocation eventu po propagáciu a ukončenie relevantných active sessions vo všetkých enforcement points. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Risk-adaptive access

Access model meniaci allow, deny, step-up, session lifetime alebo povolené actions podľa trusted contextual risk signals. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Secure Access Service Edge — SASE

Architecture category kombinujúca networking a cloud-delivered security services; môže podporovať Zero Trust, ale sama nie je dôkazom resource-level policy. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Security Service Edge — SSE

Cloud-delivered security service model typicky zahŕňajúci ZTNA, secure web gateway a CASB capabilities. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Session binding — Zero Trust

Cryptographic alebo policy väzba session/token contextu na konkrétny device, key, client alebo communication channel s cieľom obmedziť replay ukradnutého credentialu. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Shift-left policy

Policy evaluation vykonaná pred runtime, napríklad v IDE, pull requeste alebo CI, s cieľom poskytnúť skorú spätnú väzbu. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Signed policy bundle

Policy bundle s cryptographic integrity a publisher-authenticity evidence overovanou pred activation v policy engine. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## SPIFFE ID

URI-form identity workloadu v SPIFFE trust domain-e, prenášaná v cryptographically verifiable SVID. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## SPIRE

Production-ready implementation SPIFFE APIs používajúca node a workload attestation na vydávanie a rotation SVIDs. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Step-up authentication

Vyžiadanie silnejšieho alebo čerstvejšieho authentication eventu pri sensitive action, vyššom risku alebo zmene contextu. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Structured policy decision

Policy result obsahujúci okrem allow/deny aj reason, policy IDs, revision, violations alebo obligations v machine-readable forme. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## SVID

SPIFFE Verifiable Identity Document nesúci SPIFFE ID ako X.509 certificate alebo JWT token. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Trust domain — SPIFFE

SPIFFE administrative a security boundary určujúca namespace workload identities a trust bundle pre ich verification. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Undefined policy decision

Stav, keď policy query nevytvorí result; consumer musí explicitne určiť, či znamená deny, error alebo not applicable. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## ValidatingAdmissionPolicy

Stable Kubernetes in-process declarative validation resource používajúci CEL expressions nad admission requestom. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## ValidatingAdmissionPolicyBinding

Kubernetes resource prepájajúci ValidatingAdmissionPolicy s match scope-om, parameters a validation actions. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Visibility and analytics — Zero Trust

Cross-cutting capability korelujúca identity, device, network, workload, resource a decision telemetry na detekciu risku a bypass paths. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Workload attestation

Proces overujúci platform, node, process alebo orchestration attributes workloadu pred vydaním jeho cryptographic identity. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Workload federation — Zero Trust

Explicitné prepájanie workload trust domains alebo identity authorities s riadenou výmenou trust bundles a samostatnou authorization policy. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Workload identity — Zero Trust

Krátkodobá, workload-specific cryptographic identity používaná pre service authentication namiesto IP-based trust alebo shared static credentials. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Zero Trust

Súbor security princípov odstraňujúcich implicitnú dôveru podľa location alebo ownership a vyžadujúcich explicitné resource-specific access decisions. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Zero Trust Architecture — ZTA

Enterprise architecture implementujúca Zero Trust princípy cez identity, policy, enforcement, resource protection, telemetry a lifecycle controls. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Zero Trust governance

Cross-cutting ownership a decision model pre identity, resources, policies, data classification, exceptions, telemetry, privacy a migration roadmap. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Zero Trust migration

Risk-based staged presun od implicitných network trust paths k resource-specific identity-aware enforcementu s meraním bypassov a odstránením legacy paths. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Zero Trust pillar

Capability domain v CISA maturity model-e: Identity, Devices, Networks, Applications and Workloads alebo Data. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Zero Trust Policy Enforcement Point

NIST logical component presadzujúci access decision a sprostredkujúci alebo ukončujúci communication path medzi subjectom a resource-om. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Zero Trust Network Access — ZTNA

Application-specific remote access model používajúci identity, device context a policy namiesto broad network tunnel trustu. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).
