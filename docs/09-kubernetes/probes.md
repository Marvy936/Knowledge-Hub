# Probes

Kubernetes probes dávajú kubeletu opakovateľný signál o stave containeru. **Startup probe** chráni pomalý štart pred predčasným liveness/readiness hodnotením. **Liveness probe** rozhoduje, či má kubelet container reštartovať. **Readiness probe** rozhoduje, či má byť Pod používaný ako ready backend. Probe nie je všeobecný monitoring systém ani business transaction test.

## 1. Tri odlišné otázky

### Startup

```text
Dokončil process inicializáciu a môže sa začať bežné health hodnotenie?
```

### Liveness

```text
Je process v stave, z ktorého mu pravdepodobne pomôže restart?
```

### Readiness

```text
Má tento Pod práve teraz prijímať nový traffic alebo prácu?
```

Použitie jedného endpointu pre všetky tri otázky je možné iba vtedy, keď majú naozaj rovnakú failure semantics.

## 2. Kto probes vykonáva

Probes vykonáva kubelet na Node-e, kde Pod beží.

Dôsledky:

- HTTP/TCP/gRPC probe prichádza z node-local kontextu, nie cez Service alebo Ingress,
- DNS, NetworkPolicy a host routing môžu ovplyvniť niektoré probe typy,
- application nemusí vidieť rovnakú cestu ako reálny klient,
- kubelet pressure alebo runtime problém môže oneskoriť probe execution.

Probe success preukazuje iba konkrétny test z perspektívy kubeletu.

## 3. Probe handlers

Kubernetes podporuje najmä:

- `httpGet`,
- `tcpSocket`,
- `exec`,
- `grpc`.

Každý handler má iný význam a failure surface.

## 4. HTTP probe

```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: http
    scheme: HTTP
```

HTTP probe:

- otvorí connection na Pod IP a port,
- odošle HTTP request,
- vyhodnotí status podľa probe semantics,
- môže nastaviť host header alebo ďalšie headers.

Endpoint má byť:

- lacný,
- bounded,
- bez side effects,
- stabilný počas vysokého loadu,
- bez závislosti na externom DNS/load balanceri, ak to nie je zámer.

## 5. TCP probe

```yaml
livenessProbe:
  tcpSocket:
    port: 8080
```

TCP probe overí, že je možné vytvoriť TCP connection.

Neoveruje:

- správnu odpoveď protokolu,
- autentifikáciu,
- business correctness,
- dostupnosť konkrétneho endpointu,
- schopnosť dokončiť request.

Je vhodná pre protocol bez jednoduchého HTTP/gRPC health endpointu, ale môže produkovať false positives.

## 6. Exec probe

```yaml
livenessProbe:
  exec:
    command:
      - /usr/local/bin/check-health
```

Exec probe spustí process vo vnútri container environmentu.

Výhody:

- môže overiť local file/socket/process state,
- podporuje custom protocol.

Riziká:

- fork/process overhead,
- shell alebo utility nemusí byť v minimalistickom image,
- command môže zablokovať,
- nebezpečné side effects,
- vysoká frekvencia vytvára resource pressure,
- output môže obsahovať secrets.

Preferuj priamy executable a bounded timeout; nebuduj komplexný shell script ako skrytý monitoring systém.

## 7. gRPC probe

```yaml
livenessProbe:
  grpc:
    port: 9090
    service: liveness
```

gRPC probe používa gRPC Health Checking Protocol.

Môže rozlišovať service name pre startup/liveness/readiness semantics.

Over:

- application implementuje health protocol,
- numeric port je správny podľa API podpory,
- TLS/auth behavior zodpovedá built-in probe možnostiam,
- timeout a failureThreshold sú realistické.

Built-in probe nemusí podporovať všetky production gRPC security alebo routing vrstvy; testuje Pod endpoint z kubelet pathu.

## 8. Timing fields

Bežné fields:

```yaml
startupProbe:
  httpGet:
    path: /startup
    port: 8080
  initialDelaySeconds: 0
  periodSeconds: 5
  timeoutSeconds: 2
  successThreshold: 1
  failureThreshold: 60
```

### `initialDelaySeconds`

Čakanie pred prvým probe pokusom podľa lifecycle semantics.

### `periodSeconds`

Interval medzi probe pokusmi. Readiness môže byť pri not-ready containeri vyhodnocovaná aj častejšie podľa kubelet behavior.

### `timeoutSeconds`

Maximum času jedného pokusu.

### `failureThreshold`

Počet po sebe idúcich failures pred failure action.

### `successThreshold`

Počet úspechov potrebných na návrat do success state-u. Pre liveness a startup je typicky vyžadovaná hodnota 1; readiness môže používať vyššiu hodnotu na stabilizáciu.

## 9. Startup probe

Kým startup probe neuspeje:

- liveness probe sa nevykonáva,
- readiness probe sa nevykonáva,
- container dostane čas na inicializáciu.

Maximálne startup okno približne vyjadruje:

```text
failureThreshold × periodSeconds
```

plus jednotlivé timeout a scheduling detaily.

Startup probe má zlyhať iba vtedy, keď initialization nepostupuje alebo prekročila prijateľnú hranicu.

## 10. Liveness probe

Pri opakovanom liveness failure kubelet označí container ako unhealthy a spustí restart podľa Pod/container lifecycle-u.

Liveness má detegovať stav ako:

- deadlock,
- event loop trvalo nepostupuje,
- process síce žije, ale nie je schopný vykonávať základnú funkciu,
- interná korupcia odstrániteľná restartom.

Nemá zlyhávať iba preto, že:

- databáza je dočasne nedostupná,
- external API timeoutuje,
- celý region má dependency incident,
- load je vysoký, ale process stále napreduje.

Ak restart neodstráni príčinu, liveness môže vytvoriť restart storm.

## 11. Readiness probe

Readiness failure:

- nereštartuje container,
- mení Pod Ready condition,
- ovplyvňuje EndpointSlice readiness a Service traffic,
- môže zastaviť Deployment rollout progress.

Readiness môže zahŕňať dependencies potrebné na obsluhu requestu, ale musí byť navrhnutá opatrne.

Príliš široká readiness:

- odpojí všetky replicas pri shared dependency outage,
- Service ostane bez endpointov,
- zhorší graceful degradation.

Príliš úzka readiness:

- posiela traffic na Pod, ktorý nevie obsluhovať požiadavky.

## 12. Probe failure actions

### Startup failure

Po prekročení threshold kubelet container reštartuje podľa lifecycle semantics.

### Liveness failure

Kubelet container reštartuje.

### Readiness failure

Container zostáva bežať, ale Pod nie je ready pre bežný traffic.

Container restart a Pod replacement sú odlišné. Vyšší workload controller môže Pod nahradiť až pri ďalších failure alebo lifecycle mechanizmoch.

## 13. Probe-level termination grace

Startup alebo liveness probe môže podľa podporovaného API nastaviť vlastné `terminationGracePeriodSeconds`.

Použitie:

- kratší grace pre stuck process,
- odlišný shutdown čas než pri bežnom Pod deletion flow.

Readiness probe túto failure action nemá, preto probe-level termination grace pre readiness nedáva zmysel.

Aj pri liveness restart-e musí application zvládnuť termination signal a bounded cleanup.

## 14. Named ports

HTTP a TCP probes môžu podľa API používať named container port:

```yaml
ports:
  - name: health
    containerPort: 8081

readinessProbe:
  httpGet:
    port: health
    path: /ready
```

Named port zlepšuje čitateľnosť a umožní zmenu numeric portu bez zmeny probe reference.

Pri gRPC probe over podporu named ports; bežne sa používa numeric port.

## 15. HTTP host a headers

HTTP probe typicky smeruje na Pod IP. Ak application používa virtual hosting, môže byť potrebný `Host` header:

```yaml
httpGet:
  path: /healthz
  port: 8080
  httpHeaders:
    - name: Host
      value: internal.example
```

Nezamieňaj `host` field za HTTP Host header bez pochopenia routing semantics. Probe nemá obchádzať security boundary pripojením na nesprávnu host adresu.

## 16. HTTPS probes

HTTP probe môže používať `scheme: HTTPS`.

Kubelet však nemusí poskytovať rovnaký certificate verification model ako production klient. Probe success preto nie je dôkaz, že:

- certificate chain je trusted klientmi,
- hostname/SAN sedí,
- mTLS funguje,
- Ingress/Gateway TLS konfigurácia je správna.

Production TLS test patrí do synthetic monitoring alebo edge validation.

## 17. Readiness gates

Pod môže mať custom readiness gates viazané na Pod conditions aktualizované external controllerom.

```yaml
spec:
  readinessGates:
    - conditionType: example.com/LoadBalancerReady
```

Pod je Ready až keď:

- všetky containers sú ready,
- všetky readiness gate conditions sú true.

Použitie:

- external load balancer registration,
- sidecar/infrastructure readiness,
- custom admission do trafficu.

Riziko: controller failure alebo stale condition môže držať Pody trvalo NotReady.

## 18. Deployment rollout

Deployment považuje nové Pody za dostupné až podľa readiness a `minReadySeconds`.

Zlá probe môže:

- zastaviť rollout,
- vytvoriť false progress,
- odpojiť staré aj nové replicas,
- zvýšiť surge resource consumption,
- spustiť automatizovaný rollback v externom delivery systéme.

Probe je preto release safety contract, nie iba lokálny YAML detail.

## 19. Stateful workloady

Stateful Pod môže byť process-live, ale nie traffic-ready, napríklad:

- replica sa synchronizuje,
- node nie je leader,
- shard nie je assigned,
- database recovery pokračuje,
- volume replay ešte neskončil.

Readiness má reprezentovať rolu a schopnosť obsluhovať traffic. Liveness nemá reštartovať zdravú repliku iba preto, že čaká na quorum alebo leadera.

## 20. Sidecars

Každý container má vlastné probes.

Pod Ready zohľadňuje readiness všetkých relevantných containers. Sidecar readiness môže preto blokovať application traffic.

Rozhodni:

- musí sidecar fungovať pre business request?
- je sidecar iba observability helper?
- má jeho failure odstrániť Pod z trafficu?
- má byť sidecar restartovaný nezávisle?

Nepridávaj readiness probe na nepodstatný helper bez availability analýzy.

## 21. Probe endpoint design

Dobrý endpoint:

- vykoná bounded prácu,
- nealokuje veľké množstvo memory,
- nezapisuje do databázy,
- nevyžaduje globálny lock,
- nerozširuje outage cez fan-out na veľa dependencies,
- má stabilné reason codes/logging,
- neobsahuje secrets v response,
- je dostupný iba v potrebnom network scope.

Health endpoint môže byť attack surface. Chráň citlivé debug detaily a nepovoľuj management operácie cez probe path.

## 22. External monitoring vs. probes

Probes odpovedajú z pohľadu kubeletu. External monitoring overuje user path:

```text
DNS
→ load balancer
→ Gateway/Ingress
→ Service
→ EndpointSlice
→ Pod
→ application/dependency
```

Potrebuješ oboje:

- probes pre local lifecycle a traffic eligibility,
- metrics/logs/traces pre interné správanie,
- synthetic checks pre end-to-end dostupnosť.

## 23. Observability

```bash
kubectl describe pod -n production <pod>
kubectl get pod -n production <pod> -o yaml
kubectl get events -n production --sort-by=.metadata.creationTimestamp
kubectl logs -n production <pod> -c <container>
kubectl logs -n production <pod> -c <container> --previous
kubectl get endpointslice -n production
```

Sleduj:

- container restart count,
- last termination reason,
- Pod Ready condition,
- probe failure Events,
- endpoint readiness propagation,
- probe latency a status metrics v aplikácii,
- CPU throttling a memory pressure,
- kubelet/node health.

## 24. Troubleshooting

### `CrashLoopBackOff` po nasadení probe

Over command/path/port, startup čas, timeout, failure threshold, process listen address, CPU throttling a application logs pred restartom.

### Pod je Running, ale NotReady

Over readiness failure reason, EndpointSlice, custom readiness gates, sidecar readiness a dependency state.

### Probe funguje cez `kubectl exec`, ale kubelet ju hlási failed

Exec test môže používať inú network cestu alebo command environment. Pri HTTP/TCP testuj Pod IP a kubelet-like source path, nie iba `localhost`.

### Probe timeoutuje pri load-e

Over endpoint cost, CPU limit/throttling, thread pool starvation, GC pauses, timeoutSeconds a Node pressure.

### Všetky replicas sa odpojili pri database outage

Readiness je príliš závislá od shared dependency. Navrhni graceful degradation alebo rozlišuj request typy.

### Liveness spôsobuje permanentné restarty

Restart neodstraňuje root cause. Dočasne môže byť bezpečnejšie liveness upraviť alebo vypnúť cez versionovaný rollout, ale zachovaj evidence a oprav endpoint/failure model.

## 25. Anti-patterny

### Rovnaký hlboký dependency test pre liveness a readiness

Dependency outage spôsobí restart storm aj odpojenie všetkých backendov.

### `curl` exec probe každú sekundu

Vytvára process a CPU overhead a vyžaduje utility v image-i.

### Veľmi krátky timeout bez load testu

Bežný GC alebo CPU contention sa zmení na false failure.

### Readiness vždy vracia success

Rollout a Service posielajú traffic aj na nefunkčný Pod.

### Liveness bez startup probe pre pomalý štart

Kubelet reštartuje process skôr, než dokončí inicializáciu.

### Health endpoint vykonáva write alebo opravu stavu

Opakované probe calls vytvárajú side effects a race conditions.

### Probe cez Service meno na ten istý workload

Môže testovať inú repliku a skryť lokálny failure.

### Probe považovaná za monitoring

Chýba historická latency, SLI, user-path validation a incident context.

## 26. Kontrolné otázky

1. Aký je rozdiel medzi startup, liveness a readiness probe?
2. Kto probes vykonáva a z akej network perspektívy?
3. Aké sú rozdiely medzi HTTP, TCP, exec a gRPC probe?
4. Čo sa stane pri liveness failure a čo pri readiness failure?
5. Ako vypočítaš približné startup okno?
6. Prečo liveness nemá závisieť od vzdialenej databázy vo všetkých prípadoch?
7. Ako readiness ovplyvňuje EndpointSlice a Deployment rollout?
8. Kedy sú vhodné readiness gates?
9. Prečo HTTPS probe nepreukazuje správny edge TLS contract?
10. Ako diagnostikuješ false probe failures pri CPU throttlingu?

## Glossary impact

Relevantné pojmy: startup probe, liveness probe, readiness probe, HTTP probe, TCP probe, exec probe, gRPC probe, probe threshold, probe timeout, probe-level termination grace, readiness gate, health endpoint, false-positive probe failure, restart storm a synthetic monitoring.

## Oficiálna dokumentácia

- [Liveness, Readiness, and Startup Probes](https://kubernetes.io/docs/concepts/workloads/pods/probes/)
- [Configure Liveness, Readiness and Startup Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [Pod Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)
- [Container Lifecycle Hooks](https://kubernetes.io/docs/concepts/containers/container-lifecycle-hooks/)
