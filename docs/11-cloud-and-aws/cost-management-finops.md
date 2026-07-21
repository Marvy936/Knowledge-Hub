# Cost management a FinOps

AWS cost management je súbor capabilities na meranie, alokáciu, plánovanie, kontrolu a optimalizáciu cloud spendu. FinOps je operating model, v ktorom engineering, finance a business spolupracujú na maximalizácii business value cloudu. Cieľom nie je slepo minimalizovať účet; cieľom je robiť rýchle a informované rozhodnutia o cost, performance, reliability, security a growth.

## 1. Mentálny model

```text
business outcome a unit economics
→ account/tag/cost-category allocation
→ cost and usage data
→ budgets, forecasts a anomaly detection
→ utilization a optimization opportunities
→ commitments a pricing model
→ engineering action
→ validation úspory a dopadu
→ continuous FinOps cadence
```

Cost je technický aj organizačný signal. Bez ownera, allocation modelu a operational contextu zostáva iba účet bez vysvetlenia.

## 2. Cost, price, value a unit economics

Rozlišuj:

- **price** — jednotková cena služby,
- **cost** — výsledný spend pri konkrétnom usage,
- **value** — business outcome vytvorený workloadom,
- **unit cost** — cost na business jednotku, napríklad request, zákazníka, transakciu alebo build,
- **total cost of ownership** — cloud spend plus engineering, operations, licensing, support, risk a migration cost.

Nižší unit price nemusí znamenať nižší TCO, ak riešenie vyžaduje viac toil, outages alebo custom operations.

## 3. FinOps princípy

Praktický FinOps model používa:

- teams ownership usage a costu,
- centralized enablement a governance,
- timely accessible data,
- business-value decisions,
- variable cloud cost model,
- continuous optimization,
- collaboration engineering/finance/business.

FinOps nie je iba mesačný report finance tímu. Engineering decisions priamo ovplyvňujú spend cez architecture, scaling, retention, data transfer, telemetry, deployment a commitments.

## 4. Account a organization boundary

AWS account je silná cost-allocation boundary.

Multi-account model umožňuje:

- oddeliť production/non-production,
- priradiť ownera,
- používať budgets a guardrails,
- analyzovať spend podľa linked accountu,
- distribuovať commitments a shared costs,
- izolovať experiments.

Jeden shared account s nedostatočným taggingom komplikuje chargeback, anomaly ownership aj rightsizing.

## 5. Cost allocation tags

User-defined a AWS-generated cost allocation tags môžu po aktivácii vstupovať do billing/cost datasets.

Tagging contract má obsahovať napríklad:

- `Owner`,
- `Team`,
- `Application`,
- `Environment`,
- `CostCenter`,
- `BusinessUnit`,
- `ManagedBy`,
- `DataClassification`,
- `Lifecycle`.

Obmedzenia:

- nie všetky resources podporujú tags rovnako,
- tags nemusia byť retroaktívne v historických dátach,
- chýbajúce alebo nekonzistentné hodnoty znižujú allocation coverage,
- shared resources potrebujú samostatný allocation model.

## 6. Cost Categories

AWS Cost Categories umožňujú mapovať raw billing dimensions do business hierarchie.

Použitie:

- business units,
- applications,
- environments,
- cost centers,
- shared services,
- chargeback/showback,
- exception grouping.

Cost Category rules môžu používať accounts, services, tags a ďalšie billing dimensions podľa aktuálnych capabilities.

Cost Category nie je náhrada kvalitného resource taggingu. Je to business mapping nad dostupnými dátami.

## 7. Shared cost allocation

Shared costs vznikajú napríklad pri:

- Transit Gateway,
- centralized NAT/egress,
- shared Kubernetes clusteri,
- observability platforme,
- CI runners,
- security tooling,
- support plan,
- enterprise discounts,
- shared databases alebo caches.

Allocation modely:

- rovnomerne,
- podľa headcountu,
- podľa direct spendu,
- podľa usage metriky,
- podľa requests/GB/build minutes,
- fixed subscription,
- business-agreed hybrid.

Model musí byť transparentný, stabilný a pravidelne prehodnotený.

## 8. AWS Billing data oproti Cost Explorer

Billing/invoice data odpovedá na otázku, čo AWS fakturuje v billing period.

Cost Explorer je analytická vrstva na:

- filtrovanie a grouping,
- trend analysis,
- forecasting,
- amortized a net amortized views,
- utilization/coverage reports,
- rightsizing a savings recommendations.

Rozdiely môžu vzniknúť pre:

- credits a refunds,
- upfront commitments,
- amortization,
- data freshness,
- estimated current-month charges,
- tax a invoice scope,
- billing adjustments.

Pri finance reconciliation používaj správny dataset pre správny účel.

## 9. Cost Explorer

Cost Explorer pomáha analyzovať cost a usage podľa dimensions ako:

- service,
- linked account,
- Region,
- Availability Zone,
- usage type,
- operation,
- purchase option,
- instance type,
- tags,
- Cost Categories.

Praktický workflow:

```text
identifikuj čas zmeny
→ group by service/account/Region
→ drill down usage type/operation
→ koreluj deployment alebo incident
→ identifikuj ownera
→ navrhni remediation
→ over nasledujúce obdobie
```

Cost Explorer data má oneskorenie a môže sa v current billing period upravovať. Nie je vhodný ako real-time metering systém.

## 10. Unblended, blended a amortized cost

### Unblended cost

Skutočná rate účtovaná konkrétnej line item usage bez rozloženia organization average.

### Blended cost

Pri consolidated billing môže pri niektorých pohľadoch používať priemernú rate naprieč organization.

### Amortized cost

Rozkladá upfront a recurring commitment fees cez obdobie benefitu.

### Net amortized cost

Zohľadňuje ďalšie discounts, credits alebo negotiated pricing podľa dostupných dát.

Pre unit economics a commitment analýzu je amortized pohľad často informatívnejší než cash invoice pohľad.

## 11. AWS Budgets

AWS Budgets môže sledovať:

- cost,
- usage,
- Reserved Instance utilization/coverage,
- Savings Plans utilization/coverage.

Budget obsahuje:

- scope a filters,
- period,
- actual a forecast thresholds,
- notifications,
- optional actions,
- subscribers.

Budget je lagging alebo forecast control, nie hard real-time spending limit. AWS resource usage sa po prekročení budgetu automaticky nezastaví, pokiaľ nie je nakonfigurovaná explicitná action a tá podporuje daný use case.

## 12. Budget actions

Budget action môže podľa podpory napríklad:

- aplikovať IAM policy,
- aplikovať SCP,
- vykonať targeted resource action.

Riziká:

- neočakávaný production impact,
- zablokovanie remediation,
- zmena počas incidentu,
- broad scope.

Automatické enforcement actions používaj opatrne, ideálne pre sandbox alebo explicitne bounded resources. Production cost anomaly má často vyvolať triage, nie okamžitý shutdown.

## 13. Cost Anomaly Detection

AWS Cost Anomaly Detection používa modely na identifikovanie neobvyklých spend patterns.

Konfigurácia zahŕňa:

- anomaly monitor,
- monitored scope,
- alert subscription,
- threshold,
- frequency a recipients.

Anomaly triage:

```text
anomaly time a impact
→ account/service/Region/usage type
→ deployment alebo traffic change
→ pricing/commitment zmena
→ legitimate growth alebo defect?
→ owner a remediation
→ false-positive feedback a threshold review
```

Anomaly detection nenahrádza budgets ani architecture cost controls. Legitímny, ale drahý growth nemusí byť anomália.

## 14. Cost and Usage data

Granulárne billing data možno exportovať na ďalšiu analýzu.

Aktuálny AWS cost-management model používa capabilities ako:

- AWS Data Exports,
- Cost and Usage Report-compatible datasets,
- billing views,
- S3 delivery,
- Athena/BI/FinOps platform processing.

Dáta môžu obsahovať veľké množstvo line items. Potrebuješ:

- partitioning,
- schema/version handling,
- retention,
- access control,
- data quality checks,
- allocation logic,
- query cost management.

## 15. Cost Optimization Hub

Cost Optimization Hub agreguje a prioritizuje optimization opportunities naprieč accounts a Regions.

Môže zahŕňať odporúčania ako:

- rightsizing,
- idle-resource deletion,
- Savings Plans,
- Reserved Instances,
- storage alebo service-specific optimization podľa podpory.

Výhody:

- deduplication odporúčaní,
- estimated savings,
- organization-wide prioritization,
- commercial-term awareness,
- jednotný backlog.

Recommendation nie je change approval. Pred implementáciou over performance, reliability, seasonality, commitments, migration effort a rollback.

## 16. Compute Optimizer a rightsizing

Rightsizing vyhodnocuje využitie a odporúča zmenu alebo odstránenie resources.

Overuj viac než CPU:

- memory,
- network,
- disk/EBS I/O,
- burst credits,
- p95/p99 alebo peak periods,
- latency/SLO,
- seasonality,
- HA headroom,
- failover capacity,
- startup behavior.

Rightsizing production resource-u bez load testu a canary môže vytvoriť vyšší outage cost než savings.

## 17. Idle a orphaned resources

Bežné zdroje waste:

- unattached EBS volumes,
- old snapshots/AMIs,
- idle load balancers,
- unused Elastic IPs,
- oversized NAT/data paths,
- stopped instances s retained storage,
- abandoned RDS snapshots,
- stale log groups,
- orphaned Kubernetes load balancers/disks,
- forgotten dev environments,
- duplicate backups.

Deletion workflow potrebuje ownera, retention, evidence, dependency check a recovery path.

## 18. Scheduling a elasticity

Non-production cost možno znižovať:

- scheduled stop/start,
- environment TTL,
- scale-to-zero pri podporovaných workloads,
- ephemeral preview environments,
- autoscaling,
- queue-based scaling,
- build-runner elasticity.

Nezabudni na:

- data/store cost počas vypnutia,
- startup latency,
- patching,
- scheduled jobs,
- time zones,
- shared dependencies.

## 19. Savings Plans

Savings Plans poskytujú zľavu výmenou za hodinový spend commitment počas termínu.

Rozlišuj:

- Compute Savings Plans,
- EC2 Instance Savings Plans,
- scope a flexibility,
- utilization,
- coverage,
- term a payment option.

Pred nákupom analyzuj:

- stabilný baseline usage,
- architecture roadmap,
- migration/planned shutdown,
- instance family/Region flexibility,
- existing RI/SP coverage,
- seasonality,
- expected growth.

Commitment na nestabilný alebo miznúci workload môže vytvoriť unused spend.

## 20. Reserved Instances

Reserved Instances poskytujú billing discount alebo capacity-related capability podľa konkrétnej služby a typu.

Dôležité osi:

- standard/convertible podľa služby,
- regional/zonal scope,
- size flexibility,
- term/payment,
- utilization/coverage,
- reservation marketplace pri podporovaných EC2 RIs.

RDS, ElastiCache, OpenSearch a ďalšie services môžu mať vlastné reservation semantics. Nepredpokladaj, že fungujú rovnako ako EC2.

## 21. Spot

Spot využíva spare capacity za nižšiu cenu s interruption riskom.

Vhodné:

- batch,
- stateless workers,
- fault-tolerant CI,
- distributed processing,
- flexible containers.

Potrebuje:

- interruption handling,
- checkpointing,
- diversified capacity,
- fallback,
- drain,
- idempotency.

Spot nie je cost optimalizácia pre workload, ktorý nevie prežiť interruption.

## 22. Storage cost

Optimalizuj:

- S3 storage classes a lifecycle,
- incomplete multipart uploads,
- noncurrent versions,
- EBS type/size/IOPS/throughput,
- snapshots,
- EFS lifecycle tiers,
- backup retention,
- log retention,
- cross-Region replication.

Najlacnejšia storage class môže mať retrieval fee, minimum duration alebo latency, ktoré nezodpovedajú access patternu.

## 23. Data transfer cost

Data transfer je častý skrytý driver.

Analyzuj:

- internet egress,
- cross-AZ traffic,
- cross-Region traffic,
- NAT Gateway processing,
- Transit Gateway,
- replication,
- CloudFront origin/viewer transfer,
- observability export,
- backup copies,
- Kubernetes topology.

Architecture diagram bez data-flow volume a direction neposkytuje cost model.

## 24. Observability cost

Telemetry cost vzniká cez:

- custom metrics,
- high-cardinality dimensions,
- log ingestion,
- retention,
- queries,
- traces,
- cross-account/Region transfer,
- archive/retrieval.

Optimalizácia:

- sampling,
- bounded cardinality,
- retention tiers,
- filtering pri source,
- structured logs,
- SLO-relevant telemetry,
- query governance.

Nevypínaj kritické audit alebo incident evidence bez risk analýzy.

## 25. Kubernetes a container cost allocation

Shared cluster potrebuje allocation podľa:

- namespace,
- workload,
- labels/tags,
- requested a actual resources,
- node pool,
- storage,
- load balancers,
- network transfer,
- idle capacity.

Requests ovplyvňujú scheduler a required capacity, preto iba actual CPU nemusí byť férová allocation metrika.

## 26. Serverless unit economics

Pri Lambda a event-driven services sleduj:

- invocations,
- duration,
- memory/CPU allocation,
- concurrency,
- retries,
- logs,
- downstream requests,
- data transfer,
- failed alebo duplicate processing.

Vyššia memory môže skrátiť duration a znížiť total cost. Optimalizácia potrebuje benchmark, nie iba znižovanie memory settingu.

## 27. Database cost

Sleduj:

- instance/cluster size,
- storage a I/O,
- Multi-AZ/read replicas,
- backup retention,
- data transfer,
- licensing,
- idle connections,
- inefficient queries,
- overprovisioned failover capacity.

Database rightsizing bez query a workload analýzy je rizikový.

## 28. Tagging a automation guardrails

Automatizuj:

- required tags pri provisioning,
- account/OU baseline,
- expiration tags,
- untagged-resource reports,
- sandbox TTL,
- budget/anomaly ownership,
- cost allocation coverage,
- cleanup workflows.

Guardrail musí mať exception process a nesmie blokovať incident recovery.

## 29. Showback a chargeback

### Showback

Zobrazuje tímom ich cost bez finančného preúčtovania.

### Chargeback

Prenáša cost do interného budgetu alebo P&L ownera.

Pred chargebackom zabezpeč:

- dôveryhodnú allocation,
- vysvetlené shared costs,
- dispute process,
- stable dimensions,
- timely reports,
- engineering context.

Nekvalitný chargeback vytvára spory a gaming namiesto optimalizácie.

## 30. Forecasting

Forecast používa historické data a predpoklady na odhad budúceho spendu.

Zahrň:

- organic growth,
- product launches,
- migrations,
- commitment purchases/expirations,
- seasonality,
- price changes,
- architectural changes,
- one-time projects.

Machine-generated forecast bez business roadmapy môže byť presný iba pre stabilný workload.

## 31. Cost optimization workflow

```text
opportunity
→ owner a workload context
→ technical validation
→ risk/SLO analysis
→ implementation plan
→ canary alebo bounded change
→ observe performance/reliability
→ measure realized savings
→ close alebo rollback
```

Estimated savings sa nemajú reportovať ako realized savings bez overenia po zmene.

## 32. Cost incident response

Cost incident môže byť:

- runaway resource creation,
- attack alebo credential compromise,
- logging cardinality explosion,
- retry loop,
- data-transfer spike,
- misconfigured autoscaling,
- abandoned high-cost service,
- pricing/commitment mismatch.

Postup:

```text
potvrď spend signal a freshness
→ identifikuj account/service/Region/usage type
→ koreluj CloudTrail/deployment/traffic
→ zastav bezpečne rastúci driver
→ zachovaj evidence
→ over business impact
→ oprav root cause a guardrail
→ validuj ďalšie billing obdobie
```

## 33. Cost governance cadence

Príklad:

- daily: anomaly alerts a critical spend,
- weekly: engineering optimization backlog,
- monthly: budget/forecast/showback,
- quarterly: commitments, architecture a unit economics,
- annual/strategic: contract, migration a platform investment.

FinOps cadence má byť naviazaná na delivery a business planning, nie oddelená od engineeringu.

## 34. Cost a reliability trade-off

Pri každej úspore vyhodnoť:

- SLO impact,
- failover capacity,
- RTO/RPO,
- supportability,
- security/compliance,
- engineering toil,
- growth headroom,
- reversibility.

Odstránenie standby capacity môže znížiť účet a zároveň dramaticky zvýšiť expected outage loss.

## 35. Cost a sustainability

Spoločné opatrenia:

- vyššia utilization,
- autoscaling,
- odstránenie idle resources,
- efektívnejší software,
- správne instance families,
- data lifecycle,
- managed services.

Sustainability a cost však nie sú identické; Region, hardware a environmental impact môžu mať ďalšie faktory.

## 36. SOA-C03 mapovanie

- **Domain 1** — performance/capacity analysis, Cost Explorer, anomaly detection, rightsizing a remediation,
- **Domain 2** — cost reliability trade-offs, backup/DR capacity a commitments,
- **Domain 3** — tagging, budgets, automation, lifecycle a cost guardrails,
- **Domain 4** — billing access, audit, cost-allocation governance a compromise-driven spend,
- **Domain 5** — data transfer, NAT, CDN, cross-AZ/Region a network cost.

SOA-C03 exam guide explicitne zahŕňa cost/TCO analysis a billing management. Kandidát musí rozumieť nielen pricing názvom, ale aj operational trade-offom.

## 37. Troubleshooting costu

### Neočakávaný EC2 spend

Over instance-hours, instance type, Region, purchase option, ASG desired capacity, Spot/On-Demand mix a deployment history.

### NAT Gateway spike

Over bytes processed, cross-AZ route, private endpoints, download loop a centralized-egress path.

### CloudWatch cost spike

Over log ingestion, retention, custom metrics, high-cardinality dimensions, queries a agents.

### S3 cost spike

Over storage growth, requests, retrieval, lifecycle, versions, replication a data transfer.

### Savings Plan nízka utilization

Over architecture migration, stopped capacity, instance-family/Region flexibility a workload seasonality.

### Cost Explorer a invoice sa nezhodujú

Over dataset, date range, amortization, credits/refunds, taxes, estimated charges a freshness.

## 38. Anti-patterny

### Cost optimization iba po prekročení budgetu

Optimalizácia má byť kontinuálna a začína pri architecture design-e.

### Tags bez enforcementu

Allocation coverage sa postupne rozpadne.

### Estimated savings ako realized savings

Ignoruje implementáciu a sekundárne dopady.

### Rightsizing iba podľa priemerného CPU

Prehliada peaks, memory, I/O a failure headroom.

### Commitment nákup podľa jedného mesiaca

Môže uzamknúť nestabilný spend.

### Vypnutie observability kvôli costu

Môže zvýšiť outage a security risk.

### Central FinOps tím vlastní všetku optimalizáciu

Engineering nemá spätnú väzbu ani accountability.

### Budget ako hard spending cap

AWS Budgets je primárne monitoring/notification/control mechanism, nie univerzálny real-time cap.

## 39. Kontrolné otázky

1. Aký je rozdiel medzi cost, price, value a unit cost?
2. Na čo slúžia cost allocation tags a Cost Categories?
3. Ako sa líši unblended a amortized cost?
4. Čo AWS Budgets robí a čo negarantuje?
5. Ako funguje Cost Anomaly Detection?
6. Na čo slúži Cost Optimization Hub?
7. Kedy sú Savings Plans alebo RIs rizikové?
8. Ako identifikuješ data-transfer cost driver?
9. Ako meriaš realized savings?
10. Prečo FinOps potrebuje engineering, finance aj business?

## Glossary impact

Relevantné pojmy: FinOps, cloud financial management, unit cost, unit economics, total cost of ownership, cost allocation tag, Cost Category, shared cost allocation, AWS Cost Explorer, unblended cost, blended cost, amortized cost, AWS Budgets, budget action, AWS Cost Anomaly Detection, AWS Data Exports, Cost and Usage Report, AWS Cost Optimization Hub, rightsizing, AWS Compute Optimizer, idle resource, Savings Plans, Reserved Instance utilization, coverage, showback, chargeback, realized savings, cost incident a cost allocation coverage.

## Oficiálna dokumentácia

- [AWS Cost Management User Guide](https://docs.aws.amazon.com/cost-management/latest/userguide/what-is-costmanagement.html)
- [Cost Explorer](https://docs.aws.amazon.com/cost-management/latest/userguide/ce-what-is.html)
- [AWS Budgets](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html)
- [AWS Cost Anomaly Detection](https://docs.aws.amazon.com/cost-management/latest/userguide/manage-ad.html)
- [Cost Optimization Hub](https://docs.aws.amazon.com/cost-management/latest/userguide/cost-optimization-hub.html)
- [AWS Data Exports](https://docs.aws.amazon.com/cur/latest/userguide/what-is-data-exports.html)
- [AWS Billing and Cost Management home page](https://docs.aws.amazon.com/cost-management/latest/userguide/view-billing-dashboard.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Well-Architected Framework](well-architected-framework.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: AWS Certified CloudOps Engineer – Associate (SOA-C03) →](cloudops-engineer-associate-soa-c03.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
