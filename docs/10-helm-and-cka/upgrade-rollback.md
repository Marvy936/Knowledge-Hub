# Upgrade a rollback

Helm upgrade je riadený prechod z jednej release generation do druhej. Nemení iba image reference. Mení chart artifact, dependency graph, effective values, rendered manifests, hooks, Kubernetes objects a často aj schema, event alebo external durable state.

Rollback je ďalší release transition, nie návrat času. Vie použiť historický Helm chart/config/manifest subject a vytvoriť novú revision, ale automaticky nevráti databázu, queue, CRD storage, PVC obsah, external transactions, DNS, IAM ani už načítanú credential generation. Technicky úspešný rollback preto môže byť business-nekompatibilný recovery state.

## 1. Dominantný release transition lifecycle

Bezpečná zmena začína current a target subjectom, nie samotným `helm upgrade`. Najprv sa uzavrú immutable inputs, compatibility a side-effect inventory, potom sa vytvorí target render a semantic diff. Až po eligibility gate sa vykonajú hooks a API mutations, nasleduje Kubernetes reconciliation a samostatné technical a business acceptance.

```text
change intent a recovery objective
→ current release a durable-state subject
→ target release a input closure
→ compatibility a side-effect inventory
→ effective values, render a semantic diff
→ preconditions a recovery eligibility
→ hooks a release mutation
→ Kubernetes/runtime convergence
→ technical a business acceptance
→ rollback, roll-forward, compensation alebo restore
→ recovery verification a old-state retirement
```

Upgrade je bezpečný iba vtedy, keď je jasné, čo sa mení, kto je authoritative writer, ktoré side effects sú durable, či je predchádzajúca application generation kompatibilná s current state-om a ako sa overí pôvodný business outcome.

## 2. Exact Atlas transition subject

Current Atlas Payments state je release `payments-prod` revision 19 s chartom `CH57`, lockom `D57`, values `V57`, manifestom `M57`, image `I57`, schema `S13` a event contractom `E1`.

Target revision 20 používa `CH58`, `D58`, `V58`, `M58`, image `I58`, schema `S14`, event contract `E2` a cluster generation `K136`. Exact transition subject obsahuje source/target revisions, všetky chart/dependency/values/render/image identities, hook operation IDs, data/schema/event generations, cluster/context/namespace, deployment engine a Helm version.

Samotné číslo revision nie je recovery coordinate. Revision 19 môže odkazovať na artifact, ktorý už registry neuchováva, alebo na application version nekompatibilnú s current E2 backlogom. Historický manifest je iba jeden vstup do eligibility rozhodnutia.

## 3. Revision, values a input closure

Helm history obsahuje states ako deployed, superseded, failed alebo pending upgrade/rollback. Helm revision však nie je Git commit, chart version, application version, Deployment revision, schema generation ani event version. Koreláciu vytvára release evidence cez digests, labels, annotations a operation IDs.

Upgrade output závisí od chartu, locku a packaged dependencies, chart defaults, stored previous values, explicitných values files a CLI overrides, merge mode, release context, capabilities, live lookups, post-rendererov, Helm/plugins a target API/admission state-u. Reprodukovateľnosť vyžaduje uzavretý immutable input set.

Production model preferuje explicitný target values bundle. `--reuse-values` prenáša stored legacy keys, booleans a subchart enablement a môže vytvoriť configuration závislú od cluster histórie. Reset modes môžu naopak odstrániť required customizations. Pred release sa preto porovnajú current stored effective values, new defaults, explicitné target overrides a výsledný V58. Secrets sa nearchivujú v plaintext forme.

## 4. Current, target a live baseline

Pred mutation sa zachovajú tri baseline-y: current Helm-stored manifest a values, current live Kubernetes objects a proposed target render. Rozdiel medzi stored a live state-om môže vzniknúť defaultingom, admission, HPA, operatorom, GitOps controllerom, emergency patchom alebo secret/config reload controllerom.

Tieto differences sa klasifikujú podľa field authority. Rollback nesmie prepísať legitímny HPA-owned field ani bojovať s GitOps desired state-om bez rozhodnutia, ktorý writer je authoritative. Naopak manual image patch nie je dôvod považovať live object za správnejší než reviewed Git/Helm intent.

Live baseline zahŕňa object UID/generations, ReplicaSet/Pod image digests, EndpointSlice cohorts, PVC identities, loaded config/secret epochs a business request evidence. Helm manifest sám nevysvetľuje actual serving state.

## 5. Precondition a recovery eligibility gate

Upgrade sa spustí iba pri zdravom API/control plane-e, jednom release writerovi, dostatočnej capacity a failure-domain headroom-e, prijateľnom SLO state-e, dostupnom recovery evidence, zdravých dependencies/external systems a retained target aj fallback artifacts.

Gate musí vopred určiť rollback, roll-forward, compensation a restore boundaries. Ak current backup nie je restore-tested, rollback target je nekompatibilný alebo prebieha incident, release nemá bezpečný recovery envelope.

Stateful transition navyše posudzuje writer/fencing epoch, quorum a version skew, schema/protocol compatibility, snapshot generation a storage ownership. Manifest rollback pri stále aktívnom novom writerovi môže vytvoriť split-brain alebo stale writes.

## 6. Render, diff a server validation

Target build používa reviewed dependency lock, schema a semantic tests, deterministic render a server-side validation. Semantic diff sa sústreďuje na identity/names, selectors, images, ConfigMap/Secret references, Service traffic policy, PVC/StorageClass, RBAC/securityContext, hooks, CRDs, resources, probes a rollout budgets.

Textový YAML diff nie je posledný oracle. Server dry-run a admission môžu ukázať defaulting, mutation, field conflicts alebo unsupported API. Runtime comparison následne overí controller children a serving cohort. Kritická release decision musí vidieť aj durable schema/event changes, ktoré nie sú v Kubernetes manifeste.

## 7. Execution, wait a unknown outcome

Upgrade prechádza target renderom, pre-upgrade operations, sériou API mutations, release storage transitionom, controller reconciliation, post-upgrade tests a acceptance. Zlyhanie pred prvým write-om má inú recovery než timeout po migration, partial rollout alebo event publication.

`--wait` a Job waiting majú presne definovanú resource/readiness boundary. Green Helm wait nepreukazuje image digest na každom serving Pode, loaded configuration, edge traffic, schema/event compatibility, exactly-once outcome ani user journey.

Timeout je observation deadline. Kubernetes controllers môžu po client timeout-e ďalej convergovať, hook môže commitnúť a release storage môže zostať pending. Pred retry sa read-backne history, hooks, live generations a external ledgers. Blind retry môže vytvoriť ďalšiu revision nad už zmeneným state-om.

## 8. Automatic a manual rollback

Automatic failure recovery môže podľa exact Helm version/flags aplikovať previous release intent, vytvoriť rollback revision a vykonať rollback hooks. Nevracia durable data alebo external state. Je bezpečná iba vtedy, keď predchádzajúca application generation zostáva kompatibilná s current schema, events, credentials, APIs a artifacts.

Manual `helm rollback` tiež vytvára novú revision. Target subject obsahuje historical chart/dependency/values/manifest, referenced images, hooks, current Kubernetes APIs/CRDs, current schema/data/event generation a current external/secret state. Chýbajúci image digest alebo unsupported API robia historickú revision nereprodukovateľnou.

Pending upgrade/rollback predstavuje unknown outcome. Recovery zachová release storage a hook evidence, identifikuje source/target subjects, overí aktívne processes, porovná stored manifests, live objects a external state a klasifikuje completed, partial a unknown operations. Ručná editácia release Secrets je posledný version-specific zásah, nie prvý troubleshooting krok.

## 9. Compatibility matrix a recovery mechanizmy

Rollback eligibility sa hodnotí cez old application × current schema, event backlog, external API, credential epoch, Kubernetes API a CRD storage version. Verdict je eligible, eligible with compensation, not eligible alebo unknown. Unknown nie je dôvod skúsiť rollback; je to blocker, kým sa nezíska evidence alebo nezvolí bezpečnejší containment.

Rollback je vhodný pri backward-compatible durable state-e, nulových alebo reverzibilných side effectoch a dostupných artifacts. Roll-forward je vhodnejší po dokončenej incompatible migration alebo vtedy, keď malý fix obnoví correctness. Compensation rieši external registration, duplicate message, payment alebo IAM/DNS effect. Restore je DR operácia s vlastným RPO/RTO, fencing a reconciliation modelom.

Force replacement nie je všeobecný recovery mechanizmus. Delete/recreate môže zmeniť Service/LB identity, StatefulSet/PVC binding, immutable selector, CRD alebo object s finalizerom. Immutable-field error je požiadavka na explicitnú identity migration, nie signál na univerzálne `--force`.

## 10. CRD, data a concurrent writer boundaries

CRD lifecycle nie je symetrický s Helm history. Rollback controllera musí zohľadniť served/storage versions, conversion webhook, stored-version migration a current custom resources. Old controller môže byť deployed a napriek tomu current objects nevedieť dekódovať.

Helm revision nevlastní obsah PVC ani application membership. Stateful rollout potrebuje current data generation, fencing, version-skew contract, snapshot/restore test a protocol compatibility. Retained PVC môže po rollbacku obsahovať data zapísané novšou application generation.

Súbežní writers zahŕňajú Helm pipeline, GitOps, kubectl, operatora, autoscalers a secret/config controllers. Ownership sa definuje na field a lifecycle úrovni. Inak GitOps okamžite zvráti manual rollback alebo rollback prepíše legitímnu novšiu controller zmenu.

## 11. Connected incident: technický rollback, business failure

Atlas prechádzal z revision 19 na 20. Target menil image I57 na I58, schema S13 na S14 cez expand migration, outbound event E1 na E2 a consumer config na C58. Migration dokončila S14 a časť new Podov publikovala E2. Rollout sa potom zastavil, pretože C58 neobsahovala required fraud-service endpoint. Automatic failure recovery obnovila revision 19 manifests a vytvorila rollback revision 21.

Helm hlásil revision 21 ako deployed, ale payment backlog rástol. Hypotézy zahŕňali neaplikovaný rollback, unavailable I57, unready Pody, schema incompatibility, E2 decode failure, stale I58 endpoints, rollback-hook side effect a independent broker incident.

History a manifests potvrdili revision 21. Pod UIDs/image digests a EndpointSlices ukázali iba I57 serving cohortu. Schema S14 bola backward-compatible. Queue distribution a consumer errors však dokázali, že I57 nevedel dekódovať E2 backlog, zatiaľ čo broker bol healthy. Helm rollback bol technicky úspešný; recovery subject nebol business-compatible.

Containment zastavilo ďalšie retries/rollbacks, pozastavilo E2 producers, zachovalo mixed queue, nevymazalo messages, udržalo API v bounded degraded mode a zablokovalo schema contract cleanup.

Rollback bol klasifikovaný ako not eligible. Recovery zvolila roll-forward: opravila fraud endpoint v C58, vytvorila I58.1 s tolerantným E1/E2 consumerom, server-validovala revision 22, nasadila bounded cohortu, drainovala mixed backlog a overila idempotency/payment ledger pred rozšírením rollout-u.

Acceptance potvrdila revision 22, serving I58.1, schema S14, queue lag na baseline, exactly-once spracovanie E1 aj E2 a jedinú ledger transaction pre P-884. Forbidden tests vylúčili E2 decode failure a duplicate authorization. Neskorší contract cleanup sa povolil až po retirement old consumers.

## 12. Troubleshooting a release evidence

Pri incidente sa fixnú source/target/rollback revisions a ich immutable inputs, potom sa porovnajú stored a live objects, hooks, Pod cohorts, EndpointSlices, schema/event/config generations a external ledgers. Prvá divergentná boundary rozhoduje medzi rollbackom, roll-forwardom, compensation a restore.

Produkčný transition record obsahuje source/target subjects, effective values, render digest, semantic/admission diff, hooks a operation IDs, image/schema/event/config generations, technical/business acceptance, recovery eligibility a final closure evidence. Cluster release history nie je jediný DR source.

Najčastejšie anti-patterny sú `--reuse-values` ako hidden authority, wait považovaný za business success, timeout okamžite retryovaný, automatic rollback bez compatibility gate, historical revision považovaná za validný state, force replacement pri immutable errori, CRD rollback bez storage analysis a Helm rollback zamieňaný za data restore.

## Kontrolné otázky

1. Čo tvorí exact current a target release subject?
2. Prečo explicitný target values contract znižuje history dependence?
3. Čo Helm wait a revision status skutočne dokazujú?
4. Ako sa určuje rollback eligibility nad current durable state-om?
5. Kedy je bezpečnejší roll-forward alebo compensation?
6. Prečo pending operation predstavuje unknown outcome?
7. Ako CRD, PVC a concurrent writers menia rollback semantics?
8. Ktoré business a forbidden outcomes uzatvárajú recovery?

## Glossary impact

Relevantné pojmy: Helm release transition subject, upgrade input closure, recovery eligibility gate, rollback compatibility matrix, technical rollback, business-compatible recovery, pending-operation unknown outcome, compensation, roll-forward a release transition closure.

## Primárne zdroje

- [Helm — `helm upgrade`](https://helm.sh/docs/helm/helm_upgrade/)
- [Helm — `helm rollback`](https://helm.sh/docs/helm/helm_rollback/)
- [Helm — `helm history`](https://helm.sh/docs/helm/helm_history/)
- [Helm — `helm status`](https://helm.sh/docs/helm/helm_status/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Hooks](hooks.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Helm testing a troubleshooting →](helm-testing-troubleshooting.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
