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
9. [Platform as a Product](platform-as-a-product.md)
10. [Golden paths a paved road](golden-paths-and-paved-road.md)
11. [Self-service](self-service.md)
12. [Developer experience](developer-experience.md)
13. [Service catalog](service-catalog.md)
14. [Guardrails](guardrails.md)
15. [Multi-tenancy](multi-tenancy.md)
16. [Praktický GitOps projekt od Git revision po overený runtime](gitops-practical-walkthrough.md)
17. [GitOps troubleshooting](gitops-troubleshooting.md)

Aktuálny authoritative stav sekcie je **17/17 · Ready for user review**.

## Completion state

Všetkých 17 authoritative kapitol bolo po pôvodnom authoring passe kompletne znovu spracovaných v štyroch prose-first strict blokoch. Každá kapitola má explicitný authority/subject/generation/evidence model, connected incident a vysvetlené positive, recovery, failure alebo forbidden acceptance paths; per-file gates vykazujú nulové critical, high a medium learning-depth findings. Authoritative ordering, celý navigation chain, glossary fragments a incidenty `GITOPS-PAY-61` až `GITOPS-PAY-64` zostávajú zachované. Sekcia je pripravená na používateľskú kontrolu; nie je tým automaticky používateľsky schválená, Accepted, Verified ani Stable.

## Hlavný GitOps walkthrough a troubleshooting

[Praktický GitOps projekt od Git revision po overený runtime](gitops-practical-walkthrough.md) vytvára pinned kind cluster a Argo CD installation, versionovaný Kustomize environment, scoped AppProject a automated Application. Walkthrough overuje resolved Git revision, controller render, Kubernetes generations, Pod imageID, EndpointSlice a application version/business outcome. Reprodukuje Git-owned manual drift, self-heal, broken image release, Git revert recovery a prune/finalizer safety.

[GitOps troubleshooting](gitops-troubleshooting.md) rozkladá incident na source/auth, revision resolution, render inputs, desired/live diff, field ownership, apply/prune, runtime health, secrets, promotion a multi-tenancy. Connected false-green incident ukazuje rozídený Git, hidden override, live patch a ignored fields a uzatvára ho jediným authoritative release manifestom a druhou reconciliation.

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

### `GITOPS-PAY-63` — output-driven platform mandate, detached golden path, false self-service a misleading DevEx verdict

Atlas po technickom redizajne spustil `Regulated Service v4` ako povinný platform product pre nové payment services. LaunchPad cez Backstage vytváral repository, pipeline, environment Git, catalog entity, namespace, database request, workload identity, dashboards a runbook. Executive outcome znel „production-ready service do 60 minút bez ticketu“, no platform tím definoval success ako terminal status scaffolder tasku.

Intended journey:

```text
observed regulated-team job
→ supported golden-path contract
→ eligible self-service request
→ durable orchestration repository/identity/network/database/GitOps/observability
→ first usable environment
→ first production business canary
→ second change a incident drill
→ retained managed adoption a product feedback
```

Skutočný path a measurement graph:

```text
Backstage template tag regulated-service-v4
+ custom actions image latest
+ Terraform module main
+ copied pipeline fragments
+ manual private-network ticket
+ no managed upgrade channel
+ portal success po repository/PR outputs
+ survey iba successful task cohortu
```

Šesťtýždňové evidence:

```text
platform requests:                       64
portal tasks marked Succeeded:           61  (95%)
requests with first usable environment:  39  (61%)
first production business outcome:       27  (42%)
requests requiring manual ticket:        28  (44%)
template forks alebo detached copies:    19  (30%)
manual platform bypasses:                 8  (13%)
median portal task duration:              9 min
median time-to-first-production:          3.8 dňa
```

Request `LP-8841` pre `settlement-repair-api` bol v portali `Succeeded` po 7 minútach. Database ostala `WaitingCapacity`, private endpoint nebol súčasťou pathu a workload identity nemala provider-reconciliation permission. Retry vytvoril druhý environment PR, tím otvoril tri tickety a fork-ol generated pipeline. Prvý production reconciliation prišiel po 19 hodinách; `8 412` settlements zostalo v manual queue a `73` prekročilo interný 24-hodinový resolution objective.

Causal boundaries:

- **Platform-as-a-Product root cause** — roadmap a success oracle optimalizovali technical output a mandatory adoption, nie segment-specific job, usable outcome, support toil a business effect.
- **Golden-path root cause** — organizácia zamenila copied scaffolding template za managed lifecycle; chýbali immutable dependency graph, extension points, upgrade channel a explicitný detach state.
- **Self-service root cause** — user-initiated task nemal complete preflight, durable operation, child identities, waiting/unknown semantics ani usable-outcome verification.
- **Developer-experience root cause** — dashboard meral iba successful portal cohort a lokálnu task latency; vylúčil waiting, failures, abandonment, manual intervention, trust, cognitive load a time-to-production.
- **Amplifiers** — forced rollout pred capability parity, mutable actions/modules, absent consumer-version inventory, generic survey, bot activity v delivery metrics a support mimo operation timeline-u.

Authoritative redesign:

```text
regulated user segment + observed settlement-repair journey
→ falsifikovateľná product value hypothesis
→ versioned capability/golden-path contract RSP-4.1
→ pinned actions/modules + managed components + explicit extensions
→ eligibility, quota, network a permission preflight
→ durable semantic operation s child IDs a truthful waiting/partial states
→ first usable environment verification
→ first production settlement canary
→ second change, incident a upgrade tests
→ mixed-method DevEx evidence pre success/failure/abandonment cohorts
→ staged adoption, feedback closure a capability-parity gate
```

Recovery najprv zastaví mandatory migration, klasifikuje 64 consumers na managed, extensible, exception alebo detached state, opraví `LP-8841` cez jednu durable operation a až potom rozšíri pilot podľa end-to-end outcome-u. Portal a catalog status sa odvodia z effective capability generation, nie z historického template tasku.

### `GITOPS-PAY-64` — stale catalog authority, false-green guardrails a cross-tenant confused deputy

Atlas rozšíril LaunchPad o catalog-driven isolation profiles a guardrail program `GP-7`. Nový `settlement-export-api` mal patriť tenantovi `vega-regulated`, spracúvať restricted data a používať dedicated isolation profile. Repository transfer zmenil ownera, tenant boundary a data classification, ale nový descriptor neprešiel starou processor schema generation. Catalog zachoval poslednú dobrú stitched entity:

```text
visible entity generation:  catalog-g118
owner:                     orion-payments
tenant boundary:           shared-internal
data classification:       internal
isolation profile:         standard
latest source revision:    9ba771e (processing error)
```

LaunchPad nekontroloval source revision, processing error ani critical-field freshness a vytvoril namespace so standard profile-om. Restricted guardrail binding sa preto nematchol. Širšia cross-namespace rule bola iba `Warn,Audit` a preskočila ju broad `PolicyException` s `platform.atlas.io/migration=true` bez expiry. Dashboard ukazoval `0 denied requests`, hoci neukazoval expected inventory, no-match subjects ani skipped exceptions.

Flux povoľoval cross-namespace references a shared controller mal cluster-admin authority. Tenant mohol vytvoriť namespaced `SettlementConnection`; cluster-scoped operator s broad Secret read permission dôveroval user-controlled `credentialRef.namespace` a načítal `orion-payments/provider-settlement`. Vega workload tak získal Orion provider context napriek tomu, že tenant user nemal direct Secret permission.

```text
10:02:11 → descriptor revision 9ba771e merged
10:03:07 → catalog processing error; catalog-g118 ostáva visible
10:06:42 → LaunchPad plan používa stale tenant profile
10:08:13 → namespace vytvorený ako shared-internal
10:11:26 → Flux Kustomization Ready=True
10:12:04 → cross-namespace reference warning, request allowed
10:12:19 → operator načíta Orion credential
10:15:44 → prvý Vega export cez foreign provider identity
10:57:31 → tenant breach potvrdený
```

Počas 45 minút bolo v nesprávnom provider context-e dostupných `2 184` settlement records a `312` bolo exportovaných do Vega workspace. Catalog page poslala incident nesprávnemu ownerovi a predĺžila triage o 26 minút. Separate namespace a RBAC neboli complete tenant boundary, pretože privileged operator sa stal confused deputy.

Causal boundaries:

- **Service-catalog root cause** — last-good projection bola správna pre degraded discovery, ale critical automation ju použila ako fresh authority bez source/processor generation a CAS gate-u.
- **Guardrail root cause** — policy success sa meral denial countom bez expected inventory a match coverage; warn-only action a broad non-expiring exception nevytvárali prevention.
- **Multi-tenancy root cause** — namespace isolation nepokrývala cross-namespace GitOps references, cluster-admin controller, broad operator credential, network baseline ani external provider identity.
- **Amplifiers** — mutable tenant labels, wildcard Argo default project, absent operator-side tenant authorization, shared nodes/egress a incident routing podľa stale ownera.

Authoritative redesign:

```text
stable tenant ID tenant-vega-71 + restricted-v3 profile
→ exact catalog source revision a compatible processor generation
→ stitched entity catalog-g119 s critical-field freshness gate
→ namespace UID + controller-owned tenant binding
→ policy/binding/parameter generation s expected-inventory match proof
→ Deny cross-tenant references + bounded expiring exceptions
→ Flux no-cross-namespace refs + tenant service-account impersonation
→ explicit Argo source/destination/resource allowlists
→ operator same-tenant authorization a delegated credential identity
→ default-deny network, scoped egress, quota, node/storage/observability profile
→ positive Vega workflow + negative Orion access canaries
→ effective tenant acceptance a residual scan
```

Containment zrušil foreign connection, rotoval Orion credential, zastavil cross-namespace reconciliation, izoloval Vega egress a reconciled exported records. Catalog, policy a tenant boundaries boli opravené a testované spolu; izolovaná zmena jedného layeru by ponechala ďalší indirect privilege path.

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

### Platform as a Product

- definovať exact platform-product subject, internal user segment a job-to-be-done;
- vytvoriť falsifikovateľnú value hypothesis a product outcome tree;
- odlíšiť project output, technical service a dlhodobo spravovaný platform product;
- navrhnúť complete capability contract, adoption funnel a feedback closure;
- merať first usable, first production a retained managed outcome namiesto portal activity;
- vysvetliť funding, cost, ownership, roadmap authority a lifecycle;
- overiť capability parity, second cohort, second change a retirement behavior.

### Golden paths a paved road

- rozlíšiť golden path, paved road, template a guardrail;
- definovať exact path generation, dependency graph a output inventory;
- klasifikovať invariants, defaults, explicit choices a extension points;
- odlíšiť bootstrap copy od managed componentu a upgrade channelu;
- navrhnúť supported extension, time-bounded exception a detached ownership;
- testovať composition, negative cases, second user, second change a migration;
- overiť supply-chain, effective compliance a path acceptance bez golden cage.

### Self-service

- rozlíšiť self-service, automation a delegated privileged execution;
- definovať exact semantic request, eligibility, preflight a subject-bound plan;
- navrhnúť durable state machine pre waiting, partial, unknown a compensation;
- vysvetliť idempotency, child-operation identity a authoritative read-back;
- navrhnúť least-privilege delegation, quota, fairness a backpressure;
- odlíšiť accepted request, resource existence, usable capability a business outcome;
- overiť retry, cancel, update, delete, controller restart a abuse behavior.

### Developer experience

- odlíšiť developer experience, productivity, satisfaction a activity;
- definovať exact cohort, journey, platform generation a outcome subject;
- vysvetliť feedback loops, cognitive load, flow a friction taxonomy;
- mapovať journey naprieč tools, handoffs, waiting, operations a support;
- kombinovať system telemetry, survey, interview a observation bez selection bias;
- používať counterbalanced speed, quality, experience, reliability a business metrics;
- overiť causal hypothesis, privacy, feedback closure, second cohort a operational experience.

### Service catalog

- rozlíšiť inventory, registry, CMDB a service catalog podľa authority a decision contractu;
- definovať exact catalog entity, source generation, processor generation a stitched projection;
- vytvoriť field-level authority, provenance, freshness a conflict model;
- vysvetliť ingestion, processing, stitching, relations, orphan a deletion lifecycle;
- odlíšiť catalog projection od runtime, ownership, policy a business authority;
- navrhnúť CAS-bound catalog-driven automation a safe last-good semantics;
- overiť expected inventory, owner transfer, source move, processor error a second-change behavior.

### Guardrails

- rozlíšiť guardrail, safe default, gate, scorecard a širší control;
- definovať protected invariant, exact policy/binding/parameter subject a enforcement boundary;
- vysvetliť Deny, Warn, Audit, mutation, generation, background scan a failure policy;
- navrhnúť match coverage, policy rollout migration a effective-state verification;
- vytvoriť bounded subject-specific exception, expiry, compensation a break-glass lifecycle;
- testovať no-match, engine outage, selector drift, policy rollback a controller interaction;
- overiť risk outcome bez false-green denial countu a bez neprijateľného developer frictionu.

### Multi-tenancy

- definovať platform, business/data a infrastructure tenant a stable tenant identity;
- vytvoriť threat model a versionovaný isolation profile naprieč control a data plane-om;
- porovnať namespace, virtual control plane, cluster, account a dedicated compute topology;
- navrhnúť tenant-scoped RBAC, GitOps, controllers, network, storage, secrets a shared services;
- vysvetliť confused-deputy, cross-namespace reference a noisy-neighbor failure modes;
- vytvoriť durable onboarding, migration, offboarding a residual-scan lifecycle;
- overiť positive workflow, foreign-tenant negative paths, second tenant a controller compromise.

## Dominantný model sekcie

```text
business, platform alebo tenant capability intent
→ exact desired-state, release, secret, product, catalog, guardrail a tenant subject
→ declarative versioned authority, field provenance a ownership boundaries
→ validated change, product hypothesis, golden path, promotion alebo self-service request
→ source artifact, catalog projection, controller resolution, policy a durable operation
→ desired-vs-observed comparison, policy evaluation alebo bounded orchestration
→ reconciliation, provisioning, materialization, tenant isolation a consumer transition
→ effective runtime, developer, security a business outcome
→ drift, feedback, exception, rotation, recovery a lifecycle closure
→ second-change/promotion/rotation/policy/tenant/failure validation
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
- platform project/service output od platform product a user outcome;
- forced request count od usable, retained adoption;
- golden path od bootstrap template a golden cage;
- managed component od detached copy a explicitného extension/exception state-u;
- paved path od mandatory lock-in;
- self-service request od unrestricted privilege;
- accepted request od durable operation, usable capability a business outcome;
- activity metric od developer experience, productivity a counterbalanced outcome;
- service catalog od inventory, registry, CMDB a runtime authority;
- source descriptor/provider generation od stitched catalog projection;
- last-good catalog availability od fresh critical metadata decisionu;
- scorecard alebo warning od authoritative guardrail enforcementu;
- policy logic od binding, parameter, action, exception a match coverage;
- admission decision od stored, controller-resolved a effective compliance;
- namespace separation od composed control-plane a data-plane isolation;
- direct RBAC denial od controller-mediated confused-deputy pathu;
- tenant label od stable tenant identity a isolation profile generation;
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
| Platform as a Product | Learning | L2 |
| Golden paths a paved road | Learning | L2 |
| Self-service | Learning | L2 |
| Developer experience | Learning | L2 |
| Service catalog | Learning | L2 |
| Guardrails | Learning | L2 |
| Multi-tenancy | Learning | L2 |

Sekcia je **15/15 · Ready for user review**. Všetkých 15 authoritative kapitol je vytvorených, ordering a navigation chain sú complete, glossary fragmenty `16a`–`16d` sú synchronizované a finálny section-level consistency pass spája authority, reconciliation, platform product, catalog, guardrail a tenant model bez zamenenia projection alebo local successu za effective runtime a business verdict.

Tento stav neznamená **User reviewed**, **Accepted**, **Verified** ani **Stable**. Označuje, že repository-native obsah a validačné artifacts sú pripravené na používateľskú kontrolu.
