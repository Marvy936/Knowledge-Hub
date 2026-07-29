# GitOps source, pull, reconciliation a Argo CD lifecycles

## Desired-state subject

Exact repository, path, ref/commit, render inputs, target environment, object/field ownership, controller policy a acceptance scope deklaratívne riadeného system state-u. Pozri [Git ako source of truth](../docs/16-gitops-and-platform-engineering/git-as-source-of-truth.md).

## Source-of-truth boundary

Hranica určujúca, ktoré properties systému musí meniť iba authoritative versionovaný desired-state process a ktoré zostávajú runtime, observed alebo external state-om. Pozri [Git ako source of truth](../docs/16-gitops-and-platform-engineering/git-as-source-of-truth.md).

## Authoritative ref

Branch, tag, commit alebo release coordinate, ktorého transition predstavuje schválený desired-state alebo promotion decision pre konkrétny environment. Pozri [Git ako source of truth](../docs/16-gitops-and-platform-engineering/git-as-source-of-truth.md).

## Immutable desired generation

Reprodukovateľná combination commitov, artifact digestov, chart/plugin/tool versions, parameters a policy inputs, ktorá jednoznačne opisuje intended system state. Pozri [Git ako source of truth](../docs/16-gitops-and-platform-engineering/git-as-source-of-truth.md).

## Resolved desired state

Final desired manifests alebo object graph po resolve-nutí source refs, dependencies, values, parameters, overlays a generators controllerom. Pozri [Git ako source of truth](../docs/16-gitops-and-platform-engineering/git-as-source-of-truth.md) a [Argo CD](../docs/16-gitops-and-platform-engineering/argo-cd.md).

## Promotion transition — GitOps

Explicitná zmena authoritative environment reference alebo manifestu, ktorá po required evidence a approval-e povoľuje controlleru nasadiť novú generation. Pozri [Git ako source of truth](../docs/16-gitops-and-platform-engineering/git-as-source-of-truth.md).

## Environment repository

Repository alebo jeho authority boundary obsahujúca environment-specific desired state, napríklad image digests, routes, replicas, policy references a platform bindings. Pozri [Git ako source of truth](../docs/16-gitops-and-platform-engineering/git-as-source-of-truth.md).

## Render boundary — GitOps

Transition z versionovaných source inputs cez Helm, Kustomize alebo plugin generation na final manifest inventory porovnávaný a aplikovaný controllerom. Pozri [Git ako source of truth](../docs/16-gitops-and-platform-engineering/git-as-source-of-truth.md).

## Parameter override — GitOps

Desired-state input uložený mimo primary Git source values, ktorý môže mať precedence nad Git deklaráciou a vytvoriť hidden secondary authority. Pozri [Git ako source of truth](../docs/16-gitops-and-platform-engineering/git-as-source-of-truth.md) a [Argo CD](../docs/16-gitops-and-platform-engineering/argo-cd.md).

## Writer inventory — GitOps

Zoznam human, CI, GitOps, autoscaling, operator, admission a secret-management identities, ktoré môžu meniť konkrétne objects alebo fields. Pozri [Git ako source of truth](../docs/16-gitops-and-platform-engineering/git-as-source-of-truth.md).

## Field ownership — GitOps

Explicitný contract priraďujúci každý riadený field jednému authoritative writerovi alebo presne definovanému coordination modelu. Pozri [Git ako source of truth](../docs/16-gitops-and-platform-engineering/git-as-source-of-truth.md) a [Reconciliation a drift detection](../docs/16-gitops-and-platform-engineering/reconciliation-and-drift-detection.md).

## Break-glass writer

Short-lived incident identity alebo mutation path s bounded scope-om, auditom, expiry, povinným desired-state reconciliation a následným revocation. Pozri [Git ako source of truth](../docs/16-gitops-and-platform-engineering/git-as-source-of-truth.md) a [Pull-based deployment](../docs/16-gitops-and-platform-engineering/pull-based-deployment.md).

## Git desired state

State priamo deklarovaný v authoritative version control source pred controller resolution, overrides a runtime mutation. Pozri [Git ako source of truth](../docs/16-gitops-and-platform-engineering/git-as-source-of-truth.md).

## Controller desired state

Desired state, ktorý controller skutočne resolve-ol po aplikovaní refs, dependencies, parameters, overlays, plugins a internal normalization. Pozri [Git ako source of truth](../docs/16-gitops-and-platform-engineering/git-as-source-of-truth.md).

## Source-of-truth acceptance verdict

Dôkaz, že exact immutable desired generation, promotion authority, resolved inputs, writer/field ownership, rollback a second-change tests vytvárajú reprodukovateľný system intent bez hidden overrides. Pozri [Git ako source of truth](../docs/16-gitops-and-platform-engineering/git-as-source-of-truth.md).

## Pull-based deployment subject

Exact approved source, target environment, deployment agent, credentials, render, sync, health, rollback a continuous-observation scope jedného pull-based rollout-u. Pozri [Pull-based deployment](../docs/16-gitops-and-platform-engineering/pull-based-deployment.md).

## Target-side agent

Software agent pri target trust boundary, ktorý vlastnou scoped identity pulluje desired declarations a vykonáva compare/reconciliation proti target API. Pozri [Pull-based deployment](../docs/16-gitops-and-platform-engineering/pull-based-deployment.md).

## Source observation — GitOps

Polling, webhook-assisted refresh alebo iný mechanismus, ktorým agent zisťuje current authoritative desired-state generation. Pozri [Pull-based deployment](../docs/16-gitops-and-platform-engineering/pull-based-deployment.md).

## Webhook hint — GitOps

Event urýchľujúci source refresh, ktorý nenahrádza periodické observation a continuous reconciliation pri lost evente alebo source mutation bez eventu. Pozri [Pull-based deployment](../docs/16-gitops-and-platform-engineering/pull-based-deployment.md).

## Target credential boundary

Trust boundary určujúca, ktorá identity drží permission meniť production target a či CI/developer môže obísť pull agent. Pozri [Pull-based deployment](../docs/16-gitops-and-platform-engineering/pull-based-deployment.md).

## Agent-side policy

Validation a authorization vykonaná deployment agentom nad final rendered state-om a exact destination contextom pred target mutation. Pozri [Pull-based deployment](../docs/16-gitops-and-platform-engineering/pull-based-deployment.md).

## Push/pull hybrid

Deployment model, v ktorom GitOps agent, CI pipeline alebo humans súčasne menia rovnaký target state, čím vzniká multi-writer race a nejednoznačný rollback. Pozri [Pull-based deployment](../docs/16-gitops-and-platform-engineering/pull-based-deployment.md).

## Desired-state rollback

Nová schválená desired-state transition na compatible predchádzajúcu alebo opravenú generation, ktorú pull agent reconcile-ne do targetu. Pozri [Pull-based deployment](../docs/16-gitops-and-platform-engineering/pull-based-deployment.md).

## Pull-based acceptance verdict

Dôkaz, že scoped target agent automaticky pozoruje authoritative source, CI neobchádza mutation boundary, outage/break-glass/rollback paths sú bounded a second-pull obnoví convergenciu. Pozri [Pull-based deployment](../docs/16-gitops-and-platform-engineering/pull-based-deployment.md).

## Reconciliation subject — GitOps

Exact source/render generation, target resource inventory, tracking identity, field ownership, diff/ignore policy, sync/prune/self-heal behavior a acceptance scope jedného control loopu. Pozri [Reconciliation a drift detection](../docs/16-gitops-and-platform-engineering/reconciliation-and-drift-detection.md).

## Observed state — GitOps

Live target API state načítaný controllerom v konkrétnom observation čase a generation context-e. Pozri [Reconciliation a drift detection](../docs/16-gitops-and-platform-engineering/reconciliation-and-drift-detection.md).

## Effective runtime state — GitOps

Skutočná workload generation, loaded configuration, endpoints a external behavior vzniknuté z live objects a downstream controllers. Pozri [Reconciliation a drift detection](../docs/16-gitops-and-platform-engineering/reconciliation-and-drift-detection.md).

## Reconciliation loop — GitOps

Opakovaný chain source resolution, desired renderu, live observation, normalization, diffu, classified decisionu, bounded mutation a convergence verification. Pozri [Reconciliation a drift detection](../docs/16-gitops-and-platform-engineering/reconciliation-and-drift-detection.md).

## Drift taxonomy

Classification desired/live rozdielov na unauthorized, controller-owned, defaulted, admission-mutated, dependency, orphan, missing alebo runtime drift. Pozri [Reconciliation a drift detection](../docs/16-gitops-and-platform-engineering/reconciliation-and-drift-detection.md).

## Semantic diff — GitOps

Porovnanie desired a live resources po schema-aware normalization, field ownership a úzkych exceptions tak, aby verdict odrážal behavior-relevant delta. Pozri [Reconciliation a drift detection](../docs/16-gitops-and-platform-engineering/reconciliation-and-drift-detection.md).

## Ignore rule — GitOps

Versionovaná exception z diff oracle-u viazaná na exact resource/field/writera, dôvod, ownera, expiry a negative test. Pozri [Reconciliation a drift detection](../docs/16-gitops-and-platform-engineering/reconciliation-and-drift-detection.md).

## Self-heal — GitOps

Automated reconciliation live driftu späť na desired state bez potreby novej source revision, ak diff a policy označia field ako Git-owned a mutation ako safe. Pozri [Reconciliation a drift detection](../docs/16-gitops-and-platform-engineering/reconciliation-and-drift-detection.md).

## Prune eligibility — GitOps

Dôkaz, že live resource je tracked, desired inventory je validný a jeho deletion vrátane dependents je bezpečná a intended. Pozri [Reconciliation a drift detection](../docs/16-gitops-and-platform-engineering/reconciliation-and-drift-detection.md).

## False-Synced state

Status, pri ktorom diff pipeline pre broad ignore, normalization, tracking alebo hidden desired inputs neukáže behavior-critical rozdiel medzi intended a live state-om. Pozri [Reconciliation a drift detection](../docs/16-gitops-and-platform-engineering/reconciliation-and-drift-detection.md).

## Reconcile hot loop

Opakovaná apply–mutation–diff slučka bez convergencie, ktorá spotrebúva source, controller, API a admission capacity. Pozri [Reconciliation a drift detection](../docs/16-gitops-and-platform-engineering/reconciliation-and-drift-detection.md).

## Reconciliation acceptance verdict

Dôkaz, že schema-aware diff, tracking/field ownership, narrow ignore rules, self-heal/prune safety, health/business oracles a second-observation tests spoľahlivo detegujú a opravujú required drift. Pozri [Reconciliation a drift detection](../docs/16-gitops-and-platform-engineering/reconciliation-and-drift-detection.md).

## Argo CD Application subject

Exact Application UID/generation, AppProject, source revisions, render inputs, destination, sync/diff/tracking policy, credentials, controller generation, health a business acceptance scope. Pozri [Argo CD](../docs/16-gitops-and-platform-engineering/argo-cd.md).

## AppProject boundary

Argo CD policy boundary obmedzujúca trusted source repositories, destination clusters/namespaces, resource kinds a project roles pre skupinu Applications. Pozri [Argo CD](../docs/16-gitops-and-platform-engineering/argo-cd.md).

## Repository server — Argo CD

Argo CD component, ktorý získava source revisions a generuje Kubernetes manifests z repository URL, revision, path/chart, values, parameters a plugin settings. Pozri [Argo CD](../docs/16-gitops-and-platform-engineering/argo-cd.md).

## Application controller — Argo CD

Kubernetes controller, ktorý porovnáva Application desired/live state, vyhodnocuje sync a health a vykonáva sync, hooks, prune alebo self-heal podľa policy. Pozri [Argo CD](../docs/16-gitops-and-platform-engineering/argo-cd.md).

## Resolved revision — Argo CD

Exact commit SHA, chart version alebo iný immutable coordinate, na ktorý Argo CD resolve-ovalo configured branch, tag, range alebo symbolic target revision. Pozri [Argo CD](../docs/16-gitops-and-platform-engineering/argo-cd.md).

## Multi-source Application

Argo CD Application kombinujúca viac repository/chart/value sources do jedného rendered desired resource set-u a vyžadujúca evidence všetkých resolved revisions a precedence rules. Pozri [Argo CD](../docs/16-gitops-and-platform-engineering/argo-cd.md).

## Automated sync — Argo CD

Policy, pri ktorej Argo CD po zistení OutOfSync desired change-u automaticky vykoná sync bez direct deployment actionu CI pipeline. Pozri [Argo CD](../docs/16-gitops-and-platform-engineering/argo-cd.md).

## Allow-empty — Argo CD

Automated-sync option povoľujúca desired resource set bez objects; pri prune môže byť destructive a vyžaduje explicitný safety contract. Pozri [Argo CD](../docs/16-gitops-and-platform-engineering/argo-cd.md).

## Resource tracking method — Argo CD

Mechanizmus, ktorým Argo CD identifikuje resources patriace Application, napríklad annotation, annotation+label alebo label. Pozri [Argo CD](../docs/16-gitops-and-platform-engineering/argo-cd.md).

## Sync phase — Argo CD

Coarse deployment stage, napríklad PreSync, Sync alebo PostSync, určujúci lifecycle ordering hooks a resources počas sync operation. Pozri [Argo CD](../docs/16-gitops-and-platform-engineering/argo-cd.md).

## Sync wave — Argo CD

Numerické ordering resources v rámci sync phase, ktoré umožňuje postupné apply podľa dependencies a health gates. Pozri [Argo CD](../docs/16-gitops-and-platform-engineering/argo-cd.md).

## Resource hook — Argo CD

Kubernetes manifest označený hook annotation, ktorý Argo CD vykoná v definovanej sync phase a ktorého side effect, cleanup a retry musia byť idempotentné a recoverable. Pozri [Argo CD](../docs/16-gitops-and-platform-engineering/argo-cd.md).

## ApplicationSet authority

Generator/template vrstva, ktorá je authoritative nad generated Argo CD Applications a môže prepísať direct edit child Application objectu. Pozri [Argo CD](../docs/16-gitops-and-platform-engineering/argo-cd.md).

## Argo health verdict

Resource-specific Argo CD classification Healthy, Progressing, Degraded, Suspended, Missing alebo Unknown, ktorá nenahrádza business acceptance. Pozri [Argo CD](../docs/16-gitops-and-platform-engineering/argo-cd.md).

## Argo CD acceptance verdict

Dôkaz, že Application/AppProject, all resolved sources, scoped credentials, sync/prune/self-heal, tracking, diff, hooks, health a second-sync tests vytvárajú correct GitOps deployment bez hidden override alebo wrong destination. Pozri [Argo CD](../docs/16-gitops-and-platform-engineering/argo-cd.md).
