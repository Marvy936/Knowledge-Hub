# Transformer architecture na praktickej úrovni

Transformer je neural architecture, ktorá spracúva token representations pomocou attention, feed-forward vrstiev, residual connections a normalization. Pôvodná architecture používala encoder a decoder pre sequence-to-sequence úlohy. Moderné language models môžu byť encoder-only, decoder-only alebo encoder-decoder. Produkčný LLM engineer nepotrebuje ručne odvodiť každý gradient, ale musí rozumieť toku tokenu, attention maskám, logits, autoregressive generation a KV cache, pretože tieto mechanizmy určujú context, latency, memory a failure modes.

V incidente `GENAI-SUPPORT-01` support assistant používal decoder-only model. Tím zvýšil context limit a očakával, že model „pochopí viac dokumentov“. Retrieval vložil dvakrát viac textu, no relevantný runbook sa ocitol medzi boilerplate sekciami, output latency prudko vzrástla a server začal preťažené requests skracovať. Dashboard ukazoval rovnaký model snapshot, ale application behavior sa zmenil cez sequence length, position, attention workload a truncation. Root cause bol nesprávny mental model: context window sa považovala za databázu a Transformer za beznákladové čítanie celého textu.

## 1. Rodiny Transformerov

Encoder-only model vytvára contextual representations všetkých input tokenov a často sa používa na classification, extraction alebo embeddings. Decoder-only model používa causal mask a generuje ďalší token z predchádzajúceho prefixu. Encoder-decoder model najprv spracuje source sequence encoderom a decoder generuje target sequence s self-attention a cross-attention.

```text
encoder-only: input → contextual vectors
decoder-only: prefix → next-token distribution → repeated generation
encoder-decoder: source encoder → decoder conditioned on source
```

Architecture family je súčasť model subjectu. API label „text model“ nehovorí, či model poskytuje embeddings, generation, bidirectional encoding alebo cross-attention behavior.

## 2. Od textu po hidden states

Tokenizer prevedie text na token IDs. Embedding table mapuje každé ID na vektor. Model pridá alebo aplikuje positional information, pretože attention sama osebe nepozná poradie sekvencie. Výsledkom je matica hidden states s jedným vektorom na pozíciu.

```text
text
→ token IDs
→ token embeddings
→ positional information
→ repeated Transformer blocks
→ final hidden states
→ output projection
→ logits
```

Tokenizer, vocabulary a embedding matrix sú previazané. Token IDs z iného tokenizeru nie sú kompatibilné iba preto, že oba modely pracujú s textom.

## 3. Self-attention ako content-dependent mixing

Pre každý hidden state vzniknú query, key a value projections. Query jednej pozície sa porovná s keys ostatných povolených pozícií. Scaled scores prejdú softmaxom a vytvoria weights, ktorými sa zmiešajú value vectors.

Zjednodušený vzťah je:

```text
Attention(Q, K, V) = softmax(QKᵀ / √dₖ + mask) V
```

Query možno prakticky chápať ako „čo táto pozícia hľadá“, key ako „čo ponúka“ a value ako „akú informáciu prenesie“. Toto je mental model, nie doslovná symbolická databáza. Attention weight sama osebe nie je plné vysvetlenie rozhodnutia modelu.

## 4. Multi-head attention

Multi-head attention vykonáva viac projections paralelne. Rôzne heads môžu zachytávať odlišné relationships alebo position patterns, no jednotlivým heads sa nemá automaticky pripisovať stabilný ľudský význam. Outputs heads sa concatenatujú a premietnu späť do model dimension.

Počet heads, head dimension, grouped-query alebo multi-query varianty ovplyvňujú compute a KV cache. Serving engine musí byť kompatibilný s konkrétnou architecture; generic „Transformer runtime“ nestačí.

## 5. Masky

Decoder-only model používa causal mask: token na pozícii `t` nesmie pri generovaní vidieť budúce tokens. Padding mask bráni modelu používať padding ako content. Application môže používať ďalšie attention alebo sequence boundaries podľa model contractu.

Chybná maska je kritický failure. Training bez správnej causal mask môže leaknúť target; inference s nesprávnym paddingom môže meniť results podľa batch composition. Mask generation patrí do tested model/runtime pathu.

## 6. Feed-forward, residual a normalization

Attention zmieša informácie medzi pozíciami. Position-wise feed-forward network potom transformuje každý position vector nelineárne. Residual connections zachovávajú a kombinujú predchádzajúci signal; normalization stabilizuje training a activation scale.

Transformer block sa opakuje mnohokrát. Exact poradie normalization, activation function, gating a residual variant je súčasť architecture generation. Dva modely s rovnakým parameter countom nemusia mať rovnaký runtime alebo quality behavior.

## 7. Logits a next-token distribution

Final hidden state sa premietne do vocabulary-sized logits. Decoder aplikuje temperature a prípadné sampling filters, potom vyberie token. Token sa pridá do prefixu a cyklus pokračuje.

```text
prefix tokens
→ forward pass
→ logits pre ďalší token
→ decoding rule
→ selected token
→ nový prefix
```

Model počas inference „nenapíše celú odpoveď naraz“. Každý nový token závisí od prefixu vrátane predtým vygenerovaných chýb. Preto sa malá skorá odchýlka môže rozvinúť do výrazne odlišného outputu.

## 8. Training a teacher forcing

Pri autoregressive trainingu model typicky predikuje nasledujúce tokens pre veľa pozícií paralelne, pretože ground-truth prefix je známy. Loss porovná predicted distribution s target tokenom. Inference je sekvenčná cez generated prefix.

Tento rozdiel vysvetľuje, prečo training môže využiť vysokú paralelizáciu, ale generation latency rastie s počtom output tokens. Throughput a latency sa preto merajú oddelene pre prefill a decode.

## 9. Prefill a decode

Prefill spracuje celý input prompt a vytvorí hidden/KV state. Decode pridáva output tokens postupne. Dlhý input zvyšuje prefill compute a memory; dlhý output predlžuje sekvenčný decode.

```text
input tokens → prefill → KV cache
KV cache + last token → decode token 1
updated cache → decode token 2
...
```

Time to first token a inter-token latency sú odlišné metrics. Average request latency môže skryť prefill bottleneck alebo pomalý decode.

## 10. KV cache

Pri autoregressive generation by opakovaný výpočet keys a values všetkých minulých tokens bol drahý. KV cache ich uchováva pre každú layer a aktívnu sequence. Cache memory rastie s layers, sequence length, batch/concurrency a KV head configuration.

KV cache nie je application memory. Existuje iba pre konkrétnu inference sequence a runtime. Reuse medzi requests potrebuje explicitnú prompt-prefix caching semantics a privacy isolation.

Memory pressure môže spôsobiť eviction, nižšiu concurrency, OOM alebo request rejection. Serving capacity sa teda neurčuje iba veľkosťou weights.

## 11. Context position a long-context limits

Transformer môže technicky prijať dlhšiu sequence, ale quality nemusí byť rovnomerná pre všetky pozície a tasky. Long-context extension, positional encoding a training distribution ovplyvňujú využiteľnosť. „Zmestí sa do limitu“ nie je ekvivalent „model spoľahlivo použije každú informáciu“.

Retrieval a context assembly musia prioritizovať relevantný, authoritative a nekonfliktný context. Dvojnásobný context môže zhoršiť signal-to-noise, latency a cost.

## 12. Minimal attention illustration

Nasledujúci kód ilustruje shapes, nie production Transformer:

```python
import math
import torch

def scaled_dot_product_attention(
    query: torch.Tensor,
    key: torch.Tensor,
    value: torch.Tensor,
    mask: torch.Tensor | None = None,
) -> torch.Tensor:
    scores = query @ key.transpose(-2, -1)
    scores = scores / math.sqrt(query.shape[-1])

    if mask is not None:
        scores = scores.masked_fill(~mask, float("-inf"))

    weights = torch.softmax(scores, dim=-1)
    return weights @ value
```

Production implementation rieši batching, precision, optimized kernels, distributed execution, cache layout a numerical stability. Výsledok tohto helpera nie je parity test konkrétneho modelu.

## 13. Numerical a runtime boundaries

Mixed precision, quantization, kernel selection, tensor parallelism a hardware môžu meniť latency, memory a niekedy numerický output. Rovnaké weights s iným serving engineom sú nová runtime generation.

Deterministic seed nepokrýva provider-side batching, non-deterministic kernels ani model update. Application eval musí sledovať model aj runtime identity.

## 14. Failure hypotheses

Pomalý request môže byť dlhý prefill, output decode, KV cache pressure, batching wait, network alebo tool latency. Zlá odpoveď môže byť tokenizer/context assembly, position dilution, wrong mask/runtime, model limitation alebo decoding.

Attention visualization nie je root-cause proof. Diagnosis používa token counts, prompt segments, truncation, prefill/decode metrics, loaded model/runtime fingerprint a controlled ablation contextu.

## 15. Recovery a acceptance

Containment zníži context, output budget alebo concurrency, vypne problematický long-context path a route-ne kritický task na known-good release. Recovery obnoví exact model/tokenizer/runtime a validated context assembly.

Pozitívna acceptance vyžaduje správny architecture mental model, token-to-logit flow, causal masking, prefill/decode a KV cache capacity evidence. Forbidden acceptance je parameter count, context limit alebo attention heatmap ako dôkaz correctness.

Second-operation test opakuje golden requests s rovnakým subjectom a potom kontrolovane mení iba context position alebo length. Quality a latency zmena musí byť merateľná a vysvetliteľná, nie pripísaná neurčitému „model sa rozhodol“.
