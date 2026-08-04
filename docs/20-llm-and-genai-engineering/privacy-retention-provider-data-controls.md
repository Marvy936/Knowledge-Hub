# Privacy, retention a provider data controls

GenAI privacy sa nedá zhrnúť vetou „provider netrénuje na našich dátach“. Training usage, abuse-monitoring logs, application state, uploaded files, caches, traces, fine-tuning artifacts, backups, support access a third-party tools sú rozdielne data paths s rozdielnou retention a deletion semantics. Produkčný privacy contract preto identifikuje exact provider, product, endpoint, model, region, project, feature flags a external processors pre konkrétnu operation.

V incidente `GENAI-SUPPORT-09` tím predpokladal Zero Data Retention, pretože organization mala schválený ZDR profil. Aplikácia však zapla background response mode a extended prompt caching pre multimodálne requesty; uploaded files zostávali ako application state a raw OCR/transcription sa zapisovali do vlastného trace backendu na 90 dní. Provider policy nebola porušená, no composed application release nespĺňal interný 24-hodinový retention contract. Root cause bol rozdiel medzi organization-level marketing statementom a exact endpoint/feature/storage matrixom.

## 1. Exact privacy subject

Privacy verdict platí pre presnú kombináciu runtime komponentov. Názov providera alebo model family nestačí, pretože endpointy a features môžu ukladať odlišný application state.

```yaml
privacy_subject:
  operation_id: support-case-82477
  provider: provider-a
  commercial_product: direct-api
  organization: org-17
  project: sk-support-prod
  endpoint: responses
  model_snapshot: model-2026-07-15
  region: eu-central
  regional_processing: true
  retention_profile: zdr-approved-v3
  store_parameter: false
  background_mode: false
  prompt_cache_mode: memory-only
  tools: [file-search]
  release_manifest: support-release-2026-08-04.9
```

Privacy review musí vedieť, čo bolo intended a čo runtime skutočne načítal. Mutable provider defaults alebo console screenshots nie sú authoritative evidence pre konkrétny request.

## 2. Data-flow inventory

Najprv sa vytvorí end-to-end data-flow inventory. Každý hop uvádza data class, controller alebo processor role, storage, region, retention, encryption a deletion owner.

```text
user device
→ application gateway
→ media preprocessing
→ prompt/context assembly
→ model provider
→ tools a connectors
→ cache
→ telemetry a eval pipeline
→ business system
```

Bez inventory sa tím sústredí na model provider a prehliadne vlastné logs, message queue, object storage, CDN, backup alebo external MCP server. Privacy boundary je celý application graph, nie iba inference API.

## 3. Customer content, system data a derived data

Data sa klasifikujú podľa toho, čo predstavujú a kto nad nimi má práva. Customer content môže zahŕňať prompts, images, audio, documents, completions a tool payloads; system data zahŕňa account, billing, usage a operational metadata; derived data zahŕňa embeddings, classifier outputs, summaries, OCR, transcripts a evaluation labels.

Derived artifact nie je automaticky anonymný. Embedding, summary alebo redacted transcript môže stále identifikovať osobu alebo odhaliť confidential business context, preto zdedí classification a retention policy podľa lineage.

## 4. Training usage nie je retention

Provider môže deklarovať, že API data nepoužíva na training, a zároveň ich dočasne držať pre abuse monitoring alebo application state. Opačne môže application uložiť vlastné requesty na eval dataset, aj keď provider používa ZDR.

```text
not used for model training
≠ not retained
≠ not accessible for abuse review
≠ not persisted by application features
≠ deleted from customer systems
```

Privacy questionnaire musí tieto otázky rozdeliť. Jedna boolean položka `provider_uses_data=false` vedie k nepresnému compliance verdictu.

## 5. Abuse-monitoring logs

Abuse-monitoring logs slúžia na enforcement provider policies a môžu obsahovať customer content alebo derived classifier signals. Default retention, legal exceptions a eligibility pre modified monitoring alebo ZDR sa overujú proti aktuálnemu commercial contractu a endpoint matrixu.

Application potrebuje vedieť, či content môže byť zachytený pri safety incident-e alebo manual review. Exception handling sa nesmie prezentovať ako absolútne „žiadny človek nikdy neuvidí dáta“, pokiaľ contract takú garanciu explicitne neposkytuje.

## 6. Application state

Application state vzniká, keď feature potrebuje durable object: conversation, thread, file, vector store, batch, eval run, fine-tuning job, background response alebo session memory. Retention môže byť `until deleted`, fixed duration alebo feature-specific.

ZDR pre abuse logs nemusí automaticky odstrániť application state. OpenAI napríklad rozlišuje abuse-monitoring retention a application-state retention per endpoint; niektoré objects zostávajú, kým ich zákazník neodstráni, a niektoré features nie sú ZDR-compatible.

## 7. `store=false` nie je univerzálne ZDR

Request parameter `store=false` môže vypnúť customer-retrievable response storage, ale nemusí meniť provider abuse-monitoring alebo feature-specific retention. Na inom produkte môže byť ZDR samostatný account alebo project policy, ktorý request s retention-requiring modelom úplne zablokuje.

Runtime preto loguje effective retention mode a provider acknowledgment, nie iba odoslaný parameter. Client-side intent bez server-side read-back nie je dôkaz, že policy bola aplikovaná.

## 8. Endpoint a capability matrix

Každý endpoint a feature má privacy matrix. Príklad dokumentačného modelu:

```yaml
capability_matrix:
  responses:
    default_application_state: 30d
    zdr_eligible: conditional
  files:
    application_state: until_deleted
    zdr_eligible: false
  embeddings:
    application_state: none
    zdr_eligible: true
  background_mode:
    temporary_state: required
    zdr_eligible: false
```

Hodnoty sa nekopírujú navždy do interného wiki. Matrix má source URL, checked-at timestamp, contract owner a next-review date, pretože provider capabilities sa menia.

## 9. Product boundary

Priamy API, consumer chat, enterprise chat, cloud marketplace a third-party hosted model sú odlišné commercial products. Rovnaká model family môže mať rozdielnu retention, region, support access a subprocessors podľa delivery channelu.

Anthropic napríklad uvádza, že zero-data-retention agreement sa týka schváleného API použitia a nemusí pokrývať Workbench, beta products, Claude for Work alebo Files API objects. Application architecture preto nesmie preniesť API contract na iný product iba podľa brand name.

## 10. Cloud marketplace a hosted-provider boundary

Pri modeli cez AWS Bedrock, Google Vertex AI alebo Azure sa data path a contract riadia cloud delivery modelom. Model provider nemusí mať priamy prístup k prompts a completions, ale cloud service môže mať vlastné abuse, logging, retention a cross-region processing pravidlá.

Architecture decision record uvádza, kto prevádzkuje inference account, kto drží logs a ktoré terms platia. „Je to Claude“ alebo „je to OpenAI model“ neodpovedá na otázku, kto je processor konkrétneho requestu.

## 11. Region, residency a processing

Data residency môže znamenať storage at rest v zvolenom regióne, no nie automaticky regionálne inference processing alebo lokalitu system data. Niektoré providers rozlišujú regional storage, regional processing a globally processed metadata.

```text
customer-content storage region
≠ inference processing region
≠ backup region
≠ telemetry region
≠ system-data region
```

Request routing musí používať správny regional endpoint a model snapshot. Fallback do iného regionu je privacy-sensitive behavior change a vyžaduje policy decision, nie iba availability routing.

## 12. Cross-region inference

Cross-region inference môže zlepšiť capacity a resiliency, ale mení processing destination a niekedy aj miesto retained data. Gateway preto kontroluje allowed region set podľa tenant a data classification.

Pri provider outage sa high-sensitivity workload nemusí automaticky prepnúť globálne. Degraded mode môže ponúknuť lokálny read-only model, queue alebo human workflow namiesto policy-violating fallbacku.

## 13. Uploaded files a media

Files API, object storage a media processing často vytvárajú dlhšie žijúce artifacts než samotný inference request. Upload má ownera, expiry, deletion job a lineage na derived OCR, thumbnails, transcripts a embeddings.

```yaml
media_object:
  object_id: file-771
  raw_digest: sha256:91ac...
  classification: regulated-identity
  expires_at: 2026-08-05T10:00:00Z
  derived_objects:
    - ocr-771-v3
    - thumbnail-771-v1
  deletion_owner: privacy-cleaner-v6
```

Delete raw file bez odstránenia derived objects a indexes nie je complete deletion. Deletion workflow potrebuje authoritative read-back cez všetky stores.

## 14. Prompt caching

Prompt caching môže ukladať hashes, encrypted prefixes alebo KV tensors. Presná implementácia ovplyvňuje ZDR eligibility, tenant isolation, retention a invalidation.

Privacy contract uvádza cache medium, TTL, region, encryption, key scope a whether content alebo only derived state persists. „Cache je iba optimalizácia“ nie je výnimka z data inventory.

## 15. Conversation a memory state

Conversation history, agent memory a user profile môžu byť explicitný feature alebo neúmyselný by-product. Každý memory write má purpose, scope, retention a deletion semantics.

Long-term memory sa nesmie napĺňať všetkým, čo model považuje za užitočné. Deterministic policy povoľuje iba schválené fields a user-visible controls; sensitive alebo transient content zostáva operation-scoped.

## 16. Tools, MCP a external services

Dáta odoslané web searchu, MCP serveru, code execution sandboxu alebo business SaaS podliehajú ich retention policies. Provider ZDR sa na third-party destination automaticky nevzťahuje.

Tool call policy preto obsahuje data classification, destination processor, contract a minimum necessary fields. Model nesmie rozhodovať, že external tool je bezpečný iba podľa jeho description.

## 17. Telemetry a tracing

Raw prompts, completions, images, audio a tool payloads sú často najväčší privacy leak v observability pipeline. Default telemetry používa IDs, digests, token counts, reason codes a redacted previews, nie full content.

Full-content capture je time-bound break-glass feature s approval, access logging a automatic expiry. Sampling configuration a trace exporter sú súčasťou privacy release, pretože zmena observability môže zmeniť retention bez zmeny model code.

## 18. Evals a incident datasets

Produkčné failures sa často kopírujú do evaluation datasetov. Pred kopírovaním sa overí legal basis, consent, minimization, de-identification a access boundary.

Eval case zachová behavior-relevant structure, ale nemusí zachovať raw identity. Dataset manifest obsahuje source operation, transformation, reviewer, retention a deletion propagation, aby incident data nezostali navždy v test systéme.

## 19. Fine-tuning a customization

Fine-tuning files, checkpoints, adapters a job logs majú vlastný lifecycle. Training restriction na provider side neznamená, že zákaznícky fine-tuning dataset nemá byť uložený; práve naopak, feature ho potrebuje spracovať a niekedy držať do explicitného deletion.

Customization release viaže dataset digest, model snapshot, training job, artifact location a retention. Zmazanie source file nemusí automaticky odstrániť už vytvorený model artifact, preto governance určuje, či a ako sa model retrain-ne alebo retire-ne.

## 20. Data minimization

Pred provider callom sa odošle iba obsah potrebný na task. Odstránia sa nesúvisiace attachments, hidden spreadsheet sheets, EXIF metadata, full mailbox context a unnecessary identifiers.

Minimization sa testuje na utility aj privacy. Príliš agresívna redaction môže zničiť entity alignment alebo business validation; správny design používa scoped pseudonyms a trusted resolution mimo modelu.

## 21. Tokenization, pseudonymization a redaction

Pseudonymization nahradí identifikátor stable tokenom, ktorý možno v trusted boundary resolve-núť. Redaction odstráni hodnotu bez možnosti reconstruction v model context-e.

```text
Martin Vyhonský → <PERSON_17>
IBAN SK... → <BANK_ACCOUNT_4>
```

Mapping store je citlivý security asset s oddeleným accessom a kratšou retention. Placeholder nesmie byť globálne stable naprieč tenants, inak umožní correlation.

## 22. Encryption a key management

Data in transit používajú TLS a data at rest provider alebo customer-managed encryption podľa capability. Customer-managed key zvyšuje control, ale prináša rotation, availability a recovery requirements.

Key deletion môže crypto-shred-núť data, no iba ak všetky relevantné copies používajú daný key. Backups, derived artifacts a third-party stores musia byť zahrnuté v encryption inventory.

## 23. Identity a access control

Provider projects, files, vector stores, evals a logs majú least-privilege RBAC. Production workload identity nemá admin capability meniť retention controls alebo exportovať všetky customer objects.

Human support access je time-bound, approved a audited. Tenant separation sa testuje na object IDs, search, batch export aj telemetry queries, nie iba v application UI.

## 24. Deletion semantics

Delete request môže znamenať soft delete, asynchronous purge, deletion after retention window alebo okamžité logical hiding. Privacy contract uvádza authoritative completion condition.

```text
request deletion
→ revoke access
→ remove active object
→ delete derived cache/index
→ schedule backup expiry
→ verify provider deletion state
→ record completion evidence
```

Ak provider neposkytuje per-object delete pre ephemeral logs, policy sa opiera o contractual retention a preukázanú configuration. Aplikácia nesmie predstierať okamžitú deletion, ktorú systém nevie vykonať.

## 25. Backup a disaster recovery

Backups predlžujú physical persistence aj po logical deletion. Retention, encryption a restore procedures musia zachovať deletion tombstones, aby restore neobnovil údaje, ktoré už mali byť odstránené.

DR test zahŕňa privacy replay: po restore sa spustí deletion reconciliation a overí, že expired alebo deleted objects sa nevrátili do aktívneho indexu.

## 26. Legal hold a safety exceptions

Legal hold alebo safety review môže oprávnene prerušiť štandardnú retention. Exception má authority, scope, reason, start, review date a explicit release process.

Exception sa neimplementuje tichým vypnutím cleaner jobu. Affected subjects sa evidujú oddelene a access zostáva need-to-know; po skončení hold-u sa deletion dokončí a overí.

## 27. Policy as code

Privacy policy sa vyjadruje ako machine-checkable constraints nad provider, endpoint, feature, region a data class. Deployment pipeline odmietne incompatible release.

```yaml
privacy_policy:
  data_class: regulated-identity
  allowed_regions: [eu-central]
  require_zdr: true
  forbidden_features:
    - background_response
    - persistent_conversation
    - external_web_search
  max_application_retention: 24h
```

Policy engine pracuje s resolved capabilities, nie marketingovými názvami. Provider feature matrix sa pin-ne ako dependency a pravidelne revaliduje.

## 28. Runtime read-back

Po deployment-e application prečíta effective project retention, regional endpoint, model availability, storage flags a tool configuration. Read-back sa uloží s release evidence.

Ak provider policy nie je queryable, použije sa control-plane export, contract artifact a active synthetic probe. Absencia API nie je dôvod preskočiť verification; iba mení typ evidence a uncertainty.

## 29. Monitoring

Privacy telemetry sleduje bytes a records podľa data class, retention mode, region, feature a destination. Alerts pokrývajú raw-content logging, expired objects, failed deletions, cross-region routing a policy-incompatible model invocation.

Dashboard bez data-flow denominatora môže klamať. Zero failed deletions je dobrý signál iba vtedy, ak cleaner skutočne našiel a spracoval expected population.

## 30. Provider-change management

Provider môže zmeniť defaults, endpoint eligibility, region support alebo retention requirements. Dependency watcher preto monitoruje official documentation, contract notices a model metadata.

Zmena sa neposúva priamo do production. Najprv sa aktualizuje capability matrix, vykoná impact analysis a revalidujú privacy tests; incompatible model sa môže stať unavailable namiesto tichého policy downgrade-u.

## 31. Failure hypotheses

Pri privacy incidente sa paralelne overuje viacero competing hypotheses, pretože rovnaký exposed record môže pochádzať z provider storage, application telemetry, cache, derived artifactu alebo restore pathu. API je konkrétny programový product surface a jeho endpoint/feature matrix môže mať inú retention než consumer UI alebo cloud marketplace. ZDR, teda Zero Data Retention, sa interpretuje iba podľa exact contracted productu a effective runtime mode; nie je synonymom pre training restriction ani request parameter `store=false`. Workload označuje celý spracovateľský graph aplikácie a policy je vynútiteľný súbor pravidiel pre data class, region, feature a retention. Nasledujúce body sa viažu na konkrétny store, authority a read-back evidence a zostávajú otvorené, kým object graph a loaded configuration neukážu first divergence.

- **Wrong provider product** — workload používal consumer alebo beta surface namiesto contracted API; overí sa endpoint, credential a billing project.
- **Feature incompatibility** — background mode, file storage, prompt caching alebo tool vyžadovali persistence napriek ZDR expectation.
- **Application telemetry leak** — provider bol compliant, ale raw content zostal v logs, queues, traces alebo eval storage.
- **Region drift** — fallback alebo cross-region inference spracovali data mimo allowed geography.
- **Deletion gap** — raw object bol zmazaný, no embeddings, transcripts, thumbnails, backups alebo support export zostali.
- **Contract interpretation error** — training restriction sa nesprávne interpretovala ako zero retention alebo no human access.
- **Configuration drift** — project alebo organization effective mode sa líšil od intended policy po mutable console change.

Incident sa neuzavrie tvrdením „provider tvrdí, že dáta sú bezpečné“. Potrebný je store-by-store evidence a loaded configuration read-back.

## 32. Containment a recovery

Containment zastaví ďalšie data flow: vypne affected feature, zablokuje tool destination, prepne na compliant endpoint alebo queue a revoke-ne exposed credentials. Zároveň sa zachová minimálna forenzná evidence bez ďalšieho kopírovania raw contentu.

Recovery vykoná deletion alebo crypto-shred, invaliduje caches, rotuje secrets, opraví policy a revaliduje release. Ak údaje opustili trust boundary, proces zahŕňa právne, security a customer-notification authority podľa incident planu.

## 33. Acceptance

Pozitívna acceptance dokazuje, že povolený request používa správny provider product, endpoint, region a retention profile a že potrebný output vznikne bez forbidden persistence. Forbidden acceptance dokazuje, že incompatible feature alebo model je zablokovaný pred odoslaním dát.

Deletion acceptance vytvorí object graph, požiada o deletion a overí raw, derived, index, cache a restore path. Second-operation test potvrdí, že nový request po policy zmene už používa novú effective configuration a starý client pool alebo cache ju neobíde.

## 34. Čo dokumentačná validácia nepreukazuje

Dokumentácia môže správne modelovať provider controls a data flows. Nepreukazuje aktuálny commercial contract, skutočnú provider retention, regionálne processing, completion deletion jobov ani absenciu shadow stores.

Runtime `Verified` vyžaduje control-plane evidence, request probes, storage inventory a deletion tests. Produkčný `Stable` stav vyžaduje dlhodobejšie monitoring evidence, incident response a revalidáciu po provider changes.

## Primárne zdroje

- [OpenAI API data controls](https://platform.openai.com/docs/models/default-usage-policies-by-endpoint)
- [Anthropic commercial data retention](https://privacy.anthropic.com/en/articles/7996866-how-long-do-you-store-my-organization-s-data)
- [Anthropic zero data retention scope](https://privacy.anthropic.com/en/articles/8956058-i-have-a-zero-data-retention-agreement-with-anthropic-what-products-does-it-apply-to)
- [Vertex AI and zero data retention](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/vertex-ai-zero-data-retention)
- [Amazon Bedrock data protection](https://docs.aws.amazon.com/bedrock/latest/userguide/data-protection.html)
- [Amazon Bedrock data retention](https://docs.aws.amazon.com/bedrock/latest/userguide/data-retention.html)

## Kontrolné otázky

1. Ktorý provider product, endpoint, project, model, region a feature set spracovali konkrétny request?
2. Kde sa oddeľuje training usage, abuse monitoring a application-state retention?
3. Ktoré files, caches, embeddings, traces, eval datasets a backups vzniknú z jedného requestu?
4. Je `store=false` iba request option alebo authoritative zero-retention policy s read-backom?
5. Ako sa propaguje deletion do derived artifacts, indexes, caches a restore pathu?
6. Čo sa stane, keď model alebo feature nie je compatible s required retention mode?
7. Ktoré third-party tools dostávajú data mimo provider privacy contractu?

## Navigácia

- Predchádzajúca kapitola: [Guardrails, moderation a output validation](guardrails-moderation-output-validation.md)
- Späť na sekciu: [LLM and GenAI Engineering](README.md)
- Nasledujúca kapitola: [Multimodal models](multimodal-models.md)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Guardrails, moderation a output validation](guardrails-moderation-output-validation.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Multimodal models →](multimodal-models.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
