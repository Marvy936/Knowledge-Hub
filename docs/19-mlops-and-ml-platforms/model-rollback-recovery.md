# Model rollback a recovery

Rollback je riadený návrat z chybnej produkčnej generácie na known-good composite release. Nie je to iba presun Registry aliasu alebo zmena model weights. Produkčné správanie určuje model package, serving image, feature generation, threshold, fallback, resource profile, routing a downstream policy. Rollback jednej zložky môže ponechať systém v kombinácii, ktorá nikdy nebola validovaná.

V incidente `MLOPS-PAY-95` tím po zvýšení fallback rate presunul MLflow alias `champion` späť na predchádzajúcu model version. Bežiace pody však alias znovu nenačítali, feature service ostal na novej generation a review-capacity policy zostala z canary experimentu. Control plane ukazoval úspešnú Registry mutation, ale requesty naďalej používali mixed runtime. Skutočná recovery vyžadovala immutable rollback manifest, rollout do všetkých replík, request-correlated read-back a mature outcome verification.

## 1. Rollback subject

Known-good release je immutable manifest s evidence z predchádzajúcej acceptance.

```yaml
release_id: fraud-serving-2026-07-01.2
model_digest: sha256:old-model
serving_image: registry.example.com/fraud@sha256:old-image
feature_generation: fraud-request-v10
threshold_policy: threshold-v14
fallback_policy: rules-v5
resource_class: a100-mig-2g-v2
monitoring_contract: fraud-monitor-v8
```

Mutable alias je control reference. Rollback workflow ho môže zmeniť, ale deployment musí pinovať resolved version a digest. Alias mutation sama nepreukazuje loaded state.

## 2. Failure detection a rollback decision

Rollback sa nespúšťa na každý alert. Decision contract určuje severity, blast radius, confidence, recovery time a alternatívy. Pri infra bottleneck môže byť správny capacity containment, nie model rollback. Pri feature corruption treba rollbacknúť feature generation.

Decision record obsahuje incident, first divergence, affected release, evidence, approver a target generation. Emergency path môže skrátiť approvals, ale nesmie odstrániť audit trail.

## 3. Rollback strategies

Traffic rollback presmeruje requesty na existujúcu healthy revision. Je najrýchlejší, ak old revision zostala warm a kompatibilná. Deployment rollback znovu aplikuje known-good manifest a vytvorí nové pody. Registry rollback mení promotion control, no sám nemení runtime. Feature alebo policy rollback mení príslušnú generáciu.

```text
traffic rollback
deployment rollback
model/registry rollback
feature rollback
policy rollback
data correction
```

Výber závisí od first divergence. Viac zmien naraz môže byť nutných, ale každá musí byť v composite targete.

KServe canary alebo revision model môže zachovať previous revision pre rýchle presmerovanie. Prevádzkovateľ stále musí overiť actual traffic a loaded digest.

## 4. Compatibility a state

Starý model nemusí byť kompatibilný s novými features alebo schema. Rollback package preto potrebuje compatibility matrix a contract tests. Feature store môže mať iba latest online values; návrat transform code bez historical compatibility môže vytvoriť nesprávne inputs.

State zahŕňa cache, batch queue, streaming offsets, reviewer queue a downstream actions. Rollback modelu nevráti už vykonané side effects. Recovery potrebuje reconciliation a prípadne compensating action.

## 5. Idempotency a unknown outcomes

Rollback API call môže skončiť timeoutom po úspešnej mutation. Slepý retry môže prepísať novšiu decision alebo vytvoriť duplicate rollout. Workflow používa operation ID, compare-and-set a read-before-retry.

```text
submit rollback operation
→ timeout/unknown
→ read current desired state
→ read actual rollout generation
→ decide retry or reconcile
```

Každý krok loguje actor, subject, previous value a new value.

## 6. Data-plane verification

Control-plane success nie je recovery. Všetky ready repliky musia reportovať target release fingerprint. Synthetic request overí feature, model, policy a fallback. Request traces potvrdia actual routing.

```bash
kubectl -n ml-prod get inferenceservice fraud -o yaml
kubectl -n ml-prod get pods -l serving.kserve.io/inferenceservice=fraud
kubectl -n ml-prod logs <pod> --since=10m
```

Príkazy sa dopĺňajú loaded-model metrics a request evidence. `Ready=True` bez digest parity je forbidden acceptance.

## 7. Roll-forward verzus rollback

Rollback nemusí byť možný, ak sa zmenila schema, data store alebo external contract. Roll-forward vytvorí novú opravenú generation. Decision závisí od času, compatibility a risku.

Emergency patch musí prejsť minimálnym validation gate: package load, contract test, synthetic journey a bounded rollout. „Je to iba rollback“ nie je dôvod obísť validation, pretože target environment sa mohol od pôvodnej acceptance zmeniť.

## 8. Recovery vrstvy

Component recovery potvrdzuje správny model load, features a runtime. Journey recovery potvrdzuje end-to-end request, action a fallback. Business recovery potvrdzuje deadline success, queue a mature outcome.

```text
configured target
→ resolved target
→ loaded target
→ exercised journey
→ stable service window
→ mature business recovery
```

Recovery window musí byť dostatočne dlhý na odhalenie cold starts, delayed labels a periodic workloads. Incident sa neuzatvára po prvom zelenom requeste.

## 9. Reconciliation side effects

Pred rollbackom mohli vzniknúť nesprávne decisions. Systém potrebuje ledger affected operations, replay safety a compensating policy. Nie každý side effect je vratný; vtedy recovery zahŕňa human process, notification alebo financial correction.

Replay nesmie vytvoriť duplicate action. Operation ID a idempotency key viažu pôvodný a recovery attempt.

## 10. Testing a game days

Rollback sa testuje pred incidentom. Game day overí artifact dostupnosť, permissions, old-image pull, feature compatibility, traffic switch, monitoring a reconciliation. Backup model, ktorý sa nedá načítať z retention store, nie je recovery option.

Second-operation test vykoná ďalší rollback alebo no-op apply. Odhalí one-time credentials, mutable alias, garbage-collected artifact a manuálny krok.

## 11. Acceptance boundaries

Pozitívna acceptance vyžaduje immutable target, exact first divergence, approved decision, loaded parity všetkých replík, synthetic journey a stable window. Recovery acceptance pridáva reconciliation a mature outcome. Forbidden acceptance je Registry alias, Git commit, `Ready=True` alebo pokles alertu bez data-plane a business evidence.

Post-incident RCA musí oddeliť trigger, contributing conditions a detection gaps. Rollback success nie je dôkaz, že pôvodná príčina bola model; je iba potvrdenie, že known-good composite generation obnovila outcome.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Feedback loops a ground-truth delay](feedback-loops-ground-truth-delay.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Governance, approvals a audit →](governance-approvals-audit.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
