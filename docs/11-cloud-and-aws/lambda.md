# Lambda

AWS Lambda poskytuje event-driven compute bez potreby spravovať server fleet. Zákazník dodáva function code alebo container image, runtime configuration, permissions a event integration; AWS spravuje provisioning execution environments, placement, host lifecycle a základné škálovanie. Serverless však neznamená bezstavové bez premýšľania, bez limitov ani bez prevádzkovej zodpovednosti.

## 1. Mentálny model

```text
event source alebo synchronous caller
→ invocation contract
→ Lambda service admission a concurrency
→ execution environment
→ function handler
→ downstream dependencies
→ result, retry, destination alebo failure path
```

Rozlišuj:

- **function** — versionovaný code a runtime contract,
- **execution environment** — izolované runtime prostredie pre jeden alebo viac sequential invocations,
- **invocation** — jedno spracovanie eventu,
- **event source mapping** — poller pre podporované queue a stream zdroje,
- **trigger** — konfigurácia spájajúca event producer s funkciou,
- **concurrency** — počet súčasne spracovávaných invocations,
- **version a alias** — immutable deployment revision a pomenovaný traffic pointer.

## 2. Execution environment lifecycle

Štandardná Lambda execution environment používa fázy:

```text
Init → Invoke → freeze/reuse → Invoke ... → Shutdown
```

Počas `Init` sa spúšťa runtime, extensions a static initialization mimo handlera. Pri ďalšom invocation môže AWS rovnaké prostredie znovu použiť. To zlepšuje latency, ale nie je to garancia.

Dôsledky:

- globálne clients a SDK connections možno reuse-nuť,
- `/tmp` môže prežiť warm reuse, ale nie je durable storage contract,
- memory state medzi invocations nesmie byť authoritative,
- cleanup v shutdown fáze nemusí byť vhodný ako jediná delivery záruka,
- code musí fungovať aj pri úplne novom prostredí.

Aktuálna dokumentácia Lambda rozlišuje aj Durable Functions s dlhším workflow lifecycle a checkpointingom. Pri návrhu vždy over, či ide o štandardnú funkciu alebo durable execution model; ich time, state a retry semantics nie sú totožné.

## 3. Cold start a warm start

**Cold start** zahŕňa vytvorenie execution environmentu a initialization. Latency ovplyvňuje:

- runtime,
- package alebo image size,
- počet layers/extensions,
- static initialization,
- VPC/network initialization a dependency access,
- memory/CPU allocation,
- secret/config fetch,
- container image pull/cache,
- provisioned concurrency konfigurácia.

**Warm start** reuse-ne už inicializované prostredie, ale aplikácia naň nesmie spoliehať.

Optimalizácie:

- presuň reusable clients mimo handler,
- minimalizuj dependency graph,
- lazy-loaduj nepoužívané moduly,
- cache-uj secrets s bezpečným TTL,
- nepoužívaj blocking initialization bez timeoutu,
- meraj `Init Duration`, nie iba celkové duration.

## 4. Function packaging

Lambda podporuje:

- ZIP deployment package,
- container image v Amazon ECR podľa podporovaného Lambda image contractu,
- layers pre shared dependencies.

Container image nemení Lambda na ECS. Stále platí Lambda invocation, concurrency, timeout, filesystem a execution-environment model.

Package pipeline má zachovať:

- source revision,
- dependency lock,
- build platform a architecture,
- vulnerability scan,
- artifact digest,
- function version,
- deployment alias,
- rollback target.

## 5. Runtime, memory a CPU

Memory configuration ovplyvňuje dostupnú memory aj pridelený CPU výkon. Vyššia memory môže skrátiť duration natoľko, že celkový cost klesne.

Sleduj:

- duration distribution, nie iba average,
- memory high-water mark,
- CPU-bound oproti I/O-bound behavior,
- downstream latency,
- timeout margin,
- initialization duration,
- architecture kompatibilitu `x86_64` a `arm64`.

Lambda nie je vhodná pre workload, ktorý potrebuje neobmedzený runtime, stabilný host identity, privileged host access alebo dlhodobo otvorené local resources bez externalizácie.

## 6. Invocation modely

### Synchronous invocation

Caller čaká na response. Príklady:

- API Gateway,
- Application Load Balancer,
- priamy SDK/API call.

Caller alebo upstream service typicky vlastní retry policy. Function error sa musí mapovať na správny application response.

### Asynchronous invocation

Event je prijatý Lambda service a spracovaný neskôr. Lambda má vlastné retry a failure handling semantics podľa konfigurácie.

Možnosti:

- maximum event age,
- retry attempts,
- on-success destination,
- on-failure destination,
- dead-letter queue pri podporovanom modeli.

### Poll-based event source mapping

Lambda pollery čítajú batches zo zdrojov ako SQS alebo streams a volajú funkciu.

Konfigurácia môže zahŕňať:

- batch size,
- batching window,
- concurrency,
- starting position,
- partial batch response,
- bisect batch pri streamoch,
- failure destination podľa zdroja,
- filtering.

Nie všetky retry semantics patria Lambda. Pri SQS napríklad rozhoduje aj visibility timeout a queue redrive policy.

## 7. Event source mapping a idempotencia

Event-driven delivery je typicky **at-least-once**. Duplicitné processing je očakávateľná situácia, nie iba edge case.

Idempotency model:

```text
stable event/business key
→ conditional write alebo deduplication record
→ side effect
→ durable completion marker
```

Rizikové side effects:

- dvojité platby,
- duplicitné emaily,
- opakované provisioning actions,
- non-idempotent database updates,
- viacnásobný downstream publish.

Deduplication retention musí pokrývať retry a replay window. Samotný request ID Lambda nemusí byť business idempotency key.

## 8. Concurrency

Concurrency predstavuje počet paralelných invocations.

Rozlišuj:

- **account regional concurrency pool**,
- **reserved concurrency** — rezervuje a zároveň limituje concurrency funkcie,
- **provisioned concurrency** — predinicializované environments pre nižšiu startup latency,
- **event-source concurrency controls**,
- **downstream capacity**.

Reserved concurrency na nule funkciu administratívne zastaví. Príliš vysoká concurrency môže preťažiť database, API alebo NAT path.

Capacity model musí sledovať celý chain:

```text
incoming rate × average duration
→ function concurrency
→ connections/requests na dependency
→ dependency queue, quota a saturation
```

## 9. Throttling

Throttling môže vzniknúť pre:

- exhausted account concurrency,
- reserved concurrency limit,
- event source maximum concurrency,
- burst/ramp behavior,
- downstream service quota nepriamo cez retry storm.

Evidence:

- `Throttles`, `ConcurrentExecutions`, `ProvisionedConcurrencySpilloverInvocations`,
- upstream errors,
- event age alebo queue depth,
- account/service quotas,
- per-function reserved/provisioned settings.

Zvýšenie concurrency bez ochrany downstreamu môže incident zhoršiť.

## 10. Versions a aliases

Published function version je immutable snapshot podporovaných function properties. Alias smeruje na version a môže podporovať weighted traffic medzi dvoma versions.

Použitie:

- dev/stage/prod alias,
- canary deployment,
- stabilný event-source target,
- rýchly rollback pointera,
- provisioned concurrency per alias/version.

`$LATEST` je mutable a nie je vhodný ako production release identity bez explicitného procesu.

## 11. Deployment safety

Bezpečný workflow:

1. vytvor immutable artifact,
2. deploy-ni novú version,
3. vykonaj configuration a permission validation,
4. presuň malé percento trafficu cez alias,
5. sleduj error rate, duration, throttles a business SLI,
6. pokračuj alebo vráť alias,
7. zachovaj logs a deployment metadata.

Code rollback nevracia external side effects, schema alebo event replay state.

## 12. Environment variables a configuration

Environment variables sú vhodné pre non-secret runtime configuration. Pri encryption možno použiť KMS-integrated protection, ale plaintext hodnoty sú function configuration dostupná oprávneným principals a runtime procesu.

Secrets patria typicky do:

- AWS Secrets Manager,
- Systems Manager Parameter Store podľa contractu,
- short-lived credentials cez execution role.

Configuration change môže spôsobiť vytvorenie nových execution environments. Aplikácia musí zvládať mixed population počas propagation.

## 13. Execution role a resource policies

**Execution role** určuje, čo function code môže robiť.

**Resource-based policy funkcie** určuje, kto alebo ktorá služba môže funkciu invoke-nuť.

Bežné chyby:

- trigger má event konfiguráciu, ale chýba invoke permission,
- execution role nevie čítať Secret/KMS key,
- broad wildcard permissions,
- source ARN/account condition chýba,
- cross-account caller nemá obe potrebné policy strany,
- VPC endpoint policy zúži prístup.

## 14. VPC connectivity

Funkcia môže byť pripojená k customer VPC pre access k private resources. Dôležité hranice:

- vyberá subnets a Security Groups,
- potrebuje dostupné subnet IP addresses,
- internet access nevznikne iba výberom public subnetu,
- private internet egress potrebuje route cez NAT alebo vhodný endpoint,
- AWS service access možno riešiť VPC endpoints,
- DNS, NACL a return path stále platia.

Pri timeout-e na dependency over:

```text
function SG egress
→ subnet route/NACL
→ NAT alebo endpoint
→ destination SG/policy
→ DNS
→ listener a application
```

## 15. Networking a database connections

Serverless scale môže vytvoriť connection storm.

Mitigácie:

- reuse connection v warm environment,
- connection pooling/proxy,
- reserved concurrency,
- batch processing,
- backpressure cez queue,
- timeout a circuit breaker,
- RDS Proxy pri vhodnom database modeli.

Počet execution environments nie je totožný s bezpečným počtom database connections.

## 16. Timeout, retry a cancellation

Function timeout musí byť kratší než upstream timeout a ponechať priestor na graceful error handling.

Dlhý timeout môže:

- zvýšiť concurrency,
- predĺžiť retry feedback loop,
- držať connections,
- zvýšiť cost,
- maskovať pomalú dependency.

SDK retries potrebujú celkový retry budget. Lambda platform retry plus SDK retry plus downstream retry môže vytvoriť násobný request storm.

## 17. Destinations, DLQ a replay

Failure path musí byť pozorovateľný a reprocessovateľný.

Zachovaj:

- original event,
- failure reason,
- function version/alias,
- attempt metadata,
- correlation ID,
- business idempotency key,
- replay authorization a rate limit.

DLQ bez alarmu, ownershipu a replay runbooku je iba odkladanie incidentu.

## 18. Observability

Minimum:

- structured logs,
- `Errors`, `Duration`, `Throttles`, `Invocations`, `ConcurrentExecutions`,
- iterator age alebo queue age pri event sources,
- async delivery failures,
- provisioned concurrency utilization/spillover,
- traces podľa potreby,
- business success metric,
- deployment/version metadata.

CloudWatch Logs group retention nastav explicitne. Infinite retention pre high-volume debug logs zvyšuje cost a data exposure.

## 19. Logging hygiene

Neloggovať:

- credentials,
- access tokens,
- celé secrets,
- citlivé event payloads,
- unredacted authorization headers.

Použi sampling, masking a field-level classification. Lambda event často pochádza z inej služby a môže obsahovať viac citlivých dát, než handler potrebuje.

## 20. Durable state

Authoritative state ukladaj mimo execution environment:

- DynamoDB,
- RDS/Aurora,
- S3,
- queues/streams,
- workflow service,
- external system s definovanou consistency.

`/tmp`, global variable ani reuse-nutá connection nie sú durable state.

## 21. Error classes

Rozlišuj:

- **function error** — handler exception alebo explicitný failure,
- **platform/runtime error** — init, runtime, extension alebo environment failure,
- **throttle** — invocation nebola prijatá na vykonanie,
- **timeout** — handler nedokončil v limite,
- **dependency failure** — downstream timeout/deny/5xx,
- **delivery failure** — event sa nedostal alebo nebol potvrdený podľa source semantics.

## 22. Troubleshooting

### Function timeout

Over:

- REPORT duration a timeout,
- init duration,
- downstream latency,
- DNS/VPC path,
- SDK retry count,
- memory/CPU allocation,
- connection pool,
- cold oproti warm behavior.

### `AccessDenied`

Over execution role, resource policy, KMS key policy, Secret policy, VPC endpoint policy a skutočný caller ARN.

### SQS messages sa opakujú

Over visibility timeout, function duration, batch failure model, partial batch response, DLQ redrive a idempotenciu.

### DynamoDB/Kinesis iterator age rastie

Over errors, throttles, shard parallelism, batch size, reserved concurrency a downstream latency.

### Function sa nespúšťa

Over trigger state, event filters, invoke permission, source policy, disabled event source mapping a CloudTrail configuration changes.

### Náhly nárast costu

Over invocation rate, recursive/event loop, retries, duration, logs ingest, provisioned concurrency a downstream calls.

## 23. SOA-C03 mapovanie

- **Domain 1** — metrics, logs, alarms, concurrency, duration, error a remediation.
- **Domain 2** — async retry, DLQ, idempotencia, multi-AZ managed service behavior a recovery.
- **Domain 3** — versions, aliases, deployment, event sources, IaC a automation.
- **Domain 4** — execution role, resource policy, KMS, secrets, code/package security.
- **Domain 5** — VPC attachment, private endpoints, NAT, DNS a dependency connectivity.

Praktické drilly:

- reserved concurrency spôsobí throttling,
- SQS visibility timeout je kratší než function runtime,
- function SG nevie dosiahnuť RDS,
- secret rotation zmení credentials bez client refreshu,
- alias smeruje na chybnú version,
- recursive event loop generuje cost spike,
- event-source filter blokuje validné events.

## 24. Anti-patterny

### Lambda je automaticky lacnejšia

Pri vysokej steady load, dlhej duration alebo veľkom provisioned-concurrency poole môže byť iný compute model efektívnejší.

### Bez reserved concurrency na rizikovom consumerovi

Jedna funkcia môže vyčerpať regional pool alebo downstream capacity.

### DLQ bez alarmu a replay procesu

Failure sa iba presunie mimo hlavného dashboardu.

### Secret načítaný pri každom invocation bez cache

Zvyšuje latency, API cost a KMS load.

### Všetky chyby riešené retryom

Permanentný validation alebo authorization error sa retryom neopraví.

### Stateful business logika v `/tmp`

Replacement execution environmentu stratí state.

### Production traffic na `$LATEST`

Chýba immutable release identity a kontrolovaný rollback.

## 25. Kontrolné otázky

1. Aký je rozdiel medzi function, invocation a execution environment?
2. Prečo warm environment nie je durable contract?
3. Ako sa líši synchronous, asynchronous a event-source-mapping invocation?
4. Čo reserved concurrency robí?
5. Prečo môže Lambda preťažiť RDS aj keď sama škáluje správne?
6. Ako navrhneš idempotentný SQS consumer?
7. Aký je rozdiel medzi execution role a function resource policy?
8. Ktoré vrstvy overíš pri VPC timeout-e?
9. Ako fungujú versions a aliases pri canary deployment-e?
10. Čo potrebuje bezpečný DLQ replay?

## Glossary impact

Relevantné pojmy: AWS Lambda, execution environment, cold start, warm start, invocation, event source mapping, reserved concurrency, provisioned concurrency, function version, Lambda alias, asynchronous destination, dead-letter queue, partial batch response, iterator age, execution role, Lambda resource policy a durable function.

## Oficiálna dokumentácia

- [AWS Lambda Developer Guide](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)
- [Execution environment lifecycle](https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtime-environment.html)
- [Event source mappings](https://docs.aws.amazon.com/lambda/latest/dg/invocation-eventsourcemapping.html)
- [Lambda concurrency](https://docs.aws.amazon.com/lambda/latest/dg/lambda-concurrency.html)
- [Lambda retry behavior](https://docs.aws.amazon.com/lambda/latest/dg/invocation-retries.html)
- [Lambda VPC networking](https://docs.aws.amazon.com/lambda/latest/dg/configuration-vpc.html)
