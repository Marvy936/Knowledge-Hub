# Elastic Load Balancing

Elastic Load Balancing vytvára managed traffic-distribution boundary medzi clients a meniacou sa množinou backend targets. Load balancer nie je jedna stabilná IP pred servermi a target group nie je iba zoznam instances. Reálny request outcome vznikne až vtedy, keď DNS dovedie clienta k správnemu load-balancer dataplane-u, listener prijme connection, TLS a ordered rules vytvoria routing verdict, target group zostaví eligible cohort, backend connection prejde network controls a application vráti správny business response.

```text
client request
→ DNS and load-balancer node
→ listener and TLS
→ ordered rule match
→ target-group generation
→ registered, enabled and healthy target set
→ target selection
→ independent backend connection
→ application response
→ load-balancer response and logs
→ business outcome
```

Target `healthy` dokazuje iba konkrétny health-check contract. Nedokazuje, že správny listener rule vybral správnu release cohortu alebo že payment transaction skončila presne raz.

## 1. Exact traffic-distribution subject

Atlas Payments používa load-balancing subject `LB-PAY-42`. Public hostname je `pay.example.com`, load balancer `alb-pay-public-17` v `eu-central-1` a enabled ingress subnets pokrývajú tri AZs. Load-balancer SG generation je `SG-LB-18`.

HTTPS listener generation `LIS-24` používa certificate `CERT-11` a TLS policy `TLS-8`. Priority 10 matchuje `Host=pay.example.com` a path `/api/payments/*` a forwarduje 90 % na `tg-pay-v714`, 10 % na `tg-pay-v715`. Priority 20 matchuje `/api/*` a smeruje na stable group. Default action vracia fixed `404`.

Target groups používajú HTTPS port `8443`. Readiness path je `/readyz`, success matcher `200`, unhealthy threshold 2, healthy threshold 3, deregistration delay 120 sekúnd a slow start 60 sekúnd. Business request je `P-884` a accepted outcome je jedna autorizácia a jeden durable ledger result.

Incident evidence musí zachovať `Host`, path, method, client/request ID, listener/rule generation, target-group ARN, target ID/AZ, response headers, release generation a business transaction ID.

## 2. Výber ELB typu mení routing a observation model

Application Load Balancer ukončuje HTTP/HTTPS connection a vytvára novú backend connection. Vie routovať podľa hosta, pathu, methodu, headers, query alebo source IP. Je vhodný, keď verdict závisí od Layer 7 request representation.

Network Load Balancer pracuje s TCP, TLS, UDP a ďalšími podporovanými transport flows. Je vhodný pre non-HTTP protocols, statické zonálne IP identities, PrivateLink a high-throughput connection workloads. Pri NLB treba presne poznať client-IP preservation a target type.

Gateway Load Balancer transparentne vkladá appliance fleet cez GENEVE a route steering. Je vhodný pre firewall/inspection, nie pre HTTP path routing.

Classic Load Balancer je staršia generation. Migrácia na ALB/NLB mení source identity, health, TLS, stickiness, logging a target semantics; nie je to rename.

## 3. Regional service a zonálny dataplane

ELB je regional service, ale data plane sa realizuje v enabled subnets/AZs. Multi-AZ load balancer nepreukazuje Multi-AZ application, ak targets alebo database zostávajú zonálne.

```text
regional ELB configuration
→ enabled subnets and AZs
→ zonal nodes and addresses
→ target registration per AZ
→ cross-zone or zonal selection
→ target and dependency capacity
```

Ingress subnet potrebuje IP headroom pre managed scale a maintenance. IP-exhausted subnet môže obmedziť load-balancer capacity aj pri healthy targets.

## 4. Praktický ALB základ v Terraform-e

```hcl
resource "aws_lb" "payments" {
  name               = "alb-pay-public-17"
  load_balancer_type = "application"
  internal           = false
  security_groups    = [aws_security_group.alb.id]
  subnets = [
    aws_subnet.public_a.id,
    aws_subnet.public_b.id,
    aws_subnet.public_c.id,
  ]

  enable_deletion_protection = true

  access_logs {
    bucket  = aws_s3_bucket.alb_logs.id
    prefix  = "payments"
    enabled = true
  }

  tags = {
    Generation = "ALB-PAY-17"
  }
}

resource "aws_lb_target_group" "v714" {
  name        = "tg-pay-v714"
  port        = 8443
  protocol    = "HTTPS"
  target_type = "instance"
  vpc_id      = aws_vpc.payments.id

  health_check {
    enabled             = true
    protocol            = "HTTPS"
    path                = "/readyz"
    matcher             = "200"
    healthy_threshold   = 3
    unhealthy_threshold = 2
    interval            = 10
    timeout             = 5
  }

  slow_start = 60

  deregistration_delay = 120

  tags = {
    Release = "7.14.0"
  }
}
```

Terraform vytvorí desired ALB a target-group configuration. NePreukazuje, že certificate je validný, listener rules majú správnu precedence alebo targets prijímajú payment request. Tieto boundaries potrebujú live read-back a request test.

## 5. HTTPS listener a ordered rules

```hcl
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.payments.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = aws_acm_certificate.payments.arn

  default_action {
    type = "fixed-response"

    fixed_response {
      content_type = "application/json"
      message_body = "{\"error\":\"not_found\"}"
      status_code  = "404"
    }
  }
}

resource "aws_lb_listener_rule" "payments_canary" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 10

  action {
    type = "forward"

    forward {
      target_group {
        arn    = aws_lb_target_group.v714.arn
        weight = 90
      }

      target_group {
        arn    = aws_lb_target_group.v715.arn
        weight = 10
      }
    }
  }

  condition {
    host_header {
      values = ["pay.example.com"]
    }
  }

  condition {
    path_pattern {
      values = ["/api/payments/*"]
    }
  }
}
```

Listener rule priority je program order. Broad `/api/*` s nižším číslom by shadowoval presnejšiu payment rule. Weighted forward nie je presný request percentage pre malú sample; stickiness, retries a long-lived connections môžu observed distribution skresliť.

## 6. Live ALB a listener read-back

```bash
aws elbv2 describe-load-balancers \
  --names alb-pay-public-17 \
  --region eu-central-1 \
  --query 'LoadBalancers[0].{Arn:LoadBalancerArn,DNS:DNSName,Scheme:Scheme,State:State.Code,Type:Type,Subnets:AvailabilityZones[].{Zone:ZoneName,Subnet:SubnetId}}'
```

Listener inventory:

```bash
aws elbv2 describe-listeners \
  --load-balancer-arn "$LOAD_BALANCER_ARN" \
  --region eu-central-1 \
  --query 'Listeners[].{Arn:ListenerArn,Port:Port,Protocol:Protocol,SslPolicy:SslPolicy,Certificates:Certificates}'
```

Ordered rules:

```bash
aws elbv2 describe-rules \
  --listener-arn "$LISTENER_ARN" \
  --region eu-central-1 \
  --query 'Rules[].{Priority:Priority,Conditions:Conditions,Actions:Actions}'
```

Tieto commands preukazujú control-plane configuration. Nehovoria, ktorú rule použil konkrétny request. Na to treba request identity a logs/response cohort header.

## 7. DNS a viewer TLS

Application hostname typicky používa Route 53 alias na ELB DNS name. Resolved IPs sa môžu meniť a nesmú byť hard-coded.

```bash
dig pay.example.com A +short

openssl s_client \
  -connect pay.example.com:443 \
  -servername pay.example.com \
  -verify_return_error \
  -brief </dev/null
```

DNS result je sample resolver cohorty. TLS success preukazuje viewer certificate a policy pre daný client. NePreukazuje backend TLS alebo target health.

Certificate read-back:

```bash
aws acm describe-certificate \
  --certificate-arn "$CERTIFICATE_ARN" \
  --region eu-central-1 \
  --query 'Certificate.{Status:Status,Domain:DomainName,SANs:SubjectAlternativeNames,NotAfter:NotAfter,InUseBy:InUseBy}'
```

## 8. Target group ako eligibility boundary

Target group spája protocol, port, target type, health, deregistration, slow start a selection attributes. Rovnaká instance môže byť healthy v jednej target group a unhealthy v druhej.

Targets:

```bash
aws elbv2 describe-target-health \
  --target-group-arn "$TARGET_GROUP_ARN" \
  --region eu-central-1 \
  --query 'TargetHealthDescriptions[].{Target:Target.Id,Port:Target.Port,Az:Target.AvailabilityZone,State:TargetHealth.State,Reason:TargetHealth.Reason,Description:TargetHealth.Description}' \
  --output table
```

`healthy` znamená, že configured health check prešiel podľa thresholds. Matcher `200` nevaliduje response body, tenant alebo payment workflow.

## 9. Health oracle

Readiness endpoint má odpovedať, či target môže bezpečne prijať nový request. Príliš plytký check môže vrátiť 200 bez configuration alebo credentialu. Príliš hlboký check závislý od shared database môže pri jej incidente vyradiť celý fleet a spustiť replacement storm.

Rozlišuj:

```text
liveness: process nie je nenávratne zaseknutý
readiness: target môže prijať new traffic
business canary: konkrétna transaction je správna
```

ALB health check je readiness oracle, nie business canary.

## 10. Backend network a TLS

Viewer a backend sú dve connections. ALB SG potrebuje outbound k target portu a target SG inbound z ALB SG. Target subnet NACL musí povoliť backend connection a return path. Pri HTTPS target group-e application certificate/trust behavior má samostatný contract.

Direct target test z controlled VPC source:

```bash
curl --fail --show-error \
  --resolve payments.internal:8443:10.42.16.27 \
  https://payments.internal:8443/readyz
```

Direct test obchádza ALB listener/rule. Je užitočný na izoláciu backend, nie na user-path acceptance.

## 11. Weighted canary s cohort evidence

Každá response má niesť bezpečný release header, napríklad `X-Atlas-Release: 7.15.0`, a logs musia viazať request ID na target/release.

```bash
for i in $(seq 1 50); do
  curl -fsS -D - \
    -o /dev/null \
    -H 'Host: pay.example.com' \
    "https://pay.example.com/api/payments/canary-$i" \
    | awk -F': ' 'tolower($1)=="x-atlas-release" {print $2}'
done | sort | uniq -c
```

Tento experiment ukáže observed distribution pre fresh requests. Nejde o štatistickú garanciu 90/10 a nesmie vykonať real payment side effect. Canary endpoint musí byť bezpečný a non-mutating alebo používať test tenant.

## 12. Slow start, stickiness a routing algorithm

Slow start postupne pridáva traffic newly healthy targetu. Pomáha pri cache, JIT a pool warmup. Target musí byť funkčne ready ešte pred slow startom; slow start nezakryje chybný artifact.

Stickiness viaže clienta k targetu alebo target group-e podľa configured mechanismu. Môže skresliť canary a vytvoriť nerovnomerné load distribution. Stateful session iba v process memory zhoršuje replacement a failover.

Selection algorithm môže byť round-robin, least outstanding requests alebo supported weighted-random/anomaly behavior podľa target-group capabilities. Algorithm neodstráni rozdielnu target capacity.

## 13. Draining a deregistration delay

Pri deployment alebo scale-in-e target prejde do `draining`; load balancer prestane posielať nové requests a čaká na existing connections podľa deregistration delay.

```bash
aws elbv2 deregister-targets \
  --target-group-arn "$TARGET_GROUP_ARN" \
  --targets Id=i-0123456789abcdef0,Port=8443 \
  --region eu-central-1
```

Command accepted nepreukazuje complete drain. Sleduj target state:

```bash
aws elbv2 describe-target-health \
  --target-group-arn "$TARGET_GROUP_ARN" \
  --targets Id=i-0123456789abcdef0,Port=8443 \
  --region eu-central-1
```

Application termination grace musí byť dlhšia než request drain a background-work handoff. Force termination pred drain môže prerušiť transaction alebo vyvolať client retry s unknown outcome.

## 14. Fail-open a zonal behavior

Ak všetky registered targets v target group-e zlyhajú health, ELB service môže podľa konkrétneho typu a state-u fail-open a posielať traffic na unhealthy targets. To je availability mechanism, nie correctness guarantee.

Alarmy preto sledujú healthy host count, target errors, load-balancer errors a business SLI. `All targets unhealthy` nesmie byť interpretované ako bezpečný circuit breaker.

Zonal failure test musí preukázať, že remaining target capacity, database a downstream zvládnu load. DNS a existing connections môžu predlžovať cohort transition.

## 15. Access logs a request correlation

ALB access log obsahuje timestamps, client/target tuple, request, ELB/target status, processing times, chosen target a trace fields podľa format-u. Log delivery do S3 je asynchronous a potrebuje bucket policy, encryption, retention a parser version.

Praktický request:

```bash
REQUEST_ID="canary-$(date +%s)"

curl --fail --show-error \
  -H "X-Request-ID: $REQUEST_ID" \
  -H 'Host: pay.example.com' \
  https://pay.example.com/api/payments/health
```

Application a proxy logs musia zachovať correlation ID. ALB access log nevie sám potvrdiť ledger result.

CloudWatch metrics ako `RequestCount`, `HTTPCode_ELB_5XX_Count`, `HTTPCode_Target_5XX_Count`, `TargetResponseTime`, `HealthyHostCount` a `RejectedConnectionCount` sa interpretujú podľa load balancer/target group/AZ dimensions. `ELB 5XX` a `target 5XX` majú odlišné boundaries.

## 16. Worked incident: broad rule shadowuje canary

Atlas zamýšľal poslať 10 % payment API requests na release 7.15.0. Obe target groups boli healthy a Terraform plan obsahoval expected weights. Business telemetry však ukazovala nula requests na new release.

Hypotézy zahŕňali stickiness, small sample, target unhealthy, wrong alias/DNS, weighted-forward config, response header missing a rule precedence.

`describe-rules` ukázalo, že priority 5 rule `Path=/api/* → tg-pay-v714` bola pridaná pri inom release. Canary payment rule mala priority 10. ALB používa prvú matching rule, takže broad priority 5 shadowovala payment rule. Target groups aj weights boli správne, ale nedosiahnuteľné pre relevantný request.

Containment nemenilo target health ani ASG. Tím zachoval listener rules, CloudTrail, access logs a response cohort evidence. Recovery presunula broad rule za payment-specific rule, nasadila zmenu cez canary a testovala exact `Host`, path a method.

Acceptance vyžadovala observed requests v oboch release cohorts, stable business SLI, request-to-release correlation a forbidden test, pri ktorom unknown host/path skončil default 404. Druhý deployment rule-order test zabránil návratu shadowing-u.

## 17. Worked incident: target healthy, payment path zlyháva

Iný failure mode vznikne, keď `/readyz` vracia 200, no target načítal stale credential. ALB správne považuje target za healthy, ale payment request dostane provider `401`.

Root cause nie je ELB. Readiness oracle je príliš plytký alebo application credential-refresh contract zlyhal. Recovery musí opraviť runtime identity a business canary, nie zmeniť listener alebo health matcher na broad status range.

## 18. Troubleshooting podľa prvej divergentnej boundary

Ak DNS zlyhá, rieš Route 53/resolver. Ak TCP/TLS k listeneru zlyhá, rieš LB state, SG/NACL, certificate a policy. Ak listener vracia fixed/redirect response, analyzuj rule. Ak ELB vracia 502/503, analyzuj target eligibility, backend connection a capacity. Ak target vracia 5xx, pokračuj application a dependency. Ak HTTP success nesie wrong business data, analyzuj authorization, caching a transaction path.

```bash
curl -vk \
  -H 'Host: pay.example.com' \
  https://pay.example.com/api/payments/health
```

`-v` je diagnostický output a môže odhaliť citlivé headers; v production evidence sa používa opatrne a tokeny sa redigujú.

## Kontrolné otázky

1. Aký rozdiel je medzi viewer a backend connection?
2. Prečo target `healthy` nie je business acceptance?
3. Ako ordered listener rules vytvárajú routing program?
4. Prečo weighted forwarding nie je presné percento pre malú sample?
5. Ktorý response/log evidence viaže request na release cohort?
6. Čo slow start rieši a čo nevyrieši?
7. Ako deregistration delay súvisí s process termination?
8. Čo znamená ELB fail-open risk?
9. Ako odlíšiš ELB 5xx od target 5xx?
10. Ktorý positive a forbidden test uzatvorí rule-precedence recovery?

## Oficiálna dokumentácia

- [Elastic Load Balancing](https://docs.aws.amazon.com/elasticloadbalancing/latest/userguide/what-is-load-balancing.html)
- [Application Load Balancers](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html)
- [Listeners and rules](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-listeners.html)
- [Target groups](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-target-groups.html)
- [Health checks](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/target-group-health-checks.html)
- [Access logs](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-access-logs.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: EC2 a Auto Scaling](ec2-auto-scaling.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: S3, EBS a EFS →](s3-ebs-efs.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
