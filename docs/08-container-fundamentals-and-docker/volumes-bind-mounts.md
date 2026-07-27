# Volumes a bind mounts

Docker mount nie je iba cesta pridaná do containeru. Je to runtime prepojenie medzi **source data identity** a pathom v mount namespace-e procesu. Nesprávny source, daemon context, project name, ownership alebo cleanup command môže pripojiť prázdne dáta, staging dáta alebo zmazať jedinú production kópiu.

Dominantný lifecycle:

```text
data intent a persistence classification
→ mount source identity a lifecycle owner
→ daemon/project/host resolution
→ source preflight
→ attach a mount-namespace publication
→ UID/GID, LSM, propagation a read/write policy
→ initialization alebo schema transition
→ runtime I/O a durability verification
→ backup/restore evidence
→ detach, replacement, retention alebo cleanup
```

`volume`, `bind` a `tmpfs` sú rozdielne source a lifecycle modely. Ich syntax sama o sebe nedokazuje správne dáta, bezpečný access ani obnoviteľnosť.

## 1. Atlas scenár

Atlas Payments používa:

```text
application image: payments-api@sha256:I44
Docker project: atlas-payments-prod
container service: api
persistent data ID: PAYMENTS-LEDGER-PROD
volume object: atlas-payments-prod_ledger-data
volume generation: G18
mount target: /var/lib/atlas/ledger
writer epoch: W203
runtime UID:GID: 10001:10001
backup lineage: B77
```

Ďalšie mounts:

```text
read-only config bind:
/srv/atlas-payments/config/app.yaml
→ /etc/atlas/app.yaml

runtime tmpfs:
/run/atlas
```

Úspech neznamená iba to, že `Mounts` existujú v `docker inspect`. Potrebné je potvrdiť:

- správny logical data ID a generation;
- správny daemon, host a Compose project;
- správny volume alebo host source;
- správny target path bez neplánovaného obscuring-u;
- process má iba potrebný read/write access;
- application skutočne zapisuje do očakávaného data setu;
- backup a restore patria rovnakej data lineage;
- replacement containeru zachová dáta;
- cleanup neodstráni authoritative state.

## 2. Persistence classification

Každý writable path klasifikuj pred deploymentom:

```text
ephemeral runtime state
persistent business state
re-injectable configuration alebo secret
incident/audit evidence
host integration capability
```

Príklady:

| Path | Trieda | Typický source |
|---|---|---|
| `/tmp` | ephemeral | writable layer alebo bounded tmpfs |
| `/var/lib/atlas/ledger` | persistent business state | named/external volume |
| `/etc/atlas/app.yaml` | re-injectable config | read-only bind/config mechanism |
| `/run/secrets/db` | secret | tmpfs alebo secret delivery |
| `/var/run/docker.sock` | host-control capability | spravidla nesprístupňovať |

Writable container layer je naviazaná na konkrétnu container instance. Preto nemá byť jediným authoritative storage pre business state alebo incident evidence, ktoré musia prežiť replacement.

## 3. Mount subject

Pred create operáciou vytvor mount subject:

```text
mount type
source logical identity
source physical identity alebo host path
Docker daemon/context
host/node identity
Compose project/resource name
destination path
read/write mode
UID/GID a user-namespace mapping
LSM label/profile
propagation mode
expected data generation/schema
backup/retention owner
```

Rovnaký text `ledger-data:/var/lib/atlas/ledger` môže ukazovať na iný object, ak sa zmení project name, daemon endpoint alebo external volume mapping.

## 4. Named volume lifecycle

Named volume má explicitnú Docker object identity:

```bash
docker volume create atlas-ledger-data

docker run \
  --mount type=volume,src=atlas-ledger-data,dst=/var/lib/atlas/ledger \
  payments-api@sha256:I44
```

Volume:

- má lifecycle oddelený od containeru;
- môže prežiť `docker rm`;
- môže používať local alebo external driver;
- nie je automaticky replicated, encrypted alebo backed up;
- nepodporuje automaticky safe multi-writer access.

Pre intentional persistence preferuj named alebo explicitne external volume. Anonymous volume má durable bytes, ale slabšiu owner a cleanup identitu.

## 5. Compose project a volume identity

Compose typicky vytvorí meno z projektu a logical volume key:

```text
<project>_<volume-key>
```

```yaml
services:
  api:
    image: payments-api@sha256:I44
    volumes:
      - ledger-data:/var/lib/atlas/ledger

volumes:
  ledger-data:
```

Zmena project name môže vytvoriť nový prázdny volume bez zmeny YAML:

```text
atlas-payments-prod_ledger-data
atlas-payments_ledger-data
```

Pre production persistent state je často vhodné explicitné meno alebo external ownership:

```yaml
volumes:
  ledger-data:
    external: true
    name: atlas-payments-prod-ledger
```

`external: true` znamená, že Compose object nevytvára ani plne nevlastní. Deployment musí vykonať data-ID, schema, permission a backup preflight.

## 6. Bind mount lifecycle

Bind mount publikuje existujúci filesystem object z Docker daemon hosta:

```bash
docker run \
  --mount type=bind,src=/srv/atlas/config/app.yaml,dst=/etc/atlas/app.yaml,readonly \
  payments-api@sha256:I44
```

Source sa vyhodnocuje na hoste, kde beží daemon, nie nevyhnutne na stroji s CLI. Pri remote context-e alebo Docker Desktop-e preto existujú tri odlišné path subjects:

```text
client path
Docker daemon/VM path
container destination path
```

Bind mount je vhodný, keď je host path zámerná časť contractu. Znižuje však portability a prenáša host ownership, ACL, labels, case sensitivity, file-sharing a backup semantics do workloadu.

## 7. `--mount` a `-v`

Explicitná forma:

```bash
docker run --mount type=bind,src=/srv/atlas/config,dst=/etc/atlas,readonly image
```

Krátka forma:

```bash
docker run -v /srv/atlas/config:/etc/atlas:ro image
```

Pre automation preferuj `--mount`, pretože type, source, destination a policy sú čitateľnejšie. Pri chýbajúcom bind source môže krátka syntax podľa workflowu vytvoriť directory a maskovať typo; explicitný preflight má zlyhať skôr.

## 8. Mount obscuring

Mount na existujúci image path prekryje lower image content:

```text
image obsahuje /etc/atlas/default.yaml
→ bind/volume sa mountne na /etc/atlas
→ process vidí iba mounted filesystem
→ image file stále existuje v image layers, ale nie v runtime view
```

To môže spôsobiť:

- „zmiznutú“ default configuration;
- prázdny web root;
- missing migrations;
- použitie starého contentu z volume-u;
- rozdiel medzi image smoke testom a runtime behaviorom.

Inspectuj merged mount view a source content. Nekopíruj image defaults do volume implicitne ako neversionovaný migration mechanizmus.

## 9. Initialization a schema transition

Prázdny volume potrebuje explicitný initialization contract:

```text
verify data ID/generation
→ acquire single-writer authority
→ initialize alebo migrate
→ commit schema/epoch ledger
→ verify invariant
→ start application writer
```

Initialization nesmie závisieť iba od `directory is empty`. Prázdny directory môže znamenať wrong volume, failed mount alebo nesprávny project.

Migration potrebuje:

- stable migration IDs;
- concurrency control;
- idempotent alebo resumable semantics;
- old/new image compatibility;
- failure evidence;
- rollback alebo roll-forward postup.

## 10. UID, GID a effective access

Kernel rozhoduje podľa numeric credentials a filesystem metadata:

```text
container process UID/GID
+ user namespace mapping
+ source inode owner/mode/ACL
+ read-only mount flag
+ SELinux/AppArmor policy
→ allow alebo deny
```

Image môže deklarovať `USER 10001`, ale volume môže vlastniť UID `999` alebo root. `chmod 777` maskuje identity problém a rozširuje write authority.

Správna oprava začína identifikáciou:

- effective runtime UID/GID;
- host a mapped IDs;
- exact denied inode a operation;
- ACL/mode;
- LSM denial;
- read-only a propagation flags.

## 11. SELinux, AppArmor a labels

Unix permissions nie sú jediný access verdict. Na SELinux hoste bind source potrebuje správny label a sharing contract. Relabel option nesmie svojvoľne meniť shared host content.

Pri diagnostike odlišuj:

```text
path je visible v mount namespace-e?
Unix credentials povoľujú operation?
LSM policy povoľuje operation?
filesystem alebo mount je read-only?
```

## 12. Read-only nie je harmless

Read-only mount zabráni bežnému zápisu do source, ale process môže stále:

- čítať a exfiltrovať secrets;
- používať mounted Unix socket;
- volať API s credentials v súbore;
- analyzovať host configuration;
- zneužiť device alebo control interface.

Security posudzuj podľa authority source-u. Read-only Docker socket stále poskytuje API operations, ktoré socket server dovolí; filesystem flag nie je application-level authorization proxy.

## 13. tmpfs

Tmpfs je memory-backed ephemeral filesystem:

```bash
docker run \
  --mount type=tmpfs,dst=/run/atlas,tmpfs-size=64m \
  payments-api@sha256:I44
```

Používa sa pre bounded runtime scratch alebo krátkodobý plaintext podľa threat modelu. Potrebuje:

- size limit;
- memory-accounting pochopenie;
- ownership/mode;
- cleanup contract;
- posúdenie swapu, dumpov a host compromise.

Tmpfs nie je persistentný a nie je automaticky „secret-safe“.

## 14. Mount propagation a host coupling

Propagation určuje, či nested mount events prechádzajú boundary. Režimy ako `rshared` alebo `rslave` patria k úzkym storage/tooling use cases.

Široká propagation môže sprístupniť nové host mounts workloadu alebo umožniť workloadu ovplyvniť host mount topology. Default nemeň bez explicitného event-flow modelu.

## 15. Shared volume a writer authority

Docker môže pripojiť volume k viacerým containers. To nedokazuje, že application alebo filesystem podporuje concurrent writers.

Potrebný model:

```text
persistent data ID
→ active writer lease/epoch
→ storage attach a fencing
→ application lock/cluster semantics
→ write audit
```

Bez fencing-u môže po network partitione starý aj nový container zapisovať do rovnakého data setu. Shared filesystem nezmení single-node databázu na cluster.

## 16. Backup a restore

Volume existence nie je backup. Backup subject obsahuje:

```text
data ID a generation
writer/migration epoch
backup type a consistency model
source volume/backend identity
application quiesce/checkpoint evidence
encryption a access
retention/off-host location
restore target a software version
integrity a business-verification verdict
RPO/RTO
```

Hot copy live database directory nemusí byť application-consistent. Snapshot je recovery point iba po úspešnom clean restore teste.

## 17. Cleanup a destructive scope

Príkazy:

```bash
docker volume rm atlas-ledger-data
docker volume prune
docker compose down -v
```

môžu odstrániť durable state. Pred operáciou vytvor retention inventory:

- Docker daemon/context;
- project a environment;
- volume ID/name/driver;
- attached containers;
- logical data ID;
- last backup/restore verdict;
- rollback/support dependency;
- lifecycle owner a approval.

„Unused by running container“ neznamená „safe to delete“.

## 18. Worked failure: zmena project name vytvorila prázdnu databázu

Pipeline predtým používala project `atlas-payments-prod`. Nová automation odviedla project name z directory `deploy`, takže Compose vytvoril `deploy_ledger-data`.

```text
YAML volume key je rovnaký
→ physical volume name sa zmení s projectom
→ nový prázdny volume sa mountne na database path
→ mount prekryje image directory
→ database inicializuje nový prázdny cluster
→ application vyzerá healthy, ale business dáta chýbajú
```

Root cause nie je „Docker zmazal volume“. Starý volume stále existuje, ale nový workload dostal inú data identity.

Recovery:

1. zastav writes a odstráň novú instance z trafficu;
2. identifikuj oba physical volumes a ich data IDs;
3. potvrď, že starý volume je konzistentný a nebol concurrent writer;
4. oprav explicitný project/external volume contract;
5. pripoj správny volume v read-only alebo recovery režime podľa potreby;
6. verify schema, writer epoch a business records;
7. až potom obnov traffic;
8. nový prázdny volume odstráň iba po retention rozhodnutí.

## 19. Worked failure: read-only socket poskytol host-control path

Monitoring container dostal:

```text
/var/run/docker.sock → /var/run/docker.sock:ro
```

Tím predpokladal, že read-only mount povoľuje iba inspection. Unix socket však nie je obyčajný file content. Process mohol odosielať API requests daemonu a vytvoriť privileged container s host-root mountom.

```text
filesystem write flag je read-only
→ connect/write semantics socketu zostávajú použiteľné
→ daemon vykoná host-privileged API operation
```

Oprava vyžaduje odstránenie raw socketu, úzko autorizovaný proxy/exporter alebo iný telemetry path a audit všetkých operations vykonaných cez socket.

## 20. Worked failure: `down -v` zmazal authoritative state

CI cleanup použil rovnaký Compose project name ako persistent integration environment a vykonal:

```bash
docker compose down -v
```

Compose odstránil project-owned volume. Backup bol crash-consistent a nikdy neprešiel restore testom.

Failure chain:

```text
project identity collision
→ cleanup scope zahŕňa shared volume
→ `-v` autorizuje deletion
→ jediný data set zmizne
→ neoverený backup komplikuje recovery
```

Controls:

- collision-safe project names;
- external persistent volumes;
- destructive command policy;
- data-ID labels a preflight;
- tested restore evidence;
- oddelenie ephemeral test state-u od long-lived environmentu.

## 21. Causal walkthrough: application po recreate vidí prázdne dáta

### Symptóm

Po `docker compose up -d --force-recreate` je API healthy, ale ledger je prázdny.

### Zafixuj subject

Zaznamenaj:

```text
Docker context/daemon/host
Compose project a resolved model
container ID a image digest
mount type/source/destination
physical volume ID/name/driver
persistent data ID/generation
UID/GID/LSM
schema a writer epoch
backup lineage
```

### Competing hypotheses

1. nový project name vytvoril nový volume;
2. anonymous volume nahradil named volume;
3. external volume name smeruje na staging;
4. bind source sa vyhodnotil na remote daemone a je prázdny;
5. mount prekryl image alebo expected subdirectory;
6. application píše do iného pathu;
7. permission failure aktivoval fallback local storage;
8. initialization job prebehol nad wrong data ID;
9. starý volume bol odstránený cleanupom;
10. restore/migration vytvorili novú generation.

### Discriminating observation points

- `docker context show`, daemon identity;
- `docker compose config` a project name;
- `docker inspect` container `Mounts`;
- `docker volume inspect` source, labels a driver;
- filesystem UUID/data-ID marker/schema ledger;
- mount table z process namespace-u;
- effective UID/GID a LSM audit;
- application open files a configured data path;
- Engine events a volume create/remove timeline;
- backup/restore audit.

### Containment

Zastav writes a traffic. Nevytváraj ďalší volume ani nespúšťaj automatickú initialization. Zachovaj oba old/new data subjects a logs.

### Recovery

- wrong project/name → oprav explicitné mapping a reattach správny source;
- remote bind path → presuň config/data do supported source alebo oprav daemon-host path;
- wrong environment volume → vykonaj environment/data-ID preflight a pripoj correct data set;
- permission/LSM → oprav konkrétny identity/policy contract;
- cleanup deletion → obnov z posledného clean-restore-capable backupu;
- split writer → fence-ni stale writer, reconcile records a zvýš writer epoch.

### Over pôvodný outcome

Potvrď správny data ID/generation, schema, writer epoch, business record count a write/read transaction. Následný container replacement musí pripojiť rovnaký data subject bez reinitialization.

### Posuň control skôr

Pridaj explicitný project name, external/named volume contract, data-ID preflight, no-fallback storage policy, destructive cleanup guard a pravidelný clean restore test.

## 22. Referenčný mount katalóg

| Typ | Source ownership | Persistence | Hlavná failure boundary |
|---|---|---|---|
| Writable layer | container instance | typicky ephemeral | strata pri replacement-e |
| Named volume | Docker/driver object | oddelená od containeru | wrong project/source, orphan cleanup |
| External volume | iný lifecycle owner | podľa backendu | wrong environment/data ID |
| Bind mount | daemon host path | host lifecycle | path/context, permissions, host exposure |
| tmpfs | runtime memory filesystem | ephemeral | memory pressure, plaintext exposure |
| Socket/device bind | host capability endpoint | podľa hosta | authority escalation |

Katalóg sumarizuje source model. Bez data identity, writer a recovery contractu však neurčuje correctness.

## 23. Praktické controls

- klasifikuj každý writable path;
- používaj explicitný daemon/context a Compose project;
- preferuj named/external volume pre intentional state;
- labeluj volume logical data ID, environment a ownerom;
- vykonaj data-ID/schema/writer preflight pred mutation;
- používaj narrow read-only bindy, ale posudzuj authority source-u;
- nepoužívaj anonymous volumes pre kritické dáta;
- nepoužívaj `chmod 777` ako diagnózu;
- testuj replacement, backup aj clean restore;
- chráň `down -v`, prune a volume remove policy;
- odstráň raw runtime socket mounts;
- audituj project/volume collisions v CI.

## 24. Kontrolné otázky

1. Prečo mount source identity zahŕňa aj daemon a Compose project?
2. Ako sa líši named volume, external volume a bind mount lifecycle?
3. Čo spôsobuje mount obscuring?
4. Prečo prázdny directory nie je dostatočný initialization signal?
5. Ako vzniká permission verdict pri user namespaces a LSM?
6. Prečo read-only socket mount nemusí byť bezpečný?
7. Čo je writer epoch a prečo shared volume potrebuje fencing?
8. Prečo volume existence nie je backup evidence?
9. Ako môže zmena project name vytvoriť zdanlivo stratené dáta?
10. Aké dôkazy musíš zhromaždiť pred `down -v` alebo prune?

## Glossary impact

Relevantné pojmy: Docker mount subject, mount source identity, Compose volume identity, persistent data preflight, mount obscuring, bind-source resolution boundary, effective mount access verdict, volume initialization subject, destructive volume cleanup subject, socket capability mount a replacement persistence proof.

## Oficiálna dokumentácia

- [Docker storage](https://docs.docker.com/engine/storage/)
- [Volumes](https://docs.docker.com/engine/storage/volumes/)
- [Bind mounts](https://docs.docker.com/engine/storage/bind-mounts/)
- [Compose volumes](https://docs.docker.com/reference/compose-file/volumes/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Multi-stage builds](multi-stage-builds.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Docker networks a port publishing →](docker-networks-port-publishing.md)
<!-- KNOWLEDGE-NAVIGATION:END -->