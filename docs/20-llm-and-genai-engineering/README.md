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

## Plánované authoritative poradie

Nasledujúci inventory je schválený plán sekcie. Položka sa zmení na aktívny Markdown link až v pracovnom bloku, ktorý vytvorí a validuje príslušnú kapitolu. Tým sa plánovaný obsah nezamieňa za hotovú dokumentáciu.

25. LLM gateways, routing, fallback a rate limiting
26. Prompt Registry a lifecycle
27. LLM evaluation datasets a graders
28. Human evaluation a expert feedback
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

Aktuálny authoritative stav sekcie je **24/37 · In progress**. Šiesty authoritative blok aktivuje kapitoly 21–24 a incident `GENAI-SUPPORT-06`. PEFT kapitola oddeľuje base model, tokenizer/chat template, adapter config/weights, target modules, training data a composed serving release; vysvetľuje LoRA low-rank delta, QLoRA boundary, multi-adapter routing, merge/hot-swap, tenant isolation a behavior compatibility. Quantization kapitola modeluje weight/activation/compute/KV precision, PTQ/calibration, outliers, artifact/runtime/kernel/hardware identity, local serving a supply-chain/privacy boundary a oddeľuje memory fit od workload parity. Serving-performance kapitola rozkladá weights, KV cache, activations, paging, prefill/decode, static a continuous batching, admission/backpressure, fairness, parallelism, TTFT/ITL/end-to-end latency, open-loop capacity, autoscaling a OOM recovery. Caching kapitola striktne oddeľuje prefix/KV compute reuse, approximate semantic result reuse a exact response reuse a vyžaduje model/adapter/prompt/corpus/security-scoped keys, authorization pred lookupom, freshness/invalidation, atomic publish, privacy, false-hit telemetry a forbidden-hit tests. Kapitoly 21–24 sú pripravené na repository closeout; reálny adapter training, quantized export/inference, GPU load test, provider/self-hosted prompt cache, semantic/response cache traffic a business outcome neboli vykonané. Sekcia zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. Ďalší blok sú kapitoly 25–28: LLM gateways/routing/fallback/rate limiting, Prompt Registry, LLM evaluation datasets/graders a human evaluation/expert feedback.
