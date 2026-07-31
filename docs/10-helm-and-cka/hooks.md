# Hooks

Helm hook je Kubernetes resource spustený v konkrétnom bode release lifecycle-u. Nie je to iba annotation ani všeobecný „skript pred deployom“. Predstavuje imperative operation boundary vloženú do deklaratívneho release procesu a môže meniť Kubernetes, databázu, secret provider alebo iný external durable state.

Preto potrebuje vlastnú identitu, authority, idempotency, timeout, evidence a recovery contract. Úspešné vytvorenie Jobu, jeho completion, commit external side effectu a zápis successful Helm statusu sú štyri odlišné udalosti. Ak sa medzi nimi stratí response alebo process zlyhá, opakovanie release-u nesmie predpokladať nulový výsledok.

## 1. Dominantný hook lifecycle

Hook začína release operation intentom a exact side-effect contractom. Chart a dependencies vytvoria rendered hook inventory, Helm zoradí resources podľa lifecycle pointu a weightu, Kubernetes spustí workload a ten prípadne commitne durable operation. Až potom môže Helm pokračovať release-om.

```text
release intent a side-effect contract
→ rendered hook identity a inventory
→ lifecycle point, weight a execution engine
→ API acceptance a Job/Pod attempt
→ durable alebo external operation
→ success read-back a Helm verdict
→ release continuation alebo failure
→ evidence retention
→ retry, resume, compensation alebo recovery
→ cleanup a closure
```

Critical distinction je medzi `resource accepted`, `workload completed`, `side effect committed` a `release status recorded`. Tieto states nemusia nastať naraz. Hook design musí vedieť bezpečne pokračovať po každej možnej prerušenej transition.

## 2. Exact Atlas hook subject

Atlas Payments prechádza z release revision 18 na 19. Používa chart `CH57`, dependency lock `D57`, values `V57` a manifest `M57`. Pre-upgrade hook má expandovať database schema zo `S12` na `S13`.

Exact operation subject zahŕňa release name, source a target revision, lifecycle point, rendered hook digest `HK57`, Job UID `J57`, Pod attempts `P57a/P57b`, immutable image digest, execution ServiceAccount, operation ID `atlas-payments/schema-expand/19`, source/target schema generation a expected checksum.

Operation ID je dôležitejší než Job name. Job môže byť zmazaný alebo recreated, ale durable ledger musí stále vedieť, či presne táto schema transition nezačala, prebieha, commitla, skončila partial alebo bola už úspešne overená.

## 3. Lifecycle points a ordering

Annotations ako `pre-install`, `post-install`, `pre-upgrade`, `post-upgrade`, rollback/delete hooks a `test` určujú, kedy Helm resource načíta a na čo čaká. Neurčujú application compatibility. Pre-upgrade migration môže korektne dokončiť schema S13, zatiaľ čo revision 18 Pody stále bežia. Ak stará application nevie S13 čítať, správne zoradený hook vytvorí outage.

Weights poskytujú deterministic ordering medzi hooks rovnakého lifecycle pointu, napríklad RBAC, precondition, migration a verification Job. Nevytvárajú workflow transaction ani conditional compensation. Ak correctness vyžaduje rozsiahly graph, manual approvals, parallel branches alebo dlhé retries, operácia patrí skôr do deployment workflow-u alebo samostatného controlleru.

## 4. Rendered inventory a execution authority

Hooks sú normálne templates a prechádzajú rovnakým chart, dependency, values a helper graphom ako bežné resources. Dependency môže pridať vlastný hook a tým rozšíriť release authority bez zmeny parent application runtime RBAC.

Pred release sa preto evidujú všetky parent a subchart hooks, ich type, names, lifecycle point, weight, image digest, args, ServiceAccount/RBAC, resources, deadline, retry policy, operation ID, external target, delete policy a TTL. `helm get hooks` nad current release a exact target render umožnia porovnať old a new operation surface.

Hook s `cluster-admin`, broad cloud credentialom alebo plaintext secretom v args mení trust model celého chartu. Execution identity má byť dedicated, least-privileged a short-lived. Kubernetes API token sa nemá mountovať, ak ho operation nepotrebuje, a logs ani annotations nesmú obsahovať secret payload.

## 5. Readiness a success semantics

Pri Job alebo Pod hooku Helm čaká na completion. Tento verdict však hovorí iba o workload status-e. Container exit code 0 má nasledovať až po durable commit-e a overení expected target state-u. Inak môže Job skončiť successful pred tým, než external system transition skutočne converguje.

Pri ConfigMap, Secret, Role alebo inom non-workload resource môže byť readiness iba successful API load. To nepreukazuje, že consumer načítal novú generation alebo že business operation funguje. Kritické operácie sa preto modelujú completion-oriented Jobom alebo explicitným controllerom, nie vytvorením configuration objectu.

Success oracle musí byť state-based. Migration hook nehlási úspech len preto, že SQL command skončil; read-backne schema generation a checksum. External registration hook overí provider object a correlation ID. Backup hook overí artifact integrity, retention a restore compatibility, nie iba existenciu snapshot ID.

## 6. Idempotency a unknown outcome

Helm timeout je observation deadline, nie dôkaz nulového side effectu. Migration môže commitnúť S13, následne sa môže stratiť Pod status alebo Helm process môže timeoutovať pred uložením successful revision verdictu. Release potom vyzerá failed alebo pending, hoci durable state už pokročil.

Bezpečný retry najprv načíta migration ledger podľa stable operation ID, overí target schema a checksum a podľa výsledku vykoná no-op success, bounded resume alebo explicitné stop/manual reconciliation. Ak je outcome unknown, side effect sa druhýkrát nespúšťa naslepo.

Exactly-once neposkytuje Helm, Job controller ani `backoffLimit`. Vzniká kombináciou unique operation ID, durable ledgeru, idempotentnej operation, compare-and-set alebo locku, state-aware read-backu a bounded retry. External provider request token alebo database unique constraint môže byť authoritative deduplication boundary.

## 7. Concurrency a fencing

Dve pipelines môžu spustiť susedné upgrades alebo rovnakú operation. Helm metadata nemusí zabrániť duplicate database, queue alebo provider side effectu. Produkčný model má jedného authoritative release writera, CI/CD concurrency lock, unique operation identity a external lock alebo fencing token.

Databázová migration môže používať advisory lock, unique ledger row alebo compare-and-set nad schema generation. Stateful writer transition môže vyžadovať fencing epoch. Lock musí chrániť samotnú external authority, nie iba pipeline process; in-memory mutex po worker restarte nestačí.

Pri concurrent conflict-e hook nemá pokračovať s najnovšou hodnotou „nejako“. Musí rozlíšiť same-operation retry od incompatible new operation a v druhom prípade zastaviť release truthful blockerom.

## 8. Database migration a compatibility

Bezpečný data lifecycle používa expand/contract. Najprv vznikne backward-compatible schema, následne sa nasadia tolerant readers/writers, vykoná bounded backfill a až po odstránení old consumers sa contract cleanup dokončí v neskoršom release.

Blocking pre-upgrade hook je vhodný iba pri krátkej, bounded a idempotentnej operation, ktorá neodstaví všetky replicas lockom a zostáva compatible so starou cohortou. Dlhý backfill, external workflow alebo irreversible migration sa nemá skrývať v Helm timeout/retry modeli.

Rollback chartu po migration nevráti schema. Recovery decision preto pozná old/new application × old/new schema matrix, writer fencing, rollback eligibility a roll-forward path. Automatic rollback po successful migration môže vytvoriť technicky deployed starú revision nad nekompatibilným S13.

## 9. Timeout, cleanup a evidence

Timeout layers zahŕňajú external operation deadline, Job `activeDeadlineSeconds`, container retry, Helm timeout a pipeline timeout. Každá meria inú boundary. Pred retry sa kontrolujú Job UID/attempts, durable ledger, current target state, release history a live workload generation.

Hook delete policy a Kubernetes Job TTL sú samostatné cleanup mechanisms. `before-hook-creation` rieši name reuse; `hook-succeeded` odstraňuje successful resource; `hook-failed` môže odstrániť presne tú evidence, ktorú incident potrebuje. Central logs a durable operation audit musia prežiť resource deletion.

Retention policy zachová failed evidence počas diagnosis window-u, successful resources odstráni bounded spôsobom a dá manual cleanup ownera. Static Job name bez správneho delete/retry contractu môže zablokovať ďalší release na `AlreadyExists`; generovanie nového name zasa nesmie vytvoriť novú operation identity pre rovnaký side effect.

## 10. Deployment engine boundary

Helm CLI, Argo CD, Flux alebo iný engine nemusia interpretovať hooks, ordering, retries, garbage collection a health rovnako. Engine identity je preto súčasť release subjectu. Chart, ktorý funguje pri `helm upgrade --wait`, nemusí mať identický lifecycle v GitOps controlleri.

Acceptance overuje exact engine semantics: ktoré annotations podporuje, kto vlastní release history, ako rieši timeout a retries a či hook resources podliehajú prune. Kritický side effect nemá závisieť na neurčitom preklade medzi Helm a iným engine-om.

## 11. Connected incident: migration commitla, revision zlyhala

Atlas upgrade revision 19 skončil po 15 minútach ako failed. Migration Job už neexistoval, pretože delete policy a krátky TTL odstránili Pod aj Job. Nový rollout sa nespustil, Helm hlásil failure, no schema dashboard ukazoval S13. Operator zvažoval opakovať upgrade.

Hypotézy zahŕňali hook, ktorý sa nikdy nespustil; Pending/admission failure; container failure pred commitom; commit so stratenou completion; successful migration s failed verification; iného schema writera; už vykonaný duplicate retry a cleanup, ktorý odstránil jedinú lokálnu evidence.

Helm history a hooks ukázali target revision a HK57, Kubernetes audit potvrdil Job creation a central logs zachytili transaction commit. Migration ledger obsahoval operation `atlas-payments/schema-expand/19` ako complete a database mala S13 s očakávaným checksumom. Helm timeout nastal pred uložením successful hook verdictu; cleanup odstránil Job evidence pred reviewom.

Containment zastavilo automatic retries a ďalšieho schema writera, ponechalo revision 18 cohortu a zachovalo release, audit, logs a DB evidence. Databáza sa neobnovovala a release Secrets sa nemažali.

Recovery najprv overila kompatibilitu revision 18 so S13. Hook dostal state-aware behavior: rovnaký operation ID rozpoznal complete ledger a vykonal iba no-op verification. Failed-resource retention sa predĺžila a controlled retry revision 19 pokračoval rolloutom bez druhej migration.

Acceptance potvrdila jednu ledger entry, S13 checksum, deployed revision 19, Pody s image I57, exactly-once payment `P-884` a negative test, že old operation ID už nevytvorí side effect. Chaos fixture straty response po commit-e následne overila rovnaký recovery path.

## 12. Failure patterns a operation checklist

Non-Job hook môže byť API-ready, kým consumer používa starú credential generation. Dependency hook môže pridať broad cluster authority. Automatic rollback môže vrátiť manifests, nie durable external state. Pre-delete hook nemôže byť jedinou ochranou dát, pretože namespace alebo PVC môže zmiznúť mimo Helm uninstall lifecycle-u.

Pred prijatím hooku sa overuje lifecycle point a engine, complete rendered inventory, operation ID a target state, idempotency/lock/unknown outcome, image a execution authority, requests/deadline/retry, external audit, old/new compatibility, retention, recovery runbook a positive aj forbidden outcomes.

Najčastejšie anti-patterny sú hook bez durable ID, exit 0 pred state verification, broad ServiceAccount, secret v args/logs, timeout interpretovaný ako no-op, delete policy odstraňujúca failed evidence, long migration v release timeout-e a rollback považovaný za external-state reversal.

## Kontrolné otázky

1. Ktoré štyri states oddeľuje hook operation boundary?
2. Prečo Helm timeout nepreukazuje, že side effect neprebehol?
3. Ako sa readiness Job hooku líši od API readiness ConfigMap hooku?
4. Prečo operation ID musí prežiť Job deletion a retry?
5. Ktoré locks a fencing controls chránia external authority?
6. Kedy migration ešte patrí do hooku a kedy už nie?
7. Ako delete policy, TTL a central logs spolu tvoria evidence contract?
8. Ktoré forbidden outcomes musí recovery vylúčiť?

## Executable lab: idempotentný `pre-upgrade` migration Job

Hook Job nesmie používať samotnú Helm revision ako jediný idempotency key, pretože retry alebo rollback vytvára ďalšie release transitions. Operation identity má reprezentovať business schema transition, napríklad `payments-schema-s13`.

Values definujú immutable operation subject:

```yaml
migration:
  operationId: payments-schema-s13
  image: ghcr.io/example/atlas-migrations@sha256:3333333333333333333333333333333333333333333333333333333333333333
```

Template `templates/hooks/schema-migrate.yaml`:

```gotemplate
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "atlas-payments.fullname" . }}-schema-migrate
  annotations:
    helm.sh/hook: pre-upgrade
    helm.sh/hook-weight: "-10"
    helm.sh/hook-delete-policy: before-hook-creation,hook-succeeded
spec:
  ttlSecondsAfterFinished: 3600
  backoffLimit: 1
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: migrate
image: {{ required "migration.image je povinný" .Values.migration.image | quote }}
args:
  - migrate
  - --operation-id
  - {{ required "migration.operationId je povinné" .Values.migration.operationId | quote }}
  - --target-schema
  - S13
```

Migration binary musí v databáze atomicky vytvoriť alebo načítať operation ledger row podľa `operationId`. Prvý attempt vykoná transition `S12 → S13`; ďalší attempt s rovnakým ID overí už dokončený výsledok a skončí bez druhého side effectu.

Pred upgrade-om vyrenderuj iba hook:

```bash
helm template payments-prod ./atlas-payments \
  -f values-prod.yaml \
  --show-only templates/hooks/schema-migrate.yaml
```

Upgrade spusti s explicitným operation ID:

```bash
helm upgrade payments-prod ./atlas-payments \
  -n payments \
  -f values-prod.yaml \
  --set migration.operationId=payments-schema-s13 \
  --wait \
  --timeout 10m
```

Počas incidentu nezisťuj hook iba cez `helm status`. Získaj rendered hook, Job state a log:

```bash
helm get hooks payments-prod -n payments
kubectl get job -n payments -l app.kubernetes.io/instance=payments-prod -o wide
kubectl logs -n payments job/payments-prod-atlas-payments-schema-migrate
```

Ak databáza ukazuje committed `payments-schema-s13`, ale Helm timeoutoval pred successful verdictom, slepý rollback ani nový operation ID nie sú bezpečné. Controlled retry s rovnakým ID musí skončiť ako no-op verification. Hook delete policy upratuje Kubernetes Job resource; nevracia databázový side effect.

Negatívny test spustí migration image s rovnakým operation ID druhýkrát v test databáze. Počet ledger rows aj schema transition musí zostať jeden. Bez tohto second-operation testu je „Job success“ iba first-run evidence.

## Glossary impact

Relevantné pojmy: Helm hook operation subject, rendered hook inventory, hook execution attempt, external side-effect commit, unknown hook outcome, durable operation ledger, hook fencing, hook readiness boundary, evidence-retention contract a hook recovery verdict.

## Primárne zdroje

- [Helm — Chart Hooks](https://helm.sh/docs/topics/charts_hooks/)
- [Helm — Chart Tests](https://helm.sh/docs/topics/chart_tests/)
- [Helm — `helm get hooks`](https://helm.sh/docs/helm/helm_get_hooks/)
- [Kubernetes — Jobs](https://kubernetes.io/docs/concepts/workloads/controllers/job/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Chart dependencies](chart-dependencies.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Upgrade a rollback →](upgrade-rollback.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
