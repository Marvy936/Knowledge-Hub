# Blue-green deployment

Blue-green deployment pripraví novú application generation v oddelenom produkčne relevantnom targete a potom zmení autoritatívny routing pointer zo starej generation na novú. Runtime capacity môže byť oddelená, no database, queues, caches, sessions, secrets a external side effects často zostávajú spoločné. Blue-green preto neznamená dve úplne nezávislé produkcie; znamená dva explicitné application targets a riadený cutover medzi nimi.

Hlavná výhoda je rýchly routing rollback, pretože old target môže zostať pripravený. Táto výhoda platí iba dovtedy, kým old generation zostáva compatible s current shared state a nebola nevratne zmenená environment alebo data authority. Prepnutie DNS alebo load balanceru späť na blue nevráti database migration, vydané events ani provider side effects.

## 1. Dominantný dual-target model

```text
blue active a exact shared-state generation
→ green provisioned z immutable release manifestu
→ green validation bez user trafficu
→ shared-state a cutover eligibility check
→ compare-and-set routing transition blue → green
→ effective dataplane read-back
→ blue drain a green observation
→ accept, route rollback alebo roll-forward
→ old target retention alebo retirement
```

Cutover je samostatná state transition. New target readiness nepreukazuje, že route sa zmenila, že clients prestali používať cached blue endpoint alebo že long-lived sessions prešli na green.

## 2. Exact blue-green subject

```yaml
blueGreenSubject:
  service: payments-api
  environmentGeneration: prod-eu-1844
  releaseManifestDigest: sha256:release1000rc4
  blue:
    targetId: payments-blue
    release: payments-9.9.3
    artifactDigest: sha256:pay993
    configurationSha: 5f91420
  green:
    targetId: payments-green
    release: payments-10.0.0-rc.4
    artifactDigest: sha256:pay1000api
    configurationSha: 71ac290
  routing:
    authority: trafficassignment/payments-api
    currentGeneration: 1843
    desiredGeneration: 1844
  sharedState:
    databaseContract: settlement-schema-v42-expand
    eventContract: settlement-events-v18-compatible
    sessionContract: session-v6-compatible
  retention:
    blueUntil: 2026-08-01T12:00:00Z
```

Farba nie je identity. `payments-blue` môže byť po viacerých releases novšia alebo staršia generation. Subject musí vždy uviesť exact artifacts, configuration a shared-state contract.

## 3. Environment parity a isolation

Green musí používať rovnaký production ingress, identity, admission, network, dependency a secret model, pokiaľ tieto dimensions ovplyvňujú risk. Validácia cez interný Pod IP nepreukazuje public TLS, load balancer headers ani workload identity.

Oddelené majú byť application resources a mutable runtime state, ktorý nesmie preskočiť medzi targets. Shared dependencies musia byť explicitné. Ak blue a green používajú rovnakú consumer group, green shadow validation môže ukradnúť production messages. Ak používajú rovnaký session store s incompatible serialization, už samotný startup green môže poškodiť blue sessions.

## 4. Provision green z immutable subjectu

```bash
kubectl -n payments set image deployment/payments-green \
  api='registry.atlas.example/payments-api@sha256:pay1000api'

kubectl -n payments annotate deployment/payments-green \
  atlas.example/release-manifest='sha256:release1000rc4' \
  atlas.example/config-sha='71ac290' --overwrite

kubectl -n payments rollout status deployment/payments-green --timeout=10m
```

Rollout status preukazuje controller convergence. Nepreukazuje public-route behavior ani business correctness. Runtime digest sa číta z Pods a loaded configuration z application endpointu alebo telemetry.

## 5. Green validation bez autoritatívnych side effects

Green sa validuje cez production-relevant path, no test traffic musí byť identifikovateľný a side effects bounded. Read-only requests sú jednoduché. Write path potrebuje test tenant, provider sandbox alebo explicitnú dry-run/compensation semantics.

```bash
curl --fail-with-body \
  --resolve payments-green.atlas.example:443:10.20.30.40 \
  -H 'X-Test-Tenant: atlas-canary' \
  -H 'Idempotency-Key: bg-green-rc4-001' \
  https://payments-green.atlas.example/api/settlements/canary
```

HTTP success preukazuje selected endpoint path a response. Nepreukazuje final authoritative settlement, absence duplicate provider effect ani route behavior pre bežných clients. Canary record sa koreluje s database, event a provider sandbox evidence.

## 6. Shared-state compatibility gate

Pred cutoverom sa overí, že blue aj green dokážu pracovať s current database, events, caches a sessions. Ak green startup spustil destructive migration, route rollback na blue môže byť invalidný.

Compatibility matrix:

```text
blue reader ↔ current schema/events
blue writer ↔ current schema/events
green reader ↔ current schema/events
green writer ↔ current schema/events
blue/green session and cache formats
```

Blue-green nemení potrebu expand-contract modelu. Iba skracuje application routing transition.

## 7. Compare-and-set cutover

Route transition má expected previous generation:

```yaml
apiVersion: delivery.atlas.example/v1
kind: TrafficAssignment
metadata:
  name: payments-api
spec:
  expectedGeneration: 1843
  desiredGeneration: 1844
  activeTarget: payments-green
  standbyTarget: payments-blue
```

```bash
kubectl -n payments apply -f cutover.yaml
kubectl -n payments get trafficassignment payments-api -o json | jq '{generation:.metadata.generation,observed:.status.observedGeneration,active:.status.activeTarget,effective:.status.effectiveTargets,conditions:.status.conditions}'
```

Controller read-back preukazuje desired/effective target podľa control plane-u. Nepreukazuje actual load-balancer dataplane alebo resolver/client caches. Access logs a synthetic clients musia potvrdiť green traffic a forbidden new blue admissions.

## 8. DNS, connection a session lag

Ak cutover používa DNS, resolver TTL a existing connections predlžujú mixed-target interval. Load balancer target switch môže byť rýchlejší, no keep-alive, WebSocket alebo session affinity stále držia blue connections.

```text
route authority changed
→ dataplane propagation
→ resolver/cache expiration
→ new connections select green
→ old blue connections drain
```

Acceptance má merať actual target distribution, nie iba route resource status. Old target sa nevypína, kým active blue operations a connections neprejdú bezpečný threshold alebo explicitný deadline/reconciliation.

## 9. Unknown cutover outcome

Timeout po route mutation môže znamenať, že cutover prebehol a response sa stratila. Blind retry s opačným assumption môže oscillovať target alebo prebiť novšiu generation. Pred ďalšou mutation sa číta route authority, dataplane a business cohort.

```text
cutover request timeout
→ state UNKNOWN
→ read desired/observed/effective route generation
→ sample actual requests
→ conclude blue / green / split / conflicting
→ až potom retry alebo recovery
```

## 10. Routing rollback a jeho limity

Route rollback je vhodný, keď blue je healthy a compatible s current shared state. Nie je vhodný, ak green už emitoval events, zmenil data semantics alebo provider state, ktoré blue nevie spracovať. Vtedy môže byť bezpečnejší roll-forward, feature disable alebo reconciliation.

Blue retention má cost a security limit. Standby target potrebuje patched dependencies a valid credentials. Po retention window sa old resources retirujú až po potvrdení recovery alternative.

## 11. Connected incident `REL-PAY-69`

Atlas pripravil green release s novou session serialization a expand migration, ale cache prefix neobsahoval release generation. Green pre-production validation zapísala session objects, ktoré blue nevedelo dekódovať. Cutover controller zmenil route generation 1844, no client timeout spôsobil, že pipeline transition zopakovala s pôvodným expected state.

```text
green validation nad shared cache
→ blue session corruption
→ cutover committed, acknowledgement lost
→ blind retry
→ route controller conflict a split targets
→ clients s cached sessions medzi blue/green
```

Dashboard ukazoval green Ready a route desired target green. Actual traffic bolo 72 % green, 28 % blue; blue vracalo session errors. 1 842 privileged sessions sa muselo zrušiť a znovu vytvoriť.

Root cause bol incomplete shared-state a unknown-outcome contract.

## 12. Redesign a acceptance verdict

Redesign pridá release-namespaced cache/session schema, pre-cutover compatibility test, compare-and-set route generations a read-back pred retry. Blue drain sa sleduje podľa active operations a actual traffic. Route rollback sa povoľuje iba pri current compatibility verdict-e.

Blue-green deployment je prijatý iba vtedy, keď:

```text
blue/green artifacts a configs sú exact
+ green používa production-relevant path
+ validation side effects sú bounded
+ shared-state compatibility pre oba targets je potvrdená
+ cutover používa CAS generation
+ control-plane aj dataplane read-back sú green
+ blue connections/operations sú drained
+ unknown outcome sa nere-tryuje naslepo
+ rollback eligibility je current
+ second cutover/recovery rehearsal prejde
```

## 13. Troubleshooting flow

```text
blue/green release subjects
→ shared data/cache/session state
→ green readiness a canary
→ route desired/observed generation
→ load-balancer/DNS dataplane
→ actual request/session cohorts
→ blue drain
→ rollback/roll-forward eligibility
```

Competing hypotheses môžu byť green application failure, shared-state corruption, stale route generation, DNS cache, connection stickiness, split dataplane, wrong target health alebo invalid blue rollback. Farba a readiness label nie sú dostatočné evidence.

## 14. Anti-patterny

### Dve deployments znamenajú úplnú izoláciu

Database, queues, caches a sessions často zostávajú shared.

### Green test cez interný Pod IP

Obchádza public TLS, ingress, identity a routing boundaries.

### Cutover success podľa API response

Timeout môže skrývať committed transition; read-back je povinný.

### Blue je vždy rollback target

Po shared-state alebo external-effect zmene môže byť blue nekompatibilné.

### Okamžité vypnutie blue

Stráca fast recovery a môže prerušiť existing connections alebo operations.

## 15. Kontrolné otázky

1. Čo blue-green oddeľuje a čo typicky zostáva shared?
2. Čo tvorí exact dual-target subject?
3. Prečo green validation musí používať production-relevant path?
4. Ako sa testujú bounded write side effects?
5. Prečo je shared-state compatibility potrebná pre oba targets?
6. Čo preukazuje route controller read-back a čo nie?
7. Ako DNS a keep-alive predlžujú cutover?
8. Čo je unknown cutover outcome?
9. Kedy routing rollback nie je bezpečný?
10. Čo sa pokazilo v `REL-PAY-69`?
11. Ako sa uzatvára blue drain?
12. Čo musí overiť second cutover rehearsal?

## Glossary impact

Relevantné pojmy: blue-green deployment, dual-target subject, active target, standby target, production-relevant validation, shared-state compatibility, cutover generation, compare-and-set routing, dataplane propagation, split target, blue drain, route rollback eligibility a target retirement.

## Primárne zdroje

- [Kubernetes documentation — Services](https://kubernetes.io/docs/concepts/services-networking/service/)
- [Kubernetes documentation — Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Gateway API documentation](https://gateway-api.sigs.k8s.io/)
- [AWS Elastic Load Balancing documentation](https://docs.aws.amazon.com/elasticloadbalancing/)
- [Google SRE — Reliable Product Launches at Scale](https://sre.google/workbook/launch-checklist/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Rolling update](rolling-update.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Canary deployment →](canary-deployment.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
