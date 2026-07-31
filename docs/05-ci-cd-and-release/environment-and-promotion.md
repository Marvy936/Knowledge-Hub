# Environment a promotion

Environment je identifikovateľný runtime, policy a shared-state context, do ktorého sa nasadzuje release subject. Nie je to iba názov ako `dev`, `staging` alebo `production`. Exact environment zahŕňa account alebo cluster, Region, namespace, infrastructure generation, identity a network policies, dependency endpoints, secret references, data state, admission behavior, observability a deployment history.

Promotion je riadené rozhodnutie použiť ten istý immutable release manifest v ďalšom environment-e. Neznamená rebuild, zmenu tagu ani kopírovanie ručne zvolených files. Dôveryhodná promotion zachová artifact identity, pridá target-specific configuration a evidence a po deployment-e overí effective runtime aj business outcome.

## 1. Dominantný manifest-to-environment model

```text
immutable release manifest
→ exact target environment subject
→ current effective a shared state
→ environment-specific configuration render
→ promotion policy a evidence freshness
→ lock alebo compare-and-set transition
→ deployment reconciliation
→ live/runtime/business read-back
→ promoted, paused, rejected alebo recovered verdict
```

Promotion je bezpečná iba vtedy, keď source environment evidence patrí rovnakému artifactu a relevantné target assumptions zostali platné. Zmena admission policy, database contractu, secret generation alebo network path môže evidence invalidovať aj bez zmeny application image.

## 2. Exact environment subject

Atlas Payments uchováva target identity ako machine-readable record:

```yaml
environmentSubject:
  environmentId: prod-eu-payments
  accountId: "482013771900"
  region: eu-central-1
  clusterUid: 9f041da2-1c20-4a31-9b4a-9c819f774402
  namespace:
    name: payments
    uid: 0318337d-4e50-49aa-8470-97a6c44fe5a0
  platformRelease: platform-2026.31
  infrastructureStateSha: sha256:tfstate1844
  admissionPolicySha: a18d2cf
  workloadIdentityPolicySha: 12c6be0
  databaseContract: settlement-schema-v42-expand
  eventContract: settlement-events-v18-compatible
  secretReferences:
    providerCredential: pv-43
  routeGeneration: 1843
```

Cluster name alebo kube context nie je stable identity. Context môže byť lokálne premenovaný a rovnaký názov môže ukazovať na iný API endpoint. Namespace name sa môže po delete/recreate opakovať; UID rozlišuje generation.

## 3. Praktický environment read-back

Pred promotion sa číta current target, nie cached dashboard:

```bash
kubectl config current-context
kubectl get namespace kube-system -o jsonpath='{.metadata.uid}{"\n"}'
kubectl get namespace payments -o jsonpath='{.metadata.uid}{"\n"}'
kubectl -n platform-system get configmap platform-release \
  -o jsonpath='{.data.release}{" "}{.metadata.resourceVersion}{"\n"}'
```

Výstup preukazuje current client context a observed objects na API serveri. Nepreukazuje, že user má oprávnenie na všetky promotion operations, že every node používa rovnakú platform generation ani že external dependencies zodpovedajú deklarovanému subjectu. Environment inventory kombinuje Kubernetes, cloud, database a provider read-backs.

Cloud caller identity sa overí samostatne:

```bash
aws sts get-caller-identity --output json | jq '{Account,Arn}'
```

Tento output preukazuje principal pre konkrétny request. Nepreukazuje effective permissions, session policy ani správny Kubernetes workload identity mapping.

## 4. Release manifest versus environment overlay

Release manifest vlastní immutable artifact graph a cross-environment contracts. Environment overlay vlastní target-specific desired state: replica count, endpoints, secret references, quotas a policy bindings. Overlay nesmie meniť artifact bytes ani skryto rebuildovať application.

```yaml
promotionSubject:
  releaseManifestDigest: sha256:release1000rc4
  targetEnvironmentId: prod-eu-payments
  targetEnvironmentGeneration: prod-eu-1844
  overlaySha: 71ac290
  renderedManifestDigest: sha256:render8841
  policyBundleSha: 66cf902
  evidenceBundleDigest: sha256:evidence1000rc4
```

Rendered manifest digest je dôležitý, pretože source overlay môže byť rovnaký a Helm/chart dependency alebo default generation sa môže zmeniť. Promotion record preto viaže inputs aj resolved output.

## 5. Render, admission a live state

Atlas vytvára render deterministicky:

```bash
helm dependency build deploy/chart
helm template payments deploy/chart \
  --namespace payments \
  --values environments/prod-eu.yaml \
  --set-string image.digest='sha256:pay1000api' \
  > rendered.yaml

sha256sum rendered.yaml
kubectl apply --server-side --dry-run=server -f rendered.yaml -o yaml > admitted.yaml
sha256sum admitted.yaml
```

Client render preukazuje output pre lokálne chart a values inputs. Server dry-run preukazuje validation a admission response v current API server generation. Ani jeden nepreukazuje live controller convergence. `admitted.yaml` sa má porovnať s expected critical fields a neskôr s live objectom.

```bash
kubectl diff --server-side -f rendered.yaml
```

`kubectl diff` ukazuje predicted differences podľa current API observation a admission. Nepreukazuje, že apply bude bez race condition; live state sa môže medzi diff a apply zmeniť.

## 6. Promotion evidence a applicability

Evidence sa nepromuje mechanicky podľa environment poradia. Každý dôkaz má subject a applicability boundary. Unit test je environment-independent, ak testuje immutable code. Staging identity test nemusí platiť pre production account. Performance evidence môže expirovať po zmene instance type alebo provider quota.

Promotion gate vyhodnocuje:

```text
artifact evidence
+ rendered configuration evidence
+ shared-state compatibility evidence
+ target environment health/capacity
+ target-specific security/identity evidence
+ current incidents a error budget
+ recovery readiness
→ promotion verdict
```

Evidence bundle má uvádzať `validFor`, `notAfter`, target assumptions a invalidation conditions. Screenshot dashboardu bez query, time range, cohort a subjectu nie je reusable promotion evidence.

## 7. Environment lock a compare-and-set

Dve promotions do rovnakého environmentu môžu vytvoriť interleaving. Lock nemá chrániť iba pipeline job; má chrániť environment transition a mať owner, lease duration a recovery.

Kubernetes Lease môže reprezentovať bounded ownership:

```yaml
apiVersion: coordination.k8s.io/v1
kind: Lease
metadata:
  name: payments-promotion
  namespace: payments
spec:
  holderIdentity: release-payments-10.0-rc4
  leaseDurationSeconds: 900
  acquireTime: "2026-07-31T12:00:00Z"
  renewTime: "2026-07-31T12:00:00Z"
```

Existencia Lease preukazuje desired lock record, nie automaticky correct mutual exclusion. Acquirer musí používať optimistic concurrency cez `resourceVersion`, renew lease a po expiry overiť, či predchádzajúca operation nezanechala partial state.

Environment transition má expected previous generation:

```text
current release = payments-9.9
current route generation = 1843
expected previous deployment revision = 280
→ apply release 10.0-rc4 iba ak všetky hodnoty stále sedia
```

Ak sa state zmenil, pipeline nemá prepisovať nový release starým planom.

## 8. Promotion identity a short-lived credentials

Promotion actor môže byť human approval authority, ale environment mutation má vykonať scoped workload identity. Credential subject má viazať repository, workflow, ref, environment a release operation.

```text
trusted promotion workflow
→ OIDC workload assertion
→ cloud role restricted na prod-eu-payments
→ short session
→ Kubernetes/environment mutation
→ audit event
→ expiry
```

Short lifetime znižuje exposure, ale broad role stále zostáva broad. Effective authorization sa testuje positive aj forbidden operations. Deployment identity smie meniť owned resources, no nesmie napríklad čítať unrelated tenant secrets alebo meniť cluster-wide admission policy.

## 9. Deployment record a effective-state closure

Promotion record sa neuzatvára po API apply. Musí korelovať desired, live, runtime, traffic a business states.

```bash
kubectl -n payments get deployment payments-api -o json | jq '{generation:.metadata.generation,observed:.status.observedGeneration,revision:.metadata.annotations["deployment.kubernetes.io/revision"],images:[.spec.template.spec.containers[].image]}'

kubectl -n payments get pods -l app=payments-api \
  -o jsonpath='{range .items[*]}{.metadata.uid}{" "}{.status.containerStatuses[0].imageID}{"\n"}{end}'
```

Deployment output preukazuje desired images a controller observation. Pod `imageID` preukazuje runtime-resolved content pre running containers. Nepreukazuje loaded feature flags, secret values alebo database schema. Application má publikovať release/config generation a capability canary musí potvrdiť business operation.

## 10. Drift a break-glass

Manual patch alebo external controller môže meniť live state po promotion. Drift nie je iba difference; treba určiť field ownership a authority. HPA môže legitímne meniť replicas, admission pridáva sidecar a operator spravuje derived objects. Git/release system má vlastniť iba explicitné fields.

Break-glass mutation má:

```text
incident reason a approver
→ short-lived scoped credential
→ exact bounded change
→ audit a evidence preservation
→ authoritative source reconciliation
→ effective-state validation
→ credential revocation
```

„Neskôr to prepíšeme do Git-u“ bez reconciliation deadline-u vytvára druhý source of truth.

## 11. Connected incident `REL-PAY-67`

Atlas schválil release `payments-10.0-rc4` podľa staging evidence. Promotion record obsahoval tag a environment name `production`, nie digest, cluster UID ani overlay SHA. Po staging teste platform tím zmenil admission policy a production namespace bol počas incident drill-u delete/recreate-nutý s novým UID.

Súčasne LaunchPad portal priamo patchoval ConfigMap s route generation, zatiaľ čo release pipeline aplikovala Helm overlay. Promotion získala stale lock, pretože predošlý job timeoutol po mutation a lock record sa iba časovo uvoľnil.

```text
staging evidence pre artifact A/env42
→ production env sa zmenil na env43
→ stale promotion plan
→ direct portal writer + pipeline writer
→ unknown previous transition
→ apply a traffic mismatch
```

Deployment Pods boli Ready, ale polovica cohorty používala route generation `1842` a druhá `1843`. 3 214 settlements skončilo v nesprávnom provider route a 96 operations vyžadovalo reconciliation.

Root cause bol nepresný environment a promotion subject. Názov `production` skryl novú environment generation a viac writers.

## 12. Recovery a acceptance verdict

Containment zablokuje portal aj pipeline writers, zachová managedFields, Lease, rendered/admitted manifests, ConfigMap revisions a traffic logs. Recovery určí jednu authoritative environment generation, zosúladí overlay a runtime ConfigMap, vytvorí fresh promotion plan a prečíta application-loaded route generation.

Environment/promotion contract je prijatý iba vtedy, keď:

```text
target identity obsahuje account/cluster/namespace generations
+ release manifest a overlay sú immutable
+ rendered a admitted outputs sú evidované
+ evidence applicability zodpovedá targetu
+ environment transition používa lock/CAS semantics
+ deployment identity je short-lived a scoped
+ live/runtime/traffic/business read-back korelujú
+ break-glass sa reconciliuje do authority
+ second writer je forbidden alebo explicitne field-scoped
+ druhá promotion neprepisuje novší state stale planom
```

## 13. Troubleshooting flow

Pri promotion incidente mapuj:

```text
release manifest a evidence
→ target account/cluster/namespace identity
→ current infrastructure/policy/data generations
→ overlay a rendered/admitted manifest
→ lock/CAS a writers
→ apply response a controller state
→ runtime image/config/secret generation
→ traffic a business outcome
```

Competing hypotheses môžu byť wrong target, stale overlay, admission change, concurrent promotion, manual drift, portal writer, secret mismatch, shared-state incompatibility alebo unknown previous operation. Before recovery zachovaj managedFields a operation records; re-apply ich môže prepísať.

## 14. Anti-patterny

### Environment definovaný iba názvom

Názov neodlišuje cluster, namespace alebo infrastructure generation.

### Promotion ako rebuild

Nové bytes nemajú validity predchádzajúceho evidence.

### `kubectl diff` ako race-free plan

State sa môže medzi diff a apply zmeniť; transition potrebuje expected generation.

### Manual approval ako environment lock

Human decision nebráni súbežnej automatizácii ani external writerovi.

### Break-glass bez reconciliation

Live-only fix vytvára nový source of truth a neskôr môže byť nepozorovane prepísaný.

## 15. Kontrolné otázky

1. Čo tvorí exact environment subject?
2. Prečo namespace name nie je generation identity?
3. Aký rozdiel je medzi release manifestom a environment overlayom?
4. Čo preukazuje server-side dry-run a čo nie?
5. Kedy target change invaliduje evidence?
6. Ako Lease pomáha a čo negarantuje?
7. Prečo promotion potrebuje compare-and-set semantics?
8. Aké permissions má mať deployment identity?
9. Ako sa overuje effective runtime state po apply?
10. Ktorí writers sa rozchádzali v `REL-PAY-67`?
11. Ako sa uzatvára break-glass mutation?
12. Ako sa testuje forbidden stale-plan promotion?

## Glossary impact

Relevantné pojmy: environment subject, cluster UID, namespace generation, release manifest, environment overlay, rendered manifest digest, admitted state, evidence applicability, promotion lock, compare-and-set transition, deployment identity, effective-state closure, field ownership, break-glass reconciliation a stale promotion plan.

## Primárne zdroje

- [Kubernetes documentation — Server-Side Apply](https://kubernetes.io/docs/reference/using-api/server-side-apply/)
- [Kubernetes API — Lease](https://kubernetes.io/docs/reference/kubernetes-api/cluster-resources/lease-v1/)
- [Helm documentation](https://helm.sh/docs/)
- [GitOps Principles](https://opengitops.dev/)
- [OpenID Connect Core](https://openid.net/specs/openid-connect-core-1_0.html)
- [SLSA specification](https://slsa.dev/spec/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Trigger, artifact a cache](trigger-artifact-cache.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Quality gates a approvals →](quality-gates-and-approvals.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
