# Progressive delivery

Progressive delivery je riadený release system, ktorý po malých krokoch zosúlaďuje application deployment, traffic, audience, feature behavior a data-migration state s produkčnou evidence. Nie je to synonymum pre pomalý rollout ani jedna konkrétna strategy. Je to reconciliation loop nad viacerými control planes, ktoré sa môžu meniť nezávisle a dočasne sa rozísť.

Release môže mať new Pods nasadené, ale nulový traffic. Traffic môže byť na new release, no feature zostáva off. Feature môže byť enabled pre ring 1, zatiaľ čo database backfill ešte nepokrýva všetky rows. Dôveryhodný controller preto nesleduje jeden percent bar. Sleduje exact multi-axis state a povoľuje iba bounded transition, ktorého preconditions a recovery sú známe.

## 1. Dominantný multi-axis control loop

```text
versionovaný rollout contract
→ observed application/traffic/audience/feature/data state
→ precondition a generation validation
→ jeden bounded transition
→ controller/runtime read-back
→ technical, functional a business evidence
→ promote / pause / abort / inconclusive / invalid
→ authoritative recovery alebo next transition
→ closure a old-state retirement
```

Progressive delivery je bezpečná iba vtedy, keď jednotlivé control planes majú authority, generation a read-back. Ak portal mení feature flag, service mesh traffic a migration job data state bez spoločného contractu, „rollout 25 %“ nemá jednoznačný význam.

## 2. Exact rollout contract

```yaml
rolloutContract:
  id: ROLLOUT-PAY-1000-RC4
  releaseManifestDigest: sha256:release1000rc4
  targetEnvironmentGeneration: prod-eu-1844
  axes:
    application:
      stableDigest: sha256:pay993
      candidateDigest: sha256:pay1000api
    traffic:
      authority: trafficassignment/payments-api
      generation: 1844
    audience:
      ringProgramGeneration: payments-rings-v12
    feature:
      flag: settlement-review-v2
      generation: flag-pay-882
    data:
      schemaContract: settlement-schema-v42-expand
      backfillGeneration: backfill-pay-42-7
  steps:
    - id: deploy-dark
      traffic: 0
      feature: false
    - id: ring0-2-percent
      traffic: 2
      audience: ring0
      feature: true
    - id: ring1-10-percent
      traffic: 10
      audience: ring1
      feature: true
    - id: general-availability
      traffic: 100
      feature: true
  recoveryReference: recovery-payments-10.0-rc4
```

Contract definuje intended states, nie current reality. Controller pred každým stepom číta actual generations a odmietne transition, ak sa iný writer alebo incident response odchýlili od expected previous state-u.

## 3. Observed multi-axis state

```bash
kubectl -n payments get deployment payments-api -o json | jq '{generation:.metadata.generation,observed:.status.observedGeneration,images:[.spec.template.spec.containers[].image]}'

kubectl -n payments get trafficassignment payments-api -o json | jq '{generation:.metadata.generation,observed:.status.observedGeneration,effective:.status.effectiveWeights}'

curl --fail https://payments-api.internal/management/config-generation | jq '{release,flagGeneration,schemaContract,backfillGeneration}'
```

Tieto read-backs preukazujú Kubernetes control state a application-declared loaded generations. Nepreukazujú actual request distribution, authoritative database completeness ani correctness feature evaluation. Observation model kombinuje controller state, runtime telemetry a business records.

## 4. One transition at a time

Keď controller naraz zvýši traffic, zapne flag a spustí destructive migration, failure má viac možných príčin a recovery môže byť nejednoznačná. Bounded transition mení jednu risk dimension alebo explicitne koordinovaný atomic set.

```text
application dark deploy
→ verify runtime
→ bounded traffic without feature
→ verify infrastructure path
→ enable feature for stable ring
→ verify behavior
→ widen audience
→ complete data migration
```

Nie každý systém môže oddeliť všetky axes. Vtedy rollout contract musí pomenovať coupled transition a zvýšiť evidence/recovery requirements.

## 5. Preconditions a stale-plan protection

Transition používa expected current generations:

```json
{
  "expected": {
    "applicationRevision": 281,
    "trafficGeneration": 1844,
    "flagGeneration": "flag-pay-882",
    "schemaContract": "settlement-schema-v42-expand"
  },
  "desiredStep": "ring1-10-percent"
}
```

Ak current state nesedí, controller nevykoná stale plan. Human break-glass môže byť legitimate, ale musí vytvoriť new observed state a explicitné reconciliation decision.

## 6. Evidence contract per step

Každý step má vlastnú risk question. Dark deploy overuje startup, identity a dependencies. Initial traffic overuje request path. Feature activation overuje new behavior. Wider ring pridáva population diversity. Data contract step overuje migration progress a mixed-version safety.

Evidence zahŕňa:

```text
runtime generation and eligibility
+ actual traffic/audience/variant distribution
+ technical SLO and saturation
+ logical business outcomes
+ forbidden duplicate/lost/cross-tenant outcomes
+ telemetry freshness and coverage
+ recovery eligibility
```

One global dashboard nemá dostatočný subject ani applicability.

## 7. Analysis verdicts

Progressive controller používa viac states:

- **PROMOTE** — step splnil preconditions a evidence contract;
- **PAUSE** — state zostáva bounded a čaká na additional evidence alebo human context;
- **ABORT** — new exposure sa zastaví a spustí recovery;
- **INCONCLUSIVE** — sample, telemetry alebo duration nestačí;
- **INVALID** — observed state nezodpovedá rollout contractu, napríklad external writer zmenil flag;
- **COMPLETE** — full acceptance a retirement conditions sú splnené.

`INVALID` je dôležitý. Controller nesmie hodnotiť metrics pre state, ktorý sa v skutočnosti nevykonal podľa contractu.

## 8. Controller coordination a ownership

Argo Rollouts, service mesh, feature platform a migration operator môžu byť samostatné controllers. Jeden orchestrator nemusí vlastniť všetky resources, ale rollout contract potrebuje ownership graph a authoritative observation.

```text
application controller owns Deployment
traffic controller owns TrafficAssignment
flag platform owns targeting rules
data operator owns migration CR
progressive coordinator owns allowed sequence and verdict
```

Field ownership a idempotency keys bránia controllers navzájom si prepisovať desired state.

## 9. Failure containment

Pri failure sa najprv zmrazia ďalšie transitions. Nie vždy sa okamžite rollbackuje všetko. New operations sa môžu route-nuť na stable, feature vypnúť a existing candidate operations reconciliovať.

```text
freeze rollout generation
→ preserve observed multi-axis evidence
→ stop new exposure
→ classify in-flight and shared-state delta
→ choose per-axis recovery
→ validate stable plus forbidden outcome
```

Automatický global rollback môže vrátiť application, ale nevráti data alebo external effects.

## 10. Delayed watch a closure

Full traffic nie je closure. Release zostáva v delayed watch pre credential expiry, memory growth, backlog, data convergence a support signals. Old release/flag/schema compatibility sa odstráni až po consumer inventory a recovery decision.

Closure obsahuje:

```text
full desired/effective exposure
+ business acceptance
+ no unresolved reconciliation backlog
+ new recovery baseline
+ old cohort drained
+ temporary flags/rules retired or owned
+ evidence and decision record retained
```

## Doplnenie výkladu: viac control planes a postupný verdict

Progressive delivery automatizuje alebo riadi postupné exposure podľa evidence. Môže kombinovať deployment cohorts, traffic weights, rings a feature flags. Každá os má vlastnú generation.

```text
application generation
traffic route generation
feature-flag generation
configuration/schema generation
```

Verdict musí vedieť, ktorá kombinácia bola pozorovaná. „Canary 10 %“ je neúplné, ak polovica canary cohorty mala flag off.

Controller vykonáva state machine: nastaví exposure, čaká na convergence, zbiera metrics, vyhodnotí analysis a rozhodne promote/hold/abort. Timeout alebo lost response môže zanechať unknown route state; pred ďalšou mutation sa vykoná read-back.

Analysis template je code/policy. Query musí mať správne labels, denominator a no-data semantics. Green dashboard screenshot nie je reprodukovateľný verdict.

Step duration musí pokryť warm-up a delayed outcomes. Príliš rýchle promotion môže prejsť skôr, než sa objavia queue, memory leak alebo business reconciliation failures.

Progressive delivery znižuje blast radius, nie pravdepodobnosť všetkých defectov. Shared database migration môže ovplyvniť 100 % users aj pri 1 % traffic canary.

## 11. Connected incident `REL-PAY-71`

Atlas rollout mal application controller, service-mesh traffic, feature platform a backfill job. Portal ukazoval jeden progress `25 %`, ale axes boli:

```text
application: 25 % new Pods
traffic: 10 % canary requests
feature: 100 % enterprise accounts na new path kvôli stale override
data: backfill 42 % complete
```

Controller vyhodnotil canary podľa release labelu na requests, no feature enabled new behavior aj na stable Pods. Backfill worker používal stale snapshot a prepísal novšie live rows. Po latency alert-e automation vykonala `rollout undo`, ale flag a backfill pokračovali.

Výsledkom bolo 83 stale data overwrites, 31 duplicate provider effects a mixed behavior na old release. Root cause bol neexistujúci multi-axis contract a recovery.

## 12. Redesign a acceptance verdict

Redesign zavedie rollout contract s expected generations, one-transition steps, one authoritative flag writer a version-safe backfill. Verdict je invalid, ak actual population alebo loaded generation nesedí. Recovery má per-axis plan a reconciliation.

Progressive delivery je prijatá iba vtedy, keď:

```text
all control axes a authorities sú inventarizované
+ release/target/axis generations sú exact
+ each transition má expected previous state
+ one bounded risk change je explicitný
+ actual population and loaded state sa read-backne
+ evidence je step-specific a authoritative
+ invalid/inconclusive nie sú pass
+ recovery je per-axis a shared-state aware
+ forbidden split-generation state je testovaný
+ delayed watch a retirement closure prejdú
```

## 13. Troubleshooting flow

```text
rollout contract a current step
→ application desired/runtime state
→ traffic authority and actual distribution
→ audience membership
→ flag published/loaded/effective state
→ schema/backfill state
→ evidence population
→ verdict and recovery actions
```

Competing hypotheses môžu byť wrong release, route lag, ring cache, stale flag, backfill race, telemetry population mismatch alebo controller conflict. Percent progress nemá diagnostic authority.

## 14. Anti-patterny

### Jeden progress bar pre viac axes

Skryje, ktoré state transitions sa skutočne vykonali.

### Súčasná zmena trafficu, flagu a data

Zhoršuje causal diagnosis aj recovery.

### Metrics analysis nad invalid state-om

Ak actual cohort nezodpovedá contractu, result nemá applicability.

### Automatický global rollback

Application rollback nemusí zrušiť feature, data alebo external effects.

### Full traffic ako okamžitá closure

Delayed failures a old-state retirement zostávajú neoverené.

## 15. Kontrolné otázky

1. Čo progressive delivery pridáva nad canary strategy?
2. Ktoré control axes má rollout contract inventarizovať?
3. Prečo intended state nestačí?
4. Ako stale-plan protection chráni transition?
5. Prečo sa preferuje one bounded transition?
6. Čo znamená `INVALID` verdict?
7. Ako sa koordinujú viaceré controllers?
8. Prečo recovery musí byť per-axis?
9. Čo sa rozchádzalo v `REL-PAY-71`?
10. Ako version-safe backfill súvisí s rolloutom?
11. Čo obsahuje delayed watch?
12. Kedy možno old state retirenúť?

## Glossary impact

Relevantné pojmy: progressive delivery, rollout contract, control axis, multi-axis state, bounded transition, expected previous generation, stale-plan protection, step-specific evidence, invalid rollout state, progressive coordinator, per-axis recovery, delayed watch a rollout closure.

## Primárne zdroje

- [Argo Rollouts documentation](https://argo-rollouts.readthedocs.io/)
- [Flagger documentation](https://docs.flagger.app/)
- [OpenFeature specification](https://openfeature.dev/specification/)
- [GitOps Principles](https://opengitops.dev/)
- [Google SRE Workbook — Canarying Releases](https://sre.google/workbook/canarying-releases/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Feature flags](feature-flags.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Rollback a roll-forward →](rollback-and-roll-forward.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
