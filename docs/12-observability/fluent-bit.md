# Fluent Bit

Fluent Bit je edge telemetry agent a processor. Číta local files, systemd, sockets alebo ďalšie inputs, vytvára records, parsuje timestamps a fields, aplikuje filters, priraďuje tags, routuje chunks do outputs a riadi buffering, retries a backend acknowledgements. Je ľahký, ale nie je durable message broker ani exactly-once transport.

Log delivery závisí od source identity a offsetu, parser/multiline behavioru, tag routing, processor orderu, chunk storage, output response contractu a crash/restart modelu. Process `Running` preto nie je dôkazom, že každý source event vznikol v cieľovom backende presne raz.

## End-to-end lifecycle

```text
source occurrence
→ file/inode alebo socket identity
→ input read a checkpoint
→ parser a timestamp
→ multiline assembly
→ tag a route
→ filters a metadata enrichment
→ memory/filesystem chunk
→ scheduler, retry a backoff
→ output request
→ backend per-request/per-item acknowledgement
→ checkpoint advancement a buffer retirement
→ backend query a business evidence
```

Parser je typicky priradený inputu a transformuje raw source pri ingestion. Filters pracujú nad interným recordom a output plugin ho serializuje pre backend. Fluent Bit dokumentácia upozorňuje, že input parser sa aplikuje pred filters a buffered data používa internú reprezentáciu; neskoršia zmena parsera neprepíše records už uložené v bufferi. Exact behavior sa viaže na nasadenú version a config mode. citeturn886976search15turn886976search16turn886976search19

## Exact delivery subject

Atlas používa `FB-PAY-43`:

```yaml
agent: fluent-bit-daemonset
agentGeneration: FB-4.0-PAY-12
node: ip-10-42-18-27
sourcePath: /var/log/containers/provider-adapter-*.log
sourceIdentity: inode + device + filename
checkpointDatabase: /var/lib/fluent-bit/tail-containers.db
parser: cri
multilineParser: cri
tag: kube.payments.provider-adapter
filters:
  - kubernetes metadata
  - nest and modify
  - record_modifier telemetry_schema=atlas-payments-12
outputs:
  - loki tenant atlas-production
  - s3 emergency archive for failed-permanent cohort
storagePath: /var/lib/fluent-bit/storage
```

Incident evidence musí zachovať exact config file/hash, process args, input path, inode/device, DB checkpoint, tag, chunk state, retry count, output response a backend query. Filename bez inode nestačí pri rotation.

## YAML configuration

```yaml
service:
  flush: 5
  daemon: off
  log_level: info
  storage.path: /var/lib/fluent-bit/storage
  storage.sync: normal
  storage.checksum: on
  storage.backlog.mem_limit: 64M
  http_server: on
  http_listen: 0.0.0.0
  http_port: 2020

pipeline:
  inputs:
    - name: tail
      tag: kube.payments.*
      path: /var/log/containers/provider-adapter-*.log
      parser: cri
      multiline.parser: cri
      db: /var/lib/fluent-bit/tail-containers.db
      db.sync: normal
      read_from_head: false
      refresh_interval: 5
      rotate_wait: 30
      storage.type: filesystem
      mem_buf_limit: 32M
      skip_long_lines: off

  filters:
    - name: kubernetes
      match: kube.payments.*
      merge_log: on
      keep_log: off
      labels: off
      annotations: off

    - name: modify
      match: kube.payments.*
      add:
        - telemetry_schema atlas-payments-12
      remove:
        - authorization
        - payment.card_number

  outputs:
    - name: loki
      match: kube.payments.*
      host: loki-distributor
      port: 3100
      tenant_id: atlas-production
      labels: service_name=$kubernetes['labels']['app'], deployment_environment=production
      structured_metadata: trace_id=$trace_id,pod_name=$kubernetes['pod_name'],payment_operation_id=$payment_operation_id
      line_format: json
```

Configuration preukazuje desired pipeline, checkpoint DB, filesystem buffering a Loki label/metadata mapping. Nepreukazuje, že exact file je loaded, parser name existuje, filesystem je writable alebo output fields sú present.

Syntax/config validation:

```bash
fluent-bit --config=/fluent-bit/etc/fluent-bit.yaml --dry-run

fluent-bit --version
```

Dry run preukazuje parse a plugin/config initialization compatibility pre binary. Nepreukazuje source access, runtime metadata API, backend connectivity ani delivery semantics. Version output sa uloží k config generation, pretože plugin options a YAML support sú version-sensitive.

## Tail input, inode a checkpoint

Tail plugin sleduje files a ukladá offset state do SQLite DB. Rotation môže rename-nuť file, vytvoriť nový inode pod pôvodným name alebo skopírovať/truncate-nuť content. Stable source identity preto používa inode/device a checkpoint, nie iba filename.

```bash
stat -c 'path=%n device=%d inode=%i size=%s mtime=%y' \
  /var/log/containers/provider-adapter-abc.log

sqlite3 /var/lib/fluent-bit/tail-containers.db '.tables'

sqlite3 /var/lib/fluent-bit/tail-containers.db \
  'select name, offset, inode, created, rotated from in_tail_files;'
```

`stat` preukazuje current filesystem identity. DB query preukazuje checkpoint records podľa active schema, ktorá sa môže líšiť medzi versions. Ručná editácia DB počas running agentu je zakázaná; observation sa vykonáva na copy alebo podľa supported tooling.

`read_from_head=false` pri novom unseen file začne na end-e podľa plugin semantics a môže preskočiť pre-existing lines. Pri recovery po strate DB môže rovnaká konfigurácia spôsobiť loss; `read_from_head=true` môže naopak replay-nuť celý file a vytvoriť duplicates. Recovery decision potrebuje authoritative source retention a backend deduplication model.

## Parsing a multiline

CRI parser example:

```ini
[PARSER]
    Name        cri
    Format      regex
    Regex       ^(?<time>[^ ]+) (?<stream>stdout|stderr) (?<logtag>[^ ]*) (?<log>.*)$
    Time_Key    time
    Time_Format %Y-%m-%dT%H:%M:%S.%L%z
```

Application JSON je často vnorený v `log` field-e a Kubernetes filter `Merge_Log` ho môže parse-nuť podľa configuration. Malformed JSON alebo stack trace potrebuje explicitný failure behavior. Silent parser failure môže nechať raw string a downstream query fields chýbajú.

Multiline state machine musí mať start/continuation rules a flush timeout. Nesprávna start regex môže spojiť viac requests do jedného giant recordu alebo rozdeliť stack trace na stovky lines. `skip_long_lines` rozhoduje, či oversized line input zastaví alebo preskočí podľa plugin contractu; preskočenie potrebuje counter/alert, inak je to silent loss.

Parser test s fixture:

```bash
cat > /tmp/provider.log <<'EOF'
2026-07-29T09:18:42.114Z stdout F {"level":"error","trace_id":"4bf92f3577b34da6a3ce929d0e0e4736","error_type":"tls.unknown_ca","message":"handshake failed"}
EOF

fluent-bit \
  --input tail \
  --prop 'path=/tmp/provider.log' \
  --prop 'read_from_head=true' \
  --prop 'parser=cri' \
  --output stdout \
  --flush 1
```

Stdout output preukazuje local parser/record result pre fixture. Nepreukazuje production Kubernetes metadata, multiline timing, buffer/retry alebo Loki output.

## Tags, matching a filter order

Tag je routing identity. `Match` a `Match_Regex` rozhodujú, ktoré filters a outputs record dostanú. Wrong tag môže viesť k zero outputs alebo duplicate delivery do viacerých outputs.

```text
input tag kube.payments.provider-adapter
→ kubernetes filter matches kube.payments.*
→ modify filter removes forbidden fields
→ Loki output matches kube.payments.*
```

Filter order je executable policy. Redaction musí prebehnúť pred output serialization. Kubernetes metadata filter môže závisieť od API/cache connectivity; metadata failure nesmie automaticky zablokovať raw log delivery bez explicitného decisionu.

Config review kontroluje, či každý intended tag má aspoň jeden output a či sensitive fields nemôžu obísť redaction cez secondary output.

## Buffering, chunks a backpressure

Inputs vytvárajú chunks. Memory buffering je rýchle, ale process crash môže stratiť in-memory state podľa plugin/storage behavioru. Filesystem buffering zvyšuje resilience, no potrebuje disk capacity, permissions, checksum a recovery monitoring.

Internal metrics:

```bash
curl -fsS http://127.0.0.1:2020/api/v1/metrics/prometheus \
  | grep -E 'fluentbit_(input|filter|output|storage)'
```

Output preukazuje agent internal counters na konkrétnom instance. Metric names sa overujú pre version. `records` read vs output processed rozdiel môže znamenať buffered, retried, dropped alebo routed elsewhere; potrebuje per-plugin/tag accounting.

Storage inventory:

```bash
du -sh /var/lib/fluent-bit/storage

df -h /var/lib/fluent-bit/storage

find /var/lib/fluent-bit/storage -maxdepth 2 -type f -printf '%s %p\n' | sort -n | tail
```

Commands preukazujú filesystem usage a files, nie validný chunk state. Ručné mazanie buffer files počas incidentu ničí unresolved delivery authority a je zakázané bez explicitného data-loss decisionu.

Backpressure nastane, keď output retryuje a input pokračuje. `mem_buf_limit`, filesystem backlog limits a pause/resume behavior rozhodujú, či source read pokračuje. Pri tail files môže paused input neskôr dobehnúť, ak source file zostane; pri ephemeral socket source môže pressure znamenať loss.

## Output acknowledgement a retries

Loki output success typicky závisí od push HTTP response. Elasticsearch/OpenSearch output musí kontrolovať bulk item results, nie iba HTTP status. Output plugin contract sa preto líši.

Retry môže doručiť rovnaký record viackrát, ak backend request commitol a response sa stratila. Fluent Bit nie je exactly-once. Downstream deduplication môže používať stable event ID v products, ktoré to podporujú; Loki log streams typicky tolerujú duplicate line a investigation musí poznať replay window.

Retry policy potrebuje bounded backoff, queue/disk guardrail a permanent-error path. Mapping `400` sa opakovaním bez schema change neopraví a môže blokovať buffer. Permanent invalid records idú do explicitného quarantine/archive flowu podľa data policy.

## Health a loaded state

HTTP server poskytuje health/metrics endpoints podľa configuration. Process health nepreukazuje source readability ani output delivery. Kubernetes readiness, ktorá kontroluje iba port 2020, môže ponechať agent Ready pri plnom storage alebo permanent backend deny.

Loaded config generation sa publikuje ako metric/log field a porovnáva s DaemonSet desired generation. Canary line prejde source → agent → backend query:

```bash
CANARY_ID="fb-canary-$(date -u +%s)"
printf '{"event":"telemetry.canary","canary_id":"%s"}\n' "$CANARY_ID" \
  >> /var/log/atlas-observability-canary.log

logcli query \
  --addr=http://loki-query-frontend:3100 \
  --org-id=atlas-production \
  --since=10m \
  "{service_name=\"observability-canary\"} |= \"$CANARY_ID\""
```

Append preukazuje source file write. Backend query success preukazuje one end-to-end path. Count musí byť interpretovaný podľa retry/duplicate semantics; exactly one result nie je automaticky garantovaný bez downstream identity contractu.

## Worked incident: restart vytvorí duplicates a následnú loss

Node disk pressure ukončí Fluent Bit. Tail DB je na ephemeral filesysteme a po Pod replacement-e zmizne. `read_from_head=true` spôsobí replay retained container logov. Loki dostane duplicates, output retries rastú a local filesystem buffer sa zaplní. Operator zmení `read_from_head=false` a ručne zmaže buffer, čím preskočí nové unresolved lines.

Competing hypotheses sú application duplicate logging, container runtime rotation, checkpoint loss, backend retry, multiline duplication alebo query overlap. Inode/DB evidence ukáže novú prázdnu checkpoint DB a replay od offsetu 0. Records nesú rovnaké application event IDs, ale nové ingestion attempts.

Containment zastaví ďalšie Pod replacements a zachová source files, DB copy, buffer a backend sample. Ručné mazanie sa zastaví. Recovery umiestni checkpoint DB a buffer na persistent host path, nastaví bounded filesystem storage a source retention väčšiu než recovery window. Quarantine job deduplikuje business audit exports podľa event ID; Loki diagnostic logs zostanú označené replay generation.

Canary overí source read, offset advancement, restart resume, backend delivery a no forbidden sensitive fields. Failure test preruší backend, vytvorí backlog, reštartuje agent a očakáva bounded replay bez loss. Acceptance povoľuje at-least-once duplicates v documented window, ale žiadny unresolved chunk sa nesmie zmazať bez data-loss verdictu.

## Kontrolné otázky

1. Prečo Fluent Bit process health nepreukazuje log delivery?
2. Aký rozdiel je medzi filename a inode/device source identity?
3. Čo checkpoint DB umožňuje pri restart-e?
4. Prečo parser zmena neprepíše records už v bufferi?
5. Ako filter order ovplyvňuje redaction?
6. Čo internal metrics preukazujú a čo nie o backend queryability?
7. Prečo filesystem buffer nemožno počas incidentu naslepo zmazať?
8. Ako sa líši Loki HTTP acknowledgement od bulk per-item acknowledgement?
9. Prečo at-least-once retry môže vytvoriť duplicates?
10. Aký failure test uzatvára checkpoint recovery?

## Oficiálna dokumentácia

- [Fluent Bit manual](https://docs.fluentbit.io/manual/)
- [Tail input](https://docs.fluentbit.io/manual/pipeline/inputs/tail)
- [Buffering and storage](https://docs.fluentbit.io/manual/administration/buffering-and-storage)
- [Monitoring](https://docs.fluentbit.io/manual/administration/monitoring)
- [Configuration file](https://docs.fluentbit.io/manual/administration/configuring-fluent-bit)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Elasticsearch alebo OpenSearch](elasticsearch-opensearch.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Jaeger a Tempo →](jaeger-tempo.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
