# Prompt templates, variables a versioning

Prompt template je zdrojový program, ktorý vytvára konkrétny model input. Template, jeho variables, selected examples, output schema, model snapshot a decoding config spolu definujú behavior generation. Produkčná aplikácia preto nesmie používať prompt ako anonymný string uložený v kóde, dashboarde alebo mutable aliasi bez presnej verzie a render evidence.

V incidente `GENAI-SUPPORT-02` gateway používala prompt alias `support-latest`. Prompt editor zmenil poradie instructions, premenoval variable `policy_text` na `context` a pridal default prázdnu hodnotu. Jedna služba posielala staré variables, takže rendered prompt nemal policy dokument, ale request bol stále úspešný. Súčasne prompt cache držala staršiu prefix generation a traces logovali iba alias. Tím nedokázal určiť, ktoré requesty používali ktorú šablónu. Root cause bola mutable prompt authority bez typed variable contractu, immutable resolution a read-backu.

## 1. Template, rendered prompt a request nie sú to isté

Template je versionovaný zdroj s placeholders a control structure. Rendered prompt je konkrétny výsledok po dosadení variables, examples a optional segments. Provider request navyše pridáva message roles, tools, output format, model a inference parameters.

```text
prompt template source
+ variable schema
+ variable values
+ example set
+ locale/policy generation
→ rendered messages
+ provider serialization
+ model and decoding config
→ exact inference request
```

Hash template source neidentifikuje rendered prompt, ak sa zmenili variables. Hash rendered textu zas nevysvetľuje, z ktorej version a variables vznikol. Audit potrebuje obe identity.

## 2. Exact prompt release subject

Prompt release manifest viaže všetky behavior-relevant inputs. Template version sa nepovažuje za complete release bez model a output contractu.

```yaml
prompt_release:
  release_id: support-refund-prompt-2026.08.03.2
  template:
    name: support-refund-decision
    version: 8.1.0
    digest: sha256:template...
    source_commit: 4d91b27
  variable_schema:
    version: support-refund-vars-v5
    digest: sha256:variables-schema...
  examples:
    version: support-refund-examples-4.2.0
    digest: sha256:examples...
  output_schema:
    version: refund-decision-v3
    digest: sha256:json-schema...
  model_snapshot: support-llm-2026-07-28
  tokenizer_digest: sha256:tokenizer...
  decoding_policy: support-greedy-v2
  provider_adapter: responses-adapter-v6
  evaluation_report: eval-support-prompt-20260803
```

Mutable alias môže ukazovať na promoted release, ale runtime request uloží resolved release ID a digest. Alias je control pointer, nie execution identity.

## 3. Variables ako typed data contract

Variables nesmú byť neurčité dictionary entries bez schema. Každá variable má type, required/optional status, source, trust classification, size limit a missing-data behavior.

```yaml
variables:
  ticket_text:
    type: string
    required: true
    trust: untrusted-user-content
    max_chars: 12000
    source: support-ticket
  policy_document:
    type: object
    required: true
    trust: authoritative-reference
    fields:
      policy_id: string
      effective_from: date
      digest: string
      text: string
  customer_locale:
    type: enum
    values: [sk-SK, cs-CZ, en-GB]
    required: true
  previous_summary:
    type: string
    required: false
    trust: model-generated-context
    default: null
```

Missing required variable musí zastaviť render. Default prázdny string pre policy alebo authorization context je nebezpečný, pretože vytvorí syntakticky validný, ale semanticky neúplný prompt.

## 4. Trusted a untrusted interpolation

Najkritickejšia otázka nie je iba „bola variable escapovaná?“, ale do akej authority vrstvy bola vložená. Untrusted ticket text sa nesmie dosadiť do developer instruction vety.

Nebezpečný pattern:

```python
instruction = f"Dodržuj tieto pravidlá: {ticket_text}"
```

Bezpečnejší pattern udržiava trusted template bez používateľských placeholders a vytvorí samostatný data segment:

```python
messages = [
    {
        "role": "developer",
        "content": TRUSTED_SUPPORT_INSTRUCTIONS,
    },
    {
        "role": "user",
        "content": render_ticket_data(ticket_text),
    },
    {
        "role": "user",
        "content": render_policy_data(policy_document),
    },
]
```

Escaping chráni syntax template engine alebo delimiterov. Nezaručuje, že model nebude nasledovať prompt-like text v dátach. Trust classification, instruction wording, isolation a downstream authorization sú samostatné controls.

## 5. Strict rendering

Template engine má failnúť pri unknown alebo missing variables. Silent undefined, implicit type conversion a environment-dependent locale formatting vytvárajú nepozorovaný drift.

```python
from dataclasses import dataclass
from jinja2 import Environment, StrictUndefined, select_autoescape


env = Environment(
    undefined=StrictUndefined,
    autoescape=select_autoescape(default=True),
    trim_blocks=True,
    lstrip_blocks=True,
)

TEMPLATE = env.from_string(
    """
<policy_data policy_id="{{ policy_id }}">
{{ policy_text }}
</policy_data>
""".strip()
)

@dataclass(frozen=True)
class PolicyInput:
    policy_id: str
    policy_text: str


def render_policy(value: PolicyInput) -> str:
    if not value.policy_id or not value.policy_text:
        raise ValueError("policy_id and policy_text are required")
    return TEMPLATE.render(
        policy_id=value.policy_id,
        policy_text=value.policy_text,
    )
```

Autoescape behavior musí zodpovedať skutočnému output formátu. HTML escaping nie je univerzálny pre JSON, YAML alebo provider content parts. Pre každý format sa používa správny serializer namiesto ručného skladania.

## 6. Optional segments a branching

Prompt môže obsahovať optional history, examples alebo retrieved context. Každá branch zvyšuje počet reálnych prompt variants. Template version preto nestačí bez render manifestu.

```yaml
render_manifest:
  template_version: 8.1.0
  branches:
    include_history: true
    include_examples: false
    include_retrieval: true
    locale_variant: sk-SK
  variables_digest: sha256:variables-values...
  rendered_messages_digest: sha256:messages...
  token_count: 4821
```

Optional block sa nesmie aktivovať iba preto, že variable existuje ako empty container. Podmienka musí rozlišovať `missing`, `empty`, `invalid` a `present`. Napríklad empty retrieval result má viesť k explicitnému `no_authoritative_context`, nie k tichému odstráneniu celého grounding contractu.

## 7. Semantic versioning promptov

Prompt versions nemusia slepo kopírovať library SemVer, ale potrebujú konzistentnú change classification. Praktický model môže používať:

```text
major → zmena task contractu, output schema alebo authority boundary
minor → nové podporované cases, instructions alebo examples bez breaking variable change
patch → typo alebo vysvetlenie bez zamýšľanej behavior zmeny
```

Aj patch zmena môže reálne zmeniť model output. Version classification opisuje úmysel a compatibility, nie garantovaný behavior. Každá zmena preto prechádza evalom primeraným riziku.

Premenovanie required variable je breaking change, aj keď text promptu ostane podobný. Pridanie optional variable s bezpečným defaultom môže byť minor, ak starí klienti zostanú validní. Zmena output field name je major a musí byť koordinovaná s parserom.

## 8. Content-addressed identity

Human-readable version pomáha release managementu, no digest chráni exact content. Prompt registry uloží source, schema a artifacts pod immutable ID alebo digestom.

```text
prompt name + semantic version
→ immutable template object
→ content digest
→ promoted alias
→ runtime resolution
```

Pri read-backu aplikácia kontroluje, že version a digest zodpovedajú očakávanému release manifestu. Registry record bez content read-backu môže ukazovať na iný obsah po neautorizovanej mutation.

Ak provider podporuje stored prompt ID, optional version a variables, tieto polia sa logujú. Aplikácia stále potrebuje exact provider response metadata a vlastný release manifest, pretože model snapshot, tools alebo decoding config môžu byť mimo prompt objectu.

## 9. Prompt registry a ownership

Prompt registry nie je iba editor. Musí poskytovať immutable versions, review workflow, ownership, environment promotion, eval evidence, rollback a access control.

Prompt lifecycle:

```text
source change
→ lint and variable-schema validation
→ render snapshots
→ offline eval
→ security/privacy review
→ candidate version
→ controlled promotion
→ runtime resolution and tracing
→ monitoring
→ rollback or retirement
```

Business owner schvaľuje policy behavior, application owner compatibility a security owner trust boundaries. Jeden prompt engineer nemá sám meniť critical decision logic a production alias bez review.

Registry outage nesmie viesť k náhodnému použitiu `latest`. Runtime môže používať local immutable cache poslednej schválenej release s explicitným stale policy alebo fail closed podľa use case.

## 10. Render snapshots a golden tests

Unit test template enginea nestačí. Repository uchováva representative variable fixtures a expected rendered messages. Snapshot odhalí zmenu whitespace, delimiters, poradia alebo role mappingu.

```python
import hashlib
import json


def digest_messages(messages: list[dict[str, str]]) -> str:
    canonical = json.dumps(
        messages,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()
```

Snapshot nie je quality eval. Potvrdzuje iba render parity. Behavior eval overuje model output na datasete a security eval overuje adversarial variables.

Test fixtures nesmú obsahovať production PII. Syntetické alebo redigované examples musia zachovať relevantnú štruktúru bez citlivých údajov.

## 11. Compatibility matrix

Prompt release je kompatibilná iba s určitými modelmi, provider adapters, tool schemas a output parsers. Matrix zabraňuje tomu, aby sa nový prompt nasadil na starý parser alebo nový model dostal template optimalizovaný pre inú role semantics.

```yaml
compatibility:
  prompt_release: support-refund-prompt-2026.08.03.2
  supported_models:
    - support-llm-2026-07-28
  provider_adapters:
    - responses-adapter-v6
  output_parsers:
    - refund-decision-parser-v3
  tool_schema_generations:
    - no-tools
  minimum_context_window: 16000
```

Model alias bez snapshotu nemôže byť pevnou compatibility položkou. Ak provider neposkytuje immutable snapshot, platforma používa observed version/fingerprint a silnejšie regression evals.

## 12. Prompt cache a stale generations

Prompt caching môže ukladať shared prefix podľa provider-specific pravidiel. Cache hit nemení logický prompt, ale komplikuje incidenty pri mutable aliases a rolloutoch. Cache key musí rozlišovať prompt generation a model route.

Ak sa promoted prompt zmení, starý cache prefix nesmie byť interpretovaný ako nový release. Provider môže cache spravovať interne, preto application trace loguje cache metadata, resolved prompt version a model snapshot, nie iba očakávaný alias.

Semantic cache je odlišná vrstva: môže vrátiť starú odpoveď pre podobný input bez novej inference. Taký result potrebuje cached response generation, source request, validity horizon a policy compatibility. Prompt rollback sám semantic cache neinvalidačne neopraví.

## 13. Secrets a sensitive variables

Prompt variables môžu obsahovať PII, credentials alebo internal policy. Secret sa nemá vkladať do promptu iba preto, že model by ho „mohol potrebovať“. Tool používa scoped credential mimo model contextu a model dostane iba potrebný result.

Telemetry ukladá variable names, types, source IDs a digests podľa privacy policy. Raw values sa redigujú alebo držia v controlled evidence store s retention a access auditom.

Stored prompt registry nesmie obsahovať production secrets v source. Environment-specific secret interpolation pred provider callom je stále riziková a musí byť explicitne schválená; vo väčšine use cases je lepší tool boundary.

## 14. Deployment a canary

Prompt release sa deployuje podobne ako application artifact. Candidate sa najprv overí offline, potom shadow alebo bounded canary trafficom. Assignment je stabilný a traces obsahujú actual prompt release.

```text
candidate prompt release
→ offline eval
→ shadow comparison
→ canary segment
→ schema/security/business evidence
→ promotion
```

A/B experiment je vhodný pre user preference alebo business outcome, nie na vystavenie používateľov neoverenej safety regression. Critical constraints zostávajú hard gates.

Rollback presunie alias na known-good release, ale runtime musí read-backnúť resolved version. In-flight conversations môžu držať starú history alebo prompt ID, preto recovery test zahŕňa nový aj pokračujúci conversation scenario.

## 15. Observability

Každý request loguje prompt release ID, template version/digest, variable schema version, rendered digest, branch manifest, examples generation, model snapshot, decoding policy a output validation result. Raw prompt sa loguje iba podľa privacy policy.

Metrics používajú bounded labels ako prompt release, task a result class. Rendered digest a request ID patria do trace. Prompt alias bez resolved version sa nesmie používať ako jediný dashboard dimension.

Prompt-related failures sa rozdeľujú na render error, variable validation error, context overflow, output schema failure, policy-grounding failure, provider rejection a business failure. Spoločná metrika `prompt_success` by tieto odlišné vrstvy skryla.

## 16. Failure hypotheses a containment

Ak sa po prompt update zhorší behavior, skúma sa source diff, variable schema, actual values, branch activation, selected examples, rendered digest, provider serialization, model route, cache a output parser. Zmena template source nemusí byť first divergence; starý klient mohol poslať nekompatibilné variables.

Containment pinne known-good prompt release a model snapshot, vypne mutable aliases alebo cache, zastaví critical side effects a zachytí failing render manifests. Nemá ručne editovať prompt priamo v production UI bez vytvorenia novej immutable version.

Unknown outcome pri alias mutation sa rieši read-before-retry. Opakovaný „promote“ bez read-backu môže prepísať novšiu schválenú version.

## 17. Recovery a acceptance

Component recovery overí registry resolution, strict variable validation, renderer, provider adapter, cache key a output parser. Journey recovery vykoná representative fixtures, adversarial variable values, long context a missing-required-variable scenario. Business recovery sleduje správne support decisions a mature ticket outcomes.

Pozitívna acceptance vyžaduje immutable template a variable schema, typed trust-aware interpolation, render snapshots, compatibility matrix, eval evidence, promoted alias read-back a request-level resolved identity. Recovery acceptance zahŕňa rollback aj druhú promotion operáciu s novou patch version.

Forbidden acceptance je `support-latest` bez resolution, silent undefined variables, user text v trusted instruction placeholderi, prompt source diff bez behavior eval, cache hit ako correctness proof alebo manuálne prepísanie production promptu bez audit chainu. Prompt template je release artifact, nie textové nastavenie.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Zero-shot, one-shot a few-shot prompting](zero-one-few-shot-prompting.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
