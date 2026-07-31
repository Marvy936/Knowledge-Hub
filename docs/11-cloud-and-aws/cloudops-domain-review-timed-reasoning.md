# CloudOps domain review a timed reasoning

Táto kapitola premieňa blueprint AWS Certified CloudOps Engineer – Associate (`SOA-C03`) na opakovateľný tréning rozhodovania. Cieľom nie je iba označiť správnu odpoveď. Kandidát musí vedieť z neúplného symptómu vytvoriť presný subject, oddeliť známu zdravú časť systému od prvej divergentnej boundary, vybrať observation, ktorá rozlíši realistické hypotézy, a navrhnúť zmenu s najmenším potrebným blast radiusom.

K 31. júlu 2026 používa oficiálny exam guide päť domén s váhami `22 % / 22 % / 22 % / 16 % / 18 %`. Váhy sú temporálne premenlivé a pred skúškou sa musia znovu overiť. Samotný reasoning model je stabilnejší:

```text
scenario statement
→ exact account, Region, resource a generation
→ required outcome a hard constraints
→ known healthy evidence
→ first divergent boundary
→ competing hypotheses
→ discriminating observation
→ safest authoritative action
→ technical, business a forbidden validation
```

Rýchlosť bez tejto disciplíny vytvára náhodné tipovanie. Naopak detailná analýza každej služby bez časového limitu nevytvára exam readiness. Tréning preto meria správnosť, čas aj druh chyby.

## 1. Versionovaný scenario subject

Každý scenár má mať identitu a reprodukovateľný vstup. Nasledujúci YAML nie je formát AWS skúšky. Je to tréningový manifest, ktorý zabraňuje tomu, aby sa po každom pokuse nepozorovane zmenili fakty alebo akceptačné kritériá.

```yaml
scenarioId: SOA-D1-OBS-017
examGuideGeneration: SOA-C03-2026-07
contentDomain: MonitoringLoggingAnalysisRemediationPerformance
weightPercent: 22
timeLimitSeconds: 120

subject:
  account: production-payments
  region: eu-central-1
  service: payments-api
  release: 7.18.0
  alarm: ALARM-PAY-SUCCESS-18
  metric:
    namespace: Atlas/Payments
    name: SuccessfulAuthorizations
    dimensions:
      Environment: prod
      Service: payments-api

symptom: Alarm entered ALARM after deployment
knownHealthy:
  - provider and ledger show normal payment success
  - application requests continue to complete
recentChange: release 7.18.0 changed the Service dimension to payments
requiredOutcome: restore trustworthy monitoring without recycling healthy capacity
forbiddenActions:
  - restart the whole fleet
  - treat missing telemetry as proven payment failure
  - delete alarm history before diagnosis
```

Manifest rozlišuje business state od telemetry state-u. Ak kandidát preskočí `knownHealthy`, môže zvoliť destructive remediation, ktorá vytvorí reálny incident z observability chyby.

## 2. Šesťriadkový scratchpad

Na papier alebo do dočasného textového súboru stačí šesť riadkov:

```text
Subject:
Required outcome:
Known healthy:
First divergent boundary:
Best next observation:
Acceptance evidence:
```

Pri RDS scenári môže výsledok vyzerať takto:

```text
Subject: DB-PAY-42, eu-central-1, failover generation F19, payment P-884
Required outcome: jeden provider aj ledger outcome bez slepého replayu
Known healthy: nový writer prijíma fresh connections
First divergent boundary: durable commit verzus stratené acknowledgement
Best next observation: idempotency ledger + provider request IDs
Acceptance evidence: jeden provider outcome, jeden ledger row, druhý reconcile pass no-op
```

Scratchpad nie je dokumentačná réžia. Núti kandidáta oddeliť observation od action. Ak riadok `Best next observation` obsahuje „restart instance“, reasoning už preskočil dôkazovú fázu.

## 3. Error taxonomy

Percentuálne score neukáže, prečo sa kandidát mýli. Preto sa každá chyba klasifikuje:

```text
S1 subject error
   wrong account, Region, resource, principal alebo generation

S2 semantics error
   nesprávny predpoklad o službe, napríklad Multi-AZ = backup

S3 evidence error
   observation nerozlišuje vedúce hypotézy

S4 scope error
   action má zbytočne veľký blast radius

S5 recovery error
   mutation/replay bez authority, idempotency alebo reconciliation

S6 verification error
   control-plane alebo technical state prijatý bez business dôkazu
```

Opakovaný `S6` je závažnejší než jednorazová chyba syntaxe. Kandidát môže poznať AWS služby a stále uzatvárať incident pri `Available`, `Healthy` alebo `UPDATE_COMPLETE`, hoci používateľský outcome zlyháva.

Praktický ledger:

```csv
scenario,domain,seconds,points,errorClass,firstBadAssumption,nextDrill
SOA-D1-017,D1,88,2,,,none
SOA-D2-021,D2,131,0,S6,restore-job-complete-means-recovered,AWS-LAB-007
SOA-D5-009,D5,104,1,S3,checked-SG-before-effective-route,CLOUDOPS-DRILL-F
```

Tento súbor umožní vybrať konkrétny follow-up lab namiesto všeobecného „musím sa viac učiť“.

## 4. Timed session ako control loop

Jedna 45-minútová session môže používať tento rytmus:

```text
00:00–05:00  environment, objective a current exam-guide generation
05:00–30:00  dvanásť mixed-domain scenárov
30:00–40:00  replay chybných alebo pomalých scenárov bez options
40:00–45:00  error ledger, next drill a one-sentence lesson
```

Na jednu otázku pripadá približne 120 sekúnd. Prvých dvadsať sekúnd patrí subjectu a požadovanému outcome-u. Nasledujúcich približne štyridsať sekúnd slúži na boundary a evidence. Až potom sa porovnávajú answers podľa correctness, scope, cost a operational effort.

Skip trigger nastáva, keď po približne 70–80 sekundách kandidát nevie pomenovať first divergent boundary alebo dve vedúce hypotézy. Označí scenár, zapíše posledný known fact a pokračuje. Návrat tak nezačína od nuly.

## 5. Domain 1 — Monitoring, Logging, Analysis, Remediation and Performance Optimization

Táto doména začína identitou signálu. Metric nie je iba názov na grafe; time series tvorí namespace, metric name, úplný dimension set, account, Region, period a statistic. Alarm je state machine nad touto identitou. Missing datapoint nie je automaticky nula ani zdravý stav.

### Executable scenario: alarmuje stará time series

Najprv čítaj alarm configuration a históriu bez mutation:

```bash
AWS_REGION=eu-central-1
ALARM=ALARM-PAY-SUCCESS-18

aws cloudwatch describe-alarms \
  --alarm-names "$ALARM" \
  --region "$AWS_REGION" \
  --query 'MetricAlarms[0].{
    State:StateValue,
    Namespace:Namespace,
    Metric:MetricName,
    Dimensions:Dimensions,
    Period:Period,
    Statistic:Statistic,
    Missing:TreatMissingData,
    Actions:AlarmActions
  }' \
  --output yaml

aws cloudwatch describe-alarm-history \
  --alarm-name "$ALARM" \
  --history-item-type StateUpdate \
  --start-date 2026-07-31T07:00:00Z \
  --end-date 2026-07-31T09:00:00Z \
  --region "$AWS_REGION" \
  --output table
```

Očakávaná observation je, že alarm stále sleduje `Service=payments-api`, používa `TreatMissingData=breaching` a do stavu `ALARM` prešiel po zmiznutí datapoints. Tieto príkazy dokazujú configuration a evaluation history. Nehovoria, či payments reálne zlyhali.

Porovnaj current series a business logs:

```bash
aws cloudwatch list-metrics \
  --namespace Atlas/Payments \
  --metric-name SuccessfulAuthorizations \
  --region "$AWS_REGION" \
  --query 'Metrics[].Dimensions' \
  --output json

QUERY_ID=$(aws logs start-query \
  --log-group-name /atlas/prod/payments-api \
  --start-time 1785481200 \
  --end-time 1785488400 \
  --query-string 'fields @timestamp, release, outcome, service | filter release="7.18.0" | stats count() by outcome, service' \
  --region "$AWS_REGION" \
  --query queryId --output text)

aws logs get-query-results \
  --query-id "$QUERY_ID" \
  --region "$AWS_REGION"
```

Ak `list-metrics` ukáže novú dimension `Service=payments` a logs dokazujú úspešné autorizácie, first divergent boundary je telemetry contract. Bezpečná action je najprv disable-nuť destructive alarm action alebo pridať precondition, potom kompatibilne upraviť publisher a alarm. Fleet restart nie je recovery.

Acceptance vyžaduje current series, správny alarm transition, samostatný telemetry-freshness alarm a synthetic business failure, ktorý spustí iba jeden bounded remediation execution.

## 6. Domain 2 — Reliability and Business Continuity

Tu sa odlišuje component availability, business continuity, replication, backup a clean recovery. Multi-AZ chráni pred určitými infrastructure failures. Nevráti tabuľku po logickom delete, pretože standby môže rovnakú zmenu korektne replikovať.

### Executable scenario: failover alebo PITR

Scenár hovorí, že source RDS cluster je `available`, tabuľka bola omylom zmazaná, Multi-AZ peers obsahujú rovnakú zmenu a posledný čistý PITR point je dvanásť minút starý pri RPO pätnásť minút.

Najprv prečítaj topology a restore window:

```bash
aws rds describe-db-clusters \
  --db-cluster-identifier db-pay-prod-17 \
  --region eu-central-1 \
  --query 'DBClusters[0].{
    Status:Status,
    Members:DBClusterMembers,
    Earliest:EarliestRestorableTime,
    Latest:LatestRestorableTime,
    BackupRetention:BackupRetentionPeriod
  }' \
  --output yaml

aws rds describe-events \
  --source-type db-cluster \
  --source-identifier db-pay-prod-17 \
  --duration 120 \
  --region eu-central-1 \
  --output table
```

Topology output dokazuje service state a available restore interval. Neidentifikuje clean business timestamp. Ten musí vzniknúť koreláciou audit eventu, transaction logu, ledgeru a external provider state-u.

Správna answer obnoví nový isolated cluster na clean timestamp a vykoná reconciliation. Failover na ďalšieho člena by iba zmenil writera nad už poškodeným state-om. Acceptance nie je `DBClusterStatus=available`; je to schema/data invariant, compatible application, jeden payment outcome a measured Recovery Point Actual.

## 7. Domain 3 — Deployment, Provisioning and Automation

Táto doména testuje rozdiel medzi source intentom, API acceptance, controller convergence a runtime outcome. CloudFormation `UPDATE_COMPLETE`, accepted Auto Scaling refresh alebo Lambda alias update dokazujú iba určitú control-plane boundary.

### Executable scenario: ECS deployment nevyrobil serving capacity

```bash
aws ecs describe-services \
  --cluster payments-prod \
  --services payments-api \
  --region eu-central-1 \
  --query 'services[0].{
    Desired:desiredCount,
    Running:runningCount,
    Pending:pendingCount,
    Deployments:deployments,
    Events:events[0:10]
  }' \
  --output yaml

aws ecs list-tasks \
  --cluster payments-prod \
  --service-name payments-api \
  --desired-status STOPPED \
  --region eu-central-1
```

Ak service events obsahujú `RESOURCE:ENI`, application image, command a health check ešte nie sú first boundary. Scheduler nevytvoril task network identity. Ďalší observation je subnet headroom alebo ENI density, nie restart old healthy cohortu.

```bash
aws ec2 describe-subnets \
  --subnet-ids subnet-0paya subnet-0payb subnet-0payc \
  --region eu-central-1 \
  --query 'Subnets[].{Subnet:SubnetId,AZ:AvailabilityZoneId,Free:AvailableIpAddressCount}' \
  --output table
```

Recovery vytvorí alebo pripojí approved address generation a spustí canary tasks. Acceptance potvrdí image digest, task role, target eligibility, per-AZ distribution a payment canary. `runningCount=desiredCount` bez request testu je incomplete verdict.

## 8. Domain 4 — Security and Compliance

Security reasoning začína actual caller session, nie názvom role v diagram-e. Potom sa vyhodnocuje action, resource, context, identity/resource policies, boundary, session policy, SCP/RCP, service-specific policy a explicit deny.

### Executable scenario: KMS `AccessDenied`

```bash
aws sts get-caller-identity

aws kms describe-key \
  --key-id "$KEY_ARN" \
  --region eu-central-1 \
  --query 'KeyMetadata.{Arn:Arn,State:KeyState,Usage:KeyUsage,Origin:Origin}' \
  --output yaml

aws kms get-key-policy \
  --key-id "$KEY_ARN" \
  --policy-name default \
  --region eu-central-1 \
  --query Policy \
  --output text | jq .
```

Prvý command fixuje caller identity v aktuálnom credential provider contexte. Druhý overuje key identity a state. Tretí číta key policy. Úspešné `describe-key` ešte nepreukazuje permission na `Decrypt`.

Policy simulation môže pomôcť pri identity policies, ale nemusí modelovať všetky service-specific alebo Organizations layers. Definitívny positive a forbidden test používa non-production ciphertext a exact encryption context. Zlá answer pridá wildcard allow bez overenia calleru alebo KMS key policy. Správna answer opraví prvú authorization boundary a zachová deny pre nesprávny context.

## 9. Domain 5 — Networking and Content Delivery

Networking scenár sa rieši v poradí observation boundaries, pretože rovnaký timeout môže vzniknúť v DNS, route, policy, transport, listeneri alebo application. Kandidát má najprv určiť poslednú preukázateľne zdravú vrstvu a až potom zvoliť command, ktorého rozdielny output rozdelí vedúce hypotézy.

Network reasoning používa poradie:

```text
name resolution
→ address a effective route
→ stateful/stateless policy
→ gateway, endpoint alebo attachment
→ TCP/TLS
→ listener, rule alebo cache behavior
→ application outcome
```

### Executable scenario: funguje iba časť subnetov

```bash
dig +short artifact.example.net A

aws ec2 describe-network-interfaces \
  --network-interface-ids eni-0pay42c \
  --region eu-central-1 \
  --query 'NetworkInterfaces[0].{Ip:PrivateIpAddress,Subnet:SubnetId,Groups:Groups[].GroupId}' \
  --output yaml

aws ec2 describe-route-tables \
  --filters Name=association.subnet-id,Values=subnet-0payc \
  --region eu-central-1 \
  --query 'RouteTables[].{Id:RouteTableId,Routes:Routes}' \
  --output yaml
```

Ak query nevráti explicitne asociovanú table, subnet pravdepodobne používa main route table. To je observation, nie dôkaz, že route neexistuje. Nasleduje read-back main table a potom SG/NACL/packet evidence.

Pri CloudFront incidente `X-Cache: Hit` môže znamenať správny performance outcome alebo cross-tenant leak. Cache-key inputs a origin-request policy preto patria do correctness a security analýzy, nie iba cost optimization.

## 10. Porovnanie answer options

Po identifikácii boundary porovnaj každú odpoveď cez päť otázok:

```text
1. Mení správny subject a generation?
2. Rieši mechanizmus, ktorý vysvetľuje evidence?
3. Zachováva healthy capacity, security a data authority?
4. Je to najnižší potrebný operational blast radius?
5. Obsahuje alebo umožňuje acceptance validation?
```

„Most operationally efficient“ neznamená najkratší príkaz. Managed AWS mechanismus je výhodný iba vtedy, keď rieši správnu boundary a spĺňa constraints. Automatický restart celej fleet-y je ľahko vykonateľný, ale môže byť najhoršou odpoveďou.

## 11. Replay bez answer options

Každý chybný scenár sa do 24 hodín replay-ne bez možností. Kandidát odpovie:

```text
Ktoré dve hypotézy sú najpravdepodobnejšie?
Ktorý command alebo evidence source ich najlepšie rozlíši?
Aký výsledok očakávaš pri každej hypotéze?
Čo môžeš bezpečne contain-nuť pred úplným root cause?
Aký positive a forbidden test uzatvára recovery?
```

Tým sa odstráni závislosť od wording-u distractorov. Ak kandidát pozná iba písmeno odpovede, vedomosť sa neprenesie do hands-on situácie.

## 12. Readiness gate

Doména sa nepovažuje za pripravenú po jednom dobrom teste. Minimálny gate:

```yaml
domainReadiness:
  consecutiveSessions: 3
  minimumScorePercent: 80
  maximumMedianAnswerSeconds: 105
  repeatedHighRiskErrorsAllowed: 0
  requiredHandsOnLabsPassedTwice: 1
  requiredTroubleshootingDrillPassedTwice: 1
```

Tri sessions znižujú vplyv náhodnej sady. Hands-on a troubleshooting gate dokazujú, že kandidát vie command nielen rozpoznať, ale aj interpretovať jeho output a uzavrieť outcome.

## Kontrolné otázky

1. Prečo raw score neukazuje typ reasoning problému?
2. Ktoré informácie patria do scenario subjectu pred porovnávaním answers?
3. Ako scratchpad oddeľuje observation od action?
4. Prečo missing CloudWatch datapoint nie je automaticky zero?
5. Kedy Multi-AZ failover nerieši incident a treba PITR?
6. Čo `RESOURCE:ENI` dokazuje o poradí diagnostiky?
7. Prečo `get-caller-identity` predchádza IAM policy analýze?
8. Aký rozdiel je medzi route-table read-backom a packet-flow dôkazom?
9. Prečo sa chybná otázka replayuje bez options?
10. Ktoré merania uzatvárajú domain readiness?

## Oficiálna dokumentácia

- [AWS Certified CloudOps Engineer – Associate exam guide](https://docs.aws.amazon.com/aws-certification/latest/sysops-administrator-associate-03.html)
- [Domain 1: Monitoring, Logging, Analysis, Remediation, and Performance Optimization](https://docs.aws.amazon.com/aws-certification/latest/sysops-administrator-associate-03/sysops-administrator-associate-03-domain1.html)
- [Domain 2: Reliability and Business Continuity](https://docs.aws.amazon.com/aws-certification/latest/sysops-administrator-associate-03/sysops-administrator-associate-03-domain2.html)
- [Domain 4: Security and Compliance](https://docs.aws.amazon.com/aws-certification/latest/sysops-administrator-associate-03/sysops-administrator-associate-03-domain4.html)
- [Domain 5: Networking and Content Delivery](https://docs.aws.amazon.com/aws-certification/latest/sysops-administrator-associate-03/sysops-administrator-associate-03-domain5.html)
- [AWS CLI v2 Command Reference](https://docs.aws.amazon.com/cli/latest/reference/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: AWS Certified CloudOps Engineer – Associate (SOA-C03)](cloudops-engineer-associate-soa-c03.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: CloudOps hands-on labs →](cloudops-hands-on-labs.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
