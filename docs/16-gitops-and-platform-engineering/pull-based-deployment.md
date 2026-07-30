# Pull-based deployment

Pull-based deployment je trust a execution model, v ktorom target-side agent s vlastnou scoped identity resolve-ne approved desired state, porovná ho s targetom a vykoná mutation. Nie je to iba smer sieťového spojenia ani webhook po merge-i. Jeho hlavná hodnota vzniká vtedy, keď CI a developers nemajú všeobecný production write credential a agent zostáva jediným authoritative executorom riadených fields.

```text
approved environment intent
→ exact source/agent/target subject
→ periodic source observation + webhook hint
→ authenticated revision a input resolution
→ deterministic render a target-aware policy
→ desired/live comparison
→ manual alebo automated sync decision
→ bounded apply, prune a health observation
→ effective runtime a business acceptance
→ continuous re-observation, rollback a second pull
```

Pull model zachováva identity a evidence od authoritative Git generation po exact target mutation. Auto-sync, self-heal a prune sú samostatné policies; nie sú definíciou pull modelu.

## 1. Deployment subject a credential boundary

Exact subject obsahuje environment a application, repository/path/ref/resolved revisions, source trust a credentials, render inputs/toolchain, destination cluster/namespace, agent identity a Kubernetes permissions, allowed resource kinds, sync/prune/self-heal policy, tracking identity, hooks, health/business oracle a rollback/break-glass contract.

Push model:

```text
CI runner
→ production credential
→ rendered payload alebo commands
→ target mutation
```

Pull model:

```text
CI
→ artifact + reviewed Git promotion

agent pri targete
→ read trusted source
→ resolve/render/compare
→ mutate scoped target
```

Rozdiel určuje, kto drží production credentials, kto rozhoduje o source generation, či deployment pokračuje bez CI a či neskorší drift možno detegovať a opraviť. Controller s cluster-admin prístupom ku všetkým clusters môže byť rovnako nebezpečnou trust concentration; pull neodstraňuje potrebu AppProject/RBAC, repository isolation a auditovania agent identity.

## 2. Source observation a revision resolution

OpenGitOps model vyžaduje declarative, versioned/immutable desired state, software agentov, ktorí ho automaticky pullujú, a continuous reconciliation actual state-u. Webhook je iba latency hint:

```text
Git push
→ webhook refresh

súčasne
→ periodic poll a re-resolution
```

Ak webhook vypadne, agent musí zmenu nakoniec objaviť. Ak branch force-pushne, dependency sa zmení alebo cache zostarne, agent musí znovu resolve-nuť effective source. Observation interval, jitter a bounded concurrency určujú delivery aj drift-detection latency a zabraňujú fleet thundering herd-u.

Agent overuje repository endpoint, SSH/TLS trust, credential scope, fully qualified ref, resolved commit/chart digest, path, submodules/dependencies, plugin generation a revoked access. `release-9.0` môže byť branch aj tag; fully qualified ref alebo commit pin znižuje ambiguity.

## 3. Render, policy a sync authority

Agent-side render vidí final source inputs a destination context. Pred mutation má prebehnúť schema/parse validation, target-aware policy, semantic diff a server-side/dry-run kontrola. CI validation je useful, ale nemôže nahradiť agent gate, ak používa inú toolchain generation alebo nevidí target policies.

Pull neznamená automatický sync. Agent môže iba reportovať `OutOfSync`, čakať na approval/change window alebo vykonať automated sync. CI môže zavolať refresh alebo sync API a model zostáva pull-based, ak CI neposiela hidden manifests, agent sám resolve-ne authority a používa vlastnú target identity.

Sync operation inventarizuje desired/tracked resources, porovnáva state, aplikuje v poradí, prípadne prune-ne, čaká na resource health a publikuje evidence. Apply success nie je business success. Settlement canary, loaded config generation a provider path zostávajú samostatnou acceptance boundary.

## 4. Continuous reconciliation a disconnected states

Jednorazový pull po merge-i nestačí:

```text
source generation A
→ reconcile
→ live drift alebo target recovery
→ new observation
→ report alebo repair
```

Agent po restarte musí rekonštruovať desired a live inventory bez hidden in-memory deployment state-u. Source outage sa nesmie označiť ako `Synced`; cached source môže byť stale a failed render nesmie vytvoriť empty desired set pre destructive prune. Target outage vytvára pending/unknown apply states; po reconnecte treba vedieť, či aplikovať newest generation alebo zachovať required transitional migrations.

API timeout po PATCH-i je unknown outcome. Agent musí vykonať read-back so stable object identity, nie slepo opakovať non-idempotent hook. Prune vyžaduje validný non-ambiguous desired inventory, tracking/ownership proof a bounded delete.

## 5. Hybrid writers, break-glass a rollback

Najčastejšie zlyhanie je hybrid:

```text
Git merge → Argo auto-sync
CI súčasne → kubectl apply
human → live patch
```

Writers používajú odlišné renders a field managers. Každý call môže technicky uspieť, no final state nemá jednu mutation authority ani deterministic rollback.

Break-glass musí koordinovať reconciler: incident approval, short-lived scoped credential, exact mutation, owner/expiry, immediate Git reconciliation, obnovenie sync/self-heal policy, revoke credential a second-drift test. Jednoduché vypnutie Argo bez návratového gate-u vytvára unmanaged environment.

Rollback je nový desired-state transition. `kubectl rollout undo` pri Git-e na broken generation vytvára drift a controller ho môže zrušiť. Kompletný rollback zahŕňa manifests/artifacts, database/config/secret compatibility, hooks, traffic/feature state a external reconciliation.

## 6. Connected incident `GITOPS-PAY-61`

Intended path bol build/test → environment PR → commit `9f31c2a` → Argo observation/render/sync → health/canary. Skutočný path bol commit → CI direct apply → Argo sync inej resolved generation → human patch, pričom self-heal bol vypnutý a critical differences ignorované.

Timeline:

```text
20:14:03 webhook refresh
20:14:04 CI direct apply
20:14:07 Argo sync
20:18:26 human patch
20:21:11 production ref force-reset
20:28:09 ref restored
```

CI render používal `pay900a + route 1841`, Argo `pay899hf7 + route 1842` a manual patch `pay900b`. CI malo production kubeconfig. Agent preto nebol jediný executor a rollback ref-u nemohol odstrániť override ani live-only fields.

Root cause bol hybrid push/pull ownership bez mandatory handoff a reconciliation. Recovery odobrala CI kubeconfig, oddelila Git promotion od target identity, scoped-nula Argo project permissions, odstránila hidden apply a zaviedla expiring break-glass lifecycle.

## 7. Acceptance paths

**Positive path** agent nezávisle pozoruje approved revision, resolve-ne celý input graph, prejde target policy, syncne a preukáže runtime/business outcome.

**Source/target recovery path** rozlíši source-unreachable, target-unreachable a unknown apply; po recovery bezpečne pokračuje bez empty prune alebo duplicitného hook effectu.

**Drift path** druhý pull odhalí a opraví Git-owned manual drift, pričom legitimate controller-owned fields zostanú nedotknuté.

**Forbidden path** odmietne hidden CI push, broad target credential, stale cached apply, ambiguous ref, direct rollback a agent, ktorý potrebuje webhook ako jediný observation mechanismus.

Acceptance zahŕňa webhook loss, source/target outage, agent restart, direct drift, partial sync, break-glass expiry, rollback a second pull.

## 8. Troubleshooting a anti-patterny

Pri nesúlade sa mapuje authoritative ref/resolved commit, webhook/poll evidence, source auth/cache/render, policy/diff/sync decision, target API response, field managers/concurrent writers, health a business outcome. `Pipeline zavolá kubectl, ale Git je source of truth`, `webhook=pull`, `auto-sync je povinný`, cluster-admin agent a live-only rollback sú typické anti-patterny.

## 9. Kontrolné otázky

1. Ako sa push a pull líšia v credential a executor boundary?
2. Prečo webhook nie je pull authority?
3. Čo musí agent resolve-nuť a overiť?
4. Prečo pull neznamená auto-sync?
5. Kedy CI-triggered sync zostáva pull modelom?
6. Ako source a target outage menia verdict?
7. Ako sa rieši unknown apply outcome?
8. Prečo hybrid writers porušili `GITOPS-PAY-61`?
9. Ako vyzerá bounded break-glass a rollback?
10. Ktoré positive, recovery, drift a forbidden paths musia prejsť?

## Glossary impact

Relevantné pojmy: pull-based deployment subject, target-side agent, target credential boundary, source observation, webhook hint, revision resolution, agent-side policy, sync decision, continuous pull, source-unreachable state, target-unreachable state, hybrid writer, break-glass handoff, desired-state rollback a pull acceptance verdict.

## Primárne zdroje

- [OpenGitOps Principles](https://opengitops.dev/)
- [Argo CD — Automated Sync Policy](https://argo-cd.readthedocs.io/en/stable/user-guide/auto_sync/)
- [Argo CD — Architectural Overview](https://argo-cd.readthedocs.io/en/stable/operator-manual/architecture/)
- [Argo CD — Tracking and Deployment Strategies](https://argo-cd.readthedocs.io/en/stable/user-guide/tracking_strategies/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Git ako source of truth](git-as-source-of-truth.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Reconciliation a drift detection →](reconciliation-and-drift-detection.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
