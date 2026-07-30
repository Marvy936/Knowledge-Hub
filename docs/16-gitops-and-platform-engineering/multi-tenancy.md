# Multi-tenancy

Multi-tenancy je architektúrny a prevádzkový model, v ktorom viac tenantov zdieľa časť platformy, control plane-u, data plane-u alebo supporting services pri explicitne definovaných isolation, fairness, ownership a lifecycle contracts. Tenant môže byť interný tím, business unit, environment, zákazník alebo samostatná workload instance. Bez presnej definície tenant subjectu nie je možné dokázať, čo má byť izolované a čo môže byť bezpečne zdieľané.

Namespace, cluster ani account samy osebe nie sú kompletným tenant boundary. Namespace oddeľuje mená a umožňuje namespaced RBAC, quotas a policies, no nezabráni broad cluster-scoped controlleru čítať cudzie Secrets. Samostatný control plane zlepší API isolation, ale nevyrieši shared node, storage, network alebo external provider identity. Multi-tenancy sa preto posudzuje ako composition viacerých boundaries a ich effective behavior.

## 1. Dominantný model

Tenancy design začína user/business modelom a trust assumptions. Najprv sa identifikuje tenant, assets, actors, required sharing a unacceptable cross-tenant effects. Potom sa zvolí isolation profile a deployment topology. Implementácia musí preniesť tenant identity cez catalog, self-service operation, GitOps, Kubernetes, cloud, secrets, data, observability a billing bez straty alebo premapovania.

```text
business sharing model a tenant definition
→ exact tenant identity, trust a data/capability scope
→ isolation objectives a threat/noisy-neighbor model
→ namespace, virtual-control-plane, cluster/account alebo hybrid topology
→ tenant onboarding a authoritative identity propagation
→ scoped Git, controller, API, network, compute, storage a secret boundaries
→ quotas, fairness a shared-service contracts
→ effective runtime a cross-tenant negative verification
→ observability, cost a incident attribution
→ tenant change, migration a offboarding
→ residual resource/credential/data closure
→ second tenant, second controller a compromise validation
```

Acceptance verdict musí korelovať tenant registry generation, namespace/cluster/account identities, principals, GitOps sources, controller service accounts, policies, network/storage placement a effective data access. „Workloads sú v rôznych namespaces“ je iba jedna evidence vrstva.

## 2. Multi-team a multi-customer tenancy

Kubernetes rozlišuje typické multi-team a multi-customer scenarios. Pri multi-team modeli majú interné tímy priamy alebo GitOps-mediated access k API a existuje určitá úroveň vzájomnej dôvery. Pri multi-customer modeli zákazníci často Kubernetes nevidia a platforma prevádzkuje ich workloads alebo data partitions. Adversarial assumptions a regulatory requirements bývajú prísnejšie.

Rovnaká organizácia môže používať oba modely. Interné platform teams zdieľajú development cluster, zatiaľ čo production SaaS workload spracúva údaje viacerých zákazníkov v jednej application. Tenant identity na Kubernetes úrovni nemusí byť rovnaká ako business customer identity. Je potrebné modelovať obe a ich mapping.

```text
platform tenant
→ tím alebo workload owner s API/GitOps authority

business/data tenant
→ zákazník alebo legal/data isolation subject

infrastructure tenant
→ namespace, virtual cluster, cluster, account alebo dedicated resource pool
```

Jedna namespace pre tím nemusí izolovať jednotlivých zákazníkov v aplikácii. Naopak cluster-per-customer nevyrieši logický bug v shared control service, ktorý používa nesprávny customer ID. Tenancy contract musí pokračovať až po business data access.

## 3. Exact tenant subject

Tenant name `vega` nestačí. Exact subject potrebuje authority, immutable alebo versioned identity, hierarchy a lifecycle state. Tenant môže mať viac namespaces, clusters a accounts. Rename display name nemá vytvoriť nového tenanta ani zmeniť permissions podľa string comparison.

```text
tenant subject
= tenant registry a tenant ID
+ tenant type a trust class
+ parent/hierarchy a legal/data scope
+ isolation profile generation
+ authorized owners a principals
+ assigned namespaces/clusters/accounts/resource pools
+ onboarding generation a lifecycle state
```

Každý derived label alebo annotation musí byť mapovateľný späť na tenant ID a authority generation. `metadata.labels.tenant=vega` je useful selector, ale nie dôkaz, že namespace patrí tenantovi Vega, pokiaľ label môže meniť tenant alebo iný controller.

## 4. Isolation objectives a threat model

Isolation nie je binárne „hard“ alebo „soft“. Je to sada objectives pre confidentiality, integrity, availability, fairness a administrative independence. Dva trusted internal teams môžu zdieľať nodes, ale nesmú meniť resources druhého tímu. Untrusted code môže vyžadovať sandbox, dedicated node alebo cluster. Regulated customer môže potrebovať separate account a KMS boundary.

Threat model zahŕňa compromised developer account, malicious workload, vulnerable controller, misconfigured policy, noisy neighbor, data remanence, secret reference confusion, shared dependency outage a operator error. Pre každý actor sa určí, ktoré shared components môže ovplyvniť a aký blast radius je prijateľný.

Isolation profile má explicitne povedať aj čo sa zdieľa. Shared DNS, ingress, service mesh, observability, registry a operators sú cross-tenant components. Ich identities, quotas, logging a failure modes musia byť súčasťou designu, nie implicitný platform detail.

## 5. Topology: namespace, virtual control plane, cluster a account

Namespace-per-tenant je lacný a dobre podporovaný model pre namespaced resources. Umožňuje RBAC Roles, ResourceQuota, LimitRange a NetworkPolicy. Neizoluje cluster-scoped resources, API server capacity, CRDs, webhooks, StorageClasses ani controllers s cluster-wide credentials.

Virtual control plane poskytuje tenantovi vlastný API server, controller manager a data store, zatiaľ čo worker capacity môže zostať shared. Zlepšuje isolation cluster-scoped API objects a administrative autonomy. Pridáva však control-plane operations, synchronization layer a stále potrebuje data-plane isolation.

Cluster-per-tenant znižuje shared control-plane blast radius a zjednodušuje niektoré policy boundaries. Zvyšuje cost, fleet-management complexity a update burden. Samostatný cloud account/project môže pridať IAM, billing a service-quota isolation. Dedicated hardware môže byť potrebný, ak VM alebo container boundary nie je dostatočný.

| Topology | Silná stránka | Zostávajúci shared risk | Typický cost |
|---|---|---|---|
| Namespace/workload per tenant | nízky overhead, namespaced policy a sharing | cluster scope, API, nodes, controllers | policy a namespace management complexity |
| Virtual control plane | API a cluster-scoped object isolation | worker/data plane a sync layer | per-tenant control-plane operations |
| Cluster per tenant | control-plane a many add-on boundaries | cloud account, fleet tooling, shared providers | cluster count, upgrades, base cost |
| Account/project per tenant | IAM, quota, billing a cloud service scope | organization/root, CI, registry, central services | account vending a governance overhead |
| Dedicated nodes/hardware | compute/noisy-neighbor a breakout blast radius | API/control plane, network, storage services | capacity fragmentation a cost |

Rozhodnutie sa robí podľa required isolation a operational capability, nie podľa sloganu „shared clusters sú lacnejšie“.

## 6. Namespace ako management unit

Namespace je základný management scope, ale potrebuje supporting controls. Tenant alebo workload namespace má unique fleet-wide identity, trusted labels, owner, quota, default-deny network, Pod security profile, service accounts a lifecycle finalizers.

Jedna namespace per team zjednodušuje delegation, ale všetky workloads zdieľajú permissions a policies. Jedna namespace per workload umožní jemnejší blast radius, no zvyšuje management count. Hierarchical namespace tooling alebo platform-level tenant controller môže distribuovať common policies a quotas, ale sám sa stáva privileged authority.

Namespace creation je privileged operation. Tenant nemá mať možnosť vytvoriť namespace s labelom, ktorý ho zaradí do vyššieho trust profilu. Labels používané v NetworkPolicy alebo admission bindings musia byť controller-owned a chránené pred tenant mutation.

## 7. Control-plane authorization a RBAC

RBAC je primárna control-plane isolation boundary pre users a workloads. Tenant principals majú permissions iba na assigned namespaces a resource kinds. ClusterRoleBinding s tenant groupou je vysokorizikový, pretože obchádza namespaced scope. Aggregated roles a wildcard verbs/resources môžu pri pridaní nových CRDs nečakane rozšíriť authority.

Service accounts sú workload identities, nie iba Pod detail. Každý controller a GitOps operation má používať scoped service account. Impersonation je užitočná, pretože central controller môže vyhodnocovať a aplikovať ako tenant identity namiesto vlastného cluster-admin credentialu.

Authorization test musí zahŕňať `can-i` positive aj negative matrix pre druhého tenanta, secrets, rolebindings, custom resources, subresources a cluster-scoped objects. Absencia priameho `get secret` nemusí stačiť, ak tenant môže vytvoriť Pod so secretRef, debug pod, workload identity binding alebo custom resource, ktorú privileged operator spracuje.

## 8. Controllers, operators a confused deputy

Cluster-scoped controller často sleduje resources vo všetkých namespaces a používa broad permissions. Tenant môže vytvoriť namespaced custom resource, ktorá obsahuje references na external alebo cross-namespace objects. Ak controller dôveruje fieldom a vykoná privileged action, stane sa confused deputy.

Controller musí odvodiť tenant identity z trusted request namespace/UID a overiť každú referenced object a external account proti rovnakému tenant scope-u. `credentialRef.namespace`, `targetCluster`, `roleArn` alebo `bucketName` nesmú byť iba syntakticky validné. Potrebujú authorization a ownership check.

Reconciliation status má rozlíšiť denied tenant reference, waiting dependency, partial external mutation a success. Broad controller credential musí byť segmentovaný alebo používať per-tenant delegated identities. Operator compromise blast radius je súčasťou isolation profile.

## 9. GitOps multi-tenancy

GitOps pridáva source a controller authority boundary. Tenant smie meniť iba vlastné source repositories alebo paths, destinations a resource kinds. Argo CD AppProject obmedzuje trusted source repositories, destination clusters/namespaces, allowed resource kinds a project roles. Default project s wildcard sources, destinations a cluster resources nie je tenant boundary.

Flux používa Kubernetes RBAC a môže reconcile-ovať pod service accountom uvedeným v `Kustomization` alebo `HelmRelease`. Multi-tenant lockdown zakazuje cross-namespace references, remote bases a vyžaduje default alebo explicitný tenant service account. Bez toho tenant-controlled Flux object môže použiť source alebo notification resource iného namespace-u alebo central controller cluster-admin authority.

Git repository isolation sama nestačí. Tenant source môže deklarovať Namespace, ClusterRole, CRD alebo webhook, ak project/policy permits. Final render a admission musia overiť resource scope. Platform GitOps instance a tenant instances potrebujú oddelené paths, identities a installation tracking, aby sa ich field ownership neprekrýval.

## 10. Network a DNS isolation

Kubernetes defaultne umožňuje Pod-to-Pod komunikáciu, pokiaľ CNI a policies neurčia inak. Multi-tenant baseline preto často začína default-deny ingress aj egress, explicitným DNS accessom a allow rules podľa trusted namespace/workload identity.

NetworkPolicy účinkuje iba s CNI implementation, ktorá ju podporuje. Empty selector alebo mutable namespace label môže otvoriť širší scope než intended. Service mesh môže pridať workload identity, mTLS a L7 authorization, ale zvyšuje complexity a nevyrieši host-network, DNS, metadata service alebo external egress automaticky.

DNS môže prezrádzať názvy services v iných namespaces. Cross-namespace lookup a service discovery rules musia zodpovedať isolation objective. Egress gateway a firewall potrebujú tenant attribution, aby shared IP alebo NAT neodstránil auditability.

## 11. Compute, scheduling a noisy neighbors

ResourceQuota a LimitRange obmedzujú namespaced requests, limits a object count. Chránia fairness, ale nie všetky shared resources. Network bandwidth, disk IOPS, API requests, image pulls, DNS a controllers môžu zostať noisy-neighbor vectors.

Requests a limits ovplyvňujú scheduling a runtime throttling/OOM. Tenant, ktorý môže vynechať requests, môže spôsobiť overcommit a eviction iných workloads. Quota musí pokryť relevantné resources a platform musí poskytovať capacity feedback, nie iba generic `Forbidden`.

Dedicated nodes s taints, tolerations a node affinity znižujú cross-tenant compute sharing. Node labels používané pre isolation musia byť chránené NodeRestriction alebo trusted provisioningom. Sandbox runtime alebo VM boundary je vhodná pre untrusted code. Dedicated node stále zdieľa API, control-plane a často storage/network services.

API Priority and Fairness, controller work queues a external-provider quotas sú dôležité pre control-plane fairness. Jeden tenant s tisíckami Flux resources alebo failing reconciliations môže spotrebovať shared controller capacity.

## 12. Storage a data isolation

PersistentVolumeClaim je namespaced, ale PersistentVolume a storage backend môžu byť shared. Dynamic provisioning a correct reclaim policy znižujú reuse a data remanence risk. Shared StorageClass musí poskytovať tenant-safe naming, encryption, snapshots a deletion semantics.

Backup a restore sú tenant boundaries. Operator nesmie restore-núť snapshot jedného tenanta do namespace-u druhého bez explicitného data-owner decisionu. Backup catalog, encryption keys a retention policies potrebujú tenant identity. Delete namespace nemusí odstrániť external snapshot, bucket alebo database account.

Application-level data tenancy potrebuje row, schema, database alebo instance isolation model. Kubernetes namespace nepreukazuje, že SQL query obsahuje správny tenant predicate. End-to-end negative canary musí skúsiť access na foreign tenant data cez application aj infrastructure paths.

## 13. Secrets, identity a KMS boundaries

Secret name je namespaced, ale external secret provider path, KMS key a controller identity môžu byť shared. ExternalSecret alebo operator, ktorý môže specify-núť arbitrary provider path, potrebuje tenant-scoped authorization. Central secret controller má používať workload/tenant identities alebo enforce provider path policy.

Shared decryption key pre viac tenantov zvyšuje blast radius. SOPS/KMS recipients, SecretStore scope a provider roles majú zodpovedať isolation profile. Rotation sa overuje per tenant consumer a revocation nesmie prerušiť iných tenantov.

Cloud workload identity mapping musí bindovať Kubernetes service account namespace/name a cluster identity. Wildcard subject v trust policy môže umožniť tenantovi vytvoriť service account s privilegovaným názvom. Identity vending má reservation, policy a read-back.

## 14. Shared services a platform dependencies

Ingress, DNS, registry, observability, service mesh, policy engines, operators a databases môžu byť shared. Každý shared service potrebuje tenant-aware authorization, quotas, data partitioning, audit a failure containment.

Observability je často slabá boundary. Tenant môže vidieť logs, traces alebo metrics iného tenanta cez broad label query. Labels môžu byť spoofed. Backend authorization musí používať trusted tenant mapping a query scoping. Alert routing a incident pages musia korelovať ownera a tenant generation.

Container registry môže oddeliť repositories a credentials, ale shared cache alebo mutable tags môžu miešať artifacts. Billing a cost allocation potrebujú stable tenant identity, nie iba namespace name, ktorý možno zmazať a znovu použiť.

## 15. Tenant onboarding

Onboarding je distributed operation, nie vytvorenie namespace-u. Vytvára tenant registry record, owner groups, isolation profile, namespaces/accounts, quotas, network baseline, service accounts, GitOps project/source boundaries, secret/KMS scopes, observability tenancy, cost center a business/data mappings.

```text
approved tenant request
→ stable tenant ID a trust/data classification
→ isolation profile decision
→ reserved namespaces/accounts/clusters
→ owner a principal bindings
→ policy/network/quota/storage/secret baseline
→ GitOps sources, destinations a service accounts
→ shared-service partitions
→ positive owner workflow test
→ negative foreign-tenant access test
→ catalog/runtime projection
→ tenant accepted
```

Operation je idempotentná a durable. Partial onboarding nesmie označiť tenant za active. Ak namespace existuje, ale network policy alebo KMS grant chýba, status zostáva waiting/partial a workload admission môže byť fenced.

## 16. Tenant change, migration a offboarding

Tenant môže zmeniť ownera, trust class, data classification alebo topology. Upgrade zo shared namespace na dedicated cluster je identity-preserving migration. Tenant ID zostáva stable, kým resources, credentials a traffic sa presúvajú po generations.

Offboarding zahŕňa traffic stop, data retention/export, consumer dependencies, credentials, DNS, backups, cloud accounts, Git sources, policies, observability a billing. Delete namespace je iba jeden step. External providers a cluster-scoped objects môžu prežiť.

Residual scan sa vykonáva podľa tenant ID naprieč systems. Reuse tenant name alebo namespace pred closure môže spojiť nový tenant so starými data alebo roles. Tombstone/retired state chráni identity pred okamžitým reuse-om.

## 17. Observability, audit a cost attribution

Každý request, reconciliation, network flow, secret access a provider call má niesť trusted tenant identity alebo korelovateľný mapping. User-supplied label nestačí. Audit spája principal, delegated controller identity, tenant, target, policy generation a outcome.

Metrics potrebujú per-tenant a shared-service dimensions bez high-cardinality chaosu alebo data leakage. Capacity dashboard má ukázať quotas, usage, throttling, queue age a noisy-neighbor effect. Cost attribution rozlišuje direct tenant resources a shared platform allocation.

Incident timeline musí vedieť odpovedať, ktorý tenant spustil operation, ktorý controller ju vykonal, ktoré foreign resources boli čítané a kedy sa isolation obnovila. Ak logs miešajú tenants alebo redakcia odstráni subject identity, forensic verdict zostane neúplný.

## 18. Isolation testing

Positive test overuje, že tenant dokáže vykonať povolenú prácu. Negative test sa pokúsi čítať alebo meniť foreign tenant resource, použiť foreign source, secret, service account, network endpoint, storage snapshot, observability query a provider role. Oba testy sú potrebné; systém, ktorý všetko deny-ne, je izolovaný, ale nepoužiteľný.

Testovanie musí pokryť direct user aj confused-deputy paths. Tenant možno nemá `get secrets`, ale môže vytvoriť custom resource spracovanú privileged operatorom. Nemôže create ClusterRole, ale môže deploy-núť webhook alebo hostPath Pod, ak resource guardrails chýbajú.

Chaos a failure tests zahŕňajú controller outage, stale catalog, missing policy parameter, CNI failure, DNS misconfiguration, quota exhaustion, node pressure a tenant offboarding počas reconciliácie. Second-tenant test odhaľuje hard-coded defaulty, ktoré single-tenant pilot neukáže.

## 19. Connected incident `GITOPS-PAY-64`

`settlement-export-api` bol provisionovaný ako tenant `vega-regulated`, ale stale catalog generation ho klasifikovala ako `shared-internal`. Guardrail binding pre restricted profile sa nematchol a broad migration exception preskočila cross-namespace reference rule. Multi-tenancy design mal ďalšie latentné slabiny:

```text
namespace isolation:           namespace per service
Flux cross-namespace refs:     allowed
Flux default controller SA:    cluster-admin
tenant Kustomization SA:       settlement-operator
AppProject default:            wildcard sources/destinations/resources
operator watch scope:          all namespaces
operator secret permissions:   get/list/watch all namespaces
NetworkPolicy baseline:        generated only for restricted profile
node placement:                shared worker pool
credentialRef namespace:       user-controlled field
```

Tenant user nemal priamy access k Orion Secretu. Mohol však vytvoriť `SettlementConnection` v svojom namespace. Privileged operator použil user-supplied `credentialRef.namespace: orion-payments`, načítal foreign Secret a vytvoril provider connection. To je confused-deputy breach: namespaced API object bol entry pointom k cluster-wide credential authority.

Zároveň chýbal default-deny egress, pretože standard profile ho negeneroval. Vega workload mohol použiť vytvorenú connection a exportovať `312` z `2 184` dostupných records. Separate namespace a RBAC preto nechránili data plane ani controller-mediated access.

### Multi-tenant redesign

Tenant registry `tenant-vega-71` sa stáva stable authority. Namespace vending vytvára controller-owned binding s namespace UID, tenant ID a isolation profile generation. Flux používa `--no-cross-namespace-refs`, `--no-remote-bases` a tenant service-account impersonation. Argo projects majú explicitné source, destination a resource allowlists; default project je deny-by-default.

Settlement operator prechádza na namespace-scoped alebo per-tenant delegated identity. Custom resource už neobsahuje arbitrary namespace; credential reference je same-namespace alebo opaque tenant credential ID resolve-nutý providerom pod tenant identity. Operator overuje namespace UID/tenant binding aj pri každej reconcile.

Restricted profile pridáva default-deny network, explicitný DNS a provider egress, dedicated nodes alebo sandbox podľa threat modelu, tenant KMS/provider roles, quotas a observability partition. Admission a operator používajú rovnaký tenant contract, ale každý ho presadzuje na vlastnej authority boundary.

```text
tenant-vega-71 + isolation profile restricted-v3
→ namespace UID and controller-owned tenant binding
→ scoped GitOps source/destination/resource contract
→ tenant service account and provider/KMS identity
→ enforce admission cross-tenant deny
→ operator same-tenant authorization and delegated credential
→ default-deny network + explicit egress
→ quota/node/storage/observability isolation
→ positive deployment canary
→ negative Orion secret/data/network/query canaries
→ effective tenant acceptance
```

Containment zrušil provider connection, rotoval Orion credential, zablokoval cross-namespace references, izoloval Vega egress a reconciled exported records podľa business rules. Catalog, guardrail a tenancy opravy boli testované spolu; izolovaná oprava jedného layeru by nechala ďalší confused-deputy path.

## 20. Multi-tenancy acceptance verdict

Acceptance verdict sa viaže na explicitný tenant a isolation profile, nie na počet namespaces. Musí dokázať control-plane authorization, controller behavior, data-plane network/compute/storage, secrets, shared services, fairness, audit a business data isolation. Každá vrstva potrebuje positive aj negative oracle.

Verdict zahŕňa compromise assumptions. Testuje sa tenant user, workload a tenant-controlled Git source; privileged controller sa posudzuje ako samostatný attack surface. Failure jedného policy engine-u alebo stale catalog projection nesmie automaticky zmeniť tenant identity alebo povoliť foreign access.

Multi-tenancy design je prijatý, keď:

- **Tenant subject je exact** — stable tenant ID, type, trust/data scope, owner, profile generation a assigned resources sú explicitné.
- **Topology zodpovedá risku** — namespace, virtual control plane, cluster/account a node isolation sú zvolené podľa threat modelu.
- **Control-plane authorization je least privilege** — users, service accounts, GitOps controllers a operators nemajú foreign alebo zbytočný cluster scope.
- **Cluster-scoped risks sú riadené** — CRDs, webhooks, operators, StorageClasses a cluster roles majú ownership a tenant-safe semantics.
- **GitOps je tenant-scoped** — sources, destinations, resource kinds, cross-namespace refs a reconciliation identities sú bounded.
- **Network a DNS sú explicitné** — default posture, CNI enforcement, egress a cross-namespace discovery sú overené.
- **Compute a fairness sú bounded** — quotas, requests/limits, API/controller capacity a noisy-neighbor controls majú evidence.
- **Storage a data lifecycle je izolovaný** — provisioning, snapshots, restore, reclaim, encryption a application data access sú tenant-safe.
- **Secrets a provider identities sú scoped** — references, KMS, workload identities, rotation a controller credentials neprekračujú tenant boundary.
- **Shared services autorizujú tenant context** — observability, ingress, registry, mesh a databases majú partition a audit.
- **Onboarding/offboarding je durable** — partial state, migration a residual closure sú explicitné.
- **Negative tests prešli** — foreign resource, secret, network, storage, observability, provider a business-data paths sú odmietnuté.
- **Second tenant a controller-compromise test prešiel** — design nefunguje iba pre single-tenant happy path.

## 21. Troubleshooting flow

Cross-tenant symptom sa považuje za security incident, nie bežný authorization ticket. Najprv sa fence foreign access, preservujú audit a controller evidence a rotujú credentials podľa blast radiusu. Potom sa rekonštruuje tenant identity propagation od registry po effective access.

```text
cross-tenant access, mutation alebo noisy-neighbor impact
→ affected tenant IDs, assets a time window
→ user/workload/delegated controller principals
→ namespace/cluster/account and isolation profile generations
→ GitOps source, project and service-account authority
→ admission/policy decision and exceptions
→ controller/operator reference authorization
→ network, storage, secret, provider and data-plane evidence
→ containment and credential/data reconciliation
→ root boundary remediation
→ residual scan across all tenants
→ positive owner workflow + negative foreign-tenant retest
```

Ak tenant user nemal direct permission, treba hľadať indirect execution: Pod creation, custom resource, controller, service account token, workload identity, external provider alebo shared observability query. RBAC deny nie je dôkazom end-to-end isolation.

## 22. Anti-patterny

Multi-tenancy anti-patterny zvyčajne vznikajú pri povýšení jednej technickej segmentácie na kompletný isolation verdict. Nasledujúce vzory treba overovať proti exact tenant subjectu a cross-tenant effective paths.

### Namespace equals tenant boundary

Namespace je useful scope, ale cluster-scoped controllers, nodes, network, storage a external systems môžu boundary obísť. Potrebný je composed isolation profile. Namespaced RBAC pass preto musí dopĺňať controller, network, secret a data negative evidence.

### Cluster-admin GitOps controller pre tenant sources

Tenant-controlled desired state vykonávaný cluster-admin identity mení source access na cluster privilege. Controller má impersonovať tenant service account a obmedziť sources, refs, destinations a kinds.

### Broad operator, trusted custom resource

Namespaced CR nie je bezpečný iba preto, že je namespaced. Každý reference field môže byť confused-deputy path. Operator musí overovať tenant ownership a používať scoped identity.

### Mutable tenant labels ako authority

Label je vhodný selector, ale ak ho môže zmeniť tenant alebo stale automation, policy scoping zlyhá. Critical binding potrebuje controller-owned identity a namespace UID. Label môže zostať projection pre queries, nie jediná authority pre privilege.

### Quota ako kompletná fairness

CPU/memory quota nechráni API server, DNS, network, IOPS, controller queues ani provider limits. Shared capacity potrebuje viacrozmerné budgets a backpressure. Fairness verdict musí sledovať aj latency a outcome ostatných tenants.

### Dedicated nodes ako hard isolation

Dedicated node znižuje compute sharing, ale stále môže zdieľať API, kubelet trust, storage, network a controllers. Threat model musí pokryť zvyšné boundaries. Pri untrusted code môže byť potrebný sandbox alebo samostatný cluster/account.

### Offboarding delete namespace

External data, credentials, snapshots, DNS, billing a cluster-scoped resources môžu prežiť. Residual scan podľa tenant ID je povinný. Namespace name sa nesmie znovu použiť, kým closure evidence nepotvrdí odstránenie alebo bezpečné retained state-y.

### Positive test bez negative testu

To, že tenant dokáže deploy-núť, nepreukazuje, že nedokáže čítať cudzie dáta. Isolation sa overuje pokusom o forbidden paths. Test musí zahŕňať direct principal aj privileged controller-mediated execution.

## 23. Kontrolné otázky

1. Ako sa líši platform, business/data a infrastructure tenant?
2. Čo tvorí exact tenant subject a isolation profile?
3. Prečo sa „hard“ a „soft“ tenancy lepšie chápe ako spectrum?
4. Aké trade-offs majú namespace, virtual control plane, cluster a account per tenant?
5. Prečo namespace sama osebe nie je security boundary?
6. Ako môže cluster-scoped operator vytvoriť confused-deputy breach?
7. Ako Argo CD AppProject a Flux service-account impersonation podporujú tenant isolation?
8. Prečo NetworkPolicy potrebuje trusted labels a CNI enforcement?
9. Ktoré noisy-neighbor vectors ResourceQuota nepokrýva?
10. Ako sa secret/KMS/provider identity viaže na tenant?
11. Prečo `GITOPS-PAY-64` prešiel napriek namespaced RBAC?
12. Čo musí obsahovať multi-tenancy acceptance verdict?

## Glossary impact

Relevantné pojmy: multi-tenancy, tenant subject, platform tenant, business tenant, infrastructure tenant, isolation profile, control-plane isolation, data-plane isolation, namespace-per-tenant, virtual control plane, cluster-per-tenant, tenant identity propagation, controller confused deputy, tenant-scoped GitOps, tenant service-account impersonation, cross-namespace reference, noisy neighbor, tenant shared service, tenant onboarding operation, tenant residual scan, cross-tenant negative test, multi-tenancy acceptance verdict.

## Primárne zdroje

Zdroje dokumentujú Kubernetes multi-tenancy spectrum, namespace/RBAC/network/quota boundaries a GitOps-specific source, destination a reconciliation authorization. Kapitola ich skladá do end-to-end tenant contractu, pretože žiadny jednotlivý mechanizmus neposkytuje úplnú isolation sám.

Tieto dokumenty popisujú jednotlivé building blocks a odporúčania, ale Kubernetes zámerne neposkytuje jeden first-class Tenant object ani univerzálnu definíciu hard isolation. Organizácia preto musí explicitne vytvoriť tenant registry, isolation profiles a end-to-end negative tests pre svoje controllers, shared services a business data. Pri adopcii Argo CD alebo Flux treba validovať presnú prevádzkovanú verziu, default permissions a bootstrap konfiguráciu, nie predpokladať bezpečný multi-tenant default.

- [Kubernetes — Multi-tenancy](https://kubernetes.io/docs/concepts/security/multi-tenancy/)
- [Kubernetes — Namespaces](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/)
- [Kubernetes — RBAC Authorization](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [Kubernetes — Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Kubernetes — Resource Quotas](https://kubernetes.io/docs/concepts/policy/resource-quotas/)
- [Kubernetes — Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [Kubernetes — Node Isolation/Restriction](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/)
- [Flux — Multi-tenancy](https://fluxcd.io/flux/installation/configuration/multitenancy/)
- [Argo CD — Projects](https://argo-cd.readthedocs.io/en/stable/user-guide/projects/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Guardrails](guardrails.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Keycloak architecture a responsibility boundary →](../17-keycloak-and-identity-platform/keycloak-architecture-and-responsibility-boundary.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
