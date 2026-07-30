# AWS Lambda

AWS Lambda poskytuje event-driven compute bez správy host fleet-u, ale nezrušuje prevádzkovú zodpovednosť. AWS vlastní provisioning execution environments, runtime platform a service scaling. Zákazník vlastní event contract, function version, concurrency budget, retry a replay model, network, secrets, downstream capacity a business idempotency.

```text
business event
→ source and delivery generation
→ invocation admission
→ function version or alias
→ execution-environment init
→ handler and downstream side effects
→ acknowledgement or unknown outcome
→ retry, backlog, destination or replay
→ reconciliation and business result
```

Lambda sa neposudzuje otázkou „funkcia beží?“. Posudzuje sa, či exact event prešiel správnou source, version, identity a capacity cestou a či duplicate delivery nevytvorila duplicate side effect.

## 1. Exact serverless subject

Atlas Payments používa function `payments-settle`, published version `84`, production alias `live`, artifact digest `sha256:lambda-pay-7-16-0`, execution role `ROLE-LAMBDA-PAY-18` a resource-policy generation `RP-LAMBDA-PAY-7`.

Source je SQS queue `payments-settlement`, generation `QUEUE-PAY-22`, event-source mapping `ESM-PAY-12`, batch size 10, partial batch response enabled, visibility timeout 180 sekúnd a maximum source concurrency 40. Reserved concurrency je 50, provisioned concurrency na alias `live` je 8, function timeout 90 sekúnd a memory 1 024 MiB.

Event `S-884` používa business idempotency key `settle-S884`. Accepted outcome je jeden provider settlement, jeden ledger transition a jeden outbox event. Warm `/tmp` alebo global variable nesmie byť authoritative state.

## 2. Function, version, alias a execution environment

Function je code/config resource. Published version je immutable snapshot podporovaných properties. Alias je mutable pointer na version a môže mať weighted routing. Invocation je jeden attempt. Execution environment je runtime container, ktorý Lambda môže reuse-nuť pre viac sequential invocations.

```text
create environment
→ Init runtime, extensions and static code
→ Invoke handler
→ freeze
→ possible warm reuse
→ Shutdown or replacement
```

Warm reuse je performance optimization. Global SDK client alebo cache možno reuse-nuť, ale in-memory deduplication sa stratí pri replacement-e a nesmie chrániť financial invariant.

## 3. Function a alias v Terraform-e

```hcl
resource "aws_lambda_function" "settlement" {
  function_name = "payments-settle"
  role          = aws_iam_role.lambda_settlement.arn

  package_type = "Zip"
  filename     = "build/payments-settle.zip"
  source_code_hash = filebase64sha256("build/payments-settle.zip")

  runtime = "python3.13"
  handler = "handler.main"
  memory_size = 1024
  timeout     = 90

  reserved_concurrent_executions = 50

  environment {
    variables = {
      CONFIG_GENERATION = "CFG-PAY-84"
      LEDGER_TABLE      = aws_dynamodb_table.settlement_ledger.name
      PROVIDER_SECRET   = aws_secretsmanager_secret.provider.arn
    }
  }

  vpc_config {
    subnet_ids         = values(aws_subnet.application)[*].id
    security_group_ids = [aws_security_group.lambda.id]
  }

  publish = true

  tags = {
    ArtifactDigest = "sha256:lambda-pay-7-16-0"
  }
}

resource "aws_lambda_alias" "live" {
  name             = "live"
  function_name    = aws_lambda_function.settlement.function_name
  function_version = aws_lambda_function.settlement.version
}

resource "aws_lambda_provisioned_concurrency_config" "live" {
  function_name                     = aws_lambda_function.settlement.function_name
  qualifier                         = aws_lambda_alias.live.name
  provisioned_concurrent_executions = 8
}
```

`source_code_hash` vytvára Terraform diff pri zmene package bytes. Published version a alias dávajú production stabilnú identity. `$LATEST` nie je vhodná production release identity.

## 4. Event source mapping

```hcl
resource "aws_lambda_event_source_mapping" "settlement" {
  event_source_arn = aws_sqs_queue.settlement.arn
  function_name    = aws_lambda_alias.live.arn

  batch_size                         = 10
  maximum_batching_window_in_seconds = 1
  function_response_types            = ["ReportBatchItemFailures"]
  scaling_config {
    maximum_concurrency = 40
  }

  enabled = true
}
```

Mapping identity je samostatný release input. Queue môže byť recreated s novým ARN alebo visibility timeoutom, zatiaľ čo function code ostane rovnaký. Deployment gate musí porovnať exact queue ARN, mapping UUID, alias target, timeout a partial-batch configuration.

Live read-back:

```bash
aws lambda list-event-source-mappings \
  --function-name payments-settle:live \
  --event-source-arn "$QUEUE_ARN" \
  --region eu-central-1 \
  --query 'EventSourceMappings[].{UUID:UUID,State:State,FunctionArn:FunctionArn,BatchSize:BatchSize,ResponseTypes:FunctionResponseTypes,Scaling:ScalingConfig,LastResult:LastProcessingResult}'
```

Mapping `Enabled` nepreukazuje, že messages sa spracúvajú alebo že source acknowledgement je bezpečné.

## 5. Invocation model určuje retry ownera

Synchronous invocation vracia response callerovi a retry typicky vlastní caller/SDK. Asynchronous invocation používa service-managed queue a Lambda retry/event-age configuration. Poll-based mapping pre SQS/streams používa source-specific batching, lease/checkpoint a redelivery semantics.

SQS path:

```text
message visible
→ poller receives batch
→ visibility lease
→ synchronous function invoke
→ handler success/failure response
→ message delete or visibility expiry
→ possible redelivery
```

At-least-once delivery znamená, že duplicate attempt je normálny failure mode. Request ID nového attemptu sa môže zmeniť, preto nie je business key.

## 6. Idempotentný handler

Nasledujúci Python skeleton používa DynamoDB conditional claim a stable provider key. Je to didaktický pattern; production code potrebuje typed payload validation, structured errors, timeouts a observability.

```python
from __future__ import annotations

import json
import os
from typing import Any

import boto3
from botocore.exceptions import ClientError

ledger = boto3.resource("dynamodb").Table(os.environ["LEDGER_TABLE"])


def claim_operation(operation_id: str) -> bool:
    try:
        ledger.put_item(
            Item={"operationId": operation_id, "state": "PROCESSING"},
            ConditionExpression="attribute_not_exists(operationId)",
        )
        return True
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return False
        raise


def process_record(record: dict[str, Any]) -> None:
    body = json.loads(record["body"])
    operation_id = body["idempotencyKey"]

    if not claim_operation(operation_id):
        existing = ledger.get_item(Key={"operationId": operation_id}).get("Item")
        if existing and existing.get("state") == "COMPLETED":
            return
        raise RuntimeError(f"Operation {operation_id} is not safely complete")

    provider_settle(body, idempotency_key=operation_id)
    ledger.update_item(
        Key={"operationId": operation_id},
        UpdateExpression="SET #state = :state",
        ExpressionAttributeNames={"#state": "state"},
        ExpressionAttributeValues={":state": "COMPLETED"},
    )


def main(event: dict[str, Any], context: Any) -> dict[str, Any]:
    failures: list[dict[str, str]] = []

    for record in event["Records"]:
        try:
            process_record(record)
        except Exception:
            failures.append({"itemIdentifier": record["messageId"]})

    return {"batchItemFailures": failures}
```

Conditional claim zabráni dvom workers súčasne vytvoriť independent processing authority. Samotný `PROCESSING` state potrebuje timeout/lease a reconciliation pre crash po provider success-e. Provider musí akceptovať rovnaký idempotency key.

Partial batch response znižuje zbytočný replay úspešných records. Neodstraňuje duplicate delivery pri timeout-e pred response.

## 7. Visibility timeout a function timeout

Visibility timeout musí byť dlhší než worst-case handler execution a retry margin. Ak message znovu zviditeľnie, kým prvý attempt ešte pracuje, vzniknú concurrent attempts.

Read-back:

```bash
aws sqs get-queue-attributes \
  --queue-url "$QUEUE_URL" \
  --attribute-names VisibilityTimeout RedrivePolicy ApproximateNumberOfMessages ApproximateNumberOfMessagesNotVisible \
  --region eu-central-1

aws lambda get-function-configuration \
  --function-name payments-settle:live \
  --region eu-central-1 \
  --query '{Version:Version,Timeout:Timeout,Memory:MemorySize,Role:Role,Vpc:VpcConfig,Env:Environment.Variables.CONFIG_GENERATION}'
```

Function timeout nie je downstream cancellation guarantee. External provider mohol operation commitnúť pred Lambda timeoutom. Retry musí najprv reconcile-nuť podľa idempotency keyu.

## 8. Concurrency ako admission a blast-radius control

Approximate concurrency demand je arrival rate × average duration. Každá invocation môže držať DB/proxy connection, NAT port a provider request.

Reserved concurrency zároveň rezervuje a limituje function. Hodnota nula administratívne zastaví invocations. Provisioned concurrency pripravuje environments pre version/alias a rieši startup latency, nie downstream rate limit.

Read-back:

```bash
aws lambda get-function-concurrency \
  --function-name payments-settle \
  --region eu-central-1

aws lambda get-provisioned-concurrency-config \
  --function-name payments-settle \
  --qualifier live \
  --region eu-central-1
```

Zvýšenie 50 → 500 môže odstrániť `Throttles` a preťažiť database/provider. Správny limit vychádza z celého dependency chainu.

## 9. VPC attachment

VPC-attached Lambda používa selected subnets a Security Groups pre private connectivity. Public subnet sám nevytvorí internet egress; potrebuje NAT alebo endpoint path.

```text
execution environment network path
→ subnet IP capacity
→ Security Group and NACL
→ NAT or VPC endpoint
→ endpoint/resource policy
→ destination
```

Scale-out môže zlyhať na IP headroome alebo downstream connection budgete. Function configuration `VpcConfig` je control-plane evidence, nie runtime connection test.

## 10. Execution role a resource policy

Execution role určuje, čo handler môže volať. Function resource policy určuje, kto môže function invoke-nuť.

```bash
aws lambda get-policy \
  --function-name payments-settle \
  --region eu-central-1

aws iam list-attached-role-policies \
  --role-name payments-lambda-runtime
```

Trigger configuration bez invoke permission môže zostať nefunkčná. Broad execution role nevyrieši missing source permission a zvyšuje blast radius compromised code-u.

## 11. Alias promotion a rollback

Canary alias update:

```bash
aws lambda update-alias \
  --function-name payments-settle \
  --name live \
  --function-version 85 \
  --routing-config 'AdditionalVersionWeights={"84"=0.9}' \
  --region eu-central-1
```

CLI shape znamená, že primary alias version je 85 a 90 % môže smerovať na 84; weights treba vždy čítať presne. V praxi nastav canary intuitívne cez deployment tool a read-back:

```bash
aws lambda get-alias \
  --function-name payments-settle \
  --name live \
  --region eu-central-1
```

Weighted routing je probabilistic a nie každá event integration používa alias rovnako ako direct invoke. Logs musia niesť executed version. Alias rollback nevracia provider side effects ani queue checkpoint.

## 12. Observability

Platform metrics zahŕňajú Invocations, Errors, Throttles, Duration, ConcurrentExecutions, IteratorAge alebo queue metrics podľa source. Structured log viaže event ID, message ID, function version, attempt, idempotency key, result a request ID.

```python
print(json.dumps({
    "event": "settlement_attempt",
    "operationId": operation_id,
    "functionVersion": os.environ.get("AWS_LAMBDA_FUNCTION_VERSION"),
    "configGeneration": os.environ["CONFIG_GENERATION"],
    "outcome": "completed",
}))
```

Secret value alebo full payment payload sa neloguje. `Errors=0` môže koexistovať so swallowed exception alebo backlogom; business ledger zostáva authoritative oracle.

## 13. Replay manifest

DLQ alebo source replay sa nevykonáva príkazom „reprocess all“. Manifest obsahuje source record identity/checksum, failed function version, attempt history, business key, current state, approved replay version, concurrency a stop criteria.

```json
{
  "replayId": "REPLAY-S884-2",
  "sourceQueueArn": "arn:aws:sqs:eu-central-1:100000000042:payments-settlement-dlq",
  "operationIds": ["settle-S884"],
  "approvedFunctionVersion": "85",
  "maximumConcurrency": 2,
  "stopOnDuplicateProviderOutcome": true
}
```

Permanent validation alebo authorization failure sa replayom bez opravy nezmení.

## 14. Worked incident: visibility timeout vytvorí concurrent duplicate

Po release 7.16.0 rástol backlog a provider hlásil duplicate settlement attempts. CloudWatch ukazoval nízke throttles, duration p95 85 sekúnd a rastúci SQS receive count.

Approved queue generation mala visibility 180 sekúnd, no migration recreated queue ako `QUEUE-PAY-23` s 60 sekundami. Attempt 1 poslal provider settlement, potom ledger write čakal na lock. Po 60 sekundách message znovu zviditeľnela a attempt 2 začal súčasne. Provider request nepoužil stable idempotency key.

Containment znížil reserved/mapping concurrency, pozastavil event-source mapping a zachoval queue/provider/ledger evidence. Queue sa nepurge-nula.

Recovery nastavila visibility podľa worst-case execution, handler urobil atomic claim pred provider callom, provider používal `settle-S884` a partial batch response. Replay version 85 bežala s bounded concurrency.

Acceptance vyžadovala jeden completion marker, jeden provider settlement, bounded receive count, controlled backlog drain a forbidden duplicate event test.

## 15. Troubleshooting order

Ak function neinvokuje, over source event, mapping state/filter, invoke permission, alias/version a reserved concurrency. Ak timeoutuje, oddeľ Init, handler CPU/memory, DNS/network, secret fetch, connection acquisition, provider a lock wait. Ak SQS opakuje records, over queue generation, visibility, duration, batch response a idempotency.

```bash
aws lambda get-event-source-mapping \
  --uuid "$MAPPING_UUID" \
  --region eu-central-1
```

Control-plane state je prvý observation point, nie posledný.

## Kontrolné otázky

1. Aký rozdiel je medzi function, version, alias a execution environment?
2. Prečo warm memory nie je durable state?
3. Kto vlastní retry pri SQS event-source mappingu?
4. Prečo request ID nie je business idempotency key?
5. Čo partial batch response rieši a čo nevyrieši?
6. Ako visibility timeout súvisí s function timeoutom?
7. Prečo reserved concurrency chráni aj obmedzuje?
8. Aký rozdiel je medzi execution role a resource policy?
9. Prečo alias rollback nevráti external side effects?
10. Aký dôkaz uzavrie duplicate-settlement incident?

## Oficiálna dokumentácia

- [AWS Lambda Developer Guide](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)
- [Execution environment lifecycle](https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtime-environment.html)
- [Invocation methods](https://docs.aws.amazon.com/lambda/latest/dg/lambda-invocation.html)
- [Event source mappings](https://docs.aws.amazon.com/lambda/latest/dg/invocation-eventsourcemapping.html)
- [SQS event source](https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html)
- [Lambda concurrency](https://docs.aws.amazon.com/lambda/latest/dg/lambda-concurrency.html)
- [Lambda aliases](https://docs.aws.amazon.com/lambda/latest/dg/configuration-aliases.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Route 53 a CloudFront](route53-cloudfront.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: ECS a EKS →](ecs-eks.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
