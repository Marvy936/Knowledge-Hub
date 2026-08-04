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

## Plánované authoritative poradie

Nasledujúci inventory je schválený plán sekcie. Položka sa zmení na aktívny Markdown link až v pracovnom bloku, ktorý vytvorí a validuje príslušnú kapitolu. Tým sa plánovaný obsah nezamieňa za hotovú dokumentáciu.

29. Tracing, token usage a cost observability
30. Hallucination, faithfulness a factuality
31. Prompt injection a indirect prompt injection
32. Data exfiltration, tool abuse a excessive agency
33. Guardrails, moderation a output validation
34. Privacy, retention a provider data controls
35. Multimodal models
36. LLMOps a production readiness
37. LLM application troubleshooting

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

Aktuálny authoritative stav sekcie je **28/37 · In progress**. Siedmy authoritative blok aktivuje kapitoly 25–28 a incident `GENAI-SUPPORT-07`. Gateway kapitola modeluje caller a operation identity, control/data plane generations, capability-aware routing, behavior-compatible load balancing a fallback, failure classification, read-before-retry, quotas, backpressure, fairness, circuit breakers, region/data policy a attempt-versus-business telemetry. Prompt Registry kapitola oddeľuje immutable prompt version, mutable alias, rendered instance a composed application release; zavádza typed variables, role/examples/schema/tool dependencies, semantic diff, eval/approval gates, compare-and-swap promotion, runtime loaded-generation read-back, rollback, lineage a access control. LLM-evaluation kapitola definuje estimand, immutable dataset/case manifests, temporal validity, leakage-safe splits, deterministic a model graders, calibration, position/self-preference bias, multi-grader hard gates, repetitions, segment uncertainty, online correlation a grader-gaming recovery. Human-evaluation kapitola zavádza authority matrix, reprezentatívne a kvalifikované cohorts, versioned rubric/UI, blindness/randomization/overlap, inter-annotator agreement, disagreement analysis, expert adjudication, model-assisted review boundaries, ethics/privacy a authority-specific promotion evidence. Kapitoly 25–28 sú pripravené na repository closeout; reálny gateway traffic/failover/rate-limit exercise, prompt-registry promotion, provider eval execution, human annotation study, expert adjudication a business outcome neboli vykonané. Sekcia zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. Ďalší blok sú kapitoly 29–32: tracing/token usage/cost observability, hallucination/faithfulness/factuality, prompt injection a indirect prompt injection a data exfiltration/tool abuse/excessive agency.
