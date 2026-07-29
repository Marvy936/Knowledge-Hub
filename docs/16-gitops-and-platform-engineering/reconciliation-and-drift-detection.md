# Reconciliation a drift detection

Reconciliation nie je periodické spustenie `kubectl apply`. Je to control loop, ktorý opakovane resolve-ne desired generation, pozoruje live state, klasifikuje rozdiel a vykoná iba mutation povolenú ownership, safety a recovery contractom.

Drift detection zase nie je synonymum pre automatickú opravu. Najprv musí spoľahlivo určiť, či rozdiel predstavuje incident, legitímny runtime writer, defaulting, stale observation alebo iba normalizačný artefakt.

## 1. Dominantný model

```text
exact desired-state generation
→ observed live/resource inventory
→ normalization a ownership context
→ desired-vs-observed delta
→ drift classification
→ report, ignore, adopt, reconcile alebo refuse
→ bounded mutation/prune
→ controller a workload convergence
→ health/business verification
→ second-observation a recurrence closure
```

Reconciliation verdict musí byť viazaný na exact source generation, exact live object identity a explicitný field ownership.

## 2. Desired, observed a effective state

### Desired state

Controller-resolved declarative target:

```text
repository + revision + path + parameters + generator
→ rendered desired objects
```

### Observed state

State načítaný z target API v konkrétnom observation čase.

### Effective runtime state

To, čo workload skutočne vykonáva:

```text
Deployment spec
→ ReplicaSet
→ Pods
→ loaded ConfigMap/Secret
→ service endpoints
→ application/provider behavior
```

Live Kubernetes object môže zodpovedať desired manifestu, ale runtime môže stále používať starú loaded configuration alebo nesprávny external dependency state.

## 3. Reconciliation subject

Reconciliation subject obsahuje:

- Application alebo controller identity;
- source revision a render inputs;
- target cluster, namespace a API discovery generation;
- desired resource set;
- tracked live resource set;
- object UID, API version a ownership/tracking identity;
- field managers a expected writers;
- normalization/defaulting/mutation behavior;
- diff a ignore policy generation;
- sync/prune/self-heal policy;
- health checks a business acceptance;
- retry, backoff a reconciliation interval;
- incident, rollback a decommissioning boundary.

Bez identity source aj live generation je `OutOfSync` iba label bez reprodukovateľného causal modelu.

## 4. Reconciliation loop

Typický loop:

```text
observe source
→ resolve revision
→ render desired resources
→ observe target resources
→ normalize
→ compare
→ classify delta
→ act alebo report
→ observe convergence
→ requeue
```

Každý loop musí byť:

- idempotentný voči už converged state-u;
- bounded počtom mutations a retries;
- resilientný voči source/target timeoutom;
- schopný pokračovať po controller restarte;
- truthful pri partial alebo unknown apply outcome-e;
- chránený pred delete stormom pri empty/failed renderi.

## 5. Drift taxonomy

Drift treba klasifikovať podľa príčiny a authority.

### Unauthorized manual drift

Human alebo pipeline zmení Git-owned field priamo v target API.

### Legitímny controller drift

HPA mení replicas alebo operator dopĺňa controller-owned fields podľa explicitného contractu.

### Defaulting drift

API server doplní default value, ktorá v source nie je explicitne uvedená.

### Admission mutation

Webhook zmení alebo doplní object pri create/update.

### Serialization alebo ordering drift

List order, omitted empty field alebo type normalization vytvára diff bez behavior change.

### Generated-resource drift

Operator vytvorí child resource, ktorý nemá byť priamo vlastnený GitOps Application.

### Dependency drift

Manifest je rovnaký, ale mutable image tag, chart dependency alebo external secret resolve-nul inú generation.

### Orphan drift

Live resource existuje, ale už nepatrí do desired inventory alebo stratil tracking identity.

### Missing drift

Desired resource bol zmazaný alebo nikdy nevznikol.

### Runtime drift

Object spec vyzerá správne, ale Pods, loaded config, network path alebo external state neplnia contract.

## 6. Diff pipeline

Raw YAML diff často nie je správny oracle.

```text
source manifests
→ render
→ API defaulting/schema normalization
→ known-type normalization
→ ignore rules
→ managed-field ownership
→ semantic diff
```

Diff engine musí rozlišovať:

- absent vs. explicit default;
- unordered vs. ordered lists;
- quantity formáty, napríklad `1000m` a `1`;
- controller-generated fields;
- status a metadata;
- fields vlastnené iným controllerom;
- immutable field replacement;
- unknown/custom resource schemas.

Normalizácia nesmie z critical behavior rozdielu vytvoriť false negative.

## 7. Ignore rules

Ignore rule je exception z drift oracle-u, nie všeobecný opravný nástroj.

Bezpečný ignore contract obsahuje:

- exact group/kind/name/namespace alebo úzky selector;
- exact JSON pointer/JQ path alebo manager;
- ownera a dôvod;
- expected writer;
- business impact;
- expiry alebo revalidation trigger;
- positive a negative test;
- monitoring ignored fieldov mimo sync statusu.

Nebezpečný príklad:

```yaml
ignoreDifferences:
  - group: apps
    kind: Deployment
    jqPathExpressions:
      - .spec.template.spec.containers
```

Také pravidlo môže skryť image, command, ports, environment, probes, resources aj security context.

## 8. Field ownership a managedFields

Kubernetes `managedFields` eviduje field management, ale nie je automatickým business authority verdictom.

```text
GitOps controller
→ image, labels, Pod template

HPA
→ replicas

external secret controller
→ Secret data

mutating webhook
→ injected sidecar
```

Ak dva writers vlastnia rovnaký field, vzniká:

- apply conflict;
- oscillation;
- repeated OutOfSync;
- hidden overwrite;
- stale ownership po migrácii apply mechanizmu.

Reconciliation design musí určiť, či sa field:

- riadi z Git-u;
- ignoruje, lebo ho vlastní explicitný controller;
- adoptuje do Git-u;
- odstráni z iného writera;
- migruje medzi field managers.

## 9. Drift detection vs. self-heal

```text
drift detection
→ zistenie a report rozdielu

self-heal
→ automated sync pri live drift-e
```

Self-heal môže byť vhodný pre:

- deleted resources;
- unauthorized image patch;
- zmenenú security policy;
- missing labels alebo routes.

Môže byť nebezpečný pri:

- emergency incident patchi;
- nejasnom field ownershipe;
- destructive prune;
- shared resource-e;
- migration hooku s external side effectom;
- source corruption;
- controller bug-e alebo incorrect renderi.

Preto self-heal potrebuje guardrails, nie slepú maximálnu agresivitu.

## 10. Sync status, health a business outcome

### Synced

Desired a live state sa podľa current diff rules nepovažujú za rozdielne.

### Healthy

Resource-specific health logic považuje resource graph za operationally healthy.

### Business accepted

Pôvodná business capability funguje pre intended cohort a forbidden outcomes nevznikajú.

```text
Synced
≠ Healthy
≠ business correct
```

Príklady:

- Deployment môže byť Synced, ale Progressing alebo Degraded;
- Deployment môže byť Healthy, ale používať stale feature/policy generation;
- Application môže byť OutOfSync iba pre harmless defaulted field;
- Application môže byť Synced, lebo critical field je ignorovaný.

## 11. Apply a unknown outcome

Controller môže po API timeout-e nevedieť, či mutation nastala.

```text
PATCH request odoslaný
→ API server mutation dokončil
→ response sa stratila
→ controller timeout
```

Bez fresh read-back môže retry:

- znovu spustiť hook;
- vytvoriť ďalší generated name resource;
- konfliktovať s novším writerom;
- nesprávne označiť operation ako failed.

Reconciliation musí používať stable object identity, idempotent apply semantics a post-timeout observation.

## 12. Prune a orphan handling

Prune odstráni tracked live resource, ktorý už nie je v desired set-e.

Riziká:

- failed render vyprodukuje empty set;
- path alebo ref sa zmení nesprávne;
- tracking metadata sa poškodí;
- resource bol adoptovaný iným ownerom;
- deletion propagation odstráni dependents;
- finalizer zablokuje sync;
- shared resource je omylom považovaný za application-owned.

Bezpečný prune contract:

```text
valid non-ambiguous desired inventory
→ tracked ownership proof
→ deletion eligibility
→ ordering/wave
→ bounded delete
→ dependent/business validation
```

## 13. Controller retry, backoff a hot loop

Permanentný diff môže vytvoriť reconcile storm:

```text
apply
→ mutating webhook prepíše field
→ diff
→ apply
→ ...
```

Hot loop spotrebúva:

- Kubernetes API QPS;
- repository render capacity;
- controller CPU/memory;
- audit/log volume;
- admission webhook capacity;
- downstream operator work.

Metrics majú zahŕňať:

- reconciliation duration a queue depth;
- source/render errors;
- compare latency;
- OutOfSync age;
- sync attempts/result;
- resource mutation count;
- repeated same-delta count;
- health transition latency;
- drift by writer/field/class;
- controller workqueue retries.

## 14. Drift response choices

Po klasifikácii driftu možno:

### Report

Drift je viditeľný, ale mutation vyžaduje approval.

### Reconcile

Git-owned unauthorized drift sa automaticky opraví.

### Ignore

Field patrí explicitnému writerovi a ignore scope je úzky.

### Adopt

Live value sa premení na reviewed desired-state commit.

### Refuse

Controller zastaví mutation, pretože authority alebo safety je nejasná.

### Contain

Suspend-ne Application, odoberie traffic alebo zablokuje ďalšie writers pri incidente.

Action musí byť odvodená z field authority a business risku, nie iba z diff existence.

## 15. Connected incident `GITOPS-PAY-61`

Po release `payments 9.0` Argo CD porovnávalo desired a live state podľa system-wide rule:

```yaml
resource.customizations.ignoreDifferences.apps_Deployment: |
  jqPathExpressions:
    - .spec.template.spec.containers
```

Rule vzniklo mesiace predtým pre sidecar injection problém, ale platilo pre všetky Deployments a celý containers subtree.

Súčasne:

- `selfHeal` bolo `false`;
- CI a on-call menili Deployment priamo;
- parameter override menil desired image mimo Git-u;
- HPA vlastnil replicas, ale writer contract nebol dokumentovaný;
- rollout health sa vyhodnocoval iba z ready Pods.

Observed generations:

```text
Git:                 pay900a / route 1842
Argo resolved:       pay899hf7 / route 1842
live Pod template:   pay900b / route 1841
running Pods:        pay900b + pay899hf7 cohorts
```

Diff pipeline odstránil z comparison celý containers subtree. Výsledok:

```text
critical image/env drift
→ normalization/ignore
→ no actionable delta
→ Application Synced
→ self-heal sa nespustí
```

### Reconciliation root cause

Drift oracle mal broad exception, ktorá skryla critical Git-owned fields. Reconciliation navyše nemala one-writer contract ani business generation oracle.

### Evidence

- live Deployment managedFields ukázali `argocd-controller`, CI service account aj human kubectl managera;
- compare output neobsahoval container diff;
- Argo history ukazovala successful sync na resolved override generation;
- 18 a 6 Podov používalo dve image generations;
- application metrics ukázali route-policy generation `1841` v request traces;
- Git commit `9f31c2a` nikdy nebol celý effective v production.

### Recovery

```text
freeze writers a preserve live YAML/managedFields
→ remove broad system ignore
→ create narrow sidecar-owned path rule
→ remove parameter override
→ commit exact desired image/config generation
→ enable self-heal pre Git-owned critical fields
→ reconcile Deployment/ReplicaSet/Pods
→ verify loaded policy generation
→ reconcile business cohort
→ inject second manual drift a verify repair
```

## 16. Reconciliation acceptance verdict

Reconciliation a drift detection sú prijaté, keď:

- exact desired revision/render a live resource identities sú explicitné;
- desired, observed a effective runtime state sú rozlíšené;
- diff normalization je schema-aware a testovaná;
- drift taxonomy odlišuje unauthorized, controller-owned, defaulted, mutated, dependency a runtime drift;
- field ownership a tracking identity sú explicitné;
- ignore rules sú úzke, owned, versioned a testované na false negatives;
- Synced, Healthy a business accepted verdicts sú oddelené;
- self-heal scope zodpovedá Git-owned fields a emergency contractu;
- apply timeout používa read-back a stable identity;
- prune vyžaduje valid desired inventory a ownership proof;
- controller loops majú backoff, rate limits a hot-loop detection;
- source corruption, empty render, target outage a controller restart behavior sú definované;
- manual drift, admission mutation, HPA ownership, missing resource, orphan, prune a second-reconcile tests prejdú;
- forbidden hidden image/config drift, oscillation, delete storm, false-Synced a false-Healthy outcomes sú odmietnuté.

## 17. Troubleshooting flow

```text
OutOfSync, false-Synced alebo reconcile loop
→ exact Application/source revision/render
→ tracked live resource UID a ownership identity
→ raw desired/live objects
→ normalization/defaulting/admission effects
→ ignore rules a managedFields
→ sync/self-heal/prune policy
→ controller operation/retry/read-back
→ workload loaded state a health
→ business generation/outcome
→ repair, second observation a recurrence control
```

## 18. Anti-patterny

### Každý drift treba automaticky revertovať

Nie, ak field vlastní HPA, operator alebo emergency writer podľa explicitného contractu.

### Ignore manager `kube-controller-manager`

Manager-wide ignore môže skryť viac fields než intended. Potrebný je exact field/risk model.

### Synced = deployed

Synced je diff verdict. Deployment potrebuje apply, health a business evidence.

### Healthy = správna verzia

Health logic môže potvrdiť ready Pods bez kontroly image/config generation.

### Prune opraví orphaned resources

Bez ownership proof môže odstrániť shared alebo adopted resource.

### Reconciliation sa môže opakovať donekonečna

Hot loop môže zničiť control-plane capacity a musí mať classification, backoff a alert.

## 19. Kontrolné otázky

1. Ako sa desired, observed a effective runtime state líšia?
2. Čo tvorí reconciliation subject?
3. Aké hlavné drift classes existujú?
4. Prečo raw YAML diff nie je vždy správny oracle?
5. Ako broad ignore rule vytvorí false negative?
6. Ako managedFields pomáhajú a kde nestačia?
7. Ako sa drift detection líši od self-heal?
8. Prečo Synced, Healthy a business accepted nie sú synonymá?
9. Ako controller rieši unknown apply outcome?
10. Čo musí overiť prune gate?
11. Prečo `GITOPS-PAY-61` ostal Synced?
12. Čo overuje reconciliation acceptance verdict?

## Glossary impact

Relevantné pojmy: reconciliation subject, desired state, observed state, effective runtime state, reconciliation loop, drift taxonomy, unauthorized drift, controller-owned drift, dependency drift, semantic diff, normalization, ignore rule, field ownership, managedFields evidence, self-heal, prune eligibility, orphan resource, reconcile hot loop, false-Synced, health verdict a reconciliation acceptance verdict.

## Primárne zdroje

- [OpenGitOps Principles](https://opengitops.dev/)
- [Kubernetes — Controllers](https://kubernetes.io/docs/concepts/architecture/controller/)
- [Argo CD — Diff Customization](https://argo-cd.readthedocs.io/en/latest/user-guide/diffing/)
- [Argo CD — Automated Sync Policy](https://argo-cd.readthedocs.io/en/stable/user-guide/auto_sync/)
- [Argo CD — Resource Tracking](https://argo-cd.readthedocs.io/en/stable/user-guide/resource_tracking/)
