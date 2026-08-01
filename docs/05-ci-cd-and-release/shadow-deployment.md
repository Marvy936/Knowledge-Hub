# Shadow deployment

Shadow deployment vykonáva kópiu reálneho produkčného vstupu v novej implementation, ale shadow response ani mutations nesmú byť autoritatívne pre usera alebo business state. Jeho hodnota vzniká z vysokej fidelity workloadu: new release vidí reálnu distribution requestov, payloadov, tenants a dependencies. Jeho bezpečnosť vzniká iba vtedy, keď mirror, sanitization, identity a side-effect contracts zabránia neautoritatívnej execution ovplyvniť primary systém.

Shadow nie je „pošli request dvakrát“. Druhá execution môže spotrebovať provider quota, zapísať database, emitovať events, poslať email alebo ovplyvniť cache. Každý downstream dependency potrebuje explicitnú shadow semantics: sandbox, read-only, stub, isolated namespace, no-op writer alebo controlled comparison sink.

## 1. Dominantný mirror-to-comparison model

```text
primary production input
→ versionované mirror rozhodnutie
→ capture, sanitizácia a correlation identity
→ bounded asynchronous delivery do shadow
→ shadow execution v isolated authority context-e
→ non-authoritative outputs a side effects
→ primary/shadow normalization a comparison
→ coverage, fidelity, cost a safety verdict
→ promotion decision alebo remediation
```

Primary response path nesmie čakať na shadow. Shadow failure nesmie zmeniť user response. Mirror backlog však potrebuje bounds; nekontrolovaný replay môže po outage zahltiť dependencies.

## 2. Exact shadow subject

```yaml
shadowSubject:
  operation: create-settlement
  primary:
    release: payments-9.9.3
    artifactDigest: sha256:pay993
    configurationSha: 5f91420
  shadow:
    release: payments-10.0.0-rc.4
    artifactDigest: sha256:pay1000api
    configurationSha: 71ac290
  mirror:
    generation: shadow-pay-17
    samplingPercent: 10
    assignmentUnit: operation_id
    maximumLag: 30s
    maximumBacklog: 50000
  isolation:
    database: payments_shadow_17
    providerMode: sandbox
    eventTopic: settlements-shadow-17
    emailMode: sink
  comparisonSchema: settlement-result-v8
```

Shadow generation zahŕňa mirror aj dependency modes. Rovnaký code s iným sandbox alebo sanitization policy nie je rovnaký experiment.

## 3. Capture a correlation

Mirror má zachovať operation identity, primary release, event time a sanitized payload hash. Raw secrets, access tokens alebo personal data sa nemajú kopírovať bez explicitného privacy contractu.

```json
{
  "shadowGeneration": "shadow-pay-17",
  "operationId": "op-884211",
  "primaryRelease": "payments-9.9.3",
  "capturedAt": "2026-07-31T12:44:03Z",
  "payloadDigest": "sha256:payload884211",
  "sanitizationPolicySha": "sanitize-31",
  "replyExpected": false
}
```

Payload digest preukazuje identity sanitized recordu. Nepreukazuje, že sanitization zachovala fields potrebné pre behavior fidelity alebo odstránila všetky citlivé data. Policy tests a sampled manual review v controlled environment-e dopĺňajú evidence.

## 4. Asynchronous delivery a backpressure

Synchronous mirror v request path-e môže zvýšiť latency alebo zmeniť failure semantics. Preferred model publikuje bounded copy do queue alebo side channel. Ak mirror queue je plná, primary operation pokračuje a shadow coverage sa zníži podľa explicitnej policy.

```text
primary request accepted
→ authoritative execution
→ best-effort/bounded mirror record
→ primary acknowledgement nezávislý od shadow
```

Relevantné signals sú mirror acceptance ratio, queue age, dropped count, shadow processing lag a replay volume. Dashboard „shadow healthy“ bez coverage môže skrývať, že new release videla iba 2 % workloadu.

## 5. Dependency isolation

Každý external effect sa klasifikuje:

```text
read-only dependency
→ production read môže byť povolený podľa privacy/load contractu

mutable database
→ isolated schema/database alebo transaction rollback s jasnými limitmi

external provider
→ sandbox alebo protocol simulator; nikdy production mutation credential

message broker
→ shadow topic a consumer group

email/SMS/webhook
→ sink alebo explicitný allowlist test target
```

„Použi rovnaké credentials, ale nevolaj write endpoint“ je slabý control. Code bug alebo nový path môže write vykonať. Shadow identity nemá mať production mutation authorization.

## 6. Shadow environment read-back

Kubernetes identity a network restrictions sa overia:

```bash
kubectl -n payments-shadow get deployment payments-api-shadow -o json | jq '{images:[.spec.template.spec.containers[].image],serviceAccount:.spec.template.spec.serviceAccountName,labels:.metadata.labels}'

kubectl auth can-i create settlements.provider.atlas.example \
  --as=system:serviceaccount:payments-shadow:payments-shadow \
  -n payments
```

`kubectl auth can-i` preukazuje Kubernetes authorization verdict pre dané verb/resource impersonation podľa current API. Nepreukazuje cloud/provider permissions získané cez workload identity ani network reachability. Forbidden provider production operation sa testuje sandbox capability probe alebo cloud policy simulation.

## 7. Output normalization a comparison

Primary a shadow outputs môžu obsahovať timestamps, generated IDs alebo non-deterministic ordering. Comparator potrebuje versionovaný normalization contract.

```python
import json

def normalize(result: dict) -> dict:
    return {
        "decision": result.get("decision"),
        "provider_route": result.get("provider_route"),
        "fees_minor": result.get("fees_minor"),
        "required_review": result.get("required_review"),
    }
```

Normalized equality preukazuje selected fields. Nepreukazuje equivalence omitted side effects, latency alebo security decisions. Comparator inventory musí vychádzať z business contractu, nie z fields, ktoré sa ľahko porovnávajú.

## 8. Stateful a time-dependent behavior

Shadow môže spracovať request neskôr než primary. Current exchange rate, feature flag, inventory alebo provider state sa medzitým zmení. Exact replay potrebuje captured dependency snapshots alebo analysis, ktorá time skew akceptuje.

Shadow execution nesmie byť interpretovaná ako deterministic oracle, ak dependencies nie sú frozen. Difference sa klasifikuje na expected environmental, instrumentation, nondeterministic alebo semantic mismatch.

## 9. Capacity a cost

Mirroring 100 % trafficu môže zdvojnásobiť compute, logging, database reads a downstream load. Sampling má byť representative a bounded. Shadow telemetry musí mať cardinality/cost limits a oddelené alerts, aby nepage-ovala production on-call ako user-facing outage.

Load safety sa overí aj na primary dependencies. Read-only shadow queries môžu stále vyčerpať database pool alebo cache capacity.

## 10. Promotion use

Shadow evidence pomáha pri parser rewrite, migration logic, routing decision alebo new stack parity. Nepreukazuje user-perceived behavior, client interaction, browser state ani write correctness, ak writes sú stubbed. Promotion gate má presne uviesť, ktoré risks shadow pokrýva a ktoré zostávajú na canary alebo test environment.

## Doplnenie výkladu: duplikovaný traffic bez authoritative side effectu

Shadow deployment posiela kópiu production inputu candidate systému, ale primary response používateľovi pochádza zo súčasnej active path. Cieľom je pozorovať behavior pri realistickom trafficu bez exposure výsledku.

```text
primary request
→ active system → authoritative response/side effect
↘ shadow copy → candidate observation only
```

Najväčšie riziko je side-effect suppression. Candidate nesmie chargeovať kartu, posielať email alebo publikovať authoritative event. Nestačí zahodiť HTTP response; side effects môžu vzniknúť hlbšie.

Shadow input môže obsahovať PII alebo secrets. Kopírovanie do iného environmentu potrebuje data classification, masking a retention policy. Produkčné credentials sa nemajú automaticky preniesť.

Porovnanie outputs musí normalizovať nondeterministické fields, timestamps a IDs. Rozdiel neznamená automaticky defect; candidate môže mať vedome nový behavior. Comparator potrebuje domain rules.

Shadow lag a dropped copies sú evidence. Ak mirror posiela iba 60 % requestov alebo sa oneskoruje, coverage je neúplná. Shadow success nepreukazuje user-facing latency, pretože response nie je na critical path.

Cleanup odstráni mirroring rules, shadow data a temporary credentials. Candidate nemá zostať ako skrytý permanentný consumer.

## 11. Connected incident `REL-PAY-70`

Atlas shadowoval settlement requests do new routing engine. Shadow workload používal production provider credential, pretože tím chcel „maximálnu fidelity“. Application mala flag `shadow_mode=true`, ale nový error-recovery path ho nekontroloval a po timeout-e zavolal provider authorize endpoint.

```text
10 % mirrored production input
→ shadow provider request
→ timeout
→ recovery path mimo shadow guardu
→ production authorization side effect
→ primary request neskôr vykonal rovnaký effect
```

Shadow response sa userovi neposlala, ale 31 operations vytvorilo duplicate provider authorizations. Navyše mirror queue po outage replayla 48 000 records naraz a vyčerpala provider rate limit pre primary traffic.

Root cause bol capability a backpressure contract. Boolean flag nebol hard authority boundary.

## 12. Redesign a acceptance verdict

Redesign používa shadow-specific service account bez production mutation permission, provider sandbox, isolated event topic, bounded queue a replay rate. Comparator rozlišuje semantic output od side effects a environment/time differences.

Shadow deployment je prijatý iba vtedy, keď:

```text
primary/shadow/mirror generations sú exact
+ capture má correlation a privacy contract
+ primary response nezávisí od shadow
+ backlog, lag a drops sú bounded a visible
+ shadow identity nemá production mutation capability
+ dependencies majú explicitný isolation mode
+ comparison schema pokrýva relevantný business contract
+ differences sa klasifikujú, nie iba počítajú
+ forbidden provider mutation je testovaná
+ second replay po outage neohrozí primary capacity
```

## 13. Troubleshooting flow

```text
primary operation a release
→ mirror decision/coverage
→ sanitized captured record
→ queue/lag/replay
→ shadow identity a dependencies
→ shadow execution
→ outputs a side effects
→ normalization/comparison
→ primary impact
```

Competing hypotheses môžu byť missing mirror, sanitization drift, queue lag, stale dependency state, comparator defect, shadow write leak, shared cache interference alebo replay overload. Comparison mismatch samostatne neurčuje, ktorá implementation je správna.

## 14. Anti-patterny

### Boolean `shadow=true` ako jediný safety control

Code path môže flag obísť. Hard capability a dependency isolation sú potrebné.

### Synchronous shadow v primary requeste

Shadow latency alebo outage potom mení user-facing outcome.

### Production mutation credentials pre fidelity

Accidental side effect sa stáva production incidentom.

### Porovnanie iba response body

Omitted events, writes, latency a authorization decisions môžu zostať odlišné.

### Unlimited replay po outage

Backlog môže vyčerpať primary dependencies a provider quotas.

## 15. Kontrolné otázky

1. Čo robí shadow execution neautoritatívnou?
2. Čo tvorí exact shadow subject?
3. Prečo mirror nemá blokovať primary response?
4. Ako sa meria shadow coverage?
5. Prečo production read môže byť tiež rizikový?
6. Čo preukazuje `kubectl auth can-i` a čo nie?
7. Ako normalization ovplyvňuje comparison verdict?
8. Prečo time skew vytvára expected differences?
9. Aké risks shadow nepreukazuje?
10. Čo spôsobilo duplicates v `REL-PAY-70`?
11. Ako sa testuje forbidden production mutation?
12. Ako sa riadi replay backlog?

## Glossary impact

Relevantné pojmy: shadow deployment, mirrored input, shadow subject, non-authoritative execution, capture record, sanitization generation, shadow coverage, shadow lag, dependency isolation mode, shadow capability, output normalization, semantic mismatch, replay backpressure a shadow side-effect leak.

## Primárne zdroje

- [Google Cloud Architecture — Deployment archetypes](https://cloud.google.com/architecture/application-deployment-and-testing-strategies)
- [Istio — Mirroring](https://istio.io/latest/docs/tasks/traffic-management/mirroring/)
- [Envoy — Request mirroring](https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_conn_man/route_config/route)
- [Kubernetes authorization](https://kubernetes.io/docs/reference/access-authn-authz/authorization/)
- [NIST Privacy Framework](https://www.nist.gov/privacy-framework)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: A/B testing](a-b-testing.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Ring deployment →](ring-deployment.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
