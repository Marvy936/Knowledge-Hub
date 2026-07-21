# AWS identity, networking and CloudOps glossary entries

## AssumeRole — AWS STS

AWS STS operation, ktorou oprávnený principal prevezme IAM role a získa dočasnú role session s expiration, session identity a effective permissions. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## AWS Certified CloudOps Engineer – Associate

Associate-level AWS certifikácia overujúca deployment, management a operations workloads na AWS v oblastiach monitoring/remediation, reliability, automation, security a networking. Pozri [SOA-C03 guide](docs/11-cloud-and-aws/cloudops-engineer-associate-soa-c03.md).

## AWS CloudOps troubleshooting drill

Časovo obmedzený AWS fault-injection scenár s jednou známou primárnou chybou, evidence pathom, minimálnou remediation, hard validation a cleanupom. Pozri [CloudOps troubleshooting drills](docs/11-cloud-and-aws/cloudops-troubleshooting-drills.md).

## AWS sandbox account

Izolovaný AWS account určený na laby a experimenty s budget guardrails, bez production dát a s explicitným cleanup lifecycle. Pozri [CloudOps hands-on labs](docs/11-cloud-and-aws/cloudops-hands-on-labs.md).

## CloudOps domain gap map

Mapovanie aktuálnych SOA-C03 task statements na existujúce kapitoly, služby, hands-on laby, troubleshooting drilly a zostávajúce vedomostné medzery. Pozri [SOA-C03 guide](docs/11-cloud-and-aws/cloudops-engineer-associate-soa-c03.md).

## CloudOps timed reasoning

Tréning riešenia AWS scenario questions pod časovým limitom cez outcome, constraints, scope, responsibility boundary a operational trade-off. Pozri [CloudOps domain review a timed reasoning](docs/11-cloud-and-aws/cloudops-domain-review-timed-reasoning.md).

## Control-plane failure — AWS

Zlyhanie AWS API alebo management/configuration operácie, pri ktorom môže existujúci workload data plane naďalej fungovať. Pozri [CloudOps domain review a timed reasoning](docs/11-cloud-and-aws/cloudops-domain-review-timed-reasoning.md).

## Data-plane failure — AWS

Zlyhanie reálneho workload trafficu, request processingu, storage I/O alebo DNS/network cesty napriek potenciálne funkčnému AWS management API. Pozri [CloudOps domain review a timed reasoning](docs/11-cloud-and-aws/cloudops-domain-review-timed-reasoning.md).

## Egress-only Internet Gateway — AWS

VPC component poskytujúci outbound-initiated IPv6 internet connectivity bez všeobecného unsolicited inbound pathu. Pozri [Internet Gateway a NAT Gateway](docs/11-cloud-and-aws/internet-gateway-nat-gateway.md).

## Elastic network interface — ENI

Zonálny AWS network object nesúci private IP addresses, Security Groups, MAC a attachment identity pre EC2 a viaceré managed services. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## Explicit deny — IAM

Policy statement s `Effect: Deny`, ktorý pre applicable request prevažuje nad explicitnými allows v ostatných vyhodnocovaných policy vrstvách. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## Gateway endpoint — AWS

VPC endpoint integrovaný do route tables pre podporované AWS služby, typicky S3 alebo DynamoDB, bez interface-endpoint ENI modelu. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## IAM Access Analyzer

AWS IAM capability na analýzu external accessu, policy validation a vybrané unused-access alebo policy-generation workflows. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## IAM Identity Center

AWS služba pre centralizovaný workforce access, permission sets a federované temporary sessions do viacerých AWS accounts. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## IAM principal

Autentifikovaná alebo identifikovateľná AWS request identity, napríklad root user, IAM user, role session, federated principal alebo service principal. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## IAM role

AWS identity s trust policy a permissions policy modelom, ktorú principal preberá a používa cez temporary session credentials. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## IAM role trust policy

Resource-based policy role určujúca, ktoré principals a za akých conditions môžu role assume-nuť. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## IAM session policy

Policy odovzdaná pri vytváraní temporary session, ktorá môže zúžiť, ale nie rozšíriť permissions nad role a ostatné guardrails. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## Identity-based policy — AWS

IAM policy pripojená k userovi, group alebo role, ktorá povoľuje alebo denyuje actions nad resources podľa request contextu. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## Implicit deny — IAM

Predvolený authorization výsledok, keď request nemá applicable explicit allow alebo neprejde potrebnými policy boundaries. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## Interface endpoint — AWS

PrivateLink-based VPC endpoint vytvárajúci ENIs s private IPs v zvolených subnetoch a voliteľným private DNS modelom. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## Internet Gateway — AWS

Horizontálne škálovaný a vysoko dostupný VPC component poskytujúci route target pre internet-routable IPv4 a IPv6 traffic. Pozri [Internet Gateway a NAT Gateway](docs/11-cloud-and-aws/internet-gateway-nat-gateway.md).

## Isolated subnet — AWS

Subnet bez všeobecného inbound internet pathu aj bez general outbound internet pathu; môže používať iba explicitné private connectivity targets. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## Longest prefix match — AWS routing

Route selection pravidlo, pri ktorom VPC router vyberie matching route s najšpecifickejším destination prefixom. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## Main route table — AWS

Predvolená VPC route table, ktorú implicitne používajú subnety bez explicitnej asociácie s custom route table. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## NAT port exhaustion — AWS

Stav, pri ktorom NAT path nemá dostatok dostupných source-port mappings pre veľký počet concurrent connections, často koncentrovaných na rovnaký destination tuple. Pozri [Internet Gateway a NAT Gateway](docs/11-cloud-and-aws/internet-gateway-nat-gateway.md).

## Network Access Analyzer — AWS

VPC analysis capability na identifikáciu network paths, ktoré spĺňajú alebo porušujú definované access requirements. Pozri [Security Groups a Network ACLs](docs/11-cloud-and-aws/security-groups-network-acls.md).

## Network ACL — AWS

Subnet-level stateless ordered allow/deny packet filter, pri ktorom prvé matching rule number určuje výsledok a request aj return path potrebujú explicitné pravidlá. Pozri [Security Groups a Network ACLs](docs/11-cloud-and-aws/security-groups-network-acls.md).

## Permissions boundary — IAM

IAM policy nastavujúca maximálny permissions envelope, ktorý identity-based policies môžu udeliť konkrétnemu userovi alebo role. Sama permissions neudeľuje. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## Prefix list — AWS VPC

Spravovaný zoznam CIDR prefixes použiteľný v route tables alebo Security Group rules na zníženie duplicity a centralizáciu network identity. Pozri [Security Groups a Network ACLs](docs/11-cloud-and-aws/security-groups-network-acls.md).

## Private NAT Gateway — AWS

NAT Gateway bez Elastic IP určený na private network address translation cez podporované private routing targets, nie na priamy internet egress cez IGW. Pozri [Internet Gateway a NAT Gateway](docs/11-cloud-and-aws/internet-gateway-nat-gateway.md).

## Private subnet — AWS

Subnet bez priameho inbound internet pathu, ktorý môže používať NAT, VPC endpoints, proxy alebo hybrid connectivity pre outbound alebo private access. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## Public NAT Gateway — AWS

Zonálny managed NAT service vytvorený v public subnet-e s Elastic IP, používaný typicky pre outbound IPv4 connectivity private subnetov. Pozri [Internet Gateway a NAT Gateway](docs/11-cloud-and-aws/internet-gateway-nat-gateway.md).

## Public subnet — AWS

Subnet s route pathom na Internet Gateway; konkrétny resource potrebuje ešte public addressing a security/application konfiguráciu, aby bol internet reachable. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## Reachability Analyzer — AWS

VPC configuration-analysis tool modelujúci network path medzi source a destination a identifikujúci blocking component. Pozri [Security Groups a Network ACLs](docs/11-cloud-and-aws/security-groups-network-acls.md).

## Resource-based policy — AWS

Policy uložená pri resource-e, ktorá môže priamo určovať allowed alebo denied principals, actions a conditions, vrátane cross-account accessu. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## Route propagation — AWS

Automatické pridávanie routes z podporovaného gateway alebo dynamic routing source-u do route table podľa nakonfigurovaného connectivity modelu. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## Security Group — AWS

Stateful allow-only firewall priradený k ENI alebo podporovanému resource-u; return traffic pre tracked connection je povolený connection trackingom. Pozri [Security Groups a Network ACLs](docs/11-cloud-and-aws/security-groups-network-acls.md).

## Security Group reference — AWS

Security Group rule používajúca inú SG ako source alebo destination workload identity podľa podporovaného connectivity modelu namiesto statického CIDR. Pozri [Security Groups a Network ACLs](docs/11-cloud-and-aws/security-groups-network-acls.md).

## Service-linked role — AWS IAM

IAM role previazaná s konkrétnou AWS službou, ktorej trust a permissions lifecycle je definovaný danou službou. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## SOA-C03

Aktuálny exam code AWS Certified CloudOps Engineer – Associate s piatimi doménami a váhami 22 %, 22 %, 22 %, 16 % a 18 %. Pozri [SOA-C03 guide](docs/11-cloud-and-aws/cloudops-engineer-associate-soa-c03.md).

## Source/destination check — AWS

EC2 network-interface kontrola vyžadujúca, aby instance bola source alebo destination trafficu; network appliance alebo NAT instance ju môže potrebovať vypnúť. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## Temporary credentials — AWS

Časovo obmedzená sada access key ID, secret access key a session tokenu vydaná AWS STS pre role alebo federated session. Pozri [IAM](docs/11-cloud-and-aws/iam.md).

## Transit Gateway — AWS

Regionálny network transit hub prepájajúci viac VPCs a hybrid networks cez attachments, associations, propagations a vlastné route tables. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## VPC Flow Logs

AWS telemetry zachytávajúca metadata IP flows pre VPC, subnet alebo ENI scope a podporujúca network path a accept/reject analýzu bez application payloadu. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## VPC peering

Private non-transitive routing connection medzi dvoma VPCs s explicitnými routes, non-overlapping CIDRs a security/DNS konfiguráciou na oboch stranách. Pozri [VPC, subnets a route tables](docs/11-cloud-and-aws/vpc-subnets-route-tables.md).

## `iam:PassRole`

Citlivá IAM action umožňujúca principalu odovzdať role AWS službe; musí byť obmedzená na presné roles a destination services. Pozri [IAM](docs/11-cloud-and-aws/iam.md).
