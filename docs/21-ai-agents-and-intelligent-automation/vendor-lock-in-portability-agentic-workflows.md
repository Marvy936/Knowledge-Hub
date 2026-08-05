# Vendor lock-in a portability agentických workflowov

Portability nie je schopnosť exportovať diagram alebo prepísať niekoľko API calls. Agentický workflow spája model semantics, prompts, tools, identity, memory, checkpointing, approval, events, observability a execution guarantees. Lock-in vzniká vtedy, keď tieto contracts nie sú explicitné alebo keď business state existuje iba vo vendor-specific runtime formáte.

Incident `AGENT-GOV-13` odhalil, že approval ID, waiting state, tool registry, policy references a conversation memory boli uložené iba v proprietárnom execution store. Pri pokuse presunúť workflow do iného runtime-u sa podarilo importovať graph, ale nie pending approvals, idempotency keys ani exact tool schemas. Migration test preto vytvoril nový execution a takmer zopakoval produkčný side effect.

Nosný lifecycle portability je:

```text
business capability a invariants
→ portable domain contract
→ vendor-specific adapter boundaries
→ model, tool, event a state schemas
→ exportable execution a audit records
→ conformance tests
→ dual-run alebo shadow migration
→ checkpoint a pending-work transfer
→ effective outcome comparison
→ cutover, rollback a vendor-exit proof
```

## 1. Lock-in layers

Lock-in môže byť commercial, API, data, execution, operational, identity alebo skills-based. Každá vrstva má inú cenu migrácie.

Jedna open-source component neznamená portable system. Hosted control plane, proprietary checkpoints alebo closed model behavior môžu zostať kritickou dependency.

## 2. Business contract

Portable core začína business operation, invariants a outcome schema. Napríklad `approve_release`, `capture_payment` alebo `resolve_incident` má stable command, result a error semantics.

Vendor task names alebo UI node IDs nesmú byť domain contractom. Adapter ich mapuje na interné primitives.

## 3. State ownership

Business state patrí authoritative domain store-u, nie agent chat history. Workflow runtime drží orchestration state, memory store drží context a audit store drží evidence.

Ak jediná kópia approval alebo operation key existuje vo vendor checkpoint-e, exit path je neúplný. State inventory určí ownera a export format.

## 4. Workflow definition

Graph alebo YAML export môže zachovať topology, ale nie vždy runtime semantics, retries, concurrency, compensation a hidden defaults. Portability assessment porovná behavior, nie syntax.

Definition má versioned canonical model a vendor renderers. Round-trip import/export test odhaľuje stratené fields.

## 5. Tool contracts

Tool je portable iba vtedy, keď má stable operation ID, input/output schema, auth scope, idempotency, error taxonomy a side-effect classification. Prompt description nestačí.

Vendor tool node sa obalí adapterom. Agent vidí domain tool, zatiaľ čo adapter rieši konkrétny API provider.

## 6. OpenAPI a JSON Schema

OpenAPI a JSON Schema môžu štandardizovať HTTP operations a payloads. Neštandardizujú automaticky business authorization, retry safety ani provider consistency.

Schema sa pinne na generation a conformance tests. `additionalProperties`, null a enum evolution sa riadia explicitne.

## 7. MCP

Model Context Protocol štandardizuje session lifecycle a primitives ako tools, resources a prompts. Aktuálny current protocol baseline je `2025-11-25` a version sa negotiuje pri initialization.

MCP znižuje integration lock-in, ale negarantuje rovnaké tool semantics, authorization alebo data residency. Server implementation a schema generation zostávajú súčasťou trust boundary.

## 8. MCP capability negotiation

Client a server musia dohodnúť jednu protocol version a capabilities. Unsupported version má session ukončiť kontrolovane.

Portable workflow ukladá negotiated version a capability snapshot. Názov rovnakého toolu na dvoch servers nemusí znamenať rovnaký effect.

## 9. Experimental features

MCP Tasks boli v `2025-11-25` uvedené ako experimental. Experimental primitive sa nesmie stať jedinou storage authority pre critical pending work bez exit adaptera.

Portability matrix označí current, final, draft a experimental dependencies. Upgrade alebo downgrade je testovaný.

## 10. Events

CloudEvents poskytuje spoločný envelope pre event identity, source, type, time a data. Pomáha oddeliť business event od konkrétneho broker SDK.

Event portability stále vyžaduje ordering, deduplication, delivery a schema-evolution contract. CloudEvents envelope nerieši presne-once business outcome.

## 11. Observability

OpenTelemetry znižuje lock-in traces, metrics a logs cez portable semantic model a exporters. Vendor-specific dashboards však môžu obsahovať hidden queries a alert semantics.

Migration exportuje raw telemetry a versioned dashboards-as-code. Acceptance porovná incident-detection behavior, nie len počet spans.

## 12. Artifact portability

OCI images a immutable digests oddeľujú workload artifact od konkrétneho registry UI. SBOM, provenance a signatures sa prenášajú spolu s artifactom.

Portable runtime musí vedieť overiť rovnakú trust policy. Copy image bez signature policy nie je equivalent deployment.

## 13. Model abstraction

Jednotné `generate()` API nezaručuje rovnaký behavior. Providers sa líšia v tool calling, structured output, tokenization, safety filters, context limits a error semantics.

Model adapter uchová capability profile. Evals sa spúšťajú na každej approved model generation a provider fallbacku.

## 14. Prompt portability

System prompt môže obsahovať vendor-specific role syntax, tool conventions alebo hidden product features. Canonical prompt source sa oddeľuje od provider renderer-u.

Rendered prompt digest a model profile sú evidence. Migration test hodnotí trajectories a outcomes, nie string equality.

## 15. Structured outputs

Portable output používa explicitnú schema a deterministic validation. Provider-native structured mode sa mapuje na canonical object.

Fallback parser nesmie silently accept invalid shape. Unknown field alebo missing enum vytvára typed error.

## 16. Memory portability

Conversation messages, summaries, embeddings a long-term facts majú odlišné formats a retention. Export musí zachovať tenant, timestamps, provenance a deletion status.

Provider-specific vector IDs nie sú domain IDs. Reindex plan viaže raw document, chunk a embedding generation.

## 17. Checkpoints

Checkpoint obsahuje control position, state, pending tasks, retries, interrupts a versions. Proprietary serialization môže byť najväčší migration blocker.

Portable design definuje checkpoint export contract alebo safe restart boundary. Migration uprostred side effectu je zakázaná bez reconciliation.

## 18. Pending approvals

Waiting approval má subject hash, approvers, expiry a current decision state. Export iba „waiting“ nestačí.

Cutover buď prenesie celý approval envelope a identity semantics, alebo staré requests zruší a vytvorí nové. Obe actions sú auditované.

## 19. Idempotency

Stable operation IDs musia prežiť vendor migration. Nový runtime nesmie generovať nový key pre ten istý business command.

Cutover verifier porovná pending, acknowledged a confirmed operations. Unknown operations sa najprv reconciliujú.

## 20. Retry semantics

Runtimes sa líšia v tom, či retryujú task, node, step alebo celý execution. Side effects pred checkpointom sa môžu zopakovať.

Portable workflow explicitne definuje retry ownera a idempotency boundary. Vendor default sa nepovažuje za contract.

## 21. Error taxonomy

Provider errors sa mapujú na canonical categories: transient, permanent, unauthorized, invalid input, conflict a unknown outcome. Raw string matching je neportable.

Adapter zachová original error code a provider request ID. Agent dostane typed error bez straty evidence.

## 22. Identity

Vendor service account, OAuth app alebo delegate token sa mapuje na internal workload identity a policy. Migration nepresúva plaintext secrets.

Nový runtime dostane nové credentials s rovnakým alebo užším scope-om. Effective permissions sa overia negative tests.

## 23. Policy portability

Rego/OPA znižuje lock-in policy language a evaluator, ale platform-specific input shapes a policy-set events zostávajú adapters.

Canonical policy input sa stabilizuje pred OPA. Vendor binding tests overia On Save, On Run alebo equivalent lifecycle event.

## 24. Approval portability

Approval UI môže byť v Harness, n8n, ServiceNow alebo custom portal. Portable authority je approval envelope a identity decision, nie UI record ID.

Adapters musia zachovať quorum, self-approval restriction, expiry a revalidation. Lossy migration failuje closed.

## 25. Audit portability

Audit export používa stable event schema, subject IDs, actor, timestamps, result a parent correlations. Vendor audit trail ostáva supporting source.

External append-only store znižuje exit risk. Export sa pravidelne testuje obnovou a query nad historickým incidentom.

## 26. Licensing a hosting

Fair-code, open-source, source-available a proprietary licenses majú rozdielne exit možnosti. Self-hosting neznamená nulový lock-in, ak data model a operations sú špecifické.

Architecture decision record uvádza license, support horizon, hosted dependencies a cost of exit. Legal a technical portability sa hodnotia oddelene.

## 27. Custom nodes a plugins

Custom plugin zrýchli integráciu, ale zvyšuje runtime coupling. Critical business logic sa neukladá iba do vendor plugin SDK.

Plugin je adapter nad portable service alebo library. Contract tests bežia mimo vendor UI.

## 28. Data export

Každý state store má documented export, schema, encryption a restore procedure. Export bez importer testu je hypotetický.

Quarterly exit drill obnoví workflows, credentials references, approvals, memory, audit a pending operations do isolated targetu.

## 29. Conformance suite

Conformance suite spúšťa rovnaké inputs proti source a target runtime-u. Porovná decisions, tool arguments, state transitions, retries a business outcomes.

Stochastic agent output sa hodnotí invariantmi a trajectory toleranciou. Exact text equality nie je cieľ.

## 30. Shadow migration

Target runtime najprv beží read-only alebo shadow a nesmie vykonávať side effects. Produkuje proposals a decisions na porovnanie.

Divergence sa klasifikuje. Shadow success nepreukazuje mutation safety, preto nasleduje bounded canary.

## 31. Dual write

Dual write orchestration state je rizikové, pretože runtimes môžu súťažiť o execution authority. Preferuje sa single-writer a replicated evidence.

Ak dual run potrebuje porovnať side effects, jeden path používa sandbox alebo mock provider. Produkčný command má jedného executor-a.

## 32. Cutover

Cutover freeze-ne nové high-risk executions, vypočíta pending inventory, prenesie portable state a zmení event routing. Stable dedup keys zostávajú rovnaké.

Po cutover-e sa overí first operation, waiting approval, retry, cancellation a incident export. Starý runtime zostane read-only podľa retention planu.

## 33. Rollback migrácie

Migration rollback neznamená spustiť oba runtimes. Event router sa vráti na previous single writer a target pending work sa zruší alebo reconciliuje.

Operations executed počas canary sa nesmú zopakovať. Audit chain spája source a target execution IDs.

## 34. Positive acceptance

Canonical workflow sa spustí v dvoch runtimes nad rovnakým test corpusom. Oba použijú rovnaké operation IDs, tool schemas, policy decisions a approval envelope.

Outcomes a audit records sú equivalent v definovaných invariants. Export a restore pending approval prejde bez duplicate side effectu.

## 35. Forbidden acceptance

Migration stratí tenant scope, approval expiry, checkpoint generation alebo idempotency key. Target nesmie pokračovať s default values.

Vendor-specific status `success` nesmie byť automaticky mapovaný na canonical business success. Unknown sa quarantinuje.

## 36. Recovery acceptance

Po failed cutover-e sa event routing vráti na source runtime, target executions sa suspendujú a všetky possibly-executed operations sa reconciliujú.

Druhý drill migruje alternate workflow s memory, MCP tool a human approval. Exit evidence preukáže, že proces nie je závislý na ručnom vendor support zásahu.

## 37. Practical portability manifest

Portability manifest robí hidden dependencies viditeľnými. Viaže canonical contracts, vendor adapters, export status, experimental protocols a tested exit boundary.

Nasledujúci príklad nevyhlasuje workflow za portable iba preto, že používa MCP:

```yaml
workflow_portability:
  capability: production-release-approval
  canonical_contract: release-command-v3
  state_authorities:
    business: release-ledger
    orchestration: runtime-checkpoints
    approval: approval-ledger
    audit: external-event-store
  standards:
    tools:
      protocol: MCP
      version: "2025-11-25"
      experimental_features: []
    events: CloudEvents-1.0
    telemetry: OpenTelemetry
    artifacts: OCI-digest
  adapters:
    source_runtime: harness
    target_runtime: temporal
  exit_test:
    pending_approval_restored: true
    stable_operation_ids_preserved: true
    duplicate_side_effects: 0
    last_drill: 2026-08-05
```

Manifest je acceptance evidence iba spolu s reálnym export/import drillom. Deklarácia bez restore testu ostáva plánom.

## 38. Primary sources

MCP versioning a current baseline `2025-11-25` sú popísané na https://modelcontextprotocol.io/docs/learn/versioning; lifecycle a capability negotiation na https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle. Server primitives a ich ownership model opisuje https://modelcontextprotocol.io/specification/2025-11-25/server/index a experimental Tasks https://modelcontextprotocol.io/specification/2025-11-25/basic/utilities/tasks.

CloudEvents štandard a v1.0.2 release sú dostupné na https://cloudevents.io/. OPA policy testing a management interfaces sú na https://www.openpolicyagent.org/docs/policy-testing a https://www.openpolicyagent.org/docs/management-discovery. n8n source-control export behavior, vrátane rozdielu saved a published workflow version, dokumentuje https://docs.n8n.io/source-control-environments/create-environments/. Tieto standards znižujú konkrétne coupling vrstvy; žiadny z nich sám negarantuje portable business state, approval semantics ani side-effect safety.

## Zhrnutie

Portability vzniká explicitnými domain contracts, state ownershipom, stable operation IDs, exportovateľným auditom a pravidelne testovaným exit pathom. Open protocols ako MCP, CloudEvents, OpenTelemetry alebo OPA pomáhajú, ale vendor lock-in sa presúva do checkpointov, approvals, identity a hidden runtime defaults, ak sa tieto hranice nezdokumentujú.

Ďalšia kapitola vysvetlí, kedy má orchestration vlastniť workflow engine a kedy agent framework.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Human approval, audit a rollback](human-approval-audit-rollback.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Workflow engine oproti agent frameworku →](workflow-engine-vs-agent-framework.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
