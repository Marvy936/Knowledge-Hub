# Learning Roadmap

Roadmap určuje odporúčané poradie učenia. Poradie sleduje závislosti medzi témami: najprv systémové a procesné fundamenty, potom delivery a automatizácia, následne kontajnery, Kubernetes, cloud a prevádzka.

Checkbox označuje, či je téma spracovaná v repozitári. Skutočná úroveň zvládnutia a potreba opakovania sa sledujú samostatne v [REVIEW.md](REVIEW.md).

## Fáza 1 — DevOps a systémové fundamenty

### DevOps Foundations

- [x] [Software Development Life Cycle](docs/00-foundations/sdlc.md)
- [x] [DevOps](docs/00-foundations/devops.md)
- [x] [DevOps lifecycle](docs/00-foundations/devops-lifecycle.md)
- [x] [CALMS framework](docs/00-foundations/calms.md)
- [x] [Three Ways of DevOps](docs/00-foundations/three-ways.md)
- [x] [Systems thinking](docs/00-foundations/systems-thinking.md)
- [x] [Feedback loops](docs/00-foundations/feedback-loops.md)
- [x] [Continuous improvement](docs/00-foundations/continuous-improvement.md)
- [x] [T-shaped, I-shaped a π-shaped engineer](docs/00-foundations/t-shaped-engineer.md)
- [x] [Ownership mindset](docs/00-foundations/ownership-mindset.md)
- [x] [You build it, you run it](docs/00-foundations/you-build-it-you-run-it.md)
- [x] [Automation mindset](docs/00-foundations/automation-mindset.md)
- [x] [Declarative vs. imperative prístup](docs/00-foundations/declarative-vs-imperative.md)
- [x] [Idempotencia](docs/00-foundations/idempotency.md)
- [x] [Desired state a reconciliation](docs/00-foundations/desired-state-and-reconciliation.md)
- [x] [Immutable vs. mutable infrastructure](docs/00-foundations/immutable-vs-mutable-infrastructure.md)
- [x] [Toil a technical debt](docs/00-foundations/toil-and-technical-debt.md)
- [x] [Value stream mapping](docs/00-foundations/value-stream-mapping.md)
- [x] [DORA metrics](docs/00-foundations/dora-metrics.md)
- [x] [DevOps anti-patterns](docs/00-foundations/devops-anti-patterns.md)

### Linux and Systems

- [x] [Kernel a user space](docs/01-linux-and-systems/kernel-and-user-space.md)
- [x] [Procesy, thready, PID a signals](docs/01-linux-and-systems/processes-threads-pid-signals.md)
- [x] [Filesystem hierarchy, inodes a links](docs/01-linux-and-systems/filesystem-hierarchy-inodes-links.md)
- [x] [Users, groups, permissions, sudo a PAM](docs/01-linux-and-systems/users-groups-permissions-sudo-pam.md)
- [x] [Shell, Bash, pipes, redirection a exit codes](docs/01-linux-and-systems/shell-bash-pipes-redirection-exit-codes.md)
- [x] [Environment variables](docs/01-linux-and-systems/environment-variables.md)
- [x] [systemd, services a daemons](docs/01-linux-and-systems/systemd-services-daemons.md)
- [x] [Package management](docs/01-linux-and-systems/package-management.md)
- [x] [journald a logging](docs/01-linux-and-systems/journald-and-logging.md)
- [x] [Storage, mounty a filesystems](docs/01-linux-and-systems/storage-mounts-and-filesystems.md)
- [ ] Memory a CPU fundamentals
- [x] [Linux networking](docs/01-linux-and-systems/linux-networking.md)
- [x] [SSH](docs/01-linux-and-systems/ssh.md)
- [x] [Cron a systemd timers](docs/01-linux-and-systems/cron-and-systemd-timers.md)
- [x] [Namespaces](docs/01-linux-and-systems/namespaces.md)
- [x] [cgroups](docs/01-linux-and-systems/cgroups.md)
- [x] [Linux capabilities](docs/01-linux-and-systems/linux-capabilities.md)
- [x] [SELinux a AppArmor](docs/01-linux-and-systems/selinux-and-apparmor.md)
- [x] [Performance a troubleshooting](docs/01-linux-and-systems/performance-and-troubleshooting.md)

### Networking and Web Fundamentals

- [x] [OSI a TCP/IP model](docs/02-networking-and-web/osi-and-tcp-ip-model.md)
- [x] [Ethernet, MAC a ARP](docs/02-networking-and-web/ethernet-mac-arp.md)
- [x] [IPv4, IPv6 a subnetting](docs/02-networking-and-web/ipv4-ipv6-subnetting.md)
- [x] [Routing a default gateway](docs/02-networking-and-web/routing-and-default-gateway.md)
- [x] [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md)
- [ ] Ports a sockets
- [x] [DNS](docs/02-networking-and-web/dns.md)
- [x] [DHCP](docs/02-networking-and-web/dhcp.md)
- [x] [NAT](docs/02-networking-and-web/nat.md)
- [x] [Firewally](docs/02-networking-and-web/firewalls.md)
- [x] [Proxy a reverse proxy](docs/02-networking-and-web/proxy-and-reverse-proxy.md)
- [x] [Load balancing](docs/02-networking-and-web/load-balancing.md)
- [x] [HTTP](docs/02-networking-and-web/http.md)
- [ ] HTTPS, TLS, certificates a PKI
- [ ] REST APIs a WebSockets
- [x] [Network troubleshooting](docs/02-networking-and-web/network-troubleshooting.md)

### Git and Automation Basics

- [x] [Git object model](docs/03-git-and-automation/git-object-model.md)
- [x] [Working tree, staging area a repository](docs/03-git-and-automation/working-tree-staging-repository.md)
- [x] [Commit, branch, tag a HEAD](docs/03-git-and-automation/commit-branch-tag-head.md)
- [x] [Clone, fetch, pull a push](docs/03-git-and-automation/clone-fetch-pull-push.md)
- [x] [Merge a rebase](docs/03-git-and-automation/merge-and-rebase.md)
- [x] [Reset, revert a restore](docs/03-git-and-automation/reset-revert-restore.md)
- [x] [Cherry-pick a stash](docs/03-git-and-automation/cherry-pick-and-stash.md)
- [x] [Konflikty](docs/03-git-and-automation/merge-conflicts.md)
- [x] [Branching strategies](docs/03-git-and-automation/branching-strategies.md)
- [x] [Monorepo vs. multirepo](docs/03-git-and-automation/monorepo-vs-multirepo.md)
- [x] [Bash automation](docs/03-git-and-automation/bash-automation.md)
- [x] [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md)
- [x] [Python for automation](docs/03-git-and-automation/python-for-automation.md)
- [x] [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md)

## Fáza 2 — Quality, delivery a automatizácia

### Testing and Software Quality

- [x] [Verification vs. validation](docs/04-testing-and-quality/verification-vs-validation.md)
- [x] [Test pyramid](docs/04-testing-and-quality/test-pyramid.md)
- [x] [Unit, integration a component tests](docs/04-testing-and-quality/unit-integration-component-tests.md)
- [x] [Contract a API tests](docs/04-testing-and-quality/contract-and-api-tests.md)
- [x] [End-to-end a acceptance tests](docs/04-testing-and-quality/end-to-end-and-acceptance-tests.md)
- [x] [Smoke a regression tests](docs/04-testing-and-quality/smoke-and-regression-tests.md)
- [x] [Performance, load a stress tests](docs/04-testing-and-quality/performance-load-stress-tests.md)
- [x] [Security a infrastructure tests](docs/04-testing-and-quality/security-and-infrastructure-tests.md)
- [x] [Static analysis, linting a type checking](docs/04-testing-and-quality/static-analysis-linting-type-checking.md)
- [x] [Code coverage a quality gates](docs/04-testing-and-quality/code-coverage-and-quality-gates.md)
- [x] [Mocks, stubs a fakes](docs/04-testing-and-quality/mocks-stubs-fakes.md)
- [x] [Flaky tests a test data](docs/04-testing-and-quality/flaky-tests-and-test-data.md)
- [x] [Shift-left](docs/04-testing-and-quality/shift-left.md)
- [x] [Shift-right](docs/04-testing-and-quality/shift-right.md)
- [x] [Chaos testing](docs/04-testing-and-quality/chaos-testing.md)

### CI/CD and Release Engineering

- [x] [Continuous Integration](docs/05-ci-cd-and-release/continuous-integration.md)
- [x] [Continuous Delivery](docs/05-ci-cd-and-release/continuous-delivery.md)
- [x] [Continuous Deployment](docs/05-ci-cd-and-release/continuous-deployment.md)
- [x] [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md)
- [x] [Trigger, artifact a cache](docs/05-ci-cd-and-release/trigger-artifact-cache.md)
- [x] [Environment a promotion](docs/05-ci-cd-and-release/environment-and-promotion.md)
- [x] [Quality gates a approvals](docs/05-ci-cd-and-release/quality-gates-and-approvals.md)
- [x] [Pipeline as Code](docs/05-ci-cd-and-release/pipeline-as-code.md)
- [x] [Reusable a parallel pipelines](docs/05-ci-cd-and-release/reusable-and-parallel-pipelines.md)
- [x] [Artifact versioning](docs/05-ci-cd-and-release/artifact-versioning.md)
- [x] [Semantic Versioning](docs/05-ci-cd-and-release/semantic-versioning.md)
- [x] [Release management](docs/05-ci-cd-and-release/release-management.md)
- [x] [Recreate deployment](docs/05-ci-cd-and-release/recreate-deployment.md)
- [x] [Rolling update](docs/05-ci-cd-and-release/rolling-update.md)
- [x] [Blue-green deployment](docs/05-ci-cd-and-release/blue-green-deployment.md)
- [x] [Canary deployment](docs/05-ci-cd-and-release/canary-deployment.md)
- [x] [A/B testing](docs/05-ci-cd-and-release/a-b-testing.md)
- [x] [Shadow deployment](docs/05-ci-cd-and-release/shadow-deployment.md)
- [x] [Ring deployment](docs/05-ci-cd-and-release/ring-deployment.md)
- [x] [Feature flags](docs/05-ci-cd-and-release/feature-flags.md)
- [x] [Progressive delivery](docs/05-ci-cd-and-release/progressive-delivery.md)
- [x] [Rollback a roll-forward](docs/05-ci-cd-and-release/rollback-and-roll-forward.md)
- [x] [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md)

### GitLab

- [x] [Projects, groups a permissions](docs/06-gitlab/projects-groups-permissions.md)
- [x] [Merge requests a approvals](docs/06-gitlab/merge-requests-and-approvals.md)
- [x] [Protected branches a environments](docs/06-gitlab/protected-branches-and-environments.md)
- [x] [GitLab CI/CD syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md)
- [x] [Runners a executors](docs/06-gitlab/runners-and-executors.md)
- [x] [Variables a secrets](docs/06-gitlab/variables-and-secrets.md)
- [x] [Artifacts a cache](docs/06-gitlab/artifacts-and-cache.md)
- [x] [Container a package registry](docs/06-gitlab/container-and-package-registry.md)
- [x] [Environments, deployments a releases](docs/06-gitlab/environments-deployments-releases.md)
- [x] [Security scanning](docs/06-gitlab/security-scanning.md)

### Infrastructure as Code and Configuration Management

- [x] [Infrastructure as Code principles](docs/07-infrastructure-as-code-and-configuration-management/infrastructure-as-code-principles.md)
- [x] [Terraform providers, resources a data sources](docs/07-infrastructure-as-code-and-configuration-management/terraform-providers-resources-data-sources.md)
- [x] [Variables, locals a outputs](docs/07-infrastructure-as-code-and-configuration-management/variables-locals-outputs.md)
- [x] [Expressions a dependency graph](docs/07-infrastructure-as-code-and-configuration-management/expressions-and-dependency-graph.md)
- [x] [Terraform state](docs/07-infrastructure-as-code-and-configuration-management/terraform-state.md)
- [x] [Remote backend a state locking](docs/07-infrastructure-as-code-and-configuration-management/remote-backend-and-state-locking.md)
- [x] [Modules](docs/07-infrastructure-as-code-and-configuration-management/modules.md)
- [x] [Lifecycle, import a moved blocks](docs/07-infrastructure-as-code-and-configuration-management/lifecycle-import-moved-blocks.md)
- [x] [Drift](docs/07-infrastructure-as-code-and-configuration-management/drift.md)
- [x] [Terraform testing a policy](docs/07-infrastructure-as-code-and-configuration-management/terraform-testing-and-policy.md)
- [x] [Ansible architecture](docs/07-infrastructure-as-code-and-configuration-management/ansible-architecture.md)
- [x] [Inventory](docs/07-infrastructure-as-code-and-configuration-management/inventory.md)
- [x] [Modules, tasks, plays a playbooks](docs/07-infrastructure-as-code-and-configuration-management/modules-tasks-plays-playbooks.md)
- [x] [Variables, facts a templates](docs/07-infrastructure-as-code-and-configuration-management/variables-facts-templates.md)
- [x] [Handlers, loops a conditionals](docs/07-infrastructure-as-code-and-configuration-management/handlers-loops-conditionals.md)
- [x] [Roles a collections](docs/07-infrastructure-as-code-and-configuration-management/roles-and-collections.md)
- [x] [Vault](docs/07-infrastructure-as-code-and-configuration-management/vault.md)
- [x] [Ansible idempotencia](docs/07-infrastructure-as-code-and-configuration-management/ansible-idempotency.md)
- [x] [Terraform vs. Ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md)

## Fáza 3 — Containers, Kubernetes a CKA

### Container Fundamentals and Docker

- [x] [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md)
- [x] [Namespaces, cgroups a capabilities](docs/08-container-fundamentals-and-docker/namespaces-cgroups-capabilities.md)
- [x] [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md)
- [x] [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md)
- [x] [Registries](docs/08-container-fundamentals-and-docker/registries.md)
- [x] [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md)
- [x] [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md)
- [x] [Container security](docs/08-container-fundamentals-and-docker/container-security.md)
- [x] [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md)
- [x] [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md)
- [x] [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md)
- [x] [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md)
- [x] [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md)
- [x] [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md)
- [x] [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md)
- [x] [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md)
- [x] [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md)
- [x] [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md)

### Kubernetes

- [x] [Kubernetes architecture](docs/09-kubernetes/kubernetes-architecture.md)
- [x] [API a object model](docs/09-kubernetes/api-object-model.md)
- [x] [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md)
- [x] [Control plane components](docs/09-kubernetes/control-plane-components.md)
- [x] [Worker node components](docs/09-kubernetes/worker-node-components.md)
- [x] [Pod](docs/09-kubernetes/pod.md)
- [x] [ReplicaSet](docs/09-kubernetes/replicaset.md)
- [x] [Deployment](docs/09-kubernetes/deployment.md)
- [x] [StatefulSet](docs/09-kubernetes/statefulset.md)
- [x] [DaemonSet](docs/09-kubernetes/daemonset.md)
- [x] [Job a CronJob](docs/09-kubernetes/job-cronjob.md)
- [x] [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md)
- [x] [ServiceAccount](docs/09-kubernetes/serviceaccount.md)
- [x] [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md)
- [x] [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md)
- [x] [Cluster DNS](docs/09-kubernetes/cluster-dns.md)
- [x] [CNI a NetworkPolicy](docs/09-kubernetes/cni-networkpolicy.md)
- [x] [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md)
- [x] [Scheduling](docs/09-kubernetes/scheduling.md)
- [x] [Requests, limits a QoS](docs/09-kubernetes/requests-limits-qos.md)
- [x] [Probes](docs/09-kubernetes/probes.md)
- [x] [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md)
- [x] [HPA a autoscaling](docs/09-kubernetes/hpa-autoscaling.md)
- [x] [RBAC](docs/09-kubernetes/rbac.md)
- [x] [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md)
- [x] [ResourceQuota a LimitRange](docs/09-kubernetes/resourcequota-limitrange.md)
- [x] [Cluster installation a lifecycle](docs/09-kubernetes/cluster-installation-lifecycle.md)
- [x] [etcd backup a restore](docs/09-kubernetes/etcd-backup-restore.md)
- [x] [Upgrades](docs/09-kubernetes/upgrades.md)
- [x] [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md)
- [x] [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md)

### Helm and CKA

- [x] [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md)
- [x] [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md)
- [x] [Named templates](docs/10-helm-and-cka/named-templates.md)
- [x] [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md)
- [x] [Hooks](docs/10-helm-and-cka/hooks.md)
- [x] [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md)
- [x] [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md)
- [x] [CKA timed labs](docs/10-helm-and-cka/cka-timed-labs.md)
- [x] [CKA troubleshooting drills](docs/10-helm-and-cka/cka-troubleshooting-drills.md)

## Fáza 4 — Cloud, security a prevádzka

### Cloud and AWS

- [x] [IaaS, PaaS a SaaS](docs/11-cloud-and-aws/iaas-paas-saas.md)
- [x] [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md)
- [x] [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md)
- [x] [Shared responsibility model](docs/11-cloud-and-aws/shared-responsibility-model.md)
- [x] [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md)
- [x] [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md)
- [x] [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md)
- [x] [IAM](docs/11-cloud-and-aws/iam.md)
- [x] [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md)
- [x] [Internet Gateway a NAT Gateway](docs/11-cloud-and-aws/internet-gateway-nat-gateway.md)
- [x] [Security Groups a Network ACLs](docs/11-cloud-and-aws/security-groups-network-acls.md)
- [x] [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md)
- [x] [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md)
- [x] [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md)
- [x] [RDS](docs/11-cloud-and-aws/rds.md)
- [x] [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md)
- [x] [Lambda](docs/11-cloud-and-aws/lambda.md)
- [x] [ECS a EKS](docs/11-cloud-and-aws/ecs-eks.md)
- [x] [CloudWatch a CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md)
- [x] [Systems Manager](docs/11-cloud-and-aws/systems-manager.md)
- [x] [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md)
- [x] [AWS Backup](docs/11-cloud-and-aws/aws-backup.md)
- [x] [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md)
- [x] [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md)
- [x] [AWS Certified CloudOps Engineer – Associate (SOA-C03)](docs/11-cloud-and-aws/cloudops-engineer-associate-soa-c03.md)
- [x] [CloudOps domain review a timed reasoning](docs/11-cloud-and-aws/cloudops-domain-review-timed-reasoning.md)
- [x] [CloudOps hands-on labs](docs/11-cloud-and-aws/cloudops-hands-on-labs.md)
- [x] [CloudOps troubleshooting drills](docs/11-cloud-and-aws/cloudops-troubleshooting-drills.md)

### Observability

- [x] [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md)
- [x] [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md)
- [x] [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md)
- [x] [RED method](docs/12-observability/red-method.md)
- [x] [USE method](docs/12-observability/use-method.md)
- [x] [Golden Signals](docs/12-observability/golden-signals.md)
- [x] [Prometheus](docs/12-observability/prometheus.md)
- [x] [Alertmanager](docs/12-observability/alertmanager.md)
- [x] [Grafana](docs/12-observability/grafana.md)
- [x] [Loki](docs/12-observability/loki.md)
- [x] [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md)
- [x] [Fluent Bit](docs/12-observability/fluent-bit.md)
- [x] [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md)
- [x] [OpenTelemetry](docs/12-observability/opentelemetry.md)
- [x] [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md)
- [x] [Cardinality](docs/12-observability/cardinality.md)

### Security and Identity

- [x] [CIA triáda](docs/13-security-and-identity/cia-triad.md)
- [x] [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md)
- [x] [Least privilege](docs/13-security-and-identity/least-privilege.md)
- [x] [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md)
- [x] [Active Directory](docs/13-security-and-identity/active-directory.md)
- [x] [LDAP](docs/13-security-and-identity/ldap.md)
- [x] [Kerberos](docs/13-security-and-identity/kerberos.md)
- [x] [OAuth 2.0](docs/13-security-and-identity/oauth-2.md)
- [x] [OpenID Connect](docs/13-security-and-identity/openid-connect.md)
- [x] [SAML](docs/13-security-and-identity/saml.md)
- [x] [Secrets management](docs/13-security-and-identity/secrets-management.md)
- [x] [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md)
- [x] [Vulnerability a patch management](docs/13-security-and-identity/vulnerability-and-patch-management.md)
- [x] [Threat modeling](docs/13-security-and-identity/threat-modeling.md)
- [x] [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md)
- [x] [SBOM](docs/13-security-and-identity/sbom.md)
- [x] [Image signing](docs/13-security-and-identity/image-signing.md)
- [x] [Policy as Code](docs/13-security-and-identity/policy-as-code.md)
- [x] [Zero Trust](docs/13-security-and-identity/zero-trust.md)

### SRE and Operations

- [x] [Reliability, availability a durability](docs/14-sre-and-operations/reliability-availability-durability.md)
- [x] [SLI, SLO a SLA](docs/14-sre-and-operations/sli-slo-sla.md)
- [x] [Error budgets](docs/14-sre-and-operations/error-budgets.md)
- [x] [Toil](docs/14-sre-and-operations/toil.md)
- [x] [Capacity planning](docs/14-sre-and-operations/capacity-planning.md)
- [x] [Incident management](docs/14-sre-and-operations/incident-management.md)
- [x] [On-call a escalation](docs/14-sre-and-operations/on-call-and-escalation.md)
- [x] [Runbooks a playbooks](docs/14-sre-and-operations/runbooks-and-playbooks.md)
- [x] [Root cause analysis](docs/14-sre-and-operations/root-cause-analysis.md)
- [x] [Blameless postmortems](docs/14-sre-and-operations/blameless-postmortems.md)
- [x] [Backup a restore](docs/14-sre-and-operations/backup-and-restore.md)
- [x] [RPO a RTO](docs/14-sre-and-operations/rpo-and-rto.md)
- [x] [Disaster recovery](docs/14-sre-and-operations/disaster-recovery.md)
- [x] [Chaos engineering](docs/14-sre-and-operations/chaos-engineering.md)
- [x] [Operational readiness](docs/14-sre-and-operations/operational-readiness.md)

## Fáza 5 — Architecture a pokročilé oblasti

### Databases and Distributed Systems

- [x] [Relational vs. non-relational databases](docs/15-databases-and-distributed-systems/relational-vs-non-relational-databases.md)
- [x] [Transactions a ACID](docs/15-databases-and-distributed-systems/transactions-and-acid.md)
- [x] [Indexy, locks a migrations](docs/15-databases-and-distributed-systems/indexes-locks-and-migrations.md)
- [x] [Replication a high availability](docs/15-databases-and-distributed-systems/replication-and-high-availability.md)
- [x] [Backups a point-in-time recovery](docs/15-databases-and-distributed-systems/backups-and-point-in-time-recovery.md)
- [x] [Connection pooling](docs/15-databases-and-distributed-systems/connection-pooling.md)
- [x] [PostgreSQL, MySQL a Redis](docs/15-databases-and-distributed-systems/postgresql-mysql-and-redis.md)
- [x] [Monolith, modular monolith a microservices](docs/15-databases-and-distributed-systems/monolith-modular-monolith-and-microservices.md)
- [x] [Synchronous vs. asynchronous communication](docs/15-databases-and-distributed-systems/synchronous-vs-asynchronous-communication.md)
- [x] [Message queues a event-driven architecture](docs/15-databases-and-distributed-systems/message-queues-and-event-driven-architecture.md)
- [x] [Service discovery a API gateway](docs/15-databases-and-distributed-systems/service-discovery-and-api-gateway.md)
- [x] [Caching](docs/15-databases-and-distributed-systems/caching.md)
- [x] [CAP theorem](docs/15-databases-and-distributed-systems/cap-theorem.md)
- [x] [Consistency models](docs/15-databases-and-distributed-systems/consistency-models.md)
- [x] [Leader election a consensus](docs/15-databases-and-distributed-systems/leader-election-and-consensus.md)
- [x] [Retry, timeout a circuit breaker](docs/15-databases-and-distributed-systems/retry-timeout-and-circuit-breaker.md)
- [x] [Rate limiting](docs/15-databases-and-distributed-systems/rate-limiting.md)
- [x] [Idempotency a backpressure](docs/15-databases-and-distributed-systems/idempotency-and-backpressure.md)

### GitOps and Platform Engineering

- [x] [Git ako source of truth](docs/16-gitops-and-platform-engineering/git-as-source-of-truth.md)
- [x] [Pull-based deployment](docs/16-gitops-and-platform-engineering/pull-based-deployment.md)
- [x] [Reconciliation a drift detection](docs/16-gitops-and-platform-engineering/reconciliation-and-drift-detection.md)
- [x] [Argo CD](docs/16-gitops-and-platform-engineering/argo-cd.md)
- [x] [Flux](docs/16-gitops-and-platform-engineering/flux.md)
- [x] [Application promotion](docs/16-gitops-and-platform-engineering/application-promotion.md)
- [x] [GitOps secrets](docs/16-gitops-and-platform-engineering/gitops-secrets.md)
- [x] [Internal Developer Platform](docs/16-gitops-and-platform-engineering/internal-developer-platform.md)
- [x] [Platform as a Product](docs/16-gitops-and-platform-engineering/platform-as-a-product.md)
- [x] [Golden paths a paved road](docs/16-gitops-and-platform-engineering/golden-paths-and-paved-road.md)
- [x] [Self-service](docs/16-gitops-and-platform-engineering/self-service.md)
- [x] [Developer experience](docs/16-gitops-and-platform-engineering/developer-experience.md)
- [x] [Service catalog](docs/16-gitops-and-platform-engineering/service-catalog.md)
- [x] [Guardrails](docs/16-gitops-and-platform-engineering/guardrails.md)
- [x] [Multi-tenancy](docs/16-gitops-and-platform-engineering/multi-tenancy.md)
## Fáza 6 — Identity platformy

### Keycloak and Identity Platform

- [x] [Keycloak architecture a responsibility boundary](docs/17-keycloak-and-identity-platform/keycloak-architecture-and-responsibility-boundary.md)
- [x] [Realm, client, user, group, role a session](docs/17-keycloak-and-identity-platform/realm-client-user-group-role-session.md)
- [x] [OIDC clients, redirect URIs, scopes a PKCE](docs/17-keycloak-and-identity-platform/oidc-clients-redirect-uris-scopes-pkce.md)
- [x] [SAML clients, metadata, assertions a bindings](docs/17-keycloak-and-identity-platform/saml-clients-metadata-assertions-bindings.md)
- [x] [Tokens, claims, protocol mappers a client scopes](docs/17-keycloak-and-identity-platform/tokens-claims-protocol-mappers-client-scopes.md)
- [x] [Public, confidential a bearer-only client model](docs/17-keycloak-and-identity-platform/public-confidential-and-bearer-only-clients.md)
- [x] [Service accounts a machine-to-machine authentication](docs/17-keycloak-and-identity-platform/service-accounts-and-machine-to-machine-authentication.md)
- [x] [Authentication flows, executions a required actions](docs/17-keycloak-and-identity-platform/authentication-flows-executions-and-required-actions.md)
- [x] [MFA, WebAuthn, passkeys a step-up authentication](docs/17-keycloak-and-identity-platform/mfa-webauthn-passkeys-step-up-authentication.md)
- [x] [Password policies, brute-force protection a account recovery](docs/17-keycloak-and-identity-platform/password-policies-brute-force-protection-account-recovery.md)
- [x] [Identity brokering](docs/17-keycloak-and-identity-platform/identity-brokering.md)
- [x] [LDAP a Active Directory federation](docs/17-keycloak-and-identity-platform/ldap-active-directory-federation.md)
- [x] [User storage, synchronization a cache semantics](docs/17-keycloak-and-identity-platform/user-storage-synchronization-cache-semantics.md)
- [x] [Authorization Services, resources, scopes, policies a permissions](docs/17-keycloak-and-identity-platform/authorization-services-resources-scopes-policies-permissions.md)
- [x] [Token exchange, impersonation a delegated access](docs/17-keycloak-and-identity-platform/token-exchange-impersonation-delegated-access.md)
- [x] [Admin Console, Admin REST API a automation](docs/17-keycloak-and-identity-platform/admin-console-admin-rest-api-automation.md)
- [x] [Events, audit, metrics a observability](docs/17-keycloak-and-identity-platform/events-audit-metrics-observability.md)
- [x] [Themes, email templates a localization](docs/17-keycloak-and-identity-platform/themes-email-templates-localization.md)
- [x] [Keycloak server configuration, hostname a reverse proxy](docs/17-keycloak-and-identity-platform/keycloak-server-configuration-hostname-reverse-proxy.md)
- [x] [TLS, truststores, cookies, headers a production hardening](docs/17-keycloak-and-identity-platform/tls-truststores-cookies-headers-production-hardening.md)
- [x] [Database, transactions, connection pools a schema lifecycle](docs/17-keycloak-and-identity-platform/database-transactions-connection-pools-schema-lifecycle.md)
- [x] [Infinispan caches, clustering a session behavior](docs/17-keycloak-and-identity-platform/infinispan-caches-clustering-session-behavior.md)
- [x] [Keycloak Operator a Kubernetes deployment](docs/17-keycloak-and-identity-platform/keycloak-operator-kubernetes-deployment.md)
- [x] [High availability, multi-AZ a multi-cluster trade-offs](docs/17-keycloak-and-identity-platform/high-availability-multi-az-multi-cluster-trade-offs.md)
- [x] [Backup, restore, realm import/export a disaster recovery](docs/17-keycloak-and-identity-platform/backup-restore-realm-import-export-disaster-recovery.md)
- [x] [Upgrades, migration guides a rollback boundaries](docs/17-keycloak-and-identity-platform/upgrades-migration-guides-rollback-boundaries.md)
- [x] [Custom providers, SPI a extension lifecycle](docs/17-keycloak-and-identity-platform/custom-providers-spi-extension-lifecycle.md)
- [x] [Securing APIs, microservices a MCP servers cez Keycloak](docs/17-keycloak-and-identity-platform/securing-apis-microservices-mcp-servers.md)
- [x] [Keycloak performance, sizing a load testing](docs/17-keycloak-and-identity-platform/keycloak-performance-sizing-load-testing.md)
- [x] [Keycloak troubleshooting](docs/17-keycloak-and-identity-platform/keycloak-troubleshooting.md)


<!-- ACTIVE-AI-ROADMAP:START -->

## Fáza 7 — Machine Learning a MLOps

### Machine Learning Fundamentals

- [x] [Artificial intelligence, machine learning, deep learning a generative AI](docs/18-machine-learning-fundamentals/artificial-intelligence-machine-learning-deep-learning-generative-ai.md)
- [x] [Dataset, sample, feature, label a target](docs/18-machine-learning-fundamentals/dataset-sample-feature-label-target.md)
- [x] [Supervised, unsupervised a reinforcement learning](docs/18-machine-learning-fundamentals/supervised-unsupervised-reinforcement-learning.md)
- [x] [Regression, classification, ranking a clustering](docs/18-machine-learning-fundamentals/regression-classification-ranking-clustering.md)
- [x] [Train, validation a test split](docs/18-machine-learning-fundamentals/train-validation-test-split.md)
- [x] [Data preprocessing, normalization a encoding](docs/18-machine-learning-fundamentals/data-preprocessing-normalization-encoding.md)
- [x] [Feature engineering a feature selection](docs/18-machine-learning-fundamentals/feature-engineering-feature-selection.md)
- [x] [Data leakage a train-serving skew](docs/18-machine-learning-fundamentals/data-leakage-train-serving-skew.md)
- [x] [Linear a logistic regression](docs/18-machine-learning-fundamentals/linear-logistic-regression.md)
- [x] [Decision trees, random forests a gradient boosting](docs/18-machine-learning-fundamentals/decision-trees-random-forests-gradient-boosting.md)
- [x] [Neural network fundamentals](docs/18-machine-learning-fundamentals/neural-network-fundamentals.md)
- [x] [Loss functions a optimization](docs/18-machine-learning-fundamentals/loss-functions-optimization.md)
- [x] [Gradient descent, learning rate a convergence](docs/18-machine-learning-fundamentals/gradient-descent-learning-rate-convergence.md)
- [x] [Overfitting, underfitting, bias a variance](docs/18-machine-learning-fundamentals/overfitting-underfitting-bias-variance.md)
- [x] [Regularization a early stopping](docs/18-machine-learning-fundamentals/regularization-early-stopping.md)
- [x] [Hyperparameters a hyperparameter optimization](docs/18-machine-learning-fundamentals/hyperparameters-hyperparameter-optimization.md)
- [x] [Classification metrics](docs/18-machine-learning-fundamentals/classification-metrics.md)
- [x] [Regression metrics](docs/18-machine-learning-fundamentals/regression-metrics.md)
- [x] [Imbalanced datasets a threshold selection](docs/18-machine-learning-fundamentals/imbalanced-datasets-threshold-selection.md)
- [x] [Cross-validation](docs/18-machine-learning-fundamentals/cross-validation.md)
- [x] [Calibration a uncertainty](docs/18-machine-learning-fundamentals/calibration-uncertainty.md)
- [x] [Explainability a feature importance](docs/18-machine-learning-fundamentals/explainability-feature-importance.md)
- [x] [Data quality, bias a responsible AI](docs/18-machine-learning-fundamentals/data-quality-bias-responsible-ai.md)
- [x] [Reproducibility a random seeds](docs/18-machine-learning-fundamentals/reproducibility-random-seeds.md)
- [x] [Offline evaluation oproti production outcome](docs/18-machine-learning-fundamentals/offline-evaluation-production-outcome.md)
- [x] [ML troubleshooting mental model](docs/18-machine-learning-fundamentals/ml-troubleshooting-mental-model.md)

### MLOps and ML Platforms

- [x] [ML lifecycle a rozdiel medzi DevOps a MLOps](docs/19-mlops-and-ml-platforms/ml-lifecycle-devops-vs-mlops.md)
- [x] [Data, code, environment a model lineage](docs/19-mlops-and-ml-platforms/data-code-environment-model-lineage.md)
- [x] [Dataset versioning](docs/19-mlops-and-ml-platforms/dataset-versioning.md)
- [x] [Experiment tracking](docs/19-mlops-and-ml-platforms/experiment-tracking.md)
- [x] [Artifact stores](docs/19-mlops-and-ml-platforms/artifact-stores.md)
- [x] [Model packaging a reproducible environments](docs/19-mlops-and-ml-platforms/model-packaging-reproducible-environments.md)
- [x] [Model Registry, versions, stages a aliases](docs/19-mlops-and-ml-platforms/model-registry-versions-stages-aliases.md)
- [x] [Feature stores a online/offline consistency](docs/19-mlops-and-ml-platforms/feature-stores-online-offline-consistency.md)
- [x] [ML pipeline orchestration](docs/19-mlops-and-ml-platforms/ml-pipeline-orchestration.md)
- [x] [Training pipelines a distributed training](docs/19-mlops-and-ml-platforms/training-pipelines-distributed-training.md)
- [x] [CI pre ML code, data a pipelines](docs/19-mlops-and-ml-platforms/ci-for-ml-code-data-pipelines.md)
- [x] [Continuous Delivery pre modely](docs/19-mlops-and-ml-platforms/continuous-delivery-for-models.md)
- [x] [Continuous Training a retraining triggers](docs/19-mlops-and-ml-platforms/continuous-training-retraining-triggers.md)
- [x] [Model validation a promotion gates](docs/19-mlops-and-ml-platforms/model-validation-promotion-gates.md)
- [x] [Batch, online a streaming inference](docs/19-mlops-and-ml-platforms/batch-online-streaming-inference.md)
- [x] [Shadow, canary a A/B model deployment](docs/19-mlops-and-ml-platforms/shadow-canary-ab-model-deployment.md)
- [x] [Model serving a autoscaling](docs/19-mlops-and-ml-platforms/model-serving-autoscaling.md)
- [x] [GPU scheduling, utilization a capacity](docs/19-mlops-and-ml-platforms/gpu-scheduling-utilization-capacity.md)
- [x] [Model monitoring](docs/19-mlops-and-ml-platforms/model-monitoring.md)
- [x] [Data drift, concept drift a prediction drift](docs/19-mlops-and-ml-platforms/data-drift-concept-drift-prediction-drift.md)
- [x] [Performance, latency, throughput a cost monitoring](docs/19-mlops-and-ml-platforms/performance-latency-throughput-cost-monitoring.md)
- [x] [Feedback loops a ground-truth delay](docs/19-mlops-and-ml-platforms/feedback-loops-ground-truth-delay.md)
- [x] [Model rollback a recovery](docs/19-mlops-and-ml-platforms/model-rollback-recovery.md)
- [x] [Governance, approvals a audit](docs/19-mlops-and-ml-platforms/governance-approvals-audit.md)
- [x] [Privacy, security a adversarial ML](docs/19-mlops-and-ml-platforms/privacy-security-adversarial-ml.md)
- [x] [ML supply-chain security](docs/19-mlops-and-ml-platforms/ml-supply-chain-security.md)
- [x] [MLflow experiment tracking a Model Registry](docs/19-mlops-and-ml-platforms/mlflow-experiment-tracking-model-registry.md)
- [x] [MLflow evaluation, tracing a deployment](docs/19-mlops-and-ml-platforms/mlflow-evaluation-tracing-deployment.md)
- [x] [Kubeflow Pipelines](docs/19-mlops-and-ml-platforms/kubeflow-pipelines.md)
- [x] [Kubeflow Trainer a distributed training](docs/19-mlops-and-ml-platforms/kubeflow-trainer-distributed-training.md)
- [x] [KServe alebo ekvivalentný Kubernetes model serving](docs/19-mlops-and-ml-platforms/kserve-kubernetes-model-serving.md)
- [x] [Amazon SageMaker a cloud MLOps mapping](docs/19-mlops-and-ml-platforms/amazon-sagemaker-cloud-mlops-mapping.md)
- [x] [MLOps platform architecture](docs/19-mlops-and-ml-platforms/mlops-platform-architecture.md)
- [x] [MLOps troubleshooting](docs/19-mlops-and-ml-platforms/mlops-troubleshooting.md)

## Fáza 8 — LLM, GenAI a agentická automatizácia

### LLM and GenAI Engineering

- [x] [Generative AI, foundation model a large language model](docs/20-llm-and-genai-engineering/generative-ai-foundation-model-llm.md)
- [x] [Transformer architecture na praktickej úrovni](docs/20-llm-and-genai-engineering/transformer-architecture-practical.md)
- [x] [Tokens, tokenization a context window](docs/20-llm-and-genai-engineering/tokens-tokenization-context-window.md)
- [x] [Embeddings a semantic similarity](docs/20-llm-and-genai-engineering/embeddings-semantic-similarity.md)
- [x] [Inference parameters, sampling a determinism](docs/20-llm-and-genai-engineering/inference-parameters-sampling-determinism.md)
- [x] [Prompt roles, instructions, context a examples](docs/20-llm-and-genai-engineering/prompt-roles-instructions-context-examples.md)
- [x] [Zero-shot, one-shot a few-shot prompting](docs/20-llm-and-genai-engineering/zero-one-few-shot-prompting.md)
- [x] [Prompt templates, variables a versioning](docs/20-llm-and-genai-engineering/prompt-templates-variables-versioning.md)
- [x] [Prompt decomposition a chain-of-thought boundaries](docs/20-llm-and-genai-engineering/prompt-decomposition-chain-of-thought-boundaries.md)
- [x] [Structured Outputs a schema validation](docs/20-llm-and-genai-engineering/structured-outputs-schema-validation.md)
- [x] [Function calling a tool calling](docs/20-llm-and-genai-engineering/function-calling-tool-calling.md)
- [x] [Model selection a capability/cost trade-offs](docs/20-llm-and-genai-engineering/model-selection-capability-cost-tradeoffs.md)
- [x] [Model version pinning a compatibility](docs/20-llm-and-genai-engineering/model-version-pinning-compatibility.md)
- [x] [Retrieval-Augmented Generation architecture](docs/20-llm-and-genai-engineering/retrieval-augmented-generation-architecture.md)
- [x] [Chunking, metadata a document processing](docs/20-llm-and-genai-engineering/chunking-metadata-document-processing.md)
- [x] [Vector stores a indexing](docs/20-llm-and-genai-engineering/vector-stores-indexing.md)
- [x] [Retrieval, hybrid search a reranking](docs/20-llm-and-genai-engineering/retrieval-hybrid-search-reranking.md)
- [x] [Context assembly a citation grounding](docs/20-llm-and-genai-engineering/context-assembly-citation-grounding.md)
- [x] [RAG evaluation a retrieval diagnostics](docs/20-llm-and-genai-engineering/rag-evaluation-retrieval-diagnostics.md)
- [x] [Fine-tuning, instruction tuning a preference tuning](docs/20-llm-and-genai-engineering/fine-tuning-instruction-preference-tuning.md)
- [x] [PEFT, adapters a LoRA](docs/20-llm-and-genai-engineering/peft-adapters-lora.md)
- [x] [Quantization a local inference](docs/20-llm-and-genai-engineering/quantization-local-inference.md)
- [x] [GPU memory, batching a serving performance](docs/20-llm-and-genai-engineering/gpu-memory-batching-serving-performance.md)
- [x] [Prompt caching, semantic caching a response caching](docs/20-llm-and-genai-engineering/prompt-semantic-response-caching.md)
- [x] [LLM gateways, routing, fallback a rate limiting](docs/20-llm-and-genai-engineering/llm-gateways-routing-fallback-rate-limiting.md)
- [x] [Prompt Registry a lifecycle](docs/20-llm-and-genai-engineering/prompt-registry-lifecycle.md)
- [x] [LLM evaluation datasets a graders](docs/20-llm-and-genai-engineering/llm-evaluation-datasets-graders.md)
- [x] [Human evaluation a expert feedback](docs/20-llm-and-genai-engineering/human-evaluation-expert-feedback.md)
- [x] [Tracing, token usage a cost observability](docs/20-llm-and-genai-engineering/tracing-token-usage-cost-observability.md)
- [x] [Hallucination, faithfulness a factuality](docs/20-llm-and-genai-engineering/hallucination-faithfulness-factuality.md)
- [x] [Prompt injection a indirect prompt injection](docs/20-llm-and-genai-engineering/prompt-injection-indirect-prompt-injection.md)
- [x] [Data exfiltration, tool abuse a excessive agency](docs/20-llm-and-genai-engineering/data-exfiltration-tool-abuse-excessive-agency.md)
- [x] [Guardrails, moderation a output validation](docs/20-llm-and-genai-engineering/guardrails-moderation-output-validation.md)
- [x] [Privacy, retention a provider data controls](docs/20-llm-and-genai-engineering/privacy-retention-provider-data-controls.md)
- [x] [Multimodal models](docs/20-llm-and-genai-engineering/multimodal-models.md)
- [x] [LLMOps a production readiness](docs/20-llm-and-genai-engineering/llmops-production-readiness.md)
- [x] [LLM application troubleshooting](docs/20-llm-and-genai-engineering/llm-application-troubleshooting.md)

### AI Agents and Intelligent Automation

- [x] [Deterministic workflow, probabilistic component a autonomous agent](docs/21-ai-agents-and-intelligent-automation/deterministic-workflow-probabilistic-component-autonomous-agent.md)
- [x] [Agent loop, state, observation, action a termination](docs/21-ai-agents-and-intelligent-automation/agent-loop-state-observation-action-termination.md)
- [x] [Tool calling a tool contracts](docs/21-ai-agents-and-intelligent-automation/tool-calling-tool-contracts.md)
- [x] [Planning, decomposition a replanning](docs/21-ai-agents-and-intelligent-automation/planning-decomposition-replanning.md)
- [x] [Short-term state, long-term memory a external memory](docs/21-ai-agents-and-intelligent-automation/short-term-state-long-term-external-memory.md)
- [x] [Single-agent a multi-agent architecture](docs/21-ai-agents-and-intelligent-automation/single-agent-multi-agent-architecture.md)
- [x] [Supervisor, router a specialist patterns](docs/21-ai-agents-and-intelligent-automation/supervisor-router-specialist-patterns.md)
- [x] [Human-in-the-loop a approval gates](docs/21-ai-agents-and-intelligent-automation/human-in-the-loop-approval-gates.md)
- [x] [Durable execution, retries a resumability](docs/21-ai-agents-and-intelligent-automation/durable-execution-retries-resumability.md)
- [x] [Idempotency a side-effect control](docs/21-ai-agents-and-intelligent-automation/idempotency-side-effect-control.md)
- [x] [Model Context Protocol](docs/21-ai-agents-and-intelligent-automation/model-context-protocol.md)
- [x] [Agent interoperability a protocol evolution](docs/21-ai-agents-and-intelligent-automation/agent-interoperability-protocol-evolution.md)
- [x] [Agent identity, authentication a authorization](docs/21-ai-agents-and-intelligent-automation/agent-identity-authentication-authorization.md)
- [x] [Least privilege pre tools a credentials](docs/21-ai-agents-and-intelligent-automation/least-privilege-tools-credentials.md)
- [x] [Sandboxing a code execution](docs/21-ai-agents-and-intelligent-automation/sandboxing-code-execution.md)
- [x] [Prompt injection cez tools a retrieved content](docs/21-ai-agents-and-intelligent-automation/prompt-injection-tools-retrieved-content.md)
- [x] [Tool poisoning, confused deputy a data exfiltration](docs/21-ai-agents-and-intelligent-automation/tool-poisoning-confused-deputy-data-exfiltration.md)
- [x] [Agent evaluation](docs/21-ai-agents-and-intelligent-automation/agent-evaluation.md)
- [x] [Trajectory, tool-selection a outcome evaluation](docs/21-ai-agents-and-intelligent-automation/trajectory-tool-selection-outcome-evaluation.md)
- [x] [Agent tracing, replay a debugging](docs/21-ai-agents-and-intelligent-automation/agent-tracing-replay-debugging.md)
- [x] [Cost, latency a token budgets](docs/21-ai-agents-and-intelligent-automation/cost-latency-token-budgets.md)
- [x] [Agent reliability, fallback a kill switch](docs/21-ai-agents-and-intelligent-automation/agent-reliability-fallback-kill-switch.md)
- [x] [Multi-tenant isolation](docs/21-ai-agents-and-intelligent-automation/multi-tenant-isolation.md)
- [x] [Agent governance a audit](docs/21-ai-agents-and-intelligent-automation/agent-governance-audit.md)
- [ ] n8n architecture a execution model
- [ ] Triggers, nodes, expressions a data mapping
- [ ] Webhooks a API integrations
- [ ] Credentials, secrets a access control
- [ ] Error workflows, retries a partial execution
- [ ] Idempotency a duplicate-event handling
- [ ] Sub-workflows a reusable workflow contracts
- [ ] Source control a environments
- [ ] Self-hosting s PostgreSQL
- [ ] Queue mode, Redis, workers a scaling
- [ ] Binary data, storage a execution retention
- [ ] n8n monitoring, logs a security audit
- [ ] AI Agent nodes, tools a memory
- [ ] Human approval pre citlivé tool calls
- [ ] RAG a knowledge workflows v n8n
- [ ] Production hardening a troubleshooting
- [ ] Harness AI platform overview
- [ ] DevOps Agent pre pipeline a resource operations
- [ ] Worker Agents v pipelines
- [ ] MCP connectors a external tools
- [ ] AI-assisted pipeline creation a failure analysis
- [ ] Agentický code review, testing a remediation
- [ ] GitOps a release agents
- [ ] Incident triage a evidence collection
- [ ] Policy generation a policy validation
- [ ] Human approval, audit a rollback
- [ ] Vendor lock-in a portability agentických workflowov
- [ ] Workflow engine oproti agent frameworku
- [ ] n8n oproti Temporal, Airflow a Prefect use cases
- [ ] Event-driven automation
- [ ] AI-assisted CI/CD
- [ ] AI-assisted observability a incident response
- [ ] AI-assisted security operations
- [ ] Knowledge assistants a enterprise search
- [ ] Ticket, email a chat automation
- [ ] Autonomous remediation boundaries
- [ ] Evaluation-driven automation lifecycle
- [ ] Intelligent automation troubleshooting

<!-- ACTIVE-AI-ROADMAP:END -->
