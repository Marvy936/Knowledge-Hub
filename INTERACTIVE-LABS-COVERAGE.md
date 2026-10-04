# Interactive Labs Coverage Ledger

This is the authoritative per-document practical coverage baseline for documentation sections `00–18`.

**Baseline rule:** `covered` is intentionally conservative. Manual CKA/AWS exercises and Practical v1 tracks are shown as supplemental evidence only; they do not satisfy the interactive-lab gate.

## Baseline summary

- Total documentation topics: **377**
- Covered: **28**
- Partial: **42**
- Planned: **307**
- Not applicable: **0**

| Section | Documentation topic | State | Interactive lab(s) | Supplemental | Coverage note |
|---|---|---|---|---|---|
| 00-foundations | [automation-mindset](docs/00-foundations/automation-mindset.md) | `covered` | `foundations-reconciliation-idempotency` | — | Exercises typed input, bounded mutation, authoritative state, verification, recovery and replay semantics. |
| 00-foundations | [calms](docs/00-foundations/calms.md) | `planned` | — | — | Interactive backfill required. |
| 00-foundations | [continuous-improvement](docs/00-foundations/continuous-improvement.md) | `covered` | `foundations-ownership-improvement-integrity` | — | Requires a baseline, falsifiable hypothesis, guardrails, owned action, full evaluation window, effectiveness review and institutionalized learning. |
| 00-foundations | [declarative-vs-imperative](docs/00-foundations/declarative-vs-imperative.md) | `covered` | `foundations-reconciliation-idempotency` | — | Contrasts blind create sequencing with desired-state reconciliation over authoritative observed state. |
| 00-foundations | [desired-state-and-reconciliation](docs/00-foundations/desired-state-and-reconciliation.md) | `covered` | `foundations-reconciliation-idempotency` | — | Recomputes desired vs observed state, reconciles partial state and verifies effective runtime convergence. |
| 00-foundations | [devops](docs/00-foundations/devops.md) | `planned` | — | — | Interactive backfill required. |
| 00-foundations | [devops-anti-patterns](docs/00-foundations/devops-anti-patterns.md) | `planned` | — | — | Interactive backfill required. |
| 00-foundations | [devops-lifecycle](docs/00-foundations/devops-lifecycle.md) | `partial` | `foundations-delivery-flow-dora` | — | Traces one bounded source→production→recovery delivery slice; broader lifecycle ownership and operating model remain planned. |
| 00-foundations | [dora-metrics](docs/00-foundations/dora-metrics.md) | `covered` | `foundations-delivery-flow-dora` | — | Recomputes deployment frequency, lead time for changes, change failure rate and time to restore from authoritative production events with explicit windows and denominators. |
| 00-foundations | [feedback-loops](docs/00-foundations/feedback-loops.md) | `covered` | `foundations-feedback-system-dynamics` | — | Closes an end-to-end feedback loop across authoritative observation, target comparison, decision authority, bounded correction, propagation delay and global outcome verification. |
| 00-foundations | [idempotency](docs/00-foundations/idempotency.md) | `covered` | `foundations-reconciliation-idempotency` | — | Requires stable operation/resource identity, read-before-retry and duplicate-free identical replay. |
| 00-foundations | [immutable-vs-mutable-infrastructure](docs/00-foundations/immutable-vs-mutable-infrastructure.md) | `partial` | `foundations-reconciliation-idempotency` | — | Requires a digest-pinned artifact and rejects mutable references; full replacement/traffic-cutover lifecycle remains planned. |
| 00-foundations | [ownership-mindset](docs/00-foundations/ownership-mindset.md) | `covered` | `foundations-ownership-improvement-integrity` | — | Binds a service outcome to an explicit owner, bounded decision rights, direct runtime evidence, escalation, collective recovery capability and verified follow-up. |
| 00-foundations | [sdlc](docs/00-foundations/sdlc.md) | `partial` | `foundations-delivery-flow-dora` | — | Exercises traceability from source change through production exposure and recovery; discovery, design, maintenance and retirement remain outside this lab. |
| 00-foundations | [systems-thinking](docs/00-foundations/systems-thinking.md) | `covered` | `foundations-feedback-system-dynamics` | — | Requires an explicit end-to-end system boundary, distinguishes local from global optimization, identifies the real downstream constraint, models queue stock and retry amplification, and verifies the global outcome. |
| 00-foundations | [t-shaped-engineer](docs/00-foundations/t-shaped-engineer.md) | `planned` | — | — | Interactive backfill required. |
| 00-foundations | [three-ways](docs/00-foundations/three-ways.md) | `covered` | `foundations-delivery-flow-dora`, `foundations-feedback-system-dynamics`, `foundations-ownership-improvement-integrity` | — | Exercises First-Way flow, Second-Way closed feedback and Third-Way verified institutional learning across the three Foundations labs. |
| 00-foundations | [toil-and-technical-debt](docs/00-foundations/toil-and-technical-debt.md) | `covered` | `foundations-ownership-improvement-integrity` | — | Distinguishes recurring automatable toil from the underlying debt mechanism and requires debt owner, risk, interest metric, review date, exit condition and effectiveness-based closure. |
| 00-foundations | [value-stream-mapping](docs/00-foundations/value-stream-mapping.md) | `covered` | `foundations-delivery-flow-dora` | — | Reconstructs active vs wait time, process efficiency and the true queue bottleneck instead of optimizing the most visible active-work stage. |
| 00-foundations | [you-build-it-you-run-it](docs/00-foundations/you-build-it-you-run-it.md) | `covered` | `foundations-ownership-improvement-integrity` | — | Keeps primary service incident ownership with the team that builds the service while preserving a bounded platform escalation interface and shared operational capability. |
| 01-linux-and-systems | [cgroups](docs/01-linux-and-systems/cgroups.md) | `covered` | `linux-isolation-integrity` | — | Requires exact cgroup v2 placement plus effective CPU, memory and PIDs limits, runtime usage below those limits and zero unexpected OOM events. |
| 01-linux-and-systems | [cpu-and-memory-fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md) | `planned` | — | — | Interactive backfill required. |
| 01-linux-and-systems | [cron-and-systemd-timers](docs/01-linux-and-systems/cron-and-systemd-timers.md) | `partial` | `linux-storage-service-scheduler-integrity` | — | Exercises systemd timer schedule, persistence, trigger/service separation and durable outcome verification; cron-specific execution/environment semantics remain planned. |
| 01-linux-and-systems | [environment-variables](docs/01-linux-and-systems/environment-variables.md) | `planned` | — | — | Interactive backfill required. |
| 01-linux-and-systems | [filesystem-hierarchy-inodes-links](docs/01-linux-and-systems/filesystem-hierarchy-inodes-links.md) | `partial` | `linux-storage-service-scheduler-integrity` | — | Exercises pathname→mount identity, inode/link identity, dangling symlink and deleted-open inode lifetime; broader hierarchy and lookup/permission semantics remain planned. |
| 01-linux-and-systems | [journald-and-logging](docs/01-linux-and-systems/journald-and-logging.md) | `covered` | `linux-storage-service-scheduler-integrity` | — | Requires unit/run scoped journal evidence, boot identity, preserved failure class and positive completion event instead of treating missing logs as success. |
| 01-linux-and-systems | [kernel-and-user-space](docs/01-linux-and-systems/kernel-and-user-space.md) | `partial` | `linux-isolation-integrity` | — | Exercises the shared-kernel execution model and kernel-enforced namespace/cgroup/capability decisions; broader syscall, device, memory and module boundaries remain planned. |
| 01-linux-and-systems | [linux-capabilities](docs/01-linux-and-systems/linux-capabilities.md) | `covered` | `linux-isolation-integrity` | — | Validates post-exec effective/permitted/bounding/ambient sets, no_new_privs, one required privileged operation and denial of adjacent broad host-affecting operations. |
| 01-linux-and-systems | [linux-networking](docs/01-linux-and-systems/linux-networking.md) | `planned` | — | — | Interactive backfill required. |
| 01-linux-and-systems | [namespaces](docs/01-linux-and-systems/namespaces.md) | `covered` | `linux-isolation-integrity` | — | Compares host/workload namespace object identities across PID, mount, network, UTS, IPC and user namespaces and verifies namespace-root host UID mapping. |
| 01-linux-and-systems | [package-management](docs/01-linux-and-systems/package-management.md) | `planned` | — | — | Interactive backfill required. |
| 01-linux-and-systems | [performance-and-troubleshooting](docs/01-linux-and-systems/performance-and-troubleshooting.md) | `planned` | — | — | Interactive backfill required. |
| 01-linux-and-systems | [processes-threads-pid-signals](docs/01-linux-and-systems/processes-threads-pid-signals.md) | `partial` | `linux-process-signals` | — | Exercises process/signal propagation, not the full thread/PID lifecycle. |
| 01-linux-and-systems | [selinux-and-apparmor](docs/01-linux-and-systems/selinux-and-apparmor.md) | `planned` | — | — | Interactive backfill required. |
| 01-linux-and-systems | [shell-bash-pipes-redirection-exit-codes](docs/01-linux-and-systems/shell-bash-pipes-redirection-exit-codes.md) | `partial` | `bash-pipeline-failure` | — | Exercises pipeline exit propagation; redirection and broader shell semantics remain. |
| 01-linux-and-systems | [ssh](docs/01-linux-and-systems/ssh.md) | `planned` | — | — | Interactive backfill required. |
| 01-linux-and-systems | [storage-mounts-and-filesystems](docs/01-linux-and-systems/storage-mounts-and-filesystems.md) | `covered` | `linux-storage-service-scheduler-integrity` | — | Binds the backup path to the exact mount source/type/options, distinguishes df/du and inode/open-file causes, and verifies writable recovered storage before outcome acceptance. |
| 01-linux-and-systems | [systemd-services-daemons](docs/01-linux-and-systems/systemd-services-daemons.md) | `covered` | `linux-storage-service-scheduler-integrity` | — | Separates timer activation from oneshot service execution, verifies effective unit identity/result/cgroup cleanup and requires the service outcome rather than manager status alone. |
| 01-linux-and-systems | [users-groups-permissions-sudo-pam](docs/01-linux-and-systems/users-groups-permissions-sudo-pam.md) | `partial` | `linux-file-permissions` | — | Exercises Unix owner/group/mode semantics; sudo/PAM remain uncovered. |
| 02-networking-and-web | [dhcp](docs/02-networking-and-web/dhcp.md) | `planned` | — | — | Interactive backfill required. |
| 02-networking-and-web | [dns](docs/02-networking-and-web/dns.md) | `partial` | `docker-network-debug` | — | Exercises DNS/service discovery in Docker, not general DNS operation. |
| 02-networking-and-web | [ethernet-mac-arp](docs/02-networking-and-web/ethernet-mac-arp.md) | `planned` | — | — | Interactive backfill required. |
| 02-networking-and-web | [firewalls](docs/02-networking-and-web/firewalls.md) | `planned` | — | — | Interactive backfill required. |
| 02-networking-and-web | [http](docs/02-networking-and-web/http.md) | `planned` | — | — | Interactive backfill required. |
| 02-networking-and-web | [https-tls-certificates-pki](docs/02-networking-and-web/https-tls-certificates-pki.md) | `partial` | `tls-certificate-hostname` | — | Exercises SAN/hostname verification, not the complete PKI lifecycle. |
| 02-networking-and-web | [ipv4-ipv6-subnetting](docs/02-networking-and-web/ipv4-ipv6-subnetting.md) | `planned` | — | — | Interactive backfill required. |
| 02-networking-and-web | [load-balancing](docs/02-networking-and-web/load-balancing.md) | `planned` | — | — | Interactive backfill required. |
| 02-networking-and-web | [nat](docs/02-networking-and-web/nat.md) | `planned` | — | — | Interactive backfill required. |
| 02-networking-and-web | [network-troubleshooting](docs/02-networking-and-web/network-troubleshooting.md) | `partial` | `docker-network-debug` | — | One concrete DNS/service-discovery troubleshooting path. |
| 02-networking-and-web | [networking-practical-walkthrough](docs/02-networking-and-web/networking-practical-walkthrough.md) | `planned` | — | — | Interactive backfill required. |
| 02-networking-and-web | [osi-and-tcp-ip-model](docs/02-networking-and-web/osi-and-tcp-ip-model.md) | `planned` | — | — | Interactive backfill required. |
| 02-networking-and-web | [ports-and-sockets](docs/02-networking-and-web/ports-and-sockets.md) | `planned` | — | — | Interactive backfill required. |
| 02-networking-and-web | [proxy-and-reverse-proxy](docs/02-networking-and-web/proxy-and-reverse-proxy.md) | `partial` | `nginx-reverse-proxy` | — | Exercises reverse proxy behavior; forward proxy remains uncovered. |
| 02-networking-and-web | [rest-apis-and-websockets](docs/02-networking-and-web/rest-apis-and-websockets.md) | `planned` | — | — | Interactive backfill required. |
| 02-networking-and-web | [routing-and-default-gateway](docs/02-networking-and-web/routing-and-default-gateway.md) | `planned` | — | — | Interactive backfill required. |
| 02-networking-and-web | [tcp-and-udp](docs/02-networking-and-web/tcp-and-udp.md) | `planned` | — | — | Interactive backfill required. |
| 03-git-and-automation | [bash-automation](docs/03-git-and-automation/bash-automation.md) | `partial` | `bash-pipeline-failure` | — | Exercises failure-safe Bash automation, not the whole automation topic. |
| 03-git-and-automation | [branching-strategies](docs/03-git-and-automation/branching-strategies.md) | `planned` | — | — | Interactive backfill required. |
| 03-git-and-automation | [cherry-pick-and-stash](docs/03-git-and-automation/cherry-pick-and-stash.md) | `planned` | — | — | Interactive backfill required. |
| 03-git-and-automation | [clone-fetch-pull-push](docs/03-git-and-automation/clone-fetch-pull-push.md) | `planned` | — | — | Interactive backfill required. |
| 03-git-and-automation | [commit-branch-tag-head](docs/03-git-and-automation/commit-branch-tag-head.md) | `planned` | — | — | Interactive backfill required. |
| 03-git-and-automation | [git-automation-practical-walkthrough](docs/03-git-and-automation/git-automation-practical-walkthrough.md) | `planned` | — | — | Interactive backfill required. |
| 03-git-and-automation | [git-object-model](docs/03-git-and-automation/git-object-model.md) | `planned` | — | — | Interactive backfill required. |
| 03-git-and-automation | [merge-and-rebase](docs/03-git-and-automation/merge-and-rebase.md) | `partial` | `git-three-way-merge` | — | Exercises merge mechanics; rebase remains uncovered. |
| 03-git-and-automation | [merge-conflicts](docs/03-git-and-automation/merge-conflicts.md) | `covered` | `git-three-way-merge` | — | Real three-way conflict resolution and validation. |
| 03-git-and-automation | [monorepo-vs-multirepo](docs/03-git-and-automation/monorepo-vs-multirepo.md) | `planned` | — | — | Interactive backfill required. |
| 03-git-and-automation | [powershell-fundamentals](docs/03-git-and-automation/powershell-fundamentals.md) | `planned` | — | — | Interactive backfill required. |
| 03-git-and-automation | [python-for-automation](docs/03-git-and-automation/python-for-automation.md) | `planned` | — | — | Interactive backfill required. |
| 03-git-and-automation | [reset-revert-restore](docs/03-git-and-automation/reset-revert-restore.md) | `planned` | — | — | Interactive backfill required. |
| 03-git-and-automation | [working-tree-staging-repository](docs/03-git-and-automation/working-tree-staging-repository.md) | `planned` | — | — | Interactive backfill required. |
| 03-git-and-automation | [yaml-json-regular-expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md) | `planned` | — | — | Interactive backfill required. |
| 04-testing-and-quality | [chaos-testing](docs/04-testing-and-quality/chaos-testing.md) | `planned` | — | — | Interactive backfill required. |
| 04-testing-and-quality | [code-coverage-and-quality-gates](docs/04-testing-and-quality/code-coverage-and-quality-gates.md) | `planned` | — | — | Interactive backfill required. |
| 04-testing-and-quality | [contract-and-api-tests](docs/04-testing-and-quality/contract-and-api-tests.md) | `planned` | — | — | Interactive backfill required. |
| 04-testing-and-quality | [end-to-end-and-acceptance-tests](docs/04-testing-and-quality/end-to-end-and-acceptance-tests.md) | `planned` | — | — | Interactive backfill required. |
| 04-testing-and-quality | [flaky-tests-and-test-data](docs/04-testing-and-quality/flaky-tests-and-test-data.md) | `planned` | — | — | Interactive backfill required. |
| 04-testing-and-quality | [mocks-stubs-fakes](docs/04-testing-and-quality/mocks-stubs-fakes.md) | `planned` | — | — | Interactive backfill required. |
| 04-testing-and-quality | [performance-load-stress-tests](docs/04-testing-and-quality/performance-load-stress-tests.md) | `planned` | — | — | Interactive backfill required. |
| 04-testing-and-quality | [security-and-infrastructure-tests](docs/04-testing-and-quality/security-and-infrastructure-tests.md) | `planned` | — | — | Interactive backfill required. |
| 04-testing-and-quality | [shift-left](docs/04-testing-and-quality/shift-left.md) | `planned` | — | — | Interactive backfill required. |
| 04-testing-and-quality | [shift-right](docs/04-testing-and-quality/shift-right.md) | `planned` | — | — | Interactive backfill required. |
| 04-testing-and-quality | [smoke-and-regression-tests](docs/04-testing-and-quality/smoke-and-regression-tests.md) | `planned` | — | — | Interactive backfill required. |
| 04-testing-and-quality | [static-analysis-linting-type-checking](docs/04-testing-and-quality/static-analysis-linting-type-checking.md) | `planned` | — | — | Interactive backfill required. |
| 04-testing-and-quality | [test-pyramid](docs/04-testing-and-quality/test-pyramid.md) | `planned` | — | — | Interactive backfill required. |
| 04-testing-and-quality | [unit-integration-component-tests](docs/04-testing-and-quality/unit-integration-component-tests.md) | `planned` | — | — | Interactive backfill required. |
| 04-testing-and-quality | [verification-vs-validation](docs/04-testing-and-quality/verification-vs-validation.md) | `planned` | — | — | Interactive backfill required. |
| 05-ci-cd-and-release | [a-b-testing](docs/05-ci-cd-and-release/a-b-testing.md) | `partial` | `mlops-ab-experiment-integrity` | — | Exercises controlled ML A/B experimentation; general application A/B delivery remains. |
| 05-ci-cd-and-release | [artifact-versioning](docs/05-ci-cd-and-release/artifact-versioning.md) | `planned` | — | — | Interactive backfill required. |
| 05-ci-cd-and-release | [blue-green-deployment](docs/05-ci-cd-and-release/blue-green-deployment.md) | `planned` | — | — | Interactive backfill required. |
| 05-ci-cd-and-release | [canary-deployment](docs/05-ci-cd-and-release/canary-deployment.md) | `partial` | `mlops-canary-rollback` | — | Model canary semantics exercise actual exposure and rollback, but not a general application delivery path. |
| 05-ci-cd-and-release | [ci-cd-practical-walkthrough](docs/05-ci-cd-and-release/ci-cd-practical-walkthrough.md) | `planned` | — | — | Interactive backfill required. |
| 05-ci-cd-and-release | [continuous-delivery](docs/05-ci-cd-and-release/continuous-delivery.md) | `planned` | — | — | Interactive backfill required. |
| 05-ci-cd-and-release | [continuous-deployment](docs/05-ci-cd-and-release/continuous-deployment.md) | `planned` | — | — | Interactive backfill required. |
| 05-ci-cd-and-release | [continuous-integration](docs/05-ci-cd-and-release/continuous-integration.md) | `planned` | — | — | Interactive backfill required. |
| 05-ci-cd-and-release | [database-compatibility-during-deployment](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md) | `planned` | — | — | Interactive backfill required. |
| 05-ci-cd-and-release | [environment-and-promotion](docs/05-ci-cd-and-release/environment-and-promotion.md) | `partial` | `mlops-model-promotion` | — | Exercises promotion gates for models, not general environment promotion. |
| 05-ci-cd-and-release | [feature-flags](docs/05-ci-cd-and-release/feature-flags.md) | `planned` | — | — | Interactive backfill required. |
| 05-ci-cd-and-release | [pipeline-as-code](docs/05-ci-cd-and-release/pipeline-as-code.md) | `planned` | — | — | Interactive backfill required. |
| 05-ci-cd-and-release | [pipeline-stage-job-runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md) | `planned` | — | — | Interactive backfill required. |
| 05-ci-cd-and-release | [progressive-delivery](docs/05-ci-cd-and-release/progressive-delivery.md) | `planned` | — | — | Interactive backfill required. |
| 05-ci-cd-and-release | [quality-gates-and-approvals](docs/05-ci-cd-and-release/quality-gates-and-approvals.md) | `planned` | — | — | Interactive backfill required. |
| 05-ci-cd-and-release | [recreate-deployment](docs/05-ci-cd-and-release/recreate-deployment.md) | `planned` | — | — | Interactive backfill required. |
| 05-ci-cd-and-release | [release-management](docs/05-ci-cd-and-release/release-management.md) | `planned` | — | — | Interactive backfill required. |
| 05-ci-cd-and-release | [reusable-and-parallel-pipelines](docs/05-ci-cd-and-release/reusable-and-parallel-pipelines.md) | `planned` | — | — | Interactive backfill required. |
| 05-ci-cd-and-release | [ring-deployment](docs/05-ci-cd-and-release/ring-deployment.md) | `planned` | — | — | Interactive backfill required. |
| 05-ci-cd-and-release | [rollback-and-roll-forward](docs/05-ci-cd-and-release/rollback-and-roll-forward.md) | `partial` | `mlops-rollback-recovery-integrity` | — | Exercises rigorous rollback/recovery semantics in an ML serving context. |
| 05-ci-cd-and-release | [rolling-update](docs/05-ci-cd-and-release/rolling-update.md) | `planned` | — | — | Interactive backfill required. |
| 05-ci-cd-and-release | [semantic-versioning](docs/05-ci-cd-and-release/semantic-versioning.md) | `planned` | — | — | Interactive backfill required. |
| 05-ci-cd-and-release | [shadow-deployment](docs/05-ci-cd-and-release/shadow-deployment.md) | `planned` | — | — | Interactive backfill required. |
| 05-ci-cd-and-release | [trigger-artifact-cache](docs/05-ci-cd-and-release/trigger-artifact-cache.md) | `planned` | — | — | Interactive backfill required. |
| 06-gitlab | [artifacts-and-cache](docs/06-gitlab/artifacts-and-cache.md) | `planned` | — | — | Interactive backfill required. |
| 06-gitlab | [container-and-package-registry](docs/06-gitlab/container-and-package-registry.md) | `planned` | — | — | Interactive backfill required. |
| 06-gitlab | [environments-deployments-releases](docs/06-gitlab/environments-deployments-releases.md) | `planned` | — | — | Interactive backfill required. |
| 06-gitlab | [gitlab-ci-cd-syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md) | `planned` | — | — | Interactive backfill required. |
| 06-gitlab | [gitlab-pipeline-practical-walkthrough](docs/06-gitlab/gitlab-pipeline-practical-walkthrough.md) | `planned` | — | — | Interactive backfill required. |
| 06-gitlab | [gitlab-troubleshooting](docs/06-gitlab/gitlab-troubleshooting.md) | `planned` | — | — | Interactive backfill required. |
| 06-gitlab | [merge-requests-and-approvals](docs/06-gitlab/merge-requests-and-approvals.md) | `planned` | — | — | Interactive backfill required. |
| 06-gitlab | [projects-groups-permissions](docs/06-gitlab/projects-groups-permissions.md) | `planned` | — | — | Interactive backfill required. |
| 06-gitlab | [protected-branches-and-environments](docs/06-gitlab/protected-branches-and-environments.md) | `planned` | — | — | Interactive backfill required. |
| 06-gitlab | [runners-and-executors](docs/06-gitlab/runners-and-executors.md) | `planned` | — | — | Interactive backfill required. |
| 06-gitlab | [security-scanning](docs/06-gitlab/security-scanning.md) | `planned` | — | — | Interactive backfill required. |
| 06-gitlab | [variables-and-secrets](docs/06-gitlab/variables-and-secrets.md) | `planned` | — | — | Interactive backfill required. |
| 07-infrastructure-as-code-and-configuration-management | [ansible-architecture](docs/07-infrastructure-as-code-and-configuration-management/ansible-architecture.md) | `planned` | — | — | Interactive backfill required. |
| 07-infrastructure-as-code-and-configuration-management | [ansible-idempotency](docs/07-infrastructure-as-code-and-configuration-management/ansible-idempotency.md) | `covered` | `ansible-idempotency` | — | Proves an identical second run converges with changed=0. |
| 07-infrastructure-as-code-and-configuration-management | [ansible-practical-walkthrough](docs/07-infrastructure-as-code-and-configuration-management/ansible-practical-walkthrough.md) | `planned` | — | — | Interactive backfill required. |
| 07-infrastructure-as-code-and-configuration-management | [ansible-troubleshooting](docs/07-infrastructure-as-code-and-configuration-management/ansible-troubleshooting.md) | `planned` | — | — | Interactive backfill required. |
| 07-infrastructure-as-code-and-configuration-management | [drift](docs/07-infrastructure-as-code-and-configuration-management/drift.md) | `covered` | `terraform-state-drift` | — | Detects and reconciles real Terraform drift. |
| 07-infrastructure-as-code-and-configuration-management | [expressions-and-dependency-graph](docs/07-infrastructure-as-code-and-configuration-management/expressions-and-dependency-graph.md) | `planned` | — | — | Interactive backfill required. |
| 07-infrastructure-as-code-and-configuration-management | [handlers-loops-conditionals](docs/07-infrastructure-as-code-and-configuration-management/handlers-loops-conditionals.md) | `planned` | — | — | Interactive backfill required. |
| 07-infrastructure-as-code-and-configuration-management | [infrastructure-as-code-principles](docs/07-infrastructure-as-code-and-configuration-management/infrastructure-as-code-principles.md) | `planned` | — | — | Interactive backfill required. |
| 07-infrastructure-as-code-and-configuration-management | [inventory](docs/07-infrastructure-as-code-and-configuration-management/inventory.md) | `planned` | — | — | Interactive backfill required. |
| 07-infrastructure-as-code-and-configuration-management | [lifecycle-import-moved-blocks](docs/07-infrastructure-as-code-and-configuration-management/lifecycle-import-moved-blocks.md) | `planned` | — | — | Interactive backfill required. |
| 07-infrastructure-as-code-and-configuration-management | [modules](docs/07-infrastructure-as-code-and-configuration-management/modules.md) | `planned` | — | — | Interactive backfill required. |
| 07-infrastructure-as-code-and-configuration-management | [modules-tasks-plays-playbooks](docs/07-infrastructure-as-code-and-configuration-management/modules-tasks-plays-playbooks.md) | `partial` | `ansible-idempotency` | — | Uses real task/module/playbook execution but covers only a narrow boundary. |
| 07-infrastructure-as-code-and-configuration-management | [remote-backend-and-state-locking](docs/07-infrastructure-as-code-and-configuration-management/remote-backend-and-state-locking.md) | `planned` | — | — | Interactive backfill required. |
| 07-infrastructure-as-code-and-configuration-management | [roles-and-collections](docs/07-infrastructure-as-code-and-configuration-management/roles-and-collections.md) | `planned` | — | — | Interactive backfill required. |
| 07-infrastructure-as-code-and-configuration-management | [terraform-practical-walkthrough](docs/07-infrastructure-as-code-and-configuration-management/terraform-practical-walkthrough.md) | `planned` | — | — | Interactive backfill required. |
| 07-infrastructure-as-code-and-configuration-management | [terraform-providers-resources-data-sources](docs/07-infrastructure-as-code-and-configuration-management/terraform-providers-resources-data-sources.md) | `planned` | — | — | Interactive backfill required. |
| 07-infrastructure-as-code-and-configuration-management | [terraform-state](docs/07-infrastructure-as-code-and-configuration-management/terraform-state.md) | `partial` | `terraform-state-drift` | — | Uses Terraform state/read-back, but does not cover the complete state lifecycle. |
| 07-infrastructure-as-code-and-configuration-management | [terraform-testing-and-policy](docs/07-infrastructure-as-code-and-configuration-management/terraform-testing-and-policy.md) | `planned` | — | — | Interactive backfill required. |
| 07-infrastructure-as-code-and-configuration-management | [terraform-troubleshooting](docs/07-infrastructure-as-code-and-configuration-management/terraform-troubleshooting.md) | `planned` | — | — | Interactive backfill required. |
| 07-infrastructure-as-code-and-configuration-management | [terraform-vs-ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md) | `planned` | — | — | Interactive backfill required. |
| 07-infrastructure-as-code-and-configuration-management | [variables-facts-templates](docs/07-infrastructure-as-code-and-configuration-management/variables-facts-templates.md) | `planned` | — | — | Interactive backfill required. |
| 07-infrastructure-as-code-and-configuration-management | [variables-locals-outputs](docs/07-infrastructure-as-code-and-configuration-management/variables-locals-outputs.md) | `planned` | — | — | Interactive backfill required. |
| 07-infrastructure-as-code-and-configuration-management | [vault](docs/07-infrastructure-as-code-and-configuration-management/vault.md) | `planned` | — | — | Interactive backfill required. |
| 08-container-fundamentals-and-docker | [build-context-layer-cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md) | `planned` | — | — | Interactive backfill required. |
| 08-container-fundamentals-and-docker | [buildkit-buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md) | `planned` | — | — | Interactive backfill required. |
| 08-container-fundamentals-and-docker | [container-networking](docs/08-container-fundamentals-and-docker/container-networking.md) | `covered` | `docker-network-debug` | — | Exercises Docker service discovery/networking failure and repair. |
| 08-container-fundamentals-and-docker | [container-security](docs/08-container-fundamentals-and-docker/container-security.md) | `planned` | — | — | Interactive backfill required. |
| 08-container-fundamentals-and-docker | [container-storage](docs/08-container-fundamentals-and-docker/container-storage.md) | `partial` | `docker-volume-persistence` | — | Exercises persistent container storage via named volume. |
| 08-container-fundamentals-and-docker | [containers-vs-virtual-machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md) | `planned` | — | — | Interactive backfill required. |
| 08-container-fundamentals-and-docker | [docker-architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md) | `planned` | — | — | Interactive backfill required. |
| 08-container-fundamentals-and-docker | [docker-compose](docs/08-container-fundamentals-and-docker/docker-compose.md) | `planned` | — | — | Interactive backfill required. |
| 08-container-fundamentals-and-docker | [docker-networks-port-publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md) | `partial` | `docker-network-debug` | — | Exercises Docker networking; port publishing remains incomplete. |
| 08-container-fundamentals-and-docker | [docker-practical-walkthrough](docs/08-container-fundamentals-and-docker/docker-practical-walkthrough.md) | `planned` | — | — | Interactive backfill required. |
| 08-container-fundamentals-and-docker | [docker-troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md) | `partial` | `docker-network-debug` | — | One representative Docker troubleshooting incident. |
| 08-container-fundamentals-and-docker | [dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md) | `planned` | — | — | Interactive backfill required. |
| 08-container-fundamentals-and-docker | [environment-variables-health-checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md) | `planned` | — | — | Interactive backfill required. |
| 08-container-fundamentals-and-docker | [images-layers-copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md) | `planned` | — | — | Interactive backfill required. |
| 08-container-fundamentals-and-docker | [multi-stage-builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md) | `planned` | — | — | Interactive backfill required. |
| 08-container-fundamentals-and-docker | [namespaces-cgroups-capabilities](docs/08-container-fundamentals-and-docker/namespaces-cgroups-capabilities.md) | `planned` | — | — | Interactive backfill required. |
| 08-container-fundamentals-and-docker | [oci-image-runtime-standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md) | `planned` | — | — | Interactive backfill required. |
| 08-container-fundamentals-and-docker | [registries](docs/08-container-fundamentals-and-docker/registries.md) | `planned` | — | — | Interactive backfill required. |
| 08-container-fundamentals-and-docker | [volumes-bind-mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md) | `partial` | `docker-volume-persistence` | — | Named-volume persistence is covered; bind mounts remain incomplete. |
| 09-kubernetes | [api-object-model](docs/09-kubernetes/api-object-model.md) | `planned` | — | `labs/cka/README.md` | Interactive backfill required. |
| 09-kubernetes | [cluster-dns](docs/09-kubernetes/cluster-dns.md) | `planned` | — | `labs/cka/README.md` | Interactive backfill required. |
| 09-kubernetes | [cluster-installation-lifecycle](docs/09-kubernetes/cluster-installation-lifecycle.md) | `planned` | — | `labs/cka/README.md` | Interactive backfill required. |
| 09-kubernetes | [cni-networkpolicy](docs/09-kubernetes/cni-networkpolicy.md) | `planned` | — | `labs/cka/README.md` | Interactive backfill required. |
| 09-kubernetes | [configmap-secret](docs/09-kubernetes/configmap-secret.md) | `partial` | `kubernetes-configmap-rollout` | `labs/cka/README.md` | ConfigMap rollout is exercised; Secret semantics remain uncovered. |
| 09-kubernetes | [control-plane-components](docs/09-kubernetes/control-plane-components.md) | `planned` | — | `labs/cka/README.md` | Interactive backfill required. |
| 09-kubernetes | [daemonset](docs/09-kubernetes/daemonset.md) | `planned` | — | `labs/cka/README.md` | Interactive backfill required. |
| 09-kubernetes | [deployment](docs/09-kubernetes/deployment.md) | `partial` | `kubernetes-configmap-rollout` | `labs/cka/README.md` | Exercises Deployment rollout/read-back around config change. |
| 09-kubernetes | [desired-state-reconciliation-loops](docs/09-kubernetes/desired-state-reconciliation-loops.md) | `partial` | `kubernetes-configmap-rollout` | `labs/cka/README.md` | Exercises desired-state rollout behavior, not the complete controller model. |
| 09-kubernetes | [etcd-backup-restore](docs/09-kubernetes/etcd-backup-restore.md) | `planned` | — | `labs/cka/README.md` | Interactive backfill required. |
| 09-kubernetes | [hpa-autoscaling](docs/09-kubernetes/hpa-autoscaling.md) | `planned` | — | `labs/cka/README.md` | Interactive backfill required. |
| 09-kubernetes | [ingress-gateway-api](docs/09-kubernetes/ingress-gateway-api.md) | `planned` | — | `labs/cka/README.md` | Interactive backfill required. |
| 09-kubernetes | [job-cronjob](docs/09-kubernetes/job-cronjob.md) | `planned` | — | `labs/cka/README.md` | Interactive backfill required. |
| 09-kubernetes | [kubernetes-architecture](docs/09-kubernetes/kubernetes-architecture.md) | `planned` | — | `labs/cka/README.md` | Interactive backfill required. |
| 09-kubernetes | [kubernetes-practical-walkthrough](docs/09-kubernetes/kubernetes-practical-walkthrough.md) | `planned` | — | `labs/cka/README.md` | Interactive backfill required. |
| 09-kubernetes | [kubernetes-troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md) | `partial` | `kubernetes-configmap-rollout` | `labs/cka/README.md` | One bounded Kubernetes repair path. |
| 09-kubernetes | [logging-metrics-events](docs/09-kubernetes/logging-metrics-events.md) | `planned` | — | `labs/cka/README.md` | Interactive backfill required. |
| 09-kubernetes | [pod](docs/09-kubernetes/pod.md) | `planned` | — | `labs/cka/README.md` | Interactive backfill required. |
| 09-kubernetes | [probes](docs/09-kubernetes/probes.md) | `planned` | — | `labs/cka/README.md` | Interactive backfill required. |
| 09-kubernetes | [rbac](docs/09-kubernetes/rbac.md) | `planned` | — | `labs/cka/README.md` | Interactive backfill required. |
| 09-kubernetes | [replicaset](docs/09-kubernetes/replicaset.md) | `planned` | — | `labs/cka/README.md` | Interactive backfill required. |
| 09-kubernetes | [requests-limits-qos](docs/09-kubernetes/requests-limits-qos.md) | `planned` | — | `labs/cka/README.md` | Interactive backfill required. |
| 09-kubernetes | [resourcequota-limitrange](docs/09-kubernetes/resourcequota-limitrange.md) | `planned` | — | `labs/cka/README.md` | Interactive backfill required. |
| 09-kubernetes | [scheduling](docs/09-kubernetes/scheduling.md) | `planned` | — | `labs/cka/README.md` | Interactive backfill required. |
| 09-kubernetes | [securitycontext-pod-security](docs/09-kubernetes/securitycontext-pod-security.md) | `planned` | — | `labs/cka/README.md` | Interactive backfill required. |
| 09-kubernetes | [service-endpointslice](docs/09-kubernetes/service-endpointslice.md) | `planned` | — | `labs/cka/README.md` | Interactive backfill required. |
| 09-kubernetes | [serviceaccount](docs/09-kubernetes/serviceaccount.md) | `planned` | — | `labs/cka/README.md` | Interactive backfill required. |
| 09-kubernetes | [statefulset](docs/09-kubernetes/statefulset.md) | `planned` | — | `labs/cka/README.md` | Interactive backfill required. |
| 09-kubernetes | [taints-tolerations-affinity-topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md) | `planned` | — | `labs/cka/README.md` | Interactive backfill required. |
| 09-kubernetes | [upgrades](docs/09-kubernetes/upgrades.md) | `planned` | — | `labs/cka/README.md` | Interactive backfill required. |
| 09-kubernetes | [volumes-pv-pvc-storageclass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md) | `planned` | — | `labs/cka/README.md` | Interactive backfill required. |
| 09-kubernetes | [worker-node-components](docs/09-kubernetes/worker-node-components.md) | `planned` | — | `labs/cka/README.md` | Interactive backfill required. |
| 10-helm-and-cka | [chart-dependencies](docs/10-helm-and-cka/chart-dependencies.md) | `planned` | — | `labs/cka/README.md` | Interactive backfill required. |
| 10-helm-and-cka | [cka-timed-labs](docs/10-helm-and-cka/cka-timed-labs.md) | `planned` | — | `labs/cka/README.md` | Interactive backfill required. |
| 10-helm-and-cka | [cka-troubleshooting-drills](docs/10-helm-and-cka/cka-troubleshooting-drills.md) | `planned` | — | `labs/cka/README.md` | Interactive backfill required. |
| 10-helm-and-cka | [helm-chart-practical-walkthrough](docs/10-helm-and-cka/helm-chart-practical-walkthrough.md) | `planned` | — | `labs/cka/README.md` | Interactive backfill required. |
| 10-helm-and-cka | [helm-chart-template-values-release](docs/10-helm-and-cka/helm-chart-template-values-release.md) | `planned` | — | `labs/cka/README.md` | Interactive backfill required. |
| 10-helm-and-cka | [helm-testing-troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md) | `planned` | — | `labs/cka/README.md` | Interactive backfill required. |
| 10-helm-and-cka | [hooks](docs/10-helm-and-cka/hooks.md) | `planned` | — | `labs/cka/README.md` | Interactive backfill required. |
| 10-helm-and-cka | [named-templates](docs/10-helm-and-cka/named-templates.md) | `planned` | — | `labs/cka/README.md` | Interactive backfill required. |
| 10-helm-and-cka | [template-functions-pipelines](docs/10-helm-and-cka/template-functions-pipelines.md) | `planned` | — | `labs/cka/README.md` | Interactive backfill required. |
| 10-helm-and-cka | [upgrade-rollback](docs/10-helm-and-cka/upgrade-rollback.md) | `planned` | — | `labs/cka/README.md` | Interactive backfill required. |
| 11-cloud-and-aws | [aws-backup](docs/11-cloud-and-aws/aws-backup.md) | `planned` | — | `labs/aws-cloudops/README.md` | Interactive backfill required. |
| 11-cloud-and-aws | [aws-organizations-accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md) | `planned` | — | `labs/aws-cloudops/README.md` | Interactive backfill required. |
| 11-cloud-and-aws | [aws-practical-walkthrough](docs/11-cloud-and-aws/aws-practical-walkthrough.md) | `planned` | — | `labs/aws-cloudops/README.md` | Interactive backfill required. |
| 11-cloud-and-aws | [aws-troubleshooting](docs/11-cloud-and-aws/aws-troubleshooting.md) | `planned` | — | `labs/aws-cloudops/README.md` | Interactive backfill required. |
| 11-cloud-and-aws | [cloudops-domain-review-timed-reasoning](docs/11-cloud-and-aws/cloudops-domain-review-timed-reasoning.md) | `planned` | — | `labs/aws-cloudops/README.md` | Interactive backfill required. |
| 11-cloud-and-aws | [cloudops-engineer-associate-soa-c03](docs/11-cloud-and-aws/cloudops-engineer-associate-soa-c03.md) | `planned` | — | `labs/aws-cloudops/README.md` | Interactive backfill required. |
| 11-cloud-and-aws | [cloudops-hands-on-labs](docs/11-cloud-and-aws/cloudops-hands-on-labs.md) | `planned` | — | `labs/aws-cloudops/README.md` | Interactive backfill required. |
| 11-cloud-and-aws | [cloudops-troubleshooting-drills](docs/11-cloud-and-aws/cloudops-troubleshooting-drills.md) | `planned` | — | `labs/aws-cloudops/README.md` | Interactive backfill required. |
| 11-cloud-and-aws | [cloudwatch-cloudtrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md) | `planned` | — | `labs/aws-cloudops/README.md` | Interactive backfill required. |
| 11-cloud-and-aws | [cost-management-finops](docs/11-cloud-and-aws/cost-management-finops.md) | `planned` | — | `labs/aws-cloudops/README.md` | Interactive backfill required. |
| 11-cloud-and-aws | [ec2-auto-scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md) | `planned` | — | `labs/aws-cloudops/README.md` | Interactive backfill required. |
| 11-cloud-and-aws | [ecs-eks](docs/11-cloud-and-aws/ecs-eks.md) | `planned` | — | `labs/aws-cloudops/README.md` | Interactive backfill required. |
| 11-cloud-and-aws | [elastic-load-balancing](docs/11-cloud-and-aws/elastic-load-balancing.md) | `planned` | — | `labs/aws-cloudops/README.md` | Interactive backfill required. |
| 11-cloud-and-aws | [high-availability-disaster-recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md) | `planned` | — | `labs/aws-cloudops/README.md` | Interactive backfill required. |
| 11-cloud-and-aws | [iaas-paas-saas](docs/11-cloud-and-aws/iaas-paas-saas.md) | `planned` | — | `labs/aws-cloudops/README.md` | Interactive backfill required. |
| 11-cloud-and-aws | [iam](docs/11-cloud-and-aws/iam.md) | `planned` | — | `labs/aws-cloudops/README.md` | Interactive backfill required. |
| 11-cloud-and-aws | [internet-gateway-nat-gateway](docs/11-cloud-and-aws/internet-gateway-nat-gateway.md) | `planned` | — | `labs/aws-cloudops/README.md` | Interactive backfill required. |
| 11-cloud-and-aws | [kms-secrets-manager](docs/11-cloud-and-aws/kms-secrets-manager.md) | `planned` | — | `labs/aws-cloudops/README.md` | Interactive backfill required. |
| 11-cloud-and-aws | [lambda](docs/11-cloud-and-aws/lambda.md) | `planned` | — | `labs/aws-cloudops/README.md` | Interactive backfill required. |
| 11-cloud-and-aws | [public-private-hybrid-cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md) | `planned` | — | `labs/aws-cloudops/README.md` | Interactive backfill required. |
| 11-cloud-and-aws | [rds](docs/11-cloud-and-aws/rds.md) | `planned` | — | `labs/aws-cloudops/README.md` | Interactive backfill required. |
| 11-cloud-and-aws | [regions-availability-zones](docs/11-cloud-and-aws/regions-availability-zones.md) | `planned` | — | `labs/aws-cloudops/README.md` | Interactive backfill required. |
| 11-cloud-and-aws | [route53-cloudfront](docs/11-cloud-and-aws/route53-cloudfront.md) | `planned` | — | `labs/aws-cloudops/README.md` | Interactive backfill required. |
| 11-cloud-and-aws | [s3-ebs-efs](docs/11-cloud-and-aws/s3-ebs-efs.md) | `partial` | `s3-versioning-minio`, `localstack-s3-versioning` | `labs/aws-cloudops/README.md` | Exercises S3-compatible versioning; EBS/EFS and real AWS control-plane behavior remain. |
| 11-cloud-and-aws | [scalability-elasticity-fault-tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md) | `planned` | — | `labs/aws-cloudops/README.md` | Interactive backfill required. |
| 11-cloud-and-aws | [security-groups-network-acls](docs/11-cloud-and-aws/security-groups-network-acls.md) | `planned` | — | `labs/aws-cloudops/README.md` | Interactive backfill required. |
| 11-cloud-and-aws | [shared-responsibility-model](docs/11-cloud-and-aws/shared-responsibility-model.md) | `planned` | — | `labs/aws-cloudops/README.md` | Interactive backfill required. |
| 11-cloud-and-aws | [systems-manager](docs/11-cloud-and-aws/systems-manager.md) | `planned` | — | `labs/aws-cloudops/README.md` | Interactive backfill required. |
| 11-cloud-and-aws | [vpc-subnets-route-tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md) | `planned` | — | `labs/aws-cloudops/README.md` | Interactive backfill required. |
| 11-cloud-and-aws | [well-architected-framework](docs/11-cloud-and-aws/well-architected-framework.md) | `planned` | — | `labs/aws-cloudops/README.md` | Interactive backfill required. |
| 12-observability | [alert-design-alert-fatigue](docs/12-observability/alert-design-alert-fatigue.md) | `partial` | `prometheus-target-alert` | — | Exercises one alert path, not alert design/fatigue comprehensively. |
| 12-observability | [alertmanager](docs/12-observability/alertmanager.md) | `planned` | — | — | Interactive backfill required. |
| 12-observability | [cardinality](docs/12-observability/cardinality.md) | `planned` | — | — | Interactive backfill required. |
| 12-observability | [elasticsearch-opensearch](docs/12-observability/elasticsearch-opensearch.md) | `planned` | — | — | Interactive backfill required. |
| 12-observability | [fluent-bit](docs/12-observability/fluent-bit.md) | `planned` | — | — | Interactive backfill required. |
| 12-observability | [golden-signals](docs/12-observability/golden-signals.md) | `planned` | — | — | Interactive backfill required. |
| 12-observability | [grafana](docs/12-observability/grafana.md) | `planned` | — | — | Interactive backfill required. |
| 12-observability | [instrumentation-telemetry](docs/12-observability/instrumentation-telemetry.md) | `planned` | — | — | Interactive backfill required. |
| 12-observability | [jaeger-tempo](docs/12-observability/jaeger-tempo.md) | `planned` | — | — | Interactive backfill required. |
| 12-observability | [loki](docs/12-observability/loki.md) | `planned` | — | — | Interactive backfill required. |
| 12-observability | [metrics-logs-traces-events](docs/12-observability/metrics-logs-traces-events.md) | `planned` | — | — | Interactive backfill required. |
| 12-observability | [monitoring-vs-observability](docs/12-observability/monitoring-vs-observability.md) | `planned` | — | — | Interactive backfill required. |
| 12-observability | [opentelemetry](docs/12-observability/opentelemetry.md) | `planned` | — | — | Interactive backfill required. |
| 12-observability | [prometheus](docs/12-observability/prometheus.md) | `covered` | `prometheus-target-alert` | — | Repairs a real scrape target and verifies alert resolution. |
| 12-observability | [red-method](docs/12-observability/red-method.md) | `planned` | — | — | Interactive backfill required. |
| 12-observability | [use-method](docs/12-observability/use-method.md) | `planned` | — | — | Interactive backfill required. |
| 13-security-and-identity | [active-directory](docs/13-security-and-identity/active-directory.md) | `planned` | — | — | Interactive backfill required. |
| 13-security-and-identity | [authentication-authorization-auditing](docs/13-security-and-identity/authentication-authorization-auditing.md) | `partial` | `keycloak-service-account` | — | Exercises machine authentication/token validation; authorization/audit remain incomplete. |
| 13-security-and-identity | [cia-triad](docs/13-security-and-identity/cia-triad.md) | `planned` | — | — | Interactive backfill required. |
| 13-security-and-identity | [encryption-at-rest-and-in-transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md) | `partial` | `tls-certificate-hostname` | — | Exercises TLS hostname verification for data in transit. |
| 13-security-and-identity | [iam-rbac](docs/13-security-and-identity/iam-rbac.md) | `planned` | — | — | Interactive backfill required. |
| 13-security-and-identity | [image-signing](docs/13-security-and-identity/image-signing.md) | `planned` | — | — | Interactive backfill required. |
| 13-security-and-identity | [kerberos](docs/13-security-and-identity/kerberos.md) | `planned` | — | — | Interactive backfill required. |
| 13-security-and-identity | [ldap](docs/13-security-and-identity/ldap.md) | `planned` | — | — | Interactive backfill required. |
| 13-security-and-identity | [least-privilege](docs/13-security-and-identity/least-privilege.md) | `planned` | — | — | Interactive backfill required. |
| 13-security-and-identity | [oauth-2](docs/13-security-and-identity/oauth-2.md) | `partial` | `keycloak-service-account` | — | Exercises OAuth2 client credentials/service-account token flow. |
| 13-security-and-identity | [openid-connect](docs/13-security-and-identity/openid-connect.md) | `partial` | `keycloak-service-account` | — | Token validation touches OIDC identity concepts but not interactive OIDC flows. |
| 13-security-and-identity | [policy-as-code](docs/13-security-and-identity/policy-as-code.md) | `planned` | — | — | Interactive backfill required. |
| 13-security-and-identity | [saml](docs/13-security-and-identity/saml.md) | `planned` | — | — | Interactive backfill required. |
| 13-security-and-identity | [sbom](docs/13-security-and-identity/sbom.md) | `planned` | — | — | Interactive backfill required. |
| 13-security-and-identity | [secrets-management](docs/13-security-and-identity/secrets-management.md) | `planned` | — | — | Interactive backfill required. |
| 13-security-and-identity | [supply-chain-security](docs/13-security-and-identity/supply-chain-security.md) | `planned` | — | — | Interactive backfill required. |
| 13-security-and-identity | [threat-modeling](docs/13-security-and-identity/threat-modeling.md) | `planned` | — | — | Interactive backfill required. |
| 13-security-and-identity | [vulnerability-and-patch-management](docs/13-security-and-identity/vulnerability-and-patch-management.md) | `planned` | — | — | Interactive backfill required. |
| 13-security-and-identity | [zero-trust](docs/13-security-and-identity/zero-trust.md) | `planned` | — | — | Interactive backfill required. |
| 14-sre-and-operations | [backup-and-restore](docs/14-sre-and-operations/backup-and-restore.md) | `partial` | `postgres-backup-restore` | — | Exercises a concrete logical database restore, not general backup strategy/RPO. |
| 14-sre-and-operations | [blameless-postmortems](docs/14-sre-and-operations/blameless-postmortems.md) | `planned` | — | — | Interactive backfill required. |
| 14-sre-and-operations | [capacity-planning](docs/14-sre-and-operations/capacity-planning.md) | `planned` | — | — | Interactive backfill required. |
| 14-sre-and-operations | [chaos-engineering](docs/14-sre-and-operations/chaos-engineering.md) | `planned` | — | — | Interactive backfill required. |
| 14-sre-and-operations | [disaster-recovery](docs/14-sre-and-operations/disaster-recovery.md) | `planned` | — | — | Interactive backfill required. |
| 14-sre-and-operations | [error-budgets](docs/14-sre-and-operations/error-budgets.md) | `planned` | — | — | Interactive backfill required. |
| 14-sre-and-operations | [incident-management](docs/14-sre-and-operations/incident-management.md) | `planned` | — | — | Interactive backfill required. |
| 14-sre-and-operations | [on-call-and-escalation](docs/14-sre-and-operations/on-call-and-escalation.md) | `planned` | — | — | Interactive backfill required. |
| 14-sre-and-operations | [operational-readiness](docs/14-sre-and-operations/operational-readiness.md) | `planned` | — | — | Interactive backfill required. |
| 14-sre-and-operations | [reliability-availability-durability](docs/14-sre-and-operations/reliability-availability-durability.md) | `planned` | — | — | Interactive backfill required. |
| 14-sre-and-operations | [root-cause-analysis](docs/14-sre-and-operations/root-cause-analysis.md) | `planned` | — | — | Interactive backfill required. |
| 14-sre-and-operations | [rpo-and-rto](docs/14-sre-and-operations/rpo-and-rto.md) | `planned` | — | — | Interactive backfill required. |
| 14-sre-and-operations | [runbooks-and-playbooks](docs/14-sre-and-operations/runbooks-and-playbooks.md) | `planned` | — | — | Interactive backfill required. |
| 14-sre-and-operations | [sli-slo-sla](docs/14-sre-and-operations/sli-slo-sla.md) | `planned` | — | — | Interactive backfill required. |
| 14-sre-and-operations | [toil](docs/14-sre-and-operations/toil.md) | `planned` | — | — | Interactive backfill required. |
| 15-databases-and-distributed-systems | [backups-and-point-in-time-recovery](docs/15-databases-and-distributed-systems/backups-and-point-in-time-recovery.md) | `partial` | `postgres-backup-restore` | — | Exercises logical backup restore; PITR remains uncovered. |
| 15-databases-and-distributed-systems | [caching](docs/15-databases-and-distributed-systems/caching.md) | `covered` | `redis-cache-ttl` | — | Exercises stale cache repair and bounded TTL. |
| 15-databases-and-distributed-systems | [cap-theorem](docs/15-databases-and-distributed-systems/cap-theorem.md) | `planned` | — | — | Interactive backfill required. |
| 15-databases-and-distributed-systems | [connection-pooling](docs/15-databases-and-distributed-systems/connection-pooling.md) | `planned` | — | — | Interactive backfill required. |
| 15-databases-and-distributed-systems | [consistency-models](docs/15-databases-and-distributed-systems/consistency-models.md) | `planned` | — | — | Interactive backfill required. |
| 15-databases-and-distributed-systems | [idempotency-and-backpressure](docs/15-databases-and-distributed-systems/idempotency-and-backpressure.md) | `planned` | — | — | Interactive backfill required. |
| 15-databases-and-distributed-systems | [indexes-locks-and-migrations](docs/15-databases-and-distributed-systems/indexes-locks-and-migrations.md) | `partial` | `postgres-index-performance` | — | Exercises index diagnosis/repair; locks and migrations remain uncovered. |
| 15-databases-and-distributed-systems | [leader-election-and-consensus](docs/15-databases-and-distributed-systems/leader-election-and-consensus.md) | `planned` | — | — | Interactive backfill required. |
| 15-databases-and-distributed-systems | [message-queues-and-event-driven-architecture](docs/15-databases-and-distributed-systems/message-queues-and-event-driven-architecture.md) | `covered` | `rabbitmq-routing-key` | — | Exercises a real RabbitMQ routing fault and delivery repair. |
| 15-databases-and-distributed-systems | [monolith-modular-monolith-and-microservices](docs/15-databases-and-distributed-systems/monolith-modular-monolith-and-microservices.md) | `planned` | — | — | Interactive backfill required. |
| 15-databases-and-distributed-systems | [postgresql-mysql-and-redis](docs/15-databases-and-distributed-systems/postgresql-mysql-and-redis.md) | `planned` | — | — | Interactive backfill required. |
| 15-databases-and-distributed-systems | [rate-limiting](docs/15-databases-and-distributed-systems/rate-limiting.md) | `covered` | `nginx-rate-limiting` | — | Exercises request throttling, burst handling and HTTP 429. |
| 15-databases-and-distributed-systems | [relational-vs-non-relational-databases](docs/15-databases-and-distributed-systems/relational-vs-non-relational-databases.md) | `planned` | — | — | Interactive backfill required. |
| 15-databases-and-distributed-systems | [replication-and-high-availability](docs/15-databases-and-distributed-systems/replication-and-high-availability.md) | `planned` | — | — | Interactive backfill required. |
| 15-databases-and-distributed-systems | [retry-timeout-and-circuit-breaker](docs/15-databases-and-distributed-systems/retry-timeout-and-circuit-breaker.md) | `planned` | — | — | Interactive backfill required. |
| 15-databases-and-distributed-systems | [service-discovery-and-api-gateway](docs/15-databases-and-distributed-systems/service-discovery-and-api-gateway.md) | `partial` | `nginx-reverse-proxy` | — | Exercises reverse proxy/upstream resolution, not the full API gateway/service-discovery boundary. |
| 15-databases-and-distributed-systems | [synchronous-vs-asynchronous-communication](docs/15-databases-and-distributed-systems/synchronous-vs-asynchronous-communication.md) | `planned` | — | — | Interactive backfill required. |
| 15-databases-and-distributed-systems | [transactions-and-acid](docs/15-databases-and-distributed-systems/transactions-and-acid.md) | `planned` | — | — | Interactive backfill required. |
| 16-gitops-and-platform-engineering | [application-promotion](docs/16-gitops-and-platform-engineering/application-promotion.md) | `planned` | — | — | Interactive backfill required. |
| 16-gitops-and-platform-engineering | [argo-cd](docs/16-gitops-and-platform-engineering/argo-cd.md) | `planned` | — | — | Interactive backfill required. |
| 16-gitops-and-platform-engineering | [developer-experience](docs/16-gitops-and-platform-engineering/developer-experience.md) | `planned` | — | — | Interactive backfill required. |
| 16-gitops-and-platform-engineering | [flux](docs/16-gitops-and-platform-engineering/flux.md) | `planned` | — | — | Interactive backfill required. |
| 16-gitops-and-platform-engineering | [git-as-source-of-truth](docs/16-gitops-and-platform-engineering/git-as-source-of-truth.md) | `planned` | — | — | Interactive backfill required. |
| 16-gitops-and-platform-engineering | [gitops-practical-walkthrough](docs/16-gitops-and-platform-engineering/gitops-practical-walkthrough.md) | `planned` | — | — | Interactive backfill required. |
| 16-gitops-and-platform-engineering | [gitops-secrets](docs/16-gitops-and-platform-engineering/gitops-secrets.md) | `planned` | — | — | Interactive backfill required. |
| 16-gitops-and-platform-engineering | [gitops-troubleshooting](docs/16-gitops-and-platform-engineering/gitops-troubleshooting.md) | `planned` | — | — | Interactive backfill required. |
| 16-gitops-and-platform-engineering | [golden-paths-and-paved-road](docs/16-gitops-and-platform-engineering/golden-paths-and-paved-road.md) | `planned` | — | — | Interactive backfill required. |
| 16-gitops-and-platform-engineering | [guardrails](docs/16-gitops-and-platform-engineering/guardrails.md) | `planned` | — | — | Interactive backfill required. |
| 16-gitops-and-platform-engineering | [internal-developer-platform](docs/16-gitops-and-platform-engineering/internal-developer-platform.md) | `planned` | — | — | Interactive backfill required. |
| 16-gitops-and-platform-engineering | [multi-tenancy](docs/16-gitops-and-platform-engineering/multi-tenancy.md) | `planned` | — | — | Interactive backfill required. |
| 16-gitops-and-platform-engineering | [platform-as-a-product](docs/16-gitops-and-platform-engineering/platform-as-a-product.md) | `planned` | — | — | Interactive backfill required. |
| 16-gitops-and-platform-engineering | [pull-based-deployment](docs/16-gitops-and-platform-engineering/pull-based-deployment.md) | `planned` | — | — | Interactive backfill required. |
| 16-gitops-and-platform-engineering | [reconciliation-and-drift-detection](docs/16-gitops-and-platform-engineering/reconciliation-and-drift-detection.md) | `planned` | — | — | Interactive backfill required. |
| 16-gitops-and-platform-engineering | [self-service](docs/16-gitops-and-platform-engineering/self-service.md) | `planned` | — | — | Interactive backfill required. |
| 16-gitops-and-platform-engineering | [service-catalog](docs/16-gitops-and-platform-engineering/service-catalog.md) | `planned` | — | — | Interactive backfill required. |
| 17-keycloak-and-identity-platform | [admin-console-admin-rest-api-automation](docs/17-keycloak-and-identity-platform/admin-console-admin-rest-api-automation.md) | `planned` | — | `labs/keycloak-ai-api/README.md` | Interactive backfill required. |
| 17-keycloak-and-identity-platform | [authentication-flows-executions-and-required-actions](docs/17-keycloak-and-identity-platform/authentication-flows-executions-and-required-actions.md) | `planned` | — | `labs/keycloak-ai-api/README.md` | Interactive backfill required. |
| 17-keycloak-and-identity-platform | [authorization-services-resources-scopes-policies-permissions](docs/17-keycloak-and-identity-platform/authorization-services-resources-scopes-policies-permissions.md) | `planned` | — | `labs/keycloak-ai-api/README.md` | Interactive backfill required. |
| 17-keycloak-and-identity-platform | [backup-restore-realm-import-export-disaster-recovery](docs/17-keycloak-and-identity-platform/backup-restore-realm-import-export-disaster-recovery.md) | `planned` | — | `labs/keycloak-ai-api/README.md` | Interactive backfill required. |
| 17-keycloak-and-identity-platform | [custom-providers-spi-extension-lifecycle](docs/17-keycloak-and-identity-platform/custom-providers-spi-extension-lifecycle.md) | `planned` | — | `labs/keycloak-ai-api/README.md` | Interactive backfill required. |
| 17-keycloak-and-identity-platform | [database-transactions-connection-pools-schema-lifecycle](docs/17-keycloak-and-identity-platform/database-transactions-connection-pools-schema-lifecycle.md) | `planned` | — | `labs/keycloak-ai-api/README.md` | Interactive backfill required. |
| 17-keycloak-and-identity-platform | [events-audit-metrics-observability](docs/17-keycloak-and-identity-platform/events-audit-metrics-observability.md) | `planned` | — | `labs/keycloak-ai-api/README.md` | Interactive backfill required. |
| 17-keycloak-and-identity-platform | [high-availability-multi-az-multi-cluster-trade-offs](docs/17-keycloak-and-identity-platform/high-availability-multi-az-multi-cluster-trade-offs.md) | `planned` | — | `labs/keycloak-ai-api/README.md` | Interactive backfill required. |
| 17-keycloak-and-identity-platform | [identity-brokering](docs/17-keycloak-and-identity-platform/identity-brokering.md) | `planned` | — | `labs/keycloak-ai-api/README.md` | Interactive backfill required. |
| 17-keycloak-and-identity-platform | [infinispan-caches-clustering-session-behavior](docs/17-keycloak-and-identity-platform/infinispan-caches-clustering-session-behavior.md) | `planned` | — | `labs/keycloak-ai-api/README.md` | Interactive backfill required. |
| 17-keycloak-and-identity-platform | [keycloak-architecture-and-responsibility-boundary](docs/17-keycloak-and-identity-platform/keycloak-architecture-and-responsibility-boundary.md) | `planned` | — | `labs/keycloak-ai-api/README.md` | Interactive backfill required. |
| 17-keycloak-and-identity-platform | [keycloak-operator-kubernetes-deployment](docs/17-keycloak-and-identity-platform/keycloak-operator-kubernetes-deployment.md) | `planned` | — | `labs/keycloak-ai-api/README.md` | Interactive backfill required. |
| 17-keycloak-and-identity-platform | [keycloak-performance-sizing-load-testing](docs/17-keycloak-and-identity-platform/keycloak-performance-sizing-load-testing.md) | `planned` | — | `labs/keycloak-ai-api/README.md` | Interactive backfill required. |
| 17-keycloak-and-identity-platform | [keycloak-server-configuration-hostname-reverse-proxy](docs/17-keycloak-and-identity-platform/keycloak-server-configuration-hostname-reverse-proxy.md) | `planned` | — | `labs/keycloak-ai-api/README.md` | Interactive backfill required. |
| 17-keycloak-and-identity-platform | [keycloak-troubleshooting](docs/17-keycloak-and-identity-platform/keycloak-troubleshooting.md) | `planned` | — | `labs/keycloak-ai-api/README.md` | Interactive backfill required. |
| 17-keycloak-and-identity-platform | [ldap-active-directory-federation](docs/17-keycloak-and-identity-platform/ldap-active-directory-federation.md) | `planned` | — | `labs/keycloak-ai-api/README.md` | Interactive backfill required. |
| 17-keycloak-and-identity-platform | [mfa-webauthn-passkeys-step-up-authentication](docs/17-keycloak-and-identity-platform/mfa-webauthn-passkeys-step-up-authentication.md) | `planned` | — | `labs/keycloak-ai-api/README.md` | Interactive backfill required. |
| 17-keycloak-and-identity-platform | [oidc-clients-redirect-uris-scopes-pkce](docs/17-keycloak-and-identity-platform/oidc-clients-redirect-uris-scopes-pkce.md) | `partial` | `keycloak-service-account` | `labs/keycloak-ai-api/README.md` | Exercises an OIDC client in confidential/M2M mode; redirect URI/PKCE remain uncovered. |
| 17-keycloak-and-identity-platform | [password-policies-brute-force-protection-account-recovery](docs/17-keycloak-and-identity-platform/password-policies-brute-force-protection-account-recovery.md) | `planned` | — | `labs/keycloak-ai-api/README.md` | Interactive backfill required. |
| 17-keycloak-and-identity-platform | [public-confidential-and-bearer-only-clients](docs/17-keycloak-and-identity-platform/public-confidential-and-bearer-only-clients.md) | `partial` | `keycloak-service-account` | `labs/keycloak-ai-api/README.md` | Exercises confidential client behavior only. |
| 17-keycloak-and-identity-platform | [realm-client-user-group-role-session](docs/17-keycloak-and-identity-platform/realm-client-user-group-role-session.md) | `planned` | — | `labs/keycloak-ai-api/README.md` | Interactive backfill required. |
| 17-keycloak-and-identity-platform | [saml-clients-metadata-assertions-bindings](docs/17-keycloak-and-identity-platform/saml-clients-metadata-assertions-bindings.md) | `planned` | — | `labs/keycloak-ai-api/README.md` | Interactive backfill required. |
| 17-keycloak-and-identity-platform | [securing-apis-microservices-mcp-servers](docs/17-keycloak-and-identity-platform/securing-apis-microservices-mcp-servers.md) | `planned` | — | `labs/keycloak-ai-api/README.md` | Interactive backfill required. |
| 17-keycloak-and-identity-platform | [service-accounts-and-machine-to-machine-authentication](docs/17-keycloak-and-identity-platform/service-accounts-and-machine-to-machine-authentication.md) | `covered` | `keycloak-service-account` | `labs/keycloak-ai-api/README.md` | Obtains and validates a real client-credentials token. |
| 17-keycloak-and-identity-platform | [themes-email-templates-localization](docs/17-keycloak-and-identity-platform/themes-email-templates-localization.md) | `planned` | — | `labs/keycloak-ai-api/README.md` | Interactive backfill required. |
| 17-keycloak-and-identity-platform | [tls-truststores-cookies-headers-production-hardening](docs/17-keycloak-and-identity-platform/tls-truststores-cookies-headers-production-hardening.md) | `planned` | — | `labs/keycloak-ai-api/README.md` | Interactive backfill required. |
| 17-keycloak-and-identity-platform | [token-exchange-impersonation-delegated-access](docs/17-keycloak-and-identity-platform/token-exchange-impersonation-delegated-access.md) | `planned` | — | `labs/keycloak-ai-api/README.md` | Interactive backfill required. |
| 17-keycloak-and-identity-platform | [tokens-claims-protocol-mappers-client-scopes](docs/17-keycloak-and-identity-platform/tokens-claims-protocol-mappers-client-scopes.md) | `partial` | `keycloak-service-account` | `labs/keycloak-ai-api/README.md` | Exercises token claims/validation but not protocol mapper/client-scope administration. |
| 17-keycloak-and-identity-platform | [upgrades-migration-guides-rollback-boundaries](docs/17-keycloak-and-identity-platform/upgrades-migration-guides-rollback-boundaries.md) | `planned` | — | `labs/keycloak-ai-api/README.md` | Interactive backfill required. |
| 17-keycloak-and-identity-platform | [user-storage-synchronization-cache-semantics](docs/17-keycloak-and-identity-platform/user-storage-synchronization-cache-semantics.md) | `planned` | — | `labs/keycloak-ai-api/README.md` | Interactive backfill required. |
| 18-machine-learning-fundamentals | [artificial-intelligence-machine-learning-deep-learning-generative-ai](docs/18-machine-learning-fundamentals/artificial-intelligence-machine-learning-deep-learning-generative-ai.md) | `planned` | — | `labs/machine-learning/README.md` | Interactive backfill required. |
| 18-machine-learning-fundamentals | [calibration-uncertainty](docs/18-machine-learning-fundamentals/calibration-uncertainty.md) | `planned` | — | `labs/machine-learning/README.md` | Interactive backfill required. |
| 18-machine-learning-fundamentals | [classification-metrics](docs/18-machine-learning-fundamentals/classification-metrics.md) | `planned` | — | `labs/machine-learning/README.md` | Interactive backfill required. |
| 18-machine-learning-fundamentals | [cross-validation](docs/18-machine-learning-fundamentals/cross-validation.md) | `planned` | — | `labs/machine-learning/README.md` | Interactive backfill required. |
| 18-machine-learning-fundamentals | [data-leakage-train-serving-skew](docs/18-machine-learning-fundamentals/data-leakage-train-serving-skew.md) | `planned` | — | `labs/machine-learning/README.md` | Interactive backfill required. |
| 18-machine-learning-fundamentals | [data-preprocessing-normalization-encoding](docs/18-machine-learning-fundamentals/data-preprocessing-normalization-encoding.md) | `planned` | — | `labs/machine-learning/README.md` | Interactive backfill required. |
| 18-machine-learning-fundamentals | [data-quality-bias-responsible-ai](docs/18-machine-learning-fundamentals/data-quality-bias-responsible-ai.md) | `planned` | — | `labs/machine-learning/README.md` | Interactive backfill required. |
| 18-machine-learning-fundamentals | [dataset-sample-feature-label-target](docs/18-machine-learning-fundamentals/dataset-sample-feature-label-target.md) | `planned` | — | `labs/machine-learning/README.md` | Interactive backfill required. |
| 18-machine-learning-fundamentals | [decision-trees-random-forests-gradient-boosting](docs/18-machine-learning-fundamentals/decision-trees-random-forests-gradient-boosting.md) | `planned` | — | `labs/machine-learning/README.md` | Interactive backfill required. |
| 18-machine-learning-fundamentals | [explainability-feature-importance](docs/18-machine-learning-fundamentals/explainability-feature-importance.md) | `planned` | — | `labs/machine-learning/README.md` | Interactive backfill required. |
| 18-machine-learning-fundamentals | [feature-engineering-feature-selection](docs/18-machine-learning-fundamentals/feature-engineering-feature-selection.md) | `planned` | — | `labs/machine-learning/README.md` | Interactive backfill required. |
| 18-machine-learning-fundamentals | [gradient-descent-learning-rate-convergence](docs/18-machine-learning-fundamentals/gradient-descent-learning-rate-convergence.md) | `planned` | — | `labs/machine-learning/README.md` | Interactive backfill required. |
| 18-machine-learning-fundamentals | [hyperparameters-hyperparameter-optimization](docs/18-machine-learning-fundamentals/hyperparameters-hyperparameter-optimization.md) | `planned` | — | `labs/machine-learning/README.md` | Interactive backfill required. |
| 18-machine-learning-fundamentals | [imbalanced-datasets-threshold-selection](docs/18-machine-learning-fundamentals/imbalanced-datasets-threshold-selection.md) | `planned` | — | `labs/machine-learning/README.md` | Interactive backfill required. |
| 18-machine-learning-fundamentals | [linear-logistic-regression](docs/18-machine-learning-fundamentals/linear-logistic-regression.md) | `planned` | — | `labs/machine-learning/README.md` | Interactive backfill required. |
| 18-machine-learning-fundamentals | [loss-functions-optimization](docs/18-machine-learning-fundamentals/loss-functions-optimization.md) | `planned` | — | `labs/machine-learning/README.md` | Interactive backfill required. |
| 18-machine-learning-fundamentals | [ml-troubleshooting-mental-model](docs/18-machine-learning-fundamentals/ml-troubleshooting-mental-model.md) | `planned` | — | `labs/machine-learning/README.md` | Interactive backfill required. |
| 18-machine-learning-fundamentals | [neural-network-fundamentals](docs/18-machine-learning-fundamentals/neural-network-fundamentals.md) | `planned` | — | `labs/machine-learning/README.md` | Interactive backfill required. |
| 18-machine-learning-fundamentals | [offline-evaluation-production-outcome](docs/18-machine-learning-fundamentals/offline-evaluation-production-outcome.md) | `planned` | — | `labs/machine-learning/README.md` | Interactive backfill required. |
| 18-machine-learning-fundamentals | [overfitting-underfitting-bias-variance](docs/18-machine-learning-fundamentals/overfitting-underfitting-bias-variance.md) | `planned` | — | `labs/machine-learning/README.md` | Interactive backfill required. |
| 18-machine-learning-fundamentals | [regression-classification-ranking-clustering](docs/18-machine-learning-fundamentals/regression-classification-ranking-clustering.md) | `planned` | — | `labs/machine-learning/README.md` | Interactive backfill required. |
| 18-machine-learning-fundamentals | [regression-metrics](docs/18-machine-learning-fundamentals/regression-metrics.md) | `planned` | — | `labs/machine-learning/README.md` | Interactive backfill required. |
| 18-machine-learning-fundamentals | [regularization-early-stopping](docs/18-machine-learning-fundamentals/regularization-early-stopping.md) | `planned` | — | `labs/machine-learning/README.md` | Interactive backfill required. |
| 18-machine-learning-fundamentals | [reproducibility-random-seeds](docs/18-machine-learning-fundamentals/reproducibility-random-seeds.md) | `planned` | — | `labs/machine-learning/README.md` | Interactive backfill required. |
| 18-machine-learning-fundamentals | [supervised-unsupervised-reinforcement-learning](docs/18-machine-learning-fundamentals/supervised-unsupervised-reinforcement-learning.md) | `planned` | — | `labs/machine-learning/README.md` | Interactive backfill required. |
| 18-machine-learning-fundamentals | [train-validation-test-split](docs/18-machine-learning-fundamentals/train-validation-test-split.md) | `planned` | — | `labs/machine-learning/README.md` | Interactive backfill required. |
