# GitOps and Platform Engineering

Táto sekcia vysvetľuje, ako versionovaný application a platform intent prechádza cez Git authority, pull-based agents, continuous reconciliation, GitOps controllers, promotion, secret lifecycle a platform-product boundaries až k bezpečnému self-service a multi-tenant runtime outcome-u.

GitOps tu nie je synonymum pre `YAML v Git-e` ani pre konkrétny tool. Platform engineering nie je iba centralizovaný tím, ktorý píše templaty alebo prevádzkuje portal. Obe oblasti sa posudzujú podľa explicitného authority, ownership, reconciliation, safety, usability, operability a business-outcome contractu.

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
5. [Flux](flux.md)
6. [Application promotion](application-promotion.md)
7. [GitOps secrets](gitops-secrets.md)
8. [Internal Developer Platform](internal-developer-platform.md)

Aktuálny authoritative stav sekcie je **8/15 · In progress**.

## Plánované pokračovanie

Authoritative poradie bude pokračovať bez zmeny roadmapy:

9. Platform as a Product
10. Golden paths a paved road
11. Self-service
12. Developer experience
13. Service catalog
14. Guardrails
15. Multi-tenancy

## Connected learning scenarios

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

Po 38 minútach existovali tri desired/live generations a dva running cohorts:

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

### `GITOPS-PAY-62` — stale promotion, hidden Flux input, broken secret rotation a false platform success

Atlas Payments po `GITOPS-PAY-61` zaviedol Flux a interný portal LaunchPad pre release `payments 9.1`. Cieľom bolo odstrániť direct production writers a spojiť image automation, promotion, secrets a platform self-service do jedného auditovateľného flowu.

Intended transition:

```text
immutable image sha256:pay910a
→ staging image-update commit
→ staging Flux source artifact a reconciliation
→ provider credential generation pv-42
→ route policy generation 1850
→ staging settlement canary
→ promotion PR kopírujúci exact image/config/secret contract
→ production Flux reconciliation
→ runtime generation verification
→ production settlement canary
→ LaunchPad operation completion
```

Skutočný authority graph však obsahoval päť writers a tri mutable boundaries:

```text
Git environment repository
+ Flux ImageUpdateAutomation nad shared base
+ LaunchPad direct cluster ConfigMap writer
+ shared SOPS age decryption identity
+ human emergency Kubernetes Secret writer
```

Konkrétne:

- staging aj production source sledovali mutable `main`;
- image automation zapisovala image update do shared base, ktorý konzumovali oba environmenty;
- production `Kustomization` používala `postBuild.substituteFrom` ConfigMap `launchpad-runtime`, ktorú portal menil priamo v clusteri;
- staging evidence bola viazaná na `pay910a`, route generation `1850` a credential contract `pv-42`;
- kým promotion čakala na approval, image automation zmenila shared base na `pay910b` a LaunchPad zmenil route substitution na `1849`;
- merge automation proposal rebase-la bez final-render a evidence revalidation;
- SOPS payloady pre staging aj production boli decryptovateľné jedným shared age private keyom v `flux-system`;
- provider credential sa neskôr rotoval z `pv-42` na `pv-43`, ale Pods čítali Kubernetes Secret cez environment variables a neprebehla consumer rollout/reload;
- LaunchPad označil request ako `Completed` po vytvorení alebo merge promotion PR-u, nie po production reconciliation a business canary.

Timeline:

```text
10:02:11 → image automation commitne pay910a do staging
10:08:44 → staging canary prejde na route generation 1850
10:11:03 → promotion request načíta staging evidence
10:12:17 → image automation prepíše shared base na pay910b
10:13:04 → LaunchPad zmení cluster ConfigMap route=1849
10:14:22 → promotion PR merge
10:15:01 → production Flux source artifact b71f203
10:15:09 → Flux apply: pay910b + route 1849
10:16:31 → Kustomization Ready=True
10:19:18 → provider credential rotovaný na pv-43
10:23:47 → prvé provider authentication failures
10:31:02 → incident potvrdený
```

Výsledný generation graph:

```text
approved staging evidence: pay910a / route 1850 / credential pv-42
promotion UI subject:      pay910a / route 1850
Flux rendered desired:     pay910b / route 1849 / Secret pv-42
running process state:     pay910b / route 1849 / loaded pv-42
provider authority:        credential pv-43 active, pv-42 revoked
```

Potvrdené dôsledky:

- `2 746` settlements bolo routovaných cez stale route generation `1849`;
- `61` provider calls zlyhalo po revocation credentialu `pv-42`;
- retry flow vytvoril `14` unknown outcomes vyžadujúcich provider reconciliation;
- LaunchPad zobrazoval operation ako completed `17` minút pred potvrdením production failure;
- rovnaký Git source revision mohol pri zmene cluster-local ConfigMap-u vyrenderovať iný effective desired state;
- manual Secret patch a Flux desired state vytvorili writer oscillation;
- shared decryption identity zväčšila blast radius kompromitovaného controllera alebo key materialu.

Causal boundaries:

- **Flux root cause:** source artifact neidentifikoval celý effective render graph, pretože critical `substituteFrom` input bol mutable a riadený mimo Git-u; `Ready=True` zároveň neoverovalo runtime route ani loaded secret generation.
- **Promotion root cause:** approval nebola compare-and-swap decision nad immutable candidate, transitive dependencies a target base revision; final merge neinvalidoval stale evidence.
- **GitOps secrets root cause:** rotation nemala authoritative desired-state transition, overlap window ani consumer-convergence oracle; shared decryption key a manual target patch porušili environment a writer boundary.
- **IDP root cause:** portal task completion bol zamenený za usable platform capability; workflow nemal durable end-to-end operation state a portal sa stal direct runtime writerom.
- **Amplifiers:** shared base, mutable branch, absent final render, environment-variable secret consumption, no version endpoint, no production business canary a retry bez semantic operation identity.

Authoritative redesign:

```text
immutable release manifest R-910a
→ pins image/chart/policy/schema/secret-reference contract
→ staging desired state references R-910a
→ staging evidence bound to R-910a + exact environment revision
→ production proposal changes only release-manifest reference
→ target-base compare-and-swap + final-merge render/policy revalidation
→ environment-specific immutable Flux source coordinate
→ no cluster-local critical substitutions
→ namespace-scoped Flux apply identity
→ environment-scoped SOPS KMS decryption identity
→ secret pv-43 overlap rotation
→ target Secret generation triggers Pod rollout
→ workload endpoint reports artifact/config/secret generations
→ provider audit confirms pv-43 consumer convergence
→ production settlement canary
→ durable LaunchPad operation becomes Succeeded
```

Recovery flow:

```text
freeze promotion, image automation a LaunchPad direct writer
→ preserve Git/source artifacts/Kustomization/inventory/ConfigMap/Secret/Pod/provider evidence
→ identify approved, rendered, live, loaded a provider generations
→ re-establish one immutable release manifest
→ move route input into authoritative environment source
→ scope SOPS/KMS identity
→ rotate credential with overlap
→ reconcile Secret a roll Pods
→ verify loaded pv-43 and route 1850
→ reconcile unknown provider outcomes
→ complete or fail durable platform operation truthfully
→ test stale proposal, lost response, controller restart, second rotation a second promotion
```

## Cieľ zvládnutia aktívnych blokov

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
- vytvoriť reconciliation loop so stable source/resource identity;
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

### Flux

- vysvetliť source-controller, kustomize-controller, helm-controller, notification a image automation responsibilities;
- rozlíšiť configured source ref, resolved revision a immutable source artifact;
- sledovať Kustomization pipeline cez decryption, substitution, build, validation, server-side apply, inventory, prune a health;
- navrhnúť generation-aware dependencies a scoped service-account impersonation;
- diagnostikovať hidden `postBuild` input, SSA conflict, accidental prune a stale workload;
- oddeliť source Ready, Kustomization/HelmRelease Ready, effective workload a business accepted;
- považovať image automation za governed Git writer;
- overiť source/KMS outage, controller restart, second reconcile a tenant isolation.

### Application promotion

- rozlíšiť build, deploy, promote, release a expose transitions;
- definovať immutable release candidate a build-once identity continuity;
- odlíšiť artifact invariants, environment-owned configuration a runtime-owned state;
- viazať evidence a approvals na exact candidate, dependencies, target base a policy version;
- vysvetliť stale promotion race a compare-and-swap preconditions;
- promotovať compatibility graph vrátane schema, events, secrets a policies;
- rozlíšiť proposal, authoritative Git transition, reconciliation a business acceptance;
- overiť concurrent, superseded, unknown-outcome, rollback a second-promotion behavior.

### GitOps secrets

- rozlíšiť secret authority, Git desired, materialized target a loaded workload state;
- vysvetliť, prečo base64 ani private repository nie sú encryption boundary;
- porovnať encrypted-in-Git, Sealed Secrets a external-reference models;
- vysvetliť SOPS envelope encryption, recipients, data-key rotation a decryption identity;
- navrhnúť workload identity a provider/KMS least privilege;
- vysvetliť ExternalSecret refresh, target ownership a mutable provider alias semantics;
- navrhnúť overlap rotation, consumer convergence, revocation a leak response;
- overiť wrong key, provider outage, stale Secret, Pod non-reload, second rotation a cross-tenant denial.

### Internal Developer Platform

- rozlíšiť platform engineering, IDP a internal developer portal;
- definovať versionovaný platform capability a exact request subject;
- vysvetliť experience, control, execution a workload planes;
- navrhnúť durable distributed operation so semantic idempotency a identity reservation;
- mapovať Git, IaC, cloud, catalog, secrets a runtime authority bez hidden portal writerov;
- vysvetliť template lifecycle, catalog projection, policy a bounded self-service;
- rozlíšiť accepted request, provisioning, partial/unknown state a usable capability;
- overiť compensation, developer-functional outcome, decommission, second request a tenant isolation.

## Dominantný model sekcie

```text
business alebo platform capability intent
→ exact desired-state, release, secret, platform-product alebo tenant subject
→ declarative versioned authority a ownership boundaries
→ validated change, promotion alebo self-service request
→ source artifact, controller resolution, policy a durable operation
→ desired-vs-observed comparison alebo bounded orchestration
→ reconciliation, provisioning, materialization a consumer transition
→ effective runtime, developer a business outcome
→ drift, feedback, rotation, recovery a lifecycle closure
→ second-change/second-promotion/second-rotation/second-tenant validation
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
- Flux source Ready od downstream reconciliation a workload readiness;
- source artifact od final renderu s decryption, substitutions a external values;
- image discovery/update automation od production promotion authority;
- candidate evidence od fresh target-specific promotion decisionu;
- promotion proposal od authoritative merge a runtime acceptance;
- artifact invariant od environment-owned configuration;
- secret authority generation od Git declaration, Kubernetes Secret a loaded process generation;
- encrypted payload od decryption/retrieval identity a consumer convergence;
- portal task status od durable platform operation a effective capability;
- platform capability od central-ticket service;
- platform API authority od UI projection;
- scaffolding output od managed lifecycle contractu;
- paved path od mandatory lock-in;
- self-service request od unrestricted privilege;
- shared platform od tenant isolation boundary;
- configured object od valid/effective runtime mechanismu;
- trigger, root cause a causal amplifier;
- containment, reconciliation a authoritative recovery;
- first success od second-change, second-promotion, second-rotation, second-tenant a second-failure validation.

## Stav

| Téma | Status | Úroveň |
|---|---|---|
| Git ako source of truth | Learning | L2 |
| Pull-based deployment | Learning | L2 |
| Reconciliation a drift detection | Learning | L2 |
| Argo CD | Learning | L2 |
| Flux | Learning | L2 |
| Application promotion | Learning | L2 |
| GitOps secrets | Learning | L2 |
| Internal Developer Platform | Learning | L2 |
| Platform as a Product | Not Started | L0 |
| Golden paths a paved road | Not Started | L0 |
| Self-service | Not Started | L0 |
| Developer experience | Not Started | L0 |
| Service catalog | Not Started | L0 |
| Guardrails | Not Started | L0 |
| Multi-tenancy | Not Started | L0 |

Sekcia zostáva **In progress**. Stav **Ready for user review** možno použiť až po vytvorení všetkých 15 authoritative kapitol, overení complete navigation chainu, glossary, audit artifacts a finálnom section-level consistency passe.
