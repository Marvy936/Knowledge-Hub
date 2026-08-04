# Agent governance a audit

Agent governance je organizačný a technický systém, ktorý určuje, kto smie agentický systém navrhnúť, schváliť, nasadiť, meniť, používať, monitorovať, zastaviť a vyradiť. Audit je nezávislé alebo kontrolné overovanie, či sa deklarované pravidlá, rozhodnutia a runtime udalosti dajú spätne preukázať a či zodpovedajú skutočnému správaniu.

Táto kapitola uzatvára incident `AGENT-GOV-06`. Release zvýšil retrieval fan-out, pridal fallback model a presunul tenanty do pooled workerov, ale zmena bola schválená ako „prompt improvement“. Review ticket neobsahoval tool, budget, tenancy ani kill-switch generations a risk owner videl iba aggregate answer-quality score. Po incidente sa ukázalo, že trace neobsahoval complete policy a side-effect evidence, exception pre shared cache nemala expiry a nikto nevedel, kto mal authority znovu aktivovať workflow po global stop-e.

Nosný lifecycle je:

```text
business purpose a accountable owner
→ exact agent system inventory a risk classification
→ intended use, users, tenants a prohibited boundaries
→ composed release a dependency/supplier inventory
→ policy, approval, segregation of duties a exception lifecycle
→ pre-deployment evidence a go/no-go decision
→ runtime audit events, monitoring a human oversight
→ incident, stop, notification a corrective action
→ periodic review, legal/applicability reassessment a retirement
→ independent audit a second-operation proof
```

## 1. Governance nie je iba dokument

Governance musí vytvárať enforceable decisions a evidence. Policy PDF bez ownera, version, approval, enforcement point a exception lifecycle nevie riadiť runtime systém.

Technické controls bez organizačnej authority sú rovnako neúplné. Kill switch môže existovať, ale ak nie je jasné, kto ho smie aktivovať, kedy a ako sa systém znovu povolí, incident response zostáva improvizovaný.

## 2. Governance, risk, compliance a audit

Governance určuje rozhodovacie práva a accountability. Risk management identifikuje, meria, prioritizuje a ošetruje neistoty a škody; compliance overuje konkrétne právne, regulačné, zmluvné alebo interné požiadavky; audit preveruje evidence a control effectiveness.

Tieto oblasti sa prekrývajú, ale nie sú zameniteľné. „Prešlo auditom“ neznamená automaticky bezpečné pre všetky use cases a interný risk tier neurčuje právnu klasifikáciu bez osobitnej applicability analýzy.

## 3. Accountable owner

Každý agentický systém má business ownera, technical ownera, risk alebo control ownera a operational ownera. Jedna osoba môže dočasne zastávať viac rolí, ale segregation of duties musí byť primeraná impactu.

Accountable owner prijíma residual risk a business outcome. Model provider, platform tím alebo agent developer nemôže byť automaticky jediným vlastníkom všetkých následkov.

## 4. Agent system inventory

Inventory eviduje celý agentický systém, nie iba model. Zahŕňa workflow, agents, prompts, models, tools, MCP/A2A servers, retrieval sources, memory, policies, credentials, sandboxes, tenants, data classes, human roles, dependencies a deployment environments.

Každý inventory subject má stable ID a lifecycle state, napríklad proposed, evaluation, approved, limited production, general production, suspended alebo retired. Neinventarizovaný experimental agent nesmie získať production tools cez shared platform default.

## 5. Exact governance subject

Governance decision sa viaže na composed release a intended use. Vague approval „support agent v2“ nestačí, ak model route, tool catalog alebo tenant mode sa mení nezávisle.

Subject obsahuje release manifest, risk classification, approved operation classes, tenant scope, regions, data categories, autonomy level a effective interval. Zmena ktoréhokoľvek významného prvku vyvolá change assessment.

```yaml
governance_subject:
  system_id: agent-system/support-remediation
  release_id: support-remediation/5.10.0
  release_digest: sha256:71fa...
  intended_use: diagnose checkout incidents and propose bounded remediation
  autonomy: human-approved-mutation
  tenants: pooled-enterprise-eu
  data_classes: [internal, confidential/customer]
  approved_actions: [diagnostics.read, remediation.propose, rollout.restart]
  prohibited_actions: [payment.refund, credential.export, cross_tenant.read]
  risk_tier: internal/high-impact
  effective_from: 2026-08-04T18:00:00Z
```

## 6. Intended use

Intended use opisuje business problem, users, operating context, supported inputs, outputs a decision/action boundary. „Customer support“ je príliš široké, pretože zahŕňa answer generation, account mutation, refunds aj identity verification.

Governance zároveň eviduje reasonably foreseeable misuse a unsupported use. Agent musí vedieť abstain alebo route mimo approved boundary namiesto rozširovania scope podľa promptu.

## 7. Risk classification

Interný risk tier kombinuje impact, autonomy, data sensitivity, reversibility, tenant reach, external effects, scale a human oversight. Tier určuje požadovanú evidence depth, approvers, rollout a monitoring.

Risk classification sa pravidelne prehodnocuje. Read-only agent sa môže stať high-impact po pridaní toolu, multi-tenant memory alebo automatic execution, aj keď model a názov produktu zostali rovnaké.

## 8. Legal applicability

Právna klasifikácia je samostatná analýza podľa jurisdikcie, roly organizácie, intended purpose, affected persons a konkrétneho use case. Nie každý agent je automaticky high-risk systém podľa EU AI Act a interné označenie `high-impact` nie je právny záver.

Governance record uchováva applicability ownera, posúdenie, dátum, assumptions a trigger pre nové posúdenie. Kapitola poskytuje technický model, nie právne stanovisko.

## 9. NIST AI RMF mapping

NIST AI RMF organizuje risk management cez Govern, Map, Measure a Manage. Agent governance môže tieto functions použiť ako organizing model: vytvoriť accountability, zmapovať context a impacts, merať performance a risks a riadiť response a recovery.

Mapping nie je checkbox certification. Každá organization musí priradiť konkrétne controls, owners, evidence a risk tolerances svojmu systému.

## 10. EU AI Act boundaries

EU AI Act obsahuje pre relevantné high-risk systémy požiadavky na risk management, technical documentation, logging, transparency, human oversight, accuracy, robustness a cybersecurity. Konkrétna povinnosť závisí od klasifikácie a roly provider/deployer/importer/distributor alebo inej dotknutej osoby.

Governance preto nesmie slepo označiť každý agent za compliant. Musí uchovávať applicability decision a evidence pre konkrétne požiadavky tam, kde sa uplatňujú.

## 11. Policy hierarchy

Policy hierarchy typicky obsahuje organization principles, risk policy, system standard, platform controls, workflow policy a operation decision. Nižšia vrstva môže pravidlá sprísniť, ale nemôže potichu obísť nadradený forbidden invariant.

Conflict resolution je explicitný. Runtime policy engine reportuje applied bundles a decision provenance, aby audit vedel vysvetliť, prečo bola action povolená alebo odmietnutá.

## 12. Segregation of duties

Developer, evaluator, approver, deployer a auditor nemajú automaticky rovnaké práva. High-impact release nemá schváliť jediná osoba, ktorá vytvorila prompt, tool a evaluation dataset.

Segregation sa presadzuje workflowom a identity policy, nie iba procesným odporúčaním. Emergency exception je časovo obmedzená a po použití prejde independent reviewom.

## 13. Change classification

Zmeny sa klasifikujú podľa impactu: documentation-only, low-risk configuration, model/prompt change, tool/policy change, data/tenant change, autonomy expansion alebo emergency correction. Classification určuje evaly, approvers a rollout.

Agentické composed release znamená, že aj SDK default, provider alias alebo retrieval index change môže byť behavior change. Dependency updates sa preto nevylučujú z governance len preto, že application code diff je malý.

## 14. Pre-deployment evidence

Evidence package obsahuje release manifest, threat model, eval report, trajectory a forbidden-event results, cost/latency analysis, tenant isolation tests, rollback a kill-switch drill, privacy/security review a known limitations.

Evidence musí byť reprodukovateľná a viazaná na exact generations. Screenshot dashboardu alebo aggregate score bez dataset, grader a environment identity nestačí.

## 15. Go/no-go decision

Go/no-go record uvádza decision, scope, conditions, residual risks, approvers a expiry. Limited approval môže povoliť iba konkrétnych tenantov, read-only mode alebo časové okno.

No-go nie je failure governance procesu. Je očakávaný outcome, keď evidence alebo control nie je dostatočný.

## 16. Conditional approval

Conditional approval definuje measurable conditions, napríklad zákaz mutation, povinný human review, daily spend cap alebo restricted region. Runtime enforcement musí vedieť tieto conditions načítať ako policy.

Condition má ownera a expiry. Permanentná „temporary exception“ je governance defect.

## 17. Exception a waiver lifecycle

Exception record obsahuje violated control, business reason, scope, compensating controls, risk acceptance, owner, start, expiry a revocation criteria. Agent ani runtime nesmie vytvoriť exception iba preto, že policy blokuje desired action.

Po expiry sa access automaticky odoberie. Renewal vyžaduje nové evidence a nesmie iba kopírovať staré odôvodnenie.

## 18. Supplier a dependency governance

Model provider, tool vendor, MCP server, vector database, sandbox provider a observability backend sú suppliers alebo dependencies s vlastným riskom. Inventory eviduje contract, data handling, region, security, availability, versioning a exit plan.

Vendor control-plane status alebo certification nenahrádza local integration testing. Organization zodpovedá za to, ako dependency zapojila do vlastného agentického workflowu.

## 19. Data governance

Data governance určuje source authority, lawful alebo approved purpose, classification, minimization, retention, residency, access, correction a deletion. Agent memory, traces, eval datasets a prompts patria do data inventory rovnako ako hlavná database.

Derived summary alebo embedding nie je automaticky anonymný. Governance sleduje lineage a možnosť rekonštrukcie alebo citlivého inference.

## 20. Human oversight

Human oversight potrebuje kompetenciu, authority, informácie, čas a účinný intervention control. Approval button bez evidence alebo bez možnosti stop/reverse nie je efektívny oversight.

EU AI Act pri relevantných high-risk systémoch vyžaduje primerané human oversight measures a schopnosť osôb porozumieť limits a podľa potreby zasiahnuť alebo zastaviť systém. Interný systém môže rovnaký princíp použiť aj mimo právne high-risk kategórie podľa vlastného risku.

## 21. Operational constraints

Critical constraints sú mimo modelovej kontroly: action allowlists, tenant isolation, budgets, max turns, credential scope, approval, idempotency a kill switches. Agent môže navrhnúť plán, ale nemôže tieto constraints prepísať textom.

Governance owner schvaľuje constraint policy a platform owner preukazuje loaded enforcement. Prompt „nikdy neurob X“ je doplnok, nie hard governance control.

## 22. Audit trail verzus trace

Trace slúži na observability a debugging a môže byť sampled, redacted alebo neúplný. Audit trail eviduje governance a sensitive action events s požadovanou completeness, integrity, retention a access policy.

Audit event môže odkazovať na trace a secure evidence, ale nespolieha sa naň ako na jediný record. Zlyhanie trace exportera nesmie odstrániť povinný mutation alebo approval audit.

## 23. Audit event schema

Audit event obsahuje stable event ID, timestamp, tenant, operation, actor chain, system/release, policy decision, action, resource, approval, outcome, previous event alebo ledger reference a evidence digests. Raw secret sa do eventu nevkladá.

Schema má version a compatibility policy. Consumer, ktorý nepozná critical nový field, nesmie ticho interpretovať event ako complete.

## 24. Audit integrity

Audit storage používa append-only alebo tamper-evident mechanisms primerané risku. Correction nevykoná overwrite; vytvorí nový event s reference na pôvodný záznam.

Integrity control nepreukazuje pravdivosť vstupu, ak runtime poslal nesprávny tenant alebo action. Preto sa audit event tvorí z trusted policy a execution layers a pravidelne sa porovnáva s downstream ledgers.

## 25. Time a ordering

Distributed clocks a async export môžu zmeniť wall-clock ordering. Event preto nesie sequence, causal parent, operation attempt a source timestamp, kde je to možné.

Audit reconstruction rozlišuje observed-at, occurred-at a recorded-at. Neskorý event sa nesmie zaradiť ako nový side effect bez zachovania pôvodného času a identity.

## 26. Retention

Retention sa riadi legal, contractual, security, privacy a operational potrebami. Dlhšie nie je vždy lepšie; raw prompts alebo tool outputs môžu zvyšovať exposure.

Policy rozlišuje audit metadata, secure evidence payload, trace a business record. Deletion alebo legal hold vytvára evidovaný lifecycle a nesmie rozbiť required referential integrity bez tombstone alebo justified redaction.

## 27. Audit access

Audit access je least privilege a purpose-bound. Developer nemusí vidieť raw customer evidence a tenant admin nemusí vidieť interné security detections alebo iných tenantov.

Každé export, search alebo cross-tenant query môže byť samo auditovanou sensitive operation. Break-glass viewer session má expiry a post-use review.

## 28. Monitoring a control effectiveness

Governance nekončí deploymentom. Sleduje drift, forbidden events, override use, exceptions, unresolved incidents, budget breaches, tenant isolation a human-review quality.

Control effectiveness sa testuje, nie iba počíta. Nulový počet kill-switch activations môže znamenať bezpečnú prevádzku alebo nepoužiteľný control.

## 29. Metrics pre governance

Metriky zahŕňajú inventory completeness, releases bez current approval, expired exceptions, eval coverage, audit completeness, incident closure, time-to-stop, stale dependencies a supplier review age. Metriky sa spájajú s outcome a risk, nie iba s počtom documents.

Goodhartov efekt je reálny: tím môže maximalizovať checklist completion bez zlepšenia safety. Periodický qualitative review a adversarial testing zostávajú potrebné.

## 30. Incident management

Incident process identifikuje affected systems, tenants, data, actions a governance controls. Zmrazí evidence, aktivuje scoped stop, pridelí decision authority a zaznamená notifications a corrective actions.

Root cause sa nesmie zúžiť na „model urobil chybu“, ak chýbalo approval, isolation, fallback compatibility alebo audit evidence. Governance RCA skúma aj incentives, ownership a change process.

## 31. Notification a reporting

Regulatory, contractual alebo customer notification závisí od konkrétneho incidentu a jurisdiction. Governance runbook uvádza legal/privacy/security contacts a decision criteria, ale technický tím nevydáva právny záver bez authority.

Notification record obsahuje facts, uncertainties, affected scope a timestamps. Neskoršie corrections sa evidujú bez prepisu histórie.

## 32. Corrective a preventive actions

Corrective action obnovuje konkrétny control alebo outcome. Preventive action mení system, process, test alebo ownership, aby sa podobná failure class neopakovala.

Každá action má ownera, deadline, evidence a verification. Closing ticket bez second-operation testu nie je complete recovery.

## 33. Periodic review

Review sa spúšťa časovo aj event-driven: významný release, nový tool, nový tenant tier, zmena law/applicability, incident, provider change alebo drift. Review aktualizuje intended use, risk, controls a retirement plan.

Dormant system sa tiež kontroluje. Nepoužívaný agent s aktívnymi credentials a tools je latentný risk.

## 34. Retirement

Retirement zastaví nové runs, revokuje credentials, archivuje alebo vymaže state podľa retention, odstráni tools/routes a zachová required audit evidence. UI removal nestačí.

Dependent workflows a tenants dostanú migration alebo fallback plan. Re-activation vyžaduje nový governance decision, nie iba zapnutie starého deploymentu.

## 35. Independent audit

Independent auditor alebo control function potrebuje prístup k evidence bez závislosti na autorovi systému. Independence je primeraná impactu a môže byť interná alebo externá.

Audit sample zahŕňa positive, denied, fallback, kill-switch, exception a incident cases. Kontrola iba úspešných runov systematicky vynecháva najdôležitejšie boundaries.

## 36. Auditability by design

Auditability sa navrhuje spolu s identity, policy a side effects. Ak external tool nemá stable operation ID alebo read-back, neskorší audit nedokáže spoľahlivo určiť outcome.

Pridávať logging po incidente často nestačí, pretože chýbajúce historical facts sa nedajú rekonštruovať. Governance preto definuje minimum evidence pred production approvalom.

## 37. Incident `AGENT-GOV-06`

Change ticket označil release ako prompt update, hoci menil model route, retrieval depth, pooled tenancy a fallback tool. Aggregate eval score sa zlepšil, ale risk slices a tenant isolation test neboli spustené.

Shared cache exception nemala expiry a audit trace neobsahoval loaded policy, budget reservation ani kill-switch propagation. Po incidente boli owners nejasní: platform tím mohol stop aktivovať, ale iba product owner vedel schváliť re-enable a táto závislosť nebola v runbooku.

## 38. Konkurenčné hypotézy

Prvá hypotéza je individuálna developer chyba pri change classification. Druhá je neúplný composed-release inventory. Tretia je incentive optimalizovať answer score a ignorovať forbidden boundaries, štvrtá nejasná ownership matrix a piata neúčinný exception review.

Evidence zahŕňa release diff, dependency manifests, approval records, eval configuration, exception ledger, RACI alebo decision matrix, audit schema a incident timeline. Jeden chýbajúci podpis nevysvetlí systemic failure.

## 39. Containment

Containment suspenduje release a všetky active exceptions, ktoré sa viažu na shared cache a fallback route. Governance control plane nastaví no-new-mutations a evidence hold, zatiaľ čo read-only customer support pokračuje podľa safe pathu.

Decision authority a incident commander sa explicitne určia. Re-enable request sa nevytvorí, kým affected scope, unknown outcomes a required corrective controls nie sú známe.

## 40. Recovery

Recovery zavedie composed-release change classification, expiry pre exceptions, risk-sliced eval gate, tenant isolation tests, kill-switch drill a complete audit event schema. Ownership matrix pokrýva activation, containment, notification, approval a re-enable.

Historical incident records sa neprepisujú; doplnia sa correction events a secure evidence links. Periodický review overí, či podobné latentné exceptions existujú v iných agent systems.

## 41. Positive acceptance

Nový release má complete inventory, risk assessment, exact evidence package a schválený limited rollout. Runtime reportuje loaded policy, release, tenant isolation a audit generations.

Representative operation vytvorí complete trace aj audit events, business outcome a no-forbidden evidence. Approver dokáže vysvetliť scope a residual risk bez spoliehania sa na autora systému.

## 42. Forbidden acceptance

Release neprejde iba na základe aggregate quality score, provider assurance alebo successful happy-path demo. Chýbajúci tenant isolation, kill-switch, audit completeness alebo expiry je hard governance failure pre relevantný scope.

Neprípustné je spätne meniť approval alebo exception record bez correction eventu. Audit history musí ukázať pôvodné rozhodnutie aj jeho opravu.

## 43. Recovery acceptance

Drill aktivuje policy denial, expired exception, audit exporter outage a scoped kill switch. Povinné audit events zostanú dostupné, nové sensitive actions sa zastavia a recovery authority je jednoznačná.

Re-enable sa odmietne pri unresolved side effect, stale worker alebo neúplnom evidence package. Corrective actions majú independent verification.

## 44. Second-operation acceptance

Druhý tenant a odlišný workflow prejdú rovnakým governance lifecycle bez kopírovania approvalu alebo exception z prvého use case. Risk tier a evidence sa prispôsobia konkrétnemu contextu.

Test tiež overí, že retired alebo suspended release nemožno spustiť cez starý API route, queue message alebo cached configuration. Governance desired state je načítaný vo všetkých execution paths.

## 45. Praktický governance record

Governance record prepája intended use, release, risk, evidence, decision a conditions. Je machine-readable pre policy a zároveň čitateľný pre approvera a auditora.

Príklad nie je compliance certificate ani právne posúdenie. Applicability, evidence quality a loaded enforcement sa musia overiť samostatne.

```yaml
governance_decision:
  decision_id: gov-2026-0817
  system_id: agent-system/support-remediation
  release_digest: sha256:71fa...
  intended_use_version: intended-use/v5
  internal_risk_tier: high-impact
  legal_applicability:
    owner: legal-ai-governance
    assessment_ref: assessment://ai/2026/118
    conclusion: context-specific-review-completed
  evidence:
    eval_report: eval://support-remediation/5.10.0
    threat_model: threat://agent-system/support/v8
    isolation_test: test://tenant-isolation/run-441
    kill_switch_drill: drill://reliability/2026-08-04
  decision: limited-approval
  conditions:
    tenants: [tenant_acme, tenant_north]
    actions: [diagnostics.read, remediation.propose]
    mutations_require_human: true
    expires_at: 2026-09-04T00:00:00Z
  approvers: [product-owner, security-control-owner, operations-owner]
```

## 46. Praktický audit event

Audit event vzniká z trusted execution a policy layers a používa references namiesto raw sensitive payloadu. Obsahuje enough identity a causal data na prepojenie s trace, approval a external ledgerom.

Príklad preukazuje schema intent, nie tamper resistance alebo completeness. Storage, signing, sequence, retention a access controls potrebujú vlastné runtime testy.

```json
{
  "schema_version": "agent-audit/v4",
  "event_id": "evt_01K1GOV82X",
  "occurred_at": "2026-08-04T18:44:12.441Z",
  "tenant_id": "tenant_acme",
  "operation_id": "op_support_771",
  "run_id": "run_8831",
  "actor_chain": {
    "human_subject": "user:ops-219",
    "agent_workload": "spiffe://prod/agent/support-remediation",
    "tool_executor": "spiffe://prod/tool/kubernetes-rollout"
  },
  "release_digest": "sha256:71fa...",
  "policy_digest": "sha256:90bc...",
  "action": "rollout.restart",
  "resource": "k8s://prod-eu/payments/deployment/checkout",
  "approval_digest": "sha256:118e...",
  "decision": "allowed",
  "execution_outcome": "committed",
  "external_operation_ref": "k8s-op://rollout/991",
  "trace_ref": "trace://01K1TRACE9",
  "evidence_digest": "sha256:3e12..."
}
```

## 47. Prevádzkové metriky

Sleduje sa percento inventarizovaných systems, approvals viazaných na exact release, expired exceptions, audit completeness, go/no-go lead time, unresolved corrective actions, break-glass use, kill-switch drill freshness a supplier review age. Metriky sa segmentujú podľa risk tieru a autonomy.

Kvantita reviews nie je cieľ sama o sebe. Dôležité je, či controls zachytili relevantné changes a znížili incident frequency alebo blast radius.

## 48. Primárne zdroje

- [NIST — Artificial Intelligence Risk Management Framework](https://airc.nist.gov/airmf-resources/airmf/)
- [NIST — AI RMF Playbook: Govern](https://airc.nist.gov/airmf-resources/playbook/govern/)
- [NIST — AI RMF Playbook: Measure](https://airc.nist.gov/airmf-resources/playbook/measure/)
- [NIST — AI RMF Playbook: Manage](https://airc.nist.gov/airmf-resources/playbook/manage/)
- [NIST — AI RMF Playbook: Audit Log](https://airc.nist.gov/airmf-resources/playbook/audit-log/)
- [EUR-Lex — Regulation (EU) 2024/1689, Artificial Intelligence Act](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689)

## 49. Zhrnutie

Agent governance vytvára accountable decision system cez celý lifecycle: inventory, intended use, risk, change, evidence, approval, runtime oversight, exceptions, incidents, audit a retirement. Audit nie je trace screenshot ani retrospective storytelling; potrebuje stable identities, complete required events, integrity, access a retention.

Bezpečná organizácia oddeľuje interný risk tier od právnej applicability, viaže decisions na composed release, presadzuje segregation of duties a expirujúce exceptions a pravidelne testuje control effectiveness. Governance je úspešná až vtedy, keď dokáže nielen ukázať policy, ale aj preukázať loaded enforcement, actual outcome a recovery pri druhom nezávislom operatione.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Multi-tenant isolation](multi-tenant-isolation.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
