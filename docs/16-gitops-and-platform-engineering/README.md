# GitOps and Platform Engineering

Táto sekcia vysvetľuje, ako versionovaný platform a application intent prechádza cez Git authority, pull-based agents, continuous reconciliation, GitOps controllers, promotion, secrets a platform product boundaries až k bezpečnému self-service a multi-tenant runtime outcome-u.

GitOps tu nie je synonymum pre `YAML v Git-e` ani pre konkrétny tool. Platform engineering nie je iba centralizovaný tím, ktorý píše templaty. Obe oblasti sa posudzujú podľa explicitného authority, ownership, reconciliation, safety, usability a business outcome contractu.

## Predpoklady

Odporúča sa najprv dokončiť:

- [Git and Automation Basics](../03-git-and-automation/README.md),
- [CI/CD and Release Engineering](../05-ci-cd-and-release/README.md),
- [Infrastructure as Code and Configuration Management](../07-infrastructure-as-code-and-configuration-management/README.md),
- [Kubernetes](../09-kubernetes/README.md),
- [Helm and CKA](../10-helm-and-cka/README.md),
- [Security and Identity](../13-security-and-identity/README.md),
- [SRE and Operations](../14-sre-and-operations/README.md),
- [Databases and Distributed Systems](../15-databases-and-distributed-systems/README.md).

## Authoritative poradie — aktívne kapitoly

1. [Git ako source of truth](git-as-source-of-truth.md)
2. [Pull-based deployment](pull-based-deployment.md)
3. [Reconciliation a drift detection](reconciliation-and-drift-detection.md)
4. [Argo CD](argo-cd.md)

Aktuálny authoritative stav sekcie je **4/15 · In progress**.

## Plánované pokračovanie

Authoritative poradie bude pokračovať bez zmeny roadmapy:

5. Flux
6. Application promotion
7. GitOps secrets
8. Internal Developer Platform
9. Platform as a Product
10. Golden paths a paved road
11. Self-service
12. Developer experience
13. Service catalog
14. Guardrails
15. Multi-tenancy

## Connected learning scenario

### `GITOPS-PAY-61` — hidden desired state, hybrid deployment a false reconciliation verdict

Atlas Payments migroval production release `payments 9.0` na Argo CD.

Intended transition:

```text
application artifact + environment intent
→ reviewed environment commit 9f31c2a
→ authoritative production ref
→ Argo CD source observation
→ exact revision resolution a deterministic render
→ desired/live comparison
→ sync 63 resources
→ workload health
→ settlement canary a business acceptance
```

Git commit deklaroval:

```text
image digest:                 sha256:pay900a
route policy generation:     1842
replicas:                     24
termination grace:           45 s
```

Effective production writers však boli:

```text
Git environment repository
+ Argo CD parameter override
+ CI direct kubectl apply
+ on-call kubectl patch
+ HPA/admission runtime writers
```

Argo Application mala:

```yaml
spec:
  project: default
  source:
    targetRevision: production
  syncPolicy:
    automated:
      enabled: true
      prune: true
      selfHeal: false
```

Additional effective configuration:

- parameter override držal image digest `sha256:pay899hf7` a mal precedence nad Git values;
- CI runner mal production kubeconfig a po merge aplikoval render s route generation `1841`;
- on-call patchla live Deployment na `sha256:pay900b`;
- system-wide `ignoreDifferences` ignorovalo celý `/spec/template/spec/containers` subtree;
- production branch povoľovala force push;
- default AppProject povoľoval broad sources, destinations a resource kinds;
- resource tracking label modifikoval aj ďalší tool;
- health verdict kontroloval ready Pods, nie exact image/config generation ani settlement canary.

Timeline:

```text
20:14:03 → Git webhook refresh
20:14:04 → CI direct apply
20:14:07 → Argo sync
20:18:26 → human live patch
20:21:11 → production ref force-reset
20:28:09 → production ref restored
20:31:40 → Application Synced/Healthy
20:52:17 → business policy-generation mismatch potvrdený
```

Po 38 minútach existovali tri generations:

```text
Git declared:        pay900a / route 1842
Argo resolved:       pay899hf7 / route 1842
live Deployment:     pay900b / route 1841
running Pods:        pay900b + pay899hf7 cohorts
```

Potvrdené dôsledky:

- `18` Podov bežalo na `pay900b`, `6` na `pay899hf7` počas stalled rollout-u;
- `3 214` settlements použilo route policy generation `1841` namiesto `1842`;
- `96` operations vyžadovalo provider-ledger reconciliation;
- Git diff ani Argo sync status samostatne nevysvetľovali effective production state;
- rollback branch-e neodstránil CLI override ani live-only fields;
- CI compromise by mal direct production mutation path mimo GitOps controllera.

Causal boundaries:

- **Source-of-truth root cause:** critical desired fields mali viac authoritative writers a resolved desired state obsahoval hidden override mimo Git authority.
- **Pull-based root cause:** production deployment mal hybrid push/pull ownership; CI a humans držali direct credentials nad rovnakými fields ako Argo.
- **Reconciliation root cause:** broad ignore rule skryla Git-owned image/config drift a self-heal nebol schopný drift opraviť.
- **Argo CD root cause:** Application/AppProject contract bol príliš broad, používal mutable ref, hidden override, weak tracking a incomplete health oracle.
- **Amplifiers:** force push, absent writer inventory, shared instance label, no business canary a acceptance založená na `Synced/Healthy` labels.

Authoritative redesign:

```text
protected environment repository + immutable artifacts
→ Git-managed AppProject a Application
→ dedicated trusted sources/destinations/resources
→ fully qualified production ref
→ no ad-hoc parameter overrides
→ CI bez production cluster credentialu
→ Argo as sole Git-owned field writer
→ annotation tracking + installation identity
→ narrow diff exceptions
→ scoped automated sync/self-heal/prune
→ sync waves + PostSync business canary
→ exact Git/resolved/live generation evidence
→ mandatory break-glass reconciliation
```

Recovery flow:

```text
fence CI a human writers
→ preserve Git/Application/override/live/managedFields evidence
→ establish one authoritative desired generation
→ remove override a broad ignore rule
→ narrow field ownership
→ commit exact image/config state
→ reconcile Deployment/ReplicaSet/Pods
→ verify loaded policy generation a business cohort
→ revoke break-glass credentials
→ test direct drift, lost webhook, failed sync, rollback a second promotion
```

## Cieľ zvládnutia prvého bloku

### Git ako source of truth

- definovať exact desired-state subject a source-of-truth boundary;
- rozlíšiť Git desired, controller-resolved desired a live state;
- vysvetliť declarative, versioned a immutable desired generation;
- rozlíšiť commit identity od mutable branch/tag ref-u;
- identifikovať render inputs, parameter overrides a external writers;
- definovať authoritative promotion, field ownership a break-glass lifecycle;
- overiť reproducibility, rollback a second-change behavior.

### Pull-based deployment

- rozlíšiť push a pull podľa credential a execution boundary;
- vysvetliť automatic source observation a webhook ako hint;
- oddeliť pull model od auto-sync policy;
- navrhnúť scoped agent identity a target permissions;
- overiť source/render/policy pred mutation;
- definovať source/target outage a controller restart behavior;
- navrhnúť Git-recorded rollback a bounded break-glass path.

### Reconciliation a drift detection

- rozlíšiť desired, observed a effective runtime state;
- vytvoriť reconciliation loop s stable source/resource identity;
- klasifikovať unauthorized, controller-owned, defaulting, admission, dependency a runtime drift;
- vysvetliť semantic diff, normalization a managedFields evidence;
- navrhovať narrow ignore rules a explicitný field ownership;
- rozlíšiť Synced, Healthy a business accepted;
- overiť self-heal, prune, unknown apply outcome a hot-loop safety.

### Argo CD

- vysvetliť API server, repository server a application controller roles;
- definovať exact Application/AppProject subject;
- porovnať branch, tag, commit a chart tracking;
- diagnostikovať parameter overrides a multi-source precedence;
- navrhnúť automated sync, prune, self-heal a sync options;
- vysvetliť resource tracking, diff customization, phases, waves a hooks;
- oddeliť Argo sync/health status od business release acceptance;
- overiť source outage, wrong destination, direct drift a second-sync behavior.

## Dominantný model sekcie

```text
business alebo platform capability intent
→ exact desired-state, platform-product alebo tenant subject
→ declarative versioned authority a ownership boundaries
→ validated change, promotion alebo self-service request
→ pull agent/controller resolution a policy
→ desired-vs-observed comparison
→ bounded reconciliation, orchestration alebo provisioning
→ effective runtime, developer a business outcome
→ drift, feedback, recovery a lifecycle closure
→ second-change/second-tenant/second-failure validation
```

Každá komplexná kapitola musí rozlišovať:

- Git desired state, controller-resolved desired state a live/effective state;
- declarative intent od imperative execution detailu;
- immutable commit/artifact od mutable ref/tag/range;
- source commit od authoritative environment promotion;
- pull observation od webhook triggeru;
- pull model od automatic sync policy;
- target agent identity od CI/developer identity;
- drift detection od self-heal;
- expected controller mutation od unauthorized driftu;
- raw diff od semantic diffu;
- field ownera od technical field managera;
- Synced, Healthy a business accepted verdict;
- Application od ApplicationSet/template authority;
- platform capability od central-ticket service;
- paved path od mandatory lock-in;
- self-service request od unrestricted privilege;
- shared platform od tenant isolation boundary;
- configured object od valid/effective runtime mechanismu;
- trigger, root cause a causal amplifier;
- containment, reconciliation a authoritative recovery;
- first success od second-change, second-tenant a second-failure validation.

## Stav

| Téma | Status | Úroveň |
|---|---|---|
| Git ako source of truth | Learning | L2 |
| Pull-based deployment | Learning | L2 |
| Reconciliation a drift detection | Learning | L2 |
| Argo CD | Learning | L2 |
| Flux | Not Started | L0 |
| Application promotion | Not Started | L0 |
| GitOps secrets | Not Started | L0 |
| Internal Developer Platform | Not Started | L0 |
| Platform as a Product | Not Started | L0 |
| Golden paths a paved road | Not Started | L0 |
| Self-service | Not Started | L0 |
| Developer experience | Not Started | L0 |
| Service catalog | Not Started | L0 |
| Guardrails | Not Started | L0 |
| Multi-tenancy | Not Started | L0 |

Sekcia zostáva **In progress**. Stav **Ready for user review** možno použiť až po vytvorení všetkých 15 authoritative kapitol, overení complete navigation chainu, glossary, audit artifacts a finálnom section-level consistency passe.
