# Self-service

Self-service je platform capability model, v ktorom oprávnený používateľ môže sám vyjadriť intent, dostať okamžitú validáciu a spustiť bezpečne ohraničenú operáciu bez manuálneho vykonania rutinného kroku platformovým tímom. Neznamená to unrestricted privilege ani odstránenie governance. Znamená to, že policy, ownership, quota, approval a lifecycle sú zakódované v konzistentnom contracte a presadené na authoritative boundaries.

Portal button nie je dôkaz self-service. Používateľ môže vyplniť formulár, ale za ním stále vznikne ticket, nejasný waiting state alebo ručný zásah. Skutočný self-service poskytuje predvídateľnú operation identity, stav, outputs, diagnostiku, retry/recovery a overenie usable outcome-u.

## 1. Dominantný model

Dominantný model sleduje semantic request od user intentu cez authorization a planning až po effective capability. Každá transition musí byť pozorovateľná a opakovateľná bez duplicate side effects. Systém má používateľovi povedať nielen „request prijatý“, ale aj čo sa bude meniť, podľa akej policy, v akom stave operation je a aký dôkaz znamená dokončenie.

Self-service acceptance sa preto uzatvára až pri usable outcome-e alebo explicitnom terminal failure. HTTP `202 Accepted`, vytvorený pull request alebo provider `Create` response sú intermediate states. Platforma musí korelovať downstream controllers a external operations až po contract-specific readiness.

```text
authenticated user intent
→ exact request subject a capability version
→ eligibility, ownership, policy, quota a dependency preflight
→ plan, predicted outputs a required approvals
→ durable idempotent operation record
→ bounded orchestration cez authoritative systems
→ partial, waiting a unknown outcomes klasifikované
→ effective resources a permissions
→ developer-functional, operational a business verification
→ terminal success/failure/cancel state
→ change, retry, repair, delete a second-request closure
```

## 2. Self-service, automation a delegation

Automation vykonáva kroky bez manuálneho opakovania. Self-service pridáva user-facing contract, authorization, discoverability a outcome. Delegation znamená, že platforma vykonáva privileged actions v mene používateľa, ale iba v rámci prevereného intentu a policy.

Rozdiel:

```text
automation
→ script vytvorí resource

self-service
→ oprávnený používateľ požiada o capability
→ systém vysvetlí a overí contract
→ vykoná autorizovanú durable operáciu
→ používateľ dostane usable outcome a lifecycle

delegation
→ platform identity vykoná konkrétne privileged mutations
   viazané na requester, request a policy decision
```

Ručný approval môže byť súčasťou self-service, ak je risk-based, stav je transparentný a po approval-e pokračuje automatizovaný flow. Ak každý request končí neštruktúrovaným ticketom bez SLO a state modelu, ide o ticket interface, nie škálovateľný self-service.

## 3. Exact self-service request subject

Request musí identifikovať semantic intent, nie iba UI submission. Exact subject je základ idempotency, authorization, policy a read-backu. Dva clicks s rovnakým semantic intentom majú nájsť tú istú operation alebo bezpečne odmietnuť konflikt, nie vytvoriť duplicate resources.

Request subject zahŕňa:

- **Requester principal a delegated organization context** — identifikujú človeka alebo workload, jeho skupiny, tenant a dôvod, prečo smie request iniciovať.
- **Owning team a accountable service owner** — oddeľujú vykonávateľa requestu od dlhodobého vlastníka výslednej capability a support obligations.
- **Capability identity a contract version** — určujú input schema, outputs, policies, compatibility a lifecycle semantics, podľa ktorých sa operation vykoná.
- **Target resource alebo service identity** — poskytuje stable semantic key pre create, update, repair alebo delete a zabraňuje generated-name duplicates.
- **Requested action a desired outcome** — rozlišuje create, resize, rotate, promote, suspend alebo decommission a pomenúva, čo sa považuje za hotové.
- **Environment, region, tenant a data classification** — menia allowed destinations, identity, encryption, networking, audit a approval policy.
- **Dependency a compatibility context** — zahŕňa existing repositories, schema, provider account, network, quota a current generation, ktoré ovplyvňujú plán.
- **Expected current state alebo base revision** — umožňuje compare-and-swap a odmietne stale update, ktorý by prepísal novšiu zmenu.
- **Idempotency a correlation identity** — spája retries, downstream operation IDs, Git commits, cloud resources a audit evidence.
- **Requested timing, expiry a business priority** — ovplyvňujú queue, reservation, approval a cleanup, ale nesmú obísť safety bez explicitnej break-glass authority.

## 4. Discoverability a eligibility

Používateľ nemôže bezpečne použiť capability, ktorú nevie nájsť alebo ktorej scope nerozumie. Self-service interface má pred requestom vysvetliť job, supported segment, outputs, constraints, estimated timing, cost, support a alternatives.

Eligibility odpovedá, či je daný user, team, service a environment oprávnený capability použiť. Má byť vypočítaná pred mutation podľa current authoritative contextu. Príklady zahŕňajú data residency, ownership, account boundary, runtime type, quota alebo prerequisite identity.

Zlé rozhranie zobrazí všetkým rovnaký formulár a až po desiatich minútach vráti provider policy error. Dobré rozhranie buď nepodporovanú voľbu skryje s vysvetlením, alebo ju explicitne odmietne pri preflight-e a ponúkne alternative path alebo exception flow.

## 5. Preflight a plán

Preflight má odhaliť deterministické blockers pred vytvorením partial state-u. Číta current authority a zostavuje plán, ale nesmie predstierať, že všetky runtime conditions zostanú stabilné až do apply. Preto treba odlišovať validation od reservation alebo compare-and-swap precondition.

Preflight kontroluje:

- **Identity a authorization** — či requester smie konať za owning team a nad target environmentom.
- **Name a ownership conflicts** — či stable service, DNS, repository alebo catalog identity už neexistuje alebo nepatrí inému ownerovi.
- **Policy a classification** — či requested region, runtime, data a exposure kombinácia spĺňa current policy generation.
- **Quota a capacity** — či je dostupná alebo rezervovateľná required provider, cluster, network a platform capacity.
- **Dependencies a compatibility** — či existujú required network, schema, provider, GitOps a secret contracts.
- **Cost a blast radius** — či request neprekračuje budget, approval threshold alebo shared-risk limit.
- **Current-state freshness** — či observed state a expected base revision sú dostatočne nové pre bezpečný plán.

Plan má používateľovi ukázať predicted mutations, resources, costs, approvals, waiting dependencies a destructive effects. Pri delete alebo migration musí zobraziť dependents a retained data, nie iba názov hlavného resource-u.

## 6. Policy, approval a authorization

Self-service presúva vykonanie bližšie k používateľovi, ale decision authority zostáva explicitná. Authentication dokazuje principal, authorization overuje action nad resource-om a policy posudzuje kontext. Approval je dodatočný human alebo system decision pre risk, ktorý nemožno bezpečne automaticky povoliť.

Risk-based model môže vyzerať takto:

```text
low-risk bounded request
→ automatic policy decision
→ execute

medium-risk request
→ automatic checks + accountable owner approval
→ execute po freshness revalidation

high-risk alebo destructive request
→ separation of duties + change window + recovery evidence
→ execute s bounded credentialom
```

Approval musí byť viazaný na exact request digest, plan, policy version a expected base state. Ak sa inputs alebo target zmenia, starý approval sa invaliduje. Generic „platform access approved“ nesmie oprávniť arbitrary downstream action.

## 7. Delegated execution identity

Používateľ zvyčajne nedostáva direct cloud admin alebo cluster-admin credential. Platforma používa vlastnú execution identity alebo vydá short-lived scoped credential pre konkrétnu operáciu. Identity musí niesť correlation s requesterom a contractom v audit evidence.

Delegation boundary má:

- **Least-privilege permissions** — execution principal môže meniť iba resource types, tenant a environment potrebné pre capability.
- **Short lifetime alebo per-operation session** — credential sa po operácii expiruje a nemožno ho použiť ako general-purpose backdoor.
- **Policy-bound inputs** — platforma nesmie slepo preposlať user-controlled provider parameters mimo validated schema.
- **Audit linkage** — provider alebo target audit musí zachytiť platform principal aj upstream requester/operation identity tam, kde to mechanizmus umožňuje.
- **No ambient shared admin token** — dlhodobý broad secret v portal backend-e vytvára veľký blast radius a slabú attribution.
- **Revocation a containment** — kompromitovaný workflow alebo action možno zastaviť bez odstavenia všetkých platform capabilities.

## 8. Durable operation state machine

Self-service request často koordinuje minúty až hodiny trvajúce asynchrónne operácie. Synchronný HTTP request alebo Backstage task nie je dostatočný authoritative state. Potrebný je durable operation record, ktorý prežije process restart, timeout aj provider retry.

Príklad state machine:

```text
Draft
→ Validating
→ Rejected

Validating
→ Planned
→ WaitingApproval
→ Queued

Queued
→ Running
→ WaitingDependency
→ Partial
→ Unknown

Running/Waiting/Partial/Unknown
→ Repairing
→ Compensating
→ CancelRequested

→ Succeeded
→ Failed
→ Cancelled
```

Každý state má invariant a allowed transitions. `Succeeded` znamená verified capability outcome, nie iba odoslaný command. `Failed` má vysvetliť, ktoré mutations nastali a čo zostalo. `Unknown` vyžaduje read-back pred retry. `Cancelled` nemusí znamenať odstránenie všetkých side effects, kým compensation nie je potvrdená.

## 9. Idempotency a duplicate request

Idempotency chráni proti retry po timeout-e, dvojitému clicku a workflow restartu. Kľúč musí reprezentovať semantic operation, napríklad `create regulated-service atlas/settlement-repair in prod generation 4.1`, nie random HTTP request ID.

Mechanizmus:

```text
request subject + desired generation
→ atomic claim alebo operation lookup
→ existing equivalent operation?
   ├── yes: return current state/result
   ├── conflicting: reject or require update flow
   └── no: create durable operation and resource reservations
```

Downstream systems majú vlastné idempotency semantics. Git repository creation, cloud database create a external provider registration sa nemusia správať rovnako. Orchestrator preto ukladá stable downstream identities a pred retry vykoná read-back. Generated resource name bez semantic binding nie je bezpečná idempotency stratégia.

## 10. Partial a unknown outcome

Distributed self-service operation nemá globálnu ACID transakciu cez GitHub, cloud provider, Kubernetes, identity a secret manager. Failure môže nastať po každom side effecte. Platforma potrebuje saga-like recovery: retry forward, compensate, pause for intervention alebo accept partial contract s jasným statusom.

### Retry forward

Používa sa, keď dokončené kroky sú validné a missing step možno bezpečne opakovať. Napríklad repository a identity existujú, no database create zlyhal pred mutation pre quota.

### Compensation

Používa sa, keď partial outputs nemajú zostať. Compensation nie je vždy presný rollback; delete môže zlyhať, data môžu byť retained a external registration môže vyžadovať manuálne zrušenie.

### Unknown reconciliation

Pri strate response systém najprv číta authoritative target podľa stable identity a operation tokenu. Až potom klasifikuje not applied, applied alebo partial. Blind retry môže vytvoriť duplicate resource alebo side effect.

### Human-assisted recovery

Neautomatizovateľný case má vytvoriť structured intervention s exact evidence, required authority a resume pointom. Nemá sa premeniť na neštruktúrovaný ticket bez väzby na operation.

## 11. Waiting a external dependencies

Waiting nie je failure, ale musí mať reason, owner, deadline a wake-up mechanism. Capability môže čakať na approval, provider capacity, DNS propagation, certificate issuance, database restore alebo maintenance window.

Operation record má rozlišovať:

- **WaitingApproval** — konkrétny decision subject čaká na oprávneného approvera a po zmene inputs sa invaliduje.
- **WaitingCapacity** — required capacity nie je dostupná; systém drží alebo neuplatňuje reservation podľa explicitného contractu.
- **WaitingExternal** — provider operation beží a má stable external ID pre polling alebo event correlation.
- **WaitingUser** — používateľ musí doplniť alebo opraviť vstup; timeout a abandonment semantics sú definované.
- **WaitingWindow** — mutation je naplánovaná na change alebo maintenance window a plan sa pred execution revaliduje.

Neurčitý status `Pending` bez reasonu a ownera presúva diagnostiku na používateľa a znižuje dôveru.

## 12. Queue, capacity a backpressure

Self-service odstraňuje ticket bottleneck iba vtedy, ak control plane a downstream systems zvládnu demand. Unlimited concurrent provisioning môže vyčerpať cloud API rate limits, cluster admission, Git provider alebo shared database capacity a vytvoriť retry storm.

Admission model potrebuje:

- **Global platform budget** — chráni control plane a shared execution dependencies pred overloadom.
- **Capability a provider budgets** — oddeľujú pomalú database operáciu od rýchleho repository bootstrapu.
- **Tenant fairness** — jeden tím nesmie vyčerpať všetku queue alebo quota a blokovať ostatných.
- **Priority a reserved recovery capacity** — incident repair alebo security rotation môže mať vyhradený budget bez starvation bežných requestov.
- **Queue age a deadline awareness** — systém sleduje oldest request a môže odmietnuť nový demand skôr, než poruší sľub.
- **Bounded retries a jitter** — transient failure nevyvolá synchronized amplification.
- **Visible admission result** — používateľ dostane queued alebo rejected state s reasonom, nie false running status.

## 13. Usable outcome a verification layers

Resource existence nie je capability acceptance. Self-service musí overiť outcome podľa contractu a poskytnúť evidence links.

### Provisioning verification

Potvrdzuje, že authoritative outputs existujú s expected identities, configurations, permissions a ownershipom. Provider status `available` môže byť potrebný, no nie dostatočný.

### Integration verification

Overuje, že resources sú navzájom prepojené: workload identity získa secret, network dosiahne database, GitOps source sa reconcile-ne a telemetry sa prijíma.

### Developer-functional verification

Representative používateľ dokáže vykonať intended task, napríklad lokálne buildnúť service, deploynúť zmenu alebo pripojiť sa k database bez undocumented admin kroku.

### Operational verification

Runbook, alerts, backup, restore, ownership, SLO a support path sú účinné. Platforma nevytvorí production resource bez prevádzkového contractu.

### Business verification

Workload vykoná relevantný domain canary, napríklad settlement reconciliation, a potvrdí, že platform capability podporuje skutočný business outcome.

`Succeeded` state má explicitne uviesť, ktoré vrstvy boli overené a ktoré zostávajú zodpovednosťou application tímu.

## 14. Self-service change a delete

Mnohé platformy automatizujú create, ale update a delete nechajú na tickety. Skutočný self-service musí pokryť lifecycle, pretože risk často rastie pri zmene a odstránení.

Update potrebuje expected current generation, diff, compatibility a rollback. Delete potrebuje dependency graph, retention, backup, finalizer, external registrations a identity revocation. „Delete environment“ nesmie odstrániť database, ktorú používa iný service, ani nechať aktívny credential a DNS.

Destructive operation flow:

```text
delete intent
→ exact resource/dependency inventory
→ owner a data-retention decision
→ impact preview a required approvals
→ fence new writes alebo traffic
→ backup/export/reconciliation podľa contractu
→ ordered deletion a external revocation
→ residual scan
→ business a billing closure
```

## 15. Self-service a human support

Self-service neodstraňuje podporu. Mení ju z rutinného vykonávania na product assistance, exception handling a incident recovery. Support musí používať rovnakú operation identity a evidence ako používateľ, inak vzniká paralelný neauditovaný proces.

Support boundary začína tam, kde automatizovaný state machine nevie bezpečne rozhodnúť bez nového ľudského vstupu, exception authority alebo externého zásahu. Podpora preto najprv načíta authoritative operation, child-operation IDs, last confirmed state a recovery options; nevytvára nový ticket-only workflow, ktorý by stratil väzbu na pôvodný request. Ak napríklad databáza čaká na kapacitu, support nemá označiť request za hotový ani ju vytvoriť bokom pod inou identity. Má zaznamenať dependency, ownera, next observation time a povolený resume alebo cancel transition.

Tým sa support stáva súčasťou product feedback loopu. Opakovaná manuálna oprava je evidence chýbajúceho preflightu, slabého error modelu alebo absentnej capability, nie trvalý úspešný fallback. Support SLO preto sleduje čas k ďalšiemu dôveryhodnému rozhodnutiu a k usable outcome-u, nie iba čas prvej odpovede.

Dobrá podpora poskytuje:

- **In-context explanation** — status, next action a relevantná dokumentácia sú pri operation, nie v oddelenom knowledge base bez identity.
- **Escalation s evidence bundle** — ticket alebo chat obsahuje operation, resource, timeline, errors a attempted recovery bez secretov.
- **Resume alebo repair action** — support nepoužíva ad-hoc direct mutation, ale authorized platform mechanism s auditom.
- **Feedback classification** — opakované requests sa vracajú do product discovery alebo golden-path backlogu.
- **Support SLO a ownership** — waiting používateľ vie, kto rieši problém a kedy sa očakáva ďalší update.

## 16. Observability a self-service SLO

Self-service SLO sa má viazať na používateľský journey a capability class. Jednoduché repository create a multi-region database nemajú rovnakú latenciu ani failure semantics.

Required signals:

| Signal | Identita | Význam |
|---|---|---|
| Request rate a rejection | capability, version, tenant, reason | demand, eligibility a policy friction |
| Queue depth a age | capability/provider/priority | capacity a waiting risk |
| State transition latency | operation a step | kde sa request zdržiava |
| Partial/unknown count | operation type a dependency | distribučné failure a recovery backlog |
| Manual intervention | reason a team | skrytý ticket toil a chýbajúca automation |
| Outcome success | usable/production/business layer | skutočný completion contract |
| Retry a compensation | step a provider | idempotency a downstream reliability |
| Orphan/residual resources | operation a owner | cleanup a false terminal state |
| User abandonment a repeat use | cohort a capability | trust a product fit |
| Cost a quota consumption | tenant a resource | sustainability a capacity planning |

SLO môže napríklad merať „95 % eligible low-risk database requests dosiahne usable integration do 30 minút bez human intervention“. Portal API latency je supporting SLI, nie hlavný outcome.

## 17. Security a abuse model

Self-service interface je privileged automation surface. Threat model zahŕňa compromised user account, malicious inputs, confused deputy, privilege escalation, resource exhaustion, cross-tenant reference, secret exfiltration a destructive request.

Threat sa realizuje cez celý request-to-mutation chain, nie iba cez formulár. Principal môže byť legitímne autentizovaný, ale požiadať o cudzí namespace; schema-valid input môže vložiť nebezpečný IAM wildcard; delegated orchestrator môže ako confused deputy použiť broad credential nad nesprávnym tenantom; retry po unknown outcome môže zdvojiť drahý resource. Security decision preto viaže requester identity, owner, semantic request digest, approved plan, delegated principal, target inventory a observed outcome.

Controls sa skladajú sekvenčne. Authentication určí kto žiada, authorization a policy rozhodnú čo smie nad ktorým subjectom, semantic validation obmedzí význam vstupu, quota a admission chránia shared capacity a delegated execution vynucuje least privilege pri reálnej mutation. Read-back, audit a anomaly detection potom dokazujú, čo sa skutočne stalo. Vynechanie jednej boundary nemožno kompenzovať skrytím tlačidla v UI; API alebo orchestrator by stále zostali zneužiteľné.

Controls musia byť kompozitné:

- **Strong identity a recent authentication** — high-risk action môže vyžadovať step-up a nesmie dôverovať iba stale browser session.
- **Server-side authorization** — UI visibility nie je security boundary; API overuje principal, owner, action a target.
- **Schema a semantic validation** — input sa neposiela priamo do shellu, template pathu, IAM policy alebo provider API.
- **Policy a tenant scope** — references a outputs sú obmedzené na authorized resources a namespaces.
- **Quota a rate limits** — bránia cost alebo capacity abuse a musia byť fair a observable.
- **Separation of duties** — sensitive approval a execution nemá kontrolovať ten istý compromised principal bez independent evidence.
- **Secret-safe logs a outputs** — operation diagnostics nesmú publikovať credentials alebo sensitive provider payload.
- **Audit a anomaly detection** — correlation zachytáva requester, delegated principal, plan, mutations a outcome a umožňuje odhaliť neobvyklý pattern.
- **Kill switch a bounded suspension** — capability alebo tenant možno zastaviť bez straty operation state-u a bez neobmedzeného platform outage-u.

## 18. Connected incident `GITOPS-PAY-63`

LaunchPad `Regulated Service v4` bol označený ako self-service, pretože používateľ vyplnil Backstage formulár a nepotreboval platform engineer-a na vytvorenie repository. Scaffolder task však priamo vykonal niekoľko synchronous actions a pre dlhé operations iba otvoril pull requesty alebo provider requests.

Request `LP-8841` mal operation timeline:

```text
09:00:00 form submitted
09:00:03 authorization passed
09:00:09 repository created
09:00:31 catalog entity registered
09:01:10 environment PR opened
09:07:04 scaffolder task Succeeded
09:12:18 database request WaitingCapacity
09:18:42 workload identity applied without provider permission
12:46:09 private-network ticket created manually
18:21:33 database became available
next day 04:02 first end-to-end settlement reconciliation
```

Portal nemal durable operation, ktorá by korelovala states po skončení scaffolder tasku. Re-run vytvoril druhý environment PR a pokúsil sa registrovať duplicate catalog location. Database provider operation mala stable ID, ale nebolo uložené pri platform requeste; support musel hľadať podľa generated name a timestampu.

### Self-service root cause

Organizácia zamenila user-initiated automation za self-service capability. Request nemal complete preflight, durable state machine, downstream identity inventory, waiting semantics ani usable-outcome verification. Platform task uzavrel success pri vytvorení proposals, hoci rozhodujúce resources boli partial alebo waiting.

### Redesign

Nový flow používa platform operation `op-rsp-8841`:

```text
request + semantic idempotency key
→ preflight ownership/policy/quota/network/provider permissions
→ plan a predicted output inventory
→ durable operation Created
→ repository/catalog/Git changes
→ database a network child operations s stable IDs
→ WaitingCapacity alebo Running visible používateľovi
→ GitOps reconciliation a integration probes
→ first settlement-repair canary
→ Succeeded až po contract acceptance
```

Retry vracia current operation. Repair pokračuje od failed child step-u. Cancel vykoná ordered compensation a residual scan. Support používa rovnaký operation timeline a nemá direct silent mutation path.

## 19. Self-service acceptance verdict

Acceptance verdict musí preukázať autonómiu v bezpečnom contracte, nie absenciu človeka v prvom kroku. Používateľ má vedieť spustiť, sledovať, meniť a ukončiť capability a platforma musí zvládnuť partial a unknown outcomes bez duplicate alebo orphan effects.

Self-service design je prijatý, keď:

- **Capability je discoverable a eligibility zrozumiteľná** — používateľ pozná job, outputs, constraints, cost, timing a alternative paths ešte pred requestom.
- **Request subject je exact a durable** — principal, owner, capability version, target identity, desired action, base state a idempotency sú uložené.
- **Preflight odhaľuje deterministické blockers** — policy, ownership, quota, dependency a compatibility errors sa riešia pred partial mutation.
- **Plan a approval sú subject-bound** — používateľ a approver vidia exact mutations a zmena inputs alebo base state invaliduje staré rozhodnutie.
- **Delegated identity je least-privilege** — platforma nepoužíva ambient broad credential a provider audit koreluje upstream request.
- **Operation state machine je pravdivá** — waiting, partial, unknown, repair, compensation a cancellation majú explicitné semantics.
- **Retry je idempotentný a read-back based** — timeout alebo re-run nevytvorí duplicate resources ani external effects.
- **Capacity a backpressure sú bounded** — queue, fairness, quota, priority a recovery capacity chránia platformu aj downstream systems.
- **Success znamená usable outcome** — provisioning, integration, developer-functional, operational a required business verification sú explicitné.
- **Update a delete sú supported** — change, migration, revocation, retention a residual cleanup nie sú presunuté na ad-hoc tickety.
- **Support používa platform operation** — intervention, repair a escalation zachovávajú audit a authority graph.
- **Abuse a tenant tests prejdú** — unauthorized action, injection, cross-tenant reference, quota abuse, secret leak a destructive request sa odmietnu.
- **Second-request a controller-restart tests prejdú** — repeated create/update po failure alebo restarte obnoví správny state bez duplicates.

## 20. Troubleshooting flow

Self-service diagnosis začína exact operation subjectom a terminal contractom. Zelený UI status alebo jeden provider log nemôžu reprezentovať celý distributed outcome.

```text
Self-service request je stuck, false-success, duplicate alebo neúplný
→ capability version + requester/owner/tenant
→ semantic request a idempotency identity
→ expected base state, plan, policy a approval
→ durable operation a state-transition timeline
→ child operation IDs v Git/cloud/identity/runtime/provider systems
→ authoritative read-back a output inventory
→ waiting/partial/unknown classification
→ integration, usable a business verification
→ retry-forward, compensation, repair alebo cancellation
→ residual scan a second-request test
```

Ak operation hlási `Running` dlho, hypotézy zahŕňajú legitimate provider wait, lost event, controller failure, exhausted queue alebo unknown applied outcome. Polling iba portalu ich neodlíši; potrebný je child operation identity, provider status a orchestrator lease/heartbeat evidence.

## 21. Anti-patterny

### Self-service znamená dať developerom cluster-admin

Direct broad privilege presúva complexity a risk na používateľa a ruší platform policy boundary. Self-service deleguje bounded intent cez least-privilege mechanismus.

### Máme formulár, teda máme self-service

Formulár môže vytvoriť ticket alebo proposal. Bez durable operation, transparentných states, outcome a lifecycle ide iba o front-end pre manuálny proces.

### Approval po requeste vyrieši governance

Approval bez exact planu, freshness a policy contextu je rubber stamp. Governance musí byť zakódovaná pred, počas aj po execution a approval sa viaže na risk-bearing delta.

### Pri timeout-e používateľ klikne znova

Blind retry je nebezpečný pri external side effects. Systém musí vrátiť operation identity a pred retry vykonať authoritative read-back.

### Create je hlavná hodnota, delete môžeme riešiť neskôr

Resources, identities, data a cost prežijú dlhšie než create task. Chýbajúci update/delete lifecycle vytvára orphan state, bezpečnostné riziko a locked-in toil.

## 22. Kontrolné otázky

1. Čím sa self-service líši od automation a delegated execution?
2. Prečo HTTP `202 Accepted` alebo portal task success nie sú capability acceptance?
3. Ktoré rozmery tvoria exact self-service request subject?
4. Aký je rozdiel medzi preflight validation, reservation a compare-and-swap precondition?
5. Ako sa approval viaže na exact plan a prečo sa musí invalidovať?
6. Prečo platform execution identity nesmie byť ambient cluster-admin credential?
7. Ako durable state machine rozlišuje waiting, partial, unknown a failed?
8. Ako semantic idempotency zabraňuje duplicate resource po timeout-e?
9. Kedy použiť retry forward, compensation a human-assisted recovery?
10. Ako queue fairness a reserved recovery capacity chránia self-service?
11. Prečo `LP-8841` nebol skutočne self-service napriek 7-minútovému tasku?
12. Čo musí overiť self-service acceptance verdict?

## Glossary impact

Relevantné pojmy: self-service request subject, self-service eligibility, platform preflight, subject-bound plan, delegated execution identity, durable platform operation, platform waiting state, partial platform outcome, unknown platform outcome, semantic request idempotency, child operation identity, platform compensation, self-service backpressure, usable capability outcome, self-service acceptance verdict.

## Primárne zdroje

- [CNCF TAG App Delivery — Platforms White Paper](https://tag-app-delivery.cncf.io/whitepapers/platforms/)
- [CNCF TAG App Delivery — Platform Engineering Maturity Model](https://tag-app-delivery.cncf.io/wgs/platforms/maturity-model/readme/)
- [Backstage — Software Templates](https://backstage.io/docs/features/software-templates/)
- [Backstage — Authorizing Scaffolder Tasks, Parameters, Steps and Actions](https://backstage.io/docs/features/software-templates/authorizing-scaffolder-template-details/)
- [Backstage — Audit Events for Software Templates](https://backstage.io/docs/features/software-templates/audit-events/)
- [Backstage — Software Catalog](https://backstage.io/docs/features/software-catalog/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Golden paths a paved road](golden-paths-and-paved-road.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Developer experience →](developer-experience.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
