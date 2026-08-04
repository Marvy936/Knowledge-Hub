# Triggers, nodes, expressions a data mapping

n8n workflow spracúva data ako items, ktoré prechádzajú cez nodes a connections. Trigger vytvorí počiatočný execution input, action alebo core nodes ho čítajú a menia a expressions mapujú hodnoty z aktuálneho alebo predchádzajúceho execution contextu do node parameters.

Táto kapitola pokračuje v incidente `AGENT-N8N-07`. Provider poslal batch dvoch objednávok, Code node vytvoril nové output items bez zachovania väzby na pôvodné inputs a ďalší node použil výraz odkazujúci na konkrétny predchádzajúci node. Runtime nevedel jednoznačne určiť matching item a workflow použil tenant a order ID z prvého itemu aj pre druhý refund-review ticket.

Nosný data lifecycle je:

```text
trigger event alebo poll result
→ normalized input items
→ node parameter resolution
→ node execution pre item alebo batch
→ output items a item-link metadata
→ branch, merge a downstream mapping
→ schema a tenant validation
→ external action
→ execution evidence a business reconciliation
```

## 1. Trigger ako execution boundary

Trigger určuje, kedy a s akým počiatočným contextom workflow začne. Môže reagovať na HTTP webhook, pollovať API, bežať podľa schedule, čítať message broker alebo byť spustený manuálne.

Trigger success znamená prijatie alebo zistenie eventu podľa jeho semantics. Neznamená automaticky, že event je unikátny, správne zoradený alebo autorizovaný pre všetky downstream actions.

## 2. Trigger classes

Push trigger prijíma event od externého systému, polling trigger periodicky hľadá zmeny a schedule trigger vytvára execution podľa času. Message alebo stream trigger číta records z transportu s vlastným acknowledgement a delivery modelom.

Každá trieda má inú failure boundary. Webhook môže byť zopakovaný po HTTP timeoute, polling môže prekrývať časové okná a schedule môže bežať dvakrát pri nesprávnom timezone alebo failover modeli.

## 3. Manual a production trigger

Manual test trigger je dočasná interaktívna listener alebo editor operation. Production trigger používa registered endpoint, scheduler alebo subscription viazanú na published/active workflow.

Test input môže byť reprezentatívny, ale často obchádza provider signature, reverse proxy, production URL a retry behavior. Acceptance preto nepoužíva iba manual execution.

## 4. Node ako transformation alebo effect boundary

Node prijíma zero alebo viac inputs, vyhodnotí parameters a vytvorí outputs, chybu alebo side effect. Niektoré nodes iba transformujú data, iné čítajú externý systém a ďalšie vytvárajú mutation.

Vizuálna uniformita node boxov nesmie zakryť odlišný risk. Set/Edit Fields node a HTTP Request `POST` node majú zásadne inú reversibility a authorization boundary.

## 5. Core, app a trigger nodes

Core nodes riadia workflow logic, data transformation, branching, merging, waiting alebo code execution. App nodes implementujú operácie konkrétnych služieb a trigger nodes registrujú alebo zisťujú events.

Product-specific node je convenience adapter, nie nový trust model. Ak nepodporuje potrebnú API operáciu, HTTP Request node môže rozšíriť scope, ale tým rastie schema, authentication a validation zodpovednosť autora workflowu.

## 6. Items ako základný dátový model

Bežný n8n node prijíma a vracia kolekciu items. Každý item typicky obsahuje JSON data a môže odkazovať na binary data a linking metadata.

Item nie je automaticky business entity. Jeden order môže vytvoriť viac items a jeden aggregate item môže reprezentovať viac orders; explicitná business identity musí zostať v data.

## 7. JSON a binary data

JSON časť nesie štruktúrované hodnoty používané expressions a node parameters. Binary časť nesie file payload alebo reference, ktorú downstream node musí vedieť nájsť pod správnym property name.

Transformácia JSON nesmie potichu odpojiť binary reference. Execution môže byť technicky successful, ale odoslať metadata bez prílohy alebo prílohu z nesprávneho itemu.

## 8. Connections a graph

Connections určujú, kam output node pokračuje a ktorý input downstream node dostane. Graph je executable control flow; poloha, farba alebo názov node nemajú execution semantics bez connection.

Pri viacerých outputs alebo branches musí byť explicitné, ktoré conditions vedú k mutation pathu. Unconnected alebo obídený validation node môže zostať na canvase a vytvárať falošný dojem ochrany.

## 9. Node parameter resolution

Parameter môže byť fixed value alebo expression vyhodnotená v execution contextu. Resolution nastane pred alebo počas node execution podľa node semantics a pracuje s aktuálnym itemom, workflow metadata, environment variables a dostupnými previous-node data.

Parameter preview v editore je pomocný dôkaz. Produkčný run môže mať iný item count, branch, timezone alebo missing field a preto vytvoriť iný resolved value.

## 10. Expressions

Expression je dynamický výraz vložený do node parameteru. Typické references čítajú current item cez `$json`, execution metadata alebo output pomenovaného node.

Expression je code-like logic s vlastnou null, type a item-selection semantics. Musí mať input contract a testy rovnako ako malá funkcia.

## 11. Data mapping verzus transformation

Data mapping vyberá hodnotu z existujúcich inputs a priraďuje ju parameteru alebo output fieldu. Transformation mení tvar alebo význam data, napríklad normalizuje dátum, rozdeľuje batch alebo počíta derived value.

Drag-and-drop mapping môže expression vygenerovať, ale neoverí business meaning. Field `customer.id` môže byť technicky dostupný a pritom nesprávny pre tenant authorization.

## 12. Current item context

Výraz používajúci `$json` číta current item pre dané node execution. Current item je bezpečný iba vtedy, keď upstream graph zachoval intended one-to-one alebo explicit batch semantics.

Po aggregate, split alebo merge operácii sa current item meaning môže zmeniť. Autor musí znovu pomenovať entity a nespoliehať sa na pôvodný index.

## 13. Named-node references

Reference na output konkrétneho node umožňuje čítať data niekoľko krokov dozadu alebo z inej vetvy. Runtime však potrebuje vedieť, ktorý upstream item zodpovedá current itemu.

Taká reference nie je global variable lookup. Bez item linking alebo jednoznačnej branch relationship môže vybrať nesprávny item alebo skončiť chybou.

## 14. Item linking

Item linking zachováva provenance medzi output itemom a jeho input itemom. n8n túto väzbu používa, keď downstream expression žiada matching item z predchádzajúceho node.

Linking je data lineage pre runtime mapping, nie business authorization. Aj správne paired item môže obsahovať tenant ID, ktoré musí overiť policy alebo downstream resource boundary.

## 15. `pairedItem` pri custom alebo Code logic

Ak node vytvára nové items programaticky a n8n nevie väzbu odvodiť, output potrebuje explicitnú `pairedItem` informáciu. Tá určí input index a pri viacerých inputs aj input branch.

Chýbajúca väzba sa často prejaví až pri batchi alebo branchi. Single-item test prejde, pretože jediný kandidát zakryje ambiguity.

## 16. One-to-one, one-to-many a many-to-one

One-to-one transformácia môže prirodzene zachovať každý input ako jeden output. One-to-many operácia musí priradiť viac outputs k rovnakému inputu a many-to-one aggregate musí explicitne definovať, ktoré origins reprezentuje.

Downstream expression musí zodpovedať cardinality. Výber jednej customer identity z aggregate viacerých tenantov je forbidden design, nie iba mapping bug.

## 17. Multiple inputs

Merge alebo multi-input node kombinuje data z rôznych branches. Matching môže byť podľa position, field alebo node-specific mode a každý model má odlišné assumptions o completeness a ordering.

Position-based merge je krehký pri filtrovaní alebo retry. Business key matching je zvyčajne bezpečnejší, ale potrebuje uniqueness, normalization a duplicate policy.

## 18. Branching

IF, Switch alebo error route rozdelí items podľa condition. Condition musí byť vyhodnotená na authoritative fieldoch a mať explicitnú else alebo unknown cestu.

Missing field nesmie automaticky skončiť v privileged branch len preto, že expression coercion vrátila unexpected boolean. Schema validation má predchádzať security alebo financial action.

## 19. Filtering a empty output

Filter môže odstrániť všetky items a downstream node sa potom nemusí spustiť. To môže byť validný outcome, ale musí byť odlíšený od mapping error alebo silent data loss.

Workflow potrebuje metric alebo explicit result pre zero-match. Inak dashboard ukáže success, hoci žiadny business record nebol spracovaný.

## 20. Schema contracts

Každý významný node boundary má očakávané fields, types, cardinality, null policy, tenant scope a business identity. Contract môže byť dokumentovaný v node name, validation node alebo reusable sub-workflow schema.

JSON shape bez semantic contractu nestačí. Dva fields typu string môžu reprezentovať order ID a customer ID a ich zámena prejde syntakticky.

## 21. Missing, null a empty

Missing field znamená, že property neexistuje; null je explicitná absencia a empty string alebo empty array sú platné values s ďalšou semantics. Expressions a APIs ich môžu interpretovať odlišne.

Default value má byť business rozhodnutie, nie convenience fallback. Tenant ID alebo amount sa nesmú doplniť z prvého itemu, static data alebo shared defaultu.

## 22. Type coercion

External payload môže niesť číslo ako string, boolean ako text alebo timestamp bez timezone. Expression engine a node parameter môžu value konvertovať, ale implicitná coercion môže meniť comparison a routing.

Normalizačný node má vytvoriť canonical type a validation evidence. Financial amount sa spracúva ako presná decimal representation podľa downstream contractu, nie ako náhodný floating-point parse.

## 23. Dates a timezone

Schedule trigger, date expressions a API timestamps závisia od instance alebo workflow timezone a explicitného offsetu v data. Rovnaký local time môže označovať dva okamihy pri daylight-saving prechode.

Canonical event time sa uchová s timezone alebo UTC a zároveň sa odlišuje ingestion time. Poll windows a dedupe používajú authoritative event identity, nie iba rounded timestamp.

## 24. Pinned a mocked data

Pinned data zjednodušujú development tým, že editor používa stabilný node output bez opakovaného external callu. Sú test fixture, nie production evidence.

Pinned payload môže byť starý, zjednodušený alebo z iného tenanta. Pred publish sa musí overiť, že production trigger a downstream nodes neboli hodnotené iba proti nemu.

## 25. Batching a pagination

Nodes môžu spracovať viac items naraz alebo postupne čítať paginated API. Batch size ovplyvňuje memory, rate limits, partial failure a mapping cardinality.

Pagination termination potrebuje cursor alebo explicitnú last-page condition. Chybný cursor môže opakovať records a vytvoriť duplicate side effects aj bez webhook retry.

## 26. Looping a repeated execution

Loop Over Items alebo podobný control opakuje branch pre subsets items. Loop state musí byť viazaný na execution a nesmie používať shared static data ako cross-execution cursor bez concurrency control.

Partial loop failure vytvára mixed outcome. Retry celej execution bez item-level idempotency môže zopakovať už úspešné iterations.

## 27. Static workflow data

Workflow static data môže uchovávať malý stav medzi executions podľa platform semantics. Nie je to všeobecná transactional database a pri high concurrency môže vytvoriť race alebo stale read.

Critical dedupe, tenant authorization alebo financial ledger nepatria do best-effort shared state. Potrebujú external authoritative store s atomic constraints.

## 28. Shared incident `AGENT-N8N-07`

Code node normalizoval batch tak, že vytvoril nový object pre každú objednávku, ale nepreniesol item-link provenance. Downstream expression požiadala o `tenantId` z node `Verify Tenant` a pri druhom iteme nemala jednoznačný matching origin.

Single-item manual test prešiel. Produkčný batch použil prvý available tenant context a vytvoril refund-review ticket pre order B v tenantovi A.

## 29. Competing failure hypotheses

Prvá hypotéza je chýbajúci `pairedItem`, druhá position-based merge po filtrovaní, tretia stale pinned test data, štvrtá default tenant expression a piata provider payload, ktorý zmenil batch ordering. Každá predpovedá inú first divergence.

Audit preto porovná raw trigger items, normalized outputs, linking metadata, resolved parameters a downstream request. Iba final ticket body nestačí na rozlíšenie mapping paths.

## 30. Evidence preservation

Zachová sa payload digest, per-item business IDs, item count, node input/output digests, paired-item metadata, branch decisions, resolved sensitive parameter references a downstream request correlation. Raw PII sa uloží iba v controlled evidence store.

Healthy single-item a healthy batch comparator ukážu, či defect závisí od cardinality. Reprodukcia musí použiť rovnakú workflow version a node generation.

## 31. Containment

Mutation branch sa zastaví pre batch size väčší než jeden a workflow môže pokračovať read-only validáciou. Events sa durably odložia s original identity, aby provider retries nevytvorili neviditeľnú paralelnú queue.

Default tenant mapping sa odstráni alebo zmení na hard failure. Missing provenance sa nesmie „opraviť“ výberom itemu index zero.

## 32. Recovery

Code alebo custom node zachová explicitné item links a downstream node používa current normalized item s validated tenant a order identity. Merge sa zmení na key-based contract s uniqueness checkom.

Regression suite obsahuje one-to-one, one-to-many, filtered branch, reordered batch, duplicate key, missing field a two-tenant test. Každý mutation používa idempotency key viazaný na business entity.

## 33. Positive acceptance

Dvoj-item batch vytvorí dva správne correlated outputs a každý downstream request nesie intended tenant, order a idempotency key. Execution evidence umožní sledovať každý output späť k exact trigger itemu.

Zero-item a malformed-item cases majú explicitný non-mutation outcome. Success count sa zhoduje s business ledgerom.

## 34. Forbidden acceptance

Akceptácia nesmie používať iba jeden item, pinned data alebo preview resolved value. Neprípustný je fallback na first item, shared tenant default alebo position merge bez ordering invarianty.

Workflow nesmie skončiť `success`, ak critical identity field chýba. Taký item musí byť odmietnutý, quarantined alebo routed na human review.

## 35. Recovery acceptance

Replay historical affected batchu v side-effect-disabled prostredí vytvorí správne mappingy a rovnaké digests pri opakovaní. Safe production canary potom vykoná bounded side effect pre explicitne povolené test entities.

Acceptance overí aj expression errors a branch unknown path. Recovery nie je kompletná, ak iba happy path prestal zlyhávať.

## 36. Second-batch acceptance

Druhý batch zmení ordering, obsahuje iný tenant a jednu filtered položku. Remaining outputs musia zostať správne linked a nesmú zdediť identity z odstráneného itemu.

Tento test odhaľuje implicitné index assumptions. Rovnaký count a poradie by mohli defect skryť.

## 37. Praktický mapping contract

Mapping contract dokumentuje entity, cardinality, provenance a failure policy. Slúži ako review artifact pre workflow authora aj prevádzku.

Contract neobsahuje secrets a nepredpokladá, že expression preview je runtime proof. Acceptance ho porovná s execution evidence.

```yaml
mapping_contract:
  boundary: Normalize Orders -> Create Refund Review
  input:
    cardinality: one-or-more
    entity_key: providerEventId + orderId
    required: [tenantId, orderId, amount, currency]
  output:
    cardinality: one-per-valid-input
    preserves_item_link: true
    business_key: refund-review/{providerEventId}/{orderId}
  forbidden:
    - first-item fallback
    - cross-tenant aggregation
    - position-only merge after filtering
  invalid_item_policy: quarantine-with-reason
```

## 38. Prevádzkové metriky

Sledujú sa items per execution, zero-output success, expression resolution errors, mapping validation rejects, duplicate business keys, item-link failures, branch distribution, batch latency a cross-tenant negative tests. Metriky sa viažu na workflow version a node generation.

Náhly pokles output count môže byť validná zmena trafficu alebo silent filter defect. Alert sa uzatvára porovnaním s upstream event a downstream business counts.

## 39. Primárne zdroje

- [n8n Docs — Data mapping](https://docs.n8n.io/data/data-mapping/)
- [n8n Docs — Referencing data in the UI](https://docs.n8n.io/data/data-mapping/data-mapping-ui/)
- [n8n Docs — Item linking concepts](https://docs.n8n.io/data/data-mapping/data-item-linking/item-linking-concepts/)
- [n8n Docs — Item linking for node creators](https://docs.n8n.io/data/data-mapping/data-item-linking/item-linking-node-building/)
- [n8n Docs — Expressions](https://docs.n8n.io/code/expressions/)
- [n8n Docs — Nodes](https://docs.n8n.io/workflows/components/nodes/)
- [n8n Docs — Workflow executions](https://docs.n8n.io/workflows/executions/)

## 40. Zhrnutie

Trigger vytvára execution, nodes menia alebo používajú items a expressions riešia dynamic parameter mapping. Bez explicitnej entity identity, cardinality a item provenance môže technicky validný graph vykonať side effect nad nesprávnymi data.

Bezpečný workflow odlišuje mapping od transformation, testuje multi-item a branch scenarios, zachováva item linking a odmieta critical missing fields. Acceptance končí downstream business reconciliation a druhým batchom s iným orderingom, nie editor previewom alebo single-item manual runom.
