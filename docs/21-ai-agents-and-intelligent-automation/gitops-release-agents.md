# GitOps a release agents

GitOps a release agent môže vytvoriť manifest, aktualizovať image digest, otvoriť pull request, spustiť sync alebo navrhnúť rollback. Jeho bezpečný scope je orchestration nad versioned desired state; controller a target platform zostávajú authority pre reconciliation a live state.

V incidente `AGENT-DELIVERY-12` release agent zmenil deployment repository z immutable digestu na `stable` tag, pretože pipeline output neobsahoval digest. Pull request prešiel syntaktickou kontrolou a Harness GitOps application dosiahla `Synced`. Cluster však stiahol inú image generation na časti nodov a business verification chýbala. Agent následne navrhol Argo CD rollback, hoci auto-sync zostal zapnutý a Git stále deklaroval chybný tag.

Nosný lifecycle je:

```text
approved release candidate a artifact digest
→ exact Git repository, revision, path a environment
→ agent-generated desired-state diff
→ render, policy, provenance a ownership validation
→ pull request a human approval
→ authoritative Git commit
→ GitOps controller resolution a sync plan
→ ordered apply, health a business verification
→ drift, degraded state alebo incident
→ Git revert/forward fix a controlled reconciliation
→ second-release acceptance
```

## 1. Git desired state

Git repository je authority pre deklarovaný state iba v definovanom scope. Branch, commit, path, Helm values, Kustomize overlays a external dependencies tvoria exact desired-state subject.

Agent nesmie zameniť default branch alebo similarly named environment. Release manifest pinne repository URL a commit.

## 2. Live state

Live Kubernetes objects sú effective state targetu. Controller porovnáva rendered desired state s live state a reportuje sync a health conditions.

Git commit alebo merged PR nepreukazuje apply. `Synced` navyše nepreukazuje user-facing business outcome.

## 3. Harness GitOps architecture

Harness GitOps service riadi control-plane operácie a GitOps Agent v customer environment-e spolupracuje s Argo CD components. Agent potrebuje cluster a repository connectivity a scoped service account.

AI release agent nesmie preskočiť túto authority. Vytvára návrhy alebo volá povolené operations cez Harness API a RBAC.

## 4. Argo CD control loop

Argo CD repository server renderuje manifests z repository URL, revision, path a template settings. Application controller kontinuálne porovnáva live a desired state a môže vykonať sync.

Render inputs sa ukladajú do release evidence. Branch name bez resolved commitu je mutable reference.

## 5. Artifact identity

Release používa immutable image digest a provenance. Tag môže byť ľudský alias, ale desired state viaže digest alebo podpisom overiteľnú immutable reference.

Agent nesmie fallbacknúť na `latest`, `stable` alebo chýbajúci output. Missing digest zablokuje promotion.

## 6. Release subject

Release subject spája application, service, environment, artifact, configuration a database/schema generation. Dva deployments rovnakého image s odlišnými values, feature flags alebo migration state sú rozdielne releases.

Incident analysis preto nepoužíva iba image version. Manifest eviduje všetky composed generations a ich authority, aby bolo možné oddeliť binary regression od configuration alebo target-specific problému.

## 7. Agent proposal

Release agent pripraví Git diff a release plan. Nemá priamo meniť cluster mimo documented break-glass path.

Proposal obsahuje target, current commit, desired commit, artifact digest, rollout strategy, expected health a rollback path. Unresolved field zostáva explicitný.

## 8. Semantic diff

Semantic diff zvýrazní image, replicas, resources, RBAC, network policy, service routing, migrations, sync options a prune behavior. Formátovací diff sa minimalizuje.

High-risk changes vyžadujú owner review a environment-specific tests. Agent nemôže skryť destructive option v generovanom blocku.

## 9. Render validation

Helm, Kustomize alebo plugin render sa vykoná s pinned tool version a dependencies. Výsledné Kubernetes objects sa schema-validujú a policy-checkujú.

Validation používa target API versions a CRDs podľa možnosti. `SkipDryRunOnMissingResource` je explicitná exception, nie univerzálny fix.

## 10. Ownership a shared resources

Release agent overí, ktorý Application alebo controller resource vlastní. Argo CD môže failnúť pri shared resource, ak je zapnutý relevantný sync option.

Conflicting field managers a multi-source applications komplikujú authority. Agent nesmie predpokladať exclusive ownership.

## 11. Policy a admission

Git policy kontroluje desired state pred merge; admission controller kontroluje request pri apply. Oba gates sú potrebné, pretože cluster context môže odhaliť ďalšie constraints.

AI môže vysvetliť violation, ale nevypína policy ani nevytvára broad exemption. Emergency waiver má ownera, expiry a incident reference.

## 12. Pull-request promotion

Agent vytvára PR s release manifestom, rendered diff summary, provenance, blast-radius klasifikáciou a verification planom. Protected branch vyžaduje human alebo policy approvals a checks nad exact merge candidate.

Merge commit je authoritative desired-state transition. Agent session alebo chat `Accept` ho nenahrádza a stale approval sa po zmene release diffu invaliduje.

## 13. Sync plan

Pred apply sa vytvorí plan: resources to create, update, replace, prune a hooks/waves. Destructive operations sú zvýraznené.

Argo CD podporuje preview changes a confirmation pre pruning alebo deletion. Agent má používať tieto controls pre critical resources.

## 14. Sync phases a waves

PreSync, Sync a PostSync hooks a sync waves určujú order. Lower waves sa vytvárajú skôr a nezdravá skoršia wave môže zastaviť ďalší postup.

Agent musí rozumieť dependency graphu. Náhodné zmenenie wave čísla môže obísť migration alebo readiness prerequisite.

## 15. Health

Controller health vychádza z resource-specific conditions. Healthy Deployment nemusí znamenať, že dependency, route alebo business transaction funguje.

Release gate kombinuje controller health s Continuous Verification, synthetic canary a business invariant. No-data je unknown.

## 16. Sync status

`OutOfSync` znamená rozdiel desired/live podľa compare rules. `Synced` znamená, že tracked fields zodpovedajú, nie že workload je funkčný.

Ignore differences môžu skryť drift. Každá ignore rule má ownera, reason a test, že nezakrýva security alebo availability field.

## 17. Automated sync

Automated sync znižuje potrebu priameho CI accessu k Argo CD. Prune, self-heal, allow-empty a retry však menia risk a musia byť explicitne versioned.

Argo CD dokumentácia uvádza safety defaults a upozorňuje, že rollback nie je možný pri zapnutom automated sync. Recovery plan preto používa Git revert alebo dočasnú kontrolovanú zmenu policy.

## 18. Prune

Prune odstraňuje resources, ktoré už nie sú v desired state. Namespace, PVC a shared resource môžu mať vysoký blast radius.

`Prune=confirm`, `Delete=confirm`, `PruneLast` alebo no-delete annotations sú deterministic guardrails. Agent ich nesmie odstrániť kvôli „stuck sync“.

## 19. Replace a force

`Replace=true` a `Force=true` môžu resource recreateovať a spôsobiť outage. Agent môže tieto options navrhnúť iba s explicitným destructive-change classification a approvalom.

Preferred recovery je pochopiť immutable-field alebo ownership problem. Force nie je generický troubleshooting step.

## 20. Server-side apply

Server-side apply eviduje field ownership, ale `--force-conflicts` môže prevziať fields od iného managera. Agent kontroluje managedFields a expected owner.

Migration z client-side apply sa plánuje a testuje. Partial manifest s disabled validation nie je automaticky bezpečný.

## 21. Retry a self-heal

Retry rieši transient sync failure; self-heal opravuje live drift podľa Git. Ani jedno neopraví chybný desired state.

Ak Git deklaruje incident-causing configuration, self-heal ju môže znovu aplikovať po manuálnom hotfixe. Containment najprv upraví authority alebo suspendne reconciliation podľa runbooku.

## 22. Drift

Drift sa klasifikuje ako authorized external controller field, manual emergency change, malicious change alebo stale desired state. Agent zhromaždí Git, rendered a live diff.

Automatické correction je povolené iba pre známy owned scope. Unknown drift sa nesmie overwriteovať bez evidence.

## 23. Release gates

Promotion gate vyhodnocuje provenance, policy, tests, environment freeze, approvals, dependency readiness a target capacity. Model output môže vysvetliť failed condition alebo navrhnúť remediation, nie rozhodnúť o override.

Gate result je deterministic, versioned a auditable. Missing, stale alebo scope-mismatched evidence vytvára `blocked` alebo `unknown`, nikdy implicitný pass.

## 24. Progressive delivery

Canary alebo blue-green release obmedzuje blast radius. Agent navrhuje traffic steps a analysis windows, ale controller a verification system presadzujú thresholds.

Rýchle zvýšenie trafficu na základe model summary je forbidden. Každý step má evidence a abort condition.

## 25. Database a stateful changes

Schema migration, queue format alebo persistent data znižujú jednoduchú rollback schopnosť. Release plan obsahuje forward/backward compatibility a backup/restore evidence.

Agent nesmie odporučiť image rollback, ak stará binary nevie čítať novú schému. Recovery môže byť forward fix.

## 26. Rollback semantics

Argo CD vie rollbacknúť application history, ale pri auto-sync sú významné constraints a Git môže následne obnoviť chybný desired state. Preferovaný GitOps rollback je reviewed revert alebo forward commit.

Rollback command success nepreukazuje obnovu. Controller musí reconcileovať exact revision a business verification musí prejsť.

## 27. Emergency containment

Containment môže pozastaviť auto-sync, zablokovať promotion, scale down mutation worker alebo prepnúť traffic. Každý zásah má incident ownera a expiry.

Live hotfix bez Git update vytvára drift a môže byť self-healed. Runbook presne určuje, kedy je povolený a ako sa authority zosúladí.

## 28. Release evidence

Evidence bundle obsahuje source commit, manifest commit, rendered objects digest, artifact provenance, policy results, sync operation, live resource versions, health observations a business verification.

UI screenshot je sekundárny a časovo nepresný dôkaz. Machine-readable export, timestamps a checksums umožnia neskoršiu reprodukciu aj rozlíšenie desired, applied a observed state.

## 29. Positive acceptance

Agent navrhne PR s immutable digestom, render a policy checks prejdú a reviewer schváli semantic diff. Controller syncne exact Git commit v správnych waves.

Application dosiahne Synced a Healthy a business canary prejde. Druhá release s novým digestom overí, že agent nepoužíva stale context.

## 30. Forbidden acceptance

Test ponúkne mutable tag, wrong project path, shared resource, unconfirmed namespace prune, force replace alebo unsigned artifact. Agent alebo deterministic gates musia promotion zablokovať.

Očakáva sa nulová target mutation. Warning bez blocku je pre high-risk scenario nedostatočný.

## 31. Recovery acceptance

Po chybnom release sa promotion zastaví, Git desired state sa revertne alebo opraví a auto-sync behavior sa kontrolovane nastaví. Controller reconcileuje known-good commit.

Health, business canary a provider read-back potvrdia obnovu. Následná druhá safe release overí, že pipeline a agent context sú opravené.

## 32. Practical release manifest

Release manifest je composed identity release candidate-u: viaže source a manifest commit, immutable artifact, controller application generation a požadované verification gates. Bez tejto väzby sa `Synced`, image tag alebo pipeline execution nedajú spätne priradiť k jednému authoritative release subjectu.

Nasledujúci príklad je deklarovaný release intent pred vykonaním. Neobsahuje tvrdenie `verified`; tento stav môže vzniknúť až po controller read-backu, resource health a business canary v konkrétnom environment-e.

```yaml
release:
  application: payments-prod
  source_repo: ssh://git.example/platform-config
  source_commit: 8ef31ab
  manifest_path: clusters/prod/payments
  artifact:
    image: registry.example/payments
    digest: sha256:9ae1...
    provenance: sha256:77c2...
  gitops:
    controller: argocd
    application_generation: 41
    sync_options:
      prune: false
      self_heal: true
  verification:
    resource_health: required
    synthetic_payment: required
    business_metric_window: 15m
```

Manifest je release intent. Stav `verified` sa doplní až z controller a business evidence po reálnom vykonaní.

## 33. Primary sources

Aktuálna Harness dokumentácia opisuje GitOps service a Agent architecture aj DevOps Agent operations nad GitOps resources. Argo CD dokumentácia definuje repository server, application controller, sync, health, auto-sync a destructive sync options; Flux dokumentácia dopĺňa reconciliation, suspension a Ready conditions.

Harness control-plane a in-cluster GitOps Agent boundary je popísaná na https://developer.harness.io/docs/continuous-delivery/gitops/get-started/gitops-architecture/ a installation, connectivity a scoped-agent requirements na https://developer.harness.io/docs/continuous-delivery/gitops/gitops-entities/agents/install-a-harness-git-ops-agent/.

Argo CD component authority a continuous desired/live comparison dokumentuje https://argo-cd.readthedocs.io/en/stable/operator-manual/architecture/. Automated sync a rollback constraints sú na https://argo-cd.readthedocs.io/en/stable/user-guide/auto_sync/, destructive a ownership-sensitive options na https://argo-cd.readthedocs.io/en/stable/user-guide/sync-options/ a explicitný sync/preview surface na https://argo-cd.readthedocs.io/en/stable/user-guide/commands/argocd_app_sync/. Flux reconciliation, suspension a Ready conditions poskytujú porovnávací primary model na https://fluxcd.io/flux/components/kustomize/kustomizations/. Zdrojové statusy podporujú controller semantics, nie automatický business outcome.

## Zhrnutie

Release agent nesmie nahradiť Git review, controller reconciliation ani business verification. Jeho hodnota je v konzistentnom návrhu, semantic diff-e, evidence assembly a bounded orchestration.

Incident `AGENT-DELIVERY-12` vznikol preto, že mutable artifact reference, `Synced` status a rollback command boli nesprávne použité ako dôkazy. Správny model viaže immutable desired state na live read-back a user-facing outcome.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Agentický code review, testing a remediation](agentic-code-review-testing-remediation.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Incident triage a evidence collection →](incident-triage-evidence-collection.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
