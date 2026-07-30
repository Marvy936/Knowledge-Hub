# Guardrails

Guardrail je mechanizmus, ktorý udržiava zmenu alebo runtime behavior v explicitnom bezpečnom priestore bez toho, aby každé rozhodnutie presúval do manuálneho ticketu. Môže poskytovať safe default, early feedback, audit, mutation, correction alebo tvrdé odmietnutie. Jeho hodnotu neurčuje počet policy files ani nulový denial count. Určuje ju to, či chránený invariant pokrýva expected subjects, rozhoduje na authoritative boundary a preukazuje effective outcome.

```text
risk, obligation alebo invariant
→ exact protected subject a unacceptable outcome
→ enforcement a observation boundaries
→ versioned policy, binding, parameters a exceptions
→ expected subject inventory a impact preview
→ staged Warn/Audit/Deny/Generate/Correct behavior
→ request decision s provenance
→ persisted a runtime state read-back
→ coverage, violation a business verification
→ remediation, exception expiry a policy evolution
→ second tenant a bypass test
```

Policy controller `Ready=True`, successful CI lint alebo `0 denied requests` samy osebe nič nehovoria o tom, či critical request vôbec matchol policy.

## 1. Invariant pred policy jazykom

Guardrail design začína assetom, actorom, action, precondition, unacceptable outcome a tolerovanými exceptions. Rule `require tenant label` je iba syntaktický mechanismus. Underlying invariant môže byť `restricted workload nesmie byť provision-nutý mimo dedicated tenant isolation profile`.

Jedno field check nemusí invariant pokryť. Label môže byť stale, user-mutable alebo odvodený z catalog projection. Admission môže request odmietnuť, no existing resources a external provider context môžu zostať wrong. Invariant sa preto rozkladá na earliest useful feedback, authoritative preventive control a detective/effective-state verification.

Guardrail, gate, default a scorecard nie sú synonymá. Default znižuje decision load, gate podmieňuje transition, scorecard poskytuje derived assessment a guardrail ohraničuje allowed state. Golden path môže byť preferovaný, ale safety invariant má platiť aj pri custom path-e.

## 2. Exact guardrail subject

Policy name nestačí. Subject obsahuje immutable policy generation, binding a parameter generation, match constraints, enforcement point a engine version, request principal/operation/target, pre- a post-mutation object digest, selected exception a effective-state observation.

```text
policy restricted-tenant-boundary v7
+ binding production-restricted v4
+ parameter isolation-profile restricted-v3
+ request CREATE Namespace tenant-vega-71
+ admission engine Kubernetes generation
+ exception none
→ Deny alebo Allow verdict
```

Pri GitOps sa CI render, controller render a admission request môžu líšiť. Evidence nad chartom s values A neautorizuje source revision s values B. Admission mutation môže zmeniť object po CI. Subject continuity musí prejsť od reviewed renderu po stored object a runtime.

## 3. Expected inventory a match coverage

Policy success sa nedá merať iba evaluated requests. Najprv treba vedieť, ktoré subjects mali byť chránené. Expected inventory môže vychádzať z tenant registry, catalog freshness-qualified entities, namespaces, artifact inventory alebo critical API operations.

```text
expected restricted subjects
→ 47 namespaces/resources

policy matched
→ 46

no-match
→ 1 critical gap
```

Dashboard má ukázať expected, matched, passed, denied, warned, audited, errored, skipped a excepted subjects. `0 denials` môže znamenať plnú compliance, warn-only policy, broad exception alebo nulové matchovanie. No-match a evaluation error sú samostatné risk states, nie pass.

Coverage proof musí byť version-aware. Nová tenant profile generation alebo CRD môže vytvoriť subject, ktorý starý match rule nepozná. Policy rollout preto obsahuje inventory diff a negative fixture pre každý critical class.

## 4. Enforcement layers a authority

Guardrail môže poskytovať IDE/pre-commit feedback, CI render test, registry artifact policy, GitOps final-render policy, API admission, controller correction a runtime/background audit. Každý bod vidí iný subject a má inú authority.

Early feedback má byť rýchly a actionable, no je obíditeľný. Authoritative admission alebo provider policy musí chrániť invariant na final mutation path. Background scan pokrýva pre-existing resources a drift, ale nezabráni prvému violation. Runtime canary alebo data-access test overí effect, ktorý request-time policy nemôže poznať.

Layered controls majú používať korelovateľné policy generations a vysvetliť rozdiel. CI pass + admission deny môže znamenať iný render, parameter, namespace context alebo policy revision. Bez provenance developer vidí iba contradictory tools a začne policy obchádzať.

## 5. Kubernetes policy, binding a actions

ValidatingAdmissionPolicy oddeľuje abstract CEL logic, optional parameter resource a binding. Effective policy je kombinácia všetkých troch plus match conditions, validation actions a failure policy. Zmena parametra alebo binding selectoru mení guardrail aj bez zmeny expression.

`Deny` zastaví request. `Warn` request dovolí a vráti warning. `Audit` request dovolí a zaznamená failure v audit evidence. Warn/Audit sú vhodné na impact discovery a staged migration, ale nevytvárajú prevention. Dashboard nemá označiť warn-only rollout za enforced compliance.

`failurePolicy: Ignore` povoľuje request pri evaluation error-e; `Fail` ho odmietne. Rozhodnutie je per risk class. Fail-open pri critical tenant reference môže vytvoriť breach. Fail-closed policy s nedostatočnou capacity môže odstaviť API. Potrebné sú performance tests, timeout budget, emergency recovery a policy availability ownership.

## 6. Mutation, generation a correction

Mutation môže pridať safe defaults, no mení final subject. Musí byť deterministic, idempotentná, transparentná a field-owned. Viac mutators nad rovnakým fieldom vytvára precedence a oscillation. Tichá zmena service accountu, image alebo node placementu môže zmeniť tenant a security boundary.

Generate guardrail môže pri namespace creation vytvoriť NetworkPolicy, ResourceQuota alebo RoleBinding. Controller potom vlastní lifecycle generated resources a musí pokryť update, delete, orphan cleanup a outage. Tenant nesmie odstrániť alebo predefinovať critical generated object bez policy.

Corrective controller smie automaticky opraviť iba jednoznačný bounded drift. IAM, data retention alebo network mutation môže mať disruptive effect; potrebuje read-back, conflict detection a recovery. Detecting a reporting violation je často správnejšie než blind patch.

## 7. Exceptions ako capability s lifecycle-om

Exception nie je boolean annotation. Potrebuje exact policy/subject scope, requester a approver, reason a risk, alternative controls, start/expiry, usage evidence a closure verification. Wildcard alebo label-based exception bez expiry sa stáva hidden policy fork.

```text
exception request
→ exact resource/policy generation
→ risk approval
→ bounded exception object
→ match/use monitoring
→ expiry alebo revocation
→ subject returns to compliant state
→ exception removed
```

Exception musí byť evaluovaná spolu s requestom a zahrnutá v decision logu. PolicyException, ktorá preskočí všetky resources s `migration=true`, povoľuje tenantovi alebo automation rozšíriť scope, ak label nie je trusted a immutable.

Emergency exception môže byť potrebná, ale má short lifetime, ownera, incident link a negative test po closure. `Temporary` bez expiry nie je control.

## 8. Rollout ako migration

Nová guardrail policy je distributed migration nad consumer inventory. Najprv sa vykoná offline/CI test a impact preview, potom Audit/Warn pre discovery, owner remediation a exception cleanup, následne staged Deny a background verification. High-risk direct Deny môže zmraziť existing workloads, ak jediný update path narazí na unrelated legacy violation.

Rollout evidence zahŕňa match coverage, false positives/negatives, latency, errors, owner response, exception count/age a effective violation trend. Rollback policy generation musí byť pripravený, no nemá obnoviť known unsafe gap bez compensating containment.

Policy retirement tiež potrebuje lifecycle. Odstránenie controlleru alebo bindingu môže zanechať generated resources a otvorený boundary. Migration na nový engine musí porovnať decisions na rovnakom subject corpus-e.

## 9. Connected incident `GITOPS-PAY-64`

Stale catalog projection klasifikovala `settlement-export-api` ako `shared-internal` namiesto `vega-regulated/restricted`. LaunchPad preto vytvoril namespace so standard profile-om. Restricted guardrail binding sa nematchol.

Cross-namespace reference policy bola iba `Warn,Audit`. Navyše ju preskočila broad `PolicyException` pre label `platform.atlas.io/migration=true` bez expiry. Dashboard ukazoval `0 denied requests`, ale neobsahoval expected restricted-subject inventory, no-match subjects, warn failures ani skipped exceptions.

```text
expected: Vega restricted namespace/reference
actual profile: standard
restricted binding: no match
cross-namespace rule: warn/audit
broad exception: skip
request: allowed
```

Flux Kustomization bola `Ready=True` a privileged operator následne načítal foreign credential. Root cause guardrailu nebola syntaktická chyba policy. Program meral denials bez coverage a effective-state oracle-u; warn-only action a non-expiring broad exception nevytvárali prevention.

## 10. Authoritative redesign a acceptance paths

Redesign viaže stable tenant ID a controller-owned isolation profile na namespace UID. Policy bundle obsahuje exact policy/binding/parameter generations a expected inventory z freshness-qualified tenant registry. Restricted cross-tenant references používajú `Deny`; exceptions sú subject-bound a expiring. Flux cross-namespace references sú vypnuté a operator vykonáva same-tenant authorization.

Positive path dovolí validný Vega resource a runtime canary. Coverage path dokáže, že každý expected restricted subject matchol. Migration path prejde Audit/Warn až po remediation do Deny. Exception path expiruje a subject sa vráti do compliance. Failure path fail-closed odmietne unverified critical reference. Forbidden path odmietne zero-denial vanity metric, no-match-as-pass, warn-only prevention, broad label exception, stale catalog binding a policy-controller-ready proxy.

## 11. Troubleshooting a anti-patterny

Pri false-green policy sa kontroluje expected inventory, policy/binding/parameter generations, selector inputs a provenance, request principal/operation, pre/post mutation object, match/no-match reason, validation action, failurePolicy, exception selection, stored object a runtime outcome. Potom sa replay-ne exact incident subject a negative cross-tenant fixture.

Anti-patterny sú: `policy exists = enforced`, `0 denied = compliant`, `Warn je skoro Deny`, `CI pass = admission pass`, `exception cez broad label`, `policy Ready = invariant protected`, `background scan = prevention` a `mutation vždy znižuje friction`.

## Glossary impact

Relevantné pojmy: guardrail subject, protected invariant, expected policy inventory, match coverage, no-match risk, policy/binding/parameter generation, validation action, policy failure mode, mutation ownership, generated control, exception lifecycle, effective-state oracle a guardrail acceptance verdict.

## Primárne zdroje

- [Kubernetes — Validating Admission Policy](https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/)
- [Kubernetes — Policies](https://kubernetes.io/docs/concepts/policy/)
- [Kubernetes — Admission controllers](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Service catalog](service-catalog.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Multi-tenancy →](multi-tenancy.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
