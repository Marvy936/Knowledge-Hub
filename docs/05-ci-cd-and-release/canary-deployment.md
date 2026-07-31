# Canary deployment

Canary deployment postupne vystavuje nový release obmedzenej a identifikovateľnej časti produkčného workloadu. Jeho cieľom nie je iba znížiť traffic percentage. Canary má pri bounded blast radiuse testovať konkrétnu release-risk hypotézu a vytvoriť porovnateľný evidence verdict pre promotion, pause, abort alebo inconclusive stav.

Canary nie je automaticky A/B experiment. Safety canary chce odhaliť regresiu a minimalizovať škodu; nemusí merať kauzálny product uplift. Dôveryhodný canary potrebuje exact release subject, stabilnú assignment unit, reprezentatívnu cohortu, sufficient sample, predefinované technical aj business oracles a recovery path.

## 1. Dominantný bounded-exposure model

```text
healthy stable baseline
→ exact immutable canary subject
→ release-risk hypotéza a observation contract
→ stabilná a reprezentatívna assignment cohorta
→ bounded deployment a traffic/feature exposure
→ technical, functional a business evidence
→ promote / pause / abort / inconclusive
→ ďalší krok alebo authoritative recovery
→ delayed watch a cohort closure
```

Percento je iba jedna dimension. Dve percentá enterprise accounts môžu predstavovať väčší financial risk než desať percent test tenants. Cohort selection sa preto viaže na blast radius, dependency diversity, geography, tenant profile a failure detectability.

## 2. Exact canary subject

```yaml
canarySubject:
  service: payments-api
  stable:
    release: payments-9.9.3
    artifactDigest: sha256:pay993
    configurationSha: 5f91420
  canary:
    release: payments-10.0.0-rc.4
    releaseManifestDigest: sha256:release1000rc4
    artifactDigest: sha256:pay1000api
    configurationSha: 71ac290
  environmentGeneration: prod-eu-1844
  assignment:
    unit: account_id
    hashSaltGeneration: canary-salt-12
    targetPercent: 2
    exclusions:
      - regulatory-critical
      - unresolved-incident
  window:
    minimumDuration: 15m
    minimumLogicalOperations: 10000
  hypothesis:
    statement: release does not reduce final settlement completion or create duplicate provider effects
  recoveryReference: canary-recovery-1000rc4
```

Subject musí zachovať stable aj canary generation. Porovnanie canary s globálnym baseline môže byť skreslené, ak stable cohort používa inú Region, tenant mix alebo provider route.

## 3. Stable assignment

Assignment unit má zodpovedať user alebo business journey. Per-request random assignment môže poslať jeden multi-step settlement cez obe generations, miešať cache/session state a komplikovať diagnosis. Stable hashing viaže account alebo operation na cohort počas celého window-u.

```python
import hashlib

def cohort(account_id: str, salt: str, percent: int) -> str:
    digest = hashlib.sha256(f"{salt}:{account_id}".encode()).digest()
    bucket = int.from_bytes(digest[:8], "big") % 10_000
    return "canary" if bucket < percent * 100 else "stable"
```

Deterministic function preukazuje stable assignment pre rovnaké inputs. Nepreukazuje, že edge, service mesh a application používajú rovnaký salt/generation ani že account distribution je reprezentatívna. Assignment generation musí byť read-backnutá z effective routing/config state-u.

## 4. Representativeness a exclusions

Canary cohort má byť dostatočne podobná stable population pre testovaný risk. Ak obsahuje iba interných users, neoverí external IdP, mobile clients alebo provider quotas. Naopak high-value tenants môžu byť zámerne vylúčené v prvom kroku a pridané v neskoršom ring-u.

Representativeness sa hodnotí podľa relevantných dimensions:

```text
region a availability zone
client/platform version
tenant size a traffic shape
provider route a currency
authentication/authorization path
data shape a workflow type
```

Nie každá dimension má byť metric label; high-cardinality identity sa môže korelovať mimo metrics. Dôležitý je cohort inventory a analytická schopnosť.

## 5. Observation contract

Pred exposure sa definuje:

- exact population a denominator;
- signal authority a instrumentation coverage;
- minimum sample a duration;
- promotion/abort thresholds;
- missing-data policy;
- dependency a saturation guardrails;
- forbidden outcomes;
- delayed failure window.

Atlas používa final logical settlement completion, duplicate provider effects, end-to-end latency a reconciliation backlog. HTTP 2xx je pomocný signal, nie business oracle.

```bash
query='sum(rate(settlement_completed_total{release="payments-10.0.0-rc.4",cohort="canary"}[5m])) / sum(rate(settlement_started_total{release="payments-10.0.0-rc.4",cohort="canary"}[5m]))'

curl --fail --get \
  --data-urlencode "query=$query" \
  https://prometheus.atlas.example/api/v1/query | jq '.data.result'
```

Result preukazuje ratio z available series a selected labels. Nepreukazuje complete logical population, freshness všetkých scrapes ani correct event semantics. Controller kontroluje sample count, telemetry freshness a independent business records.

## 6. Canary deployment a endpoint eligibility

New release sa najprv nasadí bez trafficu a overí runtime identity:

```bash
kubectl -n payments rollout status deployment/payments-api-canary --timeout=10m
kubectl -n payments get pods -l release=payments-10.0.0-rc.4 \
  -o jsonpath='{range .items[*]}{.metadata.uid}{" "}{.status.containerStatuses[0].imageID}{"\n"}{end}'
```

Controller convergence a imageID preukazujú workload generation. Nepreukazujú route weight ani assignment. Traffic controller resource a actual request logs musia potvrdiť effective cohort.

## 7. Exposure steps a state machine

```text
DEPLOYED_NO_TRAFFIC
→ INTERNAL_CANARY
→ PRODUCTION_0_5_PERCENT
→ PRODUCTION_2_PERCENT
→ PRODUCTION_10_PERCENT
→ PRODUCTION_25_PERCENT
→ FULL_PROMOTION
```

Každý step má vlastný minimum duration/operations a môže skončiť `PASS`, `ABORT`, `PAUSE` alebo `INCONCLUSIVE`. Kroky nemusia byť percentá; môžu byť konkrétny Region, provider route alebo tenant ring.

Controller nesmie pokračovať len preto, že threshold bol krátko green. Observation window má stabilizačnú a evaluation časť. Pri low traffic sa môže predĺžiť, ale má hard maximum a explicitný inconclusive verdict.

## 8. Matched stable comparison

Absolute canary metric môže vyzerať zle počas spoločného dependency incidentu. Matched stable cohort pomáha oddeliť release-specific effect od shared failure. Porovnanie však musí používať rovnaký time window a podobné population dimensions.

```text
canary completion 96.0 %
stable matched completion 99.8 %
→ release-specific delta -3.8 pp
```

Ak canary používa iný provider route, delta môže pochádzať z route, nie code. Exact subject zahŕňa dependency generation a analysis má competing hypotheses.

## 9. Missing, delayed a biased evidence

No-data môže znamenať nulový traffic, telemetry defect alebo label mismatch. Žiadny z týchto stavov nie je pass. Tail latency a async completion môžu prísť po window-e; controller nesmie vyhodnotiť iba fast successes a ignorovať pending operations.

Canary môže vytvoriť survivorship bias, ak failed requests nevytvoria trace/metric. Business denominator má pochádzať z authoritative admission/operation records, nie iba successful handler instrumentation.

## 10. Abort a containment

Abort zastaví novú exposure a zachová cohort identity/evidence. Existing canary operations sa nesmú naslepo retryovať cez stable release, ak external outcome je unknown. Recovery môže route-nuť nové operations na stable a samostatne reconciliovať in-flight canary operations.

```text
freeze exposure generation
→ stop new canary assignments
→ preserve route/config/telemetry/operation evidence
→ classify canary in-flight state
→ rollback, flag-off alebo roll-forward
→ reconcile unknown external effects
→ verify stable and forbidden outcomes
```

## 11. Connected incident `REL-PAY-69`

Atlas canary používala per-request random 2 % routing. Multi-step settlement mohol začať na stable a dokončiť na canary. Canary metric sledovala HTTP attempts a denominator tvorili iba requests, ktoré dosiahli handler instrumentation. Fast TLS failures na new provider sidecar nemali release label a vypadli z ratio.

```text
unstable assignment
→ mixed-version journey
→ failed requests absent from denominator
→ canary dashboard 99.7 % success
→ promotion na 25 %
→ final business completion 93.1 %
```

Canary cohort navyše obsahovala prevažne low-volume tenants. Po 25 % sa dostali enterprise accounts s iným provider route a failure sa zosilnil. 4 186 settlements ostalo pending; 119 vyžadovalo reconciliation.

Root cause bol observation a assignment contract, nie iba threshold.

## 12. Redesign a acceptance verdict

Redesign používa stable `account_id` assignment, authoritative admitted-operation denominator, matched stable cohorts, provider-route dimension, minimum logical operations a no-data fail-closed. Canary in-flight operations majú release identity a reconciliation state.

Canary je prijatá iba vtedy, keď:

```text
stable a canary subjects sú exact
+ assignment unit a generation sú stable
+ cohort je reprezentatívna pre aktuálny step
+ deployment a traffic read-back sa zhodujú
+ authoritative denominator zahŕňa failures
+ minimum sample/duration sú splnené
+ matched stable porovnanie je relevantné
+ missing/late data má explicitný verdict
+ abort zachová a reconciliuje in-flight work
+ forbidden duplicate/lost outcome a second-step cohort prejdú
```

## 13. Troubleshooting flow

```text
stable/canary release subjects
→ deployment/runtime identities
→ assignment rule/generation
→ effective traffic distribution
→ cohort composition
→ signal emission/denominator/freshness
→ stable comparison a dependencies
→ verdict transition
→ in-flight recovery
```

Competing hypotheses môžu byť wrong artifact, route mismatch, unstable assignment, biased cohort, telemetry gap, denominator defect, dependency-specific failure, insufficient sample alebo delayed outcome. Percent weight bez actual cohort evidence je slabý observation point.

## 14. Anti-patterny

### Canary iba podľa replica percenta

Replica ratio nemusí zodpovedať request alebo business exposure.

### Per-request random assignment

Multi-step journey môže miešať generations a zničiť stable cohort.

### HTTP attempts ako business denominator

Failed requests pred handlerom alebo async completion môžu vypadnúť.

### No data znamená no errors

Absencia evidence je inconclusive alebo telemetry failure.

### Promotion podľa krátkeho green okna

Low sample a delayed failures môžu vytvoriť false confidence.

## 15. Kontrolné otázky

1. Čím sa safety canary odlišuje od A/B experimentu?
2. Čo tvorí exact canary subject?
3. Prečo assignment unit musí zodpovedať journey?
4. Ako sa hodnotí representativeness?
5. Čo musí obsahovať observation contract?
6. Prečo readiness nepreukazuje exposure?
7. Kedy matched stable pomáha a kedy skresľuje?
8. Ako vzniká survivorship bias v telemetry?
9. Prečo no-data nie je pass?
10. Čo sa pokazilo v `REL-PAY-69`?
11. Ako abort rieši in-flight unknown outcomes?
12. Čo musí prejsť pred ďalším canary stepom?

## Glossary impact

Relevantné pojmy: canary deployment, bounded exposure, canary subject, assignment unit, assignment generation, stable cohort, representativeness, observation contract, authoritative denominator, matched stable, minimum logical operations, inconclusive verdict, survivorship bias, canary abort a in-flight reconciliation.

## Primárne zdroje

- [Google SRE Workbook — Canarying Releases](https://sre.google/workbook/canarying-releases/)
- [Argo Rollouts — Canary strategy](https://argo-rollouts.readthedocs.io/en/stable/features/canary/)
- [Flagger documentation](https://docs.flagger.app/)
- [Prometheus HTTP API](https://prometheus.io/docs/prometheus/latest/querying/api/)
- [Kubernetes documentation — Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Blue-green deployment](blue-green-deployment.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: A/B testing →](a-b-testing.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
