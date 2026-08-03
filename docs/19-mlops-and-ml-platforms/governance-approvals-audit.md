# Governance, approvals a audit

ML governance je systém rozhodovacích práv, risk tolerancií, evidence a accountability naprieč celým lifecycle. Nemá byť manuálnou pečiatkou na konci pipeline. Approval je autoritatívne rozhodnutie viazané na presný subject a evidence bundle; audit je reprodukovateľný záznam toho, kto, čo, na základe čoho a s akým výsledkom zmenil.

V incidente `MLOPS-PAY-95` bol candidate technicky schválený, pretože offline metrics a CI prešli. Business owner však neschválil novú review-capacity policy, privacy review nevidelo rozšírené logging fields a deployment operator použil emergency override bez expiry. Po incidente nebolo možné z jedného systému zistiť, ktorý approver schválil model, policy a telemetry scope. Governance preto musela prejsť od všeobecného ticketu k immutable decision subjectu a append-only evidence chain.

## 1. Governance lifecycle

Governance pokrýva inventory, intended use, risk classification, ownership, validation, approval, deployment, monitoring, incident response a retirement.

```text
system inventory
→ intended use a context
→ risk classification
→ controls a evidence requirements
→ validation
→ approval decision
→ deployment a monitoring
→ incident/change review
→ retirement a record retention
```

NIST AI RMF organizuje risk management cez Govern, Map, Measure a Manage. Tieto funkcie nie sú jednorazový checklist; governance je cross-cutting a pokračuje počas lifecycle.

## 2. Exact approval subject

Approval musí viazať composite release a context, nie iba model version.

```yaml
decision_id: gov-fraud-2026-08-03-17
system_id: fraud-decision-platform
intended_use: transaction-risk-prioritization-v6
release_id: fraud-serving-2026-08-03.4
evidence_bundle: sha256:eval-bundle
risk_profile: high-impact-internal-v3
changes:
  model: v184
  features: fraud-request-v11
  policy: queue-capacity-v8
  telemetry: fraud-monitor-v9
decision: approved_with_conditions
conditions:
  - canary_max_traffic_10pct
  - human_review_capacity_500_per_hour
expires_at: 2026-09-03T00:00:00Z
```

Ak sa po approval zmení package digest, feature generation, action policy alebo intended use, approval už neplatí alebo potrebuje definovaný delta review.

## 3. Roles a separation of duties

RACI nestačí, ak nie je spojené s konkrétnymi permissions. Model owner vlastní performance a limitations. Data owner vlastní provenance a lawful use. Platform owner vlastní deployment a recovery. Business owner vlastní intended outcome a capacity. Risk/privacy/security role vlastní príslušné controls. Approver nesmie automaticky schvaľovať vlastnú zmenu pri high-risk subjecte.

Separation of duties sa implementuje branch protection, environment approvals, policy engine a Registry permissions. Emergency access je time-bound, logged a následne reviewed.

## 4. Risk-based gates

Nie každý model potrebuje rovnaký proces. Gate depth závisí od impactu, autonomy, affected population, reversibility, data sensitivity a regulatory context. Low-risk internal ranking môže mať automatizované approval; high-impact decision potrebuje multidisciplinárne evidence a human oversight.

Risk acceptance musí pomenovať residual risk, ownera, expiry a monitoring. „Known limitation“ bez ownera a deadline je iba odložený defect.

## 5. Evidence bundle

Approval evidence spája lineage, dataset, evaluation, package, security, deployment a operational readiness.

```text
intended-use statement
data a model lineage
evaluation a segment results
calibration/robustness/fairness evidence
package a supply-chain provenance
privacy/security review
capacity a rollback test
monitoring a incident plan
known limitations
```

Bundle je immutable alebo content-addressed. Dashboard link nie je dostatočný, ak sa jeho query alebo data neskôr zmenia.

## 6. Policy as code a manual judgment

Policy as code automatizuje deterministické controls: required fields, signed artifact, metric thresholds, approved resource class, retention a segregation. Nenahrádza odborný judgment pri intended use, social impact alebo residual risk.

Policy result musí vysvetliť input generation a failed rule. Override je samostatná decision s reason, approver, scope a expiry. Permanentný `skip=true` bez expiry je governance bypass.

## 7. Audit trail a tamper evidence

Audit event obsahuje actor identity, role, timestamp, operation ID, subject digest, previous/new state, evidence pointer a outcome. Logy musia byť append-only alebo chránené proti nepozorovanej mutation.

```json
{
  "event": "promotion_approved",
  "decision_id": "gov-fraud-2026-08-03-17",
  "actor": "risk-approver-12",
  "subject_digest": "sha256:release-manifest",
  "previous_state": "candidate",
  "new_state": "approved_with_conditions",
  "evidence_digest": "sha256:eval-bundle",
  "timestamp": "2026-08-03T11:40:00Z"
}
```

Correlation ID spája Git, CI, Registry, deployment a runtime. Audit trail nesmie ukladať secrets ani nepotrebné osobné údaje.

## 8. Regulatory a standards mapping

Governance musí mapovať konkrétny use case na platné zákony, sektorové pravidlá a interné policies. EU AI Act používa risk-based obligations; pri relevantných high-risk systémoch zahŕňa risk management, technical documentation, logging, human oversight a post-market monitoring. Presná právna klasifikácia patrí právnym a compliance odborníkom, nie automatickému MLOps toolu.

NIST AI RMF je voluntary framework, nie zákon ani certifikácia. Je vhodný na štruktúrovanie Govern, Map, Measure a Manage outcomes, ale organizácia musí vytvoriť vlastný profile podľa contextu a risk tolerance.

## 9. Human oversight

Human oversight musí mať authority, informácie, čas a možnosť zasiahnuť. Reviewer, ktorý vidí iba model score a nemôže decision zmeniť, nie je efektívny oversight. Interface musí ukázať limitations, uncertainty a escalation path.

Oversight sa testuje: vie operátor rozpoznať out-of-scope input, zastaviť automation, použiť fallback a nahlásiť incident? Training attendance sama nepreukazuje capability.

## 10. Change management a substantial modification

Model retrain, threshold change, feature addition, nový segment, logging expansion alebo deployment context môžu meniť risk. Change classifier určuje, či stačí automated delta gate alebo full reapproval.

Silent change cez mutable alias alebo feature flag obchádza governance. Runtime musí reportovať loaded composite generation a porovnať ju so schváleným subjectom.

## 11. Incident, waiver a expiry

Incident môže aktivovať emergency override. Override musí byť least privilege, časovo obmedzený a automaticky expirovať. Následná review overí použitie a obnoví normal controls.

Waiver obsahuje failed control, justification, compensating controls, ownera, affected scope a expiry. Expired waiver blokuje ďalšiu promotion.

## 12. Retirement a retention

Governance končí bezpečným retirementom. Model sa odoberie z trafficu, credentials a endpoints sa zrušia, artifacts a audit evidence sa uchovajú podľa retention policy a downstream users sa informujú. Delete Registry entry bez inventory closure môže zničiť incident evidence.

## 13. Acceptance boundaries

Pozitívna acceptance vyžaduje presný approval subject, risk-based required roles, immutable evidence, policy results, runtime conformity a audit trail. Recovery acceptance vyžaduje zdokumentovaný emergency decision, obnovenie normal controls a review side effects. Forbidden acceptance je všeobecný ticket „approved“, self-approval pri chránenom subjecte, permanent override alebo dashboard bez immutable evidence.

Second-operation test zopakuje rovnakú promotion alebo no-op approval. Ak sa rozhodnutie zmení pre mutable evidence, chýbajúci approver alebo expirovaný waiver, governance nie je deterministická. Audit musí vedieť spätne zostaviť celý decision chain bez osobnej pamäte tímu.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Model rollback a recovery](model-rollback-recovery.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
