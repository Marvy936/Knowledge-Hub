# Threat modeling

Threat modeling je systematický engineering proces, ktorým tím odvodzuje security a privacy requirements z konkrétneho systému ešte pred incidentom. Jeho výstupom nie je iba diagram ani zoznam kategórií. Hodnota vzniká v reťazi od chráneného outcome-u cez exact architecture generation a realistický attack path až po control, negative test, operational evidence a residual-risk decision.

```text
business alebo security objective
→ exact threat-model subject a scope
→ assets, actors, data a state transitions
→ trust, identity a administrative boundaries
→ assumptions a dependency failure modes
→ concrete threat statement a attack path
→ risk treatment a control mechanism
→ testovateľný security requirement
→ negative test a operational evidence
→ residual risk, owner a update trigger
```

## 1. Threat-model subject

Model musí byť viazaný na verziu systému, ktorú opisuje. Minimálny subject obsahuje:

- service alebo critical flow;
- source a architecture revision;
- environment a tenant model;
- entry a exit points;
- identity, authorization a recovery flows;
- build, deployment a supplier paths;
- data classes a retention;
- ownera, review date a otvorené risks.

Diagram bez revision identity sa môže stať false assurance po zmene runnera, proxy, issuer-a alebo deployment controlleru.

## 2. Security objectives

Objective definuje, čo nesmie byť porušené a čo musí zostať dostupné alebo auditovateľné.

Slabý objective:

```text
Build pipeline musí byť bezpečný.
```

Silnejší objective:

> Production image musí vzniknúť z approved source revision na schválenom izolovanom builderi. Untrusted contribution ani build step nesmú meniť output po testoch, používať production signing authority alebo vytvoriť artifact, ktorý admission prijme bez digest-bound provenance a final-artifact SBOM.

Objective sa musí dať preložiť do requirementu a allowed aj forbidden testu.

## 3. Scope a critical journeys

Scope môže byť celý system context alebo jeden high-impact lifecycle. Praktické models často používajú hierarchiu:

1. system context — users, external systems a hlavné boundaries;
2. service model — processes, stores a identity flows;
3. critical-flow model — detailný payment, login, recovery alebo release lifecycle;
4. implementation model — konkrétne fields, tokens, commands a state transitions.

Príliš široký scope vytvorí diagram `internet → cloud → database`. Príliš úzky model môže ignorovať CI/CD, backup alebo support path, cez ktorý sa rovnaký asset mení.

## 4. Assets nie sú iba data

Asset je každá capability alebo evidence s významným confidentiality, integrity, availability, authenticity alebo accountability impactom.

Pre release flow sú assets napríklad:

- source revision a review history;
- build definition a reusable workflows;
- builder image a runner isolation;
- dependency a cache graph;
- registry namespace a publish authority;
- signing identity a provenance issuer;
- artifact digest, SBOM a promotion record;
- admission policy a runtime inventory;
- audit logs potrebné na incident reconstruction.

CI signing identity môže mať väčší systemic impact než jeden application server, pretože dokáže vytvoriť trusted artifacts pre viac environments.

## 5. Actors, principals a attacker capabilities

Actor je človek, workload, organization alebo external system. Principal je identity, pod ktorou konkrétny system actor-a rozpoznáva.

Label `attacker` nestačí. Uveď starting position a capabilities:

- anonymous internet actor;
- authenticated tenant;
- external contributor kontrolujúci PR branch a metadata;
- compromised maintainer account;
- malicious dependency publisher;
- build step s workspace a network accessom;
- source-control, CI alebo registry administrator;
- compromised production workload.

Legitímny actor môže zneužiť allowed feature. Crafted pull-request title alebo package name môže byť syntakticky validný input, ktorý scanner nepovažuje za attack.

## 6. Data, commands a state transitions

Každý významný flow má uvádzať:

- data alebo command type;
- origin a authoritative ownera;
- protocol a serialization;
- identity alebo delegation context;
- integrity a ordering requirements;
- classification a tenant scope;
- failure, retry a replay semantics;
- logging a redaction;
- lifecycle transition, ktorý vyvoláva.

Mnohé threats vznikajú pri transition:

```text
source revision
→ approved release candidate
→ builder input
→ immutable artifact
→ signed/promoted digest
→ admitted workload
→ running production generation
```

Pri každom transition urč actor-a, preconditions, idempotency, evidence a forbidden alternate path.

## 7. Trust boundaries

Trust boundary je miesto, kde sa mení identity authority, privilege, administrative owner, tenant, execution isolation, data classification alebo cryptographic protection.

Nie je to iba firewall. Pre release flow sú relevantné:

- contributor-controlled metadata → trusted workflow interpreter;
- repository → CI control plane;
- tenant build step → runner host;
- untrusted build process → provenance/signing service;
- builder → registry;
- registry metadata → deployment policy;
- admission decision → runtime controller;
- staging → production trust root.

Na každej boundary sa pýtaj:

```text
kto vydal identity?
čo je attacker-controlled?
čo consumer validuje?
aké privilege sa mení?
kto môže boundary obísť?
čo sa stane pri outage alebo stale state-e?
```

## 8. Assumptions a dependencies

Assumption je tvrdenie, na ktorom design stojí, ale nemusí ho system priamo presadzovať. Dependency je external component alebo process, ktorého behavior system potrebuje.

Príklady critical assumptions:

- runner je ephemeral a po každom jobe zničený;
- release job nespúšťa untrusted metadata ako command source;
- provenance signing material je mimo tenant build processu;
- SBOM analyzuje final artifact, nie iba source lockfile;
- admission je jediný production deployment path;
- registry promotion zachová signatures a attestations.

Každá assumption potrebuje ownera, evidence a failure consequence. Architecture dokument, ktorý označí persistent runner ako ephemeral, je neplatný model, nie iba nepresný label.

## 9. Data Flow Diagram

DFD je reasoning model external entities, processes, stores, flows a boundaries.

```text
[Contributor]
    │ PR code + title + metadata
    ▼
[Source control]
    │ approved revision + release metadata
    ▼
[CI control plane]
    │ job definition + short-lived identity
    ▼
[Ephemeral builder] ── artifact digest ──> [Registry]
    │                     │
    ├─ provenance         ├─ SBOM/referrers
    └─ build audit        └─ signature
                              │
                              ▼
                       [Admission policy]
                              │
                              ▼
                       [Kubernetes runtime]
```

Arrow `CI builds image` je nedostatočný. Model musí ukázať, kde vstupujú PR metadata, kto vlastní runner image, kto podpisuje provenance a na ktorý digest sú claims viazané.

## 10. Threat statements

Concrete threat statement spája actor-a, condition, action, asset a impact:

```text
actor
→ zneužije konkrétnu boundary alebo condition
→ vykoná action
→ zasiahne asset
→ spôsobí security impact
```

Príklad:

> Contributor vloží crafted release-note metadata do schváleného PR. Vulnerable helper na persistentnom privileged runneri interpretuje metadata ako shell command, zmení final image po testoch a release workflow publikuje a podpíše nedôveryhodný digest. Production admission kontroluje iba existenciu attestations, takže artifact nasadí.

`Supply-chain attack` alebo `tampering` je iba category. Neurčuje missing control ani test.

## 11. STRIDE ako elicitation, nie výsledok

STRIDE pomáha klásť systematické otázky:

- **Spoofing** — možno predstierať source, builder, signer alebo workload identity?
- **Tampering** — možno zmeniť code, artifact, provenance, SBOM alebo policy?
- **Repudiation** — chýba attribution medzi contributorom, workflowom a runnerom?
- **Information Disclosure** — môže build získať secrets, source alebo tenant data?
- **Denial of Service** — môže malý input vyvolať drahý build, queue alebo policy failure?
- **Elevation of Privilege** — môže untrusted change získať release alebo production authority?

Threats sa potom formulujú nad exact flowom a boundary. Copy celej STRIDE alebo ATT&CK matice nevytvára actionable model.

## 12. Attack tree pre production artifact compromise

```text
Goal: spustiť attacker-controlled code ako trusted production image
├─ zmeniť approved source
├─ kompromitovať dependency resolution
├─ kompromitovať builder alebo runner
│  ├─ vulnerable build helper
│  ├─ persistent state z predchádzajúceho jobu
│  └─ poisoned shared cache
├─ ukradnúť publish alebo signing authority
├─ nahradiť digest pri distribúcii
└─ obísť deployment policy
   ├─ existence-only attestation gate
   ├─ mutable tag
   └─ alternate direct deployment path
```

OR branches sú alternate paths. AND branch môže vyžadovať napríklad `vulnerable helper + attacker-controlled metadata + privileged persistent runner`.

Tree ukazuje weakest path a spoločné controls. Nie je automatický probability model.

## 13. Controls ako mechanisms

Mitigation musí uviesť enforcement point, input a threat step, ktorý blokuje.

Slabé:

```text
Použiť provenance a SBOM.
```

Silnejšie:

> Build platform mimo tenant jobu vydá signed provenance pre exact digest. Production policy overí approved builder identity, expected repository/revision, build type a parameters. SBOM sa generuje z final filesystemu a policy kontroluje subject digest, lifecycle stage a completeness. Existence súboru alebo validná signature bez claim evaluation nestačí.

Defense in depth má význam, keď controls zlyhávajú nezávisle. Provenance a SBOM generované rovnakým compromised tenant processom nemusia byť dve nezávislé vrstvy.

## 14. Requirement a negative test

Threat sa prekladá do testovateľného contractu.

### Requirement R1 — untrusted metadata

> Release workflow musí prenášať PR title a release notes cez data channel, nie ich interpolovať do shell source-u. Control characters a command substitutions nesmú zmeniť executed command graph.

Negative test: crafted title vytvorí iba literal release note; nevytvorí process, file ani network side effect.

### Requirement R2 — builder isolation

> Protected release musí bežať na fresh ephemeral builderi z pinned digestu. Predchádzajúci job nesmie ovplyvniť filesystem, process, credentials ani cache authority nasledujúceho release-u.

Negative test: adversarial pre-job persistence fixture nie je v release jobe viditeľná.

### Requirement R3 — evidence authority

> Provenance musí vydať approved platform identity mimo user-defined steps a musí byť viazaná na final artifact digest. SBOM musí reprezentovať final artifact a explicitnú completeness generation.

Negative test: self-generated provenance alebo source-only SBOM pre final image policy odmietne.

### Requirement R4 — deployment

> Production workload môže používať iba digest, ktorého signer, builder, source revision, provenance a SBOM spĺňajú current policy. Mutable tag alebo missing referrers zlyhajú.

Negative test: correctly signed artifact z unapproved buildera alebo s wrong subject digestom je denied.

Expected result zahŕňa deny, audit evidence a absenciu partial side effects.

## 15. Worked incident `SEC-PAY-50`

Pôvodný Atlas release threat model bol označený revision `TM-REL-12`. Obsahoval source repository, CI, registry a Kubernetes. Explicitne však predpokladal:

```text
runner = ephemeral
provenance = platform-generated
SBOM = final artifact inventory
```

Skutočný release `7.24.0` použil persistentný `runner-prod-17`, vulnerable `atlas-build-helper 2.4.1`, job-generated provenance a source-only SBOM. Crafted PR title vyvolal command injection a final image `sha256:pay7240` obsahoval injected JAR.

### Prečo model zlyhal

- runner lifecycle nebol viazaný na inventory evidence;
- build helper a runner image neboli v DFD ani dependency inventory;
- PR metadata neboli modelované ako attacker-controlled input;
- signing/provenance authority bola nakreslená mimo jobu, hoci credential bol dostupný jobu;
- SBOM stage nebola pomenovaná;
- deployment control overoval existence evidence, nie semantics;
- alternate rollback a direct controller paths neboli negatívne testované.

Incident nebol „nepredvídateľný“. Relevantné boundary a assumptions v modeli chýbali alebo boli nepravdivé.

## 16. Evidence-preserving model update

Po incidente sa najprv zachová pôvodný `TM-REL-12`, aby zostalo viditeľné, ktoré assumptions zlyhali. Nová generation `TM-REL-13` pridá:

- contributor metadata flow;
- builder image a toolchain inventory;
- runner persistence a cache boundaries;
- provenance issuer a signing-key boundary;
- final-artifact SBOM generation;
- registry referrers a promotion;
- admission claim evaluation;
- runtime a rollback digest inventory;
- incident revocation flow.

Model sa nemá prepísať tak, aby spätne predstieral, že risk bol vždy známy.

## 17. Residual risk

Po controls zostáva napríklad:

- malicious source schválený dvoma compromised reviewers;
- compromise CI control plane-u alebo approved builder image supply chain;
- zero-day v build toolchain-e bez dostupnej detection;
- malicious dependency, ktorá je immutable a správne zaznamenaná;
- insider s oprávneným emergency bypassom.

Residual risk potrebuje business ownera, monitoring, review trigger a recovery plan. `Low` bez popisu zostávajúceho attack pathu nie je decision.

## 18. Operational evidence

Critical threats určujú, akú evidence musí systém produkovať:

- source revision, approvals a branch-policy generation;
- runner ID, image digest a ephemeral lifecycle;
- resolved dependency, action a cache identities;
- process graph a network egress release jobu;
- provenance issuer, subject, builder a parameters;
- SBOM subject, method, completeness a semantic diff;
- registry publish/promotion audit;
- admission decision s policy revision;
- running a rollback digest inventory;
- signer/builder revocation propagation latency.

Preventive control bez incident evidence môže zlyhávať potichu.

## 19. Fail-open a degraded behavior

Security dependency outage musí mať explicitné semantics. Ak provenance verifier alebo registry referrers nie sú dostupné, production release nemá implicitne pokračovať.

Možné bounded modes:

- nové production deployments fail-closed;
- existing verified workloads pokračujú;
- emergency known-good digest potrebuje oddelený break-glass approval a audit;
- low-risk non-production environment môže použiť časovo obmedzený advisory mode;
- po obnovení sa všetky deferred decisions re-evaluujú.

Degraded mode nie je general bypass.

## 20. Privacy modeling

Rovnaký system model možno použiť pre privacy objectives. LINDDUN pomáha analyzovať linking, identifying, non-repudiation, detecting, disclosure, unawareness a non-compliance.

Build a SBOM evidence môže odhaliť contributor identities, internal package names alebo architecture. Threat model preto zahŕňa minimization, access, retention a incident sharing, nielen integrity artifacts.

## 21. Update triggers a model-as-code

Model aktualizuj pri:

- novej trust alebo administrative boundary;
- zmene runnera, buildera, cache alebo CI platformy;
- novom supplierovi, dependency registry alebo build action;
- zmene signing, provenance, SBOM alebo admission flowu;
- novom deployment alebo rollback path-e;
- incident, pen-test alebo control exception;
- zmene attacker capabilities alebo threat intelligence.

Versionovaný model-as-code môže kontrolovať missing owners, stale reviews a requirements bez negative tests. Automation však nenahrádza business a architecture reasoning.

## 22. Acceptance verdict

Threat-model block je uzavretý, keď:

- model generation zodpovedá current architecture a inventory;
- critical assumptions majú runtime evidence;
- contributor metadata, builder, signing, registry a admission boundaries sú explicitné;
- každý high-impact threat má concrete statement a attack path;
- mitigations uvádzajú enforcement mechanism;
- requirements majú allowed aj forbidden tests;
- negative testy pre command injection, runner persistence, wrong builder, wrong subject a alternate deployment prejdú;
- operational evidence umožní actor-to-runtime reconstruction;
- residual risks majú ownera a review trigger;
- druhý independent review nenájde hidden privileged path v modelovanom scope-e.

## 23. Earlier controls

- PR template triggerujúci review pri zmene trust boundary alebo privileged flowu;
- architecture inventory pre runner, builder a evidence authorities;
- assumptions registry s owners a canaries;
- abuse-case fixtures pre untrusted metadata;
- attack tree pre source, build, distribution a deployment compromise;
- requirements-as-code pre provenance/SBOM/admission claims;
- mandatory negative-test evidence pri high-risk release changes;
- incident feedback, ktorý zachová old model a vytvorí new generation;
- periodic adversarial workshop s engineering, operations a security.

## 24. Anti-patterny

### Diagram bez threat statements

Je to architecture documentation, nie threat model.

### STRIDE checklist bez flow contextu

Categories sa odškrtnú, ale nevznikne missing control ani test.

### Assumption bez evidence

`Runner je ephemeral` môže byť nepravdivé práve počas incidentu.

### Mitigation ako slogan

`Použiť signing` neurčuje signer authority, subject ani verification policy.

### Existence evidence ako control

Attestation môže byť validná, ale opisovať unsafe alebo compromised process.

### Accepted risk bez ownera

Unresolved threat sa iba premenoval.

## 25. Kontrolné otázky

1. Čo tvorí exact threat-model subject?
2. Ako objective preložíš do forbidden outcome-u?
3. Prečo build identity a signing authority sú assets?
4. Ako modelovať attacker-controlled metadata?
5. Čo je trust boundary mimo network firewallu?
6. Ako sa assumption líši od dependency?
7. Prečo STRIDE nie je hotový threat model?
8. Ako attack tree odhalí weakest supply-chain path?
9. Čo musí obsahovať concrete threat statement?
10. Ako mitigation preložiť do requirementu a negative testu?
11. Prečo provenance a SBOM nemusia byť nezávislé controls?
12. Čo musí overiť threat-model acceptance verdict?

## Glossary impact

Relevantné pojmy: threat-model subject, objective-to-negative-test lifecycle, architecture generation, critical assumption evidence, administrative trust boundary, untrusted metadata flow, threat statement, attack-path generation, mitigation mechanism, security requirement, negative security test, evidence authority, model acceptance verdict a threat-model recurrence trigger.

## Primárne zdroje

- [OWASP Threat Modeling Project](https://owasp.org/www-project-threat-modeling/)
- [OWASP Threat Modeling Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html)
- [Microsoft Introduction to Threat Modeling](https://learn.microsoft.com/en-us/training/modules/tm-introduction-to-threat-modeling/)
- [MITRE CAPEC](https://capec.mitre.org/)
- [MITRE ATT&CK](https://attack.mitre.org/)
- [LINDDUN Privacy Engineering](https://linddun.org/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Vulnerability a patch management](vulnerability-and-patch-management.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Supply-chain security →](supply-chain-security.md)
<!-- KNOWLEDGE-NAVIGATION:END -->