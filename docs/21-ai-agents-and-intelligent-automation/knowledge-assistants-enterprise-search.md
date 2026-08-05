# Knowledge assistants a enterprise search

Knowledge assistant nie je len chat nad dokumentmi. Je to retrieval a answer system, ktorý musí zachovať autoritu zdroja, identitu používateľa, permissions, freshness, supersession a schopnosť vysvetliť, z čoho odpoveď vznikla. Bez týchto vlastností sa enterprise search môže stať rýchlym kanálom na únik dát alebo na šírenie zastaraného rozhodnutia.

## 1. Business outcome

Cieľom je skrátiť čas potrebný na nájdenie platného postupu, rozhodnutia alebo dôkazu bez obídenia source ACL a bez zmeny neistej odpovede na organizačnú pravdu. Úspech sa meria task completion, citation correctness, permission correctness a freshness, nie počtom odpovedí.

Abstention pri chýbajúcom oprávnení alebo dôkaze je legitímny výsledok.

## 2. Exact knowledge subject

Governed subject zahŕňa source system, tenant, repository alebo site, document ID, source revision, effective date, owner, classification, ACL generation, ingestion run, parser generation, chunk ID, embedding model a index generation.

Filename a title nie sú dostatočné. Rovnaký dokument môže existovať v draft, approved a archived verzii.

## 3. Source authority

Index nie je source of truth. Source authority ostáva napríklad schválený policy repository, records system, service catalog, ticket, SharePoint library alebo Git commit.

Index je derived serving layer. Odpoveď musí vedieť vrátiť source reference a jeho revision.

## 4. Ingestion lifecycle

Lifecycle je connect, enumerate, authorize, fetch, parse, normalize, classify, chunk, embed, index, verify a publish. Každá fáza môže byť partial.

„Indexer succeeded“ neznamená, že všetky dokumenty, permissions a deletes boli spracované.

## 5. Connector identity

Connector používa samostatnú identity s minimálnym read scope. Broad crawler account môže indexovať dáta, ktoré žiadny bežný používateľ nemá vidieť, a neskoršie application filtering nemusí chybu napraviť.

Audit spája source principal, connector configuration a ingestion run.

## 6. Permission-aware retrieval

Authorization sa má vyhodnotiť pri query time nad identity používateľa a synchronizovanými document permissions. Post-filter po generovaní answer je príliš neskoro, pretože zakázaný obsah už mohol ovplyvniť model.

Result trimming musí prebehnúť pred prompt construction.

## 7. Azure AI Search boundaries

Aktuálna Azure AI Search dokumentácia opisuje document-level access control cez security filters a preview native ACL, RBAC, Purview a SharePoint permission patterns v API `2026-05-01-preview`. Zároveň upozorňuje na lag pri synchronizácii permission changes a na explicitný refresh pri niektorých inherited SharePoint permissions.

Preview capability sa preto nesmie považovať za automatický production guarantee. Implementácia musí testovať source-specific permission propagation.

## 8. Google Agent Search boundaries

Aktuálna Google Cloud Agent Search dokumentácia rozlišuje apps, data stores, connectors, blended search, serving controls a identity-provider prerequisites pre source access control. Data-store attachment, region, Enterprise features a connector limitations sú súčasťou effective generation.

Search relevance control nie je authorization control.

## 9. Security filters

Pri custom security filters aplikácia odvodí allowed groups alebo scopes a vloží ich do query. Chyba v group expansion, case normalization alebo tenant scope môže viesť k overexposure alebo false deny.

Filter expression, identity claims a policy generation sa zapisujú do audit evidence bez zbytočného ukladania citlivých tokenov.

## 10. ACL freshness

Source permission change sa prejaví až po connector alebo index refreshi podľa konkrétneho modelu. Revoked user môže počas lag window stále dostať starý result, ak systém nemá query-time source authorization alebo emergency deny layer.

Permission freshness má vlastné SLO a alerting.

## 11. Delete a right to be forgotten

Delete event musí odstrániť source document, chunks, embeddings, caches, generated summaries a derived feedback references podľa retention policy. Tombstone bez index purge nie je dokončené vymazanie.

Deletion proof používa source ID a index generation, nie len query, ktorá náhodne nič nevrátila.

## 12. Parsing

PDF, HTML, Office dokument alebo ticket export môže byť zle rozdelený, stratiť tabuľku, hlavičku alebo footnote. Parser version a extraction warnings musia byť dostupné retrieval vrstve.

Model nesmie dopĺňať chýbajúce bunky ako fakt.

## 13. Chunking

Chunk musí niesť document identity, section path, page alebo anchor, effective dates, permissions a supersession metadata. Príliš malý chunk stratí normatívny kontext; príliš veľký znižuje retrieval precision a zvyšuje leakage surface.

Chunking generation sa pinne pri evaluation.

## 14. Embeddings a index generation

Ingestion a query musia používať kompatibilnú embedding generation. Blue-green reindex umožní porovnať recall a permission behavior pred cutoverom.

Mixed generations bez explicitného routing vytvoria neinterpretovateľné výsledky.

## 15. Search oproti answer

Search result je ranked set dokumentov. Answer je modelová syntéza nad vybraným contextom. Odpoveď môže byť nesprávna aj pri správnom search results a search môže byť nesprávny aj pri dobre formulovanej odpovedi.

Evaluation musí merať oba stupne oddelene.

## 16. Hybrid retrieval

Lexical search zachytáva exact identifiers a rare terms; vector search zachytáva semantickú podobnosť. Hybrid a reranking môžu zlepšiť relevance, ale nesmú meniť permission filters.

Reranker dostane len už autorizované candidates.

## 17. Query normalization

Spelling correction, synonym expansion a query rewrite môžu neúmyselne rozšíriť subject. Pri security alebo legal queries sa zachová original query a rewrite diff.

Exact IDs, quoted terms a negative constraints sa nesmú potichu odstrániť.

## 18. Effective dates

Policy answer musí preferovať dokument účinný pre daný environment a čas. Latest modified timestamp nemusí znamenať aktuálne platnú verziu; novší súbor môže byť draft.

Metadata obsahuje valid-from, valid-to, approval state a supersedes relation.

## 19. Citation contract

Každé normatívne tvrdenie má citation na source revision a relevantný section anchor. Citation musí podporovať konkrétne tvrdenie, nie len tematicky súvisieť.

Unavailable source alebo permission change po answer generation zmení answer state na unverifiable.

## 20. Groundedness a abstention

Assistant rozlišuje supported, inferred, conflicting a unknown claims. Pri konflikte zdrojov ukáže authority hierarchy a nevyberie si pohodlnejší text bez pravidla.

Ak dôkaz nestačí, vráti potrebný ďalší source alebo ownera.

## 21. Prompt injection v dokumentoch

Dokument môže obsahovať text „ignore previous instructions“ alebo tool-like payload. Ingested text ostáva untrusted content.

Retriever ani model nesmú podľa dokumentu meniť tool permissions, recipienta, system prompt alebo data-export behavior.

## 22. Poisoning

Útočník môže vložiť SEO-like keywords, duplicated policy alebo falošný runbook do zdroja, ku ktorému má write access. Ingestion musí zachytiť source owner, approval state a anomaly signály.

Popularita alebo embedding similarity nie je authority.

## 23. Sensitive output

Odpoveď môže kombinovať viac individuálne povolených fragments do citlivého agregátu. Output policy preto posudzuje classification, aggregation a channel, nie len document ACL.

Export, copy alebo send tools majú samostatnú authorization.

## 24. Caches

Query cache a answer cache musia byť tenant-, identity-, ACL-generation- a index-generation-aware. Shared cache key založený len na query môže leaknúť odpoveď medzi používateľmi.

Po revoke alebo delete sa invalidujú relevantné entries.

## 25. Feedback

Thumbs-up nie je source correction. Feedback sa viaže na query, answer, citations, user role a index generation a slúži na evaluation alebo proposal.

Zmenu policy source musí schváliť jeho owner v source systéme.

## 26. Knowledge assistant memory

Conversation memory môže uchovať user intent a unresolved references, ale nesmie obísť aktuálny retrieval a permissions. Starý answer vložený do memory sa znovu overí pred použitím.

Memory summary bez citations nie je knowledge record.

## 27. Enterprise search observability

Merajú sa ingestion lag, permission lag, delete lag, parser errors, zero-result rate, citation coverage, unauthorized-result tests, stale-answer rate, abstention quality a source conflicts. Relevance metrics bez permission metrics sú neúplné.

Canary principals overujú allow aj deny cases.

## 28. Evaluation set

Evaluation obsahuje exact lookup, ambiguous query, stale policy, revoked user, inherited ACL change, cross-tenant collision, malicious document, conflicting sources, deleted document a no-answer scenario. Očakávanie definuje autorizované results aj správnu odpoveď.

Test corpus nesmie obsahovať iba verejné dokumenty.

## 29. Incident AGENT-OPS-15

Knowledge assistant vyhľadá runbook pre „suspicious shared service identity“. Index obsahuje staršiu approved verziu a novú emergency exception, ale permission metadata novej verzie ešte nie je zosynchronizovaná.

Assistant vráti starý runbook „disable immediately“ bez upozornenia na ingestion lag.

## 30. Cross-system ambiguity

Security incident používa alias, ktorý sa zhoduje s osobným účtom aj production service principalom. Search query rewrite odstráni environment qualifier a reranker zvýhodní populárnejší starý dokument.

Citation odkazuje na validný source, ale nie na správnu effective generation.

## 31. Containment

Zastaví sa answer cache a downstream send/remediation tools. Index sa označí ako degraded pre daný connector a query vráti source conflict plus abstention.

Reviewer dostane oba dokumenty, ACL state a ingestion timestamps.

## 32. Recovery

Permission sync sa opraví, vykoná sa targeted reindex a canary deny/allow tests. Supersession metadata jednoznačne označí current runbook a caches sa invalidujú.

Security workflow musí re-runúť retrieval nad novou index generation, nie reuse starý answer.

## 33. Positive acceptance

Authorized user dostane current approved document, exact citation a effective-date vysvetlenie. Revoked user nedostane ani fragment, answer cache hit, snippet alebo derived summary.

Conflict vedie k abstention a owner escalation.

## 34. Forbidden acceptance

Top-1 relevance, citation presence, successful indexer run alebo document title nesmú byť acceptance. Assistant nesmie post-filterovať už vygenerovaný answer, používať crawler identity ako caller identity ani uchovať zakázaný text v memory.

## 35. Recovery acceptance

Po ACL revoke je dokument nedostupný v search, answer, cache aj conversation continuation podľa definovaného SLO. Po restore sa vráti len správne autorizovaným principalom.

Druhý test zmení inherited folder permission a musí preukázať explicitný refresh alebo emergency deny.

## 36. Practical permission-aware contract

Serving contract musí viazať query na caller identity aj index generation. Retriever nemôže vrátiť neautorizovaný candidate s tým, že answer layer ho neskôr odstráni.

```yaml
knowledge_query:
  caller:
    tenant: tenant-a
    principal_id: user-1842
    groups_generation: entra-2026-08-05T15:00Z
  corpus:
    source: policy-sharepoint
    index_generation: policies-blue-042
    permission_generation: acl-sync-884
  retrieval:
    lexical: true
    vector: true
    top_k: 8
    authorization_phase: before-rerank
  answer:
    require_citations: true
    conflict_behavior: abstain
    stale_source_behavior: disclose-and-escalate
  cache_key_fields:
    - tenant
    - principal_id
    - permission_generation
    - index_generation
    - normalized_query_digest
```

Test najprv povolí dokument členovi skupiny, potom zmení inherited ACL, ponechá starú cache entry a spustí rovnaký query. Correct result je deny alebo explicitný degraded-state hold podľa definovaného permission-freshness SLO, nikdy stará odpoveď z cache.

## 37. Troubleshooting decomposition

Pri chýbajúcom výsledku sa oddelí source absence, connector failure, parser failure, permission deny, index lag, query rewrite a ranking miss. Pri neočakávanom výsledku sa overí caller token, group expansion, ACL metadata, candidate set pred rerankom a cache key.

Tým sa zabráni „oprave relevance“ zvýšením top-k, ktorá v skutočnosti rozšíri leakage surface alebo skryje permission bug.

## 38. Primary sources

Microsoft Learn dokumentácia Azure AI Search z júla 2026 opisuje document-level access control, security filters, preview token-based ACL/RBAC/Purview patterns a permission synchronization boundaries. Google Cloud Agent Search dokumentácia z júla 2026 opisuje apps, data stores, connectors, serving controls a identity-provider requirements.

Tieto vendor capabilities sa dopĺňajú všeobecným RAG modelom z predchádzajúcich kapitol. Production authority vzniká až vlastným permission, freshness, deletion a evaluation evidence.

## Zhrnutie

Enterprise knowledge assistant je permission-aware retrieval system s modelovou answer vrstvou. Source authority, ACL generation, ingestion freshness, citations, abstention, delete propagation a adversarial evaluation musia zostať explicitné.

Ďalšia kapitola rieši ticket, e-mail a chat automation, ktorá odpovede posúva do komunikačných a procesných systémov.
