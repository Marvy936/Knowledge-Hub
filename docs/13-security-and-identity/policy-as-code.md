# Policy as Code

Policy as Code vyjadruje opakovateľné rozhodnutia o povolenom stave alebo operácii ako versionované, testovateľné a automaticky vyhodnocované rules. Policy file však nie je control. Control vznikne iba vtedy, keď exact input zachytí správny Policy Enforcement Point, decision engine používa intended policy a data generation, výsledok sa správne presadí a všetky bypass, exception, outage a recovery paths sú overené.

Dominantný model kapitoly je **intent-to-enforcement lifecycle**:

```text
business alebo security intent
→ exact decision subject a input contract
→ executable policy a supporting data
→ immutable policy artifact
→ distribúcia a loaded generation
→ evaluation a structured decision
→ enforcement na authoritative boundary
→ decision audit a runtime evidence
→ exception, rollout, rollback a revocation
→ bypass a second-decision validation
```

Policy syntax je iba jedna vrstva. Hlavná otázka je, či intended decision vznikol a bol presadený na každom relevantnom path-e.

## 1. Policy intent

Intent formuluje owner risku alebo systému zrozumiteľne pre človeka.

```text
Production smie spustiť iba release artifact,
ktorý vytvoril approved builder,
ktorý podpísal approved release workflow
a ktorého exact digest má required provenance a SBOM.
```

Executable contract musí doplniť:

- production scope;
- exact principal, action a resource;
- immutable image subject;
- signer, issuer, workflow a builder identities;
- required evidence predicates;
- input a data schemas;
- missing/unknown behavior;
- enforcement boundary;
- timeout a degraded semantics;
- exception a recovery model.

Slová `approved`, `secure` alebo `critical` bez authoritative data source-u iba automatizujú nejasnosť.

## 2. Exact policy decision subject

Decision subject je viac než policy file:

- request alebo object generation;
- caller identity a delegation;
- requested action a resource;
- environment, tenant a classification;
- policy ID a immutable revision;
- supporting data revision a freshness;
- PDP/evaluator instance;
- PEP a match scope;
- cache generation;
- decision result a obligations;
- enforcement outcome a audit correlation.

Bez tejto identity sa nedá reprodukovať, prečo rovnaký request raz prešiel a inokedy zlyhal.

## 3. Policy, configuration a control

**Policy** určuje allowed, denied alebo required outcome. **Configuration** nastavuje konkrétny component. **Control** je celý mechanism od intentu po enforced a overený outcome.

Príklad:

```text
policy
→ production image musí mať trusted evidence

configuration
→ ValidatingAdmissionPolicy, Gatekeeper alebo Kyverno resource

control
→ protected policy source + distribution + active evaluator
  + complete admission match + fail behavior + decision log
  + background/runtime audit + recovery
```

Policy uložená v Git-e bez active PEP-u je dokumentácia, nie preventive control.

## 4. PAP, PDP, PEP a PIP

**Policy Administration Point — PAP** spravuje intent, authoring, review, publication, rollout, exceptions, rollback a retirement.

**Policy Decision Point — PDP** vyhodnotí exact input proti policy a supporting data generation a vráti structured decision.

**Policy Enforcement Point — PEP** zachytí chránenú operation a result reálne presadí.

**Policy Information Point — PIP** poskytuje identity, posture, asset, vulnerability, signer, quarantine alebo ďalšie contextual data.

```text
PAP publikuje policy artifact
→ PDP načíta policy a PIP generation
→ PEP pošle exact request input
→ PDP vráti decision
→ PEP result presadí
→ audit spojí request, revision a outcome
```

Bezchybná rule nad stale PIP data vytvára chybný decision. Správny PDP bez complete PEP coverage vytvára bypass.

## 5. Input a supporting-data contract

Input je request-specific state. Supporting data sú reusable reference facts.

Production image decision môže používať:

```text
input
→ image index/manifest digest, namespace, caller, operation

supporting data
→ trusted signer identities, builder allowlist,
  quarantine set, namespace classification, exception objects
```

Obe vrstvy potrebujú:

- schema a version;
- source identity a integrity;
- freshness a loaded revision;
- missing, empty a unknown semantics;
- cardinality a size limits;
- compatibility počas producer/consumer rollout-u.

Missing quarantine data nesmie byť ticho interpretované ako „artifact nie je quarantined“.

## 6. Structured decision

Production result nemá byť iba boolean. Užitočný contract obsahuje:

```json
{
  "allow": false,
  "decision_id": "POL-DEC-51-8842",
  "policy_id": "POL-IMG-17",
  "policy_revision": "sha256:polimg17",
  "input_subject": "sha256:pay7240-arm",
  "reason": "signature subject mismatch",
  "violations": ["signed sha256:pay7240-amd"],
  "obligations": [],
  "data_revision": "TRUST-22"
}
```

PEP musí rozumieť obligations ako step-up, mutation, masking alebo audit. Obligation, ktorú PEP ignoruje, nie je enforced policy.

External error message má byť bezpečný; interný decision log môže niesť detailnejší evidence.

## 7. Defaults a combining semantics

Undefined, error a not-applicable nie sú synonymá.

- **default deny** odmietne neexplicitne povolený high-risk request;
- **default allow** môže byť dočasný advisory behavior, nie implicitný production default;
- **deny overrides** zablokuje operation pri jednom mandatory deny;
- **all must pass** vyžaduje úspech všetkých applicable controls;
- **advisory + enforcing** oddeľuje warning od blocking resultu.

Policy composition musí riešiť conflicts. Image mutation na digest a následná signature validation musia pracovať nad tým istým final objectom; ordering nesmie byť skrytý correctness dependency.

## 8. Policy artifact a loaded generation

Production policy má immutable revision: commit, bundle digest alebo signed artifact. Artifact môže obsahovať modules, data, schema, manifest a compatibility metadata.

```text
source revision
→ testovaný policy bundle sha256:polimg17
→ signed publication
→ fleet download
→ validation a atomic activation
→ active-generation telemetry
```

Current source v repository nemusí byť revision, ktorá rozhodla v incidente. Každý PDP/PEP preto reportuje active revision, last successful activation a error state.

OPA bundle môže atomicky distribuovať Rego a data. Signed bundle chráni transfer integrity a publisher identity; nedokazuje correctness intentu ani bezpečnosť publisher accountu.

## 9. Revision skew a cache

Distributed rollout vytvára revision skew. Musí mať bounded duration a observability.

Cache key musí obsahovať všetky decision-relevant dimensions, napríklad:

```text
principal + action + resource/digest + tenant
+ policy revision + data revision + quarantine generation
```

Cache podľa repository/tagu alebo URL môže preniesť allow na iný artifact či usera. Revocation SLA musí byť kratšia než cache lifetime alebo musí existovať event-driven invalidation.

## 10. OPA a Rego

Open Policy Agent oddeľuje policy decision od enforcementu a používa Rego na reasoning nad structured inputom a data.

```text
input document
+ loaded data
+ Rego rules
→ queried virtual document alebo value
```

OPA nie je proxy ani admission boundary sám osebe. Caller musí query result správne interpretovať a presadiť.

Rego policy potrebuje explicitný safe default a tests pre undefined results, missing fields, normalization, negation a type mismatches. JSON schema a strict checks znižujú chyby, ale nenahrádzajú integration test PEP-u.

Partial evaluation a WebAssembly pridávajú compiled-artifact lifecycle. Consumer musí vedieť source revision, compiler/runtime compatibility a update/revocation path.

## 11. Policy testing

Test portfolio má pokryť:

- allowed examples;
- forbidden examples;
- missing a malformed inputs;
- boundary a normalization cases;
- property invariants;
- conflict/combining behavior;
- differential corpus medzi old a new revision;
- integration PEP → PDP → enforcement;
- outage, timeout a stale-data behavior;
- alternate path a bypass tests.

Pre `SEC-PAY-51` sú required fixtures:

```text
valid signature + wrong subject       → deny
approved signer + wrong workflow      → deny
signed amd64 + selected arm64         → deny
quarantined digest + cached allow     → deny
stale policy replica                  → not ready / no traffic
custom release CRD bypass             → deny
known-good exact release              → allow
```

Unit test rule-u nepreukazuje, že admission matchuje všetky resources ani že runtime spustí accepted digest.

## 12. Shift-left, request-time enforcement a background audit

```text
shift-left
→ early developer feedback

request-time enforcement
→ authoritative operation gate

background/runtime audit
→ existing resources, drift a later trust changes
```

Vrstvy sa dopĺňajú. CI policy možno obísť manual deploymentom. Admission policy neprehodnotí automaticky running workload po signer compromise. Background audit nemusí poznať historical caller identity.

## 13. Kubernetes admission model

Kubernetes admission prebieha po authentication a authorization, ale pred persistence objectu.

```text
API request
→ authentication
→ authorization
→ mutation
→ validation
→ persistence
→ controller reconciliation
```

`ValidatingAdmissionPolicy` je in-process CEL validation mechanism; current Kubernetes documentation ho označuje stable. Policy, binding a prípadný parameter resource tvoria oddelený contract. `Deny`, `Warn` a `Audit` actions majú rozdielne enforcement semantics.

`MutatingAdmissionPolicy` je in-process CEL mutation mechanism. Mutation cez apply configuration alebo JSON Patch musí byť idempotentná a následná validation musí overiť final invariant. Pre samotný zákaz unsafe state-u je validation jednoduchšia.

External webhooks pridávajú network, TLS, certificate, latency a availability dependencies. `failurePolicy: Ignore` zachová API availability, ale vytvorí enforcement gap; `Fail` chráni invariant, ale potrebuje recovery path.

## 14. Gatekeeper a Kyverno

Gatekeeper používa Constraint Framework. `ConstraintTemplate` definuje policy code a parameter schema; `Constraint` vytvorí konkrétny scope a enforcement instance. Admission a background audit majú odlišnú evidence boundary.

Kyverno poskytuje Kubernetes-native policy APIs. Current policy model obsahuje CEL-based `ValidatingPolicy`, `ImageValidatingPolicy`, `MutatingPolicy`, `GeneratingPolicy` a `DeletingPolicy`; legacy `ClusterPolicy` model má samostatný deprecation lifecycle. Version a API status treba overovať pri upgrade, nie preberať staré manifests.

`ImageValidatingPolicy` môže extrahovať image references, mutate-nuť tag na digest a overovať signatures/attestations. Tool feature však nenahrádza exact subject, signer a PEP-coverage design.

## 15. Exceptions a break-glass

Exception je scoped, approved a expirovateľný object:

- policy ID a exact subject/resource;
- owner, approver a dôvod;
- start a expiration;
- compensating controls;
- permitted actions;
- audit a review trigger.

`disable_policy=true` pre celý cluster nie je exception. Break-glass je oddelený emergency path pre recovery; musí byť silno chránený, alertovaný, časovo obmedzený a po použití reviewed.

Expiration sa presadzuje technicky. Ticket s dátumom bez removal mechanizmu nevytvára lifecycle.

## 16. Worked incident `SEC-PAY-51`

Policy intent bol správny: production má povoliť iba exact signed release s approved provenance a SBOM.

Real policy subject:

```text
policy ID:       POL-IMG-17
bundle digest:   sha256:polimg17
trust data:      TRUST-22
PEP:             atlas-image-admission
PDP replicas:    6
resource:        AtlasRelease/payments-7-24-0
image index:     sha256:pay7240
runtime arm64:   sha256:pay7240-arm
```

Failure chain:

1. štyri PDP replicas načítali `POL-IMG-17`, dve zostali na `POL-IMG-16` po bundle activation error-e;
2. old revision kontrolovala iba broad OIDC issuer/repository regex;
3. PEP posielal repository a tag, nie final index/platform digest;
4. verification cache bola keyed podľa `repository:tag:namespace`;
5. `AtlasRelease` CRD nebolo v match scope-e; controller neskôr vytvoril Deployment pod exempt ServiceAccountom;
6. webhook používal `failurePolicy: Ignore` počas 23-sekundového timeout windowu;
7. arm64 Pods vznikli bez exact subject verdictu.

Root cause bol **neúplný intent-to-enforcement contract a PEP coverage**. Malicious release bol trigger. Revision skew, tag cache, fail-open timeout a custom-controller path boli amplifiers.

## 17. Discriminating evidence

- decision logs z allow requestov uvádzali rozdielne `policy_revision`;
- dve PDP replicas reportovali activation error a old bundle;
- input neobsahoval `sha256:pay7240-arm`;
- cache hit pre tag vznikol pred quarantine generation;
- Kubernetes audit ukázal create `AtlasRelease`, ale nie image-policy decision pre resulting Deployment;
- controller ServiceAccount bol exempted z webhook match condition;
- počas timeout-u vznikol admission allow bez decision ID.

Tým sa oddelila policy-logic chyba od distribution, PEP, cache a failure-semantics chýb.

## 18. Containment a authoritative recovery

Containment:

- freeze policy publication aj release deployments;
- preserve policy source, approvals, bundles, status, decision logs, audit events a controller logs;
- odstrániť not-ready PDPs z trafficu;
- quarantine affected digests;
- zablokovať custom-controller reconciliation bez mazania evidence.

Recovery:

1. vydať `POL-IMG-18` s exact digest/subject a evidence semantics;
2. publikovať immutable signed bundle;
3. vyžadovať active revision readiness pred trafficom;
4. posielať final mutated object a resolved digests do decisionu;
5. keyovať cache digestom, policy/data revision a quarantine generation;
6. nastaviť production fail-closed s oddeleným known-good break-glass;
7. zahrnúť native workload kinds, image-bearing fields a `AtlasRelease` path;
8. zrušiť broad ServiceAccount exemption;
9. vykonať background scan running a rollback digests;
10. overiť second bundle rollout a stale-replica failure.

Rollback source code-u bez potvrdenia loaded generation nie je recovery.

## 19. Policy acceptance verdict

Control je prijatý až keď:

- intent má ownera a testovateľný contract;
- input a supporting data majú schema, authority a freshness;
- immutable policy artifact je active vo všetkých intended evaluators;
- revision skew je bounded a not-ready instances neprijímajú traffic;
- exact request/resource/digest vstupuje do decisionu;
- structured result sa presadí bez straty obligations;
- cache a exceptions rešpektujú revocation;
- všetky direct, controller, custom-resource a emergency paths prechádzajú equivalentným controlom;
- request-time aj background/runtime evidence sú korelovateľné;
- allowed operation funguje;
- wrong subject, stale revision, timeout, expired exception a bypass paths zlyhajú;
- druhý rollout a rollback obnovia intended state bez hidden fail-open.

## 20. Troubleshooting flow

```text
exact operation a resource
→ PEP match/scope/final object
→ PDP endpoint alebo in-process evaluator
→ loaded policy revision
→ supporting-data revision a freshness
→ input schema a normalization
→ query result/undefined/default
→ combining semantics a obligations
→ cache/exception/quarantine state
→ enforcement action
→ decision/audit correlation
→ alternate paths a runtime outcome
```

Ak local test povoľuje a production deny, porovnaj input, bundle a data generations. Ak PDP povoľuje, ale operation zlyhá, skontroluj PEP mapping alebo ďalší policy layer. Operation bez decision ID signalizuje bypass alebo fallback.

## 21. Earlier controls

- policy intent s explicitným enforcement contractom;
- immutable signed bundles;
- active-generation readiness telemetry;
- schemas pre input, data a structured decisions;
- safe default a explicitné combining semantics;
- differential a property tests;
- integration a alternate-path fixtures;
- digest/policy/quarantine-aware cache;
- scoped expiring exceptions;
- audit → canary → enforcing rollout;
- production fail-closed s isolated break-glass;
- background/runtime re-evaluation;
- second-rollout a rollback rehearsal.

## 22. Anti-patterny

### Policy file equals control

Rule existuje, ale operation neprechádza PEP-om.

### Green unit tests

Policy logic funguje nad fixture, no production posiela iný input alebo nič.

### Mutable branch distribution

Historical decisions nemožno reprodukovať a fleet môže používať rozdielne state.

### Cache bez revision a digestu

Old allow prežije artifact alebo policy change.

### Permanent audit mode

Critical unsafe state sa iba reportuje bez preventive outcome-u alebo risk ownera.

### Global exception alebo fail-open

Jeden recovery case vytvorí broad bypass.

## 23. Kontrolné otázky

1. Čo tvorí exact policy decision subject?
2. Prečo policy file nie je control?
3. Ako sa PAP, PDP, PEP a PIP líšia?
4. Čo má obsahovať input, data a structured-decision contract?
5. Ako sa undefined, false, error a not-applicable líšia?
6. Prečo policy artifact potrebuje active-generation telemetry?
7. Ako revision skew a cache predlžujú exposure?
8. Čo Rego/OPA rieši a čo musí vykonať caller?
9. Ako sa shift-left, request-time a background audit dopĺňajú?
10. Kedy zvoliť in-process CEL a kedy webhook/controller?
11. Ako custom CRD alebo controller vytvorí enforcement bypass?
12. Čo musí overiť policy acceptance verdict?

## Glossary impact

Relevantné pojmy: policy decision subject, intent-to-enforcement lifecycle, input/data generation pair, active policy generation, structured enforcement contract, policy realization chain, revision-skew boundary, PEP coverage verdict, quarantine-aware decision cache, policy revocation closure, policy acceptance verdict a second-decision validation.

## Primárne zdroje

- [Open Policy Agent documentation](https://www.openpolicyagent.org/docs)
- [OPA Policy Language — Rego](https://www.openpolicyagent.org/docs/policy-language)
- [OPA Bundles](https://www.openpolicyagent.org/docs/management-bundles)
- [OPA Decision Logs](https://www.openpolicyagent.org/docs/management-decision-logs)
- [Gatekeeper documentation](https://open-policy-agent.github.io/gatekeeper/website/docs/)
- [Kubernetes Validating Admission Policy](https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/)
- [Kubernetes Mutating Admission Policy](https://kubernetes.io/docs/reference/access-authn-authz/mutating-admission-policy/)
- [Kubernetes admission webhook good practices](https://kubernetes.io/docs/concepts/cluster-administration/admission-webhooks-good-practices/)
- [Kyverno policy types](https://kyverno.io/docs/policy-types/overview/)
- [Kyverno ImageValidatingPolicy](https://kyverno.io/docs/policy-types/image-validating-policy/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Image signing](image-signing.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Zero Trust →](zero-trust.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
