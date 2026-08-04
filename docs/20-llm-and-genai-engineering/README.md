# LLM and GenAI Engineering

Sekcia vysvetľuje LLM application lifecycle od modelu, tokenizácie, promptu a structured contractu cez retrieval, tool calling a inference serving až po evals, tracing, security, cost a production troubleshooting. Demo odpoveď nie je acceptance verdict; rozhoduje reprodukovateľný dataset, exact model/prompt/retrieval generation a merateľný outcome.

## Predpoklady

Odporúčané predchádzajúce oblasti:

- Machine Learning Fundamentals
- MLOps and ML Platforms
- Security and Identity
- Observability
- Keycloak and Identity Platform

## Authoritative poradie — aktívne kapitoly

1. [Generative AI, foundation model a large language model](generative-ai-foundation-model-llm.md)
2. [Transformer architecture na praktickej úrovni](transformer-architecture-practical.md)
3. [Tokens, tokenization a context window](tokens-tokenization-context-window.md)
4. [Embeddings a semantic similarity](embeddings-semantic-similarity.md)
5. [Inference parameters, sampling a determinism](inference-parameters-sampling-determinism.md)
6. [Prompt roles, instructions, context a examples](prompt-roles-instructions-context-examples.md)
7. [Zero-shot, one-shot a few-shot prompting](zero-one-few-shot-prompting.md)
8. [Prompt templates, variables a versioning](prompt-templates-variables-versioning.md)
9. [Prompt decomposition a chain-of-thought boundaries](prompt-decomposition-chain-of-thought-boundaries.md)
10. [Structured Outputs a schema validation](structured-outputs-schema-validation.md)
11. [Function calling a tool calling](function-calling-tool-calling.md)
12. [Model selection a capability/cost trade-offs](model-selection-capability-cost-tradeoffs.md)
13. [Model version pinning a compatibility](model-version-pinning-compatibility.md)
14. [Retrieval-Augmented Generation architecture](retrieval-augmented-generation-architecture.md)
15. [Chunking, metadata a document processing](chunking-metadata-document-processing.md)
16. [Vector stores a indexing](vector-stores-indexing.md)
17. [Retrieval, hybrid search a reranking](retrieval-hybrid-search-reranking.md)
18. [Context assembly a citation grounding](context-assembly-citation-grounding.md)
19. [RAG evaluation a retrieval diagnostics](rag-evaluation-retrieval-diagnostics.md)
20. [Fine-tuning, instruction tuning a preference tuning](fine-tuning-instruction-preference-tuning.md)
21. [PEFT, adapters a LoRA](peft-adapters-lora.md)
22. [Quantization a local inference](quantization-local-inference.md)
23. [GPU memory, batching a serving performance](gpu-memory-batching-serving-performance.md)
24. [Prompt caching, semantic caching a response caching](prompt-semantic-response-caching.md)
25. [LLM gateways, routing, fallback a rate limiting](llm-gateways-routing-fallback-rate-limiting.md)
26. [Prompt Registry a lifecycle](prompt-registry-lifecycle.md)
27. [LLM evaluation datasets a graders](llm-evaluation-datasets-graders.md)
28. [Human evaluation a expert feedback](human-evaluation-expert-feedback.md)
29. [Tracing, token usage a cost observability](tracing-token-usage-cost-observability.md)
30. [Hallucination, faithfulness a factuality](hallucination-faithfulness-factuality.md)
31. [Prompt injection a indirect prompt injection](prompt-injection-indirect-prompt-injection.md)
32. [Data exfiltration, tool abuse a excessive agency](data-exfiltration-tool-abuse-excessive-agency.md)
33. [Guardrails, moderation a output validation](guardrails-moderation-output-validation.md)
34. [Privacy, retention a provider data controls](privacy-retention-provider-data-controls.md)
35. [Multimodal models](multimodal-models.md)
36. [LLMOps a production readiness](llmops-production-readiness.md)
37. [LLM application troubleshooting](llm-application-troubleshooting.md)

## Authoring a evidence štandard

Každá kapitola bude používať rovnaký prose-first štandard ako sekcie 00–17:

```text
business alebo user outcome
→ exact data/model/prompt/agent subject a generation
→ authority, trust a ownership boundary
→ internal lifecycle alebo mutation path
→ authoritative read-back a proof boundary
→ failure a competing hypotheses
→ containment a recovery
→ positive, forbidden a second-operation acceptance
```

Rýchlo sa meniace produkty, API a protokoly sa pri každom bloku znovu overia proti aktuálnym primárnym zdrojom. Dokumentácia nesmie zamieňať offline eval, control-plane status alebo úspešný tool call za produkčný business outcome.

## Praktická vrstva

Nosný end-to-end smer sekcie:

```text
versioned prompt alebo RAG corpus → model/retrieval execution → grounded structured answer → eval dataset → tracing, latency, security a cost verdict → controlled promotion
```

Samostatné laby a troubleshooting drilly sa aktivujú až po dostatočnom koncepčnom základe. Dokumentačný workflow môže overiť súbory, príkazy a konzistenciu modelu, ale nepreukazuje vykonanie tréningu, inference, agentického side effectu ani produkčného outcome-u.

## Stav

Aktuálny authoritative stav sekcie je **37/37 · Ready for user review**. Desiaty a záverečný authoritative blok uzatvára sekciu kapitolou 37 a incidentom `GENAI-SUPPORT-10`. Troubleshooting kapitola používa exact business-operation a technical-attempt identity, symptom a invariant framing, privacy-safe evidence preservation, jednotný evidence envelope, desired/resolved/loaded/effective-state comparison, causal operation graph, competing hypotheses a first-divergence analysis. Diagnostika pokrýva provider/API errors, request IDs, retryability a unknown outcomes, quotas a overload, latency a streaming, model/route/prompt/context resolution, RAG a citations, factuality, structured outputs, tools a durable side effects, guardrails, prompt injection, privacy, multimodal preprocessing, caches, cost a segment regressions aj measurement defects. Recovery model zahŕňa safe replay, counterfactual tests, composed-release bisect, change correlation, impact-driven containment, complete rollback, business/security/privacy reconciliation a positive, forbidden, recovery, second-operation a alternate-scenario acceptance. Všetkých 37 kapitol sekcie má authoritative prose-first obsah a synchronizovaný repository evidence model. Dokumentačné kontroly nepreukazujú complete production traces, provider behavior, reálne tool side effects, incident response, rollback drills ani business outcomes; sekcia je preto `Ready for user review`, nie runtime `Verified`, production `Stable` ani user `Accepted`.
