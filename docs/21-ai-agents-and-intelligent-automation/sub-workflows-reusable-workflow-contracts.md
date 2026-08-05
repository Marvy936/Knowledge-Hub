# Sub-workflows a reusable workflow contracts

Sub-workflow oddeľuje opakovateľnú časť automatizácie do samostatného workflowu, ktorý parent workflow volá cez explicitný input a output contract. Reuse znižuje duplicitu, ale zároveň vytvára novú distributed dependency: parent a child môžu mať odlišnú lifecycle generation, credentials, tenant context, retry policy a execution outcome.

Táto kapitola pokračuje v incidente `AGENT-N8N-08`. Refund parent workflow očakával child input `order_id` a jeden output na každý vstup. Reusable sub-workflow bol zmenený na `payment_id`, filtroval rejected items a v production sa publikovala iba časť závislostí. Parent sa spustil s novým saved child contractom, ale starou published parent generation a niektoré položky sa stratili bez explicitného erroru.

Nosný reusable-contract lifecycle je:

```text
business capability a owner
→ parent/child stable identities
→ versioned input schema a tenant context
→ call mode, item cardinality a timeout
→ child execution s bounded credentials
→ versioned output/error contract
→ parent reconciliation a completeness proof
→ coordinated promotion a rollback
→ compatibility a second-caller acceptance
```

## 1. Sub-workflow ako capability

Sub-workflow nie je iba vizuálne zoskupenie nodes. Je to callable capability s vlastným ownerom, inputs, outputs, side effects, dependencies a failure semantics.

Analógia s funkciou je užitočná, ale neúplná. Child môže byť samostatná execution, pracovať s externými systémami, čakať, retryovať a mať odlišný deployment lifecycle.

## 2. Parent a child identity

Parent workflow volá exact child workflow ID alebo vybraný workflow podľa n8n node configuration. Release manifest eviduje obe stable identities aj ich saved/published generations.

Display name nestačí, pretože sa môže zmeniť alebo kolidovať. Promotion musí overiť, že reference v target environment-e smeruje na intended child, nie na lokálny workflow s podobným názvom.

## 3. Execute Sub-workflow Trigger

Child workflow začína Execute Sub-workflow Trigger nodeom, ktorý prijíma call z Execute Sub-workflow alebo relevantnej tool cesty. Trigger definuje, aké input data child očakáva.

Trigger contract je authority pre caller mapping. Child nemá tajne čítať fields, ktoré schema nepopisuje, ak ich potrebuje pre tenant, authorization alebo idempotency.

## 4. Input modes

Input môže prijať všetky dáta, fields definované v UI alebo schema odvodenú z JSON example podľa aktuálnych n8n možností. Voľný passthrough zrýchľuje prototypovanie, ale zvyšuje coupling na shape parent payloadu.

Produkčný reusable workflow preferuje explicitné required a optional fields, types a semantic descriptions. Unknown fields sa buď odmietnu, alebo ignorujú podľa versioned policy.

## 5. Schema nie je iba typ

Field `amount: number` nehovorí currency, precision, povolený rozsah ani či ide o gross alebo net hodnotu. Contract obsahuje aj semantic invarianty a source authority.

Tenant, operation key a approval reference majú silnejší status než bežné business fields. Child ich overuje pred prvým side effectom a nespolieha sa na display label.

## 6. Required a optional fields

Required field je nevyhnutný na bezpečné vykonanie capability. Missing tenant, resource ID alebo operation key vedie k explicitnému failure, nie k defaultu odvodenému z prvého itemu.

Optional field má zdokumentovaný default a failure boundary. Default credential tenant alebo production region je nebezpečný, ak caller zabudne hodnotu.

## 7. Contract version

Input a output schema majú version nezávislú od názvu workflowu. Additive optional field môže byť backward compatible, zatiaľ čo rename, type change alebo zmena cardinality je breaking change.

Version sa prenáša v call envelope a zapisuje do execution metadata. Child môže dočasne podporovať dve verzie cez explicitný adapter, nie cez heuristické guessovanie.

## 8. Caller compatibility

Každý caller má inventory požadovanej contract version a supported child releases. Change review kontroluje všetkých parents, tools alebo agents, ktoré capability volajú.

Reusable workflow nie je bezpečný, ak sa testuje iba s jedným najnovším callerom. Starší scheduled alebo rarely used parent môže zlyhať až po týždňoch.

## 9. Input mapping

Parent mapuje svoje items na child contract. Mapping musí zachovať item identity, tenant, operation key a source references a overiť types pred callom.

Expression, ktorá pri viac items vyberie nesprávny linked item, môže poslať validný payload pre zlý business subject. Pre sensitive fields sa používa explicitný per-item mapping a invariant check.

## 10. Item cardinality

Execute Sub-workflow môže spracovať items podľa configured mode a child môže vrátiť rovnaký, menší alebo väčší počet outputs. Contract musí presne uviesť očakávanú cardinality transformáciu.

`one input → one terminal output` je častý bezpečný model. Filter, fan-out alebo aggregation potrebuje explicitné parent-child correlation keys a completeness pravidlá.

## 11. Item linking

n8n item linking uchováva provenance medzi input a output items. Pri custom code alebo transformáciách môže byť potrebné nastaviť `pairedItem`, aby downstream expressions vybrali správny upstream item.

Sub-workflow boundary nesmie zničiť provenance, najmä ak child reorders alebo filters items. Business-critical join sa nespolieha iba na implicitné poradie; používa stable item ID.

## 12. Output contract

Child vracia business result envelope, nie náhodný output posledného nodeu. Envelope obsahuje item ID, operation state, external reference, warnings, error classification a contract version.

Output musí rozlíšiť committed, rejected, unknown a not-attempted. Empty output nie je automaticky success ani „nič na spracovanie“.

## 13. Terminal output

Každý input má presne jeden terminal outcome alebo explicitný fan-out record. Parent porovná input a output cardinality a zastaví sa pri missing alebo duplicate correlation.

Child success bez terminal outputu je contract breach. Parent nemá pokračovať do customer notification len preto, že Execute Sub-workflow node technicky skončil.

## 14. Error contract

Child môže failnúť execution alebo vrátiť per-item error envelope podľa capability designu. Rozhodnutie musí byť konzistentné a zdokumentované, aby parent vedel, či sa aktivuje workflow-level error handler.

Systemic failure, ako credential alebo schema mismatch, typicky zastaví call. Očakávaná business rejection môže byť normalizovaný terminal outcome.

## 15. Wait for completion

Caller môže čakať na child completion alebo používať oddelený asynchronous pattern podľa node a design možností. Synchronous call zjednodušuje result propagation, ale viaže latency, timeout a worker capacity oboch workflows.

Asynchronous child potrebuje durable task identity, callback alebo polling a parent continuation state. Fire-and-forget bez completion ledgeru nie je reusable contract.

## 16. Timeout semantics

Parent timeout nepreukazuje, že child sa zastavil. Child môže pokračovať alebo už commitnúť external side effect, zatiaľ čo caller označí call ako failed.

Timeout contract definuje cancellation support, unknown outcome a reconciliation. Parent nesmie automaticky zavolať child znovu s novým operation key.

## 17. Retry ownership

Retry môže vlastniť parent, child alebo external operation layer, ale nie všetky bez spoločného budgetu a identity. Inak sa amplification násobí cez nested retries.

Contract uvádza retryable error classes, max attempts a ownera. Child vracia `retry_after` alebo terminal classification, nie generic error, ktorý parent interpretuje ľubovoľne.

## 18. Idempotency propagation

Parent vytvorí stable operation key a child ho používa pri side effects. Ak child fan-outuje viac operations, derivuje deterministic child keys a vracia ich parentovi.

Nový sub-workflow execution ID nesmie meniť business identity. Retry parentu aj child-u zostáva viazaný na rovnaký operation record.

## 19. Transaction boundary

Parent a child executions nevytvárajú jednu ACID transakciu cez všetky dependencies. Parent môže commitnúť lokálny state, child external mutation a notification môže následne zlyhať.

Contract preto definuje commit point, compensation ownera a reconciliation authority. „Child failed“ neznamená automatický rollback parent side effectu.

## 20. Credential boundary

Child používa credentials, ktoré zodpovedajú jeho capability a tenant scope. Parent nemá posielať plaintext secret ako input ani delegovať broader authority, než child potrebuje.

Credential binding je environment-specific dependency. Promotion workflow JSON bez target credential mapping nepreukazuje, že child bude volať správny provider account.

## 21. Tenant context

Verified tenant sa prenáša ako trusted context a child ho porovná s credential, resource a operation key. User-supplied tenant field bez verification nie je dostatočný.

Shared child môže obsluhovať viac tenants iba s end-to-end isolation. Cache, static data, idempotency records a logs nesmú miešať contexts.

## 22. Authorization

Parent má authority požiadať child o konkrétnu operation class; child znovu overuje policy pred side effectom. Caller name alebo project membership nie je automaticky business authorization.

Sensitive capability vyžaduje approval reference a immutable subject. Child odmietne approval pre iný resource, amount alebo tenant.

## 23. Resource budgets

Nested workflows zdieľajú CPU, memory, concurrency, provider limits a execution storage. Veľký parent fan-out môže vytvoriť stovky child executions a vyčerpať queue alebo database.

Contract obsahuje max items, payload size, concurrency a deadline. Caller batchuje alebo queueuje prácu namiesto nekontrolovaného fan-out.

## 24. Cycles a recursion

Sub-workflow dependency graph nesmie vytvoriť neúmyselný cycle alebo unbounded recursion. Dynamic workflow selection zvyšuje riziko, že child nepriamo zavolá parent.

Release validation zostaví dependency graph a presadí max depth. Legitímna recursion potrebuje termination invariant a bounded side effects.

## 25. Reuse granularity

Príliš malý child vytvára vysokú orchestration overhead a rozptýlené debugging. Príliš veľký reusable workflow sa stáva monolitom s množstvom conditional behavioru a credentials.

Dobrá capability má cohesive business purpose, stabilný contract a jasný owner. Reuse sa nevolí iba podľa počtu duplikovaných nodes.

## 26. Pure a impure sub-workflows

Pure transformation child nemení externý stav a ľahšie sa testuje a retryuje. Impure child vykonáva API alebo database mutations a potrebuje idempotency, authorization a audit.

Contract označuje side-effect class. Caller nesmie predpokladať, že „utility workflow“ je bezpečný, ak bol neskôr rozšírený o mutation node.

## 27. Testing child samostatne

Child má fixtures pre valid, invalid, boundary a multi-item inputs. Testuje types, semantics, cardinality, item linking, errors a forbidden tenant access bez potreby parent workflowu.

Pinned alebo synthetic data je test evidence, nie production outcome. Mutation tests používajú sandbox provider alebo read-only mode.

## 28. Contract tests parent-child

Integration test spustí exact parent a child generations a porovná actual envelope s schema. Test zahŕňa breaking old caller, retry, timeout a partial child output.

Contract test je release gate pre obe strany. Child change nemôže prejsť iba na základe vlastného unit-style testu.

## 29. Observability

Trace prepája parent execution, child execution, contract version, item ID, operation key a external request. Bez tohto linku incident vyzerá ako dve nesúvisiace workflows.

Metrics sledujú child call latency, error class, cardinality mismatches, contract-version usage a callers na deprecated version. Audit eviduje sensitive child mutations a approvals.

## 30. Deployment ordering

Breaking contract vyžaduje expand-migrate-contract poradie. Najprv child podporí starú aj novú verziu, potom sa migrujú parents a až po dôkaze sa stará verzia odstráni.

Nasadenie child first bez compatibility môže rozbiť starých callers. Parent first bez dostupného new child contractu zlyhá opačne.

## 31. Source control identity

Source control prenáša workflow definitions, ale target environment potrebuje správne child references, credentials, variables a publication state. Same Git commit neznamená automaticky same effective dependency graph.

Promotion manifest preto uvádza parent/child IDs alebo stable logical mapping, saved digest, published version a environment bindings. Read-back overí loaded graph.

## 32. Shared incident `AGENT-N8N-08`

Refund child zmenil input z `order_id` na `payment_id` a začal filtrovať rejected items. Development parent bol aktualizovaný, ale production pull načítal saved definitions a stará published parent generation stále posielala pôvodný field.

Child použil fallback lookup a pre časť items našiel resource, pre časť vrátil empty output. Parent neoveril cardinality a označil batch za dokončený, hoci niektoré refunds zostali absent a jeden bol retryovaný.

## 33. Competing failure hypotheses

Prvá hypotéza je input schema mismatch, druhá wrong child reference, tretia stale published parent, štvrtá credential/tenant binding drift a piata item-linking strata po filteri.

Evidence porovná parent/child saved a published generations, call payloads, contract versions, output cardinality, references, credential IDs a source-control promotion record. Samostatný child success run nevylučuje integration defect.

## 34. Evidence preservation

Zachovajú sa exact workflow JSON digests, published versions, dependency graph, input/output schema, call payload hashes, parent-child execution links, item IDs, operation keys a target environment bindings. Current fixed definitions sa neprepisujú cez incident snapshot.

Execution data sa rediguje, ale fields potrebné na contract reconstruction ostanú dostupné. Chýbajúci output sa eviduje ako defect, nie prázdny success.

## 35. Containment

Parent route sa prepne na no-new-mutations alebo queue a child breaking version sa suspenduje. Existing in-flight calls sa reconciliujú podľa operation ledgeru, nie bulk retryom.

Deprecated callers sa inventoryzujú a blocked call dostane explicitný contract error. Fallback field guessing sa vypne pre sensitive operations.

## 36. Recovery

Child dočasne podporí versioned adapter, parent odošle explicitný contract version a completeness check a deployment manifest viaže exact saved/published generations. Credential a tenant mapping sa overia v target environment-e.

Po migrácii všetkých callers sa starý contract odstráni cez controlled release. Historical executions ostanú reprodukovateľné s pôvodnou schema.

## 37. Positive acceptance

Parent odošle validný multi-item input a child vráti presne jeden terminal envelope pre každý item s rovnakou correlation a operation identity. External side effects sú v intended tenantovi a audit prepája obe executions.

Invalid alebo old contract dostane explicitné rejection bez mutation. Timeout po commit-e vedie k reconciliation, nie k druhému child callu s novým key.

## 38. Forbidden acceptance

Reusable workflow nie je accepted iba preto, že sa dá vybrať v Execute Sub-workflow node. Neprípustné sú implicitné fields, empty output ako success, unversioned breaking change a credential inherited cez plaintext input.

Parent nesmie ignorovať cardinality alebo child error state. Rovnaký display name v target instance nie je dependency proof.

## 39. Recovery acceptance

Deployment drill nasadí backward-compatible child, migruje dva parents a potom odstráni starú verziu. Old caller je pred odstránením detegovaný a po odstránení controlled rejected.

Child crash po external commit-e sa obnoví cez rovnaký operation key. Parent dostane existing committed result bez duplicate side effectu.

## 40. Second-caller acceptance

Druhý parent z iného projektu a tenant scope použije rovnakú capability cez vlastný credential mapping a operation namespace. Nemôže čítať ani ovplyvniť prvého caller-a.

Test odhalí hidden dependency na parent node name, item order alebo shared static data. Reuse je preukázaný až nezávislým callerom.

## 41. Praktický contract manifest

Manifest spája logical capability, schema, runtime dependency a policy. Je uložený mimo secrets a používa sa pri review, promotion a incident reconstruction.

```yaml
subworkflow_contract:
  capability: refunds.execute
  contract_version: 2.1.0
  workflow_logical_id: wf_refund_executor
  input:
    required:
      - tenant_id:string
      - payment_id:string
      - operation_key:string
      - amount_minor:integer
      - currency:string
    max_items: 100
  output:
    cardinality: one_terminal_result_per_input
    states: [committed, rejected, unknown, not_attempted]
  side_effect_class: financial_mutation
  retries_owned_by: child
  approval_required_over_minor: 100000
  supported_callers: [wf_refund_batch_v5, wf_manual_refund_v3]
```

## 42. Prevádzkové metriky

Sledujú sa calls podľa contract version, deprecated callers, schema rejects, cardinality mismatches, parent-child latency, nested retry amplification, child failure rate, wrong-reference detections a cross-tenant denials. Metrics sa viažu na capability, nie iba workflow display name.

Nulové schema rejects môžu znamenať kompatibilitu alebo chýbajúcu validation. Periodické negative a old-caller tests overujú enforcement.

## 43. Primárne zdroje

- [n8n Docs — Sub-workflows](https://docs.n8n.io/flow-logic/subworkflows/)
- [n8n Docs — Execute Sub-workflow](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.executeworkflow/)
- [n8n Docs — Execute Sub-workflow Trigger](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.executeworkflowtrigger/)
- [n8n Docs — Item linking](https://docs.n8n.io/data/data-mapping/data-item-linking/)
- [n8n Docs — Item linking for node creators](https://docs.n8n.io/data/data-mapping/data-item-linking/item-linking-node-building/)
- [n8n Docs — Workflow executions](https://docs.n8n.io/workflows/executions/)

## 44. Zhrnutie

Sub-workflow znižuje duplicitu iba vtedy, keď je navrhnutý ako versioned capability. Bez input/output, cardinality, error, idempotency a deployment contractu presúva coupling z canvasu do skrytého runtime správania.

Bezpečný reusable workflow zachováva item a tenant identity, explicitne vlastní retries a side effects, koordinovane sa promuje s callers a preukazuje compatibility. Accepted stav vyžaduje samostatný child test, parent-child contract test, recovery po unknown outcome a druhého nezávislého caller-a.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Idempotency a duplicate-event handling](idempotency-duplicate-event-handling.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Source control a environments →](source-control-environments.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
