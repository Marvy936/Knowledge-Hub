# Shadow, canary a A/B model deployment

Shadow, canary a A/B deployment nie sú tri názvy pre postupné nasadenie. Každý pattern odpovedá na inú otázku a vytvára inú exposure, action a causal-evidence boundary. Shadow porovnáva candidate na live requests bez vlastníctva business side effectu. Canary obmedzuje blast radius novej release a sleduje safety/quality guardrails. A/B experiment randomizuje eligible population, aby odhadol causal effect alternatív na definovaný outcome.

Traffic split v load balanceri nie je automaticky experiment. Päť percent requests môže predstavovať inú population než päť percent users. Shared queue, capacity, retries a human workflow môžu miešať treatment a control. Bez stable assignment, exposure logging a outcome attribution sa výsledok nedá interpretovať.

Incident `MLOPS-PAY-93` pokračuje rolloutom candidate 141. Shadow path omylom volal notification tool a vytváral side effect. Canary dostal 10 % requests, ale session affinity koncentrovala nových merchantov a výsledky vyzerali horšie. Následný A/B test randomizoval payment attempts namiesto merchantov, takže jeden merchant prechádzal medzi modelmi a learning medzi pokusmi porušil independence. Obe variants zároveň zdieľali review capacity; treatment vytlačil control prípady z queue a zmenil jeho outcome.

## 1. Spoločný deployment lifecycle

```text
immutable candidate release
→ deployment pattern a hypothesis
→ eligibility population
→ assignment alebo traffic routing
→ actual exposure
→ prediction a policy
→ action alebo no-action boundary
→ guardrail a outcome collection
→ decision: promote, hold, rollback, redesign
```

Pattern sa vyberá podľa otázky. Shadow overuje technical a prediction behavior na live population. Canary overuje, či je bezpečné rozšíriť live exposure. A/B test overuje, či treatment spôsobuje lepší business outcome než control.

## 2. Exact rollout subject

```yaml
rollout_subject: MLOPS-PAY-ROLLOUT-2026-08-141
candidate_release: MLOPS-PAY-RISK-PROD-2026-08-r31
control_release: MLOPS-PAY-RISK-PROD-2026-07-r29
pattern: canary
eligibility_policy: eligible_card_not_present_v5
assignment_unit: merchant_id
routing_generation: risk-rollout-router-v7
initial_exposure: 0.05
guardrail_policy: risk-canary-guardrails-v6
shared_capacity_policy: reserved_control_treatment_v2
operation_id: MLOPS-PAY-93-ROLLOUT-141
```

Subject obsahuje aj feature, threshold a action policy cez release identities. Model version bez composite release nestačí. Assignment unit a eligibility patria do subjectu, pretože menia population a interference.

## 3. Shadow deployment

Shadow candidate dostane copy inputu alebo replay, ale jeho output sa nepoužije na primary business action. Cieľom je zmerať load, latency, errors, feature availability a prediction differences na live requests.

```text
primary request
├── control path → authoritative action
└── shadow copy → candidate prediction → comparison only
```

Shadow musí mať hard side-effect isolation. Candidate credentials nesmú umožniť vytvoriť ticket, charge, notification alebo mutable external state. „Nepoužívame output“ je slabá kontrola, ak code stále môže volať tool.

Shadow traffic zdvojnásobuje časť loadu a môže ovplyvniť feature store alebo shared model server. Sampling a capacity limit chránia production. Request copy potrebuje privacy a retention policy.

Matched-request comparison je silná výhoda shadowu: control aj candidate dostanú rovnaký observation subject. Rozdiel v prediction sa dá priradiť release generation, pokiaľ features a preprocessing sú zachytené.

## 4. Shadow evidence a limity

Shadow preukazuje, čo by candidate predikoval, nie čo by sa stalo po jeho action. Human reviewers, customers a downstream systems nereagujú na shadow output. Business outcome preto zostáva counterfactual a nie je priamo pozorovaný.

Shadow môže používať historical action a label pre offline comparison, ale treatment policy by zmenila reviewed population. Candidate s vyšším score pre iné prípady môže vyzerať dobre na observed labels a stále mať neznámy real impact.

Acceptance zahŕňa fleet fingerprint, matched-request count, missing/fallback rate, latency, prediction delta, segment coverage a nulové side effects. Shadow completion nie je production promotion verdict; je evidence pre ďalší gate.

## 5. Canary deployment

Canary posiela bounded live traffic na candidate a umožňuje rýchly rollback. Je primárne safety a operational-risk pattern. Exposure sa zvyšuje v krokoch, keď technical, model a business leading guardrails zostávajú accepted.

KServe predictive `InferenceService` v serverless mode podporuje `canaryTrafficPercent`, sleduje previous rolled-out a latest ready revision a umožňuje návrat na previous revision. Táto semantics nie je univerzálna pre všetky KServe modes; release subject musí pinovať platform a deployment mode.

```yaml
spec:
  predictor:
    model:
      modelFormat:
        name: sklearn
      storageUri: s3://ml-prod/models/risk/sha256-6a11/
    canaryTrafficPercent: 10
```

Control-plane field nepreukazuje actual exposure. Request telemetry musí uviesť revision a release subject. Bad revision môže byť Ready, ale behaviorally chybný. Rollout controller health check preto nenahrádza model/business guardrails.

## 6. Traffic percent oproti population exposure

Request split, user split a entity split nie sú rovnaké. Pri payments môže jeden merchant vytvoriť stovky requests. Request-level 10 % môže treatment vystaviť takmer všetkých merchantov aspoň raz. Session affinity alebo region routing môže naopak vytvoriť úzky cohort.

Exposure report potrebuje:

```text
requests per variant
unique assignment units per variant
segment distribution
retries a duplicate attempts
actual action rate
capacity consumed
```

Canary verdict sa nemá opierať iba o configured percent. Actual exposure a telemetry completeness sú gate inputs.

## 7. Tag a explicit routing

KServe môže povoliť tag-based routing na previous a latest revision. Tento path je vhodný pre deterministic smoke, replay alebo selected internal clients. Tag route nesmie byť verejný bypass production policy.

Tagged request sa autentizuje a audit loguje. Test input má operation mode `no_side_effect` alebo izolovaný tenant. Výsledok potvrdí candidate journey pred širším traffic splitom.

Tag endpoint identity sa môže zmeniť pri novej revision. Hard-coded URL bez observed revision read-back môže testovať inú generation než intended candidate.

## 8. A/B experiment

A/B test randomizuje eligible units medzi control a treatment a porovná outcome. Assignment musí byť stable a pre-analysis plan určuje hypothesis, primary metric, guardrails, sample size, duration a stopping policy.

```yaml
experiment_id: MLOPS-PAY-EXP-2026-08-141
assignment_unit: merchant_id
randomization: hash_bucket_v3
control: release-r29
treatment: release-r31
allocation: 50/50
primary_outcome: confirmed_loss_recovered_30d
guardrails:
  - false_positive_review_rate
  - analyst_minutes_per_case
  - customer_complaints
```

Assignment event a actual exposure event sú odlišné. Unit môže byť assigned treatment, ale request zlyhá pred modelom alebo fallback použije control. Intent-to-treat a treatment-on-treated estimands odpovedajú na odlišné otázky; experiment musí uviesť, ktorý používa.

## 9. Assignment unit a contamination

Randomization unit sa vyberá podľa interference a user journey. Payment-attempt assignment môže byť nevhodný, ak merchant alebo customer reaguje na predchádzajúcu action. Merchant-level assignment znižuje cross-variant contamination, ale môže potrebovať viac času a cluster-aware analysis.

Stable hash potrebuje salt a experiment generation. Zmena allocation nemá preassignovať existujúce units bez policy. New experiment alebo explicitný ramp design zachová analysis.

Cross-device identity, anonymous-to-known merge a shared accounts vytvárajú contamination. Assignment service a analysis dataset musia používať rovnakú canonical unit identity.

## 10. Interference a shared capacity

Variants môžu zdieľať queue, reviewers, GPU, rate limit alebo downstream inventory. Treatment, ktorý vytvorí viac high-priority cases, môže vytlačiť control cases a zmeniť jeho observed outcome. Stable assignment neodstraňuje shared-resource interference.

Capacity policy môže rezervovať quotas per variant alebo analysis model zahrnie shared-state. Ak business process nedokáže izolovať capacity, experiment meria combined system pri interference, nie čistý model effect.

Canary má podobný problém: candidate môže vyzerať zdravý pri 5 %, ale pri 100 % prekročí queue alebo feature-store capacity. Ramp testuje aj scale-dependent behavior; výsledok z malej exposure sa nemá lineárne extrapolovať bez capacity modelu.

## 11. Metrics, maturity a sequential peeking

Technical metrics dozrievajú rýchlo, business outcomes môžu trvať týždne. Rollout používa layered gates: immediate safety, short-term action quality a mature outcome. Leading metric sa nesmie prezentovať ako finálny business result.

Repeated checking a stopping pri prvom „significant“ výsledku zvyšuje false-positive risk. Experiment má stopping rule, minimum duration a sample size. Emergency harm guardrail môže experiment zastaviť nezávisle od primary outcome.

Missing outcomes a selective labels sa analyzujú podľa varianty a exposure. Ak treatment posiela iné cases na review, label availability sa líši a naive comparison je biased.

## 12. Observability a version identity

Každý prediction trace obsahuje assignment, actual revision, model digest, feature generation, fallback, policy a action. Per-version metrics sú nutné pre canary. Aggregate endpoint metric môže zakryť candidate error.

```json
{
  "experiment_id": "MLOPS-PAY-EXP-2026-08-141",
  "assignment": "treatment",
  "release_subject": "MLOPS-PAY-RISK-PROD-2026-08-r31",
  "actual_revision": "risk-model-00031",
  "fallback": false,
  "action": "manual_review"
}
```

Logs bez denominátora a unique assignment unit nestačia. Telemetry pipeline completeness je súčasť verdictu.

## 13. Rollout step a approval

Canary ramp môže byť napríklad 1 %, 5 %, 20 %, 50 %, 100 %, ale čísla nie sú univerzálne. Každý step má minimum exposure, duration, guardrails a approver/automation policy.

```yaml
step: 20_percent
minimum_requests: 100000
minimum_unique_merchants: 5000
minimum_duration: 6h
required:
  technical_guardrails: pass
  feature_fallback_rate: <=0.002
  queue_capacity_headroom: >=0.25
```

Automatic ramp sa zastaví pri missing telemetry. Unknown evidence nie je green. Manual approval sa viaže na exact step a release digest.

## 14. Rollback a experiment termination

Canary rollback presunie traffic na known-good composite release. Zároveň zachová candidate evidence a reconciliuje async actions. A/B termination zastaví nové assignments alebo exposure podľa planu, ale existing units môžu potrebovať stable treatment počas journey, aby sa predišlo switching harm.

Rollback reason sa klasifikuje ako technical, model, policy, capacity alebo business. Registry alias, routing a Git desired state sa reconciliujú. Manual traffic patch bez source-of-truth update vytvára drift.

Candidate môže byť quarantined alebo zostať na shadow path pre diagnosis. Rollback neznamená automaticky, že model weights sú root cause.

## 15. Competing failure hypotheses

Zlý canary metric môže byť population imbalance, mixed revisions, feature mismatch, model regression, policy difference, capacity interference alebo telemetry defect. A/B difference môže byť randomization failure, contamination, non-compliance, missing outcomes, sequential bias alebo genuine causal effect.

First divergence sa hľadá v eligibility, assignment, actual exposure, features, prediction, action a outcome. Retraining pred overením assignment a telemetry môže odstrániť candidate, ale nevyrieši experiment design.

## 16. Recovery a acceptance

Containment pinne traffic na control alebo zastaví new assignments a zachová routing, exposure a outcome snapshots. Recovery opraví jednu vrstvu: router, identity, capacity reservation, telemetry alebo candidate. New rollout generation nepoužíva potichu starý experiment ID.

Pozitívny shadow test potvrdí matched requests a zero side effects. Pozitívny canary test potvrdí actual bounded exposure a per-revision guardrails. Pozitívny A/B test potvrdí stable randomization, balance, exposure a mature outcome analysis. Forbidden test odmietne public tag bypass, request-level assignment pri entity interference a promotion z aggregate metrics bez version labels.

Second-operation test znovu aplikuje rovnaký routing subject a očakáva no-op. Recovery test vráti previous composite release a overí journey. Deployment pattern je prijatý až vtedy, keď jeho evidence odpovedá na intended otázku a blast radius, causal inference a business side effects zostávajú explicitne oddelené.

## Primárne zdroje

- [KServe — Canary rollout strategy](https://kserve.github.io/website/docs/0.17/model-serving/predictive-inference/rollout-strategies/canary)
- [KServe — Canary rollout example and tag routing](https://kserve.github.io/website/docs/0.17/model-serving/predictive-inference/rollout-strategies/canary-example)
- [KServe — InferenceGraph routing resources](https://kserve.github.io/website/docs/0.17/reference/crd-api)
