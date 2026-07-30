# Internal Developer Platform

Internal Developer Platform (IDP) je vnútorný productized system capabilities, APIs, workflows, policies a operational ownershipu, ktorý umožňuje application tímom bezpečne vytvárať, meniť, prevádzkovať a ukončovať software bez ručného skladania celého cloud, Kubernetes, CI/CD, identity, secrets a observability toolchainu.

IDP nie je portal ani collection templates. Portal môže byť experience layer. Skutočná platforma prijme semantic request, autorizuje ho, vytvorí durable operation, orchestru-je viaceré authoritative systems, sleduje partial a unknown outcomes a označí capability za úspešnú až po funkčnom overení.

```text
developer capability need
→ discoverable versioned contract
→ authenticated a authorized request
→ durable idempotent platform operation
→ Git/IaC/cloud/identity/GitOps orchestration
→ authoritative resource graph
→ integration a runtime convergence
→ developer-functional a business verification
→ lifecycle, support a second request
```

Repository creation alebo zelený scaffolder task sú iba intermediate outcomes. Produkčná capability môže stále chýbať database, identity, network, secret, reconciled workload alebo business canary.

## 1. Platform engineering, IDP a portal

Platform engineering je disciplína navrhovania a prevádzkovania internal capabilities podľa potrieb používateľských tímov a business outcomes. IDP je výsledný capability system. Developer portal je rozhranie pre discovery, requests, status, documentation a aggregated views.

```text
portal
→ UI/API entrypoint a projection

IDP control plane
→ request model, policy, durable operations a orchestration

execution planes
→ Git, CI, IaC, cloud, identity, secrets, Kubernetes a GitOps

workload plane
→ reálne application a business outcomes
```

Backstage môže poskytovať Software Catalog, Software Templates, TechDocs a plugins, no neurčuje celý authority graph platformy. Scaffolder task môže vytvoriť repository alebo PR. To ešte nepreukazuje, že Flux reconcile-nul production, workload načítal credential a developer dokáže vykonať intended journey.

## 2. Capability contract

Platform capability je versionovaný záväzok medzi platform tímom a consumerom. Musí pomenovať inputs, outputs, guarantees, defaults, allowed choices, policy constraints, expected provisioning time, support, observability, upgrade a deletion lifecycle.

Príklad `Managed PostgreSQL` capability neznamená iba „vytvor database“. Contract môže obsahovať region, availability tier, storage/performance bounds, backup/PITR, data classification, workload identity a network requirements. Outputs musia mať stable database identity, endpoint/reference, secret binding, dashboardy, alerts, support/SLO a restore/decommission contract.

Abstraction má skryť incidental provider complexity, nie relevantné trade-offy. Developer musí vedieť, či výber vyššieho tieru mení cost, recovery, quota alebo approval. Policy enforced iba v UI nie je guardrail; rovnaký backend contract musí platiť pre portal, CLI aj automation clients.

## 3. Exact platform request subject

Request `vytvor production-ready service` je príliš neurčitý. Exact subject spája requester identity a authoritative team ownership, business/domain context, capability name a version, globally unique service identity, data classification, runtime/region/availability tier, repository/build profile, environments a promotion topology, network dependencies, stateful resources, workload identity a secrets, operational tier, cost center, expiry a policy generation.

Subject potrebuje aj semantic idempotency key a expected output inventory. Retry rovnakého requestu musí nájsť ten istý resource graph. Nový request s rovnakým service name, ale iným tenantom alebo incompatible capability version má byť conflict, nie silent reuse.

```text
(team, service identity, capability, version, environment topology)
→ operation op-8841
→ expected repositories, identities, environments, databases, catalog relations
```

User-supplied owner string nie je authorization. Platform backend musí read-backnuť authoritative membership a viazať downstream credentials na tenant a current operation subject.

## 4. Experience, control a execution planes

Experience plane zbiera inputs a zobrazuje projection. Control plane validuje schema, policy, quota a ownership, vytvára operation a riadi workflow. Execution adapters vykonávajú mutations v Git, cloud, CI, secret manageri a Kubernetes. Workload/runtime plane poskytuje final functional evidence.

Oddelenie bráni tomu, aby portal získal broad production token a priamo patchoval cluster. Portal má volať platform API alebo vytvoriť declarative request. Control plane následne používa scoped, short-lived identity pre konkrétny step a resource boundary.

Každý authoritative writer musí byť explicitný. Git je authority pre environment desired state, cloud provider pre resource state, identity provider pre principal/entitlement state, secret manager pre credential generation a runtime controllers pre observed status. Catalog a portal sú často projections; nesmú prepísať authority alebo predstierať freshness, ktorú neoverili.

## 5. Durable operation state

Provisioning trvá dlhšie než HTTP request a prechádza systems bez spoločnej transaction. API preto typicky vráti `202 Accepted` a operation ID. `Accepted` znamená, že request bol durable zaznamenaný, nie že capability existuje.

```text
RequestAccepted
→ Validating
→ Planning
→ Provisioning
→ WaitingForAuthoritativeChange
→ WaitingForReconciliation
→ Verifying
→ Succeeded
```

Failure states musia rozlišovať `Rejected`, `Blocked`, `Failed`, `PartiallySucceeded`, `UnknownOutcome`, `Compensating` a `ManualInterventionRequired`. Portal má zobrazovať current step, blocker, owner a actionable evidence. Green `Completed` po prvom GitHub API response-e je false-success contract.

Operation ledger uchováva semantic request fingerprint, policy version, attempts, downstream resource IDs, request tokens, last authoritative evidence a compensation eligibility. Po worker restarte sa workflow obnoví z ledgeru, nie z in-memory queue alebo portal logu.

## 6. Idempotency, retries a unknown outcomes

Každý downstream adapter potrebuje stable operation identity a read-back. Repository create môže používať deterministic name a provider request token; Git proposal má operation metadata; cloud resource má tags/owner; Kubernetes object stable name a tracking identity.

```text
call downstream create
→ response lost
→ read back by operation/resource identity
→ found: continue
→ absent: safe retry
→ conflicting: reconcile alebo stop
```

Blind retry od začiatku môže vytvoriť druhé repository, environment PR, database alebo IAM binding. Idempotency registry oddelená od authoritative resource creation tiež nestačí, ak process crashne medzi side effectom a registry write-om. Correctness vzniká cez provider idempotency, deterministic coordinates, durable step state a read-back.

## 7. Partial failure a compensation

Partial outcome je normálny: repository a catalog entity môžu existovať, zatiaľ čo database provisioning zlyhá. Platforma musí rozhodnúť medzi retry forward, bounded compensation, preservation pre manual repair alebo explicitným partial acceptance.

Compensation nie je `delete everything`. Repository už môže obsahovať user commits, database data alebo DNS traffic. Každý step potrebuje preconditions, ownership proof, data/traffic impact a irreversible boundary. Create-only platforma bez update, migration a safe decommission lifecycle-u produkuje orphan cost a attack surface.

Recovery flow začína inventory porovnaním:

```text
expected outputs op-8841
↔ actual Git/cloud/IAM/Kubernetes/catalog resources
→ classify complete, missing, duplicate, foreign alebo unknown
→ resume, repair, compensate alebo manual handoff
```

## 8. Verification vrstvy a platform SLO

Capability acceptance skladá viac oracles. Provisioning verification potvrdí provider resource. Integration verification potvrdí IAM, network, secret a GitOps relations. Developer-functional verification dokáže, že owner sa prihlási, pushne zmenu a použije capability. Operational verification potvrdí logs, metrics, alerts, backup a support. Business/application verification vykoná intended test journey.

```text
resource exists
≠ integrated
≠ accessible ownerovi
≠ operationally ready
≠ business usable
```

Platform SLO má merať valid request → usable capability, nie iba portal task duration. Potrebuje queue age, per-step latency/failures, partial a unknown operations, reconciliation lag, duplicate rate, manual intervention, time to first successful deploy, support toil, orphan resources a adoption/abandonment. Rýchly scaffold s trojdňovým time-to-production nie je rýchla platforma.

Backpressure a quotas chránia execution systems. Jeden tenant alebo bulk preview requesty nesmú vyčerpať cloud API, controller workers a recovery capacity pre production incident.

## 9. Security a multi-tenancy

IDP je privileged control plane. Threat model zahŕňa compromised developer account, malicious template inputs, broad plugin tokens, SSRF, secret logging, stale approval, duplicate retry a confused-deputy request. Platform identity môže vykonať viac než user; každý action preto musí zostať viazaný na autorizovaný operation subject.

Tenant identity musí prežiť requester session, operation, Git changes, cloud account/project, namespace, secret provider path, workload identity, logs a cost attribution. Portal filter `my services` nie je authorization. Backend a downstream provider policies musia odmietnuť cross-tenant coordinate aj pri syntakticky validnom requeste.

Custom actions a plugins potrebujú typed inputs, sandbox/egress controls, scoped tokens, secret-safe logging a pinned supply chain. `latest` custom-action image alebo mutable template dependency môže zmeniť effective workflow bez novej capability version a znehodnotiť audit aj retry semantics.

## 10. Connected incident `GITOPS-PAY-62`

LaunchPad mal vytvoriť repository, catalog entity, staging/production desired state, Flux a SOPS konfiguráciu, promotion a production verification. Skutočný workflow mal päť lokálnych outcomes:

```text
repository created
→ catalog projection created
→ LaunchPad priamo zapísal launchpad-runtime ConfigMap
→ promotion PR created/merged
→ portal task Completed
```

Direct ConfigMap write zmenil `postBuild.substituteFrom` input production Flux Kustomization a urobil z portalu hidden desired-state writera. Portal označil operation completed po GitHub API success, nie po Flux reconciliation a business canary. Nemal durable cross-system operation s downstream IDs; retry mohol vytvoriť druhý PR alebo zopakovať side effects.

Portal zobrazoval `pay910a / Ready`, ale actual graph bol:

```text
catalog request:    pay910a
promotion evidence: pay910a / route 1850
Flux render:        pay910b / route 1849
runtime:            pay910b / loaded pv-42
provider authority: pv-43
business canary:    failed alebo portalom nevykonaný
```

LaunchPad hlásil completion `17` minút pred potvrdením production failure. Root cause bolo zamenenie portal task completion za usable platform capability, chýbajúci durable operation subject a direct runtime writer mimo Git authority.

## 11. Authoritative redesign

Portal prijme request `op-8841` a zobrazuje projection. Durable platform controller validuje capability/version, rezervuje service identity, vytvorí declarative `PlatformService` alebo equivalent operation resource a orchestru-je Git proposals a provider requests s persisted IDs.

```text
LaunchPad request op-8841
→ durable PlatformService operation
→ scoped Git/cloud/identity/secret child operations
→ authoritative Git commits
→ Flux observed revisions
→ runtime artifact/config/secret endpoint
→ production canary
→ catalog projection refresh
→ op-8841 Succeeded
```

Critical desired state sa mení iba cez Git alebo explicitnú platform API authority. Portal nemá direct cluster write credential. Resume po worker/controller failure používa rovnaký operation ID. Status `Succeeded` vznikne až po developer-functional alebo business acceptance definovanej capability contractom.

## 12. Acceptance paths, troubleshooting a anti-patterny

Positive path vytvorí complete resource graph a usable capability. Retry path po lost response-e nájde existing outputs bez duplicates. Partial path ukáže truthful blocker a bezpečne resume-ne alebo compensate-ne. Recovery path po controller restarte obnoví ledger a dokončí same operation. Forbidden path odmietne hidden portal writer, cross-tenant action, mutable unversioned template, false success, blind retry a orphan resource.

Troubleshooting začína operation ID, requester/team/capability version, durable steps a attempts, downstream Git/cloud/IAM/Kubernetes IDs, desired commits, controller revisions, identity/secret/network integration, developer-functional test, business oracle a projection freshness. Po oprave sa opakuje identical request; musí vrátiť ten istý resource graph a truthful status.

Anti-patterny sú: „nainštalovali sme Backstage, máme IDP“, „template task success = production-ready“, „portal status je source of truth“, „retry spustí všetko od začiatku“, „self-service znamená broad privilege“ a „platforma je hotová, keď vie create“.

## Glossary impact

Relevantné pojmy: IDP capability contract, platform request subject, experience plane, platform control plane, execution adapter, durable platform operation, expected output inventory, semantic idempotency, partial capability outcome, developer-functional verification, portal projection, hidden platform writer, usable capability SLO a IDP acceptance verdict.

## Primárne zdroje

- [CNCF TAG App Delivery — Platforms White Paper](https://tag-app-delivery.cncf.io/whitepapers/platforms/)
- [CNCF — Platform Engineering Maturity Model](https://tag-app-delivery.cncf.io/whitepapers/platform-eng-maturity-model/)
- [Backstage — Software Catalog](https://backstage.io/docs/features/software-catalog/)
- [Backstage — Software Templates](https://backstage.io/docs/features/software-templates/)
- [Backstage — Authorizing scaffolder tasks and actions](https://backstage.io/docs/features/software-templates/authorizing-scaffolder-template-details/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: GitOps secrets](gitops-secrets.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Platform as a Product →](platform-as-a-product.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
