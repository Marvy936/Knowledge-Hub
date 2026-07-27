# Kubernetes workload identity, Service routing and DNS glossary entries

## Workload identity lifecycle subject

Úplný subject spájajúci workload identity intent, ServiceAccount UID, Pod UID, token instance, audience, process-loaded credential, authorization policy, external federation a auditovaný operation outcome. Pozri [ServiceAccount](../docs/09-kubernetes/serviceaccount.md).

## ServiceAccount object identity

ServiceAccount identifikovaný clusterom, namespace-om, menom a object UID; delete/create s rovnakým menom vytvára nový lifecycle subject. Pozri [ServiceAccount](../docs/09-kubernetes/serviceaccount.md).

## Admitted workload identity

Effective `serviceAccountName`, token projection a identity-related Pod configuration po API defaulting, mutation a admission, nie iba source manifest. Pozri [ServiceAccount](../docs/09-kubernetes/serviceaccount.md).

## Bound token subject

Konkrétny ServiceAccount token identifikovaný issuerom, audience, expiry, object bindingom a bezpečným fingerprintom. Pozri [ServiceAccount](../docs/09-kubernetes/serviceaccount.md).

## Token audience boundary

Recipient restriction určujúca, pre ktorý verifier alebo service je token určený; platný token s nesprávnou audience musí byť odmietnutý. Pozri [ServiceAccount](../docs/09-kubernetes/serviceaccount.md).

## Object-bound credential

Credential, ktorého validity alebo trust je viazaná na lifecycle konkrétneho Kubernetes objektu, napríklad Podu alebo ServiceAccountu. Pozri [ServiceAccount](../docs/09-kubernetes/serviceaccount.md).

## Process-loaded token generation

Token instance, ktorú application process reálne používa; môže byť staršia než aktuálny token v projected volume. Pozri [ServiceAccount](../docs/09-kubernetes/serviceaccount.md).

## ServiceAccount authorization subject

Presný authorization request viažuci authenticated ServiceAccount username na verb, API group, resource, subresource, namespace a relevantnú RBAC generation. Pozri [ServiceAccount](../docs/09-kubernetes/serviceaccount.md).

## Federation trust-policy generation

Versionovaný external identity-provider contract určujúci akceptovaný issuer, audience, namespace, ServiceAccount subject a odvodenú external rolu. Pozri [ServiceAccount](../docs/09-kubernetes/serviceaccount.md).

## Derived credential subject

Krátkodobý cloud, Vault alebo iný external credential vydaný na základe workload identity, s vlastnou expiry, permissions, auditom a revocation lifecycle-om. Pozri [ServiceAccount](../docs/09-kubernetes/serviceaccount.md).

## Pod-create identity delegation boundary

Security boundary, pri ktorej právo vytvoriť Pod alebo controller s vybraným ServiceAccountom prakticky deleguje authority tejto workload identity. Pozri [ServiceAccount](../docs/09-kubernetes/serviceaccount.md).

## Identity operation outcome

Auditovaný výsledok konkrétnej API alebo external operácie vykonanej workload identity, nie iba dôkaz, že credential existoval. Pozri [ServiceAccount](../docs/09-kubernetes/serviceaccount.md).

## Service lifecycle subject

Úplný subject spájajúci Service UID/generation, VIP a port contract, EndpointSlice cohort, node dataplane generation, client flow, backend Pod UID a business request. Pozri [Service a EndpointSlice](../docs/09-kubernetes/service-endpointslice.md).

## Service contract generation

Versionovaný Service state zahŕňajúci type, ClusterIP/clusterIPs, selector, ports, targetPorts a traffic policies. Pozri [Service a EndpointSlice](../docs/09-kubernetes/service-endpointslice.md).

## Endpoint-cohort subject

Full union EndpointSlices pre jeden Service a generation, vrátane targetRef UIDs, addresses, ports, conditions, topology a ownership metadata. Pozri [Service a EndpointSlice](../docs/09-kubernetes/service-endpointslice.md).

## EndpointSlice ownership generation

Controller alebo custom owner a jeho versionovaný lifecycle pre creation, update a cleanup EndpointSlices. Pozri [Service a EndpointSlice](../docs/09-kubernetes/service-endpointslice.md).

## Endpoint target identity

Backend endpoint identifikovaný nielen IP adresou, ale aj targetRef UID, port, address family, Node a application generation. Pozri [Service a EndpointSlice](../docs/09-kubernetes/service-endpointslice.md).

## Endpoint condition lifecycle

Transition medzi endpoint states `ready`, `serving` a `terminating` spolu s dataplane propagation a connection-drain behaviorom. Pozri [Service a EndpointSlice](../docs/09-kubernetes/service-endpointslice.md).

## Named-port contract

Cross-revision contract, v ktorom Service `targetPort` name musí byť deklarovaný a reálne obsluhovaný každým accepted Pod backendom. Pozri [Service a EndpointSlice](../docs/09-kubernetes/service-endpointslice.md).

## Service dataplane generation

Versionovaný per-Node forwarding state implementujúci Service VIP, endpoint selection a NAT alebo ekvivalentné mapovanie. Pozri [Service a EndpointSlice](../docs/09-kubernetes/service-endpointslice.md).

## Client-Service flow subject

Presný request/connection path od client Podu a Node-u cez Service VIP a node dataplane ku konkrétnemu endpointu a reverse pathu. Pozri [Service a EndpointSlice](../docs/09-kubernetes/service-endpointslice.md).

## Local-endpoint coverage

Intersection Nodes prijímajúcich traffic s ready local endpointmi potrebná pre bezpečné `Local` traffic policies. Pozri [Service a EndpointSlice](../docs/09-kubernetes/service-endpointslice.md).

## Endpoint-drain generation

Versionovaný stav spájajúci readiness removal, EndpointSlice conditions, dataplane/LB propagation, existing connections a Pod termination. Pozri [Service a EndpointSlice](../docs/09-kubernetes/service-endpointslice.md).

## Edge route lifecycle subject

Úplný subject spájajúci Route/Ingress intent, class/controller, parent/listener, attachment, resolved references, programmed dataplane, DNS, certificate, backend a client request. Pozri [Ingress a Gateway API](../docs/09-kubernetes/ingress-gateway-api.md).

## Class-controller ownership

Contract, ktorým IngressClass alebo GatewayClass vyberá controller implementation a jej capability/lifecycle ownership. Pozri [Ingress a Gateway API](../docs/09-kubernetes/ingress-gateway-api.md).

## Gateway listener subject

Konkrétny Gateway UID, listener section, address, port, protocol, hostname, TLS a allowed-route boundary. Pozri [Ingress a Gateway API](../docs/09-kubernetes/ingress-gateway-api.md).

## Route attachment subject

Obojstranný parent/listener decision viažuci Route generation na parentRef, allowedRoutes, hostname/protocol intersection a controller acceptance. Pozri [Ingress a Gateway API](../docs/09-kubernetes/ingress-gateway-api.md).

## Route parent generation

Presná parent Gateway/listener generation, ku ktorej patria Route conditions a effective attachment. Pozri [Ingress a Gateway API](../docs/09-kubernetes/ingress-gateway-api.md).

## ReferenceGrant trust subject

Provider-owned cross-namespace permission identifikujúca source group/kind/namespace a target group/kind/name. Pozri [Ingress a Gateway API](../docs/09-kubernetes/ingress-gateway-api.md).

## Resolved route configuration

Controller-generated effective configuration po zlúčení Routes, listeners, references, policies, Services, EndpointSlices a certificates. Pozri [Ingress a Gateway API](../docs/09-kubernetes/ingress-gateway-api.md).

## Programmed dataplane generation

Konkrétna route/config generation načítaná edge proxy, load balancer alebo inou dataplane instance. Pozri [Ingress a Gateway API](../docs/09-kubernetes/ingress-gateway-api.md).

## Edge cohort subject

Množina active edge instances alebo load-balancer targets, ktoré musia používať rovnakú accepted route a certificate generation. Pozri [Ingress a Gateway API](../docs/09-kubernetes/ingress-gateway-api.md).

## DNS-address generation

Versionovaný vzťah medzi Ingress/Gateway address statusom, external DNS recordmi, TTL/cache a active load-balancer addresses. Pozri [Ingress a Gateway API](../docs/09-kubernetes/ingress-gateway-api.md).

## Loaded certificate subject

Certificate identity reálne načítaná konkrétnou edge instance, typicky identifikovaná SAN, serialom, expiry a config generation. Pozri [Ingress a Gateway API](../docs/09-kubernetes/ingress-gateway-api.md).

## Route conflict inventory

Full attached-route inventory pre overlapping hostname/path space vrátane controller conflict/precedence verdictov. Pozri [Ingress a Gateway API](../docs/09-kubernetes/ingress-gateway-api.md).

## Edge retry subject

Jeden client request a všetky edge-generated backend attempts, viazané na method, timeout, retry policy a application idempotency key. Pozri [Ingress a Gateway API](../docs/09-kubernetes/ingress-gateway-api.md).

## DNS lookup lifecycle subject

Úplný subject spájajúci exact query, Pod resolver generation, search expansion, DNS path, server/cache generation, answer, selected address, fresh connection a business request. Pozri [Cluster DNS](../docs/09-kubernetes/cluster-dns.md).

## Pod resolver generation

Actual resolver state v konkrétnom Pode odvodený z namespace-u, `dnsPolicy`, `dnsConfig`, kubelet a Node resolver configuration. Pozri [Cluster DNS](../docs/09-kubernetes/cluster-dns.md).

## Query expansion subject

Exact sequence DNS names vytvorená resolverom z pôvodného mena, search domains a `ndots` semantics. Pozri [Cluster DNS](../docs/09-kubernetes/cluster-dns.md).

## Cluster-DNS Service subject

`kube-dns` Service UID/ClusterIP, EndpointSlice cohort a node dataplane path, cez ktorý Pod query dosiahne DNS backend. Pozri [Cluster DNS](../docs/09-kubernetes/cluster-dns.md).

## CoreDNS loaded configuration

Corefile a plugin generation reálne načítaná konkrétnym CoreDNS processom, odlišná od samotnej ConfigMap resourceVersion. Pozri [Cluster DNS](../docs/09-kubernetes/cluster-dns.md).

## Kubernetes DNS watch generation

Service, EndpointSlice a namespace state, ktorý CoreDNS Kubernetes plugin reálne pozoruje vo svojom informer/cache lifecycle-e. Pozri [Cluster DNS](../docs/09-kubernetes/cluster-dns.md).

## NodeLocal DNS generation

Per-Node DNS cache agent, jeho configuration, cache a upstream state tvoriace samostatnú failure domain. Pozri [Cluster DNS](../docs/09-kubernetes/cluster-dns.md).

## Upstream forwarding subject

External alebo split-horizon DNS path identifikovaný CoreDNS forward rule, upstream resolverom, transportom, zone a response generation. Pozri [Cluster DNS](../docs/09-kubernetes/cluster-dns.md).

## Negative-cache generation

NXDOMAIN alebo iný negative DNS verdict uložený v konkrétnej cache vrstve s vlastným TTL a ownerom. Pozri [Cluster DNS](../docs/09-kubernetes/cluster-dns.md).

## DNS answer subject

Konkrétna DNS odpoveď identifikovaná query name/type, response code, answer set, TTL, server a observation time. Pozri [Cluster DNS](../docs/09-kubernetes/cluster-dns.md).

## Resolver-library cache subject

Application alebo runtime-level DNS cache s vlastnými TTL, negative-cache a address-selection semantics. Pozri [Cluster DNS](../docs/09-kubernetes/cluster-dns.md).

## Fresh-connection verdict

Dôkaz, že nový lookup a nová connection použili accepted address a dosiahli správny Service alebo external backend; samotný lookup nestačí. Pozri [Cluster DNS](../docs/09-kubernetes/cluster-dns.md).

## Identity, Service, routing a DNS acceptance verdict

Záverečný verdict príslušnej kapitoly, ktorý overuje current object/generation subjects, effective runtime/dataplane state, pôvodný business outcome a relevantné forbidden outcomes. Pozri [ServiceAccount](../docs/09-kubernetes/serviceaccount.md), [Service a EndpointSlice](../docs/09-kubernetes/service-endpointslice.md), [Ingress a Gateway API](../docs/09-kubernetes/ingress-gateway-api.md) a [Cluster DNS](../docs/09-kubernetes/cluster-dns.md).
