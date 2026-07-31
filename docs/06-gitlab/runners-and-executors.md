# Runners a executors

GitLab Runner je privilegovaná execution boundary. Pipeline job nie je abstraktný command: GitLab scheduler ho priradí konkrétnemu runnerovi alebo poolu, executor vytvorí process/container/VM/Pod context, runner vloží source, artifacts, cache a credentials, job vykoná arbitrary code a po skončení musí runtime aj external resources bezpečne odstrániť.

Runner nie je executor. Runner je agent a scheduling/credential boundary; executor určuje, ako job beží. Docker executor môže byť rootful, privileged a s mounted Docker socketom, alebo bounded rootless setup. Kubernetes executor môže vytvoriť ephemeral Pod, no stále zdieľa cluster control plane, nodes a network. Shell executor spúšťa code priamo na hoste a má najslabšiu default isolation.

## 1. Dominantný job-to-cleanup model

```text
pipeline job a trust context
→ runner scope/tags/protected eligibility
→ scheduler selection and concurrency
→ executor runtime creation
→ source/artifact/cache injection
→ short-lived identity and network policy
→ arbitrary job execution
→ output/side-effect acknowledgement
→ runtime teardown and credential revocation
→ independent residual-resource cleanup
```

Successful job status nepreukazuje clean runner. Persistent workspace, process, container, Docker layer, cache, cloud resource alebo credential môže prežiť.

## 2. Exact runner execution subject

```yaml
runnerExecutionSubject:
  gitlabInstance: gitlab.atlas.example
  runnerId: 184
  runnerManagerSystemId: r_8f210a
  runnerVersion: 18.2.0
  scope: group/atlas-payments
  protected: true
  tags: [trusted-build, linux-amd64]
  executor: docker-autoscaler
  executorGeneration: runner-image-sha256-build420
  job:
    projectId: 481
    pipelineId: 771184
    jobId: 881911
    candidateSha: d94e1c6
    trustClass: protected-main
  networkPolicySha: runner-egress-31
  credentialPolicySha: oidc-payments-build-44
```

Runner ID samostatne nestačí pri autoscaling managers. Runtime image, host/VM generation a job trust class menia evidence aj blast radius.

## 3. Runner scope a tags

Instance, group a project runner scopes určujú, ktoré projects môžu job priradiť. Broad instance runner s privileged executorom vytvára large multi-tenant trust boundary. Tags sú selection constraints, nie security proof, pokiaľ untrusted project/job môže rovnaký tag použiť a runner nie je protected/scoped.

Protected runner má byť eligible iba pre protected refs/jobs podľa current GitLab semantics. To stále nepreukazuje, že protected source nemôže obsahovať untrusted code po stale approval alebo direct push bypass-e.

Runner API/inventory:

```bash
curl --fail --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "$GITLAB_URL/api/v4/runners/184" \
  | jq '{id,description,runner_type,active,paused,is_shared,run_untagged,protected,tag_list,version,revision,platform,architecture,maximum_timeout}'
```

Output preukazuje GitLab API metadata. Nepreukazuje host hardening, executor configuration, mounts, network, local credentials alebo residual state. Runner configuration a runtime inspection dopĺňajú evidence.

## 4. Executor comparison

**Shell executor** spúšťa job na host OS. Workspace, users, processes a host secrets potrebujú explicitnú isolation; vhodný je iba pre trusted code na dedicated ephemeral hoste alebo narrow use.

**Docker executor** vytvára container. Container nie je VM boundary. Privileged mode, host mounts, device access alebo Docker socket umožňujú host takeover.

**Kubernetes executor** vytvára Pod. Security závisí od service account, namespace, Pod security, node isolation, network policy, volumes a cluster multi-tenancy.

**Autoscaling/instance executors** môžu vytvoriť ephemeral VM pre job alebo limited reuse. Potrebujú image lifecycle, pool hygiene, scale controls a cleanup.

Choice sa riadi trust class, required kernel/device access, performance, cost a operational complexity.

## 5. Ephemeral versus persistent

Ephemeral runtime znižuje cross-job contamination. Musí však byť naozaj disposed po jobe, nie iba container replaced na persistent hoste s shared Docker cache a credentials.

```text
one job
→ fresh VM/Pod/workspace
→ bounded identity
→ execution
→ destroy runtime
→ external resource reconciliation
```

Persistent runners potrebujú workspace cleanup, process kill, container/network removal, secret deletion, patching a periodic reimage. Cold-canary jobs môžu overovať, že build correctness nezávisí od residual state.

## 6. Runtime inspection

Job môže zachytiť bounded runtime facts:

```bash
printf 'host=%s\n' "$(hostname)"
uname -srmo
id
cat /proc/self/cgroup
mount | sed -n '1,30p'
ip route
```

Output pomáha identifikovať kernel, identity, cgroup, mounts a route. Nepreukazuje absence privileged syscalls, metadata access alebo other tenants. Security acceptance používa configuration policy a forbidden capability probes.

## 7. Privileged build patterns

Mounting `/var/run/docker.sock` dáva jobu control nad host Docker daemon a prakticky host-level capability. Docker-in-Docker privileged mode má podobný high-risk boundary. Safer alternatives zahŕňajú rootless BuildKit, remote dedicated builder, Kaniko-like userspace build podľa current support, alebo build service s immutable request/response contractom.

```text
untrusted source
→ no host socket/device
→ remote trusted builder gets immutable candidate and build definition
→ returns digest/provenance
```

Remote builder stále potrebuje source trust, cache isolation, secret mounts a provenance.

## 8. Resource limits a overload

Runner concurrency, CPU/memory/storage, ephemeral disk, network a external quotas musia byť bounded. Job bez limitu môže evictovať other jobs alebo exhaust node disk. Autoscaling má queue/saturation signals a cost guardrails.

Kubernetes job resources:

```yaml
runners:
  config: |
    [[runners]]
      executor = "kubernetes"
      [runners.kubernetes]
        cpu_request = "1"
        cpu_limit = "2"
        memory_request = "2Gi"
        memory_limit = "4Gi"
        helper_cpu_limit = "500m"
```

Configuration preukazuje intended defaults. Nepreukazuje loaded Runner config alebo per-job overwrite. Runtime Pod spec a cgroup metrics sa read-backnú.

## 9. Workload identity

Static cloud keys na runner hoste alebo shared variables vytvárajú reusable capabilities. GitLab ID token umožňuje short-lived federation. External trust policy má bound claims ako issuer, audience, project path/ID, ref protection, environment a job context.

```bash
aws sts get-caller-identity --output json | jq '{Account,Arn}'
```

Output preukazuje current AWS principal. Nepreukazuje why trust policy issued session alebo complete permissions. Cloud audit log a token claims correlation dopĺňajú evidence.

## 10. Network a metadata boundaries

Runner egress má allowlist podľa job purpose. Untrusted job nemá pristupovať production APIs, cloud instance metadata, internal admin endpoints alebo shared caches. NetworkPolicy pri Kubernetes executorovi potrebuje DNS, registry a artifact endpoints, no default allow-all znižuje isolation.

Metadata service access môže získať node role aj keď Pod service account je bounded. Cloud/node design musí blokovať unintended IMDS path.

## 11. Cache, artifacts a helper images

Runner helper image a artifact/cache transport sú part execution subjectu. Mutable helper image alebo misconfigured object-store credentials môžu meniť behavior. Cache namespaces musia rešpektovať trust direction.

Artifacts z untrusted jobu sú untrusted data. Privileged downstream job validuje schema/digest a nesmie extractnúť archive s path traversal alebo vykonať embedded scripts.

## 12. Cancellation a cleanup

Cancel signal nemusí okamžite zastaviť child process alebo external operation. Job môže skončiť canceled, ale build push alebo deployment pokračovať. Scripts používajú traps a idempotency/read-back; independent reconciler čistí resources podľa job labels/TTL.

```text
job canceled
→ runner sends signal
→ process may ignore/delay
→ external side effect may complete
→ cleanup/reconciliation verifies outcome
```

## 13. Connected incident `GL-PAY-73`

Atlas protected group runner používal shell executor na persistent VM. `run_untagged=true` a group scope umožnil job z transferred experiment projectu. Mutable CI include pridalo tagless build job, ktorý restore-ol shared cache a našiel Docker config s registry write tokenom. Host mal production kubeconfig pre legacy deploy job.

```text
untrusted project inherited group runner
→ shell executor persistent workspace
→ residual registry credential + kubeconfig
→ artifact publication and production mutation capability
```

Job publikoval poisoned image pod candidate tag a patchol production ConfigMap. GitLab job nemal environment declaration, takže protected environment controls sa neuplatnili.

Root cause bol runner scope/persistence a residual capability, nie iba malicious script.

## 14. Containment, recovery a acceptance

Containment pause-ne runner, revoke-ne host/registry/cloud credentials, snapshot-ne evidence a inventory artifacts/deployments. Recovery reimage-ne host, oddeli untrusted/protected pools, zavedie ephemeral executors a federation a rebuild-ne affected artifacts.

Runner model je prijatý iba vtedy, keď:

```text
runner scope/tags/protected status match trust class
+ executor isolation and runtime image are exact
+ untrusted jobs have no host socket/production network
+ workspace/cache/credentials cannot cross trust boundary
+ resources/concurrency are bounded
+ workload identity is short-lived and claim-scoped
+ cancellation/unknown effects have reconciliation
+ runtime teardown and external cleanup are read-backnuté
+ forbidden untrusted-to-production capability is tested
+ second cold job proves no residual correctness dependency
```

## 15. Troubleshooting flow

```text
job/pipeline trust subject
→ runner selection and tags
→ runner manager/executor generation
→ workspace/mount/cache state
→ credentials and network
→ process/external side effects
→ cancellation/teardown
→ residual resources
```

Competing hypotheses môžu byť wrong runner scope, untagged eligibility, privileged mount, stale workspace, shared cache, node metadata, broad ID-token trust, canceled process or cleanup failure.

## 16. Anti-patterny

### Container executor equals secure isolation

Privilege, mounts and shared kernel can still expose host.

### Protected runner equals trusted code

Stale approvals/direct push can place untrusted code on protected refs.

### Shared shell runner

Persistent host state and arbitrary code create cross-project compromise.

### Static cloud credentials on runner

Capability survives jobs and weakens attribution/revocation.

### Job success equals cleanup success

External resources and credentials can remain.

## 17. Kontrolné otázky

1. Aký je rozdiel medzi Runnerom a executorom?
2. Čo tvorí exact runner execution subject?
3. Prečo tags samy nie sú security boundary?
4. Aké risks má shell executor?
5. Prečo Docker socket znamená host capability?
6. Ako ephemeral runner znižuje cross-job state?
7. Čo preukazuje runtime inspection a čo nie?
8. Ako ID token mení credential lifecycle?
9. Čo sa stalo v `GL-PAY-73`?
10. Ako sa rieši canceled external operation?
11. Ako sa testuje forbidden production access?
12. Čo musí preukázať cold second job?

## Glossary impact

Relevantné pojmy: GitLab Runner, runner manager, runner scope, protected runner, runner tags, executor, shell executor, Docker executor, Kubernetes executor, autoscaling executor, ephemeral runner, persistent workspace, privileged build, helper image, workload identity, runner cleanup a residual state.

## Primárne zdroje

- [GitLab Runner documentation](https://docs.gitlab.com/runner/)
- [GitLab Runner executors](https://docs.gitlab.com/runner/executors/)
- [GitLab Docs — Runners](https://docs.gitlab.com/ci/runners/)
- [GitLab Runner — Docker executor](https://docs.gitlab.com/runner/executors/docker/)
- [GitLab Runner — Kubernetes executor](https://docs.gitlab.com/runner/executors/kubernetes/)
- [GitLab Docs — ID token authentication](https://docs.gitlab.com/ci/secrets/id_token_authentication/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: GitLab CI/CD syntax](gitlab-ci-cd-syntax.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Variables a secrets →](variables-and-secrets.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
