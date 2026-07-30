# Argo CD

Argo CD je Kubernetes-native pull reconciler pre declarative application delivery. Jeho authoritative contract nie je UI tlačidlo `Sync`, ale presná väzba medzi Application/AppProject, resolved source generations, repo-server renderom, destination, field/resource ownershipom, diffom, sync policy, resource health a business acceptance.

```text
application delivery intent
→ exact Application/AppProject/control-plane subject
→ trusted sources a resolved input graph
→ deterministic repo-server render
→ desired/live comparison a tracking
→ project, RBAC a sync-option policy
→ phases, waves, hooks, apply a prune
→ resource health a effective workload state
→ business canary a release verdict
→ self-heal, rollback, controller recovery a second sync
```

Argo môže technicky fungovať a zároveň poskytovať false-Synced/Healthy verdict, ak Application obsahuje hidden override, broad project alebo ignore rule, mutable ref, weak tracking či druhého live writera.

## 1. Application a control-plane subject

Exact subject obsahuje Application name/namespace/UID/generation, AppProject, Argo installation a controller/repo-server version, repository/source identities a resolved revisions, renderer/parameters/plugins, destination cluster/namespace, sync policy/options, prune/self-heal/allow-empty, ignore rules, tracking method/installation ID, hooks/waves, credentials, health customizations, operation history a business/rollback contract.

Hlavné components majú odlišnú authority. API server poskytuje management API, auth/RBAC, repository/cluster credential interfaces a webhook. Repo-server fetchuje source a generuje manifests. Application controller pozoruje Applications, desired/live resources, diff, sync, tracking, health a operation history. ApplicationSet controller môže generovať Applications z authoritative template/generatora. Redis/cache, IdP, notification a plugin components ovplyvňujú control-plane availability a loaded generation.

`payments-prod je Synced` bez Application UID/generation, resolved source revisions, diff rules a controller generation nie je reprodukovateľné tvrdenie.

## 2. AppProject a end-to-end trust boundary

AppProject obmedzuje allowed source repositories, destination clusters/namespaces, cluster-scoped a namespaced resource kinds a project roles. Production project má mať explicitné allowlists:

```text
payments-prod AppProject
→ trusted environment repositories
→ production cluster
→ payments namespaces
→ bounded resource kinds
→ scoped project roles
```

Default broad project je vhodný na demo, nie ako production tenant boundary. AppProject však nenahrádza Kubernetes RBAC. Application controller service account a cluster credentials musia technicky umožňovať iba intended mutations alebo musí byť ich širší permission model kompenzovaný silným project/tenant enforcementom a auditom.

Repository credentials, repo-server plugin execution a cluster credentials sú súčasť trust pathu. Repo-server spracúva repository-controlled content; plugins potrebujú filesystem/network/credential isolation a pinned generation. ApplicationSet generator expansion musí byť bounded, pretože jedna template change môže zmeniť stovky destinations. Generated Application sa opravuje na generator/template authority vrstve, nie permanentným direct editom.

## 3. Source resolution, render a overrides

Argo môže sledovať branch, tag, commit SHA alebo Helm chart version/range. Branch je continuous mutable pointer; tag môže byť retagovaný; commit SHA je najpresnejšia immutable coordinate. Fully qualified refs znižujú ambiguity. Pri range alebo multi-source Application treba zaznamenať všetky resolved versions.

```text
chart source revision A
+ values source revision B
+ plugin/tool generation C
+ Application parameters D
→ rendered desired inventory E
```

Parameter overrides majú precedence nad Git source values. Ad-hoc production override preto predstavuje hidden desired state, ak nie je Git-managed, reviewed, visible, owned a expiring. Rollback Git ref-u ho nemusí odstrániť.

Repo-server evidence má obsahovať resolved sources, renderer version/config, parameters, dependencies, manifest inventory a render errors. Cache hit nie je authority; stale cache po ref movemente alebo credential recovery musí byť revalidated. Multi-source resource collisions a partial source availability nesmú silentne vytvoriť incomplete desired set.

## 4. Comparison, tracking a ignore rules

Application controller porovnáva rendered desired objects s tracked live resources. Tracking annotation alebo label určuje ownership inventory; shared labels, copied annotations, zmena tracking methodu alebo viac installations bez installation ID môžu vytvoriť collisions a unsafe prune.

Resource tree v UI nie je automatický ownership proof. Generated operator children môžu patriť parent controlleru, nie priamo Application.

Diff pipeline zahŕňa normalization, API defaulting, managedFields a `ignoreDifferences`. Ignore defaultne mení comparison oracle; pri príslušnej sync option môže meniť aj apply behavior. Broad path môže skryť image, env, probes a security context:

```text
critical live drift
→ ignored comparison path
→ no actionable delta
→ Synced
→ self-heal sa nespustí
```

Ignore rule potrebuje exact resource/field/manager, ownera, dôvod a negative fixture, ktorá dokazuje, že adjacent critical drift zostáva visible.

## 5. Automated sync, self-heal, prune a sync options

Automated sync aplikuje novú desired generation bez direct CI cluster credentialu. `prune` povoľuje odstrániť tracked resources chýbajúce v desired set-e. `selfHeal` spúšťa automated sync pri live drift-e bez novej source revision. `allowEmpty` povoľuje empty desired set a musí byť používané iba s explicitným destructive contractom.

Tieto flags sú samostatné:

```text
new Git generation → automated sync
manual Git-owned drift → selfHeal
resource removed from valid desired inventory → prune
```

Sync options menia mutation semantics. `Replace` alebo force delete/create môže zmeniť UID a spôsobiť disruption; server-side apply mení field ownership; `PruneLast` a propagation menia deletion ordering; `FailOnSharedResource` môže chrániť ownership collision; `RespectIgnoreDifferences` prepája compare exception so sync pre-processingom. Každá option potrebuje field/disruption/rollback assessment.

Argo automated sync sa typicky pokúša o jednu operation pre konkrétnu commit+parameters kombináciu; periodic reconciliation má defaultný interval s jitterom podľa current config. Preto hidden parameter change alebo stale override patrí do release identity rovnako ako commit.

## 6. Phases, waves, hooks a health

Sync phases a waves vytvárajú deployment state machine:

```text
PreSync → compatibility/precondition
Sync wave -10 → CRD/baseline
Sync wave 0 → application
Sync wave 5 → route exposure
PostSync → business canary
```

Ordering nenahrádza readiness. Hook musí byť idempotentný, mať stable identity, bounded deadline, delete/retention policy a recovery pri unknown outcome-e. Generated hook name môže po retry vytvoriť duplicate side effect; selective sync môže hooks preskočiť; prune môže dependency odstrániť priskoro.

Resource health (`Healthy`, `Progressing`, `Degraded`, `Suspended`, `Missing`, `Unknown`) je oddelená od sync statusu. Green Deployment nemusí overiť exact image digest vo všetkých Podoch, loaded Secret/ConfigMap, Service endpoint cohort, migration compatibility alebo provider flow. Critical Application preto potrebuje external/PostSync business oracle a per-generation runtime evidence.

## 7. Connected incident `GITOPS-PAY-61`

Production Application používala `project: default`, mutable `targetRevision: production`, automated sync s prune a `selfHeal: false`. Effective config obsahoval override `image.digest=sha256:pay899hf7`, system-wide ignore containers subtree, force-pushable branch, broad project, direct CI/human writers, shared tracking label a health uzavreté pri ready Deployment-e.

Timeline:

```text
20:14:03 webhook refresh
20:14:04 CI direct apply
20:14:07 Argo sync
20:18:26 human patch
20:21:11 production ref force-reset
20:28:09 ref restored
20:31:40 Application Synced/Healthy
20:52:17 business mismatch confirmed
```

Argo operation history bola konzistentná s controller-resolved configom, nie s Git-declared generation. Override, broad ignore a incomplete health oracle odfiltrovali rozhodujúce rozdiely. AppProject nevyjadroval production trust boundary a tracking collision oslabovala ownership evidence.

Redesign zaviedol Git-managed dedicated AppProject/Application, trusted source/destination/resource allowlists, protected fully qualified ref, nulové runtime overrides, annotation tracking s installation ID, narrow ignore exceptions, scoped self-heal, prune guards, waves a PostSync settlement canary.

## 8. Recovery a acceptance paths

**Positive path** resolve-ne celý source graph, renderuje exact inventory, syncne podľa scoped project/RBAC a potvrdí live/runtime generation aj business canary.

**Drift path** manual Git-owned patch spustí scoped self-heal; HPA/operator fields zostanú pod svojím writerom.

**Recovery path** prežije webhook/source/target outage, repo-server/controller restart a unknown hook/apply outcome bez stale renderu alebo duplicate side effectu.

**Rollback path** zmení Git-managed source/Application generation a preukáže compatible full graph; neostáva na live-only undo.

**Forbidden path** odmietne hidden override, wrong destination, broad default project, tracking collision, shared-resource prune, broad ignore, false-Synced/Healthy a direct second writer.

Acceptance zahŕňa force-push attempt, multi-source partial failure, webhook loss, controller restart, direct drift, prune, unknown hook, ApplicationSet regeneration a second sync.

## 9. Troubleshooting a anti-patterny

Pri OutOfSync alebo wrong generation sa mapuje Application UID/generation a AppProject, sources/resolved revisions, repo-server render/cache/parameters, desired inventory, live tracking/managedFields, diff/ignore rules, sync options/phases/hooks, controller operation history, health customization, loaded runtime a business generation.

Anti-patterny sú default project v production, ambiguous mutable ref, „dočasný“ override bez expiry, self-heal zapnutý bez ownershipu, ignore používané na odstránenie noise, Healthy vydávané za release success a waves vydávané za dependency correctness.

## 10. Kontrolné otázky

1. Čo tvorí exact Argo Application/control-plane subject?
2. Ako AppProject a Kubernetes RBAC spolu tvoria boundary?
3. Ako sa branch, tag, commit a multi-source coordinate líšia?
4. Prečo override oslabuje Git authority?
5. Ako tracking ovplyvňuje diff a prune?
6. Ako sa auto-sync, self-heal, prune a allowEmpty líšia?
7. Ktoré risks nesú Replace, SSA a prune options?
8. Prečo phases/waves nenahrádzajú readiness a idempotency?
9. Prečo `GITOPS-PAY-61` prešlo ako Synced/Healthy?
10. Ktoré positive, drift, recovery, rollback a forbidden paths musia prejsť?

## Glossary impact

Relevantné pojmy: Argo CD Application subject, AppProject boundary, repo-server render generation, application controller, resolved revision graph, parameter override, multi-source Application, automated sync, self-heal, prune, allow-empty, sync option, resource tracking identity, installation ID, ignoreDifferences, sync phase, sync wave, resource hook, ApplicationSet authority, false-Synced a Argo acceptance verdict.

## Primárne zdroje

- [Argo CD — Architectural Overview](https://argo-cd.readthedocs.io/en/stable/operator-manual/architecture/)
- [Argo CD — Application Specification](https://argo-cd.readthedocs.io/en/stable/user-guide/application-specification/)
- [Argo CD — Projects](https://argo-cd.readthedocs.io/en/stable/user-guide/projects/)
- [Argo CD — Automated Sync Policy](https://argo-cd.readthedocs.io/en/stable/user-guide/auto_sync/)
- [Argo CD — Sync Options](https://argo-cd.readthedocs.io/en/stable/user-guide/sync-options/)
- [Argo CD — Resource Tracking](https://argo-cd.readthedocs.io/en/stable/user-guide/resource_tracking/)
- [Argo CD — Diff Customization](https://argo-cd.readthedocs.io/en/stable/user-guide/diffing/)
- [Argo CD — Sync Phases and Waves](https://argo-cd.readthedocs.io/en/stable/user-guide/sync-waves/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Reconciliation a drift detection](reconciliation-and-drift-detection.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Flux →](flux.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
