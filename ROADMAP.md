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
- [ ] Events, audit, metrics a observability
- [ ] Themes, email templates a localization
- [ ] Keycloak server configuration, hostname a reverse proxy
- [ ] TLS, truststores, cookies, headers a production hardening
- [ ] Database, transactions, connection pools a schema lifecycle
- [ ] Infinispan caches, clustering a session behavior
- [ ] Keycloak Operator a Kubernetes deployment
- [ ] High availability, multi-AZ a multi-cluster trade-offs
- [ ] Backup, restore, realm import/export a disaster recovery
- [ ] Upgrades, migration guides a rollback boundaries
- [ ] Custom providers, SPI a extension lifecycle
- [ ] Securing APIs, microservices a MCP servers cez Keycloak
- [ ] Keycloak performance, sizing a load testing
- [ ] Keycloak troubleshooting
