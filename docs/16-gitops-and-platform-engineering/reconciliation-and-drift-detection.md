# Reconciliation a drift detection

Reconciliation je control loop, ktorý opakovane resolve-ne desired generation, pozoruje live state, klasifikuje rozdiel a vykoná iba mutation povolenú field ownershipom, safety a recovery contractom. Drift detection nie je automatické revertovanie každého rozdielu. Najprv musí rozlíšiť unauthorized drift, legitimate controller writer-a, API defaulting, admission mutation, dependency change, stale observation a runtime mismatch.

```text
exact desired generation a resource inventory
→ live object identity a observation generation
→ normalization, mutation a ownership context
→ semantic desired/live delta
→ drift class a business risk
→ report, reconcile, ignore, adopt, contain alebo refuse
→ bounded apply/prune + read-back
→ workload/runtime convergence
→ health a business acceptance
→ second observation a recurrence closure
```

`Synced`, `Healthy` a `business accepted` sú tri rozdielne verdicts. Diff engine môže byť zelený nad nesprávnym oracle-om a health môže potvrdiť ready Pods s nesprávnym image alebo config generation.

## 1. Subject a desired/observed/effective state

Exact subject obsahuje Application/controller identity, source revision a render inputs, target cluster/namespace/API generation, desired a tracked live resource set, object UID a tracking ID, field managers/writers, normalization a ignore policy, sync/prune/self-heal policy, operation history, health/business oracle a rollback/decommission boundary.

Treba oddeľovať:

```text
desired state
→ controller-resolved target objects

observed state
→ live API objects v observation čase

effective runtime state
→ ReplicaSets/Pods + loaded config/secrets + endpoints + behavior
```

Deployment spec môže byť zhodný s desired manifestom, no staré Pods alebo process-loaded Secret stále používajú predchádzajúcu generation. Naopak raw YAML diff môže ukazovať harmless defaulting bez behavior change.

## 2. Loop, semantic diff a unknown mutation

Reconciler vykonáva source observation, render, target observation, normalization, comparison, classification, action a requeue. Loop musí byť idempotentný voči converged state-u, bounded retrymi/mutations, obnoviteľný po restarte a truthful pri partial alebo unknown outcome-e.

Semantic diff zohľadňuje API schema/defaulting, quantities, unordered lists, status/metadata, managed fields, admission mutation a controller-generated fields. Raw text diff nie je správny oracle. Normalizácia však nesmie odstrániť critical behavior difference.

API timeout po PATCH-i vytvára unknown outcome:

```text
controller odošle mutation
→ API ju aplikuje
→ response sa stratí
→ controller timeout
```

Ďalší krok je fresh read-back stable object identity. Blind retry môže znovu spustiť hook, vytvoriť ďalší generated resource alebo prepísať novší writer state.

## 3. Drift classification a field authority

Drift classification sa začína otázkou, komu patrí odlišný field alebo resource. Ak human alebo pipeline priamo zmení Git-owned image či config, ide o unauthorized drift a reconciler ho môže po safety gate-e opraviť. Ak HPA mení replicas, operator spravuje child resources alebo secret controller materializuje data, rozdiel môže byť legitimate delegated writer state a slepý revert by vytvoril oscillation.

API defaulting, serialization a admission-injected sidecar môžu vytvoriť normalization alebo mutation delta bez porušenia intentu. Naopak nezmenený manifest s mutable image tagom, chartom alebo external Secretom môže vytvoriť dependency drift bez source diffu. Missing, orphaned a tracking-collision resources patria do inventory driftu. Posledná class je runtime drift: desired aj live spec vyzerajú správne, ale Pods, loaded configuration, endpointy alebo external behavior nespĺňajú contract.

```text
Git-owned unauthorized delta
→ reconcile alebo contain

delegated writer delta
→ ignore iba exact owned field + monitor

normalization/mutation delta
→ schema-aware canonicalization a bounded exception

dependency/inventory/runtime delta
→ resolve generation, ownership a business impact
```

`managedFields` pomáha identifikovať field managers, ale nie je business authority oracle. Manager name môže byť broad, stale alebo shared. Contract musí určiť exact field paths a expected writer-a. Po klasifikácii controller môže reportovať, reconcile-nuť, úzko ignorovať, adoptovať live value cez reviewed Git proposal, contain-nuť incident alebo odmietnuť mutation pre nejasnú authority. Action sa odvodzuje z field authority a risku, nie z existencie diffu.

## 4. Ignore rules a false negatives

Ignore rule je versionovaná exception z drift oracle-u. Potrebuje exact object/field/manager scope, ownera, dôvod, expected writer-a, expiry/revalidation a positive i forbidden negative fixture.

Broad rule:

```yaml
ignoreDifferences:
  - group: apps
    kind: Deployment
    jqPathExpressions:
      - .spec.template.spec.containers
```

môže skryť image, env, command, ports, probes, resources a security context. Ak diff zmizne, Application je `Synced` a self-heal nemá trigger. Manager-wide ignore môže rovnako skryť viac fields než intended.

Ignored fields musia zostať observable mimo sync labelu. Legitimate sidecar injection sa rieši exact sidecar-owned paths alebo normalized expected outputom, nie vypnutím oracle-u pre celý containers subtree.

## 5. Self-heal, prune a loop safety

Drift detection iba zisťuje rozdiel. Self-heal automaticky syncne live drift bez novej source revision. Je vhodný pre deleted resources a unauthorized Git-owned changes, ale nebezpečný pri emergency patchi, shared resource, source corruption, nejasnom ownershipe alebo hooku s external effectom.

Prune odstráni tracked live resource chýbajúci v validnom desired inventory. Bezpečný gate vyžaduje successful non-empty/non-ambiguous render, tracking/ownership proof, deletion eligibility, ordering a dependent/business validation. Failed render nesmie byť interpretovaný ako authoritative empty set.

Permanentný conflict môže vytvoriť hot loop:

```text
GitOps apply
→ webhook/operator prepíše field
→ diff
→ apply
→ ...
```

Loop potrebuje backoff, rate limit, repeated-delta detection a containment. Inak spotrebuje API, renderer, webhook a audit capacity bez convergence.

## 6. Sync, health a business evidence

`Synced` znamená iba, že desired a live objekty sa podľa current diff rules nepovažujú za odlišné. `Healthy` používa resource-specific health logic. Business acceptance potvrdzuje intended capability a forbidden outcomes.

```text
Synced
≠ applied complete history
≠ Healthy
≠ correct loaded generation
≠ business accepted
```

Critical release evidence má obsahovať resolved revision/input graph, rendered object inventory, live template/image/config digests, Pod cohort generations, loaded policy/secret generation, route/endpoints a business canary. Runtime mismatch musí vedieť zneplatniť release verdict aj pri zelenom Argo status-e.

## 7. Connected incident `GITOPS-PAY-61`

System-wide Argo customization ignorovala celý Deployment containers subtree. Súčasne bolo `selfHeal=false`, CI a human menili Deployment priamo, parameter override menil desired image a HPA ownership replicas nebolo dokumentované.

```text
Git:               pay900a / route 1842
Argo resolved:     pay899hf7 / route 1842
live Pod template: pay900b / route 1841
running Pods:      pay900b + pay899hf7
```

Diff pipeline odstránil critical image/env delta, takže Application zostala `Synced`. ManagedFields pritom ukazovali Argo, CI service account aj human kubectl managera. Osemnásť a šesť Podov používalo dve image generations; request traces dokazovali route policy `1841`; commit `9f31c2a` nikdy nebol celý effective.

Root cause bol broad false-negative oracle a chýbajúci one-writer/business-generation contract. Recovery freeze-nula writers, zachovala YAML/managedFields, odstránila broad ignore, vytvorila narrow sidecar rule, odstránila override, commitla exact generation, zapla scoped self-heal a overila loaded policy aj second injected drift.

## 8. Acceptance paths

**Positive path** exact desired generation renderuje a converge-ne na live/runtime generation, ktorú potvrdí business canary.

**Delegated-writer path** HPA/operator zmení iba vlastné fields bez oscillation alebo false driftu.

**Recovery path** po direct delete/patchi alebo controller restarte self-heal obnoví Git-owned state a read-back preukáže convergence.

**Failure path** pri source/render/target uncertainty odmietne destructive prune a označí stav truthful unknown/unreachable.

**Forbidden path** odmietne broad ignore false negative, multi-writer oscillation, empty-render delete storm, false-Synced/Healthy a repeated hot loop.

Acceptance zahŕňa manual drift, HPA ownership, admission mutation, missing/orphan resource, API timeout, prune, source corruption, controller restart a second reconciliation.

## 9. Troubleshooting a anti-patterny

Pri OutOfSync, false-Synced alebo hot loope sa mapuje Application/source/render generation, tracked UID/ID, raw desired/live objects, defaulting/mutation, ignore rules/managedFields, sync/self-heal/prune policy, controller operation/read-back, loaded runtime a business generation.

Anti-patterny sú automaticky revertovať každý drift, manager-wide ignores, `Synced=deployed`, `Healthy=správna verzia`, prune bez ownership proof a nekonečné reconciliation retries bez classification/backoffu.

## 10. Kontrolné otázky

1. Ako sa desired, observed a effective runtime state líšia?
2. Čo tvorí exact reconciliation subject?
3. Prečo raw YAML diff nie je vždy oracle?
4. Ako sa drift classes líšia podľa authority?
5. Kde managedFields pomáhajú a kde nestačia?
6. Ako broad ignore vytvára false negative?
7. Ako sa detection a self-heal líšia?
8. Čo musí overiť prune eligibility?
9. Prečo `GITOPS-PAY-61` zostal `Synced`?
10. Ktoré positive, delegated, recovery, failure a forbidden paths musia prejsť?

## Glossary impact

Relevantné pojmy: reconciliation subject, desired state, observed state, effective runtime state, semantic diff, drift taxonomy, field authority, managedFields evidence, ignore exception, false-Synced, self-heal, prune eligibility, unknown apply outcome, reconcile hot loop, business-generation oracle a reconciliation acceptance verdict.

## Primárne zdroje

- [OpenGitOps Principles](https://opengitops.dev/)
- [Kubernetes — Controllers](https://kubernetes.io/docs/concepts/architecture/controller/)
- [Argo CD — Diff Customization](https://argo-cd.readthedocs.io/en/stable/user-guide/diffing/)
- [Argo CD — Automated Sync Policy](https://argo-cd.readthedocs.io/en/stable/user-guide/auto_sync/)
- [Argo CD — Resource Tracking](https://argo-cd.readthedocs.io/en/stable/user-guide/resource_tracking/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Pull-based deployment](pull-based-deployment.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Argo CD →](argo-cd.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
