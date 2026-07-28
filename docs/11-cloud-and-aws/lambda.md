# AWS Lambda

AWS Lambda poskytuje event-driven compute bez správy host fleet-u, ale nezrušuje prevádzkovú zodpovednosť. AWS vlastní provisioning hostov, placement execution environments a platform scaling. Zákazník vlastní event contract, release identity, concurrency budget, downstream capacity, idempotenciu, retry a replay pravidlá, secrets, sieť, business state a dôkaz, že jedna prijatá udalosť vytvorila práve povolený výsledok.

Dominantný lifecycle:

```text
business request alebo event
→ exact source a delivery generation
→ invocation admission a concurrency verdict
→ execution-environment generation
→ initialization a handler execution
→ downstream transaction/side effects
→ acknowledgement alebo nejednoznačný outcome
→ retry, backlog, destination alebo replay
→ business reconciliation
→ release acceptance a retirement starej generation
```

Lambda sa preto neposudzuje podľa otázky „beží funkcia?“. Posudzuje sa podľa toho, či exact event prešiel správnou source, version, identity a capacity cestou a či retry alebo failover nevytvoril duplicitný alebo stratený business účinok.

## 1. Exact serverless execution subject

Atlas Payments používa subject `SVL-PAY-42`:

```text
account = 100000000042
Region = eu-central-1
function = payments-settle
function ARN = arn:aws:lambda:eu-central-1:100000000042:function:payments-settle
artifact digest = sha256:lambda-pay-7-16-0
published version = 84
production alias = live
alias generation = ALIAS-PAY-31
execution role generation = ROLE-LAMBDA-PAY-18
resource policy generation = RP-LAMBDA-PAY-7

source = SQS queue payments-settlement
queue ARN generation = QUEUE-PAY-22
event source mapping UUID = esm-pay-44
mapping generation = ESM-PAY-12
batch size = 10
partial batch response = enabled
visibility timeout = 180 s
maximum source concurrency = 40

reserved concurrency = 50
provisioned concurrency on alias live = 8
memory = 1 024 MB
timeout = 90 s
VPC configuration generation = VPC-LAMBDA-14
secret generation = SEC-PAY-37
database/proxy generation = PROXY-10

event = settlement S-884
business idempotency key = settle-S884
correlation ID = corr-884

required outcome =
  provider settlement, ledger transition and outbox publication exactly once

forbidden outcomes =
  duplicate provider settlement after retry
  message deletion before durable business completion
  whole-batch replay duplicates already successful records
  concurrency increase exhausts database connections
  alias rollback is declared complete while old events still execute version 84
  warm environment memory or /tmp is treated as authoritative state
```

Incident evidence musí viazať event source record ID, mapping UUID a configuration, function version/alias, request ID, execution-environment initialization, attempt number, concurrency state, downstream idempotency key, transaction outcome, queue acknowledgement a final ledger/provider result.

## 2. Function, invocation a execution environment nie sú to isté

**Function** je configuration a code identity. **Published version** je immutable release snapshot podporovaných properties. **Alias** je pomenovaný pointer na version a môže riadiť weighted exposure. **Invocation** je jedno prijatie payloadu na spracovanie. **Execution environment** je izolované runtime prostredie, ktoré Lambda môže použiť pre viac sequential invocations.

Štandardný environment lifecycle:

```text
create environment
→ Init runtime, extensions a static code
→ Invoke handler
→ freeze
→ možný warm reuse
→ ďalší Invoke
→ Shutdown alebo replacement
```

Warm reuse umožňuje znovu použiť SDK client, connection alebo lokálny cache. Nie je to durability contract. AWS môže environment kedykoľvek nahradiť; `/tmp`, global variable ani in-memory deduplication preto nesmú rozhodovať o business pravde.

Cold-start latency vzniká pred handlerom. Zahŕňa platform provisioning, runtime a extension initialization, static imports, configuration/secrets fetch, network setup a application initialization. Meranie iba handler duration môže skryť skutočný startup problém.

## 3. Invocation contract určuje vlastníka retryu

### Synchronous invocation

Caller čaká na response. Platforma vráti function error alebo response callerovi a retry typicky vlastní caller, SDK alebo upstream service.

```text
caller request
→ Lambda admission
→ handler
→ response alebo error
→ caller rozhodne retry/abort/reconcile
```

Upstream timeout musí byť dlhší než function timeout plus transport budget. Inak môže caller retryovať, kým prvá invocation stále dokončuje side effect.

### Asynchronous invocation

Lambda prijme event do service-managed queue a handler spustí neskôr. Platforma riadi retry a event-age policy; on-success/on-failure destination alebo podporovaný DLQ zachytáva výsledok podľa configuration.

Prijatie eventu neznamená business completion. Treba oddeliť:

```text
producer acknowledgement
≠ function success
≠ downstream commit
≠ destination delivery
≠ business reconciliation
```

### Poll-based event source mapping

Pri SQS, Kinesis, DynamoDB Streams, Kafka a ďalších podporovaných sources pollery vytvárajú batches a synchronous invoke voči funkcii. Source semantics, event source mapping a function spolu určujú batching, checkpoint, retry, ordering a backlog.

Nie je správne hovoriť „Lambda retryuje všetko rovnako“. SQS visibility timeout, stream checkpoint, batch splitting, partial batch response a source retention vytvárajú odlišné failure boundaries.

## 4. Delivery je typicky at-least-once

Event-driven systém musí očakávať duplicate delivery. Duplicitná invocation môže vzniknúť pri function error-e, timeout-e, strate acknowledgementu, retryi source, replayi operátora alebo race počas recovery.

Business idempotency lifecycle:

```text
stable business key
→ atomic claim alebo unique constraint
→ authoritative current-state read
→ side effect s provider idempotency key
→ database/outbox commit
→ durable completion marker
→ acknowledgement source-u
```

Lambda request ID nie je stabilný business key: nový attempt môže mať nový request ID. Deduplication retention musí pokryť source retry, event retention, manuálny replay a DR replay window.

Idempotencia sa nesmie zastaviť pri jednom database insert-e. Ak operation volá payment provider a následne zapisuje ledger, rovnaký key a reconciliation contract musí pokryť obe strany.

## 5. Batch je samostatná acknowledgement boundary

Event source mapping môže jednej invocation odovzdať viac records. Pri whole-batch failure sa môžu znovu doručiť aj records, ktoré handler už úspešne spracoval.

```text
batch [A, B, C]
→ A success
→ B permanent validation failure
→ C success
→ handler vráti whole-batch failure
→ source retry [A, B, C]
```

Partial batch response dovolí označiť konkrétne failed records. Neodstraňuje idempotenciu, pretože timeout alebo platform failure môže nastať pred vrátením partial response.

Pri ordered streams treba navyše chrániť ordering a checkpoint semantics. „Preskočiť chybný record“ môže porušiť business sequence aj keď zníži iterator age.

## 6. Concurrency je admission control aj blast-radius control

Približný concurrency dopyt:

```text
arrival rate × average processing duration
≈ required concurrent invocations
```

Tento odhad sa musí previazať s downstreamom:

```text
Lambda concurrency
→ počet active DB/proxy connections
→ provider request rate
→ NAT/endpoint ports
→ queue visibility a retry pressure
```

**Reserved concurrency** rezervuje časť regional poolu pre funkciu a zároveň ju limituje. Hodnota nula funkciu administratívne zastaví. **Provisioned concurrency** pripravuje environments pre konkrétnu version/alias a znižuje startup latency; nie je downstream rate limit. Event-source maximum concurrency obmedzuje poller-side parallelism.

Zvýšenie limitu z 50 na 500 môže odstrániť `Throttles`, ale zničiť RDS connection budget a vytvoriť dlhší incident. Správny limit je najvyššia concurrency, ktorú celý dependency chain bezpečne absorbuje.

## 7. Backpressure sa má prejaviť v source, nie v poškodenom downstream-e

Queue alebo stream môže absorbovať dočasný burst. Bezpečný systém sleduje queue depth, age of oldest message alebo iterator age a má definované:

- maximum tolerované oneskorenie;
- concurrency ramp;
- retry budget;
- downstream quota;
- event expiration;
- DLQ/failure destination;
- controlled replay rate.

Backlog je často lepší než nekontrolovaný concurrency spike. Ak však event age prekročí business deadline, „event sa neskôr spracoval“ už nemusí byť správny výsledok.

## 8. Timeout je execution boundary, nie cancellation garancia downstreamu

Po Lambda timeout-e handler prestane pokračovať, ale external request mohol byť prijatý alebo commitnutý. To vytvára unknown outcome.

```text
handler pošle provider request
→ provider commitne settlement
→ network response mešká
→ Lambda timeout
→ source retry
```

Pred retryom treba query/reconcile provider a ledger podľa idempotency key. Retry budget musí pokrývať platform retry, SDK retry aj application retry; ich násobenie vytvára retry storm.

Function timeout má byť kratší než source visibility alebo upstream deadline s dostatočnou rezervou na acknowledgement. Dlhší timeout nie je automatická oprava pomalej dependency: zvyšuje concurrent execution time, cost a počet držaných resources.

## 9. Deployment je zmena viacerých generations

Bezpečný release subject obsahuje:

```text
source revision
→ locked dependency graph
→ reproducible ZIP alebo image digest
→ runtime/architecture
→ function configuration
→ execution role a resource policy
→ published version
→ alias traffic generation
→ event-source mapping target
→ observability a rollback target
```

`$LATEST` je mutable a nepredstavuje stabilnú production identity. Alias umožní canary alebo rýchly pointer rollback, ale rollback code-u nevracia už vykonané provider calls, queue checkpoints ani schema changes.

Weighted alias routing je probabilistic exposure. Pri asynchronous/poll sources treba overiť, či konkrétna integration invoke-uje alias/version podľa intended contractu; samotná alias weight nehovorí, ktorá verzia spracovala konkrétny event. Logs a business evidence musia niesť executed version.

## 10. Configuration propagation vytvára mixed population

Zmena environment variables, runtime config, layers, extensions, VPC alebo secret-fetch logic môže vytvoriť nové environments, zatiaľ čo staré ešte dokončujú invocations.

Application preto musí tolerovať:

- dve compatible configuration generations;
- rotáciu credentials počas existujúcich connections;
- old a new code pri queue backlogu;
- schema/event compatibility;
- postupné environment replacement.

Configuration value sa má logovať ako bezpečný generation identifier, nie ako secret.

## 11. Identity má dve hlavné strany

**Execution role** určuje, čo handler a podporované platform operations môžu robiť. **Function resource-based policy** určuje, kto alebo ktorá AWS služba môže function invoke-nuť.

Diagnostický chain pre `AccessDenied`:

```text
actual caller alebo execution-role session
→ identity policy
→ permissions boundary/SCP/session policy
→ function alebo downstream resource policy
→ KMS key policy/grant
→ VPC endpoint policy
→ exact resource ARN a condition context
```

Trigger configuration bez invoke permission nemusí fungovať. Broad execution role zase nevyrieši chýbajúcu function resource policy.

## 12. VPC attachment mení dependency path

Lambda pripojená k customer VPC používa selected subnets a Security Groups na prístup k private resources. Public subnet sám nevytvorí internet access; egress vyžaduje routu cez NAT alebo vhodný VPC endpoint.

```text
execution environment ENI path
→ subnet IP capacity
→ source SG
→ route/NACL
→ NAT alebo interface/gateway endpoint
→ endpoint/resource policy
→ destination SG/listener
→ application
```

Subnet IP exhaustion môže blokovať scale-out. NAT alebo endpoint capacity, DNS a TLS zostávajú samostatnými gates. Pri RDS treba navyše riadiť connection count, nie iba packet reachability.

## 13. Secrets a external configuration

Secrets patria do Secrets Manager alebo vhodného SecureString modelu, nie do source code-u ani plaintext logs. Fetch pri každej invocation zvyšuje latency, API cost a KMS load. Nekonečný cache zase predlžuje exposure starej alebo revoked credential generation.

Bezpečný cache contract definuje TTL, refresh pri authentication failure, fallback, rotation overlap a redaction. Execution environment môže secret cache reuse-nuť, ale authoritative current version zostáva external store a consumer refresh policy.

## 14. Failure destinations a replay sú prevádzkový systém

DLQ alebo on-failure destination je iba storage boundary. Bez ownera, alarmu, retention, classification a replay runbooku sa incident len presunie mimo hlavnej queue.

Replay manifest má obsahovať:

```text
source event identity a checksum
original source/mapping generation
failed function version
attempt history a failure class
business idempotency key
current authoritative business state
approved replay version
rate/concurrency limit
start/stop criteria
post-replay reconciliation
```

Permanent validation alebo authorization failure sa replayom bez opravy nezmení. Replay do novej version môže mať iné semantics; compatibility musí byť explicitná.

## 15. Durable Functions sú odlišný execution contract

Aktuálna Lambda dokumentácia rozlišuje durable functions s checkpointovaným workflow state-om a dlhšími executions. Nejde iba o štandardný handler s dlhším timeoutom. Invocation, wait, retry, checkpoint, idempotency a event-source integration majú vlastné semantics.

Pred použitím treba identifikovať:

- durable execution name/identity;
- version a code generation;
- checkpointed step;
- external side-effect boundary;
- retry policy per operation;
- cancellation/termination semantics;
- retention a query evidence.

Rovnaký execution name môže slúžiť ako deduplication boundary iba podľa konkrétneho API contractu; business idempotency sa tým automaticky nevyrieši.

## 16. Observability musí spojiť platformu s business výsledkom

Minimum pre `SVL-PAY-42`:

- `Invocations`, `Errors`, `Throttles`, `Duration` a initialization evidence;
- `ConcurrentExecutions`, reserved/provisioned usage a spillover;
- queue depth, age, receive count a DLQ;
- event source mapping state, last processing result a iterator age podľa source;
- structured log s version, mapping, event, attempt, idempotency a correlation identity;
- downstream latency, error, quota a connection metrics;
- deployment/alias/configuration changes z CloudTrail;
- ledger/provider/business completion metric.

`Errors = 0` môže koexistovať s backlogom, swallowed exception alebo nesprávnym business outcome-om. Platform metric nie je business oracle.

## 17. Worked failure: batch retry duplikuje settlement

Po release 7.16.0 sa backlog zvyšuje a provider hlási duplicate settlement attempts.

### Exact symptom a competing hypotheses

1. reserved concurrency throttluje consumer;
2. provider je pomalý a visibility timeout vyprší;
3. partial batch response nie je effective na aktuálnej mapping generation;
4. handler volá provider pred atomic idempotency claimom;
5. deployment spustil wrong version alebo mapping target.

### Discriminating evidence

CloudWatch ukazuje nízke `Throttles`, ale duration p95 je 85 sekúnd. SQS receive count rastie a niektoré messages sú znovu visible po 60 sekundách, hoci approved visibility timeout mal byť 180 sekúnd. CloudTrail a `GetEventSourceMapping` ukážu, že mapping `ESM-PAY-12` smeruje na alias `live`, no queue bola pri migration znovu vytvorená ako generation `QUEUE-PAY-23` s visibility timeoutom 60 sekúnd.

Structured logs dokazujú:

```text
attempt 1, version 84
→ provider settlement accepted
→ ledger write čaká na lock
→ message becomes visible
→ attempt 2 starts concurrently
→ provider receives same business operation without provider idempotency key
```

Root cause nie je Lambda throttle. Je to mismatch source generation + nesprávne poradie side effectu a idempotency claimu.

### Containment

- reserved concurrency sa dočasne zníži tak, aby sa zastavil overlap a chránil provider;
- event source mapping sa pozastaví;
- queue sa nesmie purge-nuť;
- provider a ledger evidence sa zachová podľa `settle-S884`;
- nové settlement requests sa prijímajú do queue, ale nespracúvajú nekontrolovane.

### Authoritative recovery

1. visibility timeout sa nastaví podľa worst-case function timeout a retry margin;
2. handler najprv vykoná atomic business claim;
3. provider call používa `settle-S884` ako provider idempotency key;
4. ledger/outbox completion sa reconciliuje s provider outcome-om;
5. failed records používajú partial batch response;
6. replay sa spúšťa v bounded concurrency na version 85;
7. mapping sa obnoví až po canary batchi.

### Acceptance verdict

Recovery je uzavretá až keď:

- každý source record má jeden authoritative completion marker;
- provider aj ledger majú jeden settlement pre `S-884`;
- queue receive count už nevytvára concurrent duplicate processing;
- valid records v mixed batchi sa zbytočne nereplayujú;
- backlog sa vyprázdni bez prekročenia downstream budgetu;
- forbidden test s opakovaným rovnakým eventom nevytvorí druhý side effect;
- old version 84 a wrong queue generation sú vyradené z production pathu.

Skorší control: deployment gate porovná queue ARN, visibility timeout, mapping UUID/target, function timeout, partial-batch configuration a provider idempotency capability pred presunom aliasu.

## 18. Troubleshooting model

Pri incidente postupuj:

```text
business symptom
→ exact event/source/function/version subject
→ delivery a acknowledgement model
→ concurrency/backlog timeline
→ execution-environment a handler evidence
→ downstream transaction/unknown outcome
→ competing hypotheses
→ discriminating source/platform/business observations
→ evidence-preserving containment
→ idempotent recovery/replay
→ original aj forbidden outcome verification
```

### Function sa nespúšťa

Rozlíš source bez eventu, disabled mapping, filter mismatch, missing invoke permission, zero reserved concurrency, alias/version mismatch a Region/account confusion.

### Function timeoutuje

Rozdeľ Init, handler CPU/memory, DNS/network, secret fetch, connection acquisition, downstream request, SDK retries a lock/transaction wait. Zvýšenie timeoutu bez tejto lokalizácie iba rozšíri blast radius.

### SQS records sa opakujú

Over queue generation, visibility timeout, receive count, function duration, whole/partial batch response, source redrive, handler acknowledgement a idempotency.

### Stream iterator age rastie

Over shard/partition distribution, poison record, batch retry/split, reserved concurrency, downstream latency, ordering a event retention deadline.

### Cost prudko rastie

Over recursive event loop, retry amplification, duration, provisioned concurrency, high-volume logs, NAT/data transfer a downstream API calls. Cost containment nesmie zničiť evidence ani zahodiť unprocessed events.

## 19. Security a cost boundaries

Security:

- least-privilege execution role a scoped resource policy;
- source ARN/account conditions;
- signed a immutable artifacts;
- secret redaction a payload minimization;
- KMS, VPC endpoint a destination policies;
- code/dependency vulnerability a provenance;
- controlled replay permissions.

Cost:

```text
invocation count
× billed duration
× memory/architecture rate
+ provisioned concurrency
+ logs/traces
+ network/NAT/data transfer
+ downstream service usage
```

Vyššia memory môže znížiť duration a total cost. Provisioned concurrency rieši latency, nie automaticky economics. Najlacnejšia function configuration je tá, ktorá spĺňa business latency a reliability pri celkovom dependency cost-e.

## 20. Kontrolné otázky

1. Čo tvorí exact Lambda execution subject?
2. Prečo execution environment reuse nie je durable-state contract?
3. Kto vlastní retry pri synchronous, asynchronous a event-source-mapping invocation?
4. Prečo partial batch response nenahrádza idempotenciu?
5. Ako reserved concurrency zároveň chráni aj obmedzuje funkciu?
6. Prečo function timeout nevylučuje committed downstream side effect?
7. Aký je rozdiel medzi execution role a function resource policy?
8. Ako queue visibility timeout súvisí s function timeoutom a duplicate delivery?
9. Čo musí obsahovať bezpečný replay manifest?
10. Aký dôkaz odlišuje platform success od business success?

## Glossary impact

Relevantné pojmy: serverless execution subject, invocation admission verdict, execution-environment generation, delivery generation, acknowledgement boundary, partial-batch acknowledgement, concurrency budget, backlog deadline, unknown side-effect outcome, replay manifest, Lambda version/alias generation a serverless acceptance verdict.

## Oficiálna dokumentácia

- [AWS Lambda Developer Guide](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)
- [Execution environment lifecycle](https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtime-environment.html)
- [Lambda invocation methods](https://docs.aws.amazon.com/lambda/latest/dg/lambda-invocation.html)
- [Retry behavior](https://docs.aws.amazon.com/lambda/latest/dg/invocation-retries.html)
- [Event source mappings](https://docs.aws.amazon.com/lambda/latest/dg/invocation-eventsourcemapping.html)
- [Lambda concurrency](https://docs.aws.amazon.com/lambda/latest/dg/lambda-concurrency.html)
- [Invoking durable functions](https://docs.aws.amazon.com/lambda/latest/dg/durable-invoking.html)
- [Lambda VPC networking](https://docs.aws.amazon.com/lambda/latest/dg/configuration-vpc.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Route 53 a CloudFront](route53-cloudfront.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: ECS a EKS →](ecs-eks.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
