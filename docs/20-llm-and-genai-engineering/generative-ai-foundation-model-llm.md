# Generative AI, foundation model a large language model

Generative AI, foundation model a large language model nie sú synonymá. Generative AI pomenúva schopnosť systému vytvárať nový obsah alebo štruktúrovaný výstup. Foundation model pomenúva model natrénovaný na širokých dátach vo veľkom rozsahu, ktorý sa dá adaptovať na mnoho downstream úloh. Large language model je foundation model alebo iný veľký model orientovaný primárne na jazykové sekvencie. Produkčná aplikácia je ešte širší systém: obsahuje model, tokenizer, prompt, retrieval, tools, policies, storage, identity, telemetry a business workflow.

V incidente `GENAI-SUPPORT-01` interný support assistant začal po „upgrade modelu“ poskytovať iné odpovede na rovnaké tickety. Tím poznal iba marketingový model name. Nevedel, či provider zmenil snapshot, tokenizer, system instructions, retrieval corpus alebo safety policy. Offline demo stále vyzeralo dobre, no assistant začal spájať podobné, ale odlišné incidenty a vytváral presvedčivé neexistujúce runbook kroky. Root cause nebol jeden chybný prompt. Chýbal exact application subject a rozlíšenie medzi schopnosťou generovať text, vlastnosťami foundation modelu a autoritou produkčnej knowledge aplikácie.

## 1. Tri rozdielne pojmy

Generative model sa učí distribúciu alebo transformačné pravidlo, z ktorého vie vytvárať nové samples. Môže generovať text, obraz, zvuk, video, kód, molekuly alebo kombináciu modalít. Nie každý generative model je foundation model; malý model trénovaný na jednej úlohe môže byť generatívny, ale nemá širokú downstream adaptabilitu.

Foundation model je široko predtrénovaný základ, ktorý sa adaptuje promptingom, retrievalom, fine-tuningom alebo ďalšími vrstvami. Jeho centralita prináša leverage aj homogenization risk: chyba, bias alebo zlá assumption základného modelu sa môže preniesť do mnohých aplikácií.

Large language model pracuje s jazykovým alebo jazykovo-multimodálnym token streamom a predikuje ďalšie alebo chýbajúce tokens podľa training objective. „Large“ nie je stabilná technická hranica. Pre platformu je dôležitejšia architecture, tokenizer, weights generation, context limit, modality, training/adaptation a inference contract než marketingové označenie.

## 2. Model nie je aplikácia

LLM API prijme input a vráti output, ale business outcome vytvára celá application chain.

```text
user alebo event
→ identity a authorization
→ instructions a prompt assembly
→ retrieval alebo tools
→ tokenizer a model inference
→ structured parsing a policy validation
→ side effect alebo user response
→ feedback a mature outcome
```

Model nemá automatickú authority nad firemnými faktami, aktuálnym stavom alebo povolením vykonať side effect. Retrieval môže priniesť authoritative dokument, tool môže prečítať current state a policy môže povoliť action. Model iba transformuje dostupný context podľa naučených patternov a runtime instructions.

Preto sa „model odpovedal správne“ oddeľuje od „systém použil správny zdroj“, „výstup prešiel contractom“, „action bola autorizovaná“ a „používateľský problém bol vyriešený“.

## 3. Training, adaptation a inference

Foundation model lifecycle má tri odlišné vrstvy. Pretraining vytvára všeobecné weights z rozsiahlych dát a objective. Adaptation mení behavior fine-tuningom, preference tuningom, adapters alebo system-level instructions. Inference používa konkrétnu weights a serving generation na vytvorenie outputu pre jeden request.

```text
pretraining data + objective + architecture
→ base weights
→ adaptation data/policy
→ adapted model generation
→ tokenizer + prompt + runtime parameters
→ output tokens
```

Provider-managed model môže skryť časti tohto lifecycle. Platforma preto zaznamená všetky identity, ktoré provider sprístupňuje: exact model/snapshot identifier, API version, region, deployment, tokenizer alebo tokenizer family, feature flags a response metadata. Ak exact weights nie sú viditeľné, táto neistota sa nesmie zamaskovať neurčitým model name.

## 4. Probabilistická generácia

Autoregressive LLM vytvára distribúciu pravdepodobností pre ďalší token. Decoder potom vyberá token greedy výberom alebo samplingom. Aj pri nízkej temperature nie je model databáza, theorem prover ani deterministic business rule engine.

Pravdepodobný text môže byť nepravdivý. Fluency je vlastnosť learned distribution, nie evidence. Model môže správne reprodukovať bežný pattern a zároveň vymyslieť konkrétny hostname, command flag alebo incident ID, ak v contexte chýba authoritative hodnota.

Determinism má viac vrstiev. Rovnaké parameters nemusia garantovať byte-identický output pri provider updates, distributed numerical differences alebo backend changes. Reproducibility preto používa snapshot, seed tam, kde je podporovaný, tokenizer, prompt digest a recorded response; nespolieha sa na temperature `0` ako absolútnu záruku.

## 5. Exact application subject

Produkčný request potrebuje manifest, ktorý viaže všetky behavior-changing generácie.

```yaml
request_subject:
  application_release: support-assistant-2026-08-03.4
  model_provider: provider-a
  model_snapshot: llm-x-2026-07-15
  tokenizer_generation: tokenizer-x-v3
  system_prompt_digest: sha256:...
  prompt_template_digest: sha256:...
  retrieval_corpus: support-kb-2026-08-02
  retrieval_policy: hybrid-rerank-v7
  tool_schema_digest: sha256:...
  policy_generation: support-safety-v5
  inference_parameters:
    temperature: 0.2
    max_output_tokens: 700
```

User text samotný nie je complete subject. Rovnaká veta s iným system promptom, corpusom, tool schema alebo model snapshotom je iná operation. Manifest sa viaže na trace, eval result a production response.

## 6. Capabilities a limitations

Foundation model môže sumarizovať, transformovať, klasifikovať, extrahovať, generovať a kombinovať patterny naprieč domainami. Schopnosť sa však testuje na konkrétnom task distribution a contracte. Benchmark score nie je univerzálny capability flag.

Limity vznikajú z training data, objective, context, architecture, inference budget a application designu. Model môže mať stale knowledge, slabý niche coverage, nepresnú arithmetic, position sensitivity, language disparity alebo náchylnosť na prompt injection. Aplikácia tieto limity niekedy zmierni retrievalom, tools a validation, ale nemôže ich vyhlásiť za odstránené bez eval evidence.

## 7. Foundation model risk propagation

Central model dependency vytvára shared blast radius. Provider update môže zmeniť latency, refusals, tokenization, output style alebo tool-call behavior vo viacerých produktoch. Interný model môže prenášať training-data bias alebo unsafe memorization do všetkých downstream adapters.

Platforma preto udržiava model inventory, intended use, risk class, owner, provider terms, data controls, eval suites a rollback/fallback path. Model selection je governance decision nad application subjectom, nie osobná preferencia developera.

## 8. Open, closed a hosted boundaries

Open weights umožňujú väčšiu kontrolu nad deploymentom, quantization a inspection, ale neznamenajú automaticky otvorené training data, bezpečný artifact alebo lacnú prevádzku. Hosted model prenáša časť operations na providera, ale pridáva vendor API, retention, region, rate limit a hidden-update boundary.

Self-hosting presúva responsibility za GPU capacity, serving security, patches, model license, telemetry a recovery na platform team. Hosted API success presúva iba inference execution; application correctness a data governance zostávajú na organizácii.

## 9. Evaluation boundary

Model eval, application eval a business eval sú rozdielne. Model eval meria capability weights/snapshotu na datasete. Application eval zahŕňa prompt, retrieval, tools, parsing a policy. Business eval meria vyriešený ticket, správny action alebo inú mature outcome metriku.

```text
model answer quality
≠ grounded application response
≠ authorized action
≠ resolved support case
```

Promotion musí používať application-level dataset s reálnymi failure classes. Jedna ručne vybraná konverzácia alebo provider benchmark nie je acceptance.

## 10. Failure hypotheses

Ak sa output zmení, competing hypotheses zahŕňajú model snapshot, tokenizer, prompt assembly, context truncation, retrieval corpus, tool result, policy, decoder parameters alebo provider backend. Ak odpoveď znie presvedčivo, ale je chybná, skúma sa source coverage, grounding, unsupported synthesis a output validation.

Troubleshooting nezačína prompt tweakom. Najprv sa rekonštruuje exact subject a porovná first divergence medzi expected a actual application chain.

## 11. Recovery a acceptance

Containment môže vypnúť auto-actions, route-nuť high-risk requests na human review, pinovať known-good snapshot alebo znížiť scope odpovede na citované facts. Recovery obnoví composite application release, nie iba model name.

Pozitívna acceptance vyžaduje jasné rozlíšenie GAI/foundation model/LLM/application, exact release subject, versioned eval dataset, grounded source behavior, structured validation a business metric. Forbidden acceptance je „novší model je lepší“, fluent demo, temperature `0` ako determinism proof alebo provider status ako business proof.

Second-operation test zopakuje uložené eval cases s rovnakým subjectom a následne s jednou vedome zmenenou generation. Rozdiel musí byť vysvetliteľný. Ak tím nevie určiť, čo sa zmenilo, application lifecycle nie je riadený.
