# Fluent Bit

Fluent Bit je edge telemetry agent a processor. Číta lokálne sources, vytvára records, parsuje a obohacuje ich, priraďuje tags, routuje ich do outputs a riadi buffering, retries a backend acknowledgements. Je ľahký, ale nie je durable message broker ani exactly-once transport.

Log delivery závisí od source semantics, file identity a offsetu, parser/filter orderu, tag routing, chunk storage, output response contractu, checkpointu a crash/restart modelu. Process `Running` preto nie je dôkazom, že log vznikol v cieľovom backend-e presne raz.

## 1. Dominantný model

```text
source occurrence a file/socket identity
→ input read a offset state
→ parser/multiline/timestamp generation
→ tag a filter generation
→ redaction, enrichment a routing
→ chunk creation
→ memory alebo filesystem buffering
→ scheduler, retry a backpressure
→ output request
→ backend per-batch/per-item acknowledgement alebo unknown outcome
→ source checkpoint a chunk release
→ backend query a completeness validation
```

Každá boundary môže vytvoriť loss, duplicate, delay, schema drift alebo privacy incident.

## 2. Exact Fluent Bit subject

Pre Atlas Payments používame `FB-PAY-45`:

```text
business capability: final payment settlement
cluster/node/container source
DaemonSet a image/config generation
input plugin a exact path/socket
file path + inode + rotation generation
Tail DB path a schema/state generation
multiline/parser generation
tag a routing generation
filter order a metadata/redaction generation
chunk/storage path a limits
output plugin, tenant/index/stream target
backend credential/TLS generation
retry/backoff generation
source offset/checkpoint
backend acknowledgement a query read-back
```

„Fluent Bit Pod“ nie je dostatočná identity. Jeden Node môže mať inú loaded configuration, tail DB, backlog alebo source inode než zvyšok fleet-u.

## 3. Oddelené stavy

```text
source line existuje
≠ input ju prečítal
≠ parser vytvoril správny record
≠ record matchol output
≠ output request uspel
≠ backend prijal každý item
≠ query ho nájde
```

A:

```text
input offset sa posunul
≠ backend outcome je známy
≠ record možno bezpečne zahodiť
```

Pri timeout-e po backend write môže byť outcome unknown. Retry môže vytvoriť duplicate; advance checkpointu môže vytvoriť loss.

## 4. Configuration generation

Fluent Bit podporuje YAML a classic configuration. Aktuálna dokumentácia uvádza YAML ako štandardný format od verzie `3.2`; classic mode je plánovaný na deprecation na konci roka 2026.

Nový projekt má preferovať YAML, ale acceptance nezávisí od file extension. Potrebuje:

```text
source config
→ version-specific parse
→ loaded plugin graph
→ representative fixture records
→ exact routes a outputs
→ runtime counters
→ backend read-back
```

Syntakticky validná konfigurácia môže byť semanticky nefunkčná, keď tag nematchne output alebo filter zahodí records.

## 5. Inputs a source semantics

Input plugin definuje, ako sa source číta, pauzuje a obnovuje.

Príklady:

- Tail a systemd/journald;
- forward, HTTP, TCP alebo syslog;
- OpenTelemetry a metrics inputs;
- platform-specific sources.

Memory pressure sa správa odlišne podľa inputu. Tail môže prestať čítať a pokračovať zo súboru; UDP alebo iný network source môže data nenávratne stratiť.

## 6. Tail input, file identity a position DB

Tail input sleduje file path, ale recovery potrebuje aj inode/file identity a offset.

```text
path discovery
→ open file/inode
→ read bytes/lines
→ parser
→ checkpoint v position DB
→ rotation/reopen
```

Persistentná position DB chráni pred nejasným replay behaviorom. Ak je na container writable layeri alebo ephemeral Pod state-e, restart môže spôsobiť:

- reread od začiatku;
- preskočenie existujúceho obsahu podľa `read_from_head` semantics;
- duplicates;
- loss starého rotated file-u;
- konflikt dvoch agents nad jednou DB.

Nemaž Tail DB ako prvý troubleshooting krok.

## 7. Rotation a multiline

Rotation mení path, inode a otvorené file descriptors. Agent musí zvládnuť rename, truncation, delayed writes do starého file-u, nový inode a delete po rotate windowe.

Príliš krátky `rotate_wait` môže stratiť late lines. Príliš dlhý drží state a descriptors.

Multiline parser vytvára jeden logical event z viacerých fyzických lines:

```text
first-line rule
→ continuation states
→ flush timeout
→ bounded buffer
→ one logical record
```

Chybný parser môže rozdeliť exception na desiatky records alebo zlúčiť nesúvisiace events. Pri diagnostike zachovaj raw bytes vrátane exact newlines.

## 8. Parser a timestamp contract

Parser definuje:

- source timestamp a timezone;
- field names a types;
- raw-message preservation;
- parse-failure fallback;
- sensitive-field handling;
- schema/version.

Parse failure nemá ticho zmiznúť. Musí mať counter, quarantine alebo explicitný fallback record.

Chybný timestamp môže uložiť log mimo dashboard range-u alebo spôsobiť backend rejection. Ingestion time nie je automaticky správnou náhradou source event time-u.

## 9. Tags, filters a routing

Tag je interná routing identity. Filters a outputs používajú `Match` patterns.

```text
input tag
→ parse
→ metadata enrichment
→ normalization
→ producer-side alebo agent redaction
→ cardinality allowlist
→ route na outputs
```

Filter order je významný. Redaction po output fan-out-e je neskoro.

Riziká:

- žiadny output nematchne;
- broad match pošle logs do forbidden backendu;
- rewrite-tag loop;
- dva outputs vytvoria duplicitu;
- nedôveryhodná Kubernetes annotation určí tenant;
- všetky labels/annotations vytvoria Loki stream alebo mapping explosion.

Každá route potrebuje positive aj negative fixture.

## 10. Chunks a buffering

Fluent Bit zoskupuje records do chunks.

```text
records prichádzajú
→ chunk rastie
→ priradí sa output queue
→ flush attempt
→ success/retry/error
→ release podľa delivery contractu
```

### Memory buffering

Rýchle, ale volatile. Crash alebo node loss môže zničiť backlog. `mem_buf_limit` môže input pozastaviť; dôsledok závisí od inputu.

### Filesystem buffering

Zvyšuje outage tolerance a restart recovery, ale stále je lokálny a konečný. Potrebuje persistent path, permissions, encryption boundary, disk/inode monitoring a explicitný full-disk behavior.

`storage.total_limit_size` alebo podobný per-output limit môže pri vyčerpaní viesť k eviction/drop behavioru. Je to log-loss boundary, nie iba capacity metric.

## 11. Backpressure a retries

Backpressure vzniká, keď output nedokáže prijímať tempo inputu.

```text
backend outage/429/latency/permanent error
→ retries
→ queue a backlog age rastú
→ memory/disk pressure
→ input pause alebo drop
→ delayed alebo lost observability
```

Retry contract rozlišuje:

- temporary network/429/5xx;
- permanent mapping, label, timestamp alebo auth failure;
- partial item failure;
- timeout s unknown outcome;
- maximum backlog age a capacity.

Unlimited retry permanentného recordu môže blokovať zdravé records za ním.

## 12. Output acknowledgement semantics

Každý output má vlastný batch, compression, TLS, auth, response a idempotency model.

### Loki

Over tenant, bounded labels, structured metadata, timestamp a rejection reason. `429` môže byť retryable; invalid label alebo timestamp nemusí byť.

### Elasticsearch/OpenSearch

Top-level bulk `200` môže obsahovať failed items. Delivery verdict potrebuje per-item classification a mapping quarantine.

### OTLP

Over signal, protocol, endpoint/path, resource attributes, auth, tenant routing a downstream Collector backpressure.

Multi-output fan-out potrebuje per-output backlog a completion state. Úspech jedného outputu nepreukazuje úspech druhého.

## 13. Delivery semantics

Exactly-once nemožno predpokladať.

Duplicates môžu vzniknúť pri:

- backend write pred timeout acknowledgementom;
- restart-e pred durable checkpointom;
- reread rotated file-u;
- retry batchu;
- dvoch agents nad rovnakým source;
- migration dual-write.

Loss môže vzniknúť pri:

- memory-only buffer + crash;
- full filesystem buffer;
- ephemeral position DB;
- network input pause/drop;
- permanent invalid record bez quarantine;
- rotated file delete pred recovery.

Downstream evidence a incident workflow musia tolerovať bounded duplicates a vedieť identifikovať loss window.

## 14. Kubernetes DaemonSet boundary

Typický path:

```text
container stdout/stderr
→ CRI files na Node
→ jeden Fluent Bit Pod per Node
→ persistent Tail DB a buffer
→ metadata/RBAC
→ remote backend
```

Dôležité controls:

- mount exact runtime log paths;
- persistent writable state;
- tolerations pre všetky relevantné Nodes;
- Pod Security a hostPath permissions;
- resource requests/limits;
- graceful shutdown;
- network policy a credentials;
- canary rollout podľa Nodes/AZs.

Agent, ktorý nebeží na tainted alebo special Node cohort-e, vytvára observability blind spot aj pri green DaemonSet status-e pre ostatné Nodes.

## 15. Health, shutdown a self-observability

Liveness má testovať, či process dokáže pokračovať, nie či vzdialený backend je práve dostupný. Restart pri každom output failure môže zničiť local state a zhoršiť outage.

Graceful shutdown potrebuje bounded čas na zastavenie inputov, flush chunks, uloženie offsets a uzavretie DB. Veľký backlog sa nemusí zmestiť do krátkeho `terminationGracePeriodSeconds`.

Sleduj:

- input records/bytes a active files;
- parser/filter drops;
- output processed/retried/errors/dropped;
- response codes a item failures;
- chunk count, bytes a oldest backlog age;
- paused inputs;
- Tail DB a storage health;
- process restarts a loaded config generation;
- end-to-end canary query.

```text
source canary vznikne
→ input counter +1
→ output acknowledgement
→ backend query ho nájde
→ duplicate count = expected
→ latency pod guardrailom
```

## 16. Worked failure: backend outage, liveness restarty, duplicates aj loss

### Symptóm

Počas 18-minútového Loki outage rastie počet Fluent Bit restartov na production Nodes. Po obnovení Loki obsahuje časť settlement logs dvakrát, ale 6-minútové obdobie z dvoch Nodes úplne chýba. DaemonSet bol počas incidentu `Desired = Ready` a liveness po každom restarte znovu zozelenela.

### Exact subject

```text
subject: FB-PAY-45
DaemonSet generation: FB-PAY-318
affected Nodes: pay-node-17, pay-node-21
input: Tail /var/log/containers/provider-adapter*.log
Tail DB: /fluent-bit/state/tail.db
filesystem buffer: /fluent-bit/state/storage
state mount: container writable layer — bez persistent volume
read_from_head: true
liveness: zlyhá pri output health failure
Loki outage: 04:12–04:30 UTC
rotation interval: 5 min
```

### Competing hypotheses

1. application počas šiestich minút nelogovala;
2. Loki odmietol entries pre labels/timestamps;
3. parser/filter zahodil iba affected events;
4. agent nematchol output route;
5. backend timeout vytvoril duplicates;
6. restart zničil Tail DB a filesystem chunks;
7. rotation zmazala unread files pred recovery;
8. Grafana query používa nesprávny tenant alebo time range.

### Discriminating evidence

```text
source application counters: events existovali
Node files pred rotáciou: obsahovali sample IDs
Fluent Bit output retries/backlog: rast
liveness restarts: každých ~60 s počas outage
state paths: nie sú volume mount
po restarte tail.db: nová database
read_from_head: reread current files
current files: duplicated event IDs po recovery
rotated files staršie než retention: už neexistujú
Loki rejection counters: bez permanent 4xx
```

Mechanizmus:

```text
Loki je dočasne nedostupný
→ Fluent Bit bufferuje chunks na container writable layer
→ output-dependent liveness označí process unhealthy
→ kubelet nahradí container
→ Tail DB aj backlog zaniknú
→ read_from_head znovu prečíta ešte existujúce files
→ timeout/replay vytvoria duplicates
→ staršie rotated files sa medzi restartmi zmažú
→ ich unread lines už nemožno obnoviť
→ Pod readiness sa vráti, ale evidence má duplicate aj loss window
```

### Containment

- odstrániť output dependency z liveness rozhodnutia;
- zastaviť DaemonSet rollout a ďalšie restarty;
- zachovať remaining source files, inodes, agent metrics/logs a backend responses;
- predĺžiť rotation retention na affected Nodes;
- označiť affected interval ako incomplete evidence;
- nevymazávať Tail DB ani nespúšťať druhý collector nad rovnakými files.

### Authoritative recovery

1. mountnúť persistent per-Node storage pre Tail DB a filesystem chunks;
2. oddeliť liveness od backend health; backlog riešiť alertom;
3. nastaviť bounded storage limits a loss policy;
4. replaynúť zachované source files s stable event/document identity;
5. deduplikovať known replay duplicates;
6. ak source files už neexistujú a niet secondary archive, explicitne uzavrieť obdobie ako unrecoverable log loss;
7. canary-nuť config na jednom Node;
8. fault-injectnúť backend outage, container restart, rotation a recovery;
9. rozšíriť rollout po Node/AZ cohorts.

### Fluent Bit acceptance verdict

Recovery je prijatá, keď:

- Tail DB a chunks prežijú container aj Pod restart podľa navrhnutého boundary;
- temporary Loki outage nespúšťa liveness restart loop;
- backlog age rastie a po recovery bezpečne klesne;
- canary events sú queryovateľné s očakávaným duplicate contractom;
- disk-full test vyvolá explicitný loss alert a definovanú policy;
- permanent invalid record ide do quarantine a neblokuje queue;
- forbidden security logs nie sú routované do application tenant-u;
- susedný Node a druhý DaemonSet rollout zachovajú behavior.

## 17. Troubleshooting model

### Žiadne logs

```text
source path/socket
→ input loaded
→ inode/offset DB
→ parser/multiline
→ tag/filter Match
→ chunk/buffer
→ output TLS/auth
→ backend response
→ tenant/index/time query
```

### Duplicates

```text
agent restarts
→ Tail DB persistence
→ rotation/inode reuse
→ timeout/unknown outcome
→ retry/fan-out
→ multiple readers
→ backend document identity
```

### Rastúci disk backlog

```text
output availability/429/permanent errors
→ retry policy
→ oldest backlog age
→ per-output limit
→ disk/inodes
→ flush concurrency
→ loss/eviction boundary
```

### Metadata chýbajú

```text
tag/file-name contract
→ Kubernetes API/DNS/RBAC
→ metadata cache
→ Pod lifecycle
→ filter order
→ allowlist
```

## 18. Anti-patterny

### Position DB na ephemeral filesysteme

Restart mení replay behavior a evidence completeness.

### Liveness via remote backend

Dočasný backend outage vytvára agent churn a state loss.

### Unlimited retry permanentných errors

Queue sa nikdy nevyprázdni.

### Všetky Kubernetes labels a annotations

Vytvára cardinality, mapping, privacy a tenant-routing riziká.

### Dva DaemonSets čítajú rovnaké files

Vytvára duplicates a dvojnásobný load.

### Parse/redaction až v backend-e

Citlivé data už prešli agentom, sieťou a bufferom.

## 19. Kontrolné otázky

1. Čo tvorí exact Fluent Bit subject?
2. Ako sa líši source line, record, chunk a backend document/entry?
3. Prečo Tail DB potrebuje persistent file identity a offset state?
4. Ako rotation vytvára duplicate alebo loss boundary?
5. Prečo filter order ovplyvňuje security a schema?
6. Ako tag a `Match` vytvárajú routing verdict?
7. Aký je rozdiel medzi memory a filesystem bufferingom?
8. Prečo exactly-once nemožno predpokladať?
9. Ako bulk `200` môže stále obsahovať failed items?
10. Prečo output failure nemá byť automaticky liveness failure?
11. Ako overíš config generation po rollout-e?
12. Ako vykonáš end-to-end log-delivery canary?

## Glossary impact

Relevantné pojmy: Fluent Bit subject, source-file generation, Tail offset generation, position-state durability, parser generation, tag-route generation, filter-order contract, chunk-delivery state, filesystem-backlog generation, output acknowledgement, unknown log-delivery outcome, replay duplicate, log-loss window, output-independent liveness, log-delivery canary a Fluent Bit acceptance verdict.

## Primárne zdroje

- [Fluent Bit documentation](https://docs.fluentbit.io/manual)
- [Configure Fluent Bit](https://docs.fluentbit.io/manual/administration/configuring-fluent-bit)
- [YAML configuration](https://docs.fluentbit.io/manual/administration/configuring-fluent-bit/yaml/configuration-file)
- [Classic configuration](https://docs.fluentbit.io/manual/administration/configuring-fluent-bit/classic-mode)
- [Tail input](https://docs.fluentbit.io/manual/pipeline/inputs/tail)
- [Buffering and storage](https://docs.fluentbit.io/manual/administration/buffering-and-storage)
- [Backpressure](https://docs.fluentbit.io/manual/administration/backpressure)
- [Monitoring](https://docs.fluentbit.io/manual/administration/monitoring)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Elasticsearch alebo OpenSearch](elasticsearch-opensearch.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Jaeger a Tempo →](jaeger-tempo.md)
<!-- KNOWLEDGE-NAVIGATION:END -->