# Shadow deployment

Shadow deployment, často nazývaný traffic mirroring alebo dark launch, posiela kópiu produkčných requestov novej verzii bez toho, aby jej response ovplyvnila používateľa. Cieľom je pozorovať správanie pri reálnom workload-e s obmedzeným user-facing rizikom.

## 1. Základný model

```text
client request
→ primary version → authoritative response
             ↘ mirrored request → shadow version → discarded response
```

Primary path zostáva autoritatívny. Shadow path dostane kópiu vstupu, ale nesmie neplánovane meniť produkčný stav.

## 2. Čo shadow deployment overuje

Vhodný je najmä na:

- kompatibilitu requestov,
- performance pri reálnom workload mixe,
- parser a protocol behavior,
- nové query alebo ranking algoritmy,
- dependency call patterns,
- resource consumption,
- response diffing,
- capacity planning,
- observability novej verzie.

Neoveruje plnohodnotne používateľský outcome, interaktívne workflows ani všetky write semantics.

## 3. Mirror point

Traffic možno kopírovať na:

- edge proxy,
- API gateway,
- service mesh,
- load balancer,
- application layer,
- message broker,
- event stream.

Čím skôr v request path sa mirror vytvorí, tým viac originálneho kontextu zachová. Čím neskôr, tým jednoduchšie možno odstrániť citlivé alebo nebezpečné údaje.

## 4. Synchronous vs. asynchronous mirroring

### Synchronous

Primary request čaká, kým sa mirror odovzdá shadow systému. Je jednoduchší na koreláciu, ale môže zvýšiť latency a failure coupling.

### Asynchronous

Primary path uloží mirror do queue alebo ho odošle best-effort. Znižuje user-facing dopad, ale pridáva lag, sampling a možnosť straty.

Shadow infraštruktúra nesmie vytvoriť backpressure na primary path bez explicitnej policy.

## 5. Write safety

Najväčšie riziko je dvojité vykonanie side effectu.

Nebezpečné operácie:

- payment alebo order creation,
- email/SMS/push notification,
- account mutation,
- inventory reservation,
- external API write,
- queue publication,
- audit alebo compliance action,
- scheduled job.

Ochrany:

- read-only credentials,
- sandbox dependencies,
- write sink alebo null adapter,
- transaction rollback,
- isolated database/schema,
- explicitný shadow mode v aplikácii,
- side-effect allowlist,
- idempotency iba ako doplnková ochrana.

„Response zahodíme“ neznamená, že side effects nevznikli.

## 6. Authentication a authorization

Mirrored request môže obsahovať token, cookies alebo osobné údaje. Shadow verzia by nemala automaticky dostať rovnaké oprávnenia ako primary.

Možnosti:

- vymeniť user token za obmedzenú shadow identity,
- odstrániť nepotrebné claims,
- použiť read-only service account,
- redigovať citlivé headers,
- oddeliť auditné záznamy,
- zakázať externé writes.

Shadow systém je stále súčasťou produkčnej security boundary.

## 7. Data privacy

Pred mirroringom klasifikuj:

- osobné údaje,
- secrets a credentials,
- payment údaje,
- health alebo regulated data,
- tenant isolation,
- data residency.

Sampling ani interné použitie automaticky neodstraňujú privacy povinnosti. Logy shadow systému potrebujú rovnakú alebo prísnejšiu ochranu.

## 8. Sampling

Nie vždy je bezpečné alebo ekonomické mirrorovať 100 % trafficu.

Sampling možno riadiť podľa:

- percenta requestov,
- route,
- tenant segmentu,
- payload size,
- regionu,
- error-prone operation,
- request complexity,
- časového okna.

Vzorka musí zachovať workload mix relevantný pre testovanú hypotézu.

## 9. Request normalization

Primary a shadow môžu dostať odlišný input, ak sa medzi nimi mení:

- timestamp,
- nonce,
- request ID,
- expirovaný token,
- signed URL,
- transient resource reference,
- ordering,
- body stream.

Mirror layer musí vedieť, ktoré polia zachovať, regenerovať alebo odstrániť. Inak response diff odráža iba nondeterminism.

## 10. Response diffing

Porovnávať možno:

- status alebo outcome category,
- schema,
- normalized body,
- selected fields,
- ordering-insensitive collections,
- latency,
- dependency calls,
- side-effect intent,
- business score.

Pred diffom normalizuj dynamické hodnoty, napríklad timestamps, generated IDs a unordered results.

Nie každý rozdiel je chyba; nový algorithm môže byť zámerne odlišný.

## 11. Correlation

Každý mirror potrebuje väzbu:

```text
primary_request_id
shadow_request_id
artifact_digest
mirror_policy_version
sample decision
```

Bez korelácie nemožno analyzovať rozdiel, latency ani missing shadow result.

## 12. Capacity a cost

Shadow môže takmer zdvojnásobiť:

- application compute,
- network traffic,
- dependency reads,
- database queries,
- logs a traces,
- cache pressure.

Ochrany:

- rate limit,
- independent autoscaling,
- bounded queues,
- drop policy,
- dependency budgets,
- lower log verbosity,
- explicitný cost ceiling.

Primary SLO má prednosť pred úplnosťou shadow dát.

## 13. Cache a state effects

Aj read-only shadow môže meniť systém nepriamo:

- zohrievať alebo vytláčať cache,
- meniť database buffer pool,
- spotrebovať rate limits,
- vytvoriť service-discovery load,
- ovplyvniť autoscaling,
- aktivovať lazy initialization.

Preferuj oddelené cache namespaces alebo izolované dependencies, keď je interference významná.

## 14. Messaging a event shadowing

Pri queues a streams možno eventy kopírovať do shadow consumer group.

Potrebné sú:

- samostatný consumer group ID,
- zákaz authoritative acknowledgements,
- izolované output topics,
- replay a offset policy,
- schema compatibility,
- ochrana proti externým side effects.

Shadow consumer nesmie meniť primary backlog ani ownership partitionov.

## 15. Long-running workflows

Jednorazové request mirroring nemusí pokryť celý workflow. Pri viacstupňových procesoch treba:

- konzistentný shadow state,
- koreláciu udalostí,
- izolované workflow IDs,
- delayed outcome collection,
- cleanup po experimente.

Inak shadow verzia vidí iba fragmenty procesu a produkuje falošné chyby.

## 16. Promotion model

Shadow deployment môže byť krok pred canary:

```text
offline/replay test
→ shadow traffic
→ canary exposure
→ wider progressive rollout
```

Úspešný shadow test nedokazuje, že verzia je bezpečná pre user-facing writes, sessions alebo business outcome. Je to doplnková evidence.

## 17. Troubleshooting

### Shadow results často chýbajú

Over queue drops, timeout, rate limits, sampling metadata, autoscaling a correlation pipeline.

### Shadow latency je výrazne vyššia

Môže mať cold caches, inú capacity, debug logging alebo izolované dependencies. Porovnávaj relevantné podmienky.

### Primary latency sa zhoršila

Mirror je synchronný, zdieľa connection pool alebo vytvára backpressure. Oddeľ resources a nastav drop policy.

### Shadow vytvoril reálne side effects

Okamžite vypni mirror, aktivuj compensating process, audituj credentials a zaveď read-only alebo sink adapters.

### Response diff je extrémne vysoký

Skontroluj nondeterministic fields, input normalization, ordering, time-dependent logic a rozdielne configy.

## 18. Anti-patterny

### Shadow používa production write credentials

Zvyšuje riziko duplicitných alebo neautorizovaných mutations.

### Mirror 100 % bez capacity modelu

Experiment môže spôsobiť incident primárnej služby.

### Chýbajúci correlation ID

Dáta nemožno spoľahlivo porovnať.

### Každý rozdiel sa počíta ako regresia

Ignoruje zámerné behavior changes a nondeterminism.

### Úspešný shadow = automatický plný rollout

Shadow neoveril user-facing response ani všetky state transitions.

## 19. Kontrolné otázky

1. Čo je shadow deployment a čo nie je?
2. Aký je rozdiel medzi synchronous a asynchronous mirroringom?
3. Prečo discarded response nezaručuje absenciu side effects?
4. Ako chrániť credentials a osobné údaje?
5. Ako vybrať reprezentatívny sampling?
6. Čo treba normalizovať pri response diffingu?
7. Ako shadow traffic ovplyvňuje cache a dependencies?
8. Ako bezpečne shadowovať event consumers?
9. Kedy shadow zaradiť pred canary?
10. Prečo shadow úspech nestačí na release decision?

## Glossary impact

Relevantné pojmy: shadow deployment, traffic mirroring, dark launch, shadow mode, mirror point, shadow identity, response diffing, mirror sampling, side-effect sink, shadow consumer group a primary-path isolation.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: A/B testing](a-b-testing.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Ring deployment →](ring-deployment.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
