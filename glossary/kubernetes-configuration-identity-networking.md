# Kubernetes configuration, identity and networking glossary entries

## Accepted condition — Gateway API

Route alebo Gateway status condition indikujúca, že zodpovedný controller prijal resource alebo jeho attachment k parentu podľa class, listener a policy pravidiel. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## BackendRef — Gateway API

Typed reference z Route rule na backend resource, typicky Kubernetes Service a port, spolu s voliteľnou weight alebo policy metadata. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## Bound ServiceAccount token

Časovo obmedzený ServiceAccount bearer token vytvorený cez TokenRequest API, typicky viazaný na audience a Pod/object identity a projected kubeletom do workloadu. Pozri [ServiceAccount](docs/09-kubernetes/serviceaccount.md).

## Cluster DNS — Kubernetes

Cluster add-on poskytujúci DNS records pre Services a vybrané Pod identities a forwardujúci non-cluster queries na upstream resolvery. Pozri [Cluster DNS](docs/09-kubernetes/cluster-dns.md).

## Cluster domain — Kubernetes

DNS suffix cluster-local service discovery namespace-u, často `cluster.local`, ale konfigurovateľný pri vytvorení clusteru. Pozri [Cluster DNS](docs/09-kubernetes/cluster-dns.md).

## ClusterIP

Stabilná virtuálna Service IP v cluster networku, ktorú Service dataplane mapuje na aktuálne EndpointSlice backendy. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## ClusterIP DNS record

A alebo AAAA record bežného Kubernetes Service-u, ktorý resolve-ne na Service ClusterIP, nie priamo na Pod IP adresy. Pozri [Cluster DNS](docs/09-kubernetes/cluster-dns.md).

## ConfigMap

Namespaced Kubernetes API objekt pre necitlivé UTF-8 alebo binary configuration dáta používané Podmi cez environment alebo mounted volumes. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Configuration checksum — Kubernetes

Deterministický hash configuration contentu vložený do Pod template metadata, aby jeho zmena vytvorila novú workload revision a explicitný rollout. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## CoreDNS

Bežná Kubernetes cluster DNS implementation a extensible DNS server konfigurovaný pluginmi pre Kubernetes records, caching, forwarding, health a ďalšie funkcie. Pozri [Cluster DNS](docs/09-kubernetes/cluster-dns.md).

## Default backend — Ingress

Backend Service použitý pre requests, ktoré nezodpovedajú žiadnemu host/path pravidlu Ingressu. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## Default ServiceAccount

ServiceAccount automaticky vytvorený v každom namespace a použitý Podom, ktorý nemá explicitné `serviceAccountName`; nemá byť zdieľanou privilegovanou workload identity. Pozri [ServiceAccount](docs/09-kubernetes/serviceaccount.md).

## DNS negative caching

Dočasné cache-ovanie odpovede, že DNS meno neexistuje alebo nemá požadovaný record, ktoré môže predĺžiť NXDOMAIN symptóm po neskoršom vytvorení Service-u. Pozri [Cluster DNS](docs/09-kubernetes/cluster-dns.md).

## DNS policy — Kubernetes

Pod-level pravidlo určujúce zdroj a spôsob resolver configuration, napríklad `ClusterFirst`, `Default`, `ClusterFirstWithHostNet` alebo `None`. Pozri [Cluster DNS](docs/09-kubernetes/cluster-dns.md).

## DNS search domain

Suffix v Pod `/etc/resolv.conf`, ktorý resolver pridáva ku krátkym menám pri service discovery, napríklad `<namespace>.svc.<cluster-domain>`. Pozri [Cluster DNS](docs/09-kubernetes/cluster-dns.md).

## DNS TCP fallback

Prechod DNS klienta z UDP na TCP, napríklad po truncated alebo veľkej odpovedi; firewall musí podľa potreby povoľovať oba transporty na porte 53. Pozri [Cluster DNS](docs/09-kubernetes/cluster-dns.md).

## `dnsConfig` — Kubernetes

Pod spec configuration dopĺňajúca alebo pri `dnsPolicy: None` definujúca nameservers, search domains a resolver options. Pozri [Cluster DNS](docs/09-kubernetes/cluster-dns.md).

## Endpoint readiness — Kubernetes

EndpointSlice condition signalizujúci, či je backend vhodný pre bežný Service traffic podľa Pod readiness a publication policy. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## EndpointSlice

Namespaced `discovery.k8s.io` object reprezentujúci časť backend endpointov Service-u vrátane addresses, ports, conditions a topology metadata. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## Environment injection — Kubernetes

Odovzdanie ConfigMap alebo Secret hodnoty do environmentu pri vytvorení container procesu; neskoršia zmena source objektu environment bežiaceho procesu nezmení. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## External secret provider

Systém mimo Kubernetes API, ktorý vydáva alebo uchováva citlivé hodnoty a sprístupňuje ich workloadu cez synchronizáciu, CSI projection alebo runtime fetch s workload identity. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## ExternalName Service

Kubernetes Service type poskytujúci DNS alias na external name bez bežného ClusterIP proxy a selector-based EndpointSlices. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## Gateway — Gateway API

Namespaced infrastructure resource definujúci traffic entry point, listeners, addresses, TLS a pravidlá pre pripojenie Routes. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## Gateway API

Kubernetes SIG Network API family s role-oriented modelom GatewayClass, Gateway a Routes pre extensible a portable service networking. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## GatewayClass

Cluster-scoped Gateway API resource vyberajúci controller implementation a class-level lifecycle pre Gateway objekty. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## Headless Service

Kubernetes Service s `clusterIP: None`, ktorého DNS typicky publikuje priamo endpoint addresses namiesto jednej virtuálnej ClusterIP. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## Headless Service DNS

A/AAAA alebo SRV records headless Service-u vracajúce priamo backend alebo per-Pod identities, pričom client nesie selection a failover zodpovednosť. Pozri [Cluster DNS](docs/09-kubernetes/cluster-dns.md).

## HTTPRoute

Gateway API Route resource pre HTTP routing cez host, path, header alebo query matching, backend references, traffic weights a filters. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## ImagePullSecret

Kubernetes Secret reference používaná kubeletom alebo container runtime pri autentifikovanom image pull-e; nejde o application ani ServiceAccount API credential. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md) a [ServiceAccount](docs/09-kubernetes/serviceaccount.md).

## Immutable ConfigMap alebo Secret

ConfigMap alebo Secret s `immutable: true`, ktorý nemožno in-place meniť a vyžaduje nový versioned object a consumer rollout. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Ingress

Stable Kubernetes API resource pre HTTP/HTTPS host a path routing k Services, ktorý potrebuje samostatný Ingress controller a dataplane. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## IngressClass

Cluster-scoped resource určujúci, ktorý Ingress controller a class parameters spracúvajú konkrétne Ingress objekty. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## Ingress controller

Controller a dataplane integration sledujúca Ingress resources a konfiguruje reverse proxy, load balancer alebo inú implementation. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## Internal traffic policy — Service

Service policy ovplyvňujúca výber cluster-wide alebo node-local backendov pre traffic prichádzajúci z clusteru. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## Listener — Gateway API

Port, protocol, hostname, TLS a allowed-route boundary definovaná na Gateway resourci. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## LoadBalancer Service

Kubernetes Service type, ktorý prostredníctvom cloud alebo platform controlleru žiada external alebo internal load balancer a publikuje jeho address v status-e. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## NodeLocal DNSCache

Voliteľná node-local DNS caching vrstva, typicky nasadená ako DaemonSet, ktorá znižuje latency a pressure na central cluster DNS za cenu ďalšej per-node failure a cache vrstvy. Pozri [Cluster DNS](docs/09-kubernetes/cluster-dns.md).

## NodePort

Service type publikujúci port na eligible Node addresses a smerujúci traffic cez Service dataplane na backend endpoints. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## `ndots`

Resolver option určujúca, koľko bodiek musí meno obsahovať, aby sa najprv považovalo za absolute; vysoká hodnota môže znásobiť search-domain DNS queries. Pozri [Cluster DNS](docs/09-kubernetes/cluster-dns.md).

## ParentRef — Gateway API

Reference z Route na Gateway, listener alebo iný supported parent, ku ktorému sa Route pokúša pripojiť. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## PathType — Ingress

Ingress field určujúci semantics HTTP path matching-u ako `Exact`, `Prefix` alebo `ImplementationSpecific`. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## Projected configuration update

Kubelet-driven aktualizácia ConfigMap alebo Secret volume projection s eventual sync semantics; application musí podporovať reload a `subPath` mount zvyčajne aktualizáciu nedostane. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Projected ServiceAccount token

ServiceAccount token vložený do projected volume s explicitnou audience, expiration a kubelet rotation semantics. Pozri [ServiceAccount](docs/09-kubernetes/serviceaccount.md).

## ReferenceGrant

Gateway API object vytvorený v namespace referencovaného resource-u, ktorý explicitne povoľuje vybraným Routes z iného namespace cross-namespace reference. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## ResolvedRefs condition — Gateway API

Route status condition indikujúca, či controller úspešne vyriešil backend, Secret a ďalšie references vrátane cross-namespace permission. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## Resolver forwarding loop

DNS failure, pri ktorom cluster DNS forwarduje query na Node stub resolver a ten ju pošle späť na cluster DNS, často pre nesprávny kubelet `resolvConf`. Pozri [Cluster DNS](docs/09-kubernetes/cluster-dns.md).

## Route attachment — Gateway API

Proces, ktorým Route po splnení `parentRefs`, listener `allowedRoutes`, hostname/protocol a reference pravidiel začne byť prijatá a programovaná controllerom. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## Secret — Kubernetes

Namespaced API objekt pre citlivé bytes alebo strings, ktorého base64 reprezentácia nie je encryption a vyžaduje RBAC, encryption-at-rest, audit a bezpečný consumer lifecycle. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Secret encryption at rest

API server configuration šifrujúca persisted Secret payloady pred uložením do etcd; nerieši disclosure cez API, Node, Pod memory, logs alebo kompromitovanú workload identity. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Secret rotation

Riadený lifecycle vytvorenia nového credentialu, distribúcie a rollout-u consumerov, overlap/verification, revocation starého credentialu a cleanup starých copies. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Selectorless Service

Service bez `spec.selector`, ktorého backend EndpointSlices spravuje operator alebo iný explicitný owner, často pre external alebo manually discovered endpoints. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## Service — Kubernetes

Namespaced API contract poskytujúci stabilné meno, virtual address a port model pre dynamickú backend population reprezentovanú EndpointSlices. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## ServiceAccount

Namespaced non-human Kubernetes identity používaná Podmi a automation; permissions získava oddelene cez RBAC alebo inú authorization policy. Pozri [ServiceAccount](docs/09-kubernetes/serviceaccount.md).

## ServiceAccount token audience

Identifikátor intended recipienta tokenu, ktorý zabraňuje použitiu tokenu vydaného pre jednu službu voči inému verifierovi. Pozri [ServiceAccount](docs/09-kubernetes/serviceaccount.md).

## ServiceAccount username

Canonical authenticated identity `system:serviceaccount:<namespace>:<name>` používaná v authorization a audit logoch. Pozri [ServiceAccount](docs/09-kubernetes/serviceaccount.md).

## Service dataplane

Node alebo network-plugin mechanizmus implementujúci Service virtual IP, backend selection a packet forwarding podľa EndpointSlices. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## Service FQDN

Plné cluster-local DNS meno Service-u v tvare `<service>.<namespace>.svc.<cluster-domain>`. Pozri [Cluster DNS](docs/09-kubernetes/cluster-dns.md).

## Service port

Port publikovaný Kubernetes Service contractom pre klientov, odlišný od backend `targetPort`. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## Service selector

Label selector, podľa ktorého EndpointSlice controller odvodzuje backend Pods pre selector-based Service. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## Session affinity — Service

Service behavior preferujúci rovnaký backend pre klienta podľa ClientIP a timeoutu; nie je náhradou durable session storage. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## SRV record — Kubernetes DNS

DNS record vytvorený pre pomenovaný Service port, ktorý publikuje protocol, port a target service alebo per-endpoint hostname. Pozri [Cluster DNS](docs/09-kubernetes/cluster-dns.md).

## `subPath` update limitation

Kubernetes volume-mount hranica, pri ktorej ConfigMap alebo Secret pripojený cez `subPath` typicky nedostáva priebežné projection updates. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## `targetPort` — Service

Port alebo pomenovaný Pod container port, na ktorý Service dataplane smeruje traffic z publikovaného Service `port`. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## TLS Secret

Kubernetes Secret typu `kubernetes.io/tls`, typicky obsahujúci `tls.crt` a `tls.key` pre controller alebo workload; celý certificate trust a rotation contract zostáva zodpovednosťou consumer workflowu. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## TokenRequest

Kubernetes API subresource/mechanizmus na vydanie krátkodobého ServiceAccount tokenu s audience a expiration namiesto statického long-lived token Secretu. Pozri [ServiceAccount](docs/09-kubernetes/serviceaccount.md).

## Topology-aware routing — Service

Service routing model využívajúci EndpointSlice zone/topology metadata na preferenciu bližších endpointov pri zachovaní dostupnosti a správnej capacity distribution. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## Traffic splitting — Gateway API

Rozdelenie Route trafficu medzi viac backendRefs podľa weights, používané napríklad pre canary alebo migration rollout. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## Volume projection — Kubernetes configuration

Kubeletom materializované files z ConfigMapu, Secretu, ServiceAccount tokenu alebo ďalších sources v Pod mount namespace. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Workload identity — Kubernetes

Non-human identity workloadu, typicky reprezentovaná ServiceAccountom a krátkodobým tokenom alebo federovaným external credentialom. Pozri [ServiceAccount](docs/09-kubernetes/serviceaccount.md).

## Workload identity federation

Výmena ServiceAccount OIDC tokenu za krátkodobý external cloud alebo service credential podľa issuer, audience, subject a trust-policy podmienok. Pozri [ServiceAccount](docs/09-kubernetes/serviceaccount.md).

## `automountServiceAccountToken`

ServiceAccount alebo Pod setting určujúci, či kubelet automaticky pripojí štandardný ServiceAccount credential projection do Podu. Pozri [ServiceAccount](docs/09-kubernetes/serviceaccount.md).
