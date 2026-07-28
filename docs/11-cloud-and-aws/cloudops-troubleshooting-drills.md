# CloudOps troubleshooting drills

CloudOps troubleshooting je schopnosť obnoviť požadovaný business outcome bez zničenia evidence, rozšírenia blast radiusu alebo vytvorenia skrytého secondary failure. Drill preto nie je zoznam príkazov pre jeden symptóm. Je to versionovaný incident experiment, ktorý začína exact subjectom a timeline, vytvára konkurenčné kauzálne hypotézy, používa diskriminačné observation points, vykonáva containment a authoritative recovery a končí overením pôvodného aj zakázaného outcome-u.

## 1. Dominantný model: symptom-to-closure lifecycle

```text
user/business symptom
→ impact, scope a timeline
→ exact account/Region/release/resource/data/flow subject
→ recent-change correlation a volatile evidence preservation
→ control/data/recovery path map
→ competing causal hypotheses
→ discriminating observations
→ evidence-preserving containment
→ authoritative remediation alebo recovery
→ controller/runtime/data reconvergence
→ original, forbidden a adjacent-cohort validation
→ recurrence control a incident closure
```

Rýchla zmena, ktorá odstráni symptom, nemusí byť oprava. Otvorenie Security Group na `0.0.0.0/0`, pridanie AdministratorAccess alebo blind restart môžu zmeniť failure signature, odstrániť dôkazy a vytvoriť väčší incident.

## 2. Exact incident subject

Pred diagnostikou zapíš:

```text
incident/drill ID:
expected-state generation:
fault/change generation:
AWS organization/account:
Region a AZs:
caller/session identity:
workload/release/artifact:
resource IDs/ARNs a configuration versions:
data/business correlation ID:
first symptom UTC:
last known good UTC:
affected a unaffected cohorts:
recent deployments/policies/rotations/failovers:
allowed outcomes:
forbidden outcomes:
```

Názov ako `payments-api` nie je dostatočná identity. V jednom account-e môžu existovať starý a nový target group, viac launch-template versions, alias smerujúci na nový key, secret labels na rôznych versions alebo rovnaký stack name v inom Regione.

## 3. Impact a scope pred root cause

Najprv rozhodni:

- je dopad používateľský, business, security, recovery alebo iba control-plane warning;
- je affected jeden resource, jedna generation, AZ, Region, account, tenant alebo všetci clients;
- ktoré cohorts sú zdravé a môžu slúžiť ako control group;
- či failure rastie, je stabilný alebo sa sám zotavuje;
- či remediation automation už vykonáva ďalšie mutations.

Containment priority vychádza z impactu a trendu, nie z prvého error message.

## 4. Evidence preservation

Volatile evidence zachovaj pred restartom, replacementom alebo rollbackom:

- UTC timeline a request/correlation IDs;
- CloudTrail actor/session/request/error details;
- Auto Scaling, ECS/EKS, Lambda, RDS, Backup alebo CloudFormation events;
- target health reasons a load-balancer logs;
- CloudWatch metric identity, datapoints, alarm transitions a action history;
- instance/container/process logs a exit reasons;
- route tables, SG/NACL, endpoint a DNS state;
- IAM/SCP/resource/KMS policies a exact versions;
- launch template, AMI/image digest, user data a desired-state generation;
- recovery point, secret version, staging labels alebo key identity;
- recent deployment, patch, policy, rotation a cost anomaly events.

Screenshot môže dopĺňať evidence, ale CLI/API JSON a IDs sú potrebné pre presné porovnanie generations.

## 5. Path map

Podľa symptómu nakresli relevantné vrstvy.

### API/control path

```text
caller session
→ authentication
→ identity/resource/trust/SCP/boundary/KMS conditions
→ service API
→ admission/validation
→ asynchronous controller
→ realized resource
```

### Request/data path

```text
client
→ DNS/cache
→ route/gateway
→ SG/NACL/WAF/listener
→ target eligibility
→ process
→ dependency
→ business commit a acknowledgement
```

### Deployment path

```text
source/IaC/release intent
→ artifact/AMI/image generation
→ launch/deployment configuration
→ scheduler/controller
→ compute/network/storage realization
→ readiness/health
→ traffic exposure
```

### Recovery path

```text
clean boundary
→ recovery-point/key/access
→ restore target
→ dependencies/configuration
→ integrity/reconciliation
→ fencing
→ cutover/failback
```

Hypotéza musí ukazovať, na ktorom prechode sa expected state prestal realizovať.

## 6. Competing hypotheses

Nevyberaj root cause podľa najvýraznejšieho symptómu. Vytvor malý, kvalitný set hypotéz:

- jedna blízko symptómu;
- jedna v upstream control/deployment path-e;
- jedna v shared dependency alebo authorization boundary;
- podľa incidentu jedna provider/capacity alebo stale-generation hypotéza.

Každá hypotéza potrebuje:

```text
cause
→ failure mechanism
→ predicted observations
→ observation, ktorý ju odlíši
```

Hypotéza bez falsifiable prediction je iba domnienka.

## 7. Discriminating observation

Dobrá observation oddeľuje minimálne dve hypotézy.

Príklady:

- target health `Connection timed out` podporuje network/listener path; HTTP `404` podporuje wrong health contract;
- ASG activity `InsufficientInstanceCapacity` odlišuje zonal capacity od account quota;
- `AccessDenied` s KMS eventom odlišuje image/volume key path od user-data failure;
- Flow Logs `ACCEPT` plus application connection refusal posúva diagnosis za packet filter;
- correct DNS authoritative answer, ale stale resolver cache vysvetľuje iba určitú client cohortu;
- secret `AWSCURRENT` neodlišuje consumer-loaded state; per-process version fingerprint áno;
- completed backup job neodlišuje clean a business-dirty point; reconciliation query áno.

## 8. Containment pred repair

Containment zastavuje rast dopadu a zachováva recovery options. Môže zahŕňať:

- stop/cancel rollout, instance refresh alebo automation execution;
- znížiť traffic na affected generation;
- izolovať compromised principal alebo account;
- zastaviť retry/consumer source pri duplicate side effects;
- cordon/drain affected compute cohort;
- chrániť clean recovery points a log archive;
- freeze destructive cleanup alebo key deletion;
- dočasne zvýšiť capacity iba ak neskryje root bottleneck.

Containment nie je uzavretie. Po ňom musí nasledovať authoritative remediation a full validation.

## 9. Authoritative remediation

Preferuj opravu desired-state alebo source contractu:

- správna launch template/AMI/image generation;
- opravená route, policy, health contract alebo secret rotation state;
- fixed IaC a nový bounded apply;
- replacement z last-known-good artifactu;
- restore z exact clean recovery manifestu;
- idempotent reconciliation pri unknown business outcome.

Ručná mutation jedného instance, tasku alebo policy bez source update vytvára drift a ďalší reconciliation ju môže prepísať.

## 10. Worked composite incident: instance refresh, KMS a zero healthy targets

### Business symptom

O `10:04 UTC` Atlas Payments checkout začne vracať `503`. ALB dashboard ukazuje pokles healthy targets z dvoch na nulu. RDS je `available`, CPU je nízke a route/SG configuration sa podľa dashboardu nezmenila.

### Exact subject

```text
incident: CAP-PAY-42-IR-20260728
account: production-payments
Region: eu-central-1
service: payments-api
release target: 5.8.0
ASG: payments-api-prod
instance refresh ID: ir-7f2
source launch template: version 42
source AMI: ami-payments-5.8.0
AMI EBS snapshot encryption key: arn:aws:kms:...:key/image-key-prod
last known good launch template: version 41
last known good release: 5.7.3
refresh preferences: min healthy 0 %, max healthy 100 %
first refresh action: 09:59 UTC
first client 503: 10:04 UTC
```

Version `42` bola vytvorená z image pipeline v samostatnom image-builder account-e. AMI bola zdieľaná, ale customer-managed KMS key policy/grant neumožnila Auto Scaling service-linked role v production account-e použiť encrypted snapshot pri launchi.

### Causal chain

```text
instance refresh starts with min healthy 0 %
→ controller môže terminate old healthy instance pred successful replacement
→ launch template v42 requests AMI encrypted by shared customer KMS key
→ production Auto Scaling/EC2 launch path nemá required key authorization
→ replacement launch fails
→ refresh continues/retries while old capacity is removed
→ target group loses eligible targets
→ ALB returns 503
```

KMS authorization failure je primárny launch defect. Unsafe refresh preferences sú failure amplifier, ktorý zmenil deployment failure na business outage.

### Competing hypotheses

- **H1 — subnet IP exhaustion:** nové instances nemožno umiestniť; ASG activity má ukázať address/ENI capacity errors.
- **H2 — zonal instance capacity shortage:** launch zlyháva pre selected instance type/AZ; activity má ukázať insufficient capacity.
- **H3 — user-data/application readiness failure:** instance launchne, ale process alebo health check zlyhá; EC2 instances a logs majú existovať.
- **H4 — SG/target-port regression:** instances bežia, ale ALB ich nevie dosiahnuť; target health a Flow Logs majú ukázať packet/connection failure.
- **H5 — AMI/KMS authorization failure:** `RunInstances` alebo EBS volume creation zlyhá pred instance realization; ASG/CloudTrail/KMS evidence má ukázať exact key denial.

### Discriminating observations

1. ASG activity history ukáže failed launches s KMS-related client error, nie subnet alebo capacity message.
2. V affected časovom intervale nevzniknú nové EC2 instance IDs, čo oslabuje H3 a H4.
3. CloudTrail koreluje `RunInstances`/KMS operation s production service-linked role a exact `image-key-prod`.
4. Key policy povoľuje image-builder account, ale nie required production principal/service grant path.
5. Existing version `41` instances pred termination zostávali healthy; route, SG, listener a process path boli funkčné.
6. Instance refresh preferences vysvetľujú, prečo deployment failure odstránil starú capacity namiesto bezpečného zastavenia.

H5 je root cause; unsafe refresh configuration je causal amplifier. H1–H4 sú diskriminované.

### Evidence-preserving containment

1. cancel instance refresh `ir-7f2`;
2. zastav ďalšiu deployment automation;
3. zachovaj ASG activities, CloudTrail events, launch template versions, AMI/key policies a target-health timeline;
4. nastav desired source späť na launch template version `41`;
5. neotváraj SG, nepridávaj AdministratorAccess a nemeň KMS policy na broad `Principal: *`;
6. obnov minimálnu healthy capacity z last-known-good generation a čakaj na target eligibility pred ďalším replacementom.

Cancel refresh sám nemusí automaticky vrátiť už terminated capacity ani desired configuration. Containment preto explicitne obnovuje source generation a capacity.

### Authoritative recovery

```text
launch template default/source → version 41
→ launch replacement instances
→ bootstrap/process readiness
→ target health
→ client business request
→ stable cohort
```

Po obnove služby oprav samostatne version `42`:

- uprav KMS key policy/grant podľa exact cross-account AMI/EBS service contractu;
- over least-privilege principal a encryption context/constraints;
- spusti one-instance canary ASG alebo isolated launch test;
- potvrď EBS creation, boot, SSM access, process readiness a target health;
- nastav safe refresh preferences, checkpoint/alarms a abort criteria;
- až potom opakuj production refresh.

### Acceptance verdict

Incident možno uzavrieť až keď:

- checkout request cez production DNS/ALB uspeje;
- minimálne dve healthy targets sú rozložené podľa designu;
- release `5.7.3` recovery generation je stabilná alebo nový `5.8.0` canary prešiel full gate-om;
- forbidden direct/public path na instances zostáva blokovaný;
- KMS access je obmedzený na required principals a actions;
- druhý controlled replacement prejde bez capacity loss;
- alarm/abort mechanism zastaví zámerne chybný canary;
- adjacent ASG/image cohorts používajú správny key-sharing contract;
- timeline, root cause, amplifier a earlier controls sú zapísané.

## 11. Earlier controls odvodené z incidentu

Tento failure neuzatvára iba policy patch. Potrebuje system controls:

- image publication manifest obsahujúci AMI ID, Region, snapshot IDs a KMS key identity;
- pre-production launch test z consumer accountu a consumer service-linked role pathu;
- policy validation pre cross-account encrypted AMI sharing;
- refresh guardrail zakazujúci nebezpečný `min healthy` pre critical service;
- canary/checkpoint a target-health abort alarm;
- automatic stop pri launch failures pred retirementom old cohorty;
- last-known-good launch-template generation a tested recovery command;
- business request validation, nie iba EC2 launch success.

## 12. Validation layers

### Original outcome

Používateľ alebo workload opäť vykoná pôvodnú činnosť: checkout, DNS resolution, backup restore, SSM command alebo API call.

### Forbidden outcome

Oprava nevytvorila broad access, public exposure, duplicate payment, data loss, disabled audit alebo unbounded automation.

### Adjacent cohort

Over ďalšiu AZ, instance, account, Region, tenant alebo release generation. Single recovered resource môže byť výnimka.

### Second operation/reconciliation

Zopakuj relevantný controller cycle: ďalší ASG replacement, Lambda retry, ECS deployment, secret refresh, backup copy alebo CloudFormation update. Oprava, ktorá prežije iba prvý manual test, nie je stabilná.

## 13. Drill construction contract

Kvalitný drill obsahuje:

```text
known expected generation
→ one injected primary fault
→ optional one causal amplifier
→ measurable business/technical symptom
→ at least three plausible hypotheses
→ preserved evidence path
→ safe containment
→ authoritative reset/recovery
→ positive, forbidden and adjacent validation
→ deterministic cleanup
```

Po zvládnutí single-fault drillov možno pridať causal amplifier, napríklad wrong alarm remediation alebo unsafe rollout setting. Nepridávaj dve nezávislé náhodné chyby, ktoré nevytvárajú jeden vysvetliteľný incident chain.

## 14. Capability drill matrix

| Failure boundary | Representative drill | Discriminating evidence |
|---|---|---|
| Cross-account authorization | AssumeRole/KMS/resource policy denial | caller session, trust, SCP, key event |
| Public/private packet path | IGW/NAT/route/SG/NACL/return failure | route selection, Flow Logs, listener evidence |
| Target eligibility | ALB wrong port/path/SG/process bind | target health reason, local request, flow state |
| Fleet realization | ASG quota/capacity/IP/AMI/bootstrap | ASG activity, instance existence, console output |
| Signal-to-action | alarm dimension/EventBridge/Automation failure | exact series, transition, invocation and role |
| Managed-node operations | SSM agent/endpoint/profile/target mismatch | node registration, endpoint path, execution manifest |
| Storage/database | EBS AZ/performance, RDS connection/failover | service metrics plus guest/session evidence |
| Backup/recovery | selection/KMS/copy/restore consistency | policy generation, point lineage, business validation |
| DNS/edge | Route 53 TTL/health, CloudFront behavior/cache | authoritative answer, cache result, origin path |
| Serverless/container | Lambda retry/VPC, ECS/EKS placement/identity | invocation/task/Pod generation and downstream outcome |
| IaC/deployment | CloudFormation rollback/drift/PassRole | ordered stack events and realized resources |
| Cost/capacity | NAT ports, logging growth, incident usage | usage dimensions, flow/log source, unit outcome |
| Organization guardrail | SCP attachment/inheritance deny | policy version, OU path, request context |

Drill index s konkrétnymi zadaniami je oddelený v [troubleshooting/aws-cloudops](../../troubleshooting/aws-cloudops/README.md).

## 15. Time model

Meraj samostatne:

- symptom-to-scope;
- scope-to-hypotheses;
- hypotheses-to-root-cause;
- root-cause-to-containment;
- containment-to-recovery;
- recovery-to-validation;
- cleanup/closure.

Orientačné tréningové hranice:

- simple resource/config drill: 8–10 minút;
- multi-layer data path: 12–18 minút;
- multi-account, backup alebo deployment incident: 20–30 minút;
- composite business incident: 30–45 minút.

Rýchly guess a restart môže zlepšiť repair time, ale zhoršiť diagnosis fidelity a recurrence risk. Score preto nesmie používať iba total time.

## 16. Drill scoring

| Oblasť | Body |
|---|---:|
| Exact subject, impact a timeline | 10 |
| Evidence preservation | 10 |
| Competing causal hypotheses | 15 |
| Discriminating observation/root cause | 20 |
| Safe containment | 10 |
| Authoritative remediation/recovery | 15 |
| Original/forbidden/adjacent validation | 15 |
| Closure, earlier control a cleanup | 5 |

AdministratorAccess, public-open rule alebo evidence-destroying reset môže scenár technicky „opraviť“, ale zlyhá safety a closure gate.

## 17. Incident review record

```text
Incident/drill ID:
Expected and fault generations:
Account/Region/AZ:
Business symptom/impact:
First symptom/last known good UTC:
Affected/unaffected cohorts:
Exact release/resource/data/flow subject:
Recent changes:
Preserved evidence:
Control/data/recovery path:
Hypotheses and predictions:
Discriminating observations:
Root cause and causal amplifier:
Containment:
Authoritative recovery:
Original outcome validation:
Forbidden outcome validation:
Adjacent/second-operation validation:
Cleanup:
Diagnosis/containment/recovery/validation time:
Earlier controls:
Residual risk/owner:
Closure verdict:
```

## 18. Anti-patterny

### AdministratorAccess pri `AccessDenied`

Odstráni policy discrimination a zväčší blast radius.

### `0.0.0.0/0` pri network failure

Môže obísť SG symptom, ale nevyrieši route, listener, bind alebo return path.

### Restart/replace pred evidence

Odstráni process state, logs, stopped reason alebo exact failed generation.

### Prvá hypotéza ako root cause

Confirmation bias vedie k zbieraniu iba podporujúcich signálov.

### Console green ako business validation

Resource status nepreukazuje request, transaction, restore consistency ani forbidden path.

### Ručný fix bez desired-state opravy

Controller alebo ďalší deployment obnoví defect.

### Rollback bez compatibility a outcome kontroly

Starý artifact môže byť nekompatibilný s novou schema, queue backlogom alebo provider state-om.

### Restore priamo do production

Obchádza isolation, clean-state validation, fencing a reconciliation.

### Incident closed po symptom recovery

Chýba adjacent cohort, second operation, earlier control a residual-risk decision.

## 19. Kontrolné otázky

1. Čo tvorí exact CloudOps incident subject?
2. Prečo sa impact a scope určujú pred root cause?
3. Aké evidence sa môže stratiť restartom alebo replacementom?
4. Ako sa tvorí falsifiable causal hypothesis?
5. Čo je discriminating observation?
6. Ako sa líši containment od authoritative remediation?
7. Prečo manual instance fix nie je stabilná recovery?
8. Čo musí overiť forbidden-outcome test?
9. Prečo je adjacent cohort a second operation súčasť closure?
10. Ktoré earlier controls vyplývajú z instance-refresh/KMS incidentu?

## Glossary impact

Relevantné pojmy: CloudOps incident subject, symptom-to-closure lifecycle, impact/scope classification, recent-change correlation, volatile AWS evidence, control/data/recovery path map, causal CloudOps hypothesis, discriminating observation, evidence-preserving containment, authoritative cloud recovery, causal amplifier, reconvergence validation, forbidden-outcome validation, adjacent-cohort validation, second-operation verification, CloudOps closure verdict a earlier operational control.

## Oficiálne zdroje

- [SOA-C03 exam guide](https://docs.aws.amazon.com/aws-certification/latest/sysops-administrator-associate-03/sysops-administrator-associate-03.html)
- [AWS re:Post Knowledge Center](https://repost.aws/knowledge-center/)
- [Amazon EC2 Auto Scaling troubleshooting](https://docs.aws.amazon.com/autoscaling/ec2/userguide/ts-as-instancelaunchfailure.html)
- [Share encrypted AMIs across accounts](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ami-sharing.html)
- [Amazon VPC troubleshooting](https://docs.aws.amazon.com/vpc/latest/userguide/troubleshooting.html)
- [AWS Systems Manager troubleshooting](https://docs.aws.amazon.com/systems-manager/latest/userguide/troubleshooting.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: CloudOps hands-on labs](cloudops-hands-on-labs.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Monitoring vs. observability →](../12-observability/monitoring-vs-observability.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
