# Structured Outputs a schema validation

Structured output je mechanizmus, ktorým aplikácia žiada model o výstup zodpovedajúci explicitnej schéme. Jeho cieľom je odstrániť parser ambiguity a stabilizovať interface medzi modelom a kódom. Schéma však garantuje iba určitú formu. Negarantuje pravdivosť, domain correctness, authorization ani úspešný downstream side effect.

V incidente `GENAI-SUPPORT-03` model vrátil JSON, ktorý prešiel syntaktickým parserom aj strict schema validation. Pole `refund_amount` však obsahovalo správny dátový typ a nesprávnu menu; `eligible` bolo `true`, hoci policy vyžadovala human approval; a response bol po truncation označený ako completed. Tím označil request ako „validated“, pretože JSON sedel so schémou. Root cause bola zámena syntax, structure, semantics a business acceptance.

## 1. Output contract ako versioned subject

Structured-output subject obsahuje model snapshot, prompt release, schema ID a digest, strictness mode, serializer, decoder configuration a downstream consumer version.

```yaml
output_contract:
  schema_id: refund-decision
  schema_version: 4.2.0
  schema_digest: sha256:4a1f...
  strict: true
  consumer_version: refund-worker-12
  model_snapshot: provider/model-2026-07-15
  prompt_release: refund-structured-v9
```

Názov schémy bez version alebo digestu nestačí. Mutable schema alias môže spôsobiť, že rovnaký application release generuje odlišné payloads.

## 2. JSON text, JSON mode a Structured Outputs

Plain text s inštrukciou „vráť JSON“ nemá enforceovaný contract. Model môže pridať Markdown fence, komentár alebo neplatnú syntax.

JSON mode typicky garantuje syntakticky platný JSON, ale nie konkrétne required fields, enum values alebo nesting.

Structured Outputs používajú explicitnú JSON Schema alebo ekvivalentný typed contract a pri strict režime obmedzujú output na podporovaný subset schémy. Provider support, podporované keywords a behavior pri refusal alebo incomplete response sa musia overiť pre pinned model a API version.

```text
plain JSON request
→ best-effort formatting

JSON mode
→ syntakticky platný JSON

strict structured output
→ schema-conformant output v podporovanom subsete

application acceptance
→ structural + semantic + policy + authority validation
```

Posledný krok zostáva zodpovednosťou aplikácie.

## 3. Návrh schémy

Schéma má reprezentovať domain contract, nie iba aktuálny shape jedného happy-path outputu. Required fields musia byť skutočne povinné. Enum sa používa tam, kde consumer pozná uzavretú množinu hodnôt. `additionalProperties: false` bráni tichému prijatiu neznámych polí, ak provider subset túto vlastnosť podporuje.

```json
{
  "$id": "refund-decision-v4",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "decision",
    "reason_code",
    "currency",
    "amount_minor",
    "evidence_ids"
  ],
  "properties": {
    "decision": {
      "type": "string",
      "enum": ["approve", "deny", "human_review"]
    },
    "reason_code": {
      "type": "string",
      "enum": ["POLICY_OK", "OUT_OF_WINDOW", "MISSING_EVIDENCE"]
    },
    "currency": {
      "type": "string",
      "pattern": "^[A-Z]{3}$"
    },
    "amount_minor": {
      "type": "integer",
      "minimum": 0
    },
    "evidence_ids": {
      "type": "array",
      "items": {"type": "string"},
      "minItems": 1
    }
  }
}
```

Schéma nepovie, či `amount_minor` zodpovedá authoritative order recordu ani či evidence IDs existujú. To rieši semantic validator.

## 4. Structural a semantic validation

Validation pipeline má oddelené fázy:

```text
response status
→ decode JSON
→ validate schema
→ validate domain invariants
→ read-back referenced authority
→ evaluate policy
→ authorize action
```

Domain invariants môžu kontrolovať menu, rozsah, vzájomné závislosti polí a povolené state transitions. Authority validation načíta order, policy alebo account state z authoritative systemu.

```python
def validate_refund_decision(payload: dict, order: Order) -> None:
    validate_json_schema(payload, REFUND_SCHEMA)

    if payload["currency"] != order.currency:
        raise SemanticValidationError("currency mismatch")

    if payload["amount_minor"] > order.refundable_amount_minor:
        raise SemanticValidationError("amount exceeds refundable balance")

    if payload["decision"] == "approve" and order.requires_human_review:
        raise PolicyValidationError("manual approval required")

    validate_evidence_ids(payload["evidence_ids"], order)
```

Model output je candidate decision. Až tieto kontroly môžu vytvoriť accepted decision artifact.

## 5. Refusal, incomplete a transport states

Aplikácia nesmie predpokladať, že každý successful HTTP response obsahuje domain payload. Model môže odmietnuť request, response môže byť incomplete pre token limit, tool call môže nahradiť text output alebo streaming sa môže prerušiť.

Response envelope sa validuje pred domain payloadom:

```json
{
  "status": "completed",
  "finish_reason": "stop",
  "refusal": null,
  "output_contract": "refund-decision-v4",
  "payload": {}
}
```

`completed` na provider envelope stále nie je business acceptance. `incomplete`, refusal alebo missing payload sa klasifikujú osobitne a nesmú sa mapovať na deny/approve default.

## 6. Nullable, optional a missing

`null`, chýbajúce pole a prázdny string majú rozdielny význam. Ak consumer potrebuje rozlíšiť „neznáme“, „neaplikovateľné“ a „neposkytnuté“, schéma to musí vyjadriť explicitne.

Príliš veľa optional fields vytvára weak contract. Model môže vynechať rozhodujúce informácie a payload stále prejde. Naopak, povinné pole, ktoré sa nedá vždy zistiť, môže model motivovať k fabrication. V takom prípade sa pridá explicitný `status: unknown` alebo discriminated union.

## 7. Discriminated variants

Rôzne outcome classes majú často odlišné required fields. Jeden plochý object s desiatkami nullable fields je ťažko validovateľný.

```json
{
  "oneOf": [
    {
      "type": "object",
      "required": ["kind", "answer", "evidence_ids"],
      "properties": {
        "kind": {"const": "answer"},
        "answer": {"type": "string"},
        "evidence_ids": {"type": "array", "items": {"type": "string"}}
      }
    },
    {
      "type": "object",
      "required": ["kind", "reason_code"],
      "properties": {
        "kind": {"const": "human_review"},
        "reason_code": {"type": "string"}
      }
    }
  ]
}
```

Provider nemusí podporovať celý JSON Schema vocabulary. Contract sa preto testuje proti konkrétnemu API/model snapshotu a unsupported constructs sa zjednodušia bez straty domain semantics.

## 8. Repair a retry

Automatic repair smie opravovať iba syntaktické alebo bezpečne odvodené štrukturálne chyby. Nesmie vymýšľať chýbajúci business fact.

Ak schema validation zlyhá, retry zachová pôvodný input, schema version a failure detail. Ak sa zmení prompt alebo model, vzniká nový attempt generation.

```text
invalid JSON
→ parser-safe repair alebo retry

schema mismatch
→ constrained retry s exact validation error

semantic mismatch
→ retrieve/compute authoritative fact alebo escalate

policy failure
→ nikdy nežiadať model, aby policy obišiel
```

Nekonečný „self-healing“ loop je forbidden. Retry count, cost a failure class sa limitujú.

## 9. Streaming

Streaming structured output môže poskytovať partial JSON fragments, ktoré ešte nie sú validným documentom. Consumer nesmie vykonať side effect z prvého objaveného field-u. Bufferuje sa celý logical object alebo sa používa incremental parser s explicitným commit markerom.

Cancellation alebo network loss môže zanechať partial payload. Tento stav je `incomplete`, nie prázdny validný object.

## 10. Schema evolution

Schema versioning používa compatibility rules podobné API contracts. Pridanie optional field-u môže byť backward-compatible pre tolerant consumer, ale nie pri `additionalProperties: false`. Zmena enum, required field-u, type alebo semantics je breaking change.

Producer a consumer compatibility matrix patrí do release evidence:

```yaml
producer_model_release: support-model-v18
schema: refund-decision-v4.2
consumers:
  refund-worker-12: compatible
  analytics-exporter-7: compatible
  legacy-worker-9: incompatible
```

Migration používa dual-read alebo dual-write, shadow parsing a replay evals. Mutable `latest` schema sa nepoužíva ako jediná production identity.

## 11. Security boundary

Structured schema nezabraňuje prompt injection, data exfiltration ani unauthorized instructions. String field môže obsahovať malicious text, URL alebo SQL fragment, ktorý downstream systém nebezpečne interpretuje.

Každé field má trust classification a sink-specific encoding. Tool argument `path`, `query` alebo `recipient` sa validuje allowlistom a authorization policy. Schéma je iba jedna vrstva defense-in-depth.

## 12. Evaluation a observability

Telemetry rozlišuje parse failure, schema failure, semantic failure, policy rejection, refusal, incomplete output a consumer error. Jedna metrika `structured_success` tieto triedy zlieva a skrýva root cause.

Eval dataset obsahuje happy paths, missing evidence, conflicting data, adversarial text, oversized input, refusal-worthy request a schema migration cases. Meria sa contract adherence aj domain correctness.

## 13. Failure hypotheses a troubleshooting

Ak payload neprejde parserom, skúma sa provider mode, truncation, streaming assembly a model compatibility. Ak prejde schema, ale zlyhá domain validator, skúma sa prompt grounding, stale evidence a schema gap. Ak consumer zlyhá po schema migration, skúma sa compatibility matrix a rollout generation.

Pred retry sa zachová raw provider envelope, request ID, schema digest, model snapshot a finish reason. Prepísanie payloadu v logu „opravenou“ verziou ničí forensic evidence.

## 14. Acceptance

Pozitívna acceptance vyžaduje pinned schema a model support, strict structural validation, semantic/domain validation, authority read-back, refusal/incomplete handling, safe schema evolution a telemetry podľa failure class.

Recovery acceptance vyžaduje reprodukovanie pôvodného invalid subjectu, opravu konkrétnej contract alebo semantic vrstvy, replay eval a second-operation test s kompatibilným consumerom.

Forbidden acceptance je „valid JSON“ ako dôkaz correctness, schema-conformant amount bez authority read-back, default approve/deny pri incomplete response alebo model-generated fields odoslané priamo do privileged sinku.
