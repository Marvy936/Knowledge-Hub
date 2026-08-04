# Short-term state, long-term memory a external memory

Agentická aplikácia potrebuje pracovať s informáciami naprieč krokmi a opakovanými spusteniami, ale slovo *memory* často zakrýva tri odlišné mechanizmy. Short-term state drží pracovný stav jedného threadu alebo runu, long-term memory uchováva vybrané fakty, skúsenosti alebo pravidlá naprieč threadmi a external memory sprístupňuje autoritatívne dáta z externých systémov. Tieto vrstvy nemajú rovnakú authority, lifetime ani bezpečnostný význam. História konverzácie nie je automaticky pravda, sumarizovaný workaround nie je produkčný runbook a záznam v agentovej databáze nesmie prebiť aktuálny stav Kubernetes, databázy, IAM alebo ticket systému.

V incidente `AGENT-OPS-02` incident supervisor načítal z long-term memory vetu „pri checkout timeoutoch reštartuj checkout deployment“. Záznam vznikol zo starého incidentu, neobsahoval expiry ani väzbu na konkrétnu architektúru a po migrácii payment flow už neplatil. Short-term state navyše obsahoval pätnásť minút starý počet chýb a external CMDB snapshot nesprávne označoval canary deployment ako bezpečný na reštart. Agent spojil tri rozdielne vrstvy do jedného údajne spoľahlivého kontextu a vykonal akciu bez nového authoritative read-backu. Root cause nebola „zlá pamäť modelu“, ale chýbajúce scope, provenance, freshness, conflict resolution a authority pravidlá.

## 1. Memory nie je context window

Context window je množina tokenov, ktoré model vidí pri konkrétnom inference kroku. Memory je mechanizmus, ktorý rozhoduje, čo sa má uchovať, kde sa to má uložiť, komu sa to môže neskôr načítať a ako sa záznam invaliduje alebo odstráni. Informácia môže byť uložená v databáze a pritom nemusí byť vložená do aktuálneho contextu; opačne môže byť v contexte iba dočasne bez akejkoľvek persistencie.

Preto treba oddeliť štyri operácie:

```text
observe information
→ decide whether it may be stored
→ persist it under an exact scope and policy
→ retrieve and curate it for one model turn
```

Model nemá automaticky rozhodovať o všetkých štyroch operáciách. Deterministické pravidlá majú kontrolovať citlivé dáta, tenancy, retention, deletion, authority a maximálny context budget.

## 2. Short-term state

Short-term state je pracovný stav jedného threadu, incidentu, ticketu alebo agent runu. Typicky obsahuje user messages, tool proposals, tool outcomes, aktuálny plán, pending approval, budget counters a odkazy na získané evidence. Jeho primárnym účelom nie je „pamätať používateľa navždy“, ale umožniť pokračovať v tej istej operácii po ďalšom kroku, prerušení alebo process restarte.

Short-term state musí mať exact identity. Minimálny subject zahŕňa:

```yaml
thread_id: incident-2026-08-04-017
run_id: run-7b3a
business_operation_id: checkout-recovery-017
tenant_id: retail-eu
state_schema: agent-state/v4
checkpoint_generation: 38
created_at: 2026-08-04T14:12:03Z
updated_at: 2026-08-04T14:18:44Z
```

Bez `thread_id`, `run_id` a schema generation nie je možné bezpečne určiť, či resume pokračuje v správnej operácii a či uložený state ešte možno interpretovať rovnakým kódom.

## 3. Conversation history je iba časť state

Message history zachytáva dialóg, ale agent run obsahuje aj ne-konverzačný stav. Tool call môže byť navrhnutý, autorizovaný, čakajúci na approval, odoslaný, dokončený, neúspešný alebo mať unknown outcome. Tieto stavy sa nemajú rekonštruovať iba z prirodzeného jazyka v chate.

Typed state môže vyzerať takto:

```python
from typing import Literal, TypedDict


class PendingAction(TypedDict):
    action_id: str
    tool_contract: str
    arguments_digest: str
    status: Literal[
        "proposed",
        "awaiting_approval",
        "approved",
        "executing",
        "succeeded",
        "failed",
        "unknown_outcome",
    ]


class AgentState(TypedDict):
    operation_id: str
    messages: list[dict]
    evidence_refs: list[str]
    plan_version: int
    pending_actions: list[PendingAction]
    remaining_turns: int
    remaining_cost_eur: float
```

Takýto state umožňuje deterministicky zablokovať pokračovanie po unknown outcome namiesto toho, aby model podľa poslednej vety odhadol, či má akciu zopakovať.

## 4. Checkpoint nie je business commit

Checkpoint preukazuje, že orchestrator uložil svoj interný state. Nepreukazuje, že downstream side effect bol vykonaný alebo že business outcome nastal. Po úspešnom checkpoint write môže byť payment refund stále necommitnutý; po zlyhanom checkpoint write mohol downstream systém akciu dokončiť.

Recovery preto porovnáva dve línie:

```text
orchestrator checkpoint lineage
versus
external business-operation lineage
```

Pri rozdiele sa stav označí `unknown_outcome` a vykoná sa authoritative read-back podľa operation ID alebo idempotency key.

## 5. Long-term memory

Long-term memory uchováva informácie naprieč threadmi a sessions. Môže ísť o používateľskú preferenciu, stabilný organizačný fakt, overenú skúsenosť z incidentu alebo schválené procedural rule. Každý typ má inú authority a lifecycle.

Praktické rozdelenie je:

- **Semantic memory** — fakty, napríklad preferovaný jazyk používateľa alebo vlastníctvo služby. Fakt musí mať source, confidence, scope a freshness.
- **Episodic memory** — skúsenosť z predchádzajúceho runu, napríklad že konkrétny diagnostický dotaz pomohol nájsť príčinu. Epizóda nie je všeobecné pravidlo.
- **Procedural memory** — schválený spôsob práce, napríklad runbook alebo policy. Jej authority musí pochádzať z versioned zdroja, nie iba z modelovej sumarizácie.

Tieto kategórie sa nemajú ukladať do jedného anonymného textového poľa. Procedural rule môže ovplyvniť tool selection a side effects, preto vyžaduje prísnejší review a invalidation než neškodná preferencia formátu odpovede.

## 6. Exact long-term memory subject

Každý memory record potrebuje identitu a authority metadata. Príklad:

```yaml
memory_id: mem-ops-00491
memory_type: episodic
namespace:
  tenant: retail-eu
  service: checkout
  environment: production
subject:
  incident_id: INC-1042
  architecture_generation: checkout-v17
statement: >-
  During INC-1042, stale DNS cache on gateway nodes caused intermittent
  payment-provider timeouts. Restart was not required.
source_refs:
  - postmortem://INC-1042/v3
  - metrics://gateway-dns-cache/2026-05-11
confidence: reviewed
created_by: postmortem-ingestion/v2
reviewed_by: sre-checkout
created_at: 2026-05-14T09:00:00Z
valid_until: 2026-11-14T09:00:00Z
retention_policy: ops-memory-180d
supersedes: null
```

Záznam nehovorí iba *čo* si systém pamätá. Hovorí aj *pre koho*, *pre akú generáciu systému*, *z akého dôkazu*, *dokedy* a *s akou review authority*.

## 7. Namespace a tenant isolation

Long-term memory sa načítava podľa explicitného namespace. Namespace môže obsahovať tenant, user, organization, service, environment, region a memory class. Globálny search cez všetky memories je bezpečný iba pre verejné, ne-citlivé a skutočne globálne záznamy.

Chybný návrh:

```text
search_memory("checkout timeout")
```

Bezpečnejší návrh:

```text
search_memory(
  tenant="retail-eu",
  service="checkout",
  environment="production",
  architecture_generation="checkout-v21",
  allowed_types=["episodic", "procedural"],
  valid_at=now
)
```

Tenant ID sa nesmie odvodiť z textu promptu. Musí prísť z autentifikovaného execution contextu a enforcement má prebehnúť v storage vrstve.

## 8. External memory

External memory je pracovný názov pre autoritatívne alebo operatívne informácie mimo agentovej vlastnej persistence. Patria sem databázy, CMDB, Git, Kubernetes API, IAM directory, ticket systém, object store, knowledge base alebo event log.

External systém môže byť source of truth pre konkrétny subject. Napríklad:

```text
Git release manifest → desired release generation
Kubernetes API → currently loaded workload objects
payment ledger → committed refund outcome
IAM directory → current user and service entitlements
postmortem repository → reviewed incident learning
```

Agentová memory môže obsahovať odkazy a indexy, ale nemá kopírovať authority bez synchronizačného a freshness modelu.

## 9. Cache, index a memory nie sú synonymá

Cache zrýchľuje opakované získanie rovnakého výsledku a má explicitnú invalidáciu. Retrieval index umožňuje vyhľadávať dokumenty alebo chunks. Memory vyjadruje rozhodnutie, že informácia má ovplyvniť budúce runs. Jeden fyzický store môže podporovať viac funkcií, ale logické kontrakty musia zostať oddelené.

Embedding index postmortemov napríklad nie je procedural memory. Nájde podobný incident, no agent stále musí overiť architecture generation, source status a aktuálny stav systému.

## 10. Authority hierarchy

Keď sa informácie rozchádzajú, systém potrebuje explicitnú hierarchy. Typický model:

```text
current authoritative external read-back
> current approved policy or runbook
> reviewed long-term memory with matching scope
> unreviewed episodic memory
> short-term model summary
> model prior or guess
```

Táto hierarchy nie je univerzálna. Musí byť definovaná pre každý domain subject. Pri osobnej preferencii môže byť najvyššou authority aktuálne vyjadrenie používateľa; pri refund outcome je najvyššou authority ledger.

## 11. Provenance a evidence

Memory record bez provenance je tvrdenie bez možnosti auditu. Minimálne evidence metadata zahŕňajú source identifier, source generation, acquisition time, author alebo producer, review status a transformation chain.

Pri sumarizácii sa uchováva lineage:

```text
raw incident artifacts
→ filtered evidence set
→ reviewed postmortem
→ memory candidate
→ approved memory record
```

Memory record nemá tvrdiť viac než jeho source. Ak postmortem hovorí „restart nepomohol pri INC-1042“, memory nesmie generalizovať na „checkout sa nikdy nereštartuje“.

## 12. Freshness, TTL a invalidation

Každá memory class potrebuje freshness policy. Krátkodobý observation môže expirovať po sekundách, entitlement snapshot po minútach a schválený runbook až po novej verzii. TTL však nie je jediný invalidation trigger.

Záznam sa invaliduje aj pri:

- zmene architecture generation;
- zmene ownera alebo policy;
- odvolaní súhlasu používateľa;
- oprave pôvodného incidentu;
- zmene identity alebo tenancy scope;
- explicitnom supersede novším záznamom;
- zistení poisoning alebo nesprávnej generalizácie.

Retrieval musí filtrovať neplatné záznamy predtým, než sa dostanú do model contextu.

## 13. Write path

Long-term memory write je samostatná privilegovaná operácia. Model môže navrhnúť candidate, ale deterministic policy rozhoduje, či sa smie uložiť automaticky, či potrebuje review alebo sa nesmie uložiť vôbec.

```python
def propose_memory(observation: Observation) -> MemoryCandidate:
    return extract_candidate(observation)


def persist_memory(candidate: MemoryCandidate, context: AuthContext) -> str:
    validate_schema(candidate)
    enforce_tenant_scope(candidate.namespace, context)
    classify_sensitivity(candidate)
    require_source_refs(candidate)
    require_review_if_procedural(candidate)
    apply_retention_policy(candidate)
    return memory_store.insert(candidate)
```

Modelom generovaný candidate sa nesmie zapisovať rovno do globálneho namespace.

## 14. Read path a context curation

Memory retrieval nie je iba semantic search. Read path používa scope filters, authority, validity, sensitivity, task relevance a context budget. Až potom sa vybrané záznamy transformujú do prompt-safe representation.

```python
def build_memory_context(subject: Subject, auth: AuthContext, budget: int) -> list[Memory]:
    candidates = memory_store.search(
        namespace=authorized_namespace(auth),
        subject=subject,
        valid_at=now(),
    )
    candidates = [m for m in candidates if authority_allowed(m, subject)]
    candidates = deduplicate_and_resolve_conflicts(candidates)
    return select_within_token_budget(candidates, budget)
```

Model má dostať aj provenance a freshness, nie iba izolovaný statement.

## 15. Hot-path a offline memory updates

Hot-path update vzniká počas aktívneho runu. Je vhodný pre nízkorizikové preferences alebo presne validované state transitions, ale zvyšuje latency a riziko, že agent uloží unreviewed interpretáciu.

Offline update spracúva ukončené runs, feedback alebo postmortems samostatnou pipeline. Umožňuje deduplikáciu, redakciu, review a lepšie evals. Nevýhodou je oneskorenie medzi skúsenosťou a dostupnosťou memory.

Produkčný systém často kombinuje oba prístupy: bezpečné thread state sa ukladá okamžite, zatiaľ čo cross-session procedural learning vzniká až po offline review.

## 16. Compaction a summarization

Dlhý short-term state môže prekročiť context window. Trimming, summarization alebo compaction znižujú tokeny, ale sú lossy transformácie. Pôvodné authoritative tool outcomes, action IDs, approvals a evidence references sa nesmú stratiť v prirodzenom jazykovom sumári.

Bezpečný compaction artifact obsahuje:

```yaml
summary_generation: 12
covers_events: [evt-001, evt-087]
summary_text: "..."
preserved_invariants:
  - business_operation_id
  - pending_action_ids
  - approval_digests
  - unresolved_hypotheses
raw_event_archive: object://agent-runs/run-7b3a/events-v1
```

Summary zrýchľuje reasoning, ale raw event archive zostáva evidence authority.

## 17. Memory conflicts

Dva memory records môžu tvrdiť rozdielne veci. Conflict resolution sa nesmie prenechať iba modelovej preferencii textu. Deterministická vrstva porovná scope, authority, generation, timestamp, review status a supersession relation.

Možné výsledky sú:

```text
select one authoritative record
merge compatible records
mark conflict and require external read-back
quarantine both records
```

Pri high-impact rozhodnutí je bezpečná default voľba external read-back alebo human escalation.

## 18. Memory poisoning

Memory poisoning nastáva, keď nedôveryhodný obsah ovplyvní budúce runs. Zdrojom môže byť používateľský prompt, kompromitovaný dokument, tool output alebo chybný model-generated summary. Poisoned memory môže prežiť dlhšie než pôvodný útok a zasiahnuť iných používateľov alebo tenantov.

Ochrany zahŕňajú oddelenie observation od approved memory, provenance, sensitivity classification, namespace enforcement, review pre procedural records, write-rate limits, anomaly detection a možnosť rýchleho quarantine podľa producer generation.

## 19. Privacy, consent a purpose limitation

Nie všetko užitočné sa smie pamätať. Memory policy musí určiť účel spracovania, povolené kategórie dát, retention, region, export, correction a deletion path. Používateľská veta v jednom support tickete nie je automatický súhlas s globálnym profilovaním.

Pri deletion requeste sa rieši celý derivation graph:

```text
raw conversation
→ session history
→ summary
→ embedding/index entry
→ long-term memory record
→ eval or analytics copy
→ backup retention
```

Vymazanie iba primary row neposkytuje úplný deletion evidence.

## 20. Security a encryption

Memory stores obsahujú koncentrovaný kontext a sú atraktívnym cieľom. Potrebujú encryption in transit a at rest, workload identity, least privilege, row alebo namespace-level access control, audit logging a secret redaction. Citlivé raw prompts a tool outputs sa nemajú ukladať iba preto, že uľahčujú debugging.

Encrypted storage nerieši nesprávne authorization. Agent s príliš širokým read scope môže dešifrovať cudzie memories legitímnou aplikáciou.

## 21. Memory a identity lifecycle

User ID, account ID, employee ID a tenant ID sa môžu meniť alebo zlučovať. Memory namespace potrebuje stabilnú canonical identity a explicitné pravidlá pre merge, split, account deletion a role change. Email adresa nie je vhodný permanentný primary key.

Pri zmene oprávnení sa cross-session memory nepreberá automaticky. Bývalý incident commander napríklad nesmie po zmene roly naďalej čítať restricted incident memories.

## 22. Memory a multi-agent systémy

Pri viacerých agentoch treba určiť, kto vlastní short-term state a kto smie zapisovať long-term memory. Shared global scratchpad zvyšuje coupling a umožňuje, aby jeden specialist zapísal neoverenú hypotézu ako fakt pre všetkých ostatných.

Bezpečnejší model používa:

```text
supervisor-owned operation state
+ specialist-local ephemeral state
+ typed evidence exchange
+ centrally governed long-term memory writes
```

Specialist output sa stane observation pre supervisora, nie automaticky globálnou memory.

## 23. Incident `AGENT-OPS-02`

Supervisor načítal procedural-looking memory bez review statusu a architecture scope. Router poslal rovnaký incident Kubernetes aj database specialistovi, pričom obaja čítali shared scratchpad. Kubernetes specialist zapísal hypotézu „checkout pods sú deadlocked“ a database specialist ju pri ďalšom kroku považoval za potvrdený fakt.

Správny postup bol:

```text
exact incident and service generation
→ thread-scoped state with typed hypotheses
→ reviewed long-term memories filtered by architecture generation
→ current Kubernetes, database and business-metric read-back
→ conflict resolution and evidence labels
→ action proposal only after current authority wins
```

Starý memory record sa po incidente quarantinoval a postmortem pipeline vytvorila nový episodic record s explicitným dôkazom, že restart zmazal diagnostické signály a neobnovil konverziu.

## 24. Failure hypotheses

Keď agent použije nesprávnu informáciu, „model si zle zapamätal“ je iba jedna hypotéza. Failure môže vzniknúť pri scope resolution, retrieval, compaction, stale cache, identity mapping, source transformation alebo authority selection. Diagnostika preto zachováva viacero alternatív, kým evidence neurčí first divergence.

- **Wrong namespace** — retrieval použil nesprávny tenant, user, service alebo environment scope.
- **Stale memory** — záznam expiroval alebo mal byť invalidovaný novou architecture generation.
- **Authority inversion** — unreviewed summary prebil aktuálny external read-back.
- **Compaction loss** — summary odstránil pending action, approval digest alebo unresolved hypothesis.
- **Poisoned write** — nedôveryhodný observation sa uložil ako procedural fact.
- **Identity drift** — záznam sa priradil k nesprávnej canonical identity.
- **Index lag** — store obsahoval opravu, ale retrieval index ešte vracal starý record.
- **Deletion gap** — primary record bol odstránený, no derived summary alebo index entry zostal dostupný.

Každá hypotéza potrebuje potvrdzujúci a vyraďujúci dôkaz. Pri high-impact akcii sa memory nepoužije ako jediná authority.

## 25. Evidence envelope

Troubleshooting záznam pre memory decision môže mať tento tvar:

```yaml
memory_decision_id: md-8831
operation_id: checkout-recovery-017
query_subject:
  tenant: retail-eu
  service: checkout
  environment: production
retrieved_records:
  - memory_id: mem-ops-00491
    generation: 3
    authority: reviewed-episodic
    valid: true
    source_digest: sha256:...
external_readbacks:
  - subject: kubernetes/deployment/checkout
    resource_version: "8839201"
    observed_at: 2026-08-04T14:17:33Z
conflicts:
  - memory_id: mem-ops-00122
    reason: architecture_generation_mismatch
selected_context_digest: sha256:...
```

Envelope umožňuje spätne vysvetliť, prečo sa konkrétna memory dostala do kontextu a ktorá external authority ju potvrdila alebo vyvrátila.

## 26. Containment

Pri podozrení na poisoned alebo stale memory sa write path vypne skôr než read path bez rozmyslu. Následne sa môže obmedziť konkrétny producer generation, namespace, memory type alebo affected tenant. High-impact agents prejdú do read-only režimu a pred každou akciou vyžadujú external read-back.

Globálne vymazanie všetkých memories je posledná možnosť, pretože ničí evidence a môže zhoršiť dostupnosť. Quarantine zachová record na forenznú analýzu, ale odstráni ho z retrievalu.

## 27. Recovery

Recovery zahŕňa opravu scope alebo policy, reindex, invalidáciu caches, obnovu správnej identity mapping, regenerovanie summaries z raw event archive a backfill review metadata. Pri privacy incidente sa vykoná deletion graph a credential rotation podľa blast radiusu.

Po oprave sa replay-ne incident input s rovnakým memory snapshotom a potom s corrected generation. Benign control overí, že užitočné memories zostali dostupné a že oprava nezmenila systém na úplne bezkontextový.

## 28. Positive acceptance

Pozitívny test musí preukázať, že thread resume načíta správny checkpoint, long-term retrieval rešpektuje namespace a validity, external read-back prebieha pred high-impact rozhodnutím a selected context obsahuje provenance. Výsledná akcia musí dosiahnuť business postcondition, nie iba úspešný model output.

## 29. Forbidden acceptance

Zakázaný test musí potvrdiť, že agent nečíta cudzie tenant memories, nepoužíva expirovaný procedural record, neukladá secret alebo citlivý údaj bez policy a neprebije aktuálny external authority modelovým summary. Pokus musí byť blokovaný a auditovaný bez úniku zakázaného obsahu do trace.

## 30. Recovery acceptance

Recovery test vytvorí stale alebo poisoned memory, overí quarantine, opraví generation a preukáže, že affected runs používajú nový record. Zároveň kontroluje, že raw evidence zostáva dostupná oprávnenému incident tímu a deletion alebo retention povinnosti sú splnené.

## 31. Second-operation acceptance

Po úspešnom prvom run-e sa spustí druhá nezávislá operácia s rovnakým tenantom a potom operácia iného tenanta. Prvá musí dostať iba relevantnú validnú memory; druhá nesmie zdediť state, hypotheses, approvals ani personal data z predchádzajúcej operácie.

## 32. Alternate-scenario acceptance

Alternate scenario zmení architecture generation, user preference, entitlement alebo external business state. Systém musí invalidovať alebo znížiť authority starého recordu a získať nový read-back. Stabilita pri jednom statickom scenári nepreukazuje správny memory lifecycle.

## 33. Prevádzkový checklist

Pred nasadením memory vrstvy musí tím vedieť odpovedať, čo je thread state, čo je cross-session memory a ktorý external systém je authority pre každý business subject. Musí existovať versioned schema, namespace enforcement, provenance, TTL a invalidation, privacy/deletion path, quarantine, audit a test obnovy po corrupt checkpoint alebo stale indexe.

Checklist nie je acceptance verdict. Produkčný verdict vyžaduje reálne resume, tenant-isolation test, memory poisoning test, deletion exercise, external read-back a business outcome evidence.

## 34. Primárne zdroje a proof boundary

OpenAI Agents SDK Sessions dokumentuje session-scoped conversation history, viaceré persistence backends a pokračovanie prerušeného runu s rovnakou session. Je to implementačný príklad short-term history, nie univerzálny dôkaz, že uložená história je autoritatívna business memory.

LangGraph a LangChain dokumentácia rozlišuje thread-scoped short-term memory v graph state od long-term memory v namespaces a uvádza checkpointer ako základ pre resume, human-in-the-loop a fault tolerance. Anthropic pri context engineering zdôrazňuje, že agentický loop priebežne generuje viac možného kontextu, než sa zmestí do jedného model turnu, takže obsah treba cielene kurátorovať.

Repository validácia tejto kapitoly overuje syntax, odkazy, navigation a learning-depth pravidlá. Nevykonáva reálny database checkpoint, cross-tenant isolation, retention, deletion, poisoning, restore ani produkčný agent outcome.