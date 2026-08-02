# Keycloak Operator a Kubernetes deployment

Keycloak Operator nie je generátor jedného Deploymentu. Sleduje `Keycloak` Custom Resource, prekladá first-class fields a `additionalOptions` do server configuration, vytvára a vlastní workload, Services, Secrets references, ingress/route podľa configuration a status/conditions. Kubernetes `spec` je desired state, ale business-ready Keycloak vznikne až po successful reconciliation, Pod rollout-e, database/cache initialization, hostname/TLS routing a protocol journey. `kubectl apply` success preto nepreukazuje, že Operator prijal všetky fields, custom image je compatible alebo user login funguje.

Najčastejší incident vznikne pri ownership konflikte. Platform tím ručne patchne Operator-managed StatefulSet/Deployment alebo Service, Operator ho pri ďalšom reconcile vráti. Druhý incident vznikne, keď sa first-class setting zadá cez `spec.env`; Operator ho nepoužije pri svojej reconcile logike, hoci Keycloak process environment ho môže vidieť. Status môže potom opisovať inú topology než runtime process.

## 1. Dominantný CR-to-runtime lifecycle

```text
platform a identity deployment intent
→ exact CRD/Operator version generation
→ Keycloak CR generation a field ownership
→ referenced Secrets/ConfigMaps/custom image
→ Operator validation a reconciliation
→ managed Kubernetes resources
→ scheduling, rollout a Pod startup
→ Keycloak build/runtime configuration resolution
→ database/cache/hostname/TLS initialization
→ status conditions a management readiness
→ protocol/business acceptance
→ second reconcile, drift a upgrade closure
```

Každá šípka má vlastnú failure boundary. API server môže prijať CR s fieldom, ktorý starší Operator nevie spracovať. Operator môže vytvoriť Pods, ale custom image nemá optimized build. Pods môžu byť Ready, ale ingress zverejňuje admin endpointy. `status.ready=true` je platform evidence, nie proof konkrétneho realm/client flowu.

## 2. Exact Operator deployment subject

```yaml
operatorDeploymentSubject:
  cluster:
    uid: 27c7...
    version: v1.34.1
    namespace: identity-prod
  operator:
    deploymentUid: 52d1...
    image: quay.io/keycloak/keycloak-operator@sha256:4c82...
    version: 26.7.0
    crdGeneration: keycloak-crd-v2beta1-41
    olmCsv: keycloak-operator.v26.7.0
  keycloakCr:
    apiVersion: k8s.keycloak.org/v2beta1
    name: atlas-keycloak
    uid: 6ae4...
    generation: 28
    resourceVersion: "9188221"
    specHash: sha256:8a9f...
  runtimeImage:
    image: registry.atlas.example/identity/keycloak@sha256:6a91...
    optimizedBuildGeneration: kc-build-41
  dependencies:
    dbSecretUid: 41de...
    tlsSecretUid: 9b20...
    truststoreSecretUid: 77a1...
    hostname: https://sso.atlas.example
  managedWorkload:
    revision: 28
    replicas: 4
    podUids: [a1..., b2..., c3..., d4...]
  operation:
    reconcileId: kc-reconcile-1902
```

Bez CR generation a Operator/CRD version sa status nedá interpretovať. Bez Secret UID/resourceVersion nevieme, či rollout načítal successor credential. Bez runtime image digest sa custom-image behavior iba odhaduje. Bez managed workload revision sa manual patch môže zameniť za Operator-applied state.

## 3. Operator installation a CRD ownership

Operator sa môže inštalovať cez OLM alebo manifests podľa supported guide. OLM riadi Subscription, InstallPlan a ClusterServiceVersion. CRD upgrade compatibility je critical: nový CR môže používať fields, ktoré staršia CRD/Operator generation nepozná.

```bash
kubectl get crd keycloaks.k8s.keycloak.org -o yaml
kubectl -n keycloak-operator get deployment,subscription,csv,installplan
kubectl -n keycloak-operator get pods -o wide
```

Tieto outputy preukazujú installed objects. Nepreukazujú, že Operator watches intended namespace alebo že CR reconcile úspešne skončil.

Operator service account potrebuje cluster/namespace permissions podľa installation modelu. Cluster-admin je installation capability, nie runtime identity pre každú operation. RBAC review oddeľuje CRD installation, namespace reconcile a Secret access.

## 4. Basic `Keycloak` CR

```yaml
apiVersion: k8s.keycloak.org/v2beta1
kind: Keycloak
metadata:
  name: atlas-keycloak
  namespace: identity-prod
spec:
  instances: 4
  image: registry.atlas.example/identity/keycloak@sha256:6a91...
  db:
    vendor: postgres
    host: keycloak-db.cluster-7.internal
    database: keycloak
    schema: identity
    usernameSecret:
      name: keycloak-db
      key: username
    passwordSecret:
      name: keycloak-db
      key: password
    poolInitialSize: 10
    poolMinSize: 20
    poolMaxSize: 60
  hostname:
    hostname: https://sso.atlas.example
    admin: https://sso-admin.atlas.example
    backchannelDynamic: true
  http:
    tlsSecret: keycloak-tls
  ingress:
    enabled: false
```

`instances` je desired replica count, nie automatic HA proof. External database, routing, TLS, cache topology a scheduling musia byť samostatne configured. `ingress.enabled=false` je často vhodné, ak platform vytvára vlastný Gateway/Ingress s admin/public isolation.

## 5. First-class fields, `additionalOptions` a `spec.env`

Operator CR má first-class fields pre db, hostname, HTTP/TLS, features, transaction, resources, scheduling, management a ďalšie settings. Expert/dynamic provider options sa zadávajú cez `additionalOptions`.

```yaml
spec:
  additionalOptions:
    - name: spi-connections-http-client--default--connection-pool-size
      value: "200"
    - name: cache-embedded-sessions-max-count
      value: "15000"
```

Sensitive value môže byť Secret reference. `spec.env` je určený pre custom environment variables, ale Operator reconcile logic first-class settings z `spec.env` nečíta. Nepoužívaj `KC_HOSTNAME`, `KC_HTTP_ENABLED` alebo podobnú duplicate configuration cez `spec.env`, ak existuje CR field.

```text
first-class CR field
→ Operator pozná semantics a vie vytvoriť dependent resources/status

additionalOptions
→ server option passthrough, Operator pozná len name/value

spec.env
→ raw process environment bez Operator semantic ownershipu
```

Duplicated sources môžu vytvoriť drift medzi stored CR, generated resources a runtime effective config.

## 6. Custom image a optimized build

Custom providers, JDBC drivers alebo themes vyžadujú custom image. Operator očakáva production-compatible optimized image s build-time options už aplikovanými.

```Dockerfile
FROM quay.io/keycloak/keycloak:26.7.0 AS builder
ENV KC_DB=postgres
ENV KC_HEALTH_ENABLED=true
ENV KC_METRICS_ENABLED=true
COPY --chown=keycloak:keycloak providers/ /opt/keycloak/providers/
RUN /opt/keycloak/bin/kc.sh build

FROM quay.io/keycloak/keycloak:26.7.0
COPY --from=builder /opt/keycloak/ /opt/keycloak/
ENTRYPOINT ["/opt/keycloak/bin/kc.sh"]
```

Tag nie je immutable subject; CR má používať digest. Operator nevie, ktoré build-time options sú baked into image. Ak management TLS alebo port vznikne iba custom image configom, Operator probe assumptions môžu byť nesprávne. First-class `tlsSecret`, `httpManagement` a CR settings majú prednosť pre Operator-aware behavior.

## 7. Secrets a rollout generation

CR referuje Kubernetes Secrets pre database credentials, TLS, truststores a ďalšie values. Secret update nemusí automaticky znamenať runtime reload pre každý subsystem. Operator môže triggernúť rollout iba pre watched/referenced changes podľa implementation contractu.

```text
Secret successor resourceVersion
→ Operator observes dependency
→ managed workload template hash changes alebo runtime reload
→ new Pods mount successor
→ wire/database/read-back acceptance
→ predecessor retirement
```

Acceptance nesleduje iba Secret content. Kontroluje Pod template revision, mounted file hash a actual TLS/database behavior. Secret data sa nesmie zobrazovať v status/events/logs.

## 8. Ingress a hostname boundary

Operator môže vytvoriť ingress podľa CR, ale oddelený admin hostname vyžaduje access restrictions, ktoré default CR ingress nemusí vedieť vyjadriť. Samotné `hostname.admin` nevytvorí osobitný restricted ingress a default ingress nemusí blokovať admin endpoints.

```text
Operator-managed default ingress
→ convenient basic route
→ nemusí podporiť public/admin split policy

platform-managed Gateway/Ingress
→ explicit public allowlist
→ admin network/auth policy
→ management port never public
```

Pri production split route často vypni Operator ingress a sprav routes samostatne. Status ingress URL nie je security isolation proof.

## 9. Scheduling a failure domains

Operator CR podporuje priority class, affinity, tolerations a topology spread constraints. Bez custom topology spread používa server Pods default spread naprieč zones a nodes na zlepšenie availability.

```yaml
spec:
  scheduling:
    priorityClassName: identity-critical
    topologySpreadConstraints:
      - maxSkew: 1
        topologyKey: topology.kubernetes.io/zone
        whenUnsatisfiable: DoNotSchedule
        labelSelector:
          matchLabels:
            app.kubernetes.io/managed-by: keycloak-operator
            app.kubernetes.io/component: server
      - maxSkew: 1
        topologyKey: kubernetes.io/hostname
        whenUnsatisfiable: DoNotSchedule
        labelSelector:
          matchLabels:
            app.kubernetes.io/component: server
```

Scheduling intent nepreukazuje actual placement. Read-back Pod node/zone a cache topology site/rack/machine identities. Príliš strict constraints môžu zablokovať rollout pri zone outage.

Realm import a update Jobs môžu dediť scheduling server Pods, ale restrictive policy môže Job urobiť unschedulable. `spec.import.scheduling` a `spec.update.scheduling` môžu mať odlišný contract.

## 10. Resources a JVM memory

Operator poskytuje default memory requests/limits, ale production sizing musí vychádzať z workloadu, sessions, caches, providers a database latency. CPU throttling predlžuje login/request latency a cluster rebalance. Memory limit ovplyvňuje JVM heap sizing a native/off-heap overhead.

```yaml
spec:
  resources:
    requests:
      cpu: "2"
      memory: 2Gi
    limits:
      cpu: "4"
      memory: 4Gi
```

OOMKilled Pod môže stratiť in-progress authentication/action state podľa cache modelu. Resource acceptance zahŕňa peak load, rolling update surge a zone failure capacity.

## 11. Probes a management interface

Operator používa management interface health endpoints pre startup/liveness/readiness. CR musí Operatorovi umožniť odvodiť correct scheme, port a trust. Custom image-only management TLS config môže spôsobiť, že Operator probe používa HTTP na HTTPS listener.

```yaml
spec:
  httpManagement:
    port: 9000
  http:
    tlsSecret: keycloak-tls
```

Pod Ready preukazuje health endpoint result, nie login/business journey. Startup probe musí tolerovať schema migration a cluster join. Liveness nesmie vytvárať restart loop pri transient dependency failure.

## 12. Truststores a service-account token

CR `truststores` načíta PEM alebo PKCS12 z Secret/ConfigMap. Kubernetes CA files môžu byť automaticky zahrnuté. `automountServiceAccountToken=false` znižuje Kubernetes credential exposure, ale zároveň vypne automatic Kubernetes CA trust discovery a nie je kompatibilné s features/providers, ktoré Kubernetes API/token potrebujú.

```yaml
spec:
  automountServiceAccountToken: false
  truststores:
    corporate:
      secret:
        name: corporate-ca
```

Decision musí byť explicitný. External Infinispan, Kubernetes service-account identity provider alebo custom provider môže potrebovať token/API trust.

## 13. Operator-managed resource ownership

Managed resources majú labels/owner references. Ručné editovanie Deployment/StatefulSet, Service, probes alebo env je drift a Operator ho môže prepísať.

```text
manual kubectl patch managed workload
→ temporary live change
→ next reconcile restores CR-derived state
```

Break-glass zmena sa robí cez CR alebo dočasným pozastavením ownershipu podľa documented procedure, s auditom a následnou reconciliation. GitOps controller a Operator nesmú byť concurrent writers toho istého managed child resource; GitOps vlastní CR, Operator vlastní descendants.

## 14. Reconcile a status conditions

```bash
kubectl -n identity-prod get keycloak atlas-keycloak -o yaml
kubectl -n identity-prod describe keycloak atlas-keycloak
kubectl -n identity-prod get events --sort-by=.lastTimestamp
```

`metadata.generation` sa zvýši pri spec change. `status.observedGeneration` alebo conditions musia ukazovať, či Operator spracoval successor generation. Condition `Ready`/`HasErrors` a status messages sú controller evidence.

```text
spec generation 28
→ observed generation 27
→ change ešte nie je reconciled

observed generation 28 + Ready
→ controller a health gate prešli
→ protocol/business acceptance stále samostatná
```

## 15. Rollout a update strategy

CR zmena, image digest alebo Secret dependency môže vytvoriť workload rollout. Sleduj predecessor/successor Pods, image digest, config hash, schema/cache compatibility a max unavailable/surge behavior podľa managed resource.

```text
CR generation
→ workload revision
→ Pod cohort rollout
→ management readiness
→ external route traffic
→ protocol canary
→ predecessor scale-down
```

Mixed version/build/config je dočasný state s explicitnou compatibility boundary. Operator success nepreukazuje, že database migration alebo custom provider je backward compatible.

## 16. Realm import CR a job semantics

Realm import je samostatná operation, nie continuous desired-state controller pre všetky realm resources. Import Job má input realm artifact, target Keycloak CR, credentials a completion status. Partial import alebo existing realm behavior musí byť explicitné.

```text
realm artifact hash
→ KeycloakRealmImport CR generation
→ Job Pod
→ Admin/API/import transaction
→ Job completion
→ realm/client/user read-back
```

Job `Complete` nepreukazuje every object/mapper/secret. Import retry môže naraziť na existing resources alebo duplicate external effects. Kapitola 16 Admin REST rieši canonical plan a idempotency.

## 17. Autoscaling

Keycloak CR workload možno škálovať HPA podľa supported target. Autoscaling mení database pool ceiling, cache topology a required zone-failure headroom.

```text
HPA scale-out
→ new Pods
→ database connections
→ cluster join a state transfer
→ traffic readiness
```

CPU metric môže reagovať neskoro pri database wait alebo external IdP latency. Min replicas musia pokryť Pod/zone failure a maintenance. Max replicas musia rešpektovať database connection budget.

## 18. NetworkPolicy a exposure

Operator nevytvára complete zero-trust network policy pre všetky dependencies. Platform musí explicitne povoliť:

```text
ingress proxy → Keycloak HTTP/HTTPS
monitoring → management port
Keycloak Pods ↔ Keycloak cluster transport
Keycloak → database
Keycloak → LDAP/SMTP/IdP/Infinispan/DNS
Operator → Kubernetes API a managed resources
```

Public access na Pod/Service management/admin/direct listener je forbidden. Egress allowlist musí počítať s certificate/OCSP/DNS a external IdP dependencies.

## 19. Backup a delete semantics

Delete `Keycloak` CR môže odstrániť managed Kubernetes resources, ale nemá automaticky vymazať external database. OwnerReferences a finalizers určujú child cleanup. Database, DNS, certificates, external Secrets a load balancer majú vlastný lifecycle.

Pred delete/recreate zachovaj CR UID/generation, status, image/config, external dependency IDs a database backup. Nový CR s rovnakým name má nový UID a môže vytvoriť inú workload identity.

## 20. Operator upgrade

Operator/CRD upgrade má tri subjects:

```text
CRD schema/storage generation
→ Operator controller binary
→ existing Keycloak CRs a managed workloads
```

OLM môže validovať CR compatibility pri install plan-e. Nové fields v CR môžu zabrániť downgrade staršieho Operatora. Upgrade controlleru nemusí automaticky upgrade-nuť Keycloak runtime image, ale reconcile behavior sa môže zmeniť.

Acceptance testuje existing CR no-op reconcile, planned spec update, Secret rotation a child-resource drift po Operator upgrade.

## 21. Incident `KC-PAY-75`

Atlas GitOps vlastnil `Keycloak` CR aj generated StatefulSet manifest. Operator a GitOps preto bojovali o env, probes a replicas. Platform patchla `KC_PROXY_HEADERS` priamo do child workloadu; Operator ho odstránil. Následne pridala rovnakú setting do `spec.env`, ale CR first-class hostname/ingress logic ju nevidela.

Custom image mala management interface iba na HTTPS 9000, no CR neobsahoval `tlsSecret`/management-aware settings. Operator probe použila HTTP a Pods ostali NotReady. Operátor ručne zmenil probe scheme, ale reconcile patch vrátil.

```text
multiple writers na managed child
→ oscillating drift

first-class setting cez spec.env
→ runtime/controller semantic mismatch

custom image hidden management TLS
→ Operator probe mismatch
```

Recovery nechala GitOps vlastniť iba CR/Secrets/routes, Operator descendants. Proxy/hostname/TLS sa presunuli do first-class fields alebo `additionalOptions`, custom image digest a build contract sa zdokumentovali a management TLS sa vyjadrila spôsobom, ktorý Operator pozná.

## 22. Evidence-preserving containment a recovery

Zachovaj CR/CRD/Operator versions a UIDs, CR generations/spec hashes, managed child owner refs a revisions, Operator logs/events, Secret resourceVersions, image digest/build provenance, scheduling/Pod placement, probe/management endpoints, network routes a protocol canary evidence.

Containment môže zastaviť GitOps writera na managed children, freeze-nuť CR updates, odobrať broken Pod cohort z trafficu a rollback-nuť CR generation. Recovery obnoví single-writer model, reconciles desired state a overí second reconcile bez driftu.

## 23. Acceptance matrix

Positive:

```text
CR generation apply
→ Operator observed generation
→ managed rollout
→ Pods ready
→ login/admin/token journey succeeds
```

Recovery:

```text
Pod/zone failure alebo Secret rotation
→ Operator/Kubernetes recreates successor
→ cache/database/routing converge
→ second journey succeeds
```

Forbidden:

```text
manual/GitOps mutation managed child
→ policy rejects alebo Operator restores s alertom

public default ingress exposes admin/management
→ route security gate rejects

mutable image tag alebo hidden build config
→ supply-chain/deployment gate rejects
```

Second-reconcile test znovu aplikuje unchanged CR a očakáva no child churn. Second-operator test vykoná controller upgrade a no-op reconcile plus controlled spec change.

## Kontrolné otázky

- Ktorý Operator, CRD, CR a image generation riadia deployment?
- Ktoré fields sú first-class, ktoré `additionalOptions` a ktoré raw env?
- Kto je jediný writer CR a kto owns managed children?
- Je custom image optimized a immutable digestom?
- Spúšťa Secret update rollout/reload, ktorý subsystem potrebuje?
- Sú public/admin/management routes oddelené mimo default ingress limitov?
- Zodpovedajú scheduling labels cache topology failure domains?
- Sú resource/HPA limity zosúladené s database pool a cache topology?
- Prešli Pod/zone loss, Secret rotation, Operator upgrade, drift a second-reconcile testy?

## Primárne zdroje

- [Keycloak Operator Installation](https://www.keycloak.org/operator/installation)
- [Keycloak Operator — Basic deployment](https://www.keycloak.org/operator/basic-deployment)
- [Keycloak Operator — Advanced configuration](https://www.keycloak.org/operator/advanced-configuration)
- [Keycloak Operator — Realm import](https://www.keycloak.org/operator/realm-import)
- [Keycloak — Deploying across multiple availability zones with the Operator](https://www.keycloak.org/high-availability/single-cluster/deploy-keycloak)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Infinispan caches, clustering a session behavior](infinispan-caches-clustering-session-behavior.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: High availability, multi-AZ a multi-cluster trade-offs →](high-availability-multi-az-multi-cluster-trade-offs.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
