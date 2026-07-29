# Argo CD

Argo CD je Kubernetes-native GitOps controller pre declarative application delivery. Jeho podstatou nie je UI ani tlačidlo Sync, ale explicitný Application contract medzi source revisions, renderom, target destination, resource ownershipom, diffom, sync policy a health evidence.

Argo CD môže byť technicky funkčné a napriek tomu nevytvárať spoľahlivý GitOps model, ak Application používa hidden parameter overrides, broad AppProject, mutable alebo ambiguous source refs, nebezpečné ignore rules alebo nejasný multi-writer ownership.

## 1. Dominantný model

```text
application delivery intent
→ Application/AppProject subject
→ repository a revision resolution
→ repo-server render
→ application-controller desired/live comparison
→ sync policy, phases, waves a prune decision
→ Kubernetes mutation a resource tracking
→ health, history a business verification
→ drift/self-heal/rollback
→ second-sync a controller-restart closure
```

Argo CD acceptance verdict musí pokryť celý chain od exact source generation po effective workload outcome.

## 2. Hlavné komponenty

### API server

Poskytuje API pre UI, CLI a integrations. Rieši napríklad:

- Application management a status;
- sync/rollback operations;
- authentication a authorization;
- repository a cluster credential management;
- webhook endpoint;
- RBAC enforcement.

### Repository server

Resolve-uje source a generuje manifests z:

- repository URL;
- branch, tag alebo commit;
- path/chart;
- Helm/Kustomize/plugin settings;
- values a parameters;
- dependencies.

Repo-server output je controller-resolved desired state. Jeho cache, toolchain a credentials sú súčasť deployment subjectu.

### Application controller

Kontinuálne:

1. pozoruje Applications;
2. získava desired manifests;
3. číta live resources;
4. vyhodnocuje sync a health;
5. vykonáva sync alebo self-heal podľa policy;
6. spravuje operation history, hooks a resource tracking.

### Optional supporting components

Argo CD deployment môže obsahovať identity provider integration, Redis/cache components, notification controllers, ApplicationSet controller a ďalšie extensions. Ich failure a upgrade state môže meniť control-plane behavior.

## 3. Exact Argo CD Application subject

Application subject zahŕňa:

- Application name, namespace, UID a generation;
- AppProject;
- source alebo sources repository identities;
- target revisions a resolved commit/chart versions;
- paths, values, parameters a plugin generation;
- destination server/cluster a namespace;
- sync policy, prune, self-heal a allow-empty;
- sync options;
- ignore differences;
- resource tracking method a installation ID;
- hooks, phases a waves;
- repository/cluster credentials;
- controller/repo-server version a loaded configuration;
- status, operation history a health customizations;
- business acceptance a rollback contract.

`payments-prod je Synced` bez tejto identity nehovorí, ktorú source generation a ktoré comparison rules status reprezentuje.

## 4. Application CRD

Zjednodušený Application:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: payments-prod
  namespace: argocd
spec:
  project: payments-prod
  source:
    repoURL: ssh://git.example/platform/environments.git
    targetRevision: refs/heads/production
    path: clusters/prod/payments
  destination:
    server: https://kubernetes.default.svc
    namespace: payments
  syncPolicy:
    automated:
      enabled: true
      prune: true
      selfHeal: true
```

Tento object stále nepreukazuje:

- resolved commit SHA;
- rendered manifest inventory;
- whether overrides exist;
- source authenticity;
- destination readiness;
- sync success;
- workload health;
- business outcome.

## 5. AppProject ako trust boundary

AppProject môže obmedziť:

- povolené source repositories;
- povolené destination clusters a namespaces;
- cluster-scoped a namespaced resource kinds;
- project roles a RBAC;
- project-scoped repositories/clusters.

Default project s broad source/destination/resource permissions je vhodný pre demo, nie automaticky pre multi-team production.

Silný boundary:

```text
payments-prod project
→ trusted environment repositories only
→ production cluster only
→ payments namespaces only
→ explicit allow/deny resource kinds
→ scoped project roles
```

AppProject však nenahrádza Kubernetes RBAC ani repository governance. Controller service account môže mať širšie technical permissions, než project policy povoľuje cez Argo API; obe vrstvy treba auditovať.

## 6. Source tracking strategies

Argo CD môže sledovať:

### Branch alebo symbolic ref

Controller kontinuálne porovnáva manifests na aktuálnom tip-e ref-u.

Výhody:

- prirodzený continuous delivery flow;
- jednoduchá promotion cez PR/merge.

Riziká:

- force push;
- nejasný cut-off počas incidentu;
- branch/tag name ambiguity;
- viac commits môže prebehnúť medzi observations;
- rollback ref-u nemusí odstrániť overrides alebo external effects.

### Tag

Stabilnejší pointer, ale môže byť mutable retaggingom.

### Commit SHA

Najpresnejší immutable source coordinate. Promotion vyžaduje zmenu Application alebo environment manifestu na nový SHA.

### Helm chart version alebo range

Range môže automaticky resolve-nuť novú chart version. Production reproducibility vyžaduje zaznamenať resolved version a dependencies.

Fully qualified refs znižujú ambiguity:

```text
refs/heads/release-9.0
refs/tags/release-9.0
```

## 7. Parameter overrides

Argo CD môže ukladať source-tool parameters v Application spec. Overrides majú precedence nad Git source values.

```text
Git value image.digest=pay900a
Application override image.digest=pay899hf7
→ rendered desired image=pay899hf7
```

To môže byť užitočné pre experiment, ale oslabuje Git ako complete source of truth.

Production policy by mala:

- zakázať ad-hoc overrides alebo ich deklarovať v Git-managed Application objecte;
- inventarizovať current overrides;
- ukázať ich v diff/review evidence;
- priradiť ownera a expiry;
- overiť rollback a controller restart;
- alertovať na override mimo approved pathu.

## 8. Multi-source Applications

Application môže kombinovať viac sources, napríklad chart a environment values.

```text
chart repository revision A
+ values repository revision B
+ plugin/config generation C
→ rendered desired set D
```

Riziká:

- partial source availability;
- independent revision movement;
- resource collision;
- unclear ownership;
- override precedence;
- auto-sync triggered zmenou iba jednej source;
- neúplný release coordinate.

Acceptance evidence musí zachytiť všetky resolved sources, nie iba jeden revision label.

## 9. Automated sync

Automated sync umožní controlleru aplikovať detected desired change bez direct CI deployment credentialu.

Dôležité policies:

### `enabled`

Určuje, či automated sync prebieha.

### `prune`

Povoľuje odstrániť tracked resources, ktoré zmizli z desired set-u.

### `selfHeal`

Povoľuje automated sync pri live drift-e bez novej source revision.

### `allowEmpty`

Povoľuje desired set bez resources; vyžaduje vysokú opatrnosť pre destructive scenáre.

Tieto flags nie sú synonyms:

```text
new Git commit
→ automated sync

manual live patch
→ selfHeal only, ak je povolený a diff nie je ignorovaný

resource removed from Git
→ prune only, ak je povolený
```

## 10. Sync operation a options

Sync options menia apply behavior. Príklady:

- namespace creation;
- prune ordering a propagation;
- selective apply iba OutOfSync resources;
- client-side alebo server-side apply;
- replace/create behavior;
- respect ignore differences počas sync-u;
- validation/dry-run behavior.

Každá option môže meniť:

- field ownership;
- delete/recreate risk;
- immutable field handling;
- admission behavior;
- diff vs. sync consistency;
- rollback eligibility;
- external controller interactions.

`Replace=true` alebo force-like behavior nie je iba performance detail. Môže zmeniť resource UID, disruption a dependent objects.

## 11. Resource tracking

Argo CD potrebuje určiť, ktoré live resources patria Application.

Tracking methods zahŕňajú:

- annotation;
- annotation + informational label;
- label.

Annotation tracking používa tracking identity obsahujúcu Application a resource identity. Riziká:

- copied non-self-referencing annotations;
- label collision s Helm alebo iným toolom;
- zmena tracking method bez úplnej resync;
- viac Argo CD installations bez installation ID;
- manual removal tracking metadata;
- generated children nesprávne považované za owned resources.

Resource tree v UI nie je automatický ownership proof pre prune.

## 12. Diff a `ignoreDifferences`

Argo CD umožňuje ignore rules podľa:

- group/kind/name/namespace;
- JSON pointers;
- JQ path expressions;
- managed field managers;
- system-wide resource customization.

Defaultne ignore rule ovplyvňuje diff. Aby ovplyvnila aj sync apply, môže byť potrebná príslušná sync option.

Riziko:

```text
ignore broad path
→ Application Synced
→ live critical field iná než desired
→ selfHeal sa nespustí
```

Ignore rules potrebujú unit fixtures s expected ignored aj forbidden visible driftom.

## 13. Health assessment

Argo CD oddeľuje sync status od resource health. Health môže byť:

- Healthy;
- Progressing;
- Degraded;
- Suspended;
- Missing;
- Unknown.

Built-in alebo custom health logic musí odrážať actual capability. Green Deployment health nemusí overovať:

- exact image digest vo všetkých Pods;
- loaded secret/config generation;
- Service endpoints pre všetky cohorts;
- database migration compatibility;
- provider path;
- business transaction completion.

Pre critical applications je potrebný PostSync/canary alebo external acceptance oracle, nie iba resource health.

## 14. Sync phases, hooks a waves

Phases typicky zahŕňajú:

- `PreSync`;
- `Sync`;
- `PostSync`;
- failure/delete-related hook behavior podľa supported generation.

Waves určujú ordering v rámci phase.

Príklad:

```text
wave -10 → CRD alebo namespace baseline
wave -5  → database compatibility/precondition Job
wave 0   → application resources
wave 5   → route exposure
PostSync → business canary
```

Riziká:

- hook side effect nie je idempotentný;
- generated hook name vytvára duplicates;
- hook zostane po timeout-e v unknown state;
- wave ordering nenahrádza application readiness;
- selective sync môže hooks preskočiť;
- prune ordering odstráni dependency priskoro.

## 15. ApplicationSet boundary

ApplicationSet generuje Applications z listov, clusters, Git directories alebo iných generators.

Treba rozlíšiť:

```text
ApplicationSet desired template/generator
→ generated Application
→ Application desired resources
```

Direct edit generated Application môže byť prepísaný ApplicationSet controllerom. Policy sa preto musí meniť na authoritative generator/template vrstve.

Generator expansion musí byť bounded a reviewed, pretože jedna zmena môže vytvoriť alebo zmeniť stovky Applications a destinations.

## 16. Argo CD control-plane security

Security subject zahŕňa:

- API auth a RBAC;
- AppProject boundaries;
- repository credentials;
- cluster credentials;
- repo-server plugin isolation;
- webhook exposure;
- admin account/token lifecycle;
- SSO groups a project roles;
- controller service accounts;
- secret encryption a backup;
- audit logs;
- upgrade a disaster recovery.

Repo-server spracúva potentially untrusted repository content. Config management plugins a Helm/Kustomize execution musia mať bounded filesystem, network, credentials a secret exposure.

## 17. Observability

Minimálne signals:

- Application desired/resolved revision;
- sync status a OutOfSync age;
- health status a transition age;
- reconciliation queue/duration;
- repo fetch/render latency a errors;
- controller API errors/retries;
- sync operation result a resources changed;
- prune/delete count;
- hook result/duration;
- source/destination credential failures;
- ignored-difference matches;
- parameter override inventory;
- resource tracking conflicts;
- business acceptance result.

Application status bez timestamps, revision a operation contextu nestačí na incident timeline.

## 18. Connected incident `GITOPS-PAY-61`

Production Application mala:

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

Ďalší effective config:

- parameter override `image.digest=sha256:pay899hf7`;
- system-wide ignore containers subtree;
- production branch s povoleným force pushom;
- default AppProject povoľoval všetky repositories, clusters, namespaces a resource kinds;
- CI aj humans mali direct write access;
- health sa uzavrel pri ready Deployment-e bez business canary;
- resource tracking používal shared instance label, ktorý modifikoval aj Helm chart.

### Argo CD root cause

Application/AppProject contract nevyjadroval production authority a safety boundary. Hidden override, broad project, broad ignore rule, mutable ref, weak tracking a incomplete health oracle vytvorili false-Synced/Healthy verdict.

### Incident timeline

```text
20:14:03 webhook refresh
20:14:04 CI direct apply
20:14:07 Argo sync operation
20:18:26 human live patch
20:21:11 production ref force-reset
20:28:09 ref restored
20:31:40 Application Synced/Healthy
20:52:17 business policy-generation mismatch confirmed
```

Argo operation history bola technicky konzistentná s resolved Application configom. Problém bol, že Application config itself nebola úplná Git-managed authority a diff/health rules odfiltrovali rozhodujúci mismatch.

### Redesign

```text
Git-managed AppProject + Application
→ dedicated production project
→ trusted repo/destination/resource allowlists
→ fully qualified protected production ref
→ no runtime parameter overrides
→ annotation resource tracking + installation identity
→ narrow diff exceptions
→ automated sync + scoped self-heal
→ prune guards a sync waves
→ PostSync business canary
→ exact revision/render/live digest evidence
```

Break-glass:

```text
incident approval
→ temporary scoped Argo sync suspension alebo resource exception
→ short-lived cluster credential
→ recorded live mutation
→ immediate Git reconciliation
→ restore auto-sync/self-heal
→ revoke credential
→ direct-drift test
```

## 19. Argo CD acceptance verdict

Argo CD design je prijatý, keď:

- Application, AppProject, sources, destinations a controller generation sú explicitné;
- all source revisions a render inputs sú resolved a observable;
- production refs/artifacts sú non-ambiguous a reproducible;
- parameter overrides sú zakázané alebo Git-managed, visible a expiring;
- AppProjects obmedzujú trusted repositories, destinations, resources a roles;
- Kubernetes RBAC zodpovedá project policy a tenant modelu;
- sync policy, prune, self-heal a allow-empty semantics sú explicitné;
- sync options majú field-ownership, disruption a rollback assessment;
- tracking method a installation identity zabraňujú collisions;
- ignore rules sú úzke a negative-tested;
- phases/waves/hooks sú idempotentné, bounded a recovery-safe;
- Synced/Healthy/business acceptance sú oddelené;
- ApplicationSet-generated config sa mení na authoritative template vrstve;
- repo-server/plugin credentials a execution sú izolované;
- source outage, target outage, webhook loss, controller restart, force push, direct drift, prune a second-sync tests prejdú;
- forbidden hidden override, wrong destination, shared-resource prune, false-Synced, false-Healthy a dual-writer outcomes sú odmietnuté.

## 20. Troubleshooting flow

```text
Argo app je OutOfSync, false-Synced, Degraded alebo nasadilo wrong generation
→ Application UID/generation + AppProject
→ sources a resolved revisions
→ repo-server render/parameters/cache
→ desired object inventory
→ live tracking IDs/managedFields
→ diff/ignore/normalization
→ sync policy/options/phases/waves/hooks
→ controller operation history/API errors
→ health customization
→ workload/business generation
→ authoritative remediation a second sync
```

## 21. Anti-patterny

### Default project je dostatočný

Default broad policy zvyčajne nevyjadruje production tenant a resource boundary.

### `targetRevision: production` je jednoznačné

Môže byť mutable branch a môže kolidovať s tagom. Potrebná je ref a promotion policy.

### Override je iba dočasný

Bez expiry a Git reconciliation sa stáva hidden desired state-om.

### Self-heal zapneme všade

Bez field ownershipu a emergency contractu môže revertovať legitímny controller alebo incident containment.

### Ignore differences opraví OutOfSync noise

Broad rule môže skryť critical drift a zabrániť self-heal-u.

### Healthy Application znamená úspešný release

Resource health nie je business canary ani data/provider compatibility verdict.

### Sync wave vyrieši všetky dependencies

Ordering nenahrádza readiness, idempotency a external side-effect reconciliation.

## 22. Kontrolné otázky

1. Aké sú hlavné Argo CD components a ich responsibilities?
2. Čo tvorí exact Application subject?
3. Ako AppProject vytvára trust boundary?
4. Ako sa branch, tag a commit tracking líšia?
5. Prečo parameter override oslabuje Git authority?
6. Aké riziká má multi-source Application?
7. Ako sa auto-sync, prune a self-heal líšia?
8. Ako resource tracking ovplyvňuje diff a prune?
9. Prečo ignoreDifferences môže vytvoriť false-Synced stav?
10. Ako phases, waves a hooks menia deployment state machine?
11. Prečo `GITOPS-PAY-61` prešlo ako Synced/Healthy?
12. Čo overuje Argo CD acceptance verdict?

## Glossary impact

Relevantné pojmy: Argo CD Application subject, AppProject boundary, repository server, application controller, resolved revision, source tracking strategy, parameter override, multi-source Application, automated sync, self-heal, prune, allow-empty, sync option, resource tracking method, tracking ID, sync phase, sync wave, resource hook, ApplicationSet authority, false-Synced Application, Argo health verdict a Argo CD acceptance verdict.

## Primárne zdroje

- [Argo CD — Overview](https://argo-cd.readthedocs.io/en/stable/)
- [Argo CD — Architectural Overview](https://argo-cd.readthedocs.io/en/stable/operator-manual/architecture/)
- [Argo CD — Application Specification](https://argo-cd.readthedocs.io/en/latest/user-guide/application-specification/)
- [Argo CD — Projects](https://argo-cd.readthedocs.io/en/stable/user-guide/projects/)
- [Argo CD — Automated Sync Policy](https://argo-cd.readthedocs.io/en/release-3.2/user-guide/auto_sync/)
- [Argo CD — Resource Tracking](https://argo-cd.readthedocs.io/en/stable/user-guide/resource_tracking/)
- [Argo CD — Diff Customization](https://argo-cd.readthedocs.io/en/latest/user-guide/diffing/)
- [Argo CD — Sync Phases and Waves](https://argo-cd.readthedocs.io/en/release-3.2/user-guide/sync-waves/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Reconciliation a drift detection](reconciliation-and-drift-detection.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
