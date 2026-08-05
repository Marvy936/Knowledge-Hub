# Human approval pre citlivé tool calls

Human approval v n8n môže pozastaviť AI Agent pred vykonaním vybraného toolu a odoslať reviewerovi názov nástroja a navrhnuté parameters. Reviewer tool call schváli alebo zamietne; schválenie pokračuje execution, zamietnutie zruší konkrétnu akciu a agent dostane informáciu o odmietnutí.

Táto kapitola pokračuje v incidente `AGENT-N8N-10`. Po oprave memory isolation bol refund commit tool presunutý za approval. Approval message však zobrazovala iba sumu a zákaznícke meno, nie authoritative tenant, account ID, policy reason ani parameter digest. Reviewer schválil request po dlhom čakaní, hoci customer state a refund limit sa medzitým zmenili, a workflow vykonal stale intent.

Nosný lifecycle je:

```text
agent proposes sensitive tool call
→ deterministic normalization a policy classification
→ immutable approval envelope a parameter digest
→ authorized reviewer resolution
→ request delivery cez oddelený channel
→ approve, deny alebo expiry
→ freshness a precondition revalidation
→ exactly-once commit alebo safe cancellation
→ provider read-back a audit closure
```

## 1. Approval ako policy gate

Approval nie je všeobecné potvrdenie, že agent „vyzerá rozumne“. Je to rozhodnutie nad konkrétnym toolom, exact parameters, business subjectom, policy generation a časovo obmedzeným stavom.

Gate preto vzniká pred side effectom a po deterministic validation. Reviewer nesmie schvaľovať payload, ktorý sa po kliknutí ešte modelom alebo expression logikou zmení.

## 2. Kedy používať human review

Human review je vhodný pre nezvratné akcie, externú komunikáciu, delete, finančné operácie, high-value rozhodnutia a regulované procesy. Môže sa používať aj počas postupného budovania dôvery v nový agent workflow.

Nie každé tool call potrebuje človeka. Read-only lookup alebo nízkorizikový draft môže pokračovať automaticky, zatiaľ čo commit tool, vysoká suma alebo policy exception vyžaduje explicitnú approval.

## 3. Selective oversight

n8n umožňuje pripojiť human review iba k vybraným tools alebo k širšej skupine. Selective model znižuje reviewer fatigue a zachováva automatizáciu pre bezpečné kroky.

Výber však musí vychádzať z capability class, nie zo samotného názvu node. Generic HTTP tool alebo sub-workflow môže obsahovať mutation aj vtedy, keď sa volá `Lookup`, preto sa klasifikácia viaže na contract a downstream behavior.

## 4. Approval channel

Approval možno doručiť cez n8n Chat, Slack, Discord, Telegram, Teams, Gmail, WhatsApp, Google Chat alebo Outlook podľa podporovaných node capabilities. Interaction channel môže byť odlišný od approval channelu, napríklad používateľ komunikuje cez chat a reviewer rozhoduje v Teams.

Channel je iba transport. Identitu reviewerov, routing, confidentiality, message retention a compromise response musí presadzovať surrounding identity a access design.

## 5. Reviewer identity

Approval record obsahuje stable reviewer subject, organization alebo tenant, role a authentication assurance. Display name alebo channel nickname nestačí, pretože sa môže meniť alebo kolidovať.

Workflow overí, že reviewer patrí do allowed approver setu pre danú policy a nie je zároveň initiator, ak separation of duties vyžaduje nezávislú osobu. Delegácia a zastupovanie majú vlastnú expiráciu a audit.

## 6. Approval request content

Reviewer musí vidieť business intent, tool name, normalized parameters, target tenant/resource, expected effect, risk class, policy reason a expiry. Pri update alebo delete sa zobrazí aj relevantný before state a predpokladaný after state.

Message nemá zobrazovať secrets, raw tokens alebo zbytočné osobné dáta. Redakcia však nesmie odstrániť údaj potrebný na odhalenie wrong-tenant alebo wrong-resource chyby.

## 7. `$tool` variable

n8n human-review message môže použiť `$tool.name` a `$tool.parameters`, aby zobrazila tool a arguments navrhnuté agentom. Je to užitočný základ pre transparentnosť reviewerovi.

Tieto values však reprezentujú modelom navrhnutý call, nie celý security context. Workflow k nim pridá server-derived tenant, caller, policy decision, operation ID a normalized parameter digest.

## 8. `$fromAI()` a reviewer visibility

Parameters doplnené cez `$fromAI()` sú súčasťou tool inputu, ktorý reviewer vidí. Tým sa znižuje riziko, že človek schváli abstraktný zámer a model neskôr zvolí inú konkrétnu hodnotu.

Pred zobrazením sa values canonicalizujú a validujú. Reviewer nesmie dostať nejednoznačný amount string, lokálny customer label alebo relatívny čas bez authoritative identity a timezone.

## 9. Immutable approval envelope

Approval envelope je immutable snapshot schvaľovaného intentu. Obsahuje operation ID, tool contract version, exact normalized parameters, caller a tenant, policy generation, preconditions, created-at, expiry a cryptografický alebo stabilný digest.

Commit path prijme iba envelope, ktorého digest zodpovedá schválenému recordu. Ak sa parameter zmení, vznikne nový approval request, nie tichá aktualizácia pôvodného schválenia.

## 10. Operation identity

Každý citlivý request má canonical business operation key nezávislý od n8n execution ID a channel message ID. Approval, retry a provider call sa viažu na túto identitu.

Opakované kliknutie alebo redelivery approval eventu preto nevytvorí nový refund. Durable ledger vráti existujúci terminal outcome alebo pokračuje v tej istej operation state machine.

## 11. Expiry

Approval má krátku, risk-based platnosť. Po expiry sa click zaznamená ako stale decision a tool sa nevykoná, aj keď channel technicky odošle validný callback.

Expirácia chráni pred zmeneným resource stateom, policy a credential generation. High-impact delete môže mať minúty, kým nízkorizikový draft môže mať dlhšie okno.

## 12. Freshness a revalidation

Schválenie znamená súhlas s intentom za konkrétnych preconditions. Tesne pred commitom workflow znovu načíta current resource version, tenant ownership, limit, duplicate state a relevantnú policy.

Ak sa state zmenil, operation prejde do `reapproval_required` alebo `conflict`, nie do automatického commit. Reviewer dostane nový diff medzi schváleným a current stavom.

## 13. Approve semantics

Approve transition uloží reviewer identity, timestamp, envelope digest a channel evidence. Až durable zápis approval stateu povoľuje commit workerovi pokračovať.

UI alebo chat response `approved` nie je sám authoritative state. Workflow musí vedieť obnoviť rozhodnutie po restart, queue retry alebo webhook redelivery bez opätovného pýtania alebo dvojitého vykonania.

## 14. Deny semantics

Deny zruší konkrétny tool call a poskytne reason code alebo bezpečný komentár. Agent môže informovať používateľa, navrhnúť alternatívu alebo eskalovať, ale nesmie obísť zákaz výberom ekvivalentného toolu.

System message vysvetľuje, ktoré tools sú gated a ako reagovať na odmietnutie. Deterministic policy navyše blokuje semantic bypass, napríklad refund cez generic HTTP tool po zamietnutí `Create Refund`.

## 15. Timeout semantics

Ak reviewer neodpovie, workflow skončí v explicitnom `expired` alebo `timed_out` stave. Timeout nie je approval ani implicit deny s nejasným business outcome.

Escalation môže poslať nový request inému reviewerovi, ale pôvodný token sa invaliduje. Paralelné approval messages nesmú vytvoriť súťaž dvoch platných rozhodnutí bez jasnej quorum policy.

## 16. Waiting executions

Human review pozastaví workflow a vytvorí waiting state. Prevádzka musí počítať s retention, worker restartom, upgradeom a maximálnou dobou, počas ktorej execution a jeho approval data zostanú dostupné.

Waiting state sa nepovažuje za dokončenú business operáciu. Dashboard rozlišuje pending approval, expired, denied, committed a reconciliation-required outcomes.

## 17. Channel callback security

Approval link alebo callback je bearer capability, pokiaľ nie je viazaný na authenticated reviewer session. Token musí byť high entropy, scoped na jednu operation, krátkodobý a po použití neplatný.

Reverse proxy, chat preview bot alebo email security scanner môže link navštíviť automaticky. GET request preto nesmie vykonať approval; finálne rozhodnutie používa authenticated, anti-CSRF a explicitný action flow podľa channel capability.

## 18. Replay protection

Callback event môže byť doručený viackrát alebo používateľ klikne opakovane. Ledger vykoná atomic compare-and-set z `pending` do `approved` alebo `denied` a ďalšie events iba vrátia current state.

Replay protection sa viaže na operation key a envelope digest. Nové n8n execution ID alebo nový channel message ID nesmú obísť už terminal approval state.

## 19. Separation of duties

Niektoré operácie vyžadujú, aby initiator, agent owner a approver neboli tá istá osoba alebo service account. Workflow vyhodnotí subject relationships pred odoslaním requestu aj pri callbacku.

Emergency break-glass môže povoliť výnimku, ale potrebuje silnejšie authentication, reason, kratšiu platnosť a následný independent review. Samotné členstvo v admin channeli nie je dostatočná evidencia.

## 20. Quorum a viacstupňové schválenie

High-value zmena môže vyžadovať dve nezávislé approvals alebo sekvenčný business a security review. State machine eviduje required quorum, order a ktoré parameter views dostal každý reviewer.

n8n built-in human review rieši základné approve/deny flow; komplexné quorum sa môže implementovať samostatným Wait a approval workflowom. Dizajn nesmie predstierať dvojité schválenie tým, že jednu správu vidia dvaja ľudia.

## 21. Approval a subagents

Human review funguje aj v subagentovi použitom ako tool iného agenta. Parent execution však musí rozumieť, že child je waiting, denied alebo approved, a nesmie interpretovať dlhé čakanie ako tool failure vhodný na retry.

Approval envelope identifikuje effective leaf tool a jeho parameters, nie iba parent tool `Support specialist`. Reviewer musí vedieť, aký skutočný side effect child agent navrhuje.

## 22. Approval a memory

Conversation memory môže obsahovať vetu, že používateľ akciu schválil. Takýto text nemá žiadnu authority, pretože approval record vzniká iba cez definovaný reviewer channel a signed alebo authenticated callback.

Po schválení sa do memory môže vložiť bezpečný summary outcome. Commit tool však vždy číta durable approval ledger a ignoruje modelom vytvorený claim `approval=true`.

## 23. Approval a idempotency

Po approve môže worker zlyhať po provider commit, ale pred uložením local success. Retry musí použiť rovnaký idempotency key a najprv prečítať provider state.

Approval sa nespotrebuje spôsobom, ktorý znemožní recovery tej istej operation. Zároveň sa nesmie použiť na nový parameter set alebo druhý side effect.

## 24. Approval a credential binding

Reviewer schvaľuje operation voči konkrétnemu provider tenantovi a effective principalovi. Credential alias bez target account identity je nedostatočný, pretože mapping sa môže medzi requestom a commitom zmeniť.

Envelope eviduje logical credential role a provider account fingerprint. Commit revaliduje binding generation; pri zmene credential vznikne reapproval alebo controlled operator decision.

## 25. Notifications a confidentiality

Approval channel môže uchovávať message dlhšie než n8n execution. Request preto minimalizuje osobné dáta, používa private destination a zohľadňuje export, forwarding a channel administrator access.

Sensitive attachments sa neposielajú ako voľné files, ak stačí scoped link do interného review UI. Link overuje identity a tenant boundary pri každom otvorení.

## 26. Reviewer fatigue

Príliš veľa approval requests vedie k mechanickému klikaniu a znižuje kvalitu kontroly. Policy preto gates len high-risk capabilities a request zobrazuje zrozumiteľný diff a reason.

Metrics sledujú approval rate, deny rate, time-to-decision, expiry a reapproval. Vysoká 100-percentná approval rate bez denies nie je automaticky úspech; môže signalizovať neúčinnú formalitu.

## 27. Failure of approval channel

Slack, email alebo chat môže byť nedostupný, callback sa môže stratiť alebo credential exspirovať. Workflow zachová pending state a nevykoná side effect iba preto, že notification delivery zlyhala.

Fallback channel sa aktivuje podľa policy a zachová rovnaký envelope a operation identity. Multi-channel delivery nesmie vytvoriť viac platných approval tokens bez atomic coordination.

## 28. Audit evidence

Audit record obsahuje request creator, agent/workflow/model/tool generations, envelope digest, reviewer subject, decision, timestamp, reason, channel, expiry, precondition read-back, commit outcome a provider reference. Redigované tool parameters zostávajú dostatočné na rekonštrukciu rozhodnutia.

n8n execution history a channel message sú doplnkové evidence. Authoritative ledger musí prežiť workflow deletion, retention pruning a channel cleanup podľa compliance requirements.

## 29. Shared incident `AGENT-N8N-10`

Refund request na 45 € bol správne poslaný na approval. Message však ukázala iba meno a sumu, approval token nemal expiry a customer record sa po odoslaní requestu zlúčil s iným accountom.

Reviewer klikol o dva dni neskôr. Workflow vykonal tool s pôvodným local customer ID, ale current provider mapping už smeroval na iný authoritative account; approval bol technicky validný, no intent bol stale.

## 30. Containment

Tím deaktivuje commit tool alebo nastaví policy na deny-all, invaliduje outstanding approval tokens a zastaví nové requests bez complete envelope. Pending operations sa inventarizujú podľa operation ID a provider references.

Reviewer channels sa nezmažú pred uchovaním evidence. Každá už schválená, ale nedokončená operation sa reconciliuje, pretože provider side effect mohol prebehnúť aj pri local failure.

## 31. Recovery

Recovery zavedie immutable envelope, expiry, reviewer authorization, precondition version a provider account fingerprint. Callback prejde atomic transition a commit bezprostredne pred mutation znovu načíta current state.

Test zahŕňa stale approval, replay, wrong reviewer, changed credential a two-tenant collision. Systém musí bezpečne odmietnuť každý variant a stále povoliť current, správne scoped approval.

## 32. Acceptance

Pozitívny test vytvorí approval request s úplným contextom, authorized reviewer ho schváli a exactly-once commit sa potvrdí provider read-backom. Deny test musí zrušiť tool bez alternatívneho bypassu.

Forbidden test skúša zmeniť parameters po approval, použiť token po expiry a schváliť ako neautorizovaný subject. Second-operation test opakuje callback a execution retry a musí vrátiť rovnaký terminal outcome bez druhého side effectu.

## Kontrolné otázky

- Čo presne je immutable predmetom approval rozhodnutia?
- Ktoré preconditions sa tesne pred commitom znovu validujú?
- Ako sa approval token viaže na reviewer identity, operation key a expiry?
- Čo sa stane pri deny, timeout, channel outage a replay?
- Kde je ledger, ktorý prežije pruning n8n execution history?

## Primárne zdroje

- [Human-in-the-loop for AI tool calls](https://docs.n8n.io/build/integrate-ai/ai-examples/human-in-the-loop-for-tools/)
- [Wait node](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.wait/)
- [AI Agent node](https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.agent/)
