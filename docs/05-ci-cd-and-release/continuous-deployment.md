# Continuous Deployment

Continuous Deployment je release model, v ktorom každý exact release candidate, ktorý splní automatizovanú promotion policy, pokračuje bez rutinného manuálneho approvalu do produkčného deploymentu, bounded exposure a následného acceptance alebo recovery rozhodnutia. Automatizácia sa netýka iba spustenia `deploy` commandu. Musí automatizovať eligibility, preconditions, state transitions, observation windows, verdict, containment a lifecycle closure.

Odstránenie approval tlačidla samo osebe nie je Continuous Deployment. Ak evidence nie je complete, target environment generation nie je známa, canary cohort nie je stabilný alebo recovery vyžaduje improvizáciu, automatizácia iba skracuje čas od defectu k incidentu. Dôveryhodný model automatizuje bezpečné rozhodnutie nad exact subjectom.

## 1. Dominantný policy-to-production model

Continuous Deployment nadväzuje na Continuous Delivery. Candidate už musí mať immutable artifacts, environment-compatible configuration a preukázanú recovery eligibility. Deployment control loop potom rozhoduje, či a ako candidate vstúpi do produkcie.

```text
promotable release candidate
→ evidence completeness a freshness
→ change-risk a target-health classification
→ production deployment bez alebo s minimálnou exposure
→ stable cohort a traffic/feature assignment
→ technical, functional a business observations
→ promote, pause, abort alebo contain verdict
→ rollback, roll-forward, flag-off, compensation alebo restore
→ delayed-failure watch
→ old-generation retirement a policy learning
```

Rozhodnutie nie je iba `true/false`. `PAUSE` znamená zachovať state a zbierať ďalší dôkaz; `ABORT` zastavuje ďalšiu exposure a spúšťa recovery; `INCONCLUSIVE` znamená, že observation contract nebol splnený a nesmie sa ticho premeniť na pass.

## 2. Exact deployment-decision subject

Automatický controller potrebuje jeden subject spájajúci release, target a observed cohort:

```yaml
deploymentDecisionSubject:
  releaseId: payments-10.0-rc.4
  releaseManifestDigest: sha256:release1000rc4
  artifactDigest: sha256:pay1000api
  configurationSha: 71ac290
  policyBundleSha: 66cf902
  target:
    clusterUid: 9f041da2
    namespace: payments
    environmentGeneration: prod-eu-1844
  rollout:
    controller: payments-api
    revision: 281
    strategyGeneration: canary-v12
    cohortKey: account_id
    canaryPopulation: 0.02
  evidenceWindow:
    start: 2026-07-31T12:00:00Z
    duration: 15m
    minLogicalOperations: 10000
  recoveryReference: recovery-payments-10.0-rc4
```

Artifact digest bez `configurationSha` nevysvetľuje behavior. Namespace názov bez cluster UID nevysvetľuje target. Percento bez cohort key nevysvetľuje, kto bol vystavený. Observation window bez minimálneho počtu logical operations môže skončiť green iba preto, že canary nedostala reprezentatívny traffic.

## 3. Eligibility pred production mutation

Automatické rozhodnutie má fail-closed pre missing required evidence. Atlas najprv validuje release manifest:

```bash
jq -e '
  .status == "promotable" and
  .artifacts.api.indexDigest == "sha256:pay1000api" and
  (.evidence.required | sort) == (.evidence.passed | sort) and
  .exceptions.active == []
' release-candidate.json
```

Exit code `0` preukazuje, že JSON spĺňa tieto predicates. Nepreukazuje autenticitu súboru ani freshness target environmentu. Manifest preto musí byť podpísaný alebo pochádzať z trusted evidence store a target generation sa musí prečítať tesne pred mutation.

```bash
cluster_uid="$(kubectl get namespace kube-system -o jsonpath='{.metadata.uid}')"
policy_sha="$(kubectl -n platform-system get configmap release-policy \
  -o jsonpath='{.metadata.annotations.atlas\.example/policy-sha}')"
printf 'cluster_uid=%s\npolicy_sha=%s\n' "$cluster_uid" "$policy_sha"
```

Tieto hodnoty preukazujú observed cluster a ConfigMap annotation. Nepreukazujú, že policy engine skutočne načítal annotation generation. Loaded policy revision potrebuje vlastný runtime read-back alebo decision log.

## 4. Change-risk a target-health policy

Automatizácia môže meniť rollout podľa risku, ale klasifikácia musí byť explicitná. Database contract change, authentication change alebo nový external side effect potrebuje silnejší observation contract než textová úprava UI.

Policy kombinuje napríklad:

- release subject a changed components;
- schema/event/API compatibility classification;
- security a identity impact;
- blast radius a reversibility;
- current incident state, error-budget consumption a capacity headroom;
- evidence confidence a known exceptions;
- recovery readiness.

Policy output má byť structured:

```json
{
  "decision": "ALLOW_BOUNDED",
  "maxExposure": 0.02,
  "requiredWindow": "15m",
  "minimumLogicalOperations": 10000,
  "requiredSignals": [
    "settlement_completion_ratio",
    "duplicate_provider_effects",
    "p95_end_to_end_duration",
    "provider_reconciliation_backlog"
  ],
  "recoveryMode": "ROLL_FORWARD_OR_FLAG_OFF"
}
```

Structured output umožňuje audit a test. Stále však nepreukazuje, že rollout controller presadil presne tento verdict; deployment record musí korelovať policy decision ID s actual transition.

## 5. Deployment a exposure sú samostatné control planes

Nové Pods môžu existovať bez user trafficu. Naopak feature flag môže vystaviť nový behavior na starej application generation. Continuous Deployment preto sleduje application, traffic, feature a data axes oddelene.

```text
artifact/config deployment
→ runtime cohort available
→ readiness a dependency eligibility
→ traffic assignment
→ feature assignment
→ business operation
```

Controller nemá označiť release za exposed iba preto, že ReplicaSet je Ready. Musí prečítať route, load balancer alebo service-mesh generation a overiť stable assignment.

```bash
kubectl -n payments get deployment payments-api \
  -o jsonpath='{.metadata.generation}{" "}{.status.observedGeneration}{" "}{.status.updatedReplicas}{"\n"}'

kubectl -n payments get pods -l app=payments-api,release=payments-10.0-rc4 \
  -o jsonpath='{range .items[*]}{.metadata.name}{" "}{.status.containerStatuses[0].imageID}{"\n"}{end}'
```

Output preukazuje controller observation a runtime image IDs pre vybrané Pods. Nepreukazuje percento trafficu ani feature evaluation. Tie potrebujú route read-back a telemetry s release/cohort identity.

## 6. Observation contract

Automation nesmie vyberať ľubovoľné green dashboards. Pred rolloutom má definovať population, denominator, window, freshness a allowed missing-data behavior.

Atlas používa logical settlement outcome namiesto HTTP attempt success. Príklad Prometheus query cez HTTP API:

```bash
query='sum(rate(settlement_completed_total{release="payments-10.0-rc4",cohort="canary"}[5m])) / sum(rate(settlement_started_total{release="payments-10.0-rc4",cohort="canary"}[5m]))'

curl --fail --get \
  --data-urlencode "query=$query" \
  https://prometheus.atlas.example/api/v1/query | jq .
```

Query result preukazuje ratio z uložených time series pre zvolený label set a evaluation time. Nepreukazuje, že instrumentation pokrýva všetky logical operations, že labels nie sú dropnuté ani že completion event je authoritative business state. Controller má kontrolovať telemetry freshness a korelovať vybranú vzorku s database/provider evidence.

Missing data sa klasifikuje podľa príčiny. Nízky traffic môže vyžadovať dlhšie window; telemetry outage musí viesť k `INCONCLUSIVE` alebo `PAUSE`, nie automatickému successu.

## 7. Promotion state machine

Automatický rollout má explicitné states:

```text
ELIGIBLE
→ DEPLOYING_NO_TRAFFIC
→ CANARY_READY
→ OBSERVING
→ PROMOTING
→ FULLY_EXPOSED
→ DELAYED_WATCH
→ ACCEPTED
```

Failure transitions:

```text
OBSERVING → PAUSED_INCONCLUSIVE
OBSERVING → ABORTING
PROMOTING → UNKNOWN_TRANSITION
ANY → CONTAINED_INCIDENT
```

Každý transition má idempotency key, expected previous generation a postcondition. Traffic mutation s timeoutom môže byť unknown outcome: retry bez read-back môže aplikovať ďalší step alebo prepnúť nesprávnu route generation.

## 8. Bounded traffic transition a read-back

Príklad declarative route mutation používa generation pre compare-and-set semantics:

```yaml
apiVersion: delivery.atlas.example/v1
kind: TrafficAssignment
metadata:
  name: payments-api
spec:
  expectedGeneration: 1843
  desiredGeneration: 1844
  stableRelease: payments-9.9
  canaryRelease: payments-10.0-rc4
  canaryWeight: 2
```

Po apply controller číta authoritative resource:

```bash
kubectl -n payments apply -f traffic-assignment.yaml
kubectl -n payments get trafficassignment payments-api -o json | jq '{generation:.metadata.generation,observed:.status.observedGeneration,effective:.status.effectiveWeights,conditions:.status.conditions}'
```

Rovnosť desired/observed generation a effective weight preukazuje controller verdict. Nepreukazuje actual dataplane distribution. Access logs alebo request telemetry musia potvrdiť observed cohort share a stabilitu assignment key-u.

## 9. Recovery bez human approval neznamená blind rollback

Automatic recovery môže byť rýchla, ale musí rešpektovať per-layer eligibility. Application rollback nemusí byť možný po contract migration alebo po emitovaní nového eventu. Feature disable môže zastaviť nový path bez zmeny Pods. External unknown outcomes môžu vyžadovať reconciliation namiesto retry.

Recovery policy môže vybrať:

```text
flag-off
→ behavior je oddelený a old path zostáva compatible

traffic rollback
→ old cohort je healthy a shared state compatible

application rollback
→ binary/config/data/event contracts umožňujú návrat

roll-forward
→ defect má bounded opravu a rollback by bol riskantnejší

compensation/reconciliation
→ external side effect alebo unknown outcome už existuje
```

Automation musí pred akciou zachovať volatile evidence. Rýchly rollback bez route, generation a business-operation records môže skryť duplicate alebo lost effects.

## 10. Delayed failures a acceptance

Full exposure nie je okamžitá closure. Memory leak, cache eviction, credential expiry alebo backlog age sa môžu prejaviť po dlhšom čase. Release preto prejde delayed watch a closure až po splnení ďalších conditions.

Acceptance kombinuje:

- exact production artifact/config generations;
- exposure a feature generations;
- technical SLO a capacity;
- business completion a correctness;
- forbidden duplicate/lost/cross-tenant outcomes;
- reconciliation backlog;
- second operation a adjacent cohort;
- old-generation retirement.

## Ako funguje automatický production feedback loop

Continuous Deployment automaticky posúva každú zmenu, ktorá splní policy, až do production exposure. Nejde iba o odstránenie approval tlačidla. Automatizácia musí vytvoriť uzavretý control loop:

```text
candidate
→ evidence verdict
→ deployment mutation
→ controller convergence
→ runtime verification
→ business outcome
→ promote, stop alebo recover
```

Ak pipeline vykoná `kubectl apply` a označí job za successful, automatizovala iba mutation request. Continuous Deployment potrebuje aj read-back desired/live generation, rollout completion a outcome oracle.

Automatická policy musí rozlíšiť tri stavy:

```text
PASS
→ evidence potvrdzuje požadovaný subject

FAIL
→ test alebo policy našli porušenie

ERROR/MISSING
→ evidence sa nevytvorila alebo nedá vyhodnotiť
```

Fail-open preloží chýbajúci scanner report alebo nefunkčný analysis service na PASS. Pri required controls je bezpečnejší fail-closed alebo explicitný degraded decision s ownerom a časovým limitom.

Continuous Deployment zvyšuje požiadavky na batch size, observability, idempotenciu a recovery. Malá zmena sa ľahšie lokalizuje a roll-forwardne. Veľký batch s databázovou, aplikačnou a config zmenou vytvára viac recovery combinations.

Automatický rollback nie je univerzálna poistka. Ak nová verzia zapísala nekompatibilné dáta, publikovala eventy alebo vykonala external side effects, návrat image-u môže zhoršiť stav. Deployment policy preto pred exposure hodnotí per-layer rollback eligibility a môže namiesto rollbacku zvoliť feature disable, roll-forward alebo compensation.

## 11. Connected incident `REL-PAY-66`

Atlas automatic deployment prijal release `payments-10.0-rc4`, pretože CI a staging statuses boli zelené. Policy čítala mutable tag a neoverila digest ani changed production environment generation. Rollout controller nasadil `sha256:pay1000b`, zatiaľ čo staging evidence patrilo `sha256:pay1000a`.

Canary dashboard sledoval HTTP 2xx a process latency. Provider TLS sidecar z novej admission generation vracal `202 Accepted`, no final settlement completion zlyhávalo po async handoffe. Po 12 minútach controller zvýšil traffic z 2 % na 100 %.

```text
wrong release/evidence subject
→ bounded deployment
→ incomplete observation contract
→ automatic promotion
→ 38 % final completion regression
→ provider retry amplification
```

4 186 settlements ostalo v unknown alebo retry state-e. 119 provider operations vyžadovalo reconciliation. Automatizácia fungovala podľa implementovanej policy; policy však chránila nesprávny outcome.

## 12. Redesign a acceptance verdict

Redesign viaže decision na release manifest digest, target generation a logical business signals. Admission policy change invaliduje staging evidence a vyžaduje nový bounded validation path. Canary používa stable `account_id` assignment, minimum logical operations a final settlement state. Promotion zastaví telemetry freshness failure.

Continuous Deployment je prijatý iba vtedy, keď:

```text
promotable manifest je immutable a authenticated
+ target generation je fresh
+ policy output je versionovaný a korelovaný s transition
+ deployment, traffic, feature a data axes sú explicitné
+ canary population je stabilná a dostatočná
+ business aj forbidden signals sú authoritative
+ missing telemetry vedie k bounded state-u
+ unknown route outcome sa read-backne pred retry
+ recovery eligibility je per-layer
+ delayed watch a second operation prejdú
```

## 13. Troubleshooting flow

Pri false promotion postupuj:

```text
release/policy/target subject
→ eligibility decision
→ deployment desired a observed state
→ runtime cohort
→ route/feature effective generation
→ telemetry population a freshness
→ business authority
→ decision transition
→ recovery side effects
```

Competing hypotheses zahŕňajú wrong artifact, stale policy, target drift, unstable cohort, telemetry gap, invalid denominator, dependency-only failure, shared-state incompatibility a unknown transition. Containment má zmraziť ďalšie transitions, nie zničiť evidence okamžitým redeployom.

## 14. Anti-patterny

### Green CI rovno na 100 % trafficu

CI preukazuje integračný candidate, nie produkčný behavior v current environment a data generation.

### Automatický rollback pre každé zlyhanie

Rollback môže byť nekompatibilný so schema, events alebo external effects. Recovery potrebuje eligibility model.

### Missing data ako success

Telemetry outage alebo neprítomná cohorta nevytvára dôkaz bezpečnosti.

### Readiness ako business oracle

Ready Pod môže vykonávať nesprávny business outcome alebo používať zlú dependency generation.

### Percento bez stable assignment

Per-request random canary mieša users a operations medzi cohorts a komplikuje diagnosis aj causality.

## 15. Kontrolné otázky

1. Čo navyše automatizuje Continuous Deployment oproti Continuous Delivery?
2. Čo tvorí exact deployment-decision subject?
3. Prečo policy JSON samostatne nepreukazuje enforcement?
4. Aký je rozdiel medzi deploymentom a exposure?
5. Prečo je logical operation vhodnejší denominator než HTTP attempt?
6. Ako sa klasifikuje missing telemetry?
7. Čo znamená unknown traffic-transition outcome?
8. Kedy je flag-off bezpečnejší než binary rollback?
9. Prečo automatic controller v `REL-PAY-66` urobil chybný, ale policy-compliant verdict?
10. Čo musí delayed watch zachytiť?
11. Ako sa overuje forbidden duplicate outcome?
12. Ktoré states má mať production rollout state machine?

## Glossary impact

Relevantné pojmy: deployment-decision subject, promotable manifest, bounded exposure, stable cohort, observation contract, minimum logical operations, missing-data policy, rollout state machine, unknown transition, effective traffic generation, per-layer recovery eligibility, delayed-failure watch a automatic acceptance verdict.

## Primárne zdroje

- [Continuous Delivery](https://continuousdelivery.com/)
- [Kubernetes documentation — Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Argo Rollouts documentation](https://argo-rollouts.readthedocs.io/)
- [Prometheus HTTP API](https://prometheus.io/docs/prometheus/latest/querying/api/)
- [Google SRE Workbook — Canarying Releases](https://sre.google/workbook/canarying-releases/)
- [OpenFeature specification](https://openfeature.dev/specification/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Continuous Delivery](continuous-delivery.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Pipeline, stage, job a runner →](pipeline-stage-job-runner.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
