# Fluent Bit

Fluent Bit je ľahký telemetry agent a processor určený na zber, parsing, enrichment, buffering, routing a export logs, metrics a traces. V observability stacku sa používa najmä ako Node alebo host agent medzi lokálnymi zdrojmi telemetry a vzdialenými backends ako Loki, Elasticsearch/OpenSearch, OpenTelemetry Collector alebo cloud logging služby.

Fluent Bit nie je durable message broker ani automaticky exactly-once delivery systém. Jeho loss, retry a duplicate behavior závisí od input pluginu, buffer mode-u, filesystem durability, output pluginu, backend acknowledgement-u a crash scenára.

## 1. Mentálny model

```text
input
→ parser alebo decoder
→ tag
→ filters
→ router podľa Match
→ chunks a buffering
→ scheduler/retry
→ output
→ backend acknowledgement alebo failure
```

Každá vrstva môže meniť data, metadata, delivery semantics a failure behavior.

## 2. Pipeline komponenty

Fluent Bit pipeline sa skladá z:

- inputs,
- parsers,
- filters,
- tags a routing,
- buffers/chunks,
- outputs,
- service-level configuration,
- monitoring endpointov.

Jedna pipeline môže routovať rovnaký record do viacerých outputs. To zvyšuje flexibilitu aj backpressure a storage complexity.

## 3. Configuration formats

Aktuálna Fluent Bit dokumentácia označuje YAML ako štandardný configuration format od verzie 3.2. Classic `.conf` format je stále podporovaný, ale dokumentácia uvádza plánovanú deprecation na konci roka 2026.

Pri novom projekte preferuj YAML, ak všetky používané plugins a deployment tooling podporujú požadované options.

Príklad:

```yaml
service:
  flush: 1
  log_level: info
  storage.path: /var/lib/fluent-bit/storage

pipeline:
  inputs:
    - name: tail
      path: /var/log/containers/*.log
      tag: kube.*
      db: /var/lib/fluent-bit/tail.db
      storage.type: filesystem

  filters:
    - name: kubernetes
      match: kube.*

  outputs:
    - name: loki
      match: kube.*
      host: loki-gateway
      port: 3100
```

Exact option names a nesting over vždy podľa dokumentácie konkrétnej Fluent Bit verzie.

## 4. Inputs

Input plugin získava telemetry zo zdroja.

Príklady:

- Tail,
- systemd,
- forward,
- HTTP,
- TCP,
- syslog,
- journald,
- Kubernetes Events podľa pluginu,
- Prometheus scrape alebo metrics inputs,
- OpenTelemetry.

Každý input má vlastné semantics pri:

- pause/resume,
- offset persistence,
- replay,
- connection close,
- memory pressure,
- filesystem buffering,
- data loss.

## 5. Tail input

Tail input sleduje súbory a číta nové records.

Dôležité settings/concepts:

- path a exclude patterns,
- position database,
- parser,
- multiline parser,
- refresh interval,
- rotate wait,
- file buffers,
- inode/file identity,
- skip long lines,
- storage type,
- database locking/sync behavior.

### Position database

Position database uchováva offset a identity sledovaných súborov.

Bez persistentnej DB môže restart viesť podľa konfigurácie k:

- reread od začiatku,
- skipnutiu existujúcich dát,
- duplicates,
- nejasnému recovery behavioru.

DB musí byť na persistentnom writable storage a chránená pred súbežným používaním viacerými agentmi.

## 6. Log rotation

Container a host logs sa rotujú.

Agent musí správne zvládnuť:

- rename,
- truncation,
- nový inode,
- starý otvorený file descriptor,
- delayed writes do rotated file,
- delete po rotate windowe.

Príliš krátky rotate wait môže stratiť oneskorené lines. Príliš dlhý drží veľa file handles a state-u.

Pri chýbajúcich logs porovnaj inode, file path, tail DB a runtime rotation policy.

## 7. Multiline

Stack traces a niektoré application logs tvoria viac fyzických lines, ale jeden logical event.

Multiline parser potrebuje:

- start-state pattern,
- continuation rules,
- flush timeout,
- language/runtime-specific grammar,
- memory limit,
- testy pre interleaved logs.

Nesprávny multiline parser môže:

- rozdeliť jeden exception na desiatky records,
- spojiť nesúvisiace events,
- držať buffer príliš dlho,
- zvýšiť line size nad backend limit.

Preferuj application-side single-line structured JSON, keď je to možné.

## 8. Parsers

Parser premieňa raw text na structured record.

Podporované modely zahŕňajú napríklad:

- JSON,
- regex,
- logfmt,
- LTSV,
- decoders pre escaped alebo nested content.

Parser contract musí definovať:

- timestamp field a format,
- timezone,
- field names/types,
- fallback pri parse failure,
- preservation raw message,
- sensitive-field handling.

Parse failure nemá ticho dropnúť record bez metric alebo quarantine pathu.

## 9. Timestamp

Timestamp je kritický pre query a retention.

Over:

- source timestamp alebo ingestion time,
- timezone,
- fractional precision,
- clock skew,
- parse fallback,
- backend accepted range,
- reprocessed historical logs.

Chybný timestamp môže spôsobiť, že log je uložený mimo očakávaného dashboard time range alebo odmietnutý backendom.

## 10. Tags a routing

Tag identifikuje record stream vo Fluent Bit pipeline a používa sa na matching filters a outputs.

Príklad:

```text
kube.production.orders
```

Filters a outputs používajú `Match` alebo pattern semantics.

Riziká:

- record nematchne žiadny output,
- broad match pošle citlivé logs nesprávnemu backendu,
- jeden record ide do viacerých outputs a vytvára duplicitu,
- rewrite tag loop,
- dynamic tag explosion.

Routing testuj s representative tags a negative cases.

## 11. Filters

Filter modifikuje, enrichuje alebo dropuje records.

Príklady:

- parser,
- Kubernetes metadata,
- modify/record modifier,
- grep,
- nest/lift,
- Lua/Wasm custom logic,
- rewrite tag,
- throttle,
- multiline podľa modelu.

Filter ordering je významný.

Príklad:

```text
parse JSON
→ enrich Kubernetes metadata
→ normalize fields
→ redact secrets
→ remove high-cardinality metadata
→ route
```

Ak redaction nastane až po output fan-out, sensitive data už mohlo odísť.

## 12. Kubernetes filter

Kubernetes filter môže doplniť metadata podľa Pod/container identity.

Typické fields:

- namespace,
- Pod,
- container,
- labels,
- annotations,
- image,
- Node.

Riziká:

- Kubernetes API/DNS/RBAC failure,
- metadata cache staleness,
- príliš veľa labels/annotations,
- tenant identity odvodená z nedôveryhodnej annotation,
- high-cardinality metadata prenesené do backend labels/index fields,
- Merge_Log alebo parsing conflicts.

Použi explicitný allowlist Kubernetes metadata, nie automatický export všetkých labels a annotations.

## 13. Chunks

Fluent Bit interně zoskupuje records do chunks.

Chunk je základná jednotka bufferingu a flushu.

Jeho lifecycle:

```text
input pridáva records
→ chunk rastie
→ route na outputs
→ flush attempt
→ success alebo retry
→ release/delete po dokončení delivery contractu
```

Pri multi-output routing môže mať chunk references pre viac destination queues.

## 14. Memory buffering

Defaultný alebo plugin-specific memory buffering je rýchly, ale obmedzený RAM.

`mem_buf_limit` môže pozastaviť input, keď memory buffer prekročí limit.

Dôsledok pause závisí od inputu:

- Tail môže uložiť file offset a pokračovať neskôr,
- TCP/UDP/network input môže stratiť prichádzajúce data,
- upstream môže blokovať alebo dropovať.

Memory buffering nie je vhodné považovať za durable outage queue.

## 15. Filesystem buffering

Filesystem buffering presúva alebo synchronizuje chunks na local disk podľa storage modelu.

Výhody:

- väčší backlog,
- lepší restart recovery,
- menšie riziko memory exhaustion,
- lepšie pre backend outages.

Limity:

- finite disk,
- local-node failure,
- filesystem corruption,
- write amplification,
- slower replay,
- potreba cleanup a monitoring,
- nie automatický cross-node durability.

Persistent storage pre DaemonSet agent musí prežiť Pod restart a mať vhodný hostPath alebo local volume model.

## 16. Backpressure

Backpressure vzniká, keď input produkuje data rýchlejšie, než outputs dokážu flushovať.

Príčiny:

- backend outage,
- `429` throttling,
- vysoká network latency,
- authentication failure s retries,
- príliš veľký backlog,
- slow filter,
- disk saturation,
- jeden pomalý output pri fan-out.

Fluent Bit môže:

- bufferovať v memory,
- bufferovať na filesystem,
- pozastaviť input,
- retryovať,
- po dosiahnutí limitu dropovať podľa configuration/input/output semantics.

Backpressure strategy musí byť navrhnutá pred incidentom.

## 17. Storage limits

Relevantné controls zahŕňajú podľa configuration mode-u a verzie:

- memory buffer limit,
- maximum chunks držané v memory,
- backlog memory limit,
- filesystem total limits,
- per-output `storage.total_limit_size`,
- pause behavior.

Ak output queue dosiahne total limit, môže byť potrebné zahodiť najstaršie chunks, aby sa uvoľnilo miesto pre nové data. Tento behavior musí byť považovaný za explicitný log-loss boundary a alertovaný.

## 18. Retries

Output plugin vracia typicky status podobný:

- success,
- retry,
- error/permanent failure.

Retry policy musí riešiť:

- max attempts alebo unlimited model,
- exponential backoff,
- jitter,
- backlog age,
- permanent `4xx`,
- authentication failures,
- partial success,
- backend idempotency,
- shutdown behavior.

Nekonečný retry permanentne invalidného recordu môže blokovať queue.

## 19. Delivery semantics

Exactly-once sa nedá predpokladať.

Duplicates môžu vzniknúť pri:

- timeout po backend write pred acknowledgementom,
- restart pred potvrdením offsetu,
- reread rotated file-u,
- retry batchu,
- fan-out,
- backend ingest retry.

Loss môže vzniknúť pri:

- volatile memory buffer a process/node crash,
- full filesystem buffer,
- pause pri network inpute,
- permanent output error,
- parser/filter drop,
- file removal pred dočítaním,
- corrupt position database.

Downstream schema a incident workflows musia tolerovať bounded duplicates a identifikovať loss.

## 20. Outputs

Output plugin odosiela records do destination.

Príklady:

- Loki,
- Elasticsearch/OpenSearch,
- OpenTelemetry,
- Kafka,
- cloud logging,
- HTTP,
- file/stdout pre test.

Každý output má vlastné:

- authentication,
- TLS,
- batching,
- compression,
- response semantics,
- retry,
- index/label mapping,
- concurrency,
- idempotency.

## 21. Loki output

Pri Loki outpute navrhni:

- tenant identity,
- bounded labels,
- structured metadata,
- line format,
- timestamp,
- batch size,
- compression,
- retry a rate-limit behavior.

Nepromuj všetky Kubernetes labels na Loki labels.

Pri `400` over label/timestamp/line constraints. Pri `429` over Loki tenant limits a Fluent Bit backlog.

## 22. Elasticsearch/OpenSearch output

Pri document-search backend-e navrhni:

- data stream alebo index target,
- document ID semantics,
- timestamp,
- bulk batch,
- mappings/templates,
- lifecycle,
- partial-item response handling,
- retry `429`,
- quarantine mapping errors.

HTTP `200` bulk response môže stále obsahovať failed items. Output/plugin monitoring musí zachytiť item-level failures.

## 23. OpenTelemetry output

OTLP output umožňuje poslať telemetry OpenTelemetry Collectoru alebo kompatibilnému receiveru.

Over:

- signal type,
- gRPC/HTTP protocol,
- endpoint a path,
- TLS/mTLS,
- authentication headers,
- resource attributes,
- retry/backpressure,
- collector tenant routing.

Fluent Bit a OpenTelemetry Collector sa môžu dopĺňať: Fluent Bit ako efficient edge log agent, Collector ako central policy, enrichment a multi-signal gateway.

## 24. Multi-output routing

Jeden record možno poslať do viacerých destinations.

Use cases:

- primary log backend + security archive,
- migration dual-write,
- local debug + remote backend.

Riziká:

- dvojnásobný network/storage cost,
- odlišné delivery outcomes,
- jeden output vytvára backpressure,
- inconsistent transformations,
- ťažké porovnanie completeness,
- migration sa nikdy neukončí.

Dual-write potrebuje termination criteria a per-output health metrics.

## 25. Kubernetes DaemonSet

Bežný deployment:

```text
jeden Fluent Bit Pod per Node
→ mount /var/log/containers a runtime log directories
→ persistent position DB/buffer
→ Kubernetes metadata enrichment
→ remote backend
```

Potrebné controls:

- ServiceAccount/RBAC,
- hostPath read/write permissions,
- Pod Security,
- CPU/memory requests a limits,
- priority class podľa potreby,
- tolerations pre relevantné Nodes,
- graceful shutdown,
- network policy,
- disk quota,
- rollout strategy.

Ak agent nebeží na tainted control-plane alebo special Nodes, logs z týchto Nodes sa nezbierajú.

## 26. Graceful shutdown

Pri termination agent potrebuje čas na:

- zastavenie inputu,
- flush queued chunks,
- uloženie offset state-u,
- uzavretie DB/files,
- dokončenie retries podľa bounded timeoutu.

Kubernetes `terminationGracePeriodSeconds` musí zodpovedať flush a backlog modelu. Nečakaj, že veľký filesystem backlog sa odošle počas krátkeho shutdownu.

## 27. Self-monitoring

Fluent Bit poskytuje interné metrics cez HTTP/Prometheus-compatible endpointy podľa konfigurácie.

Sleduj:

- input records/bytes,
- output processed/retried/errors/dropped,
- storage chunks a bytes,
- backlog,
- paused inputs,
- retry queue,
- filter drops,
- process CPU/memory,
- uptime/restarts,
- tail files/offset state,
- backend response codes,
- filesystem capacity.

Critical alert:

```text
source log rate existuje
+ output success klesá
+ backlog rastie
→ imminent loss alebo delayed observability
```

## 28. Health checks

Process health alebo HTTP liveness nepreukazuje end-to-end delivery.

Použi vrstvy:

- process/liveness,
- configuration parse/startup,
- input active,
- output connectivity,
- backlog bounded,
- synthetic canary log queryovateľný v backend-e.

Liveness probe nesmie restartovať agenta pri dočasnom backend outage a tým zhoršovať backlog recovery.

## 29. Security

Chráň:

- backend credentials,
- TLS CA/client keys,
- host log access,
- position DB a filesystem buffer,
- configuration,
- Kubernetes API token,
- admin/metrics endpoint.

Minimalizuj:

- secrets v logs,
- request/response bodies,
- full environment variables,
- Kubernetes annotations,
- local buffer retention citlivých dát.

Filesystem buffer je dočasný log store a potrebuje permissions, encryption boundary a cleanup.

## 30. Configuration validation a rollout

Pred nasadením:

1. validuj syntax použitou verziou binary,
2. spusti representative input samples,
3. over parse output na stdout/test destination,
4. testuj multiline,
5. testuj backend `429` a outage,
6. testuj disk-full behavior,
7. testuj restart/replay,
8. testuj permanent invalid record,
9. meraj CPU/memory a throughput,
10. rollout-ni canary Nodes.

Configuration change môže zmeniť schema, routing a retention cost bez application deploymentu.

## 31. Troubleshooting: žiadne logs

```text
source file/socket existuje?
→ input plugin loaded?
→ path/permissions?
→ tail DB offset?
→ parser/multiline?
→ tag?
→ filter Match/drop?
→ output Match?
→ output connectivity/auth/TLS?
→ backend response?
→ query tenant/index/time range?
```

Použi dočasný stdout output iba v kontrolovanom prostredí; môže leak-nuť citlivé logs a zvýšiť volume.

## 32. Troubleshooting: duplicates

Over:

- agent restarts,
- tail DB persistence/corruption,
- file rotation/inode reuse,
- retry po timeout-e,
- multi-output/fan-out,
- viac agentov číta rovnaký file,
- backend document ID/dedup model,
- replay backlogu.

Nemaž tail DB ako prvý krok; môže spôsobiť masívny reread.

## 33. Troubleshooting: chýbajú multiline logs

Over:

- parser name a assignment,
- first-line rule,
- flush timeout,
- interleaving,
- max buffer/line size,
- backend line limit,
- source runtime format.

Zachovaj raw file sample vrátane exact newlines.

## 34. Troubleshooting: memory rastie

Over:

- memory buffering,
- `mem_buf_limit`,
- slow output,
- retry backlog,
- veľké multiline records,
- oversized batches,
- filter/Lua plugin,
- multi-output references,
- filesystem chunks držané `up` v memory,
- metrics endpoint.

Zvýšenie memory limitu bez vyriešenia output throughputu iba oddiali OOM.

## 35. Troubleshooting: disk buffer rastie

Over:

- backend availability/latency,
- permanent auth/mapping errors,
- retry policy,
- per-output total limit,
- storage path capacity/inodes,
- flush concurrency,
- oldest backlog age,
- output fan-out.

Rozhodni, či prioritou je zachovať najstaršie alebo najnovšie logs. Default loss behavior nemusí zodpovedať incident potrebe.

## 36. Troubleshooting: backend `429`

Postup:

1. potvrď destination a response body,
2. zníž batch concurrency/flush pressure,
3. over backend ingestion capacity a limits,
4. sleduj retry/backlog growth,
5. škáluj alebo oprav backend,
6. nastav bounded queue/loss alert,
7. validuj recovery bez retry stormu.

## 37. Troubleshooting: Kubernetes metadata chýbajú

Over:

- tag/file-name pattern očakávaný filtrom,
- API connectivity/DNS,
- ServiceAccount token,
- RBAC,
- metadata cache,
- Pod už zmazaný,
- Node hostname identity,
- filter ordering,
- labels/annotations allowlist.

## 38. Troubleshooting: config sa aplikuje, ale route nie

Over exact tag a `Match` pattern. Fluent Bit konfigurácia môže byť syntakticky validná, ale records nemusia matchovať žiadny output.

Pridaj test samples pre každý intended route aj negatívny route.

## 39. Fluent Bit oproti Fluentd a OpenTelemetry Collectoru

### Fluent Bit

- ľahký edge/Node agent,
- silný tail, parsing a buffering model,
- nízky resource footprint,
- široké output plugins.

### Fluentd

- väčší runtime a plugin ecosystem,
- komplexnejšie processing use cases,
- vyšší resource footprint podľa pipeline.

### OpenTelemetry Collector

- vendor-neutral multi-signal pipelines,
- OTLP-native,
- central processors, sampling a routing,
- menej špecializovaný na niektoré low-level file-tail use cases podľa component distribution.

Častý model:

```text
Fluent Bit na Node
→ OpenTelemetry Collector gateway
→ Loki/OpenSearch/cloud backends
```

Nepridávaj vrstvy bez jasnej policy, buffering alebo interoperability potreby.

## 40. Anti-patterny

### Memory-only buffer bez loss analýzy

Backend outage alebo process crash môže stratiť data.

### Unlimited retry permanentných errors

Queue sa nikdy nevyprázdni.

### Všetky Kubernetes labels do backendu

Vytvára cardinality, mapping a privacy problémy.

### Dva DaemonSets čítajú rovnaké files

Vytvára duplicates a dvojnásobný load.

### Position DB na ephemeral Pod filesysteme

Restart mení replay behavior.

### Parsing a redaction až v backend-e

Sensitive data už prešlo agentom a sieťou.

### Liveness restart pri každom output failure

Zvyšuje churn a môže zhoršiť loss/replay.

### Agent metrics nesledované

Telemetry loss zostane neviditeľná.

## 41. Kontrolné otázky

1. Ako vyzerá Fluent Bit pipeline?
2. Aký je rozdiel medzi input, parser, filter a output?
3. Na čo slúži tag a `Match`?
4. Prečo je position database kritická pre Tail input?
5. Ako log rotation a inode ovplyvňujú duplicates/loss?
6. Ako sa líši memory a filesystem buffering?
7. Čo sa deje pri backpressure?
8. Prečo exactly-once nemožno predpokladať?
9. Ako spracovať partial bulk failures v OpenSearch/Elasticsearch?
10. Ako monitorovať samotný Fluent Bit?
11. Ako diagnostikovať rastúci disk backlog?
12. Kedy kombinovať Fluent Bit s OpenTelemetry Collectorom?

## Glossary impact

Relevantné pojmy: Fluent Bit, input plugin, Tail input, position database, multiline parser, tag, Match, filter plugin, Kubernetes filter, chunk, memory buffering, filesystem buffering, backpressure, `mem_buf_limit`, `storage.total_limit_size`, output plugin, retry queue, delivery semantics, log replay, log loss boundary, graceful shutdown a telemetry agent self-monitoring.

## Primárne zdroje

- [Fluent Bit documentation](https://docs.fluentbit.io/manual)
- [Fluent Bit configuration](https://docs.fluentbit.io/manual/administration/configuring-fluent-bit)
- [Data pipeline inputs](https://docs.fluentbit.io/manual/data-pipeline/inputs)
- [Filters](https://docs.fluentbit.io/manual/concepts/data-pipeline/filter)
- [Outputs](https://docs.fluentbit.io/manual/concepts/data-pipeline/output)
- [Buffering and storage](https://docs.fluentbit.io/manual/administration/buffering-and-storage)
- [Backpressure](https://docs.fluentbit.io/manual/administration/backpressure)
- [Monitoring](https://docs.fluentbit.io/manual/administration/monitoring)
- [Tail input](https://docs.fluentbit.io/manual/pipeline/inputs/tail)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Elasticsearch alebo OpenSearch](elasticsearch-opensearch.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Jaeger a Tempo →](jaeger-tempo.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
