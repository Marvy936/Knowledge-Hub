# CKA troubleshooting drills

Praktický scenárový index pre performance-based Kubernetes troubleshooting. Každý drill má mať jednu známu primárnu chybu, merateľný expected state a bezpečný reset.

Autoritatívny teoretický kontext: [CKA troubleshooting drills](../../docs/10-helm-and-cka/cka-troubleshooting-drills.md).

## Vykonávací protokol

Pre každý scenár:

```text
1. Spusti timer.
2. Zapíš symptóm a scope.
3. Zachovaj relevantné evidence.
4. Pomenuj root cause pred opravou.
5. Urob minimálnu zmenu.
6. Vykonaj hard validation.
7. Resetni prostredie.
8. Zapíš diagnosis/repair/verify čas.
```

## Scenáre

| ID | Scenár | Primárna vrstva | Limit |
|---|---|---|---:|
| CKA-TS-001 | CrashLoopBackOff po ConfigMap zmene | Pod/config | 6 min |
| CKA-TS-002 | Pending Pod pre node affinity | Scheduler | 6 min |
| CKA-TS-003 | Pending Pod pre netolerovaný taint | Scheduler | 6 min |
| CKA-TS-004 | Service selector bez endpoints | Service | 5 min |
| CKA-TS-005 | Wrong targetPort | Service/app | 6 min |
| CKA-TS-006 | NetworkPolicy blokuje klienta | NetworkPolicy | 8 min |
| CKA-TS-007 | Default-deny blokuje DNS | NetworkPolicy/DNS | 8 min |
| CKA-TS-008 | CoreDNS upstream loop | DNS | 10 min |
| CKA-TS-009 | ImagePullBackOff pre Secret scope | Registry/Secret | 7 min |
| CKA-TS-010 | PVC Pending pre StorageClass | Storage | 7 min |
| CKA-TS-011 | Multi-Attach po Node failure | CSI/storage | 12 min |
| CKA-TS-012 | Node NotReady pre kubelet | Node | 10 min |
| CKA-TS-013 | Static API server Pod chybný cert path | Control plane | 12 min |
| CKA-TS-014 | Admission webhook timeout | API/admission | 10 min |
| CKA-TS-015 | RBAC wrong namespace binding | RBAC | 7 min |
| CKA-TS-016 | Deployment rollout blocked readiness | Workload | 8 min |
| CKA-TS-017 | HPA unknown CPU utilization | Autoscaling | 8 min |
| CKA-TS-018 | Gateway route unresolved backend | Gateway API | 10 min |
| CKA-TS-019 | Container OOMKilled | Resources | 7 min |
| CKA-TS-020 | Pod stuck Terminating pre volume detach | Lifecycle/storage | 10 min |

## CKA-TS-001 — CrashLoopBackOff po ConfigMap zmene

Fault injection:

- zmeň expected key `DATABASE_URL` na `DB_URL`,
- zachovaj Deployment reference na pôvodný key,
- nechaj liveness probe aktívnu.

Expected diagnosis:

- previous logs ukazujú chýbajúcu/invalid configuration,
- probe nie je primárna príčina.

Validation:

```bash
kubectl rollout status deployment/api -n production
kubectl get pod -n production -l app=api
```

## CKA-TS-002 — Pending Pod pre node affinity

Fault injection:

- nastav required node affinity na neexistujúcu label value.

Expected diagnosis:

- `FailedScheduling` Event explicitne uvádza node affinity mismatch.

Repair:

- oprav požadovanú value alebo labels podľa zadania,
- nepoužívaj `nodeName`.

## CKA-TS-003 — Pending Pod pre taint

Fault injection:

```bash
kubectl taint node <node> dedicated=batch:NoSchedule
```

- workload nemá toleration.

Validation:

- Pod je Scheduled iba po pridaní presnej toleration,
- taint sa neodstraňuje, ak je súčasťou desired node-pool policy.

## CKA-TS-004 — Service selector bez endpoints

Fault injection:

- Service selector `app=checkout`,
- Pods label `app=check-out`.

Validation:

```bash
kubectl get endpointslice -n shop -l kubernetes.io/service-name=checkout
```

## CKA-TS-005 — Wrong targetPort

Fault injection:

- Service targetPort 8080,
- application počúva na 8000.

Expected diagnosis:

- EndpointSlice existuje,
- direct PodIP:8000 funguje,
- Service path nefunguje.

## CKA-TS-006 — NetworkPolicy blokuje klienta

Fault injection:

- ingress policy vyberá backend,
- allowed client selector používa chybný key.

Validation:

- povolený client uspeje,
- nepovolený client zlyhá.

## CKA-TS-007 — Default-deny blokuje DNS

Fault injection:

- pridaj default-deny egress bez DNS allow rule.

Repair:

- povoľ presný DNS destination/protocol model clusteru,
- neotváraj celý egress.

## CKA-TS-008 — CoreDNS upstream loop

Fault injection:

- nakonfiguruj forward target na resolver, ktorý vracia request späť do CoreDNS podľa lab topológie.

Evidence:

- CoreDNS logs,
- `/etc/resolv.conf`,
- cluster-local record môže fungovať, external resolution zlyháva alebo loopuje.

## CKA-TS-009 — ImagePullBackOff pre Secret scope

Fault injection:

- registry Secret vytvor v namespace `default`,
- Pod je v `shop`.

Repair:

- vytvor alebo prenes správny namespaced Secret podľa zadania,
- nepridávaj broad credentials do default ServiceAccount bez potreby.

## CKA-TS-010 — PVC Pending

Fault injection:

- PVC odkazuje na `fast-ssd`, dostupná StorageClass je `fast`.

Validation:

- PVC Bound,
- consumer Pod má mounted volume.

## CKA-TS-011 — Multi-Attach

Fault injection:

- RWO volume viazaný na Pod na NotReady Node-e,
- replacement Pod plánovaný na iný Node.

Bezpečnostná požiadavka:

- kandidát musí identifikovať starý writer/attachment,
- nesmie force-delete storage objects bez fencing analýzy.

## CKA-TS-012 — Node NotReady

Fault injection:

```bash
sudo systemctl stop kubelet
```

Variácie:

- chybný kubelet config path,
- runtime down,
- expired client cert v izolovanom lab-e.

Validation:

- Node Ready,
- Lease sa obnovuje,
- workload recovery overená.

## CKA-TS-013 — Static API server Pod

Fault injection:

- zmeň jednu certificate alebo hostPath cestu v static Pod manifeste.

Evidence:

- kubelet logs,
- runtime container logs,
- manifest diff.

Repair:

- oprav iba chybnú path,
- neobnovuj celý cluster.

## CKA-TS-014 — Admission webhook timeout

Fault injection:

- webhook service nemá endpoints alebo používa neplatný CA bundle v disposable lab-e.

Expected diagnosis:

- nie všetky API requests zlyhávajú,
- failure sa viaže na matching webhook rules.

## CKA-TS-015 — RBAC wrong namespace binding

Fault injection:

- Role existuje v `team-a`,
- RoleBinding omylom v `team-b`.

Validation:

```bash
kubectl auth can-i get pods \
  --as=system:serviceaccount:team-a:reader \
  -n team-a
```

Negatívne overenie pre Secrets/write verbs je povinné.

## CKA-TS-016 — Deployment readiness

Fault injection:

- readiness path `/readyz`, application poskytuje `/ready`.

Expected diagnosis:

- container Running,
- Pod NotReady,
- Deployment progress deadline alebo rollout wait.

## CKA-TS-017 — HPA unknown utilization

Fault injection:

- odstráň CPU requests z target Deploymentu.

Validation:

- HPA má current/desired metric,
- nové Pody sa dajú vytvoriť v quota/capacity limite.

## CKA-TS-018 — Gateway unresolved backend

Fault injection:

- HTTPRoute backend port alebo Service name neexistuje.

Evidence:

- Route `Accepted` môže byť true,
- `ResolvedRefs` false.

Validation:

- Route status je prijatý a references resolved,
- request cez listener uspeje.

## CKA-TS-019 — OOMKilled

Fault injection:

- nastav memory limit pod stabilnú working set aplikácie.

Expected diagnosis:

- terminated reason `OOMKilled`,
- Node nemusí mať MemoryPressure.

Repair:

- uprav workload resource contract podľa zadania,
- nevypínaj limits bez analýzy.

## CKA-TS-020 — Stuck Terminating

Fault injection:

- volume detach/finalizer alebo Node unreachable podľa lab capabilities.

Bezpečnostná požiadavka:

- odlíšiť API object deletion od skutočného process/storage writer lifecycle,
- force delete iba ako explicitne povolený posledný krok.

## Reset checklist

```text
[ ] odstránené fault-injection resources
[ ] obnovené labels/taints/config
[ ] všetky Nodes Ready
[ ] system Pods Running
[ ] test namespaces čisté
[ ] PVC/PV retained alebo zmazané podľa lab policy
[ ] žiadne broad RBAC alebo privileged debug resources
[ ] nový baseline snapshot alebo cluster reset
```

## Review template

```text
ID:
Čas diagnose:
Čas repair:
Čas verify:
Prvá hypotéza:
Root cause:
Použité evidence:
Chybný zásah:
Minimálna oprava:
Hard validation:
Opakovací drill:
```
