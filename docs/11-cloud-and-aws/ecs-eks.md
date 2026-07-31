# Amazon ECS a Amazon EKS

Amazon ECS a Amazon EKS realizujú desired container workload na compute, network, storage a identity resources. ECS používa AWS-native task a service control plane. EKS poskytuje managed Kubernetes control plane a zachováva Kubernetes API, controllers a ecosystem. Rozdiel preto nie je iba „jednoduché verzus pokročilé“. Mení sa authoritative desired state, scheduler evidence, capacity ownership, workload identity, upgrade surface aj spôsob, ktorým sa dokazuje effective runtime.

Oba orchestrátory sledujú podobný business lifecycle, ale každý ho realizuje cez iné controllers a objekty:

```text
business release intent
→ immutable image a workload specification
→ orchestrator desired-state generation
→ scheduler placement
→ compute, network a storage realization
→ workload identity a configuration
→ process startup a readiness
→ service alebo target eligibility
→ traffic a business outcome
→ scaling, rollout, drain a retirement
```

Stav `RUNNING`, Kubernetes `Ready` alebo Deployment `Available` sú iba medzistavy. Closure vyžaduje read-back schváleného image/configuration subjectu, dôkaz serving pathu a business operáciu, ktorá prejde bez forbidden side effectu.

## 1. Exact container subject

Atlas Payments release `7.17.0` používa image digest `sha256:pay-api-7-17-0`, configuration `CFG-PAY-52`, secret generation `SEC-PAY-39`, database proxy `PROXY-10` a load balancer `ALB-PAY-18`. Tieto identity tvoria application generation; názov `payments-api` bez digestu, configuration a secret epoch nestačí na rozlíšenie dvoch súbežných cohortov.

ECS realization používa cluster `payments-prod`, service `payments-api`, task definition `payments-api:118`, deployment `ECS-DEP-73`, capacity provider `payments-managed-instances-v4`, network mode `awsvpc`, task role `ROLE-ECS-PAY-21`, execution role `ROLE-ECS-EXEC-14` a desired count 40. EKS realization používa cluster `payments-eks-prod`, namespace `payments`, Deployment `payments-api`, ReplicaSet `RS-PAY-219`, Service `SVC-PAY-31`, ServiceAccount `payments-api`, Pod Identity association `PODID-PAY-9`, compute generation `NODEPOOL-PAY-17` a VPC CNI generation `CNI-31`.

Accepted outcome je 40 traffic-eligible workloadov rozložených cez tri Availability Zones, least-privilege workload identity a úspešná payment `P-901`. Host alebo node role leakage, subnet IP exhaustion, mismatch medzi readiness a target eligibility a duplicate payment počas drainu sú explicitne forbidden outcomes.

## 2. ECS authority graph

Task definition je immutable runtime template. ECS service odkazuje na konkrétnu task-definition revision, drží desired count a vytvára deployment cohorts; scheduler následne hľadá capacity, na ktorej môže task realizovať. Application container ešte neexistuje, kým placement, ENI, storage, image pull a execution-role operácie neprejdú.

```text
task-definition revision
→ ECS service desired state
→ service deployment
→ scheduler a capacity provider
→ task placement
→ ENI, volumes, logs a platform credentials
→ container startup
→ target registration a health
→ client traffic a business outcome
```

Service event a stopped-task reason sú preto authoritative evidence pre failure pred application startupom. Application logs sú relevantné až vtedy, keď container vznikol a log driver alebo sidecar dokázal output doručiť. Green task count naopak nepreukazuje load-balancer routing ani správny business outcome.

## 3. ECS task definition v Terraform-e

Nasledujúca task definition pinne image digest, oddeľuje execution a task role, používa `awsvpc` networking a explicitne identifikuje configuration generation. Terraform resource vytvorí novú revision, keď sa runtime contract zmení; sám však neaktualizuje service na novú revision bez zodpovedajúcej service mutation.

```hcl
resource "aws_ecs_task_definition" "payments" {
  family                   = "payments-api"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 1024
  memory                   = 2048
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = "payments-api"
      image     = "100000000042.dkr.ecr.eu-central-1.amazonaws.com/payments-api@sha256:pay-api-7-17-0"
      essential = true

      portMappings = [{
        name          = "http"
        containerPort = 8080
        protocol      = "tcp"
      }]

      environment = [{
        name  = "CONFIG_GENERATION"
        value = "CFG-PAY-52"
      }]

      secrets = [{
        name      = "DATABASE_URL"
        valueFrom = aws_secretsmanager_secret.database.arn
      }]

      healthCheck = {
        command     = ["CMD-SHELL", "curl -fsS http://127.0.0.1:8080/readyz || exit 1"]
        interval    = 10
        timeout     = 5
        retries     = 3
        startPeriod = 30
      }

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.payments.name
          awslogs-region        = "eu-central-1"
          awslogs-stream-prefix = "payments"
        }
      }
    }
  ])
}
```

Execution role používa ECS agent alebo Fargate platforma na image pull, log delivery a secret injection podľa použitých features. Task role credentials dostáva application container a používa ich AWS SDK. Zámena týchto identít spôsobí buď startup failure, keď agent nemá potrebnú authority, alebo privilege leakage, keď application získa platformové permissions.

Po registrácii treba prečítať exact revision a container contract:

```bash
aws ecs describe-task-definition \
  --task-definition payments-api:118 \
  --region eu-central-1 \
  --query 'taskDefinition.{Revision:revision,ExecutionRole:executionRoleArn,TaskRole:taskRoleArn,NetworkMode:networkMode,Containers:containerDefinitions[].{Name:name,Image:image,Secrets:secrets,Health:healthCheck}}' \
  --output yaml
```

Tento read-back dokazuje uložený ECS template. Nedokazuje, že service revision používa, že task image skutočne stiahol ani že application načítala očakávaný secret value.

## 4. ECS service, rollout a load balancer

ECS service je controller nad desired task countom a deployment cohorts. `minimumHealthyPercent` a `maximumPercent` určujú, koľko starej capacity musí zostať a koľko dočasnej surge capacity môže rollout vytvoriť. Tieto percentá preto priamo závisia od subnet IP, compute a downstream headroomu.

```hcl
resource "aws_ecs_service" "payments" {
  name            = "payments-api"
  cluster         = aws_ecs_cluster.payments.id
  task_definition = aws_ecs_task_definition.payments.arn
  desired_count   = 40

  deployment_minimum_healthy_percent = 100
  deployment_maximum_percent         = 125
  health_check_grace_period_seconds  = 120

  network_configuration {
    subnets          = values(aws_subnet.application)[*].id
    security_groups  = [aws_security_group.application.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.payments.arn
    container_name   = "payments-api"
    container_port   = 8080
  }

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }
}
```

Circuit breaker môže označiť rolling ECS deployment ako failed a pri zapnutom rollbacku vrátiť service na posledný completed deployment. Nevráti database schema, queue messages, provider authorizations ani iné external side effects. Rollback eligibility sa preto musí overiť voči data a business generation, nie iba task-definition revision.

Live read-back oddeľuje desired count, current cohorts a event history:

```bash
aws ecs describe-services \
  --cluster payments-prod \
  --services payments-api \
  --region eu-central-1 \
  --query 'services[0].{Desired:desiredCount,Running:runningCount,Pending:pendingCount,TaskDefinition:taskDefinition,Deployments:deployments,Events:events[0:10]}' \
  --output yaml
```

Ak `runningCount` dosiahne 40, scheduler a runtime vytvorili tasky, ale target eligibility ešte môže zlyhať. Nasleduje target-health read-back, request cez intended listener rule a payment canary s release identity v response alebo trace.

## 5. ECS task diagnosis a image read-back

Task-level diagnosis musí porovnať desired service generation s reálne spustenými taskmi. `describe-tasks` vracia availability zone, lifecycle, health, task definition, container reason a image digest, čím odlišuje placement, image pull, process exit a mixed-generation failure.

```bash
TASK_ARNS=$(aws ecs list-tasks \
  --cluster payments-prod \
  --service-name payments-api \
  --region eu-central-1 \
  --query 'taskArns' \
  --output text)

aws ecs describe-tasks \
  --cluster payments-prod \
  --tasks $TASK_ARNS \
  --region eu-central-1 \
  --query 'tasks[].{Task:taskArn,State:lastStatus,Health:healthStatus,TaskDefinition:taskDefinitionArn,Az:availabilityZone,StoppedReason:stoppedReason,Containers:containers[].{Name:name,State:lastStatus,Exit:exitCode,Reason:reason,ImageDigest:imageDigest}}' \
  --output yaml
```

Image digest read-back spája runtime s approved artifact a odhaľuje mutable-tag alebo cache divergence. Container `RUNNING` však nepreukazuje application readiness; ECS `HEALTHY` môže byť container health-check verdict, ktorý sa líši od ALB target healthu a od business canary výsledku.

Pri stopped tasku treba zachovať reason, exit code, release a relevantný log interval pred opakovaným rolloutom. Hromadný restart bez tejto evidence môže odstrániť jediný dôkaz, či zlyhal execution role, image, secret injection alebo application process.

## 6. ECS capacity providers a oddelené control loops

Capacity provider spája ECS scheduler s Fargate, Fargate Spot, ECS Managed Instances alebo EC2 Auto Scaling capacity. Service desired count a host capacity sú oddelené control loops: service žiada tasky, capacity layer sa ich pokúša realizovať a scheduler reportuje, prečo placement neprešiel.

Fargate odstráni customer-managed node fleet, ale workload stále vlastní task sizing, ENI a subnet capacity, IAM roles, storage, rollout a cost. ECS Managed Instances preberajú väčšiu časť EC2 provisioning a patch lifecycle-u. Capacity provider nad vlastným Auto Scaling group necháva tímu AMI, ECS agent, OS patching, instance role, drain a replacement policy.

Service môže zostať `PENDING` bez jediného application logu, pretože process ešte nevznikol. V takom prípade sa najprv čítajú service events, capacity-provider strategy, placement failures, subnet IP headroom a quota; container command sa analyzuje až po úspešnom placement a startup boundary.

```bash
aws ecs describe-capacity-providers \
  --capacity-providers payments-managed-instances-v4 \
  --region eu-central-1 \
  --output yaml

aws ecs describe-clusters \
  --clusters payments-prod \
  --include ATTACHMENTS CONFIGURATIONS SETTINGS STATISTICS \
  --region eu-central-1 \
  --output yaml
```

Tieto príkazy čítajú capacity-provider a cluster control-plane state. Nezaručujú konkrétnu host alebo Fargate capacity v čase placementu; tú potvrdzujú task events a úspešný canary task.

## 7. EKS authority graph

EKS spravuje Kubernetes API server a súvisiaci control plane, ale zákazník stále vlastní desired Kubernetes objects, cluster access, RBAC, admission, add-ons, compute, workload networking, storage topology, upgrades a business recovery. Successful EKS API call preto dokazuje iba prijatie alebo prečítanie objectu, nie controller convergence.

```text
Kubernetes manifest
→ API authentication a authorization
→ admission a persisted object
→ controller reconciliation
→ scheduler Pod binding
→ kubelet a container runtime
→ CNI a CSI realization
→ Service, Ingress alebo target eligibility
→ application a business outcome
```

Každá boundary má vlastné evidence. API object status patrí controlleru, Pod events scheduleru a kubeletu, CNI logs network realization, EndpointSlice Service pathu a external canary používateľskému outcome-u. Preskočenie boundary vedie napríklad k analýze Service selectoru, hoci Pod ešte nemá IP adresu.

## 8. Kubernetes Deployment a Service

Deployment nižšie požaduje 40 replicas, nulový voluntary unavailability počas rollout-u a surge do 25 %. Topology constraint vyžaduje vyváženie cez zones a pri chýbajúcej capacity radšej ponechá Pods Pending, než aby potichu vytvoril single-AZ cohort.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payments-api
  namespace: payments
  labels:
    app.kubernetes.io/name: payments-api
    app.kubernetes.io/version: "7.17.0"
spec:
  replicas: 40
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 0
      maxSurge: 25%
  selector:
    matchLabels:
      app.kubernetes.io/name: payments-api
  template:
    metadata:
      labels:
        app.kubernetes.io/name: payments-api
        app.kubernetes.io/version: "7.17.0"
    spec:
      serviceAccountName: payments-api
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: DoNotSchedule
          labelSelector:
            matchLabels:
              app.kubernetes.io/name: payments-api
      containers:
        - name: payments-api
          image: 100000000042.dkr.ecr.eu-central-1.amazonaws.com/payments-api@sha256:pay-api-7-17-0
          ports:
            - name: http
              containerPort: 8080
          env:
            - name: CONFIG_GENERATION
              value: CFG-PAY-52
          resources:
            requests:
              cpu: 500m
              memory: 512Mi
            limits:
              memory: 1Gi
          readinessProbe:
            httpGet:
              path: /readyz
              port: http
            periodSeconds: 5
          lifecycle:
            preStop:
              exec:
                command: ["/app/drain", "--timeout=90s"]
      terminationGracePeriodSeconds: 120
---
apiVersion: v1
kind: Service
metadata:
  name: payments-api
  namespace: payments
spec:
  selector:
    app.kubernetes.io/name: payments-api
  ports:
    - name: http
      port: 80
      targetPort: http
```

Readiness odstraňuje unready Pod z bežných Service endpoints, ale nepreukazuje external load-balancer registration ani správny business response. `preStop` a termination grace vytvárajú čas na drain; application musí napriek tomu koordinovať in-flight requesty alebo queue leases a používať idempotency pri neznámom výsledku.

## 9. EKS access entries a Pod Identity

Human alebo automation access do Kubernetes API a workload AWS identity sú dve rozdielne authority paths. EKS access entry viaže IAM principal na EKS access policy alebo Kubernetes authorization context. Pod Identity association viaže IAM role na namespace a ServiceAccount, aby AWS SDK v Pode získalo workload credentials.

```text
operator IAM session
→ EKS authentication
→ access entry alebo iný configured authentication path
→ EKS access policy/Kubernetes RBAC
→ Kubernetes API request
```

```text
Pod namespace + ServiceAccount
→ Pod Identity association
→ Pod Identity Agent credential delivery
→ workload IAM role session
→ AWS service API request
```

Association sa vytvorí pre exact cluster, namespace, ServiceAccount a role:

```bash
aws eks create-pod-identity-association \
  --cluster-name payments-eks-prod \
  --namespace payments \
  --service-account payments-api \
  --role-arn arn:aws:iam::100000000042:role/payments-pod-runtime \
  --region eu-central-1

aws eks list-pod-identity-associations \
  --cluster-name payments-eks-prod \
  --namespace payments \
  --service-account payments-api \
  --region eu-central-1
```

List read-back dokazuje association record, nie credential použitý konkrétnym Podom. Live caller sa overí z affected workload generation:

```bash
kubectl -n payments exec deploy/payments-api -- \
  aws sts get-caller-identity
```

Výsledok musí ukázať workload role session, nie node instance role. Positive AWS API test sa doplní forbidden testom voči nepovolenému resource-u a fresh Podom po rotation; inak môže stale credential cache zakryť chybnú association.

## 10. Scheduler, kubelet a runtime diagnosis

Kubernetes Deployment status sumarizuje controller progress, nie príčinu každého Pod failure. Diagnostika preto najprv číta Deployment a ReplicaSets a potom konkrétne Pods a events podľa generation.

```bash
kubectl -n payments get deploy payments-api -o wide
kubectl -n payments rollout status deploy/payments-api --timeout=5m
kubectl -n payments get rs -l app.kubernetes.io/name=payments-api

kubectl -n payments get pods \
  -l app.kubernetes.io/name=payments-api \
  -o custom-columns='NAME:.metadata.name,PHASE:.status.phase,NODE:.spec.nodeName,POD-IP:.status.podIP,IMAGE:.spec.containers[0].image,READY:.status.containerStatuses[0].ready'

kubectl -n payments describe pod "$POD"
kubectl -n payments get events --sort-by=.lastTimestamp | tail -50
```

Pod `Pending` bez `spec.nodeName` smeruje na scheduler constraints, resources, taints, topology alebo unbound PVC. Bound Pod, ktorý nevstúpil do Running, smeruje na kubelet, image pull, CNI, CSI alebo runtime. Running, ale unready Pod posúva first divergence do application readiness alebo dependency pathu.

`kubectl rollout status` preukazuje Deployment controller verdict. Neoveruje Service selector, EndpointSlice, ingress/load balancer ani business journey. Closure preto pokračuje cez serving path namiesto ukončenia pri `successfully rolled out`.

## 11. Service, EndpointSlice a request path

Kubernetes Service je stabilná virtual identity a selector contract. EndpointSlice materializuje backend addresses a readiness conditions, ktoré Service data plane môže použiť. Prázdny EndpointSlice preto často znamená selector alebo readiness divergence, nie DNS alebo external load-balancer problém.

```bash
kubectl -n payments get svc payments-api -o yaml
kubectl -n payments get endpointslice \
  -l kubernetes.io/service-name=payments-api \
  -o yaml
```

Service read-back musí porovnať selector s Pod labels a `targetPort` s named container portom. EndpointSlice potvrdzuje selected addresses a conditions, ale nepreukazuje kube-proxy/eBPF dataplane ani application response.

In-cluster request cez Service izoluje external ingress boundary:

```bash
kubectl -n payments run curl-test \
  --rm -it --restart=Never \
  --image=curlimages/curl:8.10.1 -- \
  curl -fsS http://payments-api/readyz
```

Ak direct PodIP funguje a Service request nie, first divergence je selector, EndpointSlice alebo Service dataplane. Ak Service funguje, ale external request nie, diagnostika sa presúva na load balancer controller, targets, listener, DNS a TLS.

## 12. VPC CNI a IP capacity

Amazon VPC CNI realizuje Pod networking na EC2 nodes a prideľuje Podom adresy z VPC podľa configured mode. Scheduler môže Pod bindnúť na Node skôr, než CNI úspešne vytvorí Pod sandbox a pridelí address; preto scheduled Pod ešte nemusí mať funkčnú sieť.

```text
Pod binding
→ kubelet sandbox request
→ CNI address/ENI alebo prefix allocation
→ network namespace a routes
→ security policy
→ DNS, Service a external path
```

Subnet free addresses, contiguous prefixes pri prefix delegation, node ENI limits a warm-pool settings určujú real Pod capacity. Pridanie Nodes môže shortage zhoršiť, pretože Nodes aj ich warm pools spotrebujú ďalšie adresy.

```bash
kubectl -n kube-system get ds aws-node -o wide
kubectl -n kube-system logs ds/aws-node -c aws-node --tail=200

aws ec2 describe-subnets \
  --subnet-ids subnet-0paya subnet-0payb subnet-0payc \
  --region eu-central-1 \
  --query 'Subnets[].{Subnet:SubnetId,Az:AvailabilityZoneId,Free:AvailableIpAddressCount}' \
  --output table
```

DaemonSet status ukazuje, či CNI agent beží na intended nodes; logs ukážu allocation failure. Subnet output poskytuje aggregate free-IP observation, ale nepreukazuje contiguous `/28` availability, node-level ENI slots ani správny custom-networking selector. Recovery musí prečítať effective CNI configuration a spustiť canary Pod v každej zone.

## 13. NetworkPolicy a Security Group layers

Kubernetes NetworkPolicy opisuje allowed Pod traffic iba vtedy, keď ju použitý network dataplane enforce-uje. Security Groups vyhodnocujú AWS network identity na ENI alebo podporovanom Pod networking modeli. Obe vrstvy môžu byť súčasne potrebné a ani jedna sama nepredstavuje celý DNS-to-application path.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: payments-default-deny
  namespace: payments
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: payments-allow-api
  namespace: payments
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: payments-api
  policyTypes: [Ingress]
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: ingress-system
      ports:
        - protocol: TCP
          port: 8080
```

Manifest presence dokazuje desired policy object, nie enforcement. Positive test musí prejsť z povoleného namespace a forbidden test musí zlyhať z nepovoleného namespace alebo identity. Pri zlyhaní treba odlíšiť DNS, NetworkPolicy, Security Group, route a application listener, nie pridávať broad allow do všetkých vrstiev naraz.

## 14. Storage, topology a state authority

PVC môže byť bound na zonal volume, ktoré nie je dostupné v zone vybranej schedulerom. CSI controller, node plugin, IAM, KMS key, topology constraints, attach limit a filesystem permissions sú samostatné gates. `Bound` PVC dokazuje binding objectu, nie úspešný attach alebo mount na konkrétnom Node.

```bash
kubectl -n payments get pvc,pv -o wide
kubectl -n payments describe pod "$STATEFUL_POD"
kubectl -n kube-system get pods -l app.kubernetes.io/name=aws-ebs-csi-driver -o wide
```

Pod events môžu rozlíšiť scheduling conflict, attach timeout, KMS authorization a mount failure. Orchestrator replacement nereparuje corrupted data. Stateful recovery potrebuje application-consistent backup, current writer authority, fencing, quorum a reconciliation podľa business invariants.

## 15. Rollout, target eligibility a drain

ECS deployment aj Kubernetes RollingUpdate vymieňajú old a new cohorts. Start-before-stop potrebuje compute, subnet IP, load-balancer a downstream headroom. Readiness alebo target health riadi prijímanie nového trafficu; deregistration delay, `preStop`, termination grace a application drain chránia in-flight work.

Queue consumer má navyše lease alebo visibility contract. Ak process dostane SIGTERM po external provider commit-e, ale pred acknowledgementom queue message, rovnaká operation môže byť redelivered. Drain preto musí kombinovať zastavenie nového worku, dokončenie alebo bezpečné odovzdanie in-flight identities a idempotentný replay.

PodDisruptionBudget obmedzuje voluntary disruptions:

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: payments-api
  namespace: payments
spec:
  minAvailable: 75%
  selector:
    matchLabels:
      app.kubernetes.io/name: payments-api
```

PDB nechráni pred všetkými node alebo zone failures a nevytvára replacement capacity. Príliš prísny PDB môže blokovať drain a upgrade. Acceptance musí preto vykonať voluntary disruption, sledovať serving capacity a overiť nulový dropped alebo duplicate payment outcome.

## 16. EKS upgrade ako viacgeneračný graph

EKS upgrade nie je jedna atomická operácia. Kubernetes control plane, nodes alebo Auto Mode compute, kubelet/runtime, managed add-ons, controllers, CRDs a workloads majú samostatné versions a compatibility boundaries. Úspešný control-plane update preto neznamená, že celý cluster používa target generation.

```text
current a target Kubernetes version
→ deprecated API inventory
→ add-on, controller a CRD compatibility
→ control-plane update
→ node/runtime generations
→ workload rollout a disruption
→ Service a business acceptance
```

Preflight číta current cluster a available add-on compatibility bez hardcodovania targetu zo starého runbooku:

```bash
CURRENT_VERSION=$(aws eks describe-cluster \
  --name payments-eks-prod \
  --region eu-central-1 \
  --query 'cluster.version' \
  --output text)

aws eks describe-cluster \
  --name payments-eks-prod \
  --region eu-central-1 \
  --query 'cluster.{Version:version,Status:status,Endpoint:endpoint,PlatformVersion:platformVersion}' \
  --output yaml

aws eks list-addons \
  --cluster-name payments-eks-prod \
  --region eu-central-1

aws eks describe-addon-versions \
  --kubernetes-version "$CURRENT_VERSION" \
  --region eu-central-1
```

Tieto príkazy preukazujú current control-plane a add-on catalog context. Upgrade plan ešte potrebuje deprecated API scan, controller vendor compatibility, node skew, disruption budget, rollback/forward-recovery boundary a canary workload. Po control-plane update sa osobitne overujú nodes, add-ons, controllers, Pods, Service path a business operations.

## 17. Autoscaling ako tri previazané control loops

Workload autoscaler mení desired replicas alebo tasks podľa demand signálu. Capacity autoscaler alebo provider realizuje hosts a placement resources. Downstream guardrails určujú, koľko pridanej concurrency bezpečne unesie database, queue, provider alebo NAT path. Jeden controller preto môže splniť svoj target a poškodiť susedný subsystem.

CPU HPA môže napríklad zvýšiť Pod count pri database latency, hoci ďalšie connections saturation zhoršia. Queue age môže lepšie reprezentovať backlog, ale maximum replicas musí rešpektovať database connection budget, provider rate limit a subnet IP headroom.

```bash
kubectl -n payments get hpa payments-api -o yaml
kubectl -n payments describe hpa payments-api

aws application-autoscaling describe-scaling-activities \
  --service-namespace ecs \
  --resource-id service/payments-prod/payments-api \
  --scalable-dimension ecs:service:DesiredCount \
  --region eu-central-1
```

HPA output ukazuje metrics, desired replicas a conditions. ECS scaling activities ukazujú scaling decisions, nie úspešnú task realization. Acceptance porovná demand signal, desired count, running/ready cohort, downstream saturation a business latency; second spike musí prejsť bez oscillation alebo retry amplification.

## 18. Worked incident: scale-out vyčerpá subnet IPs

Marketing campaign zvýšila desired count z 24 na 40. ECS service aj EKS Deployment nedosiahli target capacity, hoci CPU existujúcich workloadov bolo iba približne 45 %. ECS events uviedli `RESOURCE:ENI`; tasky zostali Pending pred image pullom. EKS scheduler časť Podov bindol, no Pod events ukázali `FailedCreatePodSandBox` a VPC CNI nevedel prideliť address. Free IPv4 count bol 2, 1 a 3 v troch subnets.

Competing hypotheses zahŕňali compute shortage, quota, image pull, task role, scheduler constraints, CNI failure a downstream throttling. ECS event a EKS sandbox event lokalizovali divergence pred application startupom; subnet read-back potom podporil spoločnú VPC address-capacity root cause. Nízke CPU preto nebolo dôkazom voľnej end-to-end capacity.

Containment zastavil unlimited workload a node scaling a zachoval healthy old cohort. Pridávanie Nodes by spotrebovalo ďalšie VPC adresy a mohlo incident zhoršiť. Recovery vytvorila novú subnet/address generation, aktualizovala ECS service/capacity provider a EKS compute/CNI IPAM model a následne spustila canary tasks a Pods v každej AZ.

Positive acceptance vyžadovala 40 workloadov s approved image/configuration, balanced three-AZ placement, správnu task role alebo Pod Identity, target eligibility a úspešnú payment. Recovery test zopakoval scale-out aj AZ-loss scenario s meraným IP headroomom. Forbidden test potvrdil nulový dropped alebo duplicate payment počas drainu a second scale operation nevytvorila nový exhaustion incident.

## 19. ECS verzus EKS ako ownership rozhodnutie

ECS je vhodný, keď AWS-native task/service API, jeho deployment a capacity model a menší orchestration surface spĺňajú workload requirements. EKS je vhodný, keď Kubernetes API, operators, controllers, ecosystem alebo organizačná portability boundary predstavujú skutočnú hodnotu a tím dokáže vlastniť day-2 Kubernetes lifecycle.

Rozhodnutie sa nemá robiť podľa popularity ani podľa samotnej portability container image-u. Porovnáva sa desired-state model, identity, network a storage ownership, upgrade graph, operational skills, incident evidence, multi-tenancy, policy ecosystem a total cost. Image môže byť prenosný, zatiaľ čo IAM, Service implementation, load balancer, persistent storage a recovery contract zostanú provider-specific.

Najlepší výber je ten, pri ktorom tím vie presne vysvetliť controller boundaries, diagnostikovať first divergence a vykonať bezpečný second operation. Abstrakcia, ktorú tím nevie prevádzkovať, neznižuje complexity; iba ju presúva do incidentu.

## Kontrolné otázky

1. Čo je authoritative desired state v ECS a EKS?
2. Prečo `RUNNING`, `Ready` ani `Available` nie sú serving acceptance?
3. Aký je rozdiel medzi ECS execution role a task role?
4. Ako sa Pod Identity líši od EKS access entry?
5. Ktoré observations rozlišujú scheduler, kubelet a CNI failure?
6. Prečo môže pridanie Nodes zhoršiť IP exhaustion?
7. Čo EndpointSlice dokazuje a čo nedokazuje?
8. Ako spolu súvisia readiness, deregistration, `preStop` a termination grace?
9. Prečo control-plane update nie je celý EKS upgrade?
10. Ktoré positive, recovery a forbidden testy uzatvárajú IP-capacity incident?

## Oficiálna dokumentácia

- [Amazon ECS Developer Guide](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html)
- [ECS task definitions](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definitions.html)
- [IAM roles for Amazon ECS](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-iam-role-overview.html)
- [ECS services](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs_services.html)
- [ECS capacity providers](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/cluster-capacity-providers.html)
- [Amazon EKS User Guide](https://docs.aws.amazon.com/eks/latest/userguide/what-is-eks.html)
- [EKS access entries](https://docs.aws.amazon.com/eks/latest/userguide/access-entries.html)
- [EKS Pod Identity](https://docs.aws.amazon.com/eks/latest/userguide/pod-identities.html)
- [Amazon VPC CNI](https://docs.aws.amazon.com/eks/latest/userguide/managing-vpc-cni.html)
- [EKS IP address utilization best practices](https://docs.aws.amazon.com/eks/latest/best-practices/ip-opt.html)
- [EKS cluster updates](https://docs.aws.amazon.com/eks/latest/userguide/update-cluster.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Lambda](lambda.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: CloudWatch a CloudTrail →](cloudwatch-cloudtrail.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
