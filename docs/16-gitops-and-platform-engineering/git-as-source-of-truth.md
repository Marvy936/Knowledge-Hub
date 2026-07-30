# Git ako source of truth

Git je source of truth iba vtedy, keď jedna presne definovaná Git generation autoritatívne opisuje všetky riadené desired fields a neexistuje skrytý writer s vyššou alebo nejasnou precedence. Samotná prítomnosť YAML súborov v repozitári nestačí. Git commit môže byť immutable, no branch, tag, parameter override, mutable artifact, render plugin alebo live patch môžu zmeniť effective desired state bez novej reviewed transition.

```text
business alebo platform intent
→ exact environment/application/field subject
→ protected authoritative ref a promotion decision
→ immutable commit + pinned input graph
→ deterministic controller render
→ policy, ownership a target resolution
→ bounded reconciliation
→ live a loaded effective state
→ workload health a business acceptance
→ drift, rollback a second-change closure
```

Git nepatrí byť autoritou nad každým runtime factom. Queue offset, current database leader, Pod status, metrics, ephemeral lease alebo provider outcome sú observed alebo operational state. Git vlastní deklaratívny intent; controllers a runtime produkujú evidence, či sa intent skutočne realizoval.

## 1. Desired-state subject a tri vrstvy pravdy

Exact subject musí pomenovať repository a trust boundary, path, ref a resolved commit, environment/cluster/namespace/application, manifests alebo chart/overlay, image a dependency digests, values a parameters, secret references, render toolchain, field ownership, controller/destination, promotion evidence, rollback a break-glass contract.

Pri každom release treba oddeliť:

```text
Git-declared desired state
→ čo opisuje reviewed commit

controller-resolved desired state
→ commit + overrides + dependencies + render generation

live/effective state
→ API objects + generated children + loaded config/secrets + runtime behavior
```

Tieto vrstvy sa môžu rozísť. Git môže deklarovať správny image, controller môže použiť override a live Deployment môže byť neskôr patchnutý humanom. Naopak live system môže fungovať, hoci jeho state nemožno reprodukovať z Git-u. To je unmanaged operational debt, nie úspešný GitOps verdict.

## 2. Immutable objects, mutable refs a promotion authority

Git commit object je content-addressed a immutable. Ref je mutable pointer:

```text
refs/heads/production
→ commit A
→ neskôr commit B alebo force-reset C
```

Tag možno retagovať a branch force-pushnúť. Preto release evidence musí zachytiť resolved commit SHA a ref-protection generation, nie iba názov `production`. Fully qualified ref odstraňuje branch/tag ambiguity, no stále potrebuje protection a audit.

Commit tiež nemusí identifikovať celý release, ak manifest používa mutable input:

```yaml
image: registry.example/payments:latest
```

Rovnaký Git commit môže zajtra renderovať iný digest. Reprodukovateľná generation preto zahŕňa commit, image/chart/plugin/module digests, dependency locks, external values generation, policy bundle a secret-reference generation.

Source commit sa stáva production authority až promotion decisionom:

```text
candidate commit a immutable artifacts
→ target-specific tests a policy evidence
→ reviewed promotion transition
→ protected environment ref/manifest update
→ controller observation a reconciliation
```

Environment branch, directory, promotion PR alebo commit-pinned Application môžu byť správne. Podstatné je, aby bolo zrejmé, ktorá transition oprávnila konkrétny input graph pre konkrétny target.

## 3. Source graph a deterministic render

Application repository, environment repository a platform repository môžu mať odlišných ownerov. Effective desired state je potom graph:

```text
application image digest
+ chart commit/digest
+ environment values commit
+ platform/policy generation
+ secret reference generation
+ renderer/plugin version
→ final object inventory
```

Controller musí evidovať všetky resolved inputs. Jeden commit label nestačí pri multi-source renderi. Helm, Kustomize alebo plugin output je ďalšia authority boundary; reproducibility vyžaduje pinned toolchain, deterministic inputs, kontrolovaný network access, explicitné environment variables a comparison CI renderu s controller renderom.

Acceptance evidence obsahuje final rendered object identities, image digests, critical config generations a target scope. `CI template check passed` nie je production evidence, ak controller používa inú Helm version, hidden plugin input alebo cache staršej dependency.

## 4. Overrides, writers a field ownership

Parameter override je druhý desired-state writer:

```text
Git values: image.digest=pay900a
Argo override: image.digest=pay899hf7
→ controller desired state=pay899hf7
```

External input nie je automaticky zakázaný. HPA môže vlastniť replicas, External Secrets Secret data a operator generated children. Každý critical field však potrebuje jedného authoritative writer-a, explicitnú merge/precedence semantics a observable generation.

Writer inventory má zahŕňať GitOps controller, CI credentials, human kubectl, autoscalers, operators, admission webhooks, image automation, secret controllers, feature-flag systems a Application overrides. Dvaja reconcilers môžu byť lokálne idempotentní a spolu oscillovať. Broad ignore rule taký konflikt iba skryje.

Observed status sa nemá automaticky zapisovať späť ako intent:

```text
runtime observation
→ evidence alebo proposal
→ explicitný decision
→ nový reviewed desired-state commit
```

Bez decision boundary vzniká feedback loop, v ktorom transient runtime state prepisuje authoritative intent.

## 5. Governance, trust a break-glass

Repository s production authority potrebuje chránené refs, required review/checks, explicitných owners, scoped automation identity, secret scanning, artifact provenance a retained history. Review musí vidieť target-specific rendered delta a destructive consequences, nie iba source YAML diff.

CI, ktoré má production kubeconfig a po merge vykoná `kubectl apply`, je production writer. Git môže zostať evidence source, ale nie jediná mutation authority. Silný pull model oddeľuje CI permission na build/promotion od controller identity pri targete.

Break-glass direct mutation môže byť legitímna, ak je bounded:

```text
incident + approval
→ short-lived scoped credential
→ exact mutation a evidence
→ owner + expiry
→ immediate Git proposal/reconciliation
→ controller policy restore
→ credential revoke
→ injected second-drift test
```

Temporary patch bez expiry a mandatory reconciliation sa stáva permanentným druhým source of truth. Rollback je nový desired-state transition, ktorý obnoví celý input graph. Zmena branch pointera sama neodstráni Application override, live-only field, incompatible database generation ani external effect.

## 6. Connected incident `GITOPS-PAY-61`

Atlas Payments release `payments 9.0` mal prejsť:

```text
release manifest commit 9f31c2a
→ reviewed production ref
→ Argo resolves exact inputs
→ render 63 resources
→ sync
→ workload health
→ settlement canary
```

Git deklaroval image `sha256:pay900a`, route policy `1842`, replicas `24` a termination grace `45 s`. Effective writers však boli Git environment repository, stale Argo CLI override, CI direct apply, human patch, HPA a admission mutation.

Override držal image `sha256:pay899hf7`; CI aplikovala route generation `1841`; on-call patchla live image na `sha256:pay900b`; system-wide ignore rule skryl celý containers subtree; automated sync bol zapnutý, `selfHeal` nie; production branch povoľovala force push a sedem minút ukazovala na starší commit.

Po 38 minútach existovali tri generations:

```text
Git declared:     pay900a / route 1842
Argo resolved:    pay899hf7 / route 1842
live Deployment:  pay900b / route 1841
```

Argo ukazovalo `Synced`, pretože critical fields boli ignorované. `Healthy` potvrdzovalo ready Pods, nie intended image alebo policy. Osemnásť Podov bežalo na `pay900b`, šesť na `pay899hf7`; `3 214` settlements použilo policy `1841` a `96` operations potrebovalo provider-ledger reconciliation.

Root cause bol multi-writer desired state a controller override mimo Git-u. Force-mutable ref, broad ignore, disabled self-heal a acceptance podľa `Synced/Healthy` boli amplifiers.

## 7. Recovery a acceptance paths

Recovery fence-nula CI a human writers, exportovala Git/Application/override/cache/live managedFields evidence, odstránila override, zúžila ignore rule, commitla jednu intended generation a overila rendered, live aj loaded digests. Affected settlements sa reconciliovali podľa operation a provider identity.

**Positive path** promotion jednej pinned generation vedie cez controller render k exact live/runtime generation a business canary.

**Recovery path** po direct drift-e alebo controller restarte obnoví Git-owned fields bez straty legitimate HPA/operator ownershipu.

**Rollback path** obnoví celý resolved graph a potvrdí compatibility i business outcome, nie iba ref.

**Forbidden path** odmietne hidden override, mutable dependency bez recorded resolution, force-push bez gate-u, CI/human writer nad Git-owned fields, broad ignore a false-Synced outcome.

Acceptance zahŕňa second promotion, force-reset attempt, mutable-dependency test, controller cache/restart, direct drift a break-glass expiry/reconciliation.

## 8. Troubleshooting a anti-patterny

Pri stave `Git tvrdí A, runtime vykonáva B` sa ide od exact application/environment subjectu cez repo/path/ref/commit, artifact a renderer generations, Application parameters/overrides, rendered inventory, live objects/managedFields, writer precedence, diff rules, loaded runtime generation a business outcome.

Najčastejšie anti-patterny sú `všetko je v Git-e`, hoci existujú mutable inputs; branch name považovaný za production authority; Git history považovaná za immutable ref; status auto-commitovaný do desired source; permanentný break-glass patch; a `Synced` interpretované ako zhoda s tým, čo človek vidí v repository.

## 9. Kontrolné otázky

1. Čo tvorí exact desired-state subject?
2. Ako sa Git, controller-resolved a effective state líšia?
3. Prečo commit je immutable, ale branch alebo tag nie?
4. Čo tvorí úplnú release input generation?
5. Ktorá transition robí candidate authoritative pre production?
6. Prečo parameter override predstavuje druhého writera?
7. Ako field ownership oddeľuje GitOps, HPA, operatora a secret controller?
8. Kedy CI prestáva byť iba build systémom a stáva sa deployment writerom?
9. Prečo `GITOPS-PAY-61` ostal `Synced`?
10. Ktoré positive, recovery, rollback a forbidden paths musia prejsť?

## Glossary impact

Relevantné pojmy: desired-state subject, source-of-truth boundary, authoritative ref, promotion transition, immutable desired generation, resolved input graph, controller-resolved desired state, render boundary, parameter override, writer inventory, field authority, break-glass writer, effective runtime generation, source-of-truth rollback a source-of-truth acceptance verdict.

## Primárne zdroje

- [OpenGitOps Principles](https://opengitops.dev/)
- [Git — Data model](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects)
- [Git — gitrevisions](https://git-scm.com/docs/gitrevisions)
- [Argo CD — Tracking and Deployment Strategies](https://argo-cd.readthedocs.io/en/stable/user-guide/tracking_strategies/)
- [Argo CD — Parameter Overrides](https://argo-cd.readthedocs.io/en/stable/user-guide/parameters/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Idempotency a backpressure](../15-databases-and-distributed-systems/idempotency-and-backpressure.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Pull-based deployment →](pull-based-deployment.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
