# Model Context Protocol

Model Context Protocol (MCP) štandardizuje spojenie medzi LLM host aplikáciou a externými capabilities. Neštandardizuje samotný agent loop, business authorization ani správnosť toolu. Host stále zodpovedá za to, ktorému serveru dôveruje, aké dáta mu odovzdá, čo zobrazí používateľovi, ktoré tool calls povolí a ako overí ich skutočný outcome.

Táto kapitola používa incident `AGENT-OPS-03`. Operations agent objavil cez MCP server tool `failover_checkout`, ale host cacheoval starý tool catalog a ignoroval protocol/tool generation. Server bol upgradovaný na novú schema semantics, remote call timeoutol po commite a client vytvoril nový request bez stabilnej business operation identity. Protokolové volanie napokon vrátilo success, no checkout traffic bol zmenený dvakrát.

Nosný lifecycle je:

```text
trusted host intent
→ exact MCP server identity a protocol revision
→ transport a authorization establishment
→ capability discovery alebo negotiation
→ catalog generation a schema validation
→ resource/prompt/tool selection
→ user consent, policy a approval
→ JSON-RPC request s stable operation correlation
→ result, task handle alebo unknown outcome
→ host-side validation a authoritative read-back
→ cache invalidation, audit a recovery
```

## 1. Čo MCP rieši

MCP vytvára spoločný protocol surface pre data a capabilities, ktoré host poskytne modelu alebo agentovi. Namiesto vendor-specific konektorov môže host pracovať s rovnakým základným modelom serverov, tools, resources, prompts a súvisiacich protocol messages.

Interoperabilita však končí na wire a schema boundary. MCP server môže implementovať tool zle, zavádzať v description, vracať stale resource alebo vykonať side effect mimo deklarovanej semantics.

## 2. Host, client a server

**Host** je aplikácia vlastniaca user experience, model orchestration, consent a trust policy. **Client** je protocol component v hoste, ktorý komunikuje s jedným MCP serverom. **Server** publikuje capabilities a vykonáva requests v rámci vlastného trust a execution boundary.

Toto rozdelenie je bezpečnostne dôležité. Model nie je MCP client a MCP server nie je automaticky trusted extension hosta; medzi model proposalom a protocol execution musí zostať deterministic policy layer.

## 3. Exact connection subject

Connection record musí identifikovať server endpoint, server identity, transport, protocol revision, client generation, authorization subject a negotiated capabilities. Názov typu „GitHub MCP“ nestačí, pretože viac serverov môže používať rovnaký display name.

```yaml
connection_id: mcp-conn-8842
server_id: ops-control-prod
endpoint: https://mcp.ops.example.com/mcp
transport: streamable-http
protocol_revision: 2025-11-25
client_generation: mcp-host/v8.4.1
auth_subject: svc-agent-retail-eu
catalog_generation: sha256:1e4a...
tenant: retail-eu
environment: production
```

Pri moderných alebo draft revisions sa presná revision pinne rovnako. Automatický fallback sa zaznamená ako loaded state, nie iba debug detail.

## 4. JSON-RPC message identity

MCP používa JSON-RPC message model. Request ID koreluje protocol request a response, ale nemusí byť business idempotency key.

```json
{
  "jsonrpc": "2.0",
  "id": "rpc-7712",
  "method": "tools/call",
  "params": {
    "name": "failover_checkout",
    "arguments": {
      "operation_id": "checkout-recovery-021",
      "target_provider": "provider-b"
    }
  }
}
```

Ak client retryuje request s novým JSON-RPC ID, server stále potrebuje stable operation identity v arguments alebo tool contracte. Protocol correlation sama duplicate side effect nezastaví.

## 5. Protocol revision

MCP sa vyvíja cez dated protocol revisions. Produkčný client musí poznať presnú wire semantics, nie iba major verziu SDK.

Dokumentácia `2025-11-25` používa initialization a negotiated capabilities. Novšia `2026-07-28` era v aktuálnych SDK materiáloch mení core na stateless protocol, odstraňuje protocol-level session a presúva dlhé Tasks do extension modelu. Tieto eras nie sú zameniteľné a fallback musí byť explicitný a testovaný.

## 6. Version pinning

Pre high-impact tools sa preferuje pin exact revision alebo explicitný compatibility matrix. `auto` negotiation je vhodná iba vtedy, keď host vie bezpečne podporovať obe semantics a zaznamená, na ktorej skončil.

```yaml
mcp_version_policy:
  allowed:
    - 2025-11-25
    - 2026-07-28
  preferred: 2026-07-28
  fallback: explicit
  required_extensions:
    - io.modelcontextprotocol/tasks
```

Ak server neponúkne required capability alebo extension, host nemá simulovať podporu vlastným nezdokumentovaným behaviorom.

## 7. Legacy lifecycle

V lifecycle revision `2025-11-25` klient začína `initialize` requestom, server odpovie protocol version a capabilities a klient odošle `notifications/initialized`. Až potom sa používa normálna operation phase.

Initialization result je loaded-state evidence. Ak proxy alebo connection pool zmieša sessions medzi odlišnými server generations, catalog a capability assumptions môžu byť neplatné.

## 8. Stateless protocol a application state

Stateless protocol neznamená stateless business application. Server môže vrátiť explicitný handle, napríklad `browser_id`, `deployment_id` alebo task ID, ktorý klient použije v ďalšom requeste.

Výhodou explicitných handles je viditeľná ownership a routing semantics. Nevýhodou je, že model alebo host musí handle bezpečne uchovať, scopeovať a nesmie ho zameniť medzi tenantmi či operations.

## 9. Capability discovery

Capabilities hovoria, ktoré optional features peer podporuje. Súčasne musia byť viazané na connection/server generation, pretože server upgrade môže zmeniť tools, resources, prompts, extensions alebo notification behavior.

Discovery nie je authorization. To, že server publikuje tool, neznamená, že current user, agent alebo tenant ho smie volať.

## 10. Tools

Tool je callable capability s menom, description, input schema a prípadne output schema alebo annotations. Host používa schema na syntaktickú validáciu, ale domain invariants musí implementovať samostatne.

```json
{
  "name": "failover_checkout",
  "description": "Moves checkout traffic to an approved provider.",
  "inputSchema": {
    "type": "object",
    "required": ["operation_id", "subject_uid", "expected_generation", "target_provider"],
    "properties": {
      "operation_id": {"type": "string"},
      "subject_uid": {"type": "string"},
      "expected_generation": {"type": "integer"},
      "target_provider": {"enum": ["provider-a", "provider-b"]}
    },
    "additionalProperties": false
  }
}
```

Schema nevie sama overiť, či provider je healthy, approval platí alebo subject UID patrí current tenantovi. Tieto checks zostávajú v host policy a server executor boundary.

## 11. Tool names a catalog identity

Tool name nemusí byť globálne unikátny. Host používa compound identity server ID + tool name + tool schema/catalog generation.

Ak dva servery publikujú `delete_file`, model nesmie vidieť iba jeden neodlíšený názov. Adapter môže vytvoriť namespaced alias, ale audit musí zachovať original server a tool identity.

## 12. Tool descriptions sú untrusted input

Description a annotations pochádzajú zo servera. Malicious alebo kompromitovaný server môže tvrdiť, že mutation tool je read-only alebo že poskytnutie secrets je potrebné.

Host preto udržiava vlastný trust classification, tool allowlist, risk policy a approval requirements. Server metadata pomáhajú s UX a discovery, ale nie sú jedinou authority.

## 13. Tool catalog caching

`tools/list` môže byť cacheovaný iba s generation, TTL a invalidation semantics. Cache hit bez server/tool generation môže načítať starú schema po incompatible deploymente.

Pri mutation tooloch host pred execution overí, že selected tool identity a schema digest stále zodpovedajú approved proposal. Catalog refresh po approvale môže approval invalidovať.

## 14. Resources

Resource predstavuje readable context identifikovaný URI. Resource content je stále untrusted external data a môže obsahovať prompt injection, stale state alebo data z nesprávneho tenant scope.

Host validuje URI scheme, server ownership, MIME type, size, sensitivity, freshness a authorization. Resource read success neznamená, že obsah je pravdivý alebo vhodný na model context.

## 15. Resource templates a subscriptions

Template umožňuje parameterizované resource URIs. Parameter validation musí zabrániť path traversal, cross-tenant lookup a arbitrary backend queries.

Ak revision/server podporuje change notifications alebo subscriptions, host ich považuje za invalidation hint, nie za jediný source of truth. Stratená notification nesmie nechať cache navždy validnú.

## 16. Prompts

Server prompt je templated message alebo workflow input. Nie je to trusted system instruction a nemá prepisovať host policy, tenant boundary alebo tool authorization.

Host môže prompt zobraziť používateľovi, namespacovať ho a obmedziť rolu, v ktorej sa vloží. Prompt update potrebuje generation a eval rovnako ako lokálny prompt registry artifact.

## 17. Client-provided features

Niektoré revisions umožňujú serveru požiadať client o elicitation, sampling alebo iný input. Takýto reverse request rozširuje attack surface, pretože server môže skúšať získať citlivé dáta alebo model output.

Host používa samostatný consent a policy flow. Server nemá automaticky prístup k celému conversation contextu ani k arbitrary model provider credentials.

## 18. Transports

Bežné transporty sú stdio a HTTP-based transport. Stdio typicky spúšťa server ako lokálny subprocess; HTTP server je nezávislá remote služba.

Transport mení trust a operational model. Lokálny subprocess potrebuje binary provenance, filesystem/sandbox boundary a čistý stdout; remote HTTP potrebuje TLS, endpoint identity, Origin validation, authentication, network policy a timeout/retry semantics.

## 19. Stdio boundary

Pri stdio serveri je stdout protocol channel a nesmie obsahovať ne-protocol log lines. Logs patria na stderr alebo samostatný telemetry channel.

Host kontroluje executable path, digest, arguments, environment variables a inherited credentials. „Lokálne“ neznamená bezpečné, pretože subprocess môže čítať user files alebo network podľa OS permissions.

## 20. HTTP boundary

HTTP transport musí validovať canonical server URI a security headers podľa podporovanej revision. Local server nemá defaultne bindovať na všetky interfaces, pretože remote web page môže zneužiť DNS rebinding alebo otvorený endpoint.

Gateway nesmie meniť JSON-RPC IDs, protocol headers alebo streaming semantics bez auditovateľného contractu. Retry na mutation requeste zostáva application decision, nie implicitný proxy behavior.

## 21. Authorization

MCP authorization pre HTTP používa OAuth-based model, v ktorom server vystupuje ako protected resource a client získava token pre canonical resource. Token audience/resource musí byť viazaný na konkrétny MCP server.

Transport authorization odpovedá, či client smie komunikovať so serverom v určitom scope. Neodpovedá automaticky, či konkrétny tool call spĺňa business policy a current user intent.

## 22. Token handling

Host uchováva tokens mimo model contextu a mimo untrusted server outputov. Server nedostáva provider alebo iné server credentials, ktoré nepotrebuje.

Refresh, incremental scopes a step-up authorization sa zaznamenávajú ako identity generations. Resume po dlhom čakaní musí znovu overiť token validity a current user entitlement.

## 23. Consent

Používateľ má vidieť, ktorý server dostane aké dáta a ktorý tool vykoná akú akciu. Všeobecné „allow MCP“ nie je dostatočný approval pre destructive alebo financial mutations.

Consent artifact sa viaže na server identity, tool identity, canonical arguments, data disclosure a TTL. Catalog alebo argument drift vyžaduje nový review.

## 24. Structured results

Tool result sa validuje proti output schema, ak existuje, a následne proti host domain contractu. Text „success“ bez stable result ID, subject generation alebo postcondition nie je authoritative evidence.

```json
{
  "operation_id": "checkout-recovery-021",
  "change_id": "chg-7712",
  "subject_uid": "traffic-policy/checkout-prod/uid-9941",
  "applied_generation": 418,
  "status": "committed"
}
```

Host ešte overí effective traffic a checkout business metrics. Protocol result je jedna observation vrstva.

## 25. Error model

JSON-RPC error, tool-level error a business rejection sú odlišné. Client musí zachovať error code, message, data, server generation a request identity.

Transport timeout nevytvára JSON-RPC error a znamená unknown outcome. Tool result s `isError` alebo domain failure môže byť validný protocol response, ktorý sa nemá transportne retryovať bez contractu.

## 26. Progress a cancellation

Progress notification je advisory evidence o ongoing work. Nemá sa považovať za commit a nemá resetovať neobmedzený overall deadline.

Cancellation je request, nie garancia zastavenia downstream side effectu. Host po cancel response stále zisťuje remote task a business state.

## 27. Tasks a long-running tools

Novšie MCP extension modely umožňujú tool callu vrátiť durable task handle. Client potom uchová task ID, server identity, protocol revision, extension generation, last state a original operation correlation.

Task handle rieši disconnect a polling, ale nie idempotency sám. Reconnect musí vykonať `get` alebo subscribe pôvodného tasku, nie znovu `tools/call` s novou operation identity.

## 28. Extension negotiation

Extension je opt-in capability s vlastnou identifier a lifecycle. Host povoľuje iba známe extensions, verzie a risk profiles.

Required extension, ktorej client nerozumie, musí viesť k fail-closed connection alebo requestu. Ignorovať required semantics môže zmeniť authentication, task lifecycle alebo result interpretation.

## 29. Pagination

Catalogs a resources môžu byť stránkované. Client musí prejsť cursor chain bez duplicity alebo vynechania a zachovať catalog snapshot assumptions.

Ak sa catalog mení počas pagination, host môže dostať mixed generation. Pre high-impact use je vhodný server-provided generation/ETag alebo opakovaný read s consistency checkom.

## 30. Logging a tracing

Trace spája host operation, model proposal, server/tool identity, protocol revision, JSON-RPC ID, task ID, authorization subject, arguments digest, result digest a postcondition read-back. Sensitive payloads sa defaultne redigujú alebo nahrádzajú reference/digestom.

Server logs bez host correlation nedokážu vysvetliť, ktorý user intent alebo approval request vyvolal tool. Host logs bez server request ID zase nevedia potvrdiť remote execution.

## 31. Registry a discovery

Registry alebo configuration catalog pomáha nájsť server, ale discovery record nie je automatický trust endorsement. Host overuje publisher, package/image digest, endpoint ownership, signature, security policy a allowed environment.

Dynamic installation servera modelom je high-risk operation. Produkčný host ju nedovolí bez admin policy, sandboxu a explicitného review.

## 32. Multi-tenant isolation

Server a host musia vynucovať tenant z authenticated contextu, nie z model-provided argumentu. Tool môže prijať resource ID, ale server musí potvrdiť jeho ownership.

Caches, task handles, resource subscriptions, traces a tokens sú tenant-scoped. Cross-tenant catalog môže zdieľať public metadata, nie private capability availability alebo results.

## 33. Incident `AGENT-OPS-03`

Host mal cacheovaný tool catalog generation `v6`, v ktorom `failover_checkout` prijímal `provider`. Server deploy `v7` zmenil semantics na `target_provider` a pridal povinný `expected_generation`, ale compatibility adapter doplnil current generation automaticky.

Approval karta stále zobrazila staré arguments. Po call timeout-e gateway retryovala request a host následne vytvoril nový JSON-RPC ID aj nový operation key. Server commitol dve changes, pretože protocol IDs neboli business dedup keys.

Správny tok bol:

```text
pin server and protocol revision
→ refresh catalog and bind tool schema digest
→ construct canonical command
→ show exact approval
→ send stable operation ID
→ timeout becomes unknown outcome
→ query task/change status
→ attach existing result
→ verify traffic and checkout outcome
```

## 34. Failure hypotheses

MCP incident sa diagnostikuje po vrstvách. „Server vrátil chybu“ alebo „model vybral zlý tool“ nevysvetľuje version, transport, auth, catalog, schema ani business outcome.

- **Wrong server identity** — host sa pripojil k endpointu alebo subprocessu inej generation; overí sa endpoint, executable digest a server metadata.
- **Protocol-era mismatch** — client a server interpretovali lifecycle, sessions alebo extensions rozdielne; dôkazom sú wire headers a loaded revision.
- **Stale catalog** — model/host použil starý tool schema alebo description; porovná sa catalog digest s approval a execution.
- **Capability assumption** — host volal feature, ktorá nebola negotiated alebo discoverovaná.
- **Authorization audience error** — token bol vydaný pre inú resource URI alebo scope.
- **Schema-only validation** — payload prešiel JSON Schema, ale porušil tenant, generation alebo business invariant.
- **Unsafe transport retry** — gateway zopakovala mutation po timeoute bez stable operation key.
- **Untrusted annotation** — host uveril server metadata o read-only alebo destructive behavior.
- **Task duplication** — client po reconnecte vytvoril nový tool call namiesto pollingu pôvodného tasku.
- **False protocol success** — JSON-RPC response bol success, ale effective resource alebo business outcome sa nezmenil správne.

Každá hypotéza sa testuje proti connection manifestu, wire trace, auth metadata, catalog generation, tool contract, executor ledger a business read-backu. Model transcript je iba jedna časť evidence.

## 35. Containment

Pri MCP incidente host odpojí alebo quarantinuje konkrétny server/tool generation, nie celý agent ecosystem bez rozlíšenia. Mutation tools sa skryjú z model catalogu a existujúce tasks sa prepnú do read-only reconciliation.

Tokens sa revokujú alebo scope obmedzí, ak je podozrenie na server compromise. Catalog cache sa označí invalid a zachová sa pre forenznú analýzu.

## 36. Recovery

Recovery pinne known-good server a protocol revision, obnoví catalog, porovná schemas, opraví auth alebo transport policy a reconciliuje unknown remote tasks. Approval requests vytvorené pre starý tool digest sa nerecyklujú.

Compatibility test pokrýva podporované revisions, catalog change, pagination, auth refresh, timeout, cancellation, task resume, duplicate request a malformed/untrusted outputs. Až potom sa mutation capability znovu povolí.

## 37. Positive acceptance

Pozitívny test pripojí exact server, overí protocol revision a capabilities, načíta catalog, zavolá read tool a následne approval-bound idempotent mutation. Result sa validuje a business postcondition sa potvrdí mimo MCP server summary.

## 38. Forbidden acceptance

Zakázaný test zmení tool schema alebo server generation po approvale, použije token pre nesprávnu audience, vráti malicious annotation alebo po timeout-e zopakuje call s novým operation key. Host musí flow zastaviť.

## 39. Recovery acceptance

Recovery test reštartuje MCP server, gateway a host počas long-running tasku. Client musí znovu objaviť kompatibilný server, načítať pôvodný task/change podľa stable identity a nesmie vytvoriť duplicate side effect.

## 40. Second-operation acceptance

Nová legitímna operation použije current catalog a nový business operation ID. Nesmie zdediť starý task handle, approval ani stale catalog snapshot, ale môže bezpečne reuse rovnaký trusted connection podľa aktuálnej policy.

## 41. Zhrnutie

MCP štandardizuje agent-to-tool a host-to-context wire contract. Neprenáša automaticky trust, authorization, idempotency ani business correctness.

Produkčný MCP integration je prijateľný až vtedy, keď tím vie pre každý call pomenovať exact server a protocol revision, loaded capability/catalog generation, disclosed data, current identity, approved command, stable side-effect identity, remote outcome a nezávislý business read-back.
