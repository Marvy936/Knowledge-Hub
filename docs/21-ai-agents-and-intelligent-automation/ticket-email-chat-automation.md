# Ticket, email a chat automation

Ticket, e-mail a chat automation spája jazykový model s externou komunikáciou a procesnými záznamami. Najväčšie riziko nevzniká pri klasifikácii textu, ale v okamihu, keď systém zamení draft za autorizovanú správu, display name za príjemcu, conversation za business record alebo channel notification za potvrdené rozhodnutie.

## 1. Business outcome

Cieľom je zrýchliť intake, routing, enrichment, drafting, follow-up a status communication bez straty ownershipu, SLA, identity alebo dôvernosti. Automatizácia má znižovať manuálnu prácu, nie maskovať nevybavené požiadavky zeleným workflow statusom.

Ticket closure alebo sent message nie sú automaticky vyriešený problém.

## 2. Exact communication subject

Subject envelope zahŕňa tenant, mailbox alebo workspace, ticket project a issue ID, immutable message ID, thread alebo conversation ID, sender principal, recipients, channel, timestamps, attachments, classification, locale, SLA state a current record version.

Subject line, display name a chat text nie sú stabilné identity.

## 3. Channel semantics

E-mail je store-and-forward správa s recipients a threading heuristics. Chat je conversation stream s membership a edit/delete semantics. Ticket je process record s workflow, fields, comments, ownership a SLA.

Jednotný „message“ abstraction nesmie skryť rozdielne authority a retention pravidlá.

## 4. Intake

Inbound event sa autentifikuje, normalizuje a deduplikuje pred modelom. Systém zachová raw reference, provider delivery ID a trusted headers.

Forwarded content a quoted history sa označia oddelene od aktuálneho sender inputu.

## 5. Sender identity

From header, chat display name alebo ticket reporter môže byť spoofed, delegated alebo external. Identity resolution používa provider principal ID, tenant a verified domains.

Model nesmie z textu odvodiť, že odosielateľ je approver alebo service owner.

## 6. Recipient identity

Pred send sa recipienti resolvujú na exact mailbox, user, group alebo channel ID. Distribution group a shared mailbox majú iný blast radius než individuálny používateľ.

Ambiguous alias vedie k hold, nie k výberu najpopulárnejšieho kontaktu.

## 7. Draft versus send

Generate, save draft, request approval a send sú štyri odlišné operations. Modelový výstup je najprv draft artifact s digestom.

Send tool prijme len approved digest, exact recipient set a current thread state.

## 8. Ticket routing

Klasifikácia môže navrhnúť request type, component, priority a owner queue. Deterministic rules overujú allowed values, tenant scope, escalation policy a required fields.

Priority sa nesmie znižovať iba podľa sentimentu alebo model confidence.

## 9. SLA

SLA clock a breach risk pochádzajú z ticket systemu, nie z agent memory. Reassignment, pending-customer status a calendar generation menia effective deadline.

Agent nesmie pozastaviť SLA bez autorizovaného workflow transition.

## 10. Jira Service Management extensibility

Aktuálna Atlassian developer dokumentácia pre Jira Service Management opisuje APIs, webhooks a automation actions a uvádza, že nové extensibility smeruje na Forge, zatiaľ čo nové Connect apps už nemožno publikovať. Architecture preto pinne extension model a nepovažuje legacy automation za budúci baseline.

Automation action môže volať remote systems, ale potrebuje vlastnú idempotency, auth a result verification.

## 11. E-mail threading

In-Reply-To, References a provider thread ID sa zachovajú. Subject-prefix matching je slabá heuristika a môže spojiť dve odlišné požiadavky.

Automatický reply nesmie pridať citlivú históriu do externého threadu.

## 12. Chat membership

Channel membership sa môže zmeniť medzi draftom a sendom. Pred citlivou správou sa revaliduje recipient set a external guests.

Private channel name nie je dôkaz, že všetci členovia majú need-to-know.

## 13. Attachments

Attachment sa skenuje, klasifikuje, identifikuje digestom a spracuje oddelene od body. Model nikdy nesmie vykonať macro, script alebo link získaný z prílohy.

Generated summary odkazuje na exact attachment version.

## 14. Prompt injection

Inbound message môže prikázať agentovi poslať secrets, zmeniť priority alebo ignorovať approval. Text je business data, nie system instruction.

Tool schemas nepovoľujú recipients alebo credentials prevzaté priamo z untrusted textu bez resolution gate.

## 15. PII a confidentiality

Classification policy rozhoduje, ktoré polia možno poslať modelu a do ktorého channelu možno vrátiť odpoveď. Redaction sa vykoná pred inference a rehydration až v trusted post-processing, ak je potrebná.

Logs nesmú uchovávať celé mailbox payloads ako default.

## 16. Cross-channel correlation

Ticket, e-mail a chat môžu patriť k jednej business case, ale correlation potrebuje stable case ID. Fuzzy matching podľa názvu zákazníka môže spojiť cudzie prípady.

Každý channel si zachová vlastný authoritative record.

## 17. Idempotency

Provider môže redeliver webhook alebo workflow môže retry po timeoute. Stable operation ID viaže action type, case ID, recipient set a content digest.

Duplicate send sa kontroluje u providera aj v local outbox ledger.

## 18. Outbox pattern

Business transaction najprv uloží intended communication do outboxu. Sender worker vykoná delivery a zapíše provider message ID.

Tým sa oddelí case state od nestabilného network callu a umožní reconciliation.

## 19. Unknown delivery

Timeout po send requeste neznamená failure. Systém hľadá provider message ID, dedupe header alebo outbox correlation.

Blind retry môže zákazníkovi poslať viac protichodných správ.

## 20. Approvals

Approval envelope obsahuje exact content, recipients, attachments, channel, classification a expiry. Reviewer vidí, či ide o internú poznámku, external reply alebo broadcast.

Edit po approval vytvorí nový digest a zruší pôvodné povolenie.

## 21. Power Automate approval boundaries

Aktuálna Power Automate dokumentácia umožňuje approverom reagovať cez e-mail, approval center alebo Teams a podporuje first-to-respond aj everyone-must-approve patterns. Zároveň dokumentuje channel mismatches a limit, pri ktorom flow čakajúci dlhšie než 28 dní zlyhá, hoci approval môže zostať v action center.

Durable business process preto nesmie zamieňať flow execution lifetime za approval record lifetime.

## 22. Human-in-the-loop connector

Microsoft human-in-the-loop connector používa explicitné assignee identities a podporuje request-for-information a multistage approval, pričom niektoré operations sú preview. Production workflow musí pinovať connector behavior, timestamps a environment.

Actionable e-mail nie je universal channel pre všetkých user types.

## 23. Auto-response classes

Bez approvalu možno poslať iba presne definované low-risk responses, napríklad acknowledgment s case ID a verejným SLA. Personalized diagnosis, policy interpretation, security statement, refund promise alebo account change vyžadujú reviewer alebo deterministic policy.

Allowlist je založený na intent a data class, nie na model confidence.

## 24. Escalation

Agent eskaluje pri low confidence, conflicting data, VIP alebo regulated subject, angry threat, security indicator, repeated contact, missing entitlement alebo unsupported language. Escalation package obsahuje summary aj raw references.

Automatizácia nesmie zmeniť „needs human“ na silent queue bez ownera.

## 25. Tone a factuality

Tone policy nesmie meniť fakty, záväzky alebo legal meaning. Model oddelí known facts, planned actions a estimates.

„We fixed the issue“ je zakázané bez business verification.

## 26. Message edits a deletes

Chat edit alebo ticket comment update môže zmeniť dôkaz. Audit uchová provider version alebo event history podľa retention policy.

Delete request sa propaguje do caches, embeddings a derived summaries, ak právny dôvod nevyžaduje hold.

## 27. Localization

Language detection a translation sú derived artifacts. Critical identifiers, numbers, dates a approval choices sa validujú po preklade.

Model nesmie preložiť product name alebo command tak, že zmení target.

## 28. Observability

Merajú sa misroutes, duplicate sends, wrong-recipient near misses, approval expiry, unresolved tickets auto-closed, SLA regressions, human rewrite rate, sensitive-data blocks a unknown deliveries. Open a sent counts nestačia.

Metrics sa segmentujú podľa channelu, intentu a automation class.

## 29. Incident AGENT-OPS-15

Security workflow vytvorí draft containment notice pre konkrétneho service ownera. Recipient resolver nájde osobu aj distribution group s rovnakým aliasom a model zvolí group podľa predchádzajúcej popularity.

Draft obsahuje identity details a incident hypotheses.

## 30. Unauthorized send

Approval card ukazuje display name, nie immutable recipient set. Medzitým sa membership skupiny zmení a workflow po approval odošle citlivý text širšiemu publiku.

Ticket je následne automaticky prechodovaný na Resolved, pretože message provider vrátil success.

## 31. Containment

Zablokujú sa external send, ticket close a group recipients. Outbox ostane v `held` stave a incident commander dostane exact recipient diff.

Knowledge answer aj security proposal sa označia ako suspect generations.

## 32. Recovery

Nesprávni recipienti dostanú correction a podľa možností sa vykoná recall alebo message deletion. Ticket sa reopenne, SLA sa koriguje a audit zachytí exposure scope.

Správny owner dostane nový draft s novým digestom a approval.

## 33. Positive acceptance

Acknowledge sa odošle raz správnemu recipientovi, ticket ostane open do authoritative resolution, approval viaže exact content a recipient set a provider read-back vráti message ID. Citlivá príloha sa neodošle do channelu s guest členmi.

## 34. Forbidden acceptance

Display name, sent status, model confidence alebo approval bez digestu nesmú byť acceptance. Agent nesmie auto-close security ticket, odpovedať celej group namiesto osoby ani prevziať recipienta z message body.

## 35. Recovery acceptance

Po unknown send sa reconciliation rozhodne podľa provider evidence bez duplicate message. Po wrong-recipient incidente sa scope exposure preukáže z membership snapshotu, correction sa doručí a case sa uzavrie až po business owner acceptance.

Druhý test redeliveruje rovnaký webhook a musí vytvoriť jednu správu.

## 36. Practical communication envelope

Communication envelope robí z draftu immutable subject, ktorý možno bezpečne schváliť a doručiť. Recipient resolution sa vykoná pred approvalom a opakuje sa tesne pred sendom, aby sa zachytila zmena membershipu alebo classification.

```yaml
communication:
  case_id: SEC-2481
  channel: email
  sender_principal: mailbox://soc-notify
  recipients:
    resolved_ids: [user://service-owner-42]
    groups_allowed: false
  content:
    draft_digest: sha256:example
    classification: confidential
    attachments: []
  approval:
    required: true
    approver_role: incident-commander
    expires_at: 2026-08-05T18:30:00Z
  delivery:
    operation_id: notify:SEC-2481:sha256-example
    unknown_outcome_behavior: reconcile
  case_transition:
    on_sent: keep-open
    close_requires: business-resolution-proof
```

Contract musí prejsť testom ambiguous aliasu, zmenenej group membership, webhook redelivery, provider timeout a editovaného draftu po approvale. Každý z týchto scenárov má skončiť holdom, novým digestom alebo reconciliation, nie silent sendom.

## 37. Operational ownership

Mailbox owner spravuje sender identity a retention, service-desk owner workflow fields a SLA, security alebo privacy owner classification a automation owner model, prompts a connector generations. Bez tohto rozdelenia sa incident môže presúvať medzi tímami bez jedného vlastníka end-to-end outcome-u.

Escalation queue musí mať capacity SLO. „Routed to human“ bez prevzatia a deadline je iba iný typ strateného ticketu.

## 38. Primary sources

Atlassian developer dokumentácia z júla 2026 opisuje Jira Service Management APIs, webhooks, automation actions a prechod nových extensibility features na Forge. Microsoft Learn dokumentácia Power Automate approvals z apríla 2026 a current known-issues stránky opisujú approval typy, e-mail/Teams/action-center channels, identity requirements, channel mismatch a execution wait boundaries.

Tieto capabilities sú transport a process primitives. Správny recipient, factual message a vyriešený business case musí dokázať konkrétny workflow.

## Zhrnutie

Ticket, e-mail a chat automation potrebuje exact identities, channel-aware contracts, drafts oddelené od send authority, durable outbox, approvals, idempotency a business verification. Komunikačný success nesmie zatvoriť proces, ktorý ešte nie je vyriešený.

Ďalšia kapitola určuje hranice, v ktorých môže agent vykonať remediation bez neprimeraného rizika.
