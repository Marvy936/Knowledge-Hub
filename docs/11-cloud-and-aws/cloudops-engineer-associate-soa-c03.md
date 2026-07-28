# AWS Certified CloudOps Engineer – Associate (SOA-C03)

AWS Certified CloudOps Engineer – Associate je associate-level certifikácia pre deployment, management a operations workloads na AWS. Od 30. septembra 2025 používa nový názov a exam code `SOA-C03`; nahradila AWS Certified SysOps Administrator – Associate `SOA-C02`. Certifikačný track v tomto repozitári nie je paralelná sada service definícií. Je to evidence-driven readiness lifecycle, ktorý prepája authoritative exam contract, hlavné Cloud/AWS kapitoly, praktické laby, troubleshooting drilly, timed reasoning a explicitný readiness verdict.

## 1. Dominantný model: od role contractu k readiness verdictu

```text
CloudOps role capability contract
→ exact exam-guide generation a domain/task inventory
→ authoritative knowledge mapping
→ practical evidence inventory
→ weighted gap model
→ targeted study, lab a troubleshooting remediation
→ timed simulation
→ error provenance a confidence analysis
→ readiness verdict
→ exam alebo ďalší remediation cycle
```

Cieľom nie je „prejsť všetky videá“ ani dosiahnuť jedno náhodné practice score. Kandidát musí vedieť zmeniť business alebo operational requirement na správny AWS control/data/recovery path, rozlíšiť konkurenčné možnosti a vysvetliť, prečo zvolená odpoveď spĺňa všetky constraints.

## 2. Exact certification subject

Readiness evidence musí byť viazaná na konkrétnu exam generation. Pre aktuálny track zapisuj minimálne:

```text
certification: AWS Certified CloudOps Engineer – Associate
exam code: SOA-C03
exam-guide revision: 1.1
publication date: 2026-06-01
practice source a version:
simulation date:
65-question set identity:
domain distribution:
time used:
score a confidence profile:
linked labs/drills:
```

Bez guide version a source identity môže starý SOA-C02 materiál vyzerať ako aktuálny dôkaz, hoci nezahŕňa dnešný scope containers, multi-account/multi-Region operations, širšiu automation, moderné security operations alebo aktuálne in-scope služby.

## 3. Aktuálny exam contract

Podľa oficiálnych AWS zdrojov má aktuálna skúška:

- exam code `SOA-C03`;
- associate level;
- 130 minút;
- 65 multiple-choice alebo multiple-response questions;
- 50 scored a 15 unscored questions, pričom unscored questions nie sú označené;
- scaled score od 100 do 1 000 a minimum passing score 720;
- intended candidate profile približne jeden rok deploymentu, managementu a operations AWS workloads;
- aktuálny exam-guide revision `1.1`, publikovaný 1. júna 2026.

Skúška nie je performance-based hands-on exam ako CKA. Absencia hands-on terminalu však nemení požadovanú schopnosť: scenario question často nemožno spoľahlivo vyriešiť bez reálneho porozumenia IAM evaluation, route pathu, health lifecycle-u, backup/restore semantics alebo telemetry evidence.

## 4. Domain contract a váhy

| Doména | Váha scored contentu | Hlavný capability outcome |
|---|---:|---|
| Monitoring, Logging, Analysis, Remediation, and Performance Optimization | 22 % | získať správny signal, vysvetliť performance/failure a bezpečne remediovať |
| Reliability and Business Continuity | 22 % | navrhnúť a prevádzkovať availability, scaling, backup, recovery a DR |
| Deployment, Provisioning, and Automation | 22 % | vytvárať a meniť resources opakovateľne, bezpečne a s rollback/recovery modelom |
| Security and Compliance | 16 % | vyhodnotiť identity, authorization, protection, audit a incident controls |
| Networking and Content Delivery | 18 % | realizovať a diagnostikovať packet, DNS, load-balancing a edge path |

Váha nie je iba študijný percentuálny plán. Každá domain question môže zasiahnuť viac vrstiev. Napríklad neúspešný Systems Manager run môže byť súčasne deployment/automation problém, IAM/KMS authorization problém a private-network endpoint problém.

## 5. Capabilities, nie service recognition

SOA-C03 overuje schopnosť:

1. identifikovať požadovaný business alebo operational outcome;
2. určiť scope a responsibility boundary;
3. zostaviť complete control, data alebo recovery path;
4. vybrať managed capability, ktorá spĺňa explicitné constraints;
5. rozlíšiť configured resource od effective runtime behavior;
6. diagnostikovať zlyhanie cez evidence, nie cez service keyword;
7. vyhodnotiť security, reliability, operational-effort a cost trade-off;
8. zvoliť containment, remediation a validation, ktoré nezväčšia blast radius.

Preto je odpoveď „použiť CloudWatch“ neúplná. Kandidát musí vedieť, či otázka potrebuje metric, Logs Insights query, metric filter, alarm evaluation, EventBridge event, CloudTrail audit, Config state history alebo service-specific log.

## 6. Authoritative knowledge mapping

Hlavná Cloud/AWS sekcia tvorí jeden connected Atlas Payments subject `CAP-PAY-42`. Exam track nad ňou nevytvára nové konkurenčné definície. Mapuje task statements na už vysvetlené lifecycle-y.

### Domain 1 — Monitoring, remediation a performance

Najdôležitejšie zdroje:

- [CloudWatch a CloudTrail](cloudwatch-cloudtrail.md);
- [Systems Manager](systems-manager.md);
- [EC2 a Auto Scaling](ec2-auto-scaling.md);
- [Lambda](lambda.md);
- [ECS a EKS](ecs-eks.md);
- [Cost management a FinOps](cost-management-finops.md);
- sekcia [Observability](../12-observability/README.md).

Kandidát má vedieť prejsť od operational question cez exact signal identity a delivery path po alarm/remediation outcome. Green dashboard bez správnej dimension, retention alebo action pathu nie je evidence.

### Domain 2 — Reliability a business continuity

Najdôležitejšie zdroje:

- [Scalability, elasticity a fault tolerance](scalability-elasticity-fault-tolerance.md);
- [High availability a disaster recovery](high-availability-disaster-recovery.md);
- [Elastic Load Balancing](elastic-load-balancing.md);
- [S3, EBS a EFS](s3-ebs-efs.md);
- [RDS](rds.md);
- [Route 53 a CloudFront](route53-cloudfront.md);
- [AWS Backup](aws-backup.md).

Kandidát musí rozlíšiť availability, durability, replication, historical recovery, RPO, RTO a business reconciliation. Multi-AZ neznamená ochranu pred logical corruption a completed restore job neznamená recoverable service.

### Domain 3 — Deployment, provisioning a automation

Najdôležitejšie zdroje:

- sekcia [Infrastructure as Code and Configuration Management](../07-infrastructure-as-code-and-configuration-management/README.md);
- [EC2 a Auto Scaling](ec2-auto-scaling.md);
- [ECS a EKS](ecs-eks.md);
- [Lambda](lambda.md);
- [Systems Manager](systems-manager.md);
- [AWS Organizations a accounts](aws-organizations-accounts.md).

SOA-C03 zahŕňa aj CloudFormation-specific reasoning. Kandidát musí rozumieť stack/change-set/update/rollback/drift/StackSets lifecycle-u aj keď hlavný IaC track používa Terraform.

### Domain 4 — Security a compliance

Najdôležitejšie zdroje:

- [Shared responsibility model](shared-responsibility-model.md);
- [AWS Organizations a accounts](aws-organizations-accounts.md);
- [IAM](iam.md);
- [Security Groups a Network ACLs](security-groups-network-acls.md);
- [KMS a Secrets Manager](kms-secrets-manager.md);
- [CloudWatch a CloudTrail](cloudwatch-cloudtrail.md);
- sekcia [Security and Identity](../13-security-and-identity/README.md).

Kandidát má vedieť rozbaliť effective permission verdict cez identity/resource policies, trust, session, boundaries, SCP/RCP, KMS a endpoint conditions. Pridanie broad allow nie je validná diagnostika.

### Domain 5 — Networking a content delivery

Najdôležitejšie zdroje:

- [VPC, subnets a route tables](vpc-subnets-route-tables.md);
- [Internet Gateway a NAT Gateway](internet-gateway-nat-gateway.md);
- [Security Groups a Network ACLs](security-groups-network-acls.md);
- [Elastic Load Balancing](elastic-load-balancing.md);
- [Route 53 a CloudFront](route53-cloudfront.md);
- [Public, private a hybrid cloud](public-private-hybrid-cloud.md).

Kandidát musí zostaviť celý request a return path. Samotná existencia IGW, NAT Gateway alebo Security Group rule nepreukazuje connectivity.

## 7. Practical evidence inventory

Knowledge coverage je iba jedna vrstva readiness. Pre každú domain udržuj evidence inventory:

```text
authoritative chapters completed
→ least one bounded hands-on lab
→ least one fault-injection drill
→ CLI/API evidence preserved
→ positive a forbidden outcome verified
→ timed scenario questions completed
→ high-confidence wrong answers remediated
```

Practical evidence má obsahovať exact account/Region, resource generations, fault, observations, remediation, validation a cleanup. Screenshot výslednej zelenej konzoly bez pathu a failure diagnosis nie je plný dôkaz.

## 8. Weighted gap model

Jednoduchý celkový priemer môže skryť nebezpečný domain gap. Readiness model preto sleduje aspoň štyri osi:

- **knowledge accuracy** — správnosť odpovedí podľa domain a task statementu;
- **reasoning fidelity** — schopnosť pomenovať outcome, constraints, scope a complete path;
- **operational evidence** — laby a drilly s hard validation;
- **time stability** — výkon bez time collapse pri 130-minútovej simulácii.

Príklad:

```text
overall practice score: 82 %
Domain 1: 88 %
Domain 2: 86 %
Domain 3: 84 %
Domain 4: 58 %
Domain 5: 87 %
high-confidence wrong answers: 7
unfinished questions: 0
```

Čistý priemer vyzerá priaznivo. Domain 4 však obsahuje high-confidence nesprávne modely o KMS key policy, SCP a cross-account trust. To nie je malá štatistická odchýlka; je to systematický authorization risk, ktorý môže kontaminovať aj deployment, backup a networking questions.

## 9. Worked readiness failure: vysoké skóre, slabý capability contract

Kandidát absolvuje tri 65-question practice sets:

- `Set A`: 80 % za 117 minút;
- `Set B`: 84 % za 125 minút;
- `Set C`: 82 % za 119 minút.

Na prvý pohľad vyzerá pripravený. Review odpovedí však ukáže:

1. sedem wrong + high-confidence odpovedí;
2. pri KMS `AccessDenied` kontroluje iba IAM policy a ignoruje key policy a grant;
3. completed AWS Backup job považuje za dôkaz application recovery;
4. pri private-subnet connectivity vyberá NAT Gateway aj pre private S3 traffic, hoci explicitný constraint požaduje bez internet pathu a lowest recurring cost;
5. správne odpovede v týchto témach vznikli iba tam, kde poznal presnú formuláciu z practice banky;
6. žiadny zodpovedajúci lab alebo drill ešte nevykonal.

### Competing readiness hypotheses

- **H1 — kandidát je pripravený; chyby sú náhodné:** celkové skóre a stabilný čas to čiastočne podporujú.
- **H2 — practice source je príliš podobný naučeným otázkam:** správne odpovede bez explanation a opakujúce sa phrasing patterns to podporujú.
- **H3 — existuje systematický authorization/recovery model gap:** high-confidence wrong odpovede a chýbajúce hands-on evidence to podporujú.
- **H4 — problém je iba exam anxiety/time:** časový budget túto hypotézu oslabuje.

Diskriminačný test nie je ďalší set z rovnakej banky. Kandidát dostane nový cross-account encrypted-backup incident a musí bez možností:

```text
identifikovať caller a exact key
→ rozbaliť IAM/SCP/key-policy/grant path
→ nájsť clean recovery point
→ vytvoriť isolated restore
→ overiť business invariant
→ vysvetliť forbidden broad-access fix
```

Test zlyhá v authorization aj recovery kroku. Správny verdict je **not ready**, hoci posledný practice score bol 82 %.

### Remediation

1. znovu prejsť IAM, KMS/Secrets a AWS Backup lifecycle-y;
2. vykonať cross-account KMS a isolated-restore lab;
3. absolvovať príslušné troubleshooting drilly;
4. vytvoriť error cards pre každý high-confidence wrong model;
5. použiť novú, nezávislú timed simulation;
6. označiť ready až po stabilnom score, explainability a practical evidence.

## 10. Error provenance

Po každom sete klasifikuj chybu podľa mechanizmu:

- knowledge gap;
- stale exam-version assumption;
- missed qualifier alebo negative constraint;
- wrong scope/account/Region;
- incomplete control/data/recovery path;
- policy-evaluation error;
- availability/backup/DR confusion;
- service recognition bez outcome reasoning;
- changed answer without new evidence;
- time-budget failure;
- high-confidence wrong mental model.

Posledná kategória má najvyššiu prioritu. Wrong + low confidence je viditeľná medzera. Wrong + high confidence je chybný model, ktorý kandidát aktívne používa aj mimo skúšky.

## 11. Readiness state machine

```text
Not mapped
→ Knowledge mapped
→ Practiced
→ Timed
→ Evidence reviewed
→ Ready
```

Prechod nie je automatický:

- **Knowledge mapped** vyžaduje current guide-to-chapter map;
- **Practiced** vyžaduje labs a fault drills, nie iba otázky;
- **Timed** vyžaduje full-length simulation;
- **Evidence reviewed** vyžaduje error provenance a domain gaps;
- **Ready** vyžaduje splnenie acceptance contractu.

Ak sa zmení exam guide, významne sa zmení AWS capability alebo kandidát dlhšie nepraktizuje, readiness sa vracia do skoršieho stavu.

## 12. Readiness acceptance contract

Pred skúškou má kandidát vedieť preukázať:

- current exam guide revision a domain weights;
- viac nezávislých full-length simulations bez time collapse;
- stabilný celkový výkon bez kritického domain floor gapu;
- explanation správnych odpovedí aj distractorov;
- remediation všetkých recent high-confidence wrong modelov;
- hands-on evidence pre IAM, networking, compute, observability, automation, backup a recovery;
- schopnosť pracovať cez AWS CLI/API evidence, nie iba podľa console layoutu;
- pozitívnu aj negatívnu validation v laboch;
- cost-safe cleanup discipline;
- odmietnutie exam dumps a zachovanie exam integrity.

AWS score report je po skúške autoritatívny pass/fail verdict. Practice readiness je interný risk decision, nie predikcia garantujúca výsledok.

## 13. Study a review cadence

Praktický cyklus:

```text
current guide check
→ one domain knowledge block
→ one lab
→ one troubleshooting drill
→ 20–35 question timed set
→ error provenance
→ targeted remediation
→ periodic 65-question simulation
```

Po každej AWS guide revision over:

- zmenené skills;
- in-scope a out-of-scope services;
- nové service examples;
- či existujúce kapitoly a laby stále pokrývajú task statements;
- či staré practice materials nepoužívajú retired assumptions.

## 14. Praktický track v repozitári

- [CloudOps domain review a timed reasoning](cloudops-domain-review-timed-reasoning.md) — decision protocol pre question subject, constraints a answer selection;
- [CloudOps hands-on labs](cloudops-hands-on-labs.md) — cost-safe experiments produkujúce operational evidence;
- [CloudOps troubleshooting drills](cloudops-troubleshooting-drills.md) — subject-bound diagnosis, containment, recovery a closure;
- [Praktické AWS CloudOps laby](../../labs/aws-cloudops/README.md) — vykonávacie zadania;
- [AWS CloudOps troubleshooting scenáre](../../troubleshooting/aws-cloudops/README.md) — fault index.

## 15. Anti-patterny

### Starý SOA-C02 blueprint ako autorita

Service knowledge môže byť užitočná, ale scope a task weighting musia vychádzať z current SOA-C03 guide-u.

### Practice score bez source identity

Nie je jasné, či set zodpovedá current blueprintu, či obsahuje leaks alebo či opakuje naučené questions.

### Overall average bez domain floor

Silné networking skóre môže skryť systematický security alebo recovery gap.

### Correct answer bez explanation

Môže ísť o recognition alebo guessing, nie stabilný capability model.

### Iba video kurz bez operational evidence

Vytvára vocabulary familiarity, ale nie schopnosť diagnostikovať path a recovery boundary.

### Memorovanie exam dumps

Porušuje exam integrity a nevytvára prenositeľnú CloudOps schopnosť.

### Readiness ako jednorazový stav

Guide, services aj vlastná praktická zručnosť sa menia. Readiness potrebuje generation a review date.

## 16. Kontrolné otázky

1. Čo tvorí exact SOA-C03 readiness subject?
2. Prečo overall practice score nestačí?
3. Ako sa líši knowledge accuracy, reasoning fidelity a operational evidence?
4. Prečo je wrong + high confidence kritickejšie než wrong + low confidence?
5. Ako sa current exam guide mapuje na authoritative kapitoly?
6. Prečo completed lab bez forbidden-outcome testu nie je plný evidence?
7. Kedy sa readiness state musí vrátiť do skoršej fázy?
8. Ako rozlíšiš stale SOA-C02 assumption od current SOA-C03 contractu?
9. Čo musí obsahovať readiness acceptance contract?
10. Prečo practice readiness negarantuje AWS pass verdict?

## Glossary impact

Relevantné pojmy: SOA-C03 capability contract, exam-guide generation, certification readiness subject, authoritative knowledge mapping, practical evidence inventory, weighted domain gap, domain floor, high-confidence wrong model, error provenance, readiness state machine, readiness acceptance contract a exam-version staleness.

## Oficiálne zdroje

- [AWS Certified CloudOps Engineer – Associate](https://aws.amazon.com/certification/certified-cloudops-engineer-associate/)
- [SOA-C03 exam guide](https://docs.aws.amazon.com/aws-certification/latest/sysops-administrator-associate-03/sysops-administrator-associate-03.html)
- [SOA-C03 revisions](https://docs.aws.amazon.com/aws-certification/latest/sysops-administrator-associate-03/soa-03-revisions.html)
- [Comparison of SOA-C02 and SOA-C03](https://docs.aws.amazon.com/aws-certification/latest/sysops-administrator-associate-03/sysops-administrator-associate-03-comparison.html)
- [In-scope AWS services](https://docs.aws.amazon.com/aws-certification/latest/sysops-administrator-associate-03/soa-03-in-scope-services.html)
- [Out-of-scope AWS services](https://docs.aws.amazon.com/aws-certification/latest/sysops-administrator-associate-03/soa-03-out-of-scope-services.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Cost management a FinOps](cost-management-finops.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: CloudOps domain review a timed reasoning →](cloudops-domain-review-timed-reasoning.md)
<!-- KNOWLEDGE-NAVIGATION:END -->