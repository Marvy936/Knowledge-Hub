# Job a CronJob

Job a CronJob sú Kubernetes workload controllers pre prácu, ktorá má skončiť. Job riadi jednu alebo viac Pod executions až do požadovaného počtu úspešných dokončení. CronJob vytvára nové Job objekty podľa časového plánu.

Na rozdiel od Deploymentu alebo DaemonSetu nie je desired state „process má nepretržite bežať“, ale „definovaná práca sa má úspešne dokončiť“.

## 1. Job mentálny model

```text
Job spec
  completions: 1
  parallelism: 1
       ↓
Job controller vytvorí Pod
       ↓
Pod exit 0
       ↓
Job condition Complete=True
```

Ak Pod zlyhá alebo zanikne, Job môže vytvoriť náhradný Pod podľa retry policy. Nový Pod znamená nové vykonanie application logic.

## 2. Minimálny Job

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: report
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: report
          image: registry.example.com/report@sha256:...
          args: ["generate"]
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
```

Job Pod template musí používať `restartPolicy: Never` alebo `OnFailure`, nie `Always`.

## 3. Container restart vs. nový Pod

### `restartPolicy: OnFailure`

Kubelet môže reštartovať zlyhaný container v tom istom Pode.

### `restartPolicy: Never`

Pod skončí ako Failed a Job controller môže vytvoriť nový Pod.

Application môže teda ten istý logical work item vykonať viac než raz. Side effects musia byť idempotentné alebo deduplikované.

## 4. Completion modely

### Jedno dokončenie

Default jednoduchý Job typicky potrebuje jeden úspešný Pod.

### Fixed completions

```yaml
spec:
  completions: 10
  parallelism: 2
```

Job potrebuje desať úspešných dokončení a môže naraz spustiť približne dve aktívne Pody.

### Work queue

Ak `.spec.completions` nie je pevne stanovené a workers čítajú external queue, úspešné dokončenie a queue-empty semantics musí definovať application protocol.

### Indexed Job

```yaml
spec:
  completionMode: Indexed
  completions: 10
  parallelism: 3
```

Každý Pod dostane stabilný completion index pre statické rozdelenie práce. Index nie je automaticky business transaction ID; aplikácia ho musí mapovať deterministicky.

## 5. `parallelism` a `completions`

- `parallelism` riadi požadovanú súbežnosť aktívnych Podov,
- `completions` riadi požadovaný počet úspešných dokončení.

Príklad:

```text
completions: 100
parallelism: 10
```

Kubernetes sa snaží spracovať sto logical completions maximálne približne desiatimi aktívnymi Podmi naraz.

Reálna súbežnosť môže byť nižšia kvôli scheduling capacity, backoffu, quota alebo failure policy.

## 6. Retry a backoff

```yaml
spec:
  backoffLimit: 4
```

Job controller sleduje failures a používa backoff pred ďalšími pokusmi.

`backoffLimit` nie je ekvivalent presného počtu application attempts v každom scenári, pretože:

- container sa môže reštartovať v tom istom Pode,
- viac Podov môže zlyhávať paralelne,
- controller stav a termination timing sa môžu prekrývať,
- indexed completion môže mať per-index failure semantics podľa konfigurácie.

Retry budget navrhuj spolu s idempotenciou a external rate limits.

## 7. Active deadline

```yaml
spec:
  activeDeadlineSeconds: 1800
```

Po prekročení celkového active time limitu Job zlyhá a aktívne Pody sa ukončia.

Rozlišuj:

- per-process timeout implementovaný aplikáciou,
- Pod termination grace period,
- Job active deadline,
- external orchestrator timeout.

Timeout musí zachovať evidence a bezpečne ukončiť alebo označiť rozpracované side effects.

## 8. Suspend a resume

```yaml
spec:
  suspend: true
```

Suspended Job nevytvára novú aktívnu prácu a active Pody môžu byť ukončené podľa controller behavioru. Resume pokračuje z Job statusu, nie z memory state-u zrušeného procesu.

Application musí mať checkpoint alebo idempotentný restart model.

## 9. Pod failure policy

Job môže mať jemnejšie pravidlá pre konkrétne Pod failures podľa exit code alebo Pod conditions, ak ich daná cluster verzia podporuje.

Použitie:

- konkrétny exit code znamená permanentnú chybu a nemá sa retryovať,
- eviction alebo disruption sa nemá započítať rovnako ako application failure,
- určitá chyba má označiť konkrétny index ako failed.

Policy nesmie nahradiť zrozumiteľný application exit-code contract.

## 10. Success policy

Pri niektorých paralelných/indexovaných workloadoch môže byť úspech definovaný subsetom dokončení podľa podporovanej API. Používaj iba vtedy, keď business výsledok nevyžaduje všetky tasks.

Príklad use case:

- stačí prvých N úspešných výsledkov,
- redundantné výpočty,
- quorum-like batch outcome.

To nie je vhodné pre migráciu, kde musí byť spracovaný každý record.

## 11. Cleanup dokončených Jobs

Completed Jobs a Pody spotrebúvajú API storage a zvyšujú list/watch load.

TTL controller:

```yaml
spec:
  ttlSecondsAfterFinished: 3600
```

Po dokončení môže controller Job a dependent Pody odstrániť.

Pred agresívnym cleanupom zabezpeč:

- centralizované logs,
- metrics a result artifacts,
- audit trail,
- failure evidence,
- external status record.

API object nemá byť jediným dlhodobým záznamom výsledku.

## 12. Job status

```bash
kubectl get job report
kubectl describe job report
kubectl get pods -l job-name=report
kubectl logs job/report
```

Sleduj:

- active,
- succeeded,
- failed,
- ready,
- terminating podľa API podpory,
- completed/failed indexes,
- conditions `Complete`, `Failed` alebo `Suspended`,
- start/completion time,
- Events.

## 13. CronJob mentálny model

```text
CronJob schedule
     ↓ v každom plánovanom čase
nový Job
     ↓
Pody
     ↓
completion/failure
```

CronJob nespúšťa dlhodobý Pod priamo. Vytvára samostatné Job objekty.

## 14. Minimálny CronJob

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: nightly-report
spec:
  schedule: "0 2 * * *"
  timeZone: "Etc/UTC"
  concurrencyPolicy: Forbid
  jobTemplate:
    spec:
      backoffLimit: 3
      template:
        spec:
          restartPolicy: Never
          containers:
            - name: report
              image: registry.example.com/report@sha256:...
              args: ["generate-nightly"]
```

Použitie explicitného `timeZone` znižuje ambiguity medzi cluster/controller lokalitou a business časom.

## 15. Schedule semantics

Cron expression určuje plánované časy, nie guarantee presne-once execution.

Controller môže:

- vytvoriť Job mierne neskôr,
- vynechať príliš starý missed schedule podľa deadline,
- po recovery vytvoriť chýbajúci Job,
- v určitých failure/race situáciách vytvoriť viac než jeden Job pre logical schedule.

Job logic preto musí byť idempotentná a mala by používať logical schedule identity.

## 16. Concurrency policy

### `Allow`

Nový Job môže začať aj keď predchádzajúci stále beží.

### `Forbid`

Nový scheduled run sa nespustí, ak predchádzajúci ešte beží.

### `Replace`

Aktívny Job sa nahradí novým scheduled Jobom.

`Replace` nie je safe resume. Starý process môže mať čiastočné side effects a nový začne odznova.

## 17. Starting deadline

```yaml
spec:
  startingDeadlineSeconds: 300
```

Určuje, ako dlho po plánovanom čase môže controller ešte považovať run za oprávnený na vytvorenie.

Príliš krátky deadline môže vynechať runs pri krátkom control-plane incidente. Príliš dlhý môže po obnove spustiť zastaranú prácu, ktorá už nedáva business zmysel.

## 18. Suspend CronJobu

```yaml
spec:
  suspend: true
```

Zabráni vytváraniu budúcich Jobs. Už existujúce Jobs sa tým automaticky nemusia zastaviť.

Po resume sa missed schedules môžu vyhodnotiť podľa deadline a controller semantics. Pred resume over možný backlog.

## 19. History limits

```yaml
spec:
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 5
```

Limity kontrolujú počet zachovaných Job objektov na CronJob, nie dlhodobú observability retention.

Failure Jobs zvyčajne potrebuješ držať dlhšie než úspešné, ale logs a results musia ísť do external systému.

## 20. Time zones a daylight saving

Business schedule v lokálnom časovom pásme môže pri DST:

- preskočiť neexistujúci čas,
- zopakovať rovnaký lokálny čas,
- meniť UTC offset.

Pre infraštruktúrne tasks preferuj UTC. Ak business požiadavka vyžaduje lokálne pásmo, zdokumentuj DST behavior a deduplication key.

## 21. Exactly-once neexistuje automaticky

Kubernetes Job/CronJob neposkytujú end-to-end exactly-once business transaction.

Pre bezpečnosť používaj:

- idempotency key,
- unique database constraint,
- transactional outbox/inbox,
- checkpoint/ledger,
- compare-and-set,
- distributed lock s fencingom, ak je naozaj potrebný,
- external work queue s acknowledgment semantics.

Lock bez expiry/fencing môže po failure vytvoriť stuck alebo split-brain spracovanie.

## 22. Batch resource planning

Batch workload môže vyčerpať cluster rýchlejšie než dlhodobé služby.

Kontroluj:

- `parallelism`,
- requests/limits,
- namespace quota,
- PriorityClass,
- topology a data locality,
- API object burst,
- image pull bandwidth,
- external database/API limits,
- completion cleanup.

CronJoby spúšťané v rovnakej minúte môžu vytvoriť thundering herd.

## 23. Secrets a identity

Každý Job Pod potrebuje:

- scoped ServiceAccount,
- least-privilege RBAC,
- short-lived workload identity,
- secrets mimo image-u,
- auditovaný external access,
- network policy.

CronJob manifest môže dlhodobo existovať, preto doň nepatrí static credential s nekontrolovanou životnosťou.

## 24. Observability

```bash
kubectl get jobs
kubectl describe job <job>
kubectl get cronjobs
kubectl describe cronjob <cronjob>
kubectl get jobs --selector=job-name=<name>
kubectl get pods -l job-name=<job>
kubectl logs job/<job>
kubectl get events --sort-by=.metadata.creationTimestamp
```

Sleduj:

- scheduled timestamp a creation time,
- active/succeeded/failed counts,
- retries a duration,
- exit codes a termination reasons,
- missed schedules,
- concurrency policy decisions,
- queue lag alebo processed item count,
- duplicate/business idempotency metrics.

## 25. Failure scenáre

### Job stále vytvára nové Pody

Application opakovane zlyháva a retry budget ešte nebol vyčerpaný. Over exit code, logs, backoff, config a external dependency.

### Job je Complete, ale business výsledok chýba

Exit code 0 neznamenal commit výsledku. Oprav application success contract a result verification.

### Job je Failed po deadline

Rozlišuj timeout, scheduling delay, slow processing, deadlock a external outage.

### CronJob nevytvoril Job

Over `suspend`, schedule/timeZone, starting deadline, controller availability, Events a príliš veľa missed schedules.

### CronJob vytvoril duplicitné spracovanie

Je to možný distributed-scheduling failure mode. Použi logical run key a deduplication.

### `Forbid` stále vynecháva runs

Predchádzajúci Job trvá dlhšie než interval. Zmeň interval, optimalizuj workload alebo vedome zvoľ inú concurrency policy.

## 26. Anti-patterny

### Deployment pre batch task

Deployment reštartuje process, ktorý úspešne skončil; desired state je nepretržité bežanie, nie completion.

### Job pre dlhodobú službu

Completion/retry model nezodpovedá service availability.

### Neidempotentná migrácia s retry

Druhý pokus môže poškodiť čiastočne zmenený stav.

### `concurrencyPolicy: Allow` bez analýzy

Súbežné runs môžu meniť tie isté dáta.

### Cron schedule bez explicitného time zone contractu

Výsledok sa mení podľa konfigurácie alebo DST očakávaní.

### TTL cleanup bez external logs/results

Incident evidence zmizne spolu s Jobom a Podmi.

### Vysoký parallelism bez downstream limitov

Batch spôsobí self-inflicted outage databázy alebo API.

## 27. Kontrolné otázky

1. Aký desired state udržiava Job?
2. Ako sa líši `parallelism` od `completions`?
3. Čo mení `restartPolicy: OnFailure` oproti `Never`?
4. Prečo môže byť task vykonaný viackrát?
5. Načo slúži Indexed Job?
6. Ako sa líši active deadline od application timeoutu?
7. Čo TTL controller odstraňuje?
8. Aké sú CronJob concurrency policies?
9. Prečo CronJob negarantuje exactly-once?
10. Ako navrhneš bezpečný scheduled database cleanup?

## Glossary impact

Relevantné pojmy: Job, CronJob, Job completion, `parallelism`, `completions`, Indexed Job, completion index, `backoffLimit`, active deadline, suspended Job, Pod failure policy, TTL-after-finished, Cron schedule, concurrency policy, starting deadline, Job history limit a idempotent batch execution.

## Oficiálna dokumentácia

- [Jobs](https://kubernetes.io/docs/concepts/workloads/controllers/job/)
- [CronJobs](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/)
- [Automatic cleanup for finished Jobs](https://kubernetes.io/docs/concepts/workloads/controllers/ttlafterfinished/)
