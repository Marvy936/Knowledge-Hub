# Function calling a tool calling

Function alebo tool calling umožňuje modelu navrhnúť štruktúrované volanie externého nástroja. Model však nástroj sám osebe nevykonáva, pokiaľ platforma neposkytuje built-in execution. V každom prípade tool call zostáva návrh podliehajúci schema validation, authorization, idempotency, execution policy a result validation.

V incidente `GENAI-SUPPORT-03` model navrhol `issue_refund` s validnými JSON arguments. Dispatcher zavolal payment API bez overenia ownershipu a bez idempotency key. Response sa stratil po network timeout a celý LLM request sa zopakoval. Druhý attempt vytvoril druhú refund operation. Tím argumentoval, že „model zavolal povolený tool“, no tool availability nebola authorization a HTTP timeout nepreukazoval, že prvý side effect nenastal.

## 1. Tool-call subject

Tool execution subject zahŕňa model request, tool catalog generation, tool schema digest, selected tool, call ID, arguments, principal, authorization decision, idempotency key, target generation a execution result.

```yaml
tool_call:
  request_id: resp_1842
  call_id: call_92a
  tool_name: issue_refund
  tool_schema: support-tools-v13
  arguments_digest: sha256:8b7c...
  principal: user:4418
  authorization_policy: refund-authz-v6
  idempotency_key: refund-order-9138-v1
  target: payments-eu-prod
```

Názov toolu a arguments nestačia na bezpečný replay ani audit.

## 2. Proposal, authorization a execution

Lifecycle má explicitné boundaries:

```text
model proposes tool call
→ parse and schema validation
→ resolve principal and tenant
→ authorization and policy checks
→ business precondition read-back
→ idempotency registration
→ execute target operation
→ authoritative result read-back
→ return bounded tool result to model
→ validate final response
```

Model rozhoduje maximálne o candidate tool a candidate arguments v rámci povoleného catalogu. Authorization robí trusted application layer. Tool result sa nepovažuje za úspešný iba preto, že SDK nevyhodilo exception.

## 3. Tool catalog design

Tool catalog je API surface pre model. Každý tool potrebuje jednoznačný názov, presný description, úzky input schema a explicitný side-effect class.

```json
{
  "name": "get_refund_status",
  "description": "Read the current refund status for an order owned by the authenticated customer. Does not create or modify a refund.",
  "parameters": {
    "type": "object",
    "additionalProperties": false,
    "required": ["order_id"],
    "properties": {
      "order_id": {"type": "string", "pattern": "^ord_[0-9]+$"}
    }
  },
  "strict": true
}
```

Read a write operácie sa nezdružujú do jedného polymorfného toolu typu `manage_order(action=...)`. Úzke tools znižujú ambiguity a umožňujú rozdielne authorization a approval policies.

Tool names, descriptions a schemas sa versionujú. Zmena description môže meniť selection behavior aj bez zmeny JSON shape.

## 4. Tool choice

Provider môže podporovať modes podobné `none`, `auto`, `required` alebo forced specific tool. Tieto modes riadia model selection, nie business authorization.

`auto` je vhodné, keď text answer a tool call sú obe legitímne. `required` sa používa, keď workflow potrebuje aspoň jeden tool result, ale stále musí existovať handling pre nesprávny tool alebo invalid arguments. Forced tool znižuje selection ambiguity, no nezaručuje správne values.

Allowed-tools filter sa generuje podľa user capability, tenant, environment a workflow state. Model nemá dostať privileged tool iba s inštrukciou „nepoužívaj ho bez povolenia“.

## 5. Schema validation a semantic validation

Strict function schema znižuje malformed arguments. Aplikácia stále validuje domain semantics a authorization.

```python
def dispatch_tool(call: ToolCall, context: RequestContext) -> ToolResult:
    spec = TOOL_REGISTRY.resolve(call.name, context.catalog_generation)
    spec.validate_schema(call.arguments)

    principal = resolve_principal(context)
    authorize(principal, spec.permission, call.arguments)

    normalized = spec.normalize_arguments(call.arguments)
    validate_business_preconditions(spec, normalized, context)

    key = build_idempotency_key(context, call, normalized)
    return execute_with_readback(spec, normalized, key, context)
```

`order_id` môže byť syntakticky správny a patriť inému zákazníkovi. `amount` môže byť v rozsahu integeru a presahovať refundable balance. Tieto chyby schéma nevyrieši.

## 6. Read, compute a write tools

Tool policy klasifikuje operácie minimálne na read-only, pure compute, reversible write, irreversible write a privileged administration.

Read-only tool môže stále odhaliť sensitive data a potrebuje row-level authorization. Pure compute potrebuje resource limits. Reversible write potrebuje audit a rollback. Irreversible alebo finančný write často potrebuje human approval, step-up authentication alebo two-person rule.

Model confidence nikdy nenahrádza approval policy.

## 7. Parallel tool calls

Parallel calls sú bezpečné iba pri nezávislých operáciách. Dva reads môžu bežať paralelne. `create_customer` a `issue_invoice(customer_id)` majú dependency a vyžadujú sekvenciu.

Parallel write calls potrebujú konflikt a transaction model. Orchestrator zachová call IDs a results oddelene; nesmie zlúčiť errors do jedného textového summary.

## 8. Idempotency a unknown outcomes

Každý retriable side effect má stable idempotency key odvodený z business operation, nie z náhodného LLM attempt ID. Po timeout-e sa najprv číta authoritative target state.

```text
send write
→ timeout / connection loss
→ outcome unknown
→ query operation by idempotency key
→ return existing result alebo safely retry
```

Opätovné spustenie celého model promptu môže vyprodukovať iný call ID alebo arguments. Preto orchestration state musí zachovať už schválenú operation identity.

## 9. Tool results ako untrusted data

Tool result môže obsahovať user-generated text, retrieved document, HTML, error message alebo prompt injection. Po návrate do model contextu zostáva data, nie instruction authority.

Result wrapper obsahuje source, trust class, timestamp, truncation a schema:

```json
{
  "tool_call_id": "call_92a",
  "status": "success",
  "source": "payments-api",
  "trust": "authoritative-structured",
  "observed_at": "2026-08-03T18:42:11Z",
  "data": {
    "refund_status": "pending"
  }
}
```

Raw stack traces, credentials a internal headers sa modelu nevracajú. Error sa mapuje na bounded machine-readable class.

## 10. Error model

Tool error classes zahŕňajú invalid arguments, unauthorized, precondition failed, not found, conflict, rate limited, timeout, target unavailable a unknown outcome. Model dostane iba informácie potrebné na ďalší krok.

`unauthorized` sa nesmie preformulovať na „skús iný order ID“. `precondition failed` môže vyžiadať nový read. `unknown outcome` nesmie automaticky vyvolať nový write.

## 11. Multi-turn tool loop

Typický loop:

```text
user request
→ model tool proposal
→ application dispatch
→ tool result
→ model follow-up
→ optional next tool proposal
→ final response
```

Každé kolo má limit na počet calls, wall-clock time, token budget a side-effect budget. Loop detection sleduje opakované rovnaké arguments, alternovanie dvoch tools a calls bez nového evidence.

Final response musí vychádzať zo skutočných tool results. Modelom napísaná veta „refund bol úspešný“ bez successful authoritative read-back je forbidden.

## 12. Built-in tools, custom functions a MCP

Built-in provider tools môžu mať provider-managed execution. Custom function calls vracajú arguments aplikácii. MCP alebo iný remote tool protocol pridáva server identity, capability discovery a ďalšiu trust boundary.

Bez ohľadu na transport zostávajú rovnaké požiadavky: allowlist, versioned schema, identity, authorization, data classification, timeout, idempotency, result validation a audit.

Remote tool server nie je automaticky trusted len preto, že bol pripojený cez štandardný protokol.

## 13. Observability

Trace spája model request ID, call ID, tool name/version, argument digest, authz verdict, execution attempt, target request ID, latency a result class. Sensitive arguments sa rediguje podľa field policy, nie odstránením celej identity.

Metrics sledujú selection accuracy, invalid-argument rate, unauthorized attempts, tool errors, unknown outcomes, duplicate-prevention hits, loop rate a accepted business outcomes.

## 14. Evaluation

Eval dataset obsahuje prípady, keď model má použiť tool, nemá použiť tool, má vybrať medzi podobnými tools, má odmietnuť chýbajúce údaje a má spracovať tool error. Write tools sa testujú proti sandboxu alebo simulatoru s verifikovateľným state.

Tool selection accuracy nestačí. Journey eval overí authorization, exact side effect, read-back a final user communication.

## 15. Failure hypotheses a troubleshooting

Pri nesprávnom tool selection sa skúma catalog, descriptions, prompt, model snapshot a allowed set. Pri invalid arguments schema a domain mapping. Pri unauthorized action allowed-tools filter, principal propagation a authz enforcement. Pri duplicate write idempotency, timeout handling a read-before-retry.

Pred retry sa zachová call envelope, target request ID a observed state. Ručné prepísanie arguments bez novej attempt generation ničí audit trail.

## 16. Acceptance

Pozitívna acceptance vyžaduje versioned tool catalog, strict argument validation, server-side authorization, business preconditions, idempotent writes, authoritative read-back, bounded result injection a journey eval.

Recovery acceptance vyžaduje určenie outcome pôvodného callu, odstránenie duplicate risku, opakovanie s rovnakou business operation identity a second-operation test na inom requeste.

Forbidden acceptance je tool availability ako authorization, valid JSON arguments ako business approval, HTTP timeout ako dôkaz neúspechu alebo model-generated success text bez target read-back.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Structured Outputs a schema validation](structured-outputs-schema-validation.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Model selection a capability/cost trade-offs →](model-selection-capability-cost-tradeoffs.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
