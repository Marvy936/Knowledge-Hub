# Idempotency a duplicate-event handling

Idempotency zabezpečuje, že opakovanie tej istej logickej operácie nevytvorí ďalší business side effect. V n8n je nevyhnutná preto, že webhook provider môže event doručiť viackrát, node môže retryovať request, operátor môže retryovať execution a queue alebo sub-workflow môže rovnakú prácu znovu spustiť po timeout-e či páde workeru.

Táto kapitola pokračuje v incidente `AGENT-N8N-08`. Refund request mal tri rôzne technické identity: provider event ID, n8n execution ID a HTTP request attempt. Workflow nepoužil stabilný business operation key, takže každý retry vyzeral ako nová požiadavka. Provider pritom prvý timeoutnutý request už commitol a ďalší pokus vytvoril duplicitnú mutation.

Nosný idempotency lifecycle je:

```text
trusted event a business subject
→ canonical logical operation
→ stable idempotency key a payload fingerprint
→ atomic claim alebo existing-record read
→ side-effect attempt s rovnakou identity
→ authoritative external read-back
→ terminal result persistence
→ duplicate replay s rovnakým výsledkom
→ retention, expiry a second-tenant negative test
```

## 1. Idempotent operation

Operácia je idempotentná, keď jedno alebo viac vykonaní s rovnakým logickým významom vedie k rovnakému prijatému výsledku a nevytvára dodatočné side effects. Čisté čítanie je často prirodzene idempotentné, zatiaľ čo vytvorenie platby, refundu alebo ticketu zvyčajne potrebuje explicitný control.

Idempotency neznamená, že každý HTTP request vráti rovnaký status alebo latency. Znamená, že business systém rozpozná rovnakú operáciu a necommitne ju druhýkrát.

## 2. Duplicate event verzus duplicate operation

Duplicate event je opakované doručenie tej istej udalosti. Duplicate operation vzniká, keď workflow z dvoch rôznych eventov alebo retries vytvorí rovnaký business side effect.

Event deduplication a operation idempotency sa prekrývajú, ale nie sú zameniteľné. Dva odlišné provider events môžu legitímne reprezentovať jednu logical operation a jeden event môže obsahovať viac nezávislých operations.

## 3. Identity hierarchy

Provider event ID identifikuje delivery subject, n8n execution ID konkrétny engine run, node attempt jeden technický pokus a business operation key intended mutation. Iba posledná identity zostáva stabilná naprieč retry vrstvami.

Použitie execution ID ako idempotency key zlyhá pri retry celej execution, pretože nový run dostane novú identity. Použitie timestampu alebo random UUID vytvorí pri každom pokuse nový side effect.

## 4. Canonical business subject

Operation key sa skladá z invariantov, ktoré určujú význam operácie: tenant, resource, operation type, business object a prípadne generation alebo amount. Napríklad `refund:tenant_acme:payment_771:full` vyjadruje jeden plný refund konkrétnej platby.

Key nesmie závisieť od nestabilného poradia items, node názvu alebo workeru. Canonicalization normalizuje case, whitespace, currency precision a field ordering podľa doménového contractu.

## 5. Idempotency key

Idempotency key je opaque alebo čitateľný identifier, ktorý caller opakovane posiela pre tú istú logical operation. Provider alebo vlastný idempotency store ho viaže na request fingerprint a výsledok.

Key sa generuje pred prvou mutation a prenáša cez sub-workflow, retries aj error recovery. Nesmie sa po timeout-e znovu vytvoriť, pretože tým by sa zmenila identity operácie.

## 6. Payload fingerprint

Rovnaký key s odlišným payloadom je conflict, nie bezpečný duplicate. Store preto uchováva hash canonical requestu a pri opakovaní porovná, či amount, destination, tenant a operation type zostali rovnaké.

Ak sa payload líši, workflow zastaví a vyžaduje nový explicitný operation key alebo human decision. Tiché prijatie by mohlo vrátiť starý výsledok pre inú požiadavku.

## 7. Idempotency record

Record obsahuje key, tenant, payload hash, state, attempt metadata, external reference, response summary, created/updated time a retention policy. Je authoritative pre rozhodnutie, či sa operácia môže začať, pokračovať alebo iba vrátiť uložený výsledok.

Record je business ledger, nie iba cache. Jeho strata počas restore môže zmeniť bezpečný retry na duplicate mutation.

## 8. State machine

Typický lifecycle používa stavy `claimed`, `in_progress`, `committed`, `rejected`, `unknown`, `compensated` a `expired`. Prechody sú kontrolované a auditované; napríklad `committed` sa nesmie vrátiť do `in_progress` iba kvôli novému executionu.

Unknown state vyžaduje reconciliation. Automatický prechod z `unknown` na nový attempt bez authoritative read-back je forbidden.

## 9. Atomic claim

Pri paralelných deliveries môžu dve executions súčasne zistiť, že record neexistuje. Ak potom obe vytvoria side effect, jednoduché `check-then-act` dedupe zlyhá.

Claim musí byť atomic pomocou unique constraintu, compare-and-set, transactionu alebo iného single-writer mechanismu. Jeden worker získa ownership; ostatní čítajú existing state a čakajú alebo vrátia duplicate result.

## 10. Concurrency race

Aj správny key nepomôže, ak store dovolí dva paralelné owners. Race sa testuje viacerými súčasnými executions s rovnakým operation key a artificial delayom medzi claimom a mutation.

Acceptance vyžaduje jeden external commit a konzistentný výsledok pre všetkých callers. Duplicate denial nesmie byť iba náhodný efekt rate limitu.

## 11. Provider-native idempotency

Niektoré API podporujú idempotency key alebo conditional create priamo. Vtedy workflow posiela rovnaký key pri každom attempt-e a uchová provider request/result reference.

Provider control je silný, pretože enforcement je pri side-effect authority. Stále však treba local record pre event dedupe, tenant validation, retries a audit a treba poznať provider retention a conflict semantics.

## 12. Provider bez idempotency supportu

Ak API nemá native idempotency, workflow vytvára local single-writer record a podľa možnosti používa deterministic external resource ID alebo conditional write. Po mutation musí uložiť authoritative external reference.

Medzera medzi external commitom a local persistom zostáva riziková. Recovery preto číta provider podľa business subjectu alebo deterministic markeru, nie iba local state.

## 13. Inbox pattern

Inbox table prijíma external event s unique provider/event identity a payload hashom. Atomic insert rozhodne, či ide o nový delivery alebo duplicate.

Inbox rieši delivery dedupe, ale nie automaticky business operation. Event processor z inboxu vytvorí jeden alebo viac canonical operation records podľa doménových pravidiel.

## 14. Outbox pattern

Outbox zapisuje intended downstream event alebo command v rovnakej transakcii ako lokálny business state. Samostatný publisher ho potom opakovane doručuje, kým consumer nepotvrdí spracovanie.

n8n môže byť consumer alebo orchestration layer, no outbox authority typicky patrí aplikácii alebo database, ktorá vlastní business mutation. Workflow polling bez transactional linku môže event stratiť alebo duplikovať.

## 15. Webhook duplicate handling

Webhook endpoint najprv overí signature, tenant a freshness a až potom atomic vloží event do inboxu. Acknowledgement sa viaže na prijatie do durable state, nie nevyhnutne na dokončenie celej business operácie.

Provider redelivery s rovnakým event ID vráti úspešné acknowledgement a odkaz na existujúci state. Nemá spustiť nový workflow side effect.

## 16. Retry duplicate handling

Node retry, execution retry a manual replay musia používať rovnaký operation key. Idempotency record rozhodne, či sa má pokračovať, čakať, reconciliovať alebo vrátiť existing result.

Attempt count sa zvyšuje, ale logical operation identity zostáva rovnaká. Observability preto rozlišuje `operation_id` a `attempt_id`.

## 17. Remove Duplicates node

Workflow-level deduplication node môže odstrániť opakované items v konkrétnom toku podľa vybraných fields. Je užitočný pre data cleaning, ale nie je automaticky durable idempotency control naprieč executions a crashmi.

Produkčný side effect potrebuje persistent, atomic a tenant-scoped store. In-memory alebo execution-local dedupe nevydrží nový run ani paralelný worker.

## 18. Static workflow data

Workflow static data môže slúžiť na obmedzené state use cases podľa n8n semantics, ale nie je univerzálnou náhradou transactional idempotency ledgeru. Concurrency, deployment a recovery vlastnosti treba overiť pre konkrétnu verziu a mode.

High-impact operations používajú explicitný external datastore s unique constraints, backupom a auditom. Convenience state v orchestration platforme nemá niesť nezdokumentovanú financial authority.

## 19. TTL a retention

Idempotency record sa uchováva aspoň počas maximálneho retry/redelivery okna a business dispute obdobia primeraného impactu. Príliš krátky TTL umožní neskorému duplicate eventu vytvoriť nový side effect.

Príliš dlhý retention zvyšuje storage a privacy burden. Policy rozlišuje opaque key, payload hash, response metadata a sensitive evidence.

## 20. Expiry semantics

Po expiry key nesmie byť automaticky recyklovaný pre odlišnú operáciu, ak external system stále uchováva pôvodný resource. Reuse môže spôsobiť nejednoznačný audit alebo provider conflict.

High-impact keys sú často derivované z immutable business identity a operation type, takže prirodzene zostávajú unikátne. Expiry odstraňuje detailný payload, nie nevyhnutne tombstone identity.

## 21. Replay protection

Signature a timestamp chránia webhook pred forged alebo príliš starým replayom, zatiaľ čo event ID dedupe chráni pred legitímnou redelivery. Obe kontroly sú potrebné.

Freshness window nesmie odmietnuť validný provider retry, ktorý kontrakt povoľuje neskôr. Provider semantics určujú, či sa overuje signed original timestamp, delivery timestamp alebo sequence.

## 22. Sequence a ordering

Duplicate handling nerieši out-of-order events. Novší state event môže doraziť pred starším a oba majú odlišné event IDs.

Consumer používa provider sequence, resource version alebo monotonic business transition. Starý event sa označí ako stale a nesmie prepísať novší authoritative state.

## 23. Partial batch idempotency

Batch má parent identity, ale každý item potrebuje vlastný operation key. Retry iba unresolved subsetu nesmie opakovať už commitnuté items.

Aggregate key bez per-item ledgeru je príliš hrubý, ak provider commitne len časť batchu. Naopak iba per-item keys bez batch completeness neuvidia stratené položky.

## 24. Sub-workflow propagation

Parent workflow vytvorí operation key a odovzdá ho sub-workflowu ako povinné contract field. Child ho používa pri external mutation a vracia state aj external reference.

Sub-workflow nesmie generovať nový random key pre každý call. Ak mení operation granularity, explicitne odvádza child key z parent identity a item subjectu.

## 25. Tenant isolation

Key namespace obsahuje verified tenant alebo je uložený v tenant-isolated store. Rovnaký payment ID v dvoch provideroch alebo tenants nesmie kolidovať.

Tenant sa neberie iba z untrusted webhook body. Viaže sa na verified endpoint, credential, provider account a policy context.

## 26. Credential a idempotency binding

Operation record eviduje credential alebo provider principal generation použitú pri attempt-e. Zmena credentialu môže meniť tenant, account alebo scope a preto je relevantná pre reconciliation.

Retry po rotation je bezpečný iba vtedy, keď nová identity smeruje na rovnaký authoritative resource a provider idempotency namespace. Inak môže rovnaký key vytvoriť operation v inom účte.

## 27. Response replay

Pri duplicate requeste systém môže vrátiť uložený business výsledok alebo reference na prebiehajúcu operáciu. Caller dostane rovnaký logical outcome bez nového effectu.

Response replay musí označiť, že ide o duplicate alebo existing operation, aby observability nezapočítala nový commit. Sensitive response sa uchováva minimalizovane.

## 28. Compensation nie je deduplication

Compensation vytvára nový business side effect, ktorý zmierňuje alebo ruší predchádzajúci commit. Nie je dôkazom, že duplicate handling funguje.

Každá compensation má vlastný operation key a approval. Automatické „create then delete duplicate“ môže byť právne, finančne alebo auditne neprijateľné.

## 29. Shared incident `AGENT-N8N-08`

Provider doručil rovnaký refund event dvakrát a n8n zároveň retryol timeoutnutý HTTP node. Workflow používal `execution_id` ako dedupe field, takže všetky tri attempts mali odlišnú identity.

Prvý request bol commitnutý, druhý provider odmietol ako duplicate podľa vlastnej heuristiky a tretí prešiel cez iný endpoint. Local execution data preto nevedeli spoľahlivo určiť výsledok.

## 30. Competing failure hypotheses

Prvá hypotéza je duplicate webhook delivery, druhá node retry po unknown outcome, tretia whole-execution retry, štvrtá parallel race pred dedupe insertom a piata cross-tenant key collision.

Evidence porovná provider event IDs, operation keys, payload hashes, claim records, execution/attempt IDs, credential tenant a external ledger. Počet n8n executions nie je počet logical operations.

## 31. Evidence preservation

Zachová sa canonical key derivation rule, raw event hash, verified tenant context, inbox record, operation state transitions, unique-constraint conflicts, provider request IDs a external resource history. Secret a celý customer payload sa neukladajú do bežného incident reportu.

Point-in-time database snapshot je dôležitý pri race condition. Neskoršia oprava records nesmie prepísať pôvodné prechody bez correction eventu.

## 32. Containment

Workflow zastaví nové mutations pre affected operation class a pokračuje iba v durable intake. Duplicate deliveries sa acknowledge podľa provider contractu, ale nevytvárajú nové business attempts.

Reconciliation vytvorí zoznam committed, absent, duplicated a unknown resources. Automatická compensation zostane vypnutá, kým owner nepotvrdí impact.

## 33. Recovery

Zavedie sa atomic inbox, canonical operation key, payload conflict check a provider-native idempotency, kde je dostupná. External datastore používa unique tenant/key constraint a auditované state transitions.

Workflow retry číta record a provider state pred mutation. Historical duplicates sa uzatvoria correction alebo compensation procesom s vlastnou identity.

## 34. Positive acceptance

Päť paralelných deliveries rovnakého eventu vytvorí jeden inbox record, jednu logical operation a presne jeden external commit. Ostatné executions vrátia existing alebo in-progress result.

Rovnaký key a payload po timeout-e vedie k rovnakému provider resource. Metrics ukážu viac attempts, ale jeden accepted side effect.

## 35. Forbidden acceptance

Dedupe nie je splnené iba použitím Remove Duplicates nodeu, timestampu alebo execution ID. Neprípustný je check-then-act bez atomic claimu a nový random key pri každom retry.

Rovnaký key s odlišným tenantom alebo payloadom sa nesmie ticho prijať. Success response bez external read-back nie je idempotency proof.

## 36. Recovery acceptance

Crash sa simuluje po external commit-e a pred local final persistom. Recovered worker musí nájsť provider resource a označiť pôvodnú operation ako committed bez nového side effectu.

Restore idempotency storeu sa testuje spolu s business data. Backup, ktorý obnoví workflow, ale stratí operation ledger, je neakceptovateľný pre high-impact scope.

## 37. Second-operation acceptance

Druhý tenant s rovnakým local business ID vytvorí odlišný namespaced key a vlastný resource. Cross-tenant lookup alebo response replay je odmietnutý.

Ďalšia legitímna operation na tom istom resource, napríklad partial refund po full-refund rejection, potrebuje nový explicitný operation type a policy, nie recyklovaný key.

## 38. Praktický idempotency record

Record zachytáva logical operation, payload identity a external outcome. State mutation je atomic a každá zmena má actor a causal reference.

```yaml
idempotency_record:
  namespace: tenant_acme/refunds
  key: refund:payment_771:full
  payload_sha256: 03ef...
  state: committed
  owner_execution: exec_7712
  attempts:
    - attempt_id: node_19_try_1
      outcome: timeout_after_send
      provider_request_id: req_44ce
    - attempt_id: recovery_read_1
      outcome: resource_found
  external_resource: refund/provider/rf_991
  credential_generation: cred_refund_acme/v17
  created_at: 2026-08-05T06:12:04Z
  committed_at: 2026-08-05T06:12:06Z
  retain_until: 2027-08-05T00:00:00Z
```

## 39. Prevádzkové metriky

Sledujú sa duplicate delivery rate, claim conflicts, attempts per operation, idempotency conflicts, unknown-state age, external commit count, store latency, expired tombstones a cross-tenant denials. Metrics používajú logical operation denominator.

Nízky duplicate count nemusí byť dobrý signál, ak systém duplicates nerozpoznáva. Testované replaye a concurrency drills overujú control priamo.

## 40. Primárne zdroje

- [n8n Docs — Webhook node](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/)
- [n8n Docs — Error handling](https://docs.n8n.io/flow-logic/error-handling/)
- [n8n Docs — All executions and retries](https://docs.n8n.io/workflows/executions/all-executions/)
- [n8n Docs — Remove Duplicates](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.removeduplicates/)
- [n8n Docs — Workflow static data](https://docs.n8n.io/code/cookbook/builtin/get-workflow-static-data/)
- [Stripe Docs — Idempotent requests](https://docs.stripe.com/api/idempotent_requests)
- [AWS Builders' Library — Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)

## 41. Zhrnutie

Duplicate delivery je normálna vlastnosť distribuovaných integrácií, nie výnimočný incident. Bez canonical business identity sa node retry, provider redelivery a execution retry násobia do nepredvídateľného počtu side effects.

Bezpečný model používa tenant-scoped operation key, atomic claim, payload conflict check, durable state machine a authoritative external reconciliation. Idempotency je prijatá až vtedy, keď concurrency, crash-after-commit, restore a second-tenant test preukážu jeden logical outcome.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Error workflows, retries a partial execution](error-workflows-retries-partial-execution.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
