# Queue mode, Redis, workers a scaling

Queue mode rozdeľuje n8n na process roles, aby ingress a orchestration neboli viazané na execution capacity jedného procesu. Main alebo webhook process vytvorí execution, Redis sprostredkuje work item a worker načíta workflow state z PostgreSQL, vykoná nodes a zapíše výsledok späť do databázy. Škálovanie preto závisí od celej cesty, nie iba od počtu workerov.

Táto kapitola pokračuje v incidente `AGENT-N8N-09`. Queue depth rástla, preto autoscaler pridal workers. PostgreSQL connection budget sa vyčerpal, noví workers neboli ready a binary payloady uložené na lokálnom filesysteme neboli dostupné procesu, ktorý execution prevzal. Redis bol zdravý, ale platforma nebola schopná dokončiť business work.

Nosný queue lifecycle je:

```text
trigger alebo webhook ingress
→ exact main/webhook generation
→ execution record v shared database
→ Redis queue publication
→ eligible worker claim
→ workflow a credential read z PostgreSQL
→ node execution a external side effects
→ execution result persistence
→ completion notification cez Redis
→ authoritative business read-back a queue reconciliation
```

## 1. Queue mode purpose

Queue mode umožňuje oddeliť prijímanie práce od jej vykonávania a horizontálne pridávať workers. Pomáha pri burstoch, rôzne dlhých workflows a potrebe samostatne škálovať webhook ingress.

Queue však nepridáva nekonečnú kapacitu. Presúva bottleneck medzi Redis, PostgreSQL, workers, binary storage, external APIs a network paths.

## 2. Process roles

Main process riadi editor, timers, workflow metadata a orchestration podľa deploymentu. Webhook processors môžu samostatne prijímať production webhook requests. Workers vykonávajú production workflows.

Každá rola potrebuje presný image, configuration, database, Redis a encryption-key subject. Proces s odlišnou generation môže vytvoriť protocol alebo credential failure aj keď je individuálne healthy.

## 3. Shared PostgreSQL

Workers načítavajú workflow information a zapisujú execution results do spoločnej databázy. PostgreSQL je durable authority pre workflow a execution state, preto jeho latency a connections priamo limitujú queue throughput.

Redis health bez database health neznamená progress. Worker môže vyzdvihnúť job, ale nemusí vedieť načítať alebo commitnúť jeho stav.

## 4. Redis role

Redis funguje ako message broker pre pending executions a completion notifications. Queue item nesie execution identity, zatiaľ čo detailný workflow a result state ostáva v database.

Redis sa preto nesmie považovať za jediný backup alebo business ledger. Po incident-e sa queue stav reconciliuje s database a external systems.

## 5. Exact queue subject

Queue subject obsahuje Redis endpoint, logical database, TLS/auth generation, queue prefix, n8n version, execution mode, worker concurrency, graceful-shutdown timeout a relevantné relay limits. Label `redis-production` nestačí.

Main, webhook a workers musia používať compatible queue configuration. Split-brain prefixes alebo databases môžu vytvoriť procesy, ktoré sa navzájom nevidia.

## 6. Encryption key consistency

Workers a webhook processors potrebujú rovnakú encryption key ako main, aby vedeli používať credentials uložené v PostgreSQL. Mismatch sa môže prejaviť až pri konkrétnom credential node, nie pri simple health checku.

Key generation sa rolloutuje ako composed change. Readiness alebo canary musí vykonať bezpečný credential-backed call, nie iba otvoriť database connection.

## 7. Worker startup

Worker sa spúšťa explicitnou worker command a pripája sa k Redis aj PostgreSQL. Startup success znamená, že process beží; readiness musí potvrdiť, že dependencies sú použiteľné.

Deployment nepočíta process ako capacity, kým worker nie je ready a nezaregistroval intended generation. Replica count v orchestrátore je desired state, nie effective worker capacity.

## 8. Liveness verzus readiness

Liveness odpovedá, či process žije. Readiness odpovedá, či má použiteľné database a Redis connections a môže bezpečne prijať prácu.

n8n worker health endpoints môžu rozlišovať `/healthz` a `/healthz/readiness`, keď je health check aktivovaný. Load balancer alebo scheduler nemá posielať traffic procesu, ktorý je live, ale dependency-unready.

## 9. Worker concurrency

Jeden worker process môže spracúvať viac executions súčasne. Concurrency určuje parallel work per process a mení CPU, memory, connections, external request rate aj pressure na Redis a database.

Zvýšenie worker replicas a zvýšenie concurrency majú násobivý efekt. Capacity model používa `workers × concurrency`, ale zároveň modeluje workflow resource profile.

## 10. Heterogénne workflows

Krátky HTTP workflow a dlhý file/AI workflow nepoužívajú rovnaké resources. Jedna globálna concurrency hodnota môže viesť k head-of-line blocking, memory pressure alebo noisy-neighbor efektu.

Workload sa segmentuje podľa duration, memory, binary volume, external rate limits a side-effect risku. Ak platforma nepodporuje natívne oddelené queues pre každý class, boundaries sa riešia samostatnými instances alebo controlled routingom.

## 11. Queue depth

Queue depth ukazuje počet waiting jobs, ale nehovorí, ako dlho čakajú, aký majú workload ani či workers robia progress. Rovnaká depth môže byť normálny krátky burst alebo systémové zlyhanie.

Kľúčové sú oldest-job age, enqueue rate, completion rate, failure rate a worker readiness. Autoscaling reaguje na trend a service objective, nie na izolovaný counter.

## 12. Throughput a critical path

Throughput limituje najpomalšia shared dependency. Viac workerov nepomôže, ak PostgreSQL commits, Redis latency, binary storage alebo provider rate limit už saturujú.

Load test sleduje celý critical path od ingress po business outcome. Worker CPU utilization je iba jedna časť evidence.

## 13. Backpressure

Backpressure obmedzuje prijímanie alebo concurrency, keď downstream capacity nestačí. Bez neho queue rastie, latency sa zvyšuje a retries môžu vytvoriť amplification.

Policy môže odložiť non-critical triggers, znížiť parallelism alebo odmietnuť nové requests s explicitnou odpoveďou. Skryté prijatie práce, ktorú platforma nevie dokončiť v SLA, je horšie než bounded rejection.

## 14. Autoscaling inputs

Autoscaler potrebuje queue age a rate, ready-worker count, CPU/memory, database headroom, Redis latency, external provider limits a business priority. Scale decision má maximum, cooldown a rollback.

Ak database connection utilization prekročí safe threshold, ďalší worker môže znížiť throughput. Scaling policy preto obsahuje hard dependency guardrails.

## 15. Scale-out delay

Nový worker potrebuje image pull, startup, dependency connections, key/config load a readiness. Pri krátkom burste môže nastúpiť až po odznení loadu.

Capacity planning rozlišuje pre-warmed baseline a reactive burst capacity. SLA kratšie než worker startup vyžaduje dostatočný ready reserve.

## 16. Scale-in

Scale-in nesmie zabiť active executions bez graceful shutdown a outcome handling. Worker dostane čas dokončiť job alebo platforma musí vedieť bezpečne klasifikovať interrupted execution.

`N8N_GRACEFUL_SHUTDOWN_TIMEOUT` alebo ekvivalentná konfigurácia sa nastavuje podľa p95/p99 duration, nie arbitrárne. Long waits a human approvals potrebujú iný durability model než aktívny CPU job.

## 17. Unknown execution after termination

Ak worker skončí po external commit-e a pred result persistence, queue alebo database môže ukázať failure či incomplete state, hoci side effect existuje. Automatický retry celej execution môže duplikovať operáciu.

Recovery číta stable operation key a provider state. Queue retry semantics nenahrádzajú business idempotency.

## 18. Redis availability

Main, webhook processors a workers potrebujú Redis. Network partition alebo broker outage zastaví publication, claim alebo completion notification podľa fázy.

`QUEUE_BULL_REDIS_TIMEOUT_THRESHOLD` určuje, ako dlho n8n čaká pri nedostupnosti pred exitom. Hodnota musí ladiť s orchestrator restart policy a incident detection, aby nevznikol nekonečný crash loop.

## 19. Redis persistence a recovery

Redis durability configuration závisí od deploymentu, ale queue nie je jediný application ledger. Recovery plan musí vedieť, ktoré executions boli created, running, waiting alebo externally committed aj pri strate broker state.

Po Redis restore alebo failover-e sa nevykoná bulk replay bez database a provider reconciliation. Stale queue item môže odkazovať na už terminal operation.

## 20. Redis memory

Queue jobs, events a veľké webhook response relay messages spotrebúvajú Redis memory. Large responses môžu mať viac in-flight copies a zmeniť broker z coordination layer na payload bottleneck.

Memory model zahŕňa peak queue, response size a retention. Eviction policy nesmie potichu zahadzovať queue state; unsupported alebo unsafe eviction je hard configuration defect.

## 21. Large webhook responses

V queue mode execution beží na workerovi, ale client zostáva pripojený k main alebo webhook procesu. Response z `Respond to Webhook` sa prenáša späť cez queue message a podlieha relay size limitu.

Pre veľké body n8n podporuje offload do shared binary storage v podporovaných versions. Offload musí byť zapnutý na workers a storage musí vedieť čítať main alebo webhook process.

## 22. Webhook processors

Webhook processors samostatne škálujú ingress. Load balancer smeruje production webhook paths do webhook poolu a editor/internal API na main process podľa n8n routing modelu.

Main sa bežne nepridáva do heavy webhook poolu, pretože traffic môže degradovať editor a orchestration. Manual test webhook path ostáva na intended process-e.

## 23. Webhook URL a reverse proxy

`WEBHOOK_URL`, protocol, host a proxy headers určujú external callback identity. Nesprávny base URL môže registrovať provider webhook na nefunkčný alebo test endpoint.

Scale test používa real production route cez load balancer, TLS a webhook processor. Direct Pod call nepreukazuje ingress path.

## 24. Main-process webhooks

Pri samostatných webhook processors možno production webhook handling na main vypnúť. Tým sa znižuje accidental traffic a jasnejšie sa oddeľujú roles.

Configuration musí byť konzistentná s load balancerom. Ak main processing vypne skôr, než webhook pool je ready, vznikne outage.

## 25. Binary storage boundary

Queue mode nepodporuje lokálny filesystem binary mode ako distribuovaný shared store. File vytvorený jedným processom nemusí existovať na workerovi, ktorý execution vykoná.

Podporovaný shared mode, napríklad external object storage, musí byť dostupný všetkým relevantným process roles. Database mode môže fungovať, ale prenáša binary load do primary database a memory pathov.

## 26. Task runners

Code execution alebo task-runner architecture môže pridávať ďalšie process boundaries. Runner version, mode, network a sandbox policy sa viažu na worker generation.

Scale-out workers bez zodpovedajúcej runner capacity vytvorí nový bottleneck. Worker ready neznamená, že runner pool má capacity pre Code nodes.

## 27. Version compatibility

Main, webhook, workers a runners sa upgradujú koordinovane. Protocol, execution payload alebo storage handling sa môže meniť medzi versions.

Canary worker nesmie spracovať production job, ak mixed-version compatibility nie je potvrdená. Release manifest uvádza exact image digest každej role.

## 28. Queue monitoring

Prometheus queue metrics môžu ukazovať active, waiting, completed a failed jobs. Main a worker processes zároveň expose vlastné process metrics, ak je endpoint povolený.

Metrics sa zbierajú zo všetkých roles a označujú instance, role a generation. Aggregate bez ready-worker denominatora môže skryť, že polovica replicas nepracuje.

## 29. Logs per process

Každý process potrebuje identifikovateľné logs s execution, workflow, worker a release IDs. Viaceré workers nesmú bez koordinácie zapisovať do rovnakého lokálneho file pathu, kde dochádza ku kolíziám alebo nejasnému rotation ownershipu.

Console logs sa typicky zbierajú platformou. File output potrebuje per-process path a retention model.

## 30. Shared incident `AGENT-N8N-09`

Webhook burst vytvoril backlog a autoscaler pridal workers. Nové processes zvýšili database connections nad safe budget a časť neprešla readiness, ale replica dashboard ich stále počítal ako capacity.

Workflow zároveň prijímal PDF payloady v `filesystem` binary mode na lokálnom volume webhook Podu. Worker, ktorý job vyzdvihol, nevedel binary object načítať a execution zlyhala po queue claim-e.

## 31. Competing failure hypotheses

Prvá hypotéza je nedostatok worker CPU, druhá Redis saturation, tretia database connection exhaustion, štvrtá missing shared binary data a piata provider throttling. Queue depth je spoločný symptom, nie root cause.

Diskriminačné testy porovnajú ready workers, connection waits, Redis latency, binary object read a provider response. Zásah sa zvolí podľa najskoršej divergence.

## 32. Evidence preservation

Zachová sa enqueue/completion rate, oldest age, Redis health, worker inventory, readiness, concurrency, database sessions, binary mode a object references. Affected execution IDs sa spárujú s ingress request a external operation IDs.

Pred drainingom alebo retryom sa snapshotne queue a database state. Reconfiguration môže zmeniť evidence a zakryť pôvodný path.

## 33. Containment

Autoscaling sa zastaví, max worker count sa zníži podľa database budgetu a high-memory alebo binary workflow ingress sa obmedzí. Unsupported filesystem path sa nepokúša opraviť zdieľaním random local directory medzi ephemeral Pods.

Critical operations pokračujú v bounded cohort-e s shared storage a known-good workers. Unknown outcomes sa karanténujú.

## 34. Recovery

Binary data sa presunie do supported shared mode s migration a read-back planom. Worker concurrency, pool size a autoscaler guardrails sa zosúladia s PostgreSQL, Redis a provider capacity.

Main, webhook a worker generations sa redeploynú koordinovane. Representative webhook potvrdí ingress, queue claim, binary read, execution persistence a business outcome.

## 35. Positive acceptance

Queue age zostáva v SLO pri representative burst-e a ready-worker count zodpovedá effective capacity. Database a Redis majú headroom a všetky workers používajú rovnaký key, version a storage mode.

Binary workflow dokončí external operation a result je čitateľný z execution history. Scale-out zlepší throughput bez zvýšenia error rate alebo unknown outcomes.

## 36. Forbidden acceptance

Viac workerov nie je úspech, ak queue rastie, database connections sú saturated alebo filesystem binary objects chýbajú. Neprípustné je počítať live process ako ready capacity.

Redis green ani empty queue nepreukazuje business success; jobs mohli failnúť, byť pruned alebo skončiť neznámym side effectom.

## 37. Recovery acceptance

Redis restart, worker termination a database failover drill prebehnú bez nekontrolovaného duplicate mutation. Interrupted operations sa klasifikujú cez idempotency a provider read-back.

Po scale-in ostanú active jobs dokončené alebo explicitne reconciled. Queue, database a business ledger sa zhodujú.

## 38. Second-workflow acceptance

Druhý workload s malými JSON items a odlišným provider limitom prejde rovnakou queue platformou bez starvation od veľkého binary workflowu. Test odhalí noisy-neighbor a fairness problémy.

Scale policy sa nesmie optimalizovať iba pre jeden benchmark. Segmentované latency a failure metrics ostávajú v accepted range.

## 39. Praktický queue manifest

Manifest prepája process roles, dependencies a scaling limits. Hodnoty sú reviewable a nie sú skryté iba v autoscaler defaultoch.

```yaml
queue_subject:
  execution_mode: queue
  redis_generation: redis-prod-7
  database_subject: postgres-n8n-18-a
  encryption_key_generation: key-2026-08
  binary_mode: s3
  roles:
    main: 1
    webhook: 2
    workers:
      min: 4
      max: 10
      concurrency: 5
  guardrails:
    database_connection_utilization_max: 0.70
    oldest_job_age_seconds: 30
    graceful_shutdown_seconds: 180
```

## 40. Prevádzkové metriky

Sledujú sa enqueue, active, waiting, completed a failed jobs, oldest age, pickup latency, execution duration, ready workers, restarts, graceful shutdown failures, Redis memory/latency, database pool wait, binary read errors a provider throttling. Metriky sa segmentujú podľa workflow classu.

Autoscaling rozhodnutie sa loguje s inputs a target generation. Bez decision provenance sa nedá vysvetliť, prečo platforma pridala alebo odobrala capacity.

## 41. Primárne zdroje

- [n8n Docs — Enable queue mode](https://docs.n8n.io/deploy/host-n8n/configure-n8n/scaling/enable-queue-mode/)
- [n8n Docs — Queue mode environment variables](https://docs.n8n.io/deploy/host-n8n/configure-n8n/basic-configuration/use-environment-variables/queue-mode/)
- [n8n Docs — Enable Prometheus metrics](https://docs.n8n.io/deploy/host-n8n/configure-n8n/basic-configuration/configuration-examples/enable-prometheus-metrics/)
- [n8n Docs — Handle binary data](https://docs.n8n.io/deploy/host-n8n/configure-n8n/scaling/handle-binary-data/)
- [n8n Docs — External storage](https://docs.n8n.io/deploy/host-n8n/configure-n8n/scaling/use-external-storage/)

## 42. Zhrnutie

Queue mode je distributed execution system, nie jednoduchý worker counter. Redis koordinuje work, PostgreSQL drží authority, workers vykonávajú side effects a shared storage prenáša binary state medzi procesmi.

Bez dependency-aware scaling môže vyšší replica count znížiť throughput a zvýšiť unknown outcomes. Accepted stav vyžaduje end-to-end progress, readiness, storage visibility, database headroom a business read-back pri druhom odlišnom workload-e.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Self-hosting s PostgreSQL](self-hosting-postgresql.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Binary data, storage a execution retention →](binary-data-storage-execution-retention.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
