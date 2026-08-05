# Error workflows, retries a partial execution

Error handling v n8n určuje, ako sa technická alebo business chyba zmení na execution state, ďalšiu vetvu workflowu, retry, notification a recovery rozhodnutie. Produkčný workflow nemôže považovať každý exception za bezpečný retry ani každý zelený execution status za potvrdený business outcome, pretože pred zlyhaním už mohli byť niektoré side effects commitnuté.

Táto kapitola otvára incident `AGENT-N8N-08`. Refund workflow spracoval dávku požiadaviek, pri devätnástom iteme dostal timeout po tom, čo provider refund v skutočnosti zapísal. Node mal povolený retry, error branch neskôr pokračovala a execution skončila ako success, takže centrálne error workflow sa neaktivovalo. Operátor následne retryol celú execution s aktuálne uloženou verziou workflowu a vytvoril druhý pokus o už vykonaný refund.

Nosný failure lifecycle je:

```text
trigger a exact operation identity
→ node input a intended side effect
→ attempt, timeout alebo explicitná business rejection
→ committed, rejected alebo unknown external outcome
→ node on-error policy
→ execution status a error-workflow dispatch
→ retry alebo quarantine decision
→ reconciliation authoritativeho systému
→ recovery a second-operation proof
```

## 1. Error nie je jeden stav

Technický error znamená, že node alebo workflow nedokončil očakávaný execution contract. Môže ísť o connection failure, timeout, invalid response, expression error, credential failure alebo nedostupnú dependency. Rovnaký symptom však nehovorí, či externá operácia neprebehla, prebehla čiastočne alebo bola commitnutá bez doručenia odpovede.

Business rejection je odlišná. API môže korektne vrátiť, že objednávka nie je refundovateľná, účet je zablokovaný alebo payload porušuje doménové pravidlo. Taký výsledok môže byť successful transport a zároveň očakávaný negatívny business outcome, ktorý sa nemá opakovať ako transient failure.

## 2. Failure subject

Každé zlyhanie sa viaže na exact workflow, published alebo saved generation, execution ID, node ID, item identity, attempt a external operation identity. Bez tejto väzby sa retry stáva novou neurčitou operáciou a audit nevie rozlíšiť opakovanie od nezávislej požiadavky.

Failure record preto obsahuje aj trigger event ID, tenant, credential reference, provider request ID a idempotency key. Timestamp a error text sú pomocné signály, nie stabilná identita.

## 3. Node-level on-error policy

Node settings určujú, či chyba zastaví workflow, pokračuje cez bežný output alebo sa presmeruje cez samostatný error output. Toto rozhodnutie mení execution semantics, observability aj to, či sa aktivuje workflow-level error handler.

Policy sa volí podľa doménového kontraktu. Read-only enrichment môže bezpečne pokračovať s explicitným `unknown` výsledkom, zatiaľ čo payment mutation má pri nejasnom outcome zastaviť ďalšie mutácie a prejsť na reconciliation.

## 4. Stop workflow

Stop policy ukončí execution pri chybe nodeu a zachová failure ako viditeľný execution outcome. Je vhodná, keď downstream kroky predpokladajú complete a trusted výsledok alebo keď ďalší side effect bez neho zvyšuje škodu.

Stop však automaticky nevracia už vykonané kroky. Workflow engine neposkytuje distribuovanú transakciu cez cudzie SaaS API, database a messaging služby; rollback musí byť navrhnutý ako samostatná compensation alebo reconciliation cesta.

## 5. Continue cez regular output

Pokračovanie cez bežný output môže zachovať priechod workflowu aj pri node failure. Tento režim je nebezpečný, ak downstream nodes nevedia rozlíšiť normálny payload od error objektu alebo missing fields.

Použitie potrebuje explicitný envelope, napríklad `status`, `error_class`, `attempts` a `authoritative_outcome`. Bez neho môže workflow poslať zákazníkovi success správu po tom, čo kritický krok zlyhal.

## 6. Continue cez error output

Samostatný error output umožňuje oddeliť úspešný a chybný tok bez okamžitého ukončenia celej execution. Je vhodný pri per-item spracovaní, kde sa validné items dokončia a chybné sa presunú do quarantine alebo manual review.

Error branch musí skončiť explicitným terminal stateom. Ak iba zaloguje chybu a vráti sa do success vetvy, execution môže pôsobiť úspešne, hoci časť business práce zostala nedokončená.

## 7. Retry on fail

Node retry opakuje konkrétny node attempt podľa jeho settings. Pomáha pri transient failures, ako krátky rate limit, connection reset alebo dočasná nedostupnosť služby, ak je operácia retry-safe.

Retry nie je bezpečnostná vlastnosť sama o sebe. Ak prvý attempt mohol commitnúť side effect, ďalší attempt potrebuje rovnaký business idempotency key alebo predchádzajúci authoritative read-back.

## 8. Retry taxonomy

Retryable failure je taký, pri ktorom rovnaký logical operation môže byť zopakovaný bez zmeny významu a bez nekontrolovaného duplicate effectu. Permanent failure, ako invalid schema, forbidden scope alebo business rejection, sa po rovnakom vstupe pravdepodobne nezmení.

Unknown-outcome failure je tretia kategória. Timeout po odoslaní requestu nepreukazuje, že server operáciu nevykonal; pred retry sa číta provider resource, operation status alebo idempotency record.

## 9. Backoff a retry budget

Retry interval chráni dependency aj vlastných workerov pred tight loopom. Backoff a jitter znižujú synchronizované opakovanie viacerých executions po spoločnom výpadku, ale nemenia semantiku operácie.

Každý workflow potrebuje retry budget viazaný na deadline, provider rate limits a business urgency. Po vyčerpaní budgetu sa item presunie do waiting, quarantine alebo human review namiesto nekonečného opakovania.

## 10. Workflow-level error workflow

n8n umožňuje priradiť workflow, ktorý sa spustí pri zlyhaní iného workflowu a začína Error Trigger nodeom. Taký handler centralizuje notification, incident enrichment a bezpečné uloženie failure metadata.

Error workflow nie je automatická compensation transakcia. Nemá slepo retryovať pôvodnú mutation ani predpokladať, že dostal všetky runtime crashes; potrebuje vlastnú dostupnosť, credentials, rate limits a monitoring.

## 11. Error Trigger contract

Error Trigger dostáva kontext o zlyhanej execution a workflowe. Handler z neho vytvorí normalized incident envelope, priradí severity a rozhodne, či stačí alert, quarantine alebo okamžitý kill switch.

Payload schema sa verzuje, pretože downstream incident store a notifier nesmú závisieť od náhodného error message textu. Povinné polia zahŕňajú execution reference, workflow generation, failed node, tenant a correlation IDs.

## 12. Kedy sa error workflow nespustí

Ak node failure workflow vedome absorbuje cez continue policy a execution skončí ako success, workflow-level error handler nemusí dostať signal. Rovnako engine alebo host crash môže prerušiť proces skôr, než application-level handler vykoná svoju logiku.

Produkčná detekcia preto kombinuje error workflows s external monitoringom executions, queue, process health a business reconciliation. Absencia error notification nie je dôkaz úspechu.

## 13. Stop And Error

Stop And Error node umožňuje zmeniť doménovú podmienku na explicitné workflow failure. Používa sa napríklad vtedy, keď validation zistí chýbajúci tenant, reconciliation odhalí neznámy outcome alebo required approval neexistuje.

Tento node má niesť structured a redacted context, nie secrets alebo celý customer payload. Účelom je presadiť failure semantics a spustiť správny recovery path.

## 14. Execution status

Execution môže byť running, waiting, successful, failed alebo iný platformový stav podľa konkrétnej verzie a cesty. Status opisuje engine lifecycle, ale nemusí reprezentovať business completeness.

Successful execution môže obsahovať error-output items, skipped branches alebo downstream notification failure, ktorú workflow toleroval. Business status sa preto vedie samostatne a reconciliuje s authoritative systémom.

## 15. Partial execution

Partial execution vzniká, keď časť nodes, items alebo external side effects prebehla a zvyšok nie. Typický batch môže mať sedemnásť committed položiek, jednu unknown a dvadsaťdva ešte nezačatých.

Retry celej execution bez checkpointu a idempotency môže zopakovať už commitnuté položky. Recovery pracuje s per-item ledgerom a pokračuje iba od unresolved stateov.

## 16. Per-item outcome

Každý item má vlastný operation key, attempt count, terminal state a external reference. Aggregate execution `success=39, failed=1` nestačí, ak nie je známe, ktorá konkrétna položka zlyhala a či jej side effect zostal unknown.

Outcome envelope rozlišuje `committed`, `rejected`, `not_attempted`, `retryable`, `unknown` a `compensated`. Tieto stavy umožňujú bezpečné pokračovanie aj audit.

## 17. Cardinality a completeness

Workflow musí porovnať input cardinality s terminal outcome cardinality. Stratený item po filter, branch alebo merge môže spôsobiť tichú partial execution bez exceptionu.

Completeness invariant vyžaduje, aby každý vstup skončil práve v jednom povolenom terminal state. Duplicitný outcome alebo chýbajúci item je hard failure, aj keď všetky nodes svietia zeleno.

## 18. Branch a merge failure

Viac vetiev môže dokončiť prácu v odlišnom čase a s odlišnou error policy. Merge nesmie implicitne považovať chýbajúcu vetvu za prázdny úspech, ak business contract vyžaduje oba výsledky.

Join používa stable correlation key a explicitné timeout semantics. Po timeout-e sa rozhodne, či je výsledok partial, rejected alebo waiting, namiesto tichého pokračovania.

## 19. Unknown external outcome

Najrizikovejší failure je strata odpovede po odoslaní mutation. Client nevie, či request nedorazil, provider ho spracúva alebo ho commitol a odpoveď sa stratila.

Prvý recovery krok je authoritative query podľa idempotency key, provider request ID alebo business resource identity. Nová mutation je až posledná možnosť po dôkaze, že predchádzajúca nebola commitnutá.

## 20. Retry failed execution

n8n umožňuje retryovať failed execution s pôvodným workflowom alebo s aktuálne uloženou verziou. Obe voľby používajú predchádzajúce execution data, ale majú inú code/config generation.

Retry s original workflowom zlepšuje reprodukovateľnosť, no zachováva pôvodný defect. Retry s current saved workflowom môže obsahovať opravu, ale zároveň mení experiment; manifest musí zaznamenať pôvodnú aj novú generation a side-effect state.

## 21. Retry scope

Retry scope môže byť node attempt, item, sub-workflow, celá execution alebo provider event. Tieto vrstvy sa nesmú zamieňať, pretože každá opakuje iný rozsah práce.

Bez explicitného scope môže node retry päťkrát a operátor následne retryovať execution, zatiaľ čo provider ešte dvakrát redeliveruje webhook. Výsledkom nie sú dva, ale potenciálne desiatky attempts jednej business operácie.

## 22. Execution data a retention

Recovery potrebuje zachované inputs, outputs, errors, timestamps a node run data primerané risku. Retention a pruning však môžu odstrániť evidence skôr, než sa incident vyšetrí.

Citlivé payloady sa minimalizujú a redigujú. Stabilné IDs, hashes, generation references a external operation references sa uchovávajú dlhšie než raw personal data, ak policy dovolí.

## 23. Custom execution data

Custom execution metadata môže pridať searchable business identifiers alebo operation class, ak daná n8n edícia túto funkciu podporuje. Zlepšuje triage bez potreby prehľadávať celý payload.

Metadata nesmie obsahovať secret alebo citlivý obsah. Slúži ako index k authoritative business ledgeru, nie ako jeho náhrada.

## 24. Quarantine a dead-letter model

Item, ktorý prekročil retry budget alebo má unknown outcome, sa presunie do durable quarantine s dôvodom, evidence a next action. Nemá sa stratiť v notification chate alebo iba v execution UI.

Quarantine consumer je read-before-write a idempotent. Manual operator môže rozhodnúť o retry, compensation, rejection alebo escalation bez vytvorenia novej neprepojenej operácie.

## 25. Notification semantics

Notification oznamuje failure, impact a required action, nie iba stack trace. Obsahuje tenant, workflow, execution, affected item count, operation class, known/unknown outcomes a link na secure evidence.

Alert delivery má vlastný failure path. Critical incident sa nespolieha na jediný Slack alebo email node v rovnakom zlyhávajúcom runtime plane.

## 26. Error-handler isolation

Centrálne error workflow používa úzke read-only credentials a oddelené rate limits. Ak zdieľa rovnaký provider, queue a secret ako primary workflow, spoločný výpadok môže zablokovať aj reporting.

Handler nesmie vykonávať high-impact compensation bez approval a reconciliation. Jeho default je preserve, classify, notify a contain.

## 27. Observability

Trace prepája trigger, nodes, retries, sub-workflows a external calls, zatiaľ čo audit eviduje sensitive mutations a approvals. Metrics sledujú failure rate, retry amplification, partial completion, unknown outcomes a age quarantine.

Dashboard bez per-item denominatora môže skrývať chybu. `99 % successful executions` nie je relevantné, ak zostávajúce percento obsahuje všetky payment mutations.

## 28. Shared incident `AGENT-N8N-08`

Refund batch obsahoval štyridsať items. Prvých osemnásť bolo commitnutých, devätnásty provider spracoval, ale odpoveď timeoutla; node ho zopakoval a potom poslal error item do pokračujúcej vetvy. Zvyšné položky sa dokončili a execution bola označená ako success.

Error workflow sa preto nespustilo. Operátor retryol execution s aktuálne uloženou verziou, ktorá zmenila mapping, no nečítala provider stav. Bez per-item ledgeru sa opakovali už commitnuté operácie.

## 29. Competing failure hypotheses

Prvá hypotéza je provider necommitol timeoutnutý request. Druhá je commit bez response, tretia duplicate provider redelivery, štvrtá nesprávna continue policy a piata current-workflow retry s odlišným mappingom.

Každá hypotéza predpovedá iný provider audit, idempotency record, node attempt timeline a item cardinality. Error text samotný ich nerozlíši.

## 30. Evidence preservation

Zachová sa original trigger payload hash, event ID, workflow saved/published generation, execution a retry IDs, node settings, per-item operation keys, provider request IDs, responses, timestamps a external resource state. Current configuration po oprave sa uchová oddelene.

Evidence freeze predchádza ďalšiemu bulk retry. Ak containment vyžaduje okamžité zastavenie, najprv sa aktivuje kill switch a potom sa exportujú read-only artifacts.

## 31. Containment

Refund mutation route sa zastaví a nové events sa bezpečne queueujú alebo rejectujú podľa contractu. Read-only reconciliation porovná všetky items s provider ledgerom a označí committed, absent a unknown stavy.

Automatický retry sa vypne pre unknown outcomes. Customer communication nepoužíva success template, kým business ledger nie je complete.

## 32. Recovery

Workflow zavedie per-item operation ledger, idempotency key, explicitný error output terminal state a central error workflow. Retry decision číta provider resource pred každou mutation a pokračuje iba pre preukázane absent operations.

Already duplicated refunds sa riešia podľa business a legal policy, nie technickým delete. Opravený workflow sa nasadí canary spôsobom a overí na representative batchi.

## 33. Positive acceptance

Transient failure pred commitom sa zopakuje v retry budgete a vytvorí presne jeden external side effect. Execution aj business ledger ukážu rovnakú operation identity a terminal outcome.

Error workflow dostane failed execution, notification obsahuje korektný scope a quarantine item je dohľadateľný. Successful batch má complete per-item cardinality.

## 34. Forbidden acceptance

Nie je prípustné retryovať timeoutnutú mutation iba preto, že node hlási error. Rovnako sa neprijíma green execution, ak error branch, skipped item alebo unknown provider outcome nemá business closure.

Manual retry bez pôvodnej operation identity je nová nekontrolovaná operácia. Notification success nenahrádza reconciliation.

## 35. Recovery acceptance

Simulovaný timeout po provider commit-e musí viesť k read-back a bez ďalšej mutation. Simulovaný pre-commit connection failure môže retryovať rovnaký logical operation a skončiť jedným commitom.

Error-handler outage sa tiež testuje. External monitor musí zachytiť failed alebo stalled execution aj bez application notification.

## 36. Second-operation acceptance

Druhý batch s iným tenantom a kombináciou success, business rejection a transient failure prejde bez zdieľania operation keys. Každý item skončí v jednom terminal state a žiadny retry neprekročí tenant boundary.

Test sa opakuje po workflow update, aby current-saved retry nezamenil generation ani side-effect ledger. Pôvodný incident nesmie byť reprodukovateľný cez starú execution alebo redelivered event.

## 37. Praktický failure envelope

Failure envelope musí byť čitateľný pre error workflow aj incident systém. Hodnoty sú references a classification, nie raw secret alebo celý customer payload.

```json
{
  "schema": "n8n-failure/v2",
  "workflow_id": "wf_refund_batch",
  "workflow_generation": "sha256:8e1a...",
  "execution_id": "exec_7712",
  "node_id": "refund-provider",
  "tenant_id": "tenant_acme",
  "event_id": "evt_provider_9821",
  "item_id": "refund_1044",
  "operation_key": "refund:tenant_acme:payment_771:full",
  "attempt": 2,
  "failure_class": "timeout-after-send",
  "external_outcome": "unknown",
  "provider_request_id": "req_44ce",
  "next_action": "reconcile-before-retry"
}
```

## 38. Prevádzkové metriky

Sledujú sa failed executions, absorbed node errors, retry attempts na logical operation, retry amplification, partial batches, unknown outcomes, quarantine age, error-handler delivery a reconciliation latency. Metriky sa segmentujú podľa workflowu, node type, tenant a operation impactu.

Cieľom nie je nulový počet errors. Dôležité je, aby failure zostal viditeľný, bounded a obnoviteľný bez duplicate alebo cross-tenant side effectu.

## 39. Primárne zdroje

- [n8n Docs — Error handling](https://docs.n8n.io/flow-logic/error-handling/)
- [n8n Docs — Error Trigger](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.errortrigger/)
- [n8n Docs — Stop And Error](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.stopanderror/)
- [n8n Docs — Node settings](https://docs.n8n.io/workflows/components/nodes/)
- [n8n Docs — All executions and retry failed workflows](https://docs.n8n.io/workflows/executions/all-executions/)
- [n8n Docs — Execution data](https://docs.n8n.io/workflows/executions/)
- [n8n Docs — Workflow settings](https://docs.n8n.io/workflows/settings/)

## 40. Zhrnutie

Error workflow, node retry a execution retry riešia odlišné vrstvy. Bez explicitnej failure taxonomy a external outcome state môže automatizácia znásobiť side effects práve počas recovery.

Bezpečný model viaže každé zlyhanie na exact operation identity, rozlišuje transient, permanent a unknown outcome, vedie per-item ledger a uzatvára recovery authoritative read-backom. Engine success je iba technický signál; accepted stav vyžaduje complete business cardinality, no-forbidden evidence a druhú nezávislú operáciu.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Credentials, secrets a access control](credentials-secrets-access-control.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
