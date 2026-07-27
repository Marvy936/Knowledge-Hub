# Hooks

Helm hook je Kubernetes resource spustený v konkrétnom bode release lifecycle. Jeho účelom nie je „vykonať niečo pred alebo po deploymente“ všeobecne, ale uskutočniť presne identifikovanú operáciu, ktorej výsledok môže meniť Kubernetes aj externý durable state.

Hook preto nie je iba template annotation. Je to imperative operation boundary vložená do deklaratívneho release procesu. Musí mať vlastnú identitu, idempotency model, timeout, evidence, recovery a cleanup contract.

## 1. Dominantný lifecycle

```text
release operation intent a side-effect contract
→ rendered hook inventory
→ lifecycle point a ordering
→ Kubernetes API create/update
→ Job/Pod execution alebo non-workload API load
→ external/durable operation commit
→ Helm hook readiness verdict
→ release continuation alebo failure
→ evidence retention
→ retry, compensation alebo recovery
→ cleanup a closure
```

Kritická hranica je medzi:

```text
hook resource accepted
hook workload completed
external side effect committed
Helm release status recorded
```

Tieto stavy nemusia nastať naraz. Ak sa operácia commitne v databáze, ale Job alebo Helm klient stratí výsledok, ďalší retry nesmie predpokladať, že operácia neprebehla.

## 2. Atlas hook subject

Pre Atlas Payments pokračujeme v release chaine:

```text
chart artifact: CH57
dependency lock: D57
values bundle: V57
rendered manifest: M57
current release: payments-prod revision 18
target operation: upgrade na revision 19
```

Pre-upgrade migration hook identifikujeme ako:

```text
release: payments-prod
source revision: 18
target revision: 19
hook lifecycle point: pre-upgrade
rendered hook digest: HK57
Job UID: J57
Pod attempts: P57a, P57b
operation ID: atlas-payments/schema-expand/19
source schema generation: S12
target schema generation: S13
```

Bez operation ID, Job UID a durable schema evidence je výraz „migration hook už bežal“ nepresný.

## 3. Annotation a lifecycle point

Resource sa stane hookom cez annotation:

```yaml
metadata:
  annotations:
    helm.sh/hook: pre-upgrade
```

Bežné lifecycle points:

- `pre-install` a `post-install`;
- `pre-upgrade` a `post-upgrade`;
- `pre-rollback` a `post-rollback`;
- `pre-delete` a `post-delete`;
- `test`.

Hook timing určuje, kedy Helm resource načíta a kedy čaká na jeho readiness. Neurčuje však application compatibility.

Napríklad:

```text
pre-upgrade migration dokončí schema S13
→ staré Pody revision 18 ešte stále bežia
→ stará aplikácia musí vedieť čítať S13
```

Ak nevie, správne zoradený hook aj tak vytvorí outage.

## 4. Hook inventory vzniká renderovaním

Hooks sú templates. Pred execution prechádzajú rovnakým render chainom ako bežné resources:

```text
chart + dependencies + effective values + release context
→ rendered hook resources
→ hook type, weight, name, image, RBAC a arguments
```

Pred upgrade preto archivuj:

```bash
helm get hooks payments-prod -n production
helm template payments-prod ./chart -f values-production.yaml
```

Kontroluj najmä:

- hooks z parent chartu aj dependencies;
- image digest;
- ServiceAccount a RBAC;
- lifecycle point a weight;
- resource requests, deadline a retry policy;
- operation ID a external target;
- delete policy a TTL.

Subchart hooks sú súčasťou rovnakého release execution surface. Top-level chart ich nemôže všeobecne ignorovať.

## 5. Ordering a hook weights

Hook weight:

```yaml
metadata:
  annotations:
    helm.sh/hook-weight: "-10"
```

Nižšia hodnota sa vykoná skôr. Typický malý graph:

```text
-20: dedicated ServiceAccount a RBAC
-10: precondition Job
  0: migration Job
 10: verification Job
```

Weight poskytuje ordering, nie workflow correctness.

Ak správnosť vyžaduje rozsiahly graph s podmienkami, paralelizmom, retry politikou, manual approval a compensation, operácia už pravdepodobne patrí do samostatného workflow engine-u alebo deployment stage-u.

## 6. Readiness semantics

### Job alebo Pod hook

Helm čaká na úspešné completion. Neúspech zablokuje alebo zlyhá release operation.

```text
API create
→ scheduling
→ image pull
→ container execution
→ exit status
→ Job/Pod completion
→ Helm readiness verdict
```

### Ostatné resource kinds

ConfigMap, Secret, Role alebo podobný resource môže byť považovaný za ready po úspešnom API load-e.

```text
ConfigMap created
≠ consumer mounted current generation
≠ process reloaded configuration
≠ business operation completed
```

Business operácie preto modeluj ako completion-oriented Job s explicitným durable resultom.

## 7. Hook Job contract

Príklad:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: payments-migrate-{{ .Release.Revision }}
  labels:
    app.kubernetes.io/instance: {{ .Release.Name }}
    atlas.example.com/operation-id: "schema-expand-{{ .Release.Revision }}"
  annotations:
    helm.sh/hook: pre-upgrade
    helm.sh/hook-weight: "0"
    helm.sh/hook-delete-policy: before-hook-creation,hook-succeeded
spec:
  backoffLimit: 1
  activeDeadlineSeconds: 600
  ttlSecondsAfterFinished: 86400
  template:
    spec:
      restartPolicy: Never
      serviceAccountName: payments-migration
      containers:
        - name: migrate
          image: registry.example.com/payments-migrate@sha256:...
          args:
            - expand
            - --operation-id=atlas-payments/schema-expand/{{ .Release.Revision }}
```

Contract musí definovať:

```text
exact operation ID
source a target state
idempotency/fencing mechanism
success oracle
retry boundary
timeout
credentials a authority
logs a durable audit result
cleanup a retention
```

Exit code 0 má nasledovať až po durable commit-e a overení očakávaného state-u.

## 8. Idempotency a unknown outcome

Helm operation môže byť prerušená po side effecte, ale pred úspešným release statusom:

```text
migration transaction commitne S13
→ API response alebo Pod status sa stratí
→ Helm timeoutuje
→ release revision 19 je failed/pending
→ operator nevie, či migration prebehla
```

Správny hook pri retry:

1. načíta durable migration ledger;
2. vyhľadá operation ID `atlas-payments/schema-expand/19`;
3. overí výslednú schema generation;
4. ak je výsledok complete a zhodný, skončí ako no-op success;
5. ak je partial, vykoná bounded resume alebo explicitnú compensation;
6. ak je stav neznámy, zastaví sa a neaplikuje side effect druhýkrát.

Exactly-once execution neposkytuje Helm, Job controller ani `backoffLimit`.

## 9. Concurrency a fencing

Dve pipeline-y môžu spustiť rovnaký alebo susedný release naraz.

Potrebné controls:

```text
single authoritative release writer
+ CI/CD concurrency lock
+ external operation lock/fencing token
+ unique operation ID
+ state-aware retry
```

Helm release metadata sama nechráni databázu, queue ani external API pred duplicate side effectom.

Pre databázovú migráciu môže byť autoritou:

- migration table s unique operation ID;
- advisory lock;
- compare-and-set nad schema generation;
- fencing epoch pre stateful writera.

## 10. Database migration lifecycle

Bezpečný model:

```text
expand kompatibilnú schema
→ deploy tolerant readers/writers
→ bounded backfill alebo dual-write
→ verify current consumers
→ contract v neskoršom release
```

Blocking `pre-upgrade` migration je prijateľná iba keď:

- je bounded;
- nevytvorí nekompatibilitu so starou cohortou;
- lock neodstaví všetky replicas;
- rollback/roll-forward hranica je známa;
- operation je idempotentná;
- credentials a resource usage sú obmedzené.

Dlhá data migration nepatrí do hooku, ak release timeout alebo retry nie sú vhodný orchestration model.

## 11. Backup hook nie je restore guarantee

Úspešný backup hook musí preukázať:

```text
source data generation
→ application-consistent capture
→ encrypted off-cluster artifact
→ integrity metadata
→ retention
→ restore compatibility
→ testovaný restore path
```

Samotný vznik súboru alebo snapshot ID nie je recovery verdict.

Failed upgrade nesmie automaticky spustiť restore starého backupu bez porovnania current data generation. Taký restore by mohol prepísať novšie platné dáta.

## 12. RBAC a secret boundary

Hook Job často potrebuje širšie oprávnenia než runtime application. To zvyšuje blast radius chartu.

Používaj:

- dedicated ServiceAccount;
- namespaced Role/RoleBinding, ak cluster scope nie je nutný;
- minimálne verbs a resources;
- short-lived workload identity pre external systems;
- `automountServiceAccountToken: false`, keď Kubernetes API netreba;
- immutable image digest;
- redaction-aware logs.

Secret nesmie skončiť v:

- hook name alebo annotation;
- command-line argumente;
- Helm error message;
- rendered debug outpute;
- retained Job manifeste;
- central logs.

## 13. Timeout layers

Rozlišuj:

```text
application/external operation timeout
Job activeDeadlineSeconds
container retry/backoff
Helm operation timeout
pipeline timeout
```

Helm timeout je observation deadline, nie dôkaz, že side effect neprebehol.

Pred retry vždy over:

- Job UID a attempts;
- operation ledger;
- target schema alebo external object;
- current release status;
- live workload generation.

## 14. Cleanup a evidence retention

Hook resources nie sú bežný release inventory. `helm uninstall` ich nemusí odstrániť.

Delete policy:

```yaml
helm.sh/hook-delete-policy: before-hook-creation,hook-succeeded
```

Možnosti:

- `before-hook-creation`;
- `hook-succeeded`;
- `hook-failed`.

Kubernetes Job TTL je samostatný cleanup mechanizmus.

Navrhni retention tak, aby:

```text
failed evidence prežila incident diagnosis
central logs prežili resource deletion
successful resources nezostali bez limitu
manual cleanup mal ownera a runbook
```

`hook-failed` môže odstrániť presne tú evidence, ktorú potrebuješ pri incidente.

## 15. GitOps a deployment-engine boundary

Helm CLI, GitOps controller a iný deployment engine nemusia interpretovať hooks identicky.

Pre každý engine over:

```text
hook annotation support
ordering
retry
timeout
health/readiness
garbage collection
release-history ownership
```

Chart, ktorý funguje cez Helm CLI, nemusí mať rovnaký lifecycle v GitOps systéme. Engine identity je súčasť release subjectu.

## 16. Worked incident — migration commitla, release je failed

Atlas Payments upgrade revision 19 skončí po 15 minútach ako failed. Migration Job už neexistuje, pretože delete policy a krátky TTL odstránili Pod aj Job.

Business symptom:

```text
nový rollout sa nespustil
Helm revision 19 je failed
schema dashboard ukazuje S13
operator zvažuje opakovať upgrade
```

### Subject

```text
release payments-prod
source revision 18
target revision 19
rendered hook digest HK57
operation ID atlas-payments/schema-expand/19
expected S12 → S13
```

### Konkurenčné hypotézy

1. hook sa nikdy nespustil;
2. Job bol Pending alebo admission-denied;
3. container zlyhal pred commitom;
4. migration commitla, ale Job completion sa stratila;
5. migration commitla a verification krok zlyhal;
6. iný writer zmenil schema na S13;
7. retry už vykonal operáciu druhýkrát;
8. cleanup odstránil jedinú lokálnu evidence.

### Diskriminačné observation points

```text
helm history/status/get hooks
Kubernetes Events a audit
central Job/Pod logs
migration ledger podľa operation ID
DB schema generation a migration checksum
release writer/pipeline concurrency records
```

Finding:

```text
migration ledger: operation ID complete
schema: S13 s očakávaným checksumom
central logs: transaction commit success
Job evidence: odstránená pred incident review
Helm: timeout pred uložením successful hook verdictu
```

### Containment

- zastaviť automatické retry;
- ponechať revision 18 workload cohortu;
- zabrániť ďalšiemu schema writerovi;
- zachovať release, audit a DB evidence;
- neobnovovať databázu ani nemaž release Secrets.

### Recovery

1. overiť kompatibilitu revision 18 so schema S13;
2. upraviť hook tak, aby rovnaký operation ID rozpoznal complete state;
3. predĺžiť failed evidence retention;
4. spustiť controlled retry revision 19;
5. hook vykoná no-op verification, nie druhú migration;
6. pokračovať rolloutom a post-upgrade validation.

### Verification

```text
jedna migration ledger entry
schema S13 s očakávaným checksumom
revision 19 deployed
nové Pody používajú image I57
payment request P-884 prejde presne raz
starý operation ID už nevytvorí side effect
```

### Earlier control

- durable operation ledger;
- idempotent migration;
- release concurrency lock;
- central logs;
- failed Job retention;
- compatibility test S12/S13 × old/new app;
- chaos test straty response po commit-e.

## 17. Failure boundaries

### Non-Job hook je „ready“, consumer ešte nie

Secret hook sa vytvorí, ale application process stále používa starý credential. API acceptance nie je process-loaded verification.

### Hook s broad authority

Dependency pridá pre-upgrade hook s `cluster-admin`. Chart dependency upgrade tak rozšíri cluster takeover capability bez zmeny application runtime RBAC.

### Static Job name

Predchádzajúci failed Job zostane a ďalší release zlyhá na `AlreadyExists`. Naming, delete policy a retry identity musia byť navrhnuté spolu.

### Automatic rollback po migration

Helm obnoví manifests revision 18, ale schema ostane S13. Bez backward compatibility je Helm technicky deployed a aplikácia funkčne broken.

### Pre-delete hook ako jediná ochrana dát

Namespace alebo PVC môže byť odstránený mimo Helm uninstall lifecycle. Kritická retention policy musí existovať v storage/platform control plane.

## 18. Referenčný operation checklist

Pred prijatím hooku over:

```text
[ ] exact lifecycle point a engine semantics
[ ] rendered hook inventory vrátane dependencies
[ ] operation ID a authoritative target state
[ ] idempotency, lock a unknown-outcome behavior
[ ] image digest, ServiceAccount a RBAC
[ ] requests, limits, deadline a retry
[ ] external side-effect audit
[ ] compatibility starej a novej application cohorty
[ ] delete policy, TTL a central evidence
[ ] rollback/roll-forward/compensation runbook
[ ] original aj forbidden outcome test
```

## 19. Kontrolné otázky

1. Ktoré štyri stavy oddeľuje hook operation boundary?
2. Prečo Helm timeout nepreukazuje, že migration neprebehla?
3. Ako sa líši readiness Job hooku od readiness ConfigMap hooku?
4. Prečo hook potrebuje durable operation ID?
5. Ktoré controls zabránia duplicate side effectu pri concurrent upgrades?
6. Prečo delete policy a Job TTL nie sú to isté?
7. Kedy už migration nepatrí do Helm hooku?
8. Ako subchart hook mení release trust a authority surface?
9. Prečo automatic rollback nevracia durable external state?
10. Aké forbidden outcomes overíš po recovery?

## Glossary impact

Relevantné pojmy: Helm hook operation subject, rendered hook inventory, hook execution attempt, external side-effect commit, unknown hook outcome, hook readiness boundary, durable operation ledger, hook fencing, hook evidence-retention contract, subchart hook authority a hook recovery verdict.

## Oficiálna dokumentácia

- [Chart Hooks](https://helm.sh/docs/topics/charts_hooks/)
- [Chart Tests](https://helm.sh/docs/topics/chart_tests/)
- [`helm get hooks`](https://helm.sh/docs/helm/helm_get_hooks/)
- [`helm test`](https://helm.sh/docs/helm/helm_test/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Chart dependencies](chart-dependencies.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Upgrade a rollback →](upgrade-rollback.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
