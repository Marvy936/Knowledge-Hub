# Webhooks a API integrations

Webhooks a API nodes spájajú n8n s externými control a data planes. Webhook prijíma push event, zatiaľ čo app node alebo HTTP Request node číta alebo mení remote resource; medzi nimi existujú odlišné authentication, delivery, timeout, retry, idempotency a evidence semantics.

Táto kapitola pokračuje v incidente `AGENT-N8N-07`. Refund provider poslal event na production webhook, ale reverse proxy čakala na dokončenie celého workflowu. Downstream ticketing API bolo pomalé, provider po `504` event zopakoval a workflow bez event-level dedupe vykonal druhý `POST`.

Nosný integration lifecycle je:

```text
endpoint a API contract
→ authentication a signature policy
→ request ingress, validation a event identity
→ acknowledgement alebo synchronous response
→ durable execution a dedupe decision
→ API request s scoped credential a idempotency key
→ timeout, retry a rate-limit handling
→ authoritative response a resource read-back
→ audit, reconciliation a second-delivery test
```

## 1. Webhook ako public ingress

Webhook node vystaví HTTP endpoint, ktorý prijíma request podľa configured method a path. Produkčný endpoint je súčasť attack surface a potrebuje TLS, authentication alebo signature validation, payload limits, routing a monitoring.

Náhodne neuhádnuteľná URL nie je plnohodnotný authorization control. Endpoint môže uniknúť v provider konfigurácii, logoch alebo workflow exporte.

## 2. Test URL a production URL

n8n rozlišuje test listener používaný počas developmentu a production URL viazanú na published/active workflow. Test endpoint môže byť dočasný a vyžadovať otvorený editor listener.

Provider configuration musí smerovať na production URL pre intended environment. Successful test callback nepreukazuje production registration, load balancer route ani active workflow version.

## 3. HTTP method a path identity

Method a path tvoria časť endpoint contractu spolu s hostom, base pathom a environmentom. Rovnaký path na inom instance alebo za iným reverse proxy route je odlišný ingress subject.

Zmena pathu môže zanechať starú provider subscription. Recovery musí inventarizovať registered callbacks a vypnúť deprecated endpoint až po potvrdení, že neobsahuje pending deliveries.

## 4. Reverse proxy a base URL

Self-hosted n8n za reverse proxy potrebuje správne external base URL, forwarded headers a TLS termination assumptions. Nesúlad môže generovať nefunkčné callback URLs, redirect loops alebo nesprávnu scheme.

Proxy zároveň určuje body limits, idle timeout a retry/connection behavior. n8n workflow timeout a provider timeout sú odlišné clocks a musia byť navrhnuté spolu.

## 5. Webhook authentication

Webhook môže používať podporovanú authentication configuration alebo vlastnú validation logic podľa provider contractu. Basic/header auth, token alebo signature majú odlišnú replay a rotation semantics.

Authentication preukazuje caller alebo possession of secret podľa mechanizmu, nie uniqueness eventu. Platne podpísaný event môže byť legitímne doručený viackrát.

## 6. Signature validation

Provider signature sa typicky počíta nad exact raw request representation, timestampom a shared alebo asymmetric key materialom. Ak proxy alebo parser payload zmení pred validation, recomputed signature nemusí sedieť alebo môže overovať iné bytes.

Validation musí kontrolovať algorithm, key ID, freshness window a constant-time comparison podľa provider specification. Generic „header exists“ check nie je signature verification.

## 7. Replay protection

Timestamp window obmedzí staré captures, ale neodstráni duplicate delivery v povolenom okne. Event ID alebo nonce sa musí evidovať v durable dedupe store s appropriate retention.

Replay policy nesmie blokovať legitimate provider retry predtým, než bol event durably accepted. Dedupe state sa zapisuje atomicky s intake alebo operation reservation podľa designu.

## 8. Payload validation

Pred workflow logic sa overí content type, schema version, required fields, value ranges, tenant identity a payload size. Unknown schema sa odmietne alebo uloží do quarantine, nie automaticky mapuje cez defaults.

Validation success nie je authorization pre downstream action. Resource scope a business state sa overujú proti authoritative API alebo database.

## 9. Response modes

Webhook môže odpovedať ihneď, po dokončení posledného node alebo cez explicitný Respond to Webhook node podľa workflow designu. Každý mode mení provider-observed latency a unknown-outcome boundary.

Synchronous business response je vhodná iba keď celý critical path spoľahlivo vojde do caller timeoutu. Dlhý workflow má zvyčajne najprv potvrdiť durable acceptance a outcome komunikovať osobitne.

## 10. Early acknowledgement

Early `2xx` znižuje duplicate retries spôsobené pomalým downstreamom. Je bezpečný iba vtedy, keď event bol durably prijatý alebo queue operation má preukázateľnú recovery path.

Odpoveď pred persistence môže stratiť event pri crashi. „Rýchlo odpovedať“ a „spoľahlivo prijať“ sú dve podmienky, ktoré treba splniť spolu.

## 11. Synchronous response

Synchronous response umožňuje callerovi okamžite dostať result alebo validation error. Zvyšuje coupling na workflow latency, worker capacity a všetky downstream dependencies.

Caller timeout po external commit vytvára ambiguous delivery. Provider môže retry, aj keď pôvodná execution neskôr skončí úspešne.

## 12. Provider retry semantics

Webhook provider rozhoduje, ktoré status codes a network failures retryuje, s akým backoffom a ako dlho. Workflow author musí čítať provider contract; n8n samotné nedokáže zaručiť one delivery.

Retry count a original event ID patria do observability. Nový request ID pri každom pokuse nesmie skryť, že ide o rovnaký logical event.

## 13. Event idempotency

Idempotency key sa odvodzuje z authoritative provider event ID a operation class. Durable store atomicky rezervuje alebo nájde existujúci processing/outcome record pred mutation.

Execution ID nie je vhodný dedupe key, pretože retry vytvorí novú execution. Payload hash môže pomôcť, ale legitímne odlišné events môžu mať rovnaký payload a rovnaký event sa môže serializovať odlišne.

## 14. Ordering

Providers nemusia garantovať global ordering a retries môžu prísť po novších events. Resource version, sequence alebo occurred-at timestamp sa musí vyhodnotiť podľa provider semantics.

Last-write-wins podľa arrival time môže vrátiť business state späť. Workflow potrebuje stale-event policy a authoritative resource read-back.

## 15. HTTP Request node

HTTP Request node je univerzálny API client pre operations, ktoré app node nepodporuje. Umožňuje definovať method, URL, headers, query, body, authentication, pagination a response handling.

Flexibilita rozširuje risk: workflow author preberá zodpovednosť za endpoint allowlist, request schema, credential audience, retries, sensitive logging a response validation.

## 16. App nodes

App node poskytuje typed operations a credential integration pre konkrétnu službu. Znižuje boilerplate, ale jeho supported operations a node version môžu zaostávať za provider API.

Node success stále treba čítať podľa provider response a business read-backu. Convenience adapter nevytvára atomic transaction medzi n8n a remote service.

## 17. API contract version

Endpoint path, API version, request schema, response schema a deprecation date patria do integration manifestu. Provider alias alebo default version môže zmeniť behavior bez workflow JSON diffu.

Compatibility test sa vykonáva proti sandboxu alebo contract fixture a potom bounded production canary. Unknown response fields sa môžu ignorovať iba podľa explicitnej forward-compatibility policy.

## 18. Authentication pre outbound API

Outbound request používa n8n credential alebo explicitný short-lived token získaný cez approved flow. Credential musí mať audience, scopes, tenant a operation permissions zodpovedajúce konkrétnemu node.

Zdieľaný admin token znižuje počet credentials, ale zväčšuje blast radius a confused-deputy risk. Read a write operations môžu potrebovať oddelené identities.

## 19. Request identity

Každý outbound mutation nesie business operation key a correlation ID, ak API podporuje idempotency alebo custom metadata. Technical request ID sa zaznamená spolu s execution a node identity.

Correlation header nie je authorization a idempotency header nie je audit ledger. Každý plní inú funkciu a potrebuje own retention a read-back.

## 20. Timeouts

Connect, response a total workflow timeout majú byť odvodené z end-to-end deadline. Node timeout kratší než caller deadline necháva priestor na controlled retry alebo fallback; nekonečné čakanie blokuje worker capacity.

Timeout neznamená, že remote operation neprebehla. Pri mutation sa outcome najprv číta z authoritative API podľa idempotency key alebo resource identity.

## 21. Retries

Retry je vhodný pre transient network failure, throttling alebo explicitly retryable server error. Permanent validation, authorization alebo schema errors sa opakovaním nezlepšia.

Retry policy potrebuje max attempts, backoff, jitter, deadline a idempotency. Workflow-level retry a node/provider retry sa musia koordinovať, aby sa attempts nenásobili.

## 22. Rate limits

API môže limitovať requests podľa tokenu, tenant, endpoint alebo organization. `429` a provider headers informujú o reset alebo retry intervale, ale workflow musí chrániť aj vlastnú queue a deadlines.

Parallel items môžu prekročiť limit, aj keď jeden execution je malý. Centralized throttle alebo queue partition býva potrebný pre shared credential.

## 23. Pagination

List APIs vracajú pages cez cursor, offset alebo continuation token. Workflow musí zachovať cursor, termination condition a duplicate policy pri page retry.

Offset pagination je citlivá na concurrent inserts/deletes. Cursor alebo snapshot semantics sú bezpečnejšie, ak provider ich ponúka, ale stále treba reconciliovať total count.

## 24. Partial API success

Batch API môže vrátiť HTTP success a per-item failures. Node alebo expression musí čítať item-level outcomes a nesmie interpretovať top-level `200` ako complete acceptance.

Partial success vytvára recovery set. Retryuje sa iba failed subset s rovnakými business keys, zatiaľ čo successful items sa read-backom potvrdia.

## 25. Response validation

HTTP status, headers a body sa vyhodnocujú podľa operation contractu. Empty body, async `202`, redirect alebo provider-specific error object môžu mať odlišný význam.

Successful parse nie je business proof. Pri mutation sa číta created/updated resource alebo downstream ledger a overí tenant, version a intended fields.

## 26. SSRF a dynamic URLs

URL zostavená z webhook payloadu alebo retrieved contentu môže viesť k SSRF, internal metadata access alebo exfiltration. Allowed hosts, schemes, ports a DNS/IP resolution policy musia byť enforced mimo promptu alebo user-controlled expression.

Redirects sa kontrolujú rovnako ako pôvodná URL. Public hostname, ktorý resolve na private IP, nesmie automaticky obísť network boundary.

## 27. Payload a response secrecy

Webhook bodies, Authorization headers, API tokens a response records sa môžu objaviť v execution data alebo logs. Redaction a retention sa navrhujú podľa data class a incident needs.

Vypnutie všetkého loggingu znižuje exposure, ale ničí troubleshooting. Bezpečný model uchováva identifiers a digests a sensitive payload dáva do controlled evidence store.

## 28. Shared incident `AGENT-N8N-07`

Provider mal timeout 30 sekúnd, reverse proxy 30 sekúnd a workflow potreboval pri throttlingu 42 sekúnd. Prvá ticketing mutation bola commitnutá v 28. sekunde, ale webhook response sa nedostala k providerovi a ten event zopakoval.

Druhý run použil nový execution ID a nový outbound request ID, preto dedupe založené na execution nefungovalo. Ticketing API prijalo druhý `POST`, pretože workflow neposlal provider event ID ako idempotency key.

## 29. Competing failure hypotheses

Prvá hypotéza je provider retry po timeout, druhá load balancer retry, tretia n8n queue redelivery, štvrtá workflow loop alebo pagination duplicate a piata manual replay operátorom. Každá vytvára odlišnú request a execution topology.

Evidence porovná provider delivery attempts, edge access logs, n8n execution IDs, queue attempts, node calls a downstream audit. Duplicate ticket bez upstream evidence nemá automaticky jednu príčinu.

## 30. Evidence preservation

Zachová sa raw request digest, signature fields, provider event ID, request/trace IDs, response status a latency, execution/node IDs, retry counters, outbound idempotency key a downstream object IDs. Clock sources a timezones sa normalizujú.

Sensitive headers sa nereprodukujú v plaintext. Evidence record uvádza credential reference a token generation, nie secret value.

## 31. Containment

Endpoint sa prepne na durable early acknowledgement alebo provider delivery sa dočasne nasmeruje do controlled intake. Mutation branch používa deny-by-default pre events bez idempotency identity.

Existujúce duplicate resources sa okamžite nemažú, kým sa nerozlíši authoritative record a customer impact. Compensation je osobitná audited operation.

## 32. Recovery

Workflow atomicky rezervuje event ID, posiela stable idempotency key downstream a pri timeout číta existing operation. Proxy a n8n timeouts sa nastavia podľa deadline a response mode.

Provider subscriptions, production URL a authentication generations sa znovu overia. Historical pending deliveries sa spracujú v bounded batches s reconciliation reportom.

## 33. Positive acceptance

Validný signed event dostane response v contract deadline a vytvorí jeden intended business resource. Opakované doručenie rovnakého eventu vráti already-accepted result bez ďalšej mutation.

Invalid signature, schema alebo tenant sa odmietne pred side effectom. Observability prepája ingress, execution a downstream record.

## 34. Forbidden acceptance

Endpoint nie je accepted iba preto, že curl vráti `200` alebo app node ukáže green check. Neprípustný je mutation retry bez idempotency, dynamic arbitrary URL, shared admin token a success bez resource read-backu.

Test URL sa nesmie používať ako production endpoint. Manual listener a editor session nie sú availability architecture.

## 35. Recovery acceptance

Drill spôsobí timeout po downstream commit a zopakuje event. Druhá delivery nájde existing operation a nevytvorí duplicate resource.

Ďalší drill vráti `429` s retry hintom a overí backoff, deadline a queue pressure. Workflow nesmie prejsť do synchronized retry stormu.

## 36. Second-integration acceptance

Rovnaký integration pattern sa aplikuje na druhého providera s inou signature, pagination a rate-limit semantics. Shared helper nesmie predpokladať jeden header, status code alebo idempotency behavior.

Test preukazuje, že abstraction zachováva provider-specific contract. Generic wrapper bez exact semantics by iba presunul defect do reusable vrstvy.

## 37. Praktický integration manifest

Manifest viaže ingress a outbound contracts na versions, identities a failure policy. Je review a incident artifact, nie secret store.

Každý dynamic field má authority a validation rule. Retry a response semantics sú explicitné, aby ich runtime defaults potichu nezmenili.

```yaml
integration:
  name: refund-provider-to-ticketing
  ingress:
    method: POST
    path: /webhook/refund-events
    schema: refund-event/v3
    authentication: hmac-sha256
    event_id_field: event.id
    response_mode: durable-ack
    deadline_ms: 5000
  outbound:
    operation: ticket.create
    api_version: v2
    credential_ref: ticketing/refund-writer
    idempotency_key: refund-ticket/{event.id}/{order.id}
    timeout_ms: 8000
    retry: transient-only
  forbidden:
    - unsigned payload
    - arbitrary destination URL
    - mutation without business idempotency key
```

## 38. Prevádzkové metriky

Sledujú sa webhook request rate, auth rejects, schema rejects, response latency, timeout rate, provider retries, dedupe hits, downstream `2xx/4xx/5xx/429`, unknown outcomes, pagination duplicates a business reconciliation gap. Segmentácia používa endpoint, provider, tenant, workflow version a credential generation.

Low failed-execution rate môže koexistovať s vysokým dedupe alebo cross-tenant defectom. Metriky musia obsahovať forbidden events a accepted business count.

## 39. Primárne zdroje

- [n8n Docs — Webhook node](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/)
- [n8n Docs — Respond to Webhook node](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.respondtowebhook/)
- [n8n Docs — HTTP Request node](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/)
- [n8n Docs — Handle rate limits](https://docs.n8n.io/integrations/builtin/rate-limits/)
- [n8n Docs — API authentication](https://docs.n8n.io/api/authentication/)
- [n8n Docs — Configure webhook URLs with reverse proxy](https://docs.n8n.io/hosting/configuration/configuration-examples/webhook-url/)
- [n8n Docs — SSRF protection](https://docs.n8n.io/hosting/securing/ssrf-protection/)

## 40. Zhrnutie

Webhook a API integration je distributed protocol, nie iba spojená dvojica nodes. Caller timeout, provider retry, proxy, n8n execution, credential, remote API a business ledger majú samostatné states a authorities.

Bezpečný návrh overuje signature a schema, durably prijíma event, používa stable event a operation identities, koordinuje timeouts/retries a read-backom uzatvára mutation. `2xx`, green node alebo successful execution sú čiastkové dôkazy; accepted outcome vyžaduje no-duplicate, no-cross-tenant a second-delivery proof.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Triggers, nodes, expressions a data mapping](triggers-nodes-expressions-data-mapping.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Credentials, secrets a access control →](credentials-secrets-access-control.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
