# Control plane components

Control plane je súbor komponentov, ktoré chránia Kubernetes API, uchovávajú cluster state a robia cluster-wide rozhodnutia. Nie je to jedna monolitická služba. API server, etcd, scheduler a controller-manager majú odlišné úlohy, odlišný state a odlišné failure semantics. Keď ich zle zlejeme do jednej predstavy „master node“, pri incidente často hľadáme v nesprávnej vrstve.

V našom scenári pipeline mení Deployment `production/payments-api` na generation 12. Control plane musí request prijať, uložiť, vytvoriť nový ReplicaSet, vytvoriť Pods a prideliť ich Nodes. Samotné spustenie containerov už patrí worker-node vrstve.

## API server: vstupná a autorizačná hranica

`kube-apiserver` vystavuje Kubernetes REST API. Každý write prechádza authentication, authorization, admission, validation a persistence. API server je jediný komponent, cez ktorý má bežný controller meniť Kubernetes objekty; priamy zápis do etcd by obišiel API invariants, audit a field ownership.

Základné overenie:

```bash
kubectl cluster-info
kubectl get --raw='/livez?verbose'
kubectl get --raw='/readyz?verbose'
```

Liveness odpovedá, či proces žije. Readiness odpovedá, či je pripravený bezpečne obsluhovať requests. Ani jeden endpoint nepreukazuje, že konkrétny webhook, resource alebo business rollout funguje end-to-end.

Pri requeste možno sledovať serverový výsledok bez persistovania:

```bash
kubectl apply --server-side --dry-run=server \
  --field-manager=atlas-release \
  -f deployment.yaml -o yaml
```

Tento príkaz vykoná API parsing, conversion, defaulting a admission podľa serverovej konfigurácie. Nevykoná controller reconciliation ani scheduler.

### Authentication a authorization

API server najprv určí identitu caller-a. Potom RBAC alebo iný authorizer rozhodne, či identita smie vykonať konkrétny verb nad konkrétnym resource a scope.

```bash
kubectl auth whoami
kubectl auth can-i patch deployments.apps -n production
kubectl auth can-i create pods -n production --as=system:serviceaccount:production:payments-operator
```

`can-i` je užitočný pre otázku policy intentu, ale nezachytí všetky runtime detaily external authorizerov alebo admission webhooks. Skutočný request a audit event ostávajú autoritatívnym dôkazom.

### Admission

Po authorization môže request zmeniť alebo odmietnuť admission. Mutating webhook môže doplniť sidecar alebo labels. Validating policy môže zakázať mutable image tag, privileged container alebo chýbajúce requests.

Failure tu znamená, že object generation nevznikla. Scheduler alebo kubelet nemajú čo riešiť. Hľadaj API status code, reason, webhook name, timeout policy a audit event.

```bash
kubectl apply -f deployment.yaml -v=8
```

Verbose client output môže ukázať HTTP request a response. Pri produkčnom incidente však chráň credentials a nezverejňuj citlivé payloady.

## etcd: trvalý cluster state a quorum

Etcd uchováva Kubernetes API state. Control-plane HA nie je iba počet API serverov; potrebuje zdravé etcd quorum, správne membership, disk latency a obnoviteľné snapshots.

Pri troch members môže cluster tolerovať výpadok jedného. Pri strate quorum sa writes zastavia. Bežiace Pods na Nodes môžu ďalej spracúvať traffic, pretože kubelet a aplikácia už majú lokálny runtime state. Control plane však nevie bezpečne uložiť novú Deployment generation alebo status update.

```text
API listener je dostupný
+ etcd quorum chýba
→ reads môžu byť čiastočne dostupné podľa operácie
→ writes zlyhávajú alebo sa blokujú
→ existujúce workloads nemusia okamžite spadnúť
```

Etcd health sa posudzuje na control-plane hostoch cez nástroje a certifikáty zodpovedajúce konkrétnej distribúcii. Generické kopírovanie `etcdctl` príkazov bez správnych endpoints, CA a member identity môže viesť k diagnostike nesprávneho clusteru.

Dôležité signály sú leader stability, proposal latency, fsync/disk latency, database size, alarms a member health. Samotný „endpoint health=true“ nie je backup ani restore proof.

## Controller manager: viac controllers v jednom procese

`kube-controller-manager` hostí množstvo control loops, napríklad Deployment, ReplicaSet, Node lifecycle, Job, namespace a service-account token controllers. V cloud prostredí môžu cloud-specific controllers bežať v samostatnom cloud-controller-manageri.

Controller manager typicky používa leader election. V HA control plane môže bežať viac replík, ale aktívny leader vykonáva príslušné controllers. Krátka leader zmena môže spomaliť reconciliation bez straty persisted intentu.

```bash
kubectl get leases -n kube-system
```

Leases ukazujú leader-election state, ale interpretácia závisí od názvov a distribúcie clusteru. Ak controller-manager proces žije, no informer cache sa nevie synchronizovať s API, controllers nemusia robiť progress.

Pre `payments-api` sleduj objektový graph:

```bash
kubectl get deployment payments-api -n production -o yaml
kubectl get rs -n production -l app=payments-api -o yaml
kubectl get events -n production --sort-by=.lastTimestamp
```

Ak generation 12 existuje a `observedGeneration` zostáva 11, Deployment controller nemusí spracúvať najnovší intent. Ak observed generation sedí, ale ReplicaSet create zlyhal, conditions a Events môžu ukázať admission, quota alebo selector problém.

## Scheduler: placement decision

`kube-scheduler` sleduje Pods bez Node assignmentu. Pre každý Pod vytvorí candidate inventory, vykoná filter plugins nad hard constraints, score plugins nad vhodnými Nodes a zapíše binding.

Scheduler nepripravuje CNI, nemountuje volume a nespúšťa image. Jeho úspešný výsledok je priradenie `.spec.nodeName`.

```bash
kubectl get pods -n production -l app=payments-api \
  -o custom-columns='NAME:.metadata.name,NODE:.spec.nodeName,SCHEDULED:.status.conditions[?(@.type=="PodScheduled")].status'
```

Pri `Pending` Pode bez Node assignmentu čítaj scheduling Events:

```bash
kubectl describe pod -n production <pod-name>
```

Message môže obsahovať kombináciu dôvodov, napríklad insufficient memory, untolerated taint a topology constraints. Nevyberaj iba prvú frázu. Scheduler hodnotí množinu Nodes a viac constraints môže platiť naraz.

Scheduler má tiež leader election a internal queues. Backoff alebo unschedulable queue neznamená, že Pod sa už nikdy nepridelí; zmena cluster state-u ho môže znovu aktivovať.

## Cloud controller manager

V external cloud-provider modeli rieši cloud-controller-manager Node lifecycle, routes alebo Service typu LoadBalancer podľa konkrétnej integrácie. Kubernetes Service môže mať `status.loadBalancer`, ale external cloud resource má vlastnú identitu a lifecycle.

```bash
kubectl get service payments-api -n production -o yaml
```

`spec.type: LoadBalancer` je request. `status.loadBalancer.ingress` je controller observation. Ani prítomná adresa nedokazuje funkčný listener, health checks, security groups alebo DNS.

Unknown outcome pri cloud API mutation vyžaduje provider read-back. Blind create retry môže vytvoriť duplicate load balancer alebo IP allocation.

## Leader election a HA

Viac replík control-plane komponentu zvyšuje dostupnosť iba vtedy, keď majú spoločnú funkčnú dependency a správnu leader-election konfiguráciu. Tri API servery pred load balancerom nepomôžu, ak všetky používajú nedostupný etcd cluster alebo expirovaný signing key.

Pri výpadku leadera controller alebo scheduler krátko zastaví mutations, kým nový leader nezíska Lease. Desired state zostáva v API a nový leader pokračuje. Dlhý výpadok leader election však spomalí Pod replacement, Jobs, rollouts a scheduling.

## Certificates a identities

Control-plane komponenty používajú viac certifikátov a identities: API serving certificate, etcd client/server/peer certificates, kubelet client identities, service-account signing keys a controller credentials. Expiry alebo nesprávna trust chain môže poškodiť iba jednu cestu.

Napríklad:

```text
API server HTTPS funguje pre kubectl
→ API server nevie autentizovať voči etcd
→ readiness zlyhá a writes nie sú bezpečné
```

Alebo:

```text
API server a etcd fungujú
→ controller-manager client certificate expiroval
→ objects sa ukladajú, ale controllers nereagujú
```

Preto „control plane certificate“ nie je jedna položka. Inventory musí rozlišovať purpose, issuer, subject, expiry a rollout generation.

## Static Pods v kubeadm-style clustri

Pri self-managed kubeadm clustri bývajú control-plane komponenty definované ako static Pod manifests na jednotlivých Nodes. Kubelet ich spúšťa bez bežného scheduleru a API zobrazuje mirror Pods.

```bash
kubectl get pods -n kube-system -o wide
```

Zmena manifestu na jednom control-plane Node-e vytvorí novú lokálnu generation iba tam. Rolling update musí rešpektovať etcd quorum, API endpoint capacity a version skew. Ručné narazové prepísanie všetkých manifests môže vyradiť celý control plane.

## Audit a observability

API audit log odpovedá, kto, kedy a s akým výsledkom vykonal request. Component metrics a logs vysvetľujú latency, queue depth, errors a leader state. Events poskytujú používateľsky orientované správy, ale sú rate-limited a nie sú kompletným auditom.

Pri incidente koreluj:

```text
request timestamp a audit ID
→ API response
→ object resourceVersion/generation
→ controller reconcile
→ scheduler decision
→ Node execution
```

Chýbajúci audit event môže znamenať, že request nedorazil do očakávaného API endpointu. Chýbajúci Event neznamená, že chyba neexistovala.

## Incident: API je dostupné, rollout stojí

Pipeline úspešne vytvorila Deployment generation 12. `kubectl get` fungoval a API readiness bola zelená. Nový ReplicaSet však nevznikol.

Najprv sa overilo:

```bash
kubectl get deployment payments-api -n production \
  -o jsonpath='{.metadata.generation}{" "}{.status.observedGeneration}{"\n"}'
kubectl get leases -n kube-system
```

`observedGeneration` zostávala na 11. Controller-manager leader Lease sa opakovane menila, pretože všetky repliky mali extrémnu CPU throttling a nestíhali renew deadline. API a etcd boli zdravé, ale controller leadership nebola stabilná.

Containment spočíval v pozastavení ďalších releases. Oprava upravila control-plane resource reservation a obnovila stabilnú leader election. Recovery sa overila spracovaním generation 12, vytvorením ReplicaSetu, schedulingom, readiness a payment synthetics.

## Incident: scheduler je zdravý, Pod zostáva Pending

Scheduler logs neobsahovali internú chybu. Pod Event uvádzal, že všetky Nodes boli nevhodné pre kombináciu zone-bound PVC a podAntiAffinity. Pridanie ďalšej všeobecnej CPU kapacity nepomohlo, pretože nové Nodes boli v nesprávnej zone.

Root cause nebol scheduler process, ale nesplniteľný placement contract. Oprava zladila StorageClass topology, Node pool a workload spread pravidlá.

## Model, ktorý si treba odniesť

API server prijíma a chráni requests. Etcd drží autoritatívny cluster state. Controller-manager realizuje object graph a lifecycle control loops. Scheduler rozhoduje o Node placement-e. Cloud controller prepája vybrané objekty s cloud API. Každý komponent má vlastný dôkaz úspechu a vlastnú failure boundary. Produkčný outcome vzniká až ich spoločným fungovaním s worker Nodes a aplikáciou.

## Referencie

- [Kubernetes Components](https://kubernetes.io/docs/concepts/overview/components/)
- [kube-apiserver](https://kubernetes.io/docs/reference/command-line-tools-reference/kube-apiserver/)
- [kube-controller-manager](https://kubernetes.io/docs/reference/command-line-tools-reference/kube-controller-manager/)
- [kube-scheduler](https://kubernetes.io/docs/reference/command-line-tools-reference/kube-scheduler/)
- [Operating etcd clusters for Kubernetes](https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Desired state a reconciliation loops](desired-state-reconciliation-loops.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Worker node components →](worker-node-components.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
