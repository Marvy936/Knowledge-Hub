# Continuous Delivery pre modely

Continuous Delivery pre modely znamená, že validated model candidate sa dá bezpečne, opakovateľne a auditovateľne preniesť do cieľového inference environmentu. Neznamená automaticky, že každý úspešný training run ide do produkcie. Delivery pipeline vlastní promotion a deployment mechanizmus; model validation, business approval, online experiment a continuous training majú vlastné dôkazné hranice.

Model release je zložený subject. Okrem model package obsahuje serving image, runtime configuration, feature service, preprocessing a postprocessing, threshold alebo decision policy, routing cohort, resource limits a observability contract. Rollback iba model weights nemusí obnoviť pôvodné správanie, ak zostane nová feature generation alebo policy.

Incident `MLOPS-PAY-92` uzatvára prvý delivery blok. Atlas pipeline presunula Registry alias `champion` na model 128 a deployment manifest odkazoval priamo na alias. Päť Pods už načítalo model 128, tri staršie Pods po reštarte ešte používali model 127. Súčasne sa zmenil threshold a feature service. Control plane hlásil Ready a syntetický health check vracal HTTP 200, no request population dostávala tri rozdielne composite generations. Rollback aliasu na 127 neobnovil pôvodný threshold ani feature values.

## 1. Dominantný model-delivery lifecycle

Delivery začína immutable candidate bundle a končí overeným business journey. Mutable Registry alias môže byť promotion control, ale runtime release musí pinovať exact package a config identities.

```text
validated model candidate
→ promotion decision a approval
→ immutable release manifest
→ environment-specific render
→ admission a deployment
→ loaded model/config/feature read-back
→ shadow alebo bounded traffic exposure
→ technical a model guardrails
→ business action a outcome evidence
→ promote, hold, rollback alebo forward-fix
```

Každý krok môže zlyhať samostatne. Registry mutation môže uspieť a deployment sa nemusí začať. Deployment môže byť Ready, ale model download môže použiť stale cache. Traffic môže ísť na nový revision, ale observability query môže miešať verzie.

## 2. Exact release subject

„Nasadili sme model 128“ je príliš neurčité. Release manifest musí spojiť model package digest, serving image digest, protocol, feature generation, policy, environment, routing a ownera side effectu.

```yaml
release_subject: MLOPS-PAY-RISK-PROD-2026-08-r31
registered_model: prod.ml_team.risk_model
registry_version: 128
model_package_digest: sha256:7ab2...df90
serving_image: registry.example/ml/risk-server@sha256:91ce...101a
model_format: mlflow-pyfunc
inference_protocol: v2
feature_service: risk_features_v7
feature_registry_digest: sha256:19ac...330e
preprocessing_digest: sha256:44bd...100f
threshold_policy: review-capacity-v4
threshold_policy_digest: sha256:2f91...0aa7
deployment_manifest_commit: 8b31d4...
environment: production
routing:
  mode: canary
  initial_percent: 5
business_action: prioritize_manual_review
forbidden: direct_payment_block
```

Manifest je promotion output a deployment input. Alias `champion` môže vybrať version 128 v control-plane kroku, ale po resolution sa release pinne na package digest. Restart Podu nesmie potichu načítať inú alias generation.

## 3. Promotion nie je deployment

Promotion je rozhodnutie, že candidate spĺňa defined gates pre environment alebo ďalšiu fázu. Deployment je mutation target runtime. Tieto operácie majú odlišné permissions, audit a rollback.

```text
candidate version 128
→ validation evidence accepted
→ alias candidate-for-prod = 128
→ approved release manifest pins digest
→ Git change alebo deployment request
→ serving controller creates revision
```

Registry alias update bez deploymentu nemení live traffic, pokiaľ runtime nepoužíva alias dynamically. Git commit bez successful reconciliation nemení cluster. KServe `InferenceService` Ready nepreukazuje business outcome. Review musí preto čítať každú authority osobitne.

Promotion gates budú detailne rozpracované v samostatnej kapitole. Tu je delivery boundary taká, že pipeline prijíma gate verdict s immutable evidence references a nesmie si ho odvodiť iba z `training_run.status == FINISHED`.

## 4. Environment-specific registered models a config

Model artifact má byť rovnaký medzi staging a production. Environment-specific configuration sa môže líšiť, ale musí byť explicitná. Praktický Registry pattern používa oddelené registered models alebo namespaces pre environment a copy/promotion operation, pričom version tags nesú source lineage.

Mutable stage names sa nemajú používať ako jediná release identity. Current MLflow direction používa aliases, tags a environment-specific registered models. Alias zostáva mutable pointer, preto sa v deployment manifest-e resolved target pinne.

```python
from mlflow import MlflowClient

client = MlflowClient()
version = client.get_model_version_by_alias(
    "prod.ml_team.risk_model",
    "candidate",
)
assert version.tags["validation_bundle_digest"] == expected_bundle
resolved_version = version.version
```

Po resolution pipeline overí package manifest a digest fresh clientom. Registry metadata bez artifact bytes nestačí.

## 5. Immutable deployment manifest

Release sa renderuje do Kubernetes alebo cloud-specific manifestu s immutable inputs. Model storage URI má byť versioned alebo content-addressed. Container image je digest, nie tag. ConfigMap generation a secret versions sú súčasťou release fingerprintu.

```yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: risk-model
  namespace: ml-prod
  annotations:
    release.atlas.example/subject: MLOPS-PAY-RISK-PROD-2026-08-r31
    release.atlas.example/model-digest: sha256:7ab2...df90
spec:
  predictor:
    model:
      modelFormat:
        name: mlflow
      storageUri: s3://ml-prod/models/risk/sha256-7ab2...df90/
      runtime: atlas-mlflow-runtime-v5
    canaryTrafficPercent: 5
```

KServe predictive canary strategy v aktuálnej dokumentácii platí pre serverless deployment mode. Platform-neutral chapter preto nesmie tvrdiť, že rovnaké field semantics fungujú v každom mode alebo inference engine. Exact platform version a deployment mode patria do release subjectu.

## 6. Configured, resolved, loaded a serving state

Configured state je Git alebo submitted manifest. Resolved state je controller-observed spec, model URI a revision. Loaded state je konkrétny Pod, image ID, model digest, feature/policy config a runtime. Serving state je traffic routing a request evidence.

```text
Git commit
≠ API object accepted
≠ revision Ready
≠ every Pod loaded intended package
≠ traffic routed as intended
≠ business action correct
```

Runtime má emitovať release fingerprint pri startup-e aj pri každom prediction trace. Health endpoint môže vrátiť:

```json
{
  "release_subject": "MLOPS-PAY-RISK-PROD-2026-08-r31",
  "model_digest": "sha256:7ab2...df90",
  "feature_service": "risk_features_v7",
  "policy_digest": "sha256:2f91...0aa7",
  "ready": true
}
```

Endpoint je evidence z jedného instance. Fleet-wide acceptance potrebuje read-back zo všetkých serving instances alebo request-correlated telemetry, nie jeden náhodný request cez load balancer.

## 7. Shadow, canary a explicit test routing

Shadow deployment dostáva kópiu requestov, ale nevlastní business side effect. Umožňuje porovnať latency, errors a predictions na live population bez zmeny action. Shadow nie je risk-free: stále spracúva citlivé dáta, spotrebúva capacity a môže ovplyvniť dependencies.

Canary dostáva bounded časť live trafficu a jeho outputs môžu ovplyvniť action. Traffic percentage nie je exposure percentage, ak session affinity, retries, cohort filters alebo shared queues menia population. Routing evidence potrebuje request counts, unique entities a cohort characteristics per revision.

KServe môže pre predictive `InferenceService` rozdeliť traffic medzi previous rolled-out a latest ready revision a umožniť explicit tag routing. Tag route je vhodná pre deterministic acceptance requests, ale external clients nesmú dostať neobmedzenú možnosť obísť production routing policy.

Detailed rollout strategies budú samostatná kapitola. CD tu definuje, že release musí podporovať dark/shadow alebo bounded canary path, promotion hold a rýchly návrat na known-good composite release.

## 8. Technical, model a business guardrails

Technical guardrails sledujú availability, error rate, latency, saturation, model load failures a protocol correctness. Model guardrails sledujú input validity, prediction distribution, calibration proxy, segment behavior a forbidden outputs. Business guardrails sledujú action rate, queue capacity, human override a mature outcomes.

```text
technical green
+ model guardrails green
+ business journey acceptable
→ eligible na ďalší rollout step
```

Technical green bez model identity môže miešať revisions. Model metric bez exposure denominator môže byť selektívna. Business outcome môže dozrieť neskôr; vtedy rollout používa leading guardrails a explicitný hold, nie predstieraný finálny verdict.

Automatické promotion pravidlo musí uviesť query, time window, minimum sample, version labels, missing-data behavior a ownera. `error_rate < 1%` bez denominátora a telemetry completeness nie je gate.

## 9. Deployment orchestration a GitOps

Model CD môže vytvoriť Git change a nechať controller reconcile target environment. Git commit je desired-state evidence; controller status a live workload sú ďalšie vrstvy. Pipeline nemá paralelne meniť Git aj cluster priamo, pokiaľ ownership model explicitne neumožňuje break-glass.

Promotion PR obsahuje resolved release manifest a links na validation bundle. Merge vytvorí desired-state generation. GitOps controller aplikuje zmenu a deployment pipeline sleduje observed commit, runtime revision a business tests.

```bash
git show "$RELEASE_COMMIT":environments/prod/risk-model.yaml
kubectl get inferenceservice risk-model -n ml-prod -o yaml
kubectl get pods -n ml-prod -l serving.kserve.io/inferenceservice=risk-model \
  -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.containerStatuses[0].imageID}{"\n"}{end}'
```

Pri unknown merge alebo apply outcome sa najprv číta authoritative state. Duplicate PR alebo blind `kubectl apply` môže vytvoriť competing release generations.

## 10. Database a feature compatibility

Model release často závisí od feature schema, online store a request producerov. Backward-compatible rollout môže vyžadovať expand-contract postup: najprv publikovať nové features a producers, potom model, neskôr odstrániť staré fields.

Model signature je consumer contract. Serving layer musí odmietnuť chýbajúce required fields alebo použiť explicitný fallback, nie ticho meniť column ordering. Feature service generation je pinovaná. Ak online store obsahuje mixed generations, model rollout sa zastaví.

Compatibility matrix spája producer schema, feature view, model package a policy. Rollback candidate musí zostať kompatibilný s current upstream state. Inak „rollback modelu“ vytvorí input failure.

## 11. Credentials a approval boundary

Delivery workflow potrebuje silnejšie permissions než CI. Registry promotion, Git environment merge, cluster apply a traffic mutation majú oddelené roles. Human approval je viazaný na exact release digest; approval model 128 sa nesmie automaticky preniesť na prebuildovaný model 129.

Short-lived workload identity znižuje secret exposure. Environment protection môže vyžadovať reviewerov a branch restrictions. Approval UI status je control evidence; audit record musí zachovať approvera, release subject, timestamp a policy generation.

Break-glass rollback používa bounded role, vytvorí incident-linked audit a následne reconciliuje Git desired state. Manuálna zmena bez návratu do source of truth vytvára drift a ďalší controller ju môže prepisovať.

## 12. Rollback ako composite recovery

Rollback target nie je iba previous model version. Je to previous known-good composite generation: model package, image, feature service, preprocessing, threshold, routing a config. Niektoré components môžu byť backward compatible a nemusia sa vrátiť; rozhodnutie však musí byť explicitné.

```yaml
rollback_target:
  release_subject: MLOPS-PAY-RISK-PROD-2026-07-r29
  model_digest: sha256:1f20...aa77
  serving_image: sha256:77bc...0012
  feature_service: risk_features_v6
  policy_digest: sha256:91dd...45ef
  routing: 100_percent
```

Traffic rollback môže byť rýchly, ale sessions, caches a asynchronous actions môžu pokračovať. Recovery zahŕňa draining, cache invalidation, queue reconciliation a descendant actions. Ak nový model už vytvoril business side effects, rollback weights ich nevráti.

Roll-forward je vhodný, keď schema alebo data migration nie je bezpečne reverzibilná. CD systém má vopred poznať rollback boundaries a forward-fix path.

## 13. Unknown outcomes a idempotency

Timeout pri alias mutation, Git merge, API apply alebo traffic update nevypovedá o výsledku. Každá operation má durable ID a expected current generation. Retry najprv číta alias history, commit state, resource generation alebo routing config.

```yaml
operation_id: MLOPS-PAY-92-DEPLOY-R31
expected_current_release: MLOPS-PAY-RISK-PROD-2026-07-r29
requested_release: MLOPS-PAY-RISK-PROD-2026-08-r31
```

Conditional update odmietne mutation, ak current release už nie je expected. Tým sa zabráni tomu, aby starý retry prepisoval novšiu emergency rollback zmenu.

## 14. Competing failure hypotheses

Pri zlom canary outcome sa najprv overí observation integrity a exact revision labels. Deployment hypothesis predpokladá, že intended package nebol načítaný. Routing hypothesis predpokladá nesprávnu population alebo traffic split. Feature hypothesis predpokladá stale alebo mismatched inputs. Model hypothesis predpokladá behavior regression pri správnych inputs. Policy hypothesis predpokladá odlišný threshold alebo capacity. Business hypothesis predpokladá downstream action alebo label delay.

Matched-request shadow comparison oddeľuje model behavior od population mismatch. Fleet fingerprints odhalia mixed loaded generations. Decision trace ukáže policy. Mature labels a action completion patria až na koniec. Blind rollback iba Registry aliasu môže zakryť, ktorá vrstva zlyhala.

## 15. Recovery a acceptance layers

Containment zastaví rollout a pinne traffic na known-good revision. Zároveň zachová canary Pods, routing snapshot, requests a telemetry, ak safety dovolí. Component recovery overí package load, protocol a config. Journey recovery pošle tagged test cez feature retrieval, prediction, policy a no-side-effect action path. Business recovery sleduje real action a mature outcome.

Pozitívny test potvrdí intended release fingerprint na každom serving instance a correct tagged response. Forbidden test odmietne mutable alias v runtime manifest-e, package bez validation bundle a approval pre iný digest. Recovery test presunie traffic na previous composite release. Second-operation test znovu aplikuje rovnaký manifest a očakáva no-op, nie nový revision bez zmeny subjectu.

## 16. CD oproti Continuous Training

CD prenáša existujúci validated candidate. Continuous Training rozhoduje, kedy a z akých dát vytvoriť nový candidate. CT trigger nemá automaticky obísť delivery gates. Nový training run môže byť automatický, ale promotion a rollout zostávajú policy-controlled.

Toto oddelenie znižuje coupling. Drift signal môže spustiť training, no výsledný model musí prejsť validation, packaging, Registry a CD. Automatizácia môže byť vysoká, authority boundaries zostávajú explicitné.

## 17. Acceptance contract

Model CD je prijatá, keď immutable candidate vedie k immutable release manifestu, runtime načíta exact composite generation, traffic exposure je merateľná per revision a rollback obnoví known-good journey. Control-plane success sa nezamieňa za business success.

Delivery systém musí vedieť odpovedať: čo presne bolo schválené, čo bolo nakonfigurované, čo načítal každý instance, ktoré requesty to použili, aká policy rozhodla a aký outcome vznikol. Bez tejto traversability je automatický rollout iba rýchlejšia cesta k nejasnému incidentu.

## Primárne zdroje

- [MLflow — Model deployment](https://mlflow.org/docs/latest/deployment/)
- [MLflow — Model Registry](https://mlflow.org/docs/latest/ml/model-registry/)
- [KServe — Canary rollout strategy](https://kserve.github.io/website/docs/0.17/model-serving/predictive-inference/rollout-strategies/canary)
- [KServe — Canary rollout example](https://kserve.github.io/website/docs/0.17/model-serving/predictive-inference/rollout-strategies/canary-example)
