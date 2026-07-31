# CloudOps troubleshooting drills

Troubleshooting drill trénuje rozhodovanie pod časom a neistotou. Každý drill začína business symptomom, nie názvom služby. Kandidát musí zachovať evidence, vytvoriť competing hypotheses, vybrať observation, ktorá ich reálne rozlíši, vykonať bounded containment a uzavrieť recovery technickým aj business testom.

Drill nie je demo príkazov. Príkaz je užitočný iba vtedy, keď je jasné, ktorý exact subject číta, aký výsledok sa očakáva pri jednotlivých hypotézach a čo output ešte nepreukazuje. Spoločný lifecycle je:

```text
business symptom a exact subject
→ preserve volatile evidence
→ known healthy a first-divergent boundary
→ competing hypotheses
→ cheapest discriminating observation
→ evidence-preserving containment
→ authoritative recovery
→ control-plane read-back
→ runtime a business validation
→ forbidden outcome a second clean run
```

## Drill protocol

Časový protokol vytvára tlak, ale neospravedlňuje blind mutation. Prvé minúty patria identite subjectu a dôkazu; remediation prichádza až po observation, ktorá zmenší hypothesis space.

```text
T+0  → state symptom, business impact a exact subject
T+2  → preserve volatile evidence a current generations
T+5  → write 3–5 competing hypotheses
T+8  → run the cheapest discriminating observation
T+12 → contain blast radius without destroying evidence
T+20 → apply authoritative and reversible recovery
T+30 → verify technical, business and forbidden outcomes
T+35 → repeat critical operation or record residual risk
```

Blind restart pred evidence je failure drillu, pokiaľ restart nie je nevyhnutný na zastavenie aktívneho poškodenia. Aj vtedy sa musí najprv zachytiť minimálny volatile context: caller, release, resource generation, recent events, relevant metrics a affected business identities.

## Drill A – ECS tasks zostávajú PENDING

Desired count stúpne z 20 na 40, old tasks sú healthy a new tasks zostávajú `PENDING`. Known-good old cohort je zároveň serving capacity aj rollback boundary, preto sa nesmie zničiť pred vytvorením replacementu.

```bash
aws ecs describe-services \
  --cluster payments-prod \
  --services payments-api \
  --region eu-central-1 \
  --query 'services[0].{Desired:desiredCount,Running:runningCount,Pending:pendingCount,Deployments:deployments,Events:events[0:10]}' \
  --output yaml

aws ec2 describe-subnets \
  --subnet-ids subnet-0paya subnet-0payb subnet-0payc \
  --region eu-central-1 \
  --query 'Subnets[].{Subnet:SubnetId,AZ:AvailabilityZoneId,Free:AvailableIpAddressCount}' \
  --output table
```

Service events lokalizujú scheduler alebo placement boundary. Ak event uvádza `RESOURCE:ENI`, container command, image process a application health check ešte nie sú first failure. Subnet output porovná address headroom medzi AZs, ale nepreukazuje ENI limits na instance type ani account quota.

Containment zastaví nekontrolovaný scale-out a zachová old cohort. Recovery pridá approved subnet alebo compute/address capacity generation a spustí malý canary cohort. Positive acceptance vyžaduje správny task-definition digest, task role, target eligibility a request cez každú intended AZ. Forbidden outcome je termination old tasks pred serving replacementom; second operation zopakuje scale-out a potvrdí, že capacity boundary už nie je náhodne tesná.

## Drill B – ALB targets sú healthy, no canary nedostáva traffic

Oba target groups sú healthy, intended 10 % canary však prijíma nula requestov. Target health dokazuje iba health-check path z load balancer nodes na targets. Nedokazuje listener-rule match, priority, weighted forward action, stickiness ani client-visible DNS path.

```bash
aws elbv2 describe-rules \
  --listener-arn "$LISTENER_ARN" \
  --region eu-central-1 \
  --query 'Rules[].{Priority:Priority,Conditions:Conditions,Actions:Actions}' \
  --output yaml

aws elbv2 describe-target-health \
  --target-group-arn "$CANARY_TG" \
  --region eu-central-1 \
  --query 'TargetHealthDescriptions[].{Target:Target,State:TargetHealth.State,Reason:TargetHealth.Reason}' \
  --output table
```

Competing hypotheses zahŕňajú shadowing broad pravidlom s vyššou prioritou, host/path mismatch, weighted action na nesprávny target group, sticky cookie a chýbajúcu cohort telemetry. Rules output má určiť prvé matching pravidlo pre exact request, nie iba potvrdiť existenciu canary rule.

Recovery mení ordered listener rule alebo weight po exact host/path teste. Targets sa nereštartujú, pretože sú healthy a problém je pred nimi. Acceptance používa requesty s explicitným Host headerom, response release identity a observed distribution. Forbidden test overí, že iný tenant alebo path nie je omylom routovaný na canary; druhá zmena weightu musí byť predvídateľná a vratná.

## Drill C – RDS failover je green, ale vznikla duplicate payment

Cluster sa promoted, nový writer prijíma connections, no provider ukazuje dve autorizácie pre jednu payment identity. Green database topology preukazuje technickú dostupnosť novej generation, nie outcome transakcie, ktorej acknowledgement sa stratilo počas failoveru.

```bash
aws rds describe-events \
  --source-type db-cluster \
  --source-identifier db-pay-prod-17 \
  --duration 60 \
  --region eu-central-1 \
  --output table

aws rds describe-db-clusters \
  --db-cluster-identifier db-pay-prod-17 \
  --region eu-central-1 \
  --query 'DBClusters[0].{Status:Status,Endpoint:Endpoint,Members:DBClusterMembers}' \
  --output yaml
```

Potom sa porovná idempotency ledger, outbox, provider request IDs a client retry history pre exact payment. Timeout nie je dôkaz rollbacku. Ak database commit prežil a acknowledgement nie, blind replay vytvorí druhý external side effect.

Containment pozastaví automatic retry pre unknown outcomes a zachová transaction/provider evidence. Recovery reconciliuje podľa stable business identity, opraví provider idempotency key alebo retry contract a až potom obnoví processing. Acceptance je jeden provider aj ledger outcome, nulová unresolved cohort a no-op druhý reconciliation pass. Forbidden test vloží failover medzi commit a acknowledgement a musí zostať bez duplicate authorization.

## Drill D – Lambda, SQS backlog a duplicate side effects

Queue age rastie a niektoré messages vytvárajú duplicate settlement. Kandidát musí oddeliť backlog, throttling, visibility timeout, poison message a non-idempotent handler. Samotný `ApproximateNumberOfMessages` neukazuje, prečo message nie je dokončená.

```bash
aws lambda get-event-source-mapping \
  --uuid "$MAPPING_UUID" \
  --region eu-central-1

aws lambda get-function-configuration \
  --function-name payments-settle:live \
  --region eu-central-1

aws sqs get-queue-attributes \
  --queue-url "$QUEUE_URL" \
  --attribute-names VisibilityTimeout RedrivePolicy ApproximateNumberOfMessages ApproximateNumberOfMessagesNotVisible ApproximateAgeOfOldestMessage
```

Event-source mapping ukáže batch size, concurrency, state a failure-handling contract. Function configuration ukáže timeout, reserved concurrency a versioned environment. Queue attributes približujú backlog a visibility, ale sú eventually consistent a nepreukazujú business completion.

Containment môže pozastaviť mapping alebo znížiť bounded concurrency, nie purge-nuť queue. Recovery zosúladí visibility s worst-case processingom, zavedie partial-batch failure handling a business idempotency. Replay používa manifest exact unresolved messages. Positive test vytvorí jedno settlement; forbidden test doručí rovnakú message druhýkrát bez druhého side effectu; second run preukáže, že queue age klesá bez skrytého DLQ rastu.

## Drill E – KMS AccessDenied po policy rolloute

Po policy rolloute začnú iba niektoré Pods dostávať `AccessDenied`. Hypotézy zahŕňajú inú assumed-role session, stale static credential, key policy, identity policy, encryption context, endpoint policy a Organizations guardrail. Názov Kubernetes service accountu nie je dôkaz actual AWS principalu.

```bash
aws sts get-caller-identity

aws kms describe-key \
  --key-id "$KEY_ARN" \
  --region eu-central-1 \
  --query 'KeyMetadata.{Arn:Arn,State:KeyState,Usage:KeyUsage}'

aws kms get-key-policy \
  --key-id "$KEY_ARN" \
  --policy-name default \
  --region eu-central-1 \
  --query Policy \
  --output text | jq .
```

Caller output fixuje account a role session pre affected runtime. Key metadata potvrdzuje exact key a state, ale úspešný `DescribeKey` nepreukazuje `Decrypt`. Key policy je len jedna authorization layer.

Ak affected Pod používa legacy environment key, wildcard allow v key policy je nesprávna recovery. Containment zastaví rollout mixed credential generations. Recovery odstráni stale credential source, obnoví workload identity a opraví iba prvú denying boundary. Positive test dešifruje non-production ciphertext s exact contextom; forbidden test použije nesprávny principal alebo context; druhá fresh session musí preukázať, že staré credentials už nemajú authority.

## Drill F – Hybrid path zlyháva iba v jednej AZ

Workload v jednej AZ nevie pripojiť `ledger.internal:5443`, zatiaľ čo ostatné AZs fungujú a Direct Connect dashboard je green. Green circuit a BGP session nepreukazujú round trip pre každý source prefix ani stateful firewall path.

```bash
getent ahostsv4 ledger.internal
nc -vz -w 3 ledger.internal 5443
openssl s_client \
  -connect ledger.internal:5443 \
  -servername ledger.internal \
  -brief </dev/null
```

DNS output ukazuje resolver-visible addresses. `nc` testuje TCP establishment, nie TLS identity alebo application authorization. `openssl` pridáva TLS handshake. Ďalší read-back musí identifikovať source ENI, subnet route association, AWS advertised prefix, on-prem received prefix a return firewall session.

Containment odoberie affected AZ z novej placement generation bez vypnutia celého hybrid linku. Recovery zosúladí authoritative prefix inventory, BGP advertisements, return routes a firewall objects. Acceptance vykoná TCP, TLS a business request z každej production AZ. Forbidden test overí, že unauthorized source subnet zostáva blokovaný; failover na backup VPN musí prejsť a následný failback nesmie vytvoriť asymetrický path.

## Drill G – CloudFront vracia cross-tenant response

Tenant B dostane response tenant-a a header ukazuje `X-Cache: Hit`. To je security incident, nie iba cache misconfiguration. Evidence sa musí zachovať skôr, než invalidation odstráni reprodukovateľný object.

```bash
curl -sS -D tenant-a.headers \
  -H 'X-Tenant-ID: tenant-a' \
  "$URL" -o tenant-a.body

curl -sS -D tenant-b.headers \
  -H 'X-Tenant-ID: tenant-b' \
  "$URL" -o tenant-b.body

aws cloudfront get-distribution-config \
  --id "$DISTRIBUTION_ID"

aws cloudfront get-cache-policy \
  --id "$CACHE_POLICY_ID"
```

Dvojica requestov dokazuje user-visible collision iba vtedy, keď sa zachová request identity, headers a body hash. Distribution a cache policy read-back ukážu effective cache-key inputs a origin forwarding. `Hit` s absent tenant key podporuje shared-cache hypothesis; sám nepreukazuje, či origin tiež ignoruje tenant identity.

Containment prepne affected behavior na caching-disabled policy alebo izolovaný cache key a vykoná targeted invalidation. Origin sa nikdy neotvára public. Recovery versionuje tenant-aware cache a origin request policy. Acceptance používa A/B/A sequence, unique object markers a origin logs; forbidden test musí dokázať, že tenant B nikdy nedostane A content ani po warm cache.

## Drill H – Backup job je green, recovery point je nepoužiteľný

Source backup job je `COMPLETED`, no isolated recovery Region nemá použiteľný recovery point. Hypotézy zahŕňajú failed copy job, retention deletion, unavailable KMS key, missing IAM authority, unsupported restore metadata a application-inconsistent snapshot.

```bash
aws backup list-backup-jobs \
  --by-backup-vault-name vault-pay-prod-8 \
  --region eu-central-1

aws backup list-copy-jobs \
  --by-destination-vault-arn "$RECOVERY_VAULT_ARN" \
  --region eu-west-1

aws kms describe-key \
  --key-id "$RECOVERY_KEY_ARN" \
  --region eu-west-1
```

Source job status preukazuje iba source protection operation. Copy jobs a destination key určujú, či recovery account/Region má artifact aj cryptographic authority. Ani green copy nepreukazuje restore alebo application consistency.

Containment zachová latest clean source a destination points a zastaví retention action nad incident window. Recovery vyberie clean point, obnoví ho v clean-room boundary a vykoná schema, dependency a business validation. Closure zaznamená Recovery Point Actual a Recovery Time Actual. Forbidden test overí, že production principal nevie meniť recovery vault; druhý restore musí prejsť bez ad-hoc permission alebo manuálneho secretu.

## Drill I – CloudWatch alarm vytvára remediation loop

Alarm prechádza medzi `ALARM` a `OK` a opakovane spúšťa destructive automation. Vedúce hypotézy zahŕňajú dimension drift, missing-data semantics, delay medzi action a metric, duplicate EventBridge delivery a remediation bez idempotency.

```bash
aws cloudwatch describe-alarms \
  --alarm-names ALARM-PAY-SUCCESS-18 \
  --region eu-central-1

aws cloudwatch list-metrics \
  --namespace Atlas/Payments \
  --metric-name SuccessfulAuthorizations \
  --region eu-central-1

aws cloudwatch describe-alarm-history \
  --alarm-name ALARM-PAY-SUCCESS-18 \
  --region eu-central-1
```

Alarm configuration ukáže metric identity, periods a `TreatMissingData`. Metric inventory odhalí competing dimension generations. History ukáže transition cadence a action timing. Žiadny z týchto outputov sám nepreukazuje business failure.

Containment disable-ne iba destructive action alebo vloží precondition, nie celý monitoring. Recovery opraví metric contract, pridá telemetry-freshness signal a execution deduplication. Positive test simuluje reálny failure a očakáva jednu remediation. Forbidden test zastaví publisher pri healthy workload-e a nesmie spustiť destructive loop. Second operation musí zostať idempotentná.

## Drill J – NAT egress timeouts

Outbound requests začnú timeoutovať pri traffic spike a application retry rate rastie. Hypotézy zahŕňajú NAT port allocation pressure, destination concentration, downstream throttle, DNS change, connection leak a retry amplification. Pridanie ďalších application instances môže incident zhoršiť, pretože zvýši počet source connections.

```bash
aws ec2 describe-nat-gateways \
  --nat-gateway-ids "$NAT_ID" \
  --region eu-central-1

aws cloudwatch get-metric-data \
  --metric-data-queries file://nat-metrics.json \
  --start-time 2026-07-30T18:00:00Z \
  --end-time 2026-07-30T19:00:00Z \
  --region eu-central-1
```

NAT read-back fixuje state, subnet a addresses. Metric query musí porovnať `ErrorPortAllocation`, connection attempts, bytes a timeout window. Correlation s destination tuples, client pooling a retries rozlíši NAT pressure od downstream failure.

Containment obmedzí retries, zachová connection reuse a prípadne presmeruje bounded cohort na independent egress path. Recovery môže pridať NAT/address capacity, rozdeliť destinations alebo odstrániť zbytočný NAT použitím VPC endpointu, ale iba podľa root cause. Acceptance meria request success, latency, port-allocation errors a downstream health; scale-out replay nesmie znovu vyvolať amplification.

## Drill scorecard

Scorecard zachováva reasoning path, nie iba výsledok. Umožní rozlíšiť úspech spôsobený correct mechanismom od náhodného recovery po expirácii alebo residual state.

```yaml
drillId: CLOUDOPS-DRILL-D
subjectIdentifiedSeconds: 70
evidencePreserved: true
hypotheses:
  - visibility timeout shorter than processing
  - function throttling
  - poison record
firstObservation: event-source mapping plus queue attributes
containmentBlastRadius: bounded
recovery: passed
positiveTest: one settlement
forbiddenTest: duplicate event produced no second side effect
secondRun: passed
residualRisk: none
```

Drill prejde až po clean second run. Prvá recovery môže uspieť vďaka cache, manuálne zmenenému resource-u alebo náhodnému residual state-u. Opakovanie overuje, že mechanismus je reprodukovateľný a automation nevytvára ďalší side effect.

## Drill rotation

Každý týždeň sa rotuje aspoň jeden drill z monitoring, reliability, deployment, security a networking domény. Mesačne sa kombinujú dva failure modes, napríklad CloudWatch dimension drift počas ECS rollout-u alebo RDS failover počas Secrets rotation s mixed consumers.

Combined drills sú dôležité, pretože production evidence sa neorganizuje podľa exam domén. Kandidát sa musí naučiť, že recent deployment môže byť korelovaný, ale nie automaticky causal, a že healthy service status nevylučuje identity, data alebo business failure v susednej boundary.

## Kontrolné otázky

1. Kedy je restart prijateľný containment?
2. Prečo first-divergent boundary mení poradie príkazov?
3. Ako `RESOURCE:ENI` lokalizuje ECS failure?
4. Ktorý dôkaz rozlišuje lost acknowledgement od rollbacku?
5. Prečo sa SQS pri duplicate incidente nesmie purge-nuť?
6. Čo actual caller odhaľuje v KMS drille?
7. Prečo green Direct Connect neuzatvára hybrid path?
8. Ako sa CloudFront cache leak contain-ne bez otvorenia originu?
9. Prečo backup drill kontroluje copy, KMS aj restore?
10. Čo preukazuje druhý clean run?

## Oficiálna dokumentácia

- [AWS re:Post Knowledge Center](https://repost.aws/knowledge-center/)
- [AWS CLI Command Reference](https://docs.aws.amazon.com/cli/latest/reference/)
- [AWS Systems Manager Automation](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-automation.html)
- [Application Load Balancer target health](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/target-group-health-checks.html)
- [Amazon EC2 Auto Scaling instance refresh](https://docs.aws.amazon.com/autoscaling/ec2/userguide/instance-refresh-overview.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: CloudOps hands-on labs](cloudops-hands-on-labs.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Monitoring vs. observability →](../12-observability/monitoring-vs-observability.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
