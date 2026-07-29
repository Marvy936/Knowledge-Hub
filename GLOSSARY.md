# Glossary

Rýchly referenčný index technických pojmov používaných v Knowledge Hube. Glossary nenahrádza plné kapitoly: každé heslo obsahuje stručnú definíciu a odkaz na autoritatívny článok, ak už existuje.

## A/B testing

Riadený experiment porovnávajúci control a treatment variant na súbežných skupinách používateľov podľa vopred definovaných outcome a guardrail metrík. Pozri [A/B testing](docs/05-ci-cd-and-release/a-b-testing.md).

## Abort criterion

Vopred definovaná podmienka, pri ktorej sa rollout alebo experiment okamžite zastaví, pretože dopad prekročil prijateľnú hranicu. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md) a [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Absent-evidence verdict

Explicitné rozhodnutie, či chýbajúci signal znamená neprítomnosť udalosti alebo failure emission, collection, transport, ingestion, query či retention boundary. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Absent-evidence verdict — observability

Explicitné rozhodnutie, či chýbajúci signal znamená neprítomnosť system occurrence-u alebo failure emission, delivery, processing, ingestion, retention či query boundary. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Acceptance test

Test overujúci, či systém spĺňa dohodnuté business alebo používateľské acceptance criteria. Môže bežať na API, UI alebo inej vrstve. Pozri [End-to-end a acceptance tests](docs/04-testing-and-quality/end-to-end-and-acceptance-tests.md).

## Accepted condition — Gateway API

Route alebo Gateway status condition indikujúca, že zodpovedný controller prijal resource alebo jeho attachment k parentu podľa class, listener a policy pravidiel. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## Access acceptance verdict

Dôkaz, že current identity/session mapovanie, authorization policy, enforcement path, operation result a audit chain vytvárajú správny allowed aj forbidden outcome a prežijú second-login alebo second-sync test. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Access mode — Kubernetes storage

PV/PVC contract opisujúci podporovaný spôsob mount accessu, napríklad ReadWriteOnce, ReadOnlyMany, ReadWriteMany alebo ReadWriteOncePod; nepredstavuje application-level locking ani databázový clustering. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Access path — GitLab

Konkrétna cesta, cez ktorú subject získal capability nad resource-om, napríklad direct membership, parent-group inheritance, group sharing, custom role, protected-resource rule alebo token scope. Pozri [Projects, groups a permissions](docs/06-gitlab/projects-groups-permissions.md).

## Access-point identity enforcement

EFS behavior, pri ktorom access point obmedzí root path a nahradí client operation UID/GID configured POSIX identity, pričom filesystem policy, SG a file permissions zostávajú samostatnými gates. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Access review

Pravidelné alebo event-driven overenie, či principal stále potrebuje pridelené permissions, či ich scope a duration zostávajú primerané a či access možno odstrániť. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## Access subject

Exact identity, account, authenticator, session/token, principal mapping, requested action/resource/context, policy generation, enforcement point a audit scope analyzovaného accessu. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Access token

Credential vydaný authorization serverom a určený pre resource server na vykonanie obmedzených API operácií. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Account

Administratívny záznam identity v konkrétnom systéme, ktorý môže mať vlastný lifecycle, credentials, attributes a permissions. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Account acceptance verdict

Dôkaz, že account je v správnej OU, má reconciled baseline, povolené workload/recovery operations fungujú a zakázané Region, audit-disable, public alebo external access paths zlyhávajú. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Account baseline generation

Versionovaná realizácia identity, logging, security services, network, DNS, KMS, backup, quota, tagging a budget controls v konkrétnom AWS account-e. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Account vending — AWS

Automatizovaný proces vytvorenia a baseline konfigurácie nového AWS accountu vrátane OU placementu, identity, loggingu, networku, budgets, guardrails a ownership metadata. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## ACL — Access Control List

Rozšírený model oprávnení nad rámec owner/group/other mode bits. Pozri [Users, groups, permissions, sudo a PAM](docs/01-linux-and-systems/users-groups-permissions-sudo-pam.md).

## Action contract — alerting

Versionovaný contract určujúci user impact, urgency, ownera, safe first action, forbidden action, runbook a resolution validation konkrétneho page-u. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Action plugin — Ansible

Control-node plugin, ktorý pripravuje alebo koordinuje vykonanie Ansible action, napríklad spracuje arguments, transfer files alebo remote module result. Pozri [Ansible architecture](docs/07-infrastructure-as-code-and-configuration-management/ansible-architecture.md).

## Actionable alert

Alert, ktorý má jasného ownera, definovaný impact, konkrétnu okamžitú akciu, runbook a spôsob overenia resolution. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Actionable-rate verdict

Pomer pages alebo notifications, ktoré viedli k potrebnej ľudskej či automatickej akcii, vyhodnotený spolu s false positives, duplicates a auto-resolutions. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Active-active architecture

Architektúra, v ktorej viac lokalít alebo replicas súčasne spracúva production traffic; poskytuje vysokú využiteľnosť redundantnej kapacity, ale vyžaduje consistency, conflict-resolution a split-brain model. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Active-cardinality verdict

Rozhodnutie, či počet súčasne aktívnych series, streams, terms, alert instances alebo promoted trace dimensions zostáva v budgete pre konkrétny tenant a signal. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Active deadline — Job

Maximálny celkový čas, počas ktorého môže Kubernetes Job zostať aktívny; po jeho prekročení controller ukončí aktívne Pody a Job označí ako failed. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Active deployment digest inventory

Evidencia exact image index a selected platform manifest digestov, ktoré sú nasadené alebo potrebné pre podporovaný rollback, rescanning, retention a garbage collection. Pozri [Registries](docs/08-container-fundamentals-and-docker/registries.md).

## Active Directory Domain Services — AD DS

Distribuovaná Microsoft directory a identity platforma poskytujúca domains, forests, domain controllers, LDAP, Kerberos/NTLM, DNS-integrated discovery, Group Policy a multimaster replication. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Active-passive architecture

Architektúra, v ktorej primárny component spracúva workload a standby component prevezme úlohu po failover-e; zjednodušuje write ownership za cenu standby driftu a failover latency. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Active replica subject

Versionovaný inventory ReplicaSetom vlastnených Pod UIDs, ich lifecycle classification, readiness, availability a template equivalence pre konkrétnu ReplicaSet UID/generation. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Active series

Time series, ktorá má recent samples a spotrebúva active TSDB memory a metadata resources. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Active stream — Loki

Log stream, do ktorého sa aktuálne zapisujú log entries a ktorý drží ingester state a chunk resources. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Actor-session chain — CloudTrail

Rozbalená identity od CloudTrail `userIdentity` cez assumed-role ARN, principal/session issuer, source identity, user agent, source IP a upstream automation alebo human approval až po skutočného iniciátora API operácie. Pozri [Amazon CloudWatch a AWS CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

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

## Address-capacity boundary

Limit subnet IPv4/IPv6 addresses, ENIs, prefixes alebo Pod/task allocation modelu, ktorý môže blokovať container scale-out aj pri dostatku CPU a memory. Pozri [Amazon ECS a Amazon EKS](docs/11-cloud-and-aws/ecs-eks.md).

## Address-family publication contract

Explicitný contract určujúci IPv4/IPv6 host bind addresses, container listen addresses, DNS A/AAAA odpovede, firewall rules a client selection pre published service. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Address refactoring — Terraform

Zmena resource alebo module addressy pri zachovaní identity toho istého remote objektu, typicky deklarovaná cez `moved` block, aby nevznikol neúmyselný destroy/create. Pozri [Lifecycle, import a moved blocks](docs/07-infrastructure-as-code-and-configuration-management/lifecycle-import-moved-blocks.md).

## Address transition — Terraform

Versionovaná zmena resource alebo module instance address-y, pri ktorej má existujúci remote binding pokračovať pod novou address-ou bez neplánovaného destroy/create. Typicky sa deklaruje cez `moved` block. Pozri [Lifecycle, import a moved blocks](docs/07-infrastructure-as-code-and-configuration-management/lifecycle-import-moved-blocks.md).

## Adjacent-cohort validation — CloudOps

Overenie recovery na relevantnej susednej AZ, instance, account, tenant, Region alebo release cohort-e mimo pôvodného affected subjectu. Pozri [CloudOps troubleshooting drills](docs/11-cloud-and-aws/cloudops-troubleshooting-drills.md).

## Adjacent-cohort verification — CKA

Overenie, že oprava funguje aj na relevantných Nodes, Pods, endpoints alebo failure domains mimo jediného testovaného subjectu.

## Adjacent-cohort verification — Kubernetes

Overenie, že recovery funguje nielen na pôvodnom affected subjecte, ale aj na susedných Node, zone, release, tenant alebo endpoint cohortách. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Admission control — Kubernetes

Request-time vrstva Kubernetes API, ktorá po authentication a authorization mutuje alebo validuje relevantné create, update a delete requests pred persistence. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## Admission policy

Machine-readable pravidlo vyhodnocované v API admission path-e pred persistence alebo mutation resource-u. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Admission resource generation

Versionovaná množina defaultov, LimitRange pravidiel a ďalších admission mutations, ktoré zmenili source resource intent na effective Pod requests/limits. Pozri [Requests, limits a QoS](../docs/09-kubernetes/requests-limits-qos.md).

## Admission-to-authorization boundary

Prechod medzi úspešným authorization verdictom a admission kontrolami, ktoré ešte môžu request odmietnuť alebo mutovať. RBAC allow preto nie je dôkaz runtime úspechu. Pozri [RBAC](../docs/09-kubernetes/rbac.md).

## Admission verification

Pre-deployment policy decision, ktorý validuje image digest, signature identity, attestations a environment rules pred prijatím workloadu. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Admission webhook dependency

Synchronous external alebo in-cluster dependency API write pathu, ktorej latency, TLS, availability a failure policy priamo ovplyvňujú matching Kubernetes requests. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## Admitted/live/process-loaded state chain — Helm

Porovnanie rendered intentu s API-admitted objektom, current live resource-om a konfiguráciou skutočne načítanou application procesom. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Admitted object generation

Konkrétna object generation vzniknutá po server-side mutation a persistence, viazaná na object UID, field ownership a admission configuration generation. Pozri [Kubernetes architecture](docs/09-kubernetes/kubernetes-architecture.md) a [API a object model](docs/09-kubernetes/api-object-model.md).

## Admitted object — Kubernetes

Effective Kubernetes object po decoding, conversion, defaulting, mutating admission, validation a policy gates, ktorý bol prijatý na persistence; nemusí byť byte-for-byte zhodný so source manifestom. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Admitted Pod snapshot

Effective immutable alebo prevažne immutable Pod spec po API conversion, defaulting, mutation, validation a persistence, z ktorej kubelet vytvára runtime state konkrétneho Pod UID. Pozri [Pod](docs/09-kubernetes/pod.md).

## Admitted security contract

Resolved Pod a container security configuration po defaultingu a admission policy, ktorá sa stáva vstupom pre runtime. Nie je totožná so source manifestom ani s effective process authority. Pozri [SecurityContext a Pod Security](../docs/09-kubernetes/securitycontext-pod-security.md).

## Admitted workload identity

Effective `serviceAccountName`, token projection a identity-related Pod configuration po API defaulting, mutation a admission, nie iba source manifest. Pozri [ServiceAccount](../docs/09-kubernetes/serviceaccount.md).

## Adoptable Pod

Pod, ktorý matchuje ReplicaSet selector a nemá conflicting controller ownerReference, takže ho controller môže podľa ownership pravidiel adoptovať. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Adoption event — ReplicaSet

Controller transition, pri ktorom ReplicaSet zapíše controller ownerReference na matching adoptable Pod a začne ho započítavať do desired replica setu. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Advanced function — PowerShell

PowerShell function s `[CmdletBinding()]`, common parameters, parameter binding a cmdlet-like error/output správaním. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## Advisory gate

Quality gate, ktorý reportuje výsledok, ale neblokuje ďalší delivery krok. Používa sa pri zavádzaní alebo kalibrácii kontroly. Pozri [Code coverage a quality gates](docs/04-testing-and-quality/code-coverage-and-quality-gates.md).

## Advisory policy — Terraform

Policy as Code pravidlo, ktorého výsledok je viditeľný a auditovaný, ale samo neblokuje plan alebo apply. Používa sa pri kalibrácii alebo nízkom riziku. Pozri [Terraform testing a policy](docs/07-infrastructure-as-code-and-configuration-management/terraform-testing-and-policy.md).

## AEAD

Authenticated Encryption with Associated Data; encryption model poskytujúci confidentiality plaintextu a zároveň integrity a authenticity ciphertextu a voliteľných nešifrovaných metadata. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## Affinity population subject

Exact množina existujúcich Podov vybraná label a namespace selectorom pre required/preferred Pod affinity alebo anti-affinity výpočet. Pozri [Taints, tolerations, affinity a topology](../docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Aged-log canary

Synthetic log event, ktorého recent, historical a retention-expiry query behavior sa periodicky overuje cez celý collector, Loki storage a query lifecycle. Pozri [Loki](docs/12-observability/loki.md).

## Agent Collector

OpenTelemetry Collector nasadený blízko workloadu alebo Node-u na lokálny príjem, enrichment, batching, buffering a forwarding telemetry. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Agentless automation — Ansible

Model, v ktorom Ansible typicky nepotrebuje dlhodobo bežiaceho agenta na managed node a používa existujúci transport alebo API; stále však vyžaduje connection, identity a runtime capabilities. Pozri [Ansible architecture](docs/07-infrastructure-as-code-and-configuration-management/ansible-architecture.md).

## Aggregated ClusterRole

ClusterRole, ktorej rules controller automaticky skladá z iných ClusterRoles označených matching aggregation labels. Pozri [RBAC](docs/09-kubernetes/rbac.md).

## Aggregation generation — Kubernetes RBAC

Versionovaná množina ClusterRoles a rules zahrnutých do agregovaného ClusterRole-u; môže zmeniť effective permissions bez zmeny bindingu. Pozri [RBAC](../docs/09-kubernetes/rbac.md).

## Alarm-evaluation generation

Versionovaná kombinácia metric/query identity, periodu, statistic, threshold-u, evaluation periods, datapoints-to-alarm, missing-data behavior, actions a suppression/composite logiky. Pozri [Amazon CloudWatch a AWS CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## ALB listener rule

Prioritizované Layer 7 pravidlo Application Load Balancera, ktoré vyhodnocuje host, path, header, method, query alebo source-IP conditions a vykoná forward, redirect, fixed-response alebo podporovanú authentication action. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## Alert-action subject

Exact user outcome, signal population, rule generation, evaluation windows, alert identity, severity, owner, notification policy a external incident identity analyzovaného alertu. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Alert annotation — Prometheus

Dynamický ľudský context alerting rule, napríklad summary, description, current value alebo runbook URL, ktorý nie je súčasťou alert identity. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Alert as Code

Version-controlled model alerting rules, routing, templates, tests, ownership a runbook references nasadzovaný cez review a automatizovaný pipeline. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Alert condition

Query alebo expression spolu s thresholdom a time semantics, ktoré určujú, kedy alert prejde do active, pending alebo firing stavu. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Alert-control-plane authority

Jediný systém oprávnený vlastniť rule evaluation a paging policy konkrétneho symptom alertu, napríklad Prometheus/Alertmanager alebo Grafana-managed alerting. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Alert fatigue

Pokles pozornosti a dôvery spôsobený nadmerným počtom neakčných, duplicitných, flapping alebo nesprávne routovaných notifications. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Alert-fatigue feedback loop

Reinforcing loop, v ktorom noisy a neakčné pages znižujú dôveru a response speed, čo zhoršuje incident outcome a vedie k ďalším broad alerts alebo silences. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Alert fingerprint

Stabilný identifikátor Alertmanager alertu odvodený z jeho úplného label setu; používa sa na deduplication a alert identity. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Alert flapping

Opakované rýchle prepínanie alertu medzi firing a resolved stavom spôsobené nestabilným signalom, thresholdom, missing data alebo nedostatočným time windowom. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Alert group — Alertmanager

Množina firing alebo resolved alerts zoskupená podľa `group_by` labels a odosielaná ako jedna notification. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Alert identity

Stabilná identita alert instance odvodená z label setu a používaná na deduplication, grouping, silences a routing. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Alert-identity generation

Complete stable label set určujúci Alertmanager fingerprint, deduplication, grouping, routing, silence a inhibition behavior pre konkrétnu alert generation. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Alert label — Prometheus

Stabilný key/value atribút alertu používaný na identity, grouping, routing, silences a inhibition. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Alert-notification subject

Versionovaný subject spájajúci Prometheus rule generation, complete alert labels, Alertmanager cluster/config, route, group, receiver a external incident key. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Alert precision

Podiel alerts, ktoré správne identifikujú relevantný a actionable stav oproti false positives a neakčným notifications. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Alert retirement verdict

Rozhodnutie odstrániť, demote-nuť, zlúčiť alebo automatizovať alert, ktorý nemá ownera, action, precision alebo jedinečný detection benefit. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Alert-rule generation

Versionovaná query, population, threshold/burn-rate, windows, `for`, no-data a output-label konfigurácia vytvárajúca alert state. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Alert severity

Klasifikácia požadovanej reakcie a urgency, napríklad page, ticket alebo info, nie iba technická veľkosť nameranej hodnoty. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Alert storm

Veľké množstvo súvisiacich alebo duplicitných alerts a notifications, ktoré zahlcuje Alertmanager, receivers alebo on-call tím. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Alerting control-plane ownership — Grafana

Explicitné určenie, či rule evaluation, alert identity a notification policy vlastní Grafana-managed alerting alebo data-source-managed systém ako Prometheus/Loki. Pozri [Grafana](docs/12-observability/grafana.md).

## Alerting rule — Prometheus

PromQL expression vyhodnocovaná Prometheus rule engine-om, ktorá po splnení condition a voliteľného `for` vytvára firing alert. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Alertmanager

Komponent Prometheus ekosystému, ktorý prijíma alerts, deduplikuje ich, zoskupuje, routuje, mutuje a posiela notifications do receivers. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Alertmanager acceptance verdict

Dôkaz, že expected alert vytvoril správnu receiver notification a resolved outcome, unrelated scope nebol inhibovaný alebo silencovaný a HA/retry nevytvorili neakceptované duplicity. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Alertmanager HA

Viac Alertmanager replicas koordinovaných peer meshom a replikáciou silence/notification state-u; zvyšuje dostupnosť, ale negarantuje exactly-once notifications. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Alertmanager notification log

Runtime state používaný Alertmanagerom na deduplication, group timing a rozhodovanie o update/repeat notifications. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Alertmanager peer mesh

Peer-to-peer cluster communication medzi Alertmanager replicas na replikáciu silences a notification state-u. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Alias — YAML

YAML referencia na node označený anchorom. Znižuje duplicitu, ale môže komplikovať tooling a čitateľnosť. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Allocation-rule generation

Versionovaná sada tag, account, Cost Category a shared-cost rules použitá na mapovanie billing line items k owners/products. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

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

## Ansible capability contract

Versionované a dokumentované rozhranie reusable role alebo collection capability zahŕňajúce inputs, defaults, side effects, privilege a platform assumptions, notification topics, runtime outcome, compatibility a recovery behavior. Pozri [Roles a collections](docs/07-infrastructure-as-code-and-configuration-management/roles-and-collections.md).

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

## Ansible idempotency subject

Rekonštruovateľná identita idempotency a convergence testu zahŕňajúca source revision, execution environment, collection set, inventory a target manifest, effective values, fact/lookup generations, desired artifact identities, external operation IDs a concurrency context. Pozri [Ansible idempotencia](docs/07-infrastructure-as-code-and-configuration-management/ansible-idempotency.md).

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

## Ansible run subject

Rekonštruovateľná identita automation runu zahŕňajúca source revision, playbook, `ansible-core`, execution environment image, collections, inventory subject, resolved variables, credentials, strategy, batch a controller run ID. Pozri [Ansible architecture](docs/07-infrastructure-as-code-and-configuration-management/ansible-architecture.md).

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

## API request subject — Kubernetes

Rekonštruovateľná identita requestu zahŕňajúca cluster endpoint a CA, caller identity, verb, GVR, namespace/name alebo subresource, request digest, field manager, preconditions, admission generation a response/persistence outcome. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## API-state generation

Konzistentná Kubernetes object-state generácia viazaná na etcd cluster identity, revision, encryption configuration a čas recovery pointu. Pozri [etcd backup a restore](../docs/09-kubernetes/etcd-backup-restore.md).

## API-state RPO

Maximálna prijateľná strata Kubernetes API object zmien medzi posledným použiteľným etcd snapshotom a incidentom. Musí byť koordinovaná s RPO application dát. Pozri [etcd backup a restore](docs/09-kubernetes/etcd-backup-restore.md).

## API test

Runtime test verejného API rozhrania overujúci response, semantics, authorization a side effects. Jeho scope môže byť component, integration alebo E2E. Pozri [Contract a API tests](docs/04-testing-and-quality/contract-and-api-tests.md).

## API-to-workload lifecycle

End-to-end transition od authenticated a admitted API requestu cez persisted object generation, controller graph, scheduler assignment, node execution a Service eligibility až po application business outcome. Pozri [Kubernetes architecture](docs/09-kubernetes/kubernetes-architecture.md).

## API version negotiation — Docker

Mechanizmus, ktorým Docker client a Engine vyberú spoločnú podporovanú verziu Engine API; neznamená, že starší server podporuje všetky features novšieho CLI. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## API write-path subject

Subject-bound evidence jedného Kubernetes write-u od endpointu a caller identity cez authentication, authorization a admission po etcd revision, response, audit a watch publication. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## APIService — Kubernetes

Cluster-scoped object registrujúci aggregated API group/version a service, ktorá ju obsluhuje. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## AppArmor profile

Mandatory Access Control profil definujúci povolené paths, execute transitions, capabilities, network operations a ďalšie správanie programu. Pozri [SELinux a AppArmor](docs/01-linux-and-systems/selinux-and-apparmor.md).

## AppArmor profile — Kubernetes

Host-level Linux Security Module profil obmedzujúci filesystem, capability, network a ďalšie operations container procesu podľa Node a runtime podpory. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## Applicability verdict — Well-Architected

Explicitné rozhodnutie, či best practice je implemented, partial, missing, not applicable s evidence alebo unknown pre chýbajúce dôkazy. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Application acceptance subject — Kubernetes

Spoločná identita clusteru, top-level object UID/generation, dependent resources, Pod image/config/secret generations, eligible endpoints a business verification potrebná na prijatie rollout-u. Pozri [Kubernetes architecture](docs/09-kubernetes/kubernetes-architecture.md).

## Application-aware readiness — stateful workload

Readiness verdict odvodený z application role, synchronization, membership, data generation a client-serving capability, nie iba z otvoreného portu alebo živého processu. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Application-consistent backup

Backup vytvorený tak, aby zachoval logicky konzistentný application state, napríklad po flushnutí buffers, filesystem freeze alebo koordinovanom database checkpoint-e. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Application-consistent backup — Kubernetes storage

Backup generation vytvorená po koordinovanom application checkpoint-e, flushi alebo quiesce a následne overená clean restore testom. Pozri [Volumes, PV, PVC a StorageClass](../docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Application-consistent recovery point

Recovery point, v ktorom databázové checkpointy, logs, queue offsets a external-operation ledger patria k jednej definovanej business transaction boundary. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## application-consistent snapshot

Snapshot vytvorený po koordinovanom flush, quiesce alebo engine-native checkpoint-e tak, aby obnovené dáta reprezentovali validný application transaction state. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Application-consistent snapshot set

EBS snapshot alebo coordinated multi-volume snapshots viazané na application checkpoint/LSN po quiesce/flush procedure, nie iba crash-consistent block capture. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Application data generation — Kubernetes storage

Application-level identita mounted dát, napríklad tenant, schema, checkpoint, replication epoch a backup lineage; nie je odvodená iba z PVC alebo PV phase. Pozri [Volumes, PV, PVC a StorageClass](../docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Application Load Balancer — ALB

Layer 7 Elastic Load Balancing variant pre HTTP/HTTPS traffic s listener rules, host/path routing, target groups a application health checks. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## Application version — Helm

Version aplikácie deklarovaná chart metadata fieldom `appVersion`; je informačná a nie je automaticky chart version, image tag ani release revision. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Apply test — Terraform

Terraform test run, ktorý vykoná apply proti reálnemu alebo testovaciemu provider environmentu, vyhodnotí assertions a následne sa pokúsi vytvorenú infraštruktúru odstrániť. Pozri [Terraform testing a policy](docs/07-infrastructure-as-code-and-configuration-management/terraform-testing-and-policy.md).

## Approval — CI/CD

Explicitné rozhodnutie oprávnenej identity, ktoré povoľuje merge, promotion, deployment alebo release na základe definovaného rizika a dostupnej evidence. Pozri [Quality gates a approvals](docs/05-ci-cd-and-release/quality-gates-and-approvals.md).

## Approval freshness

Platnosť approvalu viazaná na nezmenený subject, evidence, target environment, rollout strategy a časové okno; zmena ktorejkoľvek dependency môže approval invalidovať. Pozri [Quality gates a approvals](docs/05-ci-cd-and-release/quality-gates-and-approvals.md).

## Approval rule — GitLab

GitLab pravidlo definujúce počet required approvals, eligible users alebo groups a branch/policy scope merge requestu. Pozri [Merge requests a approvals](docs/06-gitlab/merge-requests-and-approvals.md).

## Architecture contract — Kubernetes cluster

Versionovaný súbor rozhodnutí o endpoint identity, etcd topology, failure domains, CIDRs, runtime, CNI/CSI, PKI, storage, backup a upgrade modeli. Pozri [Cluster installation a lifecycle](../docs/09-kubernetes/cluster-installation-lifecycle.md).

## ARP — Address Resolution Protocol

IPv4 protokol mapujúci lokálnu next-hop IP adresu na MAC adresu. Pozri [Ethernet, MAC a ARP](docs/02-networking-and-web/ethernet-mac-arp.md).

## Artifact

Jednoznačne identifikovateľný výstup build procesu určený na testovanie alebo distribúciu. Pozri [Software Development Life Cycle](docs/00-foundations/sdlc.md).

## Artifact — CI/CD

Versionovaný a identifikovateľný výstup pipeline určený na ďalšie overenie, distribúciu alebo deployment. Na rozdiel od cache môže byť súčasťou correctness a release evidence. Pozri [Trigger, artifact a cache](docs/05-ci-cd-and-release/trigger-artifact-cache.md).

## Artifact digest

Content-derived immutable identifikátor artifactu, napríklad SHA-256 digest container image, používaný na presnú väzbu medzi buildom, evidence, promotion a deploymentom. Pozri [Trigger, artifact a cache](docs/05-ci-cd-and-release/trigger-artifact-cache.md).

## Artifact lineage — multi-stage build

Väzba od source a immutable stage inputs cez konkrétny build/test node a artifact digest až po bytes prenesené do final stage-u a publikovaný image digest. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## Artifact promotion

Presun už vytvoreného a overeného immutable artifactu medzi environmentmi alebo release stages bez jeho opätovného rebuildovania. Pozri [Continuous Delivery](docs/05-ci-cd-and-release/continuous-delivery.md).

## Artifact quarantine

Riadené zablokovanie promotion, pull alebo deploymentu konkrétneho artifact digestu pri zachovaní forensic evidence. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md) a [Image signing](docs/13-security-and-identity/image-signing.md).

## Artifact revocation

Policy decision zneplatňujúci predtým akceptovaný artifact digest, signing identity alebo trust path bez nutnosti odstrániť historickú transparency evidence. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Artifact subject — GitLab CI

Identita pipeline outputu tvorená projektom, pipeline source-om, source alebo candidate SHA, resolved configuration digestom, producer jobom a attemptom, variantom/platformou, runner/toolchain subjectom a content digestom. Pozri [Artifacts a cache](docs/06-gitlab/artifacts-and-cache.md).

## Artifact-to-process supply chain — OCI

End-to-end transition od source/build subjectu cez OCI image graph, registry, platform selection, trust verification, pull/unpack a runtime bundle až po process a deployment evidence. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Artifact version

Logical identifier artifactu používaný na komunikáciu release identity alebo compatibility významu. Má byť mapovateľný na konkrétny immutable content digest. Pozri [Artifact versioning](docs/05-ci-cd-and-release/artifact-versioning.md).

## `artifactType` — OCI

OCI manifest field opisujúci semantic media type artifactu, najmä keď config descriptor neposkytuje dostatočnú type informáciu. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## ASG reconciliation subject

Auto Scaling Group desired state, current instance/lifecycle inventory, health sources, scaling activities, suspended processes a launch/termination decisions pre jednu fleet generation. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Assertion Consumer Service — ACS

Service Provider endpoint prijímajúci a validujúci SAML Response pri browser SSO. Pozri [SAML](docs/13-security-and-identity/saml.md).

## Asset-impact matrix — CIA

System-specific mapping assetu alebo business procesu na confidentiality, integrity a availability loss, impact threshold, controls, evidence a ownera. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Asset — security

Dáta, systém, identita, služba, konfigurácia, artifact alebo business process, ktorého strata alebo kompromitovanie má hodnotiteľný dopad. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Assigned-Pod execution subject

Identita Node-side realizácie zahŕňajúca cluster, Pod UID a admitted spec, Node UID, kubelet/runtime/CNI/CSI generations, sandbox, images, mounts, probes, status a business outcome. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## Assignment–exposure funnel

Observation chain od eligible population a variant assignmentu cez application/runtime survival po reálnu treatment exposure a následný outcome. Používa sa na lokalizáciu Sample Ratio Mismatch, treatment-specific crashu, logging lossu alebo selection biasu. Pozri [A/B testing](docs/05-ci-cd-and-release/a-b-testing.md).

## Assume breach

Zero Trust design assumption, že identity, endpoint, workload alebo interná network path môžu byť kompromitované, a preto treba obmedziť trust paths, sessions a blast radius. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Assumed-role session subject

Konkrétna STS session identifikovaná session ARN, source identity, tags, policies, issue time a expiration; nie abstraktná IAM role. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## AssumeRole — AWS STS

AWS STS operation, ktorou oprávnený principal prevezme IAM role a získa dočasnú role session s expiration, session identity a effective permissions. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## Assurance — security

Dôkazy a miera dôvery, že navrhnuté security controls sú správne implementované a účinné. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Asymmetric routing

Stav, keď forward a return traffic rovnakého flow používajú rozdielne network paths. Pozri [Routing a default gateway](docs/02-networking-and-web/routing-and-default-gateway.md).

## Asyncio

Python framework pre cooperative asynchronous I/O založený na event loop-e, coroutines a tasks. Pozri [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Atomic publication — GitLab registry

Publication protocol `upload immutable content → over digesty → vytvor manifest alebo package version → read-back completeness → atomicky publikuj release reference`, s idempotency a reconciliation pri unknown outcome. Pozri [Container a package registry](docs/06-gitlab/container-and-package-registry.md).

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

## Attempt amplification — RED

Rast počtu technical attempts voči počtu logical operations spôsobený retries, hedgingom, fan-outom alebo redelivery, ktorý môže zvýšiť downstream load aj pri stabilnom business trafficu. Pozri [RED method](docs/12-observability/red-method.md).

## Attempt counter — observability

Metric counter počítajúci technical executions alebo dependency calls oddelene od caller-visible logical operations. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Attempt duration — RED

Trvanie jedného technical attemptu, ktoré nesmie byť zamieňané s end-to-end duration celej logical operation vrátane retries, queue waitu a backoffu. Pozri [RED method](docs/12-observability/red-method.md).

## Attempt rate

Počet technických pokusov o vykonanie operácie za čas vrátane retries; môže byť vyšší než počet logical operations. Pozri [RED method](docs/12-observability/red-method.md).

## Attempts-per-operation distribution

Rozdelenie počtu technical attempts pripadajúcich na jednu logical operation, používané na detekciu retry amplification a degraded dependencies. Pozri [RED method](docs/12-observability/red-method.md).

## Attestation — supply chain

Signed statement, ktorý viaže subject digest na konkrétny predicate a identity vydávajúcu dané tvrdenie. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Attribute-authority matrix

Mapping identity, ownership a authorization attributes na ich authoritative source, consumers, freshness a invalidation contract. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Attribute-Based Access Control — ABAC

Authorization model používajúci attributes principalu, resource-u, action a environmentu na vytvorenie access decisionu. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Attributed unit cost

Total spoľahlivo allocated workload cost vydelený validným business outcome volume-om v comparable period a cost view. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Audience — OAuth/OIDC/SAML

Identifier zamýšľaného konzumenta tokenu alebo assertion; musí byť validovaný, aby sa artifact nedal použiť voči inému clientovi alebo resource serveru. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md), [OpenID Connect](docs/13-security-and-identity/openid-connect.md) a [SAML](docs/13-security-and-identity/saml.md).

## Audit completeness verdict — identity

Rozhodnutie, či security audit zachoval trusted time, original actora, delegated subject, action, target, policy generation, result a celý source-to-query delivery path. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Audit-delivery contract — CloudTrail

Trail scope a event selectors spolu s S3 destination, bucket/KMS policies, integrity validation, retention, protection a monitoringom delivery failures, ktoré určujú dostupnosť audit evidence. Pozri [Amazon CloudWatch a AWS CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## Audit/Event/business-event separation

Rozlíšenie API audit requestu, krátkodobého Kubernetes diagnostického Eventu a durable application business udalosti. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Audit-generation subject

Exact source event, schema, actor/delegation fields, exporter, queue, central store, retention, access a query generation relevantnej security evidence. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Audit record

Časovo označený záznam o tom, kto vykonal akú operáciu, voči ktorému resource-u, odkiaľ a s akým výsledkom. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Authenticated scanning

Vulnerability scanning vykonaný s oprávneným host alebo application accessom, ktorý umožňuje presnejšie zistiť installed packages, configuration a patch state než čisto network-based scan. Pozri [Vulnerability a patch management](docs/13-security-and-identity/vulnerability-and-patch-management.md).

## Authentication

Proces overenia identity alebo kontroly nad authenticatorom pred vytvorením session, tokenu alebo iného authenticated contextu. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Authentication-event generation

Versionovaný výsledok verifiera viažuci principal, authenticator, method, assurance, verifier identity, timestamp a subsequent session alebo token issuance. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Authentication Service — Kerberos AS

Časť KDC, ktorá po počiatočnej authentication vydáva clientovi Ticket-Granting Ticket. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Authenticator

Prostriedok kontrolovaný claimantom a používaný na preukázanie identity, napríklad password, passkey, smart card, certificate alebo cryptographic device. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Authenticity

Vlastnosť umožňujúca dôverovať, že entity, dáta alebo artifacts pochádzajú z deklarovaného a overeného source-u. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Authoritative attribute writer

Jediný explicitne určený controller alebo tool oprávnený zapisovať konkrétny mutable object attribute. Ostatní consumers ho iba čítajú alebo používajú versionovaný transfer contract. Pozri [Terraform vs. Ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md).

## Authoritative cloud recovery

Obnova cez opravený desired-state/source contract, last-known-good generation alebo clean recovery manifest namiesto manual snowflake mutation. Pozri [CloudOps troubleshooting drills](docs/11-cloud-and-aws/cloudops-troubleshooting-drills.md).

## Authoritative dashboard writer

Jediný source alebo controller oprávnený meniť konkrétny dashboard UID, napríklad Git provisioning, Terraform alebo Operator; UI edit bez zmeny autority je iba dočasný drift. Pozri [Grafana](docs/12-observability/grafana.md).

## Authoritative identity source

Systém považovaný za zdroj pravdy pre existenciu, status, ownera alebo attributes identity, napríklad HR systém alebo service catalog. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Authoritative knowledge mapping — SOA-C03

Mapovanie current exam task statements na authoritative Knowledge Hub kapitoly a ich lifecycle/failure models namiesto vytvárania paralelných skrátených service definícií. Pozri [AWS Certified CloudOps Engineer – Associate](docs/11-cloud-and-aws/cloudops-engineer-associate-soa-c03.md).

## Authoritative remediation — Docker

Recovery vykonaná cez versionovaný source, configuration, policy, nový immutable artifact alebo explicitnú state generation namiesto ponechania ručnej mutation v bežiacom containeri. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Authoritative remediation subject — Kubernetes

Exact object, artifact, Node, data, policy alebo external state generation, ktorú remediation opravuje namiesto maskovania symptómu na inej vrstve. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Authoritative repair — CKA

Minimálna zmena na skutočnom source-of-truth alebo owner boundary, po ktorej môže systém znovu skonvergovať.

## Authoritative run

Pipeline run určený policy ako jediný zdroj required verdictu alebo release artifactu pre konkrétny candidate a workflow revision. Pozri [Trigger, artifact a cache](docs/05-ci-cd-and-release/trigger-artifact-cache.md).

## Authoritative security recovery

Obnova identity, credential, configuration, data a business state-u z dôveryhodných sources vrátane revocation, rotation, reconciliation a allowed/forbidden validation. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Authoritative source — IaC

Systém alebo versionovaný artifact považovaný za rozhodujúcu deklaráciu požadovaného infraštruktúrneho stavu; manuálne runtime zmeny sa voči nemu musia adoptovať, vrátiť alebo explicitne vyriešiť. Pozri [Infrastructure as Code principles](docs/07-infrastructure-as-code-and-configuration-management/infrastructure-as-code-principles.md).

## Authoritative writer

Jediný systém alebo workflow oprávnený meniť konkrétny mutable object alebo attribute; viac writerov vytvára ownership conflict a perpetual drift. Pozri [Terraform vs. Ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md).

## Authorization

Rozhodnutie, či principal smie vykonať konkrétnu action voči konkrétnemu resource-u v danom context-e. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Authorization closure — AWS

Positive a forbidden request tests, CloudTrail evidence a business verification, ktoré dokazujú správny effective permission graph po zmene alebo incidente. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## Authorization closure — Kubernetes

Incident closure dokazujúci odstránenie všetkých direct/group/aggregation permission paths, rotáciu uniknutých credentials a úspech allowed aj forbidden request testov. Pozri [RBAC](../docs/09-kubernetes/rbac.md).

## Authorization code

Krátkodobý jednorazový OAuth grant, ktorý client vymieňa na token endpoint-e za access token. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Authorization explainability

Schopnosť rekonštruovať principal/session, direct a nested assignments, roles/policies, resource/context, combining semantics, decision, enforcement a výsledok jedného allow alebo deny. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Authorization request subject

Exact authenticated user/groups/extras, verb, API group, resource/subresource, namespace, resourceName a request timestamp vyhodnocované authorizerom. Pozri [RBAC](../docs/09-kubernetes/rbac.md).

## Authorization request tuple

Exact principal, action, resource a context spolu s policy generation, nad ktorými vzniká authorization decision. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

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

Policy-driven rozhodnutie posunúť artifact alebo rollout do ďalšej fázy bez rutinného manuálneho approvalu na základe complete evidence, risku a environment health. Pozri [Continuous Deployment](docs/05-ci-cd-and-release/continuous-deployment.md).

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

## Automation side-effect boundary — Systems Manager

Runbook step alebo external operation, po ktorej už jednoduchý reverse API call nemusí obnoviť pôvodný state; vyžaduje explicitný rollback, compensation, restore, immutable replacement alebo manual escalation. Pozri [AWS Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## `automountServiceAccountToken`

ServiceAccount alebo Pod setting určujúci, či kubelet automaticky pripojí štandardný ServiceAccount credential projection do Podu. Pozri [ServiceAccount](docs/09-kubernetes/serviceaccount.md).

## Autoscaling acceptance verdict

Verdikt, že current metric generation, recommendation, scale write, Pod/Node realization a downstream/business outcome zodpovedajú reviewed scaling contractu. Pozri [HPA a autoscaling](../docs/09-kubernetes/hpa-autoscaling.md).

## Autoscaling control subject

Súvislá identita HPA UID/generation, scale target UID/generation, metric definition, eligible Pod cohort, recommendation, behavior policy a scale-field ownera. Pozri [HPA a autoscaling](../docs/09-kubernetes/hpa-autoscaling.md).

## Autoscaling feedback loop

Nežiaduca alebo zámerná interakcia viacerých autoscaling controllers a metrics, pri ktorej zmena replicas, requests alebo Node capacity mení vstup ďalšej scaling slučky. Pozri [HPA a autoscaling](docs/09-kubernetes/hpa-autoscaling.md).

## Autoscaling observation matrix

Mapa evidence cez metric source, API adapter, cohort, recommendation, scale subresource, Deployment/Pod/Node realization, readiness, downstream a business SLO. Pozri [HPA a autoscaling](../docs/09-kubernetes/hpa-autoscaling.md).

## Autoscaling reaction time

Čas od zmeny business demandu cez metric collection, HPA reconcile, scale write, scheduling, Node provisioning, image/startup/readiness až po novú serving capacity. Pozri [HPA a autoscaling](../docs/09-kubernetes/hpa-autoscaling.md).

## Availability — security

Zabezpečenie včasného a spoľahlivého prístupu k informáciám a službám pre autorizovaných používateľov a procesy. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Availability timing subject — Deployment

Pod UID a časový interval, počas ktorého Pod zostáva Ready podľa `minReadySeconds` a ďalších rollout conditions pred započítaním ako available replica. Pozri [Deployment](docs/09-kubernetes/deployment.md).

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

## AWS capability subject

Versionovaná identita cloudovej business capability zahŕňajúca account, Region, resources, application artifact, configuration, credential a data generations spolu s požadovaným business outcome-om. Pozri [IaaS, PaaS a SaaS](docs/11-cloud-and-aws/iaas-paas-saas.md).

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

## AWS network-generation subject

Versionovaný AWS network subject obsahujúci account, Region, VPC CIDRs, subnet/AZ inventory, ENIs, route-table associations, gateway/endpoint attachments, policy generations a DNS/observation contract. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## AWS Organizations

AWS služba na centrálne riadenie kolekcie účtov cez management account, root, OUs, organization policies, consolidated billing a delegated administration. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## AWS Outposts

AWS-managed infrastructure umiestnená v zákazníckej alebo colocation lokalite a prepojená s parent AWS Regionom, určená pre hybridné workloady s locality alebo latency požiadavkami. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## AWS placement subject

Exact account, Region, AZ ID, subnet, resource, release, data a capacity identity použitá na rozhodovanie o umiestnení a failure-domain recovery. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## AWS Region

Geografická AWS infraštruktúrna oblasť obsahujúca viac Availability Zones a predstavujúca regionálnu service, data-residency a fault-isolation boundary. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## AWS request authorization subject

Exact caller account a session ARN, credential source, action, resource ARN, Region/endpoint, request context, applicable policy generations a požadovaný service/business outcome. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## AWS responsibility subject

Konkrétny account, Region, service/resource, feature, configuration, principal, data a requested outcome, ku ktorému sa viaže provider/customer/shared responsibility verdict. Pozri [Shared responsibility model](docs/11-cloud-and-aws/shared-responsibility-model.md).

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

## Backend acknowledgement — log delivery

Výsledok output requestu potvrdený cieľovým backendom vrátane per-item semantics, nie iba transportného HTTP statusu. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Backend acknowledgement — telemetry

Dôkaz, že observability backend prijal konkrétny batch alebo record pred tým, než collector bezpečne posunie durable offset. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Backend migration — Terraform

Riadený presun state lineage a snapshots z jedného backendu do druhého so zastavením writers, backupom, overením destination identity a následným planom. Pozri [Remote backend a state locking](docs/07-infrastructure-as-code-and-configuration-management/remote-backend-and-state-locking.md).

## Backend scheduler — Tempo

Tempo component, ktorý plánuje maintenance jobs ako compaction, retention alebo redaction a prideľuje ich backend workers. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Backend target connection

Nová load-balancer-to-target connection vyhodnocovaná podľa target portu, source identity, SG/NACL, backend TLS/listener a application readiness, nezávisle od viewer connection. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## Backend worker — Tempo

Tempo component vykonávajúci maintenance jobs pridelené backend schedulerom nad object-storage blocks. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Backend writer subject — Terraform

Presná identita state writera zahŕňajúca execution run, workload identity, backend endpoint, state key alebo workspace, lineage, prior serial, lock ID a operation purpose. Používa sa na rozlíšenie aktívneho, orphaned alebo nesprávne zacieleného writera. Pozri [Remote backend a state locking](docs/07-infrastructure-as-code-and-configuration-management/remote-backend-and-state-locking.md).

## BackendRef — Gateway API

Typed reference z Route rule na backend resource, typicky Kubernetes Service a port, spolu s voliteľnou weight alebo policy metadata. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## Backfill

Riadené doplnenie alebo transformácia existujúcich dát, typicky v bounded batches s checkpointingom, rate limitom, validáciou a možnosťou pause/resume. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Backing index

Skrytý fyzický index patriaci data streamu; writes smerujú do aktuálneho write backing indexu a searches prechádzajú všetky relevantné generations. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Backing-volume identity

External storage asset identifikovaný napríklad CSI `volumeHandle`, provider volume ID, zone a encryption-key generation, ktorý PV reprezentuje v Kubernetes API. Pozri [Volumes, PV, PVC a StorageClass](../docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Backlog deadline

Najneskorší čas, do ktorého musí queued alebo stream event vytvoriť business outcome; queue depth alebo iterator age pod platform retention limitom ešte nemusí spĺňať business SLO. Pozri [AWS Lambda](docs/11-cloud-and-aws/lambda.md).

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

## Baseline contract — CloudOps lab

Dôkaz, že exact lab generation, data/control paths, telemetry, security negative tests a cleanup path fungujú pred fault injection. Pozri [CloudOps hands-on labs](docs/11-cloud-and-aws/cloudops-hands-on-labs.md).

## Baseline Pod Security Standard

Pod Security Standards profil blokujúci známe nebezpečné privilege escalations a host access pri širšej workload kompatibilite než profil Restricted. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## Batch acceptance verdict

Dôkaz, že logical run má canonical durable result, všetky work items majú explicitný stav, duplicate alebo partial side effects boli reconciled a nasledujúci run je bezpečný. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Batch fencing epoch

Monotónna alebo lease-based authority generation určujúca, ktorý worker smie konať nad konkrétnym logical runom alebo work itemom po retry, timeout-e alebo ownership transition. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Batch result ledger

Authoritative durable záznam logical runs, work items, operation IDs, checkpoints a accepted výsledkov, odlišný od Kubernetes Job statusu. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Batch size

Množstvo zmien spracovaných alebo nasadených naraz. Menšie batches znižujú blast radius a skracujú feedback. Pozri [Three Ways of DevOps](docs/00-foundations/three-ways.md).

## BDD — Behavior-Driven Development

Collaboration a discovery prístup používajúci príklady správania a spoločný jazyk na spresnenie požiadaviek; Gherkin je iba jedna možná reprezentácia. Pozri [End-to-end a acceptance tests](docs/04-testing-and-quality/end-to-end-and-acceptance-tests.md).

## Bearer token

Token použiteľný každým držiteľom bez ďalšieho proof-of-possession; jeho leakage predstavuje credential compromise počas platnosti. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## `before-hook-creation` — Helm

Default hook cleanup behavior, pri ktorom Helm pred spustením nového hook resource-u odstráni predchádzajúci resource s rovnakou identity. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Behavior-routing verdict

Prvá matching CloudFront cache behavior, ktorá pre normalized viewer path určí origin, methods, viewer policy, cache key, origin request policy a edge-function chain. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Behavioral equivalence — environment

Miera, do akej nižší environment zachováva produkčne relevantné protokoly, konfiguráciu, topology, limits a security behavior aj bez úplnej veľkostnej parity. Pozri [Environment a promotion](docs/05-ci-cd-and-release/environment-and-promotion.md).

## BestEffort QoS

Kubernetes QoS class pre Pod bez CPU a memory requests alebo limits podľa platných QoS calculation pravidiel; scheduler nemá deklarovanú potrebu a Pod je pri resource pressure typicky najzraniteľnejší. Pozri [Requests, limits a QoS](docs/09-kubernetes/requests-limits-qos.md).

## Billing-generation identity

Exact billing dataset, period, payer scope, pricing/discount rules, cost metric a finalized/estimated state použitý pri cost reasoning. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Bind — LDAP

LDAP operation, ktorá nastavuje authentication state connectionu pomocou anonymous, simple alebo SASL mechanismu. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## Bind mount — container

Sprístupnenie existujúceho daemon-host filesystem pathu do container mount namespace-u so silnou väzbou na host path, permissions, labels a lifecycle. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md) a [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## Bind-source resolution boundary

Rozhranie medzi client pathom, Docker daemon alebo Desktop VM pathom a container destination, na ktorom sa bind source môže vyhodnotiť na inom hoste alebo directory, než operator očakáva. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## Binding — Kubernetes scheduling

Finálny scheduler krok zapisujúci vybraný Node do Podu; po bindingu kubelet na danom Node-e realizuje workload. Pozri [Scheduling](docs/09-kubernetes/scheduling.md).

## Binding subject — Kubernetes scheduling

Exact Pod-to-Node placement transition po reserve, permit a pre-bind krokoch, typicky reprezentovaná zápisom Node mena do Podu. Pozri [Scheduling](../docs/09-kubernetes/scheduling.md).

## Black-box monitoring

Pozorovanie systému zvonka z perspektívy používateľa alebo clienta, napríklad cez HTTP, DNS, TLS alebo end-to-end synthetic test. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Black-box outcome canary

Kontrolovaná external operácia overujúca skutočný caller alebo business contract nezávisle od internal telemetry a dashboard assumptions. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Blast radius

Maximálny rozsah používateľov, trafficu, dát, komponentov alebo failure domains, ktoré môže zmena, incident alebo experiment ovplyvniť. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Blended cost — AWS

Cost view používajúci pri niektorých consolidated-billing scenároch priemernú rate naprieč organization family. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Blob — Git object

Nemenný Git object obsahujúci bytes jedného súboru bez filename a path metadata. Pozri [Git object model](docs/03-git-and-automation/git-object-model.md).

## Block builder — Tempo

Component, ktorý konzumuje trace records z durable queue, skladá ich do Parquet blocks a zapisuje do object storage. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Block commit boundary

Application/filesystem/database moment, po ktorom required writes a metadata boli flushnuté alebo checkpointnuté na EBS tak, aby recovery semantics boli explicitné. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Block device

Kernelové zariadenie poskytujúce blokovo adresovaný storage. Pozri [Storage, mounty a filesystems](docs/01-linux-and-systems/storage-mounts-and-filesystems.md).

## `block` — Helm

Go template action, ktorá definuje default named template content a zároveň ho vykreslí; globálna override semantics môže byť menej explicitná než values alebo library-chart contract. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Block-publication generation — tracing

Exact Kafka offsets, block-builder version, Parquet block objects, object-store paths a commit state, ktoré preukazujú prechod trace records do historical storage. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Blocking gate

Quality gate, ktorého neúspech zastaví merge, promotion alebo deployment. Má sa používať pre spoľahlivý signál spojený s neprijateľným rizikom. Pozri [Quality gates a approvals](docs/05-ci-cd-and-release/quality-gates-and-approvals.md).

## Blue-green deployment

Deployment stratégia s dvoma oddelenými produkčne relevantnými targetmi, kde sa nová verzia pripraví v neaktívnej farbe a následne sa na ňu riadene presmeruje traffic. Pozri [Blue-green deployment](docs/05-ci-cd-and-release/blue-green-deployment.md).

## Blue/Green Deployment — RDS

RDS workflow pre vytvorenie synchronizovaného staging environmentu a riadený switchover pri podporovaných engine a configuration zmenách. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## Blue/Green switchover subject

Versionovaný blue a green RDS topology, replication state, engine/schema/parameter delta, cutover preconditions, application/proxy endpoints a post-write rollback eligibility. Pozri [Amazon RDS](docs/11-cloud-and-aws/rds.md).

## Bootstrap capability gate

Podmienka, ktorá drží nový Node mimo bežného workload scheduling-u, kým critical DaemonSet capabilities neprejdú node-local canary a acceptance testom. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## Bootstrap configuration

Minimálna počiatočná konfigurácia potrebná na bezpečné pripojenie targetu k dlhodobému management workflowu, napríklad identity, trusted CA, management transport a inventory registration. Pozri [Terraform vs. Ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md).

## Bootstrap token — kubeadm

Časovo obmedzený credential používaný pri kubeadm node discovery a TLS bootstrap workflowe; musí overovať CA identity a nesmie byť dlhodobo uložený. Pozri [Cluster installation a lifecycle](docs/09-kubernetes/cluster-installation-lifecycle.md).

## Bound ServiceAccount token

Časovo obmedzený ServiceAccount bearer token vytvorený cez TokenRequest API, typicky viazaný na audience a Pod/object identity a projected kubeletom do workloadu. Pozri [ServiceAccount](docs/09-kubernetes/serviceaccount.md).

## Bound token subject

Konkrétny ServiceAccount token identifikovaný issuerom, audience, expiry, object bindingom a bezpečným fingerprintom. Pozri [ServiceAccount](../docs/09-kubernetes/serviceaccount.md).

## Bounded dimension

Telemetry dimension s malým, riadeným a relatívne stabilným počtom možných hodnôt. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Bounded reconcile transition

Jeden obmedzený, rekonštruovateľný krok control loopu, napríklad ensure finalizer, create/adopt external resource, update owned fields alebo verify cleanup, po ktorom sa state znovu pozoruje. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Bounded telemetry failure

Failure contract, pri ktorom telemetry export, buffering alebo backend outage nespôsobí nekontrolované blokovanie business threadu ani vyčerpanie application resources. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

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

## Build context subject

Identita build contextu zahŕňajúca source type, root/ref/commit, effective ignore rules, expected file inventory, named contexts, submodules a relevantné metadata. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Build definition

Versionovaný contract build procesu zahŕňajúci workflow, scripts, toolchain, environment, flags, inputs a target platform. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Build driver — Buildx

Konfigurácia určujúca, kde a ako beží BuildKit backend, napríklad `docker`, `docker-container`, Kubernetes alebo remote driver. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Build exporter — BuildKit

Komponent určujúci výsledný output build-u, napríklad registry image, local Docker image store, OCI artifact, tar alebo local filesystem. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Build frontend — BuildKit

Parser a translator, ktorý premieňa Dockerfile alebo iný build language na interný BuildKit graph. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Build graph node subject

Identita jednej build operation zahŕňajúca frontend semantics, instruction, parent result, sources, mounts, args, platform a execution options. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Build metadata — SemVer

Informácie za znakom `+` v Semantic Versioning verzii, napríklad build number alebo commit SHA. Neovplyvňujú SemVer version precedence. Pozri [Semantic Versioning](docs/05-ci-cd-and-release/semantic-versioning.md).

## Build once

Princíp vytvoriť pre konkrétny candidate jeden immutable artifact a ten istý artifact následne testovať a promovať medzi prostrediami. Pozri [Continuous Integration](docs/05-ci-cd-and-release/continuous-integration.md).

## Build once, promote many

Delivery princíp, pri ktorom sa source zostaví raz do immutable artifactu a rovnaký digest sa overuje a promotionuje cez všetky environments. Pozri [Trigger, artifact a cache](docs/05-ci-cd-and-release/trigger-artifact-cache.md).

## Build platform

Systém vykonávajúci build definitions, získavajúci inputs a vytvárajúci artifacts a provenance; predstavuje kritickú supply-chain trust boundary. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Build provenance

Attestation viažuca artifact digest na builder identity, build type, source revision, inputs a relevantné invocation metadata. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Build publication acceptance

Verdict potvrdzujúci, že exact build subject bol exportovaný do požadovaného destinationu, registry read-back obsahuje complete artifact graph a platform inventory a všetky požadované evidence patria publikovanému subjectu. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

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

## Builder node subject

Identita jedného BuildKit node-u zahŕňajúca endpoint, worker, BuildKit version/configuration, driver, platform capabilities, kernel/runtime, snapshotter, cache access, credentials a trust classification. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Builder state lifecycle

Lifecycle content store-u, snapshots, cache records, active leases, temporary exports, logs, node capacity, retention, garbage collection a retirement konkrétnej builder instance. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Builder trust domain

Izolovaná bezpečnostná oblasť pre build workloads, cache a credentials; untrusted pull-request buildy nemajú zdieľať release signing alebo production registry oprávnenia. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## BuildKit

Moderný container build backend vykonávajúci dependency graph, content-aware cache, build mounts, exporters, multi-platform outputs a attestations. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## BuildKit entitlement subject

Explicitná identita širšej build authority, napríklad host networking alebo insecure execution mode, viazaná na exact build subject, builder, requester, purpose, audit a expiration. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## BuildKit release subject

Rekonštruovateľná identita release build-u spájajúca source, frontend, contexts, base a dependency subjects, selected target, builder/nodes, platforms, caches, secrets references, exporters a expected evidence inventory. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

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

## Business-compatible recovery — Helm

Recovery verdict, pri ktorom technical release state, durable data, event/contracts, external integrations a pôvodný business outcome tvoria vzájomne kompatibilný celok. Technicky úspešný manifest rollback bez spracovateľného backlogu nie je business-compatible recovery. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Business-dirty recovery point

Technicky validný a restore-nuteľný recovery point, ktorý už obsahuje logical corruption, attacker changes alebo business-inconsistent state. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Business error population

Množina valid operations klasifikovaných podľa final caller alebo business outcome-u vrátane timeoutov, partial, degraded, silent a unknown výsledkov. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Business idempotency boundary

Stable operation identity a uniqueness/reconciliation contract pokrývajúci database changes aj external side effects, nie iba jeden local table insert. Pozri [Amazon RDS](docs/11-cloud-and-aws/rds.md).

## Business Impact Analysis — BIA

Proces určujúci kritické business capabilities, dopad výpadku, maximálne tolerované prerušenie, data-loss toleranciu, dependencies a priority obnovy. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Business-outcome lens

Custom Well-Architected lens, ktorá pridáva domain-specific failure scenarios, evidence a acceptance criteria viazané na business capability. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Business-outcome observation

Telemetry alebo validation merajúca final caller-visible či business-visible correctness a completion, nie iba interný process, target alebo HTTP acceptance stav. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Business recovery subject

Exact business capability, primary/recovery account a Region, application/data/trust generations, RTO, RPO, minimálna capacity a forbidden outcomes použité na DR rozhodovanie. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## cache behavior — CloudFront

Ordered distribution rule mapujúca path pattern na origin a definujúca viewer protocol, allowed methods, cache policy, origin request policy, headers a private-content behavior. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Cache — CI/CD

Odstrániteľná optimalizácia pipeline na znovupoužitie dependencies alebo intermediate build dát. Pipeline musí zostať korektná aj pri cache miss alebo eviction. Pozri [Trigger, artifact a cache](docs/05-ci-cd-and-release/trigger-artifact-cache.md).

## Cache-Control

HTTP response/request header definujúci freshness, revalidation, storage a shared/private cache policy. Pozri [HTTP](docs/02-networking-and-web/http.md).

## Cache decision subject — BuildKit

Rozhodnutie spájajúce build node, cache key, cache source/trust domain, hit alebo miss, reused result, platform, timestamp a export destination. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Cache freshness gap

Stav, keď je cached result technicky validný podľa key, ale nepozoroval mutable external input alebo zámerný security/update event. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## cache hit ratio — CloudFront

Podiel requests obslúžených z CloudFront cache bez potreby fetchu z originu; ovplyvňuje latency, origin load a cost. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Cache invalidation — Docker build

Stav, keď zmena instruction, parent resultu alebo relevantného inputu zmení cache key a builder musí príslušný graph node znovu vykonať. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Cache key

Identifikátor cache odvodený zo všetkých významných vstupov, napríklad OS, architecture, toolchain version, lockfile hash a build configuration. Pozri [Trigger, artifact a cache](docs/05-ci-cd-and-release/trigger-artifact-cache.md).

## cache key — CloudFront

Kombinácia pathu a vybraných query strings, headers, cookies alebo compression variantu, podľa ktorej CloudFront rozhoduje, či requests zdieľajú cached response. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Cache-key identity

Path a selected query/header/cookie/compression inputs, podľa ktorých CloudFront rozhodne, či dve viewer requests môžu bezpečne zdieľať jednu cached representation. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Cache mount — Dockerfile

Persistentnejší pomocný directory pripojený počas `RUN --mount=type=cache`, napríklad pre compiler alebo package-manager cache; môže byť odstránený a nesmie ovplyvňovať correctness build-u. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Cache poisoning

Stav, keď nedôveryhodný alebo chybný pipeline uloží cache, ktorú neskôr použije dôveryhodnejší workflow, čím môže ovplyvniť build alebo spustiť škodlivý obsah. Pozri [Trigger, artifact a cache](docs/05-ci-cd-and-release/trigger-artifact-cache.md).

## Cache poisoning path

Trust-boundary failure, pri ktorom nedôveryhodný writer ovplyvní shared build cache a release build reuseuje podvrhnutý result. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## cache policy — CloudFront

Policy určujúca cache-key inputs a minimum, default a maximum TTL pre CloudFront cache behavior. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Cache-sync boundary — Kubernetes controller

Prechod, pri ktorom controller potvrdí initial list/informer synchronization pred spustením workers alebo leader-ready behavior; nedodržanie môže interpretovať neúplnú cache ako chýbajúci state. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Cache trust and freshness verdict

Samostatné rozhodnutie potvrdzujúce, že cached result pochádza z povoleného writer trust domainu, patrí správnemu platform/node subjectu a spĺňa požadovanú freshness alebo controlled-refresh policy. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Cache trust namespace — GitLab CI

Oddelený cache key/prefix a write policy podľa trust contextu, napríklad fork, non-protected, protected alebo release. Zabraňuje tomu, aby menej dôveryhodný writer ovplyvnil citlivejší build. Pozri [Artifacts a cache](docs/06-gitlab/artifacts-and-cache.md).

## Calendar versioning

Versioning schéma odvodená primárne z kalendárneho dátumu alebo release cadence, napríklad `2026.07.21`. Pozri [Artifact versioning](docs/05-ci-cd-and-release/artifact-versioning.md).

## Callback plugin — Ansible

Plugin spracúvajúci execution events a výsledky pre console output, logs, profiling alebo external observability integrations. Pozri [Ansible architecture](docs/07-infrastructure-as-code-and-configuration-management/ansible-architecture.md).

## CALMS

DevOps rámec Culture, Automation, Lean, Measurement a Sharing. Pozri [CALMS framework](docs/00-foundations/calms.md).

## Canary analysis

Automatizované alebo riadené porovnanie novej verzie s baseline či kontrolnou skupinou podľa technických, funkčných a business metrík počas obmedzeného rollout-u. Pozri [Continuous Deployment](docs/05-ci-cd-and-release/continuous-deployment.md).

## Canary capability verdict — Kubernetes upgrade

Verdikt, že target control-plane, add-on alebo Node cohort poskytuje požadované API, network, storage, security, telemetry a business capabilities pred širším rolloutom. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Canary cohort

Stabilná skupina requestov, používateľov, tenantov alebo instances vystavená novej verzii pred širšou promotion. Pozri [Canary deployment](docs/05-ci-cd-and-release/canary-deployment.md).

## Canary deployment

Deployment stratégia postupne zvyšujúca produkčnú exposure novej verzie pri súbežnom porovnávaní so stable baseline a explicitných promotion/abort kritériách. Pozri [Canary deployment](docs/05-ci-cd-and-release/canary-deployment.md).

## Canary experiment subject

Presná identity jedného canary decisionu tvorená stable a canary release manifestom, rendered configom, feature-flag revision, cohort policy a saltom, rollout krokom, metrics query revision, analysis policy a observation window. Pozri [Canary deployment](docs/05-ci-cd-and-release/canary-deployment.md).

## Canary node pool

Malá skupina Nodes s novou Kubernetes, OS, runtime alebo add-on verziou použitá na overenie compatibility pred širším rolloutom. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Canary OU

Obmedzený Organizations scope používaný na staged policy a baseline validation pred širším attachmentom na production OUs alebo root. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Canary release

Postupné sprístupnenie novej verzie malej časti trafficu alebo používateľov s porovnávaním technických a business signálov pred širšou promotion. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Candidate integration state

Presný výsledný source tree, ktorý by po integrácii vznikol, typicky reprezentovaný synthetic merge alebo merge-queue SHA a overovaný proti aktuálnemu targetu. Pozri [Continuous Integration](docs/05-ci-cd-and-release/continuous-integration.md).

## Candidate mechanism evaluation

Posúdenie answer option podľa mechanizmu, scope-u, completeness, constraint fidelity, failure modelu, trade-offu a forbidden outcomes. Pozri [CloudOps domain review a timed reasoning](docs/11-cloud-and-aws/cloudops-domain-review-timed-reasoning.md).

## Canonical symptom page

Jediný authoritative page pre konkrétny user-facing symptom, ku ktorému cause signals slúžia ako investigation evidence namiesto duplicate paging paths. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Capability-based security

Model, v ktorom držanie konkrétnej obmedzenej capability alebo reference oprávňuje principal vykonať presne definovanú operáciu bez broad ambient authority. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## Capability-conditioned render — Helm

Render generation, ktorej output závisí od explicitného Kubernetes/API capability inventory alebo live cluster discovery. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Capability confidentiality

Confidentiality property citlivej capability, pri ktorej principal nesmie secret alebo key iba čítať, ale ani neobmedzene používať signing, decryption, impersonation či export operation. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Capability drop — container

Runtime policy odstraňujúca Linux capabilities z process credential sets, ideálne drop-all s explicitným pridaním iba potrebných oprávnení. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Capability inventory — Kubernetes workload security

Explicitný zoznam kernel, filesystem, network, device, host a API operations, ktoré workload potrebuje; používa sa na odvodenie minimálneho runtime authority contractu. Pozri [SecurityContext a Pod Security](../docs/09-kubernetes/securitycontext-pod-security.md).

## Capability — Linux capability

Samostatná časť tradičných root oprávnení, napríklad `CAP_NET_BIND_SERVICE`. Pozri [Linux capabilities](docs/01-linux-and-systems/linux-capabilities.md).

## Capacity acceptance verdict

Closure dôkaz, že capacity zmena zvýšila successful business throughput, zachovala downstream budgets, bezpečný scale-in a definovaný failure-domain outcome bez forbidden duplicít alebo straty. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Capacity cliff

Bod, pri ktorom malé ďalšie zvýšenie demandu spôsobí prudký rast queueing, latency alebo errors, pretože systém vyčerpal effective capacity. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Capacity headroom

Rezervovaná nevyužitá kapacita potrebná na absorpciu burstu alebo presun trafficu pri zlyhaní časti systému, napríklad jednej Availability Zone. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Capacity headroom — observability

Rozdiel medzi aktuálnym demandom alebo využitím a effective capacity po zohľadnení failoveru, limits a unavailable resources. Pozri [USE method](docs/12-observability/use-method.md).

## Capacity lifecycle subject

Versionovaná identita business demandu, workload unit, compute/data/dependency capacity, failure-domain inventory, scaling policy, metric contract a požadovaného business outcome-u. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Capacity realization — containers

Premena workload desired count-u na skutočne dostupný compute, memory, architecture, ENI/Pod IP, port, storage, AZ a quota capacity contract. Pozri [Amazon ECS a Amazon EKS](docs/11-cloud-and-aws/ecs-eks.md).

## Capacity Rebalancing — EC2 Auto Scaling

Auto Scaling capability, ktorá môže proaktívne spustiť náhradu Spot Instance pri zvýšenom interruption risku, pričom workload stále potrebuje drain a idempotentný recovery model. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Capacity-risk verdict

Rozhodnutie, či aktuálna saturation, scaling delay a failover headroom predstavujú imminent risk pre caller outcome alebo error budget. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Capacity test

Performance test hľadajúci maximálny udržateľný workload pri definovaných SLO a bezpečnostnej rezerve. Pozri [Performance, load a stress tests](docs/04-testing-and-quality/performance-load-stress-tests.md).

## CAPEC

MITRE Common Attack Pattern Enumeration and Classification; katalóg opakovateľných attack patterns použiteľný ako threat-modeling knowledge source, nie ako náhrada konkrétneho system modelu. Pozri [Threat modeling](docs/13-security-and-identity/threat-modeling.md).

## Capturing group — regex

Časť regular expression uzavretá v zátvorkách, ktorá zachytáva matched substring pre ďalšie spracovanie. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Cardinality

Počet unikátnych hodnôt alebo kombinácií dimensions, ktoré vytvárajú time series, log streams, indexed terms alebo ďalšie telemetry identities. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Cardinality acceptance verdict

Dôkaz, že active identities, churn, backlog, query cost a alerts zostávajú pod budgetom, critical signals sú kompletné a forbidden dimensions sa nevrátili po rollout-e alebo restart-e. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Cardinality budget

Explicitný limit a očakávaný growth model pre series, streams, indexed values alebo attributes per service, metric, tenant alebo backend. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Cardinality-budget generation

Versionovaný allowed-dimension, expected-value, active-count, churn, tenant quota, retention, cost a exception contract konkrétneho telemetry signal-u. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Cardinality containment

Minimálny auditovaný runtime zásah, ktorý zastaví tvorbu nových problematických identities a chráni platformu bez neanalyzovaného odstránenia critical evidence. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Cardinality incident

Prevádzkový incident, pri ktorom nekontrolovaný rast telemetry identities alebo indexed values ohrozuje ingestion, memory, storage, query výkon alebo cost. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Cardinality recovery generation

Authoritative producer, schema, allowlist, aggregation a runtime-limit zmena, ktorá nahradí emergency containment a prejde dependency, cost a restart validation. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Cardinality subject

Exact producer, release, tenant, signal/backend, identity model, dimensions, active count, churn, budget, dependencies a observation window analyzovanej cardinality. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Cardinality — telemetry

Počet unikátnych kombinácií labels alebo attributes; vysoká alebo neobmedzená cardinality môže výrazne zvýšiť memory, storage, query cost a destabilizovať telemetry pipeline. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Catastrophic backtracking

Patologické správanie backtracking regex engine-u, pri ktorom ambiguous nested pattern spôsobí extrémny čas spracovania non-matching vstupu. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Catch-up budget — CronJob

Policy obmedzujúca počet, concurrency a downstream load missed scheduled runs spustených po controller alebo control-plane recovery. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Causal amplifier — CloudOps incident

Sekundárny configuration alebo automation factor, ktorý nezaložil primary defect, ale zväčšil jeho scope, duration alebo business impact. Pozri [CloudOps troubleshooting drills](docs/11-cloud-and-aws/cloudops-troubleshooting-drills.md).

## Causal CloudOps hypothesis

Falsifiable tvrdenie `cause → mechanism → predicted observations`, ktoré vysvetľuje exact incident subject a možno ho odlíšiť od konkurujúcich hypotéz. Pozri [CloudOps troubleshooting drills](docs/11-cloud-and-aws/cloudops-troubleshooting-drills.md).

## Causal risk statement

Risk description spájajúci cause, failure mechanism a konkrétny business/technical impact namiesto vágneho control alebo checklist findingu. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## CEL policy

Policy vyjadrená pomocou Common Expression Language, napríklad v Kubernetes ValidatingAdmissionPolicy alebo MutatingAdmissionPolicy. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Certificate

X.509 objekt viažuci public key na identity claims, validity interval, usage a issuer signature. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## Certificate chain

Postupnosť leaf a intermediate certificates, ktorú klient overuje smerom k dôveryhodnému root CA v trust store. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## Certificate lifecycle — Kubernetes

Riadenie vydania, distribúcie, expirácie, obnovy, reloadu a zrušenia control-plane, etcd, kubelet a administrator certificates. Pozri [Cluster installation a lifecycle](docs/09-kubernetes/cluster-installation-lifecycle.md).

## Certificate loaded generation

Certificate/trust material skutočne načítaný konkrétnym API serverom, kubeletom, etcd memberom alebo klientom; môže zaostávať za file generation na disku. Pozri [Cluster installation a lifecycle](../docs/09-kubernetes/cluster-installation-lifecycle.md).

## Certification readiness subject

Exact kombinácia exam-guide generation, practice source/set identity, domain distribution, score, confidence profile, timing a linked practical evidence používaná pre readiness decision. Pozri [AWS Certified CloudOps Engineer – Associate](docs/11-cloud-and-aws/cloudops-engineer-associate-soa-c03.md).

## cgroup — Control group

Kernel mechanizmus na hierarchické zoskupovanie procesov a riadenie ich CPU, memory, I/O a process-count resources. Pozri [cgroups](docs/01-linux-and-systems/cgroups.md).

## Cgroup identity — container

Identita resource-control boundary zahŕňajúca cgroup path/ID, hierarchy, controller policy, process membership, limits, counters a pressure/events. Pozri [Namespaces, cgroups a capabilities](docs/08-container-fundamentals-and-docker/namespaces-cgroups-capabilities.md).

## Cgroup memory OOM subject

Konkrétny Pod/container cgroup, memory boundary, usage a `memory.events` generácia, v ktorej kernel ukončil process pre local cgroup memory limit. Pozri [Requests, limits a QoS](../docs/09-kubernetes/requests-limits-qos.md).

## Cgroup OOM — container

Ukončenie procesu pre memory pressure alebo limit v jeho cgroup boundary, ktoré nemusí znamenať vyčerpanie celej host memory. Pozri [Namespaces, cgroups a capabilities](docs/08-container-fundamentals-and-docker/namespaces-cgroups-capabilities.md).

## Cgroup runtime generation

Effective CPU, memory a ďalšie resource controls realizované kubeletom/runtime-om pre konkrétny Pod a container ID. Pozri [Requests, limits a QoS](../docs/09-kubernetes/requests-limits-qos.md).

## Cgroup v2

Unified Linux control-group hierarchy aplikujúca resource accounting, limits a distribution cez CPU, memory, I/O a PIDs controllers. Pozri [Namespaces, cgroups a capabilities](docs/08-container-fundamentals-and-docker/namespaces-cgroups-capabilities.md).

## Change budget — Ansible

Explicitný limit alebo allowlist opakovaných zmien povolených pri idempotency teste; všetky ostatné recurring changes sa považujú za chybu alebo drift. Pozri [Ansible idempotencia](docs/07-infrastructure-as-code-and-configuration-management/ansible-idempotency.md).

## Change fail rate

Podiel deploymentov, ktoré spôsobia degradáciu služby a vyžadujú nápravu. Pozri [DORA Metrics](docs/00-foundations/dora-metrics.md).

## Change lead time

Čas od vzniku sledovanej zmeny po jej úspešný deployment do produkcie. Pozri [DORA Metrics](docs/00-foundations/dora-metrics.md).

## Change subject — IaC

Presná identita infra zmeny zahŕňajúca source revision, resolved toolchain a dependencies, effective inputs, backend/state lineage a serial, target account/region, workload identity, saved plan a policy/approval context. Pozri [Infrastructure as Code principles](docs/07-infrastructure-as-code-and-configuration-management/infrastructure-as-code-principles.md).

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

## Chart artifact generation

Immutable packaged alebo OCI chart artifact vytvorený z konkrétneho source commit-u, dependency locku a build workflowu a identifikovaný version/digest identity. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

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

## Checkpoint subject — batch

Versionovaný durable progress state jedného logical runu, partition alebo work itemu spolu s owner epoch, input generation a result lineage. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Cherry-pick

Operácia, ktorá aplikuje zmenu vybraného commitu na aktuálny tip a vytvorí nový commit s novým parentom a object ID. Pozri [Cherry-pick a stash](docs/03-git-and-automation/cherry-pick-and-stash.md).

## Child module — Terraform

Reusable Terraform konfigurácia volaná z root alebo iného child modulu cez `module` block; jej resources sú súčasťou graphu a state-u caller root module runu. Pozri [Modules](docs/07-infrastructure-as-code-and-configuration-management/modules.md).

## Child pipeline

Samostatný pipeline run vytvorený parent pipelineom pre component, matrix časť alebo dynamicky generovaný workflow, s explicitnými input/output a failure-propagation pravidlami. Pozri [Reusable a parallel pipelines](docs/05-ci-cd-and-release/reusable-and-parallel-pipelines.md).

## Child-ReplicaSet ownership

Vzťah, v ktorom Deployment vlastní ReplicaSet revision a autoritatívne riadi jej scale počas rollout-u; manual write na child ReplicaSet môže vyšší controller prepísať. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md) a [Deployment](docs/09-kubernetes/deployment.md).

## Chunk-delivery state — Fluent Bit

Runtime stav buffered chunku voči jednému alebo viacerým outputs, napríklad queued, flushing, retrying, acknowledged alebo dropped. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Chunk — Fluent Bit

Interná jednotka zoskupujúca telemetry records na buffering, routing a output flush. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Chunk generation — Loki

Versionovaný compressed object obsahujúci log entries jedného streamu za časový interval a publikovaný spolu s index reference. Pozri [Loki](docs/12-observability/loki.md).

## Chunk — Loki

Komprimovaný container log entries jedného streamu za určitý časový interval uložený typicky v object storage. Pozri [Loki](docs/12-observability/loki.md).

## Chunk utilization — Loki

Miera naplnenia Loki chunks; príliš veľa malých streamov vytvára underutilized chunks a zvyšuje storage/index overhead. Pozri [Loki](docs/12-observability/loki.md).

## CI/CD component — GitLab

Versionovaný reusable pipeline contract publikovaný v GitLabe a používaný cez `include:component` s explicitnou verziou, inputs a definovaným behaviorom. Pozri [GitLab CI/CD syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md).

## `CI_JOB_TOKEN`

Krátkodobá GitLab job identity používaná na podporované API, artifact, package, registry alebo cross-project operácie podľa explicitného access modelu. Pozri [Variables a secrets](docs/06-gitlab/variables-and-secrets.md).

## CIA acceptance verdict

Dôkaz, že chránený asset zachoval required confidentiality, integrity a availability, incident bol reconciled a forbidden aj residual-risk outcomes boli explicitne vyhodnotené. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## CIA security subject

Exact business capability, assets, identities, data/config generations, trust boundaries, impact thresholds, controls a evidence scope analyzovanej CIA otázky. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

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

## CKA exam subject

Versionovaný certification a environment contract obsahujúci exam delivery model, čas, Kubernetes minor version, domain weights, povolené referencie a dátum overenia oficiálnych pravidiel.

## CKA troubleshooting drill

Časovo ohraničený fault-injection scenár merajúci root-cause accuracy, minimálnu opravu a hard validation Kubernetes failure-u. Pozri [CKA troubleshooting drills](docs/10-helm-and-cka/cka-troubleshooting-drills.md).

## CKA troubleshooting subject

Exact cluster/object/process/data/flow identity, ku ktorej patria symptóm, scope, timeline, owner graph, evidence a expected outcome.

## Claimant

Entita, ktorá sa pokúša preukázať kontrolu nad authenticatorom a byť rozpoznaná ako konkrétny subscriber alebo principal. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Class-controller ownership

Contract, ktorým IngressClass alebo GatewayClass vyberá controller implementation a jej capability/lifecycle ownership. Pozri [Ingress a Gateway API](../docs/09-kubernetes/ingress-gateway-api.md).

## Clean image rebuild

Nový build z trusted source a kontrolovaných inputs po odstránení kompromitovaného source, secret alebo cache pathu; vytvára nový digest a nové evidence. Pozri [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md).

## Clean recovery candidate

Recovery point alebo manifest set preukázateľne vytvorený pred corruption/compromise boundary a vhodný pre business recovery po zohľadnení RPO a reconciliation. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Clean restore verdict

Výsledok restore testu potvrdzujúci integrity/decryption backupu, správnu data identity, ownership, application recovery, business invariant a RPO/RTO. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## Clean-room build

Build vykonaný bez dôvery v existujúcu local alebo external cache, používaný na overenie reproducibility, úplnosti dependencies a absencie skrytých cache assumptions. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Clean-room build evidence

Dôkaz build-u bez reuse relevantnej cache spolu s porovnaním inputs, builder/toolchain identity, final digestu, SBOM a runtime verdictu. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Clean-room recovery

Obnova do izolovaného a kontrolovaného prostredia pred production promotion, aby sa overila integrita a zabránilo opätovnému kompromitovaniu obnovených dát. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Clean trust generation

Po incidente novo vydaná a izolovaná generácia identities, credentials, certificates, keys a policies, ktorá nie je iba replikou potenciálne kompromitovaného primary state-u. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Cleanup graph — AWS lab

Dependency-aware poradie retention decisions, resource deletions a asynchronous observations potrebné na odstránenie celej lab generation. Pozri [CloudOps hands-on labs](docs/11-cloud-and-aws/cloudops-hands-on-labs.md).

## Cleanup-incomplete verdict

Verdikt testu alebo automation runu, pri ktorom hlavné assertions prešli, ale vytvorené resources, credentials, temporary state alebo iné side effects neboli úplne odstránené. Nie je ekvivalentný plnému success-u. Pozri [Terraform testing a policy](docs/07-infrastructure-as-code-and-configuration-management/terraform-testing-and-policy.md).

## Cleanup-incomplete verdict — GitLab Runner

Execution verdict označujúci, že script alebo output môže mať známy výsledok, ale worker runtime, workspace, procesy alebo credentials neboli dôveryhodne odstránené. Vyžaduje containment a reconciliation pred retry alebo ďalším použitím poolu. Pozri [Runners a executors](docs/06-gitlab/runners-and-executors.md).

## Cleanup residue

Resource, attachment, data, policy, subscription alebo recurring charge, ktorý nečakane prežil deklarovaný lab cleanup. Pozri [CloudOps hands-on labs](docs/11-cloud-and-aws/cloudops-hands-on-labs.md).

## Cleanup transition

Povinný pipeline alebo job transition, ktorý po success, failure, timeout alebo cancellation uvoľní locks, credentials a temporary resources a zachová dostupné evidence. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## ClickOps

Primárna správa infraštruktúry manuálnymi zmenami v UI alebo konzole bez versionovaného, reviewovaného a reprodukovateľného change pathu. Pozri [Infrastructure as Code principles](docs/07-infrastructure-as-code-and-configuration-management/infrastructure-as-code-principles.md).

## Client authentication

Mechanizmus, ktorým confidential OAuth client preukazuje svoju identitu token endpointu, napríklad secretom, private-key JWT alebo mTLS. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Client Credentials grant

OAuth machine-to-machine grant, pri ktorom client získava token vo vlastnom identity kontexte bez používateľskej delegation. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Client — OAuth

Aplikácia požadujúca token a používajúca ho voči resource serveru. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Client-Service flow subject

Presný request/connection path od client Podu a Node-u cez Service VIP a node dataplane ku konkrétnemu endpointu a reverse pathu. Pozri [Service a EndpointSlice](../docs/09-kubernetes/service-endpointslice.md).

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

## Cloud deployment subject

Versionovaná identita umiestnenia capability zahŕňajúca public/private/hybrid domains, accounts, sites, networks, identity, DNS, connectivity, data a management generations. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Cloud financial management

Disciplína merania, alokácie, plánovania, kontroly a optimalizácie cloud spendu podľa business value a operational trade-offov. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Cloud portability

Schopnosť presunúť workload medzi prostrediami vrátane source, runtime, data, identity, network, observability a operational contracts, nie iba container image-u. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Cloud reconciliation subject

Identita cloud-controller alebo provider operation zahŕňajúca cluster, controller identity, object UID/generation, cloud account/region, external resource ID, request ID, desired fields a provider API outcome. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## Cloud service model

Model opisujúci rozdelenie prevádzkovej a bezpečnostnej zodpovednosti medzi providerom a zákazníkom naprieč infraštruktúrou, platformou, aplikáciou a dátami. Pozri [IaaS, PaaS a SaaS](docs/11-cloud-and-aws/iaas-paas-saas.md).

## Cloud service-model subject

Konkrétny service contract viazaný na business capability, provider/customer responsibility boundary, effective configuration, evidence, recovery a exit model; nie iba označenie IaaS, PaaS alebo SaaS. Pozri [IaaS, PaaS a SaaS](docs/11-cloud-and-aws/iaas-paas-saas.md).

## CloudFront Functions

Lightweight JavaScript edge runtime pre viewer-request a viewer-response transformácie s nízkou latency a obmedzeným execution modelom. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## CloudOps closure verdict

Rozhodnutie, že original outcome, forbidden outcomes, adjacent cohorts, second operation, evidence, earlier controls a residual risk spĺňajú incident acceptance contract. Pozri [CloudOps troubleshooting drills](docs/11-cloud-and-aws/cloudops-troubleshooting-drills.md).

## CloudOps domain gap map

Mapovanie aktuálnych SOA-C03 task statements na existujúce kapitoly, služby, hands-on laby, troubleshooting drilly a zostávajúce vedomostné medzery. Pozri [SOA-C03 guide](docs/11-cloud-and-aws/cloudops-engineer-associate-soa-c03.md).

## CloudOps incident subject

Exact incident identity zahŕňajúca account/Region/AZ, release/artifact, resource/config generations, business/data correlation, timeline a affected/unaffected cohorts. Pozri [CloudOps troubleshooting drills](docs/11-cloud-and-aws/cloudops-troubleshooting-drills.md).

## CloudOps lab subject

Exact lab identity zahŕňajúca outcome, forbidden outcomes, account/Region, caller, source generation, expected resources, cost guardrails, expiry a evidence destinations. Pozri [CloudOps hands-on labs](docs/11-cloud-and-aws/cloudops-hands-on-labs.md).

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

## Cluster capability acceptance

Verdikt, že current cluster generation poskytuje API read/write/watch, etcd quorum, Node execution, CNI/CSI/DNS, security policy, workload rollout a recovery capabilities. Pozri [Cluster installation a lifecycle](../docs/09-kubernetes/cluster-installation-lifecycle.md).

## Cluster decommission

Riadené ukončenie clusteru zahŕňajúce data retention, traffic/DNS, PV a cloud resources, credentials, audit evidence a bezpečné odstránenie hosts. Pozri [Cluster installation a lifecycle](docs/09-kubernetes/cluster-installation-lifecycle.md).

## Cluster DNS — Kubernetes

Cluster add-on poskytujúci DNS records pre Services a vybrané Pod identities a forwardujúci non-cluster queries na upstream resolvery. Pozri [Cluster DNS](docs/09-kubernetes/cluster-dns.md).

## Cluster-DNS Service subject

`kube-dns` Service UID/ClusterIP, EndpointSlice cohort a node dataplane path, cez ktorý Pod query dosiahne DNS backend. Pozri [Cluster DNS](../docs/09-kubernetes/cluster-dns.md).

## Cluster domain — Kubernetes

DNS suffix cluster-local service discovery namespace-u, často `cluster.local`, ale konfigurovateľný pri vytvorení clusteru. Pozri [Cluster DNS](docs/09-kubernetes/cluster-dns.md).

## Cluster generation — Kubernetes

Exact platform release tvorený infra/host image-om, Kubernetes a etcd verziami, kubeadm/component configom, PKI, Node pools, add-ons, policy a recovery-set generations. Pozri [Cluster installation a lifecycle](../docs/09-kubernetes/cluster-installation-lifecycle.md).

## Cluster-level logging

Architektúra, ktorá prenáša container, Node a control-plane logs do backendu s lifecycle a retenciou nezávislou od jednotlivých Podov a Nodes. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Cluster recovery set

Koordinovaný súbor etcd snapshotu, PKI, encryption/KMS materialu, component configs, infra/add-on source, image artifacts, application-data backups a runbooku potrebný na obnovu. Pozri [Cluster installation a lifecycle](../docs/09-kubernetes/cluster-installation-lifecycle.md) a [etcd backup a restore](../docs/09-kubernetes/etcd-backup-restore.md).

## Cluster-scoped resource — Kubernetes

Kubernetes resource, ktorého identity a API scope nie sú viazané na namespace, napríklad Node, Namespace alebo ClusterRole. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Cluster subject — Kubernetes

Identita clusteru zahŕňajúca API endpoint a CA, cluster/infrastructure identity, control-plane a etcd topológiu, Kubernetes version, node-pool generations, CRI/CNI/CSI, admission/policy a critical add-ons. Pozri [Kubernetes architecture](docs/09-kubernetes/kubernetes-architecture.md).

## Cluster-upgrade graph — EKS

Compatibility a transition graph zahŕňajúci EKS control plane, nodes/compute model, VPC CNI/CoreDNS/kube-proxy/CSI a ďalšie add-ons, controllers/operators/CRDs, admission, clients a workloads. Pozri [Amazon ECS a Amazon EKS](docs/11-cloud-and-aws/ecs-eks.md).

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

## CNI chain generation

Versionovaná kombinácia CNI configuration, plugin poradia a per-Node agent/dataplane state-u použitá pri `ADD` alebo `DEL` operácii. Pozri [CNI a NetworkPolicy](../docs/09-kubernetes/cni-networkpolicy.md).

## CNI chaining

Model, v ktorom sa počas jedného Pod network setupu vykoná viac CNI plugins v poradí, napríklad connectivity, port mapping, tuning alebo bandwidth policy. Pozri [CNI a NetworkPolicy](docs/09-kubernetes/cni-networkpolicy.md).

## CNI/IPAM operation subject

Identita Pod network setup alebo cleanup operácie zahŕňajúca Pod UID, sandbox/container ID, Node, CNI generation, network attachment, IPAM lease, interface, routes, request/result a cleanup verdict. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## CNI operation subject

Konkrétne CNI `ADD`, `CHECK` alebo `DEL` vykonanie viazané na runtime sandbox/container ID, network namespace, interface name a configuration generation. Pozri [CNI a NetworkPolicy](../docs/09-kubernetes/cni-networkpolicy.md).

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

## Cohort-aware Helm test

Release test, ktorý neoveruje iba jeden náhodný request, ale identifikuje všetky serving Pod alebo backend cohorts, ich image/configuration generations a rozloženie opakovaných requests. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Cohort differential diagnosis

Porovnanie jedného úspešného a jedného zlyhávajúceho subjectu podľa release, Node, zone, config, endpoint alebo telemetry generation s cieľom izolovať meniacu sa príčinu. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Cold start — Lambda

Invocation, pri ktorom Lambda musí pripraviť nové execution environment a vykonať runtime, extension a static initialization pred handlerom. Pozri [Lambda](docs/11-cloud-and-aws/lambda.md).

## Collection artifact subject — Ansible

Immutable identita publikovanej Ansible collection zahŕňajúca source revision, namespace a version, built artifact digest, publisher/provenance, resolved dependencies a podporovaný `ansible-core` contract. Pozri [Roles a collections](docs/07-infrastructure-as-code-and-configuration-management/roles-and-collections.md).

## Collection dependency — Ansible

Versionovaný vzťah collection k inej collection, ktorý ovplyvňuje resolved executable content, compatibility a supply-chain risk. Pozri [Roles a collections](docs/07-infrastructure-as-code-and-configuration-management/roles-and-collections.md).

## Collection subject — telemetry

Exact Node, Pod/container stream, local file alebo runtime source, collector Pod/config, offset a destination používané pri zbere signálu. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Collector agent

Telemetry Collector nasadený blízko workloadu alebo Node-u na lokálny príjem, enrichment, batching a export signals. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Collector distribution

Konkrétny build OpenTelemetry Collectora s definovanou množinou receivers, processors, exporters a extensions, napríklad core, contrib, vendor alebo custom distribution. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Collector distribution generation

Pinned OpenTelemetry Collector artifact a jeho exact receiver, processor, exporter a extension inventory vrátane component stability. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Collector gateway

Centralizovaná alebo tiered Collector vrstva používaná na routing, policy, tail sampling, tenant isolation a fan-out do backendov. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Collector offset generation

Durable checkpoint určujúci, po ktorú source file/inode alebo stream pozíciu bol record bezpečne spracovaný a potvrdený backendom. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Collector topology generation

Versionovaná agent, sidecar, gateway alebo tiered Collector architektúra vrátane routing, capacity, affinity, failure a tenant boundaries. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Collision domain

Oblasť zdieľaného Ethernet média, v ktorej môžu transmissions kolidovať. Pozri [Ethernet, MAC a ARP](docs/02-networking-and-web/ethernet-mac-arp.md).

## Color-specific telemetry

Metrics, logs a traces označené blue/green environmentom a artifact verziou tak, aby bolo možné analyzovať cutover a porovnať správanie oboch farieb. Pozri [Blue-green deployment](docs/05-ci-cd-and-release/blue-green-deployment.md).

## Combination-space estimate

Odhad potenciálnych a expected reálnych combinations dimensions pred zavedením telemetry schema change-u. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Combinatorial cardinality

Rast počtu telemetry identities spôsobený kombináciou viacerých dimensions, ktorých hodnoty sa navzájom násobia. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Combined release subject — Terraform a Ansible

Spoločná identita hybridného release-u viažuca Terraform plan/state/resource inventory, publikovanú host-contract generation, Ansible run subject, expected/verified fleet a application-runtime verification. Pozri [Terraform vs. Ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md).

## Command fluency — CKA

Schopnosť rýchlo a presne používať kubectl, shell, editor a cluster administration commands bez zbytočného hľadania syntaxe. Pozri [CKA timed labs](docs/10-helm-and-cka/cka-timed-labs.md).

## Command injection

Zraniteľnosť, pri ktorej neoverený vstup zmení syntax alebo spustí dodatočný príkaz. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md) a [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Commit object

Git object obsahujúci root tree snapshotu, parent commits, author/committer metadata a commit message. Pozri [Git object model](docs/03-git-and-automation/git-object-model.md).

## Commitment baseline — AWS cost

Forecast stabilného useful eligible usage po odstránení incident, retry, migration a temporary waste, používaný pred Savings Plan alebo reservation purchase. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Compatibility dimension

Jedna z vrstiev, v ktorých sa hodnotí backward compatibility, napríklad source, binary, schema, behavior, operational, security, data alebo performance contract. Version bump musí vychádzať z affected dimensions a consumer evidence, nie iba zo syntaktického diffu. Pozri [Semantic Versioning](docs/05-ci-cd-and-release/semantic-versioning.md).

## Compatibility graph — Kubernetes upgrade

Resolved vzťah medzi target Kubernetes verziou a etcd, Nodes, runtimes, add-ons, CRDs, webhooks, clients, workloads a persistent data contracts. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Compatibility matrix — deployment

Explicitná tabuľka určujúca, ktoré application, client, event a schema verzie môžu bezpečne koexistovať počas rollout-u a rollback window. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Compensating control

Alternatívny security control použitý na dosiahnutie porovnateľného zníženia risku, keď primárny control nie je možný alebo primeraný. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Competing hypothesis set — CKA

Malý súbor realistických kauzálnych vysvetlení viazaných na rovnaký incident subject.

## Complain mode

AppArmor režim, v ktorom sa porušenia profilu logujú, ale neblokujú. Pozri [SELinux a AppArmor](docs/01-linux-and-systems/selinux-and-apparmor.md).

## Complete artifact graph — OCI

Očakávaná množina image indexes, platform manifests, configs, layers a subject-bound signatures, provenance, SBOM alebo ďalších referrers potrebných pre release. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Complete evidence

Stav, pri ktorom sa vykonali všetky required controls a existujú všetky očakávané reports, shards, artifacts a tool statusy pre presný candidate. Pozri [Continuous Integration](docs/05-ci-cd-and-release/continuous-integration.md).

## Complete-path test — CloudOps

Overenie, že candidate answer pokrýva všetky required mechanism boxes od source/authorization cez realization po validation, nie iba jeden component. Pozri [CloudOps domain review a timed reasoning](docs/11-cloud-and-aws/cloudops-domain-review-timed-reasoning.md).

## Completion gap — RED

Rozdiel medzi accepted alebo started operation rate a final successful completion rate, ktorý môže signalizovať queueing, stuck workflow, dropped state alebo telemetry mismatch. Pozri [RED method](docs/12-observability/red-method.md).

## Completion index — Job

Stabilný index konkrétneho logical completion slotu pri Indexed Job-e, používaný na deterministické rozdelenie batch práce medzi Pody. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Completion-index mapping

Deterministická väzba Indexed Job completion indexu na business partition alebo work-item identity, typicky scoped logical run key-om. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Component metrics — Kubernetes

Prometheus-style metrics publikované API serverom, schedulerom, controller-managerom, kubeletom, etcd a ďalšími system components. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Component relationship — SBOM

Machine-readable väzba medzi SBOM elements, napríklad `dependsOn`, `contains`, `generatedFrom` alebo `distributedAs`. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## Component-stability inventory — OpenTelemetry

Zoznam použitých Collector components a signals s ich signal-specific stability, distribution availability a compatibility statusom. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Component template — search

Reusable časť index template-u obsahujúca mappings, settings alebo aliases pre Elasticsearch/OpenSearch index model podľa produktu. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Component test

Test celého deployovateľného komponentu cez jeho verejné rozhranie, pričom externé dependencies môžu byť nahradené controlled doubles. Pozri [Unit, integration a component tests](docs/04-testing-and-quality/unit-integration-component-tests.md).

## Compose acceptance subject

Spoločná identita resolved Compose modelu, projektu, container/image generations, resource inventory, one-shot verdictov, health a end-to-end business verification potrebná na prijatie deploymentu. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Compose container generation

Konkrétna container instance vytvorená z resolved service definition, identifikovaná Engine ID, config hashom, image digestom, project generation a health/runtime stavom. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Compose destructive scope

Množina project-owned containers, networks, volumes a orphan resources, ktoré môže zasiahnuť `down`, `down -v`, `--remove-orphans` alebo iný cleanup command. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

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

## Compose project generation

Versionovaný stav jedného Compose projektu viazaný na project name, Docker daemon/context, resolved model digest a vytvorené resource generations. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Compose resource ownership plan

Inventory určujúci pre každý network, volume, bind, image, config alebo secret, či ho vlastní Compose, external systém alebo daemon host a kto riadi preflight, retention a cleanup. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Compose service

Deklaratívna definícia workloadu v Compose modeli, z ktorej môže vzniknúť jedna alebo viac runtime container inštancií. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Compose source subject

Identita base a override files, includes/extends, active profiles, interpolation environment, project directory, Compose version a CLI options použitých na zostavenie modelu. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Compose Specification

Otvorený application-model specification pre multi-container services, networks, volumes, configs, secrets a súvisiace lifecycle metadata. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Compose trust model

Bezpečnostný model, podľa ktorého je Compose file privilegovaná executable configuration schopná spúšťať containers, mountovať host paths, pripájať devices a publikovať ports. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Compose volume identity

Effective physical volume object odvodený z Compose projectu a logical volume key alebo explicitného external name, spolu s environment, data ID a lifecycle ownerom. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## Composite alarm — CloudWatch

CloudWatch alarm kombinujúci boolean stav viacerých underlying alarmov na koreláciu, suppression alebo zníženie alert noise. Pozri [CloudWatch a CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## Composite CloudOps lab

Časovo ohraničený experiment pokrývajúci viac SOA-C03 domains, unknown failure diagnosis, bounded recovery, negative validation a full cleanup bez krokového návodu. Pozri [CloudOps hands-on labs](docs/11-cloud-and-aws/cloudops-hands-on-labs.md).

## Compute quota — Kubernetes

ResourceQuota limit agregovaných CPU, memory, ephemeral-storage alebo ďalších deklarovaných requests/limits v namespace. Pozri [ResourceQuota a LimitRange](docs/09-kubernetes/resourcequota-limitrange.md).

## Computed value — Terraform

Hodnota atribútu určená providerom alebo remote API, ktorá nemusí byť známa počas planu a môže sa zobraziť ako `known after apply`. Pozri [Terraform providers, resources a data sources](docs/07-infrastructure-as-code-and-configuration-management/terraform-providers-resources-data-sources.md).

## Concurrency budget — Lambda

Maximálny bezpečný počet concurrent invocations odvodený nielen od Lambda limitov, ale aj od database connections, provider quotas, network/NAT capacity, queue lease a business deadline-u. Pozri [AWS Lambda](docs/11-cloud-and-aws/lambda.md).

## Concurrency policy — CronJob

Pravidlo `Allow`, `Forbid` alebo `Replace`, ktoré určuje, ako CronJob reaguje, keď má začať nový scheduled run a predchádzajúci Job ešte beží. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Condition-based wait

Čakanie na explicitnú podmienku s deadline namiesto pevného sleepu. Znižuje timing flakiness a zrýchľuje test pri rýchlom výsledku. Pozri [Flaky tests a test data](docs/04-testing-and-quality/flaky-tests-and-test-data.md).

## Condition coverage

Coverage metrika sledujúca, či jednotlivé boolean podmienky nadobudli relevantné true a false výsledky. Pozri [Code coverage a quality gates](docs/04-testing-and-quality/code-coverage-and-quality-gates.md).

## Condition — Kubernetes

Štruktúrovaný status signál s typom, boolean-like stavom, reason, message a transition time, ktorý opisuje aktuálne významný aspekt resource state-u. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Confidence evidence — question review

Confidence označená pri answer selection pred známym výsledkom a používaná na rozlíšenie stable capability, guessing, knowledge gapu a high-confidence wrong modelu. Pozri [CloudOps domain review a timed reasoning](docs/11-cloud-and-aws/cloudops-domain-review-timed-reasoning.md).

## Confidentiality

Zachovanie autorizovaných obmedzení prístupu a disclosure informácií. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## ConfigMap

Namespaced Kubernetes API objekt pre necitlivé UTF-8 alebo binary configuration dáta používané Podmi cez environment alebo mounted volumes. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Configuration acceptance verdict

Dôkaz, že správny ConfigMap/Secret subject bol doručený a processom načítaný, schema a business test prešli a forbidden old alebo fallback state už nie je aktívny. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Configuration checksum — Kubernetes

Deterministický hash configuration contentu vložený do Pod template metadata, aby jeho zmena vytvorila novú workload revision a explicitný rollout. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Configuration drift — Terraform

Neželaný rozdiel medzi deklaráciami, ktoré majú reprezentovať rovnaký environment alebo policy, napríklad divergentné branches, repositories alebo neaplikované emergency zmeny. Pozri [Drift](docs/07-infrastructure-as-code-and-configuration-management/drift.md).

## Configuration identity — GitLab CI

Reprodukčný subject pipeline zahŕňajúci source SHA, pipeline source, root CI revision, resolved configuration digest, include/component identities, policy a variable context a runner/executor identity. Pozri [GitLab CI/CD syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md).

## Configuration lifecycle subject

Spoločná identita source generation, API object UID/version, workload template reference, Pod UID, delivery method, process-loaded generation a acceptance/cleanup state-u. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Configuration management

Riadenie požadovaného runtime stavu operačných systémov, aplikácií, zariadení alebo služieb pomocou opakovateľných a overiteľných zmien. Pozri [Terraform vs. Ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md).

## Configuration observation matrix

Mapovanie source, API object, Pod delivery, process state, security, rotation, readiness a business boundaries na ich subjects a observations. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Configuration recreate — container

Nahradenie container instance po zmene runtime environment alebo inej immutable container configuration, pretože už spustený process bežne neprevezme nové hodnoty automaticky. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Configuration rollout digest

Deterministická neplaintextová identity configuration contentu vložená do workload template-u alebo release manifestu s cieľom vytvoriť explicitnú Pod rollout generation. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Configuration source generation

Versionovaný approved input configuration pred vytvorením Kubernetes API objectu, napríklad Git commit, rendered manifest alebo external provider version. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Configuration subject — GitLab CI/CD

Presná identity pipeline compilation rozhodnutia tvorená source alebo candidate SHA, pipeline source, root CI revision, resolved include/component versions, resolved configuration digest, expected job inventory a relevantný runner/executor context. Pozri [GitLab CI/CD syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md).

## Configured control

Policy, resource, alarm, redundancy alebo runbook, ktorý existuje v deklarovanom/current state-e, ale ešte nemusí byť preukázane effective. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Conftest

Nástroj používajúci OPA/Rego na testovanie structured configuration, napríklad YAML, JSON alebo Terraform planov, pred runtime enforcementom. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Confused deputy

Situácia, v ktorej privileged komponent vykoná operáciu v prospech nesprávneho alebo neautorizovaného actora pre chýbajúci audience, subject alebo delegation binding. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Congestion control

Transportný mechanizmus upravujúci množstvo dát in flight podľa odhadovanej kapacity a congestion signálov network pathu. Pozri [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md).

## Connected/disconnected behavior

Explicitný contract určujúci, ktoré workload, identity, data a management operations pokračujú, fail-closed alebo sa bufferujú pri strate WAN alebo central cloud control plane-u. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Connection draining

Postup, pri ktorom sa backendu prestane posielať nový traffic, ale existujúce requests alebo connections dostanú čas na dokončenie. Pozri [Load balancing](docs/02-networking-and-web/load-balancing.md).

## connection draining — ELB

Riadené ukončovanie targetu, pri ktorom load balancer prestane posielať nové requests a ponechá existujúce connections alebo requests dobehnúť v rámci deregistration contractu. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## Connection plugin — Ansible

Plugin definujúci transport a remote execution semantics medzi control node a targetom, napríklad SSH, local, WinRM alebo network API connection. Pozri [Ansible architecture](docs/07-infrastructure-as-code-and-configuration-management/ansible-architecture.md).

## Conntrack

State table sledujúca network flows pre stateful firewall a NAT rozhodnutia. Pozri [NAT](docs/02-networking-and-web/nat.md) a [Firewally](docs/02-networking-and-web/firewalls.md).

## Conntrack — container networking

Kernel connection-tracking state používaný firewallom a NAT-om; jeho vyčerpanie môže blokovať nové connections pri stále funkčných existujúcich flows. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

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

## Consumer inventory — Terraform module

Evidencia module consumers, používaných versions, environments, owners, provider/Terraform constraints a podporovaných upgrade paths. Umožňuje bezpečné deprecation, security remediation a retirement starého contractu. Pozri [Modules](docs/07-infrastructure-as-code-and-configuration-management/modules.md).

## Consumer-loaded secret state

Secret version a credential generation skutočne načítaná konkrétnym processom, taskom, Lambda environmentom, sidecarom alebo connection poolom. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Consumer refresh gate — secret rotation

Evidence gate vyžadujúci, aby intended consumer cohorts načítali novú secret version, obnovili connections a úspešne autentizovali pred revocation old credentialu. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Container

Izolovaný runtime process alebo skupina procesov používajúca host kernel a oddelené views/resources cez namespaces, cgroups a security controls. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Container bridge network

Model, v ktorom veth pairs pripájajú container network namespaces k Linux bridge-u a host routing, firewall alebo NAT vrstve. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Container drift

Nezdokumentovaná runtime zmena vo writable layeri alebo container configuration, ktorá nie je súčasťou versionovaného image-u alebo deployment modelu a zanikne alebo sa zmení pri recreate. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Container environment

Sada environment variables dostupná runtime procesu po zlúčení image defaults a runtime overrides. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Container escape

Prelomenie container isolation boundary, pri ktorom process získa access k hostu alebo iným workloads. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Container exit code

Numerický status ukončenia PID 1 procesu; musí sa interpretovať spolu so signalom, OOM stavom, daemon/kernel logs a application contractom. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Container flow subject

Identita flowu zahŕňajúca source namespace/interface/address/port, destination, route, dataplane, pre/post-NAT tuple, policy generation, DNS answer a timestamp. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Container image

Content-addressed filesystem a runtime-metadata artifact používaný na vytvorenie container instance; typicky neobsahuje runtime kernel. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Container MTU

Maximum Transmission Unit platná na container packet path-e; nesúlad s bridge, tunnel alebo uplinkom môže spôsobiť partial connectivity. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Container network namespace

Linux namespace poskytujúci procesu vlastné interfaces, IPs, routes, sockets, loopback a network-state view. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Container orchestration subject

Versionovaná identita image digestu, ECS task/service alebo Kubernetes workload generation, configuration/secrets, scheduler, compute/network/storage capacity, workload identity, traffic cohort a business requestu. Pozri [Amazon ECS a Amazon EKS](docs/11-cloud-and-aws/ecs-eks.md).

## Container port

Port, na ktorom process počúva vo svojom network namespace; nemusí byť dostupný z hosta alebo externej siete. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Container replacement lifecycle

Model, v ktorom sa release realizuje novou exact image/runtime instance a odstránením starej pri oddelenom persistent state a service identity. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Container-restart subject — Kubernetes

Lifecycle jedného container instance restartu v rámci rovnakého Pod UID a spravidla rovnakého sandboxu, Pod IP a Pod-scoped volumes. Pozri [Pod](docs/09-kubernetes/pod.md).

## Container runtime

Software vrstva pripravujúca filesystem, namespaces, cgroups, process a lifecycle podľa runtime configuration alebo OCI štandardu. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Container Runtime Interface — CRI

gRPC contract medzi kubeletom a container runtime implementation pre Pod sandbox, container a image lifecycle. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## Container scanning — GitLab

Security scan konkrétneho container image digestu zameraný najmä na známe vulnerabilities v OS packages a podľa capability scanneru aj ďalšom image obsahu. Pozri [Security scanning](docs/06-gitlab/security-scanning.md).

## Container security baseline

Minimálna kombinácia trusted digestu, non-root usera, capability dropu, seccomp/LSM, read-only rootfs, limits, segmentation a short-lived identity. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Container security subject

Identita artifact a runtime security state-u zahŕňajúca digest, node/runtime, process authority, seccomp/LSM, mounts/devices, network, identity, secrets, resources a exceptions. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Container task subject

Identita low-level tasku zahŕňajúca containerd namespace/task ID, runtime/shim, PID, bundle/config, start/exit generation a väzbu na Docker object. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Container volume

Runtime-managed storage object s lifecycle oddeleným od containeru, ktorý však automaticky neposkytuje backup, replication ani multi-host durability. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## containerd — Docker Engine

Container lifecycle a image/snapshot komponent používaný Docker Engine-om na koordináciu tasks, runtime shims, content a snapshots podľa konkrétnej konfigurácie platformy. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Containment — CKA drill

Dočasné obmedzenie blast radiusu a ďalších writerov pri zachovaní evidence a funkčnej healthy cohorty.

## Containment generation — Kubernetes incident

Versionovaný stav trafficu, rolloutov, Nodes, retries a external reconcilers vytvorený na zastavenie ďalšieho dopadu bez zničenia evidence. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

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

Delivery model, v ktorom každá zmena spĺňajúca automatizovanú promotion policy pokračuje bez rutinného manuálneho release approvalu do produkčného rollout-u. Pozri [Continuous Deployment](docs/05-ci-cd-and-release/continuous-deployment.md).

## Continuous diagnostics — Zero Trust

Priebežné získavanie identity, endpoint, workload, network, cloud a application telemetry pre aktualizáciu access contextu a risk decisions. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Continuous Integration

Pracovný a technický model častej integrácie malých zmien do spoločnej hlavnej línie s automatizovaným verdictom nad presným candidate integration stateom. Pozri [Continuous Integration](docs/05-ci-cd-and-release/continuous-integration.md).

## Continuous rescanning — GitLab

Opakované vyhodnotenie podporovaných package, SBOM a image digestov voči novej vulnerability intelligence bez potreby source zmeny, s následným mapovaním na releases, effective deployments, ownerov a exposure. Pozri [Security scanning](docs/06-gitlab/security-scanning.md).

## Continuous rescanning — security

Opakované vyhodnocovanie už známych SBOM components, dependencies alebo image digests po aktualizácii advisory databáz bez potreby source zmeny. Pozri [Security scanning](docs/06-gitlab/security-scanning.md).

## Continuous validation — Terraform

Opakované overovanie infraštruktúrnych invariánt po apply pomocou checks, drift plans, asset policy, security rescanningu alebo runtime verification. Pozri [Terraform testing a policy](docs/07-infrastructure-as-code-and-configuration-management/terraform-testing-and-policy.md).

## Continuous verification — Zero Trust

Opakované alebo event-driven prehodnocovanie identity, posture, session a contextu počas bounded access lifecycle-u namiesto permanentnej dôvery po prvom prihlásení. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Continuous Well-Architected

Integrácia architektúrnych controls, review questions, operational evidence a improvement backlogu do priebežného delivery a operations lifecycle-u. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Continuous Well-Architected loop

Priebežné prepájanie architecture decisions, deployment evidence, SLO/security/cost signals, failure drills, findings, improvements, validation a milestones. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Contract drift

Rozdiel medzi správaním test double alebo dokumentovaného kontraktu a skutočnou dependency. Pozri [Mocks, stubs a fakes](docs/04-testing-and-quality/mocks-stubs-fakes.md).

## Contract proof — database

Strojovo aj manuálne overiteľná evidence, že starý databázový contract už nepoužíva žiadny aktívny reader, writer ani downstream consumer, migrácia a reconciliation sú dokončené a odstránenie old representation má pripravenú forward-repair alebo restore cestu. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Contract test

Test kompatibility producer/consumer rozhrania bez potreby spustiť celý distribuovaný systém. Pozri [Contract a API tests](docs/04-testing-and-quality/contract-and-api-tests.md).

## Contributing control failure — CKA

Sekundárny problém, ktorý zhoršil detekciu, blast radius alebo recovery, ale nebol primárnym root cause-om.

## Control/data-path map — Kubernetes

Mapa API a reconciliation control pathu oddelená od client request, packet, storage a business data pathu pre jeden incident subject. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Control/data/recovery plane classification — AWS

Klasifikácia question alebo incidentu podľa toho, či zlyháva API/configuration path, runtime traffic/state path alebo clean-point/restore/cutover path. Pozri [CloudOps domain review a timed reasoning](docs/11-cloud-and-aws/cloudops-domain-review-timed-reasoning.md).

## Control-flow subject — Ansible

Rekonštruovateľná identita rozhodovania `when`/loop/handler pathu zahŕňajúca host, typed effective inputs, fact a registered-result freshness, item inventory, include path, changed signals, handler definitions a batch/run context. Pozri [Handlers, loops a conditionals](docs/07-infrastructure-as-code-and-configuration-management/handlers-loops-conditionals.md).

## Control generation — security

Versionovaný source a runtime realization security policy, identity rule, key/credential boundary, detector alebo recovery controlu. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Control group — experiment

Skupina používateľov, requestov alebo systémových instances, ktorá nedostane experimentálnu zmenu a poskytuje súbežnú baseline na porovnanie. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Control inheritance — cloud compliance

Použitie provider-managed controls, napríklad physical security alebo hypervisor patchingu, ako zdedenej časti zákazníckeho compliance programu; nezbavuje zákazníka vlastných configuration a process responsibilities. Pozri [Shared responsibility model](docs/11-cloud-and-aws/shared-responsibility-model.md).

## Control plane

Časť systému vytvárajúca stav, podľa ktorého data plane rozhoduje. Pozri [OSI a TCP/IP model](docs/02-networking-and-web/osi-and-tcp-ip-model.md).

## Control-plane capability subject

Versionovaný stav konkrétnej Kubernetes control-plane capability, napríklad API write/read/watch, etcd persistence, scheduling alebo controller reconciliation, vrátane component instances, leader, configuration, dependencies, metrics a test outcome-u. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## Control-plane endpoint

Stabilná DNS/IP a load-balancer identity, cez ktorú clients a Nodes pristupujú ku Kubernetes API server replicas. Pozri [Cluster installation a lifecycle](docs/09-kubernetes/cluster-installation-lifecycle.md).

## Control-plane endpoint identity

Stable API hostname/address, load-balancer backend inventory a serving-certificate SAN/trust contract používaný klientmi a Node bootstrapom. Pozri [Cluster installation a lifecycle](../docs/09-kubernetes/cluster-installation-lifecycle.md).

## Control-plane failure — AWS

Zlyhanie AWS API alebo management/configuration operácie, pri ktorom môže existujúci workload data plane naďalej fungovať. Pozri [CloudOps domain review a timed reasoning](docs/11-cloud-and-aws/cloudops-domain-review-timed-reasoning.md).

## Control-plane health gate

Súbor podmienok ako API readiness, etcd quorum, Node/add-on health, certificate stav a backup readiness, ktoré musia prejsť pred upgrade alebo zásahom. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Control plane — Kubernetes

Sada komponentov poskytujúca API, persistence, scheduling a reconciliation cluster-wide desired state-u. Pozri [Kubernetes architecture](docs/09-kubernetes/kubernetes-architecture.md).

## Control-plane observation matrix

Mapovanie endpoint, identity, admission, persistence, scheduler, controller, cloud, certificate a packaging boundaries na ich subjects a diskriminačné observations. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## Control-plane recovery verdict

Dôkaz, že po incidente fungujú semantic API readiness, read/write/watch, etcd quorum a latency, admission, scheduler binding, controller progress a pôvodný workload/business outcome. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## Control-plane write path

Synchronous a durable transition od client endpointu cez API server identity/policy/admission vrstvy po etcd commit, response a následné watch visibility. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## Control plane — Zero Trust

Vrstva zodpovedná za identity, policy evaluation, posture, access decisions a vytvorenie alebo ukončenie communication pathu. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Control variant

Referenčný variant experimentu reprezentujúci existujúce alebo baseline správanie, voči ktorému sa hodnotí treatment. Pozri [A/B testing](docs/05-ci-cd-and-release/a-b-testing.md).

## Controlled dependency refresh

Reviewovaný prechod na nový base, repository snapshot, lock alebo external input, ktorý zámerne mení build freshness a vytvára nové artifact evidence. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Controlled exposure

Riadené sprístupňovanie release-u alebo feature obmedzenej cohrte s explicitnou artifact, configuration a routing identitou, guardrails a rozhodovacími kritériami. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Controlled fault generation

Jedna zámerná versionovaná mutation s expected affected scope, symptom, observation points, abort condition a reset/recovery pathom. Pozri [CloudOps hands-on labs](docs/11-cloud-and-aws/cloudops-hands-on-labs.md).

## Controlled Pod

Pod, ktorého controller ownerReference odkazuje na konkrétny ReplicaSet UID a ktorý controller autoritatívne započítava do replica reconciliation. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

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

## Controller convergence verdict

Verdikt, že latest desired generation bola spracovaná, owned Kubernetes aj external state zodpovedá contractu, status je generation-current, subsequent reconcile je no-op a pôvodný workload outcome bol overený. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Controller ownership boundary

Rozhranie určujúce, ktoré resource types, object UIDs, fields, dependents a external resources môže konkrétny controller autoritatívne pozorovať, meniť, reportovať a čistiť. Pozri [Kubernetes architecture](docs/09-kubernetes/kubernetes-architecture.md).

## Controller queue subject

Identita controller processing state-u zahŕňajúca controller/version, active leader, reconciliation key, object UID/generation, queue attempt, queue age, backoff a relevantný output transition. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## ControllerRevision — Kubernetes

API object uchovávajúci revision metadata workload controllerov, napríklad StatefulSetu, pre rollout history a porovnanie current/update revision. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Convergence — configuration management

Proces, pri ktorom opakované pozorovanie a aplikovanie automation vedie target k stabilnému požadovanému stavu. Pozri [Ansible idempotencia](docs/07-infrastructure-as-code-and-configuration-management/ansible-idempotency.md).

## Cookie

HTTP state token, ktorý server nastaví cez `Set-Cookie` a klient následne posiela podľa domain, path, security a SameSite scope. Pozri [HTTP](docs/02-networking-and-web/http.md).

## Coordinated omission

Measurement chyba, pri ktorej test alebo client nepočíta obdobia, keď systém nevedel prijímať novú prácu, a preto podhodnotí skutočnú latency alebo failure impact. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Copy-on-write — container filesystem

Model, pri ktorom read-only image content zostáva zdieľaný a prvá zmena vytvorí kópiu alebo záznam vo writable upper layeri. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## Copy-up

Operácia prenesenia file-u z read-only lower layeru do writable upper layeru pri prvom zápise. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## CoreDNS

Bežná Kubernetes cluster DNS implementation a extensible DNS server konfigurovaný pluginmi pre Kubernetes records, caching, forwarding, health a ďalšie funkcie. Pozri [Cluster DNS](docs/09-kubernetes/cluster-dns.md).

## CoreDNS loaded configuration

Corefile a plugin generation reálne načítaná konkrétnym CoreDNS processom, odlišná od samotnej ConfigMap resourceVersion. Pozri [Cluster DNS](../docs/09-kubernetes/cluster-dns.md).

## Corrective control

Control, ktorý po zistení incidentu opravuje alebo obmedzuje jeho následky. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Correlation chain — observability

Prechod od SLO alebo metric symptómu cez bounded cohort, exemplar/trace, spans, structured logs, deployment/config event a audit actor až po causal explanation a recovery validation. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Correlation envelope — Kubernetes telemetry

Spoločná sada cluster, operation, release, Pod UID, container ID, Node generation, request/trace ID a UTC time identities umožňujúca spájať signals rovnakého subjectu. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

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

## Cost closure — AWS lab

Dôkaz po cleanup-e, že expected retained evidence zostalo, chargeable lab resources boli odstránené a nasledujúce cost data neukazuje neočakávaný residue. Pozri [CloudOps hands-on labs](docs/11-cloud-and-aws/cloudops-hands-on-labs.md).

## Cost containment verdict

Rozhodnutie, že bounded action zastavila rastúci spend driver bez neprimeraného business, recovery, security alebo evidence damage. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Cost-data cut-off

Timestamp freshness boundary, po ktorú sú line items a adjustments zahrnuté v konkrétnej cost report alebo incident analysis generácii. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Cost incident

Neočakávaný alebo nekontrolovaný spend event spôsobený napríklad útokom, retry loopom, autoscalingom, telemetry explóziou alebo chybnou konfiguráciou. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Cost Optimization pillar

Well-Architected pillar zameraný na poskytovanie business value pri efektívnom total cost počas lifecycle-u. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Cost-view identity

Exact unblended, blended, amortized, net amortized alebo invoice perspective použitá v report-e; zmena view môže zmeniť trend bez zmeny usage. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Counter — metric

Monotónne rastúca metric hodnota používaná pre počty udalostí alebo práce; pri analýze sa typicky prevádza na rate alebo increase za časové okno. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## CPU millicore

Kubernetes CPU quantity, kde `1000m` predstavuje jednu CPU jednotku a `250m` štvrtinu CPU. Pozri [Requests, limits a QoS](docs/09-kubernetes/requests-limits-qos.md).

## CPU quota

Cgroup limit maximálneho CPU času v danom period. Po vyčerpaní môže byť workload throttled. Pozri [cgroups](docs/01-linux-and-systems/cgroups.md).

## CPU throttling

Obmedzenie CPU času containeru po vyčerpaní cgroup CPU quota; process nemusí byť ukončený, ale môže mať vyššiu latency a nižší throughput. Pozri [Requests, limits a QoS](docs/09-kubernetes/requests-limits-qos.md).

## CPU throttling subject

Konkrétny container cgroup, CPU quota/period a time window, v ktorom process vyčerpal quota a čakal napriek prípadnej voľnej CPU kapacite na Node-e. Pozri [Requests, limits a QoS](../docs/09-kubernetes/requests-limits-qos.md).

## Crash-consistent snapshot

Snapshot zodpovedajúci náhlemu výpadku bez garancie, že application buffers alebo transactions boli konzistentne uzavreté. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## `create_before_destroy` — Terraform

Lifecycle rule, ktorá pri replacement operácii žiada vytvorenie nového objektu pred zničením starého, ak platforma, názvy, capacity a dependencies umožnia ich súbežnú existenciu. Pozri [Lifecycle, import a moved blocks](docs/07-infrastructure-as-code-and-configuration-management/lifecycle-import-moved-blocks.md).

## Credential

Dôkaz alebo secret naviazaný na principal, napríklad password, private key, token seed alebo certificate key material. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Credential-after-revocation risk

Riziko, že credential alebo Secret prečítaný pred RBAC revokáciou zostáva použiteľný mimo Kubernetes API a vyžaduje provider-side revokáciu či rotáciu. Pozri [RBAC](../docs/09-kubernetes/rbac.md).

## Credential cache — Kerberos

Client-side store obsahujúci TGT a service tickets pre aktuálnu Kerberos session. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Credential overlap window

Riadené obdobie, počas ktorého old a new credentials môžu byť súčasne platné, aby sa dokončil mixed-cohort refresh bez outage-u; musí mať bounded duration a revocation verdict. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Credential revocation verdict

Dôkaz, že nový credential je načítaný a funkčný, starý credential bol zrušený u authoritative providera a pokus o jeho použitie zlyhá. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Credential revocation verdict — AWS

Dôkaz, že starý access key, STS path alebo workload credential už nemôže úspešne vykonať forbidden request; nie iba fakt, že policy alebo Secret bol zmenený. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## Credential rotation subject

Identita old/new credentialov, provider state-u, Secret objects, consumer Pod generations, overlap window, loaded-state evidence a revocation/cleanup verdictu. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Credential-source identity — AWS

Konkrétny SDK/CLI credential provider a vydaná credential/session generation, ktorú process skutočne použil na podpísanie requestu. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## CRI capability subject

Versionovaný stav kubelet-to-runtime capability zahŕňajúci runtime endpoint, configuration generation, sandbox/container/image operations, latency, errors, content store a test outcome. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

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

## Cross-pillar decision — Well-Architected

Versionované architecture rozhodnutie zaznamenávajúce benefit, trade-offs, guardrails a validation naprieč reliability, security, performance, operations, cost a sustainability outcomes. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Cross-pillar optimization guardrail

SLO, security, recovery, performance alebo capacity condition, ktorá musí zostať splnená počas cost optimization change-u. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Cross-Region backup copy

Kópia recovery pointu do iného AWS Regionu pre regionálnu isolation a disaster-recovery model. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Cross-signal cardinality amplification

Násobenie jednej dynamic dimension naprieč metrics, log streams, trace-derived metrics, indexed fields, dashboard variables a alert identities. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Cross-state contract

Explicitné rozhranie medzi samostatnými Terraform states, typicky cez publikované outputs alebo externý registry, ktoré musí mať ownership, compatibility a access policy. Pozri [Variables, locals a outputs](docs/07-infrastructure-as-code-and-configuration-management/variables-locals-outputs.md).

## Cross-system recovery consistency

Súlad času a verzie obnoveného etcd API state-u, persistent application dát, schema, credentials a external resources. Pozri [etcd backup a restore](docs/09-kubernetes/etcd-backup-restore.md).

## Cross-system recovery generation

Koordinovaná časová a compatibility väzba medzi restored Kubernetes API state-om, application data, queues, external resources, secrets a deployment/schema generations. Pozri [etcd backup a restore](../docs/09-kubernetes/etcd-backup-restore.md).

## Cross-tool contract

Úzke, versionované rozhranie medzi automation systémami, napríklad Terraform outputs publikované ako inventory metadata pre Ansible, s explicitným ownershipom a compatibility policy. Pozri [Terraform vs. Ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md).

## Cross-tool ownership subject

Versionovaný inventory objektov a atribútov spravovaných viacerými automation tools, ktorý pre každý mutable field určuje authoritative writera, read-only consumers, desired-state source, drift detector, permissions a recovery alebo transfer path. Pozri [Terraform vs. Ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md).

## Crypto-shredding

Zneprístupnenie encrypted dát bezpečným zničením všetkých key copies potrebných na ich decryption; účinnosť závisí od úplného key inventory a backup lifecycle-u. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## Cryptographic agility

Schopnosť inventarizovať a kontrolovane meniť cryptographic algorithms, protocols, parameters, certificates a key mechanisms bez neplánovaného prepisu celého systému. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## Cryptographic authorization verdict — KMS

Effective allow alebo deny výsledok z caller/session identity, IAM/SCP/boundary/session policies, key policy, grant constraints, key state, encryption context, endpoint policy a service calling pathu. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Cryptographic BOM — CBOM

Inventory cryptographic algorithms, keys, certificates, protocols a dependencies používaný na crypto governance a migration planning. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## Cryptoperiod

Schválené časové alebo usage obdobie, počas ktorého môže byť cryptographic key použitý na definované operations. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## CSI

Container Storage Interface contract oddeľujúci Kubernetes storage orchestration od vendor-specific provision, attach, mount, resize a snapshot implementation. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## CSI node-publish subject

Identita node-side storage transitionu zahŕňajúca Pod UID, volume/device ID, Node, CSI generation, stage/publish target, mount options, filesystem, operation result a cleanup state. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## CSR — Certificate Signing Request

Podpísaná žiadosť obsahujúca public key a požadované certificate identity attributes pre CA. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## Current replicas — ReplicaSet

Počet Podov aktuálne pozorovaných ReplicaSet controllerom ako súčasť jeho replica population; nemusí byť zhodný s Ready alebo Available počtom. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Current-state detection — Ansible

Mechanizmus, ktorým module alebo workflow zistí aktuálny stav targetu pred rozhodnutím, či je potrebná zmena. Pozri [Ansible idempotencia](docs/07-infrastructure-as-code-and-configuration-management/ansible-idempotency.md).

## Current-state observation — CKA

Minimálna evidence potrebná na odlíšenie initial state-u od zadania pred prvým write operation.

## Current-state observation contract — Ansible

Definícia target identity, relevantných owned fields, freshness a normalization pravidiel, podľa ktorých module alebo workflow rozpozná no-op, required delta, partial state alebo unknown outcome. Pozri [Ansible idempotencia](docs/07-infrastructure-as-code-and-configuration-management/ansible-idempotency.md).

## Current-version semantics

S3 behavior, pri ktorom request bez version ID pracuje s current version alebo delete markerom daného key, nie automaticky s business-authoritative historickou version. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Customer managed key — KMS

KMS key v zákazníckom account-e, ktorého policy, aliases, rotation, enablement, grants a deletion lifecycle spravuje zákazník. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Customer-managed layer

Vrstva služby, ktorej configuration, patching, security, availability alebo recovery zostáva zodpovednosťou zákazníka. Pozri [IaaS, PaaS a SaaS](docs/11-cloud-and-aws/iaas-paas-saas.md).

## Customer responsibility — cloud

Časť service security a operations contractu, ktorú vlastní zákazník, typicky identity, data, application, network configuration, logging, backup a business recovery. Pozri [Shared responsibility model](docs/11-cloud-and-aws/shared-responsibility-model.md).

## CustomResourceDefinition — CRD

Cluster-scoped Kubernetes object, ktorý pridáva nový custom resource type, group/version/schema a scope do API; sám osebe neposkytuje reconciliation logic. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Cutover transaction

CAS-chránený a auditovaný prechod autoritatívneho routingu zo starej deployment farby na novú, viazaný na očakávanú routing revision, immutable release subject a idempotentné failure semantics. Pozri [Blue-green deployment](docs/05-ci-cd-and-release/blue-green-deployment.md).

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

## DaemonSet acceptance verdict

Dôkaz, že každý eligible Node má správnu agent revision a effective authority, capability canary prešiel, misscheduled alebo stale host state neexistuje a workload outcome je správny. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## DaemonSet fleet-capability subject

Spoločná identita DaemonSet UID/generation, eligible Node inventory, per-Node Pods, host authority, node-local capability generations a fleet rollout verdictov. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## DaemonSet `OnDelete`

Update stratégia, pri ktorej nový DaemonSet Pod template začne platiť pre konkrétny Node až po odstránení starého Podu. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## DaemonSet rolling update

Riadené postupné nahrádzanie DaemonSet Podov novou template revision pri zachovaní nastavenej unavailable alebo surge hranice. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## DaemonSet rollout ring

Bounded subset Nodes vybraný podľa poolu, zone alebo risk class pre staged rollout a capability/business verification pred rozšírením na ďalší fleet segment. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## DAG — CI/CD

Directed Acyclic Graph vyjadrujúci explicitné dependencies medzi jobs vrátane ordering-u, artifact flowu a failure propagation. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

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

## Dashboard query budget

Odhad a guardrail query loadu odvodený z počtu panels, queries, variable expansions, viewers, refresh cadence a backend fan-outu. Pozri [Grafana](docs/12-observability/grafana.md).

## Dashboard render canary

End-to-end test, ktorý otvorí exact dashboard UID, vykoná known query a overí raw value, transformation, unit, rendered value a drilldown. Pozri [Grafana](docs/12-observability/grafana.md).

## Dashboard source generation

Immutable alebo versionovaný dashboard artifact vytvorený v authoritative source workflowe pred provisioningom do Grafany. Pozri [Grafana](docs/12-observability/grafana.md).

## DAST — Dynamic Application Security Testing

Security testovanie bežiacej aplikácie zvonka cez jej runtime rozhrania. Pozri [Security a infrastructure tests](docs/04-testing-and-quality/security-and-infrastructure-tests.md).

## Data at rest

Dáta uložené v database, filesysteme, object storage, backupe, snapshot-e alebo inom persistentnom médiu. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Data Encryption Key — DEK

Cryptographic key používaný priamo na encryption application dát alebo storage objektu; v envelope-encryption modeli je sám chránený Key Encryption Keyom. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## Data Flow Diagram — DFD

Model external entities, processes, data stores, data flows a trust boundaries používaný na systematickú identifikáciu threats. Pozri [Threat modeling](docs/13-security-and-identity/threat-modeling.md).

## Data-frame generation — Grafana

Typed query result normalizovaný Grafanou do fields a frames pred expressions, transformations a visualization. Pozri [Grafana](docs/12-observability/grafana.md).

## Data frame — Grafana

Normalizovaná štruktúra query výsledku zložená z fields, ktorú Grafana transformuje a vizualizuje. Pozri [Grafana](docs/12-observability/grafana.md).

## Data generation — stateful workload

Versionovaná identita on-disk alebo replicated data state-u vrátane cluster ID, snapshot/restore lineage, format version a replication position. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Data-ID preflight

Kontrola pred mutation potvrdzujúca environment, persistent data identity, generation/lineage, schema compatibility a writer authority. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

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

## Data-source identity — Grafana

Stable UID, plugin type, endpoint, tenant, credentials, TLS a query settings konkrétneho Grafana data source-u. Pozri [Grafana](docs/12-observability/grafana.md).

## Data-source-managed alert

Alert rule uložená a vyhodnocovaná v Prometheus, Mimir, Loki alebo inom podporovanom ruler systéme, pričom Grafana poskytuje management UI. Pozri [Grafana](docs/12-observability/grafana.md).

## Data-source plugin

Grafana plugin implementujúci query, authentication, health-check a data-frame integration pre konkrétny backend. Pozri [Grafana](docs/12-observability/grafana.md).

## Data source — Terraform

Provider-defined read-only query, ktorá načíta informácie o existujúcom alebo odvodenom objekte bez správy jeho lifecycle Terraform resource bindingom. Pozri [Terraform providers, resources a data sources](docs/07-infrastructure-as-code-and-configuration-management/terraform-providers-resources-data-sources.md).

## Data-stream generation — document search

Logical append-oriented telemetry subject a jeho current backing-index generation vytvorená cez template, rollover a product-specific lifecycle. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Data Stream Lifecycle — Elasticsearch

Elasticsearch lifecycle mechanizmus na retention a správu backing indexes data streamu podľa podporovaného deployment modelu. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Data stream — search

Logical abstraction nad rolling backing indexes optimalizovaná pre timestamped a prevažne append-only data ako logs, events a metrics. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Database recovery acceptance verdict

Closure dôkaz, že writer/connection topology, transaction outcome, data invariants, idempotency, performance a forbidden stale-reader/old-writer/master/public paths sú po failover alebo restore správne. Pozri [Amazon RDS](docs/11-cloud-and-aws/rds.md).

## Database restore generation

Nový RDS instance/cluster vytvorený zo snapshotu alebo PITR s exact restore time, KMS, parameter, network, secret, schema a application compatibility identity. Pozri [Amazon RDS](docs/11-cloud-and-aws/rds.md).

## Database subject

Versionovaná identita RDS deploymentu, endpointu, writer/reader topology, engine/schema/parameter/TLS/secret/KMS generations, application pool/proxy pathu a business transactionu. Pozri [Amazon RDS](docs/11-cloud-and-aws/rds.md).

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

## Decision packet

Kompaktný auditovateľný balík pre approvera obsahujúci subject, risk, evidence, findings, target, rollout, recovery a expiry kontext potrebný na vedomé rozhodnutie. Pozri [Quality gates a approvals](docs/05-ci-cd-and-release/quality-gates-and-approvals.md).

## Declarative configuration

Konfigurácia opisujúca požadovaný výsledný stav, nie sekvenciu krokov. Pozri [Declarative vs. Imperative Approach](docs/00-foundations/declarative-vs-imperative.md).

## Declarative policy

Policy opisujúca požadovaný decision alebo invariant bez imperatívneho control flow-u, typicky nad structured inputom a data. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Decryption identity — Ansible Vault

Workload alebo používateľská identita oprávnená získať konkrétny vault password alebo secret domain a dešifrovať ho iba v definovanom protected runtime scope. Pozri [Vault](docs/07-infrastructure-as-code-and-configuration-management/vault.md).

## Dedicated Node pool

Množina Nodes určená pre konkrétny workload alebo trust tier, typicky chránená kombináciou taintu, toleration, labelu a required node affinity. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Dedicated-pool contract

Kombinácia trusted Node labelu, Node taintu, workload toleration a required node affinity, ktorá drží cudzie workloady vonku a určený workload vo vnútri poolu. Pozri [Taints, tolerations, affinity a topology](../docs/09-kubernetes/taints-tolerations-affinity-topology.md).

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

## Delegated-actor chain

Auditovateľný chain od original human alebo workload actora cez session/token, impersonation alebo delegated workload identity až po downstream action a target. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Delegated-administration subject

Service-specific organization capability viazaná na delegated account ID, role/trust generation, managed scope, audit a emergency revocation path. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Delegated administrator — AWS Organizations

Member account zaregistrovaný na centralizovanú správu podporovanej AWS služby naprieč organization, aby sa znížil počet operácií vykonávaných v management account-e. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Delegation — identity

Kontrolované odovzdanie obmedzenej authority z jedného principalu na iný principal alebo service. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## delete marker — S3

Špeciálna current version vytvorená pri delete requeste vo versioning-enabled buckete, ktorá skryje predchádzajúcu object version bez jej okamžitého odstránenia. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Deletion subject — Kubernetes

Identita deletion lifecycle-u zahŕňajúca cluster, object UID, deletionTimestamp, propagation policy, finalizers, dependent inventory, external bindings a cleanup verdict. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Deletion timestamp — Kubernetes

Serverom nastavený čas označujúci, že object bol prijatý na deletion a čaká na graceful termination alebo finalizer cleanup. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Delivery-generation identity — Lambda

Exact source resource, event-source mapping alebo asynchronous invocation configuration, filter, batching, retry, retention/visibility, destination a target version/alias, ktoré určujú delivery a acknowledgement semantics konkrétneho eventu. Pozri [AWS Lambda](docs/11-cloud-and-aws/lambda.md).

## Demand amplification

Pomer interných attempts, fan-out calls alebo redeliveries voči logical demandu, ktorý môže rásť bez rastu user trafficu a vytvárať downstream overload. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

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

## Dependency-coupled health failure

Failure, pri ktorom healthcheck stotožní vzdialenú dependency outage s local liveness a vyvolá zbytočné restarty alebo restart storm. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Dependency cycle — Terraform

Kruhový vzťah v dependency grafe, pri ktorom objekt priamo alebo nepriamo závisí sám od seba a Terraform nevie zostaviť bezpečné execution poradie. Pozri [Expressions a dependency graph](docs/07-infrastructure-as-code-and-configuration-management/expressions-and-dependency-graph.md).

## Dependency declaration generation — Helm

Versionovaný `Chart.yaml` dependency intent zahŕňajúci names, aliases, constraints, sources, conditions, tags a import contracts pred resolution. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Dependency decommission subject — Helm

Inventár resources, dát, CRDs, hooks, external assets a parent consumers, ktoré treba bezpečne vyradiť pri disable alebo odstránení dependency. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Dependency enablement generation — Helm

Konkrétny verdict conditions, tags, aliases a effective values určujúci, ktoré dependencies vstupujú do jedného release renderu. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Dependency graph subject — Helm

Exact parent chart, declaration, lock, first-level a transitive artifact digests, aliases, conditions a trust evidence pre jednu release generation. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Dependency graph — Terraform

Directed graph vytvorený z references, provider vzťahov a explicitných dependencies, ktorý určuje plan/apply poradie a možnú paralelizáciu objektov. Pozri [Expressions a dependency graph](docs/07-infrastructure-as-code-and-configuration-management/expressions-and-dependency-graph.md).

## Dependency lock

Presne vyriešený zoznam versions priamych a transitívnych dependencies určený na reprodukovateľnú inštaláciu. Pozri [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Dependency lock file — Terraform

Súbor `.terraform.lock.hcl` zachytávajúci vybrané provider versions a package checksums pre reprodukovateľnejšiu inštaláciu dependencies. Pozri [Terraform providers, resources a data sources](docs/07-infrastructure-as-code-and-configuration-management/terraform-providers-resources-data-sources.md).

## Dependency ownership test — Helm

Rozhodnutie, či component zdieľa ownera, cadence, rollback, SLO, privilege a data lifecycle parent release-u, alebo patrí do samostatného release-u. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Dependency RED

Rate, Errors a Duration merané pre outbound dependency calls, používané na oddelenie vlastného service behavior od downstream degradácie. Pozri [RED method](docs/12-observability/red-method.md).

## Dependency scanning — GitLab

Analýza direct a transitive software dependencies podľa manifestov, lockfiles alebo SBOM a ich porovnanie s vulnerability advisory databázou. Pozri [Security scanning](docs/06-gitlab/security-scanning.md).

## Dependency scope — SBOM

Klasifikácia účelu componentu, napríklad runtime, development, test, optional, build-only alebo externally provided. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## Dependency tag — Helm

Label priradený jednej alebo viacerým dependencies, ktorý umožňuje ich skupinové enable/disable cez top-level `tags` values. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Deployability invariant

Trvalá vlastnosť systému, pri ktorej immutable artifact, evidence, configuration, shared-state compatibility, deployment automation, observability a recovery umožňujú bezpečný deployment bez stabilizačného projektu. Pozri [Continuous Delivery](docs/05-ci-cd-and-release/continuous-delivery.md).

## Deployable state

Stav, v ktorom existuje dôveryhodný immutable artifact, potrebné dôkazy, kompatibilná konfigurácia, deployment automation, observability a recovery plán umožňujúci bezpečný deployment. Pozri [Continuous Delivery](docs/05-ci-cd-and-release/continuous-delivery.md).

## Deployed-artifact correlation — GitLab

Auditovateľná väzba `finding/advisory → component alebo image digest → release manifest → deployment record → effective runtime digest → environment, owner a exposure`. Umožňuje odlíšiť opravu v source od skutočne opraveného runtime-u. Pozri [Security scanning](docs/06-gitlab/security-scanning.md).

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

## Deployment-model acceptance verdict

Closure dôkaz, že public/private/hybrid placement spĺňa povolené flows, zakázané flows, data consistency, autonomous behavior, failover/failback a business outcome. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Deployment pipeline

Automatizovaný tok od source zmeny cez build, artifact, risk-specific validation a environment promotion až po produkčne pripraveného alebo nasadeného kandidáta. Pozri [Continuous Delivery](docs/05-ci-cd-and-release/continuous-delivery.md).

## Deployment record

Auditovateľný záznam spájajúci environment, artifact digest, configuration revision, pipeline run, identity, čas a výsledok konkrétneho deploymentu vrátane partial a failed attempts. Pozri [Environment a promotion](docs/05-ci-cd-and-release/environment-and-promotion.md).

## Deployment release subject

Immutable alebo rekonštruovateľná identita rollout-u zahŕňajúca cluster, Deployment UID/generation, admitted Pod template, field ownership, old/new ReplicaSet UIDs, image/config/secret generations, strategy budgets a business outcome. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## Deployment revision

Verzia Deployment Pod template-u reprezentovaná príslušným ReplicaSetom a použitá pre rollout history alebo rollback. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## Deployment rework rate

Podiel deploymentov, ktoré sú neplánovanou opravou predchádzajúceho deploymentu. Pozri [DORA Metrics](docs/00-foundations/dora-metrics.md).

## Deployment ring

Stabilná rollout skupina používateľov, tenantov, zariadení alebo regiónov s definovaným risk profilom, membershipom a promotion contractom. Pozri [Ring deployment](docs/05-ci-cd-and-release/ring-deployment.md).

## Deployment scale ownership

Contract určujúci authoritative writera Deployment `/scale` alebo `.spec.replicas`, napríklad HPA, GitOps, manual workflow alebo custom autoscaler. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## Deployment state divergence — GitLab

Rozdiel medzi desired state-om, GitLab recorded state-om a effective runtime state-om deploymentu. Môže vzniknúť pri asynchrónnej reconciliation, nesprávnom targete, stale generation, partial mutation alebo drift-e. Pozri [Environments, deployments a releases](docs/06-gitlab/environments-deployments-releases.md).

## Deployment subject — GitLab

Presná identity runtime mutation tvorená artifact digestom, rendered config alebo infrastructure revision, trusted deployment job definition, target environmentom, actor/job identity a rollout policy. Pozri [Protected branches a environments](docs/06-gitlab/protected-branches-and-environments.md) a [Environments, deployments a releases](docs/06-gitlab/environments-deployments-releases.md).

## Deprecated API caller

Klient, controller, chart, operator alebo automation používajúca Kubernetes API verziu, ktorá bude alebo už bola odstránená, aj keď deklaratívne manifests už môžu byť migrované. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Deprecated-API closure

Dôkaz, že všetci reálni callers používajú podporované endpointy, CRD storage/conversion je compatible a starú API generation možno bezpečne odstrániť. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## deregistration delay — ELB

Target-group interval, počas ktorého deregistrovaný target zostáva v draining stave pre dokončenie existujúcich requests alebo connections. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## Derived credential subject

Krátkodobý cloud, Vault alebo iný external credential vydaný na základe workload identity, s vlastnou expiry, permissions, auditom a revocation lifecycle-om. Pozri [ServiceAccount](../docs/09-kubernetes/serviceaccount.md).

## Derived signal

Telemetry signal vypočítaný z iného signalu, napríklad metrics zo spans alebo logs; musí mať explicitný source-of-truth a sampling contract. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Derived-signal authority

Verdict určujúci, či signal vypočítaný z logs, spans alebo iného source-u má dostatočnú coverage, sampling a correctness na konkrétne SLO, alert alebo investigation použitie. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Descriptor — OCI

Štruktúra identifikujúca OCI content cez media type, digest, size a prípadné platform metadata. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

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

## Desired-state generation — containers

Exact ECS task-definition/service deployment alebo Kubernetes API object/controller generation, ktorú orchestrator reconciliuje do runtime workload population. Pozri [Amazon ECS a Amazon EKS](docs/11-cloud-and-aws/ecs-eks.md).

## Desired state — Kubernetes

Intent deklarovaný v Kubernetes object `spec` alebo odvodený vyšším controllerom, ku ktorému control loops približujú aktuálny stav. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Destination-tuple concentration

Sústredenie veľkého počtu concurrent alebo short-lived connections na rovnaký destination IP, port a protocol, ktoré môže vytvoriť NAT source-port pressure aj pri nízkom bandwidth-e. Pozri [Internet Gateway a NAT Gateway](docs/11-cloud-and-aws/internet-gateway-nat-gateway.md).

## Destructive reclaim subject

Exact PVC UID, PV UID, reclaim policy a backend volume identity, nad ktorými môže deletion transition odstrániť authoritative storage asset. Pozri [Volumes, PV, PVC a StorageClass](../docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Destructive volume cleanup subject

Presná identita daemonu, projektu, volume objectu, logical data ID, ownera, backup/restore verdictu a retention approval potrebná pred odstránením volume-u. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## Detached HEAD

Stav, v ktorom `HEAD` ukazuje priamo na commit namiesto symbolického odkazu na branch. Nové commits treba zachytiť branch refom, inak môžu zostať unreachable. Pozri [Commit, branch, tag a HEAD](docs/03-git-and-automation/commit-branch-tag-head.md).

## Detective control

Control určený na odhalenie incidentu, policy violation alebo nežiaducej zmeny. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Deterministic dependency rebuild verdict

Dôkaz, že rovnaký source a reviewed lock v clean prostredí vytvoria rovnaký packaged dependency graph bez nového version negotiation alebo internet timing driftu. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Deterministic encryption

Encryption model, v ktorom rovnaký plaintext pri rovnakom keyu a kontexte produkuje rovnaký ciphertext, čo môže umožniť equality queries, ale zároveň odhaľuje opakovanie a frequency patterns. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## Deterministic render evidence — Helm

Dôkaz, že rovnaký chart artifact, dependency lock, effective values, release context a capabilities vytvárajú rovnaký rendered-manifest digest bez neplánovaného live, časového alebo random inputu. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Deterministic render verdict — Helm

Dôkaz, že fixný chart, dependency graph, values, release context, capabilities a engine vytvoria rovnaký semantic manifest output pri opakovanom renderi. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

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

Digest uncompressed filesystem changesetu uložený v OCI image configuration rootfs chain. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Diff mode — Ansible

Režim zobrazujúci content rozdiel pri podporovaných modules; output môže obsahovať citlivé údaje a potrebuje access a retention policy. Pozri [Ansible architecture](docs/07-infrastructure-as-code-and-configuration-management/ansible-architecture.md).

## Differential policy testing

Vyhodnotenie rovnakého corpus-u inputs cez starú a novú policy revision s kontrolou semantic decision rozdielov. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Digest pinning

Viazanie dependency, action, image alebo artifact reference na immutable cryptographic content digest namiesto mutable tagu alebo version range. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Dimension inventory — observability

Úplný zoznam labels, attributes, fields a promoted dimensions spolu s ich source, boundedness, purpose, backend use a retention. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Direct access bypass — Zero Trust

Alternatívna network alebo application cesta, ktorá umožňuje dostať sa ku resource-u bez zamýšľaného identity-aware PEP a policy evaluation. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Direct membership — GitLab

Členstvo pridané priamo na konkrétny project alebo group, na rozdiel od accessu zdedeného z parent group alebo získaného sharingom. Pozri [Projects, groups a permissions](docs/06-gitlab/projects-groups-permissions.md).

## Direct Pod

Pod vytvorený bez vyššieho workload controlleru; po strate alebo Node failure nemá automatický replica replacement a rollout model. Pozri [Pod](docs/09-kubernetes/pod.md).

## Direct-Pod recovery boundary

Failure boundary Podu vytvoreného bez higher-level workload controlleru, pri ktorom Node failure alebo Pod deletion nemá automatický replica replacement owner. Pozri [Pod](docs/09-kubernetes/pod.md).

## Direct-to-storage tracing

Jaeger deployment model, v ktorom collectors zapisujú traces priamo do external storage bez durable Kafka bufferu. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Directory Information Tree — DIT

Hierarchická štruktúra LDAP directory entries organizovaná podľa Distinguished Names. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## Directory partition — AD DS

Replikovaný naming context AD DS, napríklad schema, configuration, domain alebo application partition, s vlastným replication scope-om. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Disaster declaration boundary

Podmienky, čas a authority, pri ktorých incident prechádza z lokálneho HA recovery do explicitného DR procesu. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Disaster recovery — DR

People, process a technology capability obnoviť business službu a jej dáta po udalosti presahujúcej bežný high-availability design podľa definovaných RPO a RTO. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Disaster recovery — Kubernetes

Koordinovaný proces obnovy control-plane state-u, PKI, encryption keys, external infrastructure a application dát po strate authoritative cluster state-u. Pozri [etcd backup a restore](docs/09-kubernetes/etcd-backup-restore.md).

## Disconnected operation

Schopnosť hybridného alebo edge workloadu pokračovať v definovanom režime pri strate spojenia s central cloud control plane alebo WAN dependency. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Discriminating lab observation

Metric, event, API field, log alebo request result, ktorý odlíši minimálne dve plausible hypotheses o vloženom failure mechanizme. Pozri [CloudOps hands-on labs](docs/11-cloud-and-aws/cloudops-hands-on-labs.md).

## Discriminating observation boundary

Observation point, ktorého výsledok rozdelí konkurenčné hypotézy s minimálnym rizikom a zmenou systému. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Discriminating observation — CKA

Pozorovanie alebo test, ktorý významne odlíši competing hypotheses bez zmeny viacerých vrstiev naraz.

## Discriminating observation — CloudOps

Observation point, ktorého výsledok podporuje jednu causal hypothesis a zároveň oslabuje alebo vylučuje inú. Pozri [CloudOps troubleshooting drills](docs/11-cloud-and-aws/cloudops-troubleshooting-drills.md).

## Discriminating observation point — Docker

Observation, ktorého výsledok odlišuje aspoň dve konkurenčné causal hypotheses, napríklad cgroup OOM od host OOM alebo wrong socket bind od firewall failure. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Disk watermark — search cluster

Threshold disk usage ovplyvňujúci shard allocation, relocation alebo write blocks v Elasticsearch/OpenSearch clusteri. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Distinguished Name — DN

Jednoznačný hierarchický názov LDAP entry, napríklad `uid=alice,ou=People,dc=example,dc=com`. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## Distractor taxonomy — CloudOps

Kategórie nesprávnych options ako wrong scope, half path, configured-not-effective, symptom repair, security bypass, HA/DR confusion alebo locally optimal trade-off. Pozri [CloudOps domain review a timed reasoning](docs/11-cloud-and-aws/cloudops-domain-review-timed-reasoning.md).

## Distributed cache — GitLab Runner

CI cache uložená v shared backend-e, typicky object storage, aby ju mohli používať viaceré alebo autoscaled runners. Pozri [Artifacts a cache](docs/06-gitlab/artifacts-and-cache.md).

## Distributed recovery consistency

Požiadavka, aby independently captured database, object, file, queue a external-system states tvorili logicky kompatibilný business checkpoint. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Distributed trace

Model celej cesty requestu alebo operácie cez viac services a dependencies, zložený z navzájom prepojených spans. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Distribution digest — OCI

Digest registry blobu alebo manifestu v distribuovanej reprezentácii, používaný na integrity a immutable references. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Distribution — metric

Reprezentácia rozdelenia nameraných hodnôt, napríklad latency alebo response size, ktorá zachováva viac informácií než average. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Distroless image

Minimalizovaný runtime image bez bežného shellu alebo package managera, určený na spustenie konkrétnej aplikácie s menším mutable surface; vyžaduje external observability a premyslený debugging model. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## DNAT — Destination NAT

Preklad destination adresy alebo portu, používaný napríklad pri publikovaní internej služby. Pozri [NAT](docs/02-networking-and-web/nat.md).

## DNS-address generation

Versionovaný vzťah medzi Ingress/Gateway address statusom, external DNS recordmi, TTL/cache a active load-balancer addresses. Pozri [Ingress a Gateway API](../docs/09-kubernetes/ingress-gateway-api.md).

## DNS answer subject

Konkrétna DNS odpoveď identifikovaná query name/type, response code, answer set, TTL, server a observation time. Pozri [Cluster DNS](../docs/09-kubernetes/cluster-dns.md).

## DNS delegation

Publikovanie NS records v parent DNS zone, ktorým sa authoritative zodpovednosť za domain alebo subdomain odovzdá konkrétnym name serverom. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## DNS — Domain Name System

Distribuovaný hierarchický systém mapujúci mená na resource records. Pozri [DNS](docs/02-networking-and-web/dns.md).

## DNS failover realization

End-to-end transition `health detection → authoritative Route 53 verdict → resolver/client cache expiry → reconnect → secondary capacity/data/business acceptance`. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## DNS lookup lifecycle subject

Úplný subject spájajúci exact query, Pod resolver generation, search expansion, DNS path, server/cache generation, answer, selected address, fresh connection a business request. Pozri [Cluster DNS](../docs/09-kubernetes/cluster-dns.md).

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

## Docker API operation subject

Identita Engine API mutation zahŕňajúca context/endpoint, caller, requested object/image, name/labels, runtime policy, correlation ID a purpose. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Docker bind mount

Runtime mount konkrétneho host filesystem pathu do container mount namespace-u, ktorý prenáša host path, permissions, labels a lifecycle coupling. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## Docker CLI

Client program `docker`, ktorý parsuje príkazy a komunikuje s Docker Engine API; container primitives typicky nevytvára priamo. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Docker container generation

Konkrétna Engine container instance identifikovaná object ID, create time, image digest, create configuration, mounts, endpoints, cgroup, process a health history; odlišná od service name alebo Compose service definition. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Docker containment subject

Presný incident subject, scope, časové okno, protected data/side effects a dočasné actions, ktoré znižujú dopad bez zničenia evidence alebo vytvorenia nevratnej mutation. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Docker context

Pomenovaný client-side connection profil určujúci Docker daemon endpoint, TLS/SSH metadata a ďalšie connection nastavenia; nesprávny context môže nasmerovať deštruktívny príkaz na iný host. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Docker context identity

Resolved Docker client target zahŕňajúci context name, Engine endpoint, SSH/TLS metadata a expected daemon/environment identity. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Docker daemon — `dockerd`

Dlhodobo bežiaci server Docker Engine-u spravujúci images, containers, networks, volumes, builds a komunikáciu s nižšími runtime components. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Docker Desktop

Desktop platforma zahŕňajúca Docker Engine, CLI, UI, build, credential, networking a virtualizačné komponenty; na Windows a macOS typicky používa Linux virtualizačnú vrstvu pre Linux containers. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Docker diagnostic baseline

Minimálna sada evidence zahŕňajúca versions, context, `docker info`, container state, inspect, logs, events, resource usage a disk stav pred deštruktívnym zásahom. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Docker disk usage

Storage spotrebovaný images, writable layers, volumes, build cache, logs a runtime content stores, analyzovaný napríklad cez `docker system df`. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Docker DNS generation

Versionovaný endpoint a alias inventory v konkrétnej Docker network/project boundary, ktorý mapuje stable service names na aktuálne container addresses a readiness state. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Docker embedded DNS

DNS service poskytovaná Docker Engine-om pre name resolution containers a aliases v user-defined networks. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Docker endpoint subject

Identita pripojenia containeru k Docker networku zahŕňajúca network/endpoint IDs, addresses, aliases, veth/interface, routes, DNS a attach generation. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Docker Engine

Client-server container platforma pozostávajúca z daemon-u, API a súvisiacich components na správu Docker objects a container lifecycle. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Docker Engine API

Versionované HTTP API, cez ktoré clients a integrations riadia Docker daemon; prístup k nemu je privilegovaná platformová capability. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Docker event

Časovo zoradená runtime udalosť Docker daemon-u, napríklad create, start, die, health status, network connect alebo image pull, použitá na incident koreláciu. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Docker executor — GitLab Runner

Executor, ktorý spúšťa každý job v containeri vytvorenom z definovaného image a môže pripájať service containers, volumes a cache. Pozri [Runners a executors](docs/06-gitlab/runners-and-executors.md).

## Docker forwarding path

Host-side packet transition od published bind addressu cez proxy alebo DNAT, forwarding policy, bridge/veth a reverse conntrack translation ku container socketu. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Docker health history

Obmedzený záznam posledných healthcheck executions, exit statuses a outputu dostupný cez container inspection. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Docker health status

Runtime stav `starting`, `healthy` alebo `unhealthy` odvodený z healthchecku a oddelený od process state `running` alebo `exited`. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Docker healthcheck

Periodický command definovaný image-om alebo runtime modelom, ktorého exit status určuje health state bežiaceho containeru. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Docker host network

Network mode, v ktorom container process zdieľa host network namespace, binduje priamo host ports a nemá bežnú samostatnú container network isolation. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Docker incident subject

Spoločná identita incidentu zahŕňajúca time window, Docker context/host/project, release a platform digest, container/config/data/endpoint generations, cgroup a flow state, request IDs a business audit. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Docker internal network

Docker network deklarovaná tak, aby obmedzila bežný external routing/egress podľa driver capabilities, používaná na užšie backend communication boundaries. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Docker mount subject

Identita mountu zahŕňajúca daemon/context, source type a physical/logical identity, project, destination, access flags, UID/GID mapping, LSM, propagation, data generation a ownera. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## Docker network

Pomenovaný runtime connectivity object s konkrétnym driverom, IPAM a isolation/discovery semantics pre pripojené containers. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Docker network alias

Dodatočné logical DNS meno container endpointu platné v konkrétnej Docker network boundary. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Docker network subject

Identita Docker network objectu zahŕňajúca daemon/project, network ID/name, driver/options, subnet/gateway, flags, endpoint inventory, DNS, MTU a policy generation. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Docker none network

Runtime network mode poskytujúci containeru minimálny network namespace bez bežnej external connectivity, typicky iba s loopback interfaceom. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Docker object

Daemon-managed objekt ako image, container, network alebo volume s vlastnou identity a lifecycle semantics. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Docker object-task reconciliation

Porovnanie Docker object metadata, containerd task/shim, runtime processu, endpoints, mounts a application outcome-u po timeoute alebo partial operation. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Docker port publishing

Runtime forwarding alebo routing konfigurácia mapujúca host address a port na port v container network namespace; je odlišná od Dockerfile `EXPOSE`. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Docker socket

Local Unix socket alebo obdobný endpoint poskytujúci prístup k Docker Engine API; write access je často prakticky host-administration capability. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Docker-to-Kubernetes diagnostic bridge

Prenos subject-bound diagnostickej metódy z Docker Engine modelu na Kubernetes control planes: artifact/process/cgroup/mount/flow identities zostávajú, no pribúdajú API desired state, controllers, scheduler, kubelet/CRI, Pod, Service endpoint a rollout generations. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Docker volume

Docker-managed storage object s lifecycle oddeleným od konkrétnej container instance; persistence neznamená automatický backup, replication ani multi-host durability. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## Dockerfile

Versionovaný build program obsahujúci instructions, z ktorých builder vytvorí image filesystem layers a runtime metadata. Pozri [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md).

## Dockerfile frontend

Parser a build frontend implementujúci Dockerfile syntax a prekladajúci instructions do BuildKit build graphu, často vybraný cez `# syntax=` directive. Pozri [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md).

## Dockerfile frontend identity

Versionovaná implementácia Dockerfile syntax a build semantics vybraná parser directive-om alebo builder defaultom. Pozri [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md).

## Dockerfile program subject

Identita build programu zahŕňajúca Dockerfile/frontend, immutable inputs, stage graph, args/secrets references, platform, builder a selected target. Pozri [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md).

## `.dockerignore`

Pattern file filtrujúci content zahrnutý do Docker build contextu; znižuje transfer, cache invalidation a accidental exposure, ale nie je secret manager ani náhrada za odstránenie secrets z repository history. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Document generation — Systems Manager

Exact SSM document name, version, content hash, schema, parameters, platform preconditions a default-version state použitý pri command, session, association alebo Automation execution. Pozri [AWS Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## Document — search

JSON objekt uložený v Elasticsearch/OpenSearch indexe a spracovaný podľa mappingu. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Document-search acceptance verdict

Dôkaz, že documents prešli per-item ingestom, správnou mapping generation, search visibility, lifecycle a recovery testom bez forbidden schema alebo tenant outcome-u. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Document-search subject

Exact Elasticsearch alebo OpenSearch product/version, cluster, data stream/index, template, mapping, pipeline, backing index, lifecycle, snapshot a query scope analyzovanej telemetry. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Document stream — YAML

YAML stream obsahujúci jeden alebo viac documents oddelených markerom `---`. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Domain — AD DS

Logical AD DS partition s vlastným DNS name, domain-wide objects, replication scope a domain operations roles. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Domain controller

Server hostujúci AD DS directory partitions a poskytujúci LDAP, Kerberos KDC, authentication, replication a SYSVOL/Group Policy služby. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Domain floor — certification readiness

Minimálna akceptovateľná capability úroveň v každej významnej domain, ktorá bráni silnému celkovému priemeru skryť kritický security, recovery, automation alebo networking gap. Pozri [AWS Certified CloudOps Engineer – Associate](docs/11-cloud-and-aws/cloudops-engineer-associate-soa-c03.md).

## Domain Local group

AD DS group scope typicky používaný na priradenie permissions k resources v konkrétnej doméne. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Domain-weighted lab blueprint

Rozdelenie taskov a bodov podľa aktuálnych CKA domain weights bez zredukovania cross-domain incidentov na izolované katalógy.

## Domain-weighted lab — CKA

Timed lab, ktorého bodové rozdelenie zodpovedá aktuálnym oficiálnym CKA curriculum doménam namiesto rovnomerného alebo náhodného mixu tém. Pozri [CKA timed labs](docs/10-helm-and-cka/cka-timed-labs.md).

## `DoNotSchedule` — topology spread

Hard topology spread behavior, pri ktorom scheduler Pod nenaplánuje, ak by porušil deklarovaný `maxSkew` a ďalšie constraint pravidlá. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## DORA metrics

Metriky software delivery performance sledujúce throughput a instability delivery systému. Pozri [DORA Metrics](docs/00-foundations/dora-metrics.md).

## Downstream capacity envelope

Maximum connections, concurrency, throughput alebo rate, ktoré dependency bezpečne unesie pri replica scale-up/down bez amplification incidentu. Pozri [HPA a autoscaling](../docs/09-kubernetes/hpa-autoscaling.md).

## Drain completion — containers

Dôkaz, že workload už neprijíma nové traffic alebo queue leases, dokončil alebo odovzdal in-flight work, publikoval durable outcome a môže byť bezpečne zastavený alebo jeho host terminated. Pozri [Amazon ECS a Amazon EKS](docs/11-cloud-and-aws/ecs-eks.md).

## Drain completion — load balancer

Dôkaz, že target už neprijíma nové requests, dokončil alebo odovzdal in-flight work, uzavrel business acknowledgement a môže byť bezpečne deregistrovaný a terminated. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## Drift

Rozdiel medzi deklarovaným a skutočným stavom systému. Pozri [Desired State and Reconciliation](docs/00-foundations/desired-state-and-reconciliation.md).

## Drift detection cadence

Frekvencia, s akou sa pre konkrétny state alebo infra domain vykonáva refresh/plan a klasifikácia zmien podľa security, availability a change rizika. Pozri [Drift](docs/07-infrastructure-as-code-and-configuration-management/drift.md).

## Drift detection subject — Terraform

Presná identita drift porovnania zahŕňajúca configuration revision, resolved dependencies a variables, backend/state lineage a serial, provider target, read identity, refresh time a expected resource inventory. Pozri [Drift](docs/07-infrastructure-as-code-and-configuration-management/drift.md).

## Drift noise — Terraform

Opakovaný alebo nerelevantný plan diff spôsobený napríklad provider normalizáciou, server defaults, orderingom, timestamps alebo eventual consistency namiesto významnej ownership zmeny. Pozri [Drift](docs/07-infrastructure-as-code-and-configuration-management/drift.md).

## Drift reconciliation

Riadené rozhodnutie drift revertovať, adoptovať do configuration, zmeniť ownership alebo odstrániť Terraform management s následným overením state a remote výsledku. Pozri [Drift](docs/07-infrastructure-as-code-and-configuration-management/drift.md).

## Drill score closure

Vyhodnotenie root-cause accuracy, minimal repair, validation, evidence safety a času ako oddelených výsledkov.

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

## Durable operation ledger — Helm

Autoritatívny persistentný záznam hook operácií podľa operation ID, source/target state-u, checksumu a výsledku, ktorý umožňuje rozlíšiť complete, partial, failed a unknown outcome aj po odstránení Job resource-u. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

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

## Dynamic template execution boundary — Helm

Trust boundary vytvorená funkciou ako `tpl`, ktorá mení values string z deklaratívnych dát na vykonateľný template input v odovzdanom scope-e. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Earlier operational control

Preventive, detective alebo recovery control odvodený z potvrdeného incident mechanismu a pridaný do build, deployment, policy, telemetry alebo runbook lifecycle-u. Pozri [CloudOps troubleshooting drills](docs/11-cloud-and-aws/cloudops-troubleshooting-drills.md).

## Early feedback

Informácia o kvalite alebo riziku získaná v najskoršom bode, v ktorom má kontrola dostatočnú fidelity a diagnostickú hodnotu. Pozri [Shift-left](docs/04-testing-and-quality/shift-left.md).

## East-west traffic

Traffic medzi internými workloads alebo services v rámci platformy. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## eBPF — extended Berkeley Packet Filter

Kernel technológia na spúšťanie overeného bytecode na definovaných hooks, používaná aj na observability a profiling. Pozri [Performance a troubleshooting](docs/01-linux-and-systems/performance-and-troubleshooting.md).

## EBS Multi-Attach

Capability vybraných Provisioned IOPS EBS volumes umožňujúca pripojenie k viacerým podporovaným instances v rovnakej AZ; vyžaduje cluster-aware filesystem/application a fencing. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## EBS snapshot

Point-in-time block snapshot EBS volume-u používaný na restore, copy, migration alebo backup; bez application koordinácie môže byť iba crash-consistent. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## EBS volume

Persistent block device v jednej Availability Zone, ktorý možno attachnúť k EC2 instance v rovnakej AZ. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## EC2 fleet-realization subject

Exact ASG/fleet identity vrátane desired boundaries, launch template version, AMI, instance types, subnets, SG, role, EBS/KMS, bootstrap, health, target and business generations. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

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

## Edge cohort subject

Množina active edge instances alebo load-balancer targets, ktoré musia používať rovnakú accepted route a certificate generation. Pozri [Ingress a Gateway API](../docs/09-kubernetes/ingress-gateway-api.md).

## Edge-delivery acceptance verdict

Closure dôkaz, že approved DNS/distribution/behavior/cache/origin generations poskytujú správnu a izolovanú representation, origin authorization a recovery behavior pri zachovaných forbidden tenant/public/stale/wrong-origin paths. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Edge-delivery subject

Versionovaná identita Route 53 aliasu, CloudFront distribution/certificate, ordered behavior, cache/origin policies, edge code, origin a exact viewer/business requestu. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Edge retry subject

Jeden client request a všetky edge-generated backend attempts, viazané na method, timeout, retry policy a application idempotency key. Pozri [Ingress a Gateway API](../docs/09-kubernetes/ingress-gateway-api.md).

## Edge route lifecycle subject

Úplný subject spájajúci Route/Ingress intent, class/controller, parent/listener, attachment, resolved references, programmed dataplane, DNS, certificate, backend a client request. Pozri [Ingress a Gateway API](../docs/09-kubernetes/ingress-gateway-api.md).

## Effective access

Výsledná množina permissions po vyhodnotení direct a inherited assignments, groups, roles, conditions, boundaries, resource policies a explicit denies. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Effective access — GitLab

Výsledná množina capabilities subjectu nad konkrétnym resource-om po vyhodnotení všetkých direct, inherited, shared, tokenových, custom-role a resource-policy access paths. Pozri [Projects, groups a permissions](docs/06-gitlab/projects-groups-permissions.md).

## Effective-access graph

Výsledný graph direct, group, nested, inherited, delegated a resource-policy paths spájajúci principal so sensitive capability po zohľadnení session a platform semantics. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Effective allocation coverage

Podiel in-scope spendu priradený správnemu ownerovi cez dôveryhodné a validné dimensions, nie iba syntakticky vložený do default bucketu. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Effective backup coverage

Dôkaz, že authoritative critical-resource inventory je skutočne vybraný current plan/assignmentom, má fresh source recovery point, required isolated copy a restore-test coverage. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Effective branch policy — GitLab

Capability-specific výsledok všetkých project a inherited group branch rules, ktoré matchujú konkrétny branch alebo pattern. Nesmie sa odhadovať iba podľa jednej viditeľnej rule. Pozri [Protected branches a environments](docs/06-gitlab/protected-branches-and-environments.md).

## Effective capability set

Množina Linux capabilities aktuálne používaná kernelom pri privilege checks procesu. Pozri [Linux capabilities](docs/01-linux-and-systems/linux-capabilities.md).

## Effective capacity

Kapacita skutočne dostupná workloadu po zohľadnení quotas, reservations, failures, topology, limits a maintenance, nie iba nominálny súčet resources. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Effective control

Control otestovaný alebo pozorovaný proti intended threat/failure a preukázane vytvárajúci required technical a business outcome. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Effective firewall verdict — container

Výsledok policy rozhodovania nad konkrétnym direction/interface a pre/post-NAT tuple po zohľadnení Docker, host, cloud a remote rules. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Effective flag state

Flag revision, variant, matched rule, evaluation context, SDK/cache state a application version, ktoré konkrétny runtime evaluator skutočne použil. Môže sa líšiť od poslednej hodnoty zobrazenej v control plane počas propagation alebo rejection failure. Pozri [Feature flags](docs/05-ci-cd-and-release/feature-flags.md).

## Effective host value subject — Ansible

Rekonštruovateľný host-specific value set po vyhodnotení inventory a role sources, precedence, play/role parameters, facts a cache generation, registered alebo `set_fact` values, extra vars a lookup dependencies. Pozri [Variables, facts a templates](docs/07-infrastructure-as-code-and-configuration-management/variables-facts-templates.md).

## Effective image identity — Kubernetes node

Konkrétny platform manifest a runtime `imageID`/digest použitý na Node-e, odlíšený od mutable source tagu alebo pôvodnej textovej image reference. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## Effective image metadata

Runtime defaults vo final image confige, najmä entrypoint, command, environment, user, workdir, labels, healthcheck, exposed ports a stop signal. Pozri [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md).

## Effective input subject — Terraform

Rekonštruovateľná množina root a module inputs po vyhodnotení source-u, precedence, default/null semantics, caller forwarding-u a sensitive markers, viazaná na konkrétny saved plan. Pozri [Variables, locals a outputs](docs/07-infrastructure-as-code-and-configuration-management/variables-locals-outputs.md).

## Effective machine generation — EC2

Výsledná machine/application generation vytvorená z AMI, launch template-u, user data, reachable artifacts, retrieved configuration/secrets a runtime service startupu. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Effective mount access verdict

Kernel výsledok nad visible pathom po zohľadnení process UID/GID, user mapping, inode mode/ACL, mount read-only flags a SELinux/AppArmor policy. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## Effective NetworkPolicy generation

Policy program reálne načítaný konkrétnym Node/dataplane enforcement pointom po selector resolution a controller reconciliation; môže zaostávať za API object generation. Pozri [CNI a NetworkPolicy](../docs/09-kubernetes/cni-networkpolicy.md).

## Effective organization policy

Výsledný SCP, RCP alebo declarative configuration stav vypočítaný z root, parent OU, child OU a account attachments podľa semantics daného policy typu. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Effective permission graph — AWS

Reachable authorization paths od principal/session identity cez trust, identity/resource policies, permissions boundary, session policy, SCP/RCP, conditions a service-specific policies k exact action/resource verdictu. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## Effective-privilege graph

Výsledná množina priamych aj nepriamych capabilities principalu vrátane role inheritance, workload creation, credential access, impersonation a policy-modification paths. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## Effective process authority — Kubernetes

Skutočná runtime autorita procesu po aplikovaní UID/GID/groups, capabilities, `no_new_privs`, seccomp, LSM, mounts, devices, host namespaces a runtime socketov. Pozri [SecurityContext a Pod Security](../docs/09-kubernetes/securitycontext-pod-security.md).

## Effective RBAC graph

Union všetkých RoleBinding/ClusterRoleBinding paths, group memberships, referenced Roles/ClusterRoles a aggregated rules pre konkrétny request subject. Pozri [RBAC](../docs/09-kubernetes/rbac.md).

## Effective release values — Helm

Výsledná values konfigurácia po zlúčení chart defaults, predchádzajúceho release state-u podľa zvolenej stratégie, values files a CLI overrides. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Effective resource capacity

Kapacita skutočne dostupná konkrétnemu workloadu po zohľadnení loaded limits, reservations, unhealthy members, topology, quotas, maintenance a failover constraints. Pozri [USE method](docs/12-observability/use-method.md).

## Effective resource contract

Admitted requests a limits konkrétneho Podu po defaultingu, LimitRange, policy mutation, init/sidecar calculation a RuntimeClass overhead. Pozri [Requests, limits a QoS](../docs/09-kubernetes/requests-limits-qos.md).

## Effective role — GitLab

Najvyššia rola, ktorú používateľ získa zo všetkých relevantných direct, inherited a shared memberships na danom resource. Pozri [Projects, groups a permissions](docs/06-gitlab/projects-groups-permissions.md).

## Effective route-table association

Route table, ktorú subnet skutočne používa po explicitnej asociácii alebo inheritance z main route table; subnet tag alebo diagram ju nenahrádza. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## Effective runtime policy subject

Kernel-enforced state vzniknutý z image defaults, deployment overrides, daemon/orchestrator defaults a node policy vrátane credentials, capabilities, seccomp, LSM, mounts, devices, network a cgroups. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Effective security control

Control, ktorého schválená generation je načítaná a presadzovaná na každej relevantnej boundary a ktorého allowed, forbidden a recovery outcomes boli testované. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Effective value — GitLab CI

Hodnota, ktorú konkrétny pipeline alebo job skutočne použije po vyhodnotení všetkých variable sources, precedence, protected/environment scope-u, availability phase a downstream forwarding-u. Pozri [Variables a secrets](docs/06-gitlab/variables-and-secrets.md).

## Effective values — Helm

Výsledná redigovaná konfigurácia po aplikovaní chart defaults, parent/subchart scope-u, zoradených values files a CLI overrides pre konkrétnu release operáciu. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## EFS access point

Application-specific EFS entry point vynucujúci root directory a voliteľnú POSIX identity pre mounted clienta. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## EFS mount target

ENI-based VPC endpoint v konkrétnej Availability Zone, cez ktorý clients pristupujú k EFS filesystemu protokolom NFS. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Egress AZ coverage

Zoznam source AZ cohorts, ktoré majú accepted NAT/IGW/endpoint path, address identity a failure behavior; logical regional resource alebo healthy jedna AZ nepokrýva automaticky všetky cohorts. Pozri [Internet Gateway a NAT Gateway](docs/11-cloud-and-aws/internet-gateway-nat-gateway.md).

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

## Eligible autoscaling cohort

Current Pody zahrnuté do metric výpočtu po zohľadnení target selectoru, missing metrics, readiness/startup a controller semantics. Pozri [HPA a autoscaling](../docs/09-kubernetes/hpa-autoscaling.md).

## Eligible Node — DaemonSet

Node, ktorý spĺňa DaemonSet placement podmienky vrátane labels, affinity, taints/tolerations, platformy, admission a scheduling constraints. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## Eligible-Node inventory

Versionovaný zoznam Node UIDs a attributes, ktoré podľa aktuálnej DaemonSet placement a authorization policy majú dostať node-local Pod. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## Embedded Metric Format

Structured log format, z ktorého CloudWatch extrahuje custom metrics a dimensions bez samostatného per-metric API publish callu. Pozri [CloudWatch a CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## Emergency deny lifecycle — AWS network

Coarse subnet alebo central-policy deny s ownerom, scope-om, expiry, management/recovery-access validation, rollbackom a post-incident drift cleanupom. Pozri [Security Groups a Network ACLs](docs/11-cloud-and-aws/security-groups-network-acls.md).

## Emission boundary — telemetry

Hranica, na ktorej source process alebo component vytvoril log, metric, Event, audit record alebo trace pred ďalším zberom a transportom. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

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

## Encryption-context binding

Cryptographic väzba ciphertext operation na exact non-secret key-value context, ktorý musí byť zhodný pri decrypt a môže byť použitý v KMS policy/grant conditions. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Encryption context — KMS

Non-secret key-value context kryptograficky viazaný na podporovanú KMS encrypt/decrypt operation a použiteľný v policy conditions a audite. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Encryption in transit

Cryptographic ochrana dát počas prenosu medzi endpoints, typicky spolu s peer alebo server identity validation a channel integrity. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## Encryption type — Kerberos

Cryptographic algorithm a associated key semantics používané pre Kerberos long-term keys, tickets alebo session keys. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## End-to-end alert acceptance

Dôkaz, že controlled signal vytvorí intended alert state, jednu správne routovanú external notification, acknowledgement a resolved closure bez forbidden muting alebo duplicate incidentu. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## End-to-end test

Test workflow prechádzajúci cez viac produkčne relevantných vrstiev alebo procesných hraníc od vstupu po observable výsledok. Pozri [End-to-end a acceptance tests](docs/04-testing-and-quality/end-to-end-and-acceptance-tests.md).

## End-User — OIDC

Používateľ, ktorého authentication event OpenID Provider potvrdzuje Relying Party. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md).

## Endpoint-cohort subject

Full union EndpointSlices pre jeden Service a generation, vrátane targetRef UIDs, addresses, ports, conditions, topology a ownership metadata. Pozri [Service a EndpointSlice](../docs/09-kubernetes/service-endpointslice.md).

## Endpoint condition lifecycle

Transition medzi endpoint states `ready`, `serving` a `terminating` spolu s dataplane propagation a connection-drain behaviorom. Pozri [Service a EndpointSlice](../docs/09-kubernetes/service-endpointslice.md).

## Endpoint-drain generation

Versionovaný stav spájajúci readiness removal, EndpointSlice conditions, dataplane/LB propagation, existing connections a Pod termination. Pozri [Service a EndpointSlice](../docs/09-kubernetes/service-endpointslice.md).

## Endpoint readiness — Kubernetes

EndpointSlice condition signalizujúci, či je backend vhodný pre bežný Service traffic podľa Pod readiness a publication policy. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## Endpoint-readiness propagation

Asynchrónny chain z readiness attemptu cez container/Pod conditions a EndpointSlice conditions po Service alebo external load-balancer traffic eligibility. Pozri [Probes](../docs/09-kubernetes/probes.md).

## Endpoint remap — RDS

Failover transition, pri ktorom logical RDS endpoint zostáva rovnaký, ale DNS mapping začne smerovať na promoted primary/writer; clients musia obnoviť DNS a connections. Pozri [Amazon RDS](docs/11-cloud-and-aws/rds.md).

## Endpoint replacement proof

Dôkaz, že po replacement-e alebo drain-e Docker DNS a caller connection state prestali používať stale endpoint a traffic smeruje iba na aktuálnu ready generation. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Endpoint target identity

Backend endpoint identifikovaný nielen IP adresou, ale aj targetRef UID, port, address family, Node a application generation. Pozri [Service a EndpointSlice](../docs/09-kubernetes/service-endpointslice.md).

## EndpointSlice

Namespaced `discovery.k8s.io` object reprezentujúci časť backend endpointov Service-u vrátane addresses, ports, conditions a topology metadata. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## EndpointSlice eligibility subject

Versionovaný stav Pod UID v EndpointSlice vrátane targetRef, addresses a readiness/serving/terminating conditions pre konkrétny Service a workload generation. Pozri [Pod](docs/09-kubernetes/pod.md).

## EndpointSlice ownership generation

Controller alebo custom owner a jeho versionovaný lifecycle pre creation, update a cleanup EndpointSlices. Pozri [Service a EndpointSlice](../docs/09-kubernetes/service-endpointslice.md).

## EndpointSlice revision cohort

Množina endpoint Pod UIDs patriacich jednej Deployment/ReplicaSet revision, používaná na koreláciu trafficu a telemetry s konkrétnym template digestom. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## Enforcement boundary — resource

Vrstva, na ktorej sa reálne presadzuje resource limit alebo quota, napríklad cgroup, Node, connection pool, Availability Zone alebo cloud account. Pozri [USE method](docs/12-observability/use-method.md).

## Enforcement-path coverage

Dôkaz, že authorization decision je presadený na každej skutočnej API, data-plane, delegated alebo alternate ceste ku chránenému side effectu. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Enforcement-point verdict — Kubernetes networking

Allow alebo drop rozhodnutie pre exact packet/flow v konkrétnom pre-NAT alebo post-NAT observation pointe dataplane-u. Pozri [CNI a NetworkPolicy](../docs/09-kubernetes/cni-networkpolicy.md).

## Enforcing mode

Režim SELinux alebo AppArmor policy, v ktorom sa zakázané operácie blokujú. Pozri [SELinux a AppArmor](docs/01-linux-and-systems/selinux-and-apparmor.md).

## ENI identity subject

Elastic network interface identity zahŕňajúca ENI ID, private/public addresses, subnet/AZ, Security Groups, attachment, MAC a flow-log observation fields. Instance alebo managed-service lifecycle nemusí byť totožný s ENI lifecycle-om. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## Entitlement

Konkrétne oprávnenie, role, group membership alebo capability, ktorú možno prideliť principalu. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Entitlement catalog

Governed inventory assignable roles, groups a capabilities s purpose, actions, scope, ownerom, eligibility, activation, conflicts, review, tests a retirement contractom. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Entitlement desired generation

Complete desired identity-to-entitlement graph vypočítaný z authoritative identity, job-function, ownership a policy state-u pre konkrétny reconciliation cycle. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Entity ID — SAML

Stabilný identifier SAML Identity Providera alebo Service Providera používaný v metadata a issuer/audience trust contracte. Pozri [SAML](docs/13-security-and-identity/saml.md).

## Envelope encryption

Model, v ktorom data key šifruje application data a dlhodobejší KMS key šifruje samotný data key. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Envelope-encryption subject

Exact payload/ciphertext, plaintext a encrypted data-key identity, protecting KMS key/material, encryption context a caller/service path potrebné na encrypt/decrypt reasoning. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Environment drift

Rozdiel medzi deklarovaným desired state environmentu a jeho skutočným runtime stavom, napríklad po manuálnej config alebo infrastructure zmene. Pozri [Environment a promotion](docs/05-ci-cd-and-release/environment-and-promotion.md).

## Environment identity — GitLab

Kanonické mapovanie GitLab environment name a tieru na skutočný cloud account, cluster, namespace, region, data/config boundary, ownera, protection policy a runtime identity. Pozri [Environments, deployments a releases](docs/06-gitlab/environments-deployments-releases.md).

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

## Environment-snapshot boundary

Prechod pri vytvorení container processu, keď ConfigMap/Secret values vložené cez environment tvoria nemenný process environment a neskorší API update ich nezmení. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

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

Nahraditeľná runtime inštancia, ktorej process a writable-layer state nie je jediným persistentným zdrojom dát. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Ephemeral storage request

Deklarovaná požiadavka Podu alebo containeru na Node-local ephemeral storage používaná pri scheduling-u a resource accounting-u. Pozri [Requests, limits a QoS](docs/09-kubernetes/requests-limits-qos.md).

## Ephemeral volume — Kubernetes

Volume s lifecycle viazaným na Pod alebo konkrétnu projection, napríklad `emptyDir`, ConfigMap/Secret projection alebo generic ephemeral volume. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## EPSS

Exploit Prediction Scoring System; pravdepodobnostný signal odhadujúci šancu, že publikovaná CVE bude v blízkom časovom horizonte pozorovaná ako exploatovaná, nie všeobecný business-impact score. Pozri [Vulnerability a patch management](docs/13-security-and-identity/vulnerability-and-patch-management.md).

## Equal labels — Alertmanager

Labels, ktorých hodnoty musia byť zhodné medzi source a target alertom, aby sa aplikovala inhibition. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Error numerator contract — RED

Explicitná definícia failed outcomes, result classes, partial/unknown states a scope-u používaného v čitateli error ratio. Pozri [RED method](docs/12-observability/red-method.md).

## Error provenance — certification

Klasifikácia mechanizmu chyby, napríklad stale guide assumption, missed constraint, wrong scope, incomplete path, policy error, trade-off error alebo time-budget failure. Pozri [AWS Certified CloudOps Engineer – Associate](docs/11-cloud-and-aws/cloudops-engineer-associate-soa-c03.md).

## Error rate — RED

Podiel failed operations voči relevantnému počtu valid operations pri rovnakom scope-e a success contracte. Pozri [RED method](docs/12-observability/red-method.md).

## ETag

HTTP validator reprezentácie používaný na cache revalidation a optimistic concurrency cez conditional requests. Pozri [HTTP](docs/02-networking-and-web/http.md).

## etcd compaction marker — restore

Restore voľba označujúca staršiu revision históriu ako compacted, aby watchers vykonali relist namiesto používania stale cache assumptions. Pozri [etcd backup a restore](docs/09-kubernetes/etcd-backup-restore.md).

## etcd latency amplification loop

Reinforcing failure loop, v ktorom pomalé etcd commits zvyšujú API latency, watch reconnects a controller retries, čím rastie ďalší API a storage pressure. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## etcd member health

Stav konkrétneho etcd člena z pohľadu endpoint dostupnosti, Raft membership, leader/quorum participation, revision a disk/network health. Pozri [etcd backup a restore](docs/09-kubernetes/etcd-backup-restore.md).

## etcd persistence subject

Identita Kubernetes persistence transitionu zahŕňajúca etcd cluster/member IDs, leader, revision, quorum, API request, object/resourceVersion, disk/network health a commit outcome. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

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

## Evidence completeness

Kontrola, že pre presný candidate existuje celý očakávaný manifest required testov, scanov, shardov, reports a tool execution statusov. Pozri [Continuous Deployment](docs/05-ci-cd-and-release/continuous-deployment.md).

## Evidence coverage

Preukázaný set accounts, Regions, resources, event categories, log groups, metrics, cohorts a retention windows, ktoré observability/audit design skutočne zbiera; neprítomný selector alebo source nemožno nahradiť neskorším query. Pozri [Amazon CloudWatch a AWS CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## Evidence cut-off — architecture review

Časová hranica určujúca, ktoré configuration, telemetry, test, incident, cost a policy evidence patria do konkrétnej review generation. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Evidence-driven review

Architektúrny review, v ktorom odpovede podporujú aktuálne configuration, telemetry, tests, policies, incidents a ďalšie overiteľné dôkazy. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Evidence freshness

Pravidlá určujúce, či evidence stále patrí k aktuálnemu candidate, artifactu, policy a target environment stateu a ešte neprekročila definovanú expiráciu. Pozri [Continuous Deployment](docs/05-ci-cd-and-release/continuous-deployment.md).

## Evidence manifest

Explicitný zoznam required a optional evidence položiek pre konkrétny gate subject vrátane subject identity, tool statusu, completion, timestamps, integrity a exception references. Pozri [Quality gates a approvals](docs/05-ci-cd-and-release/quality-gates-and-approvals.md).

## Evidence placement

Rozhodnutie, v ktorej najskoršej vrstve delivery možno získať dostatočne spoľahlivý dôkaz bez odstránenia relevantnej failure boundary. Pozri [Shift-left](docs/04-testing-and-quality/shift-left.md).

## Evidence preservation — CKA

Zachovanie object YAML, status/conditions, Events, current/previous logs, host/runtime state a časovej identity pred restartom, delete alebo force zásahom.

## Evidence preservation — Docker incident

Zachovanie inspect dát, logs, events, versions, image digestov, resource a host evidence pred restartom, delete alebo prune operáciou. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Evidence preservation — Kubernetes

Zachovanie object statusu, Events, logs, metrics, timestamps a configuration pred restartom, delete, rollbackom alebo restore operáciou. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Evidence-preserving containment — CloudOps

Dočasná bounded action zastavujúca rast dopadu pri zachovaní forensic, rollback a recovery options. Pozri [CloudOps troubleshooting drills](docs/11-cloud-and-aws/cloudops-troubleshooting-drills.md).

## Evidence-preserving security containment

Bounded action, ktorá zastaví pokračujúci security impact a exposure bez zničenia session, identity, policy, workload, data a audit evidence potrebnej na reconstruction. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Exact-search exception — cardinality

Schválené použitie high-cardinality field-u pre bounded exact log, trace alebo document search bez jeho promotion do metrics, Loki streams, alerts alebo unrestricted aggregations. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Exact trace lookup

Query konkrétneho trace ID odlíšená od broad attribute searchu a validovaná voči tenant, recent/historical path a storage generation. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Exam-guide generation — SOA-C03

Konkrétna revision AWS SOA-C03 exam guide-u s publication date, domain/task obsahom a in-scope/out-of-scope service inventory, ku ktorej musí byť viazaný study a readiness evidence. Pozri [AWS Certified CloudOps Engineer – Associate](docs/11-cloud-and-aws/cloudops-engineer-associate-soa-c03.md).

## Exam simulation — CKA

Plný časovo a pravidlami ohraničený tréning napodobňujúci performance-based exam workflow bez používania dôverných reálnych exam otázok. Pozri [CKA timed labs](docs/10-helm-and-cka/cka-timed-labs.md).

## Exam-version staleness

Stav, keď study material, question explanation alebo service assumption vychádza zo staršej exam generation a už nemusí zodpovedať current task alebo service scope-u. Pozri [AWS Certified CloudOps Engineer – Associate](docs/11-cloud-and-aws/cloudops-engineer-associate-soa-c03.md).

## Exception chaining — Python

Zachovanie pôvodnej exception ako príčiny novej kontextovej exception cez `raise ... from ...`. Pozri [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Exclusive runtime slot

Recreate deployment model, v ktorom môže konkrétny service alebo writer ownership v jednom okamihu patriť iba starej generácii, prázdnemu maintenance stavu alebo novej generácii. Odstraňuje mixed-version overlap za cenu capacity gapu. Pozri [Recreate deployment](docs/05-ci-cd-and-release/recreate-deployment.md).

## Exec probe

Kubernetes probe spúšťajúca command v container environment-e a vyhodnocujúca jeho exit status. Pozri [Probes](docs/09-kubernetes/probes.md).

## Executable policy

Machine-readable formalizácia policy intentu s presným input schema, scope, decision a failure semantics. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Executable specification

Príklad alebo pravidlo zapísané vo forme, ktorú možno automaticky spustiť ako dôkaz behavior. Pozri [End-to-end a acceptance tests](docs/04-testing-and-quality/end-to-end-and-acceptance-tests.md).

## Execution contract — job

Deklarované runtime, inputs, permissions, resources, timeout, retries, outputs, success criteria a cleanup semantics jedného samostatne plánovaného jobu. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## Execution-delivery verdict — Systems Manager

Dôkaz, či control-plane request bol prijatý, target resolve-nutý, invocation doručená agentovi a plugin/script skutočne začal; je oddelený od exit statusu aj application outcome-u. Pozri [AWS Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## Execution environment — Ansible

Versionovaný runtime image alebo prostredie obsahujúce `ansible-core`, Python dependencies, collections a system tools potrebné na reprodukovateľné vykonanie automation. Pozri [Ansible architecture](docs/07-infrastructure-as-code-and-configuration-management/ansible-architecture.md).

## Execution-environment generation

Konkrétna Lambda runtime environment population viazaná na function version/configuration, runtime, extensions, architecture, VPC a initialization state; warm reuse nie je durable-state garancia. Pozri [AWS Lambda](docs/11-cloud-and-aws/lambda.md).

## Execution path — CKA

Najkratšia bezpečná séria generatorov, editácií, client/server validations a mutations vedúca k požadovanému state-u.

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

## Expected context inventory

Vopred validovaná množina paths a named contexts, ktoré musia alebo nesmú byť dostupné builderu. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Expected evidence inventory — review

Vopred definované observation sources, owners, freshness limits a allowed/forbidden outcomes potrebné na zodpovedanie review questions. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Expected evidence inventory — Terraform

Vopred definovaná množina testov, reportov, planov, policy verdictov, cleanup výsledkov a runtime overení požadovaných pre konkrétnu risk class. Chýbajúca položka znamená incomplete evidence, nie pass. Pozri [Terraform testing a policy](docs/07-infrastructure-as-code-and-configuration-management/terraform-testing-and-policy.md).

## Expected Helm evidence inventory

Vopred definovaný zoznam dôkazov, ktoré musia vzniknúť pre konkrétny immutable release subject: artifact a lock digests, effective values, rendered manifest, admission verdict, hook results, live generations, runtime cohorts a business/forbidden outcomes. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Expected job inventory — GitLab CI

Explicitný manifest jobs, child pipelines a reports, ktoré musia pre konkrétny pipeline subject existovať alebo preukázateľne nebyť applicable. Odlišuje complete pass od false-green runu s ticho chýbajúcou evidence. Pozri [GitLab CI/CD syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md).

## Expected job inventory — GitLab CI/CD

Strojovo overiteľná množina jobs, shards, child pipelines a reports, ktoré musia pre konkrétny configuration subject vzniknúť alebo byť explicitne označené ako not applicable. Odlišuje complete pass od false-green pipeline s chýbajúcou evidence. Pozri [GitLab CI/CD syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md).

## Expected output inventory — GitLab CI

Manifest artifacts, reports, shards, variants alebo platforms, ktoré musí konkrétny producer/fan-in workflow vytvoriť. Actual-only agregácia bez tohto manifestu môže ticho vyhodnotiť missing output ako pass. Pozri [Artifacts a cache](docs/06-gitlab/artifacts-and-cache.md).

## Expected resource manifest — CloudOps lab

Vopred deklarovaný inventory resource names/ARNs, Regions/AZs, dependencies, retained evidence a expected cost drivers používaný pri validation a cleanup-e. Pozri [CloudOps hands-on labs](docs/11-cloud-and-aws/cloudops-hands-on-labs.md).

## Expected result inventory

Pred vykonaním fan-out-u deklarovaná množina required a optional result identities pre konkrétny immutable subject. Fan-in ju porovnáva s prijatými výsledkami, aby odhalil chýbajúci, duplicitný, stale alebo nevytvorený job či shard. Pozri [Reusable a parallel pipelines](docs/05-ci-cd-and-release/reusable-and-parallel-pipelines.md).

## Expected scanner inventory — GitLab

Manifest security controls, analyzer jobs, reportov, componentov a platforiem, ktoré musia existovať alebo mať explicitný not-applicable/unsupported verdict pre konkrétny scan subject. Chýbajúca položka znamená incomplete evidence, nie clean result. Pozri [Security scanning](docs/06-gitlab/security-scanning.md).

## Expected stage evidence inventory

Množina build, test, analysis, target a per-platform verdictov požadovaných pre release; missing evidence nie je pass. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## Expected-state contract — drill

Versionovaný initial a desired state vrátane fault injectionu, misleading evidence, forbidden changes, hard validation a reset procedúry.

## Expected target generation — Prometheus

Versionovaný inventory endpoints, ktoré majú po service discovery a target relabelingu zostať eligible na scrape. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Expected target inventory — Ansible

Očakávaná množina alebo invariant targetov pred runom, napríklad stable host IDs, count bounds, AZ/ring coverage, forbidden overlaps, allowed lifecycle states a maximum cache age. Porovnáva sa s resolved, attempted a verified host inventory. Pozri [Inventory](docs/07-infrastructure-as-code-and-configuration-management/inventory.md).

## Experiment contract

Explicitný popis hypotézy, steady state, faultu, scope, blast radiusu, trvania, abort criteria, recovery, ownershipu a dôkazov chaos experimentu. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Experiment integrity

Platnosť assignment, exposure, measurement a population boundaries potrebná pred interpretáciou experimentálneho effect estimate-u. Porušenie môže zmeniť experiment na invalidný aj pri priaznivom primary outcome. Pozri [A/B testing](docs/05-ci-cd-and-release/a-b-testing.md).

## Experiment unit

Entita randomizovaná do variantu experimentu, napríklad používateľ, tenant, device, session alebo región. Musí zodpovedať hranici možného treatment efektu. Pozri [A/B testing](docs/05-ci-cd-and-release/a-b-testing.md).

## Experiment validity

Vlastnosť experimentu, pri ktorej baseline, target, fault, workload a observation zodpovedajú deklarovanému contractu natoľko, aby výsledok mohol potvrdiť alebo vyvrátiť hypotézu. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Expiring risk acceptance

Explicitné prijatie residual risku accountable ownerom s rationale, compensating controls, expiry a re-review triggers. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Explicit deny — IAM

Policy statement s `Effect: Deny`, ktorý pre applicable request prevažuje nad explicitnými allows v ostatných vyhodnocovaných policy vrstvách. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## Exploitability status

Machine-readable tvrdenie o tom, či a prečo je konkrétna vulnerability relevantná pre konkrétny artifact alebo product context. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## Exporter contract — BuildKit

Contract určujúci, ktorý graph result sa musí exportovať, do akého destinationu a formátu, pod akou immutable identity, s akou retention a read-back verification. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Exporter-delivery subject — OpenTelemetry

Exact signal, queue, exporter component/version, endpoint, credential, tenant, acknowledgement, retry a backend read-back identity. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

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

## External binding subject — Kubernetes controller

Versionovaná väzba medzi Kubernetes owner UID/generation a external resource ID, operation/idempotency key, owned fields, provider target a cleanup status. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## External build cache

Build cache exportovaná mimo lokálneho buildera, napríklad do registry alebo CI backendu, s vlastnou access, trust, namespace a retention policy. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## External cache trust domain

Boundary určujúca identities oprávnené čítať/zapisovať build cache a release classes, pre ktoré je reuse prípustný. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## External incident identity

Stable receiver/on-call key, ktorý viaže duplicate HA notifications a firing/resolved updates k jednému operational incidentu. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## External labels — Prometheus

Labels pridávané Prometheus serverom pri komunikácii s externými systémami na identifikáciu clusteru, Regionu, tenant-u alebo replica topology. Pozri [Prometheus](docs/12-observability/prometheus.md).

## External metric — HPA

Metric pochádzajúca mimo Kubernetes object modelu, sprístupnená HPA cez external metrics API adapter. Pozri [HPA a autoscaling](docs/09-kubernetes/hpa-autoscaling.md).

## External resource — Compose

Network, volume, config alebo secret deklarovaný ako vlastnený mimo aktuálneho Compose projektu; Compose ho používa, ale nemá automaticky riadiť jeho celý lifecycle. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## External resource preflight

Kontrola external Compose networku, volume-u, configu alebo secretu pred deploymentom vrátane existence, environmentu, ownera, permissions, compatibility a cleanup zodpovednosti. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## External secret provider

Systém mimo Kubernetes API, ktorý vydáva alebo uchováva citlivé hodnoty a sprístupňuje ich workloadu cez synchronizáciu, CSI projection alebo runtime fetch s workload identity. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## External secret provider — GitLab CI/CD

Secret-management systém, z ktorého job explicitne načíta citlivú hodnotu po overení federovanej alebo inej scoped identity. Pozri [Variables a secrets](docs/06-gitlab/variables-and-secrets.md).

## External side-effect commit — Helm

Bod, v ktorom hook durable zmení databázu, queue, external API alebo inú autoritatívnu vrstvu bez ohľadu na to, či Helm následne zaznamená successful hook alebo release status. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## External-state reconciliation — etcd recovery

Post-restore porovnanie restored Kubernetes objects s cloud disks, load balancermi, DNS, certificates, IAM, databases a ďalšími external resources pred povolením controller mutations a trafficu. Pozri [etcd backup a restore](../docs/09-kubernetes/etcd-backup-restore.md).

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

## Failback authority transfer

Riadený presun authoritative data a writer/traffic ownershipu z recovery prostredia späť do primary prostredia po synchronizácii, compatibility a single-writer verifikácii. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

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

Postup zmenšujúci možné príčiny podľa scope-u: container, Pod, workload, Node, request class alebo cluster.

## Failure-domain narrowing — CKA

Postupné zužovanie incidentu z clusteru, Node-u, workloadu, Podu alebo containeru na konkrétny owner component a failure layer. Pozri [CKA troubleshooting drills](docs/10-helm-and-cka/cka-troubleshooting-drills.md).

## Failure-mode capacity

Kapacita, quota, IP space a compatible resource inventory dostupný po strate definovaného failure domainu, nie iba počas healthy steady state-u. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

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

Bod pipeline grafu, v ktorom downstream job čaká na výsledky viacerých upstream jobs alebo shards a overuje ich úplnosť. Pozri [Reusable a parallel pipelines](docs/05-ci-cd-and-release/reusable-and-parallel-pipelines.md).

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

## Fault-injection generation

Versionovaný mechanizmus vytvárajúci jednu presnú authoritative chybu s deterministickým apply/reset a známym expected state-om.

## Fault tolerance

Schopnosť systému pokračovať vo funkcii pri zlyhaní componentu prostredníctvom redundancy, replication, automatic failover, isolation a controlled retry. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Feasible Node

Node, ktorý prešiel všetkými aktívnymi scheduler filter constraints pre konkrétny Pod a môže pokračovať do scoring fázy. Pozri [Scheduling](docs/09-kubernetes/scheduling.md).

## Feasible-Node set

Množina Nodes, ktoré po aplikovaní všetkých hard scheduler constraints môžu hostiť konkrétny Pod scheduling subject. Pozri [Scheduling](../docs/09-kubernetes/scheduling.md).

## Feature branch

Dočasná branch určená na izolovaný vývoj jednej zmeny. Pri trunk-based modeli má byť krátkodobá a často integrovaná. Pozri [Branching strategies](docs/03-git-and-automation/branching-strategies.md).

## Feature flag

Runtime control oddeľujúci deployment kódu od sprístupnenia capability pomocou versionovaného evaluation pravidla. Pozri [Feature flags](docs/05-ci-cd-and-release/feature-flags.md).

## Federation

Trust model, v ktorom relying party prijíma authentication assertion alebo token od samostatne spravovaného identity provider-a. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Federation — Prometheus

Hierarchický model, v ktorom jeden Prometheus scrape-ne vybrané series z federation endpointu iného Prometheus servera. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Federation trust-policy generation

Versionovaný external identity-provider contract určujúci akceptovaný issuer, audience, namespace, ServiceAccount subject a odvodenú external rolu. Pozri [ServiceAccount](../docs/09-kubernetes/serviceaccount.md).

## Feedback loop

Cesta od vykonanej zmeny k informácii o jej výsledku. Pozri [Feedback Loops](docs/00-foundations/feedback-loops.md).

## Fencing epoch — stateful workload

Authority term alebo generation, ktorá odlišuje aktuálneho oprávneného writera/membera od stale processu s rovnakým ordinalom alebo storage identity. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Fencing token

Monotónna alebo unikátna lease identity overovaná pred každou environment mutation, ktorá zabráni starému deployment ownerovi pokračovať po strate alebo expirácii locku. Pozri [Environment a promotion](docs/05-ci-cd-and-release/environment-and-promotion.md).

## Field — Grafana

Jedna typed column alebo series v Grafana data frame s values, labels a display konfiguráciou. Pozri [Grafana](docs/12-observability/grafana.md).

## Field manager — Kubernetes

Identita declarative alebo programmatic writera zaznamenaná v `managedFields`, ktorá vlastní konkrétne object fields pri server-side apply. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Field ownership subject — Kubernetes

Rekonštruovateľný inventory field managers, owned object paths, subresources, conflicts, force transfers a authoritative team/controller pre konkrétnu object UID/generation. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Field-semantics contract — Grafana

Explicitný vzťah medzi raw value, reducerom, unitom, mappings, thresholds a rendered operational meaningom. Pozri [Grafana](docs/12-observability/grafana.md).

## File capability

Capability metadata uložené na executable súbore v extended attribute. Pozri [Linux capabilities](docs/01-linux-and-systems/linux-capabilities.md).

## File descriptor

Malé celé číslo v procese odkazujúce na kernelom spravovaný otvorený objekt. Pozri [Shell, Bash, pipes, redirection a exit codes](docs/01-linux-and-systems/shell-bash-pipes-redirection-exit-codes.md).

## File-type variable — GitLab

CI/CD variable, ktorej hodnota je zapísaná do dočasného súboru a environment variable obsahuje path k tomuto súboru. Pozri [Variables a secrets](docs/06-gitlab/variables-and-secrets.md).

## Filesystem

Štruktúra mapujúca pathname na metadata a dátové bloky. Pozri [Filesystem hierarchy, inodes a links](docs/01-linux-and-systems/filesystem-hierarchy-inodes-links.md).

## Filesystem access verdict — Kubernetes

Výsledok kombinácie process UID/GID/groups, Unix permissions/ACL, mount flags, CSI ownership, user-namespace mapping a SELinux/AppArmor policy pre exact path a operation. Pozri [SecurityContext a Pod Security](../docs/09-kubernetes/securitycontext-pod-security.md).

## Filesystem-backlog generation — Fluent Bit

Množina persistentných local chunks, ich age, size, output references a storage limits počas backend backpressure alebo outage. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Filesystem buffering — Fluent Bit

Buffering telemetry chunks na local filesystem na zvýšenie backlog capacity a restart recovery oproti memory-only modelu. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Filesystem transition — Dockerfile

Build-time zmena stage filesystemu cez `COPY`, `ADD` alebo `RUN`, ktorá vstupuje do layer graphu a môže preniesť content, ownership, permissions alebo secret residue. Pozri [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md).

## Filter-order contract — Fluent Bit

Versionované poradie parse, enrichment, normalization, redaction, cardinality control a routing filters, ktoré určuje final record a security outcome. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Filter plugin — Kubernetes scheduler

Scheduling Framework plugin vyhodnocujúci, či konkrétny Node spĺňa hard constraints Podu. Pozri [Scheduling](docs/09-kubernetes/scheduling.md).

## Final-outcome class — RED

Klasifikácia logical operation ako definitive success, definitive failure, partial success, cancellation, timeout, success after retry alebo iný finálny contract verdict. Pozri [RED method](docs/12-observability/red-method.md).

## Final stage — Dockerfile

Stage, ktorého filesystem a image config tvoria publikovaný runtime image; má obsahovať iba potrebné runtime artifacts a dependencies. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## Finalizer-before-create invariant

Controller invariant vyžadujúci durable finalizer/cleanup ownership pred vytvorením external state-u, aby delete alebo crash nemohli zanechať resource bez recoverable ownera. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Finalizer cleanup contract

Contract medzi object deletion a controllerom určujúci exact external/dependent inventory, cleanup operation, verification a podmienku bezpečného odstránenia finalizeru. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Finalizer — Kubernetes

Qualified metadata string blokujúci finálne odstránenie objectu, kým zodpovedný controller nedokončí cleanup a finalizer neodstráni. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Financial data freshness

Informácia o delay, estimated/finalized state a late adjustments cost datasetu potrebná pred budget, anomaly alebo incident decisionom. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Financial safety boundary — AWS lab

Kombinácia sandbox isolation, bounded permissions/quotas, budget signals, TTL, cost-driver observation a cleanup contractu obmedzujúca finančný blast radius experimentu. Pozri [CloudOps hands-on labs](docs/11-cloud-and-aws/cloudops-hands-on-labs.md).

## FinOps

Operating model spájajúci engineering, finance a business pri rozhodovaní o cloud value, cost, usage a trade-offoch. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## FinOps closure verdict

Dôkaz, že cost driver bol kauzálne identifikovaný, change bezpečne nasadený, business/SLO guardrails zachované a normalized realized value potvrdená v complete data periods. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## FinOps subject

Versionovaná identita payer/workloadu, billing period/dataset, pricing, allocation, commitments, business unit, owners, SLO guardrails a expected value outcome. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Firing alert

Alert instance, ktorej condition zostala aktívna podľa požadovaných time semantics a je pripravená na notification routing. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## First-attempt pass rate

Podiel testov, ktoré prejdú na prvý pokus bez retry. Je citlivejším signálom flakiness než finálna pass rate po opakovaniach. Pozri [Flaky tests a test data](docs/04-testing-and-quality/flaky-tests-and-test-data.md).

## First-match routing verdict — ALB

Výsledok ordered listener-rule evaluation, pri ktorom prvá matching rule určí action; broad higher-priority rule môže shadowovať presnejšiu canary rule. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## Flag debt

Kumulovaná komplexita starých feature flags, paralelných code paths, kombinácií stavov, testov a prevádzkových rozhodnutí po prekročení plánovaného lifecycle. Pozri [Feature flags](docs/05-ci-cd-and-release/feature-flags.md).

## Flag evaluation

Runtime rozhodnutie o variante alebo hodnote feature flagu na základe flag verzie, identity, environmentu a targeting pravidiel. Pozri [Feature flags](docs/05-ci-cd-and-release/feature-flags.md).

## Flaky test

Test, ktorý pri rovnakom kóde a deklarovaných vstupoch nedeterministicky prechádza alebo zlyháva. Pozri [Flaky tests a test data](docs/04-testing-and-quality/flaky-tests-and-test-data.md).

## Fleet convergence — Ansible

Stav, v ktorom všetky očakávané a oprávnené targety dosiahli požadovaný file, service a runtime outcome a následný run nevytvára nečakané changes. Pozri [Ansible architecture](docs/07-infrastructure-as-code-and-configuration-management/ansible-architecture.md).

## Fleet observation matrix

Mapovanie DaemonSet fleet policy, placement, runtime, host authority, node capability, rollout, bootstrap a workload outcome boundaries na ich subjects. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## Fleet-operation subject — Systems Manager

Versionovaná identita caller/session, target fleetu, managed-node enrollmentu, SSM document/runbooku, parameters, role, rate controls, command/patch/configuration generation a application validation. Pozri [AWS Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## Fleet recovery closure — EC2

Verdict, že ASG používa approved launch generation, desired/InService/serving capacity je kompatibilná, všetky AZ cohorts prešli health/business tests, bad generation je retired a druhý scale/refresh cyklus nereprodukuje failure. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Flexible Single Master Operations — FSMO

AD DS roles určené pre operácie, ktoré nemajú byť vykonávané súčasne viacerými domain controllers. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Flow control

TCP mechanizmus chrániaci receiver pred odosielaním väčšieho množstva dát, než dokáže prijať. Pozri [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md).

## Flow log — CNI

Dataplane observability záznam o povolenom alebo zamietnutom network flowe vrátane source/destination identity, portu, policy a action metadata podľa CNI implementácie. Pozri [CNI a NetworkPolicy](docs/09-kubernetes/cni-networkpolicy.md).

## Flow subject — Kubernetes networking

Exact communication identity obsahujúca source a destination Pod/Node identity, protocol, ports, direction, pre/post-NAT tuple, policy generations a connection state. Pozri [CNI a NetworkPolicy](../docs/09-kubernetes/cni-networkpolicy.md).

## Fluent Bit

Ľahký telemetry agent na inputs, parsing, filtering, buffering, routing a export logs, metrics a traces. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Fluent Bit acceptance verdict

Dôkaz, že exact sources, offsets, routes, buffers a outputs prežijú fault/restart scenáre a vytvoria queryovateľné telemetry s definovaným loss/duplicate contractom. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Fluent Bit subject

Exact Node/source, DaemonSet/config, input, inode, Tail DB, parser, tag, filter order, buffer, output, credential a acknowledgement identity analyzovanej pipeline. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Folder permission — Grafana

Prístupové pravidlo pre dashboardy a folders; samo osebe nemusí obmedziť možnosť queryovať underlying data source. Pozri [Grafana](docs/12-observability/grafana.md).

## Forbidden-authority verification

Negatívny recovery test dokazujúci, že workload po remediation nevie použiť host namespaces, runtime sockets, devices, forbidden capabilities, privileged Pod creation alebo staré credentials. Pozri [SecurityContext a Pod Security](../docs/09-kubernetes/securitycontext-pod-security.md).

## Forbidden-dimension contract

Explicitný zákaz unbounded alebo citlivej dimension v konkrétnom backend identity modeli, napríklad `merchant_id` v metric labels alebo Loki stream labels. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Forbidden feedback outcome

Explicitne zakázaný autoscaling výsledok, napríklad retry metric vytvárajúca replica/connection storm, scale-down s duplicate work alebo cross-tenant metric manipulácia. Pozri [HPA a autoscaling](../docs/09-kubernetes/hpa-autoscaling.md).

## Forbidden-operation verification — RBAC

Aktívny test, že subject po recovery nevie vykonať Secrets, exec, proxy, workload-create, RBAC-management alebo cluster-wide operations mimo schváleného contractu. Pozri [RBAC](../docs/09-kubernetes/rbac.md).

## Forbidden outcome — CKA

Stav, ktorý riešenie nesmie vytvoriť, napríklad zmena identity, broad authorization, vypnutie policy, strata availability alebo druhý storage writer.

## Forbidden outcome — Docker incident

Stav, ktorý recovery nesmie povoliť, napríklad duplicate business side effect, staging access z production, stale writer, broad port exposure alebo strata authoritative data. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Forbidden-outcome test — CloudOps lab

Explicitný test, že remediation nevytvorila public exposure, broad permission, duplicate side effect, missing audit alebo inú zakázanú capability. Pozri [CloudOps hands-on labs](docs/11-cloud-and-aws/cloudops-hands-on-labs.md).

## Forbidden outcome test — Helm

Negatívne acceptance overenie pre release alebo recovery, napríklad že starý credential je odmietnutý, duplicate authorization nevznikla, stale Pod UID neprijíma traffic alebo destructive hook sa nezopakoval. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Forbidden-outcome verification — Kubernetes

Dôkaz, že po remediation zostávajú zakázané flows, permissions, credentials, duplicate side effects alebo stale generations skutočne nefunkčné. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Forbidden release outcome

Explicitne zakázaný výsledok Helm release-u, napríklad aktivovaný legacy path, mutable artifact, duplicate business side effect, chýbajúci endpoint alebo secret leak. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Force unlock — Terraform

Riziková operácia odstránenia backend locku podľa lock ID bez ukončenia pôvodného procesu; smie sa použiť iba po potvrdení, že pôvodný writer už neexistuje. Pozri [Remote backend a state locking](docs/07-infrastructure-as-code-and-configuration-management/remote-backend-and-state-locking.md).

## Force-with-lease

Bezpečnejšia forma force pushu, ktorá aktualizuje remote ref iba vtedy, keď stále zodpovedá očakávanej hodnote. Stále ide o history rewrite. Pozri [Clone, fetch, pull a push](docs/03-git-and-automation/clone-fetch-pull-push.md).

## Foreign Pod — ReplicaSet

Pod, ktorý matchuje selector, ale vlastní ho iný controller alebo nespĺňa adoption pravidlá, takže ho konkrétny ReplicaSet nemá autoritatívne riadiť. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Forest — AD DS

Najvyššia AD DS logical a významná security boundary združujúca domains so spoločnou schema, configuration a Global Catalog modelom. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Forest recovery

Koordinovaný recovery proces na obnovu dôveryhodného AD DS forest-u po rozsiahlej corruption alebo compromise udalosti. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Forward-fix migration

Nová databázová migration opravujúca chybný alebo neúplný aktuálny stav bez pokusu mechanicky vrátiť predchádzajúcu schema. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Forward proxy

Proxy zastupujúci klienta pri komunikácii s externými servermi. Pozri [Proxy a reverse proxy](docs/02-networking-and-web/proxy-and-reverse-proxy.md).

## Forward/return path contract — AWS

Požiadavka, aby presný flow mal kompatibilnú route, policy a stateful-inspection cestu v oboch smeroch; forward reachability sama connection nepreukazuje. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## Forward secrecy

Vlastnosť key-establishment modelu, pri ktorej neskorší compromise dlhodobého private keyu neumožní dešifrovať predtým zachytené sessions. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## FQCN — Ansible

Fully Qualified Collection Name explicitne identifikujúci module, plugin alebo iný content cez namespace, collection a object name, napríklad `ansible.builtin.template`. Pozri [Modules, tasks, plays a playbooks](docs/07-infrastructure-as-code-and-configuration-management/modules-tasks-plays-playbooks.md).

## Fresh-connection verdict

Dôkaz, že nový lookup a nová connection použili accepted address a dosiahli správny Service alebo external backend; samotný lookup nestačí. Pozri [Cluster DNS](../docs/09-kubernetes/cluster-dns.md).

## Fresh-flow revocation test

Negatívne overenie, že po odstránení allow pathu nový connection attempt zlyhá, oddelene od testu existujúcich long-lived alebo pooled sessions. Pozri [Security Groups a Network ACLs](docs/11-cloud-and-aws/security-groups-network-acls.md).

## Front-channel logout

OIDC logout model využívajúci browser na komunikáciu s logout endpoints jednotlivých clients. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md).

## `fsGroup`

Pod security context group identity používaná pri ownership a access nastavení podporovaných mounted volumes. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## Fulcio

Sigstore certificate authority vydávajúca short-lived code-signing certificates pre overené OIDC identities. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Functional readiness

Dôkaz, že instance alebo nová generácia dokáže bezpečne vykonať kritický service outcome vrátane relevantnej identity, dependency, read/write a idempotency cesty. Je prísnejšia než process start, liveness alebo otvorený port. Pozri [Recreate deployment](docs/05-ci-cd-and-release/recreate-deployment.md) a [Rolling update](docs/05-ci-cd-and-release/rolling-update.md).

## Game day

Plánované tímové resilience cvičenie kombinujúce technické faults, observability, incident response, komunikáciu a následné learning actions. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Garbage collection — Kubernetes

Control-plane proces odstraňujúci dependent objects podľa owner references a deletion propagation policy. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Garbage collection — registry

Odstraňovanie manifestov alebo blobs, ktoré nie sú reachable z retained references, koordinované s pushes, deletes, referrers a retention policy. Pozri [Registries](docs/08-container-fundamentals-and-docker/registries.md).

## Gate decision contract

Model rozhodnutia spájajúci immutable subject, expected evidence manifest, applicability, freshness, versioned policy a rozhodovaciu authority do explicitného viacstavového verdictu. Pozri [Quality gates a approvals](docs/05-ci-cd-and-release/quality-gates-and-approvals.md).

## Gate subject

Presná immutable alebo versionovaná entita hodnotená gate-om, napríklad candidate SHA, release manifest digest, rendered configuration, environment revision alebo rollout cohort. Pozri [Quality gates a approvals](docs/05-ci-cd-and-release/quality-gates-and-approvals.md).

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

## Gateway listener subject

Konkrétny Gateway UID, listener section, address, port, protocol, hostname, TLS a allowed-route boundary. Pozri [Ingress a Gateway API](../docs/09-kubernetes/ingress-gateway-api.md).

## Gateway Load Balancer — GWLB

Elastic Load Balancing variant pre transparentné smerovanie flows cez virtual network appliances pomocou GENEVE encapsulation. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## GatewayClass

Cluster-scoped Gateway API resource vyberajúci controller implementation a class-level lifecycle pre Gateway objekty. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## Gauge — metric

Metric hodnota, ktorá môže rásť aj klesať a reprezentuje napríklad aktuálnu queue depth, memory usage alebo počet connections. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## GC reachability snapshot — registry

Konzistentný pohľad na retained tags, manifests, blobs, referrers, uploads, leases, deployments a rollback subjects pre GC rozhodnutie. Pozri [Registries](docs/08-container-fundamentals-and-docker/registries.md).

## Generated graph completeness

Dôkaz, že dynamický pipeline generator analyzoval deklarovaný scope, zachoval required gates, vytvoril všetkých potrebných producers/consumers a explicitne uviedol preskočené components. Pozri [Pipeline as Code](docs/05-ci-cd-and-release/pipeline-as-code.md).

## Generation closure

Stav, keď controller observed generation, dependent object graph, effective runtime a acceptance evidence všetky zodpovedajú aktuálnemu `metadata.generation`. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

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

## GitOps deployment correlation — GitLab

Väzba medzi source pipeline, release manifestom, desired-state repository commitom, controller reconciliation ID, runtime targetom a effective digestom. Odlišuje úspešný configuration request od dokončeného deploymentu. Pozri [Environments, deployments a releases](docs/06-gitlab/environments-deployments-releases.md).

## Global Catalog

AD DS capability obsahujúca partial attribute set z objects naprieč forestom pre forest-wide search a vybrané authentication/group-resolution scenáre. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Global group — AD DS

AD DS group scope typicky obsahujúci accounts z rovnakej domény a používaný na reprezentovanie business alebo job membership. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Global helper resolution — Helm

Proces výberu effective named-template definition z globálneho namespace-u parent chartu a dependencies. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

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

## Golden-Signal acceptance verdict

Dôkaz, že Latency, Traffic, Errors a Saturation používajú kompatibilné populations, original outcome je obnovený a traffic drop, duplicate effect ani telemetry absence nevytvárajú false-green stav. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Golden-Signal subject

Exact capability, workflow, valid demand population, cohort, version, measurement window a caller outcome, pre ktoré Latency, Traffic, Errors a Saturation tvoria spoločný service-health contract. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Golden Signals

Google SRE monitoring model pozostávajúci zo Latency, Traffic, Errors a Saturation pre user-facing workload. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Governance acceptance verdict — Kubernetes namespace

Verdikt, že LimitRange/ResourceQuota policy poskytuje správne admitted resources, fairness, rollout/HPA/recovery headroom, object bounds a business SLO bez neželaných defaultov. Pozri [ResourceQuota a LimitRange](../docs/09-kubernetes/resourcequota-limitrange.md).

## Governance graph

Vzťahy medzi management accountom, OUs, member accounts, delegated administrators, cross-account roles, shared networks, log archives a organization policies, ktoré určujú reálny blast radius. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Governed account lifecycle subject

Exact AWS account ID, owner, OU path, baseline generation, SCP/RCP/declarative policy set, delegated administration, Regions a allowed/forbidden outcomes od account requestu po closure. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Graceful degradation

Schopnosť systému pri nedostupnosti časti dependencies zachovať obmedzenú, ale stále užitočnú a bezpečnú funkcionalitu namiesto úplného zlyhania. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Graceful shutdown

Riadené ukončenie, pri ktorom proces prestane prijímať novú prácu, bezpečne spracuje alebo preruší rozpracovaný stav, uvoľní resources a vráti správny status. Pozri [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Graceful shutdown — telemetry agent

Riadené ukončenie inputov, flush queued chunks a uloženie offset state-u pred zastavením agenta. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Grafana

Platforma na queryovanie, vizualizáciu, alerting a interaktívne skúmanie telemetry z externých data sources. Pozri [Grafana](docs/12-observability/grafana.md).

## Grafana acceptance verdict

Dôkaz, že backend query, raw frame, transformation, unit, loaded dashboard revision, permissions a alert ownership vytvárajú správny allowed aj forbidden operational outcome. Pozri [Grafana](docs/12-observability/grafana.md).

## Grafana correlation

Konfigurácia prepájajúca fields a query context medzi metrics, logs, traces alebo ďalšími data sources počas investigation. Pozri [Grafana](docs/12-observability/grafana.md).

## Grafana Explore

Ad hoc query a investigation workspace na interaktívne skúmanie metrics, logs a traces bez vytvorenia dashboardu. Pozri [Grafana](docs/12-observability/grafana.md).

## Grafana expression

Server-side alebo alerting calculation nad výsledkami jednej či viacerých data-source queries, napríklad math, reduce, resample alebo threshold. Pozri [Grafana](docs/12-observability/grafana.md).

## Grafana HA

Multi-instance Grafana deployment so spoločnou podporovanou SQL database, konzistentnou configuration, plugins a load-balancing modelom. Pozri [Grafana](docs/12-observability/grafana.md).

## Grafana investigation path

Versionovaný drilldown chain od SLO/Golden Signals panelu cez cohort, dependency, trace/log/resource evidence až po runbook alebo incident. Pozri [Grafana](docs/12-observability/grafana.md).

## Grafana-managed alert

Alert rule uložená a vyhodnocovaná Grafana alerting engine-om nad podporovanými data sources a expressions. Pozri [Grafana](docs/12-observability/grafana.md).

## Grafana notification policy

Routing a grouping policy Grafana Alerting, ktorá mapuje alert instances na contact points podľa labels a inheritance. Pozri [Grafana](docs/12-observability/grafana.md).

## Grafana panel

Základný dashboard component kombinujúci query, transformations, field configuration a visualization. Pozri [Grafana](docs/12-observability/grafana.md).

## Grafana subject

Exact organization, folder UID, dashboard/panel UID, data-source UID, source/loaded revision, query, transformation, field config, alert owner a viewer scope. Pozri [Grafana](docs/12-observability/grafana.md).

## Grafana variable

Dashboard placeholder získaný z query, custom listu alebo iného source-u a interpolovaný do queries, titles alebo links. Pozri [Grafana](docs/12-observability/grafana.md).

## Grafana variable interpolation

Nahradenie variable jej aktuálnou hodnotou pred odoslaním query data source-u, vrátane data-source-specific escaping a formatting. Pozri [Grafana](docs/12-observability/grafana.md).

## Graph execution subject — BuildKit

Identita vykonaného build graphu zahŕňajúca frontend translation, reachable nodes, selected target, platform branches, cache hit/miss outcomes, node scheduling, execution results a exporter roots. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Graph-shaping value — Terraform

Hodnota, ktorá určuje samotnú množinu alebo identity graph objektov, napríklad `count` alebo `for_each` keys, a preto musí byť známa pred apply. Pozri [Expressions a dependency graph](docs/07-infrastructure-as-code-and-configuration-management/expressions-and-dependency-graph.md).

## Gratuitous ARP

ARP announcement používaný napríklad na aktualizáciu neighbor caches po presune virtual IP. Pozri [Ethernet, MAC a ARP](docs/02-networking-and-web/ethernet-mac-arp.md).

## Greedy quantifier — regex

Regex quantifier, ktorý najprv spotrebuje najväčší možný rozsah a podľa potreby backtrackuje. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Group-derived permission

Authorization path udelená členstvom subjectu v identity group-e, nie explicitným bindingom na jeho user alebo ServiceAccount meno. Pozri [RBAC](../docs/09-kubernetes/rbac.md).

## Group-identity contract — Alertmanager

Množina labels reprezentujúca spoločný incident boundary a určujúca, ktoré alerts sa spoja do jednej notification group. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

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

Operačný systém bežiaci vo VM nad virtualizovaným hardware a vlastným guest kernelom. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Handler deduplication — Ansible

Správanie, pri ktorom viac notifications rovnakého handlera v príslušnej handler phase vedie typicky k jednému vykonaniu handlera na host. Pozri [Handlers, loops a conditionals](docs/07-infrastructure-as-code-and-configuration-management/handlers-loops-conditionals.md).

## Handler notification — Ansible

Event vytvorený changed taskom cez `notify`, ktorý zaradí pomenovaný handler alebo `listen` topic do pending handler queue pre host. Pozri [Handlers, loops a conditionals](docs/07-infrastructure-as-code-and-configuration-management/handlers-loops-conditionals.md).

## Handler transition — Ansible

Prechod vyvolaný taskom reportujúcim `changed`, pri ktorom notification aktivuje handler, napríklad restart alebo reload služby. Je súčasťou convergence a môže zlyhať alebo sa nevykonať samostatne od pôvodného tasku. Pozri [Ansible architecture](docs/07-infrastructure-as-code-and-configuration-management/ansible-architecture.md) a [Handlers, loops a conditionals](docs/07-infrastructure-as-code-and-configuration-management/handlers-loops-conditionals.md).

## Hard-constraint intersection

Prienik resource, affinity, taint, topology, storage, port, device a ďalších hard placement podmienok; ak je prázdny, Pod je unschedulable. Pozri [Scheduling](../docs/09-kubernetes/scheduling.md).

## Hard link

Ďalší directory entry odkazujúci na ten istý inode. Pozri [Filesystem hierarchy, inodes a links](docs/01-linux-and-systems/filesystem-hierarchy-inodes-links.md).

## Hard mandatory policy — Terraform

Policy as Code pravidlo blokujúce plan alebo apply bez bežného override pathu, používané pre stabilné invariants s vysokým rizikom porušenia. Pozri [Terraform testing a policy](docs/07-infrastructure-as-code-and-configuration-management/terraform-testing-and-policy.md).

## Hard validation — CKA

Explicitný dôkaz, že resource/controller/runtime/application outcome spĺňa zadanie; object existence alebo jeden green status nestačia.

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

## Headless-Service discovery generation

Versionovaný inventory DNS records, Pod UIDs/IPs a publication state-u poskytovaný headless Service pre konkrétnu stateful workload generation. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Headless Service DNS

A/AAAA alebo SRV records headless Service-u vracajúce priamo backend alebo per-Pod identities, pričom client nesie selection a failover zodpovednosť. Pozri [Cluster DNS](docs/09-kubernetes/cluster-dns.md).

## Health check

Aktívny alebo pasívny test určujúci, či backend môže prijímať nový traffic. Pozri [Load balancing](docs/02-networking-and-web/load-balancing.md).

## health-check matcher — ELB

Sada HTTP success codes alebo iné protocol-specific kritérium, podľa ktorého target-group health check vyhodnotí odpoveď ako úspešnú. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## Health generation

Versionovaný stav healthcheck definition, container generation a jej časovej health history, ktorý sa musí viazať na konkrétny runtime subject. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Health-handler observation boundary

Presná perspective a path handlera, napríklad kubelet HTTP proti Pod IP alebo exec command v containeri; nie je totožná s external client pathom. Pozri [Probes](../docs/09-kubernetes/probes.md).

## Health remediation budget

Limitovaný restart alebo recovery contract určujúci confidence, backoff, drain, stateful risk, post-action verification a escalation threshold pri unhealthy stave. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Health-source chain — EC2 Auto Scaling

Poradie EC2 system/instance statusu, ASG health, optional ELB/EBS/VPC Lattice/custom checks, target readiness, application health a business request evidence. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Health start period

Warm-up interval healthchecku, počas ktorého startup failures nemusia prispievať k označeniu containeru za unhealthy podľa health configuration. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Health verification subject

Pod UID, container ID/restart generation, probe configuration, kubelet/Node, attempt sequence, Pod/EndpointSlice conditions a client/business outcome hodnotené ako jeden chain. Pozri [Probes](../docs/09-kubernetes/probes.md).

## Healthcheck subject

Identita probe zahŕňajúca container/image generation, command, runtime user/env/PATH, target namespace/endpoint, timing, redaction a health history. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Helm

Kubernetes package, templating a release-lifecycle tool, ktorý renderuje charts na Kubernetes manifests a uchováva release metadata bez vlastného serverového Tiller componentu. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Helm chart

Versionovaný balík obsahujúci `Chart.yaml`, default values, Kubernetes templates, voliteľné CRDs, dependencies a pomocné files. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Helm chart dependency

Chart deklarovaný alebo vendored ako súčasť parent chartu, ktorého templates a resources sa agregujú do rovnakého Helm release-u. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Helm decommission subject

Kompletný inventár Helm-managed, retained, hook-created, cluster-scoped, storage a external resources, credentials, dát a evidence potrebný na bezpečné ukončenie release-u. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## `helm dependency build`

Command rekonštruujúci `charts/` podľa existujúceho `Chart.lock` bez nového version negotiation, pokiaľ lock existuje. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## `helm dependency update`

Command re-resolvujúci dependency constraints z `Chart.yaml`, aktualizujúci `charts/` a generujúci alebo meniaci `Chart.lock`. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Helm drift triage

Porovnanie posledného release manifestu, navrhovaného renderu a live Kubernetes objectu na identifikáciu authoritative writera a zdroja rozdielu. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Helm empty semantics

Pravidlá, podľa ktorých template functions považujú `nil`, prázdny string, nulu, `false` alebo prázdnu collection za empty, čo môže aktivovať fallback. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Helm evidence lifecycle

Chain `release risk/contract → immutable subject → expected evidence → source/render/API/runtime/business observations → verdict → incident diagnosis → regression closure`, ktorý viaže všetky testy a findings na rovnaký release artifact. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Helm helper subject

Exact helper name, definition origin, caller, scope, argument dictionary, output shape/digest a target Kubernetes field. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Helm hook

Kubernetes resource template označený annotation `helm.sh/hook`, ktorý Helm vykoná v konkrétnom bode install, upgrade, rollback, delete alebo test lifecycle. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Helm hook operation subject

Exact identity hook operácie tvorená release name, source/target revision, lifecycle pointom, rendered hook digestom, Job/Pod UIDs, operation ID a source/target durable state generation. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Helm incident subject

Presný troubleshooting subject obsahujúci cluster/context/namespace, release revision, chart/dependency/values/manifest digests, live object a process identities, configuration/data generations, request alebo transaction ID a timeline. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Helm merge

Template operation spájajúca dictionaries podľa konkrétnej direction a overwrite semantics; pri nested maps môže vyžadovať `deepCopy`, aby sa zabránilo neúmyselnej mutation vstupu. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Helm partial

Reusable template fragment, typicky uložený v underscore-prefixed súbore ako `_helpers.tpl`, ktorý sám nevytvára Kubernetes manifest. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Helm pipeline

Template expression, v ktorom sa výsledok ľavej časti posiela ako posledný argument nasledujúcej funkcie. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Helm recovery hierarchy

Preferované poradie recovery od opravy authoritative source a novej revision cez dokončenie idempotentného hooku, roll-forward, eligible rollback a compensation až po restore pri skutočnej data/control-plane recovery potrebe. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Helm release

Konkrétna pomenovaná inštancia chartu nasadená do Kubernetes namespace-u s effective values, rendered manifestom, statusom a revision history. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Helm release acceptance

Verdikt spájajúci chart, dependency, values, manifest, release revision, live object, workload artifact a business outcome identity po install alebo upgrade operácii. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Helm release revision

Sekvenčné číslo konkrétnej install, upgrade alebo rollback verzie Helm release-u; nie je to Kubernetes Deployment revision ani Git commit. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Helm release state

Metadata, chart/configuration a rendered manifest uložené Helm storage driverom v clustri pre konkrétnu release revision. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Helm release subject

Exact cluster, namespace, release name, Helm tool/apply mode, chart/dependency/values/manifest identities, target revision a business operation, ku ktorým sa viaže release verdict. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Helm release transition subject

Immutable source-to-target identity upgrade-u alebo rollbacku zahŕňajúca release revisions, chart/dependency/values/manifest digests, image digests, hook operation IDs, data/schema/event generations, cluster target a Helm/deployment-engine verziu. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Helm revision evidence

Korelačný záznam spájajúci source commit, chart a dependency artifacts, effective values, rendered manifest, Helm revision, Kubernetes object generations a runtime/business outcome. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Helm roll-forward

Recovery transition, ktorý nasadí novú opravenú a current-state-compatible revision namiesto návratu k historickej revision, najmä keď durable schema, event backlog alebo external side effects už nie sú backward-compatible. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

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

## Helm troubleshooting closure

Incident closure verdict vyžadujúci opravený authoritative source, overený pôvodný aj forbidden outcome, kontrolu adjacent cohorts, stabilný druhý render/retry/reconcile a regression test na najskoršej spoľahlivej boundary. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Helm troubleshooting decision tree

Rozdelenie Helm incidentu na fetch/dependency, values/schema, render, API/admission, hook, release-state, wait alebo následný Kubernetes workload failure. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Helm unknown-operation outcome

Stav, keď Helm command timeoutol alebo zlyhal, ale časť API requests, hooks, rolloutov alebo external side effects mohla prebehnúť; pred retry je potrebný read-back. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Helm upgrade

Operácia vytvárajúca novú release revision z chartu, dependencies, effective values a render contextu a aplikujúca výsledný manifest do clusteru. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Helper call graph — Helm

Directed graph volaní od primitive identity helpers cez reusable fragments po final manifest call sites. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Helper collision — Helm

Stav, keď parent alebo dependency chart definujú rovnaký global template name a effective definition zmení render bez zmeny call site-u. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Helper consumer compatibility — Helm

Dôkaz, že zmena helper provider chartu zachováva input, output-shape, identity, selector a semantic contracts všetkých consumer charts. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Helper contract — Helm

Dokumentovaný input scope, očakávané keys, output shape, whitespace a stability semantics named template helpera. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Helper definition origin — Helm

Chart name, version, digest a source file, z ktorých pochádza effective named-template definition. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Helper-driven resource identity migration

Lifecycle zmena, pri ktorej nový naming alebo selector helper mení Kubernetes resource identity a vyžaduje explicitný migration/rollback plán. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Helper-output digest — Helm

Hash semantic alebo textovej helper output generation používaný na detekciu nečakanej zmeny reusable contractu medzi revisions. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Helper output-shape contract — Helm

Dokumentovaný scalar/map/list/fragment textový output vrátane newline, indentation, quoting a stability semantics. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Helper pseudo-signature — Helm

Explicitný dictionary-based input contract named template-u s required keys, types, root/local scope a output shape. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

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

## Hidden-queue inventory

Versionovaný zoznam všetkých čakacích vrstiev v operation path-e, napríklad client backoff, worker queue, connection pool, lock wait, device queue alebo provider scheduler. Pozri [USE method](docs/12-observability/use-method.md).

## Hidden variable — GitLab

Masked CI/CD variable, ktorej hodnotu po uložení nemožno znovu zobraziť v GitLab UI; job s prístupom ju však stále môže použiť. Pozri [Variables a secrets](docs/06-gitlab/variables-and-secrets.md).

## High availability — HA

Architektonická schopnosť minimalizovať prerušenie služby pri očakávateľných component, host alebo zonal failures pomocou redundancy, health checks a failoveru. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## High-confidence wrong model

Nesprávna odpoveď alebo operational decision vykonaná s vysokou confidence, indikujúca stabilný chybný mentálny model s vyššou remediation prioritou než neistý knowledge gap. Pozri [AWS Certified CloudOps Engineer – Associate](docs/11-cloud-and-aws/cloudops-engineer-associate-soa-c03.md).

## High-risk issue — Well-Architected

Významná odchýlka od Well-Architected best practices s relevantným security, reliability, operations, performance, cost alebo sustainability rizikom. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Histogram — metric

Metric aggregation zaznamenávajúca počet observations v definovaných buckets spolu s count a typicky sum, vhodná na latency distributions a threshold SLIs. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Historical-identity retirement

Časovo viazaný lifecycle, počas ktorého staré series, streams, terms alebo blocks po schema fix-e zaniknú cez staleness, retention, rollover alebo reindex. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Historical-log path — Loki

Query path závislý od TSDB index blocks, flushed chunks, schema periods, object-store access, compaction a retention. Pozri [Loki](docs/12-observability/loki.md).

## Historical-trace path

Trace query path cez published blocks alebo external storage, index/block metadata, object permissions, compaction a retention. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## History rewrite

Operácia vytvárajúca nové commit objects a meniaca branch-visible ancestry, napríklad rebase, amend alebo reset publikovanej branch. Pozri [Merge a rebase](docs/03-git-and-automation/merge-and-rebase.md).

## Hook delete policy — Helm

Annotation `helm.sh/hook-delete-policy` určujúca cleanup hook resource-u pred ďalším spustením, po úspechu alebo po failure. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Hook evidence-retention contract — Helm

Pravidlá určujúce, ktoré hook Job/Pod resources, logs, audit records a durable operation results prežijú success, failure, delete policy a TTL dostatočne dlho na diagnostiku a recovery. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Hook execution attempt — Helm

Jedna konkrétna Job/Pod alebo container execution generation hooku, identifikovaná resource UID, Pod UID, container ID, retry countom a operation ID; nie je totožná s logical external operation. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## `hook-failed` — Helm

Hook delete-policy hodnota požadujúca odstránenie hook resource-u po neúspešnom vykonaní; môže znížiť dostupnosť incident evidence. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Hook fencing — Helm

Lock, compare-and-set, advisory lock, epoch alebo iný control zabraňujúci concurrent hook attempts vykonať konfliktujúce durable side effects nad rovnakým target state-om. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Hook idempotency — Helm

Vlastnosť hook operácie, pri ktorej opakované alebo čiastočne dokončené vykonanie bezpečne konverguje bez duplicitných side effects. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Hook lifecycle point — Helm

Konkrétny release moment, napríklad `pre-install`, `post-upgrade` alebo `pre-delete`, v ktorom Helm spustí označený hook resource. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Hook readiness boundary — Helm

Rozdiel medzi API loadom non-workload hook resource-u, completion Job/Pod hooku, durable external side-effect commitom a Helm release statusom; každý bod poskytuje iný dôkaz. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Hook readiness — Helm

Podmienka, pri ktorej Helm považuje hook za dokončený; pri Job alebo Pod hooku čaká na úspešné completion, pri mnohých iných resource kinds stačí úspešné API načítanie. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Hook recovery verdict — Helm

Rozhodnutie založené na operation ledger-e, target state-e a release evidence, či hook treba považovať za complete no-op, bezpečne resume-nuť, kompenzovať alebo zastaviť pre unknown outcome. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

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

## Host-authority subject — DaemonSet

Effective kombinácia process credentials, capabilities, namespaces, host mounts/sockets, devices, RBAC, network egress a node/cloud identity dostupná node-agent Podu. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## Host baseline generation — Kubernetes

Versionovaný Node OS/kernel/runtime/cgroup/network/storage/security/kubelet baseline používaný pri join-e a replacement-e. Pozri [Cluster installation a lifecycle](../docs/09-kubernetes/cluster-installation-lifecycle.md).

## Host bind address — Docker

Host IP adresa, na ktorej Docker publikuje port, napríklad `127.0.0.1` pre local-only alebo `0.0.0.0` pre všetky IPv4 interfaces. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Host contract generation — Terraform a Ansible

Konkrétna versionovaná publikácia narrow resource-to-host contractu viazaná na Terraform resource subject, readiness observations, schema version a stable host identities, ktorú následne validuje Ansible inventory. Pozri [Terraform vs. Ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md).

## Host-control mount

Mounted path alebo socket, napríklad container-runtime API, ktorý poskytuje authority nad Node-om alebo inými workloads aj pri read-only filesystem mount flags. Pozri [SecurityContext a Pod Security](../docs/09-kubernetes/securitycontext-pod-security.md).

## Host coverage — Ansible

Porovnanie expected, resolved, attempted a runtime-verified host inventories. Zabraňuje tomu, aby zelený run nad neúplnou target množinou predstieral complete rollout. Pozri [Ansible architecture](docs/07-infrastructure-as-code-and-configuration-management/ansible-architecture.md) a [Inventory](docs/07-infrastructure-as-code-and-configuration-management/inventory.md).

## Host key — SSH host key

Kryptografický kľúč, ktorým SSH server preukazuje svoju identitu klientovi. Pozri [SSH](docs/01-linux-and-systems/ssh.md).

## Host network mode

Runtime mode zdieľajúci host network namespace a tým host ports, interfaces a traffic exposure. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Host port — container

Port a bind address v host namespace, ktorý forwarding alebo proxy mapuje na container port. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Host-publication subject

Exact mapping address family, host bind address/port/protocol, endpoint generation, container address/port, forwarding implementation a firewall/upstream policy. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## hosted zone — Route 53

Container authoritative DNS records pre konkrétny public alebo private DNS namespace. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## `hostvars` — Ansible

Magic mapping poskytujúci prístup k host-scoped variables iných inventory hosts; jeho použitie vytvára cross-host coupling a závisí od dostupnosti dát. Pozri [Variables, facts a templates](docs/07-infrastructure-as-code-and-configuration-management/variables-facts-templates.md).

## HPA behavior generation

Versionovaná scale-up/scale-down tolerance, stabilization a rate-policy konfigurácia použitá pri prechode z recommendation na scale action. Pozri [HPA a autoscaling](../docs/09-kubernetes/hpa-autoscaling.md).

## HPA denominator subject

Konkrétny request a metric generation použitý ako denominator pri výpočte resource utilization pre Horizontal Pod Autoscaler. Pozri [Requests, limits a QoS](../docs/09-kubernetes/requests-limits-qos.md).

## HPA metric contract

Presná metrika vrátane units, source, labels, tenant scope, query, aggregation window, freshness, missing-data semantics a očakávaného response na replica change. Pozri [HPA a autoscaling](../docs/09-kubernetes/hpa-autoscaling.md).

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

## Hybrid capability subject

Business capability rozdelená medzi cloud a private/edge prostredie s explicitným ownershipom identity, DNS, data, connectivity, telemetry a connected/disconnected behavioru. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Hybrid cloud

Deployment model integrujúci public-cloud services s on-premises, colocation alebo edge resources cez networking, identity, DNS, data a management contracts. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Hybrid connectivity

Network boundary prepájajúca cloud a externé prostredie cez VPN, dedicated link, public endpoint alebo private service endpoint s explicitným routing, encryption a redundancy modelom. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Hybrid data generation

Identita authoritative data state-u a jeho replication checkpointu, lag-u, ordering-u, conflict modelu, failover a reconciliation stavu naprieč cloud a private domains. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Hybrid DNS authority

Versionovaný contract určujúci authoritative zones, conditional forwarding, resolver endpoints, split-horizon behavior, TTL, overlapping namespaces a disconnected failure behavior. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Hybrid flow subject

Exact network a identity path zahŕňajúci source workload, IP/port, routes, gateway/tunnel/circuit, firewall, destination, return path, TLS a application authorization. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Hypercare

Dočasne zvýšená prevádzková a support pozornosť po významnom release, vrátane posilneného monitoringu, owner dostupnosti a rýchleho rozhodovacieho pathu. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Hypervisor

Virtualization vrstva poskytujúca virtual hardware a isolation pre virtual machines. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Hypothesis evidence matrix — Docker

Mapovanie konkurenčných causal hypotheses na observation points a výsledky, ktoré jednotlivé hypotézy podporia alebo vyvrátia. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

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

## IAM drift

Rozdiel medzi authoritative identity/entitlement desired state-om a effective downstream accounts, groups, roles, sessions alebo resource policies. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## IAM Identity Center

AWS služba pre centralizovaný workforce access, permission sets a federované temporary sessions do viacerých AWS accounts. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## `iam:PassRole`

Citlivá IAM action umožňujúca principalu odovzdať role AWS službe; musí byť obmedzená na presné roles a destination services. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## IAM principal

Autentifikovaná alebo identifikovateľná AWS request identity, napríklad root user, IAM user, role session, federated principal alebo service principal. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## IAM/RBAC acceptance verdict

Dôkaz, že authoritative state, reconciliation, session claims, policy bindings a effective access sú zhodné, required access funguje, forbidden paths zlyhávajú a second reconciliation neobnoví defect. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## IAM role

AWS identity s trust policy a permissions policy modelom, ktorú principal preberá a používa cez temporary session credentials. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## IAM role trust policy

Resource-based policy role určujúca, ktoré principals a za akých conditions môžu role assume-nuť. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## IAM session policy

Policy odovzdaná pri vytváraní temporary session, ktorá môže zúžiť, ale nie rozšíriť permissions nad role a ostatné guardrails. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## IAM subject

Exact authoritative identity record, entitlement generation, group/role graph, federation/session, platform policy, resource scope a audit generation analyzovaného IAM lifecycle-u. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

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

## Idempotency key — automation

Stabilná identity jednej business mutation používaná pri retries tak, aby viac network attempts nevytvorilo viac remote side effects. Musí byť kontrolovateľná alebo dohľadateľná cez remote API a audit. Pozri [Ansible idempotencia](docs/07-infrastructure-as-code-and-configuration-management/ansible-idempotency.md).

## Idempotency test — Ansible

Test vykonávajúci po prvom converge ďalší run s rovnakými inputs a overujúci, že nevzniknú neplánované changes ani side effects. Pozri [Ansible idempotencia](docs/07-infrastructure-as-code-and-configuration-management/ansible-idempotency.md).

## Idempotent batch execution

Batch návrh, pri ktorom opakované alebo duplicitné vykonanie toho istého logical work itemu nevytvorí nekonzistentné dodatočné side effects. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Idempotent reconcile

Controller behavior, pri ktorom opakované spracovanie rovnakého desired a actual state-u nevytvára neplánované duplicity alebo ďalšie side effects. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Identity

Reprezentácia osoby, workloadu, zariadenia alebo organizácie používaná naprieč identity a access lifecycle-om. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Identity-aware fan-in

Agregácia, ktorá pred verdictom overí expected inventory aj zhodu subjectu, variantu, shardu, child runu a attempt identity každého výsledku. Zelené prijaté reporty nestačia, ak výsledný set nie je úplný a porovnateľný. Pozri [Reusable a parallel pipelines](docs/05-ci-cd-and-release/reusable-and-parallel-pipelines.md).

## Identity-aware proxy

Proxy acting as PEP, ktorá autentizuje subject, vyhodnotí policy a sprostredkuje access ku konkrétnej application bez implicitnej network trust. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Identity-based policy — AWS

IAM policy pripojená k userovi, group alebo role, ktorá povoľuje alebo denyuje actions nad resources podľa request contextu. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## Identity-churn rate

Rýchlosť tvorby a zániku telemetry identities, ktorá môže destabilizovať WAL, index, compaction a recovery aj pri miernom active count-e. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Identity eligibility generation

Versionovaný stav určujúci, či identity stále spĺňa organizational a risk podmienky na použitie accountu, service-u alebo privileged entitlementu. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Identity operation outcome

Auditovaný výsledok konkrétnej API alebo external operácie vykonanej workload identity, nie iba dôkaz, že credential existoval. Pozri [ServiceAccount](../docs/09-kubernetes/serviceaccount.md).

## Identity proofing

Proces zhromažďovania a overovania evidence, ktorým sa digitálna identita spoľahlivo priraďuje reálnej osobe alebo entite. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Identity Provider — SAML

SAML entita autentizujúca principal-a a vydávajúca signed assertions. Pozri [SAML](docs/13-security-and-identity/saml.md).

## Identity reconciliation

Proces porovnávajúci authoritative identity/entitlement desired state s downstream accounts, groups, roles, sessions a local access paths a pridávajúci aj odstraňujúci delta. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Identity, Service, routing a DNS acceptance verdict

Záverečný verdict príslušnej kapitoly, ktorý overuje current object/generation subjects, effective runtime/dataplane state, pôvodný business outcome a relevantné forbidden outcomes. Pozri [ServiceAccount](../docs/09-kubernetes/serviceaccount.md), [Service a EndpointSlice](../docs/09-kubernetes/service-endpointslice.md), [Ingress a Gateway API](../docs/09-kubernetes/ingress-gateway-api.md) a [Cluster DNS](../docs/09-kubernetes/cluster-dns.md).

## Identity-to-workload audit chain

Korelácia human alebo upstream principalu, jeho session a authorization s vytvorenou workload identity a downstream actions tejto workload identity. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## `ignore_changes` — Terraform

Lifecycle rule, ktorá pri update plánovaní ignoruje zmeny vybraných atribútov. Musí mať explicitný external owner a monitoring, pretože potláča Terraform remediation, nie existenciu driftu. Pozri [Lifecycle, import a moved blocks](docs/07-infrastructure-as-code-and-configuration-management/lifecycle-import-moved-blocks.md).

## Image-config contract test

Assertion nad final image configom a runtime overrides overujúca entrypoint, command, user, environment, healthcheck, signal, ports a writable paths pre exact digest. Pozri [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md).

## Image-config transition — Dockerfile

Instruction meniaca runtime metadata image-u, napríklad `ENV`, `USER`, `ENTRYPOINT`, `CMD`, `HEALTHCHECK` alebo `STOPSIGNAL`. Pozri [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md).

## Image configuration — OCI

OCI JSON artifact obsahujúci platform, runtime defaults, user, entrypoint/command, environment, rootfs diff IDs a history metadata. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Image content subject

Identita image graphu zahŕňajúca manifest, config a ordered layer descriptors/digests, oddelená od snapshotu a runtime state-u. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## Image index — OCI

Manifest list odkazujúci na viac platform-specific manifests. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Image layer

Immutable filesystem changeset v ordered image graph-e. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## Image manifest — OCI

OCI artifact odkazujúci na jednu image configuration a ordered layer blobs. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

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

## Immutable build input inventory

Úplná identita source/contextu, Dockerfile/frontendu, base/external image digestov, dependencies, args, secret references, platformy, buildera, cache a targetu. Pozri [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md).

## Immutable chart test subject

Exact testovaný Helm artifact a environment contract vrátane chart/dependency/values/manifest digests, Helm/deployment-engine verzie, target clusteru a očakávaných runtime/data generations. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Immutable ConfigMap alebo Secret

ConfigMap alebo Secret s `immutable: true`, ktorý nemožno in-place meniť a vyžaduje nový versioned object a consumer rollout. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Immutable infrastructure

Model, v ktorom sa existujúce inštancie zásadne neupravujú, ale nahrádzajú novými. Pozri [Immutable vs. Mutable Infrastructure](docs/00-foundations/immutable-vs-mutable-infrastructure.md).

## Immutable launch subject — EC2

Pinned launch template version, AMI/provenance, user-data digest, network/storage/IAM configuration a purchase/placement constraints, ktoré reprodukovateľne vytvárajú jednu instance generation. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Immutable node replacement

Upgrade alebo oprava Node-u vytvorením novej versionovanej instance, validáciou, controlled drainom starého Node-u a následným odstránením starej infraštruktúry. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Immutable tag

Registry alebo repository tag, ktorého mapping na artifact content sa po publikovaní nesmie zmeniť. Pozri [Artifact versioning](docs/05-ci-cd-and-release/artifact-versioning.md).

## Impact/scope classification — CloudOps

Počiatočné určenie severity, trendu a affected boundary incidentu pred root-cause diagnosis a remediation priority. Pozri [CloudOps troubleshooting drills](docs/11-cloud-and-aws/cloudops-troubleshooting-drills.md).

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

## Improvement validation — Well-Architected

Subject-bound test a evidence, ktoré preukazujú, že implemented improvement odstránil failure mechanism bez vytvorenia forbidden outcomes. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## in-toto

Framework a metadata model pre zaznamenanie a overenie supply-chain steps, materials, products a autorizovaných functionaries. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## in-toto Statement

Supply-chain attestation structure obsahujúca subject digest, predicate type a predicate. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Incident closure verdict — Docker

Verdict potvrdzujúci, že authoritative recovery je nasadená, pôvodný business outcome funguje, forbidden outcomes sú absent, adjacent scope bol overený a skorší preventive control má ownera. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Incident usage — FinOps

Metered compute, request, transfer, storage alebo telemetry volume vytvorený failure amplification, attackom alebo remediation a nevhodný ako normal commitment alebo forecast baseline. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## `include` — Helm

Helm function renderujúca named template do stringu, ktorý možno ďalej spracovať v pipeline napríklad cez `nindent` alebo `sha256sum`. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## `include_role`

Dynamické načítanie Ansible role počas executionu podľa runtime contextu. Pozri [Roles a collections](docs/07-infrastructure-as-code-and-configuration-management/roles-and-collections.md).

## Incomplete verdict

Výsledok signalizujúci, že autoritatívne rozhodnutie nemožno urobiť, pretože chýba required job, shard, report, artifact alebo tool execution status. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

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

## Indirect IAM capability

Authority vznikajúca kombináciou zdanlivo úzkych permissions, napríklad `iam:PassRole` s vytvorením workloadu alebo edit policy/trust s následným assume-role pathom. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## Indirect privilege path

Povolená operation, ktorá umožní získať inú alebo vyššiu authority cez workload creation, credential read, role binding, impersonation, delegated role, trusted artifact alebo policy mutation. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## Indirect workload capability

Autorita získaná cez permission vytvoriť alebo meniť Pod/Deployment/Job, napríklad použitie silnejšej ServiceAccount, mounted Secretu, internal networku alebo runtime fields. Pozri [RBAC](../docs/09-kubernetes/rbac.md).

## Informer — Kubernetes

Client-side mechanism kombinujúci list/watch, local cache a event handlers na efektívne sledovanie Kubernetes resources pre controllers. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Informer relist boundary — recovery

Bod, v ktorom controller/client po etcd restore zahodí stale watch assumptions a načíta fresh authoritative object set, typicky po compaction/revision semantics. Pozri [etcd backup a restore](../docs/09-kubernetes/etcd-backup-restore.md).

## Infrastructure as Code — IaC

Správa infraštruktúry pomocou versionovanej deklarácie, automatizovaného plan/apply alebo reconciliation procesu, review, policy a auditovateľného recovery lifecycle. Pozri [Infrastructure as Code principles](docs/07-infrastructure-as-code-and-configuration-management/infrastructure-as-code-principles.md).

## Infrastructure policy

Policy vyhodnocujúca infrastructure source, plan, configuration alebo runtime state podľa security, compliance, cost a operational guardrails. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Ingest acknowledgement — tracing

Potvrdenie, že tracing backend alebo durable queue prijala trace records; samo nepreukazuje complete trace ani historical block publication. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Ingest pipeline — search

Server-side pipeline, ktorá pred indexingom parsuje, normalizuje, enrichuje, rediguje alebo routuje documents. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Ingester — Loki

Loki write-path component, ktorý prijíma recent log entries, drží active streams a vytvára chunks pred flushom do storage. Pozri [Loki](docs/12-observability/loki.md).

## Ingestion/query boundary — telemetry

Rozlíšenie backendom prijatého recordu od recordu správne indexovaného, retained a nájdeného v presnom tenantovi, time range a query. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

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

## Inhibition-scope contract

Source, target a `equal` label policy určujúca, v ktorých environment, Region, cluster alebo service boundaries môže firing parent alert mutovať child notifications. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Init container

Container, ktorý musí úspešne dokončiť prípravnú úlohu pred spustením bežných application containers v Pode. Pozri [Pod](docs/09-kubernetes/pod.md).

## Init side-effect boundary

Hranica určujúca, či init container vykonáva iba bezpečnú local prípravu alebo durable/shared external side effect vyžadujúci singleton, idempotency a recovery protocol. Pozri [Pod](docs/09-kubernetes/pod.md).

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

## Instance-refresh transition subject

Source a target fleet cohorts, exact launch generations, healthy-capacity preferences, warmup, checkpoints, skip-matching, rollback eligibility a business acceptance jedného refreshu. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## instance store — EC2

Host-local ephemeral block storage, ktorého dáta sa môžu stratiť pri stop, termination alebo host failure. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## instance warmup — Auto Scaling

Interval reprezentujúci čas, kým newly launched instance dosiahne plnú application a metric readiness pre scaling decisions. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Instant vector — PromQL

Množina time series s jednou sample hodnotou pre každý label set v konkrétnom evaluation čase. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Instrumentation

Kód, agent, library alebo platform capability, ktorá generuje telemetry signals o správaní systému. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Instrumentation acceptance verdict

Dôkaz, že target instrumentation generation je skutočne načítaná, vytvára správnu identity/schema, prejde backend read-backom, neporušuje overhead/privacy budget a jej consumers fungujú. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Instrumentation generation

Versionovaný súbor code-based, zero-code a platform observation mechanisms spolu s resource, scope, propagation, sampling a export semantics. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Instrumentation library

Knižnica, ktorá vytvára telemetry pre application, framework alebo dependency a nesie vlastný instrumentation scope. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Instrumentation scope

Logical software unit a jej version, s ktorou OpenTelemetry spája vytvorené spans, metrics a log records. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Instrumentation-scope generation

OpenTelemetry scope name, version a schema URL identifikujúce library alebo component, ktorý telemetry vytvoril. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Instrumentation subject

Exact combination application release-u, instrumentation generation, semantic-convention selection, Collector configu, backend route a observed business journey. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Integration decision

Autoritatívne rozhodnutie, či sa konkrétny candidate integration state môže bezpečne pridať k aktuálnej mainline na základe complete a fresh evidence. Pozri [Continuous Integration](docs/05-ci-cd-and-release/continuous-integration.md).

## Integration test

Test reálnej spolupráce komponentov alebo systému s technickou dependency, napríklad databázou, brokerom, filesystemom alebo cloud API. Pozri [Unit, integration a component tests](docs/04-testing-and-quality/unit-integration-component-tests.md).

## Integrity — security

Ochrana accuracy, completeness a správnosti dát, konfigurácie a processingu pred neautorizovanou alebo nesprávnou zmenou. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Interaction-based testing

Testovanie, ktoré overuje komunikáciu a side effects medzi objektmi alebo komponentmi, napríklad volanie gateway s konkrétnymi argumentmi. Pozri [Mocks, stubs a fakes](docs/04-testing-and-quality/mocks-stubs-fakes.md).

## Interface endpoint — AWS

PrivateLink-based VPC endpoint vytvárajúci ENIs s private IPs v zvolených subnetoch a voliteľným private DNS modelom. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## Internal direct path

Container-to-container flow cez spoločnú Docker network a service DNS priamo na container port bez host publication boundary. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Internal traffic policy — Service

Service policy ovplyvňujúca výber cluster-wide alebo node-local backendov pre traffic prichádzajúci z clusteru. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## Internet-egress subject — AWS

Exact outbound flow identity obsahujúca source ENI/subnet/AZ, selected route, IGW/NAT identity, original a translated tuple, destination/DNS/TLS identity, connection generation a business operation. Pozri [Internet Gateway a NAT Gateway](docs/11-cloud-and-aws/internet-gateway-nat-gateway.md).

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

## Inventory resolution subject — Ansible

Rekonštruovateľná identita inventory výpočtu zahŕňajúca source konfigurácie, plugin versions, source account/region a query, cache generation/age, static revision, vars sources, pattern/limit a resolution timestamp. Pozri [Inventory](docs/07-infrastructure-as-code-and-configuration-management/inventory.md).

## Inventory source — Ansible

File, directory, plugin configuration, script alebo external source, z ktorého Ansible vytvára časť výsledného inventory. Pozri [Inventory](docs/07-infrastructure-as-code-and-configuration-management/inventory.md).

## Invocation-admission verdict — Lambda

Rozhodnutie Lambda control plane-u, či exact invocation môže byť prijatá vzhľadom na source state, permissions, regional/reserved/event-source concurrency, quotas a target version/configuration. Pozri [AWS Lambda](docs/11-cloud-and-aws/lambda.md).

## IP packet

Network-layer jednotka obsahujúca source a destination IP adresu a payload vyššej vrstvy. Pozri [OSI a TCP/IP model](docs/02-networking-and-web/osi-and-tcp-ip-model.md).

## IPAM

IP Address Management mechanizmus prideľujúci a uvoľňujúci jedinečné Pod IP adresy a súvisiace subnet/route metadata. Pozri [CNI a NetworkPolicy](docs/09-kubernetes/cni-networkpolicy.md).

## IPAM allocation subject

Jedinečná väzba medzi IP pool/PodCIDR generation, runtime sandboxom, Pod UID, pridelenou adresou a lease lifecycle-om. Pozri [CNI a NetworkPolicy](../docs/09-kubernetes/cni-networkpolicy.md).

## `ipBlock` — NetworkPolicy

CIDR-based NetworkPolicy peer určený najmä pre traffic k alebo z IP rozsahov mimo selector-based Pod identity modelu; výsledok môže ovplyvniť NAT a enforcement point. Pozri [CNI a NetworkPolicy](docs/09-kubernetes/cni-networkpolicy.md).

## IPv4 private ranges

Adresy `10.0.0.0/8`, `172.16.0.0/12` a `192.168.0.0/16`, ktoré nie sú globálne routované vo verejnom Internete. Pozri [IPv4, IPv6 a subnetting](docs/02-networking-and-web/ipv4-ipv6-subnetting.md).

## IPv6 link-local address

IPv6 adresa z `fe80::/10` platná v lokálnom linkovom scope. Pozri [IPv4, IPv6 a subnetting](docs/02-networking-and-web/ipv4-ipv6-subnetting.md).

## Irreversible migration boundary — Kubernetes upgrade

Bod API storage, CRD conversion, schema, data alebo external-state transitionu, po ktorom stará generácia už nemusí byť bezpečná rollback target. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Isolated-copy acceptance

Dôkaz, že required cross-account/Region alebo locked-vault copy job dokončil intended destination recovery point s correct key, retention a restore access. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Isolated subnet — AWS

Subnet bez všeobecného inbound internet pathu aj bez general outbound internet pathu; môže používať iba explicitné private connectivity targets. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## Isolation boundary

Technická a bezpečnostná hranica oddeľujúca workload od hosta alebo iných workloads. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Item inventory — Ansible

Vopred validovaná a identifikovateľná množina business items, nad ktorými loop vytvára per-item operations. Obsahuje identity keys, required fields, ordering alebo completeness invariants a recovery semantics pri partial failure. Pozri [Handlers, loops a conditionals](docs/07-infrastructure-as-code-and-configuration-management/handlers-loops-conditionals.md).

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

## Job attempt

Jedno konkrétne vykonanie jobu vrátane runnera, časov, logs a verdictu; retry vytvára nový attempt a nesmie prepísať evidence predchádzajúceho pokusu. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

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

## Just-enough capability

Mediated a bounded operation poskytujúca presný business alebo administrative task bez full shellu, broad role alebo ambient control-plane authority. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## Just-in-time access

Dočasná aktivácia privilege na obmedzený čas po splnení podmienok ako MFA, approval alebo justification. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## JWKS

JSON Web Key Set publikujúci public cryptographic keys používané napríklad na validáciu OIDC ID Token signatures. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md).

## Kafka-buffered tracing

Tracing architecture, v ktorej durable Kafka-compatible queue oddeľuje trace ingestion od storage consumers. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Kafka trace replay window

Časový interval určený Kafka retention a consumer progressom, počas ktorého Tempo block-builder/live-store alebo Jaeger ingester dokáže znovu spracovať trace records. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## KDC

Kerberos Key Distribution Center obsahujúce Authentication Service, Ticket-Granting Service a principal/key database. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Kerberos

Ticket-based network authentication protocol používajúci KDC, TGT a service tickets na vzájomnú authentication clientov a services. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Kernel enforcement generation — Kubernetes

Exact seccomp, AppArmor, SELinux a related Node/runtime policy state použitý pre konkrétny Pod/container operation. Pozri [SecurityContext a Pod Security](../docs/09-kubernetes/securitycontext-pod-security.md).

## Kernel space

Privilegovaná časť systému, v ktorej kernel spravuje procesy, memory, devices, filesystems a networking. Pozri [Kernel a user space](docs/01-linux-and-systems/kernel-and-user-space.md).

## Key-based signing

Signing model používajúci dlhodobejší private key a distribuovaný public key alebo certificate ako trust anchor. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Key dependency manifest — KMS

Versionovaný inventory encrypted resources, ciphertext/data-key histories, grants, aliases, cross-account consumers, backups a recovery paths potrebný pred disable alebo deletion KMS key-u. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Key Encryption Key — KEK

Cryptographic key používaný na wrap alebo encryption iných keys, najmä Data Encryption Keys v envelope-encryption architektúre. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## Key Management Service — KMS

Centralizovaná služba poskytujúca kontrolovaný key lifecycle, authorization, audit a cryptographic operations; nechráni automaticky application plaintext ani nesprávne decrypt permissions. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## Key-material generation — KMS

Konkrétna cryptographic-material generation používaná KMS key-om po creation alebo rotation, pričom logical key ID môže zostať nezmenené. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Key policy — KMS

Resource policy priamo pripojená ku KMS key, ktorá je fundamentálnou súčasťou autorizácie management a cryptographic operations. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Key retirement verdict

Rozhodnutie, že nový encrypt path je active, všetky retained ciphertext/backups majú tested decrypt path, grants/consumers sú inventoried a old KMS key možno bezpečne disable-nuť alebo delete-nuť. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

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

## KMS authorization boundary

Kombinácia caller permissions, KMS key policy/grants, encryption context, Region/account a request conditions potrebná na cryptographic operation. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## KMS grant

Programaticky vytvorený permission objekt umožňujúci grantee principalovi konkrétne cryptographic operations na KMS key, často používaný AWS service integrations. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## KMS key

Logical AWS KMS resource reprezentujúci cryptographic key, jeho metadata, policy, state, aliases a key-material lifecycle. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## KMS logical key identity

Dlhodobá KMS key identity viazaná na key ID/ARN, policy, state, usage, origin, aliases a grants; môže prežiť viac key-material rotations. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

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

## Kubelet reconciliation subject

Identita jedného kubelet Pod-sync rozhodnutia zahŕňajúca Pod UID/spec, Node UID, local admission, runtime/volume/network dependencies, observed local state a status write outcome. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## Kubernetes API

Versionované HTTP rozhranie, cez ktoré users, clients, controllers a node components čítajú a menia Kubernetes resources a cluster state. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Kubernetes audit log

Bezpečnostný záznam API requests podľa audit policy, odlišný od diagnostických Events a application business events. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Kubernetes builder driver — Buildx

Buildx driver prevádzkujúci BuildKit workers v Kubernetes, s cluster schedulingom, resource controls a možnosťou native multi-architecture nodes. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Kubernetes cluster

Logická platformová jednotka pozostávajúca z control plane-u, worker nodes, cluster networku, storage a supporting integrations. Pozri [Kubernetes architecture](docs/09-kubernetes/kubernetes-architecture.md).

## Kubernetes control-chain subject

Spoločná identita clusteru, caller requestu, admitted top-level objectu, dependent/controller generations, scheduler assignment, node execution a Service/business verification. Pozri [Kubernetes architecture](docs/09-kubernetes/kubernetes-architecture.md).

## Kubernetes controller

Control loop sledujúci resources a vykonávajúci alebo požadujúci zmeny, ktoré približujú observed state k desired state-u. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Kubernetes DNS watch generation

Service, EndpointSlice a namespace state, ktorý CoreDNS Kubernetes plugin reálne pozoruje vo svojom informer/cache lifecycle-e. Pozri [Cluster DNS](../docs/09-kubernetes/cluster-dns.md).

## Kubernetes Event

Krátkodobý API objekt s diagnostickým pozorovaním componentu o konkrétnom resource alebo cluster stave. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Kubernetes executor — GitLab Runner

Executor, ktorý pre CI/CD job vytvorí Kubernetes pod s build, helper a podľa konfigurácie service containers. Pozri [Runners a executors](docs/06-gitlab/runners-and-executors.md).

## Kubernetes incident subject

Exact cluster, release, object UID/generation, Pod/container, Node, data, flow, request a time identity, ku ktorej sa viažu hypotheses a recovery verdict. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Kubernetes incident timeline

Chronologický záznam faktov, hypotéz, testov, zmien a recovery milestones s UTC časom počas incidentu. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Kubernetes object

Persistentná inštancia Kubernetes resource type-u reprezentujúca desired alebo observed cluster state cez API. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Kubernetes object subject

Identita konkrétnej object inštancie zahŕňajúca cluster, GVK/GVR, namespace/name, UID, resourceVersion, generation, field ownership, status generation, dependents a deletion state. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Kubernetes resource

API-exposed resource type s group/version, REST endpointom, schema, scope a podporovanými verbs. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Kubernetes SecurityContext

Pod alebo container configuration definujúca runtime user/group identity, capabilities, privilege escalation, filesystem, seccomp a ďalšie security controls. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## Kubernetes storage lifecycle subject

Súvislý identity chain od logical data generation cez PVC, PV, StorageClass a backing volume po attachment, mount, backup a reclaim verdict. Pozri [Volumes, PV, PVC a StorageClass](../docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Kubernetes upgrade subject

Complete current-to-target transition identity zahŕňajúca cluster, component, etcd, Node, runtime, add-on, API/CRD, workload, data a recovery generations. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

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

## Lab abort condition

Vopred definovaný impact, spend, exposure alebo control-loss threshold, pri ktorom sa experiment zastaví a prejde na containment/recovery. Pozri [CloudOps hands-on labs](docs/11-cloud-and-aws/cloudops-hands-on-labs.md).

## Lab generation — CloudOps

Jedna versionovaná realizácia lab manifestu, resources, configuration, fault a evidence, oddelená od predchádzajúcich alebo paralelných pokusov. Pozri [CloudOps hands-on labs](docs/11-cloud-and-aws/cloudops-hands-on-labs.md).

## Lab replay verdict

Rozhodnutie po evidence review, či lab generation prešla, potrebuje nový variant, musí zopakovať rovnaký failure alebo odhalila prerequisite gap. Pozri [CloudOps hands-on labs](docs/11-cloud-and-aws/cloudops-hands-on-labs.md).

## Label-contract generation — Loki

Versionovaná množina bounded stream labels, structured metadata rules a forbidden dynamic dimensions používaná pri ingestovaní logs. Pozri [Loki](docs/12-observability/loki.md).

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

## Last compatible state

Najnovší presne identifikovaný runtime subject, ktorý je technicky, dátovo, eventovo, klientsky a bezpečnostne kompatibilný s aktuálnym distributed state-om a možno ho použiť ako recovery target. Nemusí byť totožný s bezprostredne predchádzajúcim release-om. Pozri [Rollback a roll-forward](docs/05-ci-cd-and-release/rollback-and-roll-forward.md).

## Last known good

Presne identifikovaný artifact, configuration a compatibility stav s overenou produkčnou evidence, ktorý možno použiť ako recovery target. Pozri [Rollback a roll-forward](docs/05-ci-cd-and-release/rollback-and-roll-forward.md).

## Latency

Čas potrebný na dokončenie operácie alebo requestu. Pozri [Performance a troubleshooting](docs/01-linux-and-systems/performance-and-troubleshooting.md).

## Latency-boundary contract

Explicitný start a end measurement point pre latency vrátane queue, dependency alebo final workflow completion semantics a oddelenia successful, failed a degraded populations. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## latency routing — Route 53

DNS routing policy vyberajúca resource v AWS lokalite, ktorá má podľa Route 53 latency measurements najnižšiu očakávanú latency pre query source. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Latest successful artifact — GitLab

Artifact z najnovšieho úspešného pipeline na danom ref-e, ktorý môže GitLab podľa nastavenia uchovávať nezávisle od bežnej expiration policy. Pozri [Artifacts a cache](docs/06-gitlab/artifacts-and-cache.md).

## launch template — EC2

Versionovaný EC2 launch contract definujúci AMI, instance type, network, storage, IAM, metadata, user data a ďalšie launch settings. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Launch-template version closure

Dôkaz, že ASG, refresh a každá target instance používajú explicitne schválenú launch template version; `$Latest` alebo uncontrolled `$Default` closure nespĺňajú. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Layer-aware secret incident

Incident, pri ktorom secret môže byť v layeri, image metadata, context/cache, platform variante, writable layeri alebo mounted storage a vyžaduje clean rebuild aj revocation. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

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

## Level-based control protocol

Controller protocol, ktorý pri každom reconcile rekonštruuje latest subject a porovná desired, observed a external effective state namiesto závislosti od jednorazovej event sekvencie. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Level-based reconciliation

Controller model, ktorý pri každom reconcile vyhodnocuje aktuálny desired a observed state namiesto závislosti na jedinom nevynechanom evente. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Library chart — Helm

Chart typu `library`, ktorý poskytuje reusable template primitives a helpers pre iné charts bez bežného application resource lifecycle. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Library-chart provider contract

Versionovaný reusable helper API poskytovaný library chartom vrátane names, scopes, output shapes, compatibility a consumer testov. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Library-chart source injection

Schopnosť library dependency meniť parent rendered resources prostredníctvom helpers, hoci sama nevytvára samostatný workload resource set. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## lifecycle hook — Auto Scaling

Auto Scaling extension, ktorá pozastaví launch alebo termination transition, aby automation vykonala bootstrap, registration, drain alebo evidence-preservation action. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Lifecycle-hook operation subject — ASG

Logical launch alebo termination side effect viazaný na instance ID, transition, hook name, operation/idempotency key, heartbeat, timeout, durable result a retry attempts. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Lifecycle meta-argument — Terraform

Built-in Terraform block meniaci plánovanie resource lifecycle cez pravidlá ako `create_before_destroy`, `prevent_destroy`, `ignore_changes`, `replace_triggered_by`, preconditions a postconditions. Pozri [Lifecycle, import a moved blocks](docs/07-infrastructure-as-code-and-configuration-management/lifecycle-import-moved-blocks.md).

## LimitRange

Namespaced Kubernetes policy nastavujúca alebo validujúca per-container, per-Pod alebo per-PVC resource defaults, minimá, maximá a ratios. Pozri [ResourceQuota a LimitRange](docs/09-kubernetes/resourcequota-limitrange.md).

## LimitRange generation

UID/generation a resolved ruleset, ktorý pri admission-e doplnil alebo validoval requests, limits alebo PVC bounds pre konkrétny object request. Pozri [ResourceQuota a LimitRange](../docs/09-kubernetes/resourcequota-limitrange.md).

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

## Live-lookup render subject — Helm

Cluster endpoint, caller RBAC, queried object UID/resourceVersion a API response, ktoré vstupujú do manifestu pri použití `lookup`. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Liveness

Schopnosť procesu pokračovať v užitočnej práci bez potreby restartu; nie je automaticky totožná s readiness alebo external availability. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Liveness probe

Kubelet health test rozhodujúci, či je container v stave, z ktorého mu má pomôcť restart; opakované failure vedie k restartu containeru. Pozri [Probes](docs/09-kubernetes/probes.md).

## Liveness recovery contract

Tvrdenie, že konkrétny local failure je detegovaný liveness probe a restart containeru má realisticky odstrániť jeho príčinu. Pozri [Probes](../docs/09-kubernetes/probes.md).

## LLB — BuildKit

Low-Level Build graph representation používaná BuildKitom na opis operations, dependencies, mounts, cache keys a execution flow prekladom z frontendu. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Load average

Priemerný počet runnable tasks a určitých tasks v uninterruptible sleep. Pozri [Memory a CPU fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## Load-balancer dual-connection subject

Oddelené identity pre `client → load balancer` a `load balancer → target`, z ktorých každá má vlastné route, SG, NACL, port, health a return-path evidence. Pozri [Security Groups a Network ACLs](docs/11-cloud-and-aws/security-groups-network-acls.md).

## Load-balancer fail-open

Availability behavior, pri ktorom ELB môže pri all-unhealthy alebo inom service-defined nedostatku healthy targets routovať aj na unhealthy/all registered targets namiesto úplného blackhole. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## Load-balancing acceptance verdict

Closure dôkaz, že exact request matchuje approved listener/rule generation, používa eligible zonálny target cohort, dokončí business outcome a forbidden host/path/direct-target/fail-open/drain outcomes zostanú kontrolované. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## `--load` — Buildx

Build exporter skratka importujúca vhodný build output do local Docker image store-u, typicky pre single-platform local workflow. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Load shedding

Riadené odmietanie alebo obmedzenie časti práce pri preťažení, aby systém chránil kritické workflow a zabránil úplnému kolapsu. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Load test

Performance test overujúci očakávaný workload a splnenie latency, throughput, error-rate a resource kritérií. Pozri [Performance, load a stress tests](docs/04-testing-and-quality/performance-load-stress-tests.md).

## LoadBalancer Service

Kubernetes Service type, ktorý prostredníctvom cloud alebo platform controlleru žiada external alebo internal load balancer a publikuje jeho address v status-e. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## Loaded certificate subject

Certificate identity reálne načítaná konkrétnou edge instance, typicky identifikovaná SAN, serialom, expiry a config generation. Pozri [Ingress a Gateway API](../docs/09-kubernetes/ingress-gateway-api.md).

## Loaded dashboard revision

Dashboard representation skutočne uložená a používaná Grafanou po provisioningu alebo UI mutation, odlíšená od source artifactu. Pozri [Grafana](docs/12-observability/grafana.md).

## Loaded instrumentation state

Instrumentation, agent, SDK alebo Collector configuration skutočne používaná bežiacim processom, ktorá sa môže líšiť od deklarovaného environmentu alebo desired configu. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Loaded resource limit

Runtime limit, ktorý component skutočne používa, napríklad per-process connection-pool maximum; môže sa líšiť od desired alebo deklarovanej konfigurácie. Pozri [USE method](docs/12-observability/use-method.md).

## Loaded-state telemetry

Telemetry field alebo inventory preukazujúce effective configuration, secret, feature alebo release generation načítanú runtime cohortou namiesto iba desired-state deklarácie. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Local admission boundary — kubelet

Node-side rozhodnutie, či pridelený Pod môže byť realizovaný vzhľadom na aktuálnu Node capacity, capabilities, RuntimeClass, devices, volumes, pressure a local configuration. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## Local-endpoint coverage

Intersection Nodes prijímajúcich traffic s ready local endpointmi potrebná pre bezpečné `Local` traffic policies. Pozri [Service a EndpointSlice](../docs/09-kubernetes/service-endpointslice.md).

## Local PersistentVolume

PV reprezentujúci storage fyzicky viazaný na konkrétny Node alebo topology domain, s vysokým výkonom, ale bez automatickej multi-node dostupnosti. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Local TSDB generation — Prometheus

Queryovateľný local state konkrétnej Prometheus replica vytvorený z WAL, head blocku, immutable blocks, compaction a retention lifecycle-u. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Local TSDB — Prometheus

Lokálny time-series storage Prometheus servera založený na head blocku, WAL, immutable blocks, compaction a retention. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Local value — Terraform

Pomenovaná interná expression modulu dostupná cez `local.<name>`, ktorú caller nemôže priamo nastaviť. Pozri [Variables, locals a outputs](docs/07-infrastructure-as-code-and-configuration-management/variables-locals-outputs.md).

## Local-versus-remote metrics state

Explicitné porovnanie local Prometheus samples/rule state-u s remote-write queue a downstream backend read-back stavom. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Local Zone — AWS

AWS infrastructure extension približujúca vybrané služby k určitej metropolitnej oblasti pre latency-sensitive workloady a závislá od parent Regionu podľa service modelu. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## Lock-required release gate — Helm

CI policy odmietajúca release build, ak dependency declaration nemá synchronizovaný reviewed lock alebo artifacts nezodpovedajú lock identity. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Locked packaged graph — Helm

Reprodukovateľný packaged parent chart a všetky dependency artifacts vytvorené podľa reviewed `Chart.lock` a overených digestov. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Lockfile — dependency resolution

Versionovaný záznam konkrétneho resolved dependency graphu, často vrátane integrity hashes, ktorý stabilizuje opakovanie dependency resolution. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Log

Časovo označený record udalosti, state-u alebo message, ideálne so stabilnou structured schema a correlation fields. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Log archive account — AWS

Oddelený AWS member account určený na centrálne, dlhodobo chránené uloženie organization-wide audit a security logs. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Log canary

Periodicky generovaný synthetic log event používaný na overenie end-to-end collection, ingestion, storage a query latency. Pozri [Loki](docs/12-observability/loki.md).

## Log-delivery canary

Bounded synthetic event sledovaný od source inputu cez Fluent Bit acknowledgement až po backend query, duplicate count a delivery latency. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Log loss boundary

Konkrétny stav, pri ktorom telemetry pipeline môže zahodiť logs, napríklad full buffer, volatile crash, permanent output error alebo odstránený file pred dočítaním. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Log-loss window

Časový a source-specific interval, pre ktorý telemetry records nemožno preukázateľne obnoviť pre offset, buffer, rotation, drop alebo backend failure. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Log replay

Opätovné načítanie a odoslanie log records po reštarte, offset strate alebo backlog recovery, ktoré môže vytvoriť duplicates. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Log-stream identity

Tenant ID a úplný bounded Loki label set, ktoré spoločne definujú jeden log stream. Pozri [Loki](docs/12-observability/loki.md).

## Log stream — Loki

Množina log entries s rovnakým tenant ID a úplným label setom. Pozri [Loki](docs/12-observability/loki.md).

## Logical batch run subject

Identita jednej finite business operation zahŕňajúca run key, schedule alebo trigger, Job UID, template/input generation, work inventory a canonical result. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Logical data identity — Kubernetes

Application-owned identita persistentného datasetu, oddelená od Pod mena, PVC mena, PV phase a physical volume assetu. Pozri [Volumes, PV, PVC a StorageClass](../docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Logical demand unit — Golden Signals

Caller alebo business jednotka trafficu, napríklad logical settlement alebo message, oddelená od retries, fan-out calls a technical attempts. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Logical duration — RED

End-to-end trvanie caller-visible logical operation vrátane queue waitu, processingu, dependency attempts, retry backoffu a final completion pathu. Pozri [RED method](docs/12-observability/red-method.md).

## Logical operation

Jedna business alebo caller-visible operácia bez ohľadu na počet interných retry attempts a fan-out calls. Pozri [RED method](docs/12-observability/red-method.md).

## Logical-operation counter

Metric counter inkrementovaný raz podľa accepted alebo final outcome jednej business/caller-visible operation bez ohľadu na interný retry alebo fan-out počet. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Logical version

Ľudsky alebo procesne významná verzia, napríklad `2.8.1`, ktorá komunikuje release alebo compatibility význam, ale sama nemusí identifikovať konkrétne bytes bez väzby na digest. Pozri [Artifact versioning](docs/05-ci-cd-and-release/artifact-versioning.md).

## Logically air-gapped restore access

Controlled temporary path, cez ktorý recovery account môže restore-nuť recovery points z logically air-gapped vaultu po required authorization/approval. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Logically air-gapped vault — AWS Backup

Špeciálny backup vault s dodatočnou logical isolation a Vault Lock compliance ochranou pre ransomware a recovery use cases. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## LogQL

Loki query language kombinujúci stream selectors, line filters, parsing a metric aggregations nad logs. Pozri [Loki](docs/12-observability/loki.md).

## Loki

Label-indexed log aggregation systém ukladajúci log body komprimovane v chunks a používajúci object-storage-oriented storage model. Pozri [Loki](docs/12-observability/loki.md).

## Loki acceptance verdict

Dôkaz, že exact tenant/stream/schema logy sú ingestované, queryovateľné cez recent aj historical path a expirované iba podľa authoritative retention policy. Pozri [Loki](docs/12-observability/loki.md).

## Loki Compactor

Maintenance component, ktorý compactuje index blocks a podľa konfigurácie vykonáva retention a log deletion lifecycle. Pozri [Loki](docs/12-observability/loki.md).

## Loki entry acceptance

Distributor/ingester verdict, že log entry spĺňa tenant, label, timestamp, line-size, ordering a rate-limit contract a bola prijatá do write pathu. Pozri [Loki](docs/12-observability/loki.md).

## Loki evidence-completeness verdict

Rozhodnutie, či LogQL result reprezentuje očakávanú occurrence population alebo je neúplný pre collector, rejection, chunk, schema, retention či query failure. Pozri [Loki](docs/12-observability/loki.md).

## Loki labels

Bounded metadata tvoriace identity log streamov a indexovaný výberový priestor pre LogQL. Pozri [Loki](docs/12-observability/loki.md).

## Loki retention

Policy a maintenance proces určujúci, ako dlho sa log chunks a index data uchovávajú a kedy sa bezpečne odstránia. Pozri [Loki](docs/12-observability/loki.md).

## Loki retention generation

Versionovaný per-tenant/per-stream retention, Compactor/delete-delay a object-store lifecycle contract. Pozri [Loki](docs/12-observability/loki.md).

## Loki ruler

Component vyhodnocujúci LogQL recording alebo alerting rules. Pozri [Loki](docs/12-observability/loki.md).

## Loki subject

Exact tenant, stream-label generation, collector, schema period, deployment, object store, encryption, retention a LogQL scope analyzovaných logs. Pozri [Loki](docs/12-observability/loki.md).

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

Runtime vytvárajúci a spúšťajúci process podľa OCI runtime bundle a spravujúci namespaces, mounts a credentials. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Lucene

Search library tvoriaca základ Elasticsearch a OpenSearch shards a segment-based indexing/search modelu. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Lucene segment lifecycle

Prechod indexed documents cez refresh-created immutable segments, merges a neskoršie fyzické odstránenie deleted/updated records. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

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

## Managed-node eligibility

Stav, v ktorom exact machine má podporovaný OS, funkčný SSM Agent, správnu instance/hybrid identity, account/Region registration, time/DNS/TLS a required service/endpoint connectivity pre konkrétnu Systems Manager capability. Pozri [AWS Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## Managed node — Systems Manager

EC2 alebo non-EC2 machine zaregistrovaná v Systems Manager s funkčnou identity, agentom a network connectivity. Pozri [Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## Managed rotation — Secrets Manager

Rotation model, pri ktorom podporovaná managed service integrácia riadi rotation bez zákazníckej Lambda rotation function. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Managed service

Služba, pri ktorej provider preberá definovanú časť deploymentu, patchingu, availability alebo operations, pričom zákazníkovi zostáva configuration, identity, data a business outcome podľa konkrétneho contractu. Pozri [IaaS, PaaS a SaaS](docs/11-cloud-and-aws/iaas-paas-saas.md).

## Managed-service outcome boundary

Hranica medzi provider-managed platform health a zákazníckym application, data a business outcome-om; healthy managed service nepreukazuje správnu schema, access, restore ani user journey. Pozri [IaaS, PaaS a SaaS](docs/11-cloud-and-aws/iaas-paas-saas.md).

## Management account — AWS Organizations

Najvyšší organization account s billing a Organizations administrative capabilities; SCPs neobmedzujú jeho principals a preto má byť bez bežných workloadov a s minimálnym accessom. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Management-plane/workload-plane split — Docker

Rozlíšenie medzi Docker client/Engine API a daemon object managementom na jednej strane a container taskom, processom, application health a business request pathom na druhej strane. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Management-plane/workload-plane split — Kubernetes

Stav, keď API, persistence, scheduling alebo reconciliation capability je degradovaná, ale už spustené workload processes môžu dočasne pokračovať; workload success preto nepreukazuje recovery control plane-u. Pozri [Kubernetes architecture](docs/09-kubernetes/kubernetes-architecture.md) a [Control plane components](docs/09-kubernetes/control-plane-components.md).

## Mapping explosion

Nekontrolovaný rast počtu indexed field definitions spôsobený dynamic schemas alebo arbitrary object keys. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Mapping generation

Versionovaný field-type a structure contract aplikovaný na konkrétny index alebo backing-index generation. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

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

## Maximum-permission envelope

Guardrail, boundary alebo architecture contract určujúci najvyššiu authority, ktorú principal, delegated administrator alebo workload môže získať bez ohľadu na jednotlivé role assignments. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## Maximum surge

Limit dočasnej capacity nad desired replica count, ktorú môže rolling update vytvoriť na zachovanie dostupnosti a zrýchlenie rollout-u. Pozri [Rolling update](docs/05-ci-cd-and-release/rolling-update.md).

## Maximum unavailable

Limit počtu alebo percenta desired instances, ktoré môžu byť počas rolling update nedostupné. Pozri [Rolling update](docs/05-ci-cd-and-release/rolling-update.md).

## `maxLimitRequestRatio`

LimitRange pravidlo obmedzujúce maximálny pomer resource limitu k requestu pre konkrétny resource. Pozri [ResourceQuota a LimitRange](docs/09-kubernetes/resourcequota-limitrange.md).

## `maxSkew` — topology spread

Maximálna povolená nerovnomernosť počtu matching Podov medzi topology domains podľa konkrétneho spread constraintu. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Measurement boundary — telemetry

Presný observation point, napríklad client, edge, handler, consumer, dependency alebo final business completion, na ktorom signal meria occurrence. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Measurement population — RED

Množina valid operations definovaná rovnakou unit, scope, traffic eligibility a time semantics pre RED numerator, denominator a duration. Pozri [RED method](docs/12-observability/red-method.md).

## Media type — OCI

Identifikátor semantic formátu OCI descriptorom odkazovaného contentu. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

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

## Merge decision subject — GitLab

Presný obsah a context merge rozhodnutia: MR ID, source SHA, target alebo merge-base state, diff identity, merged-result alebo merge-train candidate a relevantná policy revision. Pozri [Merge requests a approvals](docs/06-gitlab/merge-requests-and-approvals.md).

## Merge mutation boundary — Helm

Hranica, na ktorej `set`, `unset`, `merge` alebo `mergeOverwrite` môžu meniť shared map reference a ovplyvniť neskoršie templates bez `deepCopy`. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Merge queue

Mechanizmus, ktorý testuje a integruje pull requests v plánovanom poradí proti aktuálnemu alebo predpokladanému stavu main branch. Pozri [Branching strategies](docs/03-git-and-automation/branching-strategies.md).

## Merge-result pipeline

Pipeline overujúca synthetic alebo reálny výsledok spojenia source zmeny s aktuálnym targetom namiesto samotného source branch tipu. Pozri [Continuous Integration](docs/05-ci-cd-and-release/continuous-integration.md).

## Merge train — GitLab

Queue model, ktorý overuje viac merge requests v predpokladanom poradí ich integrácie do target branch, aby chránil mainline health pri concurrency. Pozri [Merge requests a approvals](docs/06-gitlab/merge-requests-and-approvals.md).

## Merged filesystem lookup

Path resolution cez writable upper layer a ordered lower layers so zohľadnením whiteouts a opaque directories. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## Metamonitoring — alerting

Monitoring celého monitoring a notification reťazca vrátane source signalov, rule evaluation, Alertmanagera a externého receivera. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Metric

Agregovateľný číselný signal v čase používaný napríklad na rate, latency distribution, utilization, saturation alebo SLO measurement. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Metric-contract generation — Prometheus

Versionovaná definícia metric name, type, base unit, observation/reset boundary, labels, resource identity, expected freshness a consumers. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Metric identity contract — CloudWatch

Namespace, metric name, úplný dimension set, account/Region, unit, timestamp/resolution a publication cadence definujúce jednu CloudWatch time series a jej operational význam. Pozri [Amazon CloudWatch a AWS CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## Metric provenance and freshness — autoscaling

Evidence spájajúca observed value so source-om, query/labels, adapter generation, collection timestampom, aggregation window a tenant/workload subjectom. Pozri [HPA a autoscaling](../docs/09-kubernetes/hpa-autoscaling.md).

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

Minimalizovaná VM s rýchlejším startupom a menším overheadom pri zachovaní virtualized-kernel boundary. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Milestone generation — Well-Architected

Immutable snapshot konkrétnej review/risk/evidence state generácie používaný na porovnanie progressu, nie ako perpetual current-state proof. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Milestone — Well-Architected

Snapshot stavu workload review-u v konkrétnom čase používaný na meranie zmeny risku a improvement progressu. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Minimum detectable effect

Najmenšia zmena outcome metriky, ktorú má experiment pri zvolenej sample size a power spoľahlivo detegovať. Pozri [A/B testing](docs/05-ci-cd-and-release/a-b-testing.md).

## Minimum-TTL override

CloudFront behavior, pri ktorom positive cache-policy minimum TTL vynúti caching aspoň na tento čas aj pri origin directives `no-cache`, `no-store` alebo `private`. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## MINOR version

Druhá časť SemVer verzie, ktorá sa zvyšuje pri backward-compatible pridaní capability do deklarovaného public API. Pozri [Semantic Versioning](docs/05-ci-cd-and-release/semantic-versioning.md).

## Mirror delivery contract

Versionované pravidlá určujúce shadow mirror point, sample inventory, delivery semantics, queue/drop/lag limity, duplicate a ordering behavior a primary-path isolation. Pozri [Shadow deployment](docs/05-ci-cd-and-release/shadow-deployment.md).

## Mirror Pod

API-visible reprezentácia static Podu, ktorú kubelet vytvorí pre observability; authoritative configuration zostáva na konkrétnom Node-e. Pozri [Pod](docs/09-kubernetes/pod.md).

## Missed-schedule inventory

Zoznam CronJob scheduled timestamps, ktoré neboli vytvorené alebo dokončené, spolu s eligibility, deadline a catch-up rozhodnutím. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Missing-data verdict — CloudWatch

Alarm decision, ako vyhodnotiť absent datapoint (`breaching`, `notBreaching`, `ignore` alebo `missing`) podľa semantics konkrétneho heartbeat, success, error alebo sporadického signálu. Pozri [Amazon CloudWatch a AWS CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## Mixed-version compatibility

Schopnosť starej a novej application generácie bezpečne koexistovať nad spoločným trafficom a mutable state-om vrátane database, events, queues, cache, sessions, workers a client contractov. Pozri [Rolling update](docs/05-ci-cd-and-release/rolling-update.md).

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

## Module interface contract — Terraform

Versionované rozhranie modulu tvorené typovanými inputs, validation/default/null semantics, internými identity assumptions, minimálnymi stabilnými outputs a compatibility/deprecation policy. Pozri [Variables, locals a outputs](docs/07-infrastructure-as-code-and-configuration-management/variables-locals-outputs.md) a [Modules](docs/07-infrastructure-as-code-and-configuration-management/modules.md).

## Module registry — Terraform

Distribučná služba publikujúca versionované Terraform modules a ich metadata pre verejnú alebo internú spotrebu; sama negarantuje bezpečnosť ani kompatibilitu modulu. Pozri [Modules](docs/07-infrastructure-as-code-and-configuration-management/modules.md).

## Module source subject — Terraform

Immutable identita reusable modulu zahŕňajúca registry alebo VCS source, version/tag/commit, content digest alebo provenance podľa distribution modelu, ownera a release policy. Pozri [Modules](docs/07-infrastructure-as-code-and-configuration-management/modules.md).

## Module source — Terraform

Adresa, z ktorej Terraform počas initialization načíta child module, napríklad local path, registry alebo VCS source. Je to executable supply-chain dependency. Pozri [Modules](docs/07-infrastructure-as-code-and-configuration-management/modules.md).

## Module versioning — Terraform

Release a compatibility lifecycle reusable modulu zahŕňajúci version constraints, zmeny input/output contractu, provider requirements, migrations, deprecations a podporované upgrade paths. Pozri [Modules](docs/07-infrastructure-as-code-and-configuration-management/modules.md).

## Monitoring

Systematické sledovanie vopred definovaných signals, states a thresholds s cieľom detegovať známe failure alebo degradation conditions. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Monitoring condition contract

Versionovaná známa otázka, measurement query, threshold/no-data semantics, duration, owner, route, action a recovery condition používaná na monitoring verdict. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Monorepo

Repository obsahujúci viac služieb, knižníc alebo projektov so spoločným object graphom a možnosťou atomických cross-project zmien. Pozri [Monorepo vs. multirepo](docs/03-git-and-automation/monorepo-vs-multirepo.md).

## Mount

Pripojenie filesystemu alebo iného mountable objektu do spoločného filesystem stromu. Pozri [Storage, mounty a filesystems](docs/01-linux-and-systems/storage-mounts-and-filesystems.md).

## Mount authorization chain

End-to-end EFS path `DNS → mount target → route/SG/NACL → NFS/TLS → IAM/filesystem policy → access point → POSIX permission → operation`. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Mount generation — Kubernetes storage

Konkrétna väzba Pod UID, Node UID, VolumeAttachment/backend session, stage/publish operácií, mount options a filesystem identity. Pozri [Volumes, PV, PVC a StorageClass](../docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Mount namespace

Namespace poskytujúci samostatný pohľad na mount table a propagation. Pozri [Namespaces](docs/01-linux-and-systems/namespaces.md).

## Mount obscuring

Runtime jav, pri ktorom mount na destination path skryje image content v merged view bez odstránenia bytes z image layers. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## Mount obscuring — container

Runtime efekt, pri ktorom volume alebo bind mount pripojený na path prekryje files existujúce na rovnakom path-e v image filesysteme. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## Mount source identity

Logical a physical identita volume-u, external backendu, bind host pathu, tmpfs alebo socket/device source-u spolu s daemonom, hostom, projektom a lifecycle ownerom. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## `moved` block — Terraform

Versionovaná deklarácia `from` a `to` addressy, ktorou Terraform zachová resource alebo module identity počas configuration refaktoringu bez state surgery v každom environment-e. Pozri [Lifecycle, import a moved blocks](docs/07-infrastructure-as-code-and-configuration-management/lifecycle-import-moved-blocks.md).

## Moved history — Terraform

Sada `moved` blocks zachovaná naprieč module releases tak, aby consumers preskakujúci verzie mohli premapovať staré addresses bez neúmyselných replacements. Pozri [Lifecycle, import a moved blocks](docs/07-infrastructure-as-code-and-configuration-management/lifecycle-import-moved-blocks.md).

## Mover reconciliation

Identity lifecycle transition, ktorá vypočíta nové desired entitlements, odstráni staré incompatible paths, vykoná SoD kontrolu, pridá nové access paths a revoke-ne stale sessions. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## MSS — Maximum Segment Size

Maximálny TCP payload segmentu deklarovaný endpointom, typicky odvodený od MTU mínus IP a TCP headers. Pozri [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md).

## mTLS — Mutual TLS

TLS model autentifikujúci server aj klienta pomocou certificates. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## MTU — Maximum Transmission Unit

Maximálna veľkosť L3 packetu preneseného interfaceom bez fragmentácie. Pozri [IPv4, IPv6 a subnetting](docs/02-networking-and-web/ipv4-ipv6-subnetting.md).

## Multi-architecture SBOM

SBOM model, ktorý explicitne rozlišuje OCI image index a jednotlivé platform manifests a ich odlišné component inventories. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## Multi-AZ acceptance verdict

Dôkaz, že surviving Availability Zones majú compute, IP, egress, data, endpoint, quota a deployment capacity a udržia business outcome po strate jednej AZ. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## Multi-AZ architecture — AWS

Workload design rozkladajúci compute, networking a stateful capabilities cez viac Availability Zones tak, aby zlyhanie jednej zóny neodstavilo definovanú službu. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## Multi-AZ DB cluster — RDS

RDS deployment model s writer DB instance a dvoma readable instances v troch Availability Zones pri podporovaných engines, určený pre HA a read capacity. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## Multi-AZ DB instance deployment — RDS

RDS high-availability model s primary DB instance a synchronously maintained standby v inej Availability Zone, ktorý pri klasickom modeli neobsluhuje reads. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## Multi-cloud

Používanie services od viacerých cloud providers z obchodných, geografických, regulačných alebo technických dôvodov; samo osebe negarantuje portability ani disaster recovery. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Multi-controller oscillation

Nekonvergentný stav, pri ktorom dva individuálne idempotentné controllers autoritatívne zapisujú rozdielne hodnoty rovnakého fieldu alebo external resource-u. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Multi-loop ownership

Rozdelenie autoritatívnych fields a signals medzi HPA, VPA, Node autoscaler, GitOps a workload controller tak, aby loops nebojovali alebo neoscilovali. Pozri [HPA a autoscaling](../docs/09-kubernetes/hpa-autoscaling.md).

## Multi-party recovery approval

Workflow vyžadujúci súhlas viacerých independent trusted approvers pred high-impact restore-access operáciou nad logically air-gapped vaultom. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Multi-platform build

Jeden build workflow produkujúci platform-specific manifests a typicky spoločný image index pre viac OS/architecture kombinácií. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Multi-platform image

OCI index a graph poskytujúci manifests pre viac OS/architecture/variant kombinácií. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Multi-Region key — KMS

Súvisiace KMS key resources v rôznych Regions zdieľajúce key material a key ID properties, ale s oddelenými policies, grants a lifecycle. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Multi-signal canary — OpenTelemetry

Synthetic trace, metric a log overený cez agent, gateway, processing policies, každý intended backend, query correlation a forbidden-field check. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

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

## Multiple-response chain — CloudOps

Minimálna konzistentná kombinácia answer options, ktorá spoločne realizuje všetky required path boxes bez contradiction alebo forbidden outcome-u. Pozri [CloudOps domain review a timed reasoning](docs/11-cloud-and-aws/cloudops-domain-review-timed-reasoning.md).

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

## NACL ordered-policy generation

Kompletný inbound/outbound NACL ruleset vrátane rule numbers, CIDRs, protocols, ports, verdictov a subnet associations; first-match semantics znamená, že poradie je súčasťou policy. Pozri [Security Groups a Network ACLs](docs/11-cloud-and-aws/security-groups-network-acls.md).

## Name-reuse collision — Kubernetes

Failure, pri ktorom automation alebo external binding zamení zmazaný a znovu vytvorený object s rovnakým namespace/name, ale odlišným UID. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Named context — Docker build

Dodatočný explicitne pomenovaný build context dostupný Dockerfile-u podobne ako stage, používaný na užšie oddelenie source alebo external image inputs. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Named context subject

Identita explicitne pomenovaného build contextu, napríklad directory, Git commit alebo image digest. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Named-port contract

Cross-revision contract, v ktorom Service `targetPort` name musí byť deklarovaný a reálne obsluhovaný každým accepted Pod backendom. Pozri [Service a EndpointSlice](../docs/09-kubernetes/service-endpointslice.md).

## Named telemetry event

Structured OpenTelemetry log record s neprázdnym event name, ktoré identifikuje event type a jeho schema. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Named template — Helm

Globálne pomenovaný reusable template fragment deklarovaný cez `define` a použitý cez `template`, `include` alebo `block`. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Named volume — Docker

Docker volume s explicitným user-defined menom a samostatným lifecycle, vhodné na auditovateľnejší persistence a cleanup workflow. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## NameID — SAML

SAML subject identifier s definovaným formatom, napríklad persistent alebo transient. Pozri [SAML](docs/13-security-and-identity/saml.md).

## Namespace capacity envelope

Súčet baseline, rollout surge, HPA burst, Node-drain replacement, batch overlap a emergency recovery capacity, ktorú quota aj cluster musia umožniť. Pozri [ResourceQuota a LimitRange](../docs/09-kubernetes/resourcequota-limitrange.md).

## Namespace governance subject

Exact namespace UID, owner, quota/LimitRange generations, workload request, admitted delta, usage state a downstream capacity context. Pozri [ResourceQuota a LimitRange](../docs/09-kubernetes/resourcequota-limitrange.md).

## Namespace — Linux namespace

Kernel objekt poskytujúci procesu izolovaný pohľad na vybranú kategóriu systémového stavu. Pozri [Namespaces](docs/01-linux-and-systems/namespaces.md).

## Namespace takeover — package

Získanie kontroly nad opusteným, expirovaným alebo nesprávne rezervovaným package namespace-om a jeho použitie na distribúciu attacker-controlled contentu. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Namespace view

Process-specific pohľad na shared kernel state, napríklad PID tree, mounts alebo network stack; sám nie je resource limit ani access verdict. Pozri [Namespaces, cgroups a capabilities](docs/08-container-fundamentals-and-docker/namespaces-cgroups-capabilities.md).

## Namespaced resource — Kubernetes

Kubernetes resource, ktorého object identity a policy scope zahŕňajú namespace. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Narrow artifact copy — Dockerfile

Princíp kopírovania iba presne potrebných build outputs z build stage do final stage namiesto širokého prenosu celého stage filesystemu. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## NAT address generation

Aktuálny súbor private/public NAT addresses a AZ coverage, ktorý určuje source identity pozorovanú destination service-om a musí byť zosúladený s allowlists. Pozri [Internet Gateway a NAT Gateway](docs/11-cloud-and-aws/internet-gateway-nat-gateway.md).

## NAT availability mode

Vlastnosť rozlišujúca zonal single-AZ a regional multi-AZ NAT Gateway model. Availability mode nehovorí, či connectivity type je public alebo private. Pozri [Internet Gateway a NAT Gateway](docs/11-cloud-and-aws/internet-gateway-nat-gateway.md).

## NAT connectivity type

Vlastnosť rozlišujúca public NAT Gateway pre internet-routable translation a private NAT Gateway pre private/transit communication use cases. Nie je totožná s availability mode-om. Pozri [Internet Gateway a NAT Gateway](docs/11-cloud-and-aws/internet-gateway-nat-gateway.md).

## NAT — Network Address Translation

Mechanizmus meniaci source alebo destination IP adresy a často ports pri prechode packetu. Pozri [NAT](docs/02-networking-and-web/nat.md).

## NAT port-allocation verdict

Evidence založená na `ErrorPortAllocation`, connection counts, destination concentration, application retries/pooling a request timeline, že NAT nedokázal alokovať ďalší translated source port. Pozri [Internet Gateway a NAT Gateway](docs/11-cloud-and-aws/internet-gateway-nat-gateway.md).

## NAT port exhaustion — AWS

Stav, pri ktorom NAT path nemá dostatok dostupných source-port mappings pre veľký počet concurrent connections, často koncentrovaných na rovnaký destination tuple. Pozri [Internet Gateway a NAT Gateway](docs/11-cloud-and-aws/internet-gateway-nat-gateway.md).

## NAT64/DNS64

Prechodový model, v ktorom DNS64 syntetizuje IPv6 odpoveď a NAT64 prekladá traffic IPv6-only klienta na IPv4 server. Pozri [NAT](docs/02-networking-and-web/nat.md).

## Native builder

Builder node vykonávajúci build priamo na rovnakej architecture ako target bez user-mode emulation. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Native-histogram compatibility generation

Versionovaný adoption contract spájajúci client library, exposition, scrape, local storage/PromQL, rules, remote backend, dashboards a rollback pre Prometheus native histograms. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Native histogram — Prometheus

Histogram sample reprezentácia s dynamickejším rozlíšením a kompaktnejším prenosom než samostatné classic histogram bucket series, pri kompatibilnej pipeline. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Native runtime gate

Požadovaný test exact platform manifestu na native target platforme, ktorý overuje startup, loader/dependencies, health, signal behavior a business outcome nad digestom určeným na publication. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

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

## Negative-cache generation

NXDOMAIN alebo iný negative DNS verdict uložený v konkrétnej cache vrstve s vlastným TTL a ownerom. Pozri [Cluster DNS](../docs/09-kubernetes/cluster-dns.md).

## Negative DNS caching

Cacheovanie negatívnej DNS odpovede, napríklad `NXDOMAIN`. Pozri [DNS](docs/02-networking-and-web/dns.md).

## Negative qualifier — exam reasoning

Explicitná podmienka ako `without public internet`, `must retain evidence` alebo `without downtime`, ktorá vylučuje inak technicky funkčné candidate solutions. Pozri [CloudOps domain review a timed reasoning](docs/11-cloud-and-aws/cloudops-domain-review-timed-reasoning.md).

## Nested-group access path

Transitive entitlement cesta, v ktorej principal získava role alebo permission cez jednu alebo viac vnorených group memberships. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Network acceptance verdict

Verdikt, že current sandbox/IPAM/dataplane/policy generations poskytujú požadovaný packet aj reverse path, application identity a business outcome a zároveň blokujú forbidden flows. Pozri [CNI a NetworkPolicy](../docs/09-kubernetes/cni-networkpolicy.md).

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

## Network observation matrix

Mapa identity a evidence cez Pod sandbox, IPAM, route/tunnel, Service translation, policy selection, enforcement, connection a application boundaries. Pozri [CNI a NetworkPolicy](../docs/09-kubernetes/cni-networkpolicy.md).

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

## Node acceptance generation

Versionovaný verdict, že konkrétny Node UID po bootstrap-e, update-e alebo reboot-e poskytuje požadované DaemonSet capabilities a môže prijímať workload. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## Node affinity

Scheduling pravidlo vyberajúce alebo preferujúce Nodes podľa label expressions, hard alebo soft podľa použitého field-u. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Node allocatable

Časť Node capacity dostupná pre scheduling Pods po odpočítaní resources rezervovaných pre operating system a Kubernetes components podľa configuration. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## Node autoscaling

Automatické pridávanie alebo odoberanie Node capacity podľa schedulovateľnosti a cluster demand modelu. Pozri [HPA a autoscaling](docs/09-kubernetes/hpa-autoscaling.md).

## Node bootstrap dependency

Cyklická alebo kritická závislosť, pri ktorej Node potrebuje systémový DaemonSet agent na plnú funkčnosť, zatiaľ čo agent sám potrebuje funkčný scheduling, runtime alebo časť node infraštruktúry. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## Node candidate inventory

Versionovaný zoznam Node UIDs a ich labels, taints, conditions, allocatable, reservations, ports, devices a storage constraints pre jeden scheduling attempt. Pozri [Scheduling](../docs/09-kubernetes/scheduling.md).

## Node capability generation

Konkrétna per-Node verzia agent processu, host configuration, loaded programs/rules, sockets a registration state-u poskytujúca jednu platformovú capability. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## Node capability verdict

Dôkaz, že konkrétny worker Node bezpečne zvláda required kubelet, CRI, CNI, CSI, image, cgroup a Service-dataplane transitions, nie iba že reportuje `Ready=True`. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## Node condition

Štruktúrovaný status signál Node-u, napríklad Ready, MemoryPressure, DiskPressure alebo PIDPressure. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## Node execution generation

Versionovaný bundle node image, kubelet, runtime, CNI, CSI, cgroup a supporting configuration použitý na konkrétnej Node inštancii. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## Node execution subject — Kubernetes

Identita prideleného Podu a jeho Node-side realizácie zahŕňajúca Pod UID/spec generation, Node, kubelet/runtime/CNI/CSI generations, sandbox, image, mounts, probes, status a process outcome. Pozri [Kubernetes architecture](docs/09-kubernetes/kubernetes-architecture.md).

## Node-generation acceptance

Verdikt, že nový Node image/runtime/kubelet a jeho CNI, CSI, DNS, Service, policy, telemetry a workload capabilities fungujú pred prijatím produkčnej záťaže. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Node-label generation

Versionovaná množina security, pool a topology labels na konkrétnom Node UID alebo node-pool template-e. Pozri [Taints, tolerations, affinity a topology](../docs/09-kubernetes/taints-tolerations-affinity-topology.md).

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

## Node pressure/eviction subject

Konkrétny Node UID, pressure condition, kubelet threshold, resource signal, victim Pod UID a eviction generation. Pozri [Requests, limits a QoS](../docs/09-kubernetes/requests-limits-qos.md).

## Node recovery verdict

Dôkaz, že po node incidente fungujú sandbox create/delete, CNI/IPAM, CSI mount/unmount, image resolution, cgroup enforcement, probes, Service path, cleanup a pôvodný business outcome. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## Node replacement subject — Kubernetes cluster

Controlled transition medzi old a new Node generation vrátane join identity, capability conformance, drain, storage/network cleanup, object deletion a credential revocation. Pozri [Cluster installation a lifecycle](../docs/09-kubernetes/cluster-installation-lifecycle.md).

## NodeLocal DNS generation

Per-Node DNS cache agent, jeho configuration, cache a upstream state tvoriace samostatnú failure domain. Pozri [Cluster DNS](../docs/09-kubernetes/cluster-dns.md).

## NodeLocal DNSCache

Voliteľná node-local DNS caching vrstva, typicky nasadená ako DaemonSet, ktorá znižuje latency a pressure na central cluster DNS za cenu ďalšej per-node failure a cache vrstvy. Pozri [Cluster DNS](docs/09-kubernetes/cluster-dns.md).

## NodePort

Service type publikujúci port na eligible Node addresses a smerujúci traffic cez Service dataplane na backend endpoints. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## `nodeSelector`

Jednoduchý hard Pod placement constraint vyžadujúci, aby Node mal všetky uvedené label key/value páry. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## NoExecute failover contract

Chain od Node condition/taintu cez toleration window, eviction, replacement, storage/network reattachment a application fencing po obnovenie služby. Pozri [Taints, tolerations, affinity a topology](../docs/09-kubernetes/taints-tolerations-affinity-topology.md).

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

## Normalized realized savings

Post-change cost reduction očistená o business volume, seasonality, pricing/commitments, migration cost a secondary impacts. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Normalized route

Stabilný route pattern, napríklad `/orders/{id}`, používaný namiesto raw URL na zachovanie bounded metric a trace cardinality. Pozri [RED method](docs/12-observability/red-method.md).

## North-south traffic

Traffic medzi interným workloadom a externým klientom alebo službou mimo platformy. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## `NoSchedule` taint

Node taint effect zabraňujúci scheduleru umiestniť nový Pod bez matching toleration na daný Node. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Notification — Alertmanager

Receiver-specific správa vytvorená z jednej alert group podľa routing, timing, muting a template pravidiel. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Notification-decision path

Alertmanager lifecycle od prijatého alertu cez route, grouping, timing, silence/mute/inhibition verdict, template a receiver attempt po external incident outcome. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Notification-path canary

Kontrolovaný alert prechádzajúci rule, všetky Alertmanager replicas, route/group/muting policy, test receiver, external acknowledgement a resolved closure. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Notification-policy generation

Versionovaný routing, grouping, timing, inhibition, silence, receiver a template contract aplikovaný na alert identity. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Notification template — Alertmanager

Go template používaný na renderovanie notification title, body, links a receiver-specific payloadu. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## NUL-delimited stream

Textovo-binárny stream používajúci NUL byte ako oddeľovač, vhodný napríklad pre bezpečný prenos filesystem paths obsahujúcich whitespace alebo newline. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md).

## Number misscheduled — DaemonSet

Počet DaemonSet Podov bežiacich na Nodes, ktoré podľa aktuálneho DaemonSet placement modelu už nie sú eligible. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## NVD

National Vulnerability Database; enrichment source pre CVE records, scoring a product mappings, ktorý nie je authoritative inventory konkrétneho environmentu ani jediný prioritization source. Pozri [Vulnerability a patch management](docs/13-security-and-identity/vulnerability-and-patch-management.md).

## OAC origin authorization

CloudFront-to-S3 REST origin contract, v ktorom Origin Access Control podpisuje SigV4 request a bucket/KMS policy povoľuje exact distribution/service path bez public bucket accessu. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## OAuth 2.0

Authorization framework na delegovaný alebo workload access k protected APIs pomocou obmedzených tokens. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Object-bound credential

Credential, ktorého validity alebo trust je viazaná na lifecycle konkrétneho Kubernetes objektu, napríklad Podu alebo ServiceAccountu. Pozri [ServiceAccount](../docs/09-kubernetes/serviceaccount.md).

## Object class — LDAP

Schema definícia typu LDAP entry určujúca required a allowed attributes a inheritance. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## Object-count quota — Kubernetes

ResourceQuota limit počtu API objektov konkrétneho typu, napríklad Pods, Jobs, Secrets, PVCs alebo LoadBalancer Services. Pozri [ResourceQuota a LimitRange](docs/09-kubernetes/resourcequota-limitrange.md).

## Object-first troubleshooting

Diagnostický prístup začínajúci exact Kubernetes objectom, jeho spec/status, conditions, ownerReferences, Events a controller state-om. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Object-generation identity

S3 object identity viazaná minimálne na bucket, key, version ID, checksum, encryption a retention metadata; key bez version ID môže označovať meniacu sa current version. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Object ID — Git

Hash-based identifikátor Git objectu odvodený z typu a obsahu objektu. Pozri [Git object model](docs/03-git-and-automation/git-object-model.md).

## Object pipeline — PowerShell

Pipeline prenášajúca .NET objekty s properties a methods namiesto iba formátovaných textových riadkov. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## Object-store lifecycle mismatch — Loki

Stav, keď bucket expiration alebo transition odstráni či zneprístupní index/chunks skôr alebo inak než authoritative Loki retention model. Pozri [Loki](docs/12-observability/loki.md).

## Object UID generation

Jedna lifetime identity objectu vyjadrená UID spolu s konkrétnou desired-state generation; odlišuje name reuse aj viac zmien v rámci jednej object inštancie. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Object UID — Kubernetes

Server-generated immutable identity konkrétnej object inštancie; znovu vytvorený object s rovnakým menom dostane nové UID. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Observability

Schopnosť porozumieť internému stavu systému z jeho externých outputs a skúmať aj neočakávané otázky pomocou kvalitnej, korelovateľnej telemetry. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Observability acceptance

End-to-end dôkaz, že expected source je emitovaný, zozbieraný, potvrdený, queryable, retained, redacted a použiteľný pri alert alebo incident rozhodnutí. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Observability acceptance verdict

Dôkaz, že original business outcome je obnovený, forbidden outcome nevzniká, expected cross-signal correlation funguje a telemetry pipeline nevytvára false-green stav. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Observability evidence subject

Exact account, Region, resource/release/request/time cohort spolu s metric, log, alarm, audit, query a automation generations potrebnými na zodpovedanie konkrétnej operational alebo security otázky. Pozri [Amazon CloudWatch a AWS CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## Observability gap

Chýbajúci alebo nekvalitný signal, context, correlation, retention alebo query capability, ktorý bráni spoľahlivej diagnostike systému. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Observability maturity

Úroveň schopnosti organizácie štandardizovať instrumentation, correlation, alerting, SLO, telemetry governance a incident investigation. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Observability question contract

Exact investigation otázka viazaná na subject, time window, possible cohorts, competing hypotheses, required evidence a operational decision. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Observation-point authority

Rozhodnutie, ktorá client, edge, service, queue, dependency alebo business boundary je autoritatívna pre konkrétny metric, SLI alebo outcome. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Observed generation — Kubernetes

Status hodnota signalizujúca, ktorú verziu object desired state-u controller alebo agent už spracoval. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Observed state — Kubernetes

Stav, ktorý controller alebo agent aktuálne vidí cez API cache, runtime alebo external systém a používa ho pri reconciliation. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Observed subject — observability

Versionovaná kombinácia business capability, logical operation, release, configuration, telemetry generation, environment, Region/cohort a expected outcome, ku ktorej sa evidence viaže. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Occurrence-to-record boundary

Prechod medzi skutočnou system udalosťou a instrumentation rozhodnutím vytvoriť alebo nevytvoriť telemetry record. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## OCI artifact

Non-container alebo auxiliary content distribuovaný cez OCI manifest a registry semantics, napríklad signature, SBOM alebo provenance. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## OCI chart

Helm chart artifact distribuovaný cez OCI-compatible registry s version/digest identity a registry authentication modelom. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## OCI — Open Container Initiative

Organizácia definujúca standards pre image format, runtime lifecycle a registry distribution. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## OCI referrer

Artifact alebo discovery vzťah viažuci signature, SBOM alebo provenance na subject digest. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md) a [Registries](docs/08-container-fundamentals-and-docker/registries.md).

## OCI Referrers

OCI distribution model na discovery manifests, ktoré cez `subject` odkazujú na artifact digest, napríklad signatures, SBOMs alebo provenance. Pozri [SBOM](docs/13-security-and-identity/sbom.md) a [Image signing](docs/13-security-and-identity/image-signing.md).

## OCI release subject

Immutable release identity spájajúca source/build, image index, platform manifests, configs/layers, registry, trust artifacts a runtime contract. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## OCI runtime bundle

Directory obsahujúca `rootfs` a `config.json` s process, mounts, namespaces, capabilities a resources. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## OCI runtime — Docker

Low-level runtime implementujúci OCI Runtime Specification a vytvárajúci container process, namespaces, mounts a security/resource controls z runtime bundle-u. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## OCSP — Online Certificate Status Protocol

Protokol na zisťovanie revocation statusu certificate; server môže status poskytovať cez OCSP stapling. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## OIDC discovery

Štandardizované získanie OpenID Provider metadata vrátane issuer, endpoints a JWKS URI. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md).

## Old-generation retirement — Kubernetes upgrade

Overené odstránenie starej control-plane, Node, add-on, credential a telemetry generation po prijatí target platformy. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Omitted target — Ansible

Host alebo target, ktorý mal patriť do rollout scope-u, ale nevstúpil do resolved target inventory. Nemá task result ani `unreachable` verdict, preto sa odhalí iba porovnaním s expected target inventory. Pozri [Ansible architecture](docs/07-infrastructure-as-code-and-configuration-management/ansible-architecture.md).

## One-shot operation subject

Identita Compose migration alebo init jobu zahŕňajúca operation ID, image/config/data subject, project, concurrency lock, result a rerun/unknown-outcome semantics. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

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

## OpenTelemetry acceptance verdict

Dôkaz, že exact signal generations prešli per-hop accountingom, backend read-backom, correlation, cost a privacy checks a zostali správne po topology change alebo restart-e. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## OpenTelemetry API

Vendor-neutral programming contract používaný application a libraries na vytváranie telemetry bez vynútenia konkrétneho backendu alebo SDK konfigurácie. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## OpenTelemetry SDK

Runtime implementácia OpenTelemetry API, ktorá zabezpečuje sampling, processing, aggregation, resource configuration a export telemetry. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## OpenTelemetry subject

Exact application/release, SDK/agent, semantic schema, resource precedence, propagation, sampling, Collector distribution/config/topology, exporter, backend a evidence cut-off. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Operational acceptance testing

Overenie, že systém je prevádzkovateľný: má monitoring, recovery, backup/restore, capacity, runbooks, access controls a deployment/rollback mechanizmy. Pozri [End-to-end a acceptance tests](docs/04-testing-and-quality/end-to-end-and-acceptance-tests.md).

## Operational acceptance verdict — Systems Manager

Closure dôkaz, že exact approved targets dostali pinned document/configuration cez správnu identity a bounded execution, dosiahli technical aj business postconditions a forbidden tag-expansion, broad-role, stale-compliance a full-fleet mutation paths zostali zablokované. Pozri [AWS Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## Operational Excellence pillar

Well-Architected pillar zameraný na efektívny development, operations insight, safe change a continuous improvement. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## option group — RDS

Engine-specific RDS configuration object povoľujúci vybrané database features alebo integrations s vlastným lifecycle, restart a licensing modelom. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## Option injection

Situácia, keď hodnota začínajúca `-` je príkazom interpretovaná ako option namiesto dátového argumentu. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md).

## Orchestration acceptance verdict

Closure dôkaz, že approved image/workload generation bola správne umiestnená, má capacity, identity, network/storage a target eligibility, spĺňa business outcome a forbidden host-role, wrong-image, IP-exhaustion a unsafe-drain paths zostali kontrolované. Pozri [Amazon ECS a Amazon EKS](docs/11-cloud-and-aws/ecs-eks.md).

## `OrderedReady` — StatefulSet

Defaultný usporiadaný StatefulSet Pod management model, ktorý vytvára alebo aktualizuje ordinaly postupne a čaká na readiness pred pokračovaním. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Ordinal replacement subject

Old/new Pod UID, Node, IP, PVC/PV/backend volume, application member a fencing transitions pre jeden stabilný StatefulSet ordinal. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Ordinal slot — StatefulSet

Stabilná logical position identifikovaná ordinalom a predvídateľným Pod/DNS menom; replacement zachová slot, ale vytvorí nový Pod process subject. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

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

## Origin-request-only input

Header, cookie alebo query value forwardovaná CloudFront originu cez origin request policy, ale nezahrnutá v cache key; nesmie meniť cacheable representation bez ďalšieho bezpečného contractu. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## origin request policy — CloudFront

Policy určujúca headers, cookies a query strings posielané CloudFront originu bez ich automatického zahrnutia do cache key. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Origin Shield — CloudFront

Voliteľná regionálna caching vrstva pred originom, ktorá konsoliduje cache misses z viacerých edge locations a znižuje duplicate origin fetches. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Original outcome contract — Docker incident

Explicitný client-to-business journey a jeho latency, correctness, data, identity a exactly-once expectations, podľa ktorého sa posudzuje incident aj recovery. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Original-outcome verification — Kubernetes

Opätovné overenie pôvodného používateľského alebo business cieľa po remediation, nie iba technického stavu komponentu. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Orphan container — Compose

Container patriaci Compose projektu, ktorého service už nie je prítomná v aktuálnom resolved modeli. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Orphan volume — Docker

Volume, ktoré už nemá aktívneho workload ownera alebo referenciu, ale stále obsahuje dáta a spotrebúva storage; pred odstránením potrebuje ownership a retention overenie. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## Orphaned Pod — Kubernetes

Pod bez controller owner reference, ktorý môže zostať po orphan deletion alebo strate ownershipu a môže byť adoptovaný matching controllerom. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Orphaned Pod — ReplicaSet

Pod bez aktuálneho controller ownera, napríklad po orphan deletion alebo manual ownership zásahu, ktorý môže ďalej bežať, prijímať traffic alebo byť adoptovaný. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## OSI model

Sedemvrstvový konceptuálny model sieťovej komunikácie. Pozri [OSI a TCP/IP model](docs/02-networking-and-web/osi-and-tcp-ip-model.md).

## OTel API

Programovací contract používaný application a instrumentation libraries bez vynútenia konkrétneho backendu alebo runtime konfigurácie. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## OTel SDK

Runtime implementácia OpenTelemetry API zabezpečujúca sampling, aggregation, processing, resource configuration a export. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## OTLP

OpenTelemetry Protocol používaný na prenos telemetry medzi SDKs, Collectors a podporovanými backends. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## OU placement generation

Aktuálna poloha accountu v Organizations hierarchy spolu s parent policy inheritance cestou a časom posledného move-u. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Outcome-first parsing — CloudOps

Question intake discipline, pri ktorej sa pred service keywordom identifikuje požadovaný stav, zakázané stavy, scope, operation type a rozhodujúce qualifiers. Pozri [CloudOps domain review a timed reasoning](docs/11-cloud-and-aws/cloudops-domain-review-timed-reasoning.md).

## Outdated deployment — GitLab

Deployment zo staršieho pipeline, ktorý sa pokúša prepísať environment po tom, čo už bol nasadený novší pipeline alebo artifact. Pozri [Environments, deployments a releases](docs/06-gitlab/environments-deployments-releases.md).

## Output-independent liveness — Fluent Bit

Liveness contract, ktorý overuje schopnosť agent processu pokračovať bez reštartu iba preto, že vzdialený telemetry backend je dočasne nedostupný. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

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

## Owner-dependent graph subject

Inventory Kubernetes ownerReferences, owner/dependent UIDs, selectors, revisions, propagation policy a current lifecycle state pre konkrétnu top-level object generation. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## OwnerReference — Kubernetes

Metadata väzba dependent objectu na owner object pomocou owner UID, používaná controllers a garbage collectorom. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Ownership adoption — Terraform

Riadené prevzatie existujúceho remote objektu do Terraform management modelu cez configuration, presný provider target, import mapping, nový state binding a reviewed post-import reconciliation. Pozri [Lifecycle, import a moved blocks](docs/07-infrastructure-as-code-and-configuration-management/lifecycle-import-moved-blocks.md).

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

## Page eligibility contract

Kritériá urgentnosti, importance, actionability a reality, ktoré musí signal splniť pred preradením na human page. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Page fault

Udalosť, pri ktorej požadované virtuálne mapovanie nie je okamžite dostupné. Pozri [Memory a CPU fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## Pages-per-incident

Alert-quality metric počítajúca počet human pages vytvorených jedným operational incidentom. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Paired shadow evidence

Korelovaný primary a shadow execution record viazaný na rovnaký mirror event, input/state identity, artifact/config revisions, lag a normalization policy. Missing alebo neporovnateľný pair sa nesmie klasifikovať ako úspešná zhoda. Pozri [Shadow deployment](docs/05-ci-cd-and-release/shadow-deployment.md).

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

## Partial-batch acknowledgement

Event-source-mapping response contract, ktorý označí konkrétne failed records na retry namiesto celého batchu; timeout alebo strata response stále vyžaduje idempotentné spracovanie všetkých records. Pozri [AWS Lambda](docs/11-cloud-and-aws/lambda.md).

## Partial batch response — Lambda

Event-source-mapping contract umožňujúci označiť iba konkrétne records v batchi ako neúspešné, aby sa nemuselo retryovať celé spracované batch. Pozri [Lambda](docs/11-cloud-and-aws/lambda.md).

## Partial clone

Clone režim, ktorý odloží prenos vybraných objects a načíta ich podľa potreby, napríklad s `--filter=blob:none`. Pozri [Clone, fetch, pull a push](docs/03-git-and-automation/clone-fetch-pull-push.md).

## Partial evaluation — policy

Predvýpočet policy nad známymi data s vytvorením residual query pre runtime input, používaný na optimalizáciu alebo embedded enforcement. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Partial failure — controller

Stav, keď controller dokončí iba časť distribuovanej operácie, napríklad vytvorí external resource, ale nestihne uložiť jeho identity do statusu, a musí sa bezpečne zotaviť pri retry. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Partitioned-node execution

Stav, keď Node alebo kubelet stratil spojenie s control plane-om, ale local workload processes pokračujú a môžu sa prekrývať s replacement Pods vytvorenými inde. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## Partner allowlist boundary

External authorization boundary, pri ktorej partner rozhoduje podľa translated public source IP alebo inej egress identity; zmena NAT/EIP generation môže znefunkčniť technicky zdravý path. Pozri [Internet Gateway a NAT Gateway](docs/11-cloud-and-aws/internet-gateway-nat-gateway.md).

## Pass-the-ticket

Attack, pri ktorom útočník použije ukradnutý Kerberos TGT alebo service ticket bez znalosti pôvodného passwordu. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Password-client script — Ansible Vault

Executable helper poskytujúci vault password z chráneného zdroja, typicky po autentifikácii job identity voči secret manageru. Pozri [Vault](docs/07-infrastructure-as-code-and-configuration-management/vault.md).

## PAT — Port Address Translation

NAT model, v ktorom viac interných flows zdieľa jednu externú adresu a rozlišuje sa preloženými portmi. Pozri [NAT](docs/02-networking-and-web/nat.md).

## Patch compliance freshness

Patch verdict viazaný na exact node, OS, baseline/policy, repository/snapshot context, scan/install execution a timestamp; starý `COMPLIANT` state nie je dôkaz aktuálneho patch ani application zdravia. Pozri [AWS Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

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

## Pending operation unknown outcome — Helm

Stav, keď release metadata alebo klient nevie potvrdiť výsledok upgrade-u, rollbacku alebo hooku, hoci niektoré Kubernetes alebo external mutations mohli prebehnúť; vyžaduje observation pred retry. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Pending rollback — Helm

Release status signalizujúci nedokončenú rollback operáciu, typicky prebiehajúcu alebo prerušenú pri hooku, API requeste, wait-e alebo release storage update. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Pending upgrade — Helm

Release status signalizujúci nedokončenú upgrade operáciu; pred recovery vyžaduje kontrolu hooks, Jobs, client concurrency, live resources a release evidence. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Per-AZ endpoint cohort

Skupina application, load-balancer alebo service endpoints klasifikovaná podľa AZ ID a generation na rozlíšenie regionálneho od zonálneho failure-u. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## Per-hop telemetry accounting

Porovnanie received, accepted, refused, dropped, queued a acknowledged records na každom SDK, agent, gateway, exporter a backend hop-e. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Per-host task transition — Ansible

Jedna task operation vyhodnotená a vykonaná pre konkrétny host s vlastnou eligibility, action/module contextom a resultom `ok`, `changed`, `failed`, `unreachable` alebo `skipped`. Pozri [Modules, tasks, plays a playbooks](docs/07-infrastructure-as-code-and-configuration-management/modules-tasks-plays-playbooks.md).

## Per-item bulk verdict

Accepted, retryable, permanent-failure, quarantined alebo unknown outcome každého documentu v Elasticsearch/OpenSearch bulk response. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Per-metric HPA recommendation

Desired replica count vypočítaná pre jednu Resource, ContainerResource, Pods, Object alebo External metric pred kombináciou viacerých metrics a behavior policy. Pozri [HPA a autoscaling](../docs/09-kubernetes/hpa-autoscaling.md).

## Per-Node capability canary

End-to-end test node-local capability, napríklad sandbox create, Service flow, volume publish alebo telemetry delivery, ktorý je silnejší než agent liveness/readiness. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## Per-node overhead — DaemonSet

CPU, memory, storage, network a operational cost jedného DaemonSet Podu vynásobený počtom eligible Nodes v clustri. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## Per-Node placement subject

Väzba DaemonSet UID/generation, Node UID, Pod UID, admitted placement spec a current revision pre jeden eligible Node. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## Per-ordinal storage identity

Väzba StatefulSet ordinalu na PVC UID, PV, backend volume, filesystem a data generation. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Per-platform evidence inventory

Očakávaná množina manifest, SBOM, provenance, test, runtime a policy verdictov pre každú podporovanú OS/architecture/variant branch a vyšší image index subject. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Per-prefix route contract

Hybridný routing invariant určujúci, ktoré source a destination prefixes musia byť propagované, akceptované a symetricky routované cez primary a recovery paths. Pozri [Public, private a hybrid cloud](docs/11-cloud-and-aws/public-private-hybrid-cloud.md).

## Per-replica PVC — StatefulSet

PersistentVolumeClaim viazaný na konkrétny StatefulSet ordinal a znovu použitý náhradným Podom s rovnakou logical identity. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Performance Efficiency pillar

Well-Architected pillar zameraný na efektívny výber a používanie compute resources podľa workload requirements a technologického vývoja. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Performance test

Test časových a kapacitných vlastností systému pri explicitnom workload modeli, prostredí a success criteria. Pozri [Performance, load a stress tests](docs/04-testing-and-quality/performance-load-stress-tests.md).

## Permission graph

Resolved tok authority medzi pipeline jobs, runners, artifacts, secrets, registries, cloud roles a environments používaný na review effective blast radiusu. Pozri [Pipeline as Code](docs/05-ci-cd-and-release/pipeline-as-code.md).

## Permission path — Kubernetes RBAC

Jedna konkrétna cesta `subject/group → binding → roleRef → resolved rule → request match`, ktorá prispieva do additive allow verdictu. Pozri [RBAC](../docs/09-kubernetes/rbac.md).

## Permissions boundary

Guardrail určujúci maximálny permissions envelope identity bez samostatného udelenia accessu. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## Permissions boundary — IAM

IAM policy nastavujúca maximálny permissions envelope, ktorý identity-based policies môžu udeliť konkrétnemu userovi alebo role. Sama permissions neudeľuje. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## Permissions envelope — AWS

Policy vrstva, ktorá access sama neudeľuje, ale obmedzuje maximum candidate grants, napríklad permissions boundary, session policy, SCP alebo RCP. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## Permissive mode

SELinux režim, v ktorom sa policy denials auditujú, ale nevynucujú. Pozri [SELinux a AppArmor](docs/01-linux-and-systems/selinux-and-apparmor.md).

## Perpetual drift

Opakovaný konflikt, pri ktorom viac actorov striedavo prepisuje ten istý stav podľa rozdielnych desired-state deklarácií. Pozri [Ansible idempotencia](docs/07-infrastructure-as-code-and-configuration-management/ansible-idempotency.md).

## Persistence classification — container

Rozdelenie writable paths na ephemeral, persistent business, re-injectable config/secret a incident evidence state. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## Persistent data preflight

Kontrola logical data ID, environmentu, generation/schema, writer epoch, source volume/backend identity a backup compatibility pred prvou runtime mutation. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## Persistent data subject — container

Identita durable state-u zahŕňajúca logical data ID, generation, backend/filesystem, topology/access mode, writer authority, encryption a backup contract. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## Persistent queue — telemetry

Queue uchovávajúca telemetry state na persistentnom médiu, aby prežila process restart podľa contractu konkrétneho komponentu. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## PersistentVolume

Cluster-scoped Kubernetes object reprezentujúci konkrétny persistent storage resource a jeho capacity, access, topology, reclaim a CSI metadata. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## PersistentVolumeClaim

Namespaced Kubernetes request na persistent storage definujúci požadovanú capacity, access mode, volume mode a StorageClass. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Pester

PowerShell test framework pre assertions, mocks, setup/teardown a test discovery. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## PID limit — container

Cgroup limit počtu procesov/threadov chrániaci host pred fork bomb alebo nekontrolovaným rastom. Pozri [Namespaces, cgroups a capabilities](docs/08-container-fundamentals-and-docker/namespaces-cgroups-capabilities.md).

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

Správa delivery workflowu ako versionovaného, reviewovateľného, testovateľného a policy-validovaného privilegovaného programu. Pozri [Pipeline as Code](docs/05-ci-cd-and-release/pipeline-as-code.md).

## Pipeline cache

Dočasné znovupoužiteľné dáta určené na zrýchlenie pipeline, napríklad dependencies alebo compiler outputs. Cache nie je release artifact ani source of truth. Pozri [Continuous Integration](docs/05-ci-cd-and-release/continuous-integration.md).

## Pipeline — CI/CD

Runtime inštancia versionovaného delivery workflowu vytvorená konkrétnym triggerom a viazaná na candidate, event context, variables, jobs, permissions, artifacts a results. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## Pipeline creation policy — GitLab CI/CD

Versionovaný `workflow:rules` contract určujúci, pre ktoré pipeline sources, refs a dostupný variable context má pipeline vzniknúť a aký účel daný run plní. Pozri [GitLab CI/CD syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md).

## Pipeline instance

Konkrétny runtime run po vyhodnotení workflow definície, trigger payloadu, candidate identity, conditions, matrix, permissions a environment policy. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## Pipeline last argument — Helm

Pravidlo, podľa ktorého pipeline odovzdá svoj ľavý výsledok ako posledný positional argument nasledujúcej template funkcie. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Pipeline processor — telemetry

Komponent medzi receiverom a exporterom, ktorý môže vykonávať batching, filtering, redaction, enrichment, sampling alebo routing. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Pipeline — shell

Reťaz procesov, v ktorej stdout jedného procesu smeruje do stdin ďalšieho. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md).

## Pipeline verdict completeness — GitLab

Vlastnosť pipeline verdictu dokazujúca, že všetky required jobs, shards, child/downstream pipelines, reports a artifacts pre daný subject vznikli a boli zahrnuté do gate rozhodnutia. Pozri [GitLab CI/CD syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md).

## PKCE

Proof Key for Code Exchange, ktorý viaže authorization-code exchange na client instance cez code challenge a verifier. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## PKI — Public Key Infrastructure

Systém certificate authorities, policies, trust stores, issuance, validation, rotation a revocation pre public-key identities. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## Placement acceptance verdict

Verdikt, že desired Pody sú schedulovateľné, ready/serving cohort má požadované failure-domain rozloženie a workload ani neželaný tenant neprekročili dedicated-pool boundary. Pozri [Taints, tolerations, affinity a topology](../docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Placement deadlock

Stav, keď kombinácia hard affinity, anti-affinity, taints, topology, storage alebo resource constraints nevytvára žiadny feasible Node. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Placement drift

Rozdiel medzi current placement intentom a labels/taints/topology stavom bežiaceho Podu alebo Node-u, ktorý sa môže prejaviť až pri replacement-e pre `IgnoredDuringExecution`. Pozri [Taints, tolerations, affinity a topology](../docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Placement generation

Resolved Pod placement contract obsahujúci nodeSelector/affinity, tolerations, Pod affinity/anti-affinity, topology spread a relevantné scheduler/storage constraints. Pozri [Taints, tolerations, affinity a topology](../docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## placement group — EC2

EC2 placement constraint optimalizujúci cluster latency/throughput, spread failure isolation alebo partitioned distributed-system topology. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Placement observation matrix

Mapa evidence cez Pod generation, scheduler profile, trusted Node labels/taints, population selectors, eligible domains, skew, PVC topology, Events, binding a ready endpoint distribution. Pozri [Taints, tolerations, affinity a topology](../docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Placement verdict — containers

Scheduler decision, že task alebo Pod spĺňa viditeľné resource, attribute, topology, taint/affinity, port, volume a capacity constraints; nepreukazuje process startup, networking, readiness ani business zdravie. Pozri [Amazon ECS a Amazon EKS](docs/11-cloud-and-aws/ecs-eks.md).

## Plaintext

Nešifrované dáta dostupné application alebo používateľovi pred encryption alebo po decryption. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## Plan artifact — Terraform

Uložený Terraform plan viazaný na configuration, variables, provider/module selections a prior state, ktorý má byť reviewovaný, policy-evaluovaný a následne aplikovaný ako ten istý immutable decision artifact. Pozri [Terraform testing a policy](docs/07-infrastructure-as-code-and-configuration-management/terraform-testing-and-policy.md).

## Plan test — Terraform

Native Terraform test run používajúci `command = plan` na overenie plan-time contractu bez vytvorenia reálnej infraštruktúry. Pozri [Terraform testing a policy](docs/07-infrastructure-as-code-and-configuration-management/terraform-testing-and-policy.md).

## Platform branch subject — BuildKit

Identita jednej target-platform vetvy build graphu zahŕňajúca selected node, native/emulated/cross-compile mode, base manifest, platform cache, output manifest a test evidence. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Platform compatibility contract — container

Požiadavky na kernel/runtime features, CPU, libc, devices, filesystem, seccomp/LSM, storage a network potrebné na spustenie workloadu. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Platform decommission subject

Cluster/Node/infra/data/credential inventory a verified cleanup transition, ktorý uzatvára traffic, resources, identities, backups, audit a external infrastructure. Pozri [Cluster installation a lifecycle](../docs/09-kubernetes/cluster-installation-lifecycle.md).

## Platform manifest — OCI

Konkrétny manifest vybraný z indexu pre OS/architecture/variant, odkazujúci na config a layers. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Platform mismatch — container image

Nesúlad medzi target OS/architecture a vybraným image manifestom alebo executable, ktorý môže viesť k pull failure alebo `exec format error`. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Platform ownership matrix — Kubernetes

Explicitné rozdelenie zodpovednosti za control plane, etcd, Nodes, add-ons, upgrades, identity, application data, recovery a incident support medzi provider/platform/application owners. Pozri [Cluster installation a lifecycle](../docs/09-kubernetes/cluster-installation-lifecycle.md).

## Pod

Najmenší deployable Kubernetes compute object predstavujúci jeden alebo viac co-scheduled containers so spoločnou Pod network identity, lifecycle boundary a volumes. Pozri [Pod](docs/09-kubernetes/pod.md).

## Pod acceptance verdict

Verdikt, že konkrétny Pod UID má správny admitted spec, image/config/secret state, sandbox a mounts, containers, probes, readiness gates, EndpointSlice eligibility a business outcome. Pozri [Pod](docs/09-kubernetes/pod.md).

## Pod adoption — Kubernetes

Proces, pri ktorom controller prevezme matching Pod bez controller owner reference a nastaví ho ako svoj dependent object. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Pod affinity

Scheduling pravidlo priťahujúce Pod do topology domain, kde už existujú matching Pody. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Pod anti-affinity

Scheduling pravidlo oddeľujúce Pod od topology domains obsahujúcich matching Pody, hard alebo soft podľa konfigurácie. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Pod condition

Štruktúrovaný Pod status signal, napríklad Scheduled, Initialized, ContainersReady alebo Ready, ktorý je odlišný od high-level Pod phase. Pozri [Pod](docs/09-kubernetes/pod.md).

## Pod-create identity delegation boundary

Security boundary, pri ktorej právo vytvoriť Pod alebo controller s vybraným ServiceAccountom prakticky deleguje authority tejto workload identity. Pozri [ServiceAccount](../docs/09-kubernetes/serviceaccount.md).

## Pod-delivered configuration

Konkrétna environment alebo filesystem projection generation sprístupnená jednému Pod/container subjectu, odlišná od latest API objectu aj process-loaded state-u. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Pod effective request

Scheduler-visible resource request Podu po započítaní bežných containers, init/restartable sidecars, Pod-level resources a RuntimeClass overhead podľa current API semantics. Pozri [Requests, limits a QoS](../docs/09-kubernetes/requests-limits-qos.md).

## Pod network identity

Runtime network identity konkrétneho Podu tvorená Pod UID, sandbox/container ID, network namespace, interface a IPAM allocation; workload label alebo Pod meno ju nenahrádza. Pozri [CNI a NetworkPolicy](../docs/09-kubernetes/cni-networkpolicy.md).

## Pod network realization subject

Súvislý CNI/IPAM/interface/route/policy state vytvorený pre konkrétny Pod sandbox na konkrétnom Node-e. Pozri [CNI a NetworkPolicy](../docs/09-kubernetes/cni-networkpolicy.md).

## Pod phase

High-level summary lifecycle state-u Podu: Pending, Running, Succeeded, Failed alebo Unknown; reasons ako CrashLoopBackOff nie sú samostatné phases. Pozri [Pod](docs/09-kubernetes/pod.md).

## Pod readiness gate

Custom condition zahrnutá do Pod readiness rozhodnutia, ktorú musí nastavovať zodpovedný external alebo platform controller. Pozri [Pod](docs/09-kubernetes/pod.md).

## Pod replacement subject

Lifecycle nového Pod UID vytvoreného workload controllerom po deletion, eviction, rollout alebo failure predchádzajúceho Podu, s novým sandboxom a execution chainom. Pozri [Pod](docs/09-kubernetes/pod.md).

## Pod resolver generation

Actual resolver state v konkrétnom Pode odvodený z namespace-u, `dnsPolicy`, `dnsConfig`, kubelet a Node resolver configuration. Pozri [Cluster DNS](../docs/09-kubernetes/cluster-dns.md).

## Pod runtime-envelope subject

Identita jednej Pod repliky zahŕňajúca owner/revision, Pod UID, admitted spec, shared network/volume boundary, containers, Node assignment, conditions, endpoint eligibility a termination state. Pozri [Pod](docs/09-kubernetes/pod.md).

## Pod sandbox

Runtime prostredie Podu vytvorené cez CRI, ktoré drží najmä shared network namespace a infra lifecycle pre Pod containers. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md) a [Pod](docs/09-kubernetes/pod.md).

## Pod sandbox subject

Identita CRI runtime sandboxu konkrétneho Pod UID vrátane Node, sandbox ID, network namespace, Pod IP, CNI result, runtime generation a lifecycle state. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## Pod scheduling attempt

Jedno scheduler vyhodnotenie konkrétneho Pod UID cez queue, active profile, filter, score a binding cycle. Pozri [Scheduling](../docs/09-kubernetes/scheduling.md).

## Pod Security Admission — PSA

Built-in Kubernetes admission controller vyhodnocujúci Pods podľa versionovaných Pod Security Standards a namespace režimov enforce, audit a warn. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## Pod Security Standards — PSS

Versionované Kubernetes security profily Privileged, Baseline a Restricted definujúce povolené Pod security fields a privilege model. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## Pod selector — workload controller

Label selector určujúci population Podov, ktorú workload controller pozoruje a riadi; tvorí zásadnú ownership a reconciliation boundary. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Pod template

Embedded desired Pod metadata a spec v workload controller resource-e, z ktorého controller vytvára nové Pod instances. Pozri [Pod](docs/09-kubernetes/pod.md).

## Pod-template revision subject

Admitted Deployment Pod template, jeho hash, image/config/security content a ReplicaSet UID tvoriace jednu rollout revision. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## Pod UID generation

Jedna disposable workload-replica identity viazaná na owner revision a admitted Pod spec; replacement s podobným menom je nový subject s novým UID. Pozri [Pod](docs/09-kubernetes/pod.md).

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

## Policy-decision verdict

Exact allow, deny alebo error výsledok PDP nad principal–action–resource–context tuple-om a konkrétnou policy/attribute generation. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

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

## Policy-information freshness

Dôkaz, že group, ownership, tenant, device, risk a ďalšie PIP attributes použité pri authorization zodpovedajú current authoritative state-u. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

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

## Policy observation point — AWS network

Presná enforcement/telemetry boundary, na ktorej sú viditeľné konkrétne addresses, ports, direction a pre/post-NAT identity; verdict z iného bodu nemusí patriť rovnakému flow subjectu. Pozri [Security Groups a Network ACLs](docs/11-cloud-and-aws/security-groups-network-acls.md).

## Policy peer — NetworkPolicy

Source alebo destination množina vyjadrená cez Pod selector, namespace selector, ich kombináciu alebo `ipBlock`. Pozri [CNI a NetworkPolicy](docs/09-kubernetes/cni-networkpolicy.md).

## Policy Report — Kyverno

Kubernetes custom resource obsahujúci current evaluation results matching resources pre Kyverno policies; nejde o kompletný historical admission log. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy revision

Immutable alebo jednoznačne versionovaná identita konkrétneho policy setu použitá pri decisione, rolloute a audite. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy revocation generation — Kubernetes networking

Transition z allow policy/connection state-u na deny state vrátane overenia nových aj existujúcich flows a prípadného session/credential cleanupu. Pozri [CNI a NetworkPolicy](../docs/09-kubernetes/cni-networkpolicy.md).

## Policy routing

Routing model, ktorý môže vyberať table podľa source address, marku, ingress interface alebo ďalších selectors. Pozri [Routing a default gateway](docs/02-networking-and-web/routing-and-default-gateway.md).

## Policy selection subject — Kubernetes networking

Exact source alebo destination Pod UID, namespace/Pod labels, direction a matching NetworkPolicy UID/generation inventory použitý na vytvorenie allow unionu. Pozri [CNI a NetworkPolicy](../docs/09-kubernetes/cni-networkpolicy.md).

## Policy unit test

Automatizovaný positive, negative alebo boundary scenario overujúci expected policy decision pre konkrétny input a data. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Policy verdict — Terraform

Subject-bound rozhodnutie policy engine-u nad konkrétnou configuration alebo saved-plan evidence, ktoré explicitne rozlišuje pass, violation, exception, invalid/missing input a tool/service error. Pozri [Terraform testing a policy](docs/07-infrastructure-as-code-and-configuration-management/terraform-testing-and-policy.md).

## Policy version pinning — Pod Security

Explicitné naviazanie Pod Security Admission režimu na konkrétnu Kubernetes minor policy verziu, aby cluster upgrade nezmenil enforcement bez testovaného rollout-u. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## Policy WebAssembly

Skompilovaná policy vykonávaná ako WebAssembly module v embedded PEP alebo application runtime. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Port

16-bit transportný identifikátor socket endpointu. Port sám neurčuje aplikačný protokol. Pozri [Ports a sockets](docs/02-networking-and-web/ports-and-sockets.md).

## Port-publication subject — container

Mapping host bind addressu, portu a protocolu cez forwarding/NAT/proxy na container address/port s policy. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Port publishing

Host-side forwarding alebo proxy konfigurácia sprístupňujúca container port cez host address a port. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Position database — Fluent Bit

Persistentný state Tail inputu uchovávajúci file identity a read offset na restart a rotation recovery. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Position-state durability — Fluent Bit

Schopnosť Tail DB a source offset/inode state-u prežiť definovaný container, Pod alebo Node restart boundary. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Post-import plan — Terraform

Prvý fresh plan po vytvorení import bindingu, používaný na rozhodnutie, či configuration remote stav adoptuje, zmení alebo by nebezpečne vyvolala update či replacement. Pozri [Lifecycle, import a moved blocks](docs/07-infrastructure-as-code-and-configuration-management/lifecycle-import-moved-blocks.md).

## Post-import reconciliation — Terraform

Review prvého planu po importe, ktorý rozhoduje, či sa remote hodnoty adoptujú do configuration, vrátia k desired state-u, rozdelí sa attribute ownership alebo sa chybný binding odstráni. Pozri [Lifecycle, import a moved blocks](docs/07-infrastructure-as-code-and-configuration-management/lifecycle-import-moved-blocks.md).

## Post-promotion watch

Observation obdobie po dosiahnutí plnej expozície, ktoré sleduje oneskorené, kumulatívne alebo segmentovo zriedkavé failures pred uzavretím release rozhodnutia. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Post-relabel sample set

Exact množina samples a labels, ktorá zostane po target-label application a metric relabelingu a môže byť ingestovaná do local TSDB. Pozri [Prometheus](docs/12-observability/prometheus.md).

## PowerShell provider

Abstraction layer sprístupňujúca datasources ako filesystem, registry, certificates alebo environment cez jednotné cmdlets a drives. Pozri [PowerShell fundamentals](docs/03-git-and-automation/powershell-fundamentals.md).

## Practical evidence inventory — SOA-C03

Versionovaný zoznam dokončených labov, fault drills, CLI/API evidence, pozitívnych a forbidden-outcome tests pre jednotlivé exam domains a capability boundaries. Pozri [AWS Certified CloudOps Engineer – Associate](docs/11-cloud-and-aws/cloudops-engineer-associate-soa-c03.md).

## Pre-authentication — Kerberos

Mechanizmus, ktorým client pred vydaním TGT preukazuje kontrolu nad long-term credentialom alebo iným initial authentication factorom. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Pre/post-NAT flow identity

Rozlíšenie packet tuple pred Service/NAT translation a po nej; NetworkPolicy alebo firewall enforcement môže pozorovať iba jednu z týchto identít. Pozri [CNI a NetworkPolicy](../docs/09-kubernetes/cni-networkpolicy.md).

## Pre-release identifier

SemVer časť za pomlčkou, napríklad `rc.1`, označujúca verziu s nižšou precedence než zodpovedajúci final release. Pozri [Semantic Versioning](docs/05-ci-cd-and-release/semantic-versioning.md).

## Predictive scaling

Elasticity model pripravujúci capacity pred očakávaným demand-om na základe historických vzorov alebo forecastu. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Preemption — Kubernetes scheduling

Mechanizmus, pri ktorom scheduler môže iniciovať odstránenie nižšie prioritných Podov, aby vytvoril priestor pre unschedulable Pod s vyššou prioritou. Pozri [Scheduling](docs/09-kubernetes/scheduling.md).

## Preemption recovery subject

Pending high-priority Pod, candidate Node, victim inventory, termination state a post-victim feasibility, ktoré určujú, či preemption môže vytvoriť validný placement. Pozri [Scheduling](../docs/09-kubernetes/scheduling.md).

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

## Principal-mapping generation

Versionované pravidlá mapujúce federovaný issuer/subject a claims na local application, cloud alebo Kubernetes principal. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

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

## Privilege-dimension inventory

Explicitný inventory action, resource, data, environment, tenant, time, delegation, session-assurance a operation-budget scope-u jedného entitlementu. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## Privilege-removal closure

Dôkaz, že source assignment, nested paths, active sessions, tokens, delegated workloads a alternate identities už neposkytujú odstránenú capability. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## Privilege subject

Exact principal, business task, entitlement generation, activation/session, action/resource/data/time scope, maximum envelope a validation set analyzovaného privilege-u. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## Privileged container

Container s výrazne rozšírenými capabilities, devices a oslabenými security profiles. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Privileged container — Kubernetes

Container spustený s veľmi širokým host kernel, device a security-control prístupom; podľa mounts a namespaces môže byť prakticky host-root-equivalentný. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## Privileged exception subject

Exact namespace/workload/image/owner/capability/Node/RBAC/expiry contract povoľujúci authority nad štandardný Pod Security profil. Pozri [SecurityContext a Pod Security](../docs/09-kubernetes/securitycontext-pod-security.md).

## Privileged namespace exception

Auditovaná namespace výnimka povoľujúca systémovým workloadom širšie Pod privileges, s obmedzeným RBAC, ownerom, scope-om a expiry. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## Privileged-policy collapse

Runtime configuration, pri ktorej privileged mode alebo broad authority zruší významnú časť očakávanej container boundary. Pozri [Namespaces, cgroups a capabilities](docs/08-container-fundamentals-and-docker/namespaces-cgroups-capabilities.md).

## Probe attempt sequence

Časovo zoradená množina probe pokusov vrátane handlera, pathu, latency, timeoutu, success/failure a threshold state-u pre jeden container generation. Pozri [Probes](../docs/09-kubernetes/probes.md).

## Probe control signal

Startup, liveness alebo readiness observation, ktorej výsledok spúšťa konkrétnu kubelet alebo routing action a preto musí zodpovedať failure mechanizmu, ktorý táto action dokáže ovplyvniť. Pozri [Pod](docs/09-kubernetes/pod.md).

## Probe evidence-preservation boundary

Logs, previous-container output, Pod/EndpointSlice YAML, kubelet Events, metrics a traces, ktoré sa musia zachovať pred restartom alebo zmenou probe policy. Pozri [Probes](../docs/09-kubernetes/probes.md).

## Probe execution subject

Konkrétny kubelet, Node, Pod UID, container ID, probe type, handler a timing generation vykonávajúce jeden health attempt. Pozri [Probes](../docs/09-kubernetes/probes.md).

## Probe generation

Versionovaná startup/liveness/readiness konfigurácia vrátane handlera, port/pathu, timing fields, thresholds a termination semantics viazaná na Pod template generation. Pozri [Probes](../docs/09-kubernetes/probes.md).

## Probe hysteresis

Stavový mechanizmus, ktorý z viacerých success/failure attempts a thresholdov vytvorí finálny startup, liveness alebo readiness verdict namiesto reakcie na jediný sample. Pozri [Probes](../docs/09-kubernetes/probes.md).

## Probe-level termination grace

`terminationGracePeriodSeconds` nastavené na startup alebo liveness probe pre špecifický grace period pri probe-triggered container termination. Pozri [Probes](docs/09-kubernetes/probes.md).

## Probe threshold

`failureThreshold` alebo `successThreshold` určujúci počet po sebe idúcich výsledkov potrebných na zmenu probe state-u alebo failure action. Pozri [Probes](docs/09-kubernetes/probes.md).

## Probe timeout

Maximum času jedného probe pokusu určené `timeoutSeconds`; príliš krátka hodnota môže pri load-e alebo CPU throttlingu vytvárať false failures. Pozri [Probes](docs/09-kubernetes/probes.md).

## Process

Bežiaca inštancia programu s adresným priestorom, file descriptormi, credentials a ďalším kernel stavom. Pozri [Procesy, thready, PID a signals](docs/01-linux-and-systems/processes-threads-pid-signals.md).

## Process-loaded AWS credential

Credential generation načítaná application procesom, ktorá sa môže líšiť od najnovšieho web-identity tokenu, environmentu alebo metadata credentialu dostupného na hoste. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## Process-loaded configuration

Effective config alebo secret epoch, ktorú application process skutočne načítal a používa, odlíšená od source ConfigMap/Secret objectu alebo mounted bytes. Pozri [Pod](docs/09-kubernetes/pod.md).

## Process-loaded configuration epoch

Application-reported generation configuration alebo credentialu, ktorú process parsoval a aktívne používa pre nové operations alebo connections. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Process-loaded token generation

Token instance, ktorú application process reálne používa; môže byť staršia než aktuálny token v projected volume. Pozri [ServiceAccount](../docs/09-kubernetes/serviceaccount.md).

## Process readiness boundary

Prechod medzi spusteným processom a schopnosťou bezpečne prijímať traffic alebo vykonávať workload. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Processor-order contract

Semantics určujúca poradie Collector processors, pretože enrichment, overwrite, filtering, redaction, sampling a routing môžu pri inom poradí vytvoriť odlišný effective signal. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Processor-order contract — OpenTelemetry

Versionované poradie identity normalization, redaction, cardinality control, sampling/filtering, batching a exportu určujúce final telemetry outcome. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Producer cost attribution — observability

Priradenie ingestion, active-identity, storage, query a retention costu konkrétnemu service, teamu, tenantovi a instrumentation generation. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Product-generation identity — document search

Explicitná Elasticsearch alebo OpenSearch product/version a deployment generation, ktorá určuje podporované API, mapping, lifecycle, security a recovery semantics. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Production-derived test data

Testovacie dáta odvodené z produkcie, ktoré vyžadujú data minimization, anonymizáciu, access control a retention policy. Pozri [Flaky tests a test data](docs/04-testing-and-quality/flaky-tests-and-test-data.md).

## Production validation

Overenie technického, funkčného a business výsledku zmeny v skutočnom produkčnom kontexte po deploymente alebo počas kontrolovaného rollout-u. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Profile maturity boundary

Explicitný status OpenTelemetry Profiles specification, SDK/agent a backend supportu, ktorý musí byť overený pred production závislosťou na profile signale. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Profile — observability

Telemetry signal zobrazujúci, kde application trávi CPU time, alokuje memory alebo čaká, používaný na performance diagnostiku. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Profile — performance profile

Vzorka alebo agregácia stackov ukazujúca, kde proces trávi CPU čas, čaká alebo alokuje memory. Pozri [Performance a troubleshooting](docs/01-linux-and-systems/performance-and-troubleshooting.md).

## Programmed dataplane generation

Konkrétna route/config generation načítaná edge proxy, load balancer alebo inou dataplane instance. Pozri [Ingress a Gateway API](../docs/09-kubernetes/ingress-gateway-api.md).

## Progress deadline — Deployment

Časová hranica, po ktorej Deployment status označí rollout ako nepostupujúci; sama osebe nevykoná automatický rollback. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## Progressive delivery

Evidence-driven riadenie postupnej produkčnej exposure pomocou rollout stratégie, segmentácie, observability, promotion policy a recovery mechanizmov. Pozri [Progressive delivery](docs/05-ci-cd-and-release/progressive-delivery.md).

## Project collision incident

Failure, pri ktorom dve pipelines alebo environments používajú rovnaký Compose project a vzájomne recreatujú, testujú alebo mažú spoločné resources. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Project name — Compose

Stabilná identity Compose projektu ovplyvňujúca názvy a scope containers, networks, volumes a lifecycle commandov. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Project-network split

Failure, pri ktorom services s rovnakými logical names bežia v rozdielnych Compose project networks a preto nezdieľajú DNS ani connectivity boundary. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Projected configuration update

Kubelet-driven aktualizácia ConfigMap alebo Secret volume projection s eventual sync semantics; application musí podporovať reload a `subPath` mount zvyčajne aktualizáciu nedostane. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Projected-data subject — Kubernetes Pod

Väzba source ConfigMap, Secret, service-account token alebo Downward API field-u na Pod volume/environment snapshot, kubelet materialization a process consumption. Pozri [Pod](docs/09-kubernetes/pod.md).

## Projected ServiceAccount token

ServiceAccount token vložený do projected volume s explicitnou audience, expiration a kubelet rotation semantics. Pozri [ServiceAccount](docs/09-kubernetes/serviceaccount.md).

## Projection generation

Konkrétna ConfigMap/Secret content generation materializovaná kubeletom v projected volume na jednom Node-e a Pode. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Prometheus

Metrics monitoring a alerting systém založený na multidimenzionálnych time series, pull-based scrapingu, local TSDB a PromQL. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Prometheus acceptance verdict

Dôkaz, že expected targets a post-relabel series existujú, TSDB/rules používajú správnu population, controlled signal vytvorí alert a local/remote/no-data states sú rozlíšené. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Prometheus HA

Model viacerých nezávislých Prometheus replicas, ktoré samostatne scrape-ujú, ukladajú a vyhodnocujú rules; downstream vrstva musí riešiť deduplication. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Prometheus subject

Versionovaný metrics evidence subject zahŕňajúci producer/release, discovery a scrape config, target, post-relabel labels, Prometheus replica, TSDB, rule generation, remote-write generation a query window. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Promotable artifact

Immutable artifact, ktorého identity, evidence, configuration compatibility a recovery preconditions spĺňajú promotion policy pre ďalší environment. Pozri [Continuous Delivery](docs/05-ci-cd-and-release/continuous-delivery.md).

## Promoted trace attribute

Span attribute vybraný na indexovanie, metrics generation alebo ďalšie zrýchlené query spracovanie, čím získava samostatný cardinality a cost dopad. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Promotion authority — database

Riadené rozhodnutie, ktorá replica/Region/topology sa stáva jediným accepted writerom po failover/DR, vrátane fencing, endpoint cutover a failback reconciliation. Pozri [Amazon RDS](docs/11-cloud-and-aws/rds.md).

## Promotion evidence

Súbor výsledkov a metadata viazaných na konkrétny artifact alebo release manifest digest, ktoré odôvodňujú jeho postup do ďalšieho environmentu. Pozri [Environment a promotion](docs/05-ci-cd-and-release/environment-and-promotion.md).

## Promotion subject

Kompletný deployment tuple hodnotený pred promotion, typicky release manifest, rendered configuration, infrastructure revision, target environment a relevantný shared-state snapshot. Pozri [Environment a promotion](docs/05-ci-cd-and-release/environment-and-promotion.md).

## PromQL

Prometheus Query Language na selection, aggregation a výpočty nad time series. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Propagation generation — tracing

Versionovaný inject/extract a async/message context contract vytvárajúci parent, child a link relationships expected span graphu. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Protected branch — GitLab

Branch s policy obmedzujúcou push, merge, force push, deletion a podľa konfigurácie Code Owner alebo approval behavior. Pozri [Protected branches a environments](docs/06-gitlab/protected-branches-and-environments.md).

## Protected environment

Environment s obmedzenou deployment identitou, approval alebo policy pravidlami a auditom, používaný najmä pre produkciu a citlivé stages. Pozri [Continuous Delivery](docs/05-ci-cd-and-release/continuous-delivery.md).

## Protected environment — GitLab

GitLab environment s obmedzeným allowed-to-deploy alebo approval modelom pre citlivé runtime targety, napríklad production. Pozri [Protected branches a environments](docs/06-gitlab/protected-branches-and-environments.md).

## Protected-resource generation — AWS Backup

Exact source resource ARN/configuration/data generation, ktorá má byť vybraná effective backup assignmentom a zachytená konkrétnym jobom. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Protected-value subject — AWS

Versionovaná identita business value alebo credentialu, KMS key/materialu, secret version/stage, target credentialu, consumer-loaded state-u a required business outcome-u použitá pri encryption a secret lifecycle reasoning. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Protected variable — GitLab

CI/CD variable sprístupnená iba pipeline contextom na protected refs podľa GitLab trust pravidiel; stále vyžaduje bezpečný runner a pipeline kód. Pozri [Protected branches a environments](docs/06-gitlab/protected-branches-and-environments.md).

## Provenance attestation

Signed statement viažuci artifact na builder, source revision, build type a inputs podľa definovaného provenance predicate-u. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Provider alias — Terraform

Pomenovanie alternatívnej konfigurácie rovnakého providera používané napríklad pre inú region, account alebo endpoint boundary. Pozri [Terraform providers, resources a data sources](docs/07-infrastructure-as-code-and-configuration-management/terraform-providers-resources-data-sources.md).

## Provider configuration — Terraform

Runtime nastavenie providera, napríklad region, endpoint alebo authentication context, ktoré resource alebo module používa na API operácie. Pozri [Terraform providers, resources a data sources](docs/07-infrastructure-as-code-and-configuration-management/terraform-providers-resources-data-sources.md).

## Provider–consumer contract — CI/CD

Versionovaný behaviorálny contract medzi providerom reusable capability a consumerom. Definuje input/output schema, resolved graph semantics, permissions, artifact a evidence identity, failure propagation, compatibility, support a migration lifecycle. Pozri [Reusable a parallel pipelines](docs/05-ci-cd-and-release/reusable-and-parallel-pipelines.md).

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

## Provider target identity — Terraform

Effective provider configuration address spolu s caller accountom, regionom, endpointom a workload identity, ktorá určuje, ktorú remote authorization a failure boundary provider API operácia zasiahne. Pozri [Terraform providers, resources a data sources](docs/07-infrastructure-as-code-and-configuration-management/terraform-providers-resources-data-sources.md).

## Provider-trigger/customer-amplifier incident

Incident, pri ktorom provider failure alebo degradation spustí udalosť, ale customer architecture, capacity, configuration alebo recovery weakness zväčší business blast radius. Pozri [Shared responsibility model](docs/11-cloud-and-aws/shared-responsibility-model.md).

## Provisioned concurrency — Lambda

Počet predinicializovaných Lambda execution environments pripravených na invocations pre konkrétnu version alebo alias s cieľom znížiť startup latency. Pozri [Lambda](docs/11-cloud-and-aws/lambda.md).

## Provisioning

Vytváranie a lifecycle správa infraštruktúrnych resources, napríklad networks, compute, databases, load balancers a IAM objektov. Pozri [Terraform vs. Ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md).

## Provisioning/configuration boundary

Explicitná hranica určujúca, ktoré resources a attributes vlastní provisioning engine a ktoré configuration-management engine. Pozri [Terraform vs. Ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md).

## Provisioning-to-configuration contract

Úzke versionované rozhranie, ktorým Terraform alebo iný resource owner publikuje stable host identities, management addresses, environment a readiness metadata pre Ansible bez sprístupnenia interného alebo citlivého state-u. Pozri [Terraform vs. Ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md).

## Proxy

Sprostredkovateľ ukončujúci jednu komunikáciu a vytvárajúci samostatnú komunikáciu k ďalšiemu endpointu. Pozri [Proxy a reverse proxy](docs/02-networking-and-web/proxy-and-reverse-proxy.md).

## PSA admission verdict

`enforce`, `audit` alebo `warn` výsledok pre exact Pod request, namespace policy level a pinned Pod Security Standards version. Pozri [SecurityContext a Pod Security](../docs/09-kubernetes/securitycontext-pod-security.md).

## PSI — Pressure Stall Information

Metriky času, počas ktorého tasks čakali pre nedostupnosť CPU, memory alebo I/O kapacity. Pozri [Memory a CPU fundamentals](docs/01-linux-and-systems/cpu-and-memory-fundamentals.md).

## PSS policy generation

Pod Security Standards level a version používané ako konkrétny admission contract pre namespace alebo cluster policy. Pozri [SecurityContext a Pod Security](../docs/09-kubernetes/securitycontext-pod-security.md).

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

## Publication exposure generation

Versionovaný stav host publications, endpoint mappings, firewall/upstream policies a intended client scope použitý na audit dostupnosti aj neplánovanej exposure. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Pull-through cache — registry

Registry cache, ktorý pri prvom pull-e načíta content z upstream a následne ho poskytuje lokálne podľa freshness policy. Pozri [Registries](docs/08-container-fundamentals-and-docker/registries.md).

## `--push` — Buildx

Build exporter skratka publikujúca image alebo multi-platform index priamo do registry. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Pushgateway

Prometheus ecosystem component na dočasné vystavenie service-level metrics short-lived batch jobov, ktoré nemôžu byť prirodzene scrape-nuté počas behu. Pozri [Prometheus](docs/12-observability/prometheus.md).

## PV asset subject

Cluster-scoped PV UID, claimRef, topology, reclaim policy a CSI volumeHandle reprezentujúce konkrétny storage asset. Pozri [Volumes, PV, PVC a StorageClass](../docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## PVC claim subject

Namespaced PVC UID, effective request, StorageClass, access/volume mode a binding state používané ako workload storage claim. Pozri [Volumes, PV, PVC a StorageClass](../docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## PVC retention policy — StatefulSet

Policy určujúca, či sa StatefulSet-created PVCs zachovajú alebo odstránia pri scale-down alebo deletion podľa podporovaného API a storage lifecycle modelu. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## QoS verdict — Kubernetes

QoS class odvodená z effective CPU/memory requests a limits relevantných containers alebo Pod-level resources; ovplyvňuje resource/eviction behavior, ale nie je SLA. Pozri [Requests, limits a QoS](../docs/09-kubernetes/requests-limits-qos.md).

## Quality gate

Automatizovaný alebo kombinovaný rozhodovací bod, ktorý vyhodnotí versionovanú policy nad konkrétnou evidence a povolí, zablokuje alebo eskaluje ďalší krok delivery. Pozri [Quality gates a approvals](docs/05-ci-cd-and-release/quality-gates-and-approvals.md).

## Quarantine capability envelope

Explicitná množina forensic, logging, backup, KMS a containment operations, ktoré musia zostať povolené aj pri silnom obmedzení kompromitovaného accountu. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Quarantine OU — AWS

Organizational unit s prísnymi incident alebo decommission guardrails určená na izoláciu member accountu pri zachovaní potrebného response a evidence accessu. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Quarantine — testing

Dočasné vyradenie nestabilného testu z blocking suite pri zachovaní pravidelného spúšťania, ownera, issue a expiry. Pozri [Flaky tests a test data](docs/04-testing-and-quality/flaky-tests-and-test-data.md).

## Querier — Loki

Component vykonávajúci LogQL subqueries nad recent ingestion state-om a historical object-storage dátami. Pozri [Loki](docs/12-observability/loki.md).

## Query expansion subject

Exact sequence DNS names vytvorená resolverom z pôvodného mena, search domains a `ndots` semantics. Pozri [Cluster DNS](../docs/09-kubernetes/cluster-dns.md).

## Query frontend — Loki

Read-path component, ktorý prijíma LogQL queries, splituje ich, aplikuje caching/limits a zlučuje výsledky. Pozri [Loki](docs/12-observability/loki.md).

## Query frontend — Tempo

Read-path component, ktorý sharduje trace lookup alebo TraceQL search na jobs, distribuuje ich queriers a zlučuje výsledky. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Query generation — Grafana

Exact data source, text, variables, time range, step/interval a execution options použité na vytvorenie jedného query resultu. Pozri [Grafana](docs/12-observability/grafana.md).

## Query scheduler — Loki

Component koordinujúci a frontujúci query work medzi query frontendmi a queriers. Pozri [Loki](docs/12-observability/loki.md).

## Query storm — Grafana

Nadmerný počet alebo objem backend queries spôsobený kombináciou panels, variables, repeats, users a krátkeho refresh intervalu. Pozri [Grafana](docs/12-observability/grafana.md).

## Question-decision subject — CloudOps

Exact practice question generation spolu s outcome, constraints, scope, plane, options, confidence, time a post-answer error evidence. Pozri [CloudOps domain review a timed reasoning](docs/11-cloud-and-aws/cloudops-domain-review-timed-reasoning.md).

## Question-error closure

Uzavretie reasoning chyby až po oprave autoritatívneho modelu a úspešnom vyriešení nového scenario variantu bez phrasing recognition. Pozri [CloudOps domain review a timed reasoning](docs/11-cloud-and-aws/cloudops-domain-review-timed-reasoning.md).

## QUIC

Transportný protokol nad UDP implementujúci reliable streams, congestion control, loss recovery a TLS 1.3 integráciu. Pozri [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md).

## Quota accounting subject

ResourceQuota UID/generation, current `hard`/`used`, exact admitted request delta, scope a allow/reject decision v jednom admission time window. Pozri [ResourceQuota a LimitRange](../docs/09-kubernetes/resourcequota-limitrange.md).

## Quota admission

API admission kontrola odmietajúca create alebo update request, ktorý by prekročil ResourceQuota hard limit alebo nesplnil required quota fields. Pozri [ResourceQuota a LimitRange](docs/09-kubernetes/resourcequota-limitrange.md).

## Quota admission verdict

Server-side rozhodnutie, či effective create/update delta prekračuje matching namespace quota; nastáva pred schedulingom a runtime execution. Pozri [ResourceQuota a LimitRange](../docs/09-kubernetes/resourcequota-limitrange.md).

## Quota recovery headroom

Časť namespace quota zámerne ponechaná pre rollout surge, Node loss, HPA burst, Job overlap a emergency repair/replacement workloads. Pozri [ResourceQuota a LimitRange](../docs/09-kubernetes/resourcequota-limitrange.md).

## Quota saturation

Stav, keď ResourceQuota `used` dosiahne alebo sa približuje k `hard`, takže nové Pody, Jobs, PVCs alebo iné objects nemôžu byť prijaté. Pozri [ResourceQuota a LimitRange](docs/09-kubernetes/resourcequota-limitrange.md).

## Range vector — PromQL

Množina time series so samples za definované časové okno, používaná napríklad ako vstup `rate()` alebo `increase()`. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Ratcheting — quality

Model, ktorý povoľuje iba zachovanie alebo zlepšenie predchádzajúceho akceptovaného quality baseline. Pozri [Code coverage a quality gates](docs/04-testing-and-quality/code-coverage-and-quality-gates.md).

## Rate-controlled fleet mutation

Fleet operation rozdelená na bounded canary/waves cez max concurrency, max errors, timeout, stop condition a application assertions tak, aby chybný command alebo selector nezmenil celý fleet naraz. Pozri [AWS Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## Rate denominator contract — RED

Definícia unit, accepted/started/completed boundary, deduplication, retries, batches, valid traffic a absent-traffic semantics používaná pre Rate a error-ratio denominator. Pozri [RED method](docs/12-observability/red-method.md).

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

Policy zakazujúca zápis do image-derived rootfs a povoľujúca iba explicitné writable paths. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Read-only root filesystem — Kubernetes

Container security setting zakazujúci zápis do image root filesystemu a vyžadujúci explicitné writable mounts pre temp, cache alebo application state. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## read replica — RDS

Asynchronously replicated readable database copy používaná na read scaling, reporting, migration alebo promotion-based recovery. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## Readable-replica freshness contract

Maximum tolerovaný replication lag a explicitný set business reads, ktoré smú používať reader endpoint/replica bez porušenia read-after-write alebo decision correctness. Pozri [Amazon RDS](docs/11-cloud-and-aws/rds.md).

## Readiness

Stav, v ktorom má workload prijímať traffic alebo prácu; process môže byť live, ale ešte nemusí byť ready. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Readiness acceptance contract — SOA-C03

Podmienky pre interný ready verdict zahŕňajúce current guide, stable simulations, domain floor, explainability, remediation high-confidence errors, practical evidence a time stability. Pozri [AWS Certified CloudOps Engineer – Associate](docs/11-cloud-and-aws/cloudops-engineer-associate-soa-c03.md).

## Readiness boundary

Prechod medzi existenciou resource a jeho spôsobilosťou vstúpiť do ďalšieho automation kroku, potvrdený condition-based observation ako bootstrap completion, stable management identity a funkčný connection path. Pozri [Terraform vs. Ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md).

## Readiness eligibility verdict

Rozhodnutie, či konkrétny Pod/container generation smie prijímať novú prácu; propaguje sa cez Pod conditions a EndpointSlice, ale nie je business SLO. Pozri [Probes](../docs/09-kubernetes/probes.md).

## Readiness gate

Pod-level custom condition, ktorá musí byť true spolu s container readiness, aby bol Pod považovaný za Ready. Pozri [Probes](docs/09-kubernetes/probes.md).

## Readiness-gate generation

Versionovaná custom Pod condition, jej controller owner, observed generation, freshness a recovery behavior používané ako ďalšia traffic-eligibility podmienka. Pozri [Probes](../docs/09-kubernetes/probes.md).

## Readiness-gate subject

Custom Pod condition contract zahŕňajúci Pod UID, gate type, owning controller, external registration generation, condition state a cleanup behavior. Pozri [Pod](docs/09-kubernetes/pod.md).

## Readiness probe

Kubelet test určujúci, či má Pod prijímať nový traffic; failure nereštartuje container, ale mení readiness a backend eligibility. Pozri [Probes](docs/09-kubernetes/probes.md).

## Readiness state machine — SOA-C03

Riadený prechod `Not mapped → Knowledge mapped → Practiced → Timed → Evidence reviewed → Ready`, kde každý stav vyžaduje explicitný evidence gate. Pozri [AWS Certified CloudOps Engineer – Associate](docs/11-cloud-and-aws/cloudops-engineer-associate-soa-c03.md).

## Ready replicas — Kubernetes

Počet replík, ktorých Pody majú aktuálne Ready condition; nevypovedá automaticky o dlhodobej availability alebo business correctness. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Real User Monitoring — RUM

Zber performance a error telemetry zo skutočných používateľských klientov a sessions s možnosťou segmentácie podľa zariadenia, browsera, regiónu alebo journey. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Realization gap — AWS operations

Rozdiel medzi successful control-plane API requestom zaznamenaným CloudTrailom a neskoršou controller/runtime/application realizáciou desired state-u, ktorú treba overiť service a business telemetry. Pozri [Amazon CloudWatch a AWS CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## Realized RPO — AWS recovery

Skutočná data-loss exposure odvodená od incident/corruption boundary, selected clean recovery generation, capture/copy gaps a unreconciled external side effects. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Realized RTO — AWS recovery

End-to-end interval od detection/decision cez access, restore, initialization, dependencies, validation, reconciliation a cutover po business acceptance. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Realized savings

Úspora reálne overená po implementácii optimization change-u, nie iba estimated recommendation. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Rebase

Operácia, ktorá replayuje commits na nový base a vytvára nové commit objects s novými IDs. Pozri [Merge a rebase](docs/03-git-and-automation/merge-and-rebase.md).

## Receiver — Alertmanager

Pomenovaná kolekcia notification integrations, napríklad webhook, email, chat alebo on-call služba. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Receiver-delivery subject

Exact receiver integration, template generation, authentication, external incident key, attempt a acknowledgement/unknown-outcome state pre jednu notification group. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Receiver — telemetry

Komponent telemetry pipeline, ktorý prijíma signals cez OTLP, scrape, logs alebo iný podporovaný protocol. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Recent-change correlation — AWS incident

Versionované prepojenie symptómu s deploymentom, policy, route, rotation, failover, patchom, automation alebo capacity transition v relevantnom time windowe. Pozri [CloudOps troubleshooting drills](docs/11-cloud-and-aws/cloudops-troubleshooting-drills.md).

## Recent-log path — Loki

Query path k neflushnutým alebo recentným entries cez live ingesters a current ring ownership. Pozri [Loki](docs/12-observability/loki.md).

## Recent-trace path

Trace query path cez Tempo live-store alebo ekvivalentný current Jaeger/storage visibility model pred alebo nezávisle od historical publication. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Reclaim policy — Kubernetes storage

PV lifecycle pravidlo `Delete` alebo `Retain` určujúce, čo sa má stať s PV a podľa drivera backing storage po uvoľnení claimu; nie je náhradou backup policy. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Recommendation-to-realization gap

Rozdiel medzi estimated savings recommendation a skutočne implemented, stable a normalized measured financial outcome. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Reconciliation

Proces porovnania a opravy rozdielov medzi dvoma reprezentáciami alebo stores, napríklad počas dual write migration. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Reconciliation hot loop

Failure stav, pri ktorom controller bez semantic progressu opakovane enqueue-uje alebo zapisuje rovnaký subject, spotrebúva CPU/API/etcd capacity a blokuje ďalšie keys. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Reconciliation key

Stabilná identity resource-u, typicky `namespace/name`, vložená do controller work queue, podľa ktorej worker načíta najnovší object state. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Reconciliation loop

Opakovaný proces observe, compare, act a report, ktorý približuje actual state Kubernetes alebo external systému k desired state-u. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Reconciliation subject

Rekonštruovateľná identita jedného control-loop rozhodnutia zahŕňajúca controller/version/leader, cluster, object UID/generation/resourceVersion, queue attempt, dependents, external bindings, credentials a reconcile ID. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Reconvergence validation — CloudOps

Overenie, že controllers, runtime processes, data state a traffic sa po recovery ustálili na authoritative generation a neoscilujú späť. Pozri [CloudOps troubleshooting drills](docs/11-cloud-and-aws/cloudops-troubleshooting-drills.md).

## Reconvergence verdict

Dôkaz, že controller, kubelet/runtime, dataplane alebo external system po repair-e dosiahli požadovanú current generation.

## Recording-rule generation

Versionovaný PromQL expression, input-series inventory, evaluation interval a output metric/label contract materializujúci derived time series. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Recording rule — Prometheus

Pravidelne vyhodnocovaná PromQL expression, ktorej výsledok sa uloží ako nová time series pre opakované alebo drahé výpočty. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Recovery acceptance verdict — AWS

Closure dôkaz, že selected recovery generation je clean a consistent, application/business invariants fungujú v RTO/RPO, old writers sú fenced a forbidden exposure/duplicate outcomes nevznikajú. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Recovery authority

Explicitný owner a state-generation contract určujúci, kto smie deklarovať disaster, vybrať recovery point, povýšiť writer-a, otvoriť traffic a vykonať failback. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Recovery closure — etcd

Verdikt po restore, ktorý potvrdzuje etcd/API/controller convergence, external/application consistency, traffic/business outcome, forbidden old-state outcomes a zaznamenané RPO/RTO. Pozri [etcd backup a restore](../docs/09-kubernetes/etcd-backup-restore.md).

## Recovery control

Control umožňujúci obnoviť službu, dáta alebo dôveryhodný stav po incidente. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Recovery eligibility

Aktuálny dôkaz, že konkrétny predchádzajúci release možno bezpečne použiť na rollback alebo inú recovery: artifacts sú dostupné a dôveryhodné, config a secrets existujú, shared data a events zostávajú kompatibilné a post-recovery validation je pripravená. Pozri [Artifact versioning](docs/05-ci-cd-and-release/artifact-versioning.md) a [Release management](docs/05-ci-cd-and-release/release-management.md).

## Recovery eligibility gate — Helm

Pre-change alebo incident-time rozhodnutie, či konkrétny rollback, roll-forward, compensation alebo restore candidate je kompatibilný s current artifacts, APIs, data, events, credentials a external systems. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Recovery fencing

Mechanizmus, ktorý zabráni corrupted alebo old production writers spracúvať nové writes/side effects počas restore, reconciliation a traffic cutoveru. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Recovery keys — Vault

Quorum material používaný pri vybraných privileged Vault operations v auto-unseal modeli; nenahrádza stratený auto-unseal key. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Recovery manifest — AWS

Immutable mapping exact database restore time/log markerov, object versions/checksums, filesystem points, artifact/schema, keys/secrets, IaC a reconciliation cursoru do jednej recoverable generation. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

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

## Recovery-point generation

Konkrétny service-specific captured state s recovery-point ARN, source identity, timestamps, vault, encryption, retention a restore metadata. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Recovery Point Objective — RPO

Maximálna tolerovaná strata dát vyjadrená časom medzi incidentom a posledným použiteľným recovery pointom. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Recovery Region — AWS

AWS Region pripravený ako cieľ cross-Region disaster recovery vrátane data, capacity, quotas, identity, KMS, networking, artifacts a runbookov. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Recovery-Region subject

Versionovaný inventár account/Region enablementu, services, quotas, capacity, artifacts, identity, KMS, networking, data recovery pointu, telemetry a traffic/failback runbooku. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## Recovery-set binding

Trusted väzba snapshotu na PKI, encryption keys, configs, infra/add-ons, application-data backups a restore runbook potrebné pre danú cluster generation. Pozri [etcd backup a restore](../docs/09-kubernetes/etcd-backup-restore.md).

## Recovery set — Kubernetes

Súbor artifacts potrebný na obnovu, zahŕňajúci etcd snapshot, PKI, encryption configuration/keys, component config, infrastructure source a application data backups. Pozri [etcd backup a restore](docs/09-kubernetes/etcd-backup-restore.md).

## Recovery-set manifest

Versionovaný inventár data checkpointov, transaction logs, IaC, artifacts, configuration, identities, KMS/PKI, DNS, external integration state, telemetry a runbookov potrebných na obnovu business capability. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Recovery subject — AWS Backup

Versionovaná identita workload data, RPO/RTO, backup plan/assignment, recovery points, copy/vault/key lineage, recovery manifest, restore target a business validation. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Recovery Time Actual — RTA

Skutočný čas od začiatku recovery procesu po obnovenie validovanej business capability, porovnávaný s cieľovým RTO. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Recovery Time Objective — RTO

Cieľový maximálny čas na obnovenie definovanej business capability po incidente vrátane detekcie, rozhodnutia, data recovery, startupu, validácie a traffic cutoveru. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Recreate deployment

Deployment stratégia, ktorá ukončí starú version fleet pred spustením a pripravenosťou novej, čo typicky vytvára downtime alebo výrazný capacity dip. Pozri [Recreate deployment](docs/05-ci-cd-and-release/recreate-deployment.md).

## Recreate exclusivity boundary

Deployment strategy boundary, pri ktorej old Pods majú zaniknúť pred vytvorením new Pods, ale application/external fencing musí samostatne preukázať, že old writer už nekoná. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## Recreate strategy — Deployment

Deployment stratégia, ktorá odstráni starú Pod population pred vytvorením novej, čím akceptuje downtime alebo minimalizuje mixed-version overlap. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## RED acceptance verdict

Dôkaz, že Rate, Errors a Duration používajú konzistentné logical-operation semantics, retry amplification je bounded, SLO sa obnovilo a forbidden duplicate alebo hidden-failure outcome nevzniká. Pozri [RED method](docs/12-observability/red-method.md).

## RED method

Service-oriented monitoring metodika sledujúca Rate, Errors a Duration pre každú relevantnú operation. Pozri [RED method](docs/12-observability/red-method.md).

## RED subject

Exact logical operation, measurement/completion boundaries, release, RED schema, time window a bounded cohort, pre ktorý sa Rate, Errors a Duration vyhodnocujú. Pozri [RED method](docs/12-observability/red-method.md).

## Redacted effective configuration manifest

Evidence názvov fields, source provenance, epochs a hashes bez plaintext secrets, ktorá vysvetľuje container create a process-loaded configuration. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Redirect URI

Pre-registered client endpoint, na ktorý authorization server vracia browser authorization response. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## ReDoS — Regular Expression Denial of Service

Denial-of-service riziko spôsobené regexom s patologickou runtime complexity nad útočníkom kontrolovaným vstupom. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## ReferenceGrant

Gateway API object vytvorený v namespace referencovaného resource-u, ktorý explicitne povoľuje vybraným Routes z iného namespace cross-namespace reference. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## ReferenceGrant trust subject

Provider-owned cross-namespace permission identifikujúca source group/kind/namespace a target group/kind/name. Pozri [Ingress a Gateway API](../docs/09-kubernetes/ingress-gateway-api.md).

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

## Regional NAT Gateway subject

Logical multi-AZ NAT Gateway generation s AZ coverage, per-AZ addresses/EIPs, auto-provision alebo explicit coverage policy, routes a operational evidence. Pozri [Internet Gateway a NAT Gateway](docs/11-cloud-and-aws/internet-gateway-nat-gateway.md).

## Regional resource — AWS

Resource s identity a lifecycle scope-om v konkrétnom AWS Regione, napríklad VPC alebo väčšina managed service deployments. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## Registered variable — Ansible

Host-scoped variable vytvorená cez `register`, ktorá uchováva štruktúrovaný result konkrétneho tasku pre ďalšie conditions, loops alebo reporting. Pozri [Variables, facts a templates](docs/07-infrastructure-as-code-and-configuration-management/variables-facts-templates.md).

## Registry mirror

Alternatívny registry endpoint replikujúci alebo cacheujúci content pre availability, latency alebo air-gap účely. Pozri [Registries](docs/08-container-fundamentals-and-docker/registries.md).

## Registry publication subject

Identita publication zahŕňajúca producer, registry/repository, index/platform manifests, reachable blobs, evidence, tags, policy a read-back generation. Pozri [Registries](docs/08-container-fundamentals-and-docker/registries.md).

## Registry publication subject — GitLab

Presná identity publish rozhodnutia zahŕňajúca source/candidate SHA, resolved pipeline config, build jobs a attempts, artifact a platform digests, runner/toolchain provenance, version, SBOM/scan/signature evidence, publisher identity, namespace a release policy. Pozri [Container a package registry](docs/06-gitlab/container-and-package-registry.md).

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

## Release compensation — Helm

Cielená nápravná operácia nad external alebo durable side effectom, ktorý sa nedá vrátiť historickým rendered manifestom, napríklad duplicate message, API registration, authorization alebo DNS/IAM zmena. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Release evidence — Helm

Súbor dôkazov zahŕňajúci release history, status, values, rendered manifest, hooks, artifact identity a live Kubernetes stav. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Release history retention — Helm

Policy určujúca počet a dobu uchovania Helm revisions s trade-offom medzi rollback targets, forensic evidence, Secret exposure a etcd storage. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Release inventory — ring

Auditovateľné mapovanie ring ID a membership revision na member/workload inventory, release manifest, rendered config, exposure state, observation verdict, support ownership a recovery eligibility. Pozri [Ring deployment](docs/05-ci-cd-and-release/ring-deployment.md).

## Release management

Disciplína riadenia release identity, readiness, approvals, communication, rollout, recovery a support lifecycle od pripraveného artifactu po používateľsky dostupnú zmenu. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Release manifest

Immutable manifest spájajúci digests viacerých component artifacts, migration bundle, config schema a evidence references do jednej release identity. Pozri [Trigger, artifact a cache](docs/05-ci-cd-and-release/trigger-artifact-cache.md).

## Release manifest — GitLab

Immutable alebo versionované mapovanie pomenovaného release-u na component digests/package checksums, config, infrastructure a schema revisions, security evidence a support metadata. Pozri [Environments, deployments a releases](docs/06-gitlab/environments-deployments-releases.md).

## Release mutation boundary — Helm

Hranica, na ktorej Helm mení viac Kubernetes objektov a hooks bez garancie jednej atomickej transakcie alebo automatického zvrátenia durable side effects. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Release notes

Kurátorovaná komunikácia konkrétneho release pre používateľov, administrátorov, integrátorov alebo support, zahŕňajúca dopad, breaking changes, migráciu a known issues. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Release record

Auditovateľný záznam spájajúci release version, artifacts, source, config, migrations, evidence, approvals, rollout a výsledok. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Release/runtime evidence boundary — Helm

Rozdiel medzi Helm-stored revision, values, manifestom a hook inventory na jednej strane a live object, process-loaded configuration, serving cohort a business outcome evidence na druhej strane. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Release state machine

Auditovateľný lifecycle immutable release unit od draftu a candidate assembly cez evidence, eligibility, deployment, exposure a validation po support, closure, deprecation, revocation alebo end of life. Každý transition má subject, preconditions, evidence a ownera. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Release train

Cadence model, v ktorom zmeny pripravené do definovaného cutoffu vstúpia do spoločného release termínu a ostatné čakajú na ďalší vlak. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Release transition closure — Helm

Konečný verdict upgrade/recovery, ktorý viaže final Helm revision na live Kubernetes generations, durable data/contracts, business acceptance, forbidden outcomes a retirement starej alebo nekompatibilnej generation. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Release unit

Presne definovaná množina artifactov, configov, migrations alebo koordinovaných komponentov, ktoré sa schvaľujú a release-ujú ako jeden celok. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Reliability pillar

Well-Architected pillar zameraný na správne a konzistentné fungovanie workloadu, capacity, change a failure management. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Relying Party

OIDC client, ktorý dôveruje validovanému ID Token-u od OpenID Providera a vytvára vlastnú application session. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md).

## Remediation execution subject

Exact alarm/event generation, target manifest, automation/runbook version, execution role, deduplication/cooldown, mutation, controller transition, postcondition, rollback a business validation jednej automated remediation. Pozri [Amazon CloudWatch a AWS CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

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

## Render generation — Helm

Konkrétny výpočet chartu, dependency graphu, effective values, release contextu, capabilities, Helm engine-u a voliteľných dynamic inputs na rendered manifest. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Rendered configuration digest

Content-derived identity výslednej environment configuration po templates, overlays, defaults a non-secret inputs, používaná na väzbu promotion, approval a deployment recordu. Pozri [Environment a promotion](docs/05-ci-cd-and-release/environment-and-promotion.md).

## Rendered-field identity — Helm

Konkrétny Kubernetes resource path a value generation, ku ktorej sa viaže values-to-template transform a runtime dôsledok. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Rendered hook inventory

Complete set hook resources vyrenderovaných z parent chartu aj enabled dependencies vrátane lifecycle points, weights, names, images, RBAC, arguments, timeouts, operation IDs a cleanup policies. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Rendered-manifest digest

Hash alebo iná immutable identity final rendered manifest setu používaná na koreláciu source inputs, Helm revision a live deployment evidence. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Rendered manifest — Helm

Výsledný Kubernetes YAML vytvorený kombináciou chart templates, effective values, release contextu a capabilities pred aplikovaním na API server. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Rendered-value verdict — Grafana

Rozhodnutie, či panel display zachováva numeric a categorical semantics raw backend value-u po transformations, units, mappings a overrides. Pozri [Grafana](docs/12-observability/grafana.md).

## Repair-versus-restore verdict

Rozhodnutie, či incident pri zachovanom quorum a healthy state-e riešiť member/network/disk/TLS opravou alebo vykonať destructive cluster-state rollback zo snapshotu. Pozri [etcd backup a restore](../docs/09-kubernetes/etcd-backup-restore.md).

## Repeat interval

Interval opakovania Alertmanager notification pre nezmenenú group, ktorá zostáva firing. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Repeating panel — Grafana

Panel alebo row dynamicky duplikovaný pre každú vybranú variable value; pri veľkom scope-e môže vytvoriť query storm. Pozri [Grafana](docs/12-observability/grafana.md).

## `replace_triggered_by` — Terraform

Lifecycle rule vyžadujúca replacement resource, keď sa zmení referencovaný managed objekt alebo atribút predstavujúci explicitný lifecycle signal. Pozri [Lifecycle, import a moved blocks](docs/07-infrastructure-as-code-and-configuration-management/lifecycle-import-moved-blocks.md).

## Replacement feasibility

Dôkaz, že current placement contract zostane splniteľný po Node loss, rollout surge, HPA scale-up alebo Pod replacement-e, nie iba pre už bežiacu cohortu. Pozri [Taints, tolerations, affinity a topology](../docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Replacement-loop subject — ASG

Opakovaný chain `launch → bootstrap/health failure → terminate → replacement`, identifikovaný exact launch generation, target-health reason, grace/warmup a scaling activity evidence. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Replacement persistence proof

Dôkaz, že replacement container pripojil rovnaký expected persistent data subject a pokračuje bez neplánovanej initialization alebo data loss. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## Replacement Pod

Nový Pod object vytvorený controllerom ako náhrada zaniknutého alebo nevyhovujúceho Podu; má nový UID, IP a runtime lifecycle aj pri podobnom mene alebo template. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Replay duplicate — Fluent Bit

Druhá alebo ďalšia backend kópia toho istého source eventu vytvorená rereadom, timeout retry, position-state stratou alebo multi-reader fan-outom. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Replay identity — batch

Explicitná identita operátorského alebo recovery replay-u viazaná na pôvodný logical run bez kolízie so scheduled runom. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Replay manifest — Lambda

Schválený súbor source event identity, pôvodnej delivery/function generation, attempt history, failure class, idempotency key, current business state, replay version, rate limitu a post-replay validation. Pozri [AWS Lambda](docs/11-cloud-and-aws/lambda.md).

## Replica-set acceptance verdict

Dôkaz, že ReplicaSet vlastní presný desired Pod inventory, všetky Pods sú template-equivalentné a Ready/Available, Service vyberá správne UIDs a next reconcile je no-op. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Replica shard

Kópia primary shardu poskytujúca redundancy a read capacity, ale nie ochranu pred logical corruption alebo deletion. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## ReplicaSet

Kubernetes workload controller udržiavajúci požadovaný počet matching zameniteľných Podov. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## ReplicaSet reconciliation subject

Identita ReplicaSet control-loop rozhodnutia zahŕňajúca ReplicaSet UID/generation, desired replicas, selector, template hash, matching Pod UID inventory, ownerReferences, lifecycle classes a higher-level owner. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Replication acceptance — S3

Dôkaz, že exact eligible object version bola úspešne prenesená do intended destination podľa replication rule, IAM/KMS a status contractu; source PUT success ho nenahrádza. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Replication generation — registry

Versionovaný stav synchronizácie replica/mirror určujúci prijaté manifests, blobs, tags, deletes a referrers. Pozri [Registries](docs/08-container-fundamentals-and-docker/registries.md).

## replication lag — RDS

Časový alebo log-position rozdiel medzi source database a asynchronously applying read replica, ktorý určuje stale-read a recovery exposure. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## Report artifact — GitLab

Machine-readable job artifact v podporovanej schéme, ktorý GitLab interpretuje pre test, coverage, code-quality, dotenv, SBOM alebo security výsledky. Pozri [Artifacts a cache](docs/06-gitlab/artifacts-and-cache.md).

## Representation isolation

Požiadavka, aby viewer requests s rozdielnou tenant/user/language alebo inou content-changing identity nemohli zdieľať nesprávnu cached response. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

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

## Reserve/permit subject — Kubernetes scheduling

Dočasný scheduler state medzi výberom Node-u a bindingom vrátane resource reservation, permit decision a prípadného `Unreserve` rollbacku. Pozri [Scheduling](../docs/09-kubernetes/scheduling.md).

## Reserved concurrency — Lambda

Per-function limit, ktorý rezervuje časť regional concurrency poolu a zároveň určuje maximálny počet concurrent invocations danej funkcie. Pozri [Lambda](docs/11-cloud-and-aws/lambda.md).

## Residual risk

Risk zostávajúci po aplikovaní mitigations a controls, ktorý musí mať explicitného ownera, acceptance decision a review trigger. Pozri [Threat modeling](docs/13-security-and-identity/threat-modeling.md).

## Residual-risk verdict

Explicitné rozhodnutie o zostávajúcom security risku po containment, recovery a effective-control validation vrátane ownera, duration a acceptance podmienok. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Resilience engineering

Disciplína navrhovania a zlepšovania schopnosti sociotechnického systému predvídať, absorbovať, zotaviť sa a učiť sa z porúch a variability. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Resolved alert

Alert instance, ktorej firing condition už neplatí a prešla do ukončeného stavu podľa alerting lifecycle-u. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Resolved ClusterRole rules

Effective ruleset ClusterRole-u po aplikovaní aggregation rule a všetkých matching member ClusterRoles. Pozri [RBAC](../docs/09-kubernetes/rbac.md).

## Resolved Compose model

Výsledná configuration po interpolation, merge, profiles, includes a overrides, ktorú možno kontrolovať cez `docker compose config`. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Resolved Compose model subject

Canonical effective application model po interpolation, merge, profiles, include a extends, viazaný na source inventory, Compose version a model digest. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Resolved config digest

Immutable digest effective pipeline konfigurácie po spracovaní includes, templates, inheritance, inputs, generated graphu a policy revisions. Pozri [Pipeline as Code](docs/05-ci-cd-and-release/pipeline-as-code.md).

## Resolved configuration — GitLab CI

Výsledná GitLab CI konfigurácia po načítaní a zlúčení root súboru, includes a components a po aplikovaní konfiguračných semantics. Je skutočným review a provenance subjectom pipeline, nie iba root `.gitlab-ci.yml`. Pozri [GitLab CI/CD syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md).

## Resolved configuration — GitLab CI/CD

Konečný pipeline YAML model po spracovaní includes, components, defaults, inheritance, references a rules-relevantnej konfigurácie. Pozri [GitLab CI/CD syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md).

## Resolved dependency artifact — Helm

Exact dependency chart version a digest zvolený resolverom z declaration constraintu a source repository state-u. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Resolved-model policy

Policy vyhodnocujúca effective Compose model vrátane images, ports, mounts, networks, devices, privileged settings, secrets a external resources namiesto jednotlivých fragments. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Resolved notification

Notification informujúca receiver, že predtým firing alert group alebo alert identity už nie je aktívna. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Resolved pipeline configuration

Výsledná pipeline definícia po spracovaní includes, templates, inheritance, parameters, rules a generated configu; predstavuje konfiguráciu, ktorú platforma skutočne vykoná. Pozri [Pipeline as Code](docs/05-ci-cd-and-release/pipeline-as-code.md).

## Resolved placement evidence

Evidence spájajúca admitted Pod contract, scheduler profile generation, feasible-Node set, score vector a final Pod-to-Node binding. Pozri [Scheduling](../docs/09-kubernetes/scheduling.md).

## Resolved route configuration

Controller-generated effective configuration po zlúčení Routes, listeners, references, policies, Services, EndpointSlices a certificates. Pozri [Ingress a Gateway API](../docs/09-kubernetes/ingress-gateway-api.md).

## Resolved runtime configuration — Docker

Skutočná configuration vytvoreného containeru vrátane image, commandu, environmentu, mounts, networks, limits a security options dostupná cez inspection. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Resolved target manifest — Systems Manager

Immutable zoznam concrete managed-node alebo resource identities materializovaný z selectorov v schválenom čase a viazaný hashom na change approval, document a rate-control contract. Pozri [AWS Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## ResolvedRefs condition — Gateway API

Route status condition indikujúca, či controller úspešne vyriešil backend, Secret a ďalšie references vrátane cross-namespace permission. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## Resolver-cache cohort

Množina clients alebo recursive resolvers, ktoré počas TTL/application cache lifetime používajú rovnakú DNS answer generation a preto nemusia prejsť na nový target súčasne. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Resolver forwarding loop

DNS failure, pri ktorom cluster DNS forwarduje query na Node stub resolver a ten ju pošle späť na cluster DNS, často pre nesprávny kubelet `resolvConf`. Pozri [Cluster DNS](docs/09-kubernetes/cluster-dns.md).

## Resolver-library cache subject

Application alebo runtime-level DNS cache s vlastnými TTL, negative-cache a address-selection semantics. Pozri [Cluster DNS](../docs/09-kubernetes/cluster-dns.md).

## Resource acceptance verdict

Verdikt, že admitted requests/limits, scheduler reservation, cgroup realization, runtime throttling/OOM/eviction, autoscaling a application SLO zodpovedajú reviewed contractu. Pozri [Requests, limits a QoS](../docs/09-kubernetes/requests-limits-qos.md).

## Resource address — Terraform

Jednoznačná konfiguračná adresa managed objektu vrátane module pathu, resource type/name a prípadného `count` indexu alebo `for_each` key. Pozri [Terraform providers, resources a data sources](docs/07-infrastructure-as-code-and-configuration-management/terraform-providers-resources-data-sources.md).

## Resource-analysis subject — USE

Versionovaný subject spájajúci affected service operation a cohort s exact bounded resource-om, jeho enforcement boundary, configured a loaded capacity generation, observation windowom a ownerom. Pozri [USE method](docs/12-observability/use-method.md).

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

## Resource error observation — USE

Časovo a subjectovo viazaný dôkaz explicitného resource failure-u, napríklad OOM, acquire timeout, I/O error, quota rejection alebo allocation failure. Pozri [USE method](docs/12-observability/use-method.md).

## Resource group — GitLab CI/CD

Pipeline mechanizmus serializujúci jobs, ktoré mutujú rovnaký environment alebo shared resource, aby sa zabránilo súbežným konfliktujúcim operáciám. Pozri [GitLab CI/CD syntax](docs/06-gitlab/gitlab-ci-cd-syntax.md).

## Resource inventory — USE

Systematický zoznam bounded hardware, software a cloud resources, pre ktoré sa hľadajú utilization, saturation a error signals. Pozri [USE method](docs/12-observability/use-method.md).

## Resource lifecycle engine

Automation model sledujúci identity resources a plánujúci ich create, update, replacement a destroy operácie, typicky cez dependency graph a persistentný state. Pozri [Terraform vs. Ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md).

## Resource lifecycle subject — Kubernetes

Súvislý chain od workload demand cez source/admitted resource contract, scheduling reservation a cgroup enforcement po QoS, pressure, autoscaling a business outcome. Pozri [Requests, limits a QoS](../docs/09-kubernetes/requests-limits-qos.md).

## Resource limit — Kubernetes

Deklarované runtime maximum alebo enforcement boundary resource-u, napríklad CPU quota alebo memory cgroup limit. Pozri [Requests, limits a QoS](docs/09-kubernetes/requests-limits-qos.md).

## Resource merge precedence — telemetry

Pravidlá určujúce, ktorý SDK, detector alebo processor attribute zvíťazí pri spájaní resource identity, najmä pri stable service a ephemeral instance fields. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Resource metric definition

Presný význam resource metricu vrátane subjectu, units, working-set/RSS/cache alebo usage semantics, scrape freshness, aggregation a request/limit denominatora. Pozri [Requests, limits a QoS](../docs/09-kubernetes/requests-limits-qos.md).

## Resource metrics pipeline

Cesta kubelet resource údajov cez metrics-server a `metrics.k8s.io` API ku klientom a HPA. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Resource observation matrix

Mapa evidence cez demand, source/admission, Pod calculation, scheduling reservation, cgroup, usage, failure, QoS, autoscaling a business boundaries. Pozri [Requests, limits a QoS](../docs/09-kubernetes/requests-limits-qos.md).

## Resource — OpenTelemetry

Súbor attributes identifikujúcich entitu produkujúcu telemetry, napríklad service, host, cloud resource alebo Kubernetes workload. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Resource overcommitment — Kubernetes

Stav, keď aggregate runtime potential alebo limits presahujú fyzickú kapacitu, zatiaľ čo scheduler placement vychádza z nižších requests; zvyšuje utilization aj pressure risk. Pozri [Requests, limits a QoS](docs/09-kubernetes/requests-limits-qos.md).

## Resource owner

OAuth entita schopná autorizovať access ku protected resource. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Resource-precedence generation — OpenTelemetry

Explicitné poradie environment, cloud/Kubernetes detectorov, processorov a application configu pri určovaní effective resource attributes. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Resource request — Kubernetes

Deklarované množstvo resource-u používané schedulerom na placement a platformou ako reservation alebo relative-share signal. Pozri [Requests, limits a QoS](docs/09-kubernetes/requests-limits-qos.md).

## Resource server

API alebo služba validujúca access token a presadzujúca resource-level authorization. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Resource-versus-scope identity

Rozlíšenie observed entity, napríklad service alebo Pod, od instrumentation library/componentu a jeho version, ktorý telemetry record vytvoril. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

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

## Responsibility contract — cloud service

Explicitné rozdelenie provisioning, patching, identity, data, observability, availability, recovery a decommission responsibilities medzi providera, zákazníka a shared integration boundary. Pozri [IaaS, PaaS a SaaS](docs/11-cloud-and-aws/iaas-paas-saas.md).

## Responsibility evidence

Provider a customer dôkazy potrebné na preukázanie effective controlu, napríklad AWS compliance evidence, CloudTrail request, versionovaná policy, configuration test, restore report a business synthetic. Pozri [Shared responsibility model](docs/11-cloud-and-aws/shared-responsibility-model.md).

## Responsibility RACI — cloud

Service-specific mapping controlu na provider capability, customer ownera, evidence ownera, recovery ownera a escalation boundary. Pozri [Shared responsibility model](docs/11-cloud-and-aws/shared-responsibility-model.md).

## REST

Architectural style pre distributed hypermedia systems založený na constraints ako statelessness, cacheability a uniform interface. Pozri [REST APIs a WebSockets](docs/02-networking-and-web/rest-apis-and-websockets.md).

## Restart amplification

Pozitívna failure slučka, v ktorej liveness restarty opakujú bootstrap, connection pool, cache warm-up alebo dependency load a zhoršujú pôvodný incident. Pozri [Probes](../docs/09-kubernetes/probes.md).

## Restart loop — container

Opakovaný crash a automatický restart containeru podľa restart policy alebo external controllera, ktorý potrebuje koreláciu exit code, logs, events a dependencies. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Restart storm

Séria koordinovaných alebo opakovaných container restartov vyvolaná chybnou liveness/startup probe alebo spoločnou dependency failure, ktorá môže incident ďalej zhoršiť. Pozri [Probes](docs/09-kubernetes/probes.md).

## Restore authority

Time-bound principal, role a approval scope oprávnený vybrať recovery manifest, vytvoriť resources s protected data a rozhodnúť o validation/promotion. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Restore generation — AWS

Nový resource topology vytvorený z exact recovery pointu a restore metadata s vlastnou network, identity, encryption, schema a initialization state identity. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Restore rehearsal

Pravidelný test obnovy reálneho backup artifactu v izolovanom prostredí vrátane merania RTO a application consistency validation. Pozri [etcd backup a restore](docs/09-kubernetes/etcd-backup-restore.md).

## Restore testing — AWS Backup

Policy-driven pravidelné obnovenie recovery pointu do test targetu s následnou technical a application validation. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Restore-validation contract

Explicitné technical, data, schema, business, performance, isolation a cleanup checks, ktoré musia prejsť po restore-testing alebo incident restore jobe. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Restored etcd cluster identity

Nové member a cluster metadata vytvorené snapshot restore operáciou; starý a obnovený member state sa nesmie nekontrolovane miešať. Pozri [etcd backup a restore](docs/09-kubernetes/etcd-backup-restore.md).

## Restored logical cluster

Nová etcd cluster/member identity a clean data-directory generation vytvorená zo snapshotu; nesmie sa neplánovane miešať so starým member state-om. Pozri [etcd backup a restore](../docs/09-kubernetes/etcd-backup-restore.md).

## Restricted Pod Security Standard

Najprísnejší built-in PSS profil pre bežné workloads, vyžadujúci non-root a obmedzený privilege/capability/seccomp model podľa versionovaného štandardu. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## Result-commit invariant

Pravidlo, že process môže skončiť exit code 0 až po durable result commit-e a overení business invariantov. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Retained-PVC reuse boundary

Preflight rozhodnutie, či PVC zachovaný po StatefulSet scale-down-e obsahuje správny cluster/member/data state a môže byť bezpečne použitý pri scale-up-e. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Retransmission

Opätovné odoslanie transportných dát po detekcii straty alebo nedostatočného potvrdenia. Pozri [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md).

## Retry amplification

Násobenie pôvodného workloadu, keď client, proxy a služby nezávisle retryujú rovnaké zlyhanie a vytvoria viac pokusov na jednu business operáciu. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Retry amplification loop — cloud capacity

Causal loop, v ktorom downstream saturation zvýši latency a retries, retry-inclusive metric vyžiada ďalší scale-out a nová kapacita ďalej zvyšuje pressure na rovnaký bottleneck. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Retry-amplified metric

Autoscaling signal, ktorý zahŕňa interné retries alebo duplicate events, takže dependency failure vyzerá ako nový business demand a scale-out incident zosilní. Pozri [HPA a autoscaling](../docs/09-kubernetes/hpa-autoscaling.md).

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

## Review-staleness trigger

Zmena release-u, topology, provider, SLO/RTO/RPO, incident, test failure alebo risk expiry, ktorá invaliduje affected Well-Architected answers a vyžaduje re-review. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Revision high-water mark

Najvyššia pre-incident etcd revision, ktorú mohli controllers/clients pozorovať; používa sa pri návrhu bezpečného restore revision bump-u. Pozri [etcd backup a restore](../docs/09-kubernetes/etcd-backup-restore.md).

## Revision-to-traffic lifecycle

Deployment transition od admitted Pod template revision cez ReplicaSet capacity exchange a Pod readiness po EndpointSlice cohort, Service traffic a business acceptance. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## Revocation-complete verdict — secret lifecycle

Stav rotation, v ktorom všetci oprávnení consumers používajú novú secret epoch, stará hodnota bola zrušená a nezávislý test potvrdil, že už nie je akceptovaná. Pozri [Vault](docs/07-infrastructure-as-code-and-configuration-management/vault.md).

## Revocation latency — Zero Trust

Čas od identity, posture alebo policy revocation eventu po propagáciu a ukončenie relevantných active sessions vo všetkých enforcement points. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Rewrap

Opätovné zabalenie existujúceho DEKu novým KEKom bez decryption a re-encryption celého application payloadu. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## Rightsizing

Úprava alebo odstránenie resource-u podľa reálneho utilization, performance, reliability a capacity modelu. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Ring deployment

Progressive rollout cez stabilné deployment rings s rastúcou reprezentatívnosťou alebo kritickosťou a samostatnými entry, observation a promotion podmienkami. Pozri [Ring deployment](docs/05-ci-cd-and-release/ring-deployment.md).

## Ring membership revision

Versionovaná production policy určujúca, do ktorého deployment ring-u patrí konkrétny subject. Musí byť konzistentná naprieč services, events, telemetry a support inventory. Pozri [Ring deployment](docs/05-ci-cd-and-release/ring-deployment.md).

## Risk-adaptive access

Access model meniaci allow, deny, step-up, session lifetime alebo povolené actions podľa trusted contextual risk signals. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Risk-based deployment

Rollout policy, ktorá mení exposure, observation window, human boundary alebo recovery mechanizmus podľa business criticality, blast radiusu a compatibility rizika konkrétnej zmeny. Pozri [Continuous Deployment](docs/05-ci-cd-and-release/continuous-deployment.md).

## Risk-closure lifecycle

Flow od evidence-backed failure scenario a risk decisionu cez owned improvement change, validation a residual-risk verdict po milestone a re-review. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Risk closure verdict — Well-Architected

Dôkaz, že improvement bol nasadený, intended failure scenario bol otestovaný, forbidden outcomes nevznikli a residual risk je odstránený alebo explicitne accepted. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Role-Based Access Control — RBAC

Authorization model, ktorý združuje permissions do roles a tieto roles priraďuje principals v konkrétnom scope-e. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Role consumer inventory — Ansible

Evidencia repositories, playbooks a owners používajúcich konkrétnu role/collection version, execution environment, environment scope a podporovanú upgrade path. Umožňuje bezpečnú deprecation a security remediation. Pozri [Roles a collections](docs/07-infrastructure-as-code-and-configuration-management/roles-and-collections.md).

## Role contract — Ansible

Verejné a prevádzkové rozhranie role tvorené inputs, defaults, outputs/facts, handlers, side effects, supported platforms, privileges, idempotency a upgrade behaviorom. Pozri [Roles a collections](docs/07-infrastructure-as-code-and-configuration-management/roles-and-collections.md).

## Role-contract generation

Versionovaný role design s purpose, permissions, scope, ownerom, eligibility, activation, conflicts, tests, review a retirement semantics. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

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

## Rollback compatibility matrix — Helm

Explicitné overenie historickej application/release generation voči current schema, event backlogu, external API, credential epoch, Kubernetes API a CRD storage generation pred vykonaním rollbacku. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Rollback compatibility subject

Inventory old application artifactu a current database, event, cache, config, secret, feature a external state-u potrebný na rozhodnutie, či návrat k starej Deployment template revision je bezpečný. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## Rollback credential eligibility

Verdikt, či credential požadovaný starou application/config generation ešte môže byť bezpečne použitý; je oddelený od artifact alebo configuration rollback eligibility. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Rollback — deployment

Recovery stratégia obnovujúca predchádzajúci kompatibilný artifact, konfiguráciu, traffic target alebo infraštruktúrny state. Neznamená automaticky návrat dát a external side effects. Pozri [Rollback a roll-forward](docs/05-ci-cd-and-release/rollback-and-roll-forward.md).

## Rollback digest inventory

Množina immutable registry subjects, ktoré musia zostať pullable a policy-valid počas rollback/support windowu. Pozri [Registries](docs/08-container-fundamentals-and-docker/registries.md).

## Rollback window

Obdobie, počas ktorého sa zámerne zachováva schema, configuration, artifact a operational kompatibilita potrebná na bezpečný návrat na predchádzajúcu verziu. Pozri [Rollback a roll-forward](docs/05-ci-cd-and-release/rollback-and-roll-forward.md).

## Rolling capacity exchange

Opakovaný Deployment protocol scale-up new ReplicaSetu, readiness/availability verification a bounded scale-down old ReplicaSetu podľa surge a unavailable budgetov. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## Rolling rollback

Postupné nahrádzanie chybnej novej version fleet predchádzajúcim artifactom pri zachovaní rolling update mechanizmu a jeho compatibility obmedzení. Pozri [Rolling update](docs/05-ci-cd-and-release/rolling-update.md).

## Rolling update

Deployment stratégia postupne nahrádzajúca staré instances novými pri zachovaní časti dostupnej capacity a dočasnej koexistencii versions. Pozri [Rolling update](docs/05-ci-cd-and-release/rolling-update.md).

## Rollout acceptance verdict

Dôkaz, že latest Deployment generation je observed, canonical ReplicaSet a Pod digests sú správne, capacity/availability/traffic transitions skončili a critical business aj forbidden-outcome checks prešli. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## Rollout contract

Versionovaný popis artifactu, configu, targetu, cohort, krokov, metrics, observation windows, promotion/abort policy, recovery actions a ownera progressive rollout-u. Pozri [Progressive delivery](docs/05-ci-cd-and-release/progressive-delivery.md).

## Rollout headroom — containers

Voľná compute, address, storage a target capacity potrebná na súbežné spustenie replacement cohortu, AZ failure reserve a bezpečný drain starej population počas deploymentu. Pozri [Amazon ECS a Amazon EKS](docs/11-cloud-and-aws/ecs-eks.md).

## Rollout progress verdict

Generation-bound Deployment condition a supporting evidence určujúce, či rollout postupuje, stagnuje alebo prekročil deadline; nie je automatickou recovery action. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## Rollout reconciliation loop

Controller lifecycle `observe actual multi-axis state → classify divergence → validate preconditions → apply jeden bounded transition → over effective state → vyhodnoť evidence → reconcile znovu`. Chráni pred predpokladom, že control-plane command automaticky vytvoril desired data-plane state. Pozri [Progressive delivery](docs/05-ci-cd-and-release/progressive-delivery.md).

## Rollout rollback — Deployment

Návrat Deployment Pod template-u na zachovanú staršiu revision; nevracia databázu, queues ani iný external state. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## Rollout state machine

Explicitné stavy produkčnej expozície s povolenými transitions, observation window, success criteria, abort thresholds a rollback alebo roll-forward akciami. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Rollover — search

Lifecycle operácia vytvárajúca nový write index po splnení age, size, document-count alebo shard-size conditions. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Root module — Terraform

Konfigurácia v working directory, nad ktorou sa vykonáva plan/apply; skladá child modules, vlastní environment orchestration a určuje state/backend lifecycle. Pozri [Modules](docs/07-infrastructure-as-code-and-configuration-management/modules.md).

## Rootless container

Container/runtime model bez host-root daemon identity, typicky cez user namespaces a unprivileged helpers. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Rootless Docker

Docker daemon a containers spustené bez host root identity s user-namespace a userspace mechanizmami, znižujúce niektoré host privilege riziká za cenu feature a networking obmedzení. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Rotation split-brain — secret lifecycle

Failure stav, v ktorom secret-store labels, target-valid credentials a consumer-loaded generations ukazujú na odlišné values alebo principals. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

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

## Route attachment subject

Obojstranný parent/listener decision viažuci Route generation na parentRef, allowedRoutes, hostname/protocol intersection a controller acceptance. Pozri [Ingress a Gateway API](../docs/09-kubernetes/ingress-gateway-api.md).

## Route conflict inventory

Full attached-route inventory pre overlapping hostname/path space vrátane controller conflict/precedence verdictov. Pozri [Ingress a Gateway API](../docs/09-kubernetes/ingress-gateway-api.md).

## Route origin — AWS VPC

Pôvod route, napríklad local, static alebo propagated, ktorý ovplyvňuje ownership, priority, change path a recovery evidence. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## Route parent generation

Presná parent Gateway/listener generation, ku ktorej patria Route conditions a effective attachment. Pozri [Ingress a Gateway API](../docs/09-kubernetes/ingress-gateway-api.md).

## Route-policy generation — Alertmanager

Versionovaný route tree, matcher order, inherited grouping/timing, `continue` behavior a receiver mapping načítané konkrétnym Alertmanager runtime-om. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

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

## Rule-input closure

Dôkaz, že všetky expected source series a labels pre recording alebo alerting rule existujú, sú fresh a pokrývajú správnu population. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Run Command — Systems Manager

Capability na vzdialené vykonanie versionovaného command documentu na jednom alebo viacerých managed nodes s targetingom, rate controls a per-node outputom. Pozri [Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## `runAsNonRoot`

SecurityContext guard požadujúci, aby container process nebežal s root UID; potrebuje kompatibilný image a runtime-resolvable user identity. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## Runner — CI/CD

Agent alebo execution capacity, ktorá prijme job od CI control plane a vykoná ho prostredníctvom zvoleného executora. Runner je zároveň capacity a security boundary. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## Runner execution subject — GitLab

Identity job runtime-u zahŕňajúca source a resolved config, job attempt, runner manager/pool, worker ID a image digest, executor, helper image, architecture, cache/artifact inputs, credentials, network policy a resource limits. Pozri [Runners a executors](docs/06-gitlab/runners-and-executors.md).

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

## Runtime authority generation — Kubernetes

Effective OCI/container runtime security configuration pre konkrétny Pod UID, container ID, Node a RuntimeClass generation. Pozri [SecurityContext a Pod Security](../docs/09-kubernetes/securitycontext-pod-security.md).

## Runtime bundle subject — OCI

Identita generated `rootfs` a `config.json` zahŕňajúca selected manifest, overrides, mounts, namespaces, capabilities, resources a hooks. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Runtime configuration — container

Configuration dodaná pri vytvorení containeru, napríklad environment, command, mounts, ports, resources a security options, oddelená od immutable image artifactu. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Runtime configuration subject

Identita image defaults, Compose sources, interpolation/env files, CLI overrides, mounted configs/secrets, schema, container generation a process-loaded config epoch. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Runtime dependency closure

Úplná množina executable, interpreter/linker, libraries, certificates, DNS/NSS, timezone/locale, users, writable paths a helpers potrebných vo final stage-i. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## Runtime dependency failure

Zlyhanie knižnice, dynamic linkeru, interpreteru, certificate store alebo iného runtime componentu, ktoré môže vyzerať ako chýbajúci executable napriek existencii file-u. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Runtime digest inventory — GitLab registry

Auditovateľné mapovanie requested image/package reference na resolved OCI index alebo package checksum, platform manifest digest, pull/mirror source a digest skutočne používaný aktívnym workloadom. Pozri [Container a package registry](docs/06-gitlab/container-and-package-registry.md).

## Runtime identity — release

Effective runtime subject tvorený release manifestom spolu s rendered configuration, secret references, infrastructure a IAM revision, database/event stavom, feature flags, traffic exposure a target environmentom. Pozri [Artifact versioning](docs/05-ci-cd-and-release/artifact-versioning.md).

## Runtime isolation subject

Identita process policy vrátane host/runtime, namespaces, cgroup, UID/GID mappings, capabilities, `no_new_privs`, seccomp, LSM, mounts, devices a entrypoint. Pozri [Namespaces, cgroups a capabilities](docs/08-container-fundamentals-and-docker/namespaces-cgroups-capabilities.md).

## Runtime plaintext path — Ansible Vault

Celý tok dešifrovanej secret hodnoty od password/secret source cez Ansible memory, template alebo module argument, temporary transfer a target destination až po application process, logs, callbacks a cleanup. Pozri [Vault](docs/07-infrastructure-as-code-and-configuration-management/vault.md).

## Runtime process contract — image

Vzťah effective entrypoint/command, PID 1, signals, runtime usera, workdir, health/readiness a required filesystem/dependencies. Pozri [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md).

## Runtime shim — containerd

Per-container alebo per-runtime lifecycle proces oddeľujúci container process od containerd daemon lifecycle a poskytujúci task I/O a exit-state coordination. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Runtime socket authority

Host-admin-like authority získaná accessom k container-engine socketu. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Runtime socket exposure

Sprístupnenie Engine API socketu workloadu, ktoré často umožňuje ovládať host cez privileged containers alebo mounts. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

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

## Safe capacity

Maximálny throughput alebo concurrency, pri ktorom celý critical path spĺňa latency, reliability, downstream, cost a business-correctness contract; nie iba technický limit jednej compute vrstvy. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Safe loader — YAML

Parser režim, ktorý načítava základné dátové typy bez povolenia nebezpečnej language-specific object deserializácie. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Safety state machine

Riadený lifecycle fault experimentu od prechecks cez fault activation a removal až po recovery a cleanup, pričom každý stav má povolené transitions, timeouty a safety guardrails. Pozri [Chaos testing](docs/04-testing-and-quality/chaos-testing.md).

## Same-node coexistence contract

Dôkaz, že dve DaemonSet revisions môžu na jednom Node-e súčasne bezpečne zdieľať alebo koordinovať host ports, sockets, locks, devices a host state počas surge. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

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

## Sample sufficiency — canary

Stav, keď canary krok nazbieral dostatočný počet relevantných requests, sessions alebo business outcomes, potrebné segmentové zastúpenie a observation čas primeraný failure latency. Percento trafficu samo tento stav nedokazuje. Pozri [Canary deployment](docs/05-ci-cd-and-release/canary-deployment.md).

## Sampled coverage

Množina operations alebo records zachovaných sampling policy spolu s keep/drop dôvodmi; nemusí reprezentovať úplný traffic denominator. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Sampling-policy generation

Versionovaný head/tail/remote policy contract s keep/drop rules, expected rates, trace duration, late-span a incomplete-trace behaviorom. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md) a [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Sampling — telemetry

Výber podmnožiny traces, logs alebo profiles na kontrolu volume a cost pri zachovaní relevantných failures a business operations. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Sandboxed container runtime

Runtime pridávajúci ďalšiu isolation vrstvu medzi workload a host kernel, napríklad user-space kernel alebo lightweight VM. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Sanity test

Krátka cielená kontrola konkrétnej zmeny alebo opravy. Význam sa medzi tímami líši, preto musí mať explicitný scope. Pozri [Smoke a regression tests](docs/04-testing-and-quality/smoke-and-regression-tests.md).

## SASL — LDAP

Simple Authentication and Security Layer framework používaný LDAP na podporu rôznych authentication mechanisms nad rámec simple bindu. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## SAST — Static Application Security Testing

Statická bezpečnostná analýza source, bytecode alebo intermediate representation bez spustenia celej aplikácie. Pozri [Security a infrastructure tests](docs/04-testing-and-quality/security-and-infrastructure-tests.md).

## Saturation

Stav, keď resource nestačí okamžite obslúžiť všetku prácu a vzniká queueing alebo throttling. Pozri [Performance a troubleshooting](docs/01-linux-and-systems/performance-and-troubleshooting.md).

## Saturation observation — USE

Dôkaz práce, ktorú resource nevie okamžite obslúžiť, napríklad queue length, wait time, throttling, blocked tasks, drops alebo rejection. Pozri [USE method](docs/12-observability/use-method.md).

## Saturation-resource contract

Výber exact critical resource-u alebo queue, jeho effective capacity denominatora, wait/rejection signalu a leading thresholdu pre konkrétny Golden-Signal subject. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Saturation — USE

Množstvo práce, ktoré resource nedokáže okamžite obslúžiť a prejavuje sa queueingom, wait time, throttlingom alebo rejection. Pozri [USE method](docs/12-observability/use-method.md).

## Saved plan subject — Terraform

Konkrétny plan artifact a digest viazaný na configuration, resolved dependencies, effective inputs, state lineage/serial, refresh observations, provider versions, target identity a policy/approval verdict. Pozri [Infrastructure as Code principles](docs/07-infrastructure-as-code-and-configuration-management/infrastructure-as-code-principles.md).

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

## Scale-field ownership

Explicitné určenie, ktorý controller smie zapisovať live replica count a ako GitOps/HPA bootstrap a runtime desired state spolupracujú bez reconciliation fightu. Pozri [HPA a autoscaling](../docs/09-kubernetes/hpa-autoscaling.md).

## Scale-in drain contract

Sekvencia odstránenia resource-u z nového trafficu, dokončenia alebo odovzdania práce, business commit-u, evidence a až následnej termination. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Scale-out downstream envelope

Maximum fleet concurrency, connections, requests alebo work claims, ktoré downstream database, queue, partner alebo network path bezpečne absorbuje počas scale-out-u. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Scale subresource — Kubernetes

Štandardizované API rozhranie vystavujúce desired a current replica informácie škálovateľného workloadu pre HPA a ďalších clients. Pozri [HPA a autoscaling](docs/09-kubernetes/hpa-autoscaling.md).

## scaling activity — Auto Scaling

Auditovateľný záznam Auto Scaling launch, terminate alebo capacity-change pokusu vrátane statusu a failure reasonu. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## scaling policy — Auto Scaling

Policy meniaca desired capacity Auto Scaling Groupu podľa target tracking, step, schedule, prediction alebo iného demand contractu. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Scaling saturation verdict

Stav, keď HPA dosiahlo max/rate/capacity boundary a ďalší demand už nevie premeniť na serving capacity; vyžaduje load shedding, alert alebo remediation. Pozri [HPA a autoscaling](../docs/09-kubernetes/hpa-autoscaling.md).

## Scaling signal contract

Definícia metric source-u, pracovnej jednotky, dimensions, aggregation windowu, freshness, no-data behavioru a očakávanej reakcie na zmenu kapacity. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## `ScheduleAnyway` — topology spread

Soft topology spread behavior, pri ktorom scheduler môže Pod umiestniť aj pri porušení ideálneho skew a používa constraint pri scoring-u. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Scheduled-run identity

Jednoznačná identita CronJob schedule instance, typicky UTC timestamp alebo business interval spolu s CronJob UID/generation a logical run key. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Scheduler assignment subject

Identita scheduling rozhodnutia zahŕňajúca Pod UID/spec, schedulerName/profile/leader, queue attempt, Node inventory, requests/constraints, plugin verdicts a binding outcome. Pozri [Kubernetes architecture](docs/09-kubernetes/kubernetes-architecture.md).

## Scheduler capability subject

Versionovaný stav scheduling capability zahŕňajúci active leader, profiles/plugins, pending a unschedulable queues, API connectivity, Node/PVC inventory a binding tests. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## Scheduler profile

Konfigurácia kube-scheduleru s vlastným `schedulerName`, aktívnymi Scheduling Framework plugins, weights a plugin arguments. Pozri [Scheduling](docs/09-kubernetes/scheduling.md).

## Scheduler profile generation

Versionovaná kube-scheduler konfigurácia určujúca active plugins, weights, added affinity a ďalšie resolved placement semantics pre daný `schedulerName`. Pozri [Scheduling](../docs/09-kubernetes/scheduling.md).

## Scheduler reservation subject

Node allocatable a súčet admitted Pod requests/overhead rezervovaných schedulerom pre placement; nie je totožný s live usage. Pozri [Requests, limits a QoS](../docs/09-kubernetes/requests-limits-qos.md).

## Scheduler score vector

Per-Node výsledky active scoring plugins a ich váh po tom, čo hard filtering vytvoril feasible-Node set. Pozri [Scheduling](../docs/09-kubernetes/scheduling.md).

## `schedulerName`

Pod spec field určujúci scheduler zodpovedný za binding Podu; ak zodpovedajúci scheduler nebeží, Pod zostane unscheduled. Pozri [Scheduling](docs/09-kubernetes/scheduling.md).

## Scheduling acceptance verdict

Verdikt, že current Pod generation bola umiestnená podľa reviewed constraints, bezpečne realizovaná kubeletom a prijatá z pohľadu failure-domain a business availability. Pozri [Scheduling](../docs/09-kubernetes/scheduling.md).

## Scheduling Framework

Pluggable architektúra kube-scheduleru rozdeľujúca scheduling cycle na extension points ako QueueSort, Filter, Score, Reserve, Permit a Bind. Pozri [Scheduling](docs/09-kubernetes/scheduling.md).

## Scheduling lifecycle subject

Súvislý chain od Pod placement intentu cez queue/profile, filtering, scoring a binding po kubelet execution a workload acceptance. Pozri [Scheduling](../docs/09-kubernetes/scheduling.md).

## Scheduling observation matrix

Mapa exact subjects a evidence cez Pod intent, queue, profile, Node inventory, reservations, storage, filter, score, binding a execution boundaries. Pozri [Scheduling](../docs/09-kubernetes/scheduling.md).

## Scheduling queue

Interná scheduler štruktúra pre nové, backoff a unschedulable Pods čakajúce na ďalší scheduling attempt. Pozri [Scheduling](docs/09-kubernetes/scheduling.md).

## Schema compatibility

Schopnosť aktívnych application a data consumers fungovať s aktuálnou sadou tables, columns, constraints, types a indexov počas deploymentu. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Schema period — Loki

Časovo ohraničená Loki storage schema configuration používaná na forward-compatible zmenu index/storage formátu pre nové dáta. Pozri [Loki](docs/12-observability/loki.md).

## Schema quarantine — document search

Bounded storage a workflow pre documents odmietnuté pre mapping alebo validation conflict, ktoré sa nesmú nekonečne retryovať ani ticho zahodiť. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Schema URL — OpenTelemetry

Reference na semantic-convention schema používanú resource alebo instrumentation scope-om na podporu compatibility a migration. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Schema validation

Overenie dát voči deklarovaným typom, required fields a constraints. Neoveruje automaticky všetky business a runtime podmienky. Pozri [YAML, JSON a regular expressions](docs/03-git-and-automation/yaml-json-regular-expressions.md).

## Scope verdict — CloudOps question

Rozhodnutie, či je subject a požadovaný control resource-, AZ-, Region-, account-, organization- alebo multi-Region scoped. Pozri [CloudOps domain review a timed reasoning](docs/11-cloud-and-aws/cloudops-domain-review-timed-reasoning.md).

## Score closure

Uzavretie tasku po hard validation, forbidden-outcome checku a zaznamenaní partial-credit alebo penalty evidence.

## Score plugin — Kubernetes scheduler

Scheduling Framework plugin prideľujúci feasible Nodes relatívne skóre podľa soft preferencií a placement stratégie. Pozri [Scheduling](docs/09-kubernetes/scheduling.md).

## Scrape attempt — Prometheus

Jedna HTTP retrieval, exposition parsing a sample-validation operácia pre exact target a evaluation time; úspech vytvára `up=1`, nie business-health verdict. Pozri [Prometheus](docs/12-observability/prometheus.md).

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

## Search-visibility boundary

Prechod medzi acknowledged/durable document write-om a okamihom, keď refresh sprístupní document query engine-u. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Seccomp profile — container

System-call filter policy znižujúca host-kernel attack surface dostupný workloadu. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Seccomp profile — Kubernetes

Runtime syscall filter vybraný cez Pod alebo container security context, napríklad RuntimeDefault alebo Localhost. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## Second converge

Druhý automation run nad už nakonfigurovaným targetom používaný na overenie, že desired state je stabilný a nevznikajú recurring changes. Pozri [Ansible idempotencia](docs/07-infrastructure-as-code-and-configuration-management/ansible-idempotency.md).

## Second-converge evidence — Ansible

Subject-bound výsledok druhého complete runu po úspešnom convergence, ktorý porovná expected/resolved/verified hosts, unintended changes, handler transitions, external side effects a runtime invariants. Pozri [Ansible idempotencia](docs/07-infrastructure-as-code-and-configuration-management/ansible-idempotency.md).

## Second-operation verification — CloudOps

Zopakovanie controller alebo business operácie po oprave, napríklad ďalší replacement, retry, deployment, copy alebo refresh, aby sa preukázala stabilita mimo prvého manual testu. Pozri [CloudOps troubleshooting drills](docs/11-cloud-and-aws/cloudops-troubleshooting-drills.md).

## Second-reconciliation verdict — Kubernetes

Dôkaz, že ďalší controller reconcile, retry, replacement alebo failover zostane bounded a nevytvorí znovu drift, duplicate alebo chybný side effect. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Second-session revocation test

Validation, ktorá overí odstránený privilege v predtým active session aj v novo vydanej session po source a policy reconciliation. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## Second-sync test

Opakovaný identity/entitlement reconciliation cycle dokazujúci, že odstránený group, role alebo binding sa z authoritative source-u alebo stale mappingu znovu nevytvorí. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Secret

Citlivý credential alebo cryptographic material, ktorého získanie umožňuje access, impersonation, decryption, signing alebo privileged operation. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Secret access graph

Inventory priamych aj nepriamych paths k Secret plaintextu cez API verbs, Pod/Job creation, workload edits, exec/debug, node access, backups a external caches. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Secret classification

Dokumentovaný contract secretu zahŕňajúci ownera, účel, consumers, lifetime, rotation, revocation, delivery a compromise impact. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Secret encryption at rest

API server configuration šifrujúca persisted Secret payloady pred uložením do etcd; nerieši disclosure cez API, Node, Pod memory, logs alebo kompromitovanú workload identity. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Secret epoch

Version alebo generácia cieľového credentialu používaná na koordináciu publication, consumer rollout, runtime verification a revocation predchádzajúcej hodnoty. Pozri [Vault](docs/07-infrastructure-as-code-and-configuration-management/vault.md).

## Secret — Kubernetes

Namespaced API objekt pre citlivé bytes alebo strings, ktorého base64 reprezentácia nie je encryption a vyžaduje RBAC, encryption-at-rest, audit a bezpečný consumer lifecycle. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Secret lifecycle

Proces creation, storage, authorization, distribution, use, rotation, revocation a destruction secretu. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Secret lifecycle subject

Exact secret ARN, metadata/KMS generation, version IDs, staging labels, rotation workflow, target credential principals, consumer cohorts a loaded-state evidence. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Secret lifecycle subject — Ansible Vault

Riadená identita secretu zahŕňajúca logical secret ID, target system, environment, owner, consumer inventory, secret epoch, encrypted artifact, vault domain, decryption identity, runtime destinations, rotation deadline a revocation status. Pozri [Vault](docs/07-infrastructure-as-code-and-configuration-management/vault.md).

## Secret push protection — GitLab

Pre-receive alebo push-time kontrola, ktorá deteguje podporované secret patterns pred prijatím commitu a môže push zablokovať. Pozri [Security scanning](docs/06-gitlab/security-scanning.md).

## Secret recovery acceptance verdict

Closure dôkaz, že current labels, target credentials, consumer-loaded state, privileges, replicas a business authentication journey sú zosúladené a retired credentials zlyhávajú. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

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

## Security assurance verdict

Grounds for confidence založené na source/runtime read-backu, allowed a forbidden tests, audit evidence a recovery rehearsal, že security objectives konkrétnej implementácie sú splnené. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Security categorization

Určenie impact levelu straty confidentiality, integrity a availability pre konkrétny system alebo information type. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Security control

Management, operational, technical alebo physical safeguard navrhnutý na ochranu assets a zníženie security risku. Pozri [CIA triáda](docs/13-security-and-identity/cia-triad.md).

## Security evidence matrix — Kubernetes workload

Mapa source manifestu, admitted Podu, runtime configu, process identity/capabilities, kernel audit, mounts/devices, allowed operations, forbidden operations a business outcome. Pozri [SecurityContext a Pod Security](../docs/09-kubernetes/securitycontext-pod-security.md).

## Security evidence verdict — GitLab

Výsledok, ktorý odlišuje complete clean scan, findings, incomplete scanner/report inventory, invalid subject, analyzer/tool error, unsupported coverage a approved skip. Zelený job bez complete report evidence nie je clean verdict. Pozri [Security scanning](docs/06-gitlab/security-scanning.md).

## Security exception subject — container

Časovo obmedzená výnimka viazaná na exact workload/runtime, environment, bypassovaný control, risk, ownera, compensating controls a expiration. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

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

## Security scan subject — GitLab

Immutable source, resolved dependency graph, SBOM, package checksum, OCI platform digest, IaC plan alebo deployment identity, ku ktorej patria analyzer execution, report a finding evidence. Pozri [Security scanning](docs/06-gitlab/security-scanning.md).

## Security Service Edge — SSE

Cloud-delivered security service model typicky zahŕňajúci ZTNA, secure web gateway a CASB capabilities. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Security tooling account — AWS

Oddelený member account používaný ako delegated administrator a operational scope pre organization-wide security findings, detection a response tooling. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Segment — Lucene

Immutable index fragment v rámci shardu; nové documents sa sprístupňujú refreshom a segments sa neskôr zlučujú merge procesom. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Selected build target

Explicitne zvolený final, test, development, debug alebo artifact stage, ktorý je súčasťou release subjectu a publication policy. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## Selected route subject — AWS

Pre konkrétnu destination IP úplný súbor matching routes, longest-prefix/priority verdict, route origin a výsledný target ID/stav. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## Selector control boundary — ReplicaSet

Namespace-scoped label selector, ownership a adoption contract určujúci candidate Pod množinu, nad ktorou ReplicaSet počíta a reconcile-uje desired replicas. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Selector — Kubernetes

Výraz vyberajúci objects podľa labels a tvoriaci kritický contract pre controllers, Services, policy alebo CLI queries. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Selector-label helper — Helm

Named template generujúci stabilné labels použité workload selectorom aj Pod template-om; nesmie obsahovať mutable chart alebo application version metadata. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Selector overlap — ReplicaSet

Failure stav, pri ktorom selectors viacerých controllers vyberajú rovnaké Pods a vytvárajú conflicting replica alebo ownership instructions. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Selector ownership contract

Stable label/selector schema určujúca, ktoré objects controller vlastní, Service routuje alebo policy zasahuje, vrátane collision a migration pravidiel. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Selectorless Service

Service bez `spec.selector`, ktorého backend EndpointSlices spravuje operator alebo iný explicitný owner, často pre external alebo manually discovered endpoints. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## Self-grading — CKA

Hodnotenie lab úloh cez explicitné validation commands, partial-credit criteria, čas a bezpečnosť namiesto subjektívneho dojmu. Pozri [CKA timed labs](docs/10-helm-and-cka/cka-timed-labs.md).

## SELinux options — Kubernetes

SecurityContext fields nastavujúce SELinux label identity container procesu a volumes podľa host policy, runtime a storage podpory. Pozri [SecurityContext a Pod Security](docs/09-kubernetes/securitycontext-pod-security.md).

## SELinux security context

Label subjectu alebo objektu obsahujúci SELinux user, role, type a prípadne level/range. Pozri [SELinux a AppArmor](docs/01-linux-and-systems/selinux-and-apparmor.md).

## Semantic API health — Kubernetes cluster

Per-backend overenie TLS identity, API read/write/watch, etcd dependency a admission pathu; je silnejšie než TCP listener alebo process health. Pozri [Cluster installation a lifecycle](../docs/09-kubernetes/cluster-installation-lifecycle.md).

## Semantic API readiness

Readiness verdict API server instance založený na schopnosti bezpečne obsluhovať relevantné API operations a dependencies, nie iba na otvorenom TCP porte alebo živom process-e. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

## Semantic compatibility — data

Zachovanie rovnakého alebo explicitne transformovaného business významu hodnôt naprieč application a schema verziami. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Semantic-convention generation

Version a stability selection OpenTelemetry semantic conventions spolu s emitted old/new/dual schema a consumer migration contractom. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Semantic Conventions — OpenTelemetry

Štandardizované názvy a významy telemetry operations, resources, attributes, metrics a events. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Semantic conventions — telemetry

Štandardizované názvy a významy operations, resources a attributes umožňujúce interoperabilitu instrumentation a backendov. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Semantic-schema generation — OpenTelemetry

Exact semantic-convention stability, attribute names/units, schema URL a compatibility mapping používané producers, processors a consumers. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Semantic status transition

Status alebo condition update vykonaný iba pri významnej zmene observed state-u, nie pri každom retry attempt-e; chráni API/etcd pred self-trigger loops. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

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

## Serialization boundary — Helm

Prechod z Go/template objectu na YAML alebo JSON text a následne späť na parsed structure alebo final Kubernetes document. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Series churn

Rýchle vytváranie a zánik time series, ktoré zaťažuje WAL, index, compaction a remote storage aj pri nižšom počte súčasne active series. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Server-side apply — Kubernetes

Deklaratívny API update model, pri ktorom API server merge-uje intent a sleduje field ownership jednotlivých managers. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Serverless acceptance verdict

Closure dôkaz, že exact event prešiel approved source, version, identity a concurrency cestou, vytvoril jeden správny business outcome a duplicate, stale-version, wrong-source a uncontrolled-replay outcomes zostali zablokované. Pozri [AWS Lambda](docs/11-cloud-and-aws/lambda.md).

## Serverless execution subject

Versionovaná identita Lambda function, artifactu, published version/aliasu, source a event-source-mapping generation, concurrency/configuration/identity, exact eventu, downstream dependencies a business idempotency key použitá na invocation a recovery reasoning. Pozri [AWS Lambda](docs/11-cloud-and-aws/lambda.md).

## Service alias ownership

Contract určujúci, ktorá service vlastní konkrétny alias v danej Docker network a aké replica/load-distribution semantics caller očakáva. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Service contract — cloud

Dokumentovaný súbor support, availability, security, data, backup, lifecycle a responsibility podmienok konkrétnej cloud služby. Pozri [IaaS, PaaS a SaaS](docs/11-cloud-and-aws/iaas-paas-saas.md).

## Service contract generation

Versionovaný Service state zahŕňajúci type, ClusterIP/clusterIPs, selector, ports, targetPorts a traffic policies. Pozri [Service a EndpointSlice](../docs/09-kubernetes/service-endpointslice.md).

## Service control policy — SCP

AWS Organizations guardrail definujúci maximálny permissions envelope pre principals v member accounts; sám access neudeľuje a neobmedzuje management account. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Service dataplane

Node alebo network-plugin mechanizmus implementujúci Service virtual IP, backend selection a packet forwarding podľa EndpointSlices. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## Service dataplane generation

Versionovaný per-Node forwarding state implementujúci Service VIP, endpoint selection a NAT alebo ekvivalentné mapovanie. Pozri [Service a EndpointSlice](../docs/09-kubernetes/service-endpointslice.md).

## Service dataplane — Kubernetes

Node alebo cluster networking vrstva implementujúca virtual Service IP a forwarding na EndpointSlice backends, napríklad cez kube-proxy alebo alternatívny eBPF dataplane. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

## Service discovery — Prometheus

Mechanizmus dynamicky vytvárajúci potenciálne scrape targets a dočasné metadata labels z Kubernetes, cloud, Consul, DNS alebo iného source-u. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Service eligibility generation — Kubernetes

Versionovaný inventory ready Pod/endpoint UIDs vybraných Service/EndpointSlice contractom pre konkrétnu workload generation a dataplane state. Pozri [Kubernetes architecture](docs/09-kubernetes/kubernetes-architecture.md).

## Service endpoint generation — container networking

Versionovaný service-discovery inventory viažuci stable workload identities, addresses, readiness, eligibility a draining/removal state. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Service FQDN

Plné cluster-local DNS meno Service-u v tvare `<service>.<namespace>.svc.<cluster-domain>`. Pozri [Cluster DNS](docs/09-kubernetes/cluster-dns.md).

## Service graph

Derived graph caller/callee relationships a performance characteristics vytvorený zo spans; jeho úplnosť závisí od instrumentation a sampling coverage. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Service health verdict

Provider alebo platformový verdict o stave služby, ktorý musí byť korelovaný s customer configuration, runtime, data a business evidence a sám neuzatvára workload incident. Pozri [IaaS, PaaS a SaaS](docs/11-cloud-and-aws/iaas-paas-saas.md).

## Service — Kubernetes

Namespaced API contract poskytujúci stabilné meno, virtual address a port model pre dynamickú backend population reprezentovanú EndpointSlices. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## Service lifecycle subject

Úplný subject spájajúci Service UID/generation, VIP a port contract, EndpointSlice cohort, node dataplane generation, client flow, backend Pod UID a business request. Pozri [Service a EndpointSlice](../docs/09-kubernetes/service-endpointslice.md).

## Service-linked role — AWS IAM

IAM role previazaná s konkrétnou AWS službou, ktorej trust a permissions lifecycle je definovaný danou službou. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## Service-model acceptance verdict

Closure podmienka dokazujúca, že zvolený service model spĺňa required availability, security, recovery, observability, cost a portability outcomes pri správnom rozdelení responsibilities. Pozri [IaaS, PaaS a SaaS](docs/11-cloud-and-aws/iaas-paas-saas.md).

## Service-model exit subject

Inventár artifacts, data formats, identities, keys, network assumptions, telemetry, runbookov, commercial constraints a času potrebný na migráciu alebo ukončenie cloudovej služby. Pozri [IaaS, PaaS a SaaS](docs/11-cloud-and-aws/iaas-paas-saas.md).

## Service port

Port publikovaný Kubernetes Service contractom pre klientov, odlišný od backend `targetPort`. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## Service principal name — SPN

Kerberos identity služby viazaná na service class a hostname, ktorú client používa pri žiadosti o service ticket. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Service Provider — SAML

Aplikácia alebo služba dôverujúca validovaným assertions od SAML Identity Providera. Pozri [SAML](docs/13-security-and-identity/saml.md).

## Service readiness — pipeline

Stav, keď testovacia dependency nielen beží ako proces, ale dokáže spracovať relevantnú operáciu v deklarovanom deadline. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## Service responsibility matrix

Tabuľka mapujúca pre konkrétnu cloud službu provider, customer a shared responsibilities v oblastiach compute, identity, network, data, encryption, logging, patching a recovery. Pozri [Shared responsibility model](docs/11-cloud-and-aws/shared-responsibility-model.md).

## Service selector

Label selector, podľa ktorého EndpointSlice controller odvodzuje backend Pods pre selector-based Service. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## Service ticket — Kerberos

Časovo obmedzený ticket vydaný KDC pre konkrétny service principal a šifrovaný long-term key-om služby. Pozri [Kerberos](docs/13-security-and-identity/kerberos.md).

## Service-to-ReplicaSet selection drift

Rozdiel medzi Pod inventory vlastneným ReplicaSetom a Pod inventory vybraným Service selectorom, ktorý môže smerovať traffic na foreign, old alebo debug Pods. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Service troubleshooting chain

Diagnostické poradie Service selector → EndpointSlice readiness → targetPort → dataplane → Pod listen socket → application behavior. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Service virtualization

Nahradenie externého systému kontrolovaným simulátorom alebo sandboxom tak, aby bol test deterministickejší a lacnejší. Pozri [End-to-end a acceptance tests](docs/04-testing-and-quality/end-to-end-and-acceptance-tests.md).

## ServiceAccount

Namespaced non-human Kubernetes identity používaná Podmi a automation; permissions získava oddelene cez RBAC alebo inú authorization policy. Pozri [ServiceAccount](docs/09-kubernetes/serviceaccount.md).

## ServiceAccount authorization subject

Presný authorization request viažuci authenticated ServiceAccount username na verb, API group, resource, subresource, namespace a relevantnú RBAC generation. Pozri [ServiceAccount](../docs/09-kubernetes/serviceaccount.md).

## ServiceAccount object identity

ServiceAccount identifikovaný clusterom, namespace-om, menom a object UID; delete/create s rovnakým menom vytvára nový lifecycle subject. Pozri [ServiceAccount](../docs/09-kubernetes/serviceaccount.md).

## ServiceAccount token audience

Identifikátor intended recipienta tokenu, ktorý zabraňuje použitiu tokenu vydaného pre jednu službu voči inému verifierovi. Pozri [ServiceAccount](docs/09-kubernetes/serviceaccount.md).

## ServiceAccount username

Canonical authenticated identity `system:serviceaccount:<namespace>:<name>` používaná v authorization a audit logoch. Pozri [ServiceAccount](docs/09-kubernetes/serviceaccount.md).

## Serving-capacity realization

Prechod z desired replica count cez controller, scheduling, Node provisioning, image/startup/readiness a traffic propagation na Pody, ktoré reálne obsluhujú requests. Pozri [HPA a autoscaling](../docs/09-kubernetes/hpa-autoscaling.md).

## Serving-capacity realization — ASG

Prechod `desired → launched → running → bootstrapped → healthy/registered → traffic-accepting → business-capable`, ktorý odlišuje fleet count od reálnej kapacity. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Session

Dočasný authenticated context vytvorený po úspešnej authentication a používaný na ďalšie authorization decisions. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Session affinity

Load-balancing policy smerujúca klienta alebo key opakovane na rovnaký backend. Pozri [Load balancing](docs/02-networking-and-web/load-balancing.md).

## Session affinity — Service

Service behavior preferujúci rovnaký backend pre klienta podľa ClientIP a timeoutu; nie je náhradou durable session storage. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## Session-assurance state

Current authentication method, assurance level, authentication age, device/risk context, validity a revocation state dlhšie trvajúcej session. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Session binding — Zero Trust

Cryptographic alebo policy väzba session/token contextu na konkrétny device, key, client alebo communication channel s cieľom obmedziť replay ukradnutého credentialu. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Session Manager

Systems Manager capability poskytujúca IAM-authorized interactive shell alebo port-forwarding sessions bez potreby inbound SSH/RDP portu. Pozri [Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## Session revocation closure

Dôkaz, že browser sessions, access/refresh tokens, delegated grants a ďalšie artifacts odvodené z identity alebo authenticatora už verifier a resource services neprijímajú. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Severity — log

Klasifikácia operational závažnosti log recordu, napríklad DEBUG, INFO, WARN, ERROR alebo FATAL, ktorá musí odrážať význam pre konkrétnu operáciu. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## SG effective allow graph

Aditívny súbor applicable inbound/outbound Security Group rules, referenced SG membership, prefix lists a ENI associations, ktorý povoľuje nový flow na konkrétnej direction a porte. Pozri [Security Groups a Network ACLs](docs/11-cloud-and-aws/security-groups-network-acls.md).

## SG membership inventory

Aktuálny zoznam ENIs/resources reprezentovaných referencovanou Security Groupou; broad alebo zmenené membership môže rozšíriť access bez zmeny rule textu. Pozri [Security Groups a Network ACLs](docs/11-cloud-and-aws/security-groups-network-acls.md).

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

## Shard-assignment verdict

Explicitný green/yellow/red a allocation-explanation stav konkrétneho primary alebo replica shardu, nie všeobecný business-health verdict. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Shared-control closure verdict

Dôkaz, že provider capability, customer configuration, monitoring, recovery a forbidden-outcome controls spolu dosiahli požadovaný security alebo business outcome. Pozri [Shared responsibility model](docs/11-cloud-and-aws/shared-responsibility-model.md).

## Shared control — cloud

Security alebo operations control, pri ktorom provider poskytuje platform capability a zákazník ju musí správne nakonfigurovať, používať, monitorovať alebo integrovať. Pozri [Shared responsibility model](docs/11-cloud-and-aws/shared-responsibility-model.md).

## Shared-control interface

Presné rozhranie, kde provider dodáva capability a zákazník vlastní activation, configuration, identity, monitoring, evidence alebo recovery use; shared neznamená nejasného ownera. Pozri [Shared responsibility model](docs/11-cloud-and-aws/shared-responsibility-model.md).

## Shared-cost driver

Measured alebo business-agreed usage dimension, napríklad bytes, requests, vCPU-hours alebo build minutes, použitá na rozdelenie shared platform costu. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Shared-file namespace

EFS file/directory identity zdieľaná concurrent NFS clients s POSIX ownership, permission, locking a publication semantics. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Shared kernel

Model, v ktorom host a container processes používajú rovnaký kernel pri odlišných namespace views a limits. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Shared-port contract — Pod

Dohoda o listener addresses, ports, startup ordering a proxy pathoch medzi containers, ktoré zdieľajú jeden Pod network namespace. Pozri [Pod](docs/09-kubernetes/pod.md).

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

## Side-effect firewall — shadow

Defense-in-depth boundary kombinujúca least-privilege identity, network/egress policy, isolated output adapters a application shadow mode tak, aby shadow execution nemohla vykonať autoritatívne writes alebo external side effects. Pozri [Shadow deployment](docs/05-ci-cd-and-release/shadow-deployment.md).

## Sidecar container

Auxiliary container bežiaci v rovnakom Pode ako hlavná aplikácia a zdieľajúci jej placement, network a Pod lifecycle boundary. Pozri [Pod](docs/09-kubernetes/pod.md).

## Sidecar lifecycle contract

Definovaný startup, readiness, resource, failure, completion a shutdown behavior auxiliary containeru vo vzťahu k main application containerom jedného Podu. Pozri [Pod](docs/09-kubernetes/pod.md).

## Signal contract

Versionovaný význam telemetry signálu vrátane source, units/schema, labels, freshness, missing-data semantics, retention a očakávanej causal interpretácie. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Signal-contract generation — OpenTelemetry

Versionovaný expected signal, population, identity, schema, coverage, overhead, privacy a backend-consumer contract. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Signal latency

Čas medzi vznikom zmeny alebo failure a dostupnosťou dostatočne úplného signálu pre rollout či experiment decision. Pozri [Shift-right](docs/04-testing-and-quality/shift-right.md).

## Signal — observability

Typ telemetry reprezentujúci určitý pohľad na systém, napríklad metric, log, trace, event alebo profile. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Signal-population contract — alerting

Exact valid numerator, denominator, cohort, traffic guard, data authority a no-data semantics alert condition-u. Pozri [Alert design a alert fatigue](docs/12-observability/alert-design-alert-fatigue.md).

## Signal quality

Hodnotenie telemetry podľa correctness, completeness, freshness, contextu, correlation, schema stability, security, cost a ownershipu. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Signal-quality verdict

Klasifikácia telemetry ako complete/authoritative, partial, stale, sampled, missing pre pipeline failure alebo unknown coverage podľa konkrétneho use case-u. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Signal subject

Exact producer, operation, measurement boundary, release, instrumentation/schema generation, resource identity, coverage, pipeline a retention/query cut-off konkrétneho signalu. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

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

## Silent outcome failure

Operation, ktorá neprodukuje bežný explicitný transport error, ale nesplní final business contract, napríklad accepted command bez completion alebo `200` s nesprávnym resultom. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Simple Bind — LDAP

LDAP Bind mechanism používajúci identity a password; musí byť chránený TLS, pretože sám neposkytuje transport encryption. Pozri [LDAP](docs/13-security-and-identity/ldap.md).

## Single Logout — SAML

SAML protocol na koordináciu logoutu medzi IdP a SP sessions, ktorý môže zlyhať čiastočne a nepredstavuje automatickú globálnu revocation. Pozri [SAML](docs/13-security-and-identity/saml.md).

## Single-release dependency graph — Helm

Model, v ktorom parent chart a všetky enabled first-level aj transitive subcharts vytvárajú jednu release revision a spoločný upgrade/rollback failure domain. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Single-release failure domain — Helm

Spoločný install, upgrade, rollback, hook a revision blast radius parent chartu a všetkých enabled dependencies. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Single-writer storage

Storage contract povoľujúci v danom čase iba jedného active writer-a a vyžadujúci scheduling/fencing. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## Skip-and-return strategy — CKA

Time-management postup, pri ktorom kandidát preskočí úlohu bez jasnej rýchlej cesty, označí ju a vráti sa po získaní jednoduchších bodov. Pozri [CKA timed labs](docs/10-helm-and-cka/cka-timed-labs.md).

## Skip-and-return trigger

Vopred definovaná podmienka, pri ktorej kandidát zastaví neefektívnu alebo rizikovú úlohu, zachová subject/evidence/next observation a vráti sa neskôr.

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

## Snapshot evidence manifest

Metadata viažuce snapshot na source cluster/member, revision, hash, key count, size, tool version, time, encryption/PKI generation, storage location a restore-test verdict. Pozri [etcd backup a restore](../docs/09-kubernetes/etcd-backup-restore.md).

## Snapshot lease — container runtime

Referencia chrániaca unpacked content a snapshots používané pullom, buildom alebo containerom pred GC. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## Snapshot-recovery generation — document search

Exact repository, snapshot, product/version compatibility, selected indexes/system state, restore target a validation contract. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Snapshot subject — container filesystem

Runtime-specific unpacked representation verified image layers, z ktorej vzniká rootfs a per-container writable layer. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## SNAT — Source NAT

Preklad source adresy alebo portu, používaný typicky pri outbound komunikácii. Pozri [NAT](docs/02-networking-and-web/nat.md).

## SNI — Server Name Indication

TLS extension prenášajúca hostname, aby server alebo proxy vybral správny certificate a virtual host. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## SOA-C03

Aktuálny exam code AWS Certified CloudOps Engineer – Associate s piatimi doménami a váhami 22 %, 22 %, 22 %, 16 % a 18 %. Pozri [SOA-C03 guide](docs/11-cloud-and-aws/cloudops-engineer-associate-soa-c03.md).

## SOA-C03 capability contract

Versionovaný súbor role outcomes, exam domains, task statements, service scope a reasoning expectations, ktoré má kandidát pre aktuálnu AWS Certified CloudOps Engineer – Associate exam generation preukázať. Pozri [AWS Certified CloudOps Engineer – Associate](docs/11-cloud-and-aws/cloudops-engineer-associate-soa-c03.md).

## Soak test

Dlhodobý performance test hľadajúci memory leaks, resource leaks, queue growth a kumulatívne zlyhania. Pozri [Performance, load a stress tests](docs/04-testing-and-quality/performance-load-stress-tests.md).

## Socket

Kernel endpoint komunikácie sprístupnený procesu cez file descriptor. Pozri [Ports a sockets](docs/02-networking-and-web/ports-and-sockets.md).

## Socket capability mount

Mount Unix socketu alebo podobného host control endpointu, ktorého authority sa určuje server API oprávneniami, nie iba filesystem read/write flagom. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## Software Composition Analysis — SCA

Analýza application dependencies a package metadata na identifikáciu známych vulnerabilities, license information a component inventory; potrebuje reachability a runtime context pre presnejšiu prioritizáciu. Pozri [Vulnerability a patch management](docs/13-security-and-identity/vulnerability-and-patch-management.md).

## Software supply chain

Súbor ľudí, identities, source repositories, dependencies, build systems, tools, registries, release procesov a deployment controls, ktoré môžu ovplyvniť výsledný software artifact. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Source/destination check — AWS

EC2 network-interface kontrola vyžadujúca, aby instance bola source alebo destination trafficu; network appliance alebo NAT instance ju môže potrebovať vypnúť. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## Source-file generation — Fluent Bit

Exact path, inode, rotation state, producer/container identity a time window source log file-u čítaného Tail inputom. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Source provenance

Attestation opisujúca, ako konkrétna source revision vznikla, kto a aký process ju vytvoril a ktoré source-control controls boli presadené. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Source release generation — Helm

Current release revision a jej immutable chart/dependency/values/manifest, image a durable-state identities, z ktorých začína plánovaný transition. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Source revision

Konkrétny logicky immutable snapshot repository identifikovaný revision ID, napríklad Git commit SHA, spolu s relevantnou version-control metadata. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Source SBOM

SBOM generovaná zo source manifests, lockfiles a repository contentu pred vytvorením final artifactu. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## Source-to-admitted resource diff

Porovnanie resources v Git/source Pod template s effective values po LimitRange a ďalších admission mutations. Pozri [ResourceQuota a LimitRange](../docs/09-kubernetes/resourcequota-limitrange.md).

## Source-to-field provenance — Helm

Korelačný chain od values source/pathu a helper/pipeline transformácie po exact rendered, live a process-loaded Kubernetes field. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

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

## Split-writer incident

Failure, pri ktorom viac processov alebo nodes verí, že má write authority nad rovnakou persistent data identity. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

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

## Stable instance key — Terraform

Configuration-derived key s dlhodobým identity významom používaný v `for_each` addressách; jeho zmena je resource identity change a môže vyžadovať `moved` alebo state migration contract. Pozri [Expressions a dependency graph](docs/07-infrastructure-as-code-and-configuration-management/expressions-and-dependency-graph.md).

## Stable inventory host identity — Ansible

Dlhodobá automation identita hostu spájajúca `inventory_hostname` s immutable asset alebo instance ID, environmentom a overiteľnou connection identity. IP adresa sama osebe nie je dostatočný identity contract. Pozri [Inventory](docs/07-infrastructure-as-code-and-configuration-management/inventory.md).

## Stable network identity — StatefulSet

Predvídateľné per-ordinal DNS meno StatefulSet Podu, ktoré pretrváva ako logical slot identity naprieč Pod replacementom. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Stable ordinal identity — StatefulSet

Logical identita StatefulSet repliky odvodená z názvu a ordinalu, napríklad `db-0`, zachovaná pri replacement-e, hoci Pod UID a process sa zmenia. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Stable selector contract — Helm

Helper a values contract, ktorý zachováva immutable workload selector labels a ich zhodu s Pod a Service labels medzi podporovanými revisions. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Stable service identity

Logical `service.name` alebo ekvivalentná identity zachovaná cez scaling, restart a Pod/host replacement, oddelená od ephemeral process a instance attributes. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Stage — CI/CD

Logická skupina jobs alebo broad ordering barrier v pipeline. Stage nie je samostatná execution unit a pri presnom DAG modeli nemusí určovať všetky dependencies. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## Stage DAG subject

Identita multi-stage graphu zahŕňajúca stage names, base/inputs, dependency edges, targets, platforms, cache outcomes a transfers. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## Stage-output secret incident

Incident, pri ktorom secret prejde cez generated artifact, `COPY --from`, cache alebo export z build stage-u do final image-u. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## Staging area

Používateľský názov pre Git index ako pripravovaný snapshot ďalšieho commitu. Pozri [Working tree, staging area a repository](docs/03-git-and-automation/working-tree-staging-repository.md).

## Staging-label transition — Secrets Manager

Riadený presun labelov ako `AWSPENDING`, `AWSCURRENT` a `AWSPREVIOUS` medzi immutable secret versions; nepreukazuje sám target ani consumer state. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Stale approval — GitLab

Approval, ktorý bol udelený pre starší source SHA, target context, candidate alebo policy revision a už neposkytuje dôkaz pre aktuálny merge subject. Pozri [Merge requests a approvals](docs/06-gitlab/merge-requests-and-approvals.md).

## Staleness — Prometheus

Semantics, ktorou Prometheus prestane považovať starú sample za aktuálnu po zmiznutí targetu alebo series. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Staleness verdict — Prometheus

Rozhodnutie, či series predstavuje current measurement, zmizla pre target/label/producer zmenu alebo je už stale a nesmie byť interpretovaná ako aktuálna hodnota. Pozri [Prometheus](docs/12-observability/prometheus.md).

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

## Startup verdict

Verdikt, že konkrétny container generation dokončil bounded inicializáciu a kubelet môže začať liveness/readiness hodnotenie. Pozri [Probes](../docs/09-kubernetes/probes.md).

## Stash — Git

Lokálny Git stav uchovávajúci dočasné working-tree a index changes pod `refs/stash`. Nie je náhradou remote backupu. Pozri [Cherry-pick a stash](docs/03-git-and-automation/cherry-pick-and-stash.md).

## State-based testing

Testovanie výsledného outputu alebo stavu namiesto detailného overovania interných interakcií. Pozri [Mocks, stubs a fakes](docs/04-testing-and-quality/mocks-stubs-fakes.md).

## State boundary — Terraform

Rozsah resources zdieľajúcich jeden state, lock, permissions, plan/apply lifecycle a failure blast radius. Pozri [Infrastructure as Code principles](docs/07-infrastructure-as-code-and-configuration-management/infrastructure-as-code-principles.md) a [Terraform state](docs/07-infrastructure-as-code-and-configuration-management/terraform-state.md).

## State-delta inventory

Per-layer záznam toho, čo release zmenil v artifacte, confige, routingu, infrastructure, databáze, events, cache, external side effects a clients, spolu s current effective state-om a reversibility. Je vstupom pre recovery eligibility a voľbu rollbacku, roll-forwardu, compensation alebo restore. Pozri [Rollback a roll-forward](docs/05-ci-cd-and-release/rollback-and-roll-forward.md).

## State locking — Terraform

Backend-supported koordinácia, ktorá bráni súbežným Terraform write operáciám pracovať s rovnakým state-om a vytvoriť lost update alebo corruption. Pozri [Remote backend a state locking](docs/07-infrastructure-as-code-and-configuration-management/remote-backend-and-state-locking.md).

## State Manager

Systems Manager capability periodicky aplikujúca idempotentné document associations na target managed nodes na udržiavanie desired configuration. Pozri [Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## State snapshot — Terraform

Konkrétna verzia Terraform state-u obsahujúca resource bindings, known attributes, outputs a metadata ako lineage a serial. Pozri [Terraform state](docs/07-infrastructure-as-code-and-configuration-management/terraform-state.md).

## State surgery — Terraform

Riadená zmena state metadata pomocou príkazov ako `state mv`, `state rm` alebo výnimočne recovery push, vykonaná s lockom, backupom, review a následným planom. Pozri [Terraform state](docs/07-infrastructure-as-code-and-configuration-management/terraform-state.md).

## Stateful acceptance verdict

Dôkaz správnej ordinal/Pod/storage/member väzby, fencing-u, quorum/synchronization, client endpoints, data lineage, backup/restore a business outcome-u. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Stateful decommission subject

Versionovaný application-aware scale-down alebo removal transition zahŕňajúci leadership, traffic drain, membership, data redundancy, Pod termination a storage retention. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Stateful firewall

Firewall udržiavajúci connection/flow state a používajúci ho pri rozhodovaní o packets. Pozri [Firewally](docs/02-networking-and-web/firewalls.md).

## Stateful membership subject

Identita application clusteru, member IDs, ordinal mappings, roles, leader term, quorum view, replication positions a fencing epochs. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Stateful observation matrix

Mapovanie StatefulSet controller, ordinal, DNS, storage, membership, revision, readiness, retention a business boundaries na ich subjects a evidence. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Stateful scale transition

Application-aware pridanie alebo odstránenie ordinalu spolu s membership join/leave, rebalance, leadership, quorum, Pod a PVC lifecycle-om. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## StatefulSet

Kubernetes workload controller poskytujúci skupine Podov stabilné ordinal identities, ordered lifecycle a možnosť per-replica persistent storage. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## StatefulSet lifecycle subject

Spoločná identita StatefulSet UID/generation, revisions, ordinal slots, Pod UIDs, DNS, PVC/PV/backend data, application membership a acceptance state-u. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## StatefulSet partition

RollingUpdate hranica, ktorá aktualizuje iba StatefulSet Pody s ordinalom väčším alebo rovným nastavenej partition hodnote. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Stateless firewall

Firewall posudzujúci každý packet podľa explicitných pravidiel bez connection state. Pozri [Firewally](docs/02-networking-and-web/firewalls.md).

## Stateless return-path contract — NACL

Explicitné rules potrebné pre response direction vrátane client ephemeral destination ports, pretože NACL nepozná stav pôvodnej connection. Pozri [Security Groups a Network ACLs](docs/11-cloud-and-aws/security-groups-network-acls.md).

## Static analysis

Analýza source alebo jeho reprezentácie bez vykonania celej aplikácie, napríklad linting, type checking alebo data-flow analysis. Pozri [Static analysis, linting a type checking](docs/04-testing-and-quality/static-analysis-linting-type-checking.md).

## Static control-plane authority

Authoritative local manifest, kubelet a runtime state pre control-plane component spúšťaný ako static Pod, odlíšený od API-visible mirror Podu. Pozri [Control plane components](docs/09-kubernetes/control-plane-components.md).

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

## Storage acceptance verdict

Verdikt, že správny PVC/PV/backing asset je bezpečne attached a mounted, obsahuje accepted data generation, má jediného oprávneného writera a obnoviteľný backup. Pozri [Volumes, PV, PVC a StorageClass](../docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Storage attachment subject

Identita backend volume/objectu, node/device pathu, filesystem UUID, host/container mounts, options, topology a active writer lease-u. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## storage autoscaling — RDS

RDS capability automaticky zvýšiť allocated database storage do nastavenej maximálnej hranice pri nedostatku free space podľa service rules. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## Storage fencing

Mechanizmus zabezpečujúci, že stale writer už nemôže zapisovať pred aktiváciou nového writer-a. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## Storage fencing epoch

Monotónna application alebo storage-provider generation určujúca, ktorý writer smie aktuálne meniť persistentné dáta po failoveri alebo replacement-e. Pozri [Volumes, PV, PVC a StorageClass](../docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Storage observation matrix

Mapa evidence cez data identity, claim, StorageClass, PV, backend asset, scheduling, attachment, mount, application, backup a cleanup boundaries. Pozri [Volumes, PV, PVC a StorageClass](../docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Storage quota — Kubernetes

ResourceQuota limit agregovaných PVC requests, počtu claims alebo StorageClass-specific storage consumption v namespace. Pozri [ResourceQuota a LimitRange](docs/09-kubernetes/resourcequota-limitrange.md).

## Storage recovery acceptance verdict

Service-specific restore dôkaz viažuci správnu S3 version, EBS checkpoint/full-performance alebo EFS namespace/permissions k application a business outcome-u vrátane forbidden data identity/access paths. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Storage subject

Versionovaná identita business data, authoritative ownera, S3 object/version, EBS volume/snapshot/checkpoint alebo EFS filesystem/access-point generation, encryption, retention a recovery objective-u. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Storage troubleshooting chain

Diagnostické poradie PVC → StorageClass/provisioner → PV binding → scheduling topology → VolumeAttachment → CSI node mount → application I/O. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Storage version — Kubernetes

Interná API verzia, v ktorej API server persistuje konkrétny resource type, pričom externé clients môžu používať iné podporované versions s conversion. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## StorageClass

Cluster-scoped Kubernetes policy object definujúci provisioner, parameters, reclaim policy, binding mode, expansion a topology defaults pre dynamicky provisioned volumes. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## StorageClass generation

Versionovaný provisioning contract zahŕňajúci CSI provisioner, parameters, reclaim policy, binding mode, expansion a allowed topology. Pozri [Volumes, PV, PVC a StorageClass](../docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

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

## Structured-metadata boundary — Loki

Pravidlo určujúce, ktoré dynamic per-entry fields zostanú structured metadata namiesto stream labels, aby nevytvárali stream explosion. Pozri [Loki](docs/12-observability/loki.md).

## Structured metadata — Loki

Per-entry key/value metadata uložené bez vytvorenia novej stream identity, vhodné pre high-cardinality correlation fields. Pozri [Loki](docs/12-observability/loki.md).

## Structured policy decision

Policy result obsahujúci okrem allow/deny aj reason, policy IDs, revision, violations alebo obligations v machine-readable forme. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Stub — test double

Kontrolovaná náhrada dependency vracajúca vopred pripravené odpovede pre riadenie testovacieho scenára. Pozri [Mocks, stubs a fakes](docs/04-testing-and-quality/mocks-stubs-fakes.md).

## Subchart hook authority

RBAC, credentials a external side-effect capability pridaná dependency hookom do spoločného single-release execution surface-u, aj keď parent application runtime tieto oprávnenia nepotrebuje. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Subgroup — GitLab

Group vnorená v parent group, používaná na delegovanie ownershipu, členstva a policy pre podmnožinu projects. Pozri [Projects, groups a permissions](docs/06-gitlab/projects-groups-permissions.md).

## Subject

Entita, ktorá iniciuje operation alebo pristupuje k resource-u a je reprezentovaná principalom v security context-e. Pozri [Authentication, authorization a auditing](docs/13-security-and-identity/authentication-authorization-auditing.md).

## Subject-bound authorization verification

Overenie exact allowed a forbidden requests pre current credential, subject/groups, binding/aggregation generation a následného admission/runtime/business outcome-u. Pozri [RBAC](../docs/09-kubernetes/rbac.md).

## Subject-bound evidence closure

Verdikt, že dôkazy pre exact incident, release, Pod, Node a request subject pokrývajú source-to-query chain a podporujú prijaté rozhodnutie. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Subject-bound incident closure

Záverečný verdict spájajúci root cause, authoritative remediation, original/forbidden outcomes, adjacent cohorts, telemetry coverage a preventive control s exact incident subjectom. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Subject-bound referrer — OCI

Signature, provenance, SBOM alebo iný artifact explicitne viazaný na image index alebo platform manifest digest. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Subject-bound runtime verification

Health, configuration, client-path alebo business evidence viazaná na exact image, container/project generation a configuration/data epochs. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Subject-bound security evidence inventory

Množina signature, provenance, SBOM, scan, runtime-policy, identity, network/storage a exception evidence validná pre exact artifact/workload. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Subject-bound test stage

Test verdict viazaný na exact source, inputs, platform, build artifact a final image subject. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## Subject-bound upgrade closure

Verdikt, že target platform generation je prijatá, mixed-version stav skončil, business a telemetry fungujú a stará generácia bola bezpečne retired. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Subject identifier — OIDC

Hodnota `sub`, ktorá spolu s issuerom stabilne identifikuje End-Usera v OIDC trust doméne. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md).

## `subject` — OCI manifest

OCI descriptor viažuci artifact manifest na iný manifest digest, ktorý predstavuje jeho subject. Pozri [Image signing](docs/13-security-and-identity/image-signing.md).

## Subject-preserving reproduction — Docker

Kontrolovaný experiment, ktorý zachová relevantný image/platform digest, runtime configuration, kernel/runtime class, data clone a flow/load condition a mení iba jednu hypothesis variable. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## SubjectAccessReview

Kubernetes authorization API request zisťujúci, či konkrétna identita smie vykonať zadanú akciu nad resource-om alebo URL. Pozri [RBAC](docs/09-kubernetes/rbac.md).

## SubjectConfirmation — SAML

SAML element určujúci spôsob, recipienta, request binding a časové podmienky, za ktorých možno assertion použiť. Pozri [SAML](docs/13-security-and-identity/saml.md).

## Subnet

Časť IP address space definovaná prefixom a použitá ako logická routing alebo topology jednotka. Pozri [IPv4, IPv6 a subnetting](docs/02-networking-and-web/ipv4-ipv6-subnetting.md).

## Subnet IP headroom

Voľná použiteľná IP/ENI capacity po zohľadnení reserved addresses, steady state-u, load balancerov, endpoints, Pods, managed services a rollout/failover replacementu. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## Subnet placement subject — AWS

Exact subnet identity vrátane VPC, AZ, IPv4/IPv6 prefixes, available IP headroom, route-table association, NACL, endpoint/gateway dependencies a workload cohorts, ktoré do subnetu môžu byť umiestnené. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## `subPath` staleness boundary

Delivery boundary, pri ktorej file mount cez `subPath` typicky nesleduje priebežné ConfigMap/Secret projection updates a zostáva viazaný na pôvodný mounted file subject. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## `subPath` update limitation

Kubernetes volume-mount hranica, pri ktorej ConfigMap alebo Secret pripojený cez `subPath` typicky nedostáva priebežné projection updates. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## Subresource — Kubernetes

Samostatný API endpoint pre vybranú časť alebo operáciu resource-u, napríklad `/status`, `/scale`, `/log`, `/exec` alebo `/eviction`. Pozri [API a object model](docs/09-kubernetes/api-object-model.md).

## Subshell

Oddelený shell execution context, ktorého zmeny premenných a working directory sa nemusia preniesť späť do parent shellu. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md).

## Successful latency

Latency operácií, ktoré splnili success contract, sledovaná oddelene od rýchlych alebo pomalých failures. Pozri [Golden Signals](docs/12-observability/golden-signals.md).

## Supersession — release

Explicitný prechod, pri ktorom nový immutable candidate nahradí starší candidate. Supersession record zachová delta scope a určí, ktoré evidence, approvals a rollout rozhodnutia zostávajú platné a ktoré sa invalidujú. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Supplier due diligence

Risk-based overovanie identity, procesov, controls, evidence, maintenance, incident response a transitive dependencies software supplier-a. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## Support boundary — cloud

Hranica určujúca, ktorú časť incidentu môže meniť alebo diagnostikovať provider, zákazník alebo third party a aké evidence sú potrebné na efektívnu eskaláciu. Pozri [Shared responsibility model](docs/11-cloud-and-aws/shared-responsibility-model.md).

## Supported upgrade path — Terraform module

Module ownerom deklarovaná a testovaná cesta zo staršej podporovanej version na novšiu, zahŕňajúca contract zmeny, retained moved history, provider constraints, plan assertions a runtime verification. Pozri [Modules](docs/07-infrastructure-as-code-and-configuration-management/modules.md).

## Supported version policy

Pravidlá určujúce, ktoré release lines dostávajú opravy, security updates a podporu a kedy dosiahnu end of life. Pozri [Release management](docs/05-ci-cd-and-release/release-management.md).

## Surge-capacity subject

Node a cluster capacity, topology, ports, volumes a terminating overlap potrebné na realizáciu Deployment `maxSurge` bez porušenia availability budgetu. Pozri [Deployment](docs/09-kubernetes/deployment.md).

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

## Symptom-to-closure lifecycle — CloudOps

Incident model od user/business symptómu cez exact subject, hypotheses, discriminating evidence, containment a authoritative recovery po original/forbidden/adjacent validation a recurrence control. Pozri [CloudOps troubleshooting drills](docs/11-cloud-and-aws/cloudops-troubleshooting-drills.md).

## Symptom-to-release translation — Helm

Proces prekladu user alebo business symptómu na exact release, render, hook, live object, process, data a request identities pred formulovaním troubleshooting hypotéz. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Symptom-to-subject translation

Prevod user alebo business symptómu na konkrétne cluster, release, object, process, data, flow a time identities vhodné na falsifikovateľnú diagnostiku. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

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

## Tag-route generation — Fluent Bit

Versionovaný mapping input tags cez filter/output `Match` pravidlá na intended a forbidden destinations. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Tail input — Fluent Bit

Input plugin sledujúci log files, ich offsets a rotation lifecycle. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Tail latency

Latency najpomalšej časti request distribution, typicky sledovaná cez vyššie percentiles alebo threshold compliance. Pozri [RED method](docs/12-observability/red-method.md).

## Tail offset generation

Exact file identity a byte/record position uchovaná Tail DB pre pokračovanie čítania po flushi, rotate alebo restart-e. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Tail sampling

Trace sampling decision vykonané po zhromaždení väčšej časti trace-u, aby bolo možné zachovať errors, high-latency alebo inak zaujímavé traces. Pozri [Metrics, logs, traces a events](docs/12-observability/metrics-logs-traces-events.md).

## Tail sampling — OpenTelemetry

Sampling decision vykonané po zhromaždení väčšej časti trace-u, typicky v stateful Collector pipeline. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Taint analysis

Statická analýza sledujúca nedôveryhodné dáta od source cez transformácie po citlivý sink. Pozri [Static analysis, linting a type checking](docs/04-testing-and-quality/static-analysis-linting-type-checking.md).

## Taint — Kubernetes

Key/value/effect značka na Node-e, ktorá odpudzuje Pody bez matching toleration pri scheduling-u alebo execution-e. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Taint-repulsion verdict

Rozhodnutie, či incoming Pod toleruje všetky relevantné Node taints pre daný effect; toleration sama Node nevyberá. Pozri [Taints, tolerations, affinity a topology](../docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Target credential generation

Credential value a principal state, ktoré target database, provider alebo service aktuálne akceptuje; nemusí sa zhodovať so secret version označenou `AWSCURRENT`. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Target-eligibility cohort — containers

Množina ECS tasks alebo Kubernetes Pods, ktoré patria k approved release generation, sú runtime-ready, registered v správnom service/load-balancer path-e a môžu bezpečne prijímať nové business requests. Pozri [Amazon ECS a Amazon EKS](docs/11-cloud-and-aws/ecs-eks.md).

## Target eligibility set

Množina targets, ktoré sú registered, v enabled AZ scope, v použiteľnom lifecycle state a spĺňajú health/attribute contract pre konkrétnu target group. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## target group — ELB

Backend registration, protocol, port, health-check a traffic-lifecycle contract medzi load balancerom a jednou alebo viacerými targets. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## target health — ELB

Per-target-group stav vyjadrujúci, či registrovaný target prešiel health checks a je vhodný na routing trafficu. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## Target health oracle

Konkrétny protocol, port, path, matcher, timeout, interval a threshold contract odpovedajúci, či target môže bezpečne prijať nový traffic; nie všeobecný business-health dôkaz. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## Target manifest — Ansible

Subject-bound a auditovateľný zoznam stable host identities vybraných patternom a limitom pre konkrétny run, často doplnený environmentom, groups, connection identity a exclusion reason. Pozri [Inventory](docs/07-infrastructure-as-code-and-configuration-management/inventory.md).

## Target platform generation — Kubernetes

Schválená kombinácia Kubernetes, etcd, Node image/runtime, add-ons, APIs, controllers a workload compatibility, do ktorej upgrade konverguje. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Target — Prometheus

Network endpoint a associated labels, ktorý Prometheus plánuje pravidelne scrape-ovať. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Target publication policy

Policy overujúca, že production reference publikuje povolený target s expected base, user, content, metadata, platforms a lineage. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## Target relabeling

Prometheus relabeling fáza pred scrape-nutím, ktorá filtruje targets a mapuje discovery metadata na address, path, scheme a stabilné target labels. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Target release generation — Helm

Navrhovaná release revision so všetkými target chart/dependency/values/manifest, image, hook a durable-state generations, ktoré majú po transitione tvoriť accepted state. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## target tracking — Auto Scaling

Dynamic scaling policy snažiaca sa udržať zvolenú metric približne na target hodnote zmenou desired capacity. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Targeted follow-up drill

Nový drill odvodený z konkrétnej chyby, napríklad pomalého scope narrowing, context omylu, nebezpečného repairu alebo slabej validation.

## Targeting authority boundary — Systems Manager

Security a blast-radius hranica oddeľujúca oprávnenie meniť tags/resource-group membership od oprávnenia spúšťať privileged Run Command, patch alebo Automation nad targets vybranými týmito attributes. Pozri [AWS Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## `targetPort` — Service

Port alebo pomenovaný Pod container port, na ktorý Service dataplane smeruje traffic z publikovaného Service `port`. Pozri [Service a EndpointSlice](docs/09-kubernetes/service-endpointslice.md).

## Task-capability contract

Mapping jedného business alebo administrative tasku na required observations, preconditions, exact mutation, resource/data scope, forbidden actions, validation a audit. Pozri [Least privilege](docs/13-security-and-identity/least-privilege.md).

## Task intake protocol

Krátky pre-mutation záznam contextu, namespace-u, subjectu, desired change, hard constraints, forbidden changes, validation a časového budgetu.

## Task intake protocol — CKA

Krátky parsing úlohy na cluster/context, namespace, resource identity, požadovanú zmenu, constraints a validation criterion pred vykonaním commandov. Pozri [CKA timed labs](docs/10-helm-and-cka/cka-timed-labs.md).

## Task-oriented automation

Automation model skladajúci ordered tasks, conditions a orchestration controls nad targets namiesto univerzálneho persistentného resource graphu. Pozri [Terraform vs. Ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md).

## Task subject — CKA

Exact kombinácia cluster contextu, namespace-u alebo hostu, resource/component identity, current generation, požadovanej zmeny, constraints, forbidden changes a validation criterion.

## TCP connection

Transportný byte stream identifikovaný source/destination IP adresami a portmi. Pozri [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md).

## TCP handshake

Výmena SYN, SYN-ACK a ACK, ktorá synchronizuje sequence numbers a vytvorí TCP connection state. Pozri [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md).

## TCP/IP model

Praktický vrstvený model Application, Transport, Internet a Link používaný na opis Internet stacku. Pozri [OSI a TCP/IP model](docs/02-networking-and-web/osi-and-tcp-ip-model.md).

## TCP probe

Kubernetes probe overujúca úspešné otvorenie TCP connectionu na Pod IP a port bez overenia application protocol response alebo business correctness. Pozri [Probes](docs/09-kubernetes/probes.md).

## Technical rollback — Helm

Rollback, pri ktorom Helm úspešne obnoví historický rendered manifest a vytvorí deployed revision, ale ešte nie je preukázaná kompatibilita runtime-u s current durable alebo external state-om. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Telemetry

Dáta generované systémom o jeho stave a správaní, napríklad metrics, logs, traces, events, profiles a audit records. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Telemetry backpressure

Stav, keď downstream receiver alebo backend nestíha prijímať telemetry a producers alebo collectors musia bufferovať, retryovať, dropovať alebo obmedziť tok. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Telemetry backpressure boundary

Miesto, kde collector buffer, transport alebo backend capacity spomaľuje či dropuje signals a môže ovplyvniť Node disk, offset alebo evidence completeness. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Telemetry batching

Zoskupovanie viacerých telemetry records pred exportom na zníženie overheadu za cenu vyššej latency a väčšieho loss windowu. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Telemetry blind-spot subject

Exact Node, component, source alebo time cohort, pre ktorú evidence chýba pre pipeline failure, nie nevyhnutne pre absenciu incidentu. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Telemetry canary

Kontrolovaný end-to-end metric, log, trace alebo event occurrence používaný na overenie emission, delivery, processing, backend read-back, query a alert pathu. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Telemetry contract test

Automatizovaný test overujúci names, units, attributes, resources, correlation, cardinality a compatibility telemetry po zmene instrumentation alebo pipeline. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Telemetry coverage contract

Expected evidence inventory pre critical journey a jeho success, failure, no-data, privacy a correlation boundaries. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Telemetry coverage generation

Versionovaný inventár expected sources, collectors, configs a backend paths, ktoré musia byť end-to-end pozorovateľné pre konkrétnu cluster alebo Node generation. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Telemetry fan-out

Odosielanie rovnakého prijatého signalu do viacerých processing pipelines alebo backendov s odlišnými retention, security alebo analytics účelmi. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Telemetry freshness

Dôkaz, že expected signal source publikuje a delivery/query path prijíma dáta v povolenom delay/cadence intervale; oddeľuje chýbajúcu telemetry od nulovej business hodnoty. Pozri [Amazon CloudWatch a AWS CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## Telemetry lifecycle subject

Súvislý identity chain od source emission cez collection, buffer, transport, backend acknowledgement, indexing, query a retention po operational verdict. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Telemetry-loss window — OpenTelemetry

Time/signal-specific interval neobnoviteľnej alebo nepreukázateľnej straty pre queue overflow, processor drop, crash, expiry alebo backend failure. Pozri [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Telemetry pipeline

Reťazec instrumentation sources, agents alebo collectors, processingu, exportu, storage a query vrstiev, ktorými telemetry prechádza. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Telemetry read-back test

Validácia, ktorá po emission a exporte query-ne backend a overí effective identity, schema, value, correlation a freshness namiesto spoliehania sa iba na exporter success. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Telemetry requirement inventory

Zoznam metrics, traces, logs, events, identities, propagation a pipeline evidence odvodený z business journeys, SLIs, failure modes a operational decisions. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Telemetry retention

Čas a storage policy pre logs, metrics, Events, traces a audit records odvodená od incident, compliance, forensic a cost požiadaviek. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Telemetry retention verdict

Dôkaz, že logs, metrics, Events, audit a traces zostanú dostupné dostatočne dlho pre detection, incident, forensic a compliance potreby bez neprimeraného cost alebo exposure. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Telemetry self-observability

Monitoring samotného telemetry pipeline cez accepted, queued, dropped, retried a failed records spolu s resource usage a ingestion lagom. Pozri [Instrumentation a telemetry](docs/12-observability/instrumentation-telemetry.md).

## Telemetry tragedy of the commons

Stav shared observability platformy, v ktorom jednotliví producenti pridávajú drahú telemetry bez vlastného cost feedbacku a spoločne vyčerpajú kapacitu alebo budget. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Template artifact subject — Ansible

Identita vyrenderovaného configuration artifactu zahŕňajúca template source digest, execution environment, host identity, effective non-secret values, fact/cache generation, lookup dependencies, rendered checksum, validation verdict a destination. Pozri [Variables, facts a templates](docs/07-infrastructure-as-code-and-configuration-management/variables-facts-templates.md).

## Template contract — CI/CD

Versionované pravidlá reusable template definujúce inputs, defaults, outputs, artifacts, permissions, supported scenarios, failure semantics a compatibility policy. Pozri [Pipeline as Code](docs/05-ci-cd-and-release/pipeline-as-code.md).

## Template-equivalence verdict — ReplicaSet

Dôkaz, že controlled alebo adoptovaný Pod zodpovedá expected ReplicaSet template-u v image, config, secret, security, resources, probes a relevantných labels, nie iba selectorom. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## `template` — Helm

Go template action vkladajúca named template inline; na rozdiel od `include` neposkytuje output ako pipeline string. Pozri [Named templates](docs/10-helm-and-cka/named-templates.md).

## Template-resolution generation — document search

Effective merge matching index/component templates, priorít, settings a mappings použitý pri vytvorení nového backing indexu. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Template type graph — Helm

Sekvencia Go runtime types a textových transformácií, ktoré konkrétna pipeline vykonáva od values inputu po rendered field. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

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

## Terminating-replica overlap

Dočasný stav Deployment rollout-u, keď terminating old Pods stále držia resources, connections, ports alebo volumes popri active desired a surge Pods. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## Termination-budget subject — Pod

Pod UID, grace period, PreStop duration, signal timeline, connection drain, in-flight work, force-kill deadline a cleanup outcome tvoriace graceful termination contract. Pozri [Pod](docs/09-kubernetes/pod.md).

## Terraform backend

Terraform Core komponent určujúci state storage a podľa backendu aj locking, workspaces alebo remote execution behavior. Pozri [Remote backend a state locking](docs/07-infrastructure-as-code-and-configuration-management/remote-backend-and-state-locking.md).

## Terraform drift

Významný rozdiel medzi desired configuration, Terraform state a skutočným remote stavom, ktorý vyžaduje klasifikáciu ownershipu a vedomé reconciliation rozhodnutie. Pozri [Drift](docs/07-infrastructure-as-code-and-configuration-management/drift.md).

## Terraform evidence subject

Presná identita testovacej a policy evidence zahŕňajúca source/module revision, Terraform a provider versions, fixture/effective inputs, target identity, prior upgrade version, plan digest, policy package a cleanup/runtime verdict. Pozri [Terraform testing a policy](docs/07-infrastructure-as-code-and-configuration-management/terraform-testing-and-policy.md).

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

## Time-budget state machine — CloudOps exam

Question workflow `read/classify → solve alebo defer → provisional answer/confidence → second pass → consistency review`, ktorý chráni celý exam queue pred time collapse. Pozri [CloudOps domain review a timed reasoning](docs/11-cloud-and-aws/cloudops-domain-review-timed-reasoning.md).

## Time-series cardinality

Počet unikátnych kombinácií metric label values; nekontrolované dynamické labels výrazne zvyšujú memory, storage a query náklady. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Time series — Prometheus

Prúd timestampovaných samples identifikovaný metric name a úplným label setom. Pozri [Prometheus](docs/12-observability/prometheus.md).

## Time to first feedback

Čas od vzniku alebo odoslania zmeny po prvý relevantný a diagnostikovateľný výsledok pipeline. Pozri [Continuous Integration](docs/05-ci-cd-and-release/continuous-integration.md).

## Time to first useful feedback

Čas od vzniku alebo odoslania zmeny po prvý relevantný, diagnostikovateľný a akčný výsledok pipeline. Pozri [Continuous Integration](docs/05-ci-cd-and-release/continuous-integration.md).

## Time-to-full-performance

Recovery interval od incident decisionu po restored storage/application schopnú spĺňať production latency a throughput, nie iba po resource state `available`. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## `TIME-WAIT`

TCP state držaný po aktívnom close na ochranu pred starými segments a opätovným použitím rovnakého tuple. Pozri [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md).

## Timed lab — CKA

Praktický Kubernetes lab vykonávaný s pevným časovým limitom, bodovaním a povinnou validáciou na tréning exam execution schopností. Pozri [CKA timed labs](docs/10-helm-and-cka/cka-timed-labs.md).

## Timed-lab generation

Konkrétna verzia tréningového prostredia, task setu, fault injectors, scoring rules, hard validations a reset procedúr.

## TLS Secret

Kubernetes Secret typu `kubernetes.io/tls`, typicky obsahujúci `tls.crt` a `tls.key` pre controller alebo workload; celý certificate trust a rotation contract zostáva zodpovednosťou consumer workflowu. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## TLS termination

Bod, v ktorom proxy, load balancer alebo gateway ukončí TLS a sprístupní plaintext; vytvára novú trust boundary pre ďalší hop, identity propagation a certificate lifecycle. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## TLS — Transport Layer Security

Protokol poskytujúci šifrovanie, integritu a autentifikáciu komunikácie. Pozri [HTTPS, TLS, certificates a PKI](docs/02-networking-and-web/https-tls-certificates-pki.md).

## tmpfs mount — container

Memory-backed temporary filesystem s runtime lifecycle a explicitným size, memory a permissions contractom. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## tmpfs mount — Docker

Memory-backed runtime filesystem mount s ephemeral lifecycle, vhodný pre dočasné dáta alebo secrets podľa memory, swap a forensic threat modelu. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## Toil

Manuálna, opakujúca sa, automatizovateľná a nízko hodnotná prevádzková práca. Pozri [Toil and Technical Debt](docs/00-foundations/toil-and-technical-debt.md).

## Token audience boundary

Recipient restriction určujúca, pre ktorý verifier alebo service je token určený; platný token s nesprávnou audience musí byť odmietnutý. Pozri [ServiceAccount](../docs/09-kubernetes/serviceaccount.md).

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

## Topology-binding subject

Koordinované rozhodnutie medzi Pod constraints, scheduler selected Node/topology, StorageClass binding mode a provisioned PV affinity. Pozri [Volumes, PV, PVC a StorageClass](../docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Topology-domain inventory

Exact množina eligible Node UIDs a hodnôt `topologyKey`, ktoré tvoria domains pre jeden incoming Pod a current scheduler/placement generation. Pozri [Taints, tolerations, affinity a topology](../docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Topology domain — Kubernetes

Množina Nodes zdieľajúcich rovnakú hodnotu vybraného topology labelu, napríklad Node, zone, region alebo rack. Pozri [Taints, tolerations, affinity a topology](docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Topology-skew subject

Matching Pod population, eligible domains, current per-domain counts, `maxSkew`, `whenUnsatisfiable` a hypotetický incoming placement hodnotené ako jeden calculation subject. Pozri [Taints, tolerations, affinity a topology](../docs/09-kubernetes/taints-tolerations-affinity-topology.md).

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

## Trace-affinity contract

Pravidlo zabezpečujúce, že všetky spans jedného trace-u dorazia k rovnakej stateful tail-sampling alebo processing identity. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md) a [OpenTelemetry](docs/12-observability/opentelemetry.md).

## Trace attribute governance

Policy určujúca povolené, bounded, sensitive a searchable span attributes spolu s retention a sampling použitím. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Trace completeness

Miera, do akej backend obsahuje všetky relevantné spans a relationships konkrétneho trace-u; ovplyvňuje ju propagation, sampling, export a storage loss. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Trace-evidence loss window

Časový a tenant/partition-specific interval, pre ktorý historical traces nemožno obnoviť pre sampling, propagation, queue retention, block publication alebo storage loss. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Trace-evidence subject

Exact operation, trace/population, service/release, instrumentation, propagation, sampling, Collector, backend, tenant, recent/historical storage a query generation. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Trace-search generation

Exact backend product/version, tenant, query language/expression, attribute/index contract, time range a scanned storage generation broad trace searchu. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Trace-to-logs

Correlation workflow, ktorý z trace ID, span ID, service a času vytvorí query do log backendu. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## TraceQL

Tempo query language na trace a span search podľa attributes, duration, status a structural conditions. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Tracing-backend acceptance verdict

Dôkaz, že synthetic a incident-representative traces prešli samplingom, ingestom, recent/historical publication, lookup/search, retention a tenant-isolation checks. Pozri [Jaeger a Tempo](docs/12-observability/jaeger-tempo.md).

## Tracked connection subject — Security Group

Established flow rozpoznaný SG connection trackingom podľa relevantného tuple/state-u, odlišný od fresh connection attemptu po policy zmene. Pozri [Security Groups a Network ACLs](docs/11-cloud-and-aws/security-groups-network-acls.md).

## Traffic cutover

Riadené presmerovanie nových requestov alebo connections zo starej deployment farby na novú. Pozri [Blue-green deployment](docs/05-ci-cd-and-release/blue-green-deployment.md).

## Traffic-distribution subject

Versionovaná identita load balancera, listenera, TLS policy, ordered rule, target-group cohortu, target health/drain attributes, zonálneho placementu a business requestu použitá na ELB rozhodovanie. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## Traffic mirroring

Kopírovanie produkčných requestov do shadow systému bez použitia jeho response na primary request path. Pozri [Shadow deployment](docs/05-ci-cd-and-release/shadow-deployment.md).

## Traffic-reopen verdict — DR

Closure dôkaz, že restored state, single-writer fencing, clean credentials, external integrations, minimum capacity, telemetry a business transaction sú správne pred otvorením production trafficu. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Traffic-reopen verdict — recovery

Explicitné rozhodnutie otvoriť production traffic až po API, controller, external-resource, application-data, credential a business consistency overení. Pozri [etcd backup a restore](../docs/09-kubernetes/etcd-backup-restore.md).

## Traffic splitting — Gateway API

Rozdelenie Route trafficu medzi viac backendRefs podľa weights, používané napríklad pre canary alebo migration rollout. Pozri [Ingress a Gateway API](docs/09-kubernetes/ingress-gateway-api.md).

## Transformation generation — Grafana

Versionovaný ordered chain expressions a transformations aplikovaný na query frames pred visualization. Pozri [Grafana](docs/12-observability/grafana.md).

## Transformation — Grafana

Operácia aplikovaná na query results po ich získaní z data source-u na úpravu data frame-u pred vizualizáciou. Pozri [Grafana](docs/12-observability/grafana.md).

## Transit Gateway — AWS

Regionálny network transit hub prepájajúci viac VPCs a hybrid networks cez attachments, associations, propagations a vlastné route tables. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## Transit secrets engine — Vault

Vault engine poskytujúci encryption, decryption, signing alebo HMAC operations bez vydania underlying key materialu clientovi. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Transitive chart dependency — Helm

Dependency, ktorú parent chart získava nepriamo cez dependency vlastného subchartu; rozširuje render, hook, RBAC a supply-chain surface celého release-u. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Transitive render surface — Helm

Templates, helpers, CRDs, hooks, RBAC, images a values contracts získané nepriamo cez dependencies vlastných subcharts. Pozri [Chart dependencies](docs/10-helm-and-cka/chart-dependencies.md).

## Translated flow subject — AWS NAT

Original source/destination tuple spolu s NAT public/private addressom, translated source portom, destination tuple, connection state a reverse mappingom. Pozri [Internet Gateway a NAT Gateway](docs/11-cloud-and-aws/internet-gateway-nat-gateway.md).

## Translog

Elasticsearch/OpenSearch transaction-log mechanism používaný pri write durability a shard recovery podľa konkrétnej konfigurácie a produktu. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Trap — shell

Shell handler spustený pri definovanom signále alebo pseudo-signále ako `EXIT` či `ERR`. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md).

## Treatment variant

Experimentálny variant obsahujúci testovanú zmenu, ktorého outcome sa porovnáva s control variantom. Pozri [A/B testing](docs/05-ci-cd-and-release/a-b-testing.md).

## Trigger — CI/CD

Udalosť alebo explicitný pokyn, ktorý vytvorí pipeline run a určí jeho commit, event payload, actor identity, variables a permission context. Pozri [Trigger, artifact a cache](docs/05-ci-cd-and-release/trigger-artifact-cache.md).

## Trigger contract

Resolved runtime contract vytvorený triggerom, ktorý spája event identity, actor, candidate a workflow revision, typed inputs, permissions, secret scope a concurrency policy. Pozri [Trigger, artifact a cache](docs/05-ci-cd-and-release/trigger-artifact-cache.md).

## Trunk-based development

Branching model založený na častej integrácii malých zmien do jednej hlavnej branch, podporený krátkodobými branches, CI a feature flags. Pozri [Branching strategies](docs/03-git-and-automation/branching-strategies.md).

## Trust boundary

Miesto, kde sa mení úroveň dôvery, identity authority, administrative control, tenant, privilege alebo data-protection assumption. Pozri [Threat modeling](docs/13-security-and-identity/threat-modeling.md).

## Trust domain — SPIFFE

SPIFFE administrative a security boundary určujúca namespace workload identities a trust bundle pre ich verification. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Trusted-attribute contract

Pravidlo určujúce authoritative source, schema, writer permissions, freshness, normalization a failure behavior attribute-u používaného pri ABAC alebo role eligibility. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Trusted Node label

Placement label, ktorého key/value, owner, mutation path a node-pool generation sú chránené tak, aby workload nemohol falšovať compliance alebo dedicated-pool eligibility. Pozri [Taints, tolerations, affinity a topology](../docs/09-kubernetes/taints-tolerations-affinity-topology.md).

## Truthful changed signal — Ansible

Per-host alebo per-item result, ktorý pravdivo rozlišuje no-op od vykonanej mutation a správne riadi handler, recovery, audit a second-converge evidence. Pozri [Ansible idempotencia](docs/07-infrastructure-as-code-and-configuration-management/ansible-idempotency.md).

## TSDB index store — Loki

Odporúčaný Loki index format ukladajúci TSDB index blocks v object storage popri chunks. Pozri [Loki](docs/12-observability/loki.md).

## TSDB schema period — Loki

Dátumom ohraničená Loki storage/index generation určujúca store, object store, schema version a index prefix pre writes a historical reads. Pozri [Loki](docs/12-observability/loki.md).

## TTL-after-finished

Controller mechanizmus odstraňujúci dokončený alebo failed Job a jeho dependent resources po uplynutí `ttlSecondsAfterFinished`. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## TTL evidence gate — Job

Podmienka, že Kubernetes TTL cleanup sa môže vykonať až po externalizácii logs, result manifestu, checkpoints, operation IDs a incident evidence. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

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

## Typed render pipeline — Helm

Transformačný lifecycle od values presence/type validation cez functions, merge, serialization a indentation po final API field a runtime effect. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Typosquatting — package

Publikovanie malicious alebo deceptive package-u s názvom podobným legitimate dependency s cieľom využiť chybu používateľa alebo automatizácie. Pozri [Supply-chain security](docs/13-security-and-identity/supply-chain-security.md).

## UAT — User Acceptance Testing

Acceptance activity vykonaná alebo schválená reprezentatívnym business používateľom či stakeholderom na overenie fitu s reálnym procesom. Pozri [End-to-end a acceptance tests](docs/04-testing-and-quality/end-to-end-and-acceptance-tests.md).

## UDP datagram

Samostatná transportná správa bez zabudovanej garancie doručenia, poradia alebo retransmission. Pozri [TCP a UDP](docs/02-networking-and-web/tcp-and-udp.md).

## Unavailable budget — Deployment

Maximálny reviewovaný počet desired replicas, ktoré môžu byť počas rollout-u nedostupné podľa `maxUnavailable`, odlíšený od business capacity alebo PDB eviction budgetu. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## Unblended cost — AWS

Cost view zobrazujúci konkrétnu rate účtovanú za jednotlivé usage line items bez organization average. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Unbounded dimension

Telemetry dimension s nekontrolovaným alebo prakticky neobmedzeným počtom hodnôt, napríklad request ID, trace ID alebo user ID. Pozri [Cardinality](docs/12-observability/cardinality.md).

## Undefined policy decision

Stav, keď policy query nevytvorí result; consumer musí explicitne určiť, či znamená deny, error alebo not applicable. Pozri [Policy as Code](docs/13-security-and-identity/policy-as-code.md).

## Unit cost

Cloud cost prepočítaný na business jednotku, napríklad request, transakciu, build alebo aktívneho používateľa. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Unit-definition contract — FinOps

Explicitná definícia validnej business jednotky, napríklad successful settled payment, ktorá zabraňuje zlepšeniu unit costu cez počítanie retry alebo failed worku ako value. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Unit test

Rýchly test malej izolovanej jednotky správania s úzkym diagnostickým scope-om. Pozri [Unit, integration a component tests](docs/04-testing-and-quality/unit-integration-component-tests.md).

## Universal group — AD DS

AD DS group scope, ktorý môže obsahovať principals z viacerých domains vo forest-e a je replikovaný cez Global Catalog podľa platform semantics. Pozri [Active Directory](docs/13-security-and-identity/active-directory.md).

## Unknown batch outcome

Stav, keď worker nevie, či external side effect neprebehol, prebehol čiastočne alebo uspel bez result commit-u; pred retry vyžaduje lookup podľa stable operation identity. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Unknown commit outcome

Stav, keď database mohla transaction durable commitnúť, ale application nedostala acknowledgement pre connection failure; vyžaduje idempotency a reconciliation pred retryom. Pozri [Amazon RDS](docs/11-cloud-and-aws/rds.md).

## Unknown Docker operation outcome

Stav, keď klient nevie, či Engine mutation neprebehla, zanechala partial objects alebo úspešne spustila process; pred retry vyžaduje reconciliation. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Unknown hook outcome

Stav, keď hook side effect mohol commitnúť, ale Helm/Job completion alebo response evidence chýba; ďalší attempt musí najprv pozorovať durable operation state. Pozri [Hooks](docs/10-helm-and-cka/hooks.md).

## Unknown log-delivery outcome

Stav, keď agent nedostal acknowledgement po requeste, hoci backend mohol record prijať, takže retry nesie duplicate risk a checkpoint loss risk. Pozri [Fluent Bit](docs/12-observability/fluent-bit.md).

## Unknown notification outcome

Stav, keď Alertmanager nevie, či receiver vytvoril incident, pretože request mohol uspieť, ale acknowledgement sa stratilo; retry potom môže vytvoriť duplicate external outcome. Pozri [Alertmanager](docs/12-observability/alertmanager.md).

## Unknown operation outcome — CKA

Stav po timeout-e alebo prerušení write operation, keď nie je známe, či API alebo external side effect prebehol; pred retry sa vyžaduje read-back.

## Unknown-operation outcome — Kubernetes

Stav, keď request timeoutol alebo response zanikla, ale Kubernetes controller alebo external provider mohol side effect dokončiť; pred retry je potrebný authoritative read-back. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Unknown-outcome class — RED

Operation outcome, pri ktorom side effect mohol nastať, ale acknowledgement alebo authoritative evidence chýba; pred retry potrebuje reconciliation. Pozri [RED method](docs/12-observability/red-method.md).

## Unknown publication outcome — BuildKit

Stav po timeoute alebo partial exporte, keď nie je známe, či registry prijala úplný index, manifests, blobs, tag a attestations; pred retry vyžaduje registry read-back a graph-generation reconciliation. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Unknown reconcile outcome

Stav, keď controller nevie, či external alebo API mutation neprebehla, prebehla čiastočne alebo uspela bez zaznamenaného binding/statusu; pred retry vyžaduje lookup a reconciliation podľa stable identity. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Unknown remote outcome — IaC

Failure stav, v ktorom pipeline nedostala spoľahlivý výsledok remote mutation a pred retry musí cez request IDs, provider logs, remote observation a state reconciliation určiť, či operácia neprebehla, prebehla čiastočne alebo uspela bez state commit-u. Pozri [Infrastructure as Code principles](docs/07-infrastructure-as-code-and-configuration-management/infrastructure-as-code-principles.md).

## Unknown side-effect outcome

Stav, keď Lambda invocation timeoutne alebo stratí downstream response po tom, čo external service mohla side effect commitnúť; pred retryom vyžaduje idempotency key a authoritative reconciliation. Pozri [AWS Lambda](docs/11-cloud-and-aws/lambda.md).

## Unknown state-write outcome — Terraform

Failure stav, keď Terraform odoslal successor snapshot, ale pre timeout alebo network partition nevie, či backend write commitol. Pred ďalším writerom treba overiť version history, lineage/serial, lock a remote mutation timeline. Pozri [Terraform state](docs/07-infrastructure-as-code-and-configuration-management/terraform-state.md) a [Remote backend a state locking](docs/07-infrastructure-as-code-and-configuration-management/remote-backend-and-state-locking.md).

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

## Upgrade cohort

Množina control-plane, Node, add-on alebo workload subjects s rovnakou current alebo target generation používaná na oddelené meranie transitionu. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Upgrade health gate — Helm

Súbor pre-upgrade a post-upgrade podmienok nad clusterom, workloadom, dependencies, capacity, backups a observability, ktoré musia byť splnené pred pokračovaním release-u. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## Upgrade health gate — Kubernetes

Pre-upgrade kontrola API, etcd, Nodes, add-ons, certificates, capacity a backup stavu zabraňujúca upgradu už degraded clusteru. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Upgrade input closure — Helm

Úplný versionovaný súbor inputs rozhodujúcich o target renderi a operation behavior-e: chart artifact, dependency lock, effective values, release context, Capabilities/lookup state, post-renderer, Helm/plugins a target API/admission environment. Pozri [Upgrade a rollback](docs/10-helm-and-cka/upgrade-rollback.md).

## `upgrade --install` — Helm

Helm deployment pattern, ktorý vytvorí release, ak neexistuje, alebo aktualizuje existujúcu release; nerieši automaticky concurrency, migrations, drift ani secret management. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Upgrade-path test — Helm

Test, ktorý začína zo supported previous release s realistickými stored values, objects, retained data a external state-om a overuje target hooks, mixed-version transition, acceptance a recovery; fresh install ho nenahrádza. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Upgrade recovery gate

Pre-upgrade verdict zahŕňajúci health, spare capacity, backup, complete recovery set, restore rehearsal a rollback/roll-forward boundaries. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Upgrade test — Terraform module

Testovací workflow, ktorý vytvorí infraštruktúru podporovanou staršou module/provider verziou, následne vykoná upgrade plan/apply a overí compatibility, moved mappings a absence nečakaných replacements. Pozri [Terraform testing a policy](docs/07-infrastructure-as-code-and-configuration-management/terraform-testing-and-policy.md).

## Upstream branch

Remote-tracking alebo iný ref priradený lokálnej branch ako default comparison a synchronization target pre status, pull a push. Pozri [Clone, fetch, pull a push](docs/03-git-and-automation/clone-fetch-pull-push.md).

## Upstream forwarding subject

External alebo split-horizon DNS path identifikovaný CoreDNS forward rule, upstream resolverom, transportom, zone a response generation. Pozri [Cluster DNS](../docs/09-kubernetes/cluster-dns.md).

## URI — Uniform Resource Identifier

Identifikátor resource; URL je typ URI, ktorý zároveň opisuje spôsob alebo miesto prístupu. Pozri [HTTP](docs/02-networking-and-web/http.md).

## USE acceptance verdict

Rozhodnutie, že exact resource bottleneck bol odstránený, original user outcome obnovený, saturation a errors sa vrátili do guardrailov a capacity change nevytvorila forbidden downstream amplification. Pozri [USE method](docs/12-observability/use-method.md).

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

## Utilization observation — USE

Meranie podielu effective resource capacity používaného v presnom intervale a scope-e, vrátane explicitného time-, capacity-, throughput- alebo concurrency-based denominatora. Pozri [USE method](docs/12-observability/use-method.md).

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

## Values bundle generation

Versionovaný a redigovaný inventár všetkých values sources, ich poradia, overrides, schema verdictu a digestu pre jednu release operáciu. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Values — Helm

Konfiguračné vstupy chart templates získané z default `values.yaml`, override files a command-line overrides. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Values matrix oracle — Helm

Pre každý relevantný values case explicitne definovaný očakávaný resource, field, absence/presence a runtime effect, nie iba požiadavka, že render má skončiť bez chyby. Pozri [Helm testing a troubleshooting](docs/10-helm-and-cka/helm-testing-troubleshooting.md).

## Values precedence — Helm

Merge a override poradie, v ktorom neskoršie values files a explicitné command-line overrides prepisujú chart defaults a skoršie values. Pozri [Helm chart, template, values a release](docs/10-helm-and-cka/helm-chart-template-values-release.md).

## Values presence contract — Helm

Explicitné rozlíšenie missing key-u, `nil`, `false`, nuly, prázdneho stringu a prázdnej collection v chart configuration API. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

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

## Version-bound manifest

Immutable manifest generation, ktorá referencuje exact S3 object keys, version IDs a checksums a tým vytvára konzistentnejší multi-object publication contract. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Version-level telemetry

Metrics, logs a traces označené konkrétnou application alebo artifact verziou, ktoré umožňujú porovnať old a new behavior počas rollout-u. Pozri [Rolling update](docs/05-ci-cd-and-release/rolling-update.md).

## Version precedence

SemVer pravidlá určujúce poradie versions podľa MAJOR, MINOR, PATCH a pre-release identifiers; build metadata sa pri precedence ignorujú. Pozri [Semantic Versioning](docs/05-ci-cd-and-release/semantic-versioning.md).

## Version range

Constraint vyjadrujúci množinu akceptovaných dependency versions, ktorého konkrétna syntax a význam závisia od package ecosystemu. Pozri [Semantic Versioning](docs/05-ci-cd-and-release/semantic-versioning.md).

## Version skew — ring

Obdobie, počas ktorého rôzne deployment rings používajú odlišné release alebo client verzie nad spoločnými APIs a mutable state-om. Potrebuje maximálny podporovaný rozsah, compatibility contract a deadline. Pozri [Ring deployment](docs/05-ci-cd-and-release/ring-deployment.md).

## Vertical Pod Autoscaler — VPA

Samostatne inštalovaný Kubernetes controller a API odporúčajúci alebo aplikujúci zmeny Pod resource requests podľa observed usage a policy. Pozri [HPA a autoscaling](docs/09-kubernetes/hpa-autoscaling.md).

## Vertical scaling

Zmena kapacity jedného resource-u, napríklad väčšia VM alebo database instance, bez pridania ďalších replicas. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Veth pair

Dvojica prepojených virtual Ethernet interfaces spájajúca container namespace s host bridge/routing vrstvou. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## VEX

Vulnerability Exploitability eXchange statement vyjadrujúci affected, not affected, fixed alebo under-investigation status vulnerability voči konkrétnemu productu. Pozri [SBOM](docs/13-security-and-identity/sbom.md).

## Viewer connection — ELB

Client-to-load-balancer connection s vlastným DNS, source, listener, Security Group, TLS a request contractom; pri ALB je oddelená od backend target connection. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## Virtual environment — Python

Izolované Python prostredie s vlastným interpreter contextom a nainštalovanými packages. Pozri [Python for automation](docs/03-git-and-automation/python-for-automation.md).

## Virtual machine — VM

Izolovaný machine environment s virtual hardware, vlastným guest kernelom a userspace-om. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

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

Prelomenie guest/hypervisor boundary, pri ktorom code z VM ovplyvní hypervisor, host alebo inú VM. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Volatile AWS evidence

Logs, process/task state, target health, controller events, request IDs alebo configuration snapshots, ktoré môže restart, replacement, rollback alebo retention rýchlo odstrániť. Pozri [CloudOps troubleshooting drills](docs/11-cloud-and-aws/cloudops-troubleshooting-drills.md).

## Volatile evidence envelope

Súbor object statusov, Events, logs, container/Node state-u, packets, offsets, external auditov a timestamps, ktoré môžu remediation alebo retention rýchlo odstrániť. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Volatile evidence inventory — Docker

Vopred definovaná množina krátkodobých Docker events, container state/logs, daemon/kernel records, cgroup counters, sockets, conntrack, endpoint a process evidence, ktoré treba zachovať pred restartom, recreate, delete alebo prune. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Volume binding mode

StorageClass policy určujúca, či sa dynamic volume provision/binding vykoná okamžite alebo sa odloží do scheduling kontextu cez `WaitForFirstConsumer`. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Volume driver — Docker

Plugin alebo built-in implementation určujúca storage backend a mount semantics Docker volume-u; application consistency, backup a access modes zostávajú samostatným contractom. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## volume initialization — EBS

Proces načítania alebo zápisu všetkých blocks volume-u vytvoreného zo snapshotu alebo copy pred dosiahnutím plného stabilného výkonu. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Volume initialization readiness

Stav restored EBS volume-u, pri ktorom required snapshot blocks sú dostupné s predvídateľným performance contractom cez default initialization, Fast Snapshot Restore, provisioned initialization rate alebo completed pre-read. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Volume initialization subject

Identita empty/new volume initialization alebo schema migration zahŕňajúca data ID, generation, writer lock, migration ledger a postcondition verdict. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## Volume mode — Kubernetes

PVC/PV contract určujúci, či workload dostane filesystem mount alebo raw block device. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## Volume projection — Kubernetes configuration

Kubeletom materializované files z ConfigMapu, Secretu, ServiceAccount tokenu alebo ďalších sources v Pod mount namespace. Pozri [ConfigMap a Secret](docs/09-kubernetes/configmap-secret.md).

## VolumeAttachment

Cluster-scoped storage API object reprezentujúci attach požiadavku alebo stav CSI volume-u voči konkrétnemu Node-u. Pozri [Volumes, PV, PVC a StorageClass](docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## VolumeAttachment generation

Konkrétny Kubernetes attach intent a status medzi CSI volumeHandle a Node UID, oddelený od external provider attachment session. Pozri [Volumes, PV, PVC a StorageClass](../docs/09-kubernetes/volumes-pv-pvc-storageclass.md).

## `volumeClaimTemplates` — StatefulSet

StatefulSet šablóny, z ktorých controller vytvára samostatné PVCs pre jednotlivé ordinal replicas. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## VPC address-to-route lifecycle

Chain `network outcome → VPC/CIDR generation → zonálny subnet a ENI → effective route-table association → selected route → gateway/endpoint target → forward/return path → security a application verification`. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## VPC CNI — EKS

Kubernetes networking plugin integrujúci Pod networking s Amazon VPC ENIs a IP addressingom; jeho IPAM a subnet capacity ovplyvňujú Pod scheduling. Pozri [ECS a EKS](docs/11-cloud-and-aws/ecs-eks.md).

## VPC flow acceptance verdict

Closure, pri ktorom selected route, forward/return path, SG/NACL/firewall rules, DNS, listener/TLS a application/business request preukazujú očakávaný allowed flow aj forbidden paths. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## VPC Flow Logs

AWS telemetry zachytávajúca metadata IP flows pre VPC, subnet alebo ENI scope a podporujúca network path a accept/reject analýzu bez application payloadu. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## VPC flow-policy subject

Exact communication subject obsahujúci source/destination ENI a subnet identities, original/translated tuple, route, SG sets, NACL generations, connection state, listener/TLS identity a business request. Pozri [Security Groups a Network ACLs](docs/11-cloud-and-aws/security-groups-network-acls.md).

## VPC-origin path

Private CloudFront-to-supported-ALB/NLB/EC2 origin connection realizovaná cez CloudFront VPC origin configuration, subnet/SG a service-supported regional lifecycle. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

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

## Weighted domain gap — SOA-C03

Readiness medzera posudzovaná podľa domain weightu, severity mental-model chyby, practical-evidence coverage a time stability, nie iba podľa počtu nesprávnych odpovedí. Pozri [AWS Certified CloudOps Engineer – Associate](docs/11-cloud-and-aws/cloudops-engineer-associate-soa-c03.md).

## Weighted-exposure evidence

Request-level dôkaz viazaný na matched rule, target group, target/release identity a stickiness/connection cohort, ktorý overuje reálne canary exposure namiesto samotnej configured weight. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## weighted forwarding — ALB

ALB listener action rozdeľujúca traffic medzi viac target groups podľa relatívnych weights, často používaná pri canary alebo migration workflowe. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## weighted routing — Route 53

DNS routing policy rozdeľujúca odpovede medzi records podľa relatívnych weights, bez presnej request-level percentuálnej garancie kvôli DNS caching. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## White-box monitoring

Pozorovanie interných signals systému, napríklad queue depth, connection pool, error counters, garbage collection alebo saturation. Pozri [Monitoring vs. observability](docs/12-observability/monitoring-vs-observability.md).

## Whiteout — image layer

Marker v changesete, ktorý v merged view skryje path zo staršej layer bez odstránenia pôvodných bytes. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## Whitespace control — Helm

Použitie trim markers `{{-` a `-}}` a indentation functions na riadenie whitespace a newline v renderovanom YAML. Pozri [Template functions a pipelines](docs/10-helm-and-cka/template-functions-pipelines.md).

## Wildcard permission — Kubernetes RBAC

RBAC pravidlo s `*` pre verbs, resources alebo API groups, ktoré zahŕňa aj budúce resources alebo capabilities pridané po upgrade. Pozri [RBAC](docs/09-kubernetes/rbac.md).

## Word splitting

Shell rozdelenie nequoted expansion výsledku na viac slov podľa `IFS`. Je častým zdrojom chýb pri paths a argumentoch. Pozri [Bash automation](docs/03-git-and-automation/bash-automation.md).

## Work-item claim

Bounded ownership record jedného batch itemu s worker/run identity, lease alebo visibility timeoutom, fencing epoch a acknowledgment/checkpoint state-om. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Work queue Job

Job model, v ktorom viac worker Podov odoberá položky z external queue a completion correctness závisí od acknowledgment, retry a deduplication semantics tejto queue. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Work queue — Kubernetes controller

Fronta reconciliation keys s deduplication, retry a rate-limiting behavior používaná controller workers na bounded spracovanie zmien. Pozri [Desired state a reconciliation loops](docs/09-kubernetes/desired-state-reconciliation-loops.md).

## Worker node — Kubernetes

Fyzický alebo virtuálny server poskytujúci resources a node components potrebné na spúšťanie Pods pridelených control plane-om. Pozri [Kubernetes architecture](docs/09-kubernetes/kubernetes-architecture.md) a [Worker node components](docs/09-kubernetes/worker-node-components.md).

## Worker-node observation matrix

Mapovanie assignment, kubelet, runtime, CNI, CSI, image, resources, Service dataplane a business boundaries na ich subjects a diskriminačné observations. Pozri [Worker node components](docs/09-kubernetes/worker-node-components.md).

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

Počet workloads, ktoré možno bezpečne a výkonovo prevádzkovať na spoločnej infraštruktúre pri danom isolation/resource modeli. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Workload federation — Zero Trust

Explicitné prepájanie workload trust domains alebo identity authorities s riadenou výmenou trust bundles a samostatnou authorization policy. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Workload IAM subject

Exact workload owner, runtime/deployment binding, issuer, audience, credential generation, permissions, expiration, rotation, usage a audit identity non-human principalu. Pozri [IAM a RBAC](docs/13-security-and-identity/iam-rbac.md).

## Workload identity chain — containers

End-to-end authorization cesta od ECS task role alebo Kubernetes service account/Pod Identity association cez temporary credentials, IAM/SCP/boundary/resource/KMS policies po exact application API operation; host/node role je samostatná identity. Pozri [Amazon ECS a Amazon EKS](docs/11-cloud-and-aws/ecs-eks.md).

## Workload identity federation

Výmena ServiceAccount OIDC tokenu za krátkodobý external cloud alebo service credential podľa issuer, audience, subject a trust-policy podmienok. Pozri [ServiceAccount](docs/09-kubernetes/serviceaccount.md).

## Workload identity federation — CI/CD

Model, v ktorom job vymení krátkodobý signed identity token za scoped cloud alebo secret-provider credential bez uloženia dlhodobého access key v GitLabe. Pozri [Variables a secrets](docs/06-gitlab/variables-and-secrets.md).

## Workload identity — Kubernetes

Non-human identity workloadu, typicky reprezentovaná ServiceAccountom a krátkodobým tokenom alebo federovaným external credentialom. Pozri [ServiceAccount](docs/09-kubernetes/serviceaccount.md).

## Workload identity lifecycle subject

Úplný subject spájajúci workload identity intent, ServiceAccount UID, Pod UID, token instance, audience, process-loaded credential, authorization policy, external federation a auditovaný operation outcome. Pozri [ServiceAccount](../docs/09-kubernetes/serviceaccount.md).

## Workload identity subject — container

Short-lived authorization identity viazaná na workload/environment s audience, scopes, token epoch/expiration, issuance a auditom. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Workload identity — Zero Trust

Krátkodobá, workload-specific cryptographic identity používaná pre service authentication namiesto IP-based trust alebo shared static credentials. Pozri [Zero Trust](docs/13-security-and-identity/zero-trust.md).

## Workload isolation subject

Identita workloadu a VM/container boundary zahŕňajúca release/image, kernel, runtime config, resources, network, persistent ownera a isolation class. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Workload-plane abort criterion

Vopred definovaná Pod sandbox, network, storage, DNS, policy, telemetry alebo business podmienka, ktorá zastaví upgrade aj pri green control plane. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Workload-review subject — Well-Architected

Versionovaná identita business workloadu, release/topology, owners, constraints, lens/review generation, evidence window a expected outcomes hodnotená Well-Architected reviewom. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Workspace lifecycle

Životný cyklus job workspace-u od čistého vytvorenia cez checkout a execution po upload explicitných outputs, credential revoke a odstránenie temporary state. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## Writable layer — container

Dočasná zapisovateľná filesystem vrstva konkrétnej container instance nad read-only image layers. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## Write backing index

Najnovší backing index data streamu, do ktorého sa routujú nové documents do ďalšieho rolloveru. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Write compatibility

Schopnosť každej súčasne aktívnej application verzie zapisovať dáta, ktoré ostatné aktívne verzie bezpečne prečítajú a interpretujú. Pozri [Databázová kompatibilita počas deploymentu](docs/05-ci-cd-and-release/database-compatibility-during-deployment.md).

## Write index

Aktuálny backing index data streamu, do ktorého smerujú nové documents. Pozri [Elasticsearch alebo OpenSearch](docs/12-observability/elasticsearch-opensearch.md).

## Write-once publication

Publication contract, pri ktorom už vydaná logical version alebo candidate identity nemožno prepísať iným digestom. Collision s odlišným contentom je hard failure a unknown outcome sa rieši reconciliation podľa idempotency key. Pozri [Artifact versioning](docs/05-ci-cd-and-release/artifact-versioning.md).

## Writer epoch — container storage

Monotónna alebo fencing-aware generation authoritative writer-a použitá na odmietnutie stale processu/node-u. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## Writer-generation identity

Exact current RDS writer resource, AZ, endpoint mapping, engine/schema/parameter generation a failover timeline, ktoré určujú write authority. Pozri [Amazon RDS](docs/11-cloud-and-aws/rds.md).

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

## Zonal capacity headroom

Compute, subnet IP, quota, egress, data a dependency kapacita zostávajúca po strate definovanej Availability Zone a počas replacement alebo rollout surge-u. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Zonal egress subject

Per-AZ NAT, endpoint, route a source-subnet contract, ktorého zlyhanie môže odstaviť dependency access aj pri healthy compute a regional service control plane. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## Zonal NAT Gateway subject

NAT Gateway generation s konkrétnou AZ, subnetom, private/public addresses, route dependencies, connection capacity a source-subnet cohorts. Pozri [Internet Gateway a NAT Gateway](docs/11-cloud-and-aws/internet-gateway-nat-gateway.md).

## Zonal resource — AWS

Resource viazaný na jednu Availability Zone, napríklad subnet, EC2 instance alebo EBS volume, ktorého lifecycle a attachment constraints sú súčasťou zonal failure modelu. Pozri [Regions a Availability Zones](docs/11-cloud-and-aws/regions-availability-zones.md).

## zonal shift

Riadený presun podporovaného regional-service trafficu preč z impaired Availability Zone, ktorý stále vyžaduje zdravú capacity a dependencies v zostávajúcich AZ. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).
