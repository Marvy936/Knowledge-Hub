## Admission action

Spôsob, akým policy engine naloží s neúspešnou validáciou. `Deny` request odmietne, `Warn` ho dovolí s upozornením a `Audit` zaznamená failure do audit evidence; tieto actions preto predstavujú odlišné risk decisions, nie iba rozdielny log level.

## Background policy audit

Periodické alebo event-driven vyhodnocovanie už uložených resources voči policy. Zachytáva pre-existing a drift violations, ktoré request-time admission nevidel, ale samo osebe nemusí zabrániť ich runtime účinku ani uchovávať kompletnú historickú stopu.

## Business tenant

Zákazník, legal entity alebo iný business/data subject, ktorého údaje a operácie musia byť oddelené podľa business contractu. Nemusí sa zhodovať s platform tenantom ani s jedným Kubernetes namespace-om.

## Catalog compare-and-swap

Precondition model, pri ktorom catalog-driven operation smie pokračovať iba vtedy, ak critical entity generation zostala rovnaká ako pri plánovaní a approvale. Zmena ownera, tenant boundary alebo lifecycle preto invaliduje stale plan namiesto aplikovania bývalého rozhodnutia.

## Catalog-driven operation

Automatizovaná alebo self-service mutation, ktorá používa catalog entity alebo relation ako vstup. Bez field authority, freshness a exact entity generation môže catalog-driven operation udeliť privilege alebo vytvoriť resource podľa stale projection.

## Catalog entity subject

Exact identita catalog entity vrátane catalog instance, `apiVersion`, `kind`, namespace, name, source identity a relevantnej source/stitched generation. Display name bez scope-u a generation nie je dostatočný audit ani automation subject.

## Catalog freshness budget

Maximálna tolerovaná staleness konkrétneho catalog fieldu alebo source projection pre definovaný use case. Discovery UI môže akceptovať staršiu hodnotu než privileged tenant, IAM alebo decommission decision.

## Catalog processing error

Failure počas policies/processors alebo stitching pipeline-u, ktorý zabráni vytvoreniu novej validnej final entity. Catalog môže zachovať poslednú dobrú projection, ale critical downstream consumers musia vidieť error a nesmú dostupnosť starej entity zameniť za freshness.

## Catalog relation integrity

Vlastnosť relation graphu, pri ktorej source, type a target reference majú definovanú semantics, sú resolvable a dostatočne aktuálne pre intended decision. Dangling alebo stale relation môže zostať užitočná pre diagnostiku, ale nie je automaticky dependency truth.

## Catalog source generation

Immutable revision, provider cursor alebo iná identity raw inputu, z ktorého catalog entity vznikla. Umožňuje reprodukovať ingestion a odlíšiť aktuálny descriptor od poslednej úspešne spracovanej verzie.

## Cluster-per-tenant

Topology, v ktorej tenant dostáva samostatný Kubernetes cluster. Zlepšuje control-plane a add-on isolation, ale zvyšuje fleet-management cost a nevyrieši automaticky shared cloud account, CI, registry, external provider alebo application-level data tenancy.

## Control-plane isolation

Ochrana Kubernetes alebo iného platform API a jeho objects pred cross-tenant read, mutation, availability a policy effects. Zahŕňa authorization, API capacity, cluster-scoped resources, admission a controller boundaries.

## Controller confused deputy

Failure mode, v ktorom tenant nemá priamy privilege, ale odošle namespaced alebo inak povolený request privileged controlleru, ktorý vykoná cross-tenant alebo širšiu mutation bez overenia tenant ownershipu. Obrana vyžaduje subject propagation, reference authorization a scoped execution identity.

## Cross-namespace reference

Reference z resource v jednom namespace do source, secret, configuration alebo iného objectu v inom namespace. V multi-tenant systéme je to samostatná authorization boundary; samotná technická schopnosť resolve-núť reference nepreukazuje povolenie.

## Cross-tenant negative test

Test, ktorý sa zámerne pokúsi z tenant A čítať, meniť alebo použiť resource, identity, network endpoint, storage, observability query alebo business data tenanta B. Dopĺňa positive test a dokazuje isolation namiesto iba použiteľnosti.

## Data-plane isolation

Ochrana running workloads a ich network, compute, storage a data paths pred cross-tenant confidentiality, integrity, availability a noisy-neighbor effects. Samostatný control plane ju automaticky nezaručuje.

## Effective compliance

Stav, v ktorom nie iba request alebo uložený manifest, ale aj controller-resolved resource, running workload a relevantný security/business outcome spĺňajú chránený invariant. Policy pass bez read-backu effective state-u môže byť false green.

## Enforcement boundary

Miesto, na ktorom má guardrail dostatočnú authority a context na vykonanie záväzného allow, deny, mutation alebo correction decisionu. Skoršie IDE či CI checks môžu znižovať feedback time, ale nenahrádzajú final authoritative boundary.

## Expected catalog inventory

Externým authority setom definovaný denominator entít, ktoré majú byť v catalogu. Coverage meraná iba voči úspešne ingested entities môže skryť chýbajúci celý repository, account alebo tenant segment.

## Field authority map

Kontrakt, ktorý pre každý critical catalog field určuje authoritative writera, source identity, update mechanismus, validation, conflict policy a freshness semantics. Zabraňuje tomu, aby stitched projection alebo last-write-wins nevedomky nahradili skutočnú authority.

## Generated guardrail resource

Resource vytvorený policy alebo platform controllerom ako súčasť guardrailu, napríklad NetworkPolicy, ResourceQuota alebo RoleBinding. Potrebuje field ownership, update/delete lifecycle a pravidlá pre tenant modifications, inak generation vytvára hidden writera.

## Guardrail

Systematická hranica povoleného priestoru, ktorá umožňuje decentralizovanú autonómiu pri zachovaní definovaných security, reliability, cost alebo governance invariants. Môže kombinovať safe defaults, warnings, audit, validation, mutation, generation, denial a corrective mechanisms.

## Guardrail acceptance verdict

End-to-end rozhodnutie, že konkrétny guardrail správne matchuje expected subjects, presadzuje invariant na vhodnej boundary, má bounded exception/failure semantics a preukazuje effective risk outcome bez neprimeraného blokovania legitímnej práce.

## Guardrail failure policy

Rozhodnutie, či policy evaluation error alebo nedostupnosť enforcement komponentu vedie k povoleniu alebo odmietnutiu requestu. Fail-open a fail-closed menia security aj availability contract a musia byť zvolené podľa risk class, nie globálnym zvykom.

## Guardrail subject

Exact evaluation subject zahŕňajúci policy, binding, parameter a engine generation, principal, operation, target resource, pre/post-mutation object, exception a outcome identity. Policy name alebo resource name samostatne nie sú dostatočné.

## Infrastructure tenant

Konkrétny infrastructure scope pridelený tenantovi, napríklad namespace, virtual cluster, cluster, cloud account alebo dedicated node pool. Je projection isolation decisionu a nemusí byť totožný s business tenantom.

## Isolation profile

Versionovaný contract, ktorý pre tenant alebo workload definuje topology, authorization, network, compute, storage, secrets, shared-service, observability a lifecycle controls. Hodnota `restricted` bez generation a concrete mechanisms nie je dostatočným dôkazom isolation.

## Last-good catalog projection

Posledná bezchybná stitched entity zachovaná po novšom ingestion alebo processing failure. Zvyšuje catalog availability, ale musí niesť stale/error semantics; pre critical automation nemá byť implicitne považovaná za aktuálnu authority.

## Match coverage

Pomer alebo inventory dôkaz, že policy binding a selectors skutočne vyhodnotili všetky expected subjects. Zero violations bez match coverage môže znamenať nesprávny selector alebo vypnutý enforcement, nie compliance.

## Multi-tenancy

Model zdieľania platform resources medzi viacerými tenants pri explicitných isolation, fairness, ownership a lifecycle contracts. Nie je to synonymum pre namespace-per-team; zahŕňa control plane, data plane, controllers, external services a business data.

## Multi-tenancy acceptance verdict

End-to-end rozhodnutie, že exact tenant a isolation profile sú správne presadené cez GitOps, API, controllers, network, compute, storage, secrets, shared services a business-data paths a že positive aj foreign-tenant negative tests prešli.

## Namespace-per-tenant

Topology, v ktorej tenant alebo workload dostáva samostatný Kubernetes namespace. Poskytuje namespaced naming, RBAC, quota a policy scope, ale neizoluje cluster-scoped resources, broad controllers, shared nodes ani external identities bez ďalších controls.

## Noisy neighbor

Tenant alebo workload, ktorý spotrebovaním shared compute, I/O, network, API, controller alebo provider capacity zhorší outcome iných tenants. CPU/memory ResourceQuota pokrýva iba časť možných noisy-neighbor paths.

## Operational ownership relation

Catalog relation, ktorá spája software alebo platform entity s resolvable ownerom a konkrétnym decision/escalation scope-om. Nie je to iba display label; musí podporovať owner transfer, reachability, orphan handling a incident routing.

## Orphan entity

Catalog entity, ktorá stratila parent/provider edge alebo registered source a nemá iný aktívny ingestion path. Orphan status nepreukazuje, že runtime resource alebo software zanikol; deletion catalog recordu musí byť oddelená od decommission closure.

## Platform tenant

Interný tím, workload owner alebo iný subject, ktorému platform deleguje API, GitOps alebo self-service authority. Môže prevádzkovať viac business tenants a používať viac infrastructure scopes.

## Policy binding generation

Versionovaný effective scope, ktorý spája policy logic s resources, namespaces, operations, actions a prípadnými parameters. Rule bez matching bindingu nemá enforcement effect, preto binding patrí do policy identity.

## Policy exception subject

Exact kombinácia policy generation, resource alebo operation identity, tenant/environment, reason, owner, approval, expiry a compensating controls, pre ktorú je bypass povolený. Broad selector bez expiry je alternate policy, nie bounded exception.

## Policy generation

Immutable alebo reprodukovateľná identity effective policy logic vrátane dependencies a engine/API compatibility. Pri guardraile nestačí hash expression, ak binding, parameters alebo external data menia výsledné rozhodnutie.

## Policy parameter generation

Identity concrete values, ktorými sa abstract policy mení na environment alebo tenant-specific rule. Zmena replica limitu, trusted issueru alebo isolation profile parameteru mení effective guardrail aj bez editácie policy logic.

## Policy rollout migration

Riadený prechod policy cez expected-inventory analysis, offline tests, Audit/Warn, remediation, bounded exceptions a Enforce. Má explicitné exit criteria a expiry; permanentný audit-only stav nie je dokončený preventívny control.

## Protected invariant

Presné tvrdenie o stave alebo správaní, ktoré guardrail chráni, napríklad zákaz cross-tenant credential access. Je odvodené z threat/risk modelu a je širšie než jeden syntaktický field check.

## Runtime projection

Catalog alebo portal view odvodený z deployment, observability alebo cloud systemu. Musí niesť concrete target identity, generation a observation time a nesmie byť zamieňaný za authoritative runtime controller alebo business oracle.

## Service catalog

Riadený graph softvérových, platformových, organizačných a resource entities pre ownership, discovery, lifecycle, dependencies a developer/operational workflows. Je hubom a projection layerom; nie je automaticky authority pre každý zobrazený field.

## Service-catalog acceptance verdict

End-to-end rozhodnutie, že catalog pokrýva expected inventory, zachováva field authorities a generations, signalizuje staleness/errors, má integrity relations a vedie discovery, routing a automation k správnemu outcome-u aj pri source move, orphan alebo processor failure.

## Stitched entity generation

Identity final catalog entity vytvorenej po ingestion, policies/processors, emitted relations a stitching. Môže sa líšiť od source generation a musí odhaliť, keď final projection zostala stará po chybe novšieho inputu.

## Tenant identity propagation

Prenos stable tenant ID a isolation profile generation z tenant authority cez catalog, self-service, GitOps, namespaces/clusters, controllers, network, secrets, observability a billing. Strata alebo premapovanie identity na ľubovoľný label vytvára cross-tenant risk.

## Tenant onboarding operation

Durable distributed operation, ktorá vytvára tenant registry record, infrastructure scopes, identities, policies, quotas, network, secret/provider a shared-service partitions a končí až po positive aj negative verification. Namespace creation je iba jeden child step.

## Tenant residual scan

Post-offboarding alebo post-migration vyhľadanie všetkých resources, credentials, data, snapshots, DNS, GitOps objects, observability partitions a billing records podľa stable tenant ID. Bráni tomu, aby delete namespace zanechal aktívne foreign paths alebo aby sa identity predčasne reused.

## Tenant-scoped GitOps

GitOps model, v ktorom tenant môže používať iba povolené sources, destinations, resource kinds a reconciliation identities a nemôže reference-núť cudzie namespace resources alebo platform authority. Scope sa presadzuje v GitOps projecte/controlleri, RBAC aj admission.

## Tenant service-account impersonation

Mechanizmus, pri ktorom central GitOps alebo platform controller vykonáva tenant reconciliation pod explicitnou namespaced service-account identity namiesto vlastného cluster-admin credentialu. Umožňuje Kubernetes authorization presadiť tenant boundary aj pri shared controlleri.

## Tenant shared service

Platform service používaná viacerými tenants, napríklad ingress, DNS, registry, observability, service mesh alebo operator. Potrebuje tenant-aware authorization, partitioning, quota, audit a failure containment, pretože shared service je cross-tenant boundary.

## Tenant subject

Stable authority identity tenanta vrátane tenant ID, typu, trust/data scope-u, hierarchy, owners, isolation profile generation a assigned infrastructure scopes. Display name alebo namespace label samostatne nie je dostatočný.

## Validation action

Concrete response na policy validation result, napríklad Deny, Warn alebo Audit. Action určuje, či violation zabráni mutation alebo iba vytvorí evidence, a preto musí byť súčasťou effective policy generation.

## Virtual control plane

Per-tenant Kubernetes API server, controller manager a data store nad shared alebo sprostredkovaným data plane-om. Zlepšuje isolation cluster-scoped API objects a administrative autonomy, ale stále potrebuje network, compute, storage a controller isolation.
