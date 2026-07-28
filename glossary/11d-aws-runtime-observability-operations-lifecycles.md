# AWS runtime, observability and operations lifecycle glossary entries

## Serverless execution subject

Versionovaná identita Lambda function, artifactu, published version/aliasu, source a event-source-mapping generation, concurrency/configuration/identity, exact eventu, downstream dependencies a business idempotency key použitá na invocation a recovery reasoning. Pozri [AWS Lambda](docs/11-cloud-and-aws/lambda.md).

## Delivery-generation identity — Lambda

Exact source resource, event-source mapping alebo asynchronous invocation configuration, filter, batching, retry, retention/visibility, destination a target version/alias, ktoré určujú delivery a acknowledgement semantics konkrétneho eventu. Pozri [AWS Lambda](docs/11-cloud-and-aws/lambda.md).

## Invocation-admission verdict — Lambda

Rozhodnutie Lambda control plane-u, či exact invocation môže byť prijatá vzhľadom na source state, permissions, regional/reserved/event-source concurrency, quotas a target version/configuration. Pozri [AWS Lambda](docs/11-cloud-and-aws/lambda.md).

## Execution-environment generation

Konkrétna Lambda runtime environment population viazaná na function version/configuration, runtime, extensions, architecture, VPC a initialization state; warm reuse nie je durable-state garancia. Pozri [AWS Lambda](docs/11-cloud-and-aws/lambda.md).

## Partial-batch acknowledgement

Event-source-mapping response contract, ktorý označí konkrétne failed records na retry namiesto celého batchu; timeout alebo strata response stále vyžaduje idempotentné spracovanie všetkých records. Pozri [AWS Lambda](docs/11-cloud-and-aws/lambda.md).

## Concurrency budget — Lambda

Maximálny bezpečný počet concurrent invocations odvodený nielen od Lambda limitov, ale aj od database connections, provider quotas, network/NAT capacity, queue lease a business deadline-u. Pozri [AWS Lambda](docs/11-cloud-and-aws/lambda.md).

## Backlog deadline

Najneskorší čas, do ktorého musí queued alebo stream event vytvoriť business outcome; queue depth alebo iterator age pod platform retention limitom ešte nemusí spĺňať business SLO. Pozri [AWS Lambda](docs/11-cloud-and-aws/lambda.md).

## Unknown side-effect outcome

Stav, keď Lambda invocation timeoutne alebo stratí downstream response po tom, čo external service mohla side effect commitnúť; pred retryom vyžaduje idempotency key a authoritative reconciliation. Pozri [AWS Lambda](docs/11-cloud-and-aws/lambda.md).

## Replay manifest — Lambda

Schválený súbor source event identity, pôvodnej delivery/function generation, attempt history, failure class, idempotency key, current business state, replay version, rate limitu a post-replay validation. Pozri [AWS Lambda](docs/11-cloud-and-aws/lambda.md).

## Serverless acceptance verdict

Closure dôkaz, že exact event prešiel approved source, version, identity a concurrency cestou, vytvoril jeden správny business outcome a duplicate, stale-version, wrong-source a uncontrolled-replay outcomes zostali zablokované. Pozri [AWS Lambda](docs/11-cloud-and-aws/lambda.md).

## Container orchestration subject

Versionovaná identita image digestu, ECS task/service alebo Kubernetes workload generation, configuration/secrets, scheduler, compute/network/storage capacity, workload identity, traffic cohort a business requestu. Pozri [Amazon ECS a Amazon EKS](docs/11-cloud-and-aws/ecs-eks.md).

## Desired-state generation — containers

Exact ECS task-definition/service deployment alebo Kubernetes API object/controller generation, ktorú orchestrator reconciliuje do runtime workload population. Pozri [Amazon ECS a Amazon EKS](docs/11-cloud-and-aws/ecs-eks.md).

## Placement verdict — containers

Scheduler decision, že task alebo Pod spĺňa viditeľné resource, attribute, topology, taint/affinity, port, volume a capacity constraints; nepreukazuje process startup, networking, readiness ani business zdravie. Pozri [Amazon ECS a Amazon EKS](docs/11-cloud-and-aws/ecs-eks.md).

## Capacity realization — containers

Premena workload desired count-u na skutočne dostupný compute, memory, architecture, ENI/Pod IP, port, storage, AZ a quota capacity contract. Pozri [Amazon ECS a Amazon EKS](docs/11-cloud-and-aws/ecs-eks.md).

## Rollout headroom — containers

Voľná compute, address, storage a target capacity potrebná na súbežné spustenie replacement cohortu, AZ failure reserve a bezpečný drain starej population počas deploymentu. Pozri [Amazon ECS a Amazon EKS](docs/11-cloud-and-aws/ecs-eks.md).

## Address-capacity boundary

Limit subnet IPv4/IPv6 addresses, ENIs, prefixes alebo Pod/task allocation modelu, ktorý môže blokovať container scale-out aj pri dostatku CPU a memory. Pozri [Amazon ECS a Amazon EKS](docs/11-cloud-and-aws/ecs-eks.md).

## Workload identity chain — containers

End-to-end authorization cesta od ECS task role alebo Kubernetes service account/Pod Identity association cez temporary credentials, IAM/SCP/boundary/resource/KMS policies po exact application API operation; host/node role je samostatná identity. Pozri [Amazon ECS a Amazon EKS](docs/11-cloud-and-aws/ecs-eks.md).

## Target-eligibility cohort — containers

Množina ECS tasks alebo Kubernetes Pods, ktoré patria k approved release generation, sú runtime-ready, registered v správnom service/load-balancer path-e a môžu bezpečne prijímať nové business requests. Pozri [Amazon ECS a Amazon EKS](docs/11-cloud-and-aws/ecs-eks.md).

## Drain completion — containers

Dôkaz, že workload už neprijíma nové traffic alebo queue leases, dokončil alebo odovzdal in-flight work, publikoval durable outcome a môže byť bezpečne zastavený alebo jeho host terminated. Pozri [Amazon ECS a Amazon EKS](docs/11-cloud-and-aws/ecs-eks.md).

## Cluster-upgrade graph — EKS

Compatibility a transition graph zahŕňajúci EKS control plane, nodes/compute model, VPC CNI/CoreDNS/kube-proxy/CSI a ďalšie add-ons, controllers/operators/CRDs, admission, clients a workloads. Pozri [Amazon ECS a Amazon EKS](docs/11-cloud-and-aws/ecs-eks.md).

## Orchestration acceptance verdict

Closure dôkaz, že approved image/workload generation bola správne umiestnená, má capacity, identity, network/storage a target eligibility, spĺňa business outcome a forbidden host-role, wrong-image, IP-exhaustion a unsafe-drain paths zostali kontrolované. Pozri [Amazon ECS a Amazon EKS](docs/11-cloud-and-aws/ecs-eks.md).

## Observability evidence subject

Exact account, Region, resource/release/request/time cohort spolu s metric, log, alarm, audit, query a automation generations potrebnými na zodpovedanie konkrétnej operational alebo security otázky. Pozri [Amazon CloudWatch a AWS CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## Metric identity contract — CloudWatch

Namespace, metric name, úplný dimension set, account/Region, unit, timestamp/resolution a publication cadence definujúce jednu CloudWatch time series a jej operational význam. Pozri [Amazon CloudWatch a AWS CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## Telemetry freshness

Dôkaz, že expected signal source publikuje a delivery/query path prijíma dáta v povolenom delay/cadence intervale; oddeľuje chýbajúcu telemetry od nulovej business hodnoty. Pozri [Amazon CloudWatch a AWS CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## Missing-data verdict — CloudWatch

Alarm decision, ako vyhodnotiť absent datapoint (`breaching`, `notBreaching`, `ignore` alebo `missing`) podľa semantics konkrétneho heartbeat, success, error alebo sporadického signálu. Pozri [Amazon CloudWatch a AWS CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## Alarm-evaluation generation

Versionovaná kombinácia metric/query identity, periodu, statistic, threshold-u, evaluation periods, datapoints-to-alarm, missing-data behavior, actions a suppression/composite logiky. Pozri [Amazon CloudWatch a AWS CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## Evidence coverage

Preukázaný set accounts, Regions, resources, event categories, log groups, metrics, cohorts a retention windows, ktoré observability/audit design skutočne zbiera; neprítomný selector alebo source nemožno nahradiť neskorším query. Pozri [Amazon CloudWatch a AWS CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## Audit-delivery contract — CloudTrail

Trail scope a event selectors spolu s S3 destination, bucket/KMS policies, integrity validation, retention, protection a monitoringom delivery failures, ktoré určujú dostupnosť audit evidence. Pozri [Amazon CloudWatch a AWS CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## Actor-session chain — CloudTrail

Rozbalená identity od CloudTrail `userIdentity` cez assumed-role ARN, principal/session issuer, source identity, user agent, source IP a upstream automation alebo human approval až po skutočného iniciátora API operácie. Pozri [Amazon CloudWatch a AWS CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## Realization gap — AWS operations

Rozdiel medzi successful control-plane API requestom zaznamenaným CloudTrailom a neskoršou controller/runtime/application realizáciou desired state-u, ktorú treba overiť service a business telemetry. Pozri [Amazon CloudWatch a AWS CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## Remediation execution subject

Exact alarm/event generation, target manifest, automation/runbook version, execution role, deduplication/cooldown, mutation, controller transition, postcondition, rollback a business validation jednej automated remediation. Pozri [Amazon CloudWatch a AWS CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## Observability acceptance verdict

Closure dôkaz, že approved telemetry a audit sources majú správnu identity, freshness, coverage, retention a actor attribution, alarm rozhoduje nad správnym cohortom a automation obnovuje business outcome bez loopu alebo straty evidence. Pozri [Amazon CloudWatch a AWS CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## Fleet-operation subject — Systems Manager

Versionovaná identita caller/session, target fleetu, managed-node enrollmentu, SSM document/runbooku, parameters, role, rate controls, command/patch/configuration generation a application validation. Pozri [AWS Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## Managed-node eligibility

Stav, v ktorom exact machine má podporovaný OS, funkčný SSM Agent, správnu instance/hybrid identity, account/Region registration, time/DNS/TLS a required service/endpoint connectivity pre konkrétnu Systems Manager capability. Pozri [AWS Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## Document generation — Systems Manager

Exact SSM document name, version, content hash, schema, parameters, platform preconditions a default-version state použitý pri command, session, association alebo Automation execution. Pozri [AWS Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## Resolved target manifest — Systems Manager

Immutable zoznam concrete managed-node alebo resource identities materializovaný z selectorov v schválenom čase a viazaný hashom na change approval, document a rate-control contract. Pozri [AWS Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## Targeting authority boundary — Systems Manager

Security a blast-radius hranica oddeľujúca oprávnenie meniť tags/resource-group membership od oprávnenia spúšťať privileged Run Command, patch alebo Automation nad targets vybranými týmito attributes. Pozri [AWS Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## Execution-delivery verdict — Systems Manager

Dôkaz, či control-plane request bol prijatý, target resolve-nutý, invocation doručená agentovi a plugin/script skutočne začal; je oddelený od exit statusu aj application outcome-u. Pozri [AWS Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## Rate-controlled fleet mutation

Fleet operation rozdelená na bounded canary/waves cez max concurrency, max errors, timeout, stop condition a application assertions tak, aby chybný command alebo selector nezmenil celý fleet naraz. Pozri [AWS Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## Patch compliance freshness

Patch verdict viazaný na exact node, OS, baseline/policy, repository/snapshot context, scan/install execution a timestamp; starý `COMPLIANT` state nie je dôkaz aktuálneho patch ani application zdravia. Pozri [AWS Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## Automation side-effect boundary — Systems Manager

Runbook step alebo external operation, po ktorej už jednoduchý reverse API call nemusí obnoviť pôvodný state; vyžaduje explicitný rollback, compensation, restore, immutable replacement alebo manual escalation. Pozri [AWS Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## Operational acceptance verdict — Systems Manager

Closure dôkaz, že exact approved targets dostali pinned document/configuration cez správnu identity a bounded execution, dosiahli technical aj business postconditions a forbidden tag-expansion, broad-role, stale-compliance a full-fleet mutation paths zostali zablokované. Pozri [AWS Systems Manager](docs/11-cloud-and-aws/systems-manager.md).
