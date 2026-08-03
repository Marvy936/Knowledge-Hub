# Tokens, tokenization a context window

LLM nečíta text ako sequence slov. Tokenizer normalizuje a segmentuje input na token IDs z pevného vocabulary; model pracuje s týmito IDs a ich embeddings. Token môže byť celé slovo, časť slova, znak, byte sequence, whitespace pattern alebo special control symbol. Tokenization je súčasť modelu a application contractu, pretože mení dĺžku requestu, hranice textu, cost, truncation aj model behavior.

V incidente `GENAI-SUPPORT-01` bol slovenský support ticket v UI odhadnutý ako 3 000 „slov“, takže aplikácia pridala viacero runbookov a conversation history. Provider tokenizer však rozdelil diakritiku, paths, UUIDs a log snippets na výrazne viac tokens. Server prekročil input budget, middleware ticho odstránil najstaršiu system-owned context sekciu a model odpovedal bez policy constraints. Tím sledoval characters a words, nie exact tokenizer output a context assembly manifest.

## 1. Tokenizer je model dependency

Vocabulary priraďuje token stringom alebo byte sequences integer IDs. Embedding matrix modelu očakáva presne tieto IDs. Zmena tokenizer vocabulary, normalization, pre-tokenization alebo special tokens je compatibility-breaking zmena, ak nie je súčasťou spoločného model release.

```text
raw text
→ normalization
→ segmentation
→ token pieces
→ token IDs
→ model embeddings
```

Encode/decode nemusia byť intuitívne zrkadlá. Whitespace, Unicode normalization, invalid bytes alebo special tokens môžu mať vlastnú semantics. Debugging musí zobrazovať IDs aj decoded pieces pre exact tokenizer generation.

## 2. Prečo subword tokenization

Word-level vocabulary nevie efektívne pokryť všetky words, inflections, names, code a languages. Character-level sequence je univerzálnejšia, ale dlhá. Subword methods hľadajú kompromis: časté patterns majú vlastné tokens, zriedkavé words sa skladajú z menších pieces.

BPE-like tokenizers používajú learned merge rules; unigram model vyberá segmentation podľa learned token probabilities. SentencePiece ukazuje language-independent training priamo z raw textu. Moderné systems môžu používať byte-level alebo hybrid variants, ale praktický contract zostáva rovnaký: konkrétne text → konkrétna sequence IDs.

## 3. Token count nie je word count

Token/word ratio závisí od jazyka, domainu a formátu. Code, JSON, base64, hashes, URLs, logs a rare names môžu byť token-expensive. Rovnaký význam v dvoch jazykoch môže mať rozdielny token count, čo mení cost a available context.

Aplikácia nesmie budgetovať podľa characters alebo UI word countera. Používa tokenizer kompatibilný s exact model snapshotom alebo provider-authoritative count API.

## 4. Special tokens a chat serialization

Chat API roles sa pred inference serializujú do model-specific sequence s control tokens, separators alebo templates. User-visible text preto nie je celý prompt. System, developer, tool a assistant messages, tool schemas a hidden serialization overhead spotrebúvajú context.

```text
role messages + tool definitions + provider template
→ serialized token sequence
→ model
```

Chat template je behavior-changing generation. Manuálne skladanie special tokens bez model contractu môže spôsobiť role confusion alebo duplicate markers.

## 5. Context window ako total sequence budget

Context window je maximálny alebo podporovaný sequence budget model/runtime-u. Typicky zahŕňa input tokens a generované output tokens; presný provider contract môže rezervovať ďalší overhead. Aplikácia musí počítať s output budgetom pred odoslaním requestu.

```text
system/instructions
+ conversation
+ retrieved context
+ tool schemas/results
+ user input
+ reserved output
≤ effective context budget
```

Marketingový maximum nie je automaticky effective application budget. Provider limits, model snapshot, endpoint config a latency/cost policy môžu byť prísnejšie.

## 6. Truncation je policy decision

Keď input prekročí budget, aplikácia môže rejectnúť request, zhrnúť history, odstrániť low-priority context alebo chunkovať task. Tiché odrezanie „zľava“ alebo „sprava“ môže odstrániť system instruction, aktuálnu otázku, citation alebo schema.

Truncation policy musí definovať priority a forbidden removals. System a authorization constraints sa nesmú obetovať pre ďalší retrieved document. Request trace uloží pre-tokenization segments, token counts, retained/removed segment IDs a final prompt digest.

## 7. Praktické meranie tokenizerom

Pri open modeloch možno count overiť lokálne s pinned tokenizerom:

```python
from transformers import AutoTokenizer

MODEL_ID = "org/model-snapshot"
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_ID,
    revision="exact-commit-or-tag",
)

text = "Incident INC-184: služba vrátila HTTP 503."
encoded = tokenizer(
    text,
    add_special_tokens=True,
    return_length=True,
)

print(encoded["input_ids"])
print(encoded["length"])
print(tokenizer.convert_ids_to_tokens(encoded["input_ids"]))
```

Pre hosted model je lokálna knižnica platná iba vtedy, ak provider garantuje kompatibilitu. Inak sa používa provider count endpoint alebo response usage metadata a pridáva safety margin.

## 8. Padding, batching a masks

Batch requests majú rôzne lengths. Runtime ich môže paddingovať na spoločnú dĺžku a používa attention mask, aby padding nebol content. Padding side a special-token policy musia zodpovedať modelu.

Padding zvyšuje wasted compute. Length-aware batching môže zvýšiť throughput, ale nesmie miešať tenant data v cache alebo logs. `pad_to_multiple_of` môže pomôcť hardware kernels, no mení runtime cost, nie semantic token count.

## 9. Context assembly a segment manifest

Finálny prompt sa skladá z named segments, nie jedného anonymného stringu.

```yaml
context_assembly:
  tokenizer: tokenizer-x-v3
  effective_budget: 16384
  reserved_output: 800
  segments:
    - id: system-policy-v5
      priority: required
      tokens: 640
    - id: conversation-summary-884
      priority: high
      tokens: 1150
    - id: runbook-auth-2026-08-01
      priority: high
      tokens: 2100
    - id: retrieved-incident-771
      priority: medium
      tokens: 920
```

Manifest umožní vysvetliť, prečo sa odpoveď zmenila. Bez neho sa „rovnaký prompt“ často ukáže ako odlišná serialization alebo truncation.

## 10. Long documents a chunking boundary

Dokument väčší než context sa musí rozdeliť, vyhľadať alebo hierarchicky spracovať. Chunk boundaries môžu oddeliť heading od body, definition od exception alebo code od explanation. Overlap znižuje boundary loss, ale zvyšuje duplication a token cost.

Chunking patrí do retrieval pipeline a bude rozpracované neskôr. V tejto kapitole je dôležité, že tokenizer-aware chunk size sa meria tokens, nie znaky, a že source offsets sa zachovávajú pre citations.

## 11. Output token budget a stop behavior

`max_output_tokens` je limit, nie target. Model môže skončiť stop tokenom, stop sequence, refusal, tool callom alebo length limitom. Length-truncated JSON alebo command je invalid output class, nie úspešná odpoveď.

Aplikácia sleduje finish reason a pri structured outpute validuje complete schema. Blind continuation request môže duplikovať alebo protirečiť predchádzajúcemu outputu; continuation má explicitný contract.

## 12. Token usage, latency a cost

Input tokens ovplyvňujú prefill; output tokens ovplyvňujú sequential decode. Price a capacity sa môžu líšiť podľa input/output, cached prefixu, modality alebo provider tier. Usage metadata sa viaže na request subject a result class.

Cost per request bez usefulness denominatora je slabá metrika. Lacná odpoveď po truncation môže byť drahšia na support outcome, ak vedie k nesprávnemu zásahu.

## 13. Security boundaries

Tokenizer môže odhaliť, že visually similar Unicode text má iné IDs. Normalization a confusable characters sú relevantné pre prompt injection, identifier matching a policy filters. Security control nesmie porovnávať iba rendered text, ak downstream model pracuje s odlišnou normalization.

Token limits sa môžu zneužiť na context flooding: attacker vloží dlhý obsah, ktorý vytlačí trusted instructions alebo evidence. Priority-aware assembly a hard required segments sú containment.

## 14. Failure hypotheses

Context-limit error môže byť user text, tools, history, retrieval duplication, chat template overhead alebo nesprávny tokenizer estimate. Zmena odpovede môže byť truncation, special-token template, tokenizer snapshot alebo segment order.

Troubleshooting uloží raw segment identities, exact encoded length a final serialized prompt. Reprodukcia s približným textom nie je rovnaký request.

## 15. Recovery a acceptance

Containment zníži retrieved count, vypne nebounded tool schemas, zachová required instructions a rejectne request, ktorý nemožno bezpečne zostaviť. Recovery pinne tokenizer/template, opraví token accounting a replayne golden multilingual/code/log cases.

Pozitívna acceptance vyžaduje exact tokenizer generation, token-aware budgets, explicit truncation, output reservation, finish-reason handling a traceable segment manifest. Forbidden acceptance je word count, advertised context number alebo HTTP success po odrezanom outpute.

Second-operation test zakóduje rovnaké segments rovnakým tokenizerom a očakáva rovnaké IDs/digest. Potom zmení tokenizer alebo jeden segment a overí, že application subject a eval result vytvoria novú generation.
