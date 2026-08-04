# Idempotency a side-effect control

Idempotency nie je vlastnosť názvu endpointu ani všeobecné tvrdenie, že „retry je bezpečný“. Je to contract medzi callerom, executorom a authoritative systemom, podľa ktorého viac technických attemptov tej istej **business operation** vytvorí najviac jeden zamýšľaný efekt a vráti konzistentný outcome.

Táto kapitola nadväzuje na `AGENT-OPS-03`. Durable workflow sa po páde obnovil, ale remote failover tool dostal nový operation key. Downstream systém preto nemal možnosť rozlíšiť retry od novej business požiadavky. Idempotency vrstva musí stabilizovať identity, scope, canonical arguments, deduplication record, concurrency control a postcondition read-back skôr, než agent dostane mutation capability.

Nosný lifecycle je:

```text
business intent
→ canonical subject a operation scope
→ stable idempotency key
→ argument digest a semantic validation
→ authorization a approval binding
→ atomic claim alebo existing-result lookup
→ one side-effect owner
→ downstream commit
→ durable result a postcondition
→ retry returns same outcome
→ reconciliation pri unknown outcome
```

## 1. Business invariant

Idempotency invariant musí byť vyjadrený business jazykom. Pre checkout failover znie: „pre operation `checkout-recovery-021` sa môže commitnúť najviac jedna zmena traffic policy na schválenú target generation“.

Tento invariant je presnejší než „POST endpoint je idempotentný“. Zahŕňa subject, operation, povolený výsledok a generation boundary.

## 2. Idempotentný request verzus idempotentný outcome

Request môže byť technicky zopakovaný bez novej databázovej row, ale downstream systém môže stále dostať duplicate message alebo email. Skutočná idempotency sa hodnotí na úrovni zamýšľaného outcome-u a všetkých relevantných descendant side effectov.

Ak refund API deduplikuje payment ledger entry, ale každý retry pošle nový confirmation email a vytvorí nový support ticket, operation nie je end-to-end idempotentná. Dokumentácia preto musí uviesť side-effect graph, nie iba jeden write endpoint.

## 3. Stable idempotency key

Idempotency key reprezentuje jednu business operation alebo jeden presne definovaný side effect. Musí zostať rovnaký pri transport retries, worker retries a process recovery, ale zmeniť sa pri novej business požiadavke.

```text
idem:v1:retail-eu:production:checkout-recovery-021:traffic-failover
```

Key nesmie byť náhodne generovaný v každom attempt-e. Zároveň nemá byť iba user ID alebo resource name, pretože by neprimerane deduplikoval odlišné budúce operácie.

## 4. Scope

Scope určuje, kde musí byť key unikátny. Bežné dimenzie sú tenant, environment, operation type, canonical subject a side-effect kind.

Key bez tenant alebo environment boundary môže spôsobiť cross-tenant collision. Key bez operation type môže omylom zameniť create, cancel a compensate flow.

## 5. Canonical arguments

Deduplication podľa key funguje iba vtedy, keď systém overí, že retry nesie rovnaké execution-relevant arguments. Caller preto vytvorí canonical serialization a digest.

```python
import hashlib
import json


def argument_digest(payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()
```

Ak rovnaký key príde s iným digestom, server nesmie potichu použiť prvý alebo druhý payload. Má vrátiť conflict a vyžadovať novú operation identity alebo nový approval.

## 6. Semantic canonicalization

Syntakticky odlišné payloads môžu mať rovnaký význam. `50`, `50.0` a `"50.00"` nemajú vytvoriť tri refund operations, ak domain používa centy ako integer.

Canonicalization preto patrí do domain vrstvy. Resource aliases sa rozriešia na canonical UID, čas sa normalizuje, defaulty sa explicitne doplnia a unordered collections sa zoradia ešte pred digestom.

## 7. Deduplication record

Authoritative dedup record spája key, digest, status, owner attempt, created time, expiry a výsledok. Nie je to iba cache; je súčasťou correctness a recovery evidence.

```yaml
idempotency_key: idem:v1:retail-eu:production:checkout-recovery-021:traffic-failover
argument_digest: sha256:8e31...
status: committed
owner_attempt: attempt-01
subject_uid: traffic-policy/checkout-prod/uid-9941
result_ref: traffic-change/chg-7712
postcondition_generation: 418
created_at: 2026-08-04T15:33:41Z
expires_at: 2026-09-03T15:33:41Z
```

Result ref musí byť dostupný aj neskorším retries. Inak caller síce nevytvorí duplicate write, ale nevie získať pôvodný outcome a môže nesprávne eskalovať.

## 8. Atomic claim

Race medzi dvoma executormi sa rieši atomic claimom. Oba môžu prísť s rovnakým key v rovnakom čase, ale iba jeden sa stane ownerom execution transitionu.

```sql
INSERT INTO idempotency_ledger (
    idempotency_key, argument_digest, status, owner_attempt
) VALUES (
    :key, :digest, 'in_progress', :attempt
)
ON CONFLICT (idempotency_key) DO NOTHING;
```

Po insert-e executor vždy načíta row a porovná digest a ownership. Samotný `ON CONFLICT DO NOTHING` bez read-backu nehovorí, či request vyhral alebo našiel starý committed result.

## 9. In-progress state

`in_progress` nie je trvalý výsledok. Record potrebuje lease, heartbeat alebo owner-fencing mechanizmus, aby crash prvého executora nezablokoval operation navždy.

Nový executor však nesmie po expiry automaticky opakovať side effect. Najprv zisťuje, či predchádzajúci owner mohol commitnúť downstream operation a iba stratil možnosť zapísať result.

## 10. Fencing token

Fencing token je monotónna generation, ktorú downstream writer porovná pred commitom. Starý worker po strate lease nemôže neskôr dokončiť write, ak už nový owner získal vyššiu generation.

```text
claim generation 41 → executor A
lease expires
claim generation 42 → executor B
executor A attempts late commit with 41 → rejected
```

Bez fencing môže stale worker vykonať side effect po tom, čo orchestration už operation obnovila inde.

## 11. Exactly-once illusion

V distribuovanom systéme nemožno všeobecne garantovať, že request bol fyzicky odoslaný presne raz. Praktická garancia vzniká kombináciou at-least-once delivery, stable identity, deduplication, atomic commit a read-backu.

Preto je presnejšie hovoriť „effectively once pre konkrétny business invariant“. Marketingové „exactly once“ bez definície subjectu, failure modelu a storage boundary je neoveriteľné.

## 12. Side-effect inventory

Agentický tool contract musí uviesť všetky priame a významné nepriame efekty. Príklad traffic failoveru zahŕňa policy write, controller reconciliation, provider routing, audit event, notification a možno billing alebo capacity consequence.

Inventár odhaľuje, kde idempotency končí. Ak tool deduplikuje policy write, ale controller vytvára duplicate downstream jobs bez vlastného operation key, end-to-end invariant stále zlyhá.

## 13. One side-effect owner

Jednu mutation class má vlastniť jeden executor alebo jeden deterministic arbitration point. Viac specialistov môže vytvárať proposals, ale nemá nezávisle commitovať ekvivalentný side effect.

`AGENT-OPS-02` ukázal, že prekrývajúce sa mutation privileges vytvárajú duplicates ešte pred transport retry. Side-effect ownership je preto architecture control, nie iba API detail.

## 14. Read-only príprava

Pred mutation sa všetky možné enrichment, evidence collection a planning kroky vykonajú read-only. Tým sa znižuje počet side-effect boundaries a idempotency surface.

Model môže plán prepočítať viackrát bez produkčnej zmeny. Až exact approved command prejde do jediného executor pathu.

## 15. Outbox pattern

Ak aplikácia mení lokálnu databázu a zároveň publikuje event, outbox uloží domain change a message intent v jednej local transaction. Samostatný publisher potom doručuje event opakovane s stable message ID.

```sql
BEGIN;
UPDATE traffic_changes
SET status = 'committed'
WHERE change_id = :change_id;

INSERT INTO outbox (message_id, topic, payload)
VALUES (:operation_key, 'traffic.changed', :payload);
COMMIT;
```

Consumer stále potrebuje inbox alebo deduplication, pretože outbox typicky garantuje at-least-once delivery, nie fyzicky jednu správu.

## 16. Inbox pattern

Consumer uloží received message ID a effect v jednej transaction. Duplicate delivery potom vráti existing outcome alebo sa bezpečne ignoruje.

Inbox scope musí zahŕňať producer identity a message semantic version. Reuse rovnakého message ID po producer reset-e je contract violation, nie platný retry.

## 17. External API

Pri volaní externého API sa preferuje provider-supported idempotency key alebo client reference. Caller zároveň ukladá provider request ID, resource ID a status lookup path.

Ak provider idempotency nepodporuje, systém potrebuje business reconciliation podľa canonical subjectu a time window. Blind retry sa pri money movement, provisioning alebo destructive operations nepovoľuje.

## 18. Unknown outcome

Unknown outcome vzniká, keď caller nevie, či downstream commitol. State sa explicitne označí `outcome_unknown` a blokuje ďalší mutation attempt, kým reconciliation nerozhodne.

```text
request sent
→ connection lost
→ do not infer failure
→ query by idempotency key or client reference
→ committed: attach existing result
→ not found with authoritative guarantee: retry same key
→ still ambiguous: escalate
```

Absencia v eventually consistent search indexe nemusí dokazovať, že operácia neexistuje. Reconciliation musí používať authoritative endpoint alebo dostatočný consistency model.

## 19. Timeout a retry

Timeout policy oddeľuje safe read, idempotent write a non-idempotent write. Rovnaký HTTP status alebo socket error môže mať odlišný handling podľa operation contractu.

Retry budget sa viaže na operation, nie na každý framework layer zvlášť. SDK, gateway, workflow engine a application nesmú každý nezávisle vykonať päť retries a vytvoriť retry amplification.

## 20. Retry ownership

Jedna vrstva vlastní retry decision pre mutation. Nižšie vrstvy môžu retryovať iba preukázateľne pre-commit transport fázu alebo podľa explicitného contractu.

Ak HTTP client, service mesh a workflow engine všetky retryujú POST, tracing musí aspoň zachytiť attempts. Bez centralized policy nemožno spočítať reálny maximum-attempt bound.

## 21. Agent proposal a executor command

Model output nie je idempotency key. Deterministic adapter vytvorí canonical command, operation key a argument digest po policy a approval vyhodnotení.

```yaml
command_id: cmd-7712
operation_id: checkout-recovery-021
side_effect: traffic-failover
idempotency_key: idem:v1:retail-eu:production:checkout-recovery-021:traffic-failover
argument_digest: sha256:8e31...
approval_digest: sha256:448f...
tool_contract: traffic-admin/failover/v3
```

Ak model pri resume vytvorí mierne inú formuláciu, nesmie tým vzniknúť nový side effect. Command identity sa odvodzuje od business operation a approved semantics, nie od textu.

## 22. Approval binding

Approval sa viaže na canonical arguments a operation key. Retry rovnakého commandu môže použiť pôvodný approval iba počas jeho platnosti a pri nezmenených preconditions.

Nová target generation, amount, recipient alebo resource UID vyžaduje nový proposal a approval. Použiť rovnaký idempotency key s inými arguments je conflict, nie „edit“ existujúcej operácie.

## 23. Tool contract

Tool contract explicitne deklaruje, či operácia je read-only, naturally idempotent, keyed idempotent, conditionally safe alebo non-repeatable. Deklarácia sa testuje failure injectionom.

Tool annotation je iba metadata. Host a executor musia enforcement implementovať sami a považovať server description za untrusted, kým server identity a contract generation nie sú dôveryhodné.

## 24. Natural idempotency

Niektoré operácie nastavujú desired state, napríklad „nastav replicas na 3“. Opakovanie môže byť idempotentné, ak canonical subject a desired generation zostávajú rovnaké.

Aj tu však existujú descendant effects: každý update môže spustiť nový rollout, audit event alebo autoscaler interaction. Natural idempotency sa preto overuje na effective system behavior, nie iba na rovnakom uloženom čísle.

## 25. Conditional write

Optimistic concurrency používa expected version, ETag alebo compare-and-swap. Write prejde iba ak subject zostal v očakávanej generation.

```http
PATCH /traffic-policy/checkout
If-Match: "generation-417"
Idempotency-Key: idem:v1:...:traffic-failover
```

Ak version nesedí, request sa neretryuje s novým ETagom automaticky. Zmena subjectu invaliduje approval a vyžaduje re-read a replan.

## 26. Destructive operation

Delete môže byť idempotentný vo význame „resource neexistuje“, ale business semantics môžu zahŕňať retention, descendant resources alebo irreversible data loss. Repeated delete po recreation môže odstrániť nový resource s rovnakým menom.

Preto sa destructive key viaže na immutable resource UID a expected generation, nie iba na human-readable name. `404` po retry tiež nemusí dokazovať, že prvý delete bol authorized a auditovaný správne.

## 27. Compensation identity

Compensation je nová operation s reference na pôvodný side effect. Nepoužíva rovnaký idempotency key ako forward action.

```text
original: idem:...:traffic-failover
compensation: idem:...:traffic-failover:compensate:01
```

Compensation retry používa vlastný stable key. Inak dedup store môže návrat do pôvodného stavu zameniť za duplicate forward request.

## 28. Retention

Dedup record musí žiť aspoň tak dlho, ako môže prísť legitímny retry alebo delayed message. Krátka TTL vytvorí duplicate po expiry; nekonečná retention môže zvyšovať privacy a storage riziko.

Retention sa odvodzuje od maximum workflow duration, queue redelivery, client offline window, disaster recovery a legal policy. Purge musí zachovať minimálny tombstone alebo archive, ak staré messages môžu stále prísť.

## 29. Multi-region

Multi-region deduplication potrebuje jasný single-writer alebo conflict model. Dva regióny nemajú nezávisle claimnúť rovnaký operation key počas partition.

Možnosti zahŕňajú globally consistent store, home-region routing alebo fencing generation. Eventual merge dvoch už vykonaných money movements duplicate efekt neopraví.

## 30. Multi-tenant isolation

Tenant je súčasť key scope aj authorization checku. Caller nesmie zistiť existing result cudzieho tenanta cez timing alebo conflict response.

Dedup store používa tenant-scoped encryption, access policy, indexes a audit. Global key lookup bez tenant enforcement je data leak a confused-deputy risk.

## 31. Observability

Trace spája business operation, command, key, digest, claim generation, attempt, downstream request ID a postcondition. Metrics sledujú duplicate hits, digest conflicts, stale in-progress records, reconciliation latency a unsafe retry blocks.

Vysoký dedup-hit rate môže signalizovať normálnu redelivery, ale aj retry storm. Bez correlation s causes a layer ownershipom samotné číslo nevysvetľuje incident.

## 32. Incident `AGENT-OPS-03`

Pôvodný executor vytvoril key z `run_id` namiesto `operation_id`. Po worker crashi mal nový run iné ID, takže druhý attempt vytvoril nový key a downstream traffic service prijal druhú mutation.

Navyše gateway retryovala timeout raz a workflow engine následne štyrikrát. Maximum pokusov nebolo päť, ale až desať kombinovaných attempts. Business read-back sa vykonal iba po poslednom success response a nezachytil intermediate traffic oscillation.

Opravený flow je:

```text
stable operation-scoped key
→ canonical digest and approval match
→ atomic claim
→ downstream request with same key
→ timeout means unknown outcome
→ authoritative status lookup
→ return existing result or retry same key
→ verify traffic generation and checkout conversion
```

## 33. Failure hypotheses

Pri duplicate side effecte sa diagnostika nezačína posledným HTTP requestom, ale deriváciou business operation identity. Tím najprv dokáže, že všetky technické attempts mali patriť k jednej operácii, a potom porovná idempotency key, canonical argument digest a tenant/environment scope. Ak sa niektorá z týchto hodnôt zmenila, downstream systém nemal dostatok informácií na deduplikáciu, aj keby jeho implementation fungovala presne podľa contractu.

Druhá vrstva sleduje ownership od atomic claimu cez lease a fencing až po downstream commit. Dve úspešné claims ukazujú storage alebo transaction race; jedna claim s dvoma commitmi ukazuje chýbajúce fencing alebo descendant deduplication. Samostatne sa spočítajú retries v clientovi, proxy, service meshi a workflow engine, pretože lokálne limity sa môžu násobiť do retry amplification.

Posledná vrstva overí effective outcome graph. Primary write môže byť vykonaný iba raz, ale duplicate event, email, job alebo compensation stále porušuje business invariant. Nasledujúce hypotézy preto pomenúvajú presné divergence v identity, ownership, delivery a read-backu:

- **Key regeneration** — framework vytvoril nový key pri každom attempt-e; porovnajú sa operation a request records.
- **Scope collision** — key neobsahoval tenant, environment alebo side-effect kind a zablokoval inú legitímnu operáciu.
- **Digest omission** — server akceptoval rovnaký key s inými arguments a vrátil nesprávny existing result.
- **Non-atomic claim** — check-then-insert race dovolila dvom executorom prejsť naraz.
- **Lease without fencing** — starý owner commitol po prevzatí operation novým workerom.
- **Layered retries** — client, proxy a workflow vytvorili násobný attempt count mimo jedného budgetu.
- **Downstream gap** — primary write bol deduplikovaný, ale event, email alebo job nebol.
- **Expired tombstone** — delayed retry prišiel po purge dedup recordu.
- **Wrong reconciliation source** — eventually consistent index tvrdil `not found`, hoci authoritative ledger už obsahoval commit.
- **False success** — duplicate sa nevytvoril, ale existing result nepatril current canonical subject alebo business postcondition neplatila.

Každá hypotéza sa overuje cez key lineage, digest, claim generation, downstream ledger a effective-state read-back. Modelové vysvetlenie bez týchto artifactov nie je root cause a samotný pokles duplicate countu nepreukazuje opravu descendant side effectov.

## 34. Containment

Pri duplicate incidente sa vypne automatic retry pre affected mutation class a agents prejdú do read-only mode. Pending `in_progress` records sa neodstraňujú hromadne; označia sa na reconciliation a zachovajú evidence.

Gateway retry policy sa dočasne zníži alebo vypne pre mutation routes. Downstream môže zaviesť emergency deny alebo stricter expected-generation check, kým sa opraví key derivation.

## 35. Recovery

Recovery vytvorí operation ledger, identifikuje duplicate descendants a vykoná povolené compensations. Následne opraví key scope, atomic claim, fencing, retry ownership a status lookup.

Historical requests sa replayujú v test environment-e s crashom pred send, po send, po downstream commit a pred result persistence. Acceptance musí ukázať jeden effect pri ľubovoľnom počte attempts.

## 36. Positive acceptance

Pozitívny test odošle rovnaký approved command viackrát paralelne aj sekvenčne. Jeden attempt claimne operation, ostatné dostanú rovnaký committed result a downstream business state sa zmení iba raz.

Test overí aj descendant events a notifications. Jeden primary database row bez kontroly následných efektov nestačí.

## 37. Forbidden acceptance

Zakázaný test použije rovnaký key s iným digestom, tenantom, resource UID alebo target generation. Server musí vrátiť explicitný conflict a nevykonať ani jednu novú mutáciu.

Ďalší test simuluje stale worker s nižším fencing tokenom. Downstream commit musí odmietnuť jeho late write.

## 38. Recovery acceptance

Recovery test stratí response po commite, reštartuje executor a spustí retry. Systém musí nájsť pôvodný outcome cez key alebo authoritative reference a nesmie vytvoriť druhý effect.

Test zahŕňa aj dedup-store failover, delayed redelivery, expired lease a partial descendant delivery. Každý branch má explicitný expected state.

## 39. Second-operation acceptance

Nová legitímna failover operation dostane nový business operation ID a nový idempotency key. Musí prejsť aj keď rovnaký resource bol menený v minulosti.

Tým sa overí správny scope: deduplication chráni retry jednej operácie, ale neblokuje budúce autorizované zmeny.

## 40. Zhrnutie

Idempotency je end-to-end business contract opretý o stable identity, canonical arguments, atomic claim, downstream deduplication, fencing a authoritative read-back. Retry bez tohto contractu je iba opakované riziko.

Agent môže bezpečne používať mutation tool až vtedy, keď executor dokáže odpovedať: „ktorú presnú operation vykonávam, ako rozlíšim retry od novej požiadavky, kde je jeden side-effect owner a ako po timeoute zistím skutočný outcome?“

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Durable execution, retries a resumability](durable-execution-retries-resumability.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Model Context Protocol →](model-context-protocol.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
