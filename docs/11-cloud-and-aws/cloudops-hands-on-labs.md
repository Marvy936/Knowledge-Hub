# CloudOps hands-on labs

SOA-C03 nie je hands-on performance exam, ale scenario reasoning bez operational experience ľahko zamieňa configured resource za effective capability. CloudOps lab preto nie je návod „klikni a vytvor“. Je to bounded experiment, ktorý začína explicitným outcome a failure hypothesis, vytvára versionovaný AWS subject, zachytáva observation evidence, vkladá kontrolovaný fault, vykonáva minimálnu remediation, overuje allowed aj forbidden outcomes a končí preukázaným cleanupom.

## 1. Dominantný model: evidence-producing lab lifecycle

```text
learning/business outcome a failure hypothesis
→ sandbox, identity, budget a expiry guardrails
→ exact lab generation a expected resource manifest
→ architecture/control/data/recovery path
→ bounded provisioning
→ baseline a evidence inventory
→ controlled fault injection
→ competing hypotheses a discriminating observations
→ minimal remediation
→ technical, security a business validation
→ cleanup a cost-residue verification
→ evidence review a replay decision
```

Resource, ktorý po lab-e „funguje“, je iba časť výsledku. Plný lab outcome zahŕňa aj vysvetlený failure mechanism, zachovaný audit trail, forbidden-path test, odstránené resources a potvrdenie, že sa nevytvoril neočakávaný recurring cost.

## 2. Exact lab subject

Pred provisioningom vytvor lab manifest:

```text
lab ID a generation:
SOA-C03 domain/task:
learning outcome:
allowed outcomes:
forbidden outcomes:
failure hypothesis:
AWS account/organization:
Region a AZs:
caller/session identity:
IaC/CLI source commit:
resource-name prefix:
expected resource inventory:
expected maximum duration:
expected cost drivers a budget:
ExpiresAt:
evidence destinations:
cleanup owner a procedure:
```

Bez generation identity sa po viacerých pokusoch miešajú staré resources, CloudTrail events, metrics a costs. Potom nie je možné rozhodnúť, či evidence patrí k aktuálnej konfigurácii.

## 3. Sandbox a financial safety boundary

Použi samostatný sandbox alebo training account bez production dát a production trust paths. Minimálny guardrail contract:

- federated alebo temporary access s MFA;
- explicitný account a Region v každom command-e alebo profile;
- budget a billing notifications;
- resource prefix a tags `Owner`, `Purpose`, `LabId`, `Generation`, `ExpiresAt`;
- žiadne permanentné broad access keys;
- žiadne production secrets, snapshots alebo customer datasets;
- bounded service quotas a concurrency, ak ich lab môže spotrebovať;
- vopred definovaný cleanup graph;
- po lab-e cost a orphan-resource review.

AWS Budget nie je real-time hard cap. Guardrail preto musí kombinovať budget signal, obmedzené permissions, quotas, TTL cleanup a priebežné sledovanie drahých resources ako NAT Gateway, RDS, load balancers, public IPv4, provisioned IOPS alebo cross-Region transfer.

## 4. Preflight: cost a blast-radius estimate

Pred spustením si polož:

1. Ktoré resources účtujú za čas existence aj bez trafficu?
2. Ktoré resources vytvárajú per-request, per-GB alebo cross-AZ/Region cost?
3. Môže autoscaling, retry alebo log loop nekontrolovane rásť?
4. Môže fault injection zablokovať cleanup identity alebo KMS key?
5. Existuje recovery cesta bez broad administrator escalation?
6. Ktoré resources prežijú parent stack deletion pre retention/deletion policy?

Preflight výsledok je decision: spustiť, zmenšiť, nahradiť lacnejším emulovaným variantom alebo lab nevykonať v danom account-e.

## 5. Architecture a evidence plan

Pred provisioningom nakresli minimálne tri vrstvy:

### Control plane

```text
caller/session
→ API/IaC engine
→ IAM/SCP/resource/KMS policies
→ resource creation/update
→ service events a CloudTrail
```

### Data plane

```text
client/source
→ DNS/route/security/listener
→ workload process
→ dependency/storage
→ response/business outcome
```

### Recovery a validation plane

```text
fault/failed generation
→ containment
→ last-known-good alebo authoritative desired state
→ replacement/restore
→ allowed outcome
→ forbidden outcome
→ adjacent cohort
```

Ku každému observation pointu priraď evidence command, log, metric alebo API field ešte pred fault injection. Inak sa po incidente ľahko zbiera iba to, čo podporuje prvú hypotézu.

## 6. Baseline contract

Fault možno vložiť až po preukázanom baseline-e. Baseline musí potvrdiť:

- exact caller/account/Region;
- expected resources a generations existujú;
- control-plane operations fungujú;
- data-plane request prejde;
- telemetry a audit delivery sú queryable;
- security negative tests zlyhávajú správnym spôsobom;
- initial cost drivers zodpovedajú manifestu;
- cleanup command bol aspoň dry-run alebo dependency-review spôsobom overený.

Ak baseline nie je green, fault injection nemá jednoznačný causal význam.

## 7. Fault injection contract

Fault je jedna zámerná, versionovaná zmena s očakávaným mechanismom:

```text
fault ID:
source generation:
mutation:
expected affected scope:
expected user/business symptom:
expected observation points:
safety abort condition:
reset/recovery path:
```

Začni jednou známou chybou. Náhodná kombinácia route, SG, IAM a application faults nevytvára kvalitný learning signal; vytvára neidentifikovateľný chaos.

Bezpečné príklady:

- zmeniť target-group health path na neexistujúcu cestu;
- odstrániť jednu explicitnú route;
- zúžiť Security Group source na nesprávnu SG;
- zastaviť SSM Agent;
- zmeniť metric dimension;
- odobrať exact KMS permission v sandbox key policy;
- zmeniť backup-selection tag;
- nasadiť nekompatibilnú CloudFormation property a pozorovať rollback.

## 8. Diagnosis discipline

Po symptóme okamžite neresetuj lab. Najprv:

1. potvrď timeline a affected cohort;
2. zachovaj volatile evidence;
3. pomenuj aspoň dve plausible hypotheses;
4. vyber observation, ktorý ich odlíši;
5. identifikuj exact failed boundary;
6. až potom vykonaj najmenšiu bezpečnú remediation.

Lab bez hypotéz trénuje command recall, nie troubleshooting.

## 9. Worked composite lab: ALB/Auto Scaling health-generation mismatch

### Learning outcome

Atlas Payments status API má bežať ako immutable EC2 fleet za ALB v dvoch AZ. Kandidát musí preukázať launch-template/ASG/target-group lifecycle, telemetry, failure diagnosis, safe recovery a cleanup bez inbound SSH.

### Exact subject

```text
lab ID: SOA-LAB-ALB-017
generation: g3
account: sandbox-cloudops
Region: eu-central-1
release: status-api 2.4.0
AMI: ami-status-2.4.0
launch template version: 7
ASG: atlas-status-lab-g3
ALB listener: HTTPS :443
expected process port: 8080
expected readiness path: /readyz
ExpiresAt: same day + 4 hours
```

### Architecture

```text
client
→ ALB listener/TLS
→ target group port 8080
→ EC2 process /readyz
→ static in-memory status response

operator
→ federated session
→ Systems Manager Session/Run Command
→ no inbound SSH

metrics/logs
→ CloudWatch
API changes
→ CloudTrail
```

Použi pre-baked AMI alebo malý deterministic bootstrap. Aplikácia nesmie závisieť od production database ani providerov.

### Baseline

Preukáž:

- dva healthy targets v dvoch AZ;
- repeated HTTPS requests cez ALB vracajú release `2.4.0`;
- direct internet access na instances neexistuje;
- Session Manager funguje bez inbound management portu;
- target response time a unhealthy-host metrics sú viditeľné;
- CloudTrail obsahuje create/update operations;
- ASG nahradí jednu zámerne terminated instance bez business interruption.

### Fault generation

Vytvor target-group configuration generation `tg-g4`, ktorá zmení health path z `/readyz` na `/healthz`. Aplikácia túto route neposkytuje.

Očakávaný mechanismus:

```text
ALB health probe /healthz
→ application 404
→ target health transitions unhealthy
→ ALB vyradí targets z eligibility
→ client dostane 503
→ ASG môže začať replacement loop podľa health integration
```

### Competing hypotheses

- **H1 — application process nebeží:** vysvetľuje health failure aj client outage.
- **H2 — target SG alebo port blokuje ALB:** vysvetľuje timeout health reason.
- **H3 — health-path generation nezodpovedá application contractu:** vysvetľuje HTTP 404 pri lokálne funkčnom process-e.
- **H4 — ALB listener alebo DNS smeruje na nesprávny target group:** vysvetľuje traffic na inú generation.

### Discriminating evidence

1. `describe-target-health` ukáže health reason spojený s response code, nie connection timeout;
2. SSM `curl http://localhost:8080/readyz` vráti `200`;
3. SSM `curl http://localhost:8080/healthz` vráti `404`;
4. Security Group a Flow Logs neukazujú reject;
5. listener rule ukazuje očakávaný target-group ARN;
6. CloudTrail/config diff ukáže presnú zmenu health pathu.

H3 je podporená; H1, H2 a H4 sú diskriminované.

### Containment a recovery

Ak ASG používa ELB health replacement, dočasne zastav destructive replacement loop alebo obnov dostatočnú healthy capacity podľa runbooku. Potom authoritative recovery vytvorí novú target-group configuration generation s `/readyz`; nejde o otvorenie SG, vypnutie health checks ani ručné označenie targets za zdravé.

### Hard validation

Allowed outcomes:

- oba targets sa vrátia do `healthy`;
- client requests vracajú `2.4.0`;
- replacement instance prejde bootstrap aj readiness;
- CloudWatch alarm sa vráti do očakávaného stavu;
- druhý reconciliation/instance replacement nevytvorí regresiu.

Forbidden outcomes:

- instances nemajú public inbound path;
- port 8080 nie je otvorený pre internet CIDR;
- starý `/healthz` contract nie je skrytý broad success matcherom;
- ASG neostáva v replacement loop-e;
- neprežijú manuálne snowflake úpravy na instances.

### Cleanup a cost closure

Odstráň v dependency poradí ALB/listeners/target groups, ASG, launch template, instances, log groups podľa retention contractu, VPC endpoints alebo NAT resources vytvorené labom, IAM lab roles a test DNS records. Over:

- žiadny running/stopped EC2 subject s `LabId`;
- žiadny load balancer alebo target group;
- žiadne unattached EBS volumes, EIPs alebo ENIs;
- žiadne recurring alarms/subscriptions;
- expected retained CloudTrail evidence;
- nasledujúci cost dataset neobsahuje neočakávaný residue.

## 10. Technical, security a business validation

Lab validation má tri oddelené vrstvy.

### Technical

Resource/process/packet/API mechanizmus funguje: target je healthy, route je selected, backup sa decryptne, alarm transition nastane.

### Security

Povolený principal/path funguje a zakázaný principal/path zostáva denied. Least privilege sa netestuje iba čítaním policy JSON; potrebuje pozitívny a negatívny request.

### Business alebo functional

Pôvodný outcome je použiteľný: request vráti správnu release, restore zachová invariant, settlement nie je duplicate, DNS smeruje na správnu cohortu.

Green AWS status bez business validation môže byť false positive.

## 11. Cleanup ako súčasť experimentu

Cleanup nie je administratívny dodatok. Je to posledná state transition:

```text
active lab subject
→ dependency inventory
→ retention/evidence decision
→ ordered deletion
→ asynchronous deletion observation
→ orphan scan
→ cost-residue observation
→ closed lab generation
```

`delete-stack` alebo `terraform destroy` success nemusí znamenať nulový residue. Retained snapshots, log groups, ENIs, EIPs, S3 objects, KMS keys pending deletion alebo AWS Backup recovery points môžu zostať.

## 12. Lab portfolio podľa capability boundary

| Capability cluster | Representative lab | Povinný failure boundary |
|---|---|---|
| Identity a multi-account | AssumeRole, session conditions, KMS/resource policy | source allow vs target trust/guardrail |
| VPC a egress | two-AZ private path, NAT/endpoints, Flow Logs | route/return path/AZ dependency |
| Compute a delivery | launch template, ASG, ALB | launch vs readiness vs target eligibility |
| Observability/remediation | metric/log/event → alarm/EventBridge → Automation | signal identity alebo action authorization |
| Audit/governance | organization trail, Config, central archive | delivery policy/KMS/Region coverage |
| Backup/recovery | protected resource → isolated restore | completed point vs clean business generation |
| Systems Manager | Session/Run/Automation/Patch | managed-node eligibility a target manifest |
| IaC | CloudFormation change set/update/rollback/drift | desired change vs realized runtime |
| Storage/database | EBS/EFS/S3/RDS performance a recovery | service status vs guest/application state |
| DNS/edge | Route 53/CloudFront behavior | authoritative answer/cache key/origin path |
| Serverless/containers | Lambda/ECS/EKS deployment and scaling | invocation/placement vs downstream outcome |
| FinOps | cost attribution/anomaly/remediation | estimated vs normalized realized savings |

Každý lab nemusí pokryť všetky services. Portfolio ako celok však musí pokryť všetkých päť SOA-C03 domains a opakujúce sa cross-domain boundaries.

## 13. Timed lab progression

### Foundation drill — 30 až 45 minút

Jeden resource/path, jeden fault, explicitný cleanup. Cieľom je evidence discipline.

### Domain lab — 60 až 90 minút

Viac components v jednej domain, technical aj negative validation.

### Composite lab — 120 až 150 minút

Aspoň tri domains, pre-existing baseline, unknown failure, bounded recovery a full cleanup. Kandidát nedostane krokový návod, iba outcome, constraints a access boundary.

Time sa meria samostatne:

```text
plan
provision
baseline
fault-to-diagnosis
diagnosis-to-recovery
validation
cleanup
```

Rýchly repair po 40-minútovom neštruktúrovanom guessingu nie je dobrý výsledok.

## 14. Lab scoring

| Oblasť | Body |
|---|---:|
| Exact subject a safe plan | 10 |
| Baseline a evidence inventory | 15 |
| Correct failure mechanism | 20 |
| Minimal containment/remediation | 15 |
| Technical/business validation | 15 |
| Security a forbidden outcomes | 10 |
| Cleanup a cost closure | 10 |
| Reproducible review record | 5 |

Resource vytvorený správne, ale bez fault diagnosis, negative testu alebo cleanupu, nemôže dosiahnuť plný score.

## 15. Lab review record

```text
Lab ID/generation:
Date/account/Region:
SOA-C03 domain/task:
Outcome a forbidden outcomes:
Manifest/IaC commit:
Cost estimate/guardrails:
Baseline evidence:
Fault ID/mutation:
Symptom/scope/timeline:
Competing hypotheses:
Discriminating observations:
Root cause:
Containment/remediation:
Technical validation:
Security/negative validation:
Business validation:
Cleanup inventory:
Cost residue:
Plan/provision/diagnose/repair/verify/cleanup time:
Earlier control:
Replay decision:
```

## 16. Praktická oblasť

Konkrétne vykonávacie zadania, prerequisites a checklisty sú v [labs/aws-cloudops](../../labs/aws-cloudops/README.md). Táto kapitola definuje quality contract; lab index poskytuje jednotlivé scenáre.

## 17. Anti-patterny

### Tutorial completion ako lab success

Postup podľa krokov nepreukazuje samostatné diagnosis ani recovery reasoning.

### Fault pred baseline-om

Nie je jasné, či symptóm vytvorila zámerná mutation alebo už existujúci defect.

### AdministratorAccess ako training convenience

Odstraňuje authorization boundary, ktorú má kandidát pochopiť, a zväčšuje blast radius.

### Screenshot-only evidence

Chýba exact subject, query, timestamps, fields a reproducibility.

### Reset namiesto diagnosis

Destroy/recreate alebo restart môže odstrániť root-cause evidence.

### Positive test bez forbidden pathu

Resource môže fungovať a zároveň byť verejne alebo broad-principal dostupný.

### Cleanup podľa pamäti

Asynchronous a retained resources sa ľahko prehliadnu. Potrebný je manifest-based orphan scan.

### Budget ako jediný cost guardrail

Billing data a actions majú oneskorenie; runaway usage môže vzniknúť skôr.

## 18. Kontrolné otázky

1. Čo tvorí exact lab subject?
2. Prečo je baseline podmienkou fault injection?
3. Ako sa líši tutorial od evidence-producing experimentu?
4. Čo musí obsahovať fault contract?
5. Prečo diagnosis potrebuje competing hypotheses?
6. Ako sa líši technical, security a business validation?
7. Čo je forbidden-outcome test?
8. Prečo `destroy` success nemusí znamenať cleanup closure?
9. Ako sa meria cost residue?
10. Kedy je lab generation pripravená na uzavretie alebo replay?

## Glossary impact

Relevantné pojmy: CloudOps lab subject, lab generation, financial safety boundary, expected resource manifest, evidence plan, baseline contract, controlled fault generation, lab abort condition, discriminating lab observation, hard validation, forbidden-outcome test, cleanup graph, cleanup residue, cost closure, composite CloudOps lab a lab replay verdict.

## Oficiálne zdroje

- [SOA-C03 exam guide](https://docs.aws.amazon.com/aws-certification/latest/sysops-administrator-associate-03/sysops-administrator-associate-03.html)
- [AWS Skill Builder](https://skillbuilder.aws/)
- [AWS Well-Architected Labs](https://www.wellarchitectedlabs.com/)
- [AWS Budgets](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html)
- [Tagging AWS resources](https://docs.aws.amazon.com/tag-editor/latest/userguide/tagging.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: CloudOps domain review a timed reasoning](cloudops-domain-review-timed-reasoning.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: CloudOps troubleshooting drills →](cloudops-troubleshooting-drills.md)
<!-- KNOWLEDGE-NAVIGATION:END -->