# DaemonSet

DaemonSet je Kubernetes workload controller, ktorý zabezpečuje, aby na každom vhodnom Node-e alebo na každom Node-e z vybranej množiny bežal príslušný Pod. Desired replica count nevychádza primárne z jedného čísla, ale z počtu Node-ov spĺňajúcich scheduling a placement podmienky.

Typické použitie zahŕňa node-local logging, monitoring agentov, CNI komponenty, CSI node plugins, security agentov, device plugins alebo iné služby viazané na konkrétny Node.

## 1. Mentálny model

```text
eligible Nodes: node-a, node-b, node-c
DaemonSet desired Pods: 3

node-a → daemon Pod
node-b → daemon Pod
node-c → daemon Pod
```

Keď pribudne nový vhodný Node, DaemonSet controller vytvorí nový Pod. Keď Node prestane spĺňať podmienky, zodpovedajúci Pod sa odstráni alebo zanikne s Node lifecycle podľa situácie.

## 2. Minimálny manifest

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-agent
  namespace: platform-system
spec:
  selector:
    matchLabels:
      app: node-agent
  template:
    metadata:
      labels:
        app: node-agent
    spec:
      containers:
        - name: agent
          image: registry.example.com/node-agent@sha256:...
          resources:
            requests:
              cpu: 50m
              memory: 64Mi
```

Selector musí zodpovedať template labelom a nesmie sa prekrývať s iným controllerom.

## 3. Eligible Nodes

DaemonSet nemusí bežať na všetkých Nodes. Výber ovplyvňujú:

- `nodeSelector`,
- required node affinity,
- taints a tolerations,
- Node labels,
- OS/architecture,
- scheduler a admission constraints,
- resource availability,
- Pod security a host-resource požiadavky.

Príklad iba pre GPU Nodes:

```yaml
spec:
  template:
    spec:
      nodeSelector:
        accelerator: nvidia
```

## 4. Scheduling model

DaemonSet controller vytvára Pody s Node affinity zodpovedajúcou cieľovému Node-u. Default scheduler potom vykoná binding podľa výsledného Pod specu a cluster konfigurácie.

Dôležitý rozdiel oproti Deploymentu:

- Deployment chce N zameniteľných replík kdekoľvek,
- DaemonSet chce typicky jednu repliku na každý eligible Node.

DaemonSet Pod nemožno chápať ako globálny replica pool bez node identity.

## 5. Tolerations

Node-level agents často potrebujú bežať aj na Nodes s určitými taints alebo počas špecifických Node conditions.

Kubernetes môže DaemonSet Podom dopĺňať alebo používať tolerations potrebné pre node-local lifecycle. Vlastné široké tolerations však pridávaj iba zámerne.

Riziko:

```yaml
tolerations:
  - operator: Exists
```

Takáto konfigurácia môže agent dostať aj na control-plane, dedicated alebo izolované Nodes, kde nie je bezpečný alebo podporovaný.

## 6. Update strategies

### RollingUpdate

```yaml
spec:
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
```

Controller postupne nahrádza staré DaemonSet Pody.

Niektoré konfigurácie podporujú aj surge behavior podľa cluster verzie a API. Pri node-critical agente však treba presne vyhodnotiť, či môžu na jednom Node-e dočasne bežať dve verzie.

### OnDelete

```yaml
spec:
  updateStrategy:
    type: OnDelete
```

Nová template sa použije až po ručnom alebo externom zmazaní starého Podu.

Použitie:

- update vyžaduje node-by-node runbook,
- agent má citlivé host locks alebo device ownership,
- automatický overlap/replacement nie je bezpečný.

## 7. Rollout status

```bash
kubectl rollout status daemonset/node-agent -n platform-system
kubectl rollout history daemonset/node-agent -n platform-system
kubectl get daemonset node-agent -n platform-system -o yaml
```

Sleduj:

- desired number scheduled,
- current number scheduled,
- number ready,
- number available,
- number unavailable,
- number misscheduled,
- updated number scheduled,
- observed generation.

`numberMisscheduled` znamená Pody bežiace na Nodes, kde podľa aktuálnych pravidiel nemajú byť.

## 8. Node addition a removal

Pri novom eligible Node-e:

1. Node object a labels/taints sa objavia v API,
2. DaemonSet controller vyhodnotí eligibility,
3. vytvorí Pod viazaný na Node,
4. scheduler/kubelet/runtime realizujú Pod,
5. status sa aktualizuje.

Pri odstránení alebo zmene labelu Node-u môže controller Pod odstrániť. Ak je Node unreachable, deletion a cleanup môžu byť oneskorené podľa Node a Pod lifecycle mechanizmov.

## 9. Node bootstrap dependency

Niektoré DaemonSety sú potrebné na to, aby Node vôbec plnohodnotne fungoval:

- CNI agent,
- storage node plugin,
- kube-proxy alebo alternate dataplane,
- identity/secret node agent,
- monitoring/logging baseline.

Vzniká bootstrap dependency:

```text
Node Ready potrebuje plugin
plugin Pod potrebuje scheduling/runtime/network/storage
```

Core node add-ons preto potrebujú minimálne dependencies a jasný bootstrap path.

## 10. Priority

Node-critical DaemonSet môže používať vyššiu PriorityClass, aby scheduler preferoval jeho umiestnenie pred menej kritickými workloadmi.

Riziká:

- nesprávne vysoká priorita vytláča application Pody,
- preemption nevytvorí fyzickú kapacitu, ak agent potrebuje device alebo host port,
- priority nevyrieši invalid image, mount alebo security policy.

Priority musí zodpovedať skutočnej platformovej kritickosti.

## 11. Host resources

DaemonSety často požadujú:

- `hostNetwork`,
- `hostPID`,
- `hostPath`,
- devices,
- privileged alebo capabilities,
- host ports,
- runtime/socket access.

Každý takýto prístup zväčšuje blast radius. Node agent môže byť bezpečnostne bližšie host service než bežnému application containeru.

Controls:

- minimálny read-only host mount,
- presný device scope,
- capability drop,
- seccomp/LSM,
- non-root, ak je možné,
- trusted image a signature policy,
- oddelený ServiceAccount a RBAC,
- network egress control,
- audit a node hardening.

## 12. Networking patterns

Node-local daemon môže komunikovať cez:

- push do centrálneho backendu,
- `hostPort` a Node IP,
- headless Service a Pod DNS/endpoints,
- bežný Service,
- local-node traffic policy,
- host network.

Výber závisí od toho, či klient potrebuje konkrétny Node-local endpoint alebo ľubovoľnú repliku.

`hostPort` môže vytvoriť port collision. `hostNetwork` odstráni časť isolation a mení DNS/listen behavior.

## 13. Resources a overhead

DaemonSet requests sa násobia počtom Nodes.

Príklad:

```text
100 Nodes × 200 MiB request = 20 GiB cluster reserved memory
```

Pri návrhu sleduj:

- per-node fixed overhead,
- CPU burst a throttling,
- log buffer/storage,
- memory leak vynásobený cluster size,
- image pull bandwidth pri rollout-e,
- rollout concurrency,
- control-plane object/event load.

Malý agent na jednom Node-e môže byť veľký platformový náklad v celom clustri.

## 14. Draining Nodes

Pri `kubectl drain` sa DaemonSet Pody typicky špeciálne ignorujú alebo vyžadujú príslušný flag, pretože controller ich na tom istom Node-e znovu vytvorí, kým Node zostáva eligible.

Bežný maintenance flow:

```bash
kubectl cordon <node>
kubectl drain <node> --ignore-daemonsets ...
# maintenance
kubectl uncordon <node>
```

DaemonSet agent musí zvládnuť Node shutdown/reboot a opätovnú inicializáciu.

## 15. Static Pod vs. DaemonSet

### Static Pod

- source je local kubelet manifest,
- nevyžaduje bežný controller/API create path,
- vhodný pre bootstrap/control-plane use cases,
- správa je node-local.

### DaemonSet

- deklarovaný v API,
- controller riadi eligible Nodes,
- podporuje rollout a centralized observability,
- závisí od fungujúceho API/controller pathu.

Pre bežný node agent preferuj DaemonSet.

## 16. Deployment vs. DaemonSet

Použi Deployment, keď:

- potrebuješ N stateless replík,
- nezáleží na konkrétnom Node-e,
- traffic ide cez Service/load balancing,
- škálovanie je podľa demandu.

Použi DaemonSet, keď:

- workload poskytuje funkciu konkrétnemu Node-u,
- potrebuje prístup k node-local logs, devices alebo network,
- počet replík je odvodený od eligible Nodes,
- lifecycle má sledovať Node fleet.

## 17. Observability

```bash
kubectl get daemonset -A
kubectl describe daemonset node-agent -n platform-system
kubectl get pods -n platform-system -l app=node-agent -o wide
kubectl get nodes --show-labels
kubectl get events --sort-by=.metadata.creationTimestamp
```

Porovnaj:

- eligible Node list,
- desired/current/ready/available/updated/misscheduled counts,
- Pod distribution per Node,
- image ID a revision,
- Node labels/taints,
- Pod Events,
- host resource a agent metrics.

## 18. Failure scenáre

### Desired je menšie než počet Nodes

Nie všetky Nodes sú eligible. Over labels, taints, affinity, OS/architecture a resources.

### Desired správne, Ready nižšie

Diagnostikuj konkrétne Pody: image, config, host mount, device, permissions, CNI, probe a Node pressure.

### `numberMisscheduled > 0`

Node už nespĺňa aktuálne rules alebo template/selector sa zmenil. Over termination a controller Events.

### Rollout stojí

Nová verzia nemusí byť Ready na jednom Node-e; pri `maxUnavailable` môže blokovať ďalší postup.

### Agent funguje na väčšine Nodes, nie na jednom

Porovnaj Node-specific kernel, OS, architecture, labels, devices, filesystem, security policy a capacity.

### Nový Node ostáva bez CNI agenta

Over bootstrap taints/tolerations, image pull, runtime, scheduling, host mounts a plugin configuration. Bez CNI môže Node ostať NotReady.

## 19. Anti-patterny

### DaemonSet pre bežnú web službu

Replica count sa zbytočne viaže na Nodes a traffic model je nejasný.

### Broad host filesystem mount

Compromise agentu môže znamenať compromise Node-u.

### `operator: Exists` toleration bez policy

Agent sa rozšíri aj na citlivé Nodes.

### Host port používaný bez collision analýzy

Pod sa nemusí vytvoriť na Node-e, kde port už vlastní iný process.

### Update všetkých Nodes naraz bez blast-radius kontroly

Chybný CNI, storage alebo security agent môže narušiť celý cluster.

### Ignorovanie per-node resource overheadu

DaemonSet vyčerpáva allocatable capacity na každom Node-e.

## 20. Kontrolné otázky

1. Ako DaemonSet určuje desired replica count?
2. Čo robí Node eligible pre DaemonSet?
3. Ako sa DaemonSet líši od Deploymentu?
4. Aký je rozdiel medzi `RollingUpdate` a `OnDelete`?
5. Čo znamená `numberMisscheduled`?
6. Prečo sú tolerations pri DaemonSete citlivé?
7. Aké riziká prinášajú host resources?
8. Prečo sa DaemonSet Pody pri drain-e riešia špeciálne?
9. Ako sa líši static Pod od DaemonSetu?
10. Ako by si rolloutoval kritický CNI agent s obmedzeným blast radiusom?

## Glossary impact

Relevantné pojmy: DaemonSet, eligible Node, desired number scheduled, number misscheduled, DaemonSet rolling update, DaemonSet `OnDelete`, node-local agent, host resource access, per-node overhead a node bootstrap dependency.

## Oficiálna dokumentácia

- [DaemonSet](https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/)
- [Perform a rolling update on a DaemonSet](https://kubernetes.io/docs/tasks/manage-daemon/update-daemon-set/)
- [Safely drain a Node](https://kubernetes.io/docs/tasks/administer-cluster/safely-drain-node/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: StatefulSet](statefulset.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Job a CronJob →](job-cronjob.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
