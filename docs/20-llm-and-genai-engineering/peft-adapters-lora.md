# PEFT, adapters a LoRA

Parameter-Efficient Fine-Tuning, skrátene PEFT, je skupina adaptačných metód, ktoré nemenia všetky parameters base modelu. Namiesto plného fine-tuningu trénujú menší počet parameters, napríklad low-rank matrices, adapter layers, learned prompts alebo scaling vectors. Výsledkom nie je samostatný „malý model“, ale behavior delta viazaná na konkrétny base model, tokenizer, architecture, target modules, training data a runtime composition.

V incidente `GENAI-SUPPORT-06` tím vytrénoval LoRA adapter pre refund exceptions nad base snapshotom `support-7b-2026-06-10`. Deployment však načítal adapter nad novším snapshotom rovnakej model family. Shapes boli compatible a server sa spustil, ale chat template, tokenizer special tokens a niektoré layer semantics sa zmenili. Model odpovedal plynulo, no zhoršila sa schema adherence a pri policy conflicts začal preferovať staré patterny z tréningových dát. Root cause nebol „pokazený LoRA súbor“, ale chýbajúci composed release subject, base-model digest gate a end-to-end eval po načítaní adaptera.

## 1. Business outcome a boundary

PEFT má zmysel, keď treba adaptovať behavior alebo task performance a plný fine-tuning je príliš nákladný na compute, memory alebo storage. Nie je náhradou za RAG freshness, authorization, tool validation ani deterministic business rules.

```text
adaptation intent
→ governed dataset
→ exact base model
→ PEFT configuration
→ adapter training artifact
→ composed serving release
→ workload eval
→ controlled promotion
```

Training completion, malý adapter checkpoint ani nízka training loss nepreukazujú production outcome.

## 2. Exact adapter subject

Adapter sa identifikuje spolu s base modelom:

```yaml
adapter_release:
  release_id: refund-lora-v7
  method: lora
  base_model:
    repository: internal/support-7b
    revision: 6f1a9d2
    weights_digest: sha256:1c90...
    tokenizer_digest: sha256:ab72...
    chat_template_digest: sha256:7ee4...
  adapter:
    weights_digest: sha256:842d...
    config_digest: sha256:ba55...
    target_modules: [q_proj, k_proj, v_proj, o_proj]
    rank: 16
    alpha: 32
    dropout: 0.05
  dataset_generation: refund-adaptation-2026-08-04
  trainer_release: peft-trainer-v11
  eval_suite: refund-adapter-eval-v8
```

Samotné `adapter_model.safetensors` nestačí. Bez configu a base identity sa nedá bezpečne načítať ani reprodukovať.

## 3. Full fine-tuning verzus PEFT

Full fine-tuning aktualizuje veľkú časť alebo všetky model weights. PEFT ponechá base model prevažne frozen a pridá alebo sprístupní malú trénovateľnú časť.

| Vlastnosť | Full fine-tuning | PEFT |
|---|---|---|
| Trainable parameters | veľká časť alebo všetky | malý subset alebo nové parameters |
| Optimizer state | vysoká memory spotreba | výrazne nižšia |
| Storage per variant | celý model | adapter plus base reference |
| Serving | samostatný model alebo checkpoint | base + adapter composition |
| Capability ceiling | vyššia flexibilita | závisí od metódy, ranku a target modules |
| Operational risk | veľký artifact | compatibility a composition risk |

PEFT je parameter-efficient, nie automaticky data-efficient, quality-equivalent ani operationally simple.

## 4. Adapter metódy

Adapter je všeobecný pojem pre trainable component pridaný k frozen alebo prevažne frozen base modelu. Rôzne metódy menia iné časti computation graphu.

```text
LoRA
→ low-rank delta na vybraných linear projections

IA3 alebo scaling metódy
→ trainable multiplicative vectors

bottleneck adapters
→ malé neural layers vložené medzi pôvodné bloky

prompt/prefix tuning
→ learned virtual tokens alebo prefix states
```

Výber metódy je workload a architecture decision. Názov PEFT nepreukazuje rovnakú kvalitu ani rovnaký serving path.

## 5. Mechanizmus LoRA

LoRA ponechá pôvodnú weight matrix `W` frozen a učí low-rank update:

```text
W' = W + ΔW
ΔW = B · A
```

Ak má `W` rozmery `d_out × d_in`, matrices `A` a `B` používajú rank `r`, ktorý je podstatne menší než plné rozmery. Trainable parameter count je približne:

```text
r × d_in + d_out × r
```

Update sa často škáluje faktorom odvodeným z `alpha / r`. Rank určuje capacity adaptera, ale vyšší rank automaticky neznamená lepší generalization. Target modules, dataset quality, learning rate a base capability sú rovnako dôležité.

## 6. Target modules

LoRA sa môže aplikovať na attention projections, MLP projections alebo širšiu množinu linear layers. Napríklad:

```python
from peft import LoraConfig

config = LoraConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    bias="none",
    task_type="CAUSAL_LM",
)
```

String names sú architecture-specific. Ak target module pattern nič nenájde alebo nájde inú množinu po upgrade library/modelu, training job môže vytvoriť iný subject. Preprocessing report musí vypísať exact matched modules a trainable parameter count.

## 7. Base-model compatibility

Adapter weights sú naviazané na layer names, shapes a learned representation base modelu. Rovnaká family alebo parameter count neznamená compatibility.

Compatibility gate kontroluje:

```text
base repository + immutable revision
weights/config digest
architecture class
layer count a hidden dimensions
tokenizer a special tokens
chat template
rope/context configuration
target module names a shapes
```

Shape-compatible load je iba syntactic gate. Behavior compatibility stále vyžaduje eval.

## 8. Tokenizer a chat template

Training examples sa serializujú cez tokenizer a chat template. Zmena role tokens, end-of-turn markerov alebo BOS/EOS policy môže meniť task, ktorý model vidí.

```text
raw conversation
→ template rendering
→ token IDs
→ labels a loss mask
```

Ak training použil inú template než serving, adapter sa môže naučiť nesprávne boundaries. Manifest preto pinne tokenizer aj template digest a validation kontroluje rendered samples, nie iba raw JSON.

## 9. Dataset a intended adaptation

PEFT nemení pravidlá pre data governance. Dataset potrebuje provenance, license, privacy classification, deduplication, label authority a leakage-safe split.

Adapter training je vhodný na stabilné behavior patterns, napríklad domain terminology, output style, bounded classification alebo tool-selection convention. Mutable policies a často meniace fakty patria do authoritative retrieval alebo deterministic data source.

V incidente boli stale refund examples použité ako behavior labels. Model si ich osvojil aj v prípadoch, kde aktuálny RAG context hovoril opak. Adapter tým zvýšil conflict risk namiesto opravy freshness.

## 10. Rank, alpha a dropout

Rank `r` riadi veľkosť low-rank subspace. `alpha` riadi scaling update a dropout regularizuje adapter path. Ich význam závisí od implementation a target modules.

Hyperparameter search sa hodnotí cez workload eval, nie iba training loss:

```yaml
candidates:
  - rank: 8
    alpha: 16
  - rank: 16
    alpha: 32
  - rank: 32
    alpha: 64
metrics:
  - accepted_case_rate
  - schema_adherence
  - policy_conflict_rate
  - adjacent_capability_regression
  - adapter_memory
```

Vyšší rank zvyšuje trainable parameters, checkpoint size a niekedy serving overhead. Môže tiež overfitnúť malý dataset.

## 11. Training memory

PEFT znižuje memory pre trainable weights, gradients a optimizer state, ale base model, activations, attention states a batch data stále spotrebúvajú memory.

```text
training memory ≈
base weights
+ adapter weights
+ adapter gradients
+ optimizer state
+ activations
+ temporary kernels/buffers
```

Gradient checkpointing, mixed precision a sequence packing menia memory/throughput trade-off. „Trénujeme iba 0,1 % parameters“ neznamená, že training potrebuje iba 0,1 % plnej GPU memory.

## 12. QLoRA boundary

QLoRA kombinuje frozen quantized base model s trainable LoRA adapters. Gradients tečú cez quantized base computations do adapter parameters; base weights sa neaktualizujú ako plný 4-bit fine-tuning.

```text
4-bit frozen base
→ dequantized compute path
→ LoRA trainable delta
→ adapter gradients
```

QLoRA znižuje memory, ale pridáva quantization configuration a kernel/runtime compatibility do training subjectu. QLoRA training artifact sa nemá zamieňať s finálnym quantized serving artifactom; serving môže použiť inú precision a musí byť samostatne evaluovaný.

## 13. Multiple adapters

Jeden base model môže držať viac adapters a prepínať ich podľa route. To znižuje storage, ale rozširuje control-plane risk.

```yaml
adapter_route:
  tenant_policy: eu-support
  base_release: support-7b-v12
  active_adapter: refund-eu-v7
  allowed_adapters:
    - refund-eu-v7
    - general-eu-v5
```

Adapter selection je authorization-sensitive configuration. User input nesmie priamo zvoliť arbitrary adapter path. Trace musí zaznamenať active adapter a fallback reason.

## 14. Adapter stacking a composition

Niektoré runtimes podporujú súčasnú alebo sekvenčnú kompozíciu viacerých adapters. Dve adapters trénované samostatne nemusia byť compositional.

```text
base + language adapter + policy adapter
```

Order, scaling a merge semantics môžu meniť behavior. Každá povolená combination je nový release subject a potrebuje eval. Kombinatorická explózia je dôvod obmedziť supported compositions.

## 15. Merged verzus unmerged adapter

LoRA delta možno niekedy merge-núť do base weights pre jednoduchší serving. Merge vytvára nový full-weight artifact:

```text
base digest + adapter digest + merge implementation
→ merged weights digest
```

Merged artifact už nie je identifikovaný iba pôvodným base modelom. Unmerge nemusí byť bezpečne reverzibilný po ďalších transformáciách alebo quantization. Preto sa zachováva original base a adapter a merge sa vykonáva ako reprodukovateľný build.

Unmerged serving umožňuje rýchle prepínanie adapters, ale môže priniesť runtime overhead, memory pressure a scheduler constraints. Benchmark sa robí na reálnom serving engine.

## 16. Adapter artifact format a supply chain

Adapter package obsahuje weights, config, metadata, license a manifest. Načítanie arbitrary pickle alebo remote code je supply-chain risk.

Platforma preferuje bezpečný tensor format, immutable registry, digest verification a explicitný allowlist loaderov. `trust_remote_code=True` sa nepoužíva ako default convenience flag v production pipeline.

```bash
sha256sum adapter_model.safetensors adapter_config.json
```

Digest check overuje bytes, nie model quality alebo pôvod. Registry musí spájať digest s approved training runom a security scanom.

## 17. Training validation

Pred promotion sa kontroluje:

```text
manifest completeness
→ base compatibility
→ matched target modules
→ finite loss/gradient health
→ checkpoint integrity
→ offline workload eval
→ adjacent capability eval
→ privacy/safety checks
```

Checkpoint, ktorý sa dá načítať, môže byť behaviorálne chybný. Eval používa rovnakú composed serving configuration ako candidate deployment.

## 18. Baseline a ablation

Adapter sa porovnáva minimálne s:

```text
base model + current prompt/RAG
base model + improved prompt/RAG
base model + adapter
```

Ablation ukáže, či gain pochádza z adaptera alebo z inej zmeny. Ak prompt fix dosiahne rovnaký outcome s menším operational burden, PEFT nemusí byť správna voľba.

## 19. Catastrophic a adjacent regression

Frozen base znižuje rozsah weight updates, ale negarantuje zachovanie všetkých capabilities. Adapter môže prebiť behavior v target modules a zhoršiť general instruction following, multilingual output, refusal alebo structured schemas.

Eval preto obsahuje target aj adjacent segments. „Base weights sú frozen“ nie je dôkaz, že effective model behavior ostal zachovaný.

## 20. Serving lifecycle

Serving release sa zostavuje:

```text
load pinned base
→ verify base digest/config
→ load adapter config
→ verify target modules/shapes
→ attach alebo merge adapter
→ activate named adapter
→ warm-up
→ read-back loaded identities
→ smoke/eval traffic
```

Read-back je dôležitý. Control-plane požiadavka „load adapter X“ nepreukazuje, že každý replica worker skutočne obsluhuje X.

## 21. Hot swapping

Hot swap môže znížiť deployment time, ale potrebuje concurrency a cache boundaries. Request nesmie počas generácie zmeniť adapter. Prefix/KV cache entries nemusia byť reusable naprieč adapter identities, pretože effective weights sú iné.

Safe swap používa generation ID, drain alebo atomic worker state a post-swap read-back. Ak runtime tieto guarantees neposkytuje, použije sa immutable replica pool per release.

## 22. Multi-tenant isolation

Per-tenant adapters môžu obsahovať odvodené informácie z tenant dát. Storage, loading, cache a telemetry preto musia zachovať tenant boundary.

```text
tenant identity
→ authorized adapter release
→ isolated cache namespace
→ request execution
→ tenant-scoped logs a outcome
```

Adapter routing iba podľa user-provided tenant name je forbidden. Authorization vychádza z authenticated principal a server-side policy.

## 23. Observability

Training trace zachytáva base revision, dataset generation, PEFT config, matched modules, trainable count, hyperparameters, code/container, seed, checkpoints, metrics a eval verdict.

Runtime trace zachytáva base digest, adapter digest/name, merged/unmerged mode, quantization profile, worker generation, prompt/RAG release, latency, validation a business outcome.

Adapter-level metrics odhaľujú, že rovnaký base model môže mať rozdielnu quality, cache hit rate alebo memory footprint podľa active adaptera.

## 24. Failure hypotheses

Pri regresii sa najprv rekonštruuje composed release, pretože rovnaký adapter digest môže mať odlišný effective behavior nad iným base snapshotom, tokenizerom, chat template alebo target-module mappingom. Shape-compatible load preto nevylučuje identity defect; read-back base a adapter digests, rendered token boundaries a matched modules určí, či sa chyba objavila ešte pred inference.

Ak identity sedí, ďalšia vetva skúma training subject. Stale alebo biased dáta, chybná loss mask, agresívny rank či learning rate a overfitting môžu zlepšiť training metric, ale zhoršiť policy conflicts, structured output alebo adjacent capabilities. Dataset lineage, split, checkpoint metrics a paired eval s base release rozlišujú training defect od application-layer problému.

Serving vetva následne overuje unintended adapter composition, nesprávny merge alebo quantization order, repliku s neaktuálnym adapterom a cache reuse naprieč incompatible adapter generations. First-divergence analysis teda nezačína všeobecným tvrdením „LoRA nefunguje“, ale porovnaním requested, loaded a exercised base/adapter generation a prvého requestu, pri ktorom sa ich behavior rozišiel.

## 25. Containment

Containment vypne adapter route alebo presmeruje traffic na known-good base/full release. Zachová sa failing request subject, base/adapter digests, rendered prompt, output, validation a worker read-back.

Pri tenant-isolation incidente sa zablokuje affected cache a adapter registry scope. Pri podozrení na memorization sa zastaví serving adaptera a aktivuje data/privacy incident proces.

## 26. Recovery

Recovery môže:

```text
opraviť base pinning
opraviť tokenizer/template
znovu vytrénovať adapter z governed datasetu
znížiť rank/update magnitude
zmeniť target modules
opustiť PEFT a opraviť prompt/RAG/business rule
```

Nový candidate dostane nový digest a release ID. Starý artifact sa neprepíše in-place. Po replay a canary sa vykoná second-operation test na odlišnom case segmente a na fresh worker replike.

## 27. Acceptance

Pozitívna acceptance vyžaduje jasný adaptation use case, pinned base/tokenizer/template, governed dataset, explicitnú PEFT konfiguráciu, matched-module evidence, immutable adapter artifact, target aj adjacent evals, secure registry, composed-release read-back, controlled rollout a outcome telemetry.

Recovery acceptance vyžaduje identifikovaný incompatible alebo chybný component, known-good rollback, nový immutable candidate, fresh replay, canary a druhú odlišnú operáciu po obnovení.

Forbidden acceptance je adapter načítaný bez exact base revision, training loss ako quality verdict, frozen base ako dôkaz nulovej regression, shape-compatible load ako behavior compatibility, per-tenant adapter bez authorization boundary alebo LoRA použitá na uloženie mutable policy knowledge.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Fine-tuning, instruction tuning a preference tuning](fine-tuning-instruction-preference-tuning.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Quantization a local inference →](quantization-local-inference.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
