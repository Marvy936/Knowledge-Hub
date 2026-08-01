# Container storage

Container môže byť stateful, ale jeho proces a jeho dáta nemajú automaticky rovnaký lifecycle. Process sa môže reštartovať, container sa môže odstrániť, image sa môže nahradiť a node môže zaniknúť. Business dáta pritom často musia zostať dostupné, konzistentné a obnoviteľné.

Preto sa pri container storage nezačína otázkou „mám použiť volume alebo bind mount?“. Najprv sa určí, aké dáta aplikácia vytvára, kto je ich autorita, ako dlho majú žiť, či ich zapisuje jeden alebo viac procesov, akú consistency vyžadujú a čo sa má stať pri strate containeru alebo hosta.

Budeme sledovať `payments-api`. Hlavné transakcie zapisuje do PostgreSQL mimo Docker hosta. Lokálne cvičenie však používa JSONL ledger vo volume-e, aby bolo možné ukázať rozdiel medzi container writable layer, named volume, bind mountom a tmpfs.

## 1. Najprv inventár dát

Jedna aplikácia môže používať viac typov state-u:

```text
application binary a libraries
→ patria image-u

runtime cache
→ môže byť ephemeral

PID file alebo socket
→ patrí konkrétnej process generation

payment ledger
→ musí prežiť container replacement

secret
→ musí byť dodaný z chránenej configuration vrstvy

logy
→ majú byť odoslané mimo container lifecycle-u
```

Ak sa všetko uloží do jedného `/var/lib/app`, nie je jasné, čo sa môže bezpečne odstrániť, čo sa má backupovať a čo sa nesmie zdieľať medzi replicas. Storage design preto začína významom dát, nie syntaktickým typom mountu.

## 2. Container writable layer

Bez explicitného mountu zapisuje process do writable layer konkrétneho containeru. Táto vrstva je vhodná pre dočasný state, ktorý možno po odstránení containeru zahodiť.

```bash
docker run --name writable-demo alpine:3.22 \
  sh -c 'echo runtime > /var/lib/runtime.txt && sleep 300'
```

Súbor existuje:

```bash
docker exec writable-demo cat /var/lib/runtime.txt
```

Po odstránení containeru však zmizne spolu s writable layer:

```bash
docker rm -f writable-demo
```

Nový container z rovnakého image-u nemá žiadnu väzbu na starú writable layer. To je správne pre cache alebo scratch data. Je to katastrofa pre jedinú kópiu pending payments.

Writables layers používajú copy-on-write storage driver. Pri databázových súboroch alebo intenzívnom write workload-e môžu mať horšie a menej predvídateľné vlastnosti než storage navrhnuté pre persistentné dáta.

## 3. Named volume oddelí data lifecycle

Named volume je Docker-managed storage object. Container ho mountne na konkrétny path, ale volume môže existovať aj po odstránení containeru.

```bash
docker volume create payments-data

docker run --rm \
  --mount type=volume,source=payments-data,target=/var/lib/atlas-payments \
  alpine:3.22 \
  sh -c 'echo pay-100 > /var/lib/atlas-payments/ledger.txt'
```

Druhý container načíta rovnaké dáta:

```bash
docker run --rm \
  --mount type=volume,source=payments-data,target=/var/lib/atlas-payments \
  alpine:3.22 \
  cat /var/lib/atlas-payments/ledger.txt
```

Volume prežilo oba container lifecycles. Neznamená to však, že prežije stratu Docker hosta. Pri local volume driveri sú dáta viazané na konkrétny host storage. Presun workloadu na iný node potrebuje shared storage, replication, restore alebo aplikáciu, ktorá používa externý data systém.

## 4. Bind mount spája container s host pathom

Bind mount pripojí existujúci host path do container mount namespace-u:

```bash
mkdir -p ./local-data

docker run --rm \
  --mount type=bind,source="$PWD/local-data",target=/var/lib/atlas-payments \
  alpine:3.22 \
  sh -c 'echo pay-200 > /var/lib/atlas-payments/ledger.txt'
```

Dáta sú priamo v `./local-data` na hoste. Bind mount je praktický pri local development, source code mountoch alebo integrácii s host-managed paths. Zároveň vytvára silný coupling na konkrétny host filesystem layout, ownership, permissions, SELinux labels a pri Docker Desktop aj file-sharing vrstvu.

Writable bind mount môže aplikácii umožniť zmeniť host files. Mount `/etc`, `/var/run/docker.sock` alebo celý `/` dramaticky mení security boundary. Preto má byť source path presný a mount podľa možnosti read-only:

```bash
--mount type=bind,source="$PWD/config",target=/etc/atlas,readonly
```

## 5. Tmpfs pre dočasné citlivé alebo rýchle dáta

Tmpfs mount ukladá dáta do memory-backed filesystemu a neukladá ich ako bežné persistentné host files. Je vhodný pre dočasné súbory, ktoré nemajú prežiť container stop, alebo pre runtime state, ktorý nechceme zapisovať do image layer.

```bash
docker run --rm \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=16m \
  IMAGE
```

Tmpfs stále spotrebúva memory a môže byť ovplyvnený host swap alebo platform implementáciou. Size limit je dôležitý, pretože neobmedzený temporary write môže vytvoriť memory pressure. Tmpfs nie je backup ani tajný trezor; process s prístupom k mountu môže dáta čítať.

## 6. Mount zakryje obsah image-u

Ak image obsahuje súbor v path-e a runtime na ten istý path pripojí volume, process vidí mount, nie underlying image directory.

Image môže obsahovať:

```text
/var/lib/atlas-payments/schema.json
```

Po mountnutí prázdneho volume-u na `/var/lib/atlas-payments` sa súbor javí ako chýbajúci. Image je správny a file v layer existuje, ale mount ho zakryl.

```bash
docker inspect CONTAINER \
  --format '{{json .Mounts}}' | jq .
```

Pri chybe „súbor bol v image-i, ale aplikácia ho nevidí“ preto kontroluj final image filesystem aj runtime mounts. Bežným riešením je držať immutable defaults mimo volume pathu a pri inicializácii ich explicitne skopírovať do data directory, ak ešte neexistujú.

## 7. Numeric UID a GID sú súčasť storage contractu

Filesystem rozhoduje podľa numeric IDs a mode bits, prípadne ACL a LSM policy. Meno `app` v jednom image-i nemusí mať rovnaké UID ako `app` v inom image-i.

`payments-api` beží ako `65532:65532`. Named volume vytvorený root containerom však môže byť `root:root` s mode `0700`. Process sa spustí, ale zápis zlyhá.

Controlled initializer:

```bash
docker run --rm \
  --user 0:0 \
  --mount type=volume,source=payments-data,target=/data \
  busybox:1.36.1 \
  sh -ec 'mkdir -p /data && chown 65532:65532 /data && chmod 0750 /data'
```

Runtime aplikácia potom zostáva non-root. Initializer je samostatná privileged operation a potrebuje idempotentný contract. `chown -R` nad veľkým datasetom pri každom štarte môže byť pomalý a meniť ownership súborov, ktoré patria inému writerovi.

Pri user namespace remappingu sa container UID mapuje na host UID range. Bind mount ownership preto môže vyzerať nečakane. Diagnostika musí poznať mapping aj host filesystem.

## 8. Read-only mount a read-only root filesystem

Read-only root filesystem chráni image filesystem pred mutation. Neznamená, že všetky mounts sú read-only. Named volume môže zostať writable.

```bash
docker run --rm \
  --read-only \
  --mount type=volume,source=payments-data,target=/var/lib/atlas-payments \
  --mount type=bind,source="$PWD/config",target=/etc/atlas,readonly \
  IMAGE
```

Výsledný contract je zrozumiteľný: config sa iba číta, business data path sa zapisuje a zvyšok root filesystemu je read-only.

Application startup má tento contract overiť. Ak knižnica neočakávane zapisuje do current directory, problém sa prejaví okamžite namiesto tichého vytvárania driftu v writable layer.

## 9. Jeden writer, viac writers a fencing

Možnosť pripojiť rovnaký volume k dvom containers neznamená, že aplikácia podporuje concurrent writers. Filesystem môže byť technicky shared, no aplikačný formát môže predpokladať jedného ownera.

JSONL ledger bez locking a sequence contractu sa môže pri paralelnom zápise poškodiť. Embedded databáza môže vyžadovať local filesystem semantics a nesmie bežať nad niektorým network filesystemom. Stateful failover potrebuje fencing, aby stará aj nová instance nezapisovali súčasne.

```text
leader C1 zapisuje volume V1
→ network partition
→ platform spustí C2
→ C1 stále žije a zapisuje
→ split-brain a corruption
```

Storage design musí definovať access mode, writer election, lease alebo fencing mechanizmus a recovery pri unknown owner state.

## 10. Block, shared filesystem a object storage

Container môže používať viac storage modelov.

Block storage poskytuje device, nad ktorým sa vytvorí filesystem alebo databázový layout. Typicky sa pripája k jednému node-u alebo vyžaduje špeciálny cluster filesystem pre multi-attach.

Shared network filesystem poskytuje spoločný file namespace viacerým nodes. Prináša network latency, server-side caching a odlišné locking alebo consistency vlastnosti.

Object storage neposkytuje bežný POSIX filesystem. Aplikácia pracuje s objects cez API. Je vhodné pre immutable blobs, exports, backups a veľké súbory, ale nie je drop-in náhrada pre databázový data directory.

Výber sa riadi aplikačným access patternom, consistency a recovery, nie iba tým, čo sa dá mountnúť do containeru.

## 11. Flush a acknowledgement

Aplikácia môže zapísať do userspace bufferu, kernel page cache alebo storage device cache. HTTP `200` má zmysel iba vtedy, ak aplikácia presne vie, akú durability sľubuje.

V ukážkovom ledgeri sa po JSON encode volá `file.Sync()`. To žiada kernel o flush relevantných dát, ale konečný durability outcome stále závisí od filesystemu, volume drivera a storage backendu.

Database alebo distributed storage používa vlastný commit a replication protocol. Kopírovanie súborov running databázy bez coordination môže vytvoriť fyzicky čitateľné, ale transakčne nekonzistentné dáta.

## 12. Backup nie je volume existence

Named volume prežije container recreate, ale nie je backup. Backup musí mať samostatnú kópiu, retention, integrity verification a restore test.

Jednoduchý file-level export volume-u možno urobiť pomocou helper containeru:

```bash
docker run --rm \
  --mount type=volume,source=payments-data,target=/data,readonly \
  --mount type=bind,source="$PWD/backups",target=/backup \
  alpine:3.22 \
  tar -C /data -czf /backup/payments-data.tgz .
```

Tento backup môže byť vhodný pre zastavenú jednoduchú file aplikáciu. Pre aktívnu databázu nemusí byť application-consistent. Potrebný je database-native backup alebo coordinated quiesce.

Restore test musí vytvoriť nový data subject, spustiť aplikáciu a overiť business outcome. Úspešný `tar -x` nie je recovery verdict.

## 13. Snapshot consistency

Storage snapshot môže zachytiť block alebo filesystem stav v jednom okamihu podľa backendu. Ak aplikácia stále zapisuje a drží dáta v memory, snapshot môže byť iba crash-consistent. Po restore sa aplikácia správa, akoby host náhle spadol.

Application-consistent snapshot vyžaduje koordináciu: flush, freeze, transaction boundary alebo database-native mechanismus. Pri viacerých volumes treba zabezpečiť spoločný clean point alebo vedieť reconcile rozdielne snapshot časy.

```text
quiesce writes
→ flush application a filesystem state
→ snapshot všetkých required volumes
→ release writes
→ verify snapshot metadata
→ pravidelný restore drill
```

## 14. Cleanup a nebezpečenstvo orphan volumes

`docker compose down` štandardne odstráni containers a networks, ale named volumes neodstráni bez explicitnej voľby. To chráni dáta pri bežnom teardown-e.

```bash
docker compose down
```

Destructive variant:

```bash
docker compose down --volumes
```

Pred odstránením volume-u over, že nejde o jedinú kópiu dát, rollback candidate alebo incident evidence.

```bash
docker volume inspect payments-data
docker ps -a --filter volume=payments-data
```

Orphan volume môže zaberať disk, ale môže byť aj zámerne ponechaný data subject. Automatický `docker volume prune` bez ownership inventory je rizikový.

## 15. Incident: backup bol úspešný, restore nepoužiteľný

Atlas vytváral nightly tar archive PostgreSQL data directory z running containeru. Backup job končil exit code `0` a archív sa dal rozbaliť. Pri incidente však PostgreSQL po restore odmietol štart alebo spustil recovery s chýbajúcimi WAL segments.

Job overoval iba čitateľnosť files, nie databázový consistency contract. Niektoré stránky a WAL state boli zachytené v rozdielnych okamihoch.

Recovery musela použiť starší database-native backup. Trvalá oprava zaviedla `pg_basebackup`, WAL archiving, retention podľa RPO a pravidelný restore test do izolovaného prostredia. Volume snapshot ostal doplnkovým infrastructure artifactom, nie jediným database backupom.

## 16. Incident: recreate použil nový prázdny volume

Compose project name sa zmenil z `atlas-dev` na `atlas-payments-dev`. Volume nemalo explicitné `name`, takže Compose vytvoril nový project-scoped volume. Container bol healthy, ale payment ledger bol prázdny.

```text
starý project → atlas-dev_payments-data
nový project → atlas-payments-dev_payments-data
```

Dáta neboli vymazané. Aplikácia mountla iný volume subject.

Diagnostika porovnala `docker volume ls`, Compose labels a `.Mounts[].Name`. Oprava nastavila explicitné volume name tam, kde sa data identity mala zachovať naprieč project rename, a migration flow kopíroval dáta s verifikáciou.

## 17. Systematický storage troubleshooting

Pri symptóme „dáta chýbajú“ najprv identifikuj exact container, mount a backend:

```bash
docker inspect CONTAINER | jq '.[0].Mounts'
docker volume inspect VOLUME
docker system df -v
docker logs --timestamps CONTAINER
```

Potom rozlišuj hypotézy: nový volume, mount obscuring, nesprávny path, UID/GID, read-only mount, host filesystem full, inode exhaustion, LSM denial, corruption, split-brain alebo application buffer bez flushu.

Pred recreate, prune alebo permission repair zachovaj inspect, volume metadata, filesystem listing a application logs. Recovery sa overuje pôvodnou business operáciou, nie iba existenciou mountu.

## Čo si z kapitoly odniesť

Container writable layer patrí container instance a je vhodná pre ephemeral state. Named volume oddeľuje dáta od container lifecycle-u, ale local volume nemusí prežiť host failure. Bind mount spája workload s konkrétnym host pathom. Tmpfs poskytuje dočasný memory-backed filesystem.

Persistent storage potrebuje explicitnú identitu, UID/GID contract, access mode, consistency, backup, restore, retention a cleanup policy. Volume existence nie je backup a snapshot success nie je application recovery. Stateful container je bezpečný iba vtedy, keď je data lifecycle navrhnutý nezávisle od replaceable processu.

## Primárne zdroje

- [Docker storage overview](https://docs.docker.com/engine/storage/)
- [Volumes](https://docs.docker.com/engine/storage/volumes/)
- [Bind mounts](https://docs.docker.com/engine/storage/bind-mounts/)
- [Tmpfs mounts](https://docs.docker.com/engine/storage/tmpfs/)
- [Compose volumes](https://docs.docker.com/reference/compose-file/volumes/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Container networking](container-networking.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Container security →](container-security.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
