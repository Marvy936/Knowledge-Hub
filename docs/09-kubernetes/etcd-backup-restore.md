# etcd backup a restore

Etcd snapshot nie je iba súbor databázy. Je to recovery artifact pre konkrétnu API-state generation, revision a cluster identity. Bez integrity, PKI/encryption materialu, external-state inventory, application-data koordinácie a testovaného restore postupu môže byť snapshot technicky validný, ale prevádzkovo nepoužiteľný alebo nebezpečný.

Táto kapitola používa jeden dominantný lifecycle:

```text
recovery objectives a authoritative state inventory
→ healthy etcd source, cluster identity a revision
→ snapshot creation a metadata
→ integrity, encryption a offsite retention
→ complete recovery-set binding
→ repair-versus-restore decision
→ write isolation a evidence preservation
→ restore ako nový logical etcd cluster
→ revision bump/compaction a API-server rebind
→ controller, external a application-state reconciliation
→ traffic reopening a recovery closure
→ recurring restore rehearsal a retention
```

## 1. Atlas recovery subject

Cluster `atlas-prod-eu2` používa 3-member stacked etcd. Recovery subject musí obsahovať:

```text
Kubernetes cluster identity a control-plane endpoint
etcd cluster ID, member names/IDs a peer URLs
etcd version a data-directory generation
snapshot hash, revision, key count, size a creation time
Kubernetes/etcd PKI a certificate generation
API encryption configuration a KMS/key history
static Pod/kubeadm/component configuration
external resource inventory
application-data backup generations
RPO, RTO a traffic-reopen verdict
```

Snapshot filename ani timestamp bez trusted metadata túto identitu nenahrádza.

## 2. Čo etcd obsahuje a čo nie

Etcd typicky obsahuje Kubernetes API objects:

- workload specs/status;
- Secrets, ConfigMaps a ServiceAccounts;
- RBAC a admission configuration uloženú cez API;
- Services, EndpointSlices, Leases a controller state;
- CRDs a custom resources;
- PVC/PV/VolumeAttachment objects.

Neobsahuje automaticky:

- persistent-volume content;
- container images;
- host filesystem a local PKI files;
- external LB, DNS, IAM, disks alebo queues;
- API encryption config file, KMS keys a CA private keys;
- Git/IaC source;
- application-consistent database backup;
- logs, metrics a traces mimo API.

Etcd restore obnovuje API intent/history do snapshot revision. Neobnovuje automaticky celý business system.

## 3. Quorum, repair a disaster recovery

Etcd cluster potrebuje majority:

```text
quorum = floor(member_count / 2) + 1
```

Ak quorum existuje, restore nemusí byť správna prvá akcia. Často je bezpečnejšie:

- obnoviť connectivity;
- nahradiť failed member;
- odstrániť disk pressure;
- opraviť TLS/time;
- vykonať maintenance/defragmentation;
- obnoviť API server endpoint.

Snapshot restore je disaster-recovery alebo logical rollback operation. Všetky changes po snapshot revision môžu byť stratené a external state sa môže rozísť.

## 4. Snapshot creation subject

Preferovaný online snapshot používa healthy endpoint a authenticated TLS client. Backup operation musí zaznamenať:

- selected endpoint/member a health;
- leader/member inventory;
- source cluster ID a current revision;
- command/tool version;
- start/end time;
- destination path a free space;
- resulting hash, keys a size;
- copy/retention destination;
- operation identity a audit event.

Live filesystem copy bez koordinácie nie je ekvivalent API snapshotu. Offline data-directory backup vyžaduje riadené zastavenie a exact etcd-version workflow.

## 5. Integrity a recovery-set binding

`etcdutl snapshot status` overuje hash, revision, keys a size. To je artifact integrity, nie úplný recovery test.

Snapshot musí byť viazaný na recovery set:

```text
etcd snapshot
+ etcd a Kubernetes PKI
+ API encryption/KMS material
+ kubeadm/static Pod/component config
+ control-plane endpoint/infra metadata
+ CNI/CSI/DNS/admission versions
+ Git/IaC a image artifacts
+ application-data backups
+ restore runbook a authorized identities
```

Snapshot obsahuje citlivé API dáta vrátane Secrets. Ukladaj ho off-host, mimo rovnakého failure domainu, šifrovane, s least privilege, immutable retention a auditom.

## 6. RPO, RTO a cross-system consistency

Etcd RPO je maximálna prijateľná strata API-state changes. Musí byť koordinovaný s:

- database/data-volume RPO;
- queue a object-storage checkpoints;
- deployment/schema generation;
- certificate/secret rotation;
- external LB/DNS/cloud resources.

Príklad:

```text
etcd snapshot: 10:00
database backup: 09:30
release 5.4.0/schema change: 09:50
```

Technicky úspešný etcd restore môže vytvoriť workload, ktorý očakáva schema absentnú v databázovom backup-e.

RTO sa meria až po obnovení API, controllers, storage, external dependencies a critical business journey — nie po štarte etcd processu.

## 7. Restore decision a evidence boundary

Pred restore zachyť:

- member list, health, leader a quorum;
- current revisions/alarms/hash evidence;
- logs a data directories;
- posledný healthy timestamp;
- available snapshots a metadata;
- recent RBAC, Secret, Deployment, PVC a CRD changes;
- external resources vytvorené po snapshot čase;
- application-data backup generations;
- suspected corruption/disk/root-cause evidence.

Neobnovuj jeden member do existujúceho quorum ad hoc. Restore vytvára nový logical cluster/member state; miešanie old a restored state môže vytvoriť identity alebo consensus konflikt.

## 8. Write isolation a restored cluster generation

Po rozhodnutí restore:

```text
contain client/API writes
→ preserve old member data a logs
→ verify selected snapshot/recovery set
→ restore všetky planned members do clean data dirs
→ configure exact member names/peer URLs
→ establish one restored cluster identity
→ start/verify etcd
→ point all API servers na rovnaký cluster
```

Počas transition nesmú niektoré API servers zapisovať do starého etcd a iné do restored etcd.

TLS, SANs, peer mapping, file permissions, system time a initial-cluster configuration musia zodpovedať novej topology.

## 9. Revision rollback a Kubernetes informer caches

Restore vráti keyspace na snapshot revision. Controllers a clients mohli pred incidentom vidieť vyššie revisions a držať caches/watch state.

Etcd recovery tooling podporuje:

- revision bump;
- marking restored history compacted.

Cieľom je vytvoriť revision vyššiu než predchádzajúca observed history a prinútiť watchers k relistu namiesto pokračovania zo stale cache assumption. Hodnota bump-u musí vychádzať z revision rate, outage window a testovaného runbooku; arbitrárny malý delta nemusí stačiť.

## 10. API server a encryption boundary

Všetky API servers musia používať:

- rovnaké restored etcd endpoints;
- správny etcd CA/client certificate;
- rovnaký storage prefix;
- compatible API server version;
- správnu encryption configuration a KMS access.

Snapshot môže byť hash-validný, ale Secrets nečitateľné, ak chýba staršia encryption key generation alebo KMS provider. Recovery set musí zachovať key order/history potrebnú na decrypt existujúcich records.

## 11. Post-restore reconciliation

### Etcd a API

Over:

```text
member health, one leader a cluster ID
revision/raft consistency
latency, disk space a alarms
API read, write a watch
admission a authentication
```

### Kubernetes controllers

Over leadership, queues, relists a reconciliation pre:

- Deployments/StatefulSets/Jobs;
- Services/EndpointSlices;
- PVC/PV/VolumeAttachments;
- Secrets/ServiceAccounts/RBAC;
- CRDs/operators;
- CNI/CSI/DNS a admission webhooks.

### External state

Etcd rollback môže:

- obnoviť object pre už neexistujúci cloud resource;
- odstrániť object pre stále existujúci disk/LB/DNS/certificate;
- vrátiť staré Secret alebo RBAC intent;
- spustiť controller, ktorý external resource znovu vytvorí alebo zmaže.

Pred otvorením trafficu analyzuj destructive reconcile possibilities a rozhodni canonical external state.

## 12. Application a traffic acceptance

Recovery verdict musí overiť:

- correct deployment/image/schema generation;
- správne PVC/data a fencing identity;
- current credentials/certificates;
- queue/work-item consistency;
- Service/DNS/Gateway paths;
- idempotency a duplicate prevention;
- end-to-end payment transaction;
- forbidden old credential/RBAC/external-resource outcomes.

Traffic otvor až po coordinated API, external a application consistency verdict-e.

## 13. Causal walkthrough: API funguje, ale controllers sa po restore správajú nekonzistentne

### Incident

Po disk corruption a strate quorum bol cluster obnovený zo snapshotu z 10:00. O 10:40 API read/write funguje a etcd má leadera, ale niektoré controllers nereagujú na resources. EndpointSlices a operator-managed database state sú nekonzistentné.

### Exact subject

Fixuj:

- old cluster ID/member/revision evidence;
- selected snapshot hash a revision;
- restore command, data dirs a member mapping;
- revision bump/compaction flags;
- API server endpoints/encryption generation;
- controller Pod UID, leader term, watch resourceVersion a cache start time;
- exact object UID/generation a external resource identity;
- application-data backup time.

### Competing hypotheses

1. jeden API server stále používa starý etcd;
2. mixed old/restored members vytvorili cluster konflikt;
3. etcd TLS alebo encryption key zlyháva iba pre časť records;
4. controller leader election je nefunkčné;
5. admission webhook blokuje reconciliation;
6. restored revision je nižšia než controller cache history;
7. revision bump bol nedostatočný;
8. compaction marker nebol použitý;
9. external resource sa rozchádza s restored objectom;
10. application data generation nezodpovedá API state-u.

### Discriminating observations

Porovnaj API server etcd endpoints, etcd cluster IDs/revisions, restore metadata, controller logs/watch errors/relist events, leader leases, object UIDs/generations, external provider audit a data backup lineage.

Finding:

```text
snapshot revision: 8.1M
pre-incident controllers videli: >9.0M
restore bez adequate revision bump a mark-compacted
→ long-lived controller caches/watch assumptions ostali nad restored history
→ časť controllers nere-listovala authoritative state
→ API requests fungovali, reconciliation graph bol nekonzistentný
```

### Containment

- neotváraj production traffic;
- zastav destructive external reconcilers, ak ich outcome je neistý;
- zachovaj restored aj old data dirs, logs a exact commands;
- zastav ďalšie manual object edits;
- inventarizuj external resources a application data pred opakovaním restore.

### Authoritative recovery

- zopakuj restore z verified snapshotu do clean data directories;
- vytvor jeden consistent restored cluster;
- použij testovaný revision bump nad pre-incident high-water mark a `mark-compacted` podľa podporovanej etcd verzie;
- bindni všetky API servers na restored cluster;
- reštartuj/reconcile controllers tak, aby vykonali fresh list/watch;
- reconciliuj external resources podľa canonical owner/data identity;
- zosúlaď deployment/schema/data/secret generations.

### Verify original a forbidden outcomes

Over:

1. etcd health, one leader, cluster ID a expected revision;
2. API read/write/watch z každého endpointu;
3. controllers vykonali fresh relist a queues konvergujú;
4. Services/EndpointSlices, storage a operators zodpovedajú desired state-u;
5. external LB/DNS/disks/certificates nemajú orphan alebo duplicate generation;
6. application data je compatible s restored API state-om;
7. old Secrets/RBAC/credentials nie sú znovu použiteľné;
8. payment journey uspeje exactly once;
9. second reconciliation je bounded/no-op podľa intentu;
10. RPO/RTO a actual data loss sú zaznamenané.

### Earlier controls

Použi revision-rate telemetry, automatic high-water metadata pri backup-e, offsite immutable snapshots, full recovery-set manifest, isolated periodic restore, controller relist verification, external-state inventory a application cross-system recovery test.

## 14. Ďalšie failure boundaries

### Snapshot command skončil úspešne, artifact je chybný

Wrapper exit code nepreukazuje hash, size ani complete offsite copy. Over snapshot status a retention manifest.

### Restored etcd beží, API server nie

Skontroluj endpoints, TLS SAN/client identity, storage prefix, encryption config/KMS a static Pod manifest.

### API funguje, Secrets sú nečitateľné

Chýba encryption key/KMS history alebo provider order. Neprepisuj ciphertext novým key materialom naslepo.

### Po restore chýbajú novšie resources

Je to očakávaná strata po snapshot revision. Reaplikuj source až po external-state reconciliation, aby si nevytvoril duplicates alebo destructive deletes.

### Member hash mismatch/corruption

Zastav destructive automation, zachovaj disks/logs a postupuj podľa etcd corruption recovery. Restore na rovnaký chybný disk zopakuje incident.

### Restore test overil iba `snapshot status`

To nie je DR test. Potrebný je isolated cluster, API/controllers, external/application consistency a measured RTO.

## 15. Referenčný katalóg

### Snapshot evidence

```text
source cluster/member/leader
snapshot hash/revision/keys/size/time
tool a etcd version
encryption a PKI binding
offsite copy a retention
restore rehearsal verdict
```

### Recovery phases

1. decide repair vs restore;
2. isolate writes a preserve evidence;
3. restore clean logical cluster;
4. bind API and encryption;
5. force fresh watcher state;
6. reconcile Kubernetes a external resources;
7. restore/verify application data;
8. reopen traffic;
9. record RPO/RTO a closure.

## 16. Anti-patterny

- snapshot iba na rovnakom etcd disku;
- backup bez hash/status a restore testu;
- restore jedného člena do existujúceho quorum;
- mixed old a restored member data;
- restore bez encryption/PKI materialu;
- predpoklad, že etcd obsahuje PV dáta;
- traffic otvorený po `etcd endpoint health` bez controller/application testu;
- revision bump zvolený náhodne;
- Git source reaplikovaný bez external-state reconciliation;
- cleanup backupov bez immutable retention.

## 17. Kontrolné otázky

1. Čo tvorí exact etcd recovery subject?
2. Kedy je member repair vhodnejší než snapshot restore?
3. Prečo snapshot integrity nie je recovery readiness?
4. Čo musí obsahovať complete recovery set?
5. Prečo restore vytvára nový logical etcd cluster?
6. Aký problém rieši revision bump a `mark-compacted`?
7. Ako encryption-at-rest mení backup requirements?
8. Prečo controllers a external resources môžu po restore konať nebezpečne?
9. Ako koordinuješ etcd RPO s application-data RPO?
10. Ktoré business a forbidden outcomes uzatvárajú restore?

## Glossary impact

Relevantné pojmy: etcd recovery subject, snapshot evidence manifest, API-state generation, recovery-set binding, repair-versus-restore verdict, restored logical cluster, revision high-water mark, informer relist boundary, external-state reconciliation, cross-system recovery generation, traffic-reopen verdict, recovery closure a restore-rehearsal evidence.

## Oficiálna dokumentácia

- [Operating etcd clusters for Kubernetes](https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/)
- [etcd disaster recovery](https://etcd.io/docs/v3.7/op-guide/recovery/)
- [How to save the etcd database](https://etcd.io/docs/v3.7/tasks/operator/how-to-save-database/)
- [Securing a cluster](https://kubernetes.io/docs/tasks/administer-cluster/securing-a-cluster/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Cluster installation a lifecycle](cluster-installation-lifecycle.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Upgrades →](upgrades.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
