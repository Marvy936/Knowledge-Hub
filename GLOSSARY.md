# Glossary

Rýchly referenčný index technických pojmov používaných v Knowledge Hube. Glossary nenahrádza plné kapitoly: každé heslo obsahuje stručnú definíciu a odkaz na autoritatívny článok, ak už existuje.

## A/B testing

Riadený experiment porovnávajúci control a treatment variant na súbežných skupinách používateľov podľa vopred definovaných outcome a guardrail metrík. Pozri [A/B testing](docs/05-ci-cd-and-release/a-b-testing.md).

## Abort criterion

Vopred definovaná podmienka, pri ktorej sa rollout alebo experiment okamžite zastaví, pretože dopad prekročil prijateľnú hranicu. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md) a [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Acceptance test

Test overujúci, či systém spĺňa dohodnuté business alebo používateľské acceptance criteria. Môže bežať na API, UI alebo inej vrstve. Pozri [End-to-end a acceptance tests](docs/04-testing-and-quality/end-to-end-and-acceptance-tests.md).

## Accepted condition — Gateway API

Route alebo Gateway status condition indikujúca, že zodpovedný controller prijal resource alebo jeho attachment k parentu podľa class, listener a policy pravidiel. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## Access mode — Kubernetes storage

PV/PVC contract opisujúci podporovaný spôsob mount accessu, napríklad ReadWriteOnce, ReadOnlyMany, ReadWriteMany alebo ReadWriteOncePod; nepredstavuje application-level locking ani databázový clustering. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Access review

Pravidelné alebo event-driven overenie, či principal stále potrebuje pridelené permissions, či ich scope a duration zostávajú primerané a či access možno odstrániť. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## Access token

Credential vydaný authorization serverom a určený pre resource server na vykonanie obmedzených API operácií. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Account

Administratívny záznam identity v konkrétnom systéme, ktorý môže mať vlastný lifecycle, credentials, attributes a permissions. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Account vending — AWS

Automatizovaný proces vytvorenia a baseline konfigurácie nového AWS accountu vrátane OU placementu, identity, loggingu, networku, budgets, guardrails a ownership metadata. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## ACL — Access Control List

Rozšírený model oprávnení nad rámec owner/group/other mode bits. Pozri [Users, groups, permissions, sudo a PAM](docs/01-linux-and-systems/users-groups-permissions-sudo-pam.md).

## Action plugin — Ansible

Control-node plugin, ktorý pripravuje alebo koordinuje vykonanie Ansible action, napríklad spracuje arguments, transfer files alebo remote module result. Pozri [Ansible architecture](docs/07-infrastructure-as-code-and-configuration-management/ansible-architecture.md).

## Actionable alert

Alert, ktorý má jasného ownera, definovaný impact, konkrétnu okamžitú akciu, runbook a spôsob overenia resolution. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Active-active architecture

Architektúra, v ktorej viac lokalít alebo replicas súčasne spracúva production traffic; poskytuje vysokú využiteľnosť redundantnej kapacity, ale vyžaduje consistency, conflict-resolution a split-brain model. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Active deadline — Job

Maximálny celkový čas, počas ktorého môže Kubernetes Job zostať aktívny; po jeho prekročení controller ukončí aktívne Pody a Job označí ako failed. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Active Directory Domain Services — AD DS

Distribuovaná Microsoft directory a identity platforma poskytujúca domains, forests, domain controllers, LDAP, Kerberos/NTLM, DNS-integrated discovery, Group Policy a multimaster replication. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Active-passive architecture

Architektúra, v ktorej primárny component spracúva workload a standby component prevezme úlohu po failover-e; zjednodušuje write ownership za cenu standby driftu a failover latency. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Active series

Time series, ktorá má recent samples a spotrebúva active TSDB memory a metadata resources. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Active stream — Loki

Log stream, do ktorého sa aktuálne zapisujú log entries a ktorý drží ingester state a chunk resources. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Actual state — Kubernetes

Reálny stav clusteru alebo external systému v konkrétnom okamihu, napríklad existujúce Pods, bežiace processes, attached volumes alebo cloud resources; controller ho nemusí okamžite celý pozorovať. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Adaptive sampling — tracing

Sampling model, ktorý priebežne upravuje head-sampling probabilities podľa pozorovaného trafficu a target volume-u. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Add-on compatibility — Kubernetes

Overený vzťah medzi Kubernetes verziou a verziami CNI, CSI, CoreDNS, ingress/Gateway, admission, metrics a ďalších cluster-critical components. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Additional Authenticated Data — AAD

Dáta, ktoré AEAD algoritmus nešifruje, ale cryptographically viaže k ciphertextu a overuje ich integritu, napríklad tenant ID, protocol version alebo record type. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## Additive authorization — Kubernetes RBAC

Authorization model, v ktorom sa výsledné oprávnenia skladajú ako union všetkých matching RoleBindings a ClusterRoleBindings; prísnejšia rola neodoberie permission udelenú iným bindingom. Pozri [RBAC](docs/09-kubernetes/rbac.md).

## Additive NetworkPolicy

Semantika, pri ktorej sa povolený traffic pre Pod skladá ako union pravidiel všetkých matching NetworkPolicies; neexistuje poradie pravidiel ani explicitné deny s vyššou prioritou v štandardnom API. Pozri [CNI a NetworkPolicy](docs/09-kubernetes/cni-networkpolicy.md).

## Address refactoring — Terraform

Zmena resource alebo module addressy pri zachovaní identity toho istého remote objektu, typicky deklarovaná cez `moved` block, aby nevznikol neúmyselný destroy/create. Pozri [Lifecycle, import a moved blocks](docs/07-infrastructure-as-code-and-configuration-management/lifecycle-import-moved-blocks.md).

## Admission control — Kubernetes

Request-time vrstva Kubernetes API, ktorá po authentication a authorization mutuje alebo validuje relevantné create, update a delete requests pred persistence. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## Admission policy

Machine-readable pravidlo vyhodnocované v API admission path-e pred persistence alebo mutation resource-u. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Admission verification

Pre-deployment policy decision, ktorý validuje image digest, signature identity, attestations a environment rules pred prijatím workloadu. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Admission webhook dependency

Synchronous external alebo in-cluster dependency API write pathu, ktorej latency, TLS, availability a failure policy priamo ovplyvňujú matching Kubernetes requests. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## Advanced function — PowerShell

PowerShell function s `[CmdletBinding()]`, common parameters, parameter binding a cmdlet-like error/output správaním. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## Advisory gate

Quality gate, ktorý reportuje výsledok, ale neblokuje ďalší delivery krok. Používa sa pri zavádzaní alebo kalibrácii kontroly. Pozri [Code coverage a quality gates](docs/04-testing-and-quality/code-coverage-and-quality-gates.md).

## Advisory policy — Terraform

Policy as Code pravidlo, ktorého výsledok je viditeľný a auditovaný, ale samo neblokuje plan alebo apply. Používa sa pri kalibrácii alebo nízkom riziku. Pozri [Terraform testing a policy](docs/07-infrastructure-as-code-and-configuration-management/terraform-testing-and-policy.md).

## AEAD

Authenticated Encryption with Associated Data; encryption model poskytujúci confidentiality plaintextu a zároveň integrity a authenticity ciphertextu a voliteľných nešifrovaných metadata. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## Agent Collector

OpenTelemetry Collector nasadený blízko workloadu alebo Node-u na lokálny príjem, enrichment, batching, buffering a forwarding telemetry. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Agentless automation — Ansible

Model, v ktorom Ansible typicky nepotrebuje dlhodobo bežiaceho agenta na managed node a používa existujúci transport alebo API; stále však vyžaduje connection, identity a runtime capabilities. Pozri [Ansible architecture](docs/07-infrastructure-as-code-and-configuration-management/ansible-architecture.md).

## Aggregated ClusterRole

ClusterRole, ktorej rules controller automaticky skladá z iných ClusterRoles označených matching aggregation labels. Pozri [RBAC](docs/09-kubernetes/rbac.md).

## ALB listener rule

Prioritizované Layer 7 pravidlo Application Load Balancera, ktoré vyhodnocuje host, path, header, method, query alebo source-IP conditions a vykoná forward, redirect, fixed-response alebo podporovanú authentication action. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## Alert annotation — Prometheus

Dynamický ľudský context alerting rule, napríklad summary, description, current value alebo runbook URL, ktorý nie je súčasťou alert identity. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Alert as Code

Version-controlled model alerting rules, routing, templates, tests, ownership a runbook references nasadzovaný cez review a automatizovaný pipeline. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Alert condition

Query alebo expression spolu s thresholdom a time semantics, ktoré určujú, kedy alert prejde do active, pending alebo firing stavu. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Alert fatigue

Pokles pozornosti a dôvery spôsobený nadmerným počtom neakčných, duplicitných, flapping alebo nesprávne routovaných notifications. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Alert fingerprint

Stabilný identifikátor Alertmanager alertu odvodený z jeho úplného label setu; používa sa na deduplication a alert identity. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Alert flapping

Opakované rýchle prepínanie alertu medzi firing a resolved stavom spôsobené nestabilným signalom, thresholdom, missing data alebo nedostatočným time windowom. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Alert group — Alertmanager

Množina firing alebo resolved alerts zoskupená podľa `group_by` labels a odosielaná ako jedna notification. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Alert identity

Stabilná identita alert instance odvodená z label setu a používaná na deduplication, grouping, silences a routing. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Alert label — Prometheus

Stabilný key/value atribút alertu používaný na identity, grouping, routing, silences a inhibition. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Alert precision

Podiel alerts, ktoré správne identifikujú relevantný a actionable stav oproti false positives a neakčným notifications. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Alert severity

Klasifikácia požadovanej reakcie a urgency, napríklad page, ticket alebo info, nie iba technická veľkosť nameranej hodnoty. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Alert storm

Veľké množstvo súvisiacich alebo duplicitných alerts a notifications, ktoré zahlcuje Alertmanager, receivers alebo on-call tím. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Alerting rule — Prometheus

PromQL expression vyhodnocovaná Prometheus rule engine-om, ktorá po splnení condition a voliteľného `for` vytvára firing alert. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Alertmanager

Komponent Prometheus ekosystému, ktorý prijíma alerts, deduplikuje ich, zoskupuje, routuje, mutuje a posiela notifications do receivers. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Alertmanager HA

Viac Alertmanager replicas koordinovaných peer meshom a replikáciou silence/notification state-u; zvyšuje dostupnosť, ale negarantuje exactly-once notifications. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Alertmanager notification log

Runtime state používaný Alertmanagerom na deduplication, group timing a rozhodovanie o update/repeat notifications. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Alertmanager peer mesh

Peer-to-peer cluster communication medzi Alertmanager replicas na replikáciu silences a notification state-u. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Alias — YAML

YAML referencia na node označený anchorom. Znižuje duplicitu, ale môže komplikovať tooling a čitateľnosť. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Allowed failure

Pipeline stav, pri ktorom zlyhanie jobu zostane viditeľné, ale neblokuje definovaný downstream alebo celkový pipeline result. Musí mať explicitný dôvod a ownership. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## `allowPrivilegeEscalation`

Container security setting riadiaci možnosť procesu získať nové privileges, na Linuxe typicky cez `no_new_privs` runtime mechanizmus. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## ALPN — Application-Layer Protocol Negotiation

TLS extension, ktorou klient a server počas handshake dohodnú aplikačný protokol, napríklad `http/1.1` alebo `h2`. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## Amazon CloudFront

AWS content-delivery service, ktorá distribuuje a cache-uje content cez global edge locations a smeruje cache misses na nakonfigurované origins. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Amazon CloudWatch

AWS observability služba pre metrics, logs, alarms, dashboards, queries, traces a automated operational reactions. Pozri [CloudWatch a CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## Amazon EBS

Zonálny durable block-storage service pre EC2 a podporované AWS compute služby, sprístupnený ako block device s voliteľným typom, IOPS, throughputom, snapshotmi a encryption. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Amazon EC2

AWS compute služba poskytujúca virtuálne instances s voliteľnou instance family, image, networking, storage, IAM a lifecycle konfiguráciou. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Amazon ECS

AWS-native container orchestrator používajúci clusters, task definitions, tasks, services a capacity providers. Pozri [ECS a EKS](docs/11-cloud-and-aws/ecs-eks.md).

## Amazon EFS

Managed NFS file service poskytujúci shared POSIX filesystem pre viac clients cez mount targets vo VPC. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Amazon EKS

Managed Kubernetes služba poskytujúca AWS-managed Kubernetes control plane a integráciu s AWS networking, identity, compute a storage službami. Pozri [ECS a EKS](docs/11-cloud-and-aws/ecs-eks.md).

## Amazon RDS

Managed relational database service, ktorý spravuje časť database infrastructure, backup, maintenance a failover lifecycle-u, pričom zákazník zostáva zodpovedný za schema, queries, access, data a application recovery. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## Amazon Route 53

AWS authoritative DNS, domain registration, health-check a DNS traffic-steering service s public/private hosted zones a hybrid Resolver capabilities. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Amazon S3

Regional object-storage service ukladajúci objects identifikované bucketom a key, dostupné cez API a podporujúce storage classes, lifecycle, versioning, replication a retention controls. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Ambient capability

Linux capability, ktorú môže proces za presných podmienok zachovať pri `execve()` neprivilegovaného programu. Pozri [Linux capabilities](docs/01-linux-and-systems/linux-capabilities.md).

## AMI — Amazon Machine Image

Versionovateľný EC2 boot-image a block-device contract používaný pri vytváraní nových instances. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Amortized cost — AWS

Cost view, ktorý rozkladá upfront a recurring commitment fees cez obdobie ich benefitu, aby zobrazil ekonomický cost používania namiesto iba cash invoice momentu. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Analyzed SBOM

SBOM odvodená analýzou existujúceho binary, package, image alebo filesystemu bez plnej závislosti na source metadata. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## Analyzer — search

Komponent Lucene-based search engine-u, ktorý tokenizuje a normalizuje text pri indexing alebo query time. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Anchor — YAML

YAML mechanizmus pomenovania node, na ktorý môže odkazovať alias. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Annotated tag

Git tag reprezentovaný samostatným tag objectom s targetom, taggerom, časom, message a voliteľným kryptografickým podpisom. Pozri [Commit, branch, tag a HEAD](docs/03-git-and-automation/commit-branch-tag-head.md).

## Annotation — Grafana

Časovo označený deployment, incident, configuration alebo iný event zobrazený v dashboardoch na koreláciu telemetry so zmenami. Pozri [Grafana](docs/12-observability/grafana.md).

## Annotation — Kubernetes

Neidentifikačné key/value metadata objektu určené pre tool, controller alebo human context, nie na efektívnu selection objects. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Anonymous volume — Docker

Docker-managed volume bez user-defined mena, vytvorené pre konkrétny mount request a schopné prežiť zmazanie containeru; bez explicitného ownershipu a cleanup policy ľahko vzniká orphan state. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## Ansible collection

Versionovaný distribuovateľný balík modules, plugins, roles, playbooks, documentation a ďalšieho executable Ansible contentu. Pozri [Ansible architecture](docs/07-infrastructure-as-code-and-configuration-management/ansible-architecture.md).

## Ansible collection artifact

Versionovaný distribuovateľný balík collection contentu obsahujúci roles, modules, plugins, playbooks, metadata a dokumentáciu, ktorý má byť vytvorený z testovaného commitu a spotrebovaný cez explicitnú verziu. Pozri [Roles a collections](docs/07-infrastructure-as-code-and-configuration-management/roles-and-collections.md).

## Ansible conditional

Expression, typicky v `when`, ktorá rozhoduje, či sa task, block alebo iný podporovaný content vykoná pre konkrétny host a item context. Pozri [Handlers, loops a conditionals](docs/07-infrastructure-as-code-and-configuration-management/handlers-loops-conditionals.md).

## Ansible control node

Systém alebo execution environment, na ktorom beží `ansible-core`, načítava sa inventory a content, plánujú sa tasks a spravujú connections k targets. Pozri [Ansible architecture](docs/07-infrastructure-as-code-and-configuration-management/ansible-architecture.md).

## Ansible facts

Host-scoped runtime údaje objavené o managed node, napríklad OS, addresses, filesystems alebo hardware metadata, dostupné najmä cez `ansible_facts`. Pozri [Variables, facts a templates](docs/07-infrastructure-as-code-and-configuration-management/variables-facts-templates.md).

## Ansible handler

Task zaradený do handler queue na základe notification od tasku, ktorý reportoval zmenu; typicky aplikuje runtime reakciu ako reload alebo restart. Pozri [Handlers, loops a conditionals](docs/07-infrastructure-as-code-and-configuration-management/handlers-loops-conditionals.md).

## `ansible_host`

Connection address alebo hostname použitý Ansible transportom pre inventory host, ktorý môže byť odlišný od jeho logickej identity `inventory_hostname`. Pozri [Inventory](docs/07-infrastructure-as-code-and-configuration-management/inventory.md).

## Ansible idempotencia

Vlastnosť automation runu, pri ktorej opakovanie s rovnakými vstupmi a požadovaným stavom nevykoná ďalšie neplánované zmeny a pravdivo reportuje no-change výsledok. Pozri [Ansible idempotencia](docs/07-infrastructure-as-code-and-configuration-management/ansible-idempotency.md).

## Ansible inventory

Výsledný runtime model hosts, groups, connection metadata a variables vytvorený z jedného alebo viacerých inventory sources. Pozri [Inventory](docs/07-infrastructure-as-code-and-configuration-management/inventory.md).

## Ansible module

Executable automation jednotka implementujúca konkrétnu operáciu a vracajúca štruktúrovaný result, napríklad `changed`, `failed` a module-specific fields. Pozri [Modules, tasks, plays a playbooks](docs/07-infrastructure-as-code-and-configuration-management/modules-tasks-plays-playbooks.md).

## Ansible play

Časť playbooku mapujúca host pattern na ordered tasks, roles, variables, privilege a execution controls. Pozri [Modules, tasks, plays a playbooks](docs/07-infrastructure-as-code-and-configuration-management/modules-tasks-plays-playbooks.md).

## Ansible playbook

YAML dokument obsahujúci jeden alebo viac plays, ktorý zaznamenáva opakovateľný configuration, deployment alebo orchestration workflow. Pozri [Modules, tasks, plays a playbooks](docs/07-infrastructure-as-code-and-configuration-management/modules-tasks-plays-playbooks.md).

## Ansible role

Reusable Ansible capability organizujúca súvisiace defaults, variables, tasks, handlers, templates, files a metadata do definovaného contractu. Pozri [Roles a collections](docs/07-infrastructure-as-code-and-configuration-management/roles-and-collections.md).

## Ansible task

Jedna deklarovaná action s module arguments a execution controls aplikovaná na relevantný host context v playi. Pozri [Modules, tasks, plays a playbooks](docs/07-infrastructure-as-code-and-configuration-management/modules-tasks-plays-playbooks.md).

## Ansible variable

Pomenovaná hodnota použitá na parametrizáciu playbooku, role, inventory, tasku alebo template, ktorej výsledok závisí od source, scope a precedence. Pozri [Variables, facts a templates](docs/07-infrastructure-as-code-and-configuration-management/variables-facts-templates.md).

## Ansible Vault

Mechanizmus šifrovania Ansible variables alebo files pre ochranu citlivého obsahu at rest; nechráni automaticky plaintext počas executionu, logs ani výslednú konfiguráciu na targete. Pozri [Vault](docs/07-infrastructure-as-code-and-configuration-management/vault.md).

## Anycast

Routing model, v ktorom viac lokalít oznamuje rovnakú IP adresu a routing privedie klienta k topologicky preferovanému endpointu. Pozri [Load balancing](docs/02-networking-and-web/load-balancing.md).

## API aggregation — Kubernetes

Mechanizmus rozšírenia Kubernetes API o ďalší API server registrovaný cez `APIService`, odlišný od resource schema uloženého cez CRD. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## API contract

Dohoda o observable API behavior zahŕňajúca paths, methods, schemas, status codes, errors, authentication, compatibility a ďalšie semantics. Pozri [Contract a API tests](docs/04-testing-and-quality/contract-and-api-tests.md).

## API discovery — Kubernetes

Schopnosť klienta zistiť dostupné API groups, versions, resources, scopes a podporované verbs z konkrétneho clusteru. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## API group — Kubernetes

Logická family Kubernetes resource types, napríklad core group alebo `apps`, používaná spolu s API version a kindom. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## API request pipeline — Kubernetes

Sekvencia TLS, authentication, authorization, admission, schema/defaulting/conversion a persistence krokov spracúvajúcich Kubernetes API request. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## API-state RPO

Maximálna prijateľná strata Kubernetes API object zmien medzi posledným použiteľným etcd snapshotom a incidentom. Musí byť koordinovaná s RPO application dát. Pozri [etcd backup a restore](docs/09-kubernetes/etcd-backup-restore.md).

## API test

Runtime test verejného API rozhrania overujúci response, semantics, authorization a side effects. Jeho scope môže byť component, integration alebo E2E. Pozri [Contract a API tests](docs/04-testing-and-quality/contract-and-api-tests.md).

## API version negotiation — Docker

Mechanizmus, ktorým Docker client a Engine vyberú spoločnú podporovanú verziu Engine API; neznamená, že starší server podporuje všetky features novšieho CLI. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## APIService — Kubernetes

Cluster-scoped object registrujúci aggregated API group/version a service, ktorá ju obsluhuje. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## AppArmor profile

Mandatory Access Control profil definujúci povolené paths, execute transitions, capabilities, network operations a ďalšie správanie programu. Pozri [SELinux a AppArmor](docs/01-linux-and-systems/selinux-and-apparmor.md).

## AppArmor profile — Kubernetes

Host-level Linux Security Module profil obmedzujúci filesystem, capability, network a ďalšie operations container procesu podľa Node a runtime podpory. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## Application-consistent backup

Backup vytvorený tak, aby zachoval logicky konzistentný application state, napríklad po flushnutí buffers, filesystem freeze alebo koordinovanom database checkpoint-e. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## application-consistent snapshot

Snapshot vytvorený po koordinovanom flush, quiesce alebo engine-native checkpoint-e tak, aby obnovené dáta reprezentovali validný application transaction state. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Application Load Balancer — ALB

Layer 7 Elastic Load Balancing variant pre HTTP/HTTPS traffic s listener rules, host/path routing, target groups a application health checks. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## Application version — Helm

Version aplikácie deklarovaná chart metadata fieldom `appVersion`; je informačná a nie je automaticky chart version, image tag ani release revision. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Apply test — Terraform

Terraform test run, ktorý vykoná apply proti reálnemu alebo testovaciemu provider environmentu, vyhodnotí assertions a následne sa pokúsi vytvorenú infraštruktúru odstrániť. Pozri [Terraform testing a policy](docs/07-infrastructure-as-code-and-configuration-management/terraform-testing-and-policy.md).

## Approval — CI/CD

Explicitné rozhodnutie oprávnenej identity, ktoré povoľuje merge, promotion, deployment alebo release na základe definovaného rizika a dostupnej evidence. Pozri [Quality gates a approvals](docs/05-ci-cd-and-release/quality-gates-and-approvals.md).

## Approval rule — GitLab

GitLab pravidlo definujúce počet required approvals, eligible users alebo groups a branch/policy scope merge requestu. Pozri [Merge requests a approvals](docs/06-gitlab/merge-requests-and-approvals.md).

## ARP — Address Resolution Protocol

IPv4 protokol mapujúci lokálnu next-hop IP adresu na MAC adresu. Pozri [Ethernet, MAC a ARP](docs/02-networking-and-web/ethernet-mac-arp.md).

## Artifact

Jednoznačne identifikovateľný výstup build procesu určený na testovanie alebo distribúciu. Pozri [Software Development Life Cycle](docs/00-foundations/sdlc.md).

## Artifact — CI/CD

Versionovaný a identifikovateľný výstup pipeline určený na ďalšie overenie, distribúciu alebo deployment. Na rozdiel od cache môže byť súčasťou correctness a release evidence. Pozri [Trigger, artifact a cache](docs/05-ci-cd-and-release/trigger-artifact-cache.md).

## Artifact digest

Content-derived immutable identifikátor artifactu, napríklad SHA-256 digest container image, používaný na presnú väzbu medzi buildom, evidence, promotion a deploymentom. Pozri [Trigger, artifact a cache](docs/05-ci-cd-and-release/trigger-artifact-cache.md).

## Artifact promotion

Presun už vytvoreného a overeného immutable artifactu medzi environmentmi alebo release stages bez jeho opätovného rebuildovania. Pozri [Continuous Delivery](docs/05-ci-cd-and-release/continuous-delivery.md).

## Artifact quarantine

Riadené zablokovanie promotion, pull alebo deploymentu konkrétneho artifact digestu pri zachovaní forensic evidence. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md) a [Image signing](docs/13-security-and-identity/image-signing.md).

## Artifact revocation

Policy decision zneplatňujúci predtým akceptovaný artifact digest, signing identity alebo trust path bez nutnosti odstrániť historickú transparency evidence. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Artifact version

Logical identifier artifactu používaný na komunikáciu release identity alebo compatibility významu. Má byť mapovateľný na konkrétny immutable content digest. Pozri [Artifact versioning](docs/05-ci-cd-and-release/artifact-versioning.md).

## `artifactType` — OCI

OCI manifest field opisujúci semantic media type artifactu, najmä keď config descriptor neposkytuje dostatočnú type informáciu. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Assertion Consumer Service — ACS

Service Provider endpoint prijímajúci a validujúci SAML Response pri browser SSO. Pozri [SAML](docs/13-security-and-identity/saml.md).

## Asset — security

Dáta, systém, identita, služba, konfigurácia, artifact alebo business process, ktorého strata alebo kompromitovanie má hodnotiteľný dopad. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Assume breach

Zero Trust design assumption, že identity, endpoint, workload alebo interná network path môžu byť kompromitované, a preto treba obmedziť trust paths, sessions a blast radius. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## AssumeRole — AWS STS

AWS STS operation, ktorou oprávnený principal prevezme IAM role a získa dočasnú role session s expiration, session identity a effective permissions. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## Assurance — security

Dôkazy a miera dôvery, že navrhnuté security controls sú správne implementované a účinné. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Asymmetric routing

Stav, keď forward a return traffic rovnakého flow používajú rozdielne network paths. Pozri [Routing a default gateway](docs/02-networking-and-web/routing-and-default-gateway.md).

## Asyncio

Python framework pre cooperative asynchronous I/O založený na event loop-e, coroutines a tasks. Pozri [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Atomic write

Zápis cez dočasný súbor, validáciu a atomický rename/replace tak, aby consumer nevidel čiastočný obsah. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md) a [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Attack path

Konkrétna postupnosť krokov, trust-boundary crossings a control failures, ktorými môže threat actor dosiahnuť security impact. Pozri [Threat modeling](docs/13-security-and-identity/threat-modeling.md).

## Attack surface

Súbor rozhraní, vstupov, identities a trust boundaries, cez ktoré môže aktér ovplyvniť systém. Pozri [Security a infrastructure tests](docs/04-testing-and-quality/security-and-infrastructure-tests.md).

## Attack tree

Hierarchický model attacker goalu rozdeleného na alternatívne alebo kombinované podmienky a kroky potrebné na jeho dosiahnutie. Pozri [Threat modeling](docs/13-security-and-identity/threat-modeling.md).

## Attacker model

Explicitný opis schopností, prístupov, motivácie a obmedzení uvažovaného threat actora. Pozri [Threat modeling](docs/13-security-and-identity/threat-modeling.md).

## Attempt rate

Počet technických pokusov o vykonanie operácie za čas vrátane retries; môže byť vyšší než počet logical operations. Pozri [RED method](docs/12-observability/red-method.md).

## Attestation — supply chain

Signed statement, ktorý viaže subject digest na konkrétny predicate a identity vydávajúcu dané tvrdenie. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Attribute-Based Access Control — ABAC

Authorization model používajúci attributes principalu, resource-u, action a environmentu na vytvorenie access decisionu. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Audience — OAuth/OIDC/SAML

Identifier zamýšľaného konzumenta tokenu alebo assertion; musí byť validovaný, aby sa artifact nedal použiť voči inému clientovi alebo resource serveru. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md), [OpenID Connect](docs/13-security-and-identity/openid-connect.md) a [SAML](docs/13-security-and-identity/saml.md).

## Audit record

Časovo označený záznam o tom, kto vykonal akú operáciu, voči ktorému resource-u, odkiaľ a s akým výsledkom. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Authenticated scanning

Vulnerability scanning vykonaný s oprávneným host alebo application accessom, ktorý umožňuje presnejšie zistiť installed packages, configuration a patch state než čisto network-based scan. Pozri [Vulnerability a patch management](docs/13-security-and-identity/vulnerability-and-patch-management.md).

## Authentication

Proces overenia identity alebo kontroly nad authenticatorom pred vytvorením session, tokenu alebo iného authenticated contextu. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Authentication Service — Kerberos AS

Časť KDC, ktorá po počiatočnej authentication vydáva clientovi Ticket-Granting Ticket. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Authenticator

Prostriedok kontrolovaný claimantom a používaný na preukázanie identity, napríklad password, passkey, smart card, certificate alebo cryptographic device. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Authenticity

Vlastnosť umožňujúca dôverovať, že entity, dáta alebo artifacts pochádzajú z deklarovaného a overeného source-u. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Authoritative identity source

Systém považovaný za zdroj pravdy pre existenciu, status, ownera alebo attributes identity, napríklad HR systém alebo service catalog. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Authoritative source — IaC

Systém alebo versionovaný artifact považovaný za rozhodujúcu deklaráciu požadovaného infraštruktúrneho stavu; manuálne runtime zmeny sa voči nemu musia adoptovať, vrátiť alebo explicitne vyriešiť. Pozri [Infrastructure as Code principles](docs/07-infrastructure-as-code-and-configuration-management/infrastructure-as-code-principles.md).

## Authoritative writer

Jediný systém alebo workflow oprávnený meniť konkrétny mutable object alebo attribute; viac writerov vytvára ownership conflict a perpetual drift. Pozri [Terraform vs. Ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md).

## Authorization

Rozhodnutie, či principal smie vykonať konkrétnu action voči konkrétnemu resource-u v danom context-e. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Authorization code

Krátkodobý jednorazový OAuth grant, ktorý client vymieňa na token endpoint-e za access token. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Authorization server

OAuth server, ktorý vyhodnocuje grant, autentizuje relevantných principals a vydáva access a refresh tokens. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Authorization Server Metadata

Štandardizovaný dokument publikujúci issuer, endpoints a supported OAuth capabilities pre bezpečnejšiu client konfiguráciu. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Auto Scaling Group — ASG

EC2 fleet controller udržiavajúci minimum, desired a maximum capacity cez launch template, health evaluation, replacement a scaling policies. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Auto unseal — Vault

Vault model, v ktorom Cloud KMS, HSM alebo iný trusted seal mechanism dešifruje root-key material pri štarte bez manuálneho zadávania Shamir shares. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## automated backup — RDS

RDS-managed backup a transaction-log retention používaný na point-in-time recovery v rámci nakonfigurovaného retention windowu. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## Automated canary analysis

Automatizované vyhodnotenie canary verzie voči baseline podľa technických a business metrík, sample size, observation window a promotion/abort policy. Pozri [Canary deployment](docs/05-ci-cd-and-release/canary-deployment.md).

## Automated promotion

Policy-driven rozhodnutie posunúť artifact alebo rollout do ďalšej fázy bez manuálneho approvalu na základe testov, provenance, health a risk signálov. Pozri [Continuous Deployment](docs/05-ci-cd-and-release/continuous-deployment.md).

## Automatic instrumentation

Instrumentation poskytovaná agentom, runtime hookom, frameworkom alebo knižnicou bez explicitného vytvárania každého signalu v application code. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Automatic rollback

Automatizovaný návrat na predchádzajúcu kompatibilnú verziu po detekcii spoľahlivého failure signálu. Nie je bezpečný pri každej stateful alebo nevratnej zmene. Pozri [Continuous Deployment](docs/05-ci-cd-and-release/continuous-deployment.md).

## Automatic rollback — Helm

Release behavior, pri ktorom Helm po failed upgrade-e vytvorí rollback na predchádzajúcu úspešnú revision podľa version-specific flags; nevracia automaticky databázové ani external side effects. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Automation

Prevod opakovateľného postupu na deterministický, auditovateľný a opakovane vykonateľný mechanizmus. Pozri [Automation Mindset](docs/00-foundations/automation-mindset.md).

## Automation and orchestration — Zero Trust

Cross-cutting capability prepájajúca identity, device, network, workload a data signals s riadenými response actions, napríklad revocation alebo quarantine. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Automation runbook — Systems Manager

Versionovaný YAML alebo JSON workflow obsahujúci sequential Automation actions, parameters, branching, outputs, approvals a AWS resource operations. Pozri [Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## `automountServiceAccountToken`

ServiceAccount alebo Pod setting určujúci, či kubelet automaticky pripojí štandardný ServiceAccount credential projection do Podu. Pozri [ServiceAccount](docs/09-kubernetes/serviceaccount.md).

## Autoscaling feedback loop

Nežiaduca alebo zámerná interakcia viacerých autoscaling controllers a metrics, pri ktorej zmena replicas, requests alebo Node capacity mení vstup ďalšej scaling slučky. Pozri [HPA a autoscaling](docs/09-kubernetes/hpa-autoscaling.md).

## Availability — security

Zabezpečenie včasného a spoľahlivého prístupu k informáciám a službám pre autorizovaných používateľov a procesy. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Availability Zone — AWS

Oddelený infraštruktúrny failure domain v rámci AWS Regionu, pozostávajúci z jednej alebo viacerých fyzických lokalít s nezávislejším power, cooling a networking modelom. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## Available replicas — Kubernetes

Počet replík, ktoré sú Ready a spĺňajú príslušné availability timing podmienky controlleru; nie je totožný s počtom existujúcich alebo Running Podov. Pozri [Deployment](docs/09-kubernetes/deployment.md) a [ReplicaSet](docs/09-kubernetes/replicaset.md).

## AVC — Access Vector Cache

SELinux decision a auditný kontext opisujúci povolenie alebo zamietnutie operácie medzi source a target security contexts. Pozri [SELinux a AppArmor](docs/01-linux-and-systems/selinux-and-apparmor.md).

## Average utilization — HPA

Priemerná resource utilization cieľovej Pod population vyjadrená ako percento resource requestu, používaná napríklad pri CPU HPA. Pozri [HPA a autoscaling](docs/09-kubernetes/hpa-autoscaling.md).

## AWS account

Základná AWS resource ownership, IAM, billing, quota, telemetry a blast-radius boundary s vlastným dvanásťmiestnym account ID. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## AWS Backup

Centralizovaná AWS služba na policy-driven backup, copy, retention, restore, monitoring a audit podporovaných resource types. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## AWS Backup Audit Manager

Capability na hodnotenie backup controls a generovanie compliance evidence pre coverage, frequency, retention, encryption, copies, Vault Lock a restore testing. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## AWS Backup Vault Lock

Ochranný mechanizmus presadzujúci immutable retention pravidlá backup vaultu v governance alebo compliance modeli podľa konfigurácie. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## AWS Budgets

AWS Cost Management capability na sledovanie cost, usage, commitment utilization alebo coverage voči definovaným thresholds s notifications a voliteľnými actions. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## AWS Certified CloudOps Engineer – Associate

Associate-level AWS certifikácia overujúca deployment, management a operations workloads na AWS v oblastiach monitoring/remediation, reliability, automation, security a networking. Pozri [SOA-C03 guide](docs/11-cloud-and-aws/cloudops-engineer-associate-soa-c03.md).

## AWS CloudOps troubleshooting drill

Časovo obmedzený AWS fault-injection scenár s jednou známou primárnou chybou, evidence pathom, minimálnou remediation, hard validation a cleanupom. Pozri [CloudOps troubleshooting drills](docs/11-cloud-and-aws/cloudops-troubleshooting-drills.md).

## AWS CloudTrail

AWS audit služba zaznamenávajúca API a ďalšiu account activity vrátane identity, action, time, request context, resources a výsledku. Pozri [CloudWatch a CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## AWS Cost Anomaly Detection

Capability používajúca modely na identifikovanie neobvyklých spend patterns podľa definovaného monitoru a alert subscription. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## AWS Cost Explorer

Analytická AWS Cost Management vrstva na filtrovanie, grouping, forecasting a analýzu cost a usage vrátane amortized views a optimization reports. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## AWS Cost Optimization Hub

Centralizovaná capability agregujúca a prioritizujúca cost-optimization opportunities naprieč AWS accounts a Regions. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## AWS Data Exports

AWS capability na pravidelný export detailných billing, cost, usage a related datasets do analytického storage a query workflowu. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## AWS Fargate

Service-managed container compute engine pre ECS a EKS, pri ktorom zákazník spravuje workload sizing, identity, networking a application lifecycle bez priamej správy host nodes. Pozri [ECS a EKS](docs/11-cloud-and-aws/ecs-eks.md).

## AWS KMS

Managed cryptographic key service poskytujúca KMS keys, policy/grant authorization a cryptographic operations pre applications a AWS services. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## AWS Lambda

AWS event-driven compute služba, ktorá spúšťa function code v service-managed execution environments a škáluje invocations podľa event a concurrency modelu. Pozri [Lambda](docs/11-cloud-and-aws/lambda.md).

## AWS Organizations

AWS služba na centrálne riadenie kolekcie účtov cez management account, root, OUs, organization policies, consolidated billing a delegated administration. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## AWS Outposts

AWS-managed infrastructure umiestnená v zákazníckej alebo colocation lokalite a prepojená s parent AWS Regionom, určená pre hybridné workloady s locality alebo latency požiadavkami. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## AWS Region

Geografická AWS infraštruktúrna oblasť obsahujúca viac Availability Zones a predstavujúca regionálnu service, data-residency a fault-isolation boundary. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## AWS sandbox account

Izolovaný AWS account určený na laby a experimenty s budget guardrails, bez production dát a s explicitným cleanup lifecycle. Pozri [CloudOps hands-on labs](docs/11-cloud-and-aws/cloudops-hands-on-labs.md).

## AWS Secrets Manager

Managed secret lifecycle služba pre encrypted storage, retrieval, versioning, staging labels, rotation a monitoring credentials a ďalších secret values. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## AWS Shared Responsibility Model

Model rozdeľujúci bezpečnostné a prevádzkové responsibilities medzi AWS ako prevádzkovateľa infraštruktúry a zákazníka ako vlastníka identities, configuration, data a workloadu podľa konkrétnej služby. Pozri [Shared responsibility model](docs/11-cloud-and-aws/shared-responsibility-model.md).

## AWS Systems Manager

AWS operations platforma pre central management managed nodes a AWS resources cez remote commands, sessions, patching, state, inventory, automation a configuration storage. Pozri [Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## AWS Well-Architected Framework

Konzistentný review framework na hodnotenie workloadov podľa šiestich pilierov a vytváranie evidence-driven improvement plánu. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## AWS Well-Architected Tool

AWS služba na dokumentovanie workload reviews, lenses, risk issues, improvement plans, milestones a reports podľa Well-Architected Frameworku. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## AZ ID — AWS

Stabilný identifikátor fyzickej Availability Zone, napríklad `euc1-az2`, konzistentný naprieč AWS accounts a vhodný na cross-account topology koordináciu. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## AZ name — AWS

Account-visible názov Availability Zone, napríklad `eu-central-1a`, ktorého historické písmeno nemusí mapovať na rovnakú fyzickú zónu v rôznych účtoch. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## Back-channel logout

OIDC logout model, pri ktorom OpenID Provider posiela signed logout token priamo backendu Relying Party. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md).

## Backend migration — Terraform

Riadený presun state lineage a snapshots z jedného backendu do druhého so zastavením writers, backupom, overením destination identity a následným planom. Pozri [Remote backend a state locking](docs/07-infrastructure-as-code-and-configuration-management/remote-backend-and-state-locking.md).

## Backend scheduler — Tempo

Tempo component, ktorý plánuje maintenance jobs ako compaction, retention alebo redaction a prideľuje ich backend workers. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Backend worker — Tempo

Tempo component vykonávajúci maintenance jobs pridelené backend schedulerom nad object-storage blocks. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## BackendRef — Gateway API

Typed reference z Route rule na backend resource, typicky Kubernetes Service a port, spolu s voliteľnou weight alebo policy metadata. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## Backfill

Riadené doplnenie alebo transformácia existujúcich dát, typicky v bounded batches s checkpointingom, rate limitom, validáciou a možnosťou pause/resume. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Backing index

Skrytý fyzický index patriaci data streamu; writes smerujú do aktuálneho write backing indexu a searches prechádzajú všetky relevantné generations. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Backoff

Časová stratégia medzi opakovanými pokusmi, často exponenciálne rastúca a doplnená jitterom. Pozri [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Backport

Prenesenie opravy alebo zmeny z novšej vývojovej línie do staršej podporovanej release branch, často pomocou cherry-picku a samostatnej validácie. Pozri [Cherry-pick a stash](docs/03-git-and-automation/cherry-pick-and-stash.md).

## Backpressure

Mechanizmus, ktorým pomalší consumer obmedzí alebo signalizuje producerovi, aby nevytváral neobmedzený buffer a rastúcu latency. Pozri [REST APIs a WebSockets](docs/02-networking-and-web/rest-apis-and-websockets.md).

## Backup and restore — DR

Recovery stratégia, pri ktorej sa náhradné prostredie a state obnovujú zo záloh po incidente; má nízky steady-state cost a typicky vyššie RTO. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Backup plan — AWS

Policy expression určujúci schedule, windows, vault, lifecycle, retention, copy actions a ďalšie backup semantics pre priradené resources. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Backup vault — AWS

Logický container recovery points s vlastnou access policy, encryption, retention, lock a audit boundary. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Baggage — OpenTelemetry

Contextual key/value informácie propagované cez service boundaries spolu s trace contextom; vyžadujú prísny privacy, size a cardinality model. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Bare repository

Git repository bez working tree, používaný typicky ako serverový alebo integračný endpoint. Pozri [Clone, fetch, pull a push](docs/03-git-and-automation/clone-fetch-pull-push.md).

## Base image — Dockerfile

Image reference použitá instruction `FROM` ako počiatočný filesystem a metadata graph build stage-u; je supply-chain a patch-lifecycle dependency. Pozri [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md).

## Baseline Pod Security Standard

Pod Security Standards profil blokujúci známe nebezpečné privilege escalations a host access pri širšej workload kompatibilite než profil Restricted. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## Batch size

Množstvo zmien spracovaných alebo nasadených naraz. Menšie batches znižujú blast radius a skracujú feedback. Pozri [Three Ways of DevOps](docs/00-foundations/three-ways.md).

## BDD — Behavior-Driven Development

Collaboration a discovery prístup používajúci príklady správania a spoločný jazyk na spresnenie požiadaviek; Gherkin je iba jedna možná reprezentácia. Pozri [End-to-end a acceptance tests](docs/04-testing-and-quality/end-to-end-and-acceptance-tests.md).

## Bearer token

Token použiteľný každým držiteľom bez ďalšieho proof-of-possession; jeho leakage predstavuje credential compromise počas platnosti. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## `before-hook-creation` — Helm

Default hook cleanup behavior, pri ktorom Helm pred spustením nového hook resource-u odstráni predchádzajúci resource s rovnakou identity. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Behavioral equivalence — environment

Miera, do akej nižší environment zachováva produkčne relevantné protokoly, konfiguráciu, topology, limits a security behavior aj bez úplnej veľkostnej parity. Pozri [Environment a promotion](docs/05-ci-cd-and-release/environment-and-promotion.md).

## BestEffort QoS

Kubernetes QoS class pre Pod bez CPU a memory requests alebo limits podľa platných QoS calculation pravidiel; scheduler nemá deklarovanú potrebu a Pod je pri resource pressure typicky najzraniteľnejší. Pozri [Requests, limits a QoS](docs/09-kubernetes/requests-limits-qos.md).

## Bind — LDAP

LDAP operation, ktorá nastavuje authentication state connectionu pomocou anonymous, simple alebo SASL mechanismu. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## Bind mount — container

Sprístupnenie existujúceho host filesystem pathu do container mount namespace-u, ktoré vytvára silnú väzbu na host path, permissions, labels a lifecycle. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## Binding — Kubernetes scheduling

Finálny scheduler krok zapisujúci vybraný Node do Podu; po bindingu kubelet na danom Node-e realizuje workload. Pozri [Scheduling](docs/09-kubernetes/scheduling.md).

## Black-box monitoring

Pozorovanie systému zvonka z perspektívy používateľa alebo clienta, napríklad cez HTTP, DNS, TLS alebo end-to-end synthetic test. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Blast radius

Maximálny rozsah používateľov, trafficu, dát, komponentov alebo failure domains, ktoré môže zmena, incident alebo experiment ovplyvniť. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Blended cost — AWS

Cost view používajúci pri niektorých consolidated-billing scenároch priemernú rate naprieč organization family. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Blob — Git object

Nemenný Git object obsahujúci bytes jedného súboru bez filename a path metadata. Pozri [Git object model](docs/03-git-and-automation/git-object-model.md).

## Block builder — Tempo

Component, ktorý konzumuje trace records z durable queue, skladá ich do Parquet blocks a zapisuje do object storage. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Block device

Kernelové zariadenie poskytujúce blokovo adresovaný storage. Pozri [Storage, mounty a filesystems](docs/01-linux-and-systems/storage-mounts-and-filesystems.md).

## `block` — Helm

Go template action, ktorá definuje default named template content a zároveň ho vykreslí; globálna override semantics môže byť menej explicitná než values alebo library-chart contract. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Blocking gate

Quality gate, ktorého neúspech zastaví merge, promotion alebo deployment. Má sa používať pre spoľahlivý signál spojený s neprijateľným rizikom. Pozri [Quality gates a approvals](docs/05-ci-cd-and-release/quality-gates-and-approvals.md).

## Blue-green deployment

Deployment stratégia s dvoma oddelenými produkčne relevantnými targetmi, kde sa nová verzia pripraví v neaktívnej farbe a následne sa na ňu riadene presmeruje traffic. Pozri [Blue-green deployment](docs/05-ci-cd-and-release/blue-green-deployment.md).

## Blue/Green Deployment — RDS

RDS workflow pre vytvorenie synchronizovaného staging environmentu a riadený switchover pri podporovaných engine a configuration zmenách. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## Bootstrap configuration

Minimálna počiatočná konfigurácia potrebná na bezpečné pripojenie targetu k dlhodobému management workflowu, napríklad identity, trusted CA, management transport a inventory registration. Pozri [Terraform vs. Ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md).

## Bootstrap token — kubeadm

Časovo obmedzený credential používaný pri kubeadm node discovery a TLS bootstrap workflowe; musí overovať CA identity a nesmie byť dlhodobo uložený. Pozri [Cluster installation a lifecycle](docs/09-kubernetes/cluster-installation-lifecycle.md).

## Bound ServiceAccount token

Časovo obmedzený ServiceAccount bearer token vytvorený cez TokenRequest API, typicky viazaný na audience a Pod/object identity a projected kubeletom do workloadu. Pozri [ServiceAccount](docs/09-kubernetes/serviceaccount.md).

## Bounded dimension

Telemetry dimension s malým, riadeným a relatívne stabilným počtom možných hodnôt. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Bounding set — capability bounding set

Horná hranica Linux capabilities, ktoré proces a jeho potomkovia môžu získať. Pozri [Linux capabilities](docs/01-linux-and-systems/linux-capabilities.md).

## Branch coverage

Podiel výsledkov rozhodovacích vetiev vykonaných test suite. Poskytuje jemnejší signál než samotná line coverage. Pozri [Code coverage a quality gates](docs/04-testing-and-quality/code-coverage-and-quality-gates.md).

## Branch — Git branch

Pohyblivý ref pod `refs/heads/`, ktorý ukazuje na tip commit. Branch nie je samostatný kontajner súborov ani commitov. Pozri [Commit, branch, tag a HEAD](docs/03-git-and-automation/commit-branch-tag-head.md).

## Branch protection

Serverová policy obmedzujúca aktualizáciu dôležitej branch pomocou controls ako required reviews, CI checks, zákaz force pushu alebo merge queue. Pozri [Branching strategies](docs/03-git-and-automation/branching-strategies.md).

## Branch rule — GitLab

Policy objekt aplikovaný na konkrétny branch alebo pattern, ktorý môže riadiť push, merge, force-push a Code Owner požiadavky. Pozri [Protected branches a environments](docs/06-gitlab/protected-branches-and-environments.md).

## Break-glass access

Oddelený a kontrolovaný emergency access model určený pre stav, keď bežná identity alebo privilege activation cesta nie je dostupná. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## Break-glass access — AWS

Núdzový, oddelene chránený a auditovaný prístup do kritického AWS accountu používaný pri výpadku bežnej identity cesty alebo incidente. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Break-glass policy

Oddelený, časovo obmedzený a auditovaný policy path pre emergency access pri zlyhaní alebo nevhodnosti bežného enforcementu. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Break-glass secret

Silno chránený emergency credential dostupný cez auditovaný a obmedzený recovery postup, po ktorého použití nasleduje kontrola a typicky rotation. Pozri [Vault](docs/07-infrastructure-as-code-and-configuration-management/vault.md).

## Broadcast domain

L2 oblasť, v ktorej sa šíri Ethernet broadcast. Typicky ju oddeľuje router alebo VLAN boundary. Pozri [Ethernet, MAC a ARP](docs/02-networking-and-web/ethernet-mac-arp.md).

## Broken main

Stav, keď hlavná integračná branch nespĺňa povinné build alebo quality gates a nemá byť považovaná za dôveryhodný integračný základ. Pozri [Continuous Integration](docs/05-ci-cd-and-release/continuous-integration.md).

## Brownout

Čiastočné alebo premenlivé zlyhanie dependency, pri ktorom služba odpovedá pomaly, iba niektorým requestom alebo s neúplným výsledkom namiesto úplného outage-u. Brownout často drží resources a spúšťa retry amplification. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Budget action — AWS

Voliteľná automatická action naviazaná na AWS Budget threshold, napríklad policy alebo bounded resource-control operácia podľa podporovaných možností. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Build

Proces transformujúci zdrojové vstupy na spustiteľný alebo distribuovateľný artifact. Pozri [Software Development Life Cycle](docs/00-foundations/sdlc.md).

## Build attestation

Machine-readable statement viazaný na build output digest, napríklad provenance alebo SBOM, používaný na overenie source, build procesu a supply-chain policy. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Build bind mount — Dockerfile

Dočasný bind mount dostupný iba počas `RUN --mount=type=bind`, ktorý sprístupní build context, stage alebo named context bez automatického uloženia mount contentu do výslednej layer. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Build cache — Docker

Znovupoužiteľné výsledky build graph nodes alebo instructions identifikované cache keys a relevantnými inputs, určené na zrýchlenie build-u, nie ako jediný correctness source. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Build context — Docker

Explicitná množina files, directories a metadata dostupná builderu ako source pre `COPY`, `ADD` alebo build mounts; context root nemusí byť directory Dockerfile-u. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Build definition

Versionovaný contract build procesu zahŕňajúci workflow, scripts, toolchain, environment, flags, inputs a target platform. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Build driver — Buildx

Konfigurácia určujúca, kde a ako beží BuildKit backend, napríklad `docker`, `docker-container`, Kubernetes alebo remote driver. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Build exporter — BuildKit

Komponent určujúci výsledný output build-u, napríklad registry image, local Docker image store, OCI artifact, tar alebo local filesystem. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Build frontend — BuildKit

Parser a translator, ktorý premieňa Dockerfile alebo iný build language na interný BuildKit graph. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Build metadata — SemVer

Informácie za znakom `+` v Semantic Versioning verzii, napríklad build number alebo commit SHA. Neovplyvňujú SemVer version precedence. Pozri [Semantic Versioning](docs/05-ci-cd-and-release/semantic-versioning.md).

## Build once

Princíp vytvoriť pre konkrétny source commit jeden immutable artifact a ten istý artifact následne testovať a promovať medzi prostrediami. Pozri [Continuous Integration](docs/05-ci-cd-and-release/continuous-integration.md).

## Build once, promote many

Delivery princíp, pri ktorom sa source zostaví raz do immutable artifactu a rovnaký digest sa overuje a promotionuje cez všetky environments. Pozri [Trigger, artifact a cache](docs/05-ci-cd-and-release/trigger-artifact-cache.md).

## Build platform

Systém vykonávajúci build definitions, získavajúci inputs a vytvárajúci artifacts a provenance; predstavuje kritickú supply-chain trust boundary. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Build provenance

Attestation viažuca artifact digest na builder identity, build type, source revision, inputs a relevantné invocation metadata. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Build SBOM

SBOM generovaná počas build procesu z resolved dependencies, build metadata a vytváraného artifactu. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## Build secret — Dockerfile

Citlivý build-time input sprístupnený cez BuildKit secret mount bez zámerného uloženia do image layer alebo build argumentu; command ho stále nesmie zapísať do outputu, cache alebo logs. Pozri [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md).

## Build stage — Dockerfile

Samostatný build filesystem a graph scope vytvorený instruction `FROM`, ktorý môže slúžiť na kompiláciu, testovanie, export artifacts alebo zostavenie final image-u. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## Build Verification Test

Krátky smoke test nad novým buildom overujúci, či je artifact spustiteľný a vhodný na drahšie testovanie. Pozri [Smoke a regression tests](docs/04-testing-and-quality/smoke-and-regression-tests.md).

## Builder instance — Buildx

Logical Buildx objekt združujúci jeden alebo viac BuildKit nodes, driver, endpoints, podporované platforms a configuration. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Builder node — Buildx

Jedna execution jednotka v builder instance, ktorá poskytuje BuildKit worker capabilities a konkrétne podporované target platforms. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Builder trust domain

Izolovaná bezpečnostná oblasť pre build workloads, cache a credentials; untrusted pull-request buildy nemajú zdieľať release signing alebo production registry oprávnenia. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## BuildKit

Moderný container build backend vykonávajúci dependency graph, content-aware cache, build mounts, exporters, multi-platform outputs a attestations. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Buildx

Docker CLI plugin na správu BuildKit builders a pokročilých build workflows vrátane multi-platform builds, external cache a output exporters. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Bulk API

Search-engine API na odoslanie viacerých indexing/update/delete operations v jednom requeste; response môže obsahovať partial item failures aj pri úspešnom HTTP statuse. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Bulkhead isolation

Rozdelenie resources, queues, threads, tenants, cells alebo accounts do samostatných poolov, aby failure alebo overload jednej skupiny nevyčerpal celý systém. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Burn-rate alert

SLO alert sledujúci rýchlosť spotrebúvania error budgetu oproti tempu, ktoré by vyčerpalo budget v definovanom období. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Burstable QoS

Kubernetes QoS class pre Pod, ktorý nie je Guaranteed a má aspoň niektorý relevantný CPU alebo memory request/limit. Pozri [Requests, limits a QoS](docs/09-kubernetes/requests-limits-qos.md).

## Business Impact Analysis — BIA

Proces určujúci kritické business capabilities, dopad výpadku, maximálne tolerované prerušenie, data-loss toleranciu, dependencies a priority obnovy. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## cache behavior — CloudFront

Ordered distribution rule mapujúca path pattern na origin a definujúca viewer protocol, allowed methods, cache policy, origin request policy, headers a private-content behavior. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Cache — CI/CD

Odstrániteľná optimalizácia pipeline na znovupoužitie dependencies alebo intermediate build dát. Pipeline musí zostať korektná aj pri cache miss alebo eviction. Pozri [Trigger, artifact a cache](docs/05-ci-cd-and-release/trigger-artifact-cache.md).

## Cache-Control

HTTP response/request header definujúci freshness, revalidation, storage a shared/private cache policy. Pozri [HTTP](docs/02-networking-and-web/http.md).

## cache hit ratio — CloudFront

Podiel requests obslúžených z CloudFront cache bez potreby fetchu z originu; ovplyvňuje latency, origin load a cost. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Cache invalidation — Docker build

Stav, keď zmena instruction, parent resultu alebo relevantného inputu zmení cache key a builder musí príslušný graph node znovu vykonať. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Cache key

Identifikátor cache odvodený zo všetkých významných vstupov, napríklad OS, architecture, toolchain version, lockfile hash a build configuration. Pozri [Trigger, artifact a cache](docs/05-ci-cd-and-release/trigger-artifact-cache.md).

## cache key — CloudFront

Kombinácia pathu a vybraných query strings, headers, cookies alebo compression variantu, podľa ktorej CloudFront rozhoduje, či requests zdieľajú cached response. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Cache mount — Dockerfile

Persistentnejší pomocný directory pripojený počas `RUN --mount=type=cache`, napríklad pre compiler alebo package-manager cache; môže byť odstránený a nesmie ovplyvňovať correctness build-u. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Cache poisoning

Stav, keď nedôveryhodný alebo chybný pipeline uloží cache, ktorú neskôr použije dôveryhodnejší workflow, čím môže ovplyvniť build alebo spustiť škodlivý obsah. Pozri [Trigger, artifact a cache](docs/05-ci-cd-and-release/trigger-artifact-cache.md).

## cache policy — CloudFront

Policy určujúca cache-key inputs a minimum, default a maximum TTL pre CloudFront cache behavior. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Calendar versioning

Versioning schéma odvodená primárne z kalendárneho dátumu alebo release cadence, napríklad `2026.07.21`. Pozri [Artifact versioning](docs/05-ci-cd-and-release/artifact-versioning.md).

## Callback plugin — Ansible

Plugin spracúvajúci execution events a výsledky pre console output, logs, profiling alebo external observability integrations. Pozri [Ansible architecture](docs/07-infrastructure-as-code-and-configuration-management/ansible-architecture.md).

## CALMS

DevOps rámec Culture, Automation, Lean, Measurement a Sharing. Pozri [CALMS framework](docs/00-foundations/calms.md).

## Canary analysis

Automatizované alebo riadené porovnanie novej verzie s baseline či kontrolnou skupinou podľa technických a business metrík počas obmedzeného rollout-u. Pozri [Continuous Deployment](docs/05-ci-cd-and-release/continuous-deployment.md).

## Canary cohort

Stabilná skupina requestov, používateľov, tenantov alebo instances vystavená novej verzii pred širšou promotion. Pozri [Canary deployment](docs/05-ci-cd-and-release/canary-deployment.md).

## Canary deployment

Deployment stratégia postupne zvyšujúca produkčnú exposure novej verzie pri súbežnom porovnávaní so stable baseline a explicitných promotion/abort kritériách. Pozri [Canary deployment](docs/05-ci-cd-and-release/canary-deployment.md).

## Canary node pool

Malá skupina Nodes s novou Kubernetes, OS, runtime alebo add-on verziou použitá na overenie compatibility pred širším rolloutom. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Canary release

Postupné sprístupnenie novej verzie malej časti trafficu alebo používateľov s porovnávaním technických a business signálov pred širšou promotion. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Capability-based security

Model, v ktorom držanie konkrétnej obmedzenej capability alebo reference oprávňuje principal vykonať presne definovanú operáciu bez broad ambient authority. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## Capability drop — container

Runtime policy odstraňujúca Linux capabilities z process credential sets, ideálne s defaultom drop-all a explicitným pridaním iba nevyhnutných oprávnení. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Capability — Linux capability

Samostatná časť tradičných root oprávnení, napríklad `CAP_NET_BIND_SERVICE`. Pozri [Linux capabilities](docs/01-linux-and-systems/linux-capabilities.md).

## Capacity cliff

Bod, pri ktorom malé ďalšie zvýšenie demandu spôsobí prudký rast queueing, latency alebo errors, pretože systém vyčerpal effective capacity. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Capacity headroom

Rezervovaná nevyužitá kapacita potrebná na absorpciu burstu alebo presun trafficu pri zlyhaní časti systému, napríklad jednej Availability Zone. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Capacity headroom — observability

Rozdiel medzi aktuálnym demandom alebo využitím a effective capacity po zohľadnení failoveru, limits a unavailable resources. Pozri [USE method](docs/12-observability/use-method.md).

## Capacity Rebalancing — EC2 Auto Scaling

Auto Scaling capability, ktorá môže proaktívne spustiť náhradu Spot Instance pri zvýšenom interruption risku, pričom workload stále potrebuje drain a idempotentný recovery model. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Capacity test

Performance test hľadajúci maximálny udržateľný workload pri definovaných SLO a bezpečnostnej rezerve. Pozri [Performance, load a stress tests](docs/04-testing-and-quality/performance-load-stress-tests.md).

## CAPEC

MITRE Common Attack Pattern Enumeration and Classification; katalóg opakovateľných attack patterns použiteľný ako threat-modeling knowledge source, nie ako náhrada konkrétneho system modelu. Pozri [Threat modeling](docs/13-security-and-identity/threat-modeling.md).

## Capturing group — regex

Časť regular expression uzavretá v zátvorkách, ktorá zachytáva matched substring pre ďalšie spracovanie. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Cardinality

Počet unikátnych hodnôt alebo kombinácií dimensions, ktoré vytvárajú time series, log streams, indexed terms alebo ďalšie telemetry identities. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Cardinality budget

Explicitný limit a očakávaný growth model pre series, streams, indexed values alebo attributes per service, metric, tenant alebo backend. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Cardinality incident

Prevádzkový incident, pri ktorom nekontrolovaný rast telemetry identities alebo indexed values ohrozuje ingestion, memory, storage, query výkon alebo cost. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Cardinality — telemetry

Počet unikátnych kombinácií labels alebo attributes; vysoká alebo neobmedzená cardinality môže výrazne zvýšiť memory, storage, query cost a destabilizovať telemetry pipeline. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Catastrophic backtracking

Patologické správanie backtracking regex engine-u, pri ktorom ambiguous nested pattern spôsobí extrémny čas spracovania non-matching vstupu. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## CEL policy

Policy vyjadrená pomocou Common Expression Language, napríklad v Kubernetes ValidatingAdmissionPolicy alebo MutatingAdmissionPolicy. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Certificate

X.509 objekt viažuci public key na identity claims, validity interval, usage a issuer signature. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## Certificate chain

Postupnosť leaf a intermediate certificates, ktorú klient overuje smerom k dôveryhodnému root CA v trust store. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## Certificate lifecycle — Kubernetes

Riadenie vydania, distribúcie, expirácie, obnovy, reloadu a zrušenia control-plane, etcd, kubelet a administrator certificates. Pozri [Cluster installation a lifecycle](docs/09-kubernetes/cluster-installation-lifecycle.md).

## cgroup — Control group

Kernel mechanizmus na hierarchické zoskupovanie procesov a riadenie ich CPU, memory, I/O a process-count resources. Pozri [cgroups](docs/01-linux-and-systems/cgroups.md).

## Cgroup OOM — container

Ukončenie procesu v dôsledku prekročenia alebo nezvládnutia memory pressure v jeho cgroup boundary, ktoré nemusí znamenať vyčerpanie celej host memory. Pozri [Namespaces, cgroups a capabilities](docs/08-container-fundamentals-and-docker/namespaces-cgroups-capabilities.md).

## Cgroup v2

Unified Linux control-group hierarchy organizujúca procesy a aplikujúca resource accounting, limits a distribution cez controllers ako CPU, memory, I/O a PIDs. Pozri [Namespaces, cgroups a capabilities](docs/08-container-fundamentals-and-docker/namespaces-cgroups-capabilities.md).

## Change budget — Ansible

Explicitný limit alebo allowlist opakovaných zmien povolených pri idempotency teste; všetky ostatné recurring changes sa považujú za chybu alebo drift. Pozri [Ansible idempotencia](docs/07-infrastructure-as-code-and-configuration-management/ansible-idempotency.md).

## Change fail rate

Podiel deploymentov, ktoré spôsobia degradáciu služby a vyžadujú nápravu. Pozri [DORA Metrics](docs/00-foundations/dora-metrics.md).

## Change lead time

Čas od vzniku sledovanej zmeny po jej úspešný deployment do produkcie. Pozri [DORA Metrics](docs/00-foundations/dora-metrics.md).

## Changed state — Ansible

Task result signal `changed: true`, ktorým module alebo custom `changed_when` oznamuje, že target state bol zmenený; používa sa aj na handler notifications. Pozri [Modules, tasks, plays a playbooks](docs/07-infrastructure-as-code-and-configuration-management/modules-tasks-plays-playbooks.md).

## Changelog

Dlhodobý chronologický záznam významných zmien produktu alebo komponentu naprieč releases. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Chaos engineering

Disciplína formulovania a vykonávania kontrolovaných experimentov, ktoré overujú schopnosť systému zachovať prijateľné správanie pri poruchách a neistote. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Chaos testing

Praktická forma riadeného fault experimentu overujúca konkrétnu steady-state hypotézu v definovanom scope s bezpečnostnými kontrolami. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Chargeback — FinOps

Interný model, ktorý finančne priraďuje cloud cost konkrétnemu tímu, produktu, cost centru alebo business ownerovi. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Chart CI pipeline — Helm

Versionovaný validačný workflow od dependency locku, values schema, render matrix a policy checks cez ephemeral cluster install, `helm test`, upgrade/rollback scenár až po publikovanie immutable chart artifactu. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## `Chart.lock`

Helm-generated lock file zachytávajúci resolved dependency graph a digest metadata pre reprodukovateľnú reconstruction dependencies. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Chart-prefixed helper — Helm

Named template pomenovaný s chart-specific prefixom, napríklad `payments.labels`, aby sa znížilo riziko globálnej name collision s parent alebo dependency chartom. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Chart repository — Helm

HTTP repository model pre publikovanie packaged Helm charts a index metadata, alternatívny k OCI registry distribution. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Chart test hook — Helm

Helm test resource spúšťaný príkazom `helm test`, ktorý overuje konkrétny release invariant a reportuje výsledok cez exit status. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Chart version — Helm

Semantic version package contractu uvedená v `Chart.yaml`, ktorá identifikuje konkrétnu verziu templates, defaults, metadata a dependencies. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Check mode — Ansible

Best-effort režim predikcie zmien bez ich vykonania pri modules, ktoré ho podporujú; nie je transakčnou ani saved-plan garanciou. Pozri [Ansible architecture](docs/07-infrastructure-as-code-and-configuration-management/ansible-architecture.md).

## Cherry-pick

Operácia, ktorá aplikuje zmenu vybraného commitu na aktuálny tip a vytvorí nový commit s novým parentom a object ID. Pozri [Cherry-pick a stash](docs/03-git-and-automation/cherry-pick-and-stash.md).

## Child module — Terraform

Reusable Terraform konfigurácia volaná z root alebo iného child modulu cez `module` block; jej resources sú súčasťou graphu a state-u caller root module runu. Pozri [Modules](docs/07-infrastructure-as-code-and-configuration-management/modules.md).

## Child pipeline

Samostatný pipeline run vytvorený parent pipelineom pre component, matrix časť alebo dynamicky generovaný workflow, s explicitnými input/output a failure-propagation pravidlami. Pozri [Reusable a parallel pipelines](docs/05-ci-cd-and-release/reusable-and-parallel-pipelines.md).

## Chunk — Fluent Bit

Interná jednotka zoskupujúca telemetry records na buffering, routing a output flush. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Chunk — Loki

Komprimovaný container log entries jedného streamu za určitý časový interval uložený typicky v object storage. Pozri [Loki](docs/12-observability/loki.md).

## Chunk utilization — Loki

Miera naplnenia Loki chunks; príliš veľa malých streamov vytvára underutilized chunks a zvyšuje storage/index overhead. Pozri [Loki](docs/12-observability/loki.md).

## CI/CD component — GitLab

Versionovaný reusable pipeline contract publikovaný v GitLabe a používaný cez `include:component` s explicitnou verziou, inputs a definovaným behaviorom. Pozri [GitLab CI/CD syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md).

## `CI_JOB_TOKEN`

Krátkodobá GitLab job identity používaná na podporované API, artifact, package, registry alebo cross-project operácie podľa explicitného access modelu. Pozri [Variables a secrets](docs/06-gitlab/variables-and-secrets.md).

## CIA triáda

Základný model bezpečnostných cieľov Confidentiality, Integrity a Availability. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## CIDR — Classless Inter-Domain Routing

Zápis IP prefixu pomocou adresy a počtu network bitov, napríklad `192.0.2.0/24`. Pozri [IPv4, IPv6 a subnetting](docs/02-networking-and-web/ipv4-ipv6-subnetting.md).

## Ciphertext

Výstup encryption operácie, ktorý bez príslušného cryptographic keyu nemá prakticky odhaliť pôvodný plaintext. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## Circuit breaker

Resilience pattern, ktorý po prekročení failure prahu dočasne zastaví calls na zlyhávajúcu dependency a neskôr vykoná kontrolované test requests. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## CISA Zero Trust Maturity Model

Planning model Version 2.0 používajúci päť pillars a tri cross-cutting capabilities na hodnotenie a rozvoj Zero Trust capabilities. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## CKA

Certified Kubernetes Administrator, performance-based Linux Foundation/CNCF certifikácia overujúca praktickú správu a troubleshooting Kubernetes clusterov. Pozri [CKA timed labs](docs/10-helm-and-cka/cka-timed-labs.md).

## CKA troubleshooting drill

Časovo ohraničený fault-injection scenár merajúci root-cause accuracy, minimálnu opravu a hard validation Kubernetes failure-u. Pozri [CKA troubleshooting drills](docs/10-helm-and-cka/cka-troubleshooting-drills.md).

## Claimant

Entita, ktorá sa pokúša preukázať kontrolu nad authenticatorom a byť rozpoznaná ako konkrétny subscriber alebo principal. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Clean-room build

Build vykonaný bez dôvery v existujúcu local alebo external cache, používaný na overenie reproducibility, úplnosti dependencies a absencie skrytých cache assumptions. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Clean-room recovery

Obnova do izolovaného a kontrolovaného prostredia pred production promotion, aby sa overila integrita a zabránilo opätovnému kompromitovaniu obnovených dát. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## ClickOps

Primárna správa infraštruktúry manuálnymi zmenami v UI alebo konzole bez versionovaného, reviewovaného a reprodukovateľného change pathu. Pozri [Infrastructure as Code principles](docs/07-infrastructure-as-code-and-configuration-management/infrastructure-as-code-principles.md).

## Client authentication

Mechanizmus, ktorým confidential OAuth client preukazuje svoju identitu token endpointu, napríklad secretom, private-key JWT alebo mTLS. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Client Credentials grant

OAuth machine-to-machine grant, pri ktorom client získava token vo vlastnom identity kontexte bez používateľskej delegation. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Client — OAuth

Aplikácia požadujúca token a používajúca ho voči resource serveru. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## `CLOSE-WAIT`

TCP state, v ktorom remote peer poslal FIN, ale lokálna aplikácia ešte nezavrela socket. Pozri [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md).

## Closed workload model

Model, v ktorom fixný počet virtual users generuje ďalšiu operáciu až po dokončení predchádzajúcej. Spomalenie systému preto môže znížiť generovaný arrival rate. Pozri [Performance, load a stress tests](docs/04-testing-and-quality/performance-load-stress-tests.md).

## Cloud bursting

Hybridný scaling model, pri ktorom workload dočasne rozšíri capacity z private prostredia do public cloudu; vyžaduje runtime, data, identity, networking a licensing kompatibilitu. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Cloud controller manager

Voliteľný Kubernetes control-plane component spúšťajúci cloud-provider-specific controllers pre Node, route alebo load-balancer integrations podľa platformy. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## Cloud deployment model

Klasifikácia určujúca, kde cloud infraštruktúra beží, komu je určená a ako sa prepája a riadi, napríklad public, private alebo hybrid cloud. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Cloud financial management

Disciplína merania, alokácie, plánovania, kontroly a optimalizácie cloud spendu podľa business value a operational trade-offov. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Cloud portability

Schopnosť presunúť workload medzi prostrediami vrátane source, runtime, data, identity, network, observability a operational contracts, nie iba container image-u. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Cloud service model

Model opisujúci rozdelenie prevádzkovej a bezpečnostnej zodpovednosti medzi providerom a zákazníkom naprieč infraštruktúrou, platformou, aplikáciou a dátami. Pozri [IaaS, PaaS a SaaS](docs/11-cloud-and-aws/iaas-paas-saas.md).

## CloudFront Functions

Lightweight JavaScript edge runtime pre viewer-request a viewer-response transformácie s nízkou latency a obmedzeným execution modelom. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## CloudOps domain gap map

Mapovanie aktuálnych SOA-C03 task statements na existujúce kapitoly, služby, hands-on laby, troubleshooting drilly a zostávajúce vedomostné medzery. Pozri [SOA-C03 guide](docs/11-cloud-and-aws/cloudops-engineer-associate-soa-c03.md).

## CloudOps timed reasoning

Tréning riešenia AWS scenario questions pod časovým limitom cez outcome, constraints, scope, responsibility boundary a operational trade-off. Pozri [CloudOps domain review a timed reasoning](docs/11-cloud-and-aws/cloudops-domain-review-timed-reasoning.md).

## CloudTrail data event

High-volume CloudTrail event pre data-plane operáciu nad vybranými resource types, ktorý sa zapína cez event selectors. Pozri [CloudWatch a CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## CloudTrail Event history

Regionálny recent view management events, typicky za posledných 90 dní, určený na rýchle vyhľadávanie a nie ako dlhodobý central audit archive. Pozri [CloudWatch a CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## CloudTrail management event

CloudTrail event pre control-plane operáciu nad AWS resources alebo account configuration. Pozri [CloudWatch a CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## CloudTrail trail

Configuration zabezpečujúca priebežný výber a delivery CloudTrail events do S3 a voliteľných integrations. Pozri [CloudWatch a CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## CloudWatch alarm

State machine hodnotiaca metric alebo query podľa period, statistic, threshold, evaluation a missing-data pravidiel a voliteľne spúšťajúca actions. Pozri [CloudWatch a CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## CloudWatch dimension

Name-value attribute, ktorý spolu s namespace a metric name identifikuje konkrétnu CloudWatch time series. Pozri [CloudWatch a CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## CloudWatch log group

CloudWatch Logs policy, retention, encryption a access boundary obsahujúca jeden alebo viac log streams. Pozri [CloudWatch a CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## CloudWatch Logs Insights

Query engine na interaktívnu analýzu CloudWatch log events v zadaných log groups a time window. Pozri [CloudWatch a CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## Cluster add-on

Component dopĺňajúci Kubernetes cluster o DNS, networking, storage, metrics, routing, policy alebo inú platformovú schopnosť mimo základného API/control-plane procesu. Pozri [Cluster installation a lifecycle](docs/09-kubernetes/cluster-installation-lifecycle.md).

## Cluster add-on — Kubernetes

Platformová služba nasadená nad core clusterom, napríklad DNS, metrics, ingress/gateway, policy alebo log collection, ktorá nie je automaticky core control-plane componentom. Pozri [Kubernetes architecture](docs/09-kubernetes/kubernetes-architecture.md).

## Cluster bootstrap

Proces vytvorenia prvého funkčného control plane, PKI, etcd, kubeconfigs, bootstrap identity a základných resources pred pripojením Nodes a add-ons. Pozri [Cluster installation a lifecycle](docs/09-kubernetes/cluster-installation-lifecycle.md).

## Cluster decommission

Riadené ukončenie clusteru zahŕňajúce data retention, traffic/DNS, PV a cloud resources, credentials, audit evidence a bezpečné odstránenie hosts. Pozri [Cluster installation a lifecycle](docs/09-kubernetes/cluster-installation-lifecycle.md).

## Cluster DNS — Kubernetes

Cluster add-on poskytujúci DNS records pre Services a vybrané Pod identities a forwardujúci non-cluster queries na upstream resolvery. Pozri [Cluster DNS](docs/09-kubernetes/cluster-dns.md).

## Cluster domain — Kubernetes

DNS suffix cluster-local service discovery namespace-u, často `cluster.local`, ale konfigurovateľný pri vytvorení clusteru. Pozri [Cluster DNS](docs/09-kubernetes/cluster-dns.md).

## Cluster-level logging

Architektúra, ktorá prenáša container, Node a control-plane logs do backendu s lifecycle a retenciou nezávislou od jednotlivých Podov a Nodes. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Cluster-scoped resource — Kubernetes

Kubernetes resource, ktorého identity a API scope nie sú viazané na namespace, napríklad Node, Namespace alebo ClusterRole. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Cluster-wide symptom

Failure pozorovaný naprieč namespaces, Nodes alebo services, ktorý zvyšuje pravdepodobnosť problému v control plane, shared add-on, network, storage alebo external dependency. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## ClusterIP

Stabilná virtuálna Service IP v cluster networku, ktorú Service dataplane mapuje na aktuálne EndpointSlice backendy. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## ClusterIP DNS record

A alebo AAAA record bežného Kubernetes Service-u, ktorý resolve-ne na Service ClusterIP, nie priamo na Pod IP adresy. Pozri [Cluster DNS](docs/09-kubernetes/cluster-dns.md).

## ClusterRole

Cluster-scoped Kubernetes RBAC ruleset pre cluster resources, non-resource URLs alebo reusable namespaced permissions. Pozri [RBAC](docs/09-kubernetes/rbac.md).

## ClusterRole — Kubernetes

Kubernetes RBAC objekt obsahujúci cluster-scoped alebo reusable rules, ktoré možno bindnúť cluster-wide alebo v konkrétnom namespace. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## ClusterRoleBinding

Cluster-scoped RBAC binding udeľujúci ClusterRole permissions subjects naprieč celým cluster scope-om. Pozri [RBAC](docs/09-kubernetes/rbac.md).

## ClusterRoleBinding — Kubernetes

Kubernetes RBAC objekt, ktorý priraďuje ClusterRole principals na úrovni celého clusteru. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Cmdlet

PowerShell command implementovaný podľa jednotného Verb-Noun, parameter binding, object pipeline a error-stream modelu. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## CNA

CVE Numbering Authority; organizácia oprávnená prideľovať CVE IDs a publikovať záznamy pre definovaný scope produktov alebo vulnerabilities. Pozri [Vulnerability a patch management](docs/13-security-and-identity/vulnerability-and-patch-management.md).

## CNI

Container Network Interface specification a plugin contract používaný container runtime-om na vytvorenie, konfiguráciu a odstránenie Pod network interface-u. Pozri [CNI a NetworkPolicy](docs/09-kubernetes/cni-networkpolicy.md).

## CNI `ADD` a `DEL`

CNI lifecycle operácie, ktorými runtime žiada plugin o vytvorenie alebo odstránenie network connectivity a súvisiaceho IPAM state-u pre Pod sandbox. Pozri [CNI a NetworkPolicy](docs/09-kubernetes/cni-networkpolicy.md).

## CNI chaining

Model, v ktorom sa počas jedného Pod network setupu vykoná viac CNI plugins v poradí, napríklad connectivity, port mapping, tuning alebo bandwidth policy. Pozri [CNI a NetworkPolicy](docs/09-kubernetes/cni-networkpolicy.md).

## `coalesce` — Helm

Template function vracajúca prvú non-empty hodnotu zo zoznamu kandidátov podľa Helm/Sprig empty semantics. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Code-based instrumentation

Explicitné použitie telemetry API alebo SDK v application code na zachytenie business semantics, custom metrics, spans, logs alebo events. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Code challenge

PKCE hodnota odvodená z code verifiera a odoslaná v authorization requeste. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Code coverage

Metrika určujúca, ktorá časť kódu bola vykonaná počas testov. Nedokazuje správnosť assertions ani business behavior. Pozri [Code coverage a quality gates](docs/04-testing-and-quality/code-coverage-and-quality-gates.md).

## Code freeze

Časovo alebo rozsahovo obmedzená policy, ktorá pred release povoľuje iba vybrané zmeny. Nemá nahrádzať automatizované kontroly, malé batches a recovery schopnosť. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Code Owner — GitLab

Používateľ alebo skupina priradená k paths v `CODEOWNERS`; pri správnej protected-branch konfigurácii môže byť jej approval required pred merge. Pozri [Merge requests a approvals](docs/06-gitlab/merge-requests-and-approvals.md).

## Code verifier

Náhodná PKCE hodnota uchovaná clientom a predložená pri authorization-code exchange. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Cohort assignment

Deterministické priradenie subjektu do rollout alebo experiment skupiny pomocou stabilnej identity a versionovaného pravidla. Pozri [Canary deployment](docs/05-ci-cd-and-release/canary-deployment.md) a [A/B testing](docs/05-ci-cd-and-release/a-b-testing.md).

## Cold start — Lambda

Invocation, pri ktorom Lambda musí pripraviť nové execution environment a vykonať runtime, extension a static initialization pred handlerom. Pozri [Lambda](docs/11-cloud-and-aws/lambda.md).

## Collection dependency — Ansible

Versionovaný vzťah collection k inej collection, ktorý ovplyvňuje resolved executable content, compatibility a supply-chain risk. Pozri [Roles a collections](docs/07-infrastructure-as-code-and-configuration-management/roles-and-collections.md).

## Collector agent

Telemetry Collector nasadený blízko workloadu alebo Node-u na lokálny príjem, enrichment, batching a export signals. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Collector distribution

Konkrétny build OpenTelemetry Collectora s definovanou množinou receivers, processors, exporters a extensions, napríklad core, contrib, vendor alebo custom distribution. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Collector gateway

Centralizovaná alebo tiered Collector vrstva používaná na routing, policy, tail sampling, tenant isolation a fan-out do backendov. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Collision domain

Oblasť zdieľaného Ethernet média, v ktorej môžu transmissions kolidovať. Pozri [Ethernet, MAC a ARP](docs/02-networking-and-web/ethernet-mac-arp.md).

## Color-specific telemetry

Metrics, logs a traces označené blue/green environmentom a artifact verziou tak, aby bolo možné analyzovať cutover a porovnať správanie oboch farieb. Pozri [Blue-green deployment](docs/05-ci-cd-and-release/blue-green-deployment.md).

## Combinatorial cardinality

Rast počtu telemetry identities spôsobený kombináciou viacerých dimensions, ktorých hodnoty sa navzájom násobia. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Command fluency — CKA

Schopnosť rýchlo a presne používať kubectl, shell, editor a cluster administration commands bez zbytočného hľadania syntaxe. Pozri [CKA timed labs](docs/10-helm-and-cka/cka-timed-labs.md).

## Command injection

Zraniteľnosť, pri ktorej neoverený vstup zmení syntax alebo spustí dodatočný príkaz. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md) a [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Commit object

Git object obsahujúci root tree snapshotu, parent commits, author/committer metadata a commit message. Pozri [Git object model](docs/03-git-and-automation/git-object-model.md).

## Compatibility matrix — deployment

Explicitná tabuľka určujúca, ktoré application, client, event a schema verzie môžu bezpečne koexistovať počas rollout-u a rollback window. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Compensating control

Alternatívny security control použitý na dosiahnutie porovnateľného zníženia risku, keď primárny control nie je možný alebo primeraný. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Complain mode

AppArmor režim, v ktorom sa porušenia profilu logujú, ale neblokujú. Pozri [SELinux a AppArmor](docs/01-linux-and-systems/selinux-and-apparmor.md).

## Completion index — Job

Stabilný index konkrétneho logical completion slotu pri Indexed Job-e, používaný na deterministické rozdelenie batch práce medzi Pody. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Component metrics — Kubernetes

Prometheus-style metrics publikované API serverom, schedulerom, controller-managerom, kubeletom, etcd a ďalšími system components. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Component relationship — SBOM

Machine-readable väzba medzi SBOM elements, napríklad `dependsOn`, `contains`, `generatedFrom` alebo `distributedAs`. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## Component template — search

Reusable časť index template-u obsahujúca mappings, settings alebo aliases pre Elasticsearch/OpenSearch index model podľa produktu. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Component test

Test celého deployovateľného komponentu cez jeho verejné rozhranie, pričom externé dependencies môžu byť nahradené controlled doubles. Pozri [Unit, integration a component tests](docs/04-testing-and-quality/unit-integration-component-tests.md).

## Compose include

Mechanizmus importu ďalšieho Compose application modelu; celý transitive source a jeho privileged mounts, images, networks a commands musia byť auditované. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Compose interpolation

Nahrádzanie `${VARIABLE}` výrazov pri zostavovaní resolved Compose modelu; nie je totožné s environmentom odovzdaným procesu v containeri. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md) a [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Compose merge

Pravidlá kombinovania viacerých Compose files, pri ktorých mappings, sequences a špeciálne fields ako `command`, `entrypoint` alebo `healthcheck.test` môžu mať odlišné merge semantics. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Compose profile

Pomenovaná podmienka aktivujúca optional services, napríklad development alebo debug tooling, bez zmeny core application modelu. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Compose project

Logical application scope, ktorým Docker Compose zoskupuje services, containers, networks, volumes a labels pod spoločnú project identity. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Compose service

Deklaratívna definícia workloadu v Compose modeli, z ktorej môže vzniknúť jedna alebo viac runtime container inštancií. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Compose Specification

Otvorený application-model specification pre multi-container services, networks, volumes, configs, secrets a súvisiace lifecycle metadata. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Compose trust model

Bezpečnostný model, podľa ktorého je Compose file privilegovaná executable configuration schopná spúšťať containers, mountovať host paths, pripájať devices a publikovať ports. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Composite alarm — CloudWatch

CloudWatch alarm kombinujúci boolean stav viacerých underlying alarmov na koreláciu, suppression alebo zníženie alert noise. Pozri [CloudWatch a CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## Compute quota — Kubernetes

ResourceQuota limit agregovaných CPU, memory, ephemeral-storage alebo ďalších deklarovaných requests/limits v namespace. Pozri [ResourceQuota a LimitRange](docs/09-kubernetes/resourcequota-limitrange.md).

## Computed value — Terraform

Hodnota atribútu určená providerom alebo remote API, ktorá nemusí byť známa počas planu a môže sa zobraziť ako `known after apply`. Pozri [Terraform providers, resources a data sources](docs/07-infrastructure-as-code-and-configuration-management/terraform-providers-resources-data-sources.md).

## Concurrency policy — CronJob

Pravidlo `Allow`, `Forbid` alebo `Replace`, ktoré určuje, ako CronJob reaguje, keď má začať nový scheduled run a predchádzajúci Job ešte beží. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Condition-based wait

Čakanie na explicitnú podmienku s deadline namiesto pevného sleepu. Znižuje timing flakiness a zrýchľuje test pri rýchlom výsledku. Pozri [Flaky tests a test data](docs/04-testing-and-quality/flaky-tests-and-test-data.md).

## Condition coverage

Coverage metrika sledujúca, či jednotlivé boolean podmienky nadobudli relevantné true a false výsledky. Pozri [Code coverage a quality gates](docs/04-testing-and-quality/code-coverage-and-quality-gates.md).

## Condition — Kubernetes

Štruktúrovaný status signál s typom, boolean-like stavom, reason, message a transition time, ktorý opisuje aktuálne významný aspekt resource state-u. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Confidentiality

Zachovanie autorizovaných obmedzení prístupu a disclosure informácií. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## ConfigMap

Namespaced Kubernetes API objekt pre necitlivé UTF-8 alebo binary configuration dáta používané Podmi cez environment alebo mounted volumes. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Configuration checksum — Kubernetes

Deterministický hash configuration contentu vložený do Pod template metadata, aby jeho zmena vytvorila novú workload revision a explicitný rollout. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Configuration drift — Terraform

Neželaný rozdiel medzi deklaráciami, ktoré majú reprezentovať rovnaký environment alebo policy, napríklad divergentné branches, repositories alebo neaplikované emergency zmeny. Pozri [Drift](docs/07-infrastructure-as-code-and-configuration-management/drift.md).

## Configuration management

Riadenie požadovaného runtime stavu operačných systémov, aplikácií, zariadení alebo služieb pomocou opakovateľných a overiteľných zmien. Pozri [Terraform vs. Ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md).

## Configuration recreate — container

Nahradenie container instance po zmene runtime environment alebo inej immutable container configuration, pretože už spustený process bežne neprevezme nové hodnoty automaticky. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Conftest

Nástroj používajúci OPA/Rego na testovanie structured configuration, napríklad YAML, JSON alebo Terraform planov, pred runtime enforcementom. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Confused deputy

Situácia, v ktorej privileged komponent vykoná operáciu v prospech nesprávneho alebo neautorizovaného actora pre chýbajúci audience, subject alebo delegation binding. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Congestion control

Transportný mechanizmus upravujúci množstvo dát in flight podľa odhadovanej kapacity a congestion signálov network pathu. Pozri [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md).

## Connection draining

Postup, pri ktorom sa backendu prestane posielať nový traffic, ale existujúce requests alebo connections dostanú čas na dokončenie. Pozri [Load balancing](docs/02-networking-and-web/load-balancing.md).

## connection draining — ELB

Riadené ukončovanie targetu, pri ktorom load balancer prestane posielať nové requests a ponechá existujúce connections alebo requests dobehnúť v rámci deregistration contractu. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## Connection plugin — Ansible

Plugin definujúci transport a remote execution semantics medzi control node a targetom, napríklad SSH, local, WinRM alebo network API connection. Pozri [Ansible architecture](docs/07-infrastructure-as-code-and-configuration-management/ansible-architecture.md).

## Conntrack

State table sledujúca network flows pre stateful firewall a NAT rozhodnutia. Pozri [NAT](docs/02-networking-and-web/nat.md) a [Firewally](docs/02-networking-and-web/firewalls.md).

## Conntrack — container networking

Kernel connection-tracking state používaný firewallom a NAT-om; jeho vyčerpanie alebo nevhodné timeouts môžu spôsobovať dropped nové spojenia medzi containers a externými sieťami. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Consent — OAuth

User-facing authorization interaction zobrazujúca clienta a požadovaný access; nenahrádza server-side policy. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Consistent hashing

Hashing model minimalizujúci množstvo remapovaných keys pri pridaní alebo odstránení backendu. Pozri [Load balancing](docs/02-networking-and-web/load-balancing.md).

## Consolidated billing — AWS

AWS Organizations capability združujúca billing member accounts do centrálneho payer/management scope-u pri zachovaní resource ownershipu v jednotlivých účtoch. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Constraint — Gatekeeper

Kubernetes custom resource, ktorý instanciuje Gatekeeper ConstraintTemplate s konkrétnymi parameters, match scope a enforcement behavior. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## ConstraintTemplate — Gatekeeper

Gatekeeper resource definujúci reusable validation logic a parameter schema pre odvodené Constraints. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Constructed inventory — Ansible

Inventory transformation model vytvárajúci derived variables a groups z existujúcich host metadata pomocou expressions a grouping pravidiel. Pozri [Inventory](docs/07-infrastructure-as-code-and-configuration-management/inventory.md).

## Consumer-driven contract

Kontrakt definovaný consumerom podľa interactions, ktoré reálne potrebuje, a overovaný providerom v jeho pipeline. Pozri [Contract a API tests](docs/04-testing-and-quality/contract-and-api-tests.md).

## Container

Izolovaný runtime process alebo skupina procesov používajúca host kernel a oddelený pohľad na resources cez namespaces, cgroups a ďalšie security controls. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Container bridge network

Network model, v ktorom host-side konce veth pairs pripájajú container network namespaces k Linux bridge-u a následne k host routing, firewall alebo NAT vrstve. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Container drift

Nezdokumentovaná runtime zmena vo writable layeri alebo container configuration, ktorá nie je súčasťou versionovaného image-u alebo deployment modelu a zanikne alebo sa zmení pri recreate. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Container environment

Sada environment variables dostupná runtime procesu po zlúčení image defaults a runtime overrides. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Container escape

Prelomenie container isolation boundary, pri ktorom process získa access k hostu alebo iným workloads. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Container exit code

Numerický status ukončenia PID 1 procesu; musí sa interpretovať spolu so signalom, OOM stavom, daemon/kernel logs a application contractom. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Container image

Versionovaný a typicky content-addressed filesystem a runtime-metadata artifact používaný na vytvorenie container instance; bežne neobsahuje kernel použitý pri runtime. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md) a [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## Container MTU

Maximum Transmission Unit platná na container interface a jeho packet path-e; nesúlad s bridge, tunnel alebo host uplinkom môže spôsobovať partial connectivity a dropped veľké packets. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Container network namespace

Linux network namespace poskytujúci container procesu vlastné interfaces, IP adresy, routes, sockets, loopback a network state view. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Container port

Port, na ktorom process počúva vo svojom network namespace; nemusí byť dostupný z hosta alebo externej siete bez routing alebo port-publishing konfigurácie. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Container runtime

Software vrstva pripravujúca container filesystem, namespaces, cgroups, process a lifecycle podľa runtime configuration alebo štandardu. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Container Runtime Interface — CRI

gRPC contract medzi kubeletom a container runtime implementation pre Pod sandbox, container a image lifecycle. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## Container scanning — GitLab

Security scan konkrétneho container image digestu zameraný najmä na známe vulnerabilities v OS packages a podľa capability scanneru aj ďalšom image obsahu. Pozri [Security scanning](docs/06-gitlab/security-scanning.md).

## Container security baseline

Minimálna kombinácia controls, napríklad trusted digest, non-root user, capability drop, seccomp, LSM policy, read-only root filesystem, resource limits, network segmentation a short-lived identity. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Container volume

Runtime-managed storage object s lifecycle oddeleným od konkrétnej container instance, ktorý môže poskytovať persistence, ale nie automaticky backup, replication alebo multi-host durability. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## containerd — Docker Engine

Container lifecycle a image/snapshot komponent používaný Docker Engine-om na koordináciu tasks, runtime shims, content a snapshots podľa konkrétnej konfigurácie platformy. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Content-addressable storage

Storage model, v ktorom je identita objektu odvodená z jeho typu a obsahu. Git používa tento model pre blobs, trees, commits a tags. Pozri [Git object model](docs/03-git-and-automation/git-object-model.md).

## Content digest

Content-derived immutable identifikátor konkrétnych bytes artifactu, typicky kryptografický hash. Na rozdiel od logical version alebo mutable tagu presne určuje nasadený obsah. Pozri [Artifact versioning](docs/05-ci-cd-and-release/artifact-versioning.md).

## Content negotiation

HTTP mechanizmus, ktorým klient deklaruje preferované representations a server vyberie formát, jazyk alebo encoding. Pozri [HTTP](docs/02-networking-and-web/http.md).

## Context manager — Python

Objekt alebo generator riadiaci vstup a výstup z lifecycle scope, napríklad otvorenie a bezpečné zatvorenie súboru, locku alebo session. Pozri [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Context propagation

Prenos tracing a correlation contextu cez procesy, služby, queues a async boundaries tak, aby bolo možné rekonštruovať end-to-end operáciu. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Context root — Docker build

Root path build contextu, voči ktorému sa vyhodnocujú local source paths v `COPY` a `ADD`, nezávisle od umiestnenia Dockerfile-u. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Context switch

Prechod CPU z vykonávania jedného threadu na iný. Pozri [Memory a CPU fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## Continuous backup — AWS Backup

Backup model, ktorý pri podporovaných resources priebežne zachytáva zmeny a umožňuje point-in-time recovery v retention window. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Continuous Delivery

Schopnosť udržiavať systém a jeho artifacty v stave pripravenom na bezpečný, opakovateľný a auditovateľný produkčný deployment na požiadanie. Pozri [Continuous Delivery](docs/05-ci-cd-and-release/continuous-delivery.md).

## Continuous Deployment

Delivery model, v ktorom každá zmena spĺňajúca automatizované quality a policy podmienky pokračuje bez manuálneho release approvalu do produkcie. Pozri [Continuous Deployment](docs/05-ci-cd-and-release/continuous-deployment.md).

## Continuous diagnostics — Zero Trust

Priebežné získavanie identity, endpoint, workload, network, cloud a application telemetry pre aktualizáciu access contextu a risk decisions. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Continuous Integration

Pracovný a technický model častej integrácie malých zmien do spoločnej hlavnej línie s automatizovaným buildom, kontrolami a rýchlym feedbackom. Pozri [Continuous Integration](docs/05-ci-cd-and-release/continuous-integration.md).

## Continuous rescanning — security

Opakované vyhodnocovanie už známych SBOM components, dependencies alebo image digests po aktualizácii advisory databáz bez potreby source zmeny. Pozri [Security scanning](docs/06-gitlab/security-scanning.md).

## Continuous validation — Terraform

Opakované overovanie infraštruktúrnych invariánt po apply pomocou checks, drift plans, asset policy, security rescanningu alebo runtime verification. Pozri [Terraform testing a policy](docs/07-infrastructure-as-code-and-configuration-management/terraform-testing-and-policy.md).

## Continuous verification — Zero Trust

Opakované alebo event-driven prehodnocovanie identity, posture, session a contextu počas bounded access lifecycle-u namiesto permanentnej dôvery po prvom prihlásení. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Continuous Well-Architected

Integrácia architektúrnych controls, review questions, operational evidence a improvement backlogu do priebežného delivery a operations lifecycle-u. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Contract drift

Rozdiel medzi správaním test double alebo dokumentovaného kontraktu a skutočnou dependency. Pozri [Mocks, stubs a fakes](docs/04-testing-and-quality/mocks-stubs-fakes.md).

## Contract test

Test kompatibility producer/consumer rozhrania bez potreby spustiť celý distribuovaný systém. Pozri [Contract a API tests](docs/04-testing-and-quality/contract-and-api-tests.md).

## Control group — experiment

Skupina používateľov, requestov alebo systémových instances, ktorá nedostane experimentálnu zmenu a poskytuje súbežnú baseline na porovnanie. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Control inheritance — cloud compliance

Použitie provider-managed controls, napríklad physical security alebo hypervisor patchingu, ako zdedenej časti zákazníckeho compliance programu; nezbavuje zákazníka vlastných configuration a process responsibilities. Pozri [Shared responsibility model](docs/11-cloud-and-aws/shared-responsibility-model.md).

## Control plane

Časť systému vytvárajúca stav, podľa ktorého data plane rozhoduje. Pozri [OSI a TCP/IP model](docs/02-networking-and-web/osi-and-tcp-ip-model.md).

## Control-plane endpoint

Stabilná DNS/IP a load-balancer identity, cez ktorú clients a Nodes pristupujú ku Kubernetes API server replicas. Pozri [Cluster installation a lifecycle](docs/09-kubernetes/cluster-installation-lifecycle.md).

## Control-plane failure — AWS

Zlyhanie AWS API alebo management/configuration operácie, pri ktorom môže existujúci workload data plane naďalej fungovať. Pozri [CloudOps domain review a timed reasoning](docs/11-cloud-and-aws/cloudops-domain-review-timed-reasoning.md).

## Control-plane health gate

Súbor podmienok ako API readiness, etcd quorum, Node/add-on health, certificate stav a backup readiness, ktoré musia prejsť pred upgrade alebo zásahom. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Control plane — Kubernetes

Sada komponentov poskytujúca API, persistence, scheduling a reconciliation cluster-wide desired state-u. Pozri [Kubernetes architecture](docs/09-kubernetes/kubernetes-architecture.md).

## Control plane — Zero Trust

Vrstva zodpovedná za identity, policy evaluation, posture, access decisions a vytvorenie alebo ukončenie communication pathu. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Control variant

Referenčný variant experimentu reprezentujúci existujúce alebo baseline správanie, voči ktorému sa hodnotí treatment. Pozri [A/B testing](docs/05-ci-cd-and-release/a-b-testing.md).

## Controlled exposure

Riadené sprístupňovanie release-u alebo feature obmedzenej cohrte s explicitnou artifact, configuration a routing identitou, guardrails a rozhodovacími kritériami. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Controlled reproduction — Docker

Diagnostický postup používajúci pinned image digest, rovnakú platformu a explicitnú runtime configuration, pričom sa mení iba jedna premenná a zachováva evidence. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Controlled reproduction — Kubernetes

Najmenší bezpečný experiment reprodukujúci failure s rovnakou identity, policy, network, storage alebo Node boundary bez zbytočných production side effects. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Controller

Komponent porovnávajúci desired state s aktuálnym stavom a vykonávajúci korekčné akcie. Pozri [Desired State and Reconciliation](docs/00-foundations/desired-state-and-reconciliation.md).

## Controller cache — Kubernetes

Lokálna cache napĺňaná typicky cez list/watch, ktorú controller používa na efektívne reads; môže krátkodobo zaostávať za najnovším persisted stavom. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Controller chaining — Kubernetes

Model, v ktorom vyšší controller vytvára desired state pre nižší resource a ďalšie controllers ho postupne realizujú, napríklad Deployment → ReplicaSet → Pod → kubelet. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## ControllerRevision — Kubernetes

API object uchovávajúci revision metadata workload controllerov, napríklad StatefulSetu, pre rollout history a porovnanie current/update revision. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Convergence — configuration management

Proces, pri ktorom opakované pozorovanie a aplikovanie automation vedie target k stabilnému požadovanému stavu. Pozri [Ansible idempotencia](docs/07-infrastructure-as-code-and-configuration-management/ansible-idempotency.md).

## Cookie

HTTP state token, ktorý server nastaví cez `Set-Cookie` a klient následne posiela podľa domain, path, security a SameSite scope. Pozri [HTTP](docs/02-networking-and-web/http.md).

## Coordinated omission

Measurement chyba, pri ktorej test alebo client nepočíta obdobia, keď systém nevedel prijímať novú prácu, a preto podhodnotí skutočnú latency alebo failure impact. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Copy-on-write — container filesystem

Filesystem model, pri ktorom read-only image layer content zostáva zdieľaný a prvá zmena vytvorí novšiu kópiu alebo záznam vo writable upper layeri. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## Copy-up

Operácia, pri ktorej sa file z read-only lower layeru pri prvom zápise prenesie do writable upper layeru a ďalšie zmeny sa vykonávajú nad touto kópiou. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## CoreDNS

Bežná Kubernetes cluster DNS implementation a extensible DNS server konfigurovaný pluginmi pre Kubernetes records, caching, forwarding, health a ďalšie funkcie. Pozri [Cluster DNS](docs/09-kubernetes/cluster-dns.md).

## Corrective control

Control, ktorý po zistení incidentu opravuje alebo obmedzuje jeho následky. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Correlation ID

Identifikátor používaný na spojenie logs, requests, events alebo ďalších telemetry records patriacich k rovnakej operácii. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## CORS — Cross-Origin Resource Sharing

Browser-enforced HTTP policy určujúca, ktoré origins môžu čítať responses alebo odosielať vybrané cross-origin requests. Pozri [HTTP](docs/02-networking-and-web/http.md).

## Cosign

Sigstore nástroj na signing a verification container images, blobs a supply-chain attestations. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Cost allocation coverage

Podiel cloud spendu, ktorý možno spoľahlivo priradiť podľa accounts, tags, Cost Categories alebo iného allocation modelu. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Cost allocation tag — AWS

Aktivovaný resource tag používaný v AWS billing a cost datasets na grouping, allocation, showback alebo chargeback. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Cost Category — AWS

Business mapping vrstva, ktorá klasifikuje billing line items podľa rules nad accounts, services, tags a ďalšími dimensions. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Cost incident

Neočakávaný alebo nekontrolovaný spend event spôsobený napríklad útokom, retry loopom, autoscalingom, telemetry explóziou alebo chybnou konfiguráciou. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Cost Optimization pillar

Well-Architected pillar zameraný na poskytovanie business value pri efektívnom total cost počas lifecycle-u. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Counter — metric

Monotónne rastúca metric hodnota používaná pre počty udalostí alebo práce; pri analýze sa typicky prevádza na rate alebo increase za časové okno. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## CPU millicore

Kubernetes CPU quantity, kde `1000m` predstavuje jednu CPU jednotku a `250m` štvrtinu CPU. Pozri [Requests, limits a QoS](docs/09-kubernetes/requests-limits-qos.md).

## CPU quota

Cgroup limit maximálneho CPU času v danom period. Po vyčerpaní môže byť workload throttled. Pozri [cgroups](docs/01-linux-and-systems/cgroups.md).

## CPU throttling

Obmedzenie CPU času containeru po vyčerpaní cgroup CPU quota; process nemusí byť ukončený, ale môže mať vyššiu latency a nižší throughput. Pozri [Requests, limits a QoS](docs/09-kubernetes/requests-limits-qos.md).

## Crash-consistent snapshot

Storage snapshot zodpovedajúci stavu po náhlom výpadku napájania bez garancie, že application buffers, transactions alebo koordinované multi-volume dáta boli konzistentne uzavreté. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## `create_before_destroy` — Terraform

Lifecycle rule, ktorá pri replacement operácii žiada vytvorenie nového objektu pred zničením starého, ak platforma, názvy, capacity a dependencies umožnia ich súbežnú existenciu. Pozri [Lifecycle, import a moved blocks](docs/07-infrastructure-as-code-and-configuration-management/lifecycle-import-moved-blocks.md).

## Credential

Dôkaz alebo secret naviazaný na principal, napríklad password, private key, token seed alebo certificate key material. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Credential cache — Kerberos

Client-side store obsahujúci TGT a service tickets pre aktuálnu Kerberos session. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## CRI log

Node-local container stdout/stderr záznam v Container Runtime Interface logging formáte s timestampom, streamom a full/partial markerom. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Critical path — pipeline

Najdlhšia dependency cesta od triggeru po požadovaný výsledok pipeline. Určuje minimálnu možnú duration pri danom grafe bez ohľadu na súčet všetkých job durations. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## Cron

Časový scheduler spúšťajúci príkazy podľa crontab pravidiel. Pozri [Cron a systemd timers](docs/01-linux-and-systems/cron-and-systemd-timers.md).

## Cross-account backup copy

Kópia recovery pointu do oddeleného AWS accountu na zníženie credential a administrative blast radiusu. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Cross-compilation — container build

Vytváranie binary pre target platform odlišnú od build host platformy pomocou toolchainu a automatic platform arguments ako `TARGETOS` a `TARGETARCH`. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Cross-Region backup copy

Kópia recovery pointu do iného AWS Regionu pre regionálnu isolation a disaster-recovery model. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Cross-state contract

Explicitné rozhranie medzi samostatnými Terraform states, typicky cez publikované outputs alebo externý registry, ktoré musí mať ownership, compatibility a access policy. Pozri [Variables, locals a outputs](docs/07-infrastructure-as-code-and-configuration-management/variables-locals-outputs.md).

## Cross-system recovery consistency

Súlad času a verzie obnoveného etcd API state-u, persistent application dát, schema, credentials a external resources. Pozri [etcd backup a restore](docs/09-kubernetes/etcd-backup-restore.md).

## Cross-tool contract

Úzke, versionované rozhranie medzi automation systémami, napríklad Terraform outputs publikované ako inventory metadata pre Ansible, s explicitným ownershipom a compatibility policy. Pozri [Terraform vs. Ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md).

## Crypto-shredding

Zneprístupnenie encrypted dát bezpečným zničením všetkých key copies potrebných na ich decryption; účinnosť závisí od úplného key inventory a backup lifecycle-u. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## Cryptographic agility

Schopnosť inventarizovať a kontrolovane meniť cryptographic algorithms, protocols, parameters, certificates a key mechanisms bez neplánovaného prepisu celého systému. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## Cryptographic BOM — CBOM

Inventory cryptographic algorithms, keys, certificates, protocols a dependencies používaný na crypto governance a migration planning. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## Cryptoperiod

Schválené časové alebo usage obdobie, počas ktorého môže byť cryptographic key použitý na definované operations. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## CSI

Container Storage Interface contract oddeľujúci Kubernetes storage orchestration od vendor-specific provision, attach, mount, resize a snapshot implementation. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## CSR — Certificate Signing Request

Podpísaná žiadosť obsahujúca public key a požadované certificate identity attributes pre CA. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## Current replicas — ReplicaSet

Počet Podov aktuálne pozorovaných ReplicaSet controllerom ako súčasť jeho replica population; nemusí byť zhodný s Ready alebo Available počtom. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Current-state detection — Ansible

Mechanizmus, ktorým module alebo workflow zistí aktuálny stav targetu pred rozhodnutím, či je potrebná zmena. Pozri [Ansible idempotencia](docs/07-infrastructure-as-code-and-configuration-management/ansible-idempotency.md).

## Customer managed key — KMS

KMS key v zákazníckom account-e, ktorého policy, aliases, rotation, enablement, grants a deletion lifecycle spravuje zákazník. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Customer-managed layer

Vrstva služby, ktorej configuration, patching, security, availability alebo recovery zostáva zodpovednosťou zákazníka. Pozri [IaaS, PaaS a SaaS](docs/11-cloud-and-aws/iaas-paas-saas.md).

## Customer responsibility — cloud

Časť service security a operations contractu, ktorú vlastní zákazník, typicky identity, data, application, network configuration, logging, backup a business recovery. Pozri [Shared responsibility model](docs/11-cloud-and-aws/shared-responsibility-model.md).

## CustomResourceDefinition — CRD

Cluster-scoped Kubernetes object, ktorý pridáva nový custom resource type, group/version/schema a scope do API; sám osebe neposkytuje reconciliation logic. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Cutover window

Časový interval, v ktorom sa traffic alebo ownership práce presúva zo starej deployment farby na novú a intenzívne sa sledujú promotion a abort signály. Pozri [Blue-green deployment](docs/05-ci-cd-and-release/blue-green-deployment.md).

## CVE

Common Vulnerabilities and Exposures identifier pre verejne známy vulnerability record; poskytuje spoločný identifikátor, nie kompletný risk score ani dôkaz, že konkrétny asset je exploitable. Pozri [Vulnerability a patch management](docs/13-security-and-identity/vulnerability-and-patch-management.md).

## CVSS v4.0

Common Vulnerability Scoring System version 4.0; štandardizovaný model severity characteristics, ktorý treba kombinovať s exploitation evidence, exposure, asset criticality a business contextom. Pozri [Vulnerability a patch management](docs/13-security-and-identity/vulnerability-and-patch-management.md).

## CycloneDX 1.7

Verzia CycloneDX BOM specification pre components, services, dependency graphs, formulation, vulnerabilities, cryptographic assets a ďalšie transparency data. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## DAC — Discretionary Access Control

Model oprávnení založený najmä na UID/GID, mode bits a ACL. Pozri [SELinux a AppArmor](docs/01-linux-and-systems/selinux-and-apparmor.md).

## Daemon

Dlhšie bežiaci proces poskytujúci systémovú alebo aplikačnú službu bez priamej interaktívnej session. Pozri [systemd, services a daemons](docs/01-linux-and-systems/systemd-services-daemons.md).

## Daemon log — Docker

Log Docker daemon-u a súvisiacich runtime components používaný na diagnostiku startupu, API, storage, networking a container lifecycle failures. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## DaemonSet

Kubernetes workload controller zabezpečujúci Pod na každom eligible Node-e alebo na každom Node-e z vybranej množiny. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## DaemonSet `OnDelete`

Update stratégia, pri ktorej nový DaemonSet Pod template začne platiť pre konkrétny Node až po odstránení starého Podu. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## DaemonSet rolling update

Riadené postupné nahrádzanie DaemonSet Podov novou template revision pri zachovaní nastavenej unavailable alebo surge hranice. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## DAG — CI/CD

Directed Acyclic Graph vyjadrujúci explicitné dependencies medzi jobs. Umožňuje spustiť job hneď po dokončení jeho skutočných upstream dependencies. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## Dark launch

Nasadenie capability do produkčného prostredia bez jej priameho sprístupnenia používateľom, používané na overenie integrácie, capacity alebo prevádzkového správania. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Dashboard as code

Správa dashboard definitions cez version-controlled JSON, provisioning files, API, Terraform, Operator alebo generátor namiesto neauditovaných UI-only zmien. Pozri [Grafana](docs/12-observability/grafana.md).

## Dashboard — Grafana

Usporiadaná množina panels, variables, annotations, links a time settings navrhnutá na konkrétny operational alebo business účel. Pozri [Grafana](docs/12-observability/grafana.md).

## Dashboard link

Odkaz z dashboardu na ďalší dashboard alebo external systém s voliteľným prenosom time range-u a variables. Pozri [Grafana](docs/12-observability/grafana.md).

## Dashboard provisioning

Automatické vytváranie a synchronizácia Grafana dashboards z deklaratívneho source-u, typicky files alebo IaC. Pozri [Grafana](docs/12-observability/grafana.md).

## DAST — Dynamic Application Security Testing

Security testovanie bežiacej aplikácie zvonka cez jej runtime rozhrania. Pozri [Security a infrastructure tests](docs/04-testing-and-quality/security-and-infrastructure-tests.md).

## Data at rest

Dáta uložené v database, filesysteme, object storage, backupe, snapshot-e alebo inom persistentnom médiu. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Data Encryption Key — DEK

Cryptographic key používaný priamo na encryption application dát alebo storage objektu; v envelope-encryption modeli je sám chránený Key Encryption Keyom. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## Data Flow Diagram — DFD

Model external entities, processes, data stores, data flows a trust boundaries používaný na systematickú identifikáciu threats. Pozri [Threat modeling](docs/13-security-and-identity/threat-modeling.md).

## Data frame — Grafana

Normalizovaná štruktúra query výsledku zložená z fields, ktorú Grafana transformuje a vizualizuje. Pozri [Grafana](docs/12-observability/grafana.md).

## Data in transit

Dáta prenášané medzi clientmi, službami, storage systémami alebo telemetry komponentmi. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Data in use

Dáta počas spracovania v process memory, CPU/GPU, temporary files alebo dešifrovanom application contexte. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Data key — KMS

Symmetric key vygenerovaný cez KMS na local encryption dát, poskytovaný ako plaintext pre okamžité použitie a ako encrypted copy na uloženie. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Data link — Grafana

Odkaz naviazaný na konkrétnu field hodnotu, napríklad trace ID, Pod, error code alebo deployment revision. Pozri [Grafana](docs/12-observability/grafana.md).

## Data plane

Časť systému spracúvajúca konkrétne frames alebo packets podľa existujúceho forwarding a policy stavu. Pozri [OSI a TCP/IP model](docs/02-networking-and-web/osi-and-tcp-ip-model.md).

## Data-plane failure — AWS

Zlyhanie reálneho workload trafficu, request processingu, storage I/O alebo DNS/network cesty napriek potenciálne funkčnému AWS management API. Pozri [CloudOps domain review a timed reasoning](docs/11-cloud-and-aws/cloudops-domain-review-timed-reasoning.md).

## Data plane — Zero Trust

Vrstva prenášajúca actual application alebo data traffic po tom, čo control plane pripravil a PEP presadil access decision. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Data portability

Schopnosť exportovať dáta, metadata a configuration zo služby do použiteľného formátu a obnoviť ich v inom prostredí bez neprimeranej straty alebo downtime-u. Pozri [IaaS, PaaS a SaaS](docs/11-cloud-and-aws/iaas-paas-saas.md).

## Data source — Grafana

Plugin a configuration umožňujúca Grafane queryovať externý metrics, logs, traces, SQL, cloud alebo iný backend. Pozri [Grafana](docs/12-observability/grafana.md).

## Data-source-managed alert

Alert rule uložená a vyhodnocovaná v Prometheus, Mimir, Loki alebo inom podporovanom ruler systéme, pričom Grafana poskytuje management UI. Pozri [Grafana](docs/12-observability/grafana.md).

## Data-source plugin

Grafana plugin implementujúci query, authentication, health-check a data-frame integration pre konkrétny backend. Pozri [Grafana](docs/12-observability/grafana.md).

## Data source — Terraform

Provider-defined read-only query, ktorá načíta informácie o existujúcom alebo odvodenom objekte bez správy jeho lifecycle Terraform resource bindingom. Pozri [Terraform providers, resources a data sources](docs/07-infrastructure-as-code-and-configuration-management/terraform-providers-resources-data-sources.md).

## Data Stream Lifecycle — Elasticsearch

Elasticsearch lifecycle mechanizmus na retention a správu backing indexes data streamu podľa podporovaného deployment modelu. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Data stream — search

Logical abstraction nad rolling backing indexes optimalizovaná pre timestamped a prevažne append-only data ako logs, events a metrics. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Dataclass — Python

Deklaratívny Python model generujúci metódy pre dátovo orientovanú class, napríklad constructor, equality a representation. Pozri [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## DB instance — RDS

Konkrétne managed database environment s engine, instance class, storage, network, parameter a backup configuration. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## DB parameter group — RDS

Versionovateľná sada engine parameters priradená DB instance alebo clusteru, s dynamic alebo reboot-required semantics podľa konkrétneho parameteru. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## DB snapshot — RDS

Customer-retained point-in-time storage snapshot RDS database používaný na restore, migration alebo dlhšiu retenciu mimo automated-backup lifecycle-u. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## DB subnet group — RDS

Kolekcia VPC subnets vo viacerých Availability Zones, z ktorej RDS vyberá database placement. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## DC locator

AD DS proces, ktorým client pomocou DNS, site informácií a ďalších pravidiel nájde vhodný domain controller. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Debug container — Kubernetes

Ephemeral container pridaný do existujúceho Podu na diagnostiku pomocou schváleného debug image-u, RBAC a auditu. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Decision log — policy

Audit event zachytávajúci policy query, result, policy revision, decision ID, relevantný context a PDP instance. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Declarative configuration

Konfigurácia opisujúca požadovaný výsledný stav, nie sekvenciu krokov. Pozri [Declarative vs. Imperative Approach](docs/00-foundations/declarative-vs-imperative.md).

## Declarative policy

Policy opisujúca požadovaný decision alebo invariant bez imperatívneho control flow-u, typicky nad structured inputom a data. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Dedicated Node pool

Množina Nodes určená pre konkrétny workload alebo trust tier, typicky chránená kombináciou taintu, toleration, labelu a required node affinity. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Default backend — Ingress

Backend Service použitý pre requests, ktoré nezodpovedajú žiadnemu host/path pravidlu Ingressu. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## Default deny

Security policy, pri ktorej sa povoľuje iba explicitne definovaný traffic alebo operácie a všetko ostatné sa zamietne. Pozri [Firewally](docs/02-networking-and-web/firewalls.md).

## Default deny — NetworkPolicy

Policy pattern vyberajúci všetky Pody v namespace a nepovoľujúci žiadny traffic pre deklarovaný ingress alebo egress smer, kým ho nepovolí iná additive policy. Pozri [CNI a NetworkPolicy](docs/09-kubernetes/cni-networkpolicy.md).

## Default deny — policy

Combining alebo fallback semantics, pri ktorých neznámy, undefined alebo explicitne nepovolený prípad končí odmietnutím. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## `default` — Helm

Template function vracajúca fallback, keď input je považovaný za empty; pri explicitnom `false` alebo `0` môže zmeniť zamýšľaný význam. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Default route

Najmenej špecifická route `0.0.0.0/0` alebo `::/0`, použitá ak neexistuje presnejšia route. Pozri [Routing a default gateway](docs/02-networking-and-web/routing-and-default-gateway.md).

## Default ServiceAccount

ServiceAccount automaticky vytvorený v každom namespace a použitý Podom, ktorý nemá explicitné `serviceAccountName`; nemá byť zdieľanou privilegovanou workload identity. Pozri [ServiceAccount](docs/09-kubernetes/serviceaccount.md).

## Default StorageClass

StorageClass označená clusterom ako default pre PVCs bez explicitného `storageClassName`; zmena defaultu môže zmeniť cost, topology a lifecycle nových volumes bez zmeny workload manifestu. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## `define` — Helm

Go template action deklarujúca named template pod globálnym menom bez okamžitého render outputu. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Degraded access mode — Zero Trust

Explicitný obmedzený access model počas outage-u identity, posture, policy alebo enforcement dependency, napríklad bounded existing sessions alebo low-risk read-only operations. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Delegated administrator — AWS Organizations

Member account zaregistrovaný na centralizovanú správu podporovanej AWS služby naprieč organization, aby sa znížil počet operácií vykonávaných v management account-e. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Delegation — identity

Kontrolované odovzdanie obmedzenej authority z jedného principalu na iný principal alebo service. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## delete marker — S3

Špeciálna current version vytvorená pri delete requeste vo versioning-enabled buckete, ktorá skryje predchádzajúcu object version bez jej okamžitého odstránenia. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Deletion timestamp — Kubernetes

Serverom nastavený čas označujúci, že object bol prijatý na deletion a čaká na graceful termination alebo finalizer cleanup. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Demand unit

Workload-specific jednotka trafficu, napríklad request, message, transaction, byte, query alebo inference, ktorá reprezentuje reálny demand na systém. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Dependency alias — Helm

Local identity dependency chartu umožňujúca použiť rovnaký chart viackrát s oddelenými values a resource-name contracts. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Dependency condition — Helm

Boolean values path v dependency declaration, ktorý povoľuje alebo zakazuje načítanie konkrétneho subchartu. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Dependency confusion

Supply-chain attack, pri ktorom dependency resolver vyberie attacker-controlled package z iného registry alebo namespace namiesto zamýšľaného interného package-u. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Dependency constraint — Helm

Exact SemVer alebo version range v `Chart.yaml`, podľa ktorého `helm dependency update` vyberá kompatibilnú dependency version. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Dependency cycle — Terraform

Kruhový vzťah v dependency grafe, pri ktorom objekt priamo alebo nepriamo závisí sám od seba a Terraform nevie zostaviť bezpečné execution poradie. Pozri [Expressions a dependency graph](docs/07-infrastructure-as-code-and-configuration-management/expressions-and-dependency-graph.md).

## Dependency graph — Terraform

Directed graph vytvorený z references, provider vzťahov a explicitných dependencies, ktorý určuje plan/apply poradie a možnú paralelizáciu objektov. Pozri [Expressions a dependency graph](docs/07-infrastructure-as-code-and-configuration-management/expressions-and-dependency-graph.md).

## Dependency lock

Presne vyriešený zoznam versions priamych a transitívnych dependencies určený na reprodukovateľnú inštaláciu. Pozri [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Dependency lock file — Terraform

Súbor `.terraform.lock.hcl` zachytávajúci vybrané provider versions a package checksums pre reprodukovateľnejšiu inštaláciu dependencies. Pozri [Terraform providers, resources a data sources](docs/07-infrastructure-as-code-and-configuration-management/terraform-providers-resources-data-sources.md).

## Dependency RED

Rate, Errors a Duration merané pre outbound dependency calls, používané na oddelenie vlastného service behavior od downstream degradácie. Pozri [RED method](docs/12-observability/red-method.md).

## Dependency scanning — GitLab

Analýza direct a transitive software dependencies podľa manifestov, lockfiles alebo SBOM a ich porovnanie s vulnerability advisory databázou. Pozri [Security scanning](docs/06-gitlab/security-scanning.md).

## Dependency scope — SBOM

Klasifikácia účelu componentu, napríklad runtime, development, test, optional, build-only alebo externally provided. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## Dependency tag — Helm

Label priradený jednej alebo viacerým dependencies, ktorý umožňuje ich skupinové enable/disable cez top-level `tags` values. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Deployable state

Stav, v ktorom existuje dôveryhodný immutable artifact, potrebné dôkazy, kompatibilná konfigurácia, deployment automation, observability a recovery plán umožňujúci bezpečný deployment. Pozri [Continuous Delivery](docs/05-ci-cd-and-release/continuous-delivery.md).

## Deployed SBOM

Inventory komponentov viazaný na artifact alebo system nasadený v konkrétnom environment kontexte. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## Deployment

Kubernetes workload controller, ktorý deklaratívne riadi ReplicaSety a rollout zameniteľných Podov. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## Deployment downtime

Čas, počas ktorého deployment spôsobí úplnú alebo neprijateľnú nedostupnosť služby. Pri recreate zahŕňa shutdown, deployment, startup, migrations, readiness a routing. Pozri [Recreate deployment](docs/05-ci-cd-and-release/recreate-deployment.md).

## Deployment freeze — GitLab

Časovo definovaná GitLab policy obmedzujúca plánované deploymenty do citlivého environmentu, s explicitným emergency a exception modelom. Pozri [Environments, deployments a releases](docs/06-gitlab/environments-deployments-releases.md).

## Deployment frequency

Ako často služba úspešne nasadzuje zmeny do produkcie. Pozri [DORA Metrics](docs/00-foundations/dora-metrics.md).

## Deployment lock

Mechanizmus serializujúci alebo koordinujúci mutations jedného environmentu, aby sa paralelné deploymenty navzájom neprepísali alebo nevytvorili nekonzistentný stav. Pozri [Environment a promotion](docs/05-ci-cd-and-release/environment-and-promotion.md).

## Deployment marker

Časovo a verziou označená udalosť v observability systéme umožňujúca korelovať zmenu error rate, latency alebo business metrík s konkrétnym deploymentom. Pozri [Continuous Deployment](docs/05-ci-cd-and-release/continuous-deployment.md).

## Deployment pipeline

Automatizovaný tok od source zmeny cez build, testy, artifact, environment deployment a validáciu až po produkčne pripraveného alebo nasadeného kandidáta. Pozri [Continuous Delivery](docs/05-ci-cd-and-release/continuous-delivery.md).

## Deployment record

Auditovateľný záznam spájajúci environment, artifact digest, configuration revision, pipeline run, identity, čas a výsledok konkrétneho deploymentu. Pozri [Environment a promotion](docs/05-ci-cd-and-release/environment-and-promotion.md).

## Deployment revision

Verzia Deployment Pod template-u reprezentovaná príslušným ReplicaSetom a použitá pre rollout history alebo rollback. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## Deployment rework rate

Podiel deploymentov, ktoré sú neplánovanou opravou predchádzajúceho deploymentu. Pozri [DORA Metrics](docs/00-foundations/dora-metrics.md).

## Deployment ring

Stabilná rollout skupina používateľov, tenantov, zariadení alebo regiónov s definovaným risk profilom, membershipom a promotion contractom. Pozri [Ring deployment](docs/05-ci-cd-and-release/ring-deployment.md).

## Deprecated API caller

Klient, controller, chart, operator alebo automation používajúca Kubernetes API verziu, ktorá bude alebo už bola odstránená, aj keď deklaratívne manifests už môžu byť migrované. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## deregistration delay — ELB

Target-group interval, počas ktorého deregistrovaný target zostáva v draining stave pre dokončenie existujúcich requests alebo connections. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## Derived signal

Telemetry signal vypočítaný z iného signalu, napríklad metrics zo spans alebo logs; musí mať explicitný source-of-truth a sampling contract. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Descriptor — OCI

Štruktúra identifikujúca OCI content pomocou media type, digestu a size, prípadne ďalších annotations alebo platform metadata. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Deserialized object — PowerShell

Prenesená reprezentácia vzdialeného PowerShell objektu, ktorá typicky zachováva properties, ale nie live methods a pôvodné runtime správanie. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## desired capacity — Auto Scaling

Počet instances alebo weighted capacity units, ktoré sa Auto Scaling Group v aktuálnom čase snaží udržať. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Desired replica calculation — HPA

Výpočet odporúčaného replica countu založený približne na pomere aktuálnej a cieľovej metric hodnoty, následne upravený tolerance, missing metrics a behavior policy. Pozri [HPA a autoscaling](docs/09-kubernetes/hpa-autoscaling.md).

## Desired replicas — Kubernetes

Počet replík požadovaný v workload spec-e alebo odvodený controllerom, ku ktorému sa controller snaží priblížiť observed replica population. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Desired state

Požadovaný stav systému deklarovaný používateľom alebo automatizačným nástrojom. Pozri [Desired State and Reconciliation](docs/00-foundations/desired-state-and-reconciliation.md).

## Desired state — Kubernetes

Intent deklarovaný v Kubernetes object `spec` alebo odvodený vyšším controllerom, ku ktorému control loops približujú aktuálny stav. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Detached HEAD

Stav, v ktorom `HEAD` ukazuje priamo na commit namiesto symbolického odkazu na branch. Nové commits treba zachytiť branch refom, inak môžu zostať unreachable. Pozri [Commit, branch, tag a HEAD](docs/03-git-and-automation/commit-branch-tag-head.md).

## Detective control

Control určený na odhalenie incidentu, policy violation alebo nežiaducej zmeny. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Deterministic encryption

Encryption model, v ktorom rovnaký plaintext pri rovnakom keyu a kontexte produkuje rovnaký ciphertext, čo môže umožniť equality queries, ale zároveň odhaľuje opakovanie a frequency patterns. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## Deterministic serialization

Serializácia, pri ktorej rovnaký logický vstup vytvára stabilný byte alebo textový výstup podľa definovaných pravidiel. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Development target — Dockerfile

Multi-stage build target obsahujúci development-only tools, debugger, hot reload alebo source-mount contract, ktorý nesmie byť neúmyselne publikovaný ako production runtime image. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## Device Authorization flow

OAuth flow pre zariadenia s obmedzeným inputom, pri ktorom používateľ autorizuje device code na inom zariadení. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Device identity

Cryptographically alebo administratívne overená identita endpointu, ktorá sama osebe nedokazuje jeho aktuálny security posture. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Device posture

Aktuálne security attributes zariadenia, napríklad patch level, encryption, EDR health alebo secure boot, používané ako contextual policy inputs. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## DevOps

Kultúrne princípy, organizačné praktiky a technické mechanizmy na rýchle a bezpečné dodávanie zmien. Pozri [DevOps](docs/00-foundations/devops.md).

## DHCP — Dynamic Host Configuration Protocol

Protokol na prideľovanie IP configuration, lease a ďalších network parameters klientom. Pozri [DHCP](docs/02-networking-and-web/dhcp.md).

## DHCP lease

Časovo obmedzené oprávnenie klienta používať pridelenú adresu a konfiguráciu. Pozri [DHCP](docs/02-networking-and-web/dhcp.md).

## DHCP relay

Komponent forwardujúci DHCP komunikáciu medzi klientskym broadcast domainom a serverom v inom subnete. Pozri [DHCP](docs/02-networking-and-web/dhcp.md).

## DHCP reservation

Centrálne DHCP-managed mapovanie identity klienta na stabilnú IP adresu. Pozri [DHCP](docs/02-networking-and-web/dhcp.md).

## DHCP snooping

Switchová ochrana povoľujúca DHCP server responses iba na trusted portoch. Pozri [DHCP](docs/02-networking-and-web/dhcp.md).

## Diagnosis time — CKA drill

Čas od začiatku troubleshooting scenára po správne pomenovanie root cause na základe dôkazov. Pozri [CKA troubleshooting drills](docs/10-helm-and-cka/cka-troubleshooting-drills.md).

## Diagonal scaling

Kombinácia vertical a horizontal scalingu, pri ktorej sa najprv mení veľkosť resource-u a následne počet replicas alebo nodes. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Diff coverage

Coverage vypočítaná iba pre nový alebo zmenený kód voči zvolenému merge base. Pozri [Code coverage a quality gates](docs/04-testing-and-quality/code-coverage-and-quality-gates.md).

## Diff ID — OCI image

Digest uncompressed filesystem layer changesetu uložený v OCI image configuration rootfs chain, odlišný od digestu compressed blobu prenášaného cez registry. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Diff mode — Ansible

Režim zobrazujúci content rozdiel pri podporovaných modules; output môže obsahovať citlivé údaje a potrebuje access a retention policy. Pozri [Ansible architecture](docs/07-infrastructure-as-code-and-configuration-management/ansible-architecture.md).

## Differential policy testing

Vyhodnotenie rovnakého corpus-u inputs cez starú a novú policy revision s kontrolou semantic decision rozdielov. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Digest pinning

Viazanie dependency, action, image alebo artifact reference na immutable cryptographic content digest namiesto mutable tagu alebo version range. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Direct access bypass — Zero Trust

Alternatívna network alebo application cesta, ktorá umožňuje dostať sa ku resource-u bez zamýšľaného identity-aware PEP a policy evaluation. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Direct membership — GitLab

Členstvo pridané priamo na konkrétny project alebo group, na rozdiel od accessu zdedeného z parent group alebo získaného sharingom. Pozri [Projects, groups a permissions](docs/06-gitlab/projects-groups-permissions.md).

## Direct Pod

Pod vytvorený bez vyššieho workload controlleru; po strate alebo Node failure nemá automatický replica replacement a rollout model. Pozri [Pod](docs/09-kubernetes/pod.md).

## Direct-to-storage tracing

Jaeger deployment model, v ktorom collectors zapisujú traces priamo do external storage bez durable Kafka bufferu. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Directory Information Tree — DIT

Hierarchická štruktúra LDAP directory entries organizovaná podľa Distinguished Names. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## Directory partition — AD DS

Replikovaný naming context AD DS, napríklad schema, configuration, domain alebo application partition, s vlastným replication scope-om. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Disaster recovery — DR

People, process a technology capability obnoviť business službu a jej dáta po udalosti presahujúcej bežný high-availability design podľa definovaných RPO a RTO. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Disaster recovery — Kubernetes

Koordinovaný proces obnovy control-plane state-u, PKI, encryption keys, external infrastructure a application dát po strate authoritative cluster state-u. Pozri [etcd backup a restore](docs/09-kubernetes/etcd-backup-restore.md).

## Disconnected operation

Schopnosť hybridného alebo edge workloadu pokračovať v definovanom režime pri strate spojenia s central cloud control plane alebo WAN dependency. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Disk watermark — search cluster

Threshold disk usage ovplyvňujúci shard allocation, relocation alebo write blocks v Elasticsearch/OpenSearch clusteri. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Distinguished Name — DN

Jednoznačný hierarchický názov LDAP entry, napríklad `uid=alice,ou=People,dc=example,dc=com`. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## Distributed cache — GitLab Runner

CI cache uložená v shared backend-e, typicky object storage, aby ju mohli používať viaceré alebo autoscaled runners. Pozri [Artifacts a cache](docs/06-gitlab/artifacts-and-cache.md).

## Distributed trace

Model celej cesty requestu alebo operácie cez viac services a dependencies, zložený z navzájom prepojených spans. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Distribution digest — OCI

Content digest registry blobu alebo manifestu v jeho distribuovanej reprezentácii, používaný na integrity verification a immutable references. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Distribution — metric

Reprezentácia rozdelenia nameraných hodnôt, napríklad latency alebo response size, ktorá zachováva viac informácií než average. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Distroless image

Minimalizovaný runtime image bez bežného shellu alebo package managera, určený na spustenie konkrétnej aplikácie s menším mutable surface; vyžaduje external observability a premyslený debugging model. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## DNAT — Destination NAT

Preklad destination adresy alebo portu, používaný napríklad pri publikovaní internej služby. Pozri [NAT](docs/02-networking-and-web/nat.md).

## DNS delegation

Publikovanie NS records v parent DNS zone, ktorým sa authoritative zodpovednosť za domain alebo subdomain odovzdá konkrétnym name serverom. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## DNS — Domain Name System

Distribuovaný hierarchický systém mapujúci mená na resource records. Pozri [DNS](docs/02-networking-and-web/dns.md).

## DNS negative caching

Dočasné cache-ovanie odpovede, že DNS meno neexistuje alebo nemá požadovaný record, ktoré môže predĺžiť NXDOMAIN symptóm po neskoršom vytvorení Service-u. Pozri [Cluster DNS](docs/09-kubernetes/cluster-dns.md).

## DNS policy — Kubernetes

Pod-level pravidlo určujúce zdroj a spôsob resolver configuration, napríklad `ClusterFirst`, `Default`, `ClusterFirstWithHostNet` alebo `None`. Pozri [Cluster DNS](docs/09-kubernetes/cluster-dns.md).

## DNS resolver

Komponent vykonávajúci alebo sprostredkujúci DNS resolution. Pozri [DNS](docs/02-networking-and-web/dns.md).

## DNS search domain

Suffix v Pod `/etc/resolv.conf`, ktorý resolver pridáva ku krátkym menám pri service discovery, napríklad `<namespace>.svc.<cluster-domain>`. Pozri [Cluster DNS](docs/09-kubernetes/cluster-dns.md).

## DNS TCP fallback

Prechod DNS klienta z UDP na TCP, napríklad po truncated alebo veľkej odpovedi; firewall musí podľa potreby povoľovať oba transporty na porte 53. Pozri [Cluster DNS](docs/09-kubernetes/cluster-dns.md).

## DNS TTL

Čas, počas ktorého môže resolver cacheovať DNS resource record. Pozri [DNS](docs/02-networking-and-web/dns.md).

## `dnsConfig` — Kubernetes

Pod spec configuration dopĺňajúca alebo pri `dnsPolicy: None` definujúca nameservers, search domains a resolver options. Pozri [Cluster DNS](docs/09-kubernetes/cluster-dns.md).

## DNSSEC

DNS security extension používajúca cryptographic signatures a chain of trust na overenie authenticity a integrity DNS odpovedí. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Docker bind mount

Runtime mount konkrétneho host filesystem pathu do container mount namespace-u, ktorý prenáša host path, permissions, labels a lifecycle coupling. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## Docker CLI

Client program `docker`, ktorý parsuje príkazy a komunikuje s Docker Engine API; container primitives typicky nevytvára priamo. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Docker context

Pomenovaný client-side connection profil určujúci Docker daemon endpoint, TLS/SSH metadata a ďalšie connection nastavenia; nesprávny context môže nasmerovať deštruktívny príkaz na iný host. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Docker daemon — `dockerd`

Dlhodobo bežiaci server Docker Engine-u spravujúci images, containers, networks, volumes, builds a komunikáciu s nižšími runtime components. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Docker Desktop

Desktop platforma zahŕňajúca Docker Engine, CLI, UI, build, credential, networking a virtualizačné komponenty; na Windows a macOS typicky používa Linux virtualizačnú vrstvu pre Linux containers. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Docker diagnostic baseline

Minimálna sada evidence zahŕňajúca versions, context, `docker info`, container state, inspect, logs, events, resource usage a disk stav pred deštruktívnym zásahom. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Docker disk usage

Storage spotrebovaný images, writable layers, volumes, build cache, logs a runtime content stores, analyzovaný napríklad cez `docker system df`. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Docker embedded DNS

DNS service poskytovaná Docker Engine-om pre name resolution containers a aliases v user-defined networks. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Docker Engine

Client-server container platforma pozostávajúca z daemon-u, API a súvisiacich components na správu Docker objects a container lifecycle. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Docker Engine API

Versionované HTTP API, cez ktoré clients a integrations riadia Docker daemon; prístup k nemu je privilegovaná platformová capability. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Docker event

Časovo zoradená runtime udalosť Docker daemon-u, napríklad create, start, die, health status, network connect alebo image pull, použitá na incident koreláciu. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Docker executor — GitLab Runner

Executor, ktorý spúšťa každý job v containeri vytvorenom z definovaného image a môže pripájať service containers, volumes a cache. Pozri [Runners a executors](docs/06-gitlab/runners-and-executors.md).

## Docker health history

Obmedzený záznam posledných healthcheck executions, exit statuses a outputu dostupný cez container inspection. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Docker health status

Runtime stav `starting`, `healthy` alebo `unhealthy` odvodený z healthchecku a oddelený od process state `running` alebo `exited`. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Docker healthcheck

Periodický command definovaný image-om alebo runtime modelom, ktorého exit status určuje health state bežiaceho containeru. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Docker host network

Network mode, v ktorom container process zdieľa host network namespace, binduje priamo host ports a nemá bežnú samostatnú container network isolation. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Docker internal network

Docker network deklarovaná tak, aby obmedzila bežný external routing/egress podľa driver capabilities, používaná na užšie backend communication boundaries. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Docker network

Pomenovaný runtime connectivity object s konkrétnym driverom, IPAM a isolation/discovery semantics pre pripojené containers. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Docker network alias

Dodatočné logical DNS meno container endpointu platné v konkrétnej Docker network boundary. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Docker none network

Runtime network mode poskytujúci containeru minimálny network namespace bez bežnej external connectivity, typicky iba s loopback interfaceom. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Docker object

Daemon-managed objekt ako image, container, network alebo volume s vlastnou identity a lifecycle semantics. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Docker port publishing

Runtime forwarding alebo routing konfigurácia mapujúca host address a port na port v container network namespace; je odlišná od Dockerfile `EXPOSE`. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Docker socket

Local Unix socket alebo obdobný endpoint poskytujúci prístup k Docker Engine API; write access je často prakticky host-administration capability. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Docker volume

Docker-managed storage object s lifecycle oddeleným od konkrétnej container instance; persistence neznamená automatický backup, replication ani multi-host durability. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## Dockerfile

Versionovaný build program obsahujúci instructions, z ktorých builder vytvorí image filesystem layers a runtime metadata. Pozri [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md).

## Dockerfile frontend

Parser a build frontend implementujúci Dockerfile syntax a prekladajúci instructions do BuildKit build graphu, často vybraný cez `# syntax=` directive. Pozri [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md).

## `.dockerignore`

Pattern file filtrujúci content zahrnutý do Docker build contextu; znižuje transfer, cache invalidation a accidental exposure, ale nie je secret manager ani náhrada za odstránenie secrets z repository history. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Document — search

JSON objekt uložený v Elasticsearch/OpenSearch indexe a spracovaný podľa mappingu. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Document stream — YAML

YAML stream obsahujúci jeden alebo viac documents oddelených markerom `---`. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Domain — AD DS

Logical AD DS partition s vlastným DNS name, domain-wide objects, replication scope a domain operations roles. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Domain controller

Server hostujúci AD DS directory partitions a poskytujúci LDAP, Kerberos KDC, authentication, replication a SYSVOL/Group Policy služby. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Domain Local group

AD DS group scope typicky používaný na priradenie permissions k resources v konkrétnej doméne. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Domain-weighted lab — CKA

Timed lab, ktorého bodové rozdelenie zodpovedá aktuálnym oficiálnym CKA curriculum doménam namiesto rovnomerného alebo náhodného mixu tém. Pozri [CKA timed labs](docs/10-helm-and-cka/cka-timed-labs.md).

## `DoNotSchedule` — topology spread

Hard topology spread behavior, pri ktorom scheduler Pod nenaplánuje, ak by porušil deklarovaný `maxSkew` a ďalšie constraint pravidlá. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## DORA metrics

Metriky software delivery performance sledujúce throughput a instability delivery systému. Pozri [DORA Metrics](docs/00-foundations/dora-metrics.md).

## Drift

Rozdiel medzi deklarovaným a skutočným stavom systému. Pozri [Desired State and Reconciliation](docs/00-foundations/desired-state-and-reconciliation.md).

## Drift detection cadence

Frekvencia, s akou sa pre konkrétny state alebo infra domain vykonáva refresh/plan a klasifikácia zmien podľa security, availability a change rizika. Pozri [Drift](docs/07-infrastructure-as-code-and-configuration-management/drift.md).

## Drift noise — Terraform

Opakovaný alebo nerelevantný plan diff spôsobený napríklad provider normalizáciou, server defaults, orderingom, timestamps alebo eventual consistency namiesto významnej ownership zmeny. Pozri [Drift](docs/07-infrastructure-as-code-and-configuration-management/drift.md).

## Drift reconciliation

Riadené rozhodnutie drift revertovať, adoptovať do configuration, zmeniť ownership alebo odstrániť Terraform management s následným overením state a remote výsledku. Pozri [Drift](docs/07-infrastructure-as-code-and-configuration-management/drift.md).

## Drop — firewall action

Tiché zahodenie packetu bez explicitnej odpovede klientovi. Typickým symptómom je timeout. Pozri [Firewally](docs/02-networking-and-web/firewalls.md).

## DSSE

Dead Simple Signing Envelope; envelope format viažuci payload type a payload bytes k signatures s ochranou proti cross-protocol confusion. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Dual stack

Prevádzka IPv4 aj IPv6 na rovnakom hoste alebo službe. Pozri [IPv4, IPv6 a subnetting](docs/02-networking-and-web/ipv4-ipv6-subnetting.md).

## Dual write

Dočasný migration model, v ktorom application zapisuje rovnakú logickú zmenu do starej aj novej reprezentácie alebo store. Vyžaduje idempotency, authoritative source a reconciliation. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Dummy — test double

Hodnota potrebná iba na vyplnenie parametra bez aktívneho použitia v testovanom scenári. Pozri [Mocks, stubs a fakes](docs/04-testing-and-quality/mocks-stubs-fakes.md).

## Durable function — Lambda

Lambda execution model pre dlhšie workflowy so service-managed durable state a checkpointingom, odlišný od štandardného krátkodobého invocation contractu. Pozri [Lambda](docs/11-cloud-and-aws/lambda.md).

## Duration distribution

Rozdelenie trvania operácií používané v RED na sledovanie typical aj tail latency bez redukcie na jediný priemer. Pozri [RED method](docs/12-observability/red-method.md).

## Dynamic child pipeline — GitLab

Child pipeline, ktorého CI configuration je vytvorená alebo zvolená počas parent pipeline podľa repository alebo runtime metadata. Pozri [GitLab CI/CD syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md).

## Dynamic environment — GitLab

Dočasný environment vytvorený pre branch, merge request alebo inú krátkodobú jednotku a ukončený stop jobom, TTL alebo reconcilerom. Pozri [Environments, deployments a releases](docs/06-gitlab/environments-deployments-releases.md).

## Dynamic include — Ansible

Reusable task, role alebo playbook content načítaný počas executionu podľa runtime contextu, na rozdiel od skoršie spracovaného static importu. Pozri [Modules, tasks, plays a playbooks](docs/07-infrastructure-as-code-and-configuration-management/modules-tasks-plays-playbooks.md).

## Dynamic inventory — Ansible

Inventory získaný cez plugin alebo external script z API, CMDB, cloud platformy alebo iného meniaceho sa source-u. Pozri [Inventory](docs/07-infrastructure-as-code-and-configuration-management/inventory.md).

## Dynamic mapping

Automatické vytváranie field mappings podľa prichádzajúcich documents; bez governance môže spôsobiť schema conflicts a mapping explosion. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Dynamic provisioning — Kubernetes storage

Automatické vytvorenie backing storage a PV external provisionerom na základe PVC a StorageClass. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Dynamic secret

Credential generovaný on demand pre konkrétnu identity alebo role s krátkym lease a revocation lifecycle-om. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Dynamic separation of duties

Constraint, ktorý zakazuje použiť conflictujúce roles alebo capabilities v tej istej session alebo transaction, aj keď ich principal môže mať pridelené. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Early feedback

Informácia o kvalite alebo riziku získaná v najskoršom bode, v ktorom má kontrola dostatočnú fidelity a diagnostickú hodnotu. Pozri [Shift-left](docs/04-testing-and-quality/shift-left.md).

## East-west traffic

Network traffic medzi internými workloads alebo services v rámci platformy, ktorého nekontrolovaný default-allow model zvyšuje lateral-movement risk. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## eBPF — extended Berkeley Packet Filter

Kernel technológia na spúšťanie overeného bytecode na definovaných hooks, používaná aj na observability a profiling. Pozri [Performance a troubleshooting](docs/01-linux-and-systems/performance-and-troubleshooting.md).

## EBS Multi-Attach

Capability vybraných Provisioned IOPS EBS volumes umožňujúca pripojenie k viacerým podporovaným instances v rovnakej AZ; vyžaduje cluster-aware filesystem/application a fencing. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## EBS snapshot

Point-in-time block snapshot EBS volume-u používaný na restore, copy, migration alebo backup; bez application koordinácie môže byť iba crash-consistent. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## EBS volume

Persistent block device v jednej Availability Zone, ktorý možno attachnúť k EC2 instance v rovnakej AZ. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## EC2 instance

Konkrétna spustená alebo zastavená virtual machine identity vytvorená z AMI a launch configuration, s vlastným instance ID, network interfaces, storage a lifecycle stavom. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## ECS capacity provider

ECS abstraction určujúca compute capacity, napríklad Fargate, Fargate Spot, Managed Instances alebo EC2 Auto Scaling Group, a jej rozdelenie cez base/weight strategy. Pozri [ECS a EKS](docs/11-cloud-and-aws/ecs-eks.md).

## ECS cluster

Logická skupina ECS tasks, services a compute capacity, nad ktorou scheduler vykonáva placement a service lifecycle. Pozri [ECS a EKS](docs/11-cloud-and-aws/ecs-eks.md).

## ECS service

ECS controller udržiavajúci desired count tasks, vykonávajúci replacement, deployment a integráciu s load balancingom alebo service connectivity. Pozri [ECS a EKS](docs/11-cloud-and-aws/ecs-eks.md).

## ECS task

Jedna runtime inštancia konkrétnej ECS task definition revision pozostávajúca z jedného alebo viacerých containers. Pozri [ECS a EKS](docs/11-cloud-and-aws/ecs-eks.md).

## ECS task definition

Versionovaný immutable template určujúci containers, image, resources, ports, roles, logging, secrets, networking a storage pre ECS task. Pozri [ECS a EKS](docs/11-cloud-and-aws/ecs-eks.md).

## ECS task execution role

IAM role používaná ECS agentom alebo Fargate platformou napríklad na image pull, log delivery a secret injection pred alebo počas štartu tasku. Pozri [ECS a EKS](docs/11-cloud-and-aws/ecs-eks.md).

## ECS task role

IAM role poskytujúca AWS permissions application containers bežiacim v ECS tasku. Pozri [ECS a EKS](docs/11-cloud-and-aws/ecs-eks.md).

## Edge cloud

Compute a storage platforma umiestnená bližšie k používateľom, zariadeniam alebo výrobnému procesu pre nízku latency, lokálne spracovanie alebo prerušovanú konektivitu. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Effective access

Výsledná množina permissions po vyhodnotení direct a inherited assignments, groups, roles, conditions, boundaries, resource policies a explicit denies. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Effective capability set

Množina Linux capabilities aktuálne používaná kernelom pri privilege checks procesu. Pozri [Linux capabilities](docs/01-linux-and-systems/linux-capabilities.md).

## Effective capacity

Kapacita skutočne dostupná workloadu po zohľadnení quotas, reservations, failures, topology, limits a maintenance, nie iba nominálny súčet resources. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Effective release values — Helm

Výsledná values konfigurácia po zlúčení chart defaults, predchádzajúceho release state-u podľa zvolenej stratégie, values files a CLI overrides. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Effective role — GitLab

Najvyššia rola, ktorú používateľ získa zo všetkých relevantných direct, inherited a shared memberships na danom resource. Pozri [Projects, groups a permissions](docs/06-gitlab/projects-groups-permissions.md).

## EFS access point

Application-specific EFS entry point vynucujúci root directory a voliteľnú POSIX identity pre mounted clienta. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## EFS mount target

ENI-based VPC endpoint v konkrétnej Availability Zone, cez ktorý clients pristupujú k EFS filesystemu protokolom NFS. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Egress-isolated Pod

Pod vybraný aspoň jednou NetworkPolicy pre egress, ktorého outbound traffic je povolený iba unionom matching egress pravidiel. Pozri [CNI a NetworkPolicy](docs/09-kubernetes/cni-networkpolicy.md).

## Egress-only Internet Gateway — AWS

VPC component poskytujúci outbound-initiated IPv6 internet connectivity bez všeobecného unsolicited inbound pathu. Pozri [Internet Gateway a NAT Gateway](docs/11-cloud-and-aws/internet-gateway-nat-gateway.md).

## Egress policy — Zero Trust

Resource alebo workload-specific pravidlá určujúce povolené outbound destinations, protocols a data flows s cieľom obmedziť exfiltration a command-and-control paths. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## EKS access entry

EKS resource mapujúci AWS IAM principal na cluster access configuration a Kubernetes identity/groups podľa podporovaného access modelu. Pozri [ECS a EKS](docs/11-cloud-and-aws/ecs-eks.md).

## EKS Auto Mode

EKS compute a infrastructure management model, v ktorom AWS automatizuje väčšiu časť node, networking, storage a load-balancing operations podľa aktuálnych service capabilities. Pozri [ECS a EKS](docs/11-cloud-and-aws/ecs-eks.md).

## EKS Fargate profile

Configuration vyberajúca Kubernetes Pods podľa namespace a labels a určujúca ich spustenie na AWS Fargate. Pozri [ECS a EKS](docs/11-cloud-and-aws/ecs-eks.md).

## EKS managed node group

EKS-integrated skupina EC2 worker nodes založená na Auto Scaling Group-e, pri ktorej AWS koordinuje časť node lifecycle a update operácií. Pozri [ECS a EKS](docs/11-cloud-and-aws/ecs-eks.md).

## Elastic Load Balancing — ELB

AWS managed load-balancing family zahŕňajúca Application, Network a Gateway Load Balancers. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## Elastic network interface — ENI

Zonálny AWS network object nesúci private IP addresses, Security Groups, MAC a attachment identity pre EC2 a viaceré managed services. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## Elastic Volumes — EBS

EBS capability na online zmenu veľkosti, typu, IOPS alebo throughputu podporovaného volume-u, po ktorej môže byť potrebné samostatne rozšíriť partition a filesystem. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Elasticity

Schopnosť systému dynamicky pridávať alebo odoberať kapacitu podľa demandu, provisioning latency, policy, quotas a cost guardrails. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Elasticsearch

Distribuovaný search, analytics a document-store systém založený na Apache Lucene. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Eligible approver — GitLab

Používateľ, ktorého membership, role a approval-rule context oprávňujú poskytnúť approval započítaný pre konkrétny merge request. Pozri [Merge requests a approvals](docs/06-gitlab/merge-requests-and-approvals.md).

## Eligible Node — DaemonSet

Node, ktorý spĺňa DaemonSet placement podmienky vrátane labels, affinity, taints/tolerations, platformy, admission a scheduling constraints. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## Embedded Metric Format

Structured log format, z ktorého CloudWatch extrahuje custom metrics a dimensions bez samostatného per-metric API publish callu. Pozri [CloudWatch a CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## Empty value — Helm

Hodnota považovaná template functions ako `default` alebo `coalesce` za neprítomnú, napríklad `nil`, prázdny string, nula, `false` alebo prázdna collection podľa typu. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Emulation — multi-platform build

Spustenie target-architecture build binaries cez emulačnú vrstvu, napríklad QEMU, na hoste s odlišnou architecture; nenahrádza úplný native runtime test. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Encapsulation

Proces, pri ktorom každá sieťová vrstva pridá svoje metadata okolo payloadu vyššej vrstvy. Pozri [OSI a TCP/IP model](docs/02-networking-and-web/osi-and-tcp-ip-model.md).

## Encrypted file — Ansible Vault

Súbor, ktorého celý obsah je zašifrovaný Ansible Vaultom a musí byť dešifrovaný pri načítaní alebo použití. Pozri [Vault](docs/07-infrastructure-as-code-and-configuration-management/vault.md).

## Encrypted variable — Ansible Vault

Jednotlivá YAML hodnota uložená ako `!vault` encrypted block v inak čitateľnom súbore. Pozri [Vault](docs/07-infrastructure-as-code-and-configuration-management/vault.md).

## Encryption at rest

Cryptographic ochrana dát uložených v persistentných médiách, databázach, object stores, snapshots alebo backups podľa definovanej storage threat boundary. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## Encryption barrier — Vault

Vault cryptographic boundary chrániaca storage data; sealed Vault nemá v memory kľúče potrebné na ich decryption. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Encryption context — KMS

Non-secret key-value context kryptograficky viazaný na podporovanú KMS encrypt/decrypt operation a použiteľný v policy conditions a audite. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Encryption in transit

Cryptographic ochrana dát počas prenosu medzi endpoints, typicky spolu s peer alebo server identity validation a channel integrity. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## Encryption type — Kerberos

Cryptographic algorithm a associated key semantics používané pre Kerberos long-term keys, tickets alebo session keys. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## End-to-end test

Test workflow prechádzajúci cez viac produkčne relevantných vrstiev alebo procesných hraníc od vstupu po observable výsledok. Pozri [End-to-end a acceptance tests](docs/04-testing-and-quality/end-to-end-and-acceptance-tests.md).

## End-User — OIDC

Používateľ, ktorého authentication event OpenID Provider potvrdzuje Relying Party. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md).

## Endpoint readiness — Kubernetes

EndpointSlice condition signalizujúci, či je backend vhodný pre bežný Service traffic podľa Pod readiness a publication policy. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## EndpointSlice

Namespaced `discovery.k8s.io` object reprezentujúci časť backend endpointov Service-u vrátane addresses, ports, conditions a topology metadata. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## Enforcement boundary — resource

Vrstva, na ktorej sa reálne presadzuje resource limit alebo quota, napríklad cgroup, Node, connection pool, Availability Zone alebo cloud account. Pozri [USE method](docs/12-observability/use-method.md).

## Enforcing mode

Režim SELinux alebo AppArmor policy, v ktorom sa zakázané operácie blokujú. Pozri [SELinux a AppArmor](docs/01-linux-and-systems/selinux-and-apparmor.md).

## Entitlement

Konkrétne oprávnenie, role, group membership alebo capability, ktorú možno prideliť principalu. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Entity ID — SAML

Stabilný identifier SAML Identity Providera alebo Service Providera používaný v metadata a issuer/audience trust contracte. Pozri [SAML](docs/13-security-and-identity/saml.md).

## Envelope encryption

Model, v ktorom data key šifruje application data a dlhodobejší KMS key šifruje samotný data key. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Environment drift

Rozdiel medzi deklarovaným desired state environmentu a jeho skutočným runtime stavom, napríklad po manuálnej config alebo infrastructure zmene. Pozri [Environment a promotion](docs/05-ci-cd-and-release/environment-and-promotion.md).

## Environment injection — Kubernetes

Odovzdanie ConfigMap alebo Secret hodnoty do environmentu pri vytvorení container procesu; neskoršia zmena source objektu environment bežiaceho procesu nezmení. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Environment parity — deployment

Miera, do akej blue a green alebo iné deployment targety zachovávajú rovnaké produkčne relevantné konfigurácie, topológiu, permissions, limits a dependencies. Pozri [Blue-green deployment](docs/05-ci-cd-and-release/blue-green-deployment.md).

## Environment precedence — Docker

Pravidlá určujúce výslednú environment hodnotu pri kombinácii CLI overrides, Compose `environment`, `env_file`, image `ENV` a application defaults. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Environment promotion

Riadený posun rovnakého artifactu do ďalšieho prostredia na základe dôkazov, policy a compatibility podmienok. Pozri [Continuous Delivery](docs/05-ci-cd-and-release/continuous-delivery.md).

## Environment-scoped variable — GitLab

CI/CD variable dostupná iba jobs, ktorých deklarovaný environment zodpovedá nastavenému scope alebo patternu. Pozri [Protected branches a environments](docs/06-gitlab/protected-branches-and-environments.md).

## Environment variable

Pomenovaná hodnota odovzdaná procesu v jeho environment bloku. Pozri [Environment variables](docs/01-linux-and-systems/environment-variables.md).

## Ephemeral chart test cluster

Dočasný Kubernetes cluster používaný na realistické install, upgrade, rollback, test a uninstall overenie chart artifactu. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Ephemeral container

Diagnostický container pridaný do existujúceho Podu na troubleshooting, ktorý nie je trvalou súčasťou pôvodného workload contractu. Pozri [Pod](docs/09-kubernetes/pod.md).

## Ephemeral port

Dočasný source port typicky pridelený klientskemu socketu. Pozri [Ports a sockets](docs/02-networking-and-web/ports-and-sockets.md).

## Ephemeral port exhaustion

Stav, keď host alebo NAT nemá voľný transportný port pre nový flow. Pozri [Ports a sockets](docs/02-networking-and-web/ports-and-sockets.md) a [NAT](docs/02-networking-and-web/nat.md).

## Ephemeral runner

Build worker vytvorený pre obmedzený job alebo run a následne zničený, aby sa znížilo cross-job contamination a persistence risk. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Ephemeral runtime instance

Nahraditeľná runtime inštancia, ktorej lokálny procesový a writable-layer stav nie je považovaný za jediný persistentný zdroj dát. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Ephemeral storage request

Deklarovaná požiadavka Podu alebo containeru na Node-local ephemeral storage používaná pri scheduling-u a resource accounting-u. Pozri [Requests, limits a QoS](docs/09-kubernetes/requests-limits-qos.md).

## Ephemeral volume — Kubernetes

Volume s lifecycle viazaným na Pod alebo konkrétnu projection, napríklad `emptyDir`, ConfigMap/Secret projection alebo generic ephemeral volume. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## EPSS

Exploit Prediction Scoring System; pravdepodobnostný signal odhadujúci šancu, že publikovaná CVE bude v blízkom časovom horizonte pozorovaná ako exploatovaná, nie všeobecný business-impact score. Pozri [Vulnerability a patch management](docs/13-security-and-identity/vulnerability-and-patch-management.md).

## Equal labels — Alertmanager

Labels, ktorých hodnoty musia byť zhodné medzi source a target alertom, aby sa aplikovala inhibition. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Error rate — RED

Podiel failed operations voči relevantnému počtu valid operations pri rovnakom scope-e a success contracte. Pozri [RED method](docs/12-observability/red-method.md).

## ETag

HTTP validator reprezentácie používaný na cache revalidation a optimistic concurrency cez conditional requests. Pozri [HTTP](docs/02-networking-and-web/http.md).

## etcd compaction marker — restore

Restore voľba označujúca staršiu revision históriu ako compacted, aby watchers vykonali relist namiesto používania stale cache assumptions. Pozri [etcd backup a restore](docs/09-kubernetes/etcd-backup-restore.md).

## etcd member health

Stav konkrétneho etcd člena z pohľadu endpoint dostupnosti, Raft membership, leader/quorum participation, revision a disk/network health. Pozri [etcd backup a restore](docs/09-kubernetes/etcd-backup-restore.md).

## etcd quorum

Väčšina voting members potrebná na bezpečné potvrdenie etcd consensus operations; strata quorum blokuje spoľahlivé Kubernetes API writes. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## etcd revision bump

Posunutie revision pri snapshot restore tak, aby nová logical história prekonala revisions pozorované clients pred incidentom. Pozri [etcd backup a restore](docs/09-kubernetes/etcd-backup-restore.md).

## etcd snapshot

Point-in-time backup etcd data store-u používaný v testovanom Kubernetes control-plane recovery postupe. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## Ethernet frame

Link-layer jednotka obsahujúca source a destination MAC, EtherType, payload a kontrolné metadata. Pozri [Ethernet, MAC a ARP](docs/02-networking-and-web/ethernet-mac-arp.md).

## Event-driven autoscaling

Scaling model reagujúci na event-source alebo business metrics, napríklad queue backlog, často implementovaný ecosystem controllerom nad rámec core HPA. Pozri [HPA a autoscaling](docs/09-kubernetes/hpa-autoscaling.md).

## Event — Kubernetes

Časovo obmedzený diagnostický API object opisujúci významnú udalosť okolo iného resource-u, napríklad scheduling, image pull, probe alebo volume failure; nie je trvalým audit logom. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Event — observability

Časovo označený záznam významnej zmeny alebo udalosti, napríklad deploymentu, failoveru, scalingu alebo configuration change-u. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Event series — Kubernetes

Agregovaný Kubernetes Event reprezentujúci opakovaný rovnaký reason/message v čase namiesto neobmedzeného vytvárania samostatných objektov. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Event source mapping — Lambda

Lambda resource s pollermi, ktoré čítajú batches z podporovaných queue alebo stream sources a invoke-ujú function podľa batching, concurrency a retry konfigurácie. Pozri [Lambda](docs/11-cloud-and-aws/lambda.md).

## Eventual consistency — Kubernetes

Model, v ktorom API write uloží desired state okamžite, ale controllers, scheduler, kubelet a external systems ho realizujú asynchrónne a stav sa zhoduje až po čase. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Evidence-driven review

Architektúrny review, v ktorom odpovede podporujú aktuálne configuration, telemetry, tests, policies, incidents a ďalšie overiteľné dôkazy. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Evidence freshness

Pravidlá určujúce, či test result, scan, review alebo approval stále patrí k aktuálnemu commitu, artifactu, policy a environment state. Pozri [Quality gates a approvals](docs/05-ci-cd-and-release/quality-gates-and-approvals.md).

## Evidence placement

Rozhodnutie, v ktorej najskoršej vrstve delivery možno získať dostatočne spoľahlivý dôkaz bez odstránenia relevantnej failure boundary. Pozri [Shift-left](docs/04-testing-and-quality/shift-left.md).

## Evidence preservation — Docker incident

Zachovanie inspect dát, logs, events, versions, image digestov, resource a host evidence pred restartom, delete alebo prune operáciou. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Evidence preservation — Kubernetes

Zachovanie object statusu, Events, logs, metrics, timestamps a configuration pred restartom, delete, rollbackom alebo restore operáciou. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Exam simulation — CKA

Plný časovo a pravidlami ohraničený tréning napodobňujúci performance-based exam workflow bez používania dôverných reálnych exam otázok. Pozri [CKA timed labs](docs/10-helm-and-cka/cka-timed-labs.md).

## Exception chaining — Python

Zachovanie pôvodnej exception ako príčiny novej kontextovej exception cez `raise ... from ...`. Pozri [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Exec probe

Kubernetes probe spúšťajúca command v container environment-e a vyhodnocujúca jeho exit status. Pozri [Probes](docs/09-kubernetes/probes.md).

## Executable policy

Machine-readable formalizácia policy intentu s presným input schema, scope, decision a failure semantics. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Executable specification

Príklad alebo pravidlo zapísané vo forme, ktorú možno automaticky spustiť ako dôkaz behavior. Pozri [End-to-end a acceptance tests](docs/04-testing-and-quality/end-to-end-and-acceptance-tests.md).

## Execution environment — Ansible

Versionovaný runtime image alebo prostredie obsahujúce `ansible-core`, Python dependencies, collections a system tools potrebné na reprodukovateľné vykonanie automation. Pozri [Ansible architecture](docs/07-infrastructure-as-code-and-configuration-management/ansible-architecture.md).

## Executor — CI/CD

Mechanizmus použitý runnerom na vykonanie jobu, napríklad host shell, container, virtual machine alebo Kubernetes pod. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## Executor — GitLab Runner

Mechanizmus určujúci runtime jobu, napríklad Docker container, Kubernetes pod, autoscaled instance alebo host shell. Pozri [Runners a executors](docs/06-gitlab/runners-and-executors.md).

## Exemplar

Reference z metric sample alebo histogram observation na konkrétny trace ID, ktorá umožňuje prechod z agregovanej metriky na trace. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Exit status

Číselný výsledok ukončeného procesu alebo shell príkazu. Pozri [Shell, Bash, pipes, redirection a exit codes](docs/01-linux-and-systems/shell-bash-pipes-redirection-exit-codes.md).

## Expand-contract

Viacfázový model databázovej alebo contract zmeny: najprv sa pridá kompatibilná nová štruktúra, migrujú readers/writers a dáta, a až po rollback window sa odstráni stará štruktúra. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Expand/contract migration

Backward-compatible database alebo API migration pattern, ktorý najprv pridá nový model, následne rolloutne kompatibilný software a až v neskoršom kroku odstráni starú kompatibilitu. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Experiment contract

Explicitný popis hypotézy, steady state, faultu, scope, blast radiusu, trvania, abort criteria, recovery, ownershipu a dôkazov chaos experimentu. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Experiment unit

Entita randomizovaná do variantu experimentu, napríklad používateľ, tenant, device, session alebo región. Musí zodpovedať hranici možného treatment efektu. Pozri [A/B testing](docs/05-ci-cd-and-release/a-b-testing.md).

## Experiment validity

Vlastnosť experimentu, pri ktorej baseline, target, fault, workload a observation zodpovedajú deklarovanému contractu natoľko, aby výsledok mohol potvrdiť alebo vyvrátiť hypotézu. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Explicit deny — IAM

Policy statement s `Effect: Deny`, ktorý pre applicable request prevažuje nad explicitnými allows v ostatných vyhodnocovaných policy vrstvách. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## Exploitability status

Machine-readable tvrdenie o tom, či a prečo je konkrétna vulnerability relevantná pre konkrétny artifact alebo product context. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## Exporter — Prometheus

Komponent, ktorý číta stav systému bez native Prometheus instrumentation a vystavuje ho v Prometheus metrics formáte. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Exporter — telemetry

Komponent telemetry pipeline, ktorý odosiela spracované signals do backendu alebo ďalšieho collectora. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Exposure event

Telemetry udalosť dokazujúca, že subjekt reálne dostal konkrétny experiment alebo feature variant; assignment bez exposure nemusí znamenať ovplyvnenie. Pozri [A/B testing](docs/05-ci-cd-and-release/a-b-testing.md).

## Exposure — vulnerability management

Miera, do akej je vulnerable asset alebo attack surface dostupný relevantnému threat actorovi cez network, identity, user interaction alebo supply-chain path. Pozri [Vulnerability a patch management](docs/13-security-and-identity/vulnerability-and-patch-management.md).

## Extended resource — Kubernetes

Node resource s vendor alebo domain prefixom, napríklad GPU, publikovaný device pluginom alebo platform componentom a používaný schedulerom ako integer capacity. Pozri [Requests, limits a QoS](docs/09-kubernetes/requests-limits-qos.md).

## External build cache

Build cache exportovaná mimo lokálneho buildera, napríklad do registry alebo CI backendu, s vlastnou access, trust, namespace a retention policy. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## External labels — Prometheus

Labels pridávané Prometheus serverom pri komunikácii s externými systémami na identifikáciu clusteru, Regionu, tenant-u alebo replica topology. Pozri [Prometheus](docs/12-observability/prometheus.md).

## External metric — HPA

Metric pochádzajúca mimo Kubernetes object modelu, sprístupnená HPA cez external metrics API adapter. Pozri [HPA a autoscaling](docs/09-kubernetes/hpa-autoscaling.md).

## External resource — Compose

Network, volume, config alebo secret deklarovaný ako vlastnený mimo aktuálneho Compose projektu; Compose ho používa, ale nemá automaticky riadiť jeho celý lifecycle. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## External secret provider

Systém mimo Kubernetes API, ktorý vydáva alebo uchováva citlivé hodnoty a sprístupňuje ich workloadu cez synchronizáciu, CSI projection alebo runtime fetch s workload identity. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## External secret provider — GitLab CI/CD

Secret-management systém, z ktorého job explicitne načíta citlivú hodnotu po overení federovanej alebo inej scoped identity. Pozri [Variables a secrets](docs/06-gitlab/variables-and-secrets.md).

## ExternalName Service

Kubernetes Service type poskytujúci DNS alias na external name bez bežného ClusterIP proxy a selector-based EndpointSlices. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## Fact cache — Ansible

Cache backend uchovávajúci host facts medzi runs podľa definovanej freshness, access a invalidation policy. Pozri [Variables, facts a templates](docs/07-infrastructure-as-code-and-configuration-management/variables-facts-templates.md).

## Fail closed — gate policy

Policy, pri ktorej chýbajúca alebo nedostupná evidence spôsobí blokovanie operácie. Používa sa pri kontrolách, ktorých obídenie predstavuje neprijateľné riziko. Pozri [Quality gates a approvals](docs/05-ci-cd-and-release/quality-gates-and-approvals.md).

## `fail` — Helm

Template function okamžite ukončujúca render s chart-specific error message pri porušení explicitného invariantu. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Fail open — gate policy

Policy, pri ktorej nedostupná kontrola neblokuje operáciu, ale vytvorí viditeľný degraded signal. Je vhodná iba tam, kde riziko nedostupnosti gate prevyšuje riziko pokračovania. Pozri [Quality gates a approvals](docs/05-ci-cd-and-release/quality-gates-and-approvals.md).

## fail-open — load balancer

Failure behavior, pri ktorom load balancer za určitých all-target-unhealthy podmienok stále routuje traffic na dostupné registrované targets namiesto úplného zastavenia trafficu. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## Failback

Riadený návrat workloadu a authoritative state-u z recovery lokality späť do stabilizovaného primárneho prostredia po failover-e. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Failed deployment recovery time

Čas potrebný na obnovenie služby po zlyhaní spôsobenom deploymentom. Pozri [DORA Metrics](docs/00-foundations/dora-metrics.md).

## Failed latency

Latency requestov alebo operácií, ktoré skončili failure; sleduje sa oddelene, aby rýchle errors neskresľovali successful latency. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## `FailedScheduling`

Kubernetes Event reason indikujúci, že scheduler nenašiel alebo nevedel bindnúť vhodný Node; message typicky agreguje resource, affinity, taint, topology, storage alebo port konflikty. Pozri [Scheduling](docs/09-kubernetes/scheduling.md).

## Failover

Presun trafficu, processingu alebo write ownershipu z nefunkčného primárneho componentu alebo lokality na pripravený náhradný target. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## failover routing — Route 53

DNS routing policy s primary a secondary records, ktorá mení odpovede podľa health state-u a active-passive designu. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Failure artifact

Diagnostický dôkaz zachovaný pri zlyhaní testu, napríklad screenshot, trace, log, packet capture, request ID alebo environment metadata. Pozri [End-to-end a acceptance tests](docs/04-testing-and-quality/end-to-end-and-acceptance-tests.md).

## Failure-domain narrowing

Postupné vylučovanie API, controller, scheduler, Node, runtime, CNI, CSI, Service/DNS, application a external dependency vrstiev pomocou overiteľných hypotéz. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Failure-domain narrowing — CKA

Postupné zužovanie incidentu z clusteru, Node-u, workloadu, Podu alebo containeru na konkrétny owner component a failure layer. Pozri [CKA troubleshooting drills](docs/10-helm-and-cka/cka-troubleshooting-drills.md).

## Failure policy — admission

Pravidlo určujúce, či evaluation error alebo nedostupná admission dependency request zablokuje alebo prepustí. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Fake — test double

Zjednodušená, ale funkčná implementácia dependency používaná v teste, napríklad in-memory repository alebo fake clock. Pozri [Mocks, stubs a fakes](docs/04-testing-and-quality/mocks-stubs-fakes.md).

## False negative — testing

Výsledok, pri ktorom test prejde, hoci systém obsahuje chybu relevantnú pre testovaný risk. Pozri [Verification vs. validation](docs/04-testing-and-quality/verification-vs-validation.md).

## False negative — vulnerability finding

Stav, keď detection mechanism neidentifikuje vulnerability alebo affected asset, ktorý v skutočnosti existuje. Pozri [Vulnerability a patch management](docs/13-security-and-identity/vulnerability-and-patch-management.md).

## False positive — testing

Výsledok, pri ktorom test hlási chybu, hoci testované správanie je správne. Pozri [Verification vs. validation](docs/04-testing-and-quality/verification-vs-validation.md).

## False positive — vulnerability finding

Finding označujúci asset ako vulnerable, hoci affected code, configuration alebo exploitable condition v danom runtime neexistuje. Pozri [Vulnerability a patch management](docs/13-security-and-identity/vulnerability-and-patch-management.md).

## Fan-in — pipeline

Bod pipeline grafu, v ktorom downstream job čaká na výsledky viacerých upstream jobs alebo shards. Pozri [Reusable a parallel pipelines](docs/05-ci-cd-and-release/reusable-and-parallel-pipelines.md).

## Fan-out — pipeline

Rozdelenie jedného vstupu, artifactu alebo test suite do viacerých paralelných jobs. Pozri [Reusable a parallel pipelines](docs/05-ci-cd-and-release/reusable-and-parallel-pipelines.md).

## Fast burn

Prudké spotrebúvanie error budgetu signalizujúce významný krátkodobý user impact a potrebu rýchlej reakcie. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Fast-forward

Aktualizácia refu, pri ktorej je starý tip ancestor nového tipu, takže sa ref iba posunie bez odstránenia existujúcej ancestry. Pozri [Commit, branch, tag a HEAD](docs/03-git-and-automation/commit-branch-tag-head.md).

## Fast Snapshot Restore — EBS

Platená EBS feature enabled pre konkrétny snapshot a Availability Zone, ktorá umožňuje volumes vytvorené zo snapshotu poskytovať plný provisioned výkon bez lazy first-read initialization latency. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Fault injection

Kontrolované zavedenie konkrétneho failure condition, napríklad latency, process termination, resource pressure alebo dependency erroru. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Fault injection — CKA lab

Kontrolované zavedenie jednej alebo viacerých známych porúch do disposable lab prostredia na tréning diagnostiky a recovery. Pozri [CKA troubleshooting drills](docs/10-helm-and-cka/cka-troubleshooting-drills.md).

## Fault tolerance

Schopnosť systému pokračovať vo funkcii pri zlyhaní componentu prostredníctvom redundancy, replication, automatic failover, isolation a controlled retry. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Feasible Node

Node, ktorý prešiel všetkými aktívnymi scheduler filter constraints pre konkrétny Pod a môže pokračovať do scoring fázy. Pozri [Scheduling](docs/09-kubernetes/scheduling.md).

## Feature branch

Dočasná branch určená na izolovaný vývoj jednej zmeny. Pri trunk-based modeli má byť krátkodobá a často integrovaná. Pozri [Branching strategies](docs/03-git-and-automation/branching-strategies.md).

## Feature flag

Runtime control oddeľujúci deployment kódu od sprístupnenia capability pomocou versionovaného evaluation pravidla. Pozri [Feature flags](docs/05-ci-cd-and-release/feature-flags.md).

## Federation

Trust model, v ktorom relying party prijíma authentication assertion alebo token od samostatne spravovaného identity provider-a. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Federation — Prometheus

Hierarchický model, v ktorom jeden Prometheus scrape-ne vybrané series z federation endpointu iného Prometheus servera. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Feedback loop

Cesta od vykonanej zmeny k informácii o jej výsledku. Pozri [Feedback Loops](docs/00-foundations/feedback-loops.md).

## Field — Grafana

Jedna typed column alebo series v Grafana data frame s values, labels a display konfiguráciou. Pozri [Grafana](docs/12-observability/grafana.md).

## Field manager — Kubernetes

Identita declarative alebo programmatic writera zaznamenaná v `managedFields`, ktorá vlastní konkrétne object fields pri server-side apply. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## File capability

Capability metadata uložené na executable súbore v extended attribute. Pozri [Linux capabilities](docs/01-linux-and-systems/linux-capabilities.md).

## File descriptor

Malé celé číslo v procese odkazujúce na kernelom spravovaný otvorený objekt. Pozri [Shell, Bash, pipes, redirection a exit codes](docs/01-linux-and-systems/shell-bash-pipes-redirection-exit-codes.md).

## File-type variable — GitLab

CI/CD variable, ktorej hodnota je zapísaná do dočasného súboru a environment variable obsahuje path k tomuto súboru. Pozri [Variables a secrets](docs/06-gitlab/variables-and-secrets.md).

## Filesystem

Štruktúra mapujúca pathname na metadata a dátové bloky. Pozri [Filesystem hierarchy, inodes a links](docs/01-linux-and-systems/filesystem-hierarchy-inodes-links.md).

## Filesystem buffering — Fluent Bit

Buffering telemetry chunks na local filesystem na zvýšenie backlog capacity a restart recovery oproti memory-only modelu. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Filter plugin — Kubernetes scheduler

Scheduling Framework plugin vyhodnocujúci, či konkrétny Node spĺňa hard constraints Podu. Pozri [Scheduling](docs/09-kubernetes/scheduling.md).

## Final stage — Dockerfile

Stage, ktorého filesystem a image config tvoria publikovaný runtime image; má obsahovať iba potrebné runtime artifacts a dependencies. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## Finalizer — Kubernetes

Qualified metadata string blokujúci finálne odstránenie objectu, kým zodpovedný controller nedokončí cleanup a finalizer neodstráni. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## FinOps

Operating model spájajúci engineering, finance a business pri rozhodovaní o cloud value, cost, usage a trade-offoch. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Firing alert

Alert instance, ktorej condition zostala aktívna podľa požadovaných time semantics a je pripravená na notification routing. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## First-attempt pass rate

Podiel testov, ktoré prejdú na prvý pokus bez retry. Je citlivejším signálom flakiness než finálna pass rate po opakovaniach. Pozri [Flaky tests a test data](docs/04-testing-and-quality/flaky-tests-and-test-data.md).

## Flag debt

Kumulovaná komplexita starých feature flags, paralelných code paths, kombinácií stavov, testov a prevádzkových rozhodnutí po prekročení plánovaného lifecycle. Pozri [Feature flags](docs/05-ci-cd-and-release/feature-flags.md).

## Flag evaluation

Runtime rozhodnutie o variante alebo hodnote feature flagu na základe flag verzie, identity, environmentu a targeting pravidiel. Pozri [Feature flags](docs/05-ci-cd-and-release/feature-flags.md).

## Flaky test

Test, ktorý pri rovnakom kóde a deklarovaných vstupoch nedeterministicky prechádza alebo zlyháva. Pozri [Flaky tests a test data](docs/04-testing-and-quality/flaky-tests-and-test-data.md).

## Flexible Single Master Operations — FSMO

AD DS roles určené pre operácie, ktoré nemajú byť vykonávané súčasne viacerými domain controllers. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Flow control

TCP mechanizmus chrániaci receiver pred odosielaním väčšieho množstva dát, než dokáže prijať. Pozri [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md).

## Flow log — CNI

Dataplane observability záznam o povolenom alebo zamietnutom network flowe vrátane source/destination identity, portu, policy a action metadata podľa CNI implementácie. Pozri [CNI a NetworkPolicy](docs/09-kubernetes/cni-networkpolicy.md).

## Fluent Bit

Ľahký telemetry agent na inputs, parsing, filtering, buffering, routing a export logs, metrics a traces. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Folder permission — Grafana

Prístupové pravidlo pre dashboardy a folders; samo osebe nemusí obmedziť možnosť queryovať underlying data source. Pozri [Grafana](docs/12-observability/grafana.md).

## Force unlock — Terraform

Riziková operácia odstránenia backend locku podľa lock ID bez ukončenia pôvodného procesu; smie sa použiť iba po potvrdení, že pôvodný writer už neexistuje. Pozri [Remote backend a state locking](docs/07-infrastructure-as-code-and-configuration-management/remote-backend-and-state-locking.md).

## Force-with-lease

Bezpečnejšia forma force pushu, ktorá aktualizuje remote ref iba vtedy, keď stále zodpovedá očakávanej hodnote. Stále ide o history rewrite. Pozri [Clone, fetch, pull a push](docs/03-git-and-automation/clone-fetch-pull-push.md).

## Forest — AD DS

Najvyššia AD DS logical a významná security boundary združujúca domains so spoločnou schema, configuration a Global Catalog modelom. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Forest recovery

Koordinovaný recovery proces na obnovu dôveryhodného AD DS forest-u po rozsiahlej corruption alebo compromise udalosti. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Forward-fix migration

Nová databázová migration opravujúca chybný alebo neúplný aktuálny stav bez pokusu mechanicky vrátiť predchádzajúcu schema. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Forward proxy

Proxy zastupujúci klienta pri komunikácii s externými servermi. Pozri [Proxy a reverse proxy](docs/02-networking-and-web/proxy-and-reverse-proxy.md).

## Forward secrecy

Vlastnosť key-establishment modelu, pri ktorej neskorší compromise dlhodobého private keyu neumožní dešifrovať predtým zachytené sessions. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## FQCN — Ansible

Fully Qualified Collection Name explicitne identifikujúci module, plugin alebo iný content cez namespace, collection a object name, napríklad `ansible.builtin.template`. Pozri [Modules, tasks, plays a playbooks](docs/07-infrastructure-as-code-and-configuration-management/modules-tasks-plays-playbooks.md).

## Front-channel logout

OIDC logout model využívajúci browser na komunikáciu s logout endpoints jednotlivých clients. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md).

## `fsGroup`

Pod security context group identity používaná pri ownership a access nastavení podporovaných mounted volumes. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## Fulcio

Sigstore certificate authority vydávajúca short-lived code-signing certificates pre overené OIDC identities. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Game day

Plánované tímové resilience cvičenie kombinujúce technické faults, observability, incident response, komunikáciu a následné learning actions. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Garbage collection — Kubernetes

Control-plane proces odstraňujúci dependent objects podľa owner references a deletion propagation policy. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Garbage collection — registry

Proces odstraňovania manifestov alebo blobs, ktoré už nie sú reachable z retained references, vykonávaný s koordináciou voči pushes, deletes, referrers a retention policy. Pozri [Registries](docs/08-container-fundamentals-and-docker/registries.md).

## Gatekeeper

Kubernetes-native policy controller využívajúci OPA Constraint Framework na validation, mutation, audit a viac enforcement points. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Gatekeeper audit

Periodické vyhodnotenie existujúcich Kubernetes resources proti Gatekeeper constraints na detekciu pre-existing alebo drifted violations. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Gateway API

Kubernetes SIG Network API family s role-oriented modelom GatewayClass, Gateway a Routes pre extensible a portable service networking. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## Gateway Collector

Shared OpenTelemetry Collector tier používaný na centralized sampling, routing, redaction, policy, fan-out a backend export. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Gateway endpoint — AWS

VPC endpoint integrovaný do route tables pre podporované AWS služby, typicky S3 alebo DynamoDB, bez interface-endpoint ENI modelu. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## Gateway — Gateway API

Namespaced infrastructure resource definujúci traffic entry point, listeners, addresses, TLS a pravidlá pre pripojenie Routes. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## Gateway Load Balancer — GWLB

Elastic Load Balancing variant pre transparentné smerovanie flows cez virtual network appliances pomocou GENEVE encapsulation. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## GatewayClass

Cluster-scoped Gateway API resource vyberajúci controller implementation a class-level lifecycle pre Gateway objekty. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## Gauge — metric

Metric hodnota, ktorá môže rásť aj klesať a reprezentuje napríklad aktuálnu queue depth, memory usage alebo počet connections. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Generation — Kubernetes

Server-managed číslo reprezentujúce verziu relevantného desired state-u objektu; controller ho môže porovnávať s observed generation. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Generation lag

Rozdiel medzi aktuálnym `metadata.generation` a generáciou reportovanou controllerom ako spracovanou, signalizujúci zaostávajúcu reconciliation. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Git index

Binárna dátová štruktúra predstavujúca pripravovaný snapshot nasledujúceho commitu; obsahuje paths, modes, object IDs a pri konfliktoch viac stages. Pozri [Working tree, staging area a repository](docs/03-git-and-automation/working-tree-staging-repository.md).

## Git ref

Pomenovaný ukazovateľ na Git object ID, typicky commit. Príkladmi sú branches, remote-tracking refs a tags. Pozri [Git object model](docs/03-git-and-automation/git-object-model.md).

## GitLab cache

Odstrániteľná pipeline optimalizácia na znovupoužitie dependencies alebo intermediate dát; correctness pipeline nesmie závisieť od cache hitu. Pozri [Artifacts a cache](docs/06-gitlab/artifacts-and-cache.md).

## GitLab Container Registry

GitLab-integrovaný registry pre container alebo OCI images s project/group namespace, access controlom a CI/CD authentication workflowom. Pozri [Container a package registry](docs/06-gitlab/container-and-package-registry.md).

## GitLab deployment

Záznam úspešného alebo neúspešného nasadenia z pipeline jobu do konkrétneho GitLab environmentu, spojený s commitom, jobom, časom a statusom. Pozri [Environments, deployments a releases](docs/06-gitlab/environments-deployments-releases.md).

## GitLab environment

Pomenovaný runtime deployment target, ktorý môže mať URL, variables, protection, deployment history a static alebo dynamic lifecycle. Pozri [Environments, deployments a releases](docs/06-gitlab/environments-deployments-releases.md).

## GitLab group

Namespace a organizačná boundary obsahujúca projects a subgroups, ktorá môže poskytovať zdedené membership, settings, variables, runners a governance. Pozri [Projects, groups a permissions](docs/06-gitlab/projects-groups-permissions.md).

## GitLab job artifact

Súborový alebo reportový výstup konkrétneho CI/CD jobu uložený GitLabom na downstream použitie, diagnostiku alebo pipeline evidence. Pozri [Artifacts a cache](docs/06-gitlab/artifacts-and-cache.md).

## GitLab merge request

Workflow objekt spájajúci source a target branch, diff, commits, review, discussions, approvals, pipeline evidence a merge result. Pozri [Merge requests a approvals](docs/06-gitlab/merge-requests-and-approvals.md).

## GitLab namespace

Hierarchický path a ownership context pre user, group, subgroup alebo project resources v GitLabe. Pozri [Projects, groups a permissions](docs/06-gitlab/projects-groups-permissions.md).

## GitLab Package Registry

GitLab-integrovaný registry pre podporované package-manager formats a generic packages určené na versionovanú distribúciu dependencies a release assets. Pozri [Container a package registry](docs/06-gitlab/container-and-package-registry.md).

## GitLab pipeline configuration

Vyriešená deklarácia pipeline vytvorená z `.gitlab-ci.yml`, includes, defaults, rules, jobs, dependencies a execution metadata pri vzniku pipeline. Pozri [GitLab CI/CD syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md).

## GitLab project

Základná GitLab pracovná jednotka obsahujúca repository a podľa konfigurácie merge requests, issues, CI/CD, variables, registries, environments, security a membership. Pozri [Projects, groups a permissions](docs/06-gitlab/projects-groups-permissions.md).

## GitLab Release

GitLab objekt viazaný typicky na Git tag, ktorý zhromažďuje release name, notes, timestamp, asset links a distribučno-prevádzkové metadata bez rebuildu artifactov. Pozri [Environments, deployments a releases](docs/06-gitlab/environments-deployments-releases.md).

## GitLab Runner

Agent, ktorý prijíma eligible CI/CD jobs z GitLabu a vykonáva ich pomocou nakonfigurovaného executora v definovanej trust boundary. Pozri [Runners a executors](docs/06-gitlab/runners-and-executors.md).

## GitLab SAST

Static Application Security Testing integrované do GitLab CI/CD na detekciu potenciálnych vulnerabilities v source code pomocou language-specific analyzers a rules. Pozri [Security scanning](docs/06-gitlab/security-scanning.md).

## Global Catalog

AD DS capability obsahujúca partial attribute set z objects naprieč forestom pre forest-wide search a vybrané authentication/group-resolution scenáre. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Global group — AD DS

AD DS group scope typicky obsahujúci accounts z rovnakej domény a používaný na reprezentovanie business alebo job membership. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Global ordinals

Lucene/Elasticsearch/OpenSearch dátová štruktúra urýchľujúca aggregations nad keyword values, ktorej memory a build cost rastie pri high-cardinality fields. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Global resource — AWS

AWS resource alebo service control scope, ktorý nie je viazaný iba na jeden Region; konkrétne data-plane, endpoint a consistency semantics treba overiť v service dokumentácii. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## Global template namespace — Helm

Spoločný namespace named templates kompilovaných z parent chartu a všetkých subcharts; rovnaké helper name môže byť prepísané inou definition. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Global value — Helm

Value uložená pod top-level `global`, ktorú môžu čítať parent chart aj subcharts; je vhodná iba pre explicitný cross-chart contract. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Globbing

Shell expansion, ktorá nahrádza wildcard pattern paths zodpovedajúcimi filesystem entries. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md).

## Golden image

Versionovaný immutable machine image obsahujúci vopred zostavený a otestovaný základ systému; configuration tool môže image vytvoriť a provisioning tool nasadiť jeho konkrétnu verziu. Pozri [Terraform vs. Ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md).

## Golden path

Podporovaný a automatizovaný spôsob vývoja a delivery poskytujúci bezpečné defaults, reusable tooling, observability a policy guardrails. Pozri [Shift-left](docs/04-testing-and-quality/shift-left.md).

## Golden Signals

Google SRE monitoring model pozostávajúci zo Latency, Traffic, Errors a Saturation pre user-facing workload. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Graceful degradation

Schopnosť systému pri nedostupnosti časti dependencies zachovať obmedzenú, ale stále užitočnú a bezpečnú funkcionalitu namiesto úplného zlyhania. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Graceful shutdown

Riadené ukončenie, pri ktorom proces prestane prijímať novú prácu, bezpečne spracuje alebo preruší rozpracovaný stav, uvoľní resources a vráti správny status. Pozri [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Graceful shutdown — telemetry agent

Riadené ukončenie inputov, flush queued chunks a uloženie offset state-u pred zastavením agenta. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Grafana

Platforma na queryovanie, vizualizáciu, alerting a interaktívne skúmanie telemetry z externých data sources. Pozri [Grafana](docs/12-observability/grafana.md).

## Grafana correlation

Konfigurácia prepájajúca fields a query context medzi metrics, logs, traces alebo ďalšími data sources počas investigation. Pozri [Grafana](docs/12-observability/grafana.md).

## Grafana Explore

Ad hoc query a investigation workspace na interaktívne skúmanie metrics, logs a traces bez vytvorenia dashboardu. Pozri [Grafana](docs/12-observability/grafana.md).

## Grafana expression

Server-side alebo alerting calculation nad výsledkami jednej či viacerých data-source queries, napríklad math, reduce, resample alebo threshold. Pozri [Grafana](docs/12-observability/grafana.md).

## Grafana HA

Multi-instance Grafana deployment so spoločnou podporovanou SQL database, konzistentnou configuration, plugins a load-balancing modelom. Pozri [Grafana](docs/12-observability/grafana.md).

## Grafana-managed alert

Alert rule uložená a vyhodnocovaná Grafana alerting engine-om nad podporovanými data sources a expressions. Pozri [Grafana](docs/12-observability/grafana.md).

## Grafana notification policy

Routing a grouping policy Grafana Alerting, ktorá mapuje alert instances na contact points podľa labels a inheritance. Pozri [Grafana](docs/12-observability/grafana.md).

## Grafana panel

Základný dashboard component kombinujúci query, transformations, field configuration a visualization. Pozri [Grafana](docs/12-observability/grafana.md).

## Grafana variable

Dashboard placeholder získaný z query, custom listu alebo iného source-u a interpolovaný do queries, titles alebo links. Pozri [Grafana](docs/12-observability/grafana.md).

## Grafana variable interpolation

Nahradenie variable jej aktuálnou hodnotou pred odoslaním query data source-u, vrátane data-source-specific escaping a formatting. Pozri [Grafana](docs/12-observability/grafana.md).

## Graph-shaping value — Terraform

Hodnota, ktorá určuje samotnú množinu alebo identity graph objektov, napríklad `count` alebo `for_each` keys, a preto musí byť známa pred apply. Pozri [Expressions a dependency graph](docs/07-infrastructure-as-code-and-configuration-management/expressions-and-dependency-graph.md).

## Gratuitous ARP

ARP announcement používaný napríklad na aktualizáciu neighbor caches po presune virtual IP. Pozri [Ethernet, MAC a ARP](docs/02-networking-and-web/ethernet-mac-arp.md).

## Greedy quantifier — regex

Regex quantifier, ktorý najprv spotrebuje najväčší možný rozsah a podľa potreby backtrackuje. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Group interval

Minimálny interval pred ďalšou notification aktualizáciou existujúcej Alertmanager group po zmene jej alert setu. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Group Managed Service Account — gMSA

AD DS managed service identity s automatizovanou password lifecycle správou pre podporované Windows services a hosts. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Group sharing — GitLab

Udelenie accessu projektu alebo group členom inej group s definovaným maximum role scope-om. Pozri [Projects, groups a permissions](docs/06-gitlab/projects-groups-permissions.md).

## Group wait

Čas, ktorý Alertmanager čaká pred prvou notification novej alert group, aby mohol zhromaždiť súvisiace alerts alebo inhibiting parent alert. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## GroupVersionKind — GVK

Trojica API group, version a kind identifikujúca schema Kubernetes objectu, napríklad `apps/v1, Deployment`. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## GroupVersionResource — GVR

Trojica API group, version a REST resource name identifikujúca Kubernetes API endpoint, napríklad `apps/v1/deployments`. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## gRPC probe

Kubernetes probe používajúca gRPC Health Checking Protocol na overenie startup, liveness alebo readiness služby na Pod endpoint-e. Pozri [Probes](docs/09-kubernetes/probes.md).

## Guaranteed QoS

Kubernetes QoS class pre Pod, ktorého relevantné containers majú CPU a memory requests rovné limits podľa QoS pravidiel. Pozri [Requests, limits a QoS](docs/09-kubernetes/requests-limits-qos.md).

## Guardrail metric

Metrika chrániaca experiment alebo rollout pred neprijateľným vedľajším dopadom, aj keď primary metric vyzerá pozitívne. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Guest operating system

Operačný systém bežiaci vo virtual machine nad virtualizovaným hardware a vlastným guest kernelom. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Handler deduplication — Ansible

Správanie, pri ktorom viac notifications rovnakého handlera v príslušnej handler phase vedie typicky k jednému vykonaniu handlera na host. Pozri [Handlers, loops a conditionals](docs/07-infrastructure-as-code-and-configuration-management/handlers-loops-conditionals.md).

## Handler notification — Ansible

Event vytvorený changed taskom cez `notify`, ktorý zaradí pomenovaný handler alebo `listen` topic do pending handler queue pre host. Pozri [Handlers, loops a conditionals](docs/07-infrastructure-as-code-and-configuration-management/handlers-loops-conditionals.md).

## Hard link

Ďalší directory entry odkazujúci na ten istý inode. Pozri [Filesystem hierarchy, inodes a links](docs/01-linux-and-systems/filesystem-hierarchy-inodes-links.md).

## Hard mandatory policy — Terraform

Policy as Code pravidlo blokujúce plan alebo apply bez bežného override pathu, používané pre stabilné invariants s vysokým rizikom porušenia. Pozri [Terraform testing a policy](docs/07-infrastructure-as-code-and-configuration-management/terraform-testing-and-policy.md).

## Hard validation — CKA

Explicitný command alebo observable criterion dokazujúci, že úloha spĺňa požadovaný stav a constraints, nie iba že resource existuje. Pozri [CKA timed labs](docs/10-helm-and-cka/cka-timed-labs.md).

## Hardware Security Module — HSM

Tamper-resistant hardware alebo managed security boundary určená na generovanie, ochranu a vykonávanie cryptographic operations s obmedzeným exportom private alebo symmetric key materialu. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## `hasKey` — Helm

Map function rozlišujúca neprítomný key od prítomnej hodnoty ako `false`, `0` alebo empty string. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Head block — Prometheus

Aktívna in-memory a WAL-backed časť Prometheus TSDB obsahujúca najnovšie samples pred vytvorením immutable blockov. Pozri [Prometheus](docs/12-observability/prometheus.md).

## HEAD — Git

Špeciálny ref reprezentujúci aktuálnu checkout pozíciu. Typicky symbolicky ukazuje na current branch, ale môže ukazovať priamo na commit. Pozri [Commit, branch, tag a HEAD](docs/03-git-and-automation/commit-branch-tag-head.md).

## Head sampling

Trace sampling decision vykonané na začiatku trace-u pred poznaním finálneho outcome-u a celkovej latency. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Headless Service

Kubernetes Service s `clusterIP: None`, ktorého DNS typicky publikuje priamo endpoint addresses namiesto jednej virtuálnej ClusterIP. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## Headless Service DNS

A/AAAA alebo SRV records headless Service-u vracajúce priamo backend alebo per-Pod identities, pričom client nesie selection a failover zodpovednosť. Pozri [Cluster DNS](docs/09-kubernetes/cluster-dns.md).

## Health check

Aktívny alebo pasívny test určujúci, či backend môže prijímať nový traffic. Pozri [Load balancing](docs/02-networking-and-web/load-balancing.md).

## health-check matcher — ELB

Sada HTTP success codes alebo iné protocol-specific kritérium, podľa ktorého target-group health check vyhodnotí odpoveď ako úspešnú. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## Health start period

Warm-up interval healthchecku, počas ktorého startup failures nemusia prispievať k označeniu containeru za unhealthy podľa health configuration. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Helm

Kubernetes package, templating a release-lifecycle tool, ktorý renderuje charts na Kubernetes manifests a uchováva release metadata bez vlastného serverového Tiller componentu. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Helm chart

Versionovaný balík obsahujúci `Chart.yaml`, default values, Kubernetes templates, voliteľné CRDs, dependencies a pomocné files. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Helm chart dependency

Chart deklarovaný alebo vendored ako súčasť parent chartu, ktorého templates a resources sa agregujú do rovnakého Helm release-u. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## `helm dependency build`

Command rekonštruujúci `charts/` podľa existujúceho `Chart.lock` bez nového version negotiation, pokiaľ lock existuje. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## `helm dependency update`

Command re-resolvujúci dependency constraints z `Chart.yaml`, aktualizujúci `charts/` a generujúci alebo meniaci `Chart.lock`. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Helm drift triage

Porovnanie posledného release manifestu, navrhovaného renderu a live Kubernetes objectu na identifikáciu authoritative writera a zdroja rozdielu. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Helm hook

Kubernetes resource template označený annotation `helm.sh/hook`, ktorý Helm vykoná v konkrétnom bode install, upgrade, rollback, delete alebo test lifecycle. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Helm merge

Template operation spájajúca dictionaries podľa konkrétnej direction a overwrite semantics; pri nested maps môže vyžadovať `deepCopy`, aby sa zabránilo neúmyselnej mutation vstupu. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Helm partial

Reusable template fragment, typicky uložený v underscore-prefixed súbore ako `_helpers.tpl`, ktorý sám nevytvára Kubernetes manifest. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Helm pipeline

Template expression, v ktorom sa výsledok ľavej časti posiela ako posledný argument nasledujúcej funkcie. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Helm release

Konkrétna pomenovaná inštancia chartu nasadená do Kubernetes namespace-u s effective values, rendered manifestom, statusom a revision history. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Helm release revision

Sekvenčné číslo konkrétnej install, upgrade alebo rollback verzie Helm release-u; nie je to Kubernetes Deployment revision ani Git commit. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Helm release state

Metadata, chart/configuration a rendered manifest uložené Helm storage driverom v clustri pre konkrétnu release revision. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Helm rollback

Operácia vytvárajúca novú release revision podľa historickej revision; nepredstavuje automatický návrat durable alebo external state-u. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Helm subchart

Stand-alone chart vložený ako dependency parent chartu, s vlastným values scope-om a templates, ale spoločným výsledným release lifecycle. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Helm template

Go-template source file v chart `templates/` directory, ktorý Helm renderuje s values, release metadata a cluster capabilities na Kubernetes manifest. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Helm template function

Funkcia dostupná v Helm template engine z Go templates, Sprig alebo Helm-specific extension, ktorá transformuje input na textový alebo štruktúrovaný render output. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Helm test pyramid

Viacvrstvový chart validation model od metadata, schema a render checks cez server validation až po ephemeral cluster, test hooks a application end-to-end testy. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Helm troubleshooting decision tree

Rozdelenie Helm incidentu na fetch/dependency, values/schema, render, API/admission, hook, release-state, wait alebo následný Kubernetes workload failure. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Helm upgrade

Operácia vytvárajúca novú release revision z chartu, dependencies, effective values a render contextu a aplikujúca výsledný manifest do clusteru. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Helper contract — Helm

Dokumentovaný input scope, očakávané keys, output shape, whitespace a stability semantics named template helpera. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Helper scope — Helm

Object odovzdaný named template-u cez `template` alebo `include`, ktorý určuje význam `.` aj root symbolu `$` vo vnútri helpera. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## `_helpers.tpl`

Konvenčný underscore-prefixed súbor v `templates/` určený na definitions reusable named templates, ktorý sa sám nerenderuje ako Kubernetes manifest. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Hermetic build

Build, ktorý získava všetky inputs cez deklarovaný a kontrolovaný mechanism bez nezdokumentovaného host alebo network dependency accessu. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Hermetic test

Test, ktorý kontroluje všetky významné vstupy a nespolieha sa na nepredvídateľný externý stav. Môže používať disposable reálne dependencies. Pozri [Unit, integration a component tests](docs/04-testing-and-quality/unit-integration-component-tests.md).

## Hidden job — GitLab CI/CD

Top-level CI configuration block s názvom začínajúcim bodkou, ktorý sa nespúšťa priamo a slúži ako reusable configuration pre `extends` alebo references. Pozri [GitLab CI/CD syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md).

## Hidden queue

Čakacia vrstva, ktorá nie je viditeľná v hlavnom service dashboarde, napríklad connection pool, thread pool, kernel queue alebo downstream scheduler. Pozri [USE method](docs/12-observability/use-method.md).

## Hidden variable — GitLab

Masked CI/CD variable, ktorej hodnotu po uložení nemožno znovu zobraziť v GitLab UI; job s prístupom ju však stále môže použiť. Pozri [Variables a secrets](docs/06-gitlab/variables-and-secrets.md).

## High availability — HA

Architektonická schopnosť minimalizovať prerušenie služby pri očakávateľných component, host alebo zonal failures pomocou redundancy, health checks a failoveru. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## High-risk issue — Well-Architected

Významná odchýlka od Well-Architected best practices s relevantným security, reliability, operations, performance, cost alebo sustainability rizikom. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Histogram — metric

Metric aggregation zaznamenávajúca počet observations v definovaných buckets spolu s count a typicky sum, vhodná na latency distributions a threshold SLIs. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## History rewrite

Operácia vytvárajúca nové commit objects a meniaca branch-visible ancestry, napríklad rebase, amend alebo reset publikovanej branch. Pozri [Merge a rebase](docs/03-git-and-automation/merge-and-rebase.md).

## Hook delete policy — Helm

Annotation `helm.sh/hook-delete-policy` určujúca cleanup hook resource-u pred ďalším spustením, po úspechu alebo po failure. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## `hook-failed` — Helm

Hook delete-policy hodnota požadujúca odstránenie hook resource-u po neúspešnom vykonaní; môže znížiť dostupnosť incident evidence. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Hook idempotency — Helm

Vlastnosť hook operácie, pri ktorej opakované alebo čiastočne dokončené vykonanie bezpečne konverguje bez duplicitných side effects. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Hook lifecycle point — Helm

Konkrétny release moment, napríklad `pre-install`, `post-upgrade` alebo `pre-delete`, v ktorom Helm spustí označený hook resource. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Hook readiness — Helm

Podmienka, pri ktorej Helm považuje hook za dokončený; pri Job alebo Pod hooku čaká na úspešné completion, pri mnohých iných resource kinds stačí úspešné API načítanie. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Hook resource retention — Helm

Lifecycle rozhodnutie, ako dlho ponechať dokončený alebo failed hook resource pre audit a diagnostiku a kedy ho odstráni delete policy alebo Kubernetes TTL. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Hook side effect — Helm

Zmena external alebo durable state-u vykonaná hookom, napríklad database migration, backup alebo API registrácia, ktorú Helm manifest rollback nemusí automaticky zvrátiť. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## `hook-succeeded` — Helm

Hook delete-policy hodnota požadujúca odstránenie hook resource-u po úspešnom vykonaní. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Hook weight — Helm

Stringovo zapísané číslo v annotation `helm.sh/hook-weight`, podľa ktorého Helm vykonáva hooks od nižšej hodnoty k vyššej. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Hop limit

IPv6 field znižovaný na každom router hop-e; IPv4 ekvivalentom je TTL. Pozri [IPv4, IPv6 a subnetting](docs/02-networking-and-web/ipv4-ipv6-subnetting.md).

## Horizontal Pod Autoscaler — HPA

Kubernetes API resource a controller automaticky meniaci replica count škálovateľného workloadu podľa resource, custom alebo external metrics. Pozri [HPA a autoscaling](docs/09-kubernetes/hpa-autoscaling.md).

## Horizontal scaling

Pridanie alebo odobratie instances, workers, replicas alebo partitions s potrebným traffic distribution a state coordination modelom. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Host bind address — Docker

Host IP adresa, na ktorej Docker publikuje port, napríklad `127.0.0.1` pre local-only alebo `0.0.0.0` pre všetky IPv4 interfaces. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Host key — SSH host key

Kryptografický kľúč, ktorým SSH server preukazuje svoju identitu klientovi. Pozri [SSH](docs/01-linux-and-systems/ssh.md).

## Host network mode

Container runtime mode zdieľajúci host network namespace, čím odstraňuje bežnú container network izoláciu a vytvára priame host port, interface a traffic exposure. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Host port — container

Port a bind address v host network namespace, ktorý forwarding alebo proxy mechanizmus mapuje na container port. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## hosted zone — Route 53

Container authoritative DNS records pre konkrétny public alebo private DNS namespace. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## `hostvars` — Ansible

Magic mapping poskytujúci prístup k host-scoped variables iných inventory hosts; jeho použitie vytvára cross-host coupling a závisí od dostupnosti dát. Pozri [Variables, facts a templates](docs/07-infrastructure-as-code-and-configuration-management/variables-facts-templates.md).

## HPA tolerance

Mŕtve pásmo okolo cieľovej metric hodnoty, v ktorom HPA nemusí meniť replica count, aby obmedzil drobné oscillations. Pozri [HPA a autoscaling](docs/09-kubernetes/hpa-autoscaling.md).

## HSTS — HTTP Strict Transport Security

Browser policy oznamujúca, že doména sa má používať iba cez HTTPS počas definovaného času. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## HTTP

Aplikačný request-response protokol s methods, status codes, headers a representation semantics. Pozri [HTTP](docs/02-networking-and-web/http.md).

## HTTP/2

HTTP verzia používajúca binary framing a multiplexované streams nad jedným TCP connection. Pozri [HTTP](docs/02-networking-and-web/http.md).

## HTTP/3

HTTP verzia používajúca QUIC nad UDP s nezávislejším stream loss recovery modelom. Pozri [HTTP](docs/02-networking-and-web/http.md).

## HTTP probe

Kubernetes probe vykonávajúca HTTP alebo HTTPS request na Pod IP a nakonfigurovaný port/path z kubelet network perspektívy. Pozri [Probes](docs/09-kubernetes/probes.md).

## HTTPRoute

Gateway API Route resource pre HTTP routing cez host, path, header alebo query matching, backend references, traffic weights a filters. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## Huge pages — Kubernetes

Predalokované veľké memory pages publikované Node-om ako page-size-specific nekompresibilný resource. Pozri [Requests, limits a QoS](docs/09-kubernetes/requests-limits-qos.md).

## Hybrid cloud

Deployment model integrujúci public-cloud services s on-premises, colocation alebo edge resources cez networking, identity, DNS, data a management contracts. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Hybrid connectivity

Network boundary prepájajúca cloud a externé prostredie cez VPN, dedicated link, public endpoint alebo private service endpoint s explicitným routing, encryption a redundancy modelom. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Hypercare

Dočasne zvýšená prevádzková a support pozornosť po významnom release, vrátane posilneného monitoringu, owner dostupnosti a rýchleho rozhodovacieho pathu. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Hypervisor

Virtualization vrstva poskytujúca virtual hardware a izoláciu pre virtual machines. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## IaaS

Infrastructure as a Service: cloud model poskytujúci virtualizované compute, storage a networking primitives, pričom zákazník typicky vlastní guest OS, runtime, application a data lifecycle. Pozri [IaaS, PaaS a SaaS](docs/11-cloud-and-aws/iaas-paas-saas.md).

## IaC scanning

Statická alebo plan-level kontrola Infrastructure as Code proti syntax, schema, security a policy pravidlám. Pozri [Security a infrastructure tests](docs/04-testing-and-quality/security-and-infrastructure-tests.md).

## IAM

Disciplína a platformové capabilities na správu identities, credentials, authentication, authorization, federation, provisioning, privileged access, review a audit. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## IAM Access Analyzer

AWS IAM capability na analýzu external accessu, policy validation a vybrané unused-access alebo policy-generation workflows. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## IAM database authentication — RDS

RDS authentication model pre podporované engines, pri ktorom client generuje krátkodobý signed token cez IAM namiesto dlhodobého database passwordu. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## IAM Identity Center

AWS služba pre centralizovaný workforce access, permission sets a federované temporary sessions do viacerých AWS accounts. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## `iam:PassRole`

Citlivá IAM action umožňujúca principalu odovzdať role AWS službe; musí byť obmedzená na presné roles a destination services. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## IAM principal

Autentifikovaná alebo identifikovateľná AWS request identity, napríklad root user, IAM user, role session, federated principal alebo service principal. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## IAM role

AWS identity s trust policy a permissions policy modelom, ktorú principal preberá a používa cez temporary session credentials. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## IAM role trust policy

Resource-based policy role určujúca, ktoré principals a za akých conditions môžu role assume-nuť. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## IAM session policy

Policy odovzdaná pri vytváraní temporary session, ktorá môže zúžiť, ale nie rozšíriť permissions nad role a ostatné guardrails. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## IAST — Interactive Application Security Testing

Security analýza využívajúca runtime informácie z instrumentovanej aplikácie počas testov. Pozri [Security a infrastructure tests](docs/04-testing-and-quality/security-and-infrastructure-tests.md).

## ID Token

Signed OIDC JWT určený Relying Party, ktorý obsahuje issuer, subject, audience a authentication context claims. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md).

## ID token — GitLab CI/CD

Krátkodobý signed OIDC token vydaný jobu s definovaným audience a claims, používaný na federované overenie voči cloud alebo secret provideru. Pozri [Variables a secrets](docs/06-gitlab/variables-and-secrets.md).

## Idempotencia

Vlastnosť operácie, pri ktorej opakovanie s rovnakým vstupom vedie k rovnakému výslednému stavu. Pozri [Idempotency](docs/00-foundations/idempotency.md).

## Idempotency key

Client-generated identifikátor umožňujúci serveru rozpoznať opakovaný ne-idempotentný request a vrátiť konzistentný výsledok. Pozri [REST APIs a WebSockets](docs/02-networking-and-web/rest-apis-and-websockets.md).

## Idempotency test — Ansible

Test vykonávajúci po prvom converge ďalší run s rovnakými inputs a overujúci, že nevzniknú neplánované changes ani side effects. Pozri [Ansible idempotencia](docs/07-infrastructure-as-code-and-configuration-management/ansible-idempotency.md).

## Idempotent batch execution

Batch návrh, pri ktorom opakované alebo duplicitné vykonanie toho istého logical work itemu nevytvorí nekonzistentné dodatočné side effects. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Idempotent reconcile

Controller behavior, pri ktorom opakované spracovanie rovnakého desired a actual state-u nevytvára neplánované duplicity alebo ďalšie side effects. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Identity

Reprezentácia osoby, workloadu, zariadenia alebo organizácie používaná naprieč identity a access lifecycle-om. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Identity-aware proxy

Proxy acting as PEP, ktorá autentizuje subject, vyhodnotí policy a sprostredkuje access ku konkrétnej application bez implicitnej network trust. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Identity-based policy — AWS

IAM policy pripojená k userovi, group alebo role, ktorá povoľuje alebo denyuje actions nad resources podľa request contextu. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## Identity proofing

Proces zhromažďovania a overovania evidence, ktorým sa digitálna identita spoľahlivo priraďuje reálnej osobe alebo entite. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Identity Provider — SAML

SAML entita autentizujúca principal-a a vydávajúca signed assertions. Pozri [SAML](docs/13-security-and-identity/saml.md).

## `ignore_changes` — Terraform

Lifecycle rule, ktorá pri update plánovaní ignoruje zmeny vybraných atribútov. Musí mať explicitný external owner a monitoring, pretože potláča Terraform remediation, nie existenciu driftu. Pozri [Lifecycle, import a moved blocks](docs/07-infrastructure-as-code-and-configuration-management/lifecycle-import-moved-blocks.md).

## Image configuration — OCI

OCI JSON artifact obsahujúci platform, runtime defaults, environment, entrypoint/command, user, rootfs diff IDs a build history metadata image-u. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Image index — OCI

Manifest list odkazujúci na viac OCI manifests, typicky pre rozdielne OS, architecture a variant platformy. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Image layer

Immutable filesystem changeset v ordered image graph-e, ktorý sa skladá s ostatnými layers do výsledného root filesystemu. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## Image manifest — OCI

OCI artifact odkazujúci descriptorom na jednu image configuration a ordered list filesystem layer blobs. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Image runtime metadata — Dockerfile

Image configuration fields ako default command, entrypoint, environment, user, working directory, exposed ports, labels a stop signal použité pri vytváraní runtime containeru. Pozri [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md).

## Image signing

Cryptographic binding container image digestu na signing key alebo identity, ktorý consumer vyhodnocuje podľa verification policy. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## ImagePullSecret

Kubernetes Secret reference používaná kubeletom alebo container runtime pri autentifikovanom image pull-e; nejde o application ani ServiceAccount API credential. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md) a [ServiceAccount](docs/09-kubernetes/serviceaccount.md).

## ImageService — CRI

Časť CRI používaná kubeletom na image pull, list, status a removal operácie v container runtime. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## IMDSv2

Token-based druhá verzia EC2 Instance Metadata Service používaná na získanie instance metadata a temporary role credentials s lepšou ochranou proti niektorým SSRF a proxy útokom. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Immutable ConfigMap alebo Secret

ConfigMap alebo Secret s `immutable: true`, ktorý nemožno in-place meniť a vyžaduje nový versioned object a consumer rollout. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Immutable infrastructure

Model, v ktorom sa existujúce inštancie zásadne neupravujú, ale nahrádzajú novými. Pozri [Immutable vs. Mutable Infrastructure](docs/00-foundations/immutable-vs-mutable-infrastructure.md).

## Immutable node replacement

Upgrade alebo oprava Node-u vytvorením novej versionovanej instance, validáciou, controlled drainom starého Node-u a následným odstránením starej infraštruktúry. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Immutable tag

Registry alebo repository tag, ktorého mapping na artifact content sa po publikovaní nesmie zmeniť. Pozri [Artifact versioning](docs/05-ci-cd-and-release/artifact-versioning.md).

## Impact — security

Následok straty confidentiality, integrity alebo availability pre používateľov, organizáciu, assets alebo mission. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Imperative approach

Prístup opisujúci konkrétnu sekvenciu krokov. Pozri [Declarative vs. Imperative Approach](docs/00-foundations/declarative-vs-imperative.md).

## Imperative skeleton — CKA

Rýchlo vygenerovaný Kubernetes manifest cez imperative kubectl command s `--dry-run=client -o yaml`, ktorý sa následne deklaratívne upraví a aplikuje. Pozri [CKA timed labs](docs/10-helm-and-cka/cka-timed-labs.md).

## Impersonation

Mechanizmus, pri ktorom systém alebo administrator vykonáva action ako iný principal, pričom audit má zachovať pôvodného aj impersonovaného actora. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Implicit deny — IAM

Predvolený authorization výsledok, keď request nemá applicable explicit allow alebo neprejde potrebnými policy boundaries. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## Implicit trust

Access alebo authority udelená bez explicitného resource-specific decisionu iba na základe location, ownership, previous login alebo membership v broad zone. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Implicit typing — YAML

Automatická interpretácia plain scalaru ako boolean, number, date alebo null podľa YAML schema a parser implementácie. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Import block — Terraform

Versionovaná configuration deklarácia mapujúca existujúci remote objekt cez provider identity na konkrétnu Terraform resource instance addressu. Pozri [Lifecycle, import a moved blocks](docs/07-infrastructure-as-code-and-configuration-management/lifecycle-import-moved-blocks.md).

## `import_role`

Statické načítanie Ansible role spracované počas parse fázy, ktoré sa líši od runtime `include_role` v condition, tag a variable semantics. Pozri [Roles a collections](docs/07-infrastructure-as-code-and-configuration-management/roles-and-collections.md).

## `import-values` — Helm

Dependency declaration mechanism prenášajúci vybrané exported alebo mapped child values do parent values scope-u. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Improvement plan — Well-Architected

Prioritizovaný súbor konkrétnych remediation položiek s ownerom, target state-om a validation criteria po workload review. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## in-toto

Framework a metadata model pre zaznamenanie a overenie supply-chain steps, materials, products a autorizovaných functionaries. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## in-toto Statement

Supply-chain attestation structure obsahujúca subject digest, predicate type a predicate. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## `include` — Helm

Helm function renderujúca named template do stringu, ktorý možno ďalej spracovať v pipeline napríklad cez `nindent` alebo `sha256sum`. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## `include_role`

Dynamické načítanie Ansible role počas executionu podľa runtime contextu. Pozri [Roles a collections](docs/07-infrastructure-as-code-and-configuration-management/roles-and-collections.md).

## Index — search

Logical collection documents s vlastným mappingom, settings a shard topology. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Index stages

Viac verzií jednej path uložených v Git indexe počas konfliktu: stage 1 je merge base, stage 2 ours a stage 3 theirs. Pozri [Konflikty](docs/03-git-and-automation/merge-conflicts.md).

## Index State Management — ISM

OpenSearch policy framework na riadenie index lifecycle-u cez states, transitions a actions. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Index template

Policy aplikovaná na nové indexes alebo backing indexes podľa patternu, ktorá definuje mappings, settings a lifecycle integration. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Indexed Job

Kubernetes Job s `completionMode: Indexed`, kde každý completion slot dostáva stabilný index pre statické alebo deterministické rozdelenie práce. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Informer — Kubernetes

Client-side mechanism kombinujúci list/watch, local cache a event handlers na efektívne sledovanie Kubernetes resources pre controllers. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Infrastructure as Code — IaC

Správa infraštruktúry pomocou versionovanej deklarácie, automatizovaného plan/apply alebo reconciliation procesu, review, policy a auditovateľného recovery lifecycle. Pozri [Infrastructure as Code principles](docs/07-infrastructure-as-code-and-configuration-management/infrastructure-as-code-principles.md).

## Infrastructure policy

Policy vyhodnocujúca infrastructure source, plan, configuration alebo runtime state podľa security, compliance, cost a operational guardrails. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Ingest pipeline — search

Server-side pipeline, ktorá pred indexingom parsuje, normalizuje, enrichuje, rediguje alebo routuje documents. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Ingester — Loki

Loki write-path component, ktorý prijíma recent log entries, drží active streams a vytvára chunks pred flushom do storage. Pozri [Loki](docs/12-observability/loki.md).

## Ingress

Stable Kubernetes API resource pre HTTP/HTTPS host a path routing k Services, ktorý potrebuje samostatný Ingress controller a dataplane. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## Ingress controller

Controller a dataplane integration sledujúca Ingress resources a konfiguruje reverse proxy, load balancer alebo inú implementation. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## Ingress-isolated Pod

Pod vybraný aspoň jednou NetworkPolicy pre ingress, ktorého inbound traffic je povolený iba unionom matching ingress pravidiel. Pozri [CNI a NetworkPolicy](docs/09-kubernetes/cni-networkpolicy.md).

## IngressClass

Cluster-scoped resource určujúci, ktorý Ingress controller a class parameters spracúvajú konkrétne Ingress objekty. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## Inherited membership — GitLab

Access získaný cez membership v parent group alebo inom hierarchicky relevantnom namespace namiesto priameho pridania na project. Pozri [Projects, groups a permissions](docs/06-gitlab/projects-groups-permissions.md).

## Inhibition — Alertmanager

Automatické muting pravidlo, ktoré potlačí target alert notifications, keď firing source alert matchuje definovaný scope. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Init container

Container, ktorý musí úspešne dokončiť prípravnú úlohu pred spustením bežných application containers v Pode. Pozri [Pod](docs/09-kubernetes/pod.md).

## Inode

Filesystem objekt obsahujúci metadata a odkazy na dátové bloky. Pozri [Filesystem hierarchy, inodes a links](docs/01-linux-and-systems/filesystem-hierarchy-inodes-links.md).

## Inode exhaustion

Stav, keď filesystem nemôže vytvárať ďalšie files napriek voľnej byte capacity, čo môže narušiť image pull, logs, snapshots alebo container writes. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## InResponseTo — SAML

Identifier viažuci SAML Response alebo SubjectConfirmationData na konkrétny AuthnRequest. Pozri [SAML](docs/13-security-and-identity/saml.md).

## instance profile — EC2

IAM container, cez ktorý sa jedna IAM role pripája k EC2 instance a poskytuje jej temporary credentials cez metadata service. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## instance refresh — Auto Scaling

Riadený Auto Scaling workflow postupne nahrádzajúci fleet instances podľa novej launch template alebo desired configuration pri zachovaní nastavenej healthy capacity. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## instance store — EC2

Host-local ephemeral block storage, ktorého dáta sa môžu stratiť pri stop, termination alebo host failure. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## instance warmup — Auto Scaling

Interval reprezentujúci čas, kým newly launched instance dosiahne plnú application a metric readiness pre scaling decisions. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Instant vector — PromQL

Množina time series s jednou sample hodnotou pre každý label set v konkrétnom evaluation čase. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Instrumentation

Kód, agent, library alebo platform capability, ktorá generuje telemetry signals o správaní systému. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Instrumentation library

Knižnica, ktorá vytvára telemetry pre application, framework alebo dependency a nesie vlastný instrumentation scope. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Instrumentation scope

Logical software unit a jej version, s ktorou OpenTelemetry spája vytvorené spans, metrics a log records. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Integration test

Test reálnej spolupráce komponentov alebo systému s technickou dependency, napríklad databázou, brokerom, filesystemom alebo cloud API. Pozri [Unit, integration a component tests](docs/04-testing-and-quality/unit-integration-component-tests.md).

## Integrity — security

Ochrana accuracy, completeness a správnosti dát, konfigurácie a processingu pred neautorizovanou alebo nesprávnou zmenou. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Interaction-based testing

Testovanie, ktoré overuje komunikáciu a side effects medzi objektmi alebo komponentmi, napríklad volanie gateway s konkrétnymi argumentmi. Pozri [Mocks, stubs a fakes](docs/04-testing-and-quality/mocks-stubs-fakes.md).

## Interface endpoint — AWS

PrivateLink-based VPC endpoint vytvárajúci ENIs s private IPs v zvolených subnetoch a voliteľným private DNS modelom. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## Internal traffic policy — Service

Service policy ovplyvňujúca výber cluster-wide alebo node-local backendov pre traffic prichádzajúci z clusteru. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## Internet Gateway — AWS

Horizontálne škálovaný a vysoko dostupný VPC component poskytujúci route target pre internet-routable IPv4 a IPv6 traffic. Pozri [Internet Gateway a NAT Gateway](docs/11-cloud-and-aws/internet-gateway-nat-gateway.md).

## invalidation — CloudFront

Požiadavka na odstránenie object pathov z CloudFront edge caches pred prirodzenou TTL expiráciou. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Inventory cache — Ansible

Cache výsledkov dynamic inventory discovery, ktorá znižuje API náklady, ale vytvára freshness a stale-target riziko. Pozri [Inventory](docs/07-infrastructure-as-code-and-configuration-management/inventory.md).

## Inventory group — Ansible

Pomenovaná množina inventory hosts alebo child groups používaná na targeting, topology model a group variables. Pozri [Inventory](docs/07-infrastructure-as-code-and-configuration-management/inventory.md).

## Inventory host — Ansible

Logická target identita v Ansible inventory, ktorá môže používať samostatnú connection addressu cez `ansible_host`. Pozri [Inventory](docs/07-infrastructure-as-code-and-configuration-management/inventory.md).

## `inventory_hostname`

Stabilná logická identita hostu v Ansible inventory a host variable context-e, ktorá nemusí byť DNS alebo connection addressou. Pozri [Inventory](docs/07-infrastructure-as-code-and-configuration-management/inventory.md).

## Inventory pattern — Ansible

Expression vyberajúca hosts alebo groups pomocou union, intersection a exclusion semantics pre play alebo CLI run. Pozri [Inventory](docs/07-infrastructure-as-code-and-configuration-management/inventory.md).

## Inventory plugin — Ansible

Plugin parsujúci static alebo dynamic inventory source a vytvárajúci hosts, groups a variables v runtime inventory model-i. Pozri [Inventory](docs/07-infrastructure-as-code-and-configuration-management/inventory.md).

## Inventory source — Ansible

File, directory, plugin configuration, script alebo external source, z ktorého Ansible vytvára časť výsledného inventory. Pozri [Inventory](docs/07-infrastructure-as-code-and-configuration-management/inventory.md).

## IP packet

Network-layer jednotka obsahujúca source a destination IP adresu a payload vyššej vrstvy. Pozri [OSI a TCP/IP model](docs/02-networking-and-web/osi-and-tcp-ip-model.md).

## IPAM

IP Address Management mechanizmus prideľujúci a uvoľňujúci jedinečné Pod IP adresy a súvisiace subnet/route metadata. Pozri [CNI a NetworkPolicy](docs/09-kubernetes/cni-networkpolicy.md).

## `ipBlock` — NetworkPolicy

CIDR-based NetworkPolicy peer určený najmä pre traffic k alebo z IP rozsahov mimo selector-based Pod identity modelu; výsledok môže ovplyvniť NAT a enforcement point. Pozri [CNI a NetworkPolicy](docs/09-kubernetes/cni-networkpolicy.md).

## IPv4 private ranges

Adresy `10.0.0.0/8`, `172.16.0.0/12` a `192.168.0.0/16`, ktoré nie sú globálne routované vo verejnom Internete. Pozri [IPv4, IPv6 a subnetting](docs/02-networking-and-web/ipv4-ipv6-subnetting.md).

## IPv6 link-local address

IPv6 adresa z `fe80::/10` platná v lokálnom linkovom scope. Pozri [IPv4, IPv6 a subnetting](docs/02-networking-and-web/ipv4-ipv6-subnetting.md).

## Isolated subnet — AWS

Subnet bez všeobecného inbound internet pathu aj bez general outbound internet pathu; môže používať iba explicitné private connectivity targets. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## Isolation boundary

Technická a bezpečnostná hranica oddeľujúca workload od hosta alebo iných workloads, napríklad shared-kernel container boundary alebo hypervisor/VM boundary. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Iterator age — Lambda

Metric vyjadrujúca oneskorenie medzi vznikom stream recordu a jeho spracovaním Lambda consumerom; rast signalizuje backlog alebo pomalé spracovanie. Pozri [Lambda](docs/11-cloud-and-aws/lambda.md).

## Jaeger

Distributed tracing backend s collector, query, ingester a all-in-one roles, aktuálne postavený na OpenTelemetry Collector frameworku. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Jaeger all-in-one

Jaeger deployment role spájajúca collector a query/UI v jednom procese, vhodná najmä pre development a bounded use cases. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Jaeger collector

Jaeger role prijímajúca trace data a zapisujúca ich do storage alebo durable queue podľa deploymentu. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Jaeger ingester

Jaeger role, ktorá konzumuje spans z Kafka a zapisuje ich do trace storage. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Jaeger query

Jaeger role poskytujúca query APIs a user interface nad trace storage. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Jaeger remote sampling

Centralizovaný head-sampling model, v ktorom SDKs získavajú sampling strategies z Jaeger backendu. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Jinja template — Ansible

Textový template renderovaný typicky na control node v host-specific variable context-e a následne použitý ako configuration alebo iný artifact. Pozri [Variables, facts a templates](docs/07-infrastructure-as-code-and-configuration-management/variables-facts-templates.md).

## Jitter

Náhodná odchýlka pridaná k retry delay, ktorá znižuje synchronizované opakovanie veľkého množstva klientov. Pozri [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Job

Kubernetes workload controller, ktorý vytvára Pody a retryuje ich dovtedy, kým sa nedosiahne požadovaný completion alebo failure stav. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Job — CI/CD

Najmenšia samostatne plánovaná execution unit pipeline s vlastným runtime, inputs, permissions, commands, timeoutom, resultom a outputs. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## Job completion

Úspešne dokončený logical execution slot Jobu potvrdený Podom alebo controller statusom podľa zvoleného completion modelu. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Job history limit — CronJob

Počet úspešných alebo failed Job objektov, ktoré CronJob zachováva ako krátkodobú API históriu; nejde o dlhodobú log alebo audit retention. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Job rules — GitLab

Zhora nadol vyhodnocované podmienky, ktoré pri vytvorení pipeline rozhodujú, či job vznikne a aké `when`, variables, `needs` alebo failure správanie dostane. Pozri [GitLab CI/CD syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md).

## Joiner-mover-leaver lifecycle

Identity governance proces pre vytvorenie identity, zmenu pracovnej funkcie a úplné odstránenie accessu pri odchode. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## journald

Systémová logging služba systemd sprístupnená cez `journalctl`. Pozri [journald a logging](docs/01-linux-and-systems/journald-and-logging.md).

## JSON Schema

Deklaratívny schema jazyk na validáciu štruktúry, typov a vybraných constraints JSON dát. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Just-enough administration

Privilege model poskytujúci iba konkrétne administratívne capabilities potrebné na úlohu namiesto full admin shellu alebo broad role. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## Just-in-time access

Dočasná aktivácia privilege na obmedzený čas po splnení podmienok ako MFA, approval alebo justification. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## JWKS

JSON Web Key Set publikujúci public cryptographic keys používané napríklad na validáciu OIDC ID Token signatures. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md).

## Kafka-buffered tracing

Tracing architecture, v ktorej durable Kafka-compatible queue oddeľuje trace ingestion od storage consumers. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## KDC

Kerberos Key Distribution Center obsahujúce Authentication Service, Ticket-Granting Service a principal/key database. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Kerberos

Ticket-based network authentication protocol používajúci KDC, TGT a service tickets na vzájomnú authentication clientov a services. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Kernel space

Privilegovaná časť systému, v ktorej kernel spravuje procesy, memory, devices, filesystems a networking. Pozri [Kernel a user space](docs/01-linux-and-systems/kernel-and-user-space.md).

## Key-based signing

Signing model používajúci dlhodobejší private key a distribuovaný public key alebo certificate ako trust anchor. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Key Encryption Key — KEK

Cryptographic key používaný na wrap alebo encryption iných keys, najmä Data Encryption Keys v envelope-encryption architektúre. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## Key Management Service — KMS

Centralizovaná služba poskytujúca kontrolovaný key lifecycle, authorization, audit a cryptographic operations; nechráni automaticky application plaintext ani nesprávne decrypt permissions. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## Key policy — KMS

Resource policy priamo pripojená ku KMS key, ktorá je fundamentálnou súčasťou autorizácie management a cryptographic operations. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Key version number — KVNO

Číslo verzie Kerberos long-term key-u používané na zosúladenie ticketu s aktuálnym alebo starším keytab entry. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Keyless signing

Identity-based signing model používajúci OIDC authentication, ephemeral key pair a short-lived signing certificate namiesto manuálne spravovaného long-lived signing keyu. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Keytab

Súbor obsahujúci Kerberos service-principal long-term keys, encryption types a key versions; ide o citlivý service credential. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## `keyword` field

Search field type určený na exact matching, sorting a aggregations bez full-text analysis. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Kill switch

Technický mechanizmus umožňujúci rýchlo zastaviť fault injection, experiment alebo feature exposure pri prekročení bezpečných hraníc. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## KMS grant

Programaticky vytvorený permission objekt umožňujúci grantee principalovi konkrétne cryptographic operations na KMS key, často používaný AWS service integrations. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## KMS key

Logical AWS KMS resource reprezentujúci cryptographic key, jeho metadata, policy, state, aliases a key-material lifecycle. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Known Exploited Vulnerabilities — KEV

CISA katalóg vulnerabilities s evidence o exploitation in the wild, používaný ako silný prioritization signal pre remediation. Pozri [Vulnerability a patch management](docs/13-security-and-identity/vulnerability-and-patch-management.md).

## kube-apiserver

Core control-plane server exponujúci Kubernetes API a koordinujúci authentication, authorization, admission, validation, conversion a persistence. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## kube-controller-manager

Control-plane process spúšťajúci sadu built-in Kubernetes controllers, napríklad Node, Job, namespace a garbage-collection loops. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## kube-proxy

Bežný node component implementujúci časť Kubernetes Service dataplane-u z Service a EndpointSlice state-u; môže byť nahradený alternatívnou implementáciou. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## kube-scheduler

Control-plane component vyberajúci vhodný Node pre Pods, ktoré ešte nemajú assignment; samotné containers nespúšťa. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## Kubeadm

Bootstrap a lifecycle nástroj poskytujúci `init`, `join`, `upgrade`, certificate a configuration workflows pre Kubernetes na už pripravenej infraštruktúre. Pozri [Cluster installation a lifecycle](docs/09-kubernetes/cluster-installation-lifecycle.md).

## kubelet

Primary worker-node agent sledujúci Pods pridelené Node-u a koordinujúci runtime, volumes, probes, status a node resource lifecycle. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## Kubernetes API

Versionované HTTP rozhranie, cez ktoré users, clients, controllers a node components čítajú a menia Kubernetes resources a cluster state. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Kubernetes audit log

Bezpečnostný záznam API requests podľa audit policy, odlišný od diagnostických Events a application business events. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Kubernetes builder driver — Buildx

Buildx driver prevádzkujúci BuildKit workers v Kubernetes, s cluster schedulingom, resource controls a možnosťou native multi-architecture nodes. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Kubernetes cluster

Logická platformová jednotka pozostávajúca z control plane-u, worker nodes, cluster networku, storage a supporting integrations. Pozri [Kubernetes architecture](docs/09-kubernetes/kubernetes-architecture.md).

## Kubernetes controller

Control loop sledujúci resources a vykonávajúci alebo požadujúci zmeny, ktoré približujú observed state k desired state-u. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Kubernetes Event

Krátkodobý API objekt s diagnostickým pozorovaním componentu o konkrétnom resource alebo cluster stave. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Kubernetes executor — GitLab Runner

Executor, ktorý pre CI/CD job vytvorí Kubernetes pod s build, helper a podľa konfigurácie service containers. Pozri [Runners a executors](docs/06-gitlab/runners-and-executors.md).

## Kubernetes incident timeline

Chronologický záznam faktov, hypotéz, testov, zmien a recovery milestones s UTC časom počas incidentu. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Kubernetes object

Persistentná inštancia Kubernetes resource type-u reprezentujúca desired alebo observed cluster state cez API. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Kubernetes resource

API-exposed resource type s group/version, REST endpointom, schema, scope a podporovanými verbs. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Kubernetes SecurityContext

Pod alebo container configuration definujúca runtime user/group identity, capabilities, privilege escalation, filesystem, seccomp a ďalšie security controls. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## Kubernetes version skew

Maximálny podporovaný rozdiel verzií medzi API servers, kubelets, controller-managerom, schedulerom, kube-proxy, kubectl a deployment toolingom. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Kubernetes volume

Pod-level mount alebo device source deklarovaný v `spec.volumes`, ktorého backing môže byť ephemeral, projected alebo persistent. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Kyverno

Kubernetes-native policy engine poskytujúci policy types pre validation, mutation, generation, cleanup a image verification. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## L4 load balancing

Rozdelenie transportných flows podľa IP, portu, protokolu a connection state bez interpretácie aplikačného obsahu. Pozri [Load balancing](docs/02-networking-and-web/load-balancing.md).

## L7 load balancing

Rozdelenie requestov podľa aplikačných údajov, napríklad HTTP hostu, pathu alebo headerov. Pozri [Load balancing](docs/02-networking-and-web/load-balancing.md).

## Label — Kubernetes

Indexovateľné key/value metadata určené na grouping a selection Kubernetes objects. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Lambda alias

Pomenovaný pointer na Lambda version, ktorý môže podporovať weighted routing medzi dvoma versions a slúži ako stabilný deployment target. Pozri [Lambda](docs/11-cloud-and-aws/lambda.md).

## Lambda@Edge

CloudFront-integrated Lambda runtime pre pokročilé viewer alebo origin request/response transformácie distribuované do edge locations podľa service modelu. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Lambda execution environment

Izolované runtime prostredie vytvorené AWS Lambda pre initialization a spracovanie jedného alebo viacerých sequential invocations; jeho reuse nie je durable-state garancia. Pozri [Lambda](docs/11-cloud-and-aws/lambda.md).

## Lambda rotation — Secrets Manager

Rotation model používajúci Lambda function na create, set, test a finish kroky pre secret a target service. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Lambda version

Immutable published snapshot Lambda function code a podporovaných configuration properties používaný ako stabilná release identity. Pozri [Lambda](docs/11-cloud-and-aws/lambda.md).

## Last known good

Presne identifikovaný artifact, configuration a compatibility stav s overenou produkčnou evidence, ktorý možno použiť ako recovery target. Pozri [Rollback a roll-forward](docs/05-ci-cd-and-release/rollback-and-roll-forward.md).

## Latency

Čas potrebný na dokončenie operácie alebo requestu. Pozri [Performance a troubleshooting](docs/01-linux-and-systems/performance-and-troubleshooting.md).

## latency routing — Route 53

DNS routing policy vyberajúca resource v AWS lokalite, ktorá má podľa Route 53 latency measurements najnižšiu očakávanú latency pre query source. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Latest successful artifact — GitLab

Artifact z najnovšieho úspešného pipeline na danom ref-e, ktorý môže GitLab podľa nastavenia uchovávať nezávisle od bežnej expiration policy. Pozri [Artifacts a cache](docs/06-gitlab/artifacts-and-cache.md).

## launch template — EC2

Versionovaný EC2 launch contract definujúci AMI, instance type, network, storage, IAM, metadata, user data a ďalšie launch settings. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## LDAP

Aplikačný protocol na prístup k hierarchickým directory službám cez operations ako Bind, Search, Add, Modify a Delete. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## LDAP control

Rozšírenie LDAP operation behavior, napríklad paged results alebo server-side sorting, označené ako critical alebo non-critical. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## LDAP filter

Výraz určujúci, ktoré directory entries zodpovedajú Search requestu; user input musí byť správne escaped. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## LDAP injection

Injection attack vznikajúci vložením neescaped alebo nevalidovaného inputu do LDAP filteru alebo Distinguished Name. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## LDAP referral

LDAP response odkazujúci clienta na iný directory server alebo naming context. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## LDAPS

LDAP connection chránená TLS od začiatku transportného spojenia, typicky na samostatnom porte. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## LDIF

Textový LDAP Data Interchange Format používaný na reprezentovanie entries a directory changes. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## Leader-elected controller

Controller nasadený vo viacerých instances, ktoré cez Lease koordinujú aktívneho leadera; stále musí tolerovať retries a nie je exactly-once systémom. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Leading indicator — capacity

Signal, ktorý upozorňuje na blížiaci sa failure pred viditeľným user impactom, napríklad queue growth, throttling alebo saturation. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Lease — Kubernetes

Lightweight object v `coordination.k8s.io` používaný napríklad na Node heartbeats alebo leader election components. Pozri [Kubernetes architecture](docs/09-kubernetes/kubernetes-architecture.md).

## Lease — secrets management

Časovo obmedzený contract pre vydaný secret s TTL, renewal a revocation semantics. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Least privilege

Princíp prideľovania iba permissions potrebných na konkrétnu úlohu, v najmenšom scope-e a na najkratší potrebný čas. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## Lens — Well-Architected

Sada questions, best practices a improvement guidance pre konkrétny architecture alebo industry domain. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Level-based reconciliation

Controller model, ktorý pri každom reconcile vyhodnocuje aktuálny desired a observed state namiesto závislosti na jedinom nevynechanom evente. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Library chart — Helm

Chart typu `library`, ktorý poskytuje reusable template primitives a helpers pre iné charts bez bežného application resource lifecycle. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## lifecycle hook — Auto Scaling

Auto Scaling extension, ktorá pozastaví launch alebo termination transition, aby automation vykonala bootstrap, registration, drain alebo evidence-preservation action. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Lifecycle meta-argument — Terraform

Built-in Terraform block meniaci plánovanie resource lifecycle cez pravidlá ako `create_before_destroy`, `prevent_destroy`, `ignore_changes`, `replace_triggered_by`, preconditions a postconditions. Pozri [Lifecycle, import a moved blocks](docs/07-infrastructure-as-code-and-configuration-management/lifecycle-import-moved-blocks.md).

## LimitRange

Namespaced Kubernetes policy nastavujúca alebo validujúca per-container, per-Pod alebo per-PVC resource defaults, minimá, maximá a ratios. Pozri [ResourceQuota a LimitRange](docs/09-kubernetes/resourcequota-limitrange.md).

## LINDDUN

Privacy threat-modeling framework pokrývajúci Linkability, Identifiability, Non-repudiation, Detectability, Disclosure of information, Unawareness a Non-compliance. Pozri [Threat modeling](docs/13-security-and-identity/threat-modeling.md).

## Line coverage

Podiel vykonaných source riadkov počas testov. Vysoká hodnota sama osebe nedokazuje správnosť testov. Pozri [Code coverage a quality gates](docs/04-testing-and-quality/code-coverage-and-quality-gates.md).

## Lineage — Terraform state

Jedinečný identifikátor histórie state-u používaný na rozlíšenie nezávisle vzniknutých states a ochranu pred prepísaním nesúvisiaceho snapshotu. Pozri [Terraform state](docs/07-infrastructure-as-code-and-configuration-management/terraform-state.md).

## List/watch pattern — Kubernetes

API klient najprv získa collection snapshot cez list a následne sleduje zmeny cez watch od príslušného resourceVersion. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## `listen` topic — Ansible

Pomenovaný notification contract, na ktorý môže reagovať viac handlers bez priameho viazania notifying tasku na konkrétne handler names. Pozri [Handlers, loops a conditionals](docs/07-infrastructure-as-code-and-configuration-management/handlers-loops-conditionals.md).

## listener — ELB

Load-balancer frontend contract prijímajúci connections na konkrétnom protocol a porte a vykonávajúci default alebo rule-selected action. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## Listener — Gateway API

Port, protocol, hostname, TLS a allowed-route boundary definovaná na Gateway resourci. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## Listening socket

Socket čakajúci na nové TCP spojenia. Po `accept()` vzniká samostatný connected socket. Pozri [Ports a sockets](docs/02-networking-and-web/ports-and-sockets.md).

## Little's Law

Queueing vzťah `concurrency = throughput × time in system`. Pozri [Performance a troubleshooting](docs/01-linux-and-systems/performance-and-troubleshooting.md).

## Liveness

Schopnosť procesu pokračovať v užitočnej práci bez potreby restartu; nie je automaticky totožná s readiness alebo external availability. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Liveness probe

Kubelet health test rozhodujúci, či je container v stave, z ktorého mu má pomôcť restart; opakované failure vedie k restartu containeru. Pozri [Probes](docs/09-kubernetes/probes.md).

## LLB — BuildKit

Low-Level Build graph representation používaná BuildKitom na opis operations, dependencies, mounts, cache keys a execution flow prekladom z frontendu. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Load average

Priemerný počet runnable tasks a určitých tasks v uninterruptible sleep. Pozri [Memory a CPU fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## `--load` — Buildx

Build exporter skratka importujúca vhodný build output do local Docker image store-u, typicky pre single-platform local workflow. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Load shedding

Riadené odmietanie alebo obmedzenie časti práce pri preťažení, aby systém chránil kritické workflow a zabránil úplnému kolapsu. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Load test

Performance test overujúci očakávaný workload a splnenie latency, throughput, error-rate a resource kritérií. Pozri [Performance, load a stress tests](docs/04-testing-and-quality/performance-load-stress-tests.md).

## LoadBalancer Service

Kubernetes Service type, ktorý prostredníctvom cloud alebo platform controlleru žiada external alebo internal load balancer a publikuje jeho address v status-e. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## Local PersistentVolume

PV reprezentujúci storage fyzicky viazaný na konkrétny Node alebo topology domain, s vysokým výkonom, ale bez automatickej multi-node dostupnosti. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Local TSDB — Prometheus

Lokálny time-series storage Prometheus servera založený na head blocku, WAL, immutable blocks, compaction a retention. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Local value — Terraform

Pomenovaná interná expression modulu dostupná cez `local.<name>`, ktorú caller nemôže priamo nastaviť. Pozri [Variables, locals a outputs](docs/07-infrastructure-as-code-and-configuration-management/variables-locals-outputs.md).

## Local Zone — AWS

AWS infrastructure extension približujúca vybrané služby k určitej metropolitnej oblasti pre latency-sensitive workloady a závislá od parent Regionu podľa service modelu. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## Lockfile — dependency resolution

Versionovaný záznam konkrétneho resolved dependency graphu, často vrátane integrity hashes, ktorý stabilizuje opakovanie dependency resolution. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Log

Časovo označený record udalosti, state-u alebo message, ideálne so stabilnou structured schema a correlation fields. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Log archive account — AWS

Oddelený AWS member account určený na centrálne, dlhodobo chránené uloženie organization-wide audit a security logs. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Log canary

Periodicky generovaný synthetic log event používaný na overenie end-to-end collection, ingestion, storage a query latency. Pozri [Loki](docs/12-observability/loki.md).

## Log loss boundary

Konkrétny stav, pri ktorom telemetry pipeline môže zahodiť logs, napríklad full buffer, volatile crash, permanent output error alebo odstránený file pred dočítaním. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Log replay

Opätovné načítanie a odoslanie log records po reštarte, offset strate alebo backlog recovery, ktoré môže vytvoriť duplicates. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Log stream — Loki

Množina log entries s rovnakým tenant ID a úplným label setom. Pozri [Loki](docs/12-observability/loki.md).

## Logical operation

Jedna business alebo caller-visible operácia bez ohľadu na počet interných retry attempts a fan-out calls. Pozri [RED method](docs/12-observability/red-method.md).

## Logical version

Ľudsky alebo procesne významná verzia, napríklad `2.8.1`, ktorá komunikuje release alebo compatibility význam, ale sama nemusí identifikovať konkrétne bytes bez väzby na digest. Pozri [Artifact versioning](docs/05-ci-cd-and-release/artifact-versioning.md).

## Logically air-gapped vault — AWS Backup

Špeciálny backup vault s dodatočnou logical isolation a Vault Lock compliance ochranou pre ransomware a recovery use cases. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## LogQL

Loki query language kombinujúci stream selectors, line filters, parsing a metric aggregations nad logs. Pozri [Loki](docs/12-observability/loki.md).

## Loki

Label-indexed log aggregation systém ukladajúci log body komprimovane v chunks a používajúci object-storage-oriented storage model. Pozri [Loki](docs/12-observability/loki.md).

## Loki Compactor

Maintenance component, ktorý compactuje index blocks a podľa konfigurácie vykonáva retention a log deletion lifecycle. Pozri [Loki](docs/12-observability/loki.md).

## Loki labels

Bounded metadata tvoriace identity log streamov a indexovaný výberový priestor pre LogQL. Pozri [Loki](docs/12-observability/loki.md).

## Loki retention

Policy a maintenance proces určujúci, ako dlho sa log chunks a index data uchovávajú a kedy sa bezpečne odstránia. Pozri [Loki](docs/12-observability/loki.md).

## Loki ruler

Component vyhodnocujúci LogQL recording alebo alerting rules. Pozri [Loki](docs/12-observability/loki.md).

## Longest-prefix match

Routing pravidlo, podľa ktorého vyhráva zhodná route s najväčším počtom prefix bitov. Pozri [Routing a default gateway](docs/02-networking-and-web/routing-and-default-gateway.md).

## Longest prefix match — AWS routing

Route selection pravidlo, pri ktorom VPC router vyberie matching route s najšpecifickejším destination prefixom. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## Lookaround — regex

Zero-width regex assertion overujúca text pred alebo za aktuálnou pozíciou bez jeho zahrnutia do matchu. Nie je podporovaná vo všetkých engines. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## `lookup` — Helm

Template function čítajúca live Kubernetes API počas server-connected renderu; zavádza RBAC dependency a cluster-state-dependent output. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Loop control — Ansible

Task loop metadata a správanie riadené cez `loop_control`, napríklad pomenovaný `loop_var`, label, index alebo pause. Pozri [Handlers, loops a conditionals](docs/07-infrastructure-as-code-and-configuration-management/handlers-loops-conditionals.md).

## Low-level container runtime

Runtime implementácia, ktorá vytvorí a spustí izolovaný process podľa OCI runtime bundle a spravuje jeho low-level lifecycle, namespaces, mounts a credentials. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Lucene

Search library tvoriaca základ Elasticsearch a OpenSearch shards a segment-based indexing/search modelu. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## MAC address

Link-layer identifikátor interface používaný na Ethernet forwarding v lokálnom broadcast domain. Pozri [Ethernet, MAC a ARP](docs/02-networking-and-web/ethernet-mac-arp.md).

## MAC — Mandatory Access Control

Bezpečnostná politika vynútená systémom nad rámec rozhodnutí ownera objektu. Pozri [SELinux a AppArmor](docs/01-linux-and-systems/selinux-and-apparmor.md).

## Magic variable — Ansible

Reserved variable poskytovaná Ansible engine-om na opis inventory alebo execution contextu, napríklad `hostvars`, `groups` alebo `inventory_hostname`. Pozri [Variables, facts a templates](docs/07-infrastructure-as-code-and-configuration-management/variables-facts-templates.md).

## Main route table — AWS

Predvolená VPC route table, ktorú implicitne používajú subnety bez explicitnej asociácie s custom route table. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## Mainline

Spoločná integračná línia, typicky `main`, reprezentujúca najaktuálnejší dôveryhodný integrovaný stav projektu. Pozri [Continuous Integration](docs/05-ci-cd-and-release/continuous-integration.md).

## Maintenance mode

Kontrolovaný runtime režim používaný počas deploymentu na blokovanie alebo obmedzenie operácií, prípadne na poskytovanie informačnej response používateľom. Pozri [Recreate deployment](docs/05-ci-cd-and-release/recreate-deployment.md).

## Maintenance window

Vopred definovaný časový interval, počas ktorého je povolená plánovaná údržba alebo akceptovaný znížený service level. Pozri [Recreate deployment](docs/05-ci-cd-and-release/recreate-deployment.md).

## MAJOR version

Prvá časť SemVer verzie, ktorá sa zvyšuje pri nekompatibilnej zmene deklarovaného public API alebo compatibility contractu. Pozri [Semantic Versioning](docs/05-ci-cd-and-release/semantic-versioning.md).

## Managed control plane

Kubernetes control plane, ktorého časť lifecycle-u a availability prevádzkuje provider, zatiaľ čo zákazník zostáva zodpovedný za workload, identity, policy, data a značnú časť cluster configuration. Pozri [Kubernetes architecture](docs/09-kubernetes/kubernetes-architecture.md).

## Managed node — Ansible

Host, zariadenie alebo API target, na ktorý Ansible aplikuje automation cez connection plugin alebo provider-specific module workflow. Pozri [Ansible architecture](docs/07-infrastructure-as-code-and-configuration-management/ansible-architecture.md).

## Managed node — Systems Manager

EC2 alebo non-EC2 machine zaregistrovaná v Systems Manager s funkčnou identity, agentom a network connectivity. Pozri [Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## Managed rotation — Secrets Manager

Rotation model, pri ktorom podporovaná managed service integrácia riadi rotation bez zákazníckej Lambda rotation function. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Managed service

Služba, pri ktorej provider preberá definovanú časť deploymentu, patchingu, availability alebo operations, pričom zákazníkovi zostáva configuration, identity, data a business outcome podľa konkrétneho contractu. Pozri [IaaS, PaaS a SaaS](docs/11-cloud-and-aws/iaas-paas-saas.md).

## Management account — AWS Organizations

Najvyšší organization account s billing a Organizations administrative capabilities; SCPs neobmedzujú jeho principals a preto má byť bez bežných workloadov a s minimálnym accessom. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Mapping explosion

Nekontrolovaný rast počtu indexed field definitions spôsobený dynamic schemas alebo arbitrary object keys. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Mapping — search

Schema určujúca field names, types, analyzers a object structure dokumentov v indexe. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Masked variable — GitLab

CI/CD variable, ktorej hodnota spĺňajúca GitLab constraints sa pri výpise do job logu nahrádza maskovaným textom; masking nezabraňuje úmyselnej exfiltration jobom. Pozri [Variables a secrets](docs/06-gitlab/variables-and-secrets.md).

## Matched cohort

Experimentálna alebo kontrolná skupina zostavená tak, aby bola porovnateľná podľa významných vlastností, napríklad tenant size, regiónu, zariadenia alebo workloadu. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Matcher — Alertmanager

Podmienka nad alert labels používaná v route, silence alebo inhibition pravidle. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Matrix pipeline

Pipeline model generujúci viac jobs z kombinácie dimensions ako OS, architecture, runtime version alebo deployment target. Pozri [Reusable a parallel pipelines](docs/05-ci-cd-and-release/reusable-and-parallel-pipelines.md).

## Maximum surge

Limit dočasnej capacity nad desired replica count, ktorú môže rolling update vytvoriť na zachovanie dostupnosti a zrýchlenie rollout-u. Pozri [Rolling update](docs/05-ci-cd-and-release/rolling-update.md).

## Maximum unavailable

Limit počtu alebo percenta desired instances, ktoré môžu byť počas rolling update nedostupné. Pozri [Rolling update](docs/05-ci-cd-and-release/rolling-update.md).

## `maxLimitRequestRatio`

LimitRange pravidlo obmedzujúce maximálny pomer resource limitu k requestu pre konkrétny resource. Pozri [ResourceQuota a LimitRange](docs/09-kubernetes/resourcequota-limitrange.md).

## `maxSkew` — topology spread

Maximálna povolená nerovnomernosť počtu matching Podov medzi topology domains podľa konkrétneho spread constraintu. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Media type — OCI

Identifikátor semantic formátu descriptorom odkazovaného contentu, napríklad image manifest, image index, configuration alebo layer blob. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Member account — AWS Organizations

AWS account patriaci do organization a umiestnený pod root alebo OU, s vlastnými resources a IAM, ale podliehajúci relevantným organization policies. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Memory buffering — Fluent Bit

Dočasné držanie telemetry chunks v RAM; poskytuje nízku latency, ale obmedzenú capacity a slabšiu crash durability. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## `memory.high`

Cgroup v2 memory hranica vyvolávajúca reclaim pressure a throttling. Pozri [cgroups](docs/01-linux-and-systems/cgroups.md).

## Memory limit — Kubernetes

Cgroup memory boundary containeru alebo Podu podľa podporovaného modelu, ktorej prekročenie môže viesť k OOM termination. Pozri [Requests, limits a QoS](docs/09-kubernetes/requests-limits-qos.md).

## Memory limiter — OpenTelemetry

Collector processor chrániaci process pred uncontrolled memory growth a aktivujúci pressure behavior podľa nastavenej memory policy. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## `memory.max`

Cgroup v2 hard memory limit, ktorého prekročenie môže viesť ku cgroup-local OOM. Pozri [cgroups](docs/01-linux-and-systems/cgroups.md).

## Merge base

Najlepší spoločný ancestor dvoch commitov používaný ako base pri three-way merge a pri výpočte divergence. Pozri [Merge a rebase](docs/03-git-and-automation/merge-and-rebase.md).

## Merge commit

Commit s dvoma alebo viacerými parents, ktorý explicitne zaznamenáva integráciu rozdielnych ancestry vetiev. Pozri [Merge a rebase](docs/03-git-and-automation/merge-and-rebase.md).

## Merge queue

Mechanizmus, ktorý testuje a integruje pull requests v plánovanom poradí proti aktuálnemu alebo predpokladanému stavu main branch. Pozri [Branching strategies](docs/03-git-and-automation/branching-strategies.md).

## Merge train — GitLab

Queue model, ktorý overuje viac merge requests v predpokladanom poradí ich integrácie do target branch, aby chránil mainline health pri concurrency. Pozri [Merge requests a approvals](docs/06-gitlab/merge-requests-and-approvals.md).

## Metamonitoring — alerting

Monitoring celého monitoring a notification reťazca vrátane source signalov, rule evaluation, Alertmanagera a externého receivera. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Metric

Agregovateľný číselný signal v čase používaný napríklad na rate, latency distribution, utilization, saturation alebo SLO measurement. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Metric relabeling

Prometheus relabeling fáza po scrape-nutí a pred ingestion, používaná na drop alebo transformáciu metric samples a labels. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Metrics adapter — Kubernetes autoscaling

Component publikujúci custom alebo external metrics cez Kubernetes aggregated API pre HPA alebo ďalších consumers. Pozri [HPA a autoscaling](docs/09-kubernetes/hpa-autoscaling.md).

## Metrics-generator — Tempo

Tempo component, ktorý odvodzuje span metrics, service graphs a ďalšie metrics z ingestovaných traces. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Metrics-server

Cluster add-on implementujúci Resource Metrics API pre aktuálne CPU/memory údaje používané napríklad `kubectl top` a resource-metric HPA; nie je dlhodobý monitoring backend. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Metrics stability — Kubernetes

Alpha, beta alebo stable lifecycle contract system metrics ovplyvňujúci ich deprecation a removal pri Kubernetes upgrades. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Microsegmentation

Jemnozrnná isolation a traffic policy medzi workloadmi alebo resource groups, ktorá obmedzuje lateral movement bez považovania segmentu za automaticky trusted. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## MicroVM

Minimalizovaná virtual machine navrhnutá na rýchlejší startup a menší overhead pri zachovaní samostatnej virtualized-kernel boundary. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Milestone — Well-Architected

Snapshot stavu workload review-u v konkrétnom čase používaný na meranie zmeny risku a improvement progressu. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Minimum detectable effect

Najmenšia zmena outcome metriky, ktorú má experiment pri zvolenej sample size a power spoľahlivo detegovať. Pozri [A/B testing](docs/05-ci-cd-and-release/a-b-testing.md).

## MINOR version

Druhá časť SemVer verzie, ktorá sa zvyšuje pri backward-compatible pridaní capability do deklarovaného public API. Pozri [Semantic Versioning](docs/05-ci-cd-and-release/semantic-versioning.md).

## Mirror Pod

API-visible reprezentácia static Podu, ktorú kubelet vytvorí pre observability; authoritative configuration zostáva na konkrétnom Node-e. Pozri [Pod](docs/09-kubernetes/pod.md).

## Mixed-version control plane

Dočasný podporovaný stav HA control plane počas sekvenčného upgrade-u, keď API server replicas nemajú rovnakú verziu. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Mixed-version deployment

Obdobie rollout-u, počas ktorého stará a nová application verzia súčasne obsluhujú traffic alebo pracujú nad spoločným stavom. Pozri [Rolling update](docs/05-ci-cd-and-release/rolling-update.md).

## Mock provider — Terraform test

Test double poskytujúci deterministické provider schemas a hodnoty pre native Terraform tests bez plného reálneho API behavioru; nenahrádza integration test permissions, quotas a runtime semantics. Pozri [Terraform testing a policy](docs/07-infrastructure-as-code-and-configuration-management/terraform-testing-and-policy.md).

## Mock — test double

Test double s explicitnými očakávaniami na interakcie. Je vhodný, keď komunikácia sama tvorí relevantný kontrakt. Pozri [Mocks, stubs a fakes](docs/04-testing-and-quality/mocks-stubs-fakes.md).

## Module composition — Terraform

Skladanie menších capability modules v root module prepájaním ich explicitných outputs a inputs do jedného dependency graphu. Pozri [Modules](docs/07-infrastructure-as-code-and-configuration-management/modules.md).

## Module contract — Terraform

Stabilné rozhranie reusable modulu tvorené inputs, outputs, provider requirements, behaviorom, lifecycle assumptions, compatibility policy a dokumentovanými side effects. Pozri [Modules](docs/07-infrastructure-as-code-and-configuration-management/modules.md).

## Module instance — Terraform

Konkrétna inštancia child module callu v graph-e, vrátane prípadného `count` indexu alebo `for_each` key v module address-e. Pozri [Modules](docs/07-infrastructure-as-code-and-configuration-management/modules.md).

## Module registry — Terraform

Distribučná služba publikujúca versionované Terraform modules a ich metadata pre verejnú alebo internú spotrebu; sama negarantuje bezpečnosť ani kompatibilitu modulu. Pozri [Modules](docs/07-infrastructure-as-code-and-configuration-management/modules.md).

## Module source — Terraform

Adresa, z ktorej Terraform počas initialization načíta child module, napríklad local path, registry alebo VCS source. Je to executable supply-chain dependency. Pozri [Modules](docs/07-infrastructure-as-code-and-configuration-management/modules.md).

## Module versioning — Terraform

Release a compatibility lifecycle reusable modulu zahŕňajúci version constraints, zmeny input/output contractu, provider requirements, migrations, deprecations a podporované upgrade paths. Pozri [Modules](docs/07-infrastructure-as-code-and-configuration-management/modules.md).

## Monitoring

Systematické sledovanie vopred definovaných signals, states a thresholds s cieľom detegovať známe failure alebo degradation conditions. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Monorepo

Repository obsahujúci viac služieb, knižníc alebo projektov so spoločným object graphom a možnosťou atomických cross-project zmien. Pozri [Monorepo vs. multirepo](docs/03-git-and-automation/monorepo-vs-multirepo.md).

## Mount

Pripojenie filesystemu alebo iného mountable objektu do spoločného filesystem stromu. Pozri [Storage, mounty a filesystems](docs/01-linux-and-systems/storage-mounts-and-filesystems.md).

## Mount namespace

Namespace poskytujúci samostatný pohľad na mount table a propagation. Pozri [Namespaces](docs/01-linux-and-systems/namespaces.md).

## Mount obscuring — container

Runtime efekt, pri ktorom volume alebo bind mount pripojený na path prekryje files existujúce na rovnakom path-e v image filesysteme. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## `moved` block — Terraform

Versionovaná deklarácia `from` a `to` addressy, ktorou Terraform zachová resource alebo module identity počas configuration refaktoringu bez state surgery v každom environment-e. Pozri [Lifecycle, import a moved blocks](docs/07-infrastructure-as-code-and-configuration-management/lifecycle-import-moved-blocks.md).

## Moved history — Terraform

Sada `moved` blocks zachovaná naprieč module releases tak, aby consumers preskakujúci verzie mohli premapovať staré addresses bez neúmyselných replacements. Pozri [Lifecycle, import a moved blocks](docs/07-infrastructure-as-code-and-configuration-management/lifecycle-import-moved-blocks.md).

## MSS — Maximum Segment Size

Maximálny TCP payload segmentu deklarovaný endpointom, typicky odvodený od MTU mínus IP a TCP headers. Pozri [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md).

## mTLS — Mutual TLS

TLS model autentifikujúci server aj klienta pomocou certificates. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## MTU — Maximum Transmission Unit

Maximálna veľkosť L3 packetu preneseného interfaceom bez fragmentácie. Pozri [IPv4, IPv6 a subnetting](docs/02-networking-and-web/ipv4-ipv6-subnetting.md).

## Multi-architecture SBOM

SBOM model, ktorý explicitne rozlišuje OCI image index a jednotlivé platform manifests a ich odlišné component inventories. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## Multi-AZ architecture — AWS

Workload design rozkladajúci compute, networking a stateful capabilities cez viac Availability Zones tak, aby zlyhanie jednej zóny neodstavilo definovanú službu. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## Multi-AZ DB cluster — RDS

RDS deployment model s writer DB instance a dvoma readable instances v troch Availability Zones pri podporovaných engines, určený pre HA a read capacity. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## Multi-AZ DB instance deployment — RDS

RDS high-availability model s primary DB instance a synchronously maintained standby v inej Availability Zone, ktorý pri klasickom modeli neobsluhuje reads. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## Multi-cloud

Používanie services od viacerých cloud providers z obchodných, geografických, regulačných alebo technických dôvodov; samo osebe negarantuje portability ani disaster recovery. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Multi-platform build

Jeden build workflow produkujúci platform-specific manifests a typicky spoločný image index pre viac OS/architecture kombinácií. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Multi-platform image

OCI image index a súvisiaci graph poskytujúci platform-specific manifests pod jednou higher-level reference, napríklad pre `linux/amd64` a `linux/arm64`. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Multi-Region key — KMS

Súvisiace KMS key resources v rôznych Regions zdieľajúce key material a key ID properties, ale s oddelenými policies, grants a lifecycle. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Multi-site active-active — DR

Disaster-recovery stratégia, v ktorej viac geografických lokalít aktívne obsluhuje production traffic a potrebuje cross-site routing, capacity a data consistency model. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Multi-stage build

Dockerfile build s viacerými `FROM` stages, ktorý oddeľuje compilation, test, artifact a runtime filesystemy a umožňuje kopírovať do final image-u iba explicitné artifacts. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## Multi-writer automation

Stav, keď viac automation systémov alebo runs súbežne mení ten istý resource alebo attribute bez spoločnej ownership a concurrency policy. Pozri [Ansible idempotencia](docs/07-infrastructure-as-code-and-configuration-management/ansible-idempotency.md) a [Terraform vs. Ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md).

## Multi-writer race — Terraform

Concurrency stav, keď viac procesov číta rovnaký prior state a pokúša sa zapísať konfliktujúce snapshots alebo remote zmeny bez účinného locku a serialization. Pozri [Remote backend a state locking](docs/07-infrastructure-as-code-and-configuration-management/remote-backend-and-state-locking.md).

## Multiline parser

Parser rekonštruujúci viac fyzických log lines do jedného logical recordu, napríklad stack trace-u. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Multimaster replication — AD DS

Replication model, v ktorom môžu directory changes vzniknúť na viacerých writable domain controllers a následne convergovať cez replication metadata a topology. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## multipart upload — S3

S3 upload protocol rozdeľujúci veľký object na samostatne prenášané parts a dokončený explicitným complete requestom. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Multirepo

Model, v ktorom sú služby alebo projekty rozdelené medzi viac repositories a integrujú sa cez versioned artifacts a explicitné contracts. Pozri [Monorepo vs. multirepo](docs/03-git-and-automation/monorepo-vs-multirepo.md).

## Mutable infrastructure

Model, v ktorom sa existujúce stroje priebežne menia na mieste. Pozri [Immutable vs. Mutable Infrastructure](docs/00-foundations/immutable-vs-mutable-infrastructure.md).

## Mutable tag

Registry alebo repository tag, ktorého mapping možno prepísať na iný artifact content, napríklad `latest`. Nie je spoľahlivou deployment identity bez zachovaného digestu. Pozri [Artifact versioning](docs/05-ci-cd-and-release/artifact-versioning.md).

## Mutating admission

Admission fáza schopná zmeniť alebo doplniť incoming Kubernetes object pred jeho finálnou validáciou a persistence. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## MutatingAdmissionPolicy

Kubernetes in-process declarative policy resource používajúci CEL na riadené mutation API objects počas admission. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Mutation score

Podiel zámerných code mutations, ktoré test suite odhalí zlyhaním. Pozri [Code coverage a quality gates](docs/04-testing-and-quality/code-coverage-and-quality-gates.md).

## Mutation testing

Technika zámerne meniaca produkčný kód a overujúca, či test suite tieto zmeny zachytí. Pozri [Code coverage a quality gates](docs/04-testing-and-quality/code-coverage-and-quality-gates.md).

## Mute interval

Opakovateľné časové pravidlo, počas ktorého sa pre matching route neposielajú notifications, napríklad plánovaná pravidelná maintenance. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Mute time interval — Alertmanager

Opakujúce sa časové pravidlo, ktoré mutuje notifications na matched route počas definovaných intervalov. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Mutual authentication — Kerberos

Kerberos flow, pri ktorom client aj service cryptographically overia druhú stranu pomocou zdieľaného session contextu. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Mutual TLS — mTLS

TLS režim, v ktorom server aj client predkladajú a validujú certificates; poskytuje channel-level mutual authentication, nie automatickú application authorization. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## Named context — Docker build

Dodatočný explicitne pomenovaný build context dostupný Dockerfile-u podobne ako stage, používaný na užšie oddelenie source alebo external image inputs. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Named template — Helm

Globálne pomenovaný reusable template fragment deklarovaný cez `define` a použitý cez `template`, `include` alebo `block`. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Named volume — Docker

Docker volume s explicitným user-defined menom a samostatným lifecycle, vhodné na auditovateľnejší persistence a cleanup workflow. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## NameID — SAML

SAML subject identifier s definovaným formatom, napríklad persistent alebo transient. Pozri [SAML](docs/13-security-and-identity/saml.md).

## Namespace — Linux namespace

Kernel objekt poskytujúci procesu izolovaný pohľad na vybranú kategóriu systémového stavu. Pozri [Namespaces](docs/01-linux-and-systems/namespaces.md).

## Namespace takeover — package

Získanie kontroly nad opusteným, expirovaným alebo nesprávne rezervovaným package namespace-om a jeho použitie na distribúciu attacker-controlled contentu. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Namespaced resource — Kubernetes

Kubernetes resource, ktorého object identity a policy scope zahŕňajú namespace. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Narrow artifact copy — Dockerfile

Princíp kopírovania iba presne potrebných build outputs z build stage do final stage namiesto širokého prenosu celého stage filesystemu. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## NAT — Network Address Translation

Mechanizmus meniaci source alebo destination IP adresy a často ports pri prechode packetu. Pozri [NAT](docs/02-networking-and-web/nat.md).

## NAT port exhaustion — AWS

Stav, pri ktorom NAT path nemá dostatok dostupných source-port mappings pre veľký počet concurrent connections, často koncentrovaných na rovnaký destination tuple. Pozri [Internet Gateway a NAT Gateway](docs/11-cloud-and-aws/internet-gateway-nat-gateway.md).

## NAT64/DNS64

Prechodový model, v ktorom DNS64 syntetizuje IPv6 odpoveď a NAT64 prekladá traffic IPv6-only klienta na IPv4 server. Pozri [NAT](docs/02-networking-and-web/nat.md).

## Native builder

Builder node vykonávajúci build priamo na rovnakej architecture ako target bez user-mode emulation. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Native histogram — Prometheus

Histogram sample reprezentácia s dynamickejším rozlíšením a kompaktnejším prenosom než samostatné classic histogram bucket series, pri kompatibilnej pipeline. Pozri [Prometheus](docs/12-observability/prometheus.md).

## `ndots`

Resolver option určujúca, koľko bodiek musí meno obsahovať, aby sa najprv považovalo za absolute; vysoká hodnota môže znásobiť search-domain DNS queries. Pozri [Cluster DNS](docs/09-kubernetes/cluster-dns.md).

## NDP — Neighbor Discovery Protocol

IPv6 mechanizmus pre neighbor resolution, router discovery a prefix discovery. Pozri [IPv4, IPv6 a subnetting](docs/02-networking-and-web/ipv4-ipv6-subnetting.md).

## Near-real-time search

Search model, v ktorom acknowledged document nemusí byť okamžite viditeľný, kým neprebehne refresh. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Need-to-do

Obmedzenie privilege na actions nevyhnutné pre pracovnú alebo system task. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## Need-to-know

Obmedzenie prístupu k informáciám iba na principals, ktorí ich potrebujú na oprávnenú úlohu. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## `needs` DAG — GitLab

Explicitný directed acyclic graph job dependencies vytvorený cez `needs`, ktorý umožňuje jobs spustiť po skutočných upstream dependencies bez čakania na celé stages. Pozri [GitLab CI/CD syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md).

## Negative DNS caching

Cacheovanie negatívnej DNS odpovede, napríklad `NXDOMAIN`. Pozri [DNS](docs/02-networking-and-web/dns.md).

## Network Access Analyzer — AWS

VPC analysis capability na identifikáciu network paths, ktoré spĺňajú alebo porušujú definované access requirements. Pozri [Security Groups a Network ACLs](docs/11-cloud-and-aws/security-groups-network-acls.md).

## Network account — AWS

Centralizovaný AWS account vlastniaci organization network capabilities ako Transit Gateway, hybrid connectivity, DNS resolvers, inspection alebo IPAM. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Network ACL

Network policy aplikovaná typicky na subnet alebo segment boundary; v cloud prostredí býva často stateless. Pozri [Firewally](docs/02-networking-and-web/firewalls.md).

## Network ACL — AWS

Subnet-level stateless ordered allow/deny packet filter, pri ktorom prvé matching rule number určuje výsledok a request aj return path potrebujú explicitné pravidlá. Pozri [Security Groups a Network ACLs](docs/11-cloud-and-aws/security-groups-network-acls.md).

## Network driver — Docker

Implementácia Docker network connectivity modelu, napríklad bridge, host, none, overlay, macvlan alebo ipvlan. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Network Load Balancer — NLB

Layer 4 Elastic Load Balancing variant pre TCP, TLS, UDP a vysoký connection throughput so zonálnymi IP capabilities podľa configuration. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## Network namespace

Namespace s vlastnými interfaces, addresses, routes, sockets a firewall state. Pozri [Namespaces](docs/01-linux-and-systems/namespaces.md).

## NetworkPolicy

Namespaced Kubernetes API object deklarujúci povolený L3/L4 ingress a egress traffic pre Pods vybrané label selectorom; vyžaduje podporujúci dataplane. Pozri [CNI a NetworkPolicy](docs/09-kubernetes/cni-networkpolicy.md).

## `nindent` — Helm

Template function pridávajúca newline a následne odsadzujúca každý riadok o zadaný počet spaces, vhodná pre vkladanie YAML blocks. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## No-data policy

Explicitné pravidlo určujúce, ako alerting engine interpretuje neprítomnosť očakávaných dát. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## `no_log` — Ansible

Task alebo block control obmedzujúci zobrazenie citlivých arguments a results v bežnom Ansible outpute; nechráni všetky external logs, memory ani výsledný target state. Pozri [Vault](docs/07-infrastructure-as-code-and-configuration-management/vault.md).

## `no_new_privs`

Kernel flag zabraňujúci zvýšeniu privilege cez `execve()`. Pozri [Linux capabilities](docs/01-linux-and-systems/linux-capabilities.md).

## Node affinity

Scheduling pravidlo vyberajúce alebo preferujúce Nodes podľa label expressions, hard alebo soft podľa použitého field-u. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Node allocatable

Časť Node capacity dostupná pre scheduling Pods po odpočítaní resources rezervovaných pre operating system a Kubernetes components podľa configuration. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## Node autoscaling

Automatické pridávanie alebo odoberanie Node capacity podľa schedulovateľnosti a cluster demand modelu. Pozri [HPA a autoscaling](docs/09-kubernetes/hpa-autoscaling.md).

## Node bootstrap dependency

Cyklická alebo kritická závislosť, pri ktorej Node potrebuje systémový DaemonSet agent na plnú funkčnosť, zatiaľ čo agent sám potrebuje funkčný scheduling, runtime alebo časť node infraštruktúry. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## Node condition

Štruktúrovaný status signál Node-u, napríklad Ready, MemoryPressure, DiskPressure alebo PIDPressure. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## Node label — placement

Key/value metadata na Node objekte používaná schedulerom pri nodeSelector, affinity a topology rozhodnutiach. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Node Lease

Lease v namespace `kube-node-lease` používaný ako lightweight heartbeat konkrétneho Kubernetes Node-u. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## Node-local agent

Workload poskytujúci funkciu konkrétnemu Node-u, napríklad logging, monitoring, networking, storage alebo device integration, typicky nasadený cez DaemonSet. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## Node log agent

DaemonSet alebo host agent čítajúci Node/container logs, dopĺňajúci Kubernetes metadata a odosielajúci dáta do central backendu. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Node OOM

Host-level out-of-memory stav Node-u, pri ktorom kernel vyberá proces na ukončenie v širšom system context-e; je odlišný od container cgroup limit OOM. Pozri [Requests, limits a QoS](docs/09-kubernetes/requests-limits-qos.md).

## NodeLocal DNSCache

Voliteľná node-local DNS caching vrstva, typicky nasadená ako DaemonSet, ktorá znižuje latency a pressure na central cluster DNS za cenu ďalšej per-node failure a cache vrstvy. Pozri [Cluster DNS](docs/09-kubernetes/cluster-dns.md).

## NodePort

Service type publikujúci port na eligible Node addresses a smerujúci traffic cez Service dataplane na backend endpoints. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## `nodeSelector`

Jednoduchý hard Pod placement constraint vyžadujúci, aby Node mal všetky uvedené label key/value páry. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## `NoExecute` taint

Node taint effect blokujúci nové Pody bez matching toleration a schopný evictnuť už bežiace netolerujúce Pody. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Nominated Node

Dočasný Pod status signal používaný schedulerom najmä pri preemption workflowe, ktorý označuje očakávaný kandidátny Node, ale nie je finálnym bindingom. Pozri [Scheduling](docs/09-kubernetes/scheduling.md).

## Non-repudiation

Schopnosť poskytnúť dôkaz o pôvode alebo vykonaní operácie tak, aby ju zodpovedná entita nemohla vierohodne poprieť. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Non-terminating error — PowerShell

PowerShell error record, pri ktorom command môže pokračovať; na zachytenie cez `catch` sa často používa `-ErrorAction Stop`. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## Nonce — cryptography

Hodnota, ktorá musí byť v danom cryptographic scheme použitá podľa presných uniqueness alebo randomness požiadaviek; jej reuse môže pri niektorých AEAD modes katastroficky narušiť confidentiality a integrity. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## Nonce — OIDC

Jednorazová hodnota viažuca ID Token na konkrétny authentication request a pomáhajúca proti replay a injection. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md).

## Nondeterministic template — Helm

Template používajúci live lookup, čas, random generation alebo iný mutable input, takže rovnaký chart a values nemusia vytvoriť rovnaký manifest. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Normalized route

Stabilný route pattern, napríklad `/orders/{id}`, používaný namiesto raw URL na zachovanie bounded metric a trace cardinality. Pozri [RED method](docs/12-observability/red-method.md).

## North-south traffic

Traffic medzi interným workloadom a externým klientom, internetom alebo službou mimo platformovej boundary. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## `NoSchedule` taint

Node taint effect zabraňujúci scheduleru umiestniť nový Pod bez matching toleration na daný Node. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Notification — Alertmanager

Receiver-specific správa vytvorená z jednej alert group podľa routing, timing, muting a template pravidiel. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Notification template — Alertmanager

Go template používaný na renderovanie notification title, body, links a receiver-specific payloadu. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## NUL-delimited stream

Textovo-binárny stream používajúci NUL byte ako oddeľovač, vhodný napríklad pre bezpečný prenos filesystem paths obsahujúcich whitespace alebo newline. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md).

## Number misscheduled — DaemonSet

Počet DaemonSet Podov bežiacich na Nodes, ktoré podľa aktuálneho DaemonSet placement modelu už nie sú eligible. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## NVD

National Vulnerability Database; enrichment source pre CVE records, scoring a product mappings, ktorý nie je authoritative inventory konkrétneho environmentu ani jediný prioritization source. Pozri [Vulnerability a patch management](docs/13-security-and-identity/vulnerability-and-patch-management.md).

## OAuth 2.0

Authorization framework na delegovaný alebo workload access k protected APIs pomocou obmedzených tokens. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Object class — LDAP

Schema definícia typu LDAP entry určujúca required a allowed attributes a inheritance. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## Object-count quota — Kubernetes

ResourceQuota limit počtu API objektov konkrétneho typu, napríklad Pods, Jobs, Secrets, PVCs alebo LoadBalancer Services. Pozri [ResourceQuota a LimitRange](docs/09-kubernetes/resourcequota-limitrange.md).

## Object-first troubleshooting

Diagnostický prístup začínajúci exact Kubernetes objectom, jeho spec/status, conditions, ownerReferences, Events a controller state-om. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Object ID — Git

Hash-based identifikátor Git objectu odvodený z typu a obsahu objektu. Pozri [Git object model](docs/03-git-and-automation/git-object-model.md).

## Object pipeline — PowerShell

Pipeline prenášajúca .NET objekty s properties a methods namiesto iba formátovaných textových riadkov. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## Object UID — Kubernetes

Server-generated immutable identity konkrétnej object inštancie; znovu vytvorený object s rovnakým menom dostane nové UID. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Observability

Schopnosť porozumieť internému stavu systému z jeho externých outputs a skúmať aj neočakávané otázky pomocou kvalitnej, korelovateľnej telemetry. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Observability gap

Chýbajúci alebo nekvalitný signal, context, correlation, retention alebo query capability, ktorý bráni spoľahlivej diagnostike systému. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Observability maturity

Úroveň schopnosti organizácie štandardizovať instrumentation, correlation, alerting, SLO, telemetry governance a incident investigation. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Observed generation — Kubernetes

Status hodnota signalizujúca, ktorú verziu object desired state-u controller alebo agent už spracoval. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Observed state — Kubernetes

Stav, ktorý controller alebo agent aktuálne vidí cez API cache, runtime alebo external systém a používa ho pri reconciliation. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## OCI artifact

Non-container alebo auxiliary content distribuovaný cez OCI manifest a registry semantics, napríklad signature, SBOM alebo provenance. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## OCI chart

Helm chart artifact distribuovaný cez OCI-compatible registry s version/digest identity a registry authentication modelom. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## OCI — Open Container Initiative

Otvorená governance organizácia definujúca industry standards pre container image format, runtime bundle/lifecycle a registry distribution. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## OCI referrer

Artifact alebo discovery vzťah odkazujúci na subject digest, používaný napríklad na pripojenie signature, SBOM alebo provenance k image-u. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md) a [Registries](docs/08-container-fundamentals-and-docker/registries.md).

## OCI Referrers

OCI distribution model na discovery manifests, ktoré cez `subject` odkazujú na artifact digest, napríklad signatures, SBOMs alebo provenance. Pozri [SBOM](docs/13-security-and-identity/sbom.md) a [Image signing](docs/13-security-and-identity/image-signing.md).

## OCI runtime bundle

Directory forma pre low-level runtime obsahujúca `rootfs` a `config.json` s process, mount, namespace, capability a resource configuration. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## OCI runtime — Docker

Low-level runtime implementujúci OCI Runtime Specification a vytvárajúci container process, namespaces, mounts a security/resource controls z runtime bundle-u. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## OCSP — Online Certificate Status Protocol

Protokol na zisťovanie revocation statusu certificate; server môže status poskytovať cez OCSP stapling. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## OIDC discovery

Štandardizované získanie OpenID Provider metadata vrátane issuer, endpoints a JWKS URI. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md).

## One-shot service — Compose

Service určená na jednorazové úspešné dokončenie úlohy, napríklad migration, ktorú môže dependency vyžadovať cez `service_completed_successfully`. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Online schema change

Databázová schema operácia navrhnutá tak, aby minimalizovala blocking a downtime počas aktívnej prevádzky; jej skutočné správanie závisí od engine, verzie a dátového objemu. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## OOM killer

Kernel mechanizmus poslednej možnosti ukončujúci proces pri memory exhaustion. Pozri [Memory a CPU fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## OOMKilled — Docker

Container state signal indikujúci, že process bol ukončený v súvislosti s out-of-memory mechanizmom; root cause treba potvrdiť cgroup a kernel evidence. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Opaque token

Access token bez self-contained claims, ktorého stav a metadata resource server zisťuje typicky cez introspection. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Open Policy Agent — OPA

General-purpose policy engine vyhodnocujúci Rego policies nad structured inputom a supporting data. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Open workload model

Model, v ktorom requests prichádzajú podľa arrival rate nezávisle od aktuálnej response time systému. Pozri [Performance, load a stress tests](docs/04-testing-and-quality/performance-load-stress-tests.md).

## OpenID Connect

Federated authentication a identity layer nad OAuth 2.0 používajúca ID Tokens a štandardné claims. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md).

## OpenID Provider

OIDC authorization server, ktorý autentizuje End-Usera a vydáva ID Tokens. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md).

## OpenSearch

Distribuovaný search a analytics systém založený na Apache Lucene s vlastným plugin, security a lifecycle ekosystémom. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## OpenSSF Scorecard

Automatizovaný nástroj hodnotiaci vybrané open-source project security heuristics; jeho score je triage signal, nie security certifikácia. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## OpenTelemetry

Vendor-neutral observability framework a specification pre instrumentation, generation, collection a export traces, metrics a logs. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## OpenTelemetry API

Vendor-neutral programming contract používaný application a libraries na vytváranie telemetry bez vynútenia konkrétneho backendu alebo SDK konfigurácie. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## OpenTelemetry SDK

Runtime implementácia OpenTelemetry API, ktorá zabezpečuje sampling, processing, aggregation, resource configuration a export telemetry. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Operational acceptance testing

Overenie, že systém je prevádzkovateľný: má monitoring, recovery, backup/restore, capacity, runbooks, access controls a deployment/rollback mechanizmy. Pozri [End-to-end a acceptance tests](docs/04-testing-and-quality/end-to-end-and-acceptance-tests.md).

## Operational Excellence pillar

Well-Architected pillar zameraný na efektívny development, operations insight, safe change a continuous improvement. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## option group — RDS

Engine-specific RDS configuration object povoľujúci vybrané database features alebo integrations s vlastným lifecycle, restart a licensing modelom. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## Option injection

Situácia, keď hodnota začínajúca `-` je príkazom interpretovaná ako option namiesto dátového argumentu. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md).

## `OrderedReady` — StatefulSet

Defaultný usporiadaný StatefulSet Pod management model, ktorý vytvára alebo aktualizuje ordinaly postupne a čaká na readiness pred pokračovaním. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Organization root — AWS

Najvyšší kontajner AWS Organizations hierarchy, pod ktorým sa nachádzajú OUs a member accounts a z ktorého sa dedia podporované organization policies. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Organization trail — CloudTrail

Trail vytvorený pre AWS Organization, ktorý centralizuje event coverage member accounts do chráneného audit destination modelu. Pozri [CloudWatch a CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## Organizational Unit — OU

AD DS container používaný na organizáciu objects, administrative delegation a aplikáciu Group Policy; nie je plnou security isolation boundary. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Origin Access Control — OAC

CloudFront mechanismus na SigV4-signed private access k podporovanému S3 originu bez verejného bucketu. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## origin group — CloudFront

CloudFront primary/secondary origin pair s definovanými failover status codes pre podporovaný origin-failover workflow. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## origin request policy — CloudFront

Policy určujúca headers, cookies a query strings posielané CloudFront originu bez ich automatického zahrnutia do cache key. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Origin Shield — CloudFront

Voliteľná regionálna caching vrstva pred originom, ktorá konsoliduje cache misses z viacerých edge locations a znižuje duplicate origin fetches. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Orphan container — Compose

Container patriaci Compose projektu, ktorého service už nie je prítomná v aktuálnom resolved modeli. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Orphan volume — Docker

Volume, ktoré už nemá aktívneho workload ownera alebo referenciu, ale stále obsahuje dáta a spotrebúva storage; pred odstránením potrebuje ownership a retention overenie. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## Orphaned Pod — Kubernetes

Pod bez controller owner reference, ktorý môže zostať po orphan deletion alebo strate ownershipu a môže byť adoptovaný matching controllerom. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## OSI model

Sedemvrstvový konceptuálny model sieťovej komunikácie. Pozri [OSI a TCP/IP model](docs/02-networking-and-web/osi-and-tcp-ip-model.md).

## OTel API

Programovací contract používaný application a instrumentation libraries bez vynútenia konkrétneho backendu alebo runtime konfigurácie. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## OTel SDK

Runtime implementácia OpenTelemetry API zabezpečujúca sampling, aggregation, processing, resource configuration a export. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## OTLP

OpenTelemetry Protocol používaný na prenos telemetry medzi SDKs, Collectors a podporovanými backends. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Outdated deployment — GitLab

Deployment zo staršieho pipeline, ktorý sa pokúša prepísať environment po tom, čo už bol nasadený novší pipeline alebo artifact. Pozri [Environments, deployments a releases](docs/06-gitlab/environments-deployments-releases.md).

## Output plugin — Fluent Bit

Plugin odosielajúci routed telemetry records do konkrétneho backendu alebo destination. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Output value — Terraform

Explicitne publikovaná hodnota modulu tvoriaca jeho výstupný contract pre callerov, CLI alebo ďalšiu automatizáciu. Pozri [Variables, locals a outputs](docs/07-infrastructure-as-code-and-configuration-management/variables-locals-outputs.md).

## Over-specification — testing

Test anti-pattern, pri ktorom assertions overujú nepodstatné interné poradie alebo implementačné detaily a blokujú bezpečný refactoring. Pozri [Mocks, stubs a fakes](docs/04-testing-and-quality/mocks-stubs-fakes.md).

## Overlapping selectors — Kubernetes

Nebezpečný stav, keď viac controllerov zodpovedá rovnakým Pod labelom a môže sa pokúšať adoptovať alebo riadiť tú istú population. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Overlay network — Kubernetes

Pod network model zapuzdrujúci cross-node Pod traffic do tunnel packetov, čím znižuje potrebu upstream route knowledge za cenu encapsulation a MTU overheadu. Pozri [CNI a NetworkPolicy](docs/09-kubernetes/cni-networkpolicy.md).

## OwnerReference — Kubernetes

Metadata väzba dependent objectu na owner object pomocou owner UID, používaná controllers a garbage collectorom. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Ownership matrix

Dokumentované priradenie authoritative writera ku každému resource alebo mutable attribute naprieč provisioning, configuration a runtime systémami. Pozri [Terraform vs. Ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md).

## Ownership matrix — Kubernetes platform

Explicitné rozdelenie zodpovednosti medzi provider, platform team a application team pre control plane, Nodes, add-ons, identity, backup, upgrade a incident response. Pozri [Cluster installation a lifecycle](docs/09-kubernetes/cluster-installation-lifecycle.md).

## PaaS

Platform as a Service: cloud model poskytujúci managed runtime alebo data/application platformu, kde provider spravuje viac infraštruktúrnych a operačných vrstiev než pri IaaS. Pozri [IaaS, PaaS a SaaS](docs/11-cloud-and-aws/iaas-paas-saas.md).

## PAC — Kerberos

Microsoft Privilege Attribute Certificate prenášajúci authorization-related identity a group information v Kerberos ticketoch pre Windows authorization scenarios. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Package manager

Nástroj na inštaláciu, upgrade a odstránenie balíkov vrátane dependencies a lokálnej evidencie. Pozri [Package management](docs/01-linux-and-systems/package-management.md).

## Packfile

Kompaktný Git storage formát ukladajúci viac objektov s možnou delta kompresiou, bez zmeny logického snapshot modelu. Pozri [Git object model](docs/03-git-and-automation/git-object-model.md).

## Page cache

RAM používaná kernelom na cache file-backed dát. Pozri [Memory a CPU fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## Page fault

Udalosť, pri ktorej požadované virtuálne mapovanie nie je okamžite dostupné. Pozri [Memory a CPU fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## Pairwise subject

OIDC subject identifier odlišný medzi sectors alebo clients na zníženie cross-application correlation. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md).

## PAM — Pluggable Authentication Modules

Framework na skladanie authentication, account, session a password policy. Pozri [Users, groups, permissions, sudo a PAM](docs/01-linux-and-systems/users-groups-permissions-sudo-pam.md).

## Panel inspector

Grafana nástroj na zobrazenie raw data, query requests, statistics, transformations a panel JSON pri diagnostike. Pozri [Grafana](docs/12-observability/grafana.md).

## Parallel Pod management — StatefulSet

StatefulSet policy umožňujúca vytváranie alebo odstraňovanie Podov bez čakania na ordered readiness predchádzajúceho ordinalu. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Parameter Store

Systems Manager configuration store pre hierarchické String, StringList a KMS-protected SecureString parameters. Pozri [Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## ParentRef — Gateway API

Reference z Route na Gateway, listener alebo iný supported parent, ku ktorému sa Route pokúša pripojiť. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## Parquet trace block

Columnar Tempo storage block obsahujúci traces a attributes v Apache Parquet formáte pre efektívnejšie selective querying. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Partial batch response — Lambda

Event-source-mapping contract umožňujúci označiť iba konkrétne records v batchi ako neúspešné, aby sa nemuselo retryovať celé spracované batch. Pozri [Lambda](docs/11-cloud-and-aws/lambda.md).

## Partial clone

Clone režim, ktorý odloží prenos vybraných objects a načíta ich podľa potreby, napríklad s `--filter=blob:none`. Pozri [Clone, fetch, pull a push](docs/03-git-and-automation/clone-fetch-pull-push.md).

## Partial evaluation — policy

Predvýpočet policy nad známymi data s vytvorením residual query pre runtime input, používaný na optimalizáciu alebo embedded enforcement. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Partial failure — controller

Stav, keď controller dokončí iba časť distribuovanej operácie, napríklad vytvorí external resource, ale nestihne uložiť jeho identity do statusu, a musí sa bezpečne zotaviť pri retry. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Pass-the-ticket

Attack, pri ktorom útočník použije ukradnutý Kerberos TGT alebo service ticket bez znalosti pôvodného passwordu. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Password-client script — Ansible Vault

Executable helper poskytujúci vault password z chráneného zdroja, typicky po autentifikácii job identity voči secret manageru. Pozri [Vault](docs/07-infrastructure-as-code-and-configuration-management/vault.md).

## PAT — Port Address Translation

NAT model, v ktorom viac interných flows zdieľa jednu externú adresu a rozlišuje sa preloženými portmi. Pozri [NAT](docs/02-networking-and-web/nat.md).

## Patch Manager

Systems Manager capability pre patch scan, installation, baselines, policies a compliance reporting na managed nodes. Pozri [Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## Patch ring

Postupná deployment cohort pre update, napríklad laboratory, canary, non-production a production waves, ktorá obmedzuje blast radius a poskytuje evidence pred širším rolloutom. Pozri [Vulnerability a patch management](docs/13-security-and-identity/vulnerability-and-patch-management.md).

## Patch SLA

Risk-based časový záväzok pre remediation definovaný podľa exploitation, exposure, asset criticality a ďalších context signals, nie iba podľa scanner severity. Pozri [Vulnerability a patch management](docs/13-security-and-identity/vulnerability-and-patch-management.md).

## PATCH version

Tretia časť SemVer verzie, ktorá sa zvyšuje pri backward-compatible oprave deklarovaného behavioru. Pozri [Semantic Versioning](docs/05-ci-cd-and-release/semantic-versioning.md).

## Path traversal

Zraniteľnosť, pri ktorej vstup s prvkami ako `..` alebo absolútnou cestou unikne z povoleného adresára. Pozri [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## PathType — Ingress

Ingress field určujúci semantics HTTP path matching-u ako `Exact`, `Prefix` alebo `ImplementationSpecific`. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## PDC Emulator

Per-domain FSMO role významná pre time hierarchy, password-change preference, lockout a compatibility scenáre. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Pending alert

Alert instance, ktorej condition je aktívna, ale ešte nesplnila požadované `for` alebo ekvivalentné time semantics. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Pending rollback — Helm

Release status signalizujúci nedokončenú rollback operáciu, typicky prebiehajúcu alebo prerušenú pri hooku, API requeste, wait-e alebo release storage update. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Pending upgrade — Helm

Release status signalizujúci nedokončenú upgrade operáciu; pred recovery vyžaduje kontrolu hooks, Jobs, client concurrency, live resources a release evidence. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Per-node overhead — DaemonSet

CPU, memory, storage, network a operational cost jedného DaemonSet Podu vynásobený počtom eligible Nodes v clustri. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## Per-replica PVC — StatefulSet

PersistentVolumeClaim viazaný na konkrétny StatefulSet ordinal a znovu použitý náhradným Podom s rovnakou logical identity. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Performance Efficiency pillar

Well-Architected pillar zameraný na efektívny výber a používanie compute resources podľa workload requirements a technologického vývoja. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Performance test

Test časových a kapacitných vlastností systému pri explicitnom workload modeli, prostredí a success criteria. Pozri [Performance, load a stress tests](docs/04-testing-and-quality/performance-load-stress-tests.md).

## Permissions boundary

Guardrail určujúci maximálny permissions envelope identity bez samostatného udelenia accessu. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## Permissions boundary — IAM

IAM policy nastavujúca maximálny permissions envelope, ktorý identity-based policies môžu udeliť konkrétnemu userovi alebo role. Sama permissions neudeľuje. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## Permissive mode

SELinux režim, v ktorom sa policy denials auditujú, ale nevynucujú. Pozri [SELinux a AppArmor](docs/01-linux-and-systems/selinux-and-apparmor.md).

## Perpetual drift

Opakovaný konflikt, pri ktorom viac actorov striedavo prepisuje ten istý stav podľa rozdielnych desired-state deklarácií. Pozri [Ansible idempotencia](docs/07-infrastructure-as-code-and-configuration-management/ansible-idempotency.md).

## Persistent queue — telemetry

Queue uchovávajúca telemetry state na persistentnom médiu, aby prežila process restart podľa contractu konkrétneho komponentu. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## PersistentVolume

Cluster-scoped Kubernetes object reprezentujúci konkrétny persistent storage resource a jeho capacity, access, topology, reclaim a CSI metadata. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## PersistentVolumeClaim

Namespaced Kubernetes request na persistent storage definujúci požadovanú capacity, access mode, volume mode a StorageClass. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Pester

PowerShell test framework pre assertions, mocks, setup/teardown a test discovery. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## PID limit — container

Cgroup process-count limit chrániaci host pred fork bomb alebo nekontrolovaným rastom procesov a threadov v workload-e. Pozri [Namespaces, cgroups a capabilities](docs/08-container-fundamentals-and-docker/namespaces-cgroups-capabilities.md).

## PID namespace

Namespace poskytujúci samostatné process ID číslovanie a process tree. Pozri [Namespaces](docs/01-linux-and-systems/namespaces.md).

## PID — Process Identifier

Číselný identifikátor procesu v konkrétnom PID namespace. Pozri [Procesy, thready, PID a signals](docs/01-linux-and-systems/processes-threads-pid-signals.md).

## PIDs controller

Cgroup controller obmedzujúci počet procesov alebo threadov cez `pids.max`. Pozri [cgroups](docs/01-linux-and-systems/cgroups.md).

## Pilot light — DR

Recovery stratégia udržiavajúca v náhradnej lokalite kritický data/core základ, ktorý sa pri incidente rozšíri na plnú application capacity. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## `pipefail`

Shell option, ktorá spôsobí, že pipeline vráti nenulový status pri zlyhaní ktoréhokoľvek člena, nie iba posledného príkazu. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md).

## Pipeline as Code

Správa delivery workflowu ako versionovaného, reviewovateľného, testovateľného a policy-validovaného zdrojového kódu. Pozri [Pipeline as Code](docs/05-ci-cd-and-release/pipeline-as-code.md).

## Pipeline cache

Dočasné znovupoužiteľné dáta určené na zrýchlenie pipeline, napríklad dependencies alebo compiler outputs. Cache nie je release artifact ani source of truth. Pozri [Continuous Integration](docs/05-ci-cd-and-release/continuous-integration.md).

## Pipeline — CI/CD

Runtime inštancia versionovaného delivery workflowu vytvorená konkrétnym triggerom a viazaná na commit, event context, variables, jobs, artifacts a results. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## Pipeline last argument — Helm

Pravidlo, podľa ktorého pipeline odovzdá svoj ľavý výsledok ako posledný positional argument nasledujúcej template funkcie. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Pipeline processor — telemetry

Komponent medzi receiverom a exporterom, ktorý môže vykonávať batching, filtering, redaction, enrichment, sampling alebo routing. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Pipeline — shell

Reťaz procesov, v ktorej stdout jedného procesu smeruje do stdin ďalšieho. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md).

## PKCE

Proof Key for Code Exchange, ktorý viaže authorization-code exchange na client instance cez code challenge a verifier. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## PKI — Public Key Infrastructure

Systém certificate authorities, policies, trust stores, issuance, validation, rotation a revocation pre public-key identities. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## Placement deadlock

Stav, keď kombinácia hard affinity, anti-affinity, taints, topology, storage alebo resource constraints nevytvára žiadny feasible Node. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## placement group — EC2

EC2 placement constraint optimalizujúci cluster latency/throughput, spread failure isolation alebo partitioned distributed-system topology. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Plaintext

Nešifrované dáta dostupné application alebo používateľovi pred encryption alebo po decryption. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## Plan artifact — Terraform

Uložený Terraform plan viazaný na configuration, variables, provider/module selections a prior state, ktorý má byť reviewovaný, policy-evaluovaný a následne aplikovaný ako ten istý immutable decision artifact. Pozri [Terraform testing a policy](docs/07-infrastructure-as-code-and-configuration-management/terraform-testing-and-policy.md).

## Plan test — Terraform

Native Terraform test run používajúci `command = plan` na overenie plan-time contractu bez vytvorenia reálnej infraštruktúry. Pozri [Terraform testing a policy](docs/07-infrastructure-as-code-and-configuration-management/terraform-testing-and-policy.md).

## Platform mismatch — container image

Nesúlad medzi target OS/architecture a vybraným image manifestom alebo executable, ktorý môže viesť k pull failure alebo `exec format error`. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Pod

Najmenší deployable Kubernetes compute object predstavujúci jeden alebo viac co-scheduled containers so spoločnou Pod network identity, lifecycle boundary a volumes. Pozri [Pod](docs/09-kubernetes/pod.md).

## Pod adoption — Kubernetes

Proces, pri ktorom controller prevezme matching Pod bez controller owner reference a nastaví ho ako svoj dependent object. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Pod affinity

Scheduling pravidlo priťahujúce Pod do topology domain, kde už existujú matching Pody. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Pod anti-affinity

Scheduling pravidlo oddeľujúce Pod od topology domains obsahujúcich matching Pody, hard alebo soft podľa konfigurácie. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Pod condition

Štruktúrovaný Pod status signal, napríklad Scheduled, Initialized, ContainersReady alebo Ready, ktorý je odlišný od high-level Pod phase. Pozri [Pod](docs/09-kubernetes/pod.md).

## Pod phase

High-level summary lifecycle state-u Podu: Pending, Running, Succeeded, Failed alebo Unknown; reasons ako CrashLoopBackOff nie sú samostatné phases. Pozri [Pod](docs/09-kubernetes/pod.md).

## Pod readiness gate

Custom condition zahrnutá do Pod readiness rozhodnutia, ktorú musí nastavovať zodpovedný external alebo platform controller. Pozri [Pod](docs/09-kubernetes/pod.md).

## Pod sandbox

Runtime prostredie Podu vytvorené cez CRI, ktoré drží najmä shared network namespace a infra lifecycle pre Pod containers. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md) a [Pod](docs/09-kubernetes/pod.md).

## Pod Security Admission — PSA

Built-in Kubernetes admission controller vyhodnocujúci Pods podľa versionovaných Pod Security Standards a namespace režimov enforce, audit a warn. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## Pod Security Standards — PSS

Versionované Kubernetes security profily Privileged, Baseline a Restricted definujúce povolené Pod security fields a privilege model. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## Pod selector — workload controller

Label selector určujúci population Podov, ktorú workload controller pozoruje a riadi; tvorí zásadnú ownership a reconciliation boundary. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Pod template

Embedded desired Pod metadata a spec v workload controller resource-e, z ktorého controller vytvára nové Pod instances. Pozri [Pod](docs/09-kubernetes/pod.md).

## Point-in-time recovery — AWS Backup

Obnova podporovaného resource-u do konkrétneho času z continuous backup recovery pointu. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## point-in-time recovery — RDS

Obnova novej RDS database do vybraného času v automated-backup recovery windowe pomocou snapshots a retained transaction logs. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## Policy Administration Point — PAP

Komponent alebo proces, ktorý vytvára, mení a publikuje authorization policies. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Policy Administration Point — Policy as Code

Governance a delivery funkcia spravujúca policy authoring, approval, publication, rollout, rollback, exceptions a retirement. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy Administrator — Zero Trust

NIST Zero Trust logical component, ktorý na základe Policy Engine decisionu vytvára, konfiguruje alebo ukončuje communication path cez PEP. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Policy artifact

Immutable distribuovateľný package policy modules, data, manifestu, revision a integrity metadata. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy as Code

Prístup vyjadrujúci automatizovateľné policy decisions ako versionované, testovateľné a auditovateľné machine-readable rules. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy bundle

Versionovaný package policy a supporting data určený na atomickú distribúciu a activation v policy engine. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy bypass

Access alebo operation vykonaná mimo zamýšľaného enforcement pointu, cez exception, fail-open stav alebo alternatívny path. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy canary

Staged rollout novej policy revision na obmedzenú množinu namespaces, tenants, workloads alebo requests pred širším enforcementom. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy composition

Mechanizmus kombinovania výsledkov viacerých policies podľa explicitných semantics, napríklad deny-overrides alebo all-must-pass. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy conflict

Stav, keď dve alebo viac policies vytvárajú nezlučiteľné decisions, invariants alebo mutations pre rovnaký scope. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy coverage

Miera, do akej sú relevantné resources, actions, environments a enforcement points skutočne chránené konkrétnymi policies; odlišná od test code coverage. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy data

Supporting reference state používaný policy decisionom, napríklad approved registries, identity groups alebo resource classifications. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy Decision Point — PDP

Komponent vyhodnocujúci authorization request voči policies a contextu a vracajúci allow alebo deny decision. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Policy Decision Point — Policy as Code

Komponent vyhodnocujúci policy nad inputom a supporting data a vracajúci structured decision. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy distribution skew

Dočasný stav, keď distributed PDP alebo PEP instances používajú rozdielne policy revisions pre asynchronous rollout alebo activation failure. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy enforcement point — network

Miesto v packet path-e, kde CNI alebo iný dataplane vyhodnocuje a aplikuje network policy; jeho poloha voči NAT, Service translation a host trafficu ovplyvňuje pozorované addresses a semantics. Pozri [CNI a NetworkPolicy](docs/09-kubernetes/cni-networkpolicy.md).

## Policy Enforcement Point — PEP

Komponent pri resource boundary, ktorý presadzuje authorization decision a povolí alebo zablokuje operation. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Policy Enforcement Point — Policy as Code

Komponent zachytávajúci chránenú operation a presadzujúci policy decision voči callerovi alebo resource-u. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy Engine — Zero Trust

NIST Zero Trust logical component vyhodnocujúci enterprise policy a contextual data pre access ku konkrétnemu resource-u. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Policy exception

Explicitný, scoped, approved a expirovateľný object povoľujúci dokumentovanú odchýlku od konkrétnej policy s compensating controls. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy exception — Terraform

Časovo obmedzený a auditovaný override konkrétnej policy s ownerom, dôvodom, compensating controls, approvalom, expiration a remediation plánom. Pozri [Terraform testing a policy](docs/07-infrastructure-as-code-and-configuration-management/terraform-testing-and-policy.md).

## Policy Information Point — PIP

Zdroj trusted attributes a contextu potrebných na authorization decision. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Policy Information Point — Policy as Code

Zdroj identity, device, asset, vulnerability alebo ďalších contextual attributes poskytovaných policy decisionu. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy input

Request-specific structured document obsahujúci operation, resource a context vyhodnocovaný policy engine-om. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy intent

Ľudsky formulovaný security, compliance alebo operational cieľ, ktorý sa pri Policy as Code formalizuje do executable decision contractu. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy lifecycle

Proces definície intentu, formalizácie, review, testovania, staged rollout-u, monitoring-u, exception managementu a retirementu policy. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy obligation

Dodatočná povinnosť v decision result-e, ktorú PEP musí vykonať spolu s accessom, napríklad masking, step-up alebo audit event. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy peer — NetworkPolicy

Source alebo destination množina vyjadrená cez Pod selector, namespace selector, ich kombináciu alebo `ipBlock`. Pozri [CNI a NetworkPolicy](docs/09-kubernetes/cni-networkpolicy.md).

## Policy Report — Kyverno

Kubernetes custom resource obsahujúci current evaluation results matching resources pre Kyverno policies; nejde o kompletný historical admission log. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy revision

Immutable alebo jednoznačne versionovaná identita konkrétneho policy setu použitá pri decisione, rolloute a audite. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy routing

Routing model, ktorý môže vyberať table podľa source address, marku, ingress interface alebo ďalších selectors. Pozri [Routing a default gateway](docs/02-networking-and-web/routing-and-default-gateway.md).

## Policy unit test

Automatizovaný positive, negative alebo boundary scenario overujúci expected policy decision pre konkrétny input a data. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy version pinning — Pod Security

Explicitné naviazanie Pod Security Admission režimu na konkrétnu Kubernetes minor policy verziu, aby cluster upgrade nezmenil enforcement bez testovaného rollout-u. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## Policy WebAssembly

Skompilovaná policy vykonávaná ako WebAssembly module v embedded PEP alebo application runtime. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Port

16-bit transportný identifikátor socket endpointu. Port sám neurčuje aplikačný protokol. Pozri [Ports a sockets](docs/02-networking-and-web/ports-and-sockets.md).

## Port publishing

Host-side forwarding alebo proxy konfigurácia, ktorá sprístupní container port cez zvolený host bind address a port. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Position database — Fluent Bit

Persistentný state Tail inputu uchovávajúci file identity a read offset na restart a rotation recovery. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Post-import plan — Terraform

Prvý fresh plan po vytvorení import bindingu, používaný na rozhodnutie, či configuration remote stav adoptuje, zmení alebo by nebezpečne vyvolala update či replacement. Pozri [Lifecycle, import a moved blocks](docs/07-infrastructure-as-code-and-configuration-management/lifecycle-import-moved-blocks.md).

## Post-promotion watch

Observation obdobie po dosiahnutí plnej expozície, ktoré sleduje oneskorené, kumulatívne alebo segmentovo zriedkavé failures pred uzavretím release rozhodnutia. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## PowerShell provider

Abstraction layer sprístupňujúca datasources ako filesystem, registry, certificates alebo environment cez jednotné cmdlets a drives. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## Pre-authentication — Kerberos

Mechanizmus, ktorým client pred vydaním TGT preukazuje kontrolu nad long-term credentialom alebo iným initial authentication factorom. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Pre-release identifier

SemVer časť za pomlčkou, napríklad `rc.1`, označujúca verziu s nižšou precedence než zodpovedajúci final release. Pozri [Semantic Versioning](docs/05-ci-cd-and-release/semantic-versioning.md).

## Predictive scaling

Elasticity model pripravujúci capacity pred očakávaným demand-om na základe historických vzorov alebo forecastu. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Preemption — Kubernetes scheduling

Mechanizmus, pri ktorom scheduler môže iniciovať odstránenie nižšie prioritných Podov, aby vytvoril priestor pre unschedulable Pod s vyššou prioritou. Pozri [Scheduling](docs/09-kubernetes/scheduling.md).

## `PreferNoSchedule` taint

Soft Node taint effect, ktorému sa scheduler pokúsi vyhnúť, ale pri nedostatku vhodných možností môže Pod na Node umiestniť. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Prefix list — AWS VPC

Spravovaný zoznam CIDR prefixes použiteľný v route tables alebo Security Group rules na zníženie duplicity a centralizáciu network identity. Pozri [Security Groups a Network ACLs](docs/11-cloud-and-aws/security-groups-network-acls.md).

## `prevent_destroy` — Terraform

Lifecycle rule blokujúca plánované zničenie resource, pokiaľ je pravidlo stále prítomné v configuration; nenahrádza remote deletion protection ani backup. Pozri [Lifecycle, import a moved blocks](docs/07-infrastructure-as-code-and-configuration-management/lifecycle-import-moved-blocks.md).

## Preventive control

Control znižujúci pravdepodobnosť vzniku bezpečnostného incidentu. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Primary component — SBOM

Hlavný product, application alebo artifact, ktorého composition daná SBOM opisuje. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## Primary shard

Autoritatívna shard kópia subsetu documents, z ktorej sa koordinuje replication. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Principal

Security identity používaná pri authentication alebo authorization, napríklad user, workload, service alebo device. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## PriorityClass

Cluster-scoped Kubernetes resource definujúci numerickú Pod priority a preemption policy semantics. Pozri [Scheduling](docs/09-kubernetes/scheduling.md).

## Private cloud

Cloud-like platforma vyhradená jednej organizácii s API, self-service, automation, policy, metering a pooled-capacity operating modelom. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Private NAT Gateway — AWS

NAT Gateway bez Elastic IP určený na private network address translation cez podporované private routing targets, nie na priamy internet egress cez IGW. Pozri [Internet Gateway a NAT Gateway](docs/11-cloud-and-aws/internet-gateway-nat-gateway.md).

## Private subnet — AWS

Subnet bez priameho inbound internet pathu, ktorý môže používať NAT, VPC endpoints, proxy alebo hybrid connectivity pre outbound alebo private access. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## Privilege creep

Postupné hromadenie nepotrebných alebo zastaraných permissions počas zmien role, projektov a manuálnych grants. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## Privileged container

Container spustený s výrazne rozšírenými capabilities, device accessom a oslabenými security profiles, čím sa zásadne zmenšuje jeho isolation od hosta. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Privileged container — Kubernetes

Container spustený s veľmi širokým host kernel, device a security-control prístupom; podľa mounts a namespaces môže byť prakticky host-root-equivalentný. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## Privileged namespace exception

Auditovaná namespace výnimka povoľujúca systémovým workloadom širšie Pod privileges, s obmedzeným RBAC, ownerom, scope-om a expiry. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## Probe-level termination grace

`terminationGracePeriodSeconds` nastavené na startup alebo liveness probe pre špecifický grace period pri probe-triggered container termination. Pozri [Probes](docs/09-kubernetes/probes.md).

## Probe threshold

`failureThreshold` alebo `successThreshold` určujúci počet po sebe idúcich výsledkov potrebných na zmenu probe state-u alebo failure action. Pozri [Probes](docs/09-kubernetes/probes.md).

## Probe timeout

Maximum času jedného probe pokusu určené `timeoutSeconds`; príliš krátka hodnota môže pri load-e alebo CPU throttlingu vytvárať false failures. Pozri [Probes](docs/09-kubernetes/probes.md).

## Process

Bežiaca inštancia programu s adresným priestorom, file descriptormi, credentials a ďalším kernel stavom. Pozri [Procesy, thready, PID a signals](docs/01-linux-and-systems/processes-threads-pid-signals.md).

## Production-derived test data

Testovacie dáta odvodené z produkcie, ktoré vyžadujú data minimization, anonymizáciu, access control a retention policy. Pozri [Flaky tests a test data](docs/04-testing-and-quality/flaky-tests-and-test-data.md).

## Production validation

Overenie technického, funkčného a business výsledku zmeny v skutočnom produkčnom kontexte po deploymente alebo počas kontrolovaného rollout-u. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Profile — observability

Telemetry signal zobrazujúci, kde application trávi CPU time, alokuje memory alebo čaká, používaný na performance diagnostiku. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Profile — performance profile

Vzorka alebo agregácia stackov ukazujúca, kde proces trávi CPU čas, čaká alebo alokuje memory. Pozri [Performance a troubleshooting](docs/01-linux-and-systems/performance-and-troubleshooting.md).

## Progress deadline — Deployment

Časová hranica, po ktorej Deployment status označí rollout ako nepostupujúci; sama osebe nevykoná automatický rollback. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## Progressive delivery

Evidence-driven riadenie postupnej produkčnej exposure pomocou rollout stratégie, segmentácie, observability, promotion policy a recovery mechanizmov. Pozri [Progressive delivery](docs/05-ci-cd-and-release/progressive-delivery.md).

## Project name — Compose

Stabilná identity Compose projektu ovplyvňujúca názvy a scope containers, networks, volumes a lifecycle commandov. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Projected configuration update

Kubelet-driven aktualizácia ConfigMap alebo Secret volume projection s eventual sync semantics; application musí podporovať reload a `subPath` mount zvyčajne aktualizáciu nedostane. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Projected ServiceAccount token

ServiceAccount token vložený do projected volume s explicitnou audience, expiration a kubelet rotation semantics. Pozri [ServiceAccount](docs/09-kubernetes/serviceaccount.md).

## Prometheus

Metrics monitoring a alerting systém založený na multidimenzionálnych time series, pull-based scrapingu, local TSDB a PromQL. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Prometheus HA

Model viacerých nezávislých Prometheus replicas, ktoré samostatne scrape-ujú, ukladajú a vyhodnocujú rules; downstream vrstva musí riešiť deduplication. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Promoted trace attribute

Span attribute vybraný na indexovanie, metrics generation alebo ďalšie zrýchlené query spracovanie, čím získava samostatný cardinality a cost dopad. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Promotion evidence

Súbor výsledkov a metadata viazaných na konkrétny artifact digest, ktoré odôvodňujú jeho postup do ďalšieho environmentu. Pozri [Environment a promotion](docs/05-ci-cd-and-release/environment-and-promotion.md).

## PromQL

Prometheus Query Language na selection, aggregation a výpočty nad time series. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Protected branch — GitLab

Branch s policy obmedzujúcou push, merge, force push, deletion a podľa konfigurácie Code Owner alebo approval behavior. Pozri [Protected branches a environments](docs/06-gitlab/protected-branches-and-environments.md).

## Protected environment

Environment s obmedzenou deployment identitou, approval alebo policy pravidlami a auditom, používaný najmä pre produkciu a citlivé stages. Pozri [Continuous Delivery](docs/05-ci-cd-and-release/continuous-delivery.md).

## Protected environment — GitLab

GitLab environment s obmedzeným allowed-to-deploy alebo approval modelom pre citlivé runtime targety, napríklad production. Pozri [Protected branches a environments](docs/06-gitlab/protected-branches-and-environments.md).

## Protected variable — GitLab

CI/CD variable sprístupnená iba pipeline contextom na protected refs podľa GitLab trust pravidiel; stále vyžaduje bezpečný runner a pipeline kód. Pozri [Protected branches a environments](docs/06-gitlab/protected-branches-and-environments.md).

## Provenance attestation

Signed statement viažuci artifact na builder, source revision, build type a inputs podľa definovaného provenance predicate-u. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Provider alias — Terraform

Pomenovanie alternatívnej konfigurácie rovnakého providera používané napríklad pre inú region, account alebo endpoint boundary. Pozri [Terraform providers, resources a data sources](docs/07-infrastructure-as-code-and-configuration-management/terraform-providers-resources-data-sources.md).

## Provider configuration — Terraform

Runtime nastavenie providera, napríklad region, endpoint alebo authentication context, ktoré resource alebo module používa na API operácie. Pozri [Terraform providers, resources a data sources](docs/07-infrastructure-as-code-and-configuration-management/terraform-providers-resources-data-sources.md).

## Provider interpretation drift

Plan rozdiel spôsobený zmenou provider schema, defaults, diff suppression alebo read normalizácie namiesto manuálnej zmeny samotného remote objektu. Pozri [Drift](docs/07-infrastructure-as-code-and-configuration-management/drift.md).

## Provider lock-in

Technická, dátová, operačná alebo komerčná závislosť od konkrétneho providera, ktorá zvyšuje náklady alebo čas migrácie. Pozri [IaaS, PaaS a SaaS](docs/11-cloud-and-aws/iaas-paas-saas.md).

## Provider-managed layer

Vrstva služby, ktorej infrastructure, patching, control plane alebo application lifecycle prevádzkuje provider podľa service contractu. Pozri [IaaS, PaaS a SaaS](docs/11-cloud-and-aws/iaas-paas-saas.md).

## Provider requirement — Terraform

Deklarácia provider source addressu a povoleného version rozsahu v `required_providers`, ktorú modul potrebuje pre svoje resources a data sources. Pozri [Terraform providers, resources a data sources](docs/07-infrastructure-as-code-and-configuration-management/terraform-providers-resources-data-sources.md).

## Provider responsibility — cloud

Časť service contractu vlastnená cloud providerom, typicky physical facilities, hardware, host platform, virtualization a managed-service runtime podľa služby. Pozri [Shared responsibility model](docs/11-cloud-and-aws/shared-responsibility-model.md).

## Provider state

Deterministicky pripravený stav providera potrebný na overenie konkrétnej consumer-driven contract interaction. Pozri [Contract a API tests](docs/04-testing-and-quality/contract-and-api-tests.md).

## Provisioned concurrency — Lambda

Počet predinicializovaných Lambda execution environments pripravených na invocations pre konkrétnu version alebo alias s cieľom znížiť startup latency. Pozri [Lambda](docs/11-cloud-and-aws/lambda.md).

## Provisioning

Vytváranie a lifecycle správa infraštruktúrnych resources, napríklad networks, compute, databases, load balancers a IAM objektov. Pozri [Terraform vs. Ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md).

## Provisioning/configuration boundary

Explicitná hranica určujúca, ktoré resources a attributes vlastní provisioning engine a ktoré configuration-management engine. Pozri [Terraform vs. Ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md).

## Proxy

Sprostredkovateľ ukončujúci jednu komunikáciu a vytvárajúci samostatnú komunikáciu k ďalšiemu endpointu. Pozri [Proxy a reverse proxy](docs/02-networking-and-web/proxy-and-reverse-proxy.md).

## PSI — Pressure Stall Information

Metriky času, počas ktorého tasks čakali pre nedostupnosť CPU, memory alebo I/O kapacity. Pozri [Memory a CPU fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## PSS — Proportional Set Size

Odhad memory procesu, pri ktorom sa zdieľané pages pomerne rozdelia medzi procesy. Pozri [Memory a CPU fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## PSScriptAnalyzer

Static analysis nástroj pre PowerShell scripts a modules, ktorý kontroluje conventions, compatibility a vybrané security patterns. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## Public API — versioning

Deklarovaná compatibility boundary zahŕňajúca nielen programové interfaces, ale podľa produktu aj konfiguráciu, CLI, schemas, events, file formats a operational behavior. Pozri [Semantic Versioning](docs/05-ci-cd-and-release/semantic-versioning.md).

## Public cloud

Provider-operated multi-tenant cloud platforma poskytujúca on-demand services cez logicky izolované accounts a networks; neznamená automaticky public-internet exposure workloadu. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Public NAT Gateway — AWS

Zonálny managed NAT service vytvorený v public subnet-e s Elastic IP, používaný typicky pre outbound IPv4 connectivity private subnetov. Pozri [Internet Gateway a NAT Gateway](docs/11-cloud-and-aws/internet-gateway-nat-gateway.md).

## Public subject

OIDC subject identifier spoločný pre clients v príslušnom issuer scope-e. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md).

## Public subnet — AWS

Subnet s route pathom na Internet Gateway; konkrétny resource potrebuje ešte public addressing a security/application konfiguráciu, aby bol internet reachable. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## Pull-through cache — registry

Lokálny registry cache model, ktorý pri prvom pull-e načíta content z upstream registry a ďalším clients ho poskytuje lokálne podľa cache a freshness policy. Pozri [Registries](docs/08-container-fundamentals-and-docker/registries.md).

## `--push` — Buildx

Build exporter skratka publikujúca image alebo multi-platform index priamo do registry. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Pushgateway

Prometheus ecosystem component na dočasné vystavenie service-level metrics short-lived batch jobov, ktoré nemôžu byť prirodzene scrape-nuté počas behu. Pozri [Prometheus](docs/12-observability/prometheus.md).

## PVC retention policy — StatefulSet

Policy určujúca, či sa StatefulSet-created PVCs zachovajú alebo odstránia pri scale-down alebo deletion podľa podporovaného API a storage lifecycle modelu. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Quality gate

Automatizovaný alebo kombinovaný rozhodovací bod, ktorý vyhodnotí versionovanú policy nad konkrétnou evidence a povolí, zablokuje alebo eskaluje ďalší krok delivery. Pozri [Quality gates a approvals](docs/05-ci-cd-and-release/quality-gates-and-approvals.md).

## Quarantine OU — AWS

Organizational unit s prísnymi incident alebo decommission guardrails určená na izoláciu member accountu pri zachovaní potrebného response a evidence accessu. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Quarantine — testing

Dočasné vyradenie nestabilného testu z blocking suite pri zachovaní pravidelného spúšťania, ownera, issue a expiry. Pozri [Flaky tests a test data](docs/04-testing-and-quality/flaky-tests-and-test-data.md).

## Querier — Loki

Component vykonávajúci LogQL subqueries nad recent ingestion state-om a historical object-storage dátami. Pozri [Loki](docs/12-observability/loki.md).

## Query frontend — Loki

Read-path component, ktorý prijíma LogQL queries, splituje ich, aplikuje caching/limits a zlučuje výsledky. Pozri [Loki](docs/12-observability/loki.md).

## Query frontend — Tempo

Read-path component, ktorý sharduje trace lookup alebo TraceQL search na jobs, distribuuje ich queriers a zlučuje výsledky. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Query scheduler — Loki

Component koordinujúci a frontujúci query work medzi query frontendmi a queriers. Pozri [Loki](docs/12-observability/loki.md).

## Query storm — Grafana

Nadmerný počet alebo objem backend queries spôsobený kombináciou panels, variables, repeats, users a krátkeho refresh intervalu. Pozri [Grafana](docs/12-observability/grafana.md).

## QUIC

Transportný protokol nad UDP implementujúci reliable streams, congestion control, loss recovery a TLS 1.3 integráciu. Pozri [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md).

## Quota admission

API admission kontrola odmietajúca create alebo update request, ktorý by prekročil ResourceQuota hard limit alebo nesplnil required quota fields. Pozri [ResourceQuota a LimitRange](docs/09-kubernetes/resourcequota-limitrange.md).

## Quota saturation

Stav, keď ResourceQuota `used` dosiahne alebo sa približuje k `hard`, takže nové Pody, Jobs, PVCs alebo iné objects nemôžu byť prijaté. Pozri [ResourceQuota a LimitRange](docs/09-kubernetes/resourcequota-limitrange.md).

## Range vector — PromQL

Množina time series so samples za definované časové okno, používaná napríklad ako vstup `rate()` alebo `increase()`. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Ratcheting — quality

Model, ktorý povoľuje iba zachovanie alebo zlepšenie predchádzajúceho akceptovaného quality baseline. Pozri [Code coverage a quality gates](docs/04-testing-and-quality/code-coverage-and-quality-gates.md).

## RBAC privilege escalation

Nepriame získanie širšej kontroly cez permissions ako workload creation, Secret read, exec/proxy, RBAC `bind`/`escalate`, impersonation alebo CSR approval. Pozri [RBAC](docs/09-kubernetes/rbac.md).

## RBAC subject

User, Group alebo ServiceAccount identita, ktorej RoleBinding alebo ClusterRoleBinding udeľuje permissions. Pozri [RBAC](docs/09-kubernetes/rbac.md).

## RDS endpoint

DNS name poskytujúci stable logical connection identity pre RDS database, ktorého resolved address sa môže zmeniť pri failover-e alebo maintenance. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## RDS failover

Riadený alebo automatický presun writer/primary database role na standby alebo reader target pri Multi-AZ failure alebo maintenance udalosti. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## RDS Proxy

Managed database proxy a connection-pooling vrstva pre podporované RDS/Aurora engines, ktorá znižuje connection churn a pomáha pri burst a failover scenarios. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## Re-encryption

Proces decryption dát a ich opätovnej encryption novým DEKom, algoritmom alebo cryptographic contextom; mení samotný ciphertext a je náročnejší než rewrap. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## Reachability Analyzer — AWS

VPC configuration-analysis tool modelujúci network path medzi source a destination a identifikujúci blocking component. Pozri [Security Groups a Network ACLs](docs/11-cloud-and-aws/security-groups-network-acls.md).

## Reactive scaling

Elasticity model, ktorý mení capacity po zistení aktuálneho metric alebo demand signalu, napríklad CPU, request rate alebo queue depth. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Read compatibility

Schopnosť starej aj novej application verzie správne interpretovať dáta v aktuálnom schema a semantic stave. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Read-only root filesystem — container

Runtime policy zakazujúca zápis do image-derived root filesystemu a povoľujúca iba explicitne pripojené writable paths. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Read-only root filesystem — Kubernetes

Container security setting zakazujúci zápis do image root filesystemu a vyžadujúci explicitné writable mounts pre temp, cache alebo application state. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## read replica — RDS

Asynchronously replicated readable database copy používaná na read scaling, reporting, migration alebo promotion-based recovery. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## Readiness

Stav, v ktorom má workload prijímať traffic alebo prácu; process môže byť live, ale ešte nemusí byť ready. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Readiness boundary

Podmienka dokazujúca, že novovytvorený resource je nielen prítomný, ale pripravený na ďalší configuration alebo deployment krok. Pozri [Terraform vs. Ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md).

## Readiness gate

Pod-level custom condition, ktorá musí byť true spolu s container readiness, aby bol Pod považovaný za Ready. Pozri [Probes](docs/09-kubernetes/probes.md).

## Readiness probe

Kubelet test určujúci, či má Pod prijímať nový traffic; failure nereštartuje container, ale mení readiness a backend eligibility. Pozri [Probes](docs/09-kubernetes/probes.md).

## Ready replicas — Kubernetes

Počet replík, ktorých Pody majú aktuálne Ready condition; nevypovedá automaticky o dlhodobej availability alebo business correctness. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Real User Monitoring — RUM

Zber performance a error telemetry zo skutočných používateľských klientov a sessions s možnosťou segmentácie podľa zariadenia, browsera, regiónu alebo journey. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Realized savings

Úspora reálne overená po implementácii optimization change-u, nie iba estimated recommendation. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Rebase

Operácia, ktorá replayuje commits na nový base a vytvára nové commit objects s novými IDs. Pozri [Merge a rebase](docs/03-git-and-automation/merge-and-rebase.md).

## Receiver — Alertmanager

Pomenovaná kolekcia notification integrations, napríklad webhook, email, chat alebo on-call služba. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Receiver — telemetry

Komponent telemetry pipeline, ktorý prijíma signals cez OTLP, scrape, logs alebo iný podporovaný protocol. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Reclaim policy — Kubernetes storage

PV lifecycle pravidlo `Delete` alebo `Retain` určujúce, čo sa má stať s PV a podľa drivera backing storage po uvoľnení claimu; nie je náhradou backup policy. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Reconciliation

Proces porovnania a opravy rozdielov medzi dvoma reprezentáciami alebo stores, napríklad počas dual write migration. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Reconciliation key

Stabilná identity resource-u, typicky `namespace/name`, vložená do controller work queue, podľa ktorej worker načíta najnovší object state. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Reconciliation loop

Opakovaný proces observe, compare, act a report, ktorý približuje actual state Kubernetes alebo external systému k desired state-u. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Recording rule — Prometheus

Pravidelne vyhodnocovaná PromQL expression, ktorej výsledok sa uloží ako nová time series pre opakované alebo drahé výpočty. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Recovery control

Control umožňujúci obnoviť službu, dáta alebo dôveryhodný stav po incidente. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Recovery keys — Vault

Quorum material používaný pri vybraných privileged Vault operations v auto-unseal modeli; nenahrádza stratený auto-unseal key. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Recovery observation

Samostatná fáza resilience experimentu po odstránení faultu, ktorá overuje backlog drain, reconciliation, návrat resources a splnenie recovery deadline. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Recovery package

Predpripravený súbor identity, kompatibility informácií, workflows a rozhodovacích podkladov potrebných na rollback, roll-forward alebo restore konkrétneho release. Pozri [Rollback a roll-forward](docs/05-ci-cd-and-release/rollback-and-roll-forward.md).

## Recovery Point Actual — RPA

Skutočný vek alebo bod obnovených dát dosiahnutý pri recovery teste alebo incidente, porovnávaný s cieľovým RPO. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Recovery-point age

Čas od vytvorenia posledného validného recovery pointu, používaný ako praktický signal voči RPO požiadavke. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Recovery point — AWS Backup

Backup reprezentujúci obsah resource-u v konkrétnom čase spolu s lifecycle, encryption a recovery metadata. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Recovery Point Objective — RPO

Maximálna tolerovaná strata dát vyjadrená časom medzi incidentom a posledným použiteľným recovery pointom. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Recovery Region — AWS

AWS Region pripravený ako cieľ cross-Region disaster recovery vrátane data, capacity, quotas, identity, KMS, networking, artifacts a runbookov. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Recovery set — Kubernetes

Súbor artifacts potrebný na obnovu, zahŕňajúci etcd snapshot, PKI, encryption configuration/keys, component config, infrastructure source a application data backups. Pozri [etcd backup a restore](docs/09-kubernetes/etcd-backup-restore.md).

## Recovery Time Actual — RTA

Skutočný čas od začiatku recovery procesu po obnovenie validovanej business capability, porovnávaný s cieľovým RTO. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Recovery Time Objective — RTO

Cieľový maximálny čas na obnovenie definovanej business capability po incidente vrátane detekcie, rozhodnutia, data recovery, startupu, validácie a traffic cutoveru. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Recreate deployment

Deployment stratégia, ktorá ukončí starú version fleet pred spustením a pripravenosťou novej, čo typicky vytvára downtime alebo výrazný capacity dip. Pozri [Recreate deployment](docs/05-ci-cd-and-release/recreate-deployment.md).

## Recreate strategy — Deployment

Deployment stratégia, ktorá odstráni starú Pod population pred vytvorením novej, čím akceptuje downtime alebo minimalizuje mixed-version overlap. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## RED method

Service-oriented monitoring metodika sledujúca Rate, Errors a Duration pre každú relevantnú operation. Pozri [RED method](docs/12-observability/red-method.md).

## Redirect URI

Pre-registered client endpoint, na ktorý authorization server vracia browser authorization response. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## ReDoS — Regular Expression Denial of Service

Denial-of-service riziko spôsobené regexom s patologickou runtime complexity nad útočníkom kontrolovaným vstupom. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## ReferenceGrant

Gateway API object vytvorený v namespace referencovaného resource-u, ktorý explicitne povoľuje vybraným Routes z iného namespace cross-namespace reference. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## Reflog

Lokálna evidencia pohybov refs a `HEAD`, použiteľná na recovery commitov po reset, rebase alebo zmazaní branch pred expiráciou záznamov. Pozri [Commit, branch, tag a HEAD](docs/03-git-and-automation/commit-branch-tag-head.md).

## Refresh-only plan — Terraform

Plan režim, ktorý ukáže zmeny state-u potrebné na zosúladenie s remote observations bez plánovania remote infraštruktúry k desired configuration. Pozri [Drift](docs/07-infrastructure-as-code-and-configuration-management/drift.md).

## Refresh — search

Operácia sprístupňujúca nové Lucene segments pre search; nie je totožná s durable flushom alebo backupom. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Refresh token

Dlhšie žijúci OAuth credential používaný na získanie nových access tokens bez opakovanej user interaction. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Refresh-token rotation

Model, v ktorom každé použitie refresh tokenu vydá nový token a umožňuje detegovať reuse staršej hodnoty. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Refspec

Pravidlo mapujúce source ref na destination ref pri fetch alebo push operácii. Pozri [Clone, fetch, pull a push](docs/03-git-and-automation/clone-fetch-pull-push.md).

## Regex dialect

Konkrétna syntax a semantics regular expression engine-u, napríklad POSIX ERE, .NET, Python, PCRE alebo RE2. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Regional endpoint — AWS

Service API alebo data endpoint smerujúci request do konkrétneho AWS Regionu; nesprávny Region môže viesť k prázdnemu inventory, iným quotas alebo deploymentu do nesprávnej lokality. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## Regional resource — AWS

Resource s identity a lifecycle scope-om v konkrétnom AWS Regione, napríklad VPC alebo väčšina managed service deployments. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## Registered variable — Ansible

Host-scoped variable vytvorená cez `register`, ktorá uchováva štruktúrovaný result konkrétneho tasku pre ďalšie conditions, loops alebo reporting. Pozri [Variables, facts a templates](docs/07-infrastructure-as-code-and-configuration-management/variables-facts-templates.md).

## Registry mirror

Alternatívny registry endpoint replikujúci alebo cacheujúci content pre dostupnosť, latency, rate-limit alebo air-gap účely. Pozri [Registries](docs/08-container-fundamentals-and-docker/registries.md).

## Rego

Deklaratívny OPA policy jazyk inšpirovaný Datalogom a určený na reasoning nad nested structured data. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Regression test

Test chrániaci existujúce funkčné alebo nefunkčné správanie pred nechcenou zmenou. Pozri [Smoke a regression tests](docs/04-testing-and-quality/smoke-and-regression-tests.md).

## Rekey — Ansible Vault

Zmena passwordu alebo vault identity použitej na šifrovanie existujúceho Vault contentu; nemení automaticky samotný cieľový application credential. Pozri [Vault](docs/07-infrastructure-as-code-and-configuration-management/vault.md).

## Rekor

Sigstore transparency log pre signed software supply-chain metadata a inclusion evidence. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Relative Distinguished Name — RDN

Časť Distinguished Name identifikujúca LDAP entry relatívne voči jeho parent entry. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## RelayState — SAML

Application state prenášaný spolu so SAML protocol message, ktorý potrebuje integrity a open-redirect ochranu. Pozri [SAML](docs/13-security-and-identity/saml.md).

## Release

Produktové alebo procesné rozhodnutie sprístupniť funkcionalitu používateľom. Pozri [Software Development Life Cycle](docs/00-foundations/sdlc.md).

## Release branch

Branch určená na stabilizáciu a podporu konkrétnej release line, často s backportmi a explicitným lifecycle. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Release cadence

Pravidlo určujúce frekvenciu a časovanie releases, napríklad on-demand, fixed schedule, release train alebo continuous release. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Release candidate

Immutable artifact považovaný za potenciálny final release, ktorý musí byť testovaný a promotionovaný bez rebuildu pod rovnakou release identity. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Release evidence — Helm

Súbor dôkazov zahŕňajúci release history, status, values, rendered manifest, hooks, artifact identity a live Kubernetes stav. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Release history retention — Helm

Policy určujúca počet a dobu uchovania Helm revisions s trade-offom medzi rollback targets, forensic evidence, Secret exposure a etcd storage. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Release management

Disciplína riadenia release identity, readiness, approvals, communication, rollout, recovery a support lifecycle od pripraveného artifactu po používateľsky dostupnú zmenu. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Release manifest

Versionovaný dokument mapujúci koordinovaný release na immutable digests komponentov a relevantné configuration, infrastructure a schema revisions. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Release notes

Kurátorovaná komunikácia konkrétneho release pre používateľov, administrátorov, integrátorov alebo support, zahŕňajúca dopad, breaking changes, migráciu a known issues. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Release record

Auditovateľný záznam spájajúci release version, artifacts, source, config, migrations, evidence, approvals, rollout a výsledok. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Release train

Cadence model, v ktorom zmeny pripravené do definovaného cutoffu vstúpia do spoločného release termínu a ostatné čakajú na ďalší vlak. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Release unit

Presne definovaná množina artifactov, configov, migrations alebo koordinovaných komponentov, ktoré sa schvaľujú a release-ujú ako jeden celok. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Reliability pillar

Well-Architected pillar zameraný na správne a konzistentné fungovanie workloadu, capacity, change a failure management. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Relying Party

OIDC client, ktorý dôveruje validovanému ID Token-u od OpenID Providera a vytvára vlastnú application session. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md).

## Remediation hierarchy — Kubernetes

Preferované poradie opráv od úzkeho declarative rollbacku alebo obnovy dependency cez Pod/Node replacement a roll-forward až po disaster recovery. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Remote backend — Terraform

Backend ukladajúci Terraform state mimo lokálneho working directory a podľa typu poskytujúci collaboration, locking, versioning alebo remote-operation capabilities. Pozri [Remote backend a state locking](docs/07-infrastructure-as-code-and-configuration-management/remote-backend-and-state-locking.md).

## Remote builder — Buildx

BuildKit daemon spravovaný mimo lokálneho Docker Engine-u, ku ktorému sa Buildx pripája cez explicitný remote endpoint a trust model. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Remote drift — Terraform

Rozdiel vzniknutý zmenou managed remote objektu mimo authoritative Terraform workflowu. Pozri [Drift](docs/07-infrastructure-as-code-and-configuration-management/drift.md).

## Remote execution — Terraform

Model, v ktorom plan/apply nevykonáva lokálny CLI proces, ale spravovaný remote worker alebo platforma s vlastnou queue, identity, variables a policy vrstvou. Pozri [Remote backend a state locking](docs/07-infrastructure-as-code-and-configuration-management/remote-backend-and-state-locking.md).

## Remote read — Prometheus

Mechanizmus, ktorým Prometheus query engine načíta series z kompatibilného externého storage receivera. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Remote-tracking ref

Lokálny ref pod `refs/remotes/` reprezentujúci stav remote branch pri poslednom fetchi. Nie je to živý pohľad na server. Pozri [Clone, fetch, pull a push](docs/03-git-and-automation/clone-fetch-pull-push.md).

## Remote write — Prometheus

Asynchrónny pipeline odosielajúci ingested samples cez queues, batching a retries do kompatibilného remote-storage receivera. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Rendered manifest — Helm

Výsledný Kubernetes YAML vytvorený kombináciou chart templates, effective values, release contextu a capabilities pred aplikovaním na API server. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Repeat interval

Interval opakovania Alertmanager notification pre nezmenenú group, ktorá zostáva firing. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Repeating panel — Grafana

Panel alebo row dynamicky duplikovaný pre každú vybranú variable value; pri veľkom scope-e môže vytvoriť query storm. Pozri [Grafana](docs/12-observability/grafana.md).

## `replace_triggered_by` — Terraform

Lifecycle rule vyžadujúca replacement resource, keď sa zmení referencovaný managed objekt alebo atribút predstavujúci explicitný lifecycle signal. Pozri [Lifecycle, import a moved blocks](docs/07-infrastructure-as-code-and-configuration-management/lifecycle-import-moved-blocks.md).

## Replacement Pod

Nový Pod object vytvorený controllerom ako náhrada zaniknutého alebo nevyhovujúceho Podu; má nový UID, IP a runtime lifecycle aj pri podobnom mene alebo template. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Replica shard

Kópia primary shardu poskytujúca redundancy a read capacity, ale nie ochranu pred logical corruption alebo deletion. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## ReplicaSet

Kubernetes workload controller udržiavajúci požadovaný počet matching zameniteľných Podov. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## replication lag — RDS

Časový alebo log-position rozdiel medzi source database a asynchronously applying read replica, ktorý určuje stale-read a recovery exposure. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## Report artifact — GitLab

Machine-readable job artifact v podporovanej schéme, ktorý GitLab interpretuje pre test, coverage, code-quality, dotenv, SBOM alebo security výsledky. Pozri [Artifacts a cache](docs/06-gitlab/artifacts-and-cache.md).

## Reproducible build

Build proces, pri ktorom rovnaké explicitné vstupy a toolchain vytvoria rovnaký alebo ekvivalentný výsledný artifact. Pozri [Continuous Integration](docs/05-ci-cd-and-release/continuous-integration.md).

## Request rate

Počet requestov alebo jednotiek práce za čas na presne definovanej measurement boundary. Pozri [RED method](docs/12-observability/red-method.md).

## Required configuration

Runtime configuration field, bez ktorého application nemôže bezpečne začať a má zlyhať s redigovanou validačnou chybou. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## `required` — Helm

Template function zlyhávajúca render, keď požadovaná hodnota je empty, a vracajúca explicitnú error message. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Requirement traceability

Väzba od business potreby a požiadavky cez risk a control až po test a dôkaz výsledku. Pozri [Verification vs. validation](docs/04-testing-and-quality/verification-vs-validation.md).

## `requirements.yml` — Ansible

Dependency manifest používaný na deklarovanie a inštaláciu požadovaných Ansible roles alebo collections a ich version constraints. Pozri [Roles a collections](docs/07-infrastructure-as-code-and-configuration-management/roles-and-collections.md).

## Rerere

Git mechanizmus `reuse recorded resolution`, ktorý zaznamená riešenie konfliktu a môže ho znovu aplikovať pri opakovanom konflikte. Pozri [Konflikty](docs/03-git-and-automation/merge-conflicts.md).

## Rerun-until-green

Anti-pattern opakovania zlyhaného testu dovtedy, kým náhodne neprejde, bez riešenia príčiny alebo zachovania prvého failure signálu. Pozri [Flaky tests a test data](docs/04-testing-and-quality/flaky-tests-and-test-data.md).

## Reserved concurrency — Lambda

Per-function limit, ktorý rezervuje časť regional concurrency poolu a zároveň určuje maximálny počet concurrent invocations danej funkcie. Pozri [Lambda](docs/11-cloud-and-aws/lambda.md).

## Residual risk

Risk zostávajúci po aplikovaní mitigations a controls, ktorý musí mať explicitného ownera, acceptance decision a review trigger. Pozri [Threat modeling](docs/13-security-and-identity/threat-modeling.md).

## Resilience engineering

Disciplína navrhovania a zlepšovania schopnosti sociotechnického systému predvídať, absorbovať, zotaviť sa a učiť sa z porúch a variability. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Resolved alert

Alert instance, ktorej firing condition už neplatí a prešla do ukončeného stavu podľa alerting lifecycle-u. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Resolved Compose model

Výsledná configuration po interpolation, merge, profiles, includes a overrides, ktorú možno kontrolovať cez `docker compose config`. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Resolved configuration — GitLab CI/CD

Konečný pipeline YAML model po spracovaní includes, components, defaults, inheritance, references a rules-relevantnej konfigurácie. Pozri [GitLab CI/CD syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md).

## Resolved notification

Notification informujúca receiver, že predtým firing alert group alebo alert identity už nie je aktívna. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Resolved pipeline configuration

Výsledná pipeline definícia po spracovaní includes, templates, inheritance, parameters, rules a generated configu; predstavuje konfiguráciu, ktorú platforma skutočne vykoná. Pozri [Pipeline as Code](docs/05-ci-cd-and-release/pipeline-as-code.md).

## Resolved runtime configuration — Docker

Skutočná configuration vytvoreného containeru vrátane image, commandu, environmentu, mounts, networks, limits a security options dostupná cez inspection. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## ResolvedRefs condition — Gateway API

Route status condition indikujúca, či controller úspešne vyriešil backend, Secret a ďalšie references vrátane cross-namespace permission. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## Resolver forwarding loop

DNS failure, pri ktorom cluster DNS forwarduje query na Node stub resolver a ten ju pošle späť na cluster DNS, často pre nesprávny kubelet `resolvConf`. Pozri [Cluster DNS](docs/09-kubernetes/cluster-dns.md).

## Resource address — Terraform

Jednoznačná konfiguračná adresa managed objektu vrátane module pathu, resource type/name a prípadného `count` indexu alebo `for_each` key. Pozri [Terraform providers, resources a data sources](docs/07-infrastructure-as-code-and-configuration-management/terraform-providers-resources-data-sources.md).

## Resource-based policy — AWS

Policy uložená pri resource-e, ktorá môže priamo určovať allowed alebo denied principals, actions a conditions, vrátane cross-account accessu. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## Resource binding — Terraform

State mapovanie medzi Terraform resource instance addressou, provider contextom a konkrétnou remote object identity. Pozri [Terraform state](docs/07-infrastructure-as-code-and-configuration-management/terraform-state.md).

## Resource-centric security

Zero Trust prístup chrániaci konkrétne applications, APIs, data a workflows namiesto udeľovania broad trust celému network segmentu. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Resource Detector

Komponent automaticky získavajúci OpenTelemetry resource attributes z environmentu, cloudu, Kubernetes alebo runtime metadata. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Resource enforcement coverage — Zero Trust

Podiel a kvalita access paths ku critical resources, ktoré skutočne prechádzajú identity-aware policy evaluation a neobíditeľným PEP. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Resource group — GitLab CI/CD

Pipeline mechanizmus serializujúci jobs, ktoré mutujú rovnaký environment alebo shared resource, aby sa zabránilo súbežným konfliktujúcim operáciám. Pozri [GitLab CI/CD syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md).

## Resource inventory — USE

Systematický zoznam bounded hardware, software a cloud resources, pre ktoré sa hľadajú utilization, saturation a error signals. Pozri [USE method](docs/12-observability/use-method.md).

## Resource lifecycle engine

Automation model sledujúci identity resources a plánujúci ich create, update, replacement a destroy operácie, typicky cez dependency graph a persistentný state. Pozri [Terraform vs. Ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md).

## Resource limit — Kubernetes

Deklarované runtime maximum alebo enforcement boundary resource-u, napríklad CPU quota alebo memory cgroup limit. Pozri [Requests, limits a QoS](docs/09-kubernetes/requests-limits-qos.md).

## Resource metrics pipeline

Cesta kubelet resource údajov cez metrics-server a `metrics.k8s.io` API ku klientom a HPA. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Resource — OpenTelemetry

Súbor attributes identifikujúcich entitu produkujúcu telemetry, napríklad service, host, cloud resource alebo Kubernetes workload. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Resource overcommitment — Kubernetes

Stav, keď aggregate runtime potential alebo limits presahujú fyzickú kapacitu, zatiaľ čo scheduler placement vychádza z nižších requests; zvyšuje utilization aj pressure risk. Pozri [Requests, limits a QoS](docs/09-kubernetes/requests-limits-qos.md).

## Resource owner

OAuth entita schopná autorizovať access ku protected resource. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Resource request — Kubernetes

Deklarované množstvo resource-u používané schedulerom na placement a platformou ako reservation alebo relative-share signal. Pozri [Requests, limits a QoS](docs/09-kubernetes/requests-limits-qos.md).

## Resource server

API alebo služba validujúca access token a presadzujúca resource-level authorization. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## `resourceNames` — Kubernetes RBAC

RBAC rule field zužujúci vybrané permissions na explicitné object names, s limitmi pre create, list/watch a deletecollection semantics. Pozri [RBAC](docs/09-kubernetes/rbac.md).

## ResourceQuota

Namespaced Kubernetes API objekt obmedzujúci agregované resource requests/limits, storage alebo počet API objektov. Pozri [ResourceQuota a LimitRange](docs/09-kubernetes/resourcequota-limitrange.md).

## ResourceVersion — Kubernetes

Opaque storage version objektu alebo collection snapshotu používaná na optimistic concurrency a list/watch continuity, nie ako business version. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## response headers policy — CloudFront

CloudFront policy pridávajúca alebo upravujúca CORS, security alebo custom response headers nezávisle od origin application code. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Responsibility boundary

Presná hranica určujúca, ktoré vrstvy, controls a recovery činnosti vlastní provider, zákazník alebo obaja. Pozri [IaaS, PaaS a SaaS](docs/11-cloud-and-aws/iaas-paas-saas.md).

## REST

Architectural style pre distributed hypermedia systems založený na constraints ako statelessness, cacheability a uniform interface. Pozri [REST APIs a WebSockets](docs/02-networking-and-web/rest-apis-and-websockets.md).

## Restart loop — container

Opakovaný crash a automatický restart containeru podľa restart policy alebo external controllera, ktorý potrebuje koreláciu exit code, logs, events a dependencies. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Restart storm

Séria koordinovaných alebo opakovaných container restartov vyvolaná chybnou liveness/startup probe alebo spoločnou dependency failure, ktorá môže incident ďalej zhoršiť. Pozri [Probes](docs/09-kubernetes/probes.md).

## Restore rehearsal

Pravidelný test obnovy reálneho backup artifactu v izolovanom prostredí vrátane merania RTO a application consistency validation. Pozri [etcd backup a restore](docs/09-kubernetes/etcd-backup-restore.md).

## Restore testing — AWS Backup

Policy-driven pravidelné obnovenie recovery pointu do test targetu s následnou technical a application validation. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Restored etcd cluster identity

Nové member a cluster metadata vytvorené snapshot restore operáciou; starý a obnovený member state sa nesmie nekontrolovane miešať. Pozri [etcd backup a restore](docs/09-kubernetes/etcd-backup-restore.md).

## Restricted Pod Security Standard

Najprísnejší built-in PSS profil pre bežné workloads, vyžadujúci non-root a obmedzený privilege/capability/seccomp model podľa versionovaného štandardu. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## Retransmission

Opätovné odoslanie transportných dát po detekcii straty alebo nedostatočného potvrdenia. Pozri [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md).

## Retry amplification

Násobenie pôvodného workloadu, keď client, proxy a služby nezávisle retryujú rovnaké zlyhanie a vytvoria viac pokusov na jednu business operáciu. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Retry budget

Explicitný limit množstva alebo času retry pokusov, ktorý zabraňuje nekonečným retries a zosilneniu downstream incidentu. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Retry loop — Ansible

Opakovanie rovnakého tasku podľa `until`, `retries` a `delay`, určené pre bounded transient conditions, nie pre iteráciu business items. Pozri [Handlers, loops a conditionals](docs/07-infrastructure-as-code-and-configuration-management/handlers-loops-conditionals.md).

## Retry queue — Fluent Bit

Queue chunks čakajúcich na opakovaný output flush po retryable failure. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Reusable pipeline

Versionovaný pipeline component alebo workflow s explicitným input, output, permissions a failure contractom určený na použitie vo viacerých projects. Pozri [Reusable a parallel pipelines](docs/05-ci-cd-and-release/reusable-and-parallel-pipelines.md).

## Reverse proxy

Proxy zastupujúci serverové služby voči klientom a vykonávajúci napríklad TLS termination, routing alebo caching. Pozri [Proxy a reverse proxy](docs/02-networking-and-web/proxy-and-reverse-proxy.md).

## Review app — GitLab

Dočasný dynamic environment vytvorený pre branch alebo merge request na overenie zmeny pred merge, s vlastným URL a cleanup lifecycle. Pozri [Protected branches a environments](docs/06-gitlab/protected-branches-and-environments.md).

## Revocation latency — Zero Trust

Čas od identity, posture alebo policy revocation eventu po propagáciu a ukončenie relevantných active sessions vo všetkých enforcement points. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Rewrap

Opätovné zabalenie existujúceho DEKu novým KEKom bez decryption a re-encryption celého application payloadu. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## Rightsizing

Úprava alebo odstránenie resource-u podľa reálneho utilization, performance, reliability a capacity modelu. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Ring deployment

Progressive rollout cez stabilné deployment rings s rastúcou reprezentatívnosťou alebo kritickosťou a samostatnými entry, observation a promotion podmienkami. Pozri [Ring deployment](docs/05-ci-cd-and-release/ring-deployment.md).

## Risk-adaptive access

Access model meniaci allow, deny, step-up, session lifetime alebo povolené actions podľa trusted contextual risk signals. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Risk-based deployment

Rollout policy, ktorá mení exposure, observation window, approval alebo recovery mechanizmus podľa business criticality, blast radiusu a compatibility rizika konkrétnej zmeny. Pozri [Continuous Deployment](docs/05-ci-cd-and-release/continuous-deployment.md).

## Role-Based Access Control — RBAC

Authorization model, ktorý združuje permissions do roles a tieto roles priraďuje principals v konkrétnom scope-e. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Role contract — Ansible

Verejné a prevádzkové rozhranie role tvorené inputs, defaults, outputs/facts, handlers, side effects, supported platforms, privileges, idempotency a upgrade behaviorom. Pozri [Roles a collections](docs/07-infrastructure-as-code-and-configuration-management/roles-and-collections.md).

## Role defaults — Ansible

Ľahko override-nuteľné public defaults uložené typicky v `defaults/main.yml`, ktoré tvoria podporované customization points role. Pozri [Roles a collections](docs/07-infrastructure-as-code-and-configuration-management/roles-and-collections.md).

## Role dependency — Ansible

Metadata vzťah spôsobujúci vykonanie inej role pred závislou role; pri nadmernom používaní môže skryť orchestration graph. Pozri [Roles a collections](docs/07-infrastructure-as-code-and-configuration-management/roles-and-collections.md).

## Role engineering

Disciplína navrhovania roles z pracovných tasks, required permissions, resource scopes, constraints, ownershipu a usage evidence. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Role explosion

Nekontrolovaný rast počtu roles pri modelovaní každej kombinácie tímu, prostredia, aplikácie, resource scope-u a privilege levelu. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Role — Kubernetes

Namespaced Kubernetes RBAC objekt obsahujúci additive allow rules pre resources v konkrétnom namespace. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Role — Kubernetes RBAC

Namespaced RBAC ruleset definujúci povolené verbs nad resources a subresources v konkrétnom namespace scope-e. Pozri [RBAC](docs/09-kubernetes/rbac.md).

## Role vars — Ansible

Role variables s vyššou precedence uložené typicky vo `vars/main.yml`, vhodné najmä pre interné constants namiesto bežných environment overrides. Pozri [Roles a collections](docs/07-infrastructure-as-code-and-configuration-management/roles-and-collections.md).

## RoleBinding

Namespaced RBAC binding udeľujúci Role alebo ClusterRole rules subjects v namespace bindingu. Pozri [RBAC](docs/09-kubernetes/rbac.md).

## RoleBinding — Kubernetes

Kubernetes RBAC objekt, ktorý priraďuje Role alebo ClusterRole principals v konkrétnom namespace. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Roll-forward

Recovery stratégia nasadzujúca nový opravný artifact alebo migration namiesto návratu na starú verziu, často pre nekompatibilný alebo už zmenený shared state. Pozri [Rollback a roll-forward](docs/05-ci-cd-and-release/rollback-and-roll-forward.md).

## Rollback

Návrat k predchádzajúcej verzii aplikácie alebo konfigurácie. Pozri [Software Development Life Cycle](docs/00-foundations/sdlc.md).

## Rollback compatibility

Schopnosť predchádzajúcej application/chart revision bezpečne fungovať s aktuálnou databázovou schema, CRDs, Secrets, APIs, storage a external state-om. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Rollback — deployment

Recovery stratégia obnovujúca predchádzajúci kompatibilný artifact, konfiguráciu, traffic target alebo infraštruktúrny state. Neznamená automaticky návrat dát a external side effects. Pozri [Rollback a roll-forward](docs/05-ci-cd-and-release/rollback-and-roll-forward.md).

## Rollback window

Obdobie, počas ktorého sa zámerne zachováva schema, configuration, artifact a operational kompatibilita potrebná na bezpečný návrat na predchádzajúcu verziu. Pozri [Rollback a roll-forward](docs/05-ci-cd-and-release/rollback-and-roll-forward.md).

## Rolling rollback

Postupné nahrádzanie chybnej novej version fleet predchádzajúcim artifactom pri zachovaní rolling update mechanizmu a jeho compatibility obmedzení. Pozri [Rolling update](docs/05-ci-cd-and-release/rolling-update.md).

## Rolling update

Deployment stratégia postupne nahrádzajúca staré instances novými pri zachovaní časti dostupnej capacity a dočasnej koexistencii versions. Pozri [Rolling update](docs/05-ci-cd-and-release/rolling-update.md).

## Rollout contract

Versionovaný popis artifactu, configu, targetu, cohort, krokov, metrics, observation windows, promotion/abort policy, recovery actions a ownera progressive rollout-u. Pozri [Progressive delivery](docs/05-ci-cd-and-release/progressive-delivery.md).

## Rollout rollback — Deployment

Návrat Deployment Pod template-u na zachovanú staršiu revision; nevracia databázu, queues ani iný external state. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## Rollout state machine

Explicitné stavy produkčnej expozície s povolenými transitions, observation window, success criteria, abort thresholds a rollback alebo roll-forward akciami. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Rollover — search

Lifecycle operácia vytvárajúca nový write index po splnení age, size, document-count alebo shard-size conditions. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Root module — Terraform

Konfigurácia v working directory, nad ktorou sa vykonáva plan/apply; skladá child modules, vlastní environment orchestration a určuje state/backend lifecycle. Pozri [Modules](docs/07-infrastructure-as-code-and-configuration-management/modules.md).

## Rootless container

Container a runtime model fungujúci bez host-root daemon identity, typicky cez user namespaces a unprivileged networking/storage helpers. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Rootless Docker

Docker daemon a containers spustené bez host root identity s user-namespace a userspace mechanizmami, znižujúce niektoré host privilege riziká za cenu feature a networking obmedzení. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Route

Pravidlo určujúce next hop, interface a ďalšie parametre pre destination prefix. Pozri [Routing a default gateway](docs/02-networking-and-web/routing-and-default-gateway.md).

## Route 53 alias record

AWS-specific DNS record smerujúci zone apex alebo subdomain na podporovaný AWS resource či iný record bez bežného CNAME obmedzenia apexu. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Route 53 health check

Externá, alarm-based alebo calculated health evaluation používaná pri Route 53 DNS traffic steeringu a failover-e. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Route 53 Resolver

AWS recursive DNS capability pre VPCs a hybrid DNS, zahŕňajúca inbound/outbound endpoints a forwarding rules. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Route attachment — Gateway API

Proces, ktorým Route po splnení `parentRefs`, listener `allowedRoutes`, hostname/protocol a reference pravidiel začne byť prijatá a programovaná controllerom. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## Route propagation — AWS

Automatické pridávanie routes z podporovaného gateway alebo dynamic routing source-u do route table podľa nakonfigurovaného connectivity modelu. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## Route summarization

Reprezentácia viacerých menších prefixes jedným väčším aggregate prefixom. Pozri [Routing a default gateway](docs/02-networking-and-web/routing-and-default-gateway.md).

## Route tree — Alertmanager

Hierarchická konfigurácia matchers, receivers, grouping a timing, podľa ktorej Alertmanager spracuje každý alert. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Routed Pod network

Pod network model, v ktorom sú Pod CIDRs alebo addresses priamo routovateľné medzi Nodes alebo upstream sieťou bez overlay encapsulation. Pozri [CNI a NetworkPolicy](docs/09-kubernetes/cni-networkpolicy.md).

## Routing rollback

Recovery operácia, ktorá po neúspešnom blue-green cutover-e presmeruje traffic späť na pôvodnú farbu. Nevracia automaticky data state. Pozri [Blue-green deployment](docs/05-ci-cd-and-release/blue-green-deployment.md).

## RPO — Recovery Point Objective

Maximálne prijateľné množstvo dát vyjadrené časovým bodom, ktoré môže byť pri obnove po katastrofe stratené. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## RSS — Resident Set Size

Množstvo pages procesu aktuálne resident v RAM. Pozri [Memory a CPU fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## RTO — Recovery Time Objective

Maximálny prijateľný čas na obnovenie služby alebo business capability po katastrofickom zlyhaní. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Run Command — Systems Manager

Capability na vzdialené vykonanie versionovaného command documentu na jednom alebo viacerých managed nodes s targetingom, rate controls a per-node outputom. Pozri [Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## `runAsNonRoot`

SecurityContext guard požadujúci, aby container process nebežal s root UID; potrebuje kompatibilný image a runtime-resolvable user identity. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## Runner — CI/CD

Agent alebo execution capacity, ktorá prijme job od CI control plane a vykoná ho prostredníctvom zvoleného executora. Runner je zároveň capacity a security boundary. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## Runner isolation

Oddelenie CI jobov, workspace, credentials, cache a execution environmentov tak, aby sa obmedzil cross-project contamination a persistence nedôveryhodného stavu. Pozri [Continuous Integration](docs/05-ci-cd-and-release/continuous-integration.md).

## Runner manager

Dlhšie žijúci GitLab Runner proces alebo service, ktorý polluje job queue a pomocou executora vytvára job runtimes alebo autoscaled workers. Pozri [Runners a executors](docs/06-gitlab/runners-and-executors.md).

## Runner pool

Oddelená skupina runners s definovanými capabilities, trust levelom, network accessom a scaling policy. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## Runner system failure

Job failure spôsobený runnerom, executorom, infrastructure alebo prepare/cleanup vrstvou namiesto samotného user scriptu. Pozri [Runners a executors](docs/06-gitlab/runners-and-executors.md).

## Runspace — PowerShell

Izolovaný PowerShell execution environment s vlastným session state, používaný aj pri paralelnom spracovaní. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## Runtime configuration — container

Configuration dodaná pri vytvorení containeru, napríklad environment, command, mounts, ports, resources a security options, oddelená od immutable image artifactu. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Runtime dependency failure

Zlyhanie knižnice, dynamic linkeru, interpreteru, certificate store alebo iného runtime componentu, ktoré môže vyzerať ako chýbajúci executable napriek existencii file-u. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Runtime shim — containerd

Per-container alebo per-runtime lifecycle proces oddeľujúci container process od containerd daemon lifecycle a poskytujúci task I/O a exit-state coordination. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Runtime socket exposure

Sprístupnenie container-engine API socketu workloadu, ktoré často umožňuje vytvárať privileged containers, mounts alebo inak ovládať host a predstavuje host-admin trust boundary. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## RuntimeClass overhead

CPU a memory overhead runtime sandboxu deklarovaný RuntimeClassom a zohľadnený pri Pod scheduling-u a resource accounting-u podľa podpory. Pozri [Requests, limits a QoS](docs/09-kubernetes/requests-limits-qos.md).

## RuntimeService — CRI

Časť CRI používaná kubeletom na Pod sandbox a container create, start, stop, remove, status a streaming lifecycle. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## S3 Lifecycle

Bucket policy mechanizmus automatizujúci storage-class transitions, expiration current/noncurrent versions a cleanup incomplete multipart uploads. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## S3 Object Lock

S3 WORM retention mechanizmus chrániaci konkrétne object versions pomocou governance/compliance retention alebo legal hold. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## S3 Replication

Asynchronous copy mechanism pre S3 object versions medzi buckets v rovnakom alebo inom Regioni podľa replication rules a IAM/KMS permissions. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## S3 storage class

Per-object S3 storage tier s konkrétnym availability, retrieval latency, request, minimum-duration a cost contractom. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## S3 Versioning

Bucket capability zachovávajúca viac object versions a používajúca delete markers na recovery po overwrite alebo delete operations. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## SaaS

Software as a Service: model poskytujúci hotovú application službu, pričom zákazník typicky vlastní tenant configuration, identities, data usage, retention a integrations. Pozri [IaaS, PaaS a SaaS](docs/11-cloud-and-aws/iaas-paas-saas.md).

## SaaSBOM

Bill of Materials opisujúci software-as-a-service components, services, providers a dependencies v continuously deployed service modeli. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## Safe loader — YAML

Parser režim, ktorý načítava základné dátové typy bez povolenia nebezpečnej language-specific object deserializácie. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Safety state machine

Riadený lifecycle fault experimentu od prechecks cez fault activation a removal až po recovery a cleanup, pričom každý stav má povolené transitions, timeouty a safety guardrails. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## SAML

XML-based federation framework na prenos authentication a attribute assertions medzi Identity Providerom a Service Providerom. Pozri [SAML](docs/13-security-and-identity/saml.md).

## SAML assertion

Signed alebo encrypted XML security artifact obsahujúci statements o subjecte, authentication a attributes. Pozri [SAML](docs/13-security-and-identity/saml.md).

## SAML binding

Definícia transportu SAML messages, napríklad HTTP Redirect, HTTP POST alebo Artifact binding. Pozri [SAML](docs/13-security-and-identity/saml.md).

## SAML metadata

XML trust a configuration dokument obsahujúci entity IDs, endpoints, bindings a signing/encryption certificates. Pozri [SAML](docs/13-security-and-identity/saml.md).

## SAML profile

Kombinácia assertions, protocols a bindings pre konkrétny use case, napríklad Web Browser SSO. Pozri [SAML](docs/13-security-and-identity/saml.md).

## SAML protocol

Request/response messages definované SAML, napríklad AuthnRequest, Response alebo LogoutRequest. Pozri [SAML](docs/13-security-and-identity/saml.md).

## Sample — Prometheus

Timestampovaná hodnota patriaca ku konkrétnej Prometheus time series. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Sample ratio mismatch

Významný rozdiel medzi plánovaným a reálnym pomerom experimentálnych variantov, ktorý môže signalizovať assignment, exposure, crash, logging alebo eligibility problém. Pozri [A/B testing](docs/05-ci-cd-and-release/a-b-testing.md).

## Sampling — telemetry

Výber podmnožiny traces, logs alebo profiles na kontrolu volume a cost pri zachovaní relevantných failures a business operations. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Sandboxed container runtime

Runtime model pridávajúci medzi container workload a host kernel ďalšiu isolation vrstvu, napríklad user-space kernel alebo lightweight virtual machine. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Sanity test

Krátka cielená kontrola konkrétnej zmeny alebo opravy. Význam sa medzi tímami líši, preto musí mať explicitný scope. Pozri [Smoke a regression tests](docs/04-testing-and-quality/smoke-and-regression-tests.md).

## SASL — LDAP

Simple Authentication and Security Layer framework používaný LDAP na podporu rôznych authentication mechanisms nad rámec simple bindu. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## SAST — Static Application Security Testing

Statická bezpečnostná analýza source, bytecode alebo intermediate representation bez spustenia celej aplikácie. Pozri [Security a infrastructure tests](docs/04-testing-and-quality/security-and-infrastructure-tests.md).

## Saturation

Stav, keď resource nestačí okamžite obslúžiť všetku prácu a vzniká queueing alebo throttling. Pozri [Performance a troubleshooting](docs/01-linux-and-systems/performance-and-troubleshooting.md).

## Saturation — USE

Množstvo práce, ktoré resource nedokáže okamžite obslúžiť a prejavuje sa queueingom, wait time, throttlingom alebo rejection. Pozri [USE method](docs/12-observability/use-method.md).

## SBOM

Machine-readable inventory software components a relationships viazaný na konkrétny software artifact alebo system. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## SBOM accuracy

Miera, do akej component identities, versions, digests, suppliers a relationships zodpovedajú skutočnému artifactu. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## SBOM attestation

Signed supply-chain statement, ktorý viaže SBOM predicate na konkrétny artifact digest a producer identity. Pozri [SBOM](docs/13-security-and-identity/sbom.md) a [Image signing](docs/13-security-and-identity/image-signing.md).

## SBOM completeness

Deklarovaný rozsah a miera, do akej SBOM zachytáva všetky components a relationships v definovanom subjecte. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## SBOM diff

Semantic comparison dvoch SBOM versions zamerané na component, version, relationship, supplier a license changes namiesto textového JSON diffu. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## SBOM freshness

Vzťah SBOM ku konkrétnemu aktuálnemu immutable release artifactu a času jeho generation; creation timestamp bez digest bindingu freshness nedokazuje. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## SBOM ingestion

Pipeline na authentication source-u, schema validation, signature verification, subject binding, normalization a indexing prijatej SBOM. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## SBOM subject

Konkrétny artifact alebo system, ktorý SBOM opisuje, preferovane identifikovaný immutable digestom a doplňujúcimi package metadata. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## SCA — Software Composition Analysis

Analýza third-party dependencies, transitívneho graphu, licencií a známych vulnerabilities. Pozri [Security a infrastructure tests](docs/04-testing-and-quality/security-and-infrastructure-tests.md).

## Scalability

Schopnosť systému zvýšiť alebo znížiť spracovateľskú kapacitu bez neprimeraného zhoršenia výkonu, spoľahlivosti alebo nákladov. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Scalability test

Performance test overujúci, ako sa kapacita a SLO menia po pridaní alebo odobratí resources. Pozri [Performance, load a stress tests](docs/04-testing-and-quality/performance-load-stress-tests.md).

## Scalar — YAML

YAML node reprezentujúci jednu hodnotu, napríklad string, number, boolean alebo null. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Scale-down stabilization — HPA

Časové okno, počas ktorého HPA zohľadňuje predchádzajúce odporúčania a tlmí príliš rýchle znižovanie replicas. Pozri [HPA a autoscaling](docs/09-kubernetes/hpa-autoscaling.md).

## Scale subresource — Kubernetes

Štandardizované API rozhranie vystavujúce desired a current replica informácie škálovateľného workloadu pre HPA a ďalších clients. Pozri [HPA a autoscaling](docs/09-kubernetes/hpa-autoscaling.md).

## scaling activity — Auto Scaling

Auditovateľný záznam Auto Scaling launch, terminate alebo capacity-change pokusu vrátane statusu a failure reasonu. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## scaling policy — Auto Scaling

Policy meniaca desired capacity Auto Scaling Groupu podľa target tracking, step, schedule, prediction alebo iného demand contractu. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## `ScheduleAnyway` — topology spread

Soft topology spread behavior, pri ktorom scheduler môže Pod umiestniť aj pri porušení ideálneho skew a používa constraint pri scoring-u. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Scheduler profile

Konfigurácia kube-scheduleru s vlastným `schedulerName`, aktívnymi Scheduling Framework plugins, weights a plugin arguments. Pozri [Scheduling](docs/09-kubernetes/scheduling.md).

## `schedulerName`

Pod spec field určujúci scheduler zodpovedný za binding Podu; ak zodpovedajúci scheduler nebeží, Pod zostane unscheduled. Pozri [Scheduling](docs/09-kubernetes/scheduling.md).

## Scheduling Framework

Pluggable architektúra kube-scheduleru rozdeľujúca scheduling cycle na extension points ako QueueSort, Filter, Score, Reserve, Permit a Bind. Pozri [Scheduling](docs/09-kubernetes/scheduling.md).

## Scheduling queue

Interná scheduler štruktúra pre nové, backoff a unschedulable Pods čakajúce na ďalší scheduling attempt. Pozri [Scheduling](docs/09-kubernetes/scheduling.md).

## Schema compatibility

Schopnosť aktívnych application a data consumers fungovať s aktuálnou sadou tables, columns, constraints, types a indexov počas deploymentu. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Schema period — Loki

Časovo ohraničená Loki storage schema configuration používaná na forward-compatible zmenu index/storage formátu pre nové dáta. Pozri [Loki](docs/12-observability/loki.md).

## Schema URL — OpenTelemetry

Reference na semantic-convention schema používanú resource alebo instrumentation scope-om na podporu compatibility a migration. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Schema validation

Overenie dát voči deklarovaným typom, required fields a constraints. Neoveruje automaticky všetky business a runtime podmienky. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Score plugin — Kubernetes scheduler

Scheduling Framework plugin prideľujúci feasible Nodes relatívne skóre podľa soft preferencií a placement stratégie. Pozri [Scheduling](docs/09-kubernetes/scheduling.md).

## Scrape — Prometheus

Periodické HTTP načítanie metrics endpointu targetu, validácia samples a ich ingestion do Prometheus TSDB. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Scratch image

Minimalistický Dockerfile stage `FROM scratch` bez base filesystemu, vhodný iba pre artifact s kompletne vyriešenými runtime dependencies. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## SDLC — Software Development Life Cycle

Riadený životný cyklus softvéru od potreby po vyradenie. Pozri [Software Development Life Cycle](docs/00-foundations/sdlc.md).

## Search base — LDAP

Distinguished Name určujúci východiskový entry pre LDAP Search operation. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## Search scope — LDAP

Rozsah LDAP Search operation: base object, one level alebo subtree. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## Seccomp profile — container

System-call filter policy aplikovaná na container processes s cieľom znížiť dostupný host-kernel attack surface. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Seccomp profile — Kubernetes

Runtime syscall filter vybraný cez Pod alebo container security context, napríklad RuntimeDefault alebo Localhost. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## Second converge

Druhý automation run nad už nakonfigurovaným targetom používaný na overenie, že desired state je stabilný a nevznikajú recurring changes. Pozri [Ansible idempotencia](docs/07-infrastructure-as-code-and-configuration-management/ansible-idempotency.md).

## Secret

Citlivý credential alebo cryptographic material, ktorého získanie umožňuje access, impersonation, decryption, signing alebo privileged operation. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Secret classification

Dokumentovaný contract secretu zahŕňajúci ownera, účel, consumers, lifetime, rotation, revocation, delivery a compromise impact. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Secret encryption at rest

API server configuration šifrujúca persisted Secret payloady pred uložením do etcd; nerieši disclosure cez API, Node, Pod memory, logs alebo kompromitovanú workload identity. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Secret — Kubernetes

Namespaced API objekt pre citlivé bytes alebo strings, ktorého base64 reprezentácia nie je encryption a vyžaduje RBAC, encryption-at-rest, audit a bezpečný consumer lifecycle. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Secret lifecycle

Proces creation, storage, authorization, distribution, use, rotation, revocation a destruction secretu. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Secret push protection — GitLab

Pre-receive alebo push-time kontrola, ktorá deteguje podporované secret patterns pred prijatím commitu a môže push zablokovať. Pozri [Security scanning](docs/06-gitlab/security-scanning.md).

## Secret replication — Secrets Manager

Service capability vytvárajúca regionálne replicas secretu s vlastným per-Region encryption a status contractom. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Secret resource policy

Resource-based policy na Secrets Manager secret-e určujúca principals a conditions pre access, najmä pri cross-account modeli. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Secret revocation

Technické zneplatnenie credentialu v authoritative cieľovom systéme. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Secret rotation

Riadený lifecycle vytvorenia nového credentialu, distribúcie a rollout-u consumerov, overlap/verification, revocation starého credentialu a cleanup starých copies. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Secret staging label

Pomenovaný movable label, napríklad `AWSCURRENT`, `AWSPREVIOUS` alebo `AWSPENDING`, ktorý označuje úlohu konkrétnej secret version v lifecycle. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Secret version — Secrets Manager

Immutable secret value revision identifikovaná version ID a voliteľnými staging labels. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Secret zero

Prvotný trust anchor alebo credential potrebný na získanie ďalších secrets. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Secrets engine — Vault

Vault component mountnutý na path, ktorý ukladá, generuje alebo cryptographically spracúva citlivé dáta. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Secure Access Service Edge — SASE

Architecture category kombinujúca networking a cloud-delivered security services; môže podporovať Zero Trust, ale sama nie je dôkazom resource-level policy. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Security categorization

Určenie impact levelu straty confidentiality, integrity a availability pre konkrétny system alebo information type. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Security control

Management, operational, technical alebo physical safeguard navrhnutý na ochranu assets a zníženie security risku. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Security Group — AWS

Stateful allow-only firewall priradený k ENI alebo podporovanému resource-u; return traffic pre tracked connection je povolený connection trackingom. Pozri [Security Groups a Network ACLs](docs/11-cloud-and-aws/security-groups-network-acls.md).

## Security Group reference — AWS

Security Group rule používajúca inú SG ako source alebo destination workload identity podľa podporovaného connectivity modelu namiesto statického CIDR. Pozri [Security Groups a Network ACLs](docs/11-cloud-and-aws/security-groups-network-acls.md).

## Security in the cloud — AWS

Zákaznícka responsibility vrstva zahŕňajúca identity, configuration, data, workload OS/application, logging, backup a recovery podľa použitej AWS služby. Pozri [Shared responsibility model](docs/11-cloud-and-aws/shared-responsibility-model.md).

## Security objective

Konkrétny požadovaný security outcome pre asset alebo system boundary, napríklad tenant isolation, transaction integrity alebo bounded recovery time. Pozri [Threat modeling](docs/13-security-and-identity/threat-modeling.md).

## Security of the cloud — AWS

AWS responsibility vrstva zahŕňajúca physical facilities, hardware, host platform, virtualization a provider-managed service infrastructure. Pozri [Shared responsibility model](docs/11-cloud-and-aws/shared-responsibility-model.md).

## Security pillar — Well-Architected

Well-Architected pillar zameraný na identity, traceability, infrastructure protection, data protection, detection a incident response. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Security report artifact — GitLab

Machine-readable analyzer report, ktorý GitLab spracúva na zobrazenie security findings v pipeline, merge requeste alebo vulnerability-management vrstvách. Pozri [Security scanning](docs/06-gitlab/security-scanning.md).

## Security requirement

Testovateľná implementačná alebo prevádzková povinnosť odvodená z threatu, ktorá určuje actor, condition, expected control behavior a failure semantics. Pozri [Threat modeling](docs/13-security-and-identity/threat-modeling.md).

## Security risk

Riziko vznikajúce z možnej straty confidentiality, integrity alebo availability s ohľadom na pravdepodobnosť a dopad. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Security Service Edge — SSE

Cloud-delivered security service model typicky zahŕňajúci ZTNA, secure web gateway a CASB capabilities. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Security tooling account — AWS

Oddelený member account používaný ako delegated administrator a operational scope pre organization-wide security findings, detection a response tooling. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Segment — Lucene

Immutable index fragment v rámci shardu; nové documents sa sprístupňujú refreshom a segments sa neskôr zlučujú merge procesom. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Selector — Kubernetes

Výraz vyberajúci objects podľa labels a tvoriaci kritický contract pre controllers, Services, policy alebo CLI queries. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Selector-label helper — Helm

Named template generujúci stabilné labels použité workload selectorom aj Pod template-om; nesmie obsahovať mutable chart alebo application version metadata. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Selectorless Service

Service bez `spec.selector`, ktorého backend EndpointSlices spravuje operator alebo iný explicitný owner, často pre external alebo manually discovered endpoints. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## Self-grading — CKA

Hodnotenie lab úloh cez explicitné validation commands, partial-credit criteria, čas a bezpečnosť namiesto subjektívneho dojmu. Pozri [CKA timed labs](docs/10-helm-and-cka/cka-timed-labs.md).

## SELinux options — Kubernetes

SecurityContext fields nastavujúce SELinux label identity container procesu a volumes podľa host policy, runtime a storage podpory. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## SELinux security context

Label subjectu alebo objektu obsahujúci SELinux user, role, type a prípadne level/range. Pozri [SELinux a AppArmor](docs/01-linux-and-systems/selinux-and-apparmor.md).

## Semantic compatibility — data

Zachovanie rovnakého alebo explicitne transformovaného business významu hodnôt naprieč application a schema verziami. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Semantic Conventions — OpenTelemetry

Štandardizované názvy a významy telemetry operations, resources, attributes, metrics a events. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Semantic conventions — telemetry

Štandardizované názvy a významy operations, resources a attributes umožňujúce interoperabilitu instrumentation a backendov. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Semantic Versioning

Versioning kontrakt vo formáte `MAJOR.MINOR.PATCH`, ktorý komunikuje význam zmien voči deklarovanému public API. Pozri [Semantic Versioning](docs/05-ci-cd-and-release/semantic-versioning.md).

## Sender-constrained token

Access token viazaný na client key alebo proof mechanizmus, napríklad mTLS alebo DPoP. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Sending queue — OpenTelemetry

Exporter queue absorbujúca krátkodobý downstream výpadok alebo throttling pred retry alebo drop behaviorom. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Separation of duties

Rozdelenie právomocí tak, aby citlivú zmenu nevytvorila, neschválila a nenasadila bez nezávislej kontroly jediná identita; môže byť implementované automatizovanými policy a approvals. Pozri [Continuous Delivery](docs/05-ci-cd-and-release/continuous-delivery.md).

## Serial — Terraform state

Monotónne rastúce číslo snapshotu v jednej state lineage používané na rozpoznanie novšej verzie a ochranu pred stale overwrite. Pozri [Terraform state](docs/07-infrastructure-as-code-and-configuration-management/terraform-state.md).

## Series churn

Rýchle vytváranie a zánik time series, ktoré zaťažuje WAL, index, compaction a remote storage aj pri nižšom počte súčasne active series. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Server-side apply — Kubernetes

Deklaratívny API update model, pri ktorom API server merge-uje intent a sleduje field ownership jednotlivých managers. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Service contract — cloud

Dokumentovaný súbor support, availability, security, data, backup, lifecycle a responsibility podmienok konkrétnej cloud služby. Pozri [IaaS, PaaS a SaaS](docs/11-cloud-and-aws/iaas-paas-saas.md).

## Service control policy — SCP

AWS Organizations guardrail definujúci maximálny permissions envelope pre principals v member accounts; sám access neudeľuje a neobmedzuje management account. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Service dataplane

Node alebo network-plugin mechanizmus implementujúci Service virtual IP, backend selection a packet forwarding podľa EndpointSlices. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## Service dataplane — Kubernetes

Node alebo cluster networking vrstva implementujúca virtual Service IP a forwarding na EndpointSlice backends, napríklad cez kube-proxy alebo alternatívny eBPF dataplane. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## Service discovery — Prometheus

Mechanizmus dynamicky vytvárajúci potenciálne scrape targets a dočasné metadata labels z Kubernetes, cloud, Consul, DNS alebo iného source-u. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Service FQDN

Plné cluster-local DNS meno Service-u v tvare `<service>.<namespace>.svc.<cluster-domain>`. Pozri [Cluster DNS](docs/09-kubernetes/cluster-dns.md).

## Service graph

Derived graph caller/callee relationships a performance characteristics vytvorený zo spans; jeho úplnosť závisí od instrumentation a sampling coverage. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Service — Kubernetes

Namespaced API contract poskytujúci stabilné meno, virtual address a port model pre dynamickú backend population reprezentovanú EndpointSlices. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## Service-linked role — AWS IAM

IAM role previazaná s konkrétnou AWS službou, ktorej trust a permissions lifecycle je definovaný danou službou. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## Service port

Port publikovaný Kubernetes Service contractom pre klientov, odlišný od backend `targetPort`. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## Service principal name — SPN

Kerberos identity služby viazaná na service class a hostname, ktorú client používa pri žiadosti o service ticket. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Service Provider — SAML

Aplikácia alebo služba dôverujúca validovaným assertions od SAML Identity Providera. Pozri [SAML](docs/13-security-and-identity/saml.md).

## Service responsibility matrix

Tabuľka mapujúca pre konkrétnu cloud službu provider, customer a shared responsibilities v oblastiach compute, identity, network, data, encryption, logging, patching a recovery. Pozri [Shared responsibility model](docs/11-cloud-and-aws/shared-responsibility-model.md).

## Service selector

Label selector, podľa ktorého EndpointSlice controller odvodzuje backend Pods pre selector-based Service. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## Service ticket — Kerberos

Časovo obmedzený ticket vydaný KDC pre konkrétny service principal a šifrovaný long-term key-om služby. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Service troubleshooting chain

Diagnostické poradie Service selector → EndpointSlice readiness → targetPort → dataplane → Pod listen socket → application behavior. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Service virtualization

Nahradenie externého systému kontrolovaným simulátorom alebo sandboxom tak, aby bol test deterministickejší a lacnejší. Pozri [End-to-end a acceptance tests](docs/04-testing-and-quality/end-to-end-and-acceptance-tests.md).

## ServiceAccount

Namespaced non-human Kubernetes identity používaná Podmi a automation; permissions získava oddelene cez RBAC alebo inú authorization policy. Pozri [ServiceAccount](docs/09-kubernetes/serviceaccount.md).

## ServiceAccount token audience

Identifikátor intended recipienta tokenu, ktorý zabraňuje použitiu tokenu vydaného pre jednu službu voči inému verifierovi. Pozri [ServiceAccount](docs/09-kubernetes/serviceaccount.md).

## ServiceAccount username

Canonical authenticated identity `system:serviceaccount:<namespace>:<name>` používaná v authorization a audit logoch. Pozri [ServiceAccount](docs/09-kubernetes/serviceaccount.md).

## Session

Dočasný authenticated context vytvorený po úspešnej authentication a používaný na ďalšie authorization decisions. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Session affinity

Load-balancing policy smerujúca klienta alebo key opakovane na rovnaký backend. Pozri [Load balancing](docs/02-networking-and-web/load-balancing.md).

## Session affinity — Service

Service behavior preferujúci rovnaký backend pre klienta podľa ClientIP a timeoutu; nie je náhradou durable session storage. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## Session binding — Zero Trust

Cryptographic alebo policy väzba session/token contextu na konkrétny device, key, client alebo communication channel s cieľom obmedziť replay ukradnutého credentialu. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Session Manager

Systems Manager capability poskytujúca IAM-authorized interactive shell alebo port-forwarding sessions bez potreby inbound SSH/RDP portu. Pozri [Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## Severity — log

Klasifikácia operational závažnosti log recordu, napríklad DEBUG, INFO, WARN, ERROR alebo FATAL, ktorá musí odrážať význam pre konkrétnu operáciu. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Shadow deployment

Deployment, ktorý spracúva kópiu produkčného workloadu bez autoritatívnej response a s blokovanými alebo izolovanými side effects. Pozri [Shadow deployment](docs/05-ci-cd-and-release/shadow-deployment.md).

## Shadow read

Neautoritatívne čítanie z novej schema alebo store vykonané popri primárnom čítaní na porovnanie výsledkov pred prepnutím. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Shadow traffic

Kópia reálneho produkčného trafficu posielaná novému systému bez použitia jeho response ako výsledku pre používateľa; vyžaduje kontrolu side effects a citlivých dát. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Shallow clone

Clone s obmedzenou ancestry históriou, typicky vytvorený cez `--depth`. Znižuje prenos, ale obmedzuje operácie závislé od plného commit graphu. Pozri [Clone, fetch, pull a push](docs/03-git-and-automation/clone-fetch-pull-push.md).

## Shamir shares — Vault

Threshold shares používané na rekonštrukciu Vault unseal materialu v manuálnom Shamir seal modeli. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Shard allocation

Rozhodovanie search clusteru, na ktorom node a failure domain-e budú umiestnené primary a replica shard copies. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Shared control — cloud

Security alebo operations control, pri ktorom provider poskytuje platform capability a zákazník ju musí správne nakonfigurovať, používať, monitorovať alebo integrovať. Pozri [Shared responsibility model](docs/11-cloud-and-aws/shared-responsibility-model.md).

## Shared kernel

Model, v ktorom viac host a container processes používa ten istý kernel, hoci môže mať odlišné namespace views a resource limits. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Shared responsibility

Model, v ktorom provider a zákazník vlastnia odlišné, ale navzájom závislé časti security, availability, configuration, data protection a incident response. Pozri [IaaS, PaaS a SaaS](docs/11-cloud-and-aws/iaas-paas-saas.md).

## Shared services account — AWS

AWS member account prevádzkujúci organization-wide platform services ako artifacts, directory integrations, CI, observability alebo package mirrors. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Shell executor — GitLab Runner

Executor spúšťajúci CI/CD job priamo na runner hoste s jeho používateľskými oprávneniami a slabou isolation medzi workloadom a hostom. Pozri [Runners a executors](docs/06-gitlab/runners-and-executors.md).

## Shell expansion

Fáza, v ktorej shell spracuje parameter, command a arithmetic expansion, word splitting a pathname expansion pred spustením príkazu. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md).

## Shift-left

Presun vhodných rozhodnutí, kontrol a feedbacku do skorších fáz delivery, kde možno riziko zachytiť lacnejšie bez neprimeranej straty fidelity. Pozri [Shift-left](docs/04-testing-and-quality/shift-left.md).

## Shift-left policy

Policy evaluation vykonaná pred runtime, napríklad v IDE, pull requeste alebo CI, s cieľom poskytnúť skorú spätnú väzbu. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Shift-right

Rozšírenie validácie, observability a experimentovania do deploymentu a produkcie s kontrolovaným blast radiusom a jasnými rozhodovacími kritériami. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## `ShouldProcess` — PowerShell

PowerShell mechanizmus podporujúci `-WhatIf` a `-Confirm` pre vedome označené mutation operácie. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## Showback — FinOps

Interné zobrazenie costu tímom alebo produktom bez priameho finančného preúčtovania. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Sidecar container

Auxiliary container bežiaci v rovnakom Pode ako hlavná aplikácia a zdieľajúci jej placement, network a Pod lifecycle boundary. Pozri [Pod](docs/09-kubernetes/pod.md).

## Signal latency

Čas medzi vznikom zmeny alebo failure a dostupnosťou dostatočne úplného signálu pre rollout či experiment decision. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Signal — observability

Typ telemetry reprezentujúci určitý pohľad na systém, napríklad metric, log, trace, event alebo profile. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Signal quality

Hodnotenie telemetry podľa correctness, completeness, freshness, contextu, correlation, schema stability, security, cost a ownershipu. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Signature discovery

Proces nájdenia signatures a attestations súvisiacich s artifact digestom cez OCI Referrers alebo ecosystem-specific fallback convention. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## signed cookie — CloudFront

CloudFront private-content authorization token v cookies, ktorý môže oprávniť clienta na skupinu paths alebo resources podľa policy a expiry. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Signed image subject

OCI image index alebo platform manifest digest, ku ktorému sa signature alebo attestation explicitne viaže. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Signed policy bundle

Policy bundle s cryptographic integrity a publisher-authenticity evidence overovanou pred activation v policy engine. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## signed URL — CloudFront

Časovo alebo policy obmedzená CloudFront URL podpísaná trusted keyom pre access ku konkrétnemu private resource-u. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Signing identity policy

Authorization pravidlá určujúce, ktoré issuers, identities, repositories, workflows a contexts smú podpisovať konkrétne artifacts. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Sigstore

Open-source ecosystem pre software signing, identity-bound certificates, transparency a verification tooling. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Silence — alerting

Dočasné potlačenie notifications pre alerts matchujúce definovaný label set, s ownerom, dôvodom a expiration. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Silence — Alertmanager

Časovo ohraničené muting pravidlo nad alert label matchers vytvorené používateľom alebo API. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Silent error

Failure, ktorý neprodukuje bežný explicitný error status, napríklad `200` s chybným obsahom, nespracovaná async message alebo neobnoviteľný backup. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Simple Bind — LDAP

LDAP Bind mechanism používajúci identity a password; musí byť chránený TLS, pretože sám neposkytuje transport encryption. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## Single Logout — SAML

SAML protocol na koordináciu logoutu medzi IdP a SP sessions, ktorý môže zlyhať čiastočne a nepredstavuje automatickú globálnu revocation. Pozri [SAML](docs/13-security-and-identity/saml.md).

## Single-release dependency graph — Helm

Model, v ktorom parent chart a všetky enabled first-level aj transitive subcharts vytvárajú jednu release revision a spoločný upgrade/rollback failure domain. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Single-writer storage

Storage contract povoľujúci v danom čase iba jedného aktívneho writer-a, ktorý potrebuje scheduling, attachment alebo fencing controls na zabránenie concurrent corruption. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## Skip-and-return strategy — CKA

Time-management postup, pri ktorom kandidát preskočí úlohu bez jasnej rýchlej cesty, označí ju a vráti sa po získaní jednoduchších bodov. Pozri [CKA timed labs](docs/10-helm-and-cka/cka-timed-labs.md).

## SLAAC — Stateless Address Autoconfiguration

IPv6 mechanizmus, ktorým host vytvára adresu z prefixu oznamovaného Router Advertisement. Pozri [IPv4, IPv6 a subnetting](docs/02-networking-and-web/ipv4-ipv6-subnetting.md).

## Slow burn

Dlhšie mierne prekračovanie reliability targetu, ktoré spotrebúva error budget pomalšie, ale systematicky. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## slow start — ELB

ALB target-group mechanismus postupne zvyšujúci traffic newly healthy targetu počas warmup intervalu. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## SLSA Build L1

SLSA Build level, pri ktorom pre artifact existuje automaticky generovaná provenance, ale nemusí poskytovať silnú tamper resistance. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## SLSA Build L2

SLSA Build level vyžadujúci signed provenance generovanú hosted build platformou a consumer-side authenticity verification. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## SLSA Build L3

SLSA Build level vyžadujúci hardened build platformu s izoláciou build runs a oddelením provenance signing materialu od user-defined build steps. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## SLSA Build track

SLSA track definujúci guarantees pre build provenance, hosted build platform a hardened build isolation. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## SLSA Source track

SLSA track definujúci rastúce guarantees pre version-controlled source, history, source provenance, kontinuálne technical controls a two-party review. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Smoke test

Krátky široký test overujúci, či je build alebo deployment dostatočne funkčný na pokračovanie ďalších kontrol alebo prevádzky. Pozri [Smoke a regression tests](docs/04-testing-and-quality/smoke-and-regression-tests.md).

## SNAT — Source NAT

Preklad source adresy alebo portu, používaný typicky pri outbound komunikácii. Pozri [NAT](docs/02-networking-and-web/nat.md).

## SNI — Server Name Indication

TLS extension prenášajúca hostname, aby server alebo proxy vybral správny certificate a virtual host. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## SOA-C03

Aktuálny exam code AWS Certified CloudOps Engineer – Associate s piatimi doménami a váhami 22 %, 22 %, 22 %, 16 % a 18 %. Pozri [SOA-C03 guide](docs/11-cloud-and-aws/cloudops-engineer-associate-soa-c03.md).

## Soak test

Dlhodobý performance test hľadajúci memory leaks, resource leaks, queue growth a kumulatívne zlyhania. Pozri [Performance, load a stress tests](docs/04-testing-and-quality/performance-load-stress-tests.md).

## Socket

Kernel endpoint komunikácie sprístupnený procesu cez file descriptor. Pozri [Ports a sockets](docs/02-networking-and-web/ports-and-sockets.md).

## Software Composition Analysis — SCA

Analýza application dependencies a package metadata na identifikáciu známych vulnerabilities, license information a component inventory; potrebuje reachability a runtime context pre presnejšiu prioritizáciu. Pozri [Vulnerability a patch management](docs/13-security-and-identity/vulnerability-and-patch-management.md).

## Software supply chain

Súbor ľudí, identities, source repositories, dependencies, build systems, tools, registries, release procesov a deployment controls, ktoré môžu ovplyvniť výsledný software artifact. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Source/destination check — AWS

EC2 network-interface kontrola vyžadujúca, aby instance bola source alebo destination trafficu; network appliance alebo NAT instance ju môže potrebovať vypnúť. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## Source provenance

Attestation opisujúca, ako konkrétna source revision vznikla, kto a aký process ju vytvoril a ktoré source-control controls boli presadené. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Source revision

Konkrétny logicky immutable snapshot repository identifikovaný revision ID, napríklad Git commit SHA, spolu s relevantnou version-control metadata. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Source SBOM

SBOM generovaná zo source manifests, lockfiles a repository contentu pred vytvorením final artifactu. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## Span

Jednotka distributed trace-u reprezentujúca jednu časovo ohraničenú operation s parent relation, attributes, events a statusom. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Span event

Časovo označená bodová udalosť priradená ku konkrétnemu span-u, napríklad exception, retry alebo cache miss. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Span link

Vzťah medzi spanmi používaný pri async, batch alebo fan-out causalite, ktorá nevytvára jednoduchý parent-child strom. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## SPDX 3.0.1

Verzia System Package Data Exchange specification s profile-oriented modelom pre software, licensing, security, build a ďalšie system information. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## SPIFFE ID

URI-form identity workloadu v SPIFFE trust domain-e, prenášaná v cryptographically verifiable SVID. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Spike test

Performance test prudkej zmeny trafficu, ktorý overuje autoscaling, queues, caches, connection pools a recovery. Pozri [Performance, load a stress tests](docs/04-testing-and-quality/performance-load-stress-tests.md).

## SPIRE

Production-ready implementation SPIFFE APIs používajúca node a workload attestation na vydávanie a rotation SVIDs. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Splatting — PowerShell

Odovzdanie kolekcie named alebo positional parameters príkazu pomocou hashtable alebo array. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## Split-horizon DNS

DNS model, v ktorom rovnaké meno vracia rozdielne odpovede podľa resolvera, siete alebo klientského contextu. Pozri [DNS](docs/02-networking-and-web/dns.md).

## Spot Instance

EC2 capacity s nižšou cenou a možnosťou interruption zo strany AWS, vhodná pre interruption-tolerant workloady s drain, checkpoint a fallback modelom. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Spy — test double

Test double alebo wrapper zaznamenávajúci uskutočnené interakcie na neskoršie assertions. Pozri [Mocks, stubs a fakes](docs/04-testing-and-quality/mocks-stubs-fakes.md).

## Squash merge

Integrácia, ktorá vytvorí jeden výsledný commit bez merge ancestry na feature tip. Pozri [Merge a rebase](docs/03-git-and-automation/merge-and-rebase.md).

## SRV record — Kubernetes DNS

DNS record vytvorený pre pomenovaný Service port, ktorý publikuje protocol, port a target service alebo per-endpoint hostname. Pozri [Cluster DNS](docs/09-kubernetes/cluster-dns.md).

## SSH agent

Proces vykonávajúci podpisové operácie pomocou odomknutých private keys v pamäti. Pozri [SSH](docs/01-linux-and-systems/ssh.md).

## SSM Agent

Node-side agent komunikujúci so Systems Manager control plane a vykonávajúci podporované command, session, inventory, patch a state operations. Pozri [Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## Stable bucketing

Deterministické mapovanie subjektov do percentuálnych rollout alebo experiment buckets tak, aby sa variant nemenil náhodne medzi requestmi. Pozri [Feature flags](docs/05-ci-cd-and-release/feature-flags.md).

## Stable input — automation

Vstup s kontrolovanou identitou, typom a lifecycle, ktorého neočakávaná mutácia nespôsobuje nepredvídateľné recurring changes. Pozri [Ansible idempotencia](docs/07-infrastructure-as-code-and-configuration-management/ansible-idempotency.md).

## Stable network identity — StatefulSet

Predvídateľné per-ordinal DNS meno StatefulSet Podu, ktoré pretrváva ako logical slot identity naprieč Pod replacementom. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Stable ordinal identity — StatefulSet

Logical identita StatefulSet repliky odvodená z názvu a ordinalu, napríklad `db-0`, zachovaná pri replacement-e, hoci Pod UID a process sa zmenia. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Stage — CI/CD

Logická skupina jobs alebo broad ordering barrier v pipeline. Stage nie je samostatná execution unit a pri presnom DAG modeli nemusí určovať všetky dependencies. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## Staging area

Používateľský názov pre Git index ako pripravovaný snapshot ďalšieho commitu. Pozri [Working tree, staging area a repository](docs/03-git-and-automation/working-tree-staging-repository.md).

## Staleness — Prometheus

Semantics, ktorou Prometheus prestane považovať starú sample za aktuálnu po zmiznutí targetu alebo series. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Standing privilege

Permission alebo role, ktorá je principalu aktívne pridelená nepretržite bez samostatnej time-bound activation. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## Starting deadline — CronJob

Maximálne oneskorenie po plánovanom čase, počas ktorého môže CronJob controller ešte vytvoriť príslušný Job. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## StartTLS — LDAP

LDAP extended operation, ktorá upgraduje existujúcu plaintext LDAP connection na TLS-protected connection. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## Startup health

Schopnosť workloadu dokončiť inicializáciu v očakávanom čase; je odlišná od dlhodobej liveness a readiness. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Startup probe

Kubelet probe chrániaca pomaly štartujúci container tým, že odloží liveness a readiness hodnotenie, kým inicializácia neuspeje alebo neprekročí failure hranicu. Pozri [Probes](docs/09-kubernetes/probes.md).

## Stash — Git

Lokálny Git stav uchovávajúci dočasné working-tree a index changes pod `refs/stash`. Nie je náhradou remote backupu. Pozri [Cherry-pick a stash](docs/03-git-and-automation/cherry-pick-and-stash.md).

## State-based testing

Testovanie výsledného outputu alebo stavu namiesto detailného overovania interných interakcií. Pozri [Mocks, stubs a fakes](docs/04-testing-and-quality/mocks-stubs-fakes.md).

## State boundary — Terraform

Rozsah resources zdieľajúcich jeden state, lock, permissions, plan/apply lifecycle a failure blast radius. Pozri [Infrastructure as Code principles](docs/07-infrastructure-as-code-and-configuration-management/infrastructure-as-code-principles.md) a [Terraform state](docs/07-infrastructure-as-code-and-configuration-management/terraform-state.md).

## State locking — Terraform

Backend-supported koordinácia, ktorá bráni súbežným Terraform write operáciám pracovať s rovnakým state-om a vytvoriť lost update alebo corruption. Pozri [Remote backend a state locking](docs/07-infrastructure-as-code-and-configuration-management/remote-backend-and-state-locking.md).

## State Manager

Systems Manager capability periodicky aplikujúca idempotentné document associations na target managed nodes na udržiavanie desired configuration. Pozri [Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## State snapshot — Terraform

Konkrétna verzia Terraform state-u obsahujúca resource bindings, known attributes, outputs a metadata ako lineage a serial. Pozri [Terraform state](docs/07-infrastructure-as-code-and-configuration-management/terraform-state.md).

## State surgery — Terraform

Riadená zmena state metadata pomocou príkazov ako `state mv`, `state rm` alebo výnimočne recovery push, vykonaná s lockom, backupom, review a následným planom. Pozri [Terraform state](docs/07-infrastructure-as-code-and-configuration-management/terraform-state.md).

## Stateful firewall

Firewall udržiavajúci connection/flow state a používajúci ho pri rozhodovaní o packets. Pozri [Firewally](docs/02-networking-and-web/firewalls.md).

## StatefulSet

Kubernetes workload controller poskytujúci skupine Podov stabilné ordinal identities, ordered lifecycle a možnosť per-replica persistent storage. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## StatefulSet partition

RollingUpdate hranica, ktorá aktualizuje iba StatefulSet Pody s ordinalom väčším alebo rovným nastavenej partition hodnote. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Stateless firewall

Firewall posudzujúci každý packet podľa explicitných pravidiel bez connection state. Pozri [Firewally](docs/02-networking-and-web/firewalls.md).

## Static analysis

Analýza source alebo jeho reprezentácie bez vykonania celej aplikácie, napríklad linting, type checking alebo data-flow analysis. Pozri [Static analysis, linting a type checking](docs/04-testing-and-quality/static-analysis-linting-type-checking.md).

## Static environment — GitLab

Dlhodobo opakovane používaný environment s pevným názvom, napríklad staging alebo production. Pozri [Environments, deployments a releases](docs/06-gitlab/environments-deployments-releases.md).

## Static import — Ansible

Reusable content spracovaný staticky pri parse phase, čím sa od dynamic include odlišuje v timing-u, listovaní, tags a variable/condition semantics. Pozri [Modules, tasks, plays a playbooks](docs/07-infrastructure-as-code-and-configuration-management/modules-tasks-plays-playbooks.md).

## Static inventory — Ansible

Inventory hosts, groups a variables deklarované v versionovanom INI alebo YAML source namiesto runtime discovery cez external API. Pozri [Inventory](docs/07-infrastructure-as-code-and-configuration-management/inventory.md).

## Static Pod

Pod spravovaný priamo kubeletom na konkrétnom Node-e z local manifestu, bez bežného scheduler/controller ownershipu. Pozri [Kubernetes architecture](docs/09-kubernetes/kubernetes-architecture.md) a [Pod](docs/09-kubernetes/pod.md).

## Static provisioning — Kubernetes storage

Model, v ktorom administrator vytvorí PV pre vopred existujúci storage asset a PVC sa naň následne bindne. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Static secret

Dlhšie žijúca a opakovane používaná secret hodnota, ktorá potrebuje explicitnú rotation a revocation. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Static separation of duties

Constraint zakazujúci prideliť jednému principalu konfliktujúce roles alebo entitlements súčasne. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Steady state — chaos engineering

Merateľné používateľské alebo prevádzkové správanie, ktoré má systém počas definovaného faultu zachovať v prijateľných hraniciach. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Step-up authentication

Vyžiadanie silnejšieho alebo čerstvejšieho authentication eventu pri sensitive action, vyššom risku alebo zmene contextu. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## stickiness — ELB

Load-balancer behavior smerujúci opakované requests alebo flows klienta na rovnaký target počas definovaného obdobia. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## storage autoscaling — RDS

RDS capability automaticky zvýšiť allocated database storage do nastavenej maximálnej hranice pri nedostatku free space podľa service rules. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## Storage fencing

Mechanizmus zabezpečujúci, že starý alebo izolovaný writer už nemôže zapisovať na shared storage pred aktiváciou nového writer-a. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## Storage quota — Kubernetes

ResourceQuota limit agregovaných PVC requests, počtu claims alebo StorageClass-specific storage consumption v namespace. Pozri [ResourceQuota a LimitRange](docs/09-kubernetes/resourcequota-limitrange.md).

## Storage troubleshooting chain

Diagnostické poradie PVC → StorageClass/provisioner → PV binding → scheduling topology → VolumeAttachment → CSI node mount → application I/O. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Storage version — Kubernetes

Interná API verzia, v ktorej API server persistuje konkrétny resource type, pričom externé clients môžu používať iné podporované versions s conversion. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## StorageClass

Cluster-scoped Kubernetes policy object definujúci provisioner, parameters, reclaim policy, binding mode, expansion a topology defaults pre dynamicky provisioned volumes. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## `strace`

Nástroj na sledovanie system calls, ich výsledkov a trvania. Pozri [Performance a troubleshooting](docs/01-linux-and-systems/performance-and-troubleshooting.md).

## Strategy plugin — Ansible

Plugin určujúci, ako Ansible plánuje postup hosts cez tasks a synchronization body počas play executionu. Pozri [Ansible architecture](docs/07-infrastructure-as-code-and-configuration-management/ansible-architecture.md).

## Stream churn

Rýchle vytváranie a zánik log streams, často spôsobené ephemeral alebo dynamic label hodnotami. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Stream selector — LogQL

Label matcher expression, ktorá vyberie Loki log streamy pred line filteringom a parsingom. Pozri [Loki](docs/12-observability/loki.md).

## Stress test

Performance test nad plánovanou kapacitou zameraný na failure mode, ochranné mechanizmy a recovery. Pozri [Performance, load a stress tests](docs/04-testing-and-quality/performance-load-stress-tests.md).

## STRIDE

Threat categorization mnemonic pre Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service a Elevation of Privilege. Pozri [Threat modeling](docs/13-security-and-identity/threat-modeling.md).

## Structured helper output — Helm

Textový output named template-u, ktorý reprezentuje YAML/JSON object a caller ho môže parsovať cez `fromYaml` alebo `fromJson`; ide o serialize/parse contract, nie natívny typed return. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Structured log

Log record so stabilnými typed fields a schema namiesto závislosti na parsovaní voľného textu. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Structured metadata — Loki

Per-entry key/value metadata uložené bez vytvorenia novej stream identity, vhodné pre high-cardinality correlation fields. Pozri [Loki](docs/12-observability/loki.md).

## Structured policy decision

Policy result obsahujúci okrem allow/deny aj reason, policy IDs, revision, violations alebo obligations v machine-readable forme. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Stub — test double

Kontrolovaná náhrada dependency vracajúca vopred pripravené odpovede pre riadenie testovacieho scenára. Pozri [Mocks, stubs a fakes](docs/04-testing-and-quality/mocks-stubs-fakes.md).

## Subgroup — GitLab

Group vnorená v parent group, používaná na delegovanie ownershipu, členstva a policy pre podmnožinu projects. Pozri [Projects, groups a permissions](docs/06-gitlab/projects-groups-permissions.md).

## Subject

Entita, ktorá iniciuje operation alebo pristupuje k resource-u a je reprezentovaná principalom v security context-e. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Subject identifier — OIDC

Hodnota `sub`, ktorá spolu s issuerom stabilne identifikuje End-Usera v OIDC trust doméne. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md).

## `subject` — OCI manifest

OCI descriptor viažuci artifact manifest na iný manifest digest, ktorý predstavuje jeho subject. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## SubjectAccessReview

Kubernetes authorization API request zisťujúci, či konkrétna identita smie vykonať zadanú akciu nad resource-om alebo URL. Pozri [RBAC](docs/09-kubernetes/rbac.md).

## SubjectConfirmation — SAML

SAML element určujúci spôsob, recipienta, request binding a časové podmienky, za ktorých možno assertion použiť. Pozri [SAML](docs/13-security-and-identity/saml.md).

## Subnet

Časť IP address space definovaná prefixom a použitá ako logická routing alebo topology jednotka. Pozri [IPv4, IPv6 a subnetting](docs/02-networking-and-web/ipv4-ipv6-subnetting.md).

## `subPath` update limitation

Kubernetes volume-mount hranica, pri ktorej ConfigMap alebo Secret pripojený cez `subPath` typicky nedostáva priebežné projection updates. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Subresource — Kubernetes

Samostatný API endpoint pre vybranú časť alebo operáciu resource-u, napríklad `/status`, `/scale`, `/log`, `/exec` alebo `/eviction`. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Subshell

Oddelený shell execution context, ktorého zmeny premenných a working directory sa nemusia preniesť späť do parent shellu. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md).

## Successful latency

Latency operácií, ktoré splnili success contract, sledovaná oddelene od rýchlych alebo pomalých failures. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Supplier due diligence

Risk-based overovanie identity, procesov, controls, evidence, maintenance, incident response a transitive dependencies software supplier-a. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Support boundary — cloud

Hranica určujúca, ktorú časť incidentu môže meniť alebo diagnostikovať provider, zákazník alebo third party a aké evidence sú potrebné na efektívnu eskaláciu. Pozri [Shared responsibility model](docs/11-cloud-and-aws/shared-responsibility-model.md).

## Supported version policy

Pravidlá určujúce, ktoré release lines dostávajú opravy, security updates a podporu a kedy dosiahnu end of life. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Suspended Job

Job s pozastaveným execution lifecycle, ktorý nevytvára novú prácu a po resume pokračuje z persisted Job statusu, nie z memory state-u ukončeného procesu. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Sustainability pillar

Well-Architected pillar zameraný na minimalizovanie environmentálneho dopadu workloadu cez demand, utilization, software, data a hardware efficiency. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## SVID

SPIFFE Verifiable Identity Document nesúci SPIFFE ID ako X.509 certificate alebo JWT token. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Swap

Storage-backed priestor pre niektoré anonymné memory pages. Pozri [Memory a CPU fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## Symbolic link

Filesystem objekt obsahujúci textovú cestu na iný objekt. Pozri [Filesystem hierarchy, inodes a links](docs/01-linux-and-systems/filesystem-hierarchy-inodes-links.md).

## Symptom alert

Alert založený na user alebo business impacte namiesto jednej možnej technickej príčiny. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Synthetic alert

Kontrolovaný testovací alert používaný na overenie rule evaluation, routing, receiver delivery a acknowledgement path. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Synthetic merge commit

Dočasný commit reprezentujúci výsledok zlúčenia source branch so súčasným target branch, používaný na testovanie budúceho mainline stavu. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## Synthetic monitoring

Externý opakovaný test user-facing request pathu cez DNS, load balancer, routing a application, odlišný od kubelet-local container probes. Pozri [Probes](docs/09-kubernetes/probes.md).

## Synthetic test data

Umelo generované testovacie dáta bez priameho kopírovania reálnych osobných alebo citlivých záznamov. Pozri [Flaky tests a test data](docs/04-testing-and-quality/flaky-tests-and-test-data.md).

## system call

Kontrolovaný prechod z user space do kernel space. Pozri [Kernel a user space](docs/01-linux-and-systems/kernel-and-user-space.md).

## systemd timer

`.timer` unit aktivujúca inú unit podľa calendar alebo monotonic pravidla. Pozri [Cron a systemd timers](docs/01-linux-and-systems/cron-and-systemd-timers.md).

## systemd unit

Deklaratívny objekt spravovaný systemd, napríklad `.service`, `.socket` alebo `.timer`. Pozri [systemd, services a daemons](docs/01-linux-and-systems/systemd-services-daemons.md).

## Systems Manager rate controls

Concurrency a error-threshold nastavenia obmedzujúce paralelný rollout command alebo automation operácie a zastavujúce ďalšie targets po failure prahu. Pozri [Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## SYSVOL

AD DS replicated share obsahujúci Group Policy template data a domain logon scripts. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## T-shaped engineer

Inžinier so širokou orientáciou a hlbokou expertízou aspoň v jednej oblasti. Pozri [T-shaped engineer](docs/00-foundations/t-shaped-engineer.md).

## Tabletop exercise

Simulované incident alebo disaster-recovery cvičenie bez technického fault injection, ktoré overuje rozhodovanie, prístupy, runbooky, komunikáciu a ownership. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Tag — Git tag

Ref používaný typicky na stabilné označenie konkrétneho release commitu alebo iného objektu. Pozri [Commit, branch, tag a HEAD](docs/03-git-and-automation/commit-branch-tag-head.md).

## Tail input — Fluent Bit

Input plugin sledujúci log files, ich offsets a rotation lifecycle. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Tail latency

Latency najpomalšej časti request distribution, typicky sledovaná cez vyššie percentiles alebo threshold compliance. Pozri [RED method](docs/12-observability/red-method.md).

## Tail sampling

Trace sampling decision vykonané po zhromaždení väčšej časti trace-u, aby bolo možné zachovať errors, high-latency alebo inak zaujímavé traces. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Tail sampling — OpenTelemetry

Sampling decision vykonané po zhromaždení väčšej časti trace-u, typicky v stateful Collector pipeline. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Taint analysis

Statická analýza sledujúca nedôveryhodné dáta od source cez transformácie po citlivý sink. Pozri [Static analysis, linting a type checking](docs/04-testing-and-quality/static-analysis-linting-type-checking.md).

## Taint — Kubernetes

Key/value/effect značka na Node-e, ktorá odpudzuje Pody bez matching toleration pri scheduling-u alebo execution-e. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## target group — ELB

Backend registration, protocol, port, health-check a traffic-lifecycle contract medzi load balancerom a jednou alebo viacerými targets. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## target health — ELB

Per-target-group stav vyjadrujúci, či registrovaný target prešiel health checks a je vhodný na routing trafficu. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## Target — Prometheus

Network endpoint a associated labels, ktorý Prometheus plánuje pravidelne scrape-ovať. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Target relabeling

Prometheus relabeling fáza pred scrape-nutím, ktorá filtruje targets a mapuje discovery metadata na address, path, scheme a stabilné target labels. Pozri [Prometheus](docs/12-observability/prometheus.md).

## target tracking — Auto Scaling

Dynamic scaling policy snažiaca sa udržať zvolenú metric približne na target hodnote zmenou desired capacity. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## `targetPort` — Service

Port alebo pomenovaný Pod container port, na ktorý Service dataplane smeruje traffic z publikovaného Service `port`. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## Task intake protocol — CKA

Krátky parsing úlohy na cluster/context, namespace, resource identity, požadovanú zmenu, constraints a validation criterion pred vykonaním commandov. Pozri [CKA timed labs](docs/10-helm-and-cka/cka-timed-labs.md).

## Task-oriented automation

Automation model skladajúci ordered tasks, conditions a orchestration controls nad targets namiesto univerzálneho persistentného resource graphu. Pozri [Terraform vs. Ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md).

## TCP connection

Transportný byte stream identifikovaný source/destination IP adresami a portmi. Pozri [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md).

## TCP handshake

Výmena SYN, SYN-ACK a ACK, ktorá synchronizuje sequence numbers a vytvorí TCP connection state. Pozri [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md).

## TCP/IP model

Praktický vrstvený model Application, Transport, Internet a Link používaný na opis Internet stacku. Pozri [OSI a TCP/IP model](docs/02-networking-and-web/osi-and-tcp-ip-model.md).

## TCP probe

Kubernetes probe overujúca úspešné otvorenie TCP connectionu na Pod IP a port bez overenia application protocol response alebo business correctness. Pozri [Probes](docs/09-kubernetes/probes.md).

## Telemetry

Dáta generované systémom o jeho stave a správaní, napríklad metrics, logs, traces, events, profiles a audit records. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Telemetry backpressure

Stav, keď downstream receiver alebo backend nestíha prijímať telemetry a producers alebo collectors musia bufferovať, retryovať, dropovať alebo obmedziť tok. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Telemetry batching

Zoskupovanie viacerých telemetry records pred exportom na zníženie overheadu za cenu vyššej latency a väčšieho loss windowu. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Telemetry contract test

Automatizovaný test overujúci names, units, attributes, resources, correlation, cardinality a compatibility telemetry po zmene instrumentation alebo pipeline. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Telemetry fan-out

Odosielanie rovnakého prijatého signalu do viacerých processing pipelines alebo backendov s odlišnými retention, security alebo analytics účelmi. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Telemetry pipeline

Reťazec instrumentation sources, agents alebo collectors, processingu, exportu, storage a query vrstiev, ktorými telemetry prechádza. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Telemetry retention

Čas a storage policy pre logs, metrics, Events, traces a audit records odvodená od incident, compliance, forensic a cost požiadaviek. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Telemetry self-observability

Monitoring samotného telemetry pipeline cez accepted, queued, dropped, retried a failed records spolu s resource usage a ingestion lagom. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Telemetry tragedy of the commons

Stav shared observability platformy, v ktorom jednotliví producenti pridávajú drahú telemetry bez vlastného cost feedbacku a spoločne vyčerpajú kapacitu alebo budget. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Template contract — CI/CD

Versionované pravidlá reusable template definujúce inputs, defaults, outputs, artifacts, permissions, supported scenarios, failure semantics a compatibility policy. Pozri [Reusable a parallel pipelines](docs/05-ci-cd-and-release/reusable-and-parallel-pipelines.md).

## `template` — Helm

Go template action vkladajúca named template inline; na rozdiel od `include` neposkytuje output ako pipeline string. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Template validation — Ansible

Kontrola renderovaného dočasného file-u pomocou target parsera alebo validatora pred jeho nahradením na destination path. Pozri [Variables, facts a templates](docs/07-infrastructure-as-code-and-configuration-management/variables-facts-templates.md).

## Tempo

Object-storage-oriented distributed tracing backend s TraceQL, Grafana integráciou a oddeleným write/read lifecycle-om. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Tempo distributor

Write-path component prijímajúci trace data, validujúci limits a sharding records podľa trace ID. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Tempo live store

Read-path component poskytujúci recent trace data pred alebo nezávisle od ich historical object-storage availability. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Temporality — metric

Semantics určujúca, či metric export reprezentuje cumulative hodnotu od začiatku alebo delta zmenu za konkrétny interval. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Temporary credentials — AWS

Časovo obmedzená sada access key ID, secret access key a session tokenu vydaná AWS STS pre role alebo federated session. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## Tenant ID — Loki

Identifier oddeľujúci ingestion, storage, query a limits jednotlivých Loki tenantov. Pozri [Loki](docs/12-observability/loki.md).

## Terminating error — PowerShell

PowerShell error, ktorý zastaví aktuálnu operáciu alebo scope a môže byť zachytený cez `try/catch`. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## Terraform backend

Terraform Core komponent určujúci state storage a podľa backendu aj locking, workspaces alebo remote execution behavior. Pozri [Remote backend a state locking](docs/07-infrastructure-as-code-and-configuration-management/remote-backend-and-state-locking.md).

## Terraform drift

Významný rozdiel medzi desired configuration, Terraform state a skutočným remote stavom, ktorý vyžaduje klasifikáciu ownershipu a vedomé reconciliation rozhodnutie. Pozri [Drift](docs/07-infrastructure-as-code-and-configuration-management/drift.md).

## Terraform import

Proces vytvorenia state bindingu medzi existujúcim remote objektom a deklarovanou Terraform resource addressou bez vytvorenia objektu Terraformom. Pozri [Lifecycle, import a moved blocks](docs/07-infrastructure-as-code-and-configuration-management/lifecycle-import-moved-blocks.md).

## Terraform input variable

Deklarovaný vstup modulu dostupný cez `var.<name>` s type constraintom, defaultom, validation a ďalšími contract vlastnosťami. Pozri [Variables, locals a outputs](docs/07-infrastructure-as-code-and-configuration-management/variables-locals-outputs.md).

## Terraform provider

Samostatne versionovaný plugin implementujúci resource types, data sources, schemas a API operácie pre konkrétnu platformu alebo službu. Pozri [Terraform providers, resources a data sources](docs/07-infrastructure-as-code-and-configuration-management/terraform-providers-resources-data-sources.md).

## Terraform state

Persistentný model mapujúci Terraform resource addresses na remote identities a uchovávajúci metadata potrebné na ďalší plan/apply lifecycle. Pozri [Terraform state](docs/07-infrastructure-as-code-and-configuration-management/terraform-state.md).

## Terraform test

Native Terraform test execution definovaná v `.tftest.hcl` alebo `.tftest.json`, ktorá vykonáva plan/apply runs a assertions pre root alebo reusable module. Pozri [Terraform testing a policy](docs/07-infrastructure-as-code-and-configuration-management/terraform-testing-and-policy.md).

## Terraform test file

Súbor testovacej konfigurácie načítaný Terraformom z root configuration alebo štandardne z adresára `tests`, obsahujúci runs, variables, providers, overrides a assertions. Pozri [Terraform testing a policy](docs/07-infrastructure-as-code-and-configuration-management/terraform-testing-and-policy.md).

## Test data factory

Programový builder vytvárajúci minimálne validné testovacie objekty so stabilnými defaults a explicitnými overrides. Pozri [Flaky tests a test data](docs/04-testing-and-quality/flaky-tests-and-test-data.md).

## Test double

Kontrolovaná náhrada dependency používaná v teste; zahŕňa dummy, stub, fake, spy a mock. Pozri [Mocks, stubs a fakes](docs/04-testing-and-quality/mocks-stubs-fakes.md).

## Test fidelity

Miera, do akej test zachováva produkčne relevantné komponenty, protokoly, konfiguráciu a failure modes. Pozri [Test pyramid](docs/04-testing-and-quality/test-pyramid.md).

## Test hook — Helm

Hook resource označený hodnotou `test`, ktorý sa vykoná cez `helm test` a má overiť release-specific invariant s explicitným exit statusom. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Test isolation

Vlastnosť testu, pri ktorej jeho výsledok nezávisí od poradia, paralelných testov ani zdieľaného mutable state. Pozri [Flaky tests a test data](docs/04-testing-and-quality/flaky-tests-and-test-data.md).

## Test oracle

Mechanizmus alebo pravidlo rozhodujúce, či je pozorovaný test result správny. Pozri [Verification vs. validation](docs/04-testing-and-quality/verification-vs-validation.md).

## Test pyramid

Model test portfolio s veľkou vrstvou rýchlych úzkych kontrol, menšou integračnou vrstvou a obmedzeným počtom drahých E2E testov. Pozri [Test pyramid](docs/04-testing-and-quality/test-pyramid.md).

## Test sharding

Rozdelenie test suite medzi paralelné jobs podľa súborov, test IDs alebo historical duration s následnou validáciou úplnosti a agregáciou reportov. Pozri [Reusable a parallel pipelines](docs/05-ci-cd-and-release/reusable-and-parallel-pipelines.md).

## Test stage — Dockerfile

Multi-stage build target určený na vykonanie testov; ak nie je v dependency graph-e final targetu, pipeline ho musí explicitne buildnúť ako quality evidence. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## Test trophy

Alternatívny model zvýrazňujúci static checks a integration tests ako hlavný zdroj hodnoty, s menšou unit a E2E vrstvou. Pozri [Test pyramid](docs/04-testing-and-quality/test-pyramid.md).

## `text` field

Search field type analyzovaný pre full-text search a relevance, nie primárne pre exact aggregations. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Thread

Plánovateľná vykonávacia jednotka v rámci procesu. Pozri [Procesy, thready, PID a signals](docs/01-linux-and-systems/processes-threads-pid-signals.md).

## Threat

Potenciálna príčina neželaného bezpečnostného incidentu, napríklad attacker, insider, human error alebo infrastructure failure. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Threat model

Štruktúrovaný opis assets, trust boundaries, aktérov, attack surfaces, abuse cases a mitigations. Pozri [Security a infrastructure tests](docs/04-testing-and-quality/security-and-infrastructure-tests.md).

## Threat modeling

Systematický proces modelovania assets, actors, architecture, trust boundaries, threats, mitigations, verification a residual risk pred incidentom. Pozri [Threat modeling](docs/13-security-and-identity/threat-modeling.md).

## Threat statement

Štruktúrovaný opis toho, ako konkrétny actor cez attack condition alebo trust boundary spôsobí security impact na assete. Pozri [Threat modeling](docs/13-security-and-identity/threat-modeling.md).

## Throughput

Množstvo práce dokončenej za jednotku času. Pozri [Performance a troubleshooting](docs/01-linux-and-systems/performance-and-troubleshooting.md).

## throughput mode — EFS

EFS configuration určujúca, ako filesystem získava a účtuje dostupný aggregate throughput, napríklad Bursting, Provisioned alebo Elastic. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Ticket-Granting Service — Kerberos TGS

Časť KDC, ktorá na základe validného TGT vydáva service tickets pre požadované service principals. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Ticket-Granting Ticket — TGT

Kerberos ticket používaný clientom na získavanie service tickets bez opakovaného zadávania passwordu. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Time-series cardinality

Počet unikátnych kombinácií metric label values; nekontrolované dynamické labels výrazne zvyšujú memory, storage a query náklady. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Time series — Prometheus

Prúd timestampovaných samples identifikovaný metric name a úplným label setom. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Time to first feedback

Čas od vzniku alebo odoslania zmeny po prvý relevantný a diagnostikovateľný výsledok pipeline. Pozri [Continuous Integration](docs/05-ci-cd-and-release/continuous-integration.md).

## `TIME-WAIT`

TCP state držaný po aktívnom close na ochranu pred starými segments a opätovným použitím rovnakého tuple. Pozri [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md).

## Timed lab — CKA

Praktický Kubernetes lab vykonávaný s pevným časovým limitom, bodovaním a povinnou validáciou na tréning exam execution schopností. Pozri [CKA timed labs](docs/10-helm-and-cka/cka-timed-labs.md).

## TLS Secret

Kubernetes Secret typu `kubernetes.io/tls`, typicky obsahujúci `tls.crt` a `tls.key` pre controller alebo workload; celý certificate trust a rotation contract zostáva zodpovednosťou consumer workflowu. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## TLS termination

Bod, v ktorom proxy, load balancer alebo gateway ukončí TLS a sprístupní plaintext; vytvára novú trust boundary pre ďalší hop, identity propagation a certificate lifecycle. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## TLS — Transport Layer Security

Protokol poskytujúci šifrovanie, integritu a autentifikáciu komunikácie. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## tmpfs mount — container

Memory-backed temporary filesystem pripojený do containeru s lifecycle viazaným na runtime a potrebným explicitným size, memory a permissions limitom. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## tmpfs mount — Docker

Memory-backed runtime filesystem mount s ephemeral lifecycle, vhodný pre dočasné dáta alebo secrets podľa memory, swap a forensic threat modelu. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## Toil

Manuálna, opakujúca sa, automatizovateľná a nízko hodnotná prevádzková práca. Pozri [Toil and Technical Debt](docs/00-foundations/toil-and-technical-debt.md).

## Token endpoint

OAuth endpoint, ktorý vymieňa authorization grant alebo refresh token za access token. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Token exchange

OAuth extension na výmenu subject alebo actor tokenu za nový token s vhodným audience, scope a delegation contextom. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Token introspection

OAuth endpoint umožňujúci resource serveru zistiť active stav a metadata opaque alebo centrally validated tokenu. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Token revocation

OAuth mechanizmus na zneplatnenie tokenu alebo grant lifecycle-u. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## TokenRequest

Kubernetes API subresource/mechanizmus na vydanie krátkodobého ServiceAccount tokenu s audience a expiration namiesto statického long-lived token Secretu. Pozri [ServiceAccount](docs/09-kubernetes/serviceaccount.md).

## Toleration — Kubernetes

Pod rule povoľujúci workloadu tolerovať konkrétny Node taint; nepriťahuje Pod na tainted Node. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## `tolerationSeconds`

Čas, počas ktorého Pod toleruje matching `NoExecute` taint pred možnou eviction. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Topology-aware routing — Service

Service routing model využívajúci EndpointSlice zone/topology metadata na preferenciu bližších endpointov pri zachovaní dostupnosti a správnej capacity distribution. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## Topology domain — Kubernetes

Množina Nodes zdieľajúcich rovnakú hodnotu vybraného topology labelu, napríklad Node, zone, region alebo rack. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Topology spread constraint

Pod scheduling pravidlo riadiace maximálnu nerovnomernosť matching Pod population medzi topology domains. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Total cost of ownership — cloud

Celkové náklady služby zahŕňajúce provider bill, engineering a operations prácu, support, compliance, migration, egress, downtime risk a opportunity cost. Pozri [IaaS, PaaS a SaaS](docs/11-cloud-and-aws/iaas-paas-saas.md).

## Total cost of ownership — TCO

Celkový ekonomický cost zahŕňajúci cloud spend, engineering, operations, licensing, support, migration a risk. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## `toYaml` — Helm

Template function serializujúca hodnotu do YAML textu, ktorý musí byť vložený s korektným indentation contractom. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## `tpl` — Helm

Function vyhodnocujúca string ako Helm template v odovzdanom scope-e; rozširuje input trust boundary a môže znížiť deterministickosť renderu. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Trace affinity

Routing vlastnosť zabezpečujúca, že spans rovnakého trace-u dorazia na rovnakú stateful processing identity, napríklad tail sampler. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Trace attribute governance

Policy určujúca povolené, bounded, sensitive a searchable span attributes spolu s retention a sampling použitím. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Trace completeness

Miera, do akej backend obsahuje všetky relevantné spans a relationships konkrétneho trace-u; ovplyvňuje ju propagation, sampling, export a storage loss. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Trace-to-logs

Correlation workflow, ktorý z trace ID, span ID, service a času vytvorí query do log backendu. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## TraceQL

Tempo query language na trace a span search podľa attributes, duration, status a structural conditions. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Traffic cutover

Riadené presmerovanie nových requestov alebo connections zo starej deployment farby na novú. Pozri [Blue-green deployment](docs/05-ci-cd-and-release/blue-green-deployment.md).

## Traffic mirroring

Kopírovanie produkčných requestov do shadow systému bez použitia jeho response na primary request path. Pozri [Shadow deployment](docs/05-ci-cd-and-release/shadow-deployment.md).

## Traffic splitting — Gateway API

Rozdelenie Route trafficu medzi viac backendRefs podľa weights, používané napríklad pre canary alebo migration rollout. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## Transformation — Grafana

Operácia aplikovaná na query results po ich získaní z data source-u na úpravu data frame-u pred vizualizáciou. Pozri [Grafana](docs/12-observability/grafana.md).

## Transit Gateway — AWS

Regionálny network transit hub prepájajúci viac VPCs a hybrid networks cez attachments, associations, propagations a vlastné route tables. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## Transit secrets engine — Vault

Vault engine poskytujúci encryption, decryption, signing alebo HMAC operations bez vydania underlying key materialu clientovi. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Transitive chart dependency — Helm

Dependency, ktorú parent chart získava nepriamo cez dependency vlastného subchartu; rozširuje render, hook, RBAC a supply-chain surface celého release-u. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Translog

Elasticsearch/OpenSearch transaction-log mechanism používaný pri write durability a shard recovery podľa konkrétnej konfigurácie a produktu. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Trap — shell

Shell handler spustený pri definovanom signále alebo pseudo-signále ako `EXIT` či `ERR`. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md).

## Treatment variant

Experimentálny variant obsahujúci testovanú zmenu, ktorého outcome sa porovnáva s control variantom. Pozri [A/B testing](docs/05-ci-cd-and-release/a-b-testing.md).

## Trigger — CI/CD

Udalosť alebo explicitný pokyn, ktorý vytvorí pipeline run a určí jeho commit, event payload, actor identity, variables a permission context. Pozri [Trigger, artifact a cache](docs/05-ci-cd-and-release/trigger-artifact-cache.md).

## Trunk-based development

Branching model založený na častej integrácii malých zmien do jednej hlavnej branch, podporený krátkodobými branches, CI a feature flags. Pozri [Branching strategies](docs/03-git-and-automation/branching-strategies.md).

## Trust boundary

Miesto, kde sa mení úroveň dôvery, identity authority, administrative control, tenant, privilege alebo data-protection assumption. Pozri [Threat modeling](docs/13-security-and-identity/threat-modeling.md).

## Trust domain — SPIFFE

SPIFFE administrative a security boundary určujúca namespace workload identities a trust bundle pre ich verification. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## TSDB index store — Loki

Odporúčaný Loki index format ukladajúci TSDB index blocks v object storage popri chunks. Pozri [Loki](docs/12-observability/loki.md).

## TTL-after-finished

Controller mechanizmus odstraňujúci dokončený alebo failed Job a jeho dependent resources po uplynutí `ttlSecondsAfterFinished`. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## TTL — Time To Live

IPv4 field znižovaný na každom router hop-e; pri nule sa packet zahodí. Pozri [IPv4, IPv6 a subnetting](docs/02-networking-and-web/ipv4-ipv6-subnetting.md).

## TUF — The Update Framework

Framework pre secure software updates používajúci role separation, threshold signatures, metadata expiration a rollback, freeze a mix-and-match ochrany. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Type checking

Statická kontrola konzistencie typových kontraktov a operácií. Nenahrádza runtime validáciu nedôveryhodných vstupov. Pozri [Static analysis, linting a type checking](docs/04-testing-and-quality/static-analysis-linting-type-checking.md).

## Type enforcement

SELinux policy model založený na source type, target type, object class a permissions. Pozri [SELinux a AppArmor](docs/01-linux-and-systems/selinux-and-apparmor.md).

## Type hint — Python

Anotácia očakávaného typu používaná static analysis nástrojmi a IDE; sama osebe nie je runtime validáciou. Pozri [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Typosquatting — package

Publikovanie malicious alebo deceptive package-u s názvom podobným legitimate dependency s cieľom využiť chybu používateľa alebo automatizácie. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## UAT — User Acceptance Testing

Acceptance activity vykonaná alebo schválená reprezentatívnym business používateľom či stakeholderom na overenie fitu s reálnym procesom. Pozri [End-to-end a acceptance tests](docs/04-testing-and-quality/end-to-end-and-acceptance-tests.md).

## UDP datagram

Samostatná transportná správa bez zabudovanej garancie doručenia, poradia alebo retransmission. Pozri [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md).

## Unblended cost — AWS

Cost view zobrazujúci konkrétnu rate účtovanú za jednotlivé usage line items bez organization average. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Unbounded dimension

Telemetry dimension s nekontrolovaným alebo prakticky neobmedzeným počtom hodnôt, napríklad request ID, trace ID alebo user ID. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Undefined policy decision

Stav, keď policy query nevytvorí result; consumer musí explicitne určiť, či znamená deny, error alebo not applicable. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Unit cost

Cloud cost prepočítaný na business jednotku, napríklad request, transakciu, build alebo aktívneho používateľa. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Unit test

Rýchly test malej izolovanej jednotky správania s úzkym diagnostickým scope-om. Pozri [Unit, integration a component tests](docs/04-testing-and-quality/unit-integration-component-tests.md).

## Universal group — AD DS

AD DS group scope, ktorý môže obsahovať principals z viacerých domains vo forest-e a je replikovaný cez Global Catalog podľa platform semantics. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Unknown value — Terraform

Typovo známa, ale konkrétne neurčená hodnota počas planu, ktorú Terraform získa až pri apply alebo neskoršom provider read-e. Pozri [Expressions a dependency graph](docs/07-infrastructure-as-code-and-configuration-management/expressions-and-dependency-graph.md).

## Unmanaged infrastructure — Terraform context

Remote objekt bez bindingu v danom Terraform state-e, ktorý bežný plan nemusí objaviť, pokiaľ ho explicitne nenačíta provider data source, import alebo externý asset inventory. Pozri [Drift](docs/07-infrastructure-as-code-and-configuration-management/drift.md).

## Unseal — Vault

Proces sprístupnenia root-key materialu potrebného na odomknutie Vault encryption barrieru. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Unsupported cluster version

Kubernetes minor verzia mimo upstream alebo provider support window, pre ktorú nemusia byť dostupné security fixes, compatibility garancie ani support. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## `unwrap` — LogQL

LogQL operation premieňajúca parsed numerický field log entry na sample hodnotu pre range aggregation. Pozri [Loki](docs/12-observability/loki.md).

## Updated replicas — Deployment

Počet Deployment replík bežiacich z aktuálnej Pod template revision. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## Upgrade abort criterion — Kubernetes

Vopred definovaná SLO, error-rate, control-plane alebo dataplane podmienka, pri ktorej sa upgrade zastaví a aktivuje recovery plán. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Upgrade health gate — Helm

Súbor pre-upgrade a post-upgrade podmienok nad clusterom, workloadom, dependencies, capacity, backups a observability, ktoré musia byť splnené pred pokračovaním release-u. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Upgrade health gate — Kubernetes

Pre-upgrade kontrola API, etcd, Nodes, add-ons, certificates, capacity a backup stavu zabraňujúca upgradu už degraded clusteru. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## `upgrade --install` — Helm

Helm deployment pattern, ktorý vytvorí release, ak neexistuje, alebo aktualizuje existujúcu release; nerieši automaticky concurrency, migrations, drift ani secret management. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Upgrade test — Terraform module

Testovací workflow, ktorý vytvorí infraštruktúru podporovanou staršou module/provider verziou, následne vykoná upgrade plan/apply a overí compatibility, moved mappings a absence nečakaných replacements. Pozri [Terraform testing a policy](docs/07-infrastructure-as-code-and-configuration-management/terraform-testing-and-policy.md).

## Upstream branch

Remote-tracking alebo iný ref priradený lokálnej branch ako default comparison a synchronization target pre status, pull a push. Pozri [Clone, fetch, pull a push](docs/03-git-and-automation/clone-fetch-pull-push.md).

## URI — Uniform Resource Identifier

Identifikátor resource; URL je typ URI, ktorý zároveň opisuje spôsob alebo miesto prístupu. Pozri [HTTP](docs/02-networking-and-web/http.md).

## USE method

Resource-oriented performance metodika, ktorá pre každý resource preveruje Utilization, Saturation a Errors. Pozri [USE method](docs/12-observability/use-method.md).

## User-defined bridge — Docker

Explicitne vytvorená single-host bridge network poskytujúca vlastnú lifecycle identity, embedded DNS, aliases a isolation boundary pre pripojené containers. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## User namespace

Namespace izolujúci UID/GID mapping a capability scope. Pozri [Namespaces](docs/01-linux-and-systems/namespaces.md).

## User space

Menej privilegované prostredie, v ktorom bežia aplikácie a systémové procesy. Pozri [Kernel a user space](docs/01-linux-and-systems/kernel-and-user-space.md).

## UserInfo endpoint

OIDC protected endpoint vracajúci štandardizované claims o subjecte po predložení access tokenu. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md).

## Utilization

Miera použitia dostupnej kapacity resource. Pozri [Performance a troubleshooting](docs/01-linux-and-systems/performance-and-troubleshooting.md).

## Utilization — USE

Miera používania resource-u vyjadrená ako busy time, obsadená kapacita, throughput voči limitu alebo concurrency voči maximu. Pozri [USE method](docs/12-observability/use-method.md).

## Validating admission

Admission fáza, ktorá po relevantnej mutácii a validácii rozhodne, či Kubernetes API request povolí alebo odmietne. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## ValidatingAdmissionPolicy

Stable Kubernetes in-process declarative validation resource používajúci CEL expressions nad admission requestom. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## ValidatingAdmissionPolicyBinding

Kubernetes resource prepájajúci ValidatingAdmissionPolicy s match scope-om, parameters a validation actions. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Validation — testing

Overenie, či systém rieši správny používateľský alebo business problém v reálnom kontexte. Pozri [Verification vs. validation](docs/04-testing-and-quality/verification-vs-validation.md).

## Value stream

Celý tok práce a informácií od potreby po hodnotu doručenú používateľovi. Pozri [Value Stream Mapping](docs/00-foundations/value-stream-mapping.md).

## Values — Helm

Konfiguračné vstupy chart templates získané z default `values.yaml`, override files a command-line overrides. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Values precedence — Helm

Merge a override poradie, v ktorom neskoršie values files a explicitné command-line overrides prepisujú chart defaults a skoršie values. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Values schema — Helm

Voliteľný `values.schema.json` contract validujúci typy, required fields, enums a štruktúru Helm values pred render/install/upgrade. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Values test matrix — Helm

Sada reprezentatívnych values kombinácií vrátane defaults, production variantov, enabled/disabled features a explicitných empty hodnôt používaná na chart render a policy testovanie. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Variable precedence — Ansible

Pravidlá rozhodujúce, ktorá z viacerých definitions rovnakého variable name sa použije podľa source a explicitnosti. Pozri [Variables, facts a templates](docs/07-infrastructure-as-code-and-configuration-management/variables-facts-templates.md).

## Vault audit device

Vault component zaznamenávajúci API requests a responses do file, syslog alebo socket destination a ovplyvňujúci request availability pri úplnom write failure. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Vault auth method

Mechanizmus, ktorý autentizuje human alebo workload identity vo Vault a vydá client token s príslušnými policies. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Vault ID — Ansible

Label priradený k encrypted Vault contentu a password source-u na oddelenie environmentov alebo security domains; sám nie je secret ani access-control mechanizmus. Pozri [Vault](docs/07-infrastructure-as-code-and-configuration-management/vault.md).

## Vault password — Ansible

Secret použitý na šifrovanie a dešifrovanie Ansible Vault contentu, ktorý musí byť uložený oddelene od encrypted repository dát. Pozri [Vault](docs/07-infrastructure-as-code-and-configuration-management/vault.md).

## Vault policy

Path-based authorization pravidlá definujúce capabilities dostupné Vault tokenu alebo identity. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Vault token

Bearer credential vydaný Vaultom s policies, TTL, renewal a revocation lifecycle-om. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Vector matching — PromQL

Pravidlá spájania series pri binary operation podľa labels vrátane `on`, `ignoring`, `group_left` a `group_right`. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Vendored chart — Helm

Dependency chart uložený priamo v parent `charts/` directory ako archive alebo unpacked directory namiesto stiahnutia počas build-u. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Vendored component

External code alebo binary skopírovaný priamo do repository alebo artifactu namiesto štandardnej package-manager dependency. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## Verification bundle — Sigstore

Prenositeľný súbor obsahujúci signature, certificate chain a transparency alebo timestamp evidence potrebnú na neskoršiu verification. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Verification pass — CKA

Vyhradená záverečná časť timed labu, počas ktorej sa všetky úlohy znovu overia cez hard validation a context kontrolu. Pozri [CKA timed labs](docs/10-helm-and-cka/cka-timed-labs.md).

## Verification — testing

Overenie, či systém alebo artifact zodpovedá explicitnej špecifikácii, kontraktu alebo pravidlu. Pozri [Verification vs. validation](docs/04-testing-and-quality/verification-vs-validation.md).

## Version-level telemetry

Metrics, logs a traces označené konkrétnou application alebo artifact verziou, ktoré umožňujú porovnať old a new behavior počas rollout-u. Pozri [Rolling update](docs/05-ci-cd-and-release/rolling-update.md).

## Version precedence

SemVer pravidlá určujúce poradie versions podľa MAJOR, MINOR, PATCH a pre-release identifiers; build metadata sa pri precedence ignorujú. Pozri [Semantic Versioning](docs/05-ci-cd-and-release/semantic-versioning.md).

## Version range

Constraint vyjadrujúci množinu akceptovaných dependency versions, ktorého konkrétna syntax a význam závisia od package ecosystemu. Pozri [Semantic Versioning](docs/05-ci-cd-and-release/semantic-versioning.md).

## Vertical Pod Autoscaler — VPA

Samostatne inštalovaný Kubernetes controller a API odporúčajúci alebo aplikujúci zmeny Pod resource requests podľa observed usage a policy. Pozri [HPA a autoscaling](docs/09-kubernetes/hpa-autoscaling.md).

## Vertical scaling

Zmena kapacity jedného resource-u, napríklad väčšia VM alebo database instance, bez pridania ďalších replicas. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Veth pair

Dvojica prepojených virtual Ethernet interfaces, ktorá typicky spája container network namespace s host bridge alebo routing vrstvou. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## VEX

Vulnerability Exploitability eXchange statement vyjadrujúci affected, not affected, fixed alebo under-investigation status vulnerability voči konkrétnemu productu. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## Virtual environment — Python

Izolované Python prostredie s vlastným interpreter contextom a nainštalovanými packages. Pozri [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Virtual machine — VM

Izolovaný machine environment s virtualizovaným hardware, vlastným guest kernelom a guest userspace, ktorý poskytuje hypervisor. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Virtual memory

Abstrakcia, pri ktorej má proces vlastný virtuálny adresný priestor mapovaný kernelom na RAM, files alebo swap. Pozri [Memory a CPU fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## Virtual patching

Dočasná compensating control vrstva, napríklad WAF alebo IPS rule, ktorá blokuje známy exploit path bez odstránenia underlying vulnerability. Pozri [Vulnerability a patch management](docs/13-security-and-identity/vulnerability-and-patch-management.md).

## Visibility and analytics — Zero Trust

Cross-cutting capability korelujúca identity, device, network, workload, resource a decision telemetry na detekciu risku a bypass paths. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Visualization — Grafana

Prezentačný model panelu, napríklad time series, stat, table, heatmap alebo state timeline, zvolený podľa data shape-u a operational otázky. Pozri [Grafana](docs/12-observability/grafana.md).

## VLAN — Virtual LAN

Logicky oddelený Ethernet broadcast domain, často prenášaný cez 802.1Q tagging. Pozri [Ethernet, MAC a ARP](docs/02-networking-and-web/ethernet-mac-arp.md).

## VM escape

Prelomenie guest/hypervisor isolation boundary, pri ktorom code z virtual machine ovplyvní hypervisor, host alebo inú VM. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Volume binding mode

StorageClass policy určujúca, či sa dynamic volume provision/binding vykoná okamžite alebo sa odloží do scheduling kontextu cez `WaitForFirstConsumer`. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Volume driver — Docker

Plugin alebo built-in implementation určujúca storage backend a mount semantics Docker volume-u; application consistency, backup a access modes zostávajú samostatným contractom. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## volume initialization — EBS

Proces načítania alebo zápisu všetkých blocks volume-u vytvoreného zo snapshotu alebo copy pred dosiahnutím plného stabilného výkonu. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Volume mode — Kubernetes

PVC/PV contract určujúci, či workload dostane filesystem mount alebo raw block device. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Volume projection — Kubernetes configuration

Kubeletom materializované files z ConfigMapu, Secretu, ServiceAccount tokenu alebo ďalších sources v Pod mount namespace. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## VolumeAttachment

Cluster-scoped storage API object reprezentujúci attach požiadavku alebo stav CSI volume-u voči konkrétnemu Node-u. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## `volumeClaimTemplates` — StatefulSet

StatefulSet šablóny, z ktorých controller vytvára samostatné PVCs pre jednotlivé ordinal replicas. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## VPC CNI — EKS

Kubernetes networking plugin integrujúci Pod networking s Amazon VPC ENIs a IP addressingom; jeho IPAM a subnet capacity ovplyvňujú Pod scheduling. Pozri [ECS a EKS](docs/11-cloud-and-aws/ecs-eks.md).

## VPC Flow Logs

AWS telemetry zachytávajúca metadata IP flows pre VPC, subnet alebo ENI scope a podporujúca network path a accept/reject analýzu bez application payloadu. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## VPC peering

Private non-transitive routing connection medzi dvoma VPCs s explicitnými routes, non-overlapping CIDRs a security/DNS konfiguráciou na oboch stranách. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## VSZ — Virtual Set Size

Veľkosť virtuálneho adresného priestoru procesu. Pozri [Memory a CPU fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## Vulnerability

Slabina v systéme, konfigurácii, procese alebo control-e, ktorú môže threat využiť. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Vulnerability debt

Akumulovaný backlog neodstránených vulnerabilities a zastaraných components, ktorý zvyšuje attack surface, operational complexity a budúce remediation náklady. Pozri [Vulnerability a patch management](docs/13-security-and-identity/vulnerability-and-patch-management.md).

## Vulnerability reachability

Posúdenie, či je zraniteľný component a code path skutočne prítomný, dostupný a využiteľný v konkrétnom runtime kontexte. Pozri [Security a infrastructure tests](docs/04-testing-and-quality/security-and-infrastructure-tests.md).

## Vulnerability record — GitLab

Dlhodobejšie spravovaný security objekt odvodený zo scan findingu, ktorý má status, severity, location, identifiers, triage a remediation lifecycle. Pozri [Security scanning](docs/06-gitlab/security-scanning.md).

## W3C Trace Context

Štandardný propagation format používajúci najmä `traceparent` a `tracestate` na prenos distributed trace contextu. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## WAF — Web Application Firewall

L7 security control vyhodnocujúci HTTP requests podľa aplikačných pravidiel; nie je totožný s L3/L4 firewallom. Pozri [Firewally](docs/02-networking-and-web/firewalls.md).

## `WaitForFirstConsumer`

StorageClass binding mode odkladajúci provisioning alebo PV binding, kým scheduler pozná Pod placement constraints a vie koordinovať storage topology s vybraným Node-om. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## WAL — Prometheus

Write-Ahead Log uchovávajúci nedávne ingested samples a metadata pre recovery aktívneho TSDB head state-u po reštarte. Pozri [Prometheus](docs/12-observability/prometheus.md).

## warm pool — Auto Scaling

Pool predinicializovaných EC2 instances mimo aktívnej `InService` capacity používaný na skrátenie scale-out startup latency. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Warm standby — blue-green

Pôvodná deployment farba ponechaná po cutover-e v pripravenom a priebežne health-checkovanom stave pre rýchly routing rollback. Pozri [Blue-green deployment](docs/05-ci-cd-and-release/blue-green-deployment.md).

## Warm standby — DR

Recovery stratégia s priebežne bežiacou zmenšenou, ale funkčnou kópiou workloadu v náhradnej lokalite, ktorá sa pri incidente rozšíri a prevezme traffic. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Warm start — Lambda

Invocation v už existujúcom Lambda execution environment, ktorý môže reuse-nuť initialized code, connections a temporary files bez garancie ďalšieho reuse. Pozri [Lambda](docs/11-cloud-and-aws/lambda.md).

## Wavelength Zone — AWS

Špecializovaná AWS edge zóna integrovaná do telekomunikačnej 5G siete pre veľmi nízkolatenčné workloady a obmedzený service katalóg. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## WebSocket

Protokol poskytujúci dlhodobý full-duplex message channel po HTTP upgrade alebo ekvivalentnom transportnom mechanizme. Pozri [REST APIs a WebSockets](docs/02-networking-and-web/rest-apis-and-websockets.md).

## weighted forwarding — ALB

ALB listener action rozdeľujúca traffic medzi viac target groups podľa relatívnych weights, často používaná pri canary alebo migration workflowe. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## weighted routing — Route 53

DNS routing policy rozdeľujúca odpovede medzi records podľa relatívnych weights, bez presnej request-level percentuálnej garancie kvôli DNS caching. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## White-box monitoring

Pozorovanie interných signals systému, napríklad queue depth, connection pool, error counters, garbage collection alebo saturation. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Whiteout — image layer

Marker vo filesystem changesete, ktorý v merged image view skryje path existujúci v staršom immutable layeri bez odstránenia jeho pôvodných bytes. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## Whitespace control — Helm

Použitie trim markers `{{-` a `-}}` a indentation functions na riadenie whitespace a newline v renderovanom YAML. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Wildcard permission — Kubernetes RBAC

RBAC pravidlo s `*` pre verbs, resources alebo API groups, ktoré zahŕňa aj budúce resources alebo capabilities pridané po upgrade. Pozri [RBAC](docs/09-kubernetes/rbac.md).

## Word splitting

Shell rozdelenie nequoted expansion výsledku na viac slov podľa `IFS`. Je častým zdrojom chýb pri paths a argumentoch. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md).

## Work queue Job

Job model, v ktorom viac worker Podov odoberá položky z external queue a completion correctness závisí od acknowledgment, retry a deduplication semantics tejto queue. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Work queue — Kubernetes controller

Fronta reconciliation keys s deduplication, retry a rate-limiting behavior používaná controller workers na bounded spracovanie zmien. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Worker node — Kubernetes

Fyzický alebo virtuálny server poskytujúci resources a node components potrebné na spúšťanie Pods pridelených control plane-om. Pozri [Kubernetes architecture](docs/09-kubernetes/kubernetes-architecture.md) a [Worker node components](docs/09-kubernetes/worker-node-components.md).

## `workflow:rules` — GitLab

Pipeline-level podmienky vyhodnotené pri vytvorení pipeline, ktoré rozhodujú, či pipeline vznikne pre konkrétny source, ref a dostupný variable context. Pozri [GitLab CI/CD syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md).

## Workflow template

Versionovaný reusable opis viacerých jobs, dependencies a policy hooks poskytujúci štandardnú delivery capability pre viaceré projects. Pozri [Reusable a parallel pipelines](docs/05-ci-cd-and-release/reusable-and-parallel-pipelines.md).

## Working tree

Filesystem materialization aktuálne checkoutnutého Git snapshotu, ktorú používateľ a nástroje priamo menia. Pozri [Working tree, staging area a repository](docs/03-git-and-automation/working-tree-staging-repository.md).

## Workload attestation

Proces overujúci platform, node, process alebo orchestration attributes workloadu pred vydaním jeho cryptographic identity. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Workload boundary — Well-Architected

Explicitný scope komponentov, ľudí, procesov, dát a dependencies, ktoré spoločne poskytujú hodnotený business outcome. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Workload density

Počet alebo množstvo workloads, ktoré možno bezpečne a výkonovo prevádzkovať na spoločnej infraštruktúre pri danom resource a isolation modeli. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Workload federation — Zero Trust

Explicitné prepájanie workload trust domains alebo identity authorities s riadenou výmenou trust bundles a samostatnou authorization policy. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Workload identity federation

Výmena ServiceAccount OIDC tokenu za krátkodobý external cloud alebo service credential podľa issuer, audience, subject a trust-policy podmienok. Pozri [ServiceAccount](docs/09-kubernetes/serviceaccount.md).

## Workload identity federation — CI/CD

Model, v ktorom job vymení krátkodobý signed identity token za scoped cloud alebo secret-provider credential bez uloženia dlhodobého access key v GitLabe. Pozri [Variables a secrets](docs/06-gitlab/variables-and-secrets.md).

## Workload identity — Kubernetes

Non-human identity workloadu, typicky reprezentovaná ServiceAccountom a krátkodobým tokenom alebo federovaným external credentialom. Pozri [ServiceAccount](docs/09-kubernetes/serviceaccount.md).

## Workload identity — Zero Trust

Krátkodobá, workload-specific cryptographic identity používaná pre service authentication namiesto IP-based trust alebo shared static credentials. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Writable layer — container

Dočasná zapisovateľná filesystem vrstva konkrétnej container instance umiestnená nad read-only image layers, ktorej lifecycle je typicky viazaný na container. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## Write compatibility

Schopnosť každej súčasne aktívnej application verzie zapisovať dáta, ktoré ostatné aktívne verzie bezpečne prečítajú a interpretujú. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Write index

Aktuálny backing index data streamu, do ktorého smerujú nové documents. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## `X-Forwarded-For`

De facto HTTP header prenášajúci client IP cez proxy chain. Je dôveryhodný iba pri kontrolovanom chain-e a správnom prepisovaní. Pozri [Proxy a reverse proxy](docs/02-networking-and-web/proxy-and-reverse-proxy.md).

## xBOM

Zastrešujúci pojem pre rôzne Bill of Materials domains, napríklad software, hardware, AI, services alebo cryptographic assets. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## XML Signature Wrapping

Útok využívajúci rozdiel medzi XML elementom overeným signature knižnicou a elementom spracovaným application logic. Pozri [SAML](docs/13-security-and-identity/saml.md).

## YAML mapping

YAML kolekcia key-value párov, analogická objectu alebo dictionary. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## YAML sequence

Usporiadaná YAML kolekcia hodnôt, analogická array alebo listu. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Zero-code instrumentation

Automatic telemetry generation bez zmeny application source, typicky cez agent, runtime hooks alebo platform integration. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Zero Trust

Súbor security princípov odstraňujúcich implicitnú dôveru podľa location alebo ownership a vyžadujúcich explicitné resource-specific access decisions. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Zero Trust Architecture — ZTA

Enterprise architecture implementujúca Zero Trust princípy cez identity, policy, enforcement, resource protection, telemetry a lifecycle controls. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Zero Trust governance

Cross-cutting ownership a decision model pre identity, resources, policies, data classification, exceptions, telemetry, privacy a migration roadmap. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Zero Trust migration

Risk-based staged presun od implicitných network trust paths k resource-specific identity-aware enforcementu s meraním bypassov a odstránením legacy paths. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Zero Trust Network Access — ZTNA

Application-specific remote access model používajúci identity, device context a policy namiesto broad network tunnel trustu. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Zero Trust pillar

Capability domain v CISA maturity model-e: Identity, Devices, Networks, Applications and Workloads alebo Data. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Zero Trust Policy Enforcement Point

NIST logical component presadzujúci access decision a sprostredkujúci alebo ukončujúci communication path medzi subjectom a resource-om. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Zombie process

Ukončený proces, ktorého exit status parent ešte neprevzal cez `wait`. Pozri [Procesy, thready, PID a signals](docs/01-linux-and-systems/processes-threads-pid-signals.md).

## Zonal affinity

Preferencia komunikácie a placementu resources v rovnakej Availability Zone pre nižšiu latency alebo transfer cost pri zachovaní cross-zone recovery modelu. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## Zonal resource — AWS

Resource viazaný na jednu Availability Zone, napríklad subnet, EC2 instance alebo EBS volume, ktorého lifecycle a attachment constraints sú súčasťou zonal failure modelu. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## zonal shift

Riadený presun podporovaného regional-service trafficu preč z impaired Availability Zone, ktorý stále vyžaduje zdravú capacity a dependencies v zostávajúcich AZ. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).
