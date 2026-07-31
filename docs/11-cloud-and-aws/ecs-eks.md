# Amazon ECS a Amazon EKS

Amazon ECS a Amazon EKS realizujú desired container workload na compute, network, storage a identity resources. ECS používa AWS-native task/service control plane. EKS poskytuje managed Kubernetes control plane a zachováva Kubernetes API, controllers a ecosystem. Rozdiel nie je „jednoduché verzus pokročilé“. Mení sa authoritative desired state, scheduler evidence, capacity ownership, workload identity a upgrade surface.

```text
business release intent
→ immutable image and workload specification
→ orchestrator desired-state generation
→ scheduler placement
→ compute, network and storage realization
→ workload identity and configuration
→ process startup and readiness
→ service or target eligibility
→ traffic and business outcome
→ scaling, rollout, drain and retirement
```

`RUNNING`, `Ready` alebo `Available` sú medzistavy. Closure potrebuje client a business dôkaz.

## 1. Exact container subject

Atlas Payments release `7.17.0` používa image digest `sha256:pay-api-7-17-0`, configuration `CFG-PAY-52`, secret `SEC-PAY-39`, database proxy `PROXY-10` a load balancer `ALB-PAY-18`.

ECS realization je cluster `payments-prod`, service `payments-api`, task definition `payments-api:118`, deployment `ECS-DEP-73`, capacity provider `payments-managed-instances-v4`, `awsvpc` network mode, task role `ROLE-ECS-PAY-21`, execution role `ROLE-ECS-EXEC-14` a desired count 40.

EKS realization je cluster `payments-eks-prod`, namespace `payments`, Deployment `payments-api`, ReplicaSet `RS-PAY-219`, Service `SVC-PAY-31`, ServiceAccount `payments-api`, Pod Identity association `PODID-PAY-9`, compute generation `NODEPOOL-PAY-17` a VPC CNI `CNI-31`.

Accepted outcome je 40 eligible workloads across three AZs, least-privilege workload identity and successful payment `P-901`. Host role leakage, IP exhaustion, target-readiness mismatch a duplicate payment pri drain sú forbidden.

## 2. ECS authority graph

```text
task-definition revision
→ ECS service desired state
→ deployment
→ scheduler and capacity provider
→ task placement
→ ENI, volumes, logs and roles
→ container startup
→ target registration and health
```

Task definition je immutable runtime template. ECS service udržiava desired count a deployment cohorts. Service events and stopped reasons sú authoritative evidence pre failures pred application logs.

## 3. ECS task definition v Terraform-e

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

      portMappings = [
        {
          name          = "http"
          containerPort = 8080
          protocol      = "tcp"
        }
      ]

      environment = [
        { name = "CONFIG_GENERATION", value = "CFG-PAY-52" }
      ]

      secrets = [
        {
          name      = "DATABASE_URL"
          valueFrom = aws_secretsmanager_secret.database.arn
        }
      ]

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

Image je viazaný digestom. Execution role používa platforma na image pull/log/secret injection podľa feature contractu. Task role používa application SDK. Zámena týchto identít vedie buď k startup failure, alebo k príliš širokej application authority.

## 4. ECS service a load balancer

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

Deployment limits potrebujú subnet IP and capacity headroom. Circuit breaker môže rollbacknúť deployment cohort, no nevráti database schema alebo external provider side effect.

## 5. ECS live diagnosis

```bash
aws ecs describe-services \
  --cluster payments-prod \
  --services payments-api \
  --region eu-central-1 \
  --query 'services[0].{Desired:desiredCount,Running:runningCount,Pending:pendingCount,TaskDefinition:taskDefinition,Deployments:deployments,Events:events[0:10]}'
```

Tasks:

```bash
TASK_ARNS=$(aws ecs list-tasks \
  --cluster payments-prod \
  --service-name payments-api \
  --region eu-central-1 \
  --query 'taskArns' --output text)

aws ecs describe-tasks \
  --cluster payments-prod \
  --tasks $TASK_ARNS \
  --region eu-central-1 \
  --query 'tasks[].{Task:taskArn,State:lastStatus,Health:healthStatus,TaskDefinition:taskDefinitionArn,Az:availabilityZone,StoppedReason:stoppedReason,Containers:containers[].{Name:name,State:lastStatus,Exit:exitCode,Reason:reason,ImageDigest:imageDigest}}'
```

`runningCount=40` nepreukazuje target health ani payment success. Image digest read-back spája runtime s approved artifact.

## 6. ECS capacity providers

Capacity provider spája scheduler s Fargate, Fargate Spot, ECS Managed Instances alebo EC2 Auto Scaling capacity podľa modelu. Service desired count and host capacity sú odlišné control loops.

Fargate odstráni node fleet, ale workload stále vlastní sizing, ENI/IP capacity, roles, storage, deployment and cost. ECS Managed Instances preberajú viac EC2 provisioning/patching lifecycle-u. ASG capacity provider necháva tímu AMI, agent, OS patching a drain.

Capacity failure sa môže prejaviť ako task `PENDING` bez application logu. Service events treba čítať pred container diagnosis.

## 7. EKS authority graph

```text
Kubernetes manifest
→ API authentication and RBAC/admission
→ persisted object
→ controller reconciliation
→ scheduler Pod binding
→ kubelet and runtime
→ CNI/CSI realization
→ Service/Ingress/target eligibility
→ application outcome
```

EKS spravuje Kubernetes control plane. Zákazník vlastní workloads, namespaces, access/RBAC, admission, add-ons, compute selection, networking policy, storage topology, upgrades and business recovery.

## 8. Kubernetes Deployment a Service

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

Topology constraint vyžaduje balanced placement a môže nechať Pods Pending, ak capacity v jednej zone chýba. To je správnejšie než tichý single-AZ collapse, ak availability contract vyžaduje tri zones.

## 9. EKS access a Pod Identity

Human/automation access do Kubernetes API a workload AWS identity sú odlišné.

EKS access entry môže mapovať IAM principal do cluster access policy/RBAC path. Pod Identity association viaže IAM role na namespace and ServiceAccount.

```bash
aws eks create-pod-identity-association \
  --cluster-name payments-eks-prod \
  --namespace payments \
  --service-account payments-api \
  --role-arn arn:aws:iam::100000000042:role/payments-pod-runtime \
  --region eu-central-1
```

Read-back:

```bash
aws eks list-pod-identity-associations \
  --cluster-name payments-eks-prod \
  --namespace payments \
  --service-account payments-api \
  --region eu-central-1
```

Inside Pod:

```bash
kubectl -n payments exec deploy/payments-api -- aws sts get-caller-identity
```

ServiceAccount name alebo association existence nepreukazuje actual SDK credential. Live caller musí byť workload role, nie node role.

## 10. Scheduler, runtime a readiness diagnosis

Deployment/controller state:

```bash
kubectl -n payments get deploy payments-api -o wide
kubectl -n payments rollout status deploy/payments-api --timeout=5m
kubectl -n payments get rs -l app.kubernetes.io/name=payments-api
```

Pod placement and failure:

```bash
kubectl -n payments get pods \
  -l app.kubernetes.io/name=payments-api \
  -o custom-columns='NAME:.metadata.name,PHASE:.status.phase,NODE:.spec.nodeName,POD-IP:.status.podIP,IMAGE:.spec.containers[0].image,READY:.status.containerStatuses[0].ready'

kubectl -n payments describe pod "$POD"
kubectl -n payments get events --sort-by=.lastTimestamp | tail -50
```

Pod `Pending` pred binding smeruje na scheduler resources, taints, affinity/topology or PVC. Pod bound na Node, ale not Running, smeruje na image pull, CNI, CSI or runtime. `Ready` nepreukazuje Service selector, EndpointSlice, load balancer or business journey.

## 11. EndpointSlice a Service path

```bash
kubectl -n payments get svc payments-api -o yaml
kubectl -n payments get endpointslice \
  -l kubernetes.io/service-name=payments-api \
  -o wide
```

Service selector musí matchovať Pod labels a EndpointSlice musí obsahovať ready addresses. Direct PodIP test izoluje application from Service dataplane:

```bash
kubectl -n payments run curl-test --rm -it --restart=Never \
  --image=curlimages/curl:8.10.1 -- \
  curl -fsS http://payments-api/readyz
```

## 12. VPC CNI a IP capacity

Pri VPC CNI Pods spotrebúvajú VPC addresses podľa node/ENI/prefix configuration. Flow:

```text
Pod scheduled
→ CNI allocates address
→ network namespace and routes
→ Security Group/NetworkPolicy
→ DNS and Service path
```

Subnet free IPs, node ENI limits, prefix delegation and warm IP targets determine real Pod capacity. More Nodes can worsen shortage because Nodes themselves consume addresses.

CNI state:

```bash
kubectl -n kube-system get ds aws-node -o wide
kubectl -n kube-system logs ds/aws-node -c aws-node --tail=200
aws ec2 describe-subnets \
  --subnet-ids subnet-0paya subnet-0payb subnet-0payc \
  --region eu-central-1 \
  --query 'Subnets[].{Subnet:SubnetId,Az:AvailabilityZoneId,Free:AvailableIpAddressCount}'
```

## 13. NetworkPolicy and SG layers

Kubernetes NetworkPolicy má effect iba ak dataplane implementation ju enforce-uje. Security Groups observe ENI/AWS network identity. Policies môžu byť súčasne necessary a neither one alone represents complete path.

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

Positive and forbidden connectivity tests are required; manifest presence alone does not prove enforcement.

## 14. Storage and topology

PVC may be bound to a zonal volume incompatible with scheduler placement. CSI controller/node components, IAM, KMS, topology and mount permissions are separate gates. Stateful workload drain needs quorum, fencing and application-consistent backup.

```bash
kubectl -n payments get pvc,pv -o wide
kubectl -n payments describe pod "$STATEFUL_POD"
```

Orchestrator replacement does not recover corrupted state.

## 15. Rollout and drain

ECS deployment or Kubernetes RollingUpdate exchanges old/new cohorts. Start-before-stop needs capacity. Target/readiness controls new traffic, while task protection, deregistration delay, `preStop` and termination grace protect in-flight work.

For queue consumer, process termination must coordinate message visibility/lease. A SIGTERM after provider commit but before source acknowledgement can cause duplicate delivery.

Kubernetes PodDisruptionBudget:

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

PDB protects voluntary disruptions, not all failures, and needs replacement capacity. Too strict PDB can block node drain.

## 16. EKS upgrade graph

Control plane, nodes, Fargate/Auto Mode infrastructure, add-ons, controllers, CRDs and workloads are not one atomic upgrade.

```text
current/target Kubernetes version
→ deprecated API inventory
→ add-on and controller compatibility
→ control-plane update
→ node/runtime generations
→ workload rollout and disruption
→ application acceptance
```

Preflight:

```bash
aws eks describe-cluster \
  --name payments-eks-prod \
  --region eu-central-1 \
  --query 'cluster.{Version:version,Status:status,Endpoint:endpoint,PlatformVersion:platformVersion}'

aws eks list-addons --cluster-name payments-eks-prod --region eu-central-1
aws eks describe-addon-versions --kubernetes-version 1.35 --region eu-central-1
```

Control-plane update success does not update nodes or application.

## 17. Autoscaling has three control loops

Workload autoscaler changes desired replicas/tasks. Capacity autoscaler realizes nodes/hosts. Downstream guardrails determine whether added concurrency is safe.

CPU HPA can worsen DB saturation. Queue age may be better demand signal, but maximum replicas still respect DB/provider budget.

```bash
kubectl -n payments get hpa
kubectl -n payments describe hpa payments-api
```

## 18. Worked incident: scale-out vyčerpá subnet IPs

Marketing campaign increased desired count from 24 to 40. ECS service and EKS Deployment both failed to reach capacity. Existing CPU was only 45 %.

ECS events reported `RESOURCE:ENI`; tasks stayed Pending before image pull. EKS scheduler bound some Pods, but Pod Events showed `FailedCreatePodSandBox` and VPC CNI could not allocate address. Free IPv4 was 2, 1 and 3 across three subnets.

Root cause was shared VPC address capacity, not CPU. Adding Nodes would consume more IPs and worsen failure.

Containment stopped unlimited workload/node scaling and preserved healthy old cohort. Recovery created new subnet/address generation, updated ECS service/capacity provider and EKS NodePool/CNI IPAM model, then launched canary tasks/Pods in each AZ.

Acceptance required 40 approved image/config workloads, balanced three-AZ placement, rollout/AZ-loss IP headroom, correct task role or Pod Identity, target eligibility and no dropped/duplicate payment during drain.

## 19. ECS vs EKS decision

Choose ECS when AWS-native task/service API and smaller orchestrator surface meet requirements. Choose EKS when Kubernetes API, operators/controllers, ecosystem or portability boundary is a real requirement and team can own day-2 Kubernetes.

Decision compares total operational ownership, upgrades, identity, networking, storage, reliability and TCO. Container image portability alone does not make network/IAM/storage portable.

## Kontrolné otázky

1. What is the authoritative desired state in ECS and EKS?
2. Why is `RUNNING` or `Ready` not serving acceptance?
3. What is the difference between ECS execution and task role?
4. How does Pod Identity differ from EKS access entry?
5. Which observations distinguish scheduler from CNI failure?
6. Why can adding Nodes worsen IP exhaustion?
7. What does EndpointSlice prove?
8. How do readiness, deregistration, preStop and grace interact?
9. Why is control-plane update not a cluster upgrade?
10. Which test closes the IP-capacity recovery?

## Oficiálna dokumentácia

- [Amazon ECS Developer Guide](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html)
- [ECS task definitions](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definitions.html)
- [ECS services](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs_services.html)
- [ECS capacity providers](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/cluster-capacity-providers.html)
- [Amazon EKS User Guide](https://docs.aws.amazon.com/eks/latest/userguide/what-is-eks.html)
- [EKS Pod Identity](https://docs.aws.amazon.com/eks/latest/userguide/pod-identities.html)
- [Amazon VPC CNI](https://docs.aws.amazon.com/eks/latest/userguide/managing-vpc-cni.html)
- [EKS cluster updates](https://docs.aws.amazon.com/eks/latest/userguide/update-cluster.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Lambda](lambda.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: CloudWatch a CloudTrail →](cloudwatch-cloudtrail.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
