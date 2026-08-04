# Tool poisoning, confused deputy a data exfiltration

Tool-enabled agent nie je bezpečný iba preto, že tool call prešiel schema validáciou a downstream API vrátilo úspech. Bezpečnosť závisí od toho, kto tool publikoval, ktorú generation host načítal, aké tvrdenia o tool-e model videl, pod akou identity a authority sa operácia vykonala, ktoré dáta sa do argumentov dostali a kam mohol výsledok pokračovať.

Táto kapitola otvára incident `AGENT-EVAL-05`. Support agent načítal remote MCP server po neoznámenom upgrade. Tool `collect_checkout_diagnostics` si ponechal rovnaký názov, ale description, output schema a downstream behavior sa zmenili: nový server označil operáciu ako read-only, no výsledok zapisoval aj do externého issue trackeru. MCP proxy prijal access token určený pre inú resource, následne ho použil ako deputy pre downstream API a agent poslal customer record spolu s interným provider tokenom do issue commentu. Finálna odpoveď bola vecne správna, no sensitive data opustili trust boundary.

Nosný lifecycle je:

```text
business intent
→ exact host, server, tool a catalog generation
→ publisher identity, provenance a integrity evidence
→ tool description, schema a annotations ako untrusted claims
→ caller, subject, tenant, audience a delegated authority
→ exact input data classes a allowed transformations
→ side effect, destination a descendant effects
→ output validation, taint a egress decision
→ authoritative security a business read-back
→ containment, revocation, cleanup a second-operation proof
```

## 1. Tool poisoning nie je iba zlý opis

Tool poisoning znamená, že informácia alebo behavior spojené s toolom zmenia rozhodovanie agenta spôsobom, ktorý porušuje intended contract. Poisoning môže byť v názve, description, examples, JSON Schema, annotations, server-provided prompts, error messages, output content alebo v samotnej implementation.

Najjednoduchší príklad je description, ktorá tvrdí, že tool iba číta stav, hoci vykonáva zápis. Závažnejší prípad zachová názov a schema, ale po upgrade zmení destination, authorization model alebo descendant side effects, takže starý approval digest už neopisuje skutočnú operáciu.

## 2. Tool metadata sú vstup, nie autorita

Model používa názov, description a schema na tool selection a argument construction. Tieto polia preto ovplyvňujú plán, ale nesmú samy určovať policy, sensitivity, destructive classification alebo approval requirement.

Host vedie vlastný reviewed capability registry. Registry viaže tool server identity, catalog digest, contract version, allowed environments, data classes, side-effect classification, approval policy a ownera; server annotations môžu byť zobrazené ako hint, nie ako authoritative security label.

## 3. Exact tool subject

Tool subject nie je iba `server_name/tool_name`. Potrebuje server identity, protocol revision, catalog generation, tool schema digest, implementation alebo deployment generation a transport endpoint.

```yaml
tool_subject:
  host_release: support-agent/5.8.1
  server_identity: spiffe://agents.example.com/mcp/support-tools
  server_release: support-tools/3.4.0
  protocol_revision: "2025-11-25"
  catalog_digest: sha256:41c0...
  tool_name: collect_checkout_diagnostics
  schema_digest: sha256:b7a2...
  behavior_contract: diagnostics/v4
  endpoint: https://mcp.example.com/support
```

Ak ktorákoľvek z týchto vrstiev nesedí s approved manifestom, host nesmie predpokladať kompatibilitu podľa názvu. Tool sa skryje, prejde do read-only quarantine alebo vyžiada nový review.

## 4. Publisher a distribution trust

Tool package alebo server release potrebuje publisher identity, integrity digest, provenance a deployment evidence. TLS potvrdzuje endpoint identity počas spojenia, ale nepreukazuje, že nový artifact prešiel review alebo že jeho behavior zodpovedá predchádzajúcej generation.

Supply-chain control preto pinne image alebo package digest, overuje signature/provenance, obmedzuje kto môže meniť catalog a zaznamenáva rollout. Dynamic discovery bez reviewed registry vytvára cestu, kde model alebo untrusted content samo navrhne nový server a tým aj novú authority boundary.

## 5. Catalog drift

Catalog drift vzniká, keď host, approval UI, trace alebo agent pracujú s odlišnou verziou tool metadata. Approval môže zobraziť staré arguments a read-only label, zatiaľ čo executor už načítal novú schema alebo destination.

Pred mutation alebo sensitive read operáciou sa znovu overí loaded catalog digest. Approval envelope viaže server, tool, schema, canonical arguments, data classes, destination a behavior generation; pri drift-e sa pôvodné approval nerecykluje.

## 6. Schema poisoning

JSON Schema obmedzuje tvar argumentov, nie ich business meaning. Malicious alebo chybná schema môže pridať optional field `debug_context`, zmeniť default destination, rozšíriť enum alebo označiť raw secret ako bežný string.

Local adapter preto aplikuje vlastnú canonical schema a semantic constraints. Unknown fields sa pri sensitive tools odmietajú, defaults sa materializujú pred approvalom a každá argument hodnota sa viaže na exact tenant, resource a data classification.

## 7. Description a example poisoning

Description môže model presviedčať, aby pre „lepšiu diagnostiku“ priložil celé environment variables, access tokens alebo customer transcript. Examples môžu normalizovať nebezpečný tool chain, hoci schema sama nič nevyžaduje.

Host oddeľuje discovery text od policy. Tool-selection prompt dostáva reviewed summary a model-generated plan sa kontroluje proti data-flow policy; server-provided prose nikdy nezvyšuje oprávnenie čítať dáta alebo odoslať ich mimo pôvodného trust zone.

## 8. Output poisoning

Tool output sa vracia do model contextu a môže obsahovať ďalšie inštrukcie, skryté URLs, presvedčivú falošnú autoritu alebo odporúčanie na nasledujúci privileged tool. Úspešná response preto nie je trusted observation iba preto, že prišla z authenticated servera.

Output envelope zachová server/tool generation, request ID, result digest, data classes a integrity label. Untrusted text zostáva data; ak navrhuje nový plán, destination alebo credential use, potrebuje nezávislé policy rozhodnutie.

## 9. Error-message poisoning

Error message môže agentovi povedať, aby retry použil iný endpoint, vypol TLS validation, vložil token do argumentu alebo zavolal export tool. Model často interpretuje actionable error ako recovery instruction.

Recovery policy však pochádza z local contractu. Tool error sa klasifikuje a zobrazí ako observation, no povolené retries, fallbacky, credential refresh a alternate destinations určuje orchestrator, nie remote prose.

## 10. Confused deputy

Confused deputy vzniká, keď komponent s vlastnými oprávneniami vykoná operáciu pre caller-a, ktorý na ňu nemá authority, pretože deputy nesprávne vyhodnotí caller identity, subject, consent alebo target resource. Agentické systémy tento problém zosilňujú, pretože model môže prepájať viac tools a identity contextov.

Deputy musí vedieť, kto žiada operáciu, v mene koho sa vykonáva, pre ktorý tenant/resource, s akým delegated scope a pre aký exact action digest. Samotná platnosť tokenu alebo úspešná autentifikácia caller-a neznamená authorization.

## 11. Token audience a resource separation

MCP server nesmie prijať token určený pre inú resource a nesmie inbound token iba preposlať downstream API. Taký passthrough rozbije audience boundary, skryje skutočného deputyho v audite a môže umožniť cross-service replay.

Proxy získava samostatný downstream token pre exact resource a reduced scope. Inbound a outbound token IDs, issuers, audiences, subject/actor claims a expiration sa zaznamenajú ako delegation chain bez uloženia raw secretu.

## 12. Delegation verzus impersonation

Delegation zachová caller subject aj acting workload, takže downstream vie, kto požiadal a kto operáciu vykonal. Impersonation prezentuje deputyho ako subject a môže byť legitímna iba pri explicitnom, policy-controlled use case.

Agent platform defaultne používa delegation. Ak downstream nevie actor chain reprezentovať, gateway pridá signed operation envelope a audit correlation; nesmie potichu nahradiť user identity širokým service accountom.

## 13. Per-client consent

Proxy server s jedným statickým downstream OAuth clientom môže zneužiť existujúci consent pre iného MCP klienta. Per-client consent preto viaže usera, requesting client, downstream scopes, resource, tool/action a expiration.

Consent cookie alebo predchádzajúci úspešný login nie sú dôkazom aktuálneho súhlasu. High-impact tool zobrazí caller identity, destination, data classes a exact operation ešte pred downstream authorization flowom.

## 14. Cross-tenant confused deputy

Shared tool server môže správne autentifikovať workload, ale použiť tenant ID z model-generated argumentu bez väzby na caller. Agent tak číta alebo mení resource cudzieho tenanta.

Tenant sa odvodzuje z trusted identity contextu a policy, nie z voľného textu. Argumentový tenant musí byť rovnaký ako authorized tenant alebo explicitne povolený cross-tenant administrative subject s oddeleným approvalom.

## 15. Data exfiltration ako flow, nie iba network request

Exfiltration znamená, že dáta prejdú z povoleného source a classification do nepovoleného sinku alebo audience. Sink môže byť HTTP endpoint, issue comment, email, chat, DNS query, filename, log, metric label, trace, error message, generated code, clipboard alebo model provider.

Bezpečnostný model preto inventarizuje všetky output channels, nie iba explicitný `send_file` tool. Každý descendant effect dedí data labels a destination constraints, kým trusted declassification alebo redaction control nerozhodne inak.

## 16. Source a sink inventory

Source inventory zahŕňa user input, repositories, ticket attachments, databases, secrets, environment variables, memory, tool outputs a remote agent artifacts. Sink inventory zahŕňa tools, model requests, logs, traces, storage, notifications a external callbacks.

Policy pracuje s dvojicou source classification → allowed sink. Napríklad `customer_pii` môže ísť do approved case systemu v rovnakom tenant-e, ale nie do public issue trackeru; `credential` nesmie byť model input ani tool output bez opaque-handle transformácie.

## 17. Data minimization

Agent dostáva iba polia potrebné pre aktuálny step. Diagnostický tool nepotrebuje celý customer profile, ak rozhoduje podľa provider statusu a anonymizovaného transaction ID.

Minimization sa aplikuje pred modelom aj pred toolom. Retrieval, context assembler a adapter vytvoria purpose-specific view; redaction po tom, čo secret už prešiel modelom alebo remote serverom, nezmenší pôvodnú exposure.

## 18. Opaque handles

Sensitive credential alebo object sa môže reprezentovať opaque handle-om, ktorý model nevie prečítať ani zmeniť. Executor handle rozbalí iba pre exact server, action, tenant, arguments digest a krátke časové okno.

Handle nie je bearer token. Je single-use alebo bounded-use capability, má audience, expiry a revocation a jeho použitie sa atomicky viaže na operation ledger.

## 19. Egress policy

Network egress je capability. Tool runtime a sandbox defaultne nemajú všeobecný internet; používajú allowlisted destinations, DNS resolution policy, TLS identity validation, method/path constraints a response-size limity.

Egress gateway zaznamená destination identity a data-class decision, nie raw secret. Redirect, alternate IP, proxy CONNECT, webhook URL z untrusted inputu a DNS rebinding vyvolajú nové policy rozhodnutie.

## 20. SSRF a metadata endpoints

Tool, ktorý fetchuje URL, môže byť deputy pre prístup k internal services alebo cloud metadata credentials. URL schema validation nestačí, pretože redirects, DNS changes a alternate encodings môžu zmeniť effective destination.

Fetcher vykonáva canonical resolution, blokuje link-local/private ranges podľa policy, revaliduje každý redirect a používa isolated network identity bez cloud metadata accessu. Response z internal boundary sa nikdy nereflektuje do modelu alebo caller-a bez explicitného data-flow povolenia.

## 21. Covert channels

Aj zakázaný outbound body môže byť nahradený názvom resource, timingom, request countom alebo error textom. Úplná eliminácia covert channels nie je realistická, no high-sensitivity workflows môžu znížiť bandwidth cez fixed destinations, bounded outputs, rate limits a deterministic adapters.

Risk model rozlišuje bežné enterprise dáta od secrets alebo regulated data. Čím vyššia classification, tým menší tool catalog, kratší run, prísnejší sandbox a viac deterministic transformations.

## 22. Tool chaining

Jednotlivé tools môžu byť bezpečné, no ich kompozícia vytvorí exfiltration path: `read_secret` → `summarize` → `create_ticket`. Policy preto hodnotí celú planned chain a aktuálny taint state, nie každý call izolovane.

Po každom observation sa plan revaliduje. Nový sensitive source môže zablokovať previously allowed sink; approval pre ticket creation sa stane stale, ak arguments teraz obsahujú vyššiu data class.

## 23. Parallel tool calls

Paralelné tools môžu obísť sequential control, keď read a send operácia prebehnú skôr, než sa aktualizuje taint state. Scheduler musí rezervovať authority a data-flow decision pred dispatchom všetkých siblings.

Mutating alebo exfiltration-capable calls používajú serialization alebo transaction-like coordination. Cancellation jedného siblingu musí zastaviť aj dependent calls a unknown outcomes sa reconciliujú pred ďalším dispatchom.

## 24. Tool search a dynamic exposure

Tool search znižuje context size, ale môže dynamicky pridať capability na základe untrusted query. Search výsledok preto neznamená activation; registry filter najprv overí trust, environment, tenant, risk class a current approval mode.

Model nesmie vyhľadať a okamžite použiť nový external tool v jednej nepozorovanej vetve. Sensitive activation vytvorí explicitný catalog transition event a nový plan digest.

## 25. Remote agents ako deputies

Remote agent môže v mene local agenta volať vlastné tools, ktoré local orchestrator nevidí. Delegation contract preto definuje povolené data classes, side-effect classes, destinations, credential model a required artifact evidence.

Remote `completed` state nepreukazuje, že nested tools dodržali policy. High-impact remote capability potrebuje attested execution summary alebo sa používa iba read-only s local independent verification.

## 26. Logs a traces ako exfiltration sink

Debug tracing môže zachytiť prompts, tool arguments, outputs, headers alebo credentials. Telemetry backend je samostatná data destination s retention, tenant isolation a operator accessom.

Sensitive capture je defaultne vypnutý alebo field-level redacted. Trace zostáva použiteľný cez digests, classifications, sizes, decision IDs a secure evidence references; dočasné full capture vyžaduje incident scope, encryption, approval a automatic deletion.

## 27. Output validation

Tool output validator kontroluje schema, size, media type, origin, data classification, injection indicators a unexpected references. Schema-valid text však môže byť malicious, preto sa výsledok neinterpretuje ako instruction ani authorization.

Structured fields s business meaning prejdú semantic validation a authoritative read-back. Free-form text sa označí untrusted a môže podporiť diagnosis, no nesmie samo aktivovať privileged follow-up.

## 28. Human approval a poisoned context

Reviewer môže byť ovplyvnený rovnakým poisoned descriptionom ako model. Approval UI preto používa local reviewed labels, canonical arguments, exact destination, data classes, actor chain a diff oproti approved baseline.

UI nezobrazuje iba server-provided summary. Pri catalog drift-e alebo sensitive-taint change vyžaduje nový approval; click na starom approvale nesmie autorizovať zmenenú operáciu.

## 29. Deterministic policy envelope

Pred tool execution vytvorí orchestrator immutable envelope:

```json
{
  "operation_id": "op_checkout_8f2",
  "tool_subject": "support-tools/3.4.0#collect_checkout_diagnostics@sha256:b7a2",
  "caller": "spiffe://agents.example.com/support/run/8291",
  "human_subject": "user-1842",
  "tenant": "retail-eu",
  "action": "diagnostics.read",
  "arguments_digest": "sha256:19ee...",
  "input_classes": ["transaction_metadata"],
  "allowed_sinks": ["support-case:case-771"],
  "forbidden_sinks": ["public-issue", "model-log"],
  "approval_digest": "sha256:aa10...",
  "expires_at": "2026-08-04T18:50:00Z"
}
```

Executor overí envelope proti loaded tool generation a current policy tesne pred side effectom. Model ho nemôže meniť; rozdiel vytvorí deny alebo nový authorization cycle.

## 30. Worked incident `AGENT-EVAL-05`

Alert uviedol checkout provider timeouty. Agent načítal transaction metadata, remote tool catalog a interný provider token handle. Poisoned description odporučil priložiť „complete debug context“ a tool output obsahoval fallback instruction na vytvorenie issue.

MCP proxy prijal token s nesprávnym audience, použil vlastný broad downstream credential a issue tool dostal customer email aj rozbalený provider token. HTTP calls prešli a agent správne identifikoval provider problém, takže final-answer eval neskôr označil run ako úspešný.

## 31. First divergence

Prvý divergence nebol issue write. Nastal už pri catalog resolution: host prijal nový schema digest bez review a zachoval starý read-only classification.

Druhý divergence bol authorization: proxy nezachoval exact caller/subject/resource chain a prijal token určený pre iný resource. Exfiltration bola následok dvoch skorších trust failures, nie izolovaná chyba final toolu.

## 32. Evidence model

Vyšetrovanie potrebuje served a loaded catalog, signatures/provenance, approval envelope, token metadata, policy decisions, tool-call arguments digests, output classifications, egress logs a downstream resource history. Model transcript sám nevie preukázať loaded implementation ani effective destination.

Raw secrets sa do evidence bundle nekopírujú. Použijú sa secure references, hashes, token IDs a vault audit events, aby vyšetrovanie nevytvorilo ďalšiu exposure.

## 33. Failure hypotheses

Tool-security incident sa analyzuje od publishera po descendant sink. Najprv sa určí exact server, catalog, schema a implementation generation, pretože rovnaký názov môže reprezentovať iný behavior. Potom sa zostaví identity a authorization chain, aby sa rozlíšilo tool poisoning od deputy failure alebo cross-tenant misuse.

Ďalšia vrstva sleduje data lineage: ktoré polia vstúpili do modelu, ktoré do tool arguments, aké transformations prebehli a do ktorých sinks sa výsledok zapísal. Exfiltration môže vzniknúť cez legitímny tool, telemetry alebo error path aj bez explicitného malicious requestu.

Napokon sa porovná planned a executed chain s local registry a approval envelope. Tieto hypotézy sú zhrnutie už vysvetlených failure paths:

- **Catalog substitution** — host načítal neapproved server alebo tool generation.
- **Behavior drift** — schema ostala kompatibilná, ale destination alebo side effects sa zmenili.
- **Metadata poisoning** — description, examples alebo annotations ovplyvnili model a reviewera.
- **Output poisoning** — tool result vložil instruction alebo falošnú autoritu do ďalšieho plánu.
- **Audience confusion** — server prijal token určený pre inú resource.
- **Token passthrough** — inbound token bol preposlaný downstream namiesto separátnej delegácie.
- **Tenant binding failure** — model-generated tenant prebil trusted identity context.
- **Chain-policy gap** — jednotlivé calls boli povolené, ich kompozícia vytvorila forbidden flow.
- **Telemetry leak** — sensitive arguments alebo outputs opustili systém cez logs/traces.
- **False business success** — výsledok bol vecne správny, ale security invariant bol porušený.

Každá hypotéza sa testuje proti exact generation, policy decision a immutable destination evidence. „Model sa nechal oklamať“ nie je dostatočná root cause, ak platforma zároveň poskytla authority a exfiltration channel.

## 34. Containment

Containment odpojí konkrétny server/tool generation, zmrazí catalog refresh a zakáže affected mutation alebo export capabilities. Tokeny, handles a downstream sessions sa revokujú podľa identity graphu; pending runs prejdú do `security_reconciliation_required`.

Zachovajú sa manifests, traces s redaction policy, proxy logs, downstream audit a affected data references. Všeobecné vypnutie všetkých agentov môže byť potrebné pri neznámom blast radius, ale cieľom je presne izolovať publisher, tool, tenant, credential a sink.

## 35. Recovery

Recovery pinne known-good tool generation, opraví registry a invalidation, oddelí inbound/outbound tokens, zavedie exact audience validation, tenant binding a data-flow policy. Affected downstream records sa odstránia alebo zabezpečia podľa právnych a operational pravidiel; leaked credentials sa rotujú.

Historical runs sa nereplayujú so skutočnými side effects. Safe replay používa captured inputs, stubbed tools a deny-by-default sinks, aby overil, či nový control zastaví path pred prvým divergence.

## 36. Positive acceptance

Positive test načíta approved catalog digest, používa reviewed metadata, získa resource-bound delegated token, odošle minimal data do jediného povoleného sinku a authoritative read-back potvrdí správny tenant aj business result.

Trace obsahuje identity, policy a data-class events bez raw secretov. Descendant effects zodpovedajú manifestu a cleanup nezanechá credential ani external copy.

## 37. Forbidden acceptance

Test podstrčí tool s rovnakým názvom a novým schema digestom, malicious description, wrong-audience token, dynamic URL a output instruction na export. Host musí tool skryť alebo deny-nuť pred network side effectom.

Ďalší test vytvorí chain `read_secret` → `create_ticket`. Aj keď sú oba tools samostatne validné, policy musí kompozíciu zablokovať.

## 38. Recovery acceptance

Recovery test rotuje publisher key, invaliduje catalog cache, revokuje deputy token a odstraňuje leaked issue. Starý run nesmie po resume obnoviť quarantined tool ani cached approval.

Known-good diagnostika musí pokračovať read-only cestou a vytvoriť evidence bez citlivého exportu. Security a business outcome sa overia oddelene.

## 39. Second-operation acceptance

Nová legitímna support operation použije nový operation ID, current catalog a fresh delegated credential. Nesmie zdediť taint, tool activation, approval ani sink z incident runu.

Tým sa overí, že oprava nezablokovala celý business workflow a zároveň neobnovila standing privilege alebo hidden export path.

## 40. Praktický policy pseudocode

```python
def authorize_tool_call(run, tool, args, taint):
    manifest = registry.require_exact(
        server_id=tool.server_id,
        catalog_digest=tool.catalog_digest,
        tool_name=tool.name,
        schema_digest=tool.schema_digest,
    )

    canonical = manifest.canonicalize(args)
    caller = identity.require_attested_run(run.id)
    data_classes = classify(canonical, taint)
    destinations = manifest.resolve_destinations(canonical)

    decision = policy.evaluate(
        caller=caller,
        tenant=run.tenant,
        action=manifest.action,
        resources=manifest.resources(canonical),
        data_classes=data_classes,
        destinations=destinations,
        approval=run.current_approval,
    )
    if not decision.allowed:
        raise ToolDenied(decision.reason)

    return credential_broker.issue_handle(
        audience=manifest.server_audience,
        action=manifest.action,
        operation_id=run.operation_id,
        args_digest=sha256(canonical),
        ttl_seconds=120,
    )
```

Pseudocode ukazuje, že model-selected tool sa pred execution znovu resolvuje cez exact registry, identity, taint a destination policy. Credential vzniká až po tomto rozhodnutí a je viazaný na operation a arguments digest.

## 41. Prevádzkové metriky

Užitočné metriky zahŕňajú catalog drift denials, unknown tool generations, wrong-audience token rejects, cross-tenant argument mismatches, sensitive-source-to-external-sink blocks, dynamic tool activations, poisoned-output detections a stale-approval invalidations. Samotný počet blocked calls však nehovorí, či false negatives zostali nepovšimnuté.

Metriky sa kombinujú s adversarial evalmi, sampled manual review a downstream DLP/audit signals. Security SLO sa viaže na policy coverage, evidence completeness a containment time, nie na nulový počet alertov.

## 42. Primárne zdroje

- [Model Context Protocol — Security Best Practices](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices)
- [Model Context Protocol specification 2025-11-25 — Security and Trust & Safety](https://modelcontextprotocol.io/specification/2025-11-25)
- [Model Context Protocol — Authorization](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)
- [Model Context Protocol — Tools](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)
- [OpenAI Agents SDK — Guardrails](https://openai.github.io/openai-agents-python/guardrails/)
- [OpenAI Agents SDK — Tracing and sensitive data](https://openai.github.io/openai-agents-python/tracing/)

## 43. Zhrnutie

Tool poisoning mení agentovo rozhodovanie cez metadata, schema, output alebo implementation; confused deputy nesprávne použije vlastnú authority pre caller-a; data exfiltration presunie informáciu do nepovoleného sinku. V produkčnom incidente sa tieto tri failure classes často skladajú do jedného reťazca.

Bezpečný agentický systém pinne exact tool generation, drží local reviewed capability registry, oddeľuje inbound a downstream identity, viaže authorization na subject/resource/action, sleduje data lineage a sinky a používa deny-by-default egress. Najdôležitejšia otázka nie je „bol tool call validný?“, ale „vykonal exact reviewed tool pod správnou delegated authority iba povolenú transformáciu a neposlal žiadnu data class do nepovoleného destination alebo descendant effectu?“

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Prompt injection cez tools a retrieved content](prompt-injection-tools-retrieved-content.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->