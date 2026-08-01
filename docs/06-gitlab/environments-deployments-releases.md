# Environments, deployments a releases

GitLab environment, deployment a Release opisujú tri rozdielne vrstvy delivery systému. Environment je named target/lifecycle subject. Deployment je GitLab record pokusu umiestniť konkrétnu ref alebo artifact generation do environmentu. GitLab Release je product/release metadata object viazaný na tag a assets. Ani jeden objekt samostatne nepreukazuje actual runtime digest, traffic exposure, application-loaded configuration alebo business acceptance.

Dôveryhodný lifecycle preto koreluje GitLab source/pipeline/job records s immutable release manifestom, environment generation, external deployment controllerom, runtime state-om a user outcome-om. GitOps job, ktorý vytvorí commit, nepreukazuje cluster convergence. Environment status `stopped` nepreukazuje cleanup external resources. Release asset URL na expiring job artifact nie je durable release unit.

## 1. Dominantný request-to-runtime model

Lifecycle oddeľuje request, GitLab workflow record, external controller convergence, runtime state a business acceptance. Tieto transitions môžu skončiť v rôznych časoch a s rôznym verdictom; job success preto nesmie automaticky nastaviť production success. Diagram nižšie je correlation contract medzi GitLabom a authoritative targetom.

```text
immutable release manifest and target intent
→ exact GitLab environment subject
→ protected deployment job/approval
→ deployment request and GitLab record
→ direct apply or external controller reconciliation
→ live/runtime artifact and config read-back
→ traffic/feature exposure
→ business acceptance or recovery
→ release support metadata and environment cleanup
```

Deployment record should distinguish request accepted, mutation applied, controller converged and release accepted.

## 2. Exact environment/deployment subject

Environment name je policy locator, nie úplná target identity. Exact subject musí pridať environment ID a generation, cluster/namespace alebo controller context, release manifest, deployment request a expected runtime digests. Bez toho sa rovnaké meno môže po migrácii alebo recreate viazať na iný target.

```yaml
deploymentSubject:
  projectId: 481
  environment:
    id: 77
    name: production/eu-central-1
    slug: production-eu-central-1
    externalUrl: https://payments.atlas.example
    generation: prod-eu-1844
    protectionGeneration: env-prod-44
  deployment:
    id: 8812
    pipelineId: 771184
    jobId: 881911
    sourceSha: d94e1c6
    releaseManifestDigest: sha256:release1000rc4
    status: running
  controller:
    type: flux
    requestCommit: 9f31c2a
    desiredRevision: 9f31c2a
  runtimeExpected:
    apiDigest: sha256:pay1000api
    configSha: 71ac290
```

Environment name is locator and policy input; generation identifies current target assumptions. Deployment status is GitLab workflow state, not complete runtime verdict.

## 3. Environment declaration

`environment:` block pripája job ku GitLab environment recordu a ovplyvňuje protection, variables, deployment tracking a stop lifecycle. Je to source declaration, ktorú treba porovnať s resolved jobom a effective environment patternom. Samotný YAML nevie potvrdiť cluster context ani úspešnú external mutation.

```yaml
production_deploy:
  stage: deploy
  environment:
    name: production/eu-central-1
    url: https://payments.atlas.example
    deployment_tier: production
    on_stop: stop_production
  script:
    - ./scripts/request-gitops-promotion.sh "$RELEASE_MANIFEST_DIGEST"
```

YAML declares environment association. It does not prove protected-environment match, correct URL, external controller completion or cleanup. Dynamic environment names require bounded input and policy.

## 4. Deployment record API

Deployment API je GitLab-side read-back workflow recordu. Query musí byť viazaná na exact project a environment locator a výsledok sa koreluje s pipeline, deployable jobom a release manifestom. API status nepreukazuje controller ani runtime outcome, ale umožní zistiť, ktorý request a actor GitLab považuje za deployment.

```bash
curl --fail --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "$GITLAB_URL/api/v4/projects/481/deployments?environment=production%2Feu-central-1" \
  | jq '.[] | {id,status,sha,ref,created_at,updated_at,deployable,environment}'
```

Output proves GitLab records visible to caller. It does not prove exact artifact digest unless stored in job/release metadata, nor controller/runtime outcome. Deployment job log and external system read-back are necessary.

## 5. Direct deployment versus GitOps request

Direct deployment job mutates target API. GitOps job mutates authoritative repository and external controller later reconciles. In direct model successful API request can still leave controller failure. In GitOps model successful commit/merge only proves desired-state request.

```text
GitLab deployment job success
→ for direct apply: request/command status
→ for GitOps: source mutation accepted

still required:
controller observed desired revision
→ live objects reconciled
→ runtime digests/config loaded
→ business outcome accepted
```

GitLab deployment status can be updated by callback after external acceptance, but correlation identity must be robust and idempotent.

## 6. Outdated deployment prevention and concurrency

Two pipelines can target same environment. Resource groups or platform controls serialize jobs, but stale job might resume after newer deployment. Deployment request needs expected current release/generation.

```yaml
production_deploy:
  resource_group: payments-production
  interruptible: false
```

Resource group serializes eligible jobs according to GitLab semantics. It does not automatically reject stale release after manual retry or external change. Script/controller compares current environment release manifest with expected predecessor.

## 7. Deployment approvals and environment identity

Approval should bind artifact digest, target generation and requested transition. Retry/rebuild after approval can change subject. Environment protection and scoped variables/ID tokens must match actual environment name.

Manual job is not approval evidence if any eligible operator can run it without policy. Emergency path has separate incident-scoped capability and closure.

## 8. Runtime read-back

Runtime read-back sa vykonáva až po potvrdení target contextu, aby presný output nepatril nesprávnemu clusteru alebo namespace-u. Najprv sa číta desired/controller state Deploymentu a potom per-Pod resolved image identity. Tieto outputs stále nepreukazujú serving route ani business behavior, preto na ne nadväzuje traffic a capability canary.

```bash
kubectl -n payments get deployment payments-api -o json | jq '{generation:.metadata.generation,observed:.status.observedGeneration,images:[.spec.template.spec.containers[].image],release:.metadata.annotations["atlas.example/release-manifest"]}'

kubectl -n payments get pods -l app=payments-api \
  -o jsonpath='{range .items[*]}{.metadata.uid}{" "}{.status.containerStatuses[0].imageID}{"\n"}{end}'
```

These outputs prove Kubernetes desired/controller/runtime image state for selected objects. They do not prove traffic, feature or business acceptance. Capability canary and route/flag read-back complete deployment verdict.

## 9. Review apps

Review app subject includes MR/candidate, namespace, URL/DNS, identity, data source and TTL. It must not receive production protected secrets or broad network access. Stop job requests cleanup; independent reconciler verifies absence.

```bash
kubectl get namespace "review-$CI_MERGE_REQUEST_IID" -o json
```

NotFound after verified target/context supports namespace cleanup. It does not prove cloud DNS, databases, buckets or IAM identities were removed.

## 10. GitLab Release

GitLab Release attaches metadata to tag: name, description, milestones, evidence/assets and links. It should reference immutable release manifest and durable registry/package assets.

```bash
curl --fail --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "$GITLAB_URL/api/v4/projects/481/releases/10.0.0" \
  | jq '{tag_name,name,released_at,commit,assets,evidences}'
```

Output proves GitLab Release representation. It does not prove tag immutability, artifact bytes, deployment or support state. Release manifest remains authority.

## 11. Environment stop and cleanup

Environment `on_stop` job can set environment state to stopped. Cleanup may fail or be partial. Resources carry environment/deployment ownership labels and TTL; sweeper inventories leftovers.

```text
stop requested
→ delete/reconcile workload, DNS, identity, storage and data resources
→ read-back absence
→ mark cleanup complete
→ environment record stopped
```

Ordering matters: marking stopped before cleanup creates false-green lifecycle.

## 12. Connected incident `GL-PAY-74`

Atlas deployment job created GitOps promotion PR and immediately exited success. GitLab recorded deployment `success` and Release `10.0.0-rc.4` linked expiring job artifact. Flux reconciliation failed because target namespace had admission policy mismatch. Production continued old digest while GitLab environment UI showed new release.

Review app stop job later marked environment stopped after deleting namespace, but DNS, database and cloud role remained. Security team assumed release fixed a vulnerability because default branch and GitLab Release pointed to new tag; production still ran vulnerable digest.

```text
GitOps request success
→ GitLab deployment success
→ controller failure
→ runtime old artifact
+ release metadata new artifact
→ false remediation closure
```

Root cause was deployment/release-to-runtime correlation and cleanup semantics.

## 13. Containment, recovery and acceptance

Containment freezes promotions, preserves GitLab/controller/runtime records and inventories actual digests/resources. Recovery fixes admission/config, reconciles exact manifest, updates deployment status after business acceptance and cleans orphan review resources.

Environment/deployment/release model is accepted only when:

```text
environment identity and generation are exact
+ deployment is bound to release manifest/artifact digest
+ concurrency/stale-plan protection exists
+ approval and credentials match target subject
+ direct/GitOps request state is distinguished from convergence
+ runtime digest/config/traffic/business read-back completes verdict
+ GitLab Release links durable immutable assets
+ stop state follows actual cleanup read-back
+ forbidden false-success controller failure is tested
+ second deployment/review-app cleanup operation passes
```

## 14. Troubleshooting flow

False-green deployment sa rieši koreláciou jednej operation identity naprieč GitLab recordom, deploy jobom, external controllerom a runtime workloadom. Každý krok odpovedá na inú otázku: čo bolo požadované, čo bolo prijaté, čo sa convergovalo a čo reálne obsluhuje traffic. Až business probe uzatvára pôvodný outcome.

```text
GitLab environment/deployment/release records
→ pipeline/job/ref/artifact subject
→ protected environment and identity
→ deployment request
→ external controller desired/observed state
→ live/runtime digest/config
→ traffic/business outcome
→ cleanup/support state
```

Competing hypotheses include stale job, wrong environment name, failed controller, partial apply, wrong digest, feature mismatch, outdated deployment, release metadata drift or orphan cleanup.

## 15. Anti-patterny

### Deployment job success equals production success

Successful deploy job môže dokazovať iba API acknowledgement alebo Git commit. Controller môže neskôr zlyhať, rollout zostať partial alebo traffic smerovať na starú cohort. Production verdict potrebuje controller observed state, runtime digest/config read-back a business acceptance.

### GitLab environment name as exact target identity

Rovnaký environment name môže po migrácii ukazovať na iný cluster, namespace, account alebo policy generation. Name preto zostáva locatorom a approval inputom, kým exact subject pridáva target IDs a generation. Deploy script aj read-back musia používať ten istý target envelope.

### Release linked to expiring artifact

Release asset URL na job artifact môže expirovať alebo zmeniť access semantics počas support window-u. GitLab Release má odkazovať na immutable durable registry/package subject a release manifest. Pipeline artifact zostáva doplnkovou execution evidence, nie jediným distribučným zdrojom.

### Environment stopped before cleanup proof

Environment record môže byť označený `stopped` skôr, než sa odstránia DNS, IAM, storage, database alebo workload resources. Taký status vytvorí false-green lifecycle a orphan cost/security exposure. Cleanup closure vyžaduje independent inventory a read-back absencie pred finálnym stavom.

### Fixed branch equals fixed production

Fix na default branchi mení source subject, nie automaticky deployed artifact ani runtime. Build, scan, promotion, controller convergence a workload replacement môžu stále chýbať. Remediation sa uzatvára až keď production image/config identity zodpovedá fixed release manifestu a vulnerable cohort je odstránená.

## 16. Kontrolné otázky

1. How environment, deployment and Release differ?
2. What forms exact deployment subject?
3. What deployment API proves?
4. How direct and GitOps deployments differ?
5. Why resource group does not fully prevent stale deploy?
6. How runtime read-back closes deployment?
7. What GitLab Release does and does not prove?
8. How review-app cleanup is verified?
9. What happened in `GL-PAY-74`?
10. Why security remediation was falsely closed?
11. How deployment status should be updated from external controller?
12. What second-operation validation is required?

## Glossary impact

Relevantné pojmy: GitLab environment, environment generation, deployment record, deployable job, deployment tier, resource group, outdated deployment, GitOps deployment request, controller convergence, runtime correlation, review app, stop job, cleanup reconciliation, GitLab Release and release asset.

## Primárne zdroje

- [GitLab Docs — Environments and deployments](https://docs.gitlab.com/ci/environments/)
- [GitLab API — Deployments](https://docs.gitlab.com/api/deployments/)
- [GitLab Docs — Resource groups](https://docs.gitlab.com/ci/resource_groups/)
- [GitLab Docs — Review apps](https://docs.gitlab.com/ci/review_apps/)
- [GitLab Docs — Releases](https://docs.gitlab.com/user/project/releases/)
- [GitLab API — Releases](https://docs.gitlab.com/api/releases/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Container a package registry](container-and-package-registry.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Security scanning →](security-scanning.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
