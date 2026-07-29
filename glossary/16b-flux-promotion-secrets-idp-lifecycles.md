# Flux, promotion, GitOps secrets a Internal Developer Platform lifecycles

## Flux subject

Exact Flux installation, source object/revision/artifact, Kustomization alebo HelmRelease generation, render/decryption inputs, service account, target, inventory, health a business acceptance scope. Pozri [Flux](../docs/16-gitops-and-platform-engineering/flux.md).

## GitOps Toolkit

Súbor composable Kubernetes APIs a controllerov Fluxu, ktoré oddeľujú source acquisition, manifest reconciliation, Helm release management, notifications a image automation. Pozri [Flux](../docs/16-gitops-and-platform-engineering/flux.md).

## Source controller — Flux

Flux controller, ktorý autentizuje remote Git/OCI/Helm/bucket source, resolve-ne revision, vytvorí content artifact a publikuje jeho revision, digest a readiness downstream consumerom. Pozri [Flux](../docs/16-gitops-and-platform-engineering/flux.md).

## Source artifact — Flux

Packaged in-cluster content vytvorený source-controllerom z exact resolved remote revision a identifikovaný revision/digestom pre downstream reconciliation. Pozri [Flux](../docs/16-gitops-and-platform-engineering/flux.md).

## Kustomize controller — Flux

Flux controller, ktorý fetchne source artifact, voliteľne vykoná SOPS decryption, Kustomize build, validation, server-side apply, inventory, prune a health assessment. Pozri [Flux](../docs/16-gitops-and-platform-engineering/flux.md).

## Flux Kustomization

Custom Resource opisujúci sourceRef, path, interval, dependencies, decryption, substitutions, apply identity, prune a health reconciliation pipeline; nie je totožný so súborom `kustomization.yaml`. Pozri [Flux](../docs/16-gitops-and-platform-engineering/flux.md).

## HelmRelease — Flux

Custom Resource opisujúci desired Helm release, chart artifact, values, service-account identity, install/upgrade/test/remediation a release-history lifecycle. Pozri [Flux](../docs/16-gitops-and-platform-engineering/flux.md).

## Notification controller — Flux

Flux controller pre webhook receivers, events a outbound notifications; webhook urýchľuje observation, ale nenahrádza periodic reconciliation. Pozri [Flux](../docs/16-gitops-and-platform-engineering/flux.md).

## Image automation writer — Flux

Automatizovaná identity, ktorá podľa registry observation a ImagePolicy mení označené Git fields a vytvára nový desired-state commit. Pozri [Flux](../docs/16-gitops-and-platform-engineering/flux.md).

## Flux inventory

Controller-maintained identity set resources aplikovaných konkrétnou Kustomization, používaný na ownership correlation a garbage collection. Pozri [Flux](../docs/16-gitops-and-platform-engineering/flux.md).

## Server-side apply policy — Flux

Per-resource policy určujúca, ako Flux server-side apply koordinuje desired fields s inými field managers, napríklad Override, Merge, IfNotPresent alebo Ignore. Pozri [Flux](../docs/16-gitops-and-platform-engineering/flux.md).

## Flux dependency

Reference z Kustomization alebo HelmRelease na iný Flux reconciliation subject, ktorá blokuje dependent, kým dependency nesplní definovaný readiness contract. Pozri [Flux](../docs/16-gitops-and-platform-engineering/flux.md).

## Readiness expression — Flux

CEL expression spresňujúci, či dependency alebo custom resource dosiahli required generation-aware readiness; chybný expression môže vytvoriť false-ready alebo permanentne blocked stav. Pozri [Flux](../docs/16-gitops-and-platform-engineering/flux.md).

## Post-build substitution — Flux

Render input aplikovaný po source acquisition počas Kustomization build-u z inline values alebo ConfigMap/Secret references; external mutable reference môže vytvoriť hidden desired-state writera. Pozri [Flux](../docs/16-gitops-and-platform-engineering/flux.md).

## Flux impersonation

Použitie explicitného tenant service accountu controllerom pri target mutation, aby Kubernetes authorization obmedzila scope Kustomization alebo HelmRelease namiesto broad controller identity. Pozri [Flux](../docs/16-gitops-and-platform-engineering/flux.md).

## Flux suspension

Control-plane stav, ktorý dočasne zastaví reconciliation konkrétneho Flux objectu; nie je rollbackom a nemení desired ani live generation. Pozri [Flux](../docs/16-gitops-and-platform-engineering/flux.md).

## Flux acceptance verdict

Dôkaz, že exact source artifact, downstream render/apply identity, field ownership, inventory/prune, health, workload a business generations vytvárajú reproducible, tenant-bounded a recoverable reconciliation bez hidden inputs. Pozri [Flux](../docs/16-gitops-and-platform-engineering/flux.md).

## Application promotion

Riadený authority transition, ktorým presne identifikovaný immutable release candidate po target-relevant evidence a policy decisione vstupuje do desired state-u ďalšieho environmentu. Pozri [Application promotion](../docs/16-gitops-and-platform-engineering/application-promotion.md).

## Promotion subject

Exact candidate artifact/dependency/configuration contract, source a target environment revisions, evidence snapshot, approval/policy version, authoritative Git transition a target acceptance scope. Pozri [Application promotion](../docs/16-gitops-and-platform-engineering/application-promotion.md).

## Release candidate identity

Immutable coordinates source commit-u, build provenance, artifact digestov, chart/package versions a compatibility metadata, ku ktorým sa viaže promotion evidence. Pozri [Application promotion](../docs/16-gitops-and-platform-engineering/application-promotion.md).

## Build-once promotion

Model, v ktorom sa rovnaký immutable artifact overuje a povoľuje v postupných environmentoch bez uncontrolled environment-specific rebuild-u. Pozri [Application promotion](../docs/16-gitops-and-platform-engineering/application-promotion.md).

## Artifact invariant

Release property, ktorá musí zostať viazaná na candidate naprieč environmentmi, napríklad image digest, required schema/event capability alebo secret key format. Pozri [Application promotion](../docs/16-gitops-and-platform-engineering/application-promotion.md).

## Environment-owned configuration

Desired-state fields legitímne vlastnené konkrétnym environmentom, napríklad capacity, regional endpoint, exposure alebo target secret reference, ktoré nie sú samotným application artifactom. Pozri [Application promotion](../docs/16-gitops-and-platform-engineering/application-promotion.md).

## Candidate evidence bundle

Subject-bound collection provenance, test, scan, compatibility, staging, operational a business evidence použitého pri environment eligibility decisione. Pozri [Application promotion](../docs/16-gitops-and-platform-engineering/application-promotion.md).

## Promotion proposal

Versionovaný návrh exact environment desired-state delta, často pull request, obsahujúci candidate identity, target base revision, rendered change, evidence a recovery plan. Pozri [Application promotion](../docs/16-gitops-and-platform-engineering/application-promotion.md).

## Promotion freshness

Platnosť evidence a approvalu vzhľadom na unchanged candidate, transitive dependencies, source environment result, target base state, policy version a časové obmedzenia. Pozri [Application promotion](../docs/16-gitops-and-platform-engineering/application-promotion.md).

## Stale promotion

Proposal alebo approval, ktorého subject, dependencies, evidence alebo target base sa po rozhodnutí zmenili, takže už neautorizuje final effective generation. Pozri [Application promotion](../docs/16-gitops-and-platform-engineering/application-promotion.md).

## Promotion compare-and-swap

Precondition, že source evidence revision, candidate digest a target base commit stále zodpovedajú proposal-u pred authoritative merge transitionom. Pozri [Application promotion](../docs/16-gitops-and-platform-engineering/application-promotion.md).

## Promotion ledger

Durable operation a evidence record prepájajúci candidate, approvals, Git transition, GitOps reconciliation, runtime generation, exposure a business verdict bez preberania desired-state authority od Git-u. Pozri [Application promotion](../docs/16-gitops-and-platform-engineering/application-promotion.md).

## Superseded promotion

Pending alebo partially processed candidate, ktorý bol explicitne nahradený novším proposalom a už nesmie neskorým merge-om prepísať target desired state. Pozri [Application promotion](../docs/16-gitops-and-platform-engineering/application-promotion.md).

## Promotion acceptance verdict

Dôkaz identity continuity od immutable candidate-u cez fresh evidence, final-merge validation, authoritative target transition, controller resolution, runtime generation a business acceptance. Pozri [Application promotion](../docs/16-gitops-and-platform-engineering/application-promotion.md).

## GitOps secret subject

Exact secret purpose, authority, tenant/environment/workload scope, encrypted payload alebo provider reference, decryption/retrieval identity, target, consumer load behavior, rotation a revocation contract. Pozri [GitOps secrets](../docs/16-gitops-and-platform-engineering/gitops-secrets.md).

## Secret authority

System alebo provider, ktorý vytvára secret value, prideľuje jej version/generation, určuje active/revoked state a riadi rotation alebo lease lifecycle. Pozri [GitOps secrets](../docs/16-gitops-and-platform-engineering/gitops-secrets.md).

## Secret desired state

Git-managed encrypted payload alebo external-secret reference, schema, target a lifecycle policy bez tvrdenia, že rovnakú generation už používa workload. Pozri [GitOps secrets](../docs/16-gitops-and-platform-engineering/gitops-secrets.md).

## Materialized secret state

Plaintext secret bytes vytvorené po decryption alebo provider fetchi v Kubernetes Secret-e, volume alebo inom runtime delivery mechanism-e. Pozri [GitOps secrets](../docs/16-gitops-and-platform-engineering/gitops-secrets.md).

## Encrypted-in-Git secret

Model, v ktorom repository versionuje ciphertext a decryption metadata, zatiaľ čo autorizovaný GitOps controller vytvára plaintext až na target reconciliation boundary. Pozri [GitOps secrets](../docs/16-gitops-and-platform-engineering/gitops-secrets.md).

## External secret reference

Git-managed declaration provider objectu, property a voliteľnej version policy, podľa ktorej controller alebo workload získava secret z external authority. Pozri [GitOps secrets](../docs/16-gitops-and-platform-engineering/gitops-secrets.md).

## SOPS data key

Náhodný symmetric key použitý na encryption secret values v jednom SOPS documente a následne envelope-encrypted pre configured KMS alebo age recipients. Pozri [GitOps secrets](../docs/16-gitops-and-platform-engineering/gitops-secrets.md).

## SOPS recipient

KMS key, age public identity alebo iný master-key coordinate autorizovaný otvoriť encrypted SOPS data key pre konkrétny document. Pozri [GitOps secrets](../docs/16-gitops-and-platform-engineering/gitops-secrets.md).

## Decryption identity

Controller alebo workload principal oprávnený použiť KMS key, age private key alebo equivalent mechanismus na vznik plaintextu z encrypted desired payloadu. Pozri [GitOps secrets](../docs/16-gitops-and-platform-engineering/gitops-secrets.md).

## SealedSecret

Kubernetes Custom Resource obsahujúci ciphertext zašifrovaný pre public key Sealed Secrets controllera a voliteľne viazaný na target namespace/name. Pozri [GitOps secrets](../docs/16-gitops-and-platform-engineering/gitops-secrets.md).

## ExternalSecret

Custom Resource deklarujúci external provider reference, refresh behavior, transformáciu a target Kubernetes Secret materialization. Pozri [GitOps secrets](../docs/16-gitops-and-platform-engineering/gitops-secrets.md).

## SecretStore

Namespaced External Secrets provider/authentication configuration, ktorej Kubernetes a provider IAM scope majú obmedziť secret access konkrétneho tenant boundary. Pozri [GitOps secrets](../docs/16-gitops-and-platform-engineering/gitops-secrets.md).

## ClusterSecretStore

Cluster-scoped External Secrets provider configuration zdieľateľná naprieč namespaces; vyžaduje silnejší provider-path a consumer authorization contract pre väčší blast radius. Pozri [GitOps secrets](../docs/16-gitops-and-platform-engineering/gitops-secrets.md).

## Secret refresh policy

Consistency contract určujúci, či sa external value materializuje periodicky, iba pri desired object change-i alebo iba pri prvotnom vytvorení. Pozri [GitOps secrets](../docs/16-gitops-and-platform-engineering/gitops-secrets.md).

## Loaded secret generation

Secret version, ktorú running application process skutočne načítal a používa, odlišná od current provider version alebo Kubernetes Secret resourceVersion. Pozri [GitOps secrets](../docs/16-gitops-and-platform-engineering/gitops-secrets.md).

## Secret overlap rotation

Rotation state machine, v ktorom sú stará aj nová credential generation dočasne validné, kým sa nová materializuje, všetci consumers na ňu prejdú a až potom sa stará revokuje. Pozri [GitOps secrets](../docs/16-gitops-and-platform-engineering/gitops-secrets.md).

## Secret consumer convergence

Dôkaz, že všetky required workload instances používajú new secret generation pred revocation old generation. Pozri [GitOps secrets](../docs/16-gitops-and-platform-engineering/gitops-secrets.md).

## Secret-zero problem

Potreba bezpečne bootstrapnúť prvú identity alebo credential, ktorou controller získa access ku KMS alebo secret provideru; workload identity znižuje závislosť od static bootstrap keys. Pozri [GitOps secrets](../docs/16-gitops-and-platform-engineering/gitops-secrets.md).

## GitOps secret acceptance verdict

Dôkaz, že secret authority, encrypted/reference desired state, decryption identity, materialization, consumer reload, rotation, revocation, tenancy a recovery tvoria bezpečný lifecycle bez plaintext Git-u alebo stale loaded credentialu. Pozri [GitOps secrets](../docs/16-gitops-and-platform-engineering/gitops-secrets.md).

## Platform engineering

Disciplína navrhovania, budovania a prevádzkovania shared internal platform capabilities ako products pre bezpečnejšie a jednoduchšie software delivery a operations. Pozri [Internal Developer Platform](../docs/16-gitops-and-platform-engineering/internal-developer-platform.md).

## Internal Developer Platform

Productized system capabilities, APIs, workflows, controllers, policies, metadata a support model, ktorý poskytuje developerom bounded self-service od requestu po usable runtime outcome. Pozri [Internal Developer Platform](../docs/16-gitops-and-platform-engineering/internal-developer-platform.md).

## Internal developer portal

Experience a aggregation layer pre discovery, catalog, documentation, templates a operations; môže byť súčasťou IDP, ale sama nepredstavuje celý platform control plane. Pozri [Internal Developer Platform](../docs/16-gitops-and-platform-engineering/internal-developer-platform.md).

## Platform capability

Versionovaný internal product contract, napríklad managed runtime, database alebo delivery flow, s definovanými inputs, outputs, guarantees, constraints, ownershipom, supportom a lifecycle-om. Pozri [Internal Developer Platform](../docs/16-gitops-and-platform-engineering/internal-developer-platform.md).

## Capability contract

Machine- a human-readable definícia platformovej služby určujúca allowed request, defaults, policy, generated resources, observable success, support, update, migration a deletion semantics. Pozri [Internal Developer Platform](../docs/16-gitops-and-platform-engineering/internal-developer-platform.md).

## Platform request subject

Exact requester/team, capability/version, service identity, environment, data/operations tier, requested inputs, quota, policy bundle, idempotency key a expected outputs jednej platform operation. Pozri [Internal Developer Platform](../docs/16-gitops-and-platform-engineering/internal-developer-platform.md).

## Platform API

Authoritative interface alebo declarative resource model, ktorým clients vyjadrujú high-level platform intent a control plane ho transformuje na bounded downstream operations. Pozri [Internal Developer Platform](../docs/16-gitops-and-platform-engineering/internal-developer-platform.md).

## Experience plane — IDP

Portal, CLI, documentation a status interfaces, cez ktoré developer objavuje capability, zadáva request a pozoruje operation bez preberania authority underlying systems. Pozri [Internal Developer Platform](../docs/16-gitops-and-platform-engineering/internal-developer-platform.md).

## Platform control plane

Vrstva, ktorá validuje intent, udržiava durable operation state, vyhodnocuje policy, orchestruje downstream systems a koreluje resources a outcomes. Pozri [Internal Developer Platform](../docs/16-gitops-and-platform-engineering/internal-developer-platform.md).

## Execution plane — IDP

Git, CI, IaC, cloud, Kubernetes, GitOps, secret a observability systems, v ktorých platform control plane vykonáva alebo deleguje konkrétne mutations. Pozri [Internal Developer Platform](../docs/16-gitops-and-platform-engineering/internal-developer-platform.md).

## Durable platform operation

Persistovaný distributed workflow record s operation ID, semantic subjectom, step state-om, downstream resource IDs, attempts, partial outcomes a recovery verdictom. Pozri [Internal Developer Platform](../docs/16-gitops-and-platform-engineering/internal-developer-platform.md).

## Platform idempotency

End-to-end property, že retry rovnakého semantic platform requestu read-backne a obnoví ten istý intended resource graph namiesto vytvorenia duplicates alebo conflicting side effects. Pozri [Internal Developer Platform](../docs/16-gitops-and-platform-engineering/internal-developer-platform.md).

## Identity reservation — IDP

Skorá atomic alebo unique reservation service/repository/namespace/DNS identity, ktorá serializuje concurrent requests a chráni downstream provisioning pred duplicate creation. Pozri [Internal Developer Platform](../docs/16-gitops-and-platform-engineering/internal-developer-platform.md).

## Platform authority graph

Explicitné mapovanie platform metadata, Git desired state-u, IaC/provider state-u, GitOps reconciliation, secret authority a runtime statusu na ich authoritative systems a writers. Pozri [Internal Developer Platform](../docs/16-gitops-and-platform-engineering/internal-developer-platform.md).

## Scaffolding template

Versionovaný input schema a action workflow, ktorý vytvára initial software/resource structure; generated copy po creation typicky diverguje, pokiaľ ďalší lifecycle neudržiava managed contract. Pozri [Internal Developer Platform](../docs/16-gitops-and-platform-engineering/internal-developer-platform.md).

## Catalog projection

Developer-facing index a relation model odvodený z catalog declarations a authoritative runtime/platform evidence, ktorý nesmie byť zamenený za live alebo desired-state authority. Pozri [Internal Developer Platform](../docs/16-gitops-and-platform-engineering/internal-developer-platform.md).

## Self-service boundary

Authorization, schema, quota a policy envelope, v ktorom autentizovaný tenant môže bez central ticketu spustiť vopred approved platform action bez unrestricted underlying privilege. Pozri [Internal Developer Platform](../docs/16-gitops-and-platform-engineering/internal-developer-platform.md).

## Platform compensation

Per-step bounded recovery action pre partial distributed platform operation, vykonaná iba pri explicitnej eligibility a preconditions, nie generický destructive rollback. Pozri [Internal Developer Platform](../docs/16-gitops-and-platform-engineering/internal-developer-platform.md).

## Developer-functional verification

Dôkaz, že platform owner output nielen vytvorila, ale application team ho môže reálne použiť, napríklad autentizovať sa, deploynuť sample alebo pripojiť k managed capability. Pozri [Internal Developer Platform](../docs/16-gitops-and-platform-engineering/internal-developer-platform.md).

## IDP acceptance verdict

Dôkaz, že exact request, capability contract, durable/idempotent operation, authoritative writers, tenant guardrails, downstream reconciliation, developer-functional outcome, lifecycle a second-request recovery tvoria pravdivú usable platform capability. Pozri [Internal Developer Platform](../docs/16-gitops-and-platform-engineering/internal-developer-platform.md).
