# RED method

RED method je service-oriented monitoring metodika zameraná na tri signály každej request-driven služby: **Rate**, **Errors** a **Duration**. Je vhodná najmä pre HTTP/gRPC APIs, microservices, consumers a ďalšie systémy, v ktorých prichádza jednotka práce a očakáva sa výsledok.

RED nevysvetľuje celý interný stav systému. Poskytuje konzistentný prvý pohľad na user-facing alebo caller-facing správanie služby a vstupný bod pre ďalšiu diagnostiku cez traces, logs, USE metrics a dependency telemetry.

## 1. Mentálny model

```text
koľko práce prichádza?     → Rate
koľko práce zlyháva?       → Errors
ako dlho práca trvá?       → Duration
```

Pre každý critical operation definuj všetky tri signály s rovnakým operation scope-om a success semantics.

## 2. Rate

Rate vyjadruje počet operácií za čas.

Príklady:

- HTTP requests za sekundu,
- gRPC calls za sekundu,
- messages spracované za minútu,
- jobs dokončené za hodinu,
- database queries za sekundu.

Rate nie je iba load metric. Pomáha rozlíšiť:

- reálny traffic drop od telemetry failure,
- error spike pri stabilnom trafficu,
- latency nárast spôsobený demand burstom,
- neúspešný deployment, ktorý neprijíma requesty,
- retry storm zvyšujúci apparent traffic.

### Denominator contract

Musí byť jasné, čo sa počíta:

- prijaté requesty,
- dokončené requesty,
- attempts,
- logical operations,
- retries,
- batch items,
- messages alebo batches.

Ak jeden logical request vykoná tri retry attempts, rate na client, service a dependency vrstve bude odlišný.

## 3. Errors

Errors vyjadrujú počet alebo podiel operácií, ktoré nesplnili definovaný contract.

Error nemusí byť iba HTTP `5xx`.

Môže zahŕňať:

- explicitný application failure,
- timeout,
- cancellation,
- invalid response,
- business rejection podľa SLO contractu,
- dependency error,
- dropped message,
- retry exhaustion,
- partial batch failure,
- fallback alebo stale response, ak porušuje user expectation.

### Error rate

```text
error rate = failed operations / relevant total operations
```

Numerator a denominator musia používať rovnaký scope.

Chybný príklad:

```text
numerator   = failed payment attempts vrátane retries
denominator = unique checkout requests
```

Takáto hodnota môže presiahnuť 100 % alebo zavádzať.

### Expected oproti unexpected errors

Nie každá `4xx` odpoveď je service failure a nie každá `2xx` odpoveď je success.

Príklady:

- `404` pre neexistujúci public resource môže byť expected outcome,
- `401` po expired session môže byť expected,
- `200` s chybným business resultom môže byť failure,
- `202` prijaté do queue nemusí znamenať dokončenú operáciu,
- fallback response môže byť technically successful, ale degraded.

Error semantics musia vychádzať z contractu a user journey.

## 4. Duration

Duration je čas spracovania operácie.

Môže byť meraná:

- na clientovi,
- na edge/load balanceri,
- v service handleri,
- na dependency call-e,
- end-to-end cez celý workflow,
- ako queue wait + processing time.

Tieto boundaries nie sú rovnaké.

### Distribution namiesto average

Average latency môže maskovať tail.

Sleduj podľa use case-u:

- histogram distribution,
- p50,
- p90,
- p95,
- p99,
- max iba ako diagnostický doplnok,
- successful a failed latency oddelene.

Google SRE odporúča odlišovať latency úspešných a neúspešných requestov. Rýchla chyba nesmie zlepšovať celkovú latency metriku.

### Queue time

End-to-end duration môže obsahovať:

```text
queue wait
+ service processing
+ dependency wait
+ retry delays
+ response transfer
```

Service handler duration bez queue wait môže vyzerať zdravo, zatiaľ čo používateľ čaká sekundy.

## 5. Operation scope

RED metrics musia byť agregovateľné, ale nie natoľko broad, aby zmiešali neporovnateľné operácie.

Vhodné dimensions:

- service,
- operation alebo normalized route,
- method/protocol,
- result class,
- environment,
- bounded region/zone.

Rizikové dimensions:

- raw URL,
- user ID,
- request ID,
- exception message,
- tenant ID bez jasnej bounded policy.

Normalized route má byť napríklad `/orders/{id}`, nie `/orders/987654`.

## 6. RED pre HTTP service

Príklad metrics contractu:

```text
http_server_requests_total{
  service,
  method,
  route,
  status_class
}

http_server_request_duration_seconds{
  service,
  method,
  route,
  status_class
}
```

Queries musia počítať rate a error ratio z counterov a latency z histogramu/distribution.

Doplň:

- in-flight requests,
- request/response size,
- timeout/cancellation reason,
- retry count,
- dependency RED,
- trace exemplars alebo links.

## 7. RED pre gRPC

Error semantics majú vychádzať z gRPC status code-u, nie iba z transportného HTTP statusu.

Sleduj:

- method/service,
- unary oproti streaming,
- status code,
- messages sent/received,
- stream duration,
- cancellation a deadline exceeded.

Streaming call duration môže prirodzene trvať dlho. Potrebuje ďalšie metrics pre message rate, lag a stream health.

## 8. RED pre queues a consumers

Pri queue workload-e definuj jednotku práce.

Možnosti:

- message received rate,
- message successfully processed rate,
- processing error rate,
- processing duration,
- end-to-end message age,
- retry/dead-letter rate.

Samotná processing duration nestačí. Message môže stráviť hodiny v queue pred začiatkom spracovania.

Preto doplň:

- queue depth,
- oldest message age,
- consumer lag,
- concurrency,
- redelivery count.

## 9. RED pre batch jobs

Batch job nie je klasická online service.

Prispôsobenie:

- Rate — items alebo jobs dokončené za obdobie,
- Errors — failed items/jobs,
- Duration — job duration alebo item processing duration.

Doplň:

- last successful completion,
- freshness,
- expected schedule,
- backlog,
- partial success,
- checkpoint progress.

Pre batch systémy je freshness často dôležitejšia než request rate.

## 10. RED a retries

Retries môžu skresliť všetky tri signals:

- Rate rastie,
- Errors na attempt vrstve rastú,
- Duration logical operation rastie,
- dependency saturation sa zhoršuje.

Sleduj oddelene:

- logical operations,
- attempts,
- retry count,
- retry reason,
- success after retry,
- exhausted retries.

Dashboard, ktorý ukazuje iba final success, môže skryť prebiehajúcu dependency degradáciu.

## 11. RED a caching

Cache mení service path.

Rozlišuj:

- cache hit rate,
- miss rate,
- hit latency,
- miss latency,
- stale serve,
- origin error,
- cache fill error.

Celková latency môže vyzerať zdravo pri vysokom hit ratio, zatiaľ čo origin path je už nefunkčný.

## 12. RED a SLO

RED metrics sú často základom request-based SLIs.

Príklady:

### Availability SLI

```text
successful valid requests / all valid requests
```

### Latency SLI

```text
requests dokončené pod threshold / valid requests
```

SLO contract musí určiť:

- valid traffic,
- excluded synthetic/admin operations,
- success semantics,
- latency threshold,
- measurement point,
- window,
- treatment retries a partial failures.

RED dashboard nie je automaticky SLO. Potrebuje explicitný numerator a denominator contract.

## 13. Dashboard design

Odporúčané poradie:

1. total rate,
2. success/error ratio,
3. latency distribution a percentiles,
4. breakdown podľa operation/result,
5. deployment/version markers,
6. dependency RED,
7. traces alebo logs links.

Dashboard má umožniť prechod:

```text
service symptom
→ operation
→ version/zone/tenant class
→ dependency
→ trace
→ logs
```

Nevytváraj samostatný dashboard pre každú metric bez investigation workflowu.

## 14. Alerting

Alertuj na user-impact alebo SLO risk, nie iba na každú zmenu RED metrics.

Vhodné patterns:

- high error-rate burn,
- latency SLO burn,
- complete traffic loss pri očakávanom demand-e,
- abnormal traffic spike s downstream riskom,
- sustained zero successful completions,
- queue age prekračujúci business threshold.

Rate drop môže byť incident alebo normálna sezónnosť. Použi expected traffic, business calendar alebo multi-signal confirmation.

## 15. RED a Golden Signals

RED:

- Rate,
- Errors,
- Duration.

Golden Signals:

- Traffic,
- Errors,
- Latency,
- Saturation.

Mapovanie:

```text
Rate      ≈ Traffic
Errors    = Errors
Duration  ≈ Latency
Saturation nemá priamy RED ekvivalent
```

RED je service/request pohľad. Golden Signals pridávajú „ako blízko kapacitnej hranice sa systém nachádza“.

## 16. RED a USE

RED sleduje službu a prácu.

USE sleduje resources:

- Utilization,
- Saturation,
- Errors.

Incident workflow:

```text
RED ukáže user-facing symptom
→ trace/dependency RED lokalizuje component
→ USE ukáže resource bottleneck
→ logs/profile vysvetlia mechanizmus
```

## 17. Troubleshooting podľa RED

### Rate klesla, errors nerastú

Over:

- upstream traffic,
- DNS/load balancer routing,
- deployment registration,
- instrumentation/scrape,
- queue producer,
- business sezónnosť.

### Errors rastú, duration klesá

Možné:

- fast rejection,
- circuit breaker open,
- authentication failure,
- validation error,
- dependency unavailable pred reálnym spracovaním.

### Duration rastie, utilization je nízka

Možné:

- downstream latency,
- lock contention,
- queueing mimo sledovaného resource-u,
- connection pool exhaustion,
- DNS/TLS retries,
- rate limiting.

### Rate rastie, errors a duration zatiaľ stabilné

Over saturation headroom. RED môže byť zdravé tesne pred capacity cliffom.

## 18. Anti-patterny

### RED iba na service total

Jedna pomalá kritická operation sa stratí v aggregate.

### Status code ako jediná error definícia

Business failures a degraded responses zostanú skryté.

### Average duration

Tail latency a multimodal distribution sa stratia.

### Retry attempts zmiešané s logical operations

Rate a error ratio sú neinterpretovateľné.

### Raw path ako label

Vytvára vysokú cardinality.

### RED bez saturation

Služba môže vyzerať zdravo až do náhleho capacity collapse-u.

## 19. Kontrolné otázky

1. Čo znamenajú Rate, Errors a Duration?
2. Ako definuješ denominator pre error rate?
3. Prečo `2xx` nemusí znamenať business success?
4. Prečo oddeľovať successful a failed latency?
5. Ako retries skresľujú RED?
6. Ako prispôsobiť RED pre queue consumer?
7. Čo pridať pre batch job?
8. Ako súvisí RED so SLO?
9. Aký je rozdiel medzi RED a USE?
10. Prečo RED potrebuje saturation doplnok?

## Glossary impact

Relevantné pojmy: RED method, request rate, logical operation, attempt rate, error rate, success semantics, duration distribution, tail latency, normalized route, dependency RED, queue age, consumer lag a request-based SLI.

## Primárne zdroje

- [Grafana dashboard best practices — RED method](https://grafana.com/docs/grafana/latest/visualizations/dashboards/build-dashboards/best-practices/)
- [Grafana RED metrics concepts](https://grafana.com/docs/grafana/latest/visualizations/simplified-exploration/traces/concepts/)
- [Prometheus instrumentation practices](https://prometheus.io/docs/practices/instrumentation/)
- [Google SRE — Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/)
