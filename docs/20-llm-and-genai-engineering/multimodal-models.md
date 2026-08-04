# Multimodal models

Multimodálny model prijíma alebo generuje viac než jednu modalitu, napríklad text, image, audio, video alebo document layout. Praktická application však nepracuje s abstraktnou „fotkou“ či „nahrávkou“. Pracuje s exact media artifactom, codec-om, resolution, orientation, timestamps, sampling policy, OCR alebo transcription generation, modality tokenization a model snapshotom. Ak tieto transformácie nie sú súčasťou subjectu, rovnaký súbor môže produkovať odlišný výsledok bez zjavnej zmeny promptu.

V incidente `GENAI-SUPPORT-09` používateľ nahral fotografiu dokladu a stereo hlasovú správu. Image preprocessing zmenšil obrázok tak, že malý disclaimer a druhé priezvisko prestali byť čitateľné; audio pipeline zlúčil kanály a speaker diarization priradila vetu druhého človeka používateľovi. Model vytvoril fluent summary a validný JSON, no identita a consent boli nesprávne. Guardrail kontroloval iba text output a release manifest neobsahoval image tiling, audio downmix ani transcription generation.

## 1. Exact multimodal subject

Multimodálny verdict sa viaže na raw artifact aj celý preprocessing chain. File name, URL alebo human label nie sú dostatočná identita.

```yaml
multimodal_subject:
  operation_id: support-case-82477
  artifact_id: media-771
  raw_digest: sha256:91ac...
  modality: image+audio
  mime_types:
    - image/jpeg
    - audio/mpeg
  image:
    width: 4032
    height: 3024
    orientation: exif-6
  audio:
    duration_ms: 84211
    sample_rate_hz: 48000
    channels: 2
  preprocessing_release: media-pipeline-v18
  extraction_release: ocr-stt-v11
  model_snapshot: multimodal-2026-07-15
  prompt_release: identity-review-v9
```

Reprodukcia potrebuje raw digest alebo immutable object version. Ak source URL ukazuje na mutable content, neskorší replay nemusí hodnotiť rovnaké dáta.

## 2. Modality, representation a capability

„Model podporuje images“ neznamená, že spoľahlivo číta malé písmo, počíta objekty, interpretuje medical scans alebo chápe spatial relations. Capability sa definuje taskom, input envelope a acceptance datasetom.

```text
image captioning
≠ OCR
≠ document layout understanding
≠ chart reasoning
≠ visual grounding
≠ biometric identity verification
```

Rovnaká modality môže mať veľmi rozdielne risk a evaluation requirements. Application contract preto uvádza presnú úlohu, nie iba supported MIME type.

## 3. Architectural patterns

Multimodálne systems používajú viacero architektonických patternov. Bežný pattern má modality encoder, projector alebo connector a language-model backbone; iný system používa zjednotené modality tokens alebo samostatné expert pathways.

```text
raw media
→ modality-specific encoder
→ aligned representation alebo tokens
→ multimodal fusion
→ language/reasoning backbone
→ text, audio, image alebo tool output
```

Z application perspective je dôležité, že input sa komprimuje a transformuje. Marketingový label „native multimodal“ sám nepreukazuje zachovanie všetkých pixelov, frames, channels ani timestamps.

## 4. Information bottleneck

Media obsahuje oveľa viac raw informácie než sa zmestí do context budgetu. Preprocessing a encoder preto vykonajú selection alebo compression, ktorá môže odstrániť task-relevant detail.

Image resizing môže zničiť small text; video sampling môže preskočiť krátku udalosť; audio downsampling môže zhoršiť non-speech cue. Produkčný design identifikuje, ktoré informácie sú required a ako sa overí, že preprocessing ich zachoval.

## 5. Image ingestion

Image pipeline validuje MIME, file signature, dimensions, orientation, color space, alpha channel, animation a decompression limits. EXIF orientation sa aplikuje deterministicky a raw artifact zostáva zachovaný.

```text
raw image
→ format validation
→ orientation normalization
→ crop/tiling/resolution policy
→ safety scan
→ model input
```

Automatický center crop môže odstrániť rohový text alebo signature. Tiling zvyšuje detail, ale aj token cost a môže stratiť global spatial relation, preto sa global preview kombinuje s detail tiles podľa tasku.

## 6. Resolution a detail level

Provider API môže podporovať low, high alebo automatic image detail. Tieto režimy menia tokenization, latency, cost a schopnosť rozlíšiť malé objekty.

Detail policy je pinned podľa use case. Thumbnail stačí na hrubú classification, ale document verification potrebuje page-level alebo tile-level detail a často samostatný OCR/layout pipeline.

## 7. OCR a document extraction

OCR je vlastný modelový krok s language, confidence, bounding boxes a page order. Extracted text nie je authoritative raw document a chyby OCR sa nesmú skryť vložením textu do promptu bez provenance.

```yaml
ocr_span:
  text: "Martin Vyhonský"
  page: 1
  bounding_box: [0.18, 0.32, 0.51, 0.37]
  confidence: 0.72
  extractor_release: ocr-v11
```

Low-confidence alebo legally significant fields sa smerujú na explicit verification. Model nemá doplniť chýbajúci znak podľa plausibility a potom ho prezentovať ako prečítaný fakt.

## 8. Document layout

PDF, formulár a spreadsheet nesú význam v layout-e, tables, headers, footnotes, merged cells a reading order. Plain text extraction môže oddeliť hodnotu od labelu alebo zmiešať dva stĺpce.

Document pipeline zachová page, block, cell a relation metadata. Pri odpovedi alebo tool proposal sa evidence viaže na page a region, nie iba na celý súbor.

## 9. Image spatial grounding

Spatial grounding odpovedá, kde sa evidence nachádza. Bounding box, mask alebo point musí používať definovaný coordinate system a image version.

```text
normalized coordinates 0..1
≠ original pixel coordinates
≠ post-crop tile coordinates
```

Ak UI zobrazí box nad inou resized image, môže vizuálne potvrdiť nesprávny objekt. Transform matrix a original dimensions sú preto súčasťou evidence.

## 10. Charts, diagrams a screenshots

Chart reasoning kombinuje OCR, visual marks, axes, legends a numeric relations. Model môže prečítať labels správne a napriek tomu nesprávne interpolovať hodnotu alebo zameniť series.

High-impact numeric extraction sa overuje deterministic parserom alebo source data, ak sú dostupné. Screenshot dashboardu nie je authoritative metric, keď application môže query-nuť underlying data API.

## 11. Audio ingestion

Audio pipeline eviduje codec, sample rate, channels, duration, loudness, language a clipping. Transcoding môže meniť signal, preto sa raw digest a transcoded digest oddeľujú.

```text
raw audio
→ decode
→ channel policy
→ resample
→ voice-activity detection
→ segmentation
→ transcription/understanding
```

Mono downmix môže prekryť hovoriacich alebo zmeniť spatial cue. Multi-channel content sa nesmie automaticky zlúčiť, ak task závisí od speaker identity.

## 12. Speech versus general audio

Speech-to-text, speaker diarization, acoustic-event recognition a native audio understanding sú rozdielne capabilities. Siréna, tone, pause alebo emotion môže byť relevantná informácia, ktorú transcript neobsahuje.

Application rozhodne, či používa transcript-first pipeline alebo priamy audio-capable model. Pri transcript-first flow sa explicitne prizná information loss a neodvodzujú sa acoustic claims iba z textu.

## 13. Speaker diarization

Diarization priraďuje segments anonymným speaker labels; nepreukazuje identitu osoby. Speaker embedding alebo voice match má osobitný consent, privacy a biometric risk.

Overlapping speech a krátke interjections znižujú reliability. High-impact attribution potrebuje timestamps, confidence a human review alebo explicitný user confirmation.

## 14. Audio timestamps

Claim o tom, čo bolo povedané, sa viaže na time interval a source track. Offset môže vzniknúť trimmingom silence, resamplingom alebo spojením chunks.

Transform lineage obsahuje mapping medzi processed timeline a original timeline. UI playback a evidence citation musia používať správnu mapu, inak reviewer počuje inú vetu než model.

## 15. Video ingestion

Video kombinuje frames, audio, subtitles, metadata a temporal order. Default sampling na pevnom FPS môže preskočiť krátky event alebo zbytočne míňať budget na statickú scénu.

```text
container validation
→ shot/scene detection
→ frame sampling
→ audio extraction
→ subtitle/OCR extraction
→ temporal fusion
```

Sampling policy sa volí podľa tasku: uniform, keyframe, scene-aware, motion-aware alebo query-guided. Policy a sampled timestamps sú súčasťou exact subjectu.

## 16. Temporal grounding

Video odpoveď potrebuje interval, nie iba global description. Model musí rozlíšiť before, during, after a simultaneous events.

Temporal hallucination vzniká, keď model spojí udalosti z dvoch vzdialených frames do jedného momentu. Acceptance preto obsahuje timestamped questions a counterexamples s podobnými scénami v inom poradí.

## 17. Frame rate a missed events

Low sampling rate znižuje cost, ale zvyšuje pravdepodobnosť missed transient eventu. High sampling rate zvyšuje context pressure a môže zhoršiť reasoning tým, že zaplaví model redundantnými frames.

Task-specific capacity test meria recall podľa event duration a sampling policy. „Model podporuje hodinové video“ neznamená, že zachytí stotinu sekundy trvajúcu zmenu.

## 18. Cross-modal alignment

Multimodálny system musí určiť, ktoré textové, vizuálne a audio elements patria spolu. File order alebo nearby position nemusí byť semantic alignment.

Pri viacerých images sa každý artifact označí stable ID. Prompt a output schema používajú tieto IDs, aby model necitoval „obrázok vyššie“ alebo nezamenil customer A a customer B.

## 19. Modality conflict

Modalities môžu byť v rozpore: subtitle hovorí niečo iné než audio, screenshot má stale value oproti API, text description nezodpovedá image. System nesmie konflikt ticho vyriešiť podľa modelovej preferencie.

Authority policy určuje source hierarchy podľa claim type. Napríklad raw signed document môže byť authoritative pre podpis, ale business database pre current account status.

## 20. Context assembly

Media tokens, OCR, transcript a text prompt súťažia o context budget. Context assembly preto prideľuje budget podľa modality a tasku, nie first-come-first-served.

```yaml
context_budget:
  text_instructions: 4000
  image_tiles: 12000
  transcript: 18000
  retrieved_policy: 6000
  reserve_for_output: 4000
```

Truncation sa zaznamená ako explicitný event. Model nesmie odpovedať, ak required page alebo time segment nebol zahrnutý.

## 21. Media tokenization a cost

Providers môžu účtovať images podľa tiles/detail, audio podľa duration alebo tokens a video podľa frames/resolution. Token estimate pred requestom nemusí presne zodpovedať provider usage.

Cost ledger uchová provider-reported usage, preprocessing cost a storage. Optimalizácia resolution alebo sampling sa hodnotí proti quality a risk segmentom, nie iba priemerným costom.

## 22. Latency decomposition

Multimodálna latency zahŕňa upload, malware scan, transcode, OCR/STT, provider queue, inference, moderation a postprocessing. Jeden end-to-end p95 bez span graphu neukáže, kde vzniká problém.

Large media môže bežať asynchronously, ale background state mení retention a user experience. Architecture preto spája performance decision s privacy contractom.

## 23. Streaming a realtime interaction

Realtime voice alebo video pridáva turn detection, interruption, jitter, partial transcription a incremental moderation. Partial output môže byť používateľovi odoslaný pred final validation.

Session má exact media stream identity, sequence numbers a cancellation semantics. Interruption musí zastaviť aj downstream tool proposal, nie iba audio playback.

## 24. Generated images, audio a video

Multimodal output môže byť media, nie text. Acceptance potom zahŕňa dimensions, duration, codec, watermark alebo provenance metadata, content safety a task fidelity.

Generated media sa nesmie považovať za verified evidence reálneho sveta. UI a downstream systems musia zachovať synthetic provenance, aby sa asset nezamenil s source photo alebo recordingom.

## 25. Multimodálne prompt injection

Instructions môžu byť v visible text-e, tiny overlay, QR kóde, audio whisper, subtitle, metadata alebo video frame. OCR alebo transcription môže attack sprístupniť modelu aj vtedy, keď človek ho nevidí.

Media content sa označuje ako untrusted data a nepreberá instruction authority. Prompt-injection detector je doplnkový signal; external authorization a least-privilege tools musia zablokovať forbidden side effect aj pri detector escape.

## 26. Safety a moderation

Každá modality má vlastné harm categories, coverage a thresholds. Text moderation nad transcriptom nemusí zachytiť explicitný visual content alebo acoustic event.

Pipeline určuje, či moderation beží nad raw media, extracted representation, generated media alebo všetkými vrstvami. Language a modality limitations sa uvádzajú v release evidence a pokrývajú eval datasetom.

## 27. Privacy a biometric risk

Images a audio môžu obsahovať faces, IDs, locations, voices, bystanders a background information. EXIF, room sounds alebo reflection môžu odhaliť viac než explicitný subject.

Data minimization odstráni unnecessary metadata, tracks a regions pred provider callom. Face recognition, speaker identification alebo emotion inference sú samostatné high-risk use cases, nie implicitná súčasť „multimodal understanding“.

## 28. Accessibility

Multimodálne application má poskytovať text alternatives, captions, transcript corrections a keyboard-accessible evidence. Accessibility nie je iba UI feature; zároveň zlepšuje auditability a human review.

Generated description musí rozlišovať observed content od inference. Pri neistote používa bounded language a umožní používateľovi zobraziť source region alebo timestamp.

## 29. Evaluation dataset

Eval dataset obsahuje raw media, immutable digests, licenses, consent, annotations a preprocessing manifest. Splits sa chránia pred near-duplicate frames, template leakage a identity overlap.

Segmenty zahŕňajú resolution, lighting, orientation, language, accent, channel count, duration, document type, chart density, event duration a adversarial overlays. Global score bez týchto segmentov môže zakryť kritický failure mode.

## 30. Task-specific metrics

Image captioning používa iné metrics než OCR field extraction, visual grounding alebo temporal QA. Automatické lexical metrics často nepreukážu factual correctness ani spatial accuracy.

```text
OCR field extraction
→ exact/normalized field accuracy + abstention

visual grounding
→ IoU alebo point accuracy

video event QA
→ answer correctness + temporal localization

audio attribution
→ transcript error + speaker/time correctness
```

Human evaluation sa používa tam, kde task quality nemožno zachytiť deterministic validatorom. Expert authority sa oddeľuje od user preference.

## 31. Cross-modal consistency tests

Counterfactual test zmení jednu modality a drží ostatné konštantné. Ak sa zmení image date, odpoveď musí zmeniť date claim; ak sa vymení audio speaker, nesmie zostať stará attribution.

Conflict test vloží nesúlad medzi OCR a database alebo subtitle a audio. Expected behavior je explicitný conflict alebo authority-based resolution, nie fluent merge oboch tvrdení.

## 32. Failure hypotheses

Pri multimodálnom incidente sa overujú competing hypotheses od raw artifactu po business decision.

- **Wrong raw artifact** — mutable URL, upload race alebo dedup collision priradili iný media object; overí sa digest a object version.
- **Preprocessing loss** — resize, crop, downmix, resample alebo frame sampling odstránili relevantný detail; porovná sa raw a processed artifact.
- **Extraction error** — OCR, transcription alebo diarization vytvorili nesprávny intermediate evidence; overia sa boxes, timestamps a confidence.
- **Context truncation** — required tile, page, transcript segment alebo frame nebol vložený do model contextu.
- **Cross-modal misalignment** — model spojil text, image alebo audio z rozdielnych subjects či časov.
- **Model reasoning error** — správne representations boli dostupné, ale claim alebo relation boli nesprávne.
- **Validation gap** — output bol syntakticky validný, no business system neoveril identity, temporal alebo spatial evidence.

Prvá viditeľná nesprávna veta nemusí byť first divergence. Trace musí zachovať media pipeline, extraction, context assembly a model/tool stages.

## 33. Containment a recovery

Containment zachová raw media, vypne affected preprocessing release alebo high-impact automation a prepne na manual review. Nevykonáva sa destructive reprocessing bez zachovania pôvodného artifactu a lineage.

Recovery nasadí known-good pipeline, invaliduje derived caches, re-extract-ne affected objects a overí incident plus benign controls. Ak nesprávny multimodálny verdict vytvoril side effect, vykoná sa compensating business recovery nezávisle od model fixu.

## 34. Acceptance

Pozitívna acceptance dokazuje, že supported media prejde validation, preprocessing a modelom s požadovanou task accuracy a latency. Forbidden acceptance dokazuje, že corrupt file, cross-tenant media, hidden injection, low-confidence identity field a missing required segment nevytvoria high-impact decision.

Second-operation test zmení preprocessing alebo model release a overí, že nový request používa novú generation bez stale OCR, transcript alebo media-token cache. Alternate-scenario test použije inú modality kombináciu, napríklad image+text namiesto audio+image, aby sa nepotvrdil iba jeden incident pattern.

## 35. Čo dokumentačná validácia nepreukazuje

Dokumentácia môže vysvetliť media lifecycle a evaluation design. Nepreukazuje skutočnú image, audio alebo video capability konkrétneho modelu, provider limits, tokenization, safety coverage ani produkčnú latency.

Runtime `Verified` vyžaduje vykonané task-specific evals na exact preprocessing a model release. Produkčný `Stable` stav vyžaduje reálne traffic segmenty, drift monitoring, incident recovery a privacy evidence pre media storage.

## Primárne zdroje

- [OpenAI API image and file inputs](https://platform.openai.com/docs/quickstart/make-your-first-api-request)
- [Gemini API multimodal getting started](https://ai.google.dev/gemini-api/docs/get-started)
- [Gemini API file inputs](https://ai.google.dev/gemini-api/docs/file-input-methods)
- [Gemini API audio understanding](https://ai.google.dev/gemini-api/docs/generate-content/audio)
- [Gemini API video understanding](https://ai.google.dev/gemini-api/docs/video-understanding)
- [Multimodal Large Language Models: A Survey](https://arxiv.org/abs/2506.10016)

## Kontrolné otázky

1. Aký raw digest, media metadata a preprocessing release definujú konkrétny multimodálny input?
2. Ktoré informácie sa strácajú pri resize, crop, tiling, downmix, resampling alebo frame sampling?
3. Ako sa evidence viaže na page, bounding box, speaker a timestamp?
4. Čo sa stane pri konflikte medzi modalities alebo medzi media a authoritative database?
5. Pokrýva moderation raw media, extracted text aj generated output?
6. Ktoré task-specific metrics a segments dokazujú capability namiesto všeobecného „supports images“?
7. Invaliduje release zmena preprocessing generation, OCR/STT alebo media cache?

## Navigácia

- Predchádzajúca kapitola: [Privacy, retention a provider data controls](privacy-retention-provider-data-controls.md)
- Späť na sekciu: [LLM and GenAI Engineering](README.md)
- Nasledujúca kapitola: [LLMOps a production readiness](llmops-production-readiness.md)
