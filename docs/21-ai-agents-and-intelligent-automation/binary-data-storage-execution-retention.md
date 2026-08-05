# Binary data, storage a execution retention

n8n workflow môže spracúvať JSON items, files, images, documents a veľké API payloady. Metadata o execution a samotné binary objects však nemusia byť uložené v rovnakej vrstve. Správny návrh preto viaže execution record, binary reference, storage mode, retention policy, privacy classification a recovery point do jedného evidence modelu.

Táto kapitola pokračuje v incidente `AGENT-N8N-09`. Queue deployment používal lokálny filesystem binary mode, takže worker nevidel PDF uložené webhook procesom. Po emergency migrácii do object storage dostal bucket sedemdňový lifecycle, zatiaľ čo execution history sa uchovávala tridsať dní. O dva týždne UI stále zobrazovalo execution metadata, ale binary evidence už neexistovalo.

Nosný data lifecycle je:

```text
workflow item a data classification
→ exact execution a binary object identity
→ selected execution-data a binary-data modes
→ write a durable reference
→ cross-process read a transformation
→ execution completion a audit correlation
→ age/count/privacy retention decision
→ soft delete, hard delete a object lifecycle
→ backup/restore alebo justified deletion proof
```

## 1. Execution data verzus binary data

Execution data obsahuje workflow run state, node inputs/outputs, errors a metadata podľa save settings. Binary data je file-like payload, ktorý môže byť referencovaný z execution items, ale uložený v memory, database, filesystem alebo external object storage.

Execution row bez binary objectu nemusí byť reprodukovateľná. Binary object bez workflow, execution a tenant reference je orphan s nejasným ownerom.

## 2. Exact data subject

Data subject obsahuje execution ID, workflow ID/version, project/tenant, node a item identity, binary property, object ID, content type, size, checksum, storage mode, storage generation a retention class. Filename nie je dostatočná identita.

Pri incident-e sa porovná metadata reference s actual object a checksumom. Successful lookup podľa key nepreukazuje, že payload patrí správnemu itemu.

## 3. Default memory behavior

Pri defaultnom spracovaní môže n8n držať binary data v memory. Je to jednoduché pre malé payloady, ale veľké files alebo vysoká concurrency môžu vyčerpať Node.js heap a zabiť worker.

Memory mode nie je durable storage a nie je vhodný ako offload target pre veľké queue-mode responses. Capacity model používa peak simultaneous file size, nie iba priemerný payload.

## 4. Filesystem mode

Filesystem mode zapisuje binary data na disk a znižuje application memory pressure. Je vhodný pre single-process alebo architecture s garantovaným shared persistent pathom podľa support boundary.

Lokálny ephemeral disk sa stratí pri reschedule a iný process ho nevidí. n8n explicitne nepodporuje filesystem binary mode ako distribuovaný queue-mode store.

## 5. Database mode

Database mode uloží binary alebo execution payload do PostgreSQL podľa supported configuration. Zjednoduší shared visibility, ale zväčší primary database, WAL, backup a memory/query pressure.

Tento mode môže byť funkčný pre queue path, no nie je automaticky najlepší pre veľké files. Load test meria database growth, latency a restore duration.

## 6. External object storage

Self-hosted Enterprise môže používať podporované external storage modes, aktuálne S3 a Azure Blob pre binary data podľa n8n dokumentácie. Object storage oddeľuje veľké payloady od application filesystemu a primary database.

External mode pridáva network, bucket/container policy, credentials, region, lifecycle, version compatibility a availability dependencies. „S3-compatible“ neznamená automaticky upstream-supported behavior.

## 7. Storage mode generation

Zmena z filesystem na S3 alebo Azure ovplyvňuje, kam sa zapisujú nové objects a odkiaľ sa čítajú staré. n8n môže zachovať čitateľnosť starších modes, ak zostanú povolené a credentials dostupné.

Mode switch nie je okamžitá migrácia historických objects. Inventory musí vedieť, ktorá execution používa ktorú storage generation.

## 8. Available verzus default modes

`N8N_DEFAULT_BINARY_DATA_MODE` vyberá write target pre nové binary data. `N8N_AVAILABLE_BINARY_DATA_MODES` určuje modes, z ktorých runtime dokáže čítať podľa configuration.

Odstránenie starého mode z available listu môže zneprístupniť historické objects, aj keď fyzicky existujú. Decommission sa robí až po migration alebo expiry proof.

## 9. Object key

External binary objects používajú workflow, execution a binary-file identity v storage path-e podľa n8n modelu. Key podporuje lookup, ale sensitive business data sa nemá vkladať do readable filename alebo prefixu bez potreby.

Object metadata môže obsahovať checksum a classification, no secrets a PII sa minimalizujú. Provider logs a inventory sú súčasťou data-governance scope.

## 10. Checksum a integrity

Checksum overuje, že bytes po prenose alebo restore zodpovedajú očakávanému payloadu. Neoveruje, že payload patrí správnemu tenantovi alebo bol autorizovane spracovaný.

Integrity proof sa viaže na execution, item a object reference. Duplicate file s rovnakým hashom môže byť legitimate reuse alebo cross-tenant data leak podľa contextu.

## 11. Cross-process visibility

Main, webhook processors a workers musia vedieť čítať storage objects potrebné pre ich role. Queue response offload navyše vyžaduje, aby worker zapísal body a main/webhook process ho následne prečítal a streamoval clientovi.

Shared endpoint nestačí; všetky roles potrebujú compatible auth, region, encryption a network. Read/write asymmetry sa testuje z každého process classu.

## 12. Storage credentials

Object-storage identity má minimálny bucket/container a operation scope. Runtime typicky potrebuje read, write a delete podľa pruning modelu, ale nemá dostať account-wide administration.

Managed identity alebo default credential chain môže odstrániť static key, no stále potrebuje workload attestation a explicitnú policy. Credential generation sa loguje bez secretu.

## 13. Encryption

TLS chráni data in transit a provider-side encryption chráni stored objects podľa selected mode. Customer-managed keys pridávajú key policy, rotation a restore dependencies.

Encryption neodstraňuje application authorization ani retention povinnosti. Worker s legitimate decrypt/read authority môže stále sprístupniť nesprávny tenant object pri mapping chybe.

## 14. Large webhook response offload

Queue-mode worker môže offloadnúť response body, ktorý prekročí relay limit, do shared binary store v podporovanej n8n version. Main alebo webhook process potom číta reference a streamuje body clientovi.

Offload sa zapína na workers a nepomôže pri `default` memory mode. Database mode môže načítať body cez primary database, zatiaľ čo object storage umožňuje streamovací path s odlišným resource profileom.

## 15. Execution save policy

n8n umožňuje konfigurovať, či ukladať successful, failed, manual executions a progress. Save policy určuje dostupnosť debug evidence aj database/storage growth.

High-risk mutation workflow môže vyžadovať bohatší audit než low-risk polling. Workflow-level override nesmie potichu oslabiť organization retention minimum.

## 16. Save on error

Failed executions sú dôležité pre diagnosis, ale failure status nemusí zachytiť absorbed per-item errors alebo external unknown outcomes. Uloženie iba explicitne failed executions môže vynechať green partial failures.

Business ledger a custom execution data dopĺňajú technical status. Retention design sa viaže na outcome risk, nie iba na n8n status enum.

## 17. Save on success

Successful executions môžu byť početné a drahé na uchovanie. Pre low-risk deterministic jobs možno ponechať iba aggregate metrics a business record.

Pre sensitive mutations môže byť potrebná execution-to-provider correlation aj pri success-e. Minimalizácia preto nesmie zničiť auditability.

## 18. Save progress

Node progress snapshots zvyšujú debugging detail, ale aj write amplification a storage. Pri dlhých workflows môžu pomôcť určiť first divergence.

Voľba sa testuje pod loadom. Zapnutie progress pre všetky high-volume workflows bez capacity modelu môže zhoršiť incident, ktorý má diagnostikovať.

## 19. Manual executions

Manual runs často obsahujú test payloady, pinned data alebo secrets a nemajú sa automaticky držať dlhšie než production. Na druhej strane môžu byť evidence pre release acceptance.

Policy rozlišuje ephemeral developer test, approved validation run a incident reproduction. Každá class má odlišnú retention a access.

## 20. Age-based pruning

n8n prunes finished executions staršie než `EXECUTIONS_DATA_MAX_AGE`; default podľa current docs je 336 hodín, teda 14 dní. Age sa počíta od finish time a nevzťahuje sa na new, running alebo waiting executions.

Age threshold musí zodpovedať incident detection delay, audit a privacy. Príliš krátka doba odstráni evidence pred RCA, príliš dlhá zvyšuje exposure a cost.

## 21. Count-based pruning

Pruning sa spustí aj vtedy, keď počet finished executions prekročí `EXECUTIONS_DATA_PRUNE_MAX_COUNT`; oldest records sa odstraňujú ako prvé. High-volume burst preto môže skrátiť effective retention pod očakávaný vek.

Policy sleduje oba limits. „30 dní“ nie je pravda, ak count cap odstráni dáta po troch dňoch.

## 22. Soft a hard delete

n8n najprv označí execution na deletion a neskôr ju hard-delete-ne kvôli performance a safety bufferu. `EXECUTIONS_DATA_HARD_DELETE_BUFFER` chráni recent data počas debuggingu.

Soft-deleted record sa nesmie považovať za dlhodobý restore point. Operational query a UI môžu zobrazovať iný stav počas transition.

## 23. Non-prunable executions

Executions v `new`, `running` alebo `waiting` stave nie sú eligible pre bežný pruning. Annotated executions sa podľa current docs neprune-ujú.

Stale waiting execution preto môže rásť mimo expected retention. Samostatný monitor hľadá neprimerane staré non-terminal records a určuje ownera.

## 24. Binary pruning

Binary data pruning je viazaný na execution pruning pre interné modes. Keď sa execution odstráni, relevantné binary data majú byť odstránené podľa active mechanismu.

Pri viacerých binary modes sa pruning môže týkať iba current active mode. Historical storage preto potrebuje explicitný decommission a orphan scan.

## 25. S3 binary lifecycle

Pre S3 binary data n8n deleguje deletion na bucket lifecycle, takže policy je required, ak sa data nemajú držať neobmedzene. Lifecycle musí byť zladený s execution retention a legal hold.

Ak lifecycle vymaže object skôr než execution record, UI a audit reference zostanú broken. Ak je dlhší, vznikajú orphans a zbytočný exposure.

## 26. Azure binary lifecycle

Azure Blob binary mode analogicky potrebuje lifecycle management policy. Container môže obsahovať viac data classes, preto rules musia rozlišovať prefix a age.

Generic delete rule pre celý container môže odstrániť execution data alebo iné artifacts s odlišnou retention. Policy sa testuje na sandbox objects.

## 27. External execution data

n8n môže v podporovanej Enterprise konfigurácii ukladať execution data externe, napríklad v S3. Každá execution eviduje, kde je jej bundle uložený, takže mode switch môže byť non-destructive, ak starý store zostane configured.

Execution data nie je to isté ako binary data. Jeho lifecycle riadi n8n execution pruning a nemá sa naň aplikovať bucket lifecycle, ktorý môže predčasne zmazať referenced bundle.

## 28. Retention matrix

Retention matrix oddeľuje execution metadata, execution bundle, binary objects, audit events, business records, logs a traces. Každá class má purpose, owner, location, age/count limit, legal hold a deletion proof.

Jedna globálna hodnota `30d` je nedostatočná. Data classes majú odlišnú citlivosť a recovery hodnotu.

## 29. Privacy a minimization

Node inputs/outputs môžu obsahovať PII, tokens, documents alebo customer secrets. Ukladá sa iba to, čo potrebuje debugging, audit alebo business process, s redaction a access controls.

Binary file môže zostať citlivý aj po odstránení filename. Derived OCR text, thumbnails a embeddings patria do rovnakého lineage.

## 30. Access control

Execution history a binary objects sú dostupné iba users a workloads s project/tenant a purpose-bound accessom. Direct object URL alebo bucket browser nesmie obísť n8n authorization.

Break-glass access má expiry a audit. Support engineer nepotrebuje permanentný read ku všetkým customer files.

## 31. Backup

Database backup zachytí metadata a database-stored payloady, ale nie external binary objects alebo filesystem mimo backup scope. Object versioning alebo backup policy musí korelovať s database recovery pointom.

Restore na čas T potrebuje execution references aj objects platné pre rovnaké T. Independent latest backups môžu vytvoriť dangling references.

## 32. Restore

Isolated restore načíta database, encryption key, execution store a binary objects. Representative execution history sa otvorí a checksum potvrdí payload.

Restore nesmie automaticky aktivovať production triggers ani posielať files do external systems. Najprv sa overuje read-only integrity.

## 33. Shared incident `AGENT-N8N-09`

PDF webhook zapísal binary object na lokálny disk webhook Podu. Worker job načítal metadata z PostgreSQL, no path na jeho filesysteme neexistoval. Execution zlyhala po queue pickup-e.

Emergency zmena prepla nové writes na S3, ale lifecycle rule mazala binary objects po siedmich dňoch. Execution records ostávali tridsať dní, takže neskorý compliance review našiel iba metadata a missing file.

## 34. Competing failure hypotheses

Prvá hypotéza je corrupt upload, druhá wrong binary property mapping, tretia cross-process filesystem visibility, štvrtá expired object lifecycle a piata storage permission alebo region mismatch. Všetky môžu vyzerať ako missing binary data.

Evidence porovná object reference, mode generation, process role, provider object inventory, deletion logs, checksum a execution timing. Re-upload bez diagnosis môže vytvoriť iný payload a skryť incident.

## 35. Evidence preservation

Zachová sa execution ID, binary object ID, storage mode, object metadata, checksum, lifecycle rule generation, access/deletion events a affected worker. Secret URLs a raw sensitive payloady sa nevkladajú do broad incident ticketu.

Legal hold alebo incident hold pozastaví deletion pre bounded scope. Nemá zmeniť global lifecycle bez capacity a privacy review.

## 36. Containment

Binary workflows sa zastavia alebo presmerujú na known-good shared mode. Lifecycle delete rule sa pozastaví iba pre affected prefix a nové objects dostanú correct classification.

Missing objects sa neregenerujú automaticky, ak source authenticity nie je potvrdená. Customer alebo provider impact sa najprv zmapuje.

## 37. Recovery

Historical filesystem objects sa migrujú alebo nechajú čitateľné do expiry podľa manifestu. Object lifecycle sa zosúladí s execution retention a n8n pruning semantics.

Representative upload prejde webhook, queue, worker, object read, transformation a download. Restore drill preukáže metadata-object consistency.

## 38. Positive acceptance

Každá execution ukazuje exact storage mode a binary reference, object je čitateľný zo všetkých required process roles a checksum sedí. Retention matrix zaručuje, že object neexpiruje skôr než reference.

Pruning test odstráni eligible execution aj binary object podľa intended policy a zachová annotated alebo held record.

## 39. Forbidden acceptance

Storage nie je prijatý iba preto, že upload API vráti success alebo bucket obsahuje object. Neprípustný je queue mode s local-only filesystemom, lifecycle kratší než reference retention, public object access alebo backup bez object store.

Empty bucket po pruning jobe nie je automaticky compliance proof; môže znamenať over-delete.

## 40. Recovery acceptance

Restore obnoví selected execution metadata aj binary bytes s correct checksumom v isolated environment. Recovery point, object generation a access policy sú zdokumentované.

Mode switch test potvrdí čítanie starých aj nových objects, kým starý mode nie je controlled decommissioned.

## 41. Second-workflow acceptance

Druhý workflow s iným file type, väčším payloadom a odlišnou retention classou prejde storage aj pruning lifecycle bez použitia prvej policy naslepo. Test odhalí prefix a size assumptions.

Tenant-negative test potvrdí, že workflow B nevie čítať object workflowu A ani pri znalosti object key.

## 42. Praktická retention matrix

Matrix je machine-readable a používa sa na generovanie n8n settings, object lifecycle a review checks. Hodnoty sú príklad, nie univerzálny default.

```yaml
data_retention:
  execution_metadata:
    store: postgresql
    max_age_hours: 720
    max_count: 100000
  execution_data:
    store: s3
    deletion_authority: n8n-pruning
    bucket_lifecycle: forbidden
  binary_data:
    store: s3
    lifecycle_days: 35
    execution_reference_days: 30
  audit_events:
    store: security-ledger
    retention_days: 365
```

## 43. Prevádzkové metriky

Sledujú sa execution rows, saved payload bytes, binary object count/bytes, missing-reference rate, orphan count, prune candidates, hard-delete lag, lifecycle deletions, storage read/write latency, checksum failures a restore-drill age. Metriky sa segmentujú podľa mode a workflow.

Storage cost bez denominatora accepted executions môže klamať. Rast môže pochádzať z legitimate volume, disabled pruning alebo orphan leakage.

## 44. Primárne zdroje

- [n8n Docs — Manage execution data](https://docs.n8n.io/deploy/host-n8n/configure-n8n/scaling/manage-execution-data/)
- [n8n Docs — Execution environment variables](https://docs.n8n.io/deploy/host-n8n/configure-n8n/basic-configuration/use-environment-variables/executions/)
- [n8n Docs — Handle binary data](https://docs.n8n.io/deploy/host-n8n/configure-n8n/scaling/handle-binary-data/)
- [n8n Docs — Binary-data environment variables](https://docs.n8n.io/deploy/host-n8n/configure-n8n/basic-configuration/use-environment-variables/binary-data/)
- [n8n Docs — External storage](https://docs.n8n.io/deploy/host-n8n/configure-n8n/scaling/use-external-storage/)

## 45. Zhrnutie

Execution metadata, execution bundles a binary objects tvoria prepojený, ale distribuovaný evidence chain. Storage mode, retention a backup sa musia navrhnúť spoločne, inak reference prežije payload alebo payload prežije oprávnený deletion.

Accepted lifecycle preukazuje cross-process read, privacy, coordinated pruning, restore a tenant-negative test. Upload success, object count ani UI execution row samostatne nepreukazujú durable a správne vlastnené data.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Queue mode, Redis, workers a scaling](queue-mode-redis-workers-scaling.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
