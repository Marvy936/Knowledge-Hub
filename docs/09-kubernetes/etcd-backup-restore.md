# etcd backup a restore

Etcd je konzistentný distribuovaný key-value store, v ktorom Kubernetes uchováva API object state. Pri self-managed control plane je etcd snapshot jadrom cluster-state backupu, ale nie je úplným backupom celej platformy ani application dát. Obnova musí rešpektovať quorum, revision history, PKI, encryption keys, API server konfiguráciu a external resources.

## 1. Čo etcd obsahuje

Etcd typicky obsahuje:

- Kubernetes API objekty,
- workload specs a status,
- Secrets a ConfigMaps,
- RBAC a ServiceAccounts,
- CRDs a custom resources,
- leases, endpoints a controller state,
- admission a cluster configuration uloženú cez API.

Etcd neobsahuje automaticky:

- data v persistent volumes,
- container images,
- Node filesystemy,
- external load balancers, DNS alebo IAM,
- Git repository s deklaratívnym source,
- private keys, ktoré sú iba na filesysteme,
- encryption-at-rest configuration file a external KMS keys,
- logs, metrics a traces uložené mimo API.

## 2. Quorum model

Etcd používa consensus. Cluster s `N` members potrebuje väčšinu:

```text
quorum = floor(N / 2) + 1
```

Príklady:

- 1 member → potrebuje 1,
- 3 members → potrebuje 2,
- 5 members → potrebuje 3.

Pridanie párneho člena nezvýši počet tolerovaných súčasných výpadkov oproti predchádzajúcemu nepárnemu počtu a môže rozšíriť operational surface.

## 3. Stacked a external etcd

### Stacked etcd

Etcd member beží na každom control-plane Node-e, často ako static Pod. Data directory býva napríklad:

```text
/var/lib/etcd
```

### External etcd

Etcd cluster má vlastné hosts, certificates, monitoring a lifecycle.

Pri oboch modeloch musí backup vedieť:

- endpointy,
- CA a client certificate paths,
- etcd verziu,
- member topology,
- data directory,
- API server etcd connection configuration.

## 4. Snapshot vs. filesystem copy

### Online snapshot

Preferovaný spôsob:

```bash
ETCDCTL_API=3 etcdctl \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt \
  --key=/etc/kubernetes/pki/etcd/healthcheck-client.key \
  snapshot save /secure-backup/etcd-snapshot.db
```

Snapshot získaný cez etcd API má integrity metadata.

### Filesystem copy

Kopírovanie live data directory bez koordinácie môže vytvoriť nekonzistentnú alebo neoverenú kópiu. Pri offline data-directory backup-e musí byť etcd bezpečne zastavený a musí sa zachovať celý required state podľa etcd dokumentácie.

## 5. Snapshot z leadera

Snapshot je možné získať z healthy endpointu. Pri automatizácii over:

- endpoint health,
- kto je leader,
- aktuálnu revision,
- snapshot duration a size,
- filesystem capacity,
- úspešné dokončenie a hash.

Nespoliehaj sa iba na exit code wrapper skriptu; validuj výsledný snapshot.

## 6. Snapshot status

Moderné etcd verzie používajú `etcdutl` na offline snapshot inspection a restore:

```bash
etcdutl --write-out=table snapshot status /secure-backup/etcd-snapshot.db
```

Over najmä:

- hash/integrity,
- revision,
- total keys,
- size,
- creation timestamp z backup metadata,
- etcd/tool version compatibility.

Snapshot file bez úspešného status checku a restore testu nie je dôveryhodný backup.

## 7. Backup frekvencia

Frekvencia vychádza z RPO:

```text
maximálna prijateľná strata API state-u
```

Cluster s častými:

- deployments,
- Job/CronJob zmenami,
- certificate requests,
- operators/custom resources,
- dynamic provisioning,
- identity a RBAC zmenami

môže potrebovať častejšie snapshots než statický cluster.

RPO etcd a RPO application dát musia byť koordinované. Obnova API state-u na čas T a databázy na čas T−6h môže vytvoriť nekonzistentný systém.

## 8. Backup storage

Snapshot ukladaj:

- mimo etcd hosta,
- mimo rovnakého failure domainu,
- šifrovane,
- s least-privilege write/read identities,
- s immutable alebo object-lock retention podľa rizika,
- s checksumom a metadata,
- s pravidelným restore testom.

Snapshot môže obsahovať Kubernetes Secrets a ďalšie citlivé API dáta. Aj pri encryption at rest musia byť chránené encryption keys a configuration.

## 9. Backup set

Kompletný recovery set zahŕňa:

- etcd snapshot,
- etcd CA/client/peer certificates podľa topológie,
- Kubernetes CA a ServiceAccount signing keys podľa recovery plánu,
- API server encryption configuration,
- external KMS state alebo keys,
- static Pod manifests/component config,
- kubeadm config a cluster endpoint metadata,
- CNI/CSI/add-on versions a manifests,
- persistent application data backups,
- DNS/LB/IAM/firewall infrastructure source,
- restore runbook.

Private keys v backup sete musia mať silnejší access model než bežné manifests.

## 10. Kedy restore nepoužiť

Restore nie je prvá reakcia na každý etcd incident.

Ak quorum stále existuje, môže byť vhodnejšie:

- opraviť alebo nahradiť failed member,
- obnoviť connectivity,
- odstrániť disk pressure,
- vykonať defragmentáciu/maintenance,
- vyriešiť certificate expiry,
- obnoviť API server endpoint.

Snapshot restore je cluster-state rollback alebo disaster recovery. Môže stratiť všetky zmeny po snapshot revision.

## 11. Recovery rozhodnutie

Pred obnovou zaznamenaj:

- posledný healthy timestamp,
- aktuálnu member list a health,
- dostupnosť quorum,
- podozrenie na corruption,
- snapshot revisions a časy,
- posledné významné workload/storage/RBAC zmeny,
- dostupnosť application data backups,
- možnosť exportovať current evidence.

Náhodné spustenie restore na jednom členovi existujúceho clusteru môže vytvoriť split-brain alebo identity konflikt.

## 12. Restore vytvára nový logical cluster

Etcd restore typicky vytvorí nový data directory a nové member/cluster metadata z poskytnutej konfigurácie.

Zjednodušený single-member príklad pre izolovaný recovery lab:

```bash
etcdutl snapshot restore /secure-backup/etcd-snapshot.db \
  --name control-plane-1 \
  --initial-cluster control-plane-1=https://10.0.0.11:2380 \
  --initial-advertise-peer-urls https://10.0.0.11:2380 \
  --data-dir /var/lib/etcd-restored
```

Produkčný príkaz musí presne zodpovedať:

- počtu members,
- member names,
- peer URLs,
- data directories,
- TLS a API server topology.

Nikdy nekopíruj príklad bez adaptácie a testu na rovnakú verziu/topológiu.

## 13. Revision bump a informer cache

Po restore sa etcd revision vráti na hodnotu snapshotu. Kubernetes controllers a clients môžu mať cache alebo watch assumptions založené na vyššej revision pred incidentom.

Aktuálne etcd recovery tooling podporuje pri restore mechanizmy ako:

```bash
--bump-revision <delta>
--mark-compacted
```

Ich cieľom je posunúť revision a označiť starú históriu ako compacted, aby watchers vykonali relist namiesto použitia stale cache assumptions.

Použitie musí vychádzať z dokumentácie konkrétnej etcd verzie a testovaného Kubernetes recovery runbooku. Arbitrárny malý revision bump nemusí prekročiť pôvodnú revision.

## 14. Stacked kubeadm restore flow

Typický riadený flow:

1. zastav alebo izoluj API server writes,
2. zachovaj current data directories a logs ako evidence,
3. over snapshot status a recovery metadata,
4. restore-ni snapshot do nového data directory,
5. aktualizuj etcd static Pod manifest `hostPath`/arguments podľa plánu,
6. obnov etcd members sekvenčne podľa topológie,
7. over etcd endpoint a member health,
8. obnov API servers,
9. over API resources, controllers a Nodes,
10. vykonaj application/data consistency kontrolu.

Pri HA topológii musí byť celý restored etcd cluster vytvorený konzistentne. Nemiešaj staré a restored member state.

## 15. API server koordinácia

Počas restore zabráň API serverom zapisovať do starého alebo čiastočne obnoveného etcd clusteru.

Over API server flags/config:

- etcd endpoints,
- `--etcd-cafile`,
- `--etcd-certfile`,
- `--etcd-keyfile`,
- encryption provider configuration,
- storage prefix podľa architektúry.

Po zmene endpointov/certificates musia všetky API server replicas používať rovnaký autoritatívny etcd cluster.

## 16. Encryption at rest

Ak API server šifroval Secrets/resources pred zápisom do etcd, snapshot obsahuje ciphertext.

Na restore potrebuješ:

- rovnakú encryption configuration,
- required key material alebo KMS provider,
- správne poradie providers,
- dostupný KMS endpoint a identity,
- rotation history potrebnú na decrypt starších dát.

Snapshot bez decryption keys môže byť integrity-valid, ale prakticky nepoužiteľný.

## 17. Certificates a identity

Etcd peer a client TLS závisí od:

- CA,
- SANs,
- member names a addresses,
- file permissions,
- system time,
- certificate expiry.

Pri recovery na nové IP/hostnames môže byť potrebné znovu vydať certificates. Nepoužívaj vypnutie TLS ako rýchlu opravu produkčného restore.

## 18. Post-restore validácia

### Etcd

```bash
ETCDCTL_API=3 etcdctl endpoint health --cluster ...
ETCDCTL_API=3 etcdctl endpoint status --cluster --write-out=table ...
ETCDCTL_API=3 etcdctl member list --write-out=table ...
```

Over:

- všetky members healthy,
- jeden leader,
- rovnakú cluster ID perspektívu,
- konzistentné revisions a raft state,
- disk latency/space.

### Kubernetes API

```bash
kubectl get --raw='/readyz?verbose'
kubectl get nodes
kubectl get pods -A
kubectl get events -A --sort-by=.metadata.creationTimestamp
```

### Controllers a workloads

Over:

- controller-manager a scheduler leadership,
- EndpointSlices a Services,
- Deployments/StatefulSets/Jobs,
- PVC/PV/VolumeAttachments,
- admission webhooks,
- Secrets a ServiceAccounts,
- operators/custom resources,
- CNI/CSI/DNS.

## 19. External state reconciliation

Etcd rollback môže obnoviť API object, ktorého external resource už neexistuje, alebo odstrániť object pre external resource, ktorý stále existuje.

Príklady:

- cloud load balancer,
- disk/PV,
- DNS record,
- certificate,
- external secret,
- operator-managed database.

Po restore controllers začnú znovu reconcile-ovať. Pred otvorením production trafficu analyzuj potenciálne destructive side effects.

## 20. Application data consistency

Príklad:

- etcd snapshot obsahuje StatefulSet a PVC z 10:00,
- database backup je z 09:30,
- application deployment z 09:50 očakáva novšiu schema.

Cluster API state môže byť úspešne obnovený, ale application je nekonzistentná.

Recovery plan musí koordinovať:

- deployment revision,
- database schema,
- persistent data,
- secrets/certificates,
- external queues/object storage,
- traffic reopening.

## 21. Restore test

Pravidelný restore test má:

1. vybrať reálny backup artifact,
2. overiť integrity a decryption access,
3. obnoviť izolovaný cluster alebo recovery environment,
4. zmerať RTO,
5. validovať API resources a critical workloads,
6. vykonať application data restore/consistency test,
7. zaznamenať gaps a aktualizovať runbook,
8. bezpečne zlikvidovať citlivý test environment.

Test iba príkazu `snapshot status` nie je disaster-recovery test.

## 22. Monitoring

Sleduj:

- snapshot success/failure,
- snapshot age a revision,
- file size a duration,
- offsite copy completion,
- restore-test age a výsledok,
- etcd leader changes,
- proposal failures,
- fsync/commit latency,
- database quota/size,
- disk capacity a inodes,
- member health a clock skew.

Alert na neúspešný backup je kritickejší než dashboard zobrazujúci iba etcd `up`.

## 23. Corruption

Pri podozrení na corruption:

- zastav automatické destructive pokusy,
- zachovaj logs a data directories,
- porovnaj member hashes podľa podporovaného etcd workflowu,
- identifikuj healthy member/snapshot,
- nevytváraj snapshot z neovereného corrupted source ako jediný backup,
- postupuj podľa etcd data-corruption recovery dokumentácie.

Disk/filesystem/kernel chyby môžu byť root cause; samotný restore na rovnaký chybný disk incident zopakuje.

## 24. Troubleshooting

### `context deadline exceeded` pri snapshot save

Over endpoint health, TLS, leader/network latency, disk write capacity a snapshot size.

### Snapshot status hlási hash mismatch

Artifact je poškodený alebo nekompletný. Nepoužívaj ho bez ďalšieho forensic overenia.

### Restored etcd beží, API server nie

Over endpoints, TLS SANs, client certificates, encryption config, static Pod manifest a network/firewall.

### API funguje, ale controllers sa správajú nekonzistentne

Over restore revision model, informer relist, controller logs, leader election a resource versions.

### Po restore chýbajú novšie resources

Je to očakávaná strata po snapshot čase. Reconcile-ni ich z autoritatívneho Git/IaC source-u až po analýze external state.

### Etcd members sa nevedia spojiť

Over initial cluster mapping, peer URLs, certificates, member names, cluster token a firewall.

## 25. Anti-patterny

### Snapshot iba na rovnakom etcd disku

Host/disk failure odstráni primary aj backup.

### Backup bez integrity a restore testu

Existencia file-u nepreukazuje obnoviteľnosť.

### Restore jedného člena do existujúceho quorum bez plánu

Môže vytvoriť member/cluster identity konflikt.

### Obnova etcd bez encryption keys

Citlivé resources zostanú nečitateľné.

### Predpoklad, že etcd snapshot obsahuje PV dáta

Application state sa neobnoví.

### Restore priamo v produkcii bez izolovaného rehearsal

RTO a side effects sú neznáme.

### Automatický cleanup starých backupov bez immutable retention

Compromise alebo chyba môže odstrániť všetky recovery points.

## 26. Kontrolné otázky

1. Ktoré dáta etcd snapshot obsahuje a ktoré nie?
2. Ako sa počíta etcd quorum?
3. Prečo je online snapshot vhodnejší než live filesystem copy?
4. Načo slúži `etcdutl snapshot status`?
5. Čo musí obsahovať kompletný recovery set?
6. Prečo restore vytvára nový logical etcd cluster?
7. Aký problém po restore rieši revision bump a compaction marker?
8. Ako encryption-at-rest ovplyvňuje obnoviteľnosť snapshotu?
9. Prečo treba po restore analyzovať external controller state?
10. Čo preukazuje plnohodnotný restore test?

## Glossary impact

Relevantné pojmy: etcd snapshot, snapshot revision, etcd quorum, member health, disaster recovery, restored cluster identity, revision bump, compaction marker, recovery set, restore rehearsal, etcd corruption, API-state RPO a cross-system recovery consistency.

## Oficiálna dokumentácia

- [Operating etcd clusters for Kubernetes](https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/)
- [etcd disaster recovery](https://etcd.io/docs/v3.7/op-guide/recovery/)
- [How to save the etcd database](https://etcd.io/docs/v3.7/tasks/operator/how-to-save-database/)
- [Securing a cluster](https://kubernetes.io/docs/tasks/administer-cluster/securing-a-cluster/)
