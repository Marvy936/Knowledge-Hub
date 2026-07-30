# Self-service

Self-service je platform capability model, v ktorom oprávnený používateľ vyjadrí intent, dostane okamžitú a zrozumiteľnú validáciu a spustí bezpečne ohraničenú operáciu bez manuálneho vykonania rutinného kroku platformovým tímom. Neznamená unrestricted privilege ani odstránenie governance. Policy, ownership, quota, approval, execution identity a lifecycle sú zakódované v contracte a presadené na authoritative boundaries.

Portal button nie je self-service, ak za ním vznikne neštruktúrovaný ticket, hidden manual handoff alebo optimistic `Succeeded` pred usable outcome-om.

```text
authenticated eligible intent
→ exact request subject a capability version
→ policy, ownership, quota, capacity a dependency preflight
→ plan, approvals a reservations
→ durable idempotent operation
→ bounded child operations v authoritative systems
→ waiting, partial a unknown classification
→ effective resource graph a permissions
→ developer-functional a business verification
→ terminal outcome, repair alebo decommission
→ second identical request
```

## 1. Automation, delegation a self-service

Automation vykonáva kroky bez manuálneho opakovania. Delegation znamená, že platform identity vykonáva privileged action v mene requestera. Self-service pridáva discoverability, eligibility, user-facing contract, durable state, truthful status a usable outcome.

```text
automation
→ script vytvorí resource

delegation
→ scoped platform principal vykoná approved mutation

self-service
→ user vyberie capability, rozumie contractu,
  spustí autorizovanú operation a dostane lifecycle outcome
```

Risk-based approval môže byť legitímnou súčasťou self-service. Rozhodujúce je, že request má explicitný state, approval je viazaný na exact plan a po rozhodnutí flow pokračuje bez ručného prepisovania údajov do ticketu. Permanentná central queue bez operation SLO je ticket portal, nie skutočný self-service.

## 2. Exact request subject

Request musí reprezentovať semantic intent, nie jeden HTTP submit. Subject obsahuje requester principal a delegated organization context, accountable owner, capability a contract version, target service/resource identity, requested action a desired outcome, environment/region/tenant/data classification, dependencies, expected current state alebo base revision, priority/expiry a idempotency identity.

Príklad:

```text
create RegulatedService 4.1
for team payments-recovery
service settlement-repair-api
environments staging + production
EU regulated profile
expected no existing service identity
operation key op-8841
```

Dva clicks s rovnakým semantic subjectom majú vrátiť rovnakú operation. Rovnaký service name s iným ownerom alebo incompatible desired generation je conflict. Random request UUID bez väzby na resource intent nevie zabrániť duplicate repository alebo database.

## 3. Discoverability, eligibility a preflight

Pred requestom má interface vysvetliť supported job, target segment, outputs, constraints, timing, cost, support a alternatives. Eligibility sa počíta z current authoritative identity, ownership, environment a policy contextu. UI hide/show pravidlá sú iba experience; backend musí rovnakú authorization vykonať znovu.

Preflight odhaľuje deterministické blockers pred partial mutation: name conflicts, data residency, account/namespace ownership, quota, database/provider capacity, private-network prerequisites, workload identity permissions, secret contracts, Git/GitOps dependencies a destructive impacts. Validácia však nie je reservation. Systém má rozlišovať `checked now`, `reserved until` a `runtime dependent`.

Plan zobrazuje predicted resources, writers, cost, approvals, waiting dependencies, irreversible steps a verification oracle. Delete alebo migration plan musí ukázať dependents a retained data. Generic `policy denied` bez vysvetlenia field-u, authority a supported alternative vytvára friction a bypass.

## 4. Policy, approvals a execution identity

Authentication dokazuje principal, authorization action nad resource-om a policy posudzuje kontext. Low-risk bounded request môže prejsť automaticky. Medium-risk request môže vyžadovať accountable owner approval. High-risk alebo destructive transition môže vyžadovať separation of duties, change window a recovery evidence.

Approval je platný pre exact request digest, plan, policy version a expected base state. Zmena inputu, target generation alebo dependency ho invaliduje. Broad approval `team môže používať production` nesmie oprávniť arbitrary database, role alebo network mutations.

Platform execution identity má byť short-lived alebo per-operation, tenant- a resource-scoped a auditovateľná spolu s upstream requesterom. Portal backend s ambient cluster-admin alebo cloud-admin tokenom vytvára veľký blast radius a slabú attribution. User-controlled provider parameters sa nesmú slepo preposlať mimo typed schema a policy.

## 5. Durable operation a child identities

Asynchrónny platform flow môže trvať minúty až hodiny a prechádza Git, cloud, identity, DNS, Kubernetes a GitOps systems bez globálnej transaction. Synchronný HTTP request alebo Backstage task log preto nie je dostatočný authoritative state.

```text
Draft
→ Validating
→ Planned
→ WaitingApproval
→ Queued
→ Running
→ WaitingDependency
→ Verifying
→ Succeeded
```

Vedľajšie states sú `Rejected`, `Blocked`, `Partial`, `UnknownOutcome`, `Repairing`, `Compensating`, `ManualInterventionRequired`, `Failed` a `Cancelled`. Každý state potrebuje invariant, owner, deadline, wake-up trigger a evidence.

Operation ledger uchováva request fingerprint, capability/policy version, attempts a exact child identities: repository ID, environment PR, database request token, workload identity ID, Flux object a production canary. Portal projection sa obnovuje z ledgeru a target read-backu. Process restart nesmie stratiť resume point.

## 6. Idempotency a lost response

Idempotency sa rieši na logical operation a na každom downstream side effecte. Orchestrator atomic claimne semantic request alebo nájde existing equivalent operation. Child adapter použije provider request token, deterministic coordinate alebo read-back identity.

```text
create call odoslaný
→ response sa stratí
→ read back child resource podľa stable identity
→ exists and equivalent: record success
→ absent: safe retry
→ conflicting: stop a reconcile
```

Blind retry od začiatku môže vytvoriť druhý environment PR, database alebo IAM binding. Registry zapísaná až po side effecte má crash gap. Correctness preto vyžaduje stable IDs, provider idempotency, persisted attempt state a read-back. Same subject + different payload musí byť explicitný conflict, nie reuse starého výsledku.

## 7. Waiting, partial a unknown outcomes

Waiting nie je failure. Má reason, external owner, expected deadline, wake-up mechanism a user action. `WaitingCapacity` je pravdivý state, ak database provider nemá kapacitu; nesmie byť skrytý za portal `Succeeded`.

Partial outcome znamená, že niektoré child resources sú authoritative a iné chýbajú. Recovery môže retry forward, bounded compensate, preserve state pre manual repair alebo akceptovať explicitne partial contract. Compensation nie je delete-all. Repository už môže obsahovať commits a database data; každý delete potrebuje ownership proof a safety preconditions.

Unknown outcome vzniká pri strate response-u bez istoty, či mutation nastala. Pred retryom sa číta target. Structured manual intervention obsahuje operation ID, exact evidence, required authority a resume transition; nemá sa odpojiť do ticketu bez väzby na workflow.

## 8. Usable outcome a status contract

`202 Accepted`, pull request created, provider create accepted alebo Flux `Ready=True` sú intermediate states. Capability success sa definuje podľa contractu. Pre production-ready service môže zahŕňať complete repository/pipeline, usable environment, database a private network, correct workload identity, reconciled runtime, telemetry a production test journey.

```text
resource exists
→ integration works
→ owner má access
→ workload beží na expected generations
→ intended business canary prejde
→ Succeeded
```

Portal má ukázať current operation, child resources, blocker a next action. Cached projection musí niesť freshness a source evidence. Status `Succeeded` sa nesmie odvodiť len z posledného lokálne úspešného API call-u.

Cancellation a delete sú tiež operations. `Cancelled` neznamená automaticky, že všetky side effects zmizli. Decommission potrebuje dependency inventory, retention, backup, traffic drain, identity/secret revoke, Git desired-state removal a orphan verification.

## 9. Capacity, fairness a abuse resistance

Self-service znižuje human queue, ale môže vytvoriť machine-scale demand. Admission používa tenant quotas, capability cost, provider capacity a priority reserves. Recovery a production incident operations nesmú súťažiť na rovnakej vyčerpanej queue s bulk preview environments.

Rate limit iba na portal HTTP requests nestačí. Jedna database operation stojí viac než catalog lookup. Backpressure má preniesť current downstream capacity do admission a waiting state-u. Retry guidance potrebuje backoff, jitter a stable operation identity, aby dependency outage nevytvoril storm a duplicate resources.

Security threat model zahŕňa compromised requester, parameter injection, cross-tenant coordinate, broad plugin token, SSRF, secret logging a stale approval. Self-service je bezpečný iba vtedy, keď delegated platform identity nemôže prekročiť approved subject.

## 10. Connected incident `GITOPS-PAY-63`

Atlas tvrdil, že `Regulated Service v4` je self-service, pretože developer spustil Backstage template. Request `LP-8841` pre `settlement-repair-api` bol označený `Succeeded` po `7 minútach`. V tom čase database ostávala `WaitingCapacity`, private endpoint nebol súčasťou pathu a workload identity nemala provider-reconciliation permission.

Workflow nemal durable end-to-end operation ani persisted child IDs. Retry vytvoril druhý environment PR. Tím následne otvoril tri manuálne tickety a fork-ol pipeline. Prvá production reconciliation prišla po `19 hodinách`; `8 412` settlements zostalo v manual queue a `73` prekročilo interný 24-hodinový resolution objective.

Zo `64` requests potrebovalo `28` manuálny ticket (`44 %`), hoci portal vykazoval `61` successful tasks (`95 %`). Root cause bol user-initiated task bez complete preflight-u, durable state, waiting/unknown semantics, semantic idempotency a usable-outcome verification. Portal nahradil manual front door, nie celý manual system.

## 11. Authoritative redesign a acceptance paths

`Regulated Service 4.1` vytvára operation `op-8841`, ktorá pred mutation kontroluje database capacity, private network a workload permissions. Child requests používajú stable IDs. Waiting state ukazuje blocker a ownera. Repository alebo PR success neuzatvára operation; platforma čaká na Flux runtime generations a production canary.

Positive path dokončí full capability graph. Waiting path ostane truthful bez duplicate retries. Lost-response path read-backne child resource. Recovery path resume-ne po controller restarte. Cancel/decommission path overí retained state a orphans. Forbidden path odmietne hidden ticket, broad admin delegation, stale approval, second PR pre same operation, false success, blind compensation a cross-tenant action.

## 12. Troubleshooting a anti-patterny

Troubleshooting začína request subjectom a operation ID. Potom kontroluje capability/policy generation, preflight evidence, reservations, state transitions, attempts, child identities, target read-back, Git commits, controller revisions, integrations, runtime/business oracle a portal freshness. Prvá neuzavretá boundary určuje resume alebo repair.

Anti-patterny sú: `button = self-service`, `202 = success`, `approval cez voľný ticket`, `retry od začiatku`, `waiting je failed alebo hidden`, `platform admin token uľahčí všetko`, `compensation vymaže všetko` a `create je celý lifecycle`.

## Glossary impact

Relevantné pojmy: self-service subject, capability eligibility, preflight, reservation, delegated execution identity, durable self-service operation, child operation identity, waiting dependency, partial outcome, unknown outcome, semantic retry, usable-outcome verification a self-service acceptance verdict.

## Primárne zdroje

- [CNCF Platforms White Paper](https://tag-app-delivery.cncf.io/whitepapers/platforms/)
- [CNCF Platform Engineering Maturity Model](https://tag-app-delivery.cncf.io/whitepapers/platform-eng-maturity-model/)
- [Backstage — Software Templates](https://backstage.io/docs/features/software-templates/)
- [Backstage — Authorizing scaffolder tasks and actions](https://backstage.io/docs/features/software-templates/authorizing-scaffolder-template-details/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Golden paths a paved road](golden-paths-and-paved-road.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Developer experience →](developer-experience.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
