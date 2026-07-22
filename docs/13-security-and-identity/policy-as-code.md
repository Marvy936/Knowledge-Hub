# Policy as Code

Policy as Code je prístup, pri ktorom sú policy decisions vyjadrené ako versionované, testovateľné a automaticky vyhodnocované pravidlá. Cieľom nie je premeniť každý organizačný dokument na source code. Cieľom je presne formalizovať tie rozhodnutia, ktoré musí systém konzistentne vykonať pri build, deployment, admission, authorization, configuration alebo runtime operácii.

Policy as Code oddeľuje:

```text
policy intent
→ machine-readable policy
→ trusted input a data
→ policy decision
→ enforcement point
→ audit evidence
→ exception a lifecycle management
```

Samotná existencia policy súboru nevytvára kontrolu. Kontrola vzniká až vtedy, keď správny enforcement point používa správnu verziu policy, dôveryhodné inputs a explicitný failure model.

## 1. Mentálny model

```text
policy administrator vytvorí alebo schváli policy
→ policy distribution sprístupní konkrétnu revision
→ policy decision point vyhodnotí input a data
→ vráti structured decision
→ policy enforcement point rozhodnutie vykoná
→ decision log zachová evidence
```

Každý krok je samostatná trust boundary.

## 2. Čo je policy

Policy je explicitné pravidlo alebo množina pravidiel určujúcich povolený, zakázaný, požadovaný alebo odporúčaný stav či operáciu.

Príklady:

- kto môže čítať konkrétny resource,
- ktoré container images možno nasadiť,
- či Terraform plan spĺňa cloud guardrails,
- či Kubernetes workload používa approved registry,
- či release obsahuje potrebnú provenance,
- či configuration prekračuje cost alebo risk limit.

Policy nemá byť nejasná veta bez ownera, scope-u a decision semantics.

## 3. Policy intent a executable policy

Policy intent je ľudský cieľ:

```text
Production workloads musia používať podpísané images.
```

Executable policy potrebuje presnejší contract:

- čo je production workload,
- ktorý digest je subject,
- ktoré signing identities sú trusted,
- aké attestations sú required,
- kedy sa decision vykonáva,
- čo sa stane pri nedostupnej verification dependency,
- ako fungujú exceptions.

Preklad intentu do code-u je design a governance úloha, nie iba syntax.

## 4. Policy lifecycle

```text
definícia intentu
→ threat/risk analýza
→ formalizácia
→ review
→ test
→ audit-only rollout
→ enforce rollout
→ monitoring
→ exception management
→ zmena alebo retirement
```

Policy bez lifecycle-u sa časom stane stale, nepresnou alebo nebezpečnou.

## 5. Policy Administration Point

Policy Administration Point — PAP spravuje:

- authoring,
- versioning,
- approval,
- publication,
- rollout,
- rollback,
- ownership,
- exceptions,
- retirement.

PAP nemusí byť jeden produkt. Môže ho tvoriť Git repository, CI pipeline, artifact registry a change-management workflow.

## 6. Policy Decision Point

Policy Decision Point — PDP vyhodnocuje policy nad inputom a supporting data.

```text
input
+ policy revision
+ contextual data
→ decision
```

PDP má vrátiť structured result, napríklad:

```json
{
  "allow": false,
  "reason": "image registry is not approved",
  "policy_id": "K8S-IMAGE-004",
  "policy_revision": "sha256:..."
}
```

Boolean bez reason, identity a revision metadata je slabý operational contract.

## 7. Policy Enforcement Point

Policy Enforcement Point — PEP zachytí operáciu a presadí decision.

Príklady:

- API gateway,
- Kubernetes admission,
- CI quality gate,
- Terraform plan gate,
- service authorization middleware,
- package registry,
- deployment controller,
- database proxy.

PEP musí byť neobíditeľný pre chránenú operation alebo musí existovať detekcia bypassu.

## 8. Policy Information Point

Policy Information Point — PIP poskytuje attributes a contextual data pre decision.

Príklady:

- identity groups,
- device posture,
- asset classification,
- vulnerability status,
- environment metadata,
- approved registries,
- business ownership,
- time a location,
- image signatures a provenance.

Nesprávne alebo stale PIP data môžu vytvoriť nesprávne decision aj pri správnej policy.

## 9. Input oproti data

V policy engine modeloch sa často oddeľuje:

```text
input → konkrétny request alebo object

data  → supporting policy data a reference state
```

Príklad:

- input: Kubernetes Deployment admission request,
- data: zoznam approved registries a environment classification.

Obe vrstvy potrebujú schema, source, freshness a integrity contract.

## 10. Declarative policy

Declarative policy opisuje požadovaný decision alebo stav bez imperatívneho control flow-u.

Výhody:

- jednoduchšie reasoning,
- composability,
- auditovateľnosť,
- možnosť partial evaluation,
- stabilnejšie testovanie.

Declarative syntax sama nezaručuje zrozumiteľnosť. Komplexné negácie a implicitné defaults môžu byť rovnako nebezpečné ako procedural code.

## 11. Default deny a default allow

Policy domain musí mať explicitný default.

```text
default deny → neznáme prípady sú odmietnuté

default allow → neznáme prípady pokračujú
```

Default deny je vhodný pre authorization a high-risk admission, ale môže spôsobiť outage pri neúplnom scope-e alebo missing data.

Default allow môže byť vhodný počas audit rollout-u, ale nesmie sa zameniť za finálny enforcement.

## 12. Allowlist a denylist

Allowlist model definuje známe povolené prípady. Denylist blokuje známe zakázané prípady.

Allowlist býva silnejší pri:

- production deploymentoch,
- privileged actions,
- approved registries,
- cryptographic identities.

Denylist je užitočný pre emergency blocking, ale nedokáže enumerovať všetky budúce zlé stavy.

## 13. Policy composition

Viac policies môže rozhodovať o rovnakej operácii.

Potrebný je explicitný combining model:

- deny overrides,
- allow overrides,
- all must pass,
- first applicable,
- priority-based,
- separate advisory a enforcing results.

Bez combining semantics môže poradie evaluation neúmyselne meniť security outcome.

## 14. Policy conflict

Conflict nastáva, keď policies dávajú nezlučiteľné výsledky alebo požiadavky.

Príklady:

- jedna policy vyžaduje immutable tag, druhá povoľuje mutable alias,
- security policy blokuje privilege, platform policy ho generuje,
- region policy vyžaduje dva rozdielne regions.

Conflict detection má byť súčasť testovania a rollout-u, nie incident po deployment-e.

## 15. Policy identity a revision

Každá decision-relevant policy potrebuje:

- stabilné policy ID,
- version alebo immutable digest,
- ownera,
- scope,
- effective date,
- severity,
- change history,
- retirement state.

Decision log bez policy revision nevie spoľahlivo vysvetliť historical outcome.

## 16. Policy repository

Policy repository má používať rovnaké engineering controls ako application code:

- protected branches,
- CODEOWNERS,
- review,
- CI,
- signed commits alebo artifacts podľa risku,
- release tags/digests,
- rollback,
- audit trail.

Policy repository je high-impact source, pretože malicious policy môže povoliť alebo zablokovať široké množstvo operácií.

## 17. Separation of duties

Oddeľ:

- policy authora,
- policy approvera,
- platform operatora,
- exception approvera,
- enforcement administratora.

Jedna compromised identity nemá mať možnosť súčasne zmeniť policy, publikovať ju, vypnúť enforcement a zmazať decision logs.

## 18. Policy artifact

Production policy má byť distribuovaná ako immutable artifact alebo bundle.

Artifact má obsahovať:

- policy modules,
- data,
- manifest,
- revision,
- compatibility metadata,
- signature alebo integrity evidence,
- test evidence podľa procesu.

Deployment priamo z mutable branch pathu sťažuje audit a rollback.

## 19. Policy bundles

OPA bundles umožňujú distribuovať policy a data bez restartu engine-u.

Dôležité vlastnosti:

- snapshot alebo scoped roots,
- revision metadata,
- eventual consistency,
- atomic activation,
- status reporting,
- voliteľná persistence,
- signature verification.

Ak bundle activation zlyhá, engine má zachovať poslednú známu validnú policy a reportovať failure.

## 20. Signed policy bundles

Signed bundle chráni integrity a publisher authenticity.

Nezaručuje:

- správnosť policy intentu,
- quality review,
- bezpečnosť signing identity,
- kompatibilitu s runtime,
- správnosť supporting data.

Verifier musí používať out-of-band trusted key alebo trust root a explicitnú scope policy.

## 21. Policy distribution consistency

Distributed PDP instances nemusia aktivovať novú revision v rovnakom okamihu.

Definuj:

- rollout window,
- acceptable skew,
- minimum required revision,
- rollback semantics,
- health signal,
- behavior pri partial activation.

Security-critical revocation policy môže potrebovať rýchlejší path než bežný bundle polling.

## 22. Open Policy Agent

Open Policy Agent — OPA je general-purpose policy engine pre structured data.

```text
application alebo platform
→ pošle JSON input
→ OPA vyhodnotí Rego a data
→ vráti decision
```

OPA oddeľuje policy decision od application implementation, ale application stále musí správne vytvoriť input a presadiť výsledok.

## 23. Rego

Rego je deklaratívny policy jazyk inšpirovaný Datalogom a určený na reasoning nad nested structured documents.

Silné stránky:

- sets a comprehensions,
- reusable rules,
- structured outputs,
- policy/data separation,
- test framework,
- partial evaluation.

Riziká:

- implicit undefined result,
- nejasné negácie,
- broad object iteration,
- schema assumptions,
- performance pri veľkých datasets.

## 24. Undefined result

Rego query môže byť undefined, ak žiadne pravidlo nevytvorí result.

Consumer musí vedieť, či undefined znamená:

- deny,
- allow,
- error,
- not applicable.

Implicitné mapovanie undefined na allow je častý authorization failure.

## 25. Structured decisions

Preferuj structured decision:

```json
{
  "allowed": false,
  "violations": [
    {
      "id": "NET-002",
      "message": "public ingress is not allowed",
      "severity": "high"
    }
  ]
}
```

Structured output podporuje UX, audit, reporting a selective enforcement.

Policy engine však nesmie vracať citlivé interné data attackerovi cez error message.

## 26. Schema a type assumptions

Policy má validovať alebo deklarovať očakávaný input schema.

Problémy:

- missing field,
- field s iným typom,
- API version drift,
- null oproti empty collection,
- unknown enum,
- integer/string coercion.

Policy, ktorá pri schema zmene silently prestane matchovať, môže fail-open.

## 27. Policy data freshness

Reference data môže mať vlastný update cadence:

- identity groups — minúty,
- revoked digest — sekundy,
- asset classification — hodiny,
- compliance mapping — dni.

Definuj maximum staleness a behavior pri prekročení. Cache bez freshness contractu je implicitný trust.

## 28. External data

Policy môže potrebovať external lookup.

Trade-offy:

- aktuálnosť,
- latency,
- availability,
- determinism,
- privacy,
- replay/debugging.

Synchronous remote call v admission path-e vytvára availability dependency. Preferuj precomputed alebo cached data, ak use case nevyžaduje real-time lookup.

## 29. Partial evaluation a compilation

Partial evaluation predpočíta časti policy nad známymi data a ponechá residual query pre runtime input.

Použitie:

- výkon,
- query translation,
- edge enforcement,
- policy embedding.

Optimalizovaný output musí byť verziovaný a testovaný proti source policy, aby compilation nezmenila semantics.

## 30. WebAssembly policy

OPA policies možno podľa use case-u skompilovať do WebAssembly a vykonávať embedded v application alebo proxy.

Výhody:

- nízka latency,
- lokálna availability,
- bez network hopu.

Riziká:

- distribution consistency,
- host integration bugs,
- limited built-ins,
- stale policy,
- odlišná observability od central PDP.

## 31. Unit tests

Každá policy potrebuje positive aj negative cases.

Testuj:

- allowed expected case,
- denied expected case,
- missing fields,
- unknown values,
- boundary values,
- exception path,
- multiple matching policies,
- malformed input.

Test iba happy pathu často zachytí syntax, nie security semantics.

## 32. Table-driven tests

Table-driven tests umožňujú vyjadriť decision matrix:

```text
identity | resource | action | context | expected
```

Sú vhodné pre:

- RBAC/ABAC kombinácie,
- environment rules,
- namespace exceptions,
- cost thresholds,
- version compatibility.

Matrix má obsahovať explicitné deny cases pre každý privilege boundary.

## 33. Property a invariant testing

Niektoré policies možno testovať ako invariants:

- žiadny anonymous principal nesmie write-nuť production resource,
- žiadny workload bez ownera nesmie byť admitted,
- exception nesmie platiť po expiry,
- lower environment policy nesmie udeliť production authority.

Property testing pomáha odhaliť kombinácie, ktoré ručne písané examples nepokrývajú.

## 34. Policy coverage

Coverage ukazuje, ktoré rules a branches testy vykonali.

Nevyjadruje:

- správnosť intentu,
- completeness policy,
- kvalitu assertions,
- correctness input mappingu.

Coverage je diagnostic metric, nie security proof.

## 35. Static analysis a linting

Linting môže odhaliť:

- deprecated syntax,
- unused rules,
- risky patterns,
- duplicate logic,
- style drift,
- unreachable code.

Static analysis má byť gate pred publication, ale nemôže nahradiť scenario tests.

## 36. Golden tests a decision snapshots

Golden test porovná structured decision s approved outputom.

Pomáha zachytiť broad semantic zmenu, ale aktualizácia golden súboru bez review môže iba schváliť regression.

Pri veľkých zmenách zobraz decision diff podľa policy ID, resource a severity.

## 37. Differential testing

Pri migrácii engine-u alebo policy revision vyhodnoť rovnaký input cez old a new version.

```text
historical inputs
→ old decision
→ new decision
→ semantic diff
```

Rozdiel musí byť vysvetlený a schválený, najmä pri allow expansion.

## 38. Shift-left evaluation

Policy možno vyhodnocovať pred runtime:

- pre-commit,
- IDE,
- pull request,
- CI,
- Terraform plan,
- rendered Kubernetes manifests.

Shift-left znižuje feedback latency, ale runtime enforcement zostáva potrebný, pretože actual input a environment sa môžu líšiť.

## 39. Conftest a configuration testing

Conftest používa OPA/Rego na testovanie structured configuration, napríklad YAML, JSON, Terraform plan alebo Dockerfile-derived data.

Dôležité je testovať final rendered alebo planned representation, nie iba source template, ak transformácie môžu zmeniť výsledok.

## 40. Infrastructure as Code policy

IaC policy môže kontrolovať:

- public exposure,
- encryption,
- logging,
- region,
- tags/ownership,
- instance size,
- IAM permissions,
- destructive changes,
- cost guardrails.

Plan-time decision musí rozlišovať unknown values a computed attributes. Unknown nesmie byť automaticky považované za compliant.

## 41. Plan oproti state a runtime

```text
source policy test
→ plan policy
→ apply result
→ runtime audit
```

Každý pohľad odhaľuje iný stav.

Terraform plan môže byť compliant, ale out-of-band mutation alebo provider behavior môže vytvoriť runtime drift.

## 42. Kubernetes admission

Admission policy rozhoduje pri API write path-e pred persistence resource-u.

Môže:

- validate,
- deny,
- warn,
- mutate,
- audit podľa implementation.

Admission nevidí všetky runtime udalosti. Pod môže neskôr zlyhať, image tag sa môže zmeniť alebo external controller môže vytvoriť ďalšie objekty.

## 43. ValidatingAdmissionPolicy a CEL

Kubernetes ValidatingAdmissionPolicy je in-process declarative validation mechanizmus používajúci CEL.

Model:

```text
ValidatingAdmissionPolicy
+ ValidatingAdmissionPolicyBinding
+ voliteľný parameter resource
→ admission decision
```

Výhodou je absencia external webhook network dependency. Scope, parameters, match conditions a failure policy však stále vyžadujú dôkladný design.

## 44. MutatingAdmissionPolicy

Kubernetes MutatingAdmissionPolicy poskytuje declarative in-process mutation cez CEL-based policy model.

Mutation je riskantnejšia než validation, pretože mení user intent a môže ovplyvniť následné validators.

Preferuj validation, keď platforma nepotrebuje bezpečne a transparentne doplniť konkrétny default.

## 45. Admission ordering

Kubernetes admission môže zahŕňať viac mutating a validating stages.

Policy musí analyzovať:

- object pred mutation,
- final object po mutation,
- reinvocation,
- controller-created resources,
- subresources,
- exempt system resources.

Verifier image signature musí vidieť digest, ktorý bude skutočne uložený a spustený.

## 46. Failure policy

Admission alebo external PDP potrebuje explicitný failure behavior.

```text
Fail/deny → dependency error blokuje request
Ignore/allow → dependency error request prepustí
```

Fail-closed chráni security invariant, ale môže zastaviť control plane. Fail-open zachová availability, ale vytvorí bypass window.

Rozhodnutie má byť per-policy a per-operation, nie globálny default bez risk analýzy.

## 47. Gatekeeper

Gatekeeper integruje OPA Constraint Framework s Kubernetes.

Validation model:

- `ConstraintTemplate` definuje reusable logic a parameter schema,
- `Constraint` aplikuje template na konkrétny scope,
- enforcement action určuje deny, warn, dry-run alebo iný supported behavior,
- audit vyhodnocuje existujúce resources.

Gatekeeper podporuje viac enforcement points, napríklad admission, audit a shift-left Gator evaluation.

## 48. Gatekeeper audit

Audit deteguje pre-existing alebo drifted violations, ktoré admission nemuselo zachytiť.

Operational limits:

- periodický, nie okamžitý,
- status môže obsahovať iba limitovaný počet violations,
- potrebuje broad read permissions,
- audit writer je singleton-like dependency,
- userInfo nemusí byť dostupné pri background evaluation.

Audit report nie je historical event store.

## 49. Kyverno

Kyverno poskytuje Kubernetes-native policy resources pre validation, mutation, generation, cleanup a image verification.

Aktuálny model používa samostatné policy types ako `ValidatingPolicy`, `MutatingPolicy`, `GeneratingPolicy` a `ImageValidatingPolicy`.

Pri návrhu vždy over podporovanú API version a deprecation status konkrétnej Kyverno release.

## 50. Kyverno Policy Reports

Policy Reports reprezentujú current evaluation state matched resources.

Nie sú úplným historical logom blocked requests.

Použi:

- PolicyReport/ClusterPolicyReport pre current compliance,
- Kubernetes Events a engine metrics pre admission failures,
- external log retention pre audit history.

## 51. Validation, mutation a generation

Rozlišuj:

```text
validation → prijmi alebo odmietni
mutation   → zmeň request/object
generation → vytvor alebo synchronizuj ďalší resource
```

Mutation a generation rozširujú blast radius policy chyby. Potrebujú stricter review, ownership a rollback.

## 52. Authorization policy

Application authorization policy vyhodnocuje:

```text
principal
+ action
+ resource
+ context
→ allow/deny/obligations
```

Policy engine nenahrádza authentication ani trusted identity mapping. Neoverený caller-controlled claim nesmie byť PIP attribute.

## 53. Obligations a advice

Decision môže obsahovať viac než allow/deny:

- required MFA,
- masking fields,
- maximum transaction amount,
- logging obligation,
- approval requirement,
- rate limit tier.

PEP musí podporovať obligations atomicky. Ignorovaná obligation nesmie byť považovaná za successful enforcement.

## 54. Multi-tenant policy

Tenant boundary musí byť súčasťou inputu a data keys.

Kontroluj:

- tenant identity source,
- resource tenant,
- delegated administration,
- cross-tenant support access,
- shared caches,
- policy data partitioning,
- decision-log isolation.

Global allow rule bez tenant bindingu môže vytvoriť cross-tenant access.

## 55. Exceptions

Exception je versionovaný policy object alebo explicitná data entry, nie komentár v code-e.

Musí obsahovať:

- policy ID,
- exact scope,
- ownera,
- reason,
- risk acceptance,
- compensating controls,
- expiry,
- approvera,
- audit evidence.

Wildcard exception bez expiry je policy bypass.

## 56. Break-glass

Break-glass path má byť:

- oddelený,
- časovo obmedzený,
- strongly authenticated,
- explicitne approved,
- plne auditovaný,
- automaticky revoke-nutý,
- testovaný.

Break-glass nemá znamenať vypnutie všetkých policies bez evidencie.

## 57. Rollout model

Bezpečný rollout:

```text
unit tests
→ historical replay
→ CI advisory
→ runtime audit/dry-run
→ limited scope enforce
→ širší enforce
→ continuous monitoring
```

High-risk deny policy nemá ísť z neotestovaného commit-u priamo na všetky production requests.

## 58. Policy canary

Policy canary aplikuje novú revision iba na časť:

- namespaces,
- tenants,
- workloads,
- regions,
- request percenta podľa stabilného partitioning-u.

Porovnaj decision rate, errors, latency a business impact pred promotion.

## 59. Rollback

Rollback musí obnoviť konkrétnu poslednú známu dobrú policy revision.

Testuj:

- distribúciu old bundle,
- cache invalidation,
- PDP activation,
- decision consistency,
- rollback permissions,
- audit evidence.

Rollback na mutable `latest` nie je deterministický.

## 60. Decision logs

Decision log má obsahovať:

- decision ID,
- timestamp,
- policy revision,
- input identity alebo safe reference,
- result,
- reason/policy IDs,
- PDP instance,
- latency,
- correlation ID.

Citlivé input fields musia byť maskované alebo odstránené pred exportom.

## 61. Decision-log limits

Decision logs môžu obsahovať secrets, personal data alebo proprietary configuration.

Definuj:

- masking policy,
- sampling/drop rules,
- rate limits,
- retention,
- access control,
- integrity,
- regional data boundary.

Dropped logs musia byť metric a alert, inak audit coverage silently klesá.

## 62. Observability

Sleduj:

- allow/deny/error rate,
- not-applicable/undefined rate,
- evaluation latency,
- policy revision distribution,
- bundle activation failures,
- stale data age,
- exception usage,
- fail-open events,
- decision-log drops,
- audit backlog,
- top violated policies.

Policy labels nesmú obsahovať high-cardinality secrets alebo raw resource IDs bez kontroly.

## 63. Performance

Policy latency závisí od:

- input size,
- rule complexity,
- collection scans,
- data size,
- external calls,
- compilation/caching,
- concurrency.

Benchmarkuj realistic worst-case inputs. Pri admission path-e je policy latency súčasť API server write latency.

## 64. Availability architecture

Možnosti PDP deploymentu:

- embedded library/WASM,
- sidecar,
- node-local daemon,
- centralized service,
- in-process control-plane policy.

Trade-offy:

- consistency,
- latency,
- failure blast radius,
- update speed,
- observability,
- trust boundary.

## 65. Bootstrap problem

Policy infrastructure sama potrebuje policy:

- kto môže meniť PAP,
- kto publikuje bundles,
- kto mení trusted keys,
- kto upravuje failure mode,
- kto vypína webhook alebo sidecar,
- kto číta decision logs.

Najkritickejšie bootstrap controls musia byť chránené mimo bežnej policy path alebo viacvrstvovo.

## 66. Policy engine security

Chráň:

- admin API,
- bundle credentials,
- TLS identity,
- filesystem/cache,
- runtime sandbox,
- plugins,
- decision logs,
- policy data.

Policy engine často spracúva attacker-controlled input a high-value authorization context.

## 67. Compromised policy response

```text
identifikovať policy revision a scope
→ zastaviť ďalšiu distribution
→ quarantine malicious bundle
→ obnoviť last-known-good revision
→ zistiť decisions počas exposure window
→ identifikovať bypassed alebo blocked operations
→ revoke-nuť compromised publisher identity
→ opraviť approval a distribution path
→ pridať regression tests
```

Nestačí revert-nuť Git commit, ak old revision už beží v caches alebo embedded artifacts.

## 68. Troubleshooting decision

```text
PEP zachytil operation?
→ input schema a identity správne?
→ PDP reachable/healthy?
→ správna policy revision aktívna?
→ supporting data načítané a fresh?
→ query path správny?
→ undefined/error mapping?
→ combining semantics?
→ exception match?
→ PEP presadil celý result?
```

## 69. Typické chyby

### Policy v CI prešla, runtime request bol povolený

Runtime enforcement neexistuje, používa inú revision alebo actual object sa po render/mutation zmenil.

### Admission zablokoval celý cluster

Policy scope je príliš broad, failure policy je fail-closed bez bootstrap exception alebo external dependency zlyhala.

### Audit nevidí rovnaké violations ako admission

Audit nemá userInfo, používa iný object snapshot, ignoruje request-only context alebo má stale cache.

### Bundle sa stiahol, ale neaktivoval

Over signature, manifest roots, compile errors, compatibility a status API.

### Exception po expiry stále funguje

Data cache je stale, expiry sa nevyhodnocuje alebo exception cleanup nie je autoritatívny.

## 70. Metrics a governance

Užitočné metrics:

- policy coverage podľa enforcement pointu,
- percento policies s ownerom a tests,
- exception count a expired exceptions,
- audit-to-enforce conversion time,
- rollback success,
- stale revision count,
- fail-open events,
- mean decision latency,
- policy-caused incident rate,
- verified bypass attempts.

Počet policy files nie je maturity metric.

## 71. Anti-patterny

- policy ako neversionovaný UI setting,
- boolean decision bez reason a revision,
- iba shift-left bez runtime enforcementu,
- iba runtime deny bez developer feedbacku,
- implicitný default allow,
- external call pri každom admission requeste bez cache/failure designu,
- broad exception bez expiry,
- mutation použitá tam, kde stačí validation,
- policy engine admin API dostupné workloads,
- decision logs s plaintext secrets,
- rollout na všetky environments naraz,
- meranie úspechu počtom blokovaných requests.

## 72. Kontrolné otázky

1. Aký je rozdiel medzi policy intentom, decisionom a enforcementom?
2. Aké úlohy majú PAP, PDP, PEP a PIP?
3. Ako sa líši input a supporting data?
4. Čo znamená undefined result a prečo je nebezpečný?
5. Ako funguje OPA bundle lifecycle?
6. Čo podpis policy bundle dokazuje a čo nie?
7. Ako testovať allow aj deny semantics?
8. Prečo shift-left nenahrádza runtime enforcement?
9. Ako sa líši validation, mutation a generation?
10. Čo poskytuje Kubernetes ValidatingAdmissionPolicy?
11. Ako fungujú Gatekeeper ConstraintTemplate a Constraint?
12. Aké limity majú Policy Reports a background audit?
13. Ako navrhnúť exception a break-glass?
14. Ako zvoliť fail-open alebo fail-closed?
15. Ako reagovať na malicious policy revision?

## Glossary impact

Relevantné pojmy: Policy as Code, policy intent, executable policy, policy lifecycle, Policy Administration Point, Policy Decision Point, Policy Enforcement Point, Policy Information Point, policy input, policy data, declarative policy, default deny, policy composition, policy conflict, policy revision, policy bundle, signed policy bundle, policy distribution, Open Policy Agent, Rego, undefined decision, structured decision, partial evaluation, policy WebAssembly, policy unit test, policy coverage, differential policy testing, shift-left policy, Conftest, infrastructure policy, admission policy, ValidatingAdmissionPolicy, ValidatingAdmissionPolicyBinding, MutatingAdmissionPolicy, CEL policy, failure policy, Gatekeeper, ConstraintTemplate, Constraint, Gatekeeper audit, Kyverno, Policy Report, policy obligation, policy exception, break-glass policy, policy canary, decision log, policy revision skew a policy bypass.

## Primárne zdroje

- [Open Policy Agent documentation](https://www.openpolicyagent.org/docs)
- [OPA Policy Language — Rego](https://www.openpolicyagent.org/docs/policy-language)
- [OPA Bundles](https://www.openpolicyagent.org/docs/management-bundles)
- [OPA Decision Logs](https://www.openpolicyagent.org/docs/management-decision-logs)
- [OPA Status](https://www.openpolicyagent.org/docs/management-status)
- [Gatekeeper documentation](https://open-policy-agent.github.io/gatekeeper/website/docs/)
- [Gatekeeper Constraint Templates](https://open-policy-agent.github.io/gatekeeper/website/docs/constrainttemplates/)
- [Gatekeeper Audit](https://open-policy-agent.github.io/gatekeeper/website/docs/audit/)
- [Kubernetes Validating Admission Policy](https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/)
- [Kubernetes Mutating Admission Policy](https://kubernetes.io/docs/reference/access-authn-authz/mutating-admission-policy/)
- [Kyverno policy types](https://kyverno.io/docs/policy-types/overview/)
- [Kyverno Policy Reports](https://kyverno.io/docs/guides/reports/)
- [Conftest documentation](https://www.conftest.dev/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Image signing](image-signing.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Zero Trust →](zero-trust.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
