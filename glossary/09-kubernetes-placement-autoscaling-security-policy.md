# Kubernetes placement, autoscaling and security glossary entries

## Additive authorization — Kubernetes RBAC

Authorization model, v ktorom sa výsledné oprávnenia skladajú ako union všetkých matching RoleBindings a ClusterRoleBindings; prísnejšia rola neodoberie permission udelenú iným bindingom. Pozri [RBAC](docs/09-kubernetes/rbac.md).

## Aggregated ClusterRole

ClusterRole, ktorej rules controller automaticky skladá z iných ClusterRoles označených matching aggregation labels. Pozri [RBAC](docs/09-kubernetes/rbac.md).

## AppArmor profile — Kubernetes

Host-level Linux Security Module profil obmedzujúci filesystem, capability, network a ďalšie operations container procesu podľa Node a runtime podpory. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## Autoscaling feedback loop

Nežiaduca alebo zámerná interakcia viacerých autoscaling controllers a metrics, pri ktorej zmena replicas, requests alebo Node capacity mení vstup ďalšej scaling slučky. Pozri [HPA a autoscaling](docs/09-kubernetes/hpa-autoscaling.md).

## Average utilization — HPA

Priemerná resource utilization cieľovej Pod population vyjadrená ako percento resource requestu, používaná napríklad pri CPU HPA. Pozri [HPA a autoscaling](docs/09-kubernetes/hpa-autoscaling.md).

## Baseline Pod Security Standard

Pod Security Standards profil blokujúci známe nebezpečné privilege escalations a host access pri širšej workload kompatibilite než profil Restricted. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## ClusterRole

Cluster-scoped Kubernetes RBAC ruleset pre cluster resources, non-resource URLs alebo reusable namespaced permissions. Pozri [RBAC](docs/09-kubernetes/rbac.md).

## ClusterRoleBinding

Cluster-scoped RBAC binding udeľujúci ClusterRole permissions subjects naprieč celým cluster scope-om. Pozri [RBAC](docs/09-kubernetes/rbac.md).

## Compute quota — Kubernetes

ResourceQuota limit agregovaných CPU, memory, ephemeral-storage alebo ďalších deklarovaných requests/limits v namespace. Pozri [ResourceQuota a LimitRange](docs/09-kubernetes/resourcequota-limitrange.md).

## Dedicated Node pool

Množina Nodes určená pre konkrétny workload alebo trust tier, typicky chránená kombináciou taintu, toleration, labelu a required node affinity. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Desired replica calculation — HPA

Výpočet odporúčaného replica countu založený približne na pomere aktuálnej a cieľovej metric hodnoty, následne upravený tolerance, missing metrics a behavior policy. Pozri [HPA a autoscaling](docs/09-kubernetes/hpa-autoscaling.md).

## `DoNotSchedule` — topology spread

Hard topology spread behavior, pri ktorom scheduler Pod nenaplánuje, ak by porušil deklarovaný `maxSkew` a ďalšie constraint pravidlá. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Event-driven autoscaling

Scaling model reagujúci na event-source alebo business metrics, napríklad queue backlog, často implementovaný ecosystem controllerom nad rámec core HPA. Pozri [HPA a autoscaling](docs/09-kubernetes/hpa-autoscaling.md).

## External metric — HPA

Metric pochádzajúca mimo Kubernetes object modelu, sprístupnená HPA cez external metrics API adapter. Pozri [HPA a autoscaling](docs/09-kubernetes/hpa-autoscaling.md).

## HPA tolerance

Mŕtve pásmo okolo cieľovej metric hodnoty, v ktorom HPA nemusí meniť replica count, aby obmedzil drobné oscillations. Pozri [HPA a autoscaling](docs/09-kubernetes/hpa-autoscaling.md).

## Horizontal Pod Autoscaler — HPA

Kubernetes API resource a controller automaticky meniaci replica count škálovateľného workloadu podľa resource, custom alebo external metrics. Pozri [HPA a autoscaling](docs/09-kubernetes/hpa-autoscaling.md).

## Kubernetes SecurityContext

Pod alebo container configuration definujúca runtime user/group identity, capabilities, privilege escalation, filesystem, seccomp a ďalšie security controls. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## LimitRange

Namespaced Kubernetes policy nastavujúca alebo validujúca per-container, per-Pod alebo per-PVC resource defaults, minimá, maximá a ratios. Pozri [ResourceQuota a LimitRange](docs/09-kubernetes/resourcequota-limitrange.md).

## `maxLimitRequestRatio`

LimitRange pravidlo obmedzujúce maximálny pomer resource limitu k requestu pre konkrétny resource. Pozri [ResourceQuota a LimitRange](docs/09-kubernetes/resourcequota-limitrange.md).

## `maxSkew` — topology spread

Maximálna povolená nerovnomernosť počtu matching Podov medzi topology domains podľa konkrétneho spread constraintu. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Metrics adapter — Kubernetes autoscaling

Component publikujúci custom alebo external metrics cez Kubernetes aggregated API pre HPA alebo ďalších consumers. Pozri [HPA a autoscaling](docs/09-kubernetes/hpa-autoscaling.md).

## `NoExecute` taint

Node taint effect blokujúci nové Pody bez matching toleration a schopný evictnuť už bežiace netolerujúce Pody. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## `NoSchedule` taint

Node taint effect zabraňujúci scheduleru umiestniť nový Pod bez matching toleration na daný Node. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Node affinity

Scheduling pravidlo vyberajúce alebo preferujúce Nodes podľa label expressions, hard alebo soft podľa použitého field-u. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Node autoscaling

Automatické pridávanie alebo odoberanie Node capacity podľa schedulovateľnosti a cluster demand modelu. Pozri [HPA a autoscaling](docs/09-kubernetes/hpa-autoscaling.md).

## Node label — placement

Key/value metadata na Node objekte používaná schedulerom pri nodeSelector, affinity a topology rozhodnutiach. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Object-count quota — Kubernetes

ResourceQuota limit počtu API objektov konkrétneho typu, napríklad Pods, Jobs, Secrets, PVCs alebo LoadBalancer Services. Pozri [ResourceQuota a LimitRange](docs/09-kubernetes/resourcequota-limitrange.md).

## Placement deadlock

Stav, keď kombinácia hard affinity, anti-affinity, taints, topology, storage alebo resource constraints nevytvára žiadny feasible Node. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Pod affinity

Scheduling pravidlo priťahujúce Pod do topology domain, kde už existujú matching Pody. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Pod anti-affinity

Scheduling pravidlo oddeľujúce Pod od topology domains obsahujúcich matching Pody, hard alebo soft podľa konfigurácie. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Pod Security Admission — PSA

Built-in Kubernetes admission controller vyhodnocujúci Pods podľa versionovaných Pod Security Standards a namespace režimov enforce, audit a warn. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## Pod Security Standards — PSS

Versionované Kubernetes security profily Privileged, Baseline a Restricted definujúce povolené Pod security fields a privilege model. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## Policy version pinning — Pod Security

Explicitné naviazanie Pod Security Admission režimu na konkrétnu Kubernetes minor policy verziu, aby cluster upgrade nezmenil enforcement bez testovaného rollout-u. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## `PreferNoSchedule` taint

Soft Node taint effect, ktorému sa scheduler pokúsi vyhnúť, ale pri nedostatku vhodných možností môže Pod na Node umiestniť. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Privileged container — Kubernetes

Container spustený s veľmi širokým host kernel, device a security-control prístupom; podľa mounts a namespaces môže byť prakticky host-root-equivalentný. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## Privileged namespace exception

Auditovaná namespace výnimka povoľujúca systémovým workloadom širšie Pod privileges, s obmedzeným RBAC, ownerom, scope-om a expiry. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## Quota admission

API admission kontrola odmietajúca create alebo update request, ktorý by prekročil ResourceQuota hard limit alebo nesplnil required quota fields. Pozri [ResourceQuota a LimitRange](docs/09-kubernetes/resourcequota-limitrange.md).

## Quota saturation

Stav, keď ResourceQuota `used` dosiahne alebo sa približuje k `hard`, takže nové Pody, Jobs, PVCs alebo iné objects nemôžu byť prijaté. Pozri [ResourceQuota a LimitRange](docs/09-kubernetes/resourcequota-limitrange.md).

## RBAC privilege escalation

Nepriame získanie širšej kontroly cez permissions ako workload creation, Secret read, exec/proxy, RBAC `bind`/`escalate`, impersonation alebo CSR approval. Pozri [RBAC](docs/09-kubernetes/rbac.md).

## RBAC subject

User, Group alebo ServiceAccount identita, ktorej RoleBinding alebo ClusterRoleBinding udeľuje permissions. Pozri [RBAC](docs/09-kubernetes/rbac.md).

## Read-only root filesystem — Kubernetes

Container security setting zakazujúci zápis do image root filesystemu a vyžadujúci explicitné writable mounts pre temp, cache alebo application state. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## ResourceQuota

Namespaced Kubernetes API objekt obmedzujúci agregované resource requests/limits, storage alebo počet API objektov. Pozri [ResourceQuota a LimitRange](docs/09-kubernetes/resourcequota-limitrange.md).

## Restricted Pod Security Standard

Najprísnejší built-in PSS profil pre bežné workloads, vyžadujúci non-root a obmedzený privilege/capability/seccomp model podľa versionovaného štandardu. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## Role — Kubernetes RBAC

Namespaced RBAC ruleset definujúci povolené verbs nad resources a subresources v konkrétnom namespace scope-e. Pozri [RBAC](docs/09-kubernetes/rbac.md).

## RoleBinding

Namespaced RBAC binding udeľujúci Role alebo ClusterRole rules subjects v namespace bindingu. Pozri [RBAC](docs/09-kubernetes/rbac.md).

## Scale-down stabilization — HPA

Časové okno, počas ktorého HPA zohľadňuje predchádzajúce odporúčania a tlmí príliš rýchle znižovanie replicas. Pozri [HPA a autoscaling](docs/09-kubernetes/hpa-autoscaling.md).

## Scale subresource — Kubernetes

Štandardizované API rozhranie vystavujúce desired a current replica informácie škálovateľného workloadu pre HPA a ďalších clients. Pozri [HPA a autoscaling](docs/09-kubernetes/hpa-autoscaling.md).

## `ScheduleAnyway` — topology spread

Soft topology spread behavior, pri ktorom scheduler môže Pod umiestniť aj pri porušení ideálneho skew a používa constraint pri scoring-u. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Seccomp profile — Kubernetes

Runtime syscall filter vybraný cez Pod alebo container security context, napríklad RuntimeDefault alebo Localhost. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## SELinux options — Kubernetes

SecurityContext fields nastavujúce SELinux label identity container procesu a volumes podľa host policy, runtime a storage podpory. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## Storage quota — Kubernetes

ResourceQuota limit agregovaných PVC requests, počtu claims alebo StorageClass-specific storage consumption v namespace. Pozri [ResourceQuota a LimitRange](docs/09-kubernetes/resourcequota-limitrange.md).

## SubjectAccessReview

Kubernetes authorization API request zisťujúci, či konkrétna identita smie vykonať zadanú akciu nad resource-om alebo URL. Pozri [RBAC](docs/09-kubernetes/rbac.md).

## Taint — Kubernetes

Key/value/effect značka na Node-e, ktorá odpudzuje Pody bez matching toleration pri scheduling-u alebo execution-e. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Toleration — Kubernetes

Pod rule povoľujúci workloadu tolerovať konkrétny Node taint; nepriťahuje Pod na tainted Node. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## `tolerationSeconds`

Čas, počas ktorého Pod toleruje matching `NoExecute` taint pred možnou eviction. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Topology domain — Kubernetes

Množina Nodes zdieľajúcich rovnakú hodnotu vybraného topology labelu, napríklad Node, zone, region alebo rack. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Topology spread constraint

Pod scheduling pravidlo riadiace maximálnu nerovnomernosť matching Pod population medzi topology domains. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Vertical Pod Autoscaler — VPA

Samostatne inštalovaný Kubernetes controller a API odporúčajúci alebo aplikujúci zmeny Pod resource requests podľa observed usage a policy. Pozri [HPA a autoscaling](docs/09-kubernetes/hpa-autoscaling.md).

## Wildcard permission — Kubernetes RBAC

RBAC pravidlo s `*` pre verbs, resources alebo API groups, ktoré zahŕňa aj budúce resources alebo capabilities pridané po upgrade. Pozri [RBAC](docs/09-kubernetes/rbac.md).

## `allowPrivilegeEscalation`

Container security setting riadiaci možnosť procesu získať nové privileges, na Linuxe typicky cez `no_new_privs` runtime mechanizmus. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## `fsGroup`

Pod security context group identity používaná pri ownership a access nastavení podporovaných mounted volumes. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## `nodeSelector`

Jednoduchý hard Pod placement constraint vyžadujúci, aby Node mal všetky uvedené label key/value páry. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## `resourceNames` — Kubernetes RBAC

RBAC rule field zužujúci vybrané permissions na explicitné object names, s limitmi pre create, list/watch a deletecollection semantics. Pozri [RBAC](docs/09-kubernetes/rbac.md).

## `runAsNonRoot`

SecurityContext guard požadujúci, aby container process nebežal s root UID; potrebuje kompatibilný image a runtime-resolvable user identity. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).
