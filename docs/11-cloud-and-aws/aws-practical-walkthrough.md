# Praktický AWS projekt od lokálneho artifactu po overenú Lambda release

Táto kapitola vytvorí malý serverless release, na ktorom sú viditeľné hlavné AWS hranice: account a region identity, IAM execution role, versionovaný code artifact, DynamoDB state, Lambda configuration a `CodeSha256`, immutable published version, alias ako traffic identity, CloudWatch logs, CloudTrail audit, idempotentná business operácia, failure candidate a úplný cleanup.

Lab používa iba malé on-demand resources, ale **AWS môže účtovať poplatky**. Spúšťaj ho v sandbox account-e s budget alertom, explicitným regionom a tagmi. Cleanup je povinnou časťou walkthroughu. Nepoužívaj production account ani broad administrator credentials.

```text
local source a zip checksum
→ authenticated AWS account/region
→ IAM execution capability
→ DynamoDB idempotency table
→ Lambda $LATEST code/config
→ CodeSha256 a RevisionId read-back
→ immutable published version
→ alias `live`
→ repeated business invocation
→ logs a audit evidence
→ broken candidate bez traffic impactu
→ fixed version a alias CAS update
→ cleanup
```

## Predpoklady a lab identity

Vyžaduje sa AWS CLI v2, `python3`, `zip`, `jq`, `sha256sum` a oprávnenia vytvárať IAM role/policies, Lambda functions, DynamoDB tables, CloudWatch log groups a Lambda aliases/versions.

```bash
export AWS_REGION='eu-central-1'
export AWS_PAGER=''
export LAB_ID="atlas-aws-$(date +%Y%m%d%H%M%S)"
export FUNCTION_NAME="$LAB_ID-authorizer"
export TABLE_NAME="$LAB_ID-operations"
export ROLE_NAME="$LAB_ID-lambda-role"
export POLICY_NAME="$LAB_ID-dynamodb"
export LOG_GROUP="/aws/lambda/$FUNCTION_NAME"
export AWS_LAMBDA_RUNTIME='python3.13'
```

Najprv read-backni principal a region:

```bash
aws sts get-caller-identity --output json | tee account.json
aws configure get region
ACCOUNT_ID=$(jq -r '.Account' account.json)
CALLER_ARN=$(jq -r '.Arn' account.json)
printf 'account=%s region=%s caller=%s\n' "$ACCOUNT_ID" "$AWS_REGION" "$CALLER_ARN"
```

Úspešné STS volanie dokazuje credential identity v danom čase. Nehovorí, ktoré service actions sú povolené ani či organization SCP, permission boundary alebo resource policy neskôr request nezakáže.

Všetky resources budú mať tagy:

```text
Project=KnowledgeHub
Lab=$LAB_ID
Owner=$CALLER_ARN
ExpiresAfter=2026-08-02
```

`ExpiresAfter` je iba metadata. AWS resource automaticky neodstráni bez samostatnej cleanup automation.

## 1. Pracovný adresár a Lambda source

```bash
mkdir -p "$LAB_ID"/{src,build,evidence}
cd "$LAB_ID"
```

`src/lambda_function.py`:

```python
from __future__ import annotations

import hashlib
import json
import os
from decimal import Decimal
from typing import Any

import boto3
from botocore.exceptions import ClientError

TABLE_NAME = os.environ["TABLE_NAME"]
RELEASE_ID = os.environ["RELEASE_ID"]
TABLE = boto3.resource("dynamodb").Table(TABLE_NAME)


def response(status_code: int, body: dict[str, Any]) -> dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {"content-type": "application/json"},
        "body": json.dumps(body, sort_keys=True, default=str),
    }


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    operation_id = str(event.get("operationId", ""))
    amount = int(event.get("amount", 0))

    if not operation_id:
        return response(400, {"error": "missing_operation_id", "releaseId": RELEASE_ID})
    if amount <= 0 or amount > 10_000:
        return response(400, {"error": "invalid_amount", "releaseId": RELEASE_ID})

    authorization_id = "auth-" + hashlib.sha256(operation_id.encode()).hexdigest()[:12]
    item = {
        "operationId": operation_id,
        "authorizationId": authorization_id,
        "amount": Decimal(amount),
        "status": "authorized",
        "releaseId": RELEASE_ID,
    }

    try:
        TABLE.put_item(
            Item=item,
            ConditionExpression="attribute_not_exists(operationId)",
        )
        outcome = "created"
    except ClientError as error:
        if error.response["Error"]["Code"] != "ConditionalCheckFailedException":
            raise
        current = TABLE.get_item(
            Key={"operationId": operation_id},
            ConsistentRead=True,
        ).get("Item")
        if current is None:
            raise RuntimeError("conditional failure without readable item")
        item = current
        outcome = "replayed"

    print(json.dumps({
        "event": "authorization_result",
        "operationId": operation_id,
        "authorizationId": item["authorizationId"],
        "outcome": outcome,
        "releaseId": RELEASE_ID,
        "awsRequestId": context.aws_request_id,
    }))

    return response(200, {
        "operationId": operation_id,
        "authorizationId": item["authorizationId"],
        "amount": item["amount"],
        "status": item["status"],
        "outcome": outcome,
        "releaseId": RELEASE_ID,
        "functionVersion": context.function_version,
        "awsRequestId": context.aws_request_id,
    })
```

Conditional `PutItem` s `attribute_not_exists(operationId)` zabráni prepísaniu existujúceho itemu. Pri retry funkcia načíta pôvodný business result. Condition failure preto nie je application error; je očakávaná deduplication vetva.

Lambda runtime obsahuje AWS SDK, no jeho verzia je platform input. Produkčný artifact môže vendorovať presnú SDK verziu alebo testovať podporovaný runtime contract.

## 2. Reprodukovateľný zip a lokálny checksum

```bash
cp src/lambda_function.py build/
(
  cd build
  touch -t 198001010000 lambda_function.py
  zip -X -q ../function.zip lambda_function.py
)
sha256sum function.zip | tee evidence/function.zip.sha256
LOCAL_ZIP_SHA256=$(awk '{print $1}' evidence/function.zip.sha256)
LOCAL_ZIP_SHA256_B64=$(openssl dgst -sha256 -binary function.zip | openssl base64 -A)
printf 'hex=%s\nbase64=%s\n' "$LOCAL_ZIP_SHA256" "$LOCAL_ZIP_SHA256_B64"
```

`zip -X` odstráni extra metadata a stabilný timestamp znižuje nondeterminism. Checksum opisuje lokálne bytes; Lambda API vracia `CodeSha256` v base64. Predpoklad rovnosti platí pre priamo uploadnutý zip artifact.

## 3. DynamoDB table

```bash
aws dynamodb create-table \
  --region "$AWS_REGION" \
  --table-name "$TABLE_NAME" \
  --attribute-definitions AttributeName=operationId,AttributeType=S \
  --key-schema AttributeName=operationId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --tags \
    Key=Project,Value=KnowledgeHub \
    Key=Lab,Value="$LAB_ID"

aws dynamodb wait table-exists \
  --region "$AWS_REGION" \
  --table-name "$TABLE_NAME"

TABLE_ARN=$(aws dynamodb describe-table \
  --region "$AWS_REGION" \
  --table-name "$TABLE_NAME" \
  --query 'Table.TableArn' --output text)
printf 'table_arn=%s\n' "$TABLE_ARN"
```

`table-exists` znamená, že control plane opisuje table ako dostupnú. Neoveruje IAM role funkcie ani business conditional write.

## 4. IAM execution role

`trust-policy.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {"Service": "lambda.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }
  ]
}
```

Vytvor role:

```bash
aws iam create-role \
  --role-name "$ROLE_NAME" \
  --assume-role-policy-document file://trust-policy.json \
  --tags Key=Project,Value=KnowledgeHub Key=Lab,Value="$LAB_ID"

ROLE_ARN=$(aws iam get-role \
  --role-name "$ROLE_NAME" \
  --query 'Role.Arn' --output text)
```

`dynamodb-policy.json`:

```bash
cat > dynamodb-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "OperationTable",
      "Effect": "Allow",
      "Action": ["dynamodb:PutItem", "dynamodb:GetItem"],
      "Resource": "$TABLE_ARN"
    }
  ]
}
EOF
```

```bash
aws iam put-role-policy \
  --role-name "$ROLE_NAME" \
  --policy-name "$POLICY_NAME" \
  --policy-document file://dynamodb-policy.json

aws iam attach-role-policy \
  --role-name "$ROLE_NAME" \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

Managed basic execution policy povoľuje štandardné CloudWatch Logs writes. Inline policy je obmedzená na jednu table a dve actions. IAM propagation môže byť eventual; krátky wait pred `create-function` nie je correctness oracle, iba praktická mitigation.

```bash
sleep 10
```

## 5. Vytvorenie Lambda `$LATEST`

```bash
aws lambda create-function \
  --region "$AWS_REGION" \
  --function-name "$FUNCTION_NAME" \
  --runtime "$AWS_LAMBDA_RUNTIME" \
  --role "$ROLE_ARN" \
  --handler lambda_function.handler \
  --zip-file fileb://function.zip \
  --timeout 10 \
  --memory-size 128 \
  --environment "Variables={TABLE_NAME=$TABLE_NAME,RELEASE_ID=release-001}" \
  --logging-config LogFormat=JSON,ApplicationLogLevel=INFO,SystemLogLevel=INFO \
  --tags Project=KnowledgeHub,Lab="$LAB_ID"

aws lambda wait function-active-v2 \
  --region "$AWS_REGION" \
  --function-name "$FUNCTION_NAME"
```

Read-back:

```bash
aws lambda get-function \
  --region "$AWS_REGION" \
  --function-name "$FUNCTION_NAME" \
  > evidence/function-latest.json

jq '{
  function:.Configuration.FunctionName,
  state:.Configuration.State,
  lastUpdate:.Configuration.LastUpdateStatus,
  codeSha256:.Configuration.CodeSha256,
  revisionId:.Configuration.RevisionId,
  runtime:.Configuration.Runtime,
  role:.Configuration.Role,
  environment:.Configuration.Environment.Variables
}' evidence/function-latest.json

REMOTE_CODE_SHA256=$(jq -r '.Configuration.CodeSha256' evidence/function-latest.json)
[[ "$REMOTE_CODE_SHA256" == "$LOCAL_ZIP_SHA256_B64" ]]
```

`State=Active`, `LastUpdateStatus=Successful` a matching `CodeSha256` dokazujú accepted code/config generation pre `$LATEST`. Neznamenajú, že execution role môže DynamoDB write alebo že handler funguje.

## 6. Publish immutable version a alias

Získaj optimistic concurrency identity:

```bash
REVISION_ID=$(jq -r '.Configuration.RevisionId' evidence/function-latest.json)
VERSION_1=$(aws lambda publish-version \
  --region "$AWS_REGION" \
  --function-name "$FUNCTION_NAME" \
  --code-sha256 "$REMOTE_CODE_SHA256" \
  --revision-id "$REVISION_ID" \
  --description 'release-001' \
  --query 'Version' --output text)
printf 'version=%s\n' "$VERSION_1"
```

Published Lambda version je immutable snapshot code a relevant configuration. Alias vytvorí stabilnú invocation identity:

```bash
aws lambda create-alias \
  --region "$AWS_REGION" \
  --function-name "$FUNCTION_NAME" \
  --name live \
  --function-version "$VERSION_1" \
  --description 'accepted production-like lab version'

aws lambda get-alias \
  --region "$AWS_REGION" \
  --function-name "$FUNCTION_NAME" \
  --name live | tee evidence/alias-live.json
```

Alias update je samostatný traffic/config transition. `publish-version` samo nepresmeruje clients.

## 7. Dve invocation s rovnakou operation identity

`event.json`:

```json
{
  "operationId": "aws-lab-op-001",
  "amount": 500
}
```

Prvá invocation:

```bash
aws lambda invoke \
  --region "$AWS_REGION" \
  --function-name "$FUNCTION_NAME:live" \
  --cli-binary-format raw-in-base64-out \
  --payload file://event.json \
  --log-type Tail \
  response-1.json \
  > evidence/invoke-1.json

cat response-1.json | jq -r '.body' | jq .
```

Druhá:

```bash
aws lambda invoke \
  --region "$AWS_REGION" \
  --function-name "$FUNCTION_NAME:live" \
  --cli-binary-format raw-in-base64-out \
  --payload file://event.json \
  response-2.json \
  > evidence/invoke-2.json

jq -r '.body' response-1.json | jq -S . > /tmp/body-1.json
jq -r '.body' response-2.json | jq -S . > /tmp/body-2.json
```

`awsRequestId` a `outcome` sa prirodzene líšia, preto porovnaj business identity:

```bash
AUTH_1=$(jq -r '.body' response-1.json | jq -r '.authorizationId')
AUTH_2=$(jq -r '.body' response-2.json | jq -r '.authorizationId')
[[ "$AUTH_1" == "$AUTH_2" ]]

jq -r '.body' response-1.json | jq -e '.outcome == "created"'
jq -r '.body' response-2.json | jq -e '.outcome == "replayed"'
```

Control-plane invocation response môže obsahovať function error flag. Over:

```bash
jq '{StatusCode,FunctionError,ExecutedVersion}' evidence/invoke-1.json
jq '{StatusCode,FunctionError,ExecutedVersion}' evidence/invoke-2.json
```

`ExecutedVersion` musí zodpovedať alias targetu `$VERSION_1`.

## 8. DynamoDB remote read-back

```bash
aws dynamodb get-item \
  --region "$AWS_REGION" \
  --table-name "$TABLE_NAME" \
  --key '{"operationId":{"S":"aws-lab-op-001"}}' \
  --consistent-read \
  | tee evidence/dynamodb-item.json

jq '.Item' evidence/dynamodb-item.json
```

Jeden item s očakávaným `authorizationId` podporuje exactly-once business effect pre tento lab. Table read nepovie, koľko unsuccessful attempts prebehlo; logs a CloudTrail poskytujú ďalšie evidence.

## 9. CloudWatch logs

Lambda môže vytvoriť log group pri prvej invocation. Počkaj a získaj streams:

```bash
aws logs describe-log-streams \
  --region "$AWS_REGION" \
  --log-group-name "$LOG_GROUP" \
  --order-by LastEventTime \
  --descending \
  --max-items 5

aws logs filter-log-events \
  --region "$AWS_REGION" \
  --log-group-name "$LOG_GROUP" \
  --filter-pattern 'authorization_result' \
  > evidence/log-events.json
```

Structured application log koreluje operation, authorization, release a AWS request IDs. Log presence nepreukazuje client response alebo durable state; preto sa kombinuje s invocation a DynamoDB read-backom.

Nastav krátku retention pre lab:

```bash
aws logs put-retention-policy \
  --region "$AWS_REGION" \
  --log-group-name "$LOG_GROUP" \
  --retention-in-days 1
```

## 10. CloudTrail management evidence

CloudTrail Event History býva dostupná pre management events v regione. Vyhľadaj create/publish/alias calls:

```bash
aws cloudtrail lookup-events \
  --region "$AWS_REGION" \
  --lookup-attributes AttributeKey=ResourceName,AttributeValue="$FUNCTION_NAME" \
  --max-results 50 \
  > evidence/cloudtrail-events.json

jq -r '.Events[] | [.EventTime,.EventName,.Username,.CloudTrailEvent] | @tsv' \
  evidence/cloudtrail-events.json
```

Event History môže mať delivery delay a neobsahuje automaticky Lambda data events/invocations. Je to audit control-plane evidence, nie application request log.

## 11. Broken candidate bez zmeny aliasu `live`

Vytvor chybnú `$LATEST` configuration tým, že odkáže na neexistujúcu table. Použi current RevisionId ako compare-and-swap guard:

```bash
CURRENT_REVISION=$(aws lambda get-function-configuration \
  --region "$AWS_REGION" \
  --function-name "$FUNCTION_NAME" \
  --query 'RevisionId' --output text)

aws lambda update-function-configuration \
  --region "$AWS_REGION" \
  --function-name "$FUNCTION_NAME" \
  --revision-id "$CURRENT_REVISION" \
  --environment "Variables={TABLE_NAME=missing-$TABLE_NAME,RELEASE_ID=release-broken}"

aws lambda wait function-updated-v2 \
  --region "$AWS_REGION" \
  --function-name "$FUNCTION_NAME"
```

Publish candidate version:

```bash
BROKEN_REVISION=$(aws lambda get-function-configuration \
  --region "$AWS_REGION" \
  --function-name "$FUNCTION_NAME" \
  --query 'RevisionId' --output text)

VERSION_BROKEN=$(aws lambda publish-version \
  --region "$AWS_REGION" \
  --function-name "$FUNCTION_NAME" \
  --revision-id "$BROKEN_REVISION" \
  --description 'broken candidate' \
  --query 'Version' --output text)

aws lambda create-alias \
  --region "$AWS_REGION" \
  --function-name "$FUNCTION_NAME" \
  --name candidate \
  --function-version "$VERSION_BROKEN"
```

Invoke candidate s novou operation ID a očakávaj `FunctionError` alebo handler error response podľa failure pointu:

```bash
cat > broken-event.json <<'EOF'
{"operationId":"aws-lab-broken-001","amount":500}
EOF

aws lambda invoke \
  --region "$AWS_REGION" \
  --function-name "$FUNCTION_NAME:candidate" \
  --cli-binary-format raw-in-base64-out \
  --payload file://broken-event.json \
  broken-response.json \
  > evidence/invoke-broken.json || true

jq . evidence/invoke-broken.json
cat broken-response.json
```

Over, že `live` alias stále smeruje na version 1 a pôvodná operation funguje:

```bash
aws lambda get-alias \
  --region "$AWS_REGION" \
  --function-name "$FUNCTION_NAME" \
  --name live \
  --query 'FunctionVersion' --output text
```

Toto je oddelenie artifact publication od exposure. Broken candidate existuje, ale nemá dostať live traffic.

## 12. Fix a alias compare-and-swap update

Vráť správnu table a publikuj ďalšiu version:

```bash
CURRENT_REVISION=$(aws lambda get-function-configuration \
  --region "$AWS_REGION" \
  --function-name "$FUNCTION_NAME" \
  --query 'RevisionId' --output text)

aws lambda update-function-configuration \
  --region "$AWS_REGION" \
  --function-name "$FUNCTION_NAME" \
  --revision-id "$CURRENT_REVISION" \
  --environment "Variables={TABLE_NAME=$TABLE_NAME,RELEASE_ID=release-002}"

aws lambda wait function-updated-v2 \
  --region "$AWS_REGION" \
  --function-name "$FUNCTION_NAME"

FIXED_REVISION=$(aws lambda get-function-configuration \
  --region "$AWS_REGION" \
  --function-name "$FUNCTION_NAME" \
  --query 'RevisionId' --output text)

VERSION_2=$(aws lambda publish-version \
  --region "$AWS_REGION" \
  --function-name "$FUNCTION_NAME" \
  --revision-id "$FIXED_REVISION" \
  --description 'release-002' \
  --query 'Version' --output text)
```

Candidate alias možno aktualizovať a overiť. Live transition použije alias RevisionId:

```bash
LIVE_ALIAS_REVISION=$(aws lambda get-alias \
  --region "$AWS_REGION" \
  --function-name "$FUNCTION_NAME" \
  --name live \
  --query 'RevisionId' --output text)

aws lambda update-alias \
  --region "$AWS_REGION" \
  --function-name "$FUNCTION_NAME" \
  --name live \
  --function-version "$VERSION_2" \
  --revision-id "$LIVE_ALIAS_REVISION" \
  --description 'accepted release-002'
```

`--revision-id` zabráni prepisu aliasu, ak ho medzi read a update zmenil iný writer. Po update read-backni alias a vykonaj novú operation:

```bash
aws lambda get-alias \
  --region "$AWS_REGION" \
  --function-name "$FUNCTION_NAME" \
  --name live | tee evidence/alias-live-v2.json

cat > event-v2.json <<'EOF'
{"operationId":"aws-lab-op-002","amount":700}
EOF

aws lambda invoke \
  --region "$AWS_REGION" \
  --function-name "$FUNCTION_NAME:live" \
  --cli-binary-format raw-in-base64-out \
  --payload file://event-v2.json \
  response-v2.json \
  > evidence/invoke-v2.json

jq -r '.body' response-v2.json | jq -e \
  --arg version "$VERSION_2" \
  '.releaseId == "release-002" and .functionVersion == $version'
```

## 13. Unknown invocation outcome

Ak client timeoutne po odoslaní invoke requestu, business operation mohla byť commitnutá. Neopakuj s novou operation ID. Najprv:

```bash
aws dynamodb get-item \
  --region "$AWS_REGION" \
  --table-name "$TABLE_NAME" \
  --key '{"operationId":{"S":"UNKNOWN_OPERATION_ID"}}' \
  --consistent-read
```

Potom koreluj CloudWatch log podľa operation ID. Ak item neexistuje a retry window/policy povoľuje opakovanie, použi rovnakú ID. Conditional write zabezpečí deduplication aj pri race.

## Cleanup

Odstráň aliases, function, table, policies, role a log group. Function deletion odstráni versions aj aliases, preto samostatné alias deletion nie je nutné, ale explicitný inventory je užitočný.

```bash
aws lambda list-aliases \
  --region "$AWS_REGION" \
  --function-name "$FUNCTION_NAME"
aws lambda list-versions-by-function \
  --region "$AWS_REGION" \
  --function-name "$FUNCTION_NAME"

aws lambda delete-function \
  --region "$AWS_REGION" \
  --function-name "$FUNCTION_NAME"

aws dynamodb delete-table \
  --region "$AWS_REGION" \
  --table-name "$TABLE_NAME"
aws dynamodb wait table-not-exists \
  --region "$AWS_REGION" \
  --table-name "$TABLE_NAME"

aws iam detach-role-policy \
  --role-name "$ROLE_NAME" \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam delete-role-policy \
  --role-name "$ROLE_NAME" \
  --policy-name "$POLICY_NAME"
aws iam delete-role --role-name "$ROLE_NAME"

aws logs delete-log-group \
  --region "$AWS_REGION" \
  --log-group-name "$LOG_GROUP" || true
```

Read-back, že resources neexistujú:

```bash
aws lambda get-function --region "$AWS_REGION" --function-name "$FUNCTION_NAME" || true
aws dynamodb describe-table --region "$AWS_REGION" --table-name "$TABLE_NAME" || true
aws iam get-role --role-name "$ROLE_NAME" || true
```

Nakoniec skontroluj Cost Explorer alebo billing dashboard podľa account policy. Resource deletion neznamená okamžitú finalizáciu všetkých usage records.

## Acceptance walkthroughu

```text
principal, account a region sú explicitné
resources majú lab tags a cost-bounded configuration
zip má lokálny SHA-256 a Lambda CodeSha256 match
role trust a permissions sú oddelené
DynamoDB conditional write zabráni duplicate operation
published version je immutable release subject
alias oddeľuje publication od exposure
ExecutedVersion a releaseId sa read-backnú
CloudWatch, DynamoDB a CloudTrail evidence sú korelované
broken candidate neovplyvní live alias
alias update používa RevisionId compare-and-swap
unknown outcome sa rieši operation read-backom
cleanup odstráni compute, data, IAM a logs resources
```

Walkthrough tým spája cloud identity, IAM, serverless compute, managed data, observability, audit, immutable release a recovery v jednom malom AWS projekte.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: CloudOps troubleshooting drills](cloudops-troubleshooting-drills.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: AWS troubleshooting →](aws-troubleshooting.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
