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
- [ ] Package management
- [ ] journald a logging
- [ ] Storage, mounty a filesystems
- [ ] Memory a CPU fundamentals
- [ ] Linux networking
- [ ] SSH
- [ ] Cron a systemd timers
- [ ] Namespaces
- [ ] cgroups
- [ ] Linux capabilities
- [ ] SELinux a AppArmor
- [ ] Performance a troubleshooting

### Networking and Web Fundamentals

- [ ] OSI a TCP/IP model
- [ ] Ethernet, MAC a ARP
- [ ] IPv4, IPv6 a subnetting
- [ ] Routing a default gateway
- [ ] TCP a UDP
- [ ] Ports a sockets
- [ ] DNS
- [ ] DHCP
- [ ] NAT
- [ ] Firewally
- [ ] Proxy a reverse proxy
- [ ] Load balancing
- [ ] HTTP
- [ ] HTTPS, TLS, certificates a PKI
- [ ] REST APIs a WebSockets
- [ ] Network troubleshooting

### Git and Automation Basics

- [ ] Git object model
- [ ] Working tree, staging area a repository
- [ ] Commit, branch, tag a HEAD
- [ ] Clone, fetch, pull a push
- [ ] Merge a rebase
- [ ] Reset, revert a restore
- [ ] Cherry-pick a stash
- [ ] Konflikty
- [ ] Branching strategies
- [ ] Monorepo vs. multirepo
- [ ] Bash automation
- [ ] PowerShell fundamentals
- [ ] Python for automation
- [ ] YAML, JSON a regular expressions

## Fáza 2 — Quality, delivery a automatizácia

### Testing and Software Quality

- [ ] Verification vs. validation
- [ ] Test pyramid
- [ ] Unit, integration a component tests
- [ ] Contract a API tests
- [ ] End-to-end a acceptance tests
- [ ] Smoke a regression tests
- [ ] Performance, load a stress tests
- [ ] Security a infrastructure tests
- [ ] Static analysis, linting a type checking
- [ ] Code coverage a quality gates
- [ ] Mocks, stubs a fakes
- [ ] Flaky tests a test data
- [ ] Shift-left
- [ ] Shift-right
- [ ] Chaos testing

### CI/CD and Release Engineering

- [ ] Continuous Integration
- [ ] Continuous Delivery
- [ ] Continuous Deployment
- [ ] Pipeline, stage, job a runner
- [ ] Trigger, artifact a cache
- [ ] Environment a promotion
- [ ] Quality gates a approvals
- [ ] Pipeline as Code
- [ ] Reusable a parallel pipelines
- [ ] Artifact versioning
- [ ] Semantic Versioning
- [ ] Release management
- [ ] Recreate deployment
- [ ] Rolling update
- [ ] Blue-green deployment
- [ ] Canary deployment
- [ ] A/B testing
- [ ] Shadow deployment
- [ ] Ring deployment
- [ ] Feature flags
- [ ] Progressive delivery
- [ ] Rollback a roll-forward
- [ ] Databázová kompatibilita počas deploymentu

### GitLab

- [ ] Projects, groups a permissions
- [ ] Merge requests a approvals
- [ ] Protected branches a environments
- [ ] GitLab CI/CD syntax
- [ ] Runners a executors
- [ ] Variables a secrets
- [ ] Artifacts a cache
- [ ] Container a package registry
- [ ] Environments, deployments a releases
- [ ] Security scanning

### Infrastructure as Code and Configuration Management

- [ ] Infrastructure as Code principles
- [ ] Terraform providers, resources a data sources
- [ ] Variables, locals a outputs
- [ ] Expressions a dependency graph
- [ ] Terraform state
- [ ] Remote backend a state locking
- [ ] Modules
- [ ] Lifecycle, import a moved blocks
- [ ] Drift
- [ ] Terraform testing a policy
- [ ] Ansible architecture
- [ ] Inventory
- [ ] Modules, tasks, plays a playbooks
- [ ] Variables, facts a templates
- [ ] Handlers, loops a conditionals
- [ ] Roles a collections
- [ ] Vault
- [ ] Ansible idempotencia
- [ ] Terraform vs. Ansible

## Fáza 3 — Containers, Kubernetes a CKA

### Container Fundamentals and Docker

- [ ] Containers vs. virtual machines
- [ ] Namespaces, cgroups a capabilities
- [ ] OCI image a runtime standards
- [ ] Images, layers a copy-on-write
- [ ] Registries
- [ ] Container networking
- [ ] Container storage
- [ ] Container security
- [ ] Docker architecture
- [ ] Dockerfile
- [ ] Build context a layer cache
- [ ] Multi-stage builds
- [ ] Volumes a bind mounts
- [ ] Docker networks a port publishing
- [ ] Environment variables a health checks
- [ ] Docker Compose
- [ ] BuildKit a Buildx
- [ ] Docker troubleshooting

### Kubernetes

- [ ] Kubernetes architecture
- [ ] API a object model
- [ ] Desired state a reconciliation loops
- [ ] Control plane components
- [ ] Worker node components
- [ ] Pod
- [ ] ReplicaSet
- [ ] Deployment
- [ ] StatefulSet
- [ ] DaemonSet
- [ ] Job a CronJob
- [ ] ConfigMap a Secret
- [ ] ServiceAccount
- [ ] Service a EndpointSlice
- [ ] Ingress a Gateway API
- [ ] Cluster DNS
- [ ] CNI a NetworkPolicy
- [ ] Volumes, PV, PVC a StorageClass
- [ ] Scheduling
- [ ] Requests, limits a QoS
- [ ] Probes
- [ ] Taints, tolerations, affinity a topology
- [ ] HPA a autoscaling
- [ ] RBAC
- [ ] SecurityContext a Pod Security
- [ ] ResourceQuota a LimitRange
- [ ] Cluster installation a lifecycle
- [ ] etcd backup a restore
- [ ] Upgrades
- [ ] Logging, metrics a events
- [ ] Kubernetes troubleshooting

### Helm and CKA

- [ ] Helm chart, template, values a release
- [ ] Template functions a pipelines
- [ ] Named templates
- [ ] Chart dependencies
- [ ] Hooks
- [ ] Upgrade a rollback
- [ ] Helm testing a troubleshooting
- [ ] CKA timed labs
- [ ] CKA troubleshooting drills

## Fáza 4 — Cloud, security a prevádzka

### Cloud and AWS

- [ ] IaaS, PaaS a SaaS
- [ ] Public, private a hybrid cloud
- [ ] Regions a Availability Zones
- [ ] Shared responsibility model
- [ ] Scalability, elasticity a fault tolerance
- [ ] High availability a disaster recovery
- [ ] AWS Organizations a accounts
- [ ] IAM
- [ ] VPC, subnets a route tables
- [ ] Internet Gateway a NAT Gateway
- [ ] Security Groups a Network ACLs
- [ ] EC2 a Auto Scaling
- [ ] Elastic Load Balancing
- [ ] S3, EBS a EFS
- [ ] RDS
- [ ] Route 53 a CloudFront
- [ ] Lambda
- [ ] ECS a EKS
- [ ] CloudWatch a CloudTrail
- [ ] Systems Manager
- [ ] KMS a Secrets Manager
- [ ] AWS Backup
- [ ] Well-Architected Framework
- [ ] Cost management a FinOps

### Observability

- [ ] Monitoring vs. observability
- [ ] Metrics, logs, traces a events
- [ ] Instrumentation a telemetry
- [ ] RED method
- [ ] USE method
- [ ] Golden Signals
- [ ] Prometheus
- [ ] Alertmanager
- [ ] Grafana
- [ ] Loki
- [ ] Elasticsearch alebo OpenSearch
- [ ] Fluent Bit
- [ ] Jaeger a Tempo
- [ ] OpenTelemetry
- [ ] Alert design a alert fatigue
- [ ] Cardinality

### Security and Identity

- [ ] CIA triáda
- [ ] Authentication, authorization a auditing
- [ ] Least privilege
- [ ] IAM a RBAC
- [ ] Active Directory
- [ ] LDAP
- [ ] Kerberos
- [ ] OAuth 2.0
- [ ] OpenID Connect
- [ ] SAML
- [ ] Secrets management
- [ ] Encryption at rest a in transit
- [ ] Vulnerability a patch management
- [ ] Threat modeling
- [ ] Supply-chain security
- [ ] SBOM
- [ ] Image signing
- [ ] Policy as Code
- [ ] Zero Trust

### SRE and Operations

- [ ] Reliability, availability a durability
- [ ] SLI, SLO a SLA
- [ ] Error budgets
- [ ] Toil
- [ ] Capacity planning
- [ ] Incident management
- [ ] On-call a escalation
- [ ] Runbooks a playbooks
- [ ] Root cause analysis
- [ ] Blameless postmortems
- [ ] Backup a restore
- [ ] RPO a RTO
- [ ] Disaster recovery
- [ ] Chaos engineering
- [ ] Operational readiness

## Fáza 5 — Architecture a pokročilé oblasti

### Databases and Distributed Systems

- [ ] Relational vs. non-relational databases
- [ ] Transactions a ACID
- [ ] Indexy, locks a migrations
- [ ] Replication a high availability
- [ ] Backups a point-in-time recovery
- [ ] Connection pooling
- [ ] PostgreSQL, MySQL a Redis
- [ ] Monolith, modular monolith a microservices
- [ ] Synchronous vs. asynchronous communication
- [ ] Message queues a event-driven architecture
- [ ] Service discovery a API gateway
- [ ] Caching
- [ ] CAP theorem
- [ ] Consistency models
- [ ] Leader election a consensus
- [ ] Retry, timeout a circuit breaker
- [ ] Rate limiting
- [ ] Idempotency a backpressure

### GitOps and Platform Engineering

- [ ] Git ako source of truth
- [ ] Pull-based deployment
- [ ] Reconciliation a drift detection
- [ ] Argo CD
- [ ] Flux
- [ ] Application promotion
- [ ] GitOps secrets
- [ ] Internal Developer Platform
- [ ] Platform as a Product
- [ ] Golden paths a paved road
- [ ] Self-service
- [ ] Developer experience
- [ ] Service catalog
- [ ] Guardrails
- [ ] Multi-tenancy
