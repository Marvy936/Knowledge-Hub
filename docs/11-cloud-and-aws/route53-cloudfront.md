# Route 53 a CloudFront

Amazon Route 53 rozhoduje, akú DNS odpoveď dostane resolver pre konkrétne meno, typ, routing policy a health state. Amazon CloudFront následne ukončí viewer connection na edge dataplane-e, vyberie ordered cache behavior, zostaví cache key a pri cache miss-e vytvorí origin request. DNS steering a CDN caching sú preto dva odlišné decision systems s rozdielnymi caches, observation points a recovery časmi.

```text
DNS query
→ Route 53 authoritative verdict
→ recursive resolver a client cache
→ CloudFront viewer endpoint
→ viewer TLS a normalized request
→ first matching cache behavior
→ cache-key identity
→ cache hit alebo origin request
→ origin authorization a response
→ viewer response a business outcome
```

TTL, cache key, minimum TTL, origin request policy a error caching priamo ovplyvňujú correctness, privacy a recovery. CloudFront nie je iba performance layer a DNS record update nie je automaticky client cutover.

## 1. Exact edge subject

Atlas Payments používa hosted zone `HZ-EXAMPLE-17` pre `example.com` a record `pay.example.com A/AAAA alias`, generation `DNS-REC-31`. CloudFront distribution je `D-PAY-17`, configuration `CF-44`, alternate domain `pay.example.com`, viewer certificate `CERT-CF-12` a TLS policy `TLS-CF-8`.

Ordered behaviors tvoria request program. `/assets/*` smeruje na private S3 origin cez OAC generation `OAC-7` a immutable-asset cache policy. `/api/payments/*` smeruje na ALB origin s vypnutým cachingom a forwarded auth/tenant contextom. Default behavior smeruje na portal origin.

Sample request je `GET /api/payments/P-884` s bearer identity a `X-Tenant-ID=tenant-a`. Forbidden outcome je, aby tenant-b dostal cached response tenant-a alebo aby private S3 origin bol otvorený public ako oprava 403.

## 2. DNS authority chain

Public DNS resolution prechádza stub resolverom, recursive cache, root/TLD delegation a authoritative Route 53 name servers. Každá boundary môže držať inú generation odpovede a vlastný TTL.

```text
client query
→ recursive cache
→ root a TLD delegation
→ Route 53 hosted zone
→ record/routing/health decision
→ response cached podľa TTL
```

Hosted zone nie je domain registration ani parent delegation. Nová zone môže obsahovať správne records a byť úplne nepoužitá, ak registrar stále deleguje na old name servers.

```bash
dig +trace pay.example.com A

dig pay.example.com A +noall +answer +authority

dig @ns-123.awsdns-45.net pay.example.com A +noall +answer +authority
```

Prvý príkaz ukáže delegation chain z rootu po authoritative zone. Druhý výstup ukáže resolver-visible answer a tretí direct authoritative query obíde recursive cache. Ani jeden test nepreukazuje CloudFront TLS, matched behavior alebo origin response.

## 3. Route 53 alias na CloudFront

Route 53 alias record je authoritative DNS object, ktorý odkazuje na AWS target bez vytvorenia bežného CNAME na zone apex-e. Pre dual-stack viewer path treba samostatný `A` aj `AAAA` alias. CloudFront target nepodporuje health evaluation cez `EvaluateTargetHealth=true`, preto multi-distribution failover potrebuje vlastný supported health-check a routing design.

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

Terraform apply mení Route 53 control-plane record generation. Live read-back musí overiť exact zone, name, type a alias target:

```bash
aws route53 list-resource-record-sets \
  --hosted-zone-id ZEXAMPLE17 \
  --query 'ResourceRecordSets[?Name==`pay.example.com.`].{Name:Name,Type:Type,Alias:AliasTarget}' \
  --output yaml
```

Výstup preukazuje uložené authoritative records. Nepreukazuje, že parent delegation smeruje na túto hosted zone, že recursive resolvers už expirovali old answer alebo že existing viewer connections používajú novú distribution.

## 4. TTL a cutover

Nízky TTL znižuje maximum intended caching pre nové answers. Nezruší existing TCP/TLS sessions a nepomôže resolveru, ktorý už drží old answer s pôvodným vysokým TTL. TTL sa preto znižuje ešte pred migration window a čaká sa minimálne starý cache interval.

```text
lower TTL pred old TTL window
→ wait for old caches to expire
→ update authoritative record
→ compare authoritative a recursive answers
→ observe traffic na old/new endpoints
→ drain a retire old endpoint
→ raise steady-state TTL
```

Negative answers majú vlastný cache lifecycle. Po oprave missing recordu môže časť clients stále dostávať cached `NXDOMAIN`. Acceptance preto kombinuje authoritative query, viac recursive resolvers, client cohorts a actual traffic telemetry na old aj new endpointoch.

## 5. Routing policies

Weighted routing distribuuje DNS answers podľa relative weights, nie presné requests. Jeden veľký recursive resolver môže cacheovať jednu odpoveď pre tisíce clients, takže krátke measurement window nemusí zodpovedať configured ratio. Latency routing používa AWS latency model, nie current application p99.

Failover routing používa health state, ale business RTO zahŕňa health detection, authoritative decision, TTL, resolver behavior, reconnect a readiness secondary endpointu. Geolocation, geoproximity a IP-based policies vyberajú odpoveď podľa source cohort modelu a potrebujú default path; nie sú security boundary. Multivalue answer môže vrátiť viac healthy records, ale nie je connection-aware load balancer.

Health check musí používať direct endpoint identity. Check na tom istom failover hostname môže po DNS presmerovaní testovať secondary namiesto intended primary a vytvoriť nejednoznačný oracle.

## 6. CloudFront distribution ako request program

Distribution spája aliases, viewer certificate, origins, ordered behaviors, cache a origin-request policies, edge code, logging a WAF. Configuration je verzovaný control-plane subject; edge propagation vytvára jeho distributed effective generation.

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

ACM certificate pre alternate domain na štandardnej CloudFront distribution musí byť v `us-east-1`. Regional ALB certificate v `eu-central-1` chráni origin connection alebo ALB viewer path, ale nie automaticky viewer-to-CloudFront TLS.

## 7. Ordered cache behaviors a precedence

CloudFront vyhodnocuje ordered behaviors podľa precedence a použije prvý path pattern, ktorý request matchne; ak sa nič nezhoduje, použije default behavior. Behavior naraz vyberá origin, methods, viewer protocol, cache policy, origin-request policy a prípadné edge functions. Broad pattern môže preto presmerovať authenticated API do nesprávneho originu alebo priradiť nebezpečný cache contract.

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

Read-back musí porovnať ordered path patterns a referenced policy IDs s exact requestom. Test používa rovnaký path, method, query, headers a cookies ako production request. Úspešný request na `/ready` nepreukazuje behavior pre `/api/payments/P-884`.

## 8. Cache key je isolation identity

Cache key typicky obsahuje normalized path a selected headers, cookies, query strings a compression variant. Requests s rovnakým keyom zdieľajú cached representation bez nového origin authorization callu.

Príliš široký key znižuje hit ratio a zaťažuje origin. Príliš úzky key môže zmiešať tenants, languages alebo authorization contexts. Ak origin response závisí od identity value, value musí byť súčasťou bezpečného cache keyu alebo caching musí byť vypnutý.

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

Ak minimum TTL je väčší než nula, CloudFront môže cacheovať response aspoň tento interval aj pri origin directives `no-cache`, `no-store` alebo `private`. Authenticated API policy preto používa minimum, default aj maximum TTL nula, pokiaľ nemá explicitne navrhnutú identity-aware cache.

## 9. Origin request policy nie je cache key

Origin request policy určuje, ktoré headers, cookies a query values CloudFront pošle originu pri cache miss-e. Tieto values nemusia byť súčasťou cache keyu. Forwarding a cache isolation sú preto dve rozdielne operácie.

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

Forwardovať tenant alebo authorization header bez zahrnutia do cache keyu je bezpečné iba vtedy, keď caching je vypnutý alebo response vôbec nezávisí od tejto identity. Pri cache hit-e origin request nevznikne a origin authorization sa nevykoná.

## 10. Private S3 origin cez Origin Access Control

Origin Access Control spôsobí, že CloudFront podpisuje supported S3 origin requests cez SigV4. S3 bucket policy následne povoľuje CloudFront service principal iba pre exact distribution ARN. Viewer teda nemá dostať direct public bucket access.

```hcl
resource "aws_cloudfront_origin_access_control" "assets" {
  name                              = "atlas-assets-oac"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}
```

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

Terraform configuration preukazuje desired OAC a policy. Effective validation potrebuje CloudFront request, direct S3 forbidden request a policy read-back. CloudFront 403 sa neopravuje otvorením bucketu public; treba rozlíšiť behavior-to-origin mapping, OAC attachment, bucket alebo KMS policy, object key/version a WAF či signed-content controls.

VPC origins môžu pripojiť CloudFront k podporovaným private ALB, NLB alebo EC2 origins bez public origin exposure. Majú vlastné feature, Region a network constraints, ktoré musia byť overené proti current service documentation.

## 11. Immutable assets a invalidation

Immutable asset key obsahuje content hash, napríklad `app.7f23a1.js` alebo `styles.a91c2e.css`. Dlhý TTL je bezpečný, pretože nový release vytvorí nový object key a starý cached object zostáva správny pre starý manifest.

Invalidation je urgentný cleanup pre mutable alebo incident content, nie bežný deployment mechanismus:

```bash
INVALIDATION_ID=$(aws cloudfront create-invalidation \
  --distribution-id D-PAY-17 \
  --paths '/api/payments/*' \
  --query 'Invalidation.Id' \
  --output text)

aws cloudfront get-invalidation \
  --distribution-id D-PAY-17 \
  --id "$INVALIDATION_ID"
```

Prvý príkaz vytvorí invalidation subject a druhý číta jeho state. `Completed` dokazuje edge invalidation lifecycle, nie opravu originu, browser cache alebo service-worker cache. Veľká invalidation môže navyše vyvolať origin miss spike.

## 12. Distribution, policy a runtime read-back

Control-plane read-back začína ETagom, pretože CloudFront updates používajú configuration version na optimistic concurrency. Potom sa osobitne čítajú referenced cache a origin-request policy IDs; samotný distribution JSON nemusí obsahovať ich vnútorný contract.

```bash
aws cloudfront get-distribution-config \
  --id D-PAY-17 \
  --query '{ETag:ETag,Config:DistributionConfig}' \
  > distribution.json

aws cloudfront get-distribution \
  --id D-PAY-17 \
  --query 'Distribution.{Status:Status,Domain:DomainName,Config:DistributionConfig}' \
  --output yaml

aws cloudfront get-cache-policy \
  --id "$CACHE_POLICY_ID" \
  --output yaml
```

ETag identifikuje configuration generation a `Status=Deployed` preukazuje propagation completion. Neprokazuje correctness všetkých paths, cache keys alebo origins. Runtime request preto musí niesť exact identity a request path:

```bash
curl --fail --show-error -D /tmp/P-884.headers \
  -H 'Authorization: Bearer REDACTED' \
  -H 'X-Tenant-ID: tenant-a' \
  -H 'X-Request-ID: edge-canary-884' \
  https://pay.example.com/api/payments/P-884 \
  -o /tmp/P-884-response.json
```

Výstup a response headers `X-Cache`, `Age`, `Via` a `X-Amz-Cf-*` pomáhajú lokalizovať edge state. Dôkaz musí redigovať token a ideálne ukladať body hash alebo synthetic response, nie citlivé production payloads.

## 13. Continuous deployment a oddelené caches

CloudFront continuous deployment používa primary distribution, staging distribution a policy, ktorá smeruje selected production requests podľa weight alebo supported header mode. Viewer stále posiela request na primary domain; CloudFront interne vyberie staging. Primary a staging distributions nezdieľajú cache, takže rovnaká configuration môže mať počas warm-upu rozdielny origin load a latency.

```bash
aws cloudfront copy-distribution \
  --primary-distribution-id D-PAY-17 \
  --staging \
  --caller-reference "cf-stage-$(date +%s)"
```

Tento príkaz vytvorí staging configuration subject. Neprepojí automaticky traffic policy a nepreukazuje behavior correctness. Po úprave staging sa vytvorí continuous-deployment policy, vykonajú sa privacy a origin-capacity tests a weight sa zvyšuje iba pri stabilnom business SLI.

Promotion musí sledovať cache hit/miss, origin request volume, error rate, tenant isolation a payment canary. Cold staging cache môže zaťažiť origin viac než warmed primary, preto sa úspech nesmie posudzovať iba podľa edge latency malej cohorty.

## 14. Worked incident: tenant header forwarded, ale shared cache key

Po configuration rollout-e tenant-b dostal response tenant-a pre rovnaký path. CloudFront response mala `X-Cache: Hit from cloudfront` a `Age: 18`; origin nemal nový request tenant-b.

Rollout zamenil caching-disabled policy za policy s minimum TTL 60. `Authorization` a `X-Tenant-ID` sa forwardovali originu cez origin request policy, ale neboli v cache keyi. Prvý tenant-a request naplnil cache podľa pathu. Origin poslal `private, no-store`, no positive minimum TTL vynútil retention. Tenant-b mal rovnaký key a dostal cached body bez origin authorization.

Containment nasadil scoped non-caching policy, zachoval policy IDs, ETags, edge a origin logs a vykonal cielenú invalidation. Privacy incident process identifikoval affected cohort namiesto plošného vymazania všetkých dôkazov.

Recovery nastavila TTL 0/0/0, overila behavior precedence a testovala tenant-a/tenant-b s rovnakým pathom. Acceptance vyžadovala independent origin authorization, nulové API cache hits, private S3 cez OAC a policy-as-code gate pre kombináciu auth headers a positive minimum TTL. Second A/B/A test po warm cache musel zostať tenant-isolated.

## 15. Route 53 a CloudFront troubleshooting

`NXDOMAIN` vedie cez exact name/type, delegation, hosted zone, record a negative cache. `SERVFAIL` môže znamenať DNSSEC chain alebo forwarding loop. CloudFront `403` sa delí na viewer authorization alebo WAF, behavior selection, OAC/VPC origin a origin authorization. `502` vedie na origin DNS, TLS hostname alebo chain, path a listener. `503/504` vedie na origin capacity, connection a timeout contract.

Privacy alebo caching incident používa tento observation order:

```text
matched behavior
→ cache policy a minimum TTL
→ cache-key inputs
→ origin request policy
→ origin response variation a headers
→ X-Cache, Age a edge/origin logs
→ cross-identity forbidden test
```

Tento poriadok rozlišuje shared cache od origin-side tenant bug-u. Invalidation pred zachovaním matched policy, cache headers a origin absence môže odstrániť kľúčový dôkaz.

## 16. Recovery acceptance

Edge recovery sa uzatvára až po overení routing aj representation identity. Nestačí, že distribution je `Deployed`; positive test musí dostať správny obsah a forbidden test musí preukázať, že iný tenant, stale variant, wrong behavior alebo public-origin path nemôže byť prijatý.

Edge recovery je prijatá až keď authoritative DNS odpoveď smeruje na approved distribution, parent delegation je správna a recursive/client cohorts prešli cutoverom. Exact API path musí matchovať caching-disabled policy, tenant isolation musí prejsť po cold aj warm cache a S3 origin musí zostať private cez OAC.

Stale error alebo object variants musia byť expirované alebo cieleným spôsobom invalidované. Old endpoint sa retired až po observed traffic drain. Second operation zopakuje configuration update alebo controlled rollout bez cross-tenant response, origin overloadu alebo návratu old DNS generation.

## Kontrolné otázky

1. Prečo hosted zone nie je delegation?
2. Prečo DNS record update nie je client cutover?
3. Prečo weighted DNS nie je presné request percentage?
4. Ako ordered cache behaviors vyberajú origin a policies?
5. Prečo cache key tvorí security boundary?
6. Aký effect má positive minimum TTL na `no-store` response?
7. Kedy je header forwardovaný originu, ale nie v cache keyi, bezpečný?
8. Ako OAC chráni S3 origin a aký forbidden test to dokazuje?
9. Prečo staging a primary caches menia rollout evidence?
10. Aký A/B/A test uzatvára cross-tenant cache incident?

## Oficiálna dokumentácia

- [Route 53 Developer Guide](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/Welcome.html)
- [Routing policies](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-policy.html)
- [Routing to CloudFront](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-to-cloudfront-distribution.html)
- [CloudFront Developer Guide](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Introduction.html)
- [Cache policies](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/controlling-the-cache-key.html)
- [Origin request policies](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/controlling-origin-requests.html)
- [Origin Access Control](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-s3.html)
- [Continuous deployment](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/continuous-deployment.html)
- [How continuous deployment routes requests](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/understanding-continuous-deployment.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: RDS](rds.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Lambda →](lambda.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
