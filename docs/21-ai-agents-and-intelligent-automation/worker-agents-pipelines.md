# Worker Agents v pipelines

Worker Agent je riadená agentická capability vložená do pipeline execution. Jeho bezpečnosť závisí od immutable catalog generation, pinned image a model, typed inputs a outputs, scoped tokenov, MCP boundaries, deterministic gates a explicitných retry a reconciliation semantics.

V incidente `AGENT-HARNESS-11` pipeline referencovala mutable agent definition, broad hosted MCP connector a output `RISK_LEVEL`, ktorého missing hodnota bola downstream logikou interpretovaná ako low risk. Step bol zelený, hoci intended resource mutation nebola potvrdená.

Nosný lifecycle tejto kapitoly je:

```text
agent use case a risk class
→ immutable catalog definition a version
→ pinned image, instructions, model a MCP connectors
→ authenticated trigger a typed inputs
→ scoped runtime token a bounded tool loop
→ schema-valid evidence a declared outputs
→ deterministic downstream policy alebo approval
→ business read-back
→ cancellation, reconciliation, rollback a second-run acceptance
```

## 1. Worker Agent definition

Worker Agent je reusable catalog entity, ktorá spája instructions, model connector, optional MCP connectors, typed inputs, runtime environment a outputs. Pipeline Agent step referencuje definíciu podľa name a version, preto prompt nemá byť ad hoc duplikovaný v každej pipeline.

Bez explicitnej version vzniká mutable dependency: rovnaká pipeline môže zajtra vykonať iný agent behavior bez zmeny pipeline YAML.

## 2. Execution subject

Exact execution subject obsahuje pipeline identifier a generation, execution ID, stage/step, agent name/version, container image digest, instructions digest, model connector a model name, MCP server set, typed inputs, environment settings, scoped token a trigger payload digest.

Táto identita sa uloží pred prvým model callom. Incident bez nej nemožno reprodukovať, ak catalog alebo managed connector medzičasom zmení effective configuration.

## 3. Containerized step

Worker Agent beží ako containerized pipeline step a zdieľa pipeline scheduling, timeout, failure strategy a log lifecycle. Agent autonomy nemení fakt, že ide o step s bounded resources.

Container image sa pinne digestom. Tag `latest` je vhodný iba na discovery, nie na production acceptance, pretože mení runtime bez diffu v agent definition.

## 4. Instructions authority

Instructions field je system prompt centrálne uložený v agent definition. Pipeline má agent parameterizovať cez inputs alebo Agent Settings, nie prepísať prompt neauditovaným runtime textom.

Instructions popisujú task, allowed tools, output contract, stop conditions a refusal behavior. Security identity a permissions sa do nich nevkladajú ako textová dôvera.

## 5. Harness expressions

Instructions môžu používať expressions z triggera, pipeline, stage alebo service contextu. Každá expression má expected type, source a missing-value semantics.

PR title, branch alebo commit message sú untrusted data. Vkladajú sa do jasne označenej data sekcie, aby nemohli zmeniť system instructions alebo tool policy.

## 6. Typed inputs

Worker Agent inputs podporujú definované types, napríklad string, connector a array. Requiredness a defaults sa validujú pred spustením containeru.

Type validation nestačí pre business constraints. Repo name, environment alebo plan file potrebuje allowlist, scope a existence check; connector input potrebuje type a permission verification.

## 7. Model connector

Model connector určuje provider a default model. Worker Agent môže používať direct provider, Bedrock alebo Harness-managed connector podľa konfigurácie a permissions.

Manifest ukladá connector identifier, resolved model a provider route. Alias `latest` alebo model override bez eval evidence je drift.

## 8. Managed connector

Harness-managed connectors môžu byť account-level a view-only, pričom Worker Agent k LLM Gateway potrebuje scoped permission. Managed convenience neodstraňuje need-to-know a data-classification review.

Explicit agent permission block musí zachovať iba potrebné permissions. Odstránenie implicitnej gateway permission sa prejaví ako authorization failure, nie dôvod na pridanie broad admin scope.

## 9. MCP connectors

MCP connectors dávajú agentovi real-time access k Harness alebo external services. Každý connector viaže server URL, authentication, allowed operations a trust classification.

Hosted Harness MCP je vhodný pre platform data, ale capability scope sa stále obmedzuje scoped tokenom. Custom server sa považuje za samostatný supply-chain a authorization boundary.

## 10. GitHub compatibility boundary

Aktuálna Harness dokumentácia rozlišuje GitHub MCP connector určený pre AI Chat od Worker Agent compatibility. Worker Agent nemá predpokladať, že connector z catalogu funguje v každom AI surface.

Compatibility sa overí pri promotion a zapíše do manifestu. Workaround cez custom MCP endpoint musí mať vlastný security review.

## 11. Scoped token

Worker Agent potrebuje Harness identity s minimálnymi permissions pre resources, ktoré má čítať alebo meniť. Token audience, account/org/project scope a expiration sa viažu na execution.

Shared account-wide API key v env var je anti-pattern. Leak by umožnil inému agentovi alebo custom toolu prekročiť pipeline boundary.

## 12. Agent Settings

Agent Settings mapujú key-value pairs na runtime environment variables step-u. Sú vhodné na pipeline-specific context, ale môžu niesť untrusted alebo sensitive values.

Secrets používajú secret expressions; plain values sa redigujú podľa policy. Neznámy key alebo override security-critical settingu sa odmietne schema gateom.

## 13. Trigger context

Worker Agent pipelines môžu používať webhook, artifact, manifest alebo scheduled triggers. Trigger payload sa autentifikuje a jeho repo, branch, PR a commit values sa validujú proti connector authority.

Replay alebo duplicate trigger musí mapovať na stable operation identity. Agent execution retry nesmie vytvoriť nový business mutation key.

## 14. PR-triggered agents

Pri code review alebo remediation sa pinne head commit a base commit. Agent nesmie aplikovať fix na novší branch bez rebase a opätovnej validácie.

Output a comments uvádzajú analyzed SHA. Ak branch postúpi, result je stale advisory, nie merge-ready proof.

## 15. Tool loop

Worker Agent vykonáva multi-turn model/tool loop. Max turns, tool count, wall time a mutation count sú explicitné budgets.

Tool loop sa zastaví pri repeated identical call, policy deny, missing evidence alebo unknown side effect. Vyčerpanie budgetu vráti typed incomplete outcome.

## 16. Read, draft a commit modes

Agent tools sa delia na read-only discovery, draft/proposal a commit/mutation. Default production agent používa read alebo draft; commit capability sa pridáva iba s policy a approval boundary.

Rovnaký natural-language task sa testuje v každom mode. Model nesmie obísť deny použitím generic MCP create toolu.

## 17. Outputs

Worker Agent môže zapisovať key-value outputs do Harness output file a deklarovať aliases, ktoré downstream steps referencujú. Každý output má type, allowed values, requiredness a producer generation.

Textový `RISK_LEVEL=LOW` bez schema a provenance nesmie automaticky otvoriť deployment gate. Missing output je error alebo unknown, nikdy implicitný low risk.

## 18. Structured evidence output

Okrem short gate variables agent publikuje evidence artifact s findings, sources, analyzed commit, tool calls, uncertainty a recommended action. Artifact sa ukladá v chránenom store.

Downstream policy overí digest a schema. LLM prose sa neparsuje regexom na security decision.

## 19. Downstream gates

Agent output môže vstúpiť do approval, conditional logic alebo notification. Gate musí byť deterministic a fail-closed pri missing, malformed alebo stale outpute.

High-impact action vyžaduje independent signal, napríklad scanner result alebo human approval. Agent self-assessment nie je sole authorization.

## 20. Pipeline failure strategy

Step failure, timeout, cancellation a partial output majú explicitné semantics. Retry je bezpečný len pre idempotent read alebo draft operations.

Ak agent mohol vykonať mutation pred timeoutom, execution sa označí unknown a spustí reconciliation. Automatický retry celého trajectory je zakázaný.

## 21. Concurrency

Viaceré executions môžu analyzovať ten istý PR alebo meniť ten istý resource. Lock alebo optimistic generation check zabráni lost update a conflicting fixes.

Concurrency key zahŕňa repo/resource a target generation. Newer execution môže supersede older advisory, ale nesmie zmazať jeho audit evidence.

## 22. Resource limits

Container má CPU, memory, filesystem, network, token a duration limits. Large repository alebo log input sa chunkuje a používa bounded context selection.

OOM alebo eviction sa rozlišuje od model failure. Temp artifacts a cloned code sa po execution odstránia podľa retention policy.

## 23. Network boundary

Agent container komunikuje iba s model endpointom, approved MCP servers, Harness APIs a explicitnými repository endpoints. Egress policy blokuje metadata, internal admin a arbitrary internet destinations.

Custom dependencies v image rozširujú attack surface. SBOM, signatures a vulnerability scanning sú súčasťou image acceptance.

## 24. Secrets

Secrets sa injektujú runtime expressions a nikdy sa neobjavujú v instructions, output alebo model prompt-e, pokiaľ to nie je explicitne potrebné a schválené. Preferujú sa short-lived tokens.

Redaction sa testuje pri error, debug logu, tool result a model refusal. Secret exposure incident invaliduje credentials, nie iba log line.

## 25. Catalog governance

Catalog rozlišuje system-provided a custom agents, ownera, version, description, allowed stages, permissions a deprecation state. Discovery metadata nesmie sľubovať capability, ktorú current version nemá.

Promotion vyžaduje review agent YAML, image digest, instructions, inputs, outputs, connectors a tests. Edit existujúcej version sa zakáže; vytvorí sa nová generation.

## 26. Agent YAML

YAML je authoritative declarative representation agent definition. Review zachytí image, max turns, task, model connector, MCP servers, inputs, outputs a permission blocks.

Generated YAML z AI Chat alebo MCP create-agent toolu prechádza rovnakou policy a code review ako manuálny YAML.

## 27. Observability

Logs a traces korelujú pipeline execution, agent step, model requests, MCP server, tool name, latency a typed outcome. Sensitive payload sa rediguje.

Metrics sledujú turn count, tool errors, output validity, stale results, mutation count a business confirmation. Success step bez valid outputu sa reportuje oddelene.

## 28. Audit

Audit chain zaznamená agent definition create/update, pipeline reference, execution actor, scoped token, MCP configuration a resource mutations. Provider logs sú supplementary.

Catalog edit po incidente sa nezamieňa za stav počas execution. Evidence pinne historical generation.

## 29. Canary

Nová agent version sa spustí na representative read-only tasks a synthetic repo/resource. Sleduje selection, tool calls, outputs, latency a denied paths.

Mutation canary používa reversible target a independent read-back. Rollout sa zastaví pri schema drift, increased tool count alebo output ambiguity.

## 30. Kill switch

Kill switch dokáže deaktivovať agent version, odstrániť mutation permission, odpojiť MCP connector alebo zastaviť pipeline trigger. Control nezávisí od modelu.

Outstanding executions sa cancelujú a ich side effects reconciliujú. New tasks môžu prejsť na safe deterministic fallback.

## 31. Incident triage

Triage začína exact agent version, pipeline SHA, image digest, inputs, trigger, model route, MCP list a token scope. Potom sa rekonštruuje trajectory a first divergence.

Nejasný output môže byť spôsobený instructions, model, tool schema, MCP drift alebo downstream defaultom. Každá vrstva sa overí samostatne.

## 32. Positive acceptance

Agent analyzuje pinned synthetic PR, použije iba read tools, vráti schema-valid outputs a evidence digest. Downstream gate spracuje expected recommendation.

Druhý test s odlišným repo a findingom zmení output bez cross-run state leakage.

## 33. Forbidden acceptance

Untrusted trigger sa pokúsi prepísať instructions, vybrať privileged connector alebo vyvolať generic create tool. Agent a policy musia skončiť bez mutation a secret disclosure.

Missing output, unknown enum a stale commit musia fail-closed. Empty string nesmie znamenať allow.

## 34. Recovery acceptance

Po deaktivácii bad agent version pipeline pinne predchádzajúcu known-good generation. Re-run používa nový operation ID, ale zachová original business key a najprv reconciliuje external state.

Second execution potvrdí správny image, connector, outputs a downstream gate. Bad version už nie je selectable.

## 35. Čo green step nepreukazuje

Green Agent step preukazuje iba Harness step conclusion podľa configured failure semantics. Nezaručuje správny model reasoning, úplné tool results, valid output ani downstream business change.

Acceptance musí preto obsahovať typed output validation a independent business post-condition.

## Primárne zdroje

- https://developer.harness.io/3k-docs/ai/harness-agents/
- https://developer.harness.io/docs/platform/harness-ai/core-capabilities/in-your-pipelines/worker-agent/configuration/
- https://developer.harness.io/docs/platform/harness-ai/core-capabilities/in-your-pipelines/harness-agents-references/
- https://developer.harness.io/docs/platform/harness-ai/model-connector/
- https://developer.harness.io/docs/platform/harness-ai/core-capabilities/
- https://developer.harness.io/docs/platform/pipelines/pipeline-settings/

## Zhrnutie

Kapitola ukazuje, že worker agents v pipelines sa nesmie redukovať na dostupnosť AI funkcie alebo úspešný model response. Authoritative proof vzniká až spojením exact subjectu a generation, deterministic scope a identity, policy enforcementu, execution evidence, downstream read-backu, failure semantics a opakovateľného recovery testu.

## Navigácia

- Predchádzajúca kapitola: [DevOps Agent pre pipeline a resource operations](devops-agent-pipeline-resource-operations.md)
- Nasledujúca kapitola: [MCP connectors a external tools](mcp-connectors-external-tools.md)
