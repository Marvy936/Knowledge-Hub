# CKA timed labs

Táto oblasť obsahuje originálne praktické sety pre CKA prípravu. Úlohy nereprodukujú skutočné exam questions. Majú trénovať command fluency, context discipline, prioritizáciu a hard validation.

Autoritatívny teoretický kontext: [CKA timed labs](../../docs/10-helm-and-cka/cka-timed-labs.md).

## Pravidlá vykonania

1. Použi disposable alebo obnoviteľný lab cluster.
2. Nastav presný timer.
3. Pred štartom nečítaj riešenia ani expected root causes.
4. Pri každej úlohe zapíš context, namespace a validation criterion.
5. Posledných 10–15 % času vyhraď na verification pass.
6. Po skončení zaznamenaj chyby podľa typu, nie iba výsledné skóre.

## Spoločný scoring

| Stav | Body |
|---|---:|
| Plne splnené a validované | 100 % úlohy |
| Funkčný výsledok, chýba časť constraints | 50–80 % |
| Čiastočný relevantný stav | 20–40 % |
| Nesprávny cluster/namespace alebo deštruktívna zmena | 0 % |

## Lab A — 45 minút

### 1. Deployment rollout — 8 bodov

Context `cluster-a`, namespace `shop`.

- Deployment `catalog` nastav na image `nginx:1.27`.
- Zachovaj 3 replicas.
- Počas rollout-u nesmie byť nedostupná viac než jedna replika.
- Validácia: rollout complete a presný image v Pod template.

### 2. ConfigMap a environment — 5 bodov

- Vytvor ConfigMap `catalog-config` s `MODE=production`.
- Deployment `catalog` musí hodnotu čítať ako environment variable `MODE`.
- Ostatné environment variables nesmú byť odstránené.

### 3. Service a endpoints — 6 bodov

- Vytvor ClusterIP Service `catalog`.
- Service port 80, target port 80 pre použitý image.
- Validácia: ready EndpointSlice a HTTP odpoveď z test Podu.

### 4. NetworkPolicy — 8 bodov

- Izoluj ingress do Podov `app=catalog`.
- Povoľ TCP/80 iba z Podov `app=frontend` v rovnakom namespace.
- Ostatný ingress zostáva blokovaný.

### 5. RBAC — 6 bodov

- ServiceAccount `reporter` môže `get`, `list`, `watch` Pods v namespace `shop`.
- Nesmie meniť Pods ani čítať Secrets.
- Validácia cez `kubectl auth can-i --as=...`.

### 6. Troubleshooting — 12 bodov

- Service `checkout` nemá endpoints.
- Oprav root cause bez zmeny Service name alebo portu.
- Validácia: ready EndpointSlice a úspešný request.

## Lab B — 60 minút

### 1. Scheduling — 8 bodov

- Deployment `batch` musí bežať iba na Nodes s `workload=batch`.
- Musí tolerovať `dedicated=batch:NoSchedule`.
- Nevytváraj `nodeName` binding.

### 2. Storage — 8 bodov

- V namespace `data` vytvor PVC `reports` s veľkosťou 1 Gi a StorageClass `fast`.
- Pripoj ho do Podu `writer` na `/data`.
- Zapíš file a over jeho pretrvanie po replacement-e Podu.

### 3. CronJob — 6 bodov

- Schedule každých 10 minút.
- `concurrencyPolicy: Forbid`.
- História: 2 successful, 1 failed.
- Job musí skončiť úspešne.

### 4. HPA — 8 bodov

- Deployment `api` má HPA target 60 % CPU.
- Oprav chýbajúce prerequisites tak, aby HPA vedel vypočítať utilization.
- Zachovaj existujúce memory nastavenia.

### 5. DNS — 6 bodov

- Host-network Pod nevie používať cluster DNS.
- Oprav DNS policy bez odstránenia host networking requirementu.

### 6. Node maintenance — 10 bodov

- Cordon a drain Node podľa zadania.
- Ignoruj DaemonSet Pods podľa bezpečného maintenance workflowu.
- Po simulovanej údržbe Node uncordon.
- Validácia: Node schedulable a Ready.

## Lab C — 90 minút

### 1. Stateful workload — 10 bodov

- Headless Service `db`.
- StatefulSet `db`, 3 replicas.
- Stabilné names a per-replica 1 Gi PVC.
- Pods musia mať readiness probe.

### 2. Gateway/Ingress — 8 bodov

- Použi API dostupné v clustri.
- Host `shop.example.test`, path `/catalog`.
- Backend Service `catalog`, port 80.
- Validácia cez Host header z test klienta.

### 3. NetworkPolicy a DNS — 10 bodov

- Default-deny egress pre namespace `restricted`.
- Povoľ DNS a HTTPS iba do zadaného namespace/service selectoru.
- Over, že iný egress zlyhá.

### 4. Etcd snapshot — 12 bodov

- Použi poskytnutý endpoint, CA, cert a key.
- Ulož snapshot na zadaný secure path.
- Validuj ho cez podporovaný `etcdutl snapshot status`.
- Nemeň etcd data directory.

### 5. Control-plane diagnosis — 12 bodov

- Jeden static Pod component sa nespúšťa.
- Nájdi chybu v manifest/flag/path vrstve.
- Urob minimálnu opravu a over health.

### 6. Service troubleshooting — 10 bodov

- Service má ready endpoints, ale traffic z klienta zlyhá.
- Oddel PodIP, ServiceIP a DNS cestu.
- Oprav root cause bez odstránenia NetworkPolicy ochrany.

### 7. Rollout a rollback — 8 bodov

- Deployment aktualizuj na zadaný image.
- Ak readiness zlyhá, identifikuj dôvod a vráť funkčnú revision.
- Validácia: dostupné replicas a presná revision/image.

## Lab D — 120 minút

Použi 100-bodové rozdelenie podľa aktuálnych CKA domén:

- Troubleshooting — 30 bodov,
- Cluster architecture/configuration — 25 bodov,
- Services/networking — 20 bodov,
- Workloads/scheduling — 15 bodov,
- Storage — 10 bodov.

Zostav 15–20 úloh rotáciou z Lab A–C a z [CKA troubleshooting drills](../../troubleshooting/cka/README.md). Zmeň namespaces, images, selectors, paths a root causes, aby riešenie nebolo založené na pamäti.

## Verification pass

Na konci každého labu:

```text
[ ] správne contexts a namespaces
[ ] všetky resources existujú pod správnou identity
[ ] rollouty dokončené
[ ] Services majú ready endpoints
[ ] network allow aj deny paths overené
[ ] PVC Bound a mount funkčný
[ ] RBAC pozitívne aj negatívne overenie
[ ] Nodes Ready/schedulable podľa zadania
[ ] žiadne neplánované privileged alebo broad zmeny
[ ] pracovné debug resources odstránené
```

## Review záznam

```text
Dátum:
Lab:
Čas:
Skóre:
Nevyriešené úlohy:
Context chyby:
Nevalidované úlohy:
Najpomalšia oblasť:
Root-cause chyby:
Nasledujúce 3 drilly:
```
