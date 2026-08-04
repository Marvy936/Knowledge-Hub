# Prompt Registry a lifecycle

Prompt Registry je authoritative systém pre ukladanie, verzovanie, porovnávanie, testovanie, schvaľovanie a runtime resolution prompt artifacts. Nie je to iba textové pole v UI ani alias na poslednú editáciu. Produkčný prompt je zložený contract, ktorý zahŕňa template, role layout, typed variables, examples, output schema, tool catalog, model/runtime compatibility, evaluation evidence a promotion state.

V incidente `GENAI-SUPPORT-07` tím upravil alias `support-refund@production` priamo v registri počas prebiehajúceho canary. Aplikačný deployment ostal rovnaký, preto release dashboard neukázal zmenu. Nová prompt verzia používala iný variable name a predpokladala schema v6, zatiaľ čo runtime stále posielal schema v5. Časť gateway cohortu cache-ovala starý alias resolution a časť načítala nový. Rovnaký request preto dostal dve behaviorálne odlišné generácie bez jednoznačného rollback subjectu. Root cause bol mutable alias použitý ako runtime identita a chýbajúci composed release manifest.

## 1. Prompt artifact

Prompt artifact obsahuje viac než raw text. Musí zachytiť serialization, variables, constraints, examples, output contract a dependencies, ktoré menia model behavior.

```yaml
prompt_artifact:
  name: support-refund
  version: 14
  digest: sha256:6c91...
  template_format: jinja2-strict
  messages:
    - role: developer
      template: developer.md
    - role: user
      template: user.md
  variables_schema: refund-input-v4
  response_schema: refund-decision-v5
  exampleset: refund-examples-v7
  tool_catalog: support-tools-v15
  model_compatibility:
    - support-pro-2026-07-28
  commit_message: "Require current policy evidence and proposal-only output"
```

Artifact identity musí byť immutable. Zmena template, examples, variable schema alebo role order vytvára novú verziu alebo nový digest. Editácia existujúcej verzie ničí reprodukovateľnosť evalov a incidentov.

## 2. Registry identity

Registry typicky používa meno, verziu a alias. Meno identifikuje prompt family, verzia immutable artifact a alias mutable promotion pointer.

```text
prompt family
≠ immutable version
≠ content digest
≠ environment alias
≠ rendered prompt instance
```

Runtime trace loguje resolved immutable version a digest, nie iba alias. Alias `production` hovorí, ktorý artifact bol vybraný podľa control-plane state; nepreukazuje, že všetky runtime instances ho načítali ani že konkrétny request použil rovnakú resolution.

## 3. Authoring source

Prompt source môže byť registry UI, Git repository alebo API. Organizácia musí určiť single-writer alebo jasný synchronization contract. Ak UI a Git môžu nezávisle meniť ten istý prompt, vzniká split-brain authority.

Git-first model používa code review a CI na vytvorenie registry version. Registry-first model používa registry audit log a export do source control. V oboch prípadoch musí byť jednoznačné, ktorý systém je authoritative pre text, metadata a promotion aliases.

## 4. Template a typed variables

Prompt variables majú schema, typ, required/optional semantics, allowed length a trust classification. String interpolation bez escaping môže zmiešať trusted instructions s untrusted user alebo retrieved content.

```json
{
  "$id": "refund-input-v4",
  "type": "object",
  "required": ["case_id", "customer_request", "policy_evidence"],
  "properties": {
    "case_id": {"type": "string", "pattern": "^CASE-[0-9]+$"},
    "customer_request": {"type": "string", "maxLength": 12000},
    "policy_evidence": {
      "type": "array",
      "items": {"$ref": "policy-evidence-v3"}
    }
  },
  "additionalProperties": false
}
```

Registry validuje template proti variable schema a poskytuje strict render. Missing variable, unknown variable alebo invalid type musí zlyhať pred model callom. Silent empty string alebo implicitný `str(object)` môže meniť prompt semantics bez zjavnej chyby.

## 5. Rendered prompt instance

Immutable template sa pri requeste spojí s konkrétnymi variables, examples, retrieved context a tool/schema serialization. Rendered instance je execution artifact a má vlastný digest, pretože dve requesty s rovnakou prompt version môžu mať odlišný context.

```text
prompt version
+ variable values
+ selected examples
+ retrieval context
+ tool schemas
+ response schema
→ rendered prompt instance digest
```

Sensitive values sa nemusia ukladať v plaintext. Trace môže uchovať redacted representation, content hashes, source IDs a secure reference tak, aby bolo možné potvrdiť lineage bez zbytočného retentionu osobných údajov.

## 6. Role a message layout

Prompt version musí zachytiť role order a message boundaries. Presun textu z user do developer role alebo spojenie viacerých messages do jedného stringu môže zmeniť instruction hierarchy a provider behavior.

Registry preto neukladá iba concatenated preview. Ukladá structured message array a provider-neutral semantic representation, pričom provider adapter má vlastnú verziu. Render preview je diagnostický artifact, nie jediný source of truth.

## 7. Examples ako dependency

Few-shot examples môžu byť embedded priamo v prompt version alebo referencované immutable examplesetom. Dynamic example selection pridáva selector version, embedding/index generation a candidate IDs.

```yaml
examples:
  mode: dynamic
  set: refund-examples-v7
  selector: semantic-selector-v4
  max_examples: 4
  exclusion_policy: no-same-case-or-customer
```

Zmena examples môže zmeniť label pri nezmenenom template texte. Promotion gate preto hodnotí composed prompt release, nie iba text diff.

## 8. Response schema a tools

Structured output schema a tool definitions sú prompt dependencies, pretože provider ich serializuje do model contextu alebo instruction layer. Prompt, ktorý odkazuje na field `approved_amount`, nie je kompatibilný so schema, ktorá ho premenovala na `proposed_amount`.

Registry môže ukladať schema/tool reference alebo immutable snapshot. Reference sa pri release resolution pinne na konkrétny digest. Mutable `latest` dependency je forbidden v production manifestoch.

## 9. Model compatibility

Prompt version má declared a tested model compatibility. Prompt optimalizovaný pre jednu model family môže na inom modeli reagovať odlišne na verbosity, examples, tool descriptions alebo reasoning controls.

```yaml
compatibility:
  tested:
    - model: support-pro-2026-07-28
      api_profile: responses-v2
      result: passed
    - model: support-mini-2026-07-20
      api_profile: responses-v2
      result: failed-tool-selection
```

Declared compatibility bez eval evidence je návrhový intent. Runtime route smie vybrať iba kombináciu prompt/model/schema/tools, ktorá prešla minimálnym contract gate.

## 10. Version creation

Nová verzia vzniká explicitnou operáciou s author identity, source commit, commit message a change reason. Registry vypočíta digest a zamkne immutable fields.

```python
release = register_prompt(
    name="support-refund",
    template=template,
    variables_schema="refund-input-v4",
    response_schema="refund-decision-v5",
    metadata={
        "source_commit": "9d2a7f1",
        "ticket": "SUP-1842",
        "author": "team-support-ai",
    },
)
print(release.version, release.digest)
```

Retry po unknown create outcome používa idempotency key alebo read-back podľa source commit/digest. Slepé opakovanie môže vytvoriť dve verzie s rovnakým obsahom a nejednoznačným promotion history.

## 11. Diff a review

Prompt review potrebuje semantic diff, nie iba line diff. Kontroluje role changes, variable additions, trust boundary, examples, output schema, tool references, model parameters a changed success criteria.

Reviewer musí rozumieť workload domain a security implications. Grammatická úprava môže zmeniť refusal alebo authority semantics; naopak veľký formatting diff môže byť behaviorálne neutrálny. Review verdict je hypothesis, ktorú potvrdzuje eval.

## 12. Branches a candidate aliases

Vývoj môže používať immutable versions a aliases ako `dev`, `candidate` alebo `production`. Alias je pointer s audit history a optimistic concurrency control.

```yaml
alias_update:
  alias: candidate
  expected_current_version: 13
  new_version: 14
  evidence_bundle: eval-support-refund-2026-08-04
```

Compare-and-swap chráni pred tým, aby dva tímy ticho prepísali rovnaký alias. Alias update bez expected state môže zmazať novšiu promotion operáciu.

## 13. Promotion state machine

Prompt lifecycle používa explicitné stavy. Príkladom je draft, validated, candidate, canary, production, deprecated a retired.

```text
draft
→ static validated
→ offline evaluated
→ approved candidate
→ shadow/canary
→ production
→ deprecated
→ retired
```

Prechod má guard conditions a evidence. Registry UI, ktoré dovolí priamo označiť draft ako production bez eval a approval policy, je slabý control plane.

## 14. Evaluation gate

Každý candidate sa testuje na versioned dataset a grader bundle. Gate hodnotí target metrics aj forbidden regressions, napríklad schema validity, unsupported claims, tool misuse, privacy a latency/cost.

```yaml
promotion_gate:
  dataset: support-refund-eval-v12
  grader_bundle: refund-graders-v9
  thresholds:
    policy_correctness: ">= 0.94"
    schema_validity: "= 1.0"
    unsupported_approval_rate: "= 0"
    p95_cost_eur: "<= 0.09"
  comparison:
    baseline_prompt: support-refund-v13
```

Aggregate score nesmie kompenzovať hard safety failure. Multi-metric formula môže slúžiť na ranking, ale forbidden conditions zostávajú samostatné gates.

## 15. Baseline a paired comparison

Candidate sa porovnáva s aktuálnou production version na rovnakých cases, modeli, context generation a inference profile. Paired comparison znižuje noise a ukazuje, ktoré konkrétne cases sa zlepšili alebo zhoršili.

Prompt A/B comparison bez pinned modelu alebo retrieval corpusu nie je izolovaný experiment. Zmena viacerých dependencies naraz môže byť legitímny composed release, ale attribution sa potom robí ablationmi, nie tvrdením, že zlepšenie spôsobil samotný text.

## 16. Human approval

High-risk prompt promotion môže vyžadovať domain ownera, security alebo legal approvera. Approval sa viaže na exact artifact digest a evidence bundle, nie na prompt name alebo screenshot.

Ak sa po approval zmení template, schema, examples alebo model compatibility, approval sa invaliduje. Registry musí zabrániť „approve then edit“ patternu tým, že version je immutable.

## 17. Release manifest

Production application nepoužíva prompt alias ako jedinú release identitu. Build alebo deployment vytvorí composed manifest so resolved immutable dependencies.

```yaml
llm_release: support-assistant-2026.08.04.3
application_image: sha256:bb82...
route_policy: support-route-v18
model_snapshot: support-pro-2026-07-28
prompt:
  name: support-refund
  version: 14
  digest: sha256:6c91...
exampleset: refund-examples-v7
response_schema: refund-decision-v5
tool_catalog: support-tools-v15
eval_bundle: eval-support-refund-2026-08-04
```

Manifest je rollback a incident subject. Alias môže byť convenience pointer pri deployment resolution, ale runtime používa resolved version alebo loguje resolved identity pri každom requeste.

## 18. Runtime resolution

Aplikácia môže načítať prompt pri build time, startup alebo per request. Každý model má trade-off medzi consistency a dynamikou.

Build-time pinning dáva najsilnejšiu reproducibility, ale prompt change vyžaduje nový artifact/deployment. Startup resolution umožňuje prompt promotion bez rebuild, no rôzne instances môžu načítať odlišnú version počas rolloutu. Per-request alias resolution zvyšuje control-plane dependency a môže meniť behavior medzi dvoma requestmi tej istej session.

## 19. Local cache

Runtime často cache-uje prompt artifacts. Cache key je immutable name/version/digest, nie alias. Alias cache má krátky TTL alebo explicit invalidation a runtime stále zaznamenáva resolved version.

Po promotion sa loaded-generation read-back vykoná na každom cohort. Registry alias state nepreukazuje, že aplikácia zahodila starý cache entry alebo načítala nový artifact.

## 20. Canary a stable assignment

Prompt canary používa stabilnú assignment jednotku, napríklad tenant, user alebo case. Jeden conversation alebo case nesmie počas journey preskakovať medzi prompt versions, ak by sa tým zmenila policy alebo output contract.

Canary telemetry spája prompt version s model, retrieval, tools, validation a business outcomes. Instant feedback ako thumbs-up nestačí pri workflow, kde sa refund correctness potvrdí až neskôr.

## 21. Rollback

Rollback znamená presun production route na known-good immutable prompt release alebo celý composed manifest. Nie je to ručná editácia aktuálneho textu, ktorá vytvorí tretí neidentifikovaný stav.

```text
incident detected
→ freeze failing version and evidence
→ move production alias by compare-and-swap
→ verify alias state
→ verify loaded runtime generation
→ replay incident cases
→ verify second operation
```

Ak candidate zmenil schema alebo tool contract, samotný prompt rollback nemusí byť compatible s novším application code. Rollback plan sa preto testuje na full release graph.

## 22. Deprecation a retirement

Staré prompt versions môžu zostať potrebné na incident replay a audit. Deprecation znamená, že sa nesmú použiť pre nové production releases; retirement môže obmedziť runtime access, ale lineage metadata a digest ostávajú zachované podľa retention policy.

Sensitive prompts alebo embedded examples môžu obsahovať proprietary či personal data. Registry retention, encryption, access control a deletion workflow musia byť explicitné a zosúladené s audit requirements.

## 23. Access control

Registry oddeľuje read, author, version-create, alias-promote, deprecate a admin permissions. Runtime workload potrebuje read iba pre approved prompt scope, nie právo vytvárať verzie alebo presúvať production alias.

Tenant-specific prompts vyžadujú namespace isolation. Prompt list alebo diff môže sám obsahovať citlivé obchodné pravidlá, preto metadata endpoints nie sú automaticky verejné pre všetkých developerov.

## 24. Secrets a sensitive data

Secrets sa neukladajú priamo do prompt template. Prompt môže referencovať runtime capability alebo placeholder, ale secret injection sa vykonáva mimo model contextu, ak model hodnotu nepotrebuje.

Sensitive examples a test cases sa redigujú alebo ukladajú v chránenom dataset store. Registry preview a audit log nesmú neúmyselne kopírovať osobné údaje do dlhodobej telemetry.

## 25. Lineage

Registry spája prompt version so source commitom, authorom, eval runs, approvals, release manifests a runtime traces. Lineage umožňuje odpovedať, ktoré production requests použili chybnú verziu a ktoré downstream outcomes treba prehodnotiť.

```text
source change
→ prompt version
→ eval bundle
→ approval
→ alias transition
→ release manifest
→ runtime request
→ business outcome
```

## 26. Observability

Runtime trace loguje prompt name, immutable version, digest, rendered instance digest, variable schema, exampleset, model, route a validation verdict. Registry audit log zaznamenáva version creation, alias changes, approvals, deprecations a access events.

Metrics sa segmentujú podľa prompt version a workload facet. Aggregate product score môže zakryť, že candidate zlyháva iba pri jednom jazyku, tenant policy alebo long-context variante.

## 27. Drift a out-of-band changes

Periodický reconciler porovná registry aliases, desired release manifests a loaded runtime generations. Out-of-band alias change vytvára drift alert a môže byť automaticky vrátený alebo zablokovaný podľa ownership policy.

Registry availability alebo UI success nepreukazuje, že prompt bol correctly rendered. Synthetic runtime probe môže overiť exact version resolution a minimal schema behavior bez vykonania business side effectu.

## 28. Failure hypotheses

Pri náhlom prompt regressione sa skúma wrong alias resolution, stale runtime cache, variable schema mismatch, role serialization change, example selection drift, model incompatibility, schema/tool dependency mismatch, hidden out-of-band edit alebo eval leakage. Každá hypotéza má odlišný read-back.

Ak iba časť pods zlyháva, pravdepodobný je loaded-version split alebo cache; samotný template text by zasiahol všetky cohorts. Ak offline eval prešiel, ale production zlyháva iba s real retrieval contextom, treba skúmať context assembly a variable distribution, nie automaticky meniť instruction wording.

## 29. Containment

Containment zastaví ďalšiu promotion, pinne runtime na known-good immutable version a zachová failing prompt, rendered digests, variables lineage a affected request IDs. Neodstraňuje chybnú version z registry, pretože by sa stratilo RCA evidence.

Pri security incidente sa zruší runtime access k citlivému promptu, rotujú relevantné credentials a preskúma audit log. Alias rollback sám neodstráni uniknuté data z logs, caches alebo eval artifacts.

## 30. Recovery

Recovery obnoví known-good composed release, overí alias aj loaded runtime version, spustí paired replay a bounded canary. Opravený candidate dostane novú immutable version; pôvodný artifact sa nemení.

Druhá operácia testuje odlišný variable branch, tenant alebo model route. Úspešný pôvodný example nestačí na potvrdenie, že schema evolution, cache invalidation a fallback compatibility sú obnovené.

## 31. Acceptance

Pozitívna acceptance vyžaduje immutable prompt versions, typed variables, pinned dependencies, semantic diff a review, reproducible eval bundle, controlled aliases, full release manifest, loaded-version read-back, access control, lineage a outcome telemetry.

Recovery acceptance vyžaduje exact failing version, preserved rendered evidence, compare-and-swap rollback, runtime generation verification, incident replay, fresh candidate version a druhú odlišnú journey.

Forbidden acceptance je mutable prompt text pod rovnakou verziou, production alias ako jediná runtime identita, screenshot approval, prompt-only rollback pri incompatible schema/tools, UI save success ako serving evidence alebo offline aggregate score bez hard regression gates.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: LLM gateways, routing, fallback a rate limiting](llm-gateways-routing-fallback-rate-limiting.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->