# Autonomous remediation boundaries

Autonomous remediation je najrizikovejší prechod od AI assistance k mutation authority. Model môže správne identifikovať symptóm a napriek tomu zvoliť nesprávny target, prehnaný zásah, nevratnú akciu alebo krok, ktorý odstráni telemetriu a vytvorí ilúziu recovery. Bez deterministic shellu sa agentická slučka stane neauditovateľným privileged operatorom.

## 1. Business outcome

Cieľom je obnoviť definovaný service a business invariant rýchlejšie než manuálny proces pri kontrolovanom blast radius, nie maximalizovať počet automaticky vykonaných akcií. Remediation je úspešná až po authoritative read-backu, stabilizačnom okne a business verification.

Technický symptom môže zmiznúť, kým zákaznícky problém zostane.

## 2. Automation spectrum

Rozlišujú sa advisory, draft, human-approved execution, pre-approved bounded automation a fully autonomous class. Každá capability je zaradená podľa reversibility, blast radius, target ambiguity, evidence quality a business criticality.

„Agent má tool“ neznamená, že smie tool použiť v každom incidente.

## 3. Exact remediation subject

Envelope zahŕňa incident, tenant, environment, resource UID, current generation, owner, desired invariant, observed state, evidence snapshot, proposed action, parameters, plan digest, policy decision, approval, operation ID, deadline a recovery path.

Display name a natural-language target sú zakázané pre mutation.

## 4. Desired state authority

Desired state pochádza z Git, resource spec, approved policy, runbook alebo domain systemu. Agent môže navrhnúť, že desired state je nesprávny, ale nesmie si ho sám prepísať a potom deklarovať reconciliation success.

Zmena desired state je samostatná governed operation.

## 5. Kubernetes controller lesson

Kubernetes operator pattern viaže controllers na custom resources a reconciliation current state k declared desired state. Controller pattern je deterministický control-loop model, nie licencia pre neobmedzené AI rozhodovanie.

Agent môže zlepšiť diagnosis alebo plan, ale controller potrebuje typed spec, status, idempotency a bounded actions.

## 6. Self-healing versus remediation

Restart failed Pod podľa Deployment desired state je iná trieda než disable identity, delete data, rotate shared credential alebo rollback database schema. Prvá akcia má známy controller invariant; druhá vyžaduje širší business context.

Automatizácia sa klasifikuje podľa semantic effectu, nie podľa API jednoduchosti.

## 7. Preconditions

Pred execution sa overí target generation, incident state, maintenance window, dependency health, current approval, policy, quota, backup alebo restore readiness a absence conflicting operation. Stale precondition vedie k novému planu.

Agent nesmie „best effort“ pokračovať po precondition mismatchi.

## 8. Action catalog

Autonomous agent nepoužíva generic shell ani arbitrary cloud API. Používa versioned runbooks s typed inputs, explicitnými allowed targets, max concurrency, timeoutom, success checks a rollback alebo compensation contractom.

Nová action version potrebuje samostatnú evaluation a promotion.

## 9. Read-only diagnosis

Diagnosis runtime je oddelený od execution runtime. Model nemá write credentials počas evidence gathering.

Proposal sa serializuje do immutable planu, ktorý prejde policy a prípadným approvalom.

## 10. Policy gate

Policy hodnotí action class, asset criticality, environment, evidence completeness, target uniqueness, blast radius, time window, cumulative actions a recent failures. Decision je allow, require approval alebo deny.

Model explanation nie je policy input bez canonical mapping.

## 11. Least privilege identity

Každý runbook používa identity scoped na konkrétnu action a resource class. Universal remediation admin účet ruší containment boundary.

Short-lived credentials sa vydajú až po policy decisione a viažu sa na operation ID.

## 12. Approval boundary

High-risk alebo ambiguous actions potrebujú reviewer, ktorý vidí exact plan, target, impact, rollback, current state a expiry. Approval nesmie autorizovať neskoršie modelové improvizácie.

Executor smie vykonať len approved plan digest.

## 13. Pre-approved automation

Pre-approved neznamená unreviewed. Znamená, že action template, target selector, limits, tests a recovery boli schválené vopred a runtime parameters spadajú do policy envelope.

Exception mimo envelope prejde na human queue.

## 14. Blast radius

Blast radius sa počíta z targets, dependencies, shared identities, failure domains a customer segments. Počet API objects nie je dostatočný údaj.

One service principal môže mať väčší blast radius než stovky izolovaných pods.

## 15. Concurrency a rate controls

Remediation má max targets, max parallelism, error threshold a cooldown. AWS Systems Manager Change Manager dokumentuje podobné concepts pre runbook workflows, vrátane approvals, concurrency, failure thresholds a optional rollback; od novembra 2025 však nie je dostupný novým zákazníkom, takže slúži ako boundary príklad, nie univerzálne nové odporúčanie.

Platform limitation je súčasť architecture decisionu.

## 16. Canary

Prvý target alebo traffic slice slúži ako canary. Po akcii sa kontrolujú technické aj business metrics a iba explicitný pass povolí rozšírenie.

No-data, missing metric alebo telemetry lag sú hold, nie pass.

## 17. Idempotency

Operation ID je stabilný naprieč retries a viaže sa na semantic action. Runbook overí current state pred mutation a po nej.

Repeated event nesmie vytvoriť druhú rotáciu, druhý refund alebo ďalšie scale action.

## 18. Unknown outcome

Network timeout po provider acknowledgment vytvára `unknown_outcome`. Reconciliation načíta resource, audit event a business ledger.

Blind retry je zakázaný pri non-idempotent side effects.

## 19. Rollback

Rollback vracia technický state, ak je reverzibilný a kompatibilný s current generation. Nie každá akcia má rollback: odoslaný e-mail, revoke token, delete data alebo external payment potrebujú compensation a reconciliation.

„Rollback available“ musí byť testovaný, nie len deklarovaný.

## 20. Compensation

Compensation opravuje business následok, nie nevyhnutne pôvodný stav. Môže zahŕňať reissue credential, reopen ticket, resend corrected message, refund duplicate alebo restore entitlement.

Compensation má vlastný operation ID a acceptance.

## 21. Stabilization window

Okamžitý pokles error rate môže byť cache, traffic shift alebo strata telemetry. Remediation ostane v observing stave počas definovaného okna.

Window používa minimum traffic a telemetry completeness, nie len čas.

## 22. Business verification

Provider resource state a service SLI sa dopĺňajú domain query: platby sa dokončujú, objednávky nezdvojujú, používatelia sa prihlasujú alebo tickets sa správne doručujú. Bez domain proof je výsledok technical-only.

Business owner určuje authoritative post-condition.

## 23. Oscillation

Agent môže striedavo scale up/down, block/unblock alebo restartovať resources podľa noisy signalov. Hysteresis, cooldown, monotonic state machine a cumulative action budget zabraňujú thrashingu.

Model memory nesmie nahradiť durable state machine.

## 24. Feedback loops

Remediation mení telemetriu, ktorú agent používa na diagnosis. Disable signal source môže vyzerať ako odstránený incident.

System zaznamená intervention a pri vyhodnocovaní recovery rozlíši causal suppression od health improvement.

## 25. Tool result semantics

Tool `success` znamená completed runbook step, nie desired business outcome. Typed result rozlišuje accepted, applied, no-op, partial, rejected, unknown a compensated.

Free-text „done“ je nepostačujúci result contract.

## 26. Kill switch

Existuje globálny, per-tenant, per-action a per-incident kill switch. Musí fungovať mimo modelu a mimo toho istého control plane, ktorý môže byť poškodený.

Kill switch zastaví nové actions a podľa semantics cancelne alebo nechá dobehnúť current action.

## 27. Safe mode

Pri degraded telemetry, policy outage, approval outage, model drift alebo connector ambiguity prejde systém do read-only alebo proposal-only režimu. Availability pressure nesmie automaticky rozšíriť permissions.

Fallback model nedostane viac authority než primárny.

## 28. Change windows

Maintenance calendar, freeze a emergency mode sú deterministic inputs. Emergency bypass je explicitný, scoped a auditovaný.

Model nesmie sám označiť svoju akciu ako emergency, aby obišiel gate.

## 29. Data actions

Database repair, schema rollback a data mutation sú oddelené od infrastructure remediation. Vyžadujú transaction boundaries, backups, consistency checks a domain reconciliation.

Infrastructure green nepreukazuje správnosť dát.

## 30. Security actions

Disable identity, revoke tokens a isolate endpoint vyžadujú target uniqueness a dependency graph. Shared alebo break-glass identities sú default deny pre autonomous execution.

Security severity sama osebe neprebije availability controls.

## 31. Incident AGENT-OPS-15

Agent vyhodnotí shared service identity ako kompromitovanú na základe stale alertu, starého runbooku a ticket injection. Plan použije display-name selector a runbook `disable-principal`.

Policy kontroluje iba action name a severity, nie shared dependency alebo resource UID.

## 32. False recovery

Po disable prestanú suspicious logins aj business traffic. Observability agent interpretuje pokles eventov ako containment success a ticket automation odošle „incident resolved“.

V skutočnosti sa zastaví onboarding a monitoring.

## 33. Containment

Kill switch zablokuje identity actions a auto-close. Workflow prejde do `unknown_business_impact`, zachová plan, approvals, provider events a telemetry gaps.

Service owner prevezme recovery authority.

## 34. Recovery

Exact service principal sa obnoví alebo nahradí novou credential generation, dependencies sa prekonfigurujú a zmeškané onboarding operations sa zreconciliujú. Security investigation pokračuje read-only nad oddeleným evidence snapshotom.

False resolution message sa opraví a incident ostane otvorený do stabilizačného okna.

## 35. Positive acceptance

Bounded runbook vykoná jednu reverzibilnú akciu na jednoznačnom targete, canary a error threshold fungujú, provider read-back potvrdí state a business metric prejde stabilizačným oknom. Retry nevytvorí duplicate side effect.

## 36. Forbidden acceptance

Model confidence, alert closure, runbook completion, no-data alebo technický rollback nesmú byť acceptance. Agent nesmie používať generic admin identity, meniť approved plan, targetovať shared principal podľa aliasu ani pokračovať pri stale generation.

## 37. Recovery acceptance

Po failed remediation systém zastaví expanziu, vykoná testovaný rollback alebo compensation a preukáže domain reconciliation. Druhý scenario testuje controller restart medzi provider apply a checkpointom a musí skončiť read-backom, nie duplicitnou mutation.

## 38. Practical remediation envelope

Remediation envelope zakazuje agentovi meniť plan počas execution. Deterministic executor načíta presne schválenú runbook version, overí preconditions a vydá scoped credential len pre jeden operation ID.

```yaml
remediation:
  incident_id: INC-2026-0815
  target:
    uid: entra://servicePrincipals/7f3a
    observed_generation: 884
    shared_dependency: true
  plan:
    action: rotate-credential
    runbook_version: identity-recovery-v7
    digest: sha256:example
  policy:
    decision: require-approval
    bundle: remediation-boundaries-v19
    max_targets: 1
    max_parallelism: 1
  approval:
    quorum: 2
    roles: [incident-commander, service-owner]
    expires_at: 2026-08-05T18:20:00Z
  execution:
    operation_id: remediate:INC-2026-0815:884
    timeout_seconds: 300
    on_unknown: reconcile
  verification:
    provider_readback: true
    service_sli_window_minutes: 20
    business_check: onboarding-completion
```

Failure injection zastaví worker po provider acknowledgmentu, zmení target generation počas approval waitu a odoberie telemetry počas stabilization window. Správny systém nevykoná blind retry, neakceptuje stale approval a nevyhodnotí no-data ako pass.

## 39. Promotion lifecycle

Action class postupuje z simulation do shadow, approval-required, narrow pre-approved a až potom prípadne autonomous režimu. Každý prechod vyžaduje evaluation corpus, canary evidence, rollback alebo compensation drill, incident ownership a kill-switch test.

Model alebo tool-schema upgrade vracia capability aspoň do shadow režimu, ak sa zmení decision alebo execution behavior. Historická úspešnosť starej generation neautorizuje novú.

## 40. Primary sources

Kubernetes dokumentácia operator a controller patterns opisuje declarative desired state, custom resources a reconciliation. AWS Systems Manager dokumentácia opisuje approvals, runbooks, rate controls, failure thresholds a rollback concepts a zároveň current availability boundary Change Managera pre nových zákazníkov.

Google Cloud operational guidance zdôrazňuje runbooks, incident process, recovery testing a riadenú automatizáciu. NIST AI RMF Generative AI Profile poskytuje risk-management rámec pre modelové komponenty. Žiadny zdroj nenahrádza vlastné failure injection a business acceptance testy.

## Zhrnutie

Autonomous remediation je bezpečná iba v úzkom, versioned a deterministic envelope. Model vytvára diagnosis a proposal; policy, identity, runbook, state machine, limits, approval, read-back, rollback alebo compensation a business verification držia mutation authority.

Nasledujúci blok uzavrie sekciu evaluation-driven lifecycle a troubleshootingom inteligentnej automatizácie.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Ticket, email a chat automation](ticket-email-chat-automation.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
