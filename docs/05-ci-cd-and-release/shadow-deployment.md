# Shadow deployment

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

## 1. Definícia

Shadow deployment posiela kópiu reálneho produkčného vstupu novej verzii bez toho, aby jej výsledok určoval používateľskú response alebo autoritatívny business state. Technika sa označuje aj ako traffic mirroring; dark launch je širší pojem pre nasadenú, ale používateľsky neaktivovanú capability.

```text
client
→ primary path → authoritative response/state
       ↘ mirror → shadow path → observed, non-authoritative result
```

Shadow znižuje user-facing riziko, ale nie je automaticky bezrizikový. Kópia requestu môže spotrebovať kapacitu, čítať citlivé dáta alebo vytvoriť side effects.

## 2. Mental model: neautoritatívna paralelná execution

Shadow experiment má tri oddelené kontrakty:

- **Delivery contract —** ktorý vstup, kedy a s akou úplnosťou sa zrkadlí.
- **Safety contract —** čo shadow nesmie zmeniť alebo ovplyvniť.
- **Comparison contract —** ktoré outputs a runtime signals sa považujú za ekvivalentné alebo zámerne odlišné.

Úspešné zahodenie response nerieši safety. Side effect mohol vzniknúť pred zahodením výsledku.

## 3. Čo shadow dokáže overiť

Vhodný je na:

- request a protocol compatibility,
- parser behavior,
- reálny workload mix,
- performance a resource profile,
- dependency call pattern,
- query/ranking výsledky,
- response diffing,
- observability novej verzie,
- event-consumer processing v izolovanom výstupe.

Slabšie overuje:

- reálny user journey,
- client reaction na response,
- authoritative writes,
- session evolution,
- external side effects,
- business outcome po dlhom workflowe.

## 4. Experiment subject a provenance

Zachovaj:

- primary a shadow artifact digests,
- config revisions,
- mirror policy version,
- mirror point,
- sampling policy,
- normalization/diff version,
- shadow identity a permissions,
- dependency isolation mode,
- experiment start/stop,
- correlation ID.

Bez toho nemožno zistiť, čo bolo porovnávané.

## 5. Mirror point

Traffic možno zrkadliť na:

- edge/load balanceri,
- API gateway,
- service mesh,
- application boundary,
- broker/stream,
- data-processing pipeline.

Skorší mirror zachová viac pôvodného request contextu, ale zvyšuje privacy a write risk. Neskorší mirror umožňuje sanitizáciu, ale nemusí testovať celý path.

## 6. Synchronous verzus asynchronous delivery

### Synchronous

Primary request čaká aspoň na odovzdanie mirroru. Korelácia je jednoduchšia, ale shadow môže pridať latency alebo failure coupling.

### Asynchronous

Mirror sa vloží do bounded queue alebo odošle best-effort. Chráni primary latency, ale vzniká:

- delivery lag,
- drop,
- reordering,
- duplicate delivery,
- rozdielny concurrency profile.

Primary SLO má mať prioritu. Shadow backpressure nesmie neplánovane blokovať používateľa.

## 7. Mirror delivery semantics

Explicitne definuj:

- at-most-once, at-least-once alebo best-effort charakter,
- max queue depth,
- drop policy,
- retry limit,
- ordering,
- max lag,
- duplicate handling,
- sampling pred alebo po queue.

Comparison musí vedieť rozlíšiť missing shadow result od application mismatchu.

## 8. Sampling a representatívnosť

Sampling môže byť podľa:

- percenta,
- route/operation,
- request complexity,
- tenant/region segmentu,
- payload size,
- časového okna,
- error-prone pathu.

Sleduj sample inventory a workload distribution. Jednoduchý random sample môže podreprezentovať rare, ale kritické operácie.

## 9. Input capture a body semantics

Nie každý request možno jednoducho skopírovať:

- streaming body môže byť read-once,
- upload môže byť veľký,
- token môže expirovať,
- nonce alebo signature je jednorazová,
- referencovaný resource sa medzičasom zmení,
- request závisí od session state.

Mirror layer musí definovať capture limit, buffering, regeneration a skip reason.

## 10. Input sanitizácia

Pred odoslaním odstráň alebo transformuj:

- credentials a session tokens,
- payment/health data,
- secrets v headers/body,
- osobné identifikátory,
- signed URLs,
- nepotrebné tenant attributes.

Sanitizácia musí zachovať semantiku potrebnú pre test. Príliš agresívna redakcia môže vytvoriť nereprezentatívny input.

## 11. Shadow identity a authorization

Shadow nemá automaticky dostať user alebo primary service credentials. Preferuj:

- read-only workload identity,
- minimálne claims,
- isolated tenant/sandbox,
- explicitný shadow claim,
- zakázané external writes,
- oddelený audit stream.

Client-side authorization výsledok možno porovnať, ale enforcement nesmie byť oslabený kvôli experimentu.

## 12. Side-effect firewall

Bezpečnostná vrstva má blokovať alebo izolovať:

- payment/order writes,
- email/SMS/push,
- inventory reservation,
- account mutation,
- external API commands,
- authoritative queue publication,
- compliance actions,
- scheduled mutations.

Mechanizmy:

- read-only credentials,
- null/sink adapters,
- sandbox dependencies,
- isolated schema/database,
- transaction rollback,
- output topic,
- explicitný shadow execution mode.

Idempotency nie je jediná ochrana; duplicitný idempotency key môže mať iný scope alebo expirovať.

## 13. Indirect interference

Aj read-only shadow môže ovplyvniť primary systém:

- vytesniť cache,
- zahriať database buffer pool,
- spotrebovať quotas,
- zvýšiť connection count,
- spustiť autoscaling,
- zvýšiť log/storage load,
- aktivovať lazy initialization.

Definuj dependency a cost budgets alebo používaj izolované namespaces/resources.

## 14. Request normalization

Primary a shadow execution sa môžu líšiť pre nondeterministické vstupy:

- current time,
- random seed,
- generated request ID,
- nonce,
- expirovaný credential,
- read-after-write state,
- ordering.

Rozhodni, čo:

- zachovať identicky,
- regenerovať pre shadow,
- fixnúť test clockom,
- normalizovať iba pri diff-e,
- úplne vylúčiť.

## 15. Response a behavior diff

Porovnávaj podľa contractu:

- status/outcome class,
- schema a required fields,
- vybrané business hodnoty,
- ordering-insensitive collections,
- error category,
- dependency calls,
- resource usage,
- latency,
- intended side-effect plan.

Nie každý rozdiel je regresia. Nový ranking algoritmus má byť odlišný; dôležitá je jeho definovaná quality metric.

## 16. Diff taxonomy

Klasifikuj:

- expected change,
- acceptable nondeterminism,
- primary defect,
- shadow defect,
- input mismatch,
- state/timing mismatch,
- missing result,
- comparison-tool error.

Jedno číslo „mismatch rate“ bez klasifikácie má nízku diagnostickú hodnotu.

## 17. Correlation

Každý mirror record potrebuje:

```text
primary_request_id
shadow_request_id
mirror event ID
primary/shadow digests
sample decision
mirror lag
diff result
```

Pri async workflowe korelácia zahŕňa aj event/workflow IDs a delayed outcomes.

## 18. Capacity a cost ceiling

Shadow môže takmer zdvojnásobiť compute a reads. Chráň:

- primary request latency,
- database connection pool,
- broker throughput,
- external API quotas,
- telemetry cardinality,
- storage retention.

Použi independent autoscaling, bounded queue, rate limit a automatické zníženie sample pri tlaku.

## 19. Messaging a event shadowing

Použi samostatný consumer group a izolované outputs. Shadow consumer nesmie:

- ackovať za primary group,
- meniť primary offsets,
- publikovať authoritative events,
- súťažiť o partition ownership,
- spustiť externé side effects.

Definuj replay start, retention, ordering a cleanup.

## 20. Long-running workflows

Jednorazový request diff nemusí pokryť workflow. Potrebuješ:

- konzistentný shadow state,
- izolované workflow IDs,
- event correlation,
- delayed result collector,
- timeout a garbage collection,
- compensation pre omylom vzniknuté outputs.

## 21. Experiment validity

Výsledok môže byť:

- valid and equivalent,
- valid with expected differences,
- valid regression found,
- inconclusive pre nízku vzorku,
- invalid pre input/config mismatch,
- aborted pre safety alebo capacity.

Shadow success nesmie byť odvodený z chýbajúcich resultov.

## 22. Promotion ladder

```text
offline fixtures
→ replay
→ shadow traffic
→ canary user-facing exposure
→ širší rollout
```

Každá fáza zvyšuje fidelity. Shadow neposkytuje dôkaz o client reaction a authoritative writes, preto zvyčajne nasleduje canary.

## 23. Privacy a retention

Definuj:

- právny účel,
- data minimization,
- residency,
- encryption,
- access control,
- raw payload retention,
- diff retention,
- deletion/subject-right proces,
- zákaz secretov v logs.

Interný experiment nie je výnimka z privacy pravidiel.

## 24. Failure recovery

Pri primary impacte:

1. vypni mirror alebo zníž sample,
2. odpoj shadow resources,
3. over primary latency a dependency load,
4. drain alebo drop mirror queue,
5. zachovaj evidence.

Pri neplánovaných side effects:

1. aktivuj kill switch,
2. revoke shadow credentials,
3. zastav output adapters,
4. identifikuj affected entities,
5. vykonaj compensation/data repair,
6. spusti security/incident review.

## 25. Observability a evidence

Sleduj:

- mirror attempted/delivered/dropped,
- delivery lag,
- primary overhead,
- shadow throughput/saturation,
- correlation completeness,
- diff categories,
- skipped requests a reasons,
- side-effect blocks,
- cost,
- experiment validity.

## 26. Typické anti-patterny

### Response sa zahodí, preto je shadow bezpečný

Side effects vznikajú pred response.

### Production write credentials

Shadow môže vykonať duplicitné alebo neautorizované mutations.

### Synchronous mirror bez timeout/drop policy

Shadow dependency poškodí primary latency.

### 100 % mirroring bez capacity modelu

Experiment spôsobí incident.

### Chýbajúci correlation ID

Outputs nemožno spojiť.

### Každý mismatch je regresia

Ignoruje nondeterminism a zámernú zmenu.

### Shadow success = full release

Neboli overené user-facing responses, state transitions ani business outcome.

## 27. Diagnostický postup

1. Over primary/shadow digest a config.
2. Skontroluj mirror point a policy version.
3. Porovnaj attempted, delivered a completed counts.
4. Over delivery lag, duplicates a ordering.
5. Validuj input sanitizáciu a normalization.
6. Skontroluj shadow identity a side-effect firewall.
7. Porovnaj workload/capacity conditions.
8. Klasifikuj diffs namiesto agregovaného mismatchu.
9. Pri primary regressii vypni mirror a analyzuj shared resources.
10. Pri side effecte spusti compensation a incident workflow.

## 28. Rozhodovací rámec

1. Akú hypotézu má shadow overiť?
2. Kde sa traffic zrkadlí a čo tým vynechá?
3. Aké delivery semantics platia?
4. Ktoré dáta treba sanitizovať?
5. Ako sa technicky znemožnia side effects?
6. Aké indirect shared-resource interference hrozí?
7. Aká vzorka reprezentuje workload?
8. Ako sa normalizujú inputs a outputs?
9. Ktoré diff kategórie sú rozhodujúce?
10. Čo shadow nedokáže potvrdiť a musí overiť canary?

## 29. Kontrolný checklist

- immutable primary/shadow identities,
- mirror policy a point sú versionované,
- primary path má timeout/drop ochranu,
- sample inventory je reprezentatívny,
- citlivé dáta sú minimalizované,
- shadow identity je least privilege,
- side-effect firewall je otestovaný,
- shared dependency budgets existujú,
- correlation je end-to-end,
- diff contract pozná expected differences,
- missing result nie je success,
- promotion pokračuje ďalším fidelity krokom,
- retention a cleanup sú definované.

## 30. Kontrolné otázky

1. Aký je rozdiel medzi shadow deploymentom a dark launchom?
2. Prečo discarded response nezaručuje safety?
3. Ako sa líši synchronous a asynchronous mirroring?
4. Čo musí definovať mirror delivery contract?
5. Ako môže read-only shadow poškodiť primary systém?
6. Kedy treba meniť alebo regenerovať input fields?
7. Ako sa klasifikujú response differences?
8. Ako bezpečne shadowovať event consumer?
9. Prečo shadow neposkytuje úplný release dôkaz?
10. Čo robiť pri neplánovaných side effects?

## Summary

Shadow deployment je neautoritatívna paralelná execution reálneho workloadu. Jeho hodnota spočíva v protocol, performance a behavior evidence pred user-facing expozíciou. Bezpečnosť vyžaduje presné mirror delivery semantics, least-privilege identity, technický side-effect firewall, privacy sanitizáciu, bounded resource impact a end-to-end correlation. Výsledok musí rozlišovať validný mismatch od input, timing alebo comparison chyby. Úspešný shadow je medzikrok k canary, nie automatické povolenie plného release.

## Glossary impact

Relevantné pojmy: shadow deployment, traffic mirroring, dark launch, mirror point, mirror delivery semantics, primary-path isolation, shadow identity, side-effect firewall, request normalization, response diff taxonomy, shadow consumer group a mirror lag.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: A/B testing](a-b-testing.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Ring deployment →](ring-deployment.md)
<!-- KNOWLEDGE-NAVIGATION:END -->