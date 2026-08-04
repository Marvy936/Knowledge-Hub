# LLM application troubleshooting

LLM application troubleshooting je systematické hľadanie prvej vrstvy, v ktorej sa skutočný behavior odchýlil od požadovaného business outcome-u. Nezačína otázkou „prečo model odpovedal zle“, pretože výsledok môže vzniknúť v routingu, prompt resolution, retrievalu, cache, multimodálnom preprocessingu, provider API, guardraile, tool executore, downstream systéme alebo v meraní samotnom. Správny postup zachováva viacero competing hypotheses, viaže každý dôkaz na exact operation a release generation a uzatvára incident až po authoritative business read-backu.

V incidente `GENAI-SUPPORT-10` support assistant uviedol nepodporenú refund výnimku a refund tool vytvoril dve transakcie. Dashboard ukazoval jeden úspešný HTTP request, ale úplný operation graph obsahoval provider timeout po možnom dokončení, retry cez fallback route, partial rollout promptu, stale retrieval cache, starú guardrail generation a druhý tool attempt bez stabilného idempotency key. Viditeľná nesprávna veta nebola jediným problémom a posledný úspešný span nebol root cause. Troubleshooting musel oddeliť factuality failure, release-resolution drift, unknown tool outcome, retry behavior a chýbajúci business reconciliation.

## 1. Troubleshooting subject

Vyšetrovanie musí najprv pomenovať presný subject. „Chatbot včera zlyhal“ neumožňuje odlíšiť user session, business operation, provider request, model generation ani side effect. Subject zahŕňa časové okno, tenant, user intent, operation identity, release manifest, route, modality a authoritative outcome.

```yaml
troubleshooting_subject:
  incident_id: GENAI-SUPPORT-10
  tenant: sk-retail
  user_session_id: session-771
  business_operation_id: refund-case-82413
  application_request_id: app-req-91021
  trace_id: 8fb2a7d1...
  observed_at: 2026-08-04T12:43:18Z
  expected_outcome: explain-policy-without-writing-refund
  observed_outcome:
    answer: unsupported-refund-exception
    refund_transactions: 2
  release_manifest: support-release-2026-08-04.10
  route_release: support-route-v18
  modalities: [text, pdf]
```

Business operation a technical attempt nie sú synonymá. Jedna user akcia môže vytvoriť viac gateway, provider, retrieval a tool attempts; naopak jeden provider response môže byť iba medzikrokom dlhšej durable operation.

## 2. Symptom, impact a invariant

Symptom je pozorovanie, nie diagnóza. „Model hallucinuje“, „RAG nefunguje“ alebo „API je pomalé“ už obsahujú predčasný root-cause záver. Triage najprv zapíše pozorovaný rozdiel medzi expected a actual outcome, dotknutý segment, čas, frekvenciu, severity a porušený invariant.

```yaml
symptom:
  observed: two refunds exist for one approved operation
  expected: zero refunds because user requested explanation only
  invariant: refund write requires explicit approved action digest
  affected_segment: sk-retail / refund-policy / pdf-attachment
  first_known_bad: 2026-08-04T12:40:00Z
  last_known_good: 2026-08-04T11:55:00Z
  estimated_scope: 7 sessions
  severity: high
```

Impact sa meria business a security jazykom: nesprávna suma, unauthorized side effect, disclosure, SLA breach, blocked users alebo cost spike. Samotný počet model errors nemusí korelovať s reálnou škodou a HTTP success môže sprevádzať nesprávny business outcome.

## 3. Preserve evidence before mutation

Prvá operátorská povinnosť je zachovať dostatok dôkazov bez neprimeraného kopírovania citlivého obsahu. Unreviewed redeploy, cache flush, prompt edit alebo replay cez write tools môže zničiť lineage a vytvoriť ďalší incident. Evidence preservation preto predchádza experimentom.

Zachová sa exact manifest, loaded-state digest, trace topology, provider a client request IDs, response metadata, route decision, retrieval document IDs a scores, cache keys/generations, guardrail verdicts, tool operation IDs, authorization snapshot a business read-back. Raw prompt, document alebo tool payload sa zachová iba podľa privacy policy; tam, kde obsah nemožno logovať, sa používajú digests, classifications, object IDs a controlled forensic access.

## 4. Minimum evidence envelope

Jednotný evidence envelope umožňuje porovnávať incident, known-good operation a controlled replay. Bez neho sa tímy pozerajú na rozdielne requesty a spor o root cause je v skutočnosti spor o subject.

```yaml
evidence_envelope:
  identity:
    business_operation_id: refund-case-82413
    application_request_id: app-req-91021
    provider_request_ids: [req_a1, req_b2]
    tool_operation_ids: [refund-op-91, refund-op-92]
  release:
    intended_manifest: sha256:rel-10
    loaded_manifest: sha256:rel-10
    model_response_ids: [model-snapshot-a, model-snapshot-b]
    prompt_digest: sha256:prompt-44
    corpus_snapshot: corpus-2026-08-04.3
    index_generation: index-771
    guardrail_release: guardrail-v21
    tool_catalog: support-tools-v18
  execution:
    route_attempts: 2
    provider_attempts: 2
    retrieval_attempts: 1
    tool_attempts: 2
    streaming_completed: false
    terminal_state: partial-success
  outcome:
    answer_id: answer-551
    durable_refund_ids: [rf-901, rf-902]
    user_visible_status: success
```

Envelope nie je náhradou trace-u. Je to incident index, ktorý spája authoritative stores a umožňuje overiť, či sú všetky dôkazy z rovnakej operation a generation.

## 5. Desired, resolved, loaded a effective state

Troubleshooting oddeľuje štyri stavy. Desired state je deklarovaný release manifest. Resolved state je manifest po vyriešení aliases, dependencies, regions a feature flags. Loaded state je konfigurácia skutočne načítaná jednotlivými runtime instances. Effective state je behavior po provider-side controls, caches, user/tenant overrides a downstream policy.

```text
desired release
→ dependency resolution
→ resolved release
→ deployment a cache loading
→ loaded runtime state
→ provider a downstream effects
→ effective behavior
```

Porovnanie Git commit-u s incidentom nestačí. Partial rollout, stale process, mutable provider alias alebo tenant override môže vytvoriť behavior, ktorý sa v repository nenachádza.

## 6. Timeline a operation graph

Lineárny log býva pri GenAI aplikácii zavádzajúci, pretože retries, fallbacks, retrieval, streaming a tools vytvárajú graph. Timeline musí rozlišovať začiatok, koniec a outcome každého attemptu a zároveň durable business state.

```text
12:43:18.000  application operation starts
12:43:18.012  route selects provider A / model A
12:43:18.041  retrieval returns documents D7, D9
12:43:19.403  provider A streams tool proposal
12:43:19.710  refund tool commits operation refund-op-91
12:43:20.000  provider connection times out before terminal response
12:43:20.180  gateway retries through provider B
12:43:21.005  provider B proposes refund again
12:43:21.220  refund tool commits refund-op-92
12:43:21.500  application returns success
12:44:02.000  ledger shows two durable refunds
```

First visible error je duplicitný refund, ale first divergence môže byť chýbajúci action digest, nesprávna retry classification alebo tool executor bez read-before-retry. Graph sa preto vyhodnocuje od business invariantov späť aj od inputu dopredu.

## 7. First divergence

First divergence je najskorší preukázaný bod, kde actual execution prestal zodpovedať expected execution. Nie je to automaticky najskorší warning ani posledná exception. Každá hypotéza musí uviesť expected state, actual state, authoritative evidence a dôsledok pre ďalšie kroky.

```yaml
first_divergence_candidate:
  stage: tool authorization
  expected: refund write forbidden without approved action digest
  actual: tool executor accepted model-generated arguments directly
  evidence:
    authorization_snapshot: authz-88
    approval_token: absent
    tool_audit: allowed
  downstream_effect: refund-op-91 committed
```

Ak skoršia odchýlka iba zhoršila answer quality, ale nemohla vytvoriť side effect, nemusí byť root cause duplicitnej transakcie. Jeden incident môže mať viac contributing causes a viac first divergences pre odlišné outcomes, napríklad jednu pre false answer a druhú pre duplicate write.

## 8. Competing-hypothesis discipline

Tím si na začiatku udrží niekoľko realistických hypotéz a priebežne ich vyraďuje dôkazmi. Táto disciplína bráni tomu, aby prvý provider error, prompt diff alebo dashboard spike monopolizoval vyšetrovanie. Hypotéza musí byť falzifikovateľná a musí pomenovať dôkaz, ktorý ju potvrdí alebo odmietne.

| Hypotéza | Potvrdzujúci dôkaz | Vyraďujúci dôkaz |
|---|---|---|
| Wrong loaded release | instance read-back ukáže starý prompt alebo guardrail digest | všetky relevantné instances načítali exact expected manifest |
| Retrieval failure | required authoritative document chýba alebo je pod thresholdom | correct document a passage boli v model contextu |
| Generation failure | evidence je správne, ale atomic claim ho odporuje | claim vznikol už v extractor-e alebo tool response |
| Retry/unknown-outcome failure | prvý write sa commitol pred timeoutom a druhý attempt použil nový key | authoritative read-back ukáže prvý write absent |
| Provider-side behavior change | rovnaký immutable request replay sa líši iba na provider generation | known-good provider a snapshot reprodukujú rovnaký failure |
| Guardrail enforcement bypass | deny verdict existuje, ale downstream pokračuje | policy verdict bol allow podľa expected release |
| Measurement defect | dashboard deduplikuje attempts alebo používa chybný denominator | raw operation records zodpovedajú dashboardu |

Hypotézy sa nemajú násilne zredukovať na jednu príčinu. Complex LLM incident môže vyžadovať model-quality fix, retry fix, authorization fix a observability fix súčasne.

## 9. Symptom taxonomy

Symptom taxonomy pomáha vybrať prvé evidence queries, ale neurčuje root cause. Jedna operation môže patriť do viacerých kategórií, pretože napríklad latency spike môže aktivovať fallback a následne spôsobiť quality alebo privacy regression.

| Symptom class | Prvé otázky |
|---|---|
| Transport alebo API error | Aký status, `error.type`, provider request ID, retry count a terminal state vznikli? |
| Latency alebo timeout | Kde je čas: queue, connect, TTFT, generation, retrieval, tool, guardrail alebo downstream commit? |
| Empty, truncated alebo stuck stream | Prišiel terminal event, finish reason a final usage? Zrušil klient stream? |
| Wrong alebo unsupported answer | Ktoré atomic claims sú nesprávne a aký evidence set mal model? |
| Citation failure | Je citácia prítomná, relevantná a skutočne podporuje claim? |
| Structured-output failure | Zlyhala syntax, schema, semantic invariant alebo downstream interpretation? |
| Tool failure alebo duplicate side effect | Je outcome committed, absent alebo unknown? Použil sa durable operation ID? |
| Security alebo privacy incident | Ktorý trust boundary, data class, destination alebo permission sa porušili? |
| Cost spike | Vzrástli tokens, attempts, tool usage, cache misses, fallback alebo accepted-outcome denominator? |
| Segment regression | Ktorý jazyk, tenant, modality, model route alebo risk tier sa odchýlil? |
| Multimodal failure | Zlyhal raw artifact, preprocessing, OCR/STT, alignment, context alebo reasoning? |

Taxonomy sa používa na triage a query routing. Definitívny verdict stále vyžaduje operation-level evidence a first-divergence analýzu.

## 10. Provider API errors

HTTP a provider errors sa klasifikujú podľa retryability, authorization, request validity a unknown-outcome rizika. Status code bez request identity a operation contextu nestačí. OpenAI napríklad odporúča logovať `x-request-id` a umožňuje vlastný `X-Client-Request-Id`; rate-limit headers ukazujú limity a reset pre requests a tokens.

| Trieda | Typický význam | Bezpečná reakcia |
|---|---|---|
| 400/422 | invalid request, schema alebo parameter | nerepeatovať bez opravy requestu |
| 401 | chýbajúca alebo neplatná autentifikácia | overiť credential source, audience a expiry |
| 403 | principal nemá oprávnenie alebo policy blokuje operation | overiť authorization a product/region entitlement |
| 404 | model, object alebo endpoint neexistuje v danom scope | overiť project, region, API version a object lifecycle |
| 409 | conflict alebo state transition race | načítať authoritative current state pred ďalším pokusom |
| 429 | request, token, concurrency alebo spend limit | rešpektovať reset/backoff a chrániť fairness |
| 5xx | provider alebo gateway failure | retry iba podľa idempotency a operation semantics |
| timeout/network reset | outcome môže byť unknown | read-before-retry pri každom možnom side effectu |

SDK exception class je iba lokálna reprezentácia. Incident record zachová HTTP status, provider error code, request ID, client request ID, attempt ordinal, route a whether any response bytes or tool effects already occurred.

## 11. Retryability a unknown outcomes

Retryable transport failure neznamená retryable business operation. Read-only model call možno často zopakovať, ale agent workflow môže pred timeoutom vykonať email, payment, refund alebo permission mutation. Gateway, orchestrator a tool executor preto potrebujú jednotnú operation identity.

```text
submit durable operation K
→ connection timeout
→ query authoritative state for K
→ committed / absent / pending / indeterminate
→ retry iba s rovnakým K a policy-defined semantics
```

Nový random idempotency key pri každom technical attempt zruší ochranu. Rovnaký key bez správneho canonical request digestu môže naopak nesprávne deduplikovať odlišnú akciu; executor musí viazať key na principal, resource, action a payload digest.

## 12. Rate limits, quotas a overload

Rate-limit incident sa nevyšetruje iba podľa request countu. LLM workloads spotrebúvajú input, output, cached a reasoning tokens, concurrency, provider capacity, tool slots a spend budget. Retry storm môže znásobiť všetky tieto dimenzie a fallback môže presunúť overload do ďalšieho regiónu alebo providera.

Troubleshooting porovná request/token/concurrency limits, remaining values, reset times, queue depth, admission decisions, tenant fairness a retry amplification. Ak dashboard ukazuje 429, treba zistiť, či limit vznikol na application gateway, provider project, model deployment, region, organization alebo downstream tool API.

## 13. Latency decomposition

End-to-end latency sa rozloží na queue, gateway, retrieval, prompt assembly, provider connect, time to first token, inter-token latency, guardrail, tool, downstream commit a client rendering. Pri streaming flows je TTFT dobrý user-experience signál, ale nehovorí nič o terminal completion ani side effecte.

```yaml
latency_breakdown_ms:
  admission_queue: 140
  retrieval: 82
  prompt_assembly: 11
  provider_connect: 45
  time_to_first_token: 620
  generation: 1820
  tool_execution: 510
  output_validation: 18
  client_delivery: 33
  total: 3279
```

Percentiles sa segmentujú podľa modelu, route, prompt size, modality, tenant a cache statusu. Average môže skryť queue collapse alebo dlhý tail konkrétnej fallback route.

## 14. Streaming failures

Streaming zavádza stavy, ktoré sa nedajú zredukovať na success/error. Klient môže dostať partial text, tool proposal alebo audio frames a potom sa odpojiť; provider môže dokončiť generation a účtovať tokens, hoci application terminal event neprijme. Troubleshooting preto zaznamenáva stream start, first byte, chunks, client cancellation, provider terminal event, finish reason a final usage.

Partial output sa nesmie automaticky publikovať alebo parse-núť ako complete structured response. Tool execution počas streamu vyžaduje jasnú commit boundary; inak reconnect alebo replay môže zopakovať side effect, ktorý user nikdy nevidel.

## 15. Model and route resolution

Model name v source code nemusí byť actual model. Gateway alias, provider deployment, regional route, fallback a provider-side snapshot môžu zmeniť capability, tokenization, schema support, safety alebo latency. Incident musí zachovať requested model, resolved route, provider, response model a deployment generation.

Route troubleshooting overí compatibility requirements, health inputs, circuit state, load-balancing decision, region/data policy a fallback reason. Fallback, ktorý zachová HTTP contract, ale nie behavior contract, môže odstrániť structured output, tool support alebo safety parity a vytvoriť sekundárny incident.

## 16. Prompt resolution

Prompt troubleshooting nezačína pohľadom na aktuálny alias. Potrebný je immutable prompt version alebo digest skutočne resolved pre incident, typed variables, rendered roles/messages, examples, output schema, tool definitions a system-instruction hierarchy. Secret alebo PII hodnoty môžu byť redacted, no variable presence, classification a digest zostávajú.

Medzi typické odchýlky patrí stale alias cache, partial rollout, missing variable, nesprávny escaping, role mutation, truncated examples alebo prompt incompatible s novým modelom. Prompt diff sa interpretuje spolu s modelom, contextom a eval segmentom; samotná textová zmena nepreukazuje causal effect.

## 17. Context window a truncation

Context overflow sa môže prejaviť errorom, implicitným truncation, vynechaným documentom alebo zvýšenou latency/cost. Troubleshooting porovná estimated a provider-reported tokens, assembly order, reserved output budget, truncation policy a skutočne vložené messages/documents/tool definitions.

„Dokument bol retrieved“ neznamená „dokument bol v model contextu“. Required evidence môže byť odstránené dedupe-om, rerankerom, budget allocatorom alebo provider-side limitom. Context manifest preto obsahuje IDs, order, byte/token counts, truncation reason a digests.

## 18. Retrieval pipeline

RAG troubleshooting rozkladá retrieval na query construction, filters/ACL, embedding generation, index snapshot, candidate retrieval, hybrid merge, reranking, dedupe a context assembly. Wrong answer môže vzniknúť aj pri správnom top documente, ak relevantný passage nebol chunknutý alebo sa stratil pri assembly.

```text
user question
→ canonical retrieval query
→ tenant/ACL filters
→ candidate set
→ reranked set
→ selected chunks
→ assembled context
→ generated claims
```

Každý krok má authoritative evidence. Query replay proti aktuálnemu indexu nie je dostatočný, ak incident použil inú corpus alebo index generation.

## 19. Retrieval diagnostics

Retrieval incident sa hodnotí claim-by-claim a stage-by-stage. Najprv sa overí, či authoritative source v corpus existoval a bol temporálne platný. Potom sa zistí, či ho parser a chunker zachovali, index obsahoval, retrieval vrátil, reranker ponechal a context assembler vložil.

Metrics ako recall@k, MRR alebo nDCG pomáhajú datasetovo, ale jednotlivý incident uzavrie exact document a passage lineage. High similarity score nie je dôkaz business authority ani factual support.

## 20. Factuality a faithfulness

False answer sa rozdelí na atomic claims. Pre každý claim sa určí truth status, evidence support, citation support, temporal scope, entity scope a required authority. Factual correctness a faithfulness sa môžu rozísť: tvrdenie môže byť všeobecne pravdivé, ale nepodporené povoleným customer-policy evidence setom.

Troubleshooting rozlišuje unsupported claim, contradicted claim, stale claim, wrong entity, overgeneralization a missing abstention. Model judge môže prioritizovať review, ale high-risk verdict vyžaduje deterministic source alebo kvalifikovaného domain experta podľa authority matrix.

## 21. Citation failures

Citation presence nie je acceptance. Citácia musí smerovať na correct artifact/version, podporovať konkrétny claim a pokrývať všetky material claims, ktoré policy vyžaduje. Link na relevantný dokument môže byť stále nefaithful, ak cited passage danú výnimku neobsahuje.

Troubleshooting porovná generated claim, cited passage, retrieved passage a actual context. Tým sa odlíši wrong citation formatting, wrong source selection, unsupported inference a post-generation citation attachment, ktoré nikdy neovplyvnilo answer.

## 22. Structured output

Structured-output troubleshooting má minimálne štyri vrstvy: transport completion, syntax, schema a business semantics. Validný JSON môže mať nesprávny enum, cross-field contradiction, unauthorized action alebo amount mimo policy. Parser success preto nie je business acceptance.

```text
complete response?
→ parseable serialization?
→ schema-valid object?
→ canonicalized values?
→ business invariants?
→ authorization a side-effect policy?
```

Retry after schema failure musí rešpektovať cost a side-effect boundaries. Repair model alebo parser nesmie zmeniť význam citlivých fields bez explicitnej validation a lineage.

## 23. Tool proposal versus execution

Model tool call je návrh, nie autorizácia. Troubleshooting oddeľuje proposed tool name/arguments, schema validation, canonical resource resolution, authorization decision, approval token, executor attempt a durable business outcome. V incidente `GENAI-SUPPORT-10` modelová chyba mohla navrhnúť refund, ale duplicate write vznikol až preto, že executor prijal návrh bez approval digestu a retry použil novú operation identity.

Tool trace obsahuje argument digest a classifications, nie nevyhnutne raw secret values. Executor log je authoritative pre execution attempt; downstream system alebo ledger je authoritative pre committed outcome.

## 24. Tool errors a side effects

Tool success response môže byť false positive, ak downstream commit zlyhal po acknowledgemente. Tool error môže byť false negative, ak commit prebehol a response sa stratil. Troubleshooting vždy vykoná authoritative read-back podľa operation ID, nie iba podľa SDK return value.

Side-effect failures sa klasifikujú ako absent, committed-once, committed-multiple, partially committed, compensated alebo unknown. Každý stav má odlišný recovery path a odlišné pravidlá pre retry.

## 25. Guardrail a moderation failures

Guardrail troubleshooting sleduje detector input, normalized representation, detector/model generation, scores/categories, policy rule, enforcement action a downstream continuation. Detector môže správne označiť obsah, ale policy ho povolí; policy môže deny-nuť, ale exception handler pokračuje fail-open.

Intervention point je kritický. Final-output moderation nemôže zabrániť tool callu, ktorý sa vykonal skôr, a text-only detector neuvidí injection v obrázku alebo OCR layeri. Replay preto zachová exact modality a preprocessing release.

## 26. Prompt injection a instruction trust

Pri podozrení na prompt injection sa zisťuje, ktorý untrusted artifact vstúpil do contextu, akú provenance a trust label mal, či zmenil goal/tool plan a či external policy zabránila authority escalation. Úspešný jailbreak text nie je sám osebe dôkaz data exfiltration; decisive evidence je unauthorized data flow alebo side effect.

Troubleshooting preskúma retrieval documents, emails, tool outputs, memory writes, images a metadata. Delimiters alebo model refusal sa nepovažujú za primary security boundary; rozhoduje capability, authorization, egress a approval enforcement mimo modelu.

## 27. Privacy a data controls

Privacy incident sa mapuje store-by-store a flow-by-flow. Training opt-out, abuse-monitoring retention, application state, files, prompt caches, traces, eval stores, tool providers a backups sú odlišné surfaces. Provider request success nepreukazuje správny retention alebo region profile.

Evidence zahŕňa provider product a endpoint, organization/project, effective data-control mode, region, feature eligibility, object IDs, deletion state a application telemetry. Ak raw content nie je povolené logovať, troubleshooting sa opiera o metadata, digests, synthetic probes a controlled provider evidence.

## 28. Multimodal failures

Multimodálny incident sa rozkladá od raw media po business decision. Overí sa object digest/version, validation, resize/crop/tiling, audio resampling a channels, frame sampling, OCR/STT/diarization, context assembly, model reasoning a spatial/temporal validation.

Wrong text output môže byť dôsledok správneho modelového reasoning-u nad poškodeným intermediate artifactom. Preto sa porovná raw a processed media, boxes, timestamps, speaker labels, selected frames a confidence, nie iba finálny transcript.

## 29. Cache failures

Cache incident môže znamenať stale result, false semantic hit, cross-tenant leak, incompatible generation alebo iba neočakávaný miss a cost spike. Cache key musí viazať relevantný prompt, model, corpus, policy, tenant a schema generation; generic normalized question často nestačí.

Troubleshooting zaznamená cache type, key digest, namespace, generation, hit source, stored release metadata, TTL a invalidation events. Cache flush môže dočasne skryť root cause, preto sa pred invalidáciou zachová entry metadata a reprodukovateľný incident case.

## 30. Cost anomalies

Cost spike sa analyzuje na jednotku accepted business outcome, nie iba na request. Zvýšenie môže pochádzať z dlhšieho promptu, reasoning tokens, output length, retries, fallback, cache misses, retrieval/tool usage, multimodálnych tokens alebo failed operations bez user value.

```text
total provider a tool cost
÷ accepted business outcomes
```

Provider-reported usage, application estimate a invoice/reconciled cost sa oddeľujú. Streaming disconnect alebo failed fallback môže byť účtovaný aj vtedy, keď application posledný response nezaznamenala.

## 31. Segment analysis

Aggregate metric môže zostať stabilná, keď incident zasiahne malý high-risk segment. Troubleshooting preto segmentuje podľa tenant, locale, language, modality, model route, prompt release, corpus/index, risk tier, input length, cache state a tool path.

Segment sa vyberá podľa hypothesis, nie náhodným dashboard slicingom. Pri malých počtoch sa uvádza uncertainty a raw cases; jeden incident v critical workflow môže vyžadovať containment aj bez štatisticky významného aggregate regressionu.

## 32. Measurement a dashboard defects

Observability môže sama zlyhať. Sampling môže vynechať failed spans, aggregation môže deduplikovať retries, success môže znamenať iba HTTP 200 a dashboard denominator môže ignorovať client disconnects alebo rejected business outcomes. Troubleshooting preto overí telemetry completeness a metric definitions.

OpenTelemetry odporúča nízko-kardinalitný `error.type` a operation-specific attributes; HTTP conventions obsahujú aj resend count pre retries. Custom error messages sa nepoužívajú ako metric labels, pretože majú vysokú cardinality a komplikujú agregáciu.

## 33. Safe reproduction

Reprodukcia musí minimalizovať ďalšie škody a zachovať relevantné conditions. Produkčný incident sa nereplay-ne s live write tools, real customer data alebo broad credentials, pokiaľ neexistuje explicitný controlled plan. Preferuje sa sanitized immutable incident fixture, read-only tools, sandbox a deterministic downstream stubs.

```yaml
replay_plan:
  incident_fixture: genai-support-10-v1
  release_manifest: sha256:rel-10
  provider_mode: recorded-or-sandbox
  tool_mode: dry-run
  data: synthetic-equivalent
  assertions:
    - no_refund_commit
    - claim_supported_by_policy_passage
    - one_business_operation_identity
```

Replay fidelity sa dokumentuje. Ak provider snapshot alebo private data nemožno reprodukovať, verdict zostáva obmedzený a nesmie sa prezentovať ako complete root-cause proof.

## 34. Counterfactual tests

Counterfactual test zmení jednu premennú a ostatné drží konštantné. Napríklad použije rovnaký prompt/context s known-good modelom, rovnaký model s known-good retrieval snapshotom alebo rovnaký workflow s tool executorom v deny-all mode. Tým sa oddeľujú correlated changes.

One-factor-at-a-time nie je vždy možný pri nekompatibilných components. Vtedy sa testujú celé compatible manifests a výsledok sa interpretuje ako release-level evidence, nie dôkaz jednej line change.

## 35. Bisect composed releases

Git bisect nad application code nestačí, ak behavior závisí od modelu, promptu, corpus, tools a provider controls. Troubleshooting používa composed-release bisect: porovná known-good a first-bad manifests a vytvorí compatible intermediate candidates.

Každý candidate prejde minimálnymi safety a schema gates pred replayom. Mutable aliases sa resolve-nú na immutable versions; inak bisect testuje meniaci sa subject a výsledok nie je reprodukovateľný.

## 36. Change correlation

Deployment timestamp je iba korelačný signál. Provider môže zmeniť model snapshot, safety behavior alebo quota bez customer commit-u; corpus ingestion a feature flags môžu mať vlastný lifecycle. Change timeline preto zahŕňa všetky control planes.

```text
application deploys
prompt alias changes
model/provider metadata changes
corpus/index publications
tool schema releases
guardrail/privacy policy changes
cache invalidations
infra a quota changes
```

Absencia známej zmeny neznamená absenciu driftu. Loaded-state a provider response metadata sú silnejšie dôkazy než release calendar.

## 37. Containment decision

Containment znižuje ďalší harm skôr, než je root cause úplne známy. Rozhoduje sa podľa porušeného invariant-u a blast radiusu: disable write tool, route high-risk segment do manual review, pin known-good manifest, block destination, reduce concurrency, disable fallback alebo switch to read-only/degraded mode.

Containment musí zachovať evidence a explicitne uviesť secondary risks. Úplné vypnutie môže byť horšie než segment isolation, zatiaľ čo ponechanie unsafe automation pri neznámom scope je neprijateľné.

## 38. Symptom-specific containment

Rôzne symptómy vyžadujú rôzne prvé kroky. Pri duplicate write sa zastaví write path a vykoná ledger reconciliation. Pri privacy incidente sa zastaví data flow, revoke-nú credentials a zachová minimálna forenzná evidence. Pri quality regressione bez side effectu môže stačiť route pinning alebo manual review.

Containment action má ownera, čas, scope, rollback plan a authoritative verification. Feature flag `off` nie je dôkaz, kým runtime read-back a nový request nepotvrdia effective state.

## 39. Recovery plan

Recovery obnovuje known-good behavior a opravuje durable škodu. Technický rollback promptu alebo modelu nezruší refund, email, ACL mutation ani disclosure. Recovery plan preto oddeľuje system restoration, business compensation, security/privacy remediation a customer communication.

```yaml
recovery:
  system:
    - deploy known-good composed manifest
    - invalidate incompatible caches
    - verify loaded state on all instances
  business:
    - reconcile duplicate refunds
    - compensate affected accounts
  security_privacy:
    - revoke exposed credentials
    - delete unauthorized copies where possible
  validation:
    - replay incident fixture
    - run benign and forbidden controls
```

Forward fix sa používa iba vtedy, keď je lepšie pochopený a bezpečnejší než known-good rollback. Emergency edit bez immutable release a review vytvára ďalšiu neznámu generation.

## 40. Rollback completeness

Complete rollback vracia compatible model, prompt, corpus/index, tools/schemas, gateway route, guardrails, privacy profile, preprocessing, caches, eval expectations a application code. Vrátenie iba model aliasu môže ponechať nový tool schema alebo cache entry nekompatibilnú so starým promptom.

Po rollbacku sa vykoná loaded-state read-back na každej relevantnej instance/region a nový second-operation test. Staré in-flight workflows a queues sa explicitne drain-nú, cancel-nú alebo migrujú podľa policy.

## 41. Positive acceptance

Pozitívna acceptance preukazuje, že pôvodný povolený use case opäť dosahuje správny business outcome. Zahŕňa correct answer alebo action, required evidence/citations, schema a business invariants, latency, cost a authorized durable state. Jedna fluent odpoveď nestačí.

Acceptance dataset obsahuje incident case, reprezentatívne benign controls a dotknuté segmenty. Result sa viaže na exact recovered release manifest a loaded-state evidence.

## 42. Forbidden acceptance

Forbidden acceptance dokazuje, že incidentný nežiaduci outcome sa nemôže zopakovať. V `GENAI-SUPPORT-10` to znamená nulový refund bez approved action digestu, žiadny duplicate commit pri timeout/retry a žiadny unsupported policy claim prezentovaný ako authoritative.

Forbidden test sa nesmie zastaviť pri model refusal. Overí policy decision, tool executor, egress, downstream ledger a absence durable side effectu.

## 43. Recovery acceptance

Recovery acceptance overí celý incident lifecycle: detection, containment, rollback alebo forward fix, loaded-state read-back, replay, business reconciliation a traffic restoration. Cieľom nie je iba dostať error rate na normál, ale preukázať, že porušený invariant je obnovený.

Test zahrnie dependency failure a unknown-outcome branch. Ak recovery funguje iba pri clean provider success, nie je pripravená na rovnakú failure semantics, ktorá incident vyvolala.

## 44. Second-operation a alternate-scenario tests

Second-operation test spustí nový request po recovery a overí, že nepoužíva stale prompt, route, retrieval, guardrail alebo cache generation. Tým sa odlíši jednorazovo opravený incident record od skutočne zmeneného runtime behavioru.

Alternate-scenario test zmení tenant, jazyk, modality, tool alebo failure point a zachová rovnaký invariant. Oprava duplicate refundu musí napríklad fungovať aj pri email tool timeout-e, nie iba pri jednom refund endpoint-e.

## 45. Incident verdict

Incident verdict oddeľuje symptom, first divergence, root causes, contributing factors, detection gaps a recovery evidence. „Model hallucinated“ nie je dostatočný verdict, ak application dovolila unauthorized action alebo observability skryla retries.

```yaml
verdict:
  symptom:
    - unsupported refund claim
    - duplicate refund writes
  first_divergence:
    answer_path: retrieval cache returned stale policy generation
    side_effect_path: executor allowed write without approval digest
  root_causes:
    - cache key omitted corpus generation
    - retry created new business operation identity
  contributing_factors:
    - fallback route used different prompt cache
    - dashboard collapsed attempts into one request
  recovery_evidence:
    - incident replay pass
    - forbidden duplicate-write test pass
    - ledger reconciliation complete
```

Verdict sa môže aktualizovať, keď pribudne evidence. Postmortem nemá predstierať istotu tam, kde provider alebo historical telemetry nedovoľujú úplnú rekonštrukciu.

## 46. Troubleshooting playbook

Praktický playbook drží vyšetrovanie v konzistentnom poradí. Každý krok vytvára artifact alebo rozhodnutie, ktoré možno review-nuť a zopakovať.

1. Zapíš exact symptom, business impact a porušený invariant.
2. Identifikuj business operation, technical attempts, tenant, time window a release manifest.
3. Zastav ďalší high-impact harm a zachovaj evidence.
4. Zostav timeline a operation graph vrátane retries, fallbacks, tools a durable outcomes.
5. Porovnaj desired, resolved, loaded a effective state.
6. Vytvor competing hypotheses s potvrdzujúcim a vyraďujúcim dôkazom.
7. Nájdi first divergence pre každý material outcome.
8. Reprodukuj bezpečne s immutable fixture a dry-run tools.
9. Aplikuj complete rollback alebo reviewed forward fix.
10. Over loaded state, positive, forbidden, recovery a second-operation acceptance.
11. Reconcile-ni business, security, privacy a cost následky.
12. Zaznamenaj verdict, detection gaps, owners a follow-up controls.

Playbook nie je mechanický checklist, ktorý nahrádza expert judgment. Udržiava však evidence discipline a zabraňuje preskakovaniu business recovery alebo acceptance krokov.

## 47. Example troubleshooting query model

Observability backendy sa líšia, ale query model zostáva rovnaký: začať business operation identity a rozbaliť všetky attempts a dependencies. Query podľa posledného provider request ID by vynechala skorší timeout a prvý committed tool call.

```text
find operation where business_operation_id = "refund-case-82413"
expand:
  application spans
  gateway route attempts
  provider request IDs
  retrieval/index generations
  prompt/model/guardrail generations
  cache decisions
  tool authorization and execution attempts
  downstream durable state
order by event time and causal parent
```

High-cardinality IDs patria do traces/log lookups, nie do aggregate metric labels. Metrics používajú low-cardinality error classes, routes, releases a segments a následne odkazujú na exemplar/trace.

## 48. Anti-patterns

Troubleshooting zlyháva, keď sa tím uspokojí s posledným errorom, aktuálnym promptom alebo úspešným replayom na inom release-i. Rovnako nebezpečné je plošne flush-núť caches, zvýšiť retries alebo vypnúť guardrails bez pochopenia secondary effects.

Ďalším anti-patternom je zameniť observability za raw-data collection. Ukladanie každého promptu a dokumentu môže vytvoriť privacy incident a stále nemusí zachytiť loaded generations, authorization alebo downstream state, ktoré sú pre root cause dôležitejšie.

## 49. Runbook ownership a escalation

Každý symptom class má ownera a escalation path. Provider/API incident vedie platform alebo gateway owner, retrieval incident data/RAG owner, tool side effect application a downstream owner, security/privacy incident príslušná authority a business compensation product/operations owner.

Incident commander koordinuje spoločný timeline a verdict. Neznamená to, že jeden tím musí rozumieť všetkým vrstvám; znamená to, že evidence a decisions používajú jeden operation subject a business priority.

## 50. Continuous improvement

Po incidente sa fixtures pridajú do eval a replay suites, missing telemetry do instrumentation contractu, chýbajúce invariants do deterministic policy a operational gaps do runbookov. Fix sa neobmedzuje na prompt wording, ak incident ukázal slabý authorization, retry alebo measurement boundary.

Improvement má ownera, deadline, acceptance a review po ďalšej zmene. Metric „počet uzavretých action items“ nestačí; rozhoduje, či rovnaký failure class zachytí gate alebo containment skôr, než vytvorí business harm.

## 51. Čo dokumentačná validácia nepreukazuje

Dokumentácia a CI môžu overiť konzistentný troubleshooting model, links, examples a prose depth. Nepreukazujú, že production traces sú complete, provider request IDs sa logujú, business read-back funguje, tools sú idempotentné ani že on-call dokáže vykonať recovery pod incidentným tlakom.

Runtime `Verified` vyžaduje vykonaný troubleshooting drill nad exact release a evidence envelope. Produkčný `Stable` stav vyžaduje časové evidence, reálne incident response, úspešné rollback/recovery drills a akceptovateľné business outcomes. User `Accepted` zostáva explicitným owner alebo stakeholder verdictom.

## Primárne zdroje

- [OpenTelemetry GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/)
- [OpenTelemetry HTTP span conventions](https://opentelemetry.io/docs/specs/semconv/http/http-spans/)
- [OpenTelemetry recording errors](https://opentelemetry.io/docs/specs/semconv/general/recording-errors/)
- [OpenAI API request IDs and rate-limit headers](https://platform.openai.com/docs/api-reference/introduction)
- [AWS Generative AI Lens — operational excellence](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/operational-excellence.html)
- [AWS Generative AI Lens — monitor all application layers](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genops02-bp01.html)
- [AWS Operational Excellence — operate](https://docs.aws.amazon.com/wellarchitected/latest/operational-excellence-pillar/operate.html)

## Kontrolné otázky

1. Aký exact business operation, release manifest, tenant a časové okno vyšetrujeme?
2. Ktorý pozorovaný symptom a business invariant boli porušené bez predčasného root-cause záveru?
3. Obsahuje evidence envelope provider/client request IDs, loaded generations, retries, tools a durable outcome?
4. Kde je first divergence pre answer path a kde pre side-effect path?
5. Ktoré competing hypotheses ostávajú a aký dôkaz ich potvrdí alebo vyradí?
6. Je timeout retryable iba technicky, alebo je business outcome unknown a vyžaduje read-before-retry?
7. Bol retrieved document skutočne vložený do exact model contextu a podporuje generated claim?
8. Prešiel output iba syntax/schema validation, alebo aj business invariant a authorization?
9. Overuje containment effective runtime state a zastavilo reálny harm?
10. Vracia rollback celý compatible manifest vrátane caches, guardrails, privacy a preprocessing?
11. Dokazujú positive, forbidden, recovery a second-operation tests správny durable business outcome?
12. Ktoré telemetry, policy, eval alebo runbook gaps sa po incidente stanú preventívnym controlom?
