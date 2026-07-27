# Kubernetes health, placement, autoscaling and RBAC glossary entries

## Admission-to-authorization boundary

Prechod medzi úspešným authorization verdictom a admission kontrolami, ktoré ešte môžu request odmietnuť alebo mutovať. RBAC allow preto nie je dôkaz runtime úspechu. Pozri [RBAC](../docs/09-kubernetes/rbac.md).

## Affinity population subject

Exact množina existujúcich Podov vybraná label a namespace selectorom pre required/preferred Pod affinity alebo anti-affinity výpočet. Pozri [Taints, tolerations, affinity a topology](../docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Aggregation generation — Kubernetes RBAC

Versionovaná množina ClusterRoles a rules zahrnutých do agregovaného ClusterRole-u; môže zmeniť effective permissions bez zmeny bindingu. Pozri [RBAC](../docs/09-kubernetes/rbac.md).

## Autoscaling acceptance verdict

Verdikt, že current metric generation, recommendation, scale write, Pod/Node realization a downstream/business outcome zodpovedajú reviewed scaling contractu. Pozri [HPA a autoscaling](../docs/09-kubernetes/hpa-autoscaling.md).

## Autoscaling control subject

Súvislá identita HPA UID/generation, scale target UID/generation, metric definition, eligible Pod cohort, recommendation, behavior policy a scale-field ownera. Pozri [HPA a autoscaling](../docs/09-kubernetes/hpa-autoscaling.md).

## Autoscaling observation matrix

Mapa evidence cez metric source, API adapter, cohort, recommendation, scale subresource, Deployment/Pod/Node realization, readiness, downstream a business SLO. Pozri [HPA a autoscaling](../docs/09-kubernetes/hpa-autoscaling.md).

## Autoscaling reaction time

Čas od zmeny business demandu cez metric collection, HPA reconcile, scale write, scheduling, Node provisioning, image/startup/readiness až po novú serving capacity. Pozri [HPA a autoscaling](../docs/09-kubernetes/hpa-autoscaling.md).

## Authorization closure — Kubernetes

Incident closure dokazujúci odstránenie všetkých direct/group/aggregation permission paths, rotáciu uniknutých credentials a úspech allowed aj forbidden request testov. Pozri [RBAC](../docs/09-kubernetes/rbac.md).

## Authorization request subject

Exact authenticated user/groups/extras, verb, API group, resource/subresource, namespace, resourceName a request timestamp vyhodnocované authorizerom. Pozri [RBAC](../docs/09-kubernetes/rbac.md).

## Credential-after-revocation risk

Riziko, že credential alebo Secret prečítaný pred RBAC revokáciou zostáva použiteľný mimo Kubernetes API a vyžaduje provider-side revokáciu či rotáciu. Pozri [RBAC](../docs/09-kubernetes/rbac.md).

## Dedicated-pool contract

Kombinácia trusted Node labelu, Node taintu, workload toleration a required node affinity, ktorá drží cudzie workloady vonku a určený workload vo vnútri poolu. Pozri [Taints, tolerations, affinity a topology](../docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Downstream capacity envelope

Maximum connections, concurrency, throughput alebo rate, ktoré dependency bezpečne unesie pri replica scale-up/down bez amplification incidentu. Pozri [HPA a autoscaling](../docs/09-kubernetes/hpa-autoscaling.md).

## Effective RBAC graph

Union všetkých RoleBinding/ClusterRoleBinding paths, group memberships, referenced Roles/ClusterRoles a aggregated rules pre konkrétny request subject. Pozri [RBAC](../docs/09-kubernetes/rbac.md).

## Endpoint-readiness propagation

Asynchrónny chain z readiness attemptu cez container/Pod conditions a EndpointSlice conditions po Service alebo external load-balancer traffic eligibility. Pozri [Probes](../docs/09-kubernetes/probes.md).

## Eligible autoscaling cohort

Current Pody zahrnuté do metric výpočtu po zohľadnení target selectoru, missing metrics, readiness/startup a controller semantics. Pozri [HPA a autoscaling](../docs/09-kubernetes/hpa-autoscaling.md).

## Forbidden feedback outcome

Explicitne zakázaný autoscaling výsledok, napríklad retry metric vytvárajúca replica/connection storm, scale-down s duplicate work alebo cross-tenant metric manipulácia. Pozri [HPA a autoscaling](../docs/09-kubernetes/hpa-autoscaling.md).

## Forbidden-operation verification — RBAC

Aktívny test, že subject po recovery nevie vykonať Secrets, exec, proxy, workload-create, RBAC-management alebo cluster-wide operations mimo schváleného contractu. Pozri [RBAC](../docs/09-kubernetes/rbac.md).

## Group-derived permission

Authorization path udelená členstvom subjectu v identity group-e, nie explicitným bindingom na jeho user alebo ServiceAccount meno. Pozri [RBAC](../docs/09-kubernetes/rbac.md).

## Health-handler observation boundary

Presná perspective a path handlera, napríklad kubelet HTTP proti Pod IP alebo exec command v containeri; nie je totožná s external client pathom. Pozri [Probes](../docs/09-kubernetes/probes.md).

## Health verification subject

Pod UID, container ID/restart generation, probe configuration, kubelet/Node, attempt sequence, Pod/EndpointSlice conditions a client/business outcome hodnotené ako jeden chain. Pozri [Probes](../docs/09-kubernetes/probes.md).

## HPA behavior generation

Versionovaná scale-up/scale-down tolerance, stabilization a rate-policy konfigurácia použitá pri prechode z recommendation na scale action. Pozri [HPA a autoscaling](../docs/09-kubernetes/hpa-autoscaling.md).

## HPA metric contract

Presná metrika vrátane units, source, labels, tenant scope, query, aggregation window, freshness, missing-data semantics a očakávaného response na replica change. Pozri [HPA a autoscaling](../docs/09-kubernetes/hpa-autoscaling.md).

## Indirect workload capability

Autorita získaná cez permission vytvoriť alebo meniť Pod/Deployment/Job, napríklad použitie silnejšej ServiceAccount, mounted Secretu, internal networku alebo runtime fields. Pozri [RBAC](../docs/09-kubernetes/rbac.md).

## Liveness recovery contract

Tvrdenie, že konkrétny local failure je detegovaný liveness probe a restart containeru má realisticky odstrániť jeho príčinu. Pozri [Probes](../docs/09-kubernetes/probes.md).

## Metric provenance and freshness — autoscaling

Evidence spájajúca observed value so source-om, query/labels, adapter generation, collection timestampom, aggregation window a tenant/workload subjectom. Pozri [HPA a autoscaling](../docs/09-kubernetes/hpa-autoscaling.md).

## Multi-loop ownership

Rozdelenie autoritatívnych fields a signals medzi HPA, VPA, Node autoscaler, GitOps a workload controller tak, aby loops nebojovali alebo neoscilovali. Pozri [HPA a autoscaling](../docs/09-kubernetes/hpa-autoscaling.md).

## Node-label generation

Versionovaná množina security, pool a topology labels na konkrétnom Node UID alebo node-pool template-e. Pozri [Taints, tolerations, affinity a topology](../docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## NoExecute failover contract

Chain od Node condition/taintu cez toleration window, eviction, replacement, storage/network reattachment a application fencing po obnovenie služby. Pozri [Taints, tolerations, affinity a topology](../docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Per-metric HPA recommendation

Desired replica count vypočítaná pre jednu Resource, ContainerResource, Pods, Object alebo External metric pred kombináciou viacerých metrics a behavior policy. Pozri [HPA a autoscaling](../docs/09-kubernetes/hpa-autoscaling.md).

## Permission path — Kubernetes RBAC

Jedna konkrétna cesta `subject/group → binding → roleRef → resolved rule → request match`, ktorá prispieva do additive allow verdictu. Pozri [RBAC](../docs/09-kubernetes/rbac.md).

## Placement acceptance verdict

Verdikt, že desired Pody sú schedulovateľné, ready/serving cohort má požadované failure-domain rozloženie a workload ani neželaný tenant neprekročili dedicated-pool boundary. Pozri [Taints, tolerations, affinity a topology](../docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Placement drift

Rozdiel medzi current placement intentom a labels/taints/topology stavom bežiaceho Podu alebo Node-u, ktorý sa môže prejaviť až pri replacement-e pre `IgnoredDuringExecution`. Pozri [Taints, tolerations, affinity a topology](../docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Placement generation

Resolved Pod placement contract obsahujúci nodeSelector/affinity, tolerations, Pod affinity/anti-affinity, topology spread a relevantné scheduler/storage constraints. Pozri [Taints, tolerations, affinity a topology](../docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Placement observation matrix

Mapa evidence cez Pod generation, scheduler profile, trusted Node labels/taints, population selectors, eligible domains, skew, PVC topology, Events, binding a ready endpoint distribution. Pozri [Taints, tolerations, affinity a topology](../docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Probe attempt sequence

Časovo zoradená množina probe pokusov vrátane handlera, pathu, latency, timeoutu, success/failure a threshold state-u pre jeden container generation. Pozri [Probes](../docs/09-kubernetes/probes.md).

## Probe evidence-preservation boundary

Logs, previous-container output, Pod/EndpointSlice YAML, kubelet Events, metrics a traces, ktoré sa musia zachovať pred restartom alebo zmenou probe policy. Pozri [Probes](../docs/09-kubernetes/probes.md).

## Probe execution subject

Konkrétny kubelet, Node, Pod UID, container ID, probe type, handler a timing generation vykonávajúce jeden health attempt. Pozri [Probes](../docs/09-kubernetes/probes.md).

## Probe generation

Versionovaná startup/liveness/readiness konfigurácia vrátane handlera, port/pathu, timing fields, thresholds a termination semantics viazaná na Pod template generation. Pozri [Probes](../docs/09-kubernetes/probes.md).

## Probe hysteresis

Stavový mechanizmus, ktorý z viacerých success/failure attempts a thresholdov vytvorí finálny startup, liveness alebo readiness verdict namiesto reakcie na jediný sample. Pozri [Probes](../docs/09-kubernetes/probes.md).

## Readiness eligibility verdict

Rozhodnutie, či konkrétny Pod/container generation smie prijímať novú prácu; propaguje sa cez Pod conditions a EndpointSlice, ale nie je business SLO. Pozri [Probes](../docs/09-kubernetes/probes.md).

## Readiness-gate generation

Versionovaná custom Pod condition, jej controller owner, observed generation, freshness a recovery behavior používané ako ďalšia traffic-eligibility podmienka. Pozri [Probes](../docs/09-kubernetes/probes.md).

## Replacement feasibility

Dôkaz, že current placement contract zostane splniteľný po Node loss, rollout surge, HPA scale-up alebo Pod replacement-e, nie iba pre už bežiacu cohortu. Pozri [Taints, tolerations, affinity a topology](../docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Resolved ClusterRole rules

Effective ruleset ClusterRole-u po aplikovaní aggregation rule a všetkých matching member ClusterRoles. Pozri [RBAC](../docs/09-kubernetes/rbac.md).

## Restart amplification

Pozitívna failure slučka, v ktorej liveness restarty opakujú bootstrap, connection pool, cache warm-up alebo dependency load a zhoršujú pôvodný incident. Pozri [Probes](../docs/09-kubernetes/probes.md).

## Retry-amplified metric

Autoscaling signal, ktorý zahŕňa interné retries alebo duplicate events, takže dependency failure vyzerá ako nový business demand a scale-out incident zosilní. Pozri [HPA a autoscaling](../docs/09-kubernetes/hpa-autoscaling.md).

## Scale-field ownership

Explicitné určenie, ktorý controller smie zapisovať live replica count a ako GitOps/HPA bootstrap a runtime desired state spolupracujú bez reconciliation fightu. Pozri [HPA a autoscaling](../docs/09-kubernetes/hpa-autoscaling.md).

## Scaling saturation verdict

Stav, keď HPA dosiahlo max/rate/capacity boundary a ďalší demand už nevie premeniť na serving capacity; vyžaduje load shedding, alert alebo remediation. Pozri [HPA a autoscaling](../docs/09-kubernetes/hpa-autoscaling.md).

## Serving-capacity realization

Prechod z desired replica count cez controller, scheduling, Node provisioning, image/startup/readiness a traffic propagation na Pody, ktoré reálne obsluhujú requests. Pozri [HPA a autoscaling](../docs/09-kubernetes/hpa-autoscaling.md).

## Startup verdict

Verdikt, že konkrétny container generation dokončil bounded inicializáciu a kubelet môže začať liveness/readiness hodnotenie. Pozri [Probes](../docs/09-kubernetes/probes.md).

## Subject-bound authorization verification

Overenie exact allowed a forbidden requests pre current credential, subject/groups, binding/aggregation generation a následného admission/runtime/business outcome-u. Pozri [RBAC](../docs/09-kubernetes/rbac.md).

## Taint-repulsion verdict

Rozhodnutie, či incoming Pod toleruje všetky relevantné Node taints pre daný effect; toleration sama Node nevyberá. Pozri [Taints, tolerations, affinity a topology](../docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Topology-domain inventory

Exact množina eligible Node UIDs a hodnôt `topologyKey`, ktoré tvoria domains pre jeden incoming Pod a current scheduler/placement generation. Pozri [Taints, tolerations, affinity a topology](../docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Topology-skew subject

Matching Pod population, eligible domains, current per-domain counts, `maxSkew`, `whenUnsatisfiable` a hypotetický incoming placement hodnotené ako jeden calculation subject. Pozri [Taints, tolerations, affinity a topology](../docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Trusted Node label

Placement label, ktorého key/value, owner, mutation path a node-pool generation sú chránené tak, aby workload nemohol falšovať compliance alebo dedicated-pool eligibility. Pozri [Taints, tolerations, affinity a topology](../docs/09-kubernetes/taints-tolerations-affinity-topology.md).