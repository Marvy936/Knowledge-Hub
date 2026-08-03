# Model Registry, versions, stages a aliases

Model Registry je control-plane systém pre organizovanie, versioning, metadata, governance a promotion modelov. Neuchováva automaticky celý runtime truth. Registry version odkazuje na konkrétny model artifact alebo logged model; alias je mutable named pointer na version; tags a annotations opisujú stav alebo evidence. Deployment platforma musí reference resolve-nuť na immutable package a následne potvrdiť loaded generation.

Incident `MLOPS-PAY-91` pokračuje. Atlas používal alias `champion` a serving Pody ho resolve-ovali pri každom štarte. Po promotion sa polovica Podov reštartovala okamžite a načítala version 18, druhá polovica zostala na version 17. Registry správne ukazovala `champion → 18`, Kubernetes Deployment bol ready a oba modely vracali HTTP 200. Tím však nemal jednotný production subject ani cohort evidence. Mutable alias bol použitý ako runtime identity.

## 1. Dominantný Registry lifecycle

Registry lifecycle začína immutable candidate artifactom, nie voľným uploadom súboru s názvom „final“. Candidate sa registruje, obohatí o lineage a evaluation evidence, prejde validation a approval, dostane environment-specific reference a následne je nasadený. Deployment read-back uzatvára, ktorá version bola skutočne načítaná.

```text
experiment run a committed model package
→ logged model / artifact identity
→ registered model version
→ validation status a evidence references
→ approval alebo policy decision
→ environment promotion
→ alias alebo release-manifest update
→ deployment resolves immutable version/digest
→ loaded a exercised runtime evidence
→ retirement, rollback a retention closure
```

Registry je autorita pre governance record a named references. Artifact store je autorita pre bytes. Deployment controller je autorita pre desired rollout. Runtime je autorita pre loaded model. Business telemetry je autorita pre outcome. Zelený Registry status sa nesmie zameniť za production serving.

## 2. Registered model a model version

Registered model je logical namespace pre jeden business problem a compatible interface, napríklad `prod.risk.payment-prioritization`. Model version je Registry record vytvorený pri registrácii konkrétneho model artifactu. Version number je monotonic identifier v rámci registered modelu, nie semantic version model behavioru ani content digest.

```yaml
registered_model: prod.risk.payment-prioritization
model_version: 18
source_model_id: m-2f6c9a...
source_run_id: 6f7b8fa3b5ad4aaead859f1a5d771301
artifact_uri: models:/m-2f6c9a...
package_digest: sha256:b8ae...7d22
signature: risk-inference-v6
dataset_digest: sha256:9bd7...e802
validation_bundle: s3://ml-evidence/model-18/
created_at: 2026-08-03T10:22:07Z
```

Version 18 nie je automaticky lepšia než version 17. Môže byť failed candidate, rollback copy alebo environment promotion. Consumers nemajú odhadovať lifecycle z čísla. Tags, aliases a explicitné promotion records poskytujú context.

Registered model namespace potrebuje ownership a compatibility contract. Ak sa input signature alebo business task zásadne zmení, nová version v rovnakom namespace môže zlomiť consumers. Vtedy je vhodný nový registered model alebo explicitná major-interface boundary.

## 3. Logged model, run a Registry version

Moderný MLflow rozlišuje experiment run, logged model s vlastným model ID a Registry version. Run môže vytvoriť viac modelov. Registry version môže referencovať konkrétny logged model. Táto separácia je presnejšia než predpoklad „jeden run = jeden model“.

```text
run 6f7b...
├── checkpoint model m-a1
├── calibrated model m-b2
└── exported model m-c3
       └── registered as version 18
```

Registry lineage musí ukázať exact source model a artifact digest. `run_id` samotné je nejednoznačné. Ak sa package exportuje alebo optimalizuje po run-e, Registry má referencovať final deployable artifact, nie iba training checkpoint.

## 4. Aliases ako mutable named references

Alias je human-readable pointer na jednu model version, napríklad `candidate`, `champion`, `shadow` alebo `rollback`. MLflow umožňuje resolve cez URI ako `models:/<name>@champion` a alias možno presunúť na inú version. To je užitočné pre promotion, no alias nie je immutable release identity.

```python
from mlflow import MlflowClient

client = MlflowClient()
client.set_registered_model_alias(
    name="prod.risk.payment-prioritization",
    alias="candidate",
    version="18",
)

resolved = client.get_model_version_by_alias(
    name="prod.risk.payment-prioritization",
    alias="candidate",
)
print(resolved.version, resolved.source)
```

Operation musí zaznamenať previous a new target, actor, evidence a expected current target. Blind `set_alias` môže prepísať concurrent promotion. Ak API neposkytuje compare-and-set pre daný workflow, automation urobí read, policy check, mutation a immediate read-back; stále musí riešiť race cez serialized promotion alebo external lock/approval operation.

Runtime deployment nemá opakovane resolve-ovať mutable alias bez pinning-u. Release controller alias resolve-ne raz, uloží exact version/package digest do deployment manifestu a každý Pod reportuje loaded digest.

## 5. Model stages a ich deprecation

Historické MLflow Model Registry stages používali fixed states `None`, `Staging`, `Production` a `Archived`. Aktuálna MLflow dokumentácia stages označuje ako deprecated a odporúča migration na version aliases, tags a oddelené environment-specific registered models s access control.

Fixed stage miešal viac významov: validation status, deployment environment a lifecycle. Jeden model mohol byť production v EU a canary v US, čo jeden globálny `Production` stage nevyjadril. Stage navyše nebol vhodná security boundary.

Nová dokumentácia nemá navrhovať stages ako primárny design. Musí ich vysvetliť kvôli existujúcim systémom a migration. Legacy URI `models:/name/Production` sa nahrádza environment namespace a aliasom, napríklad `models:/prod.risk.payment-prioritization@champion`.

Migration musí inventory-zovať consumers, stages, aliases a permissions. Jednorazové priradenie aliasu bez zmeny consumer code nevyrieši mutable-runtime alebo environment isolation.

## 6. Environment promotion

Dev, staging a prod sú security a ownership boundaries, nie iba tags. MLflow odporúča oddelené environment-specific registered models a môže používať `copy_model_version()` na promotion medzi nimi. Production namespace má užšie write permissions.

```text
dev.risk.payment-prioritization@candidate
→ validation evidence
→ copy immutable model version
→ prod.risk.payment-prioritization version 18
→ prod alias candidate
→ controlled rollout
→ alias champion až po acceptance
```

Copy vytvorí nový Registry version record v target namespace; package identity má zostať rovnaká alebo musí byť explicitne znovu overená. Ak promotion repackage-uje model, vzniká nový artifact a original validation sa nedá preniesť bez parity.

Environment boundary tiež oddeľuje retention, credentials a audit. Data scientist môže registrovať dev kandidáta, no produkčný alias mení deployment automation alebo approver identity.

## 7. Tags, annotations a validation status

Tags sú key-value metadata na registered modeli alebo version. Môžu evidovať `validation_status=pending`, risk class, ownera, dataset digest alebo ticket. Annotation/comment poskytuje human context. Tags sú mutable metadata, nie cryptographic evidence.

Validation report má byť immutable artifact s digestom; tag naň odkazuje a sumarizuje verdict. Zmena tagu z `pending` na `passed` musí byť autorizovaná a auditovaná. Consumer nemá dôverovať ľubovoľnému tagu bez policy nad actorom, evidence a model digestom.

```yaml
tags:
  validation_status: passed
  validation_policy: risk-model-gate-v6
  validation_bundle_digest: sha256:77fa...1021
  approved_by: spiffe://ml-platform/promotion-controller
  approved_at: 2026-08-03T11:04:18Z
```

Approval identity v tagu môže byť spoofnuteľná, ak write permission má široká skupina. Stronger audit číta platform event/log a signed evidence statement.

## 8. Promotion gate a evidence snapshot

Promotion rozhoduje nad exact model version a fixed evidence snapshot. Gate zahŕňa lineage completeness, artifact integrity, model quality, calibration, subgroup guardrails, performance, security, interface compatibility a operational readiness. Ak sa dataset labels alebo evaluation report zmenia po approval, vzniká nový gate input a decision sa musí prepočítať.

```text
candidate version 18 + package digest B
+ evaluation bundle E6
+ policy generation P4
+ target environment prod-eu1
→ approval operation A91
→ allowed promotion transition
```

„Model passed last week“ nestačí. Verdict musí uviesť subject a generation. Registry UI je presentation surface; machine-readable promotion record je authority pre automation.

## 9. Deployment correlation

Registry reference sa pri release preloží na exact artifact. Deployment manifest obsahuje registered model, version, package digest, serving image a feature/policy contracts. Runtime `/metadata` alebo metric reportuje loaded model.

```yaml
release_id: risk-prod-eu1-2026-08-03.2
registered_model: prod.risk.payment-prioritization
registry_version: 18
resolved_from_alias: candidate
package_digest: sha256:b8ae...7d22
serving_image: registry.example/risk-serving@sha256:80cd...7810
feature_service: risk-features-v6
policy: review-capacity-v4
```

Alias sa po vytvorení release môže presunúť; release zostáva reproducible. Rollback používa previous immutable release subject, nie „alias možno stále ukazuje na starý model“.

## 10. Concurrency a unknown outcomes

Dve pipeline môžu súčasne promovovať rôzne candidates. Bez serialized operation môžu obe prejsť read gate a posledný alias write vyhrá. Promotion potrebuje operation identity, expected previous state a single-writer alebo concurrency control.

API timeout po `set_alias` je unknown outcome. Blind retry môže presunúť alias po ďalšej legitimate mutation. Client najprv read-backom zistí current target a audit events. Ak current target zodpovedá intended version, operation sa považuje za completed. Ak ukazuje expected previous version, možno bezpečne retry-nuť. Iný target vyžaduje conflict handling.

Model version creation po timeout-e môže vytvoriť duplicate versions, ak client nevie nájsť existing record podľa source model ID a idempotency metadata. Automation musí reconcile-nuť intent s Registry stateom.

## 11. Rollback a alias history

Alias presun na previous version je control-plane rollback, nie complete production recovery. Deployment musí reconcile-nuť, stiahnuť/načítať package a prejsť health, prediction a business tests. Cache môže držať novší model. Long-lived connections alebo batch jobs môžu pokračovať so starou loaded generation nezávisle od aliasu.

Registry audit/history má zachovať previous targets a promotion reasons. Ak platforma neposkytuje dostatočný alias event history, organizácia vedie append-only promotion ledger. Version delete pred retention closure zničí rollback aj audit.

## 12. Registry permissions a governance

Permissions sa aplikujú na registered model namespace a operations. Read model metadata, download artifact, create version, set tag, set alias a delete sú odlišné capabilities. Production serving identity potrebuje read exact approved artifact, nie create/delete.

Separation of duties môže vyžadovať, aby training identity vytvorila candidate, validation identity zapisovala evidence a promotion controller menil prod alias až po approval. Break-glass mutation je časovo obmedzená, auditovaná a následne reconciled do authoritative release state.

Registry nie je secret store. Tags a descriptions nesmú obsahovať credentials alebo citlivé row-level evidence.

## 13. Failure walkthrough incidentu MLOPS-PAY-91

Atlas promotion pipeline presunula `champion` na version 18. Deployment používal startup command, ktorý alias resolve-oval až v Pode. Rolling restart bol pomalý a alias mutation nebola súčasťou Pod template hash-u. Výsledkom bola mixed fleet: staré Pody version 17, nové Pody version 18.

Registry read-back bol správny, preto Registry nebola broken. Kubernetes desired state tiež nezahŕňal model version, takže controller nemal dôvod dokončiť jednotný rollout. Request telemetry nemala model digest label; aggregate metrics zmiešali oba cohorts.

Containment zastavil alias-based restarts a rollout. Tím pridal loaded-model endpoint, rozdelil traffic podľa Pod generation a vytvoril immutable release manifest pre version 17. Následne deployment explicitne pinol package digest version 18 a rollout prebehol ako nová Pod template generation.

## 14. Recovery a acceptance

Component recovery overí Registry version, artifact digest, tags a alias target. Journey recovery overí, že deployment resolve-ol exact version a každý ready Pod reportuje intended digest. Business recovery porovná cohort outcome a guardrails. Alias read-back bez runtime proof je partial recovery.

Positive test registruje candidate, viaže evidence, presunie `candidate` a vytvorí pinned release. Forbidden test odmietne missing lineage, unapproved writer alebo incompatible signature. Concurrency test spustí dve promotion operations a očakáva conflict/serialization. Unknown-outcome test simuluje timeout a read-before-retry. Second-promotion test presunie alias na ďalšiu version a overí, že previous release zostáva rollbackable.

```python
from mlflow import MlflowClient

client = MlflowClient()
version = client.get_model_version_by_alias(
    "prod.risk.payment-prioritization",
    "candidate",
)

assert version.version == "18"
assert version.tags["validation_status"] == "passed"
assert version.tags["package_digest"] == "sha256:b8ae...7d22"
```

Tento read-back dokazuje Registry metadata. Neoveruje artifact bytes, loaded runtime ani business outcome; ďalšie acceptance vrstvy sú povinné.

## 15. Kontrolné otázky

1. Aký je rozdiel medzi registered modelom, model version, logged modelom a package digestom?
2. Prečo alias nie je bezpečná runtime identity?
3. Prečo sú fixed Model Stages deprecated a čím sa nahrádzajú?
4. Ako sa rieši timeout po alias mutation?
5. Ktoré dôkazy uzatvárajú Registry promotion až do production outcome-u?

## 16. Primárne zdroje

- [MLflow Model Registry](https://mlflow.org/docs/latest/ml/model-registry/)
- [MLflow Model Registry workflows](https://mlflow.org/docs/latest/ml/model-registry/workflow)
- [MLflow Models](https://mlflow.org/docs/latest/ml/model)
- [MLflow Tracking API](https://mlflow.org/docs/latest/ml/tracking/tracking-api)

Registry organizuje lifecycle a governance modelov. Produkčný truth však vzniká až spojením immutable artifactu, release manifestu, loaded runtime, request cohortu a business evidence.
