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

## Plánované authoritative poradie

Nasledujúci inventory je schválený plán sekcie. Položka sa zmení na aktívny Markdown link až v pracovnom bloku, ktorý vytvorí a validuje príslušnú kapitolu. Tým sa plánovaný obsah nezamieňa za hotovú dokumentáciu.

5. Inference parameters, sampling a determinism
6. Prompt roles, instructions, context a examples
7. Zero-shot, one-shot a few-shot prompting
8. Prompt templates, variables a versioning
9. Prompt decomposition a chain-of-thought boundaries
10. Structured Outputs a schema validation
11. Function calling a tool calling
12. Model selection a capability/cost trade-offs
13. Model version pinning a compatibility
14. Retrieval-Augmented Generation architecture
15. Chunking, metadata a document processing
16. Vector stores a indexing
17. Retrieval, hybrid search a reranking
18. Context assembly a citation grounding
19. RAG evaluation a retrieval diagnostics
20. Fine-tuning, instruction tuning a preference tuning
21. PEFT, adapters a LoRA
22. Quantization a local inference
23. GPU memory, batching a serving performance
24. Prompt caching, semantic caching a response caching
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

Aktuálny authoritative stav sekcie je **4/37 · In progress**. Prvý authoritative blok aktivuje kapitoly 1–4 a incident `GENAI-SUPPORT-01`. Základná kapitola oddeľuje generative AI, foundation model, LLM a celú application chain a viaže model snapshot, tokenizer, prompt, retrieval, tools, policy a evals do exact request subjectu. Transformer kapitola vysvetľuje encoder/decoder families, token embeddings, positional information, Q/K/V self-attention, masks, feed-forward a residual blocks, logits, autoregressive generation, prefill/decode a KV cache. Tokenization kapitola viaže vocabulary, subword segmentation, special tokens, chat serialization, total context budget, truncation priority, segment manifest, finish reason a token/cost telemetry. Embeddings kapitola oddeľuje vectors, pooling, normalization, cosine/dot-product compatibility, similarity/relevance/identity, ANN index generation, multilingual evaluation, reindexing a access boundaries. Kapitoly 1–4 prešli substantial prose, executable/model surface a subject/evidence/failure/recovery/acceptance gate-om. Reálna inference, provider snapshot verification, tokenizer parity, embedding index build a business outcome neboli vykonané; sekcia zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. Ďalší blok sú kapitoly 5–8: inference parameters/sampling, prompt roles, zero/one/few-shot prompting a prompt templates/versioning.
