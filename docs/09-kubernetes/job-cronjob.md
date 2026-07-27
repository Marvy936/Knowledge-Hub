# Job a CronJob

Job a CronJob riadia prácu, ktorá má skončiť. Job udržiava completion contract jednej finite operation. CronJob vyhodnocuje časový plán a vytvára samostatné Jobs pre jednotlivé logical schedule instances.

Kubernetes môže opakovať container alebo Pod execution. Preto controller completion nie je automaticky business exactly-once výsledok.

Dominantný lifecycle:

```text
business operation alebo schedule intent
→ logical run identity
→ Job/CronJob UID, generation a immutable template
→ schedule eligibility alebo direct Job creation
→ Pod attempt a work-item claim
→ bounded execution, checkpoint a side effects
→ durable result commit
→ Job completion/failure verdict
→ evidence retention, TTL a cleanup
→ retry, replay, resume alebo compensation
→ business acceptance a next-run safety
```

Kľúčová diagnostická otázka nie je „skončil Pod s exit code 0?“, ale:

```text
Ktorý logical run a work item sa mal vykonať?
Koľko process/Pod/Job attempts nad ním konalo?
Aký durable result a side effects reálne commitli?
Je opakovanie bezpečné a je výsledok overený mimo Job statusu?
```

## 1. Atlas scenár

Atlas každú noc reconcile-uje payment settlement ledger s externým processorom.

```text
CronJob: production/payments-reconcile
schedule: 0 02 * * *
timeZone: Etc/UTC
logical schedule instance: 2026-07-27T02:00:00Z
logical run key: reconcile/2026-07-27
CronJob generation: 14
Job: payments-reconcile-<suffix>
image digest: REC420
configuration generation: C52
credential epoch: SE08
expected partitions: 64
```

Acceptance contract:

- jeden logical run key má jeden canonical result ledger;
- work item sa môže technicky pokúsiť vykonať viackrát, ale side effect je idempotentný alebo deduplikovaný;
- exit code 0 sa nastaví až po durable result commit-e;
- retries používajú rovnakú operation identity;
- partial progress je checkpointovaný alebo bezpečne rekonštruovateľný;
- downstream rate limits a cluster capacity sú chránené;
- TTL neodstráni jedinú incidentnú evidence;
- po recovery sa nevynechá ani nezdvojí business interval.

## 2. Identity vrstvy

Rozlišuj:

```text
CronJob UID/generation
scheduled timestamp
logical run key
Job UID
Pod UID
container ID a restart count
completion index alebo work-item ID
external operation/idempotency key
checkpoint/result ledger generation
business transaction ID
```

Meno Jobu alebo Podu samo nepreukazuje, či ide o nový business run alebo retry existujúceho runu.

CronJob vytvorený Job môže niesť scheduled timestamp metadata podľa podporovanej Kubernetes verzie. Application má napriek tomu používať explicitnú business run identity, ktorá prežije retries, replays a controller recovery.

## 3. Job subject

Pre každý Job zaznamenaj:

```text
cluster, namespace a Job UID/generation
owner CronJob UID alebo direct-run owner
logical run key a scheduled timestamp
Pod template digest, imageID, config a credential generation
completion mode, completions a parallelism
backoff, deadline, failure a success policy
Pod UIDs, attempts, restart counts a completion indexes
work-item claims, checkpoints a external request IDs
result ledger a artifact identities
Complete/Failed condition a observed timing
cleanup/TTL policy
```

Job controller riadi Pod attempts a completion counts. Business protocol musí riadiť work ownership, duplicate detection a result commit.

## 4. Pod attempt lifecycle

```text
Job controller vytvorí Pod
→ scheduler a kubelet realizujú Pod
→ process načíta run identity
→ process claimne work item
→ vykoná side effects
→ commitne checkpoint/result
→ uvoľní alebo uzavrie claim
→ skončí exit code 0
→ Job controller započíta úspešné completion
```

Ak process zlyhá po side effect-e, ale pred result commitom, ďalší attempt nesmie slepo zopakovať operáciu bez lookup-u podľa stable idempotency key.

## 5. Container restart vs. nový Pod attempt

### `restartPolicy: OnFailure`

Kubelet môže reštartovať container v tom istom Pod UID. Application logic sa vykoná znova s rovnakým Pod subjectom, ale novým container processom.

### `restartPolicy: Never`

Pod skončí Failed a Job controller môže vytvoriť nový Pod UID.

V oboch prípadoch platí:

```text
nový process attempt
≠ nový logical work item
```

Attempt counter nemá byť jediný deduplication mechanizmus. Process môže zlyhať po nepozorovanom úspechu external operation.

## 6. Completion contract

### Jedno completion

Jednoduchý Job potrebuje jeden úspešný completion. To je vhodné pre jednu finite operation, ak application success contract spoľahlivo reprezentuje durable result.

### Fixed completions

```yaml
spec:
  completions: 64
  parallelism: 8
```

Controller chce 64 successful completions s bounded concurrency. Musíš určiť, či completion reprezentuje:

- jeden deterministic partition;
- jeden work item;
- ľubovoľného workera, ktorý vyprázdnil queue;
- redundantný výpočet;
- business subset.

### Indexed Job

Completion index poskytuje stabilný index pre statické rozdelenie. Index nie je automaticky globally unique transaction ID. Viaž ho na Job UID alebo logical run key:

```text
reconcile/2026-07-27/partition/17
```

## 7. Work queue protocol

Pri external queue modeloch nestačí „worker skončil 0“. Definuj:

```text
claim identity
lease alebo visibility timeout
fencing/owner epoch
acknowledgment moment
checkpoint
retry a poison-item policy
queue-empty verdict
result completeness proof
```

Worker môže zomrieť po spracovaní, ale pred acknowledgmentom. Redelivery je normálna vlastnosť; side effect musí byť bezpečný pri opakovaní.

## 8. Retry a backoff

`backoffLimit` obmedzuje controller retry behavior, ale nie vždy mapuje 1:1 na počet application attempts, pretože existujú:

- container restarts v tom istom Pode;
- paralelné failures;
- terminating attempts;
- indexed per-index semantics;
- controller recovery a delayed observations.

Retry decision musí klasifikovať failure:

```text
transient a bezpečne opakovateľný
permanentný input/config error
unknown external outcome
partial progress s checkpointom
poison work item
capacity alebo policy rejection
```

Unknown outcome vyžaduje lookup/reconciliation, nie automatický create alebo charge call.

## 9. Deadlines a cancellation

Rozlišuj:

- application operation timeout;
- downstream request timeout;
- claim/lease expiry;
- Pod termination grace period;
- Job `activeDeadlineSeconds`;
- pipeline alebo operator timeout.

Deadline môže ukončiť Pods. Nevracia external side effects a neoznačí automaticky work item ako safe-to-retry.

Cancellation protocol má:

- prestať claimovať novú prácu;
- checkpointovať alebo označiť rozpracované items;
- uvoľniť lease bezpečne;
- zachovať operation IDs a evidence;
- odlíšiť cancelled, failed a completed result.

## 10. Suspend a resume

Suspend zastaví alebo obmedzí ďalšiu controller activity podľa resource semantics. Resume neobnoví process memory.

Bezpečný resume potrebuje:

```text
logical run key
checkpoint/result ledger
active claim inventory
stale-owner fencing
remaining work calculation
new attempt generation
```

Suspend nie je transactional pause business operation.

## 11. Pod failure a success policy

Pod failure policy môže rozlišovať permanentné exit codes, disruptions alebo per-index failures. Policy je účinná iba vtedy, keď application exit-code contract je jednoznačný.

Príklad:

```text
exit 10 → invalid immutable input; neretryovať
exit 20 → downstream rate limit; retry s backoffom
exit 30 → unknown external outcome; reconcile podľa operation ID
exit 0  → durable result commit bol overený
```

Success policy môže prijať subset úspešných indexes iba vtedy, keď business contract naozaj nepotrebuje všetky výsledky. Nesmie sa použiť na migráciu alebo settlement len preto, aby Job skončil green.

## 12. CronJob schedule subject

CronJob subject zahŕňa:

```text
CronJob UID/generation
schedule expression a time zone
controller evaluation time
logical scheduled timestamp
starting deadline
concurrency policy
active Jobs a ich logical run keys
lastScheduleTime/lastSuccessfulTime ako status evidence
missed-schedule inventory
```

Cron schedule vyjadruje požadovaný čas, nie hard real-time ani exactly-once garanciu.

## 13. Time zone a DST

Explicitný `timeZone` je súčasť business contractu. Pri lokálnom pásme môže DST:

- preskočiť neexistujúci čas;
- zopakovať rovnaký lokálny čas;
- zmeniť UTC offset;
- vytvoriť ambiguity v date-based run key.

Run identity má používať jednoznačný timestamp alebo business interval, nie iba display string ako `2026-10-25 02:30`.

Pre infra tasks býva UTC jednoduchší. Business schedule môže používať lokálne pásmo, ak sú explicitne definované duplicate/missed semantics.

## 14. Concurrency policy

### `Allow`

Povolí overlap scheduled Jobs. Je bezpečný iba pri oddelených data ranges alebo application concurrency protocol-e.

### `Forbid`

Nevytvorí nový Job, ak controller vidí active predchádzajúci Job. Neposkytuje distributed exactly-once lock nad business side effects a nevyrieši stuck Job, stale status alebo ručne vytvorený duplicate run.

### `Replace`

Nahradí active Job novým. Starý process môže byť ešte v termination-e alebo už mať partial side effects. Replace je cancellation + new execution, nie safe resume.

## 15. Starting deadline a missed schedules

Po control-plane outage-e môže CronJob controller vyhodnocovať missed schedules. `startingDeadlineSeconds` určuje, ktoré staré runs sú ešte eligible.

Rozhodnutie má zohľadniť:

- či starý business interval stále dáva zmysel;
- či downstream unesie catch-up burst;
- či runs musia byť serializované;
- či existuje external ledger už spracovaných intervalov;
- maximum missed-schedule behavior controlleru;
- možné thundering herd po obnove.

Control-plane recovery nemá automaticky spustiť desiatky neobmedzených settlement Jobs.

## 16. Exactly-once boundary

Job a CronJob poskytujú at-least-once-like execution možnosti v rôznych failure scenároch, nie end-to-end exactly-once business transakciu.

Bezpečné mechanizmy:

- stable idempotency key;
- unique constraint nad business operation;
- transactional inbox/outbox;
- compare-and-set nad result ledgerom;
- checkpoint per partition/item;
- external queue acknowledgment;
- lease s fencing epoch;
- reconciliation po unknown outcome;
- compensation pre nevratné partial side effects.

Distributed lock bez fencing-u môže po lease expiry ponechať starého workera aktívneho súčasne s novým.

## 17. Result commit a exit code

Correct success order:

```text
vykonaj alebo lookup-ni external operation
→ durable commit výsledku
→ over invariant
→ emit subject-bound metric/artifact
→ exit 0
```

Nebezpečný order:

```text
spusti async external write
→ exit 0
→ Job Complete=True
→ external write neskôr zlyhá
```

Job status je controller evidence o Pod completion. Nie je authoritative business result ledger.

## 18. Evidence retention a TTL

`ttlSecondsAfterFinished` a CronJob history limits čistia Kubernetes objects. Pred cleanupom externalizuj:

- logs s run/job/pod/attempt IDs;
- result manifest;
- work-item success/failure inventory;
- checkpoints;
- external request IDs;
- timings a resource usage;
- image/config/credential generations;
- audit a business verification.

API object ani container log na jednom Node-e nemajú byť jedinou recovery evidence.

## 19. Capacity a downstream protection

`parallelism` je controller concurrency request, nie downstream-safe limit.

Zohľadni:

- scheduler capacity a quota;
- image pull burst;
- database connection pool;
- external API rate limits;
- storage IOPS;
- queue partition count;
- PriorityClass a preemption;
- retries zvyšujúce effective concurrency;
- multiple CronJobs v rovnakom čase.

Backoff bez global budgetu môže stále vytvoriť retry storm cez veľa Pods alebo Jobs.

## 20. Worked failure: Job Complete, ale settlement chýba

Application spustila asynchrónny upload reportu a skončila exit code 0 pred potvrdením object-store commit-u.

```text
process exit 0
→ Pod Succeeded
→ Job Complete=True
→ TTL odstráni Job a Pod
→ async upload zlyhá
→ business report neexistuje
```

Kubernetes korektne vyhodnotil process completion. Application success contract bol chybný.

Recovery musí z result ledgeru zistiť chýbajúci artifact a spustiť nový operation subject. Nestačí zmeniť Job status.

## 21. Worked failure: timeout po charge vytvoril duplicate side effect

Worker odoslal settlement request s náhodným request ID. Processor operáciu vykonal, ale response sa stratila. Pod skončil errorom a retry poslal nový request ID.

```text
external commit uspel
+ response unknown
+ nový idempotency key pri retry
→ processor vykoná druhú operáciu
```

Correct recovery používa rovnaký stable key odvodený z logical run a work itemu, vykoná lookup a až potom rozhodne o retry.

## 22. Worked failure: `Replace` spustil overlap

Nightly run trval dlhšie než deň. `concurrencyPolicy: Replace` označil starý Job na termination a vytvoril nový.

Starý process ešte počas grace period zapisoval do rovnakého export pathu. Nový Job začal od začiatku.

Replace ukončuje Kubernetes workload subject. Nezaručuje okamžité zastavenie external lease alebo side effects. Application potrebuje fencing a run-generation-aware output.

## 23. Worked failure: control-plane recovery vytvoril catch-up storm

CronJob controller bol nedostupný niekoľko hodín. Po obnove bolo viac missed intervals stále v starting deadline. Súčasne vzniklo viac Jobs a každý otvoril desiatky database connections.

Root cause chain:

```text
missed schedules
→ catch-up Job burst
→ high parallelism a retries
→ database saturation
→ Jobs spomaľujú a overlap rastie
→ ďalšie retries
```

Schedule correctness musí byť koordinovaná s downstream capacity a backlog policy.

## 24. Causal troubleshooting walkthrough: jeden scheduled interval bol spracovaný dvakrát

Settlement ledger obsahuje dve operácie pre business date `2026-07-27`. V clustri existujú dva Jobs vlastnené tým istým CronJobom s blízkym creation time.

### 1. Zafixuj subject a outcome

Zaznamenaj:

```text
CronJob UID/generation, schedule a timeZone
logical scheduled timestamp a business interval
Job UIDs, ownerReferences a scheduled-timestamp annotations
Pod UIDs, restarts, attempts a completion indexes
image/config/secret generations
concurrency policy, deadline a controller timeline
idempotency keys a external request IDs
result/checkpoint ledger rows
processor audit a settlement transaction IDs
expected one canonical business result
```

### 2. Competing hypotheses

1. CronJob controller vytvoril duplicate Jobs pre jeden schedule.
2. Jeden Job bol scheduled run a druhý manual replay bez odlišnej run identity.
3. Job mal viac Pod attempts po failure.
4. `OnFailure` reštartoval container po unknown outcome.
5. Indexed Job mapoval dva indexes na rovnaký business partition.
6. `Replace` vytvoril overlap so starým terminating Jobom.
7. Concurrency policy alebo active status bol stale.
8. External operation použila nový idempotency key pri retry.
9. Result commit zlyhal po úspešnom external side effect-e.
10. DST/time-zone ambiguity vytvorila dva rovnaké display intervals.
11. Application ledger nemá unique constraint.
12. Dashboard zoskupil odlišné logical runs podľa Job name prefixu.

### 3. Discriminating observation points

- CronJob audit a controller Events;
- Job owner UID, creation timestamp a scheduled timestamp;
- Pod lineage, restart count a previous logs;
- work-item claim/checkpoint timeline;
- external request IDs a processor idempotency audit;
- database unique constraints a transaction commits;
- Job completion/failure conditions;
- cancellation/termination overlap;
- time-zone conversion pre exact schedule;
- manual create/replay audit identity.

Observation `dva Jobs existujú` nevysvetľuje duplicate business side effect. Observation `jeden Job existuje` nevylučuje viac Pod alebo container attempts.

### 4. Containment

- suspend-ni CronJob a zastav nové claims pre affected interval;
- nezmaž Jobs/Pods pred zachovaním logs a IDs;
- fence-ni logical run key v result ledger-i;
- zastav alebo obmedz ďalšie external writes;
- nekompenzuj náhodnú transakciu bez canonical ownership rozhodnutia;
- zachovaj processor a database audit;
- obmedz catch-up parallelism.

### 5. Recovery podľa boundary

- duplicate Job creation → označ canonical Job podľa run ledgeru, ostatné bezpečne ukonči;
- manual replay collision → vyžaduj nový replay ID viazaný na pôvodný logical run;
- attempt duplicate → lookup-ni external result podľa stable key;
- missing result commit → reconcile-ni processor audit do authoritative ledgeru;
- double commit → vykonaj domain-approved compensation;
- DST ambiguity → používaj unambiguous scheduled timestamp/run key;
- missing uniqueness → pridaj constraint alebo CAS protocol;
- stale active/Replace overlap → zaveď fencing lease nad logical runom.

### 6. Over pôvodný outcome

Potvrď:

- logical interval má presne jeden canonical accepted result;
- každý work item je completed, failed alebo explicitly pending;
- duplicate external operation je reconciled/compensated;
- Job conditions zodpovedajú result ledgeru;
- idempotency key reuse test prejde pri lost-response scenári;
- CronJob resume nevytvorí ďalší run pre ten istý interval;
- nasledujúci scheduled run prejde presne raz;
- TTL nastane až po external evidence retention.

### 7. Posuň control skôr

Pridaj:

- explicitný logical run key a scheduled timestamp;
- unique result ledger constraint;
- stable operation IDs pre retries;
- unknown-outcome integration test;
- per-work-item checkpoint;
- catch-up a downstream capacity budget;
- replay workflow odlišný od scheduled create;
- result-commit-before-exit invariant;
- TTL gate založený na external evidence completion.

## 25. Observation matrix

| Boundary | Subject | Kľúčové observations |
|---|---|---|
| Schedule | CronJob UID/generation + timestamp | timeZone, deadline, missed runs, policy |
| Run | logical run key + Job UID | owner, template, manual/replay identity |
| Attempt | Pod/container ID | restart, exit, termination, timing |
| Work | item/index/claim | owner epoch, checkpoint, ack |
| Side effect | operation/idempotency key | downstream audit, unknown outcome |
| Result | ledger/artifact subject | durable commit, completeness, checksum |
| Controller | Job status | active/succeeded/failed, conditions |
| Capacity | batch cohort | parallelism, quota, downstream saturation |
| Cleanup | TTL/history subject | logs/results retained, deletion timeline |
| Business | interval/transaction ID | exactly-once or compensated outcome |

## 26. Referenčné príkazy

```bash
kubectl get cronjob <name> -n <namespace> -o yaml
kubectl describe cronjob <name> -n <namespace>
kubectl get jobs -n <namespace> -o wide
kubectl get job <name> -n <namespace> -o yaml
kubectl get pods -n <namespace> -l job-name=<job> -o wide
kubectl logs -n <namespace> job/<job>
kubectl get events -A --sort-by=.metadata.creationTimestamp
```

Príkazy ukazujú Kubernetes execution evidence. Business result a idempotency evidence musia pochádzať aj z application a downstream systémov.

## 27. Referenčné pravidlá

- Job desired state je completion, nie continuous process liveness.
- CronJob vytvára Jobs; nespúšťa priamo dlhodobý Pod.
- Logical run, Job, Pod, container attempt a business operation sú odlišné subjects.
- Container alebo Pod execution sa môže opakovať.
- Exit code 0 musí nasledovať až po durable result commit-e.
- `backoffLimit` nie je presný počet business attempts.
- Timeout ani Replace nevracajú external side effects.
- `Forbid` nie je end-to-end exactly-once lock.
- Indexed completion index potrebuje deterministic business mapping.
- Suspend/resume potrebuje checkpoint a stale-owner fencing.
- TTL a history cleanup nesmú odstrániť jedinú recovery evidence.
- Batch concurrency musí rešpektovať downstream capacity.
- Recovery musí overiť logical result, nie iba Job condition.

## 28. Kontrolné otázky

1. Aký lifecycle spája scheduled intent s durable business výsledkom?
2. Ako sa líšia logical run, Job UID, Pod UID a process attempt?
3. Prečo `OnFailure` aj `Never` môžu viesť k opakovaniu application logic?
4. Ako sa líšia `parallelism` a `completions`?
5. Aký protocol potrebuje external work queue?
6. Prečo `Forbid` negarantuje exactly-once?
7. Čo musí application urobiť po unknown external outcome-e?
8. Aké riziko má `Replace`?
9. Čo musí byť externalizované pred TTL cleanupom?
10. Čo musí Job/CronJob acceptance verdict overiť?

## Glossary impact

Relevantné pojmy: logical batch run subject, scheduled-run identity, Job execution subject, Pod attempt subject, work-item claim, completion-index mapping, result-commit invariant, unknown batch outcome, batch fencing epoch, checkpoint subject, CronJob schedule subject, missed-schedule inventory, catch-up budget, replay identity, batch result ledger, TTL evidence gate, Job observation matrix a batch acceptance verdict.

## Oficiálna dokumentácia

- [Jobs](https://kubernetes.io/docs/concepts/workloads/controllers/job/)
- [CronJobs](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/)
- [Automatic cleanup for finished Jobs](https://kubernetes.io/docs/concepts/workloads/controllers/ttlafterfinished/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: DaemonSet](daemonset.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: ConfigMap a Secret →](configmap-secret.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
