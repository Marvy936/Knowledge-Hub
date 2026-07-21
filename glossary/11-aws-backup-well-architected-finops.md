# AWS recovery, architecture review and FinOps glossary entries

## Amortized cost — AWS

Cost view, ktorý rozkladá upfront a recurring commitment fees cez obdobie ich benefitu, aby zobrazil ekonomický cost používania namiesto iba cash invoice momentu. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Application-consistent backup

Backup vytvorený tak, aby zachoval logicky konzistentný application state, napríklad po flushnutí buffers, filesystem freeze alebo koordinovanom database checkpoint-e. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## AWS Backup

Centralizovaná AWS služba na policy-driven backup, copy, retention, restore, monitoring a audit podporovaných resource types. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## AWS Backup Audit Manager

Capability na hodnotenie backup controls a generovanie compliance evidence pre coverage, frequency, retention, encryption, copies, Vault Lock a restore testing. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## AWS Backup Vault Lock

Ochranný mechanizmus presadzujúci immutable retention pravidlá backup vaultu v governance alebo compliance modeli podľa konfigurácie. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## AWS Budgets

AWS Cost Management capability na sledovanie cost, usage, commitment utilization alebo coverage voči definovaným thresholds s notifications a voliteľnými actions. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## AWS Cost Anomaly Detection

Capability používajúca modely na identifikovanie neobvyklých spend patterns podľa definovaného monitoru a alert subscription. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## AWS Cost Explorer

Analytická AWS Cost Management vrstva na filtrovanie, grouping, forecasting a analýzu cost a usage vrátane amortized views a optimization reports. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## AWS Cost Optimization Hub

Centralizovaná capability agregujúca a prioritizujúca cost-optimization opportunities naprieč AWS accounts a Regions. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## AWS Data Exports

AWS capability na pravidelný export detailných billing, cost, usage a related datasets do analytického storage a query workflowu. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## AWS Well-Architected Framework

Konzistentný review framework na hodnotenie workloadov podľa šiestich pilierov a vytváranie evidence-driven improvement plánu. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## AWS Well-Architected Tool

AWS služba na dokumentovanie workload reviews, lenses, risk issues, improvement plans, milestones a reports podľa Well-Architected Frameworku. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Backup plan — AWS

Policy expression určujúci schedule, windows, vault, lifecycle, retention, copy actions a ďalšie backup semantics pre priradené resources. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Backup vault — AWS

Logický container recovery points s vlastnou access policy, encryption, retention, lock a audit boundary. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Blended cost — AWS

Cost view používajúci pri niektorých consolidated-billing scenároch priemernú rate naprieč organization family. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Budget action — AWS

Voliteľná automatická action naviazaná na AWS Budget threshold, napríklad policy alebo bounded resource-control operácia podľa podporovaných možností. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Chargeback — FinOps

Interný model, ktorý finančne priraďuje cloud cost konkrétnemu tímu, produktu, cost centru alebo business ownerovi. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Clean-room recovery

Obnova do izolovaného a kontrolovaného prostredia pred production promotion, aby sa overila integrita a zabránilo opätovnému kompromitovaniu obnovených dát. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Cloud financial management

Disciplína merania, alokácie, plánovania, kontroly a optimalizácie cloud spendu podľa business value a operational trade-offov. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Continuous Well-Architected

Integrácia architektúrnych controls, review questions, operational evidence a improvement backlogu do priebežného delivery a operations lifecycle-u. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Continuous backup — AWS Backup

Backup model, ktorý pri podporovaných resources priebežne zachytáva zmeny a umožňuje point-in-time recovery v retention window. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

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

## Cross-account backup copy

Kópia recovery pointu do oddeleného AWS accountu na zníženie credential a administrative blast radiusu. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Cross-Region backup copy

Kópia recovery pointu do iného AWS Regionu pre regionálnu isolation a disaster-recovery model. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Evidence-driven review

Architektúrny review, v ktorom odpovede podporujú aktuálne configuration, telemetry, tests, policies, incidents a ďalšie overiteľné dôkazy. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## FinOps

Operating model spájajúci engineering, finance a business pri rozhodovaní o cloud value, cost, usage a trade-offoch. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## High-risk issue — Well-Architected

Významná odchýlka od Well-Architected best practices s relevantným security, reliability, operations, performance, cost alebo sustainability rizikom. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Improvement plan — Well-Architected

Prioritizovaný súbor konkrétnych remediation položiek s ownerom, target state-om a validation criteria po workload review. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Lens — Well-Architected

Sada questions, best practices a improvement guidance pre konkrétny architecture alebo industry domain. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Logically air-gapped vault — AWS Backup

Špeciálny backup vault s dodatočnou logical isolation a Vault Lock compliance ochranou pre ransomware a recovery use cases. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Milestone — Well-Architected

Snapshot stavu workload review-u v konkrétnom čase používaný na meranie zmeny risku a improvement progressu. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Operational Excellence pillar

Well-Architected pillar zameraný na efektívny development, operations insight, safe change a continuous improvement. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Performance Efficiency pillar

Well-Architected pillar zameraný na efektívny výber a používanie compute resources podľa workload requirements a technologického vývoja. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Point-in-time recovery — AWS Backup

Obnova podporovaného resource-u do konkrétneho času z continuous backup recovery pointu. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Realized savings

Úspora reálne overená po implementácii optimization change-u, nie iba estimated recommendation. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Recovery point — AWS Backup

Backup reprezentujúci obsah resource-u v konkrétnom čase spolu s lifecycle, encryption a recovery metadata. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Recovery-point age

Čas od vytvorenia posledného validného recovery pointu, používaný ako praktický signal voči RPO požiadavke. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Reliability pillar

Well-Architected pillar zameraný na správne a konzistentné fungovanie workloadu, capacity, change a failure management. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Restore testing — AWS Backup

Policy-driven pravidelné obnovenie recovery pointu do test targetu s následnou technical a application validation. Pozri [AWS Backup](docs/11-cloud-and-aws/aws-backup.md).

## Rightsizing

Úprava alebo odstránenie resource-u podľa reálneho utilization, performance, reliability a capacity modelu. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Security pillar — Well-Architected

Well-Architected pillar zameraný na identity, traceability, infrastructure protection, data protection, detection a incident response. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Showback — FinOps

Interné zobrazenie costu tímom alebo produktom bez priameho finančného preúčtovania. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Sustainability pillar

Well-Architected pillar zameraný na minimalizovanie environmentálneho dopadu workloadu cez demand, utilization, software, data a hardware efficiency. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).

## Total cost of ownership — TCO

Celkový ekonomický cost zahŕňajúci cloud spend, engineering, operations, licensing, support, migration a risk. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Unblended cost — AWS

Cost view zobrazujúci konkrétnu rate účtovanú za jednotlivé usage line items bez organization average. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Unit cost

Cloud cost prepočítaný na business jednotku, napríklad request, transakciu, build alebo aktívneho používateľa. Pozri [Cost management a FinOps](docs/11-cloud-and-aws/cost-management-finops.md).

## Workload boundary — Well-Architected

Explicitný scope komponentov, ľudí, procesov, dát a dependencies, ktoré spoločne poskytujú hodnotený business outcome. Pozri [Well-Architected Framework](docs/11-cloud-and-aws/well-architected-framework.md).
