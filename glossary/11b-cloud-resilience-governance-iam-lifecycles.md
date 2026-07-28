# AWS resilience, governance and IAM lifecycle glossary entries

## Capacity lifecycle subject

Versionovaná identita business demandu, workload unit, compute/data/dependency capacity, failure-domain inventory, scaling policy, metric contract a požadovaného business outcome-u. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Safe capacity

Maximálny throughput alebo concurrency, pri ktorom celý critical path spĺňa latency, reliability, downstream, cost a business-correctness contract; nie iba technický limit jednej compute vrstvy. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Serving-capacity realization

Prechod od desired capacity cez launched, healthy, registered a ready resources k reálnej kapacite prijímajúcej a správne dokončujúcej business operations. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Scaling signal contract

Definícia metric source-u, pracovnej jednotky, dimensions, aggregation windowu, freshness, no-data behavioru a očakávanej reakcie na zmenu kapacity. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Retry amplification loop — cloud capacity

Causal loop, v ktorom downstream saturation zvýši latency a retries, retry-inclusive metric vyžiada ďalší scale-out a nová kapacita ďalej zvyšuje pressure na rovnaký bottleneck. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Downstream capacity envelope

Bounded connections, throughput, quota alebo concurrency, ktorú môže upstream fleet bezpečne spotrebovať bez zrútenia dependency. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Scale-in drain contract

Sekvencia odstránenia resource-u z nového trafficu, dokončenia alebo odovzdania práce, business commit-u, evidence a až následnej termination. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Zonal capacity headroom

Compute, subnet IP, quota, egress, data a dependency kapacita zostávajúca po strate definovanej Availability Zone a počas replacement alebo rollout surge-u. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Capacity acceptance verdict

Closure dôkaz, že capacity zmena zvýšila successful business throughput, zachovala downstream budgets, bezpečný scale-in a definovaný failure-domain outcome bez forbidden duplicít alebo straty. Pozri [Scalability, elasticity a fault tolerance](docs/11-cloud-and-aws/scalability-elasticity-fault-tolerance.md).

## Business recovery subject

Exact business capability, primary/recovery account a Region, application/data/trust generations, RTO, RPO, minimálna capacity a forbidden outcomes použité na DR rozhodovanie. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Recovery-set manifest

Versionovaný inventár data checkpointov, transaction logs, IaC, artifacts, configuration, identities, KMS/PKI, DNS, external integration state, telemetry a runbookov potrebných na obnovu business capability. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Recovery authority

Explicitný owner a state-generation contract určujúci, kto smie deklarovať disaster, vybrať recovery point, povýšiť writer-a, otvoriť traffic a vykonať failback. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Application-consistent recovery point

Recovery point, v ktorom databázové checkpointy, logs, queue offsets a external-operation ledger patria k jednej definovanej business transaction boundary. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Clean trust generation

Po incidente novo vydaná a izolovaná generácia identities, credentials, certificates, keys a policies, ktorá nie je iba replikou potenciálne kompromitovaného primary state-u. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Disaster declaration boundary

Podmienky, čas a authority, pri ktorých incident prechádza z lokálneho HA recovery do explicitného DR procesu. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Traffic-reopen verdict — DR

Closure dôkaz, že restored state, single-writer fencing, clean credentials, external integrations, minimum capacity, telemetry a business transaction sú správne pred otvorením production trafficu. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Failback authority transfer

Riadený presun authoritative data a writer/traffic ownershipu z recovery prostredia späť do primary prostredia po synchronizácii, compatibility a single-writer verifikácii. Pozri [High availability a disaster recovery](docs/11-cloud-and-aws/high-availability-disaster-recovery.md).

## Governed account lifecycle subject

Exact AWS account ID, owner, OU path, baseline generation, SCP/RCP/declarative policy set, delegated administration, Regions a allowed/forbidden outcomes od account requestu po closure. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Account baseline generation

Versionovaná realizácia identity, logging, security services, network, DNS, KMS, backup, quota, tagging a budget controls v konkrétnom AWS account-e. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## OU placement generation

Aktuálna poloha accountu v Organizations hierarchy spolu s parent policy inheritance cestou a časom posledného move-u. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Effective organization policy

Výsledný SCP, RCP alebo declarative configuration stav vypočítaný z root, parent OU, child OU a account attachments podľa semantics daného policy typu. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Governance graph

Vzťahy medzi management accountom, OUs, member accounts, delegated administrators, cross-account roles, shared networks, log archives a organization policies, ktoré určujú reálny blast radius. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Account acceptance verdict

Dôkaz, že account je v správnej OU, má reconciled baseline, povolené workload/recovery operations fungujú a zakázané Region, audit-disable, public alebo external access paths zlyhávajú. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Canary OU

Obmedzený Organizations scope používaný na staged policy a baseline validation pred širším attachmentom na production OUs alebo root. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Quarantine capability envelope

Explicitná množina forensic, logging, backup, KMS a containment operations, ktoré musia zostať povolené aj pri silnom obmedzení kompromitovaného accountu. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## Delegated-administration subject

Service-specific organization capability viazaná na delegated account ID, role/trust generation, managed scope, audit a emergency revocation path. Pozri [AWS Organizations a accounts](docs/11-cloud-and-aws/aws-organizations-accounts.md).

## AWS request authorization subject

Exact caller account a session ARN, credential source, action, resource ARN, Region/endpoint, request context, applicable policy generations a požadovaný service/business outcome. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## Credential-source identity — AWS

Konkrétny SDK/CLI credential provider a vydaná credential/session generation, ktorú process skutočne použil na podpísanie requestu. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## Process-loaded AWS credential

Credential generation načítaná application procesom, ktorá sa môže líšiť od najnovšieho web-identity tokenu, environmentu alebo metadata credentialu dostupného na hoste. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## Assumed-role session subject

Konkrétna STS session identifikovaná session ARN, source identity, tags, policies, issue time a expiration; nie abstraktná IAM role. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## Effective permission graph — AWS

Reachable authorization paths od principal/session identity cez trust, identity/resource policies, permissions boundary, session policy, SCP/RCP, conditions a service-specific policies k exact action/resource verdictu. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## Permissions envelope — AWS

Policy vrstva, ktorá access sama neudeľuje, ale obmedzuje maximum candidate grants, napríklad permissions boundary, session policy, SCP alebo RCP. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## KMS authorization boundary

Kombinácia caller permissions, KMS key policy/grants, encryption context, Region/account a request conditions potrebná na cryptographic operation. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## Indirect IAM capability

Authority vznikajúca kombináciou zdanlivo úzkych permissions, napríklad `iam:PassRole` s vytvorením workloadu alebo edit policy/trust s následným assume-role pathom. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## Credential revocation verdict — AWS

Dôkaz, že starý access key, STS path alebo workload credential už nemôže úspešne vykonať forbidden request; nie iba fakt, že policy alebo Secret bol zmenený. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## Authorization closure — AWS

Positive a forbidden request tests, CloudTrail evidence a business verification, ktoré dokazujú správny effective permission graph po zmene alebo incidente. Pozri [IAM](docs/11-cloud-and-aws/iam.md).
