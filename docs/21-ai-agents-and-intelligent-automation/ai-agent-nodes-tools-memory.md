# AI Agent nodes, tools a memory

n8n AI Agent node kombinuje chat model, tool schemas, prompt, execution state a voliteľnú memory do workflowu, v ktorom model rozhoduje, ktorý nástroj použije a s akými argumentmi. Výsledok preto nie je iba textová odpoveď: agent môže čítať externý stav, volať sub-workflow, meniť business systém alebo zastaviť na approval hranici.

Táto kapitola otvára incident `AGENT-N8N-10`. Support agent mal odpovedať na otázku zákazníka, vyhľadať relevantnú zmluvu a pripraviť refund request. Tool description však nerozlišoval read-only lookup od refund mutation, `$fromAI()` dovolil modelu vytvoriť customer ID bez deterministickej väzby na autentifikovaný subject a Redis Chat Memory používala iba krátky `sessionId`. Dvaja tenant users sa stretli v jednej memory session a agent navrhol refund pre nesprávny účet.

Nosný lifecycle je:

```text
authenticated request a tenant context
→ exact agent/workflow/model/tool generation
→ prompt a bounded tool inventory
→ input validation a memory-key resolution
→ model tool-selection decision
→ schema-constrained arguments
→ policy, approval alebo read-only execution
→ tool result a provenance
→ bounded iteration alebo termination
→ response, execution evidence a business verification
```

## 1. AI Agent node ako orchestration boundary

AI Agent node je root node, ktorý prijíma prompt, používa pripojený chat model a vyžaduje aspoň jeden tool sub-node. Model dostane descriptions a schemas dostupných tools a počas execution rozhoduje, či odpovie priamo alebo vykoná jeden či viac tool calls.

Node však nie je všeobecný policy engine. To, že model rozumie názvu nástroja, neznamená, že presadí tenant isolation, finančný limit alebo separation of duties; tieto pravidlá musia byť deterministic controls okolo tool boundary.

## 2. Tools Agent semantics

Aktuálny n8n AI Agent funguje ako Tools Agent a používa tool-calling interface. Tool schema opisuje argumenty a model vracia štruktúrovaný návrh volania, ktorý n8n následne mapuje na konkrétny tool node.

Tool calling znižuje parser ambiguity oproti voľnému textu, ale nerobí argument pravdivým. Hodnota môže byť syntakticky validné UUID a zároveň patriť nesprávnemu tenantovi, preto schema validation musí pokračovať authorization a business validation vrstvou.

## 3. Root node, sub-nodes a data-flow rozdiel

AI Agent je root node a chat model, memory, output parser a tools sú pripojené sub-nodes. Sub-node expression semantics sa môžu líšiť od bežných item-processing nodes, najmä pri viacerých input items, kde expression môže vyhodnotiť iba prvý item.

Workflow, ktorý pošle dávku tenant requests do jedného agent execution, preto môže nečakane použiť prvý customer context pre ďalšie položky. Bezpečný návrh explicitne normalizuje cardinality a typicky spúšťa jednu logical conversation alebo operation na jednu agent boundary.

## 4. Exact subject a generation

Každá execution eviduje workflow ID a published version, n8n release, AI Agent node version, model provider a model ID, tool inventory digest, prompt generation, memory backend a policy generation. Bez tejto identity sa dve odpovede s rovnakým textom môžu opierať o odlišné tools, credentials alebo memory.

Generation musí byť čitateľná v trace alebo execution metadata. Incident analysis nesmie hovoriť iba „agent použil refund tool“; potrebuje presne určiť, ktorý tool contract, credential binding a workflow version boli effective.

## 5. Prompt nie je authorization boundary

System message vysvetľuje úlohu, dostupné tools, zakázané správanie a očakávané ukončenie. Je dôležitý pre tool selection a reakciu na odmietnutie, no zostáva textovým vstupom do probabilistického modelu.

Pravidlo „nikdy nerefunduj viac než 50 €“ sa preto nepresadzuje iba promptom. Refund tool musí mať vlastný server-side limit, tenant binding, idempotency key a approval requirement pre rizikové rozsahy.

## 6. Tool inventory ako capability surface

Každý pripojený tool rozširuje capability surface agenta. Aj tool, ktorý agent „pravdepodobne nepoužije“, je dostupná možnosť a jeho credential môže mať výrazne širšie oprávnenia než zamýšľaná business operácia.

Production inventory preto obsahuje iba potrebné nástroje. Read-only lookup, create-draft a commit-mutation sa implementujú ako oddelené capabilities namiesto jedného univerzálneho HTTP toolu s voľným URL, method a body.

## 7. Tool description ako routing contract

Description musí vysvetliť, kedy sa tool používa, čo vracia, čo nemení a aké preconditions potrebuje. Vágny názov `Customer Tool` núti model hádať medzi lookupom, editáciou a refundom a zvyšuje pravdepodobnosť nesprávneho výberu.

Dobrá description používa business jazyk a negatívne hranice. Napríklad `Get customer contract` číta zmluvu pre authoritative customer ID z workflow contextu a nesmie meniť účet; refund návrh patrí samostatnému toolu.

## 8. Tool schema a argument contract

Schema určuje názvy, types, required fields a často descriptions jednotlivých argumentov. Umožňuje modelu vytvoriť strojovo spracovateľné volanie a n8n ho mapuje do node parameters.

Schema však musí obmedziť voľnosť. Enumerácie, numeric bounds a fixed server-derived fields sú bezpečnejšie než všeobecný `payload: object`; neautorizované identity sa vôbec nevystavujú ako modelom vyplniteľný parameter.

## 9. `$fromAI()` a dynamic parameters

`$fromAI()` umožňuje modelu doplniť tool parameter podľa promptu a tool contextu. Je vhodný pre hodnoty ako zhrnutie, návrh subjectu alebo vyhľadávací dotaz, ktoré sú prirodzene odvodené z jazyka a následne validované.

Nie je vhodný pre tenant ID, caller identity, credential selector, approval owner alebo idempotency key. Tieto hodnoty musia pochádzať z dôveryhodného workflow contextu a zostať immutable počas agent reasoning.

## 10. Deterministic parameter binding

Tool call sa pred execution obohatí o server-derived context: authenticated subject, tenant ID, allowed resource set, correlation ID a policy version. Model môže navrhnúť business intent, ale nesmie prepísať authority fields.

Praktický wrapper porovná modelom navrhnutý resource s allowed setom a pri rozpore tool odmietne. Odmietnutie sa vráti agentovi ako bounded error, nie ako výzva na hľadanie inej cesty k tej istej zakázanej operácii.

## 11. Call n8n Workflow Tool

Call n8n Workflow Tool presúva capability do reusable child workflowu s explicitnými inputs a outputs. Je vhodný na ukrytie credentials, deterministic validation, idempotency a provider-specific detailov pred agentom.

Child workflow je však security boundary iba vtedy, keď sám overuje caller context a nepoužíva implicitné široké credentials. Parent prompt alebo tool description nemôžu nahradiť validation v child workflowe.

## 12. App nodes ako AI tools

Mnohé app nodes možno pripojiť priamo ako AI tools. Model môže doplniť vybrané parameters, zatiaľ čo node používa uložené credential a vykoná operáciu voči providerovi.

Priamy app tool je vhodný pre nízkorizikové a úzko nakonfigurované operácie. Pri citlivej mutácii je bezpečnejší wrapper workflow, ktorý zúži operations, odstráni modelom riadené security fields a pridá business read-back.

## 13. HTTP Request a generic tools

Generic HTTP tool poskytuje veľkú flexibilitu, ale môže súčasne sprístupniť method, host, path, headers a body. Ak model ovláda viac týchto prvkov, tool sa mení na všeobecný network capability a zvyšuje SSRF, exfiltration a confused-deputy riziko.

Production návrh fixuje host a authentication, allowlistuje paths a methods a filtruje response. Interné metadata endpoints, loopback, link-local a tenant-external destinations zostávajú nedostupné aj pri prompt injection.

## 14. Code a Custom Code Tool

Code tool môže transformovať dáta alebo implementovať výpočet, no kód generovaný alebo ovplyvnený modelom nesmie automaticky získať host-level access. Task runner isolation, package allowlist, network policy a resource limits určujú skutočný blast radius.

Preferovaný pattern používa malú deterministickú funkciu s typed inputs. Shell, filesystem a process environment sa nevystavujú iba preto, že agent potrebuje „spracovať text“.

## 15. Read tools, draft tools a commit tools

Tool taxonomy oddeľuje observation od mutation. Read tool iba načíta stav, draft tool vytvorí návrh bez externého účinku a commit tool vykoná schválenú zmenu s idempotency a auditom.

Agent môže mať širokú read capability a obmedzenú draft capability, zatiaľ čo commit tool je za approval gate. Takýto design podporuje užitočnú autonómiu bez toho, aby každé reasoning rozhodnutie okamžite menilo produkciu.

## 16. Tool result contract

Tool result má typed status, authoritative identifiers, data provenance, freshness a error classification. Voľný text typu `done` neumožňuje rozlíšiť vytvorený refund, existujúci duplicate, pending provider operation alebo lokálne zlyhanie po external commit.

Result vracia minimum potrebných údajov a rediguje secrets a osobné dáta. Agent dostáva business-safe summary, zatiaľ čo plná evidence zostáva v auditnom alebo execution store podľa retention policy.

## 17. Tool errors a recoverability

Tool error sa klasifikuje ako validation, authorization, transient dependency, conflict, unknown outcome alebo permanent business rejection. Model môže retryovať iba triedy, pri ktorých je retry bezpečný a bounded.

Unknown outcome sa neprekladá na automatický nový mutation call. Workflow najprv vykoná provider read-back podľa idempotency key alebo business reference a až potom rozhodne o retry, compensation alebo human escalation.

## 18. Max iterations a termination

Max Iterations obmedzuje počet agent krokov a chráni pred slučkou tool calls. Limit však nie je business completion condition; agent môže skončiť pod limitom s nesprávnou odpoveďou alebo naraziť na limit po viacerých úspešných side effects.

Termination sa preto viaže na explicitný state: odpoveď pripravená, approval pending, operation committed, denied alebo escalated. Dosiahnutie iteration limitu vytvorí kontrolovaný failure outcome, nie tiché „best effort“ potvrdenie.

## 19. Intermediate steps a trajectory evidence

Return Intermediate Steps môže sprístupniť informácie o tool-selection trajectory. Sú užitočné pri debugovaní, evaluácii a zisťovaní, prečo model zvolil konkrétny nástroj.

Intermediate reasoning sa však nesmie považovať za authoritative audit a môže obsahovať citlivé vstupy alebo tool outputs. Production evidence preferuje štruktúrované tool-call events, parameters po redakcii, policy decisions a provider read-back.

## 20. Structured output

Require Specific Output Format pripája parser a žiada model o definovanú response schema. To zlepšuje downstream mapping a umožňuje validovať status, citations, confidence alebo escalation reason.

Structured output nerieši factual correctness. Pole `refundCreated: true` je iba model output, pokiaľ nie je naplnené z authoritative tool resultu alebo post-condition read-backu.

## 21. Streaming

Streaming posiela generovanú odpoveď klientovi priebežne, ak trigger a response mode streaming podporujú. Znižuje perceived latency, ale prvé tokeny môžu byť odoslané skôr, než skončí retrieval, approval alebo final validation.

Citlivé workflowy streamujú iba bezpečnú prezentačnú vrstvu. Agent nesmie oznámiť úspešnú mutáciu pred provider confirmation a nesmie streamovať secrets, hidden tool parameters alebo nevalidovaný retrieved content.

## 22. Memory purpose

Conversation memory uchováva vybrané predchádzajúce messages alebo summaries a poskytuje ich modelu pri ďalšom turne. Pomáha udržať kontext, referencie a používateľský cieľ bez opakovania celej histórie v každom requeste.

Memory nie je authoritative customer database ani approval ledger. Staré tvrdenie používateľa sa nesmie automaticky zmeniť na oprávnenie alebo current account state.

## 23. Session key

Session key určuje, ktoré turns patria do jednej conversation. Musí byť stabilný pre správnu reláciu a zároveň unikátny cez tenant, user, channel a prípadne business case.

Samotné `sessionId=1234` alebo email address bez tenant namespace môže kolidovať. Bezpečný key sa skladá deterministicky, napríklad z opaque tenant ID, authenticated subject ID a conversation ID, nie z modelom generovaného textu.

## 24. Memory backend a durability

Simple Memory je vhodná pre jednoduché alebo lokálne scenáre, zatiaľ čo Redis, PostgreSQL, MongoDB a ďalšie backends poskytujú externú persistence podľa node capability. Výber určuje dostupnosť, retention, concurrency a recovery semantics.

Backend health nestačí; treba overiť exact key, serialization generation a tenant partition. Po failoveri alebo upgrade môže byť store dostupný, ale agent môže čítať staré, nekompatibilné alebo nesprávne namespaced records.

## 25. Context window a memory trimming

Memory nemôže neobmedzene rásť, preto sa používa window, summary alebo retention policy. Príliš krátke okno odstráni potrebný constraint, príliš dlhé okno zvyšuje cost, latency a prompt-injection persistence.

Trimming je policy decision, nie náhodné odrezanie najstarších tokenov. Kritické facts sa znovu čítajú z authoritative systému a long-lived instructions sa nepreberajú z user conversation ako trusted policy.

## 26. Memory poisoning

Útočník môže vložiť do conversation text, ktorý sa v ďalších turns tvári ako interná inštrukcia alebo falošný business fact. Ak sa tento obsah persistuje, útok prežije pôvodný request a ovplyvní neskoršie tool calls.

Memory ingestion preto označuje role, source a trust level a môže filtrovať alebo sumarizovať untrusted content. Recovery zahŕňa quarantine konkrétnej session a invalidation memory generation, nie iba úpravu system promptu.

## 27. Cross-tenant memory leakage

Kolízia session key alebo nesprávny backend namespace môže spojiť dve konverzácie. Model potom odpovie s údajmi iného zákazníka alebo použije nesprávny account reference pri tool call.

Negative test vytvorí rovnaký local conversation ID v dvoch tenants a overí nulový cross-read. Telemetry musí evidovať hashed tenant a session partition bez logovania citlivého contentu.

## 28. Chat history verzus workflow state

Chat history je textová stopa konverzácie, zatiaľ čo workflow state obsahuje operation IDs, approval status, retries a terminal outcomes. Miešanie týchto vrstiev vedie k tomu, že model interpretuje vetu „už som to schválil“ ako platný approval token.

Durable operation state zostáva v deterministic store. Memory môže používateľovi pripomenúť, že approval bol vyžiadaný, ale commit tool číta platný approval record s expiry, reviewer identity a parameter digestom.

## 29. Memory a sub-workflows

Parent agent môže volať child agent alebo workflow, ktorý používa vlastnú memory. Každá boundary potrebuje explicitne rozhodnúť, či zdieľa conversation context, odovzdáva iba summary alebo začína novú scoped session.

Implicitné zdieľanie rovnakého session key rozširuje blast radius. Specialist child dostáva minimum contextu potrebné pre úlohu a nezdedí automaticky osobné dáta ani approval history parenta.

## 30. Model compatibility a tool calling

Nie každý chat model podporuje rovnaké tool-calling, streaming alebo structured-output semantics. Workflow preto pinne podporovaný provider/model a testuje argument generation, refusal, tool-choice a parser behavior pre exact generation.

Fallback model nie je drop-in náhrada, pokiaľ neprejde rovnakým contract testom. Pri provider incidente sa systém môže prepnúť na read-only režim alebo human handoff namiesto neovereného mutation-capable modelu.

## 31. Cost, latency a tool budgets

Každý iteration môže pridať model call, tool latency, memory read a retrieval. Bez budgetu sa jednoduchý request zmení na drahú alebo časovo nepredvídateľnú trajectory.

Budget zahŕňa max iterations, wall-clock deadline, per-tool timeout, token ceiling a mutation count. Po prekročení limitu workflow vráti bezpečný partial alebo escalation outcome a zachová correlation evidence.

## 32. Shared incident `AGENT-N8N-10`

Agent dostal request od tenant `north` a mal pripraviť refund draft. Memory key bol iba channel message ID, ktorý sa zhodoval s reláciou v tenantovi `south`; v history sa objavil customer reference z iného účtu a vágny `Customer operations` tool dovolil modelu vyplniť customer ID cez `$fromAI()`.

Model vytvoril validný tool call a n8n node ho technicky vykonal. Incident nevznikol parser chybou, ale kombináciou capability designu, untrusted dynamic identity a cross-tenant memory collision.

## 33. Containment

Prvý zásah deaktivuje mutation tools alebo publikuje read-only generation, izoluje dotknuté memory namespaces a zablokuje nové executions s neovereným session-key formatom. In-flight operations sa nezrušia bez kontroly provider state, pretože niektoré mohli commitnúť.

Tím uchová workflow/model/tool generations, redigované call events a provider references. Až potom opraví key derivation, rozdelí tools a pridá deterministic identity wrapper.

## 34. Recovery

Recovery zavedie tenant-scoped session key, oddelený read/draft/commit tool inventory a wrapper, ktorý customer ID číta z authenticated contextu. Memory sa rebuildne alebo invaliduje podľa incident scope a affected operations sa reconciliujú proti providerovi.

Canary test používa dve tenants s kolidujúcimi local IDs a zámerne škodlivý memory content. Obnova je úspešná až vtedy, keď nedôjde ku cross-readu, zakázané identity sa nedajú navrhnúť a intended read-only odpoveď ostane funkčná.

## 35. Acceptance

Pozitívny test preukáže, že agent zvolí správny read tool, použije bounded arguments, vráti provenance a ukončí trajectory v budgete. Mutation scenario musí vytvoriť iba draft alebo čakať na platný approval podľa policy.

Forbidden test skúša modelom zmeniť tenant ID, credential selector, idempotency key a approval owner. Second-operation test opakuje ten istý business request s rovnakou operation identity a musí vrátiť existujúci výsledok bez nového side effectu.

## Kontrolné otázky

- Ktoré parameters smie model vytvoriť a ktoré musia pochádzať z authenticated workflow contextu?
- Ako tool description rozlišuje read, draft a commit capability?
- Z čoho sa skladá tenant-safe memory session key?
- Čo sa stane pri unknown tool outcome alebo iteration limit?
- Ako preukážete, že fallback model zachováva tool a output contracts?

## Primárne zdroje

- [AI Agent node](https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.agent/)
- [Tools Agent](https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.agent/tools-agent/)
- [Human-in-the-loop for AI tool calls](https://docs.n8n.io/build/integrate-ai/ai-examples/human-in-the-loop-for-tools/)
