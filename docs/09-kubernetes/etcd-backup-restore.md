# etcd backup a restore

Etcd snapshot zachytáva Kubernetes API state v konkrétnej etcd revision. Obsahuje objekty ako Deployments, Secrets, ConfigMaps, Nodes, PVCs, RBAC a custom resources, ale neobsahuje samotné application dáta v databázach, obsah cloud diskov, external load balancers ani artifacts v registry. Restore preto nevracia celý production systém do jedného historického okamihu. Obnoví iba Kubernetes control-plane state a musí sa koordinovať s PKI, encryption keys, Nodes, storage a external resources.

V Atlas clustri `atlas-prod-eu1` používame etcd snapshot ako disaster-recovery vstup pre stratu control-plane state-u. Bežný chybný Deployment alebo jeden poškodený Node sa rieši roll-forwardom alebo replacementom, nie obnovou celého etcd. Restore je cluster-wide operácia s veľkým blast radiusom.

## Čo snapshot skutočne obsahuje

API server zapisuje serializované Kubernetes objects do etcd. Snapshot preto môže obsahovať:

```text
namespaces a workload specs
status a conditions v čase snapshotu
Secrets a ConfigMaps v uloženej podobe
RBAC, CRDs a custom resources
Service, EndpointSlice, PVC/PV a Node objects
controller leases a ďalší cluster state
```

Snapshot neobsahuje:

```text
container writable layers a Node filesystemy
obsah externých PV backendov
object storage a managed databases
registry images
cloud load balancer listener state
DNS provider records mimo Kubernetes
external secret target values
application transaction ledger mimo API
```

Obnovený PVC object môže odkazovať na disk, ktorý už neexistuje. Obnovený Service typu LoadBalancer môže odkazovať na status adresu, ktorú cloud provider medzičasom uvoľnil. Preto sa recovery uzatvára až external read-backom a business validáciou.

## Presná identita snapshotu

Súbor `snapshot.db` bez metadata nie je dostatočný recovery artifact. Uchovaj aspoň:

```text
cluster identity a environment
Kubernetes a etcd version
snapshot timestamp a časovú zónu
etcd revision, hash a status
member/endpoint inventory pri capture
PKI a encryption-configuration generation
control-plane a add-on generations
application data recovery point a dependencies
storage location, encryption a retention
restore test result
```

Snapshot z testovacieho clusteru môže byť kryptograficky platný, ale nesprávny pre production. Filename `latest.db` túto chybu nezabráni.

## Vytvorenie snapshotu

Presný `etcdctl` invocation závisí od topology, certifikátov a verzie. V kubeadm-style local etcd modeli môže vyzerať napríklad:

```bash
export ETCDCTL_API=3

etcdctl \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt \
  --key=/etc/kubernetes/pki/etcd/healthcheck-client.key \
  snapshot save /secure-backups/atlas-prod-eu1-20260801T040000Z.db
```

Tento príklad sa nesmie kopírovať bez kontroly cieľového clusteru. External etcd môže mať iné endpoints a client certificates. Managed cluster nemusí poskytovať priamy etcd access a recovery contract vlastní provider.

Po capture over snapshot:

```bash
etcdutl snapshot status \
  /secure-backups/atlas-prod-eu1-20260801T040000Z.db \
  --write-out=table
```

Nástroj a syntax sa viažu na etcd verziu. Status a hash preukazujú čitateľný snapshot artifact, nie úspešný cluster restore.

## Capture consistency

Etcd snapshot je konzistentný pre etcd keyspace v danej revision. Kubernetes controllers a external systémy však pracujú eventual-consistently. Snapshot môže zachytiť Deployment generation po create requeste, ale pred vytvorením všetkých child objektov, alebo cloud Service object pred dokončením external load balancera.

Po restore controllers znovu reconcile-nu desired state. To môže byť správne, ale môže tiež zopakovať external side effect, ak custom controller nemá idempotentnú external identity.

Application data potrebuje samostatný recovery point. Etcd revision a database backup timestamp sa majú koordinovať podľa business recovery modelu, ale netvoria automaticky jednu distribuovanú transakciu.

## Encryption at rest

Ak API server používa encryption configuration pre Secrets alebo iné resources, etcd snapshot obsahuje ciphertext viazaný na príslušnú key generation. Restore bez správneho encryption configu a kľúčov môže spôsobiť, že API server nevie objekty dešifrovať.

Recovery set preto zahŕňa:

```text
snapshot
+ API server encryption configuration
+ všetky keys potrebné na čítanie uložených generations
+ bezpečný plán prepisu a retirement starých keys
```

Samotný snapshot je citlivý artifact. Aj pri encryption at rest obsahuje množstvo cluster metadata a môže obsahovať plaintext pre resources, ktoré neboli šifrované. Musí byť šifrovaný pri transporte a uložení, accessovaný úzkou identity a auditovaný.

## PKI a service-account keys

Obnovený cluster potrebuje kompatibilnú CA a component credentials. Service-account signing keys sú osobitne dôležité: zmena môže zneplatniť existujúce tokens, zatiaľ čo zachovanie kompromitovaného keyu predlžuje riziko.

Recovery rozhoduje, ktoré identity sa obnovujú a ktoré sa rotujú. Po security incidente môže byť nesprávne slepo obnoviť staré credentials zo snapshotu alebo backup setu.

## Restore vytvára nový etcd member state

Restore sa nevykonáva prepísaním živého data directory náhodným snapshot súborom. Nástroj vytvorí nový member data directory a metadata pre novú alebo obnovenú cluster topology.

Príklad pre jeden member v izolovanom recovery prostredí:

```bash
etcdutl snapshot restore \
  /secure-backups/atlas-prod-eu1-20260801T040000Z.db \
  --name=control-plane-1 \
  --data-dir=/var/lib/etcd-restored \
  --initial-cluster=control-plane-1=https://10.0.0.11:2380 \
  --initial-advertise-peer-urls=https://10.0.0.11:2380 \
  --initial-cluster-token=atlas-prod-eu1-restore-20260801
```

Skutočná HA obnova musí definovať všetkých nových members a správne peer URLs. Príkaz sa najprv pripravuje a testuje v recovery runbooku; improvizácia v produkcii je vysoké riziko.

Restore operácia upraví cluster/member metadata tak, aby obnovený cluster nevstúpil do pôvodného membershipu ako stale member. Staré a nové data directories sa nesmú zmiešať.

## Fencing pôvodného etcd clusteru

Pred spustením obnoveného control plane-u musí byť jasné, že starý etcd cluster a API servers už nebudú prijímať writes. Dve oddelené control-plane generations nad rovnakou infraštruktúrou môžu vytvárať konfliktné desired states a external side effects.

```text
contain traffic a administrative writes
→ zastav alebo izoluj staré API/etcd members
→ zachovaj ich disks a logs ako evidence
→ obnov nový etcd cluster z jedného snapshotu
→ spusti API servers proti novej topology
→ až potom obnov controllers a Nodes
```

Network partition nie je dôkaz, že starý cluster je mŕtvy. Potrebný je infrastructure fencing, power state alebo iný autoritatívny control.

## Obnova static Pod control plane-u

V kubeadm-style clustri môže etcd bežať ako static Pod. Restore workflow typicky upraví etcd manifest alebo data directory na každom control-plane Node-e podľa runbooku a následne reštartuje static Pods cez kubelet observation.

Nesprávna úprava všetkých control-plane Nodes naraz môže odstrániť posledný funkčný API endpoint. Preto sa recovery vykonáva v kontrolovanom outage stave s offline kópiou pôvodných manifests, data directories a PKI.

Presné paths a flags sú distribučné a version-specific. Dokumentuj ich z actual cluster manifests, nie z generického blogu.

## Prvé overenie po restore

Po spustení obnoveného API neaplikuj okamžite všetky manifests nanovo. Najprv čítaj, čo sa obnovilo:

```bash
kubectl get --raw='/readyz?verbose'
kubectl get namespaces
kubectl get nodes -o wide
kubectl get deployments,statefulsets,daemonsets -A
kubectl get pvc,pv -A
kubectl get crd
```

Over, že API server dokáže dešifrovať Secrets bez ich vypisovania:

```bash
kubectl get secret -n production payments-db-se08 \
  -o jsonpath='{.metadata.uid}{"\n"}'
```

Úspešné metadata read ešte nemusí preukázať dešifrovanie konkrétneho data field-u; bezpečný test vykonáva kontrolovaný consumer alebo hash/epoch workflow bez zobrazenia secretu.

## Controllers po restore

Po obnove sa controllers pokúsia priblížiť effective state starým API objektom. Nodes alebo Pods mohli počas outage pokračovať. Ich runtime state nemusí zodpovedať obnovenému snapshotu.

Príklady:

```text
snapshot obsahuje starý Deployment generation
→ na Nodes bežia novšie Pods vytvorené po snapshote
→ API ich môže považovať za neznáme alebo orphaned

snapshot obsahuje Job ako Active
→ external export už po snapshote skončil
→ controller môže vytvoriť nový attempt

snapshot obsahuje Service LoadBalancer status
→ cloud resource bol medzitým zmenený alebo odstránený
```

Pred plným controller reconciliation je potrebné rozhodnúť, či obnovujeme cluster state „do minulosti“, alebo rekonštruujeme aktuálny desired state z Git a external inventories.

## Nodes a kubelety

Kubelet používa Pod state z API, ale na Node-e existujú lokálne sandboxes a containers. Po dlhom control-plane outage môžu byť runtime processes novšie než snapshot.

Pri kritickom DR je často bezpečnejšie worker Nodes cordonovať alebo nahradiť, než slepo pripojiť všetky staré Nodes k obnovenému control plane-u. Stateful workloads potrebujú fencing a data identity control.

Node UID v snapshot-e môže patriť starej machine lifetime. Nový Node s rovnakým menom nemá automaticky preberať starý objekt bez bootstrap/replacement workflowu.

## Persistent storage a external resources

Pre každý PVC/PV vytvor recovery inventory:

```text
PVC namespace/name/UID
PV UID a CSI volumeHandle
backend disk/snapshot identity
zone/topology
data generation a owner
attach/fencing state
```

Ak snapshot obsahuje PV, ale backend disk bol po snapshot-e zmazaný, controller object sám dáta neobnoví. Ak backend disk obsahuje novšie dáta než etcd snapshot, application a controller metadata sa môžu rozísť.

LoadBalancers, DNS records a cloud identities potrebujú provider read-back a prípadnú import/reconciliation logiku. Blind re-create môže vytvoriť duplicate resources.

## Application recovery

Po infraštruktúrnej obnove sa overuje konkrétny business chain:

```text
Deployment/StatefulSet desired state
→ Pods s exact image/config/secret generation
→ Service a edge routing
→ database/storage recovery point
→ payment request
→ exactly-once commit a downstream reconciliation
```

Kubernetes objects Ready nie sú konečný DR verdict. RPO a RTO sa merajú na business dátach a službe.

## Pravidelné restore testy

Snapshot pipeline bez restore testu je iba nádej. Test má v izolovanom prostredí:

```text
stiahnuť exact snapshot a recovery set
→ overiť hash a decrypt access
→ vytvoriť novú etcd topology
→ spustiť kompatibilný API server
→ čítať reprezentatívne encrypted resources a CRDs
→ spustiť controllers v controlled režime
→ overiť vybrané workloads a data restore
→ zmerať čas a zaznamenať gaps
→ bezpečne zničiť test environment a credentials
```

Test nesmie pripojiť obnovený cluster k production cloud resources alebo DNS bez isolation controls.

## Incident: snapshot bol platný, ale patril staging clusteru

Backup job ukladal súbory ako `latest.db` do spoločného bucketu. Production recovery stiahla najnovší objekt, ktorý vytvoril staging cluster o desať minút neskôr. `etcdutl snapshot status` prešiel a restore sa technicky spustil, no namespaces a UIDs boli nesprávne.

Containment zastavilo controllers pred external mutations. Recovery použila artifact s explicitným cluster ID, revision a signed manifestom. Skorší control zakázal neidentifikované `latest` objekty a oddelil trust/retention per cluster.

## Incident: API po restore nevedelo čítať Secrets

Snapshot vznikol počas encryption key rotation a obsahoval objekty šifrované starou aj novou key generation. Recovery set obsahoval iba nový key. API server štartoval, ale reads vybraných Secrets vracali decryption errors.

Oprava obnovila všetky read keys v správnom poradí, potom vykonala kontrolovaný rewrite objektov na novú key generation a starý key zrušila až po verifikácii. Skorší control spojil snapshot s encryption-key manifestom a restore testom.

## Incident: starý etcd member sa pripojil k obnovenej topology

Po restore jedného membera operátor spustil ďalší control-plane Node s pôvodným data directory a starým manifestom. Vznikol membership konflikt a nestabilný control plane. Časť API serverov smerovala na starú topology.

Recovery úplne zastavila všetky members, zachovala disks, vytvorila jednotnú novú topology z jedného snapshotu a aktualizovala všetky manifests. Skorší control je fencing a zákaz mixovania restored a original member directories.

## Incident: Kubernetes state sa obnovil, cloud disks nie

Etcd snapshot obsahoval StatefulSet a PVC/PV objekty. Útočník však po snapshote zmazal cloud volumes aj snapshots v rovnakom account-e. Restore vytvoril zelený API a controllers, ale Pods zostali na `FailedAttachVolume`.

Etcd backup nebol data backup. Recovery použila izolovanú cross-account data kópiu a aktualizovala PV/backend mapping podľa riadeného restore-u. Skorší control oddelil control-plane backup od immutable/off-account application data recovery.

## Incident: obnovený Job zopakoval external settlement

Snapshot zachytil Job ako Active. Po capture pôvodný Pod settlement úspešne odoslal, ale control plane zanikol pred status updateom. Po restore Job controller vytvoril nový Pod a provider dostal rovnaký batch znova.

Application idempotency key zabránil druhému commitu, ale audit ukázal, že Kubernetes Job status nemôže byť exactly-once authority. Recovery runbook začal pred aktiváciou controllers reconcile-nuť kritické external operations podľa business IDs.

## Model, ktorý si treba odniesť

Etcd snapshot obnovuje Kubernetes API keyspace, nie celý produkčný systém. Bezpečný restore potrebuje exact snapshot identity, compatible etcd/Kubernetes tools, PKI a encryption keys, fencing pôvodného clusteru, novú čistú member topology a koordináciu s Nodes, storage, cloud resources a application data. Recovery je complete až po business validation a forbidden-side-effect kontrole.

## Referencie

- [Operating etcd clusters for Kubernetes](https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/)
- [Disaster recovery for etcd clusters](https://etcd.io/docs/)
- [Encrypting Confidential Data at Rest](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Cluster installation a lifecycle](cluster-installation-lifecycle.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Upgrades →](upgrades.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
