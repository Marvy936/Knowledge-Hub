# CAP theorem

CAP theorem nie je pravidlo „vyber si dve vlastnosti“ pre celý systém. Je to scoped impossibility result: počas network partition-u nemôže replikovaná služba pri presných formálnych definíciách súčasne garantovať single-copy consistency a response od každého non-failed node-u. Praktický návrh preto rozhoduje per operation, čo sa smie stať, keď required participants nevedia koordinovať.

```text
business operation a invariant
→ exact replicated subject a client cohort
→ normal authority a topology
→ partition/reachability scenario
→ quorum a dostupné observations
→ consistency alebo availability decision
→ acknowledgement, refusal alebo bounded stale result
→ external effect a unknown outcome
→ heal, convergence a reconciliation
→ asymmetric a second-partition validation
```

Otázka `Je databáza CP alebo AP?` je príliš hrubá. Správna otázka je, či konkrétny route read, settlement write, dashboard read alebo telemetry append počas konkrétneho partition-u pokračuje, odmietne sa alebo použije slabší explicitný contract.

## 1. Exact CAP subject a formálny scope

CAP subject musí pomenovať replicated object alebo key range, operation a invariant, client/read/write cohort, topology a failure domains, partition scenár, consistency model, availability response contract, quorum, acknowledgement boundary, stale/conflict semantics a external side effects.

Vo formálnom asynchronous network modeli môžu správy arbitrárne meškať alebo sa stratiť. CAP consistency sa typicky interpretuje ako linearizability: completed write musí byť viditeľný všetkým neskorším current reads, akoby existovala jedna aktuálna kópia. Nie je to ACID consistency, schema constraint ani všeobecná business správnosť.

CAP availability znamená, že každý request prijatý non-failed node-om nakoniec dostane response. Nie je to percentuálne SLO. Response môže obsahovať stale alebo conflict-producing state, ak systém zachováva availability na úkor single-copy consistency.

Partition tolerance nie je voliteľný feature flag. Packet loss, asymmetric reachability, overloaded link, routing blackhole, process pause alebo disk stall môžu byť z pohľadu peerov nerozlíšiteľné. Timeout je observation, nie proof crashu ani partition-u.

## 2. Partition decision je per operation

Mimo partition-u môže systém poskytovať silnú consistency aj vysokú praktickú availability. Konflikt vzniká až vtedy, keď required participants nevedia koordinovať.

Pri päťčlennom clusteri s quorum `3` partition `3 + 2` umožní majority side pokračovať v consensus writes. Minority nemôže bezpečne commitovať nový log entry. Môže odmietnuť, čakať alebo poskytovať explicitne local/stale reads podľa operation contractu.

Jedna platforma môže mať túto matrix:

```text
create settlement intent
→ current authority/quorum required
→ bez quorum fail closed

choose provider route for external effect
→ linearizable minimum generation required
→ stale route forbidden

merchant dashboard
→ bounded stale read allowed
→ observed generation + stale marker

telemetry append
→ local durable buffer allowed
→ deterministic later merge
```

Toto nie je nekonzistentná architecture; je to operation-specific partition policy. Nebezpečné je implicitne použiť rovnaký local read pre dashboard aj side-effecting provider decision.

## 3. Consistency-preserving a availability-preserving paths

Consistency-preserving write počas quorum loss-u odmietne alebo prekročí deadline bez success acknowledgement-u. Stable operation identity zostane zachovaná a client neskôr queryuje authority, pretože lost response môže stále vytvoriť unknown outcome.

```text
quorum unavailable
→ no authoritative success
→ explicit unavailable/deferred response
→ status lookup po recovery
```

Availability-preserving local progress je bezpečný iba pre mergeable domain. Operation potrebuje origin/version identity, conflict policy a post-heal reconciliation. Append-only local logs, commutative counters, CRDT alebo bounded stale representation môžu byť vhodné. Non-mergeable payment intent alebo current provider route zvyčajne nie.

Last-write-wins bez domain semantics môže zahodiť legitimate concurrent update. `Replicas sa nakoniec zhodnú` nie je business correctness, ak každá strana už vykonala odlišný external effect.

Stale read je contract, nie náhoda. Musí niesť observed revision/generation, maximálny gap alebo age, allowed-use a fallback. Generation `911` môže byť prijateľná pre historical dashboard; nesmie po activation `912` autorizovať nový provider call na old route.

## 4. Quorum, clients a end-to-end authority

Quorum chráni consensus history, nie automaticky celý application path. Client môže používať member-local read, stale cache, old connection alebo process-loaded configuration. Consensus cluster môže byť safe a application aj tak vykonať nesprávne rozhodnutie.

```text
quorum commits generation 912
→ local member/cache stále vracia 911
→ application nepýta minimum generation
→ provider effect používa 911
```

Acknowledgement preto musí obsahovať alebo odkazovať na evidence: cluster/revision/term, used business generation a operation identity. Application rozhoduje, či evidence spĺňa minimum required pre danú operation.

PACELC dopĺňa praktickú otázku: počas partition-u consistency vs. availability; mimo partition-u latency vs. consistency. Member-local read môže byť rýchlejší aj bez incidentu, ale jeho použitie pre authority decision musí zostať zakázané alebo generation-bound.

## 5. Heal, convergence a business reconciliation

Network heal neuzatvára incident. Replicas môžu konvergovať na majority log, no zostávajú local accepted attempts, client retries, caches, loaded generations a external effects.

```text
connectivity restored
→ consensus members converge
→ retire stale local/cache generations
→ classify operations podľa used generation
→ reconcile provider attempts a outcomes
→ replay iba safe manifest
→ validate second partition
```

Ak minority iba odmietala authoritative writes, recovery je jednoduchší. Ak prijímala mergeable writes, treba merge a conflict evidence. Ak používala stale state na external effects, každý affected operation cohort potrebuje provider/idempotency lookup.

## 6. Connected incident `DB-PAY-59`

Atlas Payments presunul provider-route control do päťčlenného consensus clusteru: Region A mala troch voting members, Region B dvoch a quorum bolo `3`. Control plane v Region A commitol route generation `911 → 912`, teda `P1 → P2`. Potom deväťminútový partition oddelil Region B.

Region A zachovala quorum a linearizable reads vracali `912/P2`. Region B nemohla commitovať, ale control client používal member-local serializable read a application cache držala `911` s desaťminútovým TTL. Request path nerozlišoval current authority od local availability.

Počas deviatich minút vstúpilo do affected flowu `24 600` logical operations. `3 842` načítalo stale generation `911`; `1 126` attempts smerovalo na degraded `P1`; `1 384` skončilo `sent-unknown` a `27` vytvorilo duplicate physical attempts. Provider idempotency zabránila duplicate financial effectu, no CAP/read contract aj tak zlyhal.

Root cause nebol consensus split brain. Majority history bola správna. Provider-route read nemal per-operation partition contract, takže stale local availability bola dovolená pre side-effecting operation, ktorá mala vyžadovať current generation alebo explicitne odmietnuť.

## 7. Redesign a acceptance paths

Settlement/provider selection teraz vyžaduje linearizable read s minimum acceptable generation; settlement persistuje exact route generation. Pri uncertainty failne closed. Dashboard používa bounded stale projection s `observed_generation` a `stale=true`. Telemetry smie bufferovať lokálne a neskôr merge-nuť.

**Positive path** počas normal topology vráti current generation a vykoná side effect s persisted evidence.

**Recovery path** pri minority partition-e odmietne side-effecting operation, zachová stable identity a po heal-e obnoví status bez duplicate effectu.

**Availability path** dovolí iba explicitne mergeable alebo bounded-stale operations a po heal-e preukáže convergence.

**Forbidden path** odmietne stale authority read, unmergeable dual write, success acknowledgement bez quorum evidence a external effect z minority-local state-u.

Acceptance zahŕňa asymmetric partition, delayed messages, cache s old generation, lost response na quorum side, second partition a reconciliation external effects.

## 8. Troubleshooting a anti-patterny

Diagnostika ide od exact operation a replicated subjectu cez topology/reachability, quorum/term/revision, client consistency mode, cache generation, acknowledgement a external effects až po heal/convergence. `Cluster healthy` nie je end-to-end verdict.

Najčastejšie anti-patterny sú `pick two`, predstava, že partition možno vypnúť, CP označené za vždy unavailable, AP označené za permanentne nesprávne, quorum považované za application correctness, stale read označený za neškodný a heal považovaný za koniec incidentu.

## 9. Kontrolné otázky

1. Aké presné properties používa CAP theorem?
2. Ako sa CAP consistency líši od ACID consistency?
3. Čo znamená availability vo formálnom modeli?
4. Prečo je partition decision per operation?
5. Kedy môže minority side bezpečne pokračovať?
6. Aké evidence musí niesť bounded stale read?
7. Prečo quorum nechráni stale application cache?
8. Čo treba reconciliovať po network heal-e?
9. Prečo consensus cluster v `DB-PAY-59` nebol split-brain?
10. Ktoré positive, recovery, availability a forbidden paths musia prejsť?

## Glossary impact

Relevantné pojmy: CAP subject, atomic consistency — CAP, CAP availability, network partition, per-operation partition contract, quorum side, minority side, partition refusal, partition-local progress, partition-heal reconciliation, stale-authority read, minimum acceptable generation, PACELC question a CAP acceptance verdict.

## Primárne zdroje

- [Gilbert a Lynch — Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services](https://groups.csail.mit.edu/tds/reflist.html)
- [etcd API guarantees](https://etcd.io/docs/v3.7/learning/api_guarantees/)
- [etcd Failure modes](https://etcd.io/docs/v3.8/op-guide/failures/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Caching](caching.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Consistency models →](consistency-models.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
