# Multi-tenancy

Multi-tenancy je architektúrny a prevádzkový model, v ktorom viac tenantov zdieľa časť platformy, control plane-u, data plane-u alebo supporting services pri explicitných isolation, fairness, ownership a lifecycle contracts. Tenant môže byť interný tím, business unit, environment, zákazník alebo workload. Bez stable tenant identity a threat modelu nemožno dokázať, čo má byť izolované a čo môže byť bezpečne zdieľané.

Namespace, cluster ani cloud account samy osebe nie sú complete tenant boundary. Namespace poskytuje namespaced naming, RBAC, quotas a policies, ale nezastaví cluster-scoped controller s broad Secret accessom. Cluster-per-tenant stále môže zdieľať registry, CI, provider identity alebo business control service.

```text
business sharing model a tenant definition
→ stable tenant ID, trust a data scope
→ isolation/fairness objectives a threat model
→ isolation profile a topology
→ authoritative tenant onboarding
→ identity propagation cez catalog, GitOps, cluster a providers
→ scoped API/controller/network/compute/storage/data boundaries
→ positive a cross-tenant negative verification
→ attribution, incident response a lifecycle changes
→ offboarding a residual scan
→ second tenant a compromised-controller test
```

## 1. Tenant layers a exact subject

Platform tenant môže byť tím s GitOps/API authority. Business/data tenant môže byť zákazník alebo legal data subject. Infrastructure tenant môže byť namespace, virtual control plane, cluster, account alebo dedicated resource pool. Tieto identities sa môžu mapovať, ale nie sú automaticky rovnaké.

Exact subject obsahuje tenant registry a stable tenant ID, tenant type a trust class, hierarchy/legal/data scope, isolation profile generation, authorized owners/principals, assigned namespaces/clusters/accounts/pools, onboarding generation a lifecycle state.

```text
tenant-vega-71
→ business tenant Vega regulated
→ isolation profile restricted-v3
→ namespaces UID N71...
→ Git sources a service accounts
→ cloud/provider account bindings
```

Display rename `vega` nesmie vytvoriť novú authority. Label `tenant=vega` je selector, nie proof, ak ho tenant alebo untrusted controller môže meniť. Critical labels a namespace bindings majú byť controller-owned a mapovateľné na registry generation.

## 2. Isolation objectives a topology

Isolation sa rozkladá na confidentiality, integrity, availability, fairness, administrative independence a forensic attribution. Threat model zahŕňa compromised developer, malicious workload, vulnerable controller/operator, misconfigured policy, noisy neighbor, data remanence, cross-tenant reference, shared dependency outage a operator error.

Namespace-per-tenant je lacný a vhodný pri určitej vzájomnej dôvere, ale zdieľa API, CRDs, webhooks, controllers, nodes a storage classes. Virtual control plane izoluje API a cluster-scoped objects, no môže zdieľať worker/data plane. Cluster-per-tenant znižuje control-plane blast radius za cenu fleet complexity. Account/project-per-tenant pridáva IAM, quota a billing boundary. Dedicated nodes alebo hardware riešia compute isolation, nie automaticky API, network a provider identity.

Topology sa vyberá podľa required objective a operational capability. `Shared cluster je lacnejší` alebo `cluster per tenant je secure` sú neúplné tvrdenia. Isolation profile explicitne uvádza shared DNS, ingress, registry, observability, operators a provider services a ich residual risk.

## 3. Onboarding a identity propagation

Tenant onboarding je privileged state transition. Registry vytvorí stable ID a profile, platform controller vytvorí namespace/account bindings, service accounts, policies, quotas, egress a observability partitions. Catalog môže zobrazovať projection, no nemá byť sole authority bez freshness gate-u.

Tenant identity musí zostať zachovaná cez:

```text
self-service operation
→ catalog/service identity
→ environment Git path
→ Argo AppProject alebo Flux Kustomization
→ namespace UID a service account
→ cloud/provider credential
→ network/data/observability attribution
```

Strata identity na jednej boundary vytvára confused-deputy alebo billing/audit gap. Free-text tenant field v custom resource nesmie autorizovať foreign resource. Controller odvodzuje tenant z trusted namespace/UID a overuje každú reference proti registry bindingu.

## 4. API authorization, workloads a indirect privilege

RBAC má preferovať namespaced permissions a explicitné resource/verb scopes. ClusterRoleBinding, wildcards, `bind`, `escalate`, impersonation a workload creation paths potrebujú escalation analysis. Tenant bez direct `get Secret` môže secret získať vytvorením Podu, použitím privileged service accountu alebo custom resource-u, ktorú broad operator spracuje.

Service account je workload identity a controller execution boundary. Central GitOps controller môže používať impersonation alebo tenant-scoped service account, aby final mutation podliehala tenant RBAC. Default cluster-admin reconciliation robí z každého tenant-controlled manifestu indirect cluster-admin request.

Positive a negative authorization matrix testuje vlastný a cudzí namespace, Secrets, RoleBindings, custom resources, subresources, cluster-scoped objects a workload-induced access. `kubectl auth can-i` je časť evidence, nie celý runtime oracle.

## 5. Controllers a confused deputy

Cluster-scoped operator často sleduje custom resources vo všetkých namespaces a používa broad cloud/Secret permissions. Tenant môže vytvoriť namespaced resource s fieldami `credentialRef.namespace`, `targetCluster`, `roleArn` alebo `bucketName`. Syntaktická validita reference neznamená tenant authorization.

Controller musí:

```text
read request namespace UID
→ resolve trusted tenant binding
→ resolve referenced object/provider identity
→ prove same-tenant alebo approved shared relation
→ use delegated tenant credential
→ persist decision provenance
→ verify external outcome
```

Cross-tenant reference sa odmietne ešte pred privileged read/call. Broad central credential sa segmentuje alebo broker vydá short-lived tenant-bound capability. Controller status rozlišuje authorization denied, waiting, partial external mutation a success. Compromised-controller blast radius je súčasť isolation profile a chaos/security testu.

## 6. GitOps tenant boundary

Argo AppProject obmedzuje source repositories, destination clusters/namespaces, resource kinds a project roles. Default project s wildcard sources/destinations nie je multi-tenant boundary. Kubernetes RBAC pod controllerom musí zodpovedať project policy; UI/project allowlist bez enforcement identity nestačí.

Flux multi-tenant lockdown zakazuje cross-namespace references a remote bases podľa configuration a používa `spec.serviceAccountName` alebo controlled default service account v tenant namespace. Tenant source nesmie odkazovať na Secret, Source alebo Receiver iného namespace-u ani využívať controller-global cluster-admin authority.

Final render a admission kontrolujú cluster-scoped resources, Namespace, CRDs, webhooks a RBAC. Repository separation sama nezabráni tenantovi deklarovať privileged object. Platform a tenant GitOps instances potrebujú odlišné installation/tracking identities a field ownership, aby si navzájom neprune-li resources.

## 7. Network, compute a control-plane fairness

Multi-tenant network baseline typicky používa default-deny ingress/egress, explicitný DNS access, allow rules podľa trusted namespace/workload identity a scoped external egress. NetworkPolicy funguje iba s podporujúcim CNI a nepokrýva automaticky hostNetwork, node services, metadata endpoint alebo all external provider semantics.

Shared ingress, service mesh a egress gateway potrebujú tenant-aware identity, authorization a attribution. Shared NAT IP nesmie odstrániť auditability provider calls. DNS/service discovery môže prezrádzať foreign service names a potrebuje explicitný scope.

ResourceQuota a LimitRange chránia namespaced CPU/memory/object count, ale nie vždy API QPS, DNS, image pulls, controller queues, network bandwidth alebo provider quotas. API Priority and Fairness, per-tenant controller queues a rate/concurrency budgets chránia control plane. Jeden tenant s reconcile hot loopom nesmie vyčerpať recovery capacity ostatných.

Dedicated nodes, taints/affinity, sandbox runtimes alebo VMs znižujú compute breakout/noisy-neighbor risk. Node labels použité pre isolation musia byť trusted. Dedicated node stále môže zdieľať storage, API a provider credentials.

## 8. Storage, data, secrets a observability

PVC je namespaced, no PV a backend môžu byť shared. StorageClass, reclaim policy, snapshots, encryption keys a backup catalog potrebujú tenant identity. Namespace delete nemusí odstrániť external snapshot alebo database account. Restore foreign snapshot je cross-tenant data access a vyžaduje explicitný data-owner decision.

Application-level data tenancy pokračuje za Kubernetes. Query, cache key, event, object storage prefix a provider account musia niesť tenant context a authorization. Cluster-per-tenant nevyrieši bug v shared service, ktorý použije wrong customer ID.

Secrets a workload identity sú tenant boundaries. Shared controller nemá čítať arbitrary tenant Secrets. External secret path, KMS key a cloud role sa autorizujú podľa trusted tenant ID. Observability backend potrebuje tenant-aware ingestion a query authorization; labels samy nestačia, ak ich workload môže spoofovať. Support engineer access a debug export musia byť auditované a bounded.

## 9. Lifecycle, migration a offboarding

Tenant profile sa môže zmeniť, napríklad `standard → restricted-v3`. Transition musí migrovať namespace policies, GitOps identity, network/egress, nodes, storage, provider credentials, observability a catalog projection. Zmena labelu bez resource convergence vytvorí false isolation verdict.

Offboarding flow zastaví new work, drain-ne traffic, zachová required data, revoke-ne users/workload/controllers/provider identities, odstráni Git desired state a resources, zmaže alebo archivuje backups podľa retention a vykoná residual scan naprieč clusterom a external systems.

```text
tenant closing
→ inventory all bindings/resources/data
→ drain a retention decisions
→ revoke identities/secrets
→ delete desired/live/external state
→ verify no foreign access ani orphan cost
→ tombstone stable tenant ID
```

ID sa nemá okamžite reuse-nuť; stale references by mohli získať nový význam.

## 10. Connected incident `GITOPS-PAY-64`

Stale catalog generation `catalog-g118` priradila nový `settlement-export-api` k `orion-payments/shared-internal`, hoci latest descriptor ho presunul do `tenant-vega-71/restricted`. LaunchPad vytvoril standard namespace a restricted guardrail sa nematchol.

Flux povoľoval cross-namespace references a shared controller mal cluster-admin authority. Vega tenant vytvoril namespaced `SettlementConnection` s user-controlled `credentialRef.namespace=orion-payments`. Cluster-scoped operator s broad Secret read permission načítal `orion-payments/provider-settlement` a vykonal provider action v Orion context-e.

Vega user nemal direct Secret permission, no operator sa stal confused deputy. Namespace a RBAC preto neboli complete boundary. Počas `45 minút` bolo v wrong provider context-e dostupných `2 184` settlement records a `312` bolo exportovaných do Vega workspace. Shared nodes/egress a stale incident owner zväčšili dopad a triage.

Root cause bola neúplná tenant composition: stale identity propagation, cross-namespace GitOps, cluster-admin controller a operator bez same-tenant reference authorization.

## 11. Authoritative redesign a acceptance paths

Redesign používa stable `tenant-vega-71` a `restricted-v3` profile. Fresh catalog generation `g119` je precondition. Namespace UID má controller-owned tenant binding. Flux zakazuje cross-namespace refs a reconcile-uje ako tenant service account. Argo používa explicitné source/destination/resource allowlists. Operator odvodí tenant z namespace a používa delegated Vega credential; foreign reference je Deny.

Network je default-deny so scoped egress, quotas a fairness chránia shared capacity, nodes/storage/observability používajú restricted profile. Positive Vega workflow a negative Orion access canary overujú effective boundary.

Positive path umožní vlastné resources/provider context. Negative path odmietne foreign Secret, source, role, network a data access. Noisy-neighbor path zachová SLO ostatných tenantov. Migration path prejde standard→restricted bez mixed state-u. Offboarding path odstráni residual access/data. Forbidden path odmietne namespace-only assurance, user-mutable tenant label, broad operator credential, cross-namespace GitOps, shared unscoped observability, foreign restore a ID reuse.

## 12. Troubleshooting a anti-patterny

Pri cross-tenant incidente sa mapuje stable tenant IDs a registry generation, namespace UID/bindings, principals/RBAC, Git sources a controller identities, custom-resource references, operator authorization/credential, network/egress, storage/data/provider context, observability attribution a lifecycle state. Potom sa testuje každý indirect path, nie iba direct user permission.

Anti-patterny sú: `namespace = tenant isolation`, `user nemá get Secret, takže je safe`, `cluster-admin controller je iba implementation detail`, `tenant label je authority`, `NetworkPolicy vyrieši všetko`, `cluster per tenant vyrieši application data bugs`, `shared observability je automaticky izolovaná` a `namespace delete = offboarding complete`.

## Glossary impact

Relevantné pojmy: tenant subject, platform/business/infrastructure tenant, isolation profile, tenant identity propagation, trusted namespace binding, delegated controller identity, confused deputy, GitOps tenant lockdown, control-plane fairness, data/observability tenancy, tenant migration, residual scan a multi-tenancy acceptance verdict.

## Primárne zdroje

- [Kubernetes — Multi-tenancy](https://kubernetes.io/docs/concepts/security/multi-tenancy/)
- [Kubernetes — RBAC good practices](https://kubernetes.io/docs/concepts/security/rbac-good-practices/)
- [Kubernetes — Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Flux — Multi-tenancy](https://fluxcd.io/flux/installation/configuration/multitenancy/)
- [Flux — Security best practices](https://fluxcd.io/flux/security/best-practices/)
- [Argo CD — Projects](https://argo-cd.readthedocs.io/en/stable/user-guide/projects/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Guardrails](guardrails.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Keycloak architecture a responsibility boundary →](../17-keycloak-and-identity-platform/keycloak-architecture-and-responsibility-boundary.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
