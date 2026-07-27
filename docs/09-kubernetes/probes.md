# Probes

Kubernetes probe nie je všeobecné tvrdenie, že aplikácia je „zdravá“. Je to opakovaný test konkrétneho container generation z konkrétnej kubelet perspektívy. Výsledok sa premení na presne definovanú akciu: povoliť ďalšie health hodnotenie, reštartovať container alebo zmeniť traffic eligibility Podu. Business dostupnosť musí byť overená samostatne.

Táto kapitola používa jeden dominantný lifecycle:

```text
serviceability intent a failure/action model
→ Pod, container a probe generation
→ kubelet probe executor a observation path
→ jednotlivé attempts, timeouty a hysterézia
→ startup/liveness/readiness verdict
→ container action, Pod condition a EndpointSlice cohort
→ rollout, drain a client traffic
→ business outcome
→ containment, recovery a skorší control
```

## 1. Atlas Payments health subject

Atlas Payments API 5.3.1 spracúva autorizácie platieb. Pre jednu repliku musí incidentný záznam fixovať:

```text
release a image digest
Deployment/ReplicaSet revision
Pod UID a Node
container name, container ID a restart count
probe type, handler, port/path a timing generation
kubelet a Node generation
probe attempt time, latency, result a reason
Pod Ready/ContainersReady conditions
EndpointSlice endpoint generation
konkrétny payment request a client outcome
```

Názov Podu alebo text „readiness failed“ nestačí. Replacement Pod môže mať rovnaké labels, ale inú container, probe, endpoint a runtime generation.

## 2. Tri verdicty, tri odlišné akcie

### Startup

Startup probe odpovedá:

```text
Dokončil tento container generation inicializáciu natoľko,
aby sa mohlo začať liveness a readiness hodnotenie?
```

Kým startup probe neuspeje, kubelet pre daný container nevykonáva liveness ani readiness probes. Opakované startup zlyhanie nakoniec vedie k restartu containeru.

### Liveness

Liveness probe odpovedá:

```text
Je tento process v stave, z ktorého mu pravdepodobne pomôže restart?
```

Po dosiahnutí failure threshold kubelet reštartuje konkrétny container podľa jeho lifecycle a restart policy. Liveness nemá zlyhávať iba preto, že shared databáza, DNS alebo vzdialená služba má incident, ak restart lokálneho processu túto príčinu neodstráni.

### Readiness

Readiness probe odpovedá:

```text
Má tento Pod generation práve teraz prijímať novú prácu alebo traffic?
```

Readiness failure container nereštartuje. Mení container/Pod readiness a následne endpoint eligibility. Už otvorené spojenia a externé load balancery môžu mať vlastný drain a propagation lifecycle.

Jedna URL použitá pre všetky tri probe typy je správna iba vtedy, keď má rovnaký test naozaj správnu startup, restart aj traffic-removal semantics.

## 3. Probe execution path je samostatný subject

HTTP, TCP a gRPC probe vykonáva kubelet z Node kontextu proti Pod endpointu. Exec probe spúšťa command v container environment-e. Probe preto typicky neprechádza rovnakou cestou ako používateľ:

```text
kubelet/Node
→ Pod IP alebo container exec boundary
→ health handler
```

Externý klient môže používať:

```text
DNS
→ load balancer
→ Gateway alebo Ingress
→ Service dataplane
→ EndpointSlice
→ Pod
→ application a dependencies
```

Kubelet probe success nepreukazuje edge TLS, DNS, Service translation, external authorization ani business transakciu. External synthetic success zase nepreukazuje, že každý konkrétny Pod má správne local lifecycle verdicty.

## 4. Handler je observation mechanism, nie význam verdictu

### HTTP

HTTP probe otvorí spojenie na definovaný host/Pod IP, port a path a vyhodnotí HTTP výsledok. Endpoint má byť bounded, lacný, bez side effects a s reason codes použiteľnými v logs/metrics.

```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: health
  periodSeconds: 5
  timeoutSeconds: 2
  failureThreshold: 3
```

### TCP

TCP probe preukazuje iba možnosť vytvoriť TCP connection. Neoveruje protocol correctness, request completion, tenant identity ani business stav. Listening socket môže zostať dostupný aj pri zamrznutom worker poole.

### Exec

Exec probe môže overiť local file, process alebo Unix socket, ale vytvára process/runtime overhead. Command musí byť priamy, bounded a bez secret outputu či opravovania stavu. `curl` alebo shell pipeline spúšťaná každú sekundu sa môže sama stať zdrojom loadu.

### gRPC

Built-in gRPC probe používa gRPC health protocol a numeric port. Pre TLS, authentication alebo service-mesh path over, či kubelet handler reprezentuje požadovaný contract; production client path sa musí testovať samostatne.

## 5. Timing vytvára hysteréziu a failure budget

Probe generation zahŕňa minimálne:

```text
initialDelaySeconds
periodSeconds
timeoutSeconds
failureThreshold
successThreshold
prípadný probe-level termination grace
```

Jedno zlyhanie nie je automaticky konečný verdict. Kubelet zbiera sequence attempts a až threshold mení stav alebo vykoná akciu. Praktické startup okno približne tvorí počet povolených zlyhaní, interval a čas jednotlivých attemptov; musí pokryť najpomalšiu prijateľnú inicializáciu, nie iba priemer.

Krátky timeout mení CPU throttling, GC pause, I/O contention alebo kubelet pressure na false failure. Príliš dlhý threshold naopak odďaľuje detekciu skutočného deadlocku alebo traffic-unsafe Podu.

## 6. Od probe verdictu po traffic

Readiness prechádza viacerými asynchrónnymi stavmi:

```text
readiness attempt
→ container Ready state
→ Pod Ready/ContainersReady conditions
→ EndpointSlice endpoint conditions
→ node/service dataplane alebo external LB update
→ nový client connection
```

Pod `Ready=False` preto nemusí okamžite znamenať, že žiadny packet už nepríde. Existujúce keep-alive sessions, conntrack, proxy cache alebo external target registration môžu dobiehať. Bezpečný scale-down a rollout stále potrebuje drain, `preStop`, termination grace a application idempotency.

Custom readiness gate pridáva ďalší controller-owned Pod condition. Gate je platný iba vtedy, ak je známy jeho owner, observed generation, freshness a recovery behavior. Stale `False` blokuje rollout; stale `True` môže vpustiť traffic pred dokončením external registrácie.

## 7. Stateful a viac-containerové Pody

Stateful replika môže byť process-live, ale nie traffic-ready, keď:

- replayuje log alebo obnovuje volume;
- čaká na membership alebo quorum;
- nie je leader pre write traffic;
- používa neplatnú data alebo fencing generation.

Liveness ju nemá reštartovať iba preto, že správne čaká na recovery alebo rolu.

Každý container má vlastné probes. Pod readiness zohľadňuje relevantné application a sidecar containers. Observability helper nemá blokovať business traffic, pokiaľ jeho dostupnosť nie je skutočnou podmienkou bezpečného requestu. Naopak auth, proxy alebo policy sidecar môže byť súčasťou traffic contractu.

## 8. Worked failure: deep probe vytvorila restart storm

Po rolloute Payments API 5.3.1 nastal tento stav:

```text
nové Pody sa inicializujú 60 až 90 sekúnd
→ startup probe chýba
→ liveness aj readiness volajú /health/deep
→ endpoint synchronne kontroluje shared ledger DB
→ DB latency dočasne prekročí 1 s
→ readiness odstráni nové endpointy
→ liveness reštartuje rovnaké containers
→ inicializácia a DB connection churn sa opakujú
→ rollout nemá stabilnú ready cohortu
→ payment latency a retry rate rastú
```

Restart neodstraňuje shared DB latency. Naopak opakovane zahrieva runtime a vytvára nové connection pools, čím incident zosilňuje.

Správny model rozdelí:

```text
startup: dokončený local bootstrap a schema/config validation
liveness: local event-loop/progress verdict odstrániteľný restartom
readiness: schopnosť bezpečne prijať nový payment request
synthetic: reálny edge payment journey
```

## 9. Causal troubleshooting walkthrough

### Fixuj subject a timeline

Pre incident fixuj release digest, Pod UID, container ID/restart count, Node, probe config generation, kubelet, sequence attemptov, Pod conditions, EndpointSlice generation a konkrétny payment request. Nezmiešavaj starý a nový container po restarte.

### Competing hypotheses

1. handler path alebo named port sa po rolloute zmenili;
2. process počúva iba na inom address-e;
3. startup trvá dlhšie než probe budget;
4. CPU throttling alebo GC predlžujú health handler;
5. kubelet alebo Node je preťažený;
6. NetworkPolicy/host path blokuje kubelet probe;
7. deep dependency check timeoutuje;
8. readiness gate je stale;
9. sidecar drží Pod NotReady;
10. EndpointSlice alebo external LB stále používa starý verdict;
11. liveness restartuje stav, ktorý restart neopraví;
12. probe success je local, ale client path zlyháva inde.

### Discriminating observation points

```bash
kubectl get pod -n production <pod> -o yaml
kubectl describe pod -n production <pod>
kubectl logs -n production <pod> -c payments --previous
kubectl get endpointslice -n production -l kubernetes.io/service-name=payments-api -o yaml
kubectl get events -n production --sort-by=.metadata.creationTimestamp
```

Koreluj:

- exact attempt timestamps a response latency;
- application health reason codes;
- container restart/termination reason;
- CPU throttling, memory pressure a thread-pool saturation;
- Pod IP test z kubelet-like Node pathu, nie iba `localhost` cez `kubectl exec`;
- readiness gate owner a freshness;
- endpoint removal/registration čas;
- external synthetic a payment trace.

### Containment bez zničenia evidence

Zastav alebo spomaľ rollout a retry amplification. Zachovaj previous-container logs, Pod/EndpointSlice YAML, kubelet Events, metrics a request traces. Nereštartuj všetky Pody a nezvyšuj thresholds naslepo. Versionovaná dočasná zmena liveness je bezpečnejšia než manuálne nekorelované restarty.

### Authoritative recovery

- pridaj startup probe pokrývajúcu bounded initialization;
- oddeľ local-progress liveness od shared dependency health;
- navrhni readiness podľa traffic safety a graceful degradation;
- oprav timeouty až po load a latency analýze;
- uprav resource contract, ak probe zlyháva pre throttling;
- oprav gate controller alebo endpoint propagation, ak je root cause mimo handlera;
- rolloutni novú Pod/probe generation a sleduj stabilizáciu.

### Verify original a forbidden outcomes

Over:

1. nový container dokončí startup bez predčasného restartu;
2. deadlock stále vyvolá bounded liveness recovery;
3. traffic-unsafe Pod nie je v ready endpoint cohort-e;
4. krátky shared dependency incident nespustí fleet-wide restart storm;
5. edge payment journey uspeje bez duplicate authorization;
6. scale-down a replacement zachovajú drain;
7. health endpoint neodhaľuje secrets ani nevykonáva writes.

### Earlier controls

Použi probe contract review, versionovaný health reason schema, startup/load test, chaos test shared dependency outage-u, per-probe metrics, rollout gate podľa stable readiness cohorty a samostatný external synthetic journey.

## 10. Ďalšie failure boundaries

### Probe funguje cez exec, ale kubelet HTTP probe nie

`localhost` v containeri a Pod IP z Node-u sú odlišné observation paths. Over listen address, port, host header, CNI/host policy a exact handler.

### Probe cez Service meno testuje inú repliku

Health request môže skončiť na zdravom Pode a skryť lokálny failure. Lifecycle probe musí byť viazaná na vlastný container/Pod subject.

### HTTPS probe je zelená, edge TLS zlyháva

Local kubelet path nereprezentuje verejný hostname, trust chain, Gateway certificate selection ani mTLS client identity. Over edge TLS samostatne.

### Readiness je príliš hlboká

Shared dependency outage odstráni všetky endpointy a zruší možnosť graceful degradation. Rozdeľ, ktoré request classes sú bezpečné a ktoré musia byť odmietnuté.

### Readiness je príliš plytká

Socket odpovedá, ale process nemá loaded config, správnu rolu alebo funkčný worker pool. Traffic sa posiela na nefunkčný backend.

### Probe endpoint má side effects

Opakované attempts vytvoria writes, lock contention alebo opravy stavu. Probe musí iba pozorovať bounded state.

## 11. Referenčný návrhový katalóg

### Probe handlers

- `httpGet` — protocol-aware local endpoint;
- `tcpSocket` — iba connection establishment;
- `exec` — local command v container boundary;
- `grpc` — gRPC health protocol.

### Probe actions

| Probe | Success znamená | Failure action |
|---|---|---|
| Startup | inicializácia dokončená | po threshold restart containeru |
| Liveness | local progress je obnoviteľný bez restartu | po threshold restart containeru |
| Readiness | Pod smie prijímať novú prácu | zmena readiness/endpoint eligibility |

### Endpoint design controls

- bounded latency a práca;
- žiadne writes ani repair actions;
- stabilné reason codes;
- žiadny fan-out na veľa dependencies;
- žiadne secrets v response/logu;
- oddelené local lifecycle a user-path testy;
- resource a timeout hodnoty overené pod loadom.

## 12. Anti-patterny

- rovnaký deep dependency test pre startup, liveness aj readiness;
- liveness bez startup probe pre dlhú inicializáciu;
- readiness, ktorá vždy vracia success;
- `curl` exec probe s vysokou frekvenciou;
- probe cez Service alebo inú repliku;
- health handler, ktorý zapisuje alebo opravuje stav;
- thresholds zväčšené bez identifikácie latency mechanizmu;
- probe považovaná za náhradu metrics, traces a external synthetics.

## 13. Kontrolné otázky

1. Aký exact action contract má startup, liveness a readiness probe?
2. Prečo kubelet probe nepreukazuje user-path dostupnosť?
3. Ktorý subject sa zmení pri container restarte, aj keď názov Podu zostane?
4. Prečo liveness nemá zlyhávať iba pre shared dependency outage?
5. Ako readiness verdict prechádza do EndpointSlice a client trafficu?
6. Prečo `kubectl exec` test nemusí reprodukovať HTTP probe?
7. Ako CPU throttling vytvorí false probe failure?
8. Čo musí obsahovať readiness gate freshness contract?
9. Ako overíš, že recovery neopravila iba probe, ale payment outcome?
10. Ktoré preventive controls odhalia restart storm pred produkciou?

## Glossary impact

Relevantné pojmy: probe generation, probe execution subject, probe attempt sequence, startup verdict, liveness recovery contract, readiness eligibility verdict, health-handler observation boundary, probe hysteresis, endpoint-readiness propagation, readiness-gate generation, false probe failure, restart amplification, probe evidence-preservation boundary a subject-bound health verification.

## Oficiálna dokumentácia

- [Liveness, Readiness, and Startup Probes](https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/)
- [Configure Liveness, Readiness and Startup Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [Pod Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)
- [Container Lifecycle Hooks](https://kubernetes.io/docs/concepts/containers/container-lifecycle-hooks/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Requests, limits a QoS](requests-limits-qos.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Taints, tolerations, affinity a topology →](taints-tolerations-affinity-topology.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
