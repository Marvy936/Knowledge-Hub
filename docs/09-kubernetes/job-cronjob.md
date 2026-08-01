# Job a CronJob

Job riadi konečný workload, ktorý má dosiahnuť completion. CronJob vytvára Jobs podľa časového plánu. Na rozdiel od Deploymentu nie je cieľom udržiavať nekonečne bežiacu repliku, ale zaznamenať, že definovaný počet úspešných Pod completions vznikol. Kubernetes však negarantuje exactly-once business side effect. Pod alebo Job sa môže zopakovať po zlyhaní, timeout-e alebo strate acknowledgementu.

V Atlas scenári používa `settlement-export` Job na odoslanie uzavretého denného batchu do externého finančného systému. CronJob ho plánuje každú noc. Externý export musí byť idempotentný podľa batch ID, pretože Kubernetes retry model sám nevie určiť, či provider prijal posledný request pred výpadkom.

## Job ako completion controller

Jednoduchý Job:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: settlement-export-20260801
  namespace: production
spec:
  backoffLimit: 4
  activeDeadlineSeconds: 1800
  template:
    metadata:
      labels:
        app: settlement-export
        batch-id: "20260801"
    spec:
      restartPolicy: Never
      containers:
        - name: exporter
          image: registry.example.com/atlas/settlement-export@sha256:export31
          args:
            - --batch-id=20260801
```

Job controller vytvára Pods a sleduje ich úspešné alebo neúspešné ukončenie. Job `Complete=True` znamená, že Kubernetes completion contract bol splnený. Neznamená, že external provider neskôr neodmietol dáta alebo že business ledger bol reconciled.

## Pod restart policy a Job retry

Job Pod používa `restartPolicy: Never` alebo `OnFailure`. Pri `Never` kubelet skončený container nereštartuje v tom istom Pode; Job controller môže vytvoriť nový Pod. Pri `OnFailure` môže kubelet reštartovať container v rovnakom Pod UID.

```text
container restart v Pode
≠ nový Pod attempt
≠ nový Job
```

Application idempotency musí pokrývať všetky relevantné retry vrstvy.

```bash
kubectl get job settlement-export-20260801 -n production -o yaml
kubectl get pods -n production -l job-name=settlement-export-20260801 -o wide
```

Pri diagnostike sleduj Pod UIDs, container restart count, exit codes a batch ID.

## `backoffLimit` a failed attempts

`backoffLimit` obmedzuje počet retry pokusov podľa Job semantics. Backoff chráni cluster pred tight failure loopom, ale nemení chybný business operation na bezpečnú.

Ak export request skončí timeoutom po tom, čo provider commitol batch, nový attempt musí najprv zistiť stav batch ID. Blind POST môže vytvoriť duplicate settlement.

Application môže používať:

```text
stable batch ID
+ provider idempotency key
+ read-after-timeout
+ local attempt ledger
+ reconciliation
```

Kubernetes Job status sám neobsahuje external transaction outcome.

## Completion count a parallelism

Job môže vyžadovať viac completions a spúšťať ich paralelne:

```yaml
spec:
  completions: 20
  parallelism: 4
```

Pri klasickom modeli Pods vykonávajú rovnakú template a aplikácia si musí bezpečne rozdeliť prácu. Indexed Job poskytuje stabilný completion index:

```yaml
spec:
  completionMode: Indexed
  completions: 20
  parallelism: 4
```

Index možno použiť na deterministický shard, napríklad `0..19`. Index nie je automatický data lock. Dva attempts rovnakého indexu môžu existovať v prechodnom alebo failure scenári, preto output potrebuje stable identity a compare-and-set alebo idempotentný zápis.

## Success policy a partial completion

Podľa podporovanej API verzie môže Job definovať success policy pre vybrané indexed completions. Taký contract je vhodný iba vtedy, keď business úloha skutočne nepotrebuje všetky shards. „Job successful“ musí zodpovedať aplikačnému acceptance modelu, nie iba pohodlnejšiemu ukončeniu.

## Pod failure policy

Niektoré exit codes znamenajú transient chybu, iné permanentnú validation chybu. Pod failure policy môže rozhodnúť, či konkrétny failure ignorovať, započítať alebo ukončiť Job podľa podporovanej API verzie.

Aplikácia by mala používať stabilné exit-code semantics:

```text
0  → úspech
10 → invalid immutable input, retry nepomôže
20 → transient dependency failure
30 → unknown external outcome, potrebuje reconciliation
```

Samotný Kubernetes policy model však nevykoná provider reconciliation; iba riadi Job retry/termination.

## Deadline

`activeDeadlineSeconds` obmedzuje celkový aktívny čas Jobu:

```yaml
spec:
  activeDeadlineSeconds: 1800
```

Po prekročení deadline Job skončí ako failed a aktívne Pods sa ukončia. External side effect, ktorý už prebehol, sa nevráti späť. Termination handling musí bezpečne zachovať checkpoint alebo umožniť nový idempotentný attempt.

Container-level timeout a Job-level deadline majú byť koordinované. Ak application request môže čakať dlhšie než zostávajúci grace budget, termination môže vzniknúť v najhoršom možnom bode.

## TTL a história

`ttlSecondsAfterFinished` môže automaticky odstrániť finished Job po určenom čase:

```yaml
spec:
  ttlSecondsAfterFinished: 86400
```

To znižuje API clutter, ale zároveň odstráni Pods a časť ľahko dostupného evidence. Dlhodobý audit exportu musí byť uložený mimo ephemeral Job objektu: batch ledger, logs, metrics a provider acknowledgement.

## CronJob plánuje Jobs

CronJob:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: settlement-export
  namespace: production
spec:
  schedule: "15 1 * * *"
  timeZone: "Europe/Bratislava"
  concurrencyPolicy: Forbid
  startingDeadlineSeconds: 900
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 5
  jobTemplate:
    spec:
      backoffLimit: 4
      template:
        spec:
          restartPolicy: Never
          containers:
            - name: exporter
              image: registry.example.com/atlas/settlement-export@sha256:export31
              args:
                - --business-date=$(BUSINESS_DATE)
```

`timeZone` musí byť podporovaná cieľovou Kubernetes verziou. Bez explicitnej zóny sa schedule interpretuje podľa controller contractu a cluster konfigurácie. Business date nesmie byť odvodený nejasne z lokálneho času Podu pri prechode letného času.

## Schedule time nie je start time

CronJob controller periodicky vyhodnocuje plán. Job môže vzniknúť neskôr pre control-plane výpadok alebo queue delay. `startingDeadlineSeconds` určuje, ako dlho sa zmeškané spustenie ešte považuje za eligible.

```text
scheduled instant
≠ Job creation timestamp
≠ Pod start time
≠ business data interval
```

Batch musí niesť explicitný business interval alebo batch ID. Inak oneskorený Job môže spracovať „dnešné“ dáta namiesto zmeškaného včerajšieho okna.

## Concurrency policy

`Allow` dovolí prekrývanie Jobs. `Forbid` nevytvorí nový Job, ak predchádzajúci stále beží. `Replace` ukončí aktívny Job a vytvorí nový.

`Forbid` nie je distributed lock nad externým systémom. Starý Pod môže byť partitioned alebo external operation môže pokračovať mimo Kubernetes. `Replace` môže prerušiť Job po external commit-e, ale pred lokálnym acknowledgementom.

Pre settlement export je potrebný application-level lease alebo idempotency key viazaný na business batch ID.

## Suspend

CronJob možno pozastaviť:

```bash
kubectl patch cronjob settlement-export -n production \
  --type=merge -p '{"spec":{"suspend":true}}'
```

Suspend zastaví plánovanie nových Jobs. Nezastaví už aktívny Job a nerevertuje external side effects. Pri incidente treba zvlášť contain existujúce attempts.

## Ručný Job z CronJob template

Na kontrolované spustenie možno vytvoriť Job z CronJobu:

```bash
kubectl create job --from=cronjob/settlement-export \
  settlement-export-manual-20260801 -n production
```

Taký Job musí dostať explicitný batch ID a nesmie kolidovať s plánovaným runom. Vytvorenie bez business inputu môže spracovať nesprávne obdobie.

## Pozorovanie a logs

```bash
kubectl get cronjob settlement-export -n production -o yaml
kubectl get jobs -n production -l app=settlement-export
kubectl get pods -n production -l job-name=<job-name>
kubectl logs -n production job/<job-name> --all-containers=true
```

Pri viacerých Pod attempts agregovaný `kubectl logs job/...` nemusí nahradiť per-attempt evidence. Zachovaj Pod UID, timestamps, exit code, batch ID a provider request ID.

## Incident: CronJob spustil rovnaký batch dvakrát

Control plane bol krátko nedostupný a CronJob controller po obnove vytvoril zmeškaný Job. Operátor medzitým spustil manuálny Job pre rovnaký business date. Oba mali iné Kubernetes mená, ale rovnaký data interval.

`concurrencyPolicy: Forbid` nepomohol, pretože manuálny Job nebol child rovnakého CronJob active listu v okamihu rozhodnutia a oba začali takmer súčasne. Externý provider dostal duplicate batch.

Recovery použila provider idempotency key a reconciliation ledger. Skorší control zaviedol stable batch ID, application lock a audit, ktorý odmietne druhý aktívny attempt bez ohľadu na Kubernetes Job meno.

## Incident: Job bol Complete, ale export nebol prijatý

Exporter zapísal output do object storage a skončil s exit code 0. Asynchrónny downstream importer neskôr súbor odmietol pre schema chybu. Kubernetes Job zostal `Complete=True`.

Job splnil svoj definovaný process completion contract, ale contract bol príliš plytký. Oprava pridala bounded downstream acknowledgement alebo samostatný reconciliation Job a business status mimo Kubernetes Job condition.

## Incident: Replace ukončil proces po external commite

Dlhý Job prekryl ďalší schedule. `concurrencyPolicy: Replace` starý Job ukončila. Starý process už odoslal settlement providerovi, ale nestihol zapísať local acknowledgement. Nový Job poslal batch znova.

Oprava zmenila external operation na idempotentnú a pred každým retry vykonala status read-back. Replace policy zostala iba ako runtime control, nie correctness mechanizmus.

## Model, ktorý si treba odniesť

Job riadi Pod completions a retries. CronJob vytvára Jobs podľa plánovaných instantov. Ani jeden negarantuje exactly-once business side effect. Bezpečný batch systém potrebuje stabilnú business identity, idempotency, checkpoint, unknown-outcome reconciliation a audit nezávislý od TTL Kubernetes objektov.

## Referencie

- [Jobs](https://kubernetes.io/docs/concepts/workloads/controllers/job/)
- [CronJobs](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/)
- [Automatic Cleanup for Finished Jobs](https://kubernetes.io/docs/concepts/workloads/controllers/ttlafterfinished/)
