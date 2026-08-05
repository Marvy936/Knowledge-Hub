# Human approval, audit a rollback

Human approval má oddeliť návrh od oprávnenia vykonať citlivú zmenu. Kliknutie na `Approve` však nie je samo osebe bezpečnostná vlastnosť. Approval musí byť viazaný na exact subject, diff, policy generation, identity, čas a execution envelope; audit musí zachytiť celú decision chain a rollback musí obnoviť known-good state bez predstierania, že všetky externé side effects sú reverzibilné.

V incidente `AGENT-GOV-13` approver videl iba vetu „Deploy verified payments release“. Approval neukazoval mutable image tag, effective policy action `Warn and Continue` ani to, že pipeline executor mohol schváliť vlastný run. Po approvale sa zmenil manifest commit, no čakajúci execution sa obnovil bez revalidation. Audit trail nemal pipeline execution events zapnuté a rollback vrátil workload, nie už vykonané schema a payment side effects.

Nosný lifecycle je:

```text
bounded mutation proposal
→ exact approval subject a evidence snapshot
→ approver eligibility a separation of duties
→ expiry, quorum a decision
→ pre-execution revalidation
→ authorized mutation s operation ID
→ audit event chain
→ technical a business verification
→ rollback alebo roll-forward decision
→ compensating actions a reconciliation
→ second-approval acceptance
```

## 1. Approval subject

Approval subject je immutable envelope, nie názov pipeline. Obsahuje resource, environment, source commit, manifest commit, artifact digest, policy result, tool arguments, expected outcome a rollback plan.

Ak sa ktorýkoľvek load-bearing field zmení, vzniká nový subject a starý approval je neplatný. Hash approval envelope-u sa prenáša do execution-u.

## 2. Proposal verzus authorization

Agent alebo pipeline vytvára proposal. Approval je authorization decision od identity s príslušným oprávnením.

Proposal text nesmie byť interpretovaný ako implicitný súhlas. Ani previous successful approval sa nerecykluje na novú generation.

## 3. Approver eligibility

Harness approvals umožňujú určiť user groups a minimálny počet approvers. Eligibility sa vyhodnocuje pri rozhodnutí, nie iba pri vytvorení step-u.

User group membership, role a scope sa zaznamenajú do decision evidence. Deaktivovaný alebo presunutý používateľ nesmie zostať validným approverom cez cached membership.

## 4. Separation of duties

Pipeline executor, author policy, agent operator a approver sú odlišné roles pri high-risk changes. Harness approval konfigurácia podporuje zákaz schválenia vlastného execution-u.

`disallowPipelineExecutor: false` je vedomé zníženie kontroly, nie bezpečný default. Self-approval test musí byť súčasťou acceptance.

## 5. Quorum

Quorum určuje počet nezávislých approvals a prípadne rôzne role. Dve kliknutia od účtov patriacich tej istej automation identity nepredstavujú four-eyes control.

Decision engine overí uniqueness principalov a required groups. Duplicate alebo delegated session sa nezapočíta dvakrát.

## 6. Approval context

Approver potrebuje exact diff, resolved inputs, policy findings, risk, blast radius, prior execution history a rollback constraints. Vágny generated summary nestačí.

Context sa renderuje z immutable envelope-u. UI summary je view, nie source of truth.

## 7. Sensitive data

Approval card nesmie zobraziť secrets alebo zbytočné PII. Zároveň redaction nesmie skryť resource identity, tenant alebo operation scope.

Sensitive arguments sa zobrazia ako stable references a safe diffs. Approver musí vedieť, čo sa zmení, bez získania credential value.

## 8. Expiry

Approval má timeout a explicitný expiry. Harness manual approval steps majú default timeout jeden deň a podporujú dlhšie limity, ale dlhá platnosť zvyšuje stale-decision risk.

Security expiry môže byť kratší než workflow timeout. Po expiry execution failne alebo vytvorí nový approval subject.

## 9. Auto approval

Scheduled auto-approval a failure strategy `Mark as Success` sú odlišné mechanizmy. Automatické pokračovanie pri timeout-e nesmie byť prezentované ako ľudské schválenie.

High-risk mutation zakazuje fail-open approval. Auto approval má vlastnú policy, actor a audit reason.

## 10. Previous waiting executions

Harness podporuje auto-reject starších deployments pri schválení novšieho execution-u, no identity step-u a service changes ovplyvňujú behavior. Stale queue sa nesmie riešiť iba názvom step-u.

Approval coordinator porovná subject generations a explicitne zruší superseded requests. Starý execution sa nesmie po neskoršom resume dostať pred nový.

## 11. Parallel approvals

Approval step nemá bežať paralelne s mutation, ktorú má gate-ovať. Harness UI takú konfiguráciu obmedzuje, no YAML authoring môže vytvoriť nebezpečný graph.

Semantic validator overí dominanciu approval node-u nad všetkými protected paths. Visual placement nie je dôkaz control flow.

## 12. Decision types

Approval decision je approve, reject, prípadne edit-and-resubmit. Edit nevykonáva pôvodný subject; vytvára nový proposal a podľa risku nový approval.

Free-text comment je supporting context. Authority je structured decision nad subject hashom.

## 13. Rejection

Reject ukončí alebo presmeruje execution podľa explicitnej failure strategy. Nesmie automaticky vyvolať alternatívnu mutation, ktorá obíde pôvodný gate.

Reason code a comment sa uchovajú. Agent môže pripraviť remediation proposal, ale nie preklasifikovať rejection na temporary error.

## 14. Revalidation

Tesne pred mutation sa znovu overí subject hash, approver eligibility, policy bundle, environment generation, credential generation a resource preconditions.

Approval z minulosti nad starým manifestom nepovoľuje nový deploy. TOCTOU mismatch vytvára nový approval cycle.

## 15. Operation identity

Authorized mutation dostane stable operation ID spojené s approval ID. Retry používa rovnaký key a nevytvára druhý side effect.

Audit rozlišuje approval, execution attempt, provider acknowledgment a confirmed effect. Jedna approval môže autorizovať presne definovaný počet operations.

## 16. Audit chain

Audit chain obsahuje proposal creation, policy decisions, approval request, views, approvals/rejections, subject supersession, execution attempts, resource changes a rollback.

Chronologický UI list je iba view. Export alebo event stream musí zachovať stable IDs a correlations.

## 17. Harness audit scope

Harness Audit Trail je dostupný na account a organization scope a uchováva key actions. Pipeline execution audit events nemusia byť zapnuté defaultne; príslušné account setting musí byť explicitne aktivované.

Control preto testuje, že potrebné event categories skutočne vznikajú. Audit feature enabled neznamená kompletnú execution evidence.

## 18. Audit immutability

Harness opisuje audit events ako automaticky generované a nemeniteľné. Organizácia však stále rieši export, retention, access a external correlation.

Immutable vendor record nenahrádza business ledger ani provider evidence. Audit dokazuje activity, nie automaticky správnosť outcome-u.

## 19. Retention

Harness audit records sa uchovávajú do dvoch rokov; dlhšia potreba vyžaduje external streaming alebo archív. Retention sa zladí s compliance a incident horizon.

Approval evidence nesmie expirovať skôr než resource a business records potrebné na reprodukciu rozhodnutia.

## 20. Audit completeness

Každá required event class má synthetic test. Test vykoná approval, rejection, expiry, supersession, mutation a rollback a potom overí event coverage.

Chýbajúci event failuje audit acceptance aj keď deployment prešiel. No-data sa neinterpretuje ako „nič sa nestalo“.

## 21. Technical rollback

Rollback vracia deployable state na known-good artifact a configuration generation. Harness post-deployment rollback podporuje vybrané deployment types a typicky sa viaže na posledný successful deployment.

„Last successful“ musí byť resolved na exact digest a manifest. Success pipeline-u neznamená business-safe rollback target.

## 22. GitOps rollback

GitOps recovery preferuje revert alebo nový commit v source of truth a následnú reconciliation. Direct cluster mutation vytvára drift a slabšiu audit chain.

Harness GitOps podporuje history/rollback a PR pipeline môže použiť Revert PR. Rollback subject obsahuje commit, application generation a sync evidence.

## 23. Roll-forward

Pri databázových alebo external side effects môže byť roll-forward bezpečnejší než binary rollback. Decision zohľadní compatibility, data migration a user impact.

Agent môže porovnať options, no incident alebo release owner schvaľuje recovery path. Risk model je explicitný.

## 24. Non-reversible effects

Odoslaný email, payment capture, deleted object alebo irreversible schema change sa nevráti iba deploy rollbackom. Potrebuje compensating action alebo reconciliation.

Rollback plan preto klasifikuje effects ako reversible, compensatable alebo irreversible. Vágne `rollback: true` je zakázané.

## 25. Database compatibility

Application rollback na starší binary môže zlyhať po forward-only migration. Release envelope uvádza schema generation a compatibility window.

Pre expand-contract model sa rollback testuje v staging-u s realistic data. Agent nesmie predpokladať kompatibilitu podľa názvu migration.

## 26. Credential a secret changes

Rollback secretu alebo connectora môže obnoviť starý credential, ktorý je revokovaný alebo compromised. Recovery sa viaže na current authority, nie na historickú value.

Secret rollback často znamená novú rotation generation. Audit uchová reference a actor, nie plaintext.

## 27. Verification

Po rollbacku sa overí live resource digest, readiness, telemetry a business invariant. Pipeline step success nestačí.

Verification window musí vylúčiť stale caches a partial rollout. Unknown business state drží incident otvorený.

## 28. Approval pre rollback

Emergency rollback môže mať skrátený approval path, nie nulovú authority. Preddefinovaná policy určuje kto, kedy a aký known-good target môže aktivovať.

Break-glass decision má expiry, reason a post-hoc review. Agent si break-glass neudelí sám.

## 29. Rollback loop

Automatický rollback sa môže opakovane spúšťať pri noisy signal-e. Loop guard obmedzí počet transitions a eskaluje na človeka.

Každý rollback vytvára novú resource generation a verification. Systém nesmie ping-pongovať medzi dvoma neoverenými states.

## 30. Incident containment

Pri podozrení na stale approval sa execution suspenduje, mutation tokens sa revokujú a approval subjects sa označia superseded. Evidence sa uloží pred cleanupom.

Následne sa identifikujú operations, ktoré mohli prejsť medzi approvalom a revocation. Tie sa reconciliujú proti provider a business state.

## 31. Positive acceptance

Authorized approver vidí exact immutable diff, policy result a rollback constraints. Dvaja nezávislí users schvália subject, pre-execution revalidation prejde a mutation použije stable operation ID.

Audit export obsahuje všetky events a post-deploy business verification prejde. Druhý deployment vyžaduje nový approval.

## 32. Forbidden acceptance

Self-approval, expired approval, changed manifest, missing policy evidence alebo unknown audit state nesmú spustiť mutation. Timeout nesmie byť `Mark as Success` pre high-risk path.

Rollback nesmie byť označený complete, ak data reconciliation chýba. Zero unauthorized side effects je acceptance criterion.

## 33. Recovery acceptance

Po stale approval sa execution zastaví, subject supersede-ne a nový envelope prejde policy a approval cycle. Nesprávny deployment sa revertne alebo roll-forwardne podľa compatibility.

Audit chain zachová starý aj nový subject. Alternate test overí rejection, expiry a break-glass path.

## 34. Practical approval envelope

Approval envelope je immutable decision object medzi proposalom a mutation. Spája exact subject, required approvers, expiry, policy evidence, operation count a recovery constraints.

Nasledujúci record ukazuje approval, ktorý sa nesmie znovu použiť po zmene manifestu:

```yaml
approval:
  id: appr-2026-0813
  subject_digest: sha256:45be...
  resource:
    pipeline: payments-prod
    execution_generation: exec-991
    manifest_commit: 8b3f...
    artifact_digest: sha256:aa11...
  policy:
    bundle_digest: sha256:9c31...
    decision_id: dec-778
    outcome: allow
  quorum:
    required: 2
    disallow_pipeline_executor: true
  expires_at: 2026-08-05T16:00:00Z
  authorized_operations: 1
  rollback:
    target_manifest_commit: 2a19...
    business_reconciliation_required: true
```

Execution pred mutation vypočíta envelope znovu. Ak digest nesedí, approval sa nepoužije a vznikne nový request.

## 35. Primary sources

Harness manual approval stages a steps, user groups, minimum approver count, timeout, auto-reject old deployments a upozornenie na parallel YAML configuration opisuje https://developer.harness.io/docs/platform/approvals/adding-harness-approval-stages/. Governance quickstart na https://developer.harness.io/docs/platform/governance/policy-as-code/harness-governance-quickstart/ ukazuje approval konfiguráciu vrátane `minimumCount` a `disallowPipelineExecutor`.

Harness Audit Trail semantics, scope, fields, retention a potrebu explicitne zapnúť pipeline execution audit events dokumentuje https://developer.harness.io/docs/platform/governance/audit-trail/. GitOps-specific audit events sú na https://developer.harness.io/docs/continuous-delivery/gitops/security/audit-trail/. Post-deployment rollback constraints sú na https://developer.harness.io/docs/continuous-delivery/manage-deployments/rollback-deployments/ a GitOps PR/revert flow na https://developer.harness.io/docs/continuous-delivery/gitops/pr-pipelines/pr-pipelines-basics/. Tieto zdroje definujú platform mechanisms; konkrétnu reversibility a business recovery musí preukázať vlastný release a incident evidence chain.

## Zhrnutie

Human approval je bezpečnostná hranica iba vtedy, keď schvaľuje exact immutable subject, overuje eligible independent identity a pred mutation prejde revalidation. Audit musí zachytiť proposal, decision, execution a recovery; rollback musí rozlišovať workload state od externých a dátových side effects.

Ďalšia kapitola presunie pozornosť na vendor lock-in a portability agentických workflowov.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Policy generation a policy validation](policy-generation-policy-validation.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Vendor lock-in a portability agentických workflowov →](vendor-lock-in-portability-agentic-workflows.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
