# Loki

Grafana Loki je log aggregation systém založený na streamoch identifikovaných tenant ID a bounded label setom. Indexuje najmä stream metadata; log content ukladá komprimovaný v chunks. Tento model môže znížiť index cost, ale presúva veľkú časť correctness do label contractu, timestampu, collector delivery, schema periods, object-store lifecycle a query scope-u.

Loki nemôže nájsť log, ktorý nevznikol, collector ho neprečítal, distributor ho odmietol, ingester ho neflushol, object store ho predčasne zmazal alebo query vybrala nesprávny tenant či stream.

## 1. Dominantný model

```text
system alebo business occurrence
→ collector read a record generation
→ tenant, timestamp, bounded labels, metadata a body
→ distributor validation a limits
→ stream ownership a ingester acceptance
→ WAL/chunk generation a flush
→ TSDB index + chunk publication v object storage
→ recent alebo historical read path
→ LogQL selection, filtering a parsing
→ query/rule result
→ evidence-quality a retention verdict
→ operational decision a recovery validation
```

Loki availability nestačí. Potrebujeme preukázať celý occurrence-to-query path pre exact tenant, stream, schema a retention generation.

## 2. Exact Loki subject

Pre Atlas Payments používame `LOKI-PAY-45`:

```text
business capability: final payment settlement
service: provider-adapter
environment: production
region: eu-central-1
tenant: atlas-payments-prod
collector generation: FB-PAY-318
label-contract generation: LBL-PAY-27
schema period: TSDB/v13 generation
Loki deployment generation: LOKI-GEN-44
object-store bucket a prefixes
KMS/identity generation
retention generation: 30 days
object-store lifecycle generation
stream label set
structured metadata/body schema
time window a exact LogQL query
```

Názov služby a timestamp nestačia. Rovnaký log môže byť v inom tenantovi, stream generation, schema period alebo object-store prefixe.

## 3. Oddelené stavy

```text
application zapísala line
≠ collector ju prečítal
≠ Loki request ju prijal
≠ entry je durable v chunku
≠ index ju vie lokalizovať
≠ query ju vybrala
```

A rovnako:

```text
recent logs sú queryovateľné
≠ historical chunks existujú
≠ retention funguje
≠ object-store lifecycle je kompatibilný
```

Absencia query výsledku je evidence gap, kým sa neurčí konkrétna failure boundary.

## 4. Stream identity

Log stream je definovaný:

```text
tenant ID + úplný label set
```

Vhodné labels sú bounded a stabilné:

- service;
- environment;
- region/cluster;
- namespace;
- component;
- bounded severity alebo workload class.

Nevhodné labels:

- trace/request/user/order ID;
- full URL;
- exception message;
- timestamp;
- ephemeral container ID bez controlled lifecycle-u.

Každá nová label-value kombinácia vytvára nový stream. Stream explosion zvyšuje active streams, ingester memory, malé chunks, query fan-out a object-store operations.

## 5. Labels, structured metadata a body

### Labels

Indexované, používajú sa na prvotný stream selection.

### Structured metadata

Per-entry fields ako trace ID, request ID alebo Pod identity, ktoré nemajú vytvoriť nový stream. Stále zvyšujú payload a query cost, ale nemenia stream identity.

### Body

Structured JSON alebo stabilný text/logfmt record. Parser sa aplikuje až po stream selection.

```text
bounded labels zúžia dataset
→ line filter odstráni nezaujímavé entries
→ parser vytvorí query fields
→ field predicate vyberie outcome
```

Nesnaž sa emulovať document-search engine tým, že každý JSON field zmeníš na Loki label.

## 6. Write path

```text
collector batch
→ authenticated tenant gateway
→ distributor validation
→ rate/label/timestamp/line-size limits
→ ring ownership a replication
→ ingester recent state
→ chunk build
→ WAL/recovery state podľa konfigurácie
→ chunk a index flush do object storage
```

HTTP success pre batch nepreukazuje, že collector nikdy nedropoval staršie records. Naopak rejection musí byť klasifikovaná:

- retryable throttling alebo temporary backend failure;
- permanent invalid labels, timestamp alebo line size;
- tenant/auth failure;
- stream limit/cardinality failure.

Nekonečný retry permanentne invalidného batchu blokuje ďalšie logy.

## 7. Storage a schema generations

Loki ukladá:

- **index** — label sets, time ranges a odkazy na chunks;
- **chunks** — komprimované log entries streamu.

Pre nové deploymenty je TSDB index s aktuálnou odporúčanou schema generation dominantný model. Aktuálna dokumentácia odporúča `store: tsdb` a schema `v13`; staršie BoltDB-based a multi-store paths sú legacy alebo deprecated.

Schema config je časovo versionovaná:

```text
entries pred dátumom X → stará schema generation
entries od dátumu X    → nová schema generation
```

Historické period configs sa nemenia spätne bez explicitného migration a readability testu. Chybný `from` dátum alebo object-store mapping môže vytvoriť zdanlivo chýbajúce časové obdobie.

## 8. Deployment modes

### Single binary

Vhodný pre lokálny development, laby a malé prostredia. Všetky roles zdieľajú process failure domain.

### Distributed/microservices

Write, read a backend roles možno škálovať samostatne podľa konkrétnej verzie a architektúry.

Simple Scalable Deployment je v aktuálnej dokumentácii deprecated a má byť odstránený pred alebo s Loki 4.0. Nový production návrh preto musí overiť aktuálne odporúčaný deployment mode, Helm chart a component targets namiesto slepého kopírovania starého `read/write/backend` layoutu.

## 9. Read path

```text
LogQL query
→ tenant a time range
→ query frontend split/cache/limits
→ scheduler
→ queriers
→ recent data z ingesters
→ historical TSDB index a chunks z object storage
→ merge/deduplication
→ Grafana alebo API client
```

Recent a historical queries môžu zlyhať na odlišných boundaries. Recent logs závisia od live ingesters; historical logs od flushed chunks, index blocks, schema period, object-store permissions, compaction a retention.

## 10. LogQL contract

### Stream selector

```logql
{service="provider-adapter", environment="production", region="eu-central-1"}
```

### Line filter

```logql
{service="provider-adapter"} |= "settlement.failed"
```

### Structured parse

```logql
{service="provider-adapter", environment="production"}
| json
| event="payment.settlement.completed"
| outcome!="success"
```

### Log-derived metric

```logql
sum by (service) (
  rate({environment="production"} | json | outcome="failure" [5m])
)
```

Log-derived metric má source completeness, delay, sampling a parsing contract. Pre SLO denominator je native metric často autoritatívnejšia než log query.

`unwrap` a parser-based quantiles vyžadujú unit, missing-field a parse-error kontrolu. Sampled alebo dropped logs nesmú byť prezentované ako kompletná latency distribution.

## 11. Multi-tenancy a authorization

Tenant ID ovplyvňuje ingest, query, limits, retention, cache a storage scope. Header ako `X-Scope-OrgID` nie je security boundary, ak ho môže nedôveryhodný client ľubovoľne nastaviť.

Dôveryhodná gateway musí:

- autentizovať clienta;
- odvodiť alebo validovať tenant;
- obmedziť povolené tenant values;
- auditovať query a ingest identity;
- izolovať cache a storage scope.

Grafana folder permission sama osebe tenant isolation nevynucuje.

## 12. Retention, compaction a object-store lifecycle

Retention je coordinated lifecycle:

```text
retention policy
→ compactor/delete processing
→ index update
→ delayed chunk deletion
→ query behavior po retention boundary
```

Object-store lifecycle musí byť dlhší a kompatibilný s Loki retention modelom. Nemá nezávisle mazať index alebo chunks skôr, než Loki ukončí ich query lifecycle.

Sleduj:

- compaction a deletion backlog;
- object-store delete actors a failures;
- working disk;
- schema periods;
- per-tenant retention;
- versioning/backup/recovery;
- audit evidence pre compliance deletion.

Retention success nie je iba „bucket je menší“. Musí sa overiť, že allowed časové okno zostáva čitateľné a zakázané expirované obdobie už nie.

## 13. Collectors a end-to-end canary

Loki môže prijímať logs z Fluent Bit, Grafana Alloy, OpenTelemetry Collectora alebo ďalších clients.

Collector vlastní:

- source offset/inode;
- multiline reconstruction;
- parsing a redaction;
- tenant a label mapping;
- buffering a retry;
- timestamp;
- permanent-failure handling.

Loki nevie obnoviť line, ktorú collector nikdy neprečítal alebo zahodil.

Critical canary:

```text
emit bounded canary event
→ collector input counter
→ collector output acknowledgement
→ Loki accepted line
→ recent query
→ flushed historical query po definovanom čase
→ retention expiry podľa policy
```

Canary identifier patrí do body/metadata, nie do unbounded labelu.

## 14. Self-observability

Sleduj:

- accepted a rejected bytes/lines;
- rejection reason;
- active streams a chunk utilization;
- ingester memory/WAL/flush;
- ring health;
- object-store operations a errors;
- query queue, latency a bytes scanned;
- cache hit/eviction;
- compactor/retention backlog;
- ruler evaluation;
- tenant limit violations;
- end-to-end canary latency.

Process readiness nepreukazuje funkčnú storage ani query path.

## 15. Worked failure: 30-dňová retention, logy zmiznú po siedmich dňoch

### Symptóm

Po bezpečnostnom incidente potrebuje tím settlement logs staré 12 dní. Grafana a LogQL vracajú recent logs do siedmich dní, ale staršie obdobie je prázdne alebo obsahuje chunk-fetch errors. Loki configuration deklaruje 30-dňovú retention a Compactor je healthy, preto prvý verdict znie „logy nikdy neboli ingestované“.

### Exact subject

```text
subject: LOKI-PAY-45
tenant: atlas-payments-prod
stream: service=provider-adapter, environment=production
schema: TSDB/v13 period
retention generation: RET-30D-18
object-store lifecycle generation: S3-LC-7D-04
chunk prefix: loki/chunks/
index prefix: loki/index/
query window: incident -12d až -11d
```

### Competing hypotheses

1. collector vtedy nebežal alebo stratil offsets;
2. query používa nesprávny tenant, timezone alebo labels;
3. timestamp parser uložil entries mimo okna;
4. schema migration vytvorila nečitateľný period;
5. Compactor zmazal dáta podľa Loki retention;
6. object-store lifecycle zmazal chunks predčasne;
7. KMS alebo bucket permissions blokujú historical read;
8. query cache vracia stale empty result.

### Discriminating evidence

```text
recent ingest a query: healthy
historický TSDB index period: existuje
index references: obsahujú očakávané stream/chunk ranges
chunk GET: object-not-found pre >7d objects
Compactor retention: 30d, bez delete action pre affected range
object-store audit: lifecycle expiration actor
bucket rule: chunks prefix expire after 7d
index prefix: 30d
```

Mechanizmus:

```text
Loki publikuje index a chunks
→ queryable retention očakáva 30 dní
→ nezávislá bucket lifecycle rule maže chunks po 7 dňoch
→ index ešte odkazuje na neexistujúce objects
→ recent path zostáva healthy
→ historical query zlyhá alebo vráti incomplete evidence
→ declared retention je false
```

### Containment

- zastaviť alebo opraviť destructive object-store lifecycle rule;
- zachovať bucket configuration, audit logs, index blocks a missing-object manifest;
- označiť affected obdobie ako incomplete evidence;
- nevymazávať index blocks ani „resetovať“ schema;
- chrániť audit/security logs samostatnou retention boundary.

### Authoritative recovery

1. zistiť, či object versioning, replication alebo backup zachoval deleted chunks;
2. obnoviť presné object versions do očakávaných keys/prefixu;
3. ak obnova nie je možná, explicitne uzavrieť obdobie ako unrecoverable evidence loss — nie predstierať, že query fix dáta vráti;
4. zosúladiť bucket lifecycle s Loki Compactor retention a delete delay;
5. overiť index/chunk readability na canary time slices;
6. pridať synthetic aged-log canary a object-existence audit;
7. testovať retention transition aj pri ďalšom schema period-e.

### Loki acceptance verdict

Recovery alebo corrected control je prijatý, keď:

- log starý 8, 15 a 29 dní je queryovateľný podľa policy;
- recent aj historical path vracajú rovnaký canary event;
- object lifecycle nemaže allowed chunks ani index;
- po 30-dňovej hranici expirovaný canary nie je queryovateľný;
- tenant isolation a KMS permissions zostávajú správne;
- object-store audit neukazuje forbidden early deletes;
- druhý Compactor cycle a schema lookup zachovajú výsledok.

## 16. Troubleshooting model

### Chýbajúce logy

```text
occurrence vznikol?
→ source file/socket?
→ collector offset/parser/filter?
→ tenant/labels/timestamp?
→ distributor response a limits?
→ ingester/WAL/chunk flush?
→ schema/object store?
→ query tenant/selector/timezone?
```

### Recent áno, historical nie

```text
chunk flush
→ TSDB index period
→ object existence a KMS
→ compactor
→ retention
→ object-store lifecycle
→ historical query path/cache
```

### Historical áno, recent nie

```text
collector current ingest
→ distributor/limits
→ ring/ingester ownership
→ recent-data query path
→ clock skew
```

### Pomalý query

```text
tenant/time range
→ stream-selector cardinality
→ parser/regex/unwrap
→ bytes scanned a splitting
→ scheduler/queriers
→ object-store/cache
```

## 17. Anti-patterny

### Request ID ako label

Vytvorí prakticky stream per request.

### Broad 30-dňový selector bez bounded service labels

Zvyšuje stream a chunk fan-out.

### Object-store lifecycle mimo Loki retention authority

Môže zničiť allowed evidence.

### Recent query ako retention test

Neoverí flush, historical index ani object-store path.

### Collector success ako completeness proof

Collector mohol pred exportom dropovať alebo parsovať nesprávne.

### Audit logs v rovnakom tenant/access boundary

Compromise application observability môže poškodiť aj security evidence.

## 18. Kontrolné otázky

1. Čo tvorí exact Loki subject?
2. Ako tenant a label set definujú stream?
3. Prečo trace ID patrí skôr do structured metadata než labels?
4. Aký je rozdiel medzi indexom a chunkom?
5. Ako sa líši recent a historical read path?
6. Prečo je TSDB/v13 aktuálny odporúčaný storage model?
7. Ako schema periods umožňujú doprednú migration?
8. Prečo Simple Scalable Deployment nemožno považovať za nový default?
9. Ako object-store lifecycle môže porušiť Loki retention?
10. Prečo log-derived metric nemusí byť SLO autorita?
11. Ako diagnostikuješ missing logs bez zamieňania no-data za neprítomnosť occurrence-u?
12. Ako overíš retention end-to-end?

## Glossary impact

Relevantné pojmy: Loki subject, log-stream identity, label-contract generation, structured-metadata boundary, Loki entry acceptance, chunk generation, TSDB schema period, recent-log path, historical-log path, Loki retention generation, object-store lifecycle mismatch, aged-log canary, Loki evidence-completeness verdict a Loki acceptance verdict.

## Primárne zdroje

- [Loki architecture](https://grafana.com/docs/loki/latest/get-started/architecture/)
- [Loki deployment modes](https://grafana.com/docs/loki/latest/get-started/deployment-modes/)
- [Loki storage](https://grafana.com/docs/loki/latest/configure/storage/)
- [Loki storage schema](https://grafana.com/docs/loki/latest/operations/storage/schema/)
- [Loki TSDB](https://grafana.com/docs/loki/latest/operations/storage/tsdb/)
- [LogQL](https://grafana.com/docs/loki/latest/query/)
- [Loki retention](https://grafana.com/docs/loki/latest/operations/storage/retention/)
- [Loki limits](https://grafana.com/docs/loki/latest/operations/request-validation-rate-limits/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Grafana](grafana.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Elasticsearch alebo OpenSearch →](elasticsearch-opensearch.md)
<!-- KNOWLEDGE-NAVIGATION:END -->