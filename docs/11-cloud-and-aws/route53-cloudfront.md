# Route 53 a CloudFront

Amazon Route 53 rozhoduje, akú DNS odpoveď dostane resolver pre konkrétne meno, typ, routing policy a health state. Amazon CloudFront následne ukončí viewer connection na edge dataplane-e, vyberie ordered cache behavior, zostaví cache key a pri cache miss-e vytvorí origin request. DNS steering a CDN caching sú preto dva odlišné decision systems.

```text
DNS query
→ Route 53 authoritative verdict
→ resolver/client cache
→ CloudFront viewer endpoint
→ viewer TLS and normalized request
→ first matching cache behavior
→ cache-key identity
→ hit or origin request
→ origin authorization and response
→ viewer response and business outcome
```

TTL, cache key, minimum TTL, origin request policy a error caching priamo ovplyvňujú correctness, privacy a recovery. CloudFront nie je iba performance layer.

## 1. Exact edge subject

Atlas Payments používa hosted zone `HZ-EXAMPLE-17` pre `example.com` a record `pay.example.com A/AAAA alias`, generation `DNS-REC-31`. CloudFront distribution je `D-PAY-17`, configuration `CF-44`, alternate domain `pay.example.com`, viewer certificate `CERT-CF-12` a TLS policy `TLS-CF-8`.

Ordered behaviors sú:

```text
/assets/*
→ private S3 origin
→ OAC generation OAC-7
→ immutable asset cache policy

/api/payments/*
→ ALB origin
→ caching disabled
→ auth/tenant headers forwarded

default
→ portal origin
```

Sample request je `GET /api/payments/P-884` s bearer identity a `X-Tenant-ID=tenant-a`. Forbidden outcome je, aby tenant-b dostal cached response tenant-a alebo aby private S3 origin bol otvorený public ako oprava 403.

## 2. DNS authority chain

Public DNS resolution prechádza stub resolverom, recursive cache, root/TLD delegation a authoritative Route 53 name servers.

```text
client query
→ recursive cache
→ root and TLD delegation
→ Route 53 hosted zone
→ record/routing/health decision
→ response cached by TTL
```

Hosted zone nie je domain registration ani parent delegation. Nová zone môže obsahovať správne records a byť nepoužitá, ak registrar stále deleguje na old name servers.

Praktická diagnostika:

```bash
dig +trace pay.example.com A

dig pay.example.com A +noall +answer +authority

dig @ns-123.awsdns-45.net pay.example.com A +noall +answer +authority
```

`+trace` ukáže delegation chain. Direct authoritative query obchádza recursive cache. Ani jeden test nepreukazuje CloudFront TLS alebo origin behavior.

## 3. Route 53 alias na CloudFront

Terraform:

```hcl
resource "aws_route53_record" "payments_ipv4" {
  zone_id = aws_route53_zone.example.zone_id
  name    = "pay.example.com"
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.payments.domain_name
    zone_id                = aws_cloudfront_distribution.payments.hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "payments_ipv6" {
  zone_id = aws_route53_zone.example.zone_id
  name    = "pay.example.com"
  type    = "AAAA"

  alias {
    name                   = aws_cloudfront_distribution.payments.domain_name
    zone_id                = aws_cloudfront_distribution.payments.hosted_zone_id
    evaluate_target_health = false
  }
}
```

CloudFront alias targets nepodporujú `EvaluateTargetHealth=true`. Multi-distribution failover potrebuje explicitný supported health-check/routing design. Alias umožňuje zone apex a AWS resource integration; nie je general CNAME syntax.

Live read-back:

```bash
aws route53 list-resource-record-sets \
  --hosted-zone-id ZEXAMPLE17 \
  --query 'ResourceRecordSets[?Name==`pay.example.com.`]'
```

Record update je control-plane state. Resolver/client cache a existing connections môžu stále používať old destination.

## 4. TTL a cutover

Nízky TTL znižuje maximum intended caching pre nové answers, ale nezruší existing TCP/TLS sessions a nepomôže resolveru, ktorý už cache-uje old answer s pôvodným vysokým TTL.

Safe DNS migration:

```text
lower TTL before old TTL window
→ wait for old caches to expire
→ update record
→ compare authoritative and recursive answers
→ observe actual traffic on old/new endpoints
→ retire old endpoint after connection drain
→ raise TTL
```

Negative answers majú vlastný cache lifecycle. Po oprave missing recordu môže časť clients stále dostávať cached `NXDOMAIN`.

## 5. Routing policies

Weighted routing distribuuje DNS answers podľa relative weights, nie presné requests. Jeden large recursive resolver môže cacheovať answer pre tisíce clients. Latency routing používa AWS latency measurements, nie current application p99. Failover routing používa health state, ale RTO zahŕňa detection, authoritative answer, TTL, reconnect a secondary readiness.

Geolocation/geoproximity/IP-based policies vyberajú answer podľa source cohort modelu a potrebujú default path. Nie sú security boundary. Multivalue answer vracia viac healthy records, ale nie je connection-aware load balancer.

Health check musí používať direct endpoint identity. Check na rovnaký failover hostname môže po DNS presmerovaní testovať secondary a vytvoriť nejednoznačný oracle.

## 6. CloudFront distribution ako request program

Distribution spája aliases, certificate, origins, ordered behaviors, cache/origin-request policies, edge code, logging a WAF.

Terraform skeleton:

```hcl
resource "aws_cloudfront_distribution" "payments" {
  enabled         = true
  is_ipv6_enabled = true
  aliases         = ["pay.example.com"]

  origin {
    domain_name              = aws_s3_bucket.assets.bucket_regional_domain_name
    origin_id                = "assets-s3"
    origin_access_control_id = aws_cloudfront_origin_access_control.assets.id
  }

  origin {
    domain_name = aws_lb.payments.dns_name
    origin_id   = "payments-alb"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate.cloudfront.arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
}
```

CloudFront custom-domain certificate musí byť v required ACM control Region, typicky `us-east-1`. Regional ALB certificate v `eu-central-1` nie je automaticky viewer certificate pre CloudFront.

## 7. Ordered cache behaviors

CloudFront vyhodnocuje cache behaviors ako ordered routing program. Prvý matching path pattern vyberie origin a policy set, preto health všetkých origins nepomôže, ak broad behavior zachytí authenticated API request a priradí mu nesprávny cache alebo forwarding contract.

```hcl
ordered_cache_behavior {
  path_pattern     = "/api/payments/*"
  target_origin_id = "payments-alb"

  viewer_protocol_policy = "https-only"
  allowed_methods        = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
  cached_methods         = ["GET", "HEAD"]

  cache_policy_id          = aws_cloudfront_cache_policy.api_disabled.id
  origin_request_policy_id = aws_cloudfront_origin_request_policy.api.id
}

default_cache_behavior {
  target_origin_id       = "assets-s3"
  viewer_protocol_policy = "redirect-to-https"
  allowed_methods        = ["GET", "HEAD"]
  cached_methods         = ["GET", "HEAD"]
  cache_policy_id        = aws_cloudfront_cache_policy.assets.id
}
```

First matching ordered behavior vyberie origin/policies. Broad pattern môže poslať authenticated API do static originu alebo zapnúť nesprávny cache contract. Test musí používať exact path, method, headers a query.

## 8. Cache key je isolation identity

Cache key typicky obsahuje path a selected headers, cookies, query strings a compression variant. Requests s rovnakým keyom zdieľajú cached representation.

Príliš široký key znižuje hit ratio a zaťažuje origin. Príliš úzky key môže zmiešať tenants alebo languages. Ak origin response závisí od identity value, value musí byť v bezpečnom cache keyi alebo caching musí byť disabled.

Caching-disabled policy:

```hcl
resource "aws_cloudfront_cache_policy" "api_disabled" {
  name        = "atlas-api-caching-disabled"
  min_ttl     = 0
  default_ttl = 0
  max_ttl     = 0

  parameters_in_cache_key_and_forwarded_to_origin {
    cookies_config {
      cookie_behavior = "none"
    }

    headers_config {
      header_behavior = "none"
    }

    query_strings_config {
      query_string_behavior = "none"
    }

    enable_accept_encoding_brotli = true
    enable_accept_encoding_gzip   = true
  }
}
```

Ak minimum TTL > 0, CloudFront môže cache-ovať response aspoň tento interval aj keď origin posiela `no-cache`, `no-store` alebo `private`. Preto authenticated API policy používa všetky TTL nula.

## 9. Origin request policy

Origin request policy posiela originu headers/cookies/query, ktoré nemusia byť v cache keyi.

```hcl
resource "aws_cloudfront_origin_request_policy" "api" {
  name = "atlas-api-origin-request"

  headers_config {
    header_behavior = "whitelist"
    headers {
      items = ["Authorization", "X-Tenant-ID", "X-Request-ID", "Host"]
    }
  }

  cookies_config {
    cookie_behavior = "all"
  }

  query_strings_config {
    query_string_behavior = "all"
  }
}
```

Forwardovať tenant/auth header bez zahrnutia do cache key je bezpečné iba vtedy, keď caching je vypnutý. Pri cache hit-e origin authorization neprebehne.

## 10. Private S3 origin cez OAC

```hcl
resource "aws_cloudfront_origin_access_control" "assets" {
  name                              = "atlas-assets-oac"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}
```

Bucket policy povoľuje CloudFront service principal pre exact distribution ARN:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowCloudFrontReadOnly",
      "Effect": "Allow",
      "Principal": {"Service": "cloudfront.amazonaws.com"},
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::atlas-pay-assets-prod/*",
      "Condition": {
        "StringEquals": {
          "AWS:SourceArn": "arn:aws:cloudfront::100000000042:distribution/D-PAY-17"
        }
      }
    }
  ]
}
```

CloudFront 403 sa neopravuje otvorením bucketu public. Treba rozlíšiť behavior/origin mapping, OAC attachment, bucket/KMS policy, object key/version a WAF/signed-content controls.

VPC origins môžu pripojiť CloudFront k podporovaným private ALB/NLB/EC2 origins bez public origin exposure. Majú vlastné Region/feature/network constraints.

## 11. Immutable assets a invalidation

Asset keys používajú content hash:

```text
app.7f23a1.js
styles.a91c2e.css
manifest M-44
```

Dlhý TTL je bezpečný, pretože nový release vytvorí nové keys. Invalidation je urgentný cleanup pre mutable content, nie bežný deployment mechanismus.

```bash
aws cloudfront create-invalidation \
  --distribution-id D-PAY-17 \
  --paths '/api/payments/*'
```

Invalidation neopravia origin ani browser/service-worker cache a môže vyvolať origin miss spike.

## 12. Live distribution a cache policy read-back

Live read-back fixuje distribution ETag, deployed configuration a referenced policy IDs. Tieto outputs dokazujú effective control-plane generation, no actual edge POP môže stále servovať cached representation; preto sa korelujú s request ID, `X-Cache`, `Age`, matched path a origin logom.

```bash
aws cloudfront get-distribution-config \
  --id D-PAY-17 \
  --query '{ETag:ETag,Config:DistributionConfig}' > distribution.json
```

Referenced cache policy:

```bash
aws cloudfront get-cache-policy \
  --id "$CACHE_POLICY_ID"
```

Distribution ETag identifikuje configuration version. `Deployed` preukazuje propagation completion, nie correctness všetkých paths.

Runtime request:

```bash
curl --fail --show-error -D - \
  -H 'Authorization: Bearer REDACTED' \
  -H 'X-Tenant-ID: tenant-a' \
  -H 'X-Request-ID: edge-canary-884' \
  https://pay.example.com/api/payments/P-884 \
  -o /tmp/P-884-response.json
```

Response headers `X-Cache`, `Age`, `Via` a `X-Amz-Cf-*` pomáhajú lokalizovať edge state. Token sa v evidence rediguje.

## 13. Continuous deployment

CloudFront continuous deployment používa primary distribution, staging distribution a policy, ktorá smeruje selected production requests podľa weight alebo headeru. Primary a staging caches sa nezdieľajú.

```bash
aws cloudfront copy-distribution \
  --primary-distribution-id D-PAY-17 \
  --staging \
  --caller-reference "cf-stage-$(date +%s)"
```

Po úprave staging configuration sa vytvorí continuous-deployment policy a traffic sa postupne zvýši. Viewer stále posiela request na primary domain; CloudFront interne vyberie staging.

Promotion musí sledovať cache hit/miss, origin load, privacy tests a business SLI. Cold staging cache môže zaťažiť origin viac než warmed primary.

## 14. Worked incident: tenant header forwarded, ale shared cache key

Po configuration rollout-e tenant-b dostal response tenant-a pre rovnaký path. CloudFront response mala `X-Cache: Hit from cloudfront` a `Age: 18`; origin nemal nový request tenant-b.

Rollout zamenil caching-disabled policy za policy s minimum TTL 60. `Authorization` a `X-Tenant-ID` sa forwardovali originu cez origin request policy, ale neboli v cache keyi. Prvý tenant-a request naplnil cache podľa pathu. Origin poslal `private, no-store`, no positive minimum TTL vynútil retention. Tenant-b mal rovnaký key a dostal cached body bez origin authorization.

Containment nasadil scoped non-caching policy, zachoval policy IDs, ETags, edge/origin logs a vykonal cielenú invalidation. Privacy incident process identifikoval affected cohort.

Recovery nastavila TTL 0/0/0, overila behavior precedence a testovala tenant-a/tenant-b s rovnakým pathom. Acceptance vyžadovala independent origin authorization, nulové API cache hits, private S3 cez OAC a policy-as-code gate pre combination auth headers + positive minimum TTL.

## 15. Route 53/CloudFront troubleshooting

`NXDOMAIN` vedie cez exact name/type, delegation, hosted zone, record a negative cache. `SERVFAIL` môže znamenať DNSSEC chain alebo forwarding loop. CloudFront `403` sa rozdeľuje na WAF/signed content, behavior, OAC/VPC origin a origin authorization. `502` vedie na origin DNS, TLS hostname/chain, path a listener. `503/504` vedie na origin capacity a timeout.

Privacy/caching incident:

```text
matched behavior
→ cache policy and min TTL
→ cache-key inputs
→ origin request policy
→ origin response variation and headers
→ X-Cache/Age/logs
→ cross-identity forbidden test
```

## 16. Recovery acceptance

Edge recovery sa uzatvára až po overení routing aj representation identity. Nestačí, že distribution je `Deployed`; positive test musí dostať správny obsah a forbidden test musí preukázať, že iný tenant, stale variant, wrong behavior alebo public-origin path nemôže byť prijatý.

Edge recovery je prijatá až keď authoritative DNS odpoveď smeruje na approved distribution, exact API behavior matchuje caching-disabled policy, tenant isolation prejde, origin authorization je private, stale error/object variants sú odstránené alebo expired a actual client cohorts viditeľne používajú new generation.

## Kontrolné otázky

1. Prečo hosted zone nie je delegation?
2. Prečo DNS record update nie je client cutover?
3. Prečo weighted DNS nie je request percentage?
4. Ako ordered cache behaviors vyberajú origin?
5. Prečo cache key je security boundary?
6. Aký effect má positive minimum TTL na `no-store` response?
7. Kedy je header forwardovaný originu, ale nie v cache keyi, bezpečný?
8. Ako OAC chráni S3 origin?
9. Prečo staging a primary caches menia rollout evidence?
10. Aký forbidden test uzatvorí cross-tenant cache incident?

## Oficiálna dokumentácia

- [Route 53 Developer Guide](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/Welcome.html)
- [Routing policies](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-policy.html)
- [Routing to CloudFront](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-to-cloudfront-distribution.html)
- [CloudFront Developer Guide](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Introduction.html)
- [Cache policies](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/controlling-the-cache-key.html)
- [Origin request policies](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/controlling-origin-requests.html)
- [Origin Access Control](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-s3.html)
- [Continuous deployment](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/continuous-deployment.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: RDS](rds.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Lambda →](lambda.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
