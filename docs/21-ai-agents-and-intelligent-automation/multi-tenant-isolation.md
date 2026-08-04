# Multi-tenant isolation

Multi-tenant agent platform zdieľa časť control plane, runtime, model gateway, tools, memory, retrieval alebo observability medzi viacerými zákazníkmi, organizáciami alebo bezpečnostnými doménami. Izolácia znamená, že jeden tenant nedokáže čítať, meniť, ovplyvniť ani neprimerane vyčerpať resources iného tenanta, a to ani cez agentický planning, cache, tool chain, traces alebo fallback path.

Táto kapitola pokračuje v incidente `AGENT-GOV-06`. Po aktivácii fallback route sa dva tenanty dostali do spoločného worker poolu. Request identity obsahovala tenant claim, ale shared retrieval cache používala iba normalizovaný query text, session memory store indexoval konverzácie podľa lokálneho `thread_id` a tool adapter pridal tenant filter až po model-generated arguments. Výsledkom nebol priamy database bypass; agent najprv dostal stale summary iného tenanta z cache, potom ho použil ako plánovací fakt a pripravil mutation proti resource, ktorú policy až neskoro odmietla. Súbežne heavy run jedného zákazníka vyčerpal queue a token reservations pre ostatných.

Nosný lifecycle je:

```text
verified tenant a user/workload identity
→ exact operation, data a resource subject
→ tenant-aware authorization a scoped credentials
→ isolated context, memory, retrieval, cache a tool execution
→ compute, queue, network a budget fairness
→ trace, audit, eval a support-access boundaries
→ cross-tenant negative tests a noisy-neighbor tests
→ containment, tenant-scoped kill switch a evidence freeze
→ recovery, residue cleanup a re-enable
→ second-tenant a second-operation acceptance
```

## 1. Tenant je security subject

Tenant nie je iba billing label alebo UI organization name. Je security subject, ku ktorému sa viažu users, workloads, data, policies, budgets, cryptographic keys, resources, retention a incident boundaries.

Každá operation musí mať exactly one authoritative tenant context alebo explicitný cross-tenant administrative purpose. Chýbajúci, ambiguous alebo conflicting tenant context je denial condition, nie dôvod použiť default tenant.

## 2. Tenant identity chain

Identity chain rozlišuje human subject, agent workload, runtime instance, run, tool caller a downstream service actor. Každá vrstva nesie tenant context alebo preukázateľnú delegated authority konať pre konkrétneho tenanta.

Tenant claim sa nepreberá z promptu ani tool arguments. Vzniká z verified identity a policy layer ho propaguje mimo modelového textu do storage, queue, tool a audit calls.

## 3. Authentication verzus isolation

Authentication dokazuje, kto volá. Isolation určuje, ku ktorým tenant resources môže caller pristúpiť a ako sa tento boundary presadí v každej zdieľanej vrstve.

Platný token bez tenant-aware authorization môže stále umožniť cross-tenant access. Rovnako tenant filter v aplikácii nepomôže, ak background worker alebo admin tool používa širší credential bez explicitného resource scope.

## 4. Exact tenant resource subject

Resource subject obsahuje tenant, environment, resource type, resource ID, generation a data classification. Samotný object ID môže byť globálne neunikátny alebo predvídateľný.

Authorization decision sa viaže na canonical subject pred tool dispatchom. Tool nesmie prijať model-generated tenant ID, ktoré prepíše verified runtime context.

```yaml
tenant_subject:
  tenant_id: tenant_acme
  environment: prod-eu
  resource_type: support_case
  resource_id: case_9182
  resource_generation: 44
  data_classification: confidential/customer
  operation_id: op_support_771
```

## 5. Pool, silo a bridge model

Pool model zdieľa väčšinu infrastructure a presadzuje logical isolation. Silo model dáva tenantovi dedicated stack alebo významnú časť resources a bridge model kombinuje pooled a dedicated vrstvy.

Žiadny model nie je automaticky bezpečný. Silo môže stále zdieľať identity, deployment, observability alebo support plane; pool môže byť bezpečný, ak má dôsledné identity, policy, data a runtime controls.

## 6. Isolation domain inventory

Architektúra inventarizuje všetky domains, kde sa tenant data alebo influence objaví: API, queues, sessions, memory, retrieval, vector stores, caches, model context, tools, sandboxes, files, credentials, traces, eval datasets, backups a human support consoles.

Neinventarizovaná shared vrstva je častý leak path. Agent platforma má viac transient state než bežná CRUD služba a práve transient caches alebo traces bývajú mimo hlavného data modelu.

## 7. Control plane a data plane

Control plane spravuje tenant onboarding, policy, routes, budgets, tools a configuration. Data plane vykonáva agent runs a pristupuje k tenantovým resources.

Control-plane record `tenant configured` nepreukazuje data-plane loaded state. Workers, gateways a tool adapters reportujú loaded tenant-policy generation a mismatch blokuje sensitive execution.

## 8. Tenant-aware admission

Admission overí tenant status, service tier, region, budget, concurrency, allowed workflow a current isolation posture. Run sa nevytvorí, ak tenant mapping alebo required policy nie je dostupná.

Admission zároveň rezervuje tenant-specific capacity. Bez reservations môžu stovky súbežných requests všetky prejsť proti rovnakému quota snapshotu a vytvoriť noisy-neighbor incident.

## 9. Scoped credentials

Credential broker vydáva krátkodobý credential viazaný na tenant, action, resource, audience, operation a expiry. Shared standing admin credential v tool adapteri ruší veľkú časť tenant isolation.

Credential sa nevkladá do model contextu. Agent dostáva opaque capability handle a policy layer ho premení na downstream credential až po canonical authorization.

## 10. Database isolation

Databáza môže používať dedicated instance/schema, partition key, row-level security alebo kombináciu. Aplikačný `WHERE tenant_id = ?` je užitočný, ale nemá byť jedinou hranicou pre high-impact data.

Tenant key je súčasť primary alebo access path tam, kde to dáva zmysel, a database policy sa testuje independent od agent layeru. Administrative queries majú explicitný cross-tenant purpose a oddelenú identity.

## 11. Vector store a retrieval isolation

Vector search filter nie je dostatočný, ak embeddings, metadata alebo candidate cache vznikli bez tenant boundary. Cross-tenant candidate sa môže dostať do rerankera alebo trace aj vtedy, keď sa neskôr odstráni z finálneho contextu.

Index namespace, encryption, metadata policy a query credential sa viažu na tenant. Retrieval pipeline loguje candidate lineage a negative test overuje, že iný tenant sa neobjaví ani v intermediate evidence.

## 12. Memory isolation

Short-term session state, long-term memory a learned preferences používajú tenant-aware composite identity. Lokálny `thread_id`, email alebo user-provided name nie je globálne bezpečný key.

Memory write policy overí tenant, provenance, retention a allowed reuse scope. Summary vytvorená z mixed alebo untrusted state sa nesmie uložiť ako autoritatívna memory pre ďalšie runy.

## 13. Cache isolation

Cache key zahŕňa tenant, authorization scope, data classification, relevant generations a freshness. Query text alebo tool name samotné nestačia.

Shared cache storage môže zostať pooled, ale lookup a encryption boundary musia zabrániť cross-tenant hitu. Negative acceptance test používa rovnaký query text, rovnaký user-local ID a odlišný tenant.

## 14. Prompt a context isolation

System instructions, tenant policy, retrieved data a conversation history sa skladajú podľa verified subjectu. Context assembler nesmie znovu použiť mutable list alebo buffer z predchádzajúceho runu bez tenant resetu.

Sensitive tenant identifiers sa môžu pseudonymizovať pre model, ale policy layer si zachová canonical mapping mimo promptu. Pseudonymizácia nie je isolation, ak mapping alebo raw data zostáva shared bez access controlu.

## 15. Tool catalog isolation

Tenant môže mať odlišné integrations, regions, permissions alebo data-processing contracts. Tool catalog sa preto resolvuje pre tenant a jeho digest je súčasť composed release.

Model nesmie vidieť tool, ktorý tenant nemôže použiť, iba s nádejou, že authorization ho neskôr odmietne. Dynamic exposure znižuje prompt surface aj riziko confused-deputy callu.

## 16. Tool execution isolation

Pred tool callom sa runtime tenant context porovná s canonical resource subjectom a credential scope. Model arguments môžu zúžiť resource, ale nemôžu rozšíriť tenant boundary.

Tool output nesie tenant provenance a data classification. Remote MCP alebo agent server sa nepovažuje za trusted iba preto, že request obsahoval tenant ID.

## 17. Sandbox isolation

Code execution používa per-run alebo per-tenant workspace podľa risku. Writable mounts, temp directories, process namespaces, secrets a outbound destinations sa nesmú zdieľať spôsobom, ktorý umožní residue alebo side channel.

Sandbox teardown overí files, processes, handles a external artifacts. Reuse je povolený iba s preukázateľným resetom a rovnakým tenant boundary; performance optimization nesmie prebiť isolation.

## 18. Network isolation

Default-deny egress a ingress obmedzuje, kam môže tenant workload komunikovať. Kubernetes dokumentácia odporúča pri strict multi-tenancy začať default-deny network policy, ale zároveň upozorňuje, že samotný NetworkPolicy resource nemá efekt bez implementujúceho network pluginu.

Loaded network enforcement sa preto overuje praktickým testom. DNS, metadata service, internal admin endpoints a cross-namespace routes patria do threat modelu.

## 19. Compute isolation

CPU, memory, GPU, concurrency, file descriptors a process count majú tenant alebo workload quotas. ResourceQuota pomáha v Kubernetes namespace, ale nechráni všetky shared resources, napríklad network traffic alebo external provider quota.

Agent platforma potrebuje aj queue, model-token a tool capacity fairness. Compute quota bez provider budgetu nezabráni denial of wallet alebo rate-limit starvation.

## 20. Queue isolation

Queue message nesie immutable tenant a operation identity podpísanú alebo chránenú pred modelovou úpravou. Worker neodvodzuje tenant z payload textu alebo názvu tasku.

Scheduling používa fair-share, priority a per-tenant concurrency. Dead-letter queue zachová tenant boundary a support access; central DLQ bez policy môže byť cross-tenant data lake.

## 21. Model-provider isolation

Provider project, API key, region alebo endpoint môže byť pooled alebo tenant-specific. Rozhodnutie závisí od contractual, residency, quota a isolation požiadaviek.

Ak sa používa pooled provider credential, interný ledger stále viaže každý request na tenant a zabraňuje tomu, aby user-provided metadata menila billing alebo policy attribution. Provider conversation/session objects sa nesmú zdieľať medzi tenantmi.

## 22. Encryption a keys

Tenant-specific keys znižujú blast radius a umožňujú selective revocation, ale zvyšujú operational complexity. Pooled encryption môže byť vhodná pre niektoré vrstvy, ak access policy a key usage audit zachovávajú tenant separation.

Key ID a encryption context obsahujú tenant subject. Decrypt request s mismatched tenantom je forbidden event aj pre platform admin workload bez explicitného break-glass purpose.

## 23. Tracing isolation

Trace metadata nesie tenant reference, ale raw secrets alebo unrestricted customer content sa do observability systému nevkladá. Support alebo eval viewer používa tenant-scoped access a secure evidence references.

Sampling policy nesmie kombinovať payloady z viacerých tenantov do jedného debugging artifactu bez explicitného incident case. Trace export a downstream analytics sú samostatné data processors s vlastným isolation proofom.

## 24. Audit isolation

Audit ledger môže byť centralizovaný, ale každý event má canonical tenant, actor, operation, action a resource. Query API presadzuje tenant a role scope independent od UI filtrov.

Cross-tenant auditor access používa explicitnú governance role, reason, approval a time-bound session. Export je evidovaný ako ďalšia sensitive operation.

## 25. Evaluation isolation

Eval datasets nesmú miešať production tenant data bez právneho, privacy a governance základu. De-identification, synthetic substitution a access control sa aplikujú pred vytvorením reusable case.

Per-tenant regression môže byť potrebná pre custom tools alebo policies. Aggregate score nesmie skryť, že konkrétny tenant route nemá coverage alebo zlyháva isolation invariant.

## 26. Multi-agent isolation

Supervisor, specialists a remote agents zachovávajú tenant context pri každom handoffe. Delegation envelope obsahuje tenant, operation, allowed task, data classes, deadline a return sink.

Remote agent nesmie meniť tenant alebo poslať artifact do vlastného default workspace. Handoff success sa overí aj na receiving side a v descendant effects.

## 27. Administrative a support access

Support engineer potrebuje least-privilege read alebo diagnostic capability, nie shared tenant admin credential. Break-glass access má ticket, reason, approver, expiry, session recording a post-use review.

Agent nemôže sám aktivovať break-glass. Môže pripraviť evidence a request, ale authority zostáva mimo jeho planu.

## 28. Tenant configuration lifecycle

Onboarding vytvorí tenant identity, policies, keys, budgets, routes, storage a test fixtures ako jeden versionovaný lifecycle. Partial onboarding sa nesmie prezentovať ako active tenant.

Offboarding zastaví nové runy, revokuje credentials, uzavrie queues, aplikuje retention/deletion policy a overí caches, backups, traces a external integrations. Vymazanie hlavnej database row nestačí.

## 29. Tenant policy evolution

Policy change má generation a effective time. Long-running run musí pred sensitive actionom overiť current policy a nesmie pokračovať so stale snapshotom, ak sa entitlement alebo tenant status zmenil.

Historical audit zachová loaded generation. Re-evaluation event vysvetlí, prečo bol pôvodný plan zmenený alebo operation zastavená.

## 30. Noisy neighbor

Noisy neighbor môže spotrebovať compute, queue, provider rate limit, vector capacity, human reviewers alebo observability bandwidth. Isolation preto zahŕňa fairness a capacity, nielen confidentiality.

Metriky sa segmentujú per tenant a shared pool. Platforma sleduje headroom aj dominant-share utilization, aby jeden typ resource neostal neviditeľným bottleneckom.

## 31. Side channels

Latency, cache timing, error text, object enumeration alebo model context length môžu nepriamo prezradiť existenciu iného tenant resource. High-risk systems minimalizujú rozdiely a nevracajú interné identifiers v denial response.

Side-channel risk sa hodnotí podľa sensitivity a attacker capability. Nie všetky timing differences sa dajú odstrániť, ale explicitné object existence leaks sú forbidden.

## 32. Cross-tenant tool poisoning

Tenant-controlled tool metadata alebo retrieved content nesmie meniť global catalog pre ostatných tenantov. Custom integration má publisher a tenant scope a jeho descriptions, schemas a outputs zostávajú untrusted.

Promotion do shared catalogu vyžaduje platform review a new generation. Počet úspešných použití jedným tenantom nevytvára global trust.

## 33. Backup a restore

Backup subject a restore workflow zachovávajú tenant scope. Restore jedného tenanta do shared environmentu nesmie prepísať globálne sequences, cache keys alebo encryption mappings.

Restore drill overuje data, policies, keys, vector indexes, memory, external references a audit continuity. Snapshot availability sama osebe nepreukazuje usable isolated recovery.

## 34. Incident `AGENT-GOV-06`

Fallback worker pool používal shared query cache bez tenant keyu a memory store s lokálnym `thread_id`. Tenant B dostal summary vytvorenú pre tenant A, agent ju použil ako planning evidence a pripravil tool argument pre resource z cudzieho kontextu.

Authorization mutation odmietla, takže nevznikol priamy write leak, ale tenant B už videl citlivú summary v model output trace. Súbežne tenant A vyčerpal shared provider token quota a spôsobil latency breach pre ďalších zákazníkov.

## 35. Konkurenčné hypotézy

Prvá hypotéza je database authorization bypass. Druhá je cross-tenant cache hit, tretia memory key collision a štvrtá trace alebo support-viewer leak. Piatou je iba model hallucination bez reálneho cudzieho data source.

Evidence zahŕňa cache key components, memory composite IDs, retrieval candidate lineage, context assembly digest, model input secure reference, policy denial, trace access logs a provider quota attribution. Exact source lineage rozlíši leak od hallucination.

## 36. Containment

Containment aktivuje tenant a shared-component kill switches, vypne suspect cache/memory reuse a presunie affected tenants do isolated worker poolu. New cross-tenant admin exports sa dočasne blokujú a evidence sa zmrazí.

In-flight runs sa zastavia pred ďalším tool alebo model callom, ak loaded tenant policy nie je current. Potentially exposed tenants dostanú incident scope podľa potvrdených data flows, nie podľa nepresného globálneho odhadu.

## 37. Recovery

Recovery pridá tenant do cache, memory, queue a trace subjectov, zavedie credential-bound retrieval a vyčistí residue. Historical artifacts sa analyzujú na ďalšie collisions a unauthorized views.

Noisy-neighbor oprava pridá fair scheduling, tenant reservations a provider quota partitioning. Re-enable prebieha tenant po tenantovi s negative isolation a capacity tests.

## 38. Positive acceptance

Tenant A a B použijú identický query text, rovnaký lokálny thread ID a podobné resource IDs. Každý dostane iba svoje data, cache a memory evidence a tool catalog.

Súbežný heavy run tenant A neprekročí definovaný impact na latency a capacity tenant B. Trace aj billing attribution zostanú správne oddelené.

## 39. Forbidden acceptance

Release neprejde, ak cross-tenant candidate vstúpi do rerankera, model contextu, trace alebo human vieweru, aj keď finálny output ho neobsahuje. Isolation sa hodnotí cez celý data flow.

Neprípustné je tiež, aby tenant filter pochádzal z model arguments alebo user promptu. Verified runtime tenant context je nadradený a nemožno ho prepísať.

## 40. Recovery acceptance

Test vloží stale cache entry, memory collision, delayed queue message a revoked tenant policy. Systém ich odmietne alebo správne revaliduje bez fallbacku na default tenant.

Restore a worker-reuse test overí, že po cleanup nezostal filesystem, process, session alebo model conversation residue. Audit ledger zachová incident a cleanup evidence.

## 41. Second-tenant acceptance

Po oprave sa aktivuje nový tenant s rovnakými naming patterns a custom toolom. Onboarding vytvorí complete isolated subjecty a žiadny artifact sa neviaže na predchádzajúceho tenanta.

Test preukáže aj scoped kill switch: zastavenie tenant A neblokuje tenant B, ale shared compromised component zostane blocked pre oboch podľa explicitnej policy.

## 42. Praktický isolation manifest

Manifest inventarizuje tenant boundary cez jednotlivé platform layers. Každá vrstva uvádza enforcement ownera a loaded generation, aby sa isolation nestala neurčitým tvrdením „používame namespaces“.

Príklad je desired state. Runtime proof potrebuje policy read-back, negative access tests, cache/memory key evidence a capacity results.

```yaml
tenant_isolation:
  version: isolation/v6
  tenant_id: tenant_acme
  identity:
    trust_domain: spiffe://prod.example/tenant/acme
    delegated_audience: agent-tools-prod
  data:
    database_partition: tenant_acme
    vector_namespace: tenant_acme
    encryption_context: tenant_acme
  runtime:
    worker_pool: pooled-eu
    sandbox_workspace: per-run
    network_policy: default-deny-egress@sha256:91ab
  state:
    session_key: [tenant_id, user_id, conversation_id]
    cache_key_prefix: [tenant_id, authz_digest, release_digest]
  fairness:
    max_concurrent_runs: 20
    token_reservation_per_minute: 250000
    queue_weight: 5
```

## 43. Praktický authorization pseudocode

Authorization prijíma tenant context z attested runu a canonical resource z registry alebo trusted parsera. Model-provided tenant value sa ignoruje alebo musí presne zodpovedať verified contextu; nikdy ho nerozširuje.

Pseudocode ukazuje pre-dispatch decision, nie kompletnú database alebo network enforcement. Defense in depth musí rovnaký subject presadiť aj downstream service a storage layer.

```python
def authorize_tenant_action(run, tool, raw_args):
    caller = identity.require_attested_run(run.run_id)
    tenant = caller.require_single_tenant()
    contract = catalog.require_exact(tool.catalog_digest, tool.name)
    args = contract.canonicalize(raw_args)
    resource = resource_registry.resolve(args.resource_ref)

    if resource.tenant_id != tenant.id:
        raise CrossTenantDenied(
            operation_id=run.operation_id,
            caller_tenant=tenant.id,
            resource_tenant=resource.tenant_id,
        )

    decision = policy.evaluate(
        tenant=tenant.id,
        actor=caller.actor_chain,
        action=contract.action,
        resource=resource.subject,
        data_classes=contract.data_flow(args),
        loaded_policy=run.tenant_policy_digest,
    )
    if not decision.allowed:
        raise TenantPolicyDenied(decision.reason)

    return credential_broker.issue_tenant_handle(
        tenant=tenant.id,
        operation_id=run.operation_id,
        action=contract.action,
        resource=resource.subject,
        ttl_seconds=120,
    )
```

## 44. Prevádzkové metriky

Metriky zahŕňajú cross-tenant denial count, missing-tenant-context count, cache isolation misses, memory collisions, candidate lineage violations, tenant-policy staleness, per-tenant latency/cost, dominant resource share, queue fairness a break-glass sessions. Zero denied attacks nie je dôkaz isolation, ak negative tests alebo detection nefungujú.

Platforma sleduje aj support a observability access. Cross-tenant viewer query, export alebo trace link je sensitive action s vlastným auditom.

## 45. Change management

Zmena cache keyu, memory schema, tenant claim mapping, worker reuse, tool exposure, storage partition alebo quota policy je isolation change. Vyžaduje migration plán, backward compatibility a residue test.

Canary používa najmenej dva tenanty a adversarial collisions. Single-tenant staging nedokáže preukázať multi-tenant isolation.

## 46. Primárne zdroje

- [AWS Well-Architected SaaS Lens — Tenant Isolation](https://docs.aws.amazon.com/wellarchitected/latest/saas-lens/tenant-isolation.html)
- [AWS Well-Architected SaaS Lens — Preventing cross-tenant access](https://docs.aws.amazon.com/wellarchitected/latest/saas-lens/preventing-cross-tenant-access.html)
- [AWS Well-Architected SaaS Lens — Multi-tenant microservices](https://docs.aws.amazon.com/wellarchitected/latest/saas-lens/multi-tenant-microservices.html)
- [Kubernetes — Multi-tenancy](https://kubernetes.io/docs/concepts/security/multi-tenancy/)
- [Kubernetes — Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Kubernetes — Resource Quotas](https://kubernetes.io/docs/concepts/policy/resource-quotas/)

## 47. Zhrnutie

Multi-tenant isolation je end-to-end property identity, data, state, tools, runtime, network, capacity, observability a governance vrstiev. Tenant claim, namespace alebo query filter samostatne nestačí.

Bezpečná agent platforma propaguje verified tenant context mimo modelového textu, používa scoped credentials, tenant-aware keys a catalogs, default-deny communication, fair resource budgets, cross-tenant negative tests a complete residue cleanup. Isolation prejde až vtedy, keď druhý tenant nedokáže získať cudzie data ani ovplyvniť jeho outcome alebo dostupnosť cez žiadnu intermediate vrstvu.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Agent reliability, fallback a kill switch](agent-reliability-fallback-kill-switch.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Agent governance a audit →](agent-governance-audit.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
