# Rollback a roll-forward

Rollback a roll-forward sú recovery strategies nad distribuovaným state-om. Rollback sa pokúša obnoviť posledný compatible runtime subject. Roll-forward vytvára nový opravený subject, ktorý rešpektuje state už vytvorený chybným release-om. Ani jedna strategy nie je synonymum pre zmenu image tagu; recovery musí inventarizovať application, configuration, traffic, feature, data, events, sessions a external side effects.

Najčastejší omyl je predpoklad, že previous ReplicaSet alebo artifact automaticky predstavuje safe recovery point. Old binary môže byť nekompatibilný s current schema, new event backlogom alebo provider operation state-om. Rozhodnutie musí byť per layer a current, nie uložené ako statický `rollbackAvailable=true` flag pred release-om.

## 1. Dominantný impact-to-recovery model

```text
user/business impact detected
→ stop new exposure a preserve evidence
→ exact affected release/cohort/operation subject
→ state-delta inventory od last accepted generation
→ last compatible state per layer
→ rollback / roll-forward / flag-off / compensation / restore eligibility
→ bounded recovery transition
→ controller/runtime/data read-back
→ original, forbidden a second-operation validation
→ reconciliation, retirement a control learning
```

Containment a recovery sú rozdielne. Containment znižuje ďalší harm a zachováva evidence. Recovery obnovuje authoritative state a business capability. Príliš rýchly rollback môže zničiť operation records potrebné na reconciliation.

## 2. Exact recovery subject

```yaml
recoverySubject:
  incident: INC-PAY-2026-071
  environmentGeneration: prod-eu-1844
  affectedReleaseManifest: sha256:release1000rc4
  previousAcceptedReleaseManifest: sha256:release993
  exposure:
    trafficGeneration: 1844
    ringProgramGeneration: payments-rings-v12
    flagGeneration: flag-pay-882
  data:
    schemaContract: settlement-schema-v42-expand
    backfillGeneration: backfill-pay-42-7
  events:
    producerContract: settlement-events-v18
    oldestUnconsumedGeneration: v18
  externalEffects:
    providerOperationsUnknown: 119
  candidateActions:
    applicationRollback: conditional
    trafficRollback: eligible
    flagOff: eligible
    databaseRollback: forbidden
    rollForward: eligible
    reconciliation: required
```

Recovery subject zachytáva current state. Rovnaký incident o desať minút môže mať inú eligibility, keď backlog alebo migration postúpili.

## 3. State-delta inventory

Pred mutation sa porovná last accepted state s current observed state:

```text
application artifacts a configs
traffic/ring/flag generations
database schema, rows a migrations
events emitted, queued a consumed
cache/session formats
secrets and credentials
external requests and acknowledgements
in-flight operations and ownership
```

Git diff ani Deployment history nepokrývajú runtime a external state. Inventory kombinuje release manifests, Kubernetes, database, broker, provider ledger a business records.

## 4. Immediate containment

Containment má byť bounded a reversible, pokiaľ je to možné:

```text
freeze progressive controller
→ stop new candidate assignments
→ route new operations na stable alebo maintenance path
→ disable high-risk feature
→ pause destructive backfill
→ preserve logs, events, generations a operation IDs
```

Existing candidate operations sa nesmú naslepo presunúť na stable, ak provider outcome je unknown. Potrebujú operation-level reconciliation.

## 5. Application rollback eligibility

Application rollback je eligible, ak previous binary/config vie pracovať s current:

- database schema a row semantics;
- event versions a backlog;
- session/cache formats;
- secrets/credential generations;
- provider/API contracts;
- feature/data state.

Praktický artifact read-back:

```bash
kubectl -n payments rollout history deployment/payments-api
kubectl -n payments get rs -l app=payments-api \
  -o json | jq '[.items[]|{name:.metadata.name,revision:.metadata.annotations["deployment.kubernetes.io/revision"],images:[.spec.template.spec.containers[].image]}]'
```

History a ReplicaSets preukazujú stored Deployment revisions a desired images. Nepreukazujú availability artifactu v registry, old configuration, data compatibility ani business safety.

## 6. Traffic rollback a feature disable

Traffic rollback môže zastaviť exposure bez zmeny runtime fleet. Flag-off môže deaktivovať behavior. Obe strategies sú rýchle, ak stable path zostáva compatible.

```text
route new operations na stable
+ freeze candidate in-flight
+ flag off new behavior
→ preserve candidate runtime pre diagnosis
```

Ak data write alebo event už používa new semantics, stable path môže ďalej čítať damaged/incompatible state. Recovery gate musí testovať actual operation, nie iba route resource.

## 7. Roll-forward

Roll-forward je vhodný, keď root cause je bounded a previous version nie je compatible alebo rollback blast radius je väčší. Fix vytvára nový candidate, nový artifact a fresh evidence; nepoužíva manual patch bez provenance.

```text
incident state and defect
→ minimal compatible source change
→ focused plus regression evidence
→ immutable fixed release
→ bounded canary
→ reconcile existing affected state
→ broad promotion
```

Urgency môže zúžiť evidence breadth, ale exact subject, supply-chain trust a recovery sa zachovávajú.

## 8. Compensation a reconciliation

External side effects sa často nedajú rollbackovať transakčne. Payment authorization môže byť voidnutá alebo refunded, no nejde o návrat času. Unknown outcome sa najprv query-ne providerom podľa stable operation identity.

```sql
SELECT operation_id, release_id, provider_idempotency_key,
       local_state, provider_state, last_attempt_at
FROM settlement_operations
WHERE incident_id = 'INC-PAY-2026-071';
```

Query preukazuje local records. Nepreukazuje provider truth. Reconciliation načíta provider ledger a vytvorí explicitný final verdict pre každý operation.

## 9. Database restore

Restore je recovery generation, nie undo DDL. Potrebuje writer fencing, consistency point, dependency recovery a reconciliation changes po recovered point-e. Restore môže mať väčší business data loss než roll-forward migration fix.

PITR alebo backup success nepreukazuje application correctness. Restored environment sa overí izolovane, potom sa plánuje cutover alebo selective data repair.

## 10. Unknown transition outcome

Route, migration alebo deployment command môže timeoutnúť po server-side commit-e. Pred retry sa číta authoritative state:

```bash
kubectl -n payments get trafficassignment payments-api -o json | jq '{generation:.metadata.generation,observed:.status.observedGeneration,effective:.status.effectiveWeights}'
```

Output preukazuje controller state, nie actual dataplane. Recovery decision potrebuje both control a data path observations. Blind inverse mutation môže oscillovať alebo prebiť novšiu emergency change.

## 11. Recovery validation

Validation musí overiť viac než health:

```text
original user journey succeeds
forbidden duplicate/lost/cross-tenant outcome absent
existing affected operations reconciled
new second operation succeeds
adjacent unaffected cohort remains healthy
backlog and capacity recover
recovery does not reintroduce defect
```

Second operation odhaľuje stale cache, session alebo idempotency state, ktoré first canary po recovery nemusí zachytiť.

## Ako vybrať rollback, roll-forward, compensation alebo restore

Recovery rozhodnutie sa robí po vrstvách. Application bytes možno vrátiť na starý digest, configuration na starú generation a traffic na stable route. Databázové rows, eventy a external provider side effects však nemusia byť reverzibilné rovnakým príkazom. „Rollback release“ preto nie je jedna univerzálna operácia.

Rollback je vhodný, keď stará generation zostala kompatibilná s aktuálnym shared state-om a návrat neporuší in-flight work. Roll-forward používa nový artifact alebo config, ktorý defect opraví bez návratu na nekompatibilný contract. Feature disable obmedzí behavior, compensation vytvorí domain operation rušiacu predchádzajúci side effect a restore obnoví data z recovery pointu s explicitnou stratou a reconciliáciou.

Timeout alebo stratená odpoveď vytvára unknown outcome. Blind retry môže vykonať druhú mutation. Najprv sa číta controller, route, database journal alebo provider operation status podľa stabilnej identity. Až observation určí, či treba pokračovať, kompenzovať alebo iba uzavrieť evidence.

Recovery eligibility sa má vyhodnotiť pred release-om. Manifest uvádza schema/event compatibility, last-known-good artifacts, restore assumptions a operations, ktoré nemožno automaticky vrátiť. Runbook potom nie je improvizovaný počas incidentu.

Verdikt sa uzatvára technickým, functional a business read-backom. Overí sa pôvodný failure, forbidden duplicate/loss outcome, backlog a druhá operácia. Návrat deployment statusu na green bez business reconciliation nie je dokončená recovery.

## 12. Connected incident `REL-PAY-71`

Atlas progressive controller videl latency alert a vykonal `kubectl rollout undo`. Application Pods sa vrátili na `payments-9.9.3`, ale feature flag generation 882 zostala enabled pre enterprise accounts a backfill pokračoval. New release už emitoval event v18 a prepísal 83 rows zo stale snapshotu. Old consumer nepoznal new enum.

```text
application rollback
→ traffic partially stable
→ feature still new
→ data/backfill still advancing
→ event backlog incompatible
→ external unknown operations retried
```

31 duplicate provider effects vzniklo po retries. Dashboard označil rollback za successful, pretože Deployment bol Available.

Root cause bol application-only recovery model nad multi-axis state-om.

## 13. Redesign a acceptance verdict

Redesign vytvára state-delta inventory a per-layer eligibility. Incident controller freeze-ne rollout, route-ne new work na stable, vypne flag, pause-ne version-safe backfill a reconciliuje provider operations. Application rollback sa vykoná až po event/schema compatibility checku; inak sa pripraví roll-forward consumer.

Recovery je prijatá iba vtedy, keď:

```text
affected subject/cohort/operations sú exact
+ volatile evidence je preserved
+ state delta pokrýva all control/data/external layers
+ each action má current eligibility
+ unknown outcomes sa read-backnú pred retry
+ external effects sa reconcile/compensate
+ application/runtime/data generations sa korelujú
+ original and forbidden outcomes sú overené
+ second operation and adjacent cohort prejdú
+ recovery fix mení earlier control model
```

## 14. Troubleshooting flow

```text
impact and timeline
→ release/exposure subject
→ state-delta inventory
→ in-flight and unknown operations
→ per-layer compatibility
→ candidate recovery actions
→ bounded transition/read-back
→ business reconciliation
```

Competing hypotheses môžu byť application defect, feature/config mismatch, data corruption, event incompatibility, dependency outage alebo retry amplification. Automatic rollback success status samostatne nerozlišuje tieto causes.

## 15. Anti-patterny

### Previous ReplicaSet ako safe rollback proof

Stored desired state nepreukazuje current shared-state compatibility.

### Rollback all axes naraz bez inventory

Môže zničiť evidence a vytvoriť conflicting transitions.

### Retry unknown external operation

Môže duplikovať effect; najprv reconciliation.

### Roll-forward cez live patch

Fix bez source, artifact a evidence vytvára nový neauditovateľný state.

### Health green ako recovery closure

Neoveruje affected operations, duplicates, backlog ani second operation.

## 16. Kontrolné otázky

1. Aký je rozdiel medzi containmentom a recovery?
2. Čo tvorí exact recovery subject?
3. Ktoré layers patria do state-delta inventory?
4. Kedy je application rollback eligible?
5. Ako sa traffic rollback líši od binary rollbacku?
6. Kedy je roll-forward bezpečnejší?
7. Prečo external effects potrebujú reconciliation?
8. Čo znamená unknown transition outcome?
9. Prečo restore nie je jednoduché undo?
10. Čo zostalo active po rollbacku v `REL-PAY-71`?
11. Ako sa overuje forbidden outcome?
12. Prečo je second operation súčasť closure?

## Glossary impact

Relevantné pojmy: rollback, roll-forward, containment, recovery subject, state-delta inventory, last compatible state, per-layer eligibility, traffic rollback, flag-off, compensation, reconciliation, unknown transition outcome, recovery generation, second-operation validation a recovery closure.

## Primárne zdroje

- [Google SRE — Emergency Response](https://sre.google/sre-book/emergency-response/)
- [Kubernetes documentation — Rolling back a Deployment](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#rolling-back-a-deployment)
- [PostgreSQL documentation — Continuous Archiving and PITR](https://www.postgresql.org/docs/current/continuous-archiving.html)
- [AWS Builders’ Library — Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Progressive delivery](progressive-delivery.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Databázová kompatibilita počas deploymentu →](database-compatibility-during-deployment.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
