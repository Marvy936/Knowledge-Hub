# Inference parameters, sampling a determinism

LLM inference nie je iba zavolanie modelu s textom. Výstup vzniká zo sekvencie rozhodnutí nad token probability distribution a každé rozhodnutie môže zmeniť obsah, dĺžku, latenciu, cenu aj reprodukovateľnosť odpovede. Produkčný systém preto musí versionovať nielen model a prompt, ale aj decoding strategy, sampling parameters, stopping rules, seed, runtime generation a spôsob dávkovania requestov.

V incidente `GENAI-SUPPORT-02` support assistant používal rovnaký model alias a rovnaký prompt ID, no gateway po optimalizácii zmenila `do_sample=false` na nucleus sampling s `temperature=0.7` a `top_p=0.9`. Seed sa nelogoval, jedna replika používala novšiu runtime image a fallback provider ignoroval časť parametrov. Tím videl rovnaký HTTP request a podobnú fluent odpoveď, ale nevedel rozlíšiť, či regresiu spôsobila zmena promptu, model snapshotu, decoding configu alebo backendu. Root cause nebola „náhodnosť modelu“, ale neúplný inference subject.

## 1. Exact inference subject

Reprodukovateľná inference operácia potrebuje presne identifikovať všetky vstupy do token-generation procesu. Model name bez snapshotu nestačí a parameter `temperature` bez informácie, či sa vôbec používa sampling, je neúplný.

```yaml
inference_subject:
  request_id: req-support-20260803-0042
  model_provider: internal-gateway
  model_family: support-llm
  model_snapshot: support-llm-2026-07-28
  weights_digest: sha256:model...
  tokenizer_digest: sha256:tokenizer...
  chat_template_digest: sha256:chat-template...
  prompt_render_digest: sha256:rendered-messages...
  decoding:
    strategy: multinomial-sampling
    do_sample: true
    temperature: 0.7
    top_p: 0.9
    top_k: 0
    repetition_penalty: 1.0
    max_new_tokens: 320
    stop_generation: support-stop-v3
    seed: 481516
  runtime:
    image_digest: sha256:runtime...
    engine: vllm
    engine_version: 0.x-pinned
    tensor_parallel_size: 2
    quantization: none
    batch_generation: batch-9217
```

Takýto manifest nie je záruka rovnakého outputu. Je to minimálny predmet porovnania, vďaka ktorému sa dá vysvetliť, čo bolo rovnaké a čo sa zmenilo.

## 2. Od logits k ďalšiemu tokenu

Decoder vytvorí pre každý krok vektor logits nad vocabulary. Softmax ich prevedie na probability distribution. Ak sa používa greedy decoding, vyberie sa token s najvyššou pravdepodobnosťou. Pri samplingu sa token vyberie z upravenej distribúcie.

Temperature škáluje logits pred softmaxom:

```text
p_i(T) = softmax(z_i / T)
```

Nižšia hodnota zvýrazní dominantné tokeny a distribúcia bude ostrejšia. Vyššia hodnota distribúciu sploští a zvýši šancu menej pravdepodobných tokenov. Temperature nemení znalosti modelu ani nepridáva kreativitu ako samostatnú schopnosť; mení iba pravdepodobnostný výber z aktuálnych logits.

Hodnota blízka nule sa v implementáciách často správa ako greedy alebo veľmi ostrý sampling, ale presná hranica je provider-specific. Produkčný kontrakt preto používa explicitnú strategy a nie iba neurčitý parameter `temperature: 0`.

## 3. Greedy decoding a jeho hranice

Greedy decoding vyberá v každom kroku lokálne najpravdepodobnejší token. Je jednoduchý, rýchly a pri rovnakom runtime býva stabilnejší než sampling. Neznamená však globálne najlepšiu sekvenciu. Skoré lokálne rozhodnutie môže viesť k repetícii, generickej odpovedi alebo vetve, z ktorej sa model už nevie vrátiť.

Greedy output tiež nie je automaticky deterministický naprieč všetkými backendmi. Rozdiely vo floating-point redukciách, kernel implementácii, kvantizácii, tensor parallelism, batch composition alebo tie-breaking pri takmer rovnakých logits môžu zmeniť prvý token a následne celú autoregresívnu sekvenciu.

Pre classification-like úlohy, exact extraction alebo stabilné structured outputy je greedy režim často vhodný baseline. Acceptance sa však stále opiera o schema validation a eval dataset, nie o predpoklad, že „temperature nula znamená správne“.

## 4. Top-k a nucleus sampling

Top-k sampling ponechá v každom kroku iba `k` tokenov s najvyššou pravdepodobnosťou a ostatné odstráni. Jeho candidate set má pevnú veľkosť, aj keď je distribúcia raz veľmi ostrá a inokedy plochá.

Top-p alebo nucleus sampling ponechá najmenšiu množinu tokenov, ktorej kumulatívna pravdepodobnosť dosiahne zvolený prah. Candidate set sa preto dynamicky mení. Pri istej predikcii môže obsahovať málo tokenov; pri neistej predikcii viac.

```text
raw logits
→ optional penalties
→ temperature scaling
→ top-k / top-p / min-p filtering
→ renormalization
→ random draw
```

Poradie transformácií a ich exact implementácia sú súčasťou runtime contractu. Dve knižnice môžu používať rovnaké názvy parametrov, ale odlišný default, clipping alebo order of operations. Gateway musí overiť, ktoré parametre target provider skutočne prijal.

Kombinovanie veľmi nízkeho `top_p`, malého `top_k` a nízkej temperature môže distribúciu zúžiť natoľko, že systém stratí užitočnú variabilitu. Naopak vysoká temperature bez truncation môže pripustiť dlhý tail nevhodných tokenov. Parametre sa neoptimalizujú izolovane, ale na eval datasete pre konkrétny outcome.

## 5. Penalties, constraints a stopping rules

Repetition alebo frequency penalties menia logits podľa už vygenerovaných tokenov. Môžu obmedziť repetíciu, ale zároveň poškodiť presné citácie, kód, mená alebo opakovanie povinných polí. `no_repeat_ngram`, bad-word lists a forced tokens sú ešte silnejšie constraints a musia byť testované na povolených aj zakázaných prípadoch.

Stopping rule môže byť EOS token, provider stop sequence, schema-complete condition, `max_new_tokens`, deadline alebo cancellation. Každý dôvod ukončenia má odlišnú interpretáciu:

```text
stop/eos       → model alebo stop matcher ukončil sekvenciu
length         → output budget bol vyčerpaný
content_filter → provider/policy prerušil generovanie
timeout        → aplikačný deadline prerušil request
cancelled      → klient alebo orchestration ukončili operáciu
```

Truncated output sa nesmie spracovať ako kompletná odpoveď iba preto, že transport vrátil HTTP 200. Parser a business workflow musia kontrolovať finish reason, schema completeness a povinné evidence fields.

## 6. Maximum output a total budget

`max_new_tokens` obmedzuje output, nie celkový context. Aplikácia musí samostatne vypočítať input tokens, reserved output, tool alebo structured-output overhead a provider-specific limit.

Príliš veľký output budget zvyšuje latency a cost a môže podporiť zbytočné pokračovanie. Príliš malý budget spôsobí truncation, ktorú sampling parametre nevyriešia. Output limit preto patrí do task contractu a evalov: krátka intent classification, JSON extraction a dlhý report nemajú rovnakú konfiguráciu.

Pri streaming odpovedi používateľ môže začať konzumovať text skôr, než systém pozná konečný finish reason. Side effect sa nesmie spustiť z čiastočného textu, pokiaľ protokol nemá explicitnú incremental validation a commit boundary.

## 7. Beam search, best-of a viac kandidátov

Beam search udržiava viac sekvenčných kandidátov a hľadá vysoké cumulative scores. Je užitočný najmä pri niektorých constrained alebo sequence-to-sequence úlohách, no pre open-ended chat môže podporovať generické a podobné výstupy. Beam count, length normalization, early stopping a diversity parameters tvoria vlastnú decoding generation.

Best-of alebo generovanie viacerých sampled kandidátov pridáva ďalší selection model. Ak sa z piatich odpovedí vyberie jedna pomocou reward modelu, rule-based gradera alebo LLM judge, authoritative output subject zahŕňa všetkých kandidátov, ich seeds, selector generation a selection verdict. Cena a latency sa počítajú za celý proces, nie iba za vybraný text.

Výber najlepšie znejúcej odpovede bez uloženia rejected candidates vytvára survivorship bias a sťažuje RCA.

## 8. Seed a reprodukovateľnosť

Seed inicializuje pseudonáhodný generátor pre sampling, ak ho backend podporuje. Rovnaký seed môže pomôcť pri porovnaní prompt variants, ale nie je kryptografický ani univerzálny replay token.

```text
same seed
+ same weights
+ same tokenizer/template
+ same input tokens
+ same decoding implementation
+ same runtime/kernels
+ same execution shape
≈ stronger reproducibility
```

Zmena ktoréhokoľvek člena môže viesť k inému outputu. Hosted provider môže navyše meniť serving stack alebo routing bez toho, aby odhalil všetky interné detaily. Preto sa rozlišuje exact replay, bounded reproducibility a statistical stability.

Exact replay znamená byte-identical output v kontrolovanom prostredí. Bounded reproducibility znamená, že variácia zostáva v povolenom schema a quality envelope. Statistical stability znamená, že agregované výsledky nad opakovaniami a datasetom zostávajú v tolerancii.

## 9. Determinism nie je correctness

Deterministicky nesprávna odpoveď je iba stabilná chyba. Sampling s vyššou variabilitou môže občas nájsť lepšiu odpoveď, ale zároveň zväčšuje failure surface. Správny cieľ sa definuje cez outcome metrics: schema validity, factuality, groundedness, task success, safety, latency a cost.

Pre support assistant môže byť rozumný contract napríklad:

```yaml
acceptance:
  schema_valid_rate: ">= 99.9%"
  unsupported_policy_claim_rate: "<= 0.1%"
  exact_policy_id_present: "= 100%"
  answer_variance:
    repeated_runs: 20
    allowed_intent_changes: 0
    allowed_wording_variation: true
  p95_latency_ms: "<= 1800"
  cost_per_resolved_ticket_eur: "<= 0.03"
```

Tento contract povoľuje wording variance, ale zakazuje zmenu intentu alebo použitej policy identity.

## 10. Provider gateway a parameter translation

Multi-provider gateway často mapuje jednotný request na rozdielne API. Nie každý provider podporuje seed, top-k, min-p, logprobs, penalties alebo rovnaký stop behavior. Ignorovaný parameter je zmena subjectu, nie neškodný detail.

Gateway preto vytvára dva manifesty:

```text
requested decoding config
→ provider translation
→ effective accepted config
→ response metadata
```

Effective config sa číta späť z provider response alebo gateway adaptera. Ak parameter nie je podporovaný, adapter musí failnúť alebo explicitne označiť downgrade podľa policy. Tiché odstránenie `seed` alebo `response_format` je forbidden behavior.

Fallback provider sa nepovažuje za ekvivalentný iba preto, že prijíma rovnaký text. Potrebuje samostatný eval, compatibility matrix a traffic policy.

## 11. Batch composition a serving runtime

Continuous batching zvyšuje throughput, ale mení execution timing a niekedy numerickú cestu. Tensor parallelism, speculative decoding, quantization a fused kernels môžu ovplyvniť logits alebo order of completion. Pri incidentoch sa preto loguje batch generation, replica/runtime fingerprint a serving optimization flags.

Speculative decoding používa draft model na návrh tokenov a target model ich verifikuje. Pri korektnej implementácii má zachovať cieľovú distribúciu, ale je stále novou runtime generation s vlastnými failure modes, memory profile a telemetry.

Výkonová optimalizácia sa nesmie nasadiť iba na základe rovnakého priemerného textu v niekoľkých manuálnych promptoch. Potrebuje parity evaluation a repeated-run analysis.

## 12. Observability bez vysokokardinalitného chaosu

Metrics používajú bounded labels, napríklad model snapshot, decoding policy generation, result class a route. Request ID, seed alebo prompt digest patria do traces/logs, nie do neobmedzených metric labels.

Užitočná telemetry obsahuje input/output tokens, finish reason, time-to-first-token, inter-token latency, total latency, route, retries, fallback, effective decoding policy a output validation result. Logovanie raw promptu alebo outputu sa riadi privacy a retention policy.

Variabilita sa monitoruje na stable eval probes alebo sampled request groups. Porovnávanie dvoch náhodných production odpovedí bez rovnakého subjectu nie je dôkaz regresie.

## 13. Failure hypotheses a containment

Ak sa odpovede začnú meniť, prvá hypotéza nemá byť „model je náhodný“. Najprv sa porovná model snapshot, prompt render, tokenizer/chat template, effective decoding config, route, runtime image, batch generation a finish reason. Následne sa skúma, či sa zmenila population alebo eval dataset.

Containment môže prepnúť citlivý task na schválenú greedy policy, vypnúť fallback, znížiť traffic novej runtime generation alebo zastaviť side effects pri incomplete outputoch. Nemá však prepísať všetky parametre naraz pred zachytením evidence.

Unknown provider outcome sa rieši request correlation a read-before-retry. Opakovanie sampled requestu s novým seedom nie je retry rovnakého generation subjectu; je to nový attempt s novým možným outputom.

## 14. Recovery a acceptance

Component recovery potvrdzuje, že gateway rešpektuje requested parameters, runtime načíta správny model/template a finish reasons sa mapujú správne. Journey recovery vykoná rovnaký eval dataset cez schválenú decoding policy, uloží effective config a overí output validators. Business recovery sleduje správne support rozhodnutie a mature ticket outcome.

Pozitívna acceptance vyžaduje pinned model/runtime, explicitnú decoding strategy, effective parameter read-back, output a finish validation, repeated-run test a eval výsledky nad relevantnou population. Recovery acceptance vyžaduje druhú operáciu s rovnakým manifestom a samostatný alternate-scenario test, napríklad dlhý output alebo fallback route.

Forbidden acceptance je tvrdenie „temperature je nula, teda deterministické“, seed bez runtime identity, HTTP 200 bez finish reason, manuálne porovnanie dvoch odpovedí alebo tichý provider downgrade. Sampling parameter je súčasť inference contractu, nie estetický slider.
