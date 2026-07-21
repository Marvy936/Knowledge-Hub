# CKA timed labs

CKA je performance-based skúška. Nestačí poznať definície; kandidát musí v časovom limite bezpečne meniť a diagnostikovať reálny Kubernetes cluster cez command line. Timed labs preto musia merať correctness, čas, kontext, validáciu a schopnosť vrátiť sa k rozpracovanej úlohe bez poškodenia ostatných častí clusteru.

> Tento materiál obsahuje originálne tréningové úlohy. Neobsahuje ani nereprodukuje dôverné otázky zo skutočnej skúšky.

## 1. Aktuálny exam model

K dátumu spracovania tejto kapitoly oficiálna stránka uvádza:

- online proctored performance-based skúšku,
- dĺžku 2 hodiny,
- Kubernetes v1.35,
- priebežné zosúladenie s novou minor verziou približne 4 až 8 týždňov po Kubernetes release,
- domény:
  - Troubleshooting — 30 %,
  - Cluster Architecture, Installation and Configuration — 25 %,
  - Services and Networking — 20 %,
  - Workloads and Scheduling — 15 %,
  - Storage — 10 %.

Pred reálnou skúškou vždy znovu skontroluj oficiálnu CKA stránku, Curriculum Overview, Candidate Handbook a exam tips. Verzia, UI aj pravidlá sa môžu zmeniť.

## 2. Cieľ timed labs

Timed lab nemeria iba počet vyriešených úloh. Sleduj:

- správny cluster context a namespace,
- čas po prvý validný výsledok,
- počet chybných alebo deštruktívnych pokusov,
- schopnosť overiť stav,
- správne použitie dokumentácie,
- návrat k preskočenej úlohe,
- čistotu pracovného prostredia,
- zachovanie už fungujúcich resources.

## 3. Tréningové fázy

### Fáza A — command fluency

Bez časového tlaku precvičuj:

- `kubectl create ... --dry-run=client -o yaml`,
- `kubectl run`,
- `kubectl expose`,
- `kubectl set image`,
- `kubectl scale`,
- `kubectl rollout`,
- JSONPath/custom-columns,
- `kubectl explain`,
- edit/apply/patch,
- logs, describe a Events,
- kubeadm, etcdctl/etcdutl a systemd commands podľa lab prostredia.

Cieľom nie je memorovať všetko. Cieľom je vedieť rýchlo vytvoriť skeleton a presne ho doplniť.

### Fáza B — single-domain sprints

Trvanie 15 až 30 minút:

- iba storage,
- iba networking,
- iba workloads,
- iba RBAC/cluster configuration,
- iba troubleshooting.

### Fáza C — mixed timed labs

Trvanie:

- 45 minút,
- 60 minút,
- 90 minút,
- plných 120 minút.

Úlohy miešaj tak, aby si musel prepínať context a failure layer.

### Fáza D — exam simulation

Použi čisté prostredie, presný timer, povolené referencie podľa aktuálnych pravidiel a nulové vyrušovanie. Počas simulácie si nerob výklad; zaznamenávaj iba krátke marks a vráť sa k analýze po skončení.

## 4. Časová stratégia

Pri 120-minútovom tréningu:

```text
0–5 min    orientácia, contexts, rýchly scan
5–85 min   prvý priechod, vysoká istota a vysoká hodnota
85–105 min návrat k preskočeným úlohám
105–115 min validácia všetkých výsledkov
115–120 min posledné opravy a context kontrola
```

Konkrétne rozdelenie uprav podľa počtu a váhy úloh.

Pravidlo:

- ak nevieš do 60–90 sekúnd identifikovať cestu, označ úlohu a pokračuj,
- ak sa riešenie dostalo do nejasného stavu, zachovaj evidence a neeskaluj chaos,
- posledných 10–15 minút nechaj na verification pass.

## 5. Task intake protocol

Pri každej úlohe si v hlave alebo scratchpade extrahuj:

```text
cluster/context:
namespace:
resource identity:
požadovaná zmena:
constraints:
validation criterion:
```

Napríklad:

```text
context: cluster-a
namespace: payments
resource: deployment/api
change: image + maxUnavailable
constraint: zachovať 3 available replicas
validation: rollout complete + image exact
```

Tým sa znižuje riziko, že vyriešiš správnu úlohu v nesprávnom clustri.

## 6. Context discipline

Pred každou úlohou:

```bash
kubectl config use-context <context>
kubectl config current-context
kubectl config set-context --current --namespace=<namespace>
```

Pri kritických operations vypíš context priamo v prompt-e:

```bash
export PS1='[\u@\h \W $(kubectl config current-context 2>/dev/null)]\$ '
```

Nespoliehaj sa iba na predchádzajúci terminálový stav.

## 7. Imperative skeleton, declarative finish

Rýchly pattern:

```bash
kubectl create deployment web \
  --image=nginx:1.27 \
  --replicas=3 \
  --dry-run=client -o yaml > /tmp/web.yaml
```

Potom manifest uprav a aplikuj:

```bash
kubectl apply -f /tmp/web.yaml
```

Výhody:

- správna základná schema,
- rýchle vytvorenie,
- možnosť doplniť probes/resources/affinity,
- auditovateľný intermediate file.

Imperative command použi priamo iba pri jednoduchej, presne známej zmene.

## 8. Verification-driven execution

Každá úloha potrebuje konkrétny dôkaz.

### Workload

```bash
kubectl rollout status deployment/<name> -n <ns>
kubectl get deployment/<name> -n <ns> -o yaml
kubectl get pod -n <ns> -l <selector> -o wide
```

### Service/networking

```bash
kubectl get service,endpointslice -n <ns>
kubectl run curl --rm -it --restart=Never --image=curlimages/curl -- <url>
```

### Storage

```bash
kubectl get pv,pvc -A
kubectl describe pvc <name> -n <ns>
kubectl exec <pod> -n <ns> -- mount
```

### RBAC

```bash
kubectl auth can-i <verb> <resource> \
  --as=<subject> -n <ns>
```

### Cluster/node

```bash
kubectl get nodes
kubectl get --raw='/readyz?verbose'
systemctl status kubelet
```

## 9. Documentation strategy

Neotváraj dokumentáciu bez presnej otázky. Hľadaj:

- API field,
- command syntax,
- exact example,
- failure-specific guide.

Efektívny workflow:

```text
identifikujem resource a problém
→ skúsim kubectl explain/command help
→ otvorím presnú official docs stránku
→ skopírujem minimum
→ upravím identity/namespace
→ aplikujem
→ validujem
```

Nevytváraj rozsiahle poznámky počas timed runu.

## 10. Shell efficiency

Užitočné, ale nie povinné:

```bash
alias k=kubectl
export do='--dry-run=client -o yaml'
```

Ďalšie návyky:

- shell history search,
- `set -o vi` alebo emacs shortcuts podľa zvyku,
- heredoc pre krátke manifesty,
- `kubectl explain <resource>.<field>`,
- JSONPath uložené ako malé reusable patterns,
- `/tmp` pre pracovné files.

Alias, ktorý si počas stresu nepamätáš, je kontraproduktívny.

## 11. Editing strategy

Nástroj si zvoľ pred tréningom. Potrebuješ vedieť:

- search,
- delete/copy lines,
- indentation,
- save/quit,
- undo,
- line numbers,
- multi-file navigation.

Po každej väčšej editácii:

```bash
kubectl apply --dry-run=client -f file.yaml
```

Potom server validation podľa potreby.

## 12. Bodovací model pre vlastné labs

Každá úloha má:

- body podľa zložitosti,
- hard validation,
- partial-credit criteria,
- časový budget,
- destructive-change penalty.

Príklad:

```text
8 bodov — Deployment rollout
2 body — správny namespace/identity
2 body — správny image
2 body — strategy constraints
2 body — rollout verified
```

Self-grading musí používať scripts alebo explicitné commands, nie dojem.

## 13. Domain-weighted lab blueprint

Pre 100 bodov:

- 30 bodov troubleshooting,
- 25 bodov cluster architecture/configuration,
- 20 bodov services/networking,
- 15 bodov workloads/scheduling,
- 10 bodov storage.

Konkrétne úlohy nemusia kopírovať exam layout. Váha zabezpečí, že tréning neignoruje najdôležitejšie domény.

## 14. 45-minútový sprint

Príklad:

1. Opraviť Deployment readiness a image — 8 b.
2. Vytvoriť Service a overiť EndpointSlice — 6 b.
3. Opraviť Pending PVC — 5 b.
4. Vytvoriť namespaced Role/RoleBinding — 6 b.
5. Diagnostikovať NotReady Node alebo kubelet config — 10 b.
6. Opraviť NetworkPolicy/DNS connectivity — 10 b.

Cieľ: rýchle prepínanie vrstiev.

## 15. 90-minútový mixed lab

Príklad oblastí:

- kubeadm alebo control-plane config inspection,
- etcd snapshot validation,
- workload rollout/rollback,
- HPA alebo resources,
- taints/affinity,
- PV/PVC/StorageClass,
- Service/Gateway/NetworkPolicy/CoreDNS,
- logs a component troubleshooting.

Posledných 10 minút je povinný verification pass.

## 16. Plný 120-minútový lab

Odporúčaný počet:

- 15 až 20 úloh,
- mix 3–12 bodov,
- 3 až 5 troubleshooting scenárov,
- aspoň jedna multi-step cluster úloha,
- aspoň jedna storage a jedna network policy úloha,
- aspoň jedna úloha, ktorú je rozumné preskočiť a vrátiť sa.

Neoptimalizuj lab na memorovanie jedného setu. Parametre, namespaces, images a failure causes rotuj.

## 17. Original timed lab set A

### Úloha 1 — Deployment rollout

V context-e `workload-a`, namespace `shop`, aktualizuj Deployment `catalog` na image `nginx:1.27`. Počas rollout-u nesmie byť nedostupná viac než jedna replika. Over dokončenie.

### Úloha 2 — ConfigMap projection

Vytvor ConfigMap `catalog-config` s key `MODE=production`. Pripoj ju do Deploymentu ako environment variable bez zmeny ostatných variables.

### Úloha 3 — Service discovery

Vytvor ClusterIP Service `catalog` na porte 80 smerujúci na container port 8080 a over, že má ready EndpointSlice.

### Úloha 4 — NetworkPolicy

Izoluj Pods `app=catalog` pre ingress. Povoľ TCP/8080 iba z Podov `app=frontend` v rovnakom namespace.

### Úloha 5 — PVC

V namespace `shop` vytvor 1 Gi PVC so StorageClass `fast` a pripoj ho do Podu na `/data`. Over Bound a mount.

### Úloha 6 — RBAC

ServiceAccount `reporter` môže iba `get`, `list`, `watch` Pods v namespace `shop`. Over cez impersonation.

### Úloha 7 — Node placement

Deployment `batch` musí bežať iba na Nodes s labelom `workload=batch` a tolerovať taint `dedicated=batch:NoSchedule`.

### Úloha 8 — Troubleshooting

Service `checkout` nemá endpoints. Nájdeš a opravíš root cause bez zmeny Service identity.

### Úloha 9 — Control plane

Na zadanom control-plane hoste over API server static Pod manifest a identifikuj etcd endpoint/certificate paths bez ich zmeny.

### Úloha 10 — Logs

Pod `worker` sa opakovane reštartuje. Zisti exit reason a zachovaj previous container logs do `/tmp/worker-previous.log`.

## 18. Original timed lab set B

### Úloha 1

Vytvor CronJob každých 10 minút s `concurrencyPolicy: Forbid`, history limitom 2 successful a 1 failed Job.

### Úloha 2

Oprav HPA, ktorý nevie vypočítať CPU utilization pre Deployment bez requests.

### Úloha 3

Vytvor headless Service a StatefulSet s troma replikami a per-replica PVC template.

### Úloha 4

Oprav Pod, ktorý je `ImagePullBackOff` pre chybnú image reference.

### Úloha 5

Oprav DNS resolution iba v hostNetwork Pode použitím vhodnej DNS policy.

### Úloha 6

Cordon a drain určený worker Node podľa zadania, bez zmazania DaemonSet Podov; po maintenance ho uncordon.

### Úloha 7

Vytvor Gateway API HTTPRoute alebo Ingress podľa dostupných APIs a pripoj ho na existujúci backend Service.

### Úloha 8

Vykonaj a validuj etcd snapshot na určený secure path podľa poskytnutých endpoint/cert paths.

## 19. Review po timed lab-e

Po skončení klasifikuj každú chybu:

- knowledge gap,
- command syntax,
- context/namespace,
- YAML indentation/type,
- neoverený predpoklad,
- slabá diagnostika,
- time management,
- deštruktívna zmena,
- chýbajúca validation.

Pre každú chybu vytvor konkrétny drill, nie všeobecné „viac sa učiť“.

## 20. Metrics progresu

Sleduj:

- percento bodov,
- body za minútu,
- median task completion,
- počet skipped-returned tasks,
- context mistakes,
- invalid apply attempts,
- tasks bez final validation,
- troubleshooting root-cause accuracy,
- čas strávený v dokumentácii.

Cieľom je stabilita výkonu, nie jeden výnimočný výsledok.

## 21. Anti-patterny

### Tréning iba cez video

Nevytvára command-line a failure-isolation reflex.

### Rovnaký lab stále dokola

Memoruješ answers, nie mechanizmy.

### Žiadny timer

Neučíš sa prioritizovať.

### Validácia iba cez `kubectl get`

Resource môže existovať, ale nespĺňať presný contract.

### Riešenie všetkých úloh v poradí

Jedna ťažká úloha zablokuje zvyšok bodov.

### Dlhé hľadanie dokumentácie bez presnej otázky

Spotrebuje čas bez zmeny cluster state-u.

### Tréning iba application YAML

CKA má vysokú váhu troubleshooting a cluster lifecycle tém.

## 22. Kontrolné otázky

1. Prečo timed lab musí merať aj validation a context chyby?
2. Ako rozdelíš 120 minút?
3. Kedy úlohu preskočíš?
4. Čo obsahuje task intake protocol?
5. Prečo je imperative skeleton užitočný?
6. Ako navrhneš body podľa oficiálnych domén?
7. Ktoré dôkazy použiješ pre workload, Service a PVC?
8. Ako odlíšiš knowledge gap od time-management chyby?
9. Prečo treba rotovať parametre a root causes?
10. Aké metrics budeš sledovať medzi simuláciami?

## Praktické laby

Rozšírený vykonávací protokol a tréningové sety patria do [CKA labs](../../labs/cka/README.md).

## Glossary impact

Relevantné pojmy: CKA, performance-based exam, timed lab, domain-weighted lab, task intake protocol, verification pass, imperative skeleton, time-boxing, skip-and-return strategy, self-grading, command fluency a exam simulation.

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
