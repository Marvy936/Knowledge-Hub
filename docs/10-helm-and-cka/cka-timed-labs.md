# CKA timed labs

CKA timed lab nie je zoznam príkazov vykonaný proti náhodnému clusteru. Je to meraný execution lifecycle, v ktorom kandidát musí správne identifikovať task subject, zvoliť minimálnu zmenu, zachovať už fungujúci stav a preukázať exact outcome v časovom limite.

> Tento materiál obsahuje originálne tréningové úlohy. Neobsahuje ani nereprodukuje dôverné otázky zo skutočnej skúšky.

## 1. Dominantný model: od zadania po bodovo uzavretý výsledok

Každú úlohu rieš rovnakým protokolom:

```text
exam/lab generation a časový budget
→ task intake a exact subject identity
→ context, namespace a constraint confirmation
→ current-state observation
→ najkratšia bezpečná execution path
→ client/server validation pred mutáciou
→ bounded change
→ controller/runtime convergence
→ hard validation požadovaného outcome-u
→ forbidden-outcome check
→ task evidence a score closure
→ skip/return alebo ďalšia úloha
```

Timed lab je úspešný iba vtedy, keď meria všetky tri vrstvy:

```text
correctness
+ execution efficiency
+ verification discipline
```

Rýchla neoverená zmena nie je hotová úloha. Správna zmena v nesprávnom context-e je chybná úloha. Technicky funkčný resource, ktorý poruší explicitný constraint, je iba partial result.

## 2. Aktuálny exam subject

Pred každou prípravnou sériou zaznamenaj aktuálny exam subject:

```text
certification: CKA
exam delivery: online, proctored, performance-based
exam duration: 2 hours
Kubernetes version: v1.35 v čase tohto reviewu
domain weights:
  Troubleshooting: 30 %
  Cluster Architecture, Installation and Configuration: 25 %
  Services and Networking: 20 %
  Workloads and Scheduling: 15 %
  Storage: 10 %
source verification date: 2026-07-28
```

Linux Foundation uvádza, že exam environment sa zosúlaďuje s novou Kubernetes minor verziou približne štyri až osem týždňov po release. Pred reálnou skúškou preto znovu over certification page, Curriculum Overview, Candidate Handbook a Exam Tips. Timed lab blueprint musí byť versionovaný; stará doménová alebo API assumption nesmie potichu prežiť do novej tréningovej generácie.

## 3. Lab generation a acceptance contract

Jeden lab subject obsahuje:

```text
lab ID a generation
environment/cluster generation
Kubernetes minor version
počet úloh a bodov
domain distribution
fault-injection manifest
initial-state checksum alebo validation
časový limit
povolené referencie
per-task validation commands
partial-credit rules
destructive-change penalties
expected cleanup alebo reset
```

Bez exact initial state-u sa nedá odlíšiť chyba kandidáta od chybného lab prostredia. Bez hard validation sa self-grading zmení na dojem.

### Bodovanie

Pre každú úlohu oddeľ:

- subject/context správnosť,
- desired-state správnosť,
- constraint preservation,
- convergence,
- hard validation,
- bezpečnosť a čas.

Príklad osem-bodovej úlohy:

```text
2 body — správny context, namespace a Deployment identity
2 body — exact image digest/tag
2 body — rollout strategy zachováva dostupnosť
1 bod  — rollout skonvergoval
1 bod  — image a availability boli explicitne overené
```

## 4. Task intake protocol

Pred prvým príkazom extrahuj:

```text
context/cluster:
namespace:
resource alebo host subject:
požadovaná zmena:
hard constraints:
forbidden changes:
validation criterion:
časový budget:
```

Príklad:

```text
context: workload-a
namespace: payments
subject: Deployment/api UID/generation
change: image I58.1 a maxUnavailable=1
constraint: najmenej tri available replicas
forbidden: delete/recreate Service alebo selector
validation: rollout complete, exact image, availability >= 3
budget: 6 minút
```

Task intake zabraňuje najdrahšej exam chybe: správne vyriešenému problému v nesprávnom clustri, namespace alebo na nesprávnom resource-e.

## 5. Context discipline

Na začiatku úlohy over:

```bash
kubectl config use-context <context>
kubectl config current-context
kubectl config set-context --current --namespace=<namespace>
kubectl config view --minify
```

Pri host-level úlohe navyše potvrď hostname, Node identity a to, či pracuješ na control-plane alebo worker hoste.

Nespoliehaj sa na stav terminálu z predchádzajúcej úlohy. Context je súčasť task subjectu, nie UI detail.

## 6. Observation pred mutáciou

Pred zmenou potrebuješ minimum evidence, ktoré odlišuje current state od zadania:

```bash
kubectl get <resource> -n <ns> -o yaml
kubectl describe <resource> -n <ns>
kubectl get events -n <ns> --sort-by=.metadata.creationTimestamp
```

Pri existujúcom workloade zachovaj jeho identity, selector, owner graph, current image, strategy, storage a Service contract. Pri troubleshooting úlohe najprv pomenuj root-cause hypothesis; nemanipuluj viacerými vrstvami naraz.

## 7. Execution path: imperative skeleton, declarative finish

Imperative generator je vhodný na rýchle vytvorenie validného skeletonu:

```bash
kubectl create deployment web \
  --image=nginx:1.27 \
  --replicas=3 \
  --dry-run=client -o yaml > /tmp/web.yaml
```

Potom manifest doplň a pred apply over:

```bash
kubectl apply --dry-run=client -f /tmp/web.yaml
kubectl apply --dry-run=server -f /tmp/web.yaml
kubectl apply -f /tmp/web.yaml
```

Pri jednoduchej presne známej zmene môže byť rýchlejší `kubectl set image`, `scale`, `label`, `taint` alebo `patch`. Voľba príkazu však nesmie skryť požadovaný field contract alebo vytvoriť neauditovateľnú sériu pokusov.

## 8. Hard validation podľa failure layeru

### Workload/controller

```bash
kubectl rollout status deployment/<name> -n <ns>
kubectl get deployment/<name> -n <ns> -o jsonpath='{.spec.template.spec.containers[*].image}'
kubectl get rs,pod -n <ns> -l <selector> -o wide
```

### Service a networking

```bash
kubectl get service,endpointslice -n <ns>
kubectl run curl-test --rm -i --restart=Never --image=curlimages/curl -- <url>
```

Over Service contract, ready endpoint cohort a actual request. Samotný ClusterIP alebo DNS record nestačí.

### Storage

```bash
kubectl get pv,pvc -A
kubectl describe pvc <name> -n <ns>
kubectl exec <pod> -n <ns> -- sh -c 'mount; test -w /data'
```

`Bound` nepreukazuje mount ani write outcome.

### RBAC

```bash
kubectl auth can-i <verb> <resource> --as=<subject> -n <ns>
kubectl auth can-i <forbidden-verb> <sensitive-resource> --as=<subject> -n <ns>
```

Over povolený aj zakázaný outcome.

### Node a control plane

```bash
kubectl get nodes
kubectl get --raw='/readyz?verbose'
systemctl status kubelet
journalctl -u kubelet --since '-10 min'
crictl ps -a
```

Node `Ready` nie je náhrada za overenie konkrétnej capability po oprave.

## 9. Časový control loop

Pre plný 120-minútový lab:

```text
0–5 min      contexts, lab health a task scan
5–85 min     prvý priechod: vysoká istota/vysoká hodnota
85–105 min   návrat k označeným úlohám
105–115 min  hard validation a forbidden checks
115–120 min  posledné bounded opravy a context audit
```

### Skip-and-return trigger

Úlohu označ a preskoč, keď:

- do 60–90 sekúnd nevieš identifikovať execution path,
- current state je iný než lab contract a potrebuješ oddeliť environment defect,
- zmena sa dostala do unknown outcome-u,
- ďalší pokus by bol deštruktívny alebo by spotreboval neprimeraný čas,
- chýba prerequisite, ku ktorému sa môžeš vrátiť po získaní bodov inde.

Pred odchodom si zapíš subject, posledné evidence a ďalší discriminating command. Návrat potom nezačína od nuly.

## 10. Worked lab walkthrough: rollout s nesprávnym contextom ako competing hypothesis

### Zadanie

V context-e `workload-a`, namespace `payments`, aktualizuj Deployment `api` na `registry.example.com/payments@sha256:I58` a nastav `maxUnavailable: 1`. Počas rollout-u musia zostať aspoň tri available replicas.

### Task subject

```text
lab: CKA-MIXED-42 generation L42
context: workload-a
namespace: payments
Deployment: api
source generation: 17
target image: I58
replicas: 4
strategy constraint: maxUnavailable=1
forbidden: selector alebo Service identity change
```

### Competing hypotheses po tom, čo rollout command nič nemení

1. príkaz bol vykonaný v nesprávnom context-e;
2. Deployment je v inom namespace;
3. field manager/GitOps vracia image späť;
4. image change bola aplikovaná, ale rollout je blocked;
5. zadanie odkazuje na iný `api` workload.

### Discriminating observations

```bash
kubectl config current-context
kubectl get deployment api -n payments -o jsonpath='{.metadata.uid}{"\n"}{.metadata.generation}{"\n"}{.spec.template.spec.containers[*].image}{"\n"}'
kubectl get events -n payments --sort-by=.metadata.creationTimestamp
```

Finding: terminál ostal v `storage-b`; existoval tam Deployment rovnakého mena. Žiadny rollout troubleshooting v `workload-a` zatiaľ nebol relevantný.

### Containment a recovery

- ďalej nemeniť `storage-b`;
- zaznamenať neúmyselnú zmenu a bezpečne ju vrátiť podľa initial-state evidence;
- prepnúť na `workload-a`;
- overiť exact subject;
- vygenerovať patch/manifests;
- použiť server dry-run;
- aplikovať a sledovať rollout.

### Closure

```bash
kubectl rollout status deployment/api -n payments
kubectl get deployment/api -n payments -o jsonpath='{.spec.strategy.rollingUpdate.maxUnavailable}{"\n"}{.spec.template.spec.containers[*].image}{"\n"}{.status.availableReplicas}{"\n"}'
```

Original outcome: exact image I58, rollout complete, najmenej tri available replicas.

Forbidden outcome: Deployment `api` v `storage-b` nezostal zmenený; production selector a Service identity sa nezmenili.

Earlier control: context v shell prompt-e a povinný task-intake check pred prvou mutáciou.

## 11. Failure boundaries pri timed labs

### Correct object, wrong generation

Po apply môže controller alebo admission zmeniť effective spec. Over live generation, nie iba local YAML.

### Resource exists, contract neplatí

Service môže existovať bez ready endpointov; PVC môže byť Bound bez funkčného mountu; RoleBinding môže povoliť požadovanú operáciu aj nežiadaný Secrets access.

### Unknown operation outcome

API timeout po write neznamená, že write neprebehol. Pred retry read-back-ni exact object generation.

### Minimálna oprava poruší skrytý constraint

Odstránenie affinity, toleration, policy alebo resource request môže rozbehnúť Pod, ale znehodnotiť úlohu.

### Overfitting na jeden lab

Ak poznáš názvy a root causes naspamäť, netrénuješ diagnosis. Rotuj identities, namespaces, images, policy combinations a failure causes.

## 12. Domain-weighted lab blueprint

Pre 100 bodov používaj aktuálne váhy:

```text
30 — troubleshooting
25 — cluster architecture, installation a configuration
20 — services a networking
15 — workloads a scheduling
10 — storage
```

Váhy nie sú dôvodom ignorovať cross-domain úlohy. Typický incident prechádza workloadom, schedulingom, networkingom a Node execution naraz.

### Odporúčaná progresia

```text
command fluency bez timeru
→ 15–30 min single-domain sprinty
→ 45–90 min mixed labs
→ plný 120 min lab
→ čistá exam simulation
→ error classification a targeted drills
```

## 13. Originálny timed lab set A

Každá úloha musí mať samostatný hard-validation script.

1. **Deployment rollout** — aktualizuj image a zachovaj availability budget.
2. **ConfigMap projection** — oprav key/reference a over process-visible hodnotu.
3. **Service discovery** — vytvor ClusterIP Service a ready EndpointSlice.
4. **NetworkPolicy** — povoľ TCP/8080 iba z požadovanej source population.
5. **PVC** — vytvor 1 Gi PVC, pripoj ho na `/data` a over mount/write.
6. **RBAC** — `reporter` môže iba `get/list/watch` Pods; over aj forbidden write.
7. **Node placement** — required label a toleration bez úniku na general Nodes.
8. **Service troubleshooting** — oprav zero endpoints bez zmeny Service identity.
9. **Control plane inspection** — identifikuj static Pod a etcd endpoint/cert paths bez mutácie.
10. **Previous logs** — nájdi restart reason a zachovaj previous logs do určeného file-u.

## 14. Originálny timed lab set B

1. CronJob s presnou schedule, `Forbid` a history limits.
2. HPA bez vypočítateľnej CPU utilization pre chýbajúce requests.
3. Headless Service + StatefulSet + per-ordinal PVC template.
4. `ImagePullBackOff` s chybnou immutable image reference.
5. DNS v `hostNetwork` Pode cez vhodnú DNS policy.
6. Cordon/drain/uncordon bez zmazania DaemonSet Podov.
7. Gateway API HTTPRoute alebo Ingress podľa dostupných APIs.
8. etcd snapshot na secure path s explicitným status validation.

## 15. Self-grading a learning loop

Po lab-e klasifikuj každú stratu bodov:

- knowledge gap,
- command syntax,
- context/namespace,
- YAML/type,
- subject misidentification,
- neoverený predpoklad,
- diagnosis delay,
- repair delay,
- chýbajúca validation,
- destructive attempt,
- time-management failure.

Pre každú chybu vytvor konkrétny drill. „Viac sa učiť“ nie je action item.

### Metrics

Sleduj:

```text
score percent
body za minútu
median task time
diagnosis/repair/verification time
skip-and-return success
context mistakes
invalid write attempts
tasks bez hard validation
forbidden-outcome violations
documentation lookup time
```

Cieľom je stabilná correctness pod časom, nie jeden výnimočný run.

## 16. Kontrolné otázky

1. Čo tvorí exact timed-lab subject?
2. Prečo correct resource nestačí bez context a generation identity?
3. Čo musí obsahovať task intake protocol?
4. Kedy je vhodný imperative skeleton?
5. Ako sa líši client validation, server validation a outcome validation?
6. Kedy úlohu preskočíš a aké evidence si ponecháš?
7. Ako overíš original aj forbidden outcome?
8. Prečo `kubectl get` často nestačí ako hard validation?
9. Ako domain weights ovplyvnia blueprint, ale nie diagnosis flow?
10. Ako z výsledkov vytvoríš targeted troubleshooting drill?

## Praktické laby

Rozšírený vykonávací protokol a tréningové sety patria do [CKA labs](../../labs/cka/README.md).

## Glossary impact

Relevantné pojmy: CKA exam subject, timed-lab generation, task subject, task intake protocol, current-state observation, execution path, hard validation, forbidden outcome, score closure, skip-and-return trigger, unknown operation outcome, domain-weighted blueprint, diagnosis time, repair time, verification time a targeted drill.

## Oficiálne zdroje

- [Certified Kubernetes Administrator](https://training.linuxfoundation.org/certification/certified-kubernetes-administrator-cka/)
- [CKA Program Changes and Domains](https://training.linuxfoundation.org/certified-kubernetes-administrator-cka-program-changes/)
- [Kubernetes Tasks](https://kubernetes.io/docs/tasks/)
- [kubectl reference](https://kubernetes.io/docs/reference/kubectl/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Helm testing a troubleshooting](helm-testing-troubleshooting.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: CKA troubleshooting drills →](cka-troubleshooting-drills.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
