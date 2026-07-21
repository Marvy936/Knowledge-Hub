# Hooks

Helm hook je Kubernetes resource template označený špeciálnou annotation, ktorý Helm vykoná v konkrétnom bode release lifecycle. Hook môže pripraviť alebo overiť release, spustiť migráciu, backup, cleanup alebo test. Zároveň však pridáva imperative a side-effectful krok do deklaratívneho deploymentu. Každý hook preto potrebuje idempotenciu, timeout, ownership, cleanup a recovery contract.

## 1. Hook annotation

Resource sa stane hookom cez:

```yaml
metadata:
  annotations:
    helm.sh/hook: pre-upgrade
```

Bez annotation je resource bežnou súčasťou release manifestu.

Jeden resource môže implementovať viac lifecycle bodov:

```yaml
helm.sh/hook: post-install,post-upgrade
```

## 2. Dostupné hooks

Bežné hodnoty:

- `pre-install`,
- `post-install`,
- `pre-upgrade`,
- `post-upgrade`,
- `pre-rollback`,
- `post-rollback`,
- `pre-delete`,
- `post-delete`,
- `test`.

Historický `crd-install` hook sa nepoužíva; CRDs majú osobitný `crds/` lifecycle.

## 3. Install lifecycle

Zjednodušený install flow:

```text
chart validation
→ CRDs z crds/
→ template render
→ pre-install hooks
→ bežné release resources
→ prípadné wait
→ post-install hooks
→ release result
```

Hook môže zablokovať celý Helm command. Ak Job alebo Pod hook zlyhá, release operation zlyhá.

## 4. Upgrade lifecycle

```text
render target revision
→ pre-upgrade hooks
→ update/create/delete release resources
→ prípadné wait
→ post-upgrade hooks
→ revision result
```

`pre-upgrade` prebehne pred aktualizáciou bežných resources. `post-upgrade` prebehne až po ich spracovaní a podľa wait modelu môže čakať na ready stav.

Hook timing nie je náhrada za application-level compatibility. Database migration musí podporovať súbeh starej a novej application revision podľa rollout modelu.

## 5. Rollback lifecycle

```text
render/retrieve rollback target
→ pre-rollback hooks
→ rollback release resources
→ post-rollback hooks
```

Rollback hook nie je automatická inverse operácia upgrade hooku. Ak pre-upgrade migrácia zmenila schema alebo external system, rollback manifestu nemusí vedieť túto zmenu bezpečne vrátiť.

Preferuj backward-compatible migrations a roll-forward recovery.

## 6. Delete lifecycle

`pre-delete` môže napríklad:

- odstrániť workload z external registry,
- vykonať controlled drain,
- exportovať metadata,
- validovať retention policy.

`post-delete` môže vykonať cleanup external integration.

Deletion hook nesmie byť jediný ochranný mechanizmus kritických dát. Operator môže resource alebo namespace odstrániť mimo Helm lifecycle.

## 7. Hook resource kinds

Najčastejší hook je `Job`:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "payments.fullname" . }}-migrate-{{ .Release.Revision }}
  annotations:
    helm.sh/hook: pre-upgrade
    helm.sh/hook-weight: "0"
    helm.sh/hook-delete-policy: before-hook-creation,hook-succeeded
spec:
  backoffLimit: 1
  activeDeadlineSeconds: 600
  template:
    spec:
      restartPolicy: Never
      serviceAccountName: {{ include "payments.migrationServiceAccount" . }}
      containers:
        - name: migrate
          image: {{ include "payments.image" . | quote }}
          args: ["migrate"]
```

Použiť možno aj ConfigMap, Secret, ServiceAccount, Role alebo iné Kubernetes resources. Pri non-Job resources však Helm readiness semantics nemusia znamenať, že naviazaný proces alebo controller dokončil business operáciu.

## 8. Ready semantics

Pre Job alebo Pod hook Helm čaká na úspešné dokončenie. Failure hooku zlyhá release operation.

Pri ostatných resource kinds môže byť resource považovaný za ready už po úspešnom API create/update. Napríklad vytvorený ConfigMap nepreukazuje, že ho workload načítal.

Pre business operáciu používaj completion-oriented Job s explicitným exit statusom.

## 9. Hook weight

```yaml
helm.sh/hook-weight: "-10"
```

Weights:

- musia byť string reprezentácia čísla,
- môžu byť záporné, nulové alebo kladné,
- nižšia hodnota sa vykoná skôr,
- pri rovnakom weight sa uplatnia ďalšie Helm ordering pravidlá.

Príklad:

```text
-20 → ServiceAccount/RBAC
-10 → precondition Job
  0 → migration Job
 10 → verification Job
```

Aj pri weightoch sa vyhýbaj zložitému hook orchestration graphu. Viac krokov môže patriť do jednej explicitnej workflow application alebo pipeline stage.

## 10. Hook delete policy

```yaml
helm.sh/hook-delete-policy: before-hook-creation,hook-succeeded
```

Hodnoty:

- `before-hook-creation`,
- `hook-succeeded`,
- `hook-failed`.

Bez explicitnej policy sa typicky používa `before-hook-creation` behavior.

Trade-off:

- zmazanie úspešného Jobu znižuje clutter,
- ponechanie failed Jobu zachová logs a evidence,
- stále potrebuješ central logs a audit,
- rovnaký názov bez cleanupu môže blokovať ďalší release.

## 11. Job TTL

Kubernetes Job môže používať:

```yaml
ttlSecondsAfterFinished: 3600
```

TTL controller je Kubernetes cleanup mechanizmus nezávislý od Helm hook delete policy.

Kombinácia musí byť vedomá:

- hook policy riadi cleanup počas Helm lifecycle,
- TTL čistí dokončený Job neskôr,
- príliš krátky TTL odstráni incident evidence,
- bez central logs môže byť diagnostika nemožná.

## 12. Hook resources nie sú bežný release inventory

Hook-created resources Helm aktuálne nespravuje rovnakým spôsobom ako bežné release resources. `helm uninstall` preto nemusí automaticky odstrániť hook Jobs, Secrets alebo RBAC objects.

Každý hook resource potrebuje:

- unique alebo reusable naming model,
- delete policy alebo TTL,
- owner/labels,
- manual cleanup runbook,
- retention decision.

`helm.sh/resource-policy: keep` používaj iba pri explicitnom durable ownership modeli; môže zanechať orphan resources.

## 13. Naming

Statický názov:

```yaml
name: payments-migration
```

môže pri ďalšom release kolidovať s predchádzajúcim Jobom.

Revision-specific názov:

```yaml
name: {{ include "payments.fullname" . }}-migrate-{{ .Release.Revision }}
```

zlepšuje traceability, ale vytvára viac objects a potrebuje cleanup.

Názov musí rešpektovať Kubernetes length/format limity a byť deterministický pre retry tej istej revision.

## 14. Idempotencia

Helm command môže byť:

- zopakovaný operatorom,
- retryovaný pipeline-om,
- prerušený po vykonaní side effectu, ale pred uložením úspešného release statusu,
- rollbacknutý,
- spustený súbežne z dvoch automation systémov.

Hook preto nesmie predpokladať exactly-once execution.

Idempotentná migration:

- pozná aktuálnu schema version,
- používa transaction/lock podľa databázy,
- bezpečne rozpozná už aplikovaný krok,
- má bounded retry,
- nezopakuje external billing/message side effect,
- ukladá audit result mimo ephemeral Jobu.

## 15. Concurrency control

Dva Helm upgrades alebo release automation runs môžu súperiť.

Controls:

- jeden release writer,
- CI/CD concurrency lock,
- database advisory lock,
- migration table/version lock,
- unique operation ID,
- safe retry semantics.

Helm release state lock sám osebe nemusí chrániť všetky external side effects hooku.

## 16. Database migrations

Najčastejší use case, ale aj najrizikovejší.

Bezpečný model:

```text
expand schema
→ deploy backward-compatible application
→ migrate/backfill data
→ over usage
→ contract schema v neskoršom release
```

`pre-upgrade` blocking migration je vhodná iba keď:

- downtime je akceptovaný alebo nevznikne incompatibility,
- operation je bounded,
- rollback model je známy,
- database lock neodstaví všetky replicas,
- Job resources a credentials sú obmedzené.

Dlhé data migrations často patria do samostatného riadeného workflowu, nie do Helm hooku.

## 17. Backup hook

Pre-upgrade backup Job môže byť užitočný, ale úspešný exit code musí preukázať:

- application-consistent snapshot,
- uloženie mimo cluster failure domain,
- encryption,
- retention,
- integrity metadata,
- restore compatibility.

„Backup file bol vytvorený“ nie je recovery guarantee. Hook by nemal automaticky obnovovať starý backup po failed upgrade bez explicitného rozhodnutia; mohol by zničiť novšie dáta.

## 18. Validation hook

Post-install/post-upgrade Job môže overiť:

- DNS/Service connectivity,
- základný API request,
- schema version,
- required dependency,
- release-specific invariant.

Nemá nahrádzať:

- readiness probe,
- continuous synthetic monitoring,
- integration tests v CI,
- SLO alerting.

Validation hook je release gate v konkrétnom okamihu.

## 19. Test hook

Resource s:

```yaml
helm.sh/hook: test
```

sa spustí cez:

```bash
helm test <release> -n <namespace>
```

Test Job má:

- používať least-privilege ServiceAccount,
- mať timeout a bounded retry,
- nemať deštruktívne side effects,
- generovať čitateľný exit status a logs,
- po sebe upratať podľa policy.

Detailné Helm testing patrí do samostatnej kapitoly.

## 20. RBAC a identity

Hook Job často potrebuje viac oprávnení než application runtime.

Nevhodné:

- reuse `cluster-admin`,
- mount default ServiceAccount token bez potreby,
- prístup ku všetkým Secrets,
- create/update CRDs z application namespace hooku.

Preferuj:

- dedicated ServiceAccount,
- namespaced Role/RoleBinding,
- explicitné verbs/resources,
- krátkodobé external credentials cez workload identity,
- `automountServiceAccountToken: false`, ak API netreba.

## 21. Secrets

Hook môže spracovať database credentials, backup keys alebo API tokens.

Riziká:

- command-line arguments viditeľné v process metadata,
- logs,
- Job manifest/release state,
- environment variables,
- failed Pod retained pre debugging,
- temporary files a dumps.

Secret nevkladaj do annotation, name, Helm error message ani hook output. Preferuj mounted Secret/external provider a redaction-aware tooling.

## 22. Resource limits a scheduling

Hook bez requests/limits môže:

- zostať Pending pre quota/LimitRange,
- byť OOMKilled počas migrácie,
- súperiť s production workloadom,
- spôsobiť Node pressure.

Nastav:

- requests/limits podľa load testu,
- node placement podľa data/network locality,
- tolerations iba podľa potreby,
- PriorityClass opatrne,
- `activeDeadlineSeconds`,
- `backoffLimit`.

Pre-upgrade hook blokujúci release potrebuje alerting pri Pending aj Running timeout-e.

## 23. Observability

Zaznamenaj:

- release name a revision,
- chart/app version,
- hook type a weight,
- Job UID,
- start/end UTC,
- exit status,
- operation/migration ID,
- affected schema/resource,
- retry count.

Príkazy:

```bash
helm get hooks <release> -n <namespace>
kubectl get jobs,pods -n <namespace> -l app.kubernetes.io/instance=<release>
kubectl logs job/<hook-job> -n <namespace>
kubectl describe job/<hook-job> -n <namespace>
```

Central logs musia prežiť hook cleanup.

## 24. Timeout a `--wait`

Helm command timeout zahŕňa blocking operations podľa command a wait semantics. Hook Job bez vlastného deadline môže čakať až do Helm timeoutu.

Navrhni dve hranice:

- Job `activeDeadlineSeconds`,
- Helm operation timeout s rezervou na API propagation a cleanup.

Timeout neznamená, že external side effect neprebehol. Pred retry over operation state.

## 25. Atomic release behavior

Flags ako atomic/cleanup behavior môžu ovplyvniť release remediation pri failure, ale nezvrátia automaticky external side effects hooku.

Príklad:

```text
pre-upgrade migration zmení databázu
→ Deployment rollout zlyhá
→ Helm rollbackne manifests
→ database schema zostane nová
```

Application a schema musia byť backward-compatible alebo mať explicitný recovery runbook.

## 26. Hooks a GitOps

GitOps controller typicky reconciliuje deklaratívne manifests; Helm hooks sú imperative lifecycle behavior konkrétnej Helm integrácie.

Over:

- či controller hooks podporuje alebo prekladá,
- rozdiel medzi Helm hook a controller-specific hook annotation,
- retry a health behavior,
- garbage collection,
- drift po ponechaných hook resources,
- kto vlastní release history.

Chart testovaný cez Helm CLI nemusí mať identické hook semantics v inom deployment engine.

## 27. Hooks v subcharts

Hooks deklarované dependency chartom sa tiež vyhodnocujú. Top-level chart ich nevie všeobecne ignorovať.

Pred dependency upgrade skontroluj:

```bash
helm template example ./chart | grep -n "helm.sh/hook"
```

Lepšie je analyzovať source charts a rendered hooks cez Helm commands, pretože annotation môže byť templated alebo viacriadková.

Subchart hook rozširuje release RBAC, timeout a side-effect surface.

## 28. CRDs nie sú hook orchestration

CRDs patria do osobitného lifecycle modelu. Helm ich spracúva pred templates z `crds/`, ale ich upgrades, conversion webhooks, data migration a deletion musia byť riadené explicitne.

Nepoužívaj hook Job na neoverenú delete/recreate CRD operáciu. Môže dôjsť k strate všetkých custom resources.

## 29. Anti-patterny

### Každý deployment používa mnoho sekvenčných hooks

Chart sa mení na skrytý workflow engine.

### Dlhá migrácia v `pre-upgrade`

Blokuje release, prekračuje timeout a komplikuje rollback.

### Hook bez idempotencie

Retry zopakuje side effects.

### `hook-succeeded,hook-failed` bez central logs

Všetka evidence sa okamžite zmaže.

### Hook s `cluster-admin`

Application chart získava cluster takeover capability.

### Automatický restore pri failed upgrade

Môže prepísať novšie alebo konzistentné dáta.

### Spoliehanie sa na uninstall cleanup

Hook resources nemusia byť súčasťou bežného release inventory.

### Static Job name bez delete policy

Ďalší release zlyhá na `AlreadyExists`.

## 30. Troubleshooting

### Release visí na hooku

Over Job/Pod phase, scheduling Events, image pull, RBAC, quota, PVC, logs, active deadline a Helm timeout.

### Hook Job zlyhal, ale Pod už neexistuje

Delete policy alebo TTL odstránili evidence. Použi central logs/audit a uprav retention.

### Ďalší upgrade hlási `AlreadyExists`

Predchádzajúci hook resource ostal. Over name, delete policy a bezpečnosť manual cleanupu.

### Migration prebehla, release je failed

Neopakuj ju naslepo. Over migration table/operation ID, schema a application compatibility.

### Uninstall zanechal hook resources

Je to očakávaná lifecycle hranica. Použi documented cleanup podľa labels a data-retention modelu.

### Hook funguje cez Helm CLI, ale nie cez GitOps

Porovnaj deployment engine hook semantics, service account, timeout, health a garbage collection.

## 31. Kontrolné otázky

1. Čo odlišuje hook resource od bežného release resource?
2. Ktoré lifecycle hooks sú dostupné?
3. Ako sa vyhodnocuje hook weight?
4. Čo znamená ready pre Job hook a pre ConfigMap hook?
5. Prečo hook resources nemusia byť odstránené pri uninstall-e?
6. Aký je rozdiel medzi hook delete policy a Job TTL?
7. Prečo migration hook potrebuje idempotenciu?
8. Ako hook failure interaguje s databázovým side effectom?
9. Prečo sú subchart hooks supply-chain riziko?
10. Kedy operácia už nepatrí do Helm hooku, ale do samostatného workflowu?

## Glossary impact

Relevantné pojmy: Helm hook, hook lifecycle point, hook weight, hook readiness, hook delete policy, `before-hook-creation`, `hook-succeeded`, `hook-failed`, hook Job, hook idempotency, hook side effect, test hook, hook resource retention a subchart hook.

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
